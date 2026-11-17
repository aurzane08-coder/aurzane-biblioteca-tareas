<?php
// Correo con la descripción lista para copiar cuando un vídeo llega como borrador a la bandeja de TikTok
// (la bandeja no admite descripción). Se ejecuta en el servidor desde el flujo «Marketing automático»; lee el texto por la entrada estándar.
$t = trim(stream_get_contents(STDIN));
if ($t === '') exit;
$html = '<div style="font-family:Arial,sans-serif;font-size:15px;line-height:1.5;color:#222"><p><b>Tienes un vídeo nuevo en la bandeja de TikTok.</b> Ábrelo en la app, añade un sonido que esté en tendencia si quieres, pega esta descripción y publícalo.</p>'
      . '<pre style="white-space:pre-wrap;font-family:Arial,sans-serif;font-size:15px;background:#f4f2fb;padding:16px;border-radius:10px">' . htmlspecialchars($t) . '</pre>'
      . '<p style="color:#666;font-size:13px">Horas con más público: 18:00 y 22:00 (España).</p></div>';
$cab = "MIME-Version: 1.0\r\nContent-Type: text/html; charset=UTF-8\r\nFrom: AURZANE <hola@aurzane.com>\r\n";
foreach (['hola@aurzane.com', 'aurzane08@gmail.com'] as $para) @mail($para, '=?UTF-8?B?' . base64_encode('TikTok: vídeo listo para publicar') . '?=', $html, $cab, '-fhola@aurzane.com');
echo "aviso enviado\n";
