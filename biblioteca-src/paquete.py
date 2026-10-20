# -*- coding: utf-8 -*-
"""Empaqueta archivos de texto del sitio en un JSON y lo deja en el tránsito de Supabase
(el navegador lo recoge desde SiteGround). Uso: python paquete.py nombre ruta1 ruta2 ..."""
import json, sys, urllib.request
KEY = 'sb_publishable___1v6VjDew0l8uGfMyb9Nw_YyCLTPPw'
SB = 'https://chtfpqwrrarfdjcivlad.supabase.co/storage/v1/object/biblioteca-transito/'
nombre, rutas = sys.argv[1], sys.argv[2:]
d = {r.split('/')[-1]: open(r, encoding='utf-8').read() for r in rutas}
req = urllib.request.Request(SB + 'paquetes/' + nombre + '.json', data=json.dumps(d, ensure_ascii=False).encode(), method='POST',
    headers={'apikey': KEY, 'authorization': 'Bearer ' + KEY, 'content-type': 'application/json'})
try: print(nombre, urllib.request.urlopen(req, timeout=120).status)
except urllib.error.HTTPError as e: print(nombre, e.code, e.read()[:200])
