import ast, os, sys, json, re
ROOT = sys.argv[1]  # apps/api/plane
out = []

def src(node): return ast.unparse(node)

# 1. collect all classes in views
classes = {}  # name -> info
for base in ["app/views", "space/views", "api/views", "license/api/views"]:
    for dp, dn, fn in os.walk(os.path.join(ROOT, base)):
        for f in fn:
            if not f.endswith(".py"): continue
            p = os.path.join(dp, f)
            tree = ast.parse(open(p).read())
            for node in tree.body:
                if isinstance(node, ast.ClassDef):
                    info = {"file": os.path.relpath(p, ROOT), "bases": [src(b) for b in node.bases],
                            "perm_classes": None, "auth_classes": None, "methods": {}, "get_permissions": False, "line": node.lineno}
                    for b in node.body:
                        if isinstance(b, ast.Assign):
                            for t in b.targets:
                                if isinstance(t, ast.Name) and t.id == "permission_classes":
                                    info["perm_classes"] = src(b.value)
                                if isinstance(t, ast.Name) and t.id == "authentication_classes":
                                    info["auth_classes"] = src(b.value)
                        if isinstance(b, ast.FunctionDef):
                            if b.name == "get_permissions": info["get_permissions"] = src(b)
                            decs = []
                            for d in b.decorator_list:
                                s = src(d)
                                if "allow_permission" in s or "permission" in s.lower():
                                    decs.append(s)
                            info["methods"][b.name] = {"decs": decs, "line": b.lineno}
                    key = (base.split("/")[0], node.name)
                    classes[key] = info
                    classes.setdefault(("any", node.name), info)

def resolve(cls_name, area, attr):
    seen = 0
    k = (area, cls_name) if (area, cls_name) in classes else ("any", cls_name)
    while k in classes and seen < 10:
        info = classes[k]
        if info[attr] is not None: return info[attr], k[1]
        if not info["bases"]: break
        b = info["bases"][0].split(".")[-1]
        k = (area, b) if (area, b) in classes else ("any", b)
        seen += 1
    return None, None

def method_dec(cls_name, area, mname):
    k = (area, cls_name) if (area, cls_name) in classes else ("any", cls_name)
    seen=0
    while k in classes and seen < 10:
        info = classes[k]
        if mname in info["methods"]:
            return info["methods"][mname]["decs"], k[1], info["methods"][mname]["line"], info["file"]
        if not info["bases"]: break
        b = info["bases"][0].split(".")[-1]
        k = (area, b) if (area, b) in classes else ("any", b)
        seen+=1
    return None, None, None, None

def walk_urls(urlfile, prefix, area):
    tree = ast.parse(open(urlfile).read())
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and getattr(node.func, "id", None) in ("path", "re_path"):
            if len(node.args) < 2: continue
            route = node.args[0].value if isinstance(node.args[0], ast.Constant) else src(node.args[0])
            v = node.args[1]
            if isinstance(v, ast.Call) and isinstance(v.func, ast.Attribute) and v.func.attr == "as_view":
                cname = src(v.func.value).split(".")[-1]
                mapping = {}
                if v.args and isinstance(v.args[0], ast.Dict):
                    for kk, vv in zip(v.args[0].keys, v.args[0].values):
                        mapping[kk.value] = vv.value
                else:
                    k = (area, cname) if (area, cname) in classes else ("any", cname)
                    if k in classes:
                        for m in ["get","post","put","patch","delete"]:
                            d,_,_,_ = method_dec(cname, area, m)
                            if d is not None: mapping[m]=m
                pc, pcfrom = resolve(cname, area, "perm_classes")
                k = (area, cname) if (area, cname) in classes else ("any", cname)
                gp = classes[k]["get_permissions"] if k in classes else False
                for http, action in mapping.items():
                    decs, defcls, line, file = method_dec(cname, area, action)
                    out.append({"area": area, "route": prefix + route, "http": http.upper(), "class": cname, "action": action,
                                "file": file or (classes[k]["file"] if k in classes else "?"), "line": line,
                                "perm_classes": pc, "perm_from": pcfrom, "decorators": decs or [], "get_permissions": bool(gp)})

for area, d, prefix in [("app","app/urls","/api/"),("space","space/urls","/api/public/"),("api","api/urls","/api/v1/")]:
    for f in sorted(os.listdir(os.path.join(ROOT,d))):
        if f.endswith(".py"): walk_urls(os.path.join(ROOT,d,f), prefix, area)
walk_urls(os.path.join(ROOT,"license/urls.py"), "/api/instances/", "license")
json.dump(out, open(sys.argv[2],"w"), indent=1)
print(len(out))
