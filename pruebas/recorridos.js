// Prueba diaria de los recorridos importantes de AURZANE, con un navegador real (16/11/2026).
// Si algo falla, el flujo termina en error y GitHub avisa por correo. Solo lee: no crea cuentas ni envía formularios
// (la pregunta a la IA es la única petición que escribe algo y no guarda nada).
const { chromium } = require('playwright');
const fallos = [], bien = [], avisos = [];
let reto = 0;   // páginas en las que SiteGround mostró su desafío anti-robots (HTTP 202) en vez de la web
const ok = (n, c, det = '') => (c ? bien : fallos).push(n + (det ? ' · ' + det : ''));

(async () => {
  const b = await chromium.launch();
  const ctx = await b.newContext({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true, userAgent: 'Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Mobile Safari/537.36 AURZANE-prueba' });
  await ctx.route(/googlesyndication\.com|doubleclick\.net|adservice\.google|googleads|fundingchoicesmessages/, r => r.abort());   // AdSense: un robot nunca carga anuncios (serían impresiones no válidas)
  const pagina = async (url) => {
    const p = await ctx.newPage(), errs = [];
    p.on('pageerror', e => errs.push(e.message.slice(0, 120)));
    p.on('console', m => { if (m.type() === 'error' && /Refused to display|X-Frame-Options|frame-ancestors/.test(m.text())) errs.push(m.text().slice(0, 120)); });
    let r = null; try { r = await p.goto(url, { waitUntil: 'load', timeout: 45000 }); } catch (e) { errs.push('no carga: ' + e.message.slice(0, 80)); }
    if (r && r.status() === 202) { reto++; avisos.push('Desafío anti-robots de SiteGround en ' + url); }
    await p.waitForTimeout(2500);
    return { p, r, errs };
  };

  // 1. Portadas: cargan, tienen la cabecera común y no hay errores de JavaScript
  for (const u of ['https://aurzane.com/', 'https://mind.aurzane.com/', 'https://nexus.aurzane.com/', 'https://live.aurzane.com/', 'https://learn.aurzane.com/', 'https://build.aurzane.com/', 'https://ovp.aurzane.com/', 'https://aurzane.com/biblioteca/']) {
    const { p, r, errs } = await pagina(u);
    const cab = await p.$('.az-cab').catch(() => null);
    if (r && r.status() === 202) { await p.close(); continue; }
    const reto = await p.evaluate(() => document.body && document.body.innerText.length < 200).catch(() => true);
    ok('Portada ' + u, r && r.status() === 200 && cab && !reto && !errs.length, [r && r.status(), cab ? '' : 'sin cabecera', reto ? 'página vacía o desafío anti-robots' : '', errs.join(' | ')].filter(Boolean).join(' '));
    await p.close();
  }

  // 2. Test de ansiedad: responder, ver el resultado, botón «Ver resultado» y pregunta a la IA
  {
    const { p, r: r0, errs } = await pagina('https://mind.aurzane.com/test-de-ansiedad/');
    if (r0 && r0.status() === 202) { await p.close(); } else
    try {
      const n = await p.evaluate(() => { const gs = document.querySelectorAll('.opciones'); gs.forEach(g => { const o = g.querySelector('.op[data-v="1"]') || g.querySelector('.op'); if (o) o.click(); }); document.getElementById('calcular').click(); return gs.length; });
      const grupos = { length: n };
      await p.waitForFunction(() => document.body.classList.contains('hecho'), null, { timeout: 8000 });
      ok('Test: resultado', true, grupos.length + ' preguntas');
      await p.evaluate(() => window.scrollTo(0, 0)); await p.waitForTimeout(300);
      await p.evaluate(() => window.scrollTo(0, 600)); await p.waitForTimeout(500);
      const barra = await p.$('#movilBarra');
      if (barra) {
        await p.evaluate(() => { const r = document.getElementById('resultado'); window.scrollTo(0, r.getBoundingClientRect().bottom + window.scrollY + 400); });
        await p.waitForTimeout(600);
        const vis = await p.evaluate(() => document.getElementById('movilBarra').classList.contains('ver'));
        if (vis) { await p.waitForTimeout(400); await p.tap('#movilBarra a[href="#resultado"]').catch(() => p.evaluate(() => document.querySelector('#movilBarra a[href="#resultado"]').click())); await p.waitForTimeout(2500); }
        const enRes = await p.evaluate(() => { const r = document.getElementById('resultado').getBoundingClientRect(); return r.top < innerHeight && r.bottom > 0; });
        ok('Test: botón «Ver resultado» lleva al resultado', enRes);
      }
      await p.waitForSelector('#azAsis', { timeout: 6000 }).catch(() => {});
      ok('Test: aparece la IA de resultados', !!(await p.$('#azAsis')));
      const ia = await p.evaluate(async () => { try { const r = await fetch('/ai/asistente.php', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ test: 'Test de ansiedad GAD-7', resultado: '6 puntos, nivel: leve', pregunta: '¿Qué significa mi resultado?' }) }); const j = await r.json(); return r.status + ' ' + (j.respuesta ? 'ok' : (j.error || 'sin respuesta')); } catch (e) { return 'error ' + e.message; } });
      ok('Test: la IA responde', / ok$/.test(ia), ia);
    } catch (e) { ok('Test de ansiedad', false, e.message.slice(0, 120)); }
    if (!(r0 && r0.status() === 202)) { if (errs.length) ok('Test: sin errores de JavaScript', false, errs.join(' | ')); await p.close(); }
  }

  // 3. Página de error propia y mapas del sitio
  {
    const { p, r } = await pagina('https://mind.aurzane.com/esta-pagina-no-existe-prueba');
    ok('404 propia', r && r.status() === 404 && /no existe/i.test(await p.title().catch(() => '') + await p.textContent('h1').catch(() => '')), r && String(r.status()));
    for (const s of ['https://aurzane.com/sitemap-paginas.xml', 'https://nexus.aurzane.com/sitemap-universidades.xml', 'https://mind.aurzane.com/sitemap-paginas.xml', 'https://aurzane.com/robots.txt']) {
      const x = await p.request.get(s).then(async r => r.status() + ' ' + /<loc>|Sitemap:/.test(await r.text())).catch(() => 'error');
      ok('Mapa ' + s, x === '200 true', x);
    }
    await p.close();
  }

  // 4. Imágenes en AVIF para quien las acepta
  {
    const p = await ctx.newPage();
    const r = await p.request.get('https://aurzane.com/biblioteca/og.jpg', { headers: { Accept: 'image/avif,image/webp,*/*' } }).catch(() => null);
    ok('AVIF servido', r && /avif/.test(r.headers()['content-type'] || ''), r ? r.headers()['content-type'] : 'sin respuesta');
    await p.close();
  }

  await b.close();
  const res = '## Recorridos de AURZANE\n\n' + (avisos.length ? '### Avisos (no son fallos de la web)\n' + avisos.map(x => '- ' + x).join('\n') + '\n\n' : '') + (fallos.length ? '### Fallos\n' + fallos.map(x => '- ' + x).join('\n') + '\n\n' : '') + '### Bien\n' + bien.map(x => '- ' + x).join('\n') + '\n';
  console.log(res);
  if (process.env.GITHUB_STEP_SUMMARY) require('fs').appendFileSync(process.env.GITHUB_STEP_SUMMARY, res);
  require('fs').writeFileSync('pruebas/resultado.json', JSON.stringify({ fecha: new Date().toISOString(), fallos, avisos, bien }, null, 1));
  process.exit(fallos.length ? 1 : 0);
})();
