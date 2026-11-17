"""Textos limpios en las portadas y páginas (17/11/2026, plan de la auditoría final, puntos 36, 37 y 38).
- Quita las secciones «Hoja de ruta» públicas de las portadas de LEARN y BUILD (promesas sin fecha).
- Español de España: «¿Qué tan…?» → «¿Cómo de…?», «sin costo» → «sin coste».
- Sin rayas largas (—) en el texto visible: en <title> se cambian por « | » y en el resto por una coma.
  No se toca nada dentro de <script> ni <style>.
Corre cada día y tras cada despliegue; lo ya limpio no cambia. Copia previa en <web>/eliminar/textos-limpios-FECHA/."""
import os, re, sys, shutil, datetime
base = os.path.expanduser('~/' + (sys.argv[1] if len(sys.argv) > 1 else 'www')); hoy = datetime.date.today().strftime('%Y%m%d')
WEBS = ['aurzane.com', 'mind.aurzane.com', 'nexus.aurzane.com', 'live.aurzane.com', 'learn.aurzane.com', 'build.aurzane.com', 'ovp.aurzane.com']
FUERA = {'eliminar', 'node_modules', '.well-known', 'privado-ai', 'fuentes', 'wp-admin', 'wp-content', 'wp-includes', 'panel'}
ES = [(r'¿Qué tan (satisfech[oa]s?|content[oa]s?|bien|seguido|seguid[oa]s?|a menudo)', r'¿Cómo de \1'),
      (r'\bsin costo\b', 'sin coste'), (r'\bSin costo\b', 'Sin coste'), (r'\bel costo\b', 'el coste'), (r'\bEl costo\b', 'El coste')]


def sin_hoja_de_ruta(t):
    """Quita cada <section> cuya cabecera dice «Hoja de ruta», contando secciones anidadas."""
    while True:
        m = re.search(r'<span class="sh-eyebrow">Hoja de ruta</span>', t)
        if not m: return t
        ini = t.rfind('<section', 0, m.start())
        if ini < 0: return t
        prof, i = 0, ini
        for x in re.finditer(r'<section\b|</section>', t[ini:]):
            prof += 1 if x.group(0) != '</section>' else -1
            if prof == 0: i = ini + x.end(); break
        else: return t
        t = t[:ini] + t[i:]


def texto(t):
    partes = re.split(r'(<script\b.*?</script>|<style\b.*?</style>|<title>.*?</title>|<[^>]+>)', t, flags=re.S | re.I)
    for k, p in enumerate(partes):
        if not p: continue
        if p.lower().startswith('<title>'):
            partes[k] = re.sub(r'\s*—\s*', ' | ', p)
        elif p.startswith('<'):
            # atributos que se leen: alt, title, aria-label, content de descripciones
            partes[k] = re.sub(r'((?:alt|title|aria-label|content)="[^"]*?)\s+—\s+([^"]*")', r'\1, \2', p) if '—' in p and not p.lower().startswith(('<script', '<style')) else p
        else:
            q = re.sub(r'\s+—\s+', ', ', p)
            for a, b in ES: q = re.sub(a, b, q)
            partes[k] = q
    return ''.join(partes)


cambios = 0
for w in WEBS:
    raiz = os.path.join(base, w, 'public_html')
    for d, sub, fs in os.walk(raiz):
        sub[:] = [s for s in sub if s not in FUERA and not s.startswith('.')]
        for f in fs:
            if not f.endswith('.html'): continue
            p = os.path.join(d, f)
            try: t = open(p, encoding='utf-8').read()
            except Exception: continue
            n = t
            if f == 'index.html' and d == raiz and w in ('learn.aurzane.com', 'build.aurzane.com'): n = sin_hoja_de_ruta(n)
            if '—' in n or 'tan ' in n or 'costo' in n: n = texto(n)
            if n == t: continue
            c = os.path.join(base, w, 'eliminar', 'textos-limpios-' + hoy, os.path.relpath(p, raiz))
            os.makedirs(os.path.dirname(c), exist_ok=True)
            if not os.path.exists(c): shutil.copy2(p, c)
            open(p + '.tmp', 'w', encoding='utf-8').write(n); os.replace(p + '.tmp', p); cambios += 1
print(f'::notice::Textos limpios: {cambios} páginas cambiadas')
