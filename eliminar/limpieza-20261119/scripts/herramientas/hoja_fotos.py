# Descarga miniaturas de una lista de URLs y crea una hoja de contactos (para revisar fotos).
import sys, io, urllib.request
from PIL import Image, ImageDraw
urls=[l.strip() for l in open(sys.argv[1]) if l.strip() and not l.startswith('#')]
W,H,C=300,200,4
hoja=Image.new('RGB',(C*W,((len(urls)+C-1)//C)*(H+20)),'white');d=ImageDraw.Draw(hoja)
for k,u in enumerate(urls):
    x,y=(k%C)*W,(k//C)*(H+20)
    try:
        req=urllib.request.Request(u,headers={'User-Agent':'AURZANE-revision/1.0 (hola@aurzane.com)'})
        im=Image.open(io.BytesIO(urllib.request.urlopen(req,timeout=40).read())).convert('RGB');im.thumbnail((W,H));hoja.paste(im,(x,y))
    except Exception as e: d.text((x+5,y+5),'ERROR '+str(e)[:40],fill='red')
    d.text((x+4,y+H+4),str(k),fill='black')
hoja.save(sys.argv[2],quality=80);print('ok',len(urls))
