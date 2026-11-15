# Cambia el voseo rioplatense (podés, sabés, necesitás…) por el español de España en las páginas publicadas.
# Antes de tocar un archivo guarda una copia en <web>/eliminar/voseo-FECHA/. Uso: python3 voseo.py <carpeta_www>
import re, os, sys, shutil, datetime
M = {'aprendés': 'aprendes', 'decidís': 'decides', 'podés': 'puedes', 'tenés': 'tienes', 'querés': 'quieres', 'sabés': 'sabes', 'necesitás': 'necesitas',
     'elegís': 'eliges', 'hacés': 'haces', 'sentís': 'sientes', 'vivís': 'vives', 'estudiás': 'estudias', 'buscás': 'buscas', 'encontrás': 'encuentras',
     'probá': 'prueba', 'mirá': 'mira', 'empezá': 'empieza', 'pensás': 'piensas', 'contás': 'cuentas', 'llegás': 'llegas', 'usás': 'usas', 'trabajás': 'trabajas', 'imaginá': 'imagina', 'considerás': 'consideras', 'entrás': 'entras', 'respondé': 'responde', 'descubrí': 'descubre'}
# Frases concretas revisadas en contexto (no se tocan títulos de libros como «Elegí mi vida» ni nombres de archivo)
P = [('Hola, iniciá sesión<small>Accedé a todo el', 'Hola, inicia sesión<small>Accede a todo el'), ('Iniciá sesión con AURZANE ID', 'Inicia sesión con AURZANE ID'),
     ('iniciá sesión acá y entrás directo', 'inicia sesión aquí y entras directo'), ('Seguí explorando', 'Sigue explorando'), ('Explorá el corpus', 'Explora el corpus'),
     ('Explorá por tema', 'Explora por tema'), ('Explorá planes', 'Explora planes'), ('Todavía no guardaste ninguna guía. Hacé clic', 'Todavía no has guardado ninguna guía. Haz clic'),
     ('Todavía no guardaste ningún artículo. Hacé clic', 'Todavía no has guardado ningún artículo. Haz clic'), ('Elegí, entre las', 'Elige, entre las'),
     ('Elegí la opción correcta', 'Elige la opción correcta'), ('elegí la opción que', 'elige la opción que'), ('o elegí "Todos"', 'o elige "Todos"'),
     ('Elegí tu nueva contraseña', 'Elige tu nueva contraseña'), ('seguí adelante', 'sigue adelante'), ('Creá el primero', 'Crea el primero'), ('guardá enlaces', 'guarda enlaces'),
     ('Mapeá tus prioridades:</strong> Hacé una lista', 'Haz un mapa de tus prioridades:</strong> Haz una lista'), ('seguí la guía', 'sigue la guía'), ('Escribí el contenido', 'Escribe el contenido'), ('Descubrí cómo orientar', 'Descubre cómo orientar'), ('revisá que hayas respondido', 'revisa que hayas respondido'), ('revisá tu correo', 'revisa tu correo'),
     ('revisá tu bandeja', 'revisa tu bandeja'), ('querés profundizar', 'quieres profundizar'), ('marcá si está', 'marca si está'), ('marcá "Ninguna de ellas"', 'marca "Ninguna de ellas"'),
     ('Marcá la letra', 'Marca la letra'), ('Iniciá sesión una sola vez y accedé', 'Inicia sesión una sola vez y accede'), ('Hacé una lista de lo que considerás', 'Haz una lista de lo que consideras'),
     ('Explorá planes de estudio:</strong> Descargá', 'Explora planes de estudio:</strong> Descarga'), ('Elegí cómo se ve tu cuenta', 'Elige cómo se ve tu cuenta'),
     ('Escribinos', 'Escríbenos'), ('escribinos', 'escríbenos')]
pat = re.compile(r'(?<![\wáéíóúñ])(' + '|'.join(sorted(M, key=len, reverse=True)) + r')(?![\wáéíóúñ])', re.I)
base = sys.argv[1]; hoy = datetime.datetime.now().strftime('%Y%m%d-%H%M'); n = 0
for web in ['aurzane.com', 'mind.aurzane.com', 'live.aurzane.com', 'learn.aurzane.com', 'nexus.aurzane.com', 'build.aurzane.com', 'ovp.aurzane.com']:
    pub = os.path.join(base, web, 'public_html')
    for raiz, dirs, archivos in os.walk(pub):
        if '/eliminar' in raiz: continue
        for a in archivos:
            if not a.endswith(('.html', '.js')): continue
            f = os.path.join(raiz, a)
            try: s = open(f, encoding='utf-8').read()
            except Exception: continue
            t = s
            for a1, b1 in P: t = t.replace(a1, b1)
            t = pat.sub(lambda m: (lambda r: r[0].upper() + r[1:] if m.group(1)[0].isupper() else r)(M[m.group(1).lower()]), t)
            if t != s:
                copia = os.path.join(base, web, 'eliminar', 'voseo-' + hoy, os.path.relpath(f, pub))
                os.makedirs(os.path.dirname(copia), exist_ok=True); shutil.copy2(f, copia)
                open(f, 'w', encoding='utf-8').write(t); n += 1
print('archivos corregidos:', n)

# Arreglos puntuales de la portada de NEXUS (sin sustituir el archivo, que puede ser más nuevo en el servidor)
f = os.path.join(base, 'nexus.aurzane.com', 'public_html', 'index.html')
try:
    s = open(f, encoding='utf-8').read(); t = s
    t = t.replace('Mundo 02 — AURZANE NEXUS', 'Mundo 02 · AURZANE NEXUS')
    if 'no se muestran guiones' not in t:
        t = t.replace("async function cargarStats(){\n  try{", "async function cargarStats(){\n  setTimeout(()=>{ ['statArticulos','statBiblioteca'].forEach(id=>{ const e=document.getElementById(id); if(e && e.textContent.trim()==='—') e.parentElement.style.display='none'; }); }, 4000);   // si la base de datos no responde, no se muestran guiones\n  try{", 1)
    if t != s:
        copia = os.path.join(base, 'nexus.aurzane.com', 'eliminar', 'portada-' + hoy + '.html'); os.makedirs(os.path.dirname(copia), exist_ok=True); shutil.copy2(f, copia)
        open(f, 'w', encoding='utf-8').write(t); print('portada de NEXUS corregida')
except Exception as e: print('NEXUS', e)
