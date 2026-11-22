// AURZANE · Paleta v4 «Hybrid Premium Editorial» (guía de dirección de arte del 19/11/2026).
// Convierte los colores escritos a mano en las páginas (azul noche, dorado, crema) a la nueva identidad
// (verde bosque #183D32, verde profundo #12251F, marfil #F6F5F0, arena #E9E4DB, carbón #252724, champán #C7B99B)
// conservando la luminosidad de cada color: lo que era fondo oscuro sigue oscuro y lo claro sigue claro,
// así nunca queda texto claro sobre fondo claro. Los colores propios de los cinco mundos (punto de color) no se tocan.
// Es idempotente: un color ya convertido no vuelve a cambiar.
'use strict';
const lin = c => (c /= 255) <= 0.04045 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4;
const gam = c => 255 * (c <= 0.0031308 ? 12.92 * c : 1.055 * c ** (1 / 2.4) - 0.055);
function aOk(r, g, b) {
  r = lin(r); g = lin(g); b = lin(b);
  const l = Math.cbrt(0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b), m = Math.cbrt(0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b), s = Math.cbrt(0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b);
  const L = 0.2104542553 * l + 0.793617785 * m - 0.0040720468 * s, A = 1.9779984951 * l - 2.428592205 * m + 0.4505937099 * s, B = 0.0259040371 * l + 0.7827717662 * m - 0.808675766 * s;
  return [L, Math.hypot(A, B), (Math.atan2(B, A) * 180 / Math.PI + 360) % 360];
}
function deOk(L, C, H) {
  const A = C * Math.cos(H * Math.PI / 180), B = C * Math.sin(H * Math.PI / 180);
  const l = (L + 0.3963377774 * A + 0.2158037573 * B) ** 3, m = (L - 0.1055613458 * A - 0.0638541728 * B) ** 3, s = (L - 0.0894841775 * A - 1.291485548 * B) ** 3;
  return [4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s, -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s, -0.0041960863 * l - 0.7034186147 * m + 1.707614701 * s]
    .map(v => Math.max(0, Math.min(255, Math.round(gam(Math.max(0, Math.min(1, v)))))));
}
// Colores fijos de la guía: si el resultado cae cerca de uno de ellos, se usa el exacto.
const GUIA = { '#12251F': 1, '#183D32': 1, '#F6F5F0': 1, '#E9E4DB': 1, '#252724': 1, '#C7B99B': 1, '#DCE5DF': 1, '#85867F': 1 };
const GUIA_OK = Object.keys(GUIA).map(h => [h, aOk(...hexA(h))]);
function hexA(h) { h = h.replace('#', ''); if (h.length === 3) h = h.split('').map(x => x + x).join(''); return [0, 2, 4].map(i => parseInt(h.slice(i, i + 2), 16)); }
const aHex = rgb => '#' + rgb.map(v => v.toString(16).padStart(2, '0')).join('').toUpperCase();
function cerca(L, C, H) {
  for (const [h, [l, c, hh]] of GUIA_OK) { const dh = Math.min(Math.abs(H - hh), 360 - Math.abs(H - hh)) * Math.PI / 180;
    if (Math.abs(L - l) < 0.008 && Math.hypot(C - c, 2 * Math.sqrt(C * c) * Math.sin(dh / 2)) < 0.012) return hexA(h); }
  return null;
}
const VERDE = 171, NEUTRO = 120, CHAMPAN = 85, MARFIL = 95;
// Devuelve [r,g,b] nuevo o null si el color no cambia
function convertir(r, g, b) {
  const [L, C, H] = aOk(r, g, b); let n = null;
  if (C < 0.012 && L > 0.04 && L < 0.97 && (H > 200 && H < 330)) n = [L, Math.min(C, 0.008), NEUTRO];             // grises azulados casi neutros
  else if (H >= 215 && H <= 320 && L < 0.43 && C >= 0.012) { const L2 = L < 0.3 ? 0.21 + Math.max(0, L - 0.14) * 0.6 : L; n = [L2, Math.min(C * 0.5, 0.03 + 0.1 * Math.max(0, L2 - 0.24)), VERDE]; }             // azul noche, índigo y violeta oscuros: verde profundo
  else if (H >= 215 && H <= 320 && C >= 0.012 && C < 0.07) n = [L, Math.min(C * 0.3, 0.014), L > 0.8 ? VERDE : NEUTRO]; // grises azulados y lilas suaves: salvia y mineral
  else if (H >= 68 && H <= 102 && C >= 0.07) n = [L > 0.62 && L < 0.79 ? 0.79 : L, L > 0.82 ? 0.035 : 0.045, CHAMPAN];                         // dorados y ámbar: champán
  else if (H >= 45 && H <= 105 && L > 0.86 && C >= 0.009 && C < 0.07) n = [L, Math.min(C * 0.45, 0.011), MARFIL];   // cremas y beige: marfil y arena
  else if (H >= 25 && H <= 105 && L < 0.62 && C >= 0.009 && C < 0.06) n = [L, Math.min(C * 0.3, 0.008), 130];      // marrones (moca, tinta cálida): carbón
  if (!n) return null;
  const g2 = cerca(...n) || deOk(...n);
  return (g2[0] === r && g2[1] === g && g2[2] === b) ? null : g2;
}
const RE = /#([0-9a-fA-F]{6}|[0-9a-fA-F]{3})(?![0-9a-zA-Z_-])|rgba?\(\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})\s*([,/][^)]*)?\)/g;
function transformar(txt) {
  let n = 0;
  const out = txt.replace(RE, (m, hex, r, g, b, resto, pos, todo) => {
    if (hex) {
      const prev = todo.slice(Math.max(0, pos - 12), pos);
      if (/&$|&#$|[\w-]$/.test(prev) || /url\([^)]*$/.test(todo.slice(Math.max(0, pos - 200), pos))) return m;   // entidades, anclas, ids o rutas
      if (hex.length === 3 && !/[:\s,(]$|^$/.test(prev.slice(-1)) && !/[:\s(,'"]$/.test(prev)) return m;
      const c = convertir(...hexA(hex)); if (!c) return m; n++; return aHex(c);
    }
    const c = convertir(+r, +g, +b); if (!c) return m; n++;
    return (m.startsWith('rgba') ? 'rgba(' : 'rgb(') + c.join(',') + (resto || '') + ')';
  });
  // Letras v4: los mismos nombres de familia que ya usan las páginas, pero con los archivos nuevos (Instrument Serif y Manrope).
  // Se cambia la URL del archivo, no el nombre, así no hay que tocar ningún selector y la caché vieja no interfiere.
  const LETRAS = { 'bodoni-moda-latin-opsz-normal': 'instrument-serif-latin-400-normal', 'bodoni-moda-latin-ext-opsz-normal': 'instrument-serif-latin-ext-400-normal',
    'bodoni-moda-latin-opsz-italic': 'instrument-serif-latin-400-italic', 'bodoni-moda-latin-ext-opsz-italic': 'instrument-serif-latin-ext-400-italic',
    'instrument-sans-latin-wght-normal': 'manrope-latin-wght-normal', 'instrument-sans-latin-ext-wght-normal': 'manrope-latin-ext-wght-normal',
    'instrument-sans-latin-wght-italic': 'manrope-latin-wght-normal', 'instrument-sans-latin-ext-wght-italic': 'manrope-latin-ext-wght-normal' };
  const out2 = out.replace(/fuentes\/(bodoni-moda|instrument-sans)-latin(-ext)?-(opsz|wght)-(normal|italic)\.woff2/g, m => { const k = m.slice(8, -6); n++; return 'fuentes/' + (LETRAS[k] || k) + '.woff2'; });
  return { out: out2, n };
}
module.exports = { transformar, convertir, hexA, aHex, aOk };
if (require.main === module) {   // prueba: node paleta-v4.js #0B1030 #C9A24B ...
  for (const h of process.argv.slice(2)) { const c = convertir(...hexA(h)); console.log(h, '->', c ? aHex(c) : '(igual)', aOk(...hexA(h)).map(x => +x.toFixed(3)).join(' ')); }
}
