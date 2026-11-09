/* =====================================================================
   informe-export.js — AURZANE OVP
   Descarga del informe integrado en PDF y en Word (.docx), a partir del
   informe ya dibujado en #reportContent (ver informe-v2.js).

   PDF: html2canvas + jsPDF, página por página (también funciona en
        teléfonos). Los cortes de página se eligen para no partir bloques
        ni dejar títulos sueltos. El membrete se dibuja en cada página como
        una franja de color (2,7 cm si el membrete tiene color de banda),
        con número de página al pie.
   Word: docx.js. Encabezado con la misma franja, títulos, tablas,
        listas y los gráficos convertidos a imagen.
   Las librerías se cargan solo al pulsar el botón.
   ===================================================================== */
(function(global){
  'use strict';

  var URL_JSPDF = 'https://cdn.jsdelivr.net/npm/jspdf@2.5.1/dist/jspdf.umd.min.js';
  var URL_HTML2CANVAS = 'https://cdn.jsdelivr.net/npm/html2canvas@1.4.1/dist/html2canvas.min.js';
  var URL_DOCX = 'https://cdn.jsdelivr.net/npm/docx@8.5.0/build/index.umd.js';
  var cargados = {};

  // global: nombre que deja la librería en window; si ya está, no se vuelve a
  // cargar (cargar html2pdf dos veces rompe jsPDF).
  function cargarScript(url, global_){
    if(global_ && global[global_]) return Promise.resolve();
    if(cargados[url]) return cargados[url];
    cargados[url] = new Promise(function(res, rej){
      var s = document.createElement('script');
      s.src = url; s.async = true;
      s.onload = function(){ res(); };
      s.onerror = function(){ delete cargados[url]; rej(new Error('No se pudo cargar ' + url)); };
      document.head.appendChild(s);
    });
    return cargados[url];
  }

  function membrete(){ return global.__ovpMembreteActual || {}; }
  // Escudo del membrete como PNG (normaliza webp/jpg y evita problemas de
  // formato en jsPDF y docx). Devuelve null si no hay o no carga.
  async function escudoPng(){
    var url = membrete().escudo_url;
    if(!url) return null;
    try{
      var img = new Image();
      img.crossOrigin = 'anonymous';
      img.src = url;
      await img.decode();
      var max = 300, k = Math.min(1, max / Math.max(img.naturalWidth, img.naturalHeight));
      var c = document.createElement('canvas');
      c.width = Math.max(1, Math.round(img.naturalWidth * k));
      c.height = Math.max(1, Math.round(img.naturalHeight * k));
      c.getContext('2d').drawImage(img, 0, 0, c.width, c.height);
      var dataUrl = c.toDataURL('image/png');
      var bin = atob(dataUrl.split(',')[1]), buf = new Uint8Array(bin.length);
      for(var i = 0; i < bin.length; i++) buf[i] = bin.charCodeAt(i);
      return { dataUrl: dataUrl, data: buf, width: c.width, height: c.height };
    }catch(e){ return null; }
  }

  function datos(){ return global.__ovpClienteActual || { nombre: '', fecha: '' }; }
  function limpiarComillas(t){ return String(t || '').replace(/[“”]/g, '"').replace(/[‘’]/g, "'"); }
  function hexARgb(hex, def){
    var m = /^#?([0-9a-f]{6})$/i.exec(String(hex || '').trim());
    if(!m) return def;
    var n = parseInt(m[1], 16);
    return [(n >> 16) & 255, (n >> 8) & 255, n & 255];
  }
  function hexDocx(hex, def){
    var m = /^#?([0-9a-f]{6})$/i.exec(String(hex || '').trim());
    return m ? m[1].toUpperCase() : def;
  }
  function nombreArchivo(ext){
    var n = (datos().nombre || 'informe').normalize('NFD').replace(/[̀-ͯ]/g, '')
      .replace(/[^A-Za-z0-9]+/g, '-').replace(/^-+|-+$/g, '').toLowerCase() || 'informe';
    return 'informe-ovp-' + n + '.' + ext;
  }
  function descargarBlob(blob, nombre){
    var a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = nombre;
    document.body.appendChild(a);
    a.click();
    setTimeout(function(){ URL.revokeObjectURL(a.href); a.remove(); }, 4000);
  }

  /* ====================== gráficos a imagen ====================== */
  // Bloques que nunca se parten entre dos páginas y títulos que no deben
  // quedar sueltos al pie de una página.
  var NO_PARTIR = '.applicant-box, .chart-box, .exec-summary, tr, .dim-row, .career-card, .finding-block, .reco-area-head, .interp-item, .balance-col, .reco-list li, .conclusion-box p, .signature-block, .como-leer, .interpretive-disclaimer, .methodology, .data-status, .brief-row, p, h4';
  var TITULOS = 'h2, h3, .module-divider, .reco-area-head';

  function esperarImagenes(raiz){
    return Promise.all(Array.prototype.map.call(raiz.querySelectorAll('img'), function(img){
      return img.complete ? Promise.resolve() : new Promise(function(r){ img.onload = img.onerror = r; });
    }));
  }

  // Elige dónde cortar cada página: lo más abajo posible sin partir ningún
  // bloque y sin dejar un título solo al final de la página.
  function calcularCortes(raiz, altoPagina){
    var top0 = raiz.getBoundingClientRect().top;
    var total = raiz.scrollHeight;
    var bloques = Array.prototype.map.call(raiz.querySelectorAll(NO_PARTIR), function(e){
      var r = e.getBoundingClientRect();
      return { t: r.top - top0, b: r.bottom - top0 };
    }).filter(function(x){ return x.b - x.t > 0 && x.b - x.t < altoPagina * 0.95; });
    var titulos = Array.prototype.map.call(raiz.querySelectorAll(TITULOS), function(e){
      var r = e.getBoundingClientRect();
      return { t: r.top - top0, b: r.bottom - top0 };
    });
    var candidatos = [];
    bloques.forEach(function(x){ candidatos.push(x.t, x.b); });
    candidatos = candidatos.filter(function(v){ return v > 0 && v < total; }).sort(function(a, b){ return a - b; });

    function seguro(c){
      for(var i = 0; i < bloques.length; i++){
        if(bloques[i].t < c - 1 && bloques[i].b > c + 1) return false;
      }
      for(var j = 0; j < titulos.length; j++){
        if(titulos[j].t >= c - 120 && titulos[j].t < c && titulos[j].b <= c + 1) return false;
      }
      return true;
    }

    var cortes = [0], y = 0;
    while(total - y > altoPagina){
      var limite = y + altoPagina, elegido = null;
      for(var k = candidatos.length - 1; k >= 0; k--){
        var c = candidatos[k];
        if(c > limite) continue;
        if(c <= y + altoPagina * 0.35) break;
        if(seguro(c)){ elegido = c; break; }
      }
      if(elegido === null) elegido = limite;
      cortes.push(elegido);
      y = elegido;
    }
    cortes.push(total);
    return cortes;
  }

  async function generarPDF(){
    var el = document.getElementById('reportContent');
    if(!el || !el.innerHTML.trim()) throw new Error('No hay informe para descargar.');
    await cargarScript(URL_JSPDF, 'jspdf');
    await cargarScript(URL_HTML2CANVAS, 'html2canvas');

    var m = membrete();
    var conBanda = !!m.color_banda;
    var altoBanda = conBanda ? 27 : 18; // mm (2,7 cm para la franja institucional)
    var fondo = conBanda ? hexARgb(m.color_banda, [245, 196, 0]) : [8, 11, 23];
    var tinta = conBanda ? hexARgb(m.color_texto_banda, [20, 33, 61]) : [234, 207, 146];
    var marca = limpiarComillas(m.nombre_marca || 'AURZANE');
    var sub = limpiarComillas(m.subtitulo || '');
    var d = datos();
    var escudo = await escudoPng();

    var MARGEN_X = 12, MARGEN_SUP = altoBanda + 7, MARGEN_INF = 16;
    var ANCHO_MM = 210 - MARGEN_X * 2, ALTO_MM = 297 - MARGEN_SUP - MARGEN_INF;
    var ANCHO_PX = 760;
    var mmPorPx = ANCHO_MM / ANCHO_PX;
    var altoPaginaPx = Math.floor(ALTO_MM / mmPorPx);

    // Copia fuera de pantalla con ancho fijo de página y gráficos como imagen.
    var caja = document.createElement('div');
    caja.setAttribute('aria-hidden', 'true');
    caja.style.cssText = 'position:absolute;left:-12000px;top:0;width:' + ANCHO_PX + 'px;pointer-events:none;';
    var clon = el.cloneNode(true);
    clon.removeAttribute('id');
    clon.classList.add('exportando-pdf');
    clon.style.width = ANCHO_PX + 'px';
    caja.appendChild(clon);
    document.body.appendChild(caja);

    try{
      var originales = el.querySelectorAll('.chart-box svg');
      var copias = clon.querySelectorAll('.chart-box svg');
      for(var i = 0; i < copias.length; i++){
        try{
          var png = await svgAPng(originales[i], true);
          var img = document.createElement('img');
          img.src = png.dataUrl;
          img.style.cssText = 'display:block;margin:0 auto;max-width:100%;max-height:330px;width:auto;height:auto;';
          copias[i].parentNode.replaceChild(img, copias[i]);
        }catch(e){ /* se deja el SVG tal cual */ }
      }
      await esperarImagenes(clon);
      if(document.fonts && document.fonts.ready) await document.fonts.ready;

      var cortes = calcularCortes(clon, altoPaginaPx);
      var pdf = new global.jspdf.jsPDF({ unit: 'mm', format: 'a4', orientation: 'portrait', compress: true });
      var escala = (global.devicePixelRatio || 1) > 1 ? 2 : 1.7;

      // Cada página se dibuja a través de una "ventana" del alto de la
      // página que se desplaza sobre la copia del informe.
      caja.style.overflow = 'hidden';
      for(var p = 0; p < cortes.length - 1; p++){
        var y0 = cortes[p], alto = Math.ceil(cortes[p + 1] - y0);
        if(alto < 2) continue;
        caja.style.height = alto + 'px';
        clon.style.marginTop = (-y0) + 'px';
        var canvas = await global.html2canvas(caja, {
          scale: escala, backgroundColor: '#FBF9F3', logging: false, useCORS: true,
          width: ANCHO_PX, height: alto
        });
        if(p > 0) pdf.addPage();
        pdf.addImage(canvas.toDataURL('image/jpeg', 0.86), 'JPEG', MARGEN_X, MARGEN_SUP, ANCHO_MM, alto * mmPorPx, undefined, 'FAST');
        canvas.width = canvas.height = 0;
      }

      var total = pdf.internal.getNumberOfPages();
      var W = 210, H = 297;
      for(var n = 1; n <= total; n++){
        pdf.setPage(n);
        pdf.setFillColor(fondo[0], fondo[1], fondo[2]);
        pdf.rect(0, 0, W, altoBanda, 'F');
        if(conBanda){
          pdf.setFillColor(tinta[0], tinta[1], tinta[2]);
          pdf.rect(0, altoBanda - 1.1, W, 1.1, 'F');
        }
        var xMarca = MARGEN_X;
        if(escudo){
          var altoEsc = altoBanda - (conBanda ? 8 : 5);
          var anchoEsc = Math.min(altoEsc * escudo.width / escudo.height, 32);
          var altoReal = anchoEsc * escudo.height / escudo.width;
          pdf.addImage(escudo.dataUrl, 'PNG', MARGEN_X, (altoBanda - altoReal) / 2 - (conBanda ? 0.5 : 0), anchoEsc, altoReal, 'escudo', 'FAST');
          xMarca = MARGEN_X + anchoEsc + 4;
        }
        pdf.setFont('helvetica', 'normal');
        pdf.setFontSize(8);
        var anchoDer = pdf.getTextWidth('Informe Integrado de Orientación Vocacional-Profesional');
        pdf.setTextColor(tinta[0], tinta[1], tinta[2]);
        pdf.setFont('times', 'bold');
        pdf.setFontSize(conBanda ? 15 : 14);
        var lineasMarca = pdf.splitTextToSize(marca, W - MARGEN_X - anchoDer - 6 - xMarca);
        var yMarca = conBanda ? 11 : 9;
        pdf.text(lineasMarca, xMarca, yMarca);
        if(sub){
          pdf.setFont('times', 'normal');
          pdf.setFontSize(11);
          pdf.text(sub, xMarca, yMarca + lineasMarca.length * 6 + 0.5);
        }
        pdf.setFont('helvetica', 'normal');
        pdf.setFontSize(8);
        pdf.text('Informe Integrado de Orientación Vocacional-Profesional', W - MARGEN_X, yMarca, { align: 'right' });
        if(d.fecha) pdf.text('Fecha de la evaluación: ' + d.fecha, W - MARGEN_X, yMarca + 5, { align: 'right' });
        pdf.setDrawColor(228, 222, 204);
        pdf.line(MARGEN_X, H - 11, W - MARGEN_X, H - 11);
        pdf.setTextColor(140, 135, 120);
        pdf.setFontSize(7.5);
        pdf.text(limpiarComillas(d.nombre || '') + '  ·  Documento confidencial', MARGEN_X, H - 6.5);
        pdf.text('Página ' + n + ' de ' + total, W - MARGEN_X, H - 6.5, { align: 'right' });
      }
      pdf.setProperties({ title: 'Informe Integrado de Orientación Vocacional-Profesional', author: 'AURZANE OVP' });
      return pdf.output('blob');
    } finally {
      caja.remove();
    }
  }
  async function descargarPDF(){
    descargarBlob(await generarPDF(), nombreArchivo('pdf'));
  }

  async function svgAPng(svg, soloDataUrl){
    var vb = svg.viewBox && svg.viewBox.baseVal;
    var w = (vb && vb.width) || svg.getBoundingClientRect().width || 600;
    var h = (vb && vb.height) || svg.getBoundingClientRect().height || 300;
    var clon = svg.cloneNode(true);
    clon.setAttribute('xmlns', 'http://www.w3.org/2000/svg');
    clon.setAttribute('width', w);
    clon.setAttribute('height', h);
    var s = new XMLSerializer().serializeToString(clon);
    var img = new Image();
    img.src = 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(s);
    await img.decode();
    var esc = 2;
    var c = document.createElement('canvas');
    c.width = Math.round(w * esc); c.height = Math.round(h * esc);
    var ctx = c.getContext('2d');
    ctx.fillStyle = '#F3EFE2';
    ctx.fillRect(0, 0, c.width, c.height);
    ctx.drawImage(img, 0, 0, c.width, c.height);
    if(soloDataUrl) return { dataUrl: c.toDataURL('image/png'), width: w, height: h };
    var blob = await new Promise(function(r){ c.toBlob(r, 'image/png'); });
    var buf = new Uint8Array(await blob.arrayBuffer());
    var maxW = 600;
    var escala = Math.min(1, maxW / w);
    return { data: buf, width: Math.round(w * escala), height: Math.round(h * escala) };
  }

  function construirWord(D){
    var m = membrete(), d = datos();
    var conBanda = !!m.color_banda;
    var BANDA = conBanda ? hexDocx(m.color_banda, 'F5C400') : '080B17';
    var TINTA = conBanda ? hexDocx(m.color_texto_banda, '14213D') : 'EACF92';
    var ORO = '8A6A28', TEXTO = '1C1B18', TENUE = '5B584F', LAVADO = 'F3EFE2', LINEA = 'E4DECC';
    var PAGE_W = 11906, MARGEN_X = 1134;
    var ANCHO = PAGE_W - MARGEN_X * 2;
    var SIN_BORDE = { style: D.BorderStyle.NONE, size: 0, color: 'FFFFFF' };
    var bordesNinguno = { top: SIN_BORDE, bottom: SIN_BORDE, left: SIN_BORDE, right: SIN_BORDE, insideHorizontal: SIN_BORDE, insideVertical: SIN_BORDE };

    function linea(color, size){ return { style: D.BorderStyle.SINGLE, size: size || 4, color: color || LINEA }; }

    function runsDe(nodo, estilo, salida){
      salida = salida || [];
      estilo = estilo || {};
      nodo.childNodes.forEach(function(n){
        if(n.nodeType === 3){
          var t = n.nodeValue.replace(/\s+/g, ' ');
          if(t) salida.push(new D.TextRun({ text: t, bold: !!estilo.bold, italics: !!estilo.italics, color: estilo.color, size: estilo.size, font: estilo.font }));
        } else if(n.nodeType === 1){
          var tag = n.tagName;
          if(tag === 'BR'){ salida.push(new D.TextRun({ text: '', break: 1 })); return; }
          if(n.classList.contains('dim-tag') && estilo.sinEtiquetas) return;
          var e2 = Object.assign({}, estilo);
          if(tag === 'B' || tag === 'STRONG') e2.bold = true;
          if(tag === 'I' || tag === 'EM' || n.classList.contains('mono')) e2.italics = true;
          runsDe(n, e2, salida);
        }
      });
      return salida;
    }
    function textoPlano(n){ return (n.textContent || '').replace(/\s+/g, ' ').trim(); }
    function parrafo(nodo, opts){
      opts = opts || {};
      var runs = runsDe(nodo, opts.estilo || {});
      if(!runs.length) return null;
      return new D.Paragraph({ children: runs, spacing: { after: opts.after == null ? 120 : opts.after, before: opts.before || 0, line: 300 }, alignment: opts.align, indent: opts.indent });
    }
    function celda(hijos, opts){
      opts = opts || {};
      return new D.TableCell({
        children: hijos.length ? hijos : [new D.Paragraph('')],
        shading: opts.fill ? { type: D.ShadingType.CLEAR, color: 'auto', fill: opts.fill } : undefined,
        margins: { top: opts.pad || 100, bottom: opts.pad || 100, left: 140, right: 140 },
        width: opts.width ? { size: opts.width, type: D.WidthType.DXA } : undefined,
        verticalAlign: opts.vAlign,
        borders: opts.borders,
        columnSpan: opts.span
      });
    }
    function tablaCaja(hijos, fill, bordeIzq){
      return new D.Table({
        width: { size: ANCHO, type: D.WidthType.DXA },
        columnWidths: [ANCHO],
        rows: [new D.TableRow({ children: [celda(hijos, { fill: fill, pad: 160, borders: {
          top: bordeIzq ? SIN_BORDE : linea('D8C9A0'), bottom: bordeIzq ? SIN_BORDE : linea('D8C9A0'),
          right: bordeIzq ? SIN_BORDE : linea('D8C9A0'), left: bordeIzq ? linea(ORO, 18) : linea('D8C9A0') } })] })]
      });
    }
    function espacio(){ return new D.Paragraph({ children: [], spacing: { after: 120 } }); }

    function tablaSimple(filas, anchos, opts){
      opts = opts || {};
      return new D.Table({
        width: { size: ANCHO, type: D.WidthType.DXA },
        columnWidths: anchos,
        borders: { top: linea(), bottom: linea(), left: SIN_BORDE, right: SIN_BORDE, insideHorizontal: linea(), insideVertical: SIN_BORDE },
        rows: filas.map(function(f, i){
          var cab = opts.cabecera && i === 0;
          return new D.TableRow({ tableHeader: cab, children: f.map(function(c, j){
            var p = (c instanceof D.Paragraph) ? c : new D.Paragraph({ children: [new D.TextRun({ text: String(c), bold: cab || (opts.primeraNegrita && j === 0), color: cab ? ORO : (opts.colores && opts.colores[i] && j === (opts.colorCol || 1) ? opts.colores[i] : TEXTO), size: cab ? 17 : 19 })] });
            return celda([p], { width: anchos[j], fill: cab ? LAVADO : (opts.cebra && i % 2 === 0 ? 'FBF9F3' : undefined) });
          }) });
        })
      });
    }

    var COLOR_NIVEL = { Alto: '5F7A3F', Bajo: 'A15353', Medio: ORO, Top: '5F7A3F' };
    var bloques = [];
    var imagenes = D.__imagenes || [];
    var idxImg = 0;

    function procesar(el){
      Array.prototype.forEach.call(el.children, function(n){ bloque(n); });
    }

    function bloque(n){
      var cl = n.classList, tag = n.tagName;
      if(cl.contains('report-head') || cl.contains('report-footer')) return;

      if(cl.contains('applicant-box')){
        var items = n.querySelectorAll('.a-item');
        var fila1 = [], fila2 = [];
        var w = Math.floor(ANCHO / items.length);
        items.forEach(function(it){
          fila1.push(celda([new D.Paragraph({ children: [new D.TextRun({ text: textoPlano(it.querySelector('.a-lbl')).toUpperCase(), size: 14, color: TENUE })] })], { width: w, pad: 40 }));
          fila2.push(celda([new D.Paragraph({ children: [new D.TextRun({ text: textoPlano(it.querySelector('.a-val')), size: 21, bold: true, font: 'Georgia' })] })], { width: w, pad: 40 }));
        });
        bloques.push(new D.Table({ width: { size: ANCHO, type: D.WidthType.DXA }, columnWidths: items.length ? Array(items.length).fill(w) : [ANCHO], borders: bordesNinguno,
          rows: [new D.TableRow({ children: fila1 }), new D.TableRow({ children: fila2 })] }));
        bloques.push(espacio());
        return;
      }
      if(tag === 'H2'){
        bloques.push(new D.Paragraph({ heading: D.HeadingLevel.HEADING_1, keepNext: true, spacing: { before: 360, after: 120 },
          children: [new D.TextRun({ text: textoPlano(n), font: 'Georgia', size: 30, color: TEXTO })] }));
        return;
      }
      if(tag === 'H3'){
        bloques.push(new D.Paragraph({ heading: D.HeadingLevel.HEADING_2, keepNext: true, spacing: { before: 240, after: 100 },
          children: [new D.TextRun({ text: textoPlano(n), font: 'Georgia', size: 24, color: '4A4638' })] }));
        return;
      }
      if(tag === 'H4'){
        bloques.push(new D.Paragraph({ keepNext: true, spacing: { before: 120, after: 80 }, children: runsDe(n, { bold: true, font: 'Georgia', size: 22, color: '6B4F14' }) }));
        return;
      }
      if(cl.contains('module-divider')){
        bloques.push(new D.Paragraph({ alignment: D.AlignmentType.CENTER, keepNext: true, spacing: { before: 480, after: 200 },
          border: { bottom: linea(LINEA, 6) },
          children: [new D.TextRun({ text: textoPlano(n).toUpperCase(), size: 17, color: ORO, characterSpacing: 40 })] }));
        return;
      }
      if(tag === 'P'){
        var esNota = cl.contains('section-note');
        var p = parrafo(n, { estilo: esNota ? { color: TENUE, size: 19 } : { size: 21 } });
        if(p) bloques.push(p);
        return;
      }
      if(cl.contains('data-status')){
        var sp = Array.prototype.map.call(n.children, function(s){ return { t: textoPlano(s), ok: s.classList.contains('complete') }; });
        bloques.push(new D.Paragraph({ spacing: { after: 160 }, children: sp.map(function(s, i){
          return new D.TextRun({ text: (i ? '   ' : '') + (s.ok ? '✓ ' : '○ ') + s.t, size: 17, color: s.ok ? '52673A' : TENUE });
        }) }));
        return;
      }
      if(cl.contains('interpretive-disclaimer') || cl.contains('methodology') || cl.contains('como-leer') || cl.contains('conclusion-box')){
        var hijosP = n.querySelectorAll(':scope > p');
        var ps = [];
        if(hijosP.length){ hijosP.forEach(function(pp){ var x = parrafo(pp, { estilo: { size: 20 } }); if(x) ps.push(x); }); }
        else { var x2 = parrafo(n, { estilo: { size: 20 }, after: 0 }); if(x2) ps.push(x2); }
        bloques.push(tablaCaja(ps, cl.contains('interpretive-disclaimer') ? 'F7F1DF' : LAVADO, true));
        bloques.push(espacio());
        return;
      }
      if(cl.contains('career-card')){
        var hijos = [];
        Array.prototype.forEach.call(n.children, function(c){
          if(c.tagName === 'H4') hijos.push(new D.Paragraph({ spacing: { after: 100 }, children: runsDe(c, { bold: true, font: 'Georgia', size: 24, color: '6B4F14' }) }));
          else { var x = parrafo(c, { estilo: { size: 20, color: c.classList.contains('career-note') ? '5C5546' : TEXTO, italics: c.classList.contains('career-note') } }); if(x) hijos.push(x); }
        });
        bloques.push(tablaCaja(hijos, 'FBF6E8', false));
        bloques.push(espacio());
        return;
      }
      if(cl.contains('chart-box')){
        var img = imagenes[idxImg++];
        if(img){
          bloques.push(new D.Paragraph({ alignment: D.AlignmentType.CENTER, spacing: { after: 160 },
            children: [new D.ImageRun({ data: img.data, transformation: { width: img.width, height: img.height } })] }));
        }
        return;
      }
      if(cl.contains('dim-list')){
        var filas = [['Dimensión', 'Nivel', 'Resultado']], colores = [null];
        n.querySelectorAll('.dim-row').forEach(function(r){
          var nameEl = r.querySelector('.dim-name');
          var tagEl = r.querySelector('.dim-tag');
          var tagT = tagEl ? textoPlano(tagEl) : '';
          var nombre = nameEl ? textoPlano(nameEl).replace(new RegExp(tagT + '$'), '').trim() : '';
          filas.push([nombre, tagT || '—', textoPlano(r.querySelector('.dim-pd'))]);
          colores.push(COLOR_NIVEL[tagT] || TEXTO);
        });
        bloques.push(tablaSimple(filas, [Math.round(ANCHO * 0.36), Math.round(ANCHO * 0.14), ANCHO - Math.round(ANCHO * 0.36) - Math.round(ANCHO * 0.14)], { cabecera: true, primeraNegrita: true, colores: colores, colorCol: 1 }));
        bloques.push(espacio());
        return;
      }
      if(cl.contains('exec-summary')){
        var f2 = [];
        n.querySelectorAll('.exec-card').forEach(function(c){ f2.push([textoPlano(c.querySelector('.ec-lbl')), textoPlano(c.querySelector('.ec-val'))]); });
        bloques.push(tablaSimple(f2, [Math.round(ANCHO * 0.42), ANCHO - Math.round(ANCHO * 0.42)], { primeraNegrita: true, cebra: true }));
        bloques.push(espacio());
        return;
      }
      if(tag === 'TABLE'){
        var f3 = [];
        n.querySelectorAll('tr').forEach(function(tr){ f3.push(Array.prototype.map.call(tr.children, textoPlano)); });
        var nc = f3[0] ? f3[0].length : 1;
        var anchos = nc === 4 ? [1900, 2700, 1500, ANCHO - 6100] : Array(nc).fill(Math.floor(ANCHO / nc));
        bloques.push(tablaSimple(f3, anchos, { cabecera: true, primeraNegrita: true }));
        bloques.push(espacio());
        return;
      }
      if(cl.contains('finding-block')){
        var cab = n.querySelector('.fb-head');
        var cuerpo = [];
        n.querySelectorAll('.fb-body p').forEach(function(pp){ var x = parrafo(pp, { estilo: { size: 20 } }); if(x) cuerpo.push(x); });
        bloques.push(new D.Table({ width: { size: ANCHO, type: D.WidthType.DXA }, columnWidths: [ANCHO],
          rows: [
            new D.TableRow({ children: [celda([new D.Paragraph({ children: [
              new D.TextRun({ text: textoPlano(cab.querySelector('h4')), bold: true, color: 'F5EFDF', size: 22, font: 'Georgia' }),
              new D.TextRun({ text: '   ' + textoPlano(cab.querySelector('.fb-total') || document.createElement('i')), color: 'C8DBA0', size: 17 })
            ] })], { fill: '3A4326' })] }),
            new D.TableRow({ children: [celda(cuerpo, { fill: LAVADO })] })
          ] }));
        bloques.push(espacio());
        return;
      }
      if(cl.contains('reco-area')){
        var hd = n.querySelector('.reco-area-head');
        bloques.push(new D.Paragraph({ keepNext: true, spacing: { before: 160, after: 60 }, children: [
          new D.TextRun({ text: textoPlano(hd.querySelector('h4')), bold: true, font: 'Georgia', size: 22 }),
          new D.TextRun({ text: '  (' + textoPlano(hd.querySelector('.reco-band')) + ')', size: 18, color: ORO })
        ] }));
        n.querySelectorAll('li').forEach(function(li){ bloques.push(itemLista(li, '•')); });
        return;
      }
      if(tag === 'UL' || tag === 'OL'){
        n.querySelectorAll(':scope > li').forEach(function(li){
          var mark = li.querySelector('.reco-mark');
          bloques.push(itemLista(li, mark ? textoPlano(mark) + '.' : '•'));
        });
        bloques.push(espacio());
        return;
      }
      if(cl.contains('balance-grid')){
        var cols = n.querySelectorAll('.balance-col');
        var mitad = Math.floor(ANCHO / 2);
        bloques.push(new D.Table({ width: { size: ANCHO, type: D.WidthType.DXA }, columnWidths: [mitad, ANCHO - mitad], borders: bordesNinguno,
          rows: [new D.TableRow({ children: Array.prototype.map.call(cols, function(c){
            var fuerte = c.classList.contains('fuerte');
            var hs = [new D.Paragraph({ spacing: { after: 80 }, children: [new D.TextRun({ text: textoPlano(c.querySelector('h4')), bold: true, font: 'Georgia', size: 22, color: fuerte ? '5F7A3F' : 'A15353' })] })];
            c.querySelectorAll('li').forEach(function(li){ hs.push(itemLista(li, '•')); });
            return celda(hs, { fill: fuerte ? 'F0F5E6' : 'F8ECEC', width: mitad, pad: 140 });
          }) })] }));
        bloques.push(espacio());
        return;
      }
      if(cl.contains('interp-item')){
        Array.prototype.forEach.call(n.children, function(c){
          if(c.tagName === 'H4'){
            var banda = c.querySelector('.reco-band');
            var nombreH = textoPlano(c).replace(banda ? textoPlano(banda) : '', '').trim();
            var hr = [new D.TextRun({ text: nombreH, bold: true, font: 'Georgia', size: 21 })];
            if(banda) hr.push(new D.TextRun({ text: '   ' + textoPlano(banda), size: 17, color: COLOR_NIVEL[textoPlano(banda)] || ORO }));
            bloques.push(new D.Paragraph({ keepNext: true, spacing: { before: 140, after: 60 }, children: hr }));
          } else {
            var x = parrafo(c, { estilo: c.classList.contains('interp-def') ? { italics: true, color: TENUE, size: 19 } : { size: 20 } });
            if(x) bloques.push(x);
          }
        });
        return;
      }
      if(cl.contains('signature-block')){
        bloques.push(new D.Paragraph({ spacing: { before: 600 }, children: [] }));
        Array.prototype.forEach.call(n.children, function(c, i){
          bloques.push(new D.Paragraph({ alignment: D.AlignmentType.CENTER, spacing: { after: 40 },
            border: i === 0 ? { bottom: linea(TEXTO, 6) } : undefined,
            children: [new D.TextRun({ text: textoPlano(c), italics: i === 0, bold: i === 1, size: i === 0 ? 32 : 18, font: 'Georgia', color: i > 1 ? TENUE : TEXTO })] }));
        });
        return;
      }
      // contenedores genéricos
      if(n.children.length) { procesar(n); return; }
      var gen = parrafo(n, { estilo: { size: 21 } });
      if(gen) bloques.push(gen);
    }

    function itemLista(li, marca){
      var runs = [new D.TextRun({ children: [marca, new D.Tab()], color: ORO, italics: true, size: 20 })];
      li.childNodes.forEach(function(c){
        if(c.nodeType === 1 && c.classList.contains('reco-mark')) return;
        if(c.nodeType === 3){ var t = c.nodeValue.replace(/\s+/g, ' '); if(t.trim()) runs.push(new D.TextRun({ text: t, size: 20 })); }
        else if(c.nodeType === 1){ runsDe(c, { size: 20, bold: c.tagName === 'B' }, runs); }
      });
      return new D.Paragraph({ children: runs, spacing: { after: 80, line: 290 }, indent: { left: 420, hanging: 420 },
        tabStops: [{ type: D.TabStopType.LEFT, position: 420 }] });
    }

    procesar(document.getElementById('reportContent'));

    // ---------- encabezado con franja ----------
    var marca = m.nombre_marca || 'AURZANE';
    var celdaIzq = [
      new D.Paragraph({ children: [new D.TextRun({ text: marca, bold: true, font: 'Georgia', size: conBanda ? 27 : 26, color: TINTA })] })
    ];
    if(m.subtitulo) celdaIzq.push(new D.Paragraph({ children: [new D.TextRun({ text: m.subtitulo, font: 'Georgia', size: 21, color: TINTA })] }));
    var celdaDer = [
      new D.Paragraph({ alignment: D.AlignmentType.RIGHT, children: [new D.TextRun({ text: 'Informe Integrado de Orientación Vocacional-Profesional', size: 15, color: TINTA })] }),
      new D.Paragraph({ alignment: D.AlignmentType.RIGHT, children: [new D.TextRun({ text: d.fecha ? 'Fecha de la evaluación: ' + d.fecha : '', size: 15, color: TINTA })] })
    ];
    var altoBandaTw = conBanda ? 1531 : 1020; // 2,7 cm / 1,8 cm
    var izqW = Math.round(PAGE_W * 0.64);
    var escudo = D.__escudo;
    var celdasCab = [];
    if(escudo){
      var altoEscPx = conBanda ? 70 : 46;
      var anchoEscPx = Math.min(Math.round(altoEscPx * escudo.width / escudo.height), 120);
      altoEscPx = Math.round(anchoEscPx * escudo.height / escudo.width);
      var escW = MARGEN_X + anchoEscPx * 15 + 160;
      celdasCab.push(new D.TableCell({ children: [new D.Paragraph({ children: [new D.ImageRun({ data: escudo.data, transformation: { width: anchoEscPx, height: altoEscPx } })] })],
        width: { size: escW, type: D.WidthType.DXA }, verticalAlign: D.VerticalAlign.CENTER,
        shading: { type: D.ShadingType.CLEAR, color: 'auto', fill: BANDA }, margins: { left: MARGEN_X, right: 80, top: 60, bottom: 60 } }));
      izqW -= escW;
    }
    var header = new D.Header({ children: [
      new D.Table({
        width: { size: PAGE_W, type: D.WidthType.DXA },
        columnWidths: (escudo ? [PAGE_W - Math.round(PAGE_W * 0.36) - izqW] : []).concat([izqW, Math.round(PAGE_W * 0.36)]),
        indent: { size: -MARGEN_X, type: D.WidthType.DXA },
        borders: bordesNinguno,
        rows: [new D.TableRow({ height: { value: altoBandaTw, rule: D.HeightRule.EXACT }, children: celdasCab.concat([
          new D.TableCell({ children: celdaIzq, width: { size: izqW, type: D.WidthType.DXA }, verticalAlign: D.VerticalAlign.CENTER,
            shading: { type: D.ShadingType.CLEAR, color: 'auto', fill: BANDA }, margins: { left: escudo ? 80 : MARGEN_X, right: 120, top: 80, bottom: 80 } }),
          new D.TableCell({ children: celdaDer, width: { size: Math.round(PAGE_W * 0.36), type: D.WidthType.DXA }, verticalAlign: D.VerticalAlign.CENTER,
            shading: { type: D.ShadingType.CLEAR, color: 'auto', fill: BANDA }, margins: { left: 120, right: MARGEN_X, top: 80, bottom: 80 } })
        ]) })]
      }),
      new D.Paragraph({ children: [] })
    ] });
    var footer = new D.Footer({ children: [
      new D.Paragraph({ border: { top: linea(LINEA, 6) }, tabStops: [{ type: D.TabStopType.RIGHT, position: ANCHO }], children: [
        new D.TextRun({ text: (d.nombre || '') + '  ·  Documento confidencial', size: 15, color: '8C8778' }),
        new D.TextRun({ children: [new D.Tab(), 'Página ', D.PageNumber.CURRENT, ' de ', D.PageNumber.TOTAL_PAGES], size: 15, color: '8C8778' })
      ] })
    ] });

    return new D.Document({
      creator: 'AURZANE OVP',
      title: 'Informe Integrado de Orientación Vocacional-Profesional',
      styles: { default: { document: { run: { font: 'Calibri', size: 21, color: TEXTO } } } },
      sections: [{
        properties: { page: {
          size: { width: PAGE_W, height: 16838 },
          margin: { top: altoBandaTw + 500, bottom: 1200, left: MARGEN_X, right: MARGEN_X, header: 0, footer: 500 }
        } },
        headers: { default: header },
        footers: { default: footer },
        children: bloques
      }]
    });
  }

  async function generarWord(){
    var el = document.getElementById('reportContent');
    if(!el || !el.innerHTML.trim()) throw new Error('No hay informe para descargar.');
    await cargarScript(URL_DOCX, 'docx');
    var D = global.docx;
    var svgs = el.querySelectorAll('.chart-box');
    var imagenes = [];
    for(var i = 0; i < svgs.length; i++){
      var svg = svgs[i].querySelector('svg');
      try { imagenes.push(svg ? await svgAPng(svg) : null); } catch(e){ imagenes.push(null); }
    }
    D.__imagenes = imagenes;
    D.__escudo = await escudoPng();
    var doc = construirWord(D);
    return D.Packer.toBlob(doc);
  }
  async function descargarWord(){
    descargarBlob(await generarWord(), nombreArchivo('docx'));
  }

  // Botones: envuelve cada descarga con estado de "preparando" y un mensaje
  // claro si algo falla (por ejemplo, sin conexión para cargar la librería).
  function conBoton(btn, fn, etiqueta){
    return async function(){
      if(btn.disabled) return;
      var original = btn.innerHTML;
      btn.disabled = true;
      btn.innerHTML = 'Preparando ' + etiqueta + '…';
      try { await fn(); }
      catch(e){
        console.error(e);
        if(global.__aurzaneLogErr) global.__aurzaneLogErr('descarga ' + etiqueta + ': ' + (e && e.message));
        alertaSuave('No pudimos preparar el ' + etiqueta + '. Revisa tu conexión e inténtalo de nuevo.');
      }
      finally { btn.disabled = false; btn.innerHTML = original; }
    };
  }
  function alertaSuave(msg){
    if(typeof global.showToast === 'function') { global.showToast(msg, 'error'); return; }
    var t = document.createElement('div');
    t.textContent = msg;
    t.style.cssText = 'position:fixed;left:50%;bottom:28px;transform:translateX(-50%);background:#3d2a2a;color:#f5e6e6;padding:12px 18px;border-radius:8px;font-size:14px;z-index:9999;max-width:90vw;';
    document.body.appendChild(t);
    setTimeout(function(){ t.remove(); }, 4500);
  }
  function conectarBotones(btnPdf, btnWord){
    if(btnPdf) btnPdf.addEventListener('click', conBoton(btnPdf, descargarPDF, 'PDF'));
    if(btnWord) btnWord.addEventListener('click', conBoton(btnWord, descargarWord, 'Word'));
  }

  global.OVPExport = { descargarPDF: descargarPDF, descargarWord: descargarWord, generarPDF: generarPDF, generarWord: generarWord, conectarBotones: conectarBotones };
})(window);
