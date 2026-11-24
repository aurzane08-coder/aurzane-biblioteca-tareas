<?php
// Enviar por correo el resultado de un test de MIND (24/11/2026).
// El navegador solo manda qué test es, la puntuación y el correo. El texto del correo (título, nivel, explicación y consejos)
// lo saca este archivo de la propia página oficial del test en el servidor, así nadie puede usarlo para mandar mensajes
// inventados. No se guarda el resultado: solo se envía. Para frenar abusos se cuentan los envíos (con el correo y la IP
// cifrados) en privado-boletin/limites.json. Si la persona marca la casilla, también se le ofrece el boletín con doble
// confirmación (un botón en el mismo correo).
declare(strict_types=1);
$origen = (string)($_SERVER['HTTP_ORIGIN'] ?? '');
if (preg_match('#^https://([a-z]+\.)?aurzane\.com$#', $origen)) { header("Access-Control-Allow-Origin: $origen"); header('Vary: Origin'); }
header('Access-Control-Allow-Methods: POST, OPTIONS'); header('Access-Control-Allow-Headers: Content-Type');
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') { http_response_code(204); exit; }
header('Content-Type: application/json; charset=utf-8');
function fin(bool $ok, string $msg) { echo json_encode(['ok' => $ok, 'msg' => $msg], JSON_UNESCAPED_UNICODE); exit; }
if ($_SERVER['REQUEST_METHOD'] !== 'POST') fin(false, 'Método no permitido.');

$dir = dirname(__DIR__, 2) . '/privado-boletin';
if (!is_dir($dir)) { mkdir($dir, 0700, true); }
function leer($f) { return is_file($f) ? (json_decode((string)file_get_contents($f), true) ?: []) : []; }
function guardar($f, $d) { file_put_contents($f, json_encode($d, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT), LOCK_EX); chmod($f, 0600); }
$e = fn($s) => htmlspecialchars((string)$s, ENT_QUOTES, 'UTF-8');

$email = strtolower(trim((string)($_POST['email'] ?? '')));
$slug = (string)($_POST['test'] ?? '');
$pts = str_replace(',', '.', (string)($_POST['puntos'] ?? ''));
if (!empty($_POST['web'])) fin(true, 'Enviado.');   // trampa para robots
if (!filter_var($email, FILTER_VALIDATE_EMAIL) || strlen($email) > 160) fin(false, 'Ese correo no parece válido. Revísalo e inténtalo de nuevo.');
if (!preg_match('/^test-de-[a-z-]{3,40}$/', $slug) || !is_numeric($pts)) fin(false, 'No se pudo leer el resultado. Recarga la página y vuelve a calcularlo.');

// la configuración oficial del test, de su propia página
$pagina = @file_get_contents(dirname(__DIR__, 3) . "/mind.aurzane.com/public_html/$slug/index.html");
if (!$pagina || !preg_match('/var CFG=(\{.*?\});\s*\n/s', $pagina, $m)) fin(false, 'Este test todavía no permite enviar el resultado por correo.');
$cfg = json_decode($m[1], true);
if (!$cfg || empty($cfg['niveles'])) fin(false, 'Este test todavía no permite enviar el resultado por correo.');
$v = (float)$pts;
$nivel = null;
foreach ($cfg['niveles'] as $n) if ($v >= $n[0] && $v <= $n[1] + 0.0001) { $nivel = $n; break; }
if (!$nivel) { $d = 1e9; foreach ($cfg['niveles'] as $n) { $x = min(abs($v - $n[0]), abs($v - $n[1])); if ($x < $d) { $d = $x; $nivel = $n; } } }   // redondeo entre dos tramos
if ($v < (float)($cfg['min'] ?? 0) || $v > (float)($cfg['max'] ?? 1000)) fin(false, 'No se pudo leer el resultado. Recarga la página y vuelve a calcularlo.');

// límites: 4 por hora desde una IP, 3 al día al mismo correo y 300 al día en total
$fl = "$dir/limites.json"; $l = leer($fl); $ahora = time();
foreach ($l as $k => $ts) { $l[$k] = array_values(array_filter((array)$ts, fn($t) => $t > $ahora - 86400)); if (!$l[$k]) unset($l[$k]); }
$kip = 'ip' . substr(hash('sha256', 'az' . ($_SERVER['REMOTE_ADDR'] ?? '')), 0, 20); $kem = 'em' . substr(hash('sha256', 'az' . $email), 0, 20);
$enHora = count(array_filter($l[$kip] ?? [], fn($t) => $t > $ahora - 3600));
$total = array_sum(array_map('count', array_filter($l, fn($k) => str_starts_with((string)$k, 'ip'), ARRAY_FILTER_USE_KEY)));
if ($enHora >= 4 || count($l[$kem] ?? []) >= 3 || $total >= 300) fin(false, 'Has enviado varios resultados seguidos. Inténtalo de nuevo más tarde.');

$url = "https://mind.aurzane.com/$slug/";
$valor = rtrim(rtrim(number_format($v, 2, ',', ''), '0'), ',');
$consejos = '';
foreach (array_slice((array)($cfg['consejos'] ?? []), 0, 6) as $c) $consejos .= "<li style='margin:0 0 10px'><b>{$e($c[0])}.</b> {$e($c[1] ?? '')}</li>";
$ayuda = $nivel[2] === 'mal'
    ? "<p style='background:#f6efe2;border-radius:12px;padding:14px 16px'><b>Pedir ayuda funciona.</b> Tu médico de cabecera puede derivarte a psicología, o puedes buscar un psicólogo sanitario colegiado. Si en algún momento piensas en hacerte daño, llama al <b>024</b> (España), gratis y a cualquier hora.</p>" : '';
$bol = '';
if (!empty($_POST['boletin'])) {
    $s = leer("$dir/suscritos.json");
    if (!isset($s[$email])) {
        $fp = "$dir/pendientes.json"; $p = leer($fp); $tk = bin2hex(random_bytes(16));
        $p[$tk] = ['email' => $email, 't' => $ahora, 'origen' => "resultado:$slug"]; guardar($fp, $p);
        $bol = "<p style='margin-top:26px'>Pediste recibir también el boletín semanal de AURZANE. Confírmalo con este botón (si no, no te llegará nada):</p>"
             . "<p><a href='https://aurzane.com/boletin/?confirmar=$tk' style='display:inline-block;background:#E2BF6A;color:#1b1440;padding:11px 20px;border-radius:99px;font-weight:700;text-decoration:none'>Confirmar el boletín</a></p>";
    }
}
$html = "<div style='font:16px/1.6 system-ui,-apple-system,sans-serif;color:#1d1f1c;max-width:560px;margin:auto'>"
    . "<p style='letter-spacing:.08em;color:#183D32;font-weight:700;margin:0 0 18px'>AURZANE · MIND</p>"
    . "<h1 style='font-size:1.45rem;margin:0 0 6px'>{$e($cfg['titulo'] ?? 'Tu resultado')}</h1>"
    . "<p style='margin:0 0 18px;color:#5e605a'>Tu resultado de hoy, " . date('j/n/Y') . "</p>"
    . "<div style='background:#183D32;color:#F6F5F0;border-radius:16px;padding:20px 22px;margin:0 0 18px'><div style='font-size:2rem;font-weight:700;line-height:1'>$valor <span style='font-size:1rem;font-weight:400'>de {$e($cfg['max'] ?? '')}</span></div>"
    . "<div style='margin-top:6px;font-size:1.1rem;color:#D9CDB2'>{$e($nivel[3])}</div></div>"
    . "<p>{$e($nivel[4])}</p>$ayuda"
    . ($consejos ? "<h2 style='font-size:1.1rem;margin:22px 0 10px'>Qué puedes hacer</h2><ul style='padding-left:20px;margin:0'>$consejos</ul>" : '')
    . "<p style='margin-top:22px'><a href='$url?utm_source=correo&utm_medium=email&utm_campaign=resultado' style='display:inline-block;background:#183D32;color:#F6F5F0;padding:11px 20px;border-radius:99px;font-weight:700;text-decoration:none'>Ver el test y la guía completa</a></p>"
    . "<p style='color:#5e605a;font-size:14px'>Este resultado es orientativo y no sustituye la valoración de un profesional. AURZANE no guarda tus respuestas ni este resultado: solo te lo hemos enviado.</p>"
    . $bol
    . "<p style='color:#8a8c86;font-size:12px;margin-top:26px'>Recibes este correo porque lo pediste desde $url. Si no fuiste tú, ignóralo: no te llegará nada más.</p></div>";
$cab = "MIME-Version: 1.0\r\nContent-Type: text/html; charset=UTF-8\r\nFrom: AURZANE <hola@aurzane.com>\r\nReply-To: hola@aurzane.com\r\n";
$asunto = 'Tu resultado: ' . ($cfg['titulo'] ?? 'test de AURZANE');
if (!mail($email, '=?UTF-8?B?' . base64_encode($asunto) . '?=', $html, $cab, '-fhola@aurzane.com')) fin(false, 'No se pudo enviar ahora mismo. Inténtalo en unos minutos.');
$l[$kip][] = $ahora; $l[$kem][] = $ahora; guardar($fl, $l);
fin(true, 'Listo. Te lo hemos enviado a ' . $email . '. Si no lo ves en unos minutos, mira en spam o promociones.');
