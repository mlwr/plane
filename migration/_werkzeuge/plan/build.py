# -*- coding: utf-8 -*-
"""Erzeugt aus wp_spec*.py:
  - migration/plan/_data/wp-ce.json        (Array {wp, title, phase, ce_ids[], depends_on[], size})
  - migration/plan/02-arbeitspakete-ce.md  (Teil „Arbeitspakete im Detail“ und Anhänge; Kopf aus 02-kopf.md)
  - Mermaid-Abhängigkeitsgraphen je Inkrement in migration/plan/01-roadmap-ce.md
    (zwischen den Markern <!-- GEN:GRAPH:<In> --> und <!-- /GEN:GRAPH:<In> -->)
  - migration/plan/_data/wp-endpoints.json (Endpunkt → Arbeitspaket)
Aufruf: python3 -I migration/_werkzeuge/plan/build.py  (danach check_wp.py)
"""
import collections
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
MIG = os.path.normpath(os.path.join(HERE, "..", ".."))
PLAN = os.path.join(MIG, "plan")

import wp_spec  # noqa: E402
import wp_spec_i1_i3  # noqa: E402,F401
import wp_spec_i4_i7  # noqa: E402,F401

PHASES = ["I0", "I1", "I2", "I3", "I4", "I5", "I6", "I7"]
TYPES = {"V": "Vertikaler Schnitt", "B": "Backend-only", "F": "Frontend-only", "I": "Infrastruktur/Baustein",
         "D": "Editor/Dokumente", "S": "Spike", "X": "Erweiterungspunkt 🧱", "A": "Inkrement-Abnahme"}

ce = json.load(open(os.path.join(MIG, "features", "_data", "ce-features.json"), encoding="utf-8"))
CE = {f["id"]: f for f in ce}
tm = {t["id"]: t for t in json.load(open(os.path.join(MIG, "architecture", "_data", "15-ce-testmatrix.json"), encoding="utf-8"))}
EPS = json.load(open(os.path.join(MIG, "architecture", "_data", "endpoints.json"), encoding="utf-8"))["endpoints"]

WPS = wp_spec.WPS
BY = {w["wp"]: w for w in WPS}
ORDER = {w["wp"]: (PHASES.index(w["phase"]), w["wp"]) for w in WPS}
# Vorlauf-Pakete (plan/01 L-8): Pakete eines Inkrements In (n >= 1), die weder direkt noch transitiv
# von WP-I(n-1)-999 abhängen. Sie müssen in wp_spec.VORLAUF deklariert sein (Schutz gegen versehentlich
# fehlende Meilenstein-Abhängigkeiten).
def _ancestors(n, memo={}):
    if n not in memo:
        acc = set()
        for d in BY[n]["deps"]:
            if d in BY:
                acc.add(d)
                acc |= _ancestors(d)
        memo[n] = acc
    return memo[n]


VORLAUF = sorted([w["wp"] for w in WPS if w["phase"] != "I0"
                  and "WP-%s-999" % PHASES[PHASES.index(w["phase"]) - 1] not in _ancestors(w["wp"])],
                 key=lambda x: (PHASES.index(BY[x]["phase"]), x))
if set(VORLAUF) != set(wp_spec.VORLAUF):
    sys.exit("Vorlauf-Pakete weichen von wp_spec.VORLAUF ab: berechnet %s, deklariert %s" % (VORLAUF, sorted(wp_spec.VORLAUF)))
for v in VORLAUF:
    if BY[v]["type"] in ("V", "F", "A"):
        sys.exit("%s ist Vorlauf-Paket, registriert aber als Typ %s Screens (plan/01 L-8)" % (v, BY[v]["type"]))

CE_OWNER = {}
for w in WPS:
    for c in w["ce"]:
        CE_OWNER.setdefault(c, w["wp"])


def rename(s):
    """Zielbezeichner nach ADR-009C (nur in generierten Texten aus Architekturdaten; Umbenennungstabelle 17)."""
    return s.replace("Plane.", "Funk.").replace("Plane:", "Funk:").replace("Plane__", "Funk__")


# ---------------- Endpunkte zuordnen ----------------
ep_owner = {}
ep_mismatch = []
EP_PRE = set()
EP_LATE = set()
for e in EPS:
    if not e["registered"]:
        continue
    cands = sorted({CE_OWNER[c] for c in e["ce_ids"] if c in CE_OWNER}, key=lambda x: ORDER[x])
    if not cands:
        continue
    same = [c for c in cands if BY[c]["phase"] == e["increment"]]
    own = same[0] if same else cands[0]
    if e["ep"] in wp_spec.EP_OVERRIDE:
        natural = own
        own = wp_spec.EP_OVERRIDE[e["ep"]]
        if PHASES.index(BY[own]["phase"]) <= PHASES.index(BY[natural]["phase"]):
            EP_PRE.add(e["ep"])
        else:
            EP_LATE.add(e["ep"])
    ep_owner[e["ep"]] = own
    if BY[own]["phase"] != e["increment"]:
        ep_mismatch.append((e, own))
EP_BY_WP = collections.defaultdict(list)
for e in EPS:
    if e["ep"] in ep_owner:
        EP_BY_WP[ep_owner[e["ep"]]].append(e)


# ---------------- Hilfen ----------------
import unicodedata


def gh_slug(text):
    """Anker wie GitHub: Kleinbuchstaben, Satz-/Sonderzeichen entfernen, Leerzeichen → Bindestrich."""
    out = []
    for ch in text.lower():
        cat = unicodedata.category(ch)
        if cat[0] in "LNM" or ch in "-_":
            out.append(ch)
        elif ch == " ":
            out.append("-")
    return "".join(out)

def split_refs(s):
    out = []
    for part in [p.strip() for p in s.split(";") if p.strip()]:
        out.append(part.replace("migration/", ""))
    return out


def agg_analysis(w):
    d = collections.OrderedDict()
    for c in w["ce"]:
        for r in split_refs(CE[c]["doc"]):
            m = re.match(r"(\S+\.md)\s*(.*)", r)
            if not m:
                continue
            path, sec = m.group(1), m.group(2).strip()
            d.setdefault(path, [])
            if sec and sec not in d[path]:
                d[path].append(sec)
    lines = []
    for p, secs in d.items():
        lines.append("`%s`%s" % (p, (" " + ", ".join(secs)) if secs else ""))
    return lines + w["ana"]


def agg_paths(w, key):
    seen = collections.OrderedDict()
    for c in w["ce"]:
        for r in CE[c][key]:
            p = r.split(" (")[0].strip()
            seen.setdefault(p, None)
    return list(seen.keys())


def tests_for(w):
    projects, levels, specs = collections.OrderedDict(), collections.OrderedDict(), collections.OrderedDict()
    for c in w["ce"]:
        t = tm[c]
        if t["status"] == "entfällt":
            continue
        for p in re.split(r",\s*", t["project"]):
            if p and p != "–":
                projects.setdefault(rename(p), None)
        for l in t["levels"].split():
            if re.fullmatch(r"L\d", l):
                levels.setdefault(l, None)
        if t["spec"] and t["spec"] != "–":
            specs.setdefault(t["spec"], None)
    return list(projects), sorted(levels), list(specs)


def ce_table(w):
    rows = ["| CE-ID | Feature | Status (15 Anh. B) | Inkrement laut 15 | Pflicht-Ebenen | Testprojekt | E2E-Spec |", "|---|---|---|---|---|---|---|"]
    for c in w["ce"]:
        t = tm[c]
        note = t["note"].replace("|", "/") if t["status"] == "entfällt" else ""
        rows.append("| %s | %s | %s%s | %s | %s | %s | %s |" % (
            c, CE[c]["name"].replace("|", "/"), t["status"], (" – " + note) if note else "", t["inc"],
            t["levels"], rename(t["project"]), ("`%s`" % t["spec"]) if t["spec"] not in ("", "–") else "–"))
    return rows


def endpoint_lines(w):
    eps = EP_BY_WP.get(w["wp"], [])
    if not eps:
        return []
    out = ["| EP | Methode | Pfad | Oberfläche | Handler | Permission | Inkr. 04 | CE-IDs |", "|---|---|---|---|---|---|---|---|"]
    for e in eps:
        out.append("| %s%s | %s | `%s` | %s | %s | %s | %s | %s |" % (
            e["ep"], " (vorab)" if e["ep"] in EP_PRE else " (verschoben)" if e["ep"] in EP_LATE else "", e["method"], e["path"], e["surface"], rename("%s.%s" % (e["endpoint_class"] or "–", e["handler"] or "–")),
            rename(e["permission"] or "–").replace("|", "/"), e["increment"], ", ".join(e["ce_ids"])))
    return out


STD_AK = {
    "V": ["Contract: je Endpunkt dieses Pakets ≥ 1 Szenario mit Golden vom Original (Erfolg, Berechtigungsfehler, Validierungsfehler); Replay grün (L5).",
          "Permission-Matrix (05 Anhang B) für alle Endpunkte dieses Pakets als L3-Test grün; Tenant-Isolation geprüft.",
          "Signal-Stores strukturgleich zum MobX-Original (`store-parity-check`), Vitest je Action (L2).",
          "E2E-Specs dieses Pakets grün gegen Original **und** funk. (Dual-Target, Pflichtszenarien 15 §3.9.3).",
          "Visual-/DOM-/a11y-Prüfpunkte der betroffenen Screens (09 §4.14, 15 §3.10.2) innerhalb der Schwellwerte 15 §3.10.3 (Chromium); i18n-Schlüssel nur aus den Original-Locales (de/en)."],
    "B": ["Contract-Szenarien mit Original-Golden für alle HTTP-Endpunkte dieses Pakets; Replay grün.",
          "Job-/Consumer-Tests: Idempotenz (Inbox), Retry/Backoff, Zeitsteuerung mit `FixedClock`; neue Ereignistypen im Event-Katalog-Snapshot.",
          "Bei Cron-Jobs: Registrierung in `CronRegistrationTests` mit Original-Zeit (UTC)."],
    "F": ["Galerie-Eintrag mit allen Varianten/Zuständen; DOM-Vertrag = Referenz-Galerie; Visual in allen Themes (Chromium).",
          "Tastatur/Fokus (AX3/AX4) wie Original; portierte `packages/blocks`-Tests grün (falls vorhanden)."],
    "I": ["Unit-Tests ≥ 90 % Zeilen; Architekturtest für jede neue Regel; AppHost-Test, falls Topologie betroffen.",
          "Kurzreferenz in `docs/` des Repos `funk.`."],
    "D": ["G-SCHEMA unverändert (Schema-Freeze) oder genehmigte Änderung; G-DOC-Fälle für jeden betroffenen Node/Mark.",
          "Browser-Roundtrip-Test (Playwright) für Yjs, sofern Kollaboration betroffen; Visual-Prüfpunkte des Editors."],
    "S": ["Ergebnisbericht `docs/spikes/<Spike>-ergebnis.md` mit Messwerten; Messungen als automatisierte Tests, die danach dauerhaft in G4 laufen (DoD Typ S).",
          "Bei Abbruchkriterium: Fallback aus 01 §9 ohne weitere Diskussion aktiviert (außer ADR-000…009 betroffen → Auftraggeber)."],
    "X": ["Contract (Interface/Schema/Token) + CE-Default-Implementierung; Eintrag in `tests/extension-points.yaml`.",
          "Test „CE-Default = Original-Verhalten“ (Contract-Replay unverändert grün).",
          "Test mit Fake-Erweiterung aus `Funk.BuildingBlocks.Testing/Extensions` bzw. `provideFakeExtensions()` beweist Erweiterbarkeit ohne CE-Änderung (DoD Typ X)."],
    "A": ["G5 `--inc <In> --strict` grün: `ce-coverage-check`, `original-test-ledger`, Parity-Report (0 ungenehmigte Abweichungen, Endpunkt-Abdeckung des Inkrements 100 %), Visual/a11y, Lastziele, Security-Report.",
          "Demo-Video der Kern-Flows (`--video on`) und Abnahmebericht `docs/acceptance/<In>.md`; fachliche Abnahme durch den Auftraggeber."],
}


def wp_section(w):
    L = []
    L.append("### %s – %s" % (w["wp"], w["title"]))
    L.append("")
    deps = ", ".join(w["deps"]) if w["deps"] else "–"
    L.append("| Merkmal | Wert |")
    L.append("|---|---|")
    L.append("| Inkrement | %s |" % w["phase"])
    L.append("| Typ (DoD 15 §3.15.3) | %s – %s |" % (w["type"], TYPES[w["type"]]))
    L.append("| Größe | %s |" % w["size"])
    L.append("| parallelisierbar | %s |" % ("ja" if w["parallel"] else "nein"))
    L.append("| Abhängigkeiten | %s |" % deps)
    if w["wp"] in VORLAUF:
        L.append("| Vorlauf | ja – darf vor `WP-%s-999` beginnen (plan/01 L-8); abgenommen mit `WP-%s-999` |" % (PHASES[PHASES.index(w["phase"]) - 1], w["phase"]))
    L.append("| CE-IDs | %s |" % (", ".join(w["ce"]) if w["ce"] else "– (keine; %s)" % ("Erweiterungspunkt" if w["type"] == "X" else "Baustein/Spike/Abnahme")))
    if w["ep"]:
        L.append("| Andockstelle | %s |" % w["ep"])
    L.append("")
    L.append("**Ziel.** " + w["goal"])
    L.append("")
    if w["note"]:
        L.append("> **Hinweis:** " + w["note"])
        L.append("")
    if w["ce"]:
        L.append("**Enthaltene CE-IDs**")
        L.append("")
        L.extend(ce_table(w))
        L.append("")
    if w["be"] or w["fe"]:
        L.append("**Betroffene Module/Libs in `funk.`**")
        L.append("")
        for x in w["be"]:
            L.append("- Backend: " + x)
        for x in w["fe"]:
            L.append("- Frontend: " + x)
        L.append("")
    L.append("**Referenzdokumente**")
    L.append("")
    for a in w["arch"]:
        L.append("- Architektur: " + a)
    for a in agg_analysis(w):
        L.append("- Analyse/Feature: " + a)
    if w["ce"]:
        L.append("- Feature-Katalog: `features/10-ce-feature-katalog.md` (Einträge %s)" % ", ".join(w["ce"]))
    L.append("")
    be_o, fe_o = agg_paths(w, "backend_refs"), agg_paths(w, "frontend_refs")
    if be_o or fe_o or w["orig"]:
        L.append("**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)")
        L.append("")
        if be_o:
            L.append("- Backend: " + ", ".join("`%s`" % p for p in be_o))
        if fe_o:
            L.append("- Frontend: " + ", ".join("`%s`" % p for p in fe_o))
        for o in w["orig"]:
            L.append("- " + o)
        L.append("")
    epl = endpoint_lines(w)
    if epl:
        L.append("**Endpunkte (Katalog 04, `architecture/_data/endpoints.json`; %d registriert)**" % (len(epl) - 2))
        L.append("")
        L.extend(epl)
        L.append("")
    L.append("**Akzeptanzkriterien**")
    L.append("")
    i = 1
    for a in w["ak"]:
        L.append("%d. %s" % (i, a)); i += 1
    for a in STD_AK[w["type"]]:
        L.append("%d. %s" % (i, a)); i += 1
    if w["ce"] and w["type"] != "A":
        L.append("%d. `ce-coverage-check --ids %s` grün (Mindestebenen 15 Anhang B)." % (i, ",".join(w["ce"]))); i += 1
    L.append("")
    L.append("**Testumfang**")
    L.append("")
    proj, lev, specs = tests_for(w)
    if lev:
        L.append("- Pflicht-Ebenen (aus 15 Anhang B): " + ", ".join(lev))
    if proj:
        L.append("- Testprojekte: " + ", ".join("`%s`" % p for p in proj))
    if specs:
        L.append("- E2E-Specs (`frontend/apps/e2e/`): " + ", ".join("`%s`" % s for s in specs))
    for t in w["tests"]:
        L.append("- " + t)
    if not (lev or proj or specs or w["tests"]):
        L.append("- " + DEFAULT_TESTS[w["type"]])
    L.append("")
    return L


DEFAULT_TESTS = {
    "X": "Typ-X-Tests (CE-Default unverändert, Fake-Erweiterung wirkt ohne CE-Änderung), L0-Inventarabgleich `ExtensionPointInventoryTests`/`extension-registry-check`.",
    "I": "L1 ≥ 90 % Zeilen, Architekturtest je neuer Regel, AppHost-Test bei Topologie-Änderung.",
    "B": "L1/L3 der betroffenen Module, Contract-Szenarien, Job-/Consumer-Tests.",
    "F": "L2 (Vitest), Galerie-DOM/Visual (Chromium).",
    "D": "G-SCHEMA, G-DOC, Browser-Roundtrip (falls Kollaboration betroffen).",
    "S": "Messungen des Spikes als automatisierte Tests (laufen danach in G4).",
    "V": "L1–L8 laut 15 Anhang B.",
    "A": "G5 des Inkrements.",
}


# ---------------- wp-ce.json ----------------
out = []
for w in sorted(WPS, key=lambda x: ORDER[x["wp"]]):
    out.append({"wp": w["wp"], "title": w["title"], "phase": w["phase"], "ce_ids": w["ce"], "depends_on": w["deps"], "size": w["size"]})
os.makedirs(os.path.join(PLAN, "_data"), exist_ok=True)
json.dump(out, open(os.path.join(PLAN, "_data", "wp-ce.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
json.dump([{"ep": k, "wp": v} for k, v in sorted(ep_owner.items())],
          open(os.path.join(PLAN, "_data", "wp-endpoints.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# ---------------- 02-arbeitspakete-ce.md ----------------
head = open(os.path.join(HERE, "02-kopf.md"), encoding="utf-8").read()
L = [head.rstrip(), ""]
# Übersicht
L.append("## 3. Übersicht aller Arbeitspakete")
L.append("")
L.append("| WP | Titel | Inkr. | Typ | Größe | parallel | CE-IDs | Endpunkte | hängt ab von |")
L.append("|---|---|---|---|---|---|---|---|---|")
for w in sorted(WPS, key=lambda x: ORDER[x["wp"]]):
    L.append("| [%s](#%s) | %s | %s | %s | %s | %s | %d | %d | %s |" % (
        w["wp"], gh_slug("%s – %s" % (w["wp"], w["title"])),
        w["title"] + (" *(Vorlauf)*" if w["wp"] in VORLAUF else ""), w["phase"], w["type"], w["size"], "ja" if w["parallel"] else "nein", len(w["ce"]),
        len(EP_BY_WP.get(w["wp"], [])), ", ".join(w["deps"]) or "–"))
L.append("")
cnt = collections.Counter(w["phase"] for w in WPS)
L.append("Summen: %s; insgesamt %d Arbeitspakete, %d CE-IDs, %d registrierte Endpunkte." % (
    ", ".join("%s = %d" % (p, cnt[p]) for p in PHASES), len(WPS), sum(len(w["ce"]) for w in WPS), len(ep_owner)))
L.append("")
# Erweiterungspunkt-Pakete und ihre Nutzer
L.append("### 3.1 Erweiterungspunkt-Pakete (Typ X) und die Pakete, die sie nutzen")
L.append("")
L.append("| Erweiterungspunkt-Paket | Andockstelle (Quelle) | direkt abhängige Pakete |")
L.append("|---|---|---|")
for w in sorted([x for x in WPS if x["type"] == "X"], key=lambda x: ORDER[x["wp"]]):
    users = sorted([u["wp"] for u in WPS if w["wp"] in u["deps"] and u["type"] != "A"], key=lambda x: ORDER[x])
    L.append("| %s – %s | %s | %s |" % (w["wp"], w["title"].split(":")[0], w["ep"], ", ".join(users) or "– (Abnahme)"))
L.append("")
# Kritischer Pfad je Inkrement (Schätzung S=2, M=5, L=10 Agenten-Arbeitstage)
DUR = {"S": 2, "M": 5, "L": 10}
L.append("### 3.2 Kritischer Pfad je Inkrement (Schätzung)")
L.append("")
L.append("Dauer-Schätzung je Paket: S = 2, M = 5, L = 10 Agenten-Arbeitstage; Pakete außerhalb des Inkrements gelten als erledigt. Der kritische Pfad bestimmt die Mindestdauer eines Inkrements bei unbegrenzter Parallelität.")
L.append("")
L.append("Die Spalte „ab Meilenstein“ rechnet die Vorlauf-Pakete (§3.3) als bereits erledigt und gibt damit die Mindestdauer ab Abnahme des Vorgänger-Inkrements an.")
L.append("")
L.append("| Inkrement | Pakete | Summe (Tage) | kritischer Pfad (Tage) | Pfad | ab Meilenstein (Tage) | Pfad ab Meilenstein |")
L.append("|---|---|---|---|---|---|---|")
CRIT = {}


def _longest(p, skip):
    memo = {}

    def lp(n):
        if n in memo:
            return memo[n]
        best = (0, [])
        for d in BY[n]["deps"]:
            if d in BY and BY[d]["phase"] == p and d not in skip:
                r = lp(d)
                if r[0] > best[0]:
                    best = r
        memo[n] = (best[0] + DUR[BY[n]["size"]], best[1] + [n])
        return memo[n]
    return max((lp(x["wp"]) for x in WPS if x["phase"] == p and x["wp"] not in skip), key=lambda r: r[0])


for p in PHASES:
    ws = [x for x in WPS if x["phase"] == p]
    top = _longest(p, set())
    post = _longest(p, set(VORLAUF))
    CRIT[p] = (top, post)
    L.append("| %s | %d | %d | %d | %s | %s | %s |" % (p, len(ws), sum(DUR[x["size"]] for x in ws), top[0], " → ".join(top[1]),
                                                   post[0] if post != top else "=", " → ".join(post[1]) if post != top else "="))
L.append("")
L.append("### 3.3 Vorlauf-Pakete (plan/01 L-8)")
L.append("")
L.append("Vorlauf-Pakete hängen nicht vom Meilenstein des Vorgänger-Inkrements ab und dürfen beginnen, sobald ihre eigenen Abhängigkeiten gemergt sind. Sie registrieren keine Screens (geprüft: kein Typ V/F) und werden mit ihrem Inkrement abgenommen. `build.py` bricht ab, wenn die berechnete Menge von `wp_spec.VORLAUF` abweicht.")
L.append("")
L.append("| WP | Titel | Inkr. | Typ | frühester Start |")
L.append("|---|---|---|---|---|")
for v in VORLAUF:
    w = BY[v]
    L.append("| %s | %s | %s | %s | nach %s |" % (v, w["title"], w["phase"], w["type"], ", ".join(w["deps"])))
L.append("")
L.append("## 4. Arbeitspakete im Detail")
L.append("")
for p in PHASES:
    L.append("## 4.%d Inkrement %s" % (PHASES.index(p) + 1, p))
    L.append("")
    for w in sorted([x for x in WPS if x["phase"] == p], key=lambda x: ORDER[x["wp"]]):
        L.extend(wp_section(w))
# Anhang A: CE-ID → WP
L.append("## Anhang A – Zuordnung CE-ID → Arbeitspaket (vollständig, 507 Einträge)")
L.append("")
L.append("| CE-ID | Feature | WP | Inkrement WP | Inkrement laut 15 Anh. B | Status |")
L.append("|---|---|---|---|---|---|")
for f in ce:
    o = CE_OWNER.get(f["id"], "**fehlt**")
    L.append("| %s | %s | %s | %s | %s | %s |" % (f["id"], f["name"].replace("|", "/"), o, BY[o]["phase"] if o in BY else "–", tm[f["id"]]["inc"], tm[f["id"]]["status"]))
L.append("")
# Anhang B: Abweichungen Inkrement
L.append("## Anhang B – CE-IDs, deren Inkrement von 15 Anhang B abweicht (Begründung plan/04 OP-PLAN-03)")
L.append("")
L.append("| CE-ID | 15 Anh. B | Plan | WP |")
L.append("|---|---|---|---|")


def inc_ok(plan_phase, matrix_inc):
    if matrix_inc in ("–", ""):
        return True
    if "…" in matrix_inc:
        a, b = matrix_inc.split("…")
        return PHASES.index(a) <= PHASES.index(plan_phase) <= PHASES.index(b)
    return plan_phase in matrix_inc.split("/")


for f in ce:
    o = CE_OWNER[f["id"]]
    if not inc_ok(BY[o]["phase"], tm[f["id"]]["inc"]):
        L.append("| %s | %s | %s | %s |" % (f["id"], tm[f["id"]]["inc"], BY[o]["phase"], o))
L.append("")
# Anhang C: Endpunkt-Inkrement-Abweichungen
L.append("## Anhang C – Endpunkte, deren Inkrement im Katalog 04 vom Arbeitspaket abweicht")
L.append("")
L.append("Ein registrierter Endpunkt gehört zu genau einem Arbeitspaket: dem Paket, das eine seiner CE-IDs enthält und im Inkrement des Katalogs 04 liegt, sonst dem frühesten Paket mit einer seiner CE-IDs. Die folgenden Endpunkte entstehen deshalb in einem anderen Inkrement als in 04 notiert; maßgeblich ist dieser Plan (Begründung plan/04 OP-PLAN-03).")
L.append("")
L.append("| EP | Methode | Pfad | Inkr. 04 | WP | Inkr. WP |")
L.append("|---|---|---|---|---|---|")
for e, own in sorted(ep_mismatch, key=lambda x: x[0]["ep"]):
    L.append("| %s | %s | `%s` | %s | %s | %s |" % (e["ep"], e["method"], e["path"], e["increment"], own, BY[own]["phase"]))
L.append("")
tail = os.path.join(HERE, "02-review.md")
if os.path.exists(tail):
    L.append(open(tail, encoding="utf-8").read().rstrip())
    L.append("")
open(os.path.join(PLAN, "02-arbeitspakete-ce.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")

# ---------------- Graphen in 01 ----------------
road = os.path.join(PLAN, "01-roadmap-ce.md")
if os.path.exists(road):
    txt = open(road, encoding="utf-8").read()
    for p in PHASES:
        ws = sorted([x for x in WPS if x["phase"] == p], key=lambda x: ORDER[x["wp"]])
        g = ["```mermaid", "flowchart LR"]
        prev = "M%d" % (PHASES.index(p) - 1) if p != "I0" else None
        if prev:
            g.append('  %s(["%s abgenommen"])' % (prev, PHASES[PHASES.index(p) - 1]))
        for w in ws:
            short = w["title"].split(": ")[0] if w["type"] in ("X", "S") else w["title"]
            short = re.sub(r"\s*\(.*?\)", "", short)
            short = short.replace('"', "'")
            if len(short) > 48:
                short = short[:46].rstrip() + "…"
            shape = ('{{"%s<br/>%s"}}' if w["type"] == "S" else '[/"%s<br/>%s"/]' if w["type"] == "X" else '(["%s<br/>%s"])' if w["type"] == "A" else '["%s<br/>%s"]') % (w["wp"], short)
            g.append("  %s%s" % (w["wp"].replace("-", "_"), shape))
        prev_ms = "WP-%s-999" % PHASES[PHASES.index(p) - 1] if prev else None
        used = set()
        for w in ws:
            if w["type"] == "A":
                continue
            for d in w["deps"]:
                if d in BY and BY[d]["phase"] == p:
                    g.append("  %s --> %s" % (d.replace("-", "_"), w["wp"].replace("-", "_")))
                    used.add(d)
                elif d == prev_ms:
                    g.append("  %s --> %s" % (prev, w["wp"].replace("-", "_")))
                elif d in BY:
                    g.append("  %s_ext[%s] -.-> %s" % (d.replace("-", "_"), d, w["wp"].replace("-", "_")))
        acc = [w for w in ws if w["type"] == "A"]
        if acc:
            for w in ws:
                if w["type"] != "A" and w["wp"] not in used and w["wp"] in acc[0]["deps"]:
                    g.append("  %s --> %s" % (w["wp"].replace("-", "_"), acc[0]["wp"].replace("-", "_")))
        g.append("```")
        block = "<!-- GEN:GRAPH:%s -->\n%s\n<!-- /GEN:GRAPH:%s -->" % (p, "\n".join(g), p)
        txt = re.sub(r"<!-- GEN:GRAPH:%s -->.*?<!-- /GEN:GRAPH:%s -->" % (p, p), lambda m: block, txt, flags=re.S)
    open(road, "w", encoding="utf-8").write(txt)

print("WPs: %d, CE-IDs: %d, Endpunkte zugeordnet: %d, Endpunkt-Inkrement-Abweichungen: %d, vorab: %d, verschoben: %d, Overrides: %d" % (
    len(WPS), sum(len(w["ce"]) for w in WPS), len(ep_owner), len(ep_mismatch), len(EP_PRE), len(EP_LATE), len(wp_spec.EP_OVERRIDE)))
