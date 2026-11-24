<?php
// Boletín desde Mi AURZANE (24/11/2026): ver si la cuenta está suscrita, darse de alta o de baja con un clic.
// El navegador manda la sesión de AURZANE ID (el token de Supabase) y este archivo pregunta a Supabase de quién es.
// Así solo se puede suscribir o dar de baja el correo de la propia cuenta, y solo si ese correo ya está verificado
// (por eso no hace falta la doble confirmación del formulario público). Guarda en el mismo privado-boletin/suscritos.json
// con origen «mi-aurzane», para que el panel cuente cuántas altas llegan desde las cuentas.
declare(strict_types=1);
$origen = (string)($_SERVER['HTTP_ORIGIN'] ?? '');
if (preg_match('#^https://([a-z]+\.)?aurzane\.com$#', $origen)) { header("Access-Control-Allow-Origin: $origen"); header('Vary: Origin'); }
header('Access-Control-Allow-Methods: POST, OPTIONS'); header('Access-Control-Allow-Headers: Content-Type');
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') { http_response_code(204); exit; }
header('Content-Type: application/json; charset=utf-8'); header('Cache-Control: no-store');
function fin(array $r) { echo json_encode($r, JSON_UNESCAPED_UNICODE); exit; }
if ($_SERVER['REQUEST_METHOD'] !== 'POST') fin(['ok' => false, 'msg' => 'Método no permitido.']);

$dir = dirname(__DIR__, 2) . '/privado-boletin';
if (!is_dir($dir)) { mkdir($dir, 0700, true); }
$fs = "$dir/suscritos.json";
function leer($f) { return is_file($f) ? (json_decode((string)file_get_contents($f), true) ?: []) : []; }
function guardar($f, $d) { file_put_contents($f, json_encode($d, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT), LOCK_EX); chmod($f, 0600); }

$token = (string)($_POST['token'] ?? '');
$accion = (string)($_POST['accion'] ?? 'estado');
if (!preg_match('/^[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+$/', $token) || !in_array($accion, ['estado', 'alta', 'baja'], true))
    fin(['ok' => false, 'msg' => 'Vuelve a iniciar sesión e inténtalo de nuevo.']);

// ¿de quién es esta sesión? (clave pública de AURZANE ID, la misma que usa la web)
$ch = curl_init('https://chtfpqwrrarfdjcivlad.supabase.co/auth/v1/user');
curl_setopt_array($ch, [CURLOPT_RETURNTRANSFER => true, CURLOPT_TIMEOUT => 10,
    CURLOPT_HTTPHEADER => ['apikey: sb_publishable___1v6VjDew0l8uGfMyb9Nw_YyCLTPPw', "Authorization: Bearer $token"]]);
$r = curl_exec($ch); $cod = curl_getinfo($ch, CURLINFO_HTTP_CODE); curl_close($ch);
$u = $cod === 200 ? json_decode((string)$r, true) : null;
$email = strtolower(trim((string)($u['email'] ?? '')));
if (!$email) fin(['ok' => false, 'msg' => 'Tu sesión ha caducado. Vuelve a iniciar sesión.']);

$s = leer($fs);
if ($accion === 'alta') {
    if (empty($u['email_confirmed_at'])) fin(['ok' => false, 'suscrito' => false, 'msg' => 'Primero confirma tu correo con el enlace que te enviamos al crear la cuenta.']);
    if (!isset($s[$email])) { $s[$email] = ['alta' => date('c'), 'baja' => bin2hex(random_bytes(16)), 'origen' => 'mi-aurzane']; guardar($fs, $s); }
    fin(['ok' => true, 'suscrito' => true, 'msg' => 'Listo. Cada semana te llegará el boletín a ' . $email . '.']);
}
if ($accion === 'baja') {
    if (isset($s[$email])) { unset($s[$email]); guardar($fs, $s); }
    fin(['ok' => true, 'suscrito' => false, 'msg' => 'Hecho. Ya no recibirás el boletín.']);
}
fin(['ok' => true, 'suscrito' => isset($s[$email]), 'verificado' => !empty($u['email_confirmed_at'])]);
