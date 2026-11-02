// Kit de marca para los perfiles de redes: foto de perfil y portadas con foto de Pexels (licencia Pexels: uso comercial gratis).
// Uso (lo ejecuta .github/workflows/marca.yml): node marketing/marca.js carpeta_fuentes_fontsource
// Salida: marketing/marca/*.png y *.jpg
const {chromium} = require('playwright'); const fs = require('fs'); const path = require('path');
const F = process.argv[2]; const OUT = path.join(__dirname, 'marca'); fs.mkdirSync(OUT, {recursive: true});
const C = {fondo: '#141226', medio: '#2a2450', violeta: '#55479e', oro: '#e8cd8f', oroF: '#c9a24b'};
const FOTOS = {lago: '33828128', pradera: '16970874', montana: '36168129'};
const foto = (id, w, h) => `https://images.pexels.com/photos/${id}/pexels-photo-${id}.jpeg?auto=compress&cs=tinysrgb&w=${w}&h=${h}&fit=crop`;
const UA = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36', 'Referer': 'https://www.pexels.com/'};
const fuentes = `@font-face{font-family:B;src:url(file://${F}/bodoni-moda/files/bodoni-moda-latin-700-normal.woff2)}
@font-face{font-family:I;src:url(file://${F}/instrument-sans/files/instrument-sans-latin-500-normal.woff2)}
@font-face{font-family:I;font-weight:700;src:url(file://${F}/instrument-sans/files/instrument-sans-latin-700-normal.woff2)}`;

// Portadas: [nombre, ancho, alto, ancho de la zona segura centrada, alto zona segura, foto]
const PORTADAS = [
  ['portada-youtube', 2560, 1440, 1546, 360, 'lago'],
  ['portada-facebook', 1640, 624, 1100, 480, 'lago'],
  ['portada-bluesky-mastodon', 1500, 500, 1300, 360, 'lago'],
  ['portada-pinterest', 1600, 900, 1200, 600, 'lago'],
];

async function descargar(id, w, h) {
  const r = await fetch(foto(FOTOS[id], w, h), {headers: UA});
  if (!r.ok) throw new Error('foto ' + r.status);
  const f = `/tmp/marca-${id}-${w}x${h}.jpg`; fs.writeFileSync(f, Buffer.from(await r.arrayBuffer())); return f;
}

(async () => {
  const b = await chromium.launch(); const pg = await b.newPage();
  // Foto de perfil: monograma AZ dorado sobre fondo de la marca (se ve bien también en círculo y en tamaño pequeño).
  await pg.setViewportSize({width: 1080, height: 1080});
  await pg.setContent(`<html><head><meta charset="utf-8"><style>${fuentes}
  body{margin:0;width:1080px;height:1080px;display:flex;align-items:center;justify-content:center;
  background:radial-gradient(75% 75% at 50% 35%,${C.violeta} 0%,${C.medio} 45%,${C.fondo} 100%)}
  .c{width:820px;height:820px;border-radius:50%;border:10px solid ${C.oro}55;display:flex;flex-direction:column;align-items:center;justify-content:center}
  .m{font-family:B;font-size:440px;line-height:1;color:${C.oro};letter-spacing:-0.02em;text-shadow:0 10px 50px rgba(0,0,0,.45)}
  .m span{color:#fff}
  .t{font-family:B;font-size:74px;letter-spacing:.2em;color:#fff;margin-top:6px}.t span{color:${C.oro}}
  </style></head><body><div class="c"><div class="m">A<span>Z</span></div><div class="t">AUR<span>Z</span>ANE</div></div></body></html>`);
  await pg.waitForTimeout(400); await pg.screenshot({path: path.join(OUT, 'perfil.png')});

  for (const [n, w, h, sw, sh, id] of PORTADAS) {
    const f = await descargar(id, w, h);
    await pg.setViewportSize({width: w, height: h});
    const k = sh / 423;  // escala de letra según la zona segura
    const html = `<html><head><meta charset="utf-8"><style>${fuentes}
    body{margin:0;width:${w}px;height:${h}px;position:relative;overflow:hidden;color:#fff;font-family:I;
    background:url(file://${f}) center/cover}
    body:before{content:"";position:absolute;inset:0;background:linear-gradient(90deg,${C.fondo}e6 0%,${C.fondo}b3 45%,${C.fondo}40 100%)}
    .z{position:absolute;left:${(w - sw) / 2}px;top:${(h - sh) / 2}px;width:${sw}px;height:${sh}px;display:flex;flex-direction:column;justify-content:center;padding-left:${Math.round(sw * .04)}px}
    .l{font-family:B;font-size:${Math.round(120 * k)}px;letter-spacing:.12em;line-height:1}.l span{color:${C.oro}}
    .s{font-family:B;font-size:${Math.round(54 * k)}px;margin-top:${Math.round(22 * k)}px;line-height:1.15}
    .d{font-size:${Math.round(30 * k)}px;margin-top:${Math.round(18 * k)}px;opacity:.92}
    .u{display:inline-block;margin-top:${Math.round(22 * k)}px;font-weight:700;font-size:${Math.round(28 * k)}px;color:${C.fondo};background:linear-gradient(90deg,${C.oro},${C.oroF});padding:${Math.round(8 * k)}px ${Math.round(22 * k)}px;border-radius:99px;align-self:flex-start}
    </style></head><body><div class="z"><div class="l">AUR<span>Z</span>ANE</div>
    <div class="s">Psicología, bienestar y aprendizaje</div>
    <div class="d">Tests, calculadoras, cursos y libros gratis, creados por un psicólogo clínico</div>
    <div class="u">aurzane.com</div></div></body></html>`;
    fs.writeFileSync('/tmp/marca.html', html); await pg.goto('file:///tmp/marca.html');
    await pg.waitForTimeout(800); await pg.screenshot({path: path.join(OUT, n + '.jpg'), type: 'jpeg', quality: 90});
    console.log('::notice title=Marca::' + n + ' ' + w + 'x' + h);
  }
  await b.close();
})().catch(e => { console.log('::error title=Marca::' + e.message); process.exit(1); });
