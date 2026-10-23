import json, os, re, sys, collections
sys.path.insert(0, os.path.dirname(__file__))
from cat3 import C, EXCL
from overrides import SEC

ROOT = "/home/user/plane"
DATA = ROOT + "/migration/analysis/_data"
ANA = ROOT + "/migration/analysis"

DOCS = {
 "A01": "01-gesamtarchitektur-infrastruktur.md", "A02a": "02a-datenmodell-kern.md",
 "A02b": "02b-datenmodell-arbeitsobjekte.md", "A03": "03-api-intern-workspace-projekt-user.md",
 "A04": "04-api-intern-arbeitsobjekte.md", "A05": "05-api-public-v1-space-instanz.md",
 "A06": "06-auth-sicherheit-querschnitt.md", "A07": "07-hintergrundjobs-mail-storage-webhooks.md",
 "A08": "08-frontend-web-architektur.md", "A09": "09-frontend-arbeitsobjekte-layouts.md",
 "A10a": "10a-frontend-workspace-projekt-navigation.md", "A10b": "10b-frontend-cycles-modules-pages-views-weitere.md",
 "A11": "11-frontend-admin-space.md", "A12": "12-editor-echtzeit-live.md",
 "A13a": "13a-designsystem-ui-tokens.md", "A13b": "13b-shared-packages-i18n.md",
}
DOM = [
 ("WS", "Workspace & Mitglieder"), ("PRJ", "Projekte"), ("WI", "Work Items"),
 ("LV", "Layouts & Views"), ("CYC", "Cycles"), ("MOD", "Modules"), ("INT", "Intake"),
 ("PAGE", "Pages & Editor"), ("RT", "Realtime"), ("ANA", "Analytics"), ("HOME", "Home/Stickies"),
 ("NOTIF", "Notifications"), ("SRCH", "Suche/Power-K"), ("PROF", "Einstellungen/Profil"),
 ("AUTH", "Auth"), ("INST", "Instanz/God-Mode"), ("SPACE", "Public Space"), ("API", "Public API v1"),
 ("WH", "Webhooks/API-Tokens"), ("EXP", "Export"), ("AI", "Integrationen/AI"), ("I18N", "i18n/Theming"),
 ("UIX", "UI-Querschnitt (Zusatzdomäne)"), ("OPS", "Betrieb & Plattform (Zusatzdomäne)"),
]
DOMNAME = dict(DOM)

# ---- Quellen laden
SRC = {}
for tag in DOCS:
    fn = f"{DATA}/{tag}.features.json"
    for i, x in enumerate(json.load(open(fn))):
        SRC[f"{tag}#{i}"] = x
print("Quell-Einträge:", len(SRC))

# ---- Validierung
errors = []
used = collections.Counter()
for f in C:
    if f["d"] not in DOMNAME: errors.append(("domain", f["n"], f["d"]))
    for s in f["src"]:
        if s not in SRC: errors.append(("src", f["n"], s))
        used[s] += 1
excl_ids = set()
for e in EXCL:
    if e["src"] not in SRC: errors.append(("excl", e["src"]))
    excl_ids.add(e["src"])
both = [s for s in excl_ids if s in used]
missing = [s for s in SRC if s not in used and s not in excl_ids]
if errors: print("FEHLER", errors); sys.exit(1)
print("Doppelt (Katalog+Ausschluss):", both)
print("Nicht zugeordnet:", missing)
if missing or both: sys.exit(1)

# ---- Ref-Klassifikation
FRONT = ("apps/web", "apps/admin", "apps/space", "packages/", "@makeplane/propel", "pnpm-workspace.yaml")
def is_front(r): return r.startswith(FRONT)
def skip(r): return r.startswith("migration/")
REF_FIX = {"apps/web/hooks/use-intersection-observer.tsx": "apps/web/hooks/use-intersection-observer.ts",
           "apps/api/plane/permissions/page.py": "apps/api/plane/app/permissions/page.py"}

# ---- Abschnittssuche
GENERIC = {"base", "index", "root", "helper", "helpers", "utils", "types", "page", "layout", "modal", "form",
           "header", "common", "core", "constants", "issue", "project", "workspace", "user", "views", "urls",
           "models", "serializers", "settings", "store", "service", "services", "components", "app", "api",
           "admin", "space", "web", "live", "plane", "list", "block", "content", "title", "root.tsx", "auth"}
DOCTEXT = {}
def doc_sections(fn):
    if fn in DOCTEXT: return DOCTEXT[fn]
    lines = open(f"{ANA}/{fn}", encoding="utf-8").read().split("\n")
    secs = []; cur = None
    for ln in lines:
        m = re.match(r"^### (\d+\.\d+)\b", ln)
        if m: cur = m.group(1); secs.append([cur, []]); continue
        if re.match(r"^## ", ln): cur = None
        if cur is not None: secs[-1][1].append(ln)
    DOCTEXT[fn] = [(n, "\n".join(t)) for n, t in secs]
    return DOCTEXT[fn]
def tokens_for(entry):
    toks = set()
    for r in entry.get("code_refs", []):
        base = re.sub(r"\s*\(.*\)$", "", r).strip()
        for ident in re.findall(r"\(([^)]*)\)", r):
            for t in re.split(r"[,\s]+", ident):
                t = t.strip(" .")
                if len(t) >= 8 and re.match(r"^[A-Za-z_][\w.]*$", t): toks.add(t)
        base = re.sub(r":[\d,\-]+$", "", base)
        b = base.rstrip("/").split("/")[-1]
        stem = re.sub(r"\.(py|tsx|ts|js|json|css|md|html|yml|yaml|sh|conf)$", "", b)
        if len(stem) >= 6 and stem.lower() not in GENERIC and "{" not in stem: toks.add(b)
    return toks
BLACK = {
 "01-gesamtarchitektur-infrastruktur.md": {"2.2","2.3","2.4","2.5","2.11","2.27","2.29"},
 "02a-datenmodell-kern.md": {"2.2","2.13"},
 "02b-datenmodell-arbeitsobjekte.md": {"2.1","2.2","2.13"},
 "03-api-intern-workspace-projekt-user.md": {"2.12","2.13","2.15","2.16"},
 "04-api-intern-arbeitsobjekte.md": {"2.1","2.16","2.17","2.18","2.20"},
 "05-api-public-v1-space-instanz.md": {"2.3","2.4","2.5","2.9"},
 "07-hintergrundjobs-mail-storage-webhooks.md": {"2.4","2.18","2.19"},
 "10a-frontend-workspace-projekt-navigation.md": {"2.1","2.20","2.21"},
 "11-frontend-admin-space.md": {"2.3","2.17","2.27","2.29","2.30"},
 "12-editor-echtzeit-live.md": {"2.1","2.2","2.3"},
 "13a-designsystem-ui-tokens.md": {"2.1","2.30","2.32"},
}
SYN = {
 "benachrichtig": ["notification","benachrichtig","inbox"], "inbox": ["inbox","notification"], "notification": ["notification","benachrichtig"],
 "anhäng": ["attachment","anhang","anhäng"], "anhang": ["attachment","anhang"], "attachment": ["attachment","anhang"],
 "kommentar": ["kommentar","comment"], "comment": ["kommentar","comment"],
 "reaktion": ["reaktion","reaction"], "entwürf": ["draft","entwürf"], "draft": ["draft","entwürf"], "sub-work": ["sub-issue","sub-work"],
 "relation": ["relation"], "suche": ["suche","search"], "search": ["suche","search"], "zeitzon": ["timezone","zeitzon"], "timezone": ["timezone","zeitzon"],
 "passwor": ["passwor"], "einladu": ["einladung","invitation"], "mitglie": ["mitglied","member"], "member": ["mitglied","member"],
 "rollen": ["rollen","role"], "berechtig": ["berechtigung"],
 "favorit": ["favorit"], "stickie": ["stick"], "sticky": ["stick"], "webhook": ["webhook"], "export": ["export"],
 "analytics": ["analytic"], "estimat": ["estimate"], "schätz": ["estimate"], "labels": ["label"], "label": ["label"],
 "states": ["state"], "state": ["state"], "theme": ["theme"], "themes": ["theme"], "sprach": ["i18n"], "i18n": ["i18n"],
 "cycle": ["cycle"], "cycles": ["cycle"], "modul": ["modul"], "module": ["modul"], "modules": ["modul"],
 "intake": ["intake"], "pages": ["page"], "page": ["page"], "views": ["view"], "view": ["view"], "kanban": ["kanban"],
 "calendar": ["calendar","kalender"], "kalender": ["calendar","kalender"], "gantt": ["gantt","timeline"], "timeline": ["timeline","gantt"],
 "spreadsheet": ["spreadsheet"], "peek": ["peek"], "power-k": ["power-k"], "shortcut": ["tastatur"], "tastatur": ["tastatur"],
 "sidebar": ["sidebar"], "onboarding": ["onboarding"], "smtp": ["email/smtp","smtp"], "token": ["token","api-token"], "api-token": ["api-token"],
 "session": ["session"], "cookie": ["cookie"], "rate-limit": ["rate-limit","throttle"], "upload": ["upload"],
 "assets": ["asset"], "asset": ["asset"], "tabellen": ["tabellen"], "callout": ["callout"], "mention": ["mention"], "mentions": ["mention"],
 "emoji": ["emoji"], "emojis": ["emoji"], "links": ["link"], "link": ["link"], "markdown": ["markdown"], "platzhalter": ["platzhalter"],
 "outline": ["outline"], "pdf": ["pdf"], "kollaborativ": ["kollaboration"], "telemetrie": ["telemetrie"],
 "deployment": ["deployment"], "proxy": ["proxy"], "celery": ["celery"], "redis": ["redis"], "beat-jobs": ["beat-jobs"],
 "objektspeicher": ["objektspeicher"], "logging": ["logging"], "openapi": ["openapi"], "read-replica": ["read-replica"],
 "archiv": ["archiv"], "archivieren": ["archiv"], "auto-archive": ["automation"], "auto-close": ["automation"], "automation": ["automation"],
 "seed": ["seed"], "demo-workspace": ["seed"], "votes": ["vote","reaktionen & votes"], "oauth": ["oauth"], "magic-code": ["magic"],
 "icons": ["icon"], "icon-system": ["icon"], "typografie": ["typografie"], "schriften": ["schriften"], "animationen": ["animation"],
 "illustrationen": ["illustration"], "toast": ["toast"], "your": ["your work"], "quick-add": ["quick-add"], "quick-action": ["quick-action"],
 "empty-states": ["empty-state"], "skeleton": ["skeleton"], "dropdown": ["dropdown"], "rich-filter": ["rich-filter"], "display-filter": ["display-filter"],
 "breadcrumb": ["breadcrumb"], "redirect": ["redirect"], "legacy-redirects": ["routen"], "fehlerseite": ["fehler"],
 "workspace-views": ["workspace-views"], "home": ["home"], "recents": ["recent"], "zuletzt": ["zuletzt"], "widgets": ["widget"],
 "produkt-tour": ["tour"], "e-mail-benachrichtig": ["e-mail-benachrichtig"], "management-commands": ["management-commands"],
 "sub-issues": ["sub-issue"], "parent": ["sub-issue"], "versionshistorie": ["version"], "versionen": ["version"], "beschreibungs-version": ["version"],
 "aktivitätsverlauf": ["activity","verlauf"], "activity": ["activity"], "custom-theme": ["custom-theme"], "high-contrast": ["high-contrast"],
 "god-mode": ["admin"], "sign-in": ["sign-in","anmeldung","authentifizierung"], "sign-up": ["sign-up","authentifizierung"],
 "abmelden": ["sign-out","abmeldung"], "registrierung": ["sign-up"], "e-mail-adresse": ["e-mail-änderung"], "konto": ["kontodeaktivierung"],
 "slash-command": ["slash-command"], "bubble-menü": ["bubble-menü"], "drag-handle": ["drag-handle","side-menu","block-menü"], "code-block": ["code"],
 "bilder": ["bild"], "listen": ["listen-tastatur"], "realtime": ["kollaboration","live"], "live-server": ["live-server"],
 "projektliste": ["projektliste"], "projekt-settings": ["projekt-einstellungen"], "projekt-einstellungen": ["projekt-einstellungen"],
 "workspace-settings": ["einstellungs-rahmen"], "workspace-einstellungen": ["einstellungs-rahmen"], "profil-einstellungen": ["profil-/account","profil"],
 "profil-settings": ["profil-/account"], "benutzerprofil": ["benutzerprofil","your work"], "drafts": ["draft"],
}
import unicodedata
def keywords(entry):
    words = re.findall(r"[A-Za-zÄÖÜäöüß0-9][\wÄÖÜäöüß\-]*", (entry.get("name","") + " " + entry.get("area","")).lower())
    kws = set()
    for w in words:
        for k, v in SYN.items():
            if w.startswith(k): kws.update(v)
    return kws
def head_hit(k, h):
    return re.search(r"(?<![\w\-])" + re.escape(k), h) is not None
def best_section(tag, entry):
    fn = DOCS[tag]
    toks = tokens_for(entry); kws = keywords(entry)
    if not kws: return None
    black = BLACK.get(fn, set())
    best = None; bestc = 0.0
    lines_all = open(f"{ANA}/{fn}", encoding="utf-8").read().split("\n")
    heads = {m.group(1): ln.lower() for ln in lines_all for m in [re.match(r"^### (\d+\.\d+)\b", ln)] if m}
    for n, txt in doc_sections(fn):
        if n.startswith(("1.", "4.", "5.", "6.")) or n in black: continue
        h = heads.get(n, "")
        hs = sum(1 for k in kws if head_hit(k, h))
        if hs == 0: continue
        ts = min(sum(txt.count(t) for t in toks), 4)
        score = 4 * hs + ts
        if score > bestc: best, bestc = n, score
    return best

for sid, sec in SEC.items():
    fn = DOCS[sid.split('#')[0]]
    if sid not in SRC: print('Override ohne Quelle', sid); sys.exit(1)
    if not any(n == sec for n, _ in doc_sections(fn)): print('Override-Abschnitt fehlt', sid, sec); sys.exit(1)
# ---- Katalog bauen
out = []
counters = collections.Counter()
for f in C:
    counters[f["d"]] += 1
    fid = f"CE-{f['d']}-{counters[f['d']]:03d}"
    be, fe = [], []
    for s in f["src"]:
        for r in SRC[s].get("code_refs", []):
            if skip(r): continue
            r = REF_FIX.get(r, r)
            (fe if is_front(r) else be).append(r)
    be = list(dict.fromkeys(be)); fe = list(dict.fromkeys(fe))
    docs = []
    for s in f["src"]:
        tag = s.split("#")[0]
        sec = SEC.get(s) or best_section(tag, SRC[s])
        ref = f"migration/analysis/{DOCS[tag]}" + (f" §{sec}" if sec else "")
        if not any(d.startswith(f"migration/analysis/{DOCS[tag]}") for d in docs): docs.append(ref)
    f["id"] = fid; f["be"] = be; f["fe"] = fe; f["docs"] = docs
    out.append({"id": fid, "domain": DOMNAME[f["d"]], "name": f["n"],
                "description": (f["t"] + (f" [Status: {f['s']}]" if f["s"] else "")),
                "backend_refs": be, "frontend_refs": fe, "doc": "; ".join(docs)})

os.makedirs(ROOT + "/migration/features/_data", exist_ok=True)
json.dump(out, open(ROOT + "/migration/features/_data/ce-features.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
json.dump({"C": C, "EXCL": EXCL}, open(os.path.dirname(__file__) + "/built.json", "w", encoding="utf-8"), ensure_ascii=False)
print("Features:", len(out))
for d, n in DOM: print(d, counters[d])
