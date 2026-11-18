"""Rediseño visual y de uso de todo admin.html (18/11/2026), sobre el admin.html vivo. Repetible: sustituye su bloque.
Basado en los patrones de los mejores paneles (Stripe, Linear, Grafana): una barra superior con dónde estás y las acciones
de siempre, tipografía y etiquetas legibles (sin mayúsculas diminutas), tablas con cabecera fija y números alineados,
desplegables con el mismo estilo oscuro, acciones peligrosas en rojo y separadas, modo compacto para tablas largas y,
en el móvil, un menú lateral completo que se abre con un botón. No cambia ninguna función ni dato del panel.
Corre después de admin_patrocinios.py y admin_mejoras.py (mismo flujo). Copia previa en aurzane.com/eliminar/admin-diseno-FECHA/."""
import os, re, sys, shutil, datetime
base = os.path.expanduser('~/' + (sys.argv[1] if len(sys.argv) > 1 else 'www')); hoy = datetime.date.today().strftime('%Y%m%d')
f = os.path.join(base, 'aurzane.com', 'public_html', 'admin.html')
s = open(f, encoding='utf-8').read()
t = re.sub(r'<style id="azDiseno">.*?</style>\n', '', s, flags=re.S)
t = re.sub(r'<script>\n/\* Diseño del panel \(admin_diseno.*?</script>\n', '', t, flags=re.S)

CSS = r'''<style id="azDiseno">
/* Diseño del panel (admin_diseno, 18/11/2026) */
body .main{padding:0 44px 60px;max-width:1320px}
body .page-head{margin:26px 0 28px}
body .page-head h2{font-size:2rem;line-height:1.15;margin-bottom:8px}
body .page-head p{font-size:.92rem;max-width:80ch;line-height:1.55}
/* barra superior */
.az-top{position:sticky;top:0;z-index:40;display:flex;align-items:center;gap:12px;padding:14px 0;margin:0 -2px;background:linear-gradient(var(--navy) 70%,rgba(8,11,23,0));backdrop-filter:blur(6px)}
.az-migas{flex:1;min-width:0;font-size:.82rem;color:var(--silver-dim);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.az-migas b{color:var(--bone);font-weight:600}
.az-top button,.az-top a{display:inline-flex;align-items:center;gap:6px;height:36px;padding:0 13px;border:1px solid var(--line);border-radius:10px;background:var(--navy-2);color:var(--silver);font:inherit;font-size:.8rem;cursor:pointer;white-space:nowrap}
.az-top button:hover,.az-top a:hover{border-color:var(--gold);color:var(--gold-light)}
.az-top .az-kbd{font-size:.68rem;padding:1px 6px;border:1px solid var(--line);border-radius:5px;color:var(--silver-dim)}
.az-menu{display:none!important}
/* etiquetas y tablas legibles */
body th{font-family:'Instrument Sans',sans-serif;font-size:.74rem;text-transform:none;letter-spacing:0;font-weight:600;color:var(--silver-dim);background:var(--navy-2);position:sticky;top:0;z-index:2;white-space:nowrap}
body td{font-variant-numeric:tabular-nums}
body .mono,body td .mono,body td em,body td i:not(.test-dot){font-family:'Instrument Sans',sans-serif;font-style:normal;font-weight:500}
body td,body td *{font-style:normal}
body tbody tr:hover td{background:rgba(255,255,255,.025)}
body .table-scroll{max-height:72vh;overflow:auto}
body .field label{font-family:'Instrument Sans',sans-serif;font-size:.78rem;text-transform:none;letter-spacing:0;font-weight:600;color:var(--silver)}
body .kpi-card .k-lbl{font-family:'Instrument Sans',sans-serif;font-size:.78rem;text-transform:none;letter-spacing:0;margin-top:10px}
body .kpi-card .k-num{font-size:2.1rem}
body .status-pill{font-family:'Instrument Sans',sans-serif;font-size:.72rem;font-weight:600;padding:3px 10px;border-radius:99px}
body .recent-row .r-meta,body .sidebar-footer .email,body .drawer-head .d-email{font-family:'Instrument Sans',sans-serif}
body .panel{border-radius:16px}
body .panel-head{padding:16px 22px}
body .panel-head h3{font-size:1.02rem}
/* formularios y desplegables con el mismo estilo */
body select,body .field select,body textarea,body .field textarea,body input[type=text],body input[type=email],body input[type=number],body input[type=url],body input[type=date],body input[type=search]{background-color:var(--navy-2);color:var(--bone);border:1px solid var(--line);border-radius:10px;font:inherit;font-size:.88rem}
body select{appearance:none;-webkit-appearance:none;padding:9px 34px 9px 12px;min-height:38px;background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%238B92A0' stroke-width='2'%3E%3Cpath d='M6 9l6 6 6-6'/%3E%3C/svg%3E");background-repeat:no-repeat;background-position:right 12px center;cursor:pointer}
body select:focus,body textarea:focus,body input:focus{outline:none;border-color:var(--gold)}
body select option{background:var(--navy-2);color:var(--bone)}
/* botones: jerarquía clara y peligro separado */
body .btn-mini{min-height:32px;padding:6px 12px;border-radius:9px;font-size:.76rem}
body .btn-mini.az-peligro,body .btn-ghost.az-peligro{color:#e3a0a0;border-color:rgba(201,112,112,.35)}
body .btn-mini.az-peligro:hover,body .btn-ghost.az-peligro:hover{background:rgba(201,112,112,.12);color:#f1b7b7;border-color:var(--err)}
body td .btn-mini.az-peligro{margin-left:10px}
body .btn-gold{border-radius:10px}
/* estados vacíos */
body .empty-state{padding:44px 20px;font-size:.9rem;line-height:1.6}
body .empty-state:before{content:"";display:block;width:42px;height:42px;margin:0 auto 12px;border-radius:12px;border:1px dashed var(--line-strong);opacity:.7}
/* modo compacto */
body.az-compacto td{padding:8px 16px;font-size:.82rem}
body.az-compacto th{padding:8px 16px}
body.az-compacto .panel{margin-bottom:18px}
/* menú lateral */
body .nav-item{border-radius:10px}
body .nav-item.active{box-shadow:inset 3px 0 0 var(--gold)}
/* móvil: menú completo que se abre con un botón */
@media(max-width:800px){
  body .shell.show{display:block}
  body .sidebar{position:fixed;left:0;top:0;bottom:0;width:270px;z-index:100;transform:translateX(-102%);transition:transform .25s var(--ease);box-shadow:var(--shadow-lift)}
  body.az-menu-abierto .sidebar{transform:none}
  body .nav-item span.nav-label,body .sidebar-footer .email{display:inline}
  body .nav-grupo{display:block!important}
  body .sidebar-brand{text-align:left;padding:22px 24px}
  body .sidebar-brand a span.full-name,body .sidebar-brand a span.brand-letters,body .sidebar-brand .tag{display:inline}
  .az-migas{visibility:hidden}
  #azTopAct{display:none!important}
  body .main{padding:0 16px 48px}
  .az-menu{display:inline-flex!important}
  .az-top .az-ocultable{display:none}
  .az-velo{position:fixed;inset:0;background:rgba(4,6,14,.55);z-index:99;display:none}
  body.az-menu-abierto .az-velo{display:block}
  body .page-head h2{font-size:1.6rem}
}
/* filtros rápidos */
.az-chips{display:flex;flex-wrap:wrap;gap:8px;margin:-4px 0 16px}
.az-chips button{padding:7px 13px;border-radius:99px;border:1px solid var(--line);background:transparent;color:var(--silver);font:inherit;font-size:.8rem;cursor:pointer}
.az-chips button b{margin-left:4px;color:var(--bone)}
.az-chips button[aria-pressed=true]{background:var(--navy-4);border-color:var(--gold);color:var(--gold-light)}
.az-ley{font-size:.76rem;color:var(--silver-dim);margin:-14px 0 24px;display:flex;align-items:center;gap:6px;flex-wrap:wrap}
.az-ley .test-dot{display:inline-block;margin-left:8px}
@media (prefers-reduced-motion:reduce){body .sidebar{transition:none}}
</style>
'''
JS = r'''<script>
/* Diseño del panel (admin_diseno, 18/11/2026): barra superior, móvil, peligro y modo compacto */
(function(){
  var main = document.querySelector('.main'); if(!main || document.querySelector('.az-top')) return;
  var top = document.createElement('div'); top.className = 'az-top';
  top.innerHTML = '<button class="az-menu" type="button" aria-label="Abrir el menú">☰ Menú</button><div class="az-migas" id="azMigas"></div>'
    + '<button type="button" id="azTopBuscar" aria-label="Buscar sección">Buscar <span class="az-kbd">Ctrl K</span></button>'
    + '<button type="button" id="azTopAct" title="Volver a cargar esta sección">↻ Actualizar</button>'
    + '<button type="button" id="azTopDens" class="az-ocultable" title="Filas más juntas en las tablas">Compacto</button>'
    + '<a href="https://aurzane.com/" target="_blank" rel="noopener" class="az-ocultable">Ver la web ↗</a>';
  main.insertBefore(top, main.firstChild);
  var velo = document.createElement('div'); velo.className = 'az-velo'; document.body.appendChild(velo);
  var cerrarMenu = function(){ document.body.classList.remove('az-menu-abierto'); };
  top.querySelector('.az-menu').addEventListener('click', function(){ document.body.classList.toggle('az-menu-abierto'); });
  velo.addEventListener('click', cerrarMenu);
  document.addEventListener('click', function(e){ if(e.target.closest('.nav-item')) cerrarMenu(); });
  document.getElementById('azTopBuscar').addEventListener('click', function(){ document.dispatchEvent(new KeyboardEvent('keydown', { key:'k', ctrlKey:true, bubbles:true })); });
  document.getElementById('azTopAct').addEventListener('click', function(){ var n = document.querySelector('.nav-item.active'); if(n){ n.classList.remove('active'); n.click(); } });
  var dens = document.getElementById('azTopDens');
  var ponerDens = function(c){ document.body.classList.toggle('az-compacto', c); dens.textContent = c ? 'Cómodo' : 'Compacto'; try{ localStorage.setItem('azAdmDens', c ? '1' : '0'); }catch(e){} };
  try{ ponerDens(localStorage.getItem('azAdmDens') === '1'); }catch(e){}
  dens.addEventListener('click', function(){ ponerDens(!document.body.classList.contains('az-compacto')); });
  // migas: grupo › sección
  var migas = function(){ var n = document.querySelector('.nav-item.active'); if(!n) return; var g = n.previousElementSibling;
    while(g && !g.classList.contains('nav-grupo')) g = g.previousElementSibling;
    var lab = n.querySelector('.nav-label'); var nom = lab ? lab.childNodes[0].textContent.trim() : n.dataset.page;
    document.getElementById('azMigas').innerHTML = 'Panel AURZANE' + (g ? ' › ' + g.textContent.replace(/[▾▸]/g, '').trim() : '') + ' › <b>' + nom + '</b>';
    document.title = nom + ' · Panel AURZANE'; };
  new MutationObserver(migas).observe(document.querySelector('.sidebar') || document.body, { attributes:true, subtree:true, attributeFilter:['class'] });
  setTimeout(migas, 800);
  // acciones peligrosas en rojo
  var PELIGRO = /^(Eliminar|Borrar|Descartar|Rechazar|Dar de baja|Deshabilitar|Mover a la papelera|Papelera definitiva|Quitar)\b/;
  var marcar = function(){ document.querySelectorAll('.btn-mini:not(.az-pm),.btn-ghost:not(.az-pm)').forEach(function(b){ b.classList.add('az-pm'); if(PELIGRO.test((b.textContent || '').trim())) b.classList.add('az-peligro'); }); };
  new MutationObserver(function(){ clearTimeout(marcar.t); marcar.t = setTimeout(marcar, 120); }).observe(main, { childList:true, subtree:true });
  marcar();
  // Clientes: filtros rápidos por estado del proceso y leyenda de los puntos
  var tb = document.querySelector('#page-clientes tbody'), bar = document.querySelector('#page-clientes .toolbar');
  if(tb && bar){
    var chips = document.createElement('div'); chips.className = 'az-chips'; chips.setAttribute('role', 'group'); chips.setAttribute('aria-label', 'Filtrar clientes');
    bar.parentNode.insertBefore(chips, bar.nextSibling);
    var ley = document.createElement('p'); ley.className = 'az-ley'; ley.innerHTML = '<i class="test-dot done"></i> test hecho <i class="test-dot active"></i> activado, sin hacer <i class="test-dot"></i> sin activar';
    var tabla = tb.closest('.panel') || tb.closest('table'); if(tabla) tabla.parentNode.insertBefore(ley, tabla.nextSibling);
    var filtro = 'todos', EST = [['todos','Todos'],['sin','Sin activar'],['pend','Sin empezar'],['curso','A medias'],['fin','Terminados']];
    var estado = function(tr){ var d = tr.querySelectorAll('.test-dot.done').length, a = tr.querySelectorAll('.test-dot.active').length; return !d && !a ? 'sin' : !d ? 'pend' : a ? 'curso' : 'fin'; };
    var aplicar = function(){ var filas = tb.querySelectorAll('tr.client-row'), n = { todos:filas.length, sin:0, pend:0, curso:0, fin:0 };
      filas.forEach(function(tr){ var e = estado(tr); n[e]++; tr.style.display = (filtro === 'todos' || filtro === e) ? '' : 'none'; });
      chips.innerHTML = EST.map(function(x){ return '<button type="button" data-f="' + x[0] + '" aria-pressed="' + (filtro === x[0]) + '">' + x[1] + ' <b>' + n[x[0]] + '</b></button>'; }).join(''); };
    chips.addEventListener('click', function(e){ var b = e.target.closest('[data-f]'); if(!b) return; filtro = b.dataset.f; aplicar(); });
    new MutationObserver(function(){ clearTimeout(aplicar.t); aplicar.t = setTimeout(aplicar, 80); }).observe(tb, { childList:true });
    aplicar();
  }
})();
</script>
'''
if '</head>' in t: t = t.replace('</head>', CSS + '</head>', 1)
if '</body>' in t:
    i = t.rindex('</body>'); t = t[:i] + JS + t[i:]
if t != s:
    c = os.path.join(base, 'aurzane.com', 'eliminar', 'admin-diseno-' + hoy); os.makedirs(c, exist_ok=True)
    if not os.path.exists(os.path.join(c, 'admin.html')): shutil.copy2(f, c)
    open(f + '.tmp', 'w', encoding='utf-8').write(t); os.replace(f + '.tmp', f)
    print('::notice::admin.html con el diseño nuevo')
else:
    print('admin.html ya tenía el diseño nuevo')
