<?php
// Asistente de resultados de AURZANE: responde dudas sobre el resultado de un test con Gemini (plan gratuito).
// No guarda las preguntas ni los resultados. Límite: 6 preguntas al día por visitante y 250 al día en total.
header('Content-Type: application/json; charset=utf-8'); header('Cache-Control: no-store');
$origen = $_SERVER['HTTP_ORIGIN'] ?? '';
if (preg_match('#^https://([a-z0-9-]+\.)?aurzane\.com$#', $origen)) { header('Access-Control-Allow-Origin: ' . $origen); header('Vary: Origin'); }
header('Access-Control-Allow-Methods: POST, OPTIONS'); header('Access-Control-Allow-Headers: Content-Type');
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') exit;
if ($_SERVER['REQUEST_METHOD'] !== 'POST') { http_response_code(405); echo '{"error":"Usa POST"}'; exit; }
$dir = dirname(__DIR__, 2) . '/privado-ai';
$clave = trim((string)@file_get_contents("$dir/gemini.key"));
if (!$clave) { http_response_code(503); echo '{"error":"El asistente no está disponible ahora mismo."}'; exit; }
$in = json_decode(file_get_contents('php://input'), true) ?: [];
$pregunta = mb_substr(trim(strip_tags((string)($in['pregunta'] ?? ''))), 0, 400);
$test = mb_substr(trim(strip_tags((string)($in['test'] ?? ''))), 0, 120);
$resultado = mb_substr(trim(strip_tags((string)($in['resultado'] ?? ''))), 0, 1500);
if (mb_strlen($pregunta) < 3 || !$test) { http_response_code(400); echo '{"error":"Escribe tu pregunta."}'; exit; }
// límites (gratis): por visitante (IP anonimizada) y total del día
$hoy = gmdate('Y-m-d'); $fc = "$dir/asistente-$hoy.json";
$fp = fopen($fc, 'c+'); flock($fp, LOCK_EX);
$c = json_decode(stream_get_contents($fp) ?: '', true) ?: ['total' => 0, 'ip' => []];
$ip = substr(hash('sha256', ($_SERVER['REMOTE_ADDR'] ?? '') . $hoy . 'aurzane'), 0, 16);
if (($c['ip'][$ip] ?? 0) >= 6) { flock($fp, LOCK_UN); fclose($fp); http_response_code(429); echo '{"error":"Has llegado al límite de preguntas de hoy. Vuelve mañana."}'; exit; }
if ($c['total'] >= 250) { flock($fp, LOCK_UN); fclose($fp); http_response_code(429); echo '{"error":"El asistente ha llegado a su límite de hoy. Vuelve mañana."}'; exit; }
$c['total']++; $c['ip'][$ip] = ($c['ip'][$ip] ?? 0) + 1;
ftruncate($fp, 0); rewind($fp); fwrite($fp, json_encode($c)); fflush($fp); flock($fp, LOCK_UN); fclose($fp); @chmod($fc, 0600);
foreach (glob("$dir/asistente-*.json") ?: [] as $f) if ($f !== $fc && filemtime($f) < time() - 3 * 86400) @rename($f, "$dir/eliminar-" . basename($f));

$sistema = "Eres el asistente de AURZANE, una web de divulgación de psicología creada por un psicólogo clínico. Respondes en español de España, con calidez y claridad, "
  . "sin rayas largas, en un máximo de 140 palabras. Explicas el resultado de un test orientativo que la persona acaba de hacer y das ideas prácticas y realistas. "
  . "Nunca diagnosticas, nunca recomiendas medicación ni sustituyes a un profesional; si procede, sugieres hablar con un psicólogo sanitario o con el médico de cabecera. "
  . "Si la persona menciona hacerse daño, suicidio o estar en peligro, responde con empatía y pídele que llame ya al 024 (España, gratis, 24 horas) o al 112, o a la línea de crisis de su país. "
  . "No inventes datos del resultado: usa solo los que se te dan. Si la pregunta no tiene que ver con el test o con el bienestar, redirígela amablemente.";
$cuerpo = json_encode(['systemInstruction' => ['parts' => [['text' => $sistema]]],
  'contents' => [['role' => 'user', 'parts' => [['text' => "Test: $test\nResultado: $resultado\n\nPregunta: $pregunta"]]]],
  'generationConfig' => ['temperature' => 0.5, 'maxOutputTokens' => 2048],
  'safetySettings' => [['category' => 'HARM_CATEGORY_DANGEROUS_CONTENT', 'threshold' => 'BLOCK_MEDIUM_AND_ABOVE']]], JSON_UNESCAPED_UNICODE);
$texto = ''; $ultimo = 0;
foreach (['gemini-flash-lite-latest', 'gemini-flash-latest'] as $m) {
  $ch = curl_init("https://generativelanguage.googleapis.com/v1beta/models/$m:generateContent");
  curl_setopt_array($ch, [CURLOPT_POST => true, CURLOPT_RETURNTRANSFER => true, CURLOPT_TIMEOUT => 40, CURLOPT_POSTFIELDS => $cuerpo,
    CURLOPT_HTTPHEADER => ['Content-Type: application/json', 'x-goog-api-key: ' . $clave]]);
  $r = json_decode((string)curl_exec($ch), true); $ultimo = curl_getinfo($ch, CURLINFO_HTTP_CODE);
  foreach (($r['candidates'][0]['content']['parts'] ?? []) as $pt) $texto .= $pt['text'] ?? '';
  if (trim($texto)) break;
}
if (!trim($texto)) { http_response_code(503); echo json_encode(['error' => 'El asistente está muy solicitado ahora mismo. Prueba en un rato.', 'codigo' => $ultimo]); exit; }
echo json_encode(['respuesta' => trim(str_replace(['—', '–'], [',', ','], $texto)), 'quedan' => 6 - $c['ip'][$ip]], JSON_UNESCAPED_UNICODE);
