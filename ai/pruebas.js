// Pruebas funcionales de AURZANE con un navegador real (Playwright, gratis en GitHub Actions).
// Para cada página de ai/pruebas_paginas.json: la abre, mira que cargue sin errores de JavaScript y, según el tipo,
// la usa como una persona: responde los tests hasta ver el resultado, mueve los datos de las calculadoras y comprueba
// que el número cambia, abre los ejercicios guiados y revisa que los portales (Mi AURZANE, OVP) muestren su formulario.
// Salida: /tmp/ai/pruebas.json  →  la lee ai/manager.py (avisos, reparaciones y panel del admin).
const { chromium } = require('playwright');
const fs = require('fs');
const lista = JSON.parse(fs.readFileSync(__dirname + '/pruebas_paginas.json', 'utf8'));
const UA = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36 AurzaneQA/1.0';
const RUIDO = /Report Only|frame-ancestors|googlesyndication|adsbygoogle|doubleclick|gstatic|google-analytics|googletagmanager|translate\.goog|ResizeObserver loop|favicon|net::ERR_BLOCKED/i;

async function probar(browser, p) {
  const ctx = await browser.newContext({ userAgent: UA, viewport: { width: 1280, height: 900 }, locale: 'es-ES' });
  const page = await ctx.newPage();
  const errores = [];
  page.on('pageerror', e => { if (!RUIDO.test(String(e))) errores.push(String(e.message || e).slice(0, 200)); });
  page.on('console', m => { if (m.type() === 'error' && !RUIDO.test(m.text())) errores.push(m.text().slice(0, 200)); });
  const t0 = Date.now(); let ok = true, detalle = '';
  try {
    const r = await page.goto(p.url, { waitUntil: 'domcontentloaded', timeout: 45000 });
    // SiteGround a veces pide una verificación anti-robots: el navegador la resuelve solo, se espera a que vuelva la página
    let bloqueado = true;
    for (let k = 0; k < 25; k++) {   // espera a que el navegador pase la verificación de SiteGround (hasta ~25 s)
      try { const h = await page.content(); if (!/sgcaptcha/.test(page.url() + h.slice(0, 3000))) { bloqueado = false; break; } } catch (e) { }
      await page.waitForTimeout(1000);
    }
    if (bloqueado) { await ctx.close(); return { url: p.url, tipo: p.tipo, ok: null, detalle: 'SiteGround pidió verificación anti-robots y no se pudo pasar', ms: Date.now() - t0, errores: [] }; }
    await page.waitForLoadState('networkidle', { timeout: 20000 }).catch(() => {});
    const st = r ? r.status() : 0;
    if (st >= 400) { ok = false; detalle = 'La página devuelve ' + st; }
    else if (p.tipo === 'test') {
      const n = await page.$$eval('.pregunta', qs => qs.length);
      if (!n) { ok = false; detalle = 'No aparecen las preguntas del test'; }
      else {
        const preguntas = await page.$$('.pregunta');
        for (const q of preguntas) { const ops = await q.$$('.op'); if (ops.length) await ops[Math.floor(ops.length / 2)].click(); }
        await page.waitForTimeout(800);
        const btn = await page.$('#calcular'); if (btn && !(await page.evaluate(() => document.body.classList.contains('hecho')))) await btn.click().catch(() => {});
        await page.waitForTimeout(800);
        const res = await page.evaluate(() => ({ hecho: document.body.classList.contains('hecho'), r: window.__res || null, nivel: (document.getElementById('nivel') || {}).innerText || '' }));
        if (!res.hecho || !(res.r || res.nivel.trim())) { ok = false; detalle = `Respondí las ${n} preguntas pero no salió el resultado`; }
        else detalle = `Respondí ${n} preguntas: ` + (res.r ? `resultado ${res.r.valor} ${res.r.unidad || ''} (${(res.nivel || res.r.nivel || '').trim()})` : res.nivel.trim());
      }
    } else if (p.tipo === 'calculadora') {
      const leer = () => page.evaluate(() => { const v = document.getElementById('valor'); return v ? v.innerText.trim() : ''; });
      if (!(await page.$('#valor'))) {   // calculadoras con otro formato: basta con que cargue con sus campos y sin errores
        const n = await page.$$eval('input, select', x => x.length); if (!n) { ok = false; detalle = 'La calculadora no muestra sus campos'; } else detalle = `Carga bien (${n} campos)`;
        await ctx.close(); return { url: p.url, tipo: p.tipo, ok: ok && !errores.length, detalle: errores.length ? detalle + ' · error de JavaScript: ' + errores[0] : detalle, ms: Date.now() - t0, errores: errores.slice(0, 3) };
      }
      const antes = await leer();
      const campos = await page.$$('input[type=number]:not([disabled]), input[inputmode=decimal]:not([disabled])');
      if (campos.length) { const c = campos[0]; const v = parseFloat(await c.inputValue()) || 10; await c.fill(String(Math.round(v * 1.2 + 1))); await c.dispatchEvent('input'); await c.dispatchEvent('change'); }
      const btn = await page.$('#calcular'); if (btn) await btn.click().catch(() => {});
      await page.waitForTimeout(700);
      const despues = await leer();
      if (!despues || /NaN|undefined|Infinity/.test(despues)) { ok = false; detalle = `El resultado sale vacío o mal («${despues}»)`; }
      else detalle = `Cambié un dato: ${antes || '–'} → ${despues}`;
    } else if (p.tipo === 'personalidad') {
      await page.click('button.version[data-version="20"]');
      for (let k = 0; k < 15; k++) {
        if (await page.evaluate(() => { const r = document.getElementById('resultados'); return r && !r.hidden; })) break;
        await page.evaluate(() => { document.querySelectorAll('#preguntas fieldset.preg').forEach((f, j) => { const ops = f.querySelectorAll('input[type=radio]'); const o = ops[(j % 3) + 1] || ops[0]; if (o && !f.querySelector('input:checked')) o.click(); }); });
        await page.click('#btnSiguiente'); await page.waitForTimeout(700);
      }
      const r = await page.evaluate(() => ({ vis: !document.getElementById('resultados').hidden, nombre: (document.getElementById('resNombre') || {}).innerText || '' }));
      if (!r.vis || !r.nombre.trim()) { ok = false; detalle = 'Respondí las 20 preguntas pero no salió el perfil'; } else detalle = `Hice la versión exprés: perfil «${r.nombre.trim()}»`;
    } else if (p.tipo === 'ejercicio') {
      const tiene = await page.evaluate(() => !!document.querySelector('.guia, .g-escena, #g-texto, [data-guia]'));
      if (!tiene) { ok = false; detalle = 'No aparece la guía del ejercicio'; } else detalle = 'La guía del ejercicio carga';
    } else if (p.tipo === 'portal') {
      const f = await page.evaluate(() => ({ campos: document.querySelectorAll('input[type=email], input[type=password], input[type=text]').length, botones: document.querySelectorAll('button, a.btn, .btn').length, texto: document.body.innerText.length }));
      if (f.texto < 80 || !f.botones) { ok = false; detalle = 'El portal carga vacío o sin botones'; } else detalle = `Carga bien (${f.campos} campos, ${f.botones} botones)`;
    } else {
      const txt = await page.evaluate(() => document.body.innerText.length);
      if (txt < 200) { ok = false; detalle = 'La página carga casi vacía'; } else detalle = 'Carga bien';
    }
  } catch (e) { ok = false; detalle = 'No se pudo abrir: ' + String(e.message || e).split('\n')[0].slice(0, 150); }
  if (ok && errores.length) { ok = false; detalle += ` · ${errores.length} error(es) de JavaScript: ${errores[0]}`; }
  await ctx.close();
  return { url: p.url, tipo: p.tipo, ok, detalle, ms: Date.now() - t0, errores: errores.slice(0, 3) };
}

(async () => {
  const browser = await chromium.launch();
  const out = [];
  for (const p of lista) { const r = await probar(browser, p); out.push(r); console.log((r.ok ? 'OK   ' : r.ok === null ? 'BLOQ ' : 'FALLO') + ' ' + p.url + ' · ' + r.detalle); }
  await browser.close();
  fs.mkdirSync('/tmp/ai', { recursive: true });
  fs.writeFileSync('/tmp/ai/pruebas.json', JSON.stringify({ fecha: new Date().toISOString(), resultados: out }));
  console.log(`::notice title=Pruebas::${out.filter(x => x.ok).length} de ${out.length} páginas funcionan, ${out.filter(x => x.ok === null).length} sin poder comprobar por el filtro anti-robots`);
})();
