"""Foto principal de la portada servida desde aurzane.com (17/11/2026, etapa 2, tarea 27: LCP de la portada).
La foto (Unsplash, licencia Unsplash) se pedía a images.unsplash.com: en móvil, abrir conexión con otro dominio
retrasaba la imagen más grande de la portada. Este parche guarda en aurzane.com/img/hero/ la misma foto en AVIF y WebP y en
los cuatro anchos que usa la portada (600, 900, 1400 y 2200 px). Solo descarga lo que falta. Si una descarga falla,
el archivo parcial se aparta a eliminar (nunca se borra)."""
import os, sys, shutil, subprocess, datetime
base = os.path.expanduser('~/' + (sys.argv[1] if len(sys.argv) > 1 else 'www'))
FOTOS = ['1508672019048-805c876b67e2']
dst = os.path.join(base, 'aurzane.com', 'public_html', 'img', 'hero'); os.makedirs(dst, exist_ok=True)
for fid in FOTOS:
    for w, fm, q in [(w, fm, q) for w in (600, 900, 1400, 2200) for fm, q in (('avif', 45), ('webp', 55))]:
        f = os.path.join(dst, f'{fid}-{w}-q{q}.{fm}')
        if os.path.exists(f) and os.path.getsize(f) > 3000: continue
        u = f'https://images.unsplash.com/photo-{fid}?w={w}&q={q}&fm={fm}&fit=crop'
        r = subprocess.run(['curl', '-sL', '-m', '60', '-o', f, '-w', '%{http_code}', u], capture_output=True, text=True)
        if r.stdout.strip() == '200' and os.path.getsize(f) > 3000: print('foto guardada', os.path.basename(f), os.path.getsize(f) // 1024, 'KB')
        elif os.path.exists(f):
            c = os.path.join(base, 'aurzane.com', 'eliminar', 'hero-' + datetime.date.today().isoformat()); os.makedirs(c, exist_ok=True)
            shutil.move(f, os.path.join(c, os.path.basename(f))); print('::warning::descarga fallida', u)
