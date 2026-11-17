<?php
// Patrocinios de universidades en AURZANE NEXUS (fase 4, punto 60; 17/11/2026).
// 1. La universidad pide su mes gratis en nexus.aurzane.com/universidades/anunciate/ (POST aquí).
// 2. Adrián recibe un correo con botones para aprobar o rechazar (enlaces con clave única; se confirma con un botón para que
//    ningún filtro de correo lo apruebe solo al abrir el enlace).
// 3. Al aprobar empieza la prueba: la universidad recibe un correo con las fechas y su ficha sale destacada en la siguiente
//    publicación diaria. Cuando paga (fuera de la web), el botón «Renovar» del correo alarga 1 mes o 1 año.
// 4. Cada día (php patrocinio.php diario, desde el flujo «Universidades publicar portal»): avisos 5 días antes del final
//    y al terminar, y la lista pública de activos (sin datos de contacto) que usa el generador.
// Los datos de contacto se guardan fuera de la web (privado-patrocinios) y nunca se publican.
$DIR = dirname(__DIR__) . '/privado-patrocinios';
$F = "$DIR/solicitudes.json";
$ADMIN = ['hola@aurzane.com', 'aurzane08@gmail.com'];
$PRUEBA = 30;
define('PRECIO_TXT', '29 € al mes o 290 € al año, IVA no incluido');   // igual que univ/data/patrocinios.json
$YO = 'https://aurzane.com/patrocinio.php';
if (!is_dir($DIR)) @mkdir($DIR, 0700, true);

function cargar($F) { return is_file($F) ? (json_decode(file_get_contents($F), true) ?: []) : []; }
function guardar($F, $l) { file_put_contents($F, json_encode(array_values($l), JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES), LOCK_EX); @chmod($F, 0600); }
function h($s) { return htmlspecialchars((string)$s, ENT_QUOTES, 'UTF-8'); }
function fecha($f) { $m = ['', 'enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre'];
    [$a, $mm, $d] = explode('-', $f); return intval($d) . ' de ' . $m[intval($mm)] . ' de ' . $a; }
function correo($para, $asunto, $cuerpo, $responder = '') {
    $html = '<div style="font-family:Arial,sans-serif;font-size:15px;line-height:1.55;color:#1b1a2e;max-width:600px">' . $cuerpo
          . '<p style="color:#777;font-size:13px;margin-top:28px">AURZANE NEXUS · <a href="https://nexus.aurzane.com/universidades/">nexus.aurzane.com/universidades</a></p></div>';
    $cab = "MIME-Version: 1.0\r\nContent-Type: text/html; charset=UTF-8\r\nFrom: AURZANE <hola@aurzane.com>\r\n" . ($responder ? "Reply-To: $responder\r\n" : '');
    foreach ((array)$para as $p) @mail($p, '=?UTF-8?B?' . base64_encode($asunto) . '?=', $html, $cab, '-fhola@aurzane.com');
}
function boton($url, $texto, $color = '#3a50c4') { return '<a href="' . h($url) . '" style="display:inline-block;margin:4px 6px 4px 0;padding:11px 18px;border-radius:99px;background:' . $color . ';color:#fff;text-decoration:none;font-weight:bold">' . h($texto) . '</a>'; }
function mas($f, $dias) { return gmdate('Y-m-d', strtotime("$f +$dias days")); }
function ficha($s) { return 'https://nexus.aurzane.com/universidades/' . $s['id'] . '/'; }
function activos($F, $DIR) {   // lista pública: solo lo que ya se ve en la web (ficha, fechas, frase y enlace de admisión)
    $hoy = gmdate('Y-m-d'); $out = [];
    foreach (cargar($F) as $s) if (in_array($s['estado'], ['prueba', 'activo']) && $s['desde'] <= $hoy && $hoy <= $s['hasta'])
        $out[] = ['id' => $s['id'], 'desde' => $s['desde'], 'hasta' => $s['hasta'], 'texto' => $s['texto'], 'url' => $s['admision'], 'nombre' => $s['universidad']];
    file_put_contents("$DIR/activos.json", json_encode($out, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES)); return $out;
}
function botones_admin($YO, $t) {
    return boton("$YO?a=aprobar&t=$t", 'Aprobar mes gratis', '#2f7d4f') . boton("$YO?a=renovar1&t=$t", 'Pagó: +1 mes') . boton("$YO?a=renovar12&t=$t", 'Pagó: +1 año')
         . boton("$YO?a=baja&t=$t", 'Dar de baja', '#8a8a8a') . boton("$YO?a=rechazar&t=$t", 'Rechazar', '#b0413e');
}

// ---------- tarea diaria (solo desde la consola del servidor) ----------
if (PHP_SAPI === 'cli') {
    $l = cargar($F); $hoy = gmdate('Y-m-d'); $cambio = false;
    foreach ($l as &$s) {
        if (!in_array($s['estado'], ['prueba', 'activo'])) continue;
        if ($s['hasta'] === mas($hoy, 5) && ($s['aviso5'] ?? '') !== $s['hasta']) {
            $s['aviso5'] = $s['hasta']; $cambio = true;
            correo($s['correo'], 'Tu destacado en AURZANE NEXUS termina el ' . fecha($s['hasta']),
                '<p>Hola, ' . h($s['nombre']) . ':</p><p>El destacado de <b>' . h($s['universidad']) . '</b> en AURZANE NEXUS termina el <b>' . fecha($s['hasta']) . '</b>.</p>'
                . '<p>Si quieres seguir, responde a este correo y te enviamos la factura: ' . h(PRECIO_TXT) . '. Si no respondes, tu ficha vuelve a ser normal sola, sin ningún cargo.</p>'
                . '<p>Ver tu ficha: <a href="' . ficha($s) . '">' . ficha($s) . '</a></p>', 'hola@aurzane.com');
            correo($ADMIN, 'Patrocinio: ' . $s['universidad'] . ' termina en 5 días', '<p><b>' . h($s['universidad']) . '</b> (' . h($s['correo']) . ') termina el ' . fecha($s['hasta'])
                . '. Ya le he avisado. Si paga, pulsa renovar:</p><p>' . botones_admin($YO, $s['token']) . '</p>');
        }
        if ($s['hasta'] < $hoy) {
            $s['estado'] = 'terminado'; $cambio = true;
            correo($s['correo'], 'Tu destacado en AURZANE NEXUS ha terminado', '<p>Hola, ' . h($s['nombre']) . ':</p><p>El destacado de <b>' . h($s['universidad'])
                . '</b> terminó el ' . fecha($s['hasta']) . ' y tu ficha ya es normal. Gracias por confiar en AURZANE NEXUS. Si quieres volver, responde a este correo.</p>', 'hola@aurzane.com');
        }
    }
    unset($s);
    if ($cambio) guardar($F, $l);
    echo json_encode(activos($F, $DIR), JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
    exit;
}

$o = $_SERVER['HTTP_ORIGIN'] ?? ''; if (preg_match('#^https://([a-z0-9-]+\.)?aurzane\.com$#', $o)) { header('Access-Control-Allow-Origin: ' . $o); header('Vary: Origin'); }
if (($_SERVER['REQUEST_METHOD'] ?? '') === 'OPTIONS') { header('Access-Control-Allow-Methods: POST'); header('Access-Control-Allow-Headers: Content-Type'); exit; }
header('Cache-Control: no-store'); header('X-Robots-Tag: noindex, nofollow');

// ---------- botones del correo de Adrián ----------
$a = $_GET['a'] ?? ''; $t = preg_replace('/[^a-f0-9]/', '', $_GET['t'] ?? '');
if ($a && $t) {
    header('Content-Type: text/html; charset=utf-8');
    $acc = ['aprobar' => 'Aprobar el mes gratis', 'renovar1' => 'Alargar 1 mes (ya ha pagado)', 'renovar12' => 'Alargar 1 año (ya ha pagado)', 'baja' => 'Dar de baja hoy', 'rechazar' => 'Rechazar la solicitud'];
    $l = cargar($F); $i = null;
    foreach ($l as $k => $s) if (hash_equals($s['token'], $t)) $i = $k;
    $pag = fn($c) => '<!doctype html><html lang="es"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Patrocinio NEXUS</title>'
        . '<body style="font-family:Arial,sans-serif;max-width:560px;margin:40px auto;padding:0 18px;line-height:1.5;color:#1b1a2e">' . $c . '</body></html>';
    if ($i === null || !isset($acc[$a])) { http_response_code(404); echo $pag('<p>Enlace no válido.</p>'); exit; }
    $s = &$l[$i];
    $info = '<p><b>' . h($s['universidad']) . '</b><br>' . h($s['nombre']) . ' · ' . h($s['correo']) . '<br>Estado: ' . h($s['estado'])
          . ($s['hasta'] ? ' · del ' . fecha($s['desde']) . ' al ' . fecha($s['hasta']) : '') . '</p>';
    if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST') {   // primero se confirma: así ningún antivirus del correo lo activa solo
        echo $pag("<h1 style='font-size:22px'>{$acc[$a]}</h1>$info<form method='post'><button style='font-size:16px;padding:12px 22px;border-radius:99px;border:0;background:#3a50c4;color:#fff;font-weight:bold'>Confirmar</button></form>"); exit;
    }
    $hoy = gmdate('Y-m-d');
    if ($a === 'aprobar') {
        if ($s['estado'] === 'pendiente') {
            $s['estado'] = 'prueba'; $s['desde'] = $hoy; $s['hasta'] = mas($hoy, $PRUEBA - 1);
            correo($s['correo'], 'Tu mes gratis en AURZANE NEXUS ya ha empezado', '<p>Hola, ' . h($s['nombre']) . ':</p><p>Hemos aprobado tu solicitud. <b>' . h($s['universidad'])
                . '</b> sale destacada en AURZANE NEXUS del <b>' . fecha($s['desde']) . '</b> al <b>' . fecha($s['hasta']) . '</b>, gratis y sin compromiso.</p>'
                . '<ul><li>Primeras posiciones en tu país y tu ciudad, con la etiqueta «Patrocinado».</li><li>Botón a tu página de admisión con UTM (utm_source=aurzane) para medir las visitas.</li></ul>'
                . '<p>Lo verás en tu ficha en menos de 24 horas: <a href="' . ficha($s) . '">' . ficha($s) . '</a></p>'
                . '<p>Unos días antes de terminar te escribimos. Si no quieres seguir, no tienes que hacer nada: tu ficha vuelve a ser normal sola.</p>', 'hola@aurzane.com');
        }
    } elseif ($a === 'renovar1' || $a === 'renovar12') {
        $base = ($s['hasta'] && $s['hasta'] >= $hoy) ? mas($s['hasta'], 1) : $hoy;
        if (!$s['desde'] || $s['hasta'] < $hoy) $s['desde'] = $base;
        $s['hasta'] = gmdate('Y-m-d', strtotime($base . ($a === 'renovar1' ? ' +1 month' : ' +1 year') . ' -1 day')); $s['estado'] = 'activo';
        correo($s['correo'], 'Destacado renovado en AURZANE NEXUS', '<p>Hola, ' . h($s['nombre']) . ':</p><p>Gracias. <b>' . h($s['universidad']) . '</b> sigue destacada hasta el <b>' . fecha($s['hasta']) . '</b>.</p>', 'hola@aurzane.com');
    } elseif ($a === 'baja') { if (in_array($s['estado'], ['prueba', 'activo'])) { $s['hasta'] = mas($hoy, -1); $s['estado'] = 'terminado'; } }
    elseif ($a === 'rechazar') { if ($s['estado'] === 'pendiente') $s['estado'] = 'rechazada'; }
    $s['historial'][] = gmdate('Y-m-d H:i') . ' ' . $a;
    unset($s); guardar($F, $l); activos($F, $DIR);
    $s = $l[$i];
    echo $pag('<h1 style="font-size:22px">Hecho</h1><p>' . h($acc[$a]) . ':</p><p><b>' . h($s['universidad']) . '</b><br>Estado: ' . h($s['estado'])
        . ($s['hasta'] ? '<br>Del ' . fecha($s['desde']) . ' al ' . fecha($s['hasta']) : '') . '</p><p>Aparece o desaparece de NEXUS en la siguiente publicación diaria.</p>');
    exit;
}

// ---------- solicitud desde el formulario ----------
header('Content-Type: application/json; charset=utf-8');
if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST') { http_response_code(405); echo '{"ok":false,"error":"Usa el formulario."}'; exit; }
$in = json_decode(file_get_contents('php://input'), true) ?: [];
if (!empty($in['web'])) { echo '{"ok":true}'; exit; }
$c = fn($k, $n) => mb_substr(trim(strip_tags((string)($in[$k] ?? ''))), 0, $n);
$d = ['universidad' => $c('universidad', 160), 'id' => $c('id', 160), 'nombre' => $c('nombre', 120), 'correo' => $c('correo', 160),
      'admision' => $c('admision', 300), 'texto' => $c('texto', 90), 'mensaje' => $c('mensaje', 2000)];
$err = !$d['universidad'] || !$d['nombre'] || empty($in['acepto']) ? 'Faltan datos.'
     : (!filter_var($d['correo'], FILTER_VALIDATE_EMAIL) ? 'El correo no es válido.'
     : (!preg_match('#^[a-z0-9-]+/[a-z0-9-]+$#', $d['id']) ? 'Elige tu universidad de la lista que aparece al escribir.'
     : (!preg_match('#^https://[^\s<>"]+\.[^\s<>"]+#', $d['admision']) ? 'Escribe la dirección completa de tu página de admisión (https://…).' : '')));
if ($err) { http_response_code(400); echo json_encode(['ok' => false, 'error' => $err], JSON_UNESCAPED_UNICODE); exit; }
$l = cargar($F); $hoy = gmdate('Y-m-d');
$ip = substr(hash('sha256', ($_SERVER['REMOTE_ADDR'] ?? '') . $hoy . 'aurzane'), 0, 16);
if (count(array_filter($l, fn($x) => ($x['ip'] ?? '') === $ip && substr($x['fecha'], 0, 10) === $hoy)) >= 3) { echo '{"ok":true,"mensaje":"Ya hemos recibido tu solicitud. Te escribimos pronto."}'; exit; }
foreach ($l as $x) if ($x['id'] === $d['id'] && in_array($x['estado'], ['pendiente', 'prueba', 'activo'])) {
    echo json_encode(['ok' => true, 'mensaje' => 'Esta universidad ya tiene una solicitud o un destacado en curso. Te escribimos al correo.'], JSON_UNESCAPED_UNICODE); exit; }
$tok = bin2hex(random_bytes(16));
$l[] = $d + ['token' => $tok, 'estado' => 'pendiente', 'desde' => '', 'hasta' => '', 'fecha' => gmdate('Y-m-d H:i'), 'ip' => $ip, 'historial' => []];
guardar($F, array_slice($l, -500));
correo($ADMIN, 'Patrocinio NEXUS: ' . $d['universidad'], '<p><b>Nueva solicitud de mes gratis</b></p><p><b>' . h($d['universidad']) . '</b> (<a href="' . ficha($d) . '">ficha</a>)<br>'
    . h($d['nombre']) . ' · ' . h($d['correo']) . '<br>Admisión: <a href="' . h($d['admision']) . '">' . h($d['admision']) . '</a><br>Frase: ' . h($d['texto'] ?: '(sin frase)') . '</p>'
    . ($d['mensaje'] ? '<p>' . nl2br(h($d['mensaje'])) . '</p>' : '') . '<p>Antes de aprobar, comprueba que el correo es de la universidad (mismo dominio que su web).</p><p>'
    . botones_admin($YO, $tok) . '</p>', $d['correo']);
correo($d['correo'], 'Hemos recibido tu solicitud para AURZANE NEXUS', '<p>Hola, ' . h($d['nombre']) . ':</p><p>Gracias por tu interés en destacar <b>' . h($d['universidad'])
    . '</b>. Revisamos la solicitud en un plazo de 2 días laborables y te escribimos para activar tu mes gratis.</p>', 'hola@aurzane.com');
echo json_encode(['ok' => true, 'mensaje' => 'Recibido. Revisamos tu solicitud en 2 días laborables y te escribimos al correo.'], JSON_UNESCAPED_UNICODE);
