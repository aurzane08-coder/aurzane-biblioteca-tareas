# Genera la portada de aurzane.com (rediseño noviembre 2026). Uso: python3 portada/generar.py <index_actual> <salida>
# Conserva la cabecera <head> del servidor (SEO, verificaciones, AdSense) y rehace el cuerpo.
import re, sys, html
src, out = sys.argv[1], sys.argv[2]
t = open(src, encoding='utf-8').read()
head = t[t.find('<head>') + 6:t.find('</head>')]
head = re.sub(r'<style>.*?</style>', '', head, flags=re.S)
U = lambda i, w=900: f'https://images.unsplash.com/photo-{i}?w={w}&q=72&auto=format&fit=crop'
E = html.escape
import json, os
try: CIF = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'cifras', 'cifras.json'), encoding='utf-8'))
except Exception: CIF = {}
mil = lambda n: f'{n:,}'.replace(',', '.')
NU, NP = mil(CIF.get('universidades') or 6411), CIF.get('paises') or 55
# sin el nombre del autor en los datos estructurados de la portada
head = re.sub(r',?"founder":\{[^{}]*\}', '', head)

TESTS = [  # (slug o url, nombre, pregunta, duración, mundo, foto)
 ('https://mind.aurzane.com/test-de-ansiedad/', 'Ansiedad', '¿Lo que sientes es ansiedad?', '2 min', 'mind', '1505142468610-359e7d316be0'),
 ('https://mind.aurzane.com/test-de-depresion/', 'Estado de ánimo', '¿Cómo está tu ánimo estas semanas?', '2 min', 'mind', '1529665253569-6d01c0eaf7b6'),
 ('https://mind.aurzane.com/test-de-estres/', 'Estrés', '¿Cuánto estrés llevas encima?', '1 min', 'mind', '1541199249251-f713e6145474'),
 ('https://mind.aurzane.com/test-de-autoestima/', 'Autoestima', '¿Cómo te valoras de verdad?', '2 min', 'mind', '1517841905240-472988babdf9'),
 ('https://mind.aurzane.com/test-de-burnout/', 'Burnout', '¿Tu trabajo o tus estudios te están quemando?', '2 min', 'mind', '1499750310107-5fef28a66643'),
 ('https://mind.aurzane.com/test-de-tdah/', 'TDAH adulto', '¿Tu forma de concentrarte podría ser TDAH?', '2 min', 'mind', '1434030216411-0b793f4b4173'),
 ('https://mind.aurzane.com/test-de-resiliencia/', 'Resiliencia', '¿Cuánto tardas en levantarte tras un golpe?', '1 min', 'mind', '1466692476868-aef1dfb1e735'),
 ('https://mind.aurzane.com/test-de-autocompasion/', 'Autocompasión', '¿Te tratas con la amabilidad que das a otros?', '2 min', 'mind', '1544027993-37dbfe43562a'),
 ('https://mind.aurzane.com/test-de-autoeficacia/', 'Autoeficacia', '¿Cuánto confías en salir adelante?', '2 min', 'mind', '1464822759023-fed622ff2c3b'),
 ('https://mind.aurzane.com/test-de-soledad/', 'Soledad', '¿Te sientes solo aunque estés rodeado de gente?', '30 s', 'mind', '1512438248247-f0f2a5a8b7f0'),
 ('https://mind.aurzane.com/test-de-satisfaccion-con-la-vida/', 'Satisfacción con la vida', '¿Qué tan satisfecho estás con tu vida?', '1 min', 'mind', '1507525428034-b723cf961d3e'),
 ('https://live.aurzane.com/test-de-bienestar/', 'Bienestar', '¿Cómo has estado de verdad estas dos semanas?', '1 min', 'live', '1506126613408-eca07ce68773'),
 ('https://live.aurzane.com/test-de-sueno/', 'Sueño', '¿Duermes lo que tu cuerpo necesita?', '2 min', 'live', '1541781774459-bb2af2f05b55'),
 ('https://live.aurzane.com/test-de-habitos/', 'Hábitos de vida', '¿Qué nota le pondrías a tu estilo de vida?', '2 min', 'live', '1490645935967-10de6ba17061'),
]
EJ = [('https://mind.aurzane.com/ejercicios/respiracion-4-7-8/', 'Respiración 4-7-8', 'Para dormir y calmar la ansiedad', '3 min'),
      ('https://mind.aurzane.com/ejercicios/tecnica-5-4-3-2-1/', 'Técnica 5-4-3-2-1', 'Para volver al presente en una crisis', '3 min'),
      ('https://mind.aurzane.com/ejercicios/escaneo-corporal/', 'Escaneo corporal', 'Para soltar la tensión del cuerpo', '7 min'),
      ('https://mind.aurzane.com/ejercicios/pausa-de-autocompasion/', 'Pausa de autocompasión', 'Para un momento difícil', '3 min')]
CALC = [('Salud', [('IMC', 'https://live.aurzane.com/calculadora-imc/'), ('Calorías', 'https://live.aurzane.com/calculadora-calorias/'), ('Agua al día', 'https://live.aurzane.com/calculadora-agua/'), ('Embarazo', 'https://live.aurzane.com/calculadora-embarazo/')]),
        ('Dinero y vivienda', [('Hipoteca', 'https://build.aurzane.com/calculadora-hipoteca/'), ('Sueldo neto', 'https://build.aurzane.com/calculadora-sueldo-neto/'), ('Interés compuesto', 'https://live.aurzane.com/calculadora-interes-compuesto/'), ('Reforma', 'https://build.aurzane.com/calculadora-reforma/')]),
        ('Fechas y números', [('Edad exacta', 'https://live.aurzane.com/calculadora-edad/'), ('Días entre fechas', 'https://live.aurzane.com/calculadora-dias-entre-fechas/'), ('Porcentajes', 'https://live.aurzane.com/calculadora-porcentajes/')])]
CURSOS = [  # el bloque de cada curso lleva c=<slug>: cifras/cifras.py actualiza solo temas, lecciones y preguntas
 ('introduccion-psicologia', 'Introducción a la psicología', 'Psicología y bienestar', 'Mente, cerebro y conducta: de la investigación a la salud mental.', 'portada-psicologia.webp', 16, 64, 256, 'Gratis y con certificado'),
 ('ansiedad-dia-a-dia', 'Gestionar la ansiedad en el día a día', 'Bienestar emocional', 'Calma el cuerpo, revisa tus pensamientos y recupera lo que dejaste de hacer, con técnicas de la terapia cognitivo conductual.', 'portada-ansiedad.webp', 4, 12, 48, 'Gratis y con certificado'),
 ('neuroanatomia-funcional', 'Organización morfofuncional del Sistema Nervioso', 'Neurociencias', 'Del desarrollo y la médula a la corteza y las grandes vías, tema a tema.', 'portada-neuro.webp', 13, 67, 466, 'Gratis con tu cuenta AURZANE ID'),
 ('tecnicas-neurociencias', 'Metodología y técnicas de investigación en Neurociencias', 'Métodos de investigación', 'Estereotaxia, optogenética y terapia celular, con mapas, tarjetas y tests.', 'portada-metodologia.webp', 2, 9, 61, 'Gratis con tu cuenta AURZANE ID')]
FAQ = [('¿Qué es AURZANE?', 'Un ecosistema de cinco mundos (MIND, NEXUS, LIVE, LEARN y BUILD) más la orientación vocacional OVP, construido sobre ciencia aplicada. Puedes entrar solo por lo que te interese.'),
       ('¿Los tests sustituyen a un diagnóstico?', 'No. Son cuestionarios validados y orientativos: te ayudan a ponerle nombre a lo que sientes y a decidir si te conviene consultar con un profesional.'),
       ('¿Tengo que registrarme?', 'Para los tests, ejercicios, calculadoras y la biblioteca, no. La cuenta AURZANE ID solo hace falta para guardar tu progreso en los cursos y para la evaluación vocacional completa.'),
       ('¿Cómo accedo a la evaluación vocacional (OVP)?', 'Desde ovp.aurzane.com creas tu cuenta y haces las seis pruebas (CHASIDE, Holland, AF5, hábitos de estudio, APT-A y APT-B). El informe integrador aparece en tu portal al terminar y puedes descargarlo en PDF. Por lanzamiento es gratis.'),
       ('¿Quién está detrás?', 'Un psicólogo clínico titulado prepara y revisa los tests y los cursos. Cada contenido cita sus fuentes y se corrige si alguien encuentra un error. Más detalles en <a href="/sobre-aurzane.html">Sobre AURZANE</a>.'),
       ('¿Qué pasa con mis datos?', 'Los tests se calculan en tu navegador y no se guardan si no inicias sesión. Todo lo demás está explicado en la <a href="/privacidad.html">política de privacidad</a>.')]

TXT = {c[0]: c for c in CURSOS}
_cat = CIF.get('cursos') or {}
if _cat:
    try: META = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'cursos', 'meta.json'), encoding='utf-8'))
    except Exception: META = {}
    nuevos = []
    for slug, d in _cat.items():
        if slug in TXT:
            c = list(TXT[slug]); c[5], c[6], c[7] = d.get('temas', c[5]), d.get('lecciones', c[6]), d.get('preguntas', c[7]); nuevos.append(tuple(c))
        elif d.get('titulo'):
            m = META.get(slug, {})
            nuevos.append((slug, d['titulo'], m.get('area') or d.get('area') or 'Curso', d.get('descripcion') or m.get('publico') or '', m.get('portada') or 'portada-psicologia.webp',
                           d.get('temas', 0), d.get('lecciones', 0), d.get('preguntas', 0), 'Gratis y con certificado' if d.get('certificable') else 'Gratis'))
    if nuevos: CURSOS = nuevos

def tarjeta_test(t):
    u, n, q, d, m, f = t
    return (f'<a class="t-card" href="{u}" style="--c:var(--{m})"><span class="t-img"><img src="{U(f, 480)}" alt="" loading="lazy" width="480" height="300"></span>'
            f'<span class="t-txt"><b>{E(n)}</b><span>{E(q)}</span><small>{d} · {m.upper()}</small></span></a>')

intenciones = [('#tests', 'Conocerme mejor', '15 tests validados con el resultado explicado.', '1517841905240-472988babdf9', 'mind'),
               ('#calma', 'Calmarme ahora', 'Ejercicios guiados de 1 a 8 minutos.', '1544367567-0f2fcb009e0b', 'mind'),
               ('#orientacion', 'Decidir qué estudiar', 'Test vocacional, universidades y nota de acceso.', '1541339907198-e08756dedf3f', 'nexus'),
               ('#cursos', 'Aprender con un curso', 'Cursos gratis, algunos con certificado.', '1522202176988-66273c2fd55f', 'learn'),
               ('#herramientas', 'Hacer cuentas', 'Calculadoras de salud, dinero y vivienda.', '1579621970563-ebec7560ff3e', 'build'),
               ('#leer', 'Leer e investigar', 'Libros abiertos y artículos científicos.', '1532012197267-da84d127e765', 'live')]

cuerpo = f'''
<main id="contenido" tabindex="-1">

<section class="p-hero" aria-labelledby="pT">
  <img class="p-hero-foto" src="{U('1508672019048-805c876b67e2', 1800)}" srcset="{U('1508672019048-805c876b67e2', 800)} 800w, {U('1508672019048-805c876b67e2', 1400)} 1400w, {U('1508672019048-805c876b67e2', 2200)} 2200w" sizes="100vw" alt="Una persona sentada al final de un muelle, frente a un lago entre montañas" width="1800" height="1100" fetchpriority="high">
  <div class="p-hero-in">
    <h1 id="pT">Conócete, decide y construye tu vida con ciencia.</h1>
    <p class="p-lema">Tests psicológicos, cursos, calculadoras y libros gratis, creados por un psicólogo clínico y con las fuentes a la vista.</p>
    <form class="p-busca" id="pBusca" role="search">
      <label for="pQ" class="vh">Buscar en AURZANE</label>
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>
      <input id="pQ" type="search" placeholder="¿Qué quieres saber? Ansiedad, qué estudiar, hipoteca…" autocomplete="off">
      <button type="submit">Buscar</button>
    </form>
    <p class="p-pistas">Lo más buscado: <a href="https://mind.aurzane.com/test-de-personalidad/">Test de personalidad</a><a href="https://ovp.aurzane.com/">Test vocacional</a><a href="https://mind.aurzane.com/test-de-ansiedad/">Ansiedad</a><a href="https://nexus.aurzane.com/universidades/">Universidades</a></p>
    <ul class="p-cifras" aria-label="AURZANE en cifras">
      <li><b id="cTests">15</b> tests validados</li>
      <li><b>{NU} universidades</b> en {NP} países</li>
      <li><b id="cLibros">748</b> libros para leer gratis</li>
      <li><b id="cArt">25.000</b> artículos científicos</li>
    </ul>
  </div>
</section>

<section class="p-sec p-intenciones" aria-labelledby="iT">
  <div class="p-in">
    <h2 id="iT">¿Qué quieres hacer hoy?</h2>
    <ul class="p-int">
      {''.join(f'<li><a href="{h}" style="--c:var(--{m})"><img src="{U(f, 560)}" alt="" loading="lazy" width="560" height="360"><span><b>{E(n)}</b><small>{E(d)}</small></span></a></li>' for h, n, d, f, m in intenciones)}
    </ul>
  </div>
</section>

<section class="hoy" id="hoy" aria-labelledby="hoyTitulo" hidden>
  <div class="p-in hoy-grid">
    <div>
      <h2 class="hoy-fecha" id="hoyTitulo">Hoy en AURZANE · <span id="hoyDia"></span></h2>
      <blockquote class="hoy-cita" id="hoyFrase"></blockquote>
      <p class="hoy-autor" id="hoyAutor"></p>
      <div class="hoy-musica" id="hoyMusica" hidden>
        <button type="button" class="hoy-play" id="hoyPlay" aria-pressed="false">Escuchar música tranquila</button>
        <span class="hoy-cred" id="hoyCred"></span>
        <audio id="hoyAudio" preload="none" loop></audio>
      </div>
    </div>
    <ul class="hoy-lista" id="hoyLista"></ul>
  </div>
</section>

<section class="p-sec" id="tests" aria-labelledby="tT">
  <div class="p-in">
    <div class="p-cab"><h2 id="tT">Tests para conocerte</h2><p>Cuestionarios validados que usan psicólogos y médicos. Resultado al instante, explicado y sin registro.</p></div>
    <a class="p-dest" href="https://mind.aurzane.com/test-de-personalidad/">
      <img src="{U('1494790108377-be9c29b29330', 1000)}" alt="" loading="lazy" width="1000" height="700">
      <span class="p-dest-txt"><small>El más completo · desde 4 minutos</small><b>Test de personalidad de los Cinco Grandes</b><span>Descubre si eres Fogata, Faro, Telescopio u otro de los 11 perfiles, con 30 facetas, tus fortalezas y las carreras que encajan contigo.</span><em class="p-boton">Hacer el test gratis</em></span>
    </a>
    <div class="t-grid">{''.join(tarjeta_test(x) for x in TESTS)}</div>
    <p class="p-mas">También en <a href="https://mind.aurzane.com/en/">inglés</a> y <a href="https://mind.aurzane.com/pt/">portugués</a>.</p>
  </div>
</section>

<section class="p-sec p-calma" id="calma" aria-labelledby="cT">
  <div class="p-in p-dos">
    <div class="p-foto"><img src="{U('1544367567-0f2fcb009e0b', 1000)}" alt="Una mujer estirándose al atardecer junto al mar" loading="lazy" width="1000" height="700"></div>
    <div>
      <h2 id="cT">Calmarte ahora</h2>
      <p>Ejercicios guiados con voz y temporizador. Elige según lo que necesitas en este momento.</p>
      <ul class="p-lista">{''.join(f'<li><a href="{u}"><b>{E(n)}</b><span>{E(d)} · {m}</span></a></li>' for u, n, d, m in EJ)}</ul>
      <a class="p-enlace" href="https://mind.aurzane.com/ejercicios/">Ver los 13 ejercicios</a>
    </div>
  </div>
</section>

<section class="p-sec p-oscura" id="orientacion" aria-labelledby="oT">
  <div class="p-in p-dos p-dos-inv">
    <div>
      <h2 id="oT">Decidir qué estudiar, con datos</h2>
      <p>Una evaluación vocacional completa y un buscador de universidades para pasar del «no sé» a una lista corta de opciones.</p>
      <ul class="p-pasos">
        <li><a href="https://ovp.aurzane.com/"><b>Evaluación vocacional OVP</b><span>Seis pruebas (intereses, aptitudes, autoconcepto y hábitos de estudio) y un informe integrador en PDF. Gratis por lanzamiento.</span></a></li>
        <li><a href="https://nexus.aurzane.com/universidades/que-puedo-estudiar/"><b>¿Qué puedo estudiar con mi nota?</b><span>Pon tu nota de admisión y mira qué grados encajan.</span></a></li>
        <li><a href="https://nexus.aurzane.com/universidades/"><b>Buscador de universidades</b><span>{NU} instituciones en {NP} países, con sus carreras.</span></a></li>
        <li><a href="https://nexus.aurzane.com/calculadora-nota-pau/"><b>Calculadora de nota PAU</b><span>Nota de acceso y de admisión con ponderaciones.</span></a></li>
      </ul>
      <p class="p-nota">¿Eres un colegio? <a href="https://aurzane.com/colegios/">Orientación vocacional para todo tu bachillerato</a>.</p>
    </div>
    <div class="p-foto"><img src="{U('1541339907198-e08756dedf3f', 1000)}" alt="Estudiantes con toga lanzando el birrete al aire" loading="lazy" width="1000" height="700"></div>
  </div>
</section>

<section class="p-sec" id="herramientas" aria-labelledby="hT">
  <div class="p-in">
    <div class="p-cab"><h2 id="hT">Calculadoras para el día a día</h2><p>Con datos y normas de 2026, calculadas en tu navegador.</p></div>
    <div class="h-grid">{''.join(f'<div class="h-col"><h3>{E(g)}</h3><ul>' + ''.join(f'<li><a href="{u}">{E(n)}</a></li>' for n, u in L) + '</ul></div>' for g, L in CALC)}</div>
  </div>
</section>

<section class="p-sec p-suave" id="cursos" aria-labelledby="kT">
  <div class="p-in">
    <div class="p-cab"><h2 id="kT">Cursos gratis</h2><p>Lecciones breves, mapas, tarjetas de repaso y tests. Avanzas a tu ritmo y guardas tu progreso con tu cuenta.</p></div>
    <div class="k-grid" id="kGrid">{''.join(f"""<article class="k-card"><a href="https://learn.aurzane.com/curso/{s}/?c={s}"><img src="https://learn.aurzane.com/cursos/{img}" alt="" loading="lazy" width="1200" height="675"><span class="k-txt"><small>{E(a)}</small><b>{E(t)}</b><span>{E(d)}</span><ul class="k-datos"><li><b>{te}</b> temas</li><li><b>{le}</b> lecciones</li><li><b>{pr}</b> preguntas</li></ul><em>{E(acc)}</em></span></a></article>""" for s, t, a, d, img, te, le, pr, acc in CURSOS)}</div>
    <a class="p-enlace" href="https://learn.aurzane.com/cursos/">Ver todos los cursos</a>
  </div>
</section>

<section class="p-sec" id="leer" aria-labelledby="lT">
  <div class="p-in">
    <div class="p-cab"><h2 id="lT">Leer e investigar</h2><p>Libros con licencia abierta para leer aquí mismo y un buscador de artículos científicos con el resumen original.</p></div>
    <div class="l-grid">
      <div class="l-bib">
        <div class="l-estante" id="bhEstante" aria-hidden="true"></div>
        <h3>Biblioteca de libros</h3>
        <p id="bhCifras">748 libros para leer aquí, organizados por temas.</p>
        <form class="l-busca" action="/biblioteca/" method="get" role="search"><label for="bq" class="vh">Buscar un libro</label><input id="bq" name="q" type="search" placeholder="Ansiedad, apego, duelo…"><button type="submit">Buscar libros</button></form>
        <div class="l-cats" id="bhCats"></div>
      </div>
      <div class="l-otros">
        <a class="l-item" href="/research.html"><b>Research Hub</b><span id="rhTxt">Busca en las 5 bibliotecas del ecosistema a la vez: 25.000 artículos de acceso abierto, de Europe PMC, OpenAlex y PubMed.</span></a>
        <a class="l-item" href="/articulos/"><b>Artículos</b><span>Guías breves escritas a partir de estudios citados, sin resúmenes inventados.</span></a>
        <a class="l-item" href="/libros/"><b>Libros recomendados</b><span>Los títulos de psicología que más se leen ahora, con su resumen.</span></a>
        <a class="l-item" href="/frases/"><b>Frases para pensar</b><span>Citas de autores clásicos, una nueva cada día.</span></a>
      </div>
    </div>
  </div>
</section>

<section class="p-sec p-suave" id="novedades" aria-labelledby="nT">
  <div class="p-in">
    <div class="p-cab"><h2 id="nT">Lo último en AURZANE</h2><p>Artículos, tests y herramientas nuevos, según se publican.</p></div>
    <ol class="n-lista" id="nLista"><li><a href="/novedades/">Ver todas las novedades</a></li></ol>
    <a class="p-enlace" href="/novedades/">Todas las novedades</a>
  </div>
</section>

<section class="p-sec" id="confianza" aria-labelledby="fT">
  <div class="p-in p-dos">
    <div class="p-foto"><img src="{U('1471107340929-a87cd0f5b5f3', 1000)}" alt="Una pluma sobre un cuaderno abierto" loading="lazy" width="1000" height="700"></div>
    <div>
      <h2 id="fT">Por qué puedes fiarte</h2>
      <ul class="p-razones">
        <li><b>Criterio clínico.</b> Cada test y cada curso los prepara y revisa un psicólogo clínico titulado.</li>
        <li><b>Fuentes a la vista.</b> Los artículos citan estudios reales y la biblioteca académica enlaza cada trabajo con su fuente original.</li>
        <li><b>Sin registros innecesarios.</b> Los tests se calculan en tu navegador; solo creas cuenta si quieres guardar tu progreso.</li>
      </ul>
      <p><a class="p-enlace" href="/sobre-aurzane.html">Quiénes somos</a> <a class="p-enlace" href="/politica-editorial.html">Cómo preparamos los contenidos</a></p>
    </div>
  </div>
</section>

<section class="p-sec p-suave" id="preguntas" aria-labelledby="qT">
  <div class="p-in p-estrecho">
    <h2 id="qT">Preguntas frecuentes</h2>
    {''.join(f'<details><summary>{E(q)}</summary><p>{a}</p></details>' for q, a in FAQ)}
    <p class="p-nota">¿No está tu pregunta? <a href="/contacto.html">Escríbenos</a>.</p>
  </div>
</section>

</main>
'''

css = open(__file__.replace('generar.py', 'portada.css'), encoding='utf-8').read()
js = open(__file__.replace('generar.py', 'portada.js'), encoding='utf-8').read()
doc = ('<!DOCTYPE html>\n<html lang="es">\n<head>' + head + '<style>\n' + css + '\n</style>\n</head>\n<body class="portada">\n'
       '<button type="button" id="btnTema" onclick="alternarTema()" aria-label="Cambiar entre tema claro y oscuro">Tema</button>\n' +
       cuerpo + '<footer class="p-ancla" hidden></footer>\n' +
       '<script src="/biblioteca/resumen.js" defer></script>\n<script>\n' + js + '\n</script>\n</body>\n</html>\n')
open(out, 'w', encoding='utf-8').write(doc)
print('portada generada', len(doc))
