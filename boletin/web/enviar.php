<?php
// Se ejecuta por SSH desde GitHub (no es accesible por web: está protegido abajo). Envía boletin.html a cada suscrito con su enlace de baja.
// Por tandas (24/11/2026): como mucho LOTE correos por ejecución, para no pasar el límite de envíos por hora del hosting.
// El domingo la acción lo lanza cada hora hasta terminar. A quién ya se le ha enviado esta semana queda en envio-estado.json
// (con el correo cifrado), así nadie recibe el mismo boletín dos veces aunque se lance más de una vez.
if (php_sapi_name() !== 'cli') { http_response_code(404); exit; }
const LOTE = 120;
$dir = dirname(__DIR__, 2) . '/privado-boletin';
$s = is_file("$dir/suscritos.json") ? (json_decode(file_get_contents("$dir/suscritos.json"), true) ?: []) : [];
$asunto = trim((string)@file_get_contents("$dir/asunto.txt")); $html = (string)@file_get_contents("$dir/boletin.html");
if (!$asunto || !$html) { echo "falta el boletín\n"; exit(1); }
$fe = "$dir/envio-estado.json"; $semana = date('o-W');
$est = is_file($fe) ? (json_decode((string)file_get_contents($fe), true) ?: []) : [];
if (($est['semana'] ?? '') !== $semana) $est = ['semana' => $semana, 'hechos' => []];
$ok = 0; $fallos = 0;
foreach ($s as $e => $v) {
    $k = substr(hash('sha256', 'az' . $e), 0, 20);
    if (isset($est['hechos'][$k])) continue;
    if ($ok + $fallos >= LOTE) break;
    $baja = 'https://aurzane.com/boletin/?baja=' . $v['baja'];
    $cuerpo = str_replace('{{BAJA}}', $baja, $html);
    $cab = "MIME-Version: 1.0\r\nContent-Type: text/html; charset=UTF-8\r\nFrom: AURZANE <hola@aurzane.com>\r\nReply-To: hola@aurzane.com\r\nList-Unsubscribe: <$baja>\r\nList-Unsubscribe-Post: List-Unsubscribe=One-Click\r\n";
    if (mail($e, '=?UTF-8?B?' . base64_encode($asunto) . '?=', $cuerpo, $cab, '-fhola@aurzane.com')) { $ok++; $est['hechos'][$k] = 1; } else $fallos++;
    usleep(300000);
}
file_put_contents($fe, json_encode($est), LOCK_EX); chmod($fe, 0600);
$quedan = max(0, count($s) - count($est['hechos']));
echo "enviados $ok en esta tanda" . ($fallos ? ", $fallos fallos" : '') . "; llevan " . count($est['hechos']) . " de " . count($s) . ($quedan > 0 ? "; quedan $quedan para la próxima tanda" : '; terminado') . "\n";
