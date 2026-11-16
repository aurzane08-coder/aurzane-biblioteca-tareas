# Quita el nombre y el número de registro del titular de las páginas públicas del ecosistema.
# Se mantiene solo donde la ley lo exige (aviso legal y política de privacidad) y en documentos firmados
# que no son páginas públicas (certificados de LEARN, informes y generador de informes de OVP).
# Corre en el servidor cada día y en cada cambio de este archivo, así las páginas que se regeneren
# tampoco lo recuperan. Copia previa en <web>/eliminar/nombre-FECHA/. Uso: python3 - www < nombre.py
import os, re, sys, shutil, datetime
base = sys.argv[1]; hoy = datetime.datetime.now().strftime('%Y%m%d-%H%M')
WEBS = ['aurzane.com', 'mind.aurzane.com', 'nexus.aurzane.com', 'live.aurzane.com', 'learn.aurzane.com', 'build.aurzane.com', 'ovp.aurzane.com']
EXCLUIR = re.compile(r'^(aviso-legal\.html|privacidad\.html|certificado/|informe[a-z0-9-]*\.js|generar-informe\.html|admin[a-z-]*\.html|portal-cliente|eliminar/|wp-)')
NOM = r'(?:Psi\. ?Cl\. )?Adri[aá]n(?: Mauricio)? S[aá]nchez Samaniego'
REG = r'\s*\(?(?:[Rr]egistro )?SENESCYT N\.º ?[\d-]+\)?'
R = [
    (r',\s*"founder":\s*\{"@type":\s*"Person",\s*"name":\s*"' + NOM + r'"[^}]*\}', ''),
    (r'<img[^>]*alt="Firma de ' + NOM + r'"[^>]*>', ''),
    (r'\s*·\s*' + NOM + r'\s*·' + REG + r'\s*·', ' ·'),
    (r'(?:<strong>|<b>)' + NOM + r'(?:</strong>|</b>)(?:, psicólogo clínico)?,?' + '(?:' + REG + ')?' + r',?', '<strong>un psicólogo clínico titulado</strong>'),
    (NOM + r', psicólogo clínico' + '(?:' + REG + ')?' + r',?', 'un psicólogo clínico titulado'),
    (r' \(' + NOM + r'\)', ''),
]
CAP = [(r'(<p>|<li>|\. )(<strong>)?un psicólogo', lambda m: m.group(1) + (m.group(2) or '') + 'Un psicólogo'),
       (r'(summary><p>)un ', r'\1Un ')]
n, quedan = 0, []
for web in WEBS:
    raiz = os.path.join(base, web, 'public_html')
    if not os.path.isdir(raiz): continue
    for dp, dn, fn in os.walk(raiz):
        rd = os.path.relpath(dp, raiz)
        dn[:] = [x for x in dn if not EXCLUIR.match(os.path.normpath(os.path.join(rd, x)) + '/')]
        for f in fn:
            if not f.endswith(('.html', '.js')): continue
            rel = os.path.normpath(os.path.join(rd, f))
            if EXCLUIR.match(rel): continue
            p = os.path.join(raiz, rel)
            try: s = open(p, encoding='utf-8').read()
            except Exception: continue
            if 'Samaniego' not in s: continue
            t = s
            for a, b in R: t = re.sub(a, b, t)
            for a, b in CAP: t = re.sub(a, b, t)
            if re.search(r'S[aá]nchez Samaniego', t): quedan.append(web + '/' + rel)
            if t != s:
                c = os.path.join(base, web, 'eliminar', 'nombre-' + hoy, os.path.dirname(rel)); os.makedirs(c, exist_ok=True); shutil.copy2(p, c)
                open(p, 'w', encoding='utf-8').write(t); n += 1
print('páginas sin el nombre del titular:', n)
print('aún lo mencionan (revisar):', quedan[:40])
