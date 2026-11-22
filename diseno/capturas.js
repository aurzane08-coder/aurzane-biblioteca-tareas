// Capturas reales de AURZANE para revisar el diseño (navegador real, con imágenes): escritorio y móvil, tema claro y oscuro.
// Si existe diseno/borrador/<dominio>/<ruta>, se sirve ese archivo en lugar del publicado: así se ve un cambio ANTES de desplegarlo.
// Uso: node diseno/capturas.js diseno/urls.txt salida/   (variables: TEMAS="claro oscuro", VISTAS="escritorio movil", ALTO=5200)
const { chromium } = require('playwright'); const fs = require('fs'), path = require('path');
const [lista, salida] = process.argv.slice(2); fs.mkdirSync(salida, { recursive: true });
const URLS = fs.readFileSync(lista, 'utf8').split('\n').map(s => s.trim()).filter(s => s && !s.startsWith('#'));
const TEMAS = (process.env.TEMAS || 'claro oscuro').split(/\s+/), VISTAS = (process.env.VISTAS || 'escritorio movil').split(/\s+/), ALTO = +(process.env.ALTO || 5200);
// ojo: Playwright solo aplica el tamaño dentro de «viewport»; fuera de él se ignora y todo sale a 1280 px
const VP = { escritorio: { viewport: { width: 1440, height: 900 } }, movil: { viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true, deviceScaleFactor: 1 } };
const BORR = path.join(__dirname, 'borrador'); const LOCAL = process.env.LOCAL ? path.resolve(process.env.LOCAL) : null; /* LOCAL=traer/servidor: sin red */ const V4 = process.env.V4 === '1'; const PAL = require('./paleta-v4.js');
const nombre = u => u.replace(/^https?:\/\//, '').replace(/[^a-z0-9]+/gi, '_').replace(/_+$/, '').slice(0, 90);
(async () => {
  const b = await chromium.launch(); const informe = [];
  for (const u of URLS) for (const v of VISTAS) for (const t of TEMAS) {
    const ctx = await b.newContext({ locale: 'es-ES', colorScheme: t === 'oscuro' ? 'dark' : 'light', ...VP[v] });
    await ctx.addInitScript(t => { try { document.cookie = 'az_tema=' + t + ';path=/'; localStorage.setItem('aurzane-tema', t); } catch (e) {} }, t);   // la cookie común del tema (v4)
    await ctx.route(/googlesyndication\.com|doubleclick\.net|adservice\.google|googleads|fundingchoicesmessages/, r => r.fulfill({ status: 200, contentType: 'application/javascript', body: '' }));
    await ctx.route(/^https:\/\/([a-z]+\.)?aurzane\.com\//, async r => {
      const x = new URL(r.request().url()); let f = path.join(BORR, x.hostname, decodeURIComponent(x.pathname));
      if (f.endsWith('/')) f += 'index.html';
      const ext = path.extname(f).slice(1) || (r.request().resourceType() === 'document' ? 'html' : '');
      const TIPO = { html: 'text/html; charset=utf-8', js: 'application/javascript', css: 'text/css', json: 'application/json', svg: 'image/svg+xml', woff2: 'font/woff2' };
      const texto = ['html', 'js', 'css'].includes(ext) || r.request().resourceType() === 'document';
      let cuerpo = null, tipo = TIPO[ext] || 'application/octet-stream', estado = 200, cab = {};
      if (fs.existsSync(f) && fs.statSync(f).isFile()) cuerpo = fs.readFileSync(f);
      else if (LOCAL) { let g = path.join(LOCAL, x.hostname, decodeURIComponent(x.pathname)); if (g.endsWith('/') || (fs.existsSync(g) && fs.statSync(g).isDirectory())) g = path.join(g, 'index.html');
        if (fs.existsSync(g) && fs.statSync(g).isFile()) cuerpo = fs.readFileSync(g); else return r.fulfill({ status: 404, body: '' }); }
      else if (V4 && texto) { try { const res = await r.fetch(); estado = res.status(); cab = res.headers(); cuerpo = await res.body(); tipo = cab['content-type'] || tipo; } catch (e) { return r.continue(); } }
      if (cuerpo === null) return r.continue();
      if (V4 && texto && estado < 300) {
        let t = cuerpo.toString('utf8'); t = PAL.transformar(t).out;
        if (x.pathname === '/aurzane-ds.css') t += '\n' + fs.readFileSync(path.join(__dirname, 'v4.css'), 'utf8');
        cuerpo = Buffer.from(t, 'utf8');
      }
      return r.fulfill({ status: estado, contentType: tipo, body: cuerpo, headers: { 'access-control-allow-origin': '*' } });
    });
    if (LOCAL) await ctx.route(u2 => !/aurzane\.com/.test(u2.hostname), r => r.abort());
    const p = await ctx.newPage(); const err = [];
    p.on('pageerror', e => err.push('JS ' + (e.message || e).toString().slice(0, 160)));
    p.on('response', r => { if (r.status() >= 400 && !/favicon/.test(r.url())) err.push(r.status() + ' ' + r.url().slice(0, 120)); });
    const id = nombre(u) + '__' + v + '_' + t;
    try {
      await p.goto(u, { waitUntil: 'domcontentloaded', timeout: 60000 });
      for (let k = 0; k < 40; k++) { try { if (!/sgcaptcha/.test(p.url() + (await p.content()).slice(0, 3000))) break; } catch (e) {} await p.waitForTimeout(1000); }
      await p.waitForLoadState('networkidle', { timeout: LOCAL ? 4000 : 20000 }).catch(() => {});
      await p.evaluate(async A => { for (let y = 0; y < Math.min(document.body.scrollHeight, A); y += 600) { scrollTo(0, y); await new Promise(r => setTimeout(r, 120)); } scrollTo(0, 0); }, ALTO);
      await p.waitForTimeout(1800);
      const m = await p.evaluate(() => { const W = document.documentElement.clientWidth;
        const fuera = [...document.querySelectorAll('body *')].filter(e => { const r = e.getBoundingClientRect(); return r.width && r.right > W + 2 && getComputedStyle(e).position !== 'fixed'; }).slice(0, 5).map(e => e.tagName.toLowerCase() + (e.className && typeof e.className == 'string' ? '.' + e.className.split(' ')[0] : ''));
        const rotas = [...document.images].filter(i => i.complete && i.naturalWidth === 0 && i.getBoundingClientRect().width > 0).map(i => i.src.slice(0, 100)).slice(0, 5);
        // Contraste real de cada texto visible con su fondo (WCAG): se sube por los padres hasta un fondo opaco.
        // Si por medio hay una foto o un degradado, se marca como «sobre imagen» para revisarlo a ojo en la captura.
        const rgb = c => { const m = c.match(/rgba?\(([^)]+)\)/); if (!m) return null; const v = m[1].split(/[ ,\/]+/).filter(Boolean).map(Number); return [v[0], v[1], v[2], v.length > 3 ? v[3] : 1]; };
        const lum = ([r, g, b]) => { const f = x => (x /= 255) <= .03928 ? x / 12.92 : ((x + .055) / 1.055) ** 2.4; return .2126 * f(r) + .7152 * f(g) + .0722 * f(b); };
        const mezcla = (a, b) => [0, 1, 2].map(i => a[i] * a[3] + b[i] * (1 - a[3])).concat(1);
        const bajos = [], sobreImg = []; let revisados = 0;
        for (const e of document.querySelectorAll('body *')) {
          if (revisados > 2500) break;
          const tx = [...e.childNodes].some(n => n.nodeType === 3 && /\p{L}{2,}|\d/u.test(n.textContent)); if (!tx) continue;   // los emojis solos no cuentan
          const r = e.getBoundingClientRect(); if (!r.width || !r.height) continue;
          const cs = getComputedStyle(e); if (cs.visibility === 'hidden' || +cs.opacity === 0) continue;
          revisados++;
          let col = rgb(cs.color); if (!col) continue; let fondo = null, img = false, capas = [];
          for (let x = e; x; x = x.parentElement) { const s = getComputedStyle(x);
            if (s.backgroundImage && s.backgroundImage !== 'none') { img = true; break; }
            if (x.tagName === 'IMG' || x.querySelector(':scope > img, :scope > picture')) { }
            const b = rgb(s.backgroundColor); if (b && b[3] > 0) { capas.push(b); if (b[3] >= .99) { fondo = b; break; } } }
          if (img) { sobreImg.push(e.tagName.toLowerCase() + ': ' + e.textContent.trim().slice(0, 40)); continue; }
          fondo = fondo || [255, 255, 255, 1]; for (let i = capas.length - 2; i >= 0; i--) fondo = mezcla(capas[i], fondo);
          if (col[3] < 1) col = mezcla(col, fondo);
          const L1 = lum(col), L2 = lum(fondo), ratio = (Math.max(L1, L2) + .05) / (Math.min(L1, L2) + .05);
          const grande = parseFloat(cs.fontSize) >= 24 || (parseFloat(cs.fontSize) >= 18.6 && +cs.fontWeight >= 700);
          if (ratio < (grande ? 3 : 4.5)) bajos.push(ratio.toFixed(2) + ' ' + e.tagName.toLowerCase() + (e.className && typeof e.className == 'string' ? '.' + e.className.split(' ')[0] : '') + ': ' + e.textContent.trim().slice(0, 50));
        }
        return { alto: document.body.scrollHeight, ancho: document.documentElement.scrollWidth, W, fuera, rotas, imgs: document.images.length,
          tema: document.documentElement.getAttribute('data-tema') || 'claro', fondo: getComputedStyle(document.body).backgroundColor,
          contraste: { revisados, bajos: bajos.length, ej: bajos.slice(0, 15), sobreImagen: sobreImg.length, ejImg: sobreImg.slice(0, 8) } }; });
      // la ventana NO se estira al alto de la página: con 100vh/5vh el diseño se deformaría (falsos huecos enormes)
      const H = Math.min(m.alto, ALTO);
      await p.screenshot({ path: path.join(salida, id + '.jpg'), type: 'jpeg', quality: 62, fullPage: true, clip: { x: 0, y: 0, width: VP[v].viewport.width, height: H } });
      informe.push({ id, u, v, t, ...m, err: err.slice(0, 8) });
    } catch (e) { informe.push({ id, u, v, t, fallo: e.message.split('\n')[0] }); }
    await ctx.close();
  }
  fs.writeFileSync(path.join(salida, 'informe.json'), JSON.stringify(informe, null, 1)); await b.close();
})();
