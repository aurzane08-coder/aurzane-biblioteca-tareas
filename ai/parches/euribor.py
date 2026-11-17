"""Euríbor siempre al día en la calculadora de hipoteca de BUILD (17/11/2026, etapa 3 de la auditoría, tarea 42).
El flujo de GitHub descarga del Banco Central Europeo la media mensual oficial del euríbor a 12 meses
(serie FM.M.U2.EUR.RT.MM.EURIBOR1YD_.HSTA, la misma que publica el Banco de España como «euríbor oficial»)
y llama a este parche con el valor y el mes: python3 - www 2.512 2026-10
Cambia el valor por defecto, la etiqueta, la pregunta frecuente y la fuente. Si el dato no cambia, no toca nada.
Copia previa en <web>/eliminar/euribor-FECHA/."""
import os, re, sys, shutil, datetime
base = os.path.expanduser('~/' + sys.argv[1]); valor = float(sys.argv[2]); anio, mes = map(int, sys.argv[3].split('-'))
MESES = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
m = MESES[mes - 1]; v3 = f'{valor:.3f}'; vc = v3.replace('.', ',')
if not (-2 < valor < 15): sys.exit('valor fuera de rango: ' + str(valor))
p = base + '/build.aurzane.com/public_html/calculadora-hipoteca/index.html'
t = open(p, encoding='utf-8').read(); n = t
n = re.sub(r'(id="euribor" value=")[-0-9.]+(")', r'\g<1>' + v3 + r'\2', n)
n = re.sub(r'📈 Euríbor -?[0-9]+,[0-9]+%', f'📈 Euríbor {vc}%', n)
n = re.sub(r'Último dato oficial: [a-záéíóú]+ [0-9]{4}', f'Último dato oficial: {m} {anio}', n)
n = re.sub(r'El euríbor a 12 meses cerró [a-záéíóú]+ de [0-9]{4} en el -?[0-9]+,[0-9]+%, según el [A-Za-zéñ ]+?\.',
           f'El euríbor a 12 meses cerró {m} de {anio} en el {vc}% de media mensual, según el Banco Central Europeo.', n)
n = re.sub(r'Euríbor a 12 meses: [^<]*?\([a-záéíóú]+ -?[0-9]+,[0-9]+%\)\.', f'Euríbor a 12 meses: Banco Central Europeo, media mensual oficial ({m} de {anio}: {vc}%).', n)
if n == t:
    print(f'::notice::Euríbor ya al día ({m} {anio}: {vc}%)'); sys.exit(0)
copia = base + '/build.aurzane.com/eliminar/euribor-' + datetime.date.today().strftime('%Y%m%d')
os.makedirs(copia, exist_ok=True); shutil.copy2(p, copia + '/index.html')
open(p + '.tmp', 'w', encoding='utf-8').write(n); os.replace(p + '.tmp', p)
print(f'::notice::Euríbor actualizado en la calculadora de hipoteca: {m} {anio}, {vc}%')
