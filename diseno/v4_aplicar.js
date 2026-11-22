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
const MARCA_I = '/* ==== AURZANE v4 (diseno/v4.css) ==== */', MARCA_F = '/* ==== fin AURZANE v4 ==== */';
const NO = /(^|\/)(eliminar|copias?|node_modules|\.git|vendor|wp-[a-z]+)(\/|$)/;
const cambiados = []; let vistos = 0;
(function recorrer(d) {
  for (const e of fs.readdirSync(d, { withFileTypes: true })) {
    const f = path.join(d, e.name), rel = path.relative(raiz, f);
    if (NO.test(rel)) continue;
    if (e.isDirectory()) { recorrer(f); continue; }
    if (!/\.(html?|css|js)$/i.test(e.name) || /\.min\.js$/.test(e.name)) continue;
    const st = fs.statSync(f); if (st.size > 3e6) continue;
    vistos++;
    const t = fs.readFileSync(f, 'utf8'); let o;
    if (/(^|\/)aurzane-ds\.css$/.test(rel)) {   // la hoja común lleva v4.css al final (sin convertir), entre marcas para poder actualizarla
      const i = t.indexOf(MARCA_I); o = P.transformar(i >= 0 ? t.slice(0, i).replace(/\s+$/, '') : t).out;
      o += '\n\n' + MARCA_I + '\n' + V4CSS.trim() + '\n' + MARCA_F + '\n';
    } else o = P.transformar(t).out;
    if (/^aurzane\.com\/aurzane-paleta\.js$/.test(rel) && o.indexOf('Tema único para todo AURZANE') < 0) {   // tema común, antes que la paleta
      const k = o.indexOf("(function (w, d) {\n  'use strict';\n  if (w.AurzanePaleta) return;");
      if (k >= 0) o = o.slice(0, k) + TEMA + '\n' + o.slice(k); else console.error('AVISO: no encontré dónde poner el tema en aurzane-paleta.js');
    }
    if (/^aurzane\.com\/aurzane-ds\.js$/.test(rel) && o.indexOf('v4: todas las páginas tienen claro y oscuro') < 0) {   // botón «Tema» en todas las páginas
      const a = "    var tema = d.getElementById('btnTema') || d.getElementById('btnTemaMi');\n";
      if (o.indexOf(a) >= 0) o = o.replace(a, a + BOTON); else console.error('AVISO: no encontré el botón de tema en aurzane-ds.js');
    }
    if (o !== t) { fs.writeFileSync(f, o); cambiados.push(rel); }
  }
})(raiz);
console.log(`v4: ${vistos} archivos revisados, ${cambiados.length} cambiados`);
if (lista) fs.writeFileSync(lista, cambiados.join('\n') + (cambiados.length ? '\n' : ''));
