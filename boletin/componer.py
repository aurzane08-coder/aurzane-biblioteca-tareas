"""Compone el boletín semanal con lo mejor de la semana: libro de la tienda, artículo nuevo, test y frase."""
import json, os, html, datetime, hashlib
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
E = html.escape
def leer(p, d):
    try: return json.load(open(os.path.join(R, p), encoding='utf-8'))
    except Exception: return d
hoy = datetime.date.today(); sem = hoy.isocalendar()[1]
libros = [x for x in leer('tienda/catalogo.json', []) if x.get('portada')]
libro = next((x for x in libros if x.get('tendencia')), None) or (libros[sem % len(libros)] if libros else None)
arts = sorted(leer('ai/articulos_ai.json', []), key=lambda a: a.get('fecha', ''), reverse=True)
art = arts[0] if arts else None
TESTS = [('Test de ansiedad', 'https://mind.aurzane.com/test-de-ansiedad/', '7 preguntas para saber cómo están tus nervios.'),
         ('Test de sueño', 'https://live.aurzane.com/test-de-sueno/', 'Descubre qué te quita descanso y cómo mejorarlo.'),
         ('Test de autoestima', 'https://mind.aurzane.com/test-de-autoestima/', 'La escala de Rosenberg, con tu resultado explicado.'),
         ('Test de personalidad', 'https://mind.aurzane.com/test-de-personalidad/', '¿Eres Fogata, Faro o Telescopio? Descúbrelo en 4 minutos.'),
         ('Test de estrés', 'https://mind.aurzane.com/test-de-estres/', 'Cuánta tensión llevas encima esta semana.'),
         ('Test de bienestar', 'https://live.aurzane.com/test-de-bienestar/', 'El índice de la OMS en 5 preguntas.'),
         ('Test vocacional OVP', 'https://ovp.aurzane.com/portal.html', 'Para quien duda qué estudiar o hacia dónde ir.')]
test = TESTS[sem % len(TESTS)]
UTM = 'utm_source=boletin&utm_medium=email'
def u(x): return x + ('&' if '?' in x else '?') + UTM
bloq = []
if libro:
    f = f'https://aurzane.com/libros/{libro["id"]}/'
    bloq.append(f'<tr><td style="padding:22px 0;border-bottom:1px solid #eee"><p style="margin:0 0 10px;font-size:12px;font-weight:700;letter-spacing:.06em;color:#9a7a2a">LIBRO DE LA SEMANA</p>'
                f'<table role="presentation"><tr><td style="vertical-align:top;padding-right:16px"><img src="{E(libro["portada"])}" width="90" alt="" style="border-radius:4px"></td>'
                f'<td style="vertical-align:top"><p style="margin:0;font:700 19px/1.3 Georgia,serif">{E(libro["titulo"])}</p><p style="margin:4px 0 8px;color:#666">{E(libro["autor"])}</p>'
                f'<p style="margin:0 0 12px">{E((libro.get("porque") or libro.get("tendencia") or "")[:260])}</p>'
                f'<a href="{u(f)}" style="color:#5B43B8;font-weight:700">Ver de qué trata</a></td></tr></table></td></tr>')
if art:
    a_url = f'https://aurzane.com/articulos/{art["slug"]}/'
    bloq.append(f'<tr><td style="padding:22px 0;border-bottom:1px solid #eee"><p style="margin:0 0 6px;font-size:12px;font-weight:700;letter-spacing:.06em;color:#9a7a2a">PARA LEER</p>'
                f'<p style="margin:0 0 6px;font:700 19px/1.3 Georgia,serif"><a href="{u(a_url)}" style="color:#1b1440;text-decoration:none">{E(art["titulo"])}</a></p>'
                f'<p style="margin:0 0 10px">{E((art.get("resumen") or "")[:240])}</p><a href="{u(a_url)}" style="color:#5B43B8;font-weight:700">Leer el artículo</a></td></tr>')
bloq.append(f'<tr><td style="padding:22px 0;border-bottom:1px solid #eee"><p style="margin:0 0 6px;font-size:12px;font-weight:700;letter-spacing:.06em;color:#9a7a2a">TEST DE LA SEMANA</p>'
            f'<p style="margin:0 0 6px;font:700 19px/1.3 Georgia,serif">{E(test[0])}</p><p style="margin:0 0 12px">{E(test[2])} Gratis y anónimo.</p>'
            f'<a href="{u(test[1])}" style="display:inline-block;background:#E2BF6A;color:#1b1440;padding:11px 20px;border-radius:99px;font-weight:700;text-decoration:none">Hacer el test</a></td></tr>')
html_b = (f'<!doctype html><html lang="es"><meta charset="utf-8"><body style="margin:0;background:#f6f3ee"><table role="presentation" width="100%"><tr><td align="center" style="padding:24px 12px">'
          f'<table role="presentation" width="100%" style="max-width:560px;background:#fff;border-radius:14px;padding:28px;font:16px/1.6 -apple-system,Segoe UI,Arial,sans-serif;color:#222">'
          f'<tr><td><p style="margin:0;font:700 22px Georgia,serif;letter-spacing:.06em">AUR<span style="color:#C9A24B">Z</span>ANE</p><p style="margin:4px 0 0;color:#777">Tu semana en AURZANE · {hoy.strftime("%d/%m/%Y")}</p></td></tr>'
          + ''.join(bloq) +
          f'<tr><td style="padding:20px 0 0;font-size:13px;color:#888">Más de 700 libros gratis en la <a href="{u("https://aurzane.com/biblioteca/")}" style="color:#888">biblioteca</a> y toda la <a href="{u("https://aurzane.com/libros/")}" style="color:#888">tienda de libros</a>. '
          f'Los enlaces a Amazon son de afiliado. Recibes este correo porque te suscribiste en aurzane.com. <a href="{{{{BAJA}}}}" style="color:#888">Darme de baja</a>.</td></tr></table></td></tr></table></body></html>')
asunto = f'📚 {libro["titulo"]} y más: tu semana en AURZANE' if libro else 'Tu semana en AURZANE'
os.makedirs('/tmp/boletin', exist_ok=True)
open('/tmp/boletin/boletin.html', 'w', encoding='utf-8').write(html_b)
open('/tmp/boletin/asunto.txt', 'w', encoding='utf-8').write(asunto)
print('asunto:', asunto)
