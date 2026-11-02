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
const esc = s => String(s || '').replace(/&/g, '&amp;').replace(/</g, '&lt;');
(async () => {
  const L = JSON.parse(fs.readFileSync(LISTA, 'utf8'));
  const b = await chromium.launch(); const pg = await b.newPage({viewport: {width: 1080, height: 1350}});
  for (const x of L) {
    const t = T[x.mundo] || T.aurzane; const largo = (x.titulo || '').length;
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
<div class="pie"><div class="url">${esc(x.pie)}</div><div class="g">Gratis</div></div></div></body></html>`;
    fs.writeFileSync('/tmp/tarjeta.html', html); await pg.goto('file:///tmp/tarjeta.html'); await pg.waitForTimeout(250);
    await pg.screenshot({path: x.salida, type: 'jpeg', quality: 86}); console.log(x.salida);
  }
  await b.close();
})();
