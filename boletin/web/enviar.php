<?php
// Se ejecuta por SSH desde GitHub (no es accesible por web: está protegido abajo). Envía boletin.html a cada suscrito con su enlace de baja.
if (php_sapi_name() !== 'cli') { http_response_code(404); exit; }
$dir = dirname(__DIR__, 2) . '/privado-boletin';
$s = is_file("$dir/suscritos.json") ? (json_decode(file_get_contents("$dir/suscritos.json"), true) ?: []) : [];
$asunto = trim((string)file_get_contents("$dir/asunto.txt")); $html = (string)file_get_contents("$dir/boletin.html");
if (!$asunto || !$html) { echo "falta el boletín\n"; exit(1); }
$ok = 0;
foreach ($s as $e => $v) {
    $baja = 'https://aurzane.com/boletin/?baja=' . $v['baja'];
    $cuerpo = str_replace('{{BAJA}}', $baja, $html);
    $cab = "MIME-Version: 1.0\r\nContent-Type: text/html; charset=UTF-8\r\nFrom: AURZANE <hola@aurzane.com>\r\nReply-To: hola@aurzane.com\r\nList-Unsubscribe: <$baja>\r\nList-Unsubscribe-Post: List-Unsubscribe=One-Click\r\n";
    if (mail($e, '=?UTF-8?B?' . base64_encode($asunto) . '?=', $cuerpo, $cab, '-fhola@aurzane.com')) $ok++;
    usleep(300000);
}
echo "enviados $ok de " . count($s) . "\n";
