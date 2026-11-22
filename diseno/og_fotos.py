"""Imágenes para redes (og:image) con fotos reales (22/11/2026).
Regla de AURZANE: ninguna imagen hecha por Claude, tampoco las de promoción. Los og.jpg / og-*.jpg / og/*.jpg eran banners generados;
aquí se sustituye cada uno por una foto real de Unsplash según el tema de su ruta (1200x630, JPG: las redes no leen AVIF).
Uso en el flujo: python3 diseno/og_fotos.py lista.txt manifiesto.txt salida/
  lista.txt      rutas en el servidor (dominio/public_html/...) con su md5
  manifiesto.txt rutas ya cambiadas y el md5 de la foto puesta (si un generador vuelve a escribir un banner, el md5 cambia y se repone la foto)
Escribe en salida/ los JPG nuevos con su misma ruta y en salida/cambiados.txt la lista."""
import os, re, sys, subprocess, hashlib, urllib.request

FOTOS = [  # (patrón en la ruta, id de la foto en Unsplash)
    (r'ansiedad|anxiety|ansiedade|gad-7', '1505142468610-359e7d316be0'),
    (r'estres|stress|burnout|dass', '1541199249251-f713e6145474'),
    (r'depresi|depress|phq', '1529665253569-6d01c0eaf7b6'),
    (r'sueno|sleep|dormir|insomnio', '1541781774459-bb2af2f05b55'),
    (r'habito|calorias|imc|agua|embarazo', '1490645935967-10de6ba17061'),
    (r'autoestima|esteem|personalidad|autoeficacia|efficacy|autocompasion|compassion', '1517841905240-472988babdf9'),
    (r'soledad|lonel', '1512438248247-f0f2a5a8b7f0'),
    (r'resilien', '1466692476868-aef1dfb1e735'),
    (r'tdah|adhd', '1434030216411-0b793f4b4173'),
    (r'bienestar|wellbeing|who-5|satisfaccion|satisfaction|ejercicios|respiracion|coherencia|escaneo|meditaci|suspiro|tecnica|lugar-seguro|pausa|relajacion', '1506126613408-eca07ce68773'),
    (r'universidad|nota-pau|notas-de-corte|carrera', '1541339907198-e08756dedf3f'),
    (r'curso|certificad', '1522202176988-66273c2fd55f'),
    (r'hipoteca|sueldo|reforma|interes|porcentaje|dinero|alquiler', '1579621970563-ebec7560ff3e'),
    (r'biblioteca|libro|frases|lectura|tienda', '1532012197267-da84d127e765'),
    (r'vocacional|ovp|colegios', '1523240795612-9a054b0db644'),
]
MUNDO = {'mind': '1559757175-5700dde675bc', 'nexus': '1541339907198-e08756dedf3f', 'live': '1454496522488-7a8e488e8606',
         'learn': '1481627834876-b7833e8f5570', 'build': '1461360370896-922624d12aa1', 'ovp': '1523240795612-9a054b0db644', 'aurzane': '1481627834876-b7833e8f5570'}

def foto(ruta):
    r = ruta.lower(); web = r.split('/public_html/')[-1]
    for pat, i in FOTOS:
        if re.search(pat, web): return i
    h = r.split('/')[0]; return MUNDO.get(h.split('.')[0] if h != 'aurzane.com' else 'aurzane', MUNDO['aurzane'])

def bajar(i, cache={}):
    if i in cache: return cache[i]
    u = f'https://images.unsplash.com/photo-{i}?w=1200&h=630&fit=crop&crop=entropy&fm=jpg&q=82'
    try:
        b = urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'AURZANE og'}), timeout=40).read()
        ok = b[:3] == b'\xff\xd8\xff' and len(b) > 20000
    except Exception as e:
        print('no se pudo bajar', i, e); b, ok = None, False
    cache[i] = b if ok else None; return cache[i]

lista, manif, sal = sys.argv[1:4]
hecho = {}
if os.path.exists(manif):
    for l in open(manif):
        p = l.rstrip('\n').split('\t')
        if len(p) == 2: hecho[p[1]] = p[0]
cambiados = []
for l in open(lista):
    p = l.rstrip('\n').split('  ', 1)
    if len(p) != 2: continue
    md5, ruta = p[0], p[1].strip()
    if hecho.get(ruta) == md5: continue   # ya tiene su foto real
    i = foto(ruta); b = bajar(i) or bajar(MUNDO['aurzane'])
    if not b: continue
    d = os.path.join(sal, ruta); os.makedirs(os.path.dirname(d), exist_ok=True); open(d, 'wb').write(b)
    cambiados.append((hashlib.md5(b).hexdigest(), ruta)); print('foto', i, '→', ruta)
open(os.path.join(sal, 'cambiados.txt'), 'w').write(''.join(f'{m}\t{r}\n' for m, r in cambiados))
print('Cambiados:', len(cambiados))
