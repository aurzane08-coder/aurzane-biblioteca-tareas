<?php
// Formulario de contacto de aurzane.com/contacto.html: se guarda fuera de la web y se avisa por correo.
header('Content-Type: application/json; charset=utf-8'); header('Cache-Control: no-store');
if ($_SERVER['REQUEST_METHOD'] !== 'POST') { http_response_code(405); echo '{"ok":false,"error":"Usa el formulario."}'; exit; }
$in = json_decode(file_get_contents('php://input'), true) ?: [];
if (!empty($in['web'])) { echo '{"ok":true,"mensaje":"Gracias."}'; exit; }
$c = fn($k, $n) => mb_substr(trim(strip_tags((string)($in[$k] ?? ''))), 0, $n);
$d = ['nombre' => $c('nombre', 120), 'correo' => $c('correo', 160), 'motivo' => $c('motivo', 80), 'mensaje' => $c('mensaje', 3000)];
if (!$d['nombre'] || !$d['motivo'] || mb_strlen($d['mensaje']) < 5 || !filter_var($d['correo'], FILTER_VALIDATE_EMAIL) || empty($in['acepto'])) {
    http_response_code(400); echo '{"ok":false,"error":"Faltan datos o el correo no es válido."}'; exit;
}
$dir = dirname(__DIR__) . '/privado-contacto'; if (!is_dir($dir)) @mkdir($dir, 0700, true);
$hoy = gmdate('Y-m-d'); $ip = substr(hash('sha256', ($_SERVER['REMOTE_ADDR'] ?? '') . $hoy . 'aurzane'), 0, 16);
$f = "$dir/mensajes.json"; $fp = fopen($f, 'c+'); flock($fp, LOCK_EX);
$l = json_decode(stream_get_contents($fp) ?: '', true) ?: [];
if (count(array_filter($l, fn($x) => ($x['ip'] ?? '') === $ip && substr($x['fecha'] ?? '', 0, 10) === $hoy)) >= 5) { flock($fp, LOCK_UN); fclose($fp); echo '{"ok":true,"mensaje":"Ya hemos recibido tus mensajes de hoy. Te respondemos pronto."}'; exit; }
$l[] = $d + ['fecha' => gmdate('Y-m-d H:i'), 'ip' => $ip, 'estado' => 'nuevo']; $l = array_slice($l, -1000);
ftruncate($fp, 0); rewind($fp); fwrite($fp, json_encode($l, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT)); fflush($fp); flock($fp, LOCK_UN); fclose($fp); @chmod($f, 0600);
$e = fn($s) => nl2br(htmlspecialchars($s, ENT_QUOTES, 'UTF-8'));
$html = '<div style="font-family:Arial,sans-serif;font-size:15px"><p><b>' . $e($d['motivo']) . '</b></p><p>De: ' . $e($d['nombre']) . ' (' . $e($d['correo']) . ')</p><p>' . $e($d['mensaje']) . '</p></div>';
$cab = "MIME-Version: 1.0\r\nContent-Type: text/html; charset=UTF-8\r\nFrom: AURZANE <hola@aurzane.com>\r\nReply-To: " . $d['correo'] . "\r\n";
foreach (['hola@aurzane.com', 'aurzane08@gmail.com'] as $para) @mail($para, '=?UTF-8?B?' . base64_encode('Contacto web: ' . $d['motivo']) . '?=', $html, $cab, '-fhola@aurzane.com');
echo json_encode(['ok' => true, 'mensaje' => 'Mensaje enviado. Te responderemos al correo que nos has dejado.'], JSON_UNESCAPED_UNICODE);
