<?php
// Patrocinios de universidades en AURZANE NEXUS (fase 4, punto 60; 17/11/2026).
// 1. La universidad pide su mes gratis en nexus.aurzane.com/universidades/anunciate/ (POST aquí).
// 2. Adrián recibe un correo con botones para aprobar o rechazar (enlaces con clave única; se confirma con un botón para que
//    ningún filtro de correo lo apruebe solo al abrir el enlace).
// 3. Al aprobar empieza la prueba: la universidad recibe un correo con las fechas y su ficha sale destacada en la siguiente
//    publicación diaria. La universidad paga con Stripe (tarjeta, Google Pay, Apple Pay, Link, Revolut Pay, SEPA, transferencia…)
//    desde los botones de pago de sus correos; Stripe avisa aquí (?stripe=1, firma comprobada) y el destacado se alarga solo
//    un mes o un año por cada pago, también en las renovaciones automáticas. Si cancela en el portal de Stripe, sigue hasta fin del periodo.
// 5. Todo se gestiona también desde aurzane.com/admin.html, pestaña «Patrocinios» (solo administradores: es_admin() de Supabase).
// 4. Cada día (php patrocinio.php diario, desde el flujo «Universidades publicar portal»): avisos 5 días antes del final
//    y al terminar, y la lista pública de activos (sin datos de contacto) que usa el generador.
// Los datos de contacto se guardan fuera de la web (privado-patrocinios) y nunca se publican.
$DIR = dirname(__DIR__) . '/privado-patrocinios';
$F = "$DIR/solicitudes.json";
$ADMIN = ['hola@aurzane.com', 'aurzane08@gmail.com'];
$PRUEBA = 30;
define('PRECIO_TXT', '29 € al mes o 290 € al año, IVA no incluido');   // igual que univ/data/patrocinios.json
$YO = 'https://aurzane.com/patrocinio.php';
// Enlaces de pago de Stripe (creados el 18/11/2026; suscripción que se renueva sola, IVA aparte si procede)
define('PAGO_MES', 'https://buy.stripe.com/aFaeVc2Rl2qo0X15yZdUY00');
define('PAGO_ANIO', 'https://buy.stripe.com/bJe7sKdvZaWU7lp5yZdUY01');
define('PORTAL', 'https://billing.stripe.com/p/login/aFaeVc2Rl2qo0X15yZdUY00');   // la universidad cancela o cambia la tarjeta aquí
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
function enlace_pago($s, $anual) {   // client_reference_id = clave de la solicitud: así el pago se asocia solo a su universidad
    return ($anual ? PAGO_ANIO : PAGO_MES) . '?client_reference_id=' . $s['token'] . '&prefilled_email=' . rawurlencode($s['correo']) . '&locale=es';
}
function botones_pago($s) {
    return '<p>' . boton(enlace_pago($s, false), 'Seguir: 29 € al mes', '#2f7d4f') . boton(enlace_pago($s, true), 'Seguir: 290 € al año (2 meses gratis)', '#3a50c4') . '</p>'
         . '<p style="color:#555;font-size:13px">Puedes pagar con tarjeta, Google Pay, Apple Pay, Link, Revolut Pay, adeudo SEPA o transferencia. Recibes la factura al momento y la suscripción se renueva sola; la cancelas cuando quieras en <a href="' . PORTAL . '">tu portal de pagos</a>. IVA aparte si corresponde.</p>';
}
// alarga el destacado un periodo pagado: empieza al día siguiente del final actual (o hoy, si ya terminó), así no se pierden días de la prueba
function alargar(&$s, $anual, $hoy) {
    $base = ($s['hasta'] && $s['hasta'] >= $hoy) ? mas($s['hasta'], 1) : $hoy;
    if (!$s['desde'] || $s['hasta'] < $hoy) $s['desde'] = $base;
    $s['hasta'] = gmdate('Y-m-d', strtotime($base . ($anual ? ' +1 year' : ' +1 month') . ' -1 day')); $s['estado'] = 'activo';
}
// las acciones del administrador (botones del correo o pestaña Patrocinios de admin.html)
function accion($a, &$s, $hoy, $PRUEBA) {
    if ($a === 'aprobar') {
        if ($s['estado'] !== 'pendiente') return false;
        $s['estado'] = 'prueba'; $s['desde'] = $hoy; $s['hasta'] = mas($hoy, $PRUEBA - 1);
        correo($s['correo'], 'Tu mes gratis en AURZANE NEXUS ya ha empezado', '<p>Hola, ' . h($s['nombre']) . ':</p><p>Hemos aprobado tu solicitud. <b>' . h($s['universidad'])
            . '</b> sale destacada en AURZANE NEXUS del <b>' . fecha($s['desde']) . '</b> al <b>' . fecha($s['hasta']) . '</b>, gratis y sin compromiso.</p>'
            . '<ul><li>Primeras posiciones en tu país y tu ciudad, con la etiqueta «Patrocinado».</li><li>Botón a tu página de admisión con UTM (utm_source=aurzane) para medir las visitas.</li></ul>'
            . '<p>Lo verás en tu ficha en menos de 12 horas: <a href="' . ficha($s) . '">' . ficha($s) . '</a></p>'
            . '<p>Si no quieres seguir, no tienes que hacer nada: tu ficha vuelve a ser normal sola. Si quieres continuar después del mes gratis, puedes dejarlo listo ya (el pago empieza a contar cuando acaba la prueba):</p>' . botones_pago($s), 'hola@aurzane.com');
    } elseif ($a === 'renovar1' || $a === 'renovar12') {
        alargar($s, $a === 'renovar12', $hoy);
        correo($s['correo'], 'Destacado renovado en AURZANE NEXUS', '<p>Hola, ' . h($s['nombre']) . ':</p><p>Gracias. <b>' . h($s['universidad']) . '</b> sigue destacada hasta el <b>' . fecha($s['hasta']) . '</b>.</p>', 'hola@aurzane.com');
    } elseif ($a === 'baja') { if (!in_array($s['estado'], ['prueba', 'activo'])) return false; $s['hasta'] = mas($hoy, -1); $s['estado'] = 'terminado'; }
    elseif ($a === 'rechazar') { if ($s['estado'] !== 'pendiente') return false; $s['estado'] = 'rechazada'; }
    else return false;
    $s['historial'][] = gmdate('Y-m-d H:i') . ' ' . $a;
    return true;
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
            if (!empty($s['stripe_sub']) && empty($s['cancelada'])) continue;   // paga con suscripción: se renueva sola, no hace falta avisar
            correo($s['correo'], 'Tu destacado en AURZANE NEXUS termina el ' . fecha($s['hasta']),
                '<p>Hola, ' . h($s['nombre']) . ':</p><p>El destacado de <b>' . h($s['universidad']) . '</b> en AURZANE NEXUS termina el <b>' . fecha($s['hasta']) . '</b>.</p>'
                . '<p>Si quieres seguir, elige cómo (' . h(PRECIO_TXT) . '). Si no haces nada, tu ficha vuelve a ser normal sola, sin ningún cargo.</p>' . botones_pago($s)
                . '<p>Ver tu ficha: <a href="' . ficha($s) . '">' . ficha($s) . '</a></p>', 'hola@aurzane.com');
            correo($ADMIN, 'Patrocinio: ' . $s['universidad'] . ' termina en 5 días', '<p><b>' . h($s['universidad']) . '</b> (' . h($s['correo']) . ') termina el ' . fecha($s['hasta'])
                . '. Ya le he enviado los botones de pago; si paga, se alarga solo. Lo ves en aurzane.com/admin.html, pestaña Patrocinios.</p>');
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
if (($_SERVER['REQUEST_METHOD'] ?? '') === 'OPTIONS') { header('Access-Control-Allow-Methods: POST'); header('Access-Control-Allow-Headers: Content-Type, Authorization'); exit; }
header('Cache-Control: no-store'); header('X-Robots-Tag: noindex, nofollow');

// ---------- Stripe: avisos de pago (firma comprobada con la clave que Adrián guarda en admin.html) ----------
if (isset($_GET['stripe'])) {
    header('Content-Type: application/json; charset=utf-8');
    $cuerpo = file_get_contents('php://input'); $sec = trim((string)@file_get_contents("$DIR/stripe_whsec"));
    $firma = []; foreach (explode(',', $_SERVER['HTTP_STRIPE_SIGNATURE'] ?? '') as $par) { [$k, $v] = array_pad(explode('=', $par, 2), 2, ''); $firma[$k][] = $v; }
    $t_ = intval(($firma['t'] ?? ['0'])[0]); $ok = false;
    if ($sec && abs(time() - $t_) < 600) foreach ($firma['v1'] ?? [] as $v) if (hash_equals(hash_hmac('sha256', "$t_.$cuerpo", $sec), $v)) $ok = true;
    if (!$ok) { http_response_code(400); echo '{"error":"firma"}'; exit; }
    $ev = json_decode($cuerpo, true) ?: []; $o = $ev['data']['object'] ?? []; $tipo = $ev['type'] ?? ''; $hoy = gmdate('Y-m-d');
    $fp = fopen("$DIR/.cerrojo", 'c'); flock($fp, LOCK_EX);
    $l = cargar($F); $pend = cargar("$DIR/stripe_pendientes.json"); $hechas = cargar("$DIR/stripe_facturas.json"); $avisar = [];
    $sub_de = function ($o) { return $o['subscription'] ?? ($o['parent']['subscription_details']['subscription'] ?? ($o['lines']['data'][0]['parent']['subscription_item_details']['subscription'] ?? '')); };
    $cobrar = function (&$s, $inv) use (&$hechas, &$avisar, $hoy) {
        if (in_array($inv['id'], $hechas)) return; $hechas[] = $inv['id'];
        $pe = $inv['lines']['data'][0]['period'] ?? []; $anual = !empty($pe['end']) && ($pe['end'] - ($pe['start'] ?? $pe['end'])) > 40 * 86400;
        alargar($s, $anual, $hoy); $s['historial'][] = gmdate('Y-m-d H:i') . ' pago Stripe ' . ($anual ? 'anual' : 'mensual') . ' ' . number_format(($inv['amount_paid'] ?? 0) / 100, 2, ',', '.') . ' €';
        $avisar[] = [$s, $anual, $inv['hosted_invoice_url'] ?? ''];
    };
    if ($tipo === 'checkout.session.completed' || $tipo === 'checkout.session.async_payment_succeeded') {
        $tk = preg_replace('/[^a-f0-9]/', '', (string)($o['client_reference_id'] ?? ''));
        foreach ($l as &$s) if ($tk && hash_equals($s['token'], $tk)) {
            if (!empty($o['subscription'])) $s['stripe_sub'] = $o['subscription'];
            if (!empty($o['customer'])) $s['stripe_cliente'] = $o['customer'];
            unset($s['cancelada']);
            foreach ($pend as $k => $inv) if ($sub_de($inv) === ($s['stripe_sub'] ?? '-')) { $cobrar($s, $inv); unset($pend[$k]); }
        }
        unset($s);
    } elseif ($tipo === 'invoice.paid') {
        $sub = $sub_de($o); $hay = false;
        foreach ($l as &$s) if ($sub && ($s['stripe_sub'] ?? '') === $sub) { $cobrar($s, $o); $hay = true; }
        unset($s);
        if (!$hay && $sub) $pend[] = $o;   // el aviso del pago llegó antes que el de la compra: se aplica cuando llegue
    } elseif ($tipo === 'customer.subscription.deleted') {
        foreach ($l as &$s) if (($s['stripe_sub'] ?? '') === ($o['id'] ?? '-')) {
            $s['cancelada'] = $hoy; $s['historial'][] = gmdate('Y-m-d H:i') . ' suscripción cancelada en Stripe';
            correo($ADMIN, 'Patrocinio: ' . $s['universidad'] . ' ha cancelado', '<p><b>' . h($s['universidad']) . '</b> canceló su suscripción. Sigue destacada hasta el ' . fecha($s['hasta']) . ' y después vuelve a ser normal sola.</p>');
        }
        unset($s);
    }
    guardar($F, $l); guardar("$DIR/stripe_pendientes.json", array_slice($pend, -50)); guardar("$DIR/stripe_facturas.json", array_slice($hechas, -500)); activos($F, $DIR);
    flock($fp, LOCK_UN); fclose($fp);
    foreach ($avisar as [$s, $anual, $fac]) {
        correo($s['correo'], 'Pago recibido: ' . $s['universidad'] . ' sigue destacada', '<p>Hola, ' . h($s['nombre']) . ':</p><p>Gracias, hemos recibido tu pago ' . ($anual ? 'anual' : 'mensual')
            . '. <b>' . h($s['universidad']) . '</b> sale destacada en AURZANE NEXUS hasta el <b>' . fecha($s['hasta']) . '</b>. La suscripción se renueva sola; puedes cancelarla o cambiar la forma de pago en <a href="' . PORTAL . '">tu portal de pagos</a>.</p>'
            . ($fac ? '<p><a href="' . h($fac) . '">Ver o descargar la factura</a></p>' : ''), 'hola@aurzane.com');
        correo($ADMIN, 'Pago recibido: ' . $s['universidad'], '<p><b>' . h($s['universidad']) . '</b> ha pagado (' . ($anual ? 'anual' : 'mensual') . '). Destacada hasta el ' . fecha($s['hasta']) . '. No tienes que hacer nada.</p>');
    }
    echo '{"ok":true}'; exit;
}

// ---------- pestaña «Patrocinios» de aurzane.com/admin.html (solo administradores) ----------
$tk_admin = preg_replace('/^Bearer\s+/i', '', $_SERVER['HTTP_AUTHORIZATION'] ?? $_SERVER['REDIRECT_HTTP_AUTHORIZATION'] ?? '');
if ($tk_admin && isset($_GET['admin'])) {
    header('Content-Type: application/json; charset=utf-8');
    $ch = curl_init('https://chtfpqwrrarfdjcivlad.supabase.co/rest/v1/rpc/es_admin');
    curl_setopt_array($ch, [CURLOPT_POST => true, CURLOPT_RETURNTRANSFER => true, CURLOPT_TIMEOUT => 15, CURLOPT_POSTFIELDS => '{}',
      CURLOPT_HTTPHEADER => ['apikey: sb_publishable___1v6VjDew0l8uGfMyb9Nw_YyCLTPPw', 'Authorization: Bearer ' . $tk_admin, 'Content-Type: application/json']]);
    if (trim((string)curl_exec($ch)) !== 'true') { http_response_code(403); echo '{"error":"Solo para administradores"}'; exit; }
    $in = json_decode(file_get_contents('php://input'), true) ?: []; $hoy = gmdate('Y-m-d');
    if (($in['accion'] ?? '') === 'clave_stripe') {   // la clave de firma se guarda fuera de la web y nunca se devuelve
        $k = trim((string)($in['clave'] ?? ''));
        if (!preg_match('/^whsec_[A-Za-z0-9]{20,}$/', $k)) { http_response_code(400); echo '{"error":"La clave debe empezar por whsec_. Cópiala de Stripe: Desarrolladores, Webhooks, AURZANE patrocinios NEXUS, Secreto de firma."}'; exit; }
        file_put_contents("$DIR/stripe_whsec", $k); @chmod("$DIR/stripe_whsec", 0600); echo '{"ok":true}'; exit;
    }
    if (in_array($in['accion'] ?? '', ['aprobar', 'renovar1', 'renovar12', 'baja', 'rechazar'], true)) {
        $l = cargar($F); $hecho = false; $t = preg_replace('/[^a-f0-9]/', '', (string)($in['t'] ?? ''));
        foreach ($l as &$s) if ($t && hash_equals($s['token'], $t)) $hecho = accion($in['accion'], $s, $hoy, $PRUEBA);
        unset($s); if ($hecho) { guardar($F, $l); activos($F, $DIR); }
        if (!$hecho) { http_response_code(409); echo '{"error":"Esa acción no se puede hacer en el estado actual."}'; exit; }
    }
    $l = cargar($F);
    echo json_encode(['ok' => true, 'stripe' => is_file("$DIR/stripe_whsec"), 'precio' => PRECIO_TXT, 'portal' => PORTAL,
        'lista' => array_reverse(array_map(function ($s) { unset($s['ip']); $s['pago_mes'] = enlace_pago($s, false); $s['pago_anio'] = enlace_pago($s, true); return $s; }, $l))], JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
    exit;
}

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
    accion($a, $s, $hoy, $PRUEBA);
    unset($s); guardar($F, $l); activos($F, $DIR);
    $s = $l[$i];
    echo $pag('<h1 style="font-size:22px">Hecho</h1><p>' . h($acc[$a]) . ':</p><p><b>' . h($s['universidad']) . '</b><br>Estado: ' . h($s['estado'])
        . ($s['hasta'] ? '<br>Del ' . fecha($s['desde']) . ' al ' . fecha($s['hasta']) : '') . '</p><p>Aparece o desaparece de NEXUS en la siguiente publicación (dos al día). También lo tienes en aurzane.com/admin.html, pestaña Patrocinios.</p>');
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
    . ($d['mensaje'] ? '<p>' . nl2br(h($d['mensaje'])) . '</p>' : '') . '<p>Antes de aprobar, comprueba que el correo es de la universidad (mismo dominio que su web). También puedes hacerlo en aurzane.com/admin.html, pestaña Patrocinios.</p><p>'
    . botones_admin($YO, $tok) . '</p>', $d['correo']);
correo($d['correo'], 'Hemos recibido tu solicitud para AURZANE NEXUS', '<p>Hola, ' . h($d['nombre']) . ':</p><p>Gracias por tu interés en destacar <b>' . h($d['universidad'])
    . '</b>. Revisamos la solicitud en un plazo de 2 días laborables y te escribimos para activar tu mes gratis.</p>', 'hola@aurzane.com');
echo json_encode(['ok' => true, 'mensaje' => 'Recibido. Revisamos tu solicitud en 2 días laborables y te escribimos al correo.'], JSON_UNESCAPED_UNICODE);
