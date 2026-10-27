# -*- coding: utf-8 -*-
"""Genera los SQL de importación a Supabase: España (RUCT) y universidades principales.
Uso: python3 sql_import.py DATOS SALIDA_DIR
Produce 01_espana_limpiar.sql, 02_espana_universidades.sql, 03_espana_carreras_N.sql, 04_principales.sql
"""
import json, os, re, sys, uuid

DATOS, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)
RUCT = json.load(open(os.path.join(DATOS, 'ruct.json'), encoding='utf-8'))
PRIN = json.load(open(os.path.join(DATOS, 'principales.json'), encoding='utf-8'))
EN_LINEA = {'028', '054', '074', '076', '077', '080', '094', '108'}
NS = uuid.UUID('6f1c6b1e-6b55-4c8e-9c51-6e7a2a1d0b00')


def q(v):
    if v is None or v == '':
        return 'null'
    if isinstance(v, bool):
        return 'true' if v else 'false'
    if isinstance(v, (int, float)):
        return str(v)
    return "'" + str(v).replace("'", "''") + "'"


def region_de(ca):
    ca = re.sub(r'\s*Datos complementarios.*$', '', ca or '').strip()
    r = re.sub(r'^(Comunidad Foral de |Comunidad Autónoma (de |del )?|Comunidad (de |del )?|Comunitat |Principado de |Región de |Ciudad Autónoma de |Illes |Islas )', '', ca).strip()
    r = {'Valenciana': 'Comunidad Valenciana', 'Madrid': 'Comunidad de Madrid', 'Balears': 'Islas Baleares', 'Baleares': 'Islas Baleares', 'la Rioja': 'La Rioja', 'Las Illes Balears': 'Islas Baleares', 'Illes Balears': 'Islas Baleares'}.get(r, r)
    return r[:1].upper() + r[1:]


def muni(m):
    m = re.sub(r'\s*Datos complementarios.*$', '', m or '').strip()
    if '/' in m:
        m = m.split('/')[-1].strip()
    x = re.match(r'^(.+), (A|O|La|El|Los|Las|L\'|Les|Els)$', m)
    if x:
        m = x.group(2) + ("" if x.group(2).endswith("'") else ' ') + x.group(1)
    return {'Iruña': 'Pamplona', 'Iruña/Pamplona': 'Pamplona', 'Donostia': 'San Sebastián', 'València': 'Valencia', 'Castelló de la Plana': 'Castellón de la Plana', 'Elx': 'Elche'}.get(m, m)


def nombre_es(n):
    # El RUCT usa mayúsculas parciales; dejamos el nombre oficial tal cual.
    return re.sub(r'\s+', ' ', n).strip()


open(os.path.join(OUT, '01_espana_limpiar.sql'), 'w').write(
    "-- Sustituye las 5 universidades españolas antiguas por el RUCT completo\n"
    "delete from public.carreras where universidad_id in (select id from public.universidades where pais = 'España' and coalesce(fuente,'') <> 'admin');\n"
    "delete from public.universidades where pais = 'España' and coalesce(fuente,'') <> 'admin';\n")

unis, carr = [], []
centros = RUCT.get('centros', {})
for cod, r in sorted(RUCT['universidades'].items()):
    f = r.get('ficha', {})
    uid = str(uuid.uuid5(NS, 'ruct-' + cod))
    tipo = (f.get('Tipo') or '').lower()
    tipo = 'pública' if 'públic' in tipo or 'public' in tipo else 'privada'
    web = (f.get('URL') or '').split()[0] if f.get('URL') else ''
    if web and not web.startswith('http'):
        web = 'https://' + web
    anio = f.get('Año publicación') or ''
    unis.append('(' + ','.join([q(uid), q(nombre_es(r['nombre'])), q('Universidad'), q(tipo), q('España'), q(web), q(muni(f.get('Municipio') or f.get('Localidad'))),
                                 q(region_de(f.get('Comunidad Autónoma'))), q(f.get('Acrónimo')), q(int(anio) if re.fullmatch(r'\d{4}', anio) else None),
                                 q(cod in EN_LINEA), q('RUCT'), q(cod)]) + ')')
    for g in r.get('grados', []):
        sedes = []
        for c in g.get('centros', []):
            m = muni((centros.get(c['univ'] + '-' + c['codigo'], {}) or {}).get('Municipio'))
            if m and m not in sedes:
                sedes.append(m)
        cred = g.get('creditos') or ''
        cred = float(cred.replace(',', '.')) if re.fullmatch(r'\d+(?:[.,]\d+)?', cred) else None
        carr.append('(' + ','.join([q(uid), q(g.get('denominacion') or g['titulo']), q(g.get('campo')), q('Universitario (grado)'), q('En línea' if cod in EN_LINEA else None),
                                     q(region_de(f.get('Comunidad Autónoma'))), q(sedes[0] if sedes else (muni(f.get('Municipio')) or None)), q('programa'),
                                     q(g.get('rama')), q(cred), q(', '.join(sedes)), q(g.get('codigo'))]) + ')')

open(os.path.join(OUT, '02_espana_universidades.sql'), 'w').write(
    'insert into public.universidades (id,nombre,tipo_ies,tipo,pais,sitio_web,ciudad,region,acronimo,anio_creacion,en_linea,fuente,codigo_externo) values\n'
    + ',\n'.join(unis) + '\non conflict (id) do nothing;\n')

COLS = 'insert into public.carreras (universidad_id,nombre,campo_amplio,nivel_categoria,modalidad,provincia,canton,nivel_detalle,rama,creditos,sedes,codigo_externo) values\n'
TROZO = 1500
for i in range(0, len(carr), TROZO):
    open(os.path.join(OUT, f'03_espana_carreras_{i // TROZO + 1}.sql'), 'w').write(COLS + ',\n'.join(carr[i:i + TROZO]) + ';\n')

pr = []
for p in PRIN:
    pr.append('(' + ','.join([q(p['nombre']), q('Universidad'), q('pública' if p['tipo'].lower().startswith('púb') else 'privada'), q(p['pais']),
                               q(p.get('web_final') or p['web']), q(p['ciudad']), q('principales')]) + ')')
open(os.path.join(OUT, '04_principales.sql'), 'w').write(
    "delete from public.universidades u where u.fuente = 'principales';\n"
    'insert into public.universidades (nombre,tipo_ies,tipo,pais,sitio_web,ciudad,fuente) values\n' + ',\n'.join(pr) + ';\n')
print(len(unis), 'universidades RUCT,', len(carr), 'grados,', len(pr), 'principales')
