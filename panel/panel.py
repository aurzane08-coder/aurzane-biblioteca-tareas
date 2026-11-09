"""Panel privado de resultados de AURZANE (aurzane.com/panel/).

Junta en un solo JSON lo que ya se mide en distintos sitios y lo deja en el servidor, fuera de la web
(www/aurzane.com/privado-ai/panel.json). Solo lo lee panel.php después de comprobar que quien entra es administrador.
  - Visitas y páginas más vistas: registros de acceso de SiteGround (sin robots ni archivos estáticos).
  - Boletín: suscriptores confirmados y pendientes.
  - Clics en enlaces de compra (Amazon y Awin) y ventas de Awin (API con AWIN_TOKEN).
  - Clics desde redes sociales (marketing/clics.csv) y seguidores (marketing/seguidores.json).
  - Tienda y biblioteca: número de libros. Solicitudes de colegios.
Entradas: SSH (orden ssh), SG_DEST (usuario@host), AWIN_TOKEN.
"""
import json, os, re, subprocess, datetime, collections, urllib.request, csv

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SSH = os.environ.get('SSH', ''); DEST = os.environ.get('SG_DEST', '')
HOY = datetime.date.today()
DOMINIOS = ['aurzane.com', 'mind.aurzane.com', 'nexus.aurzane.com', 'live.aurzane.com', 'learn.aurzane.com', 'build.aurzane.com', 'ovp.aurzane.com']


def remoto(orden, t=300, entrada=None):
    if not SSH or not DEST: return ''
    try: return subprocess.run(SSH.split() + [DEST, orden], capture_output=True, text=True, timeout=t, input=entrada).stdout
    except Exception as e: print('remoto', e); return ''


def leer(ruta, d):
    try: return json.load(open(os.path.join(R, ruta), encoding='utf-8'))
    except Exception: return d


P = {'generado': datetime.datetime.utcnow().isoformat(timespec='minutes') + 'Z', 'avisos': []}

# ---------------------------------------------------------------- visitas (registros de acceso)
# Se procesa en el servidor y solo baja el recuento: día, dominio y página.
BOTS = r'bot|crawl|spider|slurp|facebookexternalhit|preview|monitor|curl|python|go-http|wget|headless|lighthouse|pagespeed|uptime|scan|semrush|ahrefs|mj12|dotbot|petal|bytespider|gptbot|claude|perplexity|feed|java\/|okhttp|axios|node-fetch|php\/'
# 1.ª pasada: una línea por página vista (día, dominio, ruta, visitante); 2.ª pasada: recuentos. Solo bajan los recuentos.
AWK1 = r'''{ split($4, t, /[\[\/:]/); if (t[4] == "") next;
  n = split($0, q, "\""); if (n < 6) next;
  split(q[2], rq, " "); if (rq[1] != "GET") next;
  split(q[3], st, " "); if (st[1] != "200") next;
  ua = tolower(q[6]); if (ua ~ /BOTS/ || ua == "" || ua == "-") next;
  u = rq[2]; sub(/\?.*/, "", u);
  if (u ~ /\.(js|css|png|jpe?g|gif|svg|webp|ico|woff2?|ttf|xml|txt|json|pdf|mp4|mp3|map|php|webmanifest|avif|gz|zip)$/) next;
  if (u ~ /^\/(wp-|\.well-known|cgi-bin|marketing\/|ir\/)/) next;
  m = (index("JanFebMarAprMayJunJulAugSepOctNovDec", t[3]) + 2) / 3;
  printf "%s-%02d-%02d\t%s\t%s\t%s%s\n", t[4], m, t[2], DOM, u, $1, ua }'''.replace('BOTS', BOTS)
AWK2 = r'''BEGIN { FS = "\t" } { k = $1 FS $2 FS $3; v[k]++; u = $1 FS $2 FS $4; if (!(u in s)) { s[u] = 1; uv[$1 FS $2]++ } }
  END { for (k in v) print "P" FS k FS v[k]; for (k in uv) print "U" FS k FS uv[k] }'''

def visitas():
    # localizar los registros: SiteGround los deja en www/<dominio>/logs/ (si el registro de accesos está activado)
    lista = remoto('for d in ' + ' '.join(DOMINIOS) + '; do for f in $(find www/$d/logs logs/$d -maxdepth 1 -type f -mtime -31 2>/dev/null); do echo "$d $f"; done; done')
    archivos = [l.split(' ', 1) for l in lista.splitlines() if ' ' in l]
    P['registros'] = len(archivos)
    if not archivos:
        P['avisos'].append('No se encontraron registros de acceso en el servidor. Actívalos en Site Tools > Estadísticas > Registro de accesos para ver visitas y páginas.')
        print('sin registros:', remoto('ls -la www/aurzane.com/ logs 2>&1 | head -40')[:1500])
        return
    por_dom = collections.defaultdict(list)
    for d, f in archivos: por_dom[d].append(f)
    dia_vis = collections.Counter(); dia_pag = collections.Counter(); paginas = collections.Counter(); paginas7 = collections.Counter(); dom_vis = collections.Counter()
    hace7 = (HOY - datetime.timedelta(days=7)).isoformat()
    for d, fs in por_dom.items():
        guion = ("cat > /tmp/az1.awk <<'FIN1'\n" + AWK1.replace('DOM', '"' + d + '"') + "\nFIN1\ncat > /tmp/az2.awk <<'FIN2'\n" + AWK2 + "\nFIN2\n"
                 "for f in " + ' '.join(fs) + "; do case $f in *.gz) zcat $f;; *) cat $f;; esac; done | awk -f /tmp/az1.awk | awk -f /tmp/az2.awk\nrm -f /tmp/az1.awk /tmp/az2.awk\n")
        for l in remoto('bash -s', 600, guion).splitlines():
            c = l.split('\t')
            if c[0] == 'P' and len(c) == 5:
                dia, dom, u, n = c[1], c[2], c[3], int(c[4])
                dia_pag[dia] += n; paginas[dom + u] += n
                if dia >= hace7: paginas7[dom + u] += n
            elif c[0] == 'U' and len(c) == 4:
                dia_vis[c[1]] += int(c[3]); dom_vis[c[2]] += int(c[3])
    dias = sorted(dia_vis)[-30:]
    P['visitas'] = {
        'por_dia': [{'dia': x, 'visitantes': dia_vis[x], 'paginas': dia_pag[x]} for x in dias],
        'por_dominio': dom_vis.most_common(),
        'top_30_dias': paginas.most_common(25),
        'top_7_dias': paginas7.most_common(15),
    }

# ---------------------------------------------------------------- boletín
def boletin():
    out = {}
    for k in ['suscritos', 'pendientes']:
        t = remoto(f'cat www/aurzane.com/privado-boletin/{k}.json 2>/dev/null')
        try:
            j = json.loads(t) if t.strip() else []
            out[k] = len(j)
            if k == 'suscritos':   # altas por mes, sin guardar ningún correo
                fechas = [str((v if isinstance(v, dict) else {}).get('fecha') or (v if isinstance(v, dict) else {}).get('alta') or '')[:7] for v in (j.values() if isinstance(j, dict) else j)]
                out['altas_por_mes'] = sorted(collections.Counter(f for f in fechas if f).items())[-12:]
        except Exception as e: out[k] = None; print('boletin', k, e)
    P['boletin'] = out

# ---------------------------------------------------------------- clics de compra y ventas
def compras():
    t = remoto('cat www/aurzane.com/privado-ai/clics-compra.log 2>/dev/null')
    hace30 = (HOY - datetime.timedelta(days=30)).isoformat()
    por_tienda = collections.Counter(); por_pag = collections.Counter(); por_dia = collections.Counter()
    for l in t.splitlines():
        c = l.split('\t')
        if len(c) < 3 or c[0] < hace30: continue
        por_tienda[c[1]] += 1; por_pag[c[2]] += 1; por_dia[c[0]] += 1
    AF = leer('tienda/afiliados.json', {}).get('programas', {})
    nombre = lambda k: 'Amazon' if k == 'amazon' else (AF.get(k[5:], {}).get('nombre', 'Awin ' + k[5:]) if k.startswith('awin-') else k)
    P['clics_compra'] = {'total_30_dias': sum(por_tienda.values()), 'por_tienda': [(nombre(k), v) for k, v in por_tienda.most_common()],
                         'paginas': por_pag.most_common(12), 'por_dia': sorted(por_dia.items())}
    tk = os.environ.get('AWIN_TOKEN', '').strip(); pid = leer('tienda/afiliados.json', {}).get('awin_publicador')
    if tk and pid:
        ini = (HOY - datetime.timedelta(days=30)).isoformat() + 'T00:00:00'; fin = HOY.isoformat() + 'T23:59:59'
        try:
            rq = urllib.request.Request(f'https://api.awin.com/publishers/{pid}/transactions/?startDate={ini}&endDate={fin}&timezone=UTC', headers={'Authorization': 'Bearer ' + tk})
            tr = json.load(urllib.request.urlopen(rq, timeout=60))
            ventas = collections.defaultdict(lambda: {'ventas': 0, 'importe': 0.0, 'comision': 0.0, 'moneda': ''})
            for x in tr:
                v = ventas[x.get('advertiserName') or str(x.get('advertiserId'))]
                v['ventas'] += 1; v['importe'] += float((x.get('saleAmount') or {}).get('amount') or 0); v['comision'] += float((x.get('commissionAmount') or {}).get('amount') or 0)
                v['moneda'] = (x.get('commissionAmount') or {}).get('currency') or v['moneda']
            P['awin'] = {'ventas_30_dias': sum(v['ventas'] for v in ventas.values()), 'comision_30_dias': round(sum(v['comision'] for v in ventas.values()), 2),
                         'por_tienda': sorted(([k, v['ventas'], round(v['comision'], 2), v['moneda']] for k, v in ventas.items()), key=lambda z: -z[2])}
        except Exception as e: P['awin'] = {'error': str(e)[:200]}; print('awin', e)
        try:
            rq = urllib.request.Request(f'https://api.awin.com/publishers/{pid}/programmes?relationship=joined', headers={'Authorization': 'Bearer ' + tk})
            P.setdefault('awin', {})['programas_activos'] = len(json.load(urllib.request.urlopen(rq, timeout=60)))
        except Exception as e: print('awin programas', e)
    else: P['awin'] = {'error': 'Falta AWIN_TOKEN'}
    P['amazon'] = {'nota': 'Amazon no permite leer las ventas por API sin ventas previas: consúltalas en afiliados.amazon.es. Aquí ves los clics que salen hacia Amazon.'}

# ---------------------------------------------------------------- redes
def redes():
    seg = leer('marketing/seguidores.json', {})
    dias = sorted(seg)
    act = seg[dias[-1]] if dias else {}
    prev = next((seg[d] for d in reversed(dias) if d <= (HOY - datetime.timedelta(days=30)).isoformat()), seg[dias[0]] if dias else {})
    P['seguidores'] = {'fecha': dias[-1] if dias else None, 'redes': [[r, v, (v - prev.get(r)) if isinstance(v, int) and isinstance(prev.get(r), int) else None] for r, v in sorted(act.items(), key=lambda z: -(z[1] or 0))]}
    hace30 = (HOY - datetime.timedelta(days=30)).isoformat(); por_red = collections.Counter(); por_prod = collections.Counter()
    try:
        for f in csv.DictReader(open(os.path.join(R, 'marketing/clics.csv'), encoding='utf-8')):
            if f['fecha'] >= hace30: por_red[f['red']] += int(f['clics']); por_prod[f['producto']] += int(f['clics'])
    except Exception as e: print('clics', e)
    P['clics_redes'] = {'total_30_dias': sum(por_red.values()), 'por_red': por_red.most_common(), 'contenidos': por_prod.most_common(10)}
    tg = leer('marketing/telegram_libros.json', {})
    P['telegram_libros'] = len(tg.get('enviados', []))

# ---------------------------------------------------------------- contenido y colegios
def contenido():
    try: P['tienda_libros'] = len(json.loads(remoto('cat www/aurzane.com/public_html/libros/libros.json 2>/dev/null') or '[]'))
    except Exception: P['tienda_libros'] = None
    t = remoto('cat www/aurzane.com/privado-colegios/solicitudes.json 2>/dev/null')
    try:
        s = json.loads(t) if t.strip() else []
        P['colegios'] = {'solicitudes': len(s), 'nuevas': sum(1 for x in s if x.get('estado') == 'nueva'),
                         'ultimas': [[x.get('fecha', '')[:10], x.get('colegio', ''), x.get('ciudad', ''), x.get('cargo', '')] for x in s[-8:]][::-1]}
    except Exception as e: P['colegios'] = {'solicitudes': None}; print('colegios', e)
    ia = remoto('cat www/aurzane.com/privado-ai/estado.json 2>/dev/null')
    try:
        j = json.loads(ia); P['ia'] = {k: j.get(k) for k in ['fecha', 'resumen'] if k in j}
    except Exception: pass


for paso in (visitas, boletin, compras, redes, contenido):
    try: paso()
    except Exception as e: P['avisos'].append(f'{paso.__name__}: {str(e)[:160]}'); print('ERROR', paso.__name__, e)

open('/tmp/panel.json', 'w', encoding='utf-8').write(json.dumps(P, ensure_ascii=False))
resumen = {k: (v if not isinstance(v, (dict, list)) else '…') for k, v in P.items()}
print(json.dumps(resumen, ensure_ascii=False))
if P.get('visitas'): print('visitantes últimos días:', P['visitas']['por_dia'][-3:])
