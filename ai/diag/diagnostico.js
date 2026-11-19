// Diagnóstico puntual: abre páginas con un navegador real y muestra todos sus errores (consola, red y JavaScript).
const { chromium } = require('playwright');
const URLS = process.argv.slice(2);
(async () => {
  const b = await chromium.launch();
  for (const u of URLS) {
    const ctx = await b.newContext({ locale: 'es-ES', viewport: { width: 1280, height: 900 } }); await ctx.route(/googlesyndication\.com|doubleclick\.net|adservice\.google|googleads|fundingchoicesmessages/, r => r.fulfill({ status: 200, contentType: 'application/javascript', body: '' }));   // AdSense: un robot nunca carga anuncios (serían impresiones no válidas). Con respuesta vacía y no «abort»: abortar dejaba un error «Failed to load resource» en cada página (19/11/2026)
    const p = await ctx.newPage(); const ev = [];
    p.on('pageerror', e => ev.push('JS: ' + (e.stack || e.message || e).toString().slice(0, 400)));
    p.on('console', m => { if (m.type() === 'error' || m.type() === 'warning') ev.push(m.type() + ': ' + m.text().slice(0, 300)); });
    p.on('requestfailed', r => ev.push('RED: ' + r.url().slice(0, 150) + ' ' + (r.failure() || {}).errorText));
    p.on('response', r => { if (r.status() >= 400) ev.push('HTTP ' + r.status() + ' ' + r.url().slice(0, 150)); });
    try {
      await p.goto(u, { waitUntil: 'domcontentloaded', timeout: 45000 });
      for (let k = 0; k < 30; k++) { try { if (!/sgcaptcha/.test(p.url() + (await p.content()).slice(0, 3000))) break; } catch (e) {} await p.waitForTimeout(1000); }
      await p.waitForTimeout(3000);
      await p.waitForLoadState('networkidle', { timeout: 20000 }).catch(() => {});
      const info = await p.evaluate(() => ({ url: location.href, preg: document.querySelectorAll('.pregunta').length, guia: !!document.querySelector('.guia, .g-escena, #g-texto, [data-guia]'), botones: document.querySelectorAll('button, a.btn, .btn').length, texto: document.body.innerText.length, inicio: document.body.innerText.slice(0, 200).replace(/\s+/g, ' ') }));
      console.log('\n### ' + u + '\n' + JSON.stringify(info));
    } catch (e) { console.log('\n### ' + u + '\nNO ABRE ' + e.message.split('\n')[0]); }
    ev.forEach(x => console.log('  ' + x)); await ctx.close();
  }
  await b.close();
})();
