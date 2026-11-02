<?php
// AURZANE AI · recoge los errores de JavaScript que ven los visitantes en cualquier página del ecosistema.
// Sin datos personales: solo página, mensaje técnico, archivo y línea. Se guarda fuera de la web (privado-ai/).
$o = $_SERVER['HTTP_ORIGIN'] ?? '';
if (preg_match('#^https://([a-z0-9-]+\.)?aurzane\.com$#', $o)) { header('Access-Control-Allow-Origin: ' . $o); header('Vary: Origin'); }
header('Access-Control-Allow-Methods: POST'); header('Access-Control-Allow-Headers: Content-Type');
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') { http_response_code(204); exit; }
if ($_SERVER['REQUEST_METHOD'] !== 'POST') { http_response_code(405); exit; }
$dir = dirname(__DIR__, 2) . '/privado-ai'; @mkdir($dir, 0700, true); @mkdir("$dir/ritmo", 0700, true);
// límite: 20 avisos por minuto y visitante (por huella anónima de la IP, que no se guarda)
$h = substr(hash('sha256', ($_SERVER['REMOTE_ADDR'] ?? '') . date('YmdHi')), 0, 16);
$f = "$dir/ritmo/$h"; $n = (int)@file_get_contents($f);
if ($n >= 20) { http_response_code(429); exit; }
file_put_contents($f, $n + 1);
if (mt_rand(1, 50) === 1) foreach (glob("$dir/ritmo/*") as $x) if (filemtime($x) < time() - 120) @unlink($x);
$d = json_decode(substr(file_get_contents('php://input'), 0, 4000), true);
if (!is_array($d)) { http_response_code(400); exit; }
$limpia = function ($v, $n) { return mb_substr(preg_replace('/[\t\r\n]+/', ' ', strip_tags((string)$v)), 0, $n); };
$host = $limpia($d['h'] ?? '', 60); if (!preg_match('/(^|\.)aurzane\.com$/', $host)) { http_response_code(204); exit; }
$ua = strtolower($_SERVER['HTTP_USER_AGENT'] ?? ''); $nav = preg_match('/bot|crawl|spider|headless/', $ua) ? 'bot' : (preg_match('/mobile|android|iphone/', $ua) ? 'movil' : 'escritorio');
$linea = implode("\t", [gmdate('Y-m-d H:i:s'), $host, $limpia($d['p'] ?? '', 200), $limpia($d['t'] ?? 'error', 20), $limpia($d['m'] ?? '', 300), $limpia($d['s'] ?? '', 200), (int)($d['l'] ?? 0), $nav]) . "\n";
$log = "$dir/errores.log";
if (@filesize($log) > 3000000) @rename($log, "$dir/errores-" . date('YmdHis') . '.log');
file_put_contents($log, $linea, FILE_APPEND | LOCK_EX);
http_response_code(204);
