"""Calculadoras nuevas de AURZANE BUILD (dinero, ingresos, inversión y vivienda), 16/11/2026.

Elegidas por demanda de búsqueda en España: gastos de compra de vivienda, rentabilidad del alquiler, finiquito e
indemnización, ahorro mensual (regla 50/30/20) y jubilación. Usan la misma plantilla, estilos y utilidades (AZ) que
la calculadora de sueldo neto, para que todo BUILD se vea igual. Tipos de ITP/AJD: los mismos de la calculadora de
hipoteca (una sola fuente). Escribe publicar/build.aurzane.com/<ruta>/index.html.
Después, solas: guías largas (guias.py), sitemap (mapas.py), buscador (indice.py) y títulos (titulos.py).
Uso: python3 herramientas/build_calculadoras.py"""
import json, os, re, html

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = os.path.join(R, 'traer', 'servidor', 'build.aurzane.com', 'calculadora-sueldo-neto', 'index.html')
OUT = os.path.join(R, 'publicar', 'build.aurzane.com')
SRC = open(BASE, encoding='utf-8').read()
CSS = SRC[SRC.find('<style>'):SRC.find('</style>') + 8]
PIE = SRC[SRC.find('<footer>'):SRC.rfind('<script>(function(){')]   # pie + utilidades comunes AZ
CSS_EXTRA = '<style>input[type=date]{width:100%;font:500 1rem var(--sans);color:var(--text);background:var(--surface-2);border:1.5px solid transparent;border-radius:12px;padding:10px 12px}.aviso-fin{font-size:.84rem;color:var(--text-dim);margin:14px 0 0}</style>'

TODAS = [
    ('calculadora-hipoteca', '🏠', 'Calculadora de hipoteca', 'Cuota fija o variable con el euríbor actual.', '#2f5d7c', '#0f1823'),
    ('calculadora-gastos-compra-vivienda', '🧾', 'Gastos de compra de vivienda', 'ITP o IVA de tu comunidad, notaría y registro.', '#365f52', '#0f1d19'),
    ('calculadora-rentabilidad-alquiler', '🔑', 'Rentabilidad del alquiler', 'Bruta, neta y con hipoteca: ¿compensa invertir?', '#5b4a2e', '#1c160c'),
    ('calculadora-sueldo-neto', '💶', 'Sueldo neto', 'De bruto a neto con el IRPF de 2026.', '#24506e', '#0c1620'),
    ('calculadora-finiquito', '📄', 'Finiquito e indemnización', 'Lo que te deben al dejar o perder un trabajo.', '#4a3d63', '#15111e'),
    ('calculadora-ahorro', '🐷', 'Calculadora de ahorro', 'Cuánto ahorrar al mes para tu meta (50/30/20).', '#2e5b4a', '#0d1a15'),
    ('calculadora-jubilacion', '🌅', 'Calculadora de jubilación', 'Cuánto ahorrar para complementar tu pensión.', '#6a4a2a', '#1f150b'),
    ('calculadora-reforma', '🛠️', 'Calculadora de reforma', 'Presupuesto partida a partida con IVA.', '#3d6f8f', '#132433'),
]
INTERES = ('https://live.aurzane.com/calculadora-interes-compuesto/', '📈', 'Interés compuesto', 'Cuánto crecen tus ahorros con los años.', '#2b4f6b', '#0c1520')


def tarjetas(slug, rel):
    out = []
    for r in rel:
        if r == 'interes':
            u, e, t, d, c1, c2 = INTERES
        else:
            x = [y for y in TODAS if y[0] == r][0]; u, e, t, d, c1, c2 = '/' + x[0] + '/', *x[1:]
        out.append(f'<a class="scard" style="background:linear-gradient(150deg,{c1},{c2})" href="{u}"><span class="e">{e}</span><b>{t}</b><span>{d}</span></a>')
    return '\n    '.join(out)


def pagina(c):
    url = f'https://build.aurzane.com/{c["slug"]}/'
    faq_ld = [{'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': re.sub('<[^>]+>', '', a)}} for q, a in c['faq']]
    ld = {'@context': 'https://schema.org', '@graph': [
        {'@type': 'WebApplication', 'name': c['nombre'], 'url': url, 'applicationCategory': 'FinanceApplication', 'operatingSystem': 'Web', 'inLanguage': 'es',
         'isAccessibleForFree': True, 'offers': {'@type': 'Offer', 'price': '0', 'priceCurrency': 'EUR'}, 'publisher': {'@type': 'Organization', 'name': 'AURZANE', 'url': 'https://aurzane.com/'}},
        {'@type': 'FAQPage', 'mainEntity': faq_ld}]}
    e = html.escape
    nav = ''.join(f'<a href="/{s}/"{" aria-current=\"page\"" if s == c["slug"] else ""}>{n}</a>' for s, n in
                  [('calculadora-hipoteca', 'Hipoteca'), ('calculadora-gastos-compra-vivienda', 'Gastos compra'), ('calculadora-rentabilidad-alquiler', 'Alquiler'),
                   ('calculadora-sueldo-neto', 'Sueldo'), ('calculadora-ahorro', 'Ahorro')])
    faq = '\n  '.join(f'<details class="faq"><summary>{q}</summary><p>{a}</p></details>' for q, a in c['faq'])
    cred = '\n    '.join(f'<li>{x}</li>' for x in c['creditos'])
    chips = ''.join(f'<li>{x}</li>' for x in c['chips'])
    return f'''<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<script src="https://aurzane.com/aurzane-paleta.js"></script>
<title>{e(c["titulo"])} | AURZANE BUILD</title>
<meta name="description" content="{e(c["desc"])}">
<link rel="canonical" href="{url}">
<meta property="og:title" content="{e(c["og"])}">
<meta property="og:description" content="{e(c["desc"])}">
<meta property="og:type" content="website">
<meta property="og:url" content="{url}">
<meta property="og:image" content="https://build.aurzane.com/{c["ogimg"]}/og.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:locale" content="es_ES">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="https://build.aurzane.com/{c["ogimg"]}/og.jpg">
<meta name="theme-color" content="#1d1915">
<script>(function(){{ try {{ if (localStorage.getItem('aurzane-tema') === 'oscuro') document.documentElement.setAttribute('data-tema','oscuro'); }} catch(e){{}} }})();</script>
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Bodoni+Moda:wght@500;700&family=Instrument+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
<meta name="google-adsense-account" content="ca-pub-8763758728010451">
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-8763758728010451" crossorigin="anonymous"></script>
{CSS}
{CSS_EXTRA}
</head>
<body>
<div class="utility" data-nosnippet><div class="wrap"><div class="eco"><a href="https://aurzane.com/">AURZANE</a><a href="https://mind.aurzane.com/">MIND</a><a href="https://ovp.aurzane.com/">OVP</a><a href="https://nexus.aurzane.com/">NEXUS</a><a href="https://live.aurzane.com/">LIVE</a><a href="https://learn.aurzane.com/">LEARN</a><a class=activo href="https://build.aurzane.com/">BUILD</a></div><button type="button" id="btnTema">🌓 Tema</button></div></div>
<header class="topbar" data-nosnippet><div class="wrap">
<a class="brand" href="https://build.aurzane.com/">AUR<span class="z">Z</span>ANE<small>/ BUILD</small></a>
<nav aria-label="BUILD">{nav}<a class="cuenta" href="https://aurzane.com/mi-aurzane.html">👤 Mi AURZANE</a></nav>
</div></header>
<section class="hero"><div class="wrap">
<p class="migas"><a href="https://build.aurzane.com/">BUILD</a><span>/</span>{c["nombre"]}</p>
<span class="pre">{c["pre"]}</span>
<h1>{c["h1"]}</h1>
<p class="lead">{c["lead"]}</p>
<ul class="chips">{chips}</ul>
</div></section>

<div class="wrap">
<div class="app">
  <div class="panel">
{c["form"]}
  </div>

  <aside class="panel res sticky" id="resultado" aria-live="polite">
    <div class="res-top"><h2>{c["restit"]}</h2><div class="grande" id="grande">–</div><p class="sub2" id="grandeSub"></p><span class="nivel ok" id="nivel"><i></i><span></span></span></div>
    <div class="res-cuerpo">
{c["lineas"]}
      <p id="nota" style="font-size:.86rem;color:var(--text-dim);margin:12px 0 0"></p>
    </div>
    <div class="acciones"><button class="btn btn-osc" id="compartir" type="button">Compartir este cálculo</button><button class="btn btn-linea" type="button" onclick="window.print()">Guardar en PDF</button></div>
    <p class="msg" id="msg"></p>
  </aside>
</div>

{c["extra"]}

<section class="bloque">
  <h2 class="t">Más herramientas para tu dinero y tu casa</h2>
  <div class="siguiente">
    {tarjetas(c["slug"], c["rel"])}
  </div>
</section>

<section class="bloque">
  <h2 class="t">Preguntas frecuentes</h2>
  {faq}
  <ul class="creditos">
    {cred}
  </ul>
  <p class="aviso-fin">Cálculo orientativo con fines informativos y educativos. No es asesoramiento financiero, fiscal ni legal: para decidir, consulta tu caso con un profesional.</p>
</section>
</div>
<div class="movil-barra" id="movilBarra"><div><span>{c["movil"]}</span><b id="movilValor">–</b></div><a href="#resultado">Ver detalle</a></div>

{PIE}<script>(function(){{
var $=function(id){{return document.getElementById(id);}};
var n=function(id){{var v=parseFloat(String($(id).value).replace(',','.'));return isFinite(v)?v:0;}};
var st={json.dumps(c.get("st", {}))};
function seg(id,k){{var el=$(id);if(!el)return;el.addEventListener('click',function(ev){{var b=ev.target.closest('button');if(!b)return;st[k]=b.getAttribute('data-v');Array.prototype.forEach.call(el.querySelectorAll('button'),function(x){{x.setAttribute('aria-pressed',x===b?'true':'false');}});pintar();}});Array.prototype.forEach.call(el.querySelectorAll('button'),function(x){{x.setAttribute('aria-pressed',x.getAttribute('data-v')===st[k]?'true':'false');}});}}
function nivel(clase,txt){{var e=$('nivel');e.className='nivel '+clase;e.querySelector('span').textContent=txt;}}
function hash(ids){{var q=new URLSearchParams();ids.forEach(function(k){{q.set(k,$(k).value);}});Object.keys(st).forEach(function(k){{q.set(k,st[k]);}});history.replaceState(null,'','#'+q.toString());}}
(function(){{var q=new URLSearchParams(location.hash.slice(1));q.forEach(function(v,k){{if($(k)&&$(k).tagName!=='DIV')$(k).value=v;else if(k in st)st[k]=v;}});}})();
{c["js"]}
Array.prototype.forEach.call(document.querySelectorAll('.app input,.app select'),function(i){{i.addEventListener('input',pintar);}});
pintar();document.body.classList.add('hecho');
$('compartir').addEventListener('click',function(){{AZ.compartir({json.dumps(c["nombre"], ensure_ascii=False)},{json.dumps(c["compartir"], ensure_ascii=False)},$('msg'));}});
AZ.barraMovil($('resultado'),$('movilBarra'));
}})();
</script>
</body>
</html>
'''


def campo(id, label, valor, uni='€', paso='1', col=False, extra=''):
    s = ' style="grid-column:1/-1"' if col else ''
    return f'<div class="campo"{s}><label for="{id}">{label}</label><div class="entrada"><input type="number" id="{id}" value="{valor}" min="0" step="{paso}" inputmode="decimal"{extra}><span>{uni}</span></div></div>'


def segm(id, label, ops, col=False):
    s = ' style="grid-column:1/-1"' if col else ''
    return f'<div class="campo"{s}><label>{label}</label><div class="seg" id="{id}">' + ''.join(f'<button type="button" data-v="{v}">{t}</button>' for v, t in ops) + '</div></div>'


def bloque(tit, campos, tres=False):
    return f'    <div class="bloque-form">\n      <h3>{tit}</h3>\n      <div class="campos{" tres" if tres else ""}">\n        ' + '\n        '.join(campos) + '\n      </div>\n    </div>'


def lineas(items):
    return '\n'.join(f'      <div class="linea{" total" if t else ""}"><span id="{i}L">{"<b>" + l + "</b>" if t else l}</span><b id="{i}"></b></div>' if i else f'      {l}' for i, l, t in items)


LEY = '<div class="leyenda">{}</div>'
CCAA_JS = "var CCAA=[['Andalucía',7,1.2,10],['Aragón',8,1.5,10],['Asturias',8,1.2,10],['Islas Baleares',8,1.5,10],['Canarias',6.5,1,6.5],['Cantabria',10,1.5,10],['Castilla-La Mancha',9,1.5,10],['Castilla y León',8,1.5,10],['Cataluña',10,1.5,10],['Comunidad de Madrid',6,0.75,10],['Comunidad Valenciana',10,1.5,10],['Extremadura',8,1.5,10],['Galicia',10,1.5,10],['La Rioja',7,1,10],['Navarra',6,0.5,10],['País Vasco',4,0.5,10],['Región de Murcia',8,1.5,10],['Ceuta',6,0.5,0.5],['Melilla',6,0.5,0.5]];"


def sincroniza_ccaa():
    """Toma los tipos de la calculadora de hipoteca (la fuente única) si cambian allí."""
    global CCAA_JS
    h = open(os.path.join(R, 'traer', 'servidor', 'build.aurzane.com', 'calculadora-hipoteca', 'index.html'), encoding='utf-8').read()
    m = re.search(r"var CCAA=\[.*?\];", h)
    if m: CCAA_JS = m.group(0)


sincroniza_ccaa()

CALCS = []

# 1. Gastos de compra de vivienda ------------------------------------------------------------------------------
CALCS.append(dict(
    slug='calculadora-gastos-compra-vivienda', ogimg='calculadora-hipoteca', nombre='Calculadora de gastos de compra de vivienda',
    titulo='Gastos de compra de vivienda 2026: ITP, notaría y registro',
    og='¿Cuánto cuesta comprar una casa además del precio? Gastos 2026',
    desc='Calcula los gastos de comprar una vivienda en 2026: ITP o IVA y AJD de tu comunidad, notaría, registro, gestoría y tasación, y el ahorro total que necesitas.',
    pre='🧾 Tipos de 2026 por comunidad', h1='Lo que cuesta comprar <span>además del precio</span>',
    lead='Elige tu comunidad y el precio de la vivienda: te calculamos los impuestos, la notaría, el registro y el dinero ahorrado que necesitas para firmar.',
    chips=['🏛️ ITP o IVA + AJD', '✍️ Notaría y registro', '💰 Ahorro necesario'],
    st={'tipo': 'usada', 'hip': 'si'},
    form=bloque('La vivienda', [campo('precio', 'Precio de compra', 250000, paso='1000', col=True), '<div class="campo" style="grid-column:1/-1"><label for="ccaa">Comunidad autónoma</label><select id="ccaa"></select></div>',
                                segm('tipo', 'Tipo de vivienda', [('usada', 'Segunda mano'), ('nueva', 'Obra nueva')]), segm('hip', 'Con hipoteca', [('si', 'Sí'), ('no', 'No')])]) + '\n' +
         bloque('Financiación', [campo('fin', 'Parte que financia el banco', 80, uni='%', paso='1'), campo('gestoria', 'Gestoría (opcional)', 350)]),
    restit='Gastos de la compra', movil='Gastos',
    lineas=lineas([('rImp', 'Impuestos', 0), ('rNot', 'Notaría (compraventa)', 0), ('rReg', 'Registro de la Propiedad', 0), ('rGes', 'Gestoría', 0), ('rTas', 'Tasación', 0),
                   ('rGastos', 'Total gastos', 1), ('rEntrada', 'Entrada (lo que no financia el banco)', 0), ('rAhorro', 'Ahorro que necesitas', 1),
                   ('', '<div class="apilada" id="apilada"></div>' + LEY.format('<span><b style="background:var(--n3)"></b>Entrada</span><span><b style="background:var(--violeta)"></b>Impuestos</span><span><b style="background:var(--cian)"></b>Notaría, registro y otros</span>'), 0)]),
    extra='''<section class="bloque">
  <h2 class="t">Gastos de compra en cada comunidad</h2>
  <p class="sub" id="tablaSub">Para el precio que has escrito, en segunda mano y en obra nueva. Pulsa una fila para verla arriba.</p>
  <div class="panel" style="padding:8px 20px"><div class="scroll"><table class="tabla" id="tablaCCAA"></table></div></div>
</section>
<section class="bloque">
  <h2 class="t">Cómo se calcula</h2>
  <div class="tarjetas">
    <div class="tcard"><div class="big">4% a 10%</div><h3>ITP en segunda mano</h3><p>Impuesto de Transmisiones Patrimoniales: lo fija cada comunidad. Muchas tienen tipos reducidos para jóvenes, familias numerosas o viviendas de bajo precio.</p></div>
    <div class="tcard"><div class="big">10% + AJD</div><h3>IVA en obra nueva</h3><p>Si compras al promotor pagas IVA del 10% (IGIC del 6,5% en Canarias) y Actos Jurídicos Documentados, entre el 0,5% y el 1,5% según la comunidad.</p></div>
    <div class="tcard"><div class="big">≈ 1.500 €</div><h3>Notaría, registro y gestoría</h3><p>Aranceles regulados que suben con el precio. Desde 2019, los gastos de la escritura de hipoteca los paga el banco; tú pagas la tasación.</p></div>
  </div>
</section>''',
    faq=[('¿Cuánto dinero necesito ahorrado para comprar un piso?', 'Los bancos suelen financiar hasta el 80% del precio. Necesitas el 20% restante más entre un 8% y un 12% para impuestos y gastos: en total, alrededor del 30% del precio de compra.'),
         ('¿Qué gastos paga el comprador de una vivienda?', 'El impuesto (ITP en segunda mano, IVA y AJD en obra nueva), la notaría y el registro de la compraventa, la gestoría si la contratas y la tasación si pides hipoteca. La plusvalía municipal la paga el vendedor.'),
         ('¿Quién paga los gastos de la hipoteca?', 'Desde la Ley 5/2019 de crédito inmobiliario, el banco paga la notaría, el registro y la gestoría de la escritura de hipoteca, y el AJD de la hipoteca. El comprador paga la tasación y las copias que pida.'),
         ('¿Los tipos de ITP son iguales para todos?', 'No. Esta calculadora usa el tipo general de cada comunidad. Hay tipos reducidos para menores de 35 años, familias numerosas, personas con discapacidad o viviendas protegidas, y algunas comunidades suben el tipo por tramos en viviendas caras. Consulta la web de hacienda de tu comunidad antes de firmar.')],
    creditos=['Tipos generales de ITP, IVA o IGIC y AJD de 2026: los mismos que usa la calculadora de hipoteca de AURZANE BUILD, según la normativa de cada comunidad.',
              'Notaría y registro: estimación a partir de los aranceles notariales y registrales (Reales Decretos 1426/1989 y 1427/1989), que dependen del precio y de la escritura.',
              'Gastos de la hipoteca: Ley 5/2019, reguladora de los contratos de crédito inmobiliario.'],
    rel=['calculadora-hipoteca', 'calculadora-rentabilidad-alquiler', 'calculadora-ahorro'],
    compartir='Calcula los gastos de comprar una vivienda en tu comunidad:',
    js=CCAA_JS + r'''
$('ccaa').innerHTML=CCAA.map(function(c,i){return '<option value="'+i+'"'+(i===9?' selected':'')+'>'+c[0]+'</option>';}).join('');
(function(){var q=new URLSearchParams(location.hash.slice(1));if(q.has('ccaa'))$('ccaa').value=q.get('ccaa');})();
seg('tipo','tipo');seg('hip','hip');
function gastos(precio,c,tipo,hip,ges){
  var imp=tipo==='usada'?precio*c[1]/100:precio*(c[3]+c[2])/100;
  var not=Math.min(Math.max(400+precio*0.0015,600),1500),reg=Math.min(Math.max(250+precio*0.001,400),1000),tas=hip?400:0;
  return {imp:imp,not:not,reg:reg,ges:ges,tas:tas,total:imp+not+reg+ges+tas};
}
function pintar(){
  var precio=n('precio'),c=CCAA[+$('ccaa').value]||CCAA[9],hip=st.hip==='si',fin=hip?Math.min(Math.max(n('fin'),0),100):0;
  $('fin').disabled=!hip;
  var g=gastos(precio,c,st.tipo,hip,n('gestoria')),entrada=precio*(1-fin/100),ahorro=entrada+g.total;
  $('grande').textContent=AZ.eur(g.total);$('movilValor').textContent=AZ.eur(g.total);
  $('grandeSub').textContent=(precio?AZ.fmt(g.total/precio*100,1):'0')+'% del precio · '+c[0];
  var lbl=st.tipo==='usada'?'ITP '+AZ.fmt(c[1],1)+'%':(c[0]==='Canarias'?'IGIC ':c[3]<1?'IPSI ':'IVA ')+AZ.fmt(c[3],1)+'% + AJD '+AZ.fmt(c[2],2)+'%';
  $('rImpL').textContent='Impuestos ('+lbl+')';$('rImp').textContent=AZ.eur(g.imp);$('rNot').textContent=AZ.eur(g.not);$('rReg').textContent=AZ.eur(g.reg);
  $('rGes').textContent=AZ.eur(g.ges);$('rTas').textContent=hip?AZ.eur(g.tas):'No aplica';$('rGastos').textContent=AZ.eur(g.total);
  $('rEntrada').textContent=AZ.eur(entrada);$('rAhorro').textContent=AZ.eur(ahorro);
  var t=ahorro||1;$('apilada').innerHTML='<i style="width:'+(entrada/t*100)+'%;background:var(--n3)"></i><i style="width:'+(g.imp/t*100)+'%;background:var(--violeta)"></i><i style="width:'+((g.total-g.imp)/t*100)+'%;background:var(--cian)"></i>';
  var p=precio?ahorro/precio*100:0;nivel(p<=25?'ok':p<=33?'medio':'mal','Ahorro necesario: '+AZ.fmt(p,0)+'% del precio');
  $('nota').textContent=hip?'Con una hipoteca del '+AZ.fmt(fin,0)+'% el banco presta '+AZ.eur(precio*fin/100)+'. Los gastos y la entrada salen de tus ahorros.':'Sin hipoteca no hay tasación: pagas el precio completo más los gastos.';
  $('tablaCCAA').innerHTML='<tr><th>Comunidad</th><th>Segunda mano</th><th>Obra nueva</th></tr>'+CCAA.map(function(x,i){var a=gastos(precio,x,'usada',hip,n('gestoria')),b=gastos(precio,x,'nueva',hip,n('gestoria'));return '<tr data-i="'+i+'" style="cursor:pointer"><td>'+x[0]+'</td><td>'+AZ.eur(a.total)+'</td><td>'+AZ.eur(b.total)+'</td></tr>';}).join('');
  hash(['precio','ccaa','fin','gestoria']);
}
$('tablaCCAA').addEventListener('click',function(e){var tr=e.target.closest('tr[data-i]');if(!tr)return;$('ccaa').value=tr.getAttribute('data-i');pintar();$('resultado').scrollIntoView({behavior:'smooth',block:'start'});});
'''))

# 2. Rentabilidad del alquiler -------------------------------------------------------------------------------
CALCS.append(dict(
    slug='calculadora-rentabilidad-alquiler', ogimg='calculadora-hipoteca', nombre='Calculadora de rentabilidad del alquiler',
    titulo='Calculadora de rentabilidad del alquiler: bruta y neta',
    og='¿Compensa comprar un piso para alquilar? Calcula su rentabilidad',
    desc='Calcula la rentabilidad bruta y neta de comprar un piso para alquilar: gastos, impuestos de compra, vacíos, hipoteca, flujo de caja mensual y años para recuperar la inversión.',
    pre='🔑 Inversión inmobiliaria', h1='¿Compensa comprar <span>para alquilar?</span>',
    lead='Escribe el precio, el alquiler y los gastos del piso. Te calculamos la rentabilidad bruta y neta, el dinero que te queda cada mes y, si usas hipoteca, lo que rinde tu dinero.',
    chips=['📊 Bruta y neta', '🏦 Con o sin hipoteca', '⏳ Años para recuperar'],
    st={'hip': 'no'},
    form=bloque('La compra', [campo('precio', 'Precio del piso', 180000, paso='1000'), campo('gcompra', 'Impuestos y gastos de compra', 10, uni='%', paso='0.5'),
                              campo('reforma', 'Reforma y muebles', 6000, paso='500', col=True)]) + '\n' +
         bloque('El alquiler', [campo('renta', 'Alquiler al mes', 900, paso='10'), campo('meses', 'Meses alquilado al año', 11, uni='meses', paso='0.5'),
                                campo('comunidad', 'Comunidad al año', 600, paso='50'), campo('ibi', 'IBI y basuras al año', 450, paso='50'),
                                campo('seguro', 'Seguros al año (hogar e impago)', 350, paso='50'), campo('mant', 'Mantenimiento y gestión', 5, uni='%', paso='1')]) + '\n' +
         bloque('Financiación', [segm('hip', 'Con hipoteca', [('no', 'No'), ('si', 'Sí')], col=True), campo('fin', 'Parte financiada', 70, uni='%'),
                                 campo('tin', 'Interés (TIN)', 3, uni='%', paso='0.05'), campo('plazo', 'Plazo', 25, uni='años', col=True)]),
    restit='Rentabilidad neta', movil='Rentabilidad neta',
    lineas=lineas([('rInv', 'Dinero invertido en total', 0), ('rIng', 'Ingresos por alquiler al año', 0), ('rGas', 'Gastos al año', 0), ('rBen', 'Beneficio neto al año (antes de IRPF)', 1),
                   ('rBruta', 'Rentabilidad bruta', 0), ('rPer', 'Años de alquiler para pagar el piso (PER)', 0), ('rCuota', 'Cuota de la hipoteca', 0), ('rFlujo', 'Te queda cada mes', 1), ('rRoe', 'Rentabilidad sobre tu dinero', 0)]),
    extra='''<section class="bloque">
  <h2 class="t">Qué rentabilidad es buena</h2>
  <div class="tarjetas">
    <div class="tcard"><div class="big">Bruta</div><h3>Alquiler anual ÷ precio</h3><p>Sirve para comparar pisos rápido, pero engaña: no cuenta impuestos de compra, vacíos ni gastos. Por debajo del 5% bruto, cuesta que salgan los números.</p></div>
    <div class="tcard"><div class="big">Neta</div><h3>Lo que de verdad rinde</h3><p>Resta comunidad, IBI, seguros, mantenimiento y meses vacío, y divide por todo lo invertido. Entre el 3% y el 5% neto es lo habitual en grandes ciudades.</p></div>
    <div class="tcard"><div class="big">Flujo</div><h3>El dinero de cada mes</h3><p>Con hipoteca, lo importante es que el alquiler pague la cuota y los gastos. Si el flujo es negativo, pones dinero cada mes aunque el piso se revalorice.</p></div>
  </div>
</section>''',
    faq=[('¿Cómo se calcula la rentabilidad de un alquiler?', 'La bruta es el alquiler de un año dividido entre el precio del piso. La neta resta al alquiler los gastos anuales (comunidad, IBI, seguros, mantenimiento y meses vacío) y lo divide entre todo lo invertido: precio, impuestos, gastos de compra y reforma.'),
         ('¿Qué rentabilidad neta es buena para un piso de alquiler?', 'Depende de la ciudad y del riesgo, pero como referencia, una rentabilidad neta por encima del 5% es buena, entre el 3% y el 5% es habitual en zonas caras y por debajo del 3% suele compensar más otra inversión.'),
         ('¿Cuánto IRPF se paga por alquilar un piso?', 'El rendimiento neto (alquiler menos gastos deducibles, intereses de la hipoteca y amortización del 3% del valor de construcción) tributa en la base general. Si es vivienda habitual del inquilino, en contratos firmados desde el 26 de mayo de 2023 la reducción general es del 50% y puede subir hasta el 90% en zonas tensionadas, según la Ley 12/2023.'),
         ('¿Es mejor comprar con hipoteca para alquilar?', 'La hipoteca multiplica lo que rinde tu dinero cuando el interés es menor que la rentabilidad del piso, pero también el riesgo: si el piso se queda vacío, la cuota hay que pagarla igual. Mira el flujo mensual: si es negativo, necesitas colchón.')],
    creditos=['Fórmulas estándar de rentabilidad bruta, neta, PER y rentabilidad sobre fondos propios (ROE).',
              'Reducciones del IRPF por alquiler de vivienda: Ley 12/2023, por el derecho a la vivienda, y artículo 23 de la Ley 35/2006 del IRPF.',
              'Cuota de la hipoteca con el sistema francés (cuota constante).'],
    rel=['calculadora-gastos-compra-vivienda', 'calculadora-hipoteca', 'interes'],
    compartir='Calcula si te compensa comprar un piso para alquilar:',
    js=r'''
seg('hip','hip');
function cuotaDe(P,tin,anios){var i=tin/1200,m=anios*12;if(!P||!m)return 0;return i?P*i/(1-Math.pow(1+i,-m)):P/m;}
function pintar(){
  var precio=n('precio'),inv=precio*(1+n('gcompra')/100)+n('reforma'),renta=n('renta'),ing=renta*Math.min(n('meses'),12);
  var gas=n('comunidad')+n('ibi')+n('seguro')+ing*n('mant')/100,ben=ing-gas,neta=inv?ben/inv*100:0,bruta=precio?renta*12/precio*100:0;
  var hip=st.hip==='si';['fin','tin','plazo'].forEach(function(k){$(k).disabled=!hip;});
  var P=hip?precio*Math.min(n('fin'),100)/100:0,cuota=cuotaDe(P,n('tin'),n('plazo')),propio=inv-P;
  var interes1=P*n('tin')/100,flujo=(ben-cuota*12)/12,roe=propio>0?(ben-interes1)/propio*100:0;
  $('grande').textContent=AZ.fmt(neta,2)+'%';$('movilValor').textContent=AZ.fmt(neta,2)+'%';
  $('grandeSub').textContent='sobre '+AZ.eur(inv)+' invertidos · bruta '+AZ.fmt(bruta,2)+'%';
  nivel(neta>=5?'ok':neta>=3?'medio':'mal',neta>=5?'Buena rentabilidad':neta>=3?'Rentabilidad ajustada':'Rentabilidad baja');
  $('rInv').textContent=AZ.eur(inv);$('rIng').textContent=AZ.eur(ing);$('rGas').textContent='− '+AZ.eur(gas);$('rBen').textContent=AZ.eur(ben);
  $('rBruta').textContent=AZ.fmt(bruta,2)+'%';$('rPer').textContent=renta?AZ.fmt(precio/(renta*12),1)+' años':'–';
  $('rCuota').textContent=hip?AZ.eur(cuota)+' al mes':'Sin hipoteca';
  $('rFlujo').textContent=AZ.eur(hip?flujo:ben/12)+' al mes';
  $('rRoe').textContent=hip?AZ.fmt(roe,2)+'% (primer año)':AZ.fmt(neta,2)+'%';
  var rec=ben>0?inv/ben:0;
  $('nota').textContent=(ben>0?'Con este beneficio recuperas lo invertido en unos '+AZ.fmt(rec,0)+' años, sin contar la revalorización del piso ni el IRPF.':'Con estos números el alquiler no cubre los gastos.')+(hip&&flujo<0?' Ojo: con la hipoteca pones '+AZ.eur(-flujo)+' de tu bolsillo cada mes.':'');
  hash(['precio','gcompra','reforma','renta','meses','comunidad','ibi','seguro','mant','fin','tin','plazo']);
}
'''))

# 3. Finiquito e indemnización -------------------------------------------------------------------------------
CALCS.append(dict(
    slug='calculadora-finiquito', ogimg='calculadora-sueldo-neto', nombre='Calculadora de finiquito e indemnización',
    titulo='Calculadora de finiquito e indemnización por despido 2026',
    og='¿Cuánto te deben al dejar tu trabajo? Finiquito e indemnización',
    desc='Calcula tu finiquito e indemnización en 2026: días del mes, vacaciones no disfrutadas, pagas extra y la indemnización por despido improcedente, objetivo o fin de contrato.',
    pre='📄 Estatuto de los Trabajadores', h1='Lo que te deben <span>al dejar tu trabajo</span>',
    lead='Escribe tu sueldo, tus fechas y el motivo de la salida. Te calculamos el finiquito (salario pendiente, vacaciones y pagas extra) y la indemnización que marca la ley.',
    chips=['🗓️ Vacaciones y pagas', '⚖️ Improcedente u objetivo', '🧮 Antes y después de 2012'],
    st={'pagas': '14'},
    form=bloque('Tu contrato', [campo('bruto', 'Salario bruto anual', 24000, paso='500', col=True), segm('pagas', 'Pagas', [('14', '14 (extras aparte)'), ('12', '12 (prorrateadas)')], col=True),
                                '<div class="campo"><label for="inicio">Fecha de inicio</label><input type="date" id="inicio" value="2020-03-01"></div>',
                                '<div class="campo"><label for="fin">Último día trabajado</label><input type="date" id="fin"></div>']) + '\n' +
         bloque('La salida', ['<div class="campo" style="grid-column:1/-1"><label for="motivo">Motivo</label><select id="motivo"><option value="vol">Baja voluntaria</option><option value="imp" selected>Despido improcedente</option><option value="obj">Despido objetivo (causas económicas, técnicas…)</option><option value="tem">Fin de contrato temporal</option><option value="dis">Despido disciplinario procedente</option></select></div>',
                              campo('vacas', 'Vacaciones ya disfrutadas este año', 0, uni='días'), campo('pend', 'Días de vacaciones de años anteriores sin disfrutar', 0, uni='días')]),
    restit='Total que te corresponde', movil='Total',
    lineas=lineas([('rDias', 'Salario de los días del último mes', 0), ('rVac', 'Vacaciones no disfrutadas', 0), ('rExtra', 'Parte de pagas extra', 0), ('rFiniq', 'Finiquito', 1),
                   ('rInd', 'Indemnización', 0), ('rTotal', 'Total bruto', 1)]),
    extra='''<section class="bloque">
  <h2 class="t">Indemnización según el motivo</h2>
  <div class="tarjetas">
    <div class="tcard"><div class="big">33 días</div><h3>Despido improcedente</h3><p>33 días de salario por año trabajado, con un máximo de 24 mensualidades. Por el tiempo trabajado antes del 12 de febrero de 2012 se cuentan 45 días por año.</p></div>
    <div class="tcard"><div class="big">20 días</div><h3>Despido objetivo</h3><p>20 días por año trabajado, con un máximo de 12 mensualidades. Si después se declara improcedente, sube a 33 días.</p></div>
    <div class="tcard"><div class="big">12 días</div><h3>Fin de contrato temporal</h3><p>12 días por año trabajado. En la baja voluntaria y en el despido disciplinario procedente no hay indemnización, pero sí finiquito.</p></div>
  </div>
</section>''',
    faq=[('¿Qué incluye el finiquito?', 'El salario de los días trabajados del último mes, las vacaciones generadas y no disfrutadas, y la parte proporcional de las pagas extra si no las cobras prorrateadas. Te corresponde siempre, también si te vas tú.'),
         ('¿Cuánto es la indemnización por despido improcedente?', 'Desde la reforma laboral de 2012, 33 días de salario por año trabajado con un máximo de 24 mensualidades. Si empezaste antes del 12 de febrero de 2012, ese tiempo se paga a 45 días por año (artículo 56 del Estatuto de los Trabajadores y disposición transitoria undécima).'),
         ('¿La indemnización paga IRPF?', 'La indemnización por despido está exenta de IRPF hasta la cuantía obligatoria que marca la ley, con un máximo de 180.000 euros. El finiquito sí tributa y cotiza como una nómina más.'),
         ('¿Tengo que avisar si me voy de la empresa?', 'En la baja voluntaria se suele exigir un preaviso de 15 días, o el que diga tu convenio. Si no lo das, la empresa puede descontarte del finiquito los días que falten.')],
    creditos=['Indemnizaciones: artículos 49, 53 y 56 del Estatuto de los Trabajadores (Real Decreto Legislativo 2/2015) y disposición transitoria undécima.',
              'Exención en el IRPF: artículo 7.e de la Ley 35/2006, del IRPF.',
              'Vacaciones: 30 días naturales al año (artículo 38 del Estatuto). Pagas extra calculadas por semestres (enero a junio y julio a diciembre); tu convenio puede repartirlas de otra forma.',
              'Salario diario: salario bruto anual entre 365. No incluye complementos variables, horas extra ni lo que fije tu convenio.'],
    rel=['calculadora-sueldo-neto', 'calculadora-ahorro', 'calculadora-jubilacion'],
    compartir='Calcula tu finiquito y tu indemnización:',
    js=r'''
seg('pagas','pagas');
if(!$('fin').value){var h=new Date();$('fin').value=h.getFullYear()+'-'+('0'+(h.getMonth()+1)).slice(-2)+'-'+('0'+h.getDate()).slice(-2);}
var DIA=864e5;function f(s){var p=String(s).split('-');return p.length===3?Date.UTC(+p[0],+p[1]-1,+p[2]):NaN;}
function dias(a,b){return Math.max(0,Math.round((b-a)/DIA)+1);}
function pintar(){
  var bruto=n('bruto'),i0=f($('inicio').value),f0=f($('fin').value),motivo=$('motivo').value,catorce=st.pagas==='14';
  if(!isFinite(i0)||!isFinite(f0)||f0<i0){$('grande').textContent='–';$('grandeSub').textContent='Revisa las fechas';return;}
  var fd=new Date(f0),y=fd.getUTCFullYear(),m=fd.getUTCMonth(),d=fd.getUTCDate(),diario=bruto/365;
  var mensual=bruto/(catorce?14:12),diasMes=Math.min(d,30),pDias=mensual*diasMes/30;
  var ini=Math.max(i0,Date.UTC(y,0,1)),anioDias=(Date.UTC(y+1,0,1)-Date.UTC(y,0,1))/DIA;
  var gen=30*dias(ini,f0)/anioDias,pendV=Math.max(gen-n('vacas'),0)+n('pend'),pVac=pendV*diario;
  var pExtra=0;if(catorce){var s0=m<6?Date.UTC(y,0,1):Date.UTC(y,6,1),s1=m<6?Date.UTC(y,5,30):Date.UTC(y,11,31);pExtra=(bruto/14)*dias(Math.max(s0,i0),f0)/dias(s0,s1);}
  var finiq=pDias+pVac+pExtra,total=dias(i0,f0),anios=total/365,corte=Date.UTC(2012,1,12),ind=0,txt='';
  if(motivo==='imp'){
    if(i0<corte){var d1=dias(i0,Math.min(f0,corte-DIA))*45/365,d2=f0>=corte?dias(corte,f0)*33/365:0;var dd=d1>720?Math.min(d1,1260):Math.min(d1+d2,720);ind=dd*diario;txt=AZ.fmt(dd,1)+' días de salario (45 días por año hasta 2012 y 33 después)';}
    else{var dd2=Math.min(anios*33,720);ind=dd2*diario;txt=AZ.fmt(dd2,1)+' días de salario (33 por año, máximo 24 mensualidades)';}
  }else if(motivo==='obj'){var d3=Math.min(anios*20,360);ind=d3*diario;txt=AZ.fmt(d3,1)+' días de salario (20 por año, máximo 12 mensualidades)';}
  else if(motivo==='tem'){var d4=anios*12;ind=d4*diario;txt=AZ.fmt(d4,1)+' días de salario (12 por año)';}
  else txt='Sin indemnización en '+(motivo==='vol'?'la baja voluntaria':'el despido disciplinario procedente');
  var tot=finiq+ind;
  $('grande').textContent=AZ.eur(tot);$('movilValor').textContent=AZ.eur(tot);
  $('grandeSub').textContent='en bruto · '+AZ.fmt(anios,1)+' años en la empresa';
  nivel(ind>0?'ok':'medio',ind>0?'Indemnización: '+AZ.eur(ind):'Solo finiquito');
  $('rDiasL').textContent='Salario de '+diasMes+' días del último mes';$('rDias').textContent=AZ.eur(pDias);
  $('rVacL').textContent='Vacaciones no disfrutadas ('+AZ.fmt(pendV,1)+' días)';$('rVac').textContent=AZ.eur(pVac);
  $('rExtra').textContent=catorce?AZ.eur(pExtra):'Ya cobradas cada mes';$('rFiniq').textContent=AZ.eur(finiq);$('rInd').textContent=AZ.eur(ind);$('rTotal').textContent=AZ.eur(tot);
  $('nota').textContent=txt+'. La indemnización está exenta de IRPF dentro de los límites legales; el finiquito tributa como una nómina.'+(motivo==='vol'?' Si no das el preaviso de tu convenio, te pueden descontar esos días.':'');
  hash(['bruto','inicio','fin','motivo','vacas','pend']);
}
'''))

# 4. Ahorro -----------------------------------------------------------------------------------------------------
CALCS.append(dict(
    slug='calculadora-ahorro', ogimg='calculadora-sueldo-neto', nombre='Calculadora de ahorro',
    titulo='Calculadora de ahorro: cuánto ahorrar al mes (50/30/20)',
    og='¿Cuánto tienes que ahorrar al mes para tu meta?',
    desc='Calcula cuánto ahorrar al mes para llegar a tu meta, cómo repartir tu sueldo con la regla 50/30/20, tu fondo de emergencia y en cuánto tiempo lo consigues.',
    pre='🐷 Ahorro con método', h1='Tu meta, <span>mes a mes</span>',
    lead='Escribe lo que ganas, tus gastos fijos y la meta que quieres alcanzar. Te decimos cuánto apartar cada mes, cómo repartir tu sueldo y cuánto colchón necesitas.',
    chips=['🎯 Meta y plazo', '📐 Regla 50/30/20', '🛟 Fondo de emergencia'],
    form=bloque('Tus números', [campo('ingresos', 'Ingresos netos al mes', 1800, paso='50'), campo('fijos', 'Gastos fijos al mes', 950, paso='50')]) + '\n' +
         bloque('Tu meta', [campo('meta', 'Cuánto quieres reunir', 10000, paso='500'), campo('plazo', 'En cuánto tiempo', 24, uni='meses'),
                            campo('actual', 'Lo que ya tienes ahorrado', 1000, paso='100'), campo('rent', 'Rentabilidad anual (cuenta o fondo)', 2, uni='%', paso='0.25')]),
    restit='Tienes que ahorrar al mes', movil='Al mes',
    lineas=lineas([('rPct', 'Supone de tus ingresos', 0), ('rMargen', 'Te queda tras los gastos fijos', 0), ('r20', 'Con el 20% de tu sueldo llegarías en', 0),
                   ('', '<div class="apilada" id="apilada"></div>' + LEY.format('<span><b style="background:var(--n3)"></b>Necesidades 50%</span><span><b style="background:var(--violeta)"></b>Deseos 30%</span><span><b style="background:var(--cian)"></b>Ahorro 20%</span>'), 0),
                   ('rNec', 'Necesidades (50%)', 0), ('rDes', 'Deseos (30%)', 0), ('rAho', 'Ahorro e inversión (20%)', 0), ('rEmer', 'Fondo de emergencia recomendado', 1)]),
    extra='''<section class="bloque">
  <h2 class="t">Tres reglas para ahorrar sin agobios</h2>
  <div class="tarjetas">
    <div class="tcard"><div class="big">50/30/20</div><h3>Reparte tu sueldo</h3><p>La mitad para lo necesario (casa, comida, transporte), un 30% para lo que te apetece y un 20% para ahorrar o invertir. Si tus fijos pasan del 50%, empieza por ahí.</p></div>
    <div class="tcard"><div class="big">3 a 6 meses</div><h3>Primero, el colchón</h3><p>Antes de invertir, guarda entre 3 y 6 meses de gastos fijos en una cuenta disponible. Es lo que te protege de un despido o una avería.</p></div>
    <div class="tcard"><div class="big">Día 1</div><h3>Págate a ti primero</h3><p>Programa una transferencia el día que cobras. Lo que no ves en la cuenta corriente no se gasta, y el hábito pesa más que la cantidad.</p></div>
  </div>
</section>''',
    faq=[('¿Cuánto debería ahorrar al mes?', 'Una referencia muy usada es el 20% de tus ingresos netos (regla 50/30/20). Si no llegas, empieza con lo que puedas, aunque sea un 5%, y súbelo cada vez que cobres más.'),
         ('¿Qué es la regla 50/30/20?', 'Un reparto del sueldo neto: 50% para necesidades, 30% para deseos y 20% para ahorro e inversión. La popularizó la senadora Elizabeth Warren en el libro All Your Worth (2005).'),
         ('¿Cuánto dinero tengo que tener en el fondo de emergencia?', 'Entre 3 y 6 meses de gastos fijos. Si tus ingresos son variables o eres autónomo, mejor acercarte a 6 meses o más.'),
         ('¿Dónde guardo mis ahorros?', 'El fondo de emergencia, en una cuenta remunerada o un depósito con disponibilidad inmediata. Para metas a más de 5 años, muchas personas usan fondos indexados. Compara comisiones y riesgo antes de decidir.')],
    creditos=['Regla 50/30/20: Elizabeth Warren y Amelia Warren Tyagi, All Your Worth: The Ultimate Lifetime Money Plan (2005).',
              'Aportación mensual con interés compuesto mensual (fórmula de anualidad).'],
    rel=['calculadora-jubilacion', 'interes', 'calculadora-sueldo-neto'],
    compartir='Calcula cuánto ahorrar al mes para tu meta:',
    js=r'''
function necesario(meta,actual,meses,r){var i=r/1200,fv=actual*Math.pow(1+i,meses),falta=meta-fv;if(falta<=0)return 0;return i?falta*i/(Math.pow(1+i,meses)-1):falta/meses;}
function mesesCon(meta,actual,ap,r){var i=r/1200,s=actual,k=0;if(ap<=0&&actual<meta&&!i)return Infinity;while(s<meta&&k<1200){s=s*(1+i)+ap;k++;}return k;}
function pintar(){
  var ing=n('ingresos'),fijos=n('fijos'),meta=n('meta'),pl=Math.max(Math.round(n('plazo')),1),act=n('actual'),r=n('rent');
  var ap=necesario(meta,act,pl,r),pct=ing?ap/ing*100:0,margen=ing-fijos;
  $('grande').textContent=AZ.eur(ap);$('movilValor').textContent=AZ.eur(ap);
  $('grandeSub').textContent='durante '+pl+' meses para reunir '+AZ.eur(meta);
  nivel(ap<=margen*0.6&&pct<=20?'ok':ap<=margen?'medio':'mal',ap<=margen*0.6&&pct<=20?'Meta asumible':ap<=margen?'Meta exigente':'Supera tu margen');
  $('rPct').textContent=AZ.fmt(pct,1)+'%';$('rMargen').textContent=AZ.eur(margen);
  var m20=mesesCon(meta,act,ing*0.2,r);$('r20').textContent=m20>=1200?'Más de 100 años':m20+' meses ('+AZ.fmt(m20/12,1)+' años)';
  $('rNec').textContent=AZ.eur(ing*0.5);$('rDes').textContent=AZ.eur(ing*0.3);$('rAho').textContent=AZ.eur(ing*0.2);
  $('apilada').innerHTML='<i style="width:50%;background:var(--n3)"></i><i style="width:30%;background:var(--violeta)"></i><i style="width:20%;background:var(--cian)"></i>';
  $('rEmer').textContent=AZ.eur(fijos*3)+' a '+AZ.eur(fijos*6);
  var fp=ing?fijos/ing*100:0;
  $('nota').textContent='Tus gastos fijos son el '+AZ.fmt(fp,0)+'% de lo que ingresas'+(fp>50?': por encima del 50% recomendado, revisar alquiler, seguros o suscripciones libera margen.':', dentro del 50% recomendado.');
  hash(['ingresos','fijos','meta','plazo','actual','rent']);
}
'''))

# 5. Jubilación -------------------------------------------------------------------------------------------------
CALCS.append(dict(
    slug='calculadora-jubilacion', ogimg='calculadora-sueldo-neto', nombre='Calculadora de jubilación',
    titulo='Calculadora de jubilación: cuánto ahorrar para retirarte',
    og='¿Cuánto tienes que ahorrar para jubilarte tranquilo?',
    desc='Calcula cuánto ahorrar al mes para complementar tu pensión: capital que necesitas al jubilarte, efecto de la inflación, rentabilidad y la regla del 4%.',
    pre='🌅 Planifica tu retiro', h1='Tu jubilación, <span>con números</span>',
    lead='Escribe tu edad, lo que te gustaría gastar al mes cuando te jubiles y la pensión que esperas. Te calculamos el capital que necesitas y cuánto ahorrar desde hoy.',
    chips=['💶 En euros de hoy', '📉 Con inflación', '🧮 Regla del 4%'],
    form=bloque('Tú', [campo('edad', 'Edad actual', 35, uni='años'), campo('jub', 'Edad de jubilación', 67, uni='años'),
                       campo('gasto', 'Gasto al mes cuando te jubiles', 2000, paso='50'), campo('pension', 'Pensión pública estimada al mes', 1300, paso='50')]) + '\n' +
         bloque('Tu ahorro', [campo('actual', 'Ahorro actual para la jubilación', 10000, paso='500'), campo('rent', 'Rentabilidad anual esperada', 5, uni='%', paso='0.25'),
                              campo('ipc', 'Inflación anual', 2, uni='%', paso='0.25'), campo('hasta', 'Edad hasta la que planificas', 92, uni='años')]),
    restit='Ahorro necesario al mes', movil='Al mes',
    lineas=lineas([('rFalta', 'Lo que te faltará cada mes', 0), ('rCap', 'Capital necesario al jubilarte', 1), ('rActual', 'Lo que aportará tu ahorro actual', 0),
                   ('rAnios', 'Años para ahorrar', 0), ('r4', 'Capital según la regla del 4%', 0), ('rReal', 'Rentabilidad real (descontada la inflación)', 0)]),
    extra='''<section class="bloque">
  <h2 class="t">Cómo leer el resultado</h2>
  <div class="tarjetas">
    <div class="tcard"><div class="big">€ de hoy</div><h3>Sin trampas de la inflación</h3><p>Todo está en euros con el poder de compra de hoy. Por eso usamos la rentabilidad real: lo que ganas por encima de la inflación.</p></div>
    <div class="tcard"><div class="big">4%</div><h3>La regla del 4%</h3><p>Del estudio Trinity (1998): retirar cada año el 4% del capital inicial, ajustado a la inflación, aguantó al menos 30 años en casi todos los escenarios históricos de EE. UU.</p></div>
    <div class="tcard"><div class="big">Antes</div><h3>El tiempo pesa más</h3><p>Empezar 10 años antes puede reducir a la mitad lo que hay que ahorrar cada mes, por el efecto del interés compuesto.</p></div>
  </div>
</section>''',
    faq=[('¿Cuánto dinero necesito para jubilarme?', 'Depende de lo que vayas a gastar y de tu pensión. Una referencia es la regla del 4%: multiplica por 25 lo que te faltará cada año. Si te faltan 700 euros al mes (8.400 al año), necesitarías unos 210.000 euros.'),
         ('¿Cómo sé cuánta pensión voy a cobrar?', 'La Seguridad Social tiene un simulador de jubilación en su sede electrónica (Tu Seguridad Social) con tus cotizaciones reales. Úsalo y escribe aquí la cifra que te dé.'),
         ('¿Qué rentabilidad es razonable para la jubilación?', 'A largo plazo, una cartera diversificada en bolsa mundial ha rendido históricamente por encima de la inflación, pero con caídas fuertes por el camino. Una cartera más conservadora rinde menos. Prueba varias cifras para ver cuánto cambia el resultado.'),
         ('¿Planes de pensiones o fondos indexados?', 'Los planes de pensiones permiten reducir la base del IRPF (con límites), pero el dinero queda inmovilizado y tributa como rendimiento del trabajo al rescatarlo. Los fondos indexados no desgravan al aportar, pero son flexibles y se puede traspasar sin pagar impuestos. Compara comisiones y consulta a un asesor.')],
    creditos=['Regla del 4%: Cooley, Hubbard y Walz (1998), «Retirement Savings: Choosing a Withdrawal Rate That Is Sustainable», AAII Journal (estudio Trinity).',
              'Rentabilidad real = (1 + rentabilidad) / (1 + inflación) − 1. Capital necesario como valor actual de una renta mensual durante los años de jubilación.',
              'Edad ordinaria de jubilación en España: 67 años, o 65 con carreras de cotización largas (Ley 27/2011).'],
    rel=['calculadora-ahorro', 'interes', 'calculadora-rentabilidad-alquiler'],
    compartir='Calcula cuánto ahorrar para tu jubilación:',
    js=r'''
function pintar(){
  var edad=n('edad'),jub=Math.max(n('jub'),edad),hasta=Math.max(n('hasta'),jub+1),falta=Math.max(n('gasto')-n('pension'),0),act=n('actual');
  var real=(1+n('rent')/100)/(1+n('ipc')/100)-1,i=Math.pow(1+real,1/12)-1,mA=Math.round((jub-edad)*12),mJ=Math.round((hasta-jub)*12);
  var cap=i?falta*(1-Math.pow(1+i,-mJ))/i:falta*mJ,fvAct=act*Math.pow(1+i,mA),gap=Math.max(cap-fvAct,0);
  var ap=mA>0?(i?gap*i/(Math.pow(1+i,mA)-1):gap/mA):gap;
  $('grande').textContent=AZ.eur(ap);$('movilValor').textContent=AZ.eur(ap);
  $('grandeSub').textContent='desde hoy hasta los '+AZ.fmt(jub,0)+' años, en euros de hoy';
  nivel(falta===0?'ok':ap<=300?'ok':ap<=800?'medio':'mal',falta===0?'Tu pensión cubre tu gasto':'Te faltarán '+AZ.eur(falta)+' al mes');
  $('rFalta').textContent=AZ.eur(falta);$('rCap').textContent=AZ.eur(cap);$('rActual').textContent=AZ.eur(fvAct);
  $('rAnios').textContent=AZ.fmt(mA/12,0)+' años';$('r4').textContent=AZ.eur(falta*12*25);$('rReal').textContent=AZ.fmt(real*100,2)+'%';
  var ap10=mA>120?(i?gap*i/(Math.pow(1+i,mA-120)-1):gap/(mA-120)):0;
  $('nota').textContent=gap<=0?'Con tu ahorro actual y esta rentabilidad ya cubres lo que te faltará.':(ap10?'Si empiezas 10 años más tarde, tendrías que ahorrar '+AZ.eur(ap10)+' al mes.':'Queda poco tiempo: retrasar la jubilación o bajar el gasto previsto cambia mucho el resultado.');
  hash(['edad','jub','gasto','pension','actual','rent','ipc','hasta']);
}
'''))

if __name__ == '__main__':
    for c in CALCS:
        d = os.path.join(OUT, c['slug']); os.makedirs(d, exist_ok=True)
        open(os.path.join(d, 'index.html'), 'w', encoding='utf-8').write(pagina(c))
        print('escrita', c['slug'], len(c['titulo']))
