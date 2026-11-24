"""Clientes de OVP en aurzane.com/admin.html: si abrieron su informe y cuántas veces lo descargaron (24/11/2026).
El portal guarda en la ficha de cada cliente cuándo abrió «Mi informe» por primera vez (informe_visto_at) y cada descarga en PDF o
Word (informe_descargado_at, informe_descargas), con la función ovp_marcar_informe de Supabase. Este parche añade a la tabla de
Clientes una columna «Informe» con ese dato y, encima de la tabla, un resumen: cuántos lo tienen, cuántos lo abrieron y cuántas
descargas hubo. Lee con la sesión del propio admin (window.__aurzaneSb); no cambia nada de la tabla original.
Se aplica en el servidor sobre el admin.html vivo y es repetible (quita y vuelve a poner su bloque).
Copia previa en aurzane.com/eliminar/admin-informe-FECHA/."""
import os, re, sys, shutil, datetime
base = os.path.expanduser('~/' + (sys.argv[1] if len(sys.argv) > 1 else 'www')); hoy = datetime.date.today().strftime('%Y%m%d')
f = os.path.join(base, 'aurzane.com', 'public_html', 'admin.html')
s = open(f, encoding='utf-8').read(); t = s

BLOQUE = r'''<!--az-informe-ovp--><style>
.az-inf-res{display:flex;flex-wrap:wrap;gap:10px;margin:0 0 14px}
.az-inf-res span{background:var(--navy-2);border:1px solid var(--line);border-radius:12px;padding:8px 14px;font-size:.84rem}
.az-inf-res b{font-family:"Bodoni Moda",serif;font-size:1.15rem;margin-right:6px;color:var(--gold-light)}
td.az-inf{font-size:.78rem;white-space:nowrap}
td.az-inf .ok{color:var(--ok)} td.az-inf .no{color:var(--silver-dim)}
</style>
<script>
(function () {
  var datos = null, cargando = false;
  function fecha(x) { return x ? new Date(x).toLocaleDateString('es-ES', { day: '2-digit', month: 'short' }) : ''; }
  function celda(c) {
    if (!c) return '<span class="no">—</span>';
    var hechas = (c.activaciones || []).some(function (a) { return a.completado; });
    if (!hechas) return '<span class="no">Aún sin informe</span>';
    if (!c.informe_visto_at && !c.informe_descargas) return '<span class="no">Sin abrir</span>';
    return '<span class="ok">Abierto ' + fecha(c.informe_visto_at || c.informe_descargado_at) + '</span>' +
      (c.informe_descargas ? '<br>' + c.informe_descargas + (c.informe_descargas === 1 ? ' descarga' : ' descargas') + ', última ' + fecha(c.informe_descargado_at) : '<br><span class="no">sin descargar</span>');
  }
  function resumen() {
    var page = document.getElementById('page-clientes'), tabla = page && page.querySelector('table');
    if (!tabla || !datos) return;
    var con = 0, abiertos = 0, desc = 0, quien = 0;
    Object.keys(datos).forEach(function (k) {
      var c = datos[k]; if (c.eliminado_at) return;
      if ((c.activaciones || []).some(function (a) { return a.completado; })) con++;
      if (c.informe_visto_at || c.informe_descargas) abiertos++;
      if (c.informe_descargas) { quien++; desc += c.informe_descargas; }
    });
    var r = document.getElementById('azInfRes');
    if (!r) { r = document.createElement('div'); r.id = 'azInfRes'; r.className = 'az-inf-res'; var w = tabla.closest('.table-scroll') || tabla; w.parentNode.insertBefore(r, w); }
    r.innerHTML = '<span><b>' + con + '</b>tienen informe</span><span><b>' + abiertos + '</b>lo abrieron</span><span><b>' + quien + '</b>lo descargaron (' + desc + (desc === 1 ? ' descarga' : ' descargas') + ')</span>' +
      '<span style="color:var(--silver-dim)">Se registra desde el 24/11/2026: lo anterior no consta.</span>';
  }
  function pintar() {
    var cuerpo = document.getElementById('clientsTableBody'); if (!cuerpo || !datos) return;
    var cab = document.querySelector('#page-clientes thead tr');
    var papelera = cab && /Eliminado/.test(cab.textContent);
    if (cab && !papelera && !cab.querySelector('.az-inf-th')) { var th = document.createElement('th'); th.className = 'az-inf-th'; th.textContent = 'Informe'; cab.appendChild(th); }
    if (papelera) return;
    [].forEach.call(cuerpo.querySelectorAll('tr.client-row'), function (tr) {
      if (tr.querySelector('td.az-inf')) return;
      var td = document.createElement('td'); td.className = 'az-inf'; td.innerHTML = celda(datos[tr.getAttribute('data-id')]); tr.appendChild(td);
    });
    resumen();
  }
  function cargar() {
    if (cargando || datos || !window.__aurzaneSb) return; cargando = true;
    window.__aurzaneSb.from('clientes').select('id,eliminado_at,informe_visto_at,informe_descargado_at,informe_descargas,activaciones(completado)').then(function (r) {
      cargando = false; if (r.error) { console.warn('informe OVP:', r.error.message); return; }
      datos = {}; (r.data || []).forEach(function (c) { datos[c.id] = c; }); pintar();
    });
  }
  function iniciar() {
    var cuerpo = document.getElementById('clientsTableBody'); if (!cuerpo || !window.MutationObserver) return;
    new MutationObserver(function () { if (cuerpo.querySelector('tr.client-row')) { if (datos) pintar(); else cargar(); } }).observe(cuerpo, { childList: true });
    var btn = document.getElementById('refreshBtn'); if (btn) btn.addEventListener('click', function () { datos = null; });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', iniciar); else iniciar();
})();
</script><!--/az-informe-ovp-->'''

s = re.sub(r'<!--az-informe-ovp-->[\s\S]*?<!--/az-informe-ovp-->', '', s)
s = s.replace('</body>', BLOQUE + '\n</body>', 1)
if s != t:
    copia = os.path.join(base, 'aurzane.com', 'eliminar', 'admin-informe-' + hoy, 'admin.html')
    os.makedirs(os.path.dirname(copia), exist_ok=True)
    if not os.path.exists(copia): shutil.copy2(f, copia)
    open(f, 'w', encoding='utf-8').write(s)
    print('admin.html: columna «Informe» de OVP puesta')
else:
    print('admin.html: sin cambios')
