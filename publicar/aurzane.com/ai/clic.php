<?php
// Cuenta los clics en enlaces de compra (Amazon, Awin y otros afiliados) para el panel de resultados.
// Solo guarda fecha, tienda y página de origen: nada que identifique a la persona.
header('Cache-Control: no-store');
if ($_SERVER['REQUEST_METHOD'] !== 'POST') { http_response_code(204); exit; }
$in = json_decode(file_get_contents('php://input'), true) ?: [];
$t = preg_replace('/[^a-z0-9.-]/', '', strtolower((string)($in['t'] ?? '')));
$p = preg_replace('#[^a-zA-Z0-9:/._-]#', '', (string)($in['p'] ?? ''));
if (!$t || strlen($t) > 60) { http_response_code(204); exit; }
$dir = dirname(__DIR__, 2) . '/privado-ai';
if (!is_dir($dir)) @mkdir($dir, 0700, true);
@file_put_contents("$dir/clics-compra.log", gmdate('Y-m-d') . "\t" . $t . "\t" . substr($p, 0, 160) . "\n", FILE_APPEND | LOCK_EX);
http_response_code(204);
