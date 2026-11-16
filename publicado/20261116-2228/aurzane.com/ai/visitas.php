<?php
// Medición de visitas sin cookies ni datos personales (16/11/2026, auditoría: «medir lo que pasa»).
// Recibe {h: dominio, p: ruta, e: evento opcional, o: origen} y solo SUMA contadores por día en
// privado-ai/visitas/AAAA-MM-DD.json (fuera de la web). No guarda IP, ni identificadores, ni la dirección completa de origen.
header('Content-Type: text/plain; charset=utf-8');
if ($_SERVER['REQUEST_METHOD'] !== 'POST') { http_response_code(405); exit; }
$ua = $_SERVER['HTTP_USER_AGENT'] ?? '';
if ($ua === '' || preg_match('/bot|crawl|spider|slurp|preview|headless|lighthouse|pagespeed|facebookexternalhit/i', $ua)) { http_response_code(204); exit; }
$j = json_decode(file_get_contents('php://input', false, null, 0, 2000), true);
if (!is_array($j)) { http_response_code(400); exit; }
$h = strtolower((string)($j['h'] ?? ''));
if (!preg_match('/^((mind|nexus|live|learn|build|ovp)\.)?aurzane\.com$/', $h)) { http_response_code(204); exit; }
$p = substr(preg_replace('/[^a-z0-9\/._-]/i', '', (string)($j['p'] ?? '/')), 0, 120) ?: '/';
$p = preg_replace('/\/index\.html$/', '/', $p);
$e = substr(preg_replace('/[^a-z0-9:._-]/i', '', (string)($j['e'] ?? '')), 0, 60);
$o = substr(preg_replace('/[^a-z0-9._-]/i', '', (string)($j['o'] ?? '')), 0, 40);
$dir = dirname(__DIR__, 2) . '/privado-ai/visitas'; if (!is_dir($dir)) @mkdir($dir, 0700, true);
$f = $dir . '/' . date('Y-m-d') . '.json';
$fp = @fopen($f, 'c+'); if (!$fp) { http_response_code(204); exit; }
flock($fp, LOCK_EX);
$d = json_decode(stream_get_contents($fp), true) ?: ['vistas' => [], 'eventos' => [], 'origen' => []];
$k = $h . $p;
if ($e === '') { $d['vistas'][$k] = ($d['vistas'][$k] ?? 0) + 1; if ($o !== '') $d['origen'][$o] = ($d['origen'][$o] ?? 0) + 1; }
else { $ke = $e . '|' . $k; $d['eventos'][$ke] = ($d['eventos'][$ke] ?? 0) + 1; }
if (count($d['vistas']) < 20000) { ftruncate($fp, 0); rewind($fp); fwrite($fp, json_encode($d, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE)); }
flock($fp, LOCK_UN); fclose($fp);
http_response_code(204);
