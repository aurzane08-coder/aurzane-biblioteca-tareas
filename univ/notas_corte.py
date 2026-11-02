# -*- coding: utf-8 -*-
"""Descarga las notas de corte oficiales de grado y doble grado (QEDU, Ministerio de Ciencia,
Innovación y Universidades) y las guarda en univ/data/notas_corte.json."""
import json, sys, time, urllib.parse, urllib.request
URL = 'https://www.ciencia.gob.es/home/qedu/main/zona02/0'
UA = 'Mozilla/5.0 (AURZANE catalogo universidades; hola@aurzane.com)'
out = []
for nivel in ("'GRADO'", "'GRADOD'"):
    datos = urllib.parse.urlencode({'action': 'tarjeta', 'offset': 0, 'consulta': 'Grado', 'niveles': nivel, 'ambitos': ''}).encode()
    for i in range(3):
        try:
            req = urllib.request.Request(URL, data=datos, headers={'User-Agent': UA, 'X-Requested-With': 'XMLHttpRequest', 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8', 'Referer': 'https://www.ciencia.gob.es/qedu.html'})
            filas = json.load(urllib.request.urlopen(req, timeout=120)); break
        except Exception as e:
            print('reintento', i + 1, e); time.sleep(10); filas = []
    print(nivel, len(filas))
    for f in filas:
        nota = f.get('notaCorte')
        try: nota = round(float(nota), 3) if nota not in (None, '', 'null') else None
        except ValueError: nota = None
        out.append({'titulo': f.get('titulacion'), 'cod_titulo': f.get('codTitula'), 'universidad': f.get('nombreUniversidad'), 'cod_univ': f.get('codUniv'),
                    'centro': f.get('nombreCentro'), 'tipo_centro': f.get('tipoCentro'), 'tipo': f.get('tipoUniversidad'), 'ccaa': f.get('ccaa'),
                    'provincia': f.get('provincia'), 'nota': nota, 'curso': f.get('anio'), 'nivel': f.get('nivel')})
if len(out) < 1000:
    sys.exit('Muy pocas filas: no se guarda nada para no perder los datos anteriores')
json.dump({'fuente': 'QEDU, Ministerio de Ciencia, Innovación y Universidades', 'url': 'https://www.ciencia.gob.es/qedu.html', 'filas': out},
          open('univ/data/notas_corte.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
print('OK', len(out), 'filas,', sum(1 for x in out if x['nota']), 'con nota')
