<?php
// Librero de AURZANE: recomienda libros de la tienda (solo los que existen en el catálogo), resuelve dudas de la tienda
// y recoge avisos de problemas para que AURZANE AI los revise. No guarda las preguntas. Límite: 8 preguntas al día por visitante.
header('Content-Type: application/json; charset=utf-8'); header('Cache-Control: no-store');
$origen = $_SERVER['HTTP_ORIGIN'] ?? '';
if (preg_match('#^https://([a-z0-9-]+\.)?aurzane\.com$#', $origen)) { header('Access-Control-Allow-Origin: ' . $origen); header('Vary: Origin'); }
header('Access-Control-Allow-Methods: POST, OPTIONS'); header('Access-Control-Allow-Headers: Content-Type');
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') exit;
if ($_SERVER['REQUEST_METHOD'] !== 'POST') { http_response_code(405); echo '{"error":"Usa POST"}'; exit; }
$dir = dirname(__DIR__, 2) . '/privado-ai';
$in = json_decode(file_get_contents('php://input'), true) ?: [];
$hoy = gmdate('Y-m-d');
$ip = substr(hash('sha256', ($_SERVER['REMOTE_ADDR'] ?? '') . $hoy . 'aurzane'), 0, 16);

// 1) avisos de problemas en la tienda o la biblioteca: se guardan para la revisión de la IA (sin datos personales)
if (($in['tipo'] ?? '') === 'incidencia') {
    $txt = mb_substr(trim(strip_tags((string)($in['texto'] ?? ''))), 0, 600);
    $pag = mb_substr(preg_replace('#[^a-zA-Z0-9:/._?=&%-]#', '', (string)($in['pagina'] ?? '')), 0, 200);
    if (mb_strlen($txt) < 5) { http_response_code(400); echo '{"error":"Cuéntanos un poco más qué ha fallado."}'; exit; }
    $f = "$dir/incidencias.json"; $fp = fopen($f, 'c+'); flock($fp, LOCK_EX);
    $l = json_decode(stream_get_contents($fp) ?: '', true) ?: [];
    if (count(array_filter($l, fn($x) => ($x['ip'] ?? '') === $ip && ($x['fecha'] ?? '') === $hoy)) >= 3) { flock($fp, LOCK_UN); fclose($fp); echo '{"respuesta":"Ya hemos recibido tus avisos de hoy. ¡Gracias!"}'; exit; }
    $l[] = ['fecha' => $hoy, 'hora' => gmdate('H:i'), 'pagina' => $pag, 'texto' => $txt, 'ip' => $ip, 'estado' => 'nuevo'];
    $l = array_slice($l, -300);
    ftruncate($fp, 0); rewind($fp); fwrite($fp, json_encode($l, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT)); fflush($fp); flock($fp, LOCK_UN); fclose($fp); @chmod($f, 0600);
    echo '{"respuesta":"Gracias por avisar. La IA de AURZANE lo revisará en su próxima ronda y, si es un fallo, lo arreglará o se lo pasará a Adrián."}'; exit;
}

// 2) preguntas al librero
$clave = trim((string)@file_get_contents("$dir/gemini.key"));
if (!$clave) { http_response_code(503); echo '{"error":"El librero no está disponible ahora mismo."}'; exit; }
$q = mb_substr(trim(strip_tags((string)($in['pregunta'] ?? ''))), 0, 400);
if (mb_strlen($q) < 3) { http_response_code(400); echo '{"error":"Escribe qué buscas."}'; exit; }
$fc = "$dir/librero-$hoy.json"; $fp = fopen($fc, 'c+'); flock($fp, LOCK_EX);
$c = json_decode(stream_get_contents($fp) ?: '', true) ?: ['total' => 0, 'ip' => []];
if (($c['ip'][$ip] ?? 0) >= 8 || $c['total'] >= 300) { flock($fp, LOCK_UN); fclose($fp); http_response_code(429); echo '{"error":"El librero ha llegado a su límite de hoy. Vuelve mañana o usa el buscador de la tienda."}'; exit; }
$c['total']++; $c['ip'][$ip] = ($c['ip'][$ip] ?? 0) + 1;
ftruncate($fp, 0); rewind($fp); fwrite($fp, json_encode($c)); fflush($fp); flock($fp, LOCK_UN); fclose($fp); @chmod($fc, 0600);

// candidatos: los libros del catálogo que más se parecen a la pregunta (la IA solo puede elegir entre estos)
$libros = json_decode((string)@file_get_contents(dirname(__DIR__) . '/libros/libros.json'), true) ?: [];
$norm = function ($t) { $t = mb_strtolower((string)$t); $t = strtr($t, ['á' => 'a', 'é' => 'e', 'í' => 'i', 'ó' => 'o', 'ú' => 'u', 'ü' => 'u', 'ñ' => 'n']); return preg_split('/[^a-z0-9]+/', $t, -1, PREG_SPLIT_NO_EMPTY); };
$pal = array_filter($norm($q), fn($w) => strlen($w) > 3);
foreach ($libros as $k => $l) {
    $txt = implode(' ', $norm($l['t'] . ' ' . $l['a'] . ' ' . $l['s'] . ' ' . implode(' ', $l['temas'] ?? []) . ' ' . ($l['r'] ?? '') . ' ' . ($l['tend'] ?? '')));
    $p = 0; foreach ($pal as $w) if (strpos($txt, substr($w, 0, 6)) !== false) $p++;
    $libros[$k]['_p'] = $p + (!empty($l['tend']) ? 0.3 : 0) + (!empty($l['img']) ? 0.1 : 0);
}
usort($libros, fn($a, $b) => $b['_p'] <=> $a['_p']);
$cand = array_slice($libros, 0, 45); $porId = [];
$lista = '';
foreach ($cand as $l) { $porId[$l['id']] = $l; $lista .= "- {$l['id']} | {$l['t']} | {$l['a']} | {$l['s']}" . (!empty($l['r']) ? ' | ' . mb_substr($l['r'], 0, 120) : '') . "\n"; }

$sistema = "Eres el librero de AURZANE, una web española de psicología y bienestar con una tienda de libros. Respondes en español de España, cercano y claro, sin rayas largas, en un máximo de 90 palabras. "
  . "Si la persona busca libros, recomienda de 1 a 3 SOLO de la lista que se te da (usa sus id exactos); nunca inventes libros ni datos. Si ninguno encaja, dilo y sugiere usar el buscador o la biblioteca gratis. "
  . "Datos de la tienda que puedes explicar: hay libros gratis (licencia abierta o dominio público, se leen completos en aurzane.com/biblioteca sin registro) y libros de pago, que se compran en Amazon a través del botón «Ver precio en Amazon»; "
  . "AURZANE no vende ni envía libros, el pedido, el pago, el envío y las devoluciones los gestiona Amazon; los enlaces son de afiliado y no encarecen el libro; hay una guía de regalos en aurzane.com/libros/regalar y un boletín semanal gratis. "
  . "Si algo no funciona en la web, pide que lo cuenten con el botón «¿Algo no funciona?» para que la IA lo revise. "
  . "Si la persona habla de hacerse daño o estar en peligro, responde con empatía y pídele que llame al 024 (España, gratis, 24 horas) o al 112. "
  . "Responde solo JSON: {\"respuesta\":\"...\",\"libros\":[\"id\",...]}";
$cuerpo = json_encode(['systemInstruction' => ['parts' => [['text' => $sistema]]],
  'contents' => [['role' => 'user', 'parts' => [['text' => "Libros disponibles:\n$lista\nPregunta: $q"]]]],
  'generationConfig' => ['temperature' => 0.4, 'maxOutputTokens' => 1024, 'responseMimeType' => 'application/json']], JSON_UNESCAPED_UNICODE);
$texto = ''; $ultimo = 0;
foreach (['gemini-flash-lite-latest', 'gemini-flash-latest'] as $m) {
  $ch = curl_init("https://generativelanguage.googleapis.com/v1beta/models/$m:generateContent");
  curl_setopt_array($ch, [CURLOPT_POST => true, CURLOPT_RETURNTRANSFER => true, CURLOPT_TIMEOUT => 40, CURLOPT_POSTFIELDS => $cuerpo,
    CURLOPT_HTTPHEADER => ['Content-Type: application/json', 'x-goog-api-key: ' . $clave]]);
  $r = json_decode((string)curl_exec($ch), true); $ultimo = curl_getinfo($ch, CURLINFO_HTTP_CODE);
  foreach (($r['candidates'][0]['content']['parts'] ?? []) as $pt) $texto .= $pt['text'] ?? '';
  if (trim($texto)) break;
}
$j = json_decode(preg_replace('/^```(json)?|```$/m', '', trim($texto)), true);
if (!is_array($j) || empty($j['respuesta'])) { http_response_code(503); echo json_encode(['error' => 'El librero está muy solicitado ahora mismo. Prueba en un rato o usa el buscador.', 'codigo' => $ultimo]); exit; }
$out = [];
foreach (array_slice((array)($j['libros'] ?? []), 0, 3) as $id) if (isset($porId[$id])) { $l = $porId[$id]; $out[] = ['t' => $l['t'], 'a' => $l['a'], 'img' => $l['img'] ?? '', 'f' => $l['f'] ?? '', 'u' => $l['u'] ?? '']; }
echo json_encode(['respuesta' => trim(str_replace(['—', '–'], [',', ','], (string)$j['respuesta'])), 'libros' => $out, 'quedan' => 8 - $c['ip'][$ip]], JSON_UNESCAPED_UNICODE);
