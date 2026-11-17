<?php
// Correos de bienvenida automáticos (17/11/2026, etapa 4, tarea 45). Se ejecuta cada día por SSH desde GitHub
// (no es accesible por web). A cada suscrito confirmado le llega, según los días desde su alta, el siguiente paso:
// día 0 bienvenida y test, día 3 curso gratis con certificado, día 7 test vocacional, día 14 herramientas gratis.
// El paso enviado se guarda en privado-boletin/secuencia.json; quien se da de baja deja de recibirlos. Sin publicidad de terceros.
if (php_sapi_name() !== 'cli') { http_response_code(404); exit; }
$dir = dirname(__DIR__, 2) . '/privado-boletin';
$fs = "$dir/suscritos.json"; $fq = "$dir/secuencia.json";
$s = is_file($fs) ? (json_decode((string)file_get_contents($fs), true) ?: []) : [];
$h = fopen($fq, 'c+'); flock($h, LOCK_EX);
$q = json_decode(stream_get_contents($h) ?: '', true) ?: [];
$u = fn($url, $c) => $url . (strpos($url, '?') === false ? '?' : '&') . "utm_source=boletin&utm_medium=email&utm_campaign=bienvenida&utm_content=$c";
$b = fn($url, $t, $c) => "<p><a href='" . $u($url, $c) . "' style='display:inline-block;background:#E2BF6A;color:#1b1440;padding:12px 22px;border-radius:99px;font-weight:700;text-decoration:none'>$t</a></p>";
$PASOS = [
  [0, 'Bienvenida a AURZANE: empieza por aquí',
   "<p>Gracias por confirmar. Cada domingo te llegará el boletín con el libro recomendado, el artículo nuevo y un test gratis.</p><p>Para empezar, un test corto y validado que muchos lectores hacen primero: mide tu nivel de estrés en 3 minutos, gratis y sin registro.</p>"
   . $b('https://mind.aurzane.com/test-de-estres/', 'Hacer el test de estrés', 'd0') . "<p>Es orientativo: no sustituye una valoración profesional.</p>"],
  [3, 'Un curso gratis con certificado para ti',
   "<p>En AURZANE LEARN tienes cursos breves, gratis y con certificado al aprobar: dormir mejor, autoestima, neurociencia y más. Se hacen a tu ritmo, desde el móvil.</p>"
   . $b('https://learn.aurzane.com/', 'Ver los cursos gratis', 'd3')],
  [7, '¿Qué carrera encaja contigo? Test vocacional gratis',
   "<p>Si tú o alguien de tu casa está pensando qué estudiar, el test vocacional de AURZANE relaciona intereses con carreras reales. Después puedes comparar universidades de 55 países en NEXUS.</p>"
   . $b('https://ovp.aurzane.com/', 'Hacer el test vocacional', 'd7') . $b('https://nexus.aurzane.com/universidades/comparar/', 'Comparar universidades', 'd7b')],
  [14, 'Calculadoras gratis que te ahorran dinero',
   "<p>Hipoteca con el Euríbor del día, finiquito, sueldo neto, subida del alquiler en tu municipio con datos del INE… Todas gratis y sin registro.</p>"
   . $b('https://build.aurzane.com/', 'Ver las calculadoras', 'd14')],
];
$hoy = time(); $env = 0;
foreach ($s as $e => $v) {
    if (!empty($q[$e]['fin'])) continue;
    $dias = (int)floor(($hoy - strtotime($v['alta'] ?? 'now')) / 86400);
    $hecho = (int)($q[$e]['paso'] ?? -1);
    $sig = null;   // solo el paso más reciente que toque (nunca varios el mismo día)
    foreach ($PASOS as $i => $p) if ($i > $hecho && $dias >= $p[0]) $sig = $i;
    if ($sig === null) continue;
    [$d, $asunto, $cuerpo] = $PASOS[$sig];
    $baja = 'https://aurzane.com/boletin/?baja=' . $v['baja'];
    $html = "<div style='font:16px/1.6 system-ui,sans-serif;max-width:520px;color:#1b1440'><p style='letter-spacing:.08em;color:#a8862f;font-weight:700'>AURZANE</p>$cuerpo"
          . "<p style='color:#777;font-size:13px;margin-top:28px'>Recibes este correo porque te suscribiste al boletín de AURZANE. <a href='$baja' style='color:#777'>Darme de baja</a></p></div>";
    $cab = "MIME-Version: 1.0\r\nContent-Type: text/html; charset=UTF-8\r\nFrom: AURZANE <hola@aurzane.com>\r\nReply-To: hola@aurzane.com\r\nList-Unsubscribe: <$baja>\r\nList-Unsubscribe-Post: List-Unsubscribe=One-Click\r\n";
    if (mail($e, '=?UTF-8?B?' . base64_encode($asunto) . '?=', $html, $cab, '-fhola@aurzane.com')) {
        $q[$e] = ['paso' => $sig, 'fecha' => date('c'), 'fin' => $sig === count($PASOS) - 1 ? 1 : 0]; $env++;
    }
    usleep(300000);
}
foreach (array_keys($q) as $e) if (!isset($s[$e])) unset($q[$e]);   // bajas: fuera también de la secuencia
ftruncate($h, 0); rewind($h); fwrite($h, json_encode($q, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT)); fflush($h); flock($h, LOCK_UN); fclose($h); @chmod($fq, 0600);
echo "bienvenida: $env correos; " . count($s) . " suscritos\n";
