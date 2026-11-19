"""Rendimiento del admin (19/11/2026). El panel pedía los mismos datos varias veces al abrirse: /ai/api.php tres veces,
panel/datos.php dos y patrocinio.php dos, cada módulo por su cuenta. Este script, al principio de <head>, hace que una
misma consulta hecha en los mismos 45 segundos se responda con la primera (misma respuesta, sin volver a pedirla).
Solo afecta a esas tres lecturas; las acciones (aprobar, guardar...) nunca se reutilizan. Repetible."""
import os, re, sys, shutil, datetime
base = os.path.expanduser('~/' + (sys.argv[1] if len(sys.argv) > 1 else 'www')); hoy = datetime.date.today().strftime('%Y%m%d')
f = os.path.join(base, 'aurzane.com', 'public_html', 'admin.html')
s = open(f, encoding='utf-8').read()
JS = r'''<script id="azRendimiento">
/* admin_rendimiento: una lectura repetida en 45 s reutiliza la primera respuesta */
(function(){
  var orig = window.fetch.bind(window), memo = {};
  var LECTURA = /\/ai\/api\.php(\?|$)|\/panel\/datos\.php|\/patrocinio\.php\?admin=1|\/rest\/v1\/rpc\/es_admin/;
  window.fetch = function(u, o){
    try {
      var url = typeof u === 'string' ? u : (u && u.url) || '', m = ((o && o.method) || 'GET').toUpperCase(), b = (o && typeof o.body === 'string') ? o.body : '';
      var esLectura = LECTURA.test(url) && (m === 'GET' || (m === 'POST' && (/datos\.php/.test(url) || b === '{}' || b === '' || /es_admin/.test(url))));
      if (!esLectura) return orig(u, o);
      var k = m + ' ' + url.replace(/[?&]r=\d+/, '') + ' ' + (/datos\.php/.test(url) ? '' : b), x = memo[k];
      if (x && Date.now() - x.t < 45000) return x.p.then(function(r){ return r.clone(); });
      var p = orig(u, o); memo[k] = { t: Date.now(), p: p };
      p.then(function(r){ if (!r.ok) delete memo[k]; }, function(){ delete memo[k]; });
      return p.then(function(r){ return r.clone(); });
    } catch (e) { return orig(u, o); }
  };
})();
</script>
'''
t = re.sub(r'\n<script id="azRendimiento">.*?</script>\n', '', s, flags=re.S)
t = t.replace('<head>', '<head>\n' + JS, 1) if '<head>' in t else re.sub(r'(<head[^>]*>)', lambda m: m.group(1) + '\n' + JS, t, count=1)
# Reportes de visitantes: lo resuelto deja de verse a las 24 h (sigue guardado en la tabla; 19/11/2026)
SEL_V = "select('id,creado,tipo,mensaje,url,referencia,email,origen,estado,nota').order('creado', { ascending:false }).limit(300);"
SEL_N = "select('id,creado,tipo,mensaje,url,referencia,email,origen,estado,nota,resuelto').order('creado', { ascending:false }).limit(300);"
t = t.replace(SEL_V, SEL_N)
FIL_V = "    const { data, error } = await q;\n    const body = document.getElementById('repBody')"
FIL_N = "    let { data, error } = await q;\n    if(data) data = data.filter(r => !(r.estado === 'resuelto' && r.resuelto && Date.now() - new Date(r.resuelto).getTime() > 864e5));   /* admin_rendimiento: resuelto hace más de 24 h, fuera de la lista */\n    const body = document.getElementById('repBody')"
t = t.replace(FIL_V, FIL_N)
# El núcleo del admin refrescaba sus tres módulos uno detrás de otro (1,5 s): ahora a la vez
CORE_V = "fetch('./core/services/membretes-f7-7-r2.js', { cache: 'reload' }).catch(() => null).then(() => fetch('./core/services/universities-f7-8.js', { cache: 'reload' }).catch(() => null)).then(() => fetch('./core/admin/service-f7-8.js', { cache: 'reload' }).catch(() => null)).then(() => import('./core/index-f7-8.js'))"
CORE_N = "Promise.all(['./core/services/membretes-f7-7-r2.js', './core/services/universities-f7-8.js', './core/admin/service-f7-8.js'].map(u => fetch(u, { cache: 'reload' }).catch(() => null))).then(() => import('./core/index-f7-8.js'))"
t = t.replace(CORE_V, CORE_N)
if t != s:
    c = os.path.join(base, 'aurzane.com', 'eliminar', 'admin-rendimiento-' + hoy); os.makedirs(c, exist_ok=True)
    if not os.path.exists(os.path.join(c, 'admin.html')): shutil.copy2(f, c)
    open(f + '.tmp', 'w', encoding='utf-8').write(t); os.replace(f + '.tmp', f); print('::notice::admin.html: lecturas repetidas reutilizadas')
else: print('admin.html ya tenía el rendimiento')
