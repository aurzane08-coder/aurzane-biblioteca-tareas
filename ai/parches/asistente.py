# El asistente de resultados (IA) se sirve desde el mismo dominio que el test (mind y live).
# SiteGround cortaba con un 503 las preguntas que los navegadores enviaban de mind/live a aurzane.com.
# Copia aurzane.com/ai/asistente.php a mind y live apuntando a la misma clave y los mismos límites (privado-ai de aurzane.com).
# Corre en cada cambio de este archivo y cada día. Uso: python3 - www < asistente.py
import os, sys, shutil, datetime
base = sys.argv[1]; hoy = datetime.datetime.now().strftime('%Y%m%d-%H%M')
src = os.path.join(base, 'aurzane.com', 'public_html', 'ai', 'asistente.php')
s = open(src, encoding='utf-8').read()
a = "$dir = dirname(__DIR__, 2) . '/privado-ai';"
if a not in s: sys.exit('no encuentro la ruta de privado-ai en asistente.php')
t = s.replace(a, "$dir = dirname(__DIR__, 3) . '/aurzane.com/privado-ai';   // copia de aurzane.com/ai/asistente.php (ai/parches/asistente.py)")
for web in ('mind.aurzane.com', 'live.aurzane.com'):
    d = os.path.join(base, web, 'public_html', 'ai'); os.makedirs(d, exist_ok=True)
    f = os.path.join(d, 'asistente.php')
    if os.path.exists(f) and open(f, encoding='utf-8').read() == t: continue
    if os.path.exists(f):
        c = os.path.join(base, web, 'eliminar', 'asistente-' + hoy); os.makedirs(c, exist_ok=True); shutil.copy2(f, c)
    open(f, 'w', encoding='utf-8').write(t); print('asistente copiado en', web)
print('ok')
