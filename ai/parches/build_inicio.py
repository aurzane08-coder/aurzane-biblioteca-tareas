"""Portadas de BUILD y LIVE (16/11/2026). BUILD es el mundo del dinero, los ingresos y la vivienda; LIVE, el de la salud y el día a día.
Pone en la sección de calculadoras (az-herr) las ocho herramientas de BUILD y la de interés compuesto, agrupadas
por lo que la gente busca: comprar o invertir en vivienda, y ganar, ahorrar y planificar su dinero. En LIVE, igual con
salud de la mujer, cuerpo, descanso y día a día.
Conserva la cifra del euríbor que ya tenga la tarjeta de hipoteca. Copia previa en build.aurzane.com/eliminar/."""
import os, re, sys, shutil, datetime
base = os.path.expanduser('~/' + (sys.argv[1] if len(sys.argv) > 1 else 'www'))

def aplicar(web, h2, intro, G):
    f = base + '/' + web + '/public_html/index.html'
    if not os.path.exists(f): return
    t = open(f, encoding='utf-8').read()
    m = re.search(r'(<section class="az-herr"[^>]*>\s*<style>.*?</style>)(.*?)(</section>)', t, re.S)
    if not m: print(web, 'sin sección de calculadoras'); return
    eur = re.search(r'<i>(Eur[ií]bor [^<]+)</i>', m.group(2)); eur = eur.group(1) if eur else 'Euríbor actual'
    cuerpo = f'\n    <h2 id="azHerrT">{h2}</h2>\n    <p>{intro}</p>\n'
    for tit, its in G:
        cuerpo += f'    <h3 style="font:600 1.05rem \'Instrument Sans\',sans-serif;margin:18px 0 10px;color:var(--text)">{tit}</h3>\n    <div class="az-herr-g">\n'
        cuerpo += ''.join(f'      <a href="{u}" style="background:linear-gradient(150deg,{c1},{c2})"><span class="e">{e}</span><b>{n}</b><span>{d}</span><br><i>{eur if ch == "EUR" else ch}</i></a>\n' for u, e, n, d, ch, c1, c2 in its)
        cuerpo += '    </div>\n'
    cuerpo += '  '
    n = t[:m.start(2)] + cuerpo + t[m.end(2):]
    if n != t:
        c = base + '/' + web + '/eliminar/inicio-' + datetime.datetime.now().strftime('%Y%m%d-%H%M'); os.makedirs(c, exist_ok=True)
        shutil.copy2(f, c); open(f, 'w', encoding='utf-8').write(n); print('portada de', web, 'con', sum(len(x[1]) for x in G), 'herramientas')
    else: print('portada de', web, 'sin cambios')


B = [
    ('Comprar e invertir en vivienda', [
        ('/calculadora-hipoteca/', '🏠', 'Calculadora de hipoteca', 'Cuota fija o variable, ahorro necesario y si te conviene alquilar o comprar.', 'EUR', '#2f5d7c', '#0f1823'),
        ('/calculadora-gastos-compra-vivienda/', '🧾', 'Gastos de compra de vivienda', 'ITP o IVA de tu comunidad, notaría, registro y el dinero que necesitas para firmar.', 'Nuevo', '#365f52', '#0f1d19'),
        ('/calculadora-rentabilidad-alquiler/', '🔑', 'Rentabilidad del alquiler', '¿Compensa comprar para alquilar? Rentabilidad bruta y neta, con o sin hipoteca.', 'Nuevo', '#5b4a2e', '#1c160c'),
        ('/calculadora-reforma/', '🛠️', 'Calculadora de reforma', 'Cocina, baños, suelos y ventanas: presupuesto partida a partida con IVA.', 'Precios 2026', '#3d6f8f', '#132433')]),
    ('Ganar, ahorrar y planificar', [
        ('/calculadora-sueldo-neto/', '💶', 'Sueldo neto', 'De bruto a neto con el IRPF y la Seguridad Social de 2026.', 'IRPF 2026', '#24506e', '#0c1620'),
        ('/calculadora-finiquito/', '📄', 'Finiquito e indemnización', 'Lo que te deben al dejar o perder un trabajo, según el Estatuto de los Trabajadores.', 'Nuevo', '#4a3d63', '#15111e'),
        ('/calculadora-ahorro/', '🐷', 'Calculadora de ahorro', 'Cuánto apartar al mes para tu meta y cómo repartir el sueldo con la regla 50/30/20.', 'Nuevo', '#2e5b4a', '#0d1a15'),
        ('/calculadora-jubilacion/', '🌅', 'Calculadora de jubilación', 'El capital que necesitas para complementar tu pensión y cuánto ahorrar desde hoy.', 'Nuevo', '#6a4a2a', '#1f150b'),
        ('https://live.aurzane.com/calculadora-interes-compuesto/', '📈', 'Interés compuesto', 'Cuánto crece tu dinero con los años si inviertes cada mes.', 'Inversión', '#2b4f6b', '#0c1520')])]
aplicar('build.aurzane.com', 'Calculadoras para tu dinero, tus ingresos y tu casa',
        'Números reales de 2026 para decidir antes de firmar, invertir o cambiar de trabajo. Gratis, sin registro y con la normativa citada.', B)

L = [
    ('Salud de la mujer y embarazo', [
        ('/calculadora-ovulacion/', '🌸', 'Calculadora de ovulación', 'Tus días fértiles, el día de ovulación y tu próxima regla, mes a mes.', 'Nuevo', '#b45a33', '#3a1a10'),
        ('/calculadora-embarazo/', '🤰', 'Calculadora de embarazo', 'Semanas, fecha probable de parto y calendario de pruebas.', 'Al instante', '#c46a3c', '#4a2212')]),
    ('Cuerpo y alimentación', [
        ('/calculadora-peso-ideal/', '🎯', 'Peso ideal', 'Tu rango de peso saludable según la OMS y las fórmulas médicas.', 'Nuevo', '#a5502d', '#33170d'),
        ('/calculadora-imc/', '⚖️', 'Calculadora de IMC', 'Tu IMC, tu rango según la OMS y tu peso saludable.', 'Al instante', '#c46a3c', '#4a2212'),
        ('/calculadora-calorias/', '🍽️', 'Calorías e IMC', 'Cuántas calorías necesitas al día, tu IMC, proteína y agua.', '1 minuto', '#a5502d', '#33170d'),
        ('/calculadora-agua/', '💧', 'Cuánta agua beber', 'El agua que necesitas según tu peso, ejercicio y calor.', 'Al instante', '#b45a33', '#3a1a10')]),
    ('Descanso y bienestar', [
        ('/calculadora-sueno/', '⏰', 'Calculadora de sueño', 'A qué hora acostarte o despertarte para completar tus ciclos de sueño.', 'Nuevo', '#96482a', '#2e140b'),
        ('/test-de-sueno/', '🌙', 'Test de sueño', 'Cantidad, regularidad y calidad de tu sueño con un plan de 7 días.', '2 minutos', '#96482a', '#2e140b'),
        ('/test-de-bienestar/', '🌤️', 'Test de bienestar', 'El índice WHO-5 de la OMS: cómo has estado estas dos semanas.', '1 minuto', '#b45a33', '#3a1a10'),
        ('/test-de-habitos/', '🥗', 'Test de hábitos', 'Tu nota de estilo de vida: alimentación, ejercicio, alcohol, tabaco y estrés.', '2 minutos', '#c46a3c', '#4a2212')]),
    ('Fechas y números del día a día', [
        ('/calculadora-edad/', '🎂', 'Calculadora de edad', 'Tu edad en años, meses y días y tu próximo cumpleaños.', 'Al instante', '#96482a', '#2e140b'),
        ('/calculadora-dias-entre-fechas/', '📅', 'Días entre fechas', 'Cuenta los días entre dos fechas o haz una cuenta atrás.', 'Al instante', '#a5502d', '#33170d'),
        ('/calculadora-porcentajes/', '％', 'Calculadora de porcentajes', 'Tantos por ciento, descuentos, subidas y variaciones.', 'Al instante', '#c46a3c', '#4a2212'),
        ('https://build.aurzane.com/', '💶', 'Tu dinero, en BUILD', 'Sueldo neto, ahorro, jubilación, interés compuesto e hipoteca.', 'BUILD', '#24506e', '#0c1620')])]
aplicar('live.aurzane.com', 'Tests y calculadoras para cuidarte',
        'Chequeos rápidos con base científica y resultado al instante, para tu cuerpo, tu descanso y tu día a día. Anónimos: nada sale de tu móvil.', L)
