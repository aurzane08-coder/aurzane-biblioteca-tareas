<?php
// Publicar en TikTok desde AURZANE (Content Posting API, publicación directa), siguiendo las
// Content Sharing Guidelines de TikTok: datos del creador, título editable, privacidad elegida por el usuario
// sin valor por defecto, interacciones desactivadas por defecto, divulgación de contenido comercial,
// vista previa, aviso de consentimiento de música y estado de la publicación.
// Solo para administradores de AURZANE (sesión de AURZANE ID comprobada con es_admin()).
header('Cache-Control: no-store, max-age=0');
$dir = dirname(__DIR__, 2) . '/privado-tiktok';
$vids = dirname(__DIR__) . '/marketing/video';

if (isset($_GET['api'])) {
  header('Content-Type: application/json; charset=utf-8');
  $tk = preg_replace('/^Bearer\s+/i', '', $_SERVER['HTTP_AUTHORIZATION'] ?? $_SERVER['REDIRECT_HTTP_AUTHORIZATION'] ?? '');
  $ch = curl_init('https://chtfpqwrrarfdjcivlad.supabase.co/rest/v1/rpc/es_admin');
  curl_setopt_array($ch, [CURLOPT_POST => true, CURLOPT_RETURNTRANSFER => true, CURLOPT_TIMEOUT => 15, CURLOPT_POSTFIELDS => '{}',
    CURLOPT_HTTPHEADER => ['apikey: sb_publishable___1v6VjDew0l8uGfMyb9Nw_YyCLTPPw', 'Authorization: Bearer ' . $tk, 'Content-Type: application/json']]);
  if (!$tk || trim((string)curl_exec($ch)) !== 'true') { http_response_code(403); echo '{"error":"Solo para administradores de AURZANE"}'; exit; }

  function tt($url, $body = null, $tok = null, $form = false) {
    $c = curl_init($url);
    $h = $form ? ['Content-Type: application/x-www-form-urlencoded'] : ['Content-Type: application/json; charset=UTF-8'];
    if ($tok) $h[] = 'Authorization: Bearer ' . $tok;
    curl_setopt_array($c, [CURLOPT_RETURNTRANSFER => true, CURLOPT_TIMEOUT => 60, CURLOPT_HTTPHEADER => $h]);
    if ($body !== null) { curl_setopt($c, CURLOPT_POST, true); curl_setopt($c, CURLOPT_POSTFIELDS, $form ? http_build_query($body) : json_encode($body)); }
    return json_decode((string)curl_exec($c), true) ?: [];
  }
  function token($dir) {
    $app = array_map(fn($v) => trim((string)$v), json_decode(@file_get_contents("$dir/app.json"), true) ?: []);
    $rt = trim((string)@file_get_contents("$dir/refresh"));
    if (!$rt || empty($app['client_key'])) return null;
    $r = tt('https://open.tiktokapis.com/v2/oauth/token/', ['client_key' => $app['client_key'], 'client_secret' => $app['client_secret'], 'grant_type' => 'refresh_token', 'refresh_token' => $rt], null, true);
    if (!empty($r['refresh_token']) && $r['refresh_token'] !== $rt) { file_put_contents("$dir/refresh", $r['refresh_token']); @chmod("$dir/refresh", 0600); }
    return $r['access_token'] ?? null;
  }
  $acc = $_GET['api'];
  if ($acc === 'videos') {
    $l = glob("$vids/*.mp4") ?: []; usort($l, fn($a, $b) => filemtime($b) - filemtime($a));
    echo json_encode(array_map(fn($f) => ['archivo' => basename($f), 'url' => 'https://aurzane.com/marketing/video/' . rawurlencode(basename($f)), 'mb' => round(filesize($f) / 1048576, 1)], array_slice($l, 0, 40))); exit;
  }
  $tok = token($dir);
  if (!$tok) { http_response_code(409); echo '{"error":"La cuenta de TikTok no está conectada. Conéctala en aurzane.com/tiktok/?inicio=1"}'; exit; }
  if ($acc === 'creador') { echo json_encode(tt('https://open.tiktokapis.com/v2/post/publish/creator_info/query/', new stdClass, $tok)); exit; }
  if ($acc === 'estado') { echo json_encode(tt('https://open.tiktokapis.com/v2/post/publish/status/fetch/', ['publish_id' => (string)($_GET['id'] ?? '')], $tok)); exit; }
  if ($acc === 'publicar' && $_SERVER['REQUEST_METHOD'] === 'POST') {
    $in = json_decode(file_get_contents('php://input'), true) ?: [];
    $f = $vids . '/' . basename((string)($in['archivo'] ?? ''));
    if (!is_file($f)) { http_response_code(400); echo '{"error":"Ese vídeo no existe"}'; exit; }
    if (empty($in['privacidad'])) { http_response_code(400); echo '{"error":"Elige quién puede ver el vídeo"}'; exit; }
    $tam = filesize($f);
    $info = ['title' => mb_substr((string)($in['titulo'] ?? ''), 0, 2200), 'privacy_level' => (string)$in['privacidad'],
      'disable_comment' => empty($in['comentarios']), 'disable_duet' => empty($in['duo']), 'disable_stitch' => empty($in['stitch']),
      'brand_content_toggle' => !empty($in['marca_terceros']), 'brand_organic_toggle' => !empty($in['marca_propia'])];
    $ini = tt('https://open.tiktokapis.com/v2/post/publish/video/init/', ['post_info' => $info,
      'source_info' => ['source' => 'FILE_UPLOAD', 'video_size' => $tam, 'chunk_size' => $tam, 'total_chunk_count' => 1]], $tok);
    if (empty($ini['data']['upload_url'])) { http_response_code(502); echo json_encode(['error' => $ini['error']['message'] ?? 'TikTok no aceptó la publicación', 'detalle' => $ini['error'] ?? null]); exit; }
    $c = curl_init($ini['data']['upload_url']);
    curl_setopt_array($c, [CURLOPT_CUSTOMREQUEST => 'PUT', CURLOPT_RETURNTRANSFER => true, CURLOPT_TIMEOUT => 600, CURLOPT_POSTFIELDS => file_get_contents($f),
      CURLOPT_HTTPHEADER => ['Content-Type: video/mp4', 'Content-Range: bytes 0-' . ($tam - 1) . '/' . $tam]]);
    curl_exec($c);
    echo json_encode(['publish_id' => $ini['data']['publish_id']]); exit;
  }
  http_response_code(400); echo '{"error":"Acción no válida"}'; exit;
}
header('Content-Type: text/html; charset=utf-8');
?><!DOCTYPE html>
<html lang="es"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><meta name="robots" content="noindex,nofollow"><meta name="aurzane-idiomas" content="no">
<title>Publicar en TikTok · AURZANE</title>
<link href="https://fonts.googleapis.com/css2?family=Instrument+Sans:wght@400;600;700&display=swap" rel="stylesheet">
<style>
:root{--bg:#0F1530;--card:#171F45;--line:rgba(255,255,255,.12);--txt:#F5F3EE;--dim:#A9B0C4;--acc:#25F4EE;--rosa:#FE2C55}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--txt);font:15px/1.5 "Instrument Sans",system-ui,sans-serif}
main{max-width:980px;margin:0 auto;padding:28px 18px 60px}h1{font-size:1.6rem;margin:0 0 4px}p.d{color:var(--dim);margin:0 0 20px}
.g{display:grid;grid-template-columns:300px 1fr;gap:22px}@media(max-width:760px){.g{grid-template-columns:1fr}}
.c{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:18px}
video{width:100%;aspect-ratio:9/16;background:#000;border-radius:12px}
label{display:block;font-weight:600;margin:14px 0 6px}select,textarea{width:100%;background:#0B1026;color:var(--txt);border:1px solid var(--line);border-radius:10px;padding:10px;font:inherit}
.t{display:flex;align-items:center;justify-content:space-between;gap:12px;padding:10px 0;border-bottom:1px solid var(--line)}.t small{color:var(--dim);display:block}
.t input{width:20px;height:20px}.cr{display:flex;align-items:center;gap:12px}.cr img{width:46px;height:46px;border-radius:50%}
.btn{background:var(--rosa);color:#fff;border:0;border-radius:99px;padding:13px 22px;font:700 1rem inherit;cursor:pointer;width:100%;margin-top:16px}.btn:disabled{opacity:.5;cursor:not-allowed}
.aviso{font-size:.86rem;color:var(--dim);margin-top:12px}.aviso a{color:var(--acc)}.err{color:#ffaaa3}.ok{color:#9be8cc}.sub{margin-left:28px}
</style></head><body><main>
<h1>Publicar en TikTok</h1><p class="d">Elige un vídeo de AURZANE, revisa cómo se publicará y envíalo a tu cuenta de TikTok.</p>
<div id="app" class="c">Cargando…</div>
</main>
<script src="https://unpkg.com/@supabase/supabase-js@2.45.4/dist/umd/supabase.js"></script>
<script src="/aurzane-id.js"></script>
<script>
(async function(){
  const app = document.getElementById('app'), E = s => String(s ?? '').replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
  let sb; try { sb = crearClienteAurzaneID('https://chtfpqwrrarfdjcivlad.supabase.co', 'sb_publishable___1v6VjDew0l8uGfMyb9Nw_YyCLTPPw'); } catch(e) {}
  const s = sb && (await sb.auth.getSession()).data.session;
  if(!s){ app.innerHTML = 'Inicia sesión en <a style="color:var(--acc)" href="https://aurzane.com/admin.html">AURZANE Admin</a> y vuelve a esta página.'; return; }
  const api = async (a, opt) => { const r = await fetch('?api=' + a, Object.assign({ headers:{ Authorization:'Bearer ' + s.access_token, 'Content-Type':'application/json' }, cache:'no-store' }, opt||{})); const j = await r.json().catch(()=>({})); if(!r.ok) throw new Error(j.error || ('Error ' + r.status)); return j; };
  let cr, vids;
  try { [cr, vids] = await Promise.all([api('creador'), api('videos')]); } catch(e){ app.innerHTML = '<p class="err">' + E(e.message) + '</p>'; return; }
  const c = cr.data || {};
  if(!c.creator_username){ app.innerHTML = '<p class="err">TikTok no devolvió los datos de la cuenta: ' + E((cr.error||{}).message || '') + '</p>'; return; }
  const PRIV = { PUBLIC_TO_EVERYONE:'Todo el mundo', MUTUAL_FOLLOW_FRIENDS:'Amigos (os seguís mutuamente)', FOLLOWER_OF_CREATOR:'Seguidores', SELF_ONLY:'Solo yo' };
  app.className = '';
  app.innerHTML = `<div class="g"><div class="c"><video id="v" controls playsinline></video><label for="vid">Vídeo</label><select id="vid">${vids.map(v => `<option value="${E(v.archivo)}" data-url="${E(v.url)}">${E(v.archivo.replace(/^m1-/,'').replace(/\.mp4$/,''))} · ${v.mb} MB</option>`).join('')}</select></div>
  <div class="c"><div class="cr">${c.creator_avatar_url?`<img src="${E(c.creator_avatar_url)}" alt="">`:''}<div><b>${E(c.creator_nickname)}</b><div class="d" style="color:var(--dim)">@${E(c.creator_username)} · se publicará en esta cuenta</div></div></div>
  <label for="tit">Título</label><textarea id="tit" rows="3" maxlength="2200"></textarea>
  <label for="priv">¿Quién puede ver este vídeo?</label><select id="priv"><option value="" selected disabled>Elige una opción</option>${(c.privacy_level_options||[]).map(o => `<option value="${o}">${PRIV[o]||o}</option>`).join('')}</select>
  <label>Permitir que los usuarios</label>
  <div class="t"><span>Comenten${c.comment_disabled?'<small>Desactivado en la configuración de tu cuenta</small>':''}</span><input type="checkbox" id="com" ${c.comment_disabled?'disabled':''}></div>
  <div class="t"><span>Hagan dúo${c.duet_disabled?'<small>Desactivado en la configuración de tu cuenta</small>':''}</span><input type="checkbox" id="duo" ${c.duet_disabled?'disabled':''}></div>
  <div class="t"><span>Hagan stitch${c.stitch_disabled?'<small>Desactivado en la configuración de tu cuenta</small>':''}</span><input type="checkbox" id="sti" ${c.stitch_disabled?'disabled':''}></div>
  <div class="t"><span>Divulgar contenido comercial<small>Indica si el vídeo promociona una marca, producto o servicio.</small></span><input type="checkbox" id="comer"></div>
  <div id="comerOps" hidden>
    <div class="t sub"><span>Tu marca<small>Promocionas tu propio negocio. Se etiquetará como «Contenido promocional».</small></span><input type="checkbox" id="propia"></div>
    <div class="t sub"><span>Contenido de marca<small>Promocionas a otra marca o a un tercero. Se etiquetará como «Colaboración pagada».</small></span><input type="checkbox" id="terceros"></div>
    <p class="aviso" id="comerAviso"></p>
  </div>
  <p class="aviso" id="cons"></p>
  <button class="btn" id="pub" disabled>Publicar en TikTok</button><p class="aviso" id="est" aria-live="polite"></p></div></div>`;
  const $ = id => document.getElementById(id), v = $('v'), max = c.max_video_post_duration_sec || 600;
  const ponVideo = () => { const o = $('vid').selectedOptions[0]; if(!o) return; v.src = o.dataset.url; $('tit').value = o.value.replace(/^m1-/,'').replace(/\.mp4$/,'').replace(/[-_]/g,' ') + ' #AURZANE'; };
  $('vid').onchange = ponVideo; ponVideo();
  v.onloadedmetadata = () => { if(v.duration > max) { $('est').innerHTML = '<span class="err">Este vídeo dura más de lo que permite tu cuenta (' + max + ' s).</span>'; } valida(); };
  const valida = () => {
    const comer = $('comer').checked, propia = $('propia').checked, terceros = $('terceros').checked;
    $('comerOps').hidden = !comer;
    if(terceros && $('priv').value === 'SELF_ONLY'){ $('priv').value = ''; }
    [...$('priv').options].forEach(o => { if(o.value === 'SELF_ONLY'){ o.disabled = terceros; o.title = terceros ? 'El contenido de marca no puede ser privado' : ''; } });
    $('comerAviso').textContent = comer && !propia && !terceros ? 'Elige al menos una opción para indicar qué estás promocionando.' : (terceros ? 'Tu vídeo se etiquetará como «Colaboración pagada».' : propia ? 'Tu vídeo se etiquetará como «Contenido promocional».' : '');
    $('cons').innerHTML = terceros
      ? 'Al publicar, aceptas la <a href="https://www.tiktok.com/legal/page/global/bc-policy/es" target="_blank" rel="noopener">Política de contenido de marca</a> y la <a href="https://www.tiktok.com/legal/page/global/music-usage-confirmation/es" target="_blank" rel="noopener">Confirmación de uso de música</a> de TikTok.'
      : 'Al publicar, aceptas la <a href="https://www.tiktok.com/legal/page/global/music-usage-confirmation/es" target="_blank" rel="noopener">Confirmación de uso de música</a> de TikTok.';
    $('pub').disabled = !$('priv').value || (comer && !propia && !terceros) || (v.duration && v.duration > max);
  };
  ['priv','comer','propia','terceros'].forEach(id => $(id).onchange = valida); valida();
  $('pub').onclick = async () => {
    $('pub').disabled = true; $('est').textContent = 'Enviando el vídeo a TikTok…';
    try {
      const r = await api('publicar', { method:'POST', body: JSON.stringify({ archivo:$('vid').value, titulo:$('tit').value, privacidad:$('priv').value, comentarios:$('com').checked, duo:$('duo').checked, stitch:$('sti').checked, marca_propia:$('propia').checked, marca_terceros:$('terceros').checked }) });
      $('est').innerHTML = 'Vídeo enviado. TikTok puede tardar unos minutos en procesarlo y mostrarlo en tu perfil.';
      for(let i = 0; i < 20; i++){ await new Promise(x => setTimeout(x, 6000)); const e = await api('estado&id=' + encodeURIComponent(r.publish_id)); const st = (e.data||{}).status;
        if(st === 'PUBLISH_COMPLETE'){ $('est').innerHTML = '<span class="ok">Publicado en TikTok.</span>'; break; }
        if(st === 'FAILED'){ $('est').innerHTML = '<span class="err">TikTok no pudo publicarlo: ' + E((e.data||{}).fail_reason || '') + '</span>'; break; }
        $('est').textContent = 'TikTok está procesando el vídeo (' + (st || 'en cola') + ')…'; }
    } catch(e){ $('est').innerHTML = '<span class="err">' + E(e.message) + '</span>'; }
    valida();
  };
})();
</script></body></html>
