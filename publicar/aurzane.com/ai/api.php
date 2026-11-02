<?php
// AURZANE AI · datos del panel y decisiones de la cola. Solo para el equipo: comprueba la sesión de AURZANE ID con la función es_admin() de Supabase.
header('Content-Type: application/json; charset=utf-8'); header('Cache-Control: no-store');
$tk = preg_replace('/^Bearer\s+/i', '', $_SERVER['HTTP_AUTHORIZATION'] ?? $_SERVER['REDIRECT_HTTP_AUTHORIZATION'] ?? '');
if (!$tk) { http_response_code(401); echo '{"error":"Inicia sesión"}'; exit; }
$ch = curl_init('https://chtfpqwrrarfdjcivlad.supabase.co/rest/v1/rpc/es_admin');
curl_setopt_array($ch, [CURLOPT_POST => true, CURLOPT_RETURNTRANSFER => true, CURLOPT_TIMEOUT => 15, CURLOPT_POSTFIELDS => '{}',
  CURLOPT_HTTPHEADER => ['apikey: sb_publishable___1v6VjDew0l8uGfMyb9Nw_YyCLTPPw', 'Authorization: Bearer ' . $tk, 'Content-Type: application/json']]);
$r = trim((string)curl_exec($ch));
if ($r !== 'true') { http_response_code(403); echo '{"error":"Solo para administradores"}'; exit; }
$dir = dirname(__DIR__, 2) . '/privado-ai';
$fdec = "$dir/decisiones.json";
function leer_json($f) { $j = json_decode(@file_get_contents($f) ?: '', true); return is_array($j) ? $j : []; }

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
  $in = json_decode(file_get_contents('php://input'), true) ?: [];
  @mkdir($dir, 0700, true);
  if (($in['accion'] ?? '') === 'revisar') { @touch("$dir/revisar_ya"); echo '{"ok":true,"pedida":true}'; exit; }
  if (($in['accion'] ?? '') === 'reparar') {
    $sol = ['id' => substr(md5(uniqid('', true)), 0, 10), 'fecha' => gmdate('c'),
            'clave' => preg_replace('/[^a-f0-9]/', '', substr((string)($in['clave'] ?? ''), 0, 12)),
            'texto' => mb_substr(trim(strip_tags((string)($in['texto'] ?? ''))), 0, 1000),
            'url' => filter_var(trim((string)($in['url'] ?? '')), FILTER_VALIDATE_URL) ? mb_substr(trim((string)$in['url']), 0, 300) : ''];
    if (!$sol['clave'] && !$sol['texto'] && !$sol['url']) { http_response_code(400); echo '{"error":"Describe el problema o indica una URL"}'; exit; }
    $fs = "$dir/solicitudes.json"; $fp = fopen($fs, 'c+'); flock($fp, LOCK_EX);
    $l = json_decode(stream_get_contents($fp) ?: '', true); if (!is_array($l)) $l = [];
    $l[] = $sol; $l = array_slice($l, -300);
    ftruncate($fp, 0); rewind($fp); fwrite($fp, json_encode($l, JSON_UNESCAPED_UNICODE)); fflush($fp); flock($fp, LOCK_UN); fclose($fp); @chmod($fs, 0600);
    @touch("$dir/revisar_ya");
    echo json_encode(['ok' => true, 'solicitud' => $sol], JSON_UNESCAPED_UNICODE); exit;
  }
  $id = (string)($in['id'] ?? ''); $d = (string)($in['d'] ?? '');
  if (!preg_match('/^[a-z]{2,6}-[A-Za-z0-9._-]{1,90}$/', $id) || !in_array($d, ['aprobar', 'descartar', 'deshacer'], true)) { http_response_code(400); echo '{"error":"Petición no válida"}'; exit; }
  $fp = fopen($fdec, 'c+'); flock($fp, LOCK_EX);
  $dec = json_decode(stream_get_contents($fp) ?: '', true); if (!is_array($dec)) $dec = [];
  if ($d === 'deshacer') unset($dec[$id]); else $dec[$id] = ['d' => $d, 'f' => gmdate('c')];
  if (count($dec) > 800) $dec = array_slice($dec, -800, null, true);
  ftruncate($fp, 0); rewind($fp); fwrite($fp, json_encode($dec, JSON_UNESCAPED_UNICODE)); fflush($fp); flock($fp, LOCK_UN); fclose($fp);
  @chmod($fdec, 0600);
  if ($d === 'aprobar') @touch("$dir/revisar_ya");
  echo json_encode(['ok' => true, 'pedida' => file_exists("$dir/revisar_ya"), 'decisiones' => $dec], JSON_UNESCAPED_UNICODE); exit;
}

$inf = @file_get_contents("$dir/informe.json") ?: '{}';
$err = []; $l = @file("$dir/errores.log", FILE_IGNORE_NEW_LINES) ?: [];
foreach (array_slice($l, -300) as $x) $err[] = explode("\t", $x);
echo json_encode(['informe' => json_decode($inf, true), 'errores' => array_reverse($err),
  'propuestas' => leer_json("$dir/propuestas.json"), 'decisiones' => (object)leer_json($fdec), 'pedida' => file_exists("$dir/revisar_ya"), 'solicitudes' => array_slice(leer_json("$dir/solicitudes.json"), -30)], JSON_UNESCAPED_UNICODE);
