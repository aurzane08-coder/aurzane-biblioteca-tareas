<?php
// Solicitudes de colegios (aurzane.com/colegios/): se guardan fuera de la web y se avisa por correo a AURZANE.
header('Content-Type: application/json; charset=utf-8'); header('Cache-Control: no-store');
if ($_SERVER['REQUEST_METHOD'] !== 'POST') { http_response_code(405); echo '{"ok":false,"error":"Usa el formulario."}'; exit; }
$in = json_decode(file_get_contents('php://input'), true) ?: [];
if (!empty($in['web'])) { echo '{"ok":true,"mensaje":"Gracias."}'; exit; }   // trampa para robots
$c = function ($k, $max) use ($in) { return mb_substr(trim(strip_tags((string)($in[$k] ?? ''))), 0, $max); };
$d = ['nombre' => $c('nombre', 120), 'cargo' => $c('cargo', 60), 'colegio' => $c('colegio', 160), 'ciudad' => $c('ciudad', 120),
      'correo' => $c('correo', 160), 'telefono' => $c('telefono', 40), 'estudiantes' => $c('estudiantes', 10), 'tipo' => $c('tipo', 20), 'mensaje' => $c('mensaje', 1500)];
if (!$d['nombre'] || !$d['colegio'] || !$d['ciudad'] || !$d['cargo'] || !filter_var($d['correo'], FILTER_VALIDATE_EMAIL) || empty($in['acepto'])) {
    http_response_code(400); echo '{"ok":false,"error":"Faltan datos obligatorios o el correo no es válido."}'; exit;
}
$dir = dirname(__DIR__, 2) . '/privado-colegios';
if (!is_dir($dir)) { @mkdir($dir, 0700, true); }
$hoy = gmdate('Y-m-d');
$ip = substr(hash('sha256', ($_SERVER['REMOTE_ADDR'] ?? '') . $hoy . 'aurzane'), 0, 16);
$f = "$dir/solicitudes.json"; $fp = fopen($f, 'c+'); flock($fp, LOCK_EX);
$l = json_decode(stream_get_contents($fp) ?: '', true) ?: [];
if (count(array_filter($l, fn($x) => ($x['ip'] ?? '') === $ip && substr($x['fecha'] ?? '', 0, 10) === $hoy)) >= 3) {
    flock($fp, LOCK_UN); fclose($fp); echo '{"ok":true,"mensaje":"Ya hemos recibido tu solicitud. Te escribimos pronto."}'; exit;
}
$l[] = $d + ['fecha' => gmdate('Y-m-d H:i'), 'ip' => $ip, 'estado' => 'nueva'];
ftruncate($fp, 0); rewind($fp); fwrite($fp, json_encode($l, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT)); fflush($fp); flock($fp, LOCK_UN); fclose($fp); @chmod($f, 0600);

$e = fn($s) => htmlspecialchars($s, ENT_QUOTES, 'UTF-8');
$filas = '';
foreach (['Nombre' => 'nombre', 'Cargo' => 'cargo', 'Colegio' => 'colegio', 'Ciudad' => 'ciudad', 'Correo' => 'correo', 'Teléfono' => 'telefono', 'Estudiantes' => 'estudiantes', 'Colegio militar' => 'tipo', 'Mensaje' => 'mensaje'] as $t => $k) {
    $v = $k === 'tipo' ? ($d[$k] === 'militar' ? 'Sí' : 'No') : $d[$k];
    if ($v !== '') $filas .= '<tr><td style="padding:6px 12px 6px 0;color:#666;vertical-align:top">' . $t . '</td><td style="padding:6px 0">' . nl2br($e($v)) . '</td></tr>';
}
$html = '<div style="font-family:Arial,sans-serif;font-size:15px"><h2 style="font-family:Georgia,serif">Nueva solicitud de colegio</h2><table>' . $filas . '</table>'
      . '<p style="color:#666;font-size:13px">Responde directamente a este correo para escribir a quien la envió.</p></div>';
$asunto = '=?UTF-8?B?' . base64_encode('Colegio interesado en OVP: ' . $d['colegio']) . '?=';
$cab = "MIME-Version: 1.0\r\nContent-Type: text/html; charset=UTF-8\r\nFrom: AURZANE <hola@aurzane.com>\r\nReply-To: " . $d['correo'] . "\r\n";
foreach (['hola@aurzane.com', 'aurzane08@gmail.com'] as $para) @mail($para, $asunto, $html, $cab, '-fhola@aurzane.com');

// acuse de recibo para quien escribe
$acuse = '<div style="font-family:Arial,sans-serif;font-size:15px;line-height:1.6"><p>Hola, ' . $e($d['nombre']) . ':</p>'
       . '<p>Hemos recibido la solicitud de <b>' . $e($d['colegio']) . '</b> para usar AURZANE OVP. Te escribiremos en los próximos días para preparar el membrete y el enlace de tu colegio.</p>'
       . '<p>Mientras tanto, puedes ver un informe de ejemplo: <a href="https://ovp.aurzane.com/informe-ejemplo.html">ovp.aurzane.com/informe-ejemplo.html</a></p>'
       . '<p>Un saludo,<br>Adrián Sánchez<br>Psicólogo clínico · AURZANE OVP</p></div>';
@mail($d['correo'], '=?UTF-8?B?' . base64_encode('Hemos recibido tu solicitud · AURZANE OVP') . '?=', $acuse,
      "MIME-Version: 1.0\r\nContent-Type: text/html; charset=UTF-8\r\nFrom: AURZANE <hola@aurzane.com>\r\nReply-To: hola@aurzane.com\r\n", '-fhola@aurzane.com');

echo json_encode(['ok' => true, 'mensaje' => 'Solicitud enviada. Te escribimos pronto al correo que nos has dejado.'], JSON_UNESCAPED_UNICODE);
