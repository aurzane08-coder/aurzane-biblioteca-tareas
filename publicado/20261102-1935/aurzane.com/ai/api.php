<?php
// AURZANE AI · datos del panel. Solo para el equipo: comprueba la sesión de AURZANE ID con la función es_admin() de Supabase.
header('Content-Type: application/json; charset=utf-8'); header('Cache-Control: no-store');
$tk = preg_replace('/^Bearer\s+/i', '', $_SERVER['HTTP_AUTHORIZATION'] ?? $_SERVER['REDIRECT_HTTP_AUTHORIZATION'] ?? '');
if (!$tk) { http_response_code(401); echo '{"error":"Inicia sesión"}'; exit; }
$ch = curl_init('https://chtfpqwrrarfdjcivlad.supabase.co/rest/v1/rpc/es_admin');
curl_setopt_array($ch, [CURLOPT_POST => true, CURLOPT_RETURNTRANSFER => true, CURLOPT_TIMEOUT => 15, CURLOPT_POSTFIELDS => '{}',
  CURLOPT_HTTPHEADER => ['apikey: sb_publishable___1v6VjDew0l8uGfMyb9Nw_YyCLTPPw', 'Authorization: Bearer ' . $tk, 'Content-Type: application/json']]);
$r = trim((string)curl_exec($ch));
if ($r !== 'true') { http_response_code(403); echo '{"error":"Solo para administradores"}'; exit; }
$dir = dirname(__DIR__, 2) . '/privado-ai';
$inf = @file_get_contents("$dir/informe.json") ?: '{}';
$err = []; $l = @file("$dir/errores.log", FILE_IGNORE_NEW_LINES) ?: [];
foreach (array_slice($l, -300) as $x) $err[] = explode("\t", $x);
echo json_encode(['informe' => json_decode($inf, true), 'errores' => array_reverse($err)], JSON_UNESCAPED_UNICODE);
