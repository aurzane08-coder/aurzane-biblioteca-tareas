// Auditoría UX/UI y accesibilidad de AURZANE: cada URL en 8 anchos.
// Mide desbordamiento horizontal, errores de JavaScript, recursos rotos, objetivos táctiles pequeños (WCAG 2.5.8),
// imágenes sin alt, campos sin etiqueta y violaciones de axe-core (WCAG 2.2 A/AA). Capturas en 375 y 1366.
const { chromium } = require('playwright');
const fs = require('fs');
const AXE = fs.readFileSync(require.resolve('axe-core/axe.min.js'), 'utf8');
const ANCHOS = (process.env.ANCHOS || '320,375,430,768,1024,1366,1440,1920').split(',');   /* «1366o» = mismo ancho con el tema oscuro del sistema */
const todas = fs.readFileSync(process.env.LISTA || 'auditoria/urls.txt', 'utf8').split('\n').map(s => s.trim()).filter(Boolean);
const PARTES = +(process.env.PARTES || 1), PARTE = +(process.env.PARTE || 0);
const urls = todas.filter((u, i) => i % PARTES === PARTE);
const SAL = process.env.SALIDA || 'auditoria/resultado';
fs.mkdirSync(SAL + '/capturas', { recursive: true });
const nombre = u => u.replace(/^https:\/\//, '').replace(/[^a-z0-9]+/gi, '_').replace(/_+$/, '');
(async () => {
  const b = await chromium.launch();
  const informe = [];
  for (const url of urls) {
    const fila = { url, anchos: {} };
    for (const clave of ANCHOS) {
      const w = parseInt(clave, 10), oscuro = /o$/.test(clave);
      const ctx = await b.newContext({ viewport: { width: w, height: w < 768 ? 800 : 900 }, deviceScaleFactor: 1, locale: 'es-ES', isMobile: w < 768, hasTouch: w < 768, colorScheme: oscuro ? 'dark' : 'light', bypassCSP: true });   /* sin CSP: axe no genera avisos que retrasarían el paso de la CSP a modo bloqueo */
      const p = await ctx.newPage();
      const errores = [], rotos = [];
      p.on('pageerror', e => errores.push(String(e.message).slice(0, 200)));
      p.on('console', m => { if (m.type() === 'error') errores.push('console: ' + m.text().slice(0, 200)); });
      p.on('response', r => { if (r.status() >= 400 && /aurzane\.com/.test(r.url())) rotos.push(r.status() + ' ' + r.url().slice(0, 160)); });
      const r = { };
      try {
        const t0 = Date.now();
        await p.goto(url, { waitUntil: 'networkidle', timeout: 45000 }).catch(async () => { await p.waitForTimeout(3000); });
        r.carga_ms = Date.now() - t0;
        await p.waitForSelector('.az-cab', { timeout: 6000 }).catch(() => { r.sin_cabecera = true; });
        await p.waitForFunction(() => document.documentElement.classList.contains('az-ds'), null, { timeout: 8000 }).catch(() => { r.sin_ds = true; });
        await p.addStyleTag({ content: '*,*::before,*::after{animation:none!important;transition:none!important}' }).catch(() => {});   /* sin animaciones a medias: si no, axe mide colores en plena transición */
        await p.waitForTimeout(800);
        /* recorre la página para que carguen las imágenes diferidas, como haría una persona */
        await p.evaluate(async () => { const h = () => document.documentElement.scrollHeight; for (let y = 0; y < h(); y += Math.round(innerHeight * .8)) { scrollTo(0, y); await new Promise(r => setTimeout(r, 120)); } scrollTo(0, 0); }).catch(() => {});
        await p.waitForTimeout(900);
        Object.assign(r, await p.evaluate(() => {
          const vw = document.documentElement.clientWidth;
          const anchos = [...document.querySelectorAll('body *')].filter(e => { const b = e.getBoundingClientRect(); const s = getComputedStyle(e); return b.right > vw + 2 && b.width > 0 && s.position !== 'fixed' && s.visibility !== 'hidden'; })
            .slice(0, 6).map(e => (e.tagName.toLowerCase() + (e.id ? '#' + e.id : '') + (e.className && typeof e.className === 'string' ? '.' + e.className.trim().split(/\s+/).slice(0, 2).join('.') : '') + (e.parentElement ? '<' + (e.parentElement.className && typeof e.parentElement.className === 'string' ? e.parentElement.className.split(' ')[0] : e.parentElement.tagName) : '')) + ' ' + Math.round(e.getBoundingClientRect().right));
          const objetivos = [...document.querySelectorAll('a[href], button, input:not([type=hidden]), select, [role=button]')].filter(e => { const b = e.getBoundingClientRect(); const s = getComputedStyle(e);
            return b.width > 0 && b.height > 0 && b.right > 0 && e.getAttribute('aria-hidden') !== 'true' && s.visibility !== 'hidden' && (b.width < 23.5 || b.height < 23.5) && !(e.tagName === 'A' && getComputedStyle(e).display === 'inline'); });
          const nav = document.querySelector('header nav, nav, .topbar, header');
          return {
            titulo: document.title, h1: [...document.querySelectorAll('h1')].map(h => h.innerText.trim().slice(0, 80)),
            desborda: document.documentElement.scrollWidth > vw + 1, scroll_w: document.documentElement.scrollWidth, culpables: anchos,
            objetivos_pequenos: objetivos.length, ejemplos_objetivos: objetivos.slice(0, 5).map(e => (e.innerText || e.getAttribute('aria-label') || e.tagName).trim().slice(0, 30)),
            img_sin_alt: [...document.images].filter(i => !i.hasAttribute('alt')).length,
            img_rotas: [...document.images].filter(i => i.complete && i.naturalWidth === 0 && i.src).map(i => i.src.slice(0, 120)).slice(0, 5),
            enlaces: document.querySelectorAll('a[href]').length, nav_enlaces: nav ? nav.querySelectorAll('a').length : 0,
            alto_pagina: document.documentElement.scrollHeight,
            fuentes: [...new Set([...document.querySelectorAll('h1,h2,h3,p,a,button')].slice(0, 300).map(e => getComputedStyle(e).fontFamily.split(',')[0].replace(/"/g, '')))].slice(0, 6),
            lang: document.documentElement.lang,
          };
        }));
        if ((process.env.CAPTURAS || '375,1366').split(',').includes(clave)) {
          await p.addScriptTag({ content: AXE });
          const ax = await p.evaluate(async () => { const res = await axe.run(document, { runOnly: { type: 'tag', values: ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'wcag22aa'] } });
            return res.violations.map(v => ({ id: v.id, impacto: v.impact, n: v.nodes.length, ejemplo: (v.nodes[0]?.target || []).join(' ').slice(0, 120) })); });
          r.axe = ax;
          await p.screenshot({ path: `${SAL}/capturas/${nombre(url)}-${clave}.jpg`, type: 'jpeg', quality: 55, fullPage: true, timeout: 30000 }).catch(() => {});
        }
      } catch (e) { r.fallo = String(e.message).slice(0, 200); }
      r.errores = [...new Set(errores)].slice(0, 6); r.rotos = [...new Set(rotos)].slice(0, 8);
      fila.anchos[clave] = r;
      await ctx.close();
    }
    informe.push(fila); console.log('auditado', url);
    fs.writeFileSync(SAL + '/informe' + (PARTES > 1 ? '-' + PARTE : '') + '.json', JSON.stringify(informe, null, 1));
  }
  await b.close();
})();
