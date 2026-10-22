# 23 – Bezahl-Features Cluster „Work Management“ (P04) – IST-Analyse

> **Gegenstand:** Plane v1.4.2 Community Edition (CE, AGPL-3.0), Repo-Root `/home/user/plane`. Spezifiziert werden **alle Funktionen des Clusters „Work Management“, die NICHT in der CE, sondern in den Bezahl-Editionen** (One/Pro/Business/Enterprise bzw. heute „Enterprise Grid“) enthalten sind: Work Item Types, Custom Properties (alle Typen, Pflichtfelder, Workspace- vs. Projekt-Ebene, Roll-ups, Formeln), Epics, Initiatives, Milestones, Releases, Customers, Recurring Work Items, Work Item Templates, Bulk Ops, Transfers/Conversions, Dependencies im Gantt, Auto-Transfer von Cycle-Work-Items, Module Overview, Auto-Assignment in Modules, Time Tracking/Worklogs/Timesheets/Approvals, Advanced Estimates, Public/Private/Secret Projects, Project States/Overview/Updates, Project Templates, Baselines & Deviations, Custom SLAs, Intake Forms/Assignees/Emails, Duplicate Detection.
> **Bindend:** `migration/architecture/00-grundsatzentscheidungen.md` – ADR-001 (eine Edition, alle Features immer aktiv, kein Upsell/Billing), ADR-002 (Realtime in .NET/YDotNet, kein Node zur Laufzeit), ADR-003 (Greenfield, fachliche Semantik bleibt, JSON-Verträge am Original orientiert), ADR-004 (Self-hosted/Airgapped, keine Pflicht-SaaS), ADR-005 (UI 1:1), ADR-006 (Original-Repo als Referenz).
> **Schwesterdokumente (nicht duplizieren, sondern ergänzen):** `migration/features/20-paid-spuren-im-repo.md` (P01, Repo-Spuren, PF-Nummern), `migration/features/21-paid-api-referenz-developer-docs.md` (P02, vollständige REST-Verträge der Commercial-API), `migration/features/22-paid-architektur-selfhosting-dienste.md` (P03, Commercial-Dienste inkl. Intake-E-Mail-Dienst), `migration/features/25-paid-workflows-automation-templates.md` (P06, Templates, Recurring Work Items, Workflows), `migration/features/26-paid-wissen-pages-wiki.md` (P07). CE-Basis: `migration/analysis/02b-datenmodell-arbeitsobjekte.md`, `migration/analysis/04-api-intern-arbeitsobjekte.md`.
> **Phase:** reine IST-Analyse, keine Implementierung. Stand: 2026-10-21.

---

## Inhaltsverzeichnis

1. Überblick & Quellenlage
2. Feature-Tabelle (Feature | ab Plan | Abstufung je Plan | CE-Status | Quelle)
3. Feature-Abschnitte
   - 3.0 Querschnitt: Feature-Toggles, Rollen, Activity-Typen, Icons/Illustrationen, Settings-Navigation
   - 3.1 Work Item Types und Typ-Hierarchie (WM-01, WM-02)
   - 3.2 Custom Properties – Engine, alle Property-Typen, Pflichtfelder, Formeln, Workspace-Ebene, Roll-ups (WM-03 … WM-08)
   - 3.3 Epics, Epic-Fortschritt, Epic-Updates (WM-09, WM-10)
   - 3.4 Initiatives, Initiative-Labels, Initiative-Updates, Checkpoints (WM-11 … WM-13)
   - 3.5 Milestones (WM-14)
   - 3.6 Releases (WM-15)
   - 3.7 Customers, Customer Requests, Customer Properties (WM-16 … WM-18)
   - 3.8 Recurring Work Items, Work Item Templates, Pre-defined Templates (WM-19 … WM-21)
   - 3.9 Bulk Ops, Transfers, Conversions, Duplikat in anderes Projekt (WM-22 … WM-25)
   - 3.10 Dependencies im Gantt und Custom Relations (WM-26, WM-27)
   - 3.11 Cycles & Modules: Auto-Transfer, Auto-Schedule, Module Overview, Auto-Assignment (WM-28 … WM-31)
   - 3.12 Time Tracking, Worklogs, Timesheets, Approvals (WM-32 … WM-34)
   - 3.13 Advanced Estimates (WM-35)
   - 3.14 Projekte: Public/Private/Secret, Project States, Project Labels, Overview, Updates, Templates (WM-36 … WM-41)
   - 3.15 Baselines & Deviations, Custom SLAs (WM-42, WM-43)
   - 3.16 Intake Forms, Intake Assignees, Emails for Intake (WM-44 … WM-46)
   - 3.17 Duplicate Detection (WM-47)
4. Offene Punkte / Unklarheiten / Rückfragen
- Anhang A: Endpunkt-Inventar des Clusters (Commercial-API, vollständig)
- Anhang B: i18n-Inventar des Clusters (Schlüssel → Feature)
- Anhang C: Icon- und Illustrations-Inventar des Clusters (UI 1:1)

---

## 1. Überblick & Quellenlage

### 1.1 Ausgangslage und Methode

Der Code der Commercial Edition (`makeplane/plane-ee`) ist closed-source und nicht verfügbar. Alle Bezahl-Funktionen dieses Clusters sind daher **clean-room** aus folgenden Quellen spezifiziert:

1. **CE-Repo** (`/home/user/plane`): Plan-Matrix, Upsell-Stellen, CE-Stubs/Extension-Points, Datenmodell-Felder ohne Funktion, Typen/Enums, mitgelieferte EE-Texte (i18n), Icons, Illustrationen. Jede CE-Status-Aussage wurde per `grep`/Lesen gegen das Repo geprüft.
2. **Offline-Developer-Docs** (`/home/user/makeplane/developer-docs/docs`): REST-API-Referenz der Commercial Edition, MCP-Server-Tool-Referenz (präziseste Quelle für Enums und Verhalten), Plane Compose (YAML-Schema für Typen/Properties/Features/Milestones), Webhooks, OAuth-Scopes, Self-Hosting-Doku (Plan-Badges, Intake-E-Mail, Plane AI/Embeddings).
3. **Web (sekundär):** Die Hosts `docs.plane.so`, `plane.so`, `university.plane.so` sind per Netzwerk-Policy nicht abrufbar (WebFetch → `getaddrinfo ENOTFOUND university.plane.so`; analog für plane.so laut Auftrag). **In diesem Lauf war das WebSearch-Budget des gesamten Workflows bereits ausgeschöpft** („limit: 200 WebSearch calls per turn, shared by every agent“) – es konnte **keine eigene WebSearch** ausgeführt werden. Das Quell-Repo der Nutzer-Doku (`makeplane/docs`) ist über GitHub nicht erreichbar (GitHub-MCP: Repository nicht für die Session freigegeben; `https://github.com/makeplane/docs` → HTTP 404). Web-Fakten in diesem Dokument stammen daher ausschließlich aus **WebSearch-Zusammenfassungen, die die Schwesterdokumente 20/21/22/25/26 bereits erhoben und mit URL belegt haben**; sie sind als **„W (via Dok NN)“** gekennzeichnet und nicht von P04 selbst verifiziert. Fehlende Web-Belege für Detailverhalten sind als **UNVERIFIZIERT** markiert. **Empfehlung:** Nach Freigabe weiterer WebSearch-Kontingente die in Kap. 4 gelisteten Punkte gezielt nachrecherchieren (Folge-Auftrag).

### 1.2 Planstufen

| Plan-Key im Repo | Bedeutung | Quelle |
|---|---|---|
| `free` | Free = funktional die CE („at par with the Free tier of the Cloud edition“) | `apps/web/components/workspace/billing/comparison/plans.tsx` (`PLANS_LIST`, Z. 70); `/home/user/makeplane/developer-docs/docs/self-hosting/editions-and-versions.md` (via Dok 20 §1.1) |
| `one` | historischer Self-hosted-Plan (Einmalpreis 799 „per workspace“, `isActive: false`) | `plans.tsx` Z. 1266–1275 |
| `pro` | Pro | `plans.tsx` Z. 1276–1285 |
| `business` | Business („Talk to Sales“) | `plans.tsx` Z. 1286–1293 |
| `enterprise` | Enterprise; öffentlich heute „**Enterprise Grid**“ (Top-Lizenz) | `plans.tsx` Z. 1294–1301; Doku-Badges `[Enterprise Grid]` in `/home/user/makeplane/developer-docs/docs/self-hosting/govern/ldap.md`, `…/methods/airgapped-edition.md`, `…/methods/fips-deployment.md`; W: https://plane.so/pricing, https://plane.so/enterprise-grid (via Dok 25 §1.2) |

**Wichtig:** Die Plan-Matrix `plans.tsx` ist ein **älterer Stand** als die öffentliche Doku 2026 (Dok 25 §1.2 belegt Umgruppierungen). Wo Quellen sich widersprechen, nennt die Feature-Tabelle beide Angaben. **Für die Portierung ist die Tier-Zuordnung nach ADR-001 irrelevant** – alle Features sind immer aktiv; Upgrade-Badges, „Get Pro“/„Upgrade“-Leerzustände und Plan-Gates (HTTP 402) entfallen und werden durch die echte Funktion ersetzt.

### 1.3 Quellenverzeichnis (Kürzel)

**Repo (R)**

| Kürzel | Pfad | Inhalt |
|---|---|---|
| R1 | `apps/web/components/workspace/billing/comparison/plans.tsx` | Offizielle Feature×Plan-Matrix `PLANS_COMPARISON_LIST` (Z. 72–1255), `planHighlights` (Z. 1303–1309) |
| R2 | `packages/constants/src/subscription.ts` | `ENTERPRISE_PLAN_FEATURES`, `BUSINESS_PLAN_FEATURES`, `PRO_PLAN_FEATURES`, `ONE_PLAN_FEATURES`, `FREE_PLAN_UPGRADE_FEATURES` |
| R3 | `packages/i18n/src/locales/en/work-item-type.json` | EE-Texte Work Item Types, Properties, Formeln, Hierarchie (vollständig gelesen, 474 Zeilen) |
| R4 | `packages/i18n/src/locales/en/project-settings.json` | EE-Texte Estimates (edit/switch/time), Feature-Seiten Time tracking/Milestones/Intake (Forms, Email, Notify), Project Updates, Templates, Auto-schedule cycles (vollständig gelesen, 526 Zeilen) |
| R5 | `packages/i18n/src/locales/en/workspace-settings.json` | Worklogs, Project states, Projects (Tabs), Templates, Relations |
| R6 | `packages/i18n/src/locales/en/work-item.json` | Relationstypen inkl. Dependencies, Duplicate-Modal, Bulk-Operations-Fehler, Recurring, Epic-Texte, Votes, Replies |
| R7 | `packages/i18n/src/locales/en/empty-state.json` | Leerzustände Epics, Worklogs, Work Item Types, Templates, Recurring, Project States |
| R8 | `packages/i18n/src/locales/en/common.json` | Navigation-/Gruppenlabels (`common.custom_properties`, `common.milestones`, `common.worklogs`, …), Update-Status, `duplicate_issue_found`, `failed_to_move_issue_to_project` |
| R9 | `packages/i18n/src/locales/en/update.json` | Updates-Feed (Project/Epic/Initiative-Updates) |
| R10 | `packages/i18n/src/locales/en/template.json` | Template-Texte (Projekt/Work Item/Page) |
| R11 | `apps/api/plane/db/models/issue_type.py` | `IssueType`, `ProjectIssueType` (CE, ohne Properties) |
| R12 | `apps/api/plane/db/models/project.py` | `ProjectNetwork` (Z. 30–36), `Project.NETWORK_CHOICES` (Z. 71), `network` (Z. 76), `default_assignee` (Z. 79), Feature-Flags (Z. 95–102) |
| R13 | `apps/api/plane/db/models/issue.py` | `Issue.type` (Z. 164–170), `IssueRelationChoices` + Reverse-Paare (Z. 272–293), `IssueRelation` (Z. 296–321) |
| R14 | `apps/api/plane/app/views/issue/relation.py`, `apps/api/plane/utils/issue_relation_mapper.py` | CE-Relations-Endpunkt inkl. Dependency-Typen |
| R15 | `apps/api/plane/db/models/intake.py`, `apps/api/plane/db/models/deploy_board.py` | `SourceType` (nur `IN_APP`), `IntakeIssue.source/source_email/extra`, `DeployBoard.TYPE_CHOICES` inkl. `intake` |
| R16 | `apps/web/components/issues/issue-modal/context/issue-modal-context.tsx`, `apps/web/components/issues/issue-modal/provider.tsx`, `apps/web/components/issues/issue-modal/form.tsx`, `apps/web/components/issues/issue-modal/base.tsx` | EE-Extension-Points im Work-Item-Modal (Properties, Templates, Convert, Sub-Work-Items) |
| R17 | `apps/web/store/timeline/base-timeline.store.ts`, `apps/web/store/timeline/issues-timeline.store.ts`, `apps/web/components/gantt-chart/**` | Gantt-Dependency-Stubs |
| R18 | `apps/web/components/issues/bulk-operations/root.tsx`, `apps/web/hooks/use-bulk-operation-status.ts`, `apps/web/store/issue/helpers/base-issues.store.ts`, `apps/web/services/issue/issue.service.ts`, `packages/types/src/issues/issue.ts` | Bulk-Ops-Stub und -Plumbing |
| R19 | `packages/constants/src/estimates.ts`, `apps/web/components/estimates/**`, `apps/api/plane/db/models/estimate.py`, `apps/api/plane/app/urls/estimate.py` | Estimates inkl. `time` (EE) |
| R20 | `packages/types/src/de-dupe.ts`, `apps/web/hooks/use-debounced-duplicate-issues.tsx` | Duplicate-Detection-Stub |
| R21 | `apps/web/components/common/activity/helper.tsx` | Projekt-Activity-Felder inkl. EE-Toggles (Z. 67–71, 266–285) |
| R22 | `apps/api/plane/utils/cycle_transfer_issues.py`, `apps/api/plane/app/views/cycle/base.py` (Z. 599–627) | CE-Cycle-Transfer (manuell) |
| R23 | npm `@makeplane/propel@0.7.3` (entpackt, nur gelesen): `/tmp/claude-0/-home-user-plane/fe89ae79-d9fa-54e4-b848-1dc9726b58d0/scratchpad/propel-pkg/package/dist/icons/<kategorie>/*.d.ts` | Icons (Anhang C) |
| R24 | `packages/blocks/src/empty-state/assets/{horizontal-stack,vertical-stack}/*.tsx` | Leerzustands-Illustrationen (Anhang C) |

**Offline-Doku (D)** – Basis `/home/user/makeplane/developer-docs/docs/`

| Kürzel | Pfad | Inhalt |
|---|---|---|
| D1 | `api-reference/` (Ordner `epics`, `initiative`, `milestones`, `worklogs`, `customer`, `issue-types/{types,properties,options,values}`, `project-features`, `workspace-features`, `project-labels`, `project`, `cycle`, `intake-issue`) | REST-Verträge (Anhang A) |
| D2 | `dev-tools/mcp-server-tools.md` | MCP-Tools: Enums, Verhalten (z. B. Release, Customer-Stage, Property-Typen, Relation-Definitionen) |
| D3 | `dev-tools/plane-compose.md` | YAML-Schema `schema/types.yaml` (Property-Typen inkl. `release_picker`, `formula`), `schema/features.yaml`, `work/milestones.yaml`, Workspace-Ebene „(Enterprise)“ |
| D4 | `dev-tools/intro-webhooks.md` | Webhook-v2-Events (Milestones, Relations, Dependencies) |
| D5 | `dev-tools/build-plane-app/oauth-scopes.md` | OAuth-Scopes |
| D6 | `self-hosting/govern/configure-dns-email-service.md`, `self-hosting/govern/environment-variables.md`, `self-hosting/plane-architecture.md` | Intake-E-Mail (Badge „Business“) |
| D7 | `self-hosting/govern/plane-ai/configure-plane-ai.md`, `self-hosting/govern/plane-ai/configure-embedding-model.md` | Duplicate Detection via Plane AI/Embeddings |

**Web (W, nur sekundär über Schwesterdokumente)** – URLs wie in den Schwesterdokumenten belegt: https://docs.plane.so/work-item-types, https://docs.plane.so/work-items/epics, https://plane.so/blog/epics-is-becoming-a-work-item-type-in-plane, https://plane.so/changelog/2026-05-31-epics-work-item-type-publish-mcp-apps, https://forum.plane.so/t/enabling-work-item-types-via-rest-api-silently-and-permanently-prevents-the-project-from-ever-having-the-native-epic-type/291, https://forum.plane.so/t/epics-is-becoming-a-work-item-type-ships-tuesday-may-26/136 (alle via Dok 21 §4.1/§4.7); https://university.plane.so/courses/201-the-growth/05-intro-to-initiatives.html, https://plane.so/plane-vs-linear (via Dok 21 §3 F02); https://docs.plane.so/customers, https://plane.so/blog/introducing-plane-business, https://plane.so/customer-requests, https://university.plane.so/courses/202-the-power-relay/02-intro-to-customers.html (via Dok 21 §4.3); https://plane.so/pricing (via Dok 20 PF-41); https://docs.plane.so/core-concepts/issues/time-tracking, https://university.plane.so/courses/201-the-growth/16-intro-to-time-tracking.html (via Dok 21 §4.6); https://plane.so/changelog/release-v-1-16-0-introducing-milestones-and-recurring-cycles (via Dok 21 §4.5, Dok 25 W49); https://plane.so/blog/introducing-releases (via Dok 21 §4.18); https://plane.so/changelog/release-v2-6-0-pql-releases-wiki-collections-and-more (via Dok 25 W47); https://university.plane.so/courses/201-the-growth/11-intro-to-project-states.html (via Dok 21 §4.12); https://plane.so/changelog/release-v2-5-0-project-labels-sso-for-god-mode-columns-in-pages (via Dok 26 W44); https://plane.so/changelog/cloud-april-28-2025 (via Dok 21 §4.13); https://plane.so/blog/new-work-item-detail-view-custom-relations-and-more (via Dok 25 W20); https://plane.so/changelog/release-v-1-13-0-duplicate-work-items-and-epics-across-projects (via Dok 26 W38); https://plane.so/changelog/2026-03-31-vote-on-work-items-link-sub-work-items-across-projects (via Dok 25 W50); https://docs.plane.so/workspace-administration/workspace-governance, https://plane.so/blog/introducing-workspace-governance (via Dok 25 W3/W4); https://docs.plane.so/roles-and-permissions/permissions-matrix (via Dok 25 W48); Templates/Recurring: Dok 25 W33–W44.

### 1.4 Legenden

**CE-Status** (gegen das Repo geprüft):
- **fehlt** – keine funktionale Spur außer Plan-Matrix/Texten/Icons.
- **Stub/UI-Hülle im CE** – Extension-Point, Typ/Enum, No-op-Hook, toter Service-Aufruf, Leerzustand/Upsell vorhanden; Funktion fehlt.
- **teilweise im CE** – Datenmodell oder Teilfunktion vorhanden, Bezahl-Teil fehlt.
- **im CE vorhanden (nur Cloud-Gating)** – Funktion vollständig im CE.

**Konfidenz:** **hoch** = durch Repo-Code/i18n-Text oder API-Referenz wörtlich belegt; **mittel** = aus mehreren Indizien abgeleitet oder nur über WebSearch-Zusammenfassung belegt; **niedrig** = nur Matrix-Text, Detailverhalten nicht belegt.

### 1.5 Ergebnis in Zahlen

| Kennzahl | Wert | Quelle |
|---|---|---|
| Features dieses Clusters (WM-01 … WM-47) | 47 | Kap. 2 |
| davon CE-Status „fehlt“ | 21 | Kap. 2 |
| davon „Stub/UI-Hülle im CE“ | 16 | Kap. 2 |
| davon „teilweise im CE“ | 10 | Kap. 2 |
| davon „im CE vorhanden (nur Cloud-Gating)“ | 0 | Kap. 2 |
| Commercial-REST-Endpunkte des Clusters (API v1, distinkte Methode+Pfad, nur EE; Anhang A.1) | 88 (+ 1 auch im CE vorhandener Endpunkt `transfer-issues`) | D1 |
| MCP-Aktionen ohne REST-Gegenstück, die Verhalten/Felder belegen (Anhang A.2) | 31 | D2 |
| EE-Texte des Clusters im CE-i18n (Schlüsselgruppen, Anhang B) | 31 Gruppen | R3–R10 |

---

## 2. Feature-Tabelle

| ID | Feature | ab Plan | Abstufung je Plan | CE-Status | Quelle |
|---|---|---|---|---|---|
| WM-01 | Work Item Types (Projekt-Ebene: Typen mit Icon/Hintergrund, Default-Typ, aktiv/inaktiv, Typwechsel) | Pro | Free/One ✗; Pro/Business/Enterprise ✓ | teilweise im CE (Modelle `IssueType`/`ProjectIssueType`, `Issue.type`, `Project.is_issue_type_enabled`, `type_id` in Serializern; kein CRUD, keine UI) | R1 Z. 205–214; R1 `planHighlights.pro` „Custom work items + Properties“ (Z. 1306); R3 `work_item_types.empty_state.get_pro.title` „Get Pro to enable Work item types.“; W docs.plane.so/work-item-types (via Dok 21) |
| WM-02 | Work-Item-Type-Hierarchie (Level, Parent/Child-Regeln zwischen Typen, Bruch-Validierung) | unklar (Workspace-Ebene; UNVERIFIZIERT) | – | teilweise im CE (nur `IssueType.level` Float, `ProjectIssueType.level` PositiveInt) | R3 `work_item_type_hierarchy.*`; R11 Z. 22, 37; W changelog 2026-05-31 (via Dok 21 §4.1) |
| WM-03 | Custom Properties – Projekt-Ebene (Property je Work Item Type, Werte am Work Item, Anzeige in Modal/Detail/Peek) | Pro | Pro „Project-level custom properties“; Business/Enterprise „Workspace-level properties and roll-ups“ | Stub/UI-Hülle im CE (Modal-Kontext-Signaturen, No-op-Hooks, Activity-Typ) | R1 Z. 216–225; R16; `packages/types/src/issues/activity/base.ts` Z. 84–88 |
| WM-04 | Property-Typen Text, Number, Dropdown, Boolean, Date, Member picker, Relation (Work Item/User), URL, Email, File, Release picker | Pro (mit WM-03) | Release picker setzt Releases (WM-15) voraus | fehlt | R3 `…property_type.*`; D2 Z. 212; D3 Z. 1094–1111 |
| WM-05 | Pflichtfelder (Mandatory), Default-Werte, Aktiv/Inaktiv, Optionen-Verwaltung | Pro (mit WM-03) | – | fehlt | R3 `mandate_confirmation`, `enable_disable`, `attributes.option.*` |
| WM-06 | Formula-Properties (`{Field Name}`-Syntax, `+ - * / &`, Testen, Zyklus-Erkennung) | unklar (UNVERIFIZIERT) | – | fehlt | R3 `…properties.formula.*`, `…create_update.errors.formula.*`; D2 Z. 212; D3 Z. 1111; W introducing-releases (via Dok 21 §4.18) |
| WM-07 | Workspace-Level Properties & Workspace-Level Types (zentraler Katalog, „Import from workspace“, Verknüpfen/Entknüpfen, Governance-Modus) | Business | Business/Enterprise ✓; Plane Compose: „workspace-level WIT definitions (Enterprise)“; Governance-Modus Enterprise Grid | fehlt | R1 Z. 222–223; R3 `linked_properties.*`, `types.project.*`; D2 Z. 38–42, 189; D3 Z. 1003; W workspace-governance (via Dok 25 W3/W4) |
| WM-08 | Roll-ups (Aggregation von Property-Werten über die Hierarchie) | Business | Business/Enterprise ✓ | fehlt | R1 Z. 222–223 (nur Matrix-Text) |
| WM-09 | Epics (Work Item mit Typ `is_epic`; eigene Liste, Detail, Kinder, Archiv, Cycle/Modul-Zuordnung) | Pro | Pro/Business/Enterprise ✓ | Stub/UI-Hülle im CE (umfangreiches Frontend-Plumbing, `IssueType.is_epic`, kein Backend) | R1 Z. 261–270; D1 `epics/`; D2 Z. 50–58; W docs.plane.so/work-items/epics „Pro“ (via Dok 21) |
| WM-10 | Epic-Fortschritt (Analytics je State-Gruppe, Overdue) und Epic-Updates (Status-Feed) | Pro (mit Epics) | – | Stub/UI-Hülle im CE (`TEpicAnalytics`, `EUpdateStatus`, `update.json`) | `packages/types/src/epics.ts`; `packages/types/src/enums.ts` Z. 87–91; R9 |
| WM-11 | Initiatives (Workspace-weit; Projekte/Epics/Work Items verknüpfen; State; Lead; Datum; Fortschritt) | Pro (R1, „Coming soon“) – Konflikt: Business (Plane University) | Sub-Initiativen nur Enterprise (W plane-vs-linear) | Stub/UI-Hülle im CE (Theme-Store-Flag, Asset-Typ, Slugs, Icons) | R1 Z. 272–282; D1 `initiative/`; D2 Z. 290–305; W (via Dok 21 §3 F02) |
| WM-12 | Initiative-Labels (eigener Workspace-Katalog) | wie WM-11 | – | fehlt | D1 `initiative/*label*`; Kommentar in `apps/web/components/dropdowns/label/label-select.tsx` Z. 48–49 |
| WM-13 | Initiative-/Epic-/Projekt-Updates und Checkpoints („markers … to report on progress“) | Pro („Coming soon“) | – | Stub/UI-Hülle im CE (Updates-Texte, Enum); Checkpoints fehlt | R1 Z. 284–295 (Checkpoints), Z. 354–366 (Project Updates, auskommentiert); R9 |
| WM-14 | Milestones (Projekt-Feature: Meilensteine mit Zieldatum, Work-Item-Zuordnung) | unklar | – | Stub/UI-Hülle im CE (i18n, Fetch-Key, Projekt-Overview-Sektion) | R4 `features.milestones`; `packages/constants/src/fetch-keys.ts` Z. 205–206; `apps/web/store/project/project.store.ts` Z. 21, 86; D1 `milestones/`; W v1.16.0 (via Dok 21 §4.5) |
| WM-15 | Releases (Workspace-Releases, Status, Tags, Labels, Changelog, Work-Item-Zuordnung, Release-Picker-Property) | unklar | – | fehlt (nur Icons, Illustration `changelog`, Kommentar zu Label-Scope `release`) | D2 Z. 307–356; D3 Z. 1109; R23; W introducing-releases, v2.6.0 (via Dok 21/25) |
| WM-16 | Customers (Kundenprofile, Felder Industry/Stage/Contract status/Revenue/Employees/Website/Email, Logo) | Business (Dok 21: docs.plane.so/customers, introducing-plane-business) – Konflikt: Pro „customer profiles“ (Dok 20: plane.so/pricing) | – | fehlt (nur Seed-Display-Properties `customer_count`, `customer_request_count`; Illustrationen) | D1 `customer/`; D2 Z. 463–511; `apps/api/plane/bgtasks/workspace_seed_task.py` Z. 160, 163 |
| WM-17 | Customer Requests (Anfragen je Kunde, mit Link, verknüpfte Work Items) | wie WM-16 | – | fehlt | D1 `customer/*request*`; D2 Z. 483–495 |
| WM-18 | Customer Properties (eigene Properties für Kunden, gleiche Typen wie WM-04) | wie WM-16 | – | fehlt | D1 `customer/*propert*`; D2 Z. 497–511 |
| WM-19 | Recurring Work Items | Business | Business/Enterprise ✓ | fehlt | R6 `recurring_work_items.empty_state.upgrade.description` „… Upgrade to Business …“; Detail: Dok 25 F24 |
| WM-20 | Work Item Templates (Projekt- und Workspace-Ebene, inkl. Sub-Work-Items) | Pro | Pro/Business/Enterprise ✓ | Stub/UI-Hülle im CE (Modal-Kontext `workItemTemplateId`, `handleTemplateChange`) | R1 `planHighlights.pro` „Work item templates“; R10; R16; Detail: Dok 25 F21 |
| WM-21 | Pre-defined work item Templates | Pro („Coming soon“) | Pro/Business/Enterprise | fehlt | R1 Z. 368–379; Detail: Dok 25 F23 |
| WM-22 | Bulk Ops (Mehrfachauswahl, Property-Änderung für viele Work Items) | One | One „Limited props“; Pro „All props“; Business/Enterprise zusätzlich „Work item transfers and conversions“ (Coming soon) | Stub/UI-Hülle im CE (Store `bulkUpdateProperties` + Service `bulk-operation-issues/` vorhanden, Backend-Route fehlt, Auswahl deaktiviert) | R1 Z. 162–181; R2 `PRO_PLAN_FEATURES` „Full Time Tracking + Bulk Ops“, `ONE_PLAN_FEATURES` „Time-tracking + limited bulk ops“; R18 |
| WM-23 | Work Item Transfers (Work Item in anderes Projekt oder anderen Cycle verschieben) | Pro | Pro/Business/Enterprise ✓ | teilweise im CE (nur Bulk-Transfer offener Items eines Cycles in anderen Cycle) | R1 Z. 238–247; R22; R8 `failed_to_move_issue_to_project` |
| WM-24 | Conversions (Work Item ↔ Epic; als Bulk ab Business) | Business (Bulk, Coming soon) / Einzel unklar | – | Stub/UI-Hülle im CE (`handleConvert`, Icons `ConvertToEpic*`/`ConvertToWorkItem*`) | R1 Z. 168–179; R16; R23 |
| WM-25 | Kopie eines Work Items in ein anderes Projekt („Make a copy to another project“) | unklar | – | Stub/UI-Hülle im CE (`createCopyMenuWithDuplication` gibt nur Basis-Item zurück; Modal-Texte vorhanden) | R6 `issue.duplicate.*`; `apps/web/components/issues/issue-layouts/quick-action-dropdowns/copy-menu-helper.tsx`; W v1.13.0 (via Dok 26 W38) |
| WM-26 | Dependencies in Gantt (Starts/Finishes Before/After, Verbindungslinien, abhängige Verschiebung) | Pro | Pro/Business/Enterprise ✓ | teilweise im CE (Backend speichert/liefert alle Dependency-Typen; Frontend-Typen/Optionen beschränkt; Gantt-Stubs `isDependencyEnabled=false`) | R1 Z. 227–236; R13; R14; R17; R6 `issue.relation.*` |
| WM-27 | Custom Relations (frei definierbare Relationstypen mit Outward/Inward-Label, Farbe) inkl. „Implements/Implemented by“ | unklar | – | teilweise im CE (Enum `implemented_by`/`implements` im Backend, keine UI); Definitionen fehlen | R5 `relations`; R6 Z. 197–198; D2 Z. 142–156; W custom-relations-Blog (via Dok 25 W20) |
| WM-28 | Auto-transfer Cycle Work Items (Auto-Rollover am Cycle-Ende) | Pro | Pro/Business/Enterprise ✓ | fehlt (manueller Transfer vorhanden) | R1 Z. 249–259; R4 `cycles.auto_schedule.form.auto_rollover` |
| WM-29 | Auto-schedule Cycles („recurring cycles“; Kontext von WM-28) | unklar | – | fehlt | R4 `cycles.auto_schedule.*` (Z. 442–524); W v1.16.0 „recurring cycles“ (via Dok 25 W49) |
| WM-30 | Module Overview (Übersicht mit Details und Fortschrittsdiagrammen je Modul, analog Cycle-Overview) | Pro | Pro/Business/Enterprise ✓ | teilweise im CE (Modul-Peek mit Burndown/Progress vorhanden) | R1 Z. 297–306; `apps/web/components/modules/analytics-sidebar/*` |
| WM-31 | Auto-assignment in Modules (Regeln Linear, Round Robin, Capacity) | Pro | Pro „Linear“; Business/Enterprise „Round-robin and Capacity“ | fehlt | R1 Z. 308–317 |
| WM-32 | Time Tracking + Worklogs (Zeit je Work Item loggen, Tracked time, Worklogs-Tab) | One | One „Basic“; Pro „Historical timesheets“; Business/Enterprise „Historical timesheets and approvals“ | teilweise im CE (`Project.is_time_tracking_enabled`, Export-Typ `issue_worklogs`, Activity-Typ `WORKLOG`) | R1 Z. 183–192; R12 Z. 100; D1 `worklogs/`; W time-tracking (via Dok 21 §4.6) |
| WM-33 | Timesheets / Worklog-Downloads (Workspace-Settings „Worklogs“) | Pro („Historical timesheets“) | – | fehlt | R5 `worklogs`; R7 `settings_empty_state.worklogs` |
| WM-34 | Timesheet-Approvals | Business | Business/Enterprise ✓ | fehlt | R1 Z. 189–190 (nur Matrix-Text) |
| WM-35 | Advanced Estimates (System `time`, Bearbeiten/Umsortieren/Systemwechsel) | Pro | Free/One „Basic“; Pro/Business/Enterprise „Advanced“ | teilweise im CE (points/categories vollständig; `time` als `is_ee`-Konstante; Edit/Switch nur Texte) | R1 Z. 145–154; R4 `estimates.*`; R19 |
| WM-36 | Public, Private und Secret Projects | Pro | Pro/Business/Enterprise ✓ | teilweise im CE (Netzwerk `0` „Secret“ (UI-Label „Private“) und `2` „Public“; Stufe „Private mit Beitrittsgenehmigung“ fehlt) | R1 Z. 331–341; R12 Z. 30–36, 71, 76; `packages/constants/src/project.ts` Z. 21–36 |
| WM-37 | State of Projects / Project States (Projekt-Lebenszyklus-States, Projekt-Properties, Übersicht nach States) | Pro | Pro/Business/Enterprise ✓ | fehlt | R1 Z. 343–353; R5 `project_states`, `projects`; R7 `project_overview_state_sidebar`; W project-states (via Dok 21 §4.12) |
| WM-38 | Project Labels (Workspace-Katalog für Projekt-Labels) | unklar | – | fehlt | R5 `projects.tabs.labels`; D1 `project-labels/`; W v2.5.0 (via Dok 26 W44) |
| WM-39 | Project Overview (Projekt-Übersichtsseite: Snapshot, Links, Attachments, Milestones) | Pro (Zeile auskommentiert, „Coming soon“) | – | Stub/UI-Hülle im CE (Collapsible-State im Projekt-Store, Typ `TProjectLink`, Power-K-Text) | R1 Z. 318–329; `apps/web/store/project/project.store.ts` Z. 21, 47–52, 86–87; `packages/types/src/project/project_link.ts` |
| WM-40 | Project Updates (Status-Updates On-Track/Off-Track/At-Risk mit Kommentaren/Reaktionen) | Pro (Zeile auskommentiert, „Coming soon“) | – | Stub/UI-Hülle im CE (Activity-Feld `is_project_updates_enabled`, Enum, Texte) | R1 Z. 354–366; R4 `project_updates`; R9; R21 Z. 67, 266 |
| WM-41 | Project Templates | Business | Business/Enterprise ✓ | Stub/UI-Hülle im CE (`templateId`-Props ohne Wirkung) | R1 Z. 392–401; R2 `BUSINESS_PLAN_FEATURES`; Detail: Dok 25 F20 |
| WM-42 | Baselines And Deviations | Business | Business/Enterprise ✓ | fehlt | R1 Z. 403–412 (nur Matrix-Text); R1 `planHighlights.business` (Z. 1307) |
| WM-43 | Custom SLAs (SLA-Matrizen für zeitkritische Work Items) | Business | Business/Enterprise ✓ | fehlt | R1 Z. 436–445 (nur Matrix-Text) |
| WM-44 | Intake Forms (öffentliche Formulare je Work Item Type mit gewählten Properties) | Business | Business/Enterprise ✓ | Stub/UI-Hülle im CE (`EInboxIssueSource.FORMS`, Anzeige „Intake Form user“, `DeployBoard` `intake`) | R1 Z. 447–456; R2 `BUSINESS_PLAN_FEATURES` „Intake Forms“; R4 `features.intake.form.*`; R15 |
| WM-45 | Intake Assignees / Intake responsibility (Standard-Bearbeiter für Intake, Benachrichtigung) | Business | Business/Enterprise ✓ | teilweise im CE (`Project.default_assignee` wird bei Intake-Anlage zugewiesen) | R1 Z. 425–434; R4 `features.intake.intake_responsibility`, `notify_assignee`; `apps/api/plane/app/views/intake/base.py` Z. 261–268 |
| WM-46 | Emails For Intake (Projekt-E-Mail-Adresse, E-Mail → Intake-Work-Item/Kommentar) | Business | Business/Enterprise ✓ (Matrix „Coming soon“; Doku-Badge `Business`) | Stub/UI-Hülle im CE (`IntakeIssue.source_email`, `EInboxIssueSource.EMAIL`) | R1 Z. 458–468; D6; R15; Dienst: Dok 22 §4.23 |
| WM-47 | Duplicate Detection (Duplikat-Vorschläge beim Anlegen von Work Items/Intake) | Commercial Edition (Plane AI); Plan-Tier unklar | – | Stub/UI-Hülle im CE (Typen `TDuplicateIssuePayload`/`TDeDupeIssue`, No-op-Hook, Modal-State, Texte) | R20; R16 `isDuplicateModalOpen`; R8 Z. 284–285; D7 |

**Zählung CE-Status:** fehlt (21) = WM-04, 05, 06, 07, 08, 12, 15, 16, 17, 18, 19, 21, 28, 29, 31, 33, 34, 37, 38, 42, 43 · Stub/UI-Hülle (16) = WM-03, 09, 10, 11, 13 (Updates; Checkpoints fehlen), 14, 20, 22, 24, 25, 39, 40, 41, 44, 46, 47 · teilweise (10) = WM-01, 02, 23, 26, 27, 30, 32, 35, 36, 45.

---

## 3. Feature-Abschnitte

Aufbau je Feature: **Tier** · **Funktionsbeschreibung (UI & Verhalten)** · **Datenmodell-Hinweise** · **API-Hinweise** · **UI-Hinweise (1:1)** · **CE-Status (Repo-Beleg)** · **Migrationshinweise (.NET Aspire / EF Core 10 / PostgreSQL / Angular)** · **Quellen** · **Konfidenz**. Wörtliche UI-Texte stammen aus `packages/i18n/src/locales/en/*.json` und sind 1:1 (inkl. Tippfehlern) in die Ziel-i18n zu übernehmen (ADR-005/006). Allgemeine Migrationsregel: Upsell-Elemente (`UpgradeBadge`, „Get Pro …“, „Upgrade to …“-Leerzustände, `PaidPlanUpgradeModal`, HTTP 402 bei fehlendem Plan) entfallen; an ihrer Stelle erscheint die echte Funktion (ADR-001).

### 3.0 Querschnitt (gilt für alle Features dieses Clusters)

#### 3.0.1 Projekt-Feature-Toggles

| Toggle (fachlich) | CE-Feld (`apps/api/plane/db/models/project.py` Z. 95–102) | Commercial-API `…/projects/{project_id}/features/` (D1 `project-features/overview.md`) | MCP `project update_features` (D2 Z. 377) | Plane Compose `schema/features.yaml` (D3 Z. 1245–1277) | EE-Activity-Feld (R21 Z. 67–71) | UI-Seite (R4) |
|---|---|---|---|---|---|---|
| Cycles | `cycle_view` (Default `False`) | `cycles` | `cycles` | `cycles` | – | `project_settings.features.cycles` |
| Modules | `module_view` (Default `False`) | `modules` | `modules` | `modules` | – | `project_settings.features.modules` |
| Views | `issue_views_view` (Default `False`) | `views` | `views` | `views` | – | `project_settings.features.views` |
| Pages | `page_view` (Default `True`) | `pages` | `pages` | `pages` | – | `project_settings.features.pages` |
| Intake | `intake_view` (Default `False`) | `intakes` | `intakes` | `intakes` | – | `project_settings.features.intake` |
| Time tracking | `is_time_tracking_enabled` (Default `False`) | – (nur Projekt-Feld; MCP `project update` `is_time_tracking_enabled`, D2 Z. 371) | – | – | `is_time_tracking_enabled` „enabled/disabled time tracking“ | `project_settings.features.time_tracking` |
| Work item types | `is_issue_type_enabled` (Default `False`) | `work_item_types` | `workitem_types` | `work_item_types` | `is_issue_type_enabled` „… work item types“ | `project_settings.work_item_types` |
| Epics | – (fehlt im CE) | `epics` | `epics` | `epics` („Requires at least one type with `is_epic: true`“) | `is_epic_enabled` „… epics“ | – |
| Milestones | – (fehlt im CE) | – | – | – | – | `project_settings.features.milestones` |
| Project updates | – (fehlt im CE) | – | `project_updates` | `project_updates` („Enables the project updates feed.“) | `is_project_updates_enabled` „… project updates“ | `project_settings.project_updates` |
| Workflows (Cluster P06) | – | – | `workflows` | `workflows` | `is_workflow_enabled` „… custom workflow“ | `project_settings.workflows` |
| Parallel cycles | – | – | `parallel_cycles` | `parallel_cycles` („Allows multiple active cycles to run simultaneously.“) | – | UNVERIFIZIERT |

Template-Blueprints kennen zusätzlich `is_milestone_enabled`, `is_epic_enabled`, `is_project_updates_enabled` (W `developers.plane.so/api-reference/v2/project-templates/…` via Dok 25 F20, `template_data`). Ein Toggle ist ein **fachlicher** Schalter und bleibt nach ADR-001 erhalten (vgl. `00-grundsatzentscheidungen.md`). Feature-Seiten im CE (Cycles, Modules, Views, Pages, Intake) zeigen jeweils `SettingsHeading` + `ProjectSettingsFeatureControlItem` und sind nur für Projekt-Admins (`NotAuthorizedView` sonst) (`apps/web/app/(all)/[workspaceSlug]/(settings)/settings/projects/[projectId]/features/{cycles,intake,…}/page.tsx`). EE-Feature-Seiten (Time tracking, Milestones, Project Updates) folgen demselben Muster (Titel/Beschreibung/Toggle-Texte in R4 Z. 413–436).

**Toast-Texte beim Umschalten (alle Feature-Seiten, R4 Z. 427–431):** „Updating project feature...“, „Project feature updated successfully.“, „Something went wrong while updating project feature. Please try again.“

**Edge-Case (CE-Bug, nicht übernehmen):** Die CE-Intake-Feature-Seite übergibt `featureProperty="inbox_view"`, das Modell heißt `intake_view` (`…/features/intake/page.tsx`; `apps/api/plane/db/models/project.py` Z. 99). In der Neuimplementierung einheitlich `intake_view`.

#### 3.0.2 Workspace-Feature-Toggles

Commercial-API `GET/PATCH /api/v1/workspaces/{workspace_slug}/features/` mit Objekt `{project_grouping, initiatives, teams, customers, wiki, pi}` (alle bool; D1 `workspace-features/overview.md`; Scopes `workspaces.features:read|write`). MCP `workspace update_features` mit denselben sechs Schlüsseln (D2 Z. 427–431). Relevanz für diesen Cluster: `project_grouping` (WM-37/38), `initiatives` (WM-11–13), `customers` (WM-16–18). Plane Compose zeigt zusätzlich `workspace_features: { epics: true }` als Beispiel in `workspace.yaml` (D3 Z. 1048–1072) – ein Workspace-Schalter für Epics ist sonst nirgends belegt (UNVERIFIZIERT).

#### 3.0.3 Settings-Navigation (Einordnung der EE-Seiten)

- **Projekt-Settings (CE):** Kategorien `general`, `features`, `work-structure`, `execution` mit Labels `common.general`, `common.features`, `common.work_structure`, `common.execution`; Tabs `general`, `members`, `features_cycles`, `features_modules`, `features_views`, `features_pages`, `features_intake`, `states`, `labels`, `estimates`, `automations` (`packages/constants/src/settings/project.ts`; Typ `TProjectSettingsTabs` in `packages/types/src/settings.ts` Z. 22–33). EE-Seiten dieses Clusters mit vorhandenen Labels: „Work item Types“ (`project_settings.work_item_types.heading`, Beschreibung „Create and customize different types of work items with unique properties“), „Time tracking“, „Milestones“, „Project Updates“ (`project_settings.project_updates.heading`, „Consolidated tracking and progress monitoring for this project“), „Templates“ (`project_settings.templates.heading`), „Recurring work items“ (`recurring_work_items.settings.heading`). Die genaue Kategorie-Zuordnung der EE-Tabs ist nicht belegt (UNVERIFIZIERT; Vorschlag: Time tracking/Milestones/Project Updates → `features`; Work item Types → `work-structure`; Templates/Recurring → `execution`).
- **Workspace-Settings (CE):** Kategorie `features` ist im CE **leer** (`packages/constants/src/settings/workspace.ts` Z. 78). Commercial-Screenshot (Dok 22 §3.12, Screenshot `IMG/webhooks/create-webhook.webp` der Developer-Docs): Gruppe **Features** mit „Projects, Integrations, Plane Runner, Connections, Teamspaces, Initiatives, Customers, Releases, Templates, Relations, Plane AI, Automations“. Für diesen Cluster zusätzlich belegt: „Work item Types“ (`work_item_types.label`), „Worklogs“ (`workspace_settings.settings.worklogs.title`), „Projects“ mit Tabs „Project states“/„Project labels“ (`workspace_settings.settings.projects.*`), „Relations“ (`workspace_settings.settings.relations.*`), „Templates“; Gruppenlabel „Custom properties“ (`common.custom_properties`, R8 Z. 721) und „Project structure“ (`common.project_structure`, R8 Z. 720).

#### 3.0.4 Rollen

CE-Projektrollen: `ADMIN = 20`, `MEMBER = 15`, `GUEST = 5` (`packages/types/src/project/projects.ts` `EUserProjectRoles`). Commercial-Rollen: Namespace `workspace` (Owner/Admin/Member/Guest) und `project` (Admin/Contributor/Commenter/Guest); Rollen-Slug nur mit Namespace eindeutig (D2 Z. 409–421). Feature-spezifische Rechte sind je Abschnitt angegeben; wo nicht belegt, gilt der Vorschlag: **Konfiguration** (Typen, Properties, Templates, Recurring, Intake-Formulare, Feature-Toggles) = Projekt-Admin bzw. Workspace-Admin/Owner; **Nutzung** (Werte setzen, Worklogs, Updates) = wer das Work Item bearbeiten darf (Member/Contributor). Rollenmodell-Entscheidung siehe Dok 21 §8 O15.

#### 3.0.5 Activity-Typen, Webhooks, OAuth-Scopes

| Element | Werte | Quelle |
|---|---|---|
| Activity-Typen (Frontend-Union) | `WORKLOG`, `ISSUE_ADDITIONAL_PROPERTIES_ACTIVITY` (zusätzlich zu CE-Typen) | `packages/types/src/issues/activity/base.ts` Z. 80–88 |
| Epic-Activity-Typen | `epic-comment` (statt `issue-comment`), `epic-property` (statt `issue-property`) | `apps/web/services/issue/issue_comment.service.ts` Z. 38; `apps/web/services/issue/issue_activity.service.ts` Z. 34 |
| Webhook-v2-Events des Clusters | `milestone.created/updated/deleted`; `workitem.relation.created/deleted`; `workitem.dependency.created/deleted` (getrennt von Relations!) | D4 Z. 246–274 |
| OAuth-Scopes des Clusters | `customers:read/write`, `customers.requests:*`, `customers.properties:*`, `customers.property_values:*`, `customers.work_items:*`, `initiatives:*`, `initiatives.labels:*`, `initiatives.projects:*`, `initiatives.epics:*`, `projects.epics:*`, `projects.milestones:*`, `projects.work_item_types:*`, `projects.work_item_properties:*`, `projects.work_item_property_options:*`, `projects.work_item_property_values:*`, `projects.work_items.worklogs:*`, `projects.work_items.relations:*`, `projects.features:*`, `projects.labels:*` (auch für Project Labels), `workspaces.features:*` | D5; D1 (Scope je Endpunkt, Anhang A) |
| MCP-Feature-Gates | `work_log` („Time tracking“), `workitem_type` („Work item types“), `workitem_property` („Work item properties“), einige `project`-Features; Customers, Initiatives, Releases, Pages „can also be gated by the Plane API and your plan“ | D2 Z. 60–62 |

---

### 3.1 Work Item Types und Typ-Hierarchie

#### WM-01 – Work Item Types

**Tier:** Pro, Business, Enterprise ✓; Free/One ✗ (R1 Z. 205–214 „Work item Types – Create your own work item types with your own properties.“; Highlight Pro „Custom work items + Properties“ R1 Z. 1306). Upsell-Text im CE: „Get Pro to enable Work item types.“ (`work_item_types.empty_state.get_pro.title`, R3 Z. 377–383) – entfällt. W: docs.plane.so/work-item-types (via Dok 21 §4.7).

**Funktionsbeschreibung (UI & Verhalten):**

*Workspace-Ebene* (Settings-Seite „Work item Types“, `work_item_types.label`; Beschreibung „Customize and add your own properties to tailor it to your team's needs.“, R3 Z. 3–6):
1. Abschnitt **„Types“** – „Create and customize work item types with properties.“ (R3 Z. 234–236). Sortierung „Number of projects part of“ (`types.sort_options.project_count`), Filter „Show active“ / „Show inactive“ (`types.filter_options.*`).
2. Button **„Add work item type“** (`work_item_types.create.button`) öffnet Modal **„Create work item type“** (`create.title`). Felder: Name (Placeholder „Give this work item type a unique name“), Beschreibung (Placeholder „Describe what this work item type is meant for and when it's to be used.“) (`create_update.form.*`, R3 Z. 329–337), Icon + Hintergrundfarbe (`logo_props.icon`, `logo_props.background_color` als Hex, D3 Z. 1085–1086), optional „Hierarchy level“ (WM-02). Bearbeiten: Modal „Update work item type“, Button „Update work item type“ (`update.*`).
3. Toasts: Erfolg „Work item type created successfully.“ / „Work item type {name} updated successfully.“; Fehler „Failed to create work item type. Please try again!“ bzw. Namenskonflikt „{name} type already exists. Choose a different name.“ (`create.toast.*`, `update.toast.*`) ⇒ **Name je Workspace eindeutig** (Konflikt-Antwort des Servers → HTTP 409 empfohlen).
4. **Aktiv/Inaktiv:** Toggle mit Tooltip „Click to {action}“; Lade-Toast „{action} {name} work item type“, Erfolg „Work item type {name} {action} successfully.“, Fehler „Failed to {action} work item type. Please try again!“ (`enable_disable.*`, R3 Z. 339–352). `{action}` ∈ {enable, disable} bzw. die Partizipform (UNVERIFIZIERT, Vorschlag: „Enabling“/„Disabling“ im Lade-Toast, „enabled“/„disabled“ im Erfolgs-Toast). Inaktive Typen: in Work-Item-Quick-Actions wird „Make a copy“ ausgeblendet (`shouldRender: isEditingAllowed && (issueTypeDetail?.is_active ?? true)`, `apps/web/components/issues/issue-layouts/quick-action-dropdowns/helper.tsx` Z. 219); neue Work Items können keinen inaktiven Typ wählen (Annahme, UNVERIFIZIERT).
5. **Default-Typ:** Quick Action „Set as default“ (`settings.set_as_default`). Für inaktive Typen gesperrt mit Tooltip „Activate this type before setting it as default“ (`settings.cant_set_default_inactive_message`). Bestätigung „Set as default work item type“ – „Setting {name} as the default will import it to all projects in this workspace. All new work items will use this type by default.“ – Button „Set as default“ (`settings.set_default_confirmation.*`, R3 Z. 10–14) ⇒ Setzen des Workspace-Defaults **verknüpft den Typ mit allen Projekten** (Anlage `ProjectIssueType` je Projekt) und macht ihn zum Default neuer Work Items.
6. **Löschen:** Modal „Delete this type“ – „Deletion of types may lead to loss of existing data.“ + „Do you want to disable the type instead?“ – Button „Yes, delete it“; Toasts „Work item type deleted successfully.“ / „Failed to delete work item type. Please try again!“; Server-Fehler `cannot_delete_default_work_item_type` („Cannot delete default work item type“), `cannot_delete_work_item_type_with_associated_work_items` („Cannot delete work item type with associated work items“) (`settings.item_delete_confirmation.*`, R3 Z. 274–292); Hinweis „This work item type cannot be deleted because it's set as the default for this project“ (`settings.cant_delete_default_message`) ⇒ **Löschen nur, wenn weder Default noch Work Items zugeordnet**.
7. Je Typ Unterseite **„Properties“** (WM-03) bzw. auf Workspace-Ebene **„Custom properties“** (WM-07).

*Projekt-Ebene* (Project Settings → „Work item Types“, `project_settings.work_item_types.heading`, R4 Z. 321–324):
1. Ist das Feature aus: Leerzustand „Create and customize work item types“ – „Define unique work item types for your project. Each type can have its own properties, workflows, and fields - tailored to your project and team's needs.“ – CTA „Enable“ (`settings_empty_state.work_item_types.*`, R7 Z. 229–233) bzw. „Enable Work item Types“ – „Shape work items to your work with Work item types. Customize with icons, backgrounds, and properties and configure them for this project.“ (`empty_state.enable.*`, R3 Z. 361–376).
2. **Aktivierung ist irreversibel:** Bestätigung „Once enabled, Work item Types can't be disabled.“ – „Plane's Work Item will become the default work item type for this project and will show up with its icon and background in this project.“ – Buttons „Enable“ / „Setting up“ (`empty_state.enable.confirmation.*`). Wirkung: `is_issue_type_enabled = true`; ein Standardtyp „Work Item“ (Name gemäß Text; UNVERIFIZIERT ob exakt „Work Item“) wird Default des Projekts und allen bestehenden typlosen Work Items zugeordnet (Annahme, UNVERIFIZIERT).
3. Hinzufügen-Menü **„Create new“** / **„Import from workspace“** (`types.project.add_button.*`, R3 Z. 244–248). Banner: mit Rechten „Enable work item types to import types from workspace level“, ohne Rechte „Work item types are disabled. Contact workspace admin to enable them in workspace settings.“ (`types.project.banner.*`) ⇒ Import setzt voraus, dass Typen auf Workspace-Ebene aktiviert sind (Workspace-Admin).
4. Projekt-Default: Hinweis „This work item type cannot be deleted because it's set as the default for this project“ ⇒ Default je Projekt (`ProjectIssueType.is_default`).

*Am Work Item:*
1. **Typ im Create-Modal:** Formularfeld `type_id`. Beim Projektwechsel setzt das Formular den Default-Typ des neuen Projekts, sofern noch kein Typ gewählt ist (`getIssueTypeIdOnProjectChange(projectId)`, `apps/web/components/issues/issue-modal/form.tsx` Z. 187–197; CE-Provider liefert `null`, `provider.tsx` Z. 47).
2. **Typwechsel** in Detail und Peek über den Typ-Switcher neben dem Identifier (CE-Stub `IssueTypeSwitcher` rendert nur `IssueIdentifier size="md" enableClickToCopyIdentifier`, `apps/web/components/issues/issue-type-switcher.tsx`; verwendet in `apps/web/components/issues/issue-detail/main-content.tsx` Z. 92 und `apps/web/components/issues/peek-overview/issue-detail.tsx` Z. 95). Bestätigung: „Change work item type?“ – „Changing the work item type may result in loss of custom property values that are specific to the current type. This action cannot be undone.“ – Buttons „Change type“ / „Changing“ (`change_confirmation.*`, R3 Z. 353–360) ⇒ Server löscht Werte von Properties, die am neuen Typ nicht existieren.
3. **Anzeige:** Typ-Icon vor dem Identifier (`TIssueIdentifierWithDetails.issueTypeId`, `TIssueTypeIdentifier`, `packages/types/src/issues/issue-identifier.ts`); Display-Property „Work item Type“ (`issue.display.properties.issue_type`, R6) bzw. `IIssueDisplayProperties.issue_type` (`packages/types/src/view-props.ts` Z. 177). Im List-Layout wird der Identifier-Block gerendert, wenn `displayProperties.key || displayProperties.issue_type` (`apps/web/components/issues/issue-layouts/list/block.tsx` Z. 232–242).
4. **Server-Default:** Ohne `type_id` erhält ein neues Work Item den Default-Typ des Projekts. CE-Public-API: `IssueType.objects.filter(project_issue_types__project_id=project_id, is_default=True).first()` (`apps/api/plane/api/serializers/issue.py` Z. 190–197) – **Achtung:** filtert auf `IssueType.is_default`, nicht auf `ProjectIssueType.is_default`; in der Neuimplementierung den **Projekt-Default** (`ProjectIssueType.is_default`) verwenden und fallback auf Workspace-Default.
5. **MCP-Verhalten** (D2 Z. 175–189): `resolve(project_id, name)` findet oder erzeugt einen im Projekt nutzbaren Typ, **ohne Duplikate**, exakter Namensvergleich (case-sensitive, Whitespace getrimmt); im Governance-Modus wird ein Typ nicht im Projekt angelegt, sondern der Workspace-Typ importiert. `import_to_project(project_id, workitem_type_ids)` verknüpft Workspace-Typen mit einem Projekt.
6. **Edge-Case (W, Forum via Dok 21):** „Enabling work item types via REST API silently and permanently prevents the project from ever having the native Epic type“ – Aktivierung per REST vor Anlage des Epic-Typs verhinderte die native Epic-Anlage. Neuimplementierung: Aktivierung der Typen und Epics unabhängig und idempotent gestalten (Epic-Typ jederzeit nachträglich anlegbar).

**Datenmodell-Hinweise:**
- CE: `IssueType(workspace, name ≤255, description, logo_props JSON, is_epic, is_default, is_active, level Float, external_source, external_id)`; `ProjectIssueType(project, issue_type, level PositiveInt, is_default)` mit Unique `(project, issue_type)` bei `deleted_at IS NULL`; `Issue.type` FK `SET_NULL` (R11 Z. 14–55; R13 Z. 164–170); `DraftIssue.type` (`apps/api/plane/db/models/draft.py` Z. 71–73); `Project.is_issue_type_enabled` (R12 Z. 101).
- Commercial-Objekt (D1 `issue-types/types/overview.md`, Dok 21 §4.7): `id, name*, description, logo_props, is_epic, is_default (RO), is_active, level (RO), project_ids (RO; MCP: RW), workspace, project, external_id, external_source` + Audit.
- **Vorschlag EF Core:** `WorkItemType` (Workspace-Katalog; Spalten wie CE + `logo_props jsonb`), `ProjectWorkItemType` (Link mit `is_default`, `level`), Unique-Index `(workspace_id, lower(name)) WHERE deleted_at IS NULL`; Check „höchstens ein Default je Projekt“ als partieller Unique-Index `(project_id) WHERE is_default AND deleted_at IS NULL`; dasselbe für Workspace-Default.

**API-Hinweise:** Commercial v1 (Scope `projects.work_item_types:read|write`): `GET/POST /api/v1/workspaces/{workspace_slug}/projects/{project_id}/work-item-types/`, `GET/PATCH/DELETE …/work-item-types/{type_id}/`, `GET …/work-item-types/schema/?type_id=&include=members,labels` (D1 `issue-types/types/*`). Schema-Endpunkt-Antwort `{type_id, type_name, type_description, type_logo_props, fields{…}, custom_fields{…}}` mit Standardfeldern `name`, `description_html`, `priority`, `state_id`, `assignee_ids`, `label_ids`, `start_date`, `target_date`, `parent_id`, `estimate_point_id` und Custom-Feldern `custom_field_<name>` (Details Dok 21 §4.7). Workspace-Scope: MCP ohne `project_id` (D2 Z. 181–187) – REST-Pfad dafür nicht dokumentiert (Vorschlag `…/workspaces/{slug}/work-item-types/`). Intern (Web-App) sind die Pfade nicht belegt (UNVERIFIZIERT; Vorschlag analog `/api/workspaces/{slug}/issue-types/`, `/api/workspaces/{slug}/projects/{pid}/issue-types/`).

**UI-Hinweise:** Icons: `WorkItemsOutline/Filled` (project-features), `PropertiesOutline/Filled` (properties), `HierarchyOutline/Filled` (miscellaneous); Projekt-Activity-Icon für `is_issue_type_enabled` = `ToDoOutline` (R21 Z. 71). Illustrationen `custom-properties` (horizontal-stack), `property` (vertical-stack) (R24). Typ-Icon-Picker: Plane-Logo-Picker (`logo_props`) wie bei Projekten.

**Referenz-Screenshots (D, ältere UI-Generation mit den Begriffen „Issue“/„Issue Types“; nur Struktur-/Verhaltensreferenz, Gestaltung folgt dem aktuellen CE-Design und den i18n-Texten oben):** `/home/user/makeplane/developer-docs/docs/public/images/issues/{setup-issue-types,enable-issue-types,add-issue-type,create-issue-type,activate-issue-type,add-new-property,property-details,use-issue-type}.webp` (in keiner `.md` referenziert, aber Teil der offiziellen Developer-Docs). Belegt: (1) Projekt-Settings-Eintrag „Issue Types“ als letzter Tab nach „Automations“; (2) Aktivierungsseite mit Titel „Enable Issue Types“, Beschreibung, Vorschaubild und Button „Enable“; (3) Typenliste als Akkordeon: Zeile mit Chevron, quadratischem farbigem Typ-Icon (Icon auf farbigem Hintergrund), Name, Beschreibung, rechts Badge „Default“ (Default-Typ, ohne Toggle) bzw. Edit-Stift + Aktiv-Toggle; inaktive Typen tragen ein graues Badge „Disabled“ hinter dem Namen; Seitentitel mit primärem Button „Add issue type“ oben rechts; (4) Default-Typ „Issue“ mit Beschreibung „Default issue type with the option to add new properties“; Beispieltypen „Feature“ („Track new feature requests.“), „Story“ („A user story is the smallest unit of work that needs to be done.“), „Task“ („A task represents work that needs to be done.“), „Bug“ („A bug is a problem which impairs or prevents the functions of a product.“); (5) Modal „Create Issue type“: links Icon-Picker-Kachel, rechts Namensfeld, darunter mehrzeilige Beschreibung, Buttons „Cancel“ / „Create Issue type“; (6) im Create-Work-Item-Modal ein Typ-Dropdown direkt rechts neben dem Projekt-Chip (Breadcrumb „Projekt › Typ“) mit Suchfeld und Häkchen am gewählten Typ; die Custom Properties des Typs erscheinen **als Formularzeilen zwischen Beschreibung und der Standard-Property-Leiste** (links Icon + Name, Pflichtfelder mit rotem `*`, rechts Eingabe mit Placeholdern „Add text“, „Choose date“, „Select an option“, „Select a member“).

**CE-Status:** teilweise im CE – Modelle/Felder/Serialisierung `type_id` vorhanden (u. a. `apps/api/plane/app/serializers/draft.py` Z. 359, `apps/api/plane/app/views/search/base.py` Z. 446/658), keine Endpunkte, keine Settings-Seiten, Switcher ist Stub.

**Migrationshinweise:** Typ-Verwaltung als eigenes Bounded Context „WorkItemTypes“ (gemeinsam mit Properties, WM-03). Irreversibilität der Projekt-Aktivierung serverseitig erzwingen (PATCH `is_issue_type_enabled=false` → 400). Default-Wechsel transaktional (alter Default `is_default=false`, neuer `true`).

**Quellen:** R1, R3, R4, R7, R11, R12, R13, R16, R21; D1, D2, D3; W (via Dok 21 §4.7).
**Konfidenz:** hoch (UI-Texte, Modell, API) / mittel (Aktivierungs-Nebenwirkungen, Default-Typname).

#### WM-02 – Work-Item-Type-Hierarchie

**Tier:** nicht in R1; laut Changelog 31.05.2026 „Eltern-Kind-Beziehungen zwischen Typen auf Workspace-Ebene“ (W via Dok 21 §4.1). Planstufe UNVERIFIZIERT (Workspace-Ebene → mindestens Business, vgl. WM-07).

**Funktionsbeschreibung (R3 `work_item_type_hierarchy.*`, Z. 393–474):**
1. Workspace-Settings-Tab **„Hierarchy“** (Titel/Tab/Sidebar-Label „Hierarchy“), Beschreibung „Set up hierarchy levels to organize your work. Each level defines a parent relationship with the item directly above it and child relationship with the item directly below it. “ (mit abschließendem Leerzeichen im Original).
2. Schalter **„Enable hierarchy“** – „Create parent-child relationships between different work item types.“, Tooltip „You cannot disable hierarchy once it is enabled.“ ⇒ **irreversibel**.
3. Banner, wenn Typen auf Workspace-Ebene nicht aktiv: „Define Work Item Types first to create a new hierarchy.“ mit CTA „Work item types settings“.
4. **Level-Editor (Drag & Drop):** Platzhalter „Drag and drop type to add a new hierarchy level“ (neue unterste Ebene), „Drag and drop a work item type to level {level}“ (leere Ebene), Tooltip „Drag to change level“. Verschieben: Toast „Moving {workItemTypeName} to level {level}...“ → „{workItemTypeName} moved to level {level} successfully.“. Quick Action je Level „Set as default“ – Toasts „Setting as default...“, „Hierarchy level {level} set as default successfully.“, Fehler „Failed to set hierarchy level {level} as default. Please try again.“ (Bedeutung „Default-Level“: Level, auf dem neue Work Items ohne Typwahl entstehen – UNVERIFIZIERT).
5. **Bruch-Validierung:** Würde eine Level-Änderung bestehende Eltern-/Kind-Beziehungen verletzen, erscheint Modal „Validation error!“: „Work item type {workItemTypeName} has:“ + „{count} parent work item(s)“ und/oder „{count} sub-work item(s)“ (ICU-Plural `{count, plural, one {parent work item} other {parent work items}}`, Trenner „, and “), Fußtext „This change will remove parent and child relationships from existing work items of {workItemTypeName} work item type.“; Bestätigung durch Eingabe „Confirm“ (Label „Type in "Confirm" to continue.“, Placeholder „Confirm“), Button „Apply & Unlink“ / „Applying“; Fehler-Toast „Failed to break hierarchy. Please try again.“ ⇒ Server entfernt `parent_id` der betroffenen Work Items.
6. **Durchsetzung:** Im Work-Item-Modal Fehler „The selected work item type cannot be used to create a new work item since it breaks the hierarchy rules.“ (Create) bzw. „Work item type cannot be updated since it breaks the hierarchy rules.“ (Update); im Typ-Modal Feld „Hierarchy level“ mit Fehler „Work item type cannot be updated since it breaks the hierarchy rules.“ ⇒ Regel: Ein Parent muss genau eine Ebene über dem Kind liegen („directly above it“). Epic-Kinder werden beim Hinzufügen gegen die Typ-Hierarchie validiert (D1 `epics/add-epic-work-items.md`: „Validates type hierarchy before assignment.“).

**Datenmodell-Hinweise:** CE-Trägerfelder `IssueType.level` (Float, Default 0) und `ProjectIssueType.level` (PositiveInt, Default 0) (R11 Z. 22, 37). Vorschlag: Workspace-Einstellung `hierarchy_enabled` (bool, irreversibel), `default_level` (int); Level je Typ auf Workspace-Ebene; Validierung im Domain-Service `WorkItemHierarchyPolicy` bei `parent_id`-Änderung, Typwechsel und Level-Änderung.

**API-Hinweise:** nicht dokumentiert. Vorschlag: `PATCH /api/workspaces/{slug}/work-item-types/{id}/` mit `level`; Dry-Run-Endpunkt liefert `{parent_count, child_count}` für das Bruch-Modal; Ausführen mit `force=true` entkoppelt.

**UI-Hinweise:** Icon `HierarchyOutline/Filled` (R23 miscellaneous); Drag-&-Drop analog Kanban (CE nutzt `@atlaskit/pragmatic-drag-and-drop`, siehe Frontend-Analyse 08).

**CE-Status:** teilweise (nur `level`-Felder). **Quellen:** R3, R11, D1. **Konfidenz:** mittel.

---

### 3.2 Custom Properties

#### WM-03 – Custom Properties (Projekt-Ebene) – Property-Engine

**Tier:** Pro „Project-level custom properties“; Business/Enterprise „Workspace-level properties and roll-ups“ (R1 Z. 216–225). Importer „With custom props“ ab Pro (R1 Z. 940–960).

**Funktionsbeschreibung (UI & Verhalten):**
1. Je Work Item Type Abschnitt **„Properties“** – „Create and customize properties.“ mit Info-Tooltip „Each work item type comes with a default set of properties like Title, Description, Assignee, State, Priority, Start date, Due date, Module, Cycle etc. You can also customize and add your own properties to tailor it to your team's needs.“ (`work_item_types.settings.properties.*`, R3 Z. 15–19).
2. Button **„Add new property“**; auf Projektebene zusätzlich **„Import from workspace“** (`properties.project.add_button.import_from_workspace`, R3 Z. 20–24). Leerzustand der Liste: „Add custom properties“ – „New properties you add for this work item type will show here.“ (R3 Z. 229–232); Settings-Leerzustand „Define the property and details you want to capture for this work item type. Customize it to match your project's workflow.“ mit CTA „Add property“ (`settings_empty_state.work_item_type_properties.*`, R7 Z. 234–236).
3. **Formular** „Create new custom property“ / „Update custom property“ (R3 Z. 156–187): Titel (Placeholder „Title“; Pflicht „You must name your property.“; „Property name should not exceed 255 characters.“), Beschreibung (Placeholder „Description“), Dropdown **„Property type“** (Placeholder „Select type“; Pflicht „You must select a property type.“), typabhängige **„Attributes“** (WM-04), Optionen (Pflicht bei Dropdown: „You must add at least one option.“), Schalter **„Mandatory property“** (WM-05), Schalter **„Active“** (WM-05).
4. Toasts: „Property {name} created successfully.“ / „Failed to create property. Please try again!“; „Property {name} updated successfully.“ / „Failed to update property. Please try again!“; „Property {name} deleted successfully.“ / „Failed to delete property. Please try again!“; Aktiv/Inaktiv: Laden „{action} {name} property“, Erfolg „Property {name} {action} successfully.“, Fehler „Failed to {action} property. Please try again!“ (Titel jeweils „Success!“/„Error!“) (R3 Z. 113–155).
5. **Löschen:** „Delete this property“ – „Deletion of properties may lead to loss of existing data.“ + „Do you want to disable the property instead?“ – Buttons „{action}, delete it“ und „Yes, disable it“ (R3 Z. 213–219).
6. **Werte am Work Item:**
   - *Create-/Edit-Modal:* Die aktiven Properties des gewählten Typs werden zusätzlich zu den Standardfeldern angezeigt. Vor dem Absenden ruft das Formular `handlePropertyValuesValidation({projectId, workspaceSlug, watch})` auf; bei `false` wird **nicht** gespeichert (Pflichtfelder, WM-05) (`form.tsx` Z. 222–230). Nach erfolgreichem Create/Update speichert `handleCreateUpdatePropertyValues({issueId, projectId, workspaceSlug, issueTypeId, isDraft})` die Werte (`apps/web/components/issues/issue-modal/base.tsx` Z. 222–228, 334–340; Drafts `draft-issue-layout.tsx` Z. 107–112; „Move to project“ aus Drafts `form.tsx` Z. 271–282). Zustand im Kontext: `issuePropertyValues: Record<string, unknown>`, `issuePropertyValueErrors: Record<string, unknown>` (`packages/types/src/issues/issue-property-values.ts`), `getActiveAdditionalPropertiesLength({projectId, workspaceSlug, watch})` (Anzahl aktiver Zusatz-Properties; im CE-Formular ungenutzt → steuert in EE das Layout, z. B. Breite/zweite Spalte des Modals, UNVERIFIZIERT), `handleProjectEntitiesFetch({workItemProjectId, workItemTypeId, workspaceSlug})` (lädt Typen/Properties/Optionen des Projekts) (R16).
   - *Detail/Peek:* `useWorkItemProperties(projectId, workspaceSlug, workItemId, issueServiceType)` lädt Properties und Werte (CE-Stub `apps/web/hooks/use-issue-properties.tsx`, aufgerufen in `apps/web/components/issues/peek-overview/root.tsx` Z. 53); Workspace-weit `useWorkspaceIssuePropertiesExtended(workspaceSlug)` (CE-Stub `apps/web/hooks/use-workspace-issue-properties-extended.tsx`, aufgerufen in `apps/web/hooks/use-workspace-issue-properties.ts` Z. 55). Darstellung als zusätzliche Zeilen in der Property-Sidebar unter den Standard-Properties (UNVERIFIZIERT – Referenz-Screenshots nötig, Kap. 4).
   - Jede Wertänderung erzeugt Activity `ISSUE_ADDITIONAL_PROPERTIES_ACTIVITY` (`packages/types/src/issues/activity/base.ts` Z. 84–88).
   - Fetch-Key `WORK_ITEM_TYPES_PROPERTIES_AND_OPTIONS(projectId, projectRole)` bzw. für Epics `EPICS_PROPERTIES_AND_OPTIONS` (`packages/constants/src/fetch-keys.ts` Z. 199–203).
7. **Filter/Suche:** PQL-Bedingung `cf["<property id>"]`; bei OPTION ist der Wert die Option-ID (D2 Z. 212). Dashboards können Custom Properties auswerten (W changelog 2026-10-15 „dashboard custom properties“, via Dok 26 W8; Detail UNVERIFIZIERT).
8. **Typwechsel** löscht typfremde Werte (WM-01).

**Datenmodell-Hinweise (Commercial, D1 `issue-types/properties|options|values`, D2 Z. 191–212):**

| Entität | Felder | Regeln |
|---|---|---|
| Property | `id`, `name` (RO, Slug aus `display_name`), `display_name`* (≤255), `description`, `logo_props`, `sort_order`, `property_type`* ∈ {`TEXT`,`DATETIME`,`DECIMAL`,`BOOLEAN`,`OPTION`,`RELATION`,`URL`,`EMAIL`,`FILE`,`FORMULA`}, `relation_type` ∈ {`ISSUE`,`USER`,`RELEASE`,`RICH_TEXT`} (nur bei RELATION; REST-Doku nennt nur ISSUE/USER), `is_required`, `is_multi`, `is_active`, `default_value` (Array von Strings), `settings` (Objekt, u. a. `display_format`), `validation_rules` (Objekt), `formula_config` (String, nur FORMULA), `issue_type` (RO), `workspace`, `project`, `external_id`, `external_source`, Audit, `deleted_at` | `display_format` Pflicht bei TEXT und DATETIME (D2 Z. 212) |
| Option | `id`, `name`* (eindeutig je Property: „Option with same name already exists.“), `description`, `color` (MCP), `sort_order` (Beispiel 10000.0), `logo_props`, `is_active`, `is_default`, `parent` (uuid/null → hierarchische Optionen), `property`, `external_*`, `workspace`, `project`, Audit | Pflicht-Name „Option name is required.“ (R3 Z. 94–99) |
| Value | `id`, `property_id`, `issue_id`, `value` (typabhängig), `value_type`, `external_*`, `created_at`, `updated_at` | eine Zeile je (Work Item, Property), bei `is_multi` mehrere; POST = Upsert (Multi: ersetzt alle), DELETE entfernt alle (D1 `values/*`; D2 Z. 209–212) |
| Typ↔Property-Zuordnung | MCP `manage_type_properties(attach_ids, detach_ids)`; Detach entfernt nur die Zuordnung, nicht die Property (D2 Z. 202) | ⇒ n:m-Zuordnung (Workspace-Katalog) |

Wert-Kodierung (D2 Z. 212): TEXT/URL/EMAIL/FILE → String; DATETIME → `YYYY-MM-DD` oder `YYYY-MM-DD HH:MM:SS`; DECIMAL → Zahl; BOOLEAN → `true|false`; OPTION/RELATION → ID-String oder Array (bei Multi). „Send the value's own type, not a stringified form: "007" stays the text 007, whereas 7 is the number.“

**Vorschlag EF Core (gemeinsame Engine für Work Items und Customers, WM-18):** Tabellen `custom_property` (Owner-Kind `work_item|customer`, Scope `workspace_id`, optional `project_id`), `custom_property_option` (selbstreferenzierend `parent_id`), `work_item_type_property` (n:m, `sort_order`), `custom_property_value` mit typisierten Spalten `value_text`, `value_number numeric`, `value_bool`, `value_date timestamptz`, `value_ref_id uuid` (Option/User/Work Item/Release) und Unique `(entity_id, property_id)` für Single-Werte bzw. `(entity_id, property_id, value_ref_id)` für Multi; Indizes für PQL-Filter `(property_id, value_ref_id)`, `(property_id, value_number)`, `(property_id, value_date)`; GIN-Trigram auf `value_text` für Suche. Formeln (WM-06) werden nicht gespeichert, sondern berechnet (oder als materialisierte Spalte mit Neuberechnung bei Änderung referenzierter Werte).

**API-Hinweise (Commercial v1, Anhang A.1):** Properties `GET/POST …/projects/{project_id}/work-item-types/{type_id}/work-item-properties/`, `GET/PATCH/DELETE …/work-item-properties/{property_id}/` (Scope `projects.work_item_properties:*`); Optionen `GET/POST …/projects/{project_id}/work-item-properties/{property_id}/options/`, `GET/PATCH/DELETE …/options/{option_id}/` (Scope `projects.work_item_property_options:*`); Werte `GET/POST/PATCH/DELETE …/projects/{project_id}/work-items/{work_item_id}/work-item-properties/{property_id}/values/` (Scope `projects.work_item_property_values:*`). Doku-Fehler: curl sendet `name` statt `display_name`; „Values Object“-Beispiel zeigt ein Option-Objekt (Dok 21 §1.3 D8/D9). Listen ohne Envelope (Arrays). Plan-Gate HTTP 402 entfällt.

**Referenz-Screenshot Property-Tabelle (D `…/images/issues/property-details.webp`, ältere UI-Generation):** Unter dem aufgeklappten Typ eine Karte „Properties“ mit Tabelle **Name | Type | Attributes | Mandatory | Active**; je Zeile Typ-Icon + Name, Typ-Label („Text“, „Date“, „Dropdown“, „Member picker“), Attribut-Chip („Single line“, „Paragraph“, „Single select“, bei Date das Default-Datum „Aug 22, 2024“), Checkbox „Mandatory“, Toggle „Active“; **Inline-Bearbeitung** einer Zeile mit drei Dropdowns (Name/Typ/Attribut), Bestätigen über grünes Häkchen (Tooltip „Confirm“) oder rotes ✕; Fußzeile mit Button „+ Add new property“; Leerzustand mit Stapel-Illustration und „New properties you add for this issue type will show here.“ Die aktuelle Fassung verwendet ein Formular „Create new custom property“ (R3) – ob inline oder als Modal, ist für die aktuelle Generation UNVERIFIZIERT (O-04).

**UI-Hinweise:** Property-Typ-Icons (R23): Text `TextOutline/Filled` (formatting-and-editors), Number `HashOutline/Filled` (properties), Dropdown `DropdownOutline/Filled`, Boolean `BooleanOutline`, Date `CalendarOutline/Filled` bzw. `StartDateOutline`/`DueDateOutline` (Zuordnung UNVERIFIZIERT), Member picker `MembersOutline/Filled`, Formula `FormulaOutline/Filled`, Relation `RelationsOutline/Filled`, Release picker `ReleaseTagOutline/Filled`, URL `LinkOutline/Filled` (actions), Email `MailOutline`, File `AttachOutline`/`FileOutline` (Zuordnung UNVERIFIZIERT). Mehrfachauswahl-Platzhalter „Select options“ / „{count} options selected“, Einzel „Select option“ (R3 Z. 102–110).

**CE-Status:** Stub/UI-Hülle – Kontext-/Hook-Signaturen und Activity-Typ vorhanden; keine Tabellen, Endpunkte, Komponenten.

**Quellen:** R1, R3, R7, R16, D1, D2, D3; W (via Dok 26 W8). **Konfidenz:** hoch (Texte, Felder) / mittel (Layout im Modal/Sidebar).

#### WM-04 – Property-Typen (vollständiges Inventar)

| UI-Typ (R3 `property_type.*`) | API `property_type` / `relation_type` (D2 Z. 212) | Compose-Typ (D3 Z. 1094–1111) | Attribute/Settings (R3 `attributes.*`, D2) | Wert-Format | Pflichtfeld-fähig |
|---|---|---|---|---|---|
| **Text** | `TEXT` | `text` (Alias `string`) | `display_format` ∈ `single-line` („Single line“), `multi-line` („Paragraph“), `readonly` („Read only“; Kopf „Read only data“) – Fehler „Invalid text format“ | String | ja; bei `readonly` vermutlich nein (UNVERIFIZIERT) |
| **Number** | `DECIMAL` | `number` (Integer) bzw. `decimal` (Gleitkomma) | Default-Wert-Feld Placeholder „Add number“ | Zahl | ja |
| **Dropdown** | `OPTION` (+ `is_multi`) | `option` (Alias `enum`; `options`-Liste, `is_multi`) | „Single select“ / „Multi select“; Optionen „Options“ (Placeholder „Add option“); Default „No default value“ oder Option mit `is_default` | Option-ID bzw. Array | ja |
| **Boolean** | `BOOLEAN` | `boolean` | „True | False“; Default „No default value“ | `true`/`false` | Tooltip „This property type cannot be made mandatory“ ist für mindestens einen Typ aktiv – vermutlich Boolean (UNVERIFIZIERT) |
| **Date** | `DATETIME` | `date` (`YYYY-MM-DD`) bzw. `datetime` (ISO 8601) | `display_format` ∈ `MMM dd, yyyy`, `dd/MM/yyyy`, `MM/dd/yyyy`, `yyyy/MM/dd` | `YYYY-MM-DD` bzw. `YYYY-MM-DD HH:MM:SS` | ja |
| **Member picker** | `RELATION` + `USER` | `member_picker` bzw. `relation` + `relation_type: user` | „Single select“ / „Multi select“, „No default value“ | User-ID bzw. Array | ja |
| Relation (Work Item) | `RELATION` + `ISSUE` | `relation` + `relation_type: issue` | Single/Multi | Work-Item-ID bzw. Array | ja (UNVERIFIZIERT) |
| Release picker | `RELATION` + `RELEASE` | `release_picker` („Reference to a Plane release tag. Populated on pull; push is blocked by the Plane API.“) | Single/Multi (UNVERIFIZIERT) | Release-ID (MCP) bzw. Release-Tag (Compose) – widersprüchlich, UNVERIFIZIERT | UNVERIFIZIERT |
| URL | `URL` | `url` („URL string with validation“) | – | String (validierte URL) | ja (UNVERIFIZIERT) |
| Email | `EMAIL` | `email` („Email address string with validation“) | – | String (validierte E-Mail) | ja (UNVERIFIZIERT) |
| File | `FILE` | `file` („File attachment reference“) | – | String (Asset-Referenz) | UNVERIFIZIERT |
| **Formula** | `FORMULA` + `formula_config` | `formula` („Computed value derived from other fields. Push not yet supported.“) | siehe WM-06 | berechnet (RO) | nein (Annahme) |
| (Rich Text) | `RELATION` + `RICH_TEXT` | – | nur in MCP-Enum genannt; Bedeutung unklar | UNVERIFIZIERT | UNVERIFIZIERT |

**Hinweise:** Im CE-i18n existieren UI-Labels nur für die sieben fett gesetzten Typen (R3 Z. 29–51). Für Relation (Work Item), Release picker, URL, Email, File fehlen Texte → Labels aus Referenz-Screenshots ergänzen (Kap. 4, O-04); Release-Picker-Name „Release picker“ ist via Blog belegt (W introducing-releases, via Dok 21 §4.18). **Konfidenz:** hoch (API-Enums), mittel (UI-Zuordnung).

#### WM-05 – Pflichtfelder, Default-Werte, Aktiv/Inaktiv

**Funktionsbeschreibung:**
- **Mandatory:** Checkbox „Mandatory property“ mit Tooltips „Check to mark the field as mandatory“ / „Uncheck to mark the field as optional“; bei nicht unterstütztem Typ deaktiviert mit „This property type cannot be made mandatory“. Hat die Property einen Default-Wert, erscheint beim Aktivieren der Hinweis „There seems to be a default option for this property. Making the property mandatory will remove the default value and the users will have to add a value of their choice.“ ⇒ **Pflicht und Default schließen sich aus**; Server entfernt `default_value` beim Setzen von `is_required=true` (R3 Z. 220–228).
- **Durchsetzung:** (a) Client im Work-Item-Modal vor dem Absenden (`handlePropertyValuesValidation`, `form.tsx` Z. 222–230); (b) laut Plane Compose: „When `true`, the property must have a value before a work item of this type can be marked as done.“ (D3 Z. 1090) ⇒ Server verweigert den Wechsel in einen State der Gruppe `completed`, solange Pflicht-Properties leer sind. Beide Regeln umsetzen; ob (b) zusätzlich das Anlegen ohne Wert blockiert, ist UNVERIFIZIERT (Vorschlag: Server prüft bei Create/Update nur, wenn der Client alle Properties mitsendet; Pflicht-Prüfung hart beim Abschluss).
- **Default-Werte:** `default_value` (String-Array); Dropdown über `is_default` an Optionen; Number über Feld „Add number“; Boolean/Relation „No default value“ als explizite Auswahl. Default wird beim Anlegen eines Work Items des Typs vorbelegt.
- **Aktiv/Inaktiv:** Schalter „Active“ mit Tooltips „Click to disable“ / „Click to enable“ (R3 Z. 206–212). Inaktive Properties erscheinen nicht in Formularen/Detail (Annahme), Werte bleiben erhalten (Löschdialog bietet Deaktivieren als verlustfreie Alternative).

**Quellen:** R3, R16, D3. **Konfidenz:** hoch (Texte) / mittel (Server-Durchsetzung).

#### WM-06 – Formula-Properties

**Tier:** UNVERIFIZIERT (Typ in MCP/Compose ohne Plan-Angabe; Blog „Introducing Releases“ nennt die Property-Typen „Release picker“ und „Formula“, via Dok 21 §4.18). Nicht verwechseln mit „Databases + Formulas“ in Pages (Business/Enterprise, R1 Z. 909–920; Dok 26).

**Funktionsbeschreibung (R3 Z. 180–205):**
1. Feld **„Formula field“**, Placeholder „Write the formula“, Tooltip „Enter a formula using '{'Field Name'}' syntax. Supports +, -, *, /, & operators.“ (im ICU-Escaping steht `'{'Field Name'}'` für die wörtliche Ausgabe `{Field Name}`).
2. **Property-Picker** beim Tippen (Autovervollständigung von Feldnamen) mit Leerzuständen „No matching properties“ / „No available properties“.
3. Button **„Test“** (Ladezustand „Validating“) validiert serverseitig: Erfolg „Formula is valid! Returns {resultType}“ bzw. „Formula is valid! Returns {resultType} ({count} field(s) referenced)“; Fehler „Please enter a formula“, „Missing workspace, project, or work item type context“, „Validation failed“.
4. Speichern-Validierung: „Formula expression is required.“, „Invalid formula: {error}“, „Circular reference detected. A formula cannot reference itself directly or indirectly.“, „Formula references non-existent property.“
5. Werte sind berechnet und nicht editierbar; Compose: „Push not yet supported“ (D3 Z. 1111).

**Grammatik-Vorschlag (clean-room, aus belegten Elementen):** `expr := term (('+'|'-'|'&') term)*`, `term := factor (('*'|'/') factor)*`, `factor := NUMBER | STRING | '{' NAME '}' | '(' expr ')'`; `&` = Text-Verkettung; Referenzen auf Properties desselben Typs über `display_name`; Ergebnis-Typ `number` oder `text` (`{resultType}`); Division durch 0 → leerer Wert; leere Referenzen → 0 bzw. "" (UNVERIFIZIERT, Rückfrage O-06). Zyklus-Erkennung über Abhängigkeitsgraph (DFS) beim Speichern. Ob Standardfelder (z. B. Estimate) referenzierbar sind, ist UNVERIFIZIERT.

**Datenmodell:** `formula_config` (String) an der Property (D1 `issue-types/properties/add-property.md`). **Migration:** Parser/Evaluator in C# (eigener Recursive-Descent-Parser; keine Fremd-Skript-Engine wegen Sicherheit); Neuberechnung bei Wertänderung referenzierter Properties (Domain-Event). **Konfidenz:** mittel (Texte) / niedrig (Semantik).

#### WM-07 – Workspace-Level Properties & Workspace-Level Types (inkl. Governance)

**Tier:** Business/Enterprise „Workspace-level properties and roll-ups“ (R1 Z. 222–223); Plane Compose kennzeichnet `schema/workitem_types.yaml` als „workspace-level WIT definitions (Enterprise)“ (D3 Z. 1003); zentrale Governance des Typ-/Property-Vokabulars = Enterprise Grid (W docs.plane.so/workspace-administration/workspace-governance, via Dok 25 W3/W4).

**Funktionsbeschreibung:**
1. Workspace-Katalog von Properties; je Typ Abschnitt **„Custom properties“** mit Button **„Add properties“** → Modal **„Add properties“** (Mehrfachauswahl aus dem Katalog), Leerzustand „No properties available“ – „All properties have already been linked to this type.“ (`linked_properties.*`, R3 Z. 255–264).
2. **Unlink:** Modal „Unlink property“ – „Unlinking this property will permanently delete all its values across every work item using this type. This action cannot be undone.“ – Eingabebestätigung „Type“ + `{Property-Name}` + „to continue:“ – Button „Unlink property“ / „Unlinking“ (R3 Z. 265–272) ⇒ Unlink löscht **alle Werte** dieser Property an Work Items dieses Typs (MCP-`detach` lässt die Property selbst bestehen, D2 Z. 202).
3. Projekt-Ebene: „Import from workspace“ für Typen und Properties (R3 Z. 20–24, 244–248).
4. **Governance-Modus** (D2 Z. 38–42, 189): Der Workspace besitzt das Vokabular; projektbezogene Writes werden abgelehnt; Typen werden nur importiert (`import_to_project`); Properties werden mit `workitem_type_id` ohne `project_id` im Workspace-Katalog angelegt und automatisch zugeordnet. Listenauflösung `workitem_property list`: `project_id`+`workitem_type_id` → typbezogen (Fallback projektflach, dann Workspace); nur `project_id` → alle Projekt-Properties; ohne IDs → alle Workspace-Properties (D2 Z. 212).
5. Display-Name einer Workspace-Property ist **workspaceweit eindeutig** (bei Customer-Properties belegt, D2 Z. 511; für Work-Item-Properties analog anzunehmen).

**Datenmodell:** `custom_property.project_id` nullable (NULL = Workspace-Katalog); Zuordnungstabelle Typ↔Property; Workspace-Einstellung `type_governance_mode` (Werte UNVERIFIZIERT; Dok 25 F07 beschreibt Modi any/constrained/required für Workflows). **CE-Status:** fehlt. **Quellen:** R1, R3, D2, D3; W (via Dok 25). **Konfidenz:** mittel.

#### WM-08 – Roll-ups

**Tier:** Business/Enterprise (R1 Z. 222–223). **Funktionsbeschreibung:** Nur Matrix-Text „Workspace-level properties and roll-ups“. Keine weiteren Belege im Repo, in D1–D7 oder in den Web-Zusammenfassungen der Schwesterdokumente. **Vorschlag (UNVERIFIZIERT, Rückfrage O-07):** Roll-up-Property an Eltern-Typen (Epic, Initiative, höhere Hierarchie-Level), die Werte einer Property der Kinder aggregiert (Funktionen Sum, Avg, Min, Max, Count, Count-not-empty; Filter auf State-Gruppe), read-only, Neuberechnung bei Kind-Änderung. **CE-Status:** fehlt. **Konfidenz:** niedrig.

---

### 3.3 Epics

#### WM-09 – Epics

**Tier:** Pro, Business, Enterprise ✓ (R1 Z. 261–270 „Organize long-term work in epics that house work items, cycles, and modules.“); W docs.plane.so/work-items/epics mit Label „Pro“ (via Dok 21 §3 F01).

**Funktionsbeschreibung (UI & Verhalten):**
1. **Modell:** Ein Epic ist ein Work Item, dessen Work Item Type `is_epic = true` hat; keine eigene Tabelle (D1 `epics/overview.md`: Feld `type` = ID des Work-Item-Typs; D2 Z. 50–58: „Plane represents an epic as a work item whose type is named **Epic**. There is no separate epic tool.“; R11 Z. 19).
2. **Aktivierung:** Projekt-Feature `epics` (D1 `project-features`; Compose: „Enables work item hierarchy. Requires at least one type with `is_epic: true`“, D3 Z. 1245–1277); Projekt-Activity „enabled/disabled epics“ (`is_epic_enabled`, R21 Z. 68, 270–273).
3. **Navigation & Seiten:** Projekt-Navigationseintrag „Epics“ (`sidebar.epics`, `packages/i18n/src/locales/en/navigation.json`; Aktiv-Logik für `item.key === "epics"` bereits im CE: `apps/web/components/workspace/sidebar/project-navigation.tsx` Z. 167–172, `apps/web/components/navigation/use-active-tab.ts` Z. 24–33) mit Liste unter `/{workspaceSlug}/projects/{projectId}/epics` (Redirect-Ziel nach Löschen eines Epics, `apps/web/components/modals/work-item-level.tsx` Z. 60–62). Detailansicht über das Work-Item-Linkschema `/{workspaceSlug}/browse/{IDENTIFIER}-{SEQUENCE}/` (`packages/utils/src/work-item/base.ts` Z. 333–336). Layouts: List, Kanban, Calendar, Gantt (`EGanttBlockType.EPIC = "epic"`, `packages/types/src/layout/gantt.ts` Z. 8), Spreadsheet (Spaltenkopf „Epics“ statt „Work items“, `apps/web/components/issues/issue-layouts/spreadsheet/spreadsheet-header.tsx` Z. 74). Eigene Display-Filter je Nutzer (`GET/PATCH /api/workspaces/{slug}/projects/{pid}/epics-user-properties/`, `apps/web/services/issue_filter.service.ts` Z. 37–50).
4. **Anlegen:** Modal `CreateUpdateEpicModal` (CE-Stub, Props `data, isOpen, onClose, beforeFormSubmit, onSubmit(res), fetchIssueDetails, primaryButtonText{default,loading}, isProjectSelectionDisabled`, `apps/web/components/epic-modal/modal.tsx`). Texte (R6 `epic.*`, Z. 416–430): „New Epic“, „Add Epic“, „Adding epic“, „Epic Title“, Pflicht „Epic title is required.“, „Press 'Enter' to add another epic“ (Quick-Add), „Epic created successfully“, Plural `{count, plural, one {Epic} other {Epics}}`.
5. **Kinder (Sub-Work-Items):** Epic-Kinder werden über `POST …/epics/{epic_id}/issues/` (`work_item_ids`) angehängt; der Server **validiert die Typ-Hierarchie** und setzt `parent` (D1 `epics/add-epic-work-items.md`). Löschen eines Epics setzt bei allen Kindern `parent = null` (D1 `epics/delete-epic.md`). Im Frontend nutzt der Epic-Service statt `sub-issues/` den Pfad `issues/` und statt `issue-links/` den Pfad `links/` (`apps/web/services/issue/issue.service.ts` Z. 261, 277, 288–331). In Epic-Zeilen wird der Sub-Issue-Zähler nicht angezeigt (`apps/web/components/issues/issue-layouts/spreadsheet/issue-row.tsx` Z. 129, 339; `list/block.tsx` `!isEpic`), Bulk-Auswahl in Epic-Listen deaktiviert (`spreadsheet-view.tsx` Z. 87, `list/default.tsx` Z. 137). Leerzustand Epic-Kinder: „You haven't added work items to this epic yet.“ – „Start by adding some work items to this epic and track them here.“ – „Add work items“ (`project_empty_state.epic_work_items.*`, R7 Z. 103–109).
6. **Cycles/Module:** Epics können Cycles und Modulen zugeordnet werden (Power-K: `addCycleToEpic`, `removeEpicFromCycle`, `changeModulesInEpic`; Fehlertext „Epic could not be updated. Please try again.“, `apps/web/components/power-k/ui/pages/context-based/work-item/commands.ts` Z. 309–359).
7. **Kommentare/Activity:** Activity-Typen `epic-comment`, `epic-property` (`issue_comment.service.ts` Z. 38, `issue_activity.service.ts` Z. 34). Die Detail-Antwort wird im Client mit `is_epic = true` markiert (`issue.service.ts` Z. 118–121, 449–452).
8. **Archiv:** „No archived epics yet“ – „You can archive epics that are completed or cancelled. Find them here once archived.“ (`workspace_empty_state.archive_epics.*`, R7 Z. 110–113). Das CE-Archiv der Work Items blendet Epics aus (`Issue.objects.filter(Q(type__isnull=True) | Q(type__is_epic=False))`, `apps/api/plane/app/views/issue/archive.py` Z. 99).
9. **Leerzustand Liste:** „Turn complex projects into structured epics.“ – „An epic helps you organize big goals into smaller, trackable tasks.“ – CTAs „Create an Epic“ und „Documentation“ (`project_empty_state.epics.*`, R7 Z. 97–102); Komponente `ProjectEpicsEmptyState` (CE-Stub `apps/web/components/issues/issue-layouts/empty-states/project-epic.tsx`).
10. **Suche/Relationen:** Suchparameter `epic?: boolean` (`packages/types/src/project/projects.ts` `TProjectIssuesSearchParams`); Relationen liefern `is_epic` (`apps/api/plane/api/serializers/issue.py` Z. 655–683); Home-Recents mit `is_epic` (`packages/types/src/home.ts` Z. 44); Analytics-Metrik „Epic“ (`EPIC_WORK_ITEM_COUNT`, `packages/constants/src/analytics/common.ts` Z. 185–186).
11. **Projektübergreifend:** Epics (und Work Items) können in andere Projekte dupliziert werden (W changelog v1.13.0 „Duplicate work items and epics across projects“, via Dok 26 W38); Sub-Work-Items können projektübergreifend verknüpft werden (W changelog 2026-03-31 „link sub-work items across projects“, via Dok 25 W50) – Detail UNVERIFIZIERT.
12. **Generationswechsel (W via Dok 21 §4.1):** Seit 26.05.2026 ist „Epic“ in der Cloud ein normaler, konfigurierbarer Work-Item-Typ; die separate Epic-Oberfläche wurde in die Work-Item-Liste gefaltet; Kommentare, Updates, Sub-Items und Initiative-Verknüpfungen bleiben erhalten. Das CE-Repo v1.4.2 enthält dagegen noch die **separate** Epic-Plumbing (eigene Routen/Services/Stores). **Entscheidung nötig (Rückfrage R-01):** Welche Generation ist die 1:1-Referenz? Vorschlag: Datenmodell nach neuer Generation (Epic = Typ), UI nach CE-Plumbing (eigener Nav-Eintrag „Epics“), da das CE-Frontend die Referenz für ADR-005 ist.

**Datenmodell (D1 `epics/overview.md`, vollständig in Dok 21 §4.1):** `id, name*, description (object), description_html, description_stripped, description_binary, state (RO; Request `state_id`), priority ∈ {none, urgent, high, medium, low}, assignees (RO; Request `assignee_ids`), labels (RO; Request `label_ids`), type, estimate_point, point, start_date, target_date, parent (RO; Request `parent_id`), sequence_id, sort_order, is_draft, completed_at, archived_at, project, workspace, external_id, external_source, deleted_at, created_at, updated_at, created_by, updated_by`; Kinder zusätzlich `type_id`, `last_activity_at`.

**API-Hinweise (Commercial v1, Scope `projects.epics:*`):** `GET/POST /api/v1/workspaces/{slug}/projects/{project_id}/epics/` (Cursor-Pagination), `GET/PATCH/DELETE …/epics/{epic_id}/`, `GET/POST …/epics/{epic_id}/issues/` (Doku-Fehler: Scope `projects.work-items:read` mit Bindestrich). Intern erwartet das CE-Frontend `POST/GET /api/workspaces/{slug}/projects/{pid}/epics/`, `…/epics-detail/`, `…/v2/epics/`, `…/epics/list/`, `…/epics/{id}/`, `…/epics/{id}/history/`, `…/epics/{id}/issue-relation/`, `…/epics/{id}/issues/`, `…/epics/{id}/links/`, `…/epics/{id}/subscribe/`, `…/epics-user-properties/` (`apps/web/services/issue/issue.service.ts` Z. 33–452, generisch über `${this.serviceType}`) – **keiner davon existiert im CE-Backend**.

**UI-Hinweise:** Icons `EpicOutline/Filled` (project-features), `ConvertToEpicOutline/Filled`, `ConvertToWorkItemOutline/Filled` (actions); Illustrationen `epic` (horizontal- und vertical-stack). Projekt-Activity-Icon für `is_epic_enabled` = `GridOutline` (R21 Z. 68).

**CE-Status:** Stub/UI-Hülle – vollständige Dateiliste der Epic-Plumbing in Dok 20 PF-14 (`grep -rln "is_epic|EIssueServiceType.EPICS|EIssuesStoreType.EPIC|isEpic"`).

**Migrationshinweise:** Epic = `WorkItem` mit `WorkItemType.IsEpic`; die REST-Fassade `/epics/` ist ein gefilterter View auf Work Items (Filter `type.is_epic = true`) mit Feld-Mapping `state_id→state` usw.; interne Fassade für `epics-detail`, `v2/epics`, `epics/list` analog zu den Work-Item-Endpunkten (Kern-Analyse `migration/analysis/04-api-intern-arbeitsobjekte.md` §2.2). Hierarchie-Validierung zentral (WM-02).

**Quellen:** R1, R6, R7, R11, R21; D1, D2, D3; W (via Dok 21, 25, 26). **Konfidenz:** hoch (Modell, API, Plumbing) / mittel (UI-Generation).

#### WM-10 – Epic-Fortschritt und Epic-Updates

**Tier:** wie Epics (Pro). „Progress Charts – Track progress in cycles, modules, and overviews throughout Plane …“ ab Pro (R1 Z. 538–548).

**Funktionsbeschreibung:**
- **Fortschritt (Analytics):** Je Epic Kennzahlen `backlog_issues`, `unstarted_issues`, `started_issues`, `completed_issues`, `cancelled_issues`, `overdue_issues` (`TEpicAnalytics`/`TEpicAnalyticsGroup`, `packages/types/src/epics.ts`) – Zählung der Kinder je State-Gruppe; `overdue` = Kinder mit `target_date < heute` und State-Gruppe nicht `completed`/`cancelled` (Definition UNVERIFIZIERT, analog Cycle-Analytics). Darstellung als Fortschrittsbalken/Kreis im Epic-Detail und in Epic-Listen (UNVERIFIZIERT). Leerzustand-Text „Start setting property values in work items to see progress metrics here.“ (`common_empty_state.progress.description`, R7 Z. 3–6) – Zuordnung zu Epic/Initiative-Fortschritt wahrscheinlich, UNVERIFIZIERT.
- **Updates (Status-Feed):** Gemeinsames Update-Modul für Projekte, Epics und Initiativen (R9; W Forum „Kommentare/Updates … bleiben erhalten“ bei Epics, via Dok 21 §4.1). Je Update: Status `EUpdateStatus` ∈ {`ON-TRACK` „On-Track“, `OFF-TRACK` „Off-Track“, `AT-RISK` „At risk“} (`packages/types/src/enums.ts` Z. 87–91; `common.on_track/off_track/at_risk`, R8 Z. 588–590), Text (Placeholder „Add your update here“), Button „Add Update“; Abschnitt **„Progress“ – „Since last update“** (Delta der Fortschrittszahlen seit dem letzten Update); Kommentar-Zähler `{count, plural, one{# Comment} other{# Comments}}`; Reaktionen (Toasts „Reaction created“/„The reaction has been successfully created“, „Reaction not created“/„The reaction could not be created“, „Reaction removed“/…, „Reaction not removed“/…); Erstellen „Update created“/„The update has been successfully created“ bzw. „Update not created“/„The update could not be created“; Bearbeiten „Updated“/„The update has been successfully updated“ bzw. „Update not updated“/„The update could not be updated“; Löschen-Dialog „Delete update“ – „Are you sure you want to delete this update? This is an irreversible action.“, Toasts „Update deleted“/„Update not deleted“; Leerzustand „No updates yet“ – „You can see the updates here.“ (R9 vollständig) bzw. „No updates yet.“ – „Once project members add updates it will appear here“ (`common_empty_state.updates`, R7 Z. 7–10).
- Icons `UpdatesOutline/Filled` (miscellaneous), Illustration `update` (horizontal-stack).

**Datenmodell (Vorschlag):** `entity_update(id, workspace_id, entity_type ∈ {project, epic, initiative}, entity_id, status, description_html/json/stripped, progress_snapshot jsonb {backlog, unstarted, started, completed, cancelled, overdue, total}, created_by, created_at, updated_at, deleted_at)`; `entity_update_comment`, `entity_update_reaction(update_id, actor_id, reaction)` (Unique je Actor+Reaction). „Since last update“ = Differenz aktueller Kennzahlen zu `progress_snapshot` des vorherigen Updates.

**API:** nicht öffentlich dokumentiert (UNVERIFIZIERT). **CE-Status:** Stub/UI-Hülle (Typen, Enum, Texte). **Konfidenz:** mittel (Texte) / niedrig (Berechnung).

---

### 3.4 Initiatives

#### WM-11 – Initiatives

**Tier:** Pro, Business, Enterprise ✓ laut R1 Z. 272–282 („Create initiatives to roll up several epics.“, `comingSoon: true`); plane.so/pro „epics and initiatives“ (W via Dok 20 PF-15); **Konflikt:** Plane University ordnet Initiatives Business zu (W via Dok 21 §3 F02). **Sub-Initiativen nur Enterprise** (W plane.so/plane-vs-linear via Dok 21 §4.2).

**Funktionsbeschreibung:**
1. Workspace-weite strategische Ziele, die Arbeit über **Projekte, Epics und Work Items** bündeln und Fortschritt messen (D1 `initiative/overview.md`; seit Mai 2026 beliebige Work Items statt nur Epics, W via Dok 21 §4.2).
2. **Workspace-Feature** `initiatives` (D1 `workspace-features`); Workspace-Navigation „Initiatives“ (Icon `InitiativeOutline/Filled`, workspace-features); Workspace-Settings-Eintrag „Initiatives“ (Dok 22 §3.12).
3. **Felder:** Name (Pflicht), Beschreibung als Rich-Text mit Assets (`EFileAssetType.INITIATIVE_DESCRIPTION`, `packages/types/src/enums.ts` Z. 72), Lead (Member), Start-/Enddatum, Logo/Emoji (`logo_props`), State, Labels (WM-12), verknüpfte Projekte, Epics/Work Items.
4. **State-Lebenszyklus:** API `DRAFT`, `PLANNED`, `ACTIVE`, `COMPLETED`, `CLOSED` (D1, D2 Z. 305). Propel-Icons der Kategorie `initiative-states`: `initiative-draft`, `initiative-planned`, `initiative-in-progress`, `initiative-completed`, `initiative-cancelled` (R23) ⇒ UI-Mapping `ACTIVE` → „In progress“, `CLOSED` → „Cancelled“ (UNVERIFIZIERT; Labels nicht im CE-i18n).
5. **Detailseite** mit ein-/ausklappbarer rechter Sidebar; Zustand `initiativesSidebarCollapsed` mit Persistenz in `localStorage["initiatives_sidebar_collapsed"]` (`apps/web/store/theme.store.ts` Z. 20, 32, 47, 62, 74, 181–187).
6. **Board-Ansicht** für Initiativen (W changelog 2026-04-15 „wiki collections, initiative boards“, via Dok 26 W41) – Gruppierung vermutlich nach State (UNVERIFIZIERT).
7. **Fortschritt:** Roll-up über verknüpfte Projekte/Epics/Work Items (Berechnung UNVERIFIZIERT; Vorschlag: Summe der Work-Item-Zählungen je State-Gruppe aller verknüpften Epics/Work Items und der Work Items verknüpfter Projekte, analog `TEpicAnalytics`).
8. **Updates:** Update-Feed wie WM-10 (`entity_type = initiative`).
9. **Sub-Initiativen** (Enterprise): Initiative mit Eltern-Initiative (W via Dok 21 §4.2; Details UNVERIFIZIERT).
10. Reservierte Workspace-Slugs `initiatives`, `initiative` (`packages/constants/src/workspace.ts` Z. 54–55; `apps/api/plane/utils/constants.py` Z. 47–48).

**Datenmodell (D1 `initiative/overview.md`, `add-initiative.md`):** `id, name*, description (Plain Text), description_html, description_stripped, description_binary (RO), lead (uuid), start_date, end_date (date), logo_props (object), state (enum oben), archived_at, workspace (RO), created_at, updated_at, created_by, updated_by`. Verknüpfungen: Projekte (Body `project_ids`), Epics (Body `epic_ids`), Labels (Body `label_ids`). Response-Lite-Formen: Projekt `{id,name,description,identifier,network(,project_lead,created_at,updated_at)}`, Epic `{id,name,description,priority,sequence_id,state{id,name,group},assignees,labels,created_at}` (Dok 21 §4.2). **Vorschlag EF:** `initiative`, `initiative_project` (Unique), `initiative_work_item` (Unique; ersetzt `initiative_epic`), `initiative_label`, `initiative_label_assignment`, `initiative.parent_id` (nullable, Sub-Initiativen, zyklenfrei).

**API (Commercial v1, Scopes `initiatives:*`, `initiatives.projects:*`, `initiatives.epics:*`, `initiatives.labels:*`):** `GET/POST /api/v1/workspaces/{slug}/initiatives/`, `GET/PATCH/DELETE …/initiatives/{initiative_id}/`, `GET/POST/DELETE …/initiatives/{initiative_id}/projects/`, `GET/POST/DELETE …/initiatives/{initiative_id}/epics/`, `GET/POST/DELETE …/initiatives/{initiative_id}/labels/` (DELETE mit ID-Array im Body, Dok 21 §8 O3). Pagination widersprüchlich: REST Cursor (`cursor`, `per_page`), MCP „returns every initiative; this endpoint does not paginate“ (D2 Z. 296).

**UI-Hinweise:** Icons `InitiativeOutline/Filled`, State-Icons `initiative-*` (R23); Illustration `initiative` (vertical-stack, R24). Label-Dropdown mit Scope `initiative` (Kommentar „EE switches on a `scope` (work item / release / initiative / project) and a governed label catalog“, `apps/web/components/dropdowns/label/label-select.tsx` Z. 48–49).

**CE-Status:** Stub/UI-Hülle. **Quellen:** R1, R23, R24; D1, D2; W (via Dok 20, 21, 26). **Konfidenz:** hoch (Felder/API) / mittel (UI, Fortschritt).

#### WM-12 – Initiative-Labels

Workspace-weiter Label-Katalog nur für Initiativen: `id, name*, description, color (Hex), sort_order (number), workspace, created_at` (D1 `initiative/add-initiative-label.md`); Endpunkte `GET/POST /api/v1/workspaces/{slug}/initiatives/labels/`, `GET/PATCH/DELETE …/initiatives/labels/{label_id}/`; Zuordnung `GET/POST/DELETE …/initiatives/{initiative_id}/labels/`. Label-Dropdown im Scope `initiative` (siehe WM-11). Seit 15.09.2026 gibt es zusätzlich **Workspace-Labels** (W changelog 2026-09-15 „workspace labels“, via Dok 26 W36) – Verhältnis zu Initiative-Labels UNVERIFIZIERT. **CE-Status:** fehlt. **Konfidenz:** hoch (API) / niedrig (UI).

#### WM-13 – Checkpoints und Updates an Projekten/Epics/Initiativen

**Tier:** Checkpoints Pro, Business, Enterprise („Coming soon“, R1 Z. 284–295: „Add markers to Projects, Epics and Initiatives to keep your team on track and report on progress.“); Project Updates Pro (auskommentiert, R1 Z. 354–366).

**Funktionsbeschreibung:** Updates siehe WM-10/WM-40. **Checkpoints:** außer dem Matrix-Text keine Belege (Repo, D, W). Abgrenzung zu Milestones (WM-14, projektbezogen mit Work-Item-Zuordnung) unklar. **Vorschlag (UNVERIFIZIERT, Rückfrage R-03):** Checkpoint = datierter Marker (`title`, `date`, optionale Beschreibung, optionaler Ziel-Fortschritt in %) an Projekt/Epic/Initiative, sichtbar in Timeline/Gantt und im Update-Feed (Vergleich Ist-Fortschritt am Checkpoint-Datum). **CE-Status:** Updates Stub, Checkpoints fehlt. **Konfidenz:** niedrig.

---

### 3.5 Milestones

#### WM-14 – Milestones

**Tier:** nicht in R1; eingeführt in Self-hosted v1.16.0 (05.11.2025, „Introducing milestones and recurring cycles“, W via Dok 21 §4.5 / Dok 25 W49). Planstufe UNVERIFIZIERT.

**Funktionsbeschreibung:**
1. **Projekt-Feature** „Milestones“ – „Milestones provide a layer to align work items toward shared completion dates.“ mit Toggle „Enable milestones“ – „Organize work items by milestone deadlines.“ (R4 Z. 420–426; `common.milestones`, `milestones_description`, R8 Z. 717, 844–845). Template-Blueprint-Flag `is_milestone_enabled` (via Dok 25 F20).
2. **Milestone:** Titel (Pflicht), Zieldatum; Work Items werden einem Milestone zugeordnet (D1 `milestones/*`; D2 Z. 274–288; Compose `work/milestones.yaml` mit `name` → API `title`, `target_date`, `work_items` als Liste von Sequenz-IDs, D3 Z. 1376–1400).
3. **Status-Darstellung:** Propel-Kategorie `milestone-states` mit `milestone-not-started`, `milestone-in-progress`, `milestone-done` (R23) ⇒ abgeleiteter Status aus dem Fortschritt der zugeordneten Work Items (keine `status`-Spalte in der API; Ableitungsregel UNVERIFIZIERT; Vorschlag: keine Items oder alle offen in `backlog`/`unstarted` → not started; alle `completed`/`cancelled` → done; sonst in progress).
4. **Projekt-Overview:** einklappbarer Abschnitt „milestones“, standardmäßig geöffnet (`ProjectOverviewCollapsible = "links" | "attachments" | "milestones"`, `openCollapsibleSection = ["milestones"]`, `apps/web/store/project/project.store.ts` Z. 21, 86).
5. **Gruppierung/Filter:** Work Items gruppierbar nach `milestone_id`; PQL-Feld `milestone` (UUID) (D2 Z. 48, 91).
6. Laut Changelog auch Zuordnung von Cycles/Modulen zu Milestones (W via Dok 21 §4.5) – UNVERIFIZIERT.
7. Webhook-Events `milestone.created`, `milestone.updated`, `milestone.deleted` (D4 Z. 246–248); Webhook-Filter gelten nicht für Milestones (D4 Z. 67).

**Datenmodell (D1 `milestones/overview.md`):** `id, title*, target_date, external_id, external_source, created_at, updated_at` (+ implizit `project`, `workspace`); Zuordnungsobjekt `{id, issue, milestone}` (D1 `milestones/list-milestone-work-items.md`). Kardinalität: Gruppierung nach `milestone_id` spricht für **höchstens einen Milestone je Work Item** (Vorschlag Dok 21 §8 O6: Link-Tabelle mit Unique(`issue_id`)).

**API (Commercial v1; Scope laut D5 `projects.milestones:read|write`, in D1 nicht angegeben):** `GET/POST /api/v1/workspaces/{slug}/projects/{project_id}/milestones/`, `GET/PATCH/DELETE …/milestones/{milestone_id}/`, `GET …/milestones/{milestone_id}/work-items/`. Zuordnen/Entfernen nur über MCP `manage_workitems(add_ids, remove_ids)` belegt (D2 Z. 286) → Vorschlag `POST/DELETE …/milestones/{id}/work-items/` mit `work_item_ids`.

**UI-Hinweise:** Icons `MilestoneOutline`, `MilestonesFilled` (project-features), `milestone-*` (R23); Illustration `milestone` (vertical-stack, R24); Fetch-Key `PROJECT_MILESTONES(projectId, projectRole)` (`packages/constants/src/fetch-keys.ts` Z. 205–206). Work-Item-Property „Milestone“ in Sidebar/Modal (UNVERIFIZIERT; Label fehlt im CE-i18n).

**CE-Status:** Stub/UI-Hülle. **Konfidenz:** mittel.

---

### 3.6 Releases

#### WM-15 – Releases (inkl. Release-Tags, Release-Labels, Changelog)

**Tier:** nicht in R1; eingeführt mit Release v2.6.0 („PQL, releases, wiki collections and more“, W via Dok 25 W47); Blog „Introducing Releases“ (W via Dok 21 §4.18). Planstufe UNVERIFIZIERT. Workspace-Settings-Eintrag „Releases“ im Commercial-Screenshot (Dok 22 §3.12).

**Funktionsbeschreibung (D2 Z. 307–356, D3):**
1. **Release** (workspaceweit): Name (Pflicht), Beschreibung (HTML), **Status** `unreleased` (Default), `released`, `cancelled`; **„Target date“** in der UI = Feld `release_date` (`YYYY-MM-DD`); zusätzlich gespeichertes, in der UI **nicht sichtbares** Feld `target_date`; Lead (`lead_id`, Workspace-Member); Release-Tag (`tag_id`); Flag `is_prerelease`; `external_source/external_id`.
2. **Changelog:** Rich-Text-Dokument je Release, wird **leer mit dem Release angelegt** (daher liefert `get_changelog` immer einen Datensatz); Bearbeitung mit `description_html` oder `description_stripped` (Plain Text wird in HTML gewandelt). Illustration `changelog` (vertical-stack, R24) für den Leerzustand.
3. **Work Items** zuordnen/entfernen (`add_ids`, `remove_ids`); Gruppierungsschlüssel `release_work_items__release_id` ⇒ n:m-Tabelle `release_work_items` (D2 Z. 91).
4. **Release-Tags** (Versionsmarken): `version`* (z. B. „v1.2.0“), `description`, `commit_hash`, `git_tag`; ein Tag wird einem Release über `tag_id` zugeordnet (D2 Z. 329–341). Compose-State-Pfad `releases.tags.v1.0` (D3 Z. 934) ⇒ Tags sind über `version` eindeutig.
5. **Release-Labels:** Workspace-Palette (`name`*, `color` Hex, `sort_order`); `attach`/`detach` an Releases; Löschen entfernt das Label aus der Palette für alle, Detach lässt es in der Palette (D2 Z. 343–356). Label-Dropdown mit Scope `release` (`label-select.tsx` Z. 48–49).
6. **Release-Picker-Property** an Work Items (WM-04): Compose „Reference to a Plane release tag. Populated on pull; push is blocked by the Plane API. Read-only in practice.“ (D3 Z. 1109) vs. MCP `relation_type: RELEASE` (D2 Z. 212) – Referenzziel (Release oder Release-Tag) UNVERIFIZIERT.
7. Plane Compose: Workspace-Abschnitt `releases` (überspringbar mit `--skip releases`, D3 Z. 848, 866).

**Datenmodell (Vorschlag):** `release(id, workspace_id, name, description_html/json/stripped, status, release_date, target_date, lead_id, tag_id, is_prerelease, external_*)`, `release_changelog(release_id PK/FK, description_html/json/stripped/binary)`, `release_work_item(release_id, work_item_id, Unique)`, `release_tag(id, workspace_id, version (Unique je Workspace), description, commit_hash, git_tag)`, `release_label(id, workspace_id, name, color, sort_order)`, `release_label_assignment`.

**API:** REST nicht dokumentiert (nicht in D1). Vorschlag Pfade analog MCP: `/api/v1/workspaces/{slug}/releases/`, `…/releases/{id}/changelog/`, `…/releases/{id}/work-items/`, `/release-tags/`, `/release-labels/`, `…/releases/{id}/labels/`.

**UI-Hinweise:** Icons `ReleasesOutline/Filled` (workspace-features), `ReleaseTagOutline/Filled` (miscellaneous) (R23). Alle UI-Texte fehlen im CE-i18n → aus Referenz-Screenshots ergänzen (O-04).

**CE-Status:** fehlt. **Konfidenz:** mittel (Felder/Verhalten aus MCP) / niedrig (UI).

---

### 3.7 Customers

#### WM-16 – Customers

**Tier:** **Konflikt:** Business (docs.plane.so/customers; Blog „Introducing Plane Business“: „customer database … link work items to customers“; W via Dok 21 §3 F04) vs. Pro „customer profiles“ (plane.so/pricing, W via Dok 20 PF-41). Nicht in R1. Workspace-Feature `customers` (D1 `workspace-features`).

**Funktionsbeschreibung:**
1. Workspace-Navigation „Customers“ (Icon `CustomersOutline/Filled`, workspace-features) und Workspace-Settings „Customers“ (Dok 22 §3.12); Aktivierung in den Workspace-Settings (W via Dok 21 §4.3).
2. **Kundenprofil-Felder** (D1 `customer/add-customer.md`; D2 Z. 475–481): Name (Pflicht), Beschreibung (Rich-Text: `description` object, `description_html`, `description_stripped`), E-Mail, Website (`website_url`), **„Industry“** (API-Feld `domain` – **nicht** die Web-Domain!), Mitarbeiterzahl (`employees`, Integer), **Stage** (gespeichert als Freitext; angezeigt nur `lead`, `sales_qualified_lead`, `contract_negotiation`, `closed_won`, `closed_lost`), **Contract status** (Freitext; angezeigt nur `active`, `pre_contract`, `signed`, `inactive`), **Revenue** (Jahresumsatz als String), Logo (`logo_props` oder Upload `logo_asset` → `logo_url`), `archived_at`. Andere Stage/Contract-Werte werden gespeichert, aber nicht angezeigt.
3. **Upsert-Semantik (MCP):** `create` sucht zuerst nach `external_source`+`external_id`, sonst nach `name` – erzeugt nie Duplikate; `delete` per `customer_id` oder `external_source`+`external_id` (D2 Z. 475–477).
4. **Work-Item-Verknüpfung:** Kunden ↔ Work Items (optional im Kontext eines Requests); Liste der verknüpften Work Items filterbar nach Request und Suche (D2 Z. 478–479). Am Work Item: Display-Properties **`customer_count`** und **`customer_request_count`** (in CE-Seeds bereits gesetzt: `apps/api/plane/bgtasks/workspace_seed_task.py` Z. 160, 163; `apps/api/plane/seeds/data/views.json` Z. 10; **nicht** im CE-Typ `IIssueDisplayProperties`, `packages/types/src/view-props.ts` Z. 161–178) ⇒ Listen zeigen Anzahl verknüpfter Kunden bzw. Requests.
5. **Priorisierung:** Requests nach Kunde filtern, nach Umsatz/Vertragsstatus priorisieren; verknüpfte Work Items zeigen die Kunden dahinter (W via Dok 21 §4.3).
6. **Create-Modal** mit expliziter Tab-Reihenfolge (`ETabIndices`; Kommentar „the work item, intake and customer create modals order every control through `ETabIndices`“, `packages/blocks/src/select/types.ts` Z. 383–384) – im CE-`ETabIndices` fehlt ein Customer-Eintrag (`packages/constants/src/tab-indices.ts` Z. 79–88).
7. Silo-Connector **HubSpot** existiert in der Commercial-Konfiguration; Bezug zu Customers unbelegt (Dok 22, HubSpot-Abschnitt).

**Datenmodell (Dok 21 §4.3 vollständig):** `customer(id, workspace_id, name, description jsonb/html/stripped/binary, email, website_url, domain, employees int, stage text, contract_status text, revenue text, logo_props jsonb, logo_asset_id, archived_at, external_*, Audit, deleted_at)`; `customer_request_count` (RO, berechnet).

**API (Commercial v1, Scope `customers:*`):** `GET/POST /api/v1/workspaces/{slug}/customers/`, `GET/PATCH/DELETE …/customers/{customer_id}/`; Work Items `GET/POST …/customers/{customer_id}/issues/` (Body `issue_ids`), `DELETE …/customers/{customer_id}/issues/{work_item_id}/` (Scope `customers.work_items:*`).

**UI-Hinweise:** Icons `CustomersOutline/Filled` (R23); Illustrationen `customer` (horizontal- und vertical-stack, R24). **Im CE-i18n existiert kein Customers-Namespace** → alle Texte (Feldlabels „Industry“, „Stage“, „Contract status“, „Revenue“, „Employees“, „Website“, „Email“ sind nur aus MCP-Hinweisen ableitbar) aus Referenz-Screenshots ergänzen (O-04). Stage-/Contract-Labels (Vorschlag, UNVERIFIZIERT): „Lead“, „Sales qualified lead“, „Contract negotiation“, „Closed won“, „Closed lost“; „Active“, „Pre-contract“, „Signed“, „Inactive“.

**CE-Status:** fehlt (nur Seeds/Illustrationen). **Konfidenz:** hoch (Felder/API) / niedrig (UI).

#### WM-17 – Customer Requests

**Funktionsbeschreibung:** Anfragen (Feature-Wünsche, Bugs) eines Kunden: Name (Pflicht), Beschreibung (Rich-Text), `link` (URL), verknüpfte Work Items. `work_item_ids` ist **write-only und nur beim Anlegen** wirksam, wird nie zurückgegeben; spätere Änderung über die Customer-Work-Item-Verknüpfung mit `customer_request_id` (D2 Z. 483–495; D1 `customer/add-customer-request.md`). Löschen eines Requests entkoppelt verknüpfte Work Items (Dok 21 §4.3). **API (Scope `customers.requests:*`):** `GET/POST /api/v1/workspaces/{slug}/customers/{customer_id}/requests/`, `GET/PATCH/DELETE …/requests/{resource_id}/` (Response-Beispiele der Doku fehlerhaft, Dok 21 §1.3 D1). **Datenmodell:** `customer_request(id, customer_id, workspace_id, name, description*, link, Audit)`, `customer_work_item(customer_id, work_item_id, customer_request_id NULL, Unique(customer_id, work_item_id, customer_request_id))`. **CE-Status:** fehlt. **Konfidenz:** mittel.

#### WM-18 – Customer Properties

**Funktionsbeschreibung:** Eigene Properties für Kunden mit **denselben Typen** wie Work-Item-Properties (`TEXT`, `DATETIME`, `DECIMAL`, `BOOLEAN`, `OPTION`, `RELATION` (`ISSUE`, `USER`, `RELEASE`, `RICH_TEXT`), `URL`, `EMAIL`, `FILE`, `FORMULA`); `display_name` **workspaceweit eindeutig**, `name` daraus abgeleitet; `display_format` Pflicht bei TEXT/DATETIME; Optionen `{name, description, is_default}` (D2 Z. 497–511). **Werte:** `PATCH …/customers/{customer_id}/property-values/{property_id}/` mit `{"values": ["…"]}` (Pflicht), Antwort 204; MCP `set_values` mit `{"<property_id>": ["Enterprise"]}` – **jeder Wert ist ein String**, unabhängig vom Typ; Ein-Element-Liste außer bei `is_multi`; ersetzt nur die genannten Properties (D2 Z. 508–511). **API (Scopes `customers.properties:*`, `customers.property_values:*`):** `GET/POST /api/v1/workspaces/{slug}/customer-properties/`, `GET/PATCH/DELETE …/customer-properties/{property_id}/`, `GET …/customers/{customer_id}/property-values/`, `GET/PATCH …/customers/{customer_id}/property-values/{property_id}/`. **Migration:** gemeinsame Property-Engine mit WM-03 (Owner-Kind `customer`). **CE-Status:** fehlt. **Konfidenz:** hoch (API) / niedrig (UI).

---

### 3.8 Recurring Work Items, Work Item Templates, Pre-defined Templates

Die vollständigen Spezifikationen (Formulare, API v2, Zeitlogik, Migrationshinweise) stehen in **Dok 25** (F21 Work Item Templates, F23 Pre-defined Templates/Marketplace, F24 Recurring Work Items). Hier nur Tier, CE-Prüfung und die für den Work-Management-Cluster relevanten Schnittstellen.

#### WM-19 – Recurring Work Items

**Tier:** Business („Set it once. We’ll bring it back when it’s due. Upgrade to Business to make recurring work feel effortless.“, `recurring_work_items.empty_state.upgrade.description`, R6 Z. 337 ff.). **Kurzspezifikation:** Projekt-Settings „Recurring work items“ – „Set your repeatable work once, and we’ll take care of the repeats. You’ll see everything right here when it’s time.“; Formular = Work-Item-Blueprint + Abschnitt „Schedule“ (Startdatum Pflicht „Start date is required“, Intervalltyp Pflicht „Interval type is required“; API v2: `interval_type` ∈ daily/weekly/monthly/yearly, `interval_count`, `start_at`, `end_at`, Läufe um 00:05 Projekt-Zeitzone); nur Projekt-Admins („Contact your project admin to create recurring work items“); Leerzustand „No recurring work item yet“ (R7); Löschdialog „Are you sure you want to delete recurring work item-“ … „? All of the data related to the recurring work item will be permanently removed. This action cannot be undone.“; Toasts mit `{name}` (R6). Erzeugte Work Items durchlaufen dieselbe Logik wie manuell angelegte (Default-Typ, Custom-Property-Defaults WM-05, Workflow, Activity). **CE-Status:** fehlt (`grep -rn recurring apps/api apps/web --include=*.py --include=*.tsx` ohne Treffer außer Plan-/i18n-Texten). **Quellen:** R6, R7, R8; Dok 25 F24. **Konfidenz:** mittel–hoch.

#### WM-20 – Work Item Templates

**Tier:** Pro (R1 `planHighlights.pro` „Work item templates“, Z. 1306). **Kurzspezifikation:** Projekt- und Workspace-Ebene; Formular „Name your work-item template.“ (Pflicht, < 255), „Describe when and how to use this template.“, Work-Item-Felder (Titel Pflicht „Work item title is required“, Beschreibung „Describe this work item so its clear what you will accomplish when you complete this.“), Properties inkl. Typ und **Custom-Property-Werte** (API-Seed `properties`, Dok 25 F21), Sub-Work-Items; Anwendung im Create-Modal über Tooltip „Pick a work item template“, Dropdown „Add new template“, „No templates found.“; Button „Use template“/„Applying“ (R10). **CE-Status:** Stub/UI-Hülle – Kontextfelder `workItemTemplateId`, `setWorkItemTemplateId`, `isApplyingTemplate`, `setIsApplyingTemplate`, `handleTemplateChange({workspaceSlug, reset, editorRef})`, Prop `templateId` an `IssueModalProvider`/`CreateUpdateIssueModal`; CE-Provider liefert `null`/No-ops (R16). Formularverhalten im CE bereits implementiert: Projektwechsel mit gesetztem Template setzt Template-ID zurück, Formular auf `DEFAULT_WORK_ITEM_FORM_VALUES` mit neuem `project_id`, Editor leeren; „Create more“ + Template wendet das Template nach dem Speichern erneut an; während `isApplyingTemplate` ist das Formular gesperrt (`form.tsx` Z. 157–176, 199–210, 247–256). **Quellen:** R1, R10, R16; Dok 25 F21. **Konfidenz:** hoch (Hooks) / mittel (Inhalt).

#### WM-21 – Pre-defined work item Templates

**Tier:** Pro („Coming soon“; „Choose from our available work item templates that customize work item types and properties for several use cases.“, R1 Z. 368–379). **Kurzspezifikation:** mitgelieferte Vorlagen, die Work Item Types und Properties für Anwendungsfälle vorkonfigurieren; Details und Airgapped-Empfehlung (Seed-Daten statt externer Galerie) siehe Dok 25 F23. **CE-Status:** fehlt. **Konfidenz:** niedrig.

---

### 3.9 Bulk Ops, Transfers, Conversions, Kopie in anderes Projekt

#### WM-22 – Bulk Ops

**Tier:** One „Limited props“; Pro „All props“; Business/Enterprise zusätzlich „Work item transfers and conversions“ (Coming soon) (R1 Z. 162–181; „Add several work items to cycles or modules, transfer them, or edit their properties.“). Upgrade-Karten: `PRO_PLAN_FEATURES` „Full Time Tracking + Bulk Ops“, `ONE_PLAN_FEATURES` „Time-tracking + limited bulk ops“, `FREE_PLAN_UPGRADE_FEATURES` „Time Tracking and Bulk Ops“ (R2). Welche Properties „limited“ sind, ist nicht belegt; nach ADR-001 gilt „All props“.

**Funktionsbeschreibung:**
1. **Mehrfachauswahl** in List-, Spreadsheet- und Gantt-Layout (CE-Infrastruktur `useMultipleSelectStore`, `TSelectionHelper`, `apps/web/hooks/use-multiple-select.ts`, `apps/web/store/multiple_select.store.ts`; Aktivierung über `enableSelection={isBulkOperationsEnabled && isAllowed}` u. a. in `apps/web/components/issues/issue-layouts/gantt/base-gantt-root.tsx` Z. 143; Auswertung von `useBulkOperationStatus()` in `spreadsheet/spreadsheet-view.tsx` Z. 66/87, `list/default.tsx` Z. 86/137, `gantt/base-gantt-root.tsx` Z. 61/143, `apps/web/components/gantt-chart/chart/main-content.tsx` Z. 28). In Epic-Listen deaktiviert (WM-09). Texte: „Select all“, „Deselect all“, „No work items selected“, „Please select at least one work item“ (`issue.select.*`, R6).
2. **Aktionsleiste** am unteren Rand der Liste an der Position des CE-Banners (`sticky bottom-0 left-0 z-[2] grid h-20 place-items-center px-3.5`, `apps/web/components/issues/bulk-operations/root.tsx`); der CE zeigt dort `Banner variant="accent"` mit „Change state, priority, and more for several work items at once. Save three minutes on an average per operation.“ und CTA „Upgrade to One“ (`bulk_operations.upgrade_banner.*`, R6) – **entfällt**.
3. **Änderbare Properties** (`TBulkIssueProperties = Pick<TIssue, "state_id" | "priority" | "label_ids" | "assignee_ids" | "start_date" | "target_date" | "module_ids" | "cycle_id" | "estimate_point">`, `packages/types/src/issues/issue.ts` Z. 140–156). Payload `TBulkOperationsPayload = { issue_ids: string[]; properties: Partial<TBulkIssueProperties> }`.
4. **Semantik (Client-Store, `bulkUpdateProperties`, `apps/web/store/issue/helpers/base-issues.store.ts` Z. 722–757):** Array-Properties (`label_ids`, `assignee_ids`, `module_ids`) werden **hinzugefügt** (Vereinigung mit bestehenden Werten, `uniq([...existing, ...new])`), skalare Properties ersetzt. Server muss dieselbe Semantik liefern.
5. **Server-Validierungen / Fehlertexte** (`bulk_operations.error_details.*`, R6 Z. 313–336): „Unable to archive work items“ – „Only work items belonging to Completed or Canceled state groups can be archived.“; „Unable to update work items“ – „Start date selected succeeds the due date for some work items. Ensure start date to be before the due date.“ bzw. „Due date selected precedes the start date for some work items. Ensure due date to be after the start date.“; „State change is not allowed for some work items. Ensure the state change is allowed.“ (Workflow-Regeln, Dok 25) ⇒ Bulk-Aktionen umfassen auch **Archivieren** (CE-Endpunkt `bulk-archive-issues/` existiert) und **Löschen** (CE `bulk-delete-issues/`, Power-K „Bulk delete work items“) (`apps/api/plane/app/urls/issue.py` Z. 89–101).
6. **Business:** Bulk-**Transfer** (Projekt/Cycle) und Bulk-**Conversion** (Work Item ↔ Epic) (WM-23/24).
7. Custom Properties in Bulk-Aktionen: nicht belegt (UNVERIFIZIERT; Vorschlag: zusätzlich zulassen, analog Werte-Upsert).

**API:** CE-Frontend ruft `POST /api/workspaces/{slug}/projects/{project_id}/bulk-operation-issues/` mit `TBulkOperationsPayload` (`apps/web/services/issue/issue.service.ts` Z. 339–340) – **Route existiert im CE-Backend nicht** (`grep -rn bulk-operation-issues apps/api` leer). Fehlerantwort-Format für `error_details` nicht belegt (Vorschlag: `{"error_code": "invalid_state_transition" | "invalid_issue_start_date" | "invalid_issue_target_date" | "invalid_archive_state_group", "issue_ids": [...]}` → UI mappt Code auf Text).

**CE-Status:** Stub/UI-Hülle (`useBulkOperationStatus = () => false`, `apps/web/hooks/use-bulk-operation-status.ts`). **Migrationshinweise:** Ein Domain-Command `BulkUpdateWorkItems` mit Transaktion je Request, Validierung **pro Work Item** (Teilerfolge? – UNVERIFIZIERT; Vorschlag: alles-oder-nichts mit Fehlerliste), Activity je Item, Benachrichtigungen gebündelt. **Konfidenz:** hoch (Payload/Fehler) / mittel (Teilerfolg-Semantik).

#### WM-23 – Work Item Transfers

**Tier:** Pro, Business, Enterprise ✓ („Move a work item from a project or a cycle to another.“, R1 Z. 238–247).

**Funktionsbeschreibung:**
- **Im CE vorhanden:** Bulk-Transfer aller **offenen** Work Items eines Cycles in einen anderen Cycle. UI: Hinweisleiste „Completed cycles are not editable.“ mit Button „Transfer work items“ (Icon `TransferWorkItemOutline`, `apps/web/components/cycles/transfer-issues.tsx`); Dialog „Transfer work items“ mit Suche „Search for a cycle...“, Liste der unvollständigen Cycles des Projekts mit Status-Chip, Leerzustand „You don’t have any current cycle. Please create one to transfer the work items.“, Toasts „Work items have been transferred successfully“ / „Unable to transfer work items. Please try again.“ (`apps/web/components/cycles/transfer-issues-modal.tsx`); i18n `project_cycles.transfer_work_items` „Transfer {count} work items“, `project_cycles.transfer.no_cycles_available` „No other cycles available to transfer work items to.“. Backend: nur Items der State-Gruppen `backlog`, `unstarted`, `started`; Ziel-Cycle darf nicht beendet sein („The cycle where the issues are transferred is already completed“); vorher wird ein **Progress-Snapshot** des Quell-Cycles gespeichert; Activity „updated_cycle_issues“ (R22; `POST /api/workspaces/{slug}/projects/{pid}/cycles/{cycle_id}/transfer-issues/` mit `new_cycle_id`). Commercial-API identisch (D1 `cycle/transfer-cycle-work-items.md`; MCP behauptet „moves everything“, D2 Z. 249 – Widerspruch, CE-Verhalten maßgeblich).
- **Bezahl-Erweiterung:** (a) Einzelnes Work Item in **ein anderes Projekt verschieben** – Fehlertext „Failed to move work item to project“ (`failed_to_move_issue_to_project`, R8 Z. 280; im CE ungenutzt; „Move to project“ `common.move_to_project` wird im CE nur für Workspace-Drafts verwendet, `apps/web/components/issues/workspace-draft/draft-issue-block.tsx` Z. 82). (b) Einzelnes Work Item zwischen Cycles verschieben (Cycle-Feld ist im CE bereits änderbar – Mehrwert unklar). (c) Bulk-Transfer (WM-22).
- **Verhalten Projekt-Move (Vorschlag, UNVERIFIZIERT – Rückfrage R-05):** neue `sequence_id` im Zielprojekt (Identifier ändert sich, alter Identifier als Redirect), State-Mapping per Gruppe (gleichnamiger State, sonst Default-State der Gruppe im Ziel), Labels per Name (fehlende werden entfernt oder angelegt), Cycle/Modul/Estimate werden geleert, Typ wird auf gleichnamigen Typ oder Projekt-Default gemappt, Custom-Property-Werte typfremder Properties entfallen, Sub-Work-Items und Relationen bleiben (projektübergreifend erlaubt, vgl. CE-Relations „Relations can cross projects“, R14), Attachments/Links/Kommentare/Activity wandern mit.

**CE-Status:** teilweise. **Quellen:** R1, R6, R8, R14, R22, D1, D2. **Konfidenz:** hoch (CE-Teil) / niedrig (Projekt-Move-Details).

#### WM-24 – Conversions (Work Item ↔ Epic)

**Tier:** Bulk-Conversions Business/Enterprise (Coming soon, R1 Z. 168–179); Einzel-Konvertierung ohne Plan-Angabe (UNVERIFIZIERT). **Funktionsbeschreibung:** Aktionen „Convert to Epic“ / „Convert to Work item“ (Icons `ConvertToEpicOutline/Filled`, `ConvertToWorkItemOutline/Filled`, Kategorie `actions`, R23; Texte nicht im CE-i18n). Modal-Kontext-Hook `handleConvert(workspaceSlug: string, data: Partial<TIssue>) => Promise<void>` (R16 `issue-modal-context.tsx`; CE-No-op `provider.tsx` Z. 53) ⇒ Konvertierung läuft über das Work-Item-Modal (Typwechsel auf den Epic-Typ bzw. einen Nicht-Epic-Typ). **Verhalten (Vorschlag):** Typwechsel mit Hierarchie-Validierung (WM-02); Kinder bleiben; typfremde Property-Werte entfallen (Bestätigung wie WM-01 „Change work item type?“). **CE-Status:** Stub/UI-Hülle. **Konfidenz:** mittel (Existenz) / niedrig (Details).

#### WM-25 – Kopie eines Work Items in ein anderes Projekt

**Tier:** unklar; Changelog v1.13.0 „Duplicate work items and epics across projects“ (W via Dok 26 W38). **Funktionsbeschreibung:** Quick Action „Make a copy“ (`common.actions.make_a_copy`) öffnet im CE das Create-Modal mit Payload `{...issue, name: "<Name> (copy)", sourceIssueId: issue.id}` ohne `id` (gleiches Projekt) (`apps/web/components/issues/issue-layouts/quick-action-dropdowns/issue-detail.tsx` Z. 101–108; `helper.tsx` Z. 211–229). In EE wird der Menüpunkt über `createCopyMenuWithDuplication({baseItem, activeLayout, setCreateUpdateIssueModal, setDuplicateWorkItemModal, workspaceSlug})` erweitert (CE gibt nur `baseItem` zurück, `copy-menu-helper.tsx`) – vermutlich Untermenü „In this project“ / „To another project“ (UNVERIFIZIERT). Duplikat-Modal: Titel „Make a copy to another project“, Texte „This creates a copy of the work item.“ und „All property data will be removed while duplicating.“, Projekt-Auswahl Placeholder „Select a project“; Toasts „Work item duplicated successfully“ / „Failed to duplicate work item“ (`issue.duplicate.modal.*`, `issue.toast.duplicate.*`, R6). Peek-Overview hält dafür den State `isDuplicateIssueModalOpen` (`apps/web/components/issues/peek-overview/view.tsx` Z. 61, 82, 86). **Verhalten:** neue Kopie im Zielprojekt mit Titel/Beschreibung; „All property data will be removed“ ⇒ State = Default des Zielprojekts, keine Assignees/Labels/Cycle/Modul/Estimate/Custom-Werte (Umfang UNVERIFIZIERT). **CE-Status:** Stub/UI-Hülle. **Konfidenz:** mittel.

---

### 3.10 Dependencies im Gantt und Custom Relations

#### WM-26 – Dependencies in Gantt

**Tier:** Pro, Business, Enterprise ✓ („Adjust timelines for dependent work items visually on our Gantt layout.“, R1 Z. 227–236).

**Funktionsbeschreibung:**
1. **Dependency-Typen** (built-in, D2 Z. 156): `blocking`, `blocked_by`, `start_before`, `start_after`, `finish_before`, `finish_after`; UI-Labels „Blocking“, „Blocked by“, „Starts Before“, „Starts After“, „Finishes Before“, „Finishes After“ (`issue.relation.*`, R6 Z. 186–198). Eigener Button **„Add dependency“** (`issue.add.dependency`, im CE ungenutzt) neben „Add relation“ (`issue.add.relation`, im CE genutzt in `issue-detail-widgets/action-buttons.tsx` Z. 54 und `relations/quick-action-button.tsx` Z. 57); Abschnittslabels „Dependencies“ und „Relations“ (`common.dependencies`, `common.relations`, R8 Z. 555–556). **Dependencies und Custom Relations sind unabhängig** (MCP `delete … is_dependency`, D2 Z. 150; getrennte Webhook-Events `workitem.dependency.*` vs. `workitem.relation.*`, D4 Z. 271–274).
2. **Speicher-Semantik (CE-Backend, maßgeblich):** Gespeichert werden nur die „Vorwärts“-Typen `blocked_by`, `start_before`, `finish_before` (und `relates_to`, `duplicate`, `implemented_by`). Beim Anlegen von `blocking`/`start_after`/`finish_after` werden `issue` und `related_issue` vertauscht und der Typ auf die Vorwärtsform gemappt (`get_actual_relation`, `apps/api/plane/utils/issue_relation_mapper.py`; `relation.py` Z. 266–281). Datensatz `(issue=A, related_issue=B, start_before)` bedeutet „A starts before B“ und erscheint bei B als „Starts After: A“. Lesen liefert je Work Item die Listen `blocking`, `blocked_by`, `duplicate`, `relates_to`, `start_after`, `start_before`, `finish_after`, `finish_before` (`relation.py` Z. 84–135, 200–235). Relationen dürfen Projekte überschreiten (nur Workspace-Scope, `relation.py` Z. 257–264). **Unique `(issue, related_issue)`** bei `deleted_at IS NULL` ⇒ zwischen zwei Items nur **eine** Relation beliebigen Typs (R13 Z. 305–316).
3. **Zeitliche Semantik (Vorschlag, UNVERIFIZIERT – Rückfrage R-06):** `A start_before B`: B darf nicht vor A starten (`B.start_date ≥ A.start_date`, Start-to-Start); `A finish_before B`: B darf nicht vor dem Ende von A starten (`B.start_date ≥ A.target_date`, Finish-to-Start); `A blocked_by B`: wie Finish-to-Start von B nach A, aber ohne Datumsautomatik (nur Hinweis).
4. **Gantt:** Verbindungslinien (Pfeile) zwischen Balken für Dependencies; Erzeugen durch Ziehen eines Griffs am Balken auf einen anderen Balken (CE-Stub `getIsCurrentDependencyDragging(blockId)` – „Dummy method to return if the current Block's dependency is being dragged“, `apps/web/store/timeline/base-timeline.store.ts` Z. 344–345); beim Verschieben/Resizen eines Balkens werden **abhängige Balken mitverschoben**, sofern nicht `ignoreDependencies` (Signaturen `getUpdatedPositionAfterDrag(id, shouldUpdateHalfBlock, ignoreDependencies?) => IBlockUpdateDependencyData[]` und `updateBlockPosition(id, deltaLeft, deltaWidth, ignoreDependencies?)`, Z. 59–64; CE liefert nur den gezogenen Block, Z. 296–318); Speichern aller geänderten Daten in **einem** Request `POST /api/workspaces/{slug}/projects/{pid}/issue-dates/` mit `{updates: [{id, start_date?, target_date?}]}` (CE-Endpunkt vorhanden, `apps/web/services/issue/issue.service.ts` Z. 247; `apps/api/plane/app/urls/issue.py` Z. 252–254). Flag `isDependencyEnabled` (CE `false`, Z. 85); Issue-Gantt übergibt bereits `enableDependency` (`apps/web/components/issues/issue-layouts/gantt/base-gantt-root.tsx` Z. 149), `ChartDraggable` nimmt `enableDependency` entgegen, rendert aber keine Griffe (`apps/web/components/gantt-chart/helpers/draggable.tsx`). Typ `IBlockUpdateDependencyData { id; start_date?; target_date?; meta? }` (`packages/types/src/layout/gantt.ts` Z. 37–42).
5. **Frontend-Typen erweitern:** `TIssueRelationTypes = "blocking" | "blocked_by" | "duplicate" | "relates_to"` (`packages/types/src/issues/issue_relation.ts` Z. 17) und `ISSUE_RELATION_OPTIONS`/`useTimeLineRelationOptions` (`apps/web/components/relations/index.tsx`, Schema `{key, i18n_label, className, icon(size), placeholder}`) um die Dependency-Typen ergänzen. Icons: `CalendarBeforeIcon`, `CalendarAfterIcon` (`packages/blocks/src/icons/calendar-before-icon.tsx`, `calendar-after-icon.tsx`), Propel `DependencyOutline/Filled`.

**CE-Status:** teilweise (Backend vollständig für Speicherung/Lesen; UI/Gantt fehlen). **Edge-Cases (CE-Bugs, korrigieren):** (a) `implements` wird zu `implemented_by` gemappt, aber **ohne Vertauschung** von `issue`/`related_issue` (Vertauschung nur für `blocking`, `start_after`, `finish_after`, `relation.py` Z. 270–272) ⇒ Richtung kehrt sich um; (b) die Lese-Antwort enthält keine `implements`/`implemented_by`-Listen. **Quellen:** R1, R6, R8, R13, R14, R17, D2, D4. **Konfidenz:** hoch (Speicherung, Stubs) / mittel (Gantt-Interaktion, Zeitsemantik).

#### WM-27 – Custom Relations (Relationsdefinitionen)

**Tier:** UNVERIFIZIERT (Blog „New work item detail view, custom relations and more“, W via Dok 25 W20). **Funktionsbeschreibung:** Workspace-Settings **„Relations“** – „Create and manage relation types that connect work items across your workspace.“ (`workspace_settings.settings.relations.*`, R5 Z. 277–281). Definition: `name`*, `outward` (Label in Vorwärtsrichtung), `inward` (Label in Rückrichtung), `is_active`, `color`; Listen-Filter `is_default`, `is_active` ⇒ es gibt **Standard-Definitionen** (Vermutung: „Relates to“, „Duplicate of“, „Implements“/„Implemented By“) neben eigenen (D2 Z. 142–156). Relation anlegen mit `relation_definition_id` + `relation_definition_label` (das gewählte Outward- oder Inward-Label bestimmt die Richtung). Löschen einer Relation mit `is_dependency=false`. CE kennt `implemented_by`/`implements` als Enum (R13 Z. 278, 290; Icons `ImplementsOutline/Filled`, `ImplementedByOutline/Filled`, `RelationsOutline/Filled`). **Datenmodell (Vorschlag):** `relation_definition(id, workspace_id, name, outward, inward, color, is_active, is_default, sort_order)`, `work_item_relation(id, source_id, target_id, definition_id, …, Unique(source_id, target_id, definition_id))` getrennt von `work_item_dependency(source_id, target_id, type)`. **CE-Status:** teilweise (Enum). **Konfidenz:** mittel.

---

### 3.11 Cycles & Modules: Auto-Transfer, Auto-Schedule, Module Overview, Auto-Assignment

#### WM-28 – Auto-transfer Cycle Work Items (Auto-Rollover)

**Tier:** Pro, Business, Enterprise ✓ („Transfer incomplete work items from a completed cycle to the next cycle or to the default project state.“, R1 Z. 249–259).

**Funktionsbeschreibung:** Option **„Auto-rollover work items“** mit Tooltip „On the day a cycle completes, move all unfinished work items into the next cycle.“ im Formular „Auto-schedule cycles“ (R4 Z. 491–494). Laut Matrix alternativ Rückführung „to the default project state“ (Bedeutung UNVERIFIZIERT: Items verlassen den Cycle und werden in den Default-State gesetzt? oder nur aus dem Cycle entfernt). **Verhalten (Vorschlag):** Hintergrundjob am Ende-Tag des Cycles (Projekt-Zeitzone, nach `end_date`): Ziel = nächster Cycle nach `start_date` (nicht abgeschlossen); Logik = CE-`transfer_cycle_issues` (nur State-Gruppen `backlog`/`unstarted`/`started`, Progress-Snapshot des Quell-Cycles, Activity) (R22); existiert kein nächster Cycle und ist Auto-Schedule aktiv, wird er vorher erzeugt (WM-29). **CE-Status:** fehlt (manueller Transfer vorhanden, WM-23). **Konfidenz:** mittel.

#### WM-29 – Auto-schedule Cycles (Kontext)

**Tier:** UNVERIFIZIERT; Changelog v1.16.0 „milestones and recurring cycles“ (W via Dok 25 W49). **Funktionsbeschreibung (R4 Z. 442–524, vollständig):** Abschnitt auf der Cycles-Feature-Seite „Auto-schedule cycles“ – „Keep cycles moving without manual setup.“, Tooltip „Automatically create new cycles based on your chosen schedule.“, Button „Edit“. Formular: **„Cycle Title“** (Placeholder „Title“; Tooltip „The title will be appended with numbers for subsequent cycles. For eg: Design - 1/2/3“; Pflicht „Cycle title is required“; „Title must not exceed 255 characters“), **„Cycle Duration“** in „Weeks“ (Pflicht „Cycle duration is required“, min „Cycle duration must be at least 1 week“, max „Cycle duration cannot exceed 30 weeks“, „Cycle duration must be positive“), **„Cooldown Period“** in „days“ (Tooltip „Pause between cycles before the next begins.“; Pflicht „Cooldown period is required“; „Cooldown period cannot be negative“), **„Cycle starts day“** (Pflicht „Start date is required“; „Start date cannot be in the past“), **„Number of future cycles“** (Pflicht „Number of cycles is required“; min „At least 1 cycle is required“; max „Cannot schedule more than 3 cycles“), **„Auto-rollover work items“** (WM-28). Toasts: Toggle „Enabling auto-schedule cycles“ / „Disabling auto-schedule cycles“, „Auto-schedule cycles toggled successfully.“, „Failed to toggle auto-schedule cycles.“; Speichern „Saving auto-schedule cycles configuration“, „Auto-schedule cycles configuration saved successfully.“ / „…updated successfully.“, „Failed to save …“ / „Failed to update …“. **Verhalten (abgeleitet):** Es existieren stets `n` (1–3) zukünftige Cycles; Cycle k: `start = start_day + (k-1)·(Dauer·7 + Cooldown)` Tage, `end = start + Dauer·7 − 1`; Titel „{Titel} - {laufende Nummer}“. **Datenmodell (Vorschlag):** `cycle_schedule(project_id PK, is_enabled, title, duration_weeks 1–30, cooldown_days ≥0, start_date, future_count 1–3, auto_rollover bool, next_sequence int)`. **CE-Status:** fehlt (CE-Seite `…/features/cycles/page.tsx` hat nur den Toggle „Enable cycles“). **Konfidenz:** hoch (Formular) / mittel (Berechnung).

#### WM-30 – Module Overview

**Tier:** Pro, Business, Enterprise ✓ („Like Cycle Overviews, see relevant details and progress charts for each module.“, R1 Z. 297–306). **Im CE vorhanden:** Modul-Peek (rechte Sidebar) mit Details, Fortschrittsdiagramm (Burndown über `ProgressChart`, Umschaltung Work Items ↔ Punkte bei Punkte-Schätzung, `moduleBurnDownChartOptions`), Verteilungen nach Assignees/Labels/States (`apps/web/components/modules/analytics-sidebar/{root,issue-progress,progress-stats}.tsx`, `apps/web/components/modules/module-peek-overview.tsx`). **Bezahl-Mehrwert:** nur Matrix-Text; analog zur Cycle-Übersicht vermutlich eine eigene Übersichtsseite/-ansicht je Modul mit größeren Fortschrittsdiagrammen (Progress Charts ab Pro, R1 Z. 538–548). **Vorschlag:** Modul-Detailseite mit Tab „Overview“ (Icon `OverviewOutline`), die die Sidebar-Komponenten großformatig rendert (Stats-Kacheln, Burndown, Verteilung nach State/Assignee/Label, Links). **CE-Status:** teilweise. **Konfidenz:** niedrig.

#### WM-31 – Auto-assignment in Modules

**Tier:** Pro „Linear“; Business/Enterprise „Round-robin and Capacity“ (R1 Z. 308–317: „Choose assignment rules for work items in a module including Linear, Round Robin, or Capacity.“). **Belege:** nur Matrix-Text; im CE existieren Modul-Lead und -Mitglieder (`ModuleMember`, `apps/api/plane/db/models/module.py` Z. 131–132; MCP `module create … lead, members`, D2 Z. 264). **Vorschlag (UNVERIFIZIERT, Rückfrage R-07):** Modul-Einstellung `assignment_rule ∈ {none, linear, round_robin, capacity}`, angewendet beim Hinzufügen eines Work Items **ohne Assignee** zum Modul: *Linear* = immer der Modul-Lead (oder erstes Mitglied in fester Reihenfolge); *Round Robin* = reihum über die Modul-Mitglieder (Zeiger je Modul); *Capacity* = Mitglied mit der geringsten offenen Last (Summe Estimate-Punkte bzw. Anzahl offener Items im Modul, optional gegen eine Kapazitätsgrenze je Mitglied). **CE-Status:** fehlt. **Konfidenz:** niedrig.

---

### 3.12 Time Tracking, Worklogs, Timesheets, Approvals

#### WM-32 – Time Tracking + Worklogs

**Tier:** One „Basic“; Pro „Historical timesheets“; Business/Enterprise „Historical timesheets and approvals“ (R1 Z. 183–192: „Track time per work item, see aggregated reports, and filter by need.“); Highlights One „Limited time tracking“, Pro „Full Time Tracking“ (R1 Z. 1305–1306); W docs.plane.so/core-concepts/issues/time-tracking mit Label „Pro“ (via Dok 21 §3 F07).

**Funktionsbeschreibung (UI & Verhalten):**
1. **Aktivierung je Projekt:** Projekt-Settings-Feature „Time tracking“ – „Log time spent on work items and projects.“, Toggle „Enable time tracking“ – „Project members will be able to log time worked.“ (R4 Z. 413–419); Feld `Project.is_time_tracking_enabled` (R12 Z. 100; auch in der CE-Public-API, `apps/api/plane/api/serializers/project.py` Z. 94; MCP `project update is_time_tracking_enabled`, D2 Z. 371); Projekt-Activity „enabled/disabled time tracking“ mit Icon `TimeTrackingOutline` (R21 Z. 70, 278–281).
2. **Work-Item-Property „Tracked time“** in der Property-Sidebar (Detail/Peek) mit Stoppuhr-Icon; Wert = Summe aller Worklogs im Format „{h}h {m}m“ (z. B. „0h 0m“, „2h 45m“) (Referenz-Screenshots `/home/user/makeplane/developer-docs/docs/public/images/time-tracking/log-work.webp`, `worklog-created.webp`; W „Property ‚Tracked time‘ aktualisiert sich“, via Dok 21 §4.6).
3. **„Log work“:** Textbutton „+ Log work“ rechts im Activity-Kopf (neben „Filters“). Öffnet ein Popover mit (a) Vorschau-Chip mit Stoppuhr-Icon und der berechneten Dauer (z. B. „2h 15m“), (b) zwei Zahlenfeldern nebeneinander für **Stunden** und **Minuten**, (c) mehrzeiliger Beschreibung, (d) Buttons „Cancel“ / „Save“ (Screenshot `log-work.webp`). Erfolgs-Toast „Success!“ – „Worklog created successfully.“ (Screenshot `worklog-created.webp`). Gespeichert wird `duration` in **Minuten** = `h·60 + m` (D1 `worklogs/overview.md`; D2 Z. 169).
4. **Activity-Eintrag:** Avatar mit Stoppuhr-Badge, Text „{Name} logged {Dauer}. {relative Zeit}“ (z. B. „logged 2h 15m . 1 minute ago“), Beschreibung in umrandetem Block darunter, „…“-Menü je Eintrag (Bearbeiten/Löschen; W „Einträge in der Activity bearbeit-/löschbar“, via Dok 21 §4.6). Activity-Typ `WORKLOG` (`packages/types/src/issues/activity/base.ts` Z. 80–83). Activity-Tabs der aktuellen Generation: „All“, „Comments“, „History“, „Transitions“, „Worklogs“ (W via Dok 25 F06/W20); Leerzustand „No worklogs yet“ (`common.activity_empty_state.no_worklogs`, R8 Z. 58).
5. **Erfassung für Dritte:** `created_by`/`updated_by` im Body erlaubt (D1 `worklogs/create-worklog.md`), `logged_by` RO; W „record time by members and guests“ (via Dok 21 §4.6) ⇒ Gäste dürfen ebenfalls loggen (UNVERIFIZIERT, Rechte-Matrix O-08).
6. **Projekt-Summe:** `GET …/projects/{project_id}/total-worklogs/` → `[{issue_id, duration}]` (D1 `worklogs/get-total-time.md`; MCP `project worklog_summary`, D2 Z. 375).

**Datenmodell (D1 `worklogs/overview.md`):** `id, description (Default ""), duration (int, Minuten), logged_by (RO), project_id, workspace_id, created_at, updated_at, deleted_at, created_by, updated_by` (+ implizit `issue_id`). **Vorschlag EF:** `work_item_worklog(id, workspace_id, project_id, work_item_id, logged_by_id, duration_minutes int CHECK > 0, description text, logged_at date (Default heute; für Timesheets, UNVERIFIZIERT ob separat), Audit, deleted_at)`; Index `(workspace_id, logged_by_id, created_at)`, `(project_id, work_item_id)`.

**API (Commercial v1, Scope `projects.work_items.worklogs:*`):** `GET/POST /api/v1/workspaces/{slug}/projects/{project_id}/work-items/{work_item_id}/worklogs/`, `PATCH/DELETE …/worklogs/{worklog_id}/`, `GET …/projects/{project_id}/total-worklogs/`. Interne Web-App-Pfade nicht belegt.

**CE-Status:** teilweise (Flag, Activity-Typ, Export-Typ `issue_worklogs` in `ExporterHistory.type`, `apps/api/plane/db/models/exporter.py` Z. 27–33; keine Tabelle/Endpunkte/UI). **Konfidenz:** hoch.

#### WM-33 – Timesheets / Worklog-Downloads (Workspace)

**Tier:** Pro „Historical timesheets“ (R1 Z. 188).

**Funktionsbeschreibung:**
1. Workspace-Settings-Seite **„Worklogs“** – „Download worklogs AKA timesheets for anyone in any project.“ (R5 Z. 187–191). Leerzustand „Track timesheets for all members“ – „Log time on work items to view detailed timesheets for any team member across projects.“ (`settings_empty_state.worklogs`, R7 Z. 248–251; Illustration `worklog`, horizontal-stack).
2. **Filterleiste** (Screenshot `/home/user/makeplane/developer-docs/docs/public/images/time-tracking/view-worklogs.webp`, `filter-and-download-worklogs.webp`): Dropdown „Users“ (Mehrfachauswahl Mitglieder), Dropdown „Projects“ (Mehrfachauswahl), Datumsbereich „Start date → End date“.
3. **Tabelle** mit Spalten **Project | Work item** (Screenshot: „Issue“, ältere Generation) **| Logged | Time**: Projektname; Identifier + Titel; Avatar + Name + „on {Datum}“ (z. B. „on Sep 12, 2024“); Dauer („30m“, „2h 15m“, „1h 2m“). Pagination „{von}-{bis} of {gesamt}“ mit Buttons „Prev“/„Next“.
4. **Download:** Split-Button „Download“ mit Dropdown **„Excel“** / **„CSV“** (Screenshot); erzeugt einen asynchronen Export (`ExporterHistory.type = "issue_worklogs"`, `provider ∈ {csv, xlsx}`, Status queued → processing → completed/failed, Download-URL, Filter in `filters`/`rich_filters`; `apps/api/plane/db/models/exporter.py`). Abschnitt **„Previous Downloads“** (einklappbar) mit Liste früherer Exporte und Leerzustand „No worklog downloads found“, eigene Pagination (Screenshot). Hinweis: Der CE-Export-Endpunkt filtert hart auf `type="issue_exports"` (`apps/api/plane/app/views/exporter/base.py` Z. 47, 70) – Worklog-Exporte benötigen eigene Endpunkte.
5. „Historical“: Zugriff auf beliebige vergangene Zeiträume (Abgrenzung zu „Basic“ in One nicht belegt; nach ADR-001 unbeschränkt).
6. Älterer Feature-Text (Screenshot `enable-time-tracking.webp`, Projekt-Features-Abschnitt „Work management“): „Log time, see timesheets, and download full CSVs for your entire workspace.“ – in der aktuellen i18n ersetzt durch R4-Texte; der Hinweis „Available only on some plans as indicated by the label next to the feature below.“ entfällt (ADR-001).

**Export-Spalten (Vorschlag, UNVERIFIZIERT):** Project, Work item ID, Work item title, Logged by (Name, E-Mail), Logged on (Datum), Duration (h:mm und Minuten), Description. **API (Vorschlag):** `GET /api/workspaces/{slug}/worklogs/?logged_by__in=&project_id__in=&created_at__gte=&created_at__lte=&cursor=&per_page=`, `POST /api/workspaces/{slug}/worklogs/downloads/` (`{provider, filters}`), `GET …/worklogs/downloads/`. **Rechte:** Workspace-Admin sieht alle; Member nur eigene (UNVERIFIZIERT). **CE-Status:** fehlt. **Konfidenz:** hoch (UI-Struktur aus Screenshots) / mittel (Rechte, Spalten).

#### WM-34 – Timesheet-Approvals

**Tier:** Business, Enterprise („Historical timesheets and approvals“, R1 Z. 189–190); Upsell-Text „Dashboards, Workflows, Approvals, Time Management, and other superpowers are just a click away.“ (`apps/web/components/license/modal/upgrade-modal.tsx` Z. 70). **Belege:** nur Matrix-Text. **Vorschlag (UNVERIFIZIERT, Rückfrage R-08):** Wochen-Timesheet je Mitglied (Summe der Worklogs je Tag/Projekt) mit Status `draft → submitted → approved | rejected`; Approver = Projekt-Admin bzw. konfigurierte Approver; nach Approval sind die enthaltenen Worklogs gesperrt (keine Bearbeitung/Löschung); Benachrichtigungen bei Submit/Entscheidung; Inbox-Eintrag (vgl. „Your inbox keeps all mentions, approvals, and activity in one place“, Dok 20 PF-56). **CE-Status:** fehlt. **Konfidenz:** niedrig.

---

### 3.13 Advanced Estimates

#### WM-35 – Advanced Estimates (Time, Bearbeiten, Umsortieren, Systemwechsel)

**Tier:** Free/One „Basic“; Pro/Business/Enterprise „Advanced“ (R1 Z. 145–154 „Measure effort in points in a system that works for you.“).

**Im CE vorhanden („Basic“):** Systeme `points` (Templates Fibonacci 1,2,3,5,8,13; Linear 1–6; Squares 1,4,9,16,25,36; Custom) und `categories` (T-Shirt Sizes XS–XXL; Easy to hard: Easy, Medium, Hard, Very Hard; Custom); 2–6 Werte (`estimateCount`), Wert ≤ 20 Zeichen (`MAX_ESTIMATE_POINT_INPUT_LENGTH`); Anlegen, Löschen, Aktivieren/Deaktivieren (`packages/constants/src/estimates.ts`; `apps/web/components/estimates/**`). Backend kennt bereits `PATCH` für Estimate und Estimate-Punkte (`apps/api/plane/app/urls/estimate.py`), Modell nur `categories`/`points` (`apps/api/plane/db/models/estimate.py` Z. 13–15).

**Bezahl-Funktionen:**
1. **System „Time“** (`ESTIMATE_SYSTEMS.time`, `is_ee: true`, Template „Hours“ mit Werten 1–6; i18n „Time“, „Hours“, R4 Z. 159–162). Im CE wird `time` in der Auswahl ausgefiltert (`isEstimateSystemEnabled` erlaubt nur points/categories, `apps/web/components/estimates/create/helper.tsx`), Eingabe-Komponente für TIME leer (`apps/web/components/estimates/inputs/root.tsx`). Die Template-Vorschau formatiert Time-Werte mit `convertMinutesToHoursMinutesString(Number(value))` (`create/stage-one.tsx`) ⇒ **Time-Werte sind Minuten**; die CE-Template-Werte 1–6 würden als „1m“…„6m“ erscheinen – Widerspruch zum Titel „Hours“ (UNVERIFIZIERT; Vorschlag: Template-Werte 60…360 Minuten, Anzeige „1h“…„6h“; Eingabe in Stunden + Minuten wie beim Worklog). API/MCP: `type ∈ {categories, points, time}` (D2 Z. 230).
2. **Bearbeiten** eines bestehenden Systems: Dialog „Edit estimate system“ mit zwei Optionen: **„Add, update or remove estimates“** – „Manage current system either adding, updating or removing the points or categories.“ und **„Change estimate type“** – „Convert your points system to categories system and vice versa.“ (R4 Z. 164–175). Im CE fehlt der Edit-Button (`EstimateListItemButtons` rendert nur Löschen; `onEditClick` ungenutzt, `apps/web/components/estimates/estimate-list-item-buttons.tsx`).
3. **Systemwechsel:** „Switch estimate system“, „Current estimate system“, „Select an estimate system“ (R4 Z. 176–178); Toasts „Estimate system created“ – „Created and Enabled successfully“ bzw. „Error“ – „Something went wrong“ (R4 Z. 122–131); Stufen `EEstimateUpdateStages` = `create`, `edit`, `switch` (`packages/constants/src/estimates.ts`). Beim Wechsel müssen Work-Item-Schätzungen umgemappt werden (Regel UNVERIFIZIERT; Vorschlag: Zuordnung über `key` (Sortierposition), überzählige → leer).
4. **Umsortieren:** Toasts „Estimates re-ordered“ – „Estimates have been re-ordered in your project.“ / „Estimate re-order failed“ – „We were unable to re-order the estimates, please try again“ (R4 Z. 112–121); `key` = Sortierposition (D2 Z. 230).
5. **Validierung** (R4 Z. 133–144): „Estimate needs to be greater than 0.“, „We are unable to process your request, please try again.“, „Estimate needs to be a numeric value.“, „Estimate needs to be a character value.“, „Estimate value cannot be empty.“, „Estimate value already exists.“, „You have some unsaved changes, Please save them before clicking on done“, „Estimate can't be empty. Enter a value in each field or remove those you don't have values for.“, „Please fill this estimate field“, „Estimate value cannot be repeated“.
6. **Aktive Schätzung festlegen:** MCP `project_estimate link` „makes that estimate the project's active one“ (D2 Z. 224) ⇒ mehrere Systeme je Projekt möglich, eines aktiv (`Project.estimate`).
7. Analytics/Cycle-Burndown nutzen bei `points` Punkte statt Anzahl (CE); für `time` analoge Summen in Minuten (UNVERIFIZIERT).

**Datenmodell:** `EstimateType` um `time` erweitern; `EstimatePoint.value` bei `time` = Minuten als String. **API:** Commercial-Estimate-API in Dok 21 §2.5 (CE-Code vorhanden, nicht geroutet). **CE-Status:** teilweise. **Konfidenz:** hoch (Texte/Konstanten) / mittel (Time-Werteinheit, Mapping).

---

### 3.14 Projekte: Sichtbarkeit, Project States, Project Labels, Overview, Updates, Templates

#### WM-36 – Public, Private und Secret Projects

**Tier:** Pro, Business, Enterprise ✓ (R1 Z. 331–341: „Public projects are visible and accessible to everyone. Private ones are visible but need approval to join. Secret projects aren't visible or accessible.“).

**Im CE vorhanden:** zwei Stufen `ProjectNetwork.SECRET = 0`, `PUBLIC = 2` (R12 Z. 30–36, 71, 76; Default `2`); UI-Labels **„Private“** („Accessible only by invite“) für `0` und **„Public“** („Anyone in the workspace except Guests can join“) für `2`, Icons `Lock`/`Globe2` (`packages/constants/src/project.ts` Z. 11–36; `workspace_projects.network.*`, `packages/i18n/src/locales/en/workspace.json` Z. 158–165). Workspace-Members sehen Projekte, in denen sie Mitglied sind, oder mit `network=2` (`apps/api/plane/app/views/project/base.py` Z. 117–129, 215–224); Nicht-Mitglied öffnet Projekt: `SECRET` → 403 „You do not have permission“, sonst 409 „You are not a member of this project“ (Z. 234–245) → Join-Screen „Seems like you don’t have access to this Project“ mit „Click the button below to join it.“ / Button „Join project“ („Joining project“) bzw. „Contact admin to request for access and you can continue here.“ (`project_empty_state.no_access.*`, R7 Z. 27–33). Self-Join: `POST /api/users/me/workspaces/{slug}/projects/invitations/` mit `project_ids`; Secret-Projekte nur für Workspace-Admins („Only workspace admins can join private project“), Rolle = Workspace-Rolle (`apps/api/plane/app/views/project/invite.py` Z. 118–190).

**Bezahl-Funktion:** dritte Stufe **Private = sichtbar, Beitritt nur nach Genehmigung**; CE-„Private“ (Wert 0) entspricht fachlich **Secret** (nicht sichtbar). Wert für „Private“: vermutlich `1` (Lücke im Enum; Public-API dokumentiert nur „`0` for secret, `2` for public“, D1 `project/create-project-with-template.md`, D2 Z. 379) – UNVERIFIZIERT. Plane Compose kennt `network: public | private` (D3 `plane.yaml`). **Verhalten (Vorschlag):** Private-Projekte erscheinen in der Projektliste/Projekt-Browser mit Schloss-Badge; Nicht-Mitglieder sehen Name/Beschreibung/Lead, aber keine Inhalte; Button „Request to join“ erzeugt eine Beitrittsanfrage; Projekt-Admins erhalten Inbox-Benachrichtigung und genehmigen/ablehnen (Projekt-Settings → Members, Tab „Requests“); bei Genehmigung Rolle = Default-Rolle. UI-Texte für Anfrage/Genehmigung fehlen im CE-i18n (O-04). **Datenmodell (Vorschlag):** `network ∈ {0 secret, 1 private, 2 public}`; `project_join_request(id, project_id, user_id, status pending|approved|rejected, message, decided_by, decided_at)`. **CE-Status:** teilweise. **Konfidenz:** mittel (Semantik) / niedrig (UI).

#### WM-37 – State of Projects / Project States (Project Grouping)

**Tier:** Pro, Business, Enterprise ✓ („State Of Projects – See all projects laid across states that highlight those that need attention and those on track.“, R1 Z. 343–353); Workspace-Feature `project_grouping` (D1 `workspace-features`).

**Funktionsbeschreibung:**
1. Workspace-Settings **„Projects“** – „Manage project states, and enable project labels, and other configuration.“ mit Tabs **„Project states“** / **„Project labels“** (R5 Z. 264–271). Hinweisbox „Project states“: Überschrift „See progress overview for all projects.“, Text „Project States is a Plane-only feature for tracking progress of all your projects by any project property.“, CTA „Go to settings“ (R5 Z. 258–263). Ältere Generation: Workspace-Settings-Eintrag „Project States“ (Screenshot `view-worklogs.webp`, linke Navigation).
2. **Default-Projekt-States:** Draft, Planning, Execution, Monitoring, Completed, Cancelled; erweiterbar (W Plane University „Intro to project states“, via Dok 21 §4.12). Projekt-Template-Blueprint enthält `project_state {id, name, group}` (via Dok 25 F20) ⇒ Projekt-States haben eine **Gruppe** (Werte UNVERIFIZIERT; Vorschlag: die sechs Default-States sind zugleich die Gruppen `draft`, `planning`, `execution`, `monitoring`, `completed`, `cancelled`; weitere States werden einer Gruppe zugeordnet, analog Work-Item-States).
3. **Projekt-Properties:** Leerzustand der Projekt-Overview-Sidebar „Enable project states“ – „Enable Project States to view and manage properties like state, priority, due dates and more.“ (`workspace_empty_state.project_overview_state_sidebar`, R7 Z. 194–197) ⇒ mit aktivem Feature erhalten Projekte **State, Priority, Start-/Due-Date** (und weitere Properties) in einer Sidebar der Projekt-Übersicht.
4. **Projektliste nach States:** Projekte gruppiert/gefiltert nach State; Hervorhebung „need attention“ vs. „on track“ (Matrix-Text; Kriterium UNVERIFIZIERT, Vorschlag: Projekt-Update-Status WM-40 bzw. Überfälligkeit). Workspace-Analytics-Kachel „Projects by status“ (`workspace_analytics.projects_by_status`, `packages/i18n/src/locales/en/workspace.json` Z. 149; im CE ungenutzt).
5. API für Projekt-States nicht dokumentiert (D1 nur Project Labels).

**Datenmodell (Vorschlag):** `project_state(id, workspace_id, name, color, group, sequence, is_default, description)`; Projekt-Spalten `state_id`, `priority`, `start_date`, `target_date` (nur aktiv, wenn `project_grouping` an). **CE-Status:** fehlt (CE-Komponenten `apps/web/components/project-states/*` betreffen Work-Item-States). **Konfidenz:** mittel.

#### WM-38 – Project Labels

**Tier:** UNVERIFIZIERT; Changelog v2.5.0 „Project labels …“ (W via Dok 26 W44). **Funktionsbeschreibung:** Workspace-Katalog von Labels für **Projekte** (Tab „Project labels“, R5 Z. 267–270), Zuordnung mehrerer Labels je Projekt, Filter/Gruppierung der Projektliste nach Label; Label-Dropdown im Scope `project` (`label-select.tsx` Z. 48–49). **Datenmodell (D1 `project-labels/overview.md`):** `id, name*, description, color (Hex), sort_order (Beispiel 65535), workspace, created_at, updated_at, created_by, updated_by`. **API (Scope `projects.labels:*`):** `GET/POST /api/v1/workspaces/{slug}/project-labels/`, `GET/PATCH/DELETE …/project-labels/{label_id}/`; Zuordnung Projekt↔Label nicht dokumentiert (Vorschlag: Feld `label_ids` am Projekt). **CE-Status:** fehlt. **Konfidenz:** mittel.

#### WM-39 – Project Overview

**Tier:** Pro (Zeile auskommentiert, „Coming soon“; „See just-in-time snapshots of your project with essential metrics.“, R1 Z. 318–329). **Funktionsbeschreibung:** Projekt-Übersichtsseite (Power-K „Go to project overview“, `power_k.navigation_actions.nav_project_overview`, `packages/i18n/src/locales/en/power-k.json`; Icon `OverviewOutline/Filled`, project-features) mit: Projekt-Kopf (Cover, Logo, Name, Rich-Text-Beschreibung – Asset-Typ `PROJECT_DESCRIPTION`, `packages/types/src/enums.ts` Z. 73), Kennzahlen (Work Items je State-Gruppe, Cycles, Module, Mitglieder – vgl. CE `TProjectAnalyticsCount`, `packages/types/src/project/projects.ts`), einklappbaren Abschnitten **„milestones“** (Default offen), **„links“**, **„attachments“** (`ProjectOverviewCollapsible`, `openCollapsibleSection`, `lastCollapsibleAction`, `toggleOpenCollapsibleSection`, `apps/web/store/project/project.store.ts` Z. 21, 47–52, 86–87, 274 ff.), Update-Feed (WM-40) und State-Sidebar (WM-37). **Projekt-Links:** Typ `TProjectLink { id, title, url, metadata, project_id, created_by_id, created_at }` (`packages/types/src/project/project_link.ts`) – keine CE-Endpunkte. **Datenmodell (Vorschlag):** `project_link(id, project_id, title, url, metadata jsonb)`, `project_attachment` (über FileAsset mit Entity-Typ Projekt). **CE-Status:** Stub/UI-Hülle. **Konfidenz:** mittel (Sektionen) / niedrig (Kennzahlen).

#### WM-40 – Project Updates

**Tier:** Pro (Zeile auskommentiert, „Coming soon“; „Keep stakeholders in the loop with a dedicated space for updates that everyone in the project can see.“, R1 Z. 354–366). **Funktionsbeschreibung:** Projekt-Feature-Toggle `project_updates` (MCP/Compose) bzw. Projekt-Feld `is_project_updates_enabled` mit Activity „enabled/disabled project updates“ (Icon `SubscribeOutline`, R21 Z. 67, 266–269); Settings-Seite „Project Updates“ – „Consolidated tracking and progress monitoring for this project“ (R4 Z. 433–436; `common.project_updates`, R8 Z. 711); Update-Feed mit Status On-Track/Off-Track/At-Risk, Fortschritt „Since last update“, Kommentaren, Reaktionen – Texte und Datenmodell siehe WM-10 (`entity_type = project`). Leerzustand „No updates yet.“ – „Once project members add updates it will appear here“ (R7 Z. 7–10). **CE-Status:** Stub/UI-Hülle. **Konfidenz:** mittel.

#### WM-41 – Project Templates

**Tier:** Business, Enterprise (R1 Z. 392–401 „Save states, workflows, automation, and other project settings into templates.“; `BUSINESS_PLAN_FEATURES` „Project Templates“; Highlight Business, R1 Z. 1307). **Kurzspezifikation:** siehe **Dok 25 F20** (Formular, `template_data` mit Feature-Toggles inkl. `is_time_tracking_enabled`, `is_issue_type_enabled`, `is_project_updates_enabled`, `is_epic_enabled`, `is_milestone_enabled`, States, `project_state`, Labels, Estimates, Work Item Types inkl. Properties, Epics, Intake-Settings `{is_in_app_enabled, is_email_enabled, is_form_enabled}`, Milestones, Module, Recurring Work Items, Starter-Work-Items). Commercial-v1-Endpunkt `POST /api/v1/workspaces/{slug}/projects/templates/use/` (`template_id`*, `name`, `identifier`, `description`, `network` 0/2, `project_lead` → wird Projekt-Admin; kopiert States, Labels, Estimates, Module, Work Items; D1 `project/create-project-with-template.md`); Projekt-Objekt trägt `template_id` (D1 `project/overview.md` Z. 134). **CE-Status:** Stub/UI-Hülle (`templateId`-Props in `apps/web/components/project/create-project-modal.tsx` Z. 27, 36, 82 und `apps/web/components/projects/create/root.tsx` Z. 33 ohne Wirkung). **Konfidenz:** mittel.

---

### 3.15 Baselines & Deviations, Custom SLAs

#### WM-42 – Baselines And Deviations

**Tier:** Business, Enterprise (R1 Z. 403–412 „Declare baselines for how your projects progress and zoom in on deviations.“; Highlight Business „Baselines And Deviations“, R1 Z. 1307). **Belege:** ausschließlich Matrix-Text; keine Spuren in Repo (`grep -rniE "baseline|deviation"` nur Theme-/CSS-Treffer), D1–D7 oder den Web-Zusammenfassungen. **Vorschlag (UNVERIFIZIERT, Rückfrage R-09):** *Baseline* = benannter, datierter Snapshot der Planwerte eines Projekts (je Work Item `start_date`, `target_date`, Estimate, Cycle/Modul/Milestone-Zuordnung; je Cycle/Modul/Milestone Daten; Gesamtumfang). *Deviations* = Vergleich aktueller Werte mit einer gewählten Baseline: Gantt-Overlay (Baseline-Balken grau hinter aktuellem Balken), Liste der Abweichungen (Verzug/Vorlauf in Tagen, Scope hinzugefügt/entfernt, Schätzungsänderung), Kennzahlen (Termintreue, Scope-Creep). **Datenmodell (Vorschlag):** `project_baseline(id, project_id, name, description, created_by, created_at, is_active)`, `project_baseline_item(baseline_id, entity_type, entity_id, start_date, target_date, estimate_value, cycle_id, module_ids, milestone_id)`. **CE-Status:** fehlt. **Konfidenz:** niedrig.

#### WM-43 – Custom SLAs

**Tier:** Business, Enterprise (R1 Z. 436–445 „Set SLA matrices for time-sensitive work items.“). Nicht verwechseln mit dem **Support-SLA** der Pläne (R1 Z. 1235–1251: „SLAs are by priority of work item and tiers can be requested“ – betrifft den Hersteller-Support, entfällt nach ADR-001). **Belege:** nur Matrix-Text; Propel-Icon `TimeInStateOutline/Filled` (properties) und „Time in state“-Badges (Dok 25 F06) als mögliche Bausteine – Zuordnung UNVERIFIZIERT. **Vorschlag (UNVERIFIZIERT, Rückfrage R-10):** SLA-Richtlinie je Projekt (oder Workspace) als **Matrix** Priorität × (optional) Work Item Type/Label/Customer-Stufe → Zielzeiten **First response** (bis erster Kommentar/Zuweisung) und **Resolution** (bis State-Gruppe `completed`), in Arbeitszeit oder Kalenderzeit; Uhr pausiert in konfigurierbaren States (z. B. „Waiting for customer“); Anzeige als SLA-Badge mit Restzeit/Überschreitung am Work Item, Filter „SLA breached“, Benachrichtigung bei drohendem Bruch (z. B. 80 %) und Bruch. **Datenmodell (Vorschlag):** `sla_policy(id, project_id, name, is_active, business_hours jsonb, paused_state_ids uuid[])`, `sla_policy_rule(policy_id, priority, work_item_type_id NULL, label_id NULL, response_minutes, resolution_minutes)`, `work_item_sla(work_item_id, policy_rule_id, response_due_at, resolution_due_at, responded_at, resolved_at, paused_minutes, breached_flags)`. **CE-Status:** fehlt. **Konfidenz:** niedrig.

---

### 3.16 Intake: Forms, Assignees, E-Mail

Gemeinsame Basis im CE: Intake-Feature, Zustandsmaschine (Pending −2, Rejected −1, Snoozed 0, Accepted 1, Duplicate 2) und Triage-State (Kern-Analyse `migration/analysis/04-api-intern-arbeitsobjekte.md` §3.14). Projekt-Intake-Feature-Seite der Bezahl-Editionen gliedert sich in **„Intake responsibility“** und **„Intake sources“** (R4 Z. 355–356) mit den Quellen-Karten **„In-app“** – „Get new work items from Members and Guests in your workspace without disruption to your existing work items.“, **„Email“** und **„Forms“** (R4 Z. 368–411). Template-Blueprint `intake_settings {is_in_app_enabled, is_email_enabled, is_form_enabled}` (via Dok 25 F20) ⇒ drei getrennt schaltbare Quellen. Nicht-Admins sehen Tooltips „Ask your Project Admin to turn this on.“ / „Ask your Project Admin to turn this off.“ (R4 Z. 362–363).

#### WM-44 – Intake Forms

**Tier:** Business, Enterprise (R1 Z. 447–456 „Take Intake work items from externally accessible web forms.“; `BUSINESS_PLAN_FEATURES` „Intake Forms“, R2).

**Funktionsbeschreibung (R4 `features.intake.form.*`, Z. 377–404):**
1. Quellen-Karte **„Forms“** – „Let folks outside your workspace create potential new work items for you via a dedicated and secure form.“; Feld **„Default form URL“** (öffentliche URL des Standardformulars, kopierbar).
2. **„Create Forms using work item types“**; Button **„Manage forms“** (Nicht-Workspace-Admins: Tooltip „Ask your Workspace Admin to manage this.“ ⇒ Formularverwaltung = Workspace-Admin).
3. **Formular-Editor** („Create form“ / „Edit form details“): **„Form title“** (Pflicht „Form title is required“), **„Work item type“** (Typ, dessen Properties angeboten werden), Property-Auswahl („Select properties“, Suche „Search for properties“, je Zeile „Remove property“). Toasts „Intake form created successfully“, „Intake form updated successfully“, „Failed to create intake form“, „Failed to update intake form“.
4. **Öffentliche Formularseite** in der Space-App („Space. Public-facing project pages (deployed views, intake forms, and similar)“, `/home/user/makeplane/developer-docs/docs/self-hosting/self-hosting-101.md` Z. 116); Einreichung erzeugt ein Intake-Work-Item mit `source = "FORMS"` (`EInboxIssueSource.FORMS`, `packages/types/src/inbox.ts` Z. 27–31) und Status Pending; in der Intake-Detailansicht wird als Ersteller **„Intake Form user“** angezeigt (`apps/web/components/inbox/content/issue-root.tsx` Z. 179–182). Ausgewählte Properties werden als Custom-Property-Werte gespeichert (Annahme). Felder für Absender (Name/E-Mail) UNVERIFIZIERT (`IntakeIssue.extra` JSON bzw. `source_email` als Träger).
5. Veröffentlichung über `DeployBoard` mit `entity_name = "intake"` (`TYPE_CHOICES` enthält `("intake", "Intake")`, `apps/api/plane/db/models/deploy_board.py` Z. 20–28; CE nutzt nur `"project"`, `apps/api/plane/space/views/intake.py` Z. 58, 109).

**Datenmodell (Vorschlag):** `intake_form(id, project_id, workspace_id, title, work_item_type_id, property_ids uuid[] (geordnet), is_default, anchor (öffentlicher Schlüssel), is_active)`; Space-Endpunkte `GET /api/public/anchor/{anchor}/intake-form/` (Definition) und `POST …/intake-form/submit/` mit Rate-Limit/Captcha (Airgapped: lokales Captcha, z. B. Proof-of-Work/Honeypot; UNVERIFIZIERT, welche Anti-Spam-Maßnahme das Original nutzt). **CE-Status:** Stub/UI-Hülle. **Konfidenz:** hoch (Konfiguration) / mittel (öffentliche Seite).

#### WM-45 – Intake Assignees / Intake responsibility

**Tier:** Business, Enterprise (R1 Z. 425–434 „Assign approved Intake work items to a member by default.“).

**Funktionsbeschreibung:** Abschnitt **„Intake responsibility“** mit Auswahl der verantwortlichen Mitglieder (Toasts „Setting assignees...“, „Assignees set successfully.“, „Something went wrong while setting assignees. Please try again.“) und Schalter **„Notify assignees“** – „For a new request to intake, default assignees will be alerted via notifications“ (R4 Z. 364–367, 398–410). ⇒ (a) Benachrichtigung der Verantwortlichen bei neuem Intake-Eintrag (In-App/E-Mail gemäß Benachrichtigungseinstellungen); (b) beim **Akzeptieren** wird das Work Item den Verantwortlichen zugewiesen, sofern es keine Assignees hat (Matrix-Text). **CE-Vergleich:** `Project.default_assignee` (eine Person, R12 Z. 79) wird im CE bereits beim Anlegen eines Intake-Eintrags (und jedes Work Items ohne Assignees) zugewiesen, sofern Mitglied mit Rolle ≥ 15 und aktiv (`apps/api/plane/app/views/intake/base.py` Z. 261–268; `apps/api/plane/app/serializers/issue.py` Z. 242–262). **Datenmodell (Vorschlag):** `intake_setting(project_id, assignee_ids uuid[], notify_assignees bool, is_in_app_enabled, is_email_enabled, is_form_enabled)`. **CE-Status:** teilweise. **Konfidenz:** mittel.

#### WM-46 – Emails For Intake

**Tier:** Business, Enterprise (R1 Z. 458–468 „Get an email address for reporting work items directly into a project's Intake.“, „Coming soon“); Doku-Badge „Business“ (`/home/user/makeplane/developer-docs/docs/self-hosting/govern/configure-dns-email-service.md`).

**Funktionsbeschreibung:** Quellen-Karte **„Email“** – „Collect new work items from anyone who sends an email to a Plane email address.“ mit Feld **„Email ID“** (projekteigene Adresse, kopierbar) (R4 Z. 372–376). Eingehende E-Mails werden „into work items or comments“ umgewandelt (`/home/user/makeplane/developer-docs/docs/self-hosting/plane-architecture.md`, Abschnitt „Intake“) ⇒ neue Mail → Intake-Work-Item (`source = "EMAIL"`, `source_email` = Absender; Betreff → Titel, Body → Beschreibung, Anhänge → Attachments); Antwort-Mail im Thread → Kommentar am bestehenden Item. Adressformat `issue+id@<INTAKE_EMAIL_DOMAIN>` (`environment-variables.md` Z. 255). Self-hosted: eigener SMTP-Empfangsdienst (Ports 25/465/587, TLS, `SMTP_DOMAIN` = `INTAKE_EMAIL_DOMAIN`, MX/SPF/DMARC-Records; Spam-/Domain-Blacklist, `MAX_ATTACHMENT_SIZE` 10 MB, interner Callback `POST /intake/email/`) – vollständig in **Dok 22 §4.23**.

**Datenmodell:** CE `IntakeIssue.source` (Default `IN_APP`), `source_email`, `extra` (R15); `SourceType` kennt nur `IN_APP` → um `FORMS`, `EMAIL` erweitern. Vorschlag `intake_email_address(project_id, local_part/token unique)`, `intake_email_message(message_id unique, in_reply_to, intake_issue_id, comment_id)` für Thread-Zuordnung. **Migration:** `Plane.IntakeMail` (.NET SMTP-Server + MimeKit), Airgapped über internen MX (ADR-004). **CE-Status:** Stub/UI-Hülle. **Konfidenz:** hoch (Infrastruktur) / mittel (Kommentar-Threading).

---

### 3.17 Duplicate Detection

#### WM-47 – Duplicate Detection

**Tier:** Funktion von **Plane AI** in der Commercial Edition („Plane AI brings AI-powered features to your workspace, including natural language chat, duplicate detection, and search …“, `/home/user/makeplane/developer-docs/docs/self-hosting/govern/plane-ai/configure-plane-ai.md` Z. 9; Badge „Commercial Edition“). Planstufe der Duplikaterkennung UNVERIFIZIERT (Plane AI ab Pro laut Dok 20 PF-82).

**Funktionsbeschreibung:**
1. **Technik (D7):** Ohne Embedding-Modell nutzt Plane AI BM25-Keyword-Suche; **mit** Embedding-Modell „vector similarity search, duplicate issue detection, and semantic retrieval over work items and pages“ (`configure-embedding-model.md` Z. 9). Unterstützte Modelle u. a. Cohere `embed-v4.0` (1536), OpenAI `text-embedding-3-small` (1536), Bedrock Titan v1 (1536)/v2 (1024); Vektor-Index in OpenSearch (`OPENSEARCH_ML_MODEL_ID`, `OPENSEARCH_EMBEDDING_DIMENSION` Default 1536); Bestand vektorisieren mit `manage_search_index --background --vectorize document index --force`.
2. **Anfrage/Antwort (CE-Typen, `packages/types/src/de-dupe.ts`):** `TDuplicateIssuePayload = { title: string; workspace_id: string; issue_id?: string | null; project_id?: string; description_stripped?: string }` → `TDuplicateIssueResponse = { dupes: TDeDupeIssue[] }` mit `TDeDupeIssue = { id, type_id, project_id, sequence_id, name, priority, state_id, created_by }`.
3. **Client-Hook:** `useDebouncedDuplicateIssues(workspaceSlug, workspaceId, projectId, { name, description_html?, issueId? }) => { duplicateIssues: TDeDupeIssue[] }` (CE liefert immer `[]`, `apps/web/hooks/use-debounced-duplicate-issues.tsx`) ⇒ **debounced** Abfrage während der Eingabe von Titel/Beschreibung; `issueId` schließt das eigene Item beim Bearbeiten aus.
4. **UI:** Im Work-Item-Create-Modal und im Intake-Create-Modal existiert bereits der State `isDuplicateModalOpen` / `handleDuplicateIssueModal(open)` (`apps/web/components/issues/issue-modal/base.tsx` Z. 68, 159, 382, 405–406; `form.tsx` Z. 73–74; `apps/web/components/inbox/modals/create-modal/modal.tsx` Z. 23–46; `create-root.tsx` Z. 49–50) – im CE ohne UI ⇒ bei Treffern erscheint ein Hinweis **„Duplicate work item found“** / **„Duplicate work items found“** (`duplicate_issue_found`, `duplicate_issues_found`, R8 Z. 284–285), der ein Seitenpanel/Modal mit der Trefferliste öffnet (Identifier, Titel, State, Priorität). Die Lösch- und Archiv-Modals akzeptieren bereits `TDeDupeIssue` (`data?: TIssue | TDeDupeIssue`, `apps/web/components/issues/delete-issue-modal.tsx` Z. 26; `archive-issue-modal.tsx` Z. 19) ⇒ aus der Trefferliste heraus können Duplikate **gelöscht oder archiviert** werden. Layout/Position des Panels UNVERIFIZIERT (O-04). Intake: „Mark as duplicate“ (`inbox_issue.actions.mark_as_duplicate`) ist CE-Funktion und kann Treffer übernehmen.

**API (Vorschlag, UNVERIFIZIERT):** `POST /api/workspaces/{slug}/dedupe/issues/` mit `TDuplicateIssuePayload` → `{dupes: [...]}` (max. 5–10 Treffer, Ähnlichkeitsschwelle konfigurierbar, nur Items, die der Nutzer sehen darf, ohne archivierte/gelöschte).

**Migrationshinweise (ADR-000/004):** Vektoren in **PostgreSQL/pgvector** (`work_item_embedding(work_item_id PK, model, dim, embedding vector(n), content_hash, updated_at)`, HNSW-Index `vector_cosine_ops`); Embeddings über konfigurierbaren, **lokal betreibbaren** Provider (OpenAI-kompatibler Endpunkt wie Ollama/vLLM oder ONNX-Modell im Prozess); Fallback ohne Modell: `pg_trgm`-Ähnlichkeit auf `name` + `description_stripped` (entspricht dem BM25-Fallback des Originals); Hintergrund-Job für Re-Embedding bei Titel-/Beschreibungsänderung (Outbox). **CE-Status:** Stub/UI-Hülle. **Quellen:** R8, R16, R20, D7. **Konfidenz:** hoch (Typen, Hook, Texte, Technikbasis) / niedrig (UI-Layout).

---
