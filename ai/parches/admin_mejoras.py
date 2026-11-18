"""Panel de administración más funcional (18/11/2026), sobre el admin.html vivo. Repetible (marcadores).
1. «Inicio» en vez de «Resumen»: lo que hay que hacer hoy (reportes nuevos, propuestas de la IA, patrocinios por aprobar,
   pagos por confirmar, errores de la web), cómo va AURZANE (visitas, páginas, clics a tiendas, seguidores, boletín) y
   accesos rápidos. Fuera «Distribución por plan» (OVP es gratis).
2. Menú en 5 grupos con «Sistema» plegable; la barra lateral se desplaza sola y el botón de cerrar sesión siempre se ve.
3. Cada sección tiene su dirección (admin.html#clientes…): el botón atrás funciona y al recargar sigues donde estabas.
4. Buscador de secciones con Ctrl K o «/».
Copia previa en aurzane.com/eliminar/admin-mejoras-FECHA/."""
import os, re, sys, shutil, datetime
base = os.path.expanduser('~/' + (sys.argv[1] if len(sys.argv) > 1 else 'www')); hoy = datetime.date.today().strftime('%Y%m%d')
f = os.path.join(base, 'aurzane.com', 'public_html', 'admin.html')
s = open(f, encoding='utf-8').read(); t = s

# 2. grupos del menú
t = t.replace("""var G = [['Día a día', ['resumen','resultados','clientes','reportes','ai']], ['OVP y colegios', ['reactivos','productos','personalidad','membretes','colegios']],
           ['Contenido', ['universidades','patrocinios','contenido']], ['Sistema', ['usuarios','configuracion','feature_flags','ajustes']]];""",
"""var G = [['Hoy', ['resumen','reportes','ai','resultados']], ['Personas', ['clientes','usuarios','colegios']], ['OVP', ['reactivos','membretes','personalidad']],
           ['NEXUS y contenido', ['universidades','patrocinios','contenido']], ['Sistema', ['productos','configuracion','feature_flags','ajustes']]];""")
t = t.replace("""var G = [['Día a día', ['resumen','resultados','clientes','reportes','ai']], ['OVP y colegios', ['reactivos','productos','personalidad','membretes','colegios']],
           ['Contenido', ['universidades','contenido']], ['Sistema', ['usuarios','configuracion','feature_flags','ajustes']]];""",
"""var G = [['Hoy', ['resumen','reportes','ai','resultados']], ['Personas', ['clientes','usuarios','colegios']], ['OVP', ['reactivos','membretes','personalidad']],
           ['NEXUS y contenido', ['universidades','patrocinios','contenido']], ['Sistema', ['productos','configuracion','feature_flags','ajustes']]];""")

# 1. Inicio
INICIO = '''      <!-- inicio (admin_mejoras) -->
      <div id="inHoy">
        <section class="in-hero"><div class="in-ring"><svg viewBox="0 0 120 120" aria-hidden="true"><circle cx="60" cy="60" r="50" class="in-ring-bg"/><circle cx="60" cy="60" r="50" class="in-ring-fg" id="inRing"/></svg><div><b id="inSalud">–</b><span>salud web</span></div></div>
          <div class="in-veredicto"><h3 id="inVeredicto">Cargando…</h3><p id="inResumen"></p></div></section>
        <section class="in-sec"><h3>Para hacer</h3><div class="in-tareas" id="inTareas"></div></section>
        <section class="in-sec"><h3>Cómo va AURZANE <small id="inFecha"></small></h3><div class="in-kpis" id="inKpis"></div></section>
        <div class="in-rej">
          <section class="in-caja in-ancha"><h4>Visitantes por día, 30 días</h4><div id="inGraf"></div></section>
          <section class="in-caja"><h4>Visitantes por sitio, 30 días</h4><div id="inSitios"></div></section>
          <section class="in-caja"><h4>Google: búsquedas con más impresiones</h4><div id="inGoogle"></div></section>
          <section class="in-caja"><h4>Redes: publicaciones en 24 h</h4><div id="inRedes"></div></section>
          <section class="in-caja"><h4>Visitas desde redes, 30 días</h4><div id="inClicsRedes"></div></section>
          <section class="in-caja"><h4>OVP: del registro al resultado</h4><div id="inEmbudo"></div></section>
          <section class="in-caja"><h4>Clics a tiendas por tienda, 30 días</h4><div id="inTiendas"></div></section>
          <section class="in-caja"><h4>Seguidores por red</h4><div id="inSeg"></div></section>
        </div>
        <section class="in-sec"><h3>Accesos rápidos</h3><div class="in-accesos">
          <a href="https://aurzane.com/" target="_blank" rel="noopener">aurzane.com</a><a href="https://mind.aurzane.com/" target="_blank" rel="noopener">MIND</a><a href="https://nexus.aurzane.com/" target="_blank" rel="noopener">NEXUS</a><a href="https://live.aurzane.com/" target="_blank" rel="noopener">LIVE</a><a href="https://learn.aurzane.com/" target="_blank" rel="noopener">LEARN</a><a href="https://build.aurzane.com/" target="_blank" rel="noopener">BUILD</a><a href="https://ovp.aurzane.com/" target="_blank" rel="noopener">OVP</a>
          <a href="https://dashboard.stripe.com/" target="_blank" rel="noopener">Stripe</a><a href="https://adsense.google.com/" target="_blank" rel="noopener">AdSense</a><a href="https://search.google.com/search-console" target="_blank" rel="noopener">Search Console</a><a href="https://supabase.com/dashboard/project/chtfpqwrrarfdjcivlad" target="_blank" rel="noopener">Supabase</a><a href="https://github.com/aurzane08-coder/aurzane-biblioteca-tareas/actions" target="_blank" rel="noopener">Automatizaciones</a>
        </div></section>
        <h3 class="in-ovp">OVP en cifras</h3>
      </div>
'''
# versión nueva: se quita la anterior (bloques entre marcadores) y se vuelve a poner
t = re.sub(r'      <!-- inicio \(admin_mejoras\) -->.*?<h3 class="in-ovp">[^<]*</h3>\n      </div>\n', '', t, flags=re.S)
t = re.sub(r'<script>\n/\* Panel más funcional \(admin_mejoras.*?</script>\n', '', t, flags=re.S)
t = t.replace('<div class="page-head"><h2>Inicio</h2><p>Lo que tienes que hacer hoy, cómo va AURZANE y tus accesos. Se actualiza solo cada minuto.</p></div>\n', '<div class="page-head"><h2>Resumen</h2><p>El estado general de tu proceso OVP, de un vistazo.</p></div>')
viejo_head = '<div class="page-head"><h2>Resumen</h2><p>El estado general de tu proceso OVP, de un vistazo.</p></div>'
if 'id="inHoy"' not in t and viejo_head in t:
    t = t.replace(viejo_head, '<div class="page-head"><h2>Inicio</h2><p>Lo que tienes que hacer hoy, cómo va AURZANE y tus accesos. Se actualiza solo cada minuto.</p></div>\n' + INICIO, 1)

SCRIPT = r'''<script>
/* Panel más funcional (admin_mejoras, 18/11/2026): Inicio, menú plegable, direcciones por sección y buscador */
(function(){
  var $ = function(i){ return document.getElementById(i); };
  var E = function(x){ return String(x == null ? '' : x).replace(/[&<>"']/g, function(c){ return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]; }); };
  var N = function(n){ return (n == null || n === '') ? '0' : Number(n).toLocaleString('es-ES'); };
  var st = document.createElement('style');
  st.textContent = '.nav-items{overflow-y:auto;min-height:0;scrollbar-width:thin}.main{max-width:1280px}'
    + '#page-resumen .panel:has(#planBreakdown){display:none}'
    + '#inHoy{display:grid;gap:22px;margin-bottom:26px}.in-sec h3,.in-ovp{font-family:"Bodoni Moda",serif;font-size:1.05rem;margin:0 0 12px;font-weight:600}.in-sec h3 small{font-family:inherit;font-size:.74rem;color:var(--silver-dim);font-weight:400;margin-left:8px}.in-ovp{margin:6px 0 -10px}'
    + '.in-tareas{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:12px}'
    + '.in-t{display:flex;gap:12px;align-items:center;padding:14px 16px;border:1px solid var(--line);border-radius:14px;background:var(--navy-2);cursor:pointer;text-align:left;color:inherit;font:inherit;width:100%}.in-t:hover,.in-t:focus-visible{border-color:var(--line-strong)}'
    + '.in-t b{font-family:"Bodoni Moda",serif;font-size:1.7rem;min-width:36px;color:var(--gold-light)}.in-t span{font-size:.86rem;line-height:1.35}.in-t small{display:block;color:var(--silver-dim);font-size:.74rem}.in-t.ok b{color:var(--ok)}.in-vacio{color:var(--silver-dim);font-size:.88rem}'
    + '.in-kpis{display:grid;grid-template-columns:repeat(auto-fill,minmax(170px,1fr));gap:1px;background:var(--line);border:1px solid var(--line);border-radius:14px;overflow:hidden}.in-k{background:var(--navy-2);padding:16px 18px}.in-k b{display:block;font-family:"Bodoni Moda",serif;font-size:1.5rem}.in-k span{font-size:.76rem;color:var(--silver-dim)}.in-k i{font-style:normal;font-size:.72rem;margin-left:6px}.in-k i.sube{color:var(--ok)}.in-k i.baja{color:#e08a8a}'
    + '.in-accesos{display:flex;flex-wrap:wrap;gap:8px}.in-accesos a{padding:8px 14px;border:1px solid var(--line);border-radius:99px;font-size:.84rem;color:var(--silver)}.in-accesos a:hover{border-color:var(--gold);color:var(--gold-light)}'
    + '.nav-grupo.plegable{cursor:pointer;user-select:none}.nav-grupo.plegable:after{content:" ▾"}.nav-grupo.plegado:after{content:" ▸"}'
    + '#azBusca{position:fixed;inset:0;background:rgba(5,6,15,.6);display:none;align-items:flex-start;justify-content:center;padding-top:12vh;z-index:9999}#azBusca.ver{display:flex}#azBusca div{width:min(520px,92vw);background:var(--navy-2);border:1px solid var(--line-strong);border-radius:16px;overflow:hidden}#azBusca input{width:100%;padding:16px 18px;background:transparent;border:0;border-bottom:1px solid var(--line);color:var(--bone);font:inherit;font-size:16px;outline:none}#azBusca ul{list-style:none;margin:0;padding:6px;max-height:50vh;overflow:auto}#azBusca li{padding:10px 12px;border-radius:10px;cursor:pointer;font-size:.9rem}#azBusca li.sel,#azBusca li:hover{background:rgba(201,162,75,.12)}#azBusca li small{color:var(--silver-dim);margin-left:8px}'
    + '.az-atajo{margin:0 12px 10px;padding:8px 12px;border:1px solid var(--line);border-radius:10px;font-size:.78rem;color:var(--silver-dim);cursor:pointer;background:transparent;text-align:left}@media(max-width:800px){.az-atajo{display:none}}';
  document.head.appendChild(st);
  var lab = document.querySelector('.nav-item[data-page="resumen"] .nav-label'); if(lab) lab.textContent = 'Inicio';

  // --- direcciones por sección: admin.html#clientes
  var abrir = function(k){ var n = document.querySelector('.nav-item[data-page="' + k + '"]'); if(n && !n.classList.contains('active')) n.click(); };
  document.addEventListener('click', function(ev){ var n = ev.target.closest('.nav-item[data-page]'); if(n && location.hash.slice(1) !== n.dataset.page) history.replaceState(null, '', '#' + n.dataset.page); }, true);
  window.addEventListener('hashchange', function(){ abrir(location.hash.slice(1)); });
  var inicial = location.hash.slice(1);
  if(inicial && inicial !== 'resumen'){ var k = 0, iv = setInterval(function(){ var n = document.querySelector('.nav-item[data-page="' + inicial + '"]'); if((n && n.offsetParent && window.__aurzaneSb) || ++k > 60){ clearInterval(iv); abrir(inicial); } }, 250); }

  // --- grupo «Sistema» plegable (se recuerda)
  setTimeout(function(){
    document.querySelectorAll('.nav-grupo').forEach(function(g){
      if(g.textContent.trim() !== 'Sistema') return;
      g.classList.add('plegable'); g.setAttribute('role', 'button'); g.tabIndex = 0;
      var items = function(){ var l = [], e = g.nextElementSibling; while(e && !e.classList.contains('nav-grupo')){ if(e.classList.contains('nav-item')) l.push(e); e = e.nextElementSibling; } return l; };
      var poner = function(pleg){ g.classList.toggle('plegado', pleg); items().forEach(function(e){ if(!e.classList.contains('active')) e.style.display = pleg ? 'none' : ''; }); try{ localStorage.setItem('azAdmSistema', pleg ? '1' : '0'); }catch(e){} };
      var guardado = '1'; try{ guardado = localStorage.getItem('azAdmSistema') || '1'; }catch(e){}
      poner(guardado === '1');
      g.addEventListener('click', function(){ poner(!g.classList.contains('plegado')); });
      g.addEventListener('keydown', function(e){ if(e.key === 'Enter' || e.key === ' '){ e.preventDefault(); g.click(); } });
    });
  }, 300);

  // --- buscador de secciones (Ctrl K o /)
  var caja = document.createElement('div'); caja.id = 'azBusca'; caja.innerHTML = '<div role="dialog" aria-label="Ir a una sección"><input id="azBuscaIn" placeholder="Ir a… (clientes, patrocinios, errores…)" autocomplete="off"><ul id="azBuscaL"></ul></div>';
  document.body.appendChild(caja);
  var EXTRA = { ai:'errores reparaciones cola publicado salud ia', resultados:'visitas google boletin afiliados redes estadisticas', clientes:'ovp pagos procesos', usuarios:'cuentas contraseña', colegios:'accesos militar', patrocinios:'stripe pagos universidades destacadas', universidades:'carreras fichas nexus', contenido:'articulos', reportes:'problemas avisos', resumen:'inicio hoy tareas' };
  var secciones = function(){ return Array.prototype.map.call(document.querySelectorAll('.nav-item[data-page]'), function(n){ return { k:n.dataset.page, t:n.querySelector('.nav-label') ? n.querySelector('.nav-label').childNodes[0].textContent.trim() : n.dataset.page }; }); };
  var sel = 0, lista = [];
  var norm = function(x){ return x.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, ''); };
  var pintarB = function(){ var q = norm($('azBuscaIn').value.trim()); lista = secciones().filter(function(s){ return !q || norm(s.t + ' ' + s.k + ' ' + (EXTRA[s.k] || '')).indexOf(q) >= 0; }); sel = Math.min(sel, Math.max(0, lista.length - 1));
    $('azBuscaL').innerHTML = lista.map(function(s, i){ return '<li data-k="' + s.k + '" class="' + (i === sel ? 'sel' : '') + '">' + E(s.t) + '</li>'; }).join('') || '<li>Nada con ese nombre</li>'; };
  var cerrar = function(){ caja.classList.remove('ver'); };
  var abrirB = function(){ if(!window.__aurzaneSb) return; caja.classList.add('ver'); $('azBuscaIn').value = ''; sel = 0; pintarB(); $('azBuscaIn').focus(); };
  $('azBuscaIn').addEventListener('input', function(){ sel = 0; pintarB(); });
  $('azBuscaIn').addEventListener('keydown', function(e){ if(e.key === 'ArrowDown'){ sel = Math.min(sel + 1, lista.length - 1); pintarB(); e.preventDefault(); } else if(e.key === 'ArrowUp'){ sel = Math.max(sel - 1, 0); pintarB(); e.preventDefault(); } else if(e.key === 'Enter' && lista[sel]){ cerrar(); abrir(lista[sel].k); } else if(e.key === 'Escape') cerrar(); });
  $('azBuscaL').addEventListener('click', function(e){ var li = e.target.closest('li[data-k]'); if(li){ cerrar(); abrir(li.dataset.k); } });
  caja.addEventListener('click', function(e){ if(e.target === caja) cerrar(); });
  document.addEventListener('keydown', function(e){ var enCampo = /INPUT|TEXTAREA|SELECT/.test((document.activeElement || {}).tagName || '');
    if((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k'){ e.preventDefault(); abrirB(); } else if(e.key === '/' && !enCampo){ e.preventDefault(); abrirB(); } });
  var items = document.querySelector('.sidebar .nav-items');
  if(items){ var at = document.createElement('button'); at.className = 'az-atajo'; at.type = 'button'; at.textContent = 'Buscar sección   Ctrl K'; at.addEventListener('click', abrirB); items.parentNode.insertBefore(at, items); }

  // --- Inicio: veredicto, tareas, cifras con tendencia y gráficas (SVG propio, sin librerías)
  var css2 = document.createElement('style');
  css2.textContent = '.in-hero{display:flex;gap:22px;align-items:center;padding:22px 24px;border:1px solid var(--line);border-radius:18px;background:linear-gradient(135deg,var(--navy-2),var(--navy-3,#151C3D))}'
    + '.in-ring{position:relative;width:96px;height:96px;flex:none}.in-ring svg{width:96px;height:96px;transform:rotate(-90deg)}.in-ring-bg{fill:none;stroke:var(--line);stroke-width:10}.in-ring-fg{fill:none;stroke:var(--ok);stroke-width:10;stroke-linecap:round;stroke-dasharray:314;stroke-dashoffset:314;transition:stroke-dashoffset .8s}'
    + '.in-ring>div{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center}.in-ring b{font-family:"Bodoni Moda",serif;font-size:1.7rem;line-height:1}.in-ring span{font-size:.66rem;color:var(--silver-dim)}'
    + '.in-veredicto h3{font-family:"Bodoni Moda",serif;font-size:1.45rem;margin:0 0 6px;font-weight:600}.in-veredicto p{margin:0;color:var(--silver);font-size:.88rem;line-height:1.5;max-width:70ch}'
    + '.in-k .sp{display:block;margin-top:8px;height:28px;width:100%}.in-k b{font-variant-numeric:tabular-nums}'
    + '.in-rej{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}.in-caja{border:1px solid var(--line);border-radius:16px;background:var(--navy-2);padding:18px 20px;min-width:0}.in-ancha{grid-column:span 2}.in-caja h4{margin:0 0 14px;font-size:.86rem;font-weight:600;color:var(--bone)}'
    + '.in-graf svg{width:100%;height:auto;display:block}.in-graf text{fill:var(--silver-dim);font-size:11px;font-family:inherit}.in-ley{display:flex;gap:14px;font-size:.74rem;color:var(--silver-dim);margin-bottom:8px}.in-ley i{display:inline-block;width:10px;height:3px;border-radius:2px;margin-right:6px;vertical-align:middle}'
    + '.in-bar{display:grid;grid-template-columns:minmax(80px,38%) 1fr auto;gap:10px;align-items:center;font-size:.8rem;margin:7px 0}.in-bar span:first-child{overflow:hidden;text-overflow:ellipsis;white-space:nowrap;color:var(--silver)}.in-bar .t{height:8px;border-radius:5px;background:var(--line);overflow:hidden;display:flex}.in-bar .t i{display:block;height:100%}.in-bar b{font-variant-numeric:tabular-nums;font-weight:600;min-width:36px;text-align:right}'
    + '.in-vacio{color:var(--silver-dim);font-size:.84rem}'
    + '@media(max-width:1100px){.in-rej{grid-template-columns:1fr 1fr}}@media(max-width:800px){.in-rej{grid-template-columns:1fr}.in-ancha{grid-column:auto}.in-hero{flex-direction:column;align-items:flex-start}}'
    + 'table td,table th{font-variant-numeric:tabular-nums}tbody tr:hover td{background:rgba(201,162,75,.04)}button:focus-visible,a:focus-visible,.nav-item:focus-visible,select:focus-visible,input:focus-visible{outline:2px solid var(--gold);outline-offset:2px}';
  document.head.appendChild(css2);
  var ORO = 'var(--gold)', PLATA = 'var(--silver)', OK = 'var(--ok)', MAL = '#e08a8a';
  var tarea = function(n, txt, sub, k){ return '<button class="in-t' + (n ? '' : ' ok') + '" data-in="' + k + '"><b>' + (n ? N(n) : '✓') + '</b><span>' + txt + (sub ? '<small>' + sub + '</small>' : '') + '</span></button>'; };
  var badge = function(id){ var b = $(id); return b && b.style.display !== 'none' ? parseInt(b.textContent, 10) || 0 : 0; };
  var spark = function(vals, color){ if(!vals || vals.length < 2) return ''; var mx = Math.max.apply(null, vals) || 1, w = 160, h = 28;
    var pts = vals.map(function(v, i){ return (i * w / (vals.length - 1)).toFixed(1) + ',' + (h - 2 - v / mx * (h - 4)).toFixed(1); }).join(' ');
    return '<svg class="sp" viewBox="0 0 ' + w + ' ' + h + '" preserveAspectRatio="none" aria-hidden="true"><polyline points="0,' + h + ' ' + pts + ' ' + w + ',' + h + '" fill="' + color + '" opacity=".12"/><polyline points="' + pts + '" fill="none" stroke="' + color + '" stroke-width="1.6" vector-effect="non-scaling-stroke"/></svg>'; };
  var area = function(dias){ if(!dias || dias.length < 2) return '<p class="in-vacio">Hacen falta al menos dos días de registros.</p>';
    var W = 760, H = 220, pl = 40, pb = 22, mx = Math.max.apply(null, dias.map(function(d){ return d.visitantes; })) || 1;
    var x = function(i){ return pl + i * (W - pl - 8) / (dias.length - 1); }, y = function(v){ return H - pb - v / mx * (H - pb - 10); };
    var l = dias.map(function(d, i){ return (i ? 'L' : 'M') + x(i).toFixed(1) + ' ' + y(d.visitantes).toFixed(1); }).join('');
    var media = dias.map(function(d, i){ var a = dias.slice(Math.max(0, i - 6), i + 1); return a.reduce(function(s, z){ return s + z.visitantes; }, 0) / a.length; });
    var lm = media.map(function(v, i){ return (i ? 'L' : 'M') + x(i).toFixed(1) + ' ' + y(v).toFixed(1); }).join('');
    var marcas = [0, Math.round(mx / 2), mx].map(function(v){ return '<line x1="' + pl + '" x2="' + W + '" y1="' + y(v) + '" y2="' + y(v) + '" stroke="var(--line)"/><text x="' + (pl - 6) + '" y="' + (y(v) + 4) + '" text-anchor="end">' + N(v) + '</text>'; }).join('');
    var et = dias.map(function(d, i){ return (i % 5 === 0 || i === dias.length - 1) ? '<text x="' + x(i) + '" y="' + (H - 4) + '" text-anchor="middle">' + d.dia.slice(8) + '/' + d.dia.slice(5, 7) + '</text>' : ''; }).join('');
    var puntos = dias.map(function(d, i){ return '<circle cx="' + x(i) + '" cy="' + y(d.visitantes) + '" r="2.6" fill="' + ORO + '"><title>' + d.dia + ': ' + d.visitantes + ' visitantes, ' + d.paginas + ' páginas</title></circle>'; }).join('');
    return '<div class="in-ley"><span><i style="background:' + ORO + '"></i>Visitantes</span><span><i style="background:' + PLATA + '"></i>Media de 7 días</span></div><div class="in-graf"><svg viewBox="0 0 ' + W + ' ' + H + '" role="img" aria-label="Visitantes por día en los últimos 30 días">' + marcas + et
      + '<path d="' + l + 'L' + x(dias.length - 1) + ' ' + (H - pb) + 'L' + pl + ' ' + (H - pb) + 'Z" fill="' + ORO + '" opacity=".1"/><path d="' + l + '" fill="none" stroke="' + ORO + '" stroke-width="2.2"/><path d="' + lm + '" fill="none" stroke="' + PLATA + '" stroke-width="1.6" stroke-dasharray="4 4"/>' + puntos + '</svg></div>'; };
  var barras = function(filas, color, fmt){ filas = (filas || []).filter(function(f){ return f && f[1] != null; }); if(!filas.length) return '<p class="in-vacio">Sin datos todavía.</p>';
    var mx = Math.max.apply(null, filas.map(function(f){ return +f[1] || 0; })) || 1;
    return filas.map(function(f){ return '<div class="in-bar"><span title="' + E(f[0]) + '">' + E(f[0]) + '</span><span class="t"><i style="width:' + Math.max(2, (+f[1] || 0) / mx * 100) + '%;background:' + (f[2] || color) + '"></i></span><b>' + (fmt ? fmt(f) : N(f[1])) + '</b></div>'; }).join(''); };
  var INF = null, PAN = null;
  async function token(){ var sb = window.__aurzaneSb; return sb ? (await sb.auth.getSession()).data.session?.access_token : ''; }
  async function datos(){
    var tk = await token(); if(!tk) return;
    try{ INF = ((await (await fetch('/ai/api.php', { cache:'no-store', headers:{ Authorization:'Bearer ' + tk } })).json()).informe) || INF; }catch(e){}
    try{ var q = await window.__aurzaneSb.from('reportes').select('id', { count:'exact', head:true }).eq('estado', 'nuevo'); if(q.count != null){ var rb = $('repBadge'); if(rb){ rb.textContent = q.count || ''; rb.style.display = q.count ? 'inline-block' : 'none'; } } }catch(e){}
    try{ var r = await (await fetch('https://aurzane.com/panel/datos.php', { method:'POST', headers:{ 'Content-Type':'application/json' }, body: JSON.stringify({ token: tk }) })).json(); if(!r.error) PAN = r; }catch(e){}
    pintar();
  }
  var kpiOVP = function(){ return Array.prototype.map.call(document.querySelectorAll('#kpiRow .kpi-card'), function(d){ return [((d.querySelector('.k-lbl') || {}).textContent || '').trim(), parseInt(((d.querySelector('.k-num') || {}).textContent || '').replace(/\D/g, ''), 10) || 0]; }).filter(function(x){ return x[0]; }); };
  function pintar(){
    if(!$('inTareas')) return;
    var I = INF || {}, er = I.errores || {}, probs = (I.problemas || []), prob = probs.filter(function(p){ return p.nivel !== 'bajo'; }).length;
    var nMal = probs.filter(function(p){ return p.nivel === 'mal'; }).length, nMed = probs.length - nMal, salud = I.fecha ? Math.max(0, 100 - nMal * 22 - nMed * 7) : null;
    var pend = $('pendingList') ? $('pendingList').children.length : 0;
    var t = [[badge('repBadge'), 'Reportes nuevos de visitantes', 'Problemas que te avisan desde la web', 'reportes'], [badge('aiBadge') || I.cola || 0, 'Propuestas de la IA por revisar', 'Libros, estudios y frases para aprobar', 'ai'],
             [badge('ptBadge'), 'Patrocinios por aprobar', 'Universidades que piden su mes gratis', 'patrocinios'], [prob, 'Avisos de la web', 'Lo que la IA no pudo arreglar sola', 'ai'], [er.total_24h || 0, 'Errores de visitantes en 24 h', (er.corregidos || []).length ? er.corregidos.length + ' ya corregidos' : 'JavaScript en las páginas', 'ai']];
    if(pend) t.splice(3, 0, [pend, 'Pagos de OVP por confirmar', '', 'resumen']);
    var hay = t.filter(function(x){ return x[0]; }).length;
    $('inTareas').innerHTML = t.map(function(x){ return tarea(x[0], x[1], x[2], x[3]); }).join('');
    $('inVeredicto').textContent = hay ? (hay === 1 ? 'Una cosa necesita tu atención' : hay + ' cosas necesitan tu atención') : 'Todo en orden';
    $('inResumen').textContent = (I.resumen || '').split('\n').slice(0, 3).join(' ');
    if(salud != null){ $('inSalud').textContent = salud; var rg = $('inRing'); rg.style.strokeDashoffset = 314 - 314 * salud / 100; rg.style.stroke = salud >= 85 ? 'var(--ok)' : salud >= 55 ? 'var(--gold)' : MAL; }
    var P = PAN; if(!P){ $('inKpis').innerHTML = '<div class="in-k"><span>Cargando las cifras…</span></div>'; return; }
    var dias = ((P.visitas || {}).por_dia || []).slice(-30), suma = function(a, k){ return a.reduce(function(s, d){ return s + (d[k] || 0); }, 0); };
    var u7 = suma(dias.slice(-7), 'visitantes'), u7p = suma(dias.slice(-14, -7), 'visitantes');
    var pct = function(a, b){ if(!b) return ''; var p = Math.round((a - b) / b * 100); return '<i class="' + (p >= 0 ? 'sube' : 'baja') + '">' + (p >= 0 ? '▲ +' : '▼ ') + p + ' % vs 7 días antes</i>'; };
    var segR = ((P.seguidores || {}).redes || []), seg = segR.reduce(function(s, r){ return s + (r[1] || 0); }, 0), segD = segR.reduce(function(s, r){ return s + (r[2] || 0); }, 0);
    var S = P.seo || {};
    var k = function(v, tt, extra, sp){ return '<div class="in-k"><b>' + v + '</b><span>' + tt + '</span>' + (extra ? '<span style="display:block;margin-top:4px">' + extra + '</span>' : '') + (sp || '') + '</div>'; };
    $('inKpis').innerHTML = k(N(u7), 'Visitantes, últimos 7 días', pct(u7, u7p), spark(dias.map(function(d){ return d.visitantes; }), ORO))
      + k(N(suma(dias, 'paginas')), 'Páginas vistas, 30 días', '', spark(dias.map(function(d){ return d.paginas; }), PLATA))
      + k(N(S.clics), 'Clics desde Google, 4 sem.', N(S.impresiones) + ' apariciones')
      + k(N((P.clics_compra || {}).total_30_dias), 'Clics a tiendas, 30 días', '')
      + k(N((P.clics_redes || {}).total_30_dias), 'Visitas desde redes, 30 días', '')
      + k(N(seg), 'Seguidores en redes', segD ? '<i class="sube">▲ +' + segD + ' en 30 días</i>' : '');
    $('inFecha').textContent = P.generado ? '· datos del ' + new Date(P.generado).toLocaleDateString('es-ES') : '';
    $('inGraf').innerHTML = area(dias);
    $('inSitios').innerHTML = barras(((P.visitas || {}).por_dominio || []).slice(0, 7), ORO);
    $('inGoogle').innerHTML = S.conectado ? barras((S.consultas || []).slice().sort(function(a, b){ return b[2] - a[2]; }).slice(0, 6).map(function(q){ return [q[0], q[2], null, q[3]]; }), PLATA, function(f){ return N(f[1]) + ' · pos. ' + f[3]; }) : '<p class="in-vacio">Search Console sin conectar.</p>';
    var M = (I.marketing || {}).por_red || {};
    $('inRedes').innerHTML = Object.keys(M).length ? Object.keys(M).map(function(r){ var x = M[r], tot = (x.ok || 0) + (x.fallos || 0) || 1;
      return '<div class="in-bar"><span>' + E(r) + '</span><span class="t"><i style="width:' + (x.ok / tot * 100) + '%;background:' + OK + '"></i><i style="width:' + (x.fallos / tot * 100) + '%;background:' + MAL + '"></i></span><b>' + x.ok + (x.fallos ? ' · ' + x.fallos + ' ✕' : '') + '</b></div>'; }).join('') + '<div class="in-ley" style="margin-top:10px"><span><i style="background:' + OK + '"></i>Publicadas</span><span><i style="background:' + MAL + '"></i>Fallidas</span></div>' : '<p class="in-vacio">Sin publicaciones en 24 h.</p>';
    $('inClicsRedes').innerHTML = barras((P.clics_redes || {}).por_red, ORO);
    $('inTiendas').innerHTML = barras((P.clics_compra || {}).por_tienda, OK);
    $('inSeg').innerHTML = barras(segR.map(function(r){ return [r[0], r[1] == null ? 0 : r[1], null, r[2]]; }), PLATA, function(f){ return N(f[1]) + (f[3] ? ' (+' + f[3] + ')' : ''); });
    var ov = kpiOVP(); $('inEmbudo').innerHTML = ov.length ? barras(ov, PLATA) : '<p class="in-vacio">Sin datos de OVP.</p>';
  }
  document.addEventListener('click', function(ev){ var b = ev.target.closest('[data-in]'); if(!b) return; abrir(b.dataset.in);
    if(b.dataset.in === 'ai' && /Errores/.test(b.textContent)) setTimeout(function(){ var t = document.querySelector('#aiTabs [data-t="errores"]'); if(t) t.click(); }, 600); });
  var arr = 0, iv2 = setInterval(function(){ if(window.__aurzaneSb){ clearInterval(iv2); setTimeout(datos, 2500); setInterval(pintar, 15000); setInterval(datos, 300000); } else if(++arr > 240) clearInterval(iv2); }, 500);
})();
</script>
'''
if 'admin_mejoras, 18/11/2026' not in t and '</body>' in t:
    i = t.rindex('</body>'); t = t[:i] + SCRIPT + t[i:]
if t != s:
    c = os.path.join(base, 'aurzane.com', 'eliminar', 'admin-mejoras-' + hoy); os.makedirs(c, exist_ok=True)
    if not os.path.exists(os.path.join(c, 'admin.html')): shutil.copy2(f, c)
    open(f + '.tmp', 'w', encoding='utf-8').write(t); os.replace(f + '.tmp', f)
    print('::notice::admin.html más funcional (Inicio, menú, direcciones y buscador)')
else:
    print('admin.html ya estaba mejorado')
