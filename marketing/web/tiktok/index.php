<?php
// Redirección registrada en TikTok for Developers (Login Kit): https://aurzane.com/tiktok/
// Conexión de la cuenta de TikTok de AURZANE (una sola vez).
// aurzane.com/tiktok/?inicio=1 -> TikTok pide permiso -> vuelve aquí con ?code= -> se canjea en el servidor
// y el token de actualización se guarda fuera de la web (privado-tiktok/refresh). Nunca se muestra.
header('Cache-Control: no-store, max-age=0');
header('Content-Type: text/html; charset=utf-8');
$dir = dirname(__DIR__, 2) . '/privado-tiktok';
@mkdir($dir, 0700, true);
$app = json_decode(@file_get_contents("$dir/app.json"), true) ?: [];
$app = array_map(fn($v) => trim((string)$v), $app);
$redir = 'https://aurzane.com/tiktok/';
function fin($t) { echo "<!doctype html><meta name=viewport content='width=device-width'><body style='font-family:sans-serif;padding:40px;max-width:560px;margin:auto'><h1>TikTok · AURZANE</h1><p>$t</p></body>"; exit; }
if (empty($app['client_key']) || empty($app['client_secret'])) fin('Aún no están los datos de la app. Añade los secretos TIKTOK_CLIENT_KEY y TIKTOK_CLIENT_SECRET en GitHub y espera a la siguiente ejecución del flujo de marketing.');
if (isset($_GET['inicio'])) {
    $st = bin2hex(random_bytes(16));
    file_put_contents("$dir/state", $st . "\t" . time());
    $q = http_build_query(['client_key' => $app['client_key'], 'scope' => 'user.info.basic,video.upload,video.publish',
        'response_type' => 'code', 'redirect_uri' => $redir, 'state' => $st]);
    header('Location: https://www.tiktok.com/v2/auth/authorize/?' . $q, true, 302); exit;
}
if (isset($_GET['error'])) fin('TikTok no dio permiso: ' . htmlspecialchars($_GET['error_description'] ?? $_GET['error']));
if (!isset($_GET['code'])) fin('Para conectar la cuenta, abre <a href="?inicio=1">este enlace</a>.');
[$st, $t0] = array_pad(explode("\t", @file_get_contents("$dir/state")), 2, 0);
@unlink("$dir/state");
if (!$st || !hash_equals($st, $_GET['state'] ?? '') || time() - (int)$t0 > 900) fin('El enlace caducó. <a href="?inicio=1">Vuelve a empezar</a>.');
$ch = curl_init('https://open.tiktokapis.com/v2/oauth/token/');
curl_setopt_array($ch, [CURLOPT_POST => true, CURLOPT_RETURNTRANSFER => true, CURLOPT_TIMEOUT => 30,
    CURLOPT_HTTPHEADER => ['Content-Type: application/x-www-form-urlencoded'],
    CURLOPT_POSTFIELDS => http_build_query(['client_key' => $app['client_key'], 'client_secret' => $app['client_secret'],
        'code' => $_GET['code'], 'grant_type' => 'authorization_code', 'redirect_uri' => $redir])]);
$r = json_decode(curl_exec($ch), true) ?: [];
if (empty($r['refresh_token'])) fin('No se pudo completar: ' . htmlspecialchars($r['error_description'] ?? $r['error'] ?? 'respuesta vacía'));
file_put_contents("$dir/refresh", $r['refresh_token']); chmod("$dir/refresh", 0600);
fin('Cuenta de TikTok conectada (permisos: ' . htmlspecialchars($r['scope'] ?? '') . '). Ya puedes cerrar esta página.');
