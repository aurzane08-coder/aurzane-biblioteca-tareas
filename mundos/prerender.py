"""Artículos de cada mundo dentro del HTML (sin esperar a JavaScript).

Las portadas de MIND, LIVE, BUILD y LEARN pintaban sus artículos con JavaScript después de cargar: mientras tanto, y para
Google, AdSense o cualquier lector sin JavaScript, la página solo decía «Cargando…» y «No encontramos artículos con ese filtro».
Este paso lee los artículos publicados de cada mundo y los escribe en el HTML de la portada: tarjetas reales, cifra de
artículos y fuentes, sin mensaje de carga. El JavaScript de la página sigue funcionando igual (filtros, «Ver más», guardados)
y sustituye estas tarjetas al cargar. Se ejecuta cada día y después de cada despliegue, así cada artículo nuevo aparece solo.
Antes de cambiar una portada guarda una copia en www/<mundo>/eliminar/prerender-FECHA/.
Entradas: SSH, SG_DEST.
"""
import json, os, re, html, subprocess, datetime, urllib.request

SB = 'https://chtfpqwrrarfdjcivlad.supabase.co/rest/v1/'
KEY = 'sb_publishable___1v6VjDew0l8uGfMyb9Nw_YyCLTPPw'  # solo lectura de lo publicado
SSH = os.environ.get('SSH', ''); DEST = os.environ.get('SG_DEST', '')
HOY = datetime.date.today().isoformat()
MUNDOS = {'mind': 'guías', 'live': 'artículos', 'build': 'guías', 'learn': 'guías'}
E = lambda s: html.escape(str(s or ''), quote=True)
MESES = ['ene', 'feb', 'mar', 'abr', 'may', 'jun', 'jul', 'ago', 'sept', 'oct', 'nov', 'dic']


def remoto(orden, entrada=None):
    return subprocess.run(SSH.split() + [DEST, orden], capture_output=True, text=True, timeout=120, input=entrada).stdout


def leer(tabla):
    rq = urllib.request.Request(f'{SB}{tabla}?select=slug,categoria,titulo,resumen,cuerpo,fuentes,destacado,created_at&order=created_at.desc', headers={'apikey': KEY})
    with urllib.request.urlopen(rq, timeout=60) as r: return json.load(r)


def fecha(f):
    try: d = datetime.date.fromisoformat(f[:10]); return f'{d.day} {MESES[d.month - 1]} {d.year}'
    except Exception: return ''


def transforma(t, arts, palabra):
    # imágenes y nombres de categoría: los mismos que usa la página
    img = dict(re.findall(r"\n\s*([a-z_-]+)\s*:\s*'(https://[^']+)'", t[t.find('const CAT_IMG'):t.find('};', t.find('const CAT_IMG'))]))
    etiq = dict(re.findall(r"\n\s*'?([a-z_-]+)'?\s*:\s*'([^']+)'", t[t.find('const CATEGORIAS'):t.find('};', t.find('const CATEGORIAS'))]))
    defecto = next(iter(img.values()), '')
    tarjetas = ''.join(
        f'<a class="e-card{" wide" if i % 5 == 0 else ""}" href="https://aurzane.com/articulos/{E(a["slug"])}/"><div class="e-img"><img src="{E(img.get(a["categoria"], defecto))}" alt="" loading="lazy"></div>'
        f'<div class="e-body"><span class="cat-badge">{E(etiq.get(a["categoria"], a["categoria"]))}</span><h3>{E(a["titulo"])}</h3><p>{E(a["resumen"])}</p>'
        f'<div class="e-foot"><span>{fecha(a.get("created_at") or "")}</span><span>{max(1, round(len((a.get("cuerpo") or "").split()) / 220))} min de lectura</span></div></div></a>'
        for i, a in enumerate(arts))
    fuentes = sum(len(a.get('fuentes') or []) for a in arts)
    n = t
    n = re.sub(r'(id="editorialGrid">)(?:<!--az-pre-->[\s\S]*?<!--/az-pre-->)?', lambda x: x.group(1) + '<!--az-pre-->' + tarjetas + '<!--/az-pre-->', n, count=1)
    n = re.sub(r'(id="worldMetaRow">)(?:<!--az-pre-->[\s\S]*?<!--/az-pre-->)?', lambda x: x.group(1) + f'<!--az-pre--><div class="wm"><b>{len(arts)}</b>{"guías publicadas" if palabra == "guías" else "artículos publicados"}</div><div class="wm"><b>{fuentes}</b>fuentes citadas</div><!--/az-pre-->', n, count=1)
    n = n.replace('<div id="contentArea" style="display:none;">', '<div id="contentArea" style="display:block;">', 1)
    n = re.sub(r'<div id="loadState" class="load-state"(?: style="display:none;")?>', '<div id="loadState" class="load-state" style="display:none;">', n, count=1)
    n = re.sub(r'(<div id="loadState"[^>]*>\s*<div class="spinner"></div>\s*<p[^>]*>)Cargando [^<]*(</p>)', lambda x: x.group(1) + x.group(2), n, count=1)
    n = re.sub(r'(<div id="emptyState" class="empty-state" style="display:none;">\s*(?:<[^>]+>\s*)*?<p>)[^<]*(</p>)', lambda x: x.group(1) + 'Prueba con otro filtro o mira todos los ' + palabra + '.' + x.group(2), n, count=1)
    n = re.sub(r'(id="resultCount"[^>]*>)[^<]*(<)', lambda x: x.group(1) + f'{len(arts)} {palabra}' + x.group(2), n, count=1)
    return n


for m, palabra in MUNDOS.items():
    if not SSH: break
    arch = f'www/{m}.aurzane.com/public_html/index.html'
    t = remoto(f'cat {arch} 2>/dev/null')
    if 'id="editorialGrid"' not in t: print('sin listado', m); continue
    try: arts = leer(f'{m}_articulos')
    except Exception as e: print('no se pudo leer', m, e); continue
    if not arts: print('sin artículos', m); continue
    n = transforma(t, arts, palabra)
    if n != t:
        copia = f'www/{m}.aurzane.com/eliminar/prerender-{HOY}/index.html'
        r = remoto(f'mkdir -p "$(dirname {copia})" && cp -p {arch} {copia} && cat > {arch}.pre && mv {arch}.pre {arch} && echo OK', n)
        if 'OK' in r:
            remoto(f'site-tools-client domain-all update id={m}.aurzane.com flush_cache=1 >/dev/null 2>&1; true')
            print(f'{m}: {len(arts)} {palabra} dentro de la página')
    else: print(f'{m}: sin cambios ({len(arts)} {palabra})')
