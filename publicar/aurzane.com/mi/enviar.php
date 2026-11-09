<?php
// Recordatorio mensual de Mi AURZANE (solo desde la línea de órdenes; lo lanza GitHub Actions por SSH).
// Escribe a quien activó el recordatorio si han pasado 30 días desde su último test y desde el último aviso.
if (php_sapi_name() !== 'cli') { http_response_code(404); exit; }
require __DIR__ . '/comun.php';
$prueba = in_array('--prueba', $argv, true); $enviados = 0;
foreach (glob(az_dir() . '/*.json') as $f) {
    $d = json_decode(file_get_contents($f), true) ?: [];
    if (empty($d['recordatorio']) || empty($d['email']) || empty($d['tests'])) continue;
    $ult = max(array_column($d['tests'], 'fecha'));
    if (strtotime($ult) > time() - 30 * 86400) continue;
    if (!empty($d['ultimo_aviso']) && strtotime($d['ultimo_aviso']) > time() - 28 * 86400) continue;
    $porTest = [];
    foreach ($d['tests'] as $x) $porTest[$x['clave']] = $x;   // el último de cada test
    $filas = '';
    foreach (array_slice(array_reverse($porTest), 0, 5) as $x) {
        $e = fn($s) => htmlspecialchars((string)$s, ENT_QUOTES, 'UTF-8');
        $filas .= '<li style="margin-bottom:8px"><b>' . $e($x['titulo']) . '</b>: ' . $e($x['nivel'] ?: ($x['valor'] . ($x['max'] ? ' de ' . $x['max'] : ''))) . ' (' . substr($x['fecha'], 0, 10) . ')'
                . ($x['url'] ? ' · <a href="' . $e($x['url']) . '?utm_source=recordatorio&utm_medium=email">Repetirlo</a>' : '') . '</li>';
    }
    $html = '<div style="font-family:Arial,sans-serif;font-size:15px;line-height:1.6;max-width:560px"><p>Hola:</p><p>Ha pasado un mes desde tu último test en AURZANE. Repetirlo de vez en cuando es la mejor forma de ver cómo evolucionas.</p><ul>' . $filas . '</ul>'
          . '<p><a href="https://aurzane.com/mi-aurzane.html?utm_source=recordatorio&utm_medium=email#tests" style="display:inline-block;background:#C9A24B;color:#080B17;padding:10px 18px;border-radius:99px;text-decoration:none;font-weight:bold">Ver mi evolución</a></p>'
          . '<p style="color:#777;font-size:13px">Recibes este correo porque activaste el recordatorio mensual en Mi AURZANE. Puedes desactivarlo allí mismo, en la tarjeta «Mis tests». Los tests son orientativos y no sustituyen una valoración profesional.</p></div>';
    if ($prueba) { echo "prueba: " . substr($d['email'], 0, 2) . "***\n"; continue; }
    $ok = mail($d['email'], '=?UTF-8?B?' . base64_encode('Un mes después: ¿repites tu test?') . '?=', $html,
               "MIME-Version: 1.0\r\nContent-Type: text/html; charset=UTF-8\r\nFrom: AURZANE <hola@aurzane.com>\r\nReply-To: hola@aurzane.com\r\n", '-fhola@aurzane.com');
    if ($ok) { $d['ultimo_aviso'] = gmdate('Y-m-d'); file_put_contents($f, json_encode($d, JSON_UNESCAPED_UNICODE), LOCK_EX); $enviados++; }
}
echo "Recordatorios enviados: $enviados\n";
