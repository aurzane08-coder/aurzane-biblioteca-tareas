<?php
// Boletín semanal de AURZANE: alta con doble confirmación, baja con un clic. Los correos se guardan fuera de la web (privado-boletin).
declare(strict_types=1);
$dir = dirname(__DIR__, 2) . '/privado-boletin';
if (!is_dir($dir)) { mkdir($dir, 0700, true); }
$fs = "$dir/suscritos.json"; $fp = "$dir/pendientes.json";
function leer($f) { return is_file($f) ? (json_decode((string)file_get_contents($f), true) ?: []) : []; }
function guardar($f, $d) { file_put_contents($f, json_encode($d, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT), LOCK_EX); chmod($f, 0600); }
function pagina($titulo, $t) {
    header('Content-Type: text/html; charset=utf-8');
    echo "<!doctype html><html lang='es'><meta charset='utf-8'><meta name=viewport content='width=device-width'><meta name='robots' content='noindex'><title>$titulo · AURZANE</title>"
       . "<body style='margin:0;background:#0b0e1d;color:#f3efe6;font:17px/1.6 system-ui,sans-serif'><main style='max-width:560px;margin:auto;padding:64px 24px'>"
       . "<p style='letter-spacing:.08em;color:#E2BF6A;font-weight:700'>AURZANE</p><h1 style='font-size:1.8rem;margin:0 0 12px'>$titulo</h1><p>$t</p>"
       . "<p style='margin-top:28px'><a style='color:#E2BF6A' href='https://aurzane.com/'>Volver a AURZANE</a></p></main></body></html>"; exit;
}
function correo($para, $asunto, $html) {
    $cab = "MIME-Version: 1.0\r\nContent-Type: text/html; charset=UTF-8\r\nFrom: AURZANE <hola@aurzane.com>\r\nReply-To: hola@aurzane.com\r\n";
    return mail($para, '=?UTF-8?B?' . base64_encode($asunto) . '?=', $html, $cab, '-fhola@aurzane.com');
}
$url = 'https://aurzane.com/boletin/';

if (isset($_GET['baja'])) {   // también sirve para la baja de un clic de Gmail (POST)
    $tk = preg_replace('/[^a-f0-9]/', '', (string)$_GET['baja']); $s = leer($fs);
    foreach ($s as $e => $v) if (hash_equals((string)$v['baja'], $tk)) { unset($s[$e]); guardar($fs, $s); pagina('Te has dado de baja', 'No recibirás más correos de AURZANE. Gracias por haber estado.'); }
    pagina('Hecho', 'Este correo ya no está en la lista.');
}
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $email = strtolower(trim((string)($_POST['email'] ?? '')));
    if (!empty($_POST['web'])) pagina('Listo', 'Gracias.');                       // trampa para robots
    if (!filter_var($email, FILTER_VALIDATE_EMAIL) || strlen($email) > 160) pagina('Revisa el correo', 'Ese correo no parece válido. Vuelve atrás e inténtalo de nuevo.');
    if (empty($_POST['acepto'])) pagina('Falta tu permiso', 'Para enviarte el boletín necesitamos que marques la casilla de aceptación. Vuelve atrás y márcala.');
    $s = leer($fs);
    if (isset($s[$email])) pagina('Ya estás dentro', 'Este correo ya recibe el boletín semanal de AURZANE.');
    $p = leer($fp);
    foreach ($p as $k => $v) if (($v['t'] ?? 0) < time() - 7 * 86400) unset($p[$k]);   // limpia altas sin confirmar de más de 7 días
    if (count(array_filter($p, fn($v) => ($v['t'] ?? 0) > time() - 3600)) > 60) pagina('Inténtalo más tarde', 'Ahora mismo hay demasiadas altas. Prueba en un rato.');
    $tk = bin2hex(random_bytes(16));
    $p[$tk] = ['email' => $email, 't' => time(), 'origen' => substr((string)($_POST['origen'] ?? ''), 0, 120)];
    guardar($fp, $p);
    correo($email, 'Confirma tu suscripción al boletín de AURZANE',
        "<div style='font:16px/1.6 system-ui,sans-serif;max-width:520px'><p>Hola:</p><p>Para recibir cada semana el libro recomendado, el artículo nuevo y un test gratis de AURZANE, confirma tu correo:</p>"
        . "<p><a href='{$url}?confirmar=$tk' style='display:inline-block;background:#E2BF6A;color:#1b1440;padding:12px 22px;border-radius:99px;font-weight:700;text-decoration:none'>Confirmar suscripción</a></p>"
        . "<p style='color:#777;font-size:13px'>Si no lo has pedido tú, ignora este mensaje y no recibirás nada.</p></div>");
    pagina('Revisa tu correo', 'Te hemos enviado un enlace para confirmar. Si no lo ves en unos minutos, mira en la carpeta de spam o promociones.');
}
if (isset($_GET['confirmar'])) {
    $tk = preg_replace('/[^a-f0-9]/', '', (string)$_GET['confirmar']); $p = leer($fp);
    if (!isset($p[$tk])) pagina('Enlace caducado', 'Este enlace ya se usó o ha caducado. Puedes volver a suscribirte desde cualquier página de AURZANE.');
    $s = leer($fs); $e = $p[$tk]['email'];
    $s[$e] = ['alta' => date('c'), 'baja' => bin2hex(random_bytes(16)), 'origen' => $p[$tk]['origen'] ?? ''];
    unset($p[$tk]); guardar($fp, $p); guardar($fs, $s);
    pagina('¡Bienvenida, bienvenido!', 'Ya estás suscrito. Cada semana te llegará el libro recomendado, el artículo nuevo y un test gratis. Puedes darte de baja cuando quieras desde cualquier correo.');
}
pagina('Boletín semanal de AURZANE', "Cada semana, un correo corto con el libro recomendado, el artículo nuevo y un test gratis. Sin publicidad de terceros.<form method='post' action='$url' style='margin-top:22px;display:grid;gap:10px'>"
    . "<input type='email' name='email' required placeholder='tu@correo.com' style='padding:13px 16px;border-radius:12px;border:1px solid #333;font:inherit'>"
    . "<input type='text' name='web' tabindex='-1' autocomplete='off' style='position:absolute;left:-9999px' aria-hidden='true'>"
    . "<label style='font-size:14px;color:#b9b3a6'><input type='checkbox' name='acepto' value='1' required> Acepto recibir el boletín y la <a style='color:#E2BF6A' href='/privacidad.html'>política de privacidad</a>.</label>"
    . "<input type='hidden' name='origen' value='pagina-boletin'><button style='padding:13px;border:0;border-radius:99px;background:#E2BF6A;color:#1b1440;font-weight:700;font:inherit;cursor:pointer'>Suscribirme</button></form>");
