import json, re, sys, collections
out = json.load(open(sys.argv[1]))
DROP="entfällt"
MOD = {  # resource -> module (Contracts class prefix)
 "settings":"Workspaces","member":None,"invitation":None,"theme":"Workspaces","member_preference":None,"member_profile":"Workspaces",
 "project_metadata":"Workspaces","favorite":"Workspaces","draft_work_item":"WorkItems","quick_link":"Home","recent_visit":"Home","sticky":"Home",
 "webhook":"Webhooks","analytics":"Analytics","analytics_view":"Analytics","export":"Exports","asset":"Assets","asset_legacy":"Assets","view":"Views",
 "search":"Search","ai_assistant":"Assistant","notification":"Notifications","project":"Projects","publish":"PublicSpace","state":"Projects","label":"Projects",
 "estimate":"Projects","work_item":"WorkItems","work_item_link":"WorkItems","work_item_attachment":"WorkItems","work_item_activity":"WorkItems",
 "work_item_comment":"WorkItems","work_item_subscription":"WorkItems","reaction":"WorkItems","work_item_relation":"WorkItems","cycle":"Cycles",
 "cycle_work_item":"Cycles","module":"ProjectModules","module_link":"ProjectModules","module_work_item":"ProjectModules","intake":"Intake",
 "intake_work_item":"Intake","page":"Pages","page_version":"Pages","project_invitation":"Projects",
 "board":"PublicSpace","comment":"PublicSpace","vote":"PublicSpace","workspace_asset":"PublicSpace",
 "user":"Identity","session":"Identity","user_profile":"Identity","user_account":"Identity","user_activity":"Identity","api_token":"Identity",
 "user_asset":"Assets","notification_preference":"Notifications","timezone":"Identity","unsplash":"Assistant","workspace":"Workspaces",
 "admin":"Instance","auth_legacy":"Instance","configuration":"Instance","workspace":"Workspaces",
}
def module(key):
    sc,res,verb = key.split(".")
    if sc=="instance": return "Instance"
    if sc=="public":
        if res in ("reaction",): return "PublicSpace"
        if res=="intake": return "Intake"
        if res=="asset": return "Assets"
        if res=="invitation": return "Workspaces" 
        return "PublicSpace"
    if res=="member": return "Projects" if sc=="project" else "Workspaces"
    if res=="invitation": return "Projects" if sc=="project" else "Workspaces"
    if res=="member_preference": return "Projects" if sc=="project" else "Workspaces"
    if res=="favorite" and sc=="project": return "Workspaces"
    if res in ("cycle","module","view","page","project") and verb in ("favorite","read_favorites"): return "Workspaces"
    if res=="asset" and sc=="project": return "Assets"
    if res=="analytics" and sc=="project": return "Analytics"
    if res=="workspace" and sc=="user": return "Workspaces"
    if res=="invitation" and sc=="user": return "Workspaces"
    if res=="project_invitation": return "Projects"
    return MOD.get(res) or "?"
def pascal(s): return "".join(p.capitalize() for p in re.split(r"[._]", s))
def const(key):
    sc,res,verb = key.split(".")
    return f"{module(key)}Permissions.{pascal(sc)}{pascal(res)}{pascal(verb)}"
def apiscope(key):
    sc,res,verb=key.split(".")
    plur = {"project":"projects","workspace":"workspaces","user":"users","instance":"instance","public":"public"}[sc]
    rr = res if res.endswith("s") else (res[:-1]+"ies" if res.endswith("y") else res+"s")
    rw = "read" if verb.startswith("read") or verb in ("search",) else "write"
    return f"{plur}.{rr}:{rw}"
def roles_of(tg):
    m = re.match(r"(WS|PRJ|ANON|AUTH|INST|WSA\|PA)(?:\(([AMG,]+)\))?", tg)
    return m.group(1), (m.group(2) or "")
def rules_of(tg):
    return [x for x in tg.split("+")[1:]]

# catalog
cat = collections.OrderedDict()
for o in sorted(out, key=lambda o:o["pkey"]):
    if o["target"]==DROP: continue
    c = cat.setdefault(o["pkey"], {"lvl":None,"roles":None,"rules":collections.Counter(),"n":0,"ex":[]})
    lvl, rl = roles_of(o["target"])
    c["lvl"], c["roles"] = lvl, rl
    for x in rules_of(o["target"]): c["rules"][x]+=1
    c["n"]+=1
L=[]
L.append("| # | Permission-Key | C#-Konstante | Ebene | Admin (20) | Member (15) | Guest (5) | Regeln an Endpunkten (Anzahl) | Endpunkte | API-Scope (H1) |")
L.append("|---|---|---|---|---|---|---|---|---|---|")
LV = {"WS":"Workspace","PRJ":"Projekt","ANON":"anonym","AUTH":"angemeldet","INST":"Instanz","WSA|PA":"Workspace/Projekt"}
for i,(k,c) in enumerate(cat.items(),1):
    lvl, rl = c["lvl"], c["roles"]
    if lvl in ("WS","PRJ"):
        a,m,g = ["✓" if x in rl.split(",") else "–" for x in "AMG"]
    elif lvl=="WSA|PA":
        a,m,g = "✓ (WS-Admin oder Projekt-Admin)","–","–"
    else:
        a=m=g = {"ANON":"jeder (auch anonym)","AUTH":"jeder Angemeldete","INST":"nur Instanz-Admin"}[lvl]
    rules = ", ".join(f"`{r}`×{n}" for r,n in sorted(c["rules"].items())) or "–"
    L.append(f"| {i} | `{k}` | `{const(k)}` | {LV[lvl]} | {a} | {m} | {g} | {rules} | {c['n']} | `{apiscope(k)}` |")
open(sys.argv[2],"w").write("\n".join(L)+"\n")

# endpoint table grouped by module
def short(route):
    r = route.replace("/api/workspaces/<str:slug>/projects/<uuid:project_id>", "{P}").replace("/api/workspaces/<str:slug>","{W}")
    r = r.replace("/api/v1/workspaces/<str:slug>/projects/<uuid:project_id>","{V1P}").replace("/api/v1/workspaces/<str:slug>","{V1W}")
    r = r.replace("/api/public/anchor/<str:anchor>","{SP}")
    r = re.sub(r"<(uuid|str|int):(\w+)>", r"{\2}", r)
    return r
def orig(o):
    s = o["req"]
    return s.replace("PRJ+","PRJ⁺")
groups = collections.OrderedDict()
order = ["Identity","Instance","Workspaces","Projects","WorkItems","Cycles","ProjectModules","Intake","Pages","Views","Assets","Analytics","Home","Notifications","Search","PublicSpace","Webhooks","Exports","Assistant"]
for m in order: groups[m]=[]
for o in out:
    md = module(o["pkey"]) if o["target"]!=DROP else module(o["pkey"])
    groups.setdefault(md, []).append(o)
E=[]
cnt=0
for m, lst in groups.items():
    if not lst: continue
    E.append(f"\n#### {m} ({len(lst)} Endpunkt-Methoden)\n")
    E.append("| Methode | Pfad | Original (Klasse.Aktion, Datei) | Original-Prüfung | Ziel-Permission | Ziel-Prüfung | Abw. |")
    E.append("|---|---|---|---|---|---|---|")
    for o in sorted(lst, key=lambda o:(o["area"], short(o["route"]), o["http"])):
        cnt+=1
        f = o["file"].replace("app/views/","V/").replace("api/views/","V1V/").replace("space/views/","SPV/").replace("license/api/views/","LICV/")
        line = f":{o['line']}" if o.get("line") else ""
        tgt = "—" if o["target"]==DROP else f"`{o['pkey']}`"
        tp = "**entfällt**" if o["target"]==DROP else f"`{o['target']}`"
        E.append(f"| {o['http']} | `{short(o['route'])}` | `{o['class']}.{o['action']}` ({f}{line}) | `{orig(o)}` | {tgt} | {tp} | {o['dev'] or ''} |")
open(sys.argv[3],"w").write("\n".join(E)+"\n")
print("catalog", len(cat), "endpoints", cnt, "dropped", sum(1 for o in out if o["target"]==DROP), "unknown modules", [k for k in cat if module(k)=="?"])
# data file
data = {"generated_from":"Plane v1.4.2 CE (apps/api/plane/**/urls*.py, views, permissions) via AST-Extraktion",
        "legend":{"WS(x)":"aktives Workspace-Mitglied mit Rolle in x","PRJ(x)":"aktives Projektmitglied mit Rolle in x","O":"WsAdminOverride","C:<Model>":"CreatorBypass","OWN":"nur eigene Objekte","SELF":"nur eigener Datensatz","VIS":"Gast-Sichtbarkeit guest_view_all_features","PAGE":"Page-Zugriffsregel","BOARD":"Deploy-Board-Schalter","WSA|PA":"Workspace-Admin oder Projekt-Admin"},
        "catalog":[{"key":k,"constant":const(k),"level":c["lvl"],"roles":c["roles"],"rules":dict(c["rules"]),"endpoints":c["n"],"api_scope":apiscope(k),"module":module(k)} for k,c in cat.items()],
        "endpoints":[{"method":o["http"],"path":o["route"],"area":o["area"],"class":o["class"],"action":o["action"],"file":"apps/api/plane/"+o["file"],"line":o.get("line"),
                      "original_check":o["req"],"permission":None if o["target"]==DROP else o["pkey"],"target":o["target"],"deviation":o["dev"] or None} for o in out]}
json.dump(data, open(sys.argv[4],"w"), indent=1, ensure_ascii=False)
