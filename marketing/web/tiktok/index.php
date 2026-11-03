<?php
// Redirección registrada en TikTok for Developers (Login Kit): https://aurzane.com/tiktok/ .
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
function fin($t) { echo "<!doctype html><html lang='es'><meta charset='utf-8'><meta name=viewport content='width=device-width'><title>Conectar TikTok · AURZANE</title><body style='margin:0;background:#0F1530;color:#F5F3EE;font:16px/1.6 system-ui,sans-serif'><main style='max-width:560px;margin:auto;padding:64px 24px'><p style='letter-spacing:.08em;color:#EACF92;font-weight:700'>AURZANE</p><h1 style='font-size:1.8rem;margin:0 0 12px'>Conectar con TikTok</h1><p>$t</p><p style='color:#A9B0C4;font-size:.9rem;margin-top:28px'>AURZANE publica vídeos cortos de divulgación de psicología en su cuenta de TikTok. <a style='color:#25F4EE' href='https://aurzane.com/privacidad.html'>Privacidad</a> · <a style='color:#25F4EE' href='https://aurzane.com/condiciones.html'>Condiciones</a></p></main></body></html>"; exit; }
if (empty($app['client_key']) || empty($app['client_secret'])) fin('Aún no están los datos de la app. Añade los secretos TIKTOK_CLIENT_KEY y TIKTOK_CLIENT_SECRET en GitHub y espera a la siguiente ejecución del flujo de marketing.');
if (isset($_GET['inicio'])) {
    $st = bin2hex(random_bytes(16));
    file_put_contents("$dir/state", $st . "\t" . time());
    $q = http_build_query(['client_key' => $app['client_key'], 'scope' => 'user.info.basic,video.upload,video.publish',
        'response_type' => 'code', 'redirect_uri' => $redir, 'state' => $st]);
    header('Location: https://www.tiktok.com/v2/auth/authorize/?' . $q, true, 302); exit;
}
if (isset($_GET['error'])) fin('TikTok no dio permiso: ' . htmlspecialchars($_GET['error_description'] ?? $_GET['error']));
if (!isset($_GET['code'])) fin('Conecta la cuenta de TikTok de AURZANE para publicar desde <a style="color:#25F4EE" href="/tiktok/publicar.php">la página de publicación</a>.<br><br><a href="?inicio=1" style="display:inline-block;background:#FE2C55;color:#fff;padding:13px 24px;border-radius:99px;font-weight:700;text-decoration:none">Continuar con TikTok</a>');
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
fin('Cuenta de TikTok conectada (permisos: ' . htmlspecialchars($r['scope'] ?? '') . ').<br><br><a href="/tiktok/publicar.php" style="display:inline-block;background:#FE2C55;color:#fff;padding:13px 24px;border-radius:99px;font-weight:700;text-decoration:none">Ir a publicar un vídeo</a>');
