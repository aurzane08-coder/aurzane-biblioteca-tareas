# -*- coding: utf-8 -*-
"""AURZANE NEXUS en inglés: «Study in Spain» (23/11/2026, plan de inglés acordado con Adrián, etapa 1).

Lo llama gen.py al final, con sus datos ya cargados (universidades de España del RUCT, notas de corte, fotos, ranking).
Escribe en SALIDA/../en/ lo que se publica en https://nexus.aurzane.com/en/ :
  /en/                                  portada «Study in Spain» con todas las universidades españolas
  /en/universities/<slug>/              ficha de cada universidad española con grados (versión inglesa de la ficha española)
  /en/guides/apply-to-a-spanish-university/, /en/guides/student-visa-spain/, /en/guides/cost-of-studying-in-spain/
Nada inventado: los datos salen de los mismos registros oficiales que la versión española, y las guías citan fuentes oficiales con fecha.
Los nombres de los grados se muestran con su traducción (univ/data/grados_en.json, la rellena univ/traducir_grados.py con la IA
y un glosario fijo) y siempre con el nombre oficial en español, que es el que vale para la preinscripción.
Lo que aún no tiene traducción se guarda en univ/data/grados_en_pendientes.json para la siguiente pasada."""
import os, re, json, html, collections

EN_BASE = '/en/'
SITIO = 'https://nexus.aurzane.com'

RAMA_EN = {'Artes y Humanidades': 'Arts and Humanities', 'Ciencias': 'Sciences', 'Ciencias de la Salud': 'Health Sciences',
           'Ciencias Sociales y Jurídicas': 'Social Sciences and Law', 'Ingeniería y Arquitectura': 'Engineering and Architecture',
           'Grado': "Bachelor's degrees", 'Otras': 'Other degrees'}
REGION_EN = {'Andalucía': 'Andalusia', 'Aragón': 'Aragon', 'Asturias': 'Asturias', 'Canarias': 'Canary Islands', 'Cantabria': 'Cantabria',
             'Castilla y León': 'Castile and León', 'Castilla-La Mancha': 'Castilla-La Mancha', 'Cataluña': 'Catalonia',
             'Comunidad Valenciana': 'Valencian Community', 'Extremadura': 'Extremadura', 'Galicia': 'Galicia', 'Comunidad de Madrid': 'Community of Madrid',
             'Madrid': 'Community of Madrid', 'Murcia': 'Region of Murcia', 'Navarra': 'Navarre', 'País Vasco': 'Basque Country', 'Euskadi': 'Basque Country',
             'La Rioja': 'La Rioja', 'Rioja': 'La Rioja', 'Islas Baleares': 'Balearic Islands', 'Ceuta': 'Ceuta', 'Melilla': 'Melilla'}
CIUDAD_EN = {'Sevilla': 'Seville', 'Zaragoza': 'Zaragoza', 'Pamplona/Iruña': 'Pamplona', 'Donostia-San Sebastián': 'San Sebastián',
             'Coruña (A)': 'A Coruña', 'Palmas de Gran Canaria (Las)': 'Las Palmas de Gran Canaria', 'Laguna (San Cristóbal de La)': 'San Cristóbal de La Laguna'}
# Precio medio del crédito de grado, primera matrícula, curso 2024-25 (Ministerio de Ciencia, Innovación y Universidades, enero de 2025).
# Solo las comunidades que publica la nota oficial; para las demás se da el rango nacional.
PRECIO_CRED = {'Galicia': 11.95, 'Asturias': 12.34, 'Canarias': 12.50, 'Andalucía': 12.62, 'Navarra': 19.29, 'Comunidad de Madrid': 18.55, 'Madrid': 18.55, 'Cataluña': 18.15}
F_PRECIOS = ('https://www.ciencia.gob.es/en/Noticias/2025/enero/estadistica-precios.universidades.html', 'Ministry of Science, Innovation and Universities, university fee statistics 2024-25')
F_UAM = ('https://uam.es/uam/en/admision-sistemas-educativos-extranjeros', 'Universidad Autónoma de Madrid, admission from foreign education systems')
F_UV = ('https://www.uv.es/uvweb/delegacion-incorporacion-UV/es/admision-grados/vias-acceso/preuniversitarios-fuera-union-europea-1285870573087.html', 'Universitat de València, access for students from outside the EU')
F_VISA = ('https://www.exteriores.gob.es/Consulados/lisboa/pt/ServiciosConsulares/Paginas/Consular/Visado-de-estudios.aspx', 'Spanish Ministry of Foreign Affairs, study visa requirements')
F_IPREM = ('https://www.ocu.org/dinero/trabajo-paro/noticias/smi-iprem', 'OCU, IPREM 2026 (unchanged at €600 a month)')
F_UNEDASISS = ('https://unedasiss.uned.es/', 'UNEDasiss (UNED), accreditation for students from foreign education systems')
F_HOMOL = ('https://educacionfpydeportes.gob.es/en/dam/jcr:7862606d-5908-4d9e-b147-ec65ac682deb/ayuda-solicitud-hom.pdf', 'Ministry of Education, Vocational Training and Sports, guide to the homologation application')

E = lambda s: html.escape(str(s or ''), quote=True)


def _cargar(p, defecto):
    try: return json.load(open(p, encoding='utf-8'))
    except Exception: return defecto


def generar(G):
    """G = globals() de gen.py."""
    DATOS, SALIDA, HOY, V = G['DATOS'], G['SALIDA'], G['HOY'], G['V']
    BASE = G['BASE']; fmt = G['fmt']; fmt_nota = G['fmt_nota']; commons = G['commons']; iniciales = G['iniciales']; slug = G['slug']
    rank_de = G['rank_de']; NC_CURSO = G.get('NC_CURSO') or ''
    us = [u for u in G['por_pais'].get('España', []) if u['n']]
    if not us:
        print('EN: sin universidades españolas con grados; no se genera'); return
    TRAD = _cargar(os.path.join(DATOS, 'grados_en.json'), {})
    pendientes = set()
    RAIZ = os.path.normpath(os.path.join(SALIDA, '..', 'en'))
    URLS = []

    def esc(ruta, contenido):
        p = os.path.join(RAIZ, ruta); os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, 'w', encoding='utf-8').write(contenido)

    def tr(t):   # nombre oficial en español -> inglés (o None si aún no hay traducción revisada)
        x = TRAD.get(t)
        if not x: pendientes.add(t)
        return x

    def region_en(r): return REGION_EN.get(r, r)
    def ciudad_en(c): return CIUDAD_EN.get(c, c)
    def lugar_en(u): return ', '.join(x for x in [ciudad_en(u['ciudad']), region_en(u['region'])] if x) or 'Spain'
    def tipo_en(u): return 'public' if u['tipo'] == 'Pública' else 'private'
    def url_es(u): return f'{SITIO}{BASE}espana/{u["slug"]}/'
    def url_en(u): return f'{SITIO}{EN_BASE}universities/{u["slug"]}/'

    def cabeza(titulo, desc, canon, alt_es=None, og=None, jsonld=None, precarga=None):
        alts = f'<link rel="alternate" hreflang="en" href="{E(canon)}">' + (f'<link rel="alternate" hreflang="es" href="{E(alt_es)}"><link rel="alternate" hreflang="x-default" href="{E(alt_es)}">' if alt_es else '')
        return f'''<!DOCTYPE html>
<html lang="en" data-v="{V}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<script src="https://aurzane.com/aurzane-paleta.js"></script>
<title>{E(titulo)}</title>
{f'<link rel="preload" as="image" href="{E(precarga)}" fetchpriority="high">' if precarga else ''}
<meta name="description" content="{E(desc)}">
<link rel="canonical" href="{E(canon)}">
{alts}
<meta property="og:title" content="{E(titulo)}">
<meta property="og:description" content="{E(desc)}">
<meta property="og:type" content="website">
<meta property="og:url" content="{E(canon)}">
<meta property="og:image" content="{E(og or SITIO + BASE + 'og.jpg')}">
<meta property="og:locale" content="en_GB">
<meta name="twitter:card" content="summary_large_image">
{f'<script type="application/ld+json">{json.dumps(jsonld, ensure_ascii=False)}</script>' if jsonld else ''}
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{BASE}assets/univ.css?v={V}">
<meta name="google-adsense-account" content="{G['ADS']}">
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={G['ADS']}" crossorigin="anonymous"></script>
</head>
<body class="nexus-en">
<div class="utility"><div class="wrap"><div class="eco"><a href="https://aurzane.com/">AURZANE</a><a href="https://mind.aurzane.com/en/">MIND</a><a class="activo" href="{EN_BASE}">NEXUS</a></div><button type="button" id="btnTema">🌓 Theme</button></div></div>
'''

    def topbar(actual='', es_url=None):
        def a(href, txt, k): return f'<a href="{href}"{" aria-current=page" if k == actual else ""}>{txt}</a>'
        return f'''<header class="topbar"><div class="wrap">
<a class="brand" href="{EN_BASE}">AUR<span class="z">Z</span>ANE<small>/ Study in Spain</small></a>
<button class="menu-btn" type="button" aria-expanded="false" aria-controls="topnav">☰ Menu</button>
<nav class="topnav" id="topnav" aria-label="Study in Spain">
{a(EN_BASE, 'Study in Spain', 'inicio')}
{a(EN_BASE + 'universities/', 'Universities', 'unis')}
{a(EN_BASE + 'guides/apply-to-a-spanish-university/', 'How to apply', 'apply')}
{a(EN_BASE + 'guides/student-visa-spain/', 'Student visa', 'visa')}
{a(EN_BASE + 'guides/cost-of-studying-in-spain/', 'Costs', 'costs')}
<a class="cuenta" href="{E(es_url or SITIO + BASE + 'espana/')}" hreflang="es" lang="es">Español</a>
</nav></div></header>
'''

    def pie():
        return f'''<footer><div class="wrap"><span>© {HOY.year} AURZANE NEXUS · Study in Spain</span><span><a href="{EN_BASE}">Study in Spain</a><a href="{EN_BASE}universities/">Universities</a><a href="{BASE}acerca/" hreflang="es">Sources and method (Spanish)</a><a href="https://aurzane.com/privacidad.html" hreflang="es">Privacy</a></span></div></footer>
<script src="{BASE}assets/univ.js?v={V}" defer></script>
</body></html>
'''

    def migas(*partes):
        return '<p class="migas">' + '<span>/</span>'.join(f'<a href="{h}">{E(t)}</a>' if h else E(t) for t, h in partes) + '</p>'

    def fuentes(lista):
        return '<p class="fuente">Sources: ' + '; '.join(f'<a href="{E(u)}" target="_blank" rel="noopener">{E(t)}</a>' for u, t in lista) + f'. Checked on {HOY.strftime("%-d %B %Y")}.</p>'

    def precio_txt(u):
        if u['tipo'] != 'Pública':
            return ('Private universities set their own tuition fees, and they are usually much higher than at public universities. '
                    'Check the official website of the university for the current price of each degree.')
        p = PRECIO_CRED.get(u['region'])
        base = (f'At public universities the price per credit is set by each regional government. In {region_en(u["region"])} the average price of a credit '
                f'in a first-enrolment bachelor\'s degree was €{p:.2f} in 2024-25, so a full year of 60 ECTS credits costs roughly €{fmt(round(p * 60))}.' if p else
                'At public universities the price per credit is set by each regional government. In 2024-25 the average price of a credit in a first-enrolment '
                'bachelor\'s degree ranged from €11.95 (Galicia) to €19.29 (Navarre), so a full year of 60 ECTS credits costs roughly €720 to €1,160.')
        return base + ' Some regions charge more to students from outside the EU who are not resident in Spain, so check the fee page of the university.'

    def tarjeta(u):
        foto = (f'<div class="uc-foto"><img src="{E(u["foto"])}" alt="" loading="lazy" onerror="this.parentNode.classList.add(\'sin\');this.remove()"><span>{E(iniciales(u["nombre"]))}</span></div>'
                if u.get('foto') else f'<div class="uc-foto sin"><span>{E(iniciales(u["nombre"]))}</span></div>')
        return (f'<article class="uc" data-region="{E(region_en(u["region"]))}" data-tipo="{tipo_en(u)}" data-q="{E((u["nombre"] + " " + u["ciudad"] + " " + region_en(u["region"])).lower())}">{foto}'
                f'<div class="top"><span class="mono" aria-hidden="true">{E(iniciales(u["nombre"]))}</span><div style="min-width:0;flex:1"><h3><a href="{EN_BASE}universities/{u["slug"]}/">{E(u["nombre"])}</a></h3>'
                f'<p class="lugar">📍 {E(lugar_en(u))}</p></div></div><div class="etqs"><span class="etq {"pub" if u["tipo"] == "Pública" else "priv"}">{"Public" if u["tipo"] == "Pública" else "Private"}</span>'
                + ('<span class="etq">Online</span>' if u['extra'].get('en_linea') else '') +
                f'</div><div class="pie"><span><b>{fmt(u["n"])}</b> bachelor\'s degree{"s" if u["n"] != 1 else ""}</span><span aria-hidden="true">→</span></div></article>')

    # ------------------------------------------------------------------ fichas
    for u in us:
        canon = url_en(u)
        grupos = collections.OrderedDict()
        for c in sorted(u['carreras'], key=lambda c: (tr(c['n']) or c['n']).lower()):
            grupos.setdefault(c['grupo'] or 'Otras', []).append(c)
        orden_g = sorted(grupos, key=lambda g: (-len(grupos[g]), g))
        chips = ''
        if len(orden_g) > 1:
            chips = ('<div class="chips" role="group" aria-label="Filter by branch"><button type="button" class="chip" aria-pressed="true" data-area="">All</button>' +
                     ''.join(f'<button type="button" class="chip" aria-pressed="false" data-area="{E(g)}">{E(RAMA_EN.get(g, g))} ({len(grupos[g])})</button>' for g in orden_g) + '</div>')
        lis = ''
        for g in orden_g:
            items = ''
            for c in grupos[g]:
                en = tr(c['n'])
                der = []
                if c.get('nota'): der.append(f'Cut-off mark {fmt_nota(c["nota"]).replace(",", ".")} / 14')
                if c.get('cred'): der.append(f'{c["cred"]} ECTS')
                if c.get('mod'): der.append('Online' if c['mod'] == ['En línea'] else ' · '.join(c['mod']))
                if c.get('sedes') and (len(c['sedes']) > 1 or c['sedes'][0] != u['ciudad']): der.append(', '.join(ciudad_en(s) for s in c['sedes'][:4]) + ('…' if len(c['sedes']) > 4 else ''))
                nombre = (f'{E(en)}<small lang="es">Official name: {E(c["n"])}</small>' if en else f'<span lang="es">{E(c["n"])}</span><small>Official name in Spanish (English translation coming soon)</small>')
                items += f'<li><span>{nombre}</span>{"<small>" + E(" · ".join(der)) + "</small>" if der else ""}</li>'
            lis += f'<div class="grupo" data-area="{E(g)}"><h3><span>{E(RAMA_EN.get(g, g))}</span><span>{len(grupos[g])}</span></h3><ul class="carreras">{items}</ul></div>'
        n = u['n']
        con_nota = sum(1 for c in u['carreras'] if c.get('nota'))
        bloque_c = (f'<section class="card" id="degrees"><div class="carr-cab"><h2>{fmt(n)} official bachelor\'s degree{"s" if n != 1 else ""}</h2>'
                    + (f'<input type="search" class="carr-busca" placeholder="Search its degrees" aria-label="Search degrees">' if n > 8 else '') + f'</div>{chips}{lis}'
                    '<p id="carrVacio" class="sub" hidden>No degrees match that search.</p>'
                    + (f'<p class="sub" style="margin-top:12px">Cut-off marks are the lowest admission grade that got a place in the {E(NC_CURSO) or "latest"} academic year, on the Spanish scale from 5 to 14. '
                       'They change every year with the number of places and applicants.</p>' if con_nota else '') + '</section>')
        lugar = lugar_en(u)
        tipo = tipo_en(u)
        rk = rank_de(u)
        intro = (f'{u["nombre"]} is a {tipo} university based in {lugar}, Spain. It offers {fmt(n)} official bachelor\'s degree{"s" if n != 1 else ""} '
                 f'listed in the Spanish government\'s Registry of Universities, Centres and Degrees (RUCT).')
        if u['extra'].get('anio'): intro += f' It was established in {u["extra"]["anio"]}.'
        if u['extra'].get('en_linea'): intro += ' It teaches online, so you can study without moving to its city.'
        top = [RAMA_EN.get(g, g) for g in orden_g if g in RAMA_EN and g not in ('Grado', 'Otras')][:3]
        if len(top) > 1: intro += f' Most of its degrees are in {", ".join(top[:-1])} and {top[-1]}.'
        intl = (f'<section class="card" id="international"><h2>Studying at {E(u["nombre"])} as an international student</h2>'
                '<p><b>From an EU country, or with the International or European Baccalaureate:</b> you can apply with your own school-leaving qualification. '
                'You first get an accreditation from UNEDasiss, the service run by the Spanish open university (UNED), which converts your grade to the Spanish scale. '
                'You can raise your admission grade up to 14 points with the specific competence tests (PCE).</p>'
                '<p><b>From outside the EU:</b> you usually need to have your secondary studies recognised as equivalent to the Spanish Bachillerato (homologación), '
                'through the Ministry of Education, and then get the UNEDasiss accreditation. You can apply for the accreditation as soon as you have filed the homologation request.</p>'
                '<p><b>Language:</b> most bachelor\'s degrees at Spanish universities are taught in Spanish, and in some regions partly in Catalan, Galician or Basque. '
                'Many universities ask international students for a B2 level of Spanish. Check the language of each degree on the university\'s website.</p>'
                f'<p><a href="{EN_BASE}guides/apply-to-a-spanish-university/">Read the full guide: how to apply to a Spanish university →</a></p></section>')
        costes = (f'<section class="card" id="costs"><h2>Tuition fees</h2><p>{E(precio_txt(u))}</p>'
                  f'<p>If you come from outside the EU, the student visa asks you to show at least €600 a month (100% of the IPREM, unchanged in 2026) to cover your living costs. '
                  f'<a href="{EN_BASE}guides/cost-of-studying-in-spain/">See the full cost guide →</a></p></section>')
        faq = [(f'Is {u["nombre"]} public or private?', f'According to the official registry it is a {tipo} university.'),
               (f'Where is {u["nombre"]}?', f'It is based in {lugar}, Spain.' + (' It also teaches online.' if u['extra'].get('en_linea') else '')),
               (f'How many degrees does {u["nombre"]} offer?', f'The official registry lists {fmt(n)} bachelor\'s degree{"s" if n != 1 else ""}. You can see all of them on this page, grouped by branch of knowledge.'),
               ('Can international students study here?', 'Yes. Students from other countries apply through UNEDasiss and, if they come from outside the EU, usually need the homologation of their secondary studies first. Most degrees are taught in Spanish.')]
        faq_h = ''.join(f'<details><summary>{E(q)}</summary><p>{E(r)}</p></details>' for q, r in faq)
        about = f'<section class="card guia-auto"><h2>About {E(u["nombre"])}</h2><p>{E(intro)}</p><h3>Frequently asked questions</h3>{faq_h}</section>'
        dato = [('Country', 'Spain'), ('City', E(ciudad_en(u['ciudad']) or '-'))]
        if u['region']: dato.append(('Region', E(region_en(u['region']))))
        dato.append(('Type', 'Public' if u['tipo'] == 'Pública' else 'Private'))
        if u['extra'].get('acronimo'): dato.append(('Acronym', E(u['extra']['acronimo'])))
        if u['extra'].get('anio'): dato.append(('Established', E(u['extra']['anio'])))
        if u['extra'].get('en_linea'): dato.append(('Mode', 'Online'))
        if rk: dato.append(('World ranking', f'No. {fmt(rk[0])} in the world · No. {fmt(rk[1])} in Spain <small>(by scientific citations, OpenAlex)</small>'))
        if u['web']:
            dom = re.sub(r'^https?://(www\.)?', '', u['web']).rstrip('/')
            dato.append(('Website', f'<a href="{E(u["web"])}" target="_blank" rel="noopener nofollow">{E(dom)}</a>'))
        datos_h = '<dl class="datos">' + ''.join(f'<div><dt>{k}</dt><dd>{v}</dd></div>' for k, v in dato) + '</dl>'
        vec = [v for v in us if v is not u and v['ciudad'] == u['ciudad']][:6]
        cerca = (f'<section class="card"><h2>Other universities in {E(ciudad_en(u["ciudad"]))}</h2><ul class="cercanas">' + ''.join(
            f'<li><a href="{EN_BASE}universities/{v["slug"]}/">{E(v["nombre"])}</a><small>{"Public" if v["tipo"] == "Pública" else "Private"} · {fmt(v["n"])} degree{"s" if v["n"] != 1 else ""}</small></li>' for v in vec) + '</ul></section>') if vec else ''
        cta = (f'<section class="cta"><b>Prefer Spanish?</b><p>This page is also available in Spanish, with the Spanish admission grade calculator.</p>'
               f'<a class="btn btn-luz" href="{url_es(u)}" hreflang="es" lang="es">Ver en español</a></section>')
        meta = [f'<li>📍 {E(lugar)}</li>', f'<li>{"🏛️" if u["tipo"] == "Pública" else "🏢"} {"Public" if u["tipo"] == "Pública" else "Private"} university</li>', f'<li>📚 {fmt(n)} bachelor\'s degree{"s" if n != 1 else ""}</li>']
        if rk: meta.append(f'<li>🌍 No. {fmt(rk[0])} in the world</li>')
        tit = next(t for t in (f'{u["nombre"]}: {fmt(n)} degrees, admission and fees', f'{u["nombre"]}: degrees, admission and fees', f'{u["nombre"]}: degrees and fees', u['nombre']) if len(t) <= 65)
        desc = f'{u["nombre"]} ({lugar}, Spain): its {fmt(n)} official bachelor\'s degrees in English, cut-off marks, tuition fees and how to apply as an international student.'
        jl = {'@context': 'https://schema.org', '@type': 'CollegeOrUniversity', 'name': u['nombre'], 'url': u['web'] or canon,
              'address': {'@type': 'PostalAddress', 'addressLocality': u['ciudad'] or None, 'addressRegion': u['region'] or None, 'addressCountry': 'ES'}}
        jl['address'] = {k: v for k, v in jl['address'].items() if v}
        fa = u.get('foto_archivo') or u.get('foto_ciudad')
        hf = f' style="--foto:url(\'{commons(fa, 960)}\')"' if fa else ''
        cred = (f'<a class="credito-foto" href="https://commons.wikimedia.org/wiki/File:{E(fa.replace(" ", "_"))}" target="_blank" rel="noopener">📷 Photo: Wikimedia Commons</a>') if fa else ''
        h = cabeza(tit, desc, canon, url_es(u), og=commons(fa, 1280) if fa else None, jsonld=jl, precarga=commons(fa, 960) if fa else None) + topbar('unis', url_es(u)) + f'''
<main><section class="hero ficha-h{' con-foto' if hf else ''}"{hf}><div class="wrap">{migas(("Study in Spain", EN_BASE), ("Universities", EN_BASE + "universities/"), (u["nombre"], ""))}
<div class="fila" style="margin-top:16px"><span class="mono" aria-hidden="true">{E((u["extra"].get("acronimo") or iniciales(u["nombre"]))[:5])}</span><div><h1 style="margin:0">{E(u["nombre"])}</h1></div></div>
<ul class="meta">{''.join(meta)}</ul>
<div class="acc">{f'<a class="btn btn-luz" href="{E(u["web"])}" target="_blank" rel="noopener nofollow">Official website ↗</a>' if u["web"] else ''}<a class="btn btn-claro" href="#degrees">See degrees</a><a class="btn btn-claro" href="#international">How to apply</a><a class="btn btn-claro" href="{url_es(u)}" hreflang="es" lang="es">Español</a></div>
{cred}</div></section>
<div class="wrap"><div class="ficha"><div>{bloque_c}{intl}{costes}{about}</div>
<aside><section class="card"><h2>Key facts</h2>{datos_h}</section>{cta}{cerca}</aside></div>
{fuentes([("https://www.educacion.gob.es/ruct/home", "Registry of Universities, Centres and Degrees (RUCT), Spanish Ministry of Science, Innovation and Universities"), F_PRECIOS, F_UAM, F_IPREM])}
</div></main>''' + pie()
        esc(f'universities/{u["slug"]}/index.html', h)
        URLS.append(canon)

    # ------------------------------------------------------------------ listado y portada
    regiones = sorted({region_en(u['region']) for u in us if u['region']})
    filtro = (f'<div class="en-filtro"><label><span class="vh">Search</span><input type="search" id="enQ" placeholder="University, city or region" autocomplete="off"></label>'
              f'<label><span class="vh">Region</span><select id="enR"><option value="">All regions</option>{"".join(f"<option>{E(r)}</option>" for r in regiones)}</select></label>'
              '<label><span class="vh">Type</span><select id="enT"><option value="">Public and private</option><option value="public">Public</option><option value="private">Private</option></select></label>'
              f'<p id="enN" aria-live="polite"><b>{len(us)}</b> universities</p></div>')
    js = ('<script>(function(){var q=document.getElementById("enQ"),r=document.getElementById("enR"),t=document.getElementById("enT"),n=document.getElementById("enN");'
          'function f(){var a=(q.value||"").toLowerCase().trim(),k=0;document.querySelectorAll("#enGrid .uc").forEach(function(c){'
          'var ok=(!a||c.dataset.q.indexOf(a)>=0)&&(!r.value||c.dataset.region===r.value)&&(!t.value||c.dataset.tipo===t.value);c.hidden=!ok;if(ok)k++;});'
          'n.innerHTML="<b>"+k+"</b> universit"+(k===1?"y":"ies");}[q,r,t].forEach(function(x){x.addEventListener("input",f);x.addEventListener("change",f);});})();</script>')
    orden = sorted(us, key=lambda x: (0 if x['tipo'] == 'Pública' else 1, -x['n'], x['nombre']))
    grid = f'<div class="grid-u" id="enGrid">{"".join(tarjeta(u) for u in orden)}</div>'
    n_pub = sum(1 for u in us if u['tipo'] == 'Pública'); n_grados = sum(u['n'] for u in us)
    lista_h = cabeza(f'Universities in Spain: {len(us)} public and private universities', f'All {len(us)} Spanish universities with official bachelor\'s degrees, in English: degrees, cut-off marks, fees and how to apply from abroad.',
                     SITIO + EN_BASE + 'universities/', SITIO + BASE + 'espana/') + topbar('unis') + f'''
<main><section class="hero"><div class="wrap">{migas(("Study in Spain", EN_BASE), ("Universities", ""))}
<h1>Universities in Spain</h1><p class="lead">{len(us)} universities, {n_pub} of them public, with {fmt(n_grados)} official bachelor's degrees between them. Every degree comes from the Spanish government's official registry.</p></div></section>
<div class="wrap" style="padding-top:28px">{filtro}{grid}</div></main>{js}''' + pie()
    esc('universities/index.html', lista_h)
    URLS.append(SITIO + EN_BASE + 'universities/')

    destacadas = sorted(us, key=lambda x: (-(1 if rank_de(x) else 0), (rank_de(x) or [10 ** 9])[0], -x['n']))[:6]
    guia_cards = ''.join(f'<a class="en-guia" href="{EN_BASE}guides/{s}/"><b>{t}</b><span>{d}</span></a>' for s, t, d in (
        ('apply-to-a-spanish-university', 'How to apply', 'UNEDasiss, homologation, the 14-point grade and the language you need.'),
        ('student-visa-spain', 'Student visa', 'Documents, the money you must show and what to do when you arrive.'),
        ('cost-of-studying-in-spain', 'What it costs', 'Public and private tuition, and the minimum budget for living costs.')))
    portada = cabeza('Study in Spain: universities, admission and costs for international students',
                     f'Everything you need to study a bachelor\'s degree in Spain: {len(us)} universities and {fmt(n_grados)} official degrees in English, how to apply from abroad, the student visa and real costs.',
                     SITIO + EN_BASE, SITIO + BASE + 'espana/') + topbar('inicio') + f'''
<main><section class="hero en-hero"><div class="wrap">
<p class="eyebrow">AURZANE NEXUS · in English</p>
<h1>Study in Spain</h1>
<p class="lead">Spain has {len(us)} universities with {fmt(n_grados)} official bachelor's degrees. Public universities charge from about €720 a year, and you can apply from anywhere in the world. Here is how it works, step by step, with official sources.</p>
<div class="acc"><a class="btn btn-luz" href="{EN_BASE}universities/">Browse the universities</a><a class="btn btn-claro" href="{EN_BASE}guides/apply-to-a-spanish-university/">How to apply</a></div></div></section>
<div class="wrap" style="padding-top:32px">
<section class="en-guias">{guia_cards}</section>
<h2 class="en-h2">Top universities by research</h2>
<div class="grid-u">{"".join(tarjeta(u) for u in destacadas)}</div>
<p style="margin:18px 0 40px"><a class="btn btn-osc" href="{EN_BASE}universities/">See all {len(us)} universities</a></p>
<section class="card guia-auto"><h2>Studying a bachelor's degree in Spain, in short</h2>
<p>A Spanish bachelor's degree (<i>grado</i>) usually lasts four years and 240 ECTS credits, and some, like medicine or architecture, last longer. Degrees are official only if they appear in the government's registry (RUCT); every degree on this site comes from it.</p>
<p>Admission works on a scale from 5 to 14. Students from the EU and from education systems with an agreement apply with their own school-leaving grade, converted by UNEDasiss. Students from other countries usually have their secondary studies recognised first (<i>homologación</i>). Everyone can raise their grade with extra exams.</p>
<p>Public universities are subsidised: in 2024-25 a credit cost between €11.95 and €19.29 on average depending on the region. If you come from outside the EU you will also need a student visa, which asks you to show at least €600 a month for living costs.</p></section>
{fuentes([F_UAM, F_PRECIOS, F_VISA, F_IPREM])}
</div></main>''' + pie()
    esc('index.html', portada)
    URLS.insert(0, SITIO + EN_BASE)

    # ------------------------------------------------------------------ guías (texto propio, revisado a mano; fuentes oficiales)
    def guia(s, titulo, desc, h1, cuerpo, fts, es_url=None):
        canon = f'{SITIO}{EN_BASE}guides/{s}/'
        hh = cabeza(titulo, desc, canon, es_url) + topbar({'apply-to-a-spanish-university': 'apply', 'student-visa-spain': 'visa', 'cost-of-studying-in-spain': 'costs'}[s], es_url) + f'''
<main><section class="hero"><div class="wrap">{migas(("Study in Spain", EN_BASE), ("Guides", ""), (h1, ""))}<h1>{E(h1)}</h1><p class="lead">{E(desc)}</p></div></section>
<div class="wrap en-guia-txt" style="padding-top:28px"><article class="card guia-auto">{cuerpo}</article>
<section class="cta" style="margin-top:24px"><b>Find your university</b><p>{len(us)} Spanish universities with all their official degrees, cut-off marks and fees.</p><a class="btn btn-luz" href="{EN_BASE}universities/">Browse universities</a></section>
{fuentes(fts)}</div></main>''' + pie()
        esc(f'guides/{s}/index.html', hh); URLS.append(canon)

    guia('apply-to-a-spanish-university', 'How to apply to a Spanish university as an international student',
         'The admission route depends on where you finished school. This guide explains UNEDasiss, homologation, the 14-point grade and the Spanish language requirement.',
         'How to apply to a Spanish university',
         '''<h2>1. Find out which route applies to you</h2>
<p>Spanish universities admit international students for bachelor's degrees through two main routes. Which one you follow depends on the education system where you finished secondary school, not on your nationality.</p>
<h3>Route A: EU countries and systems with an agreement</h3>
<p>This route is for students with a school-leaving qualification from an EU country, the International Baccalaureate, the European Baccalaureate, or a country that has a reciprocity agreement with Spain, as long as that qualification gives access to university in its own country.</p>
<ul><li>You request an <b>accreditation from UNEDasiss</b>, a service of the Spanish open university (UNED). It certifies your studies and gives you an access grade from 5 to 10. You do not sit the Spanish university entrance exam.</li>
<li>To compete for degrees with high demand, you can add up to 4 more points with the <b>specific competence tests (PCE)</b> run by UNEDasiss, or with the optional part of the Spanish entrance exam (PAU). Your admission grade can then reach 14.</li></ul>
<h3>Route B: other education systems</h3>
<p>If you finished school outside the EU, in a system with no agreement, you normally follow these steps:</p>
<ol><li><b>Homologation.</b> Ask the Spanish Ministry of Education, Vocational Training and Sports to recognise your secondary studies as equivalent to the Spanish <i>Bachillerato</i>. This is called <i>homologación</i>.</li>
<li><b>UNEDasiss accreditation.</b> You can request it as soon as you have filed the homologation request; you do not need to wait for the ministry's decision. Your homologated grade gives an access grade.</li>
<li><b>PCE exams (optional but often decisive).</b> At some universities the access grade combines 60% of your homologated grade with the PCE results, and the admission grade adds your two best weighted subjects, up to 14 points.</li></ol>
<p>The exact formula and the role of each test can vary between regions and universities, so check the admission page of the university you choose.</p>
<h2>2. Apply for a place (preinscripción)</h2>
<p>With your accreditation you apply for places through the <i>preinscripción</i> of each region or university, usually in early summer. You list the degrees you want in order of preference. Places are allocated by admission grade, and the lowest grade that gets a place becomes that year's <b>cut-off mark</b> (<i>nota de corte</i>). You can see the cut-off marks of each degree on our university pages.</p>
<h2>3. Check the language requirement</h2>
<p>Most bachelor's degrees at Spanish universities are taught in Spanish, and in Catalonia, the Valencian Community, the Balearic Islands, Galicia and the Basque Country some classes may be in the regional language. Many universities ask students whose education was not in Spanish for a <b>B2 level of Spanish</b>, shown with a certificate such as the DELE or the SIELE, or recorded in the UNEDasiss accreditation.</p>
<h2>4. Plan the visa and the costs</h2>
<p>If you are not an EU citizen, start the <a href="/en/guides/student-visa-spain/">student visa</a> as soon as you have your admission letter. Read our <a href="/en/guides/cost-of-studying-in-spain/">cost guide</a> to plan tuition and living costs.</p>
<h2>Frequently asked questions</h2>
<details><summary>Do I need to take the Spanish entrance exam (PAU)?</summary><p>No. International students apply with the UNEDasiss accreditation. The PAU's optional part, or the PCE exams, only serve to raise your grade.</p></details>
<details><summary>Can I apply before the homologation is approved?</summary><p>Yes, in general you can request the UNEDasiss accreditation with the receipt of your homologation request. If your admission is provisional, you must later bring the final documents within the deadline.</p></details>
<details><summary>Are there degrees taught in English?</summary><p>Some universities offer degrees or groups taught in English, especially in business, engineering and international studies, but they are a minority. Check each university's website.</p></details>''',
         [F_UAM, F_UV, F_UNEDASISS, F_HOMOL], SITIO + BASE + 'espana/')

    guia('student-visa-spain', 'Spain student visa: requirements, money and steps (2026)',
         'Who needs a Spanish student visa, the documents the consulate asks for, how much money you must show and what to do when you arrive.',
         'Spain student visa',
         '''<h2>Who needs it</h2>
<p>Citizens of the European Union, the European Economic Area and Switzerland do not need a visa to study in Spain. Everyone else needs a <b>study visa</b> (<i>visado de estudios</i>) for a stay of more than 90 days, requested at the Spanish consulate that covers the place where you live.</p>
<h2>Documents the consulate asks for</h2>
<ul><li>The national visa application form, completed and signed, and a recent passport photo.</li>
<li>A valid passport covering the whole stay, with two blank pages, issued less than 10 years ago.</li>
<li><b>Proof of admission</b> to a full-time programme at an authorised institution.</li>
<li><b>Proof of financial means:</b> at least 100% of the IPREM for each month of stay, plus 75% for the first family member who comes with you and 50% for each additional one. If you have paid your accommodation for the whole stay in advance, that amount is deducted.</li>
<li><b>Health insurance</b> from an insurer authorised in Spain, covering everything the Spanish public health system covers.</li>
<li>For stays of more than 180 days: a <b>criminal record certificate</b> from the countries where you lived in the last five years, and a <b>medical certificate</b>, both legalised or apostilled and translated into Spanish when needed.</li>
<li>Payment of the visa fee: €80 in general. Citizens of some countries, such as the United States, Canada, the United Kingdom and Australia, pay a different amount by reciprocity.</li></ul>
<h2>How much money you must show</h2>
<p>The IPREM is the Spanish reference index used for this requirement. It stays at <b>€600 a month in 2026</b>, unchanged since 2023, so a student coming alone must show at least €600 for each month of the stay, which is €7,200 for a full year.</p>
<h2>Timing</h2>
<p>Apply in person, with an appointment, well before your course starts. The consulate has one month to decide, which can be longer if it asks for more documents or an interview. Once approved, you have two months to collect the visa.</p>
<h2>When you arrive in Spain</h2>
<p>If your studies last six months or less, the visa covers the whole stay. If they last longer, the visa is valid for 90 days and you must apply for the <b>Foreigner Identity Card (TIE)</b> within one month of entering Spain.</p>
<p class="sub">Requirements can differ slightly between consulates. Always check the website of the Spanish consulate that covers where you live before you apply.</p>''',
         [F_VISA, F_IPREM])

    guia('cost-of-studying-in-spain', 'Cost of studying in Spain: tuition fees and living costs (2026)',
         'What a bachelor\'s degree costs at Spanish public and private universities, and the minimum budget for living costs that the student visa asks for.',
         'Cost of studying in Spain',
         '''<h2>Tuition at public universities</h2>
<p>Public universities are funded by the regional governments, which set the price of each credit every year. According to the Ministry of Science, Innovation and Universities, in 2024-25 the average price of a credit in a first-enrolment bachelor's degree was the lowest in its historical series. The cheapest regions were Galicia (€11.95), Asturias (€12.34), the Canary Islands (€12.50) and Andalusia (€12.62); the most expensive were Navarre (€19.29), the Community of Madrid (€18.55) and Catalonia (€18.15).</p>
<p>A full year has 60 ECTS credits, so a first year at a public university costs roughly <b>€720 to €1,160</b> in tuition, depending on the region. Repeated subjects cost more, and some regions charge higher prices to students from outside the EU who are not resident in Spain. Each university publishes its exact fees.</p>
<h2>Tuition at private universities</h2>
<p>Private universities set their own fees, which are usually several thousand euros a year and vary a lot between degrees. Check the official website of each university.</p>
<h2>Living costs</h2>
<p>The Spanish student visa asks you to show at least <b>€600 a month</b> (100% of the IPREM in 2026) for your living costs. That is the legal minimum, not a comfortable budget: rent varies a lot between cities, and Madrid, Barcelona, the Basque Country and the Balearic Islands are usually the most expensive.</p>
<h2>Scholarships</h2>
<p>Universities and regional governments offer scholarships and fee reductions, some of them open to international students. Ask the international office of the university you choose.</p>''',
         [F_PRECIOS, F_IPREM, F_VISA])

    # sitemap propio (también lo recoge el mapa diario del dominio)
    x = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + ''.join(
        f'<url><loc>{E(u)}</loc><lastmod>{HOY.isoformat()}</lastmod></url>\n' for u in URLS) + '</urlset>\n'
    open(os.path.join(RAIZ, '..', 'sitemap-en.xml'), 'w', encoding='utf-8').write(x)
    json.dump(sorted(pendientes), open(os.path.join(DATOS, 'grados_en_pendientes.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    print(f'EN: {len(us)} universidades, {len(URLS)} páginas en inglés; {len(pendientes)} nombres de grado sin traducir todavía')
