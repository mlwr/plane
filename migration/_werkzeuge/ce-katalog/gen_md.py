import json, os, re, sys, collections
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = "/home/user/plane"
OUT = ROOT + "/migration/features/10-ce-feature-katalog.md"
B = json.load(open(HERE + "/built.json", encoding="utf-8"))
C, EXCL = B["C"], B["EXCL"]
src_mod = {"__file__": HERE + "/build.py"}
exec(open(HERE + "/build.py", encoding="utf-8").read().split("# ---- Validierung")[0].replace("from cat3 import C, EXCL", "").replace("from overrides import SEC", ""), src_mod)
SRC, DOCS, DOM = src_mod["SRC"], src_mod["DOCS"], src_mod["DOM"]
DOMNAME = dict(DOM)

def esc(t): return t.replace("|", "\\|")
def code_list(refs): return "<br>".join(f"`{esc(r)}`" for r in refs) if refs else "–"
def doc_links(docs):
    out = []
    for d in docs:
        m = re.match(r"migration/analysis/(\S+?)(?: §(\S+))?$", d)
        fn, sec = m.group(1), m.group(2)
        out.append(f"[{fn[:fn.index('-')]}{' §' + sec if sec else ''}](../analysis/{fn})")
    return "<br>".join(out)
def status_cat(s):
    if not s: return "aktiv"
    if "Upsell" in s: return "Upsell im CE"
    if "defekt" in s: return "defekt/eingeschränkt"
    if "eingeschränkt" in s or "deaktiviert" in s: return "defekt/eingeschränkt"
    if "nur API" in s: return "nur API"
    if "nur Backend" in s: return "nur Backend"
    if "intern" in s: return "intern"
    return "aktiv"

def W(text, mode="a"):
    with open(OUT, mode, encoding="utf-8") as f: f.write(text)

# Zuordnung Quelle -> Features
src2ids = collections.defaultdict(list)
for f in C:
    for s in f["src"]: src2ids[s].append(f["id"])
excl_by_src = {e["src"]: e for e in EXCL}
per_tag = collections.Counter(s.split("#")[0] for s in SRC)
cat_tag = collections.Counter(s.split("#")[0] for s in SRC if s in src2ids)
exc_tag = collections.Counter(s.split("#")[0] for s in SRC if s in excl_by_src)
n_feat = len(C); n_src = len(SRC); n_excl = len(EXCL)
n_assign = sum(len(f["src"]) for f in C)
dom_count = collections.Counter(f["d"] for f in C)

# ---------------- Teil 1: Kopf, Methode ----------------
W(f"""# 10 – Feature-Katalog der Community Edition (Plane v1.4.2) – IST-Analyse

> **Gegenstand:** Vollständiger, deduplizierter Katalog aller Funktionen der Plane Community Edition v1.4.2 (AGPL-3.0), Repo-Root `/home/user/plane`, gegliedert nach fachlicher Domäne, mit stabiler ID je Feature.
> **Bindende Leitplanken:** `migration/architecture/00-grundsatzentscheidungen.md` (ADR-001: eine Edition, kein Upsell/Billing; ADR-002: Realtime in .NET/YDotNet; ADR-003: Greenfield; ADR-004: Self-hosted/Airgapped; ADR-005: UI 1:1; ADR-006: Original-Repo als Referenz).
> **Eingaben:** die Feature-Listen der Bereichsanalysen `migration/analysis/_data/A01 … A13b.features.json` (alle {n_src - per_tag['A13a']} Einträge gelesen) sowie die für diesen Katalog neu abgeleitete Liste `migration/analysis/_data/A13a.features.json` ({per_tag['A13a']} Einträge aus `migration/analysis/13a-designsystem-ui-tokens.md` Abschnitte 1–2).
> **Ausgaben:** dieses Dokument und die maschinenlesbare Fassung `migration/features/_data/ce-features.json` (Array von Objekten `{{id, domain, name, description, backend_refs[], frontend_refs[], doc}}`).
> **Ergebnis in Zahlen:** {n_src} Quell-Einträge → **{n_feat} Katalog-Features** in 24 Domänen; {n_excl} Quell-Einträge sind begründet nicht katalogisiert (unerreichbarer Code, entfallende Upsell-/Telemetrie-Elemente, Bezahl-Spuren – Abschnitt 3). Jeder Quell-Eintrag ist mindestens einem Katalog-Feature oder genau einem Ausschluss zugeordnet (Rückverfolgung in Abschnitt 4).
> **Schwester-Dokumente:** Bezahl-Features (Pro/Business/Enterprise) sind in `migration/features/20-paid-spuren-im-repo.md` bis `migration/features/28-paid-integrationen-importer-ai.md` spezifiziert (IDs PF-01 … PF-105, `migration/features/_data/P01.paid.json`); dieser Katalog verweist dorthin, übernimmt sie aber nicht.

---

## Inhaltsverzeichnis

1. Zweck, Methode und Konventionen
   - 1.1 Eingaben · 1.2 Vorgehen · 1.3 ID-Schema · 1.4 Spalten und Status-Werte · 1.5 Domänen-Übersicht · 1.6 Geklärte Widersprüche und Korrekturen der Quelldaten
2. Katalog je Domäne (2.1 Workspace & Mitglieder … 2.24 Betrieb & Plattform)
3. Nicht katalogisierte Quell-Einträge (unerreichbar, entfallend, Bezahl-Spuren)
4. Rückverfolgung: Quell-Eintrag → CE-ID (vollständig)
5. Statistik je Domäne
6. Hinweise für Implementierungs-Agenten und offene Punkte

---

## 1. Zweck, Methode und Konventionen

Der Katalog ist das zentrale Inventar, gegen das die .NET-/Angular-Neuimplementierung auf Vollständigkeit geprüft wird: Jede hier gelistete CE-Funktion muss im Zielsystem (nach ADR-001 zusammen mit allen Bezahl-Funktionen aus `migration/features/20–28`) vorhanden sein. Die Beschreibungen sind bewusst kompakt; maßgeblich für Details (Feldnamen, Endpunkte, Edge-Cases) sind das je Feature verlinkte Analyse-Dokument mit Abschnitt und der referenzierte Originalcode (ADR-006).

### 1.1 Eingaben

| Kürzel | Analyse-Dokument | Feature-Liste | Einträge | katalogisiert | ausgeschlossen |
|---|---|---|---|---|---|
""", "w")
rows = []
for tag, fn in DOCS.items():
    rows.append(f"| {tag} | `migration/analysis/{fn}` | `migration/analysis/_data/{tag}.features.json`{' (neu, dieses Dokument)' if tag == 'A13a' else ''} | {per_tag[tag]} | {cat_tag[tag]} | {exc_tag[tag]} |")
rows.append(f"| **Summe** | | | **{n_src}** | **{sum(cat_tag.values())}** | **{sum(exc_tag.values())}** |")
W("\n".join(rows) + "\n\n")

W(f"""Die Quell-Einträge haben einheitlich die Felder `name`, `area`, `description`, `code_refs` (geprüft für alle Dateien in `migration/analysis/_data/*.features.json`). Für 13a (Designsystem) gab es keine Liste; sie wurde aus `migration/analysis/13a-designsystem-ui-tokens.md` §1.1–§2.32 abgeleitet (nutzersichtbare Funktionen: Themes, Custom Theme, High Contrast, Token-System, Typografie, Schriften, Icons, Komponenten-Varianten, Illustrationen, Animationen, Lade-Indikatoren, Editor-Farben, Power-K-Optik) und im selben Schema nach `migration/analysis/_data/A13a.features.json` geschrieben.

### 1.2 Vorgehen

| Schritt | Beschreibung | Beleg |
|---|---|---|
| 1. Vollständiges Lesen | Alle {n_src} Quell-Einträge wurden gelesen; Backend-Analysen (A01–A07) sind eher grob (Endpunkt-/Modell-Ebene), Frontend-Analysen (A08–A12) fein (Bedienelement-Ebene). | `migration/analysis/_data/*.features.json` |
| 2. Deduplizierung | Einträge, die dieselbe Funktion aus verschiedenen Blickwinkeln beschreiben (Datenmodell A02, interne API A03/A04, Hintergrundjob A07, Frontend A08–A11, Shared Packages A13b), wurden zu **einem** Katalog-Feature zusammengeführt. Grobe Backend-Einträge, die mehrere feine UI-Funktionen abdecken, sind mehreren Katalog-Features zugeordnet (so verteilt sich A04#27 „Cycles verwalten“ auf {', '.join(src2ids['A04#27'])}); insgesamt {n_assign} Zuordnungen für {sum(cat_tag.values())} katalogisierte Quell-Einträge. | Abschnitt 4 |
| 3. Domänenzuordnung | Die 22 vorgegebenen fachlichen Domänen wurden um zwei Zusatzdomänen ergänzt (UIX, OPS), weil {dom_count['UIX'] + dom_count['OPS']} Funktionen (Deployment, Infrastruktur, Datenpflege, querschnittliches UI-Verhalten) sonst sachfremd einsortiert werden müssten. | Abschnitt 1.5 |
| 4. Refs | `backend_refs` = alle Quell-`code_refs` außerhalb der Client-Pfade (`apps/api`, `apps/live`, `apps/proxy`, `deployments`, `.github`, Root-Dateien); `frontend_refs` = `apps/web`, `apps/admin`, `apps/space`, `packages/*`, `@makeplane/propel@0.7.3` (npm) und `pnpm-workspace.yaml`. Reihenfolge = Reihenfolge der Quellen, Duplikate entfernt; `migration/…`-Verweise entfallen. | Build-Regel |
| 5. Gegenstücke ergänzt | Wo ein reines UI-Feature ein eindeutiges Backend-Gegenstück in den Quellen hat (oder umgekehrt), wurde die Quelle dem Feature zusätzlich zugeordnet; welche Quellen ein Feature stützen, zeigt die Spalte „Quellen“. Funktionen ohne Gegenstück (reine Client-Logik, reine Hintergrundjobs) haben bewusst „–“. | Spalten Backend-/Frontend-Refs |
| 6. Dokumentverweise | Je Quelle das zugehörige Analyse-Dokument mit dem passenden Abschnitt (§) aus Abschnitt 2 (Inventare) oder 3 (Verhalten); Abschnitte wurden über Überschriften-Stichworte ermittelt und vollständig manuell geprüft bzw. korrigiert. Die erste Angabe ist die Primärquelle. | Spalte „Analyse-Dok.“ |
| 7. Ausschlüsse | Nicht katalogisiert werden nur (B) im CE unerreichbarer Code, (C) nach ADR-001/ADR-004 entfallende Elemente und (D) reine Bezahl-Spuren, die in `migration/features/20–28` spezifiziert sind. | Abschnitt 3 |
| 8. Validierung | Maschinell geprüft: jede Quell-ID existiert, jeder Quell-Eintrag ist zugeordnet (Katalog oder Ausschluss, nie beides), jede Domäne existiert, jeder §-Abschnitt existiert im Zieldokument, jeder referenzierte Repo-Pfad existiert (Ausnahme: npm-Paket `@makeplane/propel`, Glob `packages/i18n/src/locales/en/*.json`). | Abschnitt 1.6 |

### 1.3 ID-Schema

`CE-<DOMÄNE>-<NNN>` mit dreistelliger, je Domäne fortlaufender Nummer in der Reihenfolge dieses Katalogs (Muster: `CE-WI-001`). Die IDs sind **stabil**: Neue Features erhalten die nächste freie Nummer ihrer Domäne; entfallende Features behalten ihre ID mit Status-Vermerk; Nummern werden nicht neu vergeben. Querverweise aus Architektur-, Backlog- und Testdokumenten sollen ausschließlich diese IDs nutzen.

### 1.4 Spalten und Status-Werte

| Spalte / Feld | Inhalt |
|---|---|
| ID (`id`) | stabile Katalog-ID |
| Feature (`name`) | Kurzname der Funktion |
| Beschreibung (`description`) | fachliche Kurzbeschreibung mit den wichtigsten Regeln, Grenzwerten und Seiteneffekten; im JSON wird ein Status ≠ „aktiv“ als Suffix `[Status: …]` angehängt |
| Status | leer = aktiv in der CE; **nur API** = Endpunkt ohne CE-Frontend; **nur Backend** = Hintergrundjob/Serverlogik ohne eigene UI; **intern** = technische Grundlage des Clients; **defekt/eingeschränkt** = im Original fehlerhaft oder bewusst eingeschränkt (Entscheidung „1:1 oder korrigieren“ im Analyse-Dokument); **Upsell im CE → PF-xx** = CE zeigt nur Upgrade-Hinweis, Umsetzung nach Bezahl-Spezifikation |
| Backend-Refs (`backend_refs`) | Server-/Infrastruktur-Pfade aus den Quellen |
| Frontend-Refs (`frontend_refs`) | Client-Pfade aus den Quellen |
| Analyse-Dok. (`doc`) | Analyse-Dokument(e) mit Abschnitt; im JSON als `migration/analysis/<datei> §x.y`, mehrere durch „; “ getrennt |
| Quellen | IDs der zusammengeführten Quell-Einträge (`<Kürzel>#<Index>` = Position im jeweiligen `*.features.json`, 0-basiert) |

### 1.5 Domänen-Übersicht

| Kürzel | Domäne | Features | Abgrenzung |
|---|---|---|---|
""")
ABGR = {
 "WS": "Workspace-Lebenszyklus, Mitglieder, Rollen, Einladungen, Workspace-Shell (Top-Navigation, Sidebar, Favoriten), Workspace-Settings-Rahmen",
 "PRJ": "Projektliste und -Lebenszyklus, Projekt-Navigation, Projekt-Einstellungen inkl. Feature-Toggles, Mitglieder, States, Labels, Estimates, Automationen",
 "WI": "Anlegen/Bearbeiten, Detailseite und Peek, Properties und Dropdowns, Hierarchie und Relationen, Links und Anhänge, Kommentare/Reaktionen/Aktivität, Versionen, Abos/Mentions, Archiv/Löschen/Drafts",
 "LV": "Layouts List/Kanban/Calendar/Gantt/Spreadsheet, Rich- und Legacy-Filter, Display-Optionen, Projekt- und Workspace-Views, Archiv-Ansichten",
 "CYC": "Cycles inkl. Dashboard, Burndown, Transfer, Archiv; workspace-weite Active Cycles",
 "MOD": "Module inkl. Layouts, Status, Links, Fortschritt, Archiv",
 "INT": "Intake (Triage) inkl. Snooze, Duplikat, Annahme/Ablehnung",
 "PAGE": "Page-Verwaltung, Page-Editor-Seite und gemeinsamer Editor (`packages/editor`)",
 "RT": "Live-Server (Hocuspocus/Yjs) und Kollaborations-Client",
 "ANA": "Workspace-Analytics, Analytics-Panel, Legacy-Analytics-API",
 "HOME": "Workspace-Home, Widgets, Quick links, Recents, Stickies, Produkt-Tour",
 "NOTIF": "In-App- und E-Mail-Benachrichtigungen",
 "SRCH": "Such-Endpunkte, Power-K-Kommandopalette, Tastatur-Shortcuts",
 "PROF": "Profil-Einstellungen und Benutzerprofil im Workspace („Your work“)",
 "AUTH": "Anmeldung/Registrierung (Passwort, Magic-Code, OAuth), Passwörter, Sessions, Rate-Limits, Post-Login, Onboarding",
 "INST": "Instanz-Backend (Registrierung, Konfiguration) und God Mode (`apps/admin`)",
 "SPACE": "Veröffentlichung von Projekten, öffentliches Board (`apps/space`) inkl. Space-Login",
 "API": "Öffentliche REST-API `/api/v1/` mit API-Key",
 "WH": "Workspace-Webhooks und persönliche API-Tokens",
 "EXP": "Work-Item-Export und Export-Historie",
 "AI": "KI-Assistent und Unsplash-Bildsuche (OAuth-Provider siehe AUTH)",
 "I18N": "Lokalisierung (Sprachen, Datum, Zeitzonen) sowie Theming und Designsystem (abgeleitet aus 13a)",
 "UIX": "Zusatzdomäne: domänenübergreifendes UI-Grundverhalten (Header, Leerzustände, Dialoge, Fehlerseiten, Uploads, Redirects)",
 "OPS": "Zusatzdomäne: Deployment, Infrastruktur, Dateien/Datenpflege, Sicherheit-Querschnitt, Betrieb und Entwicklung",
}
W("\n".join(f"| {d} | {n} | {dom_count[d]} | {ABGR[d]} |" for d, n in DOM) + f"\n| **Summe** | | **{n_feat}** | |\n\n")

W("""### 1.6 Geklärte Widersprüche und Korrekturen der Quelldaten

| Thema | Widersprüchliche Quellangaben | Ergebnis (im Code geprüft) | Beleg |
|---|---|---|---|
| Gültigkeit der Export-Links | „8 Tage“ (A02a#27) vs. „7 Tage“ (A03#46, A07#11, A10b#98) | Presigned-Link `ExpiresIn` = 7 × 24 × 60 × 60 s; der Ablauf-Job entfernt URLs von Exporten, die älter als 8 Tage sind | `apps/api/plane/bgtasks/export_task.py` Z. 48, 79, 112; `apps/api/plane/bgtasks/exporter_expired_task.py` Z. 26 |
| Seitengröße der Stickies | „Pagination (20)“ (A03#15) vs. „Pagination (30)“ (A08#20) | Backend-Default `default_per_page=20`, das Frontend fordert `STICKIES_PER_PAGE = 30` an | `apps/api/plane/app/views/workspace/sticky.py` Z. 51; `packages/constants/src/stickies.ts` Z. 7 |
| Webhook-Wiederholungen | „automatische Deaktivierung nach 6 Fehlversuchen“ (A07#6) | `max_retries=5` mit `retry_backoff=600` und `retry_jitter=True` → 1 Erstversuch + 5 Wiederholungen | `apps/api/plane/bgtasks/webhook_task.py` Z. 237–240, 355 |
| Intake-Statuswerte | „-2/-1/0/1/2“ (A02b#29) | `(-2, "Pending")`, `(-1, "Rejected")`, `(0, "Snoozed")`, `(1, "Accepted")`, `(2, "Duplicate")`; die UI nennt -1 „Declined“ | `apps/api/plane/db/models/intake.py` Z. 61–65 |
| Rollenwerte | „20/15/5“ | `ROLE_CHOICES = ((20, "Admin"), (15, "Member"), (5, "Guest"))` | `apps/api/plane/db/models/workspace.py` Z. 19 |
| Pfad-Korrektur | A09#40 nennt `apps/web/hooks/use-intersection-observer.tsx` | Datei heißt `apps/web/hooks/use-intersection-observer.ts` (im Katalog korrigiert) | Repo |
| Pfad-Korrektur | A04#40 nennt `apps/api/plane/permissions/page.py` | Datei liegt unter `apps/api/plane/app/permissions/page.py` (im Katalog korrigiert; zusätzlich existiert `apps/api/plane/utils/permissions/page.py`) | Repo |

---

## 2. Katalog je Domäne

""")

# ---------------- Teil 2: Domänen ----------------
for i, (d, dn) in enumerate(DOM, 1):
    feats = [f for f in C if f["d"] == d]
    W(f"### 2.{i} {dn} (CE-{d}, {len(feats)} Features)\n\n{ABGR[d]}.\n\n")
    groups = list(dict.fromkeys(f["g"] for f in feats))
    for g in groups:
        W(f"#### {g}\n\n| ID | Feature | Beschreibung | Status | Backend-Refs | Frontend-Refs | Analyse-Dok. | Quellen |\n|---|---|---|---|---|---|---|---|\n")
        for f in feats:
            if f["g"] != g: continue
            W(f"| {f['id']} | {esc(f['n'])} | {esc(f['t'])} | {esc(f['s']) if f['s'] else ''} | {code_list(f['be'])} | {code_list(f['fe'])} | {doc_links(f['docs'])} | {', '.join(f['src'])} |\n")
        W("\n")

# ---------------- Teil 3: Ausschlüsse ----------------
W("""---

## 3. Nicht katalogisierte Quell-Einträge

Diese Quell-Einträge beschreiben Code, der im CE-Repo vorhanden ist, aber keine eigenständige CE-Funktion darstellt. Sie sind vollständig aufgeführt, damit kein Eintrag „verloren“ geht.

""")
TITLES = {"B": ("3.1 Im CE-Code vorhanden, aber unerreichbar bzw. ungenutzt", "Nicht zu portieren, solange keine Funktion sie benötigt; bei Bedarf als Implementierungsdetail behandeln."),
          "C": ("3.2 Entfällt nach ADR-001 (Upsell/Billing) bzw. ADR-004 (Telemetrie)", "Wird nicht portiert. Wo das Original einen Upsell zeigt, wird die echte Funktion gebaut (siehe Verweis)."),
          "D": ("3.3 Bezahl-Spuren (Spezifikation in `migration/features/20–28`)", "CE enthält nur Stubs, Typen, Texte oder Datenmodell-Gerüste; nach ADR-001 werden die Funktionen gemäß der genannten PF-IDs umgesetzt (`migration/features/_data/P01.paid.json`).")}
for cat in "BCD":
    t, hint = TITLES[cat]
    items = [e for e in EXCL if e["cat"] == cat]
    W(f"### {t} ({len(items)} Einträge)\n\n{hint}\n\n| Quelle | Quell-Name | Grund | Verweis | Code-Refs der Quelle |\n|---|---|---|---|---|\n")
    for e in items:
        s = SRC[e["src"]]
        refs = [r for r in s.get("code_refs", []) if not r.startswith("migration/")]
        vw = e['verweis']
        vw = re.sub(r"(?<![/\w])(\d\d[ab]?-[\w-]+\.md)", r"`migration/analysis/\1`", vw) if 'features/' not in vw else vw
        W(f"| {e['src']} | {esc(s['name'])} | {esc(e['grund'])} | {esc(vw)} | {code_list(refs)} |\n")
    W("\n")

# ---------------- Teil 4: Rückverfolgung ----------------
W("""---

## 4. Rückverfolgung: Quell-Eintrag → CE-ID (vollständig)

Je Quell-Datei alle Einträge in Dateireihenfolge mit den zugeordneten Katalog-IDs bzw. dem Ausschluss (B/C/D, Abschnitt 3).

""")
for tag, fn in DOCS.items():
    W(f"### 4.{list(DOCS).index(tag) + 1} {tag} – `migration/analysis/_data/{tag}.features.json` ({per_tag[tag]} Einträge)\n\n| Quelle | Bereich (`area`) | Quell-Name | Zuordnung |\n|---|---|---|---|\n")
    idx = sorted((int(s.split('#')[1]), s) for s in SRC if s.split('#')[0] == tag)
    for _, s in idx:
        e = SRC[s]
        z = ", ".join(src2ids[s]) if s in src2ids else f"Ausschluss {excl_by_src[s]['cat']} (Abschnitt 3)"
        W(f"| {s} | {esc(e.get('area', ''))} | {esc(e['name'])} | {z} |\n")
    W("\n")

def I(d, n):
    h = [f["id"] for f in C if f["d"] == d and f["n"] == n]
    assert len(h) == 1, (d, n)
    return h[0]
# ---------------- Teil 5: Statistik ----------------
W("""---

## 5. Statistik je Domäne

Spalten: Features gesamt und nach Status (Abschnitt 1.4); „Quellen“ = Anzahl verschiedener zusammengeführter Quell-Einträge; „Zuordnungen“ = Summe der Quell-Zuordnungen; „BE-/FE-Refs“ = Summe der Pfadangaben; „ohne BE/FE“ = Features ohne Backend- bzw. Frontend-Refs.

| Kürzel | Domäne | Features | aktiv | nur API | nur Backend | intern | defekt/eingeschränkt | Upsell im CE | Quellen | Zuordnungen | BE-Refs | FE-Refs | ohne BE | ohne FE |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
""")
tot = collections.Counter()
for d, dn in DOM:
    fs = [f for f in C if f["d"] == d]
    sc = collections.Counter(status_cat(f["s"]) for f in fs)
    srcs = set(s for f in fs for s in f["src"])
    row = dict(n=len(fs), a=sc["aktiv"], api=sc["nur API"], be=sc["nur Backend"], i=sc["intern"], de=sc["defekt/eingeschränkt"], up=sc["Upsell im CE"],
               q=len(srcs), z=sum(len(f["src"]) for f in fs), ber=sum(len(f["be"]) for f in fs), fer=sum(len(f["fe"]) for f in fs),
               obe=sum(1 for f in fs if not f["be"]), ofe=sum(1 for f in fs if not f["fe"]))
    tot.update(row)
    W(f"| {d} | {dn} | {row['n']} | {row['a']} | {row['api']} | {row['be']} | {row['i']} | {row['de']} | {row['up']} | {row['q']} | {row['z']} | {row['ber']} | {row['fer']} | {row['obe']} | {row['ofe']} |\n")
W(f"| **Σ** | | **{tot['n']}** | **{tot['a']}** | **{tot['api']}** | **{tot['be']}** | **{tot['i']}** | **{tot['de']}** | **{tot['up']}** | **{sum(cat_tag.values())}**¹ | **{tot['z']}** | **{tot['ber']}** | **{tot['fer']}** | **{tot['obe']}** | **{tot['ofe']}** |\n\n")
W(f"¹ Verschiedene Quell-Einträge über alle Domänen (ein Quell-Eintrag kann mehreren Domänen zugeordnet sein; die Spaltensumme der Domänenzeilen ist daher größer).\n\n")

W(f"""**Verdichtung:** {n_src} Quell-Einträge → {n_feat} Katalog-Features + {n_excl} Ausschlüsse (B: {sum(1 for e in EXCL if e['cat']=='B')}, C: {sum(1 for e in EXCL if e['cat']=='C')}, D: {sum(1 for e in EXCL if e['cat']=='D')}). Im Mittel stützt sich ein Feature auf {f'{tot["z"]/n_feat:.2f}'.replace('.', ',')} Quell-Einträge.

**Anteile:** {tot['a']} Features ({f'{100*tot["a"]/n_feat:.1f}'.replace('.', ',')} %) sind in der CE aktiv und nutzersichtbar bzw. vom Client genutzt; {tot['api']} sind reine API-Funktionen ohne CE-Frontend, {tot['be']} reine Hintergrund-/Serverfunktionen, {tot['i']} interne Client-Grundlagen, {tot['de']} im Original defekt bzw. eingeschränkt, {tot['up']} im CE nur als Upsell vorhanden.

Abdeckung je Quell-Datei: siehe Tabelle 1.1 (Spalten „katalogisiert“/„ausgeschlossen“; Summe = Einträge je Datei).

---

## 6. Hinweise für Implementierungs-Agenten und offene Punkte

| # | Thema | Hinweis | Betroffene IDs / Quellen |
|---|---|---|---|
| 1 | Bezahl-Funktionen | Dieser Katalog enthält nur CE-Funktionen. Nach ADR-001 sind zusätzlich alle PF-Features aus `migration/features/20–28` umzusetzen; Andockpunkte der CE sind in Abschnitt 3.3 je PF-ID aufgeführt. | Abschnitt 3.3 |
| 2 | Upsell-Routen | `/:ws/active-cycles` und der Sidebar-Eintrag `active_cycles` existieren im CE nur als Upgrade-Screen; nach ADR-001 als echte Funktion gemäß PF-04 bauen. | {I('CYC','Workspace-weite Active Cycles')}; A08#14, A10b#12 |
| 3 | Defekte Original-Funktionen | Projekt-Einladungen (Anlage liefert 500), Page-Versionen (werden nie erzeugt), v1-Generic-Assets und v1-User-Asset-Löschung (Server-Variante), Legacy-Endpunkt last-visited-workspace: Entscheidung „1:1 nachbauen oder korrigieren“ gemäß Befundlisten der Analyse-Dokumente treffen. | {I('PRJ','Projekt-Einladungen per E-Mail (defekt, nur API)')}, {I('PAGE','Versionshistorie')}, {I('API','User-Assets (Avatar/Cover)')}, {I('API','Generic Workspace Assets')}, {I('HOME','Legacy-Dashboard und Aktivitätsgraphen (nur API)')} |
| 4 | Fehlender CE-Endpunkt | Das Frontend ruft einen Einzel-PATCH der Sidebar-Präferenzen (`sidebar-preferences/{{key}}`) auf, den das CE-Backend nicht bereitstellt; im Zielsystem bereitstellen. | {I('WS',"Erweiterte Sidebar 'More' mit Pin und Sortierung")}; A03#16 |
| 5 | Airgap (ADR-004) | Externe Links/Assets (GitHub-Star-Link, Changelog-iframe, AGB-/Marketing-Fuß, Kundenlogos, Unsplash, Google/GitHub/GitLab/Gitea-OAuth, LLM-Provider) müssen abschaltbar bzw. konfigurierbar sein; Schriften, Icons und Emoji-Daten werden gebündelt. | {I('WS',"What's new? (Produkt-Changelog)")}, {I('WS','Star-us-on-GitHub-Link')}, {I('AUTH','AGB-Hinweis und Auth-Fuß')}, {I('AI','Unsplash-Bildsuche')}, {I('INST','AI-Einstellungen')}, {I('I18N','Gebündelte Schriften (Airgap)')} |
| 6 | Realtime (ADR-002) | Live-Server-Funktionen (Kollaboration, Persistenz, Titel-Sync, Stateless-Events, Force-Close, Konvertierung, PDF-Export, Health) sind in .NET (YDotNet) neu zu bauen; der Browser-Client bleibt Yjs-kompatibel. | CE-RT-001 … CE-RT-009, {I('PAGE','Page exportieren (PDF/Markdown)')} |
| 7 | Telemetrie | Der Telemetrie-Schalter im God Mode bleibt als Einstellung erhalten ({I('INST','Allgemeine Instanzeinstellungen')}), der OTLP-Export nach außen entfällt (Abschnitt 3.2). | {I('INST','Allgemeine Instanzeinstellungen')}; A01#15, A05#52, A07#37 |
| 8 | Status „nur API“ | API-only-Funktionen sind Bestandteil des API-Vertrags (ADR-003: Verträge am Original orientiert) und für Contract-Tests relevant, auch ohne UI: {'; '.join(f['id'] + ' ' + f['n'] for f in C if status_cat(f['s']) == 'nur API')}. | Status-Spalte „nur API“ |
| 9 | Zusatzdomänen | UIX und OPS sind keine fachlichen Domänen; sie bündeln Querschnitt bzw. Betrieb, damit nichts verloren geht. Die Architektur-Dokumente können sie anderen Schichten (Shell, Plattform) zuordnen, ohne die IDs zu ändern. | CE-UIX-*, CE-OPS-* |
""")
print("geschrieben:", OUT, os.path.getsize(OUT))
