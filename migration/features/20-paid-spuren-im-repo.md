# 20 – Spuren der Bezahl-Features im Community-Repo (Cluster P01) – IST-Analyse

> **Gegenstand:** Plane v1.4.2 Community Edition (AGPL-3.0), Repo-Root `/home/user/plane`.
> **Ziel:** Exakte Bestandsaufnahme aller Features, die **nicht** in der Community Edition (CE), sondern in den Bezahl-Editionen (One/Pro/Business/Enterprise bzw. „Enterprise Grid“) enthalten sind – soweit sie im CE-Repo **Spuren** hinterlassen (Plan-Matrix, Upsell-Stellen, CE-Stubs, Datenmodell-Felder, Typen/Konstanten, i18n-Texte, Icons). Jede Aussage ist mit Quellpfad (relativ zum Repo-Root) belegt.
> **Bindende Leitplanken:** `migration/architecture/00-grundsatzentscheidungen.md` (ADR-001: eine Edition, alle Features immer aktiv, kein Billing/Upsell; ADR-002: Realtime in .NET/YDotNet; ADR-003: Greenfield; ADR-004: Self-hosted/Airgapped; ADR-005: UI 1:1).
> **Schwester-Dokument:** `migration/features/21-paid-api-referenz-developer-docs.md` (Cluster P02) spezifiziert die öffentlichen REST-Verträge der Bezahl-Features aus den Developer-Docs. Dieses Dokument (P01) liefert die **Repo-Spuren**, die **Tier-Zuordnung** und die **UI-/Verhaltens-Spezifikation aus den UI-Texten**. Wo P02 die API vollständig beschreibt, wird hier nur darauf verwiesen.

---

## Inhaltsverzeichnis

1. Überblick & Quellenlage
2. Vollständige Feature×Plan-Matrix aus `plans.tsx` (zeilengenaue Übertragung) und Plan-Konstanten
3. Konsolidierte Feature-Tabelle (Feature | ab Plan | Abstufung je Plan | CE-Status | Quelle)
4. Feature-Abschnitte (PF-01 bis PF-105)
5. Inventar aller Upgrade-/Upsell-Stellen
6. Inventar der CE-Stubs / Extension-Points (hinter denen EE-Code steckt)
7. Inventar der i18n-Namespaces/-Schlüssel mit EE-Texten
8. EE-Typen, -Enums und -Konstanten in `packages/*`
9. Backend-Spuren (Models, Felder, fehlende Endpunkte, reservierte Slugs)
10. Offene Punkte / Unklarheiten
- Anhang A: Vollständige Liste der i18n-Schlüsselgruppen ohne CE-Referenz (EE-relevante Auswahl, automatisch ermittelt)
- Verifikations-Protokoll (Skeptiker-Lauf)

---

## 1. Überblick & Quellenlage

### 1.1 Edition-Kennzeichnung im CE-Repo

| Spur | Inhalt | Quelle |
|---|---|---|
| `InstanceEdition` | Enum mit genau **einem** Wert `PLANE_COMMUNITY = "PLANE_COMMUNITY"` | `apps/api/plane/license/models/instance.py` (Z. 18–19) |
| `Instance.edition` | `CharField(max_length=255, default=InstanceEdition.PLANE_COMMUNITY.value)` | `apps/api/plane/license/models/instance.py` (Z. 29) |
| Registrierung | `register_instance` setzt `edition=InstanceEdition.PLANE_COMMUNITY.value` (Neuanlage und Update) | `apps/api/plane/license/management/commands/register_instance.py` (Z. 74, 86) |
| Telemetrie | sendet `"edition": str(instance.edition or "")` | `apps/api/plane/license/bgtasks/telemetry_metrics.py` (Z. 139) |
| Editions-Badge (UI) | Sidebar-Button mit Label **„Community“**, Tooltip `Version: v{package.json.version}`, öffnet `PaidPlanUpgradeModal` | `apps/web/components/workspace/edition-badge.tsx` |
| Billing-Seite | Box „Community – Unlimited projects, issues, cycles, modules, pages, and storage“ + Planvergleich | `apps/web/components/workspace/billing/root.tsx` |
| Live-Server | `PageService` „Implementation for this is found in the enterprise repository.“ | `apps/live/src/services/page/extended.service.ts` |
| Developer-Docs | Drei self-hosted Editionen: Community (AGPL, „at par with the Free tier of the Cloud“), Commercial (closed-source, „Full feature parity with our Cloud“, 12 Free-Seats/Workspace), Airgapped (Commercial ohne Internet) | `/home/user/makeplane/developer-docs/docs/self-hosting/editions-and-versions.md` |

**Konsequenz:** Die CE entspricht funktional dem **Free**-Plan der Cloud. Alles, was in der Plan-Matrix (Abschnitt 2) für `free` mit `false` bzw. mit einer schwächeren Abstufung markiert ist, ist ein Bezahl-Feature. **Ausnahmen (Verifikation):** Die Zeile „Guests“ ist für `free` `false`, die CE kennt die Rolle Guest (`ROLE_CHOICES` `(5, "Guest")`, `apps/api/plane/db/models/workspace.py` Z. 19) aber ohne Kontingent; die Zeile „One-click Deployment“ ist für `free` `false`, die CE liefert aber Installationsskripte (`deployments/cli/community/install.sh`, README mit `curl -fsSL -o setup.sh https://github.com/makeplane/plane/releases/latest/download/setup.sh`, `deployments/cli/community/README.md` Z. 69) sowie AIO-, Kubernetes- und Swarm-Varianten (`deployments/{aio,kubernetes,swarm}/community`). Diese beiden sind daher „im CE vorhanden (nur Cloud-Gating)“ bzw. „teilweise im CE“ (PF-55, PF-100).

### 1.2 Planstufen

| Plan-Key (`TPlanePlans`) | `EProductSubscriptionEnum` | Anzeige im CE-Planvergleich | Preis lt. Repo | Quelle |
|---|---|---|---|---|
| `free` | `FREE` | nicht gerendert (`shouldRenderPlanDetail` → `false`) | 0 | `apps/web/components/workspace/billing/comparison/base.tsx` (Z. 27–33), `plans.tsx` (Z. 1259–1265) |
| `one` | `ONE` | nicht gerendert („Plane one plan is not longer available“) | 799 (einmalig, „per workspace“) | `base.tsx` (Z. 30–31), `plans.tsx` (Z. 1266–1275) |
| `pro` | `PRO` | gerendert, Badge „Popular“ | 8 $/User/Monat (monatlich), 6 $/User/Monat (jährlich) | `plans.tsx` (Z. 1276–1285), `plan-detail.tsx` |
| `business` | `BUSINESS` | gerendert, CTA „Talk to Sales“ (`isActive: false` → „Quote on request“) | – (in `payment.ts`: 15 $/Monat bzw. 156 $/Jahr als `unit_amount` 1500/15600) | `plans.tsx` (Z. 1286–1293), `packages/constants/src/payment.ts` |
| `enterprise` | `ENTERPRISE` | gerendert, CTA „Talk to Sales“ | – (`unit_amount: 0`, `is_active: false`) | `plans.tsx` (Z. 1294–1301), `packages/constants/src/payment.ts` |
| „Enterprise Grid“ | – (kein Enum-Wert im CE) | – | „quote-based“ | Developer-Docs-Badges `[Enterprise Grid]` in `self-hosting/govern/ldap.md`, `self-hosting/methods/airgapped-edition*.md`, `self-hosting/methods/fips-deployment.md`; WebSearch (plane.so/pricing, plane.so/business) |

**Zuordnung „Enterprise“ ↔ „Enterprise Grid“:** Im CE-Code heißt der Top-Plan `ENTERPRISE`. Die öffentliche Doku und die Pricing-Seite (Stand der WebSearch, 10/2026) nennen den Top-Plan **„Enterprise Grid“** (Multi-Workspace-Management, LDAP, SCIM, Airgapped, API-Audit-Logs, erweiterte Zugriffskontrolle). Dieses Dokument verwendet „Enterprise“ als Spalte der Matrix und notiert „Enterprise Grid“, wo die Doku es so kennzeichnet.

**Wichtig – Self-hosted-Werte:** `PlansComparison` übergibt fest `isSelfManaged` (= `true`) an `PlansComparisonBase`; daher zeigt die CE immer `feature["self-hosted"]?.[plan] ?? feature.cloud[plan]` (`apps/web/components/workspace/billing/comparison/root.tsx` Z. 50; `base.tsx` Z. 108–112). Nur die Zeile „Member limit“ hat einen abweichenden `self-hosted`-Datensatz.

### 1.3 Quellenarten und Methode

| Nr. | Quellenart | Vorgehen | Pfade |
|---|---|---|---|
| Q1 | Plan-Matrix | Zeilengenaue Übertragung aller 14 Sektionen / 87 aktiven Zeilen + 4 auskommentierte Zeilen | `apps/web/components/workspace/billing/comparison/plans.tsx` |
| Q2 | Plan-/Billing-Konstanten | vollständig gelesen | `packages/constants/src/subscription.ts`, `packages/constants/src/payment.ts`, `packages/utils/src/subscription.ts`, `packages/types/src/payment.ts`, `packages/constants/src/endpoints.ts` |
| Q3 | Upsell-Komponenten | `grep -rniE` mit den Mustern `upgrade`, `ProIcon`, `UpgradeBadge`, `paid.?plan`, `talk.?to.?sales`, `MARKETING_PRICING`, `isEnterprise`, `comingSoon`, `feature.?flag` über `apps/`, `packages/` | Abschnitt 5 |
| Q4 | CE-Stubs/Extension-Points | Suche nach `extended*`-Dateien, `// plane web imports`, `CE change`/`EE`-Kommentaren, Stub-Rückgaben (`return <></>`, `=> false`, `=> ({})`, `() => Promise.resolve()`) | Abschnitt 6 |
| Q5 | i18n | Skript (Python, read-only) über alle `packages/i18n/src/locales/en/*.json`: jeder Schlüssel wird als „referenziert“ gezählt, wenn er als String-Literal oder als Präfix eines Template-Literals (`` `prefix.${x}` ``) in `apps/**`, `packages/**` (ohne `locales`) vorkommt. Nicht referenzierte Schlüssel = Kandidaten für EE-Texte. **Heuristik:** Schlüssel, die über Objekt-Konstanten zusammengesetzt werden, können fälschlich als nicht referenziert erscheinen; EE-Zuordnung wurde daher inhaltlich geprüft. | Abschnitt 7, Anhang A |
| Q6 | Typen/Konstanten | `packages/types/src/**`, `packages/constants/src/**` gezielt nach EE-Enums/-Werten | Abschnitt 8 |
| Q7 | Backend | `apps/api/plane/db/models/**`, Serializer/Views, URL-Dateien `apps/api/plane/app/urls/*.py` | Abschnitt 9 |
| Q8 | Icons (UI 1:1) | Icon-Namen aus `@makeplane/propel` 0.7.3 (entpackt, nur gelesen): `…/scratchpad/propel-pkg/package/dist/icons/<kategorie>/*.d.ts`; Illustrationen aus `packages/blocks/src/empty-state/assets/` | Abschnitt 8.4 |
| Q9 | Offline-Doku | Developer-Docs (Tier-Badges, API-Referenz) | `/home/user/makeplane/developer-docs/docs/**` |
| Q10 | WebSearch (ergänzend, nur Zusammenfassungen verfügbar; plane.so selbst ist per Netzwerk nicht abrufbar) | 4 Suchen zu Pricing/Business/Enterprise Grid; im Verifikationslauf 4 weitere Suchen (Verifikations-Protokoll V.2) | https://plane.so/pricing , https://plane.so/pro , https://plane.so/business , https://plane.so/blog/introducing-plane-business , https://plane.so/self-hosted/whitepaper , https://plane.so/changelog/release-v2-2-0-enterprise-rollout-enhanced-search-workspace-refinements , https://docs.plane.so/workspaces-and-users/billing-and-plans |

### 1.4 Ergebnis in Zahlen

| Kennzahl | Wert | Quelle |
|---|---|---|
| Sektionen der Plan-Matrix | 14 (`project-work-tracking`, `project-work-management`, `visualization`, `analytics-reports`, `navigation`, `workspace-user-management`, `automations-workflows`, `knowledge-management`, `importers`, `integrations`, `storage`, `security`, `self-hosted`, `support`) | `plans.tsx` Z. 72–1255 |
| Aktive Matrix-Zeilen | 87 | `plans.tsx` |
| Davon `comingSoon: true` (Zeile) | 14 (+ Sektion `integrations` mit 5 Zeilen als Ganzes `comingSoon`) | `plans.tsx` |
| Auskommentierte Zeilen | 4 („Project Overview“, „Project Updates“, „Search“, „Time Capsule“) | `plans.tsx` Z. 318–329, 354–366, 572–583, 625–656 |
| Zeilen, in denen `free` ≠ volle Funktion (Bezahl-Feature oder -Abstufung) | 76 | Abschnitt 2 |
| Konsolidierte Bezahl-Features in Abschnitt 3/4 (inkl. nicht in `plans.tsx` enthaltener, aber im Repo belegter Features) | 105 (PF-01 bis PF-105; PF-104 und PF-105 im Verifikationslauf ergänzt), davon 3 mit CE-Status „entfällt“ (PF-66, PF-99, PF-101; in der JSON-Liste als „fehlt“ mit Vermerk „entfällt“ geführt); PF-55, PF-100 und PF-103 im Verifikationslauf umklassifiziert (siehe Verifikations-Protokoll) | Abschnitt 3 |
| i18n-Namespaces, die (nahezu) vollständig EE-Texte enthalten | 9: `automation` (141/141 Schlüssel ohne CE-Referenz), `editor` (29/29), `integration` (290/291), `template` (137/137), `tour` (89/89), `update` (29/29), `wiki` (73/73), `work-item-type` (207/207), `workflow` (40/40) | Q5-Skript, Abschnitt 7 |
| Upsell-/Billing-Stellen | 22 Einträge (U1–U22) | Abschnitt 5 |
| CE-Stubs / Extension-Points | 66 Einträge (S1–S66; S58–S66 im Verifikationslauf ergänzt) | Abschnitt 6 |
| Vom CE-Frontend aufgerufene, im CE-Backend fehlende Endpunkte | 10 EE-bezogene Gruppen (Gruppen 6–10 im Verifikationslauf ergänzt) + 6 nicht EE-zuordenbare Legacy-Aufrufe | Abschnitt 9.3 |
| EE-relevante i18n-Schlüssel (bereits in 22 Sprachen übersetzt) | 1 875 | Abschnitt 7, Anhang A |

---

## 2. Vollständige Feature×Plan-Matrix aus `plans.tsx`

Quelle aller Zeilen: `apps/web/components/workspace/billing/comparison/plans.tsx`. Darstellung: `✓` = `true`, `–` = `false`, Text = String-Wert (Zeilenumbrüche `\n` als „ / “). „CS“ = `comingSoon: true` auf Zeilenebene; „CS-Badge“ = Zelle rendert `<ComingSoonBadge />` + Text. Spalte „Z.“ = Zeilennummer in `plans.tsx`.

Rendering-Regeln (`base.tsx`, `feature-detail.tsx`): `true` → `TickCircleOutline` (`size-4 text-accent-primary`), `false` → `MinusCircle` aus `lucide-react` (`size-4 text-placeholder`), `null/undefined` → `MinusOutline` (`size-4 text-placeholder`), sonst der Knoten/Text. Sektionstitel `h2 text-h5-semibold text-secondary`, Sektion-`comingSoon` rendert Badge neben dem Titel. Badge „COMING SOON“: `rounded-sm bg-accent-primary px-1.5 py-0.5 text-9 font-semibold whitespace-nowrap text-on-color`.

Ergänzung (Verifikation, `apps/web/components/workspace/billing/comparison/base.tsx` Z. 26–32, 83–118): Je Zeile werden **nur** `feature.title`, das `comingSoon`-Badge und die Zellwerte gerendert. Die Felder `description`, `selfHostedDescription`, `selfHostedOnly` (Zeile) sowie `cloudOnly`/`selfHostedOnly` (Sektion) werden in `base.tsx` **nicht** ausgewertet; die Spalten `free` und `one` blendet `shouldRenderPlanDetail` aus (sichtbar sind nur Pro, Business, Enterprise). Die Spalte „Beschreibung (Original)“ unten gibt also Quelltext wieder, der im CE-UI nicht erscheint.

### 2.1 Sektion `project-work-tracking` – „Project + work tracking“

| Z. | Feature | Beschreibung (Original) | Free | One | Pro | Business | Enterprise | CS |
|---|---|---|---|---|---|---|---|---|
| 78 | Projects | Add projects to house work items, cycles, and modules. | ✓ | ✓ | ✓ | ✓ | ✓ | |
| 89 | Work items | Add work via work items, set properties for tracking, and add to cycles or modules. | ✓ | ✓ | ✓ | ✓ | ✓ | |
| 100 | Comments | Respond to work items, @mention members, and brainstorm together without leaving Plane. | ✓ | ✓ | ✓ | ✓ | ✓ | |
| 111 | Cycles | Track work in timeboxes with differing frequency. | ✓ | ✓ | ✓ | ✓ | ✓ | |
| 122 | Modules | Group replicable work in modules with their own leads. | ✓ | ✓ | ✓ | ✓ | ✓ | |
| 133 | Intake | See suggestions and feedback from viewers and guests before you decide to add them to your project. | ✓ | ✓ | ✓ | ✓ | ✓ | |
| 145 | Estimates | Measure effort in points in a system that works for you. | Basic | Basic | Advanced | Advanced | Advanced | |

### 2.2 Sektion `project-work-management` – „Project + work management“

| Z. | Feature | Beschreibung (Original) | Free | One | Pro | Business | Enterprise | CS |
|---|---|---|---|---|---|---|---|---|
| 162 | Bulk Ops | Add several work items to cycles or modules, transfer them, or edit their properties. | – | Limited props | All props | CS-Badge + „Work item transfers and conversions“ | CS-Badge + „Work item transfers and conversions“ | |
| 183 | Time Tracking + Worklogs | Track time per work item, see aggregated reports, and filter by need. | – | Basic | Historical timesheets | Historical timesheets / and approvals | Historical timesheets / and approvals | |
| 194 | Active Cycles | See all running cycles across all projects, or soon, in a single project. | – | ✓ | ✓ | ✓ | ✓ | |
| 205 | Work item Types | Create your own work item types with your own properties. | – | – | ✓ | ✓ | ✓ | |
| 216 | Custom Properties | Create your own properties and apply them to your workspace or project. | – | – | Project-level / custom properties | Workspace-level / properties and roll-ups | Workspace-level / properties and roll-ups | |
| 227 | Dependencies in Gantt | Adjust timelines for dependent work items visually on our Gantt layout. | – | – | ✓ | ✓ | ✓ | |
| 238 | Work item Transfers | Move a work item from a project or a cycle to another. | – | – | ✓ | ✓ | ✓ | |
| 249 | Auto-transfer Cycle Work items | Transfer incomplete work items from a completed cycle to the next cycle or to the default project state. | – | – | ✓ | ✓ | ✓ | |
| 261 | Epics | Organize long-term work in epics that house work items, cycles, and modules. | – | – | ✓ | ✓ | ✓ | |
| 272 | Initiatives | Create initiatives to roll up several epics. | – | – | ✓ | ✓ | ✓ | CS |
| 284 | Checkpoints | Add markers to Projects, Epics and Initiatives to keep your team on track and report on progress. | – | – | ✓ | ✓ | ✓ | CS |
| 297 | Module Overview | Like Cycle Overviews, see relevant details and progress charts for each module. | – | – | ✓ | ✓ | ✓ | |
| 308 | Auto-assignment In Modules | Choose assignment rules for work items in a module including Linear, Round Robin, or Capacity. | – | – | Linear | Round-robin and Capacity | Round-robin and Capacity | |
| 319 (auskommentiert) | Project Overview | See just-in-time snapshots of your project with essential metrics. | – | – | ✓ | ✓ | ✓ | CS |
| 331 | Public, Private, and Secret projects | Public projects are visible and accessible to everyone. Private ones are visible but need approval to join. Secret projects aren't visible or accessible. | – | – | ✓ | ✓ | ✓ | |
| 343 | State Of Projects | See all projects laid across states that highlight those that need attention and those on track. | – | – | ✓ | ✓ | ✓ | |
| 355 (auskommentiert) | Project Updates | Keep stakeholders in the loop with a dedicated space for updates that everyone in the project can see. | – | – | ✓ | ✓ | ✓ | CS |
| 368 | Pre-defined work item Templates | Choose from our available work item templates that customize work item types and properties for several use cases. | – | – | ✓ | ✓ | ✓ | CS |
| 381 | Teamspace Cycles | See multiple cycles in multiple projects at once. | – | – | – | ✓ | ✓ | |
| 392 | Project Templates | Save states, workflows, automation, and other project settings into templates. | – | – | – | ✓ | ✓ | |
| 403 | Baselines And Deviations | Declare baselines for how your projects progress and zoom in on deviations. | – | – | – | ✓ | ✓ | |
| 414 | Scheduled Comms | Schedule reports, notifications, and messages to third-party tools. | – | – | – | ✓ | ✓ | |
| 425 | Intake Assignees | Assign approved Intake work items to a member by default. | – | – | – | ✓ | ✓ | |
| 436 | Custom SLAs | Set SLA matrices for time-sensitive work items. | – | – | – | ✓ | ✓ | |
| 447 | Intake Forms | Take Intake work items from externally accessible web forms. | – | – | – | ✓ | ✓ | |
| 458 | Emails For Intake | Get an email address for reporting work items directly into a project's Intake. | – | – | – | ✓ | ✓ | CS |

### 2.3 Sektion `visualization` – „Visualization“

| Z. | Feature | Beschreibung (Original) | Free | One | Pro | Business | Enterprise | CS |
|---|---|---|---|---|---|---|---|---|
| 476 | Layouts | Choose from the List, the Board, the Calendar, the Gantt, or the Spreadsheet layout for your work items. | ✓ | ✓ | ✓ | ✓ | ✓ | |
| 488 | Views | Save sort, filter, and display options on a layout to a view. | ✓ | ✓ | ✓ | ✓ | ✓ | |
| 499 | Shared Views | Choose a few members to share a view with. | – | – | ✓ | ✓ | ✓ | |
| 510 | Publish Views | Put a view on the Internet and let your customers interact with them. | – | – | ✓ | ✓ | ✓ | |
| 521 | Dashboards and Widgets | Create your own dashboards with custom widgets and data types. | – | – | ✓ | ✓ | ✓ | |

### 2.4 Sektion `analytics-reports` – „Analytics + reports“

| Z. | Feature | Beschreibung (Original) | Free | One | Pro | Business | Enterprise | CS |
|---|---|---|---|---|---|---|---|---|
| 538 | Progress Charts | Track progress in cycles, modules, and overviews throughout Plane without switching to dashboards or Analytics. | – | – | ✓ | ✓ | ✓ | |
| 550 | Cycle Reports | Get on-demand cycle reports during and after a cycle. Revisit reports anytime from permalinks. | – | – | ✓ | ✓ | ✓ | |
| 561 | Insights | Hindsight, On-demand insights, Foresights. | – | – | ✓ | ✓ | ✓ | CS |
| 573 (auskommentiert) | Time Capsule | Go back in your project's timeline and see point-in-time snapshots. | – | – | – | ✓ | ✓ | CS |
| 585 | Advanced Pages Analytics | See who's viewing, sharing, and commenting on your pages along with other useful info. | – | – | – | ✓ | ✓ | CS |
| 597 | Custom Reports | Generate reports by any dimension and metric across your project or workspace. | – | – | – | ✓ | ✓ | CS |

### 2.5 Sektion `navigation` – „Navigation“

| Z. | Feature | Beschreibung (Original) | Free | One | Pro | Business | Enterprise | CS |
|---|---|---|---|---|---|---|---|---|
| 615 | Power K | Access a keyboard-first gateway to almost anything in Plane. | ✓ | ✓ | ✓ | ✓ | ✓ | |
| 626 (auskommentiert) | Search | Search via natural-language queries, operators, or PQL | Basic text search | Basic text search | CS + „Operator capsules from text or PQL“ | CS + „Operator capsules from text or PQL“ | CS + „Operator capsules from text or PQL“ | |
| 658 | PQL | Write Plane Query Language in search with support for Boolean operators. Soon, you can write natural language queries. | – | – | ✓ | ✓ | ✓ | |

### 2.6 Sektion `workspace-user-management` – „Workspace and user management“

| Z. | Feature | Beschreibung (Original) | Free | One | Pro | Business | Enterprise | CS |
|---|---|---|---|---|---|---|---|---|
| 676 | Member limit | Cloud: „Number of seats that can use project and work management features“; Self-hosted (`selfHostedDescription`): „Number of users that our standard infra supports / Increase infra to get more users“ | Cloud „12“ / **Self-hosted „~50“** | Cloud „“ / **SH „~50“** | Cloud „Unlimited“ / **SH „~200“** | Cloud „Unlimited“ / **SH „~200“** | Cloud „Unlimited“ / **SH „Unlimited“** | |
| 695 | Roles | Choose from one of four pre-defined roles or create custom ones with RBAC. | Basic | Basic | Pre-defined roles | RBAC | GAC | |
| 706 | Guests | Let some users see everything or just their work items in a project. | – | 5 per paid member | 5 per paid member | 5 per paid member | 5 per paid member | |
| 717 | Approvals | Set workspace, project, and work item type approvals to designated admins. | – | – | – | ✓ | ✓ | CS |
| 729 | Admin Interface | Get an admin overview to manage workspace and project settings. | – | – | – | ✓ | ✓ | |
| 740 | Workspace Activity Logs | See filterable activity logs for your entire workspace. | – | – | – | ✓ | ✓ | |
| 751 | API-enabled Audit Logs | See a full-workspace audit log and use APIs to flag Plane activity in compliance systems. | – | – | – | ✓ | ✓ | CS |

### 2.7 Sektion `automations-workflows` – „Automations and workflows“

| Z. | Feature | Beschreibung (Original) | Free | One | Pro | Business | Enterprise | CS |
|---|---|---|---|---|---|---|---|---|
| 769 | Trigger And Action | Choose a trigger and a corresponding action per automation flow. | – | – | ✓ | ✓ | ✓ | |
| 780 | Decisions And Loops Automation | Use actions as triggers indefinitely in an automation flow. | – | – | – | ✓ | ✓ | CS |
| 792 | Number of automations | Total number of automation flows in your workspace | – | – | 5,000 | 10,000 | Unlimited | |

### 2.8 Sektion `knowledge-management` – „Knowledge management“

| Z. | Feature | Beschreibung (Original) | Free | One | Pro | Business | Enterprise | CS |
|---|---|---|---|---|---|---|---|---|
| 809 | Pages | Build knowledge bases for your teams which are accessible & shareable. | ✓ | ✓ | ✓ | ✓ | ✓ | |
| 820 | Real-time Collab | Edit a page together with members in your project, team, or workspace. | – | ✓ | ✓ | ✓ | ✓ | |
| 831 | Work item Embeds | Embed work items from any project you are a member of. | – | ✓ | ✓ | ✓ | ✓ | |
| 842 | Link-to-work items | Link pages in work items in a separate section in work item details. | – | ✓ | ✓ | ✓ | ✓ | |
| 853 | Publish | Put your pages on the web for external users and let them comment without signing into your workspace. | – | ✓ | ✓ | ✓ | ✓ | |
| 865 | Wiki | Create company-wide wikis or knowledge bases without creating a project. | – | ✓ | ✓ | ✓ | ✓ | |
| 876 | Exports | Export page content into PDFs or Word-compatible docs. | – | – | One download / at a time | Queued downloads | Queued downloads | |
| 887 | Templates | Use pages as templates for your project, team, or workspace. | – | – | ✓ | ✓ | ✓ | |
| 898 | Versions | See restorable version of edits to your pages. | – | – | 2 days | 3 months | Unlimited | |
| 909 | Databases + Formulas | Put databases and formulas into a page without worrying about losing text, images, or other content types. | – | – | – | ✓ | ✓ | CS |
| 922 | Nested Pages | Pages inside a page, organize your pages as you see fit for the progressive disclosure. | – | – | – | Word-compatible + other format downloads | Word-compatible + other format downloads | CS |

Anmerkung Z. 922: Die Zellwerte „Word-compatible + other format downloads“ passen inhaltlich nicht zur Zeile „Nested Pages“ (vermutlicher Copy-&-Paste-Fehler im Original; Zeile „Exports“ liefert die Abstufung der Downloads). Für die Portierung ist **Nested Pages = Business+** maßgeblich (bestätigt durch `BUSINESS_PLAN_FEATURES` in `packages/constants/src/subscription.ts` und `wiki.nested_pages_download_banner.title` „Nested pages require a paid plan“ in `packages/i18n/src/locales/en/wiki.json`).

### 2.9 Sektion `importers` – „Importers“

| Z. | Feature | Beschreibung (Original) | Free | One | Pro | Business | Enterprise | CS |
|---|---|---|---|---|---|---|---|---|
| 940 | Jira | Import your work items and members from Jira. | Without custom props | Without custom props | With custom props | With custom props | With custom props | |
| 951 | GitHub | Import your work items and members from GitHub. | Without custom props | Without custom props | With custom props | With custom props | With custom props | |

### 2.10 Sektion `integrations` – „Integrations“ (Sektion `comingSoon: true`)

| Z. | Feature | Beschreibung (Original) | Free | One | Pro | Business | Enterprise | CS |
|---|---|---|---|---|---|---|---|---|
| 969 | GitHub | Sync Plane work items and states to GitHub work items and states. Update GitHub automatically with activity from Plane and vice-versa. | – | – | ✓ | ✓ | ✓ | Sektion |
| 981 | Slack | Get Plane activity in Slack and use / commands in Slack to make changes in Plane. | – | – | ✓ | ✓ | ✓ | Sektion |
| 992 | Zapier | Run if-then-else automations using Zapier. | – | – | ✓ | ✓ | ✓ | Sektion |
| 1003 | Zendesk | Create Plane work items from Zendesk tickets. | – | – | ✓ | ✓ | ✓ | Sektion |
| 1014 | Freshdesk | Create Plane work items from Freshdesk tickets. | – | – | ✓ | ✓ | ✓ | Sektion |

### 2.11 Sektion `storage` – „Storage“ (`cloudOnly: true`)

| Z. | Feature | Beschreibung (Original) | Free | One | Pro | Business | Enterprise | CS |
|---|---|---|---|---|---|---|---|---|
| 1032 | Space | Total storage allowed per workspace | 5GB | – | 1 TB | 5 TB | Custom | |
| 1043 | Max file size | Limit for uploads to your workspace | 5 MB | – | 100 MB | 200 MB | Custom | |

Hinweis: `cloudOnly` wird in `base.tsx` **nicht** ausgewertet (die Sektion wird auch self-hosted angezeigt). Für die Portierung entfällt die Sektion (ADR-004: „Storage-Quoten pro Plan entfallen“); das Upload-Limit bleibt Instanzkonfiguration (`config.file_size_limit` → `useFileSize`, `apps/web/hooks/use-file-size.ts`).

### 2.12 Sektion `security` – „Security“

| Z. | Feature | Beschreibung (Original) | Free | One | Pro | Business | Enterprise | CS |
|---|---|---|---|---|---|---|---|---|
| 1060 | SAML | Get the officially supported SAML implementation and make Plane secure with any IdP. | – | ✓ | ✓ | ✓ | ✓ | |
| 1071 | OIDC (`selfHostedOnly: true`) | Get the officially supported OIDC implementation and make Plane secure with any IdP. | – | ✓ | ✓ | ✓ | ✓ | |
| 1083 | Domain Security | Choose other domains that can authenticate into your Plane workspace or restrict all but one domain. | – | – | ✓ | ✓ | ✓ | |
| 1095 | Two-factor authentication and passkeys | Secure your Plane workspace with device-dependent two-factor authentication and passkeys. | – | – | ✓ | ✓ | ✓ | |
| 1106 | Password Policy | Set custom password policies in line with your compliance requirements. | – | – | ✓ | ✓ | ✓ | |
| 1117 | LDAP | Get our official LDAP implementation and secure your Plane workspace with your LDAP server. | – | – | – | – | ✓ | CS |

### 2.13 Sektion `self-hosted` – „Self-hosted“ (`selfHostedOnly: true`)

| Z. | Feature | Beschreibung (Original) | Free | One | Pro | Business | Enterprise | CS |
|---|---|---|---|---|---|---|---|---|
| 1136 | God Mode | Manage your self-hosted Plane instance better with an instance admin interface. | ✓ | ✓ | ✓ | ✓ | ✓ | |
| 1147 | One-click Deployment | Install and deploy your self-hosted Plane to any private cloud with a single-line command. | – | ✓ | ✓ | ✓ | ✓ | |
| 1158 | Digital Ocean Marketplace app | Get our Digital Ocean-compatible app on their marketplace. | – | ✓ | ✓ | ✓ | ✓ | |
| 1169 | Heroku Platform app | Get our Heroku Platform-compatible app and deploy to Heroku easily. | – | ✓ | ✓ | ✓ | ✓ | |
| 1180 | AWS AMI | Get our AMI-compatible app from the AWS marketplace. | – | ✓ | ✓ | ✓ | ✓ | |
| 1191 | Private deployments | Get our hosted Cloud app on a private Cloud managed by us. | – | – | – | – | ✓ | CS |

### 2.14 Sektion `support` – „Support“

| Z. | Feature | Beschreibung (Original) | Free | One | Pro | Business | Enterprise | CS |
|---|---|---|---|---|---|---|---|---|
| 1209 | Channels | Get access to one or more Support channels by your plan. | Icon Forum (`ChatOutline`) | Icons Mail + Forum | Icons Mail + Forum + Chat | Full-suite / professional services | Full-suite / professional services | |
| 1235 | SLA | „Get business-friendly SLAs with higher plans. SLAs are by priority of work item and tiers can be requested.“ (Link `https://plane.so/talk-to-sales`) | – | – | ✓ | ✓ | ✓ | |

### 2.15 Plan-Highlights (`PLANE_PLANS.planHighlights`, `plans.tsx` Z. 1303–1309)

| Plan | Highlights (vollständig) |
|---|---|
| free | „Upto 12 users“, „Pages“, „Unlimited projects“, „Unlimited cycles and modules“ |
| one | „Upto 50 users“, „OIDC and SAML“, „Active cycles“, „Limited time tracking“ |
| pro | „Unlimited users“, „Custom work items + Properties“, „Work item templates“, „Full Time Tracking“ |
| business | „RBAC“, „Project Templates“, „Baselines And Deviations“, „Custom Reports“ |
| enterprise | „Private + managed deployments“, „GAC“, „LDAP support“, „Databases + Formulas“ |

### 2.16 Feature-Listen der Upgrade-Karten (`packages/constants/src/subscription.ts`)

| Konstante | Einträge (vollständig, Reihenfolge wie im Original) | Verwendung |
|---|---|---|
| `ENTERPRISE_PLAN_FEATURES` | „Private + managed deployments“, „GAC“, „LDAP support“, „Databases + Formulas“, „Unlimited and full Automation Flows“, „Full-suite professional services“ | `apps/web/components/license/modal/upgrade-modal.tsx` |
| `BUSINESS_PLAN_FEATURES` | „Project Templates“, „Workflows + Approvals“, „Decision + Loops Automation“, „Custom Reports“, „Nested Pages“, „Intake Forms“ | dito |
| `PRO_PLAN_FEATURES` | „Dashboards + Reports“, „Full Time Tracking + Bulk Ops“, „Teamspaces“, „Trigger And Action“, „Wikis“, „Popular integrations“ | dito |
| `ONE_PLAN_FEATURES` | „OIDC + SAML for SSO“, „Active Cycles“, „Real-time collab + public views and page“, „Link pages in issues and vice-versa“, „Time-tracking + limited bulk ops“, „Docker, Kubernetes and more“ | (im CE nicht referenziert) |
| `FREE_PLAN_UPGRADE_FEATURES` | „OIDC + SAML for SSO“, „Time Tracking and Bulk Ops“, „Integrations“, „Public Views and Pages“ | `apps/web/components/license/modal/card/free-plan.tsx` |

### 2.17 Billing-/Payment-Konstanten (werden **nicht** portiert, ADR-001)

| Element | Inhalt | Quelle |
|---|---|---|
| `EProductSubscriptionEnum` | `FREE`, `ONE`, `PRO`, `BUSINESS`, `ENTERPRISE` | `packages/types/src/payment.ts` |
| `TProductSubscriptionType` | `"FREE" \| "ONE" \| "PRO" \| "BUSINESS" \| "ENTERPRISE"` | dito |
| `TBillingFrequency` | `"month" \| "year"` | dito |
| `IPaymentProductPrice` | `currency`, `id`, `product`, `recurring`, `unit_amount`, `workspace_amount` | dito |
| `IPaymentProduct` | `description`, `id`, `name`, `type`, `payment_quantity`, `prices[]`, `is_active` | dito |
| `TSubscriptionPrice` | `key`, `id`, `currency`, `price`, `recurring` | dito |
| `DEFAULT_PRODUCT_BILLING_FREQUENCY` | FREE/ONE `undefined`, PRO/BUSINESS/ENTERPRISE `"month"` | `packages/constants/src/payment.ts` |
| `SUBSCRIPTION_WITH_BILLING_FREQUENCY` | PRO, BUSINESS, ENTERPRISE | dito |
| `PLANE_COMMUNITY_PRODUCTS` | PRO „Plane Pro“ (800 ct/Monat, 7200 ct/Jahr, aktiv); BUSINESS „Plane Business“ (1500 ct/Monat, 15600 ct/Jahr, aktiv; Beschreibung „The earliest packaging of Business at $10 a seat a month billed annually, $12 a seat a month billed monthly for Plane Cloud“); ENTERPRISE „Plane Enterprise“ (0, `is_active: false`) | dito |
| `TALK_TO_SALES_URL` | `https://plane.so/talk-to-sales` | dito |
| `SUBSCRIPTION_REDIRECTION_URLS` | PRO → `https://app.plane.so/upgrade/pro/self-hosted?plan=month` bzw. `…?plan=year`; BUSINESS → `…/upgrade/business/self-hosted?plan=…`; FREE/ONE/ENTERPRISE → Talk-to-Sales | dito |
| `SUBSCRIPTION_WEBPAGE_URLS` | PRO `https://plane.so/pro`, BUSINESS/ENTERPRISE `https://plane.so/business`, sonst Talk-to-Sales | dito |
| Marketing-Links | `MARKETING_PRICING_PAGE_LINK = "https://plane.so/pricing"`, `MARKETING_CONTACT_US_PAGE_LINK = "https://plane.so/contact"`, `MARKETING_PLANE_ONE_PAGE_LINK = "https://plane.so/one"` | `packages/constants/src/endpoints.ts` (Z. 31–33) |
| Utils | `calculateYearlyDiscount`, `getSubscriptionName`, `getBaseSubscriptionName` (ONE/PRO → „Free“, BUSINESS → „Pro“, ENTERPRISE → „Business“), `getSubscriptionPriceDetails` (Monatspreis = `unit_amount/100`, Jahrespreis/Monat = `unit_amount/1200`) | `packages/utils/src/subscription.ts` |

---

## 3. Konsolidierte Feature-Tabelle

Legende **CE-Status** (gegen das Repo per `grep`/Lesen geprüft):
- **fehlt** – keine funktionale Spur außer Texten/Icons/Plan-Matrix.
- **Stub/UI-Hülle im CE** – Extension-Point, Typ/Enum, leere Komponente, toter Service-Aufruf oder Upsell-Seite vorhanden, Funktion fehlt.
- **teilweise im CE** – Datenmodell oder Teilfunktion vorhanden, Bezahl-Abstufung fehlt.
- **im CE vorhanden (nur Cloud-Gating)** – Funktion ist im CE-Code vollständig, nur das Plan-Gating ist Cloud-seitig.
- **entfällt (ADR-001/004)** – reines Billing/Limit/Cloud-Thema; wird nicht portiert.
- **Abgrenzungsregel (Verifikationslauf):** Legacy-Modelle ohne jede View/URL (`Integration`, `WorkspaceIntegration`, `Github*`, `SlackProjectSync`, `Importer`) und reine Choice-Werte (z. B. `DeployBoard` `page`) gelten als **Stub/UI-Hülle**, nicht als „teilweise“; „teilweise“ setzt eine im CE erreichbare Teilfunktion oder ein produktiv genutztes Datenmodell voraus.

Legende **ab Plan (Verifikationslauf):** Bei Widerspruch zwischen `plans.tsx` (älterer Stand, enthält den nicht mehr erhältlichen Plan One) und aktuelleren bzw. spezifischeren Quellen (Doku-Labels docs.plane.so, feature-spezifische Upsell-Texte im Repo, verifizierte Schwester-Dokumente) gewinnt die aktuellere/spezifischere Quelle; der Widerspruch ist in der Spalte „Abstufung je Plan“ dokumentiert. „Enterprise“ (Code) und „Enterprise Grid“ (Doku) werden als Synonym behandelt; wo die Doku ausdrücklich „Enterprise Grid“ nennt, steht dieser Name.

Legende **ab Plan**: niedrigster Plan lt. `plans.tsx`; wo `plans.tsx` schweigt, die angegebene Quelle; „unklar“ = keine belastbare Quelle.

| ID | Feature | ab Plan | Abstufung je Plan | CE-Status | Quelle (primär) |
|---|---|---|---|---|---|
| PF-01 | Advanced Estimates (Time-Estimates, Bearbeiten/Umsortieren/Systemwechsel) | Pro | Free/One „Basic“; Pro/Business/Enterprise „Advanced“ | teilweise im CE | `plans.tsx` Z. 145; `packages/constants/src/estimates.ts`; `apps/web/components/estimates/create/helper.tsx` |
| PF-02 | Bulk Ops | One | One „Limited props“; Pro „All props“; Business/Enterprise + „Work item transfers and conversions“ (Coming soon) | Stub/UI-Hülle im CE (Store-Aktion `bulkUpdateProperties` und Service `bulkOperations` → `bulk-operation-issues/` vorhanden, Backend-Route fehlt) | `plans.tsx` Z. 162; `apps/web/hooks/use-bulk-operation-status.ts`; `apps/web/components/issues/bulk-operations/root.tsx`; `apps/web/services/issue/issue.service.ts` Z. 339–345; `apps/web/store/issue/helpers/base-issues.store.ts` Z. 718–753 |
| PF-03 | Time Tracking + Worklogs (+ Timesheets, Approvals) | One | One „Basic“; Pro „Historical timesheets“; Business/Enterprise „Historical timesheets and approvals“ | Stub/UI-Hülle im CE (nur Flag `is_time_tracking_enabled`, über die Public-API schreibbar, ohne Funktion; Export-Choice `issue_worklogs` ohne Exporter-Logik; Dok. 21/23 werten dies als „teilweise“) | `plans.tsx` Z. 183; `apps/api/plane/db/models/project.py` Z. 100; `apps/api/plane/db/models/exporter.py` Z. 31 |
| PF-04 | Active Cycles (Workspace-weit) | One | One–Enterprise ✓ | Stub/UI-Hülle im CE | `plans.tsx` Z. 194; `apps/web/components/active-cycles/workspace-active-cycles-upgrade.tsx` |
| PF-05 | Work item Types | Pro | Pro–Enterprise ✓ | teilweise im CE | `plans.tsx` Z. 205; `apps/api/plane/db/models/issue_type.py` |
| PF-06 | Custom Properties (Projekt-Ebene) | Pro | Pro „Project-level custom properties“ | Stub/UI-Hülle im CE | `plans.tsx` Z. 216; `packages/i18n/src/locales/en/work-item-type.json`; `apps/web/components/issues/issue-modal/provider.tsx` |
| PF-07 | Workspace-Level Properties und Roll-ups | Business | Business/Enterprise „Workspace-level properties and roll-ups“ | fehlt | `plans.tsx` Z. 216 |
| PF-08 | Work-Item-Type-Hierarchie (Level, Parent/Child-Regeln) | unklar | – | fehlt | `packages/i18n/src/locales/en/work-item-type.json` (`work_item_type_hierarchy.*`) |
| PF-09 | Dependencies in Gantt (Starts/Finishes Before/After) | Pro | Pro–Enterprise ✓ | teilweise im CE (Backend speichert und liefert alle vier Timeline-Relationen; Frontend-Typen/Optionen beschränkt; `isDependencyEnabled = false`) | `plans.tsx` Z. 227; `apps/api/plane/db/models/issue.py` Z. 272–293; `apps/api/plane/app/views/issue/relation.py` Z. 113–135, 225–237; `apps/api/plane/api/serializers/issue.py` Z. 545–580; `apps/web/components/relations/index.tsx`; `apps/web/store/timeline/base-timeline.store.ts` Z. 85 |
| PF-10 | Relation „Implements/Implemented by“ und Workspace-Relationstypen | unklar | – | teilweise im CE | `apps/api/plane/db/models/issue.py` Z. 278, 290; `workspace_settings.settings.relations` |
| PF-11 | Work item Transfers (zwischen Projekten/Cycles) | Pro | Pro–Enterprise ✓ | teilweise im CE | `plans.tsx` Z. 238; `apps/web/components/cycles/transfer-issues-modal.tsx` |
| PF-12 | Auto-transfer Cycle Work items (Auto-Rollover) | Pro | Pro–Enterprise ✓ | teilweise im CE (nur manueller Transfer `TransferCycleIssueEndpoint`; automatischer Transfer am Cycle-Ende fehlt) | `plans.tsx` Z. 249; `project_settings.cycles.auto_schedule.form.auto_rollover`; `apps/api/plane/app/urls/cycle.py` Z. 72; `apps/api/plane/app/views/cycle/base.py` Z. 599 |
| PF-13 | Auto-schedule Cycles | unklar | – | fehlt | `project_settings.cycles.auto_schedule.*` (`packages/i18n/src/locales/en/project-settings.json`) |
| PF-14 | Epics | Pro | Pro–Enterprise ✓ (Doku-Label docs.plane.so/work-items/epics „Pro“ laut Dok. 21; Plane University nennt Business – Widerspruch, Pro beibehalten) | Stub/UI-Hülle im CE | `plans.tsx` Z. 261; `apps/web/components/epic-modal/modal.tsx`; `apps/api/plane/db/models/issue_type.py` Z. 19 |
| PF-15 | Initiatives | Pro | Pro–Enterprise ✓ (in `plans.tsx` „Coming soon“; plane.so/pro: „epics and initiatives“); **Widerspruch:** Plane University ordnet Epics und Initiatives Business zu (Dok. 21 F02; WebSearch Verifikationslauf), Sub-Initiativen nur Enterprise (Dok. 23 WM-11) | Stub/UI-Hülle im CE | `plans.tsx` Z. 272; `apps/web/store/theme.store.ts`; `packages/types/src/enums.ts` Z. 72 |
| PF-16 | Checkpoints | Pro | Pro–Enterprise ✓ (Coming soon) | fehlt | `plans.tsx` Z. 284 |
| PF-17 | Milestones (Projekt-Feature) | unklar | – | Stub/UI-Hülle im CE | `project_settings.features.milestones.*`; `packages/constants/src/fetch-keys.ts` Z. 205; `apps/web/store/project/project.store.ts` Z. 21 |
| PF-18 | Module Overview | Pro | Pro–Enterprise ✓ | teilweise im CE | `plans.tsx` Z. 297; `apps/web/components/modules/analytics-sidebar/` |
| PF-19 | Auto-assignment in Modules | Pro | Pro „Linear“; Business/Enterprise „Round-robin and Capacity“ | fehlt | `plans.tsx` Z. 308 |
| PF-20 | Public, Private und Secret Projects | Pro | Pro–Enterprise ✓ | teilweise im CE | `plans.tsx` Z. 331; `apps/api/plane/db/models/project.py` Z. 71, 76; `packages/constants/src/project.ts` Z. 21 |
| PF-21 | State of Projects (Projekt-States/Project Grouping, Projekt-Labels) | Pro | Pro–Enterprise ✓ | fehlt | `plans.tsx` Z. 343; `workspace_settings.settings.project_states`, `workspace_settings.settings.projects` |
| PF-22 | Project Overview | Pro | Pro–Enterprise ✓ (Zeile auskommentiert, Coming soon) | Stub/UI-Hülle im CE | `plans.tsx` Z. 319; `apps/web/store/project/project.store.ts` Z. 21, 86 |
| PF-23 | Project Updates (Status-Updates On-Track/Off-Track/At-Risk) | Pro | Pro–Enterprise ✓ (nur in auskommentierter Zeile, Coming soon – schwacher Beleg) | Stub/UI-Hülle im CE (Enum `EUpdateStatus`, Activity-Text „enabled/disabled project updates“ für Feld `is_project_updates_enabled`, das im CE-Modell `Project` fehlt) | `plans.tsx` Z. 355; `packages/i18n/src/locales/en/update.json`; `packages/types/src/enums.ts` (`EUpdateStatus`); `apps/web/components/common/activity/helper.tsx` Z. 67, 266–269 |
| PF-24 | Pre-defined work item Templates | Pro | Pro–Enterprise ✓ (Coming soon) | fehlt | `plans.tsx` Z. 368 |
| PF-25 | Work-Item-Templates | Pro | Pro–Enterprise (planHighlights Pro „Work item templates“) | Stub/UI-Hülle im CE | `plans.tsx` Z. 1306; `apps/web/components/issues/issue-modal/provider.tsx` |
| PF-26 | Project Templates | Business | Business/Enterprise ✓ | Stub/UI-Hülle im CE | `plans.tsx` Z. 392; `apps/web/components/project/create-project-modal.tsx` Z. 27 |
| PF-27 | Page-Templates | Pro | Pro–Enterprise ✓ | fehlt | `plans.tsx` Z. 887; `packages/i18n/src/locales/en/template.json` |
| PF-28 | Template-Veröffentlichung im Marketplace | unklar | – | fehlt | `templates.settings.form.publish.*` (`template.json`) |
| PF-29 | Recurring work items | Business | „Upgrade to Business to make recurring work feel effortless.“ | fehlt | `recurring_work_items.empty_state.upgrade.description` (`packages/i18n/src/locales/en/work-item.json`) |
| PF-30 | Teamspaces | Pro | Pro–Enterprise (`PRO_PLAN_FEATURES` „Teamspaces“) | Stub/UI-Hülle im CE | `packages/constants/src/subscription.ts` Z. 28; `packages/types/src/issues/issue.ts` Z. 32–42 |
| PF-31 | Teamspace Cycles | Business | Business/Enterprise ✓ | fehlt | `plans.tsx` Z. 381 |
| PF-32 | Baselines And Deviations | Business | Business/Enterprise ✓ | fehlt | `plans.tsx` Z. 403 |
| PF-33 | Scheduled Comms | Business | Business/Enterprise ✓ | fehlt | `plans.tsx` Z. 414 |
| PF-34 | Intake Assignees / Intake-Verantwortung / Benachrichtigung | Business | Business/Enterprise ✓ | teilweise im CE (`Project.default_assignee` wird beim Anlegen eines Intake-Work-Items als `default_assignee_id` übergeben) | `plans.tsx` Z. 425; `project_settings.features.intake.notify_assignee`; `apps/api/plane/db/models/project.py` Z. 79; `apps/api/plane/app/views/intake/base.py` Z. 261–268 |
| PF-35 | Custom SLAs | Business | Business/Enterprise ✓ | fehlt | `plans.tsx` Z. 436 |
| PF-36 | Intake Forms | Business | Business/Enterprise ✓ | Stub/UI-Hülle im CE | `plans.tsx` Z. 447; `packages/types/src/inbox.ts` Z. 27–31; `apps/api/plane/db/models/deploy_board.py` Z. 27 |
| PF-37 | Emails For Intake | Business | Business/Enterprise ✓ (Coming soon; Doku-Badge `[Business]`) | Stub/UI-Hülle im CE (Felder `IntakeIssue.source`/`source_email` werden serialisiert und in der Activity als „created the work item via {Source}“ angezeigt, `apps/web/components/issues/issue-detail/issue-activity/activity/actions/default.tsx` Z. 39–43; kein E-Mail-Eingang; Dok. 21/22 werten dies als „teilweise“, Dok. 23 als Stub) | `plans.tsx` Z. 458; `apps/api/plane/db/models/intake.py` Z. 76–77; `self-hosting/govern/configure-dns-email-service.md` |
| PF-38 | Work Item in anderes Projekt duplizieren | unklar | – | Stub/UI-Hülle im CE (`createCopyMenuWithDuplication` gibt nur das Basis-Menüelement zurück; Prop `setDuplicateWorkItemModal` ungenutzt) | `issue.duplicate.modal.*` (`work-item.json`); `apps/web/components/issues/issue-layouts/quick-action-dropdowns/copy-menu-helper.tsx` |
| PF-39 | Antworten auf Kommentare (Replies) | unklar | – | teilweise im CE | `issue.comments.replies.*`; `apps/api/plane/db/models/issue.py` Z. 475 |
| PF-40 | Up-/Downvotes in der App | unklar | – | teilweise im CE | `issue.vote.*`; `apps/api/plane/db/models/issue.py` Z. 654 |
| PF-41 | Customers (Kunden, Kunden-Requests, Kunden-Properties) | Business | **Widerspruch:** Business (Plane University 202 „Business tier“; Blog „Introducing Plane Business“; Dok. 21 F04, Dok. 23 WM-16) vs. Pro „customer profiles“ (frühere WebSearch-Zusammenfassung plane.so/pricing, im Verifikationslauf nicht bestätigt – UNVERIFIZIERT) | fehlt | `apps/api/plane/bgtasks/workspace_seed_task.py` Z. 160–163; Developer-Docs `api-reference/customer/`; https://university.plane.so/courses/202-the-power-relay/02-intro-to-customers.html |
| PF-42 | Releases | unklar | – | fehlt | `apps/web/components/dropdowns/label/label-select.tsx` Z. 48; Propel-Icons `releases-*`, `release-tag-*` |
| PF-43 | Shared Views | Pro | Pro–Enterprise ✓ | fehlt | `plans.tsx` Z. 499 |
| PF-44 | Publish Views | Pro | Pro–Enterprise ✓ | teilweise im CE | `plans.tsx` Z. 510; `apps/api/plane/db/models/deploy_board.py` Z. 26 |
| PF-45 | Dashboards and Widgets | Pro | Pro–Enterprise ✓ | Stub/UI-Hülle im CE | `plans.tsx` Z. 521; `apps/web/components/workspace/sidebar/user-menu.tsx`; `packages/constants/src/chart.ts` |
| PF-46 | Progress Charts (über Cycles, Module, Overviews hinaus) | Pro | Pro–Enterprise ✓ | teilweise im CE | `plans.tsx` Z. 538; `apps/web/components/cycles/analytics-sidebar/sidebar-chart.tsx` |
| PF-47 | Cycle Reports (Permalinks) | Pro | Pro–Enterprise ✓ | teilweise im CE | `plans.tsx` Z. 550; `apps/api/plane/db/models/cycle.py` Z. 74 |
| PF-48 | Insights (Hindsight, On-demand, Foresights) | Pro | Pro–Enterprise ✓ (Coming soon) | fehlt | `plans.tsx` Z. 561 |
| PF-49 | Advanced Pages Analytics | Business | Business/Enterprise ✓ (Coming soon) | fehlt | `plans.tsx` Z. 585 |
| PF-50 | Custom Reports / erweiterte Analytics-Tabs | Business | Business/Enterprise ✓ (Coming soon) | teilweise im CE | `plans.tsx` Z. 597; `workspace_analytics.tabs.custom`, `workspace_analytics.upgrade_to_plan` |
| PF-51 | Time Capsule | Business | Business/Enterprise ✓ (Zeile auskommentiert, Coming soon) | fehlt | `plans.tsx` Z. 573 |
| PF-52 | PQL / erweiterte Filteroperatoren | Pro | Pro–Enterprise ✓ | Stub/UI-Hülle im CE | `plans.tsx` Z. 658; `apps/api/plane/api/views/issue.py` Z. 324–335; `apps/web/hooks/rich-filters/use-filters-operator-configs.ts` |
| PF-53 | Advanced Search (OpenSearch) | Pro | Doku-Badge `[Pro]` | fehlt | `self-hosting/govern/advanced-search.md`; `power_k.search_menu.go_to_advanced_search` |
| PF-54 | Rollen: Pre-defined Roles / RBAC / GAC | Pro | Free/One „Basic“; Pro „Pre-defined roles“; Business „RBAC“; Enterprise „GAC“ | teilweise im CE | `plans.tsx` Z. 695; `apps/api/plane/db/models/workspace.py` Z. 19 |
| PF-55 | Member-/Seat-/Guest-Limits | One | Member limit SH ~50/~50/~200/~200/Unlimited; Guests „5 per paid member“ ab One | im CE vorhanden (nur Cloud-Gating): CE kennt Guests und erzwingt keine Seat-/Guest-Limits; Limits entfallen (ADR-001) | `plans.tsx` Z. 676, 706; `apps/api/plane/db/models/workspace.py` Z. 19 |
| PF-56 | Approvals (Workspace-, Projekt-, Work-Item-Type-Approvals) | Business | Business/Enterprise ✓ (Coming soon) | fehlt | `plans.tsx` Z. 717 |
| PF-57 | Admin Interface | Business | Business/Enterprise ✓ | fehlt | `plans.tsx` Z. 729 |
| PF-58 | Workspace Activity Logs | Business | Business/Enterprise ✓ | teilweise im CE (Aktivität je Mitglied im Workspace inkl. Projektfilter und CSV-Export je Tag; workspaceweites, filterbares Log fehlt; `mutateWorkspaceMembersActivity` No-op) | `plans.tsx` Z. 740; `apps/web/store/workspace/index.ts` Z. 385–391; `apps/api/plane/app/urls/workspace.py` Z. 137–146; `apps/api/plane/app/views/workspace/user.py` Z. 409–435; `apps/api/plane/app/views/workspace/base.py` Z. 340–361 |
| PF-59 | API-enabled Audit Logs | Business | Business/Enterprise ✓ (Coming soon); WebSearch: Enterprise Grid „API audit logs“ | fehlt | `plans.tsx` Z. 751 |
| PF-60 | Mitglieder-Import per CSV (Workspace und Projekt) | unklar | – | fehlt | `workspace.members_import.*` (`workspace.json`), `project.members_import.*` (`project.json`) |
| PF-61 | Multi-Workspace-Management (Organisationsebene) | Enterprise (Grid) | WebSearch | fehlt | https://plane.so/business ; https://plane.so/self-hosted/whitepaper |
| PF-62 | Workspace-Access-Tokens | unklar | – | fehlt | `settings_empty_state.workspace_tokens` (`empty-state.json`) |
| PF-63 | Custom Automations (Trigger → Bedingung → Aktion, Zeitplan/Cron) | Business | **Widerspruch:** `plans.tsx` „Trigger And Action“ ab Pro; Doku 2026 (über Dok. 25 F09, verifiziert in `_data/P06.paid.json`): Business = Projekt-Automationen mit „Change property“/„Add comment“, Enterprise Grid = zusätzlich „Send webhook“, „Run script“, Scheduled (Cron) und global. Aktuellere Quelle gewinnt → Business | fehlt | `plans.tsx` Z. 769; `packages/i18n/src/locales/en/automation.json`; `25-paid-workflows-automation-templates.md` F09–F14 |
| PF-64 | Globale (Workspace-)Automationen | Enterprise Grid | nur Enterprise Grid (Dok. 25 F13, Web-Beleg); kein Repo-Beleg | fehlt | `automations.global_automations.*`; `25-paid-workflows-automation-templates.md` F13 |
| PF-65 | Decisions And Loops Automation | Business | Business/Enterprise ✓ (Coming soon) | fehlt | `plans.tsx` Z. 780 |
| PF-66 | Anzahl Automationen | Pro | Pro 5,000; Business 10,000; Enterprise Unlimited | entfällt (ADR-001) | `plans.tsx` Z. 792 |
| PF-67 | Auto-Reminders | Business | Business und höher nur laut Web-Beleg in Dok. 25 (Auto-Reminders); kein Repo-Beleg | fehlt | `project_settings.automations.auto-remind.*`; `25-paid-workflows-automation-templates.md` |
| PF-68 | Workflows (State-Übergänge, Reviewer, Erstellung je State) | Business | `BUSINESS_PLAN_FEATURES` „Workflows + Approvals“; Doku 2026 (Dok. 25 F01/F02): Business = ein Default-Workflow je Projekt, Enterprise Grid = mehrere typ-spezifische Workflows; Pro-Angabe „single workflow per project“ (frühere WebSearch) UNVERIFIZIERT | Stub/UI-Hülle im CE | `packages/constants/src/subscription.ts` Z. 18; `apps/web/components/workflow/use-workflow-drag-n-drop.ts`; `packages/i18n/src/locales/en/workflow.json`; `apps/web/components/common/activity/helper.tsx` Z. 69, 274–277 |
| PF-69 | Plane Runner / Scripts („Run Script“-Aktion) | Enterprise Grid | nur Enterprise Grid (Dok. 25 F19, Dok. 22 P03-F28, Web-Belege); kein Repo-Beleg | fehlt | `workspace_settings.settings.runners`; `automations.action.handler_name.run_script` |
| PF-70 | Real-time Collab (Live-Cursor/Presence) | One | One–Enterprise ✓ (Upsell-Text `wiki.upgrade_flow.description` nennt „real-time collaboration … with Plane Pro“; One nicht mehr erhältlich) | teilweise im CE | `plans.tsx` Z. 820; `apps/web/hooks/use-editor-flagging.ts` |
| PF-71 | Work item Embeds in Pages | One | One–Enterprise ✓ (Dok. 26: Doku-Label „Work item Pro“; One nicht mehr erhältlich) | Stub/UI-Hülle im CE (interaktive Extension vorhanden, aber nicht registriert; kein Slash-Befehl) | `plans.tsx` Z. 831; `packages/editor/src/extensions/core-without-props.ts` Z. 66; `packages/editor/src/extensions/document-extensions.tsx` |
| PF-72 | Link-to-work items (Pages ↔ Work Items) | One | One–Enterprise ✓ | fehlt | `plans.tsx` Z. 842; `issue.pages.*` |
| PF-73 | Publish Pages | One | One–Enterprise ✓ (Dok. 26: Doku „Publish erfordert Pro“; One nicht mehr erhältlich) | Stub/UI-Hülle im CE (nur Choice `("page", "Page")` in `DeployBoard`; keine UI, keine Space-Route, kein Endpunkt) | `plans.tsx` Z. 853; `apps/api/plane/db/models/deploy_board.py` Z. 25; `apps/space/app/routes.ts` |
| PF-74 | Wiki (Workspace-Pages) inkl. Collections | Pro | **Widerspruch:** `plans.tsx` One–Enterprise; spezifischer und aktueller: Upsell-Text „Upgrade to unlock Wiki … with Plane Pro.“ (`wiki.upgrade_flow.description`), `PRO_PLAN_FEATURES` „Wikis“, Doku „Wiki Pro and above“, „Collections Pro“ (WebSearch Verifikation; Dok. 26) → Pro. Private Collections: Business (Dok. 26, WebSearch) | Stub/UI-Hülle im CE | `plans.tsx` Z. 865; `apps/api/plane/db/models/page.py` Z. 51; `packages/i18n/src/locales/en/wiki.json`; https://docs.plane.so/pages/collections |
| PF-75 | Page-Exports (Word-kompatibel, Warteschlange) | Pro | Pro „One download at a time“; Business/Enterprise „Queued downloads“ | teilweise im CE | `plans.tsx` Z. 876; `apps/web/components/pages/modals/export-page-modal.tsx` |
| PF-76 | Page-Versionen (Aufbewahrung, Änderungs-Hervorhebung) | Pro | Pro „2 days“; Business „3 months“; Enterprise „Unlimited“ | teilweise im CE | `plans.tsx` Z. 898; `apps/api/plane/bgtasks/page_version_task.py` Z. 72–74 |
| PF-77 | Databases + Formulas in Pages | Business | Business/Enterprise ✓ (Coming soon) | fehlt | `plans.tsx` Z. 909 |
| PF-78 | Nested Pages | Business | Business/Enterprise ✓ (Coming soon) | teilweise im CE | `plans.tsx` Z. 922; `apps/api/plane/db/models/page.py` Z. 40–46 |
| PF-79 | Page-Kommentare | Business | Inline-Kommentare Business (nur Web-Beleg über Dok. 26); Page-Level-Kommentare ohne Plan-Angabe; Upsell-Tab „Comments“ (`wiki.upgrade_flow.tabs.comments`) nennt nur „paid plan“ | fehlt | `page_navigation_pane.tabs.comments.*`; `26-paid-wissen-pages-wiki.md` |
| PF-80 | Pages verschieben / teilen | Pro | Moving Pages Pro, Page-Sharing Business (Doku-Labels über Dok. 26, nicht selbst geprüft) | Stub/UI-Hülle im CE (Flags `false`; Store-Aktion `movePage` und Service `move` → nicht existierender Endpunkt `pages/{id}/move/`) | `apps/web/hooks/use-page-flag.ts`; `apps/web/store/pages/project-page.store.ts` Z. 352–369; `apps/web/services/page/project-page.service.ts` Z. 185–193 |
| PF-81 | Editor: Datei-Anhänge und externe Embeds | Pro | Doku-Labels „Attachment Pro“, „Embed Pro“ (über Dok. 26, nicht selbst geprüft); Repo-Text „Upgrade your plan to view this attachment.“ ohne Planname | Stub/UI-Hülle im CE (Extension-Points S15, S16, S48) | `packages/i18n/src/locales/en/editor.json`; `apps/web/hooks/editor/use-extended-editor-config.ts`; `packages/editor/src/types/editor-extended.ts` |
| PF-82 | Plane AI (Pi-Chat, AI-Block, Agents, MCP-Connectors, AI-Credits) | Pro | WebSearch: Pro 1,000 AI credits/Seat/Monat; Business höher (Drittquelle 2,000); Self-hosted: Commercial Edition (Doku-Badge), Plan nicht belegt (Dok. 22 P03-F12: unklar) | teilweise im CE | `apps/web/components/workspace/sidebar/sidebar-item.tsx` Z. 52; `apps/web/hooks/use-editor-flagging.ts`; `apps/web/services/ai.service.ts` Z. 37–48; `self-hosting/govern/plane-ai/configure-plane-ai.md` |
| PF-83 | Importer (Jira, GitHub; weitere Importer siehe Dok. 28) mit Custom Props | Pro | Free/One „Without custom props“ (gilt für Cloud/Commercial Free, nicht für die CE); Pro+ „With custom props“ | Stub/UI-Hülle im CE (Legacy-Modell `Importer`, `IMPORTERS_LIST`, Services gegen nicht existierende `importers/`-Endpunkte; keine Route) | `plans.tsx` Z. 940, 951; `packages/constants/src/workspace.ts` (`IMPORTERS_LIST`); `apps/web/services/integrations/{integration,github,jira}.service.ts` |
| PF-84 | GitHub-Integration (inkl. GitHub Enterprise) | Pro | Pro–Enterprise ✓ (Sektion Coming soon; Doku-Badge `[Pro]`) | Stub/UI-Hülle im CE (Legacy-Modelle ohne View/URL, ungeroutete Seite, tote Service-Aufrufe) | `plans.tsx` Z. 969; `apps/api/plane/db/models/integration/github.py`; `github_integration.*`, `github_enterprise_integration.*` |
| PF-85 | GitLab-Integration (inkl. GitLab Enterprise) | Pro | Doku-Badge `[Pro]` | fehlt | `self-hosting/govern/integrations/gitlab.md`; `gitlab_integration.*`, `gitlab_enterprise_integration.*` |
| PF-86 | Slack-Integration | Pro | Pro–Enterprise ✓ (Coming soon; Doku-Badge `[Pro]`) | Stub/UI-Hülle im CE (Legacy-Modell `SlackProjectSync` ohne View/URL, tote Service-Aufrufe `project-slack-sync/`) | `plans.tsx` Z. 981; `apps/api/plane/db/models/integration/slack.py`; `apps/web/services/app_installation.service.ts` Z. 18–62; `slack_integration.*` |
| PF-87 | Sentry-Integration | Pro | Doku-Badge `[Pro]` | fehlt | `self-hosting/govern/integrations/sentry.md`; `sentry_integration.*` |
| PF-88 | Bitbucket-Data-Center-Integration | Pro | Doku-Badge `[Pro]` | fehlt | `self-hosting/govern/integrations/bitbucket.md`; `bitbucket_dc_integration.*` |
| PF-89 | Zapier | Pro | Pro–Enterprise ✓ (Coming soon) | fehlt | `plans.tsx` Z. 992 |
| PF-90 | Zendesk / Freshdesk | Pro | Pro–Enterprise ✓ (Coming soon) | fehlt | `plans.tsx` Z. 1003, 1014 |
| PF-91 | OAuth Bridge (externe IdP-JWTs für API) | unklar | – | fehlt | `oauth_bridge_integration.*` (`integration.json`) |
| PF-92 | Applications / OAuth-Apps / Marketplace / App-Mentions | unklar | – | fehlt | `workspace_settings.settings.applications.*`; Developer-Docs `dev-tools/build-plane-app/` |
| PF-93 | Workspace-SSO SAML/OIDC mit Domain-Verifizierung („Identity“) | One | SAML/OIDC One–Enterprise ✓ (Doku-Badges `[Pro] [Business]`); für die Workspace-Identity (Domain-Verifizierung) selbst ist kein Plan belegt (Dok. 22 P03-F06, Dok. 27: unklar) | Stub/UI-Hülle im CE (Extension-Points S17, S43, S52, S53) | `plans.tsx` Z. 1060, 1071; `packages/i18n/src/locales/en/auth.json` (`sso.*`); `packages/types/src/instance/auth-ee.ts` |
| PF-94 | Domain Security | Pro | Pro–Enterprise ✓ | fehlt | `plans.tsx` Z. 1083 |
| PF-95 | Zwei-Faktor-Authentifizierung und Passkeys | Pro | Pro–Enterprise ✓ | fehlt | `plans.tsx` Z. 1095 |
| PF-96 | Password Policy | Pro | Pro–Enterprise ✓ | fehlt | `plans.tsx` Z. 1106 |
| PF-97 | LDAP | Enterprise Grid | `plans.tsx` nur `enterprise` (Coming soon); Doku-Badge `[Enterprise Grid]` („active Enterprise Grid license“) – aktuellere Quelle → Enterprise Grid | Stub/UI-Hülle im CE (Login-Extension-Points S17, S52, S53; Texte `auth.ldap.*`) | `plans.tsx` Z. 1117; `self-hosting/govern/ldap.md`; `auth.ldap.header.*` |
| PF-98 | IdP-Group-Sync (+ SCIM) | Enterprise Grid | WebSearch Whitepaper: „LDAP, SCIM, IdP group synchronization, custom roles … Enterprise Grid“; Dok. 22/27: Enterprise Grid, nur Self-hosted Commercial, nur OIDC | fehlt (nur Texte/Icons; Dok. 21/22/27 werten dies als „Stub“, im CE existiert aber kein Extension-Point dafür) | `workspace_settings.settings.group_syncing.*`; Developer-Docs `api-reference/idp-group-sync/` |
| PF-99 | Storage-Quoten / Max-File-Size je Plan | Cloud-only | Free 5GB/5 MB; Pro 1 TB/100 MB; Business 5 TB/200 MB; Enterprise Custom | entfällt (ADR-004) | `plans.tsx` Z. 1032, 1043 |
| PF-100 | Deployment-Varianten / Private deployments | One | One+ One-click/DO/Heroku/AWS; Enterprise „Private deployments“ (Coming soon); Airgapped/FIPS Enterprise Grid (Doku-Badges) | teilweise im CE (Install-Skript, Docker Compose, AIO, Kubernetes, Swarm, `restore-airgapped.sh`); Marketplace-Apps und Private deployments entfallen (ADR-004) | `plans.tsx` Z. 1147–1201; `deployments/cli/community/`; `deployments/{aio,kubernetes,swarm}/community` |
| PF-101 | Support-Kanäle / Support-SLA | Pro | Free Forum; One Mail+Forum; Pro +Chat; Business/Enterprise Full-suite | entfällt | `plans.tsx` Z. 1209, 1235 |
| PF-102 | Product Tour / „Get started“-Checkliste / Demo-Projekt | unklar (Cloud-Onboarding) | – | fehlt | `packages/i18n/src/locales/en/tour.json` |
| PF-103 | Billing, Trial, Seats, Upgrade-Flows | Cloud-only | Cloud bzw. Commercial Edition | Stub/UI-Hülle im CE (Billing-/Upsell-UI ohne Abrechnung, Abschnitt 5); entfällt (ADR-001) | Abschnitt 2.17, Abschnitt 5 |
| PF-104 | Duplicate Detection (Duplikat-Vorschläge beim Anlegen von Work Items und Intake-Requests) | unklar | Commercial Edition (Plane AI, benötigt Embedding-Modell; Dok. 22 P03-F13, Dok. 28); Plan nicht belegt | Stub/UI-Hülle im CE (Typen, No-op-Hook, Modal-State, Texte) | `packages/types/src/de-dupe.ts`; `apps/web/hooks/use-debounced-duplicate-issues.tsx`; `apps/web/components/issues/issue-modal/base.tsx` Z. 68, 382, 405; `apps/web/components/inbox/modals/create-modal/modal.tsx` Z. 23–45; `packages/i18n/src/locales/en/common.json` Z. 284–285 |
| PF-105 | Weitere Commercial-Produkte ohne Funktionsspur (Desk, Bridge, Briefs, Workgraph, PII-Scanner „Argus“, Library/Excerpts; reservierte Slugs `chat`, `calendar`, `drive`, `channels`) | unklar | keine Plan-Angabe im Repo; PII-Scanner: Produkt-Flag `PII_SCANNER`, Changelog v3.2.0 (Dok. 22 P03-F33, Dok. 27, sekundär) | fehlt (nur Propel-Icons bzw. Slugs) | Propel 0.7.3 `dist/icons/sub-brands/{desk,bridge}.d.ts`, `workspace-features/{briefs,workgraph}-{outline,filled}.d.ts`, `miscellaneous/{pii-scanner,library,library-alt,excerpt,insert-excerpt}-{outline,filled}.d.ts`; `packages/constants/src/workspace.ts` (`RESTRICTED_URLS`) |

---

## 4. Feature-Abschnitte

Aufbau je Feature: **Tier** · **Funktionsbeschreibung (UI & Verhalten)** · **UI-Hinweise (1:1)** · **Datenmodell-Hinweise** · **API-Hinweise** · **Im CE vorhanden** · **Fehlt (für Portierung zu bauen)** · **Quellen** · **Konfidenz**. Wörtliche UI-Texte stammen aus `packages/i18n/src/locales/en/*.json` und sind in den Ziel-i18n-Dateien 1:1 zu übernehmen (ADR-005/ADR-006). Migrationsregel für alle Features: Upsell-Elemente (`UpgradeBadge`, „Upgrade“-Buttons, `PaidPlanUpgradeModal`) entfallen; an ihrer Stelle erscheint die echte Funktion (ADR-001).

### 4.1 Projekt- und Arbeitsmanagement

#### PF-01 – Advanced Estimates
- **Tier:** Free/One „Basic“, Pro/Business/Enterprise „Advanced“ (`plans.tsx` Z. 145–154).
- **Funktionsbeschreibung:** „Basic“ (CE) = Estimate-System anlegen (Typ `points` oder `categories`) aus Vorlagen bzw. „Custom“, Estimate löschen, Projekt-Estimate aktivieren/deaktivieren. „Advanced“ ergänzt (abgeleitet aus nicht referenzierten Texten): (a) **Time-Estimates** (System `time`, Vorlage „Hours“ mit Werten 1–6, Anzeige über `convertMinutesToHoursMinutesString`), (b) **Bearbeiten** eines bestehenden Systems: Punkte hinzufügen/ändern („Add or update“ – `project_settings.estimates.edit.add_or_update.*`), (c) **Systemwechsel** „Change estimate type – Convert your points system to categories system and vice versa.“ (`project_settings.estimates.edit.switch.*`, `project_settings.estimates.switch` „Switch estimate system“, `…current` „Current estimate system“, `…select` „Select an estimate system“), (d) **Umsortieren** der Punkte (`project_settings.estimates.toasts.reorder.*`), Validierung `project_settings.estimates.validation.fill`/`.repeat`.
- **UI-Hinweise:** Radio-Auswahl der Systeme in `EstimateCreateStageOne`; im CE wird `time` herausgefiltert, weil `isEstimateSystemEnabled` nur `points`/`categories` zulässt; der Zweig mit `UpgradeBadge` neben dem Systemnamen (`cursor-no-drop text-tertiary`) ist das EE-Muster für gesperrte Systeme. Im CE fehlt der Edit-Button: `EstimateListItemButtons` rendert nur den Löschen-Button, `onEditClick` wird nicht verwendet.
- **Datenmodell-Hinweise:** CE-`EstimateType` kennt nur `categories`, `points` (`apps/api/plane/db/models/estimate.py` Z. 13–15); EE benötigt zusätzlich `time` (Werte in Minuten, vgl. `convertMinutesToHoursMinutesString`). `EstimatePoint.key` (int ≥ 0), `value` (≤255), `description`. Konstante `estimateCount = {min: 2, max: 6}`, `MAX_ESTIMATE_POINT_INPUT_LENGTH = 20` (`packages/constants/src/estimates.ts`).
- **API-Hinweise:** Endpunkte für Update/Reorder/Switch fehlen im CE; P02 beschreibt die öffentliche Estimate-API (`21-paid-api-referenz-developer-docs.md` §2.5).
- **Im CE vorhanden:** `ESTIMATE_SYSTEMS.time` mit `is_ee: true` (`packages/constants/src/estimates.ts` Z. 122–141), `EEstimateSystem.TIME`, `EEstimateUpdateStages` (`CREATE`, `EDIT`, `SWITCH`), `EstimateInputRoot` mit leerem `TIME`-Zweig (`apps/web/components/estimates/inputs/root.tsx`).
- **Fehlt:** Time-System inkl. Eingabe (Stunden/Minuten), Edit-/Switch-/Reorder-Flows, Backend-Validierung.
- **Quellen:** `apps/web/components/estimates/create/stage-one.tsx`, `apps/web/components/estimates/create/helper.tsx`, `apps/web/components/estimates/estimate-list-item-buttons.tsx`, `packages/i18n/src/locales/en/project-settings.json` (`project_settings.estimates.*`).
- **Konfidenz:** hoch (Time-System, Edit/Switch) / mittel (genaue Reorder-Semantik).

#### PF-02 – Bulk Ops
- **Tier:** One „Limited props“; Pro „All props“; Business/Enterprise zusätzlich „Work item transfers and conversions“ (Coming soon) (`plans.tsx` Z. 162–181). Upgrade-Karten: `PRO_PLAN_FEATURES` „Full Time Tracking + Bulk Ops“, `ONE_PLAN_FEATURES` „Time-tracking + limited bulk ops“.
- **Funktionsbeschreibung:** Mehrfachauswahl von Work Items in List-, Spreadsheet- und Gantt-Layout; danach am unteren Rand eine Aktionsleiste („Change state, priority, and more for several work items at once. Save three minutes on an average per operation.“ – `bulk_operations.upgrade_banner.message`). Aktionen lt. Matrix-Beschreibung: „Add several work items to cycles or modules, transfer them, or edit their properties.“ Fehlermeldungen der Bulk-Operation (`bulk_operations.error_details.*`): „Unable to archive work items – Only work items belonging to Completed or Canceled state groups can be archived.“, „Unable to update work items – Start date selected succeeds the due date for some work items…“, „…Due date selected precedes the start date…“, „…State change is not allowed for some work items. Ensure the state change is allowed.“ (Workflow-Bezug, PF-68).
- **UI-Hinweise:** Banner-Container `sticky bottom-0 left-0 z-[2] grid h-20 place-items-center px-3.5`, `Banner placement="inline" variant="accent"` (`apps/web/components/issues/bulk-operations/root.tsx`). Für die Portierung ersetzt die echte Aktionsleiste den Banner an derselben Stelle.
- **Datenmodell-Hinweise:** keine eigenen Tabellen; Bulk-Endpunkt mit Liste von Issue-IDs und Property-Patch.
- **API-Hinweise (korrigiert im Verifikationslauf):** Das CE-Frontend enthält den Vertrag bereits: `IssueService.bulkOperations(workspaceSlug, projectId, data)` → `POST /api/workspaces/{slug}/projects/{pid}/bulk-operation-issues/` (`apps/web/services/issue/issue.service.ts` Z. 339–345) mit Payload `TBulkOperationsPayload = {issue_ids: string[], properties: Partial<TBulkIssueProperties>}`, wobei `TBulkIssueProperties = Pick<TIssue, "state_id" | "priority" | "label_ids" | "assignee_ids" | "start_date" | "target_date" | "module_ids" | "cycle_id" | "estimate_point">` (`packages/types/src/issues/issue.ts` Z. 140–156). Store-Aktion `bulkUpdateProperties` (`apps/web/store/issue/helpers/base-issues.store.ts` Z. 718–753): Array-Werte (`label_ids`, `assignee_ids`, `module_ids`) werden an die bestehenden Werte **angehängt** (`uniq([...bestehend, ...neu])`), skalare Werte ersetzt; im Workspace-Draft-Store ist die Aktion ein No-op (`apps/web/store/issue/workspace-draft/issue.store.ts` Z. 428). **Die Backend-Route fehlt im CE** (Abschnitt 9.3). Vorhanden im CE sind nur Bulk-Delete/-Archive (siehe Kern-Analyse).
- **Im CE vorhanden:** `useBulkOperationStatus = () => false` (`apps/web/hooks/use-bulk-operation-status.ts`) – wird ausgewertet in `apps/web/components/issues/issue-layouts/spreadsheet/spreadsheet-view.tsx` Z. 66/87, `…/list/default.tsx` Z. 86/137, `…/gantt/base-gantt-root.tsx` Z. 61/143, `apps/web/components/gantt-chart/chart/main-content.tsx` Z. 28; Auswahl-Infrastruktur `useMultipleSelectStore`, `TSelectionHelper` (`apps/web/hooks/use-multiple-select.ts`). Da die Auswahl im CE deaktiviert ist (`isSelectionDisabled`), wird der Upsell-Banner faktisch nie sichtbar.
- **Fehlt:** Aktionsleiste mit allen Property-Editoren, Transfer/Conversion, Backend-Bulk-Endpunkt inkl. Validierungen oben.
- **Quellen:** `plans.tsx`, `packages/i18n/src/locales/en/work-item.json` (`bulk_operations.*`), `packages/constants/src/subscription.ts`.
- **Konfidenz:** hoch (Existenz, Fehlertexte) / mittel (exakter Umfang „Limited props“ vs. „All props“ – nicht spezifiziert; ADR-001 → immer „All props“).

#### PF-03 – Time Tracking + Worklogs
- **Tier:** One „Basic“; Pro „Historical timesheets“; Business/Enterprise „Historical timesheets and approvals“ (`plans.tsx` Z. 183–192); Highlights One „Limited time tracking“, Pro „Full Time Tracking“.
- **Funktionsbeschreibung:** Projekt-Feature-Toggle „Time tracking – Log time spent on work items and projects.“ mit Schalter „Enable time tracking – Project members will be able to log time worked.“ (`project_settings.features.time_tracking.*`). Im Work Item werden Zeiteinträge (Worklogs) erfasst; Aktivitätsfeed kennt den Typ `WORKLOG` und den Leerzustand „No worklogs yet“ (`common.activity_empty_state.no_worklogs`). Workspace-Einstellung „Worklogs – Download worklogs AKA timesheets for anyone in any project.“ (`workspace_settings.settings.worklogs.*`); Leerzustand „Track timesheets for all members – Log time on work items to view detailed timesheets for any team member across projects.“ (`settings_empty_state.worklogs`). „Approvals“ (Business) = Freigabe von Timesheets (nur Matrix-Text).
- **UI-Hinweise:** Icons `TimeTrackingOutline/Filled` (Workspace-Features), `AddTimeTrackingOutline/Filled` (Actions), `TimeEntriesOutline/Filled` (Misc); Aktivitäts-Icon für `is_time_tracking_enabled` = `TimeTrackingOutline` (`apps/web/components/common/activity/helper.tsx` Z. 34, 70, 278); Illustration `worklog` (horizontal stack, `packages/blocks/src/empty-state/assets/horizontal-stack/worklog.tsx`).
- **Datenmodell-Hinweise:** `Project.is_time_tracking_enabled` (Bool, default `false`, `apps/api/plane/db/models/project.py` Z. 100; im öffentlichen Projekt-Serializer `apps/api/plane/api/serializers/project.py` Z. 94). Worklog-Entität (Work Item, Benutzer, Dauer, Beschreibung, Datum) – Felder siehe P02 §4.6. Export-Typ `ExporterHistory.type = "issue_worklogs"` („Issue Worklogs“) existiert bereits (`apps/api/plane/db/models/exporter.py` Z. 31).
- **API-Hinweise:** Developer-Docs `api-reference/worklogs/` (create, list for issue, update, delete, get-total-time) → P02 §2.17/§4.6.
- **Im CE vorhanden:** Feld, Export-Typ, Activity-Typ `WORKLOG` (`packages/types/src/issues/activity/base.ts` Z. 80–83), Activity-Darstellung des Toggles.
- **Fehlt:** Worklog-Tabelle/-Endpunkte, Work-Item-Widget „Log time“, Projekt-Feature-Seite, Workspace-Worklogs-Seite mit Download (CSV/XLSX), Timesheet-Historie, Approvals.
- **Quellen:** wie genannt; `packages/i18n/src/locales/en/common.json` Z. 222/231 („Time Tracking“, „Log time spent on work items and projects.“).
- **Konfidenz:** hoch (Existenz/Texte) / niedrig (Approval-Workflow-Details).

#### PF-04 – Active Cycles (Workspace)
- **Tier:** One–Enterprise (`plans.tsx` Z. 194–203; Highlight One „Active cycles“).
- **Funktionsbeschreibung:** Workspace-Seite `/:workspaceSlug/active-cycles` mit allen laufenden Cycles aller Projekte (Matrix: „See all running cycles across all projects, or soon, in a single project.“). Funktionsumfang laut Upsell-Kacheln (`WORKSPACE_ACTIVE_CYCLES_DETAILS`): (1) „10,000-feet view of all active cycles. – Zoom out to see running cycles across all your projects at once instead of going from Cycle to Cycle in each project.“ (2) „Get a snapshot of each active cycle. – Track high-level metrics for all active cycles, see their state of progress, and get a sense of scope against deadlines.“ (3) „Compare burndowns. – Monitor how each of your teams are performing with a peek into each cycle's burndown report.“ (4) „Quickly see make-or-break work items. – Preview high-priority work items for each cycle against due dates. See all of them per cycle in one click.“ (5) „Zoom into cycles that need attention. – Investigate the state of any cycle that doesn't conform to expectations in one click.“ (6) „Stay ahead of blockers. – Spot challenges from one project to another and see inter-cycle dependencies that aren't obvious from any other view.“ Leerzustand: „No active cycles – You don't have any ongoing cycles right now. Active cycles appear here when they include today's date.“ (`workspace_empty_state.active_cycles`). Leerzustände der Karten: `active_cycle_analytics.empty_state.{progress,priority,assignee,label}.title` (mit Zeilenumbruch) in `packages/i18n/src/locales/en/cycle.json`.
- **UI-Hinweise:** Header `WorkspaceActiveCycleHeader` (Breadcrumb mit `CyclesOutline rotate-180`, Label `t("active_cycles")`) – `UpgradeBadge size="md"` entfällt. Sidebar: Eintrag `active-cycles` mit Label `sidebar.cycles` im Workspace-Menü (`apps/web/components/workspace/sidebar/workspace-menu.tsx` Z. 47–49) und Icon-Rotation `rotate-180` für `active_cycles` (`workspace-menu-item.tsx` Z. 64). Die Karten wiederverwenden die CE-Komponenten des projektinternen Active Cycle (`apps/web/components/cycles/active-cycle/{cycle-stats,productivity,progress,root}.tsx`).
- **Datenmodell-Hinweise:** keine neuen Tabellen; Abfrage aller `Cycle` mit `start_date <= now <= end_date` über alle Projekte, auf die der Benutzer Zugriff hat.
- **API-Hinweise:** Frontend ruft bereits `GET /api/workspaces/{slug}/active-cycles/?per_page=&cursor=` auf (`apps/web/services/cycle.service.ts` Z. 64–78; `packages/services/src/cycle/cycle.service.ts` Z. 34); Antworttyp `IWorkspaceActiveCyclesResponse {count, extra_stats, next_cursor, next_page_results, prev_cursor, prev_page_results, results: ICycle[], total_pages}` (`packages/types/src/workspace.ts` Z. 219–228). **Der Endpunkt existiert im CE-Backend nicht** (`grep active-cycles apps/api/plane` → keine Treffer).
- **Im CE vorhanden:** Route (`apps/web/app/routes/core.ts` Z. 66–67), Seite mit Upsell (`apps/web/app/(all)/[workspaceSlug]/(projects)/active-cycles/page.tsx`), Service, Typ, Assets `apps/web/app/assets/workspace-active-cycles/cta-*-{dark,light}.webp`.
- **Fehlt:** Backend-Endpunkt (Cursor-Pagination), Listen-UI mit je Cycle Stats/Burndown/Priority-Items, Power-K-Aktion `power_k.navigation_actions.nav_workspace_active_cycle`.
- **Ergänzung (Verifikation):** Backend-Spur `WorkspaceUserPreference.UserPreferenceKeys.ACTIVE_CYCLES = "active_cycles"` (`apps/api/plane/db/models/workspace.py` Z. 417–427) – die Navigationspräferenz existiert, obwohl die Seite im CE nicht nutzbar ist. Zusätzlicher toter Service-Aufruf `workspaceActiveCyclesProgressPro` → `…/cycles/{cycleId}/cycle-progress/` (Abschnitt 9.3, Gruppe 8). Hinweis zur Icon-Rotation: `workspace-menu-item.tsx` Z. 64 prüft `item.key === "active_cycles"`, der Menüeintrag in `workspace-menu.tsx` Z. 47 heißt aber `active-cycles` – die Rotation greift dort nie (CE-Inkonsistenz). Tier-Hinweis: One ist laut `base.tsx` Z. 29–30 nicht mehr erhältlich; Dok. 24 vermerkt „faktisch ab Pro“.
- **Quellen:** `apps/web/components/active-cycles/workspace-active-cycles-upgrade.tsx`, `packages/i18n/src/locales/en/common.json` Z. 124–139, `packages/i18n/src/locales/en/empty-state.json`.
- **Konfidenz:** hoch.

#### PF-05 – Work item Types
- **Tier:** Pro–Enterprise (`plans.tsx` Z. 205–214; Highlight Pro „Custom work items + Properties“).
- **Funktionsbeschreibung (aus `work-item-type.json`):** Workspace-Einstellung „Work item Types – Customize and add your own properties to tailor it to your team's needs.“ Liste „Types – Create and customize work item types with properties.“ mit Sortierung „Number of projects part of“ und Filter „Show active“/„Show inactive“. Anlegen: Modal „Create work item type“ (Button „Add work item type“), Felder Name („Give this work item type a unique name“), Beschreibung („Describe what this work item type is meant for and when it's to be used.“), Icon/Hintergrund (`logo_props`), optional „Hierarchy level“ (PF-08). Konflikt: „{name} type already exists. Choose a different name.“ Aktiv/Inaktiv-Toggle mit Toast „{action} {name} work item type“. Standardtyp: „Set as default“ mit Bestätigung „Setting {name} as the default will import it to all projects in this workspace. All new work items will use this type by default.“; inaktive Typen können nicht Standard werden („Activate this type before setting it as default“); Standardtyp nicht löschbar („This work item type cannot be deleted because it's set as the default for this project“, Fehler `cannot_delete_default_work_item_type`, `cannot_delete_work_item_type_with_associated_work_items`). Löschen: „Delete this type – Deletion of types may lead to loss of existing data. Do you want to disable the type instead?“. Projekt-Ebene: Aktivierung „Enable Work item Types – Shape work items to your work with Work item types. Customize with icons, backgrounds, and properties and configure them for this project.“ mit irreversibler Bestätigung „Once enabled, Work item Types can't be disabled. – Plane's Work Item will become the default work item type for this project and will show up with its icon and background in this project.“ (Button „Setting up“ während Ausführung); Projekt-Liste mit „Create new“ und „Import from workspace“; Banner „Enable work item types to import types from workspace level“ bzw. „Work item types are disabled. Contact workspace admin to enable them in workspace settings.“. Typwechsel am Work Item: „Change work item type? – Changing the work item type may result in loss of custom property values that are specific to the current type. This action cannot be undone.“ (Button „Change type“/„Changing“).
- **UI-Hinweise:** `IssueTypeSwitcher` (CE-Stub zeigt nur `IssueIdentifier size="md"`) ist die Stelle, an der EE einen Typ-Dropdown neben dem Identifier rendert (`apps/web/components/issues/issue-type-switcher.tsx`, verwendet in `issue-detail/main-content.tsx` Z. 92 und `peek-overview/issue-detail.tsx` Z. 95). Typ-Icon vor dem Identifier über `issueTypeId`-Props in `IssueIdentifier` (`packages/types/src/issues/issue-identifier.ts`: `TIssueIdentifierWithDetails.issueTypeId`, `TIssueTypeIdentifier`), übergeben in (vollständig, `grep -rn "issueTypeId=" apps/web`): `apps/web/components/issues/issue-detail-widgets/sub-issues/issues-list/list-item.tsx` Z. 167, `apps/web/components/issues/issue-detail/parent/sibling-item.tsx` Z. 55, `apps/web/components/issues/issue-detail/parent-select.tsx` Z. 99, `apps/web/components/issues/relations/issue-list-item.tsx` Z. 141, `apps/web/components/issues/issue-modal/components/parent-tag.tsx` Z. 54, `apps/web/components/issues/issue-modal/components/default-properties.tsx` Z. 272, `apps/web/components/issues/preview-card/root.tsx` Z. 49, `apps/web/components/issues/parent-issues-list-modal.tsx` Z. 175, `apps/web/components/home/widgets/recents/issue.tsx` Z. 77, `apps/web/components/power-k/ui/modal/search-results-map.tsx` Z. 52, `apps/web/components/core/modals/existing-issues-list-modal.tsx` Z. 198 und 294, `apps/web/components/core/modals/bulk-delete-issues-modal-item.tsx` Z. 40. Display-Property `issue_type` (`IIssueDisplayProperties.issue_type`, `packages/types/src/view-props.ts` Z. 177; List-Block `apps/web/components/issues/issue-layouts/list/block.tsx` Z. 232). Quick-Action „Edit“ wird ausgeblendet, wenn `issueTypeDetail.is_active === false` (`quick-action-dropdowns/helper.tsx` Z. 100, 219). Leerzustand Settings: „Create and customize work item types – Define unique work item types for your project. Each type can have its own properties, workflows, and fields…“ (CTA „Enable“).
- **Datenmodell-Hinweise (CE):** `IssueType` (Workspace-Ebene): `workspace`, `name`, `description`, `logo_props` (JSON), `is_epic`, `is_default`, `is_active`, `level` (Float), `external_source`, `external_id` (`apps/api/plane/db/models/issue_type.py`). `ProjectIssueType`: `project`, `issue_type`, `level` (PositiveInt), `is_default`; Unique (`project`,`issue_type`) bei `deleted_at IS NULL`. `Issue.type` FK `SET_NULL`, `related_name="issue_type"` (`issue.py` Z. 164–170), `DraftIssue.type` (`draft.py` Z. 71–73). `Project.is_issue_type_enabled` (Z. 101). Beim Anlegen über die öffentliche API wird ohne `type_id` der Projekt-Default-Typ gesetzt (`apps/api/plane/api/serializers/issue.py` Z. 190–197). Seeds setzen `display_properties.issue_type = True` (`apps/api/plane/bgtasks/workspace_seed_task.py` Z. 157).
- **API-Hinweise:** CE-Serializer liefern `type_id` (u. a. `apps/api/plane/app/serializers/draft.py` Z. 359, `apps/api/plane/app/views/search/base.py` Z. 446/658, `apps/api/plane/app/views/workspace/draft.py` Z. 175, `apps/api/plane/bgtasks/issue_version_sync.py` Z. 171). CRUD-Endpunkte für Typen fehlen im CE; öffentliche Verträge: Developer-Docs `api-reference/issue-types/types/` → P02 §2.12/§4.7. Projekt-Feature-Flag `work_item_types` (Developer-Docs `api-reference/project-features/overview.md`).
- **Im CE vorhanden:** Models, Felder, Serialisierung `type_id`, Identifier-Props.
- **Fehlt:** Workspace- und Projekt-Settings-Seiten, Typ-CRUD, Aktivierung/Import, Typwechsel inkl. Property-Wert-Verlust, Default-Handling.
- **Quellen:** wie genannt; `packages/i18n/src/locales/en/work-item-type.json` (`work_item_types.*`), `packages/i18n/src/locales/en/project-settings.json` (`project_settings.work_item_types.*`), `packages/i18n/src/locales/en/empty-state.json` (`settings_empty_state.work_item_types`).
- **Konfidenz:** hoch.

#### PF-06 – Custom Properties (Projekt-Ebene)
- **Tier:** Pro „Project-level custom properties“ (`plans.tsx` Z. 216–225).
- **Funktionsbeschreibung (aus `work-item-type.json` `work_item_types.settings.properties.*`):** Je Work-Item-Type eine Property-Liste „Properties – Create and customize properties.“ (Tooltip: „Each work item type comes with a default set of properties like Title, Description, Assignee, State, Priority, Start date, Due date, Module, Cycle etc. You can also customize and add your own properties…“). Button „Add new property“ bzw. auf Projektebene „Import from workspace“. Formular „Create new custom property“/„Update custom property“: Titel (Pflicht, ≤255 „Property name should not exceed 255 characters.“), Beschreibung, **Property type** („Select type“, Pflicht „You must select a property type.“) mit Typen **Text, Number, Dropdown, Boolean, Date, Member picker, Formula**; **Attributes**: Text „Single line“/„Paragraph“/„Read only“ (Header „Read only data“, Fehler „Invalid text format“); Number Default „Add number“; Dropdown/Member „Single select“/„Multi select“, „No default value“; Boolean „True | False“/„No default value“; Optionen „Options“ (Platzhalter „Add option“, Fehler „Option name is required.“, „Option with same name already exists.“, „You must add at least one option.“; Auswahl-Platzhalter „Select option“, „Select options“, „{count} options selected“). **Formula:** Feld „Formula field“, Tooltip „Enter a formula using '{'Field Name'}' syntax. Supports +, -, *, /, & operators.“, Platzhalter „Write the formula“, Button „Test“/„Validating“, Erfolg „Formula is valid! Returns {resultType}“ bzw. „… ({count} field(s) referenced)“, Fehler „Formula expression is required.“, „Invalid formula: {error}“, „Circular reference detected. A formula cannot reference itself directly or indirectly.“, „Formula references non-existent property.“, „Please enter a formula“, „Missing workspace, project, or work item type context“, Picker „No matching properties“/„No available properties“. **Pflichtfeld:** „Mandatory property“ – „There seems to be a default option for this property. Making the property mandatory will remove the default value and the users will have to add a value of their choice.“ (Tooltips „This property type cannot be made mandatory“, „Uncheck to mark the field as optional“, „Check to mark the field as mandatory“). **Aktiv:** „Active“ mit Tooltip „Click to disable“/„Click to enable“. **Löschen:** „Delete this property – Deletion of properties may lead to loss of existing data. Do you want to disable the property instead?“ (Buttons „{action}, delete it“, „Yes, disable it“). Leerzustand „Add custom properties – New properties you add for this work item type will show here.“ Toasts create/update/delete/enable_disable mit `{name}`/`{action}`.
- **UI-Hinweise:** Im Work-Item-Modal werden zusätzliche Properties über den Modal-Kontext gerendert und validiert: `issuePropertyValues`, `issuePropertyValueErrors`, `getActiveAdditionalPropertiesLength`, `handlePropertyValuesValidation`, `handleCreateUpdatePropertyValues({issueId, projectId, workspaceSlug, issueTypeId, isDraft})`, `handleProjectEntitiesFetch({workItemProjectId, workItemTypeId, workspaceSlug})` (`apps/web/components/issues/issue-modal/context/issue-modal-context.tsx`; CE-Provider liefert No-ops in `provider.tsx`). Work-Item-Detail: `useWorkItemProperties(projectId, workspaceSlug, workItemId, issueServiceType)` (CE: leer, `apps/web/hooks/use-issue-properties.tsx`); Workspace: `useWorkspaceIssuePropertiesExtended` (leer, `apps/web/hooks/use-workspace-issue-properties-extended.tsx`). Activity-Typ `ISSUE_ADDITIONAL_PROPERTIES_ACTIVITY` (`packages/types/src/issues/activity/base.ts` Z. 84–88). Icons: `BooleanOutline`, `DropdownOutline/Filled`, `HashOutline` (Number), `FormulaOutline`, `TextOutline`, `MembersOutline`, `PropertiesOutline` (Propel-Kategorien `properties`, `formatting-and-editors`). Illustration `custom-properties`, `property`.
- **Datenmodell-Hinweise:** `TIssuePropertyValues = Record<string, unknown>`, `TIssuePropertyValueErrors = Record<string, unknown>` (`packages/types/src/issues/issue-property-values.ts`). Öffentliche Felder (Property: `display_name`, `property_type`, `relation_type`, `is_multi`, `is_required`, `is_active`, `default_value`, `settings`, Optionen, Werte) → P02 §4.7.
- **API-Hinweise:** Developer-Docs `api-reference/issue-types/{properties,options,values}/` → P02 §2.12.
- **Im CE vorhanden:** nur die Kontext-/Hook-Signaturen und Activity-Typ.
- **Fehlt:** komplett (Tabellen, CRUD, Werte-Speicherung, Formel-Engine inkl. Zirkelprüfung, Filter/Sortierung nach Properties).
- **Quellen:** wie genannt.
- **Konfidenz:** hoch (UI/Validierung) / mittel (Formel-Grammatik – nur Operatoren `+ - * / &` und `{Field Name}`-Referenzen belegt).

#### PF-07 – Workspace-Level Properties und Roll-ups
- **Tier:** Business/Enterprise „Workspace-level properties and roll-ups“ (`plans.tsx` Z. 222–223).
- **Funktionsbeschreibung:** Properties werden auf Workspace-Ebene definiert und mit Typen verknüpft: „Custom properties“ → „Add properties“, Modal „Add properties“ (Leer: „No properties available – All properties have already been linked to this type.“); Entknüpfen: „Unlink property – Unlinking this property will permanently delete all its values across every work item using this type. This action cannot be undone.“ mit Eingabebestätigung „Type … to continue:“ (Button „Unlink property“/„Unlinking“) (`work_item_types.settings.linked_properties.*`). Projektebene importiert Workspace-Properties („Import from workspace“). „Roll-ups“ = aggregierte Werte über Hierarchien (nur Matrix-Text, keine weiteren Spuren).
- **UI-Hinweise:** Gruppenüberschrift `common.custom_properties` „Custom properties“ (Settings-Navigation).
- **Datenmodell-Hinweise:** Workspace-Property-Katalog + Verknüpfungstabelle Property↔Type; Werte je Work Item.
- **API-Hinweise:** nicht öffentlich dokumentiert (P02 nennt nur Projekt-Typ-Properties).
- **Im CE vorhanden:** nichts.
- **Fehlt:** komplett; Roll-up-Semantik unklar (Abschnitt 10).
- **Quellen:** `packages/i18n/src/locales/en/work-item-type.json`, `packages/i18n/src/locales/en/common.json` (`common.custom_properties`).
- **Konfidenz:** mittel.

#### PF-08 – Work-Item-Type-Hierarchie
- **Tier:** unklar (nicht in `plans.tsx`; Pro-Seite nennt Epics/Initiatives).
- **Funktionsbeschreibung (`work_item_type_hierarchy.*`):** Workspace-Einstellung „Hierarchy – Set up hierarchy levels to organize your work. Each level defines a parent relationship with the item directly above it and child relationship with the item directly below it.“ Schalter „Enable hierarchy – Create parent-child relationships between different work item types.“ (Tooltip „You cannot disable hierarchy once it is enabled.“). Banner, wenn keine Typen: „Define Work Item Types first to create a new hierarchy.“ (CTA „Work item types settings“). Level-Editor per Drag & Drop: „Drag and drop type to add a new hierarchy level“, „Drag and drop a work item type to level {level}“, „Drag to change level“; Quick Action „Set as default“ je Level (Toasts „Setting as default...“, „Hierarchy level {level} set as default successfully.“); Verschieben-Toast „Moving {workItemTypeName} to level {level}...“. **Bruch-Validierung** (Modal „Validation error!“): „Work item type {workItemTypeName} has: {count} parent work item(s) …, and … sub-work item(s)“ – „This change will remove parent and child relationships from existing work items of {workItemTypeName} work item type.“ – Bestätigung durch Eingabe „Confirm“ (Button „Apply & Unlink“/„Applying“). Work-Item-Modal: Fehler „The selected work item type cannot be used to create a new work item since it breaks the hierarchy rules.“ bzw. „Work item type cannot be updated since it breaks the hierarchy rules.“; Typ-Modal: Feld „Hierarchy level“.
- **Datenmodell-Hinweise:** `IssueType.level` (Float) und `ProjectIssueType.level` (PositiveInt) existieren im CE (`apps/api/plane/db/models/issue_type.py`) – Trägerfelder der Hierarchie.
- **API-Hinweise:** nicht dokumentiert.
- **Im CE vorhanden:** `level`-Felder.
- **Fehlt:** Hierarchie-Einstellung, Validierung bei Parent-Zuordnung, Bruch-Dialog.
- **Quellen:** `packages/i18n/src/locales/en/work-item-type.json` (Abschnitt `work_item_type_hierarchy`); Propel-Icon `HierarchyOutline/Filled`.
- **Konfidenz:** mittel.

#### PF-09 – Dependencies in Gantt
- **Tier:** Pro–Enterprise (`plans.tsx` Z. 227–236).
- **Funktionsbeschreibung:** Zeitliche Abhängigkeiten zwischen Work Items („Adjust timelines for dependent work items visually on our Gantt layout.“): Relationstypen „Starts Before“, „Starts After“, „Finishes Before“, „Finishes After“ (`issue.relation.start_before|start_after|finish_before|finish_after` in `work-item.json` Z. 193–196) im Relations-Widget und als Verbindungslinien im Gantt.
- **UI-Hinweise:** CE-Relations-Widget zeigt nur `relates_to`, `duplicate`, `blocked_by`, `blocking` (`apps/web/components/relations/index.tsx` – `ISSUE_RELATION_OPTIONS`, `useTimeLineRelationOptions`); die Erweiterung erfolgt in genau diesem Objekt (Schema `{key, i18n_label, className, icon(size), placeholder}`). Icons vorhanden: `CalendarBeforeIcon`, `CalendarAfterIcon` (`packages/blocks/src/icons/calendar-before-icon.tsx`, `calendar-after-icon.tsx`), Propel `DependencyOutline/Filled`. Gantt-Drag-Hilfe `apps/web/components/gantt-chart/chart/timeline-drag-helper.tsx`.
- **Datenmodell-Hinweise:** **Backend des CE kennt die Typen bereits:** `IssueRelationChoices.START_BEFORE="start_before"`, `FINISH_BEFORE="finish_before"` mit Reverse-Paaren `start_before↔start_after`, `finish_before↔finish_after` (`apps/api/plane/db/models/issue.py` Z. 272–293). Frontend-Typ `TIssueRelationTypes = "blocking" | "blocked_by" | "duplicate" | "relates_to"` (`packages/types/src/issues/issue_relation.ts` Z. 17) muss erweitert werden.
- **API-Hinweise:** Relation-Endpunkte des CE (siehe Kern-Analyse) akzeptieren die Typen; Developer-Docs `api-reference/work-item-relations/` → P02 §2.11.
- **Im CE vorhanden:** Backend-Enum, Reverse-Mapping **und funktionierende Endpunkte** (Verifikation): die interne Relation-API listet `start_before`/`start_after`/`finish_before`/`finish_after` (`apps/api/plane/app/views/issue/relation.py` Z. 113–135, 225–237), die Public-API akzeptiert beim Anlegen `RELATION_TYPE_CHOICES` mit allen vier Timeline-Typen und liefert sie in der Relations-Antwort (`apps/api/plane/api/serializers/issue.py` Z. 545–580; `apps/api/plane/api/views/issue.py` Z. 2337–2470). Frontend-Schalter `isDependencyEnabled = false` im Timeline-Store (`apps/web/store/timeline/base-timeline.store.ts` Z. 85; Interface in `issues-timeline.store.ts` Z. 13, `modules-timeline.store.ts` Z. 13).
- **Fehlt:** Frontend-Typen, Relation-Optionen, Gantt-Pfeile, Verschiebe-Logik abhängiger Items.
- **Quellen:** wie genannt.
- **Konfidenz:** hoch (Typen) / mittel (Gantt-Verhalten beim Verschieben).

#### PF-10 – „Implements/Implemented by“ und Workspace-Relationstypen
- **Tier:** unklar.
- **Funktionsbeschreibung:** Relationspaar „Implements“/„Implemented By“ (`issue.relation.implements|implemented_by`). Workspace-Einstellung „Relations – Create and manage relation types that connect work items across your workspace.“ (`workspace_settings.settings.relations.*`) → frei definierbare Relationstypen.
- **UI-Hinweise:** Propel-Icons `ImplementsOutline/Filled`, `ImplementedByOutline/Filled`, `RelationsOutline/Filled`.
- **Datenmodell-Hinweise:** CE-Backend: `IMPLEMENTED_BY="implemented_by"`, Reverse `implements` (`issue.py` Z. 278, 290). Custom-Relation-Definitionen: P02 §4.16.
- **Im CE vorhanden:** Enum-Werte.
- **Fehlt:** UI, Workspace-Relationstyp-Verwaltung.
- **Quellen:** wie genannt.
- **Konfidenz:** mittel.

#### PF-11 – Work item Transfers
- **Tier:** Pro–Enterprise (`plans.tsx` Z. 238–247).
- **Funktionsbeschreibung:** „Move a work item from a project or a cycle to another.“ Im CE existiert nur der Transfer **offener Work Items eines abgeschlossenen Cycles** in einen anderen Cycle (`apps/web/components/cycles/transfer-issues-modal.tsx`, `transfer-issues.tsx`). EE ergänzt das **Verschieben eines Work Items in ein anderes Projekt** (Text `failed_to_move_issue_to_project` in `common.json` ohne CE-Referenz) und den Transfer einzelner Items zwischen Cycles.
- **UI-Hinweise:** Propel-Icons `TransferWorkItemOutline/Filled`, `TransferWorkItemAltOutline/Filled`.
- **Datenmodell-Hinweise:** Projektwechsel erfordert Neuvergabe `sequence_id`, Mapping von State/Labels/Cycle/Module/Estimate.
- **Fehlt:** Projekt-Move-Dialog und -Endpunkt.
- **Quellen:** wie genannt.
- **Konfidenz:** mittel.

#### PF-12 – Auto-transfer Cycle Work items (Auto-Rollover)
- **Tier:** Pro–Enterprise (`plans.tsx` Z. 249–259).
- **Funktionsbeschreibung:** „Transfer incomplete work items from a completed cycle to the next cycle or to the default project state.“ In den Auto-Schedule-Einstellungen (PF-13) als Option „Auto-rollover work items – On the day a cycle completes, move all unfinished work items into the next cycle.“ (`project_settings.cycles.auto_schedule.form.auto_rollover`).
- **Im CE vorhanden (Verifikation):** manueller Transfer offener Work Items eines Cycles in einen anderen Cycle über `POST /api/workspaces/<slug>/projects/<project_id>/cycles/<cycle_id>/transfer-issues/` (`apps/api/plane/app/urls/cycle.py` Z. 72; `TransferCycleIssueEndpoint`, `apps/api/plane/app/views/cycle/base.py` Z. 599) → CE-Status „teilweise im CE“.
- **Fehlt:** Hintergrundjob am Cycle-Ende, Einstellung.
- **Quellen:** `plans.tsx`, `packages/i18n/src/locales/en/project-settings.json`.
- **Konfidenz:** mittel.

#### PF-13 – Auto-schedule Cycles
- **Tier:** unklar.
- **Funktionsbeschreibung (`project_settings.cycles.auto_schedule.*`):** In „Cycles“-Projekteinstellung Abschnitt „Auto-schedule cycles – Keep cycles moving without manual setup.“ (Tooltip „Automatically create new cycles based on your chosen schedule.“, Button „Edit“). Formular: „Cycle Title“ (Pflicht, ≤255; Tooltip „The title will be appended with numbers for subsequent cycles. For eg: Design - 1/2/3“), „Cycle Duration“ in „Weeks“ (Pflicht, min 1 „Cycle duration must be at least 1 week“, max 30 „Cycle duration cannot exceed 30 weeks“, positiv), „Cooldown Period“ in „days“ (Pflicht, ≥0; Tooltip „Pause between cycles before the next begins.“), „Cycle starts day“ (Pflicht, nicht in der Vergangenheit), „Number of future cycles“ (Pflicht, min 1, max 3 „Cannot schedule more than 3 cycles“), „Auto-rollover work items“ (PF-12). Toasts: Toggle „Enabling/Disabling auto-schedule cycles“, Speichern „Saving auto-schedule cycles configuration“, Erfolg/Fehler create/update.
- **UI-Hinweise:** CE-Seite `apps/web/app/(all)/[workspaceSlug]/(settings)/settings/projects/[projectId]/features/cycles/page.tsx` enthält nur den Toggle „Enable cycles“; der Auto-Schedule-Block folgt darunter.
- **Datenmodell-Hinweise:** Projekt-Konfiguration (Titel, Dauer Wochen, Cooldown Tage, Startdatum, Anzahl, Rollover, aktiv) + Scheduler-Job.
- **Fehlt:** komplett.
- **Quellen:** `packages/i18n/src/locales/en/project-settings.json` Z. 442–524.
- **Konfidenz:** hoch (Formular/Validierung).

#### PF-14 – Epics
- **Tier:** Pro–Enterprise (`plans.tsx` Z. 261–270).
- **Funktionsbeschreibung:** „Organize long-term work in epics that house work items, cycles, and modules.“ Epics sind Work Items eines Typs mit `is_epic = true`; sie haben eigene Projekt-Liste (`/:ws/projects/:pid/epics`), eigene Detailansicht (Link-Schema wie Work Items: `/{ws}/browse/{IDENT}-{SEQ}/`, `packages/utils/src/work-item/base.ts` Z. 333–336), eigene Display-Filter (`epics-user-properties`), eigene Kommentare (Activity-Typ `epic-comment`, `apps/web/services/issue/issue_comment.service.ts` Z. 38), Zuordnung zu Cycles/Modulen (Power-K-Befehle `addCycleToEpic`, `removeEpicFromCycle`, `changeModulesInEpic`, `apps/web/components/power-k/ui/pages/context-based/work-item/commands.ts` Z. 309–359), Sub-Work-Items (Kinder). Leerzustände: „Turn complex projects into structured epics. – An epic helps you organize big goals into smaller, trackable tasks.“ (CTA „Create an Epic“, sekundär „Documentation“), „You haven't added work items to this epic yet. – Start by adding some work items to this epic and track them here.“ (CTA „Add work items“), Archiv „No archived epics yet – You can archive epics that are completed or cancelled. Find them here once archived.“ (`empty-state.json`). Spreadsheet-Spaltenkopf „Epics“ statt „Work items“ (`spreadsheet-header.tsx` Z. 74); Bulk-Auswahl in Epic-Listen deaktiviert (`spreadsheet-view.tsx` Z. 87, `list/default.tsx` Z. 137); Sub-Issue-Zähler in Epic-Zeilen ausgeblendet (`issue-row.tsx` Z. 129, 339). Analytics-Metrik `EPIC_WORK_ITEM_COUNT` („Epic“) (`packages/constants/src/analytics/common.ts` Z. 185–186, `packages/types/src/analytics.ts` Z. 37); Epic-Analytics-Gruppen `backlog_issues`, `unstarted_issues`, `started_issues`, `completed_issues`, `cancelled_issues`, `overdue_issues` (`packages/types/src/epics.ts`). Gantt-Blocktyp `EGanttBlockType.EPIC` (`packages/types/src/layout/gantt.ts`).
- **UI-Hinweise:** Projekt-Navigation: CE kennt `work_items, cycles, modules, views, pages, intake` (`apps/web/components/workspace/sidebar/project-navigation.tsx` Z. 80–139); die Aktiv-Logik für `item.key === "epics"` existiert bereits (`project-navigation.tsx` Z. 167–172, `apps/web/components/navigation/use-active-tab.ts` Z. 24–33) → EE-Eintrag „Epics“ (`sidebar.epics`) mit Icon `EpicOutline/Filled`. Create-Modal: `CreateUpdateEpicModal` (CE-Stub `return <></>`, Props `data, isOpen, onClose, beforeFormSubmit, onSubmit, fetchIssueDetails, primaryButtonText{default,loading}, isProjectSelectionDisabled` – `apps/web/components/epic-modal/modal.tsx`). Leerzustand-Komponente `ProjectEpicsEmptyState` (CE-Stub, `apps/web/components/issues/issue-layouts/empty-states/project-epic.tsx`). Löschen leitet nach `/projects/{pid}/epics` um (`apps/web/components/modals/work-item-level.tsx` Z. 60–62). Illustrationen `epic` (horizontal + vertical stack). Icons `ConvertToEpicOutline/Filled`, `ConvertToWorkItemOutline/Filled` (Konvertierung Work Item ↔ Epic; Modal-Kontext `handleConvert(workspaceSlug, data)`).
- **Datenmodell-Hinweise:** `IssueType.is_epic` (`apps/api/plane/db/models/issue_type.py` Z. 19); Archiv-View des CE filtert Epics aus: `Issue.objects.filter(Q(type__isnull=True) | Q(type__is_epic=False))` (`apps/api/plane/app/views/issue/archive.py` Z. 99); `RelatedIssueSerializer` liefert `type_id`, `is_epic` (`apps/api/plane/api/serializers/issue.py` Z. 655–683); Frontend-Felder `TBaseIssue.type_id`, `is_epic?`, `is_intake?` (`packages/types/src/issues/issue.ts` Z. 65, 78–79); Suche `TProjectIssuesSearchParams.epic?` (`packages/types/src/project/projects.ts` Z. 158); Home-Recents `is_epic` (`packages/types/src/home.ts` Z. 44). Projekt-Feature-Flag `epics` (Developer-Docs `api-reference/project-features/overview.md`).
- **API-Hinweise:** Frontend-Service bildet bei `EIssueServiceType.EPICS` URLs `/api/workspaces/{slug}/projects/{pid}/epics/`, `…/epics-detail/`, `…/v2/epics/`, `…/epics/{id}/` (`apps/web/services/issue/issue.service.ts` Z. 27–114); Display-Filter `GET/PATCH /api/workspaces/{slug}/projects/{pid}/epics-user-properties/` (`apps/web/services/issue_filter.service.ts` Z. 39, 50). **Keiner dieser Endpunkte existiert im CE-Backend** (`grep epic apps/api/plane/app/urls` → leer). Öffentliche API: Developer-Docs `api-reference/epics/` → P02 §2.4/§4.1.
- **Im CE vorhanden (vollständige Dateiliste der Epic-Plumbing, `grep -rln "is_epic|EIssueServiceType.EPICS|EIssuesStoreType.EPIC|isEpic"`):** `apps/web/app/(all)/[workspaceSlug]/(projects)/browse/[workItem]/page.tsx`, `apps/web/components/analytics/select/analytics-params.tsx`, `apps/web/components/analytics/total-insights.tsx`, `apps/web/components/analytics/work-items/{created-vs-resolved,customized-insights,priority-chart,workitems-insight-table}.tsx`, `apps/web/components/analytics/work-items/modal/{content,index}.tsx`, `apps/web/components/common/activity/helper.tsx`, `apps/web/components/gantt-chart/{root,chart/main-content,chart/root,sidebar/root,sidebar/issues/block,sidebar/issues/sidebar}.tsx`, `apps/web/components/home/widgets/recents/issue.tsx`, `apps/web/components/issues/{create-issue-toast-action-items,delete-issue-modal,filters}.tsx`, `apps/web/components/issues/issue-detail-widgets/relations/content.tsx`, `apps/web/components/issues/issue-detail-widgets/sub-issues/{display-filters,title-actions,title}.tsx`, `apps/web/components/issues/issue-detail-widgets/sub-issues/issues-list/root.tsx`, `apps/web/components/issues/issue-detail/parent/root.tsx`, `apps/web/components/issues/issue-layouts/calendar/{base-calendar-root,calendar,day-tile,issue-block-root,issue-block,issue-blocks,quick-add-issue-actions,week-days}.tsx`, `apps/web/components/issues/issue-layouts/empty-states/index.tsx`, `apps/web/components/issues/issue-layouts/filters/header/display-filters/{display-filters-selection,display-properties}.tsx`, `apps/web/components/issues/issue-layouts/gantt/{base-gantt-root,blocks}.tsx`, `apps/web/components/issues/issue-layouts/group-drag-overlay.tsx`, `apps/web/components/issues/issue-layouts/kanban/{base-kanban-root,block,blocks-list,default,kanban-group,swimlanes}.tsx`, `apps/web/components/issues/issue-layouts/kanban/headers/group-by-card.tsx`, `apps/web/components/issues/issue-layouts/list/{base-list-root,block-root,block,blocks-list,default,list-group}.tsx`, `apps/web/components/issues/issue-layouts/list/headers/group-by-card.tsx`, `apps/web/components/issues/issue-layouts/properties/all-properties.tsx`, `apps/web/components/issues/issue-layouts/quick-add/button/{gantt,kanban,list,spreadsheet}.tsx`, `apps/web/components/issues/issue-layouts/quick-add/form/{calendar,gantt,kanban,list,root,spreadsheet}.tsx`, `apps/web/components/issues/issue-layouts/quick-add/root.tsx`, `apps/web/components/issues/issue-layouts/spreadsheet/{base-spreadsheet-root,issue-row,spreadsheet-header-column,spreadsheet-header,spreadsheet-table,spreadsheet-view}.tsx`, `apps/web/components/issues/issue-layouts/spreadsheet/columns/{header-column,sub-issue-column}.tsx`, `apps/web/components/issues/issue-layouts/utils.tsx`, `apps/web/components/issues/issue-modal/base.tsx`, `apps/web/components/issues/peek-overview/{root,view}.tsx`, `apps/web/components/issues/relations/issue-list-item.tsx`, `apps/web/components/modals/work-item-level.tsx`, `apps/web/components/navigation/use-active-tab.ts`, `apps/web/components/power-k/ui/pages/context-based/work-item/commands.ts`, `apps/web/components/workspace/sidebar/project-navigation.tsx`, `apps/web/hooks/store/{use-issue-detail,use-issues}.ts`, `apps/web/hooks/{use-group-dragndrop,use-issue-layout-store}.ts`, `apps/web/hooks/{use-issue-peek-overview-redirection,use-issues-actions}.tsx`, `apps/web/services/issue/{issue,issue_activity,issue_comment}.service.ts`, `apps/web/store/analytics.store.ts`, `apps/web/store/issue/issue-details/{activity,issue}.store.ts`, `apps/web/store/issue/root.store.ts` (`epicDetail = new IssueDetail(this, EIssueServiceType.EPICS)` Z. 228; `projectEpics`/`projectEpicsFilter`), `packages/constants/src/issue/common.ts`, `packages/types/src/home.ts`, `packages/types/src/issues/issue.ts`, `packages/utils/src/work-item/base.ts`. Router-Parameter `epicId` (`apps/web/hooks/use-issue-layout-store.ts` Z. 16, 36).
- **Fehlt:** Backend (Epic-CRUD, Fortschritts-Analytics, Epic-Properties `EPICS_PROPERTIES_AND_OPTIONS`-Fetch-Key `packages/constants/src/fetch-keys.ts` Z. 199–200), Routen/Seiten, Create-Modal, Projekt-Navigationseintrag, Konvertierung.
- **Quellen:** wie genannt.
- **Konfidenz:** hoch.

#### PF-15 – Initiatives
- **Tier:** Pro–Enterprise (`plans.tsx` Z. 272–282, „Coming soon“); plane.so/pro (WebSearch): „epics and initiatives“ im Pro-Plan.
- **Funktionsbeschreibung:** „Create initiatives to roll up several epics.“ Workspace-weite Initiativen über Projekte und Epics; Status-Zustände (aus Icons): Draft, Planned, In progress, Completed, Cancelled (Propel `initiative-states`: `initiative-draft`, `initiative-planned`, `initiative-in-progress`, `initiative-completed`, `initiative-cancelled`); Beschreibung als Rich-Text mit Assets (`EFileAssetType.INITIATIVE_DESCRIPTION`); Labels mit eigenem Scope „initiative“ (Kommentar „EE switches on a `scope` (work item / release / initiative / project)“ in `apps/web/components/dropdowns/label/label-select.tsx` Z. 48–49); eigene ein-/ausklappbare Seitenleiste (`initiativesSidebarCollapsed`, `toggleInitiativesSidebar`, LocalStorage-Key `initiatives_sidebar_collapsed` – `apps/web/store/theme.store.ts` Z. 20, 32, 47, 62, 74, 181–187); Updates (PF-23) und Checkpoints (PF-16) referenzieren Initiativen.
- **UI-Hinweise:** Icons `InitiativeOutline/Filled` (workspace-features), Illustration `initiative` (vertical stack, `packages/blocks/src/empty-state/assets/vertical-stack/initiative.tsx`). Reservierte Slugs `initiatives`, `initiative` (`packages/constants/src/workspace.ts` Z. 54–55; `apps/api/plane/utils/constants.py` Z. 47–48).
- **Datenmodell-Hinweise:** Workspace-Feature-Flag `initiatives` (Developer-Docs `api-reference/workspace-features/overview.md`); Felder/Endpunkte → P02 §2.8/§4.2 (Initiative, Initiative-Labels, Zuordnung Projekte und Epics).
- **Im CE vorhanden:** Theme-Store-Flag, Asset-Typ, Illustration, Slugs.
- **Fehlt:** komplett (Modelle, Seiten, Navigation).
- **Quellen:** wie genannt.
- **Konfidenz:** hoch (Existenz) / mittel (Detailverhalten).

#### PF-16 – Checkpoints
- **Tier:** Pro–Enterprise („Coming soon“, `plans.tsx` Z. 284–295).
- **Funktionsbeschreibung:** „Add markers to Projects, Epics and Initiatives to keep your team on track and report on progress.“ Keine weiteren Repo-Spuren. Abgrenzung zu Milestones (PF-17) unklar (Abschnitt 10).
- **Konfidenz:** niedrig.

#### PF-17 – Milestones
- **Tier:** unklar (nicht in `plans.tsx`).
- **Funktionsbeschreibung:** Projekt-Feature „Milestones – Milestones provide a layer to align work items toward shared completion dates.“ mit Schalter „Enable milestones – Organize work items by milestone deadlines.“ (`project_settings.features.milestones.*`; `common.json` `milestones`, `milestones_description`, `common.milestones`). Status (Icons): „not started“, „in progress“, „done“ (Propel `milestone-states`: `milestone-not-started`, `milestone-in-progress`, `milestone-done`). In der Projekt-Übersicht als einklappbarer Abschnitt (Projekt-Store: `type ProjectOverviewCollapsible = "links" | "attachments" | "milestones"`, Default offen `["milestones"]` – `apps/web/store/project/project.store.ts` Z. 21, 86).
- **UI-Hinweise:** Icons `MilestoneOutline`, `MilestonesFilled` (project-features); Illustration `milestone` (vertical stack).
- **Datenmodell-Hinweise:** Fetch-Key `PROJECT_MILESTONES(projectId, projectRole)` (`packages/constants/src/fetch-keys.ts` Z. 205–206). Felder/Endpunkte (Name, Zieldatum, Work-Item-Zuordnung) → P02 §2.13/§4.5.
- **Fehlt:** komplett.
- **Konfidenz:** mittel.

#### PF-18 – Module Overview
- **Tier:** Pro–Enterprise (`plans.tsx` Z. 297–306).
- **Funktionsbeschreibung:** „Like Cycle Overviews, see relevant details and progress charts for each module.“ Das CE besitzt bereits eine Modul-Analytics-Sidebar (`apps/web/components/modules/analytics-sidebar/{issue-progress,progress-stats}.tsx`); die Bezahlfunktion ist eine ausführliche Übersicht analog zur Cycle-Übersicht (Fortschrittsdiagramme, Details). Exakter Mehrumfang nicht belegt.
- **Konfidenz:** niedrig.

#### PF-19 – Auto-assignment in Modules
- **Tier:** Pro „Linear“; Business/Enterprise „Round-robin and Capacity“ (`plans.tsx` Z. 308–317).
- **Funktionsbeschreibung:** „Choose assignment rules for work items in a module including Linear, Round Robin, or Capacity.“ Keine weiteren Spuren. Modul-Mitglieder existieren im CE (`ModuleMember`, `apps/api/plane/db/models/module.py` Z. 131–132).
- **Konfidenz:** niedrig.

#### PF-20 – Public, Private und Secret Projects
- **Tier:** Pro–Enterprise (`plans.tsx` Z. 331–341).
- **Funktionsbeschreibung:** Drei Sichtbarkeitsstufen: **Public** „visible and accessible to everyone“, **Private** „visible but need approval to join“, **Secret** „aren't visible or accessible“. Das CE hat zwei Stufen: Backend `Project.NETWORK_CHOICES = ((0, "Secret"), (2, "Public"))` (`apps/api/plane/db/models/project.py` Z. 71, 76, Default `2`); Frontend `NETWORK_CHOICES` mit i18n `workspace_projects.network.private.*` („Accessible only by invite“) für `0` und `workspace_projects.network.public.*` („Anyone in the workspace except Guests can join“) für `2` (`packages/constants/src/project.ts` Z. 21–35). Der fehlende Wert `1` ist der Kandidat für „Private (Beitritt mit Genehmigung)“.
- **UI-Hinweise:** Icon-Komponente `apps/web/components/project/project-network-icon.tsx`; Join-Flow „Seems like you don't have access to this Project … Contact admin to request for access“ (`project_empty_state.no_access.*`) ist CE.
- **Fehlt:** Netzwerkstufe „Private“ mit Beitrittsanfrage/-genehmigung.
- **Konfidenz:** mittel (Wert `1` nicht belegt).

#### PF-21 – State of Projects (Projekt-States, Project Grouping, Projekt-Labels)
- **Tier:** Pro–Enterprise (`plans.tsx` Z. 343–353).
- **Funktionsbeschreibung:** Workspace-Einstellung „Projects – Manage project states, and enable project labels, and other configuration.“ mit Tabs „Project states“ und „Project labels“ (`workspace_settings.settings.projects.*`); „Project states – See progress overview for all projects. – Project States is a Plane-only feature for tracking progress of all your projects by any project property.“ (CTA „Go to settings“, `workspace_settings.settings.project_states.*`). Projektliste/-übersicht mit State-Sidebar; Leerzustand „Enable project states – Enable Project States to view and manage properties like state, priority, due dates and more.“ (`workspace_empty_state.project_overview_state_sidebar`). Analytics-Kachel „Projects by status“ (`workspace_analytics.projects_by_status`).
- **Datenmodell-Hinweise:** Workspace-Feature-Flag `project_grouping` (Developer-Docs `api-reference/workspace-features/overview.md`); Projekt-States/-Labels → P02 §4.12.
- **Im CE vorhanden:** nichts (CE-Komponenten `apps/web/components/project-states/*` betreffen Work-Item-States eines Projekts, nicht Projekt-States).
- **Konfidenz:** mittel.

#### PF-22 – Project Overview
- **Tier:** Pro (Zeile auskommentiert, „Coming soon“; `plans.tsx` Z. 318–329).
- **Funktionsbeschreibung:** „See just-in-time snapshots of your project with essential metrics.“ Projekt-Übersichtsseite mit einklappbaren Abschnitten „links“, „attachments“, „milestones“ (`apps/web/store/project/project.store.ts` Z. 21, 86) und Power-K-Navigation `power_k.navigation_actions.nav_project_overview`. Icon `OverviewOutline/Filled` (project-features).
- **Fehlt:** Seite, Projekt-Links/-Attachments (Projekt-Link-Typ `packages/types/src/project/project_link.ts` existiert).
- **Konfidenz:** mittel.

#### PF-23 – Project Updates (und Updates an Epics/Initiativen)
- **Tier:** Pro (Zeile auskommentiert, „Coming soon“; `plans.tsx` Z. 354–366).
- **Funktionsbeschreibung (`update.json`, `project_settings.project_updates.*`):** „Project Updates – Consolidated tracking and progress monitoring for this project“. Update-Feed mit „Add Update“ (Platzhalter „Add your update here“), Status je Update `EUpdateStatus`: `OFF-TRACK`, `ON-TRACK`, `AT-RISK` (`packages/types/src/enums.ts`; Labels `common.on_track` „On-Track“, `common.off_track` „Off-Track“, `common.at_risk` „At risk“), Abschnitt „Progress – Since last update“, Kommentar-Zähler „{count} Comment(s)“, Reaktionen (Toasts „Reaction created/removed“), Löschen „Delete update – Are you sure you want to delete this update? This is an irreversible action.“, Leerzustand „No updates yet – You can see the updates here.“ bzw. „No updates yet. – Once project members add updates it will appear here“ (`common_empty_state.updates`).
- **UI-Hinweise:** Icon `UpdatesOutline/Filled`; Illustration `update`.
- **Im CE vorhanden (Verifikation):** Enum `EUpdateStatus`; die Projekt-Activity rendert für das Feld `is_project_updates_enabled` den Text „enabled/disabled project updates“ mit Icon `SubscribeOutline` (`apps/web/components/common/activity/helper.tsx` Z. 67, 266–269) – das Feld existiert im CE-Modell `Project` nicht (`apps/api/plane/db/models/project.py` Z. 95–102 kennt nur `is_time_tracking_enabled`, `is_issue_type_enabled`) → CE-Status „Stub/UI-Hülle im CE“. Analog für `is_epic_enabled` („epics“, `GridOutline`, Z. 68, 270–273) und `is_workflow_enabled` („custom workflow“, `GitBranchOutline`, Z. 69, 274–277).
- **Fehlt:** Modell, API, UI (Update-Feed).
- **Tier-Hinweis:** Die Pro-Zuordnung stammt nur aus der **auskommentierten** Matrix-Zeile; Dok. 21 führt „Work-Item-/Projekt-Updates“ als „unklar“.
- **Konfidenz:** mittel–hoch (Texte) / niedrig (Tier).

#### PF-24 – Pre-defined work item Templates
- **Tier:** Pro („Coming soon“, `plans.tsx` Z. 368–379).
- **Funktionsbeschreibung:** „Choose from our available work item templates that customize work item types and properties for several use cases.“ Vorkonfigurierte Templates (mitgeliefert). Keine weiteren Spuren.
- **Konfidenz:** niedrig.

#### PF-25 – Work-Item-Templates
- **Tier:** Pro (Highlight „Work item templates“, `plans.tsx` Z. 1306).
- **Funktionsbeschreibung (`template.json`):** Template-Typ „Work item templates“: Formular „Name your work-item template.“ (Pflicht, <255), „Describe when and how to use this template.“, Work-Item-Felder „Give this work item a title.“ (Pflicht, <255), „Describe this work item so its clear what you will accomplish when you complete this.“; Buttons „Create work-item template“/„Update work-item template“. Anwendung im Create-Modal: Dropdown „Pick a work item template“ (Tooltip), „Add new template“, „No templates found.“; Button „Use template“/„Applying“. Leerzustände Sub-Entitäten im Template-Editor: „No labels yet…“, „No modules yet…“, „No work items yet…“, „No sub-work items yet…“. Herkunft „Derived from workspace“/„Derived from project“.
- **UI-Hinweise:** Modal-Kontext `workItemTemplateId`, `setWorkItemTemplateId`, `isApplyingTemplate`, `setIsApplyingTemplate`, `handleTemplateChange({workspaceSlug, reset, editorRef})` (`apps/web/components/issues/issue-modal/context/issue-modal-context.tsx`); Prop `templateId` an `CreateUpdateIssueModal` (`apps/web/components/issues/issue-modal/modal.tsx` Z. 33, 51) und `IssueModalProvider` (`provider.tsx` Z. 17). Icon `TemplatesOutline/Filled`; Illustration `template`.
- **Fehlt:** Template-Modell, Settings-Seite, Anwendung.
- **Konfidenz:** hoch.

#### PF-26 – Project Templates
- **Tier:** Business/Enterprise (`plans.tsx` Z. 392–401; `BUSINESS_PLAN_FEATURES`).
- **Funktionsbeschreibung:** „Save states, workflows, automation, and other project settings into templates.“ Formular „Name your project template.“, „Describe when and how to use this template.“, Projektfelder „Name your project.“/„Describe the purpose and goals of this project.“; Buttons „Create project template“/„Update project template“; Auswahl im Projekt-Erstellen „Pick a project template“. Rechte: „Contact your project admin to create templates“ / „Contact your workspace admin to create templates“. WebSearch (plane.so/business): Projekt-Setups inkl. Statuses, Issue Types, Labels, Default-Assignees.
- **UI-Hinweise:** `templateId` an `CreateProjectModal` (`apps/web/components/project/create-project-modal.tsx` Z. 27, 36, 82) und `CreateProjectForm` (`apps/web/components/projects/create/root.tsx` Z. 33 – im CE ungenutzt).
- **Fehlt:** komplett.
- **Konfidenz:** hoch.

#### PF-27 – Page-Templates
- **Tier:** Pro (`plans.tsx` Z. 887–896 „Templates – Use pages as templates for your project, team, or workspace.“).
- **Funktionsbeschreibung:** Template-Typ „Page templates“: „Name your page template.“, Seitenname „Untitled page“ (<255); Buttons „Create page template“/„Update page template“; Auswahl beim Seitenerstellen „Choose from template“; Leer: „There are no templates you have access to. – Please create a template“, Suche „That didn't match a template. – Try searching by other terms.“
- **Konfidenz:** hoch.

#### PF-28 – Template-Marketplace
- **Tier:** unklar.
- **Funktionsbeschreibung (`templates.settings.form.publish.*`):** Aktion „Publish to Marketplace“ bzw. „Publish settings“ (wenn veröffentlicht), „Unpublish from Marketplace“. Titel „Make your template discoverable and recognizable.“ Felder: Name (Pflicht), „Short description“ (Pflicht), „Description“ (Pflicht), „Category“ (Mehrfachauswahl, ≥1), „Keywords“ (kommagetrennt, ≥1), „Website URL“ (URL, <800), „Company name“ (Pflicht, <255), „Contact email“ (E-Mail, <255), „Link to your privacy policy“, „Link to your terms of use“ (URL, <800), „Cover image“ (Pflicht; Upload/Drag&Drop, „Upload and save“, „Remove“), „Attach screenshots“ (≥1). Unpublish-Bestätigung „Are you sure you want to unpublish template-… ? This template will no longer be available to users on the marketplace.“
- **Migrationshinweis:** Ein öffentlicher Plane-Marketplace ist im Airgapped-Betrieb (ADR-004) nicht erreichbar → als instanzlokaler Template-Katalog umsetzen (Abschnitt 10).
- **Konfidenz:** mittel.

#### PF-29 – Recurring work items
- **Tier:** Business („Upgrade to Business to make recurring work feel effortless.“ – `recurring_work_items.empty_state.upgrade.description`).
- **Funktionsbeschreibung (`work-item.json` `recurring_work_items.*`, `empty-state.json`):** Projekt-Einstellung „Recurring work items – Set your repeatable work once, and we'll take care of the repeats. You'll see everything right here when it's time.“; „New recurring work item“/„Update recurring work item“; Formular-Abschnitt „Schedule“ mit Pflicht-Startdatum („Start date is required“) und Intervalltyp („Interval type is required“); Buttons „Create recurring work item“/„Update recurring work item“; ohne Rechte „Contact your project admin to create recurring work items“; Upsell-Leerzustand „Your work, on autopilot – Set it once. We'll bring it back when it's due.“; Leerzustand „No recurring work item yet – Set up recurring work items to automate repeat tasks and stay on schedule effortlessly.“ (CTA „Create recurring work item“); Löschen „Are you sure you want to delete recurring work item-… ?“; Toasts create/update/delete.
- **UI-Hinweise:** Icon `RecurringWorkItemsOutline/Filled`; Gruppenlabel `common.recurring_work_items`.
- **Datenmodell-Hinweise:** Definition (Work-Item-Vorlage + Startdatum + Intervalltyp) + Scheduler; Intervallwerte nicht belegt (Abschnitt 10).
- **Konfidenz:** mittel.

#### PF-30 – Teamspaces
- **Tier:** Pro (`PRO_PLAN_FEATURES` „Teamspaces“; plane.so/pro lt. WebSearch: „teamspaces“).
- **Funktionsbeschreibung:** Teamspaces bündeln Mitglieder und Projekte (Developer-Docs `api-reference/teamspace/`: Members, Projects). Im CE vorbereitete Sichten: Teamspace-Work-Items (`EIssuesStoreType.TEAM`), Teamspace-Views (`TEAM_VIEW`), Projekt-Work-Items innerhalb eines Teamspace (`TEAM_PROJECT_WORK_ITEMS`) (`packages/types/src/issues/issue.ts` Z. 32–42; Stores `teamIssues`, `teamViewIssues`, `teamProjectWorkItems` in `apps/web/store/issue/root.store.ts` Z. 80–96, 148–167, 242–258; Hook-Mapping `apps/web/hooks/store/use-issues.ts` Z. 40–149); Router-Parameter `teamspaceId` (`apps/web/store/router.store.ts` Z. 18, 45, 80–84; `apps/web/hooks/use-issue-layout-store.ts` Z. 26–40). Gruppierung `team_project` → `project_id` (`packages/types/src/view-props.ts` Z. 25; `packages/constants/src/issue/common.ts` Z. 39; `apps/web/store/issue/helpers/base-issues.store.ts` Z. 126, 140; `apps/web/components/issues/issue-layouts/utils.tsx` Z. 155 `getTeamProjectColumns`). Teamspace-Beschreibung/-Kommentare mit Assets (`EFileAssetType.TEAM_SPACE_DESCRIPTION`, `TEAM_SPACE_COMMENT_DESCRIPTION`). Teamspace-Pages: Realtime-Events tragen `teamspace_id` (`packages/editor/src/types/document-collaborative-events.ts`); Seiten-Move-Texte „Private and shared pages cannot be moved to a teamspace.“, „Search for projects and teamspaces“ (`page_actions.move_page.*`). Member-Dropdown in EE mit `teamspaceId`-Scope (`apps/web/components/dropdowns/member/member-select.tsx` Z. 61–62). Settings-Gruppe „Members & Teamspaces“ (`common.members_and_teamspaces`).
- **UI-Hinweise:** Icons `TeamspacesOutline/Filled`; Illustration `teamspace` (vertical stack).
- **Datenmodell-Hinweise:** Workspace-Feature-Flag `teams`; CE-Modell `Team` (`apps/api/plane/db/models/workspace.py` Z. 261–271: `name`, `description`, `workspace`, `logo_props`) ist ein Legacy-Vorläufer ohne Projekte/Pages. Details → P02 §2.17/§4.4.
- **Fehlt:** Modelle (Teamspace, Mitglieder, Projekte, Pages, Views, Kommentare/Updates), Seiten, Navigation.
- **Konfidenz:** hoch (Existenz/Plumbing) / mittel (UI-Details).

#### PF-31 – Teamspace Cycles
- **Tier:** Business/Enterprise (`plans.tsx` Z. 381–390).
- **Funktionsbeschreibung:** „See multiple cycles in multiple projects at once.“ (Cycles aller Teamspace-Projekte). Keine weiteren Spuren.
- **Konfidenz:** niedrig.

#### PF-32 – Baselines And Deviations / PF-33 – Scheduled Comms / PF-35 – Custom SLAs
- **Tier:** jeweils Business/Enterprise (`plans.tsx` Z. 403, 414, 436).
- **Funktionsbeschreibung (nur Matrix-Text):** Baselines „Declare baselines for how your projects progress and zoom in on deviations.“; Scheduled Comms „Schedule reports, notifications, and messages to third-party tools.“; Custom SLAs „Set SLA matrices for time-sensitive work items.“ Keine weiteren Repo-Spuren (Icon `TimeInStateOutline/Filled` könnte SLA/Time-in-State dienen – nicht belegt).
- **Konfidenz:** niedrig.

#### PF-34 – Intake Assignees / Intake-Verantwortung
- **Tier:** Business/Enterprise (`plans.tsx` Z. 425–434).
- **Funktionsbeschreibung (`project_settings.features.intake.*`):** In der Intake-Feature-Seite: Abschnitt „Intake responsibility“ mit Zuweisung von Standard-Bearbeitern; „Notify assignees – For a new request to intake, default assignees will be alerted via notifications“; Toast „Setting assignees...“/„Assignees set successfully.“; Tooltips für Nicht-Admins „Ask your Project Admin to turn this on.“/„…off.“.
- **Datenmodell-Hinweise:** CE-Feld `Project.default_assignee` (FK User, `apps/api/plane/db/models/project.py` Z. 79) existiert; Mehrfach-Assignees + Notify-Flag fehlen.
- **Konfidenz:** mittel.

#### PF-36 – Intake Forms
- **Tier:** Business/Enterprise (`plans.tsx` Z. 447–456; `BUSINESS_PLAN_FEATURES` „Intake Forms“).
- **Funktionsbeschreibung (`project_settings.features.intake.form.*`):** Intake-Quelle „Forms – Let folks outside your workspace create potential new work items for you via a dedicated and secure form.“ mit Feld „Default form URL“; „Create Forms using work item types“; „Manage forms“ (Tooltip Nicht-Admin „Ask your Workspace Admin to manage this.“); „Create form“/„Edit form details“; Felder „Form title“ (Pflicht „Form title is required“), „Work item type“, Property-Auswahl („Select properties“, Suche „Search for properties“, „Remove property“); Toasts „Intake form created/updated successfully“, „Failed to create/update intake form“. In der Intake-Detailansicht erscheint als Ersteller „Intake Form user“, wenn `source === FORMS` (`apps/web/components/inbox/content/issue-root.tsx` Z. 179–182).
- **Datenmodell-Hinweise:** `EInboxIssueSource = IN_APP | FORMS | EMAIL` (`packages/types/src/inbox.ts` Z. 27–31); `IntakeIssue.source` (Default `"IN_APP"`), `source_email`, `extra` (JSON) (`apps/api/plane/db/models/intake.py` Z. 76–80); öffentliches Formular über `DeployBoard` mit `entity_name="intake"` (`apps/api/plane/db/models/deploy_board.py` Z. 27; im CE wird nur `entity_name="project"` verwendet, z. B. `apps/api/plane/app/views/project/base.py` Z. 84, 250, 546, 579, `apps/api/plane/space/views/intake.py` Z. 58, 109). Formular-Definition (Titel, Typ, Property-Liste) fehlt.
- **Fehlt:** Form-Builder, öffentliche Formularseite im Space-App (`apps/space/app/routes.ts` hat nur `issues/:anchor`), Anti-Spam/Auth.
- **Konfidenz:** hoch (Konfiguration) / mittel (öffentliche Seite).

#### PF-37 – Emails For Intake
- **Tier:** Business/Enterprise („Coming soon“, `plans.tsx` Z. 458–467); Doku „Configure DNS for Intake Email [Business]“ (`self-hosting/govern/configure-dns-email-service.md`).
- **Funktionsbeschreibung:** Intake-Quelle „Email – Collect new work items from anyone who sends an email to a Plane email address.“ mit Feld „Email ID“ (`project_settings.features.intake.email.*`). Eingangs-E-Mail erzeugt Intake-Item mit `source = "EMAIL"` und `source_email`.
- **Migrationshinweis:** Benötigt eingehenden Mail-Empfang (SMTP-Inbound oder IMAP-Polling) – self-hosted/airgapped-fähig umsetzen.
- **Konfidenz:** mittel–hoch.

#### PF-38 – Work Item in anderes Projekt duplizieren
- **Tier:** unklar.
- **Funktionsbeschreibung (`issue.duplicate.modal.*`, `issue.toast.duplicate.*`):** Modal „Make a copy to another project – This creates a copy of the work item. All property data will be removed while duplicating.“ mit Projektauswahl („Select a project“); Toasts „Work item duplicated successfully“/„Failed to duplicate work item“.
- **Im CE vorhanden (Verifikation):** Extension-Point `createCopyMenuWithDuplication(props)` gibt nur `props.baseItem` zurück; Props `activeLayout`, `setCreateUpdateIssueModal`, `setDuplicateWorkItemModal?`, `workspaceSlug?` (`apps/web/components/issues/issue-layouts/quick-action-dropdowns/copy-menu-helper.tsx`) → EE hängt hier das Untermenü „Make a copy to another project“ an. CE-Status „Stub/UI-Hülle im CE“ (S65).
- **Tier-Hinweis:** Changelog v1.13.0 „Duplicate work items and epics across projects“ (über Dok. 23 WM-25) nennt keinen Plan.
- **Konfidenz:** mittel.

#### PF-39 – Kommentar-Antworten (Replies)
- **Tier:** unklar.
- **Funktionsbeschreibung (`issue.comments.replies.*`):** Antwort-Thread unter Kommentaren: „Add reply“ (Button und Platzhalter), Toasts „Failed to fetch replies“, „Reply created/updated/deleted successfully“, Fehlervarianten. Aktion `common.actions.reply` „Reply“.
- **Datenmodell-Hinweise:** CE-Modell `IssueComment.parent` (FK self, `related_name="parent_issue_comment"`, `apps/api/plane/db/models/issue.py` Z. 475–476) existiert, ist aber laut Kommentar nicht client-schreibbar („Only the content and visibility are client-writable; actor, parent and the …“, `apps/api/plane/app/views/issue/comment.py` Z. 28).
- **Konfidenz:** mittel.

#### PF-40 – Up-/Downvotes in der App
- **Tier:** unklar.
- **Funktionsbeschreibung (`issue.vote.*`):** Tooltips „Click to upvote“, „Click to downvote“, „Click to view upvotes“, „Click to view downvotes“. Im CE existieren Votes nur im öffentlichen Board (`DeployBoard.is_votes_enabled`, `apps/api/plane/db/models/deploy_board.py` Z. 36; Modell `IssueVote`, `issue.py` Z. 654).
- **Konfidenz:** mittel.

#### PF-41 – Customers
- **Tier (korrigiert):** **Business**. Belege: Plane University 202 „enable in Workspace Settings (Business tier)“ (https://university.plane.so/courses/202-the-power-relay/02-intro-to-customers.html, WebSearch im Verifikationslauf), Launch-Post https://plane.so/blog/introducing-plane-business („customer database … link work items to customers“), Schwester-Dokumente Dok. 21 F04 und Dok. 23 WM-16. Die frühere Angabe „Pro – customer profiles“ (WebSearch-Zusammenfassung plane.so/pricing) ließ sich im Verifikationslauf nicht bestätigen (UNVERIFIZIERT); die Doku-Seite https://docs.plane.so/customers nennt keinen Plan. `PRO_PLAN_FEATURES` (`packages/constants/src/subscription.ts`) erwähnt Customers nicht.
- **Funktionsbeschreibung:** Kunden-Datenbank im Workspace mit Kunden-Requests und Kunden-Properties; Work Items werden Kunden zugeordnet; Display-Properties `customer_count` und `customer_request_count` an Work Items (Seeds `apps/api/plane/bgtasks/workspace_seed_task.py` Z. 160, 163; `apps/api/plane/seeds/data/views.json` Z. 10). Workspace-Feature-Flag `customers`.
- **UI-Hinweise:** Icons `CustomersOutline/Filled`; Illustrationen `customer` (horizontal + vertical stack). Kommentar zu Create-Modals: „intake and customer create modals order every control through `ETabIndices`“ (`packages/blocks/src/select/types.ts` Z. 384). Hinweis: Im CE-i18n existiert **kein** Customers-Namespace → Texte aus öffentlicher Quelle/Screenshots nötig (Abschnitt 10).
- **Datenmodell-/API-Hinweise:** Developer-Docs `api-reference/customer/` (22 Dateien: Customer, Requests, Properties, Property-Values, Work-Item-Links) → P02 §2.2/§4.3.
- **Konfidenz:** hoch (Existenz/API) / niedrig (UI-Texte).

#### PF-42 – Releases
- **Tier:** unklar.
- **Funktionsbeschreibung:** Labels haben in EE einen Scope „release“ (`apps/web/components/dropdowns/label/label-select.tsx` Z. 48–49); Icons `ReleasesOutline/Filled` (workspace-features), `ReleaseTagOutline/Filled`. P02 §4.18: nur in der MCP-Doku erwähnt.
- **Konfidenz:** niedrig.

### 4.2 Visualisierung, Analytics, Navigation/Suche

#### PF-43 – Shared Views
- **Tier:** Pro–Enterprise (`plans.tsx` Z. 499–508).
- **Funktionsbeschreibung:** „Choose a few members to share a view with.“ Leerzustand „project_views.empty_state.shared.*“ (ohne CE-Referenz). CE-Views kennen nur `access` 0 = Private, 1 = Public (`IssueView.access`, `apps/api/plane/db/models/view.py` Z. 66). EE ergänzt eine Freigabeliste von Mitgliedern.
- **Fehlt:** Freigabe-Modell (View ↔ User), UI zum Teilen, Sichtbarkeitsregeln.
- **Konfidenz:** mittel.

#### PF-44 – Publish Views
- **Tier:** Pro–Enterprise (`plans.tsx` Z. 510–519; `ONE_PLAN_FEATURES` „Real-time collab + public views and page“; `FREE_PLAN_UPGRADE_FEATURES` „Public Views and Pages“).
- **Funktionsbeschreibung:** „Put a view on the Internet and let your customers interact with them.“ Leerzustand `project_views.empty_state.public.*` (ohne CE-Referenz).
- **Datenmodell-Hinweise:** `DeployBoard.TYPE_CHOICES` enthält bereits `("view", "View")` neben `project`, `issue`, `module`, `cycle` (Label „Task“), `page`, `intake` (`apps/api/plane/db/models/deploy_board.py` Z. 20–28); Felder `anchor` (uuid4-hex, unique), `is_comments_enabled`, `is_reactions_enabled`, `intake`, `is_votes_enabled`, `view_props`, `is_activity_enabled`, `is_disabled`. CE nutzt ausschließlich `entity_name="project"` (Abschnitt 9).
- **Fehlt:** Publish-Dialog für Views, Space-Route für Views.
- **Konfidenz:** hoch (Modell) / mittel (UI).

#### PF-45 – Dashboards and Widgets
- **Tier:** Pro–Enterprise (`plans.tsx` Z. 521–530; `PRO_PLAN_FEATURES` „Dashboards + Reports“).
- **Funktionsbeschreibung:** Eigene Workspace-Dashboards mit Widgets („Create your own dashboards with custom widgets and data types.“). Leerzustand „Visualize your progress with dashboards – Build customizable dashboards to track metrics, measure outcomes, and present insights effectively.“ (CTA „Create new dashboard“, `workspace_empty_state.dashboard`). Widget-Farbpaletten `modern`, `horizon`, `earthen` mit je 10 Light-/Dark-Farben und i18n-Keys `dashboards.widget.color_palettes.{modern,horizon,earthen}` (Keys fehlen im CE-Locale!) (`packages/constants/src/chart.ts` Z. 41–135). Chart-Modelle `EChartModels`: `BASIC`, `STACKED`, `GROUPED`, `MULTI_LINE`, `COMPARISON`, `PROGRESS` (`packages/constants/src/chart.ts` Z. 32–39); Achsen `ChartXAxisProperty`/`ChartYAxisMetric` (`packages/types/src/analytics.ts`, `packages/constants/src/analytics/common.ts`); Chart-Labels `chart.x_axis` „X-axis“, `chart.y_axis` „Y-axis“, `chart.metric` „Metric“ (`common.json`).
- **UI-Hinweise:** Nicht verwendeter User-Menü-Eintrag `{key: "dashboards", labelTranslationKey: "workspace_dashboards" („Dashboards“), href: "/{ws}/dashboards/", access: [ADMIN, MEMBER], Icon: DashboardsOutline}` (`apps/web/components/workspace/sidebar/user-menu.tsx` Z. 34–40; `SidebarUserMenu` wird im CE nirgends gerendert). Icons `DashboardsOutline/Filled`, `WidgetOutline/Filled`; Chart-Icons `AreaOutline`, `BarOutline`, `DonutOutline`, `LineOutline`, `PieOutline`. Illustration `dashboard`. Reservierter Slug `dashboard`.
- **Abgrenzung:** `apps/web/services/dashboard.service.ts` und `packages/services/src/dashboard/dashboard.service.ts` (`/api/workspaces/{slug}/dashboard/`, `/api/dashboard/{id}/widgets/{widgetId}/`) gehören zum **veralteten** Home-Dashboard (`TDeprecatedDashboard`, Widget-Keys `TWidgetKeys` = `overview_stats`, `assigned_issues`, `created_issues`, `issues_by_state_groups`, `issues_by_priority`, `recent_activity`, `recent_projects`, `recent_collaborators` in `packages/types/src/dashboard.ts` Z. 13–21) und sind **nicht** die Bezahl-Dashboards; im CE-Backend existiert nur `users/me/workspaces/<slug>/dashboard/` (`apps/api/plane/app/urls/user.py` Z. 80).
- **Fehlt:** Dashboard-/Widget-Modelle, Abfrage-Engine, Editor, Seiten.
- **Konfidenz:** hoch (Existenz) / mittel (Widget-Typen über `EChartModels` abgeleitet).

#### PF-46 – Progress Charts
- **Tier:** Pro–Enterprise (`plans.tsx` Z. 538–547).
- **Funktionsbeschreibung:** „Track progress in cycles, modules, and overviews throughout Plane without switching to dashboards or Analytics.“ Das CE hat Burndown/Progress in Cycle- und Modul-Sidebar (`apps/web/components/cycles/analytics-sidebar/sidebar-chart.tsx`, `progress-stats.tsx`, `apps/web/components/modules/analytics-sidebar/*`) und im Active Cycle (`apps/web/components/cycles/active-cycle/productivity.tsx`). Nicht referenzierte Chart-Legenden `project_cycles.active_cycle.{chart,ideal,current,trailing,leading}` (`project.json`) deuten auf erweiterte Fortschrittsdiagramme (Ideal-, Ist-, Trailing-/Leading-Linien) hin. Leerzustand „There're no progress metrics to show yet. – Start setting property values in work items to see progress metrics here.“ (`common_empty_state.progress`).
- **Konfidenz:** mittel.

#### PF-47 – Cycle Reports
- **Tier:** Pro–Enterprise (`plans.tsx` Z. 550–559).
- **Funktionsbeschreibung:** „Get on-demand cycle reports during and after a cycle. Revisit reports anytime from permalinks.“ CE speichert bereits einen Snapshot abgeschlossener Cycles: `Cycle.progress_snapshot` (JSON, `apps/api/plane/db/models/cycle.py` Z. 74; Frontend `validateCycleSnapshot` in `sidebar-chart.tsx`).
- **Fehlt:** Report-Seite mit Permalink, On-demand-Erzeugung während des Cycles.
- **Konfidenz:** niedrig–mittel.

#### PF-48 – Insights / PF-49 – Advanced Pages Analytics / PF-51 – Time Capsule
- **Tier:** Insights Pro (Coming soon, `plans.tsx` Z. 561); Advanced Pages Analytics Business (Coming soon, Z. 585); Time Capsule Business (auskommentiert, Z. 573).
- **Funktionsbeschreibung (nur Matrix):** Insights „Hindsight, On-demand insights, Foresights.“; Pages Analytics „See who's viewing, sharing, and commenting on your pages along with other useful info.“; Time Capsule „Go back in your project's timeline and see point-in-time snapshots.“
- **Konfidenz:** niedrig.

#### PF-50 – Custom Reports / erweiterte Analytics-Tabs
- **Tier:** Business/Enterprise (Coming soon, `plans.tsx` Z. 597–606; Highlight Business „Custom Reports“).
- **Funktionsbeschreibung:** CE-Analytics hat die Tabs `overview` und `work-items` (`TAnalyticsTabsBase`, `packages/types/src/analytics.ts` Z. 40). Nicht referenzierte Texte zeigen zusätzliche Tabs/Kacheln: Tab „Scope and Demand“, Tab „Custom Analytics“ (`workspace_analytics.tabs.*`), Sperrhinweis „Upgrade to {plan} to unlock {tab}“ (`workspace_analytics.upgrade_to_plan`), Kacheln „Work items resolved vs pending“, „Projects by status“, „Active users“, „Intake Trends“, Leerzustände `workspace_analytics.empty_state.{project_insights,created_vs_resolved,customized_insights,general,cycle_progress,module_progress,intake_trends}` sowie `workspace_empty_state.analytics_{projects,no_cycle,no_module,no_intake}` („Create cycles to organise work into time-bound phases and track progress across sprints.“, „Create modules to organize your work and track progress across different stages.“, „Set up intake to manage incoming requests and track how they're accepted and rejected“).
- **UI-Hinweise:** `TAnalyticsGraphsBase = "projects" | "work-items" | "custom-work-items"`; Tab-Objekt `{key, label, content, isDisabled}` (`packages/types/src/analytics.ts` Z. 41–47) – `isDisabled` war das Gating-Flag.
- **Konfidenz:** mittel.

#### PF-52 – PQL / erweiterte Filteroperatoren
- **Tier:** Pro–Enterprise (`plans.tsx` Z. 658–668; auskommentierte Zeile „Search“: „Operator capsules from text or PQL“ ab Pro).
- **Funktionsbeschreibung:** „Write Plane Query Language in search with support for Boolean operators. Soon, you can write natural language queries.“
- **Backend-Spur (CE):** Die öffentliche Work-Item-Liste lehnt `pql` und `filters` ab: HTTP 400 mit `{"pql": "PQL and structured filters are not supported on this Plane edition. Remove the pql/filters parameter and filter results client-side, or use a Plane edition that supports work item query filtering.", "unsupported_parameters": [...]}` (`apps/api/plane/api/views/issue.py` Z. 324–335). → Ziel: Parameter `pql` (Textausdruck) und `filters` (strukturierter Ausdruck) unterstützen.
- **Frontend-Spur (CE):** Rich-Filter-Erweiterungspunkte leer: `EXTENDED_LOGICAL_OPERATOR`, `EXTENDED_EQUALITY_OPERATOR`, `EXTENDED_COLLECTION_OPERATOR`, `EXTENDED_COMPARISON_OPERATOR`, `EXTENDED_MULTI_VALUE_OPERATORS`, `EXTENDED_OPERATORS` (`packages/types/src/rich-filters/operators/extended.ts`), `EXTENDED_FILTER_FIELD_TYPE`, `TExtendedFilterFieldConfigs = never` (`…/field-types/extended.ts`), `TExtended{Exact,In,Range}OperatorConfigs = never` (`…/operator-configs/extended.ts`), `TExtendedSupported{Date,Select}FilterOperators = never` (`…/derived/extended.ts`), Labels `EXTENDED_OPERATOR_LABELS_MAP`, `EXTENDED_DATE_OPERATOR_LABELS_MAP`, `NEGATED_OPERATOR_LABELS_MAP`, `NEGATED_DATE_OPERATOR_LABELS_MAP` (alle `{}`, `packages/constants/src/rich-filters/operator-labels/extended.ts`); `useFiltersOperatorConfigs` liefert `allowedOperators = CORE_OPERATORS`, **`allowNegative: false`** (`apps/web/hooks/rich-filters/use-filters-operator-configs.ts`). EE erlaubt also Negation („is not …“) und zusätzliche Operatoren.
- **Fehlt:** PQL-Parser, Operator-Kapseln aus Text, negierte Operatoren, Server-Filterung.
- **Konfidenz:** hoch (Existenz/Schnittstellen) / niedrig (PQL-Grammatik – nicht öffentlich im Repo).

#### PF-53 – Advanced Search (OpenSearch)
- **Tier:** Pro (Doku-Badge `[Pro]`, `self-hosting/govern/advanced-search.md`: „Enable full-text search in Plane with OpenSearch. Configure advanced search indexing for work items, projects, and pages“; Batch-Indexierung über Redis ≥ 6.2).
- **Funktionsbeschreibung:** Power-K-Aktion „go to advanced search“ (`power_k.search_menu.go_to_advanced_search`, ohne CE-Referenz).
- **Migrationshinweis:** Volltextsuche in PostgreSQL (`tsvector`, `pg_trgm`) bzw. pgvector für semantische Suche statt OpenSearch (ADR-000/004).
- **Konfidenz:** mittel.

### 4.3 Workspace- und Benutzerverwaltung

#### PF-54 – Rollen: Pre-defined Roles / RBAC / GAC
- **Tier:** Free/One „Basic“; Pro „Pre-defined roles“; Business „RBAC“; Enterprise „GAC“ (`plans.tsx` Z. 695–704; Highlights Business „RBAC“, Enterprise „GAC“).
- **Funktionsbeschreibung:** Matrix-Text „Choose from one of four pre-defined roles or create custom ones with RBAC.“ CE hat **drei** feste Rollen: `ROLE_CHOICES = ((20, "Admin"), (15, "Member"), (5, "Guest"))` (`apps/api/plane/db/models/workspace.py` Z. 19), identisch `EUserWorkspaceRoles`, `EUserProjectRoles`, `EUserPermissions` (`packages/types/src/workspace.ts` Z. 15–19, `packages/types/src/project/projects.ts` Z. 13–17, `packages/types/src/enums.ts` Z. 7–11); Rollenbeschreibungen `role_details.*` (`common.json`). „GAC“ (Granular Access Control) und Whitepaper-Begriffe „custom roles, granular access control“ (WebSearch) = Enterprise Grid. Die vierte vordefinierte Rolle ist im Repo **nicht** benannt (Abschnitt 10). Icon `AccessAndRolesOutline/Filled`.
- **Fehlt:** Rollenmodell mit Permissions, Custom Roles, Zuweisung auf Workspace-/Projekt-/Teamspace-Ebene.
- **Konfidenz:** mittel (Existenz) / niedrig (Permission-Katalog).

#### PF-55 – Member-/Seat-/Guest-Limits (entfällt)
- **Tier/Werte:** siehe Matrix 2.6 Z. 676, 706. Zusätzliche Spuren: `common.add_seats` „Add Seats“, `workspace.members_import.summary.message.seat_limit` „Unable to import members due to seat limit restrictions.“, Developer-Docs „A bundle of 12 Free user seats per workspace“.
- **CE-Status (korrigiert):** „im CE vorhanden (nur Cloud-Gating)“: Die CE kennt die Rolle Guest (`apps/api/plane/db/models/workspace.py` Z. 19) und erzwingt weder Seat- noch Guest-Kontingente; die Matrix-Zeile „Guests“ (`free: false`) beschreibt nur das Cloud-Gating.
- **Migration:** Entfällt (ADR-001). Keine Seat-Prüfung.

#### PF-56 – Approvals
- **Tier:** Business/Enterprise (Coming soon, `plans.tsx` Z. 717–727; `BUSINESS_PLAN_FEATURES` „Workflows + Approvals“). **Widerspruch (Verifikation):** Die Doku 2026 kennt nur Workflow-Approval-Flows und ordnet sie **Enterprise Grid** zu (Dok. 25 F03, verifiziert in `_data/P06.paid.json`); für die Matrix-Zeile „Approvals“ (Workspace-, Projekt-, Work-Item-Type-Ebene) bleibt Business der einzige Beleg.
- **Funktionsbeschreibung:** „Set workspace, project, and work item type approvals to designated admins.“ Konkret im Repo nur als Workflow-Reviewer (PF-68: „When reviewed by … Reviewers are people who are permitted to move work items from one state to another.“) und Timesheet-Approvals (PF-03). WebSearch (plane.so/business): „assign required reviewers, and block work from moving without sign-off … designated approvers per transition“. Icon `ApproverOutline/Filled`. Inbox-Tour-Text „Your inbox keeps all mentions, approvals, and activity in one place“ (`product_tour.navigation.step_one.description`).
- **Konfidenz:** mittel.

#### PF-57 – Admin Interface / PF-58 – Workspace Activity Logs / PF-59 – API-enabled Audit Logs
- **Tier:** jeweils Business/Enterprise (`plans.tsx` Z. 729, 740, 751; Audit Logs Coming soon); WebSearch: Enterprise Grid „API audit logs“, Changelog v2.2.0 „audit logs for workspace and member activity“.
- **Funktionsbeschreibung:** Admin Interface „Get an admin overview to manage workspace and project settings.“; Activity Logs „See filterable activity logs for your entire workspace.“; Audit Logs „See a full-workspace audit log and use APIs to flag Plane activity in compliance systems.“
- **CE-Spuren:** `mutateWorkspaceMembersActivity` ist „no-op in CE“ (`apps/web/store/workspace/index.ts` Z. 385–391); **Teilfunktion im CE (Verifikation):** Aktivität eines einzelnen Mitglieds im Workspace `GET /api/workspaces/<slug>/user-activity/<user_id>/` (Filter `project` mehrfach, paginiert, Sortierung `-created_at`, ohne Felder `comment`, `vote`, `reaction`, `draft`; `WorkspaceUserActivityEndpoint`, `apps/api/plane/app/views/workspace/user.py` Z. 409–435) und CSV-Export eines Tages `POST …/user-activity/<user_id>/export/` mit Pflichtfeld `date`, max. 10 000 Zeilen (`ExportWorkspaceUserActivityEndpoint`, `apps/api/plane/app/views/workspace/base.py` Z. 340–361; URLs `apps/api/plane/app/urls/workspace.py` Z. 137–146) → PF-58 „teilweise im CE“; Profil-Einstellungen „Activity – Track your recent actions and changes across all projects and work items.“ (`account_settings.activity.*`, ohne CE-Referenz); Icons `AuditLogsOutline/Filled`, `LogsOutline/Filled`, `LogsAltOutline/Filled`, `ActivityOutline/Filled`. CE-Modell `APIActivityLog` (`apps/api/plane/db/models/api.py`) protokolliert API-Aufrufe.
- **Konfidenz:** niedrig–mittel.

#### PF-60 – Mitglieder-Import per CSV
- **Tier:** unklar.
- **Funktionsbeschreibung:** Workspace: „Import Members from CSV – Upload a CSV with columns: Email, Display Name, First Name, Last Name, Role (5, 15, or 20)“; Dropzone „Drop CSV file here“/„Drag & drop or click to upload“/„Only .csv files supported“; Buttons Cancel/Import/Try Again/Close/Done; Fortschritt „Uploading...“/„Importing...“; Ergebnis „Import Failed“/„Import Complete“, „Successfully added {count} member{plural} to the workspace.“, „No members were imported from the CSV file.“, Statistik „Successful“/„Failed“, „Download errors“; Toast „Invalid file – Only CSV files are supported.“ (`workspace.members_import.*`). Projekt: „Upload a CSV with columns: Email and Role (5=Guest, 15=Member, 20=Admin). Users must already be workspace members.“, „Download sample CSV“, Statistik „added“, „reactivated“, „already_members“, „skipped“ (`project.members_import.*`).
- **Konfidenz:** hoch (UI/Format).

#### PF-61 – Multi-Workspace-Management (Enterprise Grid)
- **Tier:** Enterprise Grid (WebSearch: plane.so/business „Business tier governs a single workspace, while Enterprise Grid adds multi-workspace management“; Changelog v2.2.0 „support for multiple workspaces“).
- **Hinweis:** Das CE erlaubt bereits mehrere Workspaces pro Instanz; gemeint ist zentrale Verwaltung mehrerer Workspaces einer Organisation (Lizenz-/Governance-Ebene). Keine Repo-Spuren.
- **Konfidenz:** niedrig.

#### PF-62 – Workspace-Access-Tokens
- **Tier:** unklar.
- **Funktionsbeschreibung:** Leerzustand „No Access tokens yet – Generate secure API tokens to connect your workspace with external systems and applications.“ (CTA „Add access token“, `settings_empty_state.workspace_tokens`), Workspace-Settings „Access Tokens“ (`workspace_settings.settings.api_tokens.*`, Heading/Description ohne CE-Referenz). CE: Personal Access Tokens nur im Profil; Route `:workspaceSlug/settings/api-tokens` leitet um (`apps/web/app/routes/core.ts` Z. 383).
- **Konfidenz:** mittel.

### 4.4 Automationen und Workflows

#### PF-63 – Custom Automations (Trigger → Bedingung → Aktion)
- **Tier (korrigiert):** **Business** (Doku 2026 über Dok. 25 F09: projektbezogene Automationen mit „Change property“ und „Add comment“ ab Business; „Send webhook“, „Run script“, Scheduled/Cron und globale Automationen nur Enterprise Grid, Dok. 25 F11–F14). **Widerspruch:** `plans.tsx` Z. 769–778 („Trigger And Action“) und `PRO_PLAN_FEATURES` „Trigger And Action“ nennen Pro; die Matrix ist der ältere Stand. Anzahl Pro 5,000 / Business 10,000 / Enterprise Unlimited (entfällt).
- **Funktionsbeschreibung (`automation.json`):** Einstellung „Custom automations“ mit „Create automation“. Modal „Create automation“/„Update automation“: Titel („Name your automation.“, Pflicht „Title is required“), Beschreibung („Describe your automation.“). Editor: **Scope** („Run on“), **Trigger** („What's the trigger for this automation?“, Sektionen „Plane events“ und „Time based“; „Fixed schedule“ mit Modus „Fixed“/„Cron“; Fixed: Frequenz „Daily“/„Weekly“/„Monthly“, „Select day“, „Day of month“, „Every“, „Day {day}“, Zeit „Hour“/„Minute“ mit Suffix „hr“/„min“, „AM“/„PM“, „Timezone“ („Select a timezone“); Validierung „Select at least one day of the week.“, „Select a day of the month.“; Zusammenfassungen „Every day at {time} ({timezone}).“, „Every week on {days} at {time} ({timezone}).“, „Every month on day {day} at {time} ({timezone}).“; Cron: „Enter Cron expression“ (Platzhalter „0 9 * * 1-5“), „Invalid cron expression.“, Vorschau „This Cron expression runs "{description}".“, Zusammenfassung „{description} ({timezone}).“; Trigger-Typ nach Anlage unveränderlich: „You can't change the trigger type once created“), **Bedingungen** („Provided“, „Add condition“), **Aktionen** („What does the automation do?“, Handler „Add comment“, „Change property“, „Run Script“; Change property: „Select a property“, „Select“, „Select value(s)“, „Select date“, Pflichtfehler für Name/Typ/Wert; Blocks „Add comment“, „Run script“, „Change property“; „Disable the automation before deleting its only action.“), **Konjunktionen** „And“, „Or“, „If“, „Then“. Aktivieren: Hinweis „Hit 'Enable' whenever your automation is complete. Once enabled, the automation will be ready to run.“; Validierung „Automation must have a trigger and at least one action to be enabled.“; Löschen nur deaktiviert („Automation must be disabled before deleting it.“). **Tabelle:** Spalten „Automation title“, „Scope“, „Projects“, „Last run on“, „Created on“, „Last updated on“, „Last run status“, „Average duration“, „Owner“, „Executions“. **Aktivität:** Filter „Show fails“, „All“, „Only activity“, „Only run history“; Run-History-Spalte „Initiator“. Leerzustand „There're no automations to show yet. – Automations help you eliminate repetitive tasks by setting triggers, conditions, and actions. Create one to save time and keep work moving effortlessly.“ Toasts create/update/enable/disable/delete/action create/update.
- **UI-Hinweise:** Power-K „New automation“ (`power_k.creation_actions.create_project_automation`). Icons `AutomationsOutline/Filled`, `TriggerOutline/Filled`, `RulesOutline/Filled`, `AutopilotGoOutline/Filled`. CE-Projektseite `…/settings/projects/:projectId/automations` (Layout + Page, `apps/web/app/routes/core.ts` Z. 342–347) enthält nur Auto-Archive/Auto-Close (`apps/web/components/automation/*`) – Custom Automations werden dort ergänzt.
- **Datenmodell-Hinweise:** Automation (Titel, Beschreibung, Scope Projekt/Global, Projekte, Owner, enabled), Trigger (Typ, Ereignis bzw. Zeitplan fixed/cron + Zeitzone), Bedingungen (Baum mit And/Or), Aktionen (Typ + Konfiguration), Run-Historie (Status, Dauer, Initiator, Zeitpunkt). Zeitzonen: CE nutzt `pytz.common_timezones`.
- **Konfidenz:** hoch (UI/Validierung) / mittel (Ereigniskatalog „Plane events“ nicht im Repo).

#### PF-64 – Globale (Workspace-)Automationen
- **Tier (korrigiert):** Enterprise Grid (Doku über Dok. 25 F13; Gegenindiz dort: Screenshot `developer-docs/docs/public/images/webhooks/create-webhook.webp` zeigt den Eintrag „Automations“ in den Workspace-Settings eines Business-Workspace). Kein Repo-Beleg.
- **Funktionsbeschreibung (`automations.global_automations.*`):** Workspace-Einstellung „Automations – Standardize processes across your workspace with global automations.“; Projektauswahl „Select projects to run this automation on“: „All projects – Automation will run for all projects in the workspace.“ oder „Select projects – Automation will run for selected projects in the workspace.“ (Platzhalter „Select projects“); Scope-Spalte „Global“ bzw. „Project“ mit „Multiple“/„All“.
- **Konfidenz:** hoch.

#### PF-65 – Decisions And Loops Automation
- **Tier:** Business/Enterprise (Coming soon, `plans.tsx` Z. 780–790; `BUSINESS_PLAN_FEATURES` „Decision + Loops Automation“).
- **Funktionsbeschreibung:** „Use actions as triggers indefinitely in an automation flow.“ (Verkettung/Verzweigung, Konjunktion „If/Then“ in `automations.conjunctions`).
- **Konfidenz:** niedrig.

#### PF-66 – Anzahl Automationen (entfällt)
- Pro 5,000 / Business 10,000 / Enterprise Unlimited (`plans.tsx` Z. 792–801); `ENTERPRISE_PLAN_FEATURES` „Unlimited and full Automation Flows“. Migration: kein Limit (ADR-001).

#### PF-67 – Auto-Reminders
- **Tier (korrigiert):** Business (nur Web-Beleg über Dok. 25; kein Repo-Beleg, keine Matrix-Zeile).
- **Funktionsbeschreibung (`project_settings.automations.auto-remind.*`):** „Auto-reminders – Plane will automatically send reminders via email and in-app notifications to keep your team on track with deadlines.“ Einstellung „Send reminder before“ (Zeitraum vor Fälligkeit). Icon `AutoReminderOutline/Filled` (neben `AutoArchive*`, `AutoClose*` des CE).
- **Konfidenz:** mittel.

#### PF-68 – Workflows
- **Tier:** Business (`BUSINESS_PLAN_FEATURES` „Workflows + Approvals“); Doku 2026 (über Dok. 25 F01/F02): Business = **ein** Default-Workflow je Projekt, **mehrere typ-spezifische Workflows** (Zuordnung je Work Item Type, wie unten in den Texten beschrieben) nur Enterprise Grid; Approval-Flows an Transitionen Enterprise Grid (Dok. 25 F03). Die frühere Angabe „a single workflow per project“ für Pro (WebSearch-Zusammenfassung plane.so/pricing) ist UNVERIFIZIERT (Dok. 25 O21).
- **Funktionsbeschreibung (`workflow.json`, `project_settings.workflows.*`, `settings_empty_state.workflows`):** Projekt-Einstellung „Workflows – Automate work item transitions and set rules to control how tasks move through your project pipeline.“ Schalter „Enable workflows – Set workflows to control work item movement“ (Tooltips „No states are added to the workflow.“, „No work item types are added to the workflow.“, „No states or work item types are added to the workflow.“; Toasts „Enabling/Disabling workflows“). **Mehrere Workflows** je Projekt: „Add new workflow“, Suche „Search workflows“, Anlage „Create new workflow“ mit Name (Pflicht, <255, nur Buchstaben/Ziffern/Leerzeichen/Bindestrich/Apostroph), Beschreibung (gleiche Zeichenregel), **Work item type** (Zuordnung je Typ); Fallback „This workflow applies to any work item type that is not assigned to a workflow.“ Detail „Define workflow“, „Add states“ (Leer: „All states are in use – All defined states for this project are already present in your current workflow.“); **Unmapped States**: „Unmapped states detected – Some work items for the selected types are currently in states that do not exist in this workflow. If you enable this workflow, these items will automatically move to the initial state for this workflow.“ (Label „Missing states“). **Je State:** „Allow new work items“ (Tooltip deaktiviert: „Work item creation is disabled for this state“; Default-State: „Default state lets all members create new work items. This can't be changed“), Zähler „{count} permitted state change(s)“, „{count} listed reviewer(s)“; Regel „Add permitted state change“ → „Change state to“ + „When reviewed by“ (Tooltip „Reviewers are people who are permitted to move work items from one state to another.“, „Add reviewers“); Baumdarstellung „For work items in … can move it to“. Verhalten in Boards: unzulässiges Ziel → „You can't move this work item here.“; Label „State change“. Quick Actions „View change history“, „Reset workflow“ (Bestätigung „If you reset this workflow, all your state-change rules will be deleted…“); Regel löschen („Once deleted, you can't undo this change…“). Upsell-Text „Control the chaos of changes and reviews with Workflows. – Set rules for where your work moves, by who, and when with Workflows in Plane.“
- **UI-Hinweise / CE-Stubs:** `useWorkFlowFDragNDrop(groupBy, subGroupBy)` liefert `{workflowDisabledSource: undefined, isWorkflowDropDisabled: false, getIsWorkflowWorkItemCreationDisabled: () => false, handleWorkFlowState: () => {}}` (`apps/web/components/workflow/use-workflow-drag-n-drop.ts`); State-Dropdown in EE mit Workflow-Gating `typeId`, `isForWorkItemCreation`, `scopedProjectIds` (Kommentar `apps/web/components/dropdowns/state/state-select.tsx` Z. 53–54; `packages/blocks/src/property-select/state-select.tsx` Z. 41 „states — used when workflows are disabled or unavailable“); `DISPLAY_WORKFLOW_PRO_CTA = false` (`packages/constants/src/state.ts` Z. 114); Fetch-Keys `WORKSPACE_WORKFLOW_STATES(workspaceSlug)`, `PROJECT_WORKFLOWS(projectId, projectRole)` (`packages/constants/src/fetch-keys.ts` Z. 71–72, 196–197); Bulk-Fehler `invalid_state_transition`. Icons `WorkflowsOutline/Filled`, `ApproverOutline/Filled`, `HistoryOutline/Filled` (Änderungshistorie, `common.change_history` „Change History“). Illustration `workflow` (horizontal + vertical).
- **Datenmodell-Hinweise:** Workflow (Projekt, Name, Beschreibung, Work-Item-Typen, aktiv, Default/Fallback), WorkflowState (State, `allow_issue_creation`), Transition (von State → zu State) mit Reviewer-Liste (User), Änderungshistorie.
- **Konfidenz:** hoch.

#### PF-69 – Plane Runner / Scripts
- **Tier (korrigiert):** Enterprise Grid (Doku https://docs.plane.so/automations/plane-runner über Dok. 25 F19 und Dok. 22 P03-F28; Gegenindiz: Screenshot `create-webhook.webp` zeigt „Plane Runner“ in einem Business-Workspace).
- **Funktionsbeschreibung:** Workspace-Einstellung „Plane Runner“ mit Heading „Scripts“, Button „New Script“, Beschreibung „Automate your workflows with custom scripts and automation rules.“ (`workspace_settings.settings.runners.*`); Automationsaktion „Run Script“. Illustrationen `runner-functions`, `runner-scripts`, `script`; Icons `ScriptsOutline/Filled`, `FunctionOutline/Filled`, `VariableOutline/Filled`, `SandboxOutline/Filled`.
- **Migrationshinweis:** Script-Ausführung im .NET-Kontext erfordert Sandbox (z. B. isolierter Container/Jint/Wasm) – Sicherheitsentscheidung offen (Abschnitt 10).
- **Konfidenz:** niedrig–mittel.

### 4.5 Wissensmanagement (Pages, Wiki, Editor)

#### PF-70 – Real-time Collab (Live-Cursor/Presence)
- **Tier:** One–Enterprise (`plans.tsx` Z. 820–829; `ONE_PLAN_FEATURES` „Real-time collab + public views and page“).
- **Funktionsbeschreibung:** „Edit a page together with members in your project, team, or workspace.“ Das CE synchronisiert Pages bereits kollaborativ (Hocuspocus/Yjs, `apps/live/*`, `packages/editor/src/hooks/use-collaborative-editor.ts`, `use-yjs-setup.ts`), deaktiviert aber in **allen** Editoren die Extension **`collaboration-cursor`** (sowie `ai`): `useEditorFlagging` → `document/liteText/richText.disabled = ["ai", "collaboration-cursor"]` (`apps/web/hooks/use-editor-flagging.ts`). Bezahlfunktion = sichtbare Cursor/Selektionen/Namen anderer Bearbeiter (Awareness) und Kollaboration in Team-/Workspace-Pages (Live-Server kennt nur `TDocumentTypes = "project_page"`, `apps/live/src/types/index.ts` Z. 26; `getPageService` wirft für andere Typen „Invalid document type“, `apps/live/src/services/page/handler.ts` Z. 12–21).
- **Migrationshinweis:** YDotNet-Server muss Awareness-Messages durchreichen (ADR-002); Dokumenttypen `project_page`, `workspace_page` (Wiki), `teamspace_page` vorsehen.
- **Konfidenz:** mittel–hoch.

#### PF-71 – Work item Embeds
- **Tier:** One–Enterprise (`plans.tsx` Z. 831–840).
- **Funktionsbeschreibung:** „Embed work items from any project you are a member of.“ CE-Editor besitzt `WorkItemEmbedExtensionConfig` (Tag `issue-embed-component`, `packages/editor/src/extensions/work-item-embed/extension-config.ts` Z. 41, 47) nur in `DocumentEditorExtensionsWithoutProps` (Parsing/Server, `packages/editor/src/extensions/core-without-props.ts` Z. 28, 66); die interaktive Extension mit `widgetCallback` (`work-item-embed/extension.tsx` Z. 15, 33) wird im CE-Dokument-Editor nicht registriert (Registry enthält nur `SlashCommands`, `packages/editor/src/extensions/document-extensions.tsx`), zusätzliche Slash-Befehle sind leer (`coreEditorAdditionalSlashCommandOptions` → `[]`, `packages/editor/src/extensions/additional-slash-command-options.tsx`). Beim PDF/Markdown-Export entfernt das CE Embeds (`apps/web/hooks/use-parse-editor-content.ts` Z. 155–156, 213–214). `TExtensions` enthält `"issue-embed"` (`packages/editor/src/types/extensions.ts` Z. 7); `TEmbedItem {id, title, subTitle, icon, projectId, workspaceSlug}` (`packages/editor/src/types/embed.ts`).
- **Fehlt:** Slash-Befehl „Work item“, Such-Popover, Embed-Karte (Live-Daten), Export-Darstellung.
- **CE-Status (korrigiert):** „Stub/UI-Hülle im CE“ statt „teilweise“: Die interaktive Extension existiert als Code, wird aber im CE nirgends registriert und kein CE-UI kann ein Embed erzeugen (`WorkItemEmbedExtension` nur in `packages/editor/src/extensions/work-item-embed/extension.tsx` Z. 26 definiert, ohne Verwendung). Tier-Hinweis: Dok. 26 zitiert das Doku-Label „Work item Pro“; `plans.tsx` nennt One (One-Plan laut `base.tsx` Z. 29–30 nicht mehr erhältlich).
- **Konfidenz:** hoch.

#### PF-72 – Link-to-work items (Pages ↔ Work Items)
- **Tier:** One–Enterprise (`plans.tsx` Z. 842–851; `ONE_PLAN_FEATURES` „Link pages in issues and vice-versa“).
- **Funktionsbeschreibung (`issue.pages.*`):** Work-Item-Detail-Abschnitt „Linked pages“ mit Aktion „Link pages“ / „Link pages to“, Filter „Show Wiki pages“, Platzhalter leerer Seite „This is an empty page. Why don't you write something inside and see it show up here like this placeholder“; Toasts „Pages updated“/„Pages update failed“, „Page removed“/„Page removal failed“. Icon `LinkPageOutline/Filled`.
- **API-Hinweise:** Developer-Docs `api-reference/work-item-pages/` → P02 §2.14/§4.9.
- **Konfidenz:** hoch.

#### PF-73 – Publish Pages
- **Tier:** One–Enterprise (`plans.tsx` Z. 853–862).
- **Funktionsbeschreibung:** „Put your pages on the web for external users and let them comment without signing into your workspace.“ Upsell-Tab „Publish pages“ (`wiki.upgrade_flow.tabs.publish_pages`). `DeployBoard` kennt `("page", "Page")` (`apps/api/plane/db/models/deploy_board.py` Z. 25); Space-App hat keine Page-Route (`apps/space/app/routes.ts`). Icon `GlobeOutline/Filled`, `WebDisabledOutline/Filled`.
- **CE-Status (korrigiert):** „Stub/UI-Hülle im CE“ statt „teilweise“: Das CE-Backend legt `DeployBoard` ausschließlich mit `entity_name="project"` an bzw. fragt nur diese ab (`apps/api/plane/app/views/project/base.py` Z. 83, 545, 578; alle `apps/api/plane/space/views/*.py`), es gibt weder Publish-UI noch Space-Seite für Pages. Tier-Hinweis: Dok. 26 zitiert die Doku „Publish erfordert Pro“; `plans.tsx` nennt One.
- **Konfidenz:** mittel–hoch.

#### PF-74 – Wiki (Workspace-Pages) inkl. Collections
- **Tier (korrigiert):** **Pro**. `plans.tsx` Z. 865–874 nennt One–Enterprise; spezifischer und aktueller sind der Upsell-Text „Upgrade to unlock Wiki – … with Plane Pro.“ (`wiki.upgrade_flow.title`/`.description`, `packages/i18n/src/locales/en/wiki.json`), `PRO_PLAN_FEATURES` „Wikis“, plane.so/pro (WebSearch) „workspace Wiki“ sowie die Doku-Kennzeichnung „Wiki Pro and above“ / „Collections Pro“ (WebSearch im Verifikationslauf, https://docs.plane.so/pages/collections; Dok. 26). **Private Collections:** Business (dieselbe Quelle; Dok. 26).
- **Funktionsbeschreibung:** „Create company-wide wikis or knowledge bases without creating a project.“ Workspace-Pages unter `/:ws/wiki/:pageId` (Power-K-Suchergebnis verlinkt Seiten ohne Projekt nach `/${workspace__slug}/wiki/${page.id}`, `apps/web/components/power-k/ui/modal/search-results-map.tsx` Z. 99–104; Pfad-Erkennung `isWikiPath`, `apps/web/hooks/use-workspace-paths.ts` Z. 18–20; Home ohne Projekt-Leerzustand im Wiki, `apps/web/components/home/home-dashboard-widgets.tsx` Z. 78–89). **Collections (`wiki.json` `wiki_collections.*`):** vordefinierte Collections „General“, „Private“, „Shared“, „Archived“; Fallback-Name „Collection“; Anlegen „Create a collection“ („Give a title to the collection“, Pflicht, <255), „Edit collection“; Löschen „Delete collection – This collection has {pageCount} page(s). Choose what happens to them.“ mit Optionen „Transfer pages and delete collection – Move all pages to another collection before deleting. Pages and their permissions are preserved.“ (Warnung „Moved pages will inherit the permissions of the selected collection.“, Ziel „Move pages to“) oder „Delete collection with pages – Permanently delete the collection and all its pages. This action can't be undone.“; Header „Add page“; Menü „Create new page“, „Add existing page“, „Edit collection“, „Collection options“; Modal „Add existing page“ (Suche „Search for pages“, Ergebnis „{count} page(s) added to collection.“, „No pages found matching your search“, „No pages available to move“, Button „Move“); Liste mit Spalten „Page name“, „Owner“, „Nested pages“, „Last activity“, „Actions“, Markierungen „Invite only“, „Restricted Access“, „Untitled“, Aufklappen „Collapse page“/„Expand page“, Leer „No pages yet – This collection doesn't have any pages right now.“, Filter-Leer „No matching pages“; Toasts `wiki_collections.toasts.{created, create_error, renamed, rename_error, transferred_deleted, deleted_with_pages, delete_error, target_required, create_page_error, create_page_in_collection_error, collection_link_copied}` (vollständig, `wiki.json`). Seitenaktionen „Remove from collection“; Move-Dialog-Platzhalter „Search for wiki collections, projects, and teamspaces“ / „Search for wiki collections and projects“; Fehler-Toast „Moved to wiki – Page was moved to wiki, but could not be added to the selected collection. It remains in General.“ (`page.json`). Upsell „Upgrade to unlock Wiki – Unlock public pages, version history, shared pages, real-time collaboration, and workspace pages for wikis, company-wide docs, and knowledge bases with Plane Pro.“ mit Tabs „Nested Pages“, „Add embeds“, „Publish pages“, „Comments“ und Button „Download data“ (`wiki.upgrade_flow.*`) – entfällt. Leerzustand „Write a note, a doc, or a full knowledge base.“ (`workspace_empty_state.wiki`).
- **Datenmodell-Hinweise:** CE-`Page` hat bereits `is_global` (Workspace-Page), `parent`, `moved_to_page`, `moved_to_project`, `sort_order`, `access` 0 Public/1 Private, `owned_by`, `is_locked`, `archived_at`, `logo_props`, M2M `projects` über `ProjectPage` (`apps/api/plane/db/models/page.py` Z. 23–58). Collections fehlen (Collection, Zugehörigkeit Page↔Collection, Rechte „Invite only“/„Restricted“). Workspace-Feature-Flag `wiki`; OAuth-Scope „wiki – Access to wiki, and all wiki related entities“ (`workspace_settings.settings.applications.scope_description.wiki`).
- **UI-Hinweise:** Sub-Brand-Icon `wiki` (Propel `sub-brands`); Empty-State-Assets `apps/web/app/assets/empty-state/wiki/navigation-pane/*` (im CE für Navigation-Pane verwendet).
- **Konfidenz:** hoch.

#### PF-75 – Page-Exports (Word-kompatibel, Warteschlange)
- **Tier:** Pro „One download at a time“; Business/Enterprise „Queued downloads“ (`plans.tsx` Z. 876–885).
- **Funktionsbeschreibung:** „Export page content into PDFs or Word-compatible docs.“ CE: clientseitiger Export **PDF** (`@react-pdf/renderer`, Seitenformate) und **Markdown** im `ExportPageModal` (`apps/web/components/pages/modals/export-page-modal.tsx` Z. 40 `TExportFormats = "pdf" | "markdown"`, Default `export_format: "pdf"`, `page_format: "A4"`); Live-Server hat zusätzlich `pdf-export.controller.ts` (`apps/live/src/controllers/`). Bezahl: Word-kompatibles Format (DOCX) und serverseitige, gequeuete Downloads; Upsell-Banner „Nested pages require a paid plan. Upgrade to unlock.“ beim Download (`wiki.nested_pages_download_banner.title`).
- **Migrationshinweis:** PDF/DOCX serverseitig in .NET (ADR-002 Konsequenz), Job-Queue.
- **Konfidenz:** mittel.

#### PF-76 – Page-Versionen (Aufbewahrung, Hervorhebung)
- **Tier:** Pro „2 days“; Business „3 months“; Enterprise „Unlimited“ (`plans.tsx` Z. 898–907).
- **Funktionsbeschreibung:** CE erstellt Versionen und begrenzt auf **20 je Page** (`apps/api/plane/bgtasks/page_version_task.py` Z. 72–74; Cleanup `get_page_versions_queryset` „beyond the maximum allowed (20 per page)“, `apps/api/plane/bgtasks/cleanup_task.py` Z. 107–124). Versionen-Panel „Version history“, „Current version“ ist CE; „Highlight changes“ (`page_navigation_pane.tabs.info.version_history.highlight_changes`) ohne CE-Referenz → Diff-Hervorhebung ist Bezahlfunktion. `PageVersion.sub_pages_data` (JSON) speichert Unterseiten-Zustand (`page.py` Z. 167).
- **Migration (ADR-001):** Aufbewahrung als Instanzeinstellung (Default „Unlimited“ bzw. großzügig), Diff-Highlighting umsetzen.
- **Konfidenz:** hoch (CE-Limit) / mittel (Highlight).

#### PF-77 – Databases + Formulas in Pages
- **Tier:** Business/Enterprise (Coming soon, `plans.tsx` Z. 909–920; Highlight Enterprise „Databases + Formulas“).
- **Funktionsbeschreibung:** „Put databases and formulas into a page without worrying about losing text, images, or other content types.“ Keine weiteren Spuren (Editor-Icons `FormulaOutline`, `InlineEquationOutline` existieren in Propel).
- **Konfidenz:** niedrig.

#### PF-78 – Nested Pages
- **Tier:** Business/Enterprise (Coming soon, `plans.tsx` Z. 922–932; `BUSINESS_PLAN_FEATURES` „Nested Pages“).
- **Funktionsbeschreibung:** „Pages inside a page, organize your pages as you see fit for the progressive disclosure.“ CE-Backend: `Page.parent` FK self (`related_name="child_page"`, `page.py` Z. 40–46); rekursive CTE `WITH RECURSIVE … descendants` in `apps/api/plane/app/views/page/base.py` Z. 67; Archiv-Restore prüft archivierten Parent (Z. 355); Unterseiten-Abfrage `parent_id=page_id` (Z. 393). Realtime-Events tragen `affectedPages {currentPage, parentPage, descendantPages}` (`packages/editor/src/types/document-collaborative-events.ts`). Wiki-Liste mit Spalte „Nested pages“ und Auf-/Zuklappen. Content-Limit-Banner (CE): „Content limit reached and live sync is off. Create a new page or use nested pages to continue syncing.“ (`page_content_limit_banner.message`).
- **Konfidenz:** hoch (Modell) / mittel (UI).

#### PF-79 – Page-Kommentare
- **Tier (korrigiert):** Business für Inline-Kommentare (Blog „Inline Page comments Business“, über Dok. 26, nicht selbst geprüft); Page-Level-Kommentare ohne Plan-Angabe. Repo: Upsell-Tab „Comments“ in `wiki.upgrade_flow.tabs.comments` (ohne Planname). Erweiterungspunkt für zusätzliche Navigation-Pane-Panels: `usePagesPaneExtensions` liefert `navigationPaneExtensions = []` (S58).
- **Funktionsbeschreibung:** Navigation-Pane-Tab „Comments“ mit Leerzustand „No comments – Add comments to see them here.“ (`page_navigation_pane.tabs.comments.*`, ohne CE-Referenz; CE-Tabs: Outline, Info, Assets – `apps/web/components/pages/navigation-pane/tab-panels/{outline,assets,root}.tsx`). Inline-Kommentare an Textstellen (nicht belegt).
- **Konfidenz:** mittel.

#### PF-80 – Pages verschieben / teilen
- **Tier (korrigiert):** Moving Pages Pro, Page-Sharing/Access-Control Business (Doku-Labels über Dok. 26, nicht selbst geprüft).
- **Zusatzspur (Verifikation):** Store-Aktion `movePage(workspaceSlug, projectId, pageId, newProjectId)` entfernt die Page nach Erfolg aus dem Projekt-Store (`apps/web/store/pages/project-page.store.ts` Z. 352–369) und ruft `ProjectPageService.move` → `POST /api/workspaces/{slug}/projects/{projectId}/pages/{pageId}/move/` mit Body `{new_project_id}` auf (`apps/web/services/page/project-page.service.ts` Z. 185–193). **Der Endpunkt fehlt im CE-Backend** (Abschnitt 9.3).
- **Funktionsbeschreibung:** `usePageFlag({workspaceSlug})` → `{isMovePageEnabled: false, isPageSharingEnabled: false}` (`apps/web/hooks/use-page-flag.ts`). Move-Dialog (`page_actions.move_page.*`): Button „Move“/„Moving“, Platzhalter „Search for projects“, „Search for projects and teamspaces“, „Search for wiki collections, projects, and teamspaces“, Regel „Private and shared pages cannot be moved to a teamspace.“, Toasts „Page moved successfully.“/„Page could not be moved. Please try again later.“. Realtime-Event `move` mit Payload `{new_project_id, new_page_id}` (CE-Konstante `DocumentCollaborativeEvents.move`, `packages/editor/src/constants/document-collaborative-events.ts`); `Page.moved_to_page`, `moved_to_project`. Sharing: Collection „Shared“, Upsell-Text „shared pages“; Leerzustände `workspace_pages.empty_state.shared.*`. Icon `MovePageOutline/Filled`, `ShareOutline/Filled`.
- **Konfidenz:** mittel.

#### PF-81 – Editor: Datei-Anhänge und externe Embeds
- **Tier (korrigiert):** Pro (Doku-Labels „Attachment Pro“, „Embed Pro“ über Dok. 26, nicht selbst geprüft); Repo-Text „Upgrade your plan to view this attachment.“ (`attachmentComponent.upgrade.description`) ohne Planname. CE-Status „Stub/UI-Hülle im CE“ (statt „fehlt“), weil die unten genannten Extension-Points existieren.
- **Funktionsbeschreibung (`editor.json`):** **Attachment-Block:** Uploader „Drop files here or click to upload“, Fehler „File too large. – Maximum size per file is {maxFileSize}MB“, „Unsupported file type. – See supported formats“, „Upload failed. – Something went wrong. Please try again.“, ARIA „Click to upload attachment“. **External Embed:** Block-Menü „Convert to Embed“, „Convert to Link“, „Convert to Rich Card“; Platzhalter „Insert your preferred embed link here, such as YouTube video, Figma design, etc.“, „Enter or paste a link“; Modal „Embed – Works with YouTube, Figma, Google Docs and more“; Fehler „Please enter a valid URL.“ Erweiterungspunkte: `IEditorPropsExtended`, `TExtendedEditorCommands`, `TExtendedEditorRefApi` = `unknown/never` (`packages/editor/src/types/editor-extended.ts`), `useExtendedEditorProps` → `{}` (`apps/web/hooks/pages/use-extended-editor-extensions.ts`), `useExtendedEditorConfig().getExtendedEditorFileHandlers` → `{}` (`apps/web/hooks/editor/use-extended-editor-config.ts`). Icons `EmbedOutline/Filled`, `AttachOutline/Filled`.
- **Migrationshinweis (ADR-004):** Externe Embeds (YouTube/Figma) sind Internet-abhängig → optional, im Airgapped-Betrieb als Link-Karte.
- **Konfidenz:** hoch (UI-Texte).

### 4.6 AI

#### PF-82 – Plane AI (Pi-Chat, AI-Block, Agents, MCP)
- **Tier:** Pro (WebSearch plane.so/pro: „1,000 AI credits per seat per month“; Business höher – Drittquelle xpay.sh 2,000; Credits „reset on the first of each month (UTC) and do not roll over“); Doku „Configure Plane AI [Commercial Edition]“ (`self-hosting/govern/plane-ai/configure-plane-ai.md`: eigene Datenbank, OpenSearch, LLM-API-Key OpenAI und/oder Anthropic, Dienst „PI“; Embeddings `configure-embedding-model.md`, `aws-opensearch-embedding.md`).
- **Funktionsbeschreibung:** Navigation „Plane AI“ (`sidebar.pi_chat`, `pi_chat`) unter `/:ws/pi-chat/` (statischer Sidebar-Key `pi_chat` in `apps/web/components/workspace/sidebar/sidebar-item.tsx` Z. 52; Pfad `isAiPath`, `apps/web/hooks/use-workspace-paths.ts` Z. 19; ungenutzter User-Menü-Eintrag `pi-chat` mit `PiChatLogo`, Zugriff Admin/Member/Guest, `user-menu.tsx` Z. 55–61); Workspace-Einstellung „Plane AI – See your work get smarter and faster with AI that is natively connected to your work and knowledge base.“ (`workspace_settings.settings.plane-intelligence.*`); **AI-Block im Editor** (`ai_block.*`: „Describe the content of this block“, „Your AI content will be generated here“, Typen „Summarize Page“, „Custom Prompt“, Aktionen „Discard“, „Generate“/„Generating“, „Rewrite“/„Rewriting“, „Use this“, „Refine“); Editor-Extension `ai` ist im CE deaktiviert (`use-editor-flagging.ts`), Plugin `packages/editor/src/plugins/ai-handle.ts`, Typ `TAIHandler {menu?(props: {isOpen, onClose})}` (`packages/editor/src/types/ai.ts`); Tour „mcp_connectors – Stop tab-switching. Connect your world. – Link GitHub, Slack to track PRs and summarize chats directly in Plane AI.“ und Checkliste „Try Plane AI chat“ (`tour.json`); OAuth-Scope „agents – Access to agents, and all agent related entities“; Illustrationen `ai-skills`, `ai-agents`, `memory`; Icons `AiStar*`, `AgentOutline/Filled`, `AgentAltOutline/Filled`, `AiSummaryOutline/Filled`, `AiFilterOutline/Filled`, `AskOutline/Filled`, `CatchupOutline/Filled`, `CopyAsPromptOutline/Filled`, `MemoryOutline/Filled`, `NewChatOutline/Filled`, Sub-Brands `plane-ai`, `plane-ai-alt`, `plane-ai-two`; Logo `PiChatLogo` (`packages/blocks/src/icons/sub-brand/pi-chat.tsx`). Developer-Docs `dev-tools/agents/*`, `dev-tools/mcp-server*.md`.
- **Im CE vorhanden (Basis-AI):** God-Mode-Seite „AI features for all your workspaces – Configure your AI API credentials so Plane AI features are turned on for all your workspaces.“ (`apps/admin/app/(all)/(dashboard)/ai/page.tsx`) mit Instanz-Keys `LLM_API_KEY`, `LLM_PROVIDER` (Default `openai`), `LLM_MODEL` (Default `gpt-4o-mini`), deprecated `GPT_ENGINE` (`apps/api/plane/utils/instance_config_variables/core.py` Z. 218–238); Endpunkte `workspaces/<slug>/ai-assistant/`, `workspaces/<slug>/projects/<pid>/ai-assistant/` (`apps/api/plane/app/urls/external.py` Z. 15, 20); Frontend `createGptTask` (`/api/workspaces/{slug}/ai-assistant/`) und `performEditorTask` (`/api/workspaces/{slug}/rephrase-grammar/`, `apps/web/services/ai.service.ts` Z. 37–48; identisch `packages/services/src/ai/ai.service.ts` Z. 68) – **`rephrase-grammar/` existiert im CE-Backend nicht** (Verifikation, `grep -rn "rephrase" apps/api/plane` ohne Treffer; Abschnitt 9.3) –, verwendet in `issue-modal/components/description-editor.tsx` Z. 123, `core/modals/gpt-assistant-popover.tsx` Z. 107, `pages/editor/ai/menu.tsx` Z. 82; `AI_EDITOR_TASKS.ASK_ANYTHING`, Ladetext „Pi is generating response“ (`packages/constants/src/ai.ts`).
- **Migrationshinweis (ADR-004):** LLM-Provider OpenAI-kompatibel (inkl. lokal: Ollama/vLLM), Embeddings in pgvector statt OpenSearch; AI-Credits entfallen (ADR-001).
- **Konfidenz:** hoch (Existenz) / niedrig (Chat-Funktionsumfang im Detail).

### 4.7 Importer und Integrationen

#### PF-83 – Importer (Jira, GitHub; weitere Importer in Dok. 28) mit Custom Props
- **Tier:** Free/One „Without custom props“, Pro+ „With custom props“ (`plans.tsx` Z. 940–960). Die Free-Werte gelten für Cloud bzw. Commercial Free – die CE enthält **keinen** Importer; für das Feature-Inventar gilt daher „ab Pro“ (Importer mit Custom Props), konsistent mit Dok. 28.
- **Funktionsbeschreibung:** Workspace-Einstellung „Imports – Connect and import data from your existing project management tools to streamline your workflow integration.“ (`workspace_settings.settings.imports.*`, ohne CE-Referenz; Leerzustand „No imports yet – Find all your previous imports here and download them.“). Import-Status-Kette (`import_status.*`): „Queued“, „Created“, „Initiated“, „Pulling“, „Timed Out“, „Pulled“, „Progressing“, „Transforming“, „Transformed“, „Pushing“, „Finished“, „Error“, „Cancelled“. Fehler des Integrationsdienstes „Silo“ (`silo_errors.*`): `invalid_query_params`, `invalid_installation_account`, `generic_error`, `connection_not_found`, `multiple_connections_found`, `cannot_create_multiple_connections`, `installation_not_found`, `user_not_found`, `error_fetching_token`, `invalid_app_credentials`, `invalid_app_installation_id`.
- **Im CE vorhanden:** `IMPORTERS_LIST` (github, jira; i18n `importer.github.*`, `importer.jira.*`) (`packages/constants/src/workspace.ts`), Modell `Importer` (`apps/api/plane/db/models/importer.py`; nur in `apps/api/plane/app/serializers/importer.py` und `apps/api/plane/utils/porters/formatters.py` referenziert, keine View/URL), Typen `packages/types/src/importer/{github-importer,jira-importer,index}.ts`, Icons `ImportsOutline/Filled`, `MigrateOutline/Filled`, Produkt-Logos der Propel-Kategorie `other-products` (vollständige Liste in 8.4). Tote Service-Aufrufe (Verifikation): `GET /api/workspaces/{slug}/importers/` und `DELETE …/importers/{service}/{importerId}/` (`apps/web/services/integrations/integration.service.ts` Z. 43, 67), `GET …/importers/{service}/` und `POST …/projects/importers/{service}/` (`apps/web/services/integrations/github.service.ts` Z. 29, 39), `GET …/importers/jira` und `POST …/projects/importers/jira/` (`apps/web/services/integrations/jira.service.ts` Z. 18, 28). **Keine** Import-Route im CE (`apps/web/app/routes/core.ts`). CE-Status daher „Stub/UI-Hülle im CE“.
- **Konfidenz:** mittel.

#### PF-84 – GitHub-Integration (inkl. GitHub Enterprise)
- **Tier:** Pro (`plans.tsx` Z. 969; Doku `self-hosting/govern/integrations/github.md` `[Pro]`).
- **Funktionsbeschreibung (`github_integration.*`, `github_enterprise_integration.*`, `integrations.*`):** „Connect and sync your GitHub work items with Plane“. Schritte: „Connect Organization – Connect your GitHub organization with Plane“ (Status „Processing“, „GitHub org added by and time“), „Connect Personal Account“ („Personal account connected – Your GitHub account is now connected to Plane“), „Repository Mapping – Map your GitHub repositories with Plane projects.“ („Link GitHub Repository to a Plane Project“, „Choose Repository...“, „Choose Project...“), **Project Issue Sync** („Sync issues from GitHub to your Plane project“, Leer „Mapped project issue sync will appear here“, „Configure Issue Sync State“, Richtung „Bidirectional - Sync issues and comments both ways between GitHub and Plane“ / „Unidirectional - Sync issues and comments from GitHub to Plane only“ mit Warnung „Data from GitHub Issue will replace data in Linked Plane Work Item (GitHub → Plane only)“, Entfernen mit Bestätigung, Hinweis „Work items are synced to {project}“, Button „Start Sync“), **Pull Request Automation / State Mapping** („Map GitHub pull request states to your Plane project“; Zustände `DRAFT_MR_OPENED` „Draft Open“, `MR_OPENED` „Open“, `MR_READY_FOR_MERGE` „Ready for Merge“, `MR_REVIEW_REQUESTED` „Review Requested“, `MR_MERGED` „Merged“, `MR_CLOSED` „Closed“, `ISSUE_OPEN` „Issue Open“, `ISSUE_CLOSED` „Issue Closed“; „Select State“, „Set State“; Option „Prevent issues from moving to an earlier state due to PR updates“). GitHub Enterprise: Formular „GitHub Enterprise Configuration“ mit „App ID“, „App Slug“, „Base URL“ (gültige URL), „Client ID“, „Client Secret“, „Webhook Secret“, „Private Key (Base64 encoded)“, Button „Connect App“. Allgemein: „{name} is not enabled for this workspace.“, „{name} integration is not configured. Please contact your instance admin to configure it.“, „Disconnect personal {providerName} account“, „Not able to access the external API. Please try again later.“, „Back to integrations“.
- **Im CE vorhanden (Legacy, nicht funktionsfähig):** Modelle `Integration`, `WorkspaceIntegration` (`apps/api/plane/db/models/integration/base.py`), `GithubRepository`, `GithubRepositorySync`, `GithubIssueSync`, `GithubCommentSync` (`…/integration/github.py`); UI `apps/web/components/integration/single-integration-card.tsx`, `apps/web/components/integration/github/select-repository.tsx`, `apps/web/components/project/integration-card.tsx`; Seite `apps/web/app/(all)/[workspaceSlug]/(settings)/settings/(workspace)/integrations/page.tsx` ist **nicht geroutet**; Service ruft `/api/integrations/` und `/api/workspaces/{slug}/workspace-integrations/` auf (`apps/web/services/integrations/integration.service.ts` Z. 18–30), außerdem (Verifikation) `DELETE …/workspace-integrations/{integrationId}/provider/` (`integration.service.ts` Z. 35), `GET …/workspace-integrations/{integrationSlug}/github-repositories` (`apps/web/services/integrations/github.service.ts` Z. 21), `POST …/workspace-integrations/{provider}/` (`apps/web/services/app_installation.service.ts` Z. 18) und `…/projects/{projectId}/workspace-integrations/{id}/github-repository-sync/` (`apps/web/services/project/project.service.ts` Z. 144, 155); alle Backend-URLs fehlen, die Legacy-Modelle werden in keiner View verwendet → CE-Status „Stub/UI-Hülle im CE“; `WEBHOOK_ALLOWED_HOSTS`-Beispiel nennt den internen Dienst „silo“ (`apps/api/plane/settings/common.py` Z. 75; `apps/api/plane/utils/ip_address.py` Z. 175). Typ-Felder `enterprise`, `is_enterprise_install` (`packages/types/src/integration.ts` Z. 69, 80).
- **Konfidenz:** hoch (UI-Texte) / mittel (Sync-Semantik).

#### PF-85 – GitLab-Integration (inkl. GitLab Enterprise)
- **Tier:** Pro (Doku `self-hosting/govern/integrations/gitlab.md` `[Pro]`).
- **Funktionsbeschreibung (`gitlab_integration.*`, `gitlab_enterprise_integration.*`):** „Connect and sync your Gitlab Merge Requests with Plane.“ „Connect Organization“, „Gitlab Project Connections – Sync merge requests from Gitlab to Plane projects.“, „Plane Project Connection – Configure pull requests state mapping from Gitlab to Plane projects“, „Link Gitlab repository to Plane project“, „Choose Entity“, „Choose Project“, „Link Plane project“, MR-Zustände mit Texten „On draft MR open, set the state to“, „On MR open, set the state to“, „On MR review requested, set the state to“, „On MR ready for merge, set the state to“, „On MR merged, set the state to“, „On MR closed, set the state to“; Issue-Sync wie GitHub (bidirektional/unidirektional). GitLab Enterprise: „Base URL“ (Platzhalter `https://glab.plane.town`), „App ID“, „Client Secret“, „Webhook Secret“, „Connect App“.
- **Konfidenz:** hoch (Texte).

#### PF-86 – Slack-Integration
- **Tier:** Pro (`plans.tsx` Z. 981; Doku `[Pro]`).
- **Funktionsbeschreibung (`slack_integration.*`):** „Connect your Slack workspace with Plane.“; persönliches Konto „Connect your personal Slack account with Plane.“/„Link your personal {providerName} account to Plane.“; „Connected Slack workspaces“ („Connected on {date}“, „Disconnect {name} workspace“); DM-Alerts „Get notified in Slack DMs for important updates, reminders, and alerts just for you.“; **Project Notifications** („Configure Slack channels for project notifications“, „Add new project notifications“, Formular „Configure Slack Channel – Receive project notifications in selected Slack channel when work item is created“ mit „Plane Project“ und „Slack Channel“, Meldungen „All projects are already connected to Slack channels.“, „All Slack channels are already connected to projects.“, Toasts create/update/delete/upsert). Matrix: Slash-Commands in Slack. Profil-Einstellung „Connections – Manage your workspace connections settings.“ (`account_settings.connections.*`).
- **Im CE vorhanden (Legacy, nicht funktionsfähig):** `SlackProjectSync` (`apps/api/plane/db/models/integration/slack.py`), `apps/web/components/integration/slack/select-channel.tsx`; tote Service-Aufrufe `…/projects/{projectId}/workspace-integrations/{integrationId}/project-slack-sync/` (GET/POST) und `…/project-slack-sync/{slackSyncId}` (DELETE) (`apps/web/services/app_installation.service.ts` Z. 32, 47, 62) → CE-Status „Stub/UI-Hülle im CE“.
- **Konfidenz:** hoch (Texte).

#### PF-87 – Sentry / PF-88 – Bitbucket Data Center
- **Tier:** Pro (Doku `self-hosting/govern/integrations/sentry.md`, `bitbucket.md` `[Pro]`).
- **Sentry (`sentry_integration.*`):** „Connect your Sentry workspace with Plane.“, „Connected Sentry workspaces“, **State Mapping** „Map Sentry issue states to your project states. Configure which states to use when a Sentry issue is resolved or unresolved.“ („Add new state mapping“, Leerzustand, Lade-/Fehlertexte für States).
- **Bitbucket DC (`bitbucket_dc_integration.*`):** „Connect and sync your Bitbucket Data Center repositories with Plane.“
- **Konfidenz:** mittel.

#### PF-89 – Zapier / PF-90 – Zendesk, Freshdesk
- **Tier:** Pro (Sektion Coming soon, `plans.tsx` Z. 992–1023). Nur Matrix-Texte: Zapier „Run if-then-else automations using Zapier.“; Zendesk/Freshdesk „Create Plane work items from … tickets.“ Migration (ADR-004): optional, abschaltbar; Zapier über Webhooks/REST abbildbar.
- **Konfidenz:** niedrig.

#### PF-91 – OAuth Bridge
- **Tier:** unklar.
- **Funktionsbeschreibung (`oauth_bridge_integration.*`):** „Validate externally-issued OIDC/JWT tokens from your IdP (Azure AD, Okta, etc.) for Plane API access.“ Install/Uninstall; Liste „Token Providers – Configure external IdPs whose JWTs are accepted as API credentials.“; Provider-Formular: Name (Pflicht), Issuer (Pflicht, `iss`), JWKS URL (Pflicht, **HTTPS** erzwungen), Audience (`aud`, kommagetrennt), User claims (Pflicht, kommagetrennt, „first match wins“ gegen Plane-E-Mail; Platzhalter „email, preferred_username, upn“), Allowed signing algorithms (≥1, asymmetrisch), JWKS cache TTL (min 60 s, Default 24 h), Rate limit („count/period“, z. B. 120/minute), „Enable this provider“; Test „JWKS Reachable“/„JWKS Unreachable“.
- **Konfidenz:** hoch (Texte).

#### PF-92 – Applications / OAuth-Apps / Marketplace / App-Mentions
- **Tier:** unklar.
- **Funktionsbeschreibung (`workspace_settings.settings.applications.*`, ~150 Schlüssel):** Workspace-Einstellung „Applications“ mit Tabs „Installed apps“, „All apps“, „Internal apps“, „Your apps“, „Third-party apps“; App erstellen („Build your own app“, „Create app“/„Update app“): App Name, Short/Long Description, App slug (eindeutig), Logo, Website, App Maker, Setup URL, Configuration URL, Webhook URL + Secret, Redirect URIs (leerzeichengetrennt), Authorized Javascript Origins, Connection Type („installed once for the workspace or let every user connect their own account“), Categories, „Supported Plans“ (entfällt, ADR-001), Privacy-/Terms-/Support-/Video-URL, Contact Email, Screenshots-Upload, **Scopes** (granular „Read-only access to“/„Write access to“ für `projects`, `wiki`, `workspaces`, `stickies`, `profile`, `agents`, `assets`; Warnung „Global scopes are expiring soon. Use granular scopes instead. For example, use project:read instead of a global read.“), Client-ID/Secret-Anzeige mit CSV-Export, „Regenerate client secret“; Consent-Screen „{app} is requesting access to your Plane workspace and profile.“ mit Workspace-Auswahl und Hinweisen („This app can only be installed after a workspace admin installs it.“, „This app hasn't been reviewed or approved by Plane yet.“); „Enable App Mentions – When this is enabled, Users can mention or assign Work Items to this application.“
- **API-Hinweise:** Developer-Docs `dev-tools/build-plane-app/{overview,create-oauth-application,oauth-scopes,choose-token-flow,webhooks,sdks,examples}.md` → P02 §6.
- **Konfidenz:** hoch (UI-Texte).

### 4.8 Sicherheit und Identität

#### PF-93 – Workspace-SSO (SAML/OIDC) mit Domain-Verifizierung („Identity“)
- **Tier:** One–Enterprise (`plans.tsx` Z. 1060, 1071 – OIDC `selfHostedOnly`); Doku-Badges `[Pro] [Business]` (`self-hosting/govern/saml-sso.md`, `oidc-sso.md`).
- **Funktionsbeschreibung (`auth.json` `sso.*`, `workspace_settings.settings.identity.*`):** Workspace-Einstellung „Identity – Configure your domain and enable Single sign-on“. **Domain management → Verified domains** („Verify the ownership of an email domain to enable single-sign on.“, „Add domain“, Liste mit Spalten „Domain name“, „Status“ = „Verified“/„Failed“/„Pending“); Add-Modal (Domain Pflicht, Format „Enter a valid domain name (e.g., plane.so)“; Erfolg „Domain added successfully. Please verify it by adding the DNS TXT record.“); Verify-Modal mit Anleitung (1. DNS-Einstellungen öffnen, 2. „Create a TXT record and paste the complete record value provided below.“, 3. „This update usually takes a few minutes but may take up to 72 hours to complete.“, 4. „Click "Verify domain"…“), Feld „TXT record value“, Buttons „Verify domain“/„I'll do it later“; Delete-Modal. **Single sign-on** (deaktiviert ohne verifizierte Domain: „Add a verified domain to configure SSO“): Karten „Enable SAML“/„Enable OIDC“ mit „Configure“/„Edit“; Wechsel-Warnung „Switch SSO Method to {newProviderShortName}? … This action will automatically disable {activeProviderLongName} … Users attempting to sign in via {activeProviderShortName} will no longer be able to access the platform until they switch to the new method.“ (= immer nur **ein** aktiver Provider); Formular „IdP-provided details for {workspaceName}“, Buttons „Configure only“, „Configure and enable“, „Save changes“; „{workspaceName} provided details for you IdP“ / „Get setup details“. SAML-Setup-Modal: Web- und Mobile-Details „Entity ID | Audience | Metadata information“, „SSO URL“, „SLO URL“, Tabelle „Mapping details“ (IdP ↔ Plane). OIDC-Setup-Modal: „Origin URL“, „Redirect URL“, „Logout URL“ (Web + Mobile).
- **Im CE vorhanden:** Instanzweite OAuth-Provider (Google, GitHub, GitLab, Gitea) in God-Mode (`TCoreInstanceAuthenticationModeKeys`, `packages/types/src/instance/auth.ts`); Erweiterungspunkte leer: `TExtendedLoginMediums = never`, `TExtendedInstanceAuthenticationModeKeys = never` (`packages/types/src/instance/auth-ee.ts`), `EXTENDED_LOGIN_MEDIUM_LABELS = {}` (`packages/constants/src/auth/extended.ts`), `useExtendedOAuthConfig` → `{isOAuthEnabled: false, oAuthOptions: []}` (`apps/web/hooks/oauth/extended.tsx`, `apps/space/hooks/oauth/extended.tsx`), `TInstanceAuthenticationModes.unavailable` (Opacity 50 % in `apps/admin/components/authentication/authentication-method-card.tsx` Z. 31). Logos aus Propel-Kategorie `other-products`: `saml`, `oidc` (`…/dist/icons/other-products/{saml,oidc}.d.ts`).
- **CE-Status (korrigiert):** „Stub/UI-Hülle im CE“ statt „fehlt“ – die genannten leeren Login-/Auth-Erweiterungspunkte (S17, S43, S52, S53) und das Kartenattribut `unavailable` (`packages/types/src/instance/auth.ts` Z. 24) sind Andockstellen. Tier-Hinweis: Die Plan-Angabe One gilt für SAML/OIDC laut Matrix; für die Workspace-Identity mit Domain-Verifizierung ist kein eigener Plan belegt (Dok. 22 P03-F06, Dok. 27: „unklar“, vermutlich Cloud-Variante, UNVERIFIZIERT).
- **Konfidenz:** hoch.

#### PF-94 – Domain Security / PF-95 – 2FA + Passkeys / PF-96 – Password Policy
- **Tier:** Pro–Enterprise (`plans.tsx` Z. 1083, 1095, 1106).
- **Funktionsbeschreibung (nur Matrix):** Domain Security „Choose other domains that can authenticate into your Plane workspace or restrict all but one domain.“; 2FA/Passkeys „Secure your Plane workspace with device-dependent two-factor authentication and passkeys.“; Password Policy „Set custom password policies in line with your compliance requirements.“ CE: Profil „Security“ (Passwort ändern, `account_settings.security.heading`), Passwortstärke-Anzeige (`apps/admin/components/common/password-strength-indicator.tsx`, `auth.common.password.errors.*` „Password length should me more than 8 characters“). God-Mode-Doku „Configure session expiry“ (`self-hosting/govern/god-mode/session-expiry.md`, ohne Badge).
- **Konfidenz:** niedrig (Details).

#### PF-97 – LDAP
- **Tier:** Enterprise (Coming soon, `plans.tsx` Z. 1117–1127); Doku „LDAP authentication [Enterprise Grid]“ – „Plane Commercial Edition with an active Enterprise Grid license“ (`self-hosting/govern/ldap.md`). Für die JSON-Feature-Liste wird die aktuellere Doku-Bezeichnung **Enterprise Grid** verwendet (konsistent mit Dok. 22 P03-F07 und Dok. 27).
- **CE-Status (korrigiert):** „Stub/UI-Hülle im CE“ (Login-Erweiterungspunkte S17, S52, S53; Texte `auth.ldap.header.*`, `auth.common.username.*`).
- **Funktionsbeschreibung:** Login-Option „Continue with {ldapProviderName}“ mit Unterzeile „Enter your {ldapProviderName} credentials“, Felder „Username“ („Enter your username“) und Passwort (`auth.ldap.header.*`, `auth.common.username.*`).
- **Konfidenz:** hoch (Login-UI) / mittel (Konfiguration → Doku).

#### PF-98 – IdP-Group-Sync (+ SCIM)
- **Tier:** Enterprise Grid (WebSearch Whitepaper: „LDAP, SCIM, IdP group synchronization, custom roles, granular access control, and API-enabled audit logs as Enterprise Grid additions“).
- **Funktionsbeschreibung (`workspace_settings.settings.group_syncing.*`):** „Group syncing – Link identity provider groups to projects and roles. User access updates automatically when group membership changes in your IdP, simplifying onboarding and offboarding.“ Schalter „Enable group syncing – Automatically add users to projects based on identity provider groups.“ Konfiguration „Configure group sync“: „Sync on login – Update group membership and project access when a user signs in.“, „Offline sync – Runs sync every six hours automatically, without waiting for users to log in.“, „Auto remove – Automatically remove users from projects when they no longer match the group.“, „Group attribute key – The identity provider attribute used to identify and sync user groups.“ (Platzhalter „Groups“). „Group mapping – Link identity provider groups to projects and roles.“ (Button „Add new group sync“; Modal Felder „User group“ (Pflicht, „Enter the IdP group names“), „Project“ (Pflicht), „Project role“ (Pflicht)); Löschen „New users from this identity group will no longer be added to the project. Users already added will keep their current role.“; Leerzustand „No group mappings yet“. Icons `GroupSyncOutline/Filled`; Illustration `group-syncing`.
- **API-Hinweise:** Developer-Docs `api-reference/idp-group-sync/` (Workspace- und Projekt-Mappings, Config) → P02 §2.6/§4.8.
- **Konfidenz:** hoch.

### 4.9 Entfallende bzw. nicht fachliche Bezahl-Merkmale

#### PF-99 – Storage-Quoten / Max File Size je Plan
- Werte siehe 2.11. Migration: entfällt (ADR-004); Upload-Limit bleibt Instanzkonfiguration (`file_size_limit` → `apps/web/hooks/use-file-size.ts`, Default `MAX_FILE_SIZE`).

#### PF-100 – Deployment-Varianten / Private deployments
- Werte siehe 2.13. Migration: entfällt; Aspire-basiertes Self-hosting/Airgapped ist Zielbild (ADR-000/004). Doku-Badges `[Enterprise Grid]` für Airgapped Docker/Kubernetes und FIPS (`self-hosting/methods/airgapped-edition*.md`, `fips-deployment.md`).
- **CE-Status (korrigiert):** „teilweise im CE“ statt „entfällt“: Die CE liefert Single-Line-Installation per `setup.sh` (`deployments/cli/community/README.md` Z. 69, `deployments/cli/community/install.sh`), Swarm (`…/README.md` Z. 77, `deployments/swarm/community`), AIO (`deployments/aio/community`), Kubernetes (`deployments/kubernetes/community`) sowie `restore.sh`/`restore-airgapped.sh` (`deployments/cli/community/`). Es fehlen DigitalOcean-/Heroku-/AWS-AMI-Marketplace-Apps und „Private deployments“ (beide entfallen, ADR-004).

#### PF-101 – Support-Kanäle / Support-SLA
- Werte siehe 2.14. Migration: entfällt. Power-K „Chat with us“ (`power_k.help_actions.chat_with_us`) entfällt bzw. wird ausgeblendet (ADR-004).

#### PF-102 – Product Tour / Get started
- **Tier:** unklar (Cloud-Onboarding; Namespace `tour.json` vollständig ohne CE-Referenz, obwohl `apps/web/components/onboarding/tour/root.tsx` existiert).
- **Funktionsbeschreibung:** Geführte Touren mit Schritten (`product_tour.{workitems,cycle,module,page,intake,mcp_connectors,navigation}.step_*`), Aktionen „Close“, „Next“, „Back“, „Done“, „Take a tour“, „Get started“, „Got it“; Demo-Projekt „Here is your demo project“; Navigations-Modal „Navigation, re-imagined“; Seite „Hey {name}, welcome aboard!“ mit Checkliste (Create a project, Create a work item, Invite team members, Create a page, Try Plane AI chat, Link Integrations), „Invite your team“, „Power up your workspace“/„Browse more integrations“, „Discover why teams switch to Plane“.
- **Migrationshinweis:** optional; Texte 1:1 übernehmen, falls Onboarding gebaut wird. Tour-Text „Use / on a page to add content from 16 block types“ dokumentiert den Ziel-Blockumfang.
- **Konfidenz:** mittel.

#### PF-103 – Billing, Trial, Seats, Upgrade-Flows
- Billing-Seite (`apps/web/components/workspace/billing/*`), Upgrade-Modal (`apps/web/components/license/*`), Business-Trial-Banner „Your 14-day Business plan trial is live!“ (`home.business_trial_banner.*`), Trial-Abbruch vor Workspace-Löschung „Cancel your trial first.“ (`workspace_settings.settings.cancel_trial.*`, `workspace_settings.settings.general.delete_modal.description`), `upgrade_request` „Ask your Workspace Admin to upgrade.“, `common.upgrade_cta.higher_subscription` „Upgrade to higher subscription“, `sidebar.upgrade_plan`, `sidebar.plane_pro`, `sidebar.business`, `common.renew`. Migration: entfällt vollständig (ADR-001). Die Route `:workspaceSlug/settings/billing` und der Settings-Eintrag `billing-and-plans` entfallen.

### 4.10 Im Verifikationslauf ergänzt

#### PF-104 – Duplicate Detection (Duplikat-Vorschläge)
- **Tier:** unklar. Commercial Edition, optionaler Teil von Plane AI, benötigt ein Embedding-Modell (Dok. 22 P03-F13, Dok. 23 WM-47, Dok. 28); keine Plan-Angabe in Repo oder Doku.
- **Funktionsbeschreibung (aus CE-Spuren):** Beim Eingeben von Titel/Beschreibung im Work-Item-Create-Modal und im Intake-Create-Modal werden entprellt mögliche Duplikate gesucht; eine Fundmeldung „Duplicate work item found“ / „Duplicate work items found“ (`common.duplicate_issue_found`, `common.duplicate_issues_found`, `packages/i18n/src/locales/en/common.json` Z. 284–285, ohne CE-Referenz) öffnet ein Duplikat-Modal (`isDuplicateModalOpen`). Aus der Trefferliste können Duplikate gelöscht oder archiviert werden (Lösch-/Archiv-Modals akzeptieren `TIssue | TDeDupeIssue`, `apps/web/components/issues/delete-issue-modal.tsx` Z. 14, 26; `apps/web/components/issues/archive-issue-modal.tsx` Z. 13, 19).
- **Datenmodell-/API-Hinweise:** Request `TDuplicateIssuePayload {title, workspace_id, issue_id?, project_id?, description_stripped?}`, Response `TDuplicateIssueResponse {dupes: TDeDupeIssue[]}`, Treffer `TDeDupeIssue {id, type_id, project_id, sequence_id, name, priority, state_id, created_by}` (`packages/types/src/de-dupe.ts`). Endpunkt im CE weder im Frontend noch im Backend benannt.
- **UI-Hinweise / CE-Stubs:** `useDebouncedDuplicateIssues(workspaceSlug, workspaceId, projectId, {name, description_html, issueId})` → `{duplicateIssues: []}` (`apps/web/hooks/use-debounced-duplicate-issues.tsx`); Modal-State `isDuplicateModalOpen`/`handleDuplicateIssueModal` in `apps/web/components/issues/issue-modal/base.tsx` Z. 68, 382, 405 (weitergereicht an `form.tsx` Z. 73) und `apps/web/components/inbox/modals/create-modal/modal.tsx` Z. 23–45 (weitergereicht an `create-root.tsx` Z. 49).
- **Migrationshinweis:** Embeddings in pgvector (ADR-000/004).
- **Konfidenz:** hoch (Existenz/Schnittstellen) / niedrig (Ranking, Schwellwerte).

#### PF-105 – Weitere Commercial-Produkte ohne Funktionsspur
- **Tier:** unklar.
- **Befund:** Für die folgenden Produkte/Features existieren im CE-Repo ausschließlich Icons im npm-Paket `@makeplane/propel` 0.7.3 bzw. reservierte Workspace-Slugs, keine Texte, Typen, Hooks oder Endpunkte: Sub-Brands `desk`, `bridge` (`dist/icons/sub-brands/{desk,bridge}.d.ts`); Workspace-Features `briefs`, `workgraph` (`dist/icons/workspace-features/{briefs,workgraph}-{outline,filled}.d.ts`); `pii-scanner` (`dist/icons/miscellaneous/pii-scanner-{outline,filled}.d.ts`; Dok. 22 P03-F33 und Dok. 27 nennen das Produkt-Flag `PII_SCANNER` und den Namen „Argus“, sekundär); `library`, `library-alt`, `excerpt`, `insert-excerpt` (`dist/icons/miscellaneous/*`); reservierte Slugs `chat`, `calendar`, `drive`, `channels` (`packages/constants/src/workspace.ts`, `apps/api/plane/utils/constants.py`).
- **Konsequenz:** Ohne Zusatzrecherche nicht spezifizierbar (OP-09).
- **Konfidenz:** hoch (Existenz der Spuren) / niedrig (Funktion).

---

## 5. Inventar aller Upgrade-/Upsell-Stellen

Ermittelt per `grep -rniE "upgrade|ProIcon|UpgradeBadge|paid.?plan|talk.?to.?sales|MARKETING_PRICING|isEnterprise|comingSoon|coming_soon|E_FEATURE_FLAGS|useFlag|feature.?flag"` über `apps/` und `packages/` (ohne `locales`, ohne `node_modules`). `isEnterprise`, `E_FEATURE_FLAGS`, `useFlag` kommen im CE **nicht** vor (EE-Feature-Flag-System nicht im Repo). Spalte „Ziel“ = Handlung in der Portierung (ADR-001).

| # | Datei | Element / Inhalt | Verkauftes Feature | Erreichbar im CE? | Ziel |
|---|---|---|---|---|---|
| U1 | `apps/web/components/workspace/upgrade-badge.tsx` | `UpgradeBadge` – Pill mit Text `t("sidebar.pro")` = „Pro“; Klassen `w-fit cursor-pointer rounded-2xl bg-accent-primary/20 text-center font-medium text-accent-secondary outline-none`, `size="md"` → `px-3 text-13`, `size="sm"` → `px-2 text-11` | generisch | – | Komponente entfällt |
| U2 | `apps/web/components/common/pro-icon.tsx` | `ProIcon` – `lucide-react` `Crown`, `text-amber-400 inline-block h-3.5 w-3.5` | generisch | – | entfällt |
| U3 | `apps/web/components/workspace/edition-badge.tsx` (gerendert in `apps/web/components/sidebar/sidebar-wrapper.tsx` Z. 85, Sidebar-Fußzeile `h-12 … border-t border-subtle bg-surface-1 p-3`) | Button `variant="tertiary" size="md"` Label „Community“, Tooltip `Version: v{version}`, öffnet `PaidPlanUpgradeModal`; ARIA `aria_labels.projects_sidebar.edition_badge` „Open paid plans' modal“ | alle Bezahlpläne | ja | Badge ohne Modal oder entfernen (Abschnitt 10, OP-01) |
| U4 | `apps/web/components/license/modal/upgrade-modal.tsx` | `PaidPlanUpgradeModal` (Dialog `size="full"`), Überschrift „Upgrade to a paid plan and unlock missing features.“, Text „Dashboards, Workflows, Approvals, Time Management, and other superpowers are just a click away. Upgrade today to unlock features your teams need yesterday.“; Karten Free/Pro/Business/Enterprise mit `PRO_/BUSINESS_/ENTERPRISE_PLAN_FEATURES`, Link „See full features list“ | Pro, Business, Enterprise | ja (über U3) | entfällt |
| U5 | `apps/web/components/license/modal/card/free-plan.tsx` | `FreePlanCard` („Free“, `FREE_PLAN_UPGRADE_FEATURES`) | One/Pro | über U4 | entfällt |
| U6 | `apps/web/components/license/modal/card/plan-upgrade.tsx` | `PlanUpgradeCard` („Monthly“/„Yearly“, Preise) | Pro/Business/Enterprise | über U4 | entfällt |
| U7 | `apps/web/components/license/modal/card/talk-to-sales.tsx` | `TalkToSalesCard` („Quote on request“, Button „Talk to Sales“) | Enterprise | über U4 | entfällt |
| U8 | `apps/web/components/license/modal/card/base-paid-plan-card.tsx` | `BasePaidPlanCard` (Tabs je Abrechnungsintervall, „Plane {planeName}“) | dito | über U4 | entfällt |
| U9 | `apps/web/components/license/modal/card/checkout-button.tsx` | `PlanCheckoutButton` („Redirecting to Stripe“ / „Upgrade to {planeName}“), `TCheckoutParams {planVariant, priceId}` | dito | über U4 | entfällt |
| U10 | `apps/web/components/license/modal/card/discount-info.tsx` | `DiscountInfo` (Preis + Rabatt) – auch in `billing/comparison/plan-detail.tsx` Z. 20, 70 | dito | ja | entfällt |
| U11 | `apps/web/components/workspace/billing/root.tsx`, `comparison/{base,feature-detail,frequency-toggle,plan-detail,plans,root}.tsx` (Route `:workspaceSlug/settings/billing`, `apps/web/app/(all)/[workspaceSlug]/(settings)/settings/(workspace)/billing/page.tsx`) | Billing-Seite „Billing & Plans – Choose your plan, manage subscriptions, and easily upgrade as your needs grow.“, Planvergleich (Abschnitt 2), Buttons „Upgrade to {Plan}“ / „Talk to Sales“, Toggle „Monthly“/„Yearly“ mit Rabatt-Pill, „Compare all features“/„Collapse comparison“ | alle | ja | Seite + Settings-Eintrag `billing-and-plans` entfallen |
| U12 | `apps/web/components/active-cycles/workspace-active-cycles-upgrade.tsx` (Seite `…/(projects)/active-cycles/page.tsx`) | Hero „On-demand snapshots of all your cycles“ + Button „Upgrade“ mit `ProIcon` → `MARKETING_PRICING_PAGE_LINK`; Gradient (dark `from-[#CFCFCF] to-[#212121]`, light `from-[#3b5ec6] to-[#f5f7fe]`); 6 Feature-Kacheln (PF-04) | Active Cycles (One) | ja | echte Active-Cycles-Seite |
| U13 | `apps/web/app/(all)/[workspaceSlug]/(projects)/active-cycles/header.tsx` Z. 16, 33 | `UpgradeBadge size="md"` neben Breadcrumb | Active Cycles | ja | Badge entfernen |
| U14 | `apps/web/components/workspace/sidebar/extended-sidebar-item.tsx` Z. 24, 199–203 | `UpgradeBadge` wenn `item.key === "active_cycles"` | Active Cycles | nein (Key nicht in `WORKSPACE_SIDEBAR_DYNAMIC_NAVIGATION_ITEMS_LINKS`) | entfernen |
| U15 | `apps/web/components/workspace/sidebar/workspace-menu-item.tsx` Z. 21, 68–71 | `UpgradeBadge` bedingungslos je Menüeintrag | alle vier Einträge von `SidebarWorkspaceMenu` (`projects`, `views`, `active-cycles`, `analytics`; `apps/web/components/workspace/sidebar/workspace-menu.tsx` Z. 33–58) | nein (`SidebarWorkspaceMenu` nirgends gerendert) | entfernen |
| U16 | `apps/web/components/project/settings/features-list.tsx` Z. 20, 119–123 | `UpgradeBadge` mit Tooltip „Pro feature“ wenn `featureItem.isPro` (alle CE-Features `isPro: false`) | EE-Projekt-Features, belegt über i18n und Activity-Texte: Time tracking, Milestones (`project_settings.features.{time_tracking,milestones}`), Work item types (`project_settings.work_item_types`), Workflows (`project_settings.workflows`), Project Updates (`project_settings.project_updates`), Epics (`is_epic_enabled`, `apps/web/components/common/activity/helper.tsx` Z. 68) | nein | entfernen; EE-Features als normale Toggles ergänzen |
| U17 | `apps/web/components/estimates/create/stage-one.tsx` Z. 17, 48–55 | `UpgradeBadge` neben gesperrtem Estimate-System; `Tooltip t("common.coming_soon")` bei `!is_available` | Time-Estimates (PF-01) | nein (`time` herausgefiltert) | Time-System freischalten |
| U18 | `apps/web/components/issues/bulk-operations/root.tsx` | Banner „Change state, priority, and more for several work items at once. Save three minutes on an average per operation.“, Button „Upgrade to One“ → `MARKETING_PLANE_ONE_PAGE_LINK` | Bulk Ops (PF-02) | praktisch nein (Auswahl deaktiviert) | echte Bulk-Leiste |
| U19 | `packages/constants/src/state.ts` Z. 114 | `DISPLAY_WORKFLOW_PRO_CTA = false` | Workflows (PF-68) | – | entfällt |
| U20 | `packages/constants/src/endpoints.ts` Z. 31–33 | `MARKETING_PRICING_PAGE_LINK`, `MARKETING_CONTACT_US_PAGE_LINK`, `MARKETING_PLANE_ONE_PAGE_LINK` | – | – | entfällt (ADR-004: keine externen Links nötig) |
| U21 | `packages/constants/src/subscription.ts`, `packages/constants/src/payment.ts`, `packages/utils/src/subscription.ts`, `packages/types/src/payment.ts` | Plan-Feature-Listen, Produkte, Preise, Redirect-URLs | alle | – | entfällt |
| U22 | `apps/web/components/navigation/customize-navigation-dialog.tsx` Z. 92–95 | Kommentare „Filter personal items by feature flags“ / „Filter workspace items by permissions and feature flags“ – im CE ohne Flag-Logik (`filteredPersonalItems = PERSONAL_ITEMS`) | EE-Navigationseinträge; im Repo belegte Kandidaten: Dashboards und Plane AI (`user-menu.tsx`), Wiki (`isWikiPath`), Teamspaces, Initiatives, Customers (Workspace-Feature-Flags `teams`, `initiatives`, `customers`, Developer-Docs `api-reference/workspace-features/overview.md`) | – | Filter auf Workspace-Feature-Toggles (fachlich, ADR-001) |

Upsell-/Billing-Texte in i18n (ohne CE-Referenz, entfallen): `common.upgrade` „Upgrade“, `common.add_seats`, `common.upgrade_cta.higher_subscription`, `common.upgrade_cta.talk_to_sales` (CE-referenziert in `plan-detail.tsx`), `upgrade_request`, `sidebar.upgrade`, `sidebar.upgrade_plan`, `sidebar.plane_pro`, `sidebar.business`, `home.business_trial_banner.*`, `workspace_settings.settings.billing_and_plans.{current_plan,free_plan,view_plans}`, `workspace_settings.settings.cancel_trial.*`, `workspace_settings.settings.general.delete_modal.{description,dismiss,cancel}`, `workspace_analytics.upgrade_to_plan`, `work_item_types.empty_state.{get_pro,upgrade}.*`, `workflows.empty_state.upgrade.*`, `automations.empty_state.upgrade.*`, `templates.empty_state.upgrade.*`, `recurring_work_items.empty_state.upgrade.*`, `wiki.upgrade_flow.*`, `wiki.nested_pages_download_banner.title`, `attachmentComponent.upgrade.description`, `bulk_operations.upgrade_banner.*`, `workspace.members_import.summary.message.seat_limit`, `cloud_maintenance_message.*`.

---

## 6. Inventar der CE-Stubs / Extension-Points

Jede Zeile ist eine Stelle, an der der EE-Code (closed source) andockt. Für die Portierung ist jeweils die **EE-Funktion** zu implementieren (Spalte „Zielverhalten“).

### 6.1 Web-App (`apps/web`)

| # | Datei | CE-Implementierung (wörtlich/sinngemäß) | Zielverhalten (Feature) |
|---|---|---|---|
| S1 | `app/routes/extended.ts` | `extendedRoutes: RouteConfigEntry[] = []` | alle EE-Routen (Epics, Teamspaces, Initiatives, Dashboards, Wiki, Pi-Chat, Customers, Releases, Settings-Seiten) |
| S2 | `app/routes/redirects/extended/index.ts` | `extendedRedirectRoutes = []` | EE-Redirects |
| S3 | `components/epic-modal/modal.tsx` | `CreateUpdateEpicModal` → `<></>` | Epic-Erstellen/Bearbeiten (PF-14) |
| S4 | `components/issues/issue-layouts/empty-states/project-epic.tsx` | `ProjectEpicsEmptyState` → `<></>` | Epic-Leerzustand (PF-14) |
| S5 | `components/workflow/use-workflow-drag-n-drop.ts` | `useWorkFlowFDragNDrop` → `{workflowDisabledSource: undefined, isWorkflowDropDisabled: false, getIsWorkflowWorkItemCreationDisabled: () => false, handleWorkFlowState: () => {}}` | Workflow-Gating bei DnD/Erstellung (PF-68) |
| S6 | `components/issues/issue-type-switcher.tsx` | zeigt nur `IssueIdentifier` | Typ-Wechsler (PF-05) |
| S7 | `components/issues/issue-modal/provider.tsx` | Kontextwerte: `workItemTemplateId: null`, `setWorkItemTemplateId: () => {}`, `isApplyingTemplate: false`, `issuePropertyValues: {}`, `issuePropertyValueErrors: {}`, `getIssueTypeIdOnProjectChange: () => null`, `getActiveAdditionalPropertiesLength: () => 0`, `handlePropertyValuesValidation: () => true`, `handleCreateUpdatePropertyValues/handleProjectEntitiesFetch/handleTemplateChange/handleConvert/handleCreateSubWorkItem: () => Promise.resolve()` | Templates, Typen, Properties, Konvertierung, Sub-Item-Erstellung (PF-05/06/14/25) |
| S8 | `hooks/use-bulk-operation-status.ts` | `() => false` | Bulk Ops (PF-02) |
| S9 | `hooks/use-page-flag.ts` | `{isMovePageEnabled: false, isPageSharingEnabled: false}` | Page-Move/-Sharing (PF-80) |
| S10 | `hooks/use-editor-flagging.ts` | `disabled: ["ai", "collaboration-cursor"]`, `flagged: []` für document/liteText/richText | AI (PF-82), Live-Cursor (PF-70) |
| S11 | `hooks/use-issue-properties.tsx` | `useWorkItemProperties` → `undefined` | Custom-Property-Laden (PF-06) |
| S12 | `hooks/use-workspace-issue-properties-extended.tsx` | `() => {}` | Workspace-Properties (PF-07) |
| S13 | `hooks/use-additional-favorite-item-details.tsx` | nur `default`-Zweig | Favoriten-Icons/-Titel für EE-Entitäten; welche Entitäten EE hier ergänzt, ist im Repo nicht benannt (Kandidaten mit EE-Routenspuren: Epics, Initiatives, Teamspaces, Dashboards, Wiki-Pages) |
| S14 | `hooks/use-additional-editor-mention.tsx` | `updateAdditionalSections → {sections: []}`, `parseAdditionalEditorContent → undefined`, `editorMentionTypes = ["user_mention"]`, Arg `enableAdvancedMentions` | erweiterte Mentions; konkrete Mention-Typen im Repo nicht benannt (Dok. 26: Work-Item-Mentions Business) |
| S15 | `hooks/editor/use-extended-editor-config.ts` | `getExtendedEditorFileHandlers → {}` | Attachment-/Embed-Handler (PF-81) |
| S16 | `hooks/pages/use-extended-editor-extensions.ts` | `useExtendedEditorProps → {}` | EE-Editor-Props für Pages (PF-71/79/81/82) |
| S17 | `hooks/oauth/extended.tsx` | `{isOAuthEnabled: false, oAuthOptions: []}` | SAML/OIDC/LDAP-Login-Buttons (PF-93/97) |
| S18 | `hooks/rich-filters/use-filters-operator-configs.ts` | `allowedOperators = CORE_OPERATORS`, `allowNegative: false` | erweiterte/negierte Operatoren (PF-52) |
| S19 | `components/work-item-filters/filters-row.tsx` | reicht an `FiltersRow` durch | EE-Filterzeile |
| S20 | `components/workspace-notifications/notification-card/content.ts` | `ADDITIONAL_NOTIFICATION_CONTENT_MAP = {}` („CE (empty - EE extends this)“) + Fallback-Renderer | Benachrichtigungstexte für EE-Activity-Felder; im Repo nicht einzeln benannt (Kandidaten aus den Activity-Typen: Work-Item-Typ, Custom Properties `ISSUE_ADDITIONAL_PROPERTIES_ACTIVITY`, Worklogs `WORKLOG`) |
| S21 | `store/pages/extended-base-page.ts` | `ExtendedBasePage.asJSONExtended → {}` | EE-Page-Felder (Collections, Sharing, Nested) |
| S22 | `store/workspace/index.ts` Z. 386–390 | `mutateWorkspaceMembersActivity` „no-op in CE“ | Workspace-Activity (PF-58) |
| S23 | `store/issue/root.store.ts` | Team-/Epic-Stores als Instanzen der Projekt-Klassen (`teamIssues`, `teamViewIssues`, `teamProjectWorkItems`, `projectEpics`, `epicDetail`) | eigene Teamspace/Epic-Stores (PF-14/30) |
| S24 | `store/theme.store.ts` | `initiativesSidebarCollapsed`, `toggleInitiativesSidebar` | Initiative-Seitenleiste (PF-15) |
| S25 | `store/project/project.store.ts` Z. 21, 86 | `ProjectOverviewCollapsible`, `openCollapsibleSection = ["milestones"]` | Projekt-Overview (PF-17/22) |
| S26 | `components/estimates/create/helper.tsx` | `isEstimateSystemEnabled`: nur POINTS/CATEGORIES | Time-Estimates (PF-01) |
| S27 | `components/estimates/inputs/root.tsx` | `case TIME: return <></>` | Time-Eingabe (PF-01) |
| S28 | `components/estimates/estimate-list-item-buttons.tsx` | nur Delete, `onEditClick` ungenutzt | Estimate bearbeiten (PF-01) |
| S29 | `components/relations/index.tsx` | `ISSUE_RELATION_OPTIONS` mit 4 Typen; `useTimeLineRelationOptions = () => ISSUE_RELATION_OPTIONS` | Timeline-Relationen (PF-09/10) |
| S30 | `components/modals/workspace-level.tsx`, `project-level.tsx`, `work-item-level.tsx` | nur CE-Modals (Projekt; Cycle/Module/View/Page; Work-Item-Löschen inkl. Epic-Zweig) | zusätzliche EE-Modals; im Repo nicht einzeln benannt (Kandidaten: Epic-Modal S3, Templates, Initiativen, Teamspaces, Dashboards) |
| S31 | `components/project/settings/features-list.tsx` | `PROJECT_FEATURES_LIST` (cycles, modules, views, pages, intake; alle `isPro: false`) | zusätzliche Projekt-Features (Time tracking, Milestones, Work item types, Epics) |
| S32 | `components/workspace/sidebar/user-menu.tsx` | `SidebarUserMenu` (Home, Dashboards, Your work, Drafts, Pi-Chat) – nicht gerendert | Navigationseinträge Dashboards/Plane AI (PF-45/82) |
| S33 | `components/workspace/sidebar/sidebar-item.tsx` Z. 51–58 | `staticItems` enthält `"pi_chat"` | Plane-AI-Eintrag (PF-82) |
| S34 | `components/integration/*`, `components/project/integration-card.tsx`, `app/(all)/[workspaceSlug]/(settings)/settings/(workspace)/integrations/page.tsx` (ungeroutet), `services/integrations/*` | Legacy-GitHub/Slack-UI gegen nicht existierende Endpunkte | Integrationen (PF-84/86) |
| S35 | `services/cycle.service.ts` Z. 64–78 | `workspaceActiveCycles` → nicht existierender Endpunkt | Active Cycles (PF-04) |
| S36 | `services/issue/issue.service.ts`, `services/issue_filter.service.ts` Z. 39, 50 | `epics`-/`epics-user-properties`-URLs | Epics (PF-14) |
| S37 | `components/projects/create/root.tsx` Z. 33, `components/project/create-project-modal.tsx` Z. 27 | Prop `templateId` ungenutzt | Projekt-Templates (PF-26) |
| S38 | `components/issues/issue-modal/modal.tsx` Z. 33, 51 | Prop `templateId` | Work-Item-Templates (PF-25) |
| S39 | `components/dropdowns/{member,label,project,module,cycle,state,intake-state}/*-select.tsx` | Kommentare „CE change: EE …“ (paginierte „lite“-Ressourcen, Scopes `teamspaceId`, `scopedProjectIds`, Label-Scope work item/release/initiative/project, Workflow-Gating `typeId`/`isForWorkItemCreation`, `useIntakeState()`) | EE-Dropdown-Varianten (PF-15/30/42/68) |
| S40 | `components/workspace/edition-badge.tsx` | „Community“-Button | entfällt (U3) |

### 6.2 Weitere Apps und Pakete

| # | Datei | CE-Implementierung | Zielverhalten |
|---|---|---|---|
| S41 | `apps/admin/components/common/header/extended.ts` | `EXTENDED_HEADER_SEGMENT_LABELS = {}` | Breadcrumb-Labels für EE-God-Mode-Seiten |
| S42 | `apps/admin/providers/extended.tsx` | `ExtendedProviders` → Kinder | EE-Provider (Lizenz/Feature-Flags – entfällt ADR-001) |
| S43 | `apps/space/hooks/oauth/extended.tsx` | `{isOAuthEnabled: false, oAuthOptions: []}` | SSO im Space-Login |
| S44 | `apps/space/components/editor/{rich-text,lite-text}-editor.tsx` | `extendedEditorProps={{}}` | EE-Editor-Props im Space |
| S45 | `apps/live/src/services/page/extended.service.ts` | abstrakte `PageService extends PageCoreService` („Implementation for this is found in the enterprise repository.“) | Workspace-/Teamspace-Page-Services (PF-70/74) |
| S46 | `apps/live/src/types/index.ts` Z. 26; `apps/live/src/services/page/handler.ts` Z. 12–21 | `TDocumentTypes = "project_page"`; sonst `AppError("Invalid document type …")` | zusätzliche Dokumenttypen |
| S47 | `apps/api/plane/utils/instance_config_variables/extended.py` | `extended_config_variables = []` | EE-Instanzkonfiguration; Inhalt im Repo nicht benannt (Kandidaten aus Doku/Helm: SSO, LDAP, Plane AI, Integrationen – Dok. 22) |
| S48 | `packages/editor/src/types/editor-extended.ts` | `IEditorExtensionOptions`, `IEditorPropsExtended`, `ICollaborativeDocumentEditorPropsExtended`, `TExtendedCommandExtraProps`, `TExtendedEditorRefApi` = `unknown`; `TExtendedEditorCommands = never` | EE-Editor-Befehle; belegt über `editor.json` (Attachment, External Embed, AI-Block) und `TExtensions` (`issue-embed`) |
| S49 | `packages/editor/src/extensions/additional-slash-command-options.tsx` | `coreEditorAdditionalSlashCommandOptions → []` | zusätzliche Slash-Befehle |
| S50 | `packages/editor/src/extensions/document-extensions.tsx` | Registry nur `SlashCommands` | belegte Kandidaten: Work-Item-Embed (`WorkItemEmbedExtension`), Collaboration-Cursor (`TExtensions` `collaboration-cursor`), AI (`TExtensions` `ai`) |
| S51 | `packages/types/src/page/extended.ts` | `TPageExtended = object` | EE-Page-Felder |
| S52 | `packages/types/src/instance/auth-ee.ts` | `TExtendedLoginMediums = never`, `TExtendedInstanceAuthenticationModeKeys = never` | SAML/OIDC/LDAP |
| S53 | `packages/constants/src/auth/extended.ts` | `EXTENDED_LOGIN_MEDIUM_LABELS = {}` | Labels der EE-Login-Medien |
| S54 | `packages/types/src/base-layouts/gantt/extended.ts` | `EXTENDED_GANTT_TIMELINE_TYPE = {}` | zusätzliche Timeline-Typen (z. B. Initiativen/Teamspaces) |
| S55 | `packages/types/src/rich-filters/{operators,field-types,operator-configs,derived}/extended.ts`, `packages/constants/src/rich-filters/operator-labels/extended.ts` | leere Operatoren/Typen/Labels | PQL/erweiterte Filter (PF-52) |
| S56 | `packages/types/src/issues/issue-property-values.ts` | `Record<string, unknown>` | Property-Wert-Typen (PF-06) |
| S57 | `packages/blocks/src/context-menu/context-menu-item.tsx` Z. 8–11 | „CE deviation from EE: EE routes `description` into the leaf row's `trailing` slot“ | UI-Detail: Beschreibung im Trailing-Slot (1:1-Abgleich) |

### 6.3 Im Verifikationslauf ergänzte Stubs / Extension-Points

Ermittelt per `find apps packages -iname '*extended*'`, Suche nach ungenutzten `_props`-Parametern und `return { items: [], modals: null }`-Mustern sowie Abgleich der Frontend-Service-URLs mit `apps/api/plane/**/urls*.py`.

| # | Datei | CE-Implementierung | Zielverhalten (Feature) |
|---|---|---|---|
| S58 | `apps/web/hooks/pages/use-pages-pane-extensions.ts` | `editorExtensionHandlers` = leere `Map`, `navigationPaneExtensions: INavigationPaneExtension[] = []`; Schnittstelle `INavigationPaneExtension {id, triggerParam, component, data?, width?}` (`apps/web/components/pages/navigation-pane/types/extensions.ts`), durchgereicht an `PageNavigationPaneRoot` (`apps/web/components/pages/editor/page-root.tsx` Z. 103, 204) | zusätzliche Page-Navigation-Pane-Panels und Editor-Handler (Page-Kommentare PF-79, Plane AI PF-82) |
| S59 | `apps/web/components/common/quick-actions-helper.tsx` | `MenuResult = {items, modals}` mit `modals: null` in `useViewMenuItems`, `useLayoutMenuItems` (Z. 118–146); `useIntakeHeaderMenuItems` → `{items: [], modals: null}` (Z. 149–153, im CE nicht eingebunden); Aufrufer behandeln „CE (array) and EE (object) return types“ (`apps/web/components/modules/quick-actions.tsx` Z. 90–107, `apps/web/components/views/quick-actions.tsx` Z. 84) | zusätzliche EE-Menüeinträge samt Modals für Cycle/Modul/View/Layout/Intake-Header; konkrete Einträge im Repo nicht benannt |
| S60 | `packages/editor/src/components/document-editor-side-effects.ts` | `DocumentEditorSideEffects(_props) → null`; Props `editor`, `id`, `updatePageProperties?`, `extendedEditorProps?` (im CE nicht eingebunden) | EE-Seiteneffekte des Dokument-Editors (Page-Properties-Updates) |
| S61 | `apps/web/components/common/modal/global.tsx` | `GlobalModals` rendert nur `ProfileSettingsModal`; eingebunden in `apps/web/app/(all)/[workspaceSlug]/layout.tsx` Z. 11 | workspaceweite EE-Modals (vgl. S30) |
| S62 | `apps/web/components/rich-filters/filter-value-input/root.tsx` | `AdditionalFilterValueInput` → Fallback „Filter type not supported“ für alle Feldtypen außer `SINGLE_SELECT`, `MULTI_SELECT`, `DATE`, `DATE_RANGE` | Werteingaben für EE-Filterfeldtypen (Custom Properties PF-06, PQL PF-52) |
| S63 | `apps/web/store/timeline/base-timeline.store.ts` Z. 85 | `isDependencyEnabled = false` (Interface in `issues-timeline.store.ts` Z. 13, `modules-timeline.store.ts` Z. 13) | Abhängigkeitslinien im Gantt (PF-09) |
| S64 | `apps/web/hooks/use-debounced-duplicate-issues.tsx` | `useDebouncedDuplicateIssues(...)` → `{duplicateIssues: []}` | Duplicate Detection (PF-104) |
| S65 | `apps/web/components/issues/issue-layouts/quick-action-dropdowns/copy-menu-helper.tsx` | `createCopyMenuWithDuplication(props)` → `props.baseItem` | „Make a copy to another project“ (PF-38) |
| S66 | `apps/web/components/common/activity/helper.tsx` Z. 67–71, 266–285 | Activity-Icons und -Texte für Projekt-Felder `is_project_updates_enabled` („project updates“), `is_epic_enabled` („epics“), `is_workflow_enabled` („custom workflow“), die im CE-Modell `Project` nicht existieren | Projekt-Feature-Toggles Project Updates (PF-23), Epics (PF-14), Workflows (PF-68) |

---

## 7. Inventar der i18n-Namespaces/-Schlüssel mit EE-Texten

Alle 28 Namespaces sind in `packages/i18n/src/constants/namespaces.ts` registriert und in allen 22 Locales vorhanden (`packages/i18n/src/locales/{bg,cs,de,en,es,fr,id,it,ja,ka-ge,ko,nl,pl,pt-BR,ro,ru,sk,tr-TR,ua,vi-VN,zh-CN,zh-TW}/`). **Die EE-Texte liegen damit bereits übersetzt (inkl. Deutsch) im CE-Repo vor** und sind für die Angular-i18n 1:1 zu übernehmen (Skill `translate` / Regeln in `packages/i18n`).

Methode siehe 1.3 (Q5). „Ohne CE-Ref.“ = Anzahl Blatt-Schlüssel ohne Referenz im CE-Code (Heuristik, enthält bei Nicht-EE-Namespaces auch dynamisch zusammengesetzte CE-Schlüssel). „EE-relevant“ = davon inhaltlich geprüfte EE-Schlüssel (vollständig in Anhang A).

| Namespace-Datei | Schlüssel gesamt | Ohne CE-Ref. | EE-relevant | EE-Inhalte (Feature) |
|---|---|---|---|---|
| `accessibility.json` | 33 | 9 | 0 | (nur CE-Sidebar-ARIA; `edition_badge` „Open paid plans' modal“ ist CE-referenziert → U3) |
| `auth.json` | 186 | 145 | 117 | `sso.*` Identity/Domains/SAML/OIDC (PF-93), `auth.ldap.*` (PF-97); übrige 28 = dynamische CE-Schlüssel |
| `automation.json` | 141 | 141 | 141 | Custom/Global Automations (PF-63/64/65) |
| `common.json` | 766 | 243 | 40 | Worklogs, Workflows, Templates, Teamspaces, Recurring, Milestones, Custom properties, Updates-Status, Upgrade/Seats, Chart-Labels, Active-Cycles-Kacheltexte |
| `cycle.json` | 11 | 4 | 4 | `active_cycle_analytics.empty_state.*` (PF-04) |
| `editor.json` | 29 | 29 | 29 | Attachment-Block, External Embed, AI-Block (PF-81/82) |
| `empty-state.json` | 142 | 73 | 48 | Epics, Dashboards, Wiki, Project States, Active Cycles, Work Item Types/Properties, Templates, Recurring, Worklogs, Group Sync, Workflows, Progress, Updates, Workspace-Tokens |
| `home.json` | 43 | 8 | 6 | Business-Trial-Banner (PF-103) |
| `inbox.json` | 43 | 16 | 0 | (CE-Status-/Leerzustandsschlüssel, dynamisch) |
| `integration.json` | 291 | 290 | 290 | GitHub, GitHub Enterprise, GitLab, GitLab Enterprise, Slack, Sentry, Bitbucket DC, OAuth Bridge, Silo-Fehler, Import-Status (PF-83–91) |
| `module.json` | 3 | 2 | 0 | – |
| `navigation.json` | 24 | 9 | 5 | `sidebar.upgrade`, `sidebar.epics`, `sidebar.upgrade_plan`, `sidebar.plane_pro`, `sidebar.business` |
| `notification.json` | 36 | 5 | 0 | – |
| `page.json` | 56 | 36 | 22 | Version-Highlight, Page-Kommentare, Move/Collections (PF-74/76/79/80) |
| `power-k.json` | 151 | 7 | 5 | New automation, Workspace Active Cycle, Project Overview, Advanced search, Chat with us |
| `project-settings.json` | 288 | 190 | 165 | Estimates edit/switch (PF-01), Auto-Reminder (PF-67), Workflows (PF-68), Work Item Types (PF-05), Intake sources/forms/email/assignees (PF-34/36/37), Time tracking (PF-03), Milestones (PF-17), Project Updates (PF-23), Templates (PF-26), Cycle Auto-Schedule (PF-12/13), Integrations-Leerzustand |
| `project.json` | 200 | 107 | 35 | Mitglieder-CSV-Import (PF-60), Active-Cycle-Chart-Legende (PF-46), Public/Shared Views (PF-43/44) |
| `settings.json` | 78 | 20 | 6 | Profil „Connections“ (PF-86), „Activity“ (PF-58) |
| `stickies.json` | 29 | 6 | 0 | – |
| `template.json` | 137 | 137 | 137 | Projekt-/Work-Item-/Page-Templates, Marketplace (PF-25–28) |
| `tour.json` | 89 | 89 | 89 | Product Tour / Get started (PF-102) |
| `update.json` | 29 | 29 | 29 | Updates (PF-23) |
| `wiki.json` | 73 | 73 | 73 | Wiki-Collections, Upgrade-Flow (PF-74/78) |
| `work-item-type.json` | 207 | 207 | 207 | Work Item Types, Properties, Hierarchie (PF-05–08) |
| `work-item.json` | 198 | 87 | 76 | Replies (PF-39), Timeline-/Implements-Relationen (PF-09/10), Duplicate (PF-38), Linked Pages (PF-72), Votes (PF-40), Recurring (PF-29), Bulk-Fehler (PF-02), Display-Property `issue_type` |
| `workflow.json` | 40 | 40 | 40 | Workflows (PF-68) |
| `workspace-settings.json` | 352 | 268 | 245 | Billing, Integrations, Imports, Worklogs, Group Sync, Identity, Project States/Projects, Templates, Relations, Cancel Trial, Applications, Plane AI, Runner, Delete-Trial-Modal, Workspace-Access-Tokens |
| `workspace.json` | 184 | 107 | 66 | Erweiterte Analytics (PF-50), Mitglieder-CSV-Import (PF-60), Active-Cycles-Leerzustand |
| **Summe** | **3 859** | **2 377** | **1 875** | |

Hinweis zu fehlenden EE-Texten: Für **Customers**, **Initiatives**, **Teamspaces**, **Dashboards** (außer Paletten-Keys), **Releases**, **Milestones** (außer Projekt-Toggle), **Pi-Chat-Oberfläche** existieren im CE-i18n **keine** eigenen Namespaces; die i18n-Keys `dashboards.widget.color_palettes.{modern,horizon,earthen}` werden in `packages/constants/src/chart.ts` referenziert, fehlen aber in allen Locales (OP-05).

---

## 8. EE-Typen, -Enums und -Konstanten in `packages/*`

### 8.1 `packages/types`

| Typ/Enum | Wert(e) mit EE-Bezug | Datei | Feature |
|---|---|---|---|
| `EProductSubscriptionEnum`, `TProductSubscriptionType`, `TBillingFrequency`, `IPaymentProduct`, `IPaymentProductPrice`, `TSubscriptionPrice`, `TProductBillingFrequency` | Planstufen/Preise | `src/payment.ts` | PF-103 (entfällt) |
| `EIssuesStoreType` | `TEAM`, `TEAM_VIEW`, `EPIC`, `TEAM_PROJECT_WORK_ITEMS` | `src/issues/issue.ts` Z. 29–43 | PF-14/30 |
| `EIssueServiceType` | `EPICS = "epics"`, `WORK_ITEMS = "work-items"` | `src/issues/issue.ts` Z. 23–27 | PF-14 |
| `TBaseIssue` | `type_id`, `is_epic?`, `is_intake?` | `src/issues/issue.ts` Z. 65, 78–79 | PF-05/14 |
| `TIssueRelationTypes` | nur `blocking`, `blocked_by`, `duplicate`, `relates_to` (EE: + `start_before`, `start_after`, `finish_before`, `finish_after`, `implements`, `implemented_by`) | `src/issues/issue_relation.ts` Z. 17 | PF-09/10 |
| `TIssuePropertyValues`, `TIssuePropertyValueErrors` | `Record<string, unknown>` | `src/issues/issue-property-values.ts` | PF-06 |
| `TIssueIdentifierWithDetails.issueTypeId`, `TIssueTypeIdentifier` | Typ-Icon am Identifier | `src/issues/issue-identifier.ts` | PF-05 |
| `IIssueActivity`-Union | `activity_type: "WORKLOG"`, `"ISSUE_ADDITIONAL_PROPERTIES_ACTIVITY"` | `src/issues/activity/base.ts` Z. 80–88 | PF-03/06 |
| `IIssueDisplayProperties.issue_type` | Display-Property | `src/view-props.ts` Z. 177 | PF-05 |
| `TIssueGroupByOptions` | `"team_project"` | `src/view-props.ts` Z. 25 | PF-30 |
| `EFileAssetType` | `TEAM_SPACE_DESCRIPTION`, `INITIATIVE_DESCRIPTION`, `PROJECT_DESCRIPTION`, `TEAM_SPACE_COMMENT_DESCRIPTION` (alle auch in `TEditorAssetType`) | `src/enums.ts` Z. 61–85 | PF-15/22/30 |
| `EUpdateStatus` | `OFF-TRACK`, `ON-TRACK`, `AT-RISK` | `src/enums.ts` Z. 87–91 | PF-23 |
| `EInboxIssueSource` | `IN_APP`, `FORMS`, `EMAIL` | `src/inbox.ts` Z. 27–31 | PF-36/37 |
| `IIntakeState`, `TIntakeStateGroups = "triage"` | separate Intake-States | `src/intake/state.ts` | Intake (EE `useIntakeState()`) |
| `TEpicAnalyticsGroup`, `TEpicAnalytics` | Epic-Fortschritt | `src/epics.ts` | PF-14 |
| `ChartYAxisMetric.EPIC_WORK_ITEM_COUNT` | Analytics | `src/analytics.ts` Z. 37 | PF-14/50 |
| `TAnalyticsTabsBase`, `TAnalyticsGraphsBase`, `AnalyticsTab.isDisabled` | `overview`, `work-items`; `custom-work-items` | `src/analytics.ts` Z. 40–47 | PF-50 |
| `EGanttBlockType.EPIC`, `PROJECT` | Gantt-Blöcke | `src/layout/gantt.ts` | PF-14 |
| `EXTENDED_GANTT_TIMELINE_TYPE` | `{}` | `src/base-layouts/gantt/extended.ts` | Timeline-Typen |
| `TProjectIssuesSearchParams.epic?`, `ISearchIssueResponse.type_id` | Suche | `src/project/projects.ts` Z. 158, 173 | PF-05/14 |
| `IWorkspaceActiveCyclesResponse` | Pagination | `src/workspace.ts` Z. 219–228 | PF-04 |
| `TPageExtended = object` | Page-Erweiterung | `src/page/extended.ts` | PF-74/78/80 |
| `TExtendedLoginMediums`, `TExtendedInstanceAuthenticationModeKeys` | `never` | `src/instance/auth-ee.ts` | PF-93/97 |
| Integration-Typen `enterprise`, `is_enterprise_install` | GitHub-Enterprise-Installation | `src/integration.ts` Z. 69, 80 | PF-84 |
| Rich-Filter-Erweiterungen | `EXTENDED_*`-Operatoren, `TExtended*` = `never` | `src/rich-filters/{operators,field-types,operator-configs,derived}/extended.ts` | PF-52 |
| `TWidgetIssue.issue_relation[].type_id` | Home-Widgets | `src/dashboard.ts` | PF-05 |
| `TDuplicateIssuePayload`, `TDeDupeIssue`, `TDuplicateIssueResponse` (Verifikation) | Duplikat-Suche | `src/de-dupe.ts` | PF-104 |
| `TBulkIssueProperties`, `TBulkOperationsPayload` (Verifikation) | Bulk-Property-Update (`state_id`, `priority`, `label_ids`, `assignee_ids`, `start_date`, `target_date`, `module_ids`, `cycle_id`, `estimate_point`) | `src/issues/issue.ts` Z. 140–156 | PF-02 |
| `TProgressSnapshot` als Rückgabe von `workspaceActiveCyclesProgressPro` (Verifikation) | Cycle-Fortschritt „Pro“ | `apps/web/services/cycle.service.ts` Z. 52–62 | PF-04/PF-46 |

### 8.2 `packages/constants`

| Konstante | Inhalt | Datei | Feature |
|---|---|---|---|
| `ESTIMATE_SYSTEMS.time` (`is_ee: true`), `EEstimateSystem.TIME`, `EEstimateUpdateStages.{EDIT,SWITCH}` | Time-Estimates, Edit/Switch | `src/estimates.ts` | PF-01 |
| `RESTRICTED_URLS` | vollständig (65 Einträge, 62 verschieden; Duplikate `monitor`, `config` je 2×, `mobile` 3×), Reihenfolge wie im Original: `404`, `accounts`, `api`, `create-workspace`, `god-mode`, `installations`, `invitations`, `onboarding`, `profile`, `spaces`, `workspace-invitations`, `password`, `flags`, `monitor`, `monitoring`, `ingest`, `plane-pro`, `plane-ultimate`, `enterprise`, `plane-enterprise`, `disco`, `silo`, `chat`, `calendar`, `drive`, `channels`, `upgrade`, `billing`, `sign-in`, `sign-up`, `signin`, `signup`, `config`, `live`, `admin`, `m`, `import`, `importers`, `integrations`, `integration`, `configuration`, `initiatives`, `initiative`, `config`, `workflow`, `workflows`, `epics`, `epic`, `story`, `mobile`, `dashboard`, `desktop`, `onload`, `real-time`, `one`, `pages`, `mobile`, `business`, `pro`, `settings`, `monitor`, `license`, `licenses`, `instances`, `instance`. EE-/Commercial-Bezug: `flags`, `monitor`, `monitoring`, `ingest`, `plane-pro`, `plane-ultimate`, `enterprise`, `plane-enterprise`, `disco`, `silo`, `chat`, `calendar`, `drive`, `channels`, `upgrade`, `billing`, `importers`, `integrations`, `initiatives`, `initiative`, `workflow`, `workflows`, `epics`, `epic`, `story`, `dashboard`, `desktop`, `real-time`, `one`, `business`, `pro`, `license`, `licenses` | `src/workspace.ts` Z. 12–78 (identisch `apps/api/plane/utils/constants.py` `RESTRICTED_WORKSPACE_SLUGS`) | Hinweis auf EE-Pfade/-Produkte (Chat, Calendar, Drive, Channels) |
| `WORKSPACE_SIDEBAR_DYNAMIC_NAVIGATION_ITEMS` | nur `views`, `analytics`, `archives` | `src/workspace.ts` | EE ergänzt Einträge |
| `IMPORTERS_LIST` | `github`, `jira` | `src/workspace.ts` | PF-83 |
| `EXPORTERS_LIST` | `csv`, `xlsx`, `json` | `src/workspace.ts` | CE |
| `CHART_COLOR_PALETTES`, `EChartModels` | Dashboard-Widget-Paletten/-Modelle | `src/chart.ts` Z. 32–135 | PF-45 |
| `ANALYTICS_Y_AXIS_VALUES` inkl. `EPIC_WORK_ITEM_COUNT` | Analytics | `src/analytics/common.ts` Z. 185–186 | PF-14/50 |
| `EIssuesStoreType.EPIC` in Store-Typ-Union, `team_project = "project_id"` | Gruppierung | `src/issue/common.ts` Z. 39, 110 | PF-14/30 |
| Fetch-Keys `WORKSPACE_WORKFLOW_STATES`, `PROJECT_WORKFLOWS`, `EPICS_PROPERTIES_AND_OPTIONS`, `PROJECT_MILESTONES` | SWR-Keys | `src/fetch-keys.ts` Z. 71–72, 196–206 | PF-68/14/17 |
| `DISPLAY_WORKFLOW_PRO_CTA = false` | Upsell-Schalter | `src/state.ts` Z. 114 | PF-68 |
| `AI_EDITOR_TASKS.ASK_ANYTHING`, `LOADING_TEXTS` „Pi is generating response“ | AI | `src/ai.ts` | PF-82 |
| `EXTENDED_LOGIN_MEDIUM_LABELS` | `{}` | `src/auth/extended.ts` | PF-93/97 |
| `EXTENDED_OPERATOR_LABELS_MAP`, `EXTENDED_DATE_OPERATOR_LABELS_MAP`, `NEGATED_OPERATOR_LABELS_MAP`, `NEGATED_DATE_OPERATOR_LABELS_MAP` | je `{}` | `src/rich-filters/operator-labels/extended.ts` | PF-52 |
| `ENTERPRISE_/BUSINESS_/PRO_/ONE_PLAN_FEATURES`, `FREE_PLAN_UPGRADE_FEATURES` | Plan-Listen | `src/subscription.ts` | 2.16 |
| Payment-/Marketing-Konstanten | siehe 2.17 | `src/payment.ts`, `src/endpoints.ts` | entfällt |

### 8.3 `packages/editor`, `packages/blocks`, `packages/utils`

| Element | Inhalt | Datei | Feature |
|---|---|---|---|
| `TExtensions` | `"ai" \| "collaboration-cursor" \| "issue-embed" \| "slash-commands" \| "enter-key" \| "image"` | `packages/editor/src/types/extensions.ts` Z. 7 | PF-70/71/82 |
| `TAIMenuProps`, `TAIHandler` | AI-Menü | `packages/editor/src/types/ai.ts` | PF-82 |
| `TEmbedItem` | Embed-Suchergebnis | `packages/editor/src/types/embed.ts` | PF-71 |
| Extended-Editor-Typen | `unknown`/`never` | `packages/editor/src/types/editor-extended.ts` | PF-81 |
| `CommonRealtimeFields.teamspace_id`, `affectedPages.{parentPage,descendantPages}` | Realtime-Events | `packages/editor/src/types/document-collaborative-events.ts` | PF-30/78 |
| `DocumentCollaborativeEvents` | vollständig: `lock`, `unlock`, `archive`, `unarchive`, `make-public`, `make-private`, `delete`, `move`, `duplicate`, `property_update`, `restore`, `error` (Payload `MovedPayload {new_project_id, new_page_id}`, `RestoredPayload {deleted_page_ids?}`, `ErrorPayload {error_message, error_type: "fetch" \| "store", error_code?: "content_too_large" \| "page_locked" \| "page_archived", should_disconnect?}`) | `packages/editor/src/constants/document-collaborative-events.ts` | PF-80 (Move) |
| Empty-State-Asset-Typen (horizontal) | `customer`, `custom-properties`, `epic`, `group-syncing`, `script`, `template`, `update`, `worklog`, `runner-functions`, `runner-scripts`, `workflow`, `ai-skills`, `ai-agents`, `memory` (+ CE-Typen) | `packages/blocks/src/empty-state/assets/asset-types.ts` | diverse |
| Empty-State-Asset-Typen (vertikal) | `customer`, `dashboard`, `epic`, `initiative`, `milestone`, `property`, `teamspace`, `workflow` (+ CE-Typen) | dito | diverse |
| `PiChatLogo` | Logo | `packages/blocks/src/icons/sub-brand/pi-chat.tsx` | PF-82 |
| `generateWorkItemLink` (Epic-Link = Work-Item-Link `/{ws}/browse/{IDENT}-{SEQ}/`) | Parameter `isEpic` | `packages/utils/src/work-item/base.ts` Z. 315–337 | PF-14 |
| Subscription-Utils | siehe 2.17 | `packages/utils/src/subscription.ts` | entfällt |

### 8.4 Icons aus `@makeplane/propel` 0.7.3 mit EE-Bezug (UI 1:1)

Quelle: `…/scratchpad/propel-pkg/package/dist/icons/<kategorie>/<name>.d.ts` (nur gelesen). Export-Namen = PascalCase des Dateinamens (z. B. `epic-outline` → `EpicOutline`).

| Kategorie | EE-relevante Icons (vollständig für EE-Features) |
|---|---|
| `workspace-features` | `briefs-*`, `customers-*`, `dashboards-*`, `initiative-*`, `new-chat-*`, `releases-*`, `teamspaces-*`, `templates-*`, `time-tracking-*`, `workgraph-*` (jeweils `-filled`/`-outline`) |
| `project-features` | `epic-*`, `milestone-outline`, `milestones-filled`, `overview-*`, `scripts-*`, `workflows-*` |
| `initiative-states` | `initiative-cancelled`, `initiative-completed`, `initiative-draft`, `initiative-in-progress`, `initiative-planned` |
| `milestone-states` | `milestone-done`, `milestone-in-progress`, `milestone-not-started` |
| `actions` | `add-time-tracking-*`, `ai-filter-*`, `ai-summary-*`, `ask-*`, `auto-reminder-*`, `catchup-*`, `convert-to-epic-*`, `convert-to-work-item-*`, `copy-as-prompt-*`, `move-page-*` |
| `miscellaneous` | `access-and-roles-*`, `agent-*`, `agent-alt-*`, `ai-star-*` (1–4/one–four), `approver-*`, `audit-logs-*`, `automations-*`, `autopilot-go-*`, `billings-*`, `dependency-*`, `excerpt-*`, `function-*`, `group-sync-*`, `hierarchy-*`, `insert-excerpt-*`, `integrations-*`, `imports-*`, `library-*`, `library-alt-*`, `link-page-*`, `memory-*`, `migrate-*`, `pii-scanner-*`, `recurring-work-items-*`, `release-tag-*`, `rules-*`, `sandbox-*`, `time-entries-*`, `transfer-work-item-*`, `transfer-work-item-alt-*`, `trigger-*`, `upgrade-*`, `upgrade-alt-filled`, `usage-*`, `variable-*`, `widget-*` |
| `properties` | `boolean-outline`, `dropdown-*`, `hash-*`, `implemented-by-*`, `implements-*`, `multi-tag-*`, `properties-*`, `scope-*`, `time-in-state-*`, `toggle-*` |
| `formatting-and-editors` | `embed-*`, `formula-*`, `inline-equation-*`, `pen-tool-*`, `presentation-*`, `translate-*` |
| `sub-brands` | `bridge`, `desk`, `plane-ai`, `plane-ai-alt`, `plane-ai-two`, `projects`, `wiki`, `work` |
| `other-products` | `asana`, `bitbucket`, `chatgpt`, `claude`, `clickup`, `codex`, `copilot`, `cursor`, `deepseek`, `discord`, `docker`, `dribbble`, `evermuse`, `facebook`, `figma`, `github`, `gitlab`, `glm-z-ai`, `gmail`, `granola`, `instagram`, `intercom`, `jira`, `kimi`, `kubernetes`, `linear`, `linkedin`, `monday`, `ms-excel`, `ms-powerpoint`, `ms-word`, `oidc`, `posthog`, `postman`, `raycast`, `saml`, `sentry`, `slack`, `x`, `youtube` |

Hinweis: Icons wie `pii-scanner`, `workgraph`, `briefs`, `library`, `excerpt`, `sub-brands/desk` und `sub-brands/bridge` weisen auf weitere Commercial-Produkte/-Features hin, für die im CE **keinerlei** sonstige Spuren existieren (OP-09).

---

## 9. Backend-Spuren (`apps/api`)

### 9.1 Models/Felder ohne vollständige CE-Funktion

| Model.Feld | Definition | Datei | Feature |
|---|---|---|---|
| `Instance.edition` | Default `PLANE_COMMUNITY` | `plane/license/models/instance.py` Z. 29 | 1.1 |
| `IssueType` (komplett) | `workspace`, `name`, `description`, `logo_props`, `is_epic`, `is_default`, `is_active`, `level`, `external_source`, `external_id` | `plane/db/models/issue_type.py` Z. 14–32 | PF-05/08/14 |
| `ProjectIssueType` (komplett) | `project`, `issue_type`, `level`, `is_default`; Unique bei `deleted_at IS NULL` | `plane/db/models/issue_type.py` Z. 35–55 | PF-05 |
| `Issue.type` | FK `IssueType`, `SET_NULL` | `plane/db/models/issue.py` Z. 164–170 | PF-05 |
| `DraftIssue.type` | FK `IssueType` | `plane/db/models/draft.py` Z. 70–74 | PF-05 |
| `Project.is_issue_type_enabled` | Bool, `False` | `plane/db/models/project.py` Z. 101 | PF-05 |
| `Project.is_time_tracking_enabled` | Bool, `False` | `plane/db/models/project.py` Z. 100 | PF-03 |
| `Project.NETWORK_CHOICES` | `(0,"Secret"),(2,"Public")` | `plane/db/models/project.py` Z. 71 | PF-20 |
| `Project.default_assignee` | FK User | `plane/db/models/project.py` Z. 79 | PF-34 |
| `IssueRelationChoices` | `START_BEFORE`, `FINISH_BEFORE`, `IMPLEMENTED_BY` + Reverse-Mapping | `plane/db/models/issue.py` Z. 272–293 | PF-09/10 |
| `IssueComment.parent` | FK self | `plane/db/models/issue.py` Z. 475–476 | PF-39 |
| `IssueVote` | Votes | `plane/db/models/issue.py` Z. 654 | PF-40 |
| `IntakeIssue.source`, `source_email`, `extra` | Default `IN_APP` | `plane/db/models/intake.py` Z. 76–80 | PF-36/37 |
| `DeployBoard.TYPE_CHOICES` | `project`, `issue`, `module`, `cycle`, `page`, `view`, `intake` | `plane/db/models/deploy_board.py` Z. 20–28 | PF-36/44/73 |
| `Page.parent`, `is_global`, `moved_to_page`, `moved_to_project` | Nested/Wiki/Move | `plane/db/models/page.py` Z. 40–55 | PF-74/78/80 |
| `PageVersion.sub_pages_data` | JSON | `plane/db/models/page.py` Z. 167 | PF-76/78 |
| `Cycle.progress_snapshot` | JSON | `plane/db/models/cycle.py` Z. 74 | PF-47 |
| `ExporterHistory.type = "issue_worklogs"` | Choice | `plane/db/models/exporter.py` Z. 31 | PF-03 |
| `Integration`, `WorkspaceIntegration`, `GithubRepository`, `GithubRepositorySync`, `GithubIssueSync`, `GithubCommentSync`, `SlackProjectSync` | Legacy-Integrationen (ohne URLs) | `plane/db/models/integration/{base,github,slack}.py` | PF-84/86 |
| `Importer` | Legacy-Importer | `plane/db/models/importer.py` | PF-83 |
| `Team` | Legacy (`name`, `description`, `workspace`, `logo_props`) | `plane/db/models/workspace.py` Z. 261–284 | PF-30 |
| `WorkspaceUserPreference.UserPreferenceKeys.ACTIVE_CYCLES` (Verifikation) | Choice `("active_cycles", "Active Cycles")` neben `views`, `analytics`, `drafts`, `your_work`, `archives`, `stickies` – Navigationspräferenz für die im CE nicht verfügbare Workspace-Active-Cycles-Seite | `plane/db/models/workspace.py` Z. 417–427 | PF-04 |

### 9.2 Logik-Spuren

| Stelle | Inhalt | Datei | Feature |
|---|---|---|---|
| PQL-Ablehnung | 400 bei `pql`/`filters` | `plane/api/views/issue.py` Z. 324–335 | PF-52 |
| Default-Typ beim Anlegen | `IssueType.objects.filter(project_issue_types__project_id=…, is_default=True).first()` | `plane/api/serializers/issue.py` Z. 190–197 | PF-05 |
| Archiv ohne Epics | `Q(type__isnull=True) \| Q(type__is_epic=False)` | `plane/app/views/issue/archive.py` Z. 99 | PF-14 |
| `RelatedIssueSerializer` | `type_id`, `is_epic` | `plane/api/serializers/issue.py` Z. 655–683 | PF-05/14 |
| Öffentlicher Projekt-Serializer | `is_time_tracking_enabled`, `is_issue_type_enabled` | `plane/api/serializers/project.py` Z. 93–94 | PF-03/05 |
| Versionslimit | 20 Versionen/Page | `plane/bgtasks/page_version_task.py` Z. 72–74; `plane/bgtasks/cleanup_task.py` Z. 107–124 | PF-76 |
| Seed-Display-Properties | `issue_type`, `customer_count`, `customer_request_count` | `plane/bgtasks/workspace_seed_task.py` Z. 145–164; `plane/seeds/data/views.json` Z. 10 | PF-05/41 |
| Seed-Page-Text | „Each project in Plane can have its own Wiki space…“ | `plane/seeds/data/pages.json` Z. 6–8 | PF-74 |
| Reservierte Slugs | `RESTRICTED_WORKSPACE_SLUGS` (siehe 8.2) | `plane/utils/constants.py` | – |
| Silo-Hinweis | `WEBHOOK_ALLOWED_HOSTS`-Beispiel `"silo,silo.namespace.svc.cluster.local,internal-api.lan"` | `plane/settings/common.py` Z. 75; `plane/utils/ip_address.py` Z. 175 | PF-83–88 |
| Erweiterte Instanz-Config | `extended_config_variables = []` | `plane/utils/instance_config_variables/extended.py` | S47 |

### 9.3 Vom CE-Frontend aufgerufene, im CE-Backend **nicht** vorhandene Endpunkte

| Endpunkt | Aufrufer | Feature |
|---|---|---|
| `GET /api/workspaces/{slug}/active-cycles/` | `apps/web/services/cycle.service.ts` Z. 69; `packages/services/src/cycle/cycle.service.ts` Z. 34 | PF-04 |
| `POST/GET/PATCH/DELETE /api/workspaces/{slug}/projects/{pid}/epics/…`, `…/epics-detail/`, `…/v2/epics/` | `apps/web/services/issue/issue.service.ts` (mit `EIssueServiceType.EPICS`) | PF-14 |
| `GET/PATCH /api/workspaces/{slug}/projects/{pid}/epics-user-properties/` | `apps/web/services/issue_filter.service.ts` Z. 39, 50 | PF-14 |
| `GET /api/integrations/`, `GET/DELETE /api/workspaces/{slug}/workspace-integrations/…` | `apps/web/services/integrations/integration.service.ts` Z. 18–30 | PF-84/86 |
| `/api/workspaces/{slug}/dashboard/…`, `/api/dashboard/{id}/widgets/{widgetId}/` | `apps/web/services/dashboard.service.ts`, `packages/services/src/dashboard/dashboard.service.ts` (veraltetes Home-Dashboard; nur `users/me/workspaces/<slug>/dashboard/` existiert) | (kein Bezahl-Feature) |
| (6, Verifikation) `POST /api/workspaces/{slug}/projects/{pid}/bulk-operation-issues/` (Body `TBulkOperationsPayload`) | `apps/web/services/issue/issue.service.ts` Z. 339–345; Store `bulkUpdateProperties` (`apps/web/store/issue/helpers/base-issues.store.ts` Z. 718–753) | PF-02 |
| (7, Verifikation) `POST /api/workspaces/{slug}/projects/{pid}/pages/{pageId}/move/` (Body `{new_project_id}`) | `apps/web/services/page/project-page.service.ts` Z. 185–193; Store `movePage` (`apps/web/store/pages/project-page.store.ts` Z. 352–369) | PF-80 |
| (8, Verifikation) `GET /api/workspaces/{slug}/projects/{pid}/cycles/{cycleId}/cycle-progress/` → `TProgressSnapshot` | `workspaceActiveCyclesProgressPro` in `apps/web/services/cycle.service.ts` Z. 52–62 und `packages/services/src/cycle/cycle-analytics.service.ts` Z. 73–78, im CE ohne Aufrufer (die CE-Variante `workspaceActiveCyclesProgress`, aufgerufen in `apps/web/store/cycle.store.ts` Z. 487, nutzt das vorhandene `…/cycles/{cycleId}/progress/`) | PF-04/PF-46 |
| (9, Verifikation) `POST /api/workspaces/{slug}/rephrase-grammar/` → `{response}` | `performEditorTask` in `apps/web/services/ai.service.ts` Z. 37–48, `packages/services/src/ai/ai.service.ts` Z. 68; Aufrufer `apps/web/components/pages/editor/ai/menu.tsx` Z. 82 | PF-82 |
| (10, Verifikation) Legacy-Importer und -Integrationen: `GET /api/workspaces/{slug}/importers/`, `DELETE …/importers/{service}/{importerId}/`, `GET …/importers/{service}/`, `POST …/projects/importers/{service}/`, `GET …/importers/jira`, `POST …/projects/importers/jira/`; `DELETE …/workspace-integrations/{id}/provider/`, `POST …/workspace-integrations/{provider}/`, `GET …/workspace-integrations/{slug}/github-repositories`, `…/projects/{pid}/workspace-integrations/{id}/github-repository-sync/`, `…/projects/{pid}/workspace-integrations/{id}/project-slack-sync/[{syncId}]` | `apps/web/services/integrations/integration.service.ts` Z. 35, 43, 67; `apps/web/services/integrations/github.service.ts` Z. 21, 29, 39; `apps/web/services/integrations/jira.service.ts` Z. 18, 28; `apps/web/services/app_installation.service.ts` Z. 18, 32, 47, 62; `apps/web/services/project/project.service.ts` Z. 144, 155 | PF-83/PF-84/PF-86 |

**Nicht EE-zuordenbare tote Aufrufe (Verifikation, nur der Vollständigkeit halber):** `POST …/projects/{pid}/bulk-subscribe-issues/` (`apps/web/services/issue/issue.service.ts` Z. 410–418, ohne Aufrufer), `GET …/projects/{pid}/archived-pages/` (`apps/web/services/page/project-page.service.ts` Z. 106), `GET …/workspaces/{slug}/my-issues/` (`apps/web/services/user.service.ts` Z. 46), `GET /api/release-notes/` (`apps/web/services/workspace.service.ts` Z. 225), `GET /api/configs/` (`apps/web/services/app_config.service.ts` Z. 21), `GET …/projects/{pid}/views/{viewId}/issues/` (`apps/web/services/view.service.ts` Z. 59). Methode: Skript-Abgleich aller `/api/…`-Literale in `apps/web`, `apps/space`, `apps/admin`, `packages/services` mit den `path(...)`-Mustern aus `apps/api/plane/**/urls*.py`, Treffer einzeln per `grep` gegengeprüft.

---

## 10. Offene Punkte / Unklarheiten

| ID | Thema | Befund | Vorschlag / Rückfrage an Auftraggeber |
|---|---|---|---|
| OP-01 | Editions-Badge in der Sidebar-Fußzeile | `WorkspaceEditionBadge` („Community“, öffnet Upgrade-Modal) ist fester Bestandteil des CE-Layouts (`apps/web/components/sidebar/sidebar-wrapper.tsx` Z. 85). ADR-001 verbietet Upsell, ADR-005 verlangt 1:1-UI. | Rückfrage: Fußzeile mit neutralem Label (z. B. Produktname + Version im Tooltip, ohne Modal) beibehalten oder Fußzeile entfernen? |
| OP-02 | Widersprüchliche Tier-Angaben | Wiki: `plans.tsx` One, `PRO_PLAN_FEATURES` „Wikis“, Upsell „with Plane Pro“, Doku „Wiki Pro“ → **entschieden: Pro**; SAML/OIDC: `plans.tsx` One, Doku-Badges Pro/Business (One beibehalten); Workflows: `BUSINESS_PLAN_FEATURES`/Doku 2026 Business vs. WebSearch „single workflow per project“ in Pro (UNVERIFIZIERT) → Business; Custom Automations: `plans.tsx` Pro vs. Doku 2026 Business → **entschieden: Business**; Customers: Pro (UNVERIFIZIERT) vs. Business (Plane University, Business-Launch-Post) → **entschieden: Business**; LDAP: `plans.tsx` Enterprise vs. Doku Enterprise Grid → Enterprise Grid; Approvals: Matrix Business vs. Doku 2026 Enterprise Grid (Approval-Flows) → Matrixzeile Business; Initiatives: `plans.tsx` „Coming soon“ vs. plane.so/pro „epics and initiatives“ vs. Plane University Business (Dok. 21) → Pro beibehalten; Nested Pages: Zellwerte in `plans.tsx` Z. 929–930 offensichtlich falsch. | Für die Portierung irrelevant (ADR-001, alles aktiv); Tabelle 3 dokumentiert den jeweils niedrigsten belegten Plan nach der Regel in Abschnitt 3 (Legende „ab Plan“). |
| OP-03 | „Enterprise“ vs. „Enterprise Grid“ | CE-Code kennt nur `ENTERPRISE`; Doku/Website nennen „Enterprise Grid“ (LDAP, SCIM, Airgapped, FIPS, Multi-Workspace, API-Audit-Logs). | Als Synonym behandeln; SCIM (nur WebSearch belegt) in den Scope aufnehmen? |
| OP-04 | Rollenmodell (Pro „four pre-defined roles“, Business RBAC, Enterprise GAC) | Vierte Rolle und Permission-Katalog sind im Repo nicht benannt. | Öffentliche Doku (docs.plane.so) per Folge-Recherche auswerten; bis dahin RBAC mit frei definierbaren Rollen über die 3 CE-Rollen hinaus entwerfen. |
| OP-05 | Fehlende UI-Texte/Screens für mehrere EE-Features | Keine i18n-Namespaces/Komponenten für Customers, Initiatives, Teamspaces, Dashboards, Releases, Milestones (UI), Pi-Chat, Approvals; Dashboard-Paletten-Keys `dashboards.widget.color_palettes.*` fehlen in allen Locales. | **Rückfrage:** Steht eine lizenzierte/Trial-Instanz der Commercial Edition für Referenz-Screenshots (ADR-005, visuelle Regressionstests) zur Verfügung? Ohne sie ist „1:1“ für diese Features nur aus öffentlichen Screenshots/Doku annäherbar. |
| OP-06 | PQL-Grammatik | Nur Existenz und API-Fehlertext belegt (`apps/api/plane/api/views/issue.py` Z. 324–335). | Eigene Grammatik (Felder/Operatoren der Rich-Filter + AND/OR/NOT) definieren und dokumentieren. |
| OP-07 | Formel-Properties / Roll-ups | Belegt: Referenzen `{Field Name}`, Operatoren `+ - * / &`, Zirkelprüfung, Ergebnistyp-Anzeige. Roll-up-Semantik unbelegt. | Formelsprache minimal nach Belegen umsetzen; Roll-ups (Summe/Min/Max/Count über Kinder) vorschlagen. |
| OP-08 | Recurring Work Items – Intervalltypen | Nur „Start date“ und „Interval type“ belegt. | Intervalle analog Automations-Zeitplan (Daily/Weekly/Monthly + Cron) vorschlagen. |
| OP-09 | Weitere Commercial-Produkte nur als Icons/Slugs | `sub-brands/desk`, `sub-brands/bridge`, `workspace-features/briefs`, `workspace-features/workgraph`, `miscellaneous/pii-scanner`, `library`, `excerpt`/`insert-excerpt`; reservierte Slugs `chat`, `calendar`, `drive`, `channels`. | **Rückfrage:** Gehören diese (für die keine Funktionsspuren existieren) zum Portierungsumfang „ALLE Features“? Falls ja, ist eine gesonderte Recherche nötig. |
| OP-10 | Marketplaces (Templates, Applications) im Airgapped-Betrieb | Publish-to-Marketplace und App-Review „approved by Plane“ setzen einen zentralen Plane-Dienst voraus. | Als instanzlokale Kataloge umsetzen (ADR-004). |
| OP-11 | Plane Runner / „Run Script“ | Ausführung benutzerdefinierter Skripte – Sprache und Sandbox unbekannt. | Sicherheitskonzept (isolierte Ausführung, Zeit-/Speicherlimits) als eigenes ADR. |
| OP-12 | Checkpoints vs. Milestones | `plans.tsx` nennt Checkpoints (Coming soon) für Projekte/Epics/Initiativen; Repo hat nur Projekt-Milestones. | Als ein Konzept (Milestone/Checkpoint auf Projekt, Epic, Initiative) modellieren, sofern keine gegenteilige Quelle. |
| OP-13 | Projekt-Netzwerk „Private (Beitritt mit Genehmigung)“ | CE nutzt 0 (UI-Label „Private“, Backend-Label „Secret“) und 2 (Public). Wert für die dritte Stufe unbelegt. | Enum `Secret=0, Private=1, Public=2` verwenden; UI-Labels gemäß Matrix. |
| OP-14 | Externe SaaS-Integrationen (Zapier, Zendesk, Freshdesk, Slack, GitHub.com, GitLab.com, Sentry) | In `plans.tsx` als „Coming soon“ bzw. Pro; im Airgapped-Betrieb nicht nutzbar. | Optional/abschaltbar (ADR-004); Rückfrage, ob Zapier/Zendesk/Freshdesk überhaupt gebaut werden sollen. |
| OP-15 | Real-time Collab im CE | CE synchronisiert Pages bereits per Yjs; nur `collaboration-cursor` ist deaktiviert. Exakter Mehrumfang „Real-time Collab“ (One) außer Cursor/Presence unklar. | Cursor/Presence + Kollaboration in Wiki-/Teamspace-Pages umsetzen. |
| OP-16 | Product Tour / Get-started | Namespace `tour.json` vollständig ohne CE-Referenz, aber `apps/web/components/onboarding/tour/root.tsx` existiert. | Klären, ob Cloud-Onboarding (Demo-Projekt, Touren) portiert werden soll. |
| OP-17 | Legacy-Integrationsmodelle | CE enthält GitHub/Slack-Modelle ohne Endpunkte. | Greenfield (ADR-003): neu entwerfen, nicht übernehmen. |
| OP-18 | Aufbewahrung Page-Versionen | CE: 20 Versionen/Page; EE: zeitbasiert bis „Unlimited“. | Instanzeinstellung mit Default „Unlimited“ (ADR-001-Konsequenz). |
| OP-19 | Heuristik i18n-Auswertung | Schlüssel, die über Konstanten-Objekte zusammengesetzt werden, können fälschlich als „ohne CE-Referenz“ erscheinen; EE-Zuordnung in Anhang A wurde inhaltlich geprüft, Restunschärfe bei `common.json`, `project-settings.json` (`project_settings.estimates.*`) möglich. | Bei Implementierung je Schlüssel gegen den Ziel-Screen prüfen. |

---

## Anhang A: i18n-Schlüsselgruppen mit EE-Texten (ohne CE-Referenz, inhaltlich EE zugeordnet)

Automatisch erzeugt (Q5), gefiltert auf EE-relevante Präfixe. Format: `` `Gruppe` (Anzahl): Restschlüssel `` – vollständiger Schlüssel = `Gruppe.Restschlüssel`. Werte stehen in `packages/i18n/src/locales/<locale>/<datei>`.

#### `packages/i18n/src/locales/en/auth.json` (117 Schlüssel)

- `sso` (2): header, description
- `sso.domain_management` (1): header
- `sso.domain_management.verified_domains` (46): header, description, button_text, list.domain_name, list.status, list.status_verified, list.status_failed, list.status_pending, add_domain.title, add_domain.description, add_domain.form.domain_label, add_domain.form.domain_placeholder, add_domain.form.domain_required, add_domain.form.domain_invalid, add_domain.primary_button_text, add_domain.primary_button_loading_text, add_domain.toast.success_title, add_domain.toast.success_message, add_domain.toast.error_message, verify_domain.title, verify_domain.description, verify_domain.instructions.label, verify_domain.instructions.step_1, verify_domain.instructions.step_2.part_1, verify_domain.instructions.step_2.part_2, verify_domain.instructions.step_2.part_3, verify_domain.instructions.step_3, verify_domain.instructions.step_4, verify_domain.verification_code_label, verify_domain.verification_code_description, verify_domain.domain_label, verify_domain.primary_button_text, verify_domain.primary_button_loading_text, verify_domain.secondary_button_text, verify_domain.toast.success_title, verify_domain.toast.success_message, verify_domain.toast.error_message, delete_domain.title, delete_domain.description.prefix, delete_domain.description.suffix, delete_domain.primary_button_text, delete_domain.primary_button_loading_text, delete_domain.secondary_button_text, delete_domain.toast.success_title, delete_domain.toast.success_message, delete_domain.toast.error_message
- `sso.providers` (2): header, disabled_message
- `sso.providers.configure` (2): create, update
- `sso.providers.switch_alert_modal` (5): title, content, primary_button_text, primary_button_text_loading, secondary_button_text
- `sso.providers.form_section` (1): title
- `sso.providers.form_action_buttons` (5): saving, save_changes, configure_only, configure_and_enable, default
- `sso.providers.setup_details_section` (2): title, button_text
- `sso.providers.saml` (26): header, description, configure.title, configure.description, configure.toast.success_title, configure.toast.create_success_message, configure.toast.update_success_message, configure.toast.error_title, configure.toast.error_message, setup_modal.web_details.header, setup_modal.web_details.entity_id.label, setup_modal.web_details.entity_id.description, setup_modal.web_details.callback_url.label, setup_modal.web_details.callback_url.description, setup_modal.web_details.logout_url.label, setup_modal.web_details.logout_url.description, setup_modal.mobile_details.header, setup_modal.mobile_details.entity_id.label, setup_modal.mobile_details.entity_id.description, setup_modal.mobile_details.callback_url.label, setup_modal.mobile_details.callback_url.description, setup_modal.mobile_details.logout_url.label, setup_modal.mobile_details.logout_url.description, setup_modal.mapping_table.header, setup_modal.mapping_table.table.idp, setup_modal.mapping_table.table.plane
- `sso.providers.oidc` (23): header, description, configure.title, configure.description, configure.toast.success_title, configure.toast.create_success_message, configure.toast.update_success_message, configure.toast.error_title, configure.toast.error_message, setup_modal.web_details.header, setup_modal.web_details.origin_url.label, setup_modal.web_details.origin_url.description, setup_modal.web_details.callback_url.label, setup_modal.web_details.callback_url.description, setup_modal.web_details.logout_url.label, setup_modal.web_details.logout_url.description, setup_modal.mobile_details.header, setup_modal.mobile_details.origin_url.label, setup_modal.mobile_details.origin_url.description, setup_modal.mobile_details.callback_url.label, setup_modal.mobile_details.callback_url.description, setup_modal.mobile_details.logout_url.label, setup_modal.mobile_details.logout_url.description
- `auth.ldap.header` (2): label, sub_header

#### `packages/i18n/src/locales/en/automation.json` (141 Schlüssel)

- `automations.settings` (2): title, create_automation
- `automations.scope` (2): label, run_on
- `automations.trigger` (8): label, add_trigger, sidebar_header, input_label, input_placeholder, section_plane_events, section_time_based, fixed_schedule
- `automations.trigger.schedule` (31): frequency, select_day, day_of_month, monthly_every, monthly_day_aria, time, hour, minute, hour_suffix, minute_suffix, am, pm, timezone, timezone_placeholder, frequency_daily, frequency_weekly, frequency_monthly, on, validation_weekly_day_required, validation_monthly_date_required, main_content_schedule_summary_daily, main_content_schedule_summary_weekly, main_content_schedule_summary_monthly, schedule_mode, schedule_mode_fixed, schedule_mode_cron, cron_expression_label, cron_expression_placeholder, cron_invalid, cron_preview, main_content_cron_summary
- `automations.trigger.button` (2): previous, next
- `automations.trigger.warning` (1): disabled_trigger_switching
- `automations.condition` (3): label, add_condition, adding_condition
- `automations.action` (5): label, add_action, sidebar_header, input_label, input_placeholder
- `automations.action.handler_name` (3): add_comment, change_property, run_script
- `automations.action.configuration` (8): label, change_property.placeholders.property_name, change_property.placeholders.change_type, change_property.placeholders.property_value_select, change_property.placeholders.property_value_select_date, change_property.validation.property_name_required, change_property.validation.change_type_required, change_property.validation.property_value_required
- `automations.action.comment_block` (1): title
- `automations.action.run_script_block` (1): title
- `automations.action.change_property_block` (1): title
- `automations.action.validation` (1): delete_only_action
- `automations.conjunctions` (4): and, or, if, then
- `automations.enable` (1): alert
- `automations.enable.validation` (1): required
- `automations.delete.validation` (1): enabled
- `automations.table` (10): title, scope, projects, last_run_on, created_on, last_updated_on, last_run_status, average_duration, owner, executions
- `automations.create_modal.heading` (2): create, update
- `automations.create_modal.title` (2): placeholder, required_error
- `automations.create_modal.description` (1): placeholder
- `automations.create_modal.submit_button` (2): create, update
- `automations.delete_modal` (1): heading
- `automations.activity.filters` (4): show_fails, all, only_activity, only_run_history
- `automations.activity.run_history` (1): initiator
- `automations.toasts.create` (4): success.title, success.message, error.title, error.message
- `automations.toasts.update` (4): success.title, success.message, error.title, error.message
- `automations.toasts.enable` (4): success.title, success.message, error.title, error.message
- `automations.toasts.disable` (4): success.title, success.message, error.title, error.message
- `automations.toasts.delete` (4): success.title, success.message, error.title, error.message
- `automations.toasts.action` (4): create.error.title, create.error.message, update.error.title, update.error.message
- `automations.empty_state.no_automations` (2): title, description
- `automations.empty_state.upgrade` (3): title, description, sub_description
- `automations.global_automations.project_select` (6): label, all_projects.label, all_projects.description, select_projects.label, select_projects.description, select_projects.placeholder
- `automations.global_automations.settings` (3): sidebar_label, title, description
- `automations.global_automations.table` (4): scope.global, scope.project.label, scope.project.multiple, scope.project.all

#### `packages/i18n/src/locales/en/common.json` (40 Schlüssel)

- `cloud_maintenance_message` (4): we_are_working_on_this_if_you_need_immediate_assistance, reach_out_to_us, otherwise_try_refreshing_the_page_occasionally_or_visit_our, status_page
- `activity_empty_state` (2): no_transitions, no_worklogs
- `(Top-Level)` (12): 10000_feet_view_description, get_snapshot_of_each_active_cycle_description, compare_burndowns_description, quickly_see_make_or_break_issues_description, zoom_into_cycles_that_need_attention_description, stay_ahead_of_blockers_description, renew, failed_to_move_issue_to_project, upgrade_request, in_app, forms, milestones_description
- `common` (17): on_track, off_track, at_risk, mandate, mandatory, upgrade, add_seats, change_history, worklogs, project_updates, workflows, templates, business, members_and_teamspaces, recurring_work_items, milestones, custom_properties
- `common.actions` (1): reply
- `common.upgrade_cta` (1): higher_subscription
- `chart` (3): x_axis, y_axis, metric

#### `packages/i18n/src/locales/en/cycle.json` (4 Schlüssel)

- `active_cycle_analytics.empty_state.progress` (1): title
- `active_cycle_analytics.empty_state.priority` (1): title
- `active_cycle_analytics.empty_state.assignee` (1): title
- `active_cycle_analytics.empty_state.label` (1): title

#### `packages/i18n/src/locales/en/editor.json` (29 Schlüssel)

- `attachmentComponent.uploader` (1): drag_and_drop
- `attachmentComponent.errors.file_too_large` (2): title, description
- `attachmentComponent.errors.unsupported_file_type` (2): title, description
- `attachmentComponent.errors.default` (2): title, description
- `attachmentComponent.upgrade` (1): description
- `attachmentComponent.aria` (1): click_to_upload
- `externalEmbedComponent.block_menu` (3): convert_to_embed, convert_to_link, convert_to_richcard
- `externalEmbedComponent.placeholder` (2): insert_embed, link
- `externalEmbedComponent.input_modal` (2): embed, works_with_links
- `externalEmbedComponent.error` (1): not_valid_link
- `ai_block.content` (2): placeholder, generated_here
- `ai_block.block_types` (3): placeholder, summarize_page, custom_prompt
- `ai_block.actions` (7): discard, generate, generating, rewriting, rewrite, use_this, refine

#### `packages/i18n/src/locales/en/empty-state.json` (48 Schlüssel)

- `common_empty_state.progress` (2): title, description
- `common_empty_state.updates` (2): title, description
- `project_empty_state.epics` (4): title, description, cta_primary, cta_secondary
- `project_empty_state.epic_work_items` (3): title, description, cta_secondary
- `workspace_empty_state.archive_epics` (2): title, description
- `workspace_empty_state.active_cycles` (2): title, description
- `workspace_empty_state.dashboard` (3): title, description, cta_primary
- `workspace_empty_state.wiki` (3): title, description, cta_primary
- `workspace_empty_state.project_overview_state_sidebar` (2): title, description
- `settings_empty_state.workspace_tokens` (3): title, description, cta_primary
- `settings_empty_state.work_item_types` (3): title, description, cta_primary
- `settings_empty_state.work_item_type_properties` (2): title, cta_secondary
- `settings_empty_state.templates` (3): title, description, cta_primary
- `settings_empty_state.recurring_work_items` (3): title, description, cta_primary
- `settings_empty_state.worklogs` (2): title, description
- `settings_empty_state.group_syncing` (1): title
- `settings_empty_state.template_setting` (3): title, description, cta_primary
- `settings_empty_state.workflows` (3): title, description, cta_primary
- `settings_empty_state.workflows.states` (2): title, description

#### `packages/i18n/src/locales/en/home.json` (6 Schlüssel)

- `home.business_trial_banner` (6): title, description, trial_ends_today, trial_ends_in_days, start_subscription, explore_business_features

#### `packages/i18n/src/locales/en/integration.json` (290 Schlüssel)

- `integrations` (15): loading, unauthorized, configure, not_enabled, not_configured, disconnect_personal_account, not_configured_message_admin, not_configured_message_support, external_api_unreachable, error_fetching_supported_integrations, back_to_integrations, select_state, set_state, choose_project, skip_backward_state_movement
- `github_integration` (45): name, description, connect_org, connect_org_description, processing, org_added_desc, connection_fetch_error, personal_account_connected, personal_account_connected_description, connect_personal_account, connect_personal_account_description, repo_mapping, repo_mapping_description, project_issue_sync, project_issue_sync_description, project_issue_sync_empty_state, configure_project_issue_sync_state, select_issue_sync_direction, allow_bidirectional_sync, allow_unidirectional_sync, allow_unidirectional_sync_warning, remove_project_issue_sync, remove_project_issue_sync_confirmation, add_pr_state_mapping, edit_pr_state_mapping, pr_state_mapping, pr_state_mapping_description, pr_state_mapping_empty_state, remove_pr_state_mapping, remove_pr_state_mapping_confirmation, issue_sync_message, link, pull_request_automation, pull_request_automation_description, DRAFT_MR_OPENED, MR_OPENED, MR_READY_FOR_MERGE, MR_REVIEW_REQUESTED, MR_MERGED, MR_CLOSED, ISSUE_OPEN, ISSUE_CLOSED, save, start_sync, choose_repository
- `gitlab_integration` (39): name, description, connection_fetch_error, connect_org, connect_org_description, project_connections, project_connections_description, plane_project_connection, plane_project_connection_description, remove_connection, remove_connection_confirmation, link, pull_request_automation, pull_request_automation_description, DRAFT_MR_OPENED, MR_OPENED, MR_REVIEW_REQUESTED, MR_READY_FOR_MERGE, MR_MERGED, MR_CLOSED, integration_enabled_text, choose_entity, choose_project, link_plane_project, project_issue_sync, project_issue_sync_description, project_issue_sync_empty_state, configure_project_issue_sync_state, select_issue_sync_direction, allow_bidirectional_sync, allow_unidirectional_sync, allow_unidirectional_sync_warning, remove_project_issue_sync, remove_project_issue_sync_confirmation, ISSUE_OPEN, ISSUE_CLOSED, save, start_sync, choose_repository
- `gitlab_enterprise_integration` (22): name, description, app_form_title, app_form_description, base_url_title, base_url_description, base_url_placeholder, base_url_error, invalid_base_url_error, client_id_title, client_id_description, client_id_placeholder, client_id_error, client_secret_title, client_secret_description, client_secret_placeholder, client_secret_error, webhook_secret_title, webhook_secret_description, webhook_secret_placeholder, webhook_secret_error, connect_app
- `slack_integration` (8): name, description, connect_personal_account, personal_account_connected, link_personal_account, connected_slack_workspaces, connected_on, disconnect_workspace
- `slack_integration.alerts.dm_alerts` (1): title
- `slack_integration.project_updates` (4): title, description, add_new_project_update, project_updates_empty_state
- `slack_integration.project_updates.project_updates_form` (18): title, description, failed_to_load_channels, project_dropdown.placeholder, project_dropdown.label, project_dropdown.no_projects, channel_dropdown.label, channel_dropdown.placeholder, channel_dropdown.no_channels, all_projects_connected, all_channels_connected, project_connection_success, project_connection_updated, project_connection_deleted, failed_delete_project_connection, failed_create_project_connection, failed_upserting_project_connection, failed_loading_project_connections
- `sentry_integration` (5): name, description, connected_sentry_workspaces, connected_on, disconnect_workspace
- `sentry_integration.state_mapping` (11): title, description, add_new_state_mapping, empty_state, failed_loading_state_mappings, loading_project_states, error_loading_states, no_states_available, no_permission_states, states_not_found, server_error_states
- `bitbucket_dc_integration` (2): name, description
- `oauth_bridge_integration` (29): name, description, header_description, connected, connect, uninstall, uninstalling, install_success, install_error, uninstall_success, uninstall_error, token_providers, token_providers_description, add_provider, edit_provider, enabled, disabled, test, no_providers_title, no_providers_description, provider_updated, provider_added, provider_save_error, provider_deleted, provider_delete_error, provider_update_error, jwks_reachable, jwks_unreachable, jwks_test_error
- `oauth_bridge_integration.provider_form` (33): name_label, name_placeholder, name_description, name_required, issuer_label, issuer_placeholder, issuer_description, issuer_required, jwks_url_label, jwks_url_placeholder, jwks_url_description, jwks_url_required, jwks_url_https, audience_label, audience_placeholder, audience_description, user_claims_label, user_claims_placeholder, user_claims_description, user_claims_required, allowed_algorithms_label, allowed_algorithms_description, allowed_algorithms_required, select_algorithms, jwks_cache_ttl_label, jwks_cache_ttl_description, jwks_cache_ttl_min, rate_limit_label, rate_limit_placeholder, rate_limit_description, enable_provider, saving, update
- `github_enterprise_integration` (34): name, description, app_form_title, app_form_description, app_id_title, app_id_description, app_id_placeholder, app_id_error, app_name_title, app_name_description, app_name_error, app_name_placeholder, base_url_title, base_url_description, base_url_placeholder, base_url_error, invalid_base_url_error, client_id_title, client_id_description, client_id_placeholder, client_id_error, client_secret_title, client_secret_description, client_secret_placeholder, client_secret_error, webhook_secret_title, webhook_secret_description, webhook_secret_placeholder, webhook_secret_error, private_key_title, private_key_description, private_key_placeholder, private_key_error, connect_app
- `silo_errors` (11): invalid_query_params, invalid_installation_account, generic_error, connection_not_found, multiple_connections_found, cannot_create_multiple_connections, installation_not_found, user_not_found, error_fetching_token, invalid_app_credentials, invalid_app_installation_id
- `import_status` (13): queued, created, initiated, pulling, timed_out, pulled, progressing, transforming, transformed, pushing, finished, error, cancelled

#### `packages/i18n/src/locales/en/navigation.json` (5 Schlüssel)

- `sidebar` (5): upgrade, epics, upgrade_plan, plane_pro, business

#### `packages/i18n/src/locales/en/page.json` (22 Schlüssel)

- `page_navigation_pane.tabs.info` (1): version_history.highlight_changes
- `page_navigation_pane.tabs.comments` (3): label, empty_state.title, empty_state.description
- `page_actions.move_page.submit_button` (2): default, loading
- `page_actions.move_page` (1): cannot_move_to_teamspace
- `page_actions.move_page.placeholders` (6): workspace_to_all, workspace_to_project, project_to_all, project_to_project, project_to_all_with_wiki, project_to_project_with_wiki
- `page_actions.move_page.toasts` (6): success.title, success.message, error.title, error.message, collection_error.title, collection_error.message
- `page_actions.remove_from_collection` (3): label, success_message, error_message

#### `packages/i18n/src/locales/en/power-k.json` (5 Schlüssel)

- `power_k.creation_actions` (1): create_project_automation
- `power_k.navigation_actions` (2): nav_workspace_active_cycle, nav_project_overview
- `power_k.help_actions` (1): chat_with_us
- `power_k.search_menu` (1): go_to_advanced_search

#### `packages/i18n/src/locales/en/project-settings.json` (165 Schlüssel)

- `project_settings.estimates.toasts` (8): reorder.success.title, reorder.success.message, reorder.error.title, reorder.error.message, switch.success.title, switch.success.message, switch.error.title, switch.error.message
- `project_settings.estimates.validation` (2): fill, repeat
- `project_settings.estimates.edit` (5): title, add_or_update.title, add_or_update.description, switch.title, switch.description
- `project_settings.estimates` (3): switch, current, select
- `project_settings.automations.auto-remind` (3): title, description, duration
- `project_settings.empty_state.integrations` (2): title, description
- `project_settings.workflows.toggle` (11): title, description, no_states_tooltip, no_work_item_types_tooltip, no_states_or_work_item_types_tooltip, toast.loading.enabling, toast.loading.disabling, toast.success.title, toast.success.message, toast.error.title, toast.error.message
- `project_settings.workflows` (4): heading, description, add_button, search
- `project_settings.workflows.detail` (7): define, add_states, unmapped_states.title, unmapped_states.description, unmapped_states.note, unmapped_states.label, unmapped_states.tooltip
- `project_settings.workflows.select_states` (2): empty_state.title, empty_state.description
- `project_settings.workflows.default_footer` (1): fallback_message
- `project_settings.workflows.create` (12): heading, name.placeholder, name.validation.max_length, name.validation.required, name.validation.invalid, description.placeholder, description.validation.invalid, work_item_type.label, success.title, success.message, error.title, error.message
- `project_settings.workflows.update` (4): success.title, success.message, error.title, error.message
- `project_settings.workflows.delete` (5): loading, success.title, success.message, error.title, error.message
- `project_settings.workflows.add_states` (4): success.title, success.message, error.title, error.message
- `project_settings.work_item_types` (2): heading, description
- `project_settings.features.intake` (34): intake_responsibility, intake_sources, toggle_tooltip_on, toggle_tooltip_off, notify_assignee.title, notify_assignee.description, in_app.title, in_app.description, email.title, email.description, email.fieldName, form.title, form.description, form.fieldName, form.create_forms, form.manage_forms, form.manage_forms_tooltip, form.create_form, form.edit_form, form.form_title, form.form_title_required, form.work_item_type, form.remove_property, form.select_properties, form.search_placeholder, form.toasts.success_create, form.toasts.success_update, form.toasts.error_create, form.toasts.error_update, toasts.set.loading, toasts.set.success.title, toasts.set.success.message, toasts.set.error.title, toasts.set.error.message
- `project_settings.features.time_tracking` (5): title, short_title, description, toggle_title, toggle_description
- `project_settings.features.milestones` (5): title, short_title, description, toggle_title, toggle_description
- `project_settings.project_updates` (2): heading, description
- `project_settings.templates` (2): heading, description
- `project_settings.cycles.auto_schedule` (42): heading, description, tooltip, edit_button, form.cycle_title.label, form.cycle_title.placeholder, form.cycle_title.tooltip, form.cycle_title.validation.required, form.cycle_title.validation.max_length, form.cycle_duration.label, form.cycle_duration.unit, form.cycle_duration.validation.required, form.cycle_duration.validation.min, form.cycle_duration.validation.max, form.cycle_duration.validation.positive, form.cooldown_period.label, form.cooldown_period.unit, form.cooldown_period.tooltip, form.cooldown_period.validation.required, form.cooldown_period.validation.negative, form.start_date.label, form.start_date.validation.required, form.start_date.validation.past, form.number_of_cycles.label, form.number_of_cycles.validation.required, form.number_of_cycles.validation.min, form.number_of_cycles.validation.max, form.auto_rollover.label, form.auto_rollover.tooltip, toast.toggle.loading_enable, toast.toggle.loading_disable, toast.toggle.success.title, toast.toggle.success.message, toast.toggle.error.title, toast.toggle.error.message, toast.save.loading, toast.save.success.title, toast.save.success.message_create, toast.save.success.message_update, toast.save.error.title, toast.save.error.message_create, toast.save.error.message_update

#### `packages/i18n/src/locales/en/project.json` (35 Schlüssel)

- `project_cycles.active_cycle` (5): chart, ideal, current, trailing, leading
- `project_views.empty_state.public` (3): title, description, primary_button.text
- `project_views.empty_state.shared` (2): title, description
- `project.members_import` (3): title, description, download_sample
- `project.members_import.dropzone` (3): active, inactive, file_type
- `project.members_import.buttons` (5): cancel, import, try_again, close, done
- `project.members_import.progress` (2): uploading, importing
- `project.members_import.summary` (8): title.complete, message.success, message.no_imports, stats.added, stats.reactivated, stats.already_members, stats.skipped, download_errors
- `project.members_import.toast` (4): invalid_file.title, invalid_file.message, import_failed.title, import_failed.message

#### `packages/i18n/src/locales/en/settings.json` (6 Schlüssel)

- `account_settings.activity` (2): heading, description
- `account_settings.connections` (3): title, heading, description
- `profile.actions` (1): connections

#### `packages/i18n/src/locales/en/template.json` (137 Schlüssel)

- `templates.settings` (5): title, description, new_project_template, new_work_item_template, new_page_template
- `templates.settings.options` (3): project.label, work_item.label, page.label
- `templates.settings.create_template` (3): label, no_permission.project, no_permission.workspace
- `templates.settings.use_template` (2): button.default, button.loading
- `templates.settings.template_source` (2): workspace.info, project.info
- `templates.settings.form` (81): project.template.name.placeholder, project.template.name.validation.required, project.template.name.validation.maxLength, project.template.description.placeholder, project.name.placeholder, project.name.validation.required, project.name.validation.maxLength, project.description.placeholder, project.button.create, project.button.update, work_item.template.name.placeholder, work_item.template.name.validation.required, work_item.template.name.validation.maxLength, work_item.template.description.placeholder, work_item.name.placeholder, work_item.name.validation.required, work_item.name.validation.maxLength, work_item.description.placeholder, work_item.button.create, work_item.button.update, page.template.name.placeholder, page.template.name.validation.required, page.template.name.validation.maxLength, page.template.description.placeholder, page.name.placeholder, page.name.validation.maxLength, page.button.create, page.button.update, publish.action, publish.unpublish_action, publish.title, publish.name.label, publish.name.placeholder, publish.name.validation.required, publish.name.validation.maxLength, publish.short_description.label, publish.short_description.placeholder, publish.short_description.validation.required, publish.description.label, publish.description.placeholder, publish.description.validation.required, publish.category.label, publish.category.placeholder, publish.category.validation.required, publish.keywords.label, publish.keywords.placeholder, publish.keywords.helperText, publish.keywords.validation.required, publish.website.label, publish.website.placeholder, publish.website.validation.invalid, publish.website.validation.maxLength, publish.company_name.label, publish.company_name.placeholder, publish.company_name.validation.required, publish.company_name.validation.maxLength, publish.contact_email.label, publish.contact_email.placeholder, publish.contact_email.validation.invalid, publish.contact_email.validation.maxLength, publish.privacy_policy_url.label, publish.privacy_policy_url.placeholder, publish.privacy_policy_url.validation.invalid, publish.privacy_policy_url.validation.maxLength, publish.terms_of_service_url.label, publish.terms_of_service_url.placeholder, publish.terms_of_service_url.validation.invalid, publish.terms_of_service_url.validation.maxLength, publish.cover_image.label, publish.cover_image.upload_title, publish.cover_image.upload_placeholder, publish.cover_image.drop_here, publish.cover_image.click_to_upload, publish.cover_image.invalid_file_or_exceeds_size_limit, publish.cover_image.upload_and_save, publish.cover_image.uploading, publish.cover_image.remove, publish.cover_image.removing, publish.cover_image.validation.required, publish.attach_screenshots.label, publish.attach_screenshots.validation.required
- `templates.empty_state.upgrade` (3): title, description, sub_description
- `templates.empty_state.no_templates` (1): button
- `templates.empty_state.no_labels` (1): description
- `templates.empty_state.no_modules` (1): description
- `templates.empty_state.no_work_items` (1): description
- `templates.empty_state.no_sub_work_items` (1): description
- `templates.empty_state.page` (4): no_templates.title, no_templates.description, no_results.title, no_results.description
- `templates.toasts.create` (4): success.title, success.message, error.title, error.message
- `templates.toasts.update` (4): success.title, success.message, error.title, error.message
- `templates.toasts.delete` (4): success.title, success.message, error.title, error.message
- `templates.toasts.unpublish` (4): success.title, success.message, error.title, error.message
- `templates.delete_confirmation` (1): title
- `templates.delete_confirmation.description` (2): prefix, suffix
- `templates.unpublish_confirmation` (1): title
- `templates.unpublish_confirmation.description` (2): prefix, suffix
- `templates.dropdown.add` (2): work_item, project
- `templates.dropdown.label` (2): project, page
- `templates.dropdown.tooltip` (1): work_item
- `templates.dropdown.no_results` (2): work_item, project

#### `packages/i18n/src/locales/en/tour.json` (89 Schlüssel)

- `product_tour.workitems.step_zero` (2): title, description
- `product_tour.workitems.step_one` (2): title, description
- `product_tour.workitems.step_two` (2): title, description
- `product_tour.workitems.step_three` (2): title, description
- `product_tour.workitems.step_four` (2): title, description
- `product_tour.cycle.step_zero` (2): title, description
- `product_tour.cycle.step_one` (2): title, description
- `product_tour.cycle.step_two` (2): title, description
- `product_tour.cycle.step_three` (2): title, description
- `product_tour.cycle.step_four` (2): title, description
- `product_tour.module.step_zero` (2): title, description
- `product_tour.module.step_one` (2): title, description
- `product_tour.module.step_two` (2): title, description
- `product_tour.module.step_three` (2): title, description
- `product_tour.module.step_four` (2): title, description
- `product_tour.page.step_zero` (2): title, description
- `product_tour.page.step_one` (2): title, description
- `product_tour.page.step_two` (2): title, description
- `product_tour.page.step_three` (2): title, description
- `product_tour.page.step_four` (2): title, description
- `product_tour.page.step_five` (2): title, description
- `product_tour.intake.step_zero` (2): title, description
- `product_tour.intake.step_one` (2): title, description
- `product_tour.intake.step_two` (2): title, description
- `product_tour.intake.step_three` (2): title, description
- `product_tour.mcp_connectors.step_zero` (2): title, description
- `product_tour.navigation.modal` (6): title, sub_title, highlight_1, highlight_2, highlight_3, footer
- `product_tour.navigation.step_zero` (2): title, description
- `product_tour.navigation.step_one` (2): title, description
- `product_tour.navigation.step_two` (2): title, description
- `product_tour.actions` (7): close, next, back, done, take_a_tour, get_started, got_it
- `product_tour.seed_data` (2): title, description
- `get_started` (2): title, description
- `get_started.checklist_section` (2): title, description
- `get_started.checklist_section.checklist_items` (6): item_1.title, item_2.title, item_3.title, item_4.title, item_5.title, item_6.title
- `get_started.team_section` (2): title, description
- `get_started.integrations_section` (2): title, more_integrations
- `get_started.switch_to_plane_section` (2): title, description

#### `packages/i18n/src/locales/en/update.json` (29 Schlüssel)

- `updates.progress` (3): title, since_last_update, comments
- `updates` (2): add_update, add_update_placeholder
- `updates.empty` (2): title, description
- `updates.reaction.create` (4): success.title, success.message, error.title, error.message
- `updates.reaction.remove` (4): success.title, success.message, error.title, error.message
- `updates.create.success` (2): title, message
- `updates.create.error` (2): title, message
- `updates.delete` (2): title, confirmation
- `updates.delete.success` (2): title, message
- `updates.delete.error` (2): title, message
- `updates.update.success` (2): title, message
- `updates.update.error` (2): title, message

#### `packages/i18n/src/locales/en/wiki.json` (73 Schlüssel)

- `wiki_collections.predefined` (4): general, private, shared, archived
- `wiki_collections` (1): fallback_name
- `wiki_collections.form` (4): name_required, name_max_length, name_placeholder_create, name_placeholder_edit
- `wiki_collections.create_modal` (2): title, submit
- `wiki_collections.edit_modal` (1): title
- `wiki_collections.delete_modal` (10): title, page_count, transfer_title, transfer_description, transfer_warning, transfer_target_label, transfer_target_placeholder, delete_with_pages_title, delete_with_pages_description, submit
- `wiki_collections.header` (1): add_page
- `wiki_collections.menu` (4): create_new_page, add_existing_page, edit_collection, collection_options
- `wiki_collections.add_existing_page_modal` (6): search_placeholder, success_message, error_message, no_pages_found, no_pages_available, submit
- `wiki_collections.list` (13): invite_only, remove_error, no_matching_pages, remove_search_criteria, remove_filters, no_pages_title, no_pages_description, untitled, restricted_access, collapse_page, expand_page, page_actions, page_link_copied
- `wiki_collections.list.columns` (5): page_name, owner, nested_pages, last_activity, actions
- `wiki_collections.toasts` (11): created, create_error, renamed, rename_error, transferred_deleted, deleted_with_pages, delete_error, target_required, create_page_error, create_page_in_collection_error, collection_link_copied
- `wiki.upgrade_flow` (2): title, description
- `wiki.upgrade_flow.upgrade_button` (1): text
- `wiki.upgrade_flow.learn_more_button` (1): text
- `wiki.upgrade_flow.download_button` (2): text, loading
- `wiki.upgrade_flow.tabs` (4): nested_pages, add_embeds, publish_pages, comments
- `wiki.nested_pages_download_banner` (1): title

#### `packages/i18n/src/locales/en/work-item-type.json` (207 Schlüssel)

- `work_item_types` (2): label, label_lowercase
- `work_item_types.settings` (4): description, cant_delete_default_message, set_as_default, cant_set_default_inactive_message
- `work_item_types.settings.set_default_confirmation` (3): title, description, confirm_button
- `work_item_types.settings.properties` (89): title, description, tooltip, add_button, project.add_button.import_from_workspace, dropdown.label, dropdown.placeholder, property_type.text.label, property_type.number.label, property_type.dropdown.label, property_type.boolean.label, property_type.date.label, property_type.member_picker.label, property_type.formula.label, attributes.label, attributes.text.single_line.label, attributes.text.multi_line.label, attributes.text.readonly.label, attributes.text.readonly.header, attributes.text.invalid_text_format.label, attributes.number.default.placeholder, attributes.relation.single_select.label, attributes.relation.multi_select.label, attributes.relation.no_default_value.label, attributes.boolean.label, attributes.boolean.no_default, attributes.option.create_update.label, attributes.option.create_update.form.placeholder, attributes.option.create_update.form.errors.name.required, attributes.option.create_update.form.errors.name.integrity, attributes.option.select.placeholder.single, attributes.option.select.placeholder.multi.default, attributes.option.select.placeholder.multi.variable, toast.create.success.title, toast.create.success.message, toast.create.error.title, toast.create.error.message, toast.update.success.title, toast.update.success.message, toast.update.error.title, toast.update.error.message, toast.delete.success.title, toast.delete.success.message, toast.delete.error.title, toast.delete.error.message, toast.enable_disable.loading, toast.enable_disable.success.title, toast.enable_disable.success.message, toast.enable_disable.error.title, toast.enable_disable.error.message, create_update.title.create, create_update.title.update, create_update.form.display_name.placeholder, create_update.form.description.placeholder, create_update.errors.name.required, create_update.errors.name.max_length, create_update.errors.property_type.required, create_update.errors.options.required, create_update.errors.formula.required, create_update.errors.formula.invalid, create_update.errors.formula.circular_reference, create_update.errors.formula.invalid_reference, formula.field_label, formula.tooltip, formula.placeholder, formula.test_button, formula.validating, formula.validation_success, formula.validation_success_with_refs, formula.error.empty, formula.error.missing_context, formula.error.validation_failed, formula.picker.no_match, formula.picker.no_available, enable_disable.label, enable_disable.tooltip.disabled, enable_disable.tooltip.enabled, delete_confirmation.title, delete_confirmation.description, delete_confirmation.secondary_description, delete_confirmation.primary_button, delete_confirmation.secondary_button, mandate_confirmation.label, mandate_confirmation.content, mandate_confirmation.tooltip.disabled, mandate_confirmation.tooltip.enabled, mandate_confirmation.tooltip.checked, empty_state.title, empty_state.description
- `work_item_types.settings.types` (9): title, description, sort_options.project_count, filter_options.show_active, filter_options.show_inactive, project.add_button.create_new, project.add_button.import_from_workspace, project.banner.with_access, project.banner.without_access
- `work_item_types.settings.linked_properties` (11): title, add_button, modal.title, modal.empty.title, modal.empty.description, unlink_confirmation.title, unlink_confirmation.description, unlink_confirmation.input_label, unlink_confirmation.input_label_suffix, unlink_confirmation.confirm, unlink_confirmation.loading
- `work_item_types.settings.item_delete_confirmation` (10): title, description, can_disable_warning, primary_button, toast.success.title, toast.success.message, toast.error.title, toast.error.message, errors.cannot_delete_default_work_item_type, errors.cannot_delete_work_item_type_with_associated_work_items
- `work_item_types.create` (2): title, button
- `work_item_types.create.toast` (5): success.title, success.message, error.title, error.message.default, error.message.conflict
- `work_item_types.update` (2): title, button
- `work_item_types.update.toast` (5): success.title, success.message, error.title, error.message.default, error.message.conflict
- `work_item_types.create_update.form` (2): name.placeholder, description.placeholder
- `work_item_types.enable_disable.toast` (5): loading, success.title, success.message, error.title, error.message
- `work_item_types.enable_disable` (1): tooltip
- `work_item_types.change_confirmation` (2): title, description
- `work_item_types.change_confirmation.button` (2): loading, default
- `work_item_types.empty_state.enable` (7): title, description, primary_button.text, confirmation.title, confirmation.description, confirmation.button.default, confirmation.button.loading
- `work_item_types.empty_state.get_pro` (3): title, description, primary_button.text
- `work_item_types.empty_state.upgrade` (3): title, description, primary_button.text
- `work_item_type_hierarchy.settings` (4): title, tab_label, description, sidebar_label
- `work_item_type_hierarchy.settings.enable_control` (3): title, description, tooltip
- `work_item_type_hierarchy.settings.workspace_work_item_types_disabled_banner` (2): content, cta
- `work_item_type_hierarchy.levels` (3): max_level_placeholder, empty_level_placeholder, drag_tooltip
- `work_item_type_hierarchy.levels.quick_actions` (6): set_as_default.label, set_as_default.toast.loading, set_as_default.toast.success.title, set_as_default.toast.success.message, set_as_default.toast.error.title, set_as_default.toast.error.message
- `work_item_type_hierarchy.levels.update_level_toast` (3): loading, success.title, success.message
- `work_item_type_hierarchy.break_hierarchy_modal` (1): title
- `work_item_type_hierarchy.break_hierarchy_modal.content` (5): intro, parent_items, child_items, parent_line_suffix_when_also_children, footer
- `work_item_type_hierarchy.break_hierarchy_modal.confirm_input` (2): label, placeholder
- `work_item_type_hierarchy.break_hierarchy_modal.error_toast` (2): title, message
- `work_item_type_hierarchy.break_hierarchy_modal.confirm_button` (2): loading, default
- `work_item_type_hierarchy.work_item_modal.invalid_work_item_type_create_toast` (2): title, message
- `work_item_type_hierarchy.work_item_modal.invalid_work_item_type_update_toast` (2): title, message
- `work_item_type_hierarchy.work_item_type_modal` (1): level
- `work_item_type_hierarchy.work_item_type_modal.invalid_level_toast` (2): title, message

#### `packages/i18n/src/locales/en/work-item.json` (76 Schlüssel)

- `issue.display.properties` (1): issue_type
- `issue.comments.replies` (9): create.submit_button, create.placeholder, toast.fetch.error.message, toast.create.success.message, toast.create.error.message, toast.update.success.message, toast.update.error.message, toast.delete.success.message, toast.delete.error.message
- `issue.relation` (6): start_before, start_after, finish_before, finish_after, implements, implemented_by
- `issue.duplicate.modal` (4): title, description1, description2, placeholder
- `issue.toast.duplicate` (2): success.message, error.message
- `issue.pages` (5): link_pages, show_wiki_pages, link_pages_to, linked_pages, no_description
- `issue.pages.toasts` (8): link.success.title, link.success.message, link.error.title, link.error.message, remove.success.title, remove.success.message, remove.error.title, remove.error.message
- `issue.vote` (4): click_to_upvote, click_to_downvote, click_to_view_upvotes, click_to_view_downvotes
- `bulk_operations.error_details.invalid_archive_state_group` (2): title, message
- `bulk_operations.error_details.invalid_issue_start_date` (2): title, message
- `bulk_operations.error_details.invalid_issue_target_date` (2): title, message
- `bulk_operations.error_details.invalid_state_transition` (2): title, message
- `recurring_work_items.settings` (4): heading, description, new_recurring_work_item, update_recurring_work_item
- `recurring_work_items.settings.form` (5): interval.title, interval.start_date.validation.required, interval.interval_type.validation.required, button.create, button.update
- `recurring_work_items.settings.create_button` (2): label, no_permission
- `recurring_work_items.empty_state.upgrade` (2): title, description
- `recurring_work_items.empty_state.no_templates` (1): button
- `recurring_work_items.toasts.create` (4): success.title, success.message, error.title, error.message
- `recurring_work_items.toasts.update` (4): success.title, success.message, error.title, error.message
- `recurring_work_items.toasts.delete` (4): success.title, success.message, error.title, error.message
- `recurring_work_items.delete_confirmation` (1): title
- `recurring_work_items.delete_confirmation.description` (2): prefix, suffix

#### `packages/i18n/src/locales/en/workflow.json` (40 Schlüssel)

- `workflows.workflow_states` (5): work_item_creation, work_item_creation_disable_tooltip, default_state, state_change_count, movers_count
- `workflows.workflow_states.state_changes` (6): label.default, label.loading, move_to, movers.label, movers.tooltip, movers.add
- `workflows.workflow_disabled` (1): title
- `workflows.workflow_enabled` (1): label
- `workflows.workflow_tree` (2): label, state_change_label
- `workflows.empty_state.upgrade` (2): title, description
- `workflows.quick_actions` (2): view_change_history, reset_workflow
- `workflows.confirmation_modals.reset_workflow` (2): title, description
- `workflows.confirmation_modals.delete_state_change` (2): title, description
- `workflows.toasts.enable_disable` (5): loading, success.title, success.message, error.title, error.message
- `workflows.toasts.reset` (4): success.title, success.message, error.title, error.message
- `workflows.toasts.add_state_change_rule` (2): error.title, error.message
- `workflows.toasts.modify_state_change_rule` (2): error.title, error.message
- `workflows.toasts.remove_state_change_rule` (2): error.title, error.message
- `workflows.toasts.modify_state_change_rule_movers` (2): error.title, error.message

#### `packages/i18n/src/locales/en/workspace-settings.json` (245 Schlüssel)

- `workspace_settings.settings.general` (3): delete_modal.description, delete_modal.dismiss, delete_modal.cancel
- `workspace_settings.settings.billing_and_plans` (3): current_plan, free_plan, view_plans
- `workspace_settings.settings.api_tokens` (2): heading, description
- `workspace_settings.settings.integrations` (5): title, heading, description, page_title, page_description
- `workspace_settings.settings.imports` (3): title, heading, description
- `workspace_settings.settings.worklogs` (3): title, heading, description
- `workspace_settings.settings.group_syncing` (33): title, heading, description, enable.title, enable.description, config.title, config.description, config.sync_on_login.title, config.sync_on_login.description, config.sync_offline.title, config.sync_offline.description, config.auto_remove.title, config.auto_remove.description, config.group_attribute_key.title, config.group_attribute_key.description, config.group_attribute_key.placeholder, group_mapping.title, group_mapping.description, group_mapping.button_text, toast.updating, toast.success, toast.error, delete_modal.title, delete_modal.content, modal.idp_group_name.text, modal.idp_group_name.required, modal.idp_group_name.placeholder, modal.project.text, modal.project.required, modal.project.placeholder, modal.default_role.text, modal.default_role.required, modal.default_role.placeholder
- `workspace_settings.settings.identity` (3): title, heading, description
- `workspace_settings.settings.project_states` (4): title, heading, description, go_to_settings
- `workspace_settings.settings.projects` (4): title, description, tabs.states, tabs.labels
- `workspace_settings.settings.templates` (3): title, heading, description
- `workspace_settings.settings.relations` (3): title, heading, description
- `workspace_settings.settings.cancel_trial` (8): title, description, dismiss, cancel, cancel_success_title, cancel_success_message, cancel_error_title, cancel_error_message
- `workspace_settings.settings.applications` (161): internal, title, applicationId_copied, clientId_copied, clientSecret_copied, third_party_apps, your_apps, connect, connected, disconnect, install, installed, configure, app_available, app_credentials_regenrated.title, app_credentials_regenrated.description, app_created.title, app_created.description, installed_apps, all_apps, internal_apps, app_name_title, app_description_title.label, app_description_title.placeholder, authorization_grant_type.title, authorization_grant_type.description, website.title, website.description, website.placeholder, app_maker.title, app_maker.description, app_maker_error, setup_url.label, setup_url.description, setup_url.placeholder, webhook_url.label, webhook_url.description, webhook_url.placeholder, webhook_secret.label, webhook_secret.description, webhook_secret.placeholder, redirect_uris.label, redirect_uris.description, redirect_uris.placeholder, app_available_description, client_id_and_secret, client_id_and_secret_description, client_id_and_secret_download, application_id, client_id, client_secret, export_as_csv, slug_already_exists, failed_to_create_application, upload_logo, app_name_error, app_short_description_title, app_short_description_error, app_description_error, app_slug_title, app_slug_error, invalid_website_error, webhook_url_title, webhook_url_error, invalid_webhook_url_error, redirect_uris_title, redirect_uris_error, invalid_redirect_uris_error, redirect_uris_description, authorized_javascript_origins_title, authorized_javascript_origins_error, invalid_authorized_javascript_origins_error, authorized_javascript_origins_description, create_app, update_app, build_your_own_app, edit_app_details, regenerate_client_secret_description, regenerate_client_secret, regenerate_client_secret_confirm_title, regenerate_client_secret_confirm_description, regenerate_client_secret_confirm_cancel, regenerate_client_secret_confirm_regenerate, read_only_access_to_workspace, write_access_to_workspace, read_only_access_to_user_profile, write_access_to_user_profile, connect_app_to_workspace, user_permissions, user_permissions_description, workspace_permissions, workspace_permissions_description, with_the_permissions, app_consent_title, choose_workspace_to_connect_app_with, app_consent_workspace_permissions_title, app_consent_user_permissions_title, app_consent_accept_title, app_consent_accept_1, app_consent_accept_2, accepting, accept, categories, select_app_categories, categories_title, categories_error, invalid_categories_error, categories_description, supported_plans, supported_plans_description, select_plans, privacy_policy_url_title, privacy_policy_url_error, invalid_privacy_policy_url_error, terms_of_service_url_title, terms_of_service_url_error, invalid_terms_of_service_url_error, support_url_title, support_url_error, invalid_support_url_error, video_url_title, video_url_error, invalid_video_url_error, setup_url_error, invalid_setup_url_error, configuration_url_title, configuration_url_error, invalid_configuration_url_error, contact_email_title, contact_email_error, invalid_contact_email_error, upload_attachments, uploading_images, drop_images_here, click_to_upload_images, invalid_file_or_exceeds_size_limit, uploading, upload_and_save, app_consent_no_access_title, app_consent_no_access_description, app_consent_unapproved_title, app_consent_unapproved_description, go_to_app, enable_app_mentions, enable_app_mentions_tooltip, scopes, select_scopes, read_access_to, write_access_to, global_permission_expiration, selected_scopes, scopes_and_permissions, read, write, scope_description.projects, scope_description.wiki, scope_description.workspaces, scope_description.stickies, scope_description.profile, scope_description.agents, scope_description.assets
- `workspace_settings.settings.plane-intelligence` (3): title, heading, description
- `workspace_settings.settings.runners` (4): title, heading, new_script, description

#### `packages/i18n/src/locales/en/workspace.json` (66 Schlüssel)

- `workspace_analytics` (13): page_label, open_tasks, error, work_items_closed_in, selected_projects, total_members, total_cycles, total_modules, upgrade_to_plan, workitem_resolved_vs_pending, projects_by_status, active_users, intake_trends
- `workspace_analytics.pending_work_items` (2): title, empty_state
- `workspace_analytics.work_items_closed_in_a_year` (2): title, empty_state
- `workspace_analytics.most_work_items_created` (2): title, empty_state
- `workspace_analytics.most_work_items_closed` (2): title, empty_state
- `workspace_analytics.tabs` (2): scope_and_demand, custom
- `workspace_analytics.empty_state.project_insights` (2): title, description
- `workspace_analytics.empty_state.created_vs_resolved` (2): title, description
- `workspace_analytics.empty_state.customized_insights` (2): title, description
- `workspace_analytics.empty_state.general` (5): title, description, primary_button.text, primary_button.comic.title, primary_button.comic.description
- `workspace_analytics.empty_state.cycle_progress` (2): title, description
- `workspace_analytics.empty_state.module_progress` (2): title, description
- `workspace_analytics.empty_state.intake_trends` (2): title, description
- `workspace_cycles.empty_state.active` (2): title, description
- `workspace.members_import` (2): title, description
- `workspace.members_import.dropzone` (3): active, inactive, file_type
- `workspace.members_import.buttons` (5): cancel, import, try_again, close, done
- `workspace.members_import.progress` (2): uploading, importing
- `workspace.members_import.summary` (8): title.failed, title.complete, message.seat_limit, message.success, message.no_imports, stats.successful, stats.failed, download_errors
- `workspace.members_import.toast` (4): invalid_file.title, invalid_file.message, import_failed.title, import_failed.message

---

## Verifikations-Protokoll

> Skeptiker-/Verifikationslauf zum Cluster P01 (Stand 2026-10-22). Geprüft wurden (a) die Tier-Zuordnung gegen `apps/web/components/workspace/billing/comparison/plans.tsx` und die Schwester-Dokumente `migration/features/21-*.md` bis `28-*.md` (inkl. `_data/P02…P09.author.json` und der bereits verifizierten Liste `_data/P06.paid.json`), (b) der CE-Status per `grep`/Lesen im Repo `/home/user/plane`, (c) die Vollständigkeit des Clusters, (d) erfundene oder übertriebene Beschreibungen. Korrekturen sind direkt im Text vorgenommen und dort mit „(Verifikation)“ bzw. „(korrigiert)“ markiert. Die finale Feature-Liste liegt in `migration/features/_data/P01.paid.json`.

### V.1 Methode

| Prüfschritt | Vorgehen | Ergebnis |
|---|---|---|
| Matrix-Zählung | Python-Skript über `plans.tsx`: Feature-`title`-Zeilen ohne vorangehende `id`-Zeile, auskommentierte `// title:`-Zeilen, `comingSoon: true`-Zeilen | 87 aktive Zeilen, 4 auskommentierte, 15 × `comingSoon` (14 Zeilen + Sektion `integrations`) – Abschnitt 1.4 bestätigt; 76 Zeilen mit `free` ≠ `true` bestätigt (11 × `free: true`) |
| Matrix-Inhalt | `plans.tsx` vollständig gelesen (1 311 Zeilen) und gegen Abschnitt 2 abgeglichen | alle Zellwerte, Zeilennummern und Highlights korrekt übertragen; Rendering-Lücke ergänzt (Abschnitt 2, „Ergänzung (Verifikation)“) |
| Rendering | `base.tsx` Z. 26–32, 83–118; `feature-detail.tsx` | Beschreibungen, `selfHostedDescription`, `selfHostedOnly`, `cloudOnly` werden nicht gerendert/ausgewertet; Spalten Free/One ausgeblendet |
| i18n-Zahlen | Python-Zählung aller Blatt-Schlüssel in `packages/i18n/src/locales/en/*.json`; Stichprobe `de`/`fr`/`ja` für `automation.json`, `wiki.json` | 3 859 Schlüssel, 28 Namespaces × 22 Locales bestätigt; EE-Texte tatsächlich übersetzt (z. B. de „Benutzerdefinierte Automatisierungen“) |
| Stub-Suche | `find apps packages -iname '*extended*'`; ungenutzte `_props`; `return { items: [], modals: null }`; Kommentare `EE`/`CE` | 9 zusätzliche Extension-Points (S58–S66) |
| Endpunkt-Abgleich | Skript: alle `/api/…`-Literale aus `apps/web`, `apps/space`, `apps/admin`, `packages/services` gegen `path(...)`-Muster aller `apps/api/plane/**/urls*.py`; jeder Treffer per `grep` gegengeprüft (Include-Präfixe `api/`, `api/public/`, `api/instances/`, `api/v1/` aus `apps/api/plane/urls.py` berücksichtigt) | 5 zusätzliche EE-bezogene Gruppen fehlender Endpunkte (9.3, Gruppen 6–10) + 6 nicht EE-zuordenbare tote Aufrufe |
| Stichproben Detailaussagen | `IssueRelationChoices`, `NETWORK_CHOICES`, `IssueType`-Felder, `DeployBoard.TYPE_CHOICES`, `IntakeIssue.source*`, PQL-Ablehnung, Versionslimit 20, `useEditorFlagging`, `usePageFlag`, `useBulkOperationStatus`, `useWorkFlowFDragNDrop`, `CreateUpdateEpicModal`, `IssueTypeSwitcher`, `extended.service.ts` (Live), `extended_config_variables`, Upsell-Stellen U3/U12/U14–U18, `estimateCount`, `MAX_ESTIMATE_POINT_INPUT_LENGTH`, „Intake Form user“, `bulk_operations.upgrade_banner.cta` „Upgrade to One“, `SidebarUserMenu`/`SidebarWorkspaceMenu` nicht gerendert, Epic-URLs fehlen im Backend, `active-cycles` fehlt im Backend | alle bestätigt; Zeilenkorrektur `DeployBoard.TYPE_CHOICES` Z. 20–28 (statt 18–27) |
| WebSearch | 4 Suchen (Kontingent ≤ 15) | siehe V.2 |

### V.2 WebSearch im Verifikationslauf

| Nr. | Suchanfrage (sinngemäß) | Ergebnis (Zusammenfassung) | Verwendung |
|---|---|---|---|
| W-V1 | docs.plane.so customers Business plan | docs.plane.so/customers nennt keinen Plan; Plane University 202 „enable in Workspace Settings (Business tier)“; plane.so/business ohne Customers-Nennung | PF-41 → Business |
| W-V2 | plane.so pricing Pro „customer“ teamspaces wiki epics initiatives | Pro: Teamspaces und Wikis bestätigt; „customer profiles“ in Pro **nicht** bestätigt; Plane University ordnet Epics/Initiatives Business zu | PF-41, PF-14, PF-15 (Widerspruch dokumentiert) |
| W-V3 | docs.plane.so automations Business Enterprise Grid | keine Plan-Angabe in den Treffern; Trigger-/Aktionsbeschreibungen; Plane-Runner-Seite docs.plane.so/automations/plane-runner | PF-63/64/69 stützen sich daher auf das verifizierte Dok. 25 |
| W-V4 | docs.plane.so wiki collections Pro publish | „Collections Pro“, „Private collections need Business“, Plane-Guide „Wiki Pro and above“ | PF-74 → Pro; Private Collections Business |

Quellen: https://docs.plane.so/customers , https://university.plane.so/courses/202-the-power-relay/02-intro-to-customers.html , https://plane.so/business , https://plane.so/pricing , https://docs.plane.so/pages/collections , https://plane.so/blog/plane-wiki-and-pages-a-guide-to-team-documentation , https://docs.plane.so/automations/plane-runner .

### V.3 Korrekturen (vollständig)

| Nr. | Stelle | Vorher | Nachher | Beleg |
|---|---|---|---|---|
| K01 | PF-41 Customers – Tier | Pro | **Business** (Widerspruch dokumentiert) | W-V1, W-V2; Dok. 21 F04; Dok. 23 WM-16; Blog „Introducing Plane Business“ |
| K02 | PF-63 Custom Automations – Tier | Pro | **Business** (`plans.tsx` Pro als älterer Stand dokumentiert) | Dok. 25 F09 (verifiziert, `_data/P06.paid.json`) |
| K03 | PF-64 Globale Automationen – Tier | unklar | **Enterprise Grid** | Dok. 25 F13 |
| K04 | PF-67 Auto-Reminders – Tier | unklar | **Business** (nur Web-Beleg) | Dok. 25 |
| K05 | PF-69 Plane Runner – Tier | unklar | **Enterprise Grid** | Dok. 25 F19, Dok. 22 P03-F28 |
| K06 | PF-68 Workflows – Tier-Details | Pro-Angabe „single workflow per project“ als Beleg | Pro-Angabe UNVERIFIZIERT; Business = Default-Workflow, Enterprise Grid = mehrere typ-spezifische Workflows | Dok. 25 F01/F02, O21 |
| K07 | PF-74 Wiki – Tier | One | **Pro** (Widerspruch zu `plans.tsx` dokumentiert) | `wiki.upgrade_flow.description` „… with Plane Pro.“; `PRO_PLAN_FEATURES` „Wikis“; W-V4; Dok. 26 |
| K08 | PF-97 LDAP – Tier | Enterprise | **Enterprise Grid** (Synonym, Doku-Name) | `self-hosting/govern/ldap.md`; Dok. 22 P03-F07; Dok. 27 |
| K09 | PF-79 Page-Kommentare – Tier | unklar | Business (Inline-Kommentare; sekundär) | Dok. 26 |
| K10 | PF-80 Pages verschieben/teilen – Tier | unklar | Pro (Move) / Business (Sharing) (sekundär) | Dok. 26 |
| K11 | PF-81 Attachments/Embeds – Tier | unklar | Pro (sekundär) | Dok. 26 |
| K12 | PF-83 Importer – Tabelle | „Free (ohne Custom Props)“, Text „u. weitere“ | Pro (Free-Werte gelten nicht für die CE); Formulierung präzisiert | `plans.tsx` Z. 940–960; Dok. 28 |
| K13 | PF-98 IdP-Group-Sync – Tier | „Enterprise (Grid)“ | Enterprise Grid | Whitepaper (WebSearch Autor), Dok. 22/27 |
| K14 | PF-02 Bulk Ops – API-Hinweis | „im CE kein Bulk-Update-Endpunkt; EE-Endpunkt nicht öffentlich dokumentiert“ | Frontend-Vertrag `POST …/bulk-operation-issues/` mit `TBulkOperationsPayload` und Store-Semantik (Array-Werte anhängen) dokumentiert; Backend-Route fehlt | `apps/web/services/issue/issue.service.ts` Z. 339–345; `packages/types/src/issues/issue.ts` Z. 140–156; `apps/web/store/issue/helpers/base-issues.store.ts` Z. 718–753 |
| K15 | PF-09 – „Im CE vorhanden“ | nur Enum/Reverse-Mapping | zusätzlich funktionierende interne und Public-API-Endpunkte für alle vier Timeline-Relationen; Frontend-Schalter `isDependencyEnabled = false` | `apps/api/plane/app/views/issue/relation.py`; `apps/api/plane/api/serializers/issue.py` Z. 545–580; `apps/web/store/timeline/base-timeline.store.ts` Z. 85 |
| K16 | PF-12 – CE-Status | fehlt | teilweise im CE (manueller Transfer vorhanden) | `TransferCycleIssueEndpoint`, `apps/api/plane/app/views/cycle/base.py` Z. 599; konsistent mit `_data/P06.paid.json` |
| K17 | PF-23 – CE-Status | fehlt | Stub/UI-Hülle im CE (Enum + Activity-Text für nicht existierendes Feld) | `apps/web/components/common/activity/helper.tsx` Z. 67, 266–269 |
| K18 | PF-38 – CE-Status | fehlt | Stub/UI-Hülle im CE | `copy-menu-helper.tsx` (`createCopyMenuWithDuplication`) |
| K19 | PF-55 – CE-Status | entfällt | im CE vorhanden (nur Cloud-Gating); Limits entfallen | Rolle Guest `apps/api/plane/db/models/workspace.py` Z. 19; keine Seat-Logik (`grep -rni seat apps/api/plane` ohne Treffer außerhalb von Migrationen) |
| K20 | PF-58 – CE-Status | Stub/UI-Hülle im CE | teilweise im CE (Aktivität je Mitglied + CSV-Export) | `apps/api/plane/app/views/workspace/user.py` Z. 409–435; `apps/api/plane/app/views/workspace/base.py` Z. 340–361 |
| K21 | PF-71 Work-Item-Embeds – CE-Status | teilweise im CE | Stub/UI-Hülle im CE | Extension nicht registriert (`document-extensions.tsx`); konsistent mit Dok. 26 |
| K22 | PF-73 Publish Pages – CE-Status | teilweise im CE | Stub/UI-Hülle im CE | nur Choice in `DeployBoard`; Backend nutzt nur `entity_name="project"`; konsistent mit Dok. 26 |
| K23 | PF-81 – CE-Status | fehlt | Stub/UI-Hülle im CE | Extension-Points S15, S16, S48 |
| K24 | PF-83, PF-84, PF-86 – CE-Status | fehlt bzw. teilweise im CE | Stub/UI-Hülle im CE (Legacy-Modelle ohne View/URL, tote Service-Aufrufe) | `grep -rln "GithubRepository\|SlackProjectSync\|WorkspaceIntegration\|Importer" apps/api/plane` → nur Models, Serializer, Porter-Formatter; Dok. 28 |
| K25 | PF-93, PF-97 – CE-Status | fehlt | Stub/UI-Hülle im CE (Login-Extension-Points) | S17, S43, S52, S53; konsistent mit Dok. 27 |
| K26 | PF-100 – CE-Status | entfällt | teilweise im CE (Installationsskripte, AIO, Kubernetes, Swarm) | `deployments/cli/community/README.md` Z. 69, 77; `deployments/{aio,kubernetes,swarm}/community` |
| K27 | Neues Feature PF-104 Duplicate Detection | – | ergänzt (Stub/UI-Hülle im CE) | `packages/types/src/de-dupe.ts`; `apps/web/hooks/use-debounced-duplicate-issues.tsx`; Dok. 23 WM-47 |
| K28 | Neues Feature PF-105 Commercial-Produkte nur als Icon/Slug | nur in OP-09 erwähnt | als Inventar-Eintrag ergänzt (fehlt) | Propel-Icons; `RESTRICTED_URLS` |
| K29 | Abschnitt 6 – Stubs | 57 | 66 (S58–S66) | Abschnitt 6.3 |
| K30 | Abschnitt 9.3 – fehlende Endpunkte | 5 Gruppen | 10 EE-bezogene Gruppen + 6 nicht EE-zuordenbare Aufrufe | Abschnitt 9.3 |
| K31 | Abschnitt 9.1 | ohne `WorkspaceUserPreference.ACTIVE_CYCLES` | ergänzt | `apps/api/plane/db/models/workspace.py` Z. 417–427 |
| K32 | PF-82 | `rephrase-grammar/` als vorhandene Basis-AI dargestellt | Endpunkt fehlt im CE-Backend | `grep -rn rephrase apps/api/plane` ohne Treffer |
| K33 | PF-80 | nur Flags | Store `movePage` + Service `move` → fehlender Endpunkt `pages/{id}/move/` | `apps/web/store/pages/project-page.store.ts` Z. 352–369; `apps/web/services/page/project-page.service.ts` Z. 185–193 |
| K34 | PF-04 | – | Backend-Präferenz `active_cycles`, toter Aufruf `cycle-progress/`, Icon-Rotations-Inkonsistenz ergänzt | Abschnitt 4 PF-04 |
| K35 | Abschnitt 1.1 | „Alles mit `free: false` ist Bezahl-Feature“ | Ausnahmen Guests und One-click Deployment ergänzt | siehe K19, K26 |
| K36 | Abschnitt 2 Rendering | – | Hinweis: Beschreibungen und Self-hosted-Flags werden nicht gerendert | `base.tsx` Z. 83–118 |
| K37 | Vage Aufzählungen („u. a.“, „…“) in PF-05, PF-74 (Toasts), PF-83, U15, U16, U22, S13, S14, S20, S30, S47, S48, S50, 8.2 `RESTRICTED_URLS`, 8.2 Operator-Label-Maps, 8.3 `DocumentCollaborativeEvents`, PF-45 Widget-Keys | unvollständig | vollständige Listen bzw. ausdrücklich als „im Repo nicht benannt“ gekennzeichnet | jeweilige Quelldatei |
| K38 | Zeilenangabe `DeployBoard.TYPE_CHOICES` | Z. 18–27 | Z. 20–28 | `apps/api/plane/db/models/deploy_board.py` |
| K39 | PF-14, PF-15, PF-70, PF-71, PF-73, PF-03, PF-37, PF-98, PF-56, PF-93 | ohne Widerspruchshinweis | Widersprüche zu Schwester-Dokumenten bzw. Web-Quellen dokumentiert (Tier oder CE-Status), Entscheidung begründet | Abschnitt 3 und 4 |
| K40 | PF-103 – CE-Status | entfällt | Stub/UI-Hülle im CE (Upsell-/Billing-UI vorhanden), Migration entfällt | Abschnitt 5 (U3–U11) |

### V.4 Bestätigte Kernaussagen (Auswahl der geprüften Belege)

| Aussage | Beleg |
|---|---|
| CE kennt nur `InstanceEdition.PLANE_COMMUNITY` | `apps/api/plane/license/models/instance.py` |
| PQL/`filters` werden in der Public-API mit HTTP 400 abgelehnt | `apps/api/plane/api/views/issue.py` Z. 324–335 |
| Live-Server: `PageService` „Implementation for this is found in the enterprise repository.“ | `apps/live/src/services/page/extended.service.ts` Z. 12 |
| Versionslimit 20 je Page | `apps/api/plane/bgtasks/page_version_task.py` Z. 71–74; `apps/api/plane/bgtasks/cleanup_task.py` Z. 107 |
| `IssueRelationChoices` mit `start_before`, `finish_before`, `implemented_by` | `apps/api/plane/db/models/issue.py` Z. 272–290 |
| Projekt-Netzwerk nur `0` „Secret“ / `2` „Public“ | `apps/api/plane/db/models/project.py` Z. 71, 76 |
| `useEditorFlagging` deaktiviert `ai` und `collaboration-cursor` in allen Editoren | `apps/web/hooks/use-editor-flagging.ts` |
| Keine Epic-, Active-Cycles-, Integrations-Endpunkte im CE-Backend | `grep` in `apps/api/plane/app/urls` |
| `UpgradeBadge` in Projekt-Feature-Liste nur bei `isPro` (alle CE-Einträge `false`) | `apps/web/components/project/settings/features-list.tsx` Z. 37–73, 119–123 |

### V.5 Widersprüche zu Schwester-Dokumenten (dokumentiert, nicht aufgelöst)

| Feature | Dok. 20 (dieses) | Schwester-Dokument | Begründung der hier gewählten Angabe |
|---|---|---|---|
| Time Tracking (PF-03) – CE-Status | Stub/UI-Hülle | Dok. 21, Dok. 23 WM-32: teilweise | nur Flag ohne Funktion; Abgrenzungsregel Abschnitt 3 |
| Emails For Intake (PF-37) – CE-Status | Stub/UI-Hülle | Dok. 21, Dok. 22 P03-F23: teilweise; Dok. 23 WM-46: Stub | kein E-Mail-Eingang; Felder nur passiv |
| IdP-Group-Sync (PF-98) – CE-Status | fehlt | Dok. 21/22/27: Stub/UI-Hülle | nur Texte/Icons, kein Extension-Point |
| Advanced Search (PF-53) – CE-Status | fehlt | Dok. 22 P03-F11: teilweise | CE-Basissuche ist kein Teil von OpenSearch-Indexierung |
| Workspace-Identity (PF-93) – Tier | One (SAML/OIDC laut Matrix) | Dok. 22 P03-F06, Dok. 27: unklar | Matrix-Zeilen SAML/OIDC; Domain-Verifizierung selbst ohne Plan-Beleg (in tier_details vermerkt) |
| Plane AI (PF-82) – Tier | Pro (Cloud-Credits) | Dok. 22 P03-F12: unklar; Dok. 28: Pro | Cloud-Credits ab Pro (WebSearch Autor); Self-hosted nur „Commercial Edition“ |
| Epics (PF-14), Initiatives (PF-15) – Tier | Pro | Plane University: Business (über Dok. 21 und W-V2) | Matrix und Doku-Label Epics „Pro“; Konflikt dokumentiert |

### V.6 Verbleibende UNVERIFIZIERT-Punkte

- Pro-Zuordnung „customer profiles“ (frühere WebSearch-Zusammenfassung plane.so/pricing) – im Verifikationslauf nicht bestätigt.
- Pro-Angabe „single workflow per project“ (frühere WebSearch-Zusammenfassung) – nicht bestätigt.
- Tier-Angaben, die nur über Schwester-Dokumente aus Web-Quellen stammen und hier nicht selbst nachgesucht wurden: PF-64, PF-67, PF-69, PF-79, PF-80, PF-81, PF-63 (Business), PF-56 (Enterprise Grid für Approval-Flows).
- AI-Credits-Werte (Pro 1,000 je Seat/Monat; Business 2,000 aus Drittquelle) – nur Autoren-WebSearch.
- SCIM (PF-98) – nur WebSearch-Whitepaper und Dok. 27.
