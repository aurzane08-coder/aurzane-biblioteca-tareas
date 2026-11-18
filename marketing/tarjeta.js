// Genera tarjetas 1080x1350 (formato vertical para redes) a partir de una lista JSON.
// Uso: node marketing/tarjeta.js lista.json carpeta_fuentes_fontsource
//   lista.json = [{id, mundo, kicker, titulo, sub, pie, emoji, salida}]
const {chromium} = require('playwright'); const fs = require('fs');
const [, , LISTA, F] = process.argv;
const T = {
  mind: ['#16112b', '#33246a', '#6b4fc7', '#e8cd8f', '#ff9a7a'],
  live: ['#2a1610', '#5e2c1b', '#b45a33', '#ffb38a', '#f2c14e'],
  build: ['#0f1823', '#1d3349', '#2f5d7c', '#f2b544', '#ff8a4c'],
  nexus: ['#0f1538', '#1e2a78', '#3a50c4', '#9fb4ff', '#7ee0ff'],
  learn: ['#13281d', '#24513a', '#4a8a66', '#c8e6a0', '#f2d16b'],
  aurzane: ['#141226', '#2a2450', '#55479e', '#e8cd8f', '#c9a24b'],
};
async function frase(pg, x, t) {
  if (x.foto && x.foto.startsWith('/')) fs.copyFileSync(x.foto, '/tmp/foto.jpg');
  else if (x.foto) { const r = await fetch(x.foto); if (r.ok) fs.writeFileSync('/tmp/foto.jpg', Buffer.from(await r.arrayBuffer())); else x.foto = ''; }
  const n = x.frase.length, tam = n > 110 ? 66 : n > 75 ? 78 : n > 45 ? 92 : 108;
  const fondo = x.foto ? `url(file:///tmp/foto.jpg?${Date.now()}) center/cover` : `radial-gradient(120% 90% at 80% 10%,${t[2]} 0%,${t[1]} 50%,${t[0]} 100%)`;
  const html = `<html><head><meta charset="utf-8"><style>
@font-face{font-family:B;src:url(file://${F}/bodoni-moda/files/bodoni-moda-latin-700-normal.woff2)}
@font-face{font-family:I;src:url(file://${F}/instrument-sans/files/instrument-sans-latin-500-normal.woff2)}
*{box-sizing:border-box}body{margin:0;width:1080px;height:1350px;color:#fff;font-family:I;background:${fondo};position:relative;overflow:hidden}
body:before{content:"";position:absolute;inset:0;background:${x.foto ? `radial-gradient(90% 60% at 50% 50%,${t[0]}b3 0%,${t[0]}80 55%,${t[0]}40 100%)` : 'none'}}
.w{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;padding:0 110px;text-align:center}
.c{font-family:B;font-size:180px;line-height:.6;color:${t[4]};opacity:.9;height:90px}
h1{font-family:B;font-size:${tam}px;line-height:1.12;margin:20px 0 0;text-shadow:0 4px 30px rgba(0,0,0,.35)}
.a{margin-top:40px;font-size:30px;color:${t[3]};letter-spacing:.02em}
.l{width:90px;height:3px;background:${t[4]};margin:46px auto 0;border-radius:3px}
.top{position:absolute;top:70px;left:0;right:0;text-align:center;font-family:B;font-size:36px;letter-spacing:.1em}.top span{color:${t[4]}}
.pie{position:absolute;bottom:64px;left:0;right:0;text-align:center;font-size:26px;opacity:.85}
.cred{position:absolute;bottom:24px;right:30px;font-size:17px;opacity:.6}
</style></head><body><div class="top">AUR<span>Z</span>ANE</div><div class="w"><div class="c">“</div><h1>${esc(x.frase)}</h1>${x.autor ? `<div class="a">${esc(x.autor)}</div>` : '<div class="l"></div>'}</div>
${x.credito ? `<div class="cred">${esc(x.credito)}</div>` : ''}</body></html>`;
  fs.writeFileSync('/tmp/tarjeta.html', html); await pg.goto('file:///tmp/tarjeta.html'); await pg.waitForTimeout(250);
  await pg.screenshot({path: x.salida, type: 'jpeg', quality: 88});
}
// Capa transparente 1080x1920 para vídeos verticales (Reels, Shorts, TikTok): el vídeo de fondo se pone con ffmpeg.
async function capa(pg, x, t) {
  // Vídeo vertical (17/11/2026): la capa sale en 4 PNG del mismo diseño para que el vídeo los muestre por pasos
  // (marca y etiqueta, título, y autor o explicación). Todo dentro de la zona segura
  // de TikTok, Reels y Shorts: nada bajo los botones de la derecha ni bajo el texto de abajo.
  await pg.setViewportSize({width: 1080, height: 1920});
  const n = (x.titulo || '').length, tam = n > 110 ? 68 : n > 75 ? 80 : n > 45 ? 94 : 108;
  const html = (paso) => `<html><head><meta charset="utf-8"><style>
@font-face{font-family:B;src:url(file://${F}/bodoni-moda/files/bodoni-moda-latin-700-normal.woff2)}
@font-face{font-family:I;src:url(file://${F}/instrument-sans/files/instrument-sans-latin-500-normal.woff2)}
@font-face{font-family:I;font-weight:700;src:url(file://${F}/instrument-sans/files/instrument-sans-latin-700-normal.woff2)}
*{box-sizing:border-box}html,body{margin:0;width:1080px;height:1920px;background:transparent;color:#fff;font-family:I;overflow:hidden}
.o{visibility:hidden}
.v{position:absolute;inset:0;background:linear-gradient(180deg,${t[0]}b3 0%,${t[0]}00 20%,${t[0]}33 38%,${t[0]}b3 58%,${t[0]}f0 100%)}
.top{position:absolute;top:150px;left:0;right:0;text-align:center;font-family:B;font-size:46px;letter-spacing:.12em;text-shadow:0 2px 18px rgba(0,0,0,.4)}.top span{color:${t[4]}}
.w{position:absolute;left:96px;right:150px;bottom:560px;text-align:center}
.k{display:inline-block;font-size:34px;font-weight:700;padding:12px 30px;border-radius:99px;background:rgba(255,255,255,.16);border:2px solid rgba(255,255,255,.3);margin-bottom:34px}
h1{font-family:B;font-size:${tam}px;line-height:1.1;margin:0;text-shadow:0 6px 40px rgba(0,0,0,.5)}
.q{display:block;font-size:${Math.round(tam * 1.9)}px;line-height:.55;height:${Math.round(tam * .62)}px;color:${t[4]}}
.a{margin-top:34px;font-size:36px;color:${t[3]};font-weight:700;letter-spacing:.02em}
.a:before{content:"";display:block;width:70px;height:3px;background:${t[4]};margin:0 auto 26px;border-radius:3px}
p{font-size:40px;line-height:1.38;margin:30px 0 0;opacity:.95;text-shadow:0 2px 20px rgba(0,0,0,.45)}
.fin{position:absolute;left:96px;right:150px;bottom:430px;text-align:center}
.fin b{display:inline-block;font-size:32px;color:${t[0]};background:linear-gradient(90deg,${t[3]},${t[4]});padding:16px 34px;border-radius:99px;box-shadow:0 10px 30px rgba(0,0,0,.3)}
</style></head><body><div class="v ${paso === 0 ? '' : 'o'}"></div><div class="top ${paso === 0 ? '' : 'o'}">AUR<span>Z</span>ANE</div>
<div class="w">${x.kicker ? `<div class="k ${paso === 0 ? '' : 'o'}">${esc(x.kicker)}</div>` : ''}<h1 class="${paso === 1 ? '' : 'o'}">${x.cita ? '<span class="q">“</span>' : ''}${esc(x.titulo)}</h1>${x.autor ? `<div class="a ${paso === 2 ? '' : 'o'}">${esc(x.autor)}</div>` : ''}${x.sub ? `<p class="${paso === 2 ? '' : 'o'}">${esc(x.sub)}</p>` : ''}</div>
</body></html>`;
  for (const paso of [0, 1, 2]) {   // sin «Síguenos» al final (18/11/2026): así el vídeo se comparte mejor
    fs.writeFileSync('/tmp/capa.html', html(paso)); await pg.goto('file:///tmp/capa.html'); await pg.waitForTimeout(200);
    await pg.screenshot({path: paso ? x.salida.replace(/\.png$/, `-${paso}.png`) : x.salida, type: 'png', omitBackground: true});
  }
  await pg.setViewportSize({width: 1080, height: 1350});
}
const esc = s => String(s || '').replace(/&/g, '&amp;').replace(/</g, '&lt;');
(async () => {
  const L = JSON.parse(fs.readFileSync(LISTA, 'utf8'));
  const b = await chromium.launch(); const pg = await b.newPage({viewport: {width: 1080, height: 1350}});
  for (const x of L) {
    const t = T[x.mundo] || T.aurzane;
    if (x.capa) { await capa(pg, x, t); console.log(x.salida); continue; }
    if (x.frase) { await frase(pg, x, t); console.log(x.salida); continue; }
    const largo = (x.titulo || '').length;
    const fs1 = largo > 90 ? 64 : largo > 60 ? 76 : largo > 38 ? 92 : 108;
    if (x.foto && x.foto.startsWith('/')) fs.copyFileSync(x.foto, '/tmp/foto.jpg');
    else if (x.foto) { const r = await fetch(x.foto); if (r.ok) { fs.writeFileSync('/tmp/foto.jpg', Buffer.from(await r.arrayBuffer())); } else x.foto = ''; }
    const fondo = x.foto ? `url(file:///tmp/foto.jpg?${Date.now()}) center/cover` : `radial-gradient(120% 90% at 85% 0%,${t[2]} 0%,${t[1]} 45%,${t[0]} 100%)`;
    const html = `<html><head><meta charset="utf-8"><style>
@font-face{font-family:B;src:url(file://${F}/bodoni-moda/files/bodoni-moda-latin-700-normal.woff2)}
@font-face{font-family:I;src:url(file://${F}/instrument-sans/files/instrument-sans-latin-500-normal.woff2)}
@font-face{font-family:I;font-weight:700;src:url(file://${F}/instrument-sans/files/instrument-sans-latin-700-normal.woff2)}
*{box-sizing:border-box}body{margin:0;width:1080px;height:1350px;color:#fff;font-family:I;background:${fondo};position:relative;overflow:hidden}
body:before{content:"";position:absolute;inset:0;${x.foto ? `background:linear-gradient(180deg,${t[0]}cc 0%,${t[0]}33 18%,${t[0]}00 30%,${t[0]}66 46%,${t[0]}f2 66%,${t[0]} 100%)` : 'background-image:radial-gradient(rgba(255,255,255,.09) 1.6px,transparent 1.8px);background-size:34px 34px'}}
.w{${x.foto ? 'justify-content:flex-end' : ''}}
.cred{position:absolute;right:80px;top:92px;font-size:19px;opacity:.75}
.w{position:absolute;inset:78px 80px 84px;display:flex;flex-direction:column}
.w.f .top{position:absolute;top:0;left:0}.w.f .pie{margin-top:44px}
.top{font-family:B;font-size:40px;letter-spacing:.08em}.top span{color:${t[4]}}.top small{font-family:I;font-size:22px;opacity:.72;letter-spacing:.16em;margin-left:12px}
.e{font-size:210px;line-height:1;margin-top:70px;filter:drop-shadow(0 24px 44px rgba(0,0,0,.35))}
.k{align-self:flex-start;margin-top:56px;font-size:30px;font-weight:700;padding:10px 26px;border-radius:99px;background:rgba(255,255,255,.12);border:1.5px solid rgba(255,255,255,.24)}
h1{font-family:B;font-size:${fs1}px;line-height:1.04;margin:30px 0 0;letter-spacing:-.005em}
p{font-size:36px;line-height:1.38;margin:30px 0 0;opacity:.88;max-width:900px}
.pie{margin-top:auto;display:flex;justify-content:space-between;align-items:flex-end;gap:30px}
.url{font-size:30px;font-weight:700;color:${t[3]}}
.g{font-size:26px;font-weight:700;color:${t[0]};background:linear-gradient(90deg,${t[3]},${t[4]});padding:14px 30px;border-radius:99px;white-space:nowrap}
</style></head><body>${x.credito ? `<div class="cred">${esc(x.credito)}</div>` : ''}<div class="w${x.foto ? ' f' : ''}"><div class="top">AUR<span>Z</span>ANE<small>/ ${esc((x.mundo || '').toUpperCase())}</small></div>
${x.emoji ? `<div class="e">${x.emoji}</div>` : ''}<div class="k">${esc(x.kicker)}</div><h1>${esc(x.titulo)}</h1>${x.sub ? `<p>${esc(x.sub)}</p>` : ''}
<div class="pie"><div class="url"></div><div class="g">Gratis</div></div></div></body></html>`;
    fs.writeFileSync('/tmp/tarjeta.html', html); await pg.goto('file:///tmp/tarjeta.html'); await pg.waitForTimeout(250);
    await pg.screenshot({path: x.salida, type: 'jpeg', quality: 86}); console.log(x.salida);
  }
  await b.close();
})();
