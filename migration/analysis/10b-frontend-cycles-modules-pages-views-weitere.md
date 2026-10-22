# 10b – Frontend: Cycles, Modules, Pages, Views, Analytics, Intake, Estimates, Labels, States, Webhooks, API-Tokens, Exporter, Automation, Integrationen, Charts, Editor-Wrapper

> Analysebereich A10b · IST-Analyse des Originals (Plane v1.4.2 CE, Repo-Stand dieses Workspaces) als Spezifikation für den 1:1-Nachbau in Angular (ADR-005). Die verbindlichen Grundsatzentscheidungen stehen in `migration/architecture/00-grundsatzentscheidungen.md` (ADR-000 … ADR-006). Nach ADR-001 gibt es keine Planstufen: Upsell und Billing entfallen, Bezahlfunktionen werden gebaut.
>
> Konventionen:
> - Fließtext deutsch. Bezeichner, Pfade, Klassen, Endpunkte und UI-Texte stehen im Original; die UI-Texte sind englisch und aus `packages/i18n/src/locales/en/*.json` aufgelöst.
> - Pfade ohne Präfix in Tabellen beziehen sich auf das in der Abschnittsüberschrift genannte Verzeichnis unter `apps/web/components/`.
> - Tailwind-Klassen sind wörtlich übernommen. Querschnittsthemen (Routing, Stores, Services, Design-System, Editor-Kern, Work-Item-Layouts) stehen in den Analysen 08, 09, 11, 12, 13a und 13b und werden hier nur referenziert.

## Inhaltsverzeichnis

1. Überblick & Verantwortlichkeiten
2. Vollständige Inventare
   - 2.1 Cycles · 2.2 Workspace Active cycles · 2.3 Modules · 2.4 Pages · 2.5 Views
   - 2.6 Analytics · 2.7 Chart-Hilfen · 2.8 Intake
   - 2.9 Estimates · 2.10 Labels · 2.11 States
   - 2.12 Webhooks · 2.13 API-Tokens · 2.14 Exporter · 2.15 Automation · 2.16 Integrationen
   - 2.17 Editor-Wrapper · 2.18 Workflow-Stub
3. Verhalten/Logik/Abläufe
   - 3.1 Cycles · 3.2 Modules · 3.3 Pages · 3.4 Views · 3.5 Analytics/Charts · 3.6 Intake
   - 3.7 Estimates · 3.8 Labels · 3.9 States
   - 3.10 Webhooks · 3.11 API-Tokens · 3.12 Exporter · 3.13 Automation · 3.14 Integrationen
   - 3.15 Editor-Wrapper
4. Abhängigkeiten zu anderen Bereichen
5. Migrationshinweise für Angular
6. Offene Punkte

---

## 1. Überblick & Verantwortlichkeiten

### 1.1 Umfang

| Verzeichnis (`apps/web/components/…`) | Dateien (ts/tsx) | Zeilen | Verantwortung |
|---|---|---|---|
| `cycles/` | 44 | 4 452 | Cycle-Liste (aktiv/kommend/abgeschlossen), Inline-Dashboard des aktiven Cycles, Peek-/Detail-Sidebar mit Fortschritt und Burndown, Anlage/Bearbeitung, Transfer offener Work Items, Archiv, Löschen, Favoriten, Filter |
| `modules/` | 47 | 4 756 | Modul-Übersicht (Liste, Galerie, Timeline), Status, Lead/Mitglieder, Links, Fortschritt, Peek-/Detail-Sidebar, Archiv, Filter/Sortierung |
| `pages/` | 65 | 5 419 | Page-Liste (Public/Private/Archived), Editor-Seite mit Kopf, Toolbar, Navigationsbereich (Outline, Info, Assets), Versionen, Lock/Access/Archive, Export (PDF/Markdown), Duplizieren, Löschen |
| `views/` | 16 | 1 503 | Projekt-Views: Liste, Anlage/Bearbeitung mit Filtern, Lock, Veröffentlichung (Stub), Favoriten |
| `workspace/views/` (ergänzend) | 9 | 916 | Workspace-Views (Standard- und eigene Views), Anlage/Bearbeitung, Löschen |
| `analytics/` | 35 | 2 389 | Workspace-Analytics (Tabs Overview, Work items), Kennzahlen, Radar-/Area-/Bar-Charts, Insight-Tabellen, CSV-Export, Analytics-Panel für Projekt/Cycle/Modul |
| `chart/` | 1 | 178 | Datenaufbereitung und Farberweiterung für Charts |
| `inbox/` | 41 | 4 280 | Intake: Liste mit Tabs Open/Closed, Filter/Sortierung, Detail, Annehmen/Ablehnen/Snooze/Duplikat/Löschen, Anlage |
| `estimates/` | 23 | 1 868 | Schätzsysteme (Points, Categories; Time ausgeblendet): Anlage-Assistent, Aktivierung, Löschen |
| `labels/` | 10 | 1 197 | Projekt-Labels: zweistufige Hierarchie, Farben, Drag&Drop, Anlage/Bearbeitung/Löschen |
| `project-states/` | 16 | 1 183 | Projekt-States je Gruppe: Reihenfolge per Drag&Drop, Default, Anlage/Bearbeitung/Löschen |
| `web-hooks/` | 16 | 916 | Workspace-Webhooks: Liste, Anlage mit Secret, Detail, Regenerieren, Löschen |
| `api-token/` | 6 | 647 | Persönliche API-Tokens: Liste, Anlage mit Ablauf, Löschen |
| `exporter/` | 6 | 815 | Work-Item-Export (CSV/Excel/JSON) und Export-Historie |
| `automation/` | 4 | 507 | Projekt-Automationen Auto-Archive und Auto-Close |
| `integration/` | 3 | 387 | GitHub-/Slack-Integrationsbausteine (in CE unerreichbar) |
| `active-cycles/` | 1 | 136 | Upsell-Seite „Active cycles“ (Workspace) |
| `editor/` | 19 | 1 724 | Web-Wrapper um `@plane/editor` (Document, Rich Text, Lite Text, Sticky), Beschreibungs-Autosave, Mentions, PDF-Dokument |
| `workflow/` | 2 | 30 | CE-Stub für Workflow-Regeln beim Drag&Drop |
| **Summe** | **364** | **33 303** | |

Zusätzlich gelesen wurden die zugehörigen Routen unter `apps/web/app/(all)/[workspaceSlug]/…` sowie die Stores:
- `apps/web/store/cycle.store.ts`, `cycle_filter.store.ts`
- `module.store.ts`, `module_filter.store.ts`
- `pages/*`, `project-view.store.ts`, `global-view.store.ts`
- `inbox/*`, `estimates/*`, `label.store.ts`, `state.store.ts`
- `analytics.store.ts`, `workspace/webhook.store.ts`

Außerdem die Services und Hilfspakete, die in den Abschnitten jeweils genannt sind.

### 1.2 Verantwortlichkeiten und Abgrenzung

- Die Planungsobjekte Cycles und Modules sowie Views liefern Rahmen, Kopf, Sidebar und Verwaltungsdialoge. Die Work-Item-Darstellung darin (`CycleLayoutRoot`, `ModuleLayoutRoot`, `ProjectViewLayoutRoot`, `AllIssueLayoutRoot`) ist Gegenstand von Analyse 09.
- Pages liefern Liste, Seitenrahmen und alle Page-Aktionen. Editor-Kern, Kollaboration (Yjs/Hocuspocus), Stateless-Events und Live-Server stehen in Analyse 12.
- Die Einstellungsseiten für Estimates, Labels, States, Automations (Projekt) sowie Webhooks und Exports (Workspace) stammen aus diesem Bereich. Die API-Tokens liegen in den Profil-Einstellungen. Der Settings-Rahmen (Navigation, `SettingsContentWrapper`, `SettingsHeading`) ist in Analyse 08 beschrieben.
- Analytics und Charts nutzen die recharts-Wrapper aus `@plane/blocks/charts/*` (Analyse 13a §2.26).
- Bezahlfunktionen erscheinen in CE als Stubs, Upsell-Seiten oder ungenutzte Texte. Nach ADR-001 sind sie zu bauen; Abschnitt 5.5 listet sie.

### 1.3 Querschnittliche Muster dieses Bereichs

| Muster | Ausprägung | Belege |
|---|---|---|
| Rechte | Projektrolle Admin (20) / Member (15) / Guest (5) über `allowPermissions(...)`; Einstellungsseiten mit `NotAuthorizedView`; viele Buttons zusätzlich clientseitig ausgeblendet oder deaktiviert | jeweilige `page.tsx`; Berechtigungsabschnitte 3.1.9, 3.2.6, 3.4.6, Rechtematrix Pages 2.4.4 |
| Laden | SWR-Schlüssel je Seite (Einstellungsseiten: `PROJECT_ESTIMATES_<ws>_<pid>`, `PROJECT_STATES_<ws>_<pid>`, `WEBHOOKS_LIST_<ws>`, `WEBHOOK_DETAILS_<ws>_<id>`, `API_TOKENS_LIST`, `EXPORT_SERVICES_LIST(ws, cursor, per_page)`) plus MobX-Stores; die Schlüssel der übrigen Bereiche stehen in 2.1.4, 2.3.5, 2.4.5, 2.5.5, 2.8.5 und 3.5.1 | 2.9.1, 2.11.2, 2.12.1, 2.13.2, 2.14.2 |
| Optimismus | Stores aktualisieren lokal vor der Antwort; mehrere Rollbacks sind wirkungslos (State-Store) oder Fehler werden verschluckt (Intake-Store) | 3.6.7 I7, 3.9.3 S1 |
| Peek per Query | `?peekCycle=<id>`, `?peekModule=<id>`; Intake per `?inboxIssueId=<id>&currentTab=<tab>`; Pages `?paneTab=…`, `?version=<id>` | 2.1.5, 2.3.6, 2.4.6, 2.8.6 |
| Browser-Speicher | `cycle_sidebar_collapsed`, `module_sidebar_collapsed`, `activeCycleTab`, `cycle-analytics-tab-<id>`, `module-analytics-tab-<id>`, `cycle_tab`, `module_display_filters`, `module_filters`, `pages_config`, `IS_FAVORITE_MENU_OPEN`, `global_view_filters/<id>` | 2.1.5, 2.3.6, 2.4.6, 2.5.6 |
| Geheimnisse einmalig | Webhook-Secret und API-Token nur in der Create-/Regenerate-Antwort, sofortiger CSV-Download, danach nicht mehr abrufbar | 3.10, 3.11 |

---

## 2. Vollständige Inventare

### 2.1 Cycles (`apps/web/components/cycles/`, 44 Dateien, 4 452 Zeilen)

#### 2.1.1 Screens und Einstiegspunkte

| Screen / Dialog | Route bzw. Auslöser | Einstiegskomponente | Quelle |
|---|---|---|---|
| Cycle-Liste (Projekt) | `/:ws/projects/:projectId/cycles` | Page `ProjectCyclesPage` → `CycleAppliedFiltersList` (Header-Variante `TERNARY`, nur bei ≥1 Filter) + `CyclesView` | `apps/web/app/(all)/[workspaceSlug]/(projects)/projects/(detail)/[projectId]/cycles/(list)/page.tsx` |
| Cycle-Listen-Kopf | Layout-Header der Liste | `CyclesListHeader` (Breadcrumb Projekt › „Cycles“; rechts `CyclesViewHeader` + Button „Add cycle“ bzw. mobil „Add“; nur Admin/Member und wenn Projekt geladen) | `.../cycles/(list)/header.tsx` |
| Mobile-Kopf Liste | `< sm` | `CyclesListMobileHeader` (Menü „Layout“ mit „List layout“, „Gallery layout“; „Timeline layout“ wird per `if (layout.key == "gantt") return null` ausgeblendet) – setzt nur `cycleFilter.displayFilters.layout`, das von der Liste **nicht ausgewertet** wird | `.../cycles/(list)/mobile-header.tsx` |
| Aktiver Cycle (Inline-Dashboard) | erste Sektion der Liste | `ActiveCycleRoot` → `ActiveCycleProgress`, `ActiveCycleProductivity`, `ActiveCycleStats` | `active-cycle/root.tsx` |
| Cycle-Peek (rechte Leiste in Liste/Archiv) | Query `?peekCycle=<id>` | `CyclePeekOverview` → `CycleDetailsSidebar` | `cycle-peek-overview.tsx`, `analytics-sidebar/root.tsx` |
| Cycle-Detail (Work Items des Cycles) | `/:ws/projects/:projectId/cycles/:cycleId` | Page `CycleDetailPage`: `CycleLayoutRoot` (siehe Analyse 09) + rechte Leiste `CycleDetailsSidebar` (absolut, `w-[21.5rem]`, `z-13`, `shadow-raised-200`) | `.../cycles/(detail)/[cycleId]/page.tsx` |
| Cycle-Detail-Kopf | Layout-Header | `CycleIssuesHeader`: Breadcrumb Projekt › „Cycles“ › `CycleSelect variant="breadcrumb"` (alle 4 Status, nicht leerbar), Count-Badge mit Tooltip „There are N work items in this cycle“, `LayoutSelection` (List, Kanban, Calendar, Spreadsheet, Gantt; ab `@4xl`, sonst `MobileLayoutSelection`), `WorkItemFiltersToggle`, Dropdown „Display“ (`ignoreGroupedFilters=["cycle"]`), Button „Analytics“ (ab `@4xl`, sonst Icon `BarOutline`), „Add work item“ (nur wenn Cycle nicht `completed`), Sidebar-Toggle (`RightSidePaneOutline`, `aria-pressed`), `CycleQuickActions` | `.../cycles/(detail)/header.tsx` |
| Mobile-Kopf Detail | `< md` | `CycleIssuesMobileHeader`: „Layout“ (List/Kanban/Calendar), „Display“, „Analytics“ | `.../cycles/(detail)/mobile-header.tsx` |
| Cycle anlegen/bearbeiten | „Add cycle“ (über `useCommandPalette().toggleCreateCycleModal`), Empty-State-CTA, Kontextmenü „Edit“ | `CycleCreateUpdateModal` → `CycleForm` | `modal.tsx`, `form.tsx` |
| Cycle löschen | Kontextmenü „Delete“ | `CycleDeleteModal` (`ConfirmDialog`) | `delete-modal.tsx` |
| Cycle archivieren | Kontextmenü „Archive“ | `ArchiveCycleModal` (`ConfirmDialog variant="primary"`) | `archived-cycles/modal.tsx` |
| Work Items übertragen | Listeneintrag „Transfer N work items“ (abgeschlossener Cycle mit offenen Items) | `TransferIssuesModal` | `transfer-issues-modal.tsx`, `list/cycle-list-item-action.tsx` |
| Hinweisleiste „Completed cycles are not editable.“ + Button „Transfer work items“ | oberhalb der Work-Item-Layouts eines abgeschlossenen Cycles (`CycleLayoutRoot`) | `TransferIssues` | `transfer-issues.tsx`, `apps/web/components/issues/issue-layouts/roots/cycle-layout-root.tsx` |
| Archivierte Cycles | `/:ws/projects/:projectId/archives/cycles` | `ArchivedCyclesHeader` + `ArchivedCycleLayoutRoot` → `ArchivedCyclesView` → `CyclesList isArchived` | `archived-cycles/*`, `.../archives/cycles/page.tsx` |
| Workspace „Active cycles“ | `/:ws/active-cycles` | CE: Upsell `WorkspaceActiveCyclesUpgrade` (siehe 2.2) | `apps/web/components/active-cycles/workspace-active-cycles-upgrade.tsx` |

#### 2.1.2 Komponenten-Inventar

| Datei | Export | Zweck / Darstellung (Klassen, Texte en) | Wesentliche Abhängigkeiten |
|---|---|---|---|
| `cycles-view-header.tsx` | `CyclesViewHeader` | Suche + Filter im Listenkopf. Geschlossen: `IconButton ghost md` mit `SearchOutline` (`aria-label` „Search“). Offen: Container `ml-auto flex w-0 … transition-[width] ease-linear` → `w-64 border-subtle px-2.5 py-1.5 opacity-100`; Input Placeholder „Search“ (`max-w-[234px] text-13`), Close-Button (`CloseOutline h-3 w-3`) leert Suche und schließt. `FiltersDropdown` (Icon `FilterOutline h-3 w-3`, Titel „Filters“, `placement="bottom-end"`, Punkt-Markierung bei aktiven Filtern) mit `CycleFiltersSelection` | `useCycleFilter`, `useOutsideClickDetector` (schließt bei leerer Suche), `FiltersDropdown` aus `components/issues/issue-layouts/filters` |
| `cycles-view.tsx` | `CyclesView` | Berechnet `filteredCycleIds = getFilteredCycleIds(projectId,false)`, `filteredCompletedCycleIds`, `filteredUpcomingCycleIds = filteredCycleIds − currentProjectActiveCycleId`. Loader `CycleModuleListLayoutLoader`; leer (beide Listen 0) → Bild (`cycle/all-filters.svg` bzw. bei Suche `cycle/name-filter.svg`, `h-36 w-36 sm:h-48 sm:w-48`), „No matching cycles“, „Remove the filters to see all cycles“ / „Remove the search criteria to see all cycles“ | `useCycle`, `useCycleFilter` |
| `list/root.tsx` | `CyclesList` | `ContentWrapper variant=HUGGING flex-row` → `ListLayout` (scrollbar-lg) + `CyclePeekOverview`. Nicht-Archiv: `ActiveCycleRoot`, Collapsible „Upcoming cycle“ (Default offen) und „Completed cycle“ (Default **geschlossen**, `pb-7`); Trigger `sticky top-0 z-[2] border-b bg-layer-1`. Archiv: flache Liste | `@base-ui/react/collapsible`, `ContentWrapper`, `ListLayout` |
| `list/cycles-list-map.tsx` | `CyclesListMap` | rendert `CyclesListItem` je ID | – |
| `list/cycles-list-item.tsx` | `CyclesListItem` | `ListItem` mit Link `/${ws}/projects/${pid}/cycles/${id}`; Präfix: Kreis-Fortschritt `CircularProgress size="md"` (`scale-150` in `size-[30px]`), `variant` `success` bei 100 % sonst `brand`, Mitte `TickOutline h-3 w-3` bzw. `${progress}%` (`text-9`). Archivierte Cycles: Klick öffnet Peek statt Navigation. Mobil-Quick-Actions (`md:hidden`) | `calculateCycleProgress`, `ListItem`, `CycleListItemAction`, `CycleQuickActions` |
| `list/cycle-list-item-action.tsx` | `CycleListItemAction` | Rechte Aktionszeile: „More details“ (`ShowOutline`, `text-11 text-accent-secondary`; sichtbar mobil, beim aktiven Cycle ohne offenen Peek, sonst `hidden group-hover:flex`) → Peek-Toggle; bei Status `draft`/`upcoming` Work-Item-Zahl (`WorkItemsOutline`); bei `completed` und offenen Items Link „Transfer {count} work items“ (`TransferWorkItemOutline`); aktiver Cycle: Datumsanzeige `MergedDateDisplay` + Tooltip „In your timezone: …“ (nur bei abweichender Projekt-TZ) + UTC-Offset-Chip + Ersteller-Avatar; sonst: `DateRangeSelect` (disabled, `select-ghost-md`, Placeholder „Start date - End date“), Ersteller-Avatar, Mitglieder (`AvatarGroup xs max=2`, Tooltip „N Members“, leer `MembersOutline`); `FavoriteStar` (nur Admin/Member, nicht archiviert); Desktop-Quick-Actions (`hidden md:block`) | `useCycle`, `useMember`, `useUserPermissions`, `useTimeZoneConverter`, `useLocalStorage(IS_FAVORITE_MENU_OPEN)`, `TransferIssuesModal`, `setPromiseToast` |
| `list/cycle-list-group-header.tsx` | `CycleListGroupHeader` | Gruppenzeile `Row py-2.5`: `CycleGroupIcon` (`h-5 w-5`), Titel (`font-medium text-primary`), optional Zähler (`pl-2 text-13 text-tertiary`), Chevron `ChevronDownOutline` mit `rotate-180` wenn offen | `@plane/blocks/icons` |
| `list/cycle-list-project-group-header.tsx` | `CycleListProjectGroupHeader` | Projekt-Gruppenzeile (Chevron rechts, `rotate-90` offen, Projekt-`Logo` 16 px, Name, Zähler). **In CE nicht verwendet** (Vorlage für Workspace-Cycle-Liste) | `useProject` |
| `list/index.ts` | Re-Export `root` | – | – |
| `cycle-peek-overview.tsx` | `CyclePeekOverview` | Rechte Leiste bei `?peekCycle`: `fixed right-0 z-[9] h-full w-full max-w-[21.5rem] … md:relative`, Box-Shadow `0px 1px 4px 0px rgba(0,0,0,0.06), 0px 2px 4px 0px rgba(16,24,40,0.06), 0px 1px 8px -1px rgba(16,24,40,0.06)`; lädt Details (`fetchCycleDetails` bzw. `fetchArchivedCycleDetails`) | `useCycle`, `generateQueryParams` |
| `quick-actions.tsx` | `CycleQuickActions` | „…“-Menü (`IconButton tertiary md`, `MoreHorizontalOutline`, `aria-label` „Options“) + gleichlautendes Rechtsklick-`ContextMenu` auf `parentRef`; Einträge aus `useCycleMenuItems` (siehe 2.1.3); hostet Edit-, Archiv-, Lösch-Modal in `div.fixed` | `components/common/quick-actions-helper.tsx`, `quick-actions-factory.tsx`, `@plane/blocks/context-menu`, `@makeplane/propel/components/menu` |
| `modal.tsx` | `CycleCreateUpdateModal` | `Dialog` `size="md"`, `disablePointerDismissal` (Klick außerhalb schließt nicht, Escape schon) → `CycleForm`; Datumsprüfung, Toasts, SWR-Mutate aktiver Cycle | `CycleService.cycleDateCheck`, `useCycle`, `useLocalStorage("cycle_tab")` |
| `form.tsx` | `CycleForm` | Formular (react-hook-form): Kopf mit `ProjectSelect pill-md` (nur Anlage, nur Projekte mit Anlegerecht) + Titel „Create cycle“/„Update cycle“ (`text-18 font-medium text-secondary`); Feld Titel (`Input size="2xl"`, Placeholder „Title“, `autoFocus`, Pflicht, max 255); Beschreibung (`TextArea lg autoResize maxRows=8`, Placeholder „Description“); `DateRangeSelect pill-md h-7` (Placeholder „Start date - End date“, `minDate = heute`, `weekStartsOn` aus Profil); Footer `border-t-[0.5px] px-5 py-4`: „Cancel“ (secondary), Submit („Create cycle“/„Creating…“ bzw. „Update cycle“/„Updating…“) | `ProjectSelect`, `getTabIndex(ETabIndices.PROJECT_CYCLE)` |
| `delete-modal.tsx` | `CycleDeleteModal` | `ConfirmDialog` Titel „Delete cycle“, Text „Are you sure you want to delete cycle "<Name>"? All of the data related to the cycle will be permanently removed. This action cannot be undone.“ | `useCycle.deleteCycle`, `PROJECT_ERROR_MESSAGES` |
| `transfer-issues-modal.tsx` | `TransferIssuesModal` | `Dialog size="sm"`; Titel „Transfer work items“ mit `TransferWorkItemOutline`; Suchfeld „Search for a cycle...“; Liste der unvollständigen Cycles des Projekts (Button je Cycle: `CyclesOutline h-5 w-5`, Name, Status-Pill `capitalize bg-layer-1 rounded-full`); leer: „You don’t have any current cycle. Please create one to transfer the work items.“; `undefined` → „Loading...“ | `useCycle.currentProjectIncompleteCycleIds`, `useIssues(CYCLE).transferIssuesFromCycle` |
| `transfer-issues.tsx` | `TransferIssues` | Leiste `-mt-2 mb-4 px-4 pt-6`: `WarningCircleOutline` + „Completed cycles are not editable.“; optional Button „Transfer work items“ (primary, Icon start) | – |
| `active-cycle/root.tsx` | `ActiveCycleRoot`, intern `ActiveCyclesComponent` | Collapsible „Active cycle“ (Default offen, Icon `type="current"`); ohne aktiven Cycle `EmptyStateDetailed assetKey="cycle"` „No active cycle“ + Beschreibung; mit Cycle: Listeneintrag (`!border-b-transparent`) + Grid `grid-cols-1 gap-3 lg:grid-cols-2 xl:grid-cols-3` mit drei Karten | `useCyclesDetails`, `next-themes` |
| `active-cycle/use-cycles-details.ts` | `useCyclesDetails` (default) | Lädt per SWR Fortschritt, Verteilungen (issues/points) und Prioritäts-Items des Cycles; liefert `handleFiltersUpdate(conditions)` → setzt Rich-Filter des Cycle-Work-Item-Stores und navigiert zur Cycle-Detailseite | `useIssues(CYCLE)`, `useWorkItemFilters`, `CYCLE_ISSUES_WITH_PARAMS` |
| `active-cycle/progress.tsx` | `ActiveCycleProgress` | Karte „Progress“ (`min-h-[17rem] rounded-lg border px-3.5 py-4`): Text „X/Y Work items closed“ (X = completed+cancelled, Y = total−cancelled; Singular „Work item“ wenn X ≤ 1), `LinearProgress md brand`; Zeilen je Gruppe `completed`, `started`, `unstarted`, `backlog` (nur > 0) mit Farbpunkt aus `PROGRESS_STATE_GROUPS_DETAILS[index]` (#16A34A, #F59E0B, #3A3A3A, #A3A3A3) und „N Work items“; Klick → Filter `state_group in [group]`; Hinweis „N cancelled work items are excluded from this report.“; leer: Bild + „Add work items to the cycle to view it's progress“ | `LinearProgress`, `SimpleEmptyState` |
| `active-cycle/productivity.tsx` | `ActiveCycleProductivity` | Karte „Work item burndown“ (Link zur Detailseite) + `EstimateTypeDropdown`; Kopfzeile „Pending points - N“ bzw. „Pending work items - N“ (backlog+unstarted+started); `ProgressChart` mit `plotTitle` „points“/„work items“; leer: „Add work items to the cycle to view the burndown chart.“ | `ProgressChart` (`components/core/sidebar/progress-chart.tsx`) |
| `active-cycle/cycle-stats.tsx` | `ActiveCycleStats` | Karte mit `Tabs variant="contained" stretch="full"`: „Priority work items“ (`Priority-Issues`), „Assignees“, „Labels“; Tab in `localStorage["activeCycleTab"]` (Default „Assignees“). Priority-Tab: Liste (`h-52`, Endlos-Laden per IntersectionObserver, Loader-Zeile `h-11 animate-pulse`) mit `IssueIdentifier xs`, Name (Tooltip „Title: …“), `PriorityIcon`, `StateSelect pill-sm disabled`, Zieltermin-Chip (Tooltip „Target Date: …“). Klick → Peek **und** Filter `priority in [urgent,high]` (navigiert zur Detailseite). Assignees-/Labels-Tab: `SingleProgressStats` je Eintrag (Klick filtert `assignee_id`/`label_id`; „No assignee“ mit Platzhalterbild `user.png`, „No labels“ ohne Klick) | `useIssueDetail.setPeekIssue`, `useIntersectionObserver`, `SingleProgressStats` |
| `analytics-sidebar/root.tsx` | `CycleDetailsSidebar` | Rahmen: Loader (2 Zeilen 15 px, 3 Zeilen 30 px) solange Cycle fehlt; dann `CycleSidebarHeader`, `CycleSidebarDetails`, `CycleAnalyticsProgress` | `useCyclesDetails` |
| `analytics-sidebar/sidebar-header.tsx` | `CycleSidebarHeader` | Sticky-Kopf mit rundem Schließen-Button (`ChevronRightOutline`, `bg-layer-3`); Name `text-18 font-semibold`; Status-Badge (Farbe aus `CYCLE_STATUS.color`, Hintergrund `${color}20`, Text „In progress“/„Yet to start“/„Completed“/„Draft“); `DateRangeSelect pill-sm` (bearbeitbar für Admin/Member, nicht archiviert, nicht abgeschlossen; `minDate = heute`) + UTC-Offset-Chip | `CycleService.cycleDateCheck`, `useCycle.updateCycleDetails` |
| `analytics-sidebar/sidebar-details.tsx` | `CycleSidebarDetails` | Beschreibung (`TextArea inline disabled autoResize`); Eigenschaftszeilen (Label `w-2/5`, Wert `w-3/5`): „Lead“ (Owner-Avatar + Name), „Members“ (`AvatarGroup max=2` oder „No assignee“), „Work items“ („completed/total“ bzw. „0 Work item“; bei abgeschlossenem Cycle aus `progress_snapshot`), „Points“ (nur Schätzsystem `points` und nicht abgeschlossen) | `useProjectEstimates`, `useMember` |
| `analytics-sidebar/issue-progress.tsx` | `CycleAnalyticsProgress`, Konstanten `cycleEstimateOptions`, `cycleChartOptions`, Funktion `validateCycleSnapshot` | Abschnitt „Progress“ (Collapsible, Default offen, nur bei gültigen Daten; sonst statisch); ohne Start/Ende „No Data yet“; enthält `SidebarChart` und `CycleProgressStats` | `useWorkItemFilters.getFilter/updateFilterValueFromSidebar` |
| `analytics-sidebar/sidebar-chart.tsx` | `SidebarChart` | `EstimateTypeDropdown` + `ProgressChart` (Loader `h-[160px]`); Wechsel des Schätztyps lädt Cycle-Details neu, bei Fehler Rücksetzung | `useCycle.setEstimateType` |
| `analytics-sidebar/progress-stats.tsx` | `CycleProgressStats` | Tabs „States“/„Assignees“/„Labels“ (`PROGRESS_STATS`, Keys `stat-states`, `stat-assignees`, `stat-labels`), Tab in `localStorage["cycle-analytics-tab-<cycleId>"]` (Default `stat-assignees`); Inhalte `StateGroupStatComponent`, `AssigneeStatComponent`, `LabelStatComponent` mit Auswahl-Highlight (`bg-layer-1`) | `components/core/sidebar/progress-stats/*` |
| `analytics-sidebar/index.ts` | Re-Export `root` | – | – |
| `dropdowns/estimate-type-dropdown.tsx` | `EstimateTypeDropdown` | `Select` (ohne Suche) mit Optionen „Work items“ (`issues`) / „Estimates“ (`points`); Trigger `select-md rounded-sm border-none bg-surface-2 text-13 font-medium`; nur sichtbar, wenn Punktedaten vorhanden **oder** Projekt-Schätzung aktiv **und** Schätzsystem ≠ `categories`; sonst optional Text (`showDefault`) | `useProjectEstimates`, `useCycle.getIsPointsDataAvailable` |
| `dropdowns/filters/root.tsx` | `CycleFiltersSelection` | Filter-Panel: Suchfeld (`text-11`, `autoFocus` außer mobil, Clear-Button), Sektionen „Status of the cycle“ (nicht im Archiv), „Start date“, „Due date“ | `FilterHeader`, `FilterOption` |
| `dropdowns/filters/status.tsx` | `FilterStatus` | Optionen aus `CYCLE_STATUS` (In progress, Yet to start, Completed, Draft), Einfachklick toggelt; Suche matcht auf `value`; „No matches found“ | `CYCLE_STATUS` |
| `dropdowns/filters/start-date.tsx` | `FilterStartDate` | Presets `DATE_AFTER_FILTER_OPTIONS` („1 week from now“, „2 weeks from now“, „1 month from now“, „2 months from now“) + „Custom“ (öffnet `DateFilterModal` Titel „Start date“); Header-Zähler „Start date (N)“ | `DateFilterModal` |
| `dropdowns/filters/end-date.tsx` | `FilterEndDate` | identisch, Titel „Due date“ | `DateFilterModal` |
| `dropdowns/filters/index.ts`, `dropdowns/index.ts` | Re-Exports | – | – |
| `applied-filters/root.tsx` | `CycleAppliedFiltersList` | Chips je Filterschlüssel (`min-h-9 rounded-md border p-1.5 text-11 capitalize`), Schlüsselname via `replaceUnderscoreIfSnakeCase`, Werte, „x“ je Schlüssel, Pill „Clear all“ (`Pill size="md" variant="outline"`); Bearbeitung nur Admin/Member oder `alwaysAllowEditing` | `useUserPermissions` |
| `applied-filters/status.tsx` | `AppliedStatusFilters` | Status-Chip mit `bgColor`/`textColor` aus `CYCLE_STATUS` | `CYCLE_STATUS` |
| `applied-filters/date.tsx` | `AppliedDateFilters` | Datums-Chip: Preset-Name oder „After <Datum>“/„Before <Datum>“ (`capitalizeFirstLetter(time)` + `renderFormattedDate`) | `DATE_AFTER_FILTER_OPTIONS` |
| `applied-filters/index.ts` | Re-Export | – | – |
| `archived-cycles/header.tsx` | `ArchivedCyclesHeader` | `ArchiveTabsList` (Tabs Work items/Cycles/Modules) + Suche (eigener Query `archivedCyclesSearchQuery`) + „Filters“ (ohne Status) | `components/archives` |
| `archived-cycles/root.tsx` | `ArchivedCycleLayoutRoot` | SWR `ARCHIVED_CYCLES_${ws}_${pid}`; Applied-Filters-Leiste (`border-b px-5 py-3`); leer: `EmptyStateDetailed assetKey="archived-cycle"` „No archived cycles yet“ / „To tidy up your project, archive completed cycles. Find them here once archived.“ | `useCycle.fetchArchivedCycles` |
| `archived-cycles/view.tsx` | `ArchivedCyclesView` | gefilterte Archivliste; leer → Bild + „No matching cycles“ (hart kodiert en) | `getFilteredArchivedCycleIds` |
| `archived-cycles/modal.tsx` | `ArchiveCycleModal` | `ConfirmDialog` Titel „Archive cycle <Name>“, Text „Are you sure you want to archive the cycle? All your archives can be restored later.“, Buttons „Archive“/„Archiving“, „Cancel“ | `useCycle.archiveCycle` |
| `archived-cycles/index.ts` | Re-Export | – | – |

#### 2.1.3 Kontextmenü Cycle (`useCycleMenuItems`, `apps/web/components/common/quick-actions-helper.tsx`)

Reihenfolge fest; Icons aus `quick-actions-factory.tsx`.

| # | Key | Text | Icon | sichtbar wenn | disabled / Beschreibung | Aktion |
|---|---|---|---|---|---|---|
| 1 | `edit` | „Edit“ | `EditOutline` | Admin/Member **und** nicht `completed` **und** nicht archiviert | – | `CycleCreateUpdateModal` mit Daten |
| 2 | `open-new-tab` | „Open in new tab“ | `NewTabOutline` | immer | – | `window.open("/${ws}/projects/${pid}/cycles/${id}", "_blank")` |
| 3 | `copy-link` | „Copy link“ | `LinkOutline` | immer | – | `copyUrlToClipboard("${ws}/projects/${pid}/cycles/${id}")` → Toast „Link copied!“ / „Link copied to clipboard“ |
| 4 | `archive` | „Archive“ | `ArchiveOutline` | Admin/Member und nicht archiviert | disabled, wenn nicht `completed`; Beschreibung „Only completed cycles can be archived“ | `ArchiveCycleModal` |
| 5 | `restore` | „Restore“ | `RestoreOutline` | Admin/Member und archiviert | – | `restoreCycle` → Toast „Cycle restored“/„The cycle has been restored.“ → Push `/${ws}/projects/${pid}/archives/cycles`; Fehler „Cycle restore failed“ |
| 6 | `delete` | „Delete“ | `DeleteOutline` | Admin/Member und nicht `completed` und nicht archiviert | – | `CycleDeleteModal` |

#### 2.1.4 Store, Services, Endpunkte (Cycles)

| Aufruf (Frontend) | HTTP | Endpunkt | Auslöser |
|---|---|---|---|
| `CycleService.getCyclesWithParams(ws,pid)` | GET | `/api/workspaces/{ws}/projects/{pid}/cycles/` | `fetchAllCycles` (Projekt-Bootstrap) |
| `getCyclesWithParams(ws,pid,"current")` | GET | `/api/workspaces/{ws}/projects/{pid}/cycles/?cycle_view=current` | `fetchActiveCycle` (Fehlerpfad Update) |
| `getWorkspaceCycles` | GET | `/api/workspaces/{ws}/cycles/` | `fetchWorkspaceCycles` |
| `getCycleDetails` | GET | `/api/workspaces/{ws}/projects/{pid}/cycles/{cid}/` | Peek, Detail, nach Patch |
| `createCycle` | POST | `/api/workspaces/{ws}/projects/{pid}/cycles/` | Formular |
| `patchCycle` | PATCH | `/api/workspaces/{ws}/projects/{pid}/cycles/{cid}/` | Formular, Sidebar-Datum |
| `deleteCycle` | DELETE | `/api/workspaces/{ws}/projects/{pid}/cycles/{cid}/` | Lösch-Dialog |
| `cycleDateCheck` | POST | `/api/workspaces/{ws}/projects/{pid}/cycles/date-check/` Body `{start_date,end_date[,cycle_id]}` → `{status:boolean}` | Formular, Sidebar-Datum |
| `workspaceActiveCyclesProgress` | GET | `/api/workspaces/{ws}/projects/{pid}/cycles/{cid}/progress/` | `useCyclesDetails`, Transfer |
| `workspaceActiveCyclesAnalytics` | GET | `/api/workspaces/{ws}/projects/{pid}/cycles/{cid}/analytics?type=issues\|points` | `useCyclesDetails` (nur wenn `distribution` bzw. `estimate_distribution` fehlt) |
| `workspaceActiveCyclesProgressPro` | GET | `/api/workspaces/{ws}/projects/{pid}/cycles/{cid}/cycle-progress/` | CE: `fetchActiveCycleProgressPro` ist leer, wird nicht aufgerufen |
| `getCycleIssues` | GET | `/api/workspaces/{ws}/projects/{pid}/cycles/{cid}/cycle-issues/?priority=urgent,high&cursor=30:0:0&per_page=30` | Priority-Tab (Folgeseiten über `fetchNextActiveCycleIssues`) |
| `transferIssues` | POST | `/api/workspaces/{ws}/projects/{pid}/cycles/{cid}/transfer-issues/` Body `{new_cycle_id}` | Transfer-Dialog |
| Favorit (über `FavoriteStore.addFavorite`) | POST | `/api/workspaces/{ws}/user-favorites/` Body `{entity_type:"cycle", entity_identifier, project_id, entity_data:{name}}` | Stern |
| Favorit entfernen (`FavoriteStore.removeFavoriteEntity` → `deleteFavorite`) | DELETE | `/api/workspaces/{ws}/user-favorites/{favoriteId}/` (Favorit wird über `entity_identifier` gesucht) | Stern |
| `CycleArchiveService.getArchivedCycles` | GET | `/api/workspaces/{ws}/projects/{pid}/archived-cycles/` | Archivseite |
| `getArchivedCycleDetails` | GET | `/api/workspaces/{ws}/projects/{pid}/archived-cycles/{cid}/` | Peek im Archiv |
| `archiveCycle` | POST | `/api/workspaces/{ws}/projects/{pid}/cycles/{cid}/archive/` → `{archived_at}` | Archiv-Dialog |
| `restoreCycle` | DELETE | `/api/workspaces/{ws}/projects/{pid}/cycles/{cid}/archive/` | „Restore“ |
| `workspaceActiveCycles` | GET | `/api/workspaces/{ws}/active-cycles/` | in CE ungenutzt (Workspace-Active-Cycles) |

Quellen: `apps/web/services/cycle.service.ts`, `apps/web/services/cycle_archive.service.ts`, `apps/web/store/cycle.store.ts`, `apps/web/store/issue/cycle/issue.store.ts`.

#### 2.1.5 Clientseitige Zustände (Cycles)

| Zustand | Ort | Persistenz | Inhalt |
|---|---|---|---|
| `cycleFilter.filters[projectId].default / .archived` | `apps/web/store/cycle_filter.store.ts` | nur Speicher (Reset bei Reload) | `TCycleFilters` `{status?, start_date?, end_date?}` (Arrays) |
| `cycleFilter.searchQuery`, `archivedCyclesSearchQuery` | dito | Speicher; `searchQuery` wird bei Projektwechsel geleert | Freitext (Name, `includes`, case-insensitiv) |
| `cycleFilter.displayFilters[projectId]` | dito | Speicher | `{active_tab: "active", layout: "list"}` (in CE ohne Wirkung auf die Liste) |
| `cycle.plotType[cycleId]` | `cycle.store.ts` | Speicher | `burndown` (Default) / `burnup` – kein UI-Schalter in CE |
| `cycle.estimatedType[cycleId]` | `cycle.store.ts` | Speicher | `issues` / `points`; wird ignoriert (immer `issues`), wenn Projekt keine Schätzung aktiv hat |
| `localStorage["cycle_sidebar_collapsed"]` | Detailseite/Header | localStorage (bool) | Sidebar zu/auf; Default `false` (= offen) |
| `localStorage["activeCycleTab"]` | `active-cycle/cycle-stats.tsx` | localStorage | „Priority-Issues“/„Assignees“/„Labels“ (Default „Assignees“) |
| `localStorage["cycle-analytics-tab-<id>"]` | `analytics-sidebar/progress-stats.tsx` | localStorage | `stat-states`/`stat-assignees`/`stat-labels` |
| `localStorage["cycle_tab"]` | `modal.tsx` | localStorage | wird nach Anlage auf `"all"` gesetzt (Altlast ohne Leser) |
| `localStorage[IS_FAVORITE_MENU_OPEN]` | `cycle-list-item-action.tsx` | localStorage | Favoriten-Sektion der Sidebar nach Favorisieren aufklappen |
| Query `peekCycle` | URL | URL | ID des Cycles im Peek |

### 2.2 Workspace „Active cycles“ (`apps/web/components/active-cycles/`, 1 Datei, 136 Zeilen)

| Screen | Route | Inhalt | Quelle |
|---|---|---|---|
| Workspace-Active-Cycles | `/:ws/active-cycles` (Sidebar-Eintrag `active-cycles`, Icon um 180° gedreht, `apps/web/components/workspace/sidebar/workspace-menu.tsx`) | Kopf `WorkspaceActiveCycleHeader`: Breadcrumb „Active cycles“ (`CyclesOutline rotate-180`) + `UpgradeBadge size="md"`; Seite `WorkspaceActiveCyclesPage` (Titel `<Workspace> - Active Cycles`) rendert nur `WorkspaceActiveCyclesUpgrade` | `apps/web/app/(all)/[workspaceSlug]/(projects)/active-cycles/{page,header,layout}.tsx`, `workspace-active-cycles-upgrade.tsx` |

| Element | Darstellung | Texte (en) |
|---|---|---|
| Hero-Banner | `ContentWrapper gap-10`; Banner `min-h-[25rem] rounded-xl`, Verlauf dunkel `from-[#CFCFCF] to-[#212121]`, hell `from-[#3b5ec6] to-[#f5f7fe]` (abhängig von `userProfile.theme.theme`); links Text `px-14 lg:w-1/2`, rechts (ab `lg`) drei Illustrationen `ctaL1`, `ctaR1`, `ctaR2` je Theme | Titel „On-demand snapshots of all your cycles“, Text „Monitor cycles across projects, track high-priority work items, and zoom in cycles that need attention.“ |
| Upgrade-Button | `Button primary sm` mit `ProIcon`, rendert Link auf `MARKETING_PRICING_PAGE_LINK` (`target="_blank"`) | „Upgrade“ |
| Feature-Kacheln | Grid `grid-cols-1 lg:grid-cols-2 xl:grid-cols-3`, Kachel `min-h-32 rounded-md bg-layer-1 p-4`, Icon `text-blue-500` | `10000_feet_view` „10,000-feet view of all active cycles.“ / „Zoom out to see running cycles across all your projects at once instead of going from Cycle to Cycle in each project.“ · `get_snapshot_of_each_active_cycle` „Get a snapshot of each active cycle.“ / „Track high-level metrics for all active cycles, see their state of progress, and get a sense of scope against deadlines.“ · `compare_burndowns` „Compare burndowns.“ / „Monitor how each of your teams are performing with a peek into each cycle's burndown report.“ · `quickly_see_make_or_break_issues` „Quickly see make-or-break work items.“ / „Preview high-priority work items for each cycle against due dates. See all of them per cycle in one click.“ · `zoom_into_cycles_that_need_attention` „Zoom into cycles that need attention.“ / „Investigate the state of any cycle that doesn't conform to expectations in one click.“ · `stay_ahead_of_blockers` „Stay ahead of blockers.“ / „Spot challenges from one project to another and see inter-cycle dependencies that aren't obvious from any other view.“ |

Die Konstante `WORKSPACE_ACTIVE_CYCLES_DETAILS` enthält zusätzlich englische `title`/`description`-Literale. Gerendert werden aber die i18n-Schlüssel `t(item.key)` und `t(`${item.key}_description`)`. Nach ADR-001 (keine Planstufen) entfällt die Upsell-Seite. An ihre Stelle tritt die echte Workspace-Übersicht aller aktiven Cycles; deren Spezifikation steht in `migration/features/24-paid-planung-insights-teams.md` §3.4.

### 2.3 Modules (`apps/web/components/modules/`, 47 Dateien, 4 756 Zeilen)

#### 2.3.1 Screens und Einstiegspunkte

| Screen / Dialog | Route bzw. Auslöser | Einstiegskomponente | Quelle |
|---|---|---|---|
| Modul-Übersicht (List/Gallery/Timeline) | `/:ws/projects/:projectId/modules` | Page `ProjectModulesPage` → `ModuleAppliedFiltersList` (bei ≥1 Filter oder Favoriten-Filter, `alwaysAllowEditing`) + `ModulesListView` | `apps/web/app/(all)/[workspaceSlug]/(projects)/projects/(detail)/[projectId]/modules/(list)/page.tsx` |
| Listenkopf | Layout-Header | `ModulesListHeader`: Breadcrumb Projekt › „Modules“; rechts `ModuleViewHeader` (ab `sm`) + „Add Module“ (mobil „Add“; Admin/Member) → `toggleCreateModuleModal(true)` | `.../modules/(list)/header.tsx` |
| Mobile-Kopf Liste | `< md` | `ModulesListMobileHeader`: Menü „Layout“ (List layout, Gallery layout; Timeline ausgeblendet) | `.../modules/(list)/mobile-header.tsx` |
| Modul-Peek | Query `?peekModule=<id>` | `ModulePeekOverview` → `ModuleAnalyticsSidebar` (max. `24rem`, `px-6`) | `module-peek-overview.tsx` |
| Modul-Detail (Work Items) | `/:ws/projects/:projectId/modules/:moduleId` | Page `ModuleIssuesPage`: `ModuleLayoutRoot` (Analyse 09) + rechte Leiste `ModuleAnalyticsSidebar` (`w-[24rem] px-6 z-13`); SWR `CURRENT_MODULE_DETAILS_${moduleId}`; Fehler → `EmptyState` „Module does not exist“ / „The module you are looking for does not exist or has been deleted.“ / „View other modules“ | `.../modules/(detail)/[moduleId]/page.tsx` |
| Modul-Detail-Kopf | Layout-Header | Breadcrumb Projekt › „Modules“ › `ModuleSelect variant="breadcrumb"`; Count-Badge „There are N work items in this module“; `LayoutSelection` (5 Layouts); `WorkItemFiltersToggle`; „Display“ (`ignoreGroupedFilters=["module"]`); „Analytics“ (Admin/Member); „Add work item“ (Admin/Member, ab `sm`); Sidebar-Toggle; `ModuleQuickActions` | `.../modules/(detail)/header.tsx` |
| Modul anlegen/bearbeiten | „Add Module“, Empty-State-CTA, Kontextmenü „Edit“ | `CreateUpdateModuleModal` → `ModuleForm` | `modal.tsx`, `form.tsx` |
| Modul löschen | Kontextmenü „Delete“ | `DeleteModuleModal` | `delete-module-modal.tsx` |
| Modul archivieren | Kontextmenü „Archive“ | `ArchiveModuleModal` | `archived-modules/modal.tsx` |
| Link hinzufügen/bearbeiten | Sidebar-Abschnitt „Links“ | `CreateUpdateModuleLinkModal` | `links/create-update-modal.tsx` |
| Archivierte Module | `/:ws/projects/:projectId/archives/modules` | `ArchivedModulesHeader` + `ArchivedModuleLayoutRoot` → `ArchivedModulesView` | `archived-modules/*` |

#### 2.3.2 Komponenten-Inventar

| Datei | Export | Zweck / Darstellung | Abhängigkeiten |
|---|---|---|---|
| `index.ts` | Barrel (applied-filters, dropdowns, select, sidebar-select, delete-module-modal, form, gantt-chart, links, modal, modules-list-view, module-card-item, module-list-item, module-peek-overview, quick-actions, module-list-item-action, module-view-header, module-layout-icon, analytics-sidebar, archived-modules) | – | – |
| `module-view-header.tsx` | `ModuleViewHeader` | `hidden sm:flex`: Suche (wie Cycles; **Close-Button leert die Suche nicht**, `updateSearchQuery("")` auskommentiert), `ModuleOrderByDropdown`, `FiltersDropdown` „Filters“ (Markierung auch bei Favoriten-Filter) mit `ModuleFiltersSelection` (Mitglieder = Workspace-Mitglieder), Layout-Umschalter (`hidden md:flex rounded-sm bg-layer-3 p-1`; Buttons `h-5.5 w-7`, aktiv `bg-layer-transparent-active`; Tooltips „List layout“, „Gallery layout“, „Timeline layout“) | `useModuleFilter`, `useMember`, `MODULE_VIEW_LAYOUTS` |
| `modules-list-view.tsx` | `ModulesListView` | Loader je Layout (`CycleModuleListLayoutLoader`, `CycleModuleBoardLayoutLoader`, `GanttLayoutLoader`); 0 Module → `EmptyStateDetailed assetKey="module"` „Map your project goals to Modules and track easily.“ + „Set your first module“ (Admin/Member); 0 Treffer → `assetKey="search"` „No matching results.“ / „No results found. Try adjusting your search terms.“; Layouts: `list` (`ListLayout` + `ModuleListItem`), `board` (Grid `grid-cols-1 gap-6 py-page-y`, ohne Peek `lg:grid-cols-2 xl:grid-cols-3 3xl:grid-cols-4`, mit Peek `lg:grid-cols-1 xl:grid-cols-2 3xl:grid-cols-3`), `gantt` (`ModulesListGanttChartView`); rechts `ModulePeekOverview` | `useModule`, `useModuleFilter`, `useCommandPalette` |
| `module-layout-icon.tsx` | `ModuleLayoutIcon` | Icons `list`→`ListOutline`, `board`→`GridOutline`, `gantt`→`TimelineOutline` (14 px, optional Container mit Rahmen) | – |
| `module-list-item.tsx` | `ModuleListItem` | `ListItem` (Link `/${ws}/projects/${project_id}/modules/${id}`); Präfix `CircularProgress` mit `progress = floor((completed+cancelled)/total·100)`; Mitte: Status `completed` → Haken (100 %) bzw. `!` (`text-13 text-accent-primary`); sonst Haken oder `${progress}%` (`text-9 text-tertiary`); Anhang: Info-Button (`InfoOutline`, `hidden group-hover:flex`, mobil sichtbar) → Peek; archivierte Module: Zeilenklick → Peek | `ListItem`, `ModuleListItemAction`, `ModuleQuickActions` |
| `module-list-item-action.tsx` | `ModuleListItemAction` | `DateRangeSelect select-ghost-md` (`h-6 rounded-sm border-[0.5px] border-strong text-11`, editierbar, `mergeDates`, Placeholder „Start date - End date“, ohne `minDate`), `ModuleStatusDropdown`, Lead-Avatar oder `UserAltOutline` mit Tooltip „No lead“, `FavoriteStar` (Admin/Member, nicht archiviert), Quick-Actions | `useModule.updateModuleDetails`, `setPromiseToast` |
| `module-card-item.tsx` | `ModuleCardItem` | Gallery-Karte (`Card` aus `@plane/blocks/card`, ganzer Inhalt ist `Link`, `data-prevent-progress`): Name (`text-14 font-medium`, Tooltip), Status-Dropdown, Info-Button; Zeile `WorkItemsOutline` + Text („0 work items“ / „N Work item(s)“ wenn alle erledigt / „X/Y Work items“), Lead-Avatar oder „No lead“; `LinearProgress md brand` (completed/total); `DateRangeSelect`; unten rechts absolut (`right-4 bottom-[18px]`) `FavoriteStar` (Admin/Member, **auch bei archivierten**) + Quick-Actions. Klicks auf Status/Datum werden per `handleEventPropagation` + `handleTriggerKeyDown` vom Link abgeschirmt | `trigger-guard.ts`, `Card` |
| `module-status-dropdown.tsx` | `ModuleStatusDropdown` | `Select` ohne Suche über `MODULE_STATUS`; Trigger neutral (`pill-md h-6 border-none bg-transparent p-0`), innen Chip `h-6 w-20 rounded-sm text-11` mit `color` und `${color}20` | `MODULE_STATUS`, `ModuleStatusIcon` |
| `module-peek-overview.tsx` | `ModulePeekOverview` | Leiste `absolute right-0 z-[9] max-w-[24rem] px-6 … md:relative` mit gleichem Box-Shadow wie Cycle-Peek; lädt Details bzw. archivierte Details | `useModule` |
| `quick-actions.tsx` | `ModuleQuickActions` | „…“-Menü (`aria-label` „Toggle quick actions menu“ aus `aria_labels.projects_sidebar.toggle_quick_actions_menu`) + Kontextmenü; Einträge `useModuleMenuItems` (2.3.3); hostet Edit-, Archiv-, Lösch-Modal | `quick-actions-helper.tsx` |
| `modal.tsx` | `CreateUpdateModuleModal` | `Dialog size="md"`, `disablePointerDismissal`, `aria-label` „Create module“/„Update module“; schließt nur bei Erfolg | `useModule.createModule/updateModuleDetails` |
| `form.tsx` | `ModuleForm` | Kopf `ProjectSelect pill-md` (nur Anlage) + Überschrift „Create module“/„Update module“ (`common.create/update` + `common.module` klein); Felder: Titel (Pflicht, ≤255, `Input 2xl autoFocus`), Beschreibung (`TextArea lg autoResize maxRows=8`), Zeile mit `DateRangeSelect pill-md` (Start/Ziel, ohne `minDate`), `ModuleStatusSelect` (Pflicht, Default `backlog`), Lead (`MemberSelect` single, Placeholder „Lead“), Members (`MemberSelect multiple`, Variante `avatar-group-md` sobald Werte, sonst `pill-md`); Footer „Cancel“, „Create Module“/„Creating“ bzw. „Update Module“/„Updating“ | `MemberSelect`, `ProjectSelect`, `getTabIndex(ETabIndices.PROJECT_MODULE)` |
| `delete-module-modal.tsx` | `DeleteModuleModal` | `ConfirmDialog` „Delete module“, Text „Are you sure you want to delete module- <Name>? All of the data related to the module will be permanently removed. This action cannot be undone.“ | `PROJECT_ERROR_MESSAGES.moduleDeleteError` |
| `select/status.tsx` | `ModuleStatusSelect` | Formular-Select (Controller, `rules.required`), Trigger `pill-md` mit Status-Icon bzw. `StateOutline` und „Status“; Fehler `text-danger-primary` | `MODULE_STATUS` |
| `select/index.ts` | Re-Export | – | – |
| `sidebar-select/select-status.tsx` | `SidebarStatusSelect` | Zeile „Status“ mit Farbpunkt-Select (**in CE nicht verwendet**) | – |
| `sidebar-select/index.ts` | Re-Export | – | – |
| `analytics-sidebar/root.tsx` | `ModuleAnalyticsSidebar`, intern `ModuleLinksCollapsible` | Sticky-Kopf mit rundem Schließen-Button (`h-5 w-5 bg-layer-3`, `ChevronRightOutline text-on-color`); Status-Select (Chip, Fallback-Farbe `#a3a3a2`, Fallback-Text „Backlog“); Name (`text-18 font-semibold`); Beschreibung (read-only TextArea); Zeilen „Date range“ (`DateRangeSelect select-ghost-md`), „Lead“ (`MemberSelect select-ghost-md`), „Members“ (multiple, Label nur bei ≤1), „Work items“ („completed/total“ oder „0 work items“), „Points“ (nur Schätzsystem `points`); `ModuleAnalyticsProgress`; Collapsible „Links“ (Default offen, wenn Links existieren) | `useModule`, `useProjectEstimates`, `MemberSelect`, `@makeplane/propel/components/collapsible` |
| `analytics-sidebar/issue-progress.tsx` | `ModuleAnalyticsProgress` | Collapsible „Progress“ (Default offen, wenn Daten gültig) mit Prozent-Badge (`bg-amber-500/20 text-amber-500 h-5 w-9`, nur > 0) und – bei Schätzsystem `points` – Select „Work items“/„Points“ (`moduleBurnDownChartOptions`: `burndown`→„Work items“, `points`→„Points“) + Spinner beim Nachladen; Inhalt `ProgressChart` + `ModuleProgressStats`; ungültige Daten: „Progress“ + Warnsymbol + „This module isn't active yet.“ (Start in Zukunft) bzw. „Invalid date. Please enter valid date.“ (Datum fehlt) | `useWorkItemFilters`, `ProgressChart` |
| `analytics-sidebar/progress-stats.tsx` | `ModuleProgressStats` | Tabs (`PROGRESS_STATS`), `localStorage["module-analytics-tab-<id>"]` (Default `stat-assignees`) | `components/core/sidebar/progress-stats/*` |
| `analytics-sidebar/index.ts` | Re-Exports | – | – |
| `links/create-update-modal.tsx` | `CreateUpdateModuleLinkModal` | `Dialog size="md"`: Titel „Add link“/„Update link“; Felder „URL“ (Pflicht „URL is required“, Placeholder „Type or paste a URL“) und „Display title“ (Beschreibung „Optional“, Placeholder „What you'd like to see this link as“); Buttons „Cancel“, „Add link“/„Adding link“ bzw. „Update link“/„Updating link“ | `InputField` |
| `links/list.tsx` | `ModuleLinksList` | Liste `link_module` | `useModule` |
| `links/list-item.tsx` | `ModulesLinksListItem` | Karte `rounded-md bg-layer-3 p-2.5`: Icon `getIconForLink(url)`, Titel oder URL als Link (`target=_blank`, Tooltip), Buttons Bearbeiten (`EditOutline`), Kopieren (`CopyOutline` → Toast „Copied to clipboard“/„The URL has been successfully copied to your clipboard“), Löschen (`DeleteOutline`); Fußzeile „Added <vor X> by <Name>“ (Bots: „<first_name> Bot“) | `calculateTimeAgo`, `copyTextToClipboard` |
| `links/index.ts` | Re-Exports | – | – |
| `gantt-chart/modules-list-layout.tsx` | `ModulesListGanttChartView` | `GanttChartRoot` (Titel/Loader „Modules“, `TimeLineTypeContext = MODULE`, Sidebar `ModuleGanttSidebar`, `showAllBlocks`); Resize/Move/Add nur Projekt-Rolle 20/15; Reorder nur bei `order_by === "sort_order"` | `components/gantt-chart` (Analyse 09 2.5) |
| `gantt-chart/blocks.tsx` | `ModuleGanttBlock`, `ModuleGanttSidebarBlock` | Block: Farbe aus Status (`getBlockViewDetails`), Overlay `bg-surface-1/50`, Name sticky ab `SIDEBAR_WIDTH`, Tooltip „<Name>: <Dauer>“, Klick → Detailseite; Sidebar-Zeile: Status-Icon 16 px + Name als Link | `getBlockViewDetails` (`issue-layouts/utils`) |
| `gantt-chart/index.ts` | Re-Exports | – | – |
| `dropdowns/order-by.tsx` | `ModuleOrderByDropdown` | Menü-Button (`ButtonElement secondary md`) mit Sortier-Icon (`SortAscendingOutline`/`SortDescendingOutline`), Label, Chevron; Einträge „Name“, „Progress“, „Number of work items“, „Due date“, „Created date“, „Manual“; Trenner + „Ascending“/„Descending“ (nicht bei Manual) | `MODULE_ORDER_BY_OPTIONS` |
| `dropdowns/filters/root.tsx` | `ModuleFiltersSelection` | Suche + Sektionen: „Favorites“ (Toggle, nicht im Archiv), „Status“ (nicht im Archiv), „Lead“, „Members“, „Start date“, „Due date“ | – |
| `dropdowns/filters/status.tsx` | `FilterStatus` | sechs Status mit `ModuleStatusIcon` | `MODULE_STATUS` |
| `dropdowns/filters/lead.tsx` | `FilterLead` | Mitglieder (Workspace) mit Avatar, eigener Nutzer als „You“, sortiert: gewählte zuerst, dann eigener Nutzer, dann alphabetisch (Sortierung nur bei Suchänderung neu berechnet); erste 5, „View all“/„View less“; Loader 3 Zeilen | `useMember`, `useUser` |
| `dropdowns/filters/members.tsx` | `FilterMembers` | identisch, Titel „Members“ | – |
| `dropdowns/filters/start-date.tsx` | `FilterStartDate` | wie Cycles (Presets + „Custom“) | `DateFilterModal` |
| `dropdowns/filters/target-date.tsx` | `FilterTargetDate` | dito, Titel „Due date“ | `DateFilterModal` |
| `dropdowns/filters/index.ts`, `dropdowns/index.ts` | Re-Exports | – | – |
| `applied-filters/root.tsx` | `ModuleAppliedFiltersList` | eigener `Header variant=TERNARY`; Chips für `status`, `start_date`, `target_date`, `lead`, `members`; Favoriten-Chip „Modules · Favorite“; Button „Clear all“ im Chip-Stil (`FILTER_GROUP_CLASSNAME`); editierbar nur bei `alwaysAllowEditing` | – |
| `applied-filters/status.tsx`, `date.tsx`, `members.tsx` | `AppliedStatusFilters`, `AppliedDateFilters`, `AppliedMembersFilters` | Status-Chip mit Farbe; Datums-Chip wie Cycles; Mitglieder-Chip mit `Avatar 2xs` + Name | `useMember` |
| `applied-filters/index.ts` | Re-Exports | – | – |
| `archived-modules/header.tsx` | `ArchivedModulesHeader` | `ArchiveTabsList` + Suche + `ModuleOrderByDropdown` + Filter (ohne Favoriten/Status) | – |
| `archived-modules/root.tsx` | `ArchivedModuleLayoutRoot` | SWR `ARCHIVED_MODULES_${ws}_${pid}`; leer `EmptyStateDetailed assetKey="archived-module"` „No archived Modules yet“ / „To tidy up your project, archive completed or cancelled modules. Find them here once archived.“ | – |
| `archived-modules/view.tsx` | `ArchivedModulesView` | Liste `ModuleListItem` + Peek (`isArchived`); leer „No matching modules“ (+ zwei Hinweistexte, hart kodiert) | – |
| `archived-modules/modal.tsx` | `ArchiveModuleModal` | `ConfirmDialog` „Archive module <Name>“ / „Are you sure you want to archive the module? All your archives can be restored later.“ | – |
| `archived-modules/index.ts` | Re-Exports | – | – |

#### 2.3.3 Kontextmenü Modul (`useModuleMenuItems`)

| # | Key | Text | sichtbar wenn | disabled / Beschreibung | Aktion |
|---|---|---|---|---|---|
| 1 | `edit` | „Edit“ | Admin/Member, nicht archiviert | – | `CreateUpdateModuleModal` |
| 2 | `open-new-tab` | „Open in new tab“ | immer | – | neues Tab `/${ws}/projects/${pid}/modules/${id}` |
| 3 | `copy-link` | „Copy link“ | immer | – | Toast „Link Copied!“ / „Module link copied to clipboard.“ |
| 4 | `archive` | „Archive“ | Admin/Member, nicht archiviert | disabled, wenn Status ∉ {`completed`, `cancelled`}; Beschreibung „Only completed or cancelled modules can be archived“ | `ArchiveModuleModal` |
| 5 | `restore` | „Restore“ | Admin/Member, archiviert | – | `restoreModule` → Toast „Restore success“/„Your module can be found in project modules.“ → Push `/${ws}/projects/${pid}/archives/modules`; Fehler „Module could not be restored. Please try again.“ |
| 6 | `delete` | „Delete“ | Admin/Member, nicht archiviert | – | `DeleteModuleModal` |

Quelle: `apps/web/components/common/quick-actions-helper.tsx`, `apps/web/components/modules/quick-actions.tsx`.

#### 2.3.4 Konstanten Modules (`packages/constants/src/module.ts`)

| Status `value` | Label (en) | Farbe | `textColor` / `bgColor` |
|---|---|---|---|
| `backlog` | Backlog | `#a3a3a2` | `text-placeholder` / `bg-layer-1` |
| `planned` | Planned | `#3f76ff` | `text-blue-500` / `bg-indigo-50` |
| `in-progress` | In Progress | `#f39e1f` | `text-amber-500` / `bg-amber-50` |
| `paused` | Paused | `#525252` | `text-tertiary` / `bg-surface-2` |
| `completed` | Completed | `#16a34a` | `text-success-primary` / `bg-success-subtle` |
| `cancelled` | Cancelled | `#ef4444` | `text-danger-primary` / `bg-danger-subtle` |

Sortieroptionen `MODULE_ORDER_BY_OPTIONS`: `name`, `progress`, `issues_length`, `target_date`, `created_at`, `sort_order` (jeweils mit `-`-Präfix absteigend, außer `sort_order`). Layouts `MODULE_VIEW_LAYOUTS`: `list`, `board`, `gantt`.

#### 2.3.5 Store, Services, Endpunkte (Modules)

| Aufruf | HTTP | Endpunkt | Auslöser |
|---|---|---|---|
| `ModuleService.getModules` | GET | `/api/workspaces/{ws}/projects/{pid}/modules/` | `fetchModules` (Projekt-Bootstrap, `project-wrapper.tsx`) |
| `getWorkspaceModules` | GET | `/api/workspaces/{ws}/modules/` | `fetchModulesSlim` (Bootstrap parallel) |
| `getModuleDetails` | GET | `/api/workspaces/{ws}/projects/{pid}/modules/{mid}/` | Detail, Peek, Plot-Wechsel |
| `createModule` | POST | `/api/workspaces/{ws}/projects/{pid}/modules/` | Formular |
| `patchModule` | PATCH | `/api/workspaces/{ws}/projects/{pid}/modules/{mid}/` | Formular, Sidebar (Status/Lead/Members/Datum), Listen-/Kartenaktionen, Gantt (Datum, `sort_order`) |
| `deleteModule` | DELETE | `/api/workspaces/{ws}/projects/{pid}/modules/{mid}/` | Lösch-Dialog |
| `createModuleLink` | POST | `/api/workspaces/{ws}/projects/{pid}/modules/{mid}/module-links/` Body `{metadata:{}, title, url}` | Link-Dialog |
| `updateModuleLink` | PATCH | `.../modules/{mid}/module-links/{linkId}/` | Link-Dialog |
| `deleteModuleLink` | DELETE | `.../modules/{mid}/module-links/{linkId}/` | Link-Liste |
| Favoriten | POST/DELETE | `/api/workspaces/{ws}/user-favorites/` bzw. `/user-favorites/{favoriteId}/` (`entity_type:"module"`) | Stern |
| `ModuleArchiveService.getArchivedModules` | GET | `/api/workspaces/{ws}/projects/{pid}/archived-modules/` | Archiv |
| `getArchivedModuleDetails` | GET | `/api/workspaces/{ws}/projects/{pid}/archived-modules/{mid}/` | Archiv-Peek |
| `archiveModule` | POST | `/api/workspaces/{ws}/projects/{pid}/modules/{mid}/archive/` | Archiv-Dialog |
| `restoreModule` | DELETE | `/api/workspaces/{ws}/projects/{pid}/modules/{mid}/archive/` | „Restore“ |

Quellen: `apps/web/services/module.service.ts`, `apps/web/services/module_archive.service.ts`, `apps/web/store/module.store.ts`.

#### 2.3.6 Clientseitige Zustände (Modules)

| Zustand | Persistenz | Inhalt |
|---|---|---|
| `moduleFilter.displayFilters[projectId]` | `localStorage["module_display_filters"]` (gesamtes Objekt aller Projekte) | `{favorites:false, layout:"list", order_by:"name"}` (Defaults bei Projektinitialisierung) |
| `moduleFilter.filters[projectId].default/.archived` | `localStorage["module_filters"]` | `TModuleFilters` `{status?, lead?, members?, start_date?, target_date?}` |
| `searchQuery`, `archivedModulesSearchQuery` | Speicher (Suche wird bei Projektwechsel geleert) | Name-Teilstring |
| `module.plotType[moduleId]` | Speicher | `burndown` (Work items) / `points`; ohne aktive Projekt-Schätzung immer `burndown` |
| `localStorage["module_sidebar_collapsed"]` | localStorage (**String** `"true"`/`"false"`) | Sidebar der Detailseite |
| `localStorage["module-analytics-tab-<id>"]` | localStorage | aktiver Statistik-Tab |
| Query `peekModule` | URL | Modul-ID im Peek |

Quelle: `apps/web/store/module_filter.store.ts` (Keys `MODULE_DISPLAY_FILTERS_KEY`, `MODULE_FILTERS_KEY`), `apps/web/store/module.store.ts`.

### 2.4 Pages (`apps/web/components/pages/`, 65 Dateien, 5 419 Zeilen)

Editor-Kern (Tiptap, Yjs, Hocuspocus-Protokoll, Toolbar-Konstanten, Stateless-Events, REST-Fallback, PDF-Export im Live-Server) ist in `migration/analysis/12-editor-echtzeit-live.md` beschrieben; hier steht die Web-Hülle.

#### 2.4.1 Screens und Einstiegspunkte

| Screen / Dialog | Route bzw. Auslöser | Einstiegskomponente | Quelle |
|---|---|---|---|
| Page-Liste mit Tabs Public/Private/Archived | `/:ws/projects/:projectId/pages?type=public\|private\|archived` (fehlend/ungültig → `public`) | Page `ProjectPagesPage` → `PagesListView` (Tab-Kopf nur wenn `isAnyPageAvailable`) → `PagesListMainContent` → `PagesListRoot` | `apps/web/app/(all)/[workspaceSlug]/(projects)/projects/(detail)/[projectId]/pages/(list)/page.tsx` |
| Listen-Kopf | Layout-Header | `PagesListHeader`: Breadcrumb Projekt › „Pages“; Button „Add page“/„Adding“ (nur `canCurrentUserCreatePage`) – legt sofort eine leere Page an (Zugriff aus `?type`: `private` → privat, sonst öffentlich) und navigiert hinein | `.../pages/(list)/header.tsx` |
| Page-Editor | `/:ws/projects/:projectId/pages/:pageId` | Page `PageDetailsPage` → `PageRoot` + `IssuePeekOverview` | `.../pages/(detail)/[pageId]/page.tsx` |
| Editor-Kopf | Layout-Header `PageDetailsHeader` | Breadcrumb Projekt › „Pages“ › `BreadcrumbNavigationSelect` (alle Pages des Projekts inkl. Archiv, je Eintrag Logo/Name + `PageAccessIcon`; Suche „Search“, leer „No matches found“); rechts `PageSyncingBadge` + `PageHeaderActions` | `.../pages/(detail)/header.tsx`, `.../pages/(detail)/layout.tsx` |
| Page anlegen (Dialog) | Power-K/Command „Create page“ (`toggleCreatePageModal`) | `CreatePageModal` → `PageForm` (mit Redirect) | `modals/create-page-modal.tsx`, `apps/web/components/modals/project-level.tsx` |
| Page löschen | Menü „Delete“ (nur archivierte Pages) | `DeletePageModal` | `modals/delete-page-modal.tsx` |
| Page exportieren | Menü „Export“ im Editor | `ExportPageModal` | `modals/export-page-modal.tsx` |
| Navigationsbereich (Outline/Info/Assets) | Query `?paneTab=outline\|info\|assets` | `PageNavigationPaneRoot` (Breite 294 px) | `navigation-pane/*` |
| Versionsansicht | Query `?paneTab=info&version=<id>` | `PageVersionsOverlay` → `PageVersionsMainContent` → `PagesVersionEditor` | `version/*` |
| AI-Menü (Pi) | `aiHandler.menu` im Editor (in CE nicht gerendert, siehe Analyse 12) | `EditorAIMenu`, `AskPiMenu` | `editor/ai/*` |

#### 2.4.2 Komponenten-Inventar

| Datei | Export | Zweck / Darstellung | Abhängigkeiten |
|---|---|---|---|
| `pages-list-view.tsx` | `PagesListView` | Rahmen; SWR `PROJECT_PAGES_${projectId}` → `fetchPagesList`; Tab-Kopf `PagesListHeaderRoot` | `usePageStore(storeType)` |
| `pages-list-main-content.tsx` | `PagesListMainContent` | Zustände: `loader === "init-loader"` → `PageLoader`; keine Pages im Projekt bzw. im Tab `public`/`private` → `EmptyStateDetailed assetKey="page"` „Document everything — from notes to PRDs“ + Beschreibung + CTA „Create your first Page“ (Admin/Member; legt sofort Page an, Zugriff nach Tab) ; Tab `archived` leer → „No archived pages yet“ / „Archive pages not on your radar. Access them here when needed.“; keine Treffer → `assetKey="search"` „No matching results.“ | `createPage`, `useUserPermissions` |
| `header/root.tsx` | `PagesListHeaderRoot` | `Header SECONDARY`: links `PageTabNavigation`; rechts `PageSearchInput`, `PageOrderByDropdown`, `FiltersDropdown` „Filters“ mit `PageFiltersSelection`; darunter `Header TERNARY` mit `PageAppliedFiltersList` bei aktiven Filtern | `useMember` (Workspace-Mitglieder) |
| `list/tab-navigation.tsx` | `PageTabNavigation` | Links „Public“, „Private“, „Archived“ (`px-4 text-13 font-medium`, aktiv `text-accent-primary` + Unterstrich `border-t-2 border-accent-strong`); Klick auf aktiven Tab ohne Navigation | – |
| `list/search-input.tsx` | `PageSearchInput` | ausklappbare Suche (Placeholder „Search pages“, `aria-label` „Search“), Escape-/Outside-Logik wie Cycles | – |
| `list/order-by.tsx` | `PageOrderByDropdown` | Menü mit „Name“, „Date created“, „Date modified“, Trenner, „Ascending“/„Descending“ | – |
| `list/filters/root.tsx` | `PageFiltersSelection` | Suche (Fokus außer mobil), „Favorites“-Toggle, `FilterCreatedDate` („Created date“, Presets `DATE_BEFORE_FILTER_OPTIONS`: 1 week ago, 2 weeks ago, 1 month ago, Today, Yesterday, Last 7 days, Last 30 days + „Custom“), `FilterCreatedBy` („Created by“, Mitglieder mit „You“) | `components/common/filters/created-at.tsx`, `created-by.tsx` |
| `list/filters/index.ts` | Re-Export | – | – |
| `list/applied-filters/root.tsx` | `PageAppliedFiltersList` | Chips `created_at`, `created_by`, Schlüssel `favorites` (nur Label + „x“), „Clear all“ | `components/common/applied-filters/date.tsx`, `members.tsx` |
| `list/applied-filters/index.ts` | Re-Export | – | – |
| `list/root.tsx` | `PagesListRoot` | `ListLayout` mit `PageListBlock` je gefilterter ID | – |
| `list/block.tsx` | `PageListBlock` | `ListItem`: Präfix Logo (16 px, `lucide`) oder `PagesOutline`; Titel `getPageName` („Untitled“ bei leerem Namen); Link `/${ws}/projects/${project_ids[0]}/pages/${id}` | `usePage` |
| `list/block-item-action.tsx` | `BlockItemAction` | Owner-Avatar (Tooltip „Owned by: <Name>“), Zugriffs-Icon (`GlobeOutline` „Public“ / `LockOutline` „Private“), Trenner (`MinusOutline rotate-90`), Info-Icon (Tooltip „Created on <Datum>“), `FavoriteStar` (Rolle ≥ Member), `PageActions` mit Reihenfolge `open-in-new-tab, copy-link, make-a-copy, toggle-lock, toggle-access, archive-restore, delete` | `usePageOperations` |
| `list/index.ts` | Re-Export | – | – |
| `dropdowns/actions.tsx` | `PageActions`, Typ `TPageActions` | Generisches „…“-Menü (`IconButton ghost sm`, `aria-label` „More actions“) + optional Kontextmenü; Einträge siehe 2.4.3; hostet `DeletePageModal` | `usePageFlag` (`isMovePageEnabled=false`) |
| `dropdowns/index.ts` | Re-Export | – | – |
| `header/actions.tsx` | `PageHeaderActions` | Reihe: `PageArchivedBadge`, `PageOfflineBadge`, `PageLockControl`, `PageCopyLinkControl`, `PageFavoriteControl`, `PageOptionsDropdown` | – |
| `header/archived-badge.tsx` | `PageArchivedBadge` | Badge `h-6 bg-accent-primary/20 text-accent-primary` „Archived at <Datum>“ | – |
| `header/offline-badge.tsx` | `PageOfflineBadge` | nur wenn editierbar und offline: Pill „Offline“ mit Tooltip „You are offline. You can continue making changes. They will be synced when you are back online.“ | `useOnlineStatus` |
| `header/lock-control.tsx` | `PageLockControl` | drei Zustände: neutral (Icon-Button `size-6`, Tooltip „Lock“), „Locked“ (Pill `bg-accent-primary/20`, Animation `animate-lock-icon`, `animate-text-slide-in`), nach Entsperren 600 ms „Unlocked“ (`animate-fade-out`, `animate-unlock-icon`), dann neutral; nur Owner oder Projekt-Admin | `usePageOperations.toggleLock` |
| `header/copy-link-control.tsx` | `PageCopyLinkControl` | Icon-Button `LinkOutline`; nach Klick 1 s Haken (`text-success-primary`) und Tooltip „Copied!“ | `copyLink` |
| `header/favorite-control.tsx` | `PageFavoriteControl` | Stern; Favorit = Füllung `--color-label-yellow-icon`; `aria-label` „Remove favorite“/„Add to favorites“; nur Rolle ≥ Member | `toggleFavorite` |
| `header/syncing-badge.tsx` | `PageSyncingBadge` | `Badge sm`: „Syncing...“ (`brand`, Icon `Dot`) bzw. „Connection lost“ (`danger`, `CloudOff`) mit Tooltips („Syncing... Your changes are being synced with the server. You can continue making changes.“ / „Connection lost. We're having trouble connecting to the websocket server. Your changes will be synced and saved every 10 seconds.“); bei `synced` nach 300 ms ausgeblendet | `lucide-react` |
| `header/index.ts` | Re-Export `root` | – | – |
| `editor/page-root.tsx` | `PageRoot`, Typen `TPageRootHandlers`, `TPageRootConfig` | Orchestrierung: Versions-Overlay, Toolbar, Banner „Content limit reached and live sync is off. Create a new page or use nested pages to continue syncing.“ (bei Realtime-Fehler `content_too_large`), `PageEditorBody`, `PageNavigationPaneRoot`; REST-Fallback (`usePageFallback`); Wiederherstellen einer Version = `clearEditor()` + `setEditorValue(html)` | `usePagesPaneExtensions`, `useExtendedEditorProps` (CE `{}`) |
| `editor/editor-body.tsx` | `PageEditorBody`, Typen `TEditorBodyConfig`, `TEditorBodyHandlers` | Scrollcontainer `#page-content-container`; schwebendes Mini-Outline rechts (nur bei geschlossenem Bereich; Striche 20/18/14 px, Hover-Popover `w-52` mit Überschriften); Kopf `PageEditorHeaderRoot` in Inhaltsbreite (`max-w-[720px]`, Vollbreite `max-w-[1152px]`); `CollaborativeDocumentEditorWithRef` (`containerClassName="h-full p-0 pb-64"`, Mentions, Realtime-Konfiguration, Nutzerfarbe, deaktivierte Extensions `ai`, `collaboration-cursor`) ; Loader `PageContentLoader` solange `pageId`/Realtime-URL fehlt | `useEditorMention`, `useEditorFlagging`, `useParseEditorContent`, `usePageFilters`, `useRealtimePageEvents` |
| `editor/header/root.tsx` | `PageEditorHeaderRoot` | Zeile `h-[48px]`: Button „Icon“ (`ReactionOutline`) zum Setzen eines Logos (sichtbar bei Hover oder leerem Titel); darunter Logo-Bereich | `EmojiPicker` (`@plane/blocks/emoji-icon-picker`) |
| `editor/header/logo-picker.tsx` | `PageEditorHeaderLogoPicker` | Logo 48 px (`size-[56px]`), Klick öffnet Picker (nur editierbar); Bereich `max-h-0` → `max-h-[56px]` | `updatePageLogo` |
| `editor/header/index.ts` | Re-Export | – | – |
| `editor/toolbar/root.tsx` | `PageEditorToolbarRoot` | Toolbar-Leiste `#page-toolbar-container` (`max-h-[52px]`, ab `md`), ausgeblendet bei deaktivierter „Sticky toolbar“ oder nicht editierbarer Page; rechts Button „Open navigation pane“ (`RightSidePaneOutline`) | `usePageFilters` |
| `editor/toolbar/toolbar.tsx` | `PageToolbar` | `Toolbar size="md" elevation="flat"` (`aria-label` „Formatting toolbar“): Typografie-Menü (Label aktiver Typ oder „Text“), `ColorDropdown`, Gruppen aus `TOOLBAR_ITEMS.document` (Toggles mit Tooltip + Shortcut; Gruppe `complex` als Buttons) | `@plane/editor` (`TOOLBAR_ITEMS`, `TYPOGRAPHY_ITEMS`) |
| `editor/toolbar/color-dropdown.tsx` | `ColorDropdown` | Popover „Color“ mit Vorschau (Text-/Hintergrundfarbe), Sektionen „Text colors“/„Background colors“ (`COLORS_LIST`, Kacheln `size-6`), Buttons „Remove text color“/„Remove background color“ | `COLORS_LIST` |
| `editor/toolbar/options-dropdown.tsx` | `PageOptionsDropdown` | `PageActions` mit Zusatz-Einträgen „Full width“ (Switch), „Sticky toolbar“ (Switch, nur editierbar), „Copy markdown“ (`ClipboardOutline`, Toast „Markdown copied to clipboard.“), „Version history“ (`HistoryOutline`, setzt `paneTab=info`), „Export“ (`ExportOutline`); Reihenfolge `full-screen, sticky-toolbar, copy-markdown, version-history, make-a-copy, archive-restore, delete, toggle-access, export` | `ExportPageModal`, `useQueryParams` |
| `editor/toolbar/index.ts` | Re-Exports | – | – |
| `editor/summary/content-browser.tsx` | `PageContentBrowser` | Liste der Überschriften H1–H3 (`getHeadings`, `onHeadingChange`); Klick → `scrollSummary`; `showOutline` → nur Striche | `EditorRefApi` |
| `editor/summary/heading-components.tsx` | `OutlineHeading1/2/3` | Buttons `pl-1 text-13` / `pl-2 text-11` / `pl-4 text-11`, Hover `text-accent-primary` | – |
| `editor/summary/index.ts` | Re-Exports | – | – |
| `editor/ai/menu.tsx` | `EditorAIMenu` | Panel `w-[210px]` → `w-[700px]` bei aktiver Aufgabe; einziger Eintrag „Ask Pi“; Antwortbereich (RichText read-only, „Replace selection“, „Add to next line“, „Re-generate response“), Ton-Buttons „Default“, „💼 Professional“, „😃 Casual“; Hinweis „By using this feature, you consent to sharing the message with a 3rd party service.“ | `AIService.performEditorTask` |
| `editor/ai/ask-pi-menu.tsx` | `AskPiMenu` | Eingabe „Tell AI what to do...“ ohne Absende-Logik; Text „AI is answering...“ | – |
| `editor/ai/index.ts` | Re-Exports | – | – |
| `navigation-pane/index.ts` | Konstanten `PAGE_NAVIGATION_PANE_WIDTH=294`, `PAGE_NAVIGATION_PANE_TABS_QUERY_PARAM="paneTab"`, `PAGE_NAVIGATION_PANE_VERSION_QUERY_PARAM="version"`, `PAGE_NAVIGATION_PANE_TAB_KEYS` | – | – |
| `navigation-pane/root.tsx` | `PageNavigationPaneRoot` | `aside` mit Breite 294 px, eingeklappt per negativem `marginRight`; Schließen-Button (`ArrowRightCircle`, Tooltip „Close navigation pane“); `Tabs contained` „Outline“, „Info“, „Assets“; Extension-Mechanismus (CE leer) | `useQueryParams` |
| `navigation-pane/tabs-list.tsx` | `PageNavigationPaneTabsList` | Tab-Leiste | – |
| `navigation-pane/types/extensions.ts`, `types/index.ts` | `INavigationPaneExtension*` | Erweiterungsschnittstelle (`id`, `triggerParam`, `component`, `data`, `width`) | – |
| `navigation-pane/tab-panels/index.ts` | `TPageNavigationPaneTab`, `PAGE_NAVIGATION_PANE_TABS_LIST`, `ORDERED_PAGE_NAVIGATION_TABS_LIST` | Tabs `outline`, `info`, `assets` | – |
| `navigation-pane/tab-panels/root.tsx` | `PageNavigationPaneTabPanelsRoot` | Panels | – |
| `navigation-pane/tab-panels/outline.tsx` | `PageNavigationPaneOutlineTabPanel` | `ScrollArea` + `PageContentBrowser`; leer → „Missing headings“ / „Let's put some headings in this page to see them here.“ | – |
| `navigation-pane/tab-panels/assets.tsx` | `PageNavigationPaneAssetsTabPanel` | Bild-Assets des Dokuments (nur Typ `image`/`imageComponent`): Kachel `h-12` mit Vorschau `w-11`, Name, Hover-Link „Download“; leer → „Missing images“ / „Add images to see them here.“ | `getEditorAssetSrc`, `getEditorAssetDownloadSrc` |
| `navigation-pane/tab-panels/info/root.tsx` | `PageNavigationPaneInfoTabPanel` | Dokument-Info, Akteure, Trenner, Versionen | – |
| `navigation-pane/tab-panels/info/document-info.tsx` | `PageNavigationPaneInfoTabDocumentInfo` | 2×2-Karten „Words“, „Characters“, „Paragraphs“, „Read time“ (`<60 s` → „Ns“, sonst aufgerundete Minuten „Nm“) | `getReadTimeFromWordsCount` |
| `navigation-pane/tab-panels/info/actors-info.tsx` | `PageNavigationPaneInfoTabActorsInfo` | „Edited by“ (Avatar 2xs + Name/„Deactivated user“ + „<kurz> ago“), „Created by“ (+ Datum); Links auf Profil | `calculateTimeAgoShort` |
| `navigation-pane/tab-panels/info/version-history.tsx` | `PageNavigationPaneInfoTabVersionHistory` | Zeitleiste: „Current version“ (aktiv ohne `version`-Param) + Versionen (Datum, Uhrzeit, Ersteller), Link setzt `?version=<id>`; SWR `PAGE_VERSIONS_LIST_${id}` | `fetchAllVersions` |
| `navigation-pane/tab-panels/empty-state/outline.tsx`, `assets.tsx` | Leerzustände | Bilder hell/dunkel `size-40` | `next-themes` |
| `version/root.tsx` | `PageVersionsOverlay` | Overlay `absolute inset-0 z-[16]` mit Breite `calc(100% - 294px)`, sichtbar bei `?version` | – |
| `version/main-content.tsx` | `PageVersionsMainContent` | Kopf (Datum/Uhrzeit, Badge „View only“ mit `ShowOutline`, Button „Restore“/„Restoring“ wenn editierbar), Inhalt; Fehler: „Something went wrong!“ / „The version could not be loaded, please try again.“ / „Try again“; SWR `PAGE_VERSION_${versionId}` | `fetchVersionDetails` |
| `version/editor.tsx` | `PagesVersionEditor` | `DocumentEditor` read-only (`wideLayout:true`, `editorClassName="pl-10"`), JSON bevorzugt, sonst HTML; Skeleton | `@/components/editor/document/editor` |
| `version/index.ts` | Re-Exports | – | – |
| `modals/create-page-modal.tsx` | `CreatePageModal` | `Dialog size="md"` mit `PageForm`; Erfolg → Reset + optional Navigation | `createPage` |
| `modals/page-form.tsx` | `PageForm` | Titel „Create page“; Logo-Button (`EmojiPicker`, `h-9 w-9 bg-layer-2`), Feld Titel (Placeholder „Title“, Pflicht, Fehler „Max length of the name should be less than 255 characters“); Fuß: `AccessField` (Public/Private-Umschalter) + Label, „Cancel“, „Create Page“/„Creating“ | `AccessField`, `getTabIndex(ETabIndices.PROJECT_PAGE)` |
| `modals/delete-page-modal.tsx` | `DeletePageModal` | `ConfirmDialog` „Delete page“ / „Are you sure you want to delete page- <Name> ? The Page will be deleted permanently. This action cannot be undone.“; Erfolg → Toast „Page deleted successfully.“ + `router.back()` wenn auf Detailseite | `removePage` |
| `modals/export-page-modal.tsx` | `ExportPageModal` | `Dialog size="xs"` „Export page“: „Export format“ (PDF/Markdown), „Include content“ (Everything/No images), „Page format“ (nur PDF: A4, A3, A2, Letter, Legal, Tabloid); „Cancel“, „Export“/„Exporting“ | `@react-pdf/renderer` `pdf()`, `PDFDocument` (`components/editor/pdf`) |
| `loaders/page-loader.tsx` | `PageLoader` | Listen-Skeleton (Kopf + 10 Zeilen mit zufälliger Breite) | – |
| `loaders/page-content-loader.tsx` | `PageContentLoader` | Editor-Skeleton (Toolbar-Kacheln 26 px, Inhaltsbalken) | – |

#### 2.4.3 Page-Menü (`PageActions`) – Einträge und Bedingungen

| Key | Text | Icon | sichtbar wenn | Aktion |
|---|---|---|---|---|
| `toggle-lock` | „Lock“/„Unlock“ | `LockedOutline`/`UnlockedOutline` | `canCurrentUserLockPage` (Owner oder Admin) | Stateless-Event `lock`/`unlock` (siehe 3.3.4) |
| `toggle-access` | „Make private“/„Make public“ | `LockOutline`/`GlobeOutline` | `canCurrentUserChangeAccess` und nicht archiviert | Event `make-private`/`make-public` |
| `open-in-new-tab` | „Open in new tab“ | `NewTabOutline` | immer | `window.open(link, "_blank")` |
| `copy-link` | „Copy link“ | `LinkOutline` | immer | Toast „Link Copied!“ / „Page link copied to clipboard.“ |
| `make-a-copy` | „Make a copy“ | `CopyOutline` | `canCurrentUserDuplicatePage` (Rolle ≥ Member) | `POST …/duplicate/` → „Page duplicated successfully.“ / „Page could not be duplicated. Please try again later.“ |
| `archive-restore` | „Archive“/„Restore“ | `ArchiveOutline`/`RestoreOutline` | `canCurrentUserArchivePage` | Event `archive`/`unarchive` |
| `delete` | „Delete“ | `DeleteOutline` | `canCurrentUserDeletePage` **und archiviert** | `DeletePageModal` |
| `move` | „Move“ | `ExportOutline` | `canCurrentUserMovePage && isMovePageEnabled` (CE: nie) | setzt nur lokalen State, kein Modal in CE |
| `full-screen` | „Full width“ + Switch | – | immer (Editor) | `pages_config.full_width` umschalten |
| `sticky-toolbar` | „Sticky toolbar“ + Switch | – | Page editierbar | `pages_config.sticky_toolbar` |
| `copy-markdown` | „Copy markdown“ | `ClipboardOutline` | immer (Editor) | `editorRef.copyMarkdownToClipboard()` |
| `version-history` | „Version history“ | `HistoryOutline` | immer (Editor) | Query `paneTab=info` |
| `export` | „Export“ | `ExportOutline` | immer (Editor) | `ExportPageModal` |

#### 2.4.4 Berechtigungsmatrix Page (`apps/web/store/pages/project-page.ts`)

„Höchste Rolle“ = höchste Projektrolle des Nutzers über alle `project_ids` der Page (20 Admin, 15 Member, 5 Guest).

| Getter | Regel |
|---|---|
| `canCurrentUserAccessPage` | Page öffentlich **oder** Nutzer ist Owner |
| `canCurrentUserEditPage` | (öffentlich und Rolle ≥ Member) oder (privat und Owner) |
| `isContentEditable` | nicht archiviert **und** nicht gesperrt **und** (Owner oder (öffentlich und Rolle ≥ Member)) |
| `canCurrentUserDuplicatePage` | Rolle ≥ Member |
| `canCurrentUserFavoritePage` | Rolle ≥ Member |
| `canCurrentUserLockPage`, `canCurrentUserChangeAccess`, `canCurrentUserArchivePage`, `canCurrentUserDeletePage`, `canCurrentUserMovePage` | Owner oder Rolle = Admin |
| `canCurrentUserCreatePage` (Store) | Projektrolle ∈ `ROLE_PERMISSIONS_TO_CREATE_PAGE` = {Admin, Member} (`apps/web/store/pages/project-page.store.ts`) |

#### 2.4.5 Services und Endpunkte (Pages)

| Aufruf | HTTP | Endpunkt |
|---|---|---|
| `ProjectPageService.fetchAll` | GET | `/api/workspaces/{ws}/projects/{pid}/pages/` |
| `fetchById` | GET | `/api/workspaces/{ws}/projects/{pid}/pages/{id}/?track_visit=true` |
| `create` | POST | `/api/workspaces/{ws}/projects/{pid}/pages/` (Body `{access}` bzw. `{name, logo_props, access}`) |
| `update` | PATCH | `/api/workspaces/{ws}/projects/{pid}/pages/{id}/` (Titel debounced 2 s, `logo_props`) |
| `updateAccess` | POST | `.../pages/{id}/access/` Body `{access: 0\|1}` |
| `remove` | DELETE | `.../pages/{id}/` |
| `archive` / `restore` | POST / DELETE | `.../pages/{id}/archive/` |
| `lock` / `unlock` | POST / DELETE | `.../pages/{id}/lock/` |
| `fetchDescriptionBinary` | GET | `.../pages/{id}/description/` (Binary, REST-Fallback) |
| `updateDescription` | PATCH | `.../pages/{id}/description/` |
| `duplicate` | POST | `.../pages/{id}/duplicate/` |
| `move` | POST | `.../pages/{id}/move/` Body `{new_project_id}` (CE ungenutzt) |
| `fetchFavorites`, `addToFavorites`, `removeFromFavorites` | GET/POST/DELETE | `.../favorite-pages/[{id}/]` (ungenutzt; Favoriten laufen über `/api/workspaces/{ws}/user-favorites/` mit `entity_type:"page"`) |
| `fetchArchived` | GET | `.../archived-pages/` (ungenutzt; Archiv-Tab filtert clientseitig) |
| `ProjectPageVersionService.fetchAllVersions` | GET | `.../pages/{id}/versions/` |
| `fetchVersionById` | GET | `.../pages/{id}/versions/{versionId}/` |
| `restoreVersion` | POST | `.../pages/{id}/versions/{versionId}/restore/` (an `PageRoot` übergeben, aber **nicht aufgerufen**) |
| `WorkspaceService.searchEntity` | GET | `/api/workspaces/{ws}/entity-search/?query_type=…&query=…&count=…&project_id={pid}` (Mentions) |
| `AIService.performEditorTask` | POST | `/api/workspaces/{ws}/rephrase-grammar/` Body `{task, text_input, casual_score?, formal_score?}` (nur AI-Menü) |

Quellen: `apps/web/services/page/project-page.service.ts`, `apps/web/services/page/project-page-version.service.ts`, `apps/web/app/(all)/[workspaceSlug]/(projects)/projects/(detail)/[projectId]/pages/(detail)/[pageId]/page.tsx`.

#### 2.4.6 Clientseitige Zustände (Pages)

| Zustand | Persistenz | Inhalt |
|---|---|---|
| `projectPage.filters` | Speicher (Suche bei Projektwechsel geleert) | `{searchQuery:"", sortKey:"updated_at", sortBy:"desc", filters?: {favorites?, created_at?, created_by?}}` |
| `localStorage["pages_config"]` | localStorage | `{full_width:false, font_size:"large-font", font_style:"sans-serif", sticky_toolbar:true}` (`apps/web/hooks/use-page-filters.ts`) |
| Query `paneTab` | URL | `outline` / `info` / `assets` (öffnet Navigationsbereich) |
| Query `version` | URL | Versions-ID (öffnet Overlay) |
| `page.isSyncingWithServer` | Speicher | `syncing` / `synced` / `error` |
| `page.editor` (`PageEditorInstance`) | Speicher | `editorRef`, `assetsList` (`apps/web/store/pages/page-editor-info.ts`) |
| `localStorage[IS_FAVORITE_MENU_OPEN]` | localStorage | Favoriten-Sektion nach Favorisieren öffnen |

### 2.5 Views (`apps/web/components/views/`, 16 Dateien, 1 503 Zeilen; ergänzend `apps/web/components/workspace/views/`, 9 Dateien, 916 Zeilen)

Die Work-Item-Darstellung innerhalb einer View (Layouts, Rich-Filter-Zeile, „Save view“/„Update view“ aus der Filterzeile) ist in Analyse 09 (§2.11, §3.8) beschrieben. Hier stehen Verwaltung, Liste, Formulare und Köpfe.

#### 2.5.1 Screens und Einstiegspunkte

| Screen / Dialog | Route bzw. Auslöser | Einstiegskomponente | Quelle |
|---|---|---|---|
| Projekt-View-Liste | `/:ws/projects/:projectId/views` | Page `ProjectViewsPage` → `ViewAppliedFiltersList` (`Header TERNARY`, bei Filtern) + `ProjectViewsList`; `issue_views_view === false` → „Views are not enabled for the project.“ + „Manage features“ (Admin) | `apps/web/app/(all)/[workspaceSlug]/(projects)/projects/(detail)/[projectId]/views/(list)/page.tsx` |
| Listenkopf | Layout-Header | `ProjectViewsHeader`: Breadcrumb Projekt › „Views“; rechts `ViewListHeader` (Suche, Sortierung, Filter ab `md`) + Button „Add view“ (**für alle Rollen**) → `toggleCreateViewModal(true)` | `.../views/(list)/header.tsx` |
| Mobile-Kopf | `< md` | `ViewMobileHeader`: Sortierung (mobil ohne Icon) + „Filters“ | `.../views/(list)/mobile-header.tsx` |
| Projekt-View-Detail | `/:ws/projects/:projectId/views/:viewId` | Page `ProjectViewIssuesPage` → `ProjectViewLayoutRoot` (Analyse 09); SWR `VIEW_DETAILS_${viewId}`; Fehler → `EmptyState` „View does not exist“ / „The view you are looking for does not exist or you don't have permission to view it.“ / „View other views“ | `.../views/(detail)/[viewId]/page.tsx` |
| Projekt-View-Kopf | Layout-Header | `ProjectViewIssuesHeader`: Breadcrumb › „Views“ › `BreadcrumbNavigationSelect` (alle Projekt-Views); Lock-Symbol mit Tooltip „Private“ bei privaten Views; `LayoutSelection` und „Display“ nur wenn **nicht** `is_locked`; `WorkItemFiltersToggle`; „Add work item“ (Admin/Member); `ViewQuickActions` (ab `md`) | `.../views/(detail)/[viewId]/header.tsx` |
| Projekt-View anlegen/bearbeiten | „Add view“, Empty-State-CTA, Menü „Edit“, „Save view“ in der Filterzeile (mit `preLoadedData`) | `CreateUpdateProjectViewModal` → `ProjectViewForm` | `modal.tsx`, `form.tsx` |
| Projekt-View löschen | Menü „Delete“ | `DeleteProjectViewModal` | `delete-view-modal.tsx` |
| Workspace-View-Liste | `/:ws/workspace-views` | Page `WorkspaceViewsPage`: Suchfeld (`InputGroup 2xl`, Placeholder „Search“) + Standard-Views (`GlobalDefaultViewListItem`: „All work items“, „Assigned“, „Created“, „Subscribed“) + eigene Views (`GlobalViewsList`) | `apps/web/app/(all)/[workspaceSlug]/(projects)/workspace-views/page.tsx` |
| Workspace-View-Detail | `/:ws/workspace-views/:globalViewId` | `AllIssueLayoutRoot isDefaultView` (Spreadsheet, Analyse 09) | `.../workspace-views/[globalViewId]/page.tsx` |
| Workspace-View-Kopf | Layout-Header | `GlobalIssuesHeader`: Breadcrumb „Views“ › Switcher (Standard- + eigene Views); `WorkItemFiltersToggle`; „Display“ (nicht bei `is_locked`, Optionen `ISSUE_DISPLAY_FILTERS_BY_PAGE.my_issues`); Button „Add view“ (alle Rollen); Quick-Actions (eigene bzw. Standard-View) | `.../workspace-views/header.tsx` |
| Workspace-View anlegen/bearbeiten | „Add view“, Menü „Edit“ | `CreateUpdateWorkspaceViewModal` → `WorkspaceViewForm` | `apps/web/components/workspace/views/modal.tsx`, `form.tsx` |
| Workspace-View löschen | Menü „Delete“ | `DeleteGlobalViewModal` | `apps/web/components/workspace/views/delete-view-modal.tsx` |

#### 2.5.2 Komponenten-Inventar (Projekt-Views, `apps/web/components/views/`)

| Datei | Export | Zweck / Darstellung | Abhängigkeiten |
|---|---|---|---|
| `views-list.tsx` | `ProjectViewsList` | Loader `ViewListLoader`; keine Treffer bei vorhandenen Views → `assetKey="search"` „No matching results.“; keine Views → `EmptyStateDetailed assetKey="view"` „Save custom views for your project“ + Beschreibung + CTA „Create view“ (Admin, Member **und Guest**) | `useProjectView`, `useCommandPalette` |
| `view-list-item.tsx` | `ProjectViewListItem` | `ListItem` mit Logo (16 px, `lucide`) oder `ViewsOutline`, Link zur View, Mobil-Quick-Actions | `ListItem` |
| `view-list-item-action.tsx` | `ViewListItemAction` | Zugriffs-Icon (Tooltip „Public“/„Private“), Badge „Live“ (`bg-success-subtle text-success-primary`, Punkt) wenn `anchor` gesetzt (veröffentlicht), Owner-Avatar, `FavoriteStar` (Admin/Member), Desktop-Quick-Actions; hostet Edit-/Lösch-Modal | `getPublishViewLink`, `useLocalStorage(IS_FAVORITE_MENU_OPEN)` |
| `view-list-header.tsx` | `ViewListHeader` | Suche (Placeholder „Search“), ab `md` `ViewOrderByDropdown` + „Filters“ (`isFiltersApplied` fest `false`) mit `ViewFiltersSelection` (Projektmitglieder) | `useProjectView.filters` |
| `filters/filter-selection.tsx` | `ViewFiltersSelection` | Suche, „Favorites“, „Created date“ (Presets `DATE_BEFORE_FILTER_OPTIONS` + Custom), „Created by“ (Filterschlüssel `owned_by`) | `FilterCreatedDate`, `FilterCreatedBy` |
| `filters/order-by.tsx` | `ViewOrderByDropdown` | „Name“, „Created at“, „Updated at“, Trenner, „Ascending“, „Descending“; mobil als Textbutton | `VIEW_SORTING_KEY_OPTIONS`, `VIEW_SORT_BY_OPTIONS` |
| `applied-filters/root.tsx` | `ViewAppliedFiltersList` | Chips `view_type` (Access), `created_at`, `owned_by`, „Clear all“ | `AppliedDateFilters`, `AppliedMembersFilters` |
| `applied-filters/access.tsx` | `AppliedAccessFilters` | Chip „Public“/„Private“ | `VIEW_ACCESS_SPECIFIERS` |
| `applied-filters/index.tsx` | Re-Export | – | – |
| `quick-actions.tsx` | `ViewQuickActions` | „…“-Menü (`aria-label` „More actions“) + Kontextmenü; Einträge `useViewMenuItems` (2.5.4); Platz für Publish-Eintrag (`useViewPublish` → CE `undefined`) | `quick-actions-helper.tsx`, `publish/use-view-publish.tsx` |
| `modal.tsx` | `CreateUpdateProjectViewModal` | `Dialog md`, `disablePointerDismissal`; Anlage → Navigation zur neuen View; Bearbeitung → `mutateFilters` + `resetExpression` | `useProjectView`, `useIssues(PROJECT_VIEW)`, `useWorkItemFilters` |
| `form.tsx` | `ProjectViewForm` | Titel „Create View“/„Update View“; Logo-Picker (`EmojiPicker iconType="lucide"`, `h-9 w-9 bg-surface-2`); Name (Pflicht „Title is required“, ≤255 „Title should be less than 255 characters“, Placeholder „Title“, `autoFocus`); Beschreibung; `LayoutDropDown` (5 Layouts) + „Display“-Dropdown (`DisplayFiltersSelection`); Rich-Filter-Zeile (`ProjectLevelWorkItemFiltersHOC isTemporary showOnMount`, `WorkItemFiltersRow variant="modal"`); Buttons „Cancel“, „Create View“/„Creating…“ bzw. „Update View“/„Updating…“ | `@/components/dropdowns/layout`, `work-item-filters/*` |
| `delete-view-modal.tsx` | `DeleteProjectViewModal` | `ConfirmDialog` „Are you sure you want to delete this view?“ / „If you confirm, all the sort, filter, and display options + the layout you have chosen for this view will be permanently deleted without any way to restore them.“; Erfolg → Push zur View-Liste + Toast „View deleted successfully.“ | `useProjectView.deleteView` |
| `helper.tsx` | `WorkspaceActiveLayout`, Typen `TWorkspaceLayoutProps`, `TLayoutSelectionProps` | Workspace-Views unterstützen nur `SPREADSHEET` (`WorkspaceSpreadsheetRoot`), andere Layouts rendern leer | `issue-layouts/spreadsheet/roots/workspace-root` |
| `publish/use-view-publish.tsx` | `useViewPublish` | CE-Stub: `isPublishModalOpen=false`, `publishContextMenu=undefined` | – |
| `publish/index.ts` | Re-Export | – | – |

#### 2.5.3 Komponenten-Inventar (Workspace-Views, `apps/web/components/workspace/views/`)

| Datei | Export | Zweck / Darstellung |
|---|---|---|
| `views-list.tsx` | `GlobalViewsList` | SWR `GLOBAL_VIEWS_LIST_${ws}` → `GET /api/workspaces/{ws}/views/`; Suche über Name |
| `view-list-item.tsx` | `GlobalViewListItem` | Zeile `h-[52px] p-4` (Name gekürzt auf 75 Zeichen, Beschreibung `text-11`), Menü „Edit View“/„Delete View“ (**ohne Rechteprüfung**) |
| `default-view-list-item.tsx` | `GlobalDefaultViewListItem` | Zeile für Standard-View (Link `/${ws}/workspace-views/${key}`) |
| `quick-action.tsx` | `WorkspaceViewQuickActions` | Menü über `useViewMenuItems` (Owner = Edit/Delete, Workspace-Admin = Delete) |
| `default-view-quick-action.tsx` | `DefaultWorkspaceViewQuickActions` | Menü „Open in new tab“, „Copy link“ |
| `form.tsx` | `WorkspaceViewForm` | Titel „Create View“/„Update View“ (`text-18`), Name, Beschreibung, „Display“ (Spreadsheet-Optionen), Rich-Filter (`WorkspaceLevelWorkItemFiltersHOC`, `EIssuesStoreType.GLOBAL`); Defaults `layout: spreadsheet`, `order_by: "-created_at"`; Buttons `size="sm"` |
| `modal.tsx` | `CreateUpdateWorkspaceViewModal` | Anlage → Toast „View created successfully.“ + Navigation; Bearbeitung sendet zusätzlich `query: {...rich_filters}`; Erfolg → `resetExpression(GLOBAL)` + Toast „View updated successfully.“ |
| `delete-view-modal.tsx` | `DeleteGlobalViewModal` | `ConfirmDialog` (Texte wie Projekt-View); entfernt `localStorage["global_view_filters/<id>"]`; schließt auch bei Fehler |
| `header.tsx` | `GlobalViewsHeader` | Tab-Leiste mit Quick-Actions je View + „+“-Button – **in CE von keiner Route verwendet** |

#### 2.5.4 Kontextmenü View (`useViewMenuItems`)

| # | Key | Text | sichtbar wenn | Aktion |
|---|---|---|---|---|
| 1 | `edit` | „Edit“ | Nutzer ist Owner (`owned_by`) | Modal mit Daten |
| 2 | `open-new-tab` | „Open in new tab“ | immer | neues Tab |
| 3 | `copy-link` | „Copy link“ | immer | Toast „Link Copied!“ / „View link copied to clipboard.“ |
| 4 | `delete` | „Delete“ | Owner **oder** Admin (Projekt-Admin bei Projekt-Views, Workspace-Admin bei Workspace-Views) | Lösch-Dialog |

Quelle: `apps/web/components/common/quick-actions-helper.tsx`.

#### 2.5.5 Services und Endpunkte (Views)

| Aufruf | HTTP | Endpunkt |
|---|---|---|
| `ViewService.getViews` | GET | `/api/workspaces/{ws}/projects/{pid}/views/` |
| `getViewDetails` | GET | `/api/workspaces/{ws}/projects/{pid}/views/{viewId}/` |
| `createView` | POST | `/api/workspaces/{ws}/projects/{pid}/views/` Body `{name, description, logo_props, rich_filters, display_filters, display_properties, access}` (Kanban ohne `group_by` → `group_by="state"`, `getValidatedViewFilters`) |
| `patchView` | PATCH | `/api/workspaces/{ws}/projects/{pid}/views/{viewId}/` |
| `deleteView` | DELETE | `/api/workspaces/{ws}/projects/{pid}/views/{viewId}/` |
| `getViewIssues` | GET | `.../views/{viewId}/issues/` (Work-Item-Liste, Analyse 09) |
| Favoriten | POST/DELETE | `/api/workspaces/{ws}/user-favorites/` (`entity_type:"view"`) |
| `WorkspaceService.getAllViews` | GET | `/api/workspaces/{ws}/views/` |
| `getViewDetails` | GET | `/api/workspaces/{ws}/views/{viewId}/` |
| `createView` | POST | `/api/workspaces/{ws}/views/` |
| `updateView` | PATCH | `/api/workspaces/{ws}/views/{viewId}/` |
| `deleteView` | DELETE | `/api/workspaces/{ws}/views/{viewId}/` |

Quellen: `apps/web/services/view.service.ts`, `apps/web/services/workspace.service.ts`, `apps/web/store/project-view.store.ts`, `apps/web/store/global-view.store.ts`.

#### 2.5.6 Clientseitige Zustände (Views)

| Zustand | Persistenz | Inhalt |
|---|---|---|
| `projectView.filters` | Speicher | `{searchQuery:"", sortBy:"desc", sortKey:"updated_at", filters?: {favorites?, created_at?, owned_by?, view_type?}}` |
| Workspace-View-Suche | lokaler React-State der Seite | Text |
| `localStorage["global_view_filters/<id>"]` | localStorage | Altlast, nur beim Löschen entfernt (Analyse 08 2.10) |

### 2.6 Analytics (`apps/web/components/analytics/`, 35 Dateien, 2 389 Zeilen)

#### 2.6.1 Screens und Einstiegspunkte

| Screen / Dialog | Route bzw. Auslöser | Einstiegskomponente | Quelle |
|---|---|---|---|
| Workspace-Analytics | `/:ws/analytics/:tabId` (`/:ws/analytics` → Redirect `overview`) | Page `AnalyticsPage`: `Tabs variant="contained"` (Tab-Leiste `border-b px-6 py-2`, rechts `AnalyticsFilterActions`), Panels je Tab; ohne Projekte (und `loader !== "init-loader"`) → `EmptyStateDetailed assetKey="project"` mit Button „Create a project“ (Admin/Member) | `apps/web/app/(all)/[workspaceSlug]/(projects)/analytics/[tabId]/page.tsx` |
| Tab „Overview“ | `tabId=overview` | `Overview` | `overview/root.tsx` |
| Tab „Work items“ | `tabId=work-items` | `WorkItems` | `work-items/root.tsx` |
| Analytics-Seitenpanel (Projekt/Cycle/Modul) | Button „Analytics“ in Projekt-Work-Items-, Cycle- und Modul-Köpfen (Desktop und mobil) | `WorkItemsModal` (rechts, `three-quarter` oder Vollbild) | `work-items/modal/*`, Konsumenten `apps/web/components/issues/filters.tsx`, `cycles/(detail)/header.tsx`, `cycles/(detail)/mobile-header.tsx`, `modules/(detail)/header.tsx`, `modules/(detail)/mobile-header.tsx`, `issues/(list)/mobile-header.tsx` |

#### 2.6.2 Komponenten-Inventar

| Datei | Export | Zweck / Darstellung | Datenquelle |
|---|---|---|---|
| `tabs.tsx` | `getAnalyticsTabs(t)` | Tabs `overview` („Overview“, `Overview`) und `work-items` („Work items“, `WorkItems`), beide `isDisabled:false` | – |
| `use-analytics-tabs.tsx` | `useAnalyticsTabs` | memoisierte Tabs | – |
| `analytics-wrapper.tsx` | `AnalyticsWrapper` (default) | `px-6 py-4`, Überschrift `text-20 font-bold mb-4 md:mb-6` | – |
| `analytics-section-wrapper.tsx` | `AnalyticsSectionWrapper` (default) | Abschnitt mit Titel `text-16 font-medium`, optionale `actions`; `subtitle` wird nicht angezeigt (auskommentiert) | – |
| `analytics-filter-actions.tsx` | `AnalyticsFilterActions` (default) | Projektauswahl (`select/project.tsx`) über beigetretene Projekte; Zeitraum-Dropdown auskommentiert | `useAnalytics.selectedProjects` |
| `select/project.tsx` | `ProjectSelect` | Mehrfach-`Select` mit Suche (Name + Identifier), Logo je Projekt; Trigger `select-md` mit `ProjectsOutline`: „All projects“ / Namen kommagetrennt / „3+ projects“ (> 3) | `useProject` |
| `select/duration.tsx` | `DurationDropdown` (default) | Zeitraum „Yesterday“, „Last 7 days“, „Last 30 days“, „Last 3 months“ – **ungenutzt** | `ANALYTICS_DURATION_FILTER_OPTIONS` |
| `select/analytics-params.tsx` | `AnalyticsSelectParams` | drei Selects: Y-Achse (Metrik), X-Achse (Eigenschaft, Icon `CalendarOutline`, Fallback „Add Property“), Gruppierung (Icon `PreferencesOutline`, Option „No value“); X und Gruppierung schließen sich gegenseitig aus | `ANALYTICS_X_AXIS_VALUES`, `ANALYTICS_Y_AXIS_VALUES` |
| `select/select-x-axis.tsx` | `SelectXAxis` | Select ohne Suche, optional „No value“ (`__no_value__`) | – |
| `select/select-y-axis.tsx` | `SelectYAxis` | Metriken „Work item“, „Estimate“, „Epic“; `ESTIMATE_POINT_COUNT` immer ausgeblendet (`hiddenOptions`), außerdem `EPIC_WORK_ITEM_COUNT` (bzw. im Epic-Modus `WORK_ITEM_COUNT`); Trigger-Fallback „Add Metric“ | `useProjectEstimates` |
| `total-insights.tsx` | `TotalInsights` (default) | Kennzahlen-Grid (`grid-cols-1 sm:grid-cols-2`, Desktop 5 bzw. 4 Spalten, Peek 2 Spalten) mit `InsightCard` je Feld aus `ANALYTICS_INSIGHTS_FIELDS[tab]` | `GET …/advance-analytics/?tab=…` |
| `insight-card.tsx` | `InsightCard` (default) | Label `text-13 text-tertiary`, Wert `text-20 font-bold`; Loader 50 px | – |
| `overview/root.tsx` | `Overview` | `TotalInsights overview` + Grid `md:grid-cols-5` mit `ProjectInsights` (3 Spalten) und `ActiveProjects` (2 Spalten) | – |
| `overview/project-insights.tsx` | `ProjectInsights` (default) | „Project Insights“: Radar-Chart (lazy `@plane/blocks/charts/radar-chart`, `h-[350px] lg:w-3/5`, Farbe `--text-color-accent-primary`, `fillOpacity 0.6`, Punkte r=4) + Liste „Summary of Projects“ / „All Projects“ / Kopf „Trend on charts“ · „Work items“ mit Name/Anzahl je Eintrag; leer → `EmptyStateCompact` „Create projects with work items and assignees to start tracking performance, progress, and team impact here.“ | `GET …/advance-analytics-charts/?type=projects` |
| `overview/active-projects.tsx` | `ActiveProjects` (default) | „Active Projects“: Liste (`h-[350px] overflow-auto`) der Projekte mit Fertigstellungsgrad; Loader 5×40 px | `GET /api/workspaces/{ws}/project-stats/?fields=total_work_items,total_completed_work_items` |
| `overview/active-project-item.tsx` | `ActiveProjectItem` (default) | Logo-Kachel `h-8 w-8 rounded-xl bg-layer-1`, Name (Tooltip), Prozent-Chip (> 50 % grün `bg-success-subtle`, sonst rot `bg-danger-subtle`) | `useProject` |
| `overview/index.ts` | Re-Export | – | – |
| `work-items/root.tsx` | `WorkItems` | `TotalInsights work-items`, `CreatedVsResolved`, `CustomizedInsights`, `WorkItemsInsightTable` | – |
| `work-items/created-vs-resolved.tsx` | `CreatedVsResolved` (default) | „Created vs Resolved“: `AreaChart h-[350px]` mit „Resolved“ (`completed_issues`, Linie `#198038`, Fläche `#19803833`) und „Created“ (`created_issues`, `#1192E8`/`#1192E833`), gestapelt, geglättet, ohne Punkte; X „Date“, Y „No. of Work items“ (Epic-Modus „No. of Epics“); Legende links unten | `GET …/advance-analytics-charts/?type=work-items` |
| `work-items/customized-insights.tsx` | `CustomizedInsights` (default) | „Customized Insights“ mit `AnalyticsSelectParams` (Defaults X=`PRIORITY`, Y=`WORK_ITEM_COUNT` bzw. Epic) und `PriorityChart` | react-hook-form |
| `work-items/priority-chart.tsx` | `PriorityChart` (default) | `BarChart h-[370px]` (`@plane/blocks/charts/bar-chart`): ohne Gruppierung ein Balken „Count“ mit Farbe aus `generateBarColor`; mit Gruppierung gestapelte Balken je Schema-Schlüssel (Farben aus `CHART_COLOR_PALETTES[0]` hell/dunkel, erweitert durch `generateExtendedColors`, Rundung nur am obersten/untersten Segment); darunter `DataTable` (Spalten X-Label + „Count“ + Schema-Spalten) mit Button „Export as csv“ | `GET …/advance-analytics-charts/?type=custom-work-items&x_axis=…&y_axis=…&group_by=…` |
| `work-items/utils.ts` | `generateBarColor` | Priorität: urgent `#ef4444`, high `#f97316`, medium `#eab308`, low `#22c55e`, sonst `#ced4da`; States: Statusfarbe, unbekannt → Hash der ID modulo Palette; sonst erste Palettenfarbe | `useProjectState.workspaceStates` |
| `work-items/workitems-insight-table.tsx` | `WorkItemsInsightTable` (default) | Tabelle je Projekt (Workspace) bzw. je Assignee (Peek): Spalten „Project“/„Assignee“ (Logo bzw. Avatar/Initiale/„Unassigned“), „Backlog“, „Started“, „Unstarted“, „Completed“, „Cancelled“; CSV-Export der gefilterten Zeilen | `GET …/advance-analytics-stats/?type=work-items` |
| `work-items/index.ts` | Re-Exports | – | – |
| `work-items/modal/index.tsx` | `WorkItemsModal` | `ModalPortal` (`@plane/blocks/portal`) rechts, Breite `three-quarter` / `full`, ohne Overlay, Outside-Click schließt; Rahmen `border-l` bzw. Vollbild `rounded-lg border` | `useAnalytics` |
| `work-items/modal/header.tsx` | `WorkItemsModalHeader` | Titel „Analytics for <Projekt> in <Cycle> in <Modul>“; Buttons Vollbild (`FullScreenOutline`/`ArrowCollapseOutline`, ab `md`) und Schließen | – |
| `work-items/modal/content.tsx` | `WorkItemsModalMainContent` | setzt beim Mount `isPeekView=true`, Projekt, Cycle, Modul im Analytics-Store (Cleanup beim Unmount); Spinner bis konfiguriert; Inhalt wie Tab „Work items“ (`p-6`) | `useAnalytics` |
| `insight-table/root.tsx` | `InsightTable` | Loader (`TableLoader`, 5 Zeilen) oder `DataTable` mit Platzhalter „<Anzahl> <headerText>“ und Export-Button | – |
| `insight-table/data-table.tsx` | `DataTable` | TanStack-Table (`@tanstack/react-table`) mit Propel `Table variant="table"`; Suchfeld (filtert erste Spalte, ausklappbar), leer → `EmptyStateCompact` | – |
| `insight-table/loader.tsx` | `TableLoader` | Skeleton-Tabelle | – |
| `insight-table/index.ts` | Re-Export | – | – |
| `export.ts` | `csvConfig`, `exportCSV` | `export-to-csv`: Trenner `,`, Dezimal `.`, Dateiname `${workspaceSlug}-analytics`, Spaltennamen aus `meta.export.label ?? key`, leere Zellen `-` | `export-to-csv` |
| `loaders.tsx` | `ProjectInsightsLoader`, `ChartLoader` | Skeletons 200 px bzw. 350 px | – |
| `empty-state.tsx` | `AnalyticsEmptyState` (default) | Bild mit Hintergrundbild, Titel, Beschreibung – **ungenutzt** | – |
| `trend-piece.tsx` | `TrendPiece` (default) | Prozent-Badge (≥ 66 grün, 33–65 gelb, < 33 rot; Varianten simple/outlined/tinted) – **ungenutzt** (auskommentiert) | – |

#### 2.6.3 Kennzahlen (`ANALYTICS_INSIGHTS_FIELDS`, `packages/constants/src/analytics/common.ts`)

| Tab | Schlüssel (Antwortfeld) | Label (en) |
|---|---|---|
| `overview` | `total_users`, `total_admins`, `total_members`, `total_guests`, `total_projects`, `total_work_items`, `total_cycles`, `total_intake` | „Total Users“, „Total Admins“, „Total Members“, „Total Guests“, „Total Projects“, „Total Work items“, „Total Cycles“, „Total Intake“ |
| `work-items` | `total_work_items`, `started_work_items`, `backlog_work_items`, `un_started_work_items`, `completed_work_items` | „Total Work items“, „Started Work items“, „Backlog Work items“, „Unstarted Work items“, „Completed Work items“ (Epic-Modus: „Epics“) |

Jedes Feld liefert `{count, filter_count}` (`IAnalyticsResponseFields`); angezeigt wird `count`.

#### 2.6.4 X-/Y-Achsen

| Konstante | Werte (Label) |
|---|---|
| `ANALYTICS_X_AXIS_VALUES` | `STATES` (State name), `STATE_GROUPS` (State group), `PRIORITY` (Priority), `LABELS` (Label), `ASSIGNEES` (Assignee), `ESTIMATE_POINTS` (Estimate point), `CYCLES` (Cycle), `MODULES` (Module), `COMPLETED_AT` (Completed date), `TARGET_DATE` (Due date), `START_DATE` (Start date), `CREATED_AT` (Created date) |
| `ANALYTICS_Y_AXIS_VALUES` | `WORK_ITEM_COUNT` (Work item), `ESTIMATE_POINT_COUNT` (Estimate), `EPIC_WORK_ITEM_COUNT` (Epic) |
| `ChartXAxisProperty` (vollständig, `packages/types/src/analytics.ts`) | zusätzlich `CREATED_BY`, `WORK_ITEM_TYPES`, `PROJECTS`, `EPICS` (in CE nicht angeboten) |
| `ChartYAxisMetric` (vollständig) | zusätzlich `PENDING_WORK_ITEM_COUNT`, `COMPLETED_WORK_ITEM_COUNT`, `IN_PROGRESS_WORK_ITEM_COUNT`, `WORK_ITEM_DUE_THIS_WEEK_COUNT`, `WORK_ITEM_DUE_TODAY_COUNT`, `BLOCKED_WORK_ITEM_COUNT` (in CE nicht angeboten) |

#### 2.6.5 Endpunkte (`apps/web/services/analytics.service.ts`)

URL-Bildung `processUrl`: Basis `/api/workspaces/{ws}`; im Peek-Modus (`isPeekView`) für `work-items` und `custom-work-items` zusätzlich `/projects/{erste project_id}` (fehlt `project_ids` → Exception „project_ids parameter is required for peek view of work items“).

| Aufruf | Endpunkt | Query |
|---|---|---|
| `getAdvanceAnalytics` | `GET {basis}/advance-analytics/` | `tab`, `project_ids?` (kommagetrennt), `cycle_id?`, `module_id?`, `epic?` |
| `getAdvanceAnalyticsStats` | `GET {basis}/advance-analytics-stats/` | `type=work-items` + Filter |
| `getAdvanceAnalyticsCharts` | `GET {basis}/advance-analytics-charts/` | `type=projects\|work-items\|custom-work-items` + Filter (+ `x_axis`, `y_axis`, `group_by` bei `custom-work-items`) |
| `ProjectService.getProjectAnalyticsCount` | `GET /api/workspaces/{ws}/project-stats/` | `fields=total_work_items,total_completed_work_items` |

#### 2.6.6 Analytics-Store (`apps/web/store/analytics.store.ts`)

| Feld | Default | Bedeutung |
|---|---|---|
| `currentTab` | `overview` | ungenutzt |
| `selectedProjects` | `[]` | Projektfilter (leer = alle) |
| `selectedDuration` | `last_30_days` | wird in SWR-Schlüssel eingebaut, aber nicht gesendet (`date_filter` auskommentiert) |
| `selectedCycle`, `selectedModule` | `""` | vom Peek-Modal gesetzt |
| `isPeekView` | `false` | Peek-Modus (Projekt-URL, Assignee- statt Projektspalte) |
| `isEpic` | `false` | Epic-Modus (nur im Peek gemäß `isEpic`-Prop, in CE nie gesetzt) |

### 2.7 Chart-Hilfen (`apps/web/components/chart/utils.ts`, 1 Datei, 178 Zeilen)

| Funktion | Verhalten | Konsument |
|---|---|---|
| `parseChartData(data, xAxisProperty, groupByProperty, xAxisDateGrouping)` | klont `data.data`/`schema`; ergänzt in jedem Datensatz fehlende Schema-Schlüssel mit `0`; X-Werte bei `PRIORITY`/`STATE_GROUPS` großschreiben (erstes Zeichen); Datums-X (`START_DATE`, `TARGET_DATE`, `CREATED_AT`, `COMPLETED_AT`) nach Gruppierung formatieren; Schema-Labels analog für Gruppierung | `analytics/work-items/priority-chart.tsx` |
| `getDateGroupingName(date, grouping)` (intern) | leer/„none“/„null“ → „None“; ungültig → Rohwert; `DAY`: aktuelles Jahr ohne Jahr (`renderFormattedDateWithoutYear`), sonst mit Jahr; `WEEK`: „<MMM>, Week <n>“ (`getWeekOfMonth`); `MONTH`: „MMM“ bzw. „MMM, yyyy“; `YEAR`: Jahr | dito (Standard `DAY`) |
| `generateExtendedColors(baseColorSet, targetCount)` | liefert `targetCount` Farben: Basisfarben, danach HSL-Interpolation zwischen nach Farbton sortierten Basisfarben mit Sättigung/Helligkeit begrenzt auf 40–60 und 80/20-Mischung mit dem Mittelwert | dito |

Die in diesem Bereich genutzten Chart-Komponenten `AreaChart` (`@plane/blocks/charts/area-chart`), `BarChart` (`@plane/blocks/charts/bar-chart`) und `RadarChart` (`@plane/blocks/charts/radar-chart`) sind recharts-Wrapper aus `@plane/blocks` (Analyse 13a/13b).

### 2.8 Intake/Inbox (`apps/web/components/inbox/`, 41 Dateien, 4 280 Zeilen)

Begriff: In der UI „Intake“, im Code und in der API `inbox`/`inbox-issues`. Ein Intake-Eintrag (`TInboxIssue`) umschließt ein Work Item (`issue`) mit Status, Snooze-Datum, Duplikat-Verweis und Quelle.

#### 2.8.1 Screens und Einstiegspunkte

| Screen / Dialog | Route bzw. Auslöser | Einstiegskomponente | Quelle |
|---|---|---|---|
| Intake-Seite | `/:ws/projects/:projectId/intake?currentTab=open\|closed&inboxIssueId=<issueId>` (`/inbox` → Redirect) | Page `ProjectInboxPage` → `InboxIssueRoot` (`inboxAccessible = project.inbox_view`); `inbox_view === false` → „Intake is not enabled for the project.“ + „Manage features“ (Admin); Seitentitel „<Projekt> - Intake“ | `apps/web/app/(all)/[workspaceSlug]/(projects)/projects/(detail)/[projectId]/intake/page.tsx` |
| Intake-Kopf | Layout-Header | `ProjectInboxHeader`: Breadcrumb Projekt › „Intake“; während `pagination-loading` „Syncing...“ mit drehendem `RefreshOutline`; Button „Add work item“ (Admin, Member **und Guest**, nur bei `inbox_view`) | `apps/web/components/projects/settings/intake/header.tsx`, `.../intake/layout.tsx` |
| Liste (linke Spalte) | immer | `InboxSidebar` (Desktop `lg:w-2/6`, mobil verschiebbare Ebene `absolute top-[50px]`) | `sidebar/root.tsx` |
| Detail (rechte Spalte) | `inboxIssueId` gesetzt | `InboxContentRoot` → `InboxIssueActionsHeader` + `InboxIssueMainContent`; ohne Auswahl `EmptyStateCompact assetKey="intake"` „Select an Intake work item to view its details“ | `content/*` |
| Intake-Eintrag anlegen | „Add work item“ | `InboxIssueCreateModalRoot` → `InboxIssueCreateRoot` | `modals/create-modal/*` |
| Annehmen („Move … to project work items“) | „Accept“ | `CreateUpdateIssueModal` (Analyse 09 2.16) mit Titel „Move <PROJ-123> to project work items“, Button „Add to project“/„Adding“ | `content/inbox-issue-header.tsx` |
| Ablehnen | „Decline“ | `DeclineIssueModal` | `modals/decline-issue-modal.tsx` |
| Zurückstellen | Menü „Snooze“ | `InboxIssueSnoozeModal` | `modals/snooze-issue-modal.tsx` |
| Als Duplikat markieren | Menü „Mark as duplicate“ | `SelectDuplicateInboxIssueModal` | `modals/select-duplicate.tsx` |
| Löschen | Menü „Delete“ | `DeleteInboxIssueModal` | `modals/delete-issue-modal.tsx` |
| Einbettung in Benachrichtigungen | Workspace-Inbox (Benachrichtigung zu Intake-Item) | `InboxContentRoot isNotificationEmbed` (ohne Tastaturnavigation/Vor-Zurück, Pfeil-Button `ArrowNarrowRightOutline` schließt) | `apps/web/components/workspace-notifications/root.tsx` |

#### 2.8.2 Komponenten-Inventar

| Datei | Export | Zweck / Darstellung |
|---|---|---|
| `index.ts` | Re-Export `root` | – |
| `root.tsx` | `InboxIssueRoot` | Initiales Laden (Tab-Wechsel bzw. Projektwechsel → `handleCurrentTab`, sonst `fetchInboxIssues(…, tab\|\|OPEN)`); `init-loading` → `InboxLayoutLoader`; `init-error` → Icon `IntakeOutline size-[60px]` + Fehlertext „Error fetching the intake work items please try again later.“; mobiler Umschalter `LeftSidePaneOutline` (`lg:hidden`, aktiv `text-accent-primary`) |
| `sidebar/root.tsx` | `InboxSidebar` | `Header SECONDARY`: `Tabs variant="underline"` „Open“ (aktiv mit Zähler-Pill `bg-accent-primary/20 text-11 font-semibold` = `total_results`) / „Closed“; rechts `FiltersRoot`; darunter Applied-Filters; Liste mit Endlos-Laden (IntersectionObserver, `rootMargin "20%"`, Loader 2×64 px); Leerzustände: mit Filtern „No matching results.“, Open „Log Intake requests“ + Beschreibung + CTA „Create Intake request“, Closed „No request closed yet“ / „All the work items whether accepted or declined can be found here.“ (hart kodiert); Auto-Auswahl des ersten Eintrags |
| `sidebar/inbox-list.tsx` | `InboxIssueList` | Map über IDs |
| `sidebar/inbox-list-item.tsx` | `InboxIssueListItem` | Link `…/intake?currentTab=<tab>&inboxIssueId=<id>`; Zeile `py-4 border-b-subtle-1 hover:bg-accent-primary/5`, ausgewählt `border border-accent-strong`; Kopf `<IDENT>-<seq>` (`text-11 font-medium text-tertiary`) + Status-Badge (nicht bei `PENDING`); Titel `text-13 truncate`; Fuß: Erstellungsdatum (Tooltip „Created on: …“), Trennpunkt, `PriorityIcon` (Tooltip „Priority: …“), Labels (> 3 → Sammel-Chip „N labels“ mit orangem Punkt, sonst je Label Chip mit Farbpunkt), Ersteller-Avatar (E-Mail enthält `intake@plane.so` → Avatar „P“ alt „Plane“) |
| `inbox-issue-status.tsx` | `InboxIssueStatus` | Badge mit Icon und Text aus `INBOX_STATUS`; Snoozed zeigt „N day(s) to go“; abgelaufener Snooze → nichts |
| `inbox-status-icon.tsx` | `InboxStatusIcon`, `ICON_PROPERTIES` | Icons/Farben je Status (siehe 2.8.4) |
| `content/root.tsx` | `InboxContentRoot` | lädt Eintrag per SWR `PROJECT_INBOX_ISSUE_DETAIL_${ws}_${pid}_${id}`; nicht (mehr) in Liste → `router.replace(…/intake?currentTab=<tab>)`; berechnet Bearbeitbarkeit |
| `content/inbox-issue-header.tsx` | `InboxIssueActionsHeader` | Desktop-Kopf (`lg:flex`, `z-15`): Identifier `text-14 font-medium text-tertiary`, Status-Badge, Speicherstatus `NameDescriptionUpdateStatus`; rechts „Previous work item“/„Next work item“ (`ChevronUp/Down`), „Accept“ (`TickCircleFilled text-success-secondary`), „Decline“ (`CloseCircleFilled text-danger-secondary`), bei abgeschlossenen Einträgen „Copy work item link“ + „Open work item“, sonst „…“-Menü mit „Snooze“/„Un snooze“, „Mark as duplicate“, „Copy work item link“, „Delete“; hostet alle Modals |
| `content/inbox-issue-mobile-header.tsx` | `InboxIssueActionsMobileHeader` | Mobil-Kopf (`lg:hidden`): Sidebar-Toggle, Vor/Zurück, Status, Menü mit „Copy work item link“, „Open work item“ (abgeschlossen), „Snooze“/„Un-snooze“, „Mark as duplicate“, „Accept“, „Decline“, „Delete“ (danger) |
| `content/issue-root.tsx` | `InboxIssueMainContent` | Titel (`IssueTitleInput`), Beschreibung (`DescriptionInput`, Auto-Save, Migrations-Updates mit `skip_activity`), Reaktionen, Beschreibungs-Versionen (`DescriptionVersionsRoot`, nur editierbar; Ersteller bei Quelle `FORMS` = „Intake Form user“), Anhänge (`IssueAttachmentRoot`), Eigenschaften, Activity (`IssueActivity isIntakeIssue`); Reload-Warnung während Speichern; Status „submitted“ → nach 3 s „saved“ |
| `content/issue-properties.tsx` | `InboxIssueContentProperties` | „Properties“ (`text-body-sm-medium`): State (angenommen → `StateSelect`, sonst `IntakeStateSelect`; immer disabled), Assignees (`MemberSelect multiple select-ghost-md`, „Add assignees“), Priority, Due date (`DateSelect`, `minDate = start_date`, löschbar), Labels (`IssueLabel isInboxIssue`), „Duplicate of“ (Chip `<IDENT>-<seq>` mit Tooltip Name, Link); nicht editierbar → `opacity-60` |
| `content/index.ts` | Re-Exports | – |
| `modals/create-modal/modal.tsx` | `InboxIssueCreateModalRoot` | `Dialog size="lg"`, `disablePointerDismissal` |
| `modals/create-modal/create-root.tsx` | `InboxIssueCreateRoot`, `defaultIssueData` | Titel „Create intake work item“; Titel-, Beschreibungs-, Eigenschaftsfelder; Fuß: Schalter „Create more“, „Discard“, „Create work item“/„Creating“; Escape/Discard nur wenn Editor bereit („Editor is still processing changes. Please wait before proceeding.“) |
| `modals/create-modal/issue-title.tsx` | `InboxIssueTitle` | `Input 2xl` Placeholder „Title“, `required`; > 255 Zeichen → „Title should be less than 255 characters“ |
| `modals/create-modal/issue-description.tsx` | `InboxIssueDescription` | `RichTextEditor` (`id="inbox-modal-editor"`, ohne Drag&Drop, Mentions mit `project_id`, Upload/Duplicate von Assets `ISSUE_DESCRIPTION`, Enter → Submit-Button klicken), Container `bg-layer-2 border-[0.5px] border-subtle-1 py-3 min-h-[150px]` |
| `modals/create-modal/issue-properties.tsx` | `InboxIssueProperties` | sichtbar: `IntakeStateSelect`, `PrioritySelect`, `MemberSelect` (Assignees), `LabelSelect`, Due date; nur bei `isVisible` (in CE nie): Start date, Cycle, Modules, Estimate, Parent („Add parent“ / Menü „Change parent work item“, „Remove parent work item“, `ParentIssuesListModal`) |
| `modals/create-modal/index.ts` | Re-Export | – |
| `modals/decline-issue-modal.tsx` | `DeclineIssueModal` | `ConfirmDialog` „Decline work item“ / „Are you sure you want to decline work item <IDENT-seq>? This action cannot be undone.“ / „Decline“/„Declining“ |
| `modals/delete-issue-modal.tsx` | `DeleteInboxIssueModal` | `ConfirmDialog` „Delete work item“ / „Are you sure you want to delete work item <IDENT-seq>? The work item will only be deleted from the intake and this action cannot be undone.“; Toast „Success“ / „Work item deleted successfully“ |
| `modals/snooze-issue-modal.tsx` | `InboxIssueSnoozeModal` | `Dialog size="xs"` mit Kalender (frühestens morgen in Projekt-Zeitzone), Button „Snooze“ |
| `modals/select-duplicate.tsx` | `SelectDuplicateInboxIssueModal` | `Dialog md` mit Inline-`Combobox`: Suche (Placeholder „Type to search“, 500 ms Debounce, Server-Suche im Projekt), Überschrift „Select work item“ (leere Suche), Einträge mit State-Farbpunkt + `<IDENT>-<seq>` + Name; leer „No work items found“ / „No matching work items found“; Loader 4×40 px |
| `inbox-filter/root.tsx` | `FiltersRoot` | `FiltersDropdown` (Breite > 1280 px: Button „Filters“ mit Chevron, sonst nur Icon) + `InboxIssueOrderByDropdown` |
| `inbox-filter/index.ts` | Re-Export | – |
| `inbox-filter/sorting/order-by.tsx` | `InboxIssueOrderByDropdown` | Menü „Created at“, „Updated at“, „ID“, Trenner, „Ascending“, „Descending“; Trigger > 1280 px mit Label |
| `inbox-filter/filters/filter-selection.tsx` | `InboxIssueFilterSelection` | Sektionen: „Work item Status“, „Priority“, „Assignees“, „Created By“, „Label“, „Created date“, „Last updated date“ |
| `inbox-filter/filters/status.tsx` | `FilterStatus` | Tab Open: Pending, Snoozed; Tab Closed: Declined, Accepted, Duplicate; letzte Auswahl kann nicht abgewählt werden (mind. 1) |
| `inbox-filter/filters/priority.tsx` | `FilterPriority` | `ISSUE_PRIORITIES` mit `PriorityIcon` |
| `inbox-filter/filters/members.tsx` | `FilterMember` | Projektmitglieder, „You“, Sortierung gewählt/eigener/alphabetisch, 5 + „View all“/„View less“ |
| `inbox-filter/filters/labels.tsx` | `FilterLabels` | Projekt-Labels mit Farbpunkt, 5 + „View all“ |
| `inbox-filter/filters/date.tsx` | `FilterDate` | Einfachauswahl „Today“, „Yesterday“, „Last 7 days“, „Last 30 days“, „Custom“ (`DateFilterModal`, Titel immer „Created date“) |
| `inbox-filter/filters/state.tsx` | `FilterState` | State-Filter – **nicht eingebunden** |
| `inbox-filter/applied-filters/root.tsx` | `InboxIssueAppliedFilters` | `Header TERNARY` mit Chips Status, State, Priority, Assignees, Created By, Label, Created date, Updated date |
| `inbox-filter/applied-filters/status.tsx`, `state.tsx`, `priority.tsx`, `member.tsx`, `label.tsx`, `date.tsx` | `InboxIssueAppliedFilters*` | Chip-Gruppen; Status ohne Gesamt-„x“ und ohne „x“ am letzten Wert; übrige mit Wert-„x“ und Gruppen-„x“ (setzt `undefined`); Datum „<After/Before> <Datum>“ |

#### 2.8.3 Aktionen im Detail-Kopf – Sichtbarkeit

| Aktion | sichtbar wenn | zusätzlich ausführbar nur für | Ergebnis |
|---|---|---|---|
| Accept | Admin/Member und Status ∈ {Pending, Snoozed} | Projekt-Admin (sonst Toast „Permission denied“ / „Only project admins can accept work items“) | Modal „Move … to project work items“ |
| Decline | wie Accept | Projekt-Admin („Only project admins can deny work items“) | Bestätigungsdialog |
| Snooze / Un snooze | wie Accept (im „…“-Menü) | Projekt-Admin („Only project admins can snooze/Un-snooze work items“) | Kalender bzw. sofortiges Aufheben |
| Mark as duplicate | wie Accept | Projekt-Admin („Only project admins can mark work item as duplicate“) | Auswahl-Dialog |
| Copy work item link | immer (Menü bzw. Button bei abgeschlossen) | – | Toast „Link copied!“ / „Work item link copied to clipboard“ |
| Open work item | Status ∈ {Declined, Accepted, Duplicate} | – | Navigation zur Work-Item-URL (`generateWorkItemLink`), Cmd/Ctrl-Klick neues Tab |
| Delete | Projekt-Admin oder Ersteller des Work Items (Desktop-Menü nur sichtbar, wenn Admin/Member) | – | Bestätigungsdialog |

Quelle: `content/inbox-issue-header.tsx`, `content/inbox-issue-mobile-header.tsx`.

#### 2.8.4 Status (`EInboxIssueStatus`, `packages/types/src/inbox.ts`; `INBOX_STATUS`, `packages/constants/src/intake.ts`)

| Wert | Key | Titel | Icon | Farben (Text/Hintergrund) | Tab |
|---|---|---|---|---|---|
| `-2` | `pending` | Pending | `WarningTriangleOutline` | `text-warning-primary` / `bg-warning-subtle` | Open |
| `-1` | `declined` | Declined | `CloseCircleOutline` | `text-danger-primary` / `bg-danger-subtle` | Closed |
| `0` | `snoozed` | Snoozed („N days to go“) | `ClockOutline` | `text-placeholder` / `bg-layer-3` (abgelaufen: `text-danger-primary` / `bg-danger-subtle`) | Open |
| `1` | `accepted` | Accepted | `TickCircleOutline` | `text-success-primary` / `bg-success-subtle` | Closed |
| `2` | `duplicate` | Duplicate | `CopyOutline` | `text-secondary` / `bg-layer-3` | Closed |

Quellen: `EInboxIssueSource` = `IN_APP`, `FORMS`, `EMAIL` (Web legt immer `IN_APP` an).

#### 2.8.5 Endpunkte (Intake)

| Aufruf | HTTP | Endpunkt |
|---|---|---|
| `InboxIssueService.list` | GET | `/api/workspaces/{ws}/projects/{pid}/inbox-issues/?status=…&priority=…&assignees=…&created_by=…&labels=…&created_at=…&updated_at=…&order_by=…&per_page=10&cursor=10:{n}:0` |
| `retrieve` | GET | `.../inbox-issues/{issueId}/?expand=issue_inbox` |
| `create` | POST | `.../inbox-issues/` Body `{source:"IN_APP", issue:{name, description_html, priority, state_id, label_ids, assignee_ids, target_date}}` |
| `update` | PATCH | `.../inbox-issues/{issueId}/` Body `{status}` bzw. `{status:0, snoozed_till:"YYYY-MM-DD"}` / `{status:-2, snoozed_till:null}` / `{status:2, duplicate_to}` |
| `updateIssue` | PATCH | `.../inbox-issues/{issueId}/` Body `{issue:{…}}` |
| `destroy` | DELETE | `.../inbox-issues/{issueId}/` |
| `IntakeWorkItemVersionService.listDescriptionVersions` | GET | `/api/workspaces/{ws}/projects/{pid}/intake-work-items/{id}/description-versions/` |
| `retrieveDescriptionVersion` | GET | `.../intake-work-items/{id}/description-versions/{versionId}/` |
| `ProjectService.projectIssuesSearch` | GET | `/api/workspaces/{ws}/projects/{pid}/search-issues/?search=…&workspace_search=false` |
| Intake-State | GET | `/api/workspaces/{ws}/projects/{pid}/intake-state/` |
| `FileService.updateBulkProjectAssetsUploadStatus` | POST | `/api/assets/v2/workspaces/{ws}/projects/{pid}/{issueId}/bulk/` Body `{asset_ids}` (nach Anlage, Analyse 07) |
| Detail-Ladevorgang zusätzlich | GET | Reaktionen, Activities, Kommentare, Anhänge des Work Items (Analyse 09 2.15) |

Quellen: `apps/web/services/inbox/inbox-issue.service.ts`, `apps/web/services/inbox/intake-work_item_version.service.ts`, `apps/web/store/inbox/*`.

#### 2.8.6 Clientseitige Zustände (Intake)

| Zustand | Persistenz | Inhalt |
|---|---|---|
| `projectInbox.currentTab` | Speicher (+ URL `currentTab`) | `open` (Default) / `closed` |
| `filtersMap[projectId]` | Speicher | `TInboxIssueFilter` (`status`, `priority`, `assignees`, `created_by`, `labels`, `state`, `created_at`, `updated_at`); Default Open `status:[-2]`, Closed `status:[1,-1,2]` |
| `sortingMap[projectId]` | Speicher | `{order_by:"issue__created_at", sort_by:"desc"}` |
| `inboxIssueIds`, `inboxIssues`, `inboxIssuePaginationInfo` | Speicher | Liste, Instanzen (`InboxIssueStore`), Cursor/Totals |
| `loader` | Speicher | `init-loading`, `filter-loading`, `mutation-loading`, `pagination-loading`, `issue-loading` |
| Query `inboxIssueId` | URL | ID des **Work Items** (nicht des Intake-Datensatzes) |
| `project.intake_count` | Speicher (Projekt-Store) | Zähler offener Pending-Einträge (Sidebar-Badge), wird bei Statuswechseln lokal angepasst |

### 2.9 Estimates (`apps/web/components/estimates/`, 23 Dateien, 1 868 Zeilen)

#### 2.9.1 Screens und Dialoge

| Screen / Dialog | Route bzw. Auslöser | Einstiegskomponente | Quelle |
|---|---|---|---|
| Projekt-Einstellungen „Estimates“ | `/:ws/settings/projects/:projectId/estimates` | Page `EstimatesSettingsPage` (Titel `<Projekt> - Estimates`, nur Projekt-Admin, sonst `NotAuthorizedView isProjectView`) → `EstimateRoot isAdmin` | `apps/web/app/(all)/[workspaceSlug]/(settings)/settings/projects/[projectId]/estimates/page.tsx`, `root.tsx` |
| Schätzsystem anlegen (2 Schritte) | Empty-State-CTA „Add estimate system“ | `CreateEstimateModal` | `create/modal.tsx` |
| Schätzsystem löschen | Papierkorb-Button am aktiven System | `DeleteEstimateModal` | `delete/modal.tsx` |

Aufbau `EstimateRoot`:
1. `EstimateLoaderScreen` (4 × `Loader.Item` 40 px) solange `loader === "init-loader"` oder die SWR-Abfrage `PROJECT_ESTIMATES_<ws>_<pid>` läuft.
2. `SettingsHeading` „Estimates“ / „Set up estimation systems to track and communicate the effort required for each work item.“
3. Mit aktivem System (`currentActiveEstimateId` = Estimate des Projekts mit `last_used === true`):
   - `SettingsBoxedControlItem` „Enable estimates for my project“ / „They help you in communicating complexity and workload of the team.“ mit `EstimateDisableSwitch`.
   - Abschnitt `SettingsHeading variant="h6"` „Estimates list“ (hart kodiert) mit `EstimateList` für genau dieses System (`isEditable`).
4. Ohne aktives System: `EmptyStateCompact assetKey="estimate"` „No estimates yet“ / „Define how your team measures effort and track it consistently across all work items.“ / CTA „Add estimate system“.
5. Archivierte Systeme (`archivedEstimateIds` = `last_used === false`): Überschrift „Archived estimates“ mit Text „Estimates have gone through a change, these are the estimates you had in your older versions which were not in use. Read more about them here.“. Der Link „here.“ zeigt auf `https://docs.plane.so/core-concepts/projects/run-project#estimate` (externer Link, im Airgap-Betrieb nicht erreichbar). Darunter `EstimateList` ohne Aktionen.

#### 2.9.2 Komponenten-Inventar

| Datei | Export | Zweck / Darstellung (Texte en) | Store / Endpunkt |
|---|---|---|---|
| `root.tsx` | `EstimateRoot` | siehe 2.9.1; hält `estimateToUpdate` (wird gesetzt, aber nie verwendet) und `estimateToDelete` | `useProjectEstimates().getProjectEstimates` → `GET /api/workspaces/{ws}/projects/{pid}/estimates/` |
| `index.ts` | Re-Export `root` | – | – |
| `estimate-disable-switch.tsx` | `EstimateDisableSwitch` | `Switch size="sm"` (`aria-label` „Toggle estimates“), an ⇔ `project.estimate` gesetzt; deaktiviert ohne Admin; Toasts „Success!“ / „Estimates have been enabled.“ bzw. „Estimates have been disabled.“, Fehler „Error!“ / „Estimate could not be disabled. Please try again“ | `updateProject(ws,pid,{estimate: aktiv ? null : currentActiveEstimateId})` → `PATCH /api/workspaces/{ws}/projects/{pid}/` |
| `estimate-list.tsx` | `EstimateList` | rendert `EstimateListItem` je ID; leer → nichts | – |
| `estimate-list-item.tsx` | `EstimateListItem` | `SettingsBoxedControlItem`: Titel = `estimate.name`, Beschreibung = Werte kommagetrennt (Typ `time` über `convertMinutesToHoursMinutesString`) | `useEstimate(id).estimatePointIds/estimatePointById` |
| `estimate-list-item-buttons.tsx` | `EstimateListItemButtons` | nur für Admin und `isEditable`: Button `h-6 w-6 rounded-sm hover:bg-layer-1` mit `DeleteOutline` 12 px; `onEditClick` wird nicht ausgewertet | – |
| `create/modal.tsx` | `CreateEstimateModal` | `Dialog` (`disablePointerDismissal`, Escape wird ignoriert), `DialogContent size="md"`; Kopf `DialogProgression` „Step {1\|2} of 2“ mit Zurück-`IconButton` (`ChevronLeftOutline`, `aria-label` „Go back“) in Schritt 2; Titel „New estimate system“; Body Schritt 1 `EstimateCreateStageOne`, Schritt 2 `EstimatePointCreateRoot`; Footer „Cancel“ (secondary md) und in Schritt 2 „Create estimate“ / „Creating“ (primary md) | `createEstimate(ws,pid,{estimate:{name, type, last_used:true}, estimate_points})` → `POST /api/workspaces/{ws}/projects/{pid}/estimates/` |
| `create/stage-one.tsx` | `EstimateCreateStageOne` | `RadioInput` „Choose an estimate system“ mit „Points“ und „Categories“ (Time durch `isEstimateSystemEnabled` entfernt; Zweige für „Coming soon“-Tooltip und `UpgradeBadge` bleiben unerreicht); Abschnitt „Start from scratch“ → Kachel „Custom“ / „Add your own {points\|categories} from scratch.“ (Text hart kodiert, TODO Übersetzung); Abschnitt „Choose a template“ → Grid `grid-cols-1 gap-3 lg:grid-cols-2`, je nicht verstecktem Template Titel + Werte | `ESTIMATE_SYSTEMS` |
| `create/helper.tsx` | `isEstimateSystemEnabled` | `points`, `categories` → `true`; `time` → `false` | – |
| `radio-select.tsx` | `RadioInput` | generische Radiogruppe (Label, Optionen mit `disabled`; Kreis aktiv `border-accent-strong bg-accent-primary/80`) | – |
| `points/create-root.tsx` | `EstimatePointCreateRoot` | Überschrift = Systemtyp (`capitalize`); `Sortable` (`@plane/blocks`) mit `EstimatePointItemPreview` je Wert, darunter offene `EstimatePointCreate`-Zeilen; Button „Add {points\|categories}“ (ghost sm, `AddOutline`) solange Anzahl ≤ `estimateCount.max − 1` | – (lokaler Zustand; bei vorhandenem `estimateId` Server-Aufrufe in Kindern) |
| `points/preview.tsx` | `EstimatePointItemPreview` | Zeile `my-1 rounded-sm border px-1`: Drag-Griff `DragDropOutline`, Wert (Zeit formatiert, leer → Platzhalter „Enter estimate“), Edit-Icon (auch Doppelklick auf den Wert), Delete-Icon nur bei mehr als `estimateCount.min` (2) Werten | – |
| `points/create.tsx` | `EstimatePointCreate` | Inline-Formular: `EstimateInputRoot`, Fehler-Icon mit Tooltip und roter Rahmen, ✓ (nur bei Inhalt) und ✕ | bei vorhandenem `estimateId`: `creteEstimatePoint` → `POST …/estimates/{id}/estimate-points/` mit `{key: n+1, value}` |
| `points/update.tsx` | `EstimatePointUpdate` | Inline-Bearbeitung analog `create.tsx`; Tooltip „You have some unsaved changes, Please save them before clicking on done“ | bei vorhandenem `estimateId`: `updateEstimatePoint` → `PATCH …/estimates/{id}/estimate-points/{pointId}/` mit `{value}` |
| `points/index.ts` | Re-Exports | – | – |
| `inputs/root.tsx` | `EstimateInputRoot` | Weiche: `points` → `EstimateNumberInput`, `categories` → `EstimateTextInput`, `time` → nichts | – |
| `inputs/number-input.tsx` | `EstimateNumberInput` | Eingabe ohne `type="number"`, Platzhalter „Enter estimate“, `autoFocus` | – |
| `inputs/text-input.tsx` | `EstimateTextInput` | wie oben für Kategorien | – |
| `inputs/index.ts` | Re-Exports | – | – |
| `delete/modal.tsx` | `DeleteEstimateModal` | `Dialog size="md"` (`disablePointerDismissal`, Escape ignoriert): Titel „Delete Estimate System“, Text „Deleting the estimate **{name}** system will remove it from all work items permanently. This action cannot be undone. If you add estimates again, you will need to update all the work items.“; „Cancel“, „Delete Estimate“ / „Deleting“ (danger); Erfolg „Estimate deleted“ / „Estimate has been removed from your project.“; Fehler „Estimate creation failed“ / „We were unable to delete the estimate, please try again.“ | `deleteEstimate` → `DELETE …/estimates/{id}/`; danach, falls Estimates aktiv, `updateProject({estimate:null})` |
| `empty-screen.tsx` | `EstimateEmptyScreen` | `DetailedEmptyState` „No estimate systems yet“ / „Create a set of estimates to communicate the amount of work per work item.“ / „Add estimate system“ – **ungenutzt** | – |
| `estimate-search.tsx` | `EstimateSearch` | Platzhaltertext „Estimate Search“ – **ungenutzt** | – |
| `loader-screen.tsx` | `EstimateLoaderScreen` | Skeleton 4 × 40 px | – |

#### 2.9.3 Konstanten und Typen (`packages/constants/src/estimates.ts`)

| Konstante | Inhalt |
|---|---|
| `EEstimateSystem` | `points`, `categories`, `time` |
| `EEstimateUpdateStages` | `create`, `edit`, `switch` (`edit`/`switch` in CE ohne UI) |
| `estimateCount` | `{min: 2, max: 6}` |
| `MAX_ESTIMATE_POINT_INPUT_LENGTH` | `20` |
| `ESTIMATE_SYSTEMS.points` | `name` „Points“, Templates `fibonacci` „Fibonacci“ (1, 2, 3, 5, 8, 13), `linear` „Linear“ (1–6), `squares` „Squares“ (1, 4, 9, 16, 25, 36), `custom` „Custom“ (1, 2; `hide: true`); `is_available: true`, `is_ee: false` |
| `ESTIMATE_SYSTEMS.categories` | `name` „Categories“, Templates `t_shirt_sizes` „T-Shirt Sizes“ (XS, S, M, L, XL, XXL), `easy_to_hard` „Easy to hard“ (Easy, Medium, Hard, Very Hard), `custom` „Custom“ (Easy, Hard; `hide: true`); `is_available: true`, `is_ee: false` |
| `ESTIMATE_SYSTEMS.time` | `name` „Time“, Template `hours` „Hours“ (Werte 1–6, als Minuten interpretiert); `is_available: true`, `is_ee: true` |

Ungenutzte i18n-Texte für die Bezahlfunktion „Edit/Switch estimate system“: `project_settings.estimates.edit.title` „Edit estimate system“, `edit.add_or_update.title` „Add, update or remove estimates“ / „Manage current system either adding, updating or removing the points or categories.“, `edit.switch.title` „Change estimate type“ / „Convert your points system to categories system and vice versa.“, `switch` „Switch estimate system“, `current` „Current estimate system“, `select` „Select an estimate system“, Toasts `reorder.*` („Estimates re-ordered“, „Estimate re-order failed“) und `switch.*` („Estimate system created“ / „Created and Enabled successfully“), Validierungen `validation.fill` „Please fill this estimate field“, `validation.repeat` „Estimate value cannot be repeated“.

Endpunkte (`apps/web/services/estimate.service.ts`): `GET /api/workspaces/{ws}/estimates/`, `GET /api/workspaces/{ws}/projects/{pid}/estimates/`, `GET …/estimates/{id}/`, `POST …/estimates/`, `DELETE …/estimates/{id}/`, `POST …/estimates/{id}/estimate-points/`, `PATCH …/estimates/{id}/estimate-points/{pointId}/`.

### 2.10 Labels (`apps/web/components/labels/`, 10 Dateien, 1 197 Zeilen)

#### 2.10.1 Screen

| Screen | Route | Inhalt | Rechte | Quelle |
|---|---|---|---|---|
| Projekt-Einstellungen „Labels“ | `/:ws/settings/projects/:projectId/labels` | Page `LabelsSettingsPage` (Titel `<Projekt> - Labels`): scrollbarer Container mit `autoScrollForElements` (`@atlaskit/pragmatic-drag-and-drop-auto-scroll`) → `ProjectSettingsLabelList` | Seite: Projekt-Admin oder -Member (sonst `NotAuthorizedView isProjectView`); Anlegen, Ziehen und Aktionen an Einzel-Labels nur Projekt-Admin (`isEditable`) | `apps/web/app/(all)/[workspaceSlug]/(settings)/settings/projects/[projectId]/labels/page.tsx`, `project-setting-label-list.tsx` |

#### 2.10.2 Komponenten-Inventar

| Datei | Export | Zweck / Darstellung (Texte en) | Store / Endpunkt |
|---|---|---|---|
| `project-setting-label-list.tsx` | `ProjectSettingsLabelList` | `SettingsHeading` „Labels“ / „Create custom labels to categorize and organize your work items“ mit Button „Add label“ (primary md, nur Admin). Inline-Anlage in Rahmen `my-2 rounded-sm border border-subtle px-3.5 py-2`. Baum `projectLabelsTree`: Label mit Kindern → `ProjectSettingLabelGroup`, sonst `ProjectSettingLabelItem`. Leer (und Formular zu) → `EmptyStateCompact assetKey="label"` „No labels yet“ / „Create personalized labels to effectively categorize and manage your work items.“ / CTA „Create your first label“ (ohne Rechteprüfung). Ladezustand: `Loader` 4 × 42 px. `DeleteLabelModal` für das gewählte Label | `useLabel()`: `projectLabels`, `projectLabelsTree`, `createLabel`, `updateLabel`, `updateLabelPosition` |
| `project-setting-label-group.tsx` | `ProjectSettingLabelGroup` | Gruppe in `LabelDndHOC isGroup`. Rahmen: Drop-Ziel `border-[2px] border-accent-strong`, sonst `border-[0.5px] border-subtle`; beim Ziehen `bg-layer-1`. Kopf `LabelItemBlock isLabelGroup` mit Menü „Edit label“ / „Delete label“ (danger). Rechts `IconButton` mit `ChevronDownOutline` (zugeklappt `rotate-90`, `aria-expanded`). Kinder `ml-6` als `ProjectSettingLabelItem isChild`. Standard: aufgeklappt | – |
| `project-setting-label-item.tsx` | `ProjectSettingLabelItem` | Einzel-Label in `LabelDndHOC`; Menü „Remove from group“ (`CloseOutline`, nur bei `parent`) und „Edit label“ (`EditOutline`); Bearbeiten ersetzt die Zeile durch `CreateUpdateLabelInline isUpdating`; `disabled={!isEditable}` blendet Griff und Aktionen aus | „Remove from group“ → `updateLabel(…, {parent: null})` → `PATCH /api/workspaces/{ws}/projects/{pid}/issue-labels/{id}/` |
| `label-block/label-item-block.tsx` | `LabelItemBlock`, `ICustomMenuItem` | Zeile: `DragHandle` (Hover sichtbar, beim Ziehen fest), `LabelName`; rechts `absolute right-2.5` Aktionsbereich mit `Menu` (`IconButton` `MoreHorizontalOutline`, `aria-label` „More actions“; Einträge mit `key === "delete_label"` als `danger`) und, nur bei Nicht-Gruppen, X-Button (`CloseOutline size-3.5`, `aria-label` „Delete“) → Löschdialog. Aktionen sichtbar bei Hover, offenem Menü oder Gruppe | – |
| `label-block/label-name.tsx` | `LabelName` | Gruppe: `GroupOutline h-3.5 w-3.5` in Labelfarbe; sonst Kreis `h-3.5 w-3.5 rounded-full` (Farbe leer → `#000`); Name `h6 text-13`; Container `pr-20` | – |
| `create-update-label-inline.tsx` | `CreateUpdateLabelInline`, `TLabelOperationsCallbacks` | Zeile: Farbkreis `h-4 w-4` als `PopoverTrigger` (`aria-label` „Open color picker“) → `ColorSwatchPicker colors={LABEL_COLOR_OPTIONS}` (`w-80 max-w-xs`); `Input size="2xl"` Platzhalter „Label title“ (Pflicht „Label title is required“, max. 255 „Label name should not exceed 255 characters“, Fehlertext darunter `pl-8 text-13 text-danger-primary`); „Cancel“ (secondary sm), „Add“ / „Adding“ bzw. „Update“ / „Updating“ (primary sm). Neue Labels: Zufallsfarbe `getRandomLabelColor()`; Bearbeiten: vorhandene Farbe, leer → `#000` | `createLabel` → `POST …/issue-labels/`; `updateLabel` → `PATCH …/issue-labels/{id}/` |
| `delete-label-modal.tsx` | `DeleteLabelModal` | `ConfirmDialog` „Delete Label“ / „Are you sure you want to delete **{name}**? This will remove the label from all the work item and from any views where the label is being filtered upon.“; Fehler-Toast „Error!“ mit `err.error` oder „Label could not be deleted. Please try again.“; kein Erfolgs-Toast | `deleteLabel` → `DELETE …/issue-labels/{id}/` |
| `label-drag-n-drop-HOC.tsx` | `LabelDndHOC`, `LabelDragPreview` | Pragmatic-DnD (`draggable` mit `dragHandle`, `dropTargetForElements` mit `attachInstruction` aus `tree-item`, `currentLevel` 0/1, `indentPerLevel: 0`, Modus `last-in-group` beim letzten Element). `DropIndicator my-1` oberhalb (`reorder-above`) bzw. unterhalb des letzten Elements (`reorder-below`); `make-child` hebt das Ziel hervor. Eigene Drag-Vorschau `border-[1px] bg-surface-1 py-3 pr-4 pl-2`. Ziehen nur Projekt-Admin | – |
| `label-utils.ts` | `getInstructionFromPayload`, `getCanDrop`, `TargetData` | Drop-Regeln (siehe 3.8.1) | – |
| `index.ts` | Re-Exports | – | – |

`LABEL_COLOR_OPTIONS` (`packages/constants/src/label.ts`, identisch mit `DEFAULT_SWATCH_COLORS` in `packages/blocks/src/common/color-swatch-picker/default-swatches.ts`): `#FF6900`, `#FCB900`, `#7BDCB5`, `#00D084`, `#8ED1FC`, `#0693E3`, `#ABB8C3`, `#EB144C`, `#F78DA7`, `#9900EF`. Fehlercode `LABEL_NAME_ALREADY_EXISTS` im Feld `name` der Fehlerantwort → „Label already exists“; sonst beim Anlegen `detail` / `error` / „Something went wrong“, beim Bearbeiten `error` / „Error while updating the label“ (Toast-Titel „Error!“ bzw. „Oops!“).

Endpunkte (`apps/web/services/issue/issue_label.service.ts`): `GET /api/workspaces/{ws}/labels/` (Workspace), `GET|POST /api/workspaces/{ws}/projects/{pid}/issue-labels/`, `PATCH|DELETE …/issue-labels/{id}/`.

### 2.11 States (`apps/web/components/project-states/`, 16 Dateien, 1 183 Zeilen)

#### 2.11.1 Screen

| Screen | Route | Inhalt | Rechte | Quelle |
|---|---|---|---|---|
| Projekt-Einstellungen „States“ | `/:ws/settings/projects/:projectId/states` | Page `StatesSettingsPage` (Titel `<Projekt> - States`): `SettingsHeading` „States“ / „Define and customize workflow states to track the progress of your work items.“ → `ProjectStateRoot` | Seite: Projekt-Admin oder -Member; Bearbeiten nur Projekt-Admin (`allowPermissions([EUserProjectRoles.ADMIN], PROJECT, ws, pid)`) | `apps/web/app/(all)/[workspaceSlug]/(settings)/settings/projects/[projectId]/states/page.tsx`, `root.tsx` |

#### 2.11.2 Komponenten-Inventar

| Datei | Export | Zweck / Darstellung (Texte en) | Store / Endpunkt |
|---|---|---|---|
| `root.tsx` | `ProjectStateRoot` | SWR `PROJECT_STATES_<ws>_<pid>` (`revalidateIfStale: false`, `revalidateOnFocus: false`); `ProjectStateLoader` bis `groupedProjectStates` vorliegt; baut `TStateOperationsCallbacks` (`createState`, `updateState`, `deleteState`, `moveStatePosition`, `markStateAsDefault`) | `fetchProjectStates` → `GET /api/workspaces/{ws}/projects/{pid}/states/` |
| `group-list.tsx` | `GroupList` | `space-y-5`; Gruppen in der Reihenfolge von `groupedProjectStates` (immer alle fünf Gruppen aus `STATE_GROUPS`: backlog, unstarted, started, completed, cancelled); alle initial aufgeklappt | – |
| `group-item.tsx` | `GroupItem` | Karte `rounded-sm border border-subtle bg-surface-2`; `Collapsible` mit Trigger `StateGroupIcon` (XL) + Gruppenschlüssel (`text-14 font-medium capitalize`), Chevron `rotate-0`/`-rotate-90`; Trailing-`IconButton` „Add“ (`AddOutline`, aktiv `text-accent-primary/80`, deaktiviert ohne Admin oder bei offenem Formular). Leere Gruppe: „No states available for the {groupKey} group“ + (Admin) „Please create a new state“. `StateCreate` außerhalb des Panels, damit Eingaben beim Zuklappen erhalten bleiben | – |
| `state-list.tsx` | `StateList` | `StateItem` je State (React-Key = `state.name`) | – |
| `state-item.tsx` | `StateItem` | Karte `group relative rounded-sm border bg-surface-1 px-3.5 py-3`, `cursor-grab` (bei nur einem State `cursor-auto`), beim Ziehen `opacity-50`; `DropIndicator` oben/unten nach nächstgelegener Kante; Bearbeiten ersetzt die Karte durch `StateUpdate` | `moveStatePosition(id, {id, group, sequence})` → `PATCH …/states/{id}/` |
| `state-item-title.tsx` | `StateItemTitle` | Drag-Indikator `DragDropOutline` (Hover, `absolute -left-1.5`, nur editierbar und mehr als ein State), `StateGroupIcon` mit Statusfarbe und Füllgrad `getStatePercentageInGroup/100`, Name `h6 text-13 font-medium`, Beschreibung `text-11 text-secondary`; Hover-Aktionen: `StateMarksAsDefault`, Edit-`IconButton` (`aria-label` „Edit“), `StateDelete` | – |
| `options/mark-as-default.tsx` | `StateMarksAsDefault` | Text-Button `text-11`: „Mark as default“, bei Default „Default“ (disabled, `text-tertiary`); Ladetext „Marking as default“ | `markStateAsDefault` → `POST …/states/{id}/mark-default/` |
| `options/delete.tsx` | `StateDelete` | `IconButton` (`aria-label` „Delete“, `aria-disabled` statt `disabled`, damit der Tooltip erscheint): `CloseOutline`, rot wenn löschbar; Tooltip „Cannot delete the default state.“ bzw. „Cannot have an empty group.“; `ConfirmDialog` „Delete State“ / „Are you sure you want to delete state- **{name}**? All of the data related to the state will be permanently removed. This action cannot be undone.“; Fehler 400 → „This state contains some work items within it, please move them to some other state to delete this state.“, sonst „State could not be deleted. Please try again.“ | `deleteState` → `DELETE …/states/{id}/` |
| `state-delete-modal.tsx` | `StateDeleteModal` | eigenständiger Löschdialog mit gleicher Funktion – **ungenutzt** | – |
| `create-update/form.tsx` | `StateForm` | `relative flex space-x-2 rounded-sm bg-surface-1 p-3`: Farbquadrat `h-5 w-5 rounded-sm` (Fallback `black`) als `PopoverTrigger` → `ColorSwatchPicker` mit Standardpalette (`DEFAULT_SWATCH_COLORS`); `Input size="2xl"` Platzhalter „Name“, `maxLength={100}`, `autoFocus`; `TextArea` „Describe this state for your members.“ (autoResize, max. 8 Zeilen); Buttons Primär (`buttonTitle`) und „Cancel“. Validierung: leerer Name → Feld rot markiert (Meldung „Name is required“ wird gesetzt, aber nicht angezeigt) | – |
| `create-update/create.tsx` | `StateCreate` | `StateForm` mit `{name:"", description:"", color: STATE_GROUPS[group].color}`, Button „Create“; Erfolg „Success!“ / „State created successfully.“; 400 → „State with that name already exists. Please try again with another name.“; sonst `data.error` oder „State could not be created. Please try again.“ | `createState` → `POST …/states/` (`{name, description, color, group}`) |
| `create-update/update.tsx` | `StateUpdate` | `StateForm` mit State-Werten, Button „Update“; Erfolg „Success!“ / „State updated successfully.“; 400 → „Another state exists with the same name. Please try again with another name.“; sonst „State could not be updated. Please try again.“ | `updateState` → `PATCH …/states/{id}/` |
| `loader.tsx` | `ProjectStateLoader` | Skeleton `space-y-5 md:w-2/3`, 4 × 40 px | – |
| `create-update/index.ts`, `options/index.ts`, `index.ts` | Re-Exports | – | – |

`STATE_GROUPS` (`packages/constants/src/state.ts`): `backlog` „Backlog“ `#d9d9d9` (Default-Name „Backlog“), `unstarted` „Unstarted“ `#3f76ff` („Todo“), `started` „Started“ `#f59e0b` („In Progress“), `completed` „Completed“ `#16a34a` („Done“), `cancelled` „Canceled“ `#dc2626` („Cancelled“). Die Gruppenüberschrift zeigt den Schlüssel (`cancelled` → „Cancelled“), nicht das Label.

Endpunkte (`apps/web/services/project/project-state.service.ts`): `GET|POST /api/workspaces/{ws}/projects/{pid}/states/`, `GET|PATCH|DELETE …/states/{id}/`, `POST …/states/{id}/mark-default/`, `GET …/intake-state/`, `GET /api/workspaces/{ws}/states/`.

### 2.12 Webhooks (`apps/web/components/web-hooks/`, 16 Dateien, 916 Zeilen)

#### 2.12.1 Screens und Dialoge

| Screen / Dialog | Route bzw. Auslöser | Inhalt | Rechte | Quelle |
|---|---|---|---|---|
| Webhook-Liste | `/:ws/settings/webhooks` | Page `WebhooksListPage` (Titel `<Workspace> - Webhooks`, Kopf `WebhooksWorkspaceSettingsHeader`): `SettingsHeading` „Webhooks“ / „Automate notifications to external services when project events occur.“ mit Button „Add webhook“ (primary md); vorhandene Webhooks → `WebhooksList` (`mt-4`), sonst `EmptyStateCompact assetKey="webhook"` „No Webhook added yet“ / „Automate notifications to external services when project events occur.“ / CTA „Add webhook“; `WebhookSettingsLoader` solange `webhooks` fehlt | Workspace-Admin; sonst `NotAuthorizedView section="settings"`; SWR `WEBHOOKS_LIST_<ws>` nur für Admins | `apps/web/app/(all)/[workspaceSlug]/(settings)/settings/(workspace)/webhooks/page.tsx` |
| Webhook-Detail | `/:ws/settings/webhooks/:webhookId` (Link aus der Liste) | Page `WebhookDetailsPage` (Titel `<Workspace> - Webhook`, Kopf `WebhookDetailsWorkspaceSettingsHeader`): `WebhookForm data=currentWebhook` + `WebhookDeleteSection`; `LogoSpinner` bis geladen | Workspace-Admin; sonst nur Text „You are not authorized to access this page.“; SWR `WEBHOOK_DETAILS_<ws>_<webhookId>` | `…/webhooks/[webhookId]/page.tsx` |
| Webhook anlegen | „Add webhook“ / Empty-State-CTA | `CreateWebhookModal` → `WebhookForm` → nach Erfolg `GeneratedHookDetails` | – | `create-webhook-modal.tsx` |
| Webhook löschen | „Delete webhook“ in der Danger zone | `DeleteWebhookModal` | – | `delete-webhook-modal.tsx` |

#### 2.12.2 Komponenten-Inventar

| Datei | Export | Zweck / Darstellung (Texte en) | Store / Endpunkt |
|---|---|---|---|
| `create-webhook-modal.tsx` | `CreateWebhookModal` | `Dialog` (`disablePointerDismissal`; Escape schließt nur, solange kein Webhook erzeugt wurde), `DialogContent size="md"` (`aria-label` „Create webhook“ bzw. „Key created“), Inhalt `min-h-0 flex-1 overflow-y-auto p-4 pb-0`. Payload: `url` plus Ereignis-Booleans (bei „all“ alle `true`, bei „individual“ die Checkbox-Werte). Erfolg: Toast „Webhook created“ / „The webhook has been successfully created“, Wechsel zu `GeneratedHookDetails`, sofortiger CSV-Download `webhook-secret-key-<Date.now()>`; Fehler „Webhook not created“ / `error.error` oder „The webhook could not be created“. `handleClose` leert Secret und Zustand nach 350 ms | `createWebhook` → `POST /api/workspaces/{ws}/webhooks/` |
| `delete-webhook-modal.tsx` | `DeleteWebhookModal` | `ConfirmDialog` „Delete webhook“ / „Are you sure you want to delete this webhook? Future events will not be delivered to this webhook. This action cannot be undone.“; danach `router.replace("/<ws>/settings/webhooks/")`, Toast „Success!“ / „Webhook deleted successfully.“; Fehler „Error!“ / „Webhook could not be deleted. Please try again.“ | `removeWebhook` → `DELETE /api/workspaces/{ws}/webhooks/{id}/` |
| `empty-state.tsx` | `WebhooksEmptyState` | Bild, „No webhooks“, „Create webhooks to receive real-time updates and automate actions“, Button „Add webhook“ – **ungenutzt** | – |
| `generated-hook-details.tsx` | `GeneratedHookDetails` | `space-y-5 p-5`: „Key created“ (`text-18 font-medium`), „Copy and save this secret key in Plane Pages. You can't see this key after you hit Close. A CSV file containing the key has been downloaded.“, `WebhookSecretKey`; Footer „Close“ (secondary md) | – |
| `utils.ts` | `getCurrentHookAsCSV` | CSV-Datensatz mit `id`, `url`, `created_at`, `updated_at` (`renderFormattedPayloadDate`), `is_active`, `secret_key`, `project`, `issue`, `module`, `cycle`, `issue_comment` (Booleans als Text), `workspace` (Workspace-Name) | – |
| `webhooks-list.tsx` | `WebhooksList` | `flex size-full flex-col gap-y-2 overflow-y-auto rounded-lg border border-subtle bg-layer-1 p-3`; Einträge in Objekt-Reihenfolge, ohne Sortierung | `useWebhook().webhooks` |
| `webhooks-list-item.tsx` | `WebhooksListItem` | Link auf `/<ws>/settings/webhooks/<id>` mit URL (truncate) und `Switch size="sm"` (`aria-label` „Toggle webhook“); Klick auf den Switch unterbindet die Navigation (`preventDefault`/`stopPropagation`); kein Toast, kein Fehler-Handling | `updateWebhook(ws,id,{is_active: !is_active})` → `PATCH …/webhooks/{id}/` |
| `form/form.tsx` | `WebhookForm` | Titel „Create webhook“ bzw. „Webhook details“ (`text-18 font-medium`); `WebhookInput` (Pflicht „URL is required“, `text-11 text-danger-primary`); im Bearbeitungsmodus `WebhookToggle`; `WebhookOptions`; bei „individual“ `WebhookIndividualEventOptions`. Bearbeiten: `WebhookSecretKey` + „Update“ / „Updating“ (primary md). Anlegen: Footer „Cancel“ + „Create“ / „Creating“ (der Create-Button verschwindet, sobald `webhookSecretKey` im Store steht). Defaults: alle fünf Ereignisse `true`, `url ""`; Ereignistyp beim Bearbeiten: alle fünf `true` → „all“, sonst „individual“ | `useWebhook().webhookSecretKey` |
| `form/input.tsx` | `WebhookInput` | Überschrift „Payload URL“; `Input size="2xl" type="url"`, Platzhalter `https://example.com/post`, `autoComplete="off"`, `autoFocus` | – |
| `form/toggle.tsx` | `WebhookToggle` | „Enable webhook“ + `Switch size="sm"` an `is_active` | – |
| `form/event-types.tsx` | `WebhookOptions` | Frage „Which events would you like to trigger this webhook?“; native Radio-Buttons „Send me everything“ (`all`) und „Select individual events“ (`individual`) | – |
| `form/individual-event-options.tsx` | `INDIVIDUAL_WEBHOOK_OPTIONS`, `WebhookIndividualEventOptions` | Grid `lg:grid-cols-2` mit `CheckboxField size="lg"`: `project` „Projects“ / „Project created, updated, or deleted“; `cycle` „Cycles“ / „Cycle created, updated, or deleted“; `issue` „Work items“ / „Work item created, updated, deleted, added to a cycle or module“; `module` „Modules“ / „Module created, updated, or deleted“; `issue_comment` „Work item comments“ / „Comment posted, updated, or deleted“ | – |
| `form/secret-key.tsx` | `WebhookSecretKey` | Überschrift „Secret key“ (nur mit `webhookId` in der URL), Hinweis „Generate a token to sign-in to the webhook payload“; Feld `h-8 max-w-lg rounded-sm border` mit 30 Punkten (maskiert) bzw. Klartext; Icons „View secret key“ (`ShowOutline`/`HideOutline`) und „Copy secret key“ (`CopyOutline`) nur, wenn ein Secret im Store liegt; Button „Re-generate key“ / „Re-generating...“ (secondary md, `RefreshOutline`), sobald `data` vorhanden ist (also auch im Erfolgsschritt des Anlegedialogs). Toasts: „Success“ / „Secret key copied to clipboard.“, „Error!“ / „Error occurred while copying secret key.“, „Success“ / „New key regenerated successfully.“, Fehler `err.error` oder „Something went wrong. Please try again.“ | `regenerateSecretKey` → `POST /api/workspaces/{ws}/webhooks/{id}/regenerate/` |
| `form/delete-section.tsx` | `WebhookDeleteSection` | `w-full border-t`; `Collapsible` „Danger zone“ (`text-16`, initial zu) mit „Once a webhook is deleted, it cannot be restored. Future events will no longer be delivered to this webhook.“ und Button „Delete webhook“ (danger md) | – |
| `form/index.ts`, `index.ts` | Re-Exports | – | – |

Detailseite `handleUpdateWebhook`: Payload `{url, is_active, project, cycle, module, issue, issue_comment}`; Toasts „Success!“ / „Webhook updated successfully.“ bzw. „Error!“ / `error.error` oder „Something went wrong. Please try again.“.

Store `apps/web/store/workspace/webhook.store.ts`: `webhooks: Record<id, IWebhook> | null`, `webhookSecretKey` (nur im Speicher), `currentWebhook` (über `router.webhookId`); Aktionen `fetchWebhooks`, `fetchWebhookById`, `createWebhook` und `regenerateSecretKey` (trennen `secret_key` aus der Antwort ab und legen ihn in `webhookSecretKey`), `updateWebhook`, `removeWebhook`, `clearSecretKey`. Endpunkte (`apps/web/services/webhook.service.ts`): `GET|POST /api/workspaces/{ws}/webhooks/`, `GET|PATCH|DELETE /api/workspaces/{ws}/webhooks/{id}/`, `POST …/webhooks/{id}/regenerate/`. Auslieferung, Signatur und Retry der Webhooks: Analyse 07.

### 2.13 API-Token / Personal Access Tokens (`apps/web/components/api-token/`, 6 Dateien, 647 Zeilen)

#### 2.13.1 Screen und Dialoge

| Screen / Dialog | Route bzw. Auslöser | Inhalt | Quelle |
|---|---|---|---|
| Profil-Einstellungen „Personal Access Tokens“ | `/settings/profile/api-tokens` (Profil-Tab `api-tokens`); Altroute `/:ws/settings/api-tokens` leitet um (`apps/web/app/routes/redirects/core/api-tokens.tsx`) | `APITokensProfileSettings`: `ProfileSettingsHeading` „Personal Access Tokens“ / „Generate secure API tokens to integrate your data with external systems and applications.“ mit Button „Add access token“ (primary md); Liste `ApiTokenListItem` (`mt-7`) oder `EmptyStateCompact assetKey="token"` „No Personal token yet“ / „Generate secure API tokens to connect your workspace with external systems and applications.“ / CTA „Add access token“; `APITokenSettingsLoader` bis geladen. Keine Rechteprüfung: jeder angemeldete Nutzer verwaltet seine eigenen Tokens | `apps/web/components/settings/profile/content/pages/api-tokens.tsx` |
| Token anlegen | „Add access token“ / CTA | `CreateApiTokenModal` → `CreateApiTokenForm` → `GeneratedTokenDetails` | `modal/*` |
| Token löschen | Hover-Icon am Listeneintrag | `DeleteApiTokenModal` | `delete-token-modal.tsx` |

#### 2.13.2 Komponenten-Inventar

| Datei | Export | Zweck / Darstellung (Texte en) | Endpunkt |
|---|---|---|---|
| `token-list-item.tsx` | `ApiTokenListItem` | `group relative flex flex-col border-b py-3`: Label `h5 text-13 font-medium truncate`, Badge „Active“ (`bg-success-subtle text-success-primary`) bzw. „Expired“ (`bg-layer-1 text-placeholder`), Beschreibung (`max-w-[70%]`, nur wenn nicht leer), Zeile `text-11`: „Expires {Datum} at {Zeit}“ / „Never expires“ / „Expired {vor X}“ (`calculateTimeAgo`); Lösch-Icon `CloseCircleOutline` (rot, Tooltip „Delete token“) nur bei Hover (`hidden group-hover:grid`) | – |
| `delete-token-modal.tsx` | `DeleteApiTokenModal` | `ConfirmDialog` „Delete access token“ / „Any application using this token will no longer have the access to Plane data. This action cannot be undone.“; Erfolg „Success!“ / „The token has been successfully deleted“ (SWR-Cache `API_TOKENS_LIST` lokal gefiltert); Fehler „Error!“ / `err.message` oder „The token could not be deleted“ | `DELETE /api/users/api-tokens/{id}` |
| `empty-state.tsx` | `ApiTokenEmptyState` | Bild, „No API tokens“, „Create API tokens for safe and easy data sharing with external apps, maintaining control and security.“, Button „Add token“ – **ungenutzt** | – |
| `modal/create-token-modal.tsx` | `CreateApiTokenModal` | `Dialog` (`disablePointerDismissal`, `onOpenChange` ohne Wirkung: Schließen nur über eigene Buttons), `DialogContent size="md"`; nach Erfolg `GeneratedTokenDetails`; CSV-Download `secret-key-<Date.now()>` mit `Title`, `Description`, `Expiry` (formatiertes Datum, Komma durch Leerzeichen ersetzt, oder „Never expires“), `Secret key`; SWR-Cache: neues Token vorn; Fehler-Toast „Error!“ / `err.message \|\| err.detail`. Reset von „Never expires“ und Ergebnis nach 350 ms | `POST /api/users/api-tokens/` |
| `modal/form.tsx` | `CreateApiTokenForm` | Titel „Create token“; `InputField size="2xl"` Platzhalter „Title“ (Pflicht „Title is required“, max. 255 „Title should be less than 255 characters“, nur Leerzeichen unzulässig); `TextAreaField` „Description“ (autoResize, max. 8 Zeilen); Ablauf-`Select` (Trigger `select-md` mit `CalendarOutline`: „Set expiration date“ / Optionslabel / „Custom date“) mit „1 week“, „1 month“, „3 months“, „1 year“, „Custom“; bei „Custom“ `DateSelect` (`minDate` morgen, `weekStartsOn` aus dem Profil, Platzhalter „Set date“, löschbar, `pill-md`); Vorschau `text-caption-sm-regular` „Expires {Datum} at {Zeit}“; alle Ablauf-Felder bei „Never expires“ deaktiviert. Footer: `DialogInfo` mit `Switch` „Never expires“, „Cancel“, „Generate token“ / „Generating“ | – |
| `modal/generated-token-details.tsx` | `GeneratedTokenDetails` | Titel „Key created“, Beschreibung „Copy and save this secret key in Plane Pages. You can't see this key after you hit Close. A CSV file containing the key has been downloaded.“; Button mit Token im Klartext und `CopyOutline` (Tooltip „Copy secret key“) → Toast „Success!“ / „Token copied to clipboard.“; Footer-Info „Expires … at …“ / „Never expires“, Button „Close“ | – |

Endpunkte (`packages/services/src/developer/api-token.service.ts`): `GET /api/users/api-tokens/`, `POST /api/users/api-tokens/`, `GET /api/users/api-tokens/{id}` und `DELETE /api/users/api-tokens/{id}` (beide ohne abschließenden Schrägstrich). `IApiToken` (`packages/types/src/api_token.ts`): `id`, `label`, `description`, `expired_at`, `is_active`, `last_used`, `token` (nur in der Create-Antwort), `user`, `user_type`, `workspace`, Audit-Felder; `last_used` wird nicht angezeigt. Der MobX-Store `apps/web/store/workspace/api-token.store.ts` (`workspaceRoot.apiToken` mit `fetchApiTokens`, `fetchApiTokenDetails`, `createApiToken`, `deleteApiToken`) existiert, wird aber von keiner Komponente genutzt; die Seite arbeitet direkt mit SWR und `APITokenService`. Token-Validierung im Backend: Analyse 06.

### 2.14 Exporter (`apps/web/components/exporter/`, 6 Dateien, 815 Zeilen)

#### 2.14.1 Screen

| Screen | Route | Inhalt | Rechte | Quelle |
|---|---|---|---|---|
| Workspace-Einstellungen „Exports“ | `/:ws/settings/exports` | Page `ExportsPage` (Titel `<Workspace> - Exports`, `SettingsContentWrapper hugging`, Kopf `ExportsWorkspaceSettingsHeader`): `SettingsHeading` „Exports“ / „Export your project data in various formats and access your export history with download links.“ → `ExportGuide` | Workspace-Admin oder -Member, sonst `NotAuthorizedView` | `apps/web/app/(all)/[workspaceSlug]/(settings)/settings/(workspace)/exports/page.tsx` |

#### 2.14.2 Komponenten-Inventar

| Datei | Export | Zweck / Darstellung (Texte en) | Endpunkt |
|---|---|---|---|
| `guide.tsx` | `ExportGuide` | `flex size-full flex-col gap-y-13` mit `ExportForm` und `PrevExports`; Paginierung `per_page = 10`, Start-Cursor `10:0:0`; liest Query `provider` (an das Formular weitergereicht, dort ungenutzt) | – |
| `export-form.tsx` | `ExportForm` | Box `rounded-lg border border-subtle bg-layer-2`: Zeile „Exporting project“ (`ProjectSelect multiple`, `projectList="all"`, Platzhalter „All projects“, angeboten nur Projekte mit Create-Recht, `w-72`), Zeile „Format“ (`Select` „CSV“, „Excel“, „JSON“), Button „Export“ / „Exporting...“ (primary md). Felder deaktiviert, wenn der Nutzer kein Workspace-Admin/-Member ist und keine Projekte oder keine Create-Aktion hat. Toasts: „Export successful“ / „You will be able to download the exported {CSV\|Excel\|JSON} from the previous export.“; Fehler „Error“ / „Export was unsuccessful. Please try again.“. Ein Rich-Filter-Block (`WorkspaceLevelWorkItemFiltersHOC`, Tooltip „Apply filters to export specific work items based on your criteria.“) ist auskommentiert | `ProjectExportService.csvExport` → `POST /api/workspaces/{ws}/export-issues/` mit `{provider, project, multiple: project.length > 1, rich_filters}` |
| `prev-exports.tsx` | `PrevExports` | Kopf `border-b pb-3.5`: „Previous exports“ (`text-h6-medium`) + Button „Refresh status“ / „Refreshing“ (tertiary sm, `RefreshOutline` dreht sich); rechts „Prev“ / „Next“ (secondary xs, nur bei Ergebnissen, deaktiviert ohne Vor-/Folgeseite). Inhalt: `ImportExportSettingsLoader`, `DataTable` (`@makeplane/propel`) mit `useExportColumns`, oder `EmptyStateCompact assetKey="export"` „No exports yet“ / „You don't have any export records right now. Once you export data, all records will appear here.“ | `IntegrationService.getExportsServicesList` → `GET /api/workspaces/{ws}/export-issues?per_page=10&cursor=…` |
| `column.tsx` | `useExportColumns` | Spalten „Exported By“ (Avatar 16 px oder Initiale `bg-gray-700`, Name), „Exported On“ (`renderFormattedDate(created_at)`), „Exported projects“ („{n} project(s)“), „Format“ (CSV/Excel/JSON), „Status“ (Badge `capitalize`: `completed` grün, `processing` `bg-yellow-500/20 text-yellow-500`, `failed` rot, `expired` `bg-orange-500/20 text-orange-500`, sonst grau), „Download“ (Link „Download“ mit `DownloadOutline` in neuem Tab, nur `completed`; sonst „-“; älter als 7 Tage „Expired“ rot) | – |
| `export-modal.tsx` | `Exporter` | `Dialog size="sm"` „Export to {Format}“ mit `ProjectSelect`, `Checkbox` „Export the data into separate files“, „Cancel“ und „Exports“; danach `router.push("/<ws>/settings/exports")` – **ungenutzt** | `POST …/export-issues/` |
| `single-export.tsx` | `SingleExport` | Zeile „Export to {Format}“ + Status-Badge, Datum, „Exported by …“, Button „Download“ – **ungenutzt** | – |

`EXPORTERS_LIST` (`packages/constants/src/workspace.ts`): `csv` („CSV“), `xlsx` („Excel“), `json` („JSON“), jeweils `type: "export"`. Backend (`apps/api/plane/app/views/exporter/base.py`): Provider außerhalb von `csv`, `xlsx`, `json` → 400 „Provider '…' not found.“; leere Projektliste → alle aktiven Projekte, in denen der Nutzer Mitglied ist; `rich_filters` wird nicht ausgewertet; die Erzeugung läuft asynchron (`issue_export_task`, Analyse 07); `GET` verlangt `per_page` und `cursor` (sonst 400).

### 2.15 Automation (`apps/web/components/automation/`, 4 Dateien, 507 Zeilen)

#### 2.15.1 Screen

| Screen | Route | Inhalt | Rechte | Quelle |
|---|---|---|---|---|
| Projekt-Einstellungen „Automations“ | `/:ws/settings/projects/:projectId/automations` | Page `AutomationSettingsPage` (Titel `<Projekt> - Automations`, `hugging`): `SettingsHeading` „Automations“ / „Configure automated actions to streamline your project management workflow and reduce manual tasks.“, darunter `AutoArchiveAutomation` und `AutoCloseAutomation`; jede Änderung → `updateProject` (Fehler-Toast „Error!“ / „Something went wrong. Please try again.“) | Projekt-Admin, sonst `NotAuthorizedView isProjectView` | `apps/web/app/(all)/[workspaceSlug]/(settings)/settings/projects/[projectId]/automations/page.tsx` |

#### 2.15.2 Komponenten-Inventar

| Datei | Export | Zweck / Darstellung (Texte en) | Projektfelder |
|---|---|---|---|
| `auto-archive-automation.tsx` | `AutoArchiveAutomation` | Zeile `border-b py-2`: Icon-Kachel `size-10 rounded-sm bg-layer-2` mit `RestoreOutline`, `SettingsControlItem` „Auto-archive closed work items“ / „Plane will auto archive work items that have been completed or canceled.“ + `Switch size="sm"`. Aktiv: Box `ml-13 rounded-sm border bg-surface-2 px-5 py-4` „Auto-archive work items that are closed for“ + `Select` (Optionen „1 month“, „3 months“, „6 months“, „9 months“, „12 months“ plus ein abweichender aktueller Wert, aufsteigend sortiert) mit Footer-Button „Customize time range“; Loader 50 px, solange das Projekt fehlt | `archive_in` (0 = aus; Einschalten → 1) |
| `auto-close-automation.tsx` | `AutoCloseAutomation` | Icon `AutoCloseOutline` (`text-danger-primary`), „Auto-close work items“ / „Plane will automatically close work items that haven't been completed or canceled.“ + Switch. Aktiv: „Auto-close work items that are inactive for“ + Monats-`Select` wie oben; „Auto-close status“ + `Select` über die States der Gruppe `cancelled` (Icon `StateGroupIcon`, deaktiviert bei nur einem solchen State, Platzhalter „State“) | `close_in` (0 = aus), `default_state` (Ziel-State; Einschalten → erster `cancelled`-State) |
| `select-month-modal.tsx` | `SelectMonthModal` | `Dialog size="md"` „Customize time range“: `InputField type="number"` (2xl, Platzhalter „Enter Months“, Suffix „Months“, 1–12; Fehler „Select a month between 1 and 12.“), „Cancel“, „Submit“ / „Submitting...“ | `archive_in` bzw. `close_in` (Initialwert 1; bei Auto-Close zusätzlich `default_state`) |
| `index.ts` | Re-Exports | – | – |

`PROJECT_AUTOMATION_MONTHS` (`packages/constants/src/project.ts`): 1, 3, 6, 9, 12 (Label `workspace_projects.common.months_count` = „{months, plural, one{# month} other{# months}}“). Ungenutzte Texte der Bezahlfunktion „Auto-reminders“: `project_settings.automations.auto-remind.title` „Auto-reminders“, `.description` „Plane will automatically send reminders via email and in-app notifications to keep your team on track with deadlines.“, `.duration` „Send reminder before“. Die Hintergrundjobs für Archivieren und Schließen beschreibt Analyse 07.

### 2.16 Integrationen (`apps/web/components/integration/`, 3 Dateien, 387 Zeilen)

| Datei | Export | Zweck / Darstellung (Texte en) | Endpunkt | Erreichbarkeit |
|---|---|---|---|---|
| `single-integration-card.tsx` | `SingleIntegrationCard` | Zeile `border-b bg-surface-1 px-4 py-6`: Logo 40 px (GitHub/Slack), Titel + `TickCircleOutline` bei installiert; Text installiert „Activate GitHub on individual projects to sync with specific repositories.“ / „Activate Slack on individual projects to sync with specific channels.“, nicht installiert „Connect with GitHub with your Plane workspace to sync project work items.“ / „Connect with Slack with your Plane workspace to sync project work items.“, sonst „Loading...“; Buttons „Install“ / „Installing...“ (öffnet OAuth-Popup über `useIntegrationPopup`) bzw. „Uninstall“ / „Uninstalling...“ (danger); ohne Workspace-Admin Tooltip „You don't have permission to perform this“; Toasts „Deleted successfully!“ / „{title} integration deleted successfully.“ bzw. „Error!“ / „{title} integration could not be deleted. Please try again.“ | `GET /api/workspaces/{ws}/workspace-integrations/`, `DELETE …/workspace-integrations/{id}/provider/` | nur von der Seite `apps/web/app/(all)/[workspaceSlug]/(settings)/settings/(workspace)/integrations/page.tsx` (Überschrift „Integrations“, `GET /api/integrations/`) genutzt, die in `apps/web/app/routes/core.ts` **nicht registriert** ist |
| `github/select-repository.tsx` | `SelectRepository` | `Select` über GitHub-Repositories (Suche über `full_name`, Label auf 25 Zeichen gekürzt), unendliches Nachladen per Footer „Click to load more...“ / „Loading...“ | `GET {VITE_API_BASE_URL}/api/workspaces/{ws}/workspace-integrations/{id}/github-repositories/?page=n` | nur aus `apps/web/components/project/integration-card.tsx`, das selbst nirgends eingebunden ist |
| `slack/select-channel.tsx` | `SelectChannel` | handgebauter Schalter `h-4 w-6 rounded-full bg-gray-700`; an → Slack-Kanal-Sync entfernen, aus → OAuth-Popup `slackChannel` | `GET\|POST\|DELETE /api/workspaces/{ws}/projects/{pid}/workspace-integrations/{id}/project-slack-sync/…` (`apps/web/services/app_installation.service.ts`) | wie oben, nur aus `components/project/integration-card.tsx` |

`useIntegrationPopup` (`apps/web/hooks/use-integration-popup.tsx`) öffnet ein Fenster 600 × 600 px auf `https://github.com/apps/{github_app_name}/installations/new?state=<ws>`, `https://slack.com/oauth/v2/authorize?scope=chat:write,…&client_id=…&state=<ws>` oder (Kanal) `…?scope=incoming-webhook&client_id=…&state=<ws>,<pid>[,<id>]` und prüft jede Sekunde, ob es geschlossen wurde. Das CE-Backend enthält die Modelle `Integration`, `WorkspaceIntegration`, `GithubRepository`, `GithubRepositorySync`, `GithubIssueSync`, `GithubCommentSync` und `SlackProjectSync` (`apps/api/plane/db/models/integration/`), registriert aber keine URLs dafür. Die Integrationsoberfläche ist in CE also unerreichbar und funktionslos; die Ziel-Integrationen spezifiziert `migration/features/28-paid-integrationen-importer-ai.md` §3.A.

### 2.17 Editor-Wrapper (`apps/web/components/editor/`, 19 Dateien, 1 724 Zeilen)

Die Wrapper verbinden die Editoren aus `@plane/editor` (Analyse 12 §2.1–§2.20) mit Web-Stores und Diensten. Gemeinsam ist allen: Mention-Suche über `useEditorMention` (Analyse 12 §3.20) → `WorkspaceService.searchEntity` (`GET /api/workspaces/{ws}/entity-search/`), Datei-Handler über `useEditorConfig().getEditorFileHandlers`, Extension-Flags über `useEditorFlagging` (`apps/web/hooks/use-editor-flagging.ts`; CE-Stub: für `document`, `liteText` und `richText` jeweils `disabled: ["ai", "collaboration-cursor"]`, `flagged: []`; Analyse 12 §5.8) und Inhalts-Metadaten über `useParseEditorContent`. Eigene Screens gibt es hier nicht.

| Datei | Export | Zweck / Verhalten | Konsumenten |
|---|---|---|---|
| `document/editor.tsx` | `DocumentEditor` (`forwardRef`) | Wrapper um `DocumentEditorWithRef`; `editable: false` braucht keine Upload-/Such-Callbacks (Platzhalter-Funktionen); `enableAdvancedMentions: true`; `containerClassName` ergänzt `relative pb-3 pl-3`; `getMentionedEntityDetails` liefert `display_name` aus `useMember` | `apps/web/components/pages/version/editor.tsx` (Versionsanzeige, read-only) |
| `rich-text/editor.tsx` | `RichTextEditor` (`forwardRef`) | Wrapper um `RichTextEditorWithRef`; `searchMentionCallback`, `uploadFile`, `duplicateFile` Pflicht bei `editable: true`; `extendedEditorProps={}`; `containerClassName` + `relative pb-3 pl-3` | `apps/web/components/issues/issue-modal/components/description-editor.tsx`, `inbox/modals/create-modal/issue-description.tsx`, `core/modals/gpt-assistant-popover.tsx`, `core/description-versions/modal.tsx`, `profile/activity/activity-list.tsx`, `pages/editor/ai/menu.tsx`, `pages/editor/ai/ask-pi-menu.tsx`, `rich-text/description-input/root.tsx` |
| `rich-text/index.ts` | Re-Export | – | – |
| `rich-text/description-input/root.tsx` | `DescriptionInput` | Beschreibungsfeld mit Autosave: `react-hook-form` (`description_html`, `description_json`, `isMigrationUpdate`); `onChange` ignoriert unveränderten Inhalt (`lastSavedContent`), setzt `setIsSubmitting("submitting")` und speichert nach 1 500 ms Debounce über `onSubmit({description_html, description_json}, isMigrationUpdate)`; danach `setIsSubmitting("submitted")`. Beim Unmount wird ein noch offener Stand sofort gespeichert. Leere Beschreibung wird als `<p></p>` normalisiert; `swrDescription` übernimmt externe Änderungen (Pseudo-Realtime). Uploads über `useEditorAsset().uploadEditorAsset` (`entity_identifier`, `entity_type = fileAssetType`), Duplizieren über `duplicateEditorAsset`; Fehler „Asset upload failed. Please try again later.“ bzw. „Asset duplication failed. Please try again later.“. Platzhalter über `getDescriptionPlaceholderI18n(isFocused, value)`; `dragDropEnabled` | `apps/web/components/issues/peek-overview/issue-detail.tsx`, `issues/issue-detail/main-content.tsx`, `inbox/content/issue-root.tsx` |
| `rich-text/description-input/loader.tsx` | `DescriptionInputLoader` | Skeleton (Zeilen 100 %/80 %/50 % × 26 px, zwei Zeilen mit 26-px-Quadrat + 400 px, rechts unten 100 px + 50 px) | `DescriptionInput`, `inbox/content/issue-root.tsx` |
| `rich-text/description-input/index.ts` | Re-Export | – | – |
| `lite-text/editor.tsx` | `LiteTextEditor` (`forwardRef`) | Wrapper um `LiteTextEditorWithRef` für Kommentare. Varianten: `full` (Default; `IssueCommentToolbar` unter dem Editor, bei `showToolbarInitially=false` nur bei Fokus, Animation `max-h-[200px] scale-y-100` ↔ `max-h-0 scale-y-0 invisible`), `lite` (kompakte `LiteToolbar` rechts neben dem Editor), `none` (keine Toolbar). Platzhalter Default „Add comment“ (`issue.comments.placeholder`), Button-Text Default `common.comment`; Mention-Suche mit `project_id` und `issue_id`; Rahmen `relative rounded-sm border border-subtle` (`p-3` außer `lite`) | `apps/web/components/comments/comment-create.tsx`, `comments/card/edit-form.tsx`, `comments/card/display.tsx`, `workspace-notifications/sidebar/notification-card/content.tsx` |
| `lite-text/toolbar.tsx` | `IssueCommentToolbar` | Leiste `flex h-9 w-full items-stretch gap-1.5 overflow-x-scroll bg-surface-2`: optional Zugriffsumschalter („Private“ `LockOutline` = `INTERNAL`, „Public“ `GlobeOutline` = `EXTERNAL`); Gruppen aus `TOOLBAR_ITEMS.lite` mit Tooltip (Name + Shortcut) und Aktiv-Zustand über `editorRef.isMenuItemActive` (aktualisiert per `onStateChange`); rechts sticky Submit-Button (primary sm), deaktiviert bei leerem Kommentar oder solange `isEditorReadyToDiscard()` falsch ist (Uploads laufen) | intern (`LiteTextEditor`) |
| `lite-text/lite-toolbar.tsx` | `LiteToolbar` | zwei Buttons: Anhang (`AttachOutline`, führt `IMAGE_ITEM` aus) und Senden (`TopArrowOutline`, `bg-accent-primary`, deaktiviert bei leer oder Senden) | intern |
| `lite-text/index.ts` | Re-Exports | – | – |
| `sticky-editor/editor.tsx` | `StickyEditor` (`forwardRef`) | `LiteTextEditorWithRef` immer editierbar, Extension `enter-key` zusätzlich deaktiviert (Enter erzeugt Zeilenumbruch), Mentions ohne Suche; Toolbar-Bereich `h-[60px] px-4` mit gleicher Fokus-Animation | `apps/web/components/stickies/sticky/inputs.tsx` |
| `sticky-editor/toolbar.tsx` | `StickyEditorToolbar` | links Palette-Button (`PaletteOutline`, Tooltip „Background color“) und `TOOLBAR_ITEMS.sticky` (Bold, Italic, To-do-list; aktiv `font-heavy`), rechts „Delete“ (`DeleteOutline`); Klick außerhalb schließt die Palette | intern |
| `sticky-editor/color-palette.tsx` | `STICKY_COLORS_LIST`, `ColorPalette` | Popover `absolute bottom-5 left-0 z-10 w-56 rounded-md bg-surface-1 p-2` „Background colors“ mit 8 Feldern `h-6 w-6`: `gray`, `peach`, `pink`, `orange`, `green`, `light-blue`, `dark-blue`, `purple` (Farbe `var(--editor-colors-<key>-background)`); Auswahl → `handleUpdate({background_color: key})` | intern |
| `sticky-editor/index.ts` | Re-Exports | – | – |
| `embeds/mentions/root.tsx` | `EditorMentionsRoot` | rendert für `entity_name === "user_mention"` `EditorUserMention`, sonst nichts | alle Wrapper, `apps/web/components/pages/editor/editor-body.tsx` |
| `embeds/mentions/user.tsx` | `EditorUserMention` | Inline-Chip `not-prose inline rounded-sm px-1 py-0.5`: eigener Nutzer `bg-label-yellow-bg text-label-yellow-text`, sonst `bg-accent-subtle-active text-accent-primary`; Link `@{display_name}` auf `/<ws>/profile/<id>`; Hover-Popover (Verzögerung 100 ms) mit Avatar `xl`, Vor-/Nachname, Projektrolle (`ROLE`); unbekannter Nutzer → „@suspended user“ (`bg-layer-1 text-tertiary`) | intern |
| `embeds/mentions/index.ts` | Re-Export | – | – |
| `pdf/document.tsx` | `PDFDocument` | `@react-pdf/renderer` `Document` + `Page` (Format aus Prop, weißer Hintergrund, Padding 64) + `react-pdf-html` mit Stylesheet: Schrift Inter (alle Schnitte registriert) bzw. Courier für Code; Typografie `h1.page-title` 1,6 rem bold, Überschriften `h1`–`h6` 1,4–0,8 rem semibold, Absätze 0,8 rem; Listen und Task-Listen (Checkbox-Quadrat, erledigt `#3f76ff`, erledigter Text `#a3a3a3`); Codeblock `#f7f7f7`, Inline-Code `#e8e8e8`/`#f97316`; Zitat mit linkem Rand `3px solid gray`; Trennlinie; Mention `#3f76ff` auf `#3f76ff33`; Tabellenzellen `1px solid #e5e5e5`. Rem-Umrechnung über `convertRemToPixel` | `apps/web/components/pages/modals/export-page-modal.tsx` |
| `pdf/index.ts` | Re-Export | – | – |

Die Toolbar-Konstanten `TOOLBAR_ITEMS.lite`/`.sticky`, `IMAGE_ITEM` und die Befehle `executeMenuItemCommand`/`isMenuItemActive` stammen aus `@plane/editor` (Analyse 12 §2.19, §2.20).

### 2.18 Workflow-Stub (`apps/web/components/workflow/`, 2 Dateien, 30 Zeilen)

| Datei | Export | Inhalt | Aufrufer |
|---|---|---|---|
| `use-workflow-drag-n-drop.ts` | `useWorkFlowFDragNDrop(groupBy, subGroupBy?)` | CE-Stub: `workflowDisabledSource: undefined`, `isWorkflowDropDisabled: false`, `getIsWorkflowWorkItemCreationDisabled: () => false`, `handleWorkFlowState: () => {}` | `apps/web/components/issues/issue-layouts/list/list-group.tsx`, `kanban/kanban-group.tsx`, `kanban/default.tsx`, `kanban/swimlanes.tsx` |
| `index.ts` | Re-Export | – | – |

Die Workflow-Regeln (erlaubte Übergänge, Sperren beim Ziehen und Anlegen) sind eine Bezahlfunktion und nach ADR-001 zu bauen: `migration/features/25-paid-workflows-automation-templates.md` F01–F08.

---

## 3. Verhalten/Logik/Abläufe im Detail (inkl. Edge-Cases)

### 3.1 Cycles

#### 3.1.1 Status-Ableitung und Gruppierung der Liste

- Der Status kommt vom Server (`ICycle.status`, Großschreibung möglich) und wird überall per `toLocaleLowerCase()` normalisiert; fehlt er, gilt `"draft"` (`list/cycles-list-item.tsx`, Kommentar „TODO: change this logic once backend fix the response“). Werte: `current`, `upcoming`, `completed`, `draft` (`packages/constants/src/cycle.ts`).
- `getFilteredCycleIds(projectId, false)` liefert alle nicht archivierten Cycles des Projekts, deren Name die Suche enthält und die `shouldFilterCycle` bestehen, danach `orderCycles`: **nur** Status `current`, `upcoming`, `draft`; Sortierung nach Statusrang (current 1, upcoming 2, draft 3), innerhalb `upcoming` nach `start_date`, sonst nach `name.toLowerCase()` (`packages/utils/src/cycle.ts`). Bei `sortByManual=true` (in CE nicht genutzt) nach `sort_order`.
- „Upcoming cycle“-Gruppe = diese Liste ohne den aktiven Cycle → enthält Upcoming **und** Draft (`cycles-view.tsx`).
- „Completed cycle“-Gruppe = `getFilteredCompletedCycleIds`: Status `completed`, sortiert nur nach „hat Startdatum“ (`sortBy(c => !c.start_date)`, d. h. mit Datum zuerst, sonst Map-Reihenfolge).
- Aktiver Cycle = erster Eintrag in `cycleMap` des Projekts mit Status `current` (`currentProjectActiveCycleId`); er wird **unabhängig von Suche/Filter** immer im Block „Active cycle“ gezeigt.
- Leerer Treffer (Upcoming- und Completed-Liste leer) zeigt den „No matching cycles“-Zustand, auch wenn ein aktiver Cycle existiert (der aktive Cycle zählt in `filteredCycleIds` mit, daher nur bei Filtern, die ihn ausschließen).
- 0 Cycles im Projekt (`currentProjectCycleIds.length === 0`) → Empty-State „Group and timebox your work in Cycles.“ mit CTA „Set your first cycle“ (disabled für Nicht-Member) (`cycles/(list)/page.tsx`).
- `cycle_view === false` → Empty-State „Cycles is not enabled for this project.“ + Button „Manage features“ → `/${ws}/settings/projects/${pid}/features` (nur Projekt-Admin; die Route existiert nicht, siehe Analyse 08 3.10).

#### 3.1.2 Suche und Filter

- Suche: Namens-Teilstring, case-insensitiv; Escape leert zuerst den Text, zweites Escape schließt und blurt; Outside-Click schließt nur bei leerem Text (`cycles-view-header.tsx`).
- Filterlogik (`shouldFilterCycle`): UND über Schlüssel; `status` = ODER innerhalb der Liste; `start_date`/`end_date`: **alle** gewählten Datumsfilter müssen erfüllt sein (UND), Cycles ohne Datum fallen heraus.
- Datumsfilterwerte (`satisfiesDateFilter`, `packages/utils/src/filter.ts`): Presets `"<n>_weeks|months;after;fromnow"` (Differenz in Kalendertagen ≥ 7/14/30/60); benutzerdefiniert `"YYYY-MM-DD;after"` (≥) / `"YYYY-MM-DD;before"` (≤); Bereich = zwei Einträge `after` + `before`.
- „Custom“: Ist bereits ein benutzerdefiniertes Datum gewählt, entfernt ein erneuter Klick alle Werte mit `-` (also alle Custom-Datumswerte, Toggle-Logik im Header); sonst öffnet `DateFilterModal` (Typ „before“/„after“/„range“, Default `range` von heute bis heute + 1 Monat, zwei Kalender, Vorschau „After: … Before: …“, Buttons „Cancel“/„Apply“) (`apps/web/components/core/filters/date-filter-modal.tsx`).
- Toggle-Algorithmus `handleFilters`: Arrays werden elementweise getoggelt; Einzelwert getoggelt; Ergebnis per `updateFilters(projectId, {[key]: newValues})` (mutiert dabei das bestehende Array, MobX-`set`).
- Applied-Filters: „x“ am Schlüssel leert den Schlüssel; „x“ am Wert entfernt den Wert; „Clear all“ setzt `filters[projectId].default = {}`. Für Guests/Viewer sind die Chips nicht editierbar.
- Filter und Suche sind **nicht** persistent (nur MobX), anders als Work-Item-Filter (Analyse 09 3.7).

#### 3.1.3 Anlegen / Bearbeiten (`modal.tsx`, `form.tsx`)

1. Öffnen: Projekt = `data.project_id` (Bearbeiten) > `projectId` der URL > erstes Workspace-Projekt. Projektwahl nur beim Anlegen, gefiltert auf `projectsWithCreatePermissions`.
2. Validierung: Titel Pflicht („Title is required“), ≤ 255 Zeichen („Title should be less than 255 characters“), Fehlertext `text-11 text-danger-primary` unter dem Feld. Datum optional (Draft = ohne Datum); `minDate` = heute (Vergangenheit nicht wählbar).
3. Payload: Formwerte + `start_date`/`end_date` als `YYYY-MM-DD` (`renderFormattedPayloadDate`) oder `null`.
4. Datumsprüfung nur, wenn beide Daten gesetzt sind: beim Anlegen immer, beim Bearbeiten nur bei geänderten Daten (`POST …/cycles/date-check/` mit `cycle_id`). `status=false` → Toast Error „You already have a cycle on the given dates, if you want to create a draft cycle, remove the dates.“ – Modal bleibt offen.
5. Anlegen: `createCycle` → Store-Eintrag; liegt heute im Zeitraum, `mutate("PROJECT_ACTIVE_CYCLE_${pid}")`; Toast „Success!“/„Cycle created successfully.“; Fehler: `err.detail` oder „Error in creating cycle. Please try again.“; danach `localStorage cycle_tab = "all"`; Modal schließt (auch nach Fehler, da `handleClose()` nach `await` immer läuft).
6. Bearbeiten: optimistisch `cycleMap[id] = {...alt, ...payload}`, `PATCH`, danach `fetchCycleDetails`; bei Fehler `fetchAllCycles` + `fetchActiveCycle` und Fehler-Toast („Error in updating cycle. Please try again.“ bzw. `err.detail`).
7. Tastatur: Tab-Reihenfolge über `getTabIndex(ETabIndices.PROJECT_CYCLE, isMobile)`; Escape schließt; Klick außerhalb schließt nicht.

#### 3.1.4 Peek (`?peekCycle`) und Detail-Sidebar

- „More details“ toggelt `peekCycle` in der Query (gleiche ID → entfernt, sonst gesetzt; übrige Query bleibt über `generateQueryParams`). Archivierte Cycles öffnen beim Zeilenklick den Peek statt der Detailseite.
- Peek lädt Details (`GET …/cycles/{id}/` bzw. `…/archived-cycles/{id}/`); Breite max. 21.5 rem; mobil `fixed` über der Liste, ab `md` `relative` neben der Liste. Schließen entfernt den Query-Parameter.
- Sidebar-Kopf: Datumsbereich direkt editierbar (Admin/Member, nicht archiviert, nicht abgeschlossen). Ablauf: beide Daten gesetzt → `date-check` (Fehler/Netzwerkfehler = ungültig) → gültig: `PATCH` (nicht abgewartet) + Toast „Success!“/„Cycle updated successfully.“; ungültig: Toast „Error!“/„You already have a cycle on the given dates, if you want to create a draft cycle, you can do that by removing both the dates.“ und Formularwert bleibt alt. Einzelnes Datum oder Leeren → ohne Prüfung gespeichert.
- „Progress“-Abschnitt: nur mit Start- und Enddatum Inhalt, sonst „No Data yet“. Chart nur wenn `start_date ≤ heute` und `end_date ≥ start_date`.
- `validateCycleSnapshot`: Ist `progress_snapshot` (abgeschlossener Cycle) nicht leer, überschreiben dessen Felder die Live-Werte (Zahlen und Verteilungen des Abschlusszeitpunkts).
- Statistik-Tabs filtern die Work-Item-Liste des Cycles (`updateFilterValueFromSidebar(EIssuesStoreType.CYCLE, cycleId, {property, operator:"in", value})`); nur interaktiv, wenn **kein** Peek offen ist (`isEditable = !peekCycle && cycleFilter !== undefined`), also nur auf der Detailseite. Mehrfachauswahl per Toggle, aktiver Eintrag `bg-layer-1`.
- „States“-Tab zeigt fünf Gruppen `backlog`, `unstarted`, `started`, `completed`, `cancelled` mit Prozent = Gruppenwert / Gesamtzahl (bei `points` Schätzpunkte).
- Bei Cycles sind Schätztyp (`estimatedType`: `issues`/`points`) und Plot-Typ (`plotType`: `burndown`/`burnup`) getrennt. `CycleProgressStats` wählt die Feldnamen der Assignee-/Label-Zeilen aber nach `plotType` (`burndown` → `completed_issues`/`total_issues`, sonst `completed_estimates`/`total_estimates`). Da kein UI `plotType` ändert, gilt immer `burndown`; im Modus „Estimates“ wird `estimate_distribution` (Felder `completed_estimates`, `total_estimates`, `pending_estimates`, `packages/types/src/cycle/cycle.ts`) mit Issue-Feldnamen gelesen → Werte `undefined`, Anzeige „0% of “ (Fehler im Original; Module verwenden `plotType="points"` korrekt, siehe 3.2.5).

#### 3.1.5 Burndown-/Progress-Chart (`components/core/sidebar/progress-chart.tsx`)

- Datenbasis: `distribution.completion_chart` bzw. `estimate_distribution.completion_chart` – Objekt `{ "YYYY-MM-DD": pendingCount }`.
- Punkte: `name = renderFormattedDateWithoutYear(key)`, `current = distribution[key] ?? 0`, `ideal = total × (1 − index/(n−1))` (lineare Ideallinie von Gesamtzahl auf 0; bei n = 1 Division durch 0 → `NaN`/`-Infinity`).
- Darstellung: `AreaChart` aus `@plane/blocks/charts/area-chart` (recharts), zwei Flächen: „Current {plotTitle}“ (Linie `#3F76FF`, Fläche `#3F76FF33`, Punkte, geglättet) und „Ideal {plotTitle}“ (Linie `#A9BBD0`, gestrichelt `6, 3`, Breite 1, ohne Füllung); X-Achse „Date“, Y-Achse „Completion“, Legende unten zentriert (marginTop 20), Höhe `h-[370px]`, `margin.bottom=30`.
- `formatActiveCycle`/`formatV1Data`/`formatV2Data` (`packages/utils/src/cycle.ts`) berechnen eine erweiterte Burn-down/Burn-up-Datenreihe je Datum mit den Feldern `date`, `scope`, `completed`, `backlog`, `started`, `unstarted`, `cancelled`, `pending`, `ideal`, `actual` für Cycle-Version 1 und 2; in CE von keiner Komponente dieses Bereichs genutzt (Pro-Chart „cycle-progress“).

#### 3.1.6 Aktiver Cycle (Inline-Dashboard)

- SWR-Schlüssel (`use-cycles-details.ts`): `PROJECT_ACTIVE_CYCLE_${pid}_PROGRESS_${cid}` (Fortschritt, kein Revalidate bei Fokus), `PROJECT_ACTIVE_CYCLE_${pid}_DURATION_${cid}` (Analytics `issues`, nur wenn `distribution` fehlt), `PROJECT_ACTIVE_CYCLE_${pid}_ESTIMATE_DURATION_${cid}` (Analytics `points`, nur wenn `estimate_distribution` fehlt), `CYCLE_ISSUES_WITH_PARAMS(cid,{priority:"urgent,high"})` (Prioritäts-Items, 30 je Seite). Derselbe Hook läuft auch auf der Detailseite und in der Sidebar.
- Fortschrittskarte lädt erst, wenn `cycle.started_issues` existiert (`hasOwnProperty`) – sonst Skeleton.
- Klick auf Gruppen/Assignees/Labels/Priority-Item ruft `handleFiltersUpdate(conditions)`: setzt den Rich-Filter-Ausdruck des Cycle-Stores (`updateFilterExpressionFromConditions`) **und** navigiert per `router.push` zur Cycle-Detailseite; das Priority-Item öffnet zusätzlich den Work-Item-Peek.
- Liste „Priority work items“ lädt Folgeseiten, sobald die Loader-Zeile sichtbar wird (`rootMargin "0% 0% 100% 0%"`), solange `nextPageResults` `true` oder `undefined` ist.

#### 3.1.7 Transfer von Work Items

- Sichtbar (Listeneintrag): Projekt-Route vorhanden, Status `completed`, `total − (cancelled + completed) > 0`; Text „Transfer {count} work items“ (ohne Plural-Regel).
- Sichtbar (Detail, `CycleLayoutRoot`): Leiste immer bei `completed`; Button nur, wenn `progress_snapshot` leer und `backlog + unstarted + started > 0`.
- Zielauswahl: `currentProjectIncompleteCycleIds` = Cycles des Projekts, nicht archiviert, Status ≠ `completed`, Enddatum nicht vergangen (enthält Draft und Upcoming; der Quell-Cycle ist als `completed` ausgeschlossen); Suche nach Name.
- Klick auf Ziel: Request wird gestartet und das Modal **sofort** geschlossen (kein Warten); Erfolg → Toast „Work items have been transferred successfully“, dann `GET …/progress/` für Quelle und Ziel (Fehler → Toast „Error“/„Unable to fetch cycle details“); Fehler → „Unable to transfer work items. Please try again.“. Der Cycle-Issue-Store lädt die aktuelle Liste neu, falls Pagination aktiv ist (`fetchIssues(..., "mutation", ...)`).

#### 3.1.8 Löschen, Archivieren, Wiederherstellen, Favoriten

- Löschen: `DELETE`; Erfolg → bei offener Detailseite oder Peek Push auf `/${ws}/projects/${pid}/cycles`; Toast „Success!“/„Cycle deleted successfully.“; Store entfernt Cycle, aktive Markierung und Favorit. Fehler: Antwort `error === "You don't have the required permissions."` → Toast `workspace_projects.error.permission`, sonst `error` + `workspace_projects.error.cycle_delete`. Modal schließt in beiden Fällen.
- Archivieren: nur abgeschlossene Cycles (Menüeintrag disabled mit Beschreibung); `POST …/archive/` → `archived_at` gesetzt, Favorit aus Store entfernt; Toast „Archive success“/„Your archives can be found in project archives.“; Push zur Cycle-Liste. Fehler werden im Store geloggt und **nicht** weitergereicht – der Fehler-Toast „Cycle could not be archived. Please try again.“ erscheint daher praktisch nie.
- Wiederherstellen: `DELETE …/archive/` → `archived_at = null`; analog werden Fehler im Store geschluckt (Erfolgs-Toast erscheint auch bei Fehler).
- Favoriten: optimistisch `is_favorite` umschalten, `setPromiseToast` mit „Adding cycle to favorites“ → „Success!“/„Cycle added to favorites.“ bzw. „Error!“/„Couldn't add the cycle to favorites. Please try again.“ (Entfernen analog); nach erfolgreichem Hinzufügen wird die Favoriten-Sektion der App-Sidebar geöffnet (`IS_FAVORITE_MENU_OPEN`). Rücksetzung bei Fehler.

#### 3.1.9 Berechtigungen (Cycles)

| Aktion | Erlaubt | Quelle |
|---|---|---|
| Cycle anlegen (Button, Empty-State-CTA) | Projekt-Admin, -Member | `cycles/(list)/header.tsx`, `cycles/(list)/page.tsx` |
| Bearbeiten, Löschen | Projekt-Admin, -Member; nicht bei `completed` oder archiviert | `quick-actions-helper.tsx` |
| Archivieren | Projekt-Admin, -Member; nur `completed` | dito |
| Wiederherstellen | Projekt-Admin, -Member; nur archiviert | dito |
| Datum in Sidebar ändern | Projekt-Admin, -Member; nicht archiviert/abgeschlossen | `analytics-sidebar/sidebar-header.tsx` |
| Favorisieren | Projekt-Admin, -Member; nicht archiviert | `list/cycle-list-item-action.tsx` |
| Filter-Chips bearbeiten | Projekt-Admin, -Member | `applied-filters/root.tsx` |
| „Add work item“, „Analytics“ im Detailkopf | Projekt-Admin, -Member („Add work item“ zusätzlich nicht bei `completed`) | `cycles/(detail)/header.tsx` |
| Feature deaktiviert → „Manage features“ | nur Projekt-Admin | `cycles/(list)/page.tsx` |

#### 3.1.10 Edge-Cases (Cycles)

| # | Verhalten im Original | Quelle |
|---|---|---|
| C1 | Mobile-Layoutmenü der Liste ändert `displayFilters.layout`, die Liste ignoriert den Wert (immer Liste) | `cycles/(list)/mobile-header.tsx`, `list/root.tsx` |
| C2 | `DateFilterModal` vergleicht `date1` mit sich selbst (`date2 = getDate(watch("date1"))`), „Apply“ ist daher nie wegen ungültigem Bereich deaktiviert | `components/core/filters/date-filter-modal.tsx` |
| C3 | `ProgressChart` mit nur einem Datum erzeugt `ideal = NaN` (Division durch 0) | `components/core/sidebar/progress-chart.tsx` |
| C4 | Archivieren/Wiederherstellen: Store fängt Fehler ab → UI zeigt immer Erfolg | `apps/web/store/cycle.store.ts` |
| C5 | Transfer-Modal schließt vor Abschluss des Requests; Doppelklick nicht möglich, aber kein Ladezustand | `transfer-issues-modal.tsx` |
| C6 | `TransferIssuesModal` nutzt `currentProjectIncompleteCycleIds` (Router-Projekt), nicht das Projekt des Cycles | `transfer-issues-modal.tsx` |
| C7 | Anlage-/Update-Modal schließt auch bei Server-Fehler | `modal.tsx` |
| C8 | Zwei verschiedene „abgeschlossen“-Definitionen: `currentProjectCompletedCycleIds` (Enddatum vor heute **oder** Status `completed`; steuert die Read-only-Sperre der Work-Item-Layouts in `issue-layouts/{list,kanban,calendar,spreadsheet}/roots/cycle-root.tsx`) vs. `getFilteredCompletedCycleIds` (nur Status `completed`; Listengruppe). Ein Cycle mit abgelaufenem Enddatum, aber Serverstatus ≠ `completed`, ist im Layout gesperrt, erscheint aber nicht in „Completed cycle“ | `apps/web/store/cycle.store.ts` |
| C9 | `CycleListProjectGroupHeader` ist ungenutzt | `list/cycle-list-project-group-header.tsx` |
| C10 | Delete-/Archive-/Transfer-Texte sind hart kodiert (nicht i18n) | `delete-modal.tsx`, `archived-cycles/modal.tsx`, `transfer-issues-modal.tsx`, `transfer-issues.tsx` |
| C11 | Analytics-Button im Detailkopf nur für Admin/Member sichtbar (an `canUserCreateIssue` gekoppelt) | `cycles/(detail)/header.tsx` |
| C12 | Assignee-/Label-Statistik der Cycle-Sidebar im Modus „Estimates“ leer (falsche Feldnamen, siehe 3.1.4) | `analytics-sidebar/progress-stats.tsx` |

### 3.2 Modules

#### 3.2.1 Liste, Filter, Sortierung

- `getFilteredModuleIds(projectId)`: nicht archivierte Module des Projekts, Name enthält Suche (case-insensitiv), `shouldFilterModule` erfüllt, dann `orderModules(order_by)` (`apps/web/store/module.store.ts`, `packages/utils/src/module.ts`).
- `shouldFilterModule`: UND über Schlüssel; `status` ODER; `lead` ODER (`lead_id`); `members` = **mindestens ein** gewähltes Mitglied in `member_ids`; Datumsfilter wie Cycles (alle müssen erfüllt sein, Module ohne Datum fallen heraus); `displayFilters.favorites` → nur `is_favorite`.
- `orderModules`: `name`/`-name` natürliche Sortierung (`Intl.Collator("en-US",{numeric:true, sensitivity:"base"})`); `progress` = `(completed+cancelled)/total` (NaN → 0; `-progress` negiert); `issues_length` nach `total_issues`, `-issues_length` nach `!total_issues` (nur „hat Items“-Partition, keine echte Absteigend-Sortierung); `target_date` aufsteigend, `-target_date` nach `!target_date` (dito); `created_at`/`-created_at` analog; `sort_order` aufsteigend. **Fehlt `order_by`, liefert die Funktion eine leere Liste** (nur theoretisch, Default ist `name`).
- Sortier-Dropdown: Wechsel des Feldes behält die Richtung bei (außer bei/zu „Manual“); „Ascending“/„Descending“ setzt/entfernt das `-`-Präfix; bei „Manual“ sind die Richtungsoptionen ausgeblendet.
- Persistenz: Display-Filter und Filter werden bei jeder Änderung vollständig nach `localStorage` geschrieben und beim Start geladen (`loadFromLocalStorage`, Fehler → Reset). Suche nicht.
- „Clear all“ leert Filter **und** setzt `favorites=false` (`clearAllFilters`).
- Applied-Filters sind auf der Listen- und Archivseite immer editierbar (`alwaysAllowEditing`), unabhängig von der Rolle.

#### 3.2.2 Layouts der Übersicht

| Layout | Darstellung | Interaktion |
|---|---|---|
| `list` | `ModuleListItem` je Modul (Fortschrittskreis, Name, Info-Button, Datumsbereich, Status-Chip, Lead, Favorit, „…“) | Zeilenklick → Detailseite (archiviert → Peek); Inline-Änderung von Datum/Status (Admin/Member, nicht archiviert) |
| `board` (Gallery) | Karten-Grid, Spaltenzahl abhängig von Breite und offenem Peek | Karte = Link zur Detailseite; Status/Datum inline; Stern + Menü außerhalb des Links |
| `gantt` (Timeline) | `GanttChartRoot` mit Modul-Blöcken (Farbe = Status), Sidebar mit Status-Icon + Name | Blöcke verschieben/Ränder ziehen (PATCH `start_date`/`target_date`, nur Rolle 20/15), Reorder nur bei `order_by=sort_order` (PATCH `sort_order = newSortOrder`), „Add block“ für Module ohne Datum; Blockklick → Detailseite |

- Inline-Änderungen (`handleModuleDetailsChange`): optimistisch im Store, `PATCH`, Erfolg → Toast „Success!“/„Module updated successfully.“, Fehler → Rollback + Toast `err.detail` oder „Module could not be updated. Please try again.“.
- Mobil (`< md`) gibt es keine Timeline-Option; Desktop-Umschalter ab `md`.

#### 3.2.3 Anlegen / Bearbeiten

- Projekt-Auswahl und Rechte wie Cycles. Pflicht: Titel (≤ 255) und Status (Default `backlog`). Keine Datumsprüfung gegen Überschneidung, kein `minDate`.
- Anlegen sendet alle Formwerte (`name`, `description`, `status`, `lead_id`, `member_ids`, `start_date`, `target_date`, `project_id`); Bearbeiten sendet ebenfalls das ganze Formular (`dirtyFields` wird übergeben, aber nicht genutzt).
- Erfolg → Toast „Success!“/„Module created successfully.“ bzw. „Module updated successfully.“ und Schließen; Fehler → Toast mit `err.detail` / `err.error` / „Module could not be created. Please try again.“ – Modal bleibt offen.
- Nach Submit wird das Formular auf Defaults zurückgesetzt.

#### 3.2.4 Sidebar (Peek und Detail)

- Status, Datum, Lead, Members sofort speichern (`submitChanges` → `updateModuleDetails`). Datum: Toast „Module updated successfully.“ erscheint **vor** dem Ergebnis (nicht abgewartet); Lead/Members/Status ohne Toast.
- Bearbeitbar nur für Projekt-Admin/-Member und nicht archivierte Module.
- „Links“: sichtbar als Liste nur für Admin/Member mit vorhandenen Links; Guests/Viewer sehen auch bei vorhandenen Links „No links added yet“ (Bedingung `isEditingAllowed && link_module.length > 0`). „Add link“ nur Admin/Member und nicht archiviert. URL ohne `http`-Präfix wird mit `http://` ergänzt. Löschen ohne Rückfrage, Toast „Module link deleted successfully.“ bzw. „Some error occurred“. Nach Schließen des Link-Dialogs wird die Bearbeitungsauswahl 500 ms verzögert zurückgesetzt.
- „Progress“: gültig, wenn Start ≤ heute und Ziel ≥ Start. Prozent-Badge: bei `points` `completed_estimate_points/total_estimate_points`, sonst `completed_issues/total_issues` (Bedingung prüft zweimal `completedIssues != 0`). Wechsel Work items/Points lädt Details neu (Spinner), Fehler → Rücksetzen.
- Statistik-Tabs wie Cycles (nur auf der Detailseite filternd); bei `plotType="points"` werden `completed_estimates`/`total_estimates` gelesen (korrekt).

#### 3.2.5 Löschen, Archivieren, Wiederherstellen, Favoriten

- Löschen: `DELETE`; Push zur Modulliste nur, wenn `useParams().moduleId` gesetzt ist (Detailseite). Die Prüfung auf `peekModule` liest einen Routen-Parameter, der nie existiert (Query-Parameter) → im Peek keine Navigation. Fehlertexte über `PROJECT_ERROR_MESSAGES.permissionError` / `moduleDeleteError`.
- Archivieren nur bei Status `completed` oder `cancelled`; Store schluckt Fehler (`console.error`) → Erfolgs-Toast „Archive success“ erscheint immer, danach Push zur Modulliste.
- Wiederherstellen: Fehler ebenfalls geschluckt → immer „Restore success“.
- Favoriten: Store fängt Fehler ab (Rollback, kein Rethrow) → `setPromiseToast` zeigt immer Erfolg („Adding module to favorites...“ → „Module added to favorites.“; Entfernen „Removing module from favorites...“ → „Module removed from favorites.“).

#### 3.2.6 Berechtigungen (Modules)

| Aktion | Erlaubt | Quelle |
|---|---|---|
| Modul anlegen | Projekt-Admin, -Member | `modules/(list)/header.tsx`, `modules-list-view.tsx` |
| Bearbeiten (Menü, Inline, Sidebar) | Projekt-Admin, -Member; nicht archiviert | `quick-actions-helper.tsx`, `module-list-item-action.tsx`, `analytics-sidebar/root.tsx` |
| Archivieren | Projekt-Admin, -Member; Status completed/cancelled | `quick-actions-helper.tsx` |
| Löschen | Projekt-Admin, -Member; nicht archiviert | dito |
| Timeline-Änderungen | Projektrolle 20 oder 15 (`member_role`) | `gantt-chart/modules-list-layout.tsx` |
| „Manage features“ bei deaktiviertem Feature | nur Projekt-Admin | `modules/(list)/page.tsx` |

#### 3.2.7 Edge-Cases (Modules)

| # | Verhalten | Quelle |
|---|---|---|
| M1 | Such-Close-Button leert die Suche nicht (nur Schließen): die Liste bleibt nach dem Text gefiltert, obwohl das Feld nicht mehr sichtbar ist (Cycles leeren beim Schließen) | `module-view-header.tsx` |
| M2 | `-issues_length`, `-target_date`, `-created_at` sortieren nur nach „hat Wert/hat Items“, nicht absteigend | `packages/utils/src/module.ts` |
| M3 | Favoriten-Stern auf Gallery-Karte auch für archivierte Module sichtbar | `module-card-item.tsx` |
| M4 | Lösch-Dialog prüft `useParams().peekModule` (nie gesetzt) | `delete-module-modal.tsx` |
| M5 | Links für Nicht-Editoren unsichtbar | `analytics-sidebar/root.tsx` |
| M6 | Archive/Restore/Favorit: Fehler werden im Store geschluckt | `apps/web/store/module.store.ts` |
| M7 | Status `completed` mit < 100 % zeigt `!` im Fortschrittskreis | `module-list-item.tsx` |
| M8 | Lead-/Members-Filter sortieren Optionen nur bei Suchänderung neu (Memo-Abhängigkeit nur `searchQuery`) | `dropdowns/filters/lead.tsx`, `members.tsx` |
| M9 | `SidebarStatusSelect` ungenutzt | `sidebar-select/select-status.tsx` |
| M10 | Sidebar-Zustand als String gespeichert (Cycle: Boolean) | `modules/(detail)/[moduleId]/page.tsx` |

### 3.3 Pages

#### 3.3.1 Liste

- Laden: `GET …/pages/` einmal je Projekt (SWR `PROJECT_PAGES_${projectId}`; die Detail-Layout-Route nutzt denselben Schlüssel). Bestehende Instanzen werden ohne `name` aktualisiert (`mutateProperties(otherFields, false)`), damit ein lokal editierter Titel nicht überschrieben wird. `loader`: `init-loader` beim ersten Laden des Tabs, sonst `mutation-loader`.
- Tab-Zuordnung (`filterPagesByPageType`): `public` = `access === 0` und nicht archiviert; `private` = `access === 1` und nicht archiviert; `archived` = `archived_at` gesetzt (unabhängig vom Zugriff). Private Pages anderer Nutzer liefert der Server nicht.
- Filter/Suche/Sortierung (`getCurrentProjectFilteredPageIdsByTab`): Name (`getPageName`, leer → „Untitled“) enthält Suche; `created_by` ODER über `owned_by`; `created_at` alle Datumsfilter (UND); `favorites` → nur Favoriten; Sortierung `name` (lowercase), `created_at`, `updated_at`, jeweils `desc` durch Umkehren. Default `updated_at desc`.
- Applied-Filters immer editierbar; „Clear all“ setzt nur `filters.filters = {}` (Suche/Sortierung bleiben).
- „Add page“ (Kopf) und Empty-State-CTA legen **ohne Dialog** eine Page an (`POST` mit `{access}`) und navigieren zur neuen Page; Fehler → Toast `err.data.error` oder „Page could not be created. Please try again.“. Der Dialog `CreatePageModal` (Titel, Logo, Zugriff) wird nur über Power-K/Command-Palette geöffnet (`toggleCreatePageModal`).
- Kontextmenü auf Listenzeilen: Rechtsklick öffnet dieselben Einträge wie „…“ (`ContextMenu parentRef`).

#### 3.3.2 Editor-Seite: Laden, Zugriff, Lebenszyklus

1. SWR `PAGE_DETAILS_${pageId}` → `GET …/pages/{id}/?track_visit=true` mit Revalidierung bei Fokus und Reconnect.
2. Solange keine Page-Instanz existiert und kein Fehler: `LogoSpinner` zentriert.
3. Fehler oder `!canCurrentUserAccessPage` → „Page not found“ / „The page you are trying to access doesn't exist or you don't have permission to view it.“ + Button „View other Pages“ (Link zur Liste).
4. `deleted_at` gesetzt → Redirect zur Liste.
5. `PageRoot` baut die Realtime-URL `ws(s)://{VITE_LIVE_BASE_URL || origin}{VITE_LIVE_BASE_PATH}/collaboration?documentType=project_page&projectId=…&workspaceSlug=…` (Protokoll `wss` bei HTTPS); ohne URL → Content-Loader. Nutzerobjekt für Awareness `{id, name: display_name, color: hslToHex(generateRandomColor(id))}`.
6. Bei jedem Page-Wechsel: Sync-Status `syncing`; Verbindungszustände `disconnected` → `error` („Connection lost“-Badge), `synced` → `synced`, sonst `syncing`.
7. Realtime-Fehler `content_too_large` → Warn-Banner oberhalb des Editors (bleibt bis Reload).
8. REST-Fallback, Titel-Sync, Stateless-Events, Deep-Link: Analyse 12 (§3.6, §3.7, §3.9, §3.12).
9. Titeländerungen (Titel-Editor) setzen `page.name`; eine MobX-Reaction mit 2 s Verzögerung sendet `PATCH {name}`; Fehler → alter Name (`oldName`).
10. Datei-Uploads im Editor: `uploadEditorAsset` mit `entity_type = EFileAssetType.PAGE_DESCRIPTION`, `entity_identifier = pageId`; Duplizieren von Assets über `duplicateEditorAsset` (Analyse 07/12).
11. Mentions: nur Nutzer (`useEditorMention`, `searchEntity` mit `project_id`); Darstellung `EditorMentionsRoot`.

#### 3.3.3 Toolbar, Anzeigeoptionen, Outline

- Toolbar nur ab `md` sichtbar und nur bei editierbarer Page mit aktivierter „Sticky toolbar“; sonst nur der Button zum Öffnen des Navigationsbereichs (oben rechts, `absolute top-0 right-0 z-10`).
- Aktive Zustände der Toolbar-Buttons werden bei jeder Editor-Statusänderung neu berechnet (`editorRef.onStateChange`). Typografie-Menü führt den Befehl nur aus, wenn sich der Typ ändert.
- `pages_config` (localStorage) gilt für alle Pages: Vollbreite (`max-w-[1152px]` statt `720px`, Klasse `wide-layout`), Schriftgröße/-art (`TDisplayConfig`, Default `large-font`, `sans-serif`; in CE ohne eigenes UI änderbar, nur Defaults), Sticky-Toolbar.
- Mini-Outline (rechts im Inhalt, `top-[64px]`, sticky `top-[72px]`): nur sichtbar bei geschlossenem Navigationsbereich; Klick öffnet Bereich mit Tab `outline`; Hover zeigt Überschriften-Popover (Klick scrollt).
- Navigationsbereich offen ⇔ `paneTab` ∈ {`outline`, `info`, `assets`}. Tabwechsel setzt `paneTab`; Wechsel weg von `info` entfernt `version`. Schließen entfernt beide Parameter.

#### 3.3.4 Lock, Access, Archive (kollaborative Aktionen)

- Ablauf (`useCollaborativePageActions`): eigene Aktion → Store-Methode mit `shouldSync=true` (optimistisch + REST: `POST/DELETE …/lock/`, `POST …/access/`, `POST/DELETE …/archive/`) → danach `editorRef.emitRealTimeUpdate(serverEventName)`; empfangene Stateless-Nachricht → Store-Methode mit `shouldSync=false` (nur lokal). Fehler → Toast mit aktionsspezifischem Text: „Page could not be locked. Please try again later.“, „Page could not be unlocked. Please try again later.“, „Page could not be archived. Please try again later.“, „Page could not be restored. Please try again later.“, „Page could not be made public. Please try again later.“, „Page could not be made private. Please try again later.“ (`apps/web/hooks/use-collaborative-page-actions.tsx`).
- Erfolgstoasts (`usePageOperations`): „Page locked successfully.“, „Page unlocked successfully.“, „The page has been marked private and moved to the private section.“ / „… public …“, „Page archived successfully.“, „Page restored successfully.“; Favoriten „Page added to favorites.“ / „Page removed from favorites.“ (danach Favoriten-Sektion der Sidebar öffnen).
- Gesperrte oder archivierte Pages sind nicht editierbar (`isContentEditable`); die Toolbar verschwindet, Logo-Picker deaktiviert, Version-„Restore“ ausgeblendet.
- Archivieren entfernt einen vorhandenen Favoriten aus dem Store; Server-Fehler beim Archivieren werden gefangen (`archived_at = null`), der Erfolgstoast erscheint dennoch.
- Realtime-Ereignisse anderer Clients (`useRealtimePageEvents`): `archived`, `unarchived`, `locked`, `unlocked`, `made-public`, `made-private`, `deleted` (Store entfernen; eigene geöffnete Page → Redirect zur Liste, bei fremdem Löscher Toast „Page deleted“ / „Page deleted by <Name>“), `property_updated` (Titel + Felder), `error` (Toast „Failed to load page“/„Failed to save page“; Codes `page_locked`/`page_archived` setzen lokal `is_locked`/`archived_at`).

#### 3.3.5 Versionen

- Liste: SWR `PAGE_VERSIONS_LIST_${pageId}` → `GET …/versions/`; Einträge mit `last_saved_at` und `owned_by`.
- Anzeige: `?version=<id>` öffnet Overlay über dem Editor (Breite minus Navigationsbereich); Inhalt read-only `DocumentEditor`; JSON wird bevorzugt, bei leerem JSON HTML.
- „Restore“ (nur `isContentEditable`): ersetzt den Editorinhalt clientseitig (`clearEditor()` + `setEditorValue(description_html ?? "<p></p>")`) – die Änderung läuft dadurch über Yjs/Live-Server; der REST-Endpunkt `…/versions/{id}/restore/` wird **nicht** verwendet. Erfolg → Toast „Page version restored.“ und Overlay schließen; Fehler „Failed to restore page version.“.

#### 3.3.6 Export

- PDF: HTML `<h1 class="page-title">{Titel}</h1>` + `editorRef.getDocument().html` → `replaceCustomComponentsFromHTMLContent` (Mentions/Work-Item-Embeds/Bilder; „No images“ entfernt Bilder) → `@react-pdf/renderer` mit `PDFDocument` (`apps/web/components/editor/pdf/document.tsx`) im Format A4/A3/A2/LETTER/LEGAL/TABLOID → Download `<dateiname>-<format>.pdf`.
- Markdown: `editorRef.getMarkDown()` → `replaceCustomComponentsFromMarkdownContent` → Download `<dateiname>.md`.
- Dateiname = Titel kleingeschrieben, alle Zeichen außer `a-z0-9-_` → `-`, Mehrfach-Bindestriche zusammengefasst. Toast „Page exported successfully.“ / „Page could not be exported. Please try again later.“; Formular-Reset 300 ms nach Schließen.
- Export erfolgt vollständig im Browser; der Live-Endpunkt `/pdf-export` wird in CE nicht genutzt (Analyse 12 §3.23).

#### 3.3.7 Löschen, Duplizieren

- Löschen nur für archivierte Pages (Menüeintrag sonst nicht sichtbar). `DELETE …/pages/{id}/`, Store entfernt Page + Favorit; auf der Detailseite `router.back()`.
- Duplizieren: `POST …/duplicate/`; die neue Page wird **nicht** in den Store übernommen – sie erscheint erst nach erneutem Laden der Liste (SWR-Revalidierung).

#### 3.3.8 Edge-Cases (Pages)

| # | Verhalten | Quelle |
|---|---|---|
| P1 | Realtime-Event `deleted` ruft `removePage({shouldSync:false})`, `removePage` ignoriert `shouldSync` und sendet erneut `DELETE` (jeder empfangende Client) | `apps/web/hooks/use-realtime-page-events.tsx`, `apps/web/store/pages/project-page.store.ts` |
| P2 | Version-Restore nutzt nicht den Restore-Endpunkt | `editor/page-root.tsx` |
| P3 | Archiv-Fehler werden geschluckt (Erfolgstoast trotz Fehler) | `apps/web/store/pages/base-page.ts` |
| P4 | Duplikat erscheint nicht sofort in der Liste | `apps/web/hooks/use-page-operations.ts` |
| P5 | „Ask Pi“-Eingabe ohne Absenden-Funktion; Ton-Buttons markieren immer „Default“ als aktiv | `editor/ai/ask-pi-menu.tsx`, `editor/ai/menu.tsx` |
| P6 | „Move“-Eintrag existiert, Modal fehlt in CE (`isMovePageEnabled=false`) | `dropdowns/actions.tsx`, `apps/web/hooks/use-page-flag.ts` |
| P7 | `CreatePageModal` nur über Command-Palette; „Add page“ legt unbenannte Page an | `pages/(list)/header.tsx`, `modals/create-page-modal.tsx` |
| P8 | Tab-Kopf (Tabs, Suche, Filter) wird ausgeblendet, solange das Projekt keine einzige Page hat | `pages-list-view.tsx` |
| P9 | `PageOfflineBadge` Punkt hat dieselbe Farbe wie der Hintergrund (`bg-layer-1` auf `bg-layer-1`) | `header/offline-badge.tsx` |
| P10 | Assets-Tab listet nur Bilder; Anhänge anderer Typen erscheinen nicht | `navigation-pane/tab-panels/assets.tsx` |
| P11 | Gelöschte-Page-Meldung „Page deleted“ hat Typ `error` | `use-realtime-page-events.tsx` |

### 3.4 Views

#### 3.4.1 Projekt-View-Liste

- Views werden beim Projekt-Bootstrap über `fetchViews` geladen (Analyse 08 3.3). `getProjectViews` sortiert nur; `getFilteredProjectViews` filtert zusätzlich: Name (`getViewName`, leer → „Untitled“) enthält Suche, `owned_by` (vergleicht mit `view.created_by`), `created_at` (alle Datumsfilter UND), `view_type` (Access; **überschreibt** das bisherige Ergebnis statt UND – nur über Applied-Filters erreichbar, die UI bietet keinen Access-Filter an), `favorites` → nur Favoriten. Sortierung `orderBy(views, [name.toLowerCase()|created_at|updated_at], [asc|desc])`; Default `updated_at desc` (`packages/utils/src/project-views.ts`).
- Der Filter-Button zeigt nie die „aktiv“-Markierung (`isFiltersApplied={false}`).
- Applied-Filters immer editierbar; Entfernen von `favorites` setzt `false`.

#### 3.4.2 Projekt-View anlegen/bearbeiten

1. Defaults: `access: PUBLIC`, Display-Properties aus `getComputedDisplayProperties()`, Display-Filter `getComputedDisplayFilters()` mit `group_by: "state"`; „Save view“ aus der Filterzeile übergibt `preLoadedData` (aktuelle Filter/Display), Bearbeiten übergibt die View (`{...DEFAULT_VALUES, ...preLoadedData, ...data}`).
2. Die Rich-Filter-Zeile im Formular arbeitet auf einer temporären Filterinstanz (`isTemporary`, `showOnMount`); Änderungen schreiben `rich_filters` ins Formular.
3. Submit sendet genau `name`, `description`, `logo_props`, `rich_filters`, `display_filters`, `display_properties`, `access` (der Access-Schalter ist im Formular nicht sichtbar – `access` bleibt Default bzw. bisheriger Wert).
4. Anlage: `POST` → Store → Navigation `/${ws}/projects/${pid}/views/${id}` → Toast „Success!“/„View created successfully.“; Fehler „Failed to create view. Please try again.“.
5. Bearbeitung: optimistisch `viewMap[id] = {...alt, ...payload}`, `PATCH`, danach Filter des View-Work-Item-Stores ersetzen (`mutateFilters`) und Rich-Filter-Ausdruck zurücksetzen (`resetExpression(PROJECT_VIEW, id, rich_filters)`); **kein** Erfolgstoast; Fehler „Failed to update view. Please try again.“ (optimistische Änderung bleibt bestehen).
6. Klick außerhalb schließt das Modal nicht (`disablePointerDismissal`).

#### 3.4.3 Gesperrte Views

- `is_locked` blendet im View-Kopf Layout-Auswahl und „Display“ aus (Projekt- und Workspace-Views). Ein UI zum Sperren gibt es in CE nicht (Bezahlfunktion, siehe 5.5).

#### 3.4.4 Veröffentlichte Views

- `anchor` gesetzt → Badge „Live“ in der Liste; Klick setzt nur einen ungenutzten lokalen State. Publish-Menüeintrag, Publish-Modal und Link (`getPublishViewLink` = `{SPACE_BASE_URL || origin}{SPACE_BASE_PATH}/views/{anchor}`) sind in CE Stubs (`useViewPublish`).

#### 3.4.5 Workspace-Views

- Standard-Views `all-issues`, `assigned`, `created`, `subscribed` (`DEFAULT_GLOBAL_VIEWS_LIST`, `packages/constants/src/workspace.ts`) sind statisch; Suche filtert deren übersetzte Labels und die Namen der eigenen Views.
- Eigene Views: `GET /api/workspaces/{ws}/views/`; Anlage mit Defaults `layout: spreadsheet`, `order_by: -created_at`; nur Spreadsheet-Layout wird dargestellt (`WorkspaceActiveLayout`).
- Bearbeiten (`updateGlobalView`): optimistische Feldübernahme; ändert sich `rich_filters` laut Antwort, wird der Filter-Ausdruck des Workspace-Issue-Stores aktualisiert und die Liste neu geladen (`fetchIssuesWithExistingPagination(..., "mutation")`). Fehler werden gefangen (Rollback), das Modal bleibt ohne Meldung offen.
- Löschen: `DELETE`, Store-Eintrag entfernt, `localStorage["global_view_filters/<id>"]` gelöscht; Fehler → Toast „Failed to delete the view. Please try again.“; Modal schließt immer. Keine Navigation nach dem Löschen (auf der Detailseite bleibt die URL der gelöschten View).

#### 3.4.6 Berechtigungen (Views)

| Aktion | Erlaubt laut UI | Quelle |
|---|---|---|
| Projekt-View anlegen | Button „Add view“: alle; Empty-State-CTA: Admin, Member, Guest | `views/(list)/header.tsx`, `views-list.tsx` |
| Projekt-View bearbeiten | Owner | `quick-actions-helper.tsx` |
| Projekt-View löschen | Owner oder Projekt-Admin | dito |
| Favorisieren | Projekt-Admin, -Member | `view-list-item-action.tsx` |
| „Add work item“ im View-Kopf | Projekt-Admin, -Member | `views/(detail)/[viewId]/header.tsx` |
| Workspace-View anlegen | alle (Button ohne Prüfung) | `workspace-views/header.tsx` |
| Workspace-View bearbeiten/löschen (Kopf-Menü) | Owner bzw. Owner/Workspace-Admin | `workspace/views/quick-action.tsx` |
| Workspace-View bearbeiten/löschen (Listenzeile) | alle (keine Prüfung) | `workspace/views/view-list-item.tsx` |
| Feature deaktiviert → „Manage features“ | Projekt-Admin | `views/(list)/page.tsx` |

#### 3.4.7 Edge-Cases (Views)

| # | Verhalten | Quelle |
|---|---|---|
| V1 | `view_type`-Filter überschreibt statt UND-Verknüpfung | `packages/utils/src/project-views.ts` |
| V2 | Filter-Button nie als aktiv markiert | `view-list-header.tsx`, `views/(list)/mobile-header.tsx` |
| V3 | Projekt-View-Update ohne Erfolgsmeldung, optimistische Änderung ohne Rollback | `modal.tsx`, `apps/web/store/project-view.store.ts` |
| V4 | Workspace-View-Update sendet zusätzliches Feld `query` (Kopie von `rich_filters`) | `workspace/views/modal.tsx` |
| V5 | `GlobalViewsHeader` ungenutzt | `workspace/views/header.tsx` |
| V6 | Listenzeilen der Workspace-Views bieten Edit/Delete ohne Rechteprüfung (Server entscheidet) | `workspace/views/view-list-item.tsx` |
| V7 | Klick auf „Live“-Badge ohne Wirkung | `view-list-item-action.tsx` |
| V8 | Workspace-View-Löschung auf der Detailseite navigiert nicht weg | `workspace/views/delete-view-modal.tsx` |
| V9 | `owned_by`-Filter vergleicht mit `created_by` | `packages/utils/src/project-views.ts` |

### 3.5 Analytics und Charts

#### 3.5.1 Tabs, Filter, Laden

1. `/:ws/analytics` leitet auf `/:ws/analytics/overview` um (`apps/web/app/routes/core.ts`, `routes/redirects/core/analytics.tsx`). Der Tab kommt aus `:tabId`. Ein Tab-Wechsel setzt den lokalen Zustand und führt `router.push("/<ws>/analytics/<tab>")` aus (`…/analytics/[tabId]/page.tsx`).
2. Die Seite rendert nichts, solange `workspaceProjectIds` undefiniert ist. Bei 0 Projekten (und `loader !== "init-loader"`) erscheint der Empty-State „Create a project“; er ist deaktiviert für Gäste und öffnet sonst das Projekt-Anlage-Modal.
3. Der Projektfilter (`AnalyticsFilterActions`) bietet die beigetretenen Projekte (`joinedProjectIds`) an und schreibt `selectedProjects` in den MobX-Store `analytics`. Er ist nicht persistent und gilt für alle Tabs.
4. Jede Kachel bzw. jedes Diagramm lädt per SWR. Die Schlüssel kombinieren `workspaceSlug`, `selectedDuration`, `selectedProjects`, `selectedCycle`, `selectedModule` und je nach Komponente `isPeekView`/`isEpic` (`total-insights.tsx`, `project-insights.tsx`, `created-vs-resolved.tsx`, `priority-chart.tsx`, `workitems-insight-table.tsx`). Gesendet werden `project_ids` (kommagetrennt, nur wenn gesetzt), `cycle_id`, `module_id` und `epic`. `selectedDuration` (Default `last_30_days`) geht nur in die Schlüssel ein: Der `date_filter` ist auskommentiert, das Zeitraum-Dropdown ebenfalls.
5. „Active Projects“ (`overview/active-projects.tsx`) lädt unabhängig vom Projektfilter (`["projectAnalyticsCount", ws]`). Der Fertigstellungsgrad ist `round(completed_issues / total_issues × 100)`, ohne Werte 0 %; über 50 % grün, sonst rot.

#### 3.5.2 Analytics-Seitenpanel (Projekt, Cycle, Modul)

- „Analytics“ in den Köpfen von Projekt-Work-Items, Cycle- und Moduldetail öffnet `WorkItemsModal`. `WorkItemsModalMainContent` setzt beim Mount `isPeekView = true`, `selectedProjects = [projectId]`, `selectedCycle` und `selectedModule`. Beim Unmount setzt es alle vier zurück, auch eine zuvor auf der Analytics-Seite getroffene Projektauswahl.
- Im Peek-Modus leitet `AnalyticsService.processUrl` die Typen `work-items` und `custom-work-items` auf `/api/workspaces/{ws}/projects/{project_ids[0]}/…` um. Ohne `project_ids` wirft der Service „project_ids parameter is required for peek view of work items“.
- Darstellung im Peek: Kennzahlen-Grid zweispaltig (Vollbild wie Seite), Insight-Tabelle je Assignee statt je Projekt (Spalten „Assignee“ statt „Project“, Kopftext „Assignee“ statt „Projects“).
- Vollbild-Umschalter ab `md`. Ein Klick außerhalb des Panels schließt es.

#### 3.5.3 Customized Insights (`work-items/customized-insights.tsx`, `priority-chart.tsx`)

- Die Defaults sind X = `PRIORITY` und Y = `WORK_ITEM_COUNT` (Epic-Modus `EPIC_WORK_ITEM_COUNT`). X-Achse und Gruppierung schließen sich gegenseitig aus: Der jeweils gewählte Wert fehlt in der anderen Auswahl, die Gruppierung bietet zusätzlich „No value“.
- Ohne Gruppierung zeichnet das Diagramm einen Balken „Count“ je X-Wert. Die Farbe kommt aus `generateBarColor`:
  - Priorität: urgent `#ef4444`, high `#f97316`, medium `#eab308`, low `#22c55e`, sonst `#ced4da`.
  - States: Farbe des Workspace-States, unbekannte ID → Palettenfarbe per Hash.
  - Alle anderen X-Werte: erste Palettenfarbe.
- Mit Gruppierung zeichnet es gestapelte Balken je Schema-Schlüssel. Die Farben stammen aus `CHART_COLOR_PALETTES[0]` (hell/dunkel nach Theme), bei Bedarf über `generateExtendedColors` erweitert. Rundung gibt es nur am obersten bzw. untersten Segment mit Wert ≠ 0.
- Datenaufbereitung über `parseChartData` (2.7):
  - fehlende Schema-Schlüssel → 0
  - Priority/State-Group mit großem Anfangsbuchstaben
  - Datumswerte nach `DAY` gruppiert: im laufenden Jahr ohne Jahreszahl, sonst mit Jahr; leer, „none“ oder „null“ → „None“
- Unter dem Diagramm steht eine Tabelle mit „Export as csv“. Der Export nimmt die aktuell gefilterten Zeilen (`getRowModel`).

#### 3.5.4 Tabellen und CSV

- `DataTable` (`insight-table/data-table.tsx`): Das Suchfeld filtert nur die erste Spalte. Es ist ausklappbar, ein X leert den Filter.
- `exportCSV` (`export.ts`): Dateiname `<workspaceSlug>-analytics.csv`, Trenner `,`, Dezimalzeichen `.`. Spalten aus `meta.export` (`label ?? key`), leere Zellen `-`. `InsightTable` exportiert die gefilterten Zeilen.

#### 3.5.5 Edge-Cases (Analytics)

| # | Verhalten | Quelle |
|---|---|---|
| A1 | `ActiveProjects` fordert `fields=total_work_items,total_completed_work_items` an. Das Backend kennt nur `total_issues`, `completed_issues`, `total_members`, `total_cycles`, `total_modules` und liefert bei ungültigen Feldern alle. Die Anzeige funktioniert also nur zufällig. „completed“ zählt dort Gruppen `completed` **und** `cancelled` | `overview/active-projects.tsx`, `apps/api/plane/app/views/analytic/base.py` (`ProjectStatsEndpoint`) |
| A2 | Schließen des Analytics-Panels löscht die Projektauswahl der Analytics-Seite | `work-items/modal/content.tsx` |
| A3 | Zeitraumfilter: Store-Feld und SWR-Schlüssel existieren, werden aber nicht gesendet; `DurationDropdown` ist ungenutzt | `apps/web/store/analytics.store.ts`, `select/duration.tsx` |
| A4 | Der SWR-Schlüssel von `TotalInsights` enthält `isPeekView` nicht. Peek und Seite teilen bei gleicher Projektauswahl denselben Cache | `total-insights.tsx` |
| A5 | Ein unbekannter `tabId` zeigt eine leere Tab-Fläche ohne aktiven Tab | `…/analytics/[tabId]/page.tsx` |
| A6 | `ESTIMATE_POINT_COUNT` ist als Y-Metrik immer ausgeblendet; `EPIC_WORK_ITEM_COUNT` nur im Epic-Modus sichtbar, der in CE nie gesetzt wird | `select/select-y-axis.tsx` |
| A7 | `AnalyticsSectionWrapper` ignoriert `subtitle` (dort stünde der Zeitraum) | `analytics-section-wrapper.tsx` |
| A8 | Der SWR-Schlüssel von `PriorityChart` enthält Zeilenumbrüche (Template-String über mehrere Zeilen). Das ist funktional unkritisch, beim Port aber nicht nachzubauen | `work-items/priority-chart.tsx` |

### 3.6 Intake

#### 3.6.1 Laden, Tabs, Paginierung

1. Erster Aufruf: `fetchInboxIssues(ws, pid, undefined, tab||open)` → `initializeDefaultFilters` setzt bei leerem Zustand Status-Filter (Open: `[-2]`, Closed: `[1,-1,2]`) und Sortierung `issue__created_at desc`. Projektwechsel leert Einträge, IDs und Pagination.
2. Request `GET …/inbox-issues/` mit 10 je Seite (`PER_PAGE_COUNT = 10`, Cursor `10:0:0`), Filter als kommagetrennte Strings, Datumsfilter über `getCustomDates` in Bereichsform `YYYY-MM-DD;after,YYYY-MM-DD;before` (Today, Yesterday, Last 7 days = heute−7 … heute, Last 30 days = heute−30 … heute) bzw. Custom-Werte direkt, Sortierung `order_by` mit `-` für absteigend (`-issue__created_at` Default).
3. Tab-Wechsel (`handleCurrentTab`): setzt Tab, leert Liste, **setzt Filter und Sortierung zurück** auf die Tab-Defaults und lädt mit `filter-loading`; URL wird auf `?currentTab=<tab>` gesetzt.
4. Filter-/Sortieränderung: setzt Wert, verwirft Pagination, lädt neu (`filter-loading` → Sidebar-Skeleton, solange keine nächste Seite bekannt).
5. Folgeseiten: IntersectionObserver auf dem Ende der Liste ruft `fetchInboxPaginationIssues`, solange `inboxIssueIds.length < total_results`; Ergebnisse werden dedupliziert angehängt.
6. Ist keine `inboxIssueId` in der URL, aber die Liste nicht leer, navigiert die Sidebar automatisch zum ersten Eintrag.
7. Detail: SWR lädt `GET …/inbox-issues/{id}/?expand=issue_inbox` und parallel Reaktionen, Activities, Kommentare, Anhänge; ist die ID nicht in der aktuellen Liste (`getIsIssueAvailable`), wird auf `…/intake?currentTab=<tab>` ersetzt (nicht bei Einbettung).

#### 3.6.2 Clientseitige Listenfilterung (`filteredInboxIssueIds`)

- Open-Tab: Filter-Status ∩ {Pending, Snoozed}. Beide gewählt → alle geladenen IDs. Nur Snoozed → Status Snoozed und `snoozed_till` in der Zukunft. Nur Pending → Status Pending **oder** Snoozed mit abgelaufenem `snoozed_till` (abgelaufene Snoozes gelten als Pending).
- Closed-Tab: Status ∈ gewählte {Accepted, Declined, Duplicate}.
- Der Status-Filter erzwingt mindestens einen Wert (Abwahl des letzten Werts wird ignoriert; im Applied-Chip fehlt das „x“ am letzten Wert).

#### 3.6.3 Anlegen

- Felder: Titel (Pflicht, ≤ 255), Beschreibung (Rich Text), Intake-State (Projekt-Singleton aus `GET …/intake-state/`, ohne Auswahl automatisch dieser State), Priorität (Default `none`), Assignees, Labels, Due date (`minDate` = Startdatum, Default heute, das selbst aber nicht gesendet wird).
- Submit prüft `isEditorReadyToDiscard()`; Payload siehe 2.8.5 (`state_id` leer → `""`). Erfolg: hochgeladene Assets per Bulk-Status bestätigen; ohne „Create more“ → Navigation `…/intake/?currentTab=open&inboxIssueId=<issueId>` und Schließen; mit „Create more“ → Editor leeren, Formular zurücksetzen; Toast „Success!“ / „Work item created successfully.“; Fehler „Some error occurred. Please try again.“.
- Store: neue ID wird angehängt, `total_results + 1`, bei Status Pending `project.intake_count + 1`.
- Escape und „Discard“ schließen nur, wenn der Editor nicht mehr verarbeitet; Klick außerhalb schließt nicht.

#### 3.6.4 Statusaktionen

| Aktion | Ablauf | Seiteneffekte |
|---|---|---|
| Accept | „Accept“ öffnet das Work-Item-Modal mit den Daten des Intake-Items (Titel „Move <IDENT-seq> to project work items“). Beim Absenden läuft zuerst `beforeFormSubmit` = `PATCH {status:1}` (danach Modal-State zurücksetzen, Navigation zum nächsten/vorherigen Eintrag), anschließend das reguläre Update des Work Items aus dem Formular (inkl. Cycle/Modul) mit Toast „Success!“ + Aktions-Links (`showActionItemsOnUpdate`) | `intake_count − 1`, `total_results − 1`, Work Item in den globalen Issue-Store übernommen |
| Decline | Bestätigung → `PATCH {status:-1}` → Navigation zum nächsten/vorherigen | `intake_count − 1` (wenn vorher Pending), `total_results − 1` |
| Snooze | Kalender (frühestens morgen in Projekt-Zeitzone; Vorbelegung: bisheriges Snooze-Datum, falls ≥ morgen, sonst morgen) → `PATCH {status:0, snoozed_till:"YYYY-MM-DD"}` (Datum gilt als Tag in der Projekt-Zeitzone) → Navigation | Pending → Snoozed: `intake_count − 1` |
| Un snooze | nur wenn `snoozed_till` gesetzt und noch Tage übrig: `PATCH {status:-2, snoozed_till:null}` → Navigation | → Pending: `intake_count + 1` |
| Mark as duplicate | Auswahl eines Work Items des Projekts (eigenes ausgeschlossen) → `PATCH {status:2, duplicate_to}`; keine Navigation | `duplicate_issue_detail` aktualisiert; vorher Pending → `intake_count − 1` |
| Delete | Bestätigung → `DELETE` → Navigation `…/intake` | `total_results − 1`; vorher Pending → `intake_count − 1`; Fehlertext bei `error === "Only admin or creator can delete the work item"` → `workspace_projects.error.permission`, sonst `issueDeleteError` |

- „Nächster/vorheriger“ Eintrag nach einer Aktion: Index+1, sonst Index−1, sonst keiner (dann `…/intake?currentTab=<tab>`).
- Fehler bei Statusänderungen werden im Store abgefangen (Rollback ohne Toast).

#### 3.6.5 Navigation und Tastatur

- Pfeil hoch/runter (global `keydown`, nicht in Einbettung, nicht während Speichern, nicht wenn Fokus im Editor `.tiptap` oder im Titel `#title-input`) wechseln zyklisch zum vorherigen/nächsten Eintrag; die URL verliert dabei `currentTab` (`…/intake?inboxIssueId=<id>`).
- Buttons „Previous work item“/„Next work item“ verhalten sich identisch.
- Klick auf den bereits gewählten Listeneintrag verhindert Navigation; auf Mobilgeräten schließt jeder Klick die Liste.

#### 3.6.6 Bearbeitbarkeit des Inhalts

`isEditable = (Projekt-Admin oder Ersteller) und Status ∉ {Declined, Accepted, Duplicate} und nicht (Guest und nicht Ersteller)`. Titel, Beschreibung, Assignees, Priorität, Due date, Labels speichern über `PATCH …/inbox-issues/{id}/ {issue:{…}}` mit optimistischer Übernahme und anschließendem Neuladen der Activities; Fehler → Rollback (die Komponente erwartet eine Exception für den Toast „Work item update failed“, der Store wirft aber keine). State ist im Intake nie änderbar.

#### 3.6.7 Edge-Cases (Intake)

| # | Verhalten | Quelle |
|---|---|---|
| I1 | CTA „Create Intake request“ im leeren Open-Tab navigiert nur zu `/intake` statt das Anlage-Modal zu öffnen | `sidebar/root.tsx` |
| I2 | Tab-Wechsel setzt alle Filter und Sortierung zurück | `apps/web/store/inbox/project-inbox.store.ts` |
| I3 | Tastaturnavigation entfernt `currentTab` aus der URL | `content/inbox-issue-header.tsx` |
| I4 | `FilterState` existiert, ist aber nicht im Filter-Panel (Applied-Chip „State“ ist vorhanden) | `inbox-filter/filters/state.tsx`, `filter-selection.tsx` |
| I5 | Datumsfilter-Modal heißt auch für „Last updated date“ „Created date“ | `inbox-filter/filters/date.tsx` |
| I6 | Erweiterte Felder im Anlage-Formular (Start, Cycle, Modules, Estimate, Parent) sind hinter `isVisible=false` verborgen | `modals/create-modal/issue-properties.tsx` |
| I7 | Store-Updates werfen keine Fehler → keine Fehlermeldungen bei Status-/Feldänderungen | `apps/web/store/inbox/inbox-issue.store.ts` |
| I8 | „Add work item“ im Intake-Kopf auch für Guests; Accept/Decline/Snooze/Duplicate-Buttons für Member sichtbar, Ausführung aber nur Admin (Toast „Permission denied“) | `projects/settings/intake/header.tsx`, `content/inbox-issue-header.tsx` |
| I9 | `total_results` wird bei jeder Statusänderung um 1 verringert, auch bei Snooze (Eintrag bleibt im Open-Tab) | `apps/web/store/inbox/inbox-issue.store.ts` |
| I10 | Intake-Bot-Ersteller wird über E-Mail-Teilstring `intake@plane.so` erkannt | `sidebar/inbox-list-item.tsx` |
| I11 | Closed-Leerzustand hart kodiert (TODO Übersetzung) | `sidebar/root.tsx` |

### 3.7 Estimates

#### 3.7.1 Anlage-Assistent (`create/modal.tsx`)

1. Beim Öffnen: System `points`, keine Werte, Fehlerliste leer.
2. Schritt 1: System wählen (Points/Categories). Ein Klick auf eine Template-Kachel oder „Custom“ übernimmt `ESTIMATE_SYSTEMS[system].templates[name].values` (2–6 Werte mit `key` 1…n) und wechselt zu Schritt 2.
3. Schritt 2 bietet folgende Aktionen:
   - Werte inline bearbeiten (✓ übernimmt nur lokal, solange kein `estimateId` existiert).
   - Neue Zeile über „Add …“. Nach dem Bestätigen öffnet sich automatisch die nächste leere Zeile, solange nur eine Anlagezeile offen ist.
   - Werte entfernen, solange mehr als 2 vorhanden sind.
   - Reihenfolge per Drag&Drop ändern: `key` wird zu Position 1…n neu nummeriert.
   - Der Zurück-Pfeil verwirft alle Werte und setzt das System auf `points`.
4. „Create estimate“ prüft `validateEstimatePointError`. Ein Fehler liegt vor, wenn für einen Eintrag die ungespeicherte Eingabe vom gespeicherten Wert abweicht, der Wert leer ist oder eine Meldung gesetzt ist. Bei Fehlern werden unveränderte nicht-leere Einträge aus der Liste entfernt. Die übrigen erhalten, falls noch ohne Meldung, „Estimate can't be empty. Enter a value in each field or remove those you don't have values for.“.
5. Payload `{estimate: {name: "Points"|"Categories", type, last_used: true}, estimate_points: [{key, value}]}`. Der Name ist immer der Systemname, nicht der Template-Name. Erfolg: Toast „Estimate created“ / „The estimate has been created successfully“, Modal schließen. Fehler: „Estimate creation failed“ / „We were unable to create the new estimate, please try again.“.
6. Das neue System wird aktives System (`last_used`), **aber nicht eingeschaltet**. `project.estimate` bleibt `null`, weil der Store-Aufruf `updateProject({estimate})` auskommentiert ist (`apps/web/store/estimates/project-estimate.store.ts`) und das Backend `project.estimate` beim Anlegen nicht setzt (`apps/api/plane/app/views/estimate/base.py`). Die Nutzer müssen danach den Schalter „Enable estimates for my project“ betätigen.

#### 3.7.2 Wertvalidierung (`points/create.tsx`, `points/update.tsx`)

| Prüfung | Meldung |
|---|---|
| leer | „Estimate value cannot be empty.“ |
| Duplikat (`isEstimatePointValuesRepeated`, `packages/utils/src/estimates.ts`: Kategorien per getrimmtem Text, Points/Time per `Number`) | „Estimate value already exists.“ |
| Points/Time: keine Zahl | „Estimate needs to be a numeric value.“ |
| Points/Time: ≤ 0 | „Estimate needs to be greater than 0.“ |
| Categories: Zahl | „Estimate needs to be a character value.“ |
| Länge > 20 Zeichen | Eingabe wird nicht übernommen |
| Serverfehler beim direkten Speichern (nur mit `estimateId`) | „We are unable to process your request, please try again.“ (Feld), Toast „Estimate creation failed“ bzw. „Estimate modification failed“ / „We were unable to modify the estimate, please try again“ |

#### 3.7.3 Aktivieren, Deaktivieren, Löschen

- Der Schalter setzt `project.estimate` auf die aktive Estimate-ID bzw. `null` (`PATCH …/projects/{pid}/`). Ein ausgeschaltetes System bleibt erhalten.
- Löschen entfernt das System (`DELETE …/estimates/{id}/`); bei eingeschalteten Estimates folgt `PATCH project {estimate: null}`. Danach zeigt die Seite wieder den Empty-State.
- Archivierte Systeme (`last_used = false`) sind nur Anzeige ohne Aktionen.

#### 3.7.4 Edge-Cases (Estimates)

| # | Verhalten | Quelle |
|---|---|---|
| E1 | Neu angelegtes System ist nicht eingeschaltet (siehe 3.7.1 Schritt 6) | `apps/web/store/estimates/project-estimate.store.ts` |
| E2 | Anlage- und Löschdialog ignorieren Escape und Klick außerhalb | `create/modal.tsx`, `delete/modal.tsx` |
| E3 | Fehler-Toast beim Löschen trägt den Titel „Estimate creation failed“ | `delete/modal.tsx` |
| E4 | Bestehende Systeme lassen sich in CE nicht bearbeiten. `points/*` unterstützen zwar `estimateId` (direkte Server-Aufrufe), werden aber nur aus dem Anlage-Assistenten ohne ID genutzt; `onEditClick`/`estimateToUpdate` sind tot. Bei vorhandener ID würde Löschen einer Zeile nur einen unsichtbaren Zustand `estimatePointDeleteToggle` setzen | `root.tsx`, `points/preview.tsx` |
| E5 | Zeit-Schätzungen („Time“, Minuten) sind ausgeblendet (`isEstimateSystemEnabled("time") = false`) | `create/helper.tsx` |
| E6 | Der Seiteninhalt ist für Nicht-Admins zwar mit `pointer-events-none opacity-60` vorgesehen, die Seite selbst lässt aber nur Admins zu | `…/estimates/page.tsx` |
| E7 | Der Empty-State-CTA prüft keine Rechte (durch E6 unkritisch) | `root.tsx` |

### 3.8 Labels

#### 3.8.1 Hierarchie und Drag&Drop (`label-utils.ts`, `label-drag-n-drop-HOC.tsx`, `apps/web/store/label.store.ts`)

- Es gibt zwei Ebenen: Wurzel-Labels und Kinder (`parent` gesetzt). Ein Wurzel-Label mit Kindern wird als Gruppe dargestellt. Der Baum entsteht per `buildTree` aus `projectLabels`, sortiert nach `sort_order`.
- `getCanDrop`: kein Drop auf sich selbst oder auf den eigenen Parent; Gruppen nicht auf Kinder.
- Blockierte Instruktionen je Ziel: `make-child` bei Kindern, `reorder-below` bei allen außer dem letzten Element einer Ebene.
- `getInstructionFromPayload` bestimmt die Instruktion in dieser Reihenfolge:
  1. Mehrere Drop-Ziele und Ziel ist Gruppe → `make-child`.
  2. Blockierte Instruktion → bei Kindern `reorder-above`, sonst `make-child`.
  3. Eine Gruppe als Quelle mit `make-child` → `reorder-above`, weil Gruppen nicht verschachtelt werden.
- Beim Drop: bei `make-child` ist der Parent das Ziel, sonst der Parent des Ziels; das Referenz-Label ist das Ziel, außer bei `make-child`; bei `reorder-below` gilt `dropAtEndOfList`.
- `updateLabelPosition` endet ohne Änderung, wenn der Parent gleich bleibt und kein Referenz-Label vorliegt. Sonst ermittelt es die Ziel-Liste (Wurzel oder Kinder des Parents) und den Index des Referenz-Labels (bzw. das Ende). Die Sortierung ergibt sich wie folgt:
  - Vorgänger und Nachfolger vorhanden: Mittelwert.
  - Nur Nachfolger: `next / 2`.
  - Nur Vorgänger: `prev + 10000`.
  - Sonst: `65535`.
  - Leere Ziel-Liste: keine `sort_order`, der Server vergibt sie.

  Payload `{parent, sort_order?}` → `PATCH …/issue-labels/{id}/`.
- „Remove from group“ setzt `parent: null`.

#### 3.8.2 Anlegen und Bearbeiten

- „Add label“ öffnet das Inline-Formular oberhalb der Liste mit einer zufälligen Farbe aus `LABEL_COLOR_OPTIONS`. Der Fokus springt auf den Namen.
- „Edit label“ ersetzt die Zeile durch das Formular und setzt `isUpdating`. Das hebt bei Gruppen das Überlauf-Clipping auf.
- Bei Fehlern bleibt das Formular mit den Eingaben offen, siehe 2.10.2 für die Meldungen.

#### 3.8.3 Edge-Cases (Labels)

| # | Verhalten | Quelle |
|---|---|---|
| L1 | Gruppenkopf (`LabelItemBlock` ohne `disabled`) zeigt Projekt-Membern den Drag-Griff (ohne Funktion, `LabelDndHOC` registriert Drag nur für Admins) und das Menü „Edit label“/„Delete label“; die Aktion scheitert dann serverseitig | `project-setting-label-group.tsx`, `label-drag-n-drop-HOC.tsx` |
| L2 | Löschen einer Gruppe löscht serverseitig die Kinder mit (`Label.parent` `on_delete=CASCADE`, `apps/api/plane/db/models/label.py`). Lokal wird nur der Parent entfernt, die Kinder verschwinden aus dem Baum, bleiben aber bis zum Neuladen im Store; der Löschdialog warnt nicht vor den Kindern | `apps/web/store/label.store.ts`, `delete-label-modal.tsx` |
| L3 | Der Aktionsbereich ist initial sichtbar (`isMenuActive` startet mit `true`), bis ein Klick außerhalb erfolgt | `label-block/label-item-block.tsx` |
| L4 | Leere Labelfarbe → Anzeige `#000` | `label-block/label-name.tsx` |
| L5 | Kein Erfolgs-Toast bei Anlegen, Bearbeiten, Löschen | `create-update-label-inline.tsx`, `delete-label-modal.tsx` |
| L6 | Der Empty-State-CTA „Create your first label“ öffnet das Anlageformular auch für Projekt-Member (der Button „Add label“ ist nur für Admins sichtbar) | `project-setting-label-list.tsx` |

### 3.9 States

#### 3.9.1 Ordnung und Drag&Drop

- Die Reihenfolge ergibt sich aus der Gruppenfolge von `STATE_GROUPS` und innerhalb der Gruppe aus `sequence` (`sortStates`, `packages/utils/src/work-item/state.ts`).
- Beim Drop auf einen State berechnet `getCurrentStateSequence` die neue `sequence`:
  - Kante oben: Mittelwert mit dem Vorgänger, ohne Vorgänger `current − 65535`.
  - Kante unten: Mittelwert mit dem Nachfolger, ohne Nachfolger `current + 65535`.
  - Ohne Kante oder ohne `sequence`: `65535`.
- Payload `{id, group: Zielgruppe, sequence}`. Ein Drop auf einen State einer anderen Gruppe verschiebt den State in diese Gruppe.
- Nicht ziehbar ist der einzige State einer Gruppe; leere Gruppen bieten kein Drop-Ziel.
- `moveStatePosition` aktualisiert optimistisch.

#### 3.9.2 Default, Anlegen, Bearbeiten, Löschen

- „Mark as default“ setzt optimistisch den bisherigen Default auf `false` und den gewählten auf `true` (`POST …/mark-default/`). Pro Projekt gibt es genau einen Default.
- Anlegen über „+“ der Gruppe: Die Gruppe klappt auf, das Formular erscheint unter dem Panel mit der Gruppenfarbe aus `STATE_GROUPS`. Erfolg schließt das Formular.
- Bearbeiten ersetzt die Karte durch das Formular.
- Löschen ist gesperrt für den Default-State und den einzigen State einer Gruppe (Tooltip statt Dialog). Hat der State Work Items, lehnt der Server mit 400 ab.

#### 3.9.3 Edge-Cases (States)

| # | Verhalten | Quelle |
|---|---|---|
| S1 | Optimistische Updates in `moveStatePosition` und `markStateAsDefault` halten das Original nur als Referenz auf dasselbe, mutierte Objekt; ein Rollback stellt nichts wieder her | `apps/web/store/state.store.ts` |
| S2 | Die DnD-Registrierung in `StateItem` gibt die Cleanup-Funktion von `combine(...)` nicht zurück, Listener werden bei jedem Effektlauf erneut registriert | `state-item.tsx` |
| S3 | Ladezustände „Creating“, „Updating“, „Marking as default“ werden nie angezeigt (Loader wird nicht bzw. sofort wieder auf `false` gesetzt) | `create-update/create.tsx`, `update.tsx`, `options/mark-as-default.tsx` |
| S4 | Leerer Name: Feld wird rot, die Meldung „Name is required“ erscheint nicht | `create-update/form.tsx` |
| S5 | React-Key der State-Liste ist `state.name` | `state-list.tsx` |
| S6 | Fehlerbehandlung `errorStatus.data.error` in `StateCreate` greift ohne Prüfung auf `data` zu | `create-update/create.tsx` |
| S7 | `getStatePercentageInGroup` liefert −1 für unbekannte States; die Icon-Füllung wird dann mit −0,01 berechnet | `apps/web/store/state.store.ts`, `state-item-title.tsx` |

### 3.10 Webhooks

#### 3.10.1 Anlegen und Secret

1. „Add webhook“ öffnet den Dialog. Ereignistyp-Default ist „Send me everything“; bei „Select individual events“ erscheinen fünf Checkboxen (alle vorausgewählt).
2. Absenden sendet `POST …/webhooks/` mit `url` und den Booleans. Das Backend erzeugt das Secret; der Store trennt `secret_key` aus der Antwort ab und hält es nur im Speicher (`webhookSecretKey`).
3. Danach lädt der Browser sofort eine CSV-Datei mit allen Webhook-Feldern und dem Secret herunter, der Dialog zeigt „Key created“. Das Secret ist maskiert (30 Punkte) und lässt sich anzeigen und kopieren. Ab jetzt ist der Dialog nur noch über „Close“ zu schließen.
4. Nach dem Schließen (auch auf der Listen-Seite per Effekt) wird das Secret aus dem Store gelöscht. Das Secret eines bestehenden Webhooks ist danach nie wieder abrufbar, nur neu erzeugbar.

#### 3.10.2 Bearbeiten, Aktivieren, Löschen

- Liste: Der Schalter je Eintrag patcht `is_active` ohne Rückmeldung; ein Klick auf die Zeile öffnet die Detailseite.
- Detail: Das Formular ist mit den Werten vorbelegt. Der Ereignistyp wird abgeleitet: alle fünf `true` → „all“. „Update“ sendet `{url, is_active, project, cycle, module, issue, issue_comment}`.
- „Re-generate key“: `POST …/regenerate/`, Toast „New key regenerated successfully.“. Danach steht das neue Secret im Store (anzeigen und kopieren möglich).
- Löschen über „Danger zone“ → Bestätigung → `DELETE`, dann `router.replace` auf die Liste.

#### 3.10.3 Edge-Cases (Webhooks)

| # | Verhalten | Quelle |
|---|---|---|
| W1 | Wechsel von „individual“ auf „all“ auf der Detailseite ändert nichts: Die Seite sendet die Checkbox-Werte und ignoriert den Ereignistyp | `…/webhooks/[webhookId]/page.tsx`, `form/form.tsx` |
| W2 | „Re-generate key“ lädt die CSV mit dem Secret aus dem Render-Zeitpunkt. Beim ersten Regenerieren nach dem Laden der Seite (Secret `null`) entsteht keine Datei, bei weiteren Regenerierungen enthält sie das vorherige Secret | `form/secret-key.tsx` |
| W3 | „Re-generate key“ erscheint auch im Erfolgsschritt des Anlegedialogs; dort ist `currentWebhook` leer, eine CSV entsteht nie | `generated-hook-details.tsx`, `form/secret-key.tsx` |
| W4 | Nicht-Admins sehen auf der Detailseite nur einen Text statt `NotAuthorizedView` | `…/webhooks/[webhookId]/page.tsx` |
| W5 | Der Listen-Schalter hat weder Fehlerbehandlung noch Toast | `webhooks-list-item.tsx` |
| W6 | Die URL wird clientseitig nur über die Pflichtregel („URL is required“) und die native `type="url"`-Prüfung des Browsers validiert; Erreichbarkeit der URL und eine Beschränkung auf `https` prüft das Frontend nicht | `form/form.tsx`, `form/input.tsx` |

### 3.11 API-Tokens

1. „Add access token“ öffnet den Dialog. Titel ist Pflicht, die Beschreibung optional.
2. Ablauf: Ohne „Never expires“ muss eine Option gewählt sein, sonst erscheint der Toast „Please select an expiration date.“.
   - Vorgaben: heute + 1 Woche, 1 Monat, 3 Monate oder 1 Jahr, als ISO-Zeitstempel.
   - „Custom“: gewähltes Datum (frühestens morgen) plus aktuelle Uhrzeit.
   - „Never expires“: `expired_at: null`.
3. Nach „Generate token“ (`POST /api/users/api-tokens/`) zeigt der Dialog das Token einmalig im Klartext (Klick kopiert). Parallel lädt der Browser eine CSV-Datei herunter. Das Token erscheint vorn in der Liste.
4. Die Liste zeigt Aktiv/Abgelaufen nach `is_active` vom Server und das Ablaufdatum mit Uhrzeit bzw. „Expired <vor X>“.
5. Löschen: Bestätigung → `DELETE /api/users/api-tokens/{id}`. Der SWR-Cache wird lokal gefiltert, ohne Neuladen.

Edge-Cases: T1 Der Dialog lässt sich weder per Escape noch per Klick außerhalb schließen (`create-token-modal.tsx`). T2 Das Lösch-Icon erscheint nur bei Hover und ist auf Touch-Geräten kaum erreichbar (`token-list-item.tsx`). T3 Pfade für `retrieve`/`destroy` ohne abschließenden Schrägstrich (`packages/services/src/developer/api-token.service.ts`). T4 `last_used` ist vorhanden, wird aber nicht angezeigt.

### 3.12 Exporter

1. Projekte (optional, leer = alle eigenen Projekte laut Backend) und Format wählen. „Export“ sendet `POST …/export-issues/` mit `multiple = project.length > 1`. Die Checkbox „Export the data into separate files“ existiert nur im ungenutzten `Exporter`-Dialog.
2. Erfolg: Toast, dann Neuladen der Liste „Previous exports“ (Seite 1 mit Cursor `10:0:0`).
3. Solange ein Eintrag `processing` ist, lädt die Liste alle 3 s neu. „Refresh status“ lädt manuell, „Prev“/„Next“ blättern per `prev_cursor`/`next_cursor`.
4. Download: Link auf `url` des Eintrags in neuem Tab, nur bei `completed` und `created_at` jünger als 7 Tage (rein clientseitige Prüfung). Ältere Einträge zeigen „Expired“.

Edge-Cases: X1 `rich_filters` wird gesendet, aber das Backend wertet es nicht aus; die Filter-UI ist auskommentiert (`export-form.tsx`, `apps/api/plane/app/views/exporter/base.py`). X2 Die Liste ruft `…/export-issues` ohne abschließenden Schrägstrich auf, das POST mit (`apps/web/services/integrations/integration.service.ts`, `project-export.service.ts`). X3 Die angebotenen Projekte sind auf Projekte mit Create-Recht beschränkt, das Backend exportiert bei leerer Auswahl aber alle Mitgliedsprojekte. X4 Die 7-Tage-Grenze ist im Client hart kodiert; der Status `expired` vom Server wird separat als Badge gezeigt.

### 3.13 Automation

- Auto-Archive: Der Schalter setzt `archive_in` auf 1, wenn er vorher 0 war, sonst auf 0. Die Monatsauswahl patcht `archive_in`. „Customize time range“ schließt das Select und öffnet den Dialog (1–12).
- Auto-Close: Der Schalter setzt `{close_in: 1, default_state: <erster cancelled-State>}` bzw. `{close_in: 0, default_state: null}`. Die Monatsauswahl patcht `close_in`, die Statusauswahl `default_state`. Als Status sind nur States der Gruppe `cancelled` wählbar.
- Die Ausführung (Archivieren nach `archive_in` Monaten in completed/cancelled, Schließen nach `close_in` Monaten Inaktivität in `default_state`) erfolgt serverseitig (Analyse 07).

Edge-Cases: AU1 Der Dialog „Customize time range“ für Auto-Close sendet immer auch `default_state` = erster cancelled-State und überschreibt damit eine abweichende Statuswahl (`auto-close-automation.tsx`, `select-month-modal.tsx`). AU2 Der Zahlenwert aus dem Dialog wird als Text aus dem Input übernommen (`InputField` liefert das Event an `react-hook-form`) (`select-month-modal.tsx`). AU3 Ist `archive_in`/`close_in` `undefined`, gilt die Automation als aus, ein Klick setzt sie auf 0 statt 1. AU4 `onSubmit` prüft `!workspaceSlug && !projectId` (UND statt ODER).

### 3.14 Integrationen

Die Integrationsoberfläche ist in CE nicht erreichbar:
- Die Seite `…/settings/(workspace)/integrations/page.tsx` ist nicht als Route registriert.
- `components/project/integration-card.tsx` (Konsument von `SelectRepository` und `SelectChannel`) wird nirgends eingebunden.
- Das Backend registriert keine Integrations-URLs.

Das Verhalten beschränkt sich damit auf den OAuth-Popup-Ablauf in `useIntegrationPopup`: Fenster öffnen, jede Sekunde prüfen, ob es geschlossen wurde, dann den Ladezustand beenden. Eine Ergebnisauswertung findet nicht statt.

### 3.15 Editor-Wrapper

- `DescriptionInput` speichert 1 500 ms nach der letzten Änderung. Identischer Inhalt (`lastSavedContent`) löst keine Speicherung aus. Beim Unmount wird ein offener Stand gespeichert. `isMigrationUpdate` (reine Block-ID-Ergänzung) wird an `onSubmit` durchgereicht; die Konsumenten senden dann `skip_activity` (Analyse 12 §3.1, Analyse 09).
- `LiteTextEditor`: Enter sendet über `onEnterKeyPress` (Extension `enter-key`). Der Submit-Button ist gesperrt, solange der Kommentar leer ist oder Uploads laufen (`isEditorReadyToDiscard`).
- `StickyEditor`: Enter fügt einen Zeilenumbruch ein (Extension `enter-key` deaktiviert). Eine Farbwahl schreibt `background_color` des Stickies.
- `EditorUserMention`: Hover öffnet nach 100 ms die Profilkarte. Ein Klick navigiert zum Profil. Gelöschte oder unbekannte Nutzer erscheinen als „@suspended user“.

---

## 4. Abhängigkeiten zu anderen Bereichen

### 4.1 Eingehend (dieser Bereich nutzt)

| Bereich | Genutzte Bausteine | Verweis |
|---|---|---|
| Web-Architektur | Routen und Redirects (`apps/web/app/routes/core.ts`), Guards/Layouts, Store-Baum (`CoreRootStore` mit `cycle`, `cycleFilter`, `module`, `moduleFilter`, `projectPages`, `projectView`, `globalView`, `projectInbox`, `projectEstimate`, `label`, `state`, `analytics`; Sub-Store `workspaceRoot.webhook`), Services, Hooks, Browser-Storage, Bezahl-Erweiterungspunkte | Analyse 08 §2.2, §2.3, §2.5, §2.7, §2.8, §2.10, §2.16 |
| Work-Item-Layouts | `CycleLayoutRoot`, `ModuleLayoutRoot`, `ProjectViewLayoutRoot`, `AllIssueLayoutRoot`; Rich-Filter-Zeile und „Save view“; Work-Item-Modal (`CreateUpdateIssueModal`, Accept-Flow im Intake); Dropdowns (`ProjectSelect`, `MemberSelect`, `LabelSelect`, `PrioritySelect`, `CycleSelect`, `DateSelect`); Activity/Kommentare im Intake-Detail; Gantt-Engine für Modul-Timeline | Analyse 09 §2.5, §2.11, §2.15, §2.16, §2.19, §3.8 |
| Editor/Echtzeit | `CollaborativeDocumentEditorWithRef` (Pages), `DocumentEditorWithRef`, `RichTextEditorWithRef`, `LiteTextEditorWithRef`, `TOOLBAR_ITEMS`, `EditorRefApi` (`getDocument`, `clearEditor`, `setEditorValue`, `emitRealTimeUpdate`, `isEditorReadyToDiscard`), Stateless-Events, REST-Fallback, Live-PDF-Export (in CE ungenutzt) | Analyse 12 §2.1–§2.20, §2.27, §3.6, §3.7, §3.9, §3.23 |
| Design-System | `@makeplane/propel` (Dialog, Menu, Tabs, Collapsible, Select, Switch, Tooltip, Popover, Button, IconButton, InputField, Checkbox, Table, Avatar), `@plane/blocks` (`ListItem`, `ConfirmDialog`, `EmptyStateCompact`/`EmptyStateDetailed`, `Loader`, `ColorSwatchPicker`, `Sortable`, `DropIndicator`, `DragHandle`, `ModalPortal`, Charts `AreaChart`/`BarChart`/`RadarChart`, `toast`), Icons, Tokens | Analyse 13a §2.22–§2.27, §2.31 |
| Shared Packages | `packages/constants` (`CYCLE_STATUS`, `MODULE_STATUS`, `ESTIMATE_SYSTEMS`, `STATE_GROUPS`, `LABEL_COLOR_OPTIONS`, `PROJECT_AUTOMATION_MONTHS`, `EXPORTERS_LIST`, `ANALYTICS_*`, `INBOX_STATUS`, `DEFAULT_GLOBAL_VIEWS_LIST`, Fetch-Keys); `packages/utils` (`cycle.ts`, `module.ts`, `project-views.ts`, `page.ts`, `intake.ts`, `estimates.ts`, `work-item/state.ts`, `array.ts#buildTree`, `filter.ts`); `packages/types`; `packages/services` (`APITokenService`); `packages/i18n` | Analyse 13b §2.1–§2.4, §2.7, §3.4, §3.6, §3.7 |
| Shell, Sidebar, Power-K, Einstellungsrahmen, Profil | Anlage-Modals über die Command-Palette (`toggleCreateCycleModal`, `toggleCreateModuleModal`, `toggleCreatePageModal`, `toggleCreateProjectModal`), Sidebar-Favoriten, Settings-Layout (`SettingsContentWrapper`, `SettingsHeading`, `SettingsBoxedControlItem`, `SettingsControlItem`), Profil-Tab `api-tokens` | Schwesteranalyse 10a |
| Backend-API | Endpunkte je Bereich in 2.1.4, 2.3.5, 2.4.5, 2.5.5, 2.6.5, 2.8.5, 2.9.3, 2.10.2, 2.11.2, 2.12.2, 2.13.2, 2.14.2, 2.16 | Analysen 03 und 04 |
| Hintergrundjobs | Webhook-Auslieferung, Issue-Export (`issue_export_task`), Auto-Archive/Auto-Close, Page-Versionen | Analyse 07 §2.10, §2.12, §3.4, §3.5, §3.7, §3.10 |
| Auth/Sicherheit | API-Token-Authentifizierung, Webhook-Signatur, Rollenprüfung serverseitig | Analyse 06 |

### 4.2 Ausgehend (andere Bereiche nutzen)

| Konsument | Genutzter Baustein aus diesem Bereich | Quelle |
|---|---|---|
| Work-Item-Layouts und -Köpfe (Analyse 09) | `TransferIssues`-Leiste (`cycle-layout-root.tsx`), `useWorkFlowFDragNDrop` (List/Kanban), `WorkItemsModal` (Analytics-Button in `issues/filters.tsx` und den Köpfen von Projekt-Work-Items, Cycle- und Moduldetail), `DescriptionInput` (Peek, Detail), `LiteTextEditor` (Kommentare), `RichTextEditor` (Work-Item-Modal) | `apps/web/components/issues/issue-layouts/roots/cycle-layout-root.tsx`, `issues/issue-layouts/kanban/{kanban-group,default,swimlanes}.tsx`, `issues/issue-layouts/list/list-group.tsx`, `issues/filters.tsx`, `issues/peek-overview/issue-detail.tsx`, `issues/issue-detail/main-content.tsx`, `issues/issue-modal/components/description-editor.tsx`, `comments/comment-create.tsx`, `comments/card/edit-form.tsx`, `comments/card/display.tsx` |
| Stickies | `StickyEditor`, `STICKY_COLORS_LIST` | `apps/web/components/stickies/sticky/inputs.tsx` |
| Benachrichtigungen | `LiteTextEditor` (read-only Kommentaranzeige) | `apps/web/components/workspace-notifications/sidebar/notification-card/content.tsx` |
| Profil-Aktivität, GPT-Popover, Beschreibungsversionen | `RichTextEditor` | `apps/web/components/profile/activity/activity-list.tsx`, `core/modals/gpt-assistant-popover.tsx`, `core/description-versions/modal.tsx` |
| Work-Item-Dropdowns und -Filter | Intake-State (`IntakeStateSelect`), Cycle-/Modul-Daten aus den Stores, States/Labels/Estimates aus den Stores | Analyse 09 §2.19 |

## 5. Migrationshinweise für Angular

### 5.1 1:1 übertragbar

| Baustein | Begründung | Quelle |
|---|---|---|
| Reine Logik in `packages/utils`: `orderCycles`, `shouldFilterCycle`, `calculateCycleProgress`, `formatActiveCycle`/`formatV1Data`/`formatV2Data`, `orderModules`, `shouldFilterModule`, `getFilteredProjectViews`-Regeln, Page-Filter/-Sortierung, `getCustomDates`, `isEstimatePointValuesRepeated`, `convertMinutesToHoursMinutesString`, `sortStates`, `getCurrentStateSequence`, `buildTree`, `satisfiesDateFilter` | framework-frei (TypeScript), direkt in ein Angular-Workspace-Paket übernehmbar | Analyse 13b §1.3, §2.4 |
| Lokale Algorithmen in Komponenten: Label-`sort_order` (65535/Mittelwert/`next/2`/`prev + 10000`), Label-Drop-Instruktionen (`getInstructionFromPayload`, `getCanDrop`), `parseChartData`, `generateExtendedColors`, `generateBarColor`, `exportCSV`/`csvConfig`, `getCurrentHookAsCSV`, Ablaufdatums-Berechnung der API-Tokens, Intake-Listenfilter (`filteredInboxIssueIds`), Schätzwert-Validierung | reine Funktionen; beim Port aus Komponenten bzw. Stores in Services/Utils ziehen | 2.7, 2.10.2, 3.5.3, 3.6.2, 3.7.2, 3.8.1, 3.11 |
| Konstanten: `CYCLE_STATUS`, `MODULE_STATUS`, `ESTIMATE_SYSTEMS`, `estimateCount`, `STATE_GROUPS`, `LABEL_COLOR_OPTIONS`, `PROJECT_AUTOMATION_MONTHS`, `EXPORTERS_LIST`, `ANALYTICS_*`, `INBOX_STATUS`, `DEFAULT_GLOBAL_VIEWS_LIST`, `STICKY_COLORS_LIST`, `INDIVIDUAL_WEBHOOK_OPTIONS`, `EXPIRY_DATE_OPTIONS`, `WORKSPACE_ACTIVE_CYCLES_DETAILS` (bis zur Ablösung) | Datenobjekte | 2.x |
| `@atlaskit/pragmatic-drag-and-drop` (Kern, `hitbox/tree-item`, `hitbox/closest-edge`, `auto-scroll`) | Vanilla-JS; in Angular per Direktive auf `ElementRef` nutzbar, gleiche Instruktionen und Drop-Indikatoren | 2.10.2, 2.11.2 |
| `@tanstack/table-core` (Analytics-Tabellen, Exporter-Tabelle) | `@tanstack/angular-table` verfügbar; Spalten-Definitionen inklusive `meta.export` übertragbar | 2.6.2 |
| `export-to-csv`, `date-fns` | framework-frei | 2.6.2, 2.13.2 |
| i18n-Schlüssel und Texte | ICU-Format (`months_count` mit `plural`) bleibt; Angular-i18n muss ICU-Plural unterstützen | Analyse 13b §5.2 |

### 5.2 Neu zu bauen

| Baustein | Hinweis | Quelle |
|---|---|---|
| MobX-Stores und SWR | Signal-basierte Services mit eigenem Request-Cache. SWR-Semantik nachbilden: Schlüssel, `revalidateOnFocus`, `revalidateIfStale: false` bei States, lokale `mutate`-Updates bei Tokens und Integrationen | 2.x, 3.x |
| Formulare (`react-hook-form`) | Reactive Forms mit identischen Regeln und Meldungen. Beispiele: Titel ≤ 255, Label ≤ 255, State-Name ≤ 100, Monate 1–12, Schätzwert ≤ 20 Zeichen | 2.9–2.15 |
| Charts | Kein recharts in Angular. Eigene Chart-Komponenten (D3 bzw. eine Bibliothek mit voller Stilkontrolle) müssen die Optik der Wrapper `AreaChart` (gestapelt, geglättet, ohne Punkte), `BarChart` (gestapelt, Rundung nur außen), `RadarChart` (Füllung 0,6, Punktradius 4) und des Burndown-Charts (`ProgressChart`) treffen | 2.6.2, 3.5.3, 3.1.5 |
| PDF-Export der Pages | `@react-pdf/renderer` + `react-pdf-html` sind React-gebunden. Ersatz: Erzeugung im Browser mit eigenem HTML→PDF-Mapping des Stylesheets aus `pdf/document.tsx` oder serverseitig in .NET (Analyse 12 §5.6). Seitenformate A4, A3, A2, Letter, Legal, Tabloid | 2.17, 3.3.6 |
| Editor-Wrapper | Angular-Hüllen um den portierten Editor-Kern (Analyse 12 §5.1, §5.2) mit Autosave (1 500 ms, Speichern beim Zerstören), Mention-Chip mit Hover-Karte, Kommentar-/Sticky-Toolbars | 2.17, 3.15 |
| Dialog-Semantik | Je Dialog festhalten, ob Escape und Klick außerhalb schließen: Estimates (beides gesperrt), API-Token (beides gesperrt), Webhook (Klick gesperrt, Escape bis zur Erzeugung erlaubt), Intake-Anlage (Klick gesperrt) | 2.9.2, 2.12.2, 2.13.2, 3.6.3 |
| Peek und Panels | Query-Parameter `peekCycle`, `peekModule`, `inboxIssueId`, `currentTab`, `paneTab`, `version` als Router-Zustand; Analytics-Panel als Portal rechts mit Outside-Click | 2.1.5, 2.3.6, 2.4.6, 2.8.6, 3.5.2 |
| Endlos-Laden und Polling | Intake-Liste per IntersectionObserver (10 je Seite), Export-Historie mit 3-s-Polling bei `processing`, GitHub-Repos per Seitenzähler | 3.6.1, 3.12, 2.16 |
| Tastatur | Intake: Pfeil hoch/runter global (Ausnahmen `.tiptap`, `#title-input`) | 3.6.5 |

### 5.3 Anforderungen an die .NET-API (aus Frontend-Sicht)

- **Pfade und Schrägstriche:** Pfade und Payloads der Endpunkte aus 2.x unverändert übernehmen. Einige Aufrufe kommen ohne abschließenden Schrägstrich: `GET/DELETE /api/users/api-tokens/{id}`, `GET /api/workspaces/{ws}/export-issues`. Das ASP.NET-Routing muss beide Varianten annehmen.
- **Einmalige Geheimnisse:** Webhook-Secret nur in den Antworten von Create und `regenerate/`, API-Token nur in der Create-Antwort; Listen und Detail liefern sie nie. `is_active` der Tokens berechnet der Server aus `expired_at` (`APITokenReadSerializer.get_is_active`, `apps/api/plane/app/serializers/api.py`; `token` ist in Lese-Antworten ausgeschlossen).
- **Estimates:**
  - Create (`{estimate:{name,type,last_used}, estimate_points}`) setzt `project.estimate` nicht; das bisherige Verhalten erzeugt E1.
  - Archivierte Systeme sind `last_used = false`.
  - Löschen entfernt das System von allen Work Items.
- **Labels:** `sort_order` als Gleitkommazahl. Doppelter Name → Fehler mit `LABEL_NAME_ALREADY_EXISTS` im Feld `name`. Löschen einer Gruppe kaskadiert auf die Kinder.
- **States:**
  - 400 bei doppeltem Namen.
  - 400 beim Löschen eines States mit Work Items.
  - `mark-default/` garantiert genau einen Default.
  - `sequence` als Gleitkommazahl; `group` per PATCH änderbar.
- **Intake:** Status `-2` Pending, `-1` Declined, `0` Snoozed, `1` Accepted, `2` Duplicate; `snoozed_till` als Kalendertag in der Projekt-Zeitzone; `duplicate_to`; Liste mit Cursor `10:0:0` und Filtern als Komma-Strings (2.8.5).
- **Analytics:** `advance-analytics`, `advance-analytics-stats`, `advance-analytics-charts` jeweils auf Workspace- und (für `work-items`/`custom-work-items` im Peek) Projektebene. `project-stats` mit Feldauswahl und Fallback auf alle Felder (A1).
- **Exporter:**
  - Provider `csv`, `xlsx`, `json`.
  - Leere Projektliste → alle Mitgliedsprojekte.
  - Status `processing`, `completed`, `failed`, `expired`.
  - Download-URL in `url`.
  - Das Frontend sperrt Downloads nach 7 Tagen.
- **Automationen:** Projektfelder `archive_in`, `close_in` (Monate, 0 = aus) und `default_state`; Ausführung als Hintergrundjob (Analyse 07 §3.7).
- **Integrationen:** In CE gibt es keine Endpunkte. Neue Integrations-APIs gemäß `migration/features/28-paid-integrationen-importer-ai.md` §3.A.

### 5.4 Fallstricke

| Fallstrick | Entscheidung nötig / Hinweis | Belege |
|---|---|---|
| Fehlerhafte Originalverhalten, die funktional relevant sind | korrigieren statt nachbauen empfohlen: C2 (Datumsbereich nie ungültig), C8 (zwei „abgeschlossen“-Definitionen), P1 (DELETE-Echo bei Realtime-Löschung), I7/I9 (verschluckte Fehler, falsche Zähler), E1 (Estimate nicht eingeschaltet), L2 (Kinder beim Gruppenlöschen), S1 (wirkungsloser Rollback), W1/W2 (Webhook-Ereignistyp, CSV mit altem Secret), A1 (Feldnamen `project-stats`), X1 (`rich_filters` ignoriert), AU1 (Status-Reset beim Monatsdialog) | 3.1.10, 3.3.8, 3.6.7, 3.7.4, 3.8.3, 3.9.3, 3.10.3, 3.5.5, 3.12, 3.13 |
| Optische Eigenheiten | beibehalten (ADR-005): hart kodierte englische Texte (C10, I11, Labels-/States-/Webhook-Texte), Großschreibung der Gruppenschlüssel („Cancelled“), Badge-Farben `bg-yellow-500/20` und `bg-orange-500/20` im Exporter | 3.1.10, 2.11.2, 2.14.2 |
| Rechte nur im Client | viele Aktionen sind nur ausgeblendet (L1, L6, V6, I8); die .NET-API muss jede Aktion selbst prüfen | 3.8.3, 3.4.7, 3.6.7 |
| Zeitzonen | Cycle-Daten, Snooze-Datum (Projekt-Zeitzone), Ablaufdaten der Tokens (lokale Uhrzeit + Datum), 7-Tage-Grenze der Exporte; .NET muss `DateOnly` vs. `DateTimeOffset` je Feld exakt abbilden | 3.1.3, 3.6.4, 3.11, 3.12 |
| Browser-Speicher-Kompatibilität | Schlüssel aus 1.3 unverändert verwenden, damit bestehende Nutzerzustände greifen; `module_sidebar_collapsed` ist ein String, `cycle_sidebar_collapsed` ein Boolean | 2.1.5, 2.3.6, 3.2.7 M10 |
| Externe Links und CDN | Archiv-Hinweis Estimates (`docs.plane.so`), Upsell `MARKETING_PRICING_PAGE_LINK`, GitHub/Slack-OAuth; im Airgap-Betrieb entfernen bzw. konfigurierbar machen | 2.9.1, 2.2, 2.16 |
| Tote Bausteine | nicht portieren, aber dokumentiert halten: `EstimateEmptyScreen`, `EstimateSearch`, `StateDeleteModal`, `WebhooksEmptyState`, `ApiTokenEmptyState`, `Exporter`, `SingleExport`, `CycleListProjectGroupHeader`, `SidebarStatusSelect`, `GlobalViewsHeader`, `DurationDropdown`, `AnalyticsEmptyState`, `TrendPiece`, `ApiTokenStore`, Integrationskomponenten | 2.x |

### 5.5 Bezahlfunktionen dieses Bereichs (ADR-001: alle zu bauen)

| Funktion | CE-Spur | Spezifikation |
|---|---|---|
| Workspace-weite Active Cycles | Upsell-Seite `WorkspaceActiveCyclesUpgrade`, ungenutzter Endpunkt `GET /api/workspaces/{ws}/active-cycles/`, `CycleListProjectGroupHeader` | `migration/features/24-paid-planung-insights-teams.md` P05-23 |
| Progress Charts / Cycle-Fortschritt „Pro“ (Burnup, Version 2) | `plotType` ohne UI, `fetchActiveCycleProgressPro` leer, `formatActiveCycle`/`formatV2Data` ohne Aufrufer, Endpunkt `…/cycle-progress/` | 24 P05-19, P05-20 |
| Auto-schedule, Auto-Rollover, Complete/Archive laufender Cycles, Cycle Updates | keine UI | 24 P05-21, P05-22, P05-25, P05-26; `migration/features/23-paid-work-management.md` WM-28, WM-29 |
| Module Overview, Auto-Assignment in Modules | keine UI | 23 WM-30, WM-31 |
| Advanced Estimates (Time, Bearbeiten, Umsortieren, Systemwechsel) | `time` mit `is_ee: true`, `isEstimateSystemEnabled("time") = false`, ungenutzte Texte `edit.*`, `switch.*`, `reorder.*`, `points/*` mit `estimateId`-Zweig | 23 WM-35 |
| Shared Views, Publish Views, View-Lock-UI | `useViewPublish`-Stub, „Live“-Badge, `is_locked` ohne Schalter | 24 P05-27, P05-28 (Lock: siehe 6) |
| Erweiterte Analytics-Tabs, Insights, Custom Reports, Zeitraumfilter, zusätzliche Achsen/Metriken, Epics | `ChartXAxisProperty`/`ChartYAxisMetric`-Werte ohne Angebot, `isEpic`, `DurationDropdown`, `selectedDuration` | 24 P05-14, P05-15, P05-16 |
| Nested Pages, Moving Pages, Page-Publish, Versionen (Server-Restore, Vergleich), Page-Exports | `isMovePageEnabled = false`, `move/`-Endpunkt ungenutzt, Banner „use nested pages“, clientseitiger Restore | `migration/features/26-paid-wissen-pages-wiki.md` P07-04, P07-06, P07-08, P07-09, P07-19 |
| Plane AI im Editor („Ask Pi“, Ton-Varianten) | Extension `ai` deaktiviert, `EditorAIMenu`/`AskPiMenu` nicht gerendert | `migration/features/28-paid-integrationen-importer-ai.md` P09-F33, P09-F34; Analyse 12 §5.8 |
| Workflows (Übergangsregeln, Sperren beim Ziehen/Anlegen) | `useWorkFlowFDragNDrop`-Stub | `migration/features/25-paid-workflows-automation-templates.md` F01–F08 |
| Custom Automations, Auto-Reminders | Texte `auto-remind.*` ohne UI | 25 F09–F17 |
| Intake Forms, Intake-Zuständigkeit, Intake per E-Mail, Duplicate Detection, erweiterte Intake-Felder | `isVisible = false` für Start date, Cycle, Modules, Estimate, Parent | 23 WM-44, WM-45, WM-46, WM-47 |
| GitHub- und Slack-Integration | tote Komponenten in `components/integration/`, nicht registrierte Seite, Modelle ohne URLs | 28 P09-F02 bis P09-F05, P09-F09 bis P09-F11 |
| Kollaborations-Cursor | Extension `collaboration-cursor` in `useEditorFlagging` deaktiviert | Analyse 12 §5.8 |

## 6. Offene Punkte

| # | Frage | Kontext |
|---|---|---|
| O1 | Sollen die funktionalen Fehler des Originals (Liste in 5.4, Zeile 1) korrigiert werden, oder gilt auch hier strikte 1:1-Treue? Empfehlung: korrigieren, Optik beibehalten. | 3.x Edge-Cases |
| O2 | Für die Bezahl-UIs aus 5.5 gibt es im Repo keine Referenzoberflächen. Gibt es Zugang zu einer Business/Enterprise-Instanz (Screenshots, Abläufe), insbesondere für Workspace-Active-Cycles, Advanced Estimates, Publish Views und Nested Pages? | 5.5 |
| O3 | Wie wird ein View gesperrt (`is_locked`)? CE wertet das Feld nur aus, bietet aber keinen Schalter; die Bezahlfunktion ist in den Feature-Dokumenten nicht eindeutig beschrieben. | 3.4.3 |
| O4 | Soll ein neu angelegtes Schätzsystem automatisch eingeschaltet werden (E1)? | 3.7.1 |
| O5 | Seitenexport als PDF: im Browser nachbauen oder serverseitig in .NET erzeugen (gleiche Optik wie `pdf/document.tsx`)? Hängt mit der Entscheidung zum Live-PDF-Export zusammen (Analyse 12 §6). | 2.17, 3.3.6 |
| O6 | Welche Chart-Bibliothek ist im Angular-Frontend zulässig (selbst gehostet, airgap-tauglich), und wie wird die Pixelgleichheit zu recharts nachgewiesen? | 5.2 |
| O7 | Sollen die externen Links (Dokumentation, Pricing, OAuth-Anbieter) im Airgap-Betrieb entfallen oder konfigurierbar sein? | 5.4 |
| O8 | Analytics: Soll der vorhandene, aber ungenutzte Zeitraumfilter aktiviert werden (zusammen mit den erweiterten Analytics-Tabs) oder bis dahin entfallen? | 3.5.5 A3 |
| O9 | Exporter: Soll der auskommentierte Rich-Filter für Exporte gebaut werden? Dann muss das Backend `rich_filters` auswerten (X1). | 3.12 |
| O10 | Webhook-Secrets und API-Tokens: Soll der CSV-Sofortdownload beibehalten werden (Sicherheitsabwägung: Klartext-Secret im Download-Ordner)? | 3.10.1, 3.11 |
| O11 | Integrationen: Sollen die alten CE-Modelle (`WorkspaceIntegration`, `GithubRepositorySync`, `SlackProjectSync`) im neuen Datenmodell erhalten bleiben oder durch das Integrationsmodell aus Dokument 28 ersetzt werden? | 2.16 |
