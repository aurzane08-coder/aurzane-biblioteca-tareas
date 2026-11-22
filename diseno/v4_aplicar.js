// Aplica el rediseño v4 a una carpeta con la misma estructura que el servidor (<dominio>/<ruta>):
//   colores a la nueva paleta, letras nuevas, tema claro por defecto, marca de familia de plantilla,
//   y añade v4.css al final de aurzane-ds.css. Solo reescribe los archivos que cambian. Es idempotente.
// Uso: node diseno/v4_aplicar.js <carpeta> [--lista cambiados.txt]
'use strict';
const fs = require('fs'), path = require('path'), P = require('./paleta-v4.js');
const raiz = path.resolve(process.argv[2] || '.');
const iL = process.argv.indexOf('--lista'), lista = iL > 0 ? process.argv[iL + 1] : null;
const V4CSS = fs.readFileSync(path.join(__dirname, 'v4.css'), 'utf8');
const TEMA = fs.readFileSync(path.join(__dirname, 'v4_tema.js'), 'utf8');
const BOTON = "    // v4: todas las páginas tienen claro y oscuro; si la página no trae su propio botón, se crea uno con el tema común\n    if (!tema && window.AurzaneTema) { tema = d.createElement('button'); tema.type = 'button'; tema.id = 'btnTema';\n      tema.addEventListener('click', function () { window.AurzaneTema.alternar(); }); }\n";
// Foto real (Unsplash, las mismas que ya usa AURZANE en tests y portada) para los artículos que no traen imagen propia,
// elegida por el tema del artículo; si no encaja ninguno, la foto de su mundo.
const FOTO_V4 = "    /* FOTO_V4 (rediseño v4, 22/11/2026): sin imagen propia, foto real según el tema; nunca una imagen creada */\n" +
  "    if (!img) { var tx = ((a.categoria || '') + ' ' + (a.titulo || '')).toLowerCase(), F = [[/ansiedad|p[áa]nico|preocupa/, '1505142468610-359e7d316be0'], [/estr[ée]s|burnout|agotamiento/, '1541199249251-f713e6145474'], [/depresi|[áa]nimo|triste/, '1529665253569-6d01c0eaf7b6'], [/sue[ñn]o|insomnio|dormir|descans/, '1541781774459-bb2af2f05b55'], [/h[áa]bito|aliment|nutric|ejercicio|deporte/, '1490645935967-10de6ba17061'], [/autoestima|identidad|personalidad/, '1517841905240-472988babdf9'], [/pareja|relaci|amistad|famil|v[íi]nculo|cuidado/, '1544027993-37dbfe43562a'], [/soledad|aislamiento/, '1512438248247-f0f2a5a8b7f0'], [/duelo|p[ée]rdida|muerte|resilien|trauma/, '1466692476868-aef1dfb1e735'], [/bienestar|felicidad|satisfacc|prop[óo]sito|mindful|calma/, '1506126613408-eca07ce68773'], [/carrera|vocaci|universidad|oferta|acceso|elegir/, '1541339907198-e08756dedf3f'], [/aprend|estudi|memoria|metacog|educa|ense[ñn]|tdah|atenci/, '1434030216411-0b793f4b4173'], [/curso|formaci|certific/, '1522202176988-66273c2fd55f'], [/hipoteca|vivienda|dinero|ahorro|inmobil|finanz|sueldo|inver/, '1579621970563-ebec7560ff3e'], [/libro|lectura|biblioteca/, '1532012197267-da84d127e765']], M = { mind: '1559757175-5700dde675bc', nexus: '1541339907198-e08756dedf3f', live: '1454496522488-7a8e488e8606', learn: '1481627834876-b7833e8f5570', build: '1461360370896-922624d12aa1' }, id = '';\n" +
  "      for (var q = 0; q < F.length && !id; q++) if (F[q][0].test(tx)) id = F[q][1];\n" +
  "      img = 'https://images.unsplash.com/photo-' + (id || M[a.mundo] || M.mind) + '?w=800&h=450&q=70&fit=crop&auto=format'; }\n";
const MARCA_I = '/* ==== AURZANE v4 (diseno/v4.css) ==== */', MARCA_F = '/* ==== fin AURZANE v4 ==== */';
const NO = /(^|\/)(eliminar|copias?|node_modules|\.git|vendor|wp-[a-z]+)(\/|$)/;
function aplicar(rel, t) {   // rel = <dominio>/<ruta>
  let o;
  if (/(^|\/)aurzane-ds\.css$/.test(rel)) {   // la hoja común lleva v4.css al final (sin convertir), entre marcas para poder actualizarla
    const i = t.indexOf(MARCA_I); o = P.transformar(i >= 0 ? t.slice(0, i).replace(/\s+$/, '') : t).out;
    o += '\n\n' + MARCA_I + '\n' + V4CSS.trim() + '\n' + MARCA_F + '\n';
  } else o = P.transformar(t).out;
  // Imágenes de Unsplash siempre con formato automático: el servidor de Unsplash entrega AVIF a quien lo admite (y WebP/JPG al resto)
  o = o.replace(/(https:\/\/images\.unsplash\.com\/photo-[\w-]+)(\?[^"'\s)<>]*)?/g, (m, base, q) => {
    q = (q || '?').replace(/&amp;/g, '&'); if (/[?&]auto=format/.test(q) || /[?&]fm=/.test(q)) return m;
    return base + (q === '?' ? '?auto=format' : q + (q.endsWith('?') || q.endsWith('&') ? '' : '&') + 'auto=format');
  });
  if (/^aurzane\.com\/aurzane-paleta\.js$/.test(rel) && o.indexOf('Tema único para todo AURZANE') < 0) {   // tema común, antes que la paleta
    const k = o.indexOf("(function (w, d) {\n  'use strict';\n  if (w.AurzanePaleta) return;");
    if (k >= 0) o = o.slice(0, k) + TEMA + '\n' + o.slice(k); else console.error('AVISO: no encontré dónde poner el tema en aurzane-paleta.js');
  }
  if (/^aurzane\.com\/aurzane-ds\.js$/.test(rel) && o.indexOf('v4: todas las páginas tienen claro y oscuro') < 0) {   // botón «Tema» en todas las páginas
    const a = "    var tema = d.getElementById('btnTema') || d.getElementById('btnTemaMi');\n";
    if (o.indexOf(a) >= 0) o = o.replace(a, a + BOTON); else console.error('AVISO: no encontré el botón de tema en aurzane-ds.js');
  }
  if (/^aurzane\.com\/aurzane-contenido\.js$/.test(rel) && o.indexOf('FOTO_V4') < 0) {   // tarjetas de artículos: siempre con foto real
    const a = "    var img = a.imagen && !/\\/biblioteca\\/recientes\\//.test(a.imagen) ? a.imagen : '';\n";
    if (o.indexOf(a) >= 0) o = o.replace(a, a + FOTO_V4); else console.error('AVISO: no encontré las tarjetas de artículos en aurzane-contenido.js');
  }
  if (/^aurzane\.com\/aurzane-estilo\.js$/.test(rel) && o.indexOf("'alquiler-por-municipio'") < 0) {   // la tarjeta del alquiler por municipio también lleva foto
    // sin fotos repetidas en la misma fila: reforma con una cocina en obra y alquiler por municipio con un salón (Unsplash, gratuitas)
    const a = "'calculadora-sueno': 'dormir' };", b = "viaje: '", c = "'calculadora-reforma': 'casa'";
    if (o.indexOf(a) >= 0 && o.indexOf(b) >= 0 && o.indexOf(c) >= 0) o = o.replace(a, "'calculadora-sueno': 'dormir', 'alquiler-por-municipio': 'salon', 'ejercicios': 'bienestar' };").replace(b, "obra: '1618832515490-e181c4794a45', salon: '1554995207-c18c203602cb', " + b).replace(c, "'calculadora-reforma': 'obra'");
    else console.error('AVISO: no encontré las fotos de tarjetas en aurzane-estilo.js');
  }
  if (/^aurzane\.com\/aurzane-contenido\.js$/.test(rel) && o.indexOf('az-art-c') < 0) {   // «Artículos recientes» de cada mundo: tarjeta con foto (antes solo texto)
    const a = `return '<a href="' + url + '" style="display:block;padding:16px 18px;border-radius:14px;border:1px solid rgba(127,127,127,.25);color:inherit;text-decoration:none;background:rgba(127,127,127,.05)">' +`;
    const b = `E(a.resumen) + '</span></a>';\n  }`;
    if (o.indexOf(a) >= 0 && o.indexOf(b) >= 0) o = o.replace(a, `return '<a class="az-art-c" href="' + url + '">' + (img ? '<img src="' + E(img) + '" alt="" loading="lazy" width="800" height="450">' : '') + '<span class="az-art-t">' +`).replace(b, `E(a.resumen) + '</span></span></a>';\n  }`);
    else console.error('AVISO: no encontré la tarjeta de artículos recientes en aurzane-contenido.js');
  }
  if (/^aurzane\.com\/aurzane-estilo\.js$/.test(rel) && o.indexOf('az-video-dia-caido') < 0) {   // vídeo del día retirado de YouTube: sin miniatura gris, la sección no se muestra
    const a = `'/hqdefault.jpg" alt="" loading="lazy">`;
    if (o.indexOf(a) >= 0) o = o.replace(a, `'/hqdefault.jpg" alt="" loading="lazy" data-v4="az-video-dia-caido" onload="if(this.naturalWidth<=120){var s=this.closest(\\'section\\');if(s)s.remove()}" onerror="var s=this.closest(\\'section\\');if(s)s.remove()">`);
    else console.error('AVISO: no encontré la miniatura del vídeo del día en aurzane-estilo.js');
  }
  if (/^aurzane\.com\/aurzane-estilo\.js$/.test(rel) && o.indexOf('az-v4-herofoto') < 0) {   // tests y calculadoras: cabecera con la foto grande de cada herramienta (no un fondo verde liso)
    const a = "    if (!/^(test-de-|calculadora-)/.test(slug) || slug === 'test-de-personalidad' || d.querySelector('.az-portada')) return;";
    const b = "    if (/^(test-de-|calculadora-)|^alquiler-por-municipio$/.test(slug)) { var hv = d.querySelector('section.hero') || d.querySelector('.hero');\n" +
      "      if (hv && !hv.hasAttribute('data-v4-foto')) { hv.setAttribute('data-v4-foto', '1'); hv.style.setProperty('--v4-foto', foto(TEMA[slug] || (slug === 'test-de-personalidad' ? 'espejo' : 'grafica'), 1800)); html.classList.add('az-v4-herofoto'); } }\n";
    if (o.indexOf(a) >= 0) o = o.replace(a, b + a); else console.error('AVISO: no encontré la portada de tests y calculadoras en aurzane-estilo.js');
  }
  return o;
}
module.exports = { aplicar };
if (require.main !== module) return;
const cambiados = []; let vistos = 0;
(function recorrer(d) {
  for (const e of fs.readdirSync(d, { withFileTypes: true })) {
    const f = path.join(d, e.name), rel = path.relative(raiz, f);
    if (NO.test(rel)) continue;
    if (e.isDirectory()) { recorrer(f); continue; }
    if (!/\.(html?|css|js)$/i.test(e.name) || /\.min\.js$/.test(e.name)) continue;
    const st = fs.statSync(f); if (st.size > 3e6) continue;
    vistos++;
    const t = fs.readFileSync(f, 'utf8'); const o = aplicar(rel, t);
    if (o !== t) { fs.writeFileSync(f, o); cambiados.push(rel); }
  }
})(raiz);
console.log(`v4: ${vistos} archivos revisados, ${cambiados.length} cambiados`);
if (lista) fs.writeFileSync(lista, cambiados.join('\n') + (cambiados.length ? '\n' : ''));
