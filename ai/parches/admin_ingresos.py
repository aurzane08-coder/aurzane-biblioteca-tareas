"""Pestaña «Ingresos» en aurzane.com/admin.html (18/11/2026).
Todas las formas en que AURZANE gana dinero, en un solo sitio: qué es cada una, por dónde y cuándo paga, el mínimo para cobrar,
cómo va (cifras reales de los últimos 30 días cuando la fuente lo permite) y un botón para abrir su panel.
Cifras: aurzane.com/panel/datos.php (clics hacia tiendas y ventas de Awin) y patrocinio.php?admin=1 (patrocinios de Stripe).
Amazon México no se incluye: no está aceptando afiliados.
Se aplica en el servidor sobre el admin.html vivo y es repetible (quita y vuelve a poner sus bloques). Va después de los otros
parches del admin en el mismo flujo. Copia previa en aurzane.com/eliminar/admin-ingresos-FECHA/."""
import os, re, sys, shutil, datetime
base = os.path.expanduser('~/' + (sys.argv[1] if len(sys.argv) > 1 else 'www')); hoy = datetime.date.today().strftime('%Y%m%d')
f = os.path.join(base, 'aurzane.com', 'public_html', 'admin.html')
s = open(f, encoding='utf-8').read(); t = s

NAV = '''      <div class="nav-item" data-page="ingresos">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M3 17l5-5 4 4 8-8"/><path d="M15 8h5v5"/></svg>
        <span class="nav-label">Ingresos</span>
      </div>
'''
PAGE = '''    <!-- INGRESOS (admin_ingresos) -->
    <div class="page" id="page-ingresos">
      <div class="page-head"><h2>Ingresos</h2><p>Todas las formas en que AURZANE gana dinero: cómo van, por dónde te pagan y qué falta para cobrar. Las cifras son reales y se actualizan solas.</p></div>
      <div class="ig-kpis" id="igKpis"><div class="ig-k"><span>Cargando las cifras…</span></div></div>
      <div class="ig-dos">
        <div class="panel"><div class="panel-head"><h3>Clics hacia tiendas y socios</h3><small class="ig-sub">últimos 30 días</small></div><div id="igClics" class="ig-barras"></div></div>
        <div class="panel"><div class="panel-head"><h3>Para poder cobrar</h3><small class="ig-sub">marca lo que ya tengas hecho</small></div><div id="igLista"></div></div>
      </div>
      <div class="panel">
        <div class="panel-head"><h3>Fuentes de ingresos</h3><button class="btn-ghost" style="width:auto;" id="igRecargar">Actualizar</button></div>
        <div class="table-scroll"><table>
          <thead><tr><th>Fuente</th><th>Cómo va</th><th>Cómo te paga</th><th>Cuándo y mínimo</th><th></th></tr></thead>
          <tbody id="igTabla"></tbody>
        </table></div>
        <p class="ig-nota">Los mínimos y plazos son los habituales de cada programa; si alguno cambia, manda lo que diga su panel. Todo es ingreso que se declara en España.</p>
      </div>
    </div>
'''
SCRIPT = r'''<style id="azIngresos">
.ig-kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:14px;margin-bottom:22px}
.ig-k{background:var(--navy-2);border:1px solid var(--line);border-radius:16px;padding:16px 18px}
.ig-k b{display:block;font-family:"Bodoni Moda",serif;font-size:1.7rem;color:var(--gold-light);line-height:1.1}
.ig-k span{display:block;font-size:.84rem;margin-top:4px}.ig-k small{display:block;color:var(--silver-dim);font-size:.74rem;margin-top:2px}
.ig-dos{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:18px}
.ig-sub{color:var(--silver-dim);font-size:.76rem}
.ig-barras .ig-b{display:grid;grid-template-columns:minmax(90px,150px) 1fr 44px;gap:10px;align-items:center;font-size:.84rem;margin:7px 0}
.ig-b span:first-child{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.ig-b .t{height:10px;border-radius:99px;background:var(--navy-3,rgba(255,255,255,.06));overflow:hidden}
.ig-b .t i{display:block;height:100%;border-radius:99px;background:var(--gold)}.ig-b b{text-align:right;font-variant-numeric:tabular-nums}
.ig-check{display:flex;gap:10px;align-items:flex-start;padding:8px 0;border-bottom:1px solid var(--line);font-size:.86rem;cursor:pointer}
.ig-check:last-child{border-bottom:0}.ig-check input{margin-top:3px;accent-color:var(--gold)}.ig-check small{display:block;color:var(--silver-dim);font-size:.76rem}
.ig-check.hecho span{text-decoration:line-through;opacity:.55}
#igTabla td{vertical-align:top;font-size:.84rem}#igTabla td small{display:block;color:var(--silver-dim);font-size:.76rem;margin-top:2px}
.ig-nota{color:var(--silver-dim);font-size:.78rem;margin:12px 0 0}
.ig-vacio{color:var(--silver-dim);font-size:.86rem}
</style>
<script>
/* Ingresos (admin_ingresos, 18/11/2026) */
(function(){
  var $ = function(i){ return document.getElementById(i); };
  var E = function(x){ return String(x == null ? '' : x).replace(/[&<>"']/g, function(c){ return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]; }); };
  var N = function(n){ return (+n || 0).toLocaleString('es-ES'); };
  var EUR = function(n, m){ return (+n || 0).toLocaleString('es-ES', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + ' ' + (m === 'USD' ? '$' : '€'); };
  /* [clave, nombre, qué es, cómo paga, cuándo y mínimo, panel] */
  var F = [
    ['stripe', 'Stripe', 'Patrocinios de universidades en NEXUS (y pagos de OVP más adelante). Tarjeta, Google Pay, Apple Pay, Revolut, Klarna, SEPA…', 'Transferencia a tu banco', 'Automático, unos días después de cada cobro', 'https://dashboard.stripe.com/payouts'],
    ['kofi', 'Ko-fi', 'Donaciones de quien quiere apoyar AURZANE', 'Entra en tu Stripe', 'Al momento', 'https://ko-fi.com/manage/supportreceived'],
    ['adsense', 'Google AdSense', 'Anuncios en las páginas públicas', 'Transferencia en euros', 'Una vez al mes, desde 70 €', 'https://adsense.google.com/adsense/'],
    ['amazon', 'Amazon Afiliados España', 'Libros y productos de la tienda y la biblioteca', 'Transferencia en euros', 'Unos 60 días tras cerrar el mes, desde 25 €', 'https://afiliados.amazon.es/home/reports'],
    ['amazonus', 'Amazon Afiliados EE. UU.', 'Los mismos enlaces, para quien entra desde Estados Unidos', 'Transferencia si la admite para España; si no, tarjeta regalo', 'Unos 60 días; requiere el formulario fiscal W-8BEN', 'https://affiliate-program.amazon.com/home/reports'],
    ['awin', 'Awin', 'SaludOnNet, Casa del Libro, Fnac, Naturitas, Myprotein, Decathlon y más socios junto a cada herramienta', 'Transferencia en euros', 'Dos veces al mes, desde unos 20 €, cuando la tienda ha pagado a Awin', 'https://ui.awin.com/'],
    ['udemy', 'Impact (Udemy)', 'Cursos de pago de Udemy al final de cada curso de LEARN', 'Transferencia o PayPal', 'Mensual, desde el mínimo que elijas', 'https://app.impact.com/'],
    ['paypal', 'PayPal (en Stripe)', 'Pagar con PayPal en la página de pago de Stripe', 'Al saldo de Stripe', 'Falta una cuenta de PayPal Business registrada en España', ''],
    ['youtube', 'YouTube', 'Programa de socios del canal AURZANE', 'Por tu misma cuenta de AdSense', 'Desde 1.000 suscriptores y 4.000 horas vistas (o 10 millones de vistas de Shorts)', 'https://studio.youtube.com/'],
    ['tiktok', 'TikTok', 'Creator Rewards (vídeos de más de 1 minuto)', 'Banco o PayPal', 'Desde 10.000 seguidores y 100.000 vistas en 30 días', 'https://www.tiktok.com/tiktokstudio']
  ];
  var LISTA = [
    ['banco-stripe', 'Cuenta bancaria añadida en Stripe', 'Sin ella, lo cobrado se queda retenido en Stripe', 'https://dashboard.stripe.com/settings/payouts'],
    ['fiscal-adsense', 'Datos fiscales y de pago en AdSense', 'Te los pide al acercarte a los 70 €', 'https://adsense.google.com/adsense/'],
    ['banco-amazon', 'Forma de pago en Amazon Afiliados España', 'Cuenta bancaria e información fiscal', 'https://afiliados.amazon.es/home/account'],
    ['w8-amazonus', 'Formulario W-8BEN en Amazon EE. UU.', 'Sin él no te paga', 'https://affiliate-program.amazon.com/home/account'],
    ['banco-awin', 'Cuenta bancaria en Awin', 'Pagos, detalles de pago', 'https://ui.awin.com/'],
    ['banco-impact', 'Forma de pago y datos fiscales en Impact', 'Para cobrar lo de Udemy', 'https://app.impact.com/'],
    ['paypal-es', 'PayPal Business registrada en España', 'Para añadir PayPal a los pagos de Stripe', 'https://www.paypal.com/es/business'],
    ['gestor', 'Hablar con el gestor del IVA y la declaración', 'Antes de que los ingresos sean regulares', '']
  ];
  var HECHO = {}; try { HECHO = JSON.parse(localStorage.getItem('azIngresosHecho') || '{}'); } catch(e) {}
  var PAN = null, PT = null;
  async function token(){ var sb = window.__aurzaneSb; return sb ? (await sb.auth.getSession()).data.session?.access_token : ''; }
  async function cargar(){
    var tk = await token(); if(!tk) return;
    try { var r = await (await fetch('https://aurzane.com/panel/datos.php', { method:'POST', headers:{ 'Content-Type':'application/json' }, body: JSON.stringify({ token: tk }) })).json(); if(!r.error) PAN = r; } catch(e) {}
    try { var p = await fetch('/patrocinio.php?admin=1', { method:'POST', cache:'no-store', headers:{ Authorization:'Bearer ' + tk, 'Content-Type':'application/json' }, body:'{}' }); if(p.ok) PT = await p.json(); } catch(e) {}
    pintar();
  }
  function clicsDe(re){ var l = ((PAN || {}).clics_compra || {}).por_tienda || []; return l.filter(function(x){ return re.test(x[0]); }).reduce(function(a, x){ return a + (+x[1] || 0); }, 0); }
  function estado(k){
    var aw = (PAN || {}).awin || {}, pl = (PT || {}).lista || [];
    var act = pl.filter(function(s){ return s.estado === 'activo' || s.estado === 'prueba'; }).length, pag = pl.filter(function(s){ return s.estado === 'activo' && s.stripe_sub && !s.cancelada; }).length;
    if(k === 'stripe') return PT ? (PT.stripe ? '<span class="status-pill paid">Conectado</span>' : '<span class="status-pill pending">Falta la clave</span>') + '<small>' + N(act) + ' universidades destacadas, ' + N(pag) + ' pagando con Stripe</small>' : '<small>Sin datos todavía</small>';
    if(k === 'awin') return aw.error ? '<small>' + E(aw.error) + '</small>' : '<span class="status-pill paid">' + N(aw.programas_activos) + ' socios activos</span><small>' + N(aw.ventas_30_dias) + ' ventas, ' + EUR(aw.comision_30_dias) + ' de comisión en 30 días</small><small>' + N(clicsDe(/^(?!Amazon$|udemy$)/i)) + ' clics hacia socios</small>';
    if(k === 'amazon') return '<span class="status-pill paid">Activo</span><small>' + N(clicsDe(/^Amazon$/i)) + ' clics hacia Amazon en 30 días</small><small>Las ventas se ven en su panel</small>';
    if(k === 'amazonus') return '<span class="status-pill paid">Activo</span><small>Visitantes desde EE. UU.</small>';
    if(k === 'udemy') return '<span class="status-pill paid">Aceptado</span><small>' + N(clicsDe(/udemy/i)) + ' clics hacia Udemy en 30 días</small>';
    if(k === 'kofi') return '<span class="status-pill paid">Activo</span>';
    if(k === 'adsense') return '<span class="status-pill pending">En revisión</span><small>Anuncios automáticos ya puestos</small>';
    if(k === 'paypal') return '<span class="status-pill pending">Pendiente</span>';
    if(k === 'youtube' || k === 'tiktok'){ var r = (((PAN || {}).seguidores || {}).redes || []).filter(function(x){ return String(x[0]).toLowerCase().indexOf(k) === 0; })[0]; return '<span class="status-pill pending">Creciendo</span>' + (r && r[1] != null ? '<small>' + N(r[1]) + ' seguidores</small>' : ''); }
    return '';
  }
  function pintar(){
    if(!$('igTabla')) return;
    var aw = (PAN || {}).awin || {}, cc = (PAN || {}).clics_compra || {}, pl = (PT || {}).lista || [];
    var pag = pl.filter(function(s){ return s.estado === 'activo' && s.stripe_sub && !s.cancelada; }).length;
    $('igKpis').innerHTML = [
      [aw.error ? '–' : EUR(aw.comision_30_dias), 'Comisión de Awin', '30 días, ' + N(aw.ventas_30_dias) + ' ventas'],
      [N(cc.total_30_dias), 'Clics hacia tiendas y socios', '30 días, todas las fuentes'],
      [N(pag), 'Universidades pagando', 'Suscripción activa en Stripe'],
      [N(aw.programas_activos), 'Socios de Awin activos', 'Más Amazon y Udemy']
    ].map(function(k){ return '<div class="ig-k"><b>' + E(k[0]) + '</b><span>' + E(k[1]) + '</span><small>' + E(k[2]) + '</small></div>'; }).join('');
    var l = (cc.por_tienda || []).slice(0, 10), mx = Math.max.apply(null, l.map(function(x){ return +x[1] || 0; }).concat([1]));
    $('igClics').innerHTML = l.length ? l.map(function(x){ return '<div class="ig-b"><span title="' + E(x[0]) + '">' + E(x[0]) + '</span><span class="t"><i style="width:' + Math.max(2, x[1] / mx * 100) + '%"></i></span><b>' + N(x[1]) + '</b></div>'; }).join('') : '<p class="ig-vacio">Todavía no hay clics hacia tiendas en los últimos 30 días.</p>';
    $('igLista').innerHTML = LISTA.map(function(x){ var h = !!HECHO[x[0]]; return '<label class="ig-check' + (h ? ' hecho' : '') + '"><input type="checkbox" data-ig="' + x[0] + '"' + (h ? ' checked' : '') + '><span>' + E(x[1]) + '<small>' + E(x[2]) + (x[3] ? ' · <a href="' + E(x[3]) + '" target="_blank" rel="noopener" style="color:var(--gold-light)">Abrir</a>' : '') + '</small></span></label>'; }).join('');
    $('igTabla').innerHTML = F.map(function(x){ return '<tr><td><b>' + E(x[1]) + '</b><small>' + E(x[2]) + '</small></td><td>' + estado(x[0]) + '</td><td>' + E(x[3]) + '</td><td>' + E(x[4]) + '</td><td>' + (x[5] ? '<a class="btn-mini" href="' + E(x[5]) + '" target="_blank" rel="noopener">Abrir panel</a>' : '') + '</td></tr>'; }).join('');
  }
  document.addEventListener('change', function(ev){ var c = ev.target.closest('[data-ig]'); if(!c) return; HECHO[c.dataset.ig] = c.checked; try { localStorage.setItem('azIngresosHecho', JSON.stringify(HECHO)); } catch(e) {} c.closest('.ig-check').classList.toggle('hecho', c.checked); });
  var nav = document.querySelector('.nav-item[data-page="ingresos"]'); if(nav) nav.addEventListener('click', cargar);
  var rc = $('igRecargar'); if(rc) rc.addEventListener('click', cargar);
  pintar(); if(location.hash === '#ingresos') setTimeout(cargar, 2500);
})();
</script>
'''
if 'data-page="ingresos"' not in t:
    ancla = '      <div class="nav-item" data-page="usuarios">'
    if ancla in t: t = t.replace(ancla, NAV + ancla, 1)
if 'id="page-ingresos"' not in t and '    <!-- USUARIOS -->' in t:
    t = t.replace('    <!-- USUARIOS -->', PAGE + '    <!-- USUARIOS -->', 1)
# en el grupo «Hoy» del menú, después de Resultados
t = t.replace("['Hoy', ['resumen','reportes','ai','resultados']]", "['Hoy', ['resumen','reportes','ai','resultados','ingresos']]")
t = re.sub(r'<style id="azIngresos">.*?</style>\n<script>\n/\* Ingresos \(admin_ingresos.*?</script>\n', '', t, flags=re.S)
if '</body>' in t:
    i = t.rindex('</body>'); t = t[:i] + SCRIPT + t[i:]
if t != s:
    c = os.path.join(base, 'aurzane.com', 'eliminar', 'admin-ingresos-' + hoy); os.makedirs(c, exist_ok=True)
    if not os.path.exists(os.path.join(c, 'admin.html')): shutil.copy2(f, c)
    open(f + '.tmp', 'w', encoding='utf-8').write(t); os.replace(f + '.tmp', f)
    print('::notice::admin.html con la pestaña Ingresos')
else:
    print('admin.html ya tenía Ingresos')
