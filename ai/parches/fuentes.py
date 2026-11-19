"""Fuentes propias en vez de Google Fonts (17/11/2026, etapa 2 de la auditoría, tarea 27: portada lenta).
Antes cada página pedía una hoja a fonts.googleapis.com y luego las letras a fonts.gstatic.com: dos dominios
más antes de pintar nada en móvil. Ahora las mismas letras (Bodoni Moda e Instrument Sans, licencia OFL) salen
de https://aurzane.com/fuentes/ y la hoja va escrita dentro de la página, sin petición que bloquee.
Solo se cambia el enlace si pide únicamente esas dos familias; si una página usa otra (Cormorant, Fraunces...)
se deja como está. Se puede repetir sin efecto: lo ya cambiado no se toca. Copia de cada archivo cambiado en
<web>/eliminar/fuentes-FECHA/. Corre cada día y tras cada despliegue, así lo que generan las automatizaciones
nuevas también queda con las fuentes propias."""
import os, re, sys, shutil, datetime, urllib.parse
base = os.path.expanduser('~/' + (sys.argv[1] if len(sys.argv) > 1 else 'www')); hoy = datetime.datetime.now().strftime('%Y%m%d')
WEBS = ['aurzane.com', 'mind.aurzane.com', 'nexus.aurzane.com', 'live.aurzane.com', 'learn.aurzane.com', 'build.aurzane.com', 'ovp.aurzane.com']
FUERA = {'eliminar', 'wp-admin', 'wp-content', 'wp-includes', 'node_modules', '.well-known', 'privado-ai', 'fuentes'}
U = 'https://aurzane.com/fuentes/'
LAT = 'U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+0304,U+0308,U+0329,U+2000-206F,U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD'
EXT = 'U+0100-02BA,U+02BD-02C5,U+02C7-02CC,U+02CE-02D7,U+02DD-02FF,U+0304,U+0308,U+0329,U+1D00-1DBF,U+1E00-1E9F,U+1EF2-1EFF,U+2020,U+20A0-20AB,U+20AD-20C0,U+2113,U+2C60-2C7F,U+A720-A7FF'


def cara(fam, est, peso, arch, rango):
    return f"@font-face{{font-family:'{fam}';font-style:{est};font-weight:{peso};font-display:swap;src:url({U}{arch}) format('woff2');unicode-range:{rango}}}"


CSS = ''.join([
    cara('Bodoni Moda', 'normal', '400 900', 'bodoni-moda-latin-opsz-normal.woff2', LAT),
    cara('Bodoni Moda', 'normal', '400 900', 'bodoni-moda-latin-ext-opsz-normal.woff2', EXT),
    cara('Bodoni Moda', 'italic', '400 900', 'bodoni-moda-latin-opsz-italic.woff2', LAT),
    cara('Bodoni Moda', 'italic', '400 900', 'bodoni-moda-latin-ext-opsz-italic.woff2', EXT),
    cara('Instrument Sans', 'normal', '400 700', 'instrument-sans-latin-wght-normal.woff2', LAT),
    cara('Instrument Sans', 'normal', '400 700', 'instrument-sans-latin-ext-wght-normal.woff2', EXT),
    cara('Instrument Sans', 'italic', '400 700', 'instrument-sans-latin-wght-italic.woff2', LAT),
    cara('Instrument Sans', 'italic', '400 700', 'instrument-sans-latin-ext-wght-italic.woff2', EXT)])
NUEVO = (f'<link rel="preload" href="{U}instrument-sans-latin-wght-normal.woff2" as="font" type="font/woff2" crossorigin>'
         f'<link rel="preload" href="{U}bodoni-moda-latin-opsz-normal.woff2" as="font" type="font/woff2" crossorigin>'
         f'<style id="az-fuentes">{CSS}</style>')
ENLACE = re.compile(r'<link\b[^>]*href=["\'](https://fonts\.googleapis\.com/css2?\?[^"\']+)["\'][^>]*>\s*', re.I)
PRECON = re.compile(r'<link\b[^>]*rel=["\']preconnect["\'][^>]*href=["\']https://fonts\.(googleapis|gstatic)\.com/?["\'][^>]*>\s*'
                    r'|<link\b[^>]*href=["\']https://fonts\.(googleapis|gstatic)\.com/?["\'][^>]*rel=["\']preconnect["\'][^>]*>\s*', re.I)
NUESTRAS = {'Bodoni Moda', 'Instrument Sans'}


def familias(url):
    q = urllib.parse.parse_qs(urllib.parse.urlparse(url.replace('&amp;', '&')).query)
    return {f.split(':')[0].replace('+', ' ').strip() for f in q.get('family', [])}


def htaccess(dir_f):
    """Las letras se piden desde los 7 dominios: hace falta permiso CORS y caché larga."""
    p = dir_f + '/.htaccess'
    t = ('# AURZANE fuentes propias\n<IfModule mod_headers.c>\n<FilesMatch "\\.woff2$">\nHeader always set Access-Control-Allow-Origin "*"\n'
         'Header set Cache-Control "public, max-age=31536000, immutable"\n</FilesMatch>\n</IfModule>\nAddType font/woff2 .woff2\n')
    if not os.path.exists(p) or open(p).read() != t:
        open(p, 'w').write(t)


PALETA = '<script src="https://aurzane.com/aurzane-paleta.js"></script>'
PRE_DS = re.compile(r'<link rel="preload" href="https://aurzane\.com/aurzane-ds\.css\?v=[0-9A-Za-z._-]+" as="style" data-azpre="1">')


def version_ds():
    """Versión de la hoja común que carga aurzane-paleta.js; con ella se adelanta su descarga en cada página."""
    try:
        m = re.search(r"aurzane-ds\.css\?v=([0-9A-Za-z._-]+)", open(base + '/aurzane.com/public_html/aurzane-paleta.js', encoding='utf-8').read())
        return m.group(1) if m else ''
    except Exception: return ''


def precarga(t, v):
    """Hoja común precargada en paralelo con aurzane-paleta.js (antes se pedía después: medio segundo más en móvil)."""
    if not v or PALETA not in t: return t
    tag = f'<link rel="preload" href="https://aurzane.com/aurzane-ds.css?v={v}" as="style" data-azpre="1">'
    if PRE_DS.search(t): return PRE_DS.sub(tag, t, count=1)
    return t.replace(PALETA, PALETA + tag, 1)


def main():
    raiz_f = base + '/aurzane.com/public_html/fuentes'
    if not os.path.exists(raiz_f + '/instrument-sans-latin-wght-normal.woff2'):
        print('::warning::Faltan las fuentes en aurzane.com/fuentes/: no se cambia ninguna página'); return
    htaccess(raiz_f)
    total, dejadas, pre = 0, 0, 0
    VDS = version_ds()
    for w in WEBS:
        raiz = base + '/' + w + '/public_html'; copia = base + '/' + w + '/eliminar/fuentes-' + hoy
        for d, sub, fs in os.walk(raiz):
            sub[:] = [s for s in sub if s not in FUERA and not s.startswith('.')]
            for f in fs:
                if not f.endswith('.html'): continue
                p = os.path.join(d, f)
                try: t = open(p, encoding='utf-8').read()
                except Exception: continue
                t0 = t
                t = precarga(t, VDS)
                if 'fonts.googleapis.com' not in t:
                    if t != t0:   # solo cambia una etiqueta de precarga: sin copia (serían miles de copias en cada cambio de versión)
                        tmp = p + '.tmp-fuentes-' + str(os.getpid()); open(tmp, 'w', encoding='utf-8').write(t); os.replace(tmp, p); pre += 1
                    continue
                t = re.sub(r'<noscript>\s*(<link\b[^>]*fonts\.googleapis\.com[^>]*>)\s*</noscript>', lambda m: '' if not (familias(re.search(r'href=["\'](https://fonts[^"\']+)', m.group(1)).group(1)) - NUESTRAS) else m.group(0), t)
                hecho = [False]

                def cambia(m):
                    if familias(m.group(1)) - NUESTRAS:
                        return m.group(0)
                    if hecho[0] or 'id="az-fuentes"' in t:
                        return ''
                    hecho[0] = True
                    return NUEVO
                n = ENLACE.sub(cambia, t)
                if n == t0:
                    dejadas += 1; continue
                if 'fonts.googleapis.com/css' not in n:
                    n = PRECON.sub('', n)
                rel = os.path.relpath(p, raiz); dst = os.path.join(copia, rel)
                os.makedirs(os.path.dirname(dst), exist_ok=True); shutil.copy2(p, dst)
                tmp = p + '.tmp-fuentes-' + str(os.getpid()); open(tmp, 'w', encoding='utf-8').write(n); os.replace(tmp, p); total += 1
    print(f'::notice::Fuentes propias: {total} páginas cambiadas; {dejadas} usan otras familias y siguen con Google Fonts; hoja común precargada (v{VDS}) en {pre} páginas más')


main()
