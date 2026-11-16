"""Portada de BUILD (16/11/2026): BUILD es el mundo del dinero, los ingresos y la vivienda.
Pone en la sección de calculadoras (az-herr) las ocho herramientas de BUILD y la de interés compuesto, agrupadas
por lo que la gente busca: comprar o invertir en vivienda, y ganar, ahorrar y planificar su dinero.
Conserva la cifra del euríbor que ya tenga la tarjeta de hipoteca. Copia previa en build.aurzane.com/eliminar/."""
import os, re, sys, shutil, datetime
base = os.path.expanduser('~/' + (sys.argv[1] if len(sys.argv) > 1 else 'www'))
f = base + '/build.aurzane.com/public_html/index.html'
t = open(f, encoding='utf-8').read()
m = re.search(r'(<section class="az-herr"[^>]*>\s*<style>.*?</style>)(.*?)(</section>)', t, re.S)
if not m: print('sin sección de calculadoras'); sys.exit(0)
eur = re.search(r'<i>(Eur[ií]bor [^<]+)</i>', m.group(2)); eur = eur.group(1) if eur else 'Euríbor actual'
G = [
    ('Comprar e invertir en vivienda', [
        ('/calculadora-hipoteca/', '🏠', 'Calculadora de hipoteca', 'Cuota fija o variable, ahorro necesario y si te conviene alquilar o comprar.', eur, '#2f5d7c', '#0f1823'),
        ('/calculadora-gastos-compra-vivienda/', '🧾', 'Gastos de compra de vivienda', 'ITP o IVA de tu comunidad, notaría, registro y el dinero que necesitas para firmar.', 'Nuevo', '#365f52', '#0f1d19'),
        ('/calculadora-rentabilidad-alquiler/', '🔑', 'Rentabilidad del alquiler', '¿Compensa comprar para alquilar? Rentabilidad bruta y neta, con o sin hipoteca.', 'Nuevo', '#5b4a2e', '#1c160c'),
        ('/calculadora-reforma/', '🛠️', 'Calculadora de reforma', 'Cocina, baños, suelos y ventanas: presupuesto partida a partida con IVA.', 'Precios 2026', '#3d6f8f', '#132433')]),
    ('Ganar, ahorrar y planificar', [
        ('/calculadora-sueldo-neto/', '💶', 'Sueldo neto', 'De bruto a neto con el IRPF y la Seguridad Social de 2026.', 'IRPF 2026', '#24506e', '#0c1620'),
        ('/calculadora-finiquito/', '📄', 'Finiquito e indemnización', 'Lo que te deben al dejar o perder un trabajo, según el Estatuto de los Trabajadores.', 'Nuevo', '#4a3d63', '#15111e'),
        ('/calculadora-ahorro/', '🐷', 'Calculadora de ahorro', 'Cuánto apartar al mes para tu meta y cómo repartir el sueldo con la regla 50/30/20.', 'Nuevo', '#2e5b4a', '#0d1a15'),
        ('/calculadora-jubilacion/', '🌅', 'Calculadora de jubilación', 'El capital que necesitas para complementar tu pensión y cuánto ahorrar desde hoy.', 'Nuevo', '#6a4a2a', '#1f150b'),
        ('https://live.aurzane.com/calculadora-interes-compuesto/', '📈', 'Interés compuesto', 'Cuánto crece tu dinero con los años si inviertes cada mes.', 'Inversión', '#2b4f6b', '#0c1520')])]
cuerpo = '\n    <h2 id="azHerrT">Calculadoras para tu dinero, tus ingresos y tu casa</h2>\n    <p>Números reales de 2026 para decidir antes de firmar, invertir o cambiar de trabajo. Gratis, sin registro y con la normativa citada.</p>\n'
for tit, its in G:
    cuerpo += f'    <h3 style="font:600 1.05rem \'Instrument Sans\',sans-serif;margin:18px 0 10px;color:var(--text)">{tit}</h3>\n    <div class="az-herr-g">\n'
    cuerpo += ''.join(f'      <a href="{u}" style="background:linear-gradient(150deg,{c1},{c2})"><span class="e">{e}</span><b>{n}</b><span>{d}</span><br><i>{ch}</i></a>\n' for u, e, n, d, ch, c1, c2 in its)
    cuerpo += '    </div>\n'
cuerpo += '  '
n = t[:m.start(2)] + cuerpo + t[m.end(2):]
if n != t:
    c = base + '/build.aurzane.com/eliminar/inicio-' + datetime.datetime.now().strftime('%Y%m%d-%H%M'); os.makedirs(c, exist_ok=True)
    shutil.copy2(f, c); open(f, 'w', encoding='utf-8').write(n); print('portada de BUILD con', sum(len(x[1]) for x in G), 'calculadoras')
else: print('portada de BUILD sin cambios')
