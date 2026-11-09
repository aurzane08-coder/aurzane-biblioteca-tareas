/* Panel de resultados de AURZANE: visitas, boletín, ventas, redes y Google. Lo usa la pestaña «Resultados» de admin.html.
   AurzanePanel.pintar(contenedor, tokenDeSesion): pide /panel/datos.php (solo administradores) y lo dibuja. */
(function (w, d) {
  if (w.AurzanePanel) return;
  var st = d.createElement('style'); st.textContent = '.azp{--bg:#080B17;--sup:#0F1530;--sup2:#151C3D;--txt:#F5F3EE;--sua:#9AA1B2;--oro:#C9A24B;--oro2:#EACF92;--lin:rgba(199,205,214,.13);--ok:#8CC084;--mal:#E39B9B;--s1:#7FA7E8;--s2:#C9A24B}.azp a{color:var(--oro2)}.azp h2{font:500 1.15rem "Bodoni Moda",serif;margin-bottom:12px}.azp .sub{color:var(--sua);margin-bottom:22px}.azp .kpis{display:grid;grid-template-columns:repeat(auto-fill,minmax(170px,1fr));gap:12px;margin-bottom:22px}.azp .kpi{background:var(--sup);border:1px solid var(--lin);border-radius:14px;padding:14px 16px}.azp .kpi b{display:block;font-size:1.65rem;font-variant-numeric:tabular-nums;line-height:1.2}.azp .kpi span{color:var(--sua);font-size:.84rem}.azp .kpi i{font-style:normal;font-size:.8rem;margin-left:6px}.azp .sube{color:var(--ok)}.azp .baja{color:var(--mal)}.azp .rej{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:16px}.azp .caja{background:var(--sup);border:1px solid var(--lin);border-radius:14px;padding:18px;min-width:0}.azp .caja.ancha{grid-column:1/-1}.azp table{width:100%;border-collapse:collapse;font-size:.88rem}.azp td,.azp th{padding:6px 4px;border-bottom:1px solid var(--lin);text-align:left;vertical-align:top}.azp th{color:var(--sua);font-weight:600}.azp td.n{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}.azp td.url{word-break:break-all}.azp .vacio{color:var(--sua);font-size:.9rem}.azp .aviso{background:rgba(201,162,75,.1);border:1px solid rgba(201,162,75,.35);color:var(--oro2);border-radius:10px;padding:10px 14px;margin-bottom:14px;font-size:.9rem}.azp .leyenda{display:flex;gap:16px;font-size:.82rem;color:var(--sua);margin-bottom:6px}.azp .leyenda i{display:inline-block;width:10px;height:10px;border-radius:2px;margin-right:6px;vertical-align:middle}.azp svg text{fill:var(--sua);font-size:11px}.azp .barra{height:8px;border-radius:4px;background:var(--sup2);position:relative;min-width:60px}.azp .barra i{position:absolute;inset:0;width:var(--v);background:var(--oro);border-radius:4px}.azp .rej{grid-template-columns:1fr}@media(max-width:800px){.azp .rej{grid-template-columns:1fr}}'; d.head.appendChild(st);
  var E = function(s){ return String(s == null ? '' : s).replace(/[&<>"]/g, function(c){ return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]; }); };
  var N = function(n){ return n == null ? '—' : Number(n).toLocaleString('es-ES'); };
  function dibujar(app, P) {
  function tabla(filas, cab, fmt){
    if(!filas || !filas.length) return '<p class="vacio">Sin datos todavía.</p>';
    var max = Math.max.apply(null, filas.map(function(f){ return +f[1] || 0; })) || 1;
    return '<table><tr>' + cab.map(function(c, i){ return '<th' + (i ? ' style="text-align:right"' : '') + '>' + E(c) + '</th>'; }).join('') + '</tr>' + filas.map(function(f){
      return '<tr><td class="url">' + (fmt ? fmt(f[0]) : E(f[0])) + '</td>' + f.slice(1).map(function(v, i){ return '<td class="n">' + (i === 0 && typeof v === 'number' ? N(v) : E(v)) + '</td>'; }).join('') + '</tr>';
    }).join('') + '</table>';
  }
  function enlace(u){ return '<a href="https://' + E(u) + '" target="_blank" rel="noopener">' + E(u.replace(/^aurzane\.com/, '')) + '</a>'; }
  function grafica(dias){
    if(!dias || dias.length < 2) return '<p class="vacio">Hacen falta al menos dos días de registros.</p>';
    var W = 1000, H = 220, pl = 40, pb = 24, max = Math.max.apply(null, dias.map(function(d){ return d.paginas; })) || 1;
    var x = function(i){ return pl + i * (W - pl - 10) / (dias.length - 1); }, y = function(v){ return H - pb - v / max * (H - pb - 12); };
    var linea = function(k){ return dias.map(function(d, i){ return (i ? 'L' : 'M') + x(i).toFixed(1) + ' ' + y(d[k]).toFixed(1); }).join(''); };
    var marcas = [0, Math.round(max / 2), max].map(function(v){ return '<line x1="' + pl + '" x2="' + W + '" y1="' + y(v) + '" y2="' + y(v) + '" stroke="rgba(199,205,214,.1)"/><text x="' + (pl - 6) + '" y="' + (y(v) + 4) + '" text-anchor="end">' + N(v) + '</text>'; }).join('');
    var et = dias.map(function(d, i){ return (i % Math.ceil(dias.length / 8) === 0 || i === dias.length - 1) ? '<text x="' + x(i) + '" y="' + (H - 6) + '" text-anchor="' + (i === dias.length - 1 ? 'end' : 'middle') + '">' + d.dia.slice(8) + '/' + d.dia.slice(5, 7) + '</text>' : ''; }).join('');
    var puntos = dias.map(function(d, i){ return '<circle cx="' + x(i) + '" cy="' + y(d.visitantes) + '" r="3" fill="var(--s1)"><title>' + d.dia + ': ' + d.visitantes + ' visitantes, ' + d.paginas + ' páginas</title></circle>'; }).join('');
    return '<div class="leyenda"><span><i style="background:var(--s1)"></i>Visitantes</span><span><i style="background:var(--s2)"></i>Páginas vistas</span></div>' +
      '<svg viewBox="0 0 ' + W + ' ' + H + '" width="100%" role="img" aria-label="Visitantes y páginas vistas por día">' + marcas + et +
      '<path d="' + linea('paginas') + '" fill="none" stroke="var(--s2)" stroke-width="2"/><path d="' + linea('visitantes') + '" fill="none" stroke="var(--s1)" stroke-width="2.5"/>' + puntos + '</svg>';
  }

  var V = P.visitas || {}, dias = V.por_dia || [];
  var suma = function(a, k){ return a.reduce(function(s, d){ return s + (d[k] || 0); }, 0); };
  var u7 = suma(dias.slice(-7), 'visitantes'), u7p = suma(dias.slice(-14, -7), 'visitantes');
  var cambio = function(a, b){ if(!b) return ''; var p = Math.round((a - b) / b * 100); return '<i class="' + (p >= 0 ? 'sube' : 'baja') + '">' + (p >= 0 ? '+' : '') + p + ' %</i>'; };
  var seg = (P.seguidores && P.seguidores.redes) || [];
  var totalSeg = seg.reduce(function(s, r){ return s + (r[1] || 0); }, 0);
  var B = P.boletin || {}, CC = P.clics_compra || {}, AW = P.awin || {}, CR = P.clics_redes || {}, COL = P.colegios || {};

  var h = '<p class="sub">Actualizado: ' + new Date(P.generado).toLocaleString('es-ES') + '. Se recalcula cada mañana.</p>';
  (P.avisos || []).forEach(function(a){ h += '<p class="aviso">' + E(a) + '</p>'; });
  h += '<div class="kpis">' +
    '<div class="kpi"><b>' + N(u7) + cambio(u7, u7p) + '</b><span>Visitantes, últimos 7 días</span></div>' +
    '<div class="kpi"><b>' + N(suma(dias.slice(-30), 'paginas')) + '</b><span>Páginas vistas, 30 días</span></div>' +
    '<div class="kpi"><b>' + N(B.suscritos) + '</b><span>Suscriptores del boletín' + (B.pendientes ? ' (' + N(B.pendientes) + ' sin confirmar)' : '') + '</span></div>' +
    '<div class="kpi"><b>' + N(CC.total_30_dias) + '</b><span>Clics hacia tiendas, 30 días</span></div>' +
    '<div class="kpi"><b>' + (AW.error ? '—' : N(AW.ventas_30_dias)) + '</b><span>Ventas Awin, 30 días' + (AW.comision_30_dias ? ' · ' + N(AW.comision_30_dias) + ' €' : '') + '</span></div>' +
    '<div class="kpi"><b>' + N(totalSeg) + '</b><span>Seguidores en redes</span></div>' +
    '<div class="kpi"><b>' + N(CR.total_30_dias) + '</b><span>Clics desde redes, 30 días</span></div>' +
    '<div class="kpi"><b>' + N(COL.solicitudes) + '</b><span>Solicitudes de colegios' + (COL.nuevas ? ' (' + COL.nuevas + ' nuevas)' : '') + '</span></div>' +
  '</div>';
  h += '<div class="rej"><div class="caja ancha"><h2>Visitas por día</h2>' + grafica(dias) + '</div>' +
    '<div class="caja"><h2>Páginas más vistas, 7 días</h2>' + tabla(V.top_7_dias, ['Página', 'Vistas'], enlace) + '</div>' +
    '<div class="caja"><h2>Páginas más vistas, 30 días</h2>' + tabla(V.top_30_dias, ['Página', 'Vistas'], enlace) + '</div>' +
    '<div class="caja"><h2>Visitantes por sitio</h2>' + tabla(V.por_dominio, ['Sitio', 'Visitantes']) + '</div>' +
    '<div class="caja"><h2>Boletín: altas por mes</h2>' + tabla((B.altas_por_mes || []).slice().reverse(), ['Mes', 'Altas']) + '</div>' +
    '<div class="caja"><h2>Clics hacia tiendas</h2>' + tabla(CC.por_tienda, ['Tienda', 'Clics']) + '<p class="vacio" style="margin-top:10px">' + E((P.amazon || {}).nota || '') + '</p></div>' +
    '<div class="caja"><h2>Páginas que más venden (clics)</h2>' + tabla(CC.paginas, ['Página', 'Clics'], enlace) + '</div>' +
    '<div class="caja"><h2>Ventas en Awin, 30 días</h2>' + (AW.error ? '<p class="vacio">' + E(AW.error) + '</p>' : tabla((AW.por_tienda || []).map(function(t){ return [t[0], t[1], N(t[2]) + ' ' + E(t[3])]; }), ['Tienda', 'Ventas', 'Comisión'])) +
      (AW.programas_activos != null ? '<p class="vacio" style="margin-top:10px">Programas de Awin aprobados: ' + N(AW.programas_activos) + '</p>' : '') + '</div>' +
    '<div class="caja"><h2>Seguidores por red</h2>' + tabla(seg.map(function(r){ return [r[0], r[1] == null ? 'sin permiso de lectura' : r[1], r[2] == null ? '' : (r[2] >= 0 ? '+' : '') + r[2]]; }), ['Red', 'Seguidores', '30 días']) + '</div>' +
    '<div class="caja"><h2>Clics desde redes por red</h2>' + tabla(CR.por_red, ['Red', 'Clics']) + '</div>' +
    '<div class="caja"><h2>Publicaciones con más clics</h2>' + tabla(CR.contenidos, ['Contenido', 'Clics']) + '</div>' +
    '<div class="caja ancha"><h2>Solicitudes de colegios</h2>' + tabla((COL.ultimas || []).map(function(c){ return [c[1] + ' · ' + c[2], c[3], c[0]]; }), ['Colegio', 'Cargo', 'Fecha']) + '</div>' +
    '<div class="caja ancha"><h2>Contenido</h2><table><tr><td>Libros en la tienda</td><td class="n">' + N(P.tienda_total) + '</td></tr><tr><td>Libros de pago elegidos</td><td class="n">' + N(P.tienda_libros) + '</td></tr><tr><td>Libros publicados en Telegram</td><td class="n">' + N(P.telegram_libros) + ' de 365</td></tr></table></div>' +
  '</div>';
  var S = P.seo || {};
  h += '<div class="rej"><div class="caja ancha"><h2>Google (Search Console)</h2>' + (S.conectado ? '<p class="vacio" style="margin-bottom:10px">' + N(S.clics) + ' clics y ' + N(S.impresiones) + ' impresiones entre ' + E((S.periodo || [])[0]) + ' y ' + E((S.periodo || [])[1]) + '.</p>' +
    '<div class="rej" style="margin:0"><div>' + tabla((S.consultas || []).slice(0, 15).map(function(q){ return [q[0], q[1], N(q[2]), q[3]]; }), ['Búsqueda', 'Clics', 'Impresiones', 'Posición']) + '</div>' +
    '<div>' + tabla((S.paginas || []).slice(0, 15).map(function(q){ return [q[0].replace(/^https?:\/\//, ''), q[1], N(q[2]), q[3]]; }), ['Página', 'Clics', 'Impresiones', 'Posición'], enlace) + '</div></div>' +
    '<h2 style="margin-top:18px">Títulos mejorados por la IA</h2>' + tabla((S.cambios_titulos || []).map(function(c){ return [c[1].replace(/^https?:\/\//, ''), c[3], c[0]]; }), ['Página', 'Título nuevo', 'Fecha'], enlace) +
    '<h2 style="margin-top:18px">Artículos en cola por lo que la gente busca</h2>' + tabla((S.temas_nuevos || []).map(function(t){ return [t[2], t[1], t[0]]; }), ['Artículo', 'Búsqueda', 'Fecha'])
    : '<p class="vacio">' + E(S.aviso || 'Search Console todavía no está conectado.') + ' <a href="https://aurzane.com/youtube/?cuenta=gsc" target="_blank" rel="noopener">Conectar ahora</a></p>') + '</div></div>';
  app.innerHTML = h;
  }
  w.AurzanePanel = { pintar: function (app, token) {
    app.classList.add('azp'); app.innerHTML = '<p class="vacio">Cargando resultados…</p>';
    return fetch('https://aurzane.com/panel/datos.php', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ token: token }) })
      .then(function (r) { return r.json(); })
      .then(function (P) { if (P.error) { app.innerHTML = '<p class="vacio">' + E(P.error) + '</p>'; return; } dibujar(app, P); })
      .catch(function () { app.innerHTML = '<p class="vacio">No se pudo cargar el panel. Vuelve a intentarlo en un momento.</p>'; });
  } };
})(window, document);
