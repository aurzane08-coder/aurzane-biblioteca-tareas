<?php
// Informes de la política de seguridad (CSP) en modo solo informe (16/11/2026).
// Guarda una línea por aviso en privado-ai/csp.log (fuera de la web), sin datos personales, hasta 2 MB.
header('Content-Type: text/plain; charset=utf-8');
if ($_SERVER['REQUEST_METHOD'] !== 'POST') { http_response_code(405); exit; }
$raw = file_get_contents('php://input', false, null, 0, 20000);
$j = json_decode($raw, true);
if (!is_array($j)) { http_response_code(400); exit; }
$r = $j['csp-report'] ?? ($j[0]['body'] ?? $j);
$limpia = function ($u) { $u = (string)$u; $p = parse_url($u); return isset($p['host']) ? ($p['scheme'] ?? 'https') . '://' . $p['host'] . ($p['path'] ?? '') : substr($u, 0, 60); };
$linea = date('c') . "\t" . substr((string)($r['effective-directive'] ?? $r['violated-directive'] ?? $r['effectiveDirective'] ?? ''), 0, 40) . "\t"
  . $limpia($r['blocked-uri'] ?? $r['blockedURL'] ?? '') . "\t" . $limpia($r['document-uri'] ?? $r['documentURL'] ?? '') . "\n";
$f = dirname(__DIR__, 2) . '/privado-ai/csp.log';
if (!file_exists($f) || filesize($f) < 2000000) @file_put_contents($f, $linea, FILE_APPEND | LOCK_EX);
http_response_code(204);
