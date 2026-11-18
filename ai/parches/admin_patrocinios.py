"""Pestaña «Patrocinios» en aurzane.com/admin.html (18/11/2026) y lecciones de los errores en la pestaña de la IA.
Adrián lo controla todo desde admin.html: aquí ve las solicitudes de universidades, aprueba el mes gratis, alarga, da de baja,
copia los enlaces de pago de Stripe y guarda la clave de firma de Stripe (se guarda fuera de la web y nunca se vuelve a mostrar).
Habla con aurzane.com/patrocinio.php?admin=1, que comprueba la sesión con es_admin() de Supabase.
Se aplica en el servidor sobre el admin.html vivo y es repetible (marcadores). Copia previa en aurzane.com/eliminar/admin-patrocinios-FECHA/."""
import os, sys, shutil, datetime
base = os.path.expanduser('~/' + (sys.argv[1] if len(sys.argv) > 1 else 'www')); hoy = datetime.date.today().strftime('%Y%m%d')
f = os.path.join(base, 'aurzane.com', 'public_html', 'admin.html')
s = open(f, encoding='utf-8').read(); t = s

NAV = '''      <div class="nav-item" data-page="patrocinios">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M12 3l2.6 5.3 5.9.9-4.3 4.1 1 5.8L12 16.4 6.8 19.1l1-5.8L3.5 9.2l5.9-.9z"/></svg>
        <span class="nav-label">Patrocinios <span class="status-pill pending" id="ptBadge" style="display:none;margin-left:4px"></span></span>
      </div>
'''
PAGE = '''    <!-- PATROCINIOS (admin_patrocinios) -->
    <div class="page" id="page-patrocinios">
      <div class="page-head"><h2>Patrocinios de universidades</h2><p>Las universidades piden su mes gratis en nexus.aurzane.com/universidades/anunciate/. Aquí lo apruebas; después pagan solas con Stripe y el destacado se alarga solo con cada pago. Sale o se quita de NEXUS en la siguiente publicación (dos al día).</p></div>
      <div class="panel" id="ptStripe"></div>
      <div class="panel">
        <div class="panel-head"><h3>Solicitudes y destacados</h3><button class="btn-ghost" style="width:auto;" id="ptRecargar">Actualizar</button></div>
        <div class="table-scroll"><table>
          <thead><tr><th>Universidad</th><th>Contacto</th><th>Estado</th><th>Periodo</th><th>Pago</th><th>Acciones</th></tr></thead>
          <tbody id="ptTabla"><tr><td colspan="6">Cargando…</td></tr></tbody>
        </table></div>
      </div>
    </div>
'''
SCRIPT = r'''<script>
/* Patrocinios (admin_patrocinios, 18/11/2026) y lecciones de los errores de la IA */
(function(){
  var $ = function(i){ return document.getElementById(i); };
  var E = function(x){ return String(x == null ? '' : x).replace(/[&<>"']/g, function(c){ return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]; }); };
  var toast = function(m, t){ if(typeof showToast === 'function') showToast(m, t); };
  var D = null;
  async function api(datos){
    var sb = window.__aurzaneSb; var tk = sb ? (await sb.auth.getSession()).data.session?.access_token : '';
    var r = await fetch('/patrocinio.php?admin=1', { method:'POST', cache:'no-store', headers:{ Authorization:'Bearer ' + tk, 'Content-Type':'application/json' }, body: JSON.stringify(datos || {}) });
    var j = await r.json().catch(function(){ return {}; });
    if(!r.ok) throw new Error(j.error || 'No se pudo completar.');
    return j;
  }
  var EST = { pendiente:['Por aprobar','pending'], prueba:['Mes gratis','paid'], activo:['Activo, pagado','paid'], terminado:['Terminado','pending'], rechazada:['Rechazada','pending'] };
  function fecha(f){ if(!f) return ''; var p = f.split('-'); return p[2] + '/' + p[1] + '/' + p[0]; }
  function pintar(){
    var l = D.lista || [], pend = l.filter(function(s){ return s.estado === 'pendiente'; }).length;
    var b = $('ptBadge'); if(b){ b.textContent = pend; b.style.display = pend ? '' : 'none'; }
    $('ptStripe').innerHTML = D.stripe
      ? '<div class="panel-head"><h3>Pagos con Stripe</h3><span class="status-pill paid">Conectados</span></div><p style="color:var(--silver);font-size:.88rem;margin:0">Las universidades pagan con tarjeta, Google Pay, Apple Pay, Link, Revolut Pay, adeudo SEPA o transferencia (' + E(D.precio) + '). Cada pago alarga su destacado solo y reciben la factura al momento. Para cancelar o cambiar la tarjeta usan su <a href="' + E(D.portal) + '" target="_blank" rel="noopener" style="color:var(--gold-light)">portal de pagos</a>.</p>'
      : '<div class="panel-head"><h3>Conectar los pagos de Stripe</h3><span class="status-pill pending">Falta un paso</span></div>'
        + '<p style="color:var(--silver);font-size:.88rem">Los enlaces de pago ya están creados. Falta guardar la clave que firma los avisos de Stripe para que cada pago alargue el destacado solo:</p>'
        + '<ol style="color:var(--silver);font-size:.88rem;line-height:1.7"><li>En Stripe abre <b>Desarrolladores, Webhooks</b> y entra en <b>AURZANE patrocinios NEXUS</b>.</li><li>En <b>Secreto de firma</b> pulsa <b>Mostrar</b> y cópialo (empieza por whsec_).</li><li>Pégalo aquí y guarda. Se guarda en el servidor, fuera de la web, y no se vuelve a mostrar.</li></ol>'
        + '<div class="form-grid"><div class="field full"><input id="ptClave" type="password" autocomplete="off" placeholder="whsec_…"></div><div class="field full"><button class="btn-gold" id="ptGuardarClave">Guardar clave de Stripe</button></div></div>';
    var g = $('ptGuardarClave'); if(g) g.onclick = async function(){ try{ await api({ accion:'clave_stripe', clave: $('ptClave').value.trim() }); $('ptClave').value = ''; toast('Pagos de Stripe conectados.'); cargar(); } catch(e){ toast(e.message, 'error'); } };
    $('ptTabla').innerHTML = l.length ? l.map(function(s){
      var e = EST[s.estado] || [s.estado, 'pending'], acc = [];
      if(s.estado === 'pendiente'){ acc.push(['aprobar','Aprobar mes gratis']); acc.push(['rechazar','Rechazar']); }
      if(s.estado === 'prueba' || s.estado === 'activo' || s.estado === 'terminado'){ acc.push(['renovar1','+1 mes']); acc.push(['renovar12','+1 año']); }
      if(s.estado === 'prueba' || s.estado === 'activo') acc.push(['baja','Dar de baja']);
      var pago = s.stripe_sub ? (s.cancelada ? 'Stripe, cancelada el ' + fecha(s.cancelada) : 'Stripe, se renueva sola') : (s.estado === 'pendiente' || s.estado === 'rechazada' ? '' : 'Sin pago todavía');
      return '<tr><td><b>' + E(s.universidad) + '</b><br><a href="https://nexus.aurzane.com/universidades/' + E(s.id) + '/" target="_blank" rel="noopener" style="color:var(--gold-light);font-size:.8rem">Ver ficha</a>'
        + (s.texto ? '<div style="font-size:.78rem;color:var(--silver-dim)">«' + E(s.texto) + '»</div>' : '') + '</td>'
        + '<td>' + E(s.nombre) + '<br><a href="mailto:' + E(s.correo) + '" style="color:var(--silver);font-size:.8rem">' + E(s.correo) + '</a><br><a href="' + E(s.admision) + '" target="_blank" rel="noopener" style="color:var(--silver-dim);font-size:.76rem">Admisión</a></td>'
        + '<td><span class="status-pill ' + e[1] + '">' + E(e[0]) + '</span><div style="font-size:.74rem;color:var(--silver-dim)">Pedido ' + E(s.fecha) + '</div></td>'
        + '<td class="mono" style="font-size:.8rem">' + (s.hasta ? fecha(s.desde) + ' a ' + fecha(s.hasta) : '') + '</td>'
        + '<td style="font-size:.8rem">' + E(pago) + (s.estado !== 'pendiente' && s.estado !== 'rechazada' ? '<br><button class="btn-mini" data-pt-copia="' + E(s.pago_mes) + '">Enlace mensual</button> <button class="btn-mini" data-pt-copia="' + E(s.pago_anio) + '">Enlace anual</button>' : '') + '</td>'
        + '<td>' + acc.map(function(a){ return '<button class="btn-mini" data-pt-t="' + E(s.token) + '" data-pt-a="' + a[0] + '">' + a[1] + '</button>'; }).join(' ') + '</td></tr>';
    }).join('') : '<tr><td colspan="6">Todavía no ha llegado ninguna solicitud. Las universidades la piden desde «Destaca tu universidad» en NEXUS.</td></tr>';
  }
  async function cargar(){ try{ D = await api({}); pintar(); } catch(e){ $('ptTabla').innerHTML = '<tr><td colspan="6">' + E(e.message) + '</td></tr>'; } }
  document.addEventListener('click', async function(ev){
    var c = ev.target.closest('[data-pt-copia]');
    if(c){ try{ await navigator.clipboard.writeText(c.dataset.ptCopia); toast('Enlace de pago copiado. Ya va asociado a esta universidad.'); } catch(e){ toast('No se pudo copiar.', 'error'); } return; }
    var b = ev.target.closest('[data-pt-a]'); if(!b) return;
    var nombres = { aprobar:'Aprobar el mes gratis', rechazar:'Rechazar la solicitud', renovar1:'Alargar 1 mes (ya ha pagado fuera de Stripe)', renovar12:'Alargar 1 año (ya ha pagado fuera de Stripe)', baja:'Dar de baja hoy' };
    var hacer = async function(){ b.disabled = true; try{ D = await api({ accion: b.dataset.ptA, t: b.dataset.ptT }); pintar(); toast('Hecho. NEXUS se actualiza en la siguiente publicación.'); } catch(e){ toast(e.message, 'error'); b.disabled = false; } };
    if(typeof showConfirm === 'function') showConfirm(nombres[b.dataset.ptA], 'La universidad recibe un correo automático si corresponde.', hacer); else hacer();
  });
  var nav = document.querySelector('.nav-item[data-page="patrocinios"]'); if(nav) nav.addEventListener('click', cargar);
  var rc = $('ptRecargar'); if(rc) rc.addEventListener('click', cargar);
  setTimeout(function(){ if(window.__aurzaneSb) cargar(); }, 2500);   // para el número de solicitudes por aprobar en el menú

  // Lecciones de los errores de JavaScript: qué significa cada uno, cómo se arregló y cuáles ya están corregidos
  async function lecciones(){
    var tab = document.querySelector('.ai-tab[data-t="errores"]'); if(!tab) return;
    var box = $('aiErrLecciones'); if(!box){ box = document.createElement('div'); box.id = 'aiErrLecciones'; tab.appendChild(box); }
    try{
      var sb = window.__aurzaneSb, tk = (await sb.auth.getSession()).data.session?.access_token;
      var j = await (await fetch('/ai/api.php', { cache:'no-store', headers:{ Authorization:'Bearer ' + tk } })).json();
      var er = ((j.informe || {}).errores) || {}, top = er.top || [], cor = er.corregidos || [];
      var h = '';
      if(top.some(function(x){ return x.leccion; })) h += '<div class="ai-card" style="margin-top:16px"><h3>Qué significa cada error<small>lo que la IA ha aprendido y cómo se arregla</small></h3>' + top.filter(function(x){ return x.leccion; }).map(function(x){ return '<div class="ai-row" style="display:block"><b>' + E(x.mensaje.slice(0,120)) + '</b><div class="ai-meta">' + E(x.leccion.causa) + ' Arreglo: ' + E(x.leccion.arreglo) + '</div></div>'; }).join('') + '</div>';
      if(cor.length) h += '<div class="ai-card" style="margin-top:16px"><h3>Ya corregidos<small>el archivo cambió después del último error</small></h3>' + cor.map(function(x){ return '<div class="ai-row"><span class="n">' + E(x.mensaje.slice(0,110)) + '</span><span class="v">' + x.veces + ' veces · arreglado ' + E((x.cambiado||'').slice(0,10)) + '</span></div>'; }).join('') + '</div>';
      box.innerHTML = h;
    } catch(e){}
  }
  document.addEventListener('click', function(ev){ var t = ev.target.closest('#aiTabs [data-t="errores"]'); if(t) setTimeout(lecciones, 300); });
})();
</script>
'''
if 'data-page="patrocinios"' not in t:
    ancla = '      <div class="nav-item" data-page="usuarios">'
    if ancla in t: t = t.replace(ancla, NAV + ancla, 1)
if 'id="page-patrocinios"' not in t and '    <!-- USUARIOS -->' in t:
    t = t.replace('    <!-- USUARIOS -->', PAGE + '    <!-- USUARIOS -->', 1)
t = t.replace("['Contenido', ['universidades','contenido']]", "['Contenido', ['universidades','patrocinios','contenido']]")
if 'admin_patrocinios, 18/11/2026' not in t and '</body>' in t:
    i = t.rindex('</body>'); t = t[:i] + SCRIPT + t[i:]
if t != s:
    c = os.path.join(base, 'aurzane.com', 'eliminar', 'admin-patrocinios-' + hoy); os.makedirs(c, exist_ok=True)
    if not os.path.exists(os.path.join(c, 'admin.html')): shutil.copy2(f, c)
    open(f + '.tmp', 'w', encoding='utf-8').write(t); os.replace(f + '.tmp', f)
    print('::notice::admin.html con la pestaña Patrocinios')
else:
    print('admin.html ya tenía Patrocinios')
