# Textos que prometían algo que los tests gratis no dan (devolución con un profesional, interpretación clínica).
# Copia del original en <web>/eliminar/textos-FECHA/. Uso: python3 textos.py <carpeta_www>
import os, sys, shutil, datetime
base = sys.argv[1]; hoy = datetime.datetime.now().strftime('%Y%m%d-%H%M')
CAMBIOS = {
    'mind.aurzane.com/public_html/index.html': [
        ('<h4>Sin algoritmos genéricos</h4><p>Interpretación clínica real, no un resultado automático sin contexto.</p>',
         '<h4>Escalas validadas</h4><p>Cuestionarios publicados que usan los profesionales, con su referencia.</p>'),
        ('<h4>100% virtual</h4><p>Tests online, corrección automática, devolución con profesional.</p>',
         '<h4>Resultado al instante</h4><p>Tu puntuación explicada al momento, gratis y sin registro.</p>')]}
for rel, pares in CAMBIOS.items():
    f = os.path.join(base, rel)
    try: s = open(f, encoding='utf-8').read()
    except Exception as e: print('no encontrado', rel, e); continue
    t = s
    for a, b in pares: t = t.replace(a, b)
    if t == s: print('sin cambios', rel); continue
    web = rel.split('/')[0]; copia = os.path.join(base, web, 'eliminar', 'textos-' + hoy, os.path.basename(f))
    os.makedirs(os.path.dirname(copia), exist_ok=True); shutil.copy2(f, copia)
    open(f, 'w', encoding='utf-8').write(t); print('corregido', rel)
