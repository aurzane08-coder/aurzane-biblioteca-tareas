"""Busca en Awin programas útiles para AURZANE (cursos, idiomas, libros, bienestar) que todavía no están unidos."""
import json, os, urllib.request
tk = os.environ['AWIN_TOKEN']; pid = 3149553
CLAVES = ['edx', 'coursera', 'udemy', 'domestika', 'babbel', 'busuu', 'preply', 'lingoda', 'skillshare', 'masterclass', 'udacity', 'linkedin',
          'emagister', 'campus', 'escuela', 'academy', 'academia', 'curso', 'course', 'learning', 'school', 'universi', 'educa', 'study', 'language',
          'libro', 'book', 'storytel', 'audible', 'kobo', 'nubico', 'bookbeo', 'mindful', 'calm', 'headspace', 'yoga', 'meditat', 'sleep', 'psicolog',
          'therapy', 'terapia', 'student', 'estudiant', 'notebook', 'papeler', 'office', 'lamy', 'moleskine']
out = []
for rel in ('notjoined', 'pending', 'joined', 'rejected'):
    rq = urllib.request.Request(f'https://api.awin.com/publishers/{pid}/programmes?relationship={rel}', headers={'Authorization': 'Bearer ' + tk})
    try: L = json.load(urllib.request.urlopen(rq, timeout=120))
    except Exception as e: print(rel, e); continue
    print(rel, len(L))
    for p in L:
        n = (p.get('name') or '').lower()
        if any(k in n for k in CLAVES):
            out.append((rel, p.get('id'), p.get('name'), (p.get('primaryRegion') or {}).get('countryCode'), p.get('displayUrl')))
for o in sorted(out): print(*o, sep=' | ')
