# 24 – Bezahl-Features Cluster P05 „Planung, Insights, Teams“ – IST-Analyse

> **Gegenstand:** Funktionen der closed-source Commercial Edition (Pro / Business / Enterprise bzw. „Enterprise Grid“) aus den Bereichen Teamspaces, Dashboards & Widgets, Analytics/Insights/Custom Reports, Cycle-Erweiterungen (Workspace-Active-Cycles, Progress Charts, Cycle Reports, Auto-Schedule, Auto-Rollover, Parallel Cycles), Views (Shared/Published), PQL und erweiterte Filter, Advanced Search, Scheduled Comms, Workspace Activity Logs sowie Home-/Your-Work-/Navigations-Erweiterungen.
> **Basis:** Plane v1.4.2 Community Edition (CE) unter `/home/user/plane` (nur gelesen), Developer-Docs `/home/user/makeplane/developer-docs/docs`, Helm-Chart `/home/user/makeplane/helm-charts/charts/plane-enterprise`, npm-Paket `@makeplane/propel` 0.7.3 (entpackt, nur gelesen), sekundäre Web-Zusammenfassungen aus den Schwesterdokumenten.
> **Verifikationsstand:** Skeptiker-/Verifikationslauf vom 22.10.2026 (Tier gegen R1/R2, Schwester-Dokumente 20–28 und 13 gezielte WebSearch-Abfragen; CE-Status per `grep` im Repo; Vollständigkeit; Übertreibungen). Korrekturen sind im Text mit „(Verifikation)“ markiert; Details und Belege im Abschnitt „Verifikations-Protokoll“ am Dokumentende. Finale Feature-Liste: `migration/features/_data/P05.paid.json`.
> **Bindend:** `migration/architecture/00-grundsatzentscheidungen.md` (ADR-000 … ADR-006). Insbesondere: keine Plan-Stufen (ADR-001) – jede hier als „Pro/Business/Enterprise“ markierte Funktion ist in der Zielplattform **immer aktiv**; Upsell-Elemente entfallen und werden durch die echte Funktion ersetzt. Realtime in reinem .NET (ADR-002). Greenfield-Schema (ADR-003). Self-hosted/Airgapped ohne Pflicht-Außenabhängigkeit (ADR-004). UI 1:1 (ADR-005).

## Inhaltsverzeichnis

1. [Überblick & Quellenlage](#1-überblick--quellenlage)
2. [Feature-Tabelle](#2-feature-tabelle)
3. [Feature-Abschnitte](#3-feature-abschnitte)
   - 3.1 Teamspaces (P05-01 … P05-08)
   - 3.2 Dashboards & Widgets (P05-09 … P05-13)
   - 3.3 Analytics, Insights, Reports (P05-14 … P05-18)
   - 3.4 Cycles (P05-19 … P05-26) inkl. Abgrenzung CE
   - 3.5 Views (P05-27, P05-28) inkl. Abgrenzung Workspace-Views
   - 3.6 PQL und erweiterte Filter (P05-29, P05-30, P05-35)
   - 3.7 Advanced Search (P05-31)
   - 3.8 Scheduled Comms (P05-32)
   - 3.9 Workspace Activity Logs (P05-33)
   - 3.10 Home-, Your-Work- und Navigations-Erweiterungen (P05-34)
4. [Offene Punkte / Unklarheiten](#4-offene-punkte--unklarheiten)
- Anhang A: Inventar der CE-Spuren (Stubs, Typen, Extension-Points) des Clusters
- Anhang B: i18n-Schlüssel des Clusters (vollständig, mit Referenzstatus)
- Anhang C: Icons und Illustrationen des Clusters
- Anhang D: Endpunkt-Inventar des Clusters
- Anhang E: Abgrenzung – im CE bereits vorhandene Funktionen dieses Themenfelds

---

## 1. Überblick & Quellenlage

### 1.1 Auftrag, Abgrenzung und Querverweise

Dieses Dokument vertieft den Cluster P05. Überschneidungen mit Schwesterdokumenten werden **nicht** dupliziert, sondern referenziert; wo dieses Dokument präzisiert oder korrigiert, ist das in 1.4 vermerkt.

| Thema | Primär behandelt in | Hier |
|---|---|---|
| Plan-Matrix (alle 87 Zeilen), Upsell-Inventar, CE-Stub-Inventar gesamt | `migration/features/20-paid-spuren-im-repo.md` (PF-04, PF-12, PF-13, PF-30, PF-31, PF-33, PF-43 … PF-53, PF-58) | vertieft und korrigiert |
| Teamspace-Public-API (TS1–TS11), Workspace-Features (WF1/WF2), Advanced-Search-API (W8), PQL-Fakten (F25) | `migration/features/21-paid-api-referenz-developer-docs.md` §2.17, §4.4, §4.14, §4.19 | übernommen, ergänzt |
| OpenSearch-Architektur (9 Indizes, Redis-Batching), Webhooks v2 mit PQL-Filter | `migration/features/22-paid-architektur-selfhosting-dienste.md` §4.11 (P03-F11), P03-F24 | referenziert |
| Auto-Schedule-Cycles (Querverweis „Cycle-Cluster“) | `migration/features/25-paid-workflows-automation-templates.md` F27 | **hier vollständig** (P05-21) |
| Teamspace-Pages, Advanced Pages Analytics, Editor-Block „Link dashboard widgets“ | `migration/features/26-paid-wissen-pages-wiki.md` P07-17, P07-25, P07-42 | referenziert (P05-04, P05-13, P05-18) |
| Workspace Activity Logs, API-Audit-Logs | `migration/features/27-paid-sicherheit-admin-lizenz.md` P08-17, P08-18 | referenziert, Cluster-Sicht ergänzt (P05-33) |
| CE-Analytics (Endpunkte AN-01 … AN-16), CE-Cycles (Y1 … Y23), CE-Views (W1 …), CE-Suche (SR-01 … SR-03) | `migration/analysis/03-api-intern-workspace-projekt-user.md`, `migration/analysis/04-api-intern-arbeitsobjekte.md` | nur als Basis referenziert |

### 1.2 Quellen und Kürzel

| Kürzel | Bedeutung |
|---|---|
| `W/` | `apps/web/` (Repo-Root `/home/user/plane`) |
| `SPC/` | `apps/space/` |
| `API/` | `apps/api/plane/` |
| `T/` | `packages/types/src/` |
| `C/` | `packages/constants/src/` |
| `U/` | `packages/utils/src/` |
| `B/` | `packages/blocks/src/` |
| `L/` | `packages/i18n/src/locales/en/` |
| `R1` | `W/components/workspace/billing/comparison/plans.tsx` (offizielle Feature×Plan-Matrix; Zeilennummern „Z.“ beziehen sich auf diese Datei) |
| `R2` | `C/subscription.ts` (Feature-Listen der Upgrade-Karten) |
| `DD/` | `/home/user/makeplane/developer-docs/docs/` (Offline-Developer-Docs der Commercial Edition) |
| `IMG/` | `DD/public/images/` (Screenshots; Commercial- oder ältere CE-Oberflächen) |
| `HC/` | `/home/user/makeplane/helm-charts/charts/plane-enterprise/` |
| `PROPEL/` | `@makeplane/propel` 0.7.3, entpackt unter `/tmp/claude-0/-home-user-plane/fe89ae79-d9fa-54e4-b848-1dc9726b58d0/scratchpad/propel-pkg/package/dist/` (nur gelesen) |
| `V2/` | (Verifikation) REST-API v2 der Commercial Edition, Branch `docs/api-reference-v2` der Developer-Docs, Commit `b89c72c` (11.08.2026), Klon unter `/tmp/claude-0/-home-user-plane/fe89ae79-d9fa-54e4-b848-1dc9726b58d0/scratchpad/devdocs-v2/repo/docs/api-reference/v2/` (Quellenstand siehe `migration/features/21-paid-api-referenz-developer-docs.md` V.3) |

**Web-Quellen (WS).** `docs.plane.so`, `plane.so` und `developers.plane.so` sind per Netzwerk-Policy nicht abrufbar. In **diesem** Lauf war zusätzlich das WebSearch-Budget (200 Aufrufe pro Turn, geteilt mit allen parallelen Agenten) bereits beim ersten Aufruf erschöpft; das GitHub-Repo der Nutzer-Doku ist für diese Session nicht freigegeben. Web-Belege stammen daher ausschließlich aus den von Schwester-Agenten bereits erhobenen WebSearch-Zusammenfassungen (sekundär, nicht wortgetreu) oder bestehen nur aus URL/Titel (URL-Slug als Beleg für Existenz und Zeitpunkt, Inhalt **nicht** gelesen).

| ID | URL | Belegter Inhalt | Herkunft |
|---|---|---|---|
| WS1 | https://docs.plane.so/core-concepts/workspaces/teamspaces | Teamspace-Pages im Tab „Pages“, nur für Teamspace-Mitglieder, immer öffentlich im Teamspace; Kommentare bleiben im Teamspace sichtbar; Lead darf jede Seite/jeden Kommentar archivieren/löschen | Dok. 26 (W30) §3.17, §3.15 |
| WS2 | https://docs.plane.so/roles-and-permissions/permissions-matrix | Rechte Teamspace-Pages (Member: sehen, erstellen, bearbeiten, duplizieren, verschieben, exportieren, favorisieren; archivieren/löschen nur eigene) | Dok. 26 (W29) |
| WS3 | https://plane.so/pro , https://plane.so/pricing | Pro enthält „teamspaces“ | Dok. 20 (Q10, PF-30) |
| WS4 | https://plane.so/changelog/release-v3-1-0-audit-logs-skills-in-plane-ai-dashboards-and-more | nur Titel: Dashboards-Neuerungen in Commercial v3.1.0 | Dok. 25 (W30), 26 (W15) |
| WS5 | https://plane.so/changelog/2026-05-15-embed-media-in-the-editor-pql-in-dashboards-and-more | nur Titel: „PQL in dashboards“ (Cloud 15.05.2026) | Dok. 25 (W51), 26 (W33) |
| WS6 | https://plane.so/changelog/2026-06-30-mermaid-js-diagrams-pql-dashboard-filters | nur Titel: „PQL dashboard filters“ (Cloud 30.06.2026) | Dok. 26 (W20) |
| WS7 | https://plane.so/changelog/2026-08-14-collapsible-toggle-blocks-dashboard-intake-widgets | nur Titel: „dashboard intake widgets“ (Cloud 14.08.2026) | Dok. 26 (W17) |
| WS8 | https://plane.so/changelog/2026-10-15-page-comments-dashboard-custom-properties | nur Titel: „dashboard custom properties“ (Cloud 15.10.2026) | Dok. 26 (W8) |
| WS9 | https://plane.so/changelog/2026-08-31-shared-views-tabs-in-pages-and-more | nur Titel: „shared views“ (Cloud 31.08.2026) | Dok. 26 (W18) |
| WS10 | https://plane.so/changelog/release-v2-6-0-pql-releases-wiki-collections-and-more | nur Titel: PQL in Commercial v2.6.0 | Dok. 26 (W41) |
| WS11 | https://plane.so/changelog/release-v-1-16-0-introducing-milestones-and-recurring-cycles | nur Titel: „Recurring cycles“ in Commercial v1.16.0 | Dok. 25 (W49), 26 (W28) |
| WS12 | https://plane.so/changelog/release-v2-2-0-enterprise-rollout-enhanced-search-workspace-refinements | nur Titel: „enhanced search“ in Commercial v2.2.0 | Dok. 20 (Q10) |
| WS13 | https://docs.plane.so/core-concepts/issues/plane-query-language | PQL-Leitfaden existiert (verlinkt aus `DD/dev-tools/mcp-server.md` Z. 58 und `DD/dev-tools/mcp-server-tools.md` Z. 46); Inhalt nicht gelesen | DD |
| WS14 | https://docs.plane.so/workspaces-and-users/audit-logs | Audit-Log-Doku existiert; Inhalt nicht gelesen | Dok. 27 (W4) |
| WS15 | https://docs.plane.so/pages/page-analytics | Page-Analytics-Details | Dok. 26 (W6) |
| WS16 | https://docs.plane.so/core-concepts/pages/editor-blocks | Block „Link dashboard widgets“ mit Label „Enterprise“ | Dok. 26 (W4, W19) |
| WS17 | https://docs.plane.so/core-concepts/workspaces/teamspaces ; https://university.plane.so/courses/201-the-growth/08-intro-to-teamspaces.html ; https://docs.plane.so/introduction/quickstart/growing-teams | Doku-Label „Pro“; Aktivierung in Workspace Settings → Tab „Teamspaces“, **danach nicht mehr abschaltbar**; Anlegen mit Name, Team lead, Team members; alle Teamspace-Mitglieder erhalten automatisch **Member**-Zugriff auf verknüpfte Projekte; Team Leads haben keine besonderen Workspace-Rechte | WebSearch Verifikation (Zusammenfassung, sekundär) |
| WS18 | https://docs.plane.so/core-concepts/workspaces/teamspaces ; https://plane.so/teamspaces ; https://github.com/makeplane/docs/pull/324/files ; https://plane.so/changelog/release-v3-2-0-workspace-governance-ai-memory-pii-scanning-and-more | Teamspace-Overview mit Aktivitäten aller Teamspace-Projekte und Navigation Work items/Cycles/Views/Pages; Work items mit Tabs „Team“ (Work Items der Teamspace-Mitglieder) und „Project“ (alle Work Items verknüpfter Projekte; ältere Doku); Cycles aller verknüpften Projekte konsolidiert inkl. Beitrag je Person; Views: eigene Teamspace-Views oder alle Views der verknüpften Projekte per Tab-Wechsel; Pages als Team-Wissensbasis; Feed „real-time team updates“; Admins können Kommentare an Work Items, Pages **und Teamspaces** mit Grund (abuse, spam, off-topic, sensitive info, other) aus-/einblenden (v3.2.0) | WebSearch Verifikation (sekundär) |
| WS19 | https://docs.plane.so/dashboards ; https://plane.so/dashboards | Dashboards in der linken Sidebar; Button „Add dashboard“ oben rechts; Name + Auswahl der Projekte; „+ Add widget“ → Typ wählen, Daten konfigurieren, benennen, per Drag & Drop platzieren; Widget-Typen **Bar chart, Line chart, Area chart, Donut chart, Pie chart, Number**; Widgets filterbar nach Assignee, Priority, State, Label oder beliebiger Work-Item-Property | WebSearch Verifikation (sekundär) |
| WS20 | https://identichosting.duckdns.org/makeplane/docs/pull/452/files (Spiegel eines Doku-PR, kein offizieller Stand) | Badge „Pro“ für Dashboards; Sichtbarkeit privat/öffentlich, Default **Public**; Tabellen-Widget | WebSearch Verifikation (sekundär, Entwurf) |
| WS21 | https://plane.so/blog/introducing-pql-and-enhanced-dashboards (12.05.2026) | PQL; „Text to PQL“ (AI, natürliche Sprache → PQL) nur Enterprise; PQL in Dashboards auf drei Ebenen: **source, quick und widget filters**; neu gestaltete Dashboard-Oberfläche, **Tabellen-Widget**, interaktive Charts (Aufschlüsselung nach Metrik/Dimension, Drill-down per Klick auf Segmente) | WebSearch Verifikation (sekundär) |
| WS22 | https://docs.plane.so/core-concepts/issues/plane-query-language | Seitentitel „Plane Query Language (PQL) **Enterprise Grid**“; Muster Feld–Operator–Wert, `AND`/`OR`, Klammern; Editor führt per Dropdown durch Feld → Operator → Wert; verfügbar in Work items, Cycles, Modules, Views, Teamspace work items, Workspace views; Operatoren feldabhängig: `id`/`title` mit exakt, ungleich und `~` (contains), `type` mit `IN`/`NOT IN` | WebSearch Verifikation (sekundär) |
| WS23 | https://plane.so/changelog/2026-08-14-collapsible-toggle-blocks-dashboard-intake-widgets ; https://plane.so/changelog/release-v3-1-0-audit-logs-skills-in-plane-ai-dashboards-and-more ; https://plane.so/blog/whats-new-in-plane-august-2026 | Intake-Widgets: accepted vs. declined, durchschnittliche Zeit bis Annahme/Ablehnung, request breakdown, intake items aging, „Intake volume by source“; Widget-Konfiguration nach Projekt filterbar (Standardfilter oder PQL); Dashboard **duplizieren** samt Widgets; Widgets „Cycle Progress Bar“ (ein oder mehrere Cycles) und „Work Item Type Progress“ | WebSearch Verifikation (sekundär) |
| WS24 | https://university.plane.so/courses/201-the-growth/09-intro-to-cycle-automation.html | „Cycle Automation (Auto-Schedule Cycles)“ als **Business**-Funktion, aktiviert in den Projekt-Einstellungen; Cooldown zwischen Cycles; Rollover unfertiger Work Items (Kurs-Entwurf mit Platzhalter-Video) | WebSearch Verifikation (sekundär, niedrig) |
| WS25 | https://university.plane.so/courses/302-the-ecosystem/03-intro-to-plane-publish.html ; https://docs.plane.so/views | „How to Publish (Pro)“: View anlegen, öffnen, „Publish“, Einstellungen, URL teilen; Projekt-Views für alle Projektmitglieder sichtbar | WebSearch Verifikation (sekundär) |
| WS26 | https://plane.so/blog/whats-new-in-plane-august-2026 ; https://plane.so/changelog/2026-08-31-shared-views-tabs-in-pages-and-more | Shared Views: gespeicherte View an ausgewählte Personen geben, je Person **view-only oder edit** | WebSearch Verifikation (sekundär) |
| WS27 | https://plane.so/blog/introducing-progress-charts ; https://docs.plane.so/core-concepts/cycles | Progress Charts in Cycles, Active Cycles, Modules und Home (Okt. 2024); ältere Cycles-Doku: „Only one active cycle is allowed in a project at a time“; Active Cycles aller Projekte an einer Stelle | WebSearch Verifikation (sekundär) |
| WS28 | https://docs.plane.so/core-concepts/analytics | ältere Analytics-Doku mit den Tabs „Scope and Demand“ und „Custom Analytics“ (bestätigt K1) | WebSearch Verifikation (sekundär) |

### 1.3 Methode

| Schritt | Vorgehen | Ergebnis |
|---|---|---|
| M1 | Plan-Zuordnung zeilengenau aus R1 und R2 | Tier-Spalten in Kap. 2 |
| M2 | `grep` über `apps/`, `packages/` nach `teamspace`, `team_space`, `team_project`, `TEAM_VIEW`, `dashboard`, `widget`, `active-cycles`, `cycle-progress`, `version === 2`, `formatActiveCycle`, `pql`, `EXTENDED_*`, `anchor`, `publish`, `advanced`, `new_at_plane`, `quick_tutorial`, `mutateWorkspaceMembersActivity`; jede Fundstelle gelesen | Anhang A (48 Einträge) |
| M3 | i18n: alle Schlüssel des Clusters aus `L/*.json` mit Referenzstatus (Skript über die P01-Orphan-Liste; manuelle Korrektur dynamisch referenzierter Schlüssel) | Anhang B (228 Schlüssel) |
| M4 | Developer-Docs: Teamspace-API, Workspace-/Project-Features, Advanced-Search-API, MCP-Server-Tools (PQL), Webhooks (PQL-Filter), Plane Compose (`parallel_cycles`, `project_updates`), `self-hosting/govern/advanced-search.md` | Kap. 3 |
| M5 | Screenshots angesehen: `IMG/cycles/active-cycles-ui.png`, `IMG/cycles/active-cycle-ui.png`, `IMG/analytics/analytics-custom-analytics.png`, `IMG/analytics/analytics-scope-demand.png`, `IMG/views/views-overview.png`, `IMG/webhooks/create-webhook.webp`, `IMG/time-tracking/view-worklogs.webp`; Upsell-Assets `W/app/assets/workspace-active-cycles/cta-*-light.webp` | UI-Hinweise |
| M6 | Backend-Gegenprobe (Modelle, URLs, Views) | CE-Status je Feature |

### 1.4 Korrekturen und Präzisierungen gegenüber Dokument 20

| Nr. | Aussage in Dok. 20 | Befund dieses Dokuments | Beleg |
|---|---|---|---|
| K1 | PF-50: Nicht referenzierte Texte `workspace_analytics.tabs.scope_and_demand` („Scope and Demand“), `workspace_analytics.tabs.custom` („Custom Analytics“) zeigen EE-Tabs | **Falsch zugeordnet.** Es sind Reste der **alten CE-Analytics** (v0.x). Screenshots `IMG/analytics/analytics-scope-demand.png` und `IMG/analytics/analytics-custom-analytics.png` zeigen genau diese Tabs mit „Total open tasks“, „Pending issues“, „Most issues created/closed“, „Issues closed in a year“, „Selected Projects“ (Total members/cycles/modules), „Refresh“, „Export as CSV“. Die zugehörigen Backend-Endpunkte existieren im CE noch (`API/app/urls/analytic.py` Z. 26–53: `analytics/`, `analytic-view/`, `saved-analytic-view/`, `export-analytics/`, `default-analytics/`). Gleiches gilt für `workspace_analytics.open_tasks`, `.pending_work_items.*`, `.most_work_items_created.*`, `.most_work_items_closed.*`, `.work_items_closed_in_a_year.*`, `.work_items_closed_in`, `.selected_projects`, `.total_members`, `.total_cycles`, `.total_modules`, `.error`, `.empty_state.general.*` | Anhang B |
| K2 | PF-43/PF-44: `project_views.empty_state.shared.*` / `.public.*` belegen Shared/Public Views | **Falsch zugeordnet.** Texte lauten „No shared pages yet – Pages that others have shared with you will appear here.“ bzw. „No public pages yet …“ – identisch mit `project_page.empty_state.public.*` (`L/project.json`). Es sind fehlplatzierte Page-Texte; „shared“ gehört zum Page-Sharing (Dok. 26 P07-16) | `L/project.json` |
| K3 | – | **Workspace-Views** (globale Views „All work items“, „Assigned“, „Created“, „Subscribed“ + eigene) sind **CE**, kein Bezahl-Feature. Bezahl-Anteile sind nur Shared/Publish | `T/workspace-views.ts` Z. 41; `W/app/routes/core.ts` Z. 109–113; R1 Z. 488 („Views“ ab Free) |
| K4 | – | **Burndown nach Work Items/Estimates** (Umschalter „Work items“/„Estimates“) und die Cycle-Analytics-Sidebar (Assignee-/Label-/State-Verteilung) sind **CE**. Bezahl-Anteil ist „Progress Charts“ (v2-Fortschrittsreihe, Scope-Linie, Burn-up) | `W/components/cycles/analytics-sidebar/issue-progress.tsx` Z. 36–39; `W/components/cycles/dropdowns/estimate-type-dropdown.tsx` |
| K5 | – | `workspace_dashboard.empty_state.*` („Overview of your projects, activity, and metrics“) und `workspace_empty_state.your_work_by_state/by_priority` gehören zum **veralteten CE-Home-Dashboard** (`T/dashboard.ts` `TWidgetKeys`; `API/app/urls/user.py` Z. 80), nicht zu den Bezahl-Dashboards | `T/dashboard.ts` |
| K6 | PF-04: Active Cycles „One–Enterprise“ | bestätigt. **(Verifikation, korrigiert):** Die ursprüngliche Aussage, der CE-Sidebar-Eintrag „Cycles“ werde immer gerendert, ist falsch. `SidebarWorkspaceMenu` (`W/components/workspace/sidebar/workspace-menu.tsx`, Eintrag `key: "active-cycles"` Z. 46–52) wird im CE nirgends importiert; die gerenderte Sidebar (`W/components/workspace/sidebar/sidebar-menu-items.tsx` Z. 82–121) nutzt `WORKSPACE_SIDEBAR_DYNAMIC_NAVIGATION_ITEMS_LINKS` = Views, Analytics, Archives (`C/workspace.ts` Z. 201–229) – **ohne** Active Cycles. Die Seite `/:workspaceSlug/active-cycles` ist im CE nur per URL erreichbar. Im Customize-/Extended-Sidebar-Code ist für den Key `active_cycles` ein `UpgradeBadge` vorgesehen (`W/components/workspace/sidebar/extended-sidebar-item.tsx` Z. 199–203), und das Backend legt die Navigations-Präferenz `active_cycles` an (`API/db/models/workspace.py` Z. 420–427; `API/app/views/workspace/user_preference.py` Z. 33) | wie links; Dok. 20 V.1 („`SidebarUserMenu`/`SidebarWorkspaceMenu` nicht gerendert“) |
| K7 | PF-46: Trailing/Leading-Legende deutet erweiterte Fortschrittsdiagramme an | präzisiert: das CE enthält die vollständige **Datenaufbereitung** der EE-Progress-Charts (`U/cycle.ts` `formatActiveCycle`, `formatV1Data`, `formatV2Data`, Typen `TCycleProgress`, `TProgressChartData`) ohne Aufrufer sowie den No-op-Hook `fetchActiveCycleProgressPro` (Endpunkt `…/cycle-progress/`) für Cycles mit `version === 2` | Anhang A, A-28 … A-33 |

### 1.5 Ergebnis in Zahlen

| Kennzahl | Wert |
|---|---|
| Bezahl-Features in diesem Cluster (Kap. 2) | 35 (P05-01 … P05-35; P05-35 im Verifikationslauf ergänzt) |
| davon mit belegter Plan-Zuordnung aus R1/R2/DD/Doku-Label | 20 (P05-01, P05-05, P05-09, P05-10, P05-13, P05-14, P05-16 … P05-20, P05-22, P05-23, P05-27 … P05-33; davon P05-13, P05-29 nur über sekundäre Doku-Labels) |
| davon nur über sekundäre Web-Quelle (niedrig) | 2 (P05-21 Business laut University-Kurs; P05-35 Enterprise laut Blog) |
| davon aus P05-01 abgeleitet (UNVERIFIZIERT) | 5 (P05-02, P05-03, P05-04, P05-07, P05-08) |
| davon „unklar“ (keine belastbare Plan-Quelle) | 8 (P05-06, P05-11, P05-12, P05-15, P05-24, P05-25, P05-26, P05-34) |
| davon mit Repo-Spuren über die Plan-Matrix hinaus (Stub/Typ/Service/Text) | 21 |
| CE-Spuren-Inventar (Anhang A) | 52 Einträge (48 + 4 im Verifikationslauf) |
| i18n-Schlüssel des Clusters (Anhang B) | 228, davon 172 ohne CE-Referenz (Kandidaten EE oder Legacy; Verifikation: 3 Schlüssel `workspace_empty_state.views.*` sind doch referenziert), zusätzlich 3 referenzierte, aber fehlende Schlüssel |
| Vom CE-Frontend aufgerufene, im CE-Backend fehlende Endpunkte dieses Clusters | 2 (`GET /api/workspaces/{slug}/active-cycles/`, `GET …/cycles/{cycle_id}/cycle-progress/`) |
| Im CE abgelehnte Public-API-Parameter | 2 (`pql`, `filters`) |

---

## 2. Feature-Tabelle

Legende **CE-Status** (gegen Repo geprüft): **fehlt** – keine funktionale Spur außer Texten/Matrix; **Stub/UI-Hülle im CE** – Typen, Store-Plätze, leere Komponenten, tote Service-Aufrufe oder Upsell-Seite vorhanden, Funktion fehlt; **teilweise im CE** – Datenmodell oder Teilfunktion vorhanden; **im CE vorhanden** – siehe Anhang E (kein Bezahl-Feature). Legende **ab Plan**: niedrigster Plan lt. R1; sonst angegebene Quelle; „unklar“ = keine belastbare Quelle. „CS“ = in R1 „Coming soon“. **(Verifikation)** Bei Widerspruch zwischen R1/R2 und einem aktuellen Doku-Label (docs.plane.so, 2026) gilt nach Auftrag die aktuellere/spezifischere Quelle; der Widerspruch ist in der Zeile und im Verifikations-Protokoll dokumentiert. Die Matrix R1 ist erkennbar älter (z. B. „Initiatives“ und „Advanced Pages Analytics“ noch „Coming soon“, Plan „One“ noch gelistet), daher gehen Doku-Labels vor.

| ID | Feature | ab Plan | Abstufung je Plan | CE-Status | Quelle |
|---|---|---|---|---|---|
| P05-01 | Teamspaces – Kern (Anlegen/Ändern/Löschen, Lead, Beschreibung, Logo, Mitglieder, Projekte) | Pro | Free/One –; Pro/Business/Enterprise ✓ | Stub/UI-Hülle im CE | R2 Z. 25–32 („Teamspaces“); WS3; WS17 (Doku-Label „Pro“, Verifikation); `DD/api-reference/teamspace/*`; `V2/teamspaces/*`; `IMG/webhooks/create-webhook.webp` |
| P05-02 | Teamspace-Work-Items (alle Work Items der Teamspace-Projekte, Gruppierung „Team project“) | Pro (abgeleitet aus P05-01, UNVERIFIZIERT) | wie P05-01 | Stub/UI-Hülle im CE | `T/issues/issue.ts` Z. 32; `C/issue/common.ts` Z. 39, 120 |
| P05-03 | Teamspace-Projekt-Work-Items (Projektsicht im Teamspace-Kontext) | Pro (UNVERIFIZIERT) | wie P05-01 | Stub/UI-Hülle im CE | `T/issues/issue.ts` Z. 42; `W/hooks/use-issue-layout-store.ts` Z. 28 |
| P05-04 | Teamspace-Views und Teamspace-Pages | Pro (UNVERIFIZIERT) | wie P05-01 | Stub/UI-Hülle im CE | `T/issues/issue.ts` Z. 36; `T/page/core.ts` Z. 78–83; WS1; Dok. 26 P07-17 |
| P05-05 | Teamspace-Cycles (Cycles mehrerer Projekte gleichzeitig) | Business | Free/One/Pro –; Business/Enterprise ✓ | fehlt | R1 Z. 381–390 |
| P05-06 | Teamspace-Kommentare/-Updates (Beschreibung und Kommentar-Feed mit Assets) | unklar | – | Stub/UI-Hülle im CE | `T/enums.ts` Z. 71, 74, 82, 85 |
| P05-07 | Workspace-Feature „Teamspaces“ (`teams` bzw. v2 `is_teams_enabled`) inkl. Settings-Seite | Pro (folgt P05-01) | – | fehlt | `DD/api-reference/workspace-features/get-workspace-features.md`; `V2/workspace-features/overview.md`; `DD/dev-tools/mcp-server-tools.md` Z. 430; `IMG/webhooks/create-webhook.webp`; WS17 (einmal aktiviert nicht abschaltbar) |
| P05-08 | Teamspace-bezogene Member-Auswahl, Suche, Realtime-Kontext | Pro (UNVERIFIZIERT) | – | Stub/UI-Hülle im CE | `W/components/dropdowns/member/member-select.tsx` Z. 55–65; `packages/editor/src/types/document-collaborative-events.ts` Z. 35–80; `DD/self-hosting/govern/advanced-search.md` (Index `{prefix}_teamspaces`) |
| P05-09 | Dashboards (Workspace-Dashboards anlegen, öffnen, verwalten) | Pro | Free/One –; Pro/Business/Enterprise ✓ | Stub/UI-Hülle im CE | R1 Z. 521–530; R2 („Dashboards + Reports“); `W/components/workspace/sidebar/user-menu.tsx` Z. 34–40 |
| P05-10 | Dashboard-Widgets (Diagrammtypen, Chart-Modelle, Achsen/Metriken, Farbpaletten) | Pro | wie P05-09 | teilweise im CE (Chart-Infrastruktur, Analytics nutzt BASIC/STACKED) | `C/chart.ts` Z. 13–135; `T/analytics.ts` Z. 9–38; `T/charts/*` |
| P05-11 | Dashboard-Filter inkl. PQL (Ebenen source, quick, widget) | unklar (Standard-Filter ≥ Pro wie Dashboards; PQL-Anteil folgt P05-29 = Enterprise Grid, Verifikation) | – | fehlt | WS5, WS6 (nur Titel); WS21; WS23 |
| P05-12 | Dashboard-Widgets für Intake und Custom Properties | unklar | – | fehlt | WS7, WS8 (nur Titel); WS19, WS23 (Verifikation) |
| P05-13 | Dashboard-Widgets in Pages einbetten („Link dashboard widgets“) | Enterprise Grid (Doku-Label „Enterprise“ = Top-Plan, heute „Enterprise Grid“; Verifikation) | nur Top-Plan | fehlt | Dok. 26 P07-42 (WS16); `DD/self-hosting/self-hosting-101.md` Z. 54 (Pläne Free, Pro, Business, Enterprise Grid) |
| P05-14 | Insights („Hindsight, On-demand insights, Foresights“) | Pro (CS) | Pro/Business/Enterprise ✓ | fehlt | R1 Z. 561–571 |
| P05-15 | Erweiterte Analytics-Tabs (Cycles, Modules, Intake, Projekte/Users) mit Tab-Gating | unklar | Text „Upgrade to {plan} to unlock {tab}“ | teilweise im CE (Tab-Architektur mit `isDisabled`) | `L/workspace.json` Z. 134–151; `T/analytics.ts` Z. 42–47 |
| P05-16 | Custom Reports | Business (CS) | Business/Enterprise ✓ | fehlt | R1 Z. 597–606; R1 `planHighlights.business` |
| P05-17 | Time Capsule (Point-in-time-Snapshots) | Business (Zeile auskommentiert, CS) | Business/Enterprise ✓ | fehlt | R1 Z. 573–583 |
| P05-18 | Advanced Pages Analytics | Business (CS in R1; lt. Doku ausgeliefert) | Business/Enterprise ✓ | fehlt | R1 Z. 585–595; Dok. 26 P07-25 |
| P05-19 | Progress Charts (tägliche Fortschrittsreihe v2, Scope-Linie, Burn-down/Burn-up, Ideal) | Pro | Pro/Business/Enterprise ✓ | teilweise im CE (Typen, Utils, No-op-Fetch) | R1 Z. 538–547; `U/cycle.ts` Z. 79–190; `T/cycle/cycle.ts` Z. 53–64, 139, 147–158 |
| P05-20 | Cycle Reports (On-demand während/nach dem Cycle, Permalinks) | Pro | Pro/Business/Enterprise ✓ | teilweise im CE (`progress_snapshot`) | R1 Z. 550–559; `API/db/models/cycle.py` Z. 74 |
| P05-21 | Auto-schedule Cycles (wiederkehrende Cycles; v2-Projekt-Flag `is_automated_cycle_enabled`) | Business (nur University-Kurs, niedrig; Verifikation) | – | fehlt (nur Texte) | `L/project-settings.json` (`project_settings.cycles.auto_schedule.*`); WS11; WS24; `V2/project-features/overview.md` |
| P05-22 | Auto-Rollover (Auto-transfer Cycle Work items) | Pro (R1; Widerspruch: University-Kurs WS24 ordnet Rollover der Business-Cycle-Automation zu) | Pro/Business/Enterprise ✓ | teilweise im CE (nur manueller Transfer; Verifikation, vorher „fehlt“) | R1 Z. 249–258; `project_settings.cycles.auto_schedule.form.auto_rollover.*`; `API/app/urls/cycle.py` Z. 72; `API/utils/cycle_transfer_issues.py` |
| P05-23 | Workspace-weite Active Cycles | One (Matrix); One nicht mehr verkauft → faktisch ab Pro | One/Pro/Business/Enterprise ✓ | Stub/UI-Hülle im CE (Route, Upsell-Seite, Service, Typ, Navigations-Präferenz; kein gerenderter Sidebar-Eintrag; Backend fehlt) | R1 Z. 194–203; R2 `ONE_PLAN_FEATURES`; `W/components/active-cycles/workspace-active-cycles-upgrade.tsx` |
| P05-24 | Parallel Cycles (mehrere aktive Cycles je Projekt) | unklar | – | fehlt (CE verbietet Überschneidung) | `DD/dev-tools/plane-compose.md` Z. 1259; `DD/dev-tools/mcp-server-tools.md` Z. 377; `V2/project-features/overview.md` (`is_parallel_cycles_enabled`) |
| P05-25 | Cycle-Aktionen „Complete“, manuelles Starten/Beenden (v2-Flag `is_manually_start_end_cycles_enabled`) und Archivieren laufender Cycles | unklar | – | fehlt (CE: nur beendete archivierbar) | `DD/dev-tools/mcp-server-tools.md` Z. 250–251; `V2/project-features/overview.md`; Dok. 21 §5 |
| P05-26 | Cycle Updates (Status-Updates On-Track/Off-Track/At-Risk an Cycles) | unklar | – | fehlt; Existenz UNVERIFIZIERT | `L/update.json`; `T/enums.ts` Z. 87–91 (nur generisch) |
| P05-27 | Shared Views (View mit ausgewählten Mitgliedern teilen, je Person view-only oder edit) | Pro | Free/One –; Pro/Business/Enterprise ✓ | fehlt | R1 Z. 499–508; WS9; WS26 |
| P05-28 | Publish Views (View öffentlich im Space-App) | Pro (R1; University „How to Publish (Pro)“, WS25) – widersprüchlich: One (R2 `ONE_PLAN_FEATURES` „public views“) | Pro/Business/Enterprise ✓ | teilweise im CE (`DeployBoard` Typ `view`, `anchor`, „Live“-Badge, Link-Helper, Stub-Hook) | R1 Z. 510–519; R2; WS25; `API/db/models/deploy_board.py` Z. 20–28; `W/components/views/publish/use-view-publish.tsx` |
| P05-29 | PQL (Plane Query Language) in Work-Item-Listen, Cycles, Modules, Views, Teamspace-Work-Items, Workspace-Views, API, Webhooks, Dashboards | Enterprise Grid (Doku-Label WS22; Verifikation) – **Widerspruch:** R1 Pro (ältere Matrix) | R1: Free/One –; Pro/Business/Enterprise ✓ – Doku 2026: nur Enterprise Grid | Stub/UI-Hülle im CE (Public-API lehnt `pql` ab) | WS22; WS21; R1 Z. 658–668; `API/api/views/issue.py` Z. 324–335; `DD/dev-tools/mcp-server-tools.md` Z. 44–58, 254; `DD/dev-tools/intro-webhooks.md` Z. 71–102; `V2/project-views/overview.md`, `V2/workspace-views/overview.md` (`pql_filters`); WS10, WS13 |
| P05-30 | Operator-Kapseln und erweiterte Filteroperatoren (Negation, OR) im Filter-UI | Pro (auskommentierte Matrix-Zeile „Search“, CS) | Free/One „Basic text search“; Pro+ „Operator capsules from text or PQL“ | Stub/UI-Hülle im CE (EXTENDED_* leer, `allowNegative: false`; Backend kann `or`/`not`) | R1 Z. 626–656; `W/hooks/rich-filters/use-filters-operator-configs.ts`; `API/utils/filters/filter_backend.py` Z. 147–210 |
| P05-31 | Advanced Search (Volltext, Fuzzy, Autocomplete, Multi-Entity) | Pro | Doku-Badge `[Pro]` | fehlt (CE: einfache Suche) | `DD/self-hosting/govern/advanced-search.md` Z. 7; `DD/api-reference/issue/advanced-search-work-items.md`; `L/power-k.json` Z. 174; WS12 |
| P05-32 | Scheduled Comms (geplante Reports, Benachrichtigungen, Nachrichten an Dritt-Tools) | Business | Business/Enterprise ✓ | fehlt | R1 Z. 414–423 |
| P05-33 | Workspace Activity Logs (filterbar, ganzer Workspace) | Business | Business/Enterprise ✓ | teilweise im CE (Aktivität je User; No-op-Store-Methode) | R1 Z. 740–749; Dok. 27 P08-17 |
| P05-34 | Home-, Your-Work- und Navigations-Erweiterungen (Home-Widgets „New at Plane“/„Quick tutorial“, Sidebar-Einträge Dashboards/Teamspaces/Active Cycles, Power-K-Ziele) | unklar | – | Stub/UI-Hülle im CE | `W/components/home/home-dashboard-widgets.tsx` Z. 49–58; `API/app/views/workspace/home.py` Z. 31–35; `L/power-k.json` Z. 107–108; `W/components/workspace/sidebar/user-menu.tsx` (nicht gerendert) |
| P05-35 | Text to PQL (natürliche Sprache → PQL, AI) | Enterprise Grid (Blog WS21: „Enterprise-only“; Top-Plan heißt in der Doku „Enterprise Grid“, `DD/self-hosting/self-hosting-101.md` Z. 54; sekundär; Verifikation, neu) | nur Top-Plan | fehlt | WS21; R1 Z. 658–668 („Soon, you can write natural language queries.“); R1 Z. 625–656 (auskommentiert „Search via natural-language queries“) |

---

## 3. Feature-Abschnitte

Aufbau je Feature: **Tier** · **Funktionsbeschreibung (belegt)** · **Ergänzender Entwurf (UNVERIFIZIERT)**, sofern zur Umsetzbarkeit nötig · **UI-Hinweise** · **Datenmodell-Hinweise** · **API-Hinweise** · **CE-Status** · **Migrationshinweis** · **Quellen** · **Konfidenz**. Wörtliche UI-Texte stammen aus `L/*.json` und sind 1:1 zu übernehmen (ADR-005/ADR-006). Alle Datenmodell- und API-Vorschläge folgen ADR-003 (Greenfield, `snake_case`-JSON, fachliche Semantik des Originals).

### 3.1 Teamspaces

#### P05-01 – Teamspaces (Kern)

- **Tier:** Pro (R2 Z. 25–32 `PRO_PLAN_FEATURES` enthält „Teamspaces“; WS3; Doku-Label „Pro“ und University-Kurs 201/08 „Pro-tier“, WS17 – Verifikation). Keine eigene Zeile in R1 – nur „Teamspace Cycles“ (Business, P05-05).
- **Funktionsbeschreibung (belegt):**
  - Zweck: „Teamspaces allow you to organize teams, projects, and members within a workspace, providing a way to group related work and manage access at a team level.“ (`DD/api-reference/teamspace/overview.md`).
  - Teamspace-Objekt: `id` (uuid), `name` (string, **Pflicht**), `description_json` (object), `description_html` (string), `description_stripped` (string), `description_binary` (string), `logo_props` (object), `lead` (uuid, Benutzer), `workspace` (uuid), `created_at`, `updated_at`, `created_by`, `updated_by` (`DD/api-reference/teamspace/overview.md`).
  - Mitglieder werden über `member_ids` hinzugefügt/entfernt; Antwort: User-Objekte `{id, first_name, last_name, email, avatar, avatar_url, display_name}` (`DD/api-reference/teamspace/add-teamspace-members.md`; Dok. 21 TS6–TS8).
  - Projekte werden über `project_ids` hinzugefügt/entfernt (`DD/api-reference/teamspace/add-projects-to-teamspace.md`; Dok. 21 TS9–TS11).
  - Workspace-Settings, Gruppe „Features“, enthalten den Eintrag **„Teamspaces“** (zwischen „Connections“ und „Initiatives“) (`IMG/webhooks/create-webhook.webp`).
  - Teamspaces sind über Advanced Search auffindbar (Index `{prefix}_teamspaces` „Teamspace discovery“, `DD/self-hosting/govern/advanced-search.md` Z. 289).
  - OAuth-Scopes `teamspaces:read|write`, `teamspaces.members:read|write`, `teamspaces.projects:read|write` (Dok. 21 §6; Dok. 28 Z. 2068–2073).
  - Beschreibung ist ein Rich-Text-Dokument mit eingebetteten Assets (`EFileAssetType.TEAM_SPACE_DESCRIPTION`, `T/enums.ts` Z. 71) und Teil von `TEditorAssetType` (Z. 82).
  - Gruppenüberschrift „Members & Teamspaces“ (`L/common.json` Z. 715, `common.members_and_teamspaces`) – Einsatzort im CE nicht referenziert (vermutlich Abschnitt in Member-Dropdowns oder Settings, UNVERIFIZIERT).
  - **(Verifikation, sekundär WS17/WS18):** Doku-Label „Pro“; Anlegen mit den Feldern Name, Team lead, Team members; beim Verknüpfen eines Projekts erhalten **alle Teamspace-Mitglieder automatisch Member-Zugriff** auf das Projekt; Team Leads erhalten dadurch **keine** besonderen Workspace-Rechte. Teamspace-Ansicht: Overview mit Aktivitäten aller verknüpften Projekte und Navigation Work items / Cycles / Views / Pages.
  - **API v2 (Verifikation, `V2/teamspaces/overview.md`, `update-teamspace.md`):** Objekt `{id, name, description_html, lead_id, logo_props, member_ids[], project_ids[], created_at, created_by_id}`; Endpunkte `GET/POST /api/v2/workspaces/{slug}/teamspaces/`, `GET/PATCH/DELETE …/teamspaces/{pk}/`; `PATCH` mit `member_ids`/`project_ids` **ersetzt** die jeweilige Menge („Replaces the current set“); `name` max. 255 Zeichen; `lead_id` und `logo_props` nullable; `?expand=lead`; Fehler `402 payment_required` „The feature this endpoint belongs to isn't enabled on your plan or is switched off“ (entfällt nach ADR-001 bis auf den Fall „switched off“), `409 conflict` bei Geschäftsregel-Verstoß. Scope `teamspaces:write`.
- **Ergänzender Entwurf (UNVERIFIZIERT):** Teamspace-Liste unter `/:workspaceSlug/teamspaces`; Detail mit Tabs „Overview“, „Work items“, „Cycles“, „Views“, „Pages“ (Tabs sekundär belegt, WS18; Routen UNVERIFIZIERT); Overview mit Beschreibung, Lead, Mitglieder-Avataren, Projekt-Liste, Fortschritt und Kommentar-/Update-Feed (P05-06). Anlegen nur durch Workspace-Admins (UNVERIFIZIERT); Lead verwaltet Mitglieder/Projekte (UNVERIFIZIERT). Teamspace-Mitglieder müssen Workspace-Mitglieder sein; Gäste nicht (UNVERIFIZIERT).
- **UI-Hinweise:** Icons `TeamspacesOutline`/`TeamspacesFilled` (`PROPEL/icons/workspace-features/teamspaces-*.d.ts`); Leerzustand-Illustration `teamspace` (vertikaler Stapel, `B/empty-state/assets/vertical-stack/teamspace.tsx`, Registry `B/empty-state/assets/asset-registry.tsx` Z. 134). Logo-Auswahl wie bei Projekten (`logo_props` = `TLogoProps`, vgl. `migration/analysis/02b-datenmodell-arbeitsobjekte.md` Z. 878). Beschreibung mit dem Rich-Text-Editor (Asset-Typ s. o.).
- **Datenmodell-Hinweise (Vorschlag, EF Core):**
  - `teamspaces(id uuid PK, workspace_id FK, name varchar(255) NOT NULL, description_json jsonb, description_html text, description_stripped text, description_binary bytea, logo_props jsonb, lead_id uuid NULL FK users, sort_order double, created_at, updated_at, created_by_id, updated_by_id, deleted_at)`; Unique `(workspace_id, lower(name)) WHERE deleted_at IS NULL` (analog CE-Legacy-Modell `Team`, `API/db/models/workspace.py` Z. 271–279 – UNVERIFIZIERT für EE).
  - `teamspace_members(id, teamspace_id FK, member_id FK users, workspace_id, created_*, deleted_at)`, Unique `(teamspace_id, member_id) WHERE deleted_at IS NULL`.
  - `teamspace_projects(id, teamspace_id FK, project_id FK, workspace_id, sort_order, created_*, deleted_at)`, Unique `(teamspace_id, project_id)`.
  - `teamspace_user_properties(teamspace_id, user_id, filters/rich_filters jsonb, display_filters jsonb, display_properties jsonb)` analog `CycleUserProperties` (`API/db/models/cycle.py` Z. 130–157) für die Work-Item-Ansichten (P05-02).
  - Das CE-Modell `Team` (`API/db/models/workspace.py` Z. 261–283: `name`, `description`, `workspace`, `logo_props`) ist ein Legacy-Rest ohne Mitglieder und **nicht** zu portieren.
- **Seiteneffekt (Verifikation, WS17):** Projekt-Verknüpfung legt für jedes Teamspace-Mitglied eine Projektmitgliedschaft mit Rolle Member an (bzw. hebt sie nicht ab, wenn bereits höher – UNVERIFIZIERT); Verhalten beim Entfernen der Verknüpfung UNVERIFIZIERT (O-02).
- **API-Hinweise:** Public-API v1 (belegt): `GET/POST /api/v1/workspaces/{slug}/teamspaces/` (Liste cursor-paginiert `per_page` Default 20, max 100), `GET/PATCH/DELETE …/teamspaces/{teamspace_id}/`, `GET/POST/DELETE …/teamspaces/{teamspace_id}/members/` (Body `member_ids`), `GET/POST/DELETE …/teamspaces/{teamspace_id}/projects/` (Body `project_ids`) (`DD/api-reference/teamspace/*.md`; Dok. 21 TS1–TS11). Interne App-API (Vorschlag): spiegelbildlich unter `/api/workspaces/{slug}/teamspaces/…` plus `GET …/teamspaces/{id}/issues/` (P05-02), `…/cycles/` (P05-05), `…/views/` (P05-04), `…/pages/` (P05-04), `…/comments/` (P05-06), `…/activities/`.
- **CE-Status:** Stub/UI-Hülle (Anhang A, A-01 … A-20).
- **Migrationshinweis:** Feature-Toggle `teams` (P05-07) bleibt als fachliche Einstellung (ADR-001). Teamspace-Beschreibung als kollaboratives Dokument über den YDotNet-Realtime-Server (ADR-002) nur, falls EE es so betreibt (UNVERIFIZIERT) – Minimal: HTML/JSON speichern wie CE-Projektbeschreibung.
- **Konfidenz:** hoch (Existenz, API, Felder); niedrig (UI-Aufbau, Rechte).

#### P05-02 – Teamspace-Work-Items

- **Tier:** Pro (abgeleitet aus P05-01; UNVERIFIZIERT).
- **Funktionsbeschreibung (belegt durch CE-Plumbing):**
  - Eigener Issue-Store-Typ `EIssuesStoreType.TEAM` (`T/issues/issue.ts` Z. 32); Ermittlung aus Route: nur `teamspaceId` gesetzt → `TEAM` (`W/hooks/use-issue-layout-store.ts` Z. 40).
  - Ansicht ist **workspace-level** (`isWorkspaceLevel` enthält `TEAM`, `W/components/issues/issue-layouts/utils.tsx` Z. 95–104) → Gruppierungsspalten wie bei Workspace-Views (Projekt-übergreifend).
  - Zusätzliche Gruppierung **„Team project“** (`team_project`, Label `common.team_project` = „Team project“, `C/issue/common.ts` Z. 120 mit Kommentar „required this on team issues“), intern auf `project_id` gemappt (`C/issue/common.ts` Z. 39; `W/store/issue/helpers/base-issues.store.ts` Z. 126, 140); Filter-Schlüssel `team_project` (`T/view-props.ts` Z. 140; `W/store/issue/helpers/issue-filter-helper.store.ts` Z. 146); Spaltenquelle `getTeamProjectColumns` (CE: `undefined`, `utils.tsx` Z. 846).
  - Anlage neuer Work Items aus dieser Ansicht vorgesehen (`TCreateModalStoreTypes` enthält `TEAM`, `C/issue/common.ts` Z. 102–111); Drag & Drop zwischen Gruppen vorgesehen (`W/hooks/use-group-dragndrop.ts` Z. 29).
  - Query-Parameter-Ermittlung kennt `viewType` `"team_issues"` (`U/work-item/base.ts` Z. 104–113) – die zugehörigen Display-Filter-Konfigurationen fehlen im CE-Objekt `ISSUE_DISPLAY_FILTERS_BY_PAGE` (`C/issue/filter.ts` Z. 112–295).
- **(Verifikation, sekundär WS18):** „bird's-eye view“ aller Work Items des Teams über alle Projekte; ältere Doku nennt zwei Tabs: **„Team“** (Work Items, die Teamspace-Mitgliedern zugewiesen sind) und **„Project“** (alle Work Items der verknüpften Projekte). PQL ist in „Teamspace work items“ verfügbar (WS22, P05-29).
- **Ergänzender Entwurf (UNVERIFIZIERT):** Layouts wie Workspace-Views (List, Kanban, Calendar, Spreadsheet, Gantt), Filter wie `my_issues` plus `team_project`; Datenmenge = Work Items aller Projekte in `teamspace_projects`, auf die der Benutzer Zugriff hat; Tab „Team“ = zusätzlich `assignees ∩ teamspace_members`.
- **UI-Hinweise:** identische Layout-Komponenten wie Projekt-/Workspace-Ansicht (`migration/analysis/09-frontend-arbeitsobjekte-layouts.md`).
- **Datenmodell-Hinweise:** keine neue Fachtabelle; Benutzer-Ansichtseinstellungen in `teamspace_user_properties` (P05-01).
- **API-Hinweise (Vorschlag):** `GET /api/workspaces/{slug}/teamspaces/{teamspace_id}/issues/?…` mit derselben Grouped-Pagination wie `GET /api/workspaces/{slug}/issues/` (CE-Workspace-Issues).
- **CE-Status:** Stub/UI-Hülle (Stores `teamIssues`/`teamIssuesFilter` werden im CE mit Projekt-Store-Klassen instanziiert, `W/store/issue/root.store.ts` Z. 80–81, 148–149, 242–243; Hook-Mapping `W/hooks/store/use-issues.ts` Z. 40, 106–109).
- **Konfidenz:** hoch (Existenz, Gruppierung), mittel (Umfang).

#### P05-03 – Teamspace-Projekt-Work-Items

- **Tier:** Pro (UNVERIFIZIERT).
- **Funktionsbeschreibung (belegt):** Store-Typ `TEAM_PROJECT_WORK_ITEMS` (`T/issues/issue.ts` Z. 42); Route enthält `teamspaceId` **und** `projectId` (`W/hooks/use-issue-layout-store.ts` Z. 28); workspace-level (`utils.tsx` Z. 102); `viewType` `"team_project_work_items"` (`U/work-item/base.ts` Z. 113); eigene Stores `teamProjectWorkItems`/`teamProjectWorkItemsFilter` (`W/store/issue/root.store.ts` Z. 95–96, 166–167, 257–258).
- **Ergänzender Entwurf (UNVERIFIZIERT):** Innerhalb eines Teamspace die Work Items eines einzelnen Teamspace-Projekts mit Teamspace-spezifischen Ansichtseinstellungen anzeigen (getrennt von den persönlichen Projekt-Einstellungen).
- **Datenmodell-/API-Hinweise (Vorschlag):** `GET /api/workspaces/{slug}/teamspaces/{teamspace_id}/projects/{project_id}/issues/`; Ansichtseinstellungen je `(teamspace_id, project_id, user_id)`.
- **CE-Status:** Stub/UI-Hülle.
- **Konfidenz:** mittel.

#### P05-04 – Teamspace-Views und Teamspace-Pages

- **Tier:** Pro (UNVERIFIZIERT; folgt P05-01).
- **Funktionsbeschreibung (belegt):**
  - Views: Store-Typ `TEAM_VIEW` (`T/issues/issue.ts` Z. 36), Route mit `teamspaceId` und `viewId` (`W/hooks/use-issue-layout-store.ts` Z. 26), Stores `teamViewIssues`/`teamViewIssuesFilter` (`W/store/issue/root.store.ts` Z. 92–93, 160–161, 251–252), Create-Modal unterstützt `TEAM_VIEW` (`C/issue/common.ts` Z. 105).
  - Pages: Live-Server-Dokumenttyp `"team_page"` mit `teamId` (`T/page/core.ts` Z. 78–83); Realtime-Ereignisse tragen `teamspace_id` (`packages/editor/src/types/document-collaborative-events.ts` Z. 43, 60, 75); Seiten-Verschieben-Dialog: „Private and shared pages cannot be moved to a teamspace.“, Platzhalter „Search for projects and teamspaces“, „Search for wiki collections, projects, and teamspaces“ (`L/page.json` Z. 85–91).
  - Teamspace-Pages (WS1, WS2 via Dok. 26 P07-17): Tab „Pages“; nur für Teamspace-Mitglieder sichtbar; immer öffentlich im Teamspace (keine Private-Option); Member dürfen sehen, erstellen, bearbeiten, duplizieren, verschieben, exportieren, favorisieren; archivieren/löschen nur eigene; Lead darf jede Seite archivieren/wiederherstellen/löschen; Nested Pages und Templates verfügbar; Publish und Work-Item-Links nicht.
- **(Verifikation, sekundär WS18):** Teamspace-Views: eigene Views des Teamspace **oder** alle Views der verknüpften Projekte per Tab-Wechsel; Teamspace-Pages als Wissensbasis getrennt von Wiki und Projekt-Pages.
- **Datenmodell-Hinweise (Vorschlag):** `issue_views.teamspace_id uuid NULL` (View-Scope: Projekt **oder** Workspace **oder** Teamspace; CE kennt Projekt/Workspace über `project` NULL, `API/db/models/view.py` Z. 58–99); `pages.teamspace_id uuid NULL` bzw. Scope-Enum `project|workspace|teamspace`.
- **API-Hinweise (Vorschlag):** `…/teamspaces/{id}/views/` (CRUD wie Projekt-Views), `…/teamspaces/{id}/views/{view_id}/issues/`, `…/teamspaces/{id}/pages/` (CRUD wie Projekt-Pages).
- **Migrationshinweis:** Realtime-Dokumentkontext im YDotNet-Server um `team_page` erweitern (ADR-002); Berechtigungsprüfung über Teamspace-Mitgliedschaft.
- **Konfidenz:** hoch (Existenz), mittel (Rechte, aus sekundärer Quelle).

#### P05-05 – Teamspace-Cycles

- **Tier:** Business (R1 Z. 381–390: Free/One/Pro `false`, Business/Enterprise `true`).
- **Funktionsbeschreibung (belegt):** „See multiple cycles in multiple projects at once.“ (R1 Z. 383).
- **(Verifikation, sekundär WS18):** Cycles-Ansicht des Teamspace bündelt die Cycles aller verknüpften Projekte; laut Produktseite zusätzlich Beitrag je Person zum Cycle („who's falling behind“).
- **Ergänzender Entwurf (UNVERIFIZIERT):** Tab „Cycles“ im Teamspace mit allen Cycles der Teamspace-Projekte, gruppiert nach Status (`TCycleGroups` = `current`, `upcoming`, `completed`, `draft`, `T/cycle/cycle.ts` Z. 4); für laufende Cycles dieselben Karten wie P05-23 (Progress, Burndown, Priority-Items). Keine eigenen Teamspace-Cycle-Entitäten – Aggregation bestehender Projekt-Cycles.
- **API-Hinweise (Vorschlag):** `GET /api/workspaces/{slug}/teamspaces/{teamspace_id}/cycles/?cycle_view=current|upcoming|completed|draft`.
- **CE-Status:** fehlt.
- **Konfidenz:** niedrig.

#### P05-06 – Teamspace-Kommentare / -Updates

- **Tier:** unklar.
- **Funktionsbeschreibung (belegt):** Asset-Typ `TEAM_SPACE_COMMENT_DESCRIPTION` (`T/enums.ts` Z. 74, 85) → Teamspaces besitzen Kommentare mit Rich-Text und Datei-Assets. WS1 (sekundär): Kommentare bleiben im Teamspace sichtbar; Lead darf jeden Kommentar löschen. **(Verifikation, WS18):** Changelog v3.2.0 nennt Teamspace-Kommentare ausdrücklich (Admins können Kommentare an Work Items, Pages und Teamspaces mit Grund abuse/spam/off-topic/sensitive info/other aus- und einblenden – Moderationsfunktion des Governance-Clusters, hier nur als Anforderung an das Kommentarmodell: Felder `is_hidden`, `hidden_reason`, `hidden_by`, `hidden_at` – Vorschlag); Overview-Feed „real-time team updates, collated from across projects“ (Produktseite).
- **Ergänzender Entwurf (UNVERIFIZIERT):** Overview-Feed mit Kommentaren und Aktivitäten (Mitglied/Projekt hinzugefügt/entfernt, Lead geändert, Beschreibung geändert), Reaktionen wie bei Work-Item-Kommentaren. Ob Status-Updates (`L/update.json`, `EUpdateStatus`) auch für Teamspaces existieren, ist nicht belegt.
- **Datenmodell-Hinweise (Vorschlag):** `teamspace_comments(id, teamspace_id, workspace_id, actor_id, comment_json jsonb, comment_html text, comment_stripped text, parent_id NULL, edited_at, created_*, deleted_at)`, `teamspace_comment_reactions(comment_id, actor_id, reaction)`, `teamspace_activities(id, teamspace_id, actor_id, verb, field, old_value, new_value, old_identifier, new_identifier, comment, created_at)`; Backend-Enum `FileAsset.EntityTypeContext` um `TEAM_SPACE_DESCRIPTION`, `TEAM_SPACE_COMMENT_DESCRIPTION` erweitern (CE-Backend kennt sie nicht, `API/db/models/asset.py` Z. 36–46).
- **CE-Status:** Stub/UI-Hülle (nur Frontend-Enum).
- **Konfidenz:** mittel (Kommentare), niedrig (Updates).

#### P05-07 – Workspace-Feature „Teamspaces“ (`teams`)

- **Tier:** Pro (folgt P05-01).
- **Funktionsbeschreibung (belegt):** Workspace-Feature-Flags `{project_grouping, initiatives, teams, customers, wiki, pi}` (`DD/api-reference/workspace-features/get-workspace-features.md`; MCP `workspace update_features` mit `teams`, `DD/dev-tools/mcp-server-tools.md` Z. 430). Settings-Navigation „Features → Teamspaces“ (`IMG/webhooks/create-webhook.webp`).
- **(Verifikation, korrigiert):** Laut Doku (WS17, sekundär) wird das Feature in Workspace Settings → Tab „Teamspaces“ eingeschaltet und kann **danach nicht mehr abgeschaltet werden** („Once on, the feature cannot be turned off in a workspace“). Die ursprüngliche Annahme eines beidseitigen Schalters ist damit widerlegt. API v2 führt das Flag als `is_teams_enabled` („Whether teamspaces are available“, `V2/workspace-features/overview.md`); v1/MCP als `teams`.
- **Ergänzender Entwurf (UNVERIFIZIERT):** Settings-Seite „Teamspaces“ mit einmaligem Aktivierungs-Schalter (danach gesperrt) und Liste der Teamspaces; vor der Aktivierung sind Teamspace-Navigation und -Routen ausgeblendet. Ob `PATCH …/features/` mit `teams: false` serverseitig abgelehnt wird (z. B. 409), ist UNVERIFIZIERT.
- **Datenmodell-Hinweise (Vorschlag):** `workspace_features(workspace_id PK, project_grouping bool, initiatives bool, teams bool, customers bool, wiki bool, pi bool, …)`.
- **API-Hinweise:** `GET/PATCH /api/v1/workspaces/{slug}/features/` (Scopes `workspaces.features:read|write`).
- **CE-Status:** fehlt.
- **Migrationshinweis:** Toggle bleibt (fachliche Einstellung, ADR-001), Default `false` mit einmaliger Aktivierung analog Original (Verifikation; vorher „Default `true`“ ohne Beleg).
- **Konfidenz:** hoch (Flag), niedrig (Settings-UI).

#### P05-08 – Teamspace-bezogene Querschnittsfunktionen

- **Tier:** Pro (UNVERIFIZIERT).
- **Funktionsbeschreibung (belegt):**
  - Member-Dropdown: „EE sources a paginated members "lite" resource with server-side scopes (`scope`, `teamspaceId`, `scopedProjectIds`, `getPage`)“ (`W/components/dropdowns/member/member-select.tsx` Z. 55–65) → Mitglieder-Auswahl kann auf Teamspace-Mitglieder eingeschränkt werden; serverseitig paginiert.
  - Filter-HOC kennt Entitätstyp „teamspace“ (`W/components/work-item-filters/filters-hoc/shared.ts` Z. 13; `packages/shared-state/src/store/work-item-filters/filter.store.ts` Z. 31).
  - Router-Getter `teamspaceId` (`W/store/router.store.ts` Z. 18, 45, 80–84) und Spiegelung in `IssueRootStore.teamspaceId` (`W/store/issue/root.store.ts` Z. 46, 114, 181, 205).
  - **(Verifikation, ergänzt):** Auch Cycle-, Modul- und State-Auswahl lesen in EE paginierte „lite“-Ressourcen mit `scopedProjectIds` (projektübergreifende Auswahl, z. B. in Teamspace- oder Workspace-Ansichten): `W/components/dropdowns/cycle/cycle-select.tsx` Z. 62–63, `W/components/dropdowns/module/module-select.tsx` Z. 55–56, `W/components/dropdowns/state/state-select.tsx` Z. 53–55 (dort zusätzlich `typeId`, `isForWorkItemCreation` für Workflow-Gating). Der Teamspace-Bezug von `scopedProjectIds` ist UNVERIFIZIERT.
- **API-Hinweise (Vorschlag):** `GET /api/workspaces/{slug}/members/lite/?scope=…&teamspace_id=…&project_ids=…&cursor=…&search=…`.
- **CE-Status:** Stub/UI-Hülle.
- **Konfidenz:** mittel.

### 3.2 Dashboards & Widgets

#### P05-09 – Dashboards

- **Tier:** Pro (R1 Z. 521–530: „Dashboards and Widgets – Create your own dashboards with custom widgets and data types.“, Free/One `false`, Pro/Business/Enterprise `true`; R2 `PRO_PLAN_FEATURES` „Dashboards + Reports“; Upgrade-Modal „Dashboards, Workflows, Approvals, Time Management, and other superpowers are just a click away.“ `W/components/license/modal/upgrade-modal.tsx` Z. 70).
- **Funktionsbeschreibung (belegt):**
  - Navigation: Eintrag `{key: "dashboards", labelTranslationKey: "workspace_dashboards" („Dashboards“), href: "/{workspaceSlug}/dashboards/", access: [ADMIN, MEMBER], Icon: DashboardsOutline}` im (im CE nicht gerenderten) `SidebarUserMenu` zwischen „Home“ und „Your work“ (`W/components/workspace/sidebar/user-menu.tsx` Z. 26–62, Eintrag Z. 34–40) → Gäste sehen keine Dashboards.
  - Leerzustand der Dashboard-Liste: Titel „Visualize your progress with dashboards“, Beschreibung „Build customizable dashboards to track metrics, measure outcomes, and present insights effectively.“, CTA „Create new dashboard“ (`L/empty-state.json` Z. 184–188, `workspace_empty_state.dashboard.*`); Illustration `dashboard` (`B/empty-state/assets/asset-types.ts` Z. 50, Registry Z. 113).
  - Workspace-Slug `dashboard` ist reserviert (`C/workspace.ts` Z. 63; identisch `API/utils/constants.py` `RESTRICTED_WORKSPACE_SLUGS`).
  - Release-Historie (nur Titel): Dashboard-Neuerungen in Commercial v3.1.0 (WS4), „PQL in dashboards“ (WS5), „PQL dashboard filters“ (WS6), „dashboard intake widgets“ (WS7), „dashboard custom properties“ (WS8).
- **Ergänzender Entwurf (UNVERIFIZIERT):** Liste aller Dashboards des Workspace (Name, Owner, Favorit), „Create new dashboard“-Modal (Name, optional Beschreibung, Projekt-Scope), Dashboard-Detailseite mit Raster aus Widgets (Hinzufügen, Bearbeiten, Verschieben, Größe ändern, Löschen, Duplizieren), Dashboard-Filter (P05-11) im Kopf, Favorisieren, Löschen mit Bestätigung. Sichtbarkeit: privat/öffentlich im Workspace analog `IssueView.access`.
- **UI-Hinweise:** Icons `DashboardsOutline`/`DashboardsFilled` (`PROPEL/icons/workspace-features/dashboards-*`), `WidgetOutline`/`WidgetFilled` (`PROPEL/icons/miscellaneous/widget-*`), Diagramm-Icons `AreaOutline`, `BarOutline`, `DonutOutline`, `LineOutline`, `PieOutline` (+ `*Filled`) (`PROPEL/icons/charts/`). Chart-Komponenten liegen bereits im CE-Paket `@plane/blocks` (`B/charts/{area-chart,bar-chart,line-chart,pie-chart,radar-chart,tree-map,components}`).
- **Datenmodell-Hinweise (Vorschlag):** `dashboards(id, workspace_id, name varchar(255), description text, logo_props jsonb, owned_by_id, access smallint (0 private, 1 public – UNVERIFIZIERT), project_ids uuid[] oder Join-Tabelle dashboard_projects, filters jsonb (Rich-Filter-Ausdruck), pql text NULL, sort_order double, created_*, deleted_at)`; Favoriten über bestehende `user_favorites.entity_type = "dashboard"` (CE-Favoritenmodell ist generisch, `API/db/models/favorite.py` Z. 20).
- **API-Hinweise (Vorschlag):** `GET/POST /api/workspaces/{slug}/dashboards/`, `GET/PATCH/DELETE /api/workspaces/{slug}/dashboards/{dashboard_id}/`. **Kollisionsgefahr:** das CE kennt Legacy-Endpunkte des alten Home-Dashboards `GET /api/users/me/workspaces/{slug}/dashboard/` (`API/app/urls/user.py` Z. 80) und vom Frontend-Service `/api/workspaces/{slug}/dashboard/`, `/api/dashboard/{id}/widgets/{widgetId}/` (`W/services/dashboard.service.ts`, `packages/services/src/dashboard/dashboard.service.ts`) – diese sind **nicht** die Bezahl-Dashboards; neue Routen im Plural `dashboards`.
- **CE-Status:** Stub/UI-Hülle.
- **Migrationshinweis:** Angular-Route `/:workspaceSlug/dashboards` und `/:workspaceSlug/dashboards/:dashboardId`; Sidebar-Benutzermenü gemäß `SIDEBAR_USER_MENU_ITEMS` rendern (P05-34).
- **Konfidenz:** hoch (Existenz, Navigation, Leerzustand), niedrig (Detail-UI).

#### P05-10 – Dashboard-Widgets

- **Tier:** Pro (wie P05-09).
- **Funktionsbeschreibung (belegt, aus CE-Konstanten/Typen, die nur EE-Widgets voll nutzen):**
  - **Chart-Modelle** `EChartModels`: `BASIC`, `STACKED`, `GROUPED`, `MULTI_LINE`, `COMPARISON`, `PROGRESS` (`C/chart.ts` Z. 32–39). Die CE-Analytics verwenden nur `BASIC` (ohne Gruppierung) und `STACKED` (mit `group_by`) (`W/components/analytics/work-items/priority-chart.tsx` Z. 87–137).
  - **X-Achsen-Eigenschaften** `ChartXAxisProperty`: `STATES`, `STATE_GROUPS`, `LABELS`, `ASSIGNEES`, `ESTIMATE_POINTS`, `CYCLES`, `MODULES`, `PRIORITY`, `START_DATE`, `TARGET_DATE`, `CREATED_AT`, `COMPLETED_AT`, `CREATED_BY`, `WORK_ITEM_TYPES`, `PROJECTS`, `EPICS` (`T/analytics.ts` Z. 9–26). CE-Backend unterstützt davon nur die ersten 13 (`API/utils/build_chart.py` Z. 19–33); `WORK_ITEM_TYPES`, `PROJECTS`, `EPICS` sind EE.
  - **Y-Metriken** `ChartYAxisMetric`: `WORK_ITEM_COUNT`, `ESTIMATE_POINT_COUNT`, `PENDING_WORK_ITEM_COUNT`, `COMPLETED_WORK_ITEM_COUNT`, `IN_PROGRESS_WORK_ITEM_COUNT`, `WORK_ITEM_DUE_THIS_WEEK_COUNT`, `WORK_ITEM_DUE_TODAY_COUNT`, `BLOCKED_WORK_ITEM_COUNT`, `EPIC_WORK_ITEM_COUNT` (`T/analytics.ts` Z. 28–38). CE-UI bietet nur „Work item“, „Estimate“, „Epic“ (`C/analytics/common.ts` `ANALYTICS_Y_AXIS_VALUES`), CE-Backend filtert nur `WORK_ITEM_COUNT` (`API/utils/build_chart.py` Z. 37–41).
  - **Datumsgruppierung** `ChartXAxisDateGrouping`: `DAY`, `WEEK`, `MONTH`, `YEAR` (`C/chart.ts` Z. 13–18) für Datums-Achsen `START_DATE`, `TARGET_DATE`, `CREATED_AT`, `COMPLETED_AT` (`CHART_X_AXIS_DATE_PROPERTIES`, Z. 25–30). Beschriftung: DAY → „MMM d“ (aktuelles Jahr) bzw. „MMM d, yyyy“; WEEK → „{MMM}, Week {n}“ (Woche des Monats); MONTH → „MMM“ bzw. „MMM, yyyy“; YEAR → „yyyy“; leere Werte → „None“ (`W/components/chart/utils.ts` Z. 19–55).
  - **Großschreibung** des ersten Buchstabens für `PRIORITY`, `STATE_GROUPS` (`TO_CAPITALIZE_PROPERTIES`, `C/chart.ts` Z. 20–23).
  - **Datenformat** einer Widget-Antwort: `TChart = {data: TChartDatum[], schema: Record<string,string>}`, `TChartDatum = {key, name, count} & Record<groupKey, number>` (`T/charts/common.ts` Z. 9–18); fehlende Gruppenwerte werden mit `0` aufgefüllt (`W/components/chart/utils.ts` Z. 57–117, Kommentar „WIDGET_X_AXIS_DATE_PROPERTIES“ belegt die Herkunft aus den Widgets).
  - **Farbpaletten** `TChartColorScheme` = `modern` | `horizon` | `earthen` mit je 10 Light-/Dark-Farben; i18n-Labels `dashboards.widget.color_palettes.{modern,horizon,earthen}` (**fehlen** in `L/*.json`) (`C/chart.ts` Z. 41–135; `T/charts/common.ts` Z. 7). Mehr Serien als 10 Farben → HSL-Interpolation `generateExtendedColors` (`W/components/chart/utils.ts` Z. 118–175).
  - Achsenbeschriftungen „X-axis“, „Y-axis“, „Metric“ (`L/common.json`, `chart.*`, ohne CE-Referenz); Achsenlabel-Klasse `uppercase text-tertiary/60 text-13 tracking-wide` (`C/chart.ts` Z. 10–11).
  - Chart-Primitive mit Widget-tauglichen Optionen: Balken-Varianten `bar` | `lollipop` | `lollipop-dotted` (`T/charts/index.ts` `TBarChartShapeVariant`), Area mit `comparisonLine`, Pie/Donut mit `innerRadius`, `centerLabel`, `customLegend`, TreeMap, Radar, Scatter (`T/charts/index.ts`; `B/charts/*`).
- **Ergänzender Entwurf (UNVERIFIZIERT) – Widget-Typ × Modell:**

| Widget-Typ (Icon) | zulässige Modelle | Darstellung |
|---|---|---|
| Bar (`BarOutline`) | BASIC, STACKED, GROUPED | Balken je X-Wert; STACKED/GROUPED je `group_by`-Wert; Varianten bar/lollipop |
| Line (`LineOutline`) | BASIC, MULTI_LINE | Linie je Serie |
| Area (`AreaOutline`) | BASIC, STACKED, COMPARISON | Fläche; COMPARISON mit Vergleichslinie (`comparisonLine`) |
| Donut (`DonutOutline`) | BASIC, PROGRESS | Ring; PROGRESS mit Mittelwert (`centerLabel`, z. B. „{completed}/{total}“) |
| Pie (`PieOutline`) | BASIC | Torte |
| Number | BASIC | große Kennzahl (`count`, vgl. `API/utils/build_chart.py` Z. 101–108 – Aggregat ohne X-Achse) |

  Konfiguration je Widget: Name, Typ, Modell, X-Achse, Y-Metrik, Gruppierung, Datumsgruppierung, Farbpalette, Legende/Tooltip an/aus, Widget-Filter; Layout `{x, y, w, h}` im Raster.
- **Semantik der Y-Metriken (Vorschlag, aus Namen abgeleitet, UNVERIFIZIERT):** `WORK_ITEM_COUNT` = Anzahl; `ESTIMATE_POINT_COUNT` = Summe der Estimate-Werte (nur Estimate-Typ `points`, vgl. CE-Cycle-Progress `API/app/views/cycle/base.py` Z. 669–715); `PENDING_WORK_ITEM_COUNT` = State-Gruppe ∉ {completed, cancelled}; `COMPLETED_WORK_ITEM_COUNT` = Gruppe completed; `IN_PROGRESS_WORK_ITEM_COUNT` = Gruppe started; `WORK_ITEM_DUE_THIS_WEEK_COUNT` = `target_date` in aktueller Woche; `WORK_ITEM_DUE_TODAY_COUNT` = `target_date` = heute; `BLOCKED_WORK_ITEM_COUNT` = hat Relation „blocked_by“ zu nicht abgeschlossenem Work Item; `EPIC_WORK_ITEM_COUNT` = Anzahl Epics (Work-Item-Typ `is_epic`).
- **Datenmodell-Hinweise (Vorschlag):** `dashboard_widgets(id, dashboard_id FK, workspace_id, name varchar(255), chart_type varchar (BAR_CHART|LINE_CHART|AREA_CHART|DONUT_CHART|PIE_CHART|NUMBER), chart_model varchar (EChartModels), x_axis_property varchar (ChartXAxisProperty) NULL, x_axis_date_grouping varchar NULL, y_axis_metric varchar (ChartYAxisMetric), group_by varchar NULL, config jsonb {color_scheme, show_legend, show_tooltip, orientation, bar_variant, …}, filters jsonb, layout jsonb {x,y,w,h}, sort_order, created_*, deleted_at)`.
- **API-Hinweise (Vorschlag):** `GET/POST …/dashboards/{id}/widgets/`, `PATCH/DELETE …/widgets/{widget_id}/`, `GET …/widgets/{widget_id}/charts/?` → `TChart`; serverseitige Aggregation als Erweiterung des CE-Chart-Builders (`API/utils/build_chart.py`) um die EE-Achsen/Metriken.
- **CE-Status:** teilweise (Infrastruktur und Typen vorhanden, keine Widgets).
- **Migrationshinweis:** Aggregation in EF Core über `GroupBy` + `Sum/Count` bzw. Raw-SQL mit `date_trunc` für Datumsgruppierung (Zeitzone des Benutzers beachten, vgl. CE-Analytics `ANALYTICS_V2_DATE_KEYS`, `C/analytics/common.ts`). Angular: Chart-Bibliothek muss die Recharts-Optik (Achsen, Tooltip, Legende) 1:1 treffen (ADR-005).
- **Konfidenz:** hoch (Enums, Paletten, Datenformat), niedrig (Widget-Typ-Katalog, Editor-UI).

#### P05-11 – Dashboard-Filter inkl. PQL

- **Tier:** unklar (≥ Pro).
- **Funktionsbeschreibung (belegt):** nur Changelog-Titel „PQL in dashboards“ (WS5) und „PQL dashboard filters“ (WS6).
- **Ergänzender Entwurf (UNVERIFIZIERT):** Dashboard-weiter Filter (Projekte, Zeitraum, Rich-Filter) und optionaler PQL-Ausdruck (P05-29), der auf alle Widgets angewendet wird; Widget-Filter wirken zusätzlich (UND-Verknüpfung).
- **Datenmodell/API:** Felder `dashboards.filters`, `dashboards.pql`, `dashboard_widgets.filters`; Widget-Daten-Endpunkt akzeptiert Overrides `?pql=` (Vorschlag).
- **CE-Status:** fehlt.
- **Konfidenz:** niedrig.

#### P05-12 – Dashboard-Widgets für Intake und Custom Properties

- **Tier:** unklar.
- **Funktionsbeschreibung (belegt):** nur Changelog-Titel „dashboard intake widgets“ (WS7) und „dashboard custom properties“ (WS8).
- **Ergänzender Entwurf (UNVERIFIZIERT):** Datenquelle „Intake“ (Intake-Work-Items nach Status `-2` Pending, `-1` Rejected, `0` Snoozed, `1` Accepted, `2` Duplicate – `IntakeIssueStatus` des CE-Modells, `API/db/models/intake.py` Z. 44–68) und X-Achse/Gruppierung nach Custom Properties (Work-Item-Properties, vgl. Dok. 20 PF-06) bzw. Y-Metrik „Summe einer numerischen Property“.
- **CE-Status:** fehlt.
- **Konfidenz:** niedrig.

#### P05-13 – Dashboard-Widgets in Pages einbetten

- **Tier:** Enterprise (Grid) laut Doku-Label (Dok. 26 P07-42, WS16; UNVERIFIZIERT).
- **Funktionsbeschreibung (sekundär):** Editor-Block „Link dashboard widgets“ bettet ein Widget (Chart, Tabelle, Zahl) eines bestehenden Dashboards in eine Seite ein, synchron mit den Daten; mindestens ein Dashboard mit Widgets erforderlich (Dok. 26 Z. 762).
- **Migrationshinweis:** Tiptap-Node mit Attributen `dashboard_id`, `widget_id`; Rendering über denselben Widget-Daten-Endpunkt (P05-10). Persistenzformat nicht belegt (Dok. 26 OP-06).
- **Konfidenz:** niedrig.

### 3.3 Analytics, Insights, Reports

#### P05-14 – Insights

- **Tier:** Pro, „Coming soon“ (R1 Z. 561–571: „Insights – Hindsight, On-demand insights, Foresights.“).
- **Funktionsbeschreibung (belegt):** nur Matrix-Text. Keine Repo-Spuren.
- **Ergänzender Entwurf (UNVERIFIZIERT):** „Hindsight“ = rückblickende Auswertungen abgeschlossener Cycles/Module (Velocity, Scope-Änderungen), „On-demand insights“ = auf Anforderung erzeugte Zusammenfassungen (ggf. Plane AI, Dok. 28), „Foresights“ = Prognosen (Abschlussdatum aus Burn-Rate).
- **Migrationshinweis:** Da „Coming soon“ in der Matrix und ohne Spezifikation: niedrige Priorität; bei Umsetzung lokale LLM-Option (ADR-004).
- **Konfidenz:** niedrig.

#### P05-15 – Erweiterte Analytics-Tabs

- **Tier:** unklar (Text „Upgrade to {plan} to unlock {tab}“, `L/workspace.json` Z. 147 → Tabs waren je Plan gesperrt).
- **Funktionsbeschreibung (belegt):**
  - CE-Analytics hat die Tabs `overview` („Overview“) und `work-items` („Work items“) (`W/components/analytics/tabs.tsx`; `T/analytics.ts` Z. 40). Tab-Objekt `{key, label, content, isDisabled}` (`T/analytics.ts` Z. 42–47); die Seite rendert `disabled={tab.isDisabled}` (`W/app/(all)/[workspaceSlug]/(projects)/analytics/[tabId]/page.tsx` Z. 84–86). `useAnalyticsTabs(workspaceSlug)` nimmt den Workspace bereits entgegen, nutzt ihn im CE aber nicht (`W/components/analytics/use-analytics-tabs.tsx`) → Erweiterungspunkt für planabhängige Tabs.
  - Nicht referenzierte Texte für weitere Tabs/Karten: „Work items resolved vs pending“, „Projects by status“, „Active users“, „Intake Trends“ (`L/workspace.json` Z. 148–151); Leerzustände „Cycle progress analytics will appear here. Add work items to cycles to start tracking progress.“, „Module progress analytics will appear here. Add work items to modules to start tracking progress.“, „Intake trends analytics will appear here. Add work items to intake to start tracking trends.“ (Z. 134–146); `workspace_empty_state.analytics_projects` „Create projects to visualize project metrics here.“, `.analytics_no_cycle` „Create cycles to organise work into time-bound phases and track progress across sprints.“, `.analytics_no_module` „Create modules to organize your work and track progress across different stages.“, `.analytics_no_intake` „Set up intake to manage incoming requests and track how they're accepted and rejected“ (`L/empty-state.json` Z. 156–170).
  - Typ `TAnalyticsGraphsBase` enthält bereits `"projects"` (`T/analytics.ts` Z. 41).
- **Ergänzender Entwurf (UNVERIFIZIERT):** zusätzliche Tabs „Cycles“ (Fortschritt je Cycle), „Modules“ (Fortschritt je Modul), „Intake“ (Eingang/Annahme/Ablehnung über Zeit), „Projects“ (Projekte nach Projekt-State, setzt Projekt-States voraus, Dok. 20 PF-21), „Users“ (aktive Benutzer); Overview erweitert um „Work items resolved vs pending“.
- **API-Hinweise (Vorschlag):** CE-Muster beibehalten: `GET /api/workspaces/{slug}/advance-analytics/?tab=cycles|modules|intake|projects|users`, `…/advance-analytics-stats/?type=…`, `…/advance-analytics-charts/?type=…` (CE: `API/app/views/analytic/advance.py` Z. 107–121, 161–165, 288–314 lehnen unbekannte Tabs mit 400 „Invalid tab“ ab).
- **CE-Status:** teilweise (Architektur und Texte).
- **Migrationshinweis:** Kein Gating (ADR-001): `isDisabled` immer `false`; der Text `workspace_analytics.upgrade_to_plan` entfällt.
- **Konfidenz:** mittel (Existenz), niedrig (Inhalt je Tab).

#### P05-16 – Custom Reports

- **Tier:** Business, „Coming soon“ (R1 Z. 597–606: „Generate reports by any dimension and metric across your project or workspace.“; R1 `planHighlights.business` „Custom Reports“; R2 `BUSINESS_PLAN_FEATURES` „Custom Reports“).
- **Funktionsbeschreibung (belegt):** nur Matrix-/Highlight-Texte.
- **Ergänzender Entwurf (UNVERIFIZIERT):** gespeicherte Auswertungen „Dimension × Metrik“ (Achsen/Metriken wie P05-10) auf Projekt- oder Workspace-Ebene, tabellarisch und als Diagramm, Export CSV. Technisch identisch zur Widget-Engine; ein Report = gespeicherte Widget-Konfiguration außerhalb eines Dashboards. Das CE besitzt mit `AnalyticView` (`analytic_views`, `name`, `description`, `query`, `query_dict`) bereits ein Speichermodell für Analytics-Abfragen (`migration/analysis/02a-datenmodell-kern.md` §2.3.33; Endpunkte AN-02 … AN-07 in `migration/analysis/03-api-intern-workspace-projekt-user.md` Z. 530–535).
- **Datenmodell-Hinweise (Vorschlag):** `reports(id, workspace_id, project_id NULL, name, description, chart_type, chart_model, x_axis_property, x_axis_date_grouping, y_axis_metric, group_by, filters jsonb, pql text, owned_by_id, access, created_*, deleted_at)`.
- **CE-Status:** fehlt (Legacy-`AnalyticView` als Ausgangspunkt).
- **Konfidenz:** niedrig.

#### P05-17 – Time Capsule

- **Tier:** Business, Zeile auskommentiert, „Coming soon“ (R1 Z. 573–583: „Go back in your project's timeline and see point-in-time snapshots.“).
- **Funktionsbeschreibung:** nur Matrix-Text; keine Spuren.
- **Migrationshinweis:** Da im Original nicht ausgeliefert (auskommentiert), **nicht** Teil des Portierungsumfangs; als offener Punkt geführt (O-12).
- **Konfidenz:** niedrig.

#### P05-18 – Advanced Pages Analytics

- **Tier:** Business (R1 Z. 585–595, „Coming soon“; laut Doku ausgeliefert, Dok. 26 P07-25).
- **Funktionsbeschreibung (sekundär, WS15 via Dok. 26 Z. 690–693):** Seiten-Menü „Analytics“ mit Zeitraum 7/30/90 Tage/gesamt, Kennzahlen Total views, Unique views, Nested pages, Attachments, Tageskurve, Tab „Viewers“; Zählregel 1 Ansicht/Person/Stunde, Owner-Ansichten ausgeschlossen; Collection-Analytics.
- **Verweis:** vollständige Spezifikation in Dok. 26 P07-25.
- **Konfidenz:** mittel (sekundär).

### 3.4 Cycles

#### P05-19 – Progress Charts

- **Tier:** Pro (R1 Z. 538–547: „Track progress in cycles, modules, and overviews throughout Plane without switching to dashboards or Analytics.“).
- **Funktionsbeschreibung (belegt aus CE-Code ohne Aufrufer):**
  - **Cycle-Versionen:** `Cycle.version` (Integer, Default 1, `API/db/models/cycle.py` Z. 80). Für `version === 2` lädt das Frontend zusätzlich den „Pro“-Fortschritt, sobald die Cycle-Sidebar geöffnet ist: `fetchActiveCycleProgressPro(workspaceSlug, projectId, cycleId)` (`W/store/issue/cycle/issue.store.ts` Z. 146–156; im CE No-op `W/store/cycle.store.ts` Z. 504) über `GET /api/workspaces/{slug}/projects/{project_id}/cycles/{cycle_id}/cycle-progress/` (`W/services/cycle.service.ts` Z. 52–62; `packages/services/src/cycle/cycle-analytics.service.ts` Z. 73–78) – **Endpunkt fehlt im CE-Backend** (nur `…/progress/`, `API/app/urls/cycle.py` Z. 96–99).
  - **Tägliche Fortschrittsreihe** `ICycle.progress: any[]` (`T/cycle/cycle.ts` Z. 112). Aus `formatV2Data` ableitbare Felder je Eintrag: `progress_date` (bzw. `date`), `total_issues`, `completed_issues`, `cancelled_issues`, `backlog_issues`, `started_issues`, `unstarted_issues`, `total_estimate_points`, `completed_estimate_points`, `cancelled_estimate_points`, `backlog_estimate_points`, `started_estimate_points`, `unstarted_estimate_points` (`U/cycle.ts` Z. 139–178; `W/store/cycle.store.ts` Z. 248 prüft `p.total_estimate_points > 0`).
  - **Diagrammreihe** `TProgressChartData` = `{date, scope, completed, backlog, started, unstarted, cancelled, pending, ideal, actual}[]` (`T/cycle/cycle.ts` Z. 147–158) bzw. `TCycleProgress` (Z. 53–64).
  - **Berechnung** (`U/cycle.ts`):
    - `scope` = `total_issues` (Typ Work Items) bzw. `total_estimate_points` (Typ Estimates) (Z. 79).
    - `ideal(date)` = `floor(Tage(date → end_date, inklusiv) / Tage(start_date → end_date, inklusiv) × scope)` (Z. 88–94; `U/datetime.ts` Z. 111–127).
    - `pending` = `total − completed − cancelled`; `completed` = completed-Wert.
    - `actual` = bei **Burn-down** `|pending|`, bei **Burn-up** `completed`; nur bis heute gesetzt.
    - v2: `scope` vor heute aus dem Tageswert, ab heute bis `end_date` der heutige Scope (Scope-Änderungen werden sichtbar = Scope-Creep); `ideal` vor heute aus Tageswert, ab heute bis vor `end_date` der heutige Idealwert, danach `null`; Zukunftstage bis `end_date + 2` werden über `generateDateArray` angehängt (`U/datetime.ts` Z. 392–412); Duplikate je Datum entfernt (`uniqBy`).
    - v1: aus `distribution.completion_chart` (Datum → offene Menge) des CE-Analytics-Endpunkts (`formatV1Data`, Z. 103–137).
  - **Plot-Typ** `TCyclePlotType` = `"burndown" | "burnup"` (`T/cycle/cycle.ts` Z. 139), Store `plotType` je Cycle mit Default `burndown` (`W/store/cycle.store.ts` Z. 362, 380); Optionsliste `cycleChartOptions` = „Burn-down“, „Burn-up“ (`W/components/cycles/analytics-sidebar/issue-progress.tsx` Z. 40–43) – im CE **ohne UI**.
  - Nicht referenzierte Legenden: „Burndown chart“, „Ideal“, „Current“, „Trailing“, „Leading“ (`L/project.json`, `project_cycles.active_cycle.{chart,ideal,current,trailing,leading}`); Leerzustand „There're no progress metrics to show yet. – Start setting property values in work items to see progress metrics here.“ (`L/empty-state.json`, `common_empty_state.progress`).
  - Matrix nennt neben Cycles auch **Module** und **Overviews** (Projekt-/Epic-/Initiative-Overview, andere Cluster).
- **Ergänzender Entwurf (UNVERIFIZIERT):** In Cycle-Sidebar und Active-Cycle-Karte Umschalter Burn-down/Burn-up neben dem bestehenden Umschalter Work items/Estimates; Linien „Ideal“ (gestrichelt), „Current“ (Fläche), „Scope“; Bereiche „Trailing“ (hinter Ideal) und „Leading“ (vor Ideal) farbig hervorgehoben; Tooltip mit Tageswerten (Backlog/Unstarted/Started/Completed/Cancelled).
- **Datenmodell-Hinweise (Vorschlag):** `cycle_progress_snapshots(id, cycle_id FK, project_id, workspace_id, progress_date date, total_issues int, completed_issues, cancelled_issues, backlog_issues, started_issues, unstarted_issues, total_estimate_points double, completed_estimate_points, cancelled_estimate_points, backlog_estimate_points, started_estimate_points, unstarted_estimate_points, created_at)`, Unique `(cycle_id, progress_date)`; Erzeugung täglich (Scheduler, Zeitzone `Cycle.timezone`) und bei Änderungen des aktuellen Tages (Upsert); neue Cycles `version = 2`. Analog für Module `module_progress_snapshots` (UNVERIFIZIERT).
- **API-Hinweise:** `GET …/cycles/{cycle_id}/cycle-progress/` → `TProgressSnapshot` + `progress: [...]` (Form aus `U/cycle.ts` abgeleitet; Antwortschema UNVERIFIZIERT).
- **CE-Status:** teilweise (Typen, Utils, Store-Stub; Backend fehlt).
- **Migrationshinweis:** Scheduler in .NET (Quartz.NET oder BackgroundService mit `pg_advisory_lock`, vgl. Dok. 22 HA-Hinweise); Berechnung serverseitig über `GROUP BY state.group`.
- **Konfidenz:** hoch (Datenform, Berechnung), mittel (UI).

#### P05-20 – Cycle Reports

- **Tier:** Pro (R1 Z. 550–559: „Get on-demand cycle reports during and after a cycle. Revisit reports anytime from permalinks.“).
- **Funktionsbeschreibung (belegt):** CE speichert beim Transfer offener Work Items einen Fortschritts-Schnappschuss im Quell-Cycle: `progress_snapshot = {total_issues, completed_issues, cancelled_issues, started_issues, unstarted_issues, backlog_issues, distribution: {labels, assignees, completion_chart}, estimate_distribution: {labels, assignees, completion_chart} | {}}` (`API/utils/cycle_transfer_issues.py` Z. 410–432); das Frontend überlagert Cycle-Werte mit dem Snapshot (`validateCycleSnapshot`, `W/components/cycles/analytics-sidebar/issue-progress.tsx` Z. 45–57); CE-Progress-Endpunkt liest ihn (`API/app/views/cycle/base.py` Z. 717–723).
- **Ergänzender Entwurf (UNVERIFIZIERT):** Aktion „Generate report“ an laufenden und abgeschlossenen Cycles erzeugt einen unveränderlichen Bericht (Kopfdaten, Progress, Burndown/Burn-up, Verteilung nach Assignees/Labels/States, Liste übertragener Work Items); jeder Bericht hat einen Permalink; Berichtsliste je Cycle.
- **Datenmodell-Hinweise (Vorschlag):** `cycle_reports(id, cycle_id, project_id, workspace_id, kind varchar (on_demand|completion), generated_by_id, generated_at, snapshot jsonb (TProgressSnapshot + progress-Reihe + Verteilungen), created_*)`; Permalink `/:workspaceSlug/projects/:projectId/cycles/:cycleId/reports/:reportId`.
- **API-Hinweise (Vorschlag):** `GET/POST …/cycles/{cycle_id}/reports/`, `GET …/reports/{report_id}/`.
- **CE-Status:** teilweise (`progress_snapshot`).
- **Konfidenz:** niedrig (Report-UI), hoch (Snapshot-Format).

#### P05-21 – Auto-schedule Cycles

- **Tier:** unklar (keine Matrix-Zeile; Changelog „Recurring cycles“ Commercial v1.16.0, WS11).
- **Funktionsbeschreibung (belegt, `L/project-settings.json` `project_settings.cycles.auto_schedule.*`):**
  - Abschnitt in den Projekt-Einstellungen „Cycles“ unterhalb des Schalters „Enable cycles“: Überschrift „Auto-schedule cycles“, Beschreibung „Keep cycles moving without manual setup.“, Tooltip „Automatically create new cycles based on your chosen schedule.“, Button „Edit“.
  - Formularfelder und Validierung:

| Feld | Label | Einheit/Platzhalter | Tooltip | Validierung (Text) |
|---|---|---|---|---|
| `cycle_title` | „Cycle Title“ | Platzhalter „Title“ | „The title will be appended with numbers for subsequent cycles. For eg: Design - 1/2/3“ | Pflicht „Cycle title is required“; max. 255 „Title must not exceed 255 characters“ |
| `cycle_duration` | „Cycle Duration“ | „Weeks“ | – | Pflicht „Cycle duration is required“; ≥ 1 „Cycle duration must be at least 1 week“; ≤ 30 „Cycle duration cannot exceed 30 weeks“; > 0 „Cycle duration must be positive“ |
| `cooldown_period` | „Cooldown Period“ | „days“ | „Pause between cycles before the next begins.“ | Pflicht „Cooldown period is required“; ≥ 0 „Cooldown period cannot be negative“ |
| `start_date` | „Cycle starts day“ | – | – | Pflicht „Start date is required“; nicht in der Vergangenheit „Start date cannot be in the past“ |
| `number_of_cycles` | „Number of future cycles“ | – | – | Pflicht „Number of cycles is required“; ≥ 1 „At least 1 cycle is required“; ≤ 3 „Cannot schedule more than 3 cycles“ |
| `auto_rollover` | „Auto-rollover work items“ | Schalter | „On the day a cycle completes, move all unfinished work items into the next cycle.“ | – |

  - Toasts: Umschalten „Enabling auto-schedule cycles“ / „Disabling auto-schedule cycles“, Erfolg „Success!“ – „Auto-schedule cycles toggled successfully.“, Fehler „Error!“ – „Failed to toggle auto-schedule cycles.“; Speichern „Saving auto-schedule cycles configuration“, Erfolg „Auto-schedule cycles configuration saved successfully.“ (Anlage) bzw. „… updated successfully.“ (Änderung), Fehler „Failed to save …“ bzw. „Failed to update auto-schedule cycles configuration.“
- **Verhalten (aus Texten abgeleitet):** Es werden stets `number_of_cycles` (1–3) zukünftige Cycles vorgehalten; Cycle *n* heißt „{cycle_title} - {n}“; Dauer `cycle_duration` Wochen; zwischen Ende und nächstem Start liegen `cooldown_period` Tage; erster Start am `start_date`. Nachfolger werden erzeugt, sobald ein Cycle abgeschlossen ist (UNVERIFIZIERT: Zeitpunkt der Nachproduktion).
- **UI-Hinweise:** CE-Seite `W/app/(all)/[workspaceSlug]/(settings)/settings/projects/[projectId]/features/cycles/page.tsx` enthält nur `ProjectSettingsFeatureControlItem` „Enable cycles“; der Auto-Schedule-Block folgt darunter (nur für Projekt-Admins, wie die Seite selbst: `allowPermissions([ADMIN], PROJECT)`).
- **Datenmodell-Hinweise (Vorschlag):** `project_cycle_schedules(id, project_id UNIQUE, workspace_id, is_enabled bool, cycle_title varchar(255), cycle_duration_weeks smallint 1–30, cooldown_days smallint ≥ 0, start_date date, number_of_cycles smallint 1–3, auto_rollover bool, next_sequence int, created_*, updated_*)`; erzeugte Cycles referenzieren `schedule_id` (nullable).
- **API-Hinweise (Vorschlag):** `GET/POST/PATCH /api/workspaces/{slug}/projects/{project_id}/cycle-schedule/`, `POST …/cycle-schedule/toggle/`.
- **CE-Status:** fehlt (nur Texte).
- **Migrationshinweis:** Täglicher Job je Projekt-Zeitzone; Zusammenspiel mit CE-Regel „keine überlappenden Cycles“ (Fehlertext `project_cycles.action.update.error.already_exists`) und P05-24.
- **Konfidenz:** hoch (Formular), mittel (Verhalten).

#### P05-22 – Auto-Rollover (Auto-transfer Cycle Work items)

- **Tier:** Pro (R1 Z. 249–258: „Transfer incomplete work items from a completed cycle to the next cycle or to the default project state.“).
- **Funktionsbeschreibung (belegt):** Option „Auto-rollover work items – On the day a cycle completes, move all unfinished work items into the next cycle.“ im Auto-Schedule-Formular (P05-21). Matrix nennt alternativ „to the default project state“ (UNVERIFIZIERT, wann).
- **CE-Basis:** manueller Transfer existiert (`POST …/cycles/{cycle_id}/transfer-issues/`, nur unvollständige Work Items, Snapshot wie P05-20; `API/utils/cycle_transfer_issues.py`; UI `W/components/cycles/transfer-issues-modal.tsx`).
- **Migrationshinweis:** Rollover-Job ruft dieselbe Domänenlogik wie der manuelle Transfer auf (Snapshot schreiben, offene Work Items umhängen, Activity erzeugen).
- **CE-Status:** fehlt.
- **Konfidenz:** mittel.

#### P05-23 – Workspace-weite Active Cycles

- **Tier:** One (R1 Z. 194–203: Free `false`, One–Enterprise `true`; R1 `planHighlights.one` „Active cycles“; R2 `ONE_PLAN_FEATURES` „Active Cycles“). Da der Plan „One“ nicht mehr angeboten wird (`W/components/workspace/billing/comparison/base.tsx` Z. 30–31; Dok. 20 §1.2), ist die Funktion in aktuellen Plänen ab Pro enthalten.
- **Funktionsbeschreibung (belegt):**
  - Seite `/:workspaceSlug/active-cycles` (`W/app/routes/core.ts` Z. 66–67), Seitentitel „{Workspace} - Active Cycles“ (`W/app/(all)/[workspaceSlug]/(projects)/active-cycles/page.tsx`), Sidebar-Eintrag „Cycles“ (`sidebar.cycles`) mit Icon `CyclesOutline` (Rotation `rotate-180` lt. Dok. 20 PF-04), sichtbar für ADMIN und MEMBER (`W/components/workspace/sidebar/workspace-menu.tsx` Z. 46–52); Power-K-Aktion „Go to all active cycles“ (`L/power-k.json` Z. 107).
  - Funktionsumfang laut Upsell (`W/components/active-cycles/workspace-active-cycles-upgrade.tsx` Z. 28–66; Texte `L/common.json` Z. 124–139): „On-demand snapshots of all your cycles“; „Monitor cycles across projects, track high-priority work items, and zoom in cycles that need attention.“; sechs Punkte „10,000-feet view of all active cycles.“, „Get a snapshot of each active cycle.“, „Compare burndowns.“, „Quickly see make-or-break work items.“, „Zoom into cycles that need attention.“, „Stay ahead of blockers.“ mit Beschreibungen (Anhang B).
  - Leerzustände: „No active cycles – You don't have any ongoing cycles right now. Active cycles appear here when they include today's date.“ (`workspace_empty_state.active_cycles`, `L/empty-state.json` Z. 180) und Variante „Cycles of your projects that includes any period that encompasses today's date within its range. Find the progress and details of all your active cycle here.“ (`workspace_cycles.empty_state.active`, `L/workspace.json`).
  - Kartenleerzustände (mit Zeilenumbruch): `active_cycle_analytics.empty_state.{progress,priority,assignee,label}.title` (`L/cycle.json`).
  - **Layout** (Screenshots `IMG/cycles/active-cycles-ui.png` „Active Cycles – Beta“ und Upsell-Assets `W/app/assets/workspace-active-cycles/cta-r-1-light.webp`, `cta-r-2-light.webp`): je Projekt ein Block mit Projekt-Logo und -Name; darunter eine Cycle-Zeile mit Cycle-Icon, Zeitraum bzw. Name, „{n} days left“, „Lead“ mit Avatar/Name und Button „View Cycle“; darunter drei Karten: **Progress** („{x}/{y} Issues closed“, segmentierter Balken, Zeilen Completed/Started/Unstarted/Backlog mit Anzahl, Hinweis „{n} cancelled issue(s) is excluded from this report“), **Issue burndown** (Legende „Ideal“/„Current“, rechts „Pending issues - {n}“, Flächen-/Liniendiagramm), **High-priority issues** (Liste mit Prioritäts-Icon, Identifier, Titel, State-Pill, Fälligkeitsdatum, „View more“; Leer: „There are no high priority issues present in this cycle.“). Die heutige CE-Projektansicht des aktiven Cycles verwendet dieselben Kartentypen (`W/components/cycles/active-cycle/{progress,productivity,cycle-stats}.tsx`; Tabs „Priority work items“, „Assignees“, „Labels“) – die EE-Workspace-Seite wiederverwendet sie je Cycle (Dok. 20 PF-04).
- **API-Hinweise (belegt):** `GET /api/workspaces/{slug}/active-cycles/?per_page={n}&cursor={c}` (`W/services/cycle.service.ts` Z. 64–78; `packages/services/src/cycle/cycle.service.ts` Z. 29; SWR-Key `WORKSPACE_ACTIVE_CYCLES_LIST_{SLUG}_{CURSOR}_{PER_PAGE}`, `C/fetch-keys.ts` Z. 98–99) → `IWorkspaceActiveCyclesResponse {count, extra_stats: null, next_cursor, next_page_results, prev_cursor, prev_page_results, results: ICycle[], total_pages}` (`T/workspace.ts` Z. 219–228). **Im CE-Backend nicht vorhanden.** Für die Karten werden die vorhandenen Projekt-Endpunkte genutzt: `…/cycles/{id}/progress/`, `…/cycles/{id}/analytics/?type=issues|points` (`W/services/cycle.service.ts` Z. 25–50; Dok. 04 Y22/Y23).
- **Verhalten (Vorschlag, UNVERIFIZIERT wo nicht anders belegt):** Ergebnis = alle Cycles mit `start_date ≤ jetzt ≤ end_date` (belegt durch Leerzustandstext „include today's date“) in nicht archivierten Projekten mit aktivierten Cycles, in denen der Benutzer Mitglied ist; Sortierung nach Projekt; Cursor-Pagination im CE-Format `"{per_page}:{page}:{offset}"`.
- **Datenmodell-Hinweise:** keine neue Tabelle.
- **CE-Status:** Stub/UI-Hülle.
- **Migrationshinweis:** Upsell-Seite entfällt (ADR-001) – an ihrer Stelle die Liste; Bilder `cta-*` werden nicht benötigt.
- **Konfidenz:** hoch (Endpunkt, Kartentypen), mittel (exaktes aktuelles Layout – Screenshot ist eine Beta-Version).

#### P05-24 – Parallel Cycles

- **Tier:** unklar.
- **Funktionsbeschreibung (belegt):** Projekt-Feature-Flag `parallel_cycles` „Allows multiple active cycles to run simultaneously.“ (`DD/dev-tools/plane-compose.md` Z. 1259, Beispiel `parallel_cycles: false`; MCP `project update_features` Parameter `parallel_cycles`, `DD/dev-tools/mcp-server-tools.md` Z. 377). Die Public-API-Projekt-Features (`DD/api-reference/project-features/overview.md`: `epics`, `modules`, `cycles`, `views`, `pages`, `intakes`, `work_item_types`) nennen es nicht.
- **CE-Basis:** Überlappende Cycles sind verboten (Date-Check, Fehlertext „You already have a cycle on the given dates, if you want to create a draft cycle, you can do that by removing both the dates.“, `L/project.json` `project_cycles.action.update.error.already_exists`); CE-Frontend kennt genau einen aktiven Cycle je Projekt (`currentProjectActiveCycleId`, `W/store/cycle.store.ts`).
- **Ergänzender Entwurf (UNVERIFIZIERT):** Bei aktivem Flag entfällt die Überlappungsprüfung; die Projekt-Cycle-Liste zeigt mehrere „Active cycle“-Blöcke; Active-Cycles-Seite (P05-23) listet alle.
- **Datenmodell:** `projects.parallel_cycles bool` bzw. Projekt-Feature-Tabelle.
- **CE-Status:** fehlt.
- **Konfidenz:** mittel (Flag), niedrig (Verhalten).

#### P05-25 – Cycle-Aktionen „Complete“ und Archivieren laufender Cycles

- **Tier:** unklar.
- **Funktionsbeschreibung (belegt):** MCP-Tool `cycle` Aktion `complete` „sets end_date to today“; `archive` „ends the cycle first if it is still running“; Status-Filter `current, upcoming, completed, draft, incomplete` (`DD/dev-tools/mcp-server-tools.md` Z. 240–254). CE erlaubt Archivieren nur beendeter Cycles („Only completed cycles can be archived“, `L/project.json`; Dok. 21 §5).
- **API-Hinweise (Vorschlag):** `POST …/cycles/{cycle_id}/complete/` (setzt `end_date` = heute in `Cycle.timezone`, schreibt Snapshot, löst ggf. Auto-Rollover P05-22 aus).
- **CE-Status:** fehlt.
- **Konfidenz:** mittel.

#### P05-26 – Cycle Updates

- **Tier:** unklar; **Existenz UNVERIFIZIERT.**
- **Befund:** Das generische Updates-Modul (`L/update.json`: „Add Update“, „Add your update here“, Fortschritt „Progress“ / „Since last update“ / „{count} Comments“, Reaktionen, Löschen „Are you sure you want to delete this update? This is an irreversible action.“; Status `EUpdateStatus` `OFF-TRACK`, `ON-TRACK`, `AT-RISK`, `T/enums.ts` Z. 87–91; Labels „On-Track“, „Off-Track“, „At risk“, `L/common.json` Z. 588–590; Leerzustand „No updates yet. – Once project members add updates it will appear here“) ist für **Project Updates** belegt (`project_settings.project_updates.*` „Project Updates – Consolidated tracking and progress monitoring for this project“; Projekt-Feature `project_updates`, `DD/dev-tools/plane-compose.md` Z. 1260). Für Cycles gibt es im Repo und in den Developer-Docs **keinen** Beleg.
- **Empfehlung:** Updates-Modul generisch bauen (`entity_type` ∈ {project, epic, initiative, …}) – Cycle-Unterstützung erst nach Nachrecherche (O-08). Project Updates gehören zum Projekt-Cluster.
- **Konfidenz:** niedrig.

### 3.5 Views

#### P05-27 – Shared Views

- **Tier:** Pro (R1 Z. 499–508: „Choose a few members to share a view with.“). Changelog-Titel „shared views“ Cloud 31.08.2026 (WS9).
- **Funktionsbeschreibung (belegt):** CE-Views kennen nur `access` 0 = Private, 1 = Public (`API/db/models/view.py` Z. 66; `T/views.ts` `EViewAccess { PRIVATE, PUBLIC }` Z. 15–18; UI-Optionen „Public“/„Private“ `C/views.ts` Z. 9–15); Tooltip „Public“/„Private“ mit `GlobeOutline`/`LockOutline` in der View-Liste (`W/components/views/view-list-item-action.tsx` Z. 92–96; Tooltip Z. 93). Text „Save custom sorts, filters, and display options or share them with your team.“ (`L/common.json` Z. 228, `views_description`, ohne CE-Referenz).
- **Ergänzender Entwurf (UNVERIFIZIERT):** Private Views können ausgewählten Projekt-/Workspace-Mitgliedern freigegeben werden (Dialog mit Member-Auswahl); geteilte Views erscheinen bei den Empfängern in der View-Liste; nur Owner/Admin ändern die Freigabe. Analog Page-Sharing (Dok. 26 P07-16: Stufen „Can view“/„Can comment“/„Can edit“ – für Views vermutlich nur Lesen).
- **Datenmodell-Hinweise (Vorschlag):** `issue_view_members(id, view_id FK, member_id FK, access smallint NULL, created_*, deleted_at)`, Unique `(view_id, member_id)`; Sichtbarkeit: `access = public` ∨ `owned_by = me` ∨ Eintrag in `issue_view_members`.
- **API-Hinweise (Vorschlag):** `GET/POST/DELETE /api/workspaces/{slug}/projects/{project_id}/views/{view_id}/members/` bzw. Workspace-Variante `…/workspace-views/{view_id}/members/`.
- **CE-Status:** fehlt. (Hinweis K2: `project_views.empty_state.shared.*` ist ein Page-Text.)
- **Konfidenz:** mittel (Existenz), niedrig (Details).

#### P05-28 – Publish Views

- **Tier:** Pro laut R1 Z. 510–519 („Put a view on the Internet and let your customers interact with them.“). **Widerspruch:** R2 `ONE_PLAN_FEATURES` „Real-time collab + public views and page“ und `FREE_PLAN_UPGRADE_FEATURES` „Public Views and Pages“ legen „One“ nahe.
- **Funktionsbeschreibung (belegt):**
  - `DeployBoard.TYPE_CHOICES` enthält `("view", "View")`; Felder `entity_identifier`, `entity_name`, `anchor` (uuid4-hex, unique), `is_comments_enabled`, `is_reactions_enabled`, `is_votes_enabled`, `view_props`, `is_activity_enabled`, `is_disabled`, `intake` (`API/db/models/deploy_board.py` Z. 19–39).
  - Frontend-Typen: `IProjectView.anchor?` (`T/views.ts` Z. 39), `IPublishedProjectView` (View mit `filters` statt `rich_filters`, Z. 43–45), `TPublishViewSettings {is_comments_enabled, is_reactions_enabled, is_votes_enabled}` (Z. 47–51), `TPublishViewDetails = TPublishViewSettings & {id, anchor}` (Z. 53–56).
  - Hook-Stub `useViewPublish(isPublished, isAuthorized)` → `{isPublishModalOpen, setPublishModalOpen, publishContextMenu}` (`W/components/views/publish/use-view-publish.tsx`); Quick-Actions fügen `publishContextMenu` an Position 2 ein, Berechtigung Admin **oder** Owner (`W/components/views/quick-actions.tsx` Z. 58, 88).
  - Listeneintrag zeigt bei `anchor` ein grünes „Live“-Badge (`rounded-sm bg-success-subtle px-3 py-1.5 text-11 font-medium text-success-primary`, Punkt `size-1.5 rounded-full bg-success-primary`), Klick öffnet das Publish-Modal (`W/components/views/view-list-item-action.tsx` Z. 98–107).
  - Öffentlicher Link `{SPACE_BASE_URL|origin}{SPACE_BASE_PATH}/views/{anchor}` (`U/project-views.ts` Z. 105–110).
  - Space-App: Hinweistext „Enter the public-share URL or link of the view or Page you are trying to see in the browser's address bar.“ (`SPC/components/account/user-logged-in.tsx`, Dok. 11 Z. 824).
- **Fehlt im CE:** Route `views/:anchor` in `SPC/app/routes.ts` (nur `/`, `:workspaceSlug/:projectId`, `issues/:anchor`); `TPublishEntityType` kennt nur `"project" | "page"` (`T/publish.ts` Z. 10); Publish-Modal für Views; Backend-Endpunkte.
- **Ergänzender Entwurf (UNVERIFIZIERT):** Publish-Modal analog Projekt-Publish (`W/components/project/publish-project/modal.tsx`: Schalter „Allow comments“, „Allow reactions“, „Allow voting“, Buttons „Publish“/„Publishing“, „Update settings“/„Updating“, „Unpublish“/„Unpublishing“, „Cancel“, Link „Open in new tab“) **ohne** Layout-Auswahl (Layout kommt aus der View). Öffentliche Seite zeigt die View mit ihren Filtern/Display-Optionen read-only, Interaktion gemäß Schaltern.
- **API-Hinweise (Vorschlag):** `GET/POST/PATCH/DELETE /api/workspaces/{slug}/projects/{project_id}/views/{view_id}/publish/`; öffentlich `GET /api/public/anchor/{anchor}/settings/` (vorhanden, generisch), `GET /api/public/anchor/{anchor}/views/` und `…/views/issues/` (Vorschlag).
- **CE-Status:** teilweise.
- **Konfidenz:** hoch (Modell, Link, Badge), mittel (Modal, Space-Seite).

> **Abgrenzung:** Workspace-Views (globale Views) und Projekt-Views mit Private/Public, Favoriten, Sperren (`is_locked`), Logo, Sortierung sind CE (Anhang E).

### 3.6 PQL und erweiterte Filter

#### P05-29 – PQL (Plane Query Language)

- **Tier:** Pro (R1 Z. 658–668: „Write Plane Query Language in search with support for Boolean operators. Soon, you can write natural language queries.“). Commercial v2.6.0 (WS10).
- **Funktionsbeschreibung (belegt):**
  - **Einsatzorte:** Suche (R1), Public-API/MCP-Listen `workitem list`, `list_archived`, `count`, `cycle list_workitems`, `module list_workitems` mit Parameter `pql` (`DD/dev-tools/mcp-server-tools.md` Z. 44–48, 78–83, 247, 267), Webhook-Filter „Work item v2 filters“ mit Modi **Basic** (Picker) und **PQL** (Text), „Switching between modes is lossless“, Auswertung zur Zustellzeit, Fehler ⇒ Zustellung übersprungen (`DD/dev-tools/intro-webhooks.md` Z. 60–102), Dashboards (WS5, WS6).
  - **Felder (MCP-Dialekt):** `project`, `assignee`, `state`, `stateGroup`, `label`, `cycle`, `module`, `type`, `milestone`, `createdBy` (bzw. „creator“), `priority`, Custom Property `cf["<property id>"]` (OPTION-Wert = Option-ID) (`DD/dev-tools/mcp-server-tools.md` Z. 48, 212, 254, 272). UUID-basierte Felder verlangen UUIDs.
  - **Funktionen:** `currentUser()`, `openStates()`, `isOverdue()`, `childOf("PROJ-12")` (lesbarer Identifier) (`DD/dev-tools/mcp-server-tools.md` Z. 58, 254; `DD/dev-tools/mcp-server.md` Z. 29, 703).
  - **Operatoren/Syntax:** `=`, `IN`, `AND`, `OR`, Klammern, Zeichenketten in doppelten Anführungszeichen; Beispiele `priority = "urgent" AND assignee = currentUser()`, `stateGroup IN openStates() AND isOverdue()`, `assignee = currentUser() AND (stateGroup = "started" OR isOverdue())`, `type = "<type id>"`, `stateGroup = "started"`.
  - **Webhook-Dialekt (Teilmenge):** Felder `type_id`, `state_group` (`backlog`·`unstarted`·`started`·`completed`·`cancelled`), `assignee_id`, `label_id`, `project_id`, `priority` (`none`·`low`·`medium`·`high`·`urgent`), `start_date`, `target_date` (ISO-Datum); Syntax `priority = "urgent"`, `priority in ["urgent", "high"]` (`DD/dev-tools/intro-webhooks.md` Z. 88–102).
  - Gruppierungsschlüssel für `count` (`state_id`, `state__group`, `priority`, `project_id`, `type_id`, `labels__id`, `assignees__id`, `issue_module__module_id`, `release_work_items__release_id`, `cycle_id`, `milestone_id`, `created_by`, `target_date`, `start_date`) sind **keine** PQL-Felder; „filtering on state__group is rejected“ (`DD/dev-tools/mcp-server-tools.md` Z. 91).
  - Referenz-Tool `get_pql_reference` mit `detail` = `full` (Operatoren, Funktionen, häufige Fehler, Beispiele) oder `brief` (Feld-/Operator-Kurzreferenz) (Z. 517–523). Nutzer-Doku WS13.
  - **CE-Gegenstück:** Public-API `GET …/work-items/` lehnt `pql` und `filters` mit HTTP 400 ab: `{"pql": "PQL and structured filters are not supported on this Plane edition. Remove the pql/filters parameter and filter results client-side, or use a Plane edition that supports work item query filtering.", "unsupported_parameters": [...]}` (`API/api/views/issue.py` Z. 324–335).
- **Ergänzender Entwurf (UNVERIFIZIERT) – Grammatik (EBNF), vereinigt aus beiden Dialekten:**

```
query      = orExpr ;
orExpr     = andExpr { "OR" andExpr } ;
andExpr    = notExpr { "AND" notExpr } ;
notExpr    = [ "NOT" ] primary ;
primary    = "(" orExpr ")" | comparison | funcCall ;
comparison = field op value | field ( "IN" | "NOT IN" ) list ;
op         = "=" | "!=" | ">" | ">=" | "<" | "<=" ;
list       = "[" value { "," value } "]" | "(" value { "," value } ")" | funcCall ;
value      = STRING | NUMBER | DATE | funcCall ;
field      = IDENT | "cf" "[" STRING "]" ;
funcCall   = IDENT "(" [ value { "," value } ] ")" ;
```

  Schlüsselwörter case-insensitiv; Feld-Aliase camelCase ↔ snake_case (`stateGroup`/`state_group`, `assignee`/`assignee_id`, `label`/`label_id`, `project`/`project_id`, `type`/`type_id`, `createdBy`/`created_by`, `startDate`/`start_date`, `dueDate`/`target_date`). `NOT`, `!=` und Vergleichsoperatoren sind nicht belegt.
- **Datenmodell-Hinweise:** Speicherung als Text (`pql text`) neben dem Rich-Filter-JSON; für verlustfreies Umschalten Basic ↔ PQL kanonischer Printer.
- **API-Hinweise:** `?pql=` an Work-Item-Listen (Projekt- und Workspace-Ebene), Cycle-/Modul-Work-Item-Listen, `count`; Fehler 400 mit Positionsangabe (Vorschlag).
- **CE-Status:** Stub/UI-Hülle.
- **Migrationshinweis:** .NET-Parser (handgeschrieben rekursiv-absteigend oder Parser-Kombinator) → AST → Übersetzung in den CE-Rich-Filter-Baum (`{"and": [...]}`, `{"or": [...]}`, `{"not": {...}}`, Blattknoten `feld__operator: wert`), den das CE-Backend bereits auswertet (`API/utils/filters/filter_backend.py` Z. 147–210, 350–422) → EF-Core-Expression. Funktionen werden serverseitig aufgelöst (`currentUser()` = angemeldeter Benutzer, `openStates()` = States der Gruppen backlog/unstarted/started, `isOverdue()` = `target_date < heute ∧ Gruppe ∉ {completed, cancelled}`, `childOf(id)` = `parent_id` = Work Item mit Identifier) – Semantik UNVERIFIZIERT.
- **Konfidenz:** mittel (Syntaxbeispiele, Felder, Funktionen), niedrig (vollständige Grammatik).

#### P05-30 – Operator-Kapseln und erweiterte Filteroperatoren

- **Tier:** Pro (auskommentierte R1-Zeile „Search – Search via natural-language queries, operators, or PQL“: Free/One „Basic text search“, Pro/Business/Enterprise „COMING SOON – Operator capsules from text or PQL“, R1 Z. 626–656).
- **Funktionsbeschreibung (belegt):** Die CE-Rich-Filter-Architektur hat leere EE-Erweiterungspunkte: `EXTENDED_LOGICAL_OPERATOR`, `EXTENDED_EQUALITY_OPERATOR`, `EXTENDED_COLLECTION_OPERATOR`, `EXTENDED_COMPARISON_OPERATOR`, `EXTENDED_MULTI_VALUE_OPERATORS`, `EXTENDED_OPERATORS` (`T/rich-filters/operators/extended.ts`), `EXTENDED_FILTER_FIELD_TYPE` und `TExtendedFilterFieldConfigs = never` (`T/rich-filters/field-types/extended.ts`), weitere in `T/rich-filters/operator-configs/extended.ts`, `T/rich-filters/derived/extended.ts`, Labels in `C/rich-filters/operator-labels/extended.ts` (Dok. 20 PF-52). CE-Operatoren: logisch nur `and`; `exact`, `in`, `range` (`T/rich-filters/operators/core.ts`); Filter-Gruppen nur `AND` (`T/rich-filters/expression.ts` `TFilterAndGroupNode`). `useFiltersOperatorConfigs` liefert `allowedOperators = CORE_OPERATORS`, `allowNegative: false` (`W/hooks/rich-filters/use-filters-operator-configs.ts`). Das CE-**Backend** wertet `or` und `not` bereits aus (`API/utils/filters/filter_backend.py` Z. 147–210).
- **Ergänzender Entwurf (UNVERIFIZIERT):** Pro+ schaltet negierte Operatoren („is not“, „is not any of“, „not between“), OR-Gruppen und weitere Operatoren frei; „Operator capsules from text“ = Eingabe von Text/PQL in der Filterleiste wird in Filter-Kapseln (Chips) umgewandelt.
- **CE-Status:** Stub/UI-Hülle.
- **Migrationshinweis:** Angular-Filterleiste mit `allowNegative = true` und OR-Gruppen; Labels der negierten Operatoren sind im CE leer (`NEGATED_OPERATOR_LABELS_MAP = {}`) → Texte neu festlegen (O-10).
- **Konfidenz:** mittel (Erweiterungspunkte), niedrig (Operatorkatalog).

### 3.7 Advanced Search

#### P05-31 – Advanced Search

- **Tier:** Pro (Badge `[Pro]`, `DD/self-hosting/govern/advanced-search.md` Z. 7). Commercial v2.2.0 „enhanced search“ (WS12).
- **Funktionsbeschreibung (belegt, `DD/self-hosting/govern/advanced-search.md`):** „Full-text search across work items, projects, cycles, modules, pages, and more“, „Fuzzy matching that tolerates typos“, „Autocomplete with instant suggestions as you type“, „Multi-entity search that searches across all content types in a single query“; Zugang über „global search shortcut (Cmd/Ctrl + K) or search within specific projects and sections“. Neun Indizes: `issues` (Feldgewichtung Titel > Beschreibung, State-Filter), `issue_comments`, `projects` (Metadatenfilter), `cycles`, `modules`, `pages`, `workspaces`, `issue_views`, `teamspaces`. Synchronisation: Signal → Redis-Queue → Batch alle 5 s; Suche geht direkt an den Index (Details Dok. 22 §4.11).
  - Public-API: `POST /api/v1/workspaces/{slug}/work-items/advanced-search/` Body `query` (string), `filters` (an `IssueFilterSet`), `limit` (int), `workspace_search` (bool), `project_id` (uuid) → Liste `{id, name, sequence_id, project_identifier, project_id, workspace_id, type_id, state_id, priority, target_date, start_date}` (`DD/api-reference/issue/advanced-search-work-items.md`; Dok. 21 W8).
  - Power-K: Aktion „Go to advanced search“ (`L/power-k.json` Z. 174, ohne CE-Referenz).
- **CE-Basis:** Power-K-Suche über `GET /api/workspaces/{slug}/search/?search=&workspace_search=&project_id=` (500 ms Debounce, Ergebnisgruppen `workspace`, `project`, `issue`, `cycle`, `module`, `issue_view`, `page`; Kopfzeile „Search results for "{term}" in workspace|project:“) (`W/components/power-k/ui/modal/search-menu.tsx`; `C/workspace.ts` `WORKSPACE_DEFAULT_SEARCH_RESULT`; Dok. 03 SR-01).
- **Ergänzender Entwurf (UNVERIFIZIERT):** Eigene Seite „Advanced search“ (aus Power-K erreichbar) mit Suchfeld, Entitätstyp-Tabs (Work items, Comments, Projects, Cycles, Modules, Pages, Views, Teamspaces), Filtern (Projekt, State, Assignee, Priorität, Datum) und Treffer-Hervorhebung; Autocomplete im Power-K.
- **Datenmodell/Migration (ADR-004):** kein OpenSearch; je Entität generierte `tsvector`-Spalte (`setweight(name,'A') || setweight(description_stripped,'B')`) mit GIN-Index, `websearch_to_tsquery`, `pg_trgm` (GIN `gin_trgm_ops`) für Fuzzy/Autocomplete, Ranking `ts_rank_cd` + `similarity`; optional pgvector für semantische Suche (Dok. 22 §4.11). Kommentare (`issue_comments.comment_stripped`) mit indexieren. Sichtbarkeitsfilter wie CE-Suche.
- **CE-Status:** fehlt.
- **Konfidenz:** hoch (Umfang, API), niedrig (eigene Such-UI).

### 3.8 Scheduled Comms

#### P05-32 – Scheduled Comms

- **Tier:** Business (R1 Z. 414–423: „Schedule reports, notifications, and messages to third-party tools.“, Business/Enterprise `true`).
- **Funktionsbeschreibung:** nur Matrix-Text. Keine weiteren Repo-, Doku- oder Changelog-Spuren gefunden.
- **Ergänzender Entwurf (UNVERIFIZIERT):** Zeitgesteuerte Versendung von (a) Reports (Dashboard/Custom Report/Cycle Report als PDF/CSV/Link), (b) Digest-Benachrichtigungen, (c) Nachrichten an Integrationen (Slack, Webhook, E-Mail). Zeitplan-Modell analog Automations-„Schedule“ mit Modi „Fixed“ (Frequenzen inkl. „Weekly“, Zusammenfassungen „Every day at {time} ({timezone}).“, „Every week on {days} at {time} ({timezone}).“, „Every month on day {day} at {time} ({timezone}).“) und „Cron“ (`L/automation.json` Z. 19–46; Dok. 25).
- **Datenmodell-Hinweise (Vorschlag):** `scheduled_communications(id, workspace_id, name, source_type (dashboard|report|cycle_report|digest), source_id NULL, channel (email|slack|webhook), channel_config jsonb, recipients jsonb, schedule_mode (fixed|cron), schedule jsonb, timezone, is_enabled, last_run_at, next_run_at, created_*)`, `scheduled_communication_runs(id, schedule_id, started_at, finished_at, status, error)`.
- **CE-Status:** fehlt.
- **Migrationshinweis:** Externe Kanäle optional/abschaltbar (ADR-004); E-Mail über konfigurierten SMTP.
- **Konfidenz:** niedrig.

### 3.9 Workspace Activity Logs

#### P05-33 – Workspace Activity Logs

- **Tier:** Business (R1 Z. 740–749: „See filterable activity logs for your entire workspace.“; nicht „Coming soon“).
- **Funktionsbeschreibung und CE-Basis:** vollständig in Dok. 27 P08-17 (Aktivität je Benutzer `GET /api/workspaces/{slug}/user-activity/{user_id}/` + Export; No-op `mutateWorkspaceMembersActivity` in `W/store/workspace/index.ts` Z. 385–391, ohne Aufrufer). Ergänzend aus diesem Cluster:
  - Nicht referenzierte Leerzustände `activity_empty_state.{no_activity, no_transitions, no_comments, no_worklogs, no_history}` = „No activity yet“, „No transitions yet“, „No comments yet“, „No worklogs yet“, „No history yet“ (`L/common.json`) – passend zu Aktivitätsfiltern mit Transitions (Workflows) und Worklogs (Time Tracking) (UNVERIFIZIERT, ob Workspace-Log oder Work-Item-Activity).
  - Profil-Einstellungen „Activity – Track your recent actions and changes across all projects and work items.“ (`L/settings.json`, `account_settings.activity.*`, ohne CE-Referenz; CE-Profil-Settings-Tabs `general`, `preferences`, `notifications`, `security`, `api-tokens`, `T/settings.ts` Z. 11).
  - Icons `ActivityOutline/Filled`, `LogsOutline/Filled`, `LogsAltOutline/Filled`, `AuditLogsOutline/Filled`, `HistoryOutline/Filled` (`PROPEL/icons/miscellaneous/`).
- **Abgrenzung:** „API-enabled Audit Logs“ (Business, CS) = Dok. 27 P08-18.
- **Konfidenz:** CE-Basis hoch, EE-UI niedrig.

### 3.10 Home-, Your-Work- und Navigations-Erweiterungen

#### P05-34 – Home-, Your-Work- und Navigations-Erweiterungen

- **Tier:** unklar (teilweise Cloud-Inhalte).
- **Funktionsbeschreibung (belegt):**
  - **Home-Widgets:** `THomeWidgetKeys` = `quick_links`, `recents`, `my_stickies`, `quick_tutorial`, `new_at_plane` (`T/home.ts` Z. 11; Backend `WorkspaceHomePreference.HomeWidgetKeys`, `API/db/models/workspace.py` Z. 377–382). Im CE haben `new_at_plane` („New at Plane“) und `quick_tutorial` („Quick tutorial“) **keine Komponente** (`component: null`, `W/components/home/home-dashboard-widgets.tsx` Z. 49–58) und werden vom Backend beim Anlegen der Präferenzen ausgelassen (`API/app/views/workspace/home.py` Z. 29–33). Präferenz je Benutzer/Workspace: `key`, `is_enabled`, `config` (jsonb), `sort_order`; Verwaltung im Modal „Manage widgets“ mit Drag & Drop, Toasts „Widget reordered successfully.“ / „Error occurred while reordering widget.“ (`L/home.json`).
  - **Business-Trial-Banner** auf Home: „Your 14-day Business plan trial is live!“, „Explore all Business features. When you're ready, choose to subscribe. You'll not be billed automatically.“, „Trial ends today“, „Trial ends in {days} day(s)“, „Start subscription“, „Explore Business features“ (`L/home.json`, `home.business_trial_banner.*`) → **entfällt** (ADR-001).
  - **Sidebar-Benutzermenü** der Commercial Edition (`W/components/workspace/sidebar/user-menu.tsx` Z. 26–62, im CE nicht gerendert): Reihenfolge Home (`/{ws}/`, alle Rollen) → **Dashboards** (`/{ws}/dashboards/`, Admin/Member) → Your work (`/{ws}/profile/{userId}/`, Admin/Member) → Drafts (`/{ws}/drafts/`, Admin/Member, mit Zähler `draft_issue_count`) → Plane AI (`/{ws}/pi-chat/`, alle Rollen, Icon `PiChatLogo`).
  - **Workspace-Menü** (CE gerendert, `W/components/workspace/sidebar/workspace-menu.tsx` Z. 31–60): Projects, Views (`/workspace-views/all-issues/`), Cycles (`/active-cycles/`, P05-23), Analytics (`/analytics/`).
  - **Power-K:** „Go to all active cycles“ (P05-23), „Go to project overview“ (Projekt-Cluster), „Go to advanced search“ (P05-31) (`L/power-k.json` Z. 107, 108, 174).
  - **Your work** (Profilseiten Summary/Assigned/Created/Subscribed/Activity, `C/profile.ts` Z. 10–44; Routen `W/app/routes/core.ts` Z. 91–99) ist CE; EE-Erweiterungen sind **nicht** belegt.
- **Ergänzender Entwurf (UNVERIFIZIERT):** „New at Plane“ = Feed von Produktneuigkeiten (Changelog), „Quick tutorial“ = Einstiegsvideos/-schritte; beide sind in der Cloud an externe Inhalte gebunden.
- **Migrationshinweis (ADR-004):** „New at Plane“ nur mit gebündeltem, offline verfügbarem Inhalt (z. B. Release-Notes der eigenen Plattform) oder deaktiviert; „Quick tutorial“ mit gebündelten Assets. Sidebar-Benutzermenü und Teamspaces-Navigation rendern (Reihenfolge s. o.; Position der Teamspaces in der Sidebar UNVERIFIZIERT, O-03).
- **Konfidenz:** hoch (Widget-Keys, Menüstruktur), niedrig (Widget-Inhalte).

---

## 4. Offene Punkte / Unklarheiten

| Nr. | Thema | Unklarheit | Vorschlag / Nachrecherche |
|---|---|---|---|
| O-01 | Recherche-Lücke | WebSearch-Budget in diesem Lauf erschöpft (erster Aufruf abgewiesen); `docs.plane.so`/`plane.so` nicht abrufbar; GitHub-Doku-Repo nicht freigegeben. Viele Detailangaben sind daher „UNVERIFIZIERT“. | Folgelauf mit Budget, gezielt: https://docs.plane.so/core-concepts/workspaces/teamspaces , https://docs.plane.so/core-concepts/issues/plane-query-language , https://docs.plane.so/core-concepts/dashboards (Pfad UNVERIFIZIERT), https://docs.plane.so/core-concepts/cycles (Active cycles, Progress, Reports; Pfad UNVERIFIZIERT), https://docs.plane.so/core-concepts/views (Shared/Publish; Pfad UNVERIFIZIERT), https://plane.so/changelog (WS4–WS12 Inhalte), https://plane.so/pricing |
| O-02 | Teamspaces – Rechte | Wer darf Teamspaces anlegen/löschen (nur Workspace-Admin?), Rolle des Leads, Sichtbarkeit von Projekten/Work Items für Teamspace-Mitglieder ohne Projektmitgliedschaft | Nachrecherche WS1/WS2; bis dahin: Admin legt an, Lead/Admin verwaltet, Daten nur aus Projekten mit Mitgliedschaft |
| O-03 | Teamspaces – Navigation/Routen | Position in der Sidebar, exakte Routen (`/:ws/teamspaces/:teamspaceId/...`), Tabs | Route-Parameter `teamspaceId`, `viewId`, `projectId` sind belegt (`W/hooks/use-issue-layout-store.ts`); Pfadsegmente UNVERIFIZIERT |
| O-04 | Teamspace-Cycles | Eigene UI oder Aggregation der Projekt-Cycles? | Aggregation (Entwurf P05-05) |
| O-05 | Dashboards – Widget-Katalog | Exakte Widget-Typen (Number? Table? Text?), Editor-UI, Rasterlogik, Sichtbarkeit/Teilen von Dashboards | Nachrecherche WS4–WS8 und Nutzer-Doku Dashboards |
| O-06 | Y-Metriken | Semantik von `BLOCKED_WORK_ITEM_COUNT`, `WORK_ITEM_DUE_THIS_WEEK_COUNT` (Wochenbeginn), `ESTIMATE_POINT_COUNT` bei Kategorien-/Zeit-Estimates | Vorschlag P05-10; Wochenbeginn aus Benutzer-Einstellung `start_of_the_week` (CE-Profilfeld, Dok. 03) |
| O-07 | Progress v2 | Antwortschema `…/cycle-progress/`; Erzeugungsrhythmus der Tageswerte; Bedeutung „Trailing“/„Leading“ | Entwurf P05-19 |
| O-08 | Cycle Updates | Existenz nicht belegt | erst nach Nachrecherche umsetzen; Updates-Modul generisch |
| O-09 | Publish Views – Tier | R1 sagt Pro, R2 legt One nahe | für die Portierung irrelevant (ADR-001) |
| O-10 | PQL – Grammatik | Vollständige Feld-/Funktionsliste, `NOT`, `!=`, Datumsvergleiche, Fehlermeldungen; zwei Dialekte (MCP camelCase vs. Webhook snake_case) | Parser mit Aliasen (P05-29); Nachrecherche WS13 |
| O-11 | Advanced Search – UI | Eigene Seite oder nur erweitertes Power-K? | Nachrecherche WS12; Minimal: Power-K-Ergebnisse aus FTS + Link „Go to advanced search“ auf Suchseite |
| O-12 | Insights, Custom Reports, Time Capsule, Scheduled Comms | nur Matrix-Texte, teils „Coming soon“/auskommentiert | Insights und Custom Reports als niedrig priorisierte Erweiterung der Widget-Engine; Time Capsule nicht portieren (nicht ausgeliefert) |
| O-13 | Analytics-Tabs | Welche zusätzlichen Tabs EE heute zeigt | Entwurf P05-15; Texte vorhanden |
| O-14 | Auto-Schedule | Zeitpunkt der Nachproduktion künftiger Cycles; Verhalten bei manuell angelegten Cycles; Wechselwirkung mit Parallel Cycles | Entwurf P05-21 |
| O-15 | Home-Widgets | Inhalte „New at Plane“/„Quick tutorial“ im Airgapped-Betrieb | gebündelte Inhalte oder ausblenden (ADR-004) |
| O-16 | `dashboards.widget.color_palettes.*` | i18n-Schlüssel referenziert, aber in keiner Locale vorhanden | Texte „Modern“, „Horizon“, „Earthen“ (aus den Keys abgeleitet, UNVERIFIZIERT) in alle Locales aufnehmen |
| O-17 | Orphan-Heuristik | Referenzstatus in Anhang B ist heuristisch (dynamische Schlüssel können fälschlich als unreferenziert erscheinen; 7 Fälle manuell korrigiert) | bei Implementierung je Schlüssel prüfen |

---

## Anhang A: Inventar der CE-Spuren (Stubs, Typen, Extension-Points) des Clusters

| Nr. | Datei (Zeilen) | Inhalt | Feature |
|---|---|---|---|
| A-01 | `T/issues/issue.ts` Z. 29–43 | `EIssuesStoreType` mit `TEAM`, `TEAM_VIEW`, `TEAM_PROJECT_WORK_ITEMS` | P05-02 … P05-04 |
| A-02 | `W/store/issue/root.store.ts` Z. 46, 80–81, 92–96, 114, 148–149, 160–161, 166–167, 181, 205, 242–243, 251–252, 257–258 | `teamspaceId`; Stores `teamIssues(Filter)`, `teamViewIssues(Filter)`, `teamProjectWorkItems(Filter)` als Projekt-Store-Platzhalter | P05-02 … P05-04 |
| A-03 | `W/hooks/store/use-issues.ts` Z. 40–149 | Mapping der Team-Store-Typen | P05-02 … P05-04 |
| A-04 | `W/hooks/use-issue-layout-store.ts` Z. 16–40 | Store-Typ aus Route-Parametern `teamspaceId`, `viewId`, `projectId` | P05-02 … P05-04 |
| A-05 | `W/store/router.store.ts` Z. 18, 45, 80–84 | Getter `teamspaceId` aus der Query | P05-08 |
| A-06 | `W/components/issues/issue-layouts/utils.tsx` Z. 95–104, 155, 846 | `isWorkspaceLevel` inkl. Team-Typen; `team_project: getTeamProjectColumns` (CE `undefined`) | P05-02 |
| A-07 | `W/store/issue/helpers/base-issues.store.ts` Z. 126, 140 | `team_project` → `project_id` | P05-02 |
| A-08 | `W/store/issue/helpers/issue-filter-helper.store.ts` Z. 146 | Filter `team_project` | P05-02 |
| A-09 | `C/issue/common.ts` Z. 39, 102–111, 120 | Enum-Wert `team_project`, `TCreateModalStoreTypes`, Gruppierung „Team project“ | P05-02 |
| A-10 | `T/view-props.ts` Z. 25, 77, 140; `T/issues.ts` Z. 129 | `team_project` in Group-By/Order/Filter-Typen | P05-02 |
| A-11 | `U/work-item/base.ts` Z. 104–113; `C/issue/filter.ts` Z. 112–295 | `viewType` `team_issues`, `team_project_work_items` ohne Konfiguration in `ISSUE_DISPLAY_FILTERS_BY_PAGE` | P05-02, P05-03 |
| A-12 | `W/hooks/use-group-dragndrop.ts` Z. 29 | DnD-Typ inkl. `TEAM_PROJECT_WORK_ITEMS` | P05-03 |
| A-13 | `T/enums.ts` Z. 71, 74, 82, 85; `API/db/models/asset.py` Z. 36–46 | Asset-Typen `TEAM_SPACE_DESCRIPTION`, `TEAM_SPACE_COMMENT_DESCRIPTION` (Backend ohne) | P05-01, P05-06 |
| A-14 | `T/enums.ts` Z. 87–91 | `EUpdateStatus` | P05-26 |
| A-15 | `packages/editor/src/types/document-collaborative-events.ts` Z. 35–80 | `teamspace_id` in Realtime-Ereignissen | P05-04 |
| A-16 | `T/page/core.ts` Z. 78–83 | `documentType: "team_page"`, `teamId` | P05-04 |
| A-17 | `W/components/dropdowns/member/member-select.tsx` Z. 55–65 | Kommentar zu EE-Member-Scopes `teamspaceId` | P05-08 |
| A-18 | `W/components/work-item-filters/filters-hoc/shared.ts` Z. 13; `packages/shared-state/src/store/work-item-filters/filter.store.ts` Z. 31 | Entitätstyp „teamspace“ | P05-08 |
| A-19 | `B/empty-state/assets/asset-types.ts` Z. 50, 65; `B/empty-state/assets/asset-registry.tsx` Z. 113, 134; `B/empty-state/assets/vertical-stack/{dashboard,teamspace}.tsx` | Illustrationen `dashboard`, `teamspace` | P05-01, P05-09 |
| A-20 | `API/db/models/workspace.py` Z. 261–283 | Legacy-Modell `Team` (nicht portieren) | P05-01 |
| A-21 | `W/components/workspace/sidebar/user-menu.tsx` Z. 26–62 | `SIDEBAR_USER_MENU_ITEMS` mit „Dashboards“ (Z. 34–40); Komponente nicht gerendert | P05-09, P05-34 |
| A-22 | `C/chart.ts` Z. 10–135 | Achsenklassen, `ChartXAxisDateGrouping`, `TO_CAPITALIZE_PROPERTIES`, `CHART_X_AXIS_DATE_PROPERTIES`, `EChartModels`, `CHART_COLOR_PALETTES` | P05-10 |
| A-23 | `T/analytics.ts` Z. 9–47 | `ChartXAxisProperty` (+ `WORK_ITEM_TYPES`, `PROJECTS`, `EPICS`), `ChartYAxisMetric` (+ 6 EE-Metriken), Tab-Typen mit `isDisabled` | P05-10, P05-15 |
| A-24 | `T/charts/common.ts` Z. 7–18; `T/charts/index.ts` | `TChartColorScheme`, `TChart`, `TChartDatum`, Chart-Props (Lollipop, Comparison-Line, Center-Label) | P05-10 |
| A-25 | `W/components/chart/utils.ts` Z. 19–175 | `parseChartData` (Kommentar „WIDGET_X_AXIS_DATE_PROPERTIES“), `generateExtendedColors` | P05-10 |
| A-26 | `W/components/analytics/tabs.tsx`; `W/components/analytics/use-analytics-tabs.tsx` | Tab-Liste; ungenutzter Parameter `_workspaceSlug` | P05-15 |
| A-27 | `W/components/active-cycles/workspace-active-cycles-upgrade.tsx`; `W/app/(all)/[workspaceSlug]/(projects)/active-cycles/page.tsx`; `W/app/routes/core.ts` Z. 66–67; `W/app/assets/workspace-active-cycles/cta-{l-1,r-1,r-2}-{dark,light}.webp` | Upsell-Seite statt Funktion | P05-23 |
| A-28 | `W/services/cycle.service.ts` Z. 25–78; `packages/services/src/cycle/cycle.service.ts` Z. 29; `packages/services/src/cycle/cycle-analytics.service.ts` Z. 30–78 | `workspaceActiveCycles` (`/active-cycles/`), `workspaceActiveCyclesProgressPro` (`/cycle-progress/`) | P05-19, P05-23 |
| A-29 | `W/store/cycle.store.ts` Z. 74, 245–252, 362, 380, 504 | `fetchActiveCycleProgressPro` No-op; `getIsPointsDataAvailable` mit `version === 2`; `plotType` | P05-19 |
| A-30 | `W/store/issue/cycle/issue.store.ts` Z. 146–156 | Aufruf Pro-Progress bei `version === 2` und offener Sidebar | P05-19 |
| A-31 | `T/cycle/cycle.ts` Z. 53–64, 112–113, 139, 147–158 | `TCycleProgress`, `progress`, `version`, `TCyclePlotType`, `TProgressChartData` | P05-19 |
| A-32 | `U/cycle.ts` Z. 79–190 | `scope`, `ideal`, `formatV1Data`, `formatV2Data`, `formatActiveCycle` (ohne Aufrufer) | P05-19 |
| A-33 | `W/components/cycles/analytics-sidebar/issue-progress.tsx` Z. 40–43 | `cycleChartOptions` „Burn-down“/„Burn-up“ ohne UI | P05-19 |
| A-34 | `T/workspace.ts` Z. 219–228; `C/fetch-keys.ts` Z. 98–99 | `IWorkspaceActiveCyclesResponse`, SWR-Key | P05-23 |
| A-35 | `W/components/views/publish/use-view-publish.tsx`; `W/components/views/quick-actions.tsx` Z. 58, 88; `W/components/views/view-list-item-action.tsx` Z. 62, 98–107; `U/project-views.ts` Z. 105–110 | Publish-Stub, „Live“-Badge, Link-Helper | P05-28 |
| A-36 | `T/views.ts` Z. 39, 43–56; `T/publish.ts` Z. 10 | Publish-Typen; `TPublishEntityType` ohne `view` | P05-28 |
| A-37 | `API/db/models/deploy_board.py` Z. 19–39 | `TYPE_CHOICES` inkl. `view` | P05-28 |
| A-38 | `SPC/app/routes.ts` | keine Route `views/:anchor` | P05-28 |
| A-39 | `API/api/views/issue.py` Z. 324–335 | Ablehnung `pql`/`filters` | P05-29 |
| A-40 | `T/rich-filters/operators/extended.ts`, `T/rich-filters/field-types/extended.ts`, `T/rich-filters/operator-configs/extended.ts`, `T/rich-filters/derived/extended.ts`, `C/rich-filters/operator-labels/extended.ts`, `W/hooks/rich-filters/use-filters-operator-configs.ts` | leere EE-Operator-Erweiterungen, `allowNegative: false` | P05-30 |
| A-41 | `API/utils/filters/filter_backend.py` Z. 147–210, 350–422 | Backend wertet `and`/`or`/`not` aus | P05-29, P05-30 |
| A-42 | `L/power-k.json` Z. 107, 108, 174 | Power-K-Ziele ohne CE-Referenz | P05-23, P05-31, P05-34 |
| A-43 | `W/components/home/home-dashboard-widgets.tsx` Z. 27–59; `API/app/views/workspace/home.py` Z. 29–33; `API/db/models/workspace.py` Z. 374–383 | Widgets `new_at_plane`, `quick_tutorial` ohne Komponente / vom Backend ausgelassen | P05-34 |
| A-44 | `W/store/workspace/index.ts` Z. 385–391 | `mutateWorkspaceMembersActivity` No-op | P05-33 |
| A-45 | `W/components/workspace/sidebar/workspace-menu.tsx` Z. 46–52 | Sidebar-Eintrag Active Cycles (ADMIN/MEMBER) | P05-23 |
| A-46 | `W/app/routes/extended.ts` | `extendedRoutes = []` (Routen für Teamspaces, Dashboards u. a. fehlen) | alle |
| A-47 | `C/subscription.ts` Z. 7–49 | Feature-Listen der Upgrade-Karten (entfallen, ADR-001) | Tier-Belege |
| A-48 | `W/components/license/modal/upgrade-modal.tsx` Z. 70 | Upsell-Text „Dashboards, Workflows, Approvals, Time Management …“ (entfällt) | P05-09 |

---

## Anhang B: i18n-Schlüssel des Clusters (vollständig, mit Referenzstatus)

Spalte „im CE referenziert“: Ergebnis der heuristischen Analyse (P01-Orphan-Liste) mit manuellen Korrekturen (O-17). „nein (Kandidat EE/Legacy)“ bedeutet: im CE-Code nicht verwendet – entweder EE-Text oder Legacy-Rest (siehe K1, K2, K5). Alle Texte sind in 22 Sprachen vorhanden und 1:1 zu übernehmen; Upsell-/Trial-Texte entfallen (ADR-001).

| Datei | Schlüssel | Text (en) | im CE referenziert |
|---|---|---|---|
| `common.json` | `active_cycles` | Active cycles | ja |
| `common.json` | `active_cycles_description` | Monitor cycles across projects, track high-priority work items, and zoom in cycles that need attention. | ja |
| `common.json` | `on_demand_snapshots_of_all_your_cycles` | On-demand snapshots of all your cycles | ja |
| `common.json` | `10000_feet_view` | 10,000-feet view of all active cycles. | ja |
| `common.json` | `10000_feet_view_description` | Zoom out to see running cycles across all your projects at once instead of going from Cycle to Cycle in each project. | ja (dynamisch: Template-Literal mit Suffix `_description` in `W/components/active-cycles/workspace-active-cycles-upgrade.tsx` Z. 130) |
| `common.json` | `get_snapshot_of_each_active_cycle` | Get a snapshot of each active cycle. | ja |
| `common.json` | `get_snapshot_of_each_active_cycle_description` | Track high-level metrics for all active cycles, see their state of progress, and get a sense of scope against deadlines. | ja (dynamisch: Template-Literal mit Suffix `_description` in `W/components/active-cycles/workspace-active-cycles-upgrade.tsx` Z. 130) |
| `common.json` | `compare_burndowns` | Compare burndowns. | ja |
| `common.json` | `compare_burndowns_description` | Monitor how each of your teams are performing with a peek into each cycle's burndown report. | ja (dynamisch: Template-Literal mit Suffix `_description` in `W/components/active-cycles/workspace-active-cycles-upgrade.tsx` Z. 130) |
| `common.json` | `quickly_see_make_or_break_issues` | Quickly see make-or-break work items. | ja |
| `common.json` | `quickly_see_make_or_break_issues_description` | Preview high-priority work items for each cycle against due dates. See all of them per cycle in one click. | ja (dynamisch: Template-Literal mit Suffix `_description` in `W/components/active-cycles/workspace-active-cycles-upgrade.tsx` Z. 130) |
| `common.json` | `zoom_into_cycles_that_need_attention` | Zoom into cycles that need attention. | ja |
| `common.json` | `zoom_into_cycles_that_need_attention_description` | Investigate the state of any cycle that doesn't conform to expectations in one click. | ja (dynamisch: Template-Literal mit Suffix `_description` in `W/components/active-cycles/workspace-active-cycles-upgrade.tsx` Z. 130) |
| `common.json` | `stay_ahead_of_blockers` | Stay ahead of blockers. | ja |
| `common.json` | `stay_ahead_of_blockers_description` | Spot challenges from one project to another and see inter-cycle dependencies that aren't obvious from any other view. | ja (dynamisch: Template-Literal mit Suffix `_description` in `W/components/active-cycles/workspace-active-cycles-upgrade.tsx` Z. 130) |
| `common.json` | `your_work` | Your work | ja |
| `common.json` | `preview` | Preview | nein (Kandidat EE/Legacy) |
| `common.json` | `cycles_description` | Timebox work per project and adjust the time period as needed. One cycle can be 2 weeks, the next 1 week. | nein (Kandidat EE/Legacy) |
| `common.json` | `views_description` | Save custom sorts, filters, and display options or share them with your team. | nein (Kandidat EE/Legacy) |
| `common.json` | `common.team_project` | Team project | ja |
| `common.json` | `common.on_track` | On-Track | nein (Kandidat EE/Legacy) |
| `common.json` | `common.off_track` | Off-Track | nein (Kandidat EE/Legacy) |
| `common.json` | `common.at_risk` | At risk | nein (Kandidat EE/Legacy) |
| `common.json` | `common.team` | Team | nein (Kandidat EE/Legacy) |
| `common.json` | `common.teams` | Teams | nein (Kandidat EE/Legacy) |
| `common.json` | `common.project_updates` | Project Updates | nein (Kandidat EE/Legacy) |
| `common.json` | `common.members_and_teamspaces` | Members & Teamspaces | nein (Kandidat EE/Legacy) |
| `common.json` | `chart.x_axis` | X-axis | nein (Kandidat EE/Legacy) |
| `common.json` | `chart.y_axis` | Y-axis | nein (Kandidat EE/Legacy) |
| `common.json` | `chart.metric` | Metric | nein (Kandidat EE/Legacy) |
| `common.json` | `workspace_dashboards` | Dashboards | ja |
| `cycle.json` | `active_cycle.empty_state.progress.title` | Add work items to the cycle to view it's progress | ja |
| `cycle.json` | `active_cycle.empty_state.chart.title` | Add work items to the cycle to view the burndown chart. | ja |
| `cycle.json` | `active_cycle.empty_state.priority_issue.title` | Observe high priority work items tackled in the cycle at a glance. | ja |
| `cycle.json` | `active_cycle.empty_state.assignee.title` | Add assignees to work items to see a breakdown of work by assignees. | ja |
| `cycle.json` | `active_cycle.empty_state.label.title` | Add labels to work items to see the breakdown of work by labels. | ja |
| `cycle.json` | `cycle.label` | {count, plural, one {Cycle} other {Cycles}} | ja |
| `cycle.json` | `cycle.no_cycle` | No cycle | ja |
| `cycle.json` | `active_cycle_analytics.empty_state.progress.title` | Add work items to the cycle to view it's\n progress | nein (Kandidat EE/Legacy) |
| `cycle.json` | `active_cycle_analytics.empty_state.priority.title` | Observe high priority work items tackled in\n the cycle at a glance. | nein (Kandidat EE/Legacy) |
| `cycle.json` | `active_cycle_analytics.empty_state.assignee.title` | Add assignees to work items to see a\n breakdown of work by assignees. | nein (Kandidat EE/Legacy) |
| `cycle.json` | `active_cycle_analytics.empty_state.label.title` | Add labels to work items to see the\n breakdown of work by labels. | nein (Kandidat EE/Legacy) |
| `empty-state.json` | `common_empty_state.progress.title` | There're no progress metrics to show yet. | nein (Kandidat EE/Legacy) |
| `empty-state.json` | `common_empty_state.progress.description` | Start setting property values in work items to see progress metrics here. | nein (Kandidat EE/Legacy) |
| `empty-state.json` | `common_empty_state.updates.title` | No updates yet. | nein (Kandidat EE/Legacy) |
| `empty-state.json` | `common_empty_state.updates.description` | Once project members add updates it will appear here | nein (Kandidat EE/Legacy) |
| `empty-state.json` | `workspace_empty_state.views.title` | No Views yet | nein (Kandidat EE/Legacy) |
| `empty-state.json` | `workspace_empty_state.views.description` | Add work items to your project and use views to filter, sort, and monitor progress effortlessly. | nein (Kandidat EE/Legacy) |
| `empty-state.json` | `workspace_empty_state.views.cta_primary` | Add work item | nein (Kandidat EE/Legacy) |
| `empty-state.json` | `workspace_empty_state.analytics_projects.title` | Create projects to visualize project metrics here. | nein (Kandidat EE/Legacy) |
| `empty-state.json` | `workspace_empty_state.analytics_work_items.title` | Create projects with work items and assignees to start tracking performance, progress, and team impact here. | ja |
| `empty-state.json` | `workspace_empty_state.analytics_no_cycle.title` | Create cycles to organise work into time-bound phases and track progress across sprints. | nein (Kandidat EE/Legacy) |
| `empty-state.json` | `workspace_empty_state.analytics_no_module.title` | Create modules to organize your work and track progress across different stages. | nein (Kandidat EE/Legacy) |
| `empty-state.json` | `workspace_empty_state.analytics_no_intake.title` | Set up intake to manage incoming requests and track how they're accepted and rejected | nein (Kandidat EE/Legacy) |
| `empty-state.json` | `workspace_empty_state.active_cycles.title` | No active cycles | nein (Kandidat EE/Legacy) |
| `empty-state.json` | `workspace_empty_state.active_cycles.description` | You don't have any ongoing cycles right now. Active cycles appear here when they include today's date. | nein (Kandidat EE/Legacy) |
| `empty-state.json` | `workspace_empty_state.dashboard.title` | Visualize your progress with dashboards | nein (Kandidat EE/Legacy) |
| `empty-state.json` | `workspace_empty_state.dashboard.description` | Build customizable dashboards to track metrics, measure outcomes, and present insights effectively. | nein (Kandidat EE/Legacy) |
| `empty-state.json` | `workspace_empty_state.dashboard.cta_primary` | Create new dashboard | nein (Kandidat EE/Legacy) |
| `workspace.json` | `workspace_dashboard.empty_state.general.title` | Overview of your projects, activity, and metrics | nein (Kandidat EE/Legacy) |
| `workspace.json` | `workspace_dashboard.empty_state.general.description` | Welcome to Plane, we are excited to have you here. Create your first project and track your work items, and this page will transform into a space that helps you progress. Admins will also see items which help their team progress. | nein (Kandidat EE/Legacy) |
| `workspace.json` | `workspace_dashboard.empty_state.general.primary_button.text` | Build your first project | nein (Kandidat EE/Legacy) |
| `workspace.json` | `workspace_dashboard.empty_state.general.primary_button.comic.title` | Everything starts with a project in Plane | nein (Kandidat EE/Legacy) |
| `workspace.json` | `workspace_dashboard.empty_state.general.primary_button.comic.description` | A project could be a product's roadmap, a marketing campaign, or launching a new car. | nein (Kandidat EE/Legacy) |
| `workspace.json` | `workspace_analytics.label` | Analytics | ja |
| `workspace.json` | `workspace_analytics.page_label` | {workspace} - Analytics | ja (Template-Literal ohne Platzhalter, `W/app/(all)/[workspaceSlug]/(projects)/analytics/[tabId]/page.tsx` Z. 43) |
| `workspace.json` | `workspace_analytics.open_tasks` | Total open tasks | nein (Kandidat EE/Legacy) |
| `workspace.json` | `workspace_analytics.error` | There was some error in fetching the data. | nein (Kandidat EE/Legacy) |
| `workspace.json` | `workspace_analytics.work_items_closed_in` | Work items closed in | nein (Kandidat EE/Legacy) |
| `workspace.json` | `workspace_analytics.selected_projects` | Selected projects | nein (Kandidat EE/Legacy) |
| `workspace.json` | `workspace_analytics.total_members` | Total members | nein (Kandidat EE/Legacy) |
| `workspace.json` | `workspace_analytics.total_cycles` | Total cycles | nein (Kandidat EE/Legacy) |
| `workspace.json` | `workspace_analytics.total_modules` | Total modules | nein (Kandidat EE/Legacy) |
| `workspace.json` | `workspace_analytics.pending_work_items.title` | Pending work items | nein (Kandidat EE/Legacy) |
| `workspace.json` | `workspace_analytics.pending_work_items.empty_state` | Analysis of pending work items by co-workers appears here. | nein (Kandidat EE/Legacy) |
| `workspace.json` | `workspace_analytics.work_items_closed_in_a_year.title` | Work items closed in a year | nein (Kandidat EE/Legacy) |
| `workspace.json` | `workspace_analytics.work_items_closed_in_a_year.empty_state` | Close work items to view analysis of the same in the form of a graph. | nein (Kandidat EE/Legacy) |
| `workspace.json` | `workspace_analytics.most_work_items_created.title` | Most work items created | nein (Kandidat EE/Legacy) |
| `workspace.json` | `workspace_analytics.most_work_items_created.empty_state` | Co-workers and the number of work items created by them appears here. | nein (Kandidat EE/Legacy) |
| `workspace.json` | `workspace_analytics.most_work_items_closed.title` | Most work items closed | nein (Kandidat EE/Legacy) |
| `workspace.json` | `workspace_analytics.most_work_items_closed.empty_state` | Co-workers and the number of work items closed by them appears here. | nein (Kandidat EE/Legacy) |
| `workspace.json` | `workspace_analytics.tabs.scope_and_demand` | Scope and Demand | nein (Kandidat EE/Legacy) |
| `workspace.json` | `workspace_analytics.tabs.custom` | Custom Analytics | nein (Kandidat EE/Legacy) |
| `workspace.json` | `workspace_analytics.total` | Total {entity} | ja |
| `workspace.json` | `workspace_analytics.started_work_items` | Started {entity} | ja |
| `workspace.json` | `workspace_analytics.backlog_work_items` | Backlog {entity} | ja |
| `workspace.json` | `workspace_analytics.un_started_work_items` | Unstarted {entity} | ja |
| `workspace.json` | `workspace_analytics.completed_work_items` | Completed {entity} | ja |
| `workspace.json` | `workspace_analytics.project_insights` | Project Insights | ja |
| `workspace.json` | `workspace_analytics.summary_of_projects` | Summary of Projects | ja |
| `workspace.json` | `workspace_analytics.all_projects` | All Projects | ja |
| `workspace.json` | `workspace_analytics.trend_on_charts` | Trend on charts | ja |
| `workspace.json` | `workspace_analytics.active_projects` | Active Projects | ja |
| `workspace.json` | `workspace_analytics.customized_insights` | Customized Insights | ja |
| `workspace.json` | `workspace_analytics.created_vs_resolved` | Created vs Resolved | ja |
| `workspace.json` | `workspace_analytics.empty_state.project_insights.title` | No data yet | nein (Kandidat EE/Legacy) |
| `workspace.json` | `workspace_analytics.empty_state.project_insights.description` | Work items assigned to you, broken down by state, will show up here. | nein (Kandidat EE/Legacy) |
| `workspace.json` | `workspace_analytics.empty_state.created_vs_resolved.title` | No data yet | nein (Kandidat EE/Legacy) |
| `workspace.json` | `workspace_analytics.empty_state.created_vs_resolved.description` | Work items created and resolved over time will show up here. | nein (Kandidat EE/Legacy) |
| `workspace.json` | `workspace_analytics.empty_state.customized_insights.title` | No data yet | nein (Kandidat EE/Legacy) |
| `workspace.json` | `workspace_analytics.empty_state.customized_insights.description` | Work items assigned to you, broken down by state, will show up here. | nein (Kandidat EE/Legacy) |
| `workspace.json` | `workspace_analytics.empty_state.general.title` | Track progress, workloads, and allocations. Spot trends, remove blockers, and move work faster | nein (Kandidat EE/Legacy) |
| `workspace.json` | `workspace_analytics.empty_state.general.description` | See scope versus demand, estimates, and scope creep. Get performance by team members and teams, and make sure your project runs on time. | nein (Kandidat EE/Legacy) |
| `workspace.json` | `workspace_analytics.empty_state.general.primary_button.text` | Start your first project | nein (Kandidat EE/Legacy) |
| `workspace.json` | `workspace_analytics.empty_state.general.primary_button.comic.title` | Analytics works best with Cycles + Modules | nein (Kandidat EE/Legacy) |
| `workspace.json` | `workspace_analytics.empty_state.general.primary_button.comic.description` | First, timebox your issues into Cycles and, if you can, group issues that span more than a cycle into Modules. Check out both on the left nav. | nein (Kandidat EE/Legacy) |
| `workspace.json` | `workspace_analytics.empty_state.cycle_progress.title` | No data yet | nein (Kandidat EE/Legacy) |
| `workspace.json` | `workspace_analytics.empty_state.cycle_progress.description` | Cycle progress analytics will appear here. Add work items to cycles to start tracking progress. | nein (Kandidat EE/Legacy) |
| `workspace.json` | `workspace_analytics.empty_state.module_progress.title` | No data yet | nein (Kandidat EE/Legacy) |
| `workspace.json` | `workspace_analytics.empty_state.module_progress.description` | Module progress analytics will appear here. Add work items to modules to start tracking progress. | nein (Kandidat EE/Legacy) |
| `workspace.json` | `workspace_analytics.empty_state.intake_trends.title` | No data yet | nein (Kandidat EE/Legacy) |
| `workspace.json` | `workspace_analytics.empty_state.intake_trends.description` | Intake trends analytics will appear here. Add work items to intake to start tracking trends. | nein (Kandidat EE/Legacy) |
| `workspace.json` | `workspace_analytics.upgrade_to_plan` | Upgrade to {plan} to unlock {tab} | nein (Kandidat EE/Legacy) |
| `workspace.json` | `workspace_analytics.workitem_resolved_vs_pending` | Work items resolved vs pending | nein (Kandidat EE/Legacy) |
| `workspace.json` | `workspace_analytics.projects_by_status` | Projects by status | nein (Kandidat EE/Legacy) |
| `workspace.json` | `workspace_analytics.active_users` | Active users | nein (Kandidat EE/Legacy) |
| `workspace.json` | `workspace_analytics.intake_trends` | Intake Trends | nein (Kandidat EE/Legacy) |
| `workspace.json` | `workspace_cycles.empty_state.active.title` | No active cycles | nein (Kandidat EE/Legacy) |
| `workspace.json` | `workspace_cycles.empty_state.active.description` | Cycles of your projects that includes any period that encompasses today's date within its range. Find the progress and details of all your active cycle here. | nein (Kandidat EE/Legacy) |
| `project.json` | `project_cycles.active_cycle.label` | Active cycle | ja |
| `project.json` | `project_cycles.active_cycle.progress` | Progress | ja |
| `project.json` | `project_cycles.active_cycle.chart` | Burndown chart | nein (Kandidat EE/Legacy) |
| `project.json` | `project_cycles.active_cycle.priority_issue` | Priority work items | ja |
| `project.json` | `project_cycles.active_cycle.assignees` | Assignees | ja |
| `project.json` | `project_cycles.active_cycle.issue_burndown` | Work item burndown | ja |
| `project.json` | `project_cycles.active_cycle.ideal` | Ideal | nein (Kandidat EE/Legacy) |
| `project.json` | `project_cycles.active_cycle.current` | Current | nein (Kandidat EE/Legacy) |
| `project.json` | `project_cycles.active_cycle.labels` | Labels | ja |
| `project.json` | `project_cycles.active_cycle.trailing` | Trailing | nein (Kandidat EE/Legacy) |
| `project.json` | `project_cycles.active_cycle.leading` | Leading | nein (Kandidat EE/Legacy) |
| `project-settings.json` | `project_settings.project_updates.heading` | Project Updates | nein (Kandidat EE/Legacy) |
| `project-settings.json` | `project_settings.project_updates.description` | Consolidated tracking and progress monitoring for this project | nein (Kandidat EE/Legacy) |
| `project-settings.json` | `project_settings.cycles.auto_schedule.heading` | Auto-schedule cycles | nein (Kandidat EE/Legacy) |
| `project-settings.json` | `project_settings.cycles.auto_schedule.description` | Keep cycles moving without manual setup. | nein (Kandidat EE/Legacy) |
| `project-settings.json` | `project_settings.cycles.auto_schedule.tooltip` | Automatically create new cycles based on your chosen schedule. | nein (Kandidat EE/Legacy) |
| `project-settings.json` | `project_settings.cycles.auto_schedule.edit_button` | Edit | nein (Kandidat EE/Legacy) |
| `project-settings.json` | `project_settings.cycles.auto_schedule.form.cycle_title.label` | Cycle Title | nein (Kandidat EE/Legacy) |
| `project-settings.json` | `project_settings.cycles.auto_schedule.form.cycle_title.placeholder` | Title | nein (Kandidat EE/Legacy) |
| `project-settings.json` | `project_settings.cycles.auto_schedule.form.cycle_title.tooltip` | The title will be appended with numbers for subsequent cycles. For eg: Design - 1/2/3 | nein (Kandidat EE/Legacy) |
| `project-settings.json` | `project_settings.cycles.auto_schedule.form.cycle_title.validation.required` | Cycle title is required | nein (Kandidat EE/Legacy) |
| `project-settings.json` | `project_settings.cycles.auto_schedule.form.cycle_title.validation.max_length` | Title must not exceed 255 characters | nein (Kandidat EE/Legacy) |
| `project-settings.json` | `project_settings.cycles.auto_schedule.form.cycle_duration.label` | Cycle Duration | nein (Kandidat EE/Legacy) |
| `project-settings.json` | `project_settings.cycles.auto_schedule.form.cycle_duration.unit` | Weeks | nein (Kandidat EE/Legacy) |
| `project-settings.json` | `project_settings.cycles.auto_schedule.form.cycle_duration.validation.required` | Cycle duration is required | nein (Kandidat EE/Legacy) |
| `project-settings.json` | `project_settings.cycles.auto_schedule.form.cycle_duration.validation.min` | Cycle duration must be at least 1 week | nein (Kandidat EE/Legacy) |
| `project-settings.json` | `project_settings.cycles.auto_schedule.form.cycle_duration.validation.max` | Cycle duration cannot exceed 30 weeks | nein (Kandidat EE/Legacy) |
| `project-settings.json` | `project_settings.cycles.auto_schedule.form.cycle_duration.validation.positive` | Cycle duration must be positive | nein (Kandidat EE/Legacy) |
| `project-settings.json` | `project_settings.cycles.auto_schedule.form.cooldown_period.label` | Cooldown Period | nein (Kandidat EE/Legacy) |
| `project-settings.json` | `project_settings.cycles.auto_schedule.form.cooldown_period.unit` | days | nein (Kandidat EE/Legacy) |
| `project-settings.json` | `project_settings.cycles.auto_schedule.form.cooldown_period.tooltip` | Pause between cycles before the next begins. | nein (Kandidat EE/Legacy) |
| `project-settings.json` | `project_settings.cycles.auto_schedule.form.cooldown_period.validation.required` | Cooldown period is required | nein (Kandidat EE/Legacy) |
| `project-settings.json` | `project_settings.cycles.auto_schedule.form.cooldown_period.validation.negative` | Cooldown period cannot be negative | nein (Kandidat EE/Legacy) |
| `project-settings.json` | `project_settings.cycles.auto_schedule.form.start_date.label` | Cycle starts day | nein (Kandidat EE/Legacy) |
| `project-settings.json` | `project_settings.cycles.auto_schedule.form.start_date.validation.required` | Start date is required | nein (Kandidat EE/Legacy) |
| `project-settings.json` | `project_settings.cycles.auto_schedule.form.start_date.validation.past` | Start date cannot be in the past | nein (Kandidat EE/Legacy) |
| `project-settings.json` | `project_settings.cycles.auto_schedule.form.number_of_cycles.label` | Number of future cycles | nein (Kandidat EE/Legacy) |
| `project-settings.json` | `project_settings.cycles.auto_schedule.form.number_of_cycles.validation.required` | Number of cycles is required | nein (Kandidat EE/Legacy) |
| `project-settings.json` | `project_settings.cycles.auto_schedule.form.number_of_cycles.validation.min` | At least 1 cycle is required | nein (Kandidat EE/Legacy) |
| `project-settings.json` | `project_settings.cycles.auto_schedule.form.number_of_cycles.validation.max` | Cannot schedule more than 3 cycles | nein (Kandidat EE/Legacy) |
| `project-settings.json` | `project_settings.cycles.auto_schedule.form.auto_rollover.label` | Auto-rollover work items | nein (Kandidat EE/Legacy) |
| `project-settings.json` | `project_settings.cycles.auto_schedule.form.auto_rollover.tooltip` | On the day a cycle completes, move all unfinished work items into the next cycle. | nein (Kandidat EE/Legacy) |
| `project-settings.json` | `project_settings.cycles.auto_schedule.toast.toggle.loading_enable` | Enabling auto-schedule cycles | nein (Kandidat EE/Legacy) |
| `project-settings.json` | `project_settings.cycles.auto_schedule.toast.toggle.loading_disable` | Disabling auto-schedule cycles | nein (Kandidat EE/Legacy) |
| `project-settings.json` | `project_settings.cycles.auto_schedule.toast.toggle.success.title` | Success! | nein (Kandidat EE/Legacy) |
| `project-settings.json` | `project_settings.cycles.auto_schedule.toast.toggle.success.message` | Auto-schedule cycles toggled successfully. | nein (Kandidat EE/Legacy) |
| `project-settings.json` | `project_settings.cycles.auto_schedule.toast.toggle.error.title` | Error! | nein (Kandidat EE/Legacy) |
| `project-settings.json` | `project_settings.cycles.auto_schedule.toast.toggle.error.message` | Failed to toggle auto-schedule cycles. | nein (Kandidat EE/Legacy) |
| `project-settings.json` | `project_settings.cycles.auto_schedule.toast.save.loading` | Saving auto-schedule cycles configuration | nein (Kandidat EE/Legacy) |
| `project-settings.json` | `project_settings.cycles.auto_schedule.toast.save.success.title` | Success! | nein (Kandidat EE/Legacy) |
| `project-settings.json` | `project_settings.cycles.auto_schedule.toast.save.success.message_create` | Auto-schedule cycles configuration saved successfully. | nein (Kandidat EE/Legacy) |
| `project-settings.json` | `project_settings.cycles.auto_schedule.toast.save.success.message_update` | Auto-schedule cycles configuration updated successfully. | nein (Kandidat EE/Legacy) |
| `project-settings.json` | `project_settings.cycles.auto_schedule.toast.save.error.title` | Error! | nein (Kandidat EE/Legacy) |
| `project-settings.json` | `project_settings.cycles.auto_schedule.toast.save.error.message_create` | Failed to save auto-schedule cycles configuration. | nein (Kandidat EE/Legacy) |
| `project-settings.json` | `project_settings.cycles.auto_schedule.toast.save.error.message_update` | Failed to update auto-schedule cycles configuration. | nein (Kandidat EE/Legacy) |
| `power-k.json` | `power_k.navigation_actions.nav_workspace_active_cycle` | Go to all active cycles | nein (Kandidat EE/Legacy) |
| `power-k.json` | `power_k.navigation_actions.nav_project_overview` | Go to project overview | nein (Kandidat EE/Legacy) |
| `power-k.json` | `power_k.search_menu.no_results` | No results found | ja |
| `power-k.json` | `power_k.search_menu.clear_search` | Clear search | ja |
| `power-k.json` | `power_k.search_menu.go_to_advanced_search` | Go to advanced search | nein (Kandidat EE/Legacy) |
| `update.json` | `updates.progress.title` | Progress | nein (Kandidat EE/Legacy) |
| `update.json` | `updates.progress.since_last_update` | Since last update | nein (Kandidat EE/Legacy) |
| `update.json` | `updates.progress.comments` | {count, plural, one{# Comment} other{# Comments}} | nein (Kandidat EE/Legacy) |
| `update.json` | `updates.add_update` | Add Update | nein (Kandidat EE/Legacy) |
| `update.json` | `updates.add_update_placeholder` | Add your update here | nein (Kandidat EE/Legacy) |
| `update.json` | `updates.empty.title` | No updates yet | nein (Kandidat EE/Legacy) |
| `update.json` | `updates.empty.description` | You can see the updates here. | nein (Kandidat EE/Legacy) |
| `update.json` | `updates.reaction.create.success.title` | Reaction created | nein (Kandidat EE/Legacy) |
| `update.json` | `updates.reaction.create.success.message` | The reaction has been successfully created | nein (Kandidat EE/Legacy) |
| `update.json` | `updates.reaction.create.error.title` | Reaction not created | nein (Kandidat EE/Legacy) |
| `update.json` | `updates.reaction.create.error.message` | The reaction could not be created | nein (Kandidat EE/Legacy) |
| `update.json` | `updates.reaction.remove.success.title` | Reaction removed | nein (Kandidat EE/Legacy) |
| `update.json` | `updates.reaction.remove.success.message` | The reaction has been successfully removed | nein (Kandidat EE/Legacy) |
| `update.json` | `updates.reaction.remove.error.title` | Reaction not removed | nein (Kandidat EE/Legacy) |
| `update.json` | `updates.reaction.remove.error.message` | The reaction could not be removed | nein (Kandidat EE/Legacy) |
| `update.json` | `updates.create.success.title` | Update created | nein (Kandidat EE/Legacy) |
| `update.json` | `updates.create.success.message` | The update has been successfully created | nein (Kandidat EE/Legacy) |
| `update.json` | `updates.create.error.title` | Update not created | nein (Kandidat EE/Legacy) |
| `update.json` | `updates.create.error.message` | The update could not be created | nein (Kandidat EE/Legacy) |
| `update.json` | `updates.delete.title` | Delete update | nein (Kandidat EE/Legacy) |
| `update.json` | `updates.delete.confirmation` | Are you sure you want to delete this update? This is an irreversible action. | nein (Kandidat EE/Legacy) |
| `update.json` | `updates.delete.success.title` | Update deleted | nein (Kandidat EE/Legacy) |
| `update.json` | `updates.delete.success.message` | The update has been successfully deleted | nein (Kandidat EE/Legacy) |
| `update.json` | `updates.delete.error.title` | Update not deleted | nein (Kandidat EE/Legacy) |
| `update.json` | `updates.delete.error.message` | The update could not be deleted | nein (Kandidat EE/Legacy) |
| `update.json` | `updates.update.success.title` | Updated | nein (Kandidat EE/Legacy) |
| `update.json` | `updates.update.success.message` | The update has been successfully updated | nein (Kandidat EE/Legacy) |
| `update.json` | `updates.update.error.title` | Update not updated | nein (Kandidat EE/Legacy) |
| `update.json` | `updates.update.error.message` | The update could not be updated | nein (Kandidat EE/Legacy) |
| `page.json` | `page_actions.move_page.cannot_move_to_teamspace` | Private and shared pages cannot be moved to a teamspace. | nein (Kandidat EE/Legacy) |
| `page.json` | `page_actions.move_page.placeholders.workspace_to_all` | Search for projects and teamspaces | nein (Kandidat EE/Legacy) |
| `page.json` | `page_actions.move_page.placeholders.workspace_to_project` | Search for projects | nein (Kandidat EE/Legacy) |
| `page.json` | `page_actions.move_page.placeholders.project_to_all` | Search for projects and teamspaces | nein (Kandidat EE/Legacy) |
| `page.json` | `page_actions.move_page.placeholders.project_to_project` | Search for projects | nein (Kandidat EE/Legacy) |
| `page.json` | `page_actions.move_page.placeholders.project_to_all_with_wiki` | Search for wiki collections, projects, and teamspaces | nein (Kandidat EE/Legacy) |
| `page.json` | `page_actions.move_page.placeholders.project_to_project_with_wiki` | Search for wiki collections and projects | nein (Kandidat EE/Legacy) |
| `home.json` | `home.new_at_plane.title` | New at Plane | ja |
| `home.json` | `home.quick_tutorial.title` | Quick tutorial | ja |
| `home.json` | `home.widget.reordered_successfully` | Widget reordered successfully. | ja |
| `home.json` | `home.widget.reordering_failed` | Error occurred while reordering widget. | ja |
| `home.json` | `home.manage_widgets` | Manage widgets | ja |
| `home.json` | `home.business_trial_banner.title` | Your 14-day Business plan trial is live! | nein (Kandidat EE/Legacy) |
| `home.json` | `home.business_trial_banner.description` | Explore all Business features. When you're ready, choose to subscribe. You'll not be billed automatically. | nein (Kandidat EE/Legacy) |
| `home.json` | `home.business_trial_banner.trial_ends_today` | Trial ends today | nein (Kandidat EE/Legacy) |
| `home.json` | `home.business_trial_banner.trial_ends_in_days` | Trial ends in {days, plural, one {# day} other {# days}} | nein (Kandidat EE/Legacy) |
| `home.json` | `home.business_trial_banner.start_subscription` | Start subscription | nein (Kandidat EE/Legacy) |
| `home.json` | `home.business_trial_banner.explore_business_features` | Explore Business features | nein (Kandidat EE/Legacy) |
| `settings.json` | `account_settings.activity.heading` | Activity | nein (Kandidat EE/Legacy) |
| `settings.json` | `account_settings.activity.description` | Track your recent actions and changes across all projects and work items. | nein (Kandidat EE/Legacy) |

**Nicht vorhandene, aber referenzierte Schlüssel:** `dashboards.widget.color_palettes.modern`, `dashboards.widget.color_palettes.horizon`, `dashboards.widget.color_palettes.earthen` (`C/chart.ts` Z. 49, 77, 105 – in keiner Locale-Datei vorhanden, O-16).

---

## Anhang C: Icons und Illustrationen des Clusters

Quelle Icons: `PROPEL/icons/<kategorie>/<name>-{outline,filled}.d.ts` (Export-Namen `<Name>Outline`, `<Name>Filled`). Quelle Illustrationen: `B/empty-state/assets/`.

| Kategorie | Icons (jeweils Outline + Filled) | Verwendung im Cluster |
|---|---|---|
| `workspace-features` | `teamspaces`, `dashboards`, `cycles`, `views`, `analytics`, `your-work`, `home`, `drafts` | Teamspaces (P05-01), Dashboards (P05-09), Active Cycles (P05-23, `CyclesOutline` mit `rotate-180`), Views (P05-27/28), Analytics (P05-15), Sidebar (P05-34) |
| `project-features` | `overview` | Overviews mit Progress Charts (P05-19) |
| `charts` | `area`, `bar`, `donut`, `line`, `pie` | Widget-Typen (P05-10) |
| `miscellaneous` | `widget`, `updates`, `activity`, `logs`, `logs-alt`, `audit-logs`, `history`, `transfer-work-item`, `transfer-work-item-alt` | Widgets, Updates (P05-26), Activity Logs (P05-33), Transfer/Rollover (P05-22) |
| Illustrationen (vertikal) | `dashboard` (`vertical-stack/dashboard.tsx`), `teamspace` (`vertical-stack/teamspace.tsx`), `cycle`, `view` | Leerzustände P05-09, P05-01, P05-23, P05-27 |
| Illustrationen (horizontal) | `update` (`horizontal-stack/update.tsx`), `search-compact` | Updates-Leerzustand, Suche |
| Bild-Assets | `W/app/assets/workspace-active-cycles/cta-{l-1,r-1,r-2}-{dark,light}.webp` | nur Upsell (entfällt, ADR-001) |

---

## Anhang D: Endpunkt-Inventar des Clusters

Legende Status: **CE** = im CE-Backend vorhanden; **fehlt (CE-FE ruft)** = vom CE-Frontend aufgerufen, im CE-Backend nicht vorhanden; **EE-Public** = in der Commercial-Public-API dokumentiert; **Vorschlag** = clean-room-Entwurf dieses Dokuments (UNVERIFIZIERT).

| Nr. | Methode | Pfad | Zweck | Status | Quelle |
|---|---|---|---|---|---|
| E-01 | GET | `/api/workspaces/{slug}/active-cycles/?per_page=&cursor=` | Workspace-Active-Cycles | fehlt (CE-FE ruft) | `W/services/cycle.service.ts` Z. 64–78 |
| E-02 | GET | `/api/workspaces/{slug}/projects/{project_id}/cycles/{cycle_id}/cycle-progress/` | Fortschritt v2 (Progress Charts) | fehlt (CE-FE ruft, No-op) | `W/services/cycle.service.ts` Z. 52–62 |
| E-03 | GET | `/api/workspaces/{slug}/projects/{project_id}/cycles/{cycle_id}/progress/` | Fortschritt (State-Gruppen, Estimate-Summen) | CE | `API/app/urls/cycle.py` Z. 96–99 |
| E-04 | GET | `/api/workspaces/{slug}/projects/{project_id}/cycles/{cycle_id}/analytics/?type=issues\|points` | Verteilung + `completion_chart` | CE | `API/app/urls/cycle.py` Z. 101–105 |
| E-05 | POST | `/api/workspaces/{slug}/projects/{project_id}/cycles/{cycle_id}/transfer-issues/` | Transfer + Snapshot | CE | Dok. 04 |
| E-06 | GET/POST | `/api/v1/workspaces/{slug}/teamspaces/` | Teamspaces | EE-Public | `DD/api-reference/teamspace/` |
| E-07 | GET/PATCH/DELETE | `/api/v1/workspaces/{slug}/teamspaces/{teamspace_id}/` | Teamspace | EE-Public | dto. |
| E-08 | GET/POST/DELETE | `/api/v1/workspaces/{slug}/teamspaces/{teamspace_id}/members/` | Mitglieder (`member_ids`) | EE-Public | dto. |
| E-09 | GET/POST/DELETE | `/api/v1/workspaces/{slug}/teamspaces/{teamspace_id}/projects/` | Projekte (`project_ids`) | EE-Public | dto. |
| E-10 | GET/PATCH | `/api/v1/workspaces/{slug}/features/` | Workspace-Features inkl. `teams` | EE-Public | `DD/api-reference/workspace-features/` |
| E-11 | POST | `/api/v1/workspaces/{slug}/work-items/advanced-search/` | Advanced Search | EE-Public | `DD/api-reference/issue/advanced-search-work-items.md` |
| E-12 | GET | `/api/v1/workspaces/{slug}/projects/{project_id}/work-items/?pql=&filters=` | PQL-/Strukturfilter | CE lehnt ab (400) / EE-Public (MCP) | `API/api/views/issue.py` Z. 324–335; `DD/dev-tools/mcp-server-tools.md` |
| E-13 | GET | `/api/workspaces/{slug}/search/` | einfache Suche (Basis P05-31) | CE | Dok. 03 SR-01 |
| E-14 | GET | `/api/workspaces/{slug}/advance-analytics/`, `…-stats/`, `…-charts/` (+ Projekt-Varianten unter `…/projects/{project_id}/`) | Analytics (Basis P05-15) | CE | `API/app/urls/analytic.py` Z. 60–88 |
| E-15 | GET/POST/PATCH/DELETE | `/api/workspaces/{slug}/analytic-view/…`, `saved-analytic-view/{id}/` | Legacy-Analytics-Ansichten (Basis P05-16) | CE | `API/app/urls/analytic.py` Z. 31–43 |
| E-16 | GET | `/api/workspaces/{slug}/user-activity/{user_id}/` (+ `export/`) | Aktivität je Benutzer (Basis P05-33) | CE | Dok. 27 P08-17 |
| E-17 | GET, PATCH | `/api/workspaces/{slug}/home-preferences/`, `/api/workspaces/{slug}/home-preferences/{key}/` | Home-Widgets (Basis P05-34) | CE | `API/app/urls/workspace.py` Z. 230–236; `API/app/views/workspace/home.py` |
| E-18 | GET/POST | `/api/workspaces/{slug}/teamspaces/` (+ Detail, `members/`, `projects/`, `issues/`, `projects/{project_id}/issues/`, `cycles/`, `views/`, `views/{view_id}/issues/`, `pages/`, `comments/`, `activities/`) | interne App-API Teamspaces | Vorschlag | P05-01 … P05-06 |
| E-19 | GET | `/api/workspaces/{slug}/members/lite/?scope=&teamspace_id=&project_ids=&cursor=&search=` | Member-Auswahl mit Scopes | Vorschlag | P05-08 |
| E-20 | GET/POST, GET/PATCH/DELETE | `/api/workspaces/{slug}/dashboards/`, `…/dashboards/{dashboard_id}/` | Dashboards | Vorschlag | P05-09 |
| E-21 | GET/POST, PATCH/DELETE, GET | `…/dashboards/{dashboard_id}/widgets/`, `…/widgets/{widget_id}/`, `…/widgets/{widget_id}/charts/` | Widgets und Widget-Daten (`TChart`) | Vorschlag | P05-10 |
| E-22 | GET/POST, GET | `…/projects/{project_id}/cycles/{cycle_id}/reports/`, `…/reports/{report_id}/` | Cycle Reports | Vorschlag | P05-20 |
| E-23 | GET/POST/PATCH | `…/projects/{project_id}/cycle-schedule/` (+ `toggle/`) | Auto-Schedule/Rollover | Vorschlag | P05-21, P05-22 |
| E-24 | POST | `…/projects/{project_id}/cycles/{cycle_id}/complete/` | Cycle abschließen | Vorschlag | P05-25 |
| E-25 | GET/POST/DELETE | `…/projects/{project_id}/views/{view_id}/members/`, `…/workspace-views/{view_id}/members/` | Shared Views | Vorschlag | P05-27 |
| E-26 | GET/POST/PATCH/DELETE | `…/projects/{project_id}/views/{view_id}/publish/`; öffentlich `/api/public/anchor/{anchor}/views/…` | Publish Views | Vorschlag | P05-28 |
| E-27 | GET/POST/PATCH/DELETE | `/api/workspaces/{slug}/reports/…` | Custom Reports | Vorschlag | P05-16 |
| E-28 | GET/POST/PATCH/DELETE | `/api/workspaces/{slug}/scheduled-communications/…` | Scheduled Comms | Vorschlag | P05-32 |
| E-29 | GET | `/api/workspaces/{slug}/activities/?actor=&project=&entity_type=&verb=&from=&to=&cursor=` | Workspace Activity Logs | Vorschlag (Dok. 27) | P05-33 |

---

## Anhang E: Abgrenzung – im CE bereits vorhandene Funktionen dieses Themenfelds

Diese Funktionen sind **keine** Bezahl-Features und werden über die Analyse-Dokumente in `migration/analysis/` portiert; sie bilden die Basis der EE-Erweiterungen.

| Funktion | Beleg | Bezug |
|---|---|---|
| Workspace-Views (globale Views „All work items“, „Assigned“, „Created“, „Subscribed“ + eigene; Private/Public, Sperren, Favoriten) | `T/workspace-views.ts` Z. 15–43; `W/components/workspace/views/*`; R1 Z. 488 | Basis P05-27/28 |
| Projekt-Views (Private/Public, Logo, Sortierung, Favoriten, `is_locked`) | `API/db/models/view.py` Z. 58–99; `W/components/views/*` | Basis P05-27/28 |
| Cycle-Burndown nach Work Items/Estimates, Cycle-Sidebar mit Verteilung nach Assignees/Labels/State-Gruppen, Projekt-Active-Cycle mit Karten Progress/Burndown/Priority-Assignees-Labels | `W/components/cycles/analytics-sidebar/*`; `W/components/cycles/active-cycle/*`; `W/components/core/sidebar/progress-chart.tsx` | Basis P05-19, P05-23 |
| Cycle-Transfer mit `progress_snapshot` | `API/utils/cycle_transfer_issues.py` Z. 410–432 | Basis P05-20, P05-22 |
| Analytics „Overview“ und „Work items“ inkl. Customized Insights (X/Y/Group-by), Created vs Resolved, Insight-Tabelle, Analytics-Modal in Cycle/Modul/Filterleiste | `W/components/analytics/*`; `W/components/issues/filters.tsx` Z. 56–136 | Basis P05-10, P05-15 |
| Legacy-Analytics-Endpunkte (`analytics/`, `analytic-view/`, `saved-analytic-view/`, `export-analytics/`, `default-analytics/`) | `API/app/urls/analytic.py` Z. 26–53 | Basis P05-16 |
| Home mit Widgets Quick links, Recents, Stickies, „Manage widgets“ | `W/components/home/*` | Basis P05-34 |
| Veraltetes Home-Dashboard (`overview_stats`, `assigned_issues`, `created_issues`, `issues_by_state_groups`, `issues_by_priority`, `recent_activity`, `recent_projects`, `recent_collaborators`) | `T/dashboard.ts`; `API/app/urls/user.py` Z. 80 | nicht mit P05-09 verwechseln |
| Your work (Profil: Summary, Assigned, Created, Subscribed, Activity) | `C/profile.ts` Z. 10–44; `W/app/routes/core.ts` Z. 91–99 | Basis P05-34 |
| Power-K-Suche (Workspace/Projekt) | `W/components/power-k/ui/modal/search-menu.tsx` | Basis P05-31 |
| Rich-Filter (AND, `exact`/`in`/`range`), Backend mit `and`/`or`/`not` | `T/rich-filters/*`; `API/utils/filters/filter_backend.py` | Basis P05-29/30 |
