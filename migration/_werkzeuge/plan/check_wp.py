# -*- coding: utf-8 -*-
"""Vollständigkeits- und Konsistenzprüfung für migration/plan/_data/wp-ce.json.

Aufruf (aus beliebigem Verzeichnis):
    python3 -I migration/_werkzeuge/plan/check_wp.py

Prüft:
  1. jede CE-ID aus features/_data/ce-features.json ist genau einem Arbeitspaket zugeordnet,
  2. es gibt keine unbekannten CE-IDs,
  3. WP-IDs sind eindeutig und folgen dem Schema WP-<PHASE>-<NNN>,
  4. jede Abhängigkeit existiert, liegt nicht in einer späteren Phase und der Graph ist azyklisch,
  5. Felder und Werte (phase, size) sind gültig,
  6. jede CE-ID mit Status „entfällt“ (15 Anhang B) liegt in einem Arbeitspaket, das den Ersatznachweis führt,
  7. jedes Erweiterungspunkt-Arbeitspaket (Nummernkreis 2xx) trägt keine CE-ID,
  8. jedes Paket eines Inkrements (außer den Spikes WP-I0-9nn) liegt unter der Abnahme WP-In-999,
  9. (Information) Vorlauf-Pakete = Pakete in In (n ≥ 1) ohne transitive Abhängigkeit auf WP-I(n-1)-999.
Exit-Code 0 = alles in Ordnung, 1 = Fehler (Liste auf stdout).
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MIG = os.path.normpath(os.path.join(HERE, "..", ".."))
PHASES = ["I0", "I1", "I2", "I3", "I4", "I5", "I6", "I7"]


def main():
    ce = json.load(open(os.path.join(MIG, "features", "_data", "ce-features.json"), encoding="utf-8"))
    tm = json.load(open(os.path.join(MIG, "architecture", "_data", "15-ce-testmatrix.json"), encoding="utf-8"))
    wps = json.load(open(os.path.join(MIG, "plan", "_data", "wp-ce.json"), encoding="utf-8"))
    errors = []
    all_ids = [f["id"] for f in ce]
    known = set(all_ids)
    status = {t["id"]: t["status"] for t in tm}

    ids = [w["wp"] for w in wps]
    for w in wps:
        for key in ("wp", "title", "phase", "ce_ids", "depends_on", "size"):
            if key not in w:
                errors.append("%s: Feld '%s' fehlt" % (w.get("wp"), key))
        if not re.fullmatch(r"WP-I[0-7]-\d{3}", w["wp"]):
            errors.append("%s: ID-Schema verletzt" % w["wp"])
        if w["phase"] not in PHASES or w["wp"].split("-")[1] != w["phase"]:
            errors.append("%s: Phase '%s' ungültig" % (w["wp"], w["phase"]))
        if w["size"] not in ("S", "M", "L"):
            errors.append("%s: Größe '%s' ungültig" % (w["wp"], w["size"]))
        if w["wp"].split("-")[2].startswith("2") and w["ce_ids"]:
            errors.append("%s: Erweiterungspunkt-Paket trägt CE-IDs" % w["wp"])
    dup = sorted({i for i in ids if ids.count(i) > 1})
    if dup:
        errors.append("doppelte WP-IDs: %s" % ", ".join(dup))

    owner = {}
    for w in wps:
        for c in w["ce_ids"]:
            if c not in known:
                errors.append("%s: unbekannte CE-ID %s" % (w["wp"], c))
            owner.setdefault(c, []).append(w["wp"])
    missing = [c for c in all_ids if c not in owner]
    multi = {c: o for c, o in owner.items() if len(o) > 1}
    if missing:
        errors.append("%d CE-IDs ohne Arbeitspaket: %s" % (len(missing), ", ".join(missing)))
    for c, o in sorted(multi.items()):
        errors.append("%s mehrfach zugeordnet: %s" % (c, ", ".join(o)))

    byid = {w["wp"]: w for w in wps}
    for w in wps:
        for d in w["depends_on"]:
            if d not in byid:
                errors.append("%s: Abhängigkeit %s existiert nicht" % (w["wp"], d))
            elif PHASES.index(byid[d]["phase"]) > PHASES.index(w["phase"]):
                errors.append("%s: Abhängigkeit %s liegt in späterer Phase" % (w["wp"], d))
            if d == w["wp"]:
                errors.append("%s: hängt von sich selbst ab" % w["wp"])
    # Zyklenprüfung (DFS)
    state = {}

    def visit(n, stack):
        state[n] = 1
        for d in byid[n]["depends_on"]:
            if d not in byid:
                continue
            if state.get(d) == 1:
                errors.append("Zyklus: %s" % " → ".join(stack + [n, d]))
            elif state.get(d) is None:
                visit(d, stack + [n])
        state[n] = 2

    for n in byid:
        if state.get(n) is None:
            visit(n, [])

    anc_memo = {}

    def ancestors(n):
        if n not in anc_memo:
            acc = set()
            for d in byid[n]["depends_on"]:
                if d in byid:
                    acc.add(d)
                    acc |= ancestors(d)
            anc_memo[n] = acc
        return anc_memo[n]

    vorlauf = []
    if not any(e.startswith("Zyklus") for e in errors):
        for p in PHASES:
            acc = "WP-%s-999" % p
            if acc not in byid:
                errors.append("Abnahme-Paket %s fehlt" % acc)
                continue
            under = ancestors(acc)
            for w in wps:
                if w["phase"] == p and w["wp"] != acc and w["wp"] not in under and not re.fullmatch(r"WP-I0-9\d\d", w["wp"]):
                    errors.append("%s liegt nicht unter der Abnahme %s" % (w["wp"], acc))
        for w in wps:
            i = PHASES.index(w["phase"])
            if i > 0 and "WP-%s-999" % PHASES[i - 1] not in ancestors(w["wp"]):
                vorlauf.append(w["wp"])

    dropped = [c for c in all_ids if status.get(c) == "entfällt"]
    for c in dropped:
        for o in owner.get(c, []):
            if not byid[o]["title"].lower().count("entfallen"):
                errors.append("%s (entfällt) liegt in %s ohne Ersatznachweis im Titel" % (c, o))

    n_ce = sum(len(w["ce_ids"]) for w in wps)
    print("Arbeitspakete: %d | CE-IDs im Katalog: %d | zugeordnet: %d | davon entfällt: %d" % (len(wps), len(all_ids), n_ce, len(dropped)))
    per_phase = {p: [w for w in wps if w["phase"] == p] for p in PHASES}
    for p in PHASES:
        print("  %s: %3d WPs, %3d CE-IDs" % (p, len(per_phase[p]), sum(len(w["ce_ids"]) for w in per_phase[p])))
    print("Vorlauf-Pakete (%d): %s" % (len(vorlauf), ", ".join(vorlauf) or "–"))
    if errors:
        print("FEHLER (%d):" % len(errors))
        for e in errors:
            print("  - " + e)
        return 1
    print("OK: jede CE-ID ist genau einem Arbeitspaket zugeordnet; Abhängigkeitsgraph gültig und azyklisch.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
