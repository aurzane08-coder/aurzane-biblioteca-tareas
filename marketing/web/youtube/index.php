<?php
// Conexión de canales de YouTube para publicar (una sola vez por canal).
// aurzane.com/youtube/?inicio=1&cuenta=clips -> Google pide permiso (elige el canal) -> vuelve aquí con ?code= -> se canjea en el servidor
// y el token de actualización se guarda fuera de la web (privado-youtube/refresh_<cuenta>). Nunca se muestra.
// Redirección que debe estar autorizada en el cliente OAuth de Google: https://aurzane.com/youtube/
header('Cache-Control: no-store, max-age=0');
header('Content-Type: text/html; charset=utf-8');
$dir = dirname(__DIR__, 2) . '/privado-youtube';
@mkdir($dir, 0700, true);
$app = json_decode(@file_get_contents("$dir/app.json"), true) ?: [];
$redir = 'https://aurzane.com/youtube/';
function fin($t) { echo "<!doctype html><html lang='es'><meta charset='utf-8'><meta name=viewport content='width=device-width'><title>Conectar YouTube · AURZANE</title><body style='margin:0;background:#0F1530;color:#F5F3EE;font:16px/1.6 system-ui,sans-serif'><main style='max-width:560px;margin:auto;padding:64px 24px'><p style='letter-spacing:.08em;color:#EACF92;font-weight:700'>AURZANE</p><h1 style='font-size:1.8rem;margin:0 0 12px'>Conectar un canal de YouTube</h1><p>$t</p></main></body></html>"; exit; }
if (empty($app['client_id']) || empty($app['client_secret'])) fin('Aún no están los datos de la app. Espera a la siguiente ejecución del flujo de clips.');
if (isset($_GET['inicio'])) {
    $cuenta = preg_replace('/[^a-z]/', '', $_GET['cuenta'] ?? 'clips') ?: 'clips';
    $st = bin2hex(random_bytes(16));
    file_put_contents("$dir/state", $st . "\t" . time() . "\t" . $cuenta);
    $q = http_build_query(['client_id' => $app['client_id'], 'redirect_uri' => $redir, 'response_type' => 'code', 'access_type' => 'offline',
        'prompt' => 'consent select_account', 'scope' => $cuenta === 'gsc' ? 'https://www.googleapis.com/auth/webmasters.readonly' : 'https://www.googleapis.com/auth/youtube.upload https://www.googleapis.com/auth/youtube.readonly', 'state' => $st]);
    header('Location: https://accounts.google.com/o/oauth2/v2/auth?' . $q, true, 302); exit;
}
if (isset($_GET['error'])) fin('Google no dio permiso: ' . htmlspecialchars($_GET['error']));
if (!isset($_GET['code']) && ($_GET['cuenta'] ?? '') === 'gsc') fin('Conecta Search Console para que la IA de AURZANE mejore títulos y artículos según lo que la gente busca. Elige la cuenta de Google con la que verificaste aurzane.com. El permiso es solo de lectura.<br><br><a href="?inicio=1&cuenta=gsc" style="display:inline-block;background:#C9A24B;color:#080B17;padding:13px 24px;border-radius:99px;font-weight:700;text-decoration:none">Conectar Search Console</a>');
if (!isset($_GET['code'])) fin('Conecta el canal Clips-All. Al elegir cuenta, escoge el canal <b>Clips-All</b>.<br><br><a href="?inicio=1&cuenta=clips" style="display:inline-block;background:#FF0033;color:#fff;padding:13px 24px;border-radius:99px;font-weight:700;text-decoration:none">Conectar Clips-All</a>');
[$st, $t0, $cuenta] = array_pad(explode("\t", @file_get_contents("$dir/state")), 3, '');
@unlink("$dir/state");
if (!$st || !hash_equals($st, $_GET['state'] ?? '') || time() - (int)$t0 > 900) fin('El enlace caducó. <a style="color:#EACF92" href="?inicio=1&cuenta=clips">Vuelve a empezar</a>.');
$ch = curl_init('https://oauth2.googleapis.com/token');
curl_setopt_array($ch, [CURLOPT_POST => true, CURLOPT_RETURNTRANSFER => true, CURLOPT_TIMEOUT => 30,
    CURLOPT_POSTFIELDS => http_build_query(['client_id' => $app['client_id'], 'client_secret' => $app['client_secret'],
        'code' => $_GET['code'], 'grant_type' => 'authorization_code', 'redirect_uri' => $redir])]);
$r = json_decode(curl_exec($ch), true) ?: [];
if (empty($r['refresh_token'])) fin('No se pudo completar: ' . htmlspecialchars($r['error_description'] ?? $r['error'] ?? 'respuesta vacía'));
if ($cuenta === 'gsc') {
    $ch = curl_init('https://www.googleapis.com/webmasters/v3/sites');
    curl_setopt_array($ch, [CURLOPT_RETURNTRANSFER => true, CURLOPT_TIMEOUT => 20, CURLOPT_HTTPHEADER => ['Authorization: Bearer ' . $r['access_token']]]);
    $sites = json_decode(curl_exec($ch), true) ?: [];
    file_put_contents("$dir/refresh_gsc", $r['refresh_token']); chmod("$dir/refresh_gsc", 0600);
    $n = count($sites['siteEntry'] ?? []);
    fin($n ? "Search Console conectado: $n propiedades. Desde mañana la IA usará las búsquedas reales para mejorar títulos y artículos." : 'Conectado, pero esta cuenta no tiene acceso a ninguna propiedad de Search Console' . (isset($sites['error']) ? ' (' . htmlspecialchars($sites['error']['message'] ?? '') . ')' : '') . '. <a style="color:#EACF92" href="?inicio=1&cuenta=gsc">Prueba con otra cuenta</a>.');
}
$canal = '';
$ch = curl_init('https://www.googleapis.com/youtube/v3/channels?part=snippet&mine=true');
curl_setopt_array($ch, [CURLOPT_RETURNTRANSFER => true, CURLOPT_TIMEOUT => 20, CURLOPT_HTTPHEADER => ['Authorization: Bearer ' . $r['access_token']]]);
$c = json_decode(curl_exec($ch), true) ?: []; $canal = $c['items'][0]['snippet']['title'] ?? '';
file_put_contents("$dir/refresh_$cuenta", $r['refresh_token']); chmod("$dir/refresh_$cuenta", 0600);
fin('Canal conectado: <b>' . htmlspecialchars($canal ?: 'sin nombre') . '</b>. Si no es Clips-All, <a style="color:#EACF92" href="?inicio=1&cuenta=clips">vuelve a conectarlo</a> eligiendo el canal correcto.');
