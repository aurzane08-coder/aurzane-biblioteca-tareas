import re,hashlib,sys
def norm(s):
    s=re.sub(r'<meta property="og:image" content="[^"]*"><meta property="og:image:width"[^\n]*\n</head>','</head>',s)
    s=re.sub(r'<title>[^<]*</title>','',s); s=re.sub(r'<meta property="og:title" content="[^"]*">','',s)
    return hashlib.md5(s.encode()).hexdigest()
for f in sys.argv[1:]: print(norm(open(f,encoding='utf-8').read()), f)
