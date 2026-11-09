<?php
// Devuelve el panel de resultados (privado-ai/panel.json) solo a administradores de AURZANE.
// Comprueba la sesión AURZANE ID con Supabase: la propia base de datos decide con es_admin().
header('Content-Type: application/json; charset=utf-8'); header('Cache-Control: no-store'); header('X-Robots-Tag: noindex');
$tk = '';
if (preg_match('/^Bearer\s+([A-Za-z0-9._-]+)$/', $_SERVER['HTTP_AUTHORIZATION'] ?? ($_SERVER['REDIRECT_HTTP_AUTHORIZATION'] ?? ''), $m)) $tk = $m[1];
if (!$tk) { $in = json_decode(file_get_contents('php://input'), true) ?: []; $tk = preg_replace('/[^A-Za-z0-9._-]/', '', (string)($in['token'] ?? '')); }
if (!$tk) { http_response_code(401); echo '{"error":"Inicia sesión."}'; exit; }
$ch = curl_init('https://chtfpqwrrarfdjcivlad.supabase.co/rest/v1/rpc/es_admin');
curl_setopt_array($ch, [CURLOPT_POST => true, CURLOPT_RETURNTRANSFER => true, CURLOPT_TIMEOUT => 20, CURLOPT_POSTFIELDS => '{}',
  CURLOPT_HTTPHEADER => ['Content-Type: application/json', 'apikey: sb_publishable___1v6VjDew0l8uGfMyb9Nw_YyCLTPPw', 'Authorization: Bearer ' . $tk]]);
$r = trim((string)curl_exec($ch)); $code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
if ($code !== 200 || $r !== 'true') { http_response_code(403); echo '{"error":"Esta cuenta no tiene acceso al panel."}'; exit; }
$f = dirname(__DIR__, 2) . '/privado-ai/panel.json';
if (!is_file($f)) { http_response_code(404); echo '{"error":"El panel todavía no se ha generado. Se crea cada mañana."}'; exit; }
readfile($f);
