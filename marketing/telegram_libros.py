"""Libro del día en el canal de Telegram de AURZANE.

La primera vez publica un paquete de 15 libros y después uno al día, hasta 365.
Solo se sube el PDF cuando la licencia permite redistribuirlo tal cual en un canal (dominio público o CC sin «NC»).
Los libros con licencia «no comercial» (CC BY-NC...) se presentan con su portada y el enlace para leerlos gratis
en la biblioteca, porque el canal también recomienda libros con enlace de afiliado.
"""
import json, os, re, sys, time, datetime, urllib.request, urllib.parse

D = os.path.dirname(os.path.abspath(__file__))
EST = os.path.join(D, 'telegram_libros.json')
T, CANAL = os.environ.get('TELEGRAM_TOKEN', ''), os.environ.get('TELEGRAM_CANAL', '')
if not T or not CANAL: sys.exit('Faltan TELEGRAM_TOKEN o TELEGRAM_CANAL')


def tg(metodo, datos):
    rq = urllib.request.Request(f'https://api.telegram.org/bot{T}/{metodo}', data=urllib.parse.urlencode(datos).encode())
    try:
        with urllib.request.urlopen(rq, timeout=120) as r: return json.loads(r.read())
    except urllib.error.HTTPError as e: return json.loads(e.read() or b'{}')


def libre(lic):
    """Dominio público o Creative Commons sin cláusula no comercial (BY, BY-SA, BY-ND): se puede compartir el PDF tal cual."""
    lic = (lic or '').upper()
    return 'DOMINIO' in lic or (lic.startswith('CC') and not re.search(r'\bNC\b|-NC', lic))


js = urllib.request.urlopen('https://aurzane.com/biblioteca/catalogo.js', timeout=90).read().decode('utf-8')
B = json.loads(js[js.index('{'):js.rstrip().rstrip(';').rindex('}') + 1])
temas = {str(t['n']): t['nombre'] for t in B['temas']}
libros = [l for l in B['libros'] if l.get('tipo') == 'pdf' and l.get('pdf')]
# primero los más atractivos para el público general: con portada, de extensión razonable, temas cercanos
CERCA = ('Autoestima', 'Emoc', 'Estrés', 'Ansiedad', 'Hábito', 'Duelo', 'Relaci', 'Bienestar', 'Sueño', 'Motivación', 'Felicidad', 'Resiliencia', 'Relatos', 'Familia', 'Aprend')
def puntos(l):
    t = temas.get(str(l.get('principal')), '')
    return (-(1 if l.get('portada') else 0), -(1 if any(c in t for c in CERCA) else 0), -(1 if 20 <= (l.get('paginas') or 0) <= 400 else 0), l['id'])
libros.sort(key=puntos)

est = json.load(open(EST, encoding='utf-8')) if os.path.exists(EST) else {'enviados': [], 'dias': {}}
hoy = datetime.date.today().isoformat()
if est['dias'].get(hoy) and os.environ.get('FORZAR') != '1': sys.exit(f'Hoy ya se publicó el libro del día ({est["dias"][hoy]})')
cuantos = 15 if not est['enviados'] else 1
if len(est['enviados']) >= 365: sys.exit('Ya se publicaron los 365 libros')
pend = [l for l in libros if l['id'] not in est['enviados']][:cuantos]
hechos = []
for l in pend:
    aut = (l.get('autores') or '').split(';')[0].strip()
    ficha = f'https://aurzane.com/biblioteca/libro/{l["id"]}.html'
    tema = temas.get(str(l.get('principal')), '')
    tit = re.sub(r'[<>&]', '', l['titulo'])
    cab = f'📖 <b>{tit}</b>' + (f'\n✍️ {re.sub(r"[<>&]", "", aut)}' if aut else '') + (f'\n🏷 {tema}' if tema else '') + (f' · {l["paginas"]} páginas' if l.get('paginas') else '')
    resumen = re.sub(r'[<>&]', '', (l.get('resumen') or ''))[:400]
    pie = (f'\n\n📜 Licencia: {l.get("licencia")}. Fuente: {re.sub(r"[<>&]", "", l.get("fuente") or l.get("repo") or "")[:120]}'
           f'\n\n👉 Ficha y lectura online: {ficha}\n📚 Más de 700 libros gratis: https://aurzane.com/biblioteca/\n\n#LibroDelDía #LibrosGratis #Psicología')
    if libre(l.get('licencia')):
        r = tg('sendDocument', {'chat_id': CANAL, 'document': f'https://aurzane.com/biblioteca/{l["pdf"]}', 'parse_mode': 'HTML',
                                'caption': (cab + '\n\n' + resumen)[:700] + pie[:320]})
        if not r.get('ok'):   # PDF de más de 20 MB u otro problema: se publica con portada y enlace
            print('PDF no enviado:', l['id'], r.get('description'))
            r = None
    else: r = None
    if r is None:
        texto = cab + '\n\n' + resumen + '\n\nLéelo completo y gratis aquí:' + pie
        if l.get('portada'):
            r = tg('sendPhoto', {'chat_id': CANAL, 'photo': f'https://aurzane.com/biblioteca/{l["portada"]}', 'caption': texto[:1020], 'parse_mode': 'HTML'})
        if not r or not r.get('ok'):
            r = tg('sendMessage', {'chat_id': CANAL, 'text': texto[:4000], 'parse_mode': 'HTML', 'disable_web_page_preview': 'false'})
    if r.get('ok'):
        est['enviados'].append(l['id']); hechos.append(l['id']); print('publicado:', l['titulo'][:80])
    else: print('no publicado:', l['id'], r.get('description'))
    time.sleep(4)
if hechos: est['dias'][hoy] = hechos[-1]
json.dump(est, open(EST, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'::notice title=Telegram::{len(hechos)} libro(s) publicados hoy; {len(est["enviados"])} de 365 en total')
