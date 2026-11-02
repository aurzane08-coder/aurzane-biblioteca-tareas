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
  $id = (string)($in['id'] ?? ''); $d = (string)($in['d'] ?? '');
  if (!preg_match('/^[a-z]{2,6}-[A-Za-z0-9._-]{1,90}$/', $id) || !in_array($d, ['aprobar', 'descartar', 'deshacer'], true)) { http_response_code(400); echo '{"error":"Petición no válida"}'; exit; }
  @mkdir($dir, 0700, true);
  $fp = fopen($fdec, 'c+'); flock($fp, LOCK_EX);
  $dec = json_decode(stream_get_contents($fp) ?: '', true); if (!is_array($dec)) $dec = [];
  if ($d === 'deshacer') unset($dec[$id]); else $dec[$id] = ['d' => $d, 'f' => gmdate('c')];
  if (count($dec) > 800) $dec = array_slice($dec, -800, null, true);
  ftruncate($fp, 0); rewind($fp); fwrite($fp, json_encode($dec, JSON_UNESCAPED_UNICODE)); fflush($fp); flock($fp, LOCK_UN); fclose($fp);
  @chmod($fdec, 0600);
  echo json_encode(['ok' => true, 'decisiones' => $dec], JSON_UNESCAPED_UNICODE); exit;
}

$inf = @file_get_contents("$dir/informe.json") ?: '{}';
$err = []; $l = @file("$dir/errores.log", FILE_IGNORE_NEW_LINES) ?: [];
foreach (array_slice($l, -300) as $x) $err[] = explode("\t", $x);
echo json_encode(['informe' => json_decode($inf, true), 'errores' => array_reverse($err),
  'propuestas' => leer_json("$dir/propuestas.json"), 'decisiones' => (object)leer_json($fdec)], JSON_UNESCAPED_UNICODE);
