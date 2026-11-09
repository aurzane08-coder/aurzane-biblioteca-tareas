<?php
// Utilidades de Mi AURZANE: historial de tests guardado fuera de la web, un archivo por cuenta.
const AZ_SB = 'https://chtfpqwrrarfdjcivlad.supabase.co';
const AZ_KEY = 'sb_publishable___1v6VjDew0l8uGfMyb9Nw_YyCLTPPw';
function az_dir() { $d = dirname(__DIR__, 2) . '/privado-mi'; if (!is_dir($d)) @mkdir($d, 0700, true); return $d; }
function az_archivo($uid) { return az_dir() . '/' . preg_replace('/[^a-f0-9-]/', '', $uid) . '.json'; }
function az_leer($uid) { $f = az_archivo($uid); return is_file($f) ? (json_decode(file_get_contents($f), true) ?: []) : []; }
function az_guardar($uid, $d) { $f = az_archivo($uid); file_put_contents($f, json_encode($d, JSON_UNESCAPED_UNICODE), LOCK_EX); @chmod($f, 0600); }
// Comprueba la sesión AURZANE ID con Supabase y devuelve [id, email] o null
function az_usuario($tk) {
    if (!$tk || !preg_match('/^[A-Za-z0-9._-]{20,}$/', $tk)) return null;
    $ch = curl_init(AZ_SB . '/auth/v1/user');
    curl_setopt_array($ch, [CURLOPT_RETURNTRANSFER => true, CURLOPT_TIMEOUT => 15, CURLOPT_HTTPHEADER => ['apikey: ' . AZ_KEY, 'Authorization: Bearer ' . $tk]]);
    $u = json_decode((string)curl_exec($ch), true);
    return (curl_getinfo($ch, CURLINFO_HTTP_CODE) === 200 && !empty($u['id'])) ? [$u['id'], $u['email'] ?? ''] : null;
}
