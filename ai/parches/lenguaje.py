# Lenguaje común del ecosistema (guía en mundos/lenguaje.md). Corre en el servidor cada día.
# Mensajes de error sin textos técnicos para el usuario, «Cargando…» igual en todas partes y estados con la misma forma.
# Copia previa en <web>/eliminar/lenguaje-FECHA/. Uso: python3 - www < lenguaje.py
import os, re, sys, shutil, datetime
base = sys.argv[1]; hoy = datetime.datetime.now().strftime('%Y%m%d-%H%M')
R = [  # (patrón, sustitución)
    (r"'Hubo un problema al finalizar: ' \+ error\.message \+ '[^']*'", "'No se pudo finalizar la evaluación. Tus respuestas ya están guardadas: inténtalo de nuevo en un momento.'"),
    (r"'Hubo un problema guardando tus respuestas: ' \+ saveAllError\.message \+ '[^']*'", "'No se pudieron guardar tus respuestas. Revisa tu conexión e inténtalo de nuevo.'"),
    (r'Cargando\.\.\.', 'Cargando…'), (r'(?<=[>\'"])cargando…?(?=[<\'"])', 'Cargando…'),
    (r'Guardado ✓', 'Guardado'),
    (r'Algo salió mal\.?', 'No se pudo completar la acción.'), (r'Ocurrió un error\.?', 'No se pudo completar la acción.'),
]
EXCL = ('eliminar', 'wp-content', 'wp-includes', 'wp-admin', 'universidades', 'libro', 'libros')
n = 0
for web in ['aurzane.com', 'mind.aurzane.com', 'live.aurzane.com', 'learn.aurzane.com', 'nexus.aurzane.com', 'build.aurzane.com', 'ovp.aurzane.com']:
    pub = os.path.join(base, web, 'public_html')
    for raiz, dirs, archivos in os.walk(pub):
        dirs[:] = [d for d in dirs if d not in EXCL]
        for a in archivos:
            if not a.endswith(('.html', '.js')): continue
            f = os.path.join(raiz, a)
            try: s = open(f, encoding='utf-8').read()
            except Exception: continue
            t = s
            for p, b in R: t = re.sub(p, b, t)
            if t != s:
                c = os.path.join(base, web, 'eliminar', 'lenguaje-' + hoy, os.path.relpath(f, pub)); os.makedirs(os.path.dirname(c), exist_ok=True)
                shutil.copy2(f, c); open(f, 'w', encoding='utf-8').write(t); n += 1
print('archivos con el lenguaje común:', n)
