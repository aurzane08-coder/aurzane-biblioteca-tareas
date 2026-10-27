"""Descarga del RUCT (Ministerio) todas las universidades españolas y sus grados oficiales vigentes.
Salida: univ/data/ruct.json
"""
import re, json, time, html, os, sys, urllib.request, urllib.parse, http.cookiejar

B = 'https://www.educacion.gob.es/ruct/'
UA = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36'
EXCLUIR = {'000', '086', '091', '092', '093', '095', '096', '099', '101', '105'}
cj = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
op.addheaders = [('User-Agent', UA)]


def get(url, data=None):
    for i in range(6):
        try:
            if data is not None:
                data_b = urllib.parse.urlencode(data).encode()
                r = op.open(url, data_b, timeout=60)
            else:
                r = op.open(url, timeout=60)
            b = r.read()
            time.sleep(0.12)
            return b.decode('iso-8859-15', 'replace')
        except Exception as e:
            print('  reintento', url[:90], e, flush=True)
            time.sleep(3 + i * 3)
    return ''


def limpio(s):
    s = re.sub(r'<[^>]+>', ' ', s)
    s = html.unescape(s).replace('\xa0', ' ')
    return re.sub(r'\s+', ' ', s).strip()


def campos(page):
    """Pares 'Etiqueta :' -> valor de las fichas del RUCT."""
    out = {}
    for m in re.finditer(r'<label[^>]*>\s*<span[^>]*>(.*?)</span>(.*?)</label>', page, re.S):
        k = limpio(m.group(1)).rstrip(':').strip()
        v = limpio(m.group(2))
        if k and k not in out:
            out[k] = v
    if not out:  # formato alternativo: <dt>/<dd> o <strong>
        for m in re.finditer(r'<(?:dt|th|strong)[^>]*>(.*?)</(?:dt|th|strong)>\s*<(?:dd|td|span)[^>]*>(.*?)</(?:dd|td|span)>', page, re.S):
            out.setdefault(limpio(m.group(1)).rstrip(':').strip(), limpio(m.group(2)))
    return out


def texto_campos(page):
    """Respaldo: busca 'Etiqueta : valor' en el texto plano."""
    t = limpio(page)
    return t


def valor(t, etiqueta, sig):
    m = re.search(re.escape(etiqueta) + r'\s*:\s*(.*?)\s*(?:' + '|'.join(re.escape(x) for x in sig) + r')\s*:', t)
    return m.group(1).strip() if m else ''


def universidades():
    p = get(B + 'consultaestudios?actual=estudios')
    sel = p[p.find('id="codigoUniversidad"'):]
    sel = sel[:sel.find('</select>')]
    return [(c, limpio(n)) for c, n in re.findall(r'<option value="(\d{3})"\s*>(.*?)</option>', sel) if c not in EXCLUIR]


def ficha_univ(cod):
    t = texto_campos(get(f'{B}universidad.action?codigoUniversidad={cod}&actual=universidades'))
    claves = ['Código de la universidad', 'Acrónimo', 'Tipo', 'CIF', 'Código Erasmus', 'Con ánimo de lucro', 'Administración Educativa Responsable',
              'Domicilio', 'Código postal', 'Localidad', 'Municipio', 'Provincia', 'Comunidad Autónoma', 'Mapa', 'URL', 'E-mail', 'Teléfono 1', 'Fax',
              'Tipo Boletín', 'Año publicación', 'Tipo disposición']
    d = {}
    for i, k in enumerate(claves[:-1]):
        d[k] = valor(t, k, claves[i + 1:])
    return d


def lista_grados(cod):
    datos = {'consulta': '1', 'codigoEstudio': '', 'codigoUniversidad': cod, 'descripcionEstudio': '', 'codigoTipo': 'G', 'codigoSubTipo': '',
             'codigoRama': '', 'ambito': '', 'codigoEstado': '', 'situacion': '', 'buscarHistorico': 'N', 'action:listaestudios': 'Consultar'}
    get(B + 'consultaestudios?actual=estudios')
    page = get(B + 'consultaestudios.action?actual=estudios', datos)
    filas, n = [], 1
    while True:
        tab = page[page.find('id="estudio"'):]
        tab = tab[:tab.find('</table>')]
        for tr in re.findall(r'<tr class="(?:odd|even)">(.*?)</tr>', tab, re.S):
            tds = re.findall(r'<td[^>]*>(.*?)</td>', tr, re.S)
            if len(tds) < 5:
                continue
            link = re.search(r'estudio\.action\?([^"]+)"', tds[1])
            filas.append({'codigo': limpio(tds[0]), 'titulo': limpio(tds[1]), 'nivel': limpio(tds[3]), 'estado': limpio(tds[4]),
                          'url': 'estudio.action?' + html.unescape(link.group(1)) if link else ''})
        n += 1
        sig = re.search(r'href="(listaestudios\?[^"]*d-\d+-p=' + str(n) + r'[^"]*)"', page)
        if not sig:
            break
        page = get(B + html.unescape(sig.group(1)))
    return filas


def vigente(estado):
    e = estado.upper()
    if 'EXTINGUIDA' in e or 'A EXTINGUIR' in e or 'JUDICIAL' in e:
        return False
    return 'PUBLICADO' in e or 'AUTORIZADO' in e


def ficha_grado(url):
    p = get(B + url)
    t = limpio(p)
    d = {'rama': valor(t, 'Rama', ['Campo de estudio', 'Créditos', 'Nº Créditos de Formación Básica']),
         'campo': valor(t, 'Campo de estudio', ['Créditos', 'Nº Créditos de Formación Básica']),
         'creditos': valor(t, 'Créditos Totales', ['Fechas y Enlaces a BOE', 'Fecha de verificación']),
         'meces': valor(t, 'Nivel MECES', ['Rama', 'Campo de estudio'])}
    d['rama'] = d['rama'].split(' Campo de estudio')[0]
    d['campo'] = re.sub(r'\s+Créditos$', '', d['campo']).strip()
    m = re.match(r'\d+(?:[.,]\d+)?', d['creditos']); d['creditos'] = m.group(0) if m else ''
    i = p.find('id="centro"')
    centros = []
    if i > 0:
        tab = p[i:p.find('</table>', i)]
        for tr in re.findall(r'<tr class="(?:odd|even)">(.*?)</tr>', tab, re.S):
            tds = re.findall(r'<td[^>]*>(.*?)</td>', tr, re.S)
            m = re.search(r'codigoUniversidad=(\d+)&amp;codigoCentro=(\d+)', tr)
            if len(tds) >= 3:
                centros.append({'univ': m.group(1) if m else '', 'codigo': limpio(tds[1]), 'nombre': limpio(tds[2])})
    d['centros'] = centros
    return d


def ficha_centro(cu, cc):
    t = limpio(get(f'{B}centro.action?codigoUniversidad={cu}&codigoCentro={cc}&actual=centros'))
    claves = ['Municipio', 'Provincia', 'Comunidad Autónoma', 'Mapa', 'URL', 'E-mail', 'Teléfono']
    d = {k: valor(t, k, claves[i + 1:] + ['Datos complementarios', 'Documento', 'Tipo de centro']) for i, k in enumerate(claves[:3])}
    d['tipo'] = valor(t, 'Tipo de centro', ['Tipo de enseñanza', 'Naturaleza', 'Datos de ubicación', 'Domicilio'])
    d['ensenanza'] = valor(t, 'Tipo de enseñanza', ['Naturaleza', 'Datos de ubicación', 'Domicilio', 'Centro adscrito'])
    i = t.find('Datos de identificación')
    d['texto'] = t[i:i + 900] if i >= 0 else t[:900]
    return d


def denominacion(t):
    m = re.match(r'^Graduad[oa](?: o Graduad[oa])? en (.+?) por (?:la|el|las|los) .+$', t)
    if m:
        return m.group(1).strip()
    m = re.match(r'^Graduad[oa](?: o Graduad[oa])? en (.+)$', t)
    return m.group(1).strip() if m else t


if __name__ == '__main__':
    salida = 'univ/data/ruct.json'
    prev = json.load(open(salida)) if os.path.exists(salida) and '--seguir' in sys.argv else {}
    unis = universidades()
    print(len(unis), 'universidades', flush=True)
    res = prev or {'universidades': {}, 'centros': {}}
    for cod, nombre in unis:
        if cod in res['universidades'] and res['universidades'][cod].get('completa'):
            continue
        u = {'codigo': cod, 'nombre': nombre, 'ficha': ficha_univ(cod)}
        filas = [f for f in lista_grados(cod) if vigente(f['estado'])]
        grados = []
        for f in filas:
            d = ficha_grado(f['url']) if f['url'] else {}
            grados.append({**f, 'denominacion': denominacion(f['titulo']), **d})
            for c in d.get('centros', []):
                k = c['univ'] + '-' + c['codigo']
                if c['univ'] and k not in res['centros']:
                    res['centros'][k] = {'nombre': c['nombre'], **ficha_centro(c['univ'], c['codigo'])}
        u['grados'] = grados
        u['completa'] = True
        res['universidades'][cod] = u
        print(cod, nombre, len(grados), 'grados', len(res['centros']), 'centros', flush=True)
        json.dump(res, open(salida, 'w'), ensure_ascii=False)
    print('FIN', sum(len(u['grados']) for u in res['universidades'].values()))
