<?php
// Mi AURZANE: guarda los resultados de los tests de cada cuenta y el recordatorio mensual.
// Acciones (POST JSON con token de sesión): guardar, listar, borrar, recordatorio.
require __DIR__ . '/comun.php';
header('Content-Type: application/json; charset=utf-8'); header('Cache-Control: no-store');
$o = $_SERVER['HTTP_ORIGIN'] ?? '';
if (preg_match('#^https://([a-z0-9-]+\.)?aurzane\.com$#', $o)) { header('Access-Control-Allow-Origin: ' . $o); header('Vary: Origin'); }
header('Access-Control-Allow-Methods: POST, OPTIONS'); header('Access-Control-Allow-Headers: Content-Type');
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') exit;
if ($_SERVER['REQUEST_METHOD'] !== 'POST') { http_response_code(405); echo '{"error":"Usa POST"}'; exit; }
$in = json_decode(file_get_contents('php://input'), true) ?: [];
$u = az_usuario((string)($in['token'] ?? ''));
if (!$u) { http_response_code(401); echo '{"error":"Inicia sesión para guardar tus resultados."}'; exit; }
[$uid, $email] = $u;
$d = az_leer($uid) + ['tests' => [], 'recordatorio' => false];
$d['email'] = $email;
$acc = $in['accion'] ?? 'listar';
$t = fn($s, $n) => mb_substr(trim(strip_tags((string)$s)), 0, $n);

if ($acc === 'guardar') {
    $lista = isset($in['resultados']) && is_array($in['resultados']) ? array_slice($in['resultados'], 0, 20) : [$in];
    $nuevos = 0;
    foreach ($lista as $r) {
        $clave = preg_replace('/[^a-z0-9-]/', '', strtolower((string)($r['clave'] ?? '')));
        if (!$clave) continue;
        $fecha = preg_match('/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}/', (string)($r['fecha'] ?? '')) ? substr($r['fecha'], 0, 16) : gmdate('Y-m-d\TH:i');
        foreach ($d['tests'] as $x) if ($x['clave'] === $clave && $x['fecha'] === $fecha) continue 2;   // ya guardado
        $d['tests'][] = ['clave' => $clave, 'titulo' => $t($r['titulo'] ?? $clave, 120), 'valor' => is_numeric($r['valor'] ?? null) ? +$r['valor'] : null,
                         'max' => is_numeric($r['max'] ?? null) ? +$r['max'] : null, 'nivel' => $t($r['nivel'] ?? '', 80),
                         'url' => preg_match('#^https://([a-z0-9-]+\.)?aurzane\.com/#', (string)($r['url'] ?? '')) ? substr($r['url'], 0, 200) : '', 'fecha' => $fecha];
        $nuevos++;
    }
    $d['tests'] = array_slice($d['tests'], -500);
    az_guardar($uid, $d);
    echo json_encode(['ok' => true, 'nuevos' => $nuevos]); exit;
}
if ($acc === 'borrar') {
    $clave = preg_replace('/[^a-z0-9-]/', '', (string)($in['clave'] ?? '')); $fecha = (string)($in['fecha'] ?? '');
    $d['tests'] = array_values(array_filter($d['tests'], fn($x) => !($x['clave'] === $clave && ($fecha === '' || $x['fecha'] === $fecha))));
    az_guardar($uid, $d); echo '{"ok":true}'; exit;
}
if ($acc === 'recordatorio') {
    $d['recordatorio'] = !empty($in['activo']); if ($d['recordatorio']) $d['recordatorio_desde'] = gmdate('Y-m-d');
    az_guardar($uid, $d); echo json_encode(['ok' => true, 'recordatorio' => $d['recordatorio']]); exit;
}
echo json_encode(['tests' => $d['tests'], 'recordatorio' => !empty($d['recordatorio'])], JSON_UNESCAPED_UNICODE);
