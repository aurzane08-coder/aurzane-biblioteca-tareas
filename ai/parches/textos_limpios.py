"""Textos limpios en las portadas y páginas (17/11/2026, plan de la auditoría final, puntos 36, 37 y 38).
- Quita las secciones «Hoja de ruta» públicas de las portadas de LEARN y BUILD (promesas sin fecha).
- Español de España: «¿Qué tan…?» → «¿Cómo de…?», «sin costo» → «sin coste».
- Fichas de libros sin guía (biblioteca/libro/ref-*.html sin «Ideas clave»): el título decía «resumen y ficha» sin tener
  resumen; pasa a «ficha del libro». Las fichas con guía (resumen, ideas clave, preguntas) se quedan como están.
- Biblioteca (aurzane.com/biblioteca/libro/): las fichas sin resumen tenían como descripción solo «Léelo gratis en español.»;
  ahora una propia con título, autor y tema. Las que no tienen imagen para compartir llevan su portada (o la de AURZANE).
- Páginas indexables sin canonical: se añade la suya.
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


def biblioteca(t, f):
    slug = f[:-5]
    h1 = re.search(r'<h1>([^<]+)</h1>', t); au = re.search(r'<p class="autores">([^<]+)</p>', t)
    tema = re.search(r'<a class="chip leer" href="../tema/[^"]+">([^<]+)</a>', t)
    if h1 and re.search(r'<meta name="description" content="\s*Léelo gratis en español\.">', t):
        d = f'Lee gratis «{h1.group(1)}»' + (f', de {au.group(1).split(";")[0].strip()}' if au else '') + \
            (f': libro de {tema.group(1).lower()}' if tema else '') + ' en español, legal y sin registro, en la biblioteca de AURZANE.'
        d = d if len(d) <= 160 else d[:157].rsplit(' ', 1)[0] + '…'
        t = re.sub(r'(<meta name="description" content=")\s*Léelo gratis en español\.(">)', lambda m: m.group(1) + d.replace('"', '&quot;') + m.group(2), t, count=1)
        t = re.sub(r'(<meta property="og:description" content=")\s*Léelo gratis en español\.(">)', lambda m: m.group(1) + d.replace('"', '&quot;') + m.group(2), t, count=1)
    if 'property="og:image"' not in t and '</head>' in t:
        img = next((m for m in re.findall(r'<img src="\.\./portadas/([^"]+)"', t) if m.rsplit('.', 1)[0] and slug.startswith(m.rsplit('.', 1)[0][:40])), '')
        u = 'https://aurzane.com/biblioteca/portadas/' + img if img else 'https://aurzane.com/og-portada.jpg'
        t = t.replace('</head>', f'<meta property="og:image" content="{u}">\n</head>', 1)
    return t


def canonica(t, w, raiz, p):
    # las páginas cuyo contenido cambia con «?…» (leer.html?libro=, articulo.html?id=, cursos.html?c=) no llevan canonical fija
    if 'location.search' in t or 'URLSearchParams' in t: return t
    if re.search(r'rel=["\']canonical', t, re.I) or re.search(r'<meta[^>]+name=["\']robots["\'][^>]+noindex', t, re.I) or '</head>' not in t: return t
    rel = os.path.relpath(p, raiz).replace(os.sep, '/')
    u = f'https://{w}/' + (rel[:-10] if rel.endswith('index.html') else rel)
    return t.replace('</head>', f'<link rel="canonical" href="{u}">\n</head>', 1)


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
            if w == 'aurzane.com' and os.path.basename(d) == 'libro' and 'biblioteca' in d: n = biblioteca(n, f)
            n = canonica(n, w, raiz, p)
            if f.startswith('ref-') and 'Ideas clave' not in n and 'resumen y ficha' in n:
                n = re.sub(r'(<title>[^<]*?)resumen y ficha', r'\1ficha del libro', n)
                n = re.sub(r'(<meta property="og:title" content="[^"]*?)resumen y ficha', r'\1ficha del libro', n)
            if '—' in n or 'tan ' in n or 'costo' in n: n = texto(n)
            if n == t: continue
            c = os.path.join(base, w, 'eliminar', 'textos-limpios-' + hoy, os.path.relpath(p, raiz))
            os.makedirs(os.path.dirname(c), exist_ok=True)
            if not os.path.exists(c): shutil.copy2(p, c)
            open(p + '.tmp', 'w', encoding='utf-8').write(n); os.replace(p + '.tmp', p); cambios += 1
print(f'::notice::Textos limpios: {cambios} páginas cambiadas')
