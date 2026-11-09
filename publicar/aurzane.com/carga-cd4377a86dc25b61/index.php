<?php
// Carga temporal del curso para el editor SQL de Supabase. Caduca sola.
if (time() > 1794269881 || ($_GET['t'] ?? '') !== '37f95cb4a04b0d48be4f1368') { http_response_code(404); exit; }
header('Access-Control-Allow-Origin: https://supabase.com');
header('Content-Type: text/plain; charset=utf-8');
header('Cache-Control: no-store');
header('X-Robots-Tag: noindex');
readfile(__DIR__ . '/carga.sql.txt');
