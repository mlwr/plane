import json,sys
f=sys.argv[1]
d=json.load(open(f))
tag=f.split('.')[0]
for i,x in enumerate(d):
    print(f"[{tag}#{i}] ({x.get('area')}) {x['name']}\n  D: {x['description']}\n  R: {'; '.join(x.get('code_refs',[]))}")
