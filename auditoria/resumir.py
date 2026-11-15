import json,glob,collections,sys
def cargar(n):
    r=[]
    for f in sorted(glob.glob(f'auditoria/{n}/informe-*.json')): r+=json.load(open(f))
    return [p for p in r if not p['url'].endswith(('.js','.css'))]
def res(r):
    des=collections.Counter(); axn=collections.Counter(); tipos=set(); err=0; rot=0; pag=0; malos=[]; axe_det=collections.Counter()
    for p in r:
        A=p['anchos']; o=[w for w,a in A.items() if a.get('desborda')]
        if o: pag+=1; malos.append((p['url'],o,A[o[0]].get('culpables',[])[:3]))
        for w,a in A.items():
            if a.get('desborda'): des[w]+=1
            for v in a.get('axe',[]): axn[v['id']]+=v['n']; axe_det[(v['id'],p['url'][8:60],v.get('ejemplo','')[:50])]+=v['n']
            err+=len([e for e in a.get('errores',[]) if 'ds.css' not in e and 'ERR_FAILED' not in e]); rot+=len(a.get('rotos',[]))
    return dict(paginas=len(r),con_desborde=pag,desborde=dict(des),axe=dict(axn),axe_total=sum(axn.values()),errores=err,rotos=rot),malos,axe_det
for n in sys.argv[1:]:
    a,m,d=res(cargar(n)); print(n,json.dumps(a,ensure_ascii=False))
    if n==sys.argv[-1]:
        for x in m: print('  OVF',x)
        for k,v in d.most_common(30): print('  AXE',v,k)
