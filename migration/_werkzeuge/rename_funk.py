import re,glob,sys,collections
root=sys.argv[1]
files=[f for f in sorted(glob.glob(root+'/architecture/*.md')+glob.glob(root+'/plan/*.md')+glob.glob(root+'/architecture/_data/*.json')+glob.glob(root+'/plan/_data/*.json')+glob.glob(root+'/_werkzeuge/plan/*.py')+glob.glob(root+'/_werkzeuge/permission-matrix/*.py'))
       if not re.search(r'/(00-grundsatz|17-abgleich)',f) and '17-abgleich' not in f]
ORIG_TYPES={'PlaneLogo','PlaneLockup','PlaneToastProvider'}
ORIG_NPM={'editor','blocks','types','constants','utils','propel','services','tailwind-config','shared-state','hooks','decorators','logger','typescript-config','i18n'}
IND=re.compile(r'Original|original|apps/|packages/|\.py\b|Django|Celery|makeplane|053b2c0')
safe=[(re.compile(r'\bPlane\.(?=[A-Z])'),'Funk.'),
      (re.compile(r'\bPlane(?=[A-Z][A-Za-z0-9]+)(?!Logo\b|Lockup\b|ToastProvider\b)'),'Funk'),
      (re.compile(r'\bPlane:(?=[A-Z])'),'Funk:'),(re.compile(r'\bPlane__'),'Funk__'),
      (re.compile(r'\bPLANE(?=0\d)'),'FUNK'),
      (re.compile(r'\bplane\.(?=[a-z_]+\.[a-z_]+\.v\d)'),'funk.'),
      (re.compile(r'(?<![\w/-])plane-(?=(web|admin|space|backend|forgejo|instance-admin)\b)'),'funk-')]
amb=[(re.compile(r'\bPLANE_(?=[A-Z])'),'FUNK_'),(re.compile(r'X-Plane-'),'X-Funk-'),(re.compile(r'\bplane_(?=(api|wh)_)'),'funk_'),
     (re.compile(r'(?i)(realm\W{0,3}`?)plane(`)'),r'\1funk\2')]
npm=re.compile(r'@plane/([a-z-]+)')
stats=collections.Counter(); skipped=collections.Counter()
for f in files:
    lines=open(f,encoding='utf-8').read().split('\n'); out=[]
    for l in lines:
        o=l
        for p,r in safe:
            l,n=p.subn(r,l); stats[p.pattern[:20]]+=n
        orig_line=bool(IND.search(o))
        for p,r in amb:
            if orig_line: skipped[p.pattern[:20]]+=len(p.findall(l))
            else:
                l,n=p.subn(r,l); stats[p.pattern[:20]]+=n
        def nrep(m):
            name=m.group(1)
            if name in ORIG_NPM and orig_line:
                skipped['@plane/']+=1; return m.group(0)
            stats['@plane/']+=1; return '@funk/'+name
        l=npm.sub(nrep,l)
        out.append(l)
    open(f,'w',encoding='utf-8').write('\n'.join(out))
print('files',len(files)); print('replaced',dict(stats)); print('skipped(original context)',dict(skipped))
