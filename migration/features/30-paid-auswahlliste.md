# Auswahlliste der Bezahl-Features

Diese Liste dient der Entscheidung, **welche Bezahl-Features nach der Community Edition umgesetzt werden** und in welcher Reihenfolge. Sie fasst alle 246 Features aus [29-paid-feature-matrix.md](29-paid-feature-matrix.md) zu 68 Paketen zusammen. 28 Features entfallen nach ADR-001/ADR-004 (Lizenz, Billing, Hersteller-Betrieb) , ADR-007 (GitHub/GitLab/Bitbucket, ersetzt durch Forgejo) bzw. ADR-008 (SSO, LDAP, 2FA, Passkeys, Password Policy, Domains – übernimmt Keycloak) (siehe Abschnitt „Entfällt“).

## So wird die Liste benutzt

1. Pakete ankreuzen (`[x]`), die gebraucht werden. Einzelne Features innerhalb eines Pakets können ebenfalls abgewählt werden.
2. Optional in der Spalte **Prio** eine Reihenfolge vergeben (1 = zuerst).
3. Pakete mit 🧱 **strukturrelevant** wirken auf das Fundament der CE. Ihre Erweiterungspunkte werden im Architektur-Rahmen in jedem Fall vorgesehen, auch wenn das Paket selbst erst später oder gar nicht umgesetzt wird. Dadurch bleibt ein späterer Ausbau ohne Umbau der CE möglich.
4. Abhängigkeiten beachten: Ein Paket setzt die genannten Pakete voraus.

**Aufwand** (grobe Schätzung in Personentagen für Backend + Frontend + Tests auf dem fertigen CE-Fundament, ±50 %): **S** 2–5 PT, **M** 5–15 PT, **L** 15–40 PT, **XL** 40–100 PT. Die Schätzung ist eine Orientierung für die Priorisierung, keine Zusage; die Detailplanung je Paket erfolgt erst kurz vor der Umsetzung.

**Plan im Original:** niedrigster Plan, ab dem ein Feature des Pakets in Plane verfügbar ist (laut Matrix). In der Zielplattform gibt es keine Plan-Stufen (ADR-001); die Angabe dient nur der Einordnung.

## Übersicht

| Bereich | Pakete | davon 🧱 | S | M | L | XL |
|---|---|---|---|---|---|---|
| A Work Management | 17 | 4 | 3 | 7 | 6 | 1 |
| B Planung, Insights, Teams | 8 | 2 | 1 | 3 | 3 | 1 |
| C Workflows, Automationen, Templates | 6 | 2 | 0 | 2 | 3 | 1 |
| D Wissen: Pages & Wiki | 12 | 2 | 1 | 6 | 3 | 2 |
| E Sicherheit & Administration | 5 | 2 | 0 | 3 | 1 | 1 |
| F Integrationen & Importer | 9 | 2 | 0 | 2 | 6 | 1 |
| G Plane AI | 3 | 1 | 0 | 0 | 2 | 1 |
| H Plattform, API & Betrieb | 8 | 2 | 0 | 3 | 4 | 1 |

## A – Work Management

| ✓ | Prio | Paket | Aufwand | 🧱 | Plan im Original | Setzt voraus |
|---|---|---|---|---|---|---|
| [ ] | | **A1** Work-Item-Types & Custom Properties (Projekt-Ebene) | XL (40–100 PT) | 🧱 | Pro | – |
| [ ] | | **A2** Workspace-weite Types/Properties, Typ-Hierarchie, Roll-ups, Property Contexts | L (15–40 PT) | 🧱 | Business, Enterprise | A1 |
| [ ] | | **A3** Epics (inkl. Fortschritt, Updates, Conversions) | M (5–15 PT) |  | Pro, unklar | A1 |
| [ ] | | **A4** Initiatives inkl. Labels, Checkpoints/Updates | M (5–15 PT) |  | Pro | A3 |
| [ ] | | **A5** Milestones | S (2–5 PT) |  | Pro | – |
| [ ] | | **A6** Releases (Tags, Labels, Links, Changelog) | M (5–15 PT) |  | Business | – |
| [ ] | | **A7** Customers inkl. Requests und Properties | L (15–40 PT) |  | Business | A1 (Property-Engine) |
| [ ] | | **A8** Bulk Ops, Transfers, projektübergreifende Kopien | M (5–15 PT) |  | Pro | – |
| [ ] | | **A9** Relationen & Abhängigkeiten (Gantt-Dependencies, Custom Relations, Implements, projektübergreifende Sub-Items) | L (15–40 PT) | 🧱 | Pro, Enterprise, unklar | – |
| [ ] | | **A10** Time Tracking, Worklogs, Timesheets, Timesheet-Approvals | M (5–15 PT) |  | Pro, Business | – |
| [ ] | | **A11** Advanced Estimates (Zeit-Schätzungen, Systemwechsel) | S (2–5 PT) |  | Pro | – |
| [ ] | | **A12** Module Overview & Auto-Assignment | M (5–15 PT) |  | Pro | – |
| [ ] | | **A13** Projekt-Organisation (Private/Secret Projects, Project States, Project Labels, Overview, Updates) | L (15–40 PT) |  | Pro, unklar | – |
| [ ] | | **A14** Baselines & Deviations, Custom SLAs | L (15–40 PT) |  | Business | – |
| [ ] | | **A15** Intake-Erweiterungen (Intake Forms, E-Mail-Intake, Intake Assignees) | L (15–40 PT) |  | Business | – |
| [ ] | | **A16** Votes und Kommentar-Antworten an Work Items | S (2–5 PT) |  | unklar | – |
| [ ] | | **A17** Workspace Governance für States und Labels | M (5–15 PT) | 🧱 | Enterprise | – |

<details><summary><b>A1</b> – 6 Features</summary>

_Hinweis:_ Erweitert Work-Item-Modell, Filter-/Gruppierungs-Engine, Spreadsheet, API. Basis für Epics, Customers, Templates, Importer mit Custom Props.

- [ ] `EE-P04-001` Work Item Types auf Projekt-Ebene (Name, Beschreibung, Icon, Farbe, Default-Typ, aktiv/inaktiv, Typwechsel) — Plan: Pro · CE: teilweise im CE · Konfidenz: hoch · Detail: migration/features/23-paid-work-management.md#WM-01; migration/features/20-paid-spuren-im-repo.md#PF-05; migration/features/21-paid-api-referenz-developer-docs.md#F08
- [ ] `EE-P04-003` Custom Properties auf Projekt-Ebene (Property-Engine, Werte am Work Item) — Plan: Pro · CE: Stub/UI-Hülle im CE · Konfidenz: hoch · Detail: migration/features/23-paid-work-management.md#WM-03; migration/features/20-paid-spuren-im-repo.md#PF-06; migration/features/21-paid-api-referenz-developer-docs.md#F09
- [ ] `EE-P04-004` Property-Typen (Text, Number, Dropdown, Boolean, Date, Member picker, Relation, URL, Email, File, Release picker, Formula) — Plan: Pro · CE: fehlt · Konfidenz: mittel · Detail: migration/features/23-paid-work-management.md#WM-04
- [ ] `EE-P04-005` Pflichtfelder, Default-Werte, Aktiv/Inaktiv und Optionen-Verwaltung von Properties — Plan: Pro · CE: fehlt · Konfidenz: mittel · Detail: migration/features/23-paid-work-management.md#WM-05
- [ ] `EE-P04-006` Formula-Properties (`property_type=FORMULA`) — Plan: Pro · CE: fehlt · Konfidenz: mittel · Detail: migration/features/23-paid-work-management.md#WM-06; migration/features/21-paid-api-referenz-developer-docs.md#F10
- [ ] `EE-P02-001` Work-Item-Type-Schema-Endpunkt (Standard- und Custom-Felder eines Typs für LLM/MCP) — Plan: Pro · CE: fehlt · Konfidenz: hoch · Detail: migration/features/21-paid-api-referenz-developer-docs.md#F11

</details>

<details><summary><b>A2</b> – 4 Features</summary>

_Hinweis:_ Enterprise-Funktionen; Governance-Regeln irreversibel.

- [ ] `EE-P04-002` Work-Item-Type-Hierarchie (Level, Parent/Child-Regeln, Bruch-Validierung; irreversibel) — Plan: Enterprise · CE: teilweise im CE · Konfidenz: mittel · Detail: migration/features/23-paid-work-management.md#WM-02; migration/features/20-paid-spuren-im-repo.md#PF-08
- [ ] `EE-P04-007` Workspace-Level Properties und Workspace-Level Types (Workspace-Modus: Katalog, Import, Link/Unlink, Governance) — Plan: Enterprise · CE: fehlt · Konfidenz: mittel · Detail: migration/features/23-paid-work-management.md#WM-07; migration/features/20-paid-spuren-im-repo.md#PF-07; migration/features/21-paid-api-referenz-developer-docs.md#F43
- [ ] `EE-P04-008` Roll-ups (Property-Aggregation) — Plan: Business · CE: fehlt · Konfidenz: niedrig · Detail: migration/features/23-paid-work-management.md#WM-08
- [ ] `EE-P04-046` Property Contexts (kontextabhängige Regeln einer Workspace-Property je Projekt-/Typ-Menge) — Plan: Enterprise · CE: fehlt · Konfidenz: niedrig · Detail: migration/features/23-paid-work-management.md#WM-52; migration/features/21-paid-api-referenz-developer-docs.md#F40

</details>

<details><summary><b>A3</b> – 3 Features</summary>

- [ ] `EE-P04-009` Epics (Work-Item-Typ Epic, Epic-Kinder, Epic-API) — Plan: Pro · CE: Stub/UI-Hülle im CE · Konfidenz: hoch · Detail: migration/features/23-paid-work-management.md#WM-09; migration/features/20-paid-spuren-im-repo.md#PF-14; migration/features/21-paid-api-referenz-developer-docs.md#F01
- [ ] `EE-P04-010` Epic-Fortschritt und Epic-Updates — Plan: Pro · CE: Stub/UI-Hülle im CE · Konfidenz: mittel · Detail: migration/features/23-paid-work-management.md#WM-10
- [ ] `EE-P04-021` Conversions (Work Item ↔ Epic; Bulk-Conversions) [coming soon] — Plan: unklar · CE: Stub/UI-Hülle im CE · Konfidenz: niedrig · Detail: migration/features/23-paid-work-management.md#WM-24

</details>

<details><summary><b>A4</b> – 3 Features</summary>

- [ ] `EE-P04-011` Initiatives (Bündelung von Epics/Projekten bzw. Work Items) [Matrix coming soon, ausgeliefert] — Plan: Pro · CE: Stub/UI-Hülle im CE · Konfidenz: hoch · Detail: migration/features/23-paid-work-management.md#WM-11; migration/features/20-paid-spuren-im-repo.md#PF-15; migration/features/21-paid-api-referenz-developer-docs.md#F02
- [ ] `EE-P04-012` Initiative-Labels — Plan: Pro · CE: fehlt · Konfidenz: hoch · Detail: migration/features/23-paid-work-management.md#WM-12; migration/features/21-paid-api-referenz-developer-docs.md#F03
- [ ] `EE-P04-013` Checkpoints und Updates an Projekten/Epics/Initiativen [coming soon] — Plan: Pro · CE: Stub/UI-Hülle im CE · Konfidenz: niedrig · Detail: migration/features/23-paid-work-management.md#WM-13; migration/features/20-paid-spuren-im-repo.md#PF-16

</details>

<details><summary><b>A5</b> – 1 Features</summary>

- [ ] `EE-P04-014` Milestones (Projekt-Meilensteine, Work-Item-Zuordnung) — Plan: Pro · CE: Stub/UI-Hülle im CE · Konfidenz: hoch · Detail: migration/features/23-paid-work-management.md#WM-14; migration/features/21-paid-api-referenz-developer-docs.md#F06; migration/features/20-paid-spuren-im-repo.md#PF-17

</details>

<details><summary><b>A6</b> – 1 Features</summary>

- [ ] `EE-P04-015` Releases (Workspace- und Projekt-Releases, Tags, Labels, Links, Kommentare, Changelog) — Plan: Business · CE: fehlt · Konfidenz: hoch · Detail: migration/features/23-paid-work-management.md#WM-15; migration/features/21-paid-api-referenz-developer-docs.md#F24; migration/features/20-paid-spuren-im-repo.md#PF-42

</details>

<details><summary><b>A7</b> – 3 Features</summary>

- [ ] `EE-P04-016` Customers (Kundenprofile, Work-Item-Verknüpfung) — Plan: Business · CE: fehlt · Konfidenz: hoch · Detail: migration/features/23-paid-work-management.md#WM-16; migration/features/20-paid-spuren-im-repo.md#PF-41; migration/features/21-paid-api-referenz-developer-docs.md#F04
- [ ] `EE-P04-017` Customer Requests — Plan: Business · CE: fehlt · Konfidenz: mittel · Detail: migration/features/23-paid-work-management.md#WM-17; migration/features/21-paid-api-referenz-developer-docs.md#F04
- [ ] `EE-P04-018` Customer Properties — Plan: Business · CE: fehlt · Konfidenz: mittel · Detail: migration/features/23-paid-work-management.md#WM-18; migration/features/21-paid-api-referenz-developer-docs.md#F04

</details>

<details><summary><b>A8</b> – 3 Features</summary>

- [ ] `EE-P04-019` Bulk Ops (Mehrfachauswahl, Property-Änderung, Archivieren, Löschen, Abonnieren) — Plan: Pro · CE: Stub/UI-Hülle im CE · Konfidenz: hoch · Detail: migration/features/23-paid-work-management.md#WM-22; migration/features/20-paid-spuren-im-repo.md#PF-02
- [ ] `EE-P04-020` Work Item Transfers (Work Item in anderes Projekt oder anderen Cycle verschieben) — Plan: Pro · CE: teilweise im CE · Konfidenz: mittel · Detail: migration/features/23-paid-work-management.md#WM-23; migration/features/20-paid-spuren-im-repo.md#PF-11
- [ ] `EE-P04-022` Kopie eines Work Items in ein anderes Projekt („Duplicate work items and epics across projects“) — Plan: Pro · CE: Stub/UI-Hülle im CE · Konfidenz: mittel · Detail: migration/features/23-paid-work-management.md#WM-25; migration/features/20-paid-spuren-im-repo.md#PF-38

</details>

<details><summary><b>A9</b> – 4 Features</summary>

_Hinweis:_ Relationstypen als Katalog statt fester Enum-Liste anlegen.

- [ ] `EE-P04-023` Dependencies in Gantt (Starts/Finishes Before/After, Verbindungslinien, abhängige Verschiebung; Dependencies-API) — Plan: Pro · CE: teilweise im CE · Konfidenz: hoch · Detail: migration/features/23-paid-work-management.md#WM-26; migration/features/20-paid-spuren-im-repo.md#PF-09; migration/features/21-paid-api-referenz-developer-docs.md#F39
- [ ] `EE-P04-024` Custom Relations (frei definierbare Relationstypen, Workspace-Settings „Relations“) — Plan: Enterprise · CE: fehlt · Konfidenz: mittel · Detail: migration/features/23-paid-work-management.md#WM-27; migration/features/21-paid-api-referenz-developer-docs.md#F22; migration/features/20-paid-spuren-im-repo.md#PF-10
- [ ] `EE-P04-025` Eingebauter Relationstyp „Implements“ / „Implemented by“ — Plan: unklar · CE: teilweise im CE · Konfidenz: mittel · Detail: migration/features/23-paid-work-management.md#WM-53; migration/features/20-paid-spuren-im-repo.md#PF-10
- [ ] `EE-P04-044` Projektübergreifende Sub-Work-Items — Plan: unklar · CE: fehlt · Konfidenz: mittel · Detail: migration/features/23-paid-work-management.md#WM-50

</details>

<details><summary><b>A10</b> – 3 Features</summary>

- [ ] `EE-P04-028` Time Tracking und Worklogs (Zeit je Work Item, Worklogs-Tab, Tracked time) — Plan: Pro · CE: teilweise im CE · Konfidenz: hoch · Detail: migration/features/23-paid-work-management.md#WM-32; migration/features/20-paid-spuren-im-repo.md#PF-03; migration/features/21-paid-api-referenz-developer-docs.md#F07
- [ ] `EE-P04-029` Timesheets / Worklog-Downloads (Workspace-Settings „Worklogs“) — Plan: Pro · CE: fehlt · Konfidenz: mittel · Detail: migration/features/23-paid-work-management.md#WM-33
- [ ] `EE-P04-030` Timesheet-Approvals — Plan: Business · CE: fehlt · Konfidenz: niedrig · Detail: migration/features/23-paid-work-management.md#WM-34

</details>

<details><summary><b>A11</b> – 1 Features</summary>

- [ ] `EE-P04-031` Advanced Estimates (System `time`, Bearbeiten, Umsortieren, Systemwechsel) — Plan: Pro · CE: teilweise im CE · Konfidenz: hoch · Detail: migration/features/23-paid-work-management.md#WM-35; migration/features/20-paid-spuren-im-repo.md#PF-01; migration/features/21-paid-api-referenz-developer-docs.md#F21

</details>

<details><summary><b>A12</b> – 2 Features</summary>

- [ ] `EE-P04-026` Module Overview (Übersicht mit Details und Fortschrittsdiagrammen je Modul) — Plan: Pro · CE: teilweise im CE · Konfidenz: niedrig · Detail: migration/features/23-paid-work-management.md#WM-30; migration/features/20-paid-spuren-im-repo.md#PF-18
- [ ] `EE-P04-027` Auto-assignment in Modules (Zuweisungsregeln Linear, Round Robin, Capacity) — Plan: Pro · CE: fehlt · Konfidenz: niedrig · Detail: migration/features/23-paid-work-management.md#WM-31; migration/features/20-paid-spuren-im-repo.md#PF-19; migration/features/25-paid-workflows-automation-templates.md#F29

</details>

<details><summary><b>A13</b> – 5 Features</summary>

- [ ] `EE-P04-032` Public, Private und Secret Projects (Stufe „Private mit Beitrittsgenehmigung“) — Plan: Pro · CE: teilweise im CE · Konfidenz: mittel · Detail: migration/features/23-paid-work-management.md#WM-36; migration/features/20-paid-spuren-im-repo.md#PF-20
- [ ] `EE-P04-033` State of Projects / Project States (Project Grouping) — Plan: Pro · CE: fehlt · Konfidenz: mittel · Detail: migration/features/23-paid-work-management.md#WM-37; migration/features/20-paid-spuren-im-repo.md#PF-21; migration/features/21-paid-api-referenz-developer-docs.md#F18
- [ ] `EE-P04-034` Project Labels — Plan: unklar · CE: fehlt · Konfidenz: mittel · Detail: migration/features/23-paid-work-management.md#WM-38; migration/features/20-paid-spuren-im-repo.md#PF-21; migration/features/21-paid-api-referenz-developer-docs.md#F18
- [ ] `EE-P04-035` Project Overview (Projekt-Übersichtsseite: Snapshot, Links, Attachments, Milestones) [coming soon] — Plan: Pro · CE: Stub/UI-Hülle im CE · Konfidenz: mittel · Detail: migration/features/23-paid-work-management.md#WM-39; migration/features/20-paid-spuren-im-repo.md#PF-22
- [ ] `EE-P04-036` Project Updates (Status-Updates On-Track/Off-Track/At-Risk mit Kommentaren/Reaktionen) [coming soon] — Plan: Pro · CE: Stub/UI-Hülle im CE · Konfidenz: mittel · Detail: migration/features/23-paid-work-management.md#WM-40; migration/features/20-paid-spuren-im-repo.md#PF-23; migration/features/21-paid-api-referenz-developer-docs.md#F27

</details>

<details><summary><b>A14</b> – 2 Features</summary>

_Hinweis:_ Benötigt Zeitreihen/Snapshots bzw. SLA-Timer im Job-System.

- [ ] `EE-P04-037` Baselines And Deviations — Plan: Business · CE: fehlt · Konfidenz: niedrig · Detail: migration/features/23-paid-work-management.md#WM-42; migration/features/20-paid-spuren-im-repo.md#PF-32
- [ ] `EE-P04-038` Custom SLAs (SLA-Matrizen für zeitkritische Work Items) — Plan: Business · CE: fehlt · Konfidenz: niedrig · Detail: migration/features/23-paid-work-management.md#WM-43; migration/features/20-paid-spuren-im-repo.md#PF-35

</details>

<details><summary><b>A15</b> – 3 Features</summary>

_Hinweis:_ E-Mail-Intake braucht SMTP-Empfangsdienst.

- [ ] `EE-P04-039` Intake Forms (extern erreichbare Web-Formulare) — Plan: Business · CE: Stub/UI-Hülle im CE · Konfidenz: hoch · Detail: migration/features/23-paid-work-management.md#WM-44; migration/features/20-paid-spuren-im-repo.md#PF-36
- [ ] `EE-P04-040` Intake Assignees / Intake responsibility (Standard-Bearbeiter, Benachrichtigung) — Plan: Business · CE: teilweise im CE · Konfidenz: mittel · Detail: migration/features/23-paid-work-management.md#WM-45; migration/features/20-paid-spuren-im-repo.md#PF-34
- [ ] `EE-P04-041` Emails For Intake (E-Mail-Adresse je Projekt-Intake) [Matrix coming soon, ausgeliefert] — Plan: Business · CE: Stub/UI-Hülle im CE · Konfidenz: hoch · Detail: migration/features/23-paid-work-management.md#WM-46; migration/features/20-paid-spuren-im-repo.md#PF-37; migration/features/21-paid-api-referenz-developer-docs.md#F28; migration/features/22-paid-architektur-selfhosting-dienste.md#P03-F23

</details>

<details><summary><b>A16</b> – 2 Features</summary>

- [ ] `EE-P04-042` Work-Item-Votes in der App (Up-/Downvotes an Work Items, Epics, Intake) — Plan: unklar · CE: teilweise im CE · Konfidenz: hoch · Detail: migration/features/23-paid-work-management.md#WM-48; migration/features/20-paid-spuren-im-repo.md#PF-40
- [ ] `EE-P04-043` Kommentar-Antworten (Reply-Threads unter Work-Item-Kommentaren) — Plan: unklar · CE: teilweise im CE · Konfidenz: mittel · Detail: migration/features/23-paid-work-management.md#WM-49; migration/features/20-paid-spuren-im-repo.md#PF-39

</details>

<details><summary><b>A17</b> – 1 Features</summary>

- [ ] `EE-P04-045` Workspace Governance für States und Labels (Label-Scopes, Sperre der Projekt-Bearbeitung) — Plan: Enterprise · CE: teilweise im CE · Konfidenz: mittel · Detail: migration/features/23-paid-work-management.md#WM-51

</details>

## B – Planung, Insights, Teams

| ✓ | Prio | Paket | Aufwand | 🧱 | Plan im Original | Setzt voraus |
|---|---|---|---|---|---|---|
| [ ] | | **B1** Teamspaces (inkl. Work Items, Views, Pages, Kommentare, Member-Kontext, Feature-Schalter) | XL (40–100 PT) | 🧱 | Pro, unklar | – |
| [ ] | | **B2** Dashboards & Widgets (inkl. Filter, Intake-/Property-Widgets, Einbettung in Pages) | L (15–40 PT) |  | Pro, Enterprise, unklar | Charts-Bibliothek |
| [ ] | | **B3** Analytics-Erweiterungen, Custom Reports, Insights, Time Capsule | L (15–40 PT) |  | Pro, Business, unklar | – |
| [ ] | | **B4** Cycle-Erweiterungen (Progress Charts, Reports, Auto-Schedule, Auto-Rollover, Active Cycles, Parallel Cycles, Complete/Start/End, Teamspace Cycles) | M (5–15 PT) |  | Pro, Business, unklar | B1 für Teamspace Cycles |
| [ ] | | **B5** Shared Views und Publish Views | M (5–15 PT) |  | Pro | – |
| [ ] | | **B6** Erweiterte Filter, PQL, Text-to-PQL, Advanced Search | L (15–40 PT) | 🧱 | Pro, Enterprise | G1 für Text-to-PQL |
| [ ] | | **B7** Scheduled Comms (geplante Berichte/Nachrichten) | M (5–15 PT) |  | Business | Job-System |
| [ ] | | **B8** Home-/Navigations-Erweiterungen, Product Tour | S (2–5 PT) |  | unklar | – |

<details><summary><b>B1</b> – 7 Features</summary>

_Hinweis:_ Neue Sichtbarkeitsebene zwischen Workspace und Projekt.

- [ ] `EE-P05-001` Teamspaces (Anlegen/Ändern/Löschen, Lead, Beschreibung, Logo, Mitglieder, Projekte) — Plan: Pro · CE: Stub/UI-Hülle im CE · Konfidenz: hoch · Detail: migration/features/24-paid-planung-insights-teams.md#P05-01; migration/features/20-paid-spuren-im-repo.md#PF-30; migration/features/21-paid-api-referenz-developer-docs.md#F05
- [ ] `EE-P05-002` Teamspace-Work-Items (Tabs „Team“/„Project“, Gruppierung „Team project“) — Plan: Pro · CE: Stub/UI-Hülle im CE · Konfidenz: mittel · Detail: migration/features/24-paid-planung-insights-teams.md#P05-02
- [ ] `EE-P05-003` Teamspace-Projekt-Work-Items — Plan: Pro · CE: Stub/UI-Hülle im CE · Konfidenz: mittel · Detail: migration/features/24-paid-planung-insights-teams.md#P05-03
- [ ] `EE-P05-004` Teamspace-Views und Teamspace-Pages — Plan: Pro · CE: Stub/UI-Hülle im CE · Konfidenz: mittel · Detail: migration/features/24-paid-planung-insights-teams.md#P05-04; migration/features/26-paid-wissen-pages-wiki.md#P07-17
- [ ] `EE-P05-006` Teamspace-Kommentare/-Updates — Plan: unklar · CE: Stub/UI-Hülle im CE · Konfidenz: mittel · Detail: migration/features/24-paid-planung-insights-teams.md#P05-06
- [ ] `EE-P05-007` Workspace-Feature „Teamspaces“ (`teams` / `is_teams_enabled`) inkl. Settings-Seite — Plan: Pro · CE: fehlt · Konfidenz: hoch · Detail: migration/features/24-paid-planung-insights-teams.md#P05-07
- [ ] `EE-P05-008` Teamspace-bezogene Member-Auswahl, Suche, Realtime-Kontext — Plan: Pro · CE: Stub/UI-Hülle im CE · Konfidenz: mittel · Detail: migration/features/24-paid-planung-insights-teams.md#P05-08

</details>

<details><summary><b>B2</b> – 5 Features</summary>

- [ ] `EE-P05-009` Dashboards (eigene Dashboards) — Plan: Pro · CE: Stub/UI-Hülle im CE · Konfidenz: hoch · Detail: migration/features/24-paid-planung-insights-teams.md#P05-09; migration/features/20-paid-spuren-im-repo.md#PF-45
- [ ] `EE-P05-010` Dashboard-Widgets (Typen, Chart-Modelle, Achsen/Metriken, Farbpaletten) — Plan: Pro · CE: teilweise im CE · Konfidenz: mittel · Detail: migration/features/24-paid-planung-insights-teams.md#P05-10
- [ ] `EE-P05-011` Dashboard-Filter inkl. PQL (Ebenen source, quick, widget) — Plan: unklar · CE: fehlt · Konfidenz: niedrig · Detail: migration/features/24-paid-planung-insights-teams.md#P05-11
- [ ] `EE-P05-012` Dashboard-Widgets für Intake und Custom Properties — Plan: unklar · CE: fehlt · Konfidenz: niedrig · Detail: migration/features/24-paid-planung-insights-teams.md#P05-12
- [ ] `EE-P05-013` Dashboard-Widgets in Pages einbetten („Link dashboard widgets“-Block) — Plan: Enterprise · CE: fehlt · Konfidenz: niedrig · Detail: migration/features/24-paid-planung-insights-teams.md#P05-13; migration/features/26-paid-wissen-pages-wiki.md#P07-42

</details>

<details><summary><b>B3</b> – 4 Features</summary>

- [ ] `EE-P05-014` Insights (Hindsight, On-demand insights, Foresights) [coming soon] — Plan: Pro · CE: fehlt · Konfidenz: niedrig · Detail: migration/features/24-paid-planung-insights-teams.md#P05-14; migration/features/20-paid-spuren-im-repo.md#PF-48
- [ ] `EE-P05-015` Erweiterte Analytics-Tabs (Cycles, Modules, Intake, Projects/Users) mit Tab-Gating — Plan: unklar · CE: teilweise im CE · Konfidenz: mittel · Detail: migration/features/24-paid-planung-insights-teams.md#P05-15; migration/features/20-paid-spuren-im-repo.md#PF-50
- [ ] `EE-P05-016` Custom Reports (Berichte nach beliebiger Dimension/Metrik) [coming soon] — Plan: Business · CE: fehlt · Konfidenz: mittel · Detail: migration/features/24-paid-planung-insights-teams.md#P05-16; migration/features/20-paid-spuren-im-repo.md#PF-50
- [ ] `EE-P05-017` Time Capsule (Point-in-time-Snapshots) [coming soon] — Plan: Business · CE: fehlt · Konfidenz: niedrig · Detail: migration/features/24-paid-planung-insights-teams.md#P05-17; migration/features/20-paid-spuren-im-repo.md#PF-51

</details>

<details><summary><b>B4</b> – 8 Features</summary>

- [ ] `EE-P05-005` Teamspace Cycles (mehrere Cycles mehrerer Projekte gleichzeitig) — Plan: Business · CE: fehlt · Konfidenz: niedrig · Detail: migration/features/24-paid-planung-insights-teams.md#P05-05; migration/features/20-paid-spuren-im-repo.md#PF-31
- [ ] `EE-P05-018` Progress Charts (Cycle-Fortschritt v2, Scope-Linie, Burn-down/Burn-up) — Plan: Pro · CE: teilweise im CE · Konfidenz: hoch · Detail: migration/features/24-paid-planung-insights-teams.md#P05-19; migration/features/20-paid-spuren-im-repo.md#PF-46
- [ ] `EE-P05-019` Cycle Reports (On-demand, Permalinks) — Plan: Pro · CE: teilweise im CE · Konfidenz: niedrig · Detail: migration/features/24-paid-planung-insights-teams.md#P05-20; migration/features/20-paid-spuren-im-repo.md#PF-47
- [ ] `EE-P05-020` Auto-schedule Cycles (wiederkehrende Cycles) — Plan: Business · CE: fehlt · Konfidenz: niedrig · Detail: migration/features/24-paid-planung-insights-teams.md#P05-21; migration/features/23-paid-work-management.md#WM-29; migration/features/20-paid-spuren-im-repo.md#PF-13; migration/features/25-paid-workflows-automation-templates.md#F27
- [ ] `EE-P05-021` Auto-transfer Cycle Work items / Auto-Rollover — Plan: Pro · CE: teilweise im CE · Konfidenz: mittel · Detail: migration/features/24-paid-planung-insights-teams.md#P05-22; migration/features/23-paid-work-management.md#WM-28; migration/features/20-paid-spuren-im-repo.md#PF-12; migration/features/25-paid-workflows-automation-templates.md#F28
- [ ] `EE-P05-022` Workspace-weite Active Cycles — Plan: Pro · CE: Stub/UI-Hülle im CE · Konfidenz: hoch · Detail: migration/features/24-paid-planung-insights-teams.md#P05-23; migration/features/20-paid-spuren-im-repo.md#PF-04
- [ ] `EE-P05-023` Parallel Cycles (mehrere aktive Cycles je Projekt) — Plan: unklar · CE: fehlt · Konfidenz: mittel · Detail: migration/features/24-paid-planung-insights-teams.md#P05-24
- [ ] `EE-P05-024` Cycle-Aktionen „Complete“, manuelles Starten/Beenden und Archivieren laufender Cycles — Plan: unklar · CE: fehlt · Konfidenz: mittel · Detail: migration/features/24-paid-planung-insights-teams.md#P05-25

</details>

<details><summary><b>B5</b> – 2 Features</summary>

- [ ] `EE-P05-025` Shared Views (View mit ausgewählten Mitgliedern teilen) — Plan: Pro · CE: fehlt · Konfidenz: mittel · Detail: migration/features/24-paid-planung-insights-teams.md#P05-27; migration/features/20-paid-spuren-im-repo.md#PF-43
- [ ] `EE-P05-026` Publish Views (View öffentlich ins Internet stellen) — Plan: Pro · CE: teilweise im CE · Konfidenz: hoch · Detail: migration/features/24-paid-planung-insights-teams.md#P05-28; migration/features/20-paid-spuren-im-repo.md#PF-44

</details>

<details><summary><b>B6</b> – 4 Features</summary>

_Hinweis:_ Filter-Engine von Anfang an mit AND/OR/NOT und Operatoren bauen.

- [ ] `EE-P05-027` PQL (Plane Query Language) — Plan: Enterprise · CE: Stub/UI-Hülle im CE · Konfidenz: mittel · Detail: migration/features/24-paid-planung-insights-teams.md#P05-29; migration/features/20-paid-spuren-im-repo.md#PF-52; migration/features/21-paid-api-referenz-developer-docs.md#F25
- [ ] `EE-P05-028` Operator-Kapseln und erweiterte Filteroperatoren (Negation, OR) im Filter-UI [coming soon] — Plan: Pro · CE: Stub/UI-Hülle im CE · Konfidenz: niedrig · Detail: migration/features/24-paid-planung-insights-teams.md#P05-30; migration/features/20-paid-spuren-im-repo.md#PF-52
- [ ] `EE-P05-029` Advanced Search (OpenSearch-gestützt; Fallback Postgres) — Plan: Pro · CE: fehlt · Konfidenz: hoch · Detail: migration/features/24-paid-planung-insights-teams.md#P05-31; migration/features/20-paid-spuren-im-repo.md#PF-53; migration/features/21-paid-api-referenz-developer-docs.md#F20; migration/features/22-paid-architektur-selfhosting-dienste.md#P03-F11
- [ ] `EE-P05-032` Text to PQL (natürliche Sprache → PQL, AI) — Plan: Enterprise · CE: fehlt · Konfidenz: niedrig · Detail: migration/features/24-paid-planung-insights-teams.md#P05-35

</details>

<details><summary><b>B7</b> – 1 Features</summary>

- [ ] `EE-P05-030` Scheduled Comms (geplante Berichte, Benachrichtigungen, Nachrichten an Drittsysteme) — Plan: Business · CE: fehlt · Konfidenz: niedrig · Detail: migration/features/24-paid-planung-insights-teams.md#P05-32; migration/features/20-paid-spuren-im-repo.md#PF-33

</details>

<details><summary><b>B8</b> – 2 Features</summary>

- [ ] `EE-P05-031` Home-, Your-Work- und Navigations-Erweiterungen (Widgets „New at Plane“, „Quick tutorial“, Commercial-Sidebar-Menüs) — Plan: unklar · CE: Stub/UI-Hülle im CE · Konfidenz: mittel · Detail: migration/features/24-paid-planung-insights-teams.md#P05-34
- [ ] `EE-P01-002` Product Tour / „Get started“ (geführte Touren, Demo-Projekt, Get-started-Checkliste; i18n-Namespace `tour`) — Plan: unklar · CE: fehlt · Konfidenz: mittel · Detail: migration/features/20-paid-spuren-im-repo.md#PF-102

</details>

## C – Workflows, Automationen, Templates

| ✓ | Prio | Paket | Aufwand | 🧱 | Plan im Original | Setzt voraus |
|---|---|---|---|---|---|---|
| [ ] | | **C1** Workflows (Default-Workflow, mehrere typ-spezifische, Historie, Time-in-State, Governance) | L (15–40 PT) | 🧱 | Business, Enterprise | – |
| [ ] | | **C2** Approvals (Workflow-Transitionen, Workspace/Projekt/Typ) | M (5–15 PT) |  | Business, Enterprise | C1 |
| [ ] | | **C3** Automation-Engine (Trigger, Bedingungen, Aktionen, Logs, global, zeitgesteuert, Decisions & Loops, Outbox) | XL (40–100 PT) | 🧱 | Commercial-Free, Business, Enterprise | Event/Outbox |
| [ ] | | **C4** Scripting (Plane Runner, Transition Hooks) | L (15–40 PT) |  | Enterprise | C1, C3 |
| [ ] | | **C5** Templates (Projekt, Work Item, Page, vordefinierte, Marketplace) | L (15–40 PT) |  | Pro, Business, unklar | A1, C1 für vollständige Projekt-Templates |
| [ ] | | **C6** Recurring Work Items & Auto-Reminders | M (5–15 PT) |  | Business | Job-System |

<details><summary><b>C1</b> – 5 Features</summary>

_Hinweis:_ Zentrale State-Change-Pipeline in der CE vorsehen.

- [ ] `EE-P06-001` Workflows: Default-Workflow je Projekt (erlaubte State-Wechsel, Mover/Reviewer, „Allow new work items“, Erzwingung) — Plan: Business · CE: Stub/UI-Hülle im CE · Konfidenz: hoch · Detail: migration/features/25-paid-workflows-automation-templates.md#F01; migration/features/20-paid-spuren-im-repo.md#PF-68; migration/features/21-paid-api-referenz-developer-docs.md#F42
- [ ] `EE-P06-002` Mehrere, typ-spezifische Workflows je Projekt — Plan: Enterprise · CE: Stub/UI-Hülle im CE · Konfidenz: mittel · Detail: migration/features/25-paid-workflows-automation-templates.md#F02; migration/features/21-paid-api-referenz-developer-docs.md#F42
- [ ] `EE-P06-005` Workflow-Änderungshistorie und „Reset workflow“ — Plan: Business · CE: fehlt · Konfidenz: mittel · Detail: migration/features/25-paid-workflows-automation-templates.md#F05
- [ ] `EE-P06-006` Transitions-Tab mit Time-in-State — Plan: Business · CE: fehlt · Konfidenz: mittel · Detail: migration/features/25-paid-workflows-automation-templates.md#F06
- [ ] `EE-P06-007` Workspace Governance für Workflows (Modi, Pins, effektiver Workflow) — Plan: Enterprise · CE: fehlt · Konfidenz: mittel · Detail: migration/features/25-paid-workflows-automation-templates.md#F07

</details>

<details><summary><b>C2</b> – 2 Features</summary>

- [ ] `EE-P06-003` Approval Flows an Workflow-Transitionen (Approver, `required_approvals`) — Plan: Enterprise · CE: fehlt · Konfidenz: mittel · Detail: migration/features/25-paid-workflows-automation-templates.md#F03
- [ ] `EE-P06-008` Approvals auf Workspace-, Projekt- und Work-Item-Type-Ebene (Matrix-Zeile „Approvals“) [coming soon] — Plan: Business · CE: fehlt · Konfidenz: mittel · Detail: migration/features/25-paid-workflows-automation-templates.md#F08; migration/features/20-paid-spuren-im-repo.md#PF-56; migration/features/27-paid-sicherheit-admin-lizenz.md#P08-15

</details>

<details><summary><b>C3</b> – 9 Features</summary>

_Hinweis:_ Domain-Events + Outbox in der CE vorsehen.

- [ ] `EE-P06-009` Custom Automations je Projekt (Trigger → Bedingungen → Aktionen) — Plan: Business · CE: fehlt · Konfidenz: mittel · Detail: migration/features/25-paid-workflows-automation-templates.md#F09; migration/features/20-paid-spuren-im-repo.md#PF-63; migration/features/21-paid-api-referenz-developer-docs.md#F35
- [ ] `EE-P06-010` Automation-Trigger (Work item created/updated, State changed, Assignee changed, Comment added; Scheduled) — Plan: Business · CE: fehlt · Konfidenz: mittel · Detail: migration/features/25-paid-workflows-automation-templates.md#F10
- [ ] `EE-P06-011` Automation-Bedingungen („Provided“: State, Priority, Assignees, Labels, Work item type, Created by) — Plan: Business · CE: fehlt · Konfidenz: mittel · Detail: migration/features/25-paid-workflows-automation-templates.md#F11
- [ ] `EE-P06-012` Automation-Aktionen (Change property, Add comment; Send webhook, Run script) — Plan: Business · CE: fehlt · Konfidenz: mittel · Detail: migration/features/25-paid-workflows-automation-templates.md#F12
- [ ] `EE-P06-013` Global (Workspace-)Automations („All projects“ / „Select projects“) — Plan: Enterprise · CE: fehlt · Konfidenz: mittel · Detail: migration/features/25-paid-workflows-automation-templates.md#F13; migration/features/20-paid-spuren-im-repo.md#PF-64; migration/features/21-paid-api-referenz-developer-docs.md#F35
- [ ] `EE-P06-014` Scheduled Automations (Fixed Daily/Weekly/Monthly oder Cron; Aktion Run script) — Plan: Enterprise · CE: fehlt · Konfidenz: mittel · Detail: migration/features/25-paid-workflows-automation-templates.md#F14
- [ ] `EE-P06-015` Decisions and Loops Automation [coming soon] — Plan: Business · CE: fehlt · Konfidenz: niedrig · Detail: migration/features/25-paid-workflows-automation-templates.md#F15; migration/features/20-paid-spuren-im-repo.md#PF-65
- [ ] `EE-P06-017` Automation-Ausführungslogs (Activity / Run History) — Plan: Business · CE: fehlt · Konfidenz: mittel · Detail: migration/features/25-paid-workflows-automation-templates.md#F17
- [ ] `EE-P06-018` Automation-Consumer / Outbox-Architektur (Outbox-Poller → RabbitMQ → Consumer) — Plan: Commercial-Free · CE: fehlt · Konfidenz: mittel · Detail: migration/features/25-paid-workflows-automation-templates.md#F18; migration/features/22-paid-architektur-selfhosting-dienste.md#P03-F29

</details>

<details><summary><b>C4</b> – 2 Features</summary>

_Hinweis:_ Ohne Node: JavaScript-Sandbox in .NET (z. B. Jint) nötig.

- [ ] `EE-P06-004` Transition Conditions / Workflow Hooks (pre/post, `run_script`, `send_webhook`) — Plan: Enterprise · CE: fehlt · Konfidenz: mittel · Detail: migration/features/25-paid-workflows-automation-templates.md#F04
- [ ] `EE-P06-019` Plane Runner (Scripts und Functions für Automationen, Transitionen, Cron) — Plan: Enterprise · CE: fehlt · Konfidenz: mittel · Detail: migration/features/25-paid-workflows-automation-templates.md#F19; migration/features/22-paid-architektur-selfhosting-dienste.md#P03-F28; migration/features/28-paid-integrationen-importer-ai.md#P09-F54; migration/features/20-paid-spuren-im-repo.md#PF-69

</details>

<details><summary><b>C5</b> – 5 Features</summary>

- [ ] `EE-P06-020` Project Templates (States, Workflows, Automationen, Projekteinstellungen als Vorlage) — Plan: Business · CE: Stub/UI-Hülle im CE · Konfidenz: hoch · Detail: migration/features/25-paid-workflows-automation-templates.md#F20; migration/features/23-paid-work-management.md#WM-41; migration/features/20-paid-spuren-im-repo.md#PF-26; migration/features/21-paid-api-referenz-developer-docs.md#F19
- [ ] `EE-P06-021` Work Item Templates (Projekt und Workspace, inkl. Sub-Work-Items; Templates-API) — Plan: Pro · CE: Stub/UI-Hülle im CE · Konfidenz: hoch · Detail: migration/features/25-paid-workflows-automation-templates.md#F21; migration/features/23-paid-work-management.md#WM-20; migration/features/20-paid-spuren-im-repo.md#PF-25; migration/features/21-paid-api-referenz-developer-docs.md#F37
- [ ] `EE-P06-022` Page Templates (Projekt-Pages und Wiki) — Plan: Pro · CE: fehlt · Konfidenz: hoch · Detail: migration/features/25-paid-workflows-automation-templates.md#F22; migration/features/26-paid-wissen-pages-wiki.md#P07-10; migration/features/20-paid-spuren-im-repo.md#PF-27
- [ ] `EE-P06-023` Pre-defined work item Templates [coming soon] — Plan: Pro · CE: fehlt · Konfidenz: mittel · Detail: migration/features/25-paid-workflows-automation-templates.md#F23; migration/features/23-paid-work-management.md#WM-21; migration/features/20-paid-spuren-im-repo.md#PF-24
- [ ] `EE-P06-024` Template-Marketplace (Publish, Kategorien, Verifizierung, Kopie) — Plan: unklar · CE: fehlt · Konfidenz: mittel · Detail: migration/features/25-paid-workflows-automation-templates.md#F23; migration/features/20-paid-spuren-im-repo.md#PF-28

</details>

<details><summary><b>C6</b> – 2 Features</summary>

- [ ] `EE-P06-025` Recurring Work Items — Plan: Business · CE: fehlt · Konfidenz: mittel · Detail: migration/features/25-paid-workflows-automation-templates.md#F24; migration/features/23-paid-work-management.md#WM-19; migration/features/20-paid-spuren-im-repo.md#PF-29
- [ ] `EE-P06-026` Auto-Reminders (Fälligkeits-Erinnerungen) — Plan: Business · CE: fehlt · Konfidenz: mittel · Detail: migration/features/25-paid-workflows-automation-templates.md#F26; migration/features/20-paid-spuren-im-repo.md#PF-67

</details>

## D – Wissen: Pages & Wiki

| ✓ | Prio | Paket | Aufwand | 🧱 | Plan im Original | Setzt voraus |
|---|---|---|---|---|---|---|
| [ ] | | **D1** Wiki & Collections (öffentlich/privat) | L (15–40 PT) | 🧱 | Pro, Business | – |
| [ ] | | **D2** Nested Pages & Verschieben von Pages | M (5–15 PT) | 🧱 | Pro, Business | – |
| [ ] | | **D3** Page-Versionen erweitert (Aufbewahrung, Vergleich, Highlight, Restore) | M (5–15 PT) |  | Pro, unklar | – |
| [ ] | | **D4** Realtime-Presence (Avatare, Live-Cursor) | S (2–5 PT) |  | Pro | Realtime-Server |
| [ ] | | **D5** Page-Publish & Exporte (PDF/Word/Markdown, Queue, ZIP) | L (15–40 PT) |  | Pro | – |
| [ ] | | **D6** Work-Item-Verknüpfung (Embeds, Mentions, Link Pages, erweiterte Mentions/Backlinks) | M (5–15 PT) |  | Pro, Business, unklar | – |
| [ ] | | **D7** Kommentare in Pages (inline, Page-Level, Moderation) | L (15–40 PT) |  | Business, unklar | – |
| [ ] | | **D8** Page-Sharing, Page-Labels, Page-Benachrichtigungen | M (5–15 PT) |  | Business, unklar | E5 (Rechtemodell) |
| [ ] | | **D9** Erweiterte Editor-Blöcke (Draw.io, Embeds, Attachments, Video, Columns, Tabs, Toggle, Status, Date, LaTeX, Mermaid, HTML-Artifact, TOC, Link pages, Page-Embed, Widget, Block-Links) | XL (40–100 PT) |  | Pro, Business, unklar | Editor-Port |
| [ ] | | **D10** Databases + Formulas in Pages | XL (40–100 PT) |  | Business | A1 (Property-Typen) |
| [ ] | | **D11** Advanced Pages Analytics | M (5–15 PT) |  | Business | – |
| [ ] | | **D12** Pages-Public-API | M (5–15 PT) |  | unklar | D1, D2 |

<details><summary><b>D1</b> – 3 Features</summary>

_Hinweis:_ Pages ohne Projekt im Datenmodell vorsehen.

- [ ] `EE-P07-001` Wiki (Workspace-Seiten ohne Projekt) inkl. Wiki-Home, Sidebar, Feature-Toggle — Plan: Pro · CE: Stub/UI-Hülle im CE · Konfidenz: hoch · Detail: migration/features/26-paid-wissen-pages-wiki.md#P07-01; migration/features/20-paid-spuren-im-repo.md#PF-74; migration/features/21-paid-api-referenz-developer-docs.md#F14
- [ ] `EE-P07-002` Wiki-Collections (öffentlich, Default „General“) inkl. Drag-and-drop-Reordering — Plan: Pro · CE: fehlt · Konfidenz: hoch · Detail: migration/features/26-paid-wissen-pages-wiki.md#P07-02; migration/features/20-paid-spuren-im-repo.md#PF-74
- [ ] `EE-P07-003` Private Collections (nur eingeladene Mitglieder) — Plan: Business · CE: fehlt · Konfidenz: hoch · Detail: migration/features/26-paid-wissen-pages-wiki.md#P07-03

</details>

<details><summary><b>D2</b> – 2 Features</summary>

- [ ] `EE-P07-004` Nested Pages (Unterseiten, Hierarchie, Umhängen) [Matrix coming soon, ausgeliefert] — Plan: Business · CE: teilweise im CE · Konfidenz: hoch · Detail: migration/features/26-paid-wissen-pages-wiki.md#P07-04; migration/features/20-paid-spuren-im-repo.md#PF-78
- [ ] `EE-P07-017` Moving Pages (Projekt ↔ Projekt ↔ Teamspace ↔ Wiki/Collection) — Plan: Pro · CE: Stub/UI-Hülle im CE · Konfidenz: mittel · Detail: migration/features/26-paid-wissen-pages-wiki.md#P07-19; migration/features/20-paid-spuren-im-repo.md#PF-80

</details>

<details><summary><b>D3</b> – 2 Features</summary>

- [ ] `EE-P07-005` Page-Versionen: Aufbewahrung — Plan: Pro · CE: teilweise im CE · Konfidenz: hoch · Detail: migration/features/26-paid-wissen-pages-wiki.md#P07-05; migration/features/20-paid-spuren-im-repo.md#PF-76
- [ ] `EE-P07-006` Page-Versionen: „Highlight changes“, Vergleich zweier Versionen, Server-Restore — Plan: unklar · CE: Stub/UI-Hülle im CE · Konfidenz: mittel · Detail: migration/features/26-paid-wissen-pages-wiki.md#P07-06

</details>

<details><summary><b>D4</b> – 1 Features</summary>

- [ ] `EE-P07-007` Real-time Collaboration: Presence-Avatare und Live-Cursor (CRDT-Sync selbst ist CE) — Plan: Pro · CE: teilweise im CE · Konfidenz: hoch · Detail: migration/features/26-paid-wissen-pages-wiki.md#P07-07; migration/features/20-paid-spuren-im-repo.md#PF-70

</details>

<details><summary><b>D5</b> – 2 Features</summary>

_Hinweis:_ PDF/DOCX-Erzeugung in .NET.

- [ ] `EE-P07-008` Page-Publish (öffentlicher Link, Kommentare Externer, Report) — Plan: Pro · CE: Stub/UI-Hülle im CE · Konfidenz: hoch · Detail: migration/features/26-paid-wissen-pages-wiki.md#P07-08; migration/features/20-paid-spuren-im-repo.md#PF-73
- [ ] `EE-P07-009` Page-Exports PDF/Word/Markdown, Hintergrund-Queue, ZIP inkl. Unterseiten — Plan: Pro · CE: teilweise im CE · Konfidenz: hoch · Detail: migration/features/26-paid-wissen-pages-wiki.md#P07-09; migration/features/20-paid-spuren-im-repo.md#PF-75; migration/features/22-paid-architektur-selfhosting-dienste.md#P03-F30

</details>

<details><summary><b>D6</b> – 4 Features</summary>

- [ ] `EE-P07-010` Work-Item-Embeds in Pages (Block) — Plan: Pro · CE: Stub/UI-Hülle im CE · Konfidenz: hoch · Detail: migration/features/26-paid-wissen-pages-wiki.md#P07-11; migration/features/20-paid-spuren-im-repo.md#PF-71
- [ ] `EE-P07-011` Work-Item-Mentions in Pages und „Create work item from selection“ — Plan: Business · CE: Stub/UI-Hülle im CE · Konfidenz: mittel · Detail: migration/features/26-paid-wissen-pages-wiki.md#P07-12
- [ ] `EE-P07-012` Link Pages ↔ Work Items (Pages-Sektion im Work Item; Work-Item-Pages-API) — Plan: Pro · CE: fehlt · Konfidenz: hoch · Detail: migration/features/26-paid-wissen-pages-wiki.md#P07-13; migration/features/20-paid-spuren-im-repo.md#PF-72; migration/features/21-paid-api-referenz-developer-docs.md#F13
- [ ] `EE-P07-042` Erweiterte Mentions im Document-Editor (Seiten/Projekte/Zyklen/Module) und Backlinks — Plan: unklar · CE: Stub/UI-Hülle im CE · Konfidenz: niedrig · Detail: migration/features/26-paid-wissen-pages-wiki.md#P07-47

</details>

<details><summary><b>D7</b> – 2 Features</summary>

- [ ] `EE-P07-013` Inline-Kommentare (an markiertem Text, Threads, Resolve) — Plan: Business · CE: fehlt · Konfidenz: hoch · Detail: migration/features/26-paid-wissen-pages-wiki.md#P07-14; migration/features/20-paid-spuren-im-repo.md#PF-79
- [ ] `EE-P07-014` Page-Level-Kommentare, Kommentar-Filter, Moderation (hide/unhide) — Plan: unklar · CE: fehlt · Konfidenz: mittel · Detail: migration/features/26-paid-wissen-pages-wiki.md#P07-15; migration/features/20-paid-spuren-im-repo.md#PF-79

</details>

<details><summary><b>D8</b> – 3 Features</summary>

- [ ] `EE-P07-015` Page-Sharing / Access-Control (Mitglieder, Can view/comment/edit; Listenfilter `type=shared`) — Plan: Business · CE: Stub/UI-Hülle im CE · Konfidenz: mittel · Detail: migration/features/26-paid-wissen-pages-wiki.md#P07-16; migration/features/21-paid-api-referenz-developer-docs.md#F15; migration/features/20-paid-spuren-im-repo.md#PF-80
- [ ] `EE-P07-016` Page Labels (eigene Workspace-Seitenlabels) — Plan: Business · CE: teilweise im CE · Konfidenz: hoch · Detail: migration/features/26-paid-wissen-pages-wiki.md#P07-18
- [ ] `EE-P07-040` Page-Benachrichtigungen (Freigabe-Mail, Page-Subscriber) — Plan: unklar · CE: fehlt · Konfidenz: niedrig · Detail: migration/features/26-paid-wissen-pages-wiki.md#P07-44

</details>

<details><summary><b>D9</b> – 17 Features</summary>

_Hinweis:_ Pro Block einzeln abwählbar; Draw.io als eigener Container.

- [ ] `EE-P07-019` Draw.io-Diagramme und -Boards in Pages — Plan: Business · CE: fehlt · Konfidenz: mittel · Detail: migration/features/26-paid-wissen-pages-wiki.md#P07-21; migration/features/28-paid-integrationen-importer-ai.md#P09-F59; migration/features/22-paid-architektur-selfhosting-dienste.md#P03-F31
- [ ] `EE-P07-020` Externe Embeds / Rich Cards (Iframely), Medien per URL — Plan: Pro · CE: Stub/UI-Hülle im CE · Konfidenz: hoch · Detail: migration/features/26-paid-wissen-pages-wiki.md#P07-22; migration/features/22-paid-architektur-selfhosting-dienste.md#P03-F32; migration/features/20-paid-spuren-im-repo.md#PF-81
- [ ] `EE-P07-021` Attachments in Pages (inkl. Office-Bearbeitung) — Plan: Pro · CE: Stub/UI-Hülle im CE · Konfidenz: hoch · Detail: migration/features/26-paid-wissen-pages-wiki.md#P07-23; migration/features/20-paid-spuren-im-repo.md#PF-81
- [ ] `EE-P07-022` Video-Block — Plan: Pro · CE: fehlt · Konfidenz: mittel · Detail: migration/features/26-paid-wissen-pages-wiki.md#P07-24
- [ ] `EE-P07-027` Editor-Block Columns (2/3/4 Spalten) — Plan: Pro · CE: fehlt · Konfidenz: mittel · Detail: migration/features/26-paid-wissen-pages-wiki.md#P07-30
- [ ] `EE-P07-028` Editor-Block Tabs (horizontal/vertikal) — Plan: Business · CE: fehlt · Konfidenz: mittel · Detail: migration/features/26-paid-wissen-pages-wiki.md#P07-31
- [ ] `EE-P07-029` Editor-Block Toggle (aufklappbar) — Plan: Business · CE: fehlt · Konfidenz: mittel · Detail: migration/features/26-paid-wissen-pages-wiki.md#P07-32
- [ ] `EE-P07-030` Editor-Inline Status (farbiges Label) — Plan: Pro · CE: fehlt · Konfidenz: mittel · Detail: migration/features/26-paid-wissen-pages-wiki.md#P07-33
- [ ] `EE-P07-031` Editor-Inline Date — Plan: Pro · CE: fehlt · Konfidenz: hoch · Detail: migration/features/26-paid-wissen-pages-wiki.md#P07-34
- [ ] `EE-P07-032` Block- und Inline-Gleichungen (LaTeX) — Plan: Business · CE: fehlt · Konfidenz: hoch · Detail: migration/features/26-paid-wissen-pages-wiki.md#P07-35
- [ ] `EE-P07-033` Mermaid-Diagramm-Block — Plan: unklar · CE: fehlt · Konfidenz: mittel · Detail: migration/features/26-paid-wissen-pages-wiki.md#P07-36
- [ ] `EE-P07-034` HTML-Artifact-Block (sandboxed) — Plan: Business · CE: fehlt · Konfidenz: niedrig · Detail: migration/features/26-paid-wissen-pages-wiki.md#P07-37
- [ ] `EE-P07-035` Table-of-contents-Block — Plan: Business · CE: fehlt · Konfidenz: mittel · Detail: migration/features/26-paid-wissen-pages-wiki.md#P07-38
- [ ] `EE-P07-036` „Link pages“-Block (Live-Liste von Wiki-Seiten) — Plan: Business · CE: fehlt · Konfidenz: mittel · Detail: migration/features/26-paid-wissen-pages-wiki.md#P07-39
- [ ] `EE-P07-037` Page-Embed-Block (`/page`) und „Linked page embed“ — Plan: Business · CE: fehlt · Konfidenz: mittel · Detail: migration/features/26-paid-wissen-pages-wiki.md#P07-40
- [ ] `EE-P07-038` Widget-Block (Chart aus Work-Item-Daten) — Plan: unklar · CE: fehlt · Konfidenz: niedrig · Detail: migration/features/26-paid-wissen-pages-wiki.md#P07-41
- [ ] `EE-P07-039` Block-Links (Link auf einen Block kopieren) — Plan: unklar · CE: fehlt · Konfidenz: niedrig · Detail: migration/features/26-paid-wissen-pages-wiki.md#P07-43

</details>

<details><summary><b>D10</b> – 1 Features</summary>

_Hinweis:_ Kaum öffentlich spezifiziert.

- [ ] `EE-P07-018` Databases + Formulas in Pages [coming soon] — Plan: Business · CE: fehlt · Konfidenz: niedrig · Detail: migration/features/26-paid-wissen-pages-wiki.md#P07-20; migration/features/20-paid-spuren-im-repo.md#PF-77

</details>

<details><summary><b>D11</b> – 1 Features</summary>

- [ ] `EE-P07-023` Advanced Pages Analytics (Page + Collection) [Matrix coming soon, ausgeliefert] — Plan: Business · CE: fehlt · Konfidenz: hoch · Detail: migration/features/26-paid-wissen-pages-wiki.md#P07-25; migration/features/24-paid-planung-insights-teams.md#P05-18; migration/features/20-paid-spuren-im-repo.md#PF-49

</details>

<details><summary><b>D12</b> – 1 Features</summary>

- [ ] `EE-P07-041` Pages-Public-API (v1/v2: Pages, Collections, Templates, Published Pages, Attachments, Work-Item-Pages, MCP) — Plan: unklar · CE: fehlt · Konfidenz: mittel · Detail: migration/features/26-paid-wissen-pages-wiki.md#P07-45; migration/features/21-paid-api-referenz-developer-docs.md#F33

</details>

## E – Sicherheit & Administration

| ✓ | Prio | Paket | Aufwand | 🧱 | Plan im Original | Setzt voraus |
|---|---|---|---|---|---|---|
| [ ] | | **E3** IdP Group Sync aus Keycloak-Gruppen/-Rollen (→ Workspace-/Projektrollen), SCIM optional | M (5–15 PT) | 🧱 | Enterprise | E5 |
| [ ] | | **E5** Rollenmodell (RBAC, Custom Roles, GAC) | XL (40–100 PT) | 🧱 | Business, Enterprise | – |
| [ ] | | **E6** Admin Interface, Workspace Activity Logs, Audit Logs (API) | M (5–15 PT) |  | Business, Enterprise | Event/Outbox |
| [ ] | | **E7** God-Mode-Erweiterungen (User Management, Session-Einstellungen, System Checks, Multi-Workspace-Management) | M (5–15 PT) |  | Commercial-Free, Enterprise | – |
| [ ] | | **E8** PII-/Sensitive-Data-Scanner (Argus) | L (15–40 PT) |  | unklar | – |

<details><summary><b>E3</b> – 2 Features</summary>

_Hinweis:_ LDAP, SAML/OIDC-SSO, 2FA, Passkeys, Password Policy und Domain-Regeln übernimmt Keycloak (ADR-008).

- [ ] `EE-P08-005` IdP Group Sync (OIDC-Gruppen → Workspace-/Projektrollen) — Plan: Enterprise · CE: fehlt · Konfidenz: hoch · Detail: migration/features/27-paid-sicherheit-admin-lizenz.md#P08-05; migration/features/21-paid-api-referenz-developer-docs.md#F12; migration/features/22-paid-architektur-selfhosting-dienste.md#P03-F08; migration/features/20-paid-spuren-im-repo.md#PF-98
- [ ] `EE-P08-006` SCIM-Provisioning — Plan: Enterprise · CE: fehlt · Konfidenz: niedrig · Detail: migration/features/27-paid-sicherheit-admin-lizenz.md#P08-06; migration/features/20-paid-spuren-im-repo.md#PF-98

</details>

<details><summary><b>E5</b> – 3 Features</summary>

_Hinweis:_ Berechtigungskatalog statt fester Rollenwerte bereits in der CE.

- [ ] `EE-P08-011` Rollen: System-Rollen / RBAC (Owner, Workspace Admin, Member, Guest; Projekt Admin, Contributor, Commenter, Guest) — Plan: Business · CE: teilweise im CE · Konfidenz: mittel · Detail: migration/features/27-paid-sicherheit-admin-lizenz.md#P08-11; migration/features/20-paid-spuren-im-repo.md#PF-54; migration/features/21-paid-api-referenz-developer-docs.md#F26
- [ ] `EE-P08-012` Custom Roles (benutzerdefinierte Rollen aus Permission Schemes) — Plan: Enterprise · CE: fehlt · Konfidenz: mittel · Detail: migration/features/27-paid-sicherheit-admin-lizenz.md#P08-12; migration/features/21-paid-api-referenz-developer-docs.md#F26; migration/features/22-paid-architektur-selfhosting-dienste.md#P03-F45
- [ ] `EE-P08-013` GAC – Granular Access Control (Permission Schemes, bedingte Rechte, effektive Berechtigungen) — Plan: Enterprise · CE: fehlt · Konfidenz: mittel · Detail: migration/features/27-paid-sicherheit-admin-lizenz.md#P08-13; migration/features/22-paid-architektur-selfhosting-dienste.md#P03-F45; migration/features/21-paid-api-referenz-developer-docs.md#F26

</details>

<details><summary><b>E6</b> – 3 Features</summary>

- [ ] `EE-P08-015` Admin Interface (Admin-Übersicht für Workspace- und Projekt-Einstellungen) — Plan: Business · CE: fehlt · Konfidenz: niedrig · Detail: migration/features/27-paid-sicherheit-admin-lizenz.md#P08-16; migration/features/20-paid-spuren-im-repo.md#PF-57
- [ ] `EE-P08-016` Workspace Activity Logs (filterbares Aktivitätsprotokoll des gesamten Workspace) — Plan: Business · CE: teilweise im CE · Konfidenz: mittel · Detail: migration/features/27-paid-sicherheit-admin-lizenz.md#P08-17; migration/features/24-paid-planung-insights-teams.md#P05-33; migration/features/20-paid-spuren-im-repo.md#PF-58
- [ ] `EE-P08-017` API-enabled Audit Logs / Workspace-Audit-Log (Settings + v2-API `audit-logs`) [Matrix coming soon, ausgeliefert] — Plan: Enterprise · CE: fehlt · Konfidenz: mittel · Detail: migration/features/27-paid-sicherheit-admin-lizenz.md#P08-18; migration/features/20-paid-spuren-im-repo.md#PF-59; migration/features/21-paid-api-referenz-developer-docs.md#F34; migration/features/22-paid-architektur-selfhosting-dienste.md#P03-F44

</details>

<details><summary><b>E7</b> – 4 Features</summary>

- [ ] `EE-P08-025` God Mode: User Management (Instanz-Benutzer, Instanz-Admins einladen, Suspend) — Plan: Commercial-Free · CE: teilweise im CE · Konfidenz: hoch · Detail: migration/features/27-paid-sicherheit-admin-lizenz.md#P08-27; migration/features/22-paid-architektur-selfhosting-dienste.md#P03-F03
- [ ] `EE-P08-026` God Mode: Session-Einstellungen (Session expiry, Admin session expiry) — Plan: Commercial-Free · CE: teilweise im CE · Konfidenz: hoch · Detail: migration/features/27-paid-sicherheit-admin-lizenz.md#P08-28; migration/features/22-paid-architektur-selfhosting-dienste.md#P03-F35; migration/features/22-paid-architektur-selfhosting-dienste.md#P03-F03
- [ ] `EE-P03-001` Health-Probes und God-Mode-„System checks“ (`/api/live/`, `/api/ready/`, `/api/health/` je Dienst) — Plan: Commercial-Free · CE: teilweise im CE · Konfidenz: hoch · Detail: migration/features/22-paid-architektur-selfhosting-dienste.md#P03-F34; migration/features/22-paid-architektur-selfhosting-dienste.md#P03-F03
- [ ] `EE-P01-001` Multi-Workspace-Management (zentrale Verwaltung mehrerer Workspaces einer Organisation) — Plan: Enterprise · CE: fehlt · Konfidenz: niedrig · Detail: migration/features/20-paid-spuren-im-repo.md#PF-61

</details>

<details><summary><b>E8</b> – 1 Features</summary>

- [ ] `EE-P08-027` Argus – Sensitive-Data-/PII-Scanner — Plan: unklar · CE: fehlt · Konfidenz: mittel · Detail: migration/features/27-paid-sicherheit-admin-lizenz.md#P08-29; migration/features/22-paid-architektur-selfhosting-dienste.md#P03-F33; migration/features/20-paid-spuren-im-repo.md#PF-105

</details>

## F – Integrationen & Importer

| ✓ | Prio | Paket | Aufwand | 🧱 | Plan im Original | Setzt voraus |
|---|---|---|---|---|---|---|
| [ ] | | **F1** Integrations-Framework (Connections, Webhook-Empfang, Sync-Engine) | L (15–40 PT) | 🧱 | Pro | H1 |
| [ ] | | **F2** Forgejo-Integration (ADR-007): Instanz-/Org-Verbindung, persönliche Konten, Repo↔Projekt-Mapping, bidirektionaler Issue-Sync, PR-/Commit-Automation, Status in Work Items, Branch aus Work Item, Webhooks, Importer, Forgejo-Login | XL (40–100 PT) | 🧱 | neu (ADR-007) | F1 |
| [ ] | | **F5** Slack (Verbindung, Benachrichtigungen, Slash-Command, Thread-Sync, Unfurl) | L (15–40 PT) |  | Pro | F1 |
| [ ] | | **F6** Sentry | M (5–15 PT) |  | Pro | F1 |
| [ ] | | **F7** Weitere SaaS-Connectoren (HubSpot, Cursor-Agent, Zapier, Zendesk, Freshdesk) | L (15–40 PT) |  | Pro, unklar | F1 |
| [ ] | | **F8** Importer-Framework, CSV-Import (Work Items, Mitglieder) | M (5–15 PT) |  | Commercial-Free, unklar | – |
| [ ] | | **F9** Jira-Importer (Cloud, Server/Data Center) | L (15–40 PT) |  | Commercial-Free, unklar | F8, A1 für Custom Props |
| [ ] | | **F10** Importer Linear, Asana, ClickUp, GitHub | L (15–40 PT) |  | Commercial-Free, unklar | F8 |
| [ ] | | **F11** Importer Notion, Confluence (in Pages/Wiki) | L (15–40 PT) |  | unklar | F8, D1 |

<details><summary><b>F1</b> – 1 Features</summary>

_Hinweis:_ Voraussetzung für F2, F5–F7.

- [ ] `EE-P09-001` Integrations-Framework „Silo“, Integrations-Übersicht, Workspace-/persönliche Connections [Matrix coming soon, ausgeliefert] — Plan: Pro · CE: Stub/UI-Hülle im CE · Konfidenz: mittel · Detail: migration/features/28-paid-integrationen-importer-ai.md#P09-F01; migration/features/22-paid-architektur-selfhosting-dienste.md#P03-F14

</details>

<details><summary><b>F2</b> – 0 Features</summary>

_Hinweis:_ Einzige Code-Hosting-Integration (ersetzt GitHub/GitLab/Bitbucket). Funktionsumfang orientiert an den GitHub/GitLab-Features der Commercial Edition; Forgejo als Aspire-Ressource im Stack. Kein EE-Gegenstück, daher ohne EE-IDs.


</details>

<details><summary><b>F5</b> – 3 Features</summary>

_Hinweis:_ Nur mit Internetzugang.

- [ ] `EE-P09-009` Slack: Workspace verbinden, persönliches Konto, DM-Alerts [Matrix coming soon, ausgeliefert] — Plan: Pro · CE: Stub/UI-Hülle im CE · Konfidenz: hoch · Detail: migration/features/28-paid-integrationen-importer-ai.md#P09-F09; migration/features/20-paid-spuren-im-repo.md#PF-86; migration/features/22-paid-architektur-selfhosting-dienste.md#P03-F18
- [ ] `EE-P09-010` Slack: Projekt-Benachrichtigungen (Projekt ↔ Channel) — Plan: Pro · CE: Stub/UI-Hülle im CE · Konfidenz: hoch · Detail: migration/features/28-paid-integrationen-importer-ai.md#P09-F10; migration/features/22-paid-architektur-selfhosting-dienste.md#P03-F18
- [ ] `EE-P09-011` Slack: `/plane`-Slash-Command, Message-Shortcuts, Thread-Sync, Link-Unfurl — Plan: Pro · CE: fehlt · Konfidenz: mittel · Detail: migration/features/28-paid-integrationen-importer-ai.md#P09-F11; migration/features/22-paid-architektur-selfhosting-dienste.md#P03-F18

</details>

<details><summary><b>F6</b> – 1 Features</summary>

- [ ] `EE-P09-012` Sentry-Integration — Plan: Pro · CE: Stub/UI-Hülle im CE · Konfidenz: hoch · Detail: migration/features/28-paid-integrationen-importer-ai.md#P09-F12; migration/features/20-paid-spuren-im-repo.md#PF-87; migration/features/22-paid-architektur-selfhosting-dienste.md#P03-F19

</details>

<details><summary><b>F7</b> – 5 Features</summary>

_Hinweis:_ Nur mit Internetzugang.

- [ ] `EE-P09-013` HubSpot-Connector — Plan: unklar · CE: fehlt · Konfidenz: niedrig · Detail: migration/features/28-paid-integrationen-importer-ai.md#P09-F13; migration/features/22-paid-architektur-selfhosting-dienste.md#P03-F20
- [ ] `EE-P09-014` Cursor-Agent-Integration — Plan: unklar · CE: fehlt · Konfidenz: niedrig · Detail: migration/features/28-paid-integrationen-importer-ai.md#P09-F14; migration/features/22-paid-architektur-selfhosting-dienste.md#P03-F21
- [ ] `EE-P09-015` Zapier [coming soon] — Plan: Pro · CE: fehlt · Konfidenz: niedrig · Detail: migration/features/28-paid-integrationen-importer-ai.md#P09-F15; migration/features/20-paid-spuren-im-repo.md#PF-89
- [ ] `EE-P09-016` Zendesk (Work Items aus Tickets) [coming soon] — Plan: Pro · CE: fehlt · Konfidenz: niedrig · Detail: migration/features/28-paid-integrationen-importer-ai.md#P09-F16; migration/features/20-paid-spuren-im-repo.md#PF-90
- [ ] `EE-P09-017` Freshdesk (Work Items aus Tickets) [coming soon] — Plan: Pro · CE: fehlt · Konfidenz: niedrig · Detail: migration/features/28-paid-integrationen-importer-ai.md#P09-F17; migration/features/20-paid-spuren-im-repo.md#PF-90

</details>

<details><summary><b>F8</b> – 3 Features</summary>

- [ ] `EE-P09-019` Importer-Framework (Imports-Seite, Job-Status, Historie, Importer-Worker) — Plan: Commercial-Free · CE: Stub/UI-Hülle im CE · Konfidenz: mittel · Detail: migration/features/28-paid-integrationen-importer-ai.md#P09-F21; migration/features/22-paid-architektur-selfhosting-dienste.md#P03-F22; migration/features/20-paid-spuren-im-repo.md#PF-83
- [ ] `EE-P09-027` CSV-Importer für Work Items — Plan: Commercial-Free · CE: fehlt · Konfidenz: mittel · Detail: migration/features/28-paid-integrationen-importer-ai.md#P09-F29
- [ ] `EE-P09-029` Mitglieder-Import per CSV (Workspace und Projekt) — Plan: unklar · CE: Stub/UI-Hülle im CE · Konfidenz: hoch · Detail: migration/features/28-paid-integrationen-importer-ai.md#P09-F32; migration/features/27-paid-sicherheit-admin-lizenz.md#P08-31; migration/features/20-paid-spuren-im-repo.md#PF-60

</details>

<details><summary><b>F9</b> – 2 Features</summary>

- [ ] `EE-P09-020` Jira-Cloud-Importer (inkl. Custom Properties) — Plan: Commercial-Free · CE: Stub/UI-Hülle im CE · Konfidenz: mittel · Detail: migration/features/28-paid-integrationen-importer-ai.md#P09-F22; migration/features/20-paid-spuren-im-repo.md#PF-83
- [ ] `EE-P09-021` Jira-Server/Data-Center-Importer — Plan: unklar · CE: fehlt · Konfidenz: mittel · Detail: migration/features/28-paid-integrationen-importer-ai.md#P09-F23

</details>

<details><summary><b>F10</b> – 4 Features</summary>

- [ ] `EE-P09-022` Linear-Importer — Plan: Commercial-Free · CE: fehlt · Konfidenz: mittel · Detail: migration/features/28-paid-integrationen-importer-ai.md#P09-F24
- [ ] `EE-P09-023` Asana-Importer — Plan: Commercial-Free · CE: fehlt · Konfidenz: mittel · Detail: migration/features/28-paid-integrationen-importer-ai.md#P09-F25
- [ ] `EE-P09-024` ClickUp-Importer — Plan: unklar · CE: fehlt · Konfidenz: mittel · Detail: migration/features/28-paid-integrationen-importer-ai.md#P09-F26
- [ ] `EE-P09-028` GitHub-Importer — Plan: Commercial-Free · CE: Stub/UI-Hülle im CE · Konfidenz: mittel · Detail: migration/features/28-paid-integrationen-importer-ai.md#P09-F30; migration/features/20-paid-spuren-im-repo.md#PF-83

</details>

<details><summary><b>F11</b> – 2 Features</summary>

- [ ] `EE-P09-025` Notion-Importer — Plan: unklar · CE: fehlt · Konfidenz: niedrig · Detail: migration/features/28-paid-integrationen-importer-ai.md#P09-F27
- [ ] `EE-P09-026` Confluence-Importer — Plan: unklar · CE: fehlt · Konfidenz: mittel · Detail: migration/features/28-paid-integrationen-importer-ai.md#P09-F28

</details>

## G – Plane AI

| ✓ | Prio | Paket | Aufwand | 🧱 | Plan im Original | Setzt voraus |
|---|---|---|---|---|---|---|
| [ ] | | **G1** AI-Basis (LLM-/Embedding-Provider, Semantic Search mit pgvector, Duplicate Detection, Feature-Schalter) | L (15–40 PT) | 🧱 | Pro, unklar | – |
| [ ] | | **G2** Pi-Chat inkl. Connectors (MCP), Skills, Memory, Agents, Autopilot | XL (40–100 PT) |  | Pro | G1, H4 |
| [ ] | | **G3** AI im Editor und AI-Aktionen (Selection-Aktionen, /ai-Block, Agent in Pages, Work-Creation, Summary/Catch-up, Applets) | L (15–40 PT) |  | Pro, Business, unklar | G1 |

<details><summary><b>G1</b> – 4 Features</summary>

_Hinweis:_ Indexierungs-Pipeline in der CE vorsehen; lokaler Provider für Airgapped.

- [ ] `EE-P09-030` Plane AI: Dienst „PI“, Workspace-Feature `pi`, Settings-Seite „Plane AI“ — Plan: Pro · CE: Stub/UI-Hülle im CE · Konfidenz: hoch · Detail: migration/features/28-paid-integrationen-importer-ai.md#P09-F33; migration/features/22-paid-architektur-selfhosting-dienste.md#P03-F12; migration/features/21-paid-api-referenz-developer-docs.md#F29; migration/features/20-paid-spuren-im-repo.md#PF-82
- [ ] `EE-P09-038` AI-Suche / Semantic Search (Embeddings, Vektorsuche) — Plan: unklar · CE: fehlt · Konfidenz: mittel · Detail: migration/features/28-paid-integrationen-importer-ai.md#P09-F41; migration/features/22-paid-architektur-selfhosting-dienste.md#P03-F13
- [ ] `EE-P09-039` Duplicate Detection (Duplikat-Vorschläge beim Anlegen von Work Items und Intake-Requests) — Plan: unklar · CE: Stub/UI-Hülle im CE · Konfidenz: mittel · Detail: migration/features/28-paid-integrationen-importer-ai.md#P09-F42; migration/features/23-paid-work-management.md#WM-47; migration/features/20-paid-spuren-im-repo.md#PF-104; migration/features/22-paid-architektur-selfhosting-dienste.md#P03-F13
- [ ] `EE-P09-042` LLM-Provider- und Embedding-Konfiguration — Plan: unklar · CE: teilweise im CE · Konfidenz: hoch · Detail: migration/features/28-paid-integrationen-importer-ai.md#P09-F45

</details>

<details><summary><b>G2</b> – 6 Features</summary>

- [ ] `EE-P09-031` Pi-Chat („Plane AI“-Chat) — Plan: Pro · CE: Stub/UI-Hülle im CE · Konfidenz: mittel · Detail: migration/features/28-paid-integrationen-importer-ai.md#P09-F34
- [ ] `EE-P09-032` Plane AI: Connectors (MCP) — Plan: Pro · CE: Stub/UI-Hülle im CE · Konfidenz: mittel · Detail: migration/features/28-paid-integrationen-importer-ai.md#P09-F35
- [ ] `EE-P09-033` Plane AI: Skills — Plan: Pro · CE: Stub/UI-Hülle im CE · Konfidenz: mittel · Detail: migration/features/28-paid-integrationen-importer-ai.md#P09-F36
- [ ] `EE-P09-034` Plane AI: Memory — Plan: Pro · CE: Stub/UI-Hülle im CE · Konfidenz: niedrig · Detail: migration/features/28-paid-integrationen-importer-ai.md#P09-F37
- [ ] `EE-P09-035` Plane AI: eingebaute Agents — Plan: Pro · CE: Stub/UI-Hülle im CE · Konfidenz: mittel · Detail: migration/features/28-paid-integrationen-importer-ai.md#P09-F38
- [ ] `EE-P09-036` Plane AI: Autopilot-Modus (Ausführung ohne Einzelbestätigung) — Plan: Pro · CE: fehlt · Konfidenz: niedrig · Detail: migration/features/28-paid-integrationen-importer-ai.md#P09-F61

</details>

<details><summary><b>G3</b> – 6 Features</summary>

- [ ] `EE-P07-024` Plane AI im Editor: Selection-Aktionen (Paraphrase, Simplify, Elaborate, Summarize, Get title, Ton) und Seitenzusammenfassung — Plan: Pro · CE: Stub/UI-Hülle im CE · Konfidenz: mittel · Detail: migration/features/26-paid-wissen-pages-wiki.md#P07-27; migration/features/28-paid-integrationen-importer-ai.md#P09-F39
- [ ] `EE-P07-025` Plane AI: AI-Block (`/ai`) — Plan: Business · CE: fehlt · Konfidenz: mittel · Detail: migration/features/26-paid-wissen-pages-wiki.md#P07-28; migration/features/28-paid-integrationen-importer-ai.md#P09-F39
- [ ] `EE-P07-026` Plane AI: Prompt/Agent in Pages mit Proposals (accept/reject) — Plan: Business · CE: fehlt · Konfidenz: niedrig · Detail: migration/features/26-paid-wissen-pages-wiki.md#P07-29; migration/features/28-paid-integrationen-importer-ai.md#P09-F39
- [ ] `EE-P09-037` AI-Work-Creation (Text → Work Items) und Beschreibungs-Generierung — Plan: unklar · CE: teilweise im CE · Konfidenz: niedrig · Detail: migration/features/28-paid-integrationen-importer-ai.md#P09-F40
- [ ] `EE-P09-040` AI-Aktionen Summary, Catch-up, Copy-as-prompt, AI-Filter — Plan: unklar · CE: fehlt · Konfidenz: niedrig · Detail: migration/features/28-paid-integrationen-importer-ai.md#P09-F43
- [ ] `EE-P09-041` Applets / Artifacts (AI-generierte, versionierte HTML-Dashboards) — Plan: unklar · CE: fehlt · Konfidenz: hoch · Detail: migration/features/28-paid-integrationen-importer-ai.md#P09-F44; migration/features/21-paid-api-referenz-developer-docs.md#F41

</details>

## H – Plattform, API & Betrieb

| ✓ | Prio | Paket | Aufwand | 🧱 | Plan im Original | Setzt voraus |
|---|---|---|---|---|---|---|
| [ ] | | **H1** OAuth-App-Plattform (Apps, Consent, Scopes, Bot-User, App-Mentions, Marketplace, OAuth Bridge) | L (15–40 PT) | 🧱 | unklar | – |
| [ ] | | **H2** Agents-Plattform (Agent Runs, Activities, Signals) | L (15–40 PT) |  | unklar | H1 |
| [ ] | | **H3** Public API v2 und API-Erweiterungen (Feature-APIs, Member entfernen, Views-API, Webhooks v2, Workspace-Tokens, GraphQL/Marketplace-Endpunkte) | L (15–40 PT) |  | Commercial-Free, unklar | – |
| [ ] | | **H4** MCP-Server (OAuth-Transport, Tool-Gates) | M (5–15 PT) |  | unklar | H1 |
| [ ] | | **H5** Developer-Tools (Plane Compose, SDKs Node/Python) | M (5–15 PT) |  | unklar | H3 |
| [ ] | | **H6** Realtime-Event-Server (Live-Updates für alle Objekte) | M (5–15 PT) | 🧱 | unklar | – |
| [ ] | | **H7** Betrieb: Airgapped, FIPS, HA/Read-Replica/External Secrets, separater API-Pool, Installer/Backup | L (15–40 PT) |  | Commercial-Free, Enterprise | – |
| [ ] | | **H8** Clients: Desktop-App, Mobile-Apps | XL (40–100 PT) |  | Commercial-Free, unklar | H3 |

<details><summary><b>H1</b> – 4 Features</summary>

_Hinweis:_ Empfehlung: Keycloak als Autorisierungsserver (ADR-008) statt eigenem OAuth2-Server.

- [ ] `EE-P09-044` OAuth-App-Plattform („Build your own app“, Consent, Bot-/User-Token, Scopes, Installationen) — Plan: unklar · CE: Stub/UI-Hülle im CE · Konfidenz: hoch · Detail: migration/features/28-paid-integrationen-importer-ai.md#P09-F47; migration/features/22-paid-architektur-selfhosting-dienste.md#P03-F25; migration/features/21-paid-api-referenz-developer-docs.md#F31; migration/features/20-paid-spuren-im-repo.md#PF-92
- [ ] `EE-P09-045` App-Marketplace — Plan: unklar · CE: Stub/UI-Hülle im CE · Konfidenz: mittel · Detail: migration/features/28-paid-integrationen-importer-ai.md#P09-F48; migration/features/20-paid-spuren-im-repo.md#PF-92; migration/features/22-paid-architektur-selfhosting-dienste.md#P03-F40
- [ ] `EE-P09-046` App-Mentions / Bot-User — Plan: unklar · CE: teilweise im CE · Konfidenz: hoch · Detail: migration/features/28-paid-integrationen-importer-ai.md#P09-F49
- [ ] `EE-P09-018` OAuth Bridge (externe IdP-JWTs als API-Credentials) — Plan: unklar · CE: Stub/UI-Hülle im CE · Konfidenz: hoch · Detail: migration/features/28-paid-integrationen-importer-ai.md#P09-F20; migration/features/22-paid-architektur-selfhosting-dienste.md#P03-F09; migration/features/20-paid-spuren-im-repo.md#PF-91

</details>

<details><summary><b>H2</b> – 1 Features</summary>

- [ ] `EE-P09-047` Agents-Plattform (Agent Runs, Activities, Signals) — Plan: unklar · CE: Stub/UI-Hülle im CE · Konfidenz: hoch · Detail: migration/features/28-paid-integrationen-importer-ai.md#P09-F50; migration/features/22-paid-architektur-selfhosting-dienste.md#P03-F26; migration/features/21-paid-api-referenz-developer-docs.md#F30

</details>

<details><summary><b>H3</b> – 8 Features</summary>

- [ ] `EE-P02-002` Projekt-Feature-API (`/features/` bündelt Projekt-Schalter `epics`, `work_item_types`, `parallel_cycles`, `project_updates`, `workflows`) — Plan: unklar · CE: teilweise im CE · Konfidenz: hoch · Detail: migration/features/21-paid-api-referenz-developer-docs.md#F16
- [ ] `EE-P02-003` Workspace-Feature-API (`project_grouping`, `initiatives`, `teams`, `customers`, `wiki`, `pi`) — Plan: unklar · CE: fehlt · Konfidenz: hoch · Detail: migration/features/21-paid-api-referenz-developer-docs.md#F17
- [ ] `EE-P02-004` Workspace-Mitglied per Public-API entfernen (inkl. Deaktivierung in allen Projekten und Seat-Reduktion) — Plan: unklar · CE: teilweise im CE · Konfidenz: hoch · Detail: migration/features/21-paid-api-referenz-developer-docs.md#F23
- [ ] `EE-P02-005` Public API v2 (`/api/v2/`: PATCH-only, problem+json, Offset-/Cursor-Pagination, `?fields=`/`?expand=`, Upsert, Bulk) — Plan: unklar · CE: fehlt · Konfidenz: hoch · Detail: migration/features/21-paid-api-referenz-developer-docs.md#F32
- [ ] `EE-P02-006` Views-API (Projekt- und Workspace-Views in der Public-API) — Plan: unklar · CE: teilweise im CE · Konfidenz: mittel · Detail: migration/features/21-paid-api-referenz-developer-docs.md#F36
- [ ] `EE-P09-048` Webhooks v2 (Webhook-CRUD, Delivery-Logs, v2-Events) — Plan: unklar · CE: teilweise im CE · Konfidenz: hoch · Detail: migration/features/28-paid-integrationen-importer-ai.md#P09-F51; migration/features/22-paid-architektur-selfhosting-dienste.md#P03-F24; migration/features/21-paid-api-referenz-developer-docs.md#F38
- [ ] `EE-P09-049` Workspace-Access-Tokens — Plan: unklar · CE: teilweise im CE · Konfidenz: mittel · Detail: migration/features/28-paid-integrationen-importer-ai.md#P09-F52; migration/features/20-paid-spuren-im-repo.md#PF-62
- [ ] `EE-P03-006` GraphQL- und Marketplace-Endpunkte (`/graphql/`, `/marketplace/`) — Plan: Commercial-Free · CE: fehlt · Konfidenz: niedrig · Detail: migration/features/22-paid-architektur-selfhosting-dienste.md#P03-F40

</details>

<details><summary><b>H4</b> – 1 Features</summary>

- [ ] `EE-P09-050` MCP-Server (OAuth-Transport, Tool-Gates) — Plan: unklar · CE: teilweise im CE · Konfidenz: hoch · Detail: migration/features/28-paid-integrationen-importer-ai.md#P09-F53; migration/features/22-paid-architektur-selfhosting-dienste.md#P03-F27

</details>

<details><summary><b>H5</b> – 2 Features</summary>

- [ ] `EE-P09-051` Plane Compose (project-as-code CLI) — Plan: unklar · CE: fehlt · Konfidenz: hoch · Detail: migration/features/28-paid-integrationen-importer-ai.md#P09-F55; migration/features/22-paid-architektur-selfhosting-dienste.md#P03-F43
- [ ] `EE-P09-052` Offizielle SDKs (Node, Python) — Plan: unklar · CE: fehlt · Konfidenz: hoch · Detail: migration/features/28-paid-integrationen-importer-ai.md#P09-F56

</details>

<details><summary><b>H6</b> – 1 Features</summary>

_Hinweis:_ Mit SignalR im Rahmen vorsehen.

- [ ] `EE-P03-007` Flux – Realtime-Event-Server (`/flux`, WebSocket mit Redis) — Plan: unklar · CE: fehlt · Konfidenz: niedrig · Detail: migration/features/22-paid-architektur-selfhosting-dienste.md#P03-F41

</details>

<details><summary><b>H7</b> – 5 Features</summary>

_Hinweis:_ Airgapped ist durch ADR-004 bereits gesetzt.

- [ ] `EE-P03-002` Airgapped Edition (Betrieb ohne Internet, Images aus eigener Registry, Offline-Aktivierung) — Plan: Enterprise · CE: teilweise im CE · Konfidenz: hoch · Detail: migration/features/22-paid-architektur-selfhosting-dienste.md#P03-F36; migration/features/27-paid-sicherheit-admin-lizenz.md#P08-23b; migration/features/20-paid-spuren-im-repo.md#PF-100
- [ ] `EE-P03-003` FIPS-140-3-Images / FIPS-Betriebsprofil — Plan: Enterprise · CE: fehlt · Konfidenz: hoch · Detail: migration/features/22-paid-architektur-selfhosting-dienste.md#P03-F37; migration/features/27-paid-sicherheit-admin-lizenz.md#P08-23c; migration/features/20-paid-spuren-im-repo.md#PF-100
- [ ] `EE-P03-004` Betriebsfeatures des Commercial-Charts (HA, Read-Replica, External Secrets, Custom CA, Storage-Proxy, GCS, OpenTelemetry, PSA/OpenShift) — Plan: Commercial-Free · CE: teilweise im CE · Konfidenz: hoch · Detail: migration/features/22-paid-architektur-selfhosting-dienste.md#P03-F38
- [ ] `EE-P03-005` Dedizierte External-API-Instanz (zweiter Backend-Pool für öffentlichen API-Verkehr) — Plan: Commercial-Free · CE: fehlt · Konfidenz: mittel · Detail: migration/features/22-paid-architektur-selfhosting-dienste.md#P03-F39
- [ ] `EE-P03-008` Prime CLI und Commercial-Installationsmethoden (Installer, Backup/Restore, Docker AIO, Swarm, Podman, Coolify, Portainer) [entfällt als Plan-/Billing-Mechanik] — Plan: Commercial-Free · CE: teilweise im CE · Konfidenz: hoch · Detail: migration/features/22-paid-architektur-selfhosting-dienste.md#P03-F42

</details>

<details><summary><b>H8</b> – 2 Features</summary>

_Hinweis:_ Eigene Produkte, nicht Teil von Web/Angular.

- [ ] `EE-P09-053` Desktop-App (macOS, Linux) — Plan: unklar · CE: Stub/UI-Hülle im CE · Konfidenz: mittel · Detail: migration/features/28-paid-integrationen-importer-ai.md#P09-F57
- [ ] `EE-P09-054` Mobile-Apps (iOS/Android) — Plan: Commercial-Free · CE: Stub/UI-Hülle im CE · Konfidenz: mittel · Detail: migration/features/28-paid-integrationen-importer-ai.md#P09-F58

</details>

## Entfällt (ADR-001 / ADR-004 / ADR-007 / ADR-008)

Diese Einträge sind Lizenz-, Billing-, Kontingent- oder Hersteller-Betriebsmechanik bzw. Funktionen, die durch Forgejo (Paket F2) oder Keycloak (ADR-008) ersetzt werden.

| ID | Feature | Grund |
|---|---|---|
| `EE-P03-009` | Installationskanäle der Matrix: One-click Deployment, DigitalOcean-Marketplace-App, Heroku-App, AWS AMI [entfällt als Plan-/Billing-Mechanik] | ADR-004 (Vertriebskanäle) |
| `EE-P03-010` | Private + managed deployments (vom Hersteller betriebene private Cloud-Instanz) [coming soon; entfällt als Plan-/Billing-Mechanik] | ADR-004 (Hersteller-Betrieb) |
| `EE-P06-016` | Anzahl Automationen je Workspace (Limit) [entfällt als Plan-/Billing-Mechanik] | ADR-001 |
| `EE-P08-001` | SAML-SSO instanzweit (God Mode, inkl. God-Mode-Login per SSO) | ADR-008 (Keycloak: Identity Brokering) |
| `EE-P08-002` | OIDC-SSO instanzweit (God Mode) | ADR-008 (Keycloak: Identity Brokering) |
| `EE-P08-003` | Workspace-Identity: verifizierte Domains und Workspace-SSO (SAML oder OIDC) | ADR-008 (Keycloak: Realms/Identity Provider/Domains) |
| `EE-P08-004` | LDAP-Authentifizierung [Matrix coming soon, ausgeliefert] | ADR-008 (Keycloak: User Federation LDAP/AD) |
| `EE-P08-007` | Zwei-Faktor-Authentifizierung | ADR-008 (Keycloak: OTP) |
| `EE-P08-008` | Passkeys | ADR-008 (Keycloak: WebAuthn/Passkeys) |
| `EE-P08-009` | Password Policy (eigene Passwort-Richtlinien) | ADR-008 (Keycloak: Password Policies) |
| `EE-P08-010` | Domain Security (erlaubte/gesperrte Anmelde-Domains) | ADR-008 (Keycloak: Domain-/Registrierungsregeln) |
| `EE-P08-014` | Guests-Kontingent (5 Gäste je bezahltem Mitglied) [entfällt als Plan-/Billing-Mechanik] | ADR-001 |
| `EE-P08-018` | Workspace-Lizenz und Seite „Billing and plans“ (Sync plan, Delink, Trial, Upgrade-Flow) [entfällt als Plan-/Billing-Mechanik] | ADR-001 |
| `EE-P08-019` | Enterprise-Grid-Instanzlizenz (God Mode → Billing) [entfällt als Plan-/Billing-Mechanik] | ADR-001 |
| `EE-P08-020` | Offline-Lizenzdatei (Airgapped) [entfällt als Plan-/Billing-Mechanik] | ADR-001 |
| `EE-P08-021` | Prime-Portal und Monitor-Dienst (Lizenzvalidierung, Feature-Flags, Plan-Synchronisation) [entfällt als Plan-/Billing-Mechanik] | ADR-001 |
| `EE-P08-022` | Member-Limits und Seat-Berechnung (Aufhebung der Mitgliedergrenze) [entfällt als Plan-/Billing-Mechanik] | ADR-001 |
| `EE-P08-023` | Storage-Limits (Workspace-Speicher, Max file size) [entfällt als Plan-/Billing-Mechanik] | ADR-001/004 |
| `EE-P08-024` | Support-Kanäle, SLA und „Chat with us“ [entfällt als Plan-/Billing-Mechanik] | ADR-001 |
| `EE-P09-002` | GitHub: Organisation verbinden, persönliches Konto, Repository-Mapping [Matrix coming soon, ausgeliefert] | ADR-007 (ersetzt durch Forgejo, Paket F2) |
| `EE-P09-003` | GitHub: Pull-Request-Automation (PR-State-Mapping) | ADR-007 (ersetzt durch Forgejo, Paket F2) |
| `EE-P09-004` | GitHub: Project Issue Sync (bi-/unidirektional inkl. Kommentare, Sub-Issues) | ADR-007 (ersetzt durch Forgejo, Paket F2) |
| `EE-P09-005` | GitHub Enterprise (Server und Enterprise Cloud ghe.com) | ADR-007 (ersetzt durch Forgejo, Paket F2) |
| `EE-P09-006` | GitLab (gitlab.com): MR-State-Mapping, Issue Sync | ADR-007 (ersetzt durch Forgejo, Paket F2) |
| `EE-P09-007` | GitLab Self-managed („Gitlab Enterprise“) | ADR-007 (ersetzt durch Forgejo, Paket F2) |
| `EE-P09-008` | Bitbucket Cloud und Bitbucket Data Center | ADR-007 (ersetzt durch Forgejo, Paket F2) |
| `EE-P09-043` | AI-Usage, Credits, Token-Budget [entfällt als Plan-/Billing-Mechanik] | ADR-001 |
| `EE-P09-055` | Flatfile-Importer (CSV über Flatfile, Beta) [entfällt als Plan-/Billing-Mechanik] | ADR-004 (Cloud-only) |

## Prüfsumme

- Features in der Matrix: 246
- Zugeordnet zu Paketen: 218
- Entfällt: 28
- Pakete: 68, davon strukturrelevant: 17

_Erzeugt mit `migration/_werkzeuge/paid-auswahl/build.py`; das Skript prüft, dass jede EE-ID genau einmal vorkommt._
