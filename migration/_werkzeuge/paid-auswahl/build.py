"""Erzeugt migration/features/30-paid-auswahlliste.md aus features/_data/paid-features.json.

Jedes EE-Feature wird genau einem Paket zugeordnet; das Skript bricht ab, wenn eine ID fehlt
oder doppelt vergeben ist. Aufruf: python3 -I migration/_werkzeuge/paid-auswahl/build.py

ACHTUNG: Die erzeugte Datei enthält inzwischen die Auswahl des Auftraggebers (Ankreuzungen) und die
Priorisierung in Wellen. Ein erneuter Lauf überschreibt beides; vorher sichern bzw. nachtragen.
"""
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
DATA = os.path.join(ROOT, "migration", "features", "_data", "paid-features.json")
OUT = os.path.join(ROOT, "migration", "features", "30-paid-auswahlliste.md")

EFFORT = {"S": "2–5 PT", "M": "5–15 PT", "L": "15–40 PT", "XL": "40–100 PT"}

# (Paket-ID, Name, Aufwand, strukturrelevant, Abhängigkeiten, Hinweis, [EE-IDs])
GROUPS = [
    ("A", "Work Management", [
        ("A1", "Work-Item-Types & Custom Properties (Projekt-Ebene)", "XL", True, "–",
         "Erweitert Work-Item-Modell, Filter-/Gruppierungs-Engine, Spreadsheet, API. Basis für Epics, Customers, Templates, Importer mit Custom Props.",
         ["EE-P04-001", "EE-P04-003", "EE-P04-004", "EE-P04-005", "EE-P04-006", "EE-P02-001"]),
        ("A2", "Workspace-weite Types/Properties, Typ-Hierarchie, Roll-ups, Property Contexts", "L", True, "A1",
         "Enterprise-Funktionen; Governance-Regeln irreversibel.",
         ["EE-P04-002", "EE-P04-007", "EE-P04-008", "EE-P04-046"]),
        ("A3", "Epics (inkl. Fortschritt, Updates, Conversions)", "M", False, "A1", "",
         ["EE-P04-009", "EE-P04-010", "EE-P04-021"]),
        ("A4", "Initiatives inkl. Labels, Checkpoints/Updates", "M", False, "A3", "",
         ["EE-P04-011", "EE-P04-012", "EE-P04-013"]),
        ("A5", "Milestones", "S", False, "–", "", ["EE-P04-014"]),
        ("A6", "Releases (Tags, Labels, Links, Changelog)", "M", False, "–", "", ["EE-P04-015"]),
        ("A7", "Customers inkl. Requests und Properties", "L", False, "A1 (Property-Engine)", "",
         ["EE-P04-016", "EE-P04-017", "EE-P04-018"]),
        ("A8", "Bulk Ops, Transfers, projektübergreifende Kopien", "M", False, "–", "",
         ["EE-P04-019", "EE-P04-020", "EE-P04-022"]),
        ("A9", "Relationen & Abhängigkeiten (Gantt-Dependencies, Custom Relations, Implements, projektübergreifende Sub-Items)", "L", True, "–",
         "Relationstypen als Katalog statt fester Enum-Liste anlegen.",
         ["EE-P04-023", "EE-P04-024", "EE-P04-025", "EE-P04-044"]),
        ("A10", "Time Tracking, Worklogs, Timesheets, Timesheet-Approvals", "M", False, "–", "",
         ["EE-P04-028", "EE-P04-029", "EE-P04-030"]),
        ("A11", "Advanced Estimates (Zeit-Schätzungen, Systemwechsel)", "S", False, "–", "", ["EE-P04-031"]),
        ("A12", "Module Overview & Auto-Assignment", "M", False, "–", "", ["EE-P04-026", "EE-P04-027"]),
        ("A13", "Projekt-Organisation (Private/Secret Projects, Project States, Project Labels, Overview, Updates)", "L", False, "–", "",
         ["EE-P04-032", "EE-P04-033", "EE-P04-034", "EE-P04-035", "EE-P04-036"]),
        ("A14", "Baselines & Deviations, Custom SLAs", "L", False, "–", "Benötigt Zeitreihen/Snapshots bzw. SLA-Timer im Job-System.",
         ["EE-P04-037", "EE-P04-038"]),
        ("A15", "Intake-Erweiterungen (Intake Forms, E-Mail-Intake, Intake Assignees)", "L", False, "–", "E-Mail-Intake braucht SMTP-Empfangsdienst.",
         ["EE-P04-039", "EE-P04-040", "EE-P04-041"]),
        ("A16", "Votes und Kommentar-Antworten an Work Items", "S", False, "–", "", ["EE-P04-042", "EE-P04-043"]),
        ("A17", "Workspace Governance für States und Labels", "M", True, "–", "", ["EE-P04-045"]),
    ]),
    ("B", "Planung, Insights, Teams", [
        ("B1", "Teamspaces (inkl. Work Items, Views, Pages, Kommentare, Member-Kontext, Feature-Schalter)", "XL", True, "–",
         "Neue Sichtbarkeitsebene zwischen Workspace und Projekt.",
         ["EE-P05-001", "EE-P05-002", "EE-P05-003", "EE-P05-004", "EE-P05-006", "EE-P05-007", "EE-P05-008"]),
        ("B2", "Dashboards & Widgets (inkl. Filter, Intake-/Property-Widgets, Einbettung in Pages)", "L", False, "Charts-Bibliothek",
         "", ["EE-P05-009", "EE-P05-010", "EE-P05-011", "EE-P05-012", "EE-P05-013"]),
        ("B3", "Analytics-Erweiterungen, Custom Reports, Insights, Time Capsule", "L", False, "–", "",
         ["EE-P05-014", "EE-P05-015", "EE-P05-016", "EE-P05-017"]),
        ("B4", "Cycle-Erweiterungen (Progress Charts, Reports, Auto-Schedule, Auto-Rollover, Active Cycles, Parallel Cycles, Complete/Start/End, Teamspace Cycles)", "M", False, "B1 für Teamspace Cycles",
         "", ["EE-P05-005", "EE-P05-018", "EE-P05-019", "EE-P05-020", "EE-P05-021", "EE-P05-022", "EE-P05-023", "EE-P05-024"]),
        ("B5", "Shared Views und Publish Views", "M", False, "–", "", ["EE-P05-025", "EE-P05-026"]),
        ("B6", "Erweiterte Filter, PQL, Text-to-PQL, Advanced Search", "L", True, "G1 für Text-to-PQL",
         "Filter-Engine von Anfang an mit AND/OR/NOT und Operatoren bauen.",
         ["EE-P05-027", "EE-P05-028", "EE-P05-029", "EE-P05-032"]),
        ("B7", "Scheduled Comms (geplante Berichte/Nachrichten)", "M", False, "Job-System", "", ["EE-P05-030"]),
        ("B8", "Home-/Navigations-Erweiterungen, Product Tour", "S", False, "–", "", ["EE-P05-031", "EE-P01-002"]),
    ]),
    ("C", "Workflows, Automationen, Templates", [
        ("C1", "Workflows (Default-Workflow, mehrere typ-spezifische, Historie, Time-in-State, Governance)", "L", True, "–",
         "Zentrale State-Change-Pipeline in der CE vorsehen.",
         ["EE-P06-001", "EE-P06-002", "EE-P06-005", "EE-P06-006", "EE-P06-007"]),
        ("C2", "Approvals (Workflow-Transitionen, Workspace/Projekt/Typ)", "M", False, "C1", "", ["EE-P06-003", "EE-P06-008"]),
        ("C3", "Automation-Engine (Trigger, Bedingungen, Aktionen, Logs, global, zeitgesteuert, Decisions & Loops, Outbox)", "XL", True, "Event/Outbox",
         "Domain-Events + Outbox in der CE vorsehen.",
         ["EE-P06-009", "EE-P06-010", "EE-P06-011", "EE-P06-012", "EE-P06-013", "EE-P06-014", "EE-P06-015", "EE-P06-017", "EE-P06-018"]),
        ("C4", "Scripting (Plane Runner, Transition Hooks)", "L", False, "C1, C3",
         "Ohne Node: JavaScript-Sandbox in .NET (z. B. Jint) nötig.", ["EE-P06-004", "EE-P06-019"]),
        ("C5", "Templates (Projekt, Work Item, Page, vordefinierte, Marketplace)", "L", False, "A1, C1 für vollständige Projekt-Templates",
         "", ["EE-P06-020", "EE-P06-021", "EE-P06-022", "EE-P06-023", "EE-P06-024"]),
        ("C6", "Recurring Work Items & Auto-Reminders", "M", False, "Job-System", "", ["EE-P06-025", "EE-P06-026"]),
    ]),
    ("D", "Wissen: Pages & Wiki", [
        ("D1", "Wiki & Collections (öffentlich/privat)", "L", True, "–", "Pages ohne Projekt im Datenmodell vorsehen.",
         ["EE-P07-001", "EE-P07-002", "EE-P07-003"]),
        ("D2", "Nested Pages & Verschieben von Pages", "M", True, "–", "", ["EE-P07-004", "EE-P07-017"]),
        ("D3", "Page-Versionen erweitert (Aufbewahrung, Vergleich, Highlight, Restore)", "M", False, "–", "", ["EE-P07-005", "EE-P07-006"]),
        ("D4", "Realtime-Presence (Avatare, Live-Cursor)", "S", False, "Realtime-Server", "", ["EE-P07-007"]),
        ("D5", "Page-Publish & Exporte (PDF/Word/Markdown, Queue, ZIP)", "L", False, "–", "PDF/DOCX-Erzeugung in .NET.",
         ["EE-P07-008", "EE-P07-009"]),
        ("D6", "Work-Item-Verknüpfung (Embeds, Mentions, Link Pages, erweiterte Mentions/Backlinks)", "M", False, "–", "",
         ["EE-P07-010", "EE-P07-011", "EE-P07-012", "EE-P07-042"]),
        ("D7", "Kommentare in Pages (inline, Page-Level, Moderation)", "L", False, "–", "", ["EE-P07-013", "EE-P07-014"]),
        ("D8", "Page-Sharing, Page-Labels, Page-Benachrichtigungen", "M", False, "E5 (Rechtemodell)", "",
         ["EE-P07-015", "EE-P07-016", "EE-P07-040"]),
        ("D9", "Erweiterte Editor-Blöcke (Draw.io, Embeds, Attachments, Video, Columns, Tabs, Toggle, Status, Date, LaTeX, Mermaid, HTML-Artifact, TOC, Link pages, Page-Embed, Widget, Block-Links)", "XL", False, "Editor-Port",
         "Pro Block einzeln abwählbar; Draw.io als eigener Container.",
         ["EE-P07-019", "EE-P07-020", "EE-P07-021", "EE-P07-022", "EE-P07-027", "EE-P07-028", "EE-P07-029", "EE-P07-030",
          "EE-P07-031", "EE-P07-032", "EE-P07-033", "EE-P07-034", "EE-P07-035", "EE-P07-036", "EE-P07-037", "EE-P07-038", "EE-P07-039"]),
        ("D10", "Databases + Formulas in Pages", "XL", False, "A1 (Property-Typen)", "Kaum öffentlich spezifiziert.", ["EE-P07-018"]),
        ("D11", "Advanced Pages Analytics", "M", False, "–", "", ["EE-P07-023"]),
        ("D12", "Pages-Public-API", "M", False, "D1, D2", "", ["EE-P07-041"]),
    ]),
    ("E", "Sicherheit & Administration", [
        ("E3", "IdP Group Sync aus Keycloak-Gruppen/-Rollen (→ Workspace-/Projektrollen), SCIM optional", "M", True, "E5",
         "LDAP, SAML/OIDC-SSO, 2FA, Passkeys, Password Policy und Domain-Regeln übernimmt Keycloak (ADR-008).", ["EE-P08-005", "EE-P08-006"]),
        ("E5", "Rollenmodell (RBAC, Custom Roles, GAC)", "XL", True, "–",
         "Berechtigungskatalog statt fester Rollenwerte bereits in der CE.", ["EE-P08-011", "EE-P08-012", "EE-P08-013"]),
        ("E6", "Admin Interface, Workspace Activity Logs, Audit Logs (API)", "M", False, "Event/Outbox", "",
         ["EE-P08-015", "EE-P08-016", "EE-P08-017"]),
        ("E7", "God-Mode-Erweiterungen (User Management, Session-Einstellungen, System Checks, Multi-Workspace-Management)", "M", False, "–", "",
         ["EE-P08-025", "EE-P08-026", "EE-P03-001", "EE-P01-001"]),
        ("E8", "PII-/Sensitive-Data-Scanner (Argus)", "L", False, "–", "", ["EE-P08-027"]),
    ]),
    ("F", "Integrationen & Importer", [
        ("F1", "Integrations-Framework (Connections, Webhook-Empfang, Sync-Engine)", "L", True, "H1",
         "Voraussetzung für F2, F5–F7.", ["EE-P09-001"]),
        ("F2", "Forgejo-Integration (ADR-007): Instanz-/Org-Verbindung, persönliche Konten, Repo↔Projekt-Mapping, bidirektionaler Issue-Sync, PR-/Commit-Automation, Status in Work Items, Branch aus Work Item, Webhooks, Importer, Forgejo-Login", "XL", True, "F1",
         "Einzige Code-Hosting-Integration (ersetzt GitHub/GitLab/Bitbucket). Funktionsumfang orientiert an den GitHub/GitLab-Features der Commercial Edition; Forgejo als Aspire-Ressource im Stack. Kein EE-Gegenstück, daher ohne EE-IDs.",
         []),
        ("F5", "Slack (Verbindung, Benachrichtigungen, Slash-Command, Thread-Sync, Unfurl)", "L", False, "F1", "Nur mit Internetzugang.",
         ["EE-P09-009", "EE-P09-010", "EE-P09-011"]),
        ("F6", "Sentry", "M", False, "F1", "", ["EE-P09-012"]),
        ("F7", "Weitere SaaS-Connectoren (HubSpot, Cursor-Agent, Zapier, Zendesk, Freshdesk)", "L", False, "F1", "Nur mit Internetzugang.",
         ["EE-P09-013", "EE-P09-014", "EE-P09-015", "EE-P09-016", "EE-P09-017"]),
        ("F8", "Importer-Framework, CSV-Import (Work Items, Mitglieder)", "M", False, "–", "", ["EE-P09-019", "EE-P09-027", "EE-P09-029"]),
        ("F9", "Jira-Importer (Cloud, Server/Data Center)", "L", False, "F8, A1 für Custom Props", "", ["EE-P09-020", "EE-P09-021"]),
        ("F10", "Importer Linear, Asana, ClickUp, GitHub", "L", False, "F8", "", ["EE-P09-022", "EE-P09-023", "EE-P09-024", "EE-P09-028"]),
        ("F11", "Importer Notion, Confluence (in Pages/Wiki)", "L", False, "F8, D1", "", ["EE-P09-025", "EE-P09-026"]),
    ]),
    ("G", "Plane AI", [
        ("G1", "AI-Basis (LLM-/Embedding-Provider, Semantic Search mit pgvector, Duplicate Detection, Feature-Schalter)", "L", True, "–",
         "Indexierungs-Pipeline in der CE vorsehen; lokaler Provider für Airgapped.",
         ["EE-P09-030", "EE-P09-038", "EE-P09-039", "EE-P09-042"]),
        ("G2", "Pi-Chat inkl. Connectors (MCP), Skills, Memory, Agents, Autopilot", "XL", False, "G1, H4", "",
         ["EE-P09-031", "EE-P09-032", "EE-P09-033", "EE-P09-034", "EE-P09-035", "EE-P09-036"]),
        ("G3", "AI im Editor und AI-Aktionen (Selection-Aktionen, /ai-Block, Agent in Pages, Work-Creation, Summary/Catch-up, Applets)", "L", False, "G1",
         "", ["EE-P07-024", "EE-P07-025", "EE-P07-026", "EE-P09-037", "EE-P09-040", "EE-P09-041"]),
    ]),
    ("H", "Plattform, API & Betrieb", [
        ("H1", "OAuth-App-Plattform (Apps, Consent, Scopes, Bot-User, App-Mentions, Marketplace, OAuth Bridge)", "L", True, "–",
         "Empfehlung: Keycloak als Autorisierungsserver (ADR-008) statt eigenem OAuth2-Server.", ["EE-P09-044", "EE-P09-045", "EE-P09-046", "EE-P09-018"]),
        ("H2", "Agents-Plattform (Agent Runs, Activities, Signals)", "L", False, "H1", "", ["EE-P09-047"]),
        ("H3", "Public API v2 und API-Erweiterungen (Feature-APIs, Member entfernen, Views-API, Webhooks v2, Workspace-Tokens, GraphQL/Marketplace-Endpunkte)", "L", False, "–",
         "", ["EE-P02-002", "EE-P02-003", "EE-P02-004", "EE-P02-005", "EE-P02-006", "EE-P09-048", "EE-P09-049", "EE-P03-006"]),
        ("H4", "MCP-Server (OAuth-Transport, Tool-Gates)", "M", False, "H1", "", ["EE-P09-050"]),
        ("H5", "Developer-Tools (Plane Compose, SDKs Node/Python)", "M", False, "H3", "", ["EE-P09-051", "EE-P09-052"]),
        ("H6", "Realtime-Event-Server (Live-Updates für alle Objekte)", "M", True, "–", "Mit SignalR im Rahmen vorsehen.", ["EE-P03-007"]),
        ("H7", "Betrieb: Airgapped, FIPS, HA/Read-Replica/External Secrets, separater API-Pool, Installer/Backup", "L", False, "–",
         "Airgapped ist durch ADR-004 bereits gesetzt.", ["EE-P03-002", "EE-P03-003", "EE-P03-004", "EE-P03-005", "EE-P03-008"]),
        ("H8", "Clients: Desktop-App, Mobile-Apps", "XL", False, "H3", "Eigene Produkte, nicht Teil von Web/Angular.",
         ["EE-P09-053", "EE-P09-054"]),
    ]),
]

# Entfällt nach ADR-001 (keine Plan-Stufen/Billing), ADR-004 (kein Hersteller-Betrieb) ADR-007 (nur Forgejo) bzw. ADR-008 (Login nur über Keycloak)
DROPPED = {
    "EE-P08-014": "ADR-001", "EE-P08-018": "ADR-001", "EE-P08-019": "ADR-001", "EE-P08-020": "ADR-001",
    "EE-P08-021": "ADR-001", "EE-P08-022": "ADR-001", "EE-P08-023": "ADR-001/004", "EE-P08-024": "ADR-001",
    "EE-P06-016": "ADR-001", "EE-P09-043": "ADR-001", "EE-P09-055": "ADR-004 (Cloud-only)",
    "EE-P03-010": "ADR-004 (Hersteller-Betrieb)", "EE-P03-009": "ADR-004 (Vertriebskanäle)",
    "EE-P09-002": "ADR-007 (ersetzt durch Forgejo, Paket F2)", "EE-P09-003": "ADR-007 (ersetzt durch Forgejo, Paket F2)",
    "EE-P09-004": "ADR-007 (ersetzt durch Forgejo, Paket F2)", "EE-P09-005": "ADR-007 (ersetzt durch Forgejo, Paket F2)",
    "EE-P09-006": "ADR-007 (ersetzt durch Forgejo, Paket F2)", "EE-P09-007": "ADR-007 (ersetzt durch Forgejo, Paket F2)",
    "EE-P09-008": "ADR-007 (ersetzt durch Forgejo, Paket F2)",
    "EE-P08-001": "ADR-008 (Keycloak: Identity Brokering)", "EE-P08-002": "ADR-008 (Keycloak: Identity Brokering)",
    "EE-P08-003": "ADR-008 (Keycloak: Realms/Identity Provider/Domains)", "EE-P08-004": "ADR-008 (Keycloak: User Federation LDAP/AD)",
    "EE-P08-007": "ADR-008 (Keycloak: OTP)", "EE-P08-008": "ADR-008 (Keycloak: WebAuthn/Passkeys)",
    "EE-P08-009": "ADR-008 (Keycloak: Password Policies)", "EE-P08-010": "ADR-008 (Keycloak: Domain-/Registrierungsregeln)",
}


def main():
    feats = {f["id"]: f for f in json.load(open(DATA, encoding="utf-8"))}
    seen = {}
    for _, _, pkgs in GROUPS:
        for pid, _, _, _, _, _, ids in pkgs:
            for i in ids:
                if i in seen or i in DROPPED:
                    sys.exit(f"{i} doppelt vergeben ({seen.get(i, 'entfällt')} / {pid})")
                if i not in feats:
                    sys.exit(f"{i} unbekannt (Paket {pid})")
                seen[i] = pid
    missing = sorted(set(feats) - set(seen) - set(DROPPED))
    if missing:
        sys.exit("Nicht zugeordnet: " + ", ".join(missing))

    n_pkg = sum(len(p) for _, _, p in GROUPS)
    L = []
    w = L.append
    w("# Auswahlliste der Bezahl-Features")
    w("")
    w("Diese Liste dient der Entscheidung, **welche Bezahl-Features nach der Community Edition umgesetzt werden** und in welcher Reihenfolge. "
      f"Sie fasst alle {len(feats)} Features aus [29-paid-feature-matrix.md](29-paid-feature-matrix.md) zu {n_pkg} Paketen zusammen. "
      f"{len(DROPPED)} Features entfallen nach ADR-001/ADR-004 (Lizenz, Billing, Hersteller-Betrieb) , ADR-007 (GitHub/GitLab/Bitbucket, ersetzt durch Forgejo) bzw. ADR-008 (SSO, LDAP, 2FA, Passkeys, Password Policy, Domains – übernimmt Keycloak) (siehe Abschnitt „Entfällt“).")
    w("")
    w("## So wird die Liste benutzt")
    w("")
    w("1. Pakete ankreuzen (`[x]`), die gebraucht werden. Einzelne Features innerhalb eines Pakets können ebenfalls abgewählt werden.")
    w("2. Optional in der Spalte **Prio** eine Reihenfolge vergeben (1 = zuerst).")
    w("3. Pakete mit 🧱 **strukturrelevant** wirken auf das Fundament der CE. Ihre Erweiterungspunkte werden im Architektur-Rahmen in jedem Fall vorgesehen, "
      "auch wenn das Paket selbst erst später oder gar nicht umgesetzt wird. Dadurch bleibt ein späterer Ausbau ohne Umbau der CE möglich.")
    w("4. Abhängigkeiten beachten: Ein Paket setzt die genannten Pakete voraus.")
    w("")
    w("**Aufwand** (grobe Schätzung in Personentagen für Backend + Frontend + Tests auf dem fertigen CE-Fundament, ±50 %): "
      + ", ".join(f"**{k}** {v}" for k, v in EFFORT.items()) + ". "
      "Die Schätzung ist eine Orientierung für die Priorisierung, keine Zusage; die Detailplanung je Paket erfolgt erst kurz vor der Umsetzung.")
    w("")
    w("**Plan im Original:** niedrigster Plan, ab dem ein Feature des Pakets in Plane verfügbar ist (laut Matrix). In der Zielplattform gibt es keine Plan-Stufen (ADR-001); die Angabe dient nur der Einordnung.")
    w("")
    w("## Übersicht")
    w("")
    w("| Bereich | Pakete | davon 🧱 | S | M | L | XL |")
    w("|---|---|---|---|---|---|---|")
    for gid, gname, pkgs in GROUPS:
        cnt = {k: sum(1 for p in pkgs if p[2] == k) for k in EFFORT}
        w(f"| {gid} {gname} | {len(pkgs)} | {sum(1 for p in pkgs if p[3])} | " + " | ".join(str(cnt[k]) for k in EFFORT) + " |")
    w("")

    order = {"Commercial-Free": 0, "Pro": 1, "Business": 2, "Enterprise": 3, "Cloud-only": 4, "unklar": 5}
    for gid, gname, pkgs in GROUPS:
        w(f"## {gid} – {gname}")
        w("")
        w("| ✓ | Prio | Paket | Aufwand | 🧱 | Plan im Original | Setzt voraus |")
        w("|---|---|---|---|---|---|---|")
        for pid, name, eff, struct, deps, hint, ids in pkgs:
            plans = sorted({feats[i]["min_plan"] for i in ids}, key=lambda p: order.get(p, 9)) or ["neu (ADR-007)"]
            w(f"| [ ] | | **{pid}** {name} | {eff} ({EFFORT[eff]}) | {'🧱' if struct else ''} | {', '.join(plans)} | {deps} |")
        w("")
        for pid, name, eff, struct, deps, hint, ids in pkgs:
            w(f"<details><summary><b>{pid}</b> – {len(ids)} Features</summary>")
            w("")
            if hint:
                w(f"_Hinweis:_ {hint}")
                w("")
            for i in ids:
                f = feats[i]
                w(f"- [ ] `{i}` {f['name']} — Plan: {f['min_plan']} · CE: {f['ce_status']} · Konfidenz: {f['confidence']} · Detail: {f['doc']}")
            w("")
            w("</details>")
            w("")

    w("## Entfällt (ADR-001 / ADR-004 / ADR-007 / ADR-008)")
    w("")
    w("Diese Einträge sind Lizenz-, Billing-, Kontingent- oder Hersteller-Betriebsmechanik bzw. Funktionen, die durch Forgejo (Paket F2) oder Keycloak (ADR-008) ersetzt werden.")
    w("")
    w("| ID | Feature | Grund |")
    w("|---|---|---|")
    for i in sorted(DROPPED):
        w(f"| `{i}` | {feats[i]['name']} | {DROPPED[i]} |")
    w("")
    w("## Prüfsumme")
    w("")
    w(f"- Features in der Matrix: {len(feats)}")
    w(f"- Zugeordnet zu Paketen: {len(seen)}")
    w(f"- Entfällt: {len(DROPPED)}")
    w(f"- Pakete: {n_pkg}, davon strukturrelevant: {sum(1 for _, _, p in GROUPS for x in p if x[3])}")
    w("")
    w("_Erzeugt mit `migration/_werkzeuge/paid-auswahl/build.py`; das Skript prüft, dass jede EE-ID genau einmal vorkommt._")
    open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print(f"ok: {len(seen)} zugeordnet, {len(DROPPED)} entfallen, {n_pkg} Pakete -> {OUT}")


if __name__ == "__main__":
    main()
