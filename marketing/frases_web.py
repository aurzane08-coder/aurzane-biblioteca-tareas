"""Frases de autores clásicos tomadas de Wikiquote en español (licencia CC BY-SA), para los vídeos y las tarjetas.
(17/11/2026, petición de Adrian: frases de Proverbia o de otros sitios, siempre distintas.)
Solo autores de dominio público (fallecidos hace más de 80 años) y frases cortas que se leen bien en un vídeo.
Se ejecuta en la planificación semanal; guarda marketing/frases_web.json: [[frase, "Autor (vía Wikiquote)"], ...]."""
import json, os, re, sys, urllib.request, urllib.parse, html
D = os.path.dirname(os.path.abspath(__file__))
AUTORES = ['Séneca', 'Marco Aurelio', 'Epicteto', 'Confucio', 'Lao-Tse', 'Aristóteles', 'Platón', 'Sócrates', 'Benjamin Franklin',
           'Ralph Waldo Emerson', 'Henry David Thoreau', 'León Tolstói', 'Antonio Machado', 'Miguel de Cervantes', 'Baltasar Gracián',
           'Johann Wolfgang von Goethe', 'Friedrich Nietzsche', 'William James', 'Leonardo da Vinci', 'Victor Hugo', 'Mark Twain',
           'Rabindranath Tagore', 'Khalil Gibran', 'Miguel de Unamuno', 'José Martí', 'Amado Nervo', 'Santiago Ramón y Cajal',
           'Concepción Arenal', 'Plutarco', 'Cicerón', 'Montaigne', 'Blaise Pascal', 'Arthur Schopenhauer', 'Fiódor Dostoyevski',
           'Oscar Wilde', 'Benito Pérez Galdós', 'Gustavo Adolfo Bécquer', 'Rubén Darío', 'Federico García Lorca', 'Ramón María del Valle-Inclán']
TEMAS = re.compile(r'\b(vida|vivir|tiempo|alma|ánimo|miedo|dolor|feliz|felicidad|esfuerzo|paciencia|amor|amistad|sabio|sabiduría|aprender|'
                   r'camino|valor|fuerza|esperanza|hábito|trabajo|calma|paz|mente|pensamiento|corazón|libertad|cambio|fracas|éxito|'
                   r'conocer|conócete|bondad|virtud|verdad|presente|mañana|hoy|soledad|descanso|voluntad)', re.I)
MALO = re.compile(r'\b(muerte|morir|matar|suicid|dios|guerra|sangre|mujer(es)? (son|es)|raza|esclav)', re.I)


def wikitexto(pagina):
    u = 'https://es.wikiquote.org/w/api.php?' + urllib.parse.urlencode({'action': 'parse', 'page': pagina, 'prop': 'wikitext', 'format': 'json', 'redirects': 1})
    try:
        with urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'AURZANE/1.0 (hola@aurzane.com)'}), timeout=40) as r:
            return json.load(r)['parse']['wikitext']['*']
    except Exception as e:
        print('Wikiquote', pagina, str(e)[:80]); return ''


def limpia(t):
    t = re.sub(r'<ref[^>]*>.*?</ref>|<ref[^>]*/>|<[^>]+>', '', t, flags=re.S)
    t = re.sub(r'\[\[(?:[^|\]]*\|)?([^\]]+)\]\]', r'\1', t)
    t = re.sub(r'\{\{[^}]*\}\}', '', t); t = re.sub(r"'{2,}", '', t)
    t = re.sub(r'[«»"“”]', '', html.unescape(t)).strip()
    return re.sub(r'\s+', ' ', t)


def frases_de(autor):
    w = wikitexto(autor); out = []
    for ln in w.splitlines():
        if not re.match(r'^\*\s*[^*:]', ln): continue   # solo citas de primer nivel (las de segundo nivel son fuentes o notas)
        f = limpia(ln[1:])
        if not (30 <= len(f) <= 150) or not TEMAS.search(f) or MALO.search(f): continue
        if re.search(r'[\[\]{}|=]|http|Fuente|Cita|Atribuid|traducci', f, re.I): continue
        if not re.search(r'[áéíóúñ¿¡]|\b(el|la|que|de|no|es)\b', f): continue   # en español
        out.append([f if f[-1] in '.!?»' else f + '.', autor + ' (vía Wikiquote)'])
    return out[:12]


def main():
    todas, vistas = [], set()
    for a in AUTORES:
        for f, au in frases_de(a):
            k = re.sub(r'\W+', '', f.lower())
            if k not in vistas: vistas.add(k); todas.append([f, au])
    if len(todas) < 40: print('::warning::Pocas frases de Wikiquote:', len(todas), '(se deja la lista anterior)'); return
    json.dump(todas, open(os.path.join(D, 'frases_web.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    print(f'::notice title=Frases::{len(todas)} frases de {len({a for _, a in todas})} autores clásicos (Wikiquote, CC BY-SA)')


if __name__ == '__main__': main()
