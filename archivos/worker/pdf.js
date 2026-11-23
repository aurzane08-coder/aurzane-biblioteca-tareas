// AURZANE · intermediario de PDF (Cloudflare Worker, plan gratuito)
// Entrega a aurzane.com los PDF guardados en Internet Archive con CORS, para que el lector propio de la web
// (pdf.js) los abra dentro de la página, también en el móvil. Guarda copia en la caché de Cloudflare.
//   /bib/<archivo>.pdf  → archive.org/download/aurzane-bib-<archivo>/<archivo>.pdf
//   /rec/<archivo>.pdf  → archive.org/download/aurzane-rec-<archivo>/<archivo>.pdf
const ORIGENES = ['https://aurzane.com', 'https://www.aurzane.com'];
const CORS = {
  'Access-Control-Allow-Methods': 'GET, HEAD, OPTIONS',
  'Access-Control-Allow-Headers': 'Range',
  'Access-Control-Expose-Headers': 'Accept-Ranges, Content-Range, Content-Length',
  'Vary': 'Origin',
};
export default {
  async fetch(req, env, ctx) {
    const u = new URL(req.url), o = req.headers.get('Origin');
    const cab = new Headers(CORS);
    if (o && (ORIGENES.includes(o) || /^https:\/\/[a-z]+\.aurzane\.com$/.test(o))) cab.set('Access-Control-Allow-Origin', o);
    if (req.method === 'OPTIONS') return new Response(null, { status: 204, headers: cab });
    if (req.method !== 'GET' && req.method !== 'HEAD') return new Response('Método no permitido', { status: 405, headers: cab });
    const m = u.pathname.match(/^\/(bib|rec)\/([a-z0-9._-]+\.pdf)$/i);
    if (!m) return new Response('No encontrado', { status: 404, headers: cab });
    const id = `aurzane-${m[1].toLowerCase()}-${m[2].replace(/\.pdf$/i, '')}`;
    const destino = `https://archive.org/download/${id}/${m[2]}`;
    const pide = new Headers();
    const rango = req.headers.get('Range'); if (rango) pide.set('Range', rango);
    const r = await fetch(destino, { method: req.method, headers: pide, cf: { cacheEverything: true, cacheTtl: 2592000 } });
    const h = new Headers(r.headers);
    for (const [k, v] of cab) h.set(k, v);
    for (const k of ['Content-Security-Policy-Report-Only', 'Set-Cookie', 'Strict-Transport-Security']) h.delete(k);
    h.set('Cache-Control', 'public, max-age=2592000');
    h.set('Content-Type', 'application/pdf');
    return new Response(r.body, { status: r.status, headers: h });
  },
};
