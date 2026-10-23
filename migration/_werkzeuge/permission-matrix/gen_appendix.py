import json, re, sys, collections
d = json.load(open(sys.argv[1], encoding='utf-8'))
cat = {c['key']: c for c in d['catalog']}
LV = {"WS":"Workspace","PRJ":"Projekt","ANON":"anonym","AUTH":"angemeldet","INST":"Instanz","WSA|PA":"Workspace/Projekt"}
out = []
out.append("## Anhang A – Permission-Katalog (vollständig, 258 Keys)\n")
out.append("Erzeugt aus `migration/architecture/_data/05-permission-matrix.json` (Feld `catalog`). Spalten Admin/Member/Guest = Grant der System-Rolle (Workspace- bzw. Projektrolle je nach Ebene); „Regeln“ = an wie vielen Endpunkten des Keys die Regel zusätzlich deklariert ist (Notation §3.13.2); „API-Scope (H1)“ = reservierter Scope-Name für Bearer-Tokens (§6.4). Die C#-Konstanten erzeugt `tools/Funk.PermissionGen` (§5.8).\n")
out.append("| # | Permission-Key | C#-Konstante | Ebene | Admin (20) | Member (15) | Guest (5) | Regeln an Endpunkten (Anzahl) | Endpunkte | API-Scope (H1) |")
out.append("|---|---|---|---|---|---|---|---|---|---|")
for i, c in enumerate(d['catalog'], 1):
    lvl, rl = c['level'], c['roles'] or ""
    if lvl in ("WS","PRJ"):
        a,m,g = ["✓" if x in rl.split(",") else "–" for x in "AMG"]
    elif lvl == "WSA|PA":
        a,m,g = "✓ (WS-Admin oder Projekt-Admin)","–","–"
    else:
        a=m=g={"ANON":"jeder (auch anonym)","AUTH":"jeder Angemeldete","INST":"nur Instanz-Admin"}[lvl]
    rules = ", ".join(f"`{r}`×{n}" for r,n in sorted(c['rules'].items())) or "–"
    out.append(f"| {i} | `{c['key']}` | `{c['constant']}` | {LV[lvl]} | {a} | {m} | {g} | {rules} | {c['endpoints']} | `{c['api_scope']}` |")
out.append("")

def short(route):
    r = route.replace("/api/workspaces/<str:slug>/projects/<uuid:project_id>", "{P}").replace("/api/workspaces/<str:slug>","{W}")
    r = r.replace("/api/v1/workspaces/<str:slug>/projects/<uuid:project_id>","{V1P}").replace("/api/v1/workspaces/<str:slug>","{V1W}")
    r = r.replace("/api/public/anchor/<str:anchor>","{SP}")
    r = re.sub(r"<(uuid|str|int):(\w+)>", r"{\2}", r)
    return r
DROPMOD = {"CycleViewSet":"Cycles","IssueViewSet":"WorkItems","IssueCommentViewSet":"WorkItems","ModuleViewSet":"ProjectModules",
           "ProjectViewSet":"Projects","IssueViewViewSet":"Views","WorkspaceViewViewSet":"Views","WorkSpaceViewSet":"Workspaces",
           "CycleIssueViewSet":"Cycles","ModuleIssueViewSet":"ProjectModules","ProjectFavoritesViewSet":"Workspaces"}
def module(e):
    if e['permission']: return cat[e['permission']]['module']
    if e['area']=="license": return "Instance"
    if e['path'].startswith("/api/users/"): return "Identity"
    return DROPMOD.get(e['class'], "?")
order = ["Identity","Instance","Workspaces","Projects","WorkItems","Cycles","ProjectModules","Intake","Pages","Views","Assets","Analytics","Home","Notifications","Search","PublicSpace","Webhooks","Exports","Assistant"]
groups = collections.OrderedDict((m, []) for m in order)
for e in d['endpoints']:
    groups.setdefault(module(e), []).append(e)
assert "?" not in groups or not groups["?"], [ (e['class'],e['path']) for e in groups.get("?",[])]
out.append("## Anhang B – Endpunkt-×-Rollen-Matrix (vollständig, 672 Endpunkt-Methoden)\n")
out.append("Erzeugt aus `migration/architecture/_data/05-permission-matrix.json` (Feld `endpoints`), gruppiert nach Eigentümer-Modul (`01` §5.4). Pfad-Kürzel: `{W}` = `/api/workspaces/{slug}`, `{P}` = `{W}/projects/{project_id}`, `{V1W}` = `/api/v1/workspaces/{slug}`, `{V1P}` = `{V1W}/projects/{project_id}`, `{SP}` = `/api/public/anchor/{anchor}`. Datei-Kürzel: `V/` = `app/views/`, `V1V/` = `api/views/`, `SPV/` = `space/views/`, `LICV/` = `license/api/views/` (relativ zu `apps/api/plane/`).\n")
out.append("**Spalten:** „Original-Prüfung“ = wirksame Prüfung im Original (`WS(…)`/`PRJ(…)` = Permission-Klasse → `DenyStyle.Detail`; `PRJ⁺(…)` = `allow_permission` mit WS-Admin-Override bzw. `… ∨ Creator(Model)` = `allow_permission(creator=True)` → `DenyStyle.Error`; `Auth` = nur angemeldet; `Anon` = `AllowAny`; `INST` = `InstanceAdminPermission`). „Ziel-Prüfung“ = Notation §3.13.2. „Abw.“ = Korrektur-/Harmonisierungs-ID (§3.18) bzw. `ADR-008`.\n")
cnt = 0
for m, lst in groups.items():
    if not lst: continue
    out.append(f"\n### B.{m} ({len(lst)} Endpunkt-Methoden)\n")
    out.append("| Methode | Pfad | Original (Klasse.Aktion, Datei) | Original-Prüfung | Ziel-Permission | Ziel-Prüfung | Abw. |")
    out.append("|---|---|---|---|---|---|---|")
    for e in sorted(lst, key=lambda e:(e['area'], short(e['path']), e['method'])):
        cnt += 1
        f = e['file'].replace("apps/api/plane/","").replace("app/views/","V/").replace("api/views/","V1V/").replace("space/views/","SPV/").replace("license/api/views/","LICV/")
        line = f":{e['line']}" if e.get('line') else ""
        tgt = "—" if e['permission'] is None else f"`{e['permission']}`"
        tp = "**entfällt**" if e['target']=="entfällt" else f"`{e['target']}`"
        orig = e['original_check'].replace("PRJ+","PRJ⁺").replace("|","\\|")
        tp = tp.replace("WSA|PA","WSA\\|PA")
        dev = (e['deviation'] or "").replace("|","\\|")
        out.append(f"| {e['method']} | `{short(e['path'])}` | `{e['class']}.{e['action']}` ({f}{line}) | `{orig}` | {tgt} | {tp} | {dev} |")
out.append("")
print(f"catalog {len(d['catalog'])} endpoints {cnt}", file=sys.stderr)
open(sys.argv[2],"w",encoding='utf-8').write("\n".join(out)+"\n")
