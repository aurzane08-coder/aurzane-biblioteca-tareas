"""Arreglos de los errores de JavaScript que detectó el AI Manager (18/11/2026). Se aplica en el servidor y es repetible.

1. «aurzane-id.js necesita que supabase-js ya esté cargado» (mind, nexus, live, learn, ovp): si la librería de cuentas
   no llega (bloqueador, red lenta, CDN caída), antes la página entera se rompía. Ahora aurzane-id.js devuelve un cliente
   «sin conexión» que dice que no hay sesión y la página sigue funcionando; en cuanto supabase-js carga, se usa el de verdad.
2. «d.body is null» en biblioteca/leer.html?libro=…: la página redirigía con JavaScript desde la cabecera mientras los
   scripts comunes intentaban pintar. La redirección la hace ahora el servidor (301), antes de cargar nada.
Copias previas en aurzane.com/eliminar/errores-js-FECHA/."""
import os, re, sys, shutil, datetime
base = os.path.expanduser('~/' + (sys.argv[1] if len(sys.argv) > 1 else 'www')); hoy = datetime.date.today().strftime('%Y%m%d')
copias = os.path.join(base, 'aurzane.com', 'eliminar', 'errores-js-' + hoy)


def copia(f, nombre):
    os.makedirs(copias, exist_ok=True); d = os.path.join(copias, nombre)
    if not os.path.exists(d): shutil.copy2(f, d)


def escribir(f, t):
    open(f + '.tmp', 'w', encoding='utf-8').write(t); os.replace(f + '.tmp', f)


# 1. aurzane-id.js sin romper la página
STUB = '''    if (!global.supabase || !global.supabase.createClient) {
      // aurzane-errores-js: sin supabase-js (bloqueador o red) la página no se rompe; funciona como «sin sesión»
      console.warn("aurzane-id.js: supabase-js no está cargado; la página sigue sin sesión.");
      const sinRed = { message: "No se pudo conectar con AURZANE ID. Recarga la página.", code: "sin_conexion" };
      const vacio = () => Promise.resolve({ data: null, error: sinRed });
      const cadena = new Proxy(function () {}, { get: (t, k) => k === "then" ? (ok, ko) => vacio().then(ok, ko) : () => cadena, apply: () => cadena });
      return {
        auth: {
          getSession: () => Promise.resolve({ data: { session: null }, error: null }),
          getUser: () => Promise.resolve({ data: { user: null }, error: null }),
          onAuthStateChange: () => ({ data: { subscription: { unsubscribe() {} } } }),
          signOut: () => Promise.resolve({ error: null }),
          signInWithPassword: vacio, signUp: vacio, signInWithOtp: vacio, signInWithOAuth: vacio,
          resetPasswordForEmail: vacio, updateUser: vacio, refreshSession: vacio,
        },
        from: () => cadena, rpc: vacio, storage: { from: () => cadena }, functions: { invoke: vacio },
        channel: () => ({ on() { return this; }, subscribe() { return this; } }), removeChannel() {},
      };
    }'''
PAT = re.compile(r'    if \(!global\.supabase \|\| !global\.supabase\.createClient\) \{\n      throw new Error\(\n        "aurzane-id\.js necesita[^\n]*\n      \);\n    \}')
for host in ('aurzane.com', 'mind.aurzane.com', 'nexus.aurzane.com', 'live.aurzane.com', 'learn.aurzane.com', 'build.aurzane.com', 'ovp.aurzane.com'):
    f = os.path.join(base, host, 'public_html', 'aurzane-id.js')
    if not os.path.isfile(f): continue
    s = open(f, encoding='utf-8').read()
    if 'aurzane-errores-js' in s: print(host, 'aurzane-id.js ya arreglado'); continue
    t, n = PAT.subn(lambda m: STUB, s)
    if n:
        copia(f, host + '-aurzane-id.js'); escribir(f, t); print('::notice::aurzane-id.js sin romper la página en', host)
    else:
        print('::warning::aurzane-id.js de', host, 'tiene otra forma; revisar a mano')

# 2. leer.html?libro=x → libro/x.html desde el servidor
ht = os.path.join(base, 'aurzane.com', 'public_html', '.htaccess')
s = open(ht, encoding='utf-8').read()
BLOQUE = '''# BEGIN AURZANE-LEER-LIBRO
# biblioteca/leer.html?libro=x redirige en el servidor (antes lo hacía JavaScript y saltaban errores «d.body is null»)
RewriteCond %{QUERY_STRING} (?:^|&)libro=([a-z0-9-]+)(?:&|$)
RewriteRule ^biblioteca/leer\\.html$ /biblioteca/libro/%1.html [R=301,L,QSD]
# END AURZANE-LEER-LIBRO
'''
if 'AURZANE-LEER-LIBRO' not in s and 'RewriteEngine On\n' in s:
    copia(ht, 'htaccess')
    m_ = '# BEGIN AURZANE-AI redirecciones'   # fuera de los bloques que reescriben otros parches
    i = s.index(m_) if m_ in s else s.index('RewriteEngine On\n') + len('RewriteEngine On\n')
    escribir(ht, s[:i] + BLOQUE + s[i:]); print('::notice::leer.html?libro= redirige desde el servidor')
else:
    print('leer.html: sin cambios')
