# 09 – Frontend: Arbeitsobjekte (Work Items) – Layouts, Ansichten, Peek, Detail, Modal, Filter, Dropdowns

> Analysebereich A09 · IST-Analyse des Originals (Plane CE, Repo-Stand dieses Workspaces) als Spezifikation für den 1:1-Nachbau in Angular (ADR-005) · Verbindliche Grundsatzentscheidungen: `migration/architecture/00-grundsatzentscheidungen.md` (ADR-000 … ADR-006).
>
> Konventionen: Fließtext deutsch; Bezeichner, Pfade, Klassen, Endpunkte und UI-Texte (en, aus `packages/i18n/src/locales/en/*.json` aufgelöst) im Original. Pfade ohne Präfix in Tabellen beziehen sich auf das in der Abschnittsüberschrift genannte Verzeichnis. Tailwind-Klassen sind wörtlich übernommen, weil ADR-005 identische Klassenstrings voraussetzt (s. `migration/analysis/08-frontend-web-architektur.md` 5.1).

## Inhaltsverzeichnis

1. Überblick & Verantwortlichkeiten
2. Vollständige Inventare (2.1 Roots/HOCs · 2.2 List · 2.3 Kanban · 2.4 Calendar · 2.5 Gantt · 2.6 Spreadsheet · 2.7 Quick-Add · 2.8 Quick-Actions · 2.9 Empty-States · 2.10 Display-Filter · 2.11 Rich-Filter · 2.12 Peek · 2.13 Detailseite · 2.14 Widgets · 2.15 Activity/Kommentare · 2.16 Modal · 2.17 Drafts · 2.18 Einzeldateien · 2.19 Dropdowns · 2.20 Read-only · 2.21 Base-Layouts · 2.22 Skeletons)
3. Verhalten/Logik/Abläufe (3.1 Gemeinsam · 3.2–3.6 Layouts · 3.7 Laden/Persistenz · 3.8 Rich-Filter · 3.9 Peek · 3.10 Detail · 3.11 Modal/Drafts · 3.12 Activity · 3.13 Archiv/Löschen · 3.14 Tastatur · 3.15 Edge-Cases)
4. Abhängigkeiten zu anderen Bereichen
5. Migrationshinweise .NET/EF Core/Angular
6. Offene Punkte

---

## 1. Überblick & Verantwortlichkeiten

### 1.1 Umfang

| Verzeichnis (`apps/web/components/…`) | Dateien (ts/tsx) | Zeilen | Inhalt |
|---|---|---|---|
| `issues/` gesamt | 322 | 31 155 | alles unten Aufgeführte |
| `issues/issue-layouts/` | 161 | 15 929 | Layout-Roots, List, Kanban, Calendar, Gantt-Wrapper, Spreadsheet, Properties, Quick-Add, Quick-Actions, Empty-States, Display-/Legacy-Filter, Utilities |
| `issues/issue-detail/` | 62 | 4 795 | Detailseite, Sidebar, Parent, Labels, Links (Modal), Reaktionen, Subscription, Activity-Feed |
| `issues/issue-detail-widgets/` | 37 | 3 340 | Sub-Work-Items, Relations, Links, Attachments (Collapsibles + Aktionen) |
| `issues/issue-modal/` | 13 | 2 127 | Create/Edit-Modal, Draft-Logik, Kontext-Provider (CE-Stubs für Typen/Vorlagen) |
| `issues/peek-overview/` | 9 | 1 344 | Peek (Side/Modal/Full-Screen) |
| `issues/workspace-draft/` | 8 | 845 | Workspace-Entwürfe |
| `issues/attachment/` | 10 | 760 | Attachment-Liste/-Kacheln |
| `issues/relations/` | 3 | 389 | Relationslisten |
| `issues/preview-card/` | 3 | 132 | Hover-Vorschaukarte |
| `issues/bulk-operations/` | 2 | 67 | CE-Upsell-Stub |
| `gantt-chart/` | 39 | 3 332 | Timeline-Engine (Chart, Sidebar, Blöcke, DnD, Resize, Ansichten) |
| `rich-filters/` | 19 | 1 453 | generische Filterzeile/-chips |
| `work-item-filters/` | 6 | 612 | Work-Item-Anbindung der Rich-Filter |
| `dropdowns/` | 12 | 1 355 | Store-gebundene Property-Selects |
| `comments/` | 9 | 934 | Kommentar-Karten, Eingabe, Reaktionen |
| `readonly/` | 9 | 463 | Read-only-Wertanzeigen |
| `base-layouts/` | 16 | 1 036 | generisches List/Kanban/Gantt-Gerüst (in CE ungenutzt) |
| `relations/` | 1 | 42 | Relationstyp-Optionen |
| `epic-modal/` | 2 | 33 | CE-Stub |

### 1.2 Verantwortlichkeiten

| Verantwortung | Kern-Komponenten | Abschnitt |
|---|---|---|
| Darstellung von Work-Item-Mengen in 5 Layouts (`list`, `kanban`, `calendar`, `gantt_chart`, `spreadsheet`) für 13 Store-Kontexte (Projekt, Cycle, Modul, Projekt-View, Workspace-View, Profil, Archiv, Drafts, Epics, Teamspace-Varianten) | `roots/*`, `issue-layout-HOC.tsx`, `list/*`, `kanban/*`, `calendar/*`, `gantt/*` + `gantt-chart/*`, `spreadsheet/*` | 2.1–2.6, 3.1–3.6 |
| Gruppierung (`group_by`, Kanban zusätzlich `sub_group_by`/Swimlanes), Sortierung (`order_by`), Anzeigeoptionen (Display-Properties, `sub_issue`, `show_empty_groups`, Calendar-Layout Monat/Woche) | `filters/header/display-filters/*`, `utils.tsx` | 2.10, 3.1, 3.7 |
| Drag-and-Drop (Gruppenwechsel, Reihenfolge, Calendar-Datum, Gantt-Verschieben/Resize/Reorder, Kanban-Löschzone) | `use-group-dragndrop`, `utils.tsx`, `gantt-chart/*` | 3.1.4, 3.3–3.5 |
| Schnellerfassung inline (Quick-Add) und Inline-Bearbeitung aller Properties | `quick-add/*`, `properties/*`, `spreadsheet/columns/*` | 2.7, 2.1, 2.6 |
| Kontextaktionen („…“-Menü und Rechtsklick) | `quick-action-dropdowns/*` | 2.8 |
| Filtern über Rich-Filter-Ausdrücke inkl. Speichern/Aktualisieren von Views | `rich-filters/*`, `work-item-filters/*` | 2.11, 3.8 |
| Einzelansicht als Peek (3 Modi) und als Detailseite inkl. Widgets, Activity, Kommentare, Reaktionen, Abos | `peek-overview/*`, `issue-detail/*`, `issue-detail-widgets/*`, `comments/*` | 2.12–2.15, 3.9–3.12 |
| Anlegen/Bearbeiten im Modal inkl. Entwurfs-Sicherung und „Create more“; Workspace-Entwürfe | `issue-modal/*`, `workspace-draft/*` | 2.16, 2.17, 3.11 |
| Archivieren/Wiederherstellen/Löschen | `archive-issue-modal.tsx`, `delete-issue-modal.tsx`, `issue-detail-quick-actions.tsx` | 2.18, 3.13 |
| Wiederverwendbare Property-Selects und Read-only-Werte | `dropdowns/*`, `readonly/*`, `@plane/blocks/property-select` | 2.19, 2.20 |
| Lade-, Leer- und Fehlerzustände | `empty-states/*`, `ui/loader/layouts/*`, Peek-/Detail-Fehler | 2.9, 2.22 |

### 1.3 Komponentenbaum (Projekt-Work-Items, vereinfacht)

```
ProjectLayoutRoot (IssuesStoreContext = PROJECT)
├─ ProjectLevelWorkItemFiltersHOC  ── Rich-Filter-Instanz (shared-state)
│  ├─ WorkItemFiltersRow (FiltersRow → FilterItem* + AddFilterButton + Clear/Save/Update)
│  └─ IssueLayoutHOC  ── Skeleton | Empty-State | LayoutErrorBoundary
│     ├─ ListLayout      → BaseListRoot → List → ListGroup* → IssueBlocksList → IssueBlockRoot (RenderIfVisible) → IssueBlock → IssueProperties
│     ├─ KanBanLayout    → BaseKanBanRoot → KanBan | KanBanSwimLanes → KanbanGroup* → KanbanIssueBlocksList → KanbanIssueBlock
│     ├─ CalendarLayout  → BaseCalendarRoot → CalendarChart → CalendarWeekHeader + CalendarWeekDays → CalendarDayTile → CalendarIssueBlocks
│     ├─ BaseGanttRoot   → GanttChartRoot → ChartViewRoot (Sidebar + Timeline) → GanttChartBlocksList
│     └─ ProjectSpreadsheetLayout → BaseSpreadsheetRoot → SpreadsheetView → SpreadsheetTable (Header + IssueRow*)
└─ IssuePeekOverview → IssueView (Header, PeekOverviewIssueDetails, IssueDetailWidgets, PeekOverviewProperties, IssueActivity)
Seitenkopf: IssuesHeader → HeaderFilters (Layout-Auswahl, Filter-Toggle, Display, Analytics) + „Add work item“ → CreateUpdateIssueModal
```

Quellen: `apps/web/components/issues/issue-layouts/roots/project-layout-root.tsx`, `apps/web/components/issues/header.tsx`, `apps/web/components/issues/filters.tsx`, `apps/web/components/issues/peek-overview/root.tsx` (Details in 2.1–2.18).

### 1.4 CE vs. Bezahl-Editionen in diesem Bereich (Kurzüberblick, Details 5.4)

Im CE-Code sind folgende Bezahlfunktionen dieses Bereichs **nur als Stub/Erweiterungspunkt** vorhanden und müssen gemäß ADR-001 als echte Funktion gebaut werden: Bulk Operations (Mehrfachauswahl + Massenbearbeitung), Workflows (Übergangsregeln beim DnD und im State-Select), Teamspaces (`team_project`-Gruppierung, TEAM-Stores), Duplizieren in anderes Projekt, Epics (Modal, Empty-State, Epic-Detail), Work-Item-Typen inkl. Custom Properties, Vorlagen (Templates) und Konvertierung, erweiterte/negierte Filteroperatoren, Timeline-Abhängigkeiten (Gantt-Verbindungen, Relationstypen `start_before`/`start_after`/`finish_before`/`finish_after`), Relationen `implements`/`implemented_by`, Kommentar-Antworten, paginierte/gescopte Selects (Workflow-gesteuerte States, Label-Scopes). Zeitbasierte Schätzungen (`EEstimateSystem.TIME`, in `packages/constants/src/estimates.ts` mit `is_ee: true` markiert) werden in diesem Bereich bereits korrekt angezeigt (`convertMinutesToHoursMinutesString`); ihre Anlage gehört zum Bereich Estimates.

---

## 2. Vollständige Inventare

### 2.1 Layout-Roots, HOCs, gemeinsame Utilities (`apps/web/components/issues/issue-layouts/`)

| Datei | Export | Zweck / Verhalten (für 1:1-Nachbau relevant) |
|---|---|---|
| `roots/project-layout-root.tsx` | `ProjectLayoutRoot` | Projekt-Arbeitsobjekte. Liest `workspaceSlug`, `projectId` aus Route; SWR-Key `PROJECT_ISSUES_${ws}_${pid}` lädt `issuesFilter.fetchFilters(ws, pid)` (`revalidateIfStale:false, revalidateOnFocus:false`). Setzt `IssuesStoreContext = EIssuesStoreType.PROJECT`. Umhüllt mit `ProjectLevelWorkItemFiltersHOC` (`enableSaveView`, `filtersToShowByLayout = ISSUE_DISPLAY_FILTERS_BY_PAGE.issues.filters`). Zeigt `WorkItemFiltersRow` oben, darunter Layout-Switch (`list`→`ListLayout`, `kanban`→`KanBanLayout`, `calendar`→`CalendarLayout`, `gantt_chart`→`BaseGanttRoot`, `spreadsheet`→`ProjectSpreadsheetLayout`). **Mutation-Loader**: bei `issues.getIssueLoader()==="mutation"` fixes 40×40-Kästchen `top-[70px] right-[20px] z-50 rounded-sm bg-layer-1 shadow-sm` mit `Spinner h-4 w-4`. Rendert `IssuePeekOverview` am Ende. Bis Filter geladen: leeres Fragment. |
| `roots/cycle-layout-root.tsx` | `CycleLayoutRoot` | Wie Projekt, Store `CYCLE`, SWR-Key `CYCLE_ISSUES_${ws}_${pid}_${cycleId}`. Berechnet `cycleStatus = cycle.status.toLowerCase() ?? "draft"`, `isCompletedCycle = status==="completed"`. Bei abgeschlossenem Cycle: Banner `TransferIssues` (Button „Transfer work items“) über der Filterzeile; `canTransferIssues = isEmpty(progress_snapshot) && (backlog_issues+unstarted_issues+started_issues) > 0`; `disabled = !isEmpty(progress_snapshot)`. Öffnet `TransferIssuesModal`. Gantt erhält `isCompletedCycle`. |
| `roots/module-layout-root.tsx` | `ModuleLayoutRoot` | Store `MODULE`, SWR-Key `MODULE_ISSUES_…_${moduleId}`; Layout-Container ist `Row variant=HUGGING` (`@plane/blocks/layout`). |
| `roots/project-view-layout-root.tsx` | `ProjectViewLayoutRoot` | Store `PROJECT_VIEW`. `initialWorkItemFilters` = displayFilters/displayProperties/kanbanFilters des Stores + `richFilters = projectView.rich_filters`. HOC mit `enableSaveView`, `saveViewOptions.label="Save as"`, `enableUpdateView`. SWR ohne Optionen (revalidiert!). **Cleanup beim Unmount**: `issuesFilter.resetFilters(ws, viewId)` (ungespeicherte Änderungen verworfen). |
| `roots/archived-issue-layout-root.tsx` | `ArchivedIssueLayoutRoot` | Store `ARCHIVED`, SWR-Key `ARCHIVED_ISSUES_${ws}_${pid}`. Nur List-Layout (`ArchivedIssueListLayout`). `filtersToShowByLayout = ISSUE_DISPLAY_FILTERS_BY_PAGE.archived_issues.filters`. Kein „Save view“. |
| `roots/all-issue-layout-root.tsx` | `AllIssueLayoutRoot` | Workspace-Ansichten (`/workspace-views/:globalViewId`), Store `GLOBAL`. Lädt Views (`WORKSPACE_GLOBAL_VIEWS_${ws}`) und Issues (`WORKSPACE_GLOBAL_VIEW_ISSUES_${ws}_${viewId}`: `clear()`, `toggleLoading(true)`, `fetchFilters`, `fetchIssues(ws, viewId, groupedIssueIds ? "mutation" : "init-loader", {canGroup:false, perPageCount:100})`). Statische Views (`STATIC_VIEW_TYPES`) brauchen keine View-Details. Query-Params werden als `routeFilters` durchgereicht. **Empty-State** wenn View nicht existiert: `EmptyStateDetailed` title „View does not exist“, description „The view you are looking for does not exist or you don't have permission to view it.“, assetKey `view`, Primär-Aktion „Go to All work items“ → `/${ws}/workspace-views/all-issues`. HOC `WorkspaceLevelWorkItemFiltersHOC` (Save as / Update view, Filter `ISSUE_DISPLAY_FILTERS_BY_PAGE.my_issues.filters`). Layout-Auswahl delegiert an `WorkspaceActiveLayout` (`apps/web/components/views/helper.tsx`, anderer Bereich). Container `h-full overflow-hidden bg-surface-1`, innen `border-b border-strong`. |
| `issue-layout-HOC.tsx` | `IssueLayoutHOC` | Gemeinsamer Wrapper aller Layouts: solange `getIssueLoader()==="init-loader"` oder Gesamtanzahl `undefined` → Layout-spezifischer Skeleton-Loader (`ListLayoutLoader`, `KanbanLayoutLoader`, `SpreadsheetLayoutLoader`, `CalendarLayoutLoader`, `GanttLayoutLoader` aus `apps/web/components/ui/loader/layouts/*`). Wenn Gesamtanzahl `0` und Layout ≠ Calendar → `IssueLayoutEmptyState`. Sonst `LayoutErrorBoundary key={layout}`. |
| `layout-icon.tsx` | `IssueLayoutIcon` | Icon-Mapping: list→`ListOutline`, kanban→`BoardOutline`, calendar→`CalendarOutline`, spreadsheet→`TableOutline`, gantt_chart→`TimelineOutline` (alle `@makeplane/propel/icons`). |
| `group-drag-overlay.tsx` | `GroupDragOverlay` | Overlay über einer Gruppe beim Drag (absolute, `bg-layer-1/85 text-13 font-medium text-tertiary`, Ausrichtung `justify-start/center/end` je nach Ziehrichtung). Sichtbar nur wenn `isDraggingOverColumn && canOverlayBeVisible`. Inhalt: bei `dropErrorMessage` → Warn-Icon `WarningCircleOutline 13px` + Text; sonst „This layout is ordered by **<Order-Label>**.“ + „Drop here to move the work item“/„…epic“. Bei Workflow-Sperre (`workflowDisabledSource`) kein Text, nur Hintergrund `bg-danger-subtle`. |
| `utils.tsx` | diverse | Siehe 3.1 (Gruppenspalten, DnD-Algorithmus, Sort-Order, Highlight, Kartenhöhe, Gantt-Block-Style, Spreadsheet-Spalten-Mapping, Identifier-Breite). |
| `properties/all-properties.tsx` | `IssueProperties` | Eigenschaftsleiste der List-/Kanban-Karten (Reihenfolge und Regeln s. 3.2, Abschnitt „Eigenschaftsleiste“). |
| `properties/labels.tsx` | `IssuePropertyLabels` | Adapter über `LabelSelect`: `fullWidth && noLabelBorder` → Variante `table-cell` (+ CSS-Klasse `clickable` für Spreadsheet-Tastaturnavigation), sonst `pill-sm`; Wrapper `h-5`/`h-full`, schluckt Click (stopPropagation+preventDefault). Viele Props als `@deprecated` markiert (nur Kompatibilität). |
| `properties/with-display-properties-HOC.tsx` | `WithDisplayPropertiesHOC` | Rendert Kinder nur, wenn `displayProperties[key]` (bei Array: **alle** Keys) true ist **und** optional `shouldRenderProperty(displayProperties)` true liefert. |
| `properties/index.ts` | Barrel | `labels`, `all-properties`. |

### 2.2 List-Layout (`apps/web/components/issues/issue-layouts/list/`)

| Datei | Export | Zweck / Verhalten |
|---|---|---|
| `base-list-root.tsx` | `BaseListRoot` | Gemeinsamer Root für Stores `PROJECT, MODULE, CYCLE, PROJECT_VIEW, PROFILE, ARCHIVED, WORKSPACE_DRAFT, TEAM, TEAM_VIEW, EPIC`. Props: `QuickActions`, `addIssuesToView?`, `canEditPropertiesBasedOnProject?`, `viewId?`, `isCompletedCycle?`, `isEpic?`. Effekt: `fetchIssues("init-loader", {canGroup:true, perPageCount: group_by ? 50 : 100}, viewId)` bei Änderung von `group_by`/`viewId`. `canEditProperties(projectId) = viewFlags.enableInlineEditing && (canEditPropertiesBasedOnProject?.(pid) ?? isEditingAllowed)`; `isEditingAllowed` = Projektrolle ADMIN oder MEMBER. `disableIssueCreation = !viewFlags.enableIssueCreation \|\| !isEditingAllowed`. Collapse-Status der Gruppen wird **in `kanbanFilters.group_by`** gespeichert (geteilt mit Kanban) → `updateFilters(projectId, KANBAN_FILTERS, {group_by: collapsedGroups})`. Hintergrund `relative size-full bg-surface-2`. |
| `default.tsx` | `List` | Berechnet Gruppen via `getGroupByColumns({groupBy, includeNone:true, isWorkspaceLevel, isEpic})`; ohne Gruppierung eine Gruppe `id="All Issues"`, Name „All work items“/„All Epics“. Auto-Scroll beim Drag (`autoScrollForElements`). Baut `entities` (groupId→issueIds) für Mehrfachauswahl (`MultipleSelectGroup`, `disabled = !useBulkOperationStatus() \|\| isEpic`). Scroll-Container `vertical-scrollbar scrollbar-lg size-full overflow-auto bg-surface-1`. Unten `IssueBulkOperationsRoot`. |
| `list-group.tsx` | `ListGroup` | Eine Gruppe: Sticky-Header (`Row`, `border-b border-subtle bg-layer-1 py-1 pr-3 hover:bg-layer-1-hover`, sticky `top-0 z-[2]` nur wenn aufgeklappt und count>0), Drop-Target (`type:"COLUMN"`), Drag-Overlay, Blockliste, Pagination („Load more ↓“ bei Gruppierung, sonst 3 Skeleton-Zeilen mit IntersectionObserver), Quick-Add unten (sticky `bottom-0 z-[1]`). Leere Gruppen werden nur bei `show_empty_groups` angezeigt. |
| `headers/group-by-card.tsx` | `HeaderGroupByCard` | Gruppen-Header: Gruppen-Checkbox (nur bei Hover sichtbar, `group-hover/list-header`), Icon (Fallback `CircleDashed 3.5`), Titel (`line-clamp-1 font-medium text-primary`), Anzahl (`pl-2 text-13 font-medium text-tertiary`), Klick auf Titelzeile = Collapse-Toggle. „+“-Button (`h-5 w-5 rounded-xs hover:bg-layer-1`, `AddOutline`): in Cycle/Modul-Kontext als Menü mit „Create work item“ / „Add an existing work item“ (→ `ExistingIssuesListModal` mit `searchParams` `{module: id}` bzw. `{cycle: true}`), sonst direkt Create-Modal mit `data = group.payload`. Bei `isEpic` → `CreateUpdateEpicModal`. Toasts: „Work items added to the cycle successfully.“ / „Selected work items could not be added to the cycle. Please try again.“ (Text sagt auch bei Modulen „cycle“). |
| `blocks-list.tsx` | `IssueBlocksList` | Rendert `IssueBlockRoot` je Issue-ID (`nestingLevel 0`, `spacingLeft 0`, `isLastChild`). |
| `block-root.tsx` | `IssueBlockRoot` | Drop-Target pro Zeile (`type:"ISSUE"`, `attachInstruction` mit Modus `last-in-group` für letztes Element), `DropIndicator` oben (DRAG_OVER) bzw. unten (DRAG_BELOW beim letzten Kind). Virtualisierung via `RenderIfVisible` (`verticalOffset=100` %, Placeholder `ListLoaderItemRow shouldAnimate={false} renderForPlaceHolder defaultPropertyCount={4}`, `defaultValue = shouldRenderByDefault \|\| isIssueNew` (<30 s alt), `shouldRecordHeights = isMobile`). Rekursive Sub-Issue-Darstellung bei Expand (nicht für Epics), Einrückung `spacingLeft + 12px` pro Ebene. Outside-Click entfernt `highlight`-Klasse. Element-ID `issue_${issueId}_${groupId}_${subGroupId}`. |
| `block.tsx` | `IssueBlock` | Die eigentliche Zeile (`ControlLink` → Work-Item-Link; Klick ohne Modifier öffnet Peek). Details s. 3.2. |
| `list-view-types.d.ts` | `IQuickActionProps`, `TRenderQuickActions` | Props der Quick-Action-Menüs: `parentRef, issue, handleDelete, handleUpdate?, handleRemoveFromView?, handleArchive?, handleRestore?, handleMoveToIssues?, customActionButton?, portalElement?, readOnly?, placements?`. |
| `roots/project-root.tsx` | `ListLayout` | `QuickActions = ProjectIssueQuickActions`, Edit-Recht pro Projekt (ADMIN/MEMBER). |
| `roots/cycle-root.tsx` | `CycleListLayout` | `CycleIssueQuickActions`; `isCompletedCycle` aus `currentProjectCompletedCycleIds`; Edit nur wenn nicht abgeschlossen und ADMIN/MEMBER; `addIssuesToView = issues.addIssueToCycle(ws,pid,cycleId,ids)`; `viewId = cycleId`. |
| `roots/module-root.tsx` | `ModuleListLayout` | `ModuleIssueQuickActions`; `addIssuesToView = issues.addIssuesToModule(...)`; `viewId = moduleId`. |
| `roots/project-view-root.tsx` | `ProjectViewListLayout` | `ProjectIssueQuickActions`, `viewId`. |
| `roots/profile-issues-root.tsx` | `ProfileIssuesListLayout` | `ProjectIssueQuickActions`; Edit-Recht pro Projekt; `viewId = profileViewId`. |
| `roots/archived-issue-root.tsx` | `ArchivedIssueListLayout` | `ArchivedIssueQuickActions`; `canEditPropertiesBasedOnProject = () => false` (alles read-only). |

### 2.3 Kanban-/Board-Layout (`apps/web/components/issues/issue-layouts/kanban/`)

| Datei | Export | Zweck / Verhalten |
|---|---|---|
| `base-kanban-root.tsx` | `BaseKanBanRoot` | Root für Stores `PROJECT, MODULE, CYCLE, PROJECT_VIEW, PROFILE, TEAM, TEAM_VIEW, EPIC`. Lädt `fetchIssues("init-loader", {canGroup:true, perPageCount: sub_group_by ? 10 : 30}, viewId)` bei Änderung von `group_by`/`sub_group_by`/`viewId`. Nachladen pro Gruppe/Subgruppe nur wenn Loader ≠ `"pagination"`. Wählt `KanBanSwimLanes` (mit `sub_group_by`) oder `KanBan`. Scroll-Container `horizontal-scrollbar scrollbar-lg flex h-full w-full bg-surface-2` + (`vertical-scrollbar overflow-y-auto` bei Swimlanes, sonst `overflow-x-auto overflow-y-hidden`), innen `w-max min-w-full`. Auto-Scroll beim Drag. `showEmptyGroup` Default **true** (List: false). `disableIssueCreation = !enableIssueCreation \|\| !isEditingAllowed \|\| isCompletedCycle`. Enthält `DeleteIssueModal` + `KanbanDeleteDropZone` (Drop → Lösch-Bestätigung → `removeIssue`). Collapse: `handleCollapsedGroups("group_by"\|"sub_group_by", id)` → `kanbanFilters`. |
| `default.tsx` | `KanBan` | Spaltenreihe (`ContentWrapper` `flex-row gap-4 !pt-2 !pb-0`). Je Spalte: Breite `w-[350px]` (eingeklappt: schmal), Sticky-Header (`sticky top-0 z-[2] bg-surface-2 py-1`) **nur wenn `sub_group_by === null`**; Inhalt `RenderIfVisible` (`verticalOffset 100`, `horizontalOffset 100`, `min-h-[120px]`, Platzhalter `KanbanColumnLoader ignoreHeader cardHeight=approx cardsInColumn=min(n,3)`, sofort sichtbar für die ersten 5 Spalten in den ersten 2 Subgruppen, `useIdleTime`). Sichtbarkeit: `!showEmptyGroup` blendet Spalten mit 0 aus; eingeklappte Spalten zeigen keine Karten. `isDragDisabled = !getCanUserDragDrop(group_by, sub_group_by)`. |
| `kanban-group.tsx` | `KanbanGroup` | Spalte/Zelle als Drop-Target (`{groupId, subGroupId, columnId: "${groupId}__${subGroupId}", type:"COLUMN"}`) + Auto-Scroll. DOM-ID `${groupId}__${sub_group_id}`. Beim Drag-Over `rounded-sm bg-layer-1`. Overlay-Ausrichtung `justify-center` (ohne Subgruppe) bzw. `justify-start`. Pagination: in Subgruppen „Load more ↓“ (sticky bottom, `p-3 text-13 font-medium text-accent-primary hover:underline`), ohne Subgruppe 3 Karten-Skeletons + IntersectionObserver (`rootMargin "0% 100% 100% 100%"`). Quick-Add sticky unten (`bg-surface-2 py-0.5`) mit Vorbelegung aus Gruppe **und** Subgruppe. `canDragIssuesInCurrentGrouping = group_by ∈ DRAG_ALLOWED_GROUPS && (!sub_group_by \|\| sub_group_by ∈ DRAG_ALLOWED_GROUPS)`. |
| `blocks-list.tsx` | `KanbanIssueBlocksList` | Karten; `draggableId = ${issueId}__${groupId}__${subGroupId}`; `shouldRenderByDefault = index <= 10`. |
| `block.tsx` | `KanbanIssueBlock`, intern `KanbanIssueDetailsBlock` | Karte: `ControlLink` (`rounded-lg border border-subtle bg-layer-2 p-3 text-13 shadow-raised-100 hover:border-strong hover:shadow-raised-200`; gepeekt `border-accent-strong`; beim Ziehen `z-[100] bg-layer-1`), außen `mb-2`. Inhalt via `RenderIfVisible` (`defaultHeight 100px`, `horizontalOffset 100`, `verticalOffset 200`): Zeile 1 `IssueIdentifier` + rechts oben Quick-Action-Button (`MoreHorizontalOutline 3.5`, nur bei Hover `group-hover/kanban-block`, auf Mobil immer, aktiv `bg-layer-1 text-primary`); Zeile 2 Titel (`line-clamp-1 text-body-sm-medium text-primary`, Tooltip voller Name); Zeile 3 `IssueProperties` (`flex flex-wrap gap-2 pt-1.5 text-tertiary`, activeLayout „Kanban“). Karte ist Draggable **und** Drop-Target (`DropIndicator` über der Karte bei Hover). Klick → `useIssuePeekOverviewRedirection` (Mobil: Navigation, Desktop: Peek). |
| `kanban-delete-drop-zone.tsx` | `KanbanDeleteDropZone` | Fixe Zone oben mittig (`fixed left-1/2 -translate-x-1/2 top-3 w-72`), nur während Drag sichtbar (`opacity-100`, `z-40`), Text „Drop here to delete the work item.“ (`rounded-sm border-2 border-danger-strong/20 bg-surface-1 px-3 py-5 text-11 font-medium italic text-danger-primary`; Hover: `bg-danger-primary blur-2xl`, `transition duration-300`). Drop-Target `{columnId:"issue-trash-box", groupId:"issue-trash-box", type:"DELETE"}`. |
| `headers/group-by-card.tsx` | `HeaderGroupByCard` | Spalten-Header: Icon (Fallback `Circle 14`), Titel, Anzahl, Collapse-Button (`ArrowCollapseOutline`; eingeklappt `FullScreenOutline`) nur ohne Subgruppierung, „+“ (`AddOutline`, in Cycle/Modul als Menü „Create work item“/„Add an existing work item“, `align end`). Eingeklappt: vertikale Darstellung `w-[44px] flex-col`, Titel `vertical-lr max-h-[400px]`. |
| `headers/sub-group-by-card.tsx` | `HeaderSubGroupByCard` | Swimlane-Header: Chevron (`ChevronUpOutline` offen / `ChevronDownOutline` zu), Icon, Titel (`text-13 text-primary`), Anzahl; ganze Zeile klickbar → toggelt `sub_group_by`-Collapse. |
| `swimlanes.tsx` | `KanBanSwimLanes`, intern `SubGroupSwimlaneHeader`, `SubGroupSwimlane` | Sticky Spaltenkopfzeile (`sticky top-0 z-[4] h-[50px] bg-surface-2`, je Spalte `w-[350px]`, Header ohne Collapse-Button); darunter je Subgruppe sticky Zeilenheader (`sticky top-[50px] z-[3] border-y-[0.5px] border-subtle bg-layer-1 py-1`, innen `Row sticky left-0`) und eine `KanBan`-Zeile mit `sub_group_id`. Subgruppen-Anzahl kumulativ (`getGroupIssueCount(undefined, subId, true)`). Leere Spalten/Zeilen nur bei `showEmptyGroup`. |
| `roots/project-root.tsx` | `KanBanLayout` | `ProjectIssueQuickActions`, Edit-Recht pro Projekt. |
| `roots/cycle-root.tsx` | `CycleKanBanLayout` | wie List-Cycle (abgeschlossen = read-only, `addIssueToCycle`). |
| `roots/module-root.tsx` | `ModuleKanBanLayout` | `addIssuesToModule`. |
| `roots/project-view-root.tsx` | `ProjectViewKanBanLayout` | `viewId`. |
| `roots/profile-issues-root.tsx` | `ProfileIssuesKanBanLayout` | Edit-Recht pro Projekt, `viewId = profileViewId`. |

### 2.4 Calendar-Layout (`apps/web/components/issues/issue-layouts/calendar/`)

| Datei | Export | Zweck / Verhalten |
|---|---|---|
| `base-calendar-root.tsx` | `BaseCalendarRoot` | Stores `PROJECT, MODULE, CYCLE, PROJECT_VIEW, TEAM, TEAM_VIEW, EPIC` (bei `isEpic` immer `EPIC`). Liest `displayFilters.calendar.layout` (Default `"month"`), Zeitraum aus `CalendarStore.getStartAndEndDate(layout)`; lädt `fetchIssues("init-loader", {canGroup:true, perPageCount: month ? 4 : 30, before: endDate, after: startDate, groupedBy: "target_date"}, viewId)` → Gruppen = Datum `YYYY-MM-DD`. Drag-Drop setzt `target_date` (s. 3.4). Container `h-full w-full overflow-hidden bg-surface-1 pt-4`. `readOnly = isCompletedCycle`. Quick-Actions erhalten `placements`. |
| `calendar.tsx` | `CalendarChart` | Header + `IssueLayoutHOC(CALENDAR)` (zeigt **keinen** Empty-State, nur Loader). Scroll-Container (`flex w-full flex-col overflow-y-auto md:h-full`, ab >768 px `vertical-scrollbar scrollbar-lg`), sticky `CalendarWeekHeader`, Monatsansicht = Wochenzeilen (`grid grid-cols-1 divide-y-[0.5px] divide-subtle-1`), Wochenansicht = eine `CalendarWeekDays`. **Mobilansicht** (`md:hidden`): Überschrift `"<Tag> <Monat>, <Jahr>"` (`p-4 text-18 font-semibold`) + Liste der Issues des ausgewählten Tages (`CalendarIssueBlocks isDragDisabled isMobileView`) – im Original **doppelt** gerendert (innerhalb und außerhalb des HOC). Liest `viewFlags` fest aus dem **PROJECT**-Store (nicht aus dem aktuellen Store). Ohne `calendarPayload` → zentrierter `Spinner`. |
| `header.tsx` | `CalendarHeader` | `Row mb-4 justify-between`: links „‹“ / „›“ (`ChevronLeft/RightOutline 16`) + `CalendarMonthsDropdown`; rechts Button „Today“ (`rounded-sm bg-layer-transparent px-2.5 py-1 text-11 font-medium text-secondary hover:bg-layer-transparent-hover hover:text-primary`) + `CalendarOptionsDropdown`. Vor/Zurück: Monat ±1 (1. des Monats) bzw. Woche ±7 Tage. Today: `activeMonthDate = 1. des aktuellen Monats`, `activeWeekDate = heute`, `selectedDate = heute`. |
| `dropdowns/months-dropdown.tsx` | `CalendarMonthsDropdown` | Trigger-Text `text-18 font-semibold`: Monatsansicht „<Monat> <Jahr>“; Wochenansicht „<Monat> <Jahr>“ (gleicher Monat), „<Mon> - <Mon> <Jahr>“ (Monatswechsel) bzw. „<Mon> <Jahr> - <Mon> <Jahr>“ (Jahreswechsel), Fallback „Week view“. In Wochenansicht **disabled**. Popover (`variant rich`, `w-56`): Jahr mit ‹ › (`text-11`), 4-spaltiges Monatsraster (Kurznamen, `rounded-sm py-0.5 text-11 hover:bg-layer-1`). |
| `dropdowns/options-dropdown.tsx` | `CalendarOptionsDropdown` | Menü „Options“ (Desktop: `bg-layer-1 px-2.5 py-1 text-11` mit `ChevronUpOutline` (zu: `rotate-180`); Mobil: `MoreVerticalOutline`). Radio-Gruppe `CALENDAR_LAYOUTS` („Month layout“, „Week layout“) + Separator + Checkbox „Show weekends“ (`common.actions.show_weekends`). Schreibt `display_filters.calendar.{layout\|show_weekends}` über `updateFilters(projectId, DISPLAY_FILTERS, …)`; Layoutwechsel ruft `updateCalendarPayload(activeMonthDate\|activeWeekDate)`. Auf Mobil schließt das Menü nach Auswahl. |
| `week-header.tsx` | `CalendarWeekHeader` | Sticky Wochentagskopf (`grid-cols-7` bzw. `grid-cols-5` ohne Wochenende, `h-11 bg-layer-1 px-4 md:justify-end`, Kurzname). Reihenfolge nach `user.profile.start_of_the_week`. Während `isLoading` animierter Balken (`h-[1.5px] w-3/4 animate-[bar-loader_2s_linear_infinite] bg-accent-primary`). |
| `week-days.tsx` | `CalendarWeekDays` | Eine Woche als Grid (`md:divide-x-[0.5px] divide-subtle-1`, `h-full` in Wochenansicht); blendet Sa/So ohne `show_weekends` aus; sortiert nach Wochenstart. |
| `day-tile.tsx` | `CalendarDayTile` | Tageszelle = Drop-Target `{date}`. Desktop-Kopf (`text-11 px-2 py-1.5 text-right`): am 1. des Monats Kurzmonat vorangestellt; heute = Kreis `h-5 w-5 rounded-full bg-accent-primary text-on-color`; Monatsansicht: Tage außerhalb des Monats `text-tertiary`. Wochenende `bg-layer-1`. Inhalt `min-h-[5rem]` (Monat), beim Drag-Over `bg-layer-transparent-hover opacity-70`. Mobil: Button mit Tageszahl (`size-6 rounded-full`; ausgewählt `bg-accent-primary text-on-color`, heute `bg-accent-primary/10 text-accent-primary`). |
| `issue-blocks.tsx` | `CalendarIssueBlocks` | Liste je Tag (`p-1 px-2`), Paginations-Skeleton (`h-10 md:h-8 animate-pulse rounded-sm bg-layer-1`), Quick-Add (mit `target_date` = Tag) wenn erlaubt und nicht read-only, „Load more“-Button (`text-11 font-medium text-accent-primary hover:bg-layer-1`). |
| `issue-block-root.tsx` | `CalendarIssueBlockRoot` | Draggable (`{id, date: target_date}`), `canDrag = !isDragDisabled && canEditProperties(project)`. |
| `issue-block.tsx` | `CalendarIssueBlock` | Eintrag (`h-10 md:h-8 px-4 md:px-1 rounded-sm`; `bg-surface-1 hover:bg-surface-2`; Drag: `border-accent-strong bg-surface-2 shadow-raised-200`; gepeekt: `border-accent-strong`): State-Farbstreifen (`w-0.5 h-full rounded-sm`), `IssueIdentifier` (nach Display-Properties `key`/`issue_type`), Titel (`text-13 font-medium md:text-11 md:font-regular truncate`), Quick-Action „…“ (Hover). **Hover-Preview**: `Popover openOnHover delay=100` → `WorkItemPreviewCard` (`side bottom, align start, sideOffset 8`). Menü-Placement: `bottom-end`, außer Button liegt <220 px über Fensterunterkante → `top-end`. Auf Mobil ist der Link disabled. |
| `quick-add-issue-actions.tsx` | `CalendarQuickAddIssueActions` | Eigener Quick-Add-Trigger (nur bei Hover über Tageszelle sichtbar, `md:opacity-0 md:group-hover:opacity-100`): Menü mit „Add work item“/„Add Epic“ und (nicht Epic) „Add existing work item“. Existing → `ExistingIssuesListModal` mit `searchParams` `{module, target_date:"none"}` / `{cycle:true, target_date:"none"}` / `{target_date:"none"}`; blendet Issues aus, deren `start_date` nach dem Ziel-Tag liegt. Übernahme: für jedes Issue `updateIssue(…, {target_date})`, danach `addIssuesToView(ids)`; `setPromiseToast` „Adding work item“ → „Work items added successfully“. Nur mit Route-`projectId`. |
| `utils.ts` | `handleDragDrop` | Kein Update bei gleichem Datum; sonst `updateIssue(projectId, id, {id, target_date: destinationDate})`. |
| `roots/project-root.tsx` | `CalendarLayout` | Edit-Recht pro Projekt. |
| `roots/cycle-root.tsx` | `CycleCalendarLayout` | `addIssueToCycle`, `isCompletedCycle`. |
| `roots/module-root.tsx` | `ModuleCalendarLayout` | `addIssuesToModule`. |
| `roots/project-view-root.tsx` | `ProjectViewCalendarLayout` | `viewId`. |
| `dropdowns/index.ts` | Barrel | – |

### 2.5 Gantt/Timeline (`apps/web/components/issues/issue-layouts/gantt/` + `apps/web/components/gantt-chart/`)

**Issue-spezifische Wrapper**

| Datei | Export | Zweck / Verhalten |
|---|---|---|
| `issue-layouts/gantt/base-gantt-root.tsx` | `BaseGanttRoot` | Stores `PROJECT, MODULE, CYCLE, PROJECT_VIEW, EPIC`. Lädt `fetchIssues("init-loader", {canGroup:false, perPageCount:100}, viewId)`; `initGantt()` beim Mount. Blöcke = `groupedIssueIds["All Issues"]`. `isAllowed` = ADMIN/MEMBER (Projekt). Konfiguration für `GanttChartRoot`: `border=false`, `title`/`loaderTitle` = „Work items“/„Epics“ (`issue.label`/`epic.label` count 2), `enableBlockLeftResize/RightResize/Move/AddBlock = isAllowed`, `enableReorder = order_by==="sort_order" && isAllowed`, `enableSelection = useBulkOperationStatus() && isAllowed` (CE: false), `showAllBlocks`, `enableDependency` (CE ohne Wirkung). Quick-Add (nur `enableIssueCreation && isAllowed && !isCompletedCycle`) mit Vorbelegung `start_date = heute`, `target_date = morgen`, Container `sticky bottom-0 z-[1]`. Block-Update: `sort_order.newSortOrder` → `sort_order`; Datumsänderungen → `issues.updateIssueDates(ws, updates, projectId)`; Fehler-Toast „Error while updating work item dates, Please try again Later“. |
| `issue-layouts/gantt/blocks.tsx` | `IssueGanttBlock` | Balken: Hintergrund = State-Farbe (`getBlockViewDetails` inkl. Masken-Gradient bei Halbblöcken), Overlay `bg-surface-1/50`, Titel sticky bei `left: 360px` (`px-2.5 py-1 text-13 text-primary truncate`), Klick → Peek/Navigation. Hover (100 ms) → `WorkItemPreviewCard`. |
| ebd. | `IssueGanttSidebarBlock` | Sidebar-Zeile: `ControlLink` (Identifier + Name mit Tooltip, `text-13 font-medium truncate`), Klick → Peek (stopPropagation). |
| `issue-layouts/gantt/index.ts` | Barrel | – |

**Generische Gantt-Engine (`apps/web/components/gantt-chart/`)**

| Datei | Export | Zweck / Verhalten |
|---|---|---|
| `constants.ts` | `BLOCK_HEIGHT=44`, `HEADER_HEIGHT=48`, `GANTT_BREADCRUMBS_HEIGHT=40`, `SIDEBAR_WIDTH=360`, `DEFAULT_BLOCK_WIDTH=60`, `GANTT_SELECT_GROUP="gantt-issues"` | Maße in px. |
| `root.tsx` | `GanttChartRoot` | Schreibt `blockIds` in Timeline-Store; reicht alle Flags an `ChartViewRoot`. Defaults: `border=true`, `loaderTitle="blocks"`, alle `enable*=false`, `showToday=true`. |
| `contexts/index.tsx` | `TimeLineTypeContext`, `useTimeLineType` | Wählt Timeline-Store (`ISSUE`, `MODULE`, `PROJECT`, `GROUPED`) via `apps/web/hooks/use-timeline-chart.ts`. |
| `chart/root.tsx` | `ChartViewRoot` | Verwaltet sichtbaren Zeitraum: `updateCurrentViewRenderPayload(side, view, targetDate?)` generiert Render-Daten über `weekView/monthView/quarterView`, verbindet links/rechts (`mergeRenderPayloads`), korrigiert Scroll-Position (`#gantt-container`), scrollt initial auf „heute“ (zentriert, Formel `|Tage| * dayWidth − (clientWidth/2 − dayWidth) + 360/2`). **Vollbild**: Toggle rendert per `createPortal` in `#full-screen-portal` (`inset-0 z-[25]`). Container `relative flex h-full flex-col rounded-xs bg-surface-1 select-none shadow`, optional `border-[0.5px] border-subtle`. |
| `chart/header.tsx` | `GanttChartHeader` | Kopfzeile (Höhe 40 px, `bg-surface-1 py-2`): rechtsbündig „<n> <loaderTitle>“ (`text-11 font-medium text-tertiary`, sonst „Loading“), Ansichts-Buttons aus `VIEWS_LIST` („Week“, „Month“, „Quarter“; aktiv `bg-layer-transparent-selected`, `aria-pressed`), „Today“ (wenn `showToday`), Vollbild-Button (`FullScreenOutline` / `ArrowCollapseOutline`, `aria-label` „Full screen“). |
| `chart/main-content.tsx` | `GanttChartMainContent` | Scroll-Container `#gantt-container` (`vertical-scrollbar horizontal-scrollbar scrollbar-lg overflow-auto border-t-[0.5px] border-subtle`) mit Sidebar (sticky links) + Chart (`ActiveChartView` + Zeilen + Blöcke, `translateY(48px)`). **Endlos-Scroll horizontal**: bei Restbreite < Viewport → rechts/links nachgenerieren. `handleScrollToBlock`: erweitert ggf. Zeitraum bis Blockdatum und scrollt auf `marginLeft − 4 (− 60 bei nur Zieldatum)`. Auto-Scroll vertikal nur für Sidebar-Reorder (`dragInstanceId === "GANTT_REORDER"`). `MultipleSelectGroup` (disabled ohne Bulk-Ops oder bei Epics). Unter dem Container `quickAdd` und `IssueBulkOperationsRoot`. |
| `chart/timeline-drag-helper.tsx` | `TimelineDragHelper` | `useAutoScroller(ganttContainerRef, isDragging, 360, 48)` – Auto-Scroll am Rand während Resize/Move. |
| `chart/views/week.tsx` | `WeekChartView` | Pro Woche: Kopf (Titel „<Mon> <Jahr>“ bzw. „<Mon> <Jahr> - <Mon> <Jahr>“ sticky bei 360 px, rechts „Week <n>“), Tageszeile (Abkürzung + Datum; heute `bg-accent-primary px-1 text-on-color` und Spalte `bg-accent-primary/20`), Spalten; Sa/So-Spalten `bg-surface-2 outline-strong`. |
| `chart/views/month.tsx` | `MonthChartView` | Monatszeile (Titel „<monat> <Jahr>“ capitalize, aktueller Monat Badge „Current“ `bg-accent-primary px-1 text-9 text-on-color`), Wochenzeile („<Start>-<Ende>“ + „w<n>“, aktuelle Woche hervorgehoben), Wochenspalten. |
| `chart/views/quarter.tsx` | `QuarterChartView` | Quartalskopf („Jan - Mar <Jahr>“ + „Q1“, Badge „Current“), Monatszeile (Kurzname, aktueller Monat `rounded-lg bg-accent-primary px-2`), Monatsspalten. |
| `views/week-view.ts` | `weekView`, `getWeeksBetweenTwoDates`, `IWeekBlock`, `IDayBlock` | Zeitraum: initial ±`approxFilterRange` (Woche: 4) **Monate** um heute; Wochen beginnen am Benutzer-Wochenstart; `weekNumber` nach `getWeekNumberByDate`. |
| `views/month-view.ts` | `monthView`, `getMonthsBetweenTwoDates`, `IMonthBlock`, `IMonthView` | ±6 Monate; Payload = Monate + Wochen (ohne Tage); Merge per `uniqBy`. |
| `views/quarter-view.ts` | `quarterView`, `groupMonthsToQuarters`, `IQuarterMonthBlock` | ±24 Monate initial, Nachladen ±12; Gruppierung in Quartale. |
| `views/helpers.ts` | `generateDate`, `getNumberOfDaysInMonth`, `getWeekNumberByDate`, `getNumberOfDaysBetweenTwoDates`, `getDateFromPositionOnGantt`, `getItemPositionWidth`, `getPositionFromDate` | Positionsmathematik (s. 3.5). |
| `views/index.ts` | Barrel | – |
| `data/index.ts` | `VIEWS_LIST`, `weeks`, `months`, `quarters`, `generateWeeks`, `datePreview`, `timePreview`, `charCapitalize`, `bindZero`, `currentViewDataWithView` | `VIEWS_LIST`: week (`dayWidth 60`, Range 4), month (`dayWidth 20`, Range 6), quarter (`dayWidth 5`, Range 24); i18n `common.week/month/quarter`. |
| `blocks/block-row-list.tsx` | `GanttChartRowList` | Zeilenhintergründe (virtualisiert, Platzhalter 44 px). |
| `blocks/block-row.tsx` | `BlockRow` | Zeile 44 px; Hover setzt `activeBlockId` (Sidebar und Chart synchron hervorgehoben `bg-layer-transparent-hover`); gepeekt `border-accent-strong rounded-l-sm`; ausgewählt `bg-accent-primary/5`; fokussiert `border-strong-1`. Ist der Balken außerhalb des sichtbaren Bereichs (IntersectionObserver, `rootMargin 0 0 0 -360px`) → Sprung-Button (`h-8 w-8 rounded-sm border border-strong bg-layer-1`, `ArrowNarrowRightOutline`, bei links verborgen `rotate-180`, sticky bei 364 px) → `handleScrollToBlock`. Ohne Datum + `enableAddBlock` → `ChartAddBlock`. |
| `blocks/block.tsx` | `GanttChartBlock` | Positionierter Container (`marginLeft`, `width`, Höhe 44, ID `gantt-block-${id}`), `transition-all` beim Bewegen nur in Wochenansicht; virtualisiert (Platzhalter `h-8 rounded-sm bg-layer-1`); Move nur bei vollständigem Block (Start **und** Ziel). |
| `blocks/blocks-list.tsx` | `GanttChartBlocksList` | Rendert alle Blöcke; Flags können Funktionen `(blockId)=>boolean` sein. |
| `helpers/draggable.tsx` | `ChartDraggable` | Block mit linkem/rechtem Resize-Handle und Move-Bereich (`h-8 rounded-sm`, `onMouseDown` → move). |
| `helpers/blockResizables/left-resizable.tsx` | `LeftResizable` | Griff `w-3 cursor-col-resize` links; sichtbarer Balken `h-7 w-1 bg-surface-1` bei `group-hover`; Datums-Badge links (`-left-36 w-32`, `rounded-sm bg-accent-subtle px-2 py-1 text-11 text-tertiary`) bei Hover/Resize/Move. |
| `helpers/blockResizables/right-resizable.tsx` | `RightResizable` | Spiegelbildlich rechts; Datum = Position Ende −1 Tag. |
| `helpers/blockResizables/use-gantt-resizable.ts` | `useGanttResizable` | Maus-basiertes Resize/Move (s. 3.5). |
| `helpers/add-block.tsx` | `ChartAddBlock` | Für Zeilen ohne Datum: „+“-Button folgt der Maus (`h-8 w-8 rounded-sm border border-strong bg-layer-1`), Tooltip mit Datum unter dem Cursor; Klick setzt `start_date` = Spalte, `target_date` = +1 Tag (Quartal +7). |
| `helpers/index.ts` | Barrel | – |
| `sidebar/root.tsx` | `GanttChartSidebar` | Sticky Sidebar `#gantt-sidebar` (360 px, `border-r-[0.5px] border-subtle-1 bg-surface-1`), Kopf (48 px, `items-end pb-2 pr-4 text-13 font-medium text-tertiary`): Gruppen-Checkbox (nur `enableSelection`), Titel, rechts „Duration“ (`common.duration`). |
| `sidebar/gantt-dnd-HOC.tsx` | `GanttDnDHOC` | Reorder-DnD (`dragInstanceId:"GANTT_REORDER"`), Drop-Indikator oben/unten; Versuch ohne Erlaubnis → Toast warning „Warning!“ „Drag and drop is only enabled when sorted by manual“; nach Drop Highlight mit Linie. |
| `sidebar/utils.ts` | `handleOrderChange` | Sort-Order: oben `first − 1000`, unten `last + 1000`, sonst Mittelwert; ruft `blockUpdateHandler(data, {sort_order:{destinationIndex,newSortOrder,sourceIndex}})`. |
| `sidebar/issues/sidebar.tsx` | `IssueGanttSidebar` | Virtualisierte Liste (`GanttLayoutListItemLoader` als Platzhalter), Endlos-Laden per IntersectionObserver (Skeleton `h-10 md:h-8 animate-pulse`), initial 4 `Loader.Item 34px`. |
| `sidebar/issues/block.tsx` | `IssuesSidebarBlock` | Zeile 44 px mit Checkbox (Hover), `IssueGanttSidebarBlock`, rechts Dauer „<n> day(s)“ (`text-13 text-secondary`) nur bei Start+Ziel. |
| `sidebar/modules/sidebar.tsx` | `ModuleGanttSidebar` | Gleiche Logik für Modul-Timeline (Bereich Module). |
| `sidebar/modules/block.tsx` | `ModulesSidebarBlock` | Zeile mit `ModuleGanttSidebarBlock` (aus `@/components/modules`) + Dauer. |
| `sidebar/index.ts`, `sidebar/issues/index.ts`, `sidebar/modules/index.ts`, `chart/index.ts`, `chart/views/index.ts`, `index.ts` | Barrels | – |

### 2.6 Spreadsheet/Table-Layout (`apps/web/components/issues/issue-layouts/spreadsheet/`)

| Datei | Export | Zweck / Verhalten |
|---|---|---|
| `base-spreadsheet-root.tsx` | `BaseSpreadsheetRoot` | Stores `PROJECT, MODULE, CYCLE, PROJECT_VIEW, TEAM, TEAM_VIEW, EPIC`. `fetchIssues("init-loader", {canGroup:false, perPageCount:100}, viewId)`. Keine Gruppierung. Sortierung über Spaltenkopf → `updateFilters(projectId, DISPLAY_FILTERS, {order_by})`. `disableIssueCreation = !enableIssueCreation \|\| !isEditingAllowed \|\| isCompletedCycle`. Quick-Actions erhalten `portalElement`. |
| `roots/workspace-root.tsx` | `WorkspaceSpreadsheetRoot` | Workspace-Ansichten (`GLOBAL`): Edit-Recht pro Issue-Projekt (ADMIN/MEMBER), `AllIssueQuickActions` (Delete, Update, Archive). Display-Filter-Update `updateFilters(ws, undefined, DISPLAY_FILTERS, …, globalViewId)`. Loader: `SpreadsheetLayoutLoader` solange `isLoading && issuesLoading && init-loader` oder keine Daten. `isWorkspaceLevel` → alle Spalten (auch Cycle/Module unabhängig von Projekt-Features). |
| `roots/project-root.tsx` | `ProjectSpreadsheetLayout` | Edit-Recht pro Projekt. |
| `roots/cycle-root.tsx` | `CycleSpreadsheetLayout` | Read-only bei abgeschlossenem Cycle. |
| `roots/module-root.tsx` | `ModuleSpreadsheetLayout` | – |
| `roots/project-view-root.tsx` | `ProjectViewSpreadsheetLayout` | – |
| `spreadsheet-view.tsx` | `SpreadsheetView` | Rahmen (`relative flex h-full w-full flex-col overflow-x-hidden bg-layer-1 whitespace-nowrap text-secondary`), Portal-Div `.spreadsheet-menu-portal` für Menüs, `MultipleSelectGroup` (Gruppe `SPREADSHEET_SELECT_GROUP="spreadsheet-issues"`), Scroll-Container (`vertical-scrollbar horizontal-scrollbar scrollbar-lg`), Quick-Add unten (`border-t border-subtle`, sticky `bottom-0 left-0 z-5`), `IssueBulkOperationsRoot`. Spaltenliste = `SPREADSHEET_PROPERTY_LIST` (state, priority, assignee, labels, modules, cycle, start_date, due_date, estimate, created_on, updated_on, link, attachment_count, sub_issue_count); auf Projektebene ohne `cycle` (wenn `cycle_view` aus) und `modules` (wenn `module_view` aus). `isEstimateEnabled = currentProject.estimate !== null`. Ohne Issues → leeres Fragment. |
| `spreadsheet-table.tsx` | `SpreadsheetTable` | `<table class="w-full overflow-y-auto bg-surface-1" onKeyDown=Tastaturnavigation>`; `thead` + `tbody` + `tfoot` (3 `SpreadsheetIssueRowLoader` als IntersectionObserver-Ziel bei weiteren Seiten). Beim horizontalen Scrollen erhält die erste Spalte per DOM-Manipulation einen Schatten (`8px 22px 22px 10px rgba(0,0,0,0.05)`, Header `8px -22px …`). Spaltenanzahl für Loader = aktive Display-Properties ohne `key` (und ohne `estimate`, wenn deaktiviert). |
| `spreadsheet-header.tsx` | `SpreadsheetHeader` | `thead sticky top-0 left-0 z-[12] border-b-[0.5px] border-subtle`. Erste Spalte (`h-11 min-w-60 md:sticky left-0 z-[15] bg-layer-1 border-r-[0.5px] text-13 font-medium`, Inhalt `px-page-x`, innen `min-w-80`): Gruppen-Checkbox (Hover) + „Work items“/„Epics“. Danach `SpreadsheetHeaderColumn` je Property. |
| `spreadsheet-header-column.tsx` | `SpreadsheetHeaderColumn` | `th` (`h-11 min-w-36 border border-y-0 border-subtle bg-layer-1 py-1 text-13 font-medium`, `tabIndex=0`) nur wenn Display-Property aktiv und `shouldRenderColumn` (Estimate nur bei aktivierter Schätzung, `apps/web/helpers/issue-filter.helper.ts:12`). Nach Schließen des Menüs Fokus zurück auf `th`. |
| `columns/header-column.tsx` | `HeaderColumn` | Menü-Trigger (`clickable`, Icon `h-4 w-4 text-placeholder` + Titel, rechts Sortier-Icon wenn aktiv + `ChevronDownOutline`). Menü: „<asc> → <desc>“ (`SortDescendingOutline`), „<desc> → <asc>“ (`SortAscendingOutline`), „Clear sorting“ (`EraserOutline`, nur wenn diese Spalte sortiert und `order_by ≠ -created_at` → setzt `-created_at`). Auswahl wird zusätzlich in **localStorage** `spreadsheetViewSorting` (`${order}_${property}`) und `spreadsheetViewActiveSortingProperty` gespeichert. Bei Epics heißt `sub_issue_count` „Work items“. |
| `issue-row.tsx` | `SpreadsheetIssueRow`, intern `IssueRowDetails` | Zeile (`RenderIfVisible as="tr"`, Platzhalter-`td colSpan=100` Höhe `calc(2.75rem - 1px)`, `verticalOffset 100`; ausgewählt Klasse `group selected-issue-row`, aktiv `border-strong-1`). Erste Zelle sticky (`md:sticky left-0 z-10 max-w-lg`, `tabIndex 0`): `ControlLink` → `Row h-11 border-r-[0.5px] text-13 clickable` mit Identifier (`min-w-24`, nur bei `key`), Checkbox, Einrückung (`spacingLeft` 6 + 12/Ebene), Chevron (Sub-Issues), Name (`text-13 truncate`, Tooltip), Quick-Action „…“ (Hover-sichtbar). Gepeekt: `border-accent-strong`. Danach `IssueColumn` je Property. Sub-Issues rekursiv (bis Ebene 3, danach Peek). |
| `issue-column.tsx` | `IssueColumn` | `td` (`h-11 min-w-36 border-r-[1px] border-subtle text-13`, `tabIndex 0`) mit Komponente aus `SPREADSHEET_COLUMNS`; `onClose` fokussiert die Zelle. |
| `columns/state-column.tsx` | `SpreadsheetStateColumn` | `StateSelect variant table-cell tooltip`. |
| `columns/priority-column.tsx` | `SpreadsheetPriorityColumn` | `PrioritySelect table-cell`. |
| `columns/assignee-column.tsx` | `SpreadsheetAssigneeColumn` | `MemberSelect multiple table-cell`, Placeholder „Assignees“. |
| `columns/label-column.tsx` | `SpreadsheetLabelColumn` | `IssuePropertyLabels` als Tabellenzelle (Placeholder „Select labels“). |
| `columns/module-column.tsx` | `SpreadsheetModuleColumn` | `ModuleSelect multiple table-cell tooltip`, Placeholder „Select modules“; Diff → `changeModulesInIssue`. |
| `columns/cycle-column.tsx` | `SpreadsheetCycleColumn` | `CycleSelect table-cell`, Placeholder „Select cycle“; `addCycleToIssue`/`removeCycleFromIssue`. |
| `columns/start-date-column.tsx` | `SpreadsheetStartDateColumn` | `DateSelect table-cell clearable`, `maxDate = target_date`, Icon `StartDateOutline`. |
| `columns/due-date-column.tsx` | `SpreadsheetDueDateColumn` | `DateSelect table-cell clearable`, `minDate = start_date`, Icon `DueDateOutline`, überfällig rot. |
| `columns/estimate-column.tsx` | `SpreadsheetEstimateColumn` | `EstimateSelect table-cell`, Placeholder „Estimate“. |
| `columns/created-on-column.tsx` | `SpreadsheetCreatedOnColumn` | Read-only Datum (`text-11`). |
| `columns/updated-on-column.tsx` | `SpreadsheetUpdatedOnColumn` | Read-only Datum. |
| `columns/link-column.tsx` | `SpreadsheetLinkColumn` | „N link(s)“ (nicht übersetzt). |
| `columns/attachment-column.tsx` | `SpreadsheetAttachmentColumn` | „N attachment(s)“. |
| `columns/sub-issue-column.tsx` | `SpreadsheetSubIssueColumn` | „N sub-work item(s)“; Klick (wenn >0) → `/{ws}/projects/{pid}/[archives/]{issues\|epics}/{id}#sub-issues`; bei Epics leer. |
| `columns/index.ts` | Barrel | – |

### 2.7 Quick-Add (`apps/web/components/issues/issue-layouts/quick-add/`)

| Datei | Export | Zweck / Verhalten |
|---|---|---|
| `root.tsx` | `QuickAddIssueRoot`, Typen `TQuickAddIssueForm`, `TQuickAddIssueButton` | Zustand offen/zu (optional kontrolliert über `isQuickAddOpen`/`setIsQuickAddOpen`). `react-hook-form` mit `{name:""}`; beim Schließen Reset. Submit: Reset **sofort** (Formular bleibt offen → schnelles Mehrfach-Erfassen), Payload `createIssuePayload(projectId, {...prePopulatedData, ...formData})` (setzt `id` = UUIDv4, `tempId` = UUIDv4, `priority:"none"`, leere Arrays, Zähler 0), `quickAddCallback(projectId, payload)` mit `setPromiseToast`: loading „Adding work item“/„Adding epic“, success „Success!“ + „Work item created successfully“/„Epic created successfully“ + Toast-Aktionen (s. `create-issue-toast-action-items.tsx`), error „Error!“ + `err.message` oder „Some error occurred. Please try again.“. Fehlerrahmen bei Validierungsfehler: `border-danger-strong bg-danger-subtle`. Nur mit Route-`projectId` (sonst nichts). Default-Button (ohne Custom): „New work item“/„New Epic“. |
| `form/root.tsx` | `QuickAddIssueFormRoot` | Wählt Formular je Layout; `Escape` und Outside-Click schließen; Fokus auf `name` beim Öffnen. |
| `form/list.tsx` | `ListQuickAddIssueForm` | Zeile (`border-[0.5px] border-t-0 border-subtle bg-surface-1 px-3`, `shadow-raised-200`): Projekt-Identifier (`text-11 font-medium text-placeholder`, Fallback „...“), Input (Placeholder „Work item title“, Pflicht „Work item title is required.“, `py-3 text-13 font-medium text-secondary`), darunter Hinweis „Press 'Enter' to add another work item“ (`text-11 italic text-secondary`). |
| `form/kanban.tsx` | `KanbanQuickAddIssueForm` | Karte (`m-1 rounded-sm bg-layer-2 shadow-raised-200`, Identifier oben `text-11 text-tertiary`), Hinweisleiste `bg-layer-3`. |
| `form/calendar.tsx` | `CalendarQuickAddIssueForm` | Kompakt (`md:text-11`, `md:border-[0.5px] md:shadow-raised-100`), Placeholder „Work item Title“/„Epic Title“, Pflichttext „Work item title is required.“ (hart codiert), Ein-/Ausblend-Animation (`scale-95 opacity-0` → `scale-100 opacity-100`). |
| `form/gantt.tsx` | `GanttQuickAddIssueForm` | Wie List; bei Fehler `border-danger-strong/20 bg-danger-subtle`. |
| `form/spreadsheet.tsx` | `SpreadsheetQuickAddIssueForm` | Identifier `w-20`, Input `py-3 text-13`, Hinweis `mt-3 ml-3`. |
| `form/index.ts` | Barrel | – |
| `button/list.tsx` | `ListQuickAddIssueButton` | `Row py-3`, `AddOutline 3.5` + „New work item“/„New Epic“. |
| `button/kanban.tsx` | `KanbanQuickAddIssueButton` | `rounded-lg px-2 py-1.5` + „New work item“. |
| `button/gantt.tsx` | `GanttQuickAddIssueButton` | sticky unten, `border-t-[1px] border-subtle`, „New work item“. |
| `button/spreadsheet.tsx` | `SpreadsheetAddIssueButton` | „Add work item“/„Add Epic“. |
| `button/index.ts`, `index.ts` | Barrels | – |
| `../../create-issue-toast-action-items.tsx` | `useCreateIssueToastActions` | Toast-Aktionen nach Erstellen: „Copy link“ (`copyUrlToClipboard`), Identifier `ABC-12` (kopiert Text), primär „View“ (`href` Work-Item-Link, `target _blank`). Leer, wenn Identifier/Sequenz fehlt. |

### 2.8 Quick-Action-Menüs („…“ und Rechtsklick-Kontextmenü) (`apps/web/components/issues/issue-layouts/quick-action-dropdowns/`)

Alle Varianten rendern **zwei** Oberflächen mit identischen Einträgen: (a) `Menu` (Propel) mit Trigger `customActionButton` bzw. Fallback `IconButton variant ghost size sm` + `MoreHorizontalOutline` (`aria-label` „More actions“), Platzierung über `toSideAndAlign(placements)`; (b) `ContextMenu` (`packages/blocks/src/context-menu/context-menu.tsx`) am `parentRef` – Rechtsklick öffnet am Cursor (nicht auf Mobil). Trigger-Guard (`quickActionTriggerGuard`) verhindert, dass Klick/Enter/Space die umgebende Zeile (Link) auslöst; Popup stoppt Bubbling. Einträge mit `nestedMenuItems` werden zu Submenüs (`MenuSubmenu`, in CE ungenutzt).

| Datei | Export | Einträge (Reihenfolge) & Regeln |
|---|---|---|
| `helper.tsx` | `useMenuItemFactory`, `useIssueActionHandlers`, `handleOptionalAction`, `quickActionTriggerGuard`, `isNativeQuickActionTrigger`, `stopQuickActionPropagation`, Sets `useProjectIssueMenuItems`, `useWorkItemDetailMenuItems`, `useAllIssueMenuItems`, `useCycleIssueMenuItems`, `useModuleIssueMenuItems`, `useArchivedIssueMenuItems` | Eintragsfabrik: **Edit** (`EditOutline`, nur `isEditingAllowed`) öffnet Create/Update-Modal mit Issue; **Make a copy** (`CopyOutline`, nur Edit-Recht und aktiver Issue-Typ) öffnet Modal mit Kopie-Payload; **Open in new tab** (`NewTabOutline`, `window.open(link,"_blank")`); **Copy link** (`LinkOutline`, Toast success „Link copied“ / „Work item link copied to clipboard“); **Remove from cycle** / **Remove from module** (`CloseCircleOutline`, hart codierte englische Titel); **Archive** (`ArchiveOutline`, `disabled` wenn State-Gruppe ∉ {completed, cancelled}, dann Beschreibung „Only completed or canceled work items can be archived“); **Restore** (`RestoreOutline`, Toast „Restore success“ / „Your work item can be found in project work items.“, Fehler „Work item could not be restored. Please try again.“); **Delete** (`DeleteOutline`) öffnet `DeleteIssueModal`. Fehlt ein Handler → Toast error „Action not available“ / „<Name> action is not implemented.“. |
| `copy-menu-helper.tsx` | `createCopyMenuWithDuplication` | CE-Stub: gibt den „Make a copy“-Eintrag unverändert zurück (EE ergänzt hier ein Duplizieren-in-anderes-Projekt-Submenü → in der neuen Plattform implementieren, s. 5). |
| `project-issue.tsx` | `ProjectIssueQuickActions` | Edit, Make a copy, Open in new tab, Copy link, Archive, Delete. Edit-Recht = ADMIN/MEMBER im **Issue-Projekt** && `!readOnly`; Archive nur wenn `handleArchive` vorhanden. Kopie-Payload: alle Felder außer `id`, `name = "<name> (copy)"`, `sourceIssueId = id`. Default-Placement `bottom-end`. |
| `cycle-issue.tsx` | `CycleIssueQuickActions` | Edit (setzt `cycle_id = aktueller Cycle` im Modal), Make a copy, Open in new tab, Copy link, Remove from cycle (`handleRemoveFromView`), Archive, Delete. Edit-Recht = ADMIN/MEMBER im aktuellen Projekt. Placement `bottom-start`. |
| `module-issue.tsx` | `ModuleIssueQuickActions` | Wie Cycle, aber Edit setzt `module_ids = [moduleId]`, „Remove from module“. |
| `all-issue.tsx` | `AllIssueQuickActions` | Workspace-Views: Edit, Make a copy, Open in new tab, Copy link, Archive, Delete; Edit-Recht nur `!readOnly` (Rolle wird vom Aufrufer geprüft). Store `GLOBAL`. |
| `archived-issue.tsx` | `ArchivedIssueQuickActions` | Restore, Open in new tab, Copy link, Delete. Restore erlaubt wenn `handleRestore` und ADMIN/MEMBER (unabhängig von `readOnly`); Delete nur bei Edit-Recht && `!readOnly` (im Archiv-List-Root ist `readOnly` immer true → **Delete ausgeblendet**). Placement `bottom-end`. |
| `issue-detail.tsx` | `WorkItemDetailQuickActions` | Für Detail-/Peek-Kopf: Make a copy, Open in new tab, Archive (nur nicht archiviert), Restore (nur archiviert), Delete. Trigger `IconButton size md variant secondary` (`aria-label` „Options“). Optional Callbacks `toggleEditIssueModal`, `toggleDeleteIssueModal`, `toggleDuplicateIssueModal`, `toggleArchiveIssueModal` (für Tastatur-Kontext/Peek); `isPeekMode` blendet Edit/Copy link aus. Create-Modal mit `fetchIssueDetails={false}`. |
| `index.ts` | Barrel | exportiert zusätzlich `../../workspace-draft/quick-action`. |

### 2.9 Layout-Empty-States (`apps/web/components/issues/issue-layouts/empty-states/`)

Alle nutzen `EmptyStateDetailed` (`@plane/blocks/empty-state`) mit `assetKey` (Illustration), Titel, Beschreibung und Aktions-Buttons. Aktionen sind deaktiviert ohne Rolle ADMIN/MEMBER. „Filter aktiv“-Varianten nutzen `useWorkItemFilterInstance(storeType, entityId).hasActiveFilters` / `.clearFilters`.

| Datei | Export / Store | Zustand → Inhalt (en) |
|---|---|---|
| `index.tsx` | `IssueLayoutEmptyState` | Switch: PROJECT→`ProjectEmptyState`, PROJECT_VIEW→`ProjectViewEmptyState`, ARCHIVED→`ProjectArchivedEmptyState`, CYCLE→`CycleEmptyState`, MODULE→`ModuleEmptyState`, GLOBAL→`GlobalViewEmptyState`, PROFILE→`ProfileViewEmptyState`, EPIC→`ProjectEpicsEmptyState`, sonst `null`. |
| `project-issues.tsx` | `ProjectEmptyState` | Filter aktiv: asset `search`, „No matching results.“ / „No results found. Try adjusting your search terms.“, Button sekundär „Clear all filters“. Sonst: asset `work-item`, „Start with your first work item.“ / „Work items are the building blocks of your project — assign owners, set priorities, and track progress easily.“, primär „Create your first work item“ → `toggleCreateIssueModal(true, PROJECT)`. |
| `project-view.tsx` | `ProjectViewEmptyState` | (nicht übersetzt) „View work items will appear here“ / „Work items help you track individual pieces of work. With work items, keep track of what's going on, who is working on it, and what's done.“, primär „New work item“ → Create-Modal (PROJECT_VIEW). |
| `archived-issues.tsx` | `ProjectArchivedEmptyState` | Filter aktiv: Suche-Empty-State + „Clear filters“. Sonst asset `archived-work-item`, „No archived work items yet“ / „Manually or through automation, you can archive work items that are completed or cancelled. Find them here once archived.“, primär „Set automation“ → `/{ws}/settings/projects/{pid}/automations`. |
| `cycle.tsx` | `CycleEmptyState` | Abgeschlossen (Snapshot vorhanden oder Status completed): „No work items in the cycle“ / „No work items in the cycle. Work items are either transferred or hidden. To see hidden work items if any, update your display properties accordingly.“ (ohne Aktion). Filter aktiv: Suche + „Clear filters“. Sonst: „No work items to show in this cycle“ / „Create work items to begin monitoring your team's progress this cycle and achieve your goals on time.“, primär „Create work item“ (Create-Modal CYCLE), sekundär „Add existing work item“ → `ExistingIssuesListModal {cycle:true}` → `addIssueToCycle`, Toasts „Work items added to the cycle successfully.“ / „Selected work items could not be added to the cycle. Please try again.“. |
| `module.tsx` | `ModuleEmptyState` | Filter aktiv: Suche. Sonst „No work items to show in this Module“ / „Create work items to begin monitoring this module.“, „Create work item“, „Add existing work item“ (`{module: id}`), Toasts „…added to the module successfully.“ / „…could not be added to the module…“. |
| `global-view.tsx` | `GlobalViewEmptyState` | Keine Projekte: asset `project` (`size-40`), „No project“ / „To create work items or manage your work, you need to create a project or be a part of one.“, „Start your first project“ → Create-Project-Modal. Sonst „No Views yet“ / „Add work items to your project and use views to filter, sort, and monitor progress effortlessly.“, „Add work item“. Rechte: Workspace-ADMIN/MEMBER. |
| `profile-view.tsx` | `ProfileViewEmptyState` | i18n `profile.empty_state.<profileViewId>.*` (assigned: „No work items are assigned to you“ / „Work items assigned to you can be tracked from here.“; created: „No work items yet“ / „All work items created by you come here, track them here directly.“; subscribed: „No work items yet“ / „Subscribe to work items you are interested in, track all of them here.“). |
| `project-epic.tsx` | `ProjectEpicsEmptyState` | CE-Stub (leer) – Epics sind Bezahlfeature, Empty-State neu bauen. |

### 2.10 Layout-Auswahl, Display-Filter („Display“-Dropdown) und klassische Filter (`apps/web/components/issues/issue-layouts/filters/`)

**Layout-Auswahl & Display**

| Datei | Export | Zweck / Verhalten |
|---|---|---|
| `header/layout-selection.tsx` | `LayoutSelection` | Segment-Control (`flex gap-1 rounded-md bg-layer-3 p-1`), je Layout ein Button `h-5.5 w-7 rounded-sm hover:bg-layer-transparent-hover`, aktiv `bg-layer-transparent-active`; Icon 14 px (`text-primary` aktiv, sonst `text-secondary`), Tooltip/`aria-label` = „List Layout“, „Board Layout“, „Calendar Layout“, „Table Layout“, „Timeline Layout“. Reihenfolge `ISSUE_LAYOUTS` (list, kanban, calendar, spreadsheet, gantt_chart). Klick auf aktives Layout ignoriert. |
| `header/mobile-layout-selection.tsx` | `MobileLayoutSelection` | Mobil: Menü-Trigger (sekundärer Button-Look mit aktuellem Layout-Icon + Chevron), Einträge mit Icon + Label („List“, „Board“, „Calendar“, „Table“, „Timeline“). |
| `header/display-filters/display-filters-selection.tsx` | `DisplayFiltersSelection` | Inhalt des „Display“-Popovers (`vertical-scrollbar scrollbar-sm divide-y divide-subtle-1 px-2.5`), Sektionen in fester Reihenfolge: Display Properties → Group by → Sub-group by (nur Kanban **und** `group_by !== null`) → Order by (nur wenn Optionen nicht leer) → Options (Extra-Optionen, wenn `extra_options.access`). Schaltet `cycle`/`module` aus Gruppierung und Properties aus, wenn `cycleViewDisabled`/`moduleViewDisabled`. Extra-Optionen-Defaults: `show_empty_groups ?? true`, `sub_issue ?? true`. |
| `header/display-filters/display-properties.tsx` | `FilterDisplayProperties` | Titel „Display Properties“, Chips (`rounded-sm border px-2 py-0.5 text-11`; aktiv `border-accent-strong bg-accent-primary text-on-color`, sonst `border-subtle hover:bg-layer-1`) – Toggle je Property. Reihenfolge `ISSUE_DISPLAY_PROPERTIES`: ID, Assignee, Start date, Due date, Labels, Priority, State, Sub-work item count (bei Epics „Work item count“), Attachment count, Link, Estimate, Module, Cycle. `issue_type` ist in CE nicht in der Liste. |
| `header/display-filters/group-by.tsx` | `FilterGroupBy` | „Group by“, Radio-Optionen (`FilterOption multiple=false`); bei Kanban wird die aktuelle Sub-Gruppe ausgeblendet; ignorierte Gruppen ausgeblendet. |
| `header/display-filters/sub-group-by.tsx` | `FilterSubGroupBy` | Titel (hart codiert) „Sub-group by“; blendet aktuelle Gruppe aus. |
| `header/display-filters/order-by.tsx` | `FilterOrderBy` | „Order by“; aktiv = `order_by ?? "-created_at"`. |
| `header/display-filters/extra-options.tsx` | `FilterExtraOptions` | Checkboxen „Show sub-work items“ (`sub_issue`), „Show empty groups“ (`show_empty_groups`) – nur die laut Seite erlaubten. |
| `header/helpers/dropdown.tsx` | `FiltersDropdown` | Popover-Rahmen für „Display“/„Filters“: ab Container-Breite `@4xl` Button sekundär mit Icon + Titel (Punkt `h-2 w-2 rounded-full bg-accent-primary` oben rechts bei angewendeten Filtern), darunter nur `IconButton` (miniIcon). Panel `variant rich`, `w-[18.75rem] max-h-[30rem] lg:max-h-[37.5rem]`. Alternativ eigener `menuButton`. |
| `header/helpers/filter-header.tsx` | `FilterHeader` | Sticky Sektionskopf (`text-caption-sm-medium text-placeholder`) mit Auf/Zu-Chevron (`h-5 w-5 rounded-sm`). |
| `header/helpers/filter-option.tsx` | `FilterOption` | Zeile (`rounded-sm p-1.5 hover:bg-layer-transparent-hover`), Checkbox 12×12 (multiple: `rounded-xs`, single: `rounded-full`; aktiv `border-accent-strong bg-accent-primary text-on-color` + `TickOutline 10`), optional Icon (`w-5`), Titel `text-caption-sm-regular text-secondary`, optional pulsierender Punkt. |
| `header/helpers/index.ts`, `header/index.ts`, `index.ts`, `header/display-filters/index.ts` | Barrels | – |

**Klassische Filter-Sektionen (Legacy-Filter-Dropdown).** Die Bausteine aus `apps/web/components/issues/issue-layouts/filters/` (Filter-Sektionen, `FilterHeader`, `FilterOption`, Display-Filter-Dropdown) werden außerhalb dieses Verzeichnisses von genau diesen Dateien importiert (ermittelt per `grep -rl "issue-layouts/filters"`): `apps/web/app/(all)/[workspaceSlug]/(projects)/profile/[userId]/mobile-header.tsx`, `apps/web/app/(all)/[workspaceSlug]/(projects)/projects/(detail)/[projectId]/cycles/(detail)/header.tsx`, `apps/web/app/(all)/[workspaceSlug]/(projects)/projects/(detail)/[projectId]/cycles/(detail)/mobile-header.tsx`, `apps/web/app/(all)/[workspaceSlug]/(projects)/projects/(detail)/[projectId]/issues/(list)/mobile-header.tsx`, `apps/web/app/(all)/[workspaceSlug]/(projects)/projects/(detail)/[projectId]/modules/(detail)/header.tsx`, `apps/web/app/(all)/[workspaceSlug]/(projects)/projects/(detail)/[projectId]/modules/(detail)/mobile-header.tsx`, `apps/web/app/(all)/[workspaceSlug]/(projects)/projects/(detail)/[projectId]/views/(detail)/[viewId]/header.tsx`, `apps/web/app/(all)/[workspaceSlug]/(projects)/projects/(detail)/[projectId]/views/(list)/mobile-header.tsx`, `apps/web/app/(all)/[workspaceSlug]/(projects)/workspace-views/header.tsx`, `apps/web/components/common/filters/created-at.tsx`, `apps/web/components/common/filters/created-by.tsx`, `apps/web/components/cycles/archived-cycles/header.tsx`, `apps/web/components/cycles/cycles-view-header.tsx`, `apps/web/components/cycles/dropdowns/filters/end-date.tsx`, `apps/web/components/cycles/dropdowns/filters/start-date.tsx`, `apps/web/components/cycles/dropdowns/filters/status.tsx`, `apps/web/components/inbox/inbox-filter/filters/date.tsx`, `apps/web/components/inbox/inbox-filter/filters/labels.tsx`, `apps/web/components/inbox/inbox-filter/filters/members.tsx`, `apps/web/components/inbox/inbox-filter/filters/priority.tsx`, `apps/web/components/inbox/inbox-filter/filters/state.tsx`, `apps/web/components/inbox/inbox-filter/filters/status.tsx`, `apps/web/components/inbox/inbox-filter/root.tsx`, `apps/web/components/issues/archived-issues-header.tsx`, `apps/web/components/issues/filters.tsx`, `apps/web/components/issues/issue-detail-widgets/sub-issues/display-filters.tsx`, `apps/web/components/issues/issue-detail-widgets/sub-issues/filters.tsx`, `apps/web/components/modules/archived-modules/header.tsx`, `apps/web/components/modules/dropdowns/filters/lead.tsx`, `apps/web/components/modules/dropdowns/filters/members.tsx`, `apps/web/components/modules/dropdowns/filters/root.tsx`, `apps/web/components/modules/dropdowns/filters/start-date.tsx`, `apps/web/components/modules/dropdowns/filters/status.tsx`, `apps/web/components/modules/dropdowns/filters/target-date.tsx`, `apps/web/components/modules/module-view-header.tsx`, `apps/web/components/pages/header/root.tsx`, `apps/web/components/pages/list/filters/root.tsx`, `apps/web/components/profile/profile-issues-filter.tsx`, `apps/web/components/project/dropdowns/filters/access.tsx`, `apps/web/components/project/dropdowns/filters/created-at.tsx`, `apps/web/components/project/dropdowns/filters/lead.tsx`, `apps/web/components/project/dropdowns/filters/members.tsx`, `apps/web/components/project/dropdowns/filters/root.tsx`, `apps/web/components/project/filters.tsx`, `apps/web/components/projects/mobile-header.tsx`, `apps/web/components/views/filters/filter-selection.tsx`, `apps/web/components/views/form.tsx`, `apps/web/components/views/view-list-header.tsx`, `apps/web/components/workspace/views/form.tsx`.

Gemeinsames Muster: `FilterHeader` mit Titel „<Name> (<Anzahl>)“, Suche über `searchQuery` (Teilstring, case-insensitive), Sortierung: ausgewählte zuerst, dann (bei Mitgliedern) „ich“ zuerst, dann alphabetisch; erste 5 sichtbar, Toggle „View all“/„View less“ (`ml-8 text-11 font-medium text-accent-primary`); keine Treffer → „No matches found“ (`text-11 italic text-placeholder`); ohne Daten 3 Skeleton-Zeilen 20 px.

| Datei | Export | Titel | Optionen / Icon |
|---|---|---|---|
| `header/filters/assignee.tsx` | `FilterAssignees` | „Assignee“ | Mitglieder, Avatar xs, eigener Name als „You“ |
| `header/filters/created-by.tsx` | `FilterCreatedBy` | „Created by“ | Mitglieder, Avatar, „You“ |
| `header/filters/mentions.tsx` | `FilterMentions` | „Mention“ | Mitglieder, Avatar, „You“ |
| `header/filters/labels.tsx` | `FilterLabels` | „Label“ | Labels mit Farbpunkt (`LabelIcons`) |
| `header/filters/priority.tsx` | `FilterPriority` | „Priority“ | urgent…none mit `PriorityIcon`; Suche auf Key; leer → „No matches found“ (i18n `common.search.no_matches_found`) |
| `header/filters/state.tsx` | `FilterState` | „State“ | Projekt-States mit `StateGroupIcon` (Farbe, Order) |
| `header/filters/state-group.tsx` | `FilterStateGroup` | „State group“ | `STATE_GROUPS` (Backlog, Unstarted, Started, Completed, Cancelled) |
| `header/filters/cycle.tsx` | `FilterCycle` | „Cycle“ | Cycles mit `CycleGroupIcon` |
| `header/filters/module.tsx` | `FilterModule` | „Module“ | Module mit `ModuleOutline` |
| `header/filters/project.tsx` | `FilterProjects` | „Project“ | Projekte mit Logo |
| `header/filters/start-date.tsx` | `FilterStartDate` | „Start date“ | `DATE_AFTER_FILTER_OPTIONS` („1 week from now“ `1_weeks;after;fromnow`, „2 weeks from now“, „1 month from now“ `1_months;after;fromnow`, „2 months from now“) + „Custom“ → `DateFilterModal` (`apps/web/components/core/filters/date-filter-modal`); Custom-Werte enthalten „-“ (Datum) |
| `header/filters/due-date.tsx` | `FilterDueDate` | „Due date“ | wie Start date |
| `header/filters/index.ts` | Barrel | – | – |

**Angewendete Filter (Chips)** – `applied-filters/*.tsx`: Chip `flex items-center gap-1 rounded-sm bg-layer-1 p-1 text-11`, Entfernen-Button `CloseOutline 10` (`text-tertiary hover:text-secondary`) nur wenn `editable`.

| Datei | Export | Darstellung |
|---|---|---|
| `applied-filters/members.tsx` | `AppliedMembersFilters` | Avatar `2xs` + Anzeigename (Workspace-Mitglied) |
| `applied-filters/priority.tsx` | `AppliedPriorityFilters` | `PriorityIcon 3×3` + Key |
| `applied-filters/date.tsx` | `AppliedDateFilters` | Name aus `DATE_AFTER_FILTER_OPTIONS` oder „<After/Before> <Datum>“ (Format `YYYY-MM-DD;after`) – immer entfernbar |
| `applied-filters/label.tsx` | `AppliedLabelsFilters` | Farbpunkt + Labelname |
| `applied-filters/state.tsx` | `AppliedStateFilters` | `StateGroupIcon` + Name |
| `applied-filters/state-group.tsx` | `AppliedStateGroupFilters` | `StateGroupIcon` + Gruppe |
| `applied-filters/cycle.tsx` | `AppliedCycleFilters` | `CycleGroupIcon` + Name |
| `applied-filters/module.tsx` | `AppliedModuleFilters` | `ModuleOutline` + Name |
| `applied-filters/project.tsx` | `AppliedProjectFilters` | Logo + Name |
| `applied-filters/index.ts` | Barrel | – |

### 2.11 Rich-Filters (`apps/web/components/rich-filters/`) und Work-Item-Filter-Anbindung (`apps/web/components/work-item-filters/`)

**Generische Rich-Filter-UI**

| Datei | Export | Zweck / Verhalten |
|---|---|---|
| `filters-row.tsx` | `FiltersRow` | Filterzeile unter dem Seitenkopf. Varianten `header` (Default; `Header variant TERNARY min-h-11 bg-surface-1 !px-3`) und `modal` (`min-h-11 rounded-lg bg-layer-1 p-2`). Inhalt `flex items-start gap-2 rounded-lg bg-layer-1 px-4 py-2`: links alle Bedingungen (`FilterItem`) + `AddFilterButton` (Icon `AddFilterOutline`, im Modal-Variant mit Label „Filters“ solange keine Bedingung); rechts (abgetrennt `border-l border-subtle pl-4`, nur wenn Aktionen möglich) Buttons sekundär sm: „Clear all“ (`canClearFilters`), „Save view“ bzw. Label aus Optionen (`canSaveView`), „Update view“ (`canUpdateView`; während Speichern „Confirming“ + Spinner, 240 ms Nachlauf gegen Flackern). Ein-/Ausblenden über `RowTransition` (`-translate-y-1 opacity-0` → `translate-y-0 opacity-100`, 150/100 ms) gesteuert durch `filter.isVisible`. Solange Konfigurationen nicht bereit und keine Bedingungen: Skeleton 44 px. Buttons via `ElementTransition` (`scale-95 opacity-0` → `scale-100 opacity-100`, 200/150 ms). |
| `filters-toggle.tsx` | `FiltersToggle` | Filter-Button im Seitenkopf: ohne Bedingungen, Zeile verborgen und ohne ungespeicherte Änderungen → `AddFilterButton` (Icon-only, Auswahl öffnet zusätzlich die Zeile). Sonst `IconButton md` (`FilterOutline`; bei Bedingungen/Änderungen `SelectedFilterOutline` in `text-accent-primary`, Variante `tertiary`), Klick toggelt Zeilen-Sichtbarkeit, `aria-pressed`. |
| `add-filters/button.tsx` | `AddFilterButton` | Trigger (Button/IconButton-Chrome) für `AddFilterDropdown`; Auswahl → `filter.addCondition(AND, {property, operator: firstOperator, value: undefined}, isNegation)`. Versteckt wenn `isDisabled`. |
| `add-filters/dropdown.tsx` | `AddFilterDropdown` | Combobox mit Suche (Placeholder „Search“), Liste der verfügbaren Felder (`configManager.allAvailableConfigs`: aktivierte Felder ohne bereits verwendete, außer `allowMultipleFilters`), Icon `size-4 text-tertiary`, optional `rightContent`. Leer: „All filters applied“ (keine Felder mehr) bzw. „No matching results“. Feld ohne Operator → Toast error „Filter configuration error“ / „This filter is not properly configured and cannot be applied“. Wird auch zum **Ändern der Eigenschaft** einer bestehenden Bedingung genutzt. |
| `filter-item/root.tsx` | `FilterItem` | Chip aus 4 Segmenten (`h-7 rounded-sm border border-subtle bg-surface-1`, Segmente durch `border-r border-subtle-1` getrennt): Eigenschaft (Icon 3.5 + Label, `text-11 text-tertiary`, klickbar → Eigenschaft wechseln), Operator (`Select` `select-ghost-md`, ohne Chevron; deaktiviert, wenn nur ein Operator), Wert (`FilterValueInput`), Entfernen (×). Loader `FilterItemLoader` (28×180 px) solange Konfigurationen fehlen; ohne Konfiguration `InvalidFilterItem`. |
| `filter-item/container.tsx` | `FilterItemContainer` | Rahmen; Varianten `default`/`error` (`border-danger-strong bg-surface-2`); Einblend-Animation (opacity/scale) beim Hinzufügen einer Bedingung ohne Wert; optional Tooltip. |
| `filter-item/property.tsx` | `FilterItemProperty` | Eigenschaftssegment (`px-2 py-[5px] text-11 text-tertiary`), Tooltip aus `tooltipContent`. |
| `filter-item/close-button.tsx` | `FilterItemCloseButton` | `CloseOutline 3.5`, `aria-label` „Remove filter“, `px-1.5 text-placeholder hover:bg-layer-transparent-hover hover:text-tertiary` → `removeCondition(id)`. |
| `filter-item/invalid.tsx` | `InvalidFilterItem` | Fehler-Chip: Icon `WarningCircleOutline`, Label „Invalid filter“, Tooltip „This filter condition is no longer valid. The property may have been deleted or your access to it may have changed.“ |
| `filter-item/loader.tsx` | `FilterItemLoader` | Skeleton. |
| `filter-value-input/root.tsx` | `FilterValueInput`, `AdditionalFilterValueInput` | Wählt Eingabe nach `FILTER_FIELD_TYPE`: `SINGLE_SELECT`, `MULTI_SELECT`, `DATE`, `DATE_RANGE`; sonst „Filter type not supported“ (`text-11 text-placeholder cursor-not-allowed`). |
| `filter-value-input/select/multi.tsx` | `MultiSelectFilterValueInput` | `Select multiple` (Optionen asynchron via `config.getOptions()`, „Loading“ als Leer-Text), öffnet automatisch wenn noch kein Wert; unbekannte IDs bleiben als Platzhalter-Option erhalten. |
| `filter-value-input/select/single.tsx` | `SingleSelectFilterValueInput` | Einfachauswahl; erneutes Wählen desselben Werts setzt `null`. |
| `filter-value-input/select/selected-options-display.tsx` | `SelectedOptionsDisplay` | Anzeige: leer „--“; bis 2 (single: 1) Werte mit Icon, Label `max-w-24 truncate`, Komma-getrennt; Rest „+N more“ (`animate-fade-in`); ohne Optionen „N option(s) selected“. |
| `filter-value-input/select/shared.tsx` | `loadOptions` | Lädt Optionen (Fehler → Konsole). |
| `filter-value-input/date/single.tsx` | `SingleDateFilterValueInput` | `DateSelect pill-lg` flach im Chip, Placeholder „--“, auto-open ohne Wert, Wochenstart aus Profil, `min/max` aus Konfiguration. |
| `filter-value-input/date/range.tsx` | `DateRangeFilterValueInput` | `DateRangeSelect mergeDates pill-lg`, unvollständiger Bereich rot (`text-danger-primary`) und auto-open; erst bei vollständigem Bereich `[from, to]`, sonst `[]`. |
| `transition-components.tsx` | `ElementTransition`, `RowTransition` | Selbstgebaute Enter/Leave-Transitions (Ersatz für Headless-UI). |
| `shared.ts` | `COMMON_FILTER_ITEM_BORDER_CLASSNAME = "border-r border-subtle-1"`, `EMPTY_FILTER_PLACEHOLDER_TEXT = "--"`, `TFilterValueInputProps` | – |

**Work-Item-spezifische Anbindung**

| Datei | Export | Zweck / Verhalten |
|---|---|---|
| `filters-hoc/base.tsx` | `WorkItemFiltersHOC` | Ohne `initialWorkItemFilters` → Kinder mit `filter: undefined`. Sonst `getOrCreateFilter({entityType, entityId (bei `isTemporary`: `TEMP-<id\|uuid>`), initialExpression: richFilters, onExpressionChange: updateFilters, expressionOptions: {saveViewOptions, updateViewOptions}, showOnMount})` aus `useWorkItemFilters()` (`apps/web/hooks/store/work-item-filters/use-work-item-filters`). Registriert Feldkonfigurationen aus `useWorkItemFiltersConfig`; löscht die Instanz beim Unmount. |
| `filters-hoc/project-level.tsx` | `ProjectLevelWorkItemFiltersHOC` | Liefert Projekt-States/Labels/Mitglieder/Cycles/Module an die Konfiguration. **Save view** erlaubt, wenn `project.issue_views_view === true`, `enableSaveView`, Rolle ADMIN/MEMBER. **Update view** erlaubt, wenn `enableUpdateView`, View nicht `is_locked`, ADMIN/MEMBER **und** aktueller Nutzer = `owned_by`. „Additional changes“ = Display-Filter/-Properties weichen von gespeicherter View ab. Save → `CreateUpdateProjectViewModal` vorbefüllt (`name` = „<View-Name> 2“ bzw. „Untitled“, `description`, `logo_props`, `access` (Default `PUBLIC`), `rich_filters`, `display_filters`, `display_properties`). Update → `updateView(ws, pid, viewId, {rich_filters, display_filters, display_properties})`; Toasts „Success!“/„Your view has been updated successfully.“, „Error!“/„Your view could not be updated. Please try again.“, „We couldn't find the view“/„The view you're trying to update doesn't exist.“ |
| `filters-hoc/workspace-level.tsx` | `WorkspaceLevelWorkItemFiltersHOC` | Analog für Workspace-Views (`CreateUpdateWorkspaceViewModal`, `updateGlobalView`); Optionen: Workspace-Mitglieder, Workspace-Labels, `joinedProjectIds`. Save: Workspace-ADMIN/MEMBER. Update zusätzlich nicht bei Default-Views (`DEFAULT_GLOBAL_VIEWS_LIST`). |
| `filters-hoc/shared.ts` | Typen `TSharedWorkItemFiltersProps`, `TSharedWorkItemFiltersHOCProps`, `TEnableSaveViewProps`, `TEnableUpdateViewProps` | – |
| `filters-row.tsx` | `WorkItemFiltersRow` | Typisierter Wrapper um `FiltersRow`. |
| `filters-toggle.tsx` | `WorkItemFiltersToggle` | Holt Instanz per `(entityType, entityId)` und rendert `FiltersToggle` (wird in Seitenköpfen genutzt). |

**Filterfelder (`apps/web/hooks/work-item-filters/use-work-item-filters-config.tsx`, Fabriken `packages/utils/src/work-item-filters/configs/filters/*.ts`)**

| Property-Key | Label | Icon (Feld) | Options-Icon | Operatoren (CE) | Aktiv wenn |
|---|---|---|---|---|---|
| `state_id` | State | `StateOutline` | `StateGroupIcon` (Farbe) | `in` (Anzeige „is“ bei ≤1 Wert, „is any of“ bei >1) | Feld erlaubt + States geladen |
| `state_group` | State Group | `StateOutline` | `StateGroupIcon` | `in` | erlaubt |
| `assignee_id` | Assignees | `MembersOutline` | Avatar 2xs | `in` | erlaubt + Mitglieder |
| `priority` | Priority | `PriorityOutline` | `PriorityIcon` | `in` (`packages/utils/src/work-item-filters/configs/filters/priority.ts`) | erlaubt |
| `project_id` | Projects | `ProjectsOutline` | Projekt-Logo 12 | `in` | erlaubt + Projekte |
| `mention_id` | Mentions | `AtOutline` | Avatar | `in` | erlaubt + Mitglieder |
| `label_id` | Label | `LabelsOutline` | Farbpunkt 2.5 | `in` | erlaubt + Labels |
| `cycle_id` | Cycle | `CyclesOutline` | `CycleGroupIcon` | `in` | erlaubt + `project.cycle_view` |
| `module_id` | Module | `ModuleOutline` | `ModuleOutline` | `in` | erlaubt + `project.module_view` |
| `start_date` | Start date | `StartDateOutline` | – | `exact` („is“, Datum), `range` („between“, Datumsbereich); mehrfach verwendbar | **immer** |
| `target_date` | Target date | `DueDateOutline` | – | wie oben | immer |
| `created_at` | Created at | `CalendarOutline` | – | wie oben | immer |
| `updated_at` | Updated at | `CalendarOutline` | – | wie oben | immer |
| `created_by_id` | Created by | `UserOutline` | Avatar | `in` | erlaubt + Mitglieder |
| `subscriber_id` | Subscriber | `MembersOutline` | Avatar | `in` | erlaubt + Mitglieder |

Reihenfolge im Dropdown = Reihenfolge der `configs`-Liste: State, State Group, Assignees, Priority, Projects, Mentions, Label, Cycle, Module, Start date, Target date, Created at, Updated at, Created by, Subscriber. Operator-Labels: `exact`=„is“, `in`=„is any of“, `range`=„between“, leer „--“ (`packages/constants/src/rich-filters/operator-labels/core.ts`). Logischer Operator nur `and`. CE: `useFiltersOperatorConfigs` (`apps/web/hooks/rich-filters/use-filters-operator-configs.ts`) liefert `allowedOperators = CORE_OPERATORS`, `allowNegative = false`; `EXTENDED_*`-Operatoren und Negations-Labels (`packages/types/src/rich-filters/operators/extended.ts`, `packages/constants/src/rich-filters/operator-labels/extended.ts`) sind leer → Bezahl-Editionen erweitern hier (s. 5).

### 2.12 Peek-Overview (`apps/web/components/issues/peek-overview/`)

| Datei | Export | Zweck / Verhalten |
|---|---|---|
| `root.tsx` | `IssuePeekOverview` | Props: `embedIssue?`, `embedRemoveCurrentNotification?`, `is_draft?`, `storeType?`. Liest `peekIssue {workspaceSlug, projectId, issueId, nestingLevel?, isArchived?}` aus `IssueDetailStore`. Lädt per SWR-Key `["peek-issue", ws, pid, id]` (`fetchIssue`, keine Revalidierung bei Focus/Reconnect). `useWorkItemProperties` lädt Begleitdaten (Labels/States/Mitglieder …). Definiert `issueOperations` (s. 3.9). `isEditable` = ADMIN/MEMBER im Peek-Projekt. Ohne Peek → leeres Fragment. |
| `view.tsx` | `IssueView` | Panel mit Modus-State `peekMode` (Default **„side-peek“**, nicht persistiert). Klassen: Side-Peek `absolute top-0 right-0 bottom-0 w-full md:w-[50%] border-l`; Modal `top-[8.33%] left-[8.33%] size-5/6`; Full-Screen `absolute inset-0 m-4`; gemeinsam `z-[25] rounded-sm border border-subtle bg-surface-1 transition-all duration-300`, Schatten `0 4px 8px rgba(0,0,0,.12), 0 6px 12px rgba(16,24,40,.12), 0 1px 16px rgba(16,24,40,.12)`. Render per Portal in `#full-screen-portal` (außer `embedIssue`). Inhalt: Side-Peek/Modal einspaltig (`px-8 py-5 gap-3`: Details → Widgets → Properties → Activity); Full-Screen zweispaltig (links Details/Widgets/Activity `p-4 py-5`, rechts Properties `w-[400px] border-l p-4 py-5`, bei Archiv `pointer-events-none`). Fehler → `IssuePeekOverviewError`; Laden → `IssuePeekOverviewLoader`. Schließen: Outside-Click (s. 3.9) und `Escape` (nicht bei offenen Modals, fokussiertem `INPUT`, offenen Editor-Dropbars oder Bild-Vollbild-Modal; danach Fokus zurück auf `#issue-<id>`). Lokale Modals (Delete/Archive/Duplicate/Edit) blockieren Outside-Close. |
| `header.tsx` | `IssuePeekOverviewHeader`, Typ `TPeekModes` | Links: „Schließen“ (`ArrowNarrowRightOutline 4×4`, Tooltip „Close the peek view“), „Vollbild-Seite“ (`DragDropOutline`, Link zur Detailseite, Tooltip „Open work item in full screen“, schließt Peek), Modus-Select (Icon-Trigger `icon-md`, Tooltip „Toggle peek view layout“, Optionen „Side Peek“ `SidePeekOutline`, „Modal“ `ModalPeekOutline`, „Full Screen“ `FullScreenPeekOutline`; nicht bei `embedIssue`). Rechts: Speicherstatus `NameDescriptionUpdateStatus`, Subscribe-Button (`IssueSubscription`, nicht im Archiv), „Copy link“ (`IconButton secondary md`, Toast „Link copied!“ / „Link copied to clipboard“), `WorkItemDetailQuickActions isPeekMode`. Full-Screen: Kopf mit `border-b`. Delete im Archiv über Archiv-Store. |
| `issue-detail.tsx` | `PeekOverviewIssueDetails` | Parent-Zeile (`IssueParentDetail`, wenn `parent_id`), Identifier (`IssueTypeSwitcher` → in CE nur `IssueIdentifier size md enableClickToCopyIdentifier`), Titel (`IssueTitleInput`), Beschreibung (`DescriptionInput`, `containerClassName "-ml-3 border-none"`, `fileAssetType ISSUE_DESCRIPTION`, leere Beschreibung → `<p></p>`; Migrations-Updates mit `skip_activity:"true"`), darunter Reaktionen (`IssueReaction`) und Versionsverlauf (`DescriptionVersionsRoot`, nur wenn editierbar; Restore setzt Editor-Inhalt). Speicherstatus: `submitting` → Reload-Warnung aktiv; `submitted` → nach 2 s `saved`. |
| `properties.tsx` | `PeekOverviewProperties` | „Properties“ (`text-body-xs-medium`), Liste `SidebarPropertyListItem` (Icon + Label + Wert, `space-y-3`, disabled `opacity-60`): State (`StateSelect select-ghost-md tooltip`), Assignees (`MemberSelect multiple`, Placeholder „Add assignees“, Label nur bei ≤1), Priority, Created by (Avatar + Name; Intake-Bot-Nutzer `*-intake` als „Plane“), Start date („Add start date“, `maxDate = target_date`), Due date („Add due date“, `minDate = start_date`, überfällig rot), Estimate (nur wenn Projekt-Schätzung aktiv, Placeholder „None“), Modules (wenn `module_view`), Cycle (wenn `cycle_view`), Parent (`IssueParentSelectRoot`), Labels (`IssueLabel`). |
| `error.tsx` | `IssuePeekOverviewError` | Schließen-Button + `EmptyState` (Bild `app/assets/empty-state/issue.svg`): „Work item does not exist“ / „The work item you are looking for does not exist, has been archived, or has been deleted.“ |
| `loader.tsx` | `IssuePeekOverviewLoader` | Skeleton (Kopf 30 px-Blöcke, Titel/Beschreibung-Zeilen 15 px, Sub-Issues, 2 Attachment-Kacheln 250×50, 6 Property-Zeilen 150×25). |
| `peek-overviews.tsx` | `HomePeekOverviewsRoot` | Rendert Peek nur, wenn ein Peek gesetzt ist (Home-Seite). |
| `index.ts` | Barrel | `root`. |
| `../issue-update-status.tsx` | `NameDescriptionUpdateStatus` | „Saving...“ mit drehendem `RefreshOutline 3.5` bzw. „Saved“ (`text-13 text-tertiary`, `fade-in/fade-out`). |
| `../issue-type-switcher.tsx` | `IssueTypeSwitcher` | CE: nur Identifier (EE: Work-Item-Typ-Wechsel → neu bauen, s. 5). |

### 2.13 Work-Item-Detailseite (`apps/web/components/issues/issue-detail/`)

| Datei | Export | Zweck / Verhalten |
|---|---|---|
| `root.tsx` | `IssueDetailRoot`, Typen `TIssueOperations`, `TIssueDetailRoot` | Seite `/{ws}/browse/{IDENT}-{seq}/` bzw. Archiv. Nicht gefunden → `EmptyState` (Bild `issue.svg`) „Work item does not exist“ / „The work item you are looking for does not exist, has been archived, or has been deleted.“, Button „View other work items“ → `/{ws}/projects/{pid}/issues`. Layout: links Hauptinhalt (`h-full w-full space-y-6 overflow-y-auto px-9 py-5`), rechts Sidebar (`fixed right-0 z-[5] h-full w-full min-w-[300px] border-l border-subtle bg-surface-1 sm:w-1/2 md:relative md:w-1/4 lg:min-w-80 xl:min-w-96`; eingeklappt via `issueDetailSidebarCollapsed` → `right: -100vw`). Rendert zusätzlich `IssuePeekOverview` (für Sub-Issues/Relationen). `issueOperations`: fetch, update (Toast „Error!“/„Work item update failed“), remove (Archiv-Store bei archiviert; Toast „Work item deleted successfully“ / „… delete failed“), archive, addCycleToIssue, addIssueToCycle (Fehler „Work item could not be added to the cycle. Please try again.“), removeIssueFromCycle / removeIssueFromModule (Promise-Toasts „Removing work item from the cycle|module“ → „…removed … successfully.“ / „…could not be removed…“), changeModulesInIssue. Edit-Recht ADMIN/MEMBER; Sidebar zusätzlich nicht im Archiv. |
| `main-content.tsx` | `IssueMainContent` | Reihenfolge: Parent-Chip (`IssueParentDetail`) → Kopfzeile (Identifier via `IssueTypeSwitcher` + Speicherstatus) → Titel (`IssueTitleInput`) → Beschreibung (`DescriptionInput`, `containerClassName "-ml-6 border-none p-0! pl-6!"`) → Reaktionen + Versionsverlauf (`DescriptionVersionsRoot`, nur editierbar) → Widgets (`IssueDetailWidgets`, `renderWidgetModals = !peekAktiv`) → bei Fensterbreite < 768 px die Properties (`PeekOverviewProperties`) inline → Activity (`IssueActivity`). Reload-Schutz beim Speichern; „Saved“ nach 2 s. |
| `sidebar.tsx` | `IssueDetailsSidebar` | „Properties“ (`h5 mt-5 text-body-xs-medium`, `px-6`), Liste `space-y-2.5` (nicht editierbar `opacity-60`): State, Assignees, Priority, Created by (Avatar + Name, `px-2`), Start date, Due date, Estimate (nur `areEstimateEnabledByProjectId(projectId)`), Modules (`module_view`), Cycle (`cycle_view`), Parent, Labels. Gleiche Komponenten wie Peek (Variante `select-ghost-md`). |
| `issue-detail-quick-actions.tsx` | `IssueDetailQuickActions` | Kopfaktionen der Detailseite: Subscribe (nicht archiviert), Copy link (kopiert **absolute** URL `origin + link`, Toast „Link copied!“ / „Copied to clipboard“), `WorkItemDetailQuickActions`. Delete → Weiterleitung `/{ws}/projects/{pid}/issues` (bzw. `/archives/issues`); Archive → Weiterleitung Issues-Liste (Fehler `issue.archive.failed.message`); Restore → Toast + Weiterleitung zum Work-Item. |
| `issue-identifier.tsx` | `IssueIdentifier` | `"<IDENT>-<seq>"` aus Store (`issueId`) oder Props (`projectIdentifier`, `issueSequenceId`); ausgeblendet wenn `displayProperties.key === false`. |
| `identifier-text.tsx` | `IdentifierText` | Button-Text (`text-12 font-medium whitespace-nowrap`), Größen `xs`=`text-caption-sm-regular`, `sm`=`text-caption-sm-medium`, `md`=`text-caption-md-medium`, `lg`=`text-caption-lg-medium`; Varianten `default/tertiary`=`text-tertiary`, `secondary`, `primary`, `primary-subtle`=`text-primary/80`, `success`. Optional Klick-zum-Kopieren (Tooltip „Click to copy“, Toast „Work item ID copied to clipboard“). |
| `subscription.tsx` | `IssueSubscription` | Button sekundär md: `SubscribeOutline` + „Subscribe“ bzw. `UnsubscribeOutline` + „Unsubscribe“ (Text ab `sm` sichtbar), „Loading“ während Request; disabled ohne ADMIN/MEMBER. Solange Status unbekannt: Skeleton 106×28. Toasts „Work item subscribed successfully“ / „Work item unsubscribed successfully“ / „Some error occurred. Please try again.“ |
| `cycle-select.tsx` | `IssueCycleSelect` | `CycleSelect select-ghost-md`, Placeholder „No cycle“, `clearable` (Zeile „No cycle“), deaktiviert während Update; setzen → `addCycleToIssue`, leeren → `removeIssueFromCycle(oldCycleId)`. |
| `module-select.tsx` | `IssueModuleSelect` | `ModuleSelect multiple`, Placeholder „No module“; Änderungen werden **serialisiert** (Promise-Queue), Diff gegen aktuellen Store-Stand → `changeModulesInIssue(add, remove)`; Fehler geloggt. |
| `parent-select.tsx` | `IssueParentSelect` | Button (`rounded-sm px-2 py-0.5 hover:bg-layer-transparent-hover`, aktiv `bg-layer-transparent-selected`): mit Parent → Identifier-Link (neuer Tab, Tooltip „Title: <Name>“) + „×“ (Tooltip „Remove“, `hover:text-danger-primary`) ; ohne → „Add parent work item“ (`text-placeholder`); Edit-Stift bei Hover. Öffnet `ParentIssuesListModal` (Store `isParentIssueModalOpen === issueId`). |
| `../parent-select-root.tsx` | `IssueParentSelectRoot` | Setzen: `update({parent_id})` → `fetch` → `fetchSubIssues(neuerParent)` → Modal zu. Entfernen: `removeSubIssue(parent, issue)` mit Sub-Issue-Loader-Flag, danach `fetchSubIssues(parent)`; Fehler „Something went wrong“. |
| `../parent-issues-list-modal.tsx` | `ParentIssuesListModal` | Dialog md mit Combobox (Suche, 500 ms Debounce) → `projectService.projectIssuesSearch(ws, pid, {search, parent: true \| (Epic: epic: true), issue_id, workspace_search:false})`. Überschrift „Search results for "<q>" in project:“, Loader 4×40 px, Leerzustand `IssueSearchModalEmptyState`. Einträge: State-Farbpunkt 1.5 + Identifier + Name, rechts bei Hover Rakete-Icon-Link (neuer Tab). Auswahl → `onChange(issue)` und schließen. |
| `parent/root.tsx` | `IssueParentDetail` | Chip über dem Titel (`mb-5 w-min rounded-md border border-strong bg-layer-1 px-2.5 py-1 text-11`): State-Farbpunkt + Identifier + Name (erste 50 Zeichen); Klick → Epic: Navigation, sonst Peek. Menü „…“: Gruppe „Sibling work items“ (`IssueParentSiblings`), Eintrag (danger) „Remove parent work item“ → `update({parent_id:null})`. |
| `parent/siblings.tsx` | `IssueParentSiblings` | Lädt Kinder des Parents (`ISSUE_PARENT_CHILD_ISSUES_…`), listet alle außer aktuellem; „Loading“ / „No sibling work items“. |
| `parent/sibling-item.tsx` | `IssueParentSiblingItem` | `MenuLinkItem external` mit Identifier + Name. |
| `label/root.tsx` | `IssueLabel` | `LabelSelect select-ghost-md`, Placeholder „Add labels“, Projekt-Admins können aus der Suche neues Label anlegen; Inbox-Variante (`isInboxIssue`, `onLabelUpdate`). Fehler „Work item update failed“. |
| `relation-select.tsx` | `IssueRelationSelect` | Legacy-Relation-Feld (Chips `"<IDENT>-<seq>"` farbig je Typ, „×“ entfernt, Placeholder je Typ). Öffnet `ExistingIssuesListModal` mit `{issue_relation:true, issue_id}`, `workspaceLevelToggle`; leer → Toast „Please select at least one work item.“ |
| `links/create-update-link-modal.tsx` | `IssueLinkCreateUpdateModal` | Dialog md: Titel „Add link“/„Update link“; Felder „URL“ (Pflicht, Fehler „URL is invalid“, Placeholder „Type or paste a URL“) und „Display title“ (Hinweis „Optional“, Placeholder „What you'd like to see this link as“). URL ohne `http` → `http://` vorangestellt. Buttons „Cancel“ / „Add link“ („Adding link“) bzw. „Update link“ („Updating link“). |
| `links/link-item.tsx` | `IssueLinkItem` | Link-Kachel (`h-10 rounded-sm border-[0.5px] border-subtle bg-surface-2 px-3 hover:bg-layer-1`, Grid-Spalten `col-span-12 lg:6 xl:4 2xl:3 3xl:2`): Favicon (`metadata.favicon`) oder `LinkOutline`, Titel oder URL (+ `metadata.title` grau), Tooltip URL, „vor X“ (`calculateTimeAgo`), Kopieren (`CopyOutline`, Toast „Link copied!“), Menü „Edit“/„Delete“ (disabled ohne Recht). |
| `links/link-list.tsx` | `LinkList` | Spalte der `IssueLinkItem`s (genutzt in Widgets). |
| `links/root.tsx`, `links/links.tsx`, `links/link-detail.tsx` | `IssueLinkRoot`, `IssueLinkList`, `IssueLinkDetail` | **Legacy, nirgends eingebunden** (nur Barrel-Export). Toasttexte „Link created/updated/removed“ werden aber im Widget-Helper wiederverwendet (s. 2.14). |
| `reactions/issue.tsx` | `IssueReaction` | `EmojiReactionPicker` + `EmojiReactionGroup` (`@plane/blocks/emoji-reaction`, `mt-4`): je Emoji Zähler, eigene Reaktion hervorgehoben, Tooltip mit Nutzernamen; Klick toggelt; „+“ öffnet Picker (`bottom-start`). Emoji ↔ API-Format: Codepoints dezimal mit „-“ verbunden (`stringToEmoji`). Toasts „Reaction created successfully“ / „Reaction removed successfully“ / „Reaction creation failed“ / „Reaction remove failed“. Read-only im Archiv. |
| `reactions/issue-comment.tsx` | `IssueCommentReaction` | Gleiches für Kommentare (Remove ohne `await`). |
| `issue-activity/*` | s. 2.15 | Activity/Kommentar-Feed. |
| `index.ts`, `label/index.ts`, `links/index.ts`, `parent/index.ts`, `reactions/index.ts` | Barrels | – |

### 2.14 Detail-Widgets: Sub-Work-Items, Relations, Links, Attachments (`apps/web/components/issues/issue-detail-widgets/`, `.../attachment/`, `.../relations/`, `apps/web/components/relations/`)

**Rahmen**

| Datei | Export | Zweck / Verhalten |
|---|---|---|
| `root.tsx` | `IssueDetailWidgets` | Props `workspaceSlug, projectId, issueId, disabled, renderWidgetModals=true, issueServiceType (issues/epics), hideWidgets?: ("sub-work-items"\|"relations"\|"links"\|"attachments")[]`. Aufbau: Aktionsleiste → Collapsibles → (optional) Modals. |
| `action-buttons.tsx` | `IssueDetailWidgetActionButtons` | Button-Reihe (`flex flex-wrap gap-2`): „Add sub-work item“ (`ViewsOutline`), „Add relation“ (`RelationsOutline`), „Add link“ (`LinkOutline`), „Attach“ (`AttachOutline`). |
| `widget-button.tsx` | `IssueDetailWidgetButton` | Propel-Button sekundär md, Icon 3.5 + Titel `text-body-xs-medium`. |
| `issue-detail-widget-collapsibles.tsx` | `IssueDetailWidgetCollapsibles` | Zeigt nur Sektionen mit Inhalt: Sub-Issues (≥1), Relations (Anzahl > 0), Links (`link_count > 0`), Attachments (Anzahl > 0 oder laufende Uploads). Offen/zu-Zustand im Store `openWidgets` / `toggleOpenWidget`. |
| `issue-detail-widget-modals.tsx` | `IssueDetailWidgetModals` | Zentrale Modals: Link-Modal; Create-Modal für Sub-Issue (`data {parent_id, project_id}`, `isProjectSelectionDisabled`, nach Erstellen `addSubIssue(parent,[id])`); Existing-Modal für Sub-Issues (`searchParams {sub_issue:true, issue_id: parent}`); Existing-Modal für Relationen (`{issue_relation:true, issue_id}`, `workspaceLevelToggle`; leer → Toast „Please select at least one work item.“; danach `createRelation(ws,pid,id,relationKey,ids)`). Beim Schließen `setLastWidgetAction(<widget>)` (öffnet Widget nach Aktion). |

**Sub-Work-Items**

| Datei | Export | Zweck / Verhalten |
|---|---|---|
| `sub-issues/root.tsx` | `SubIssuesCollapsible` | `Collapsible` mit Titel und (nur offen) Aktionen. |
| `sub-issues/title.tsx` | `SubIssuesCollapsibleTitle` | „Sub-work items“ (bei Epics „Work item“), `CircularProgress md` (`success` bei 100 %, sonst `brand`), „<erledigt>/<gesamt> Done“ (erledigt = State-Gruppe completed). |
| `sub-issues/title-actions.tsx` | `SubWorkItemTitleActions` | Display-Filter (`SubIssueDisplayFilters`), Filter (`SubIssueFilters`, Felder `SUB_WORK_ITEM_AVAILABLE_FILTERS_FOR_WORK_ITEM_PAGE` = priority, state, issue_type, assignees, start_date, target_date), „+“-Menü. Klicks werden gestoppt (kein Auf-/Zuklappen). Filter-Toggle-Logik: Werte toggeln; Arrays (Custom-Datum) elementweise. |
| `sub-issues/display-filters.tsx` | `SubIssueDisplayFilters` | Trigger `PreferencesOutline 3.5` (aktiv `bg-accent-primary/20` + Punkt), Inhalt: Display Properties (key, assignee, start_date, due_date, priority, state), Group by (state, priority, assignees, None), Order by (-created_at, -updated_at, start_date, -priority). |
| `sub-issues/filters.tsx` | `SubIssueFilters` | Trigger `FilterOutline`, Suchfeld („Search“) + Legacy-Sektionen Priority, State group, State, Projects, Assignees, Start date, Due date (gemäß `availableFilters`), max-h 350 px. |
| `sub-issues/quick-action-button.tsx` | `SubIssuesActionButton` | Menü „Create new“ (`AddOutline`) → Create-Modal mit Parent; „Add existing“ (`WorkItemsOutline`) → Existing-Modal. |
| `sub-issues/content.tsx` | `SubIssuesCollapsibleContent` | Lädt Sub-Issues beim Mount (mit Loader-/Sichtbarkeits-Helfern `${parent}_root`, schützt gegen StrictMode-Doppelaufruf); rendert `SubIssuesListRoot`; Delete-Modal (`isSubIssue`) → `deleteSubIssue`; Update-Modal → `updateSubIssue(..., fromModal=true)`. |
| `sub-issues/helper.ts` | `useSubIssueOperations` | `copyLink` („Link copied!“ / „Sub-work item link copied to clipboard“), `fetchSubIssues` (Fehler „Sub-work items fetch failed“), `addSubIssue` („Sub-work items added successfully“ / „…add failed“), `updateSubIssue` („Sub-work item updated successfully“ / „Error updating sub-work item“), `removeSubIssue` (entfernt Parent-Beziehung; „Sub-work items removed successfully“ / „…remove failed“), `deleteSubIssue` (löscht Issue). Jeweils `issue_loader`-Flag. Bei Epics heißen Entitäten „Work item(s)“. |
| `sub-issues/issues-list/root.tsx` | `SubIssuesListRoot` | Gruppierung nur auf Root-Ebene (`displayFilters.group_by`); 0 gefilterte Treffer → `SectionEmptyState` (Icon `FilterOutline`) „You don't have sub-work items that match the filters you've applied.“ / „To see all sub-work items, clear all applied filters.“ + „Clear filters“ (`resetFilters`); bei Epics Varianten „…work items…“. |
| `sub-issues/issues-list/list-group.tsx` | `SubIssuesListGroup` | Ohne Gruppierung flache Liste; mit Gruppierung `Collapsible` (Icon, Name `text-13 font-medium`, Anzahl `text-placeholder`), Default offen. |
| `sub-issues/issues-list/list-item.tsx` | `SubIssuesListItem` | Zeile (`min-h-11 py-1 pr-2 hover:bg-surface-2`, Einrückung `spacingLeft` +22 px/Ebene): Chevron (nur bei eigenen Kindern, nicht für Root; während Laden drehendes `LinkOutline`), Identifier (Display-Property `key`), Name, Properties, Menü: „Edit work item“, „Copy work item link“, „Remove parent work item“ (bei Epics „Remove work item“), „Delete work item“ (Edit-Einträge nur mit Recht). Klick → Peek. |
| `sub-issues/issues-list/properties.tsx` | `SubIssuesListItemProperties` | State, Priority, Datumsbereich bzw. Start/Due (`pill-sm`), Assignees (`avatar-group-sm`/`pill-sm`), jeweils per Display-Property; Änderungen über `updateSubIssue`. |
| `sub-issues/index.ts` | Barrel | – |

**Relations**

| Datei | Export | Zweck / Verhalten |
|---|---|---|
| `apps/web/components/relations/index.tsx` | `ISSUE_RELATION_OPTIONS`, `useTimeLineRelationOptions` | CE-Typen: `relates_to` („Relates to“, `RelatesToOutline`, `bg-layer-1 text-secondary`, Placeholder „Add related work items“), `duplicate` („Duplicate of“, `DuplicateOfOutline`), `blocked_by` („Blocked by“, `BlockingOutline`, `bg-danger-subtle text-danger-primary`), `blocking` („Blocking“, `CloseCircleOutline`, `bg-yellow-500/20 text-yellow-700`). i18n kennt zusätzlich `start_before`, `start_after`, `finish_before`, `finish_after`, `implements`, `implemented_by` (Bezahl-Editionen). |
| `relations/root.tsx` | `RelationsCollapsible` | Titel „Relations <Anzahl>“, Aktion „+“ nur offen & editierbar. |
| `relations/title.tsx` | `RelationsCollapsibleTitle` | Anzahl `getRelationCountByIssueId(issueId, options)` (`text-14 text-tertiary`). |
| `relations/quick-action-button.tsx` | `RelationActionButton` | Menü mit allen Relationstypen (Icon 12 + Label) → `setRelationKey` + `toggleRelationModal(issueId, key)`. |
| `relations/content.tsx` | `RelationsCollapsibleContent`, Typ `TRelationObject` | Je Typ mit Einträgen ein verschachteltes `Collapsible` (`defaultOpen`, Icon-Badge mit Typ-Farbe, Label `text-13 font-medium`) mit `RelationIssueList`. Edit-Modal (Issue bzw. Epic-Modal), Delete-Modal: entfernt **zuerst** die Relation und löscht dann das Issue/Epic. |
| `relations/helper.tsx` | `useRelationOperations` | `copyLink` („Work item link copied to clipboard“ / „Epic …“), `update` („Work item updated successfully“ / „…update failed“), `remove` (löschen). |
| `../relations/issue-list.tsx` | `RelationIssueList` | Liste. |
| `../relations/issue-list-item.tsx` | `RelationIssueListItem` | Zeile (`min-h-11 px-1.5 py-1 hover:bg-surface-2`): Platzhalter 20 px, Identifier, Name, Properties (`RelationIssueProperty`), Menü „Edit“, „Copy link“, „Remove relation“, „Delete“. Klick: Epic → neuer Tab, sonst Peek. |
| `../relations/properties.tsx` | `RelationIssueProperty` | State, Priority, Assignees (`pill-sm` / `avatar-group-sm`). |

**Links**

| Datei | Export | Zweck / Verhalten |
|---|---|---|
| `links/root.tsx` | `LinksCollapsible` | Titel „Links <link_count>“, Aktion „+“. |
| `links/title.tsx` | `IssueLinksCollapsibleTitle` | – |
| `links/content.tsx` | `IssueLinksCollapsibleContent` | `LinkList` (s. 2.13). |
| `links/helper.tsx` | `useLinkOperations` | create/update/remove mit Toasts „Link created“ / „The link has been successfully created“, „Link not created“ / Serverfehler `error.data.error` oder „The link could not be created“, analog updated/removed. |
| `links/quick-action-button.tsx` | `IssueLinksActionButton` | Öffnet Link-Modal (`toggleIssueLinkModal(true)`). |

**Attachments**

| Datei | Export | Zweck / Verhalten |
|---|---|---|
| `attachments/root.tsx` | `AttachmentsCollapsible` | Titel „Attachments <attachment_count>“, Aktion „+“ (Upload). |
| `attachments/title.tsx` | `IssueAttachmentsCollapsibleTitle` | – |
| `attachments/content.tsx` | `IssueAttachmentsCollapsibleContent` | `IssueAttachmentItemList`. |
| `attachments/helper.tsx` | `useAttachmentOperations`, Typen | `create(file)` mit Promise-Toast „Uploading attachment...“ → „Attachment uploaded“ / „The attachment has been successfully uploaded“ bzw. „Attachment not uploaded“; `remove(id)` → „Attachment removed“ / „The attachment has been successfully removed“ bzw. „Attachment not removed“ / „The Attachment could not be removed“. Snapshot `uploadStatus` (Fortschritt je Upload). |
| `attachments/quick-action-button.tsx` | `IssueAttachmentActionButton` | Dropzone-Button (1 Datei, `maxSize = instance.config.file_size_limit ?? 5 MB`); Fehler „Only one file can be uploaded at a time.“ / „File must be of <N>MB or less in size.“ / „File could not be attached. Try uploading again.“; danach Activity neu laden + `setLastWidgetAction("attachments")`. |
| `../attachment/attachment-item-list.tsx` | `IssueAttachmentItemList` | Liste + Dropzone über der Liste (Drag-Overlay `bg-surface-2/75`, Box `border-dashed`, `UploadOutline 7` + „Drag and drop anywhere to upload“; bei <3 Einträgen `min-h-[200px]`). Upload-Zeilen zuerst. |
| `../attachment/attachment-list-item.tsx` | `IssueAttachmentsListItem` | Zeile `h-11 px-3 hover:bg-surface-2`: Datei-Icon (nach Endung, 18 px), „<name>.<ext>“, Punkt, Größe (`convertBytesToSize`), Avatar Uploader (Tooltip „<Name> uploaded on <Datum>“), Menü „Delete“; Klick öffnet Datei in neuem Tab. |
| `../attachment/attachment-list-upload-item.tsx` | `IssueAttachmentsUploadItem` | Upload-Zeile (`bg-surface-2 pl-9`), `CircularProgress` + „<n>% done“. |
| `../attachment/delete-attachment-modal.tsx` | `IssueAttachmentDeleteModal` | `ConfirmDialog` „Delete attachment“, Text „Are you sure you want to delete attachment- **<name>**? This attachment will be permanently removed. This action cannot be undone.“ |
| `../attachment/root.tsx`, `attachment-upload.tsx`, `attachments-list.tsx`, `attachment-detail.tsx`, `attachment-upload-details.tsx` | `IssueAttachmentRoot`, `IssueAttachmentUpload`, `IssueAttachmentsList`, `IssueAttachmentsDetail`, `IssueAttachmentsUploadDetails` | Kachel-Variante (Grid `sm:2 xl:3 2xl:4` Spalten, Kacheln `h-[60px] rounded-md border-2`), Upload-Kachel „Click or drag a file here“ / „Drop here...“ / „Uploading...“ / „Invalid file type or size (max N MB)“; Datei-Kachel mit Name (10 Zeichen), Info-Tooltip, Typ/Größe, „×“ löschen. **Nur von Intake verwendet** (`apps/web/components/inbox/content/issue-root.tsx`). |
| `attachments/index.ts`, `links/index.ts`, `relations/index.ts`, `index.ts`, `../attachment/index.ts` | Barrels | – |

### 2.15 Activity-Feed & Kommentare (`apps/web/components/issues/issue-detail/issue-activity/`, `apps/web/components/comments/`)

**Activity-Rahmen**

| Datei | Export | Zweck / Verhalten |
|---|---|---|
| `issue-activity/root.tsx` | `IssueActivity`, Typ `TActivityOperations` | Kopf „Activity“ (`text-h5-medium text-primary`) + rechts Sortier-Button und Filter-Menü. Filter in **localStorage** `issue_activity_filters` (Default `ACTIVITY, COMMENT, STATE, ASSIGNEE`; mindestens einer bleibt aktiv), Sortierung in localStorage `activity_sort_order` (Default `asc`). Kommentar-Eingabe (`CommentCreate showToolbarInitially`) **unten** bei `asc`, **oben** bei `desc`; ausgeblendet wenn `disabled` (Archiv). Access-Specifier (intern/öffentlich) nur wenn `project.anchor` gesetzt (Projekt ist veröffentlicht, s. Space-Bereich). |
| `issue-activity/activity-comment-root.tsx` | `IssueActivityCommentRoot` | Holt `getActivityAndCommentsByIssueId(issueId, sortOrder)`; ohne Daten → `IssueActivityLoader`; leer → nichts. Filtert per `filterActivityOnSelectedFilters` (Einträge mit `activity_type === "DEFAULT"` immer sichtbar). `COMMENT` → `CommentCard` (`showCopyLinkOption` außer Intake, `enableReplies`), Typen aus `BASE_ACTIVITY_FILTER_TYPES` (ACTIVITY, STATE, ASSIGNEE, DEFAULT) → `IssueActivityItem`. `ends` = top/bottom für Zeitleistenlinie. |
| `issue-activity/sort-root.tsx` | `ActivitySortRoot` | `IconButton tertiary sm` (`SortAscendingOutline`/`SortDescendingOutline`, `aria-label` „Sort“). |
| `issue-activity/filter-root.tsx` | `ActivityFilterRoot` | Optionen `ACTIVITY_FILTER_TYPE_OPTIONS`: „Updates“ (ACTIVITY), „Comments“ (COMMENT), „State“ (STATE), „Assignee“ (ASSIGNEE). |
| `issue-activity/activity-filter.tsx` | `ActivityFilter` | Menü mit `MenuCheckboxItem`s; Trigger `IconButton tertiary sm FilterOutline`; Punkt (`h-2 w-2 bg-accent-primary`) wenn nicht alle Filter aktiv. |
| `issue-activity/loader.tsx` | `IssueActivityLoader` | 3 Skeleton-Einträge (28×28 + 2–3 Zeilen). |
| `issue-activity/helper.tsx` | `useWorkItemCommentOperations` | `copyCommentLink` (`<link>#comment-<id>`, „Comment link copied to clipboard“), `createComment` („Comment created successfully“ / „Comment creation failed. Please try again later.“), `updateComment`, `removeComment`, `uploadCommentAsset` (`EFileAssetType.COMMENT_DESCRIPTION`), `duplicateCommentAsset`, `addCommentReaction`/`deleteCommentReaction`/`react`, `reactionIds`, `userReactions`, `getReactionUsers` (Namen via `formatTextList`). |
| `issue-activity/index.ts` | Barrel | – |
| `activity/activity-list.tsx` | `IssueActivityItem` | Switch über `activity.field` (s. Tabelle unten). |
| `activity/actions/helpers/activity-block.tsx` | `IssueActivityBlockComponent` | Eintrag: vertikale Linie (`left-[13px] w-px bg-layer-3`), Icon-Kachel 28×28 (`rounded-lg border border-subtle bg-layer-2 shadow-raised-100`, Default `HierarchyOutline`), Text `text-caption-sm-regular text-secondary`: Akteur (Link `/{ws}/profile/{actorId}`, `font-medium text-primary hover:underline`; bei Erstellung `IssueCreatorDisplay`), Inhalt, relative Zeit (`calculateTimeAgo`, Tooltip „<Datum>, <Uhrzeit>“). |
| `activity/actions/helpers/issue-user.tsx` | `IssueUser` | Akteur-Link bzw. `customUserName`. |
| `activity/actions/helpers/issue-creator.tsx` | `IssueCreatorDisplay` | Ersteller (Fallback „Plane“). |
| `activity/actions/helpers/issue-link.tsx` | `IssueLink` | Link „<IDENT>-<seq> <Name>“ (neuer Tab) bzw. „Work items“ + Tooltip „This work item has been deleted“. |
| `activity/actions/helpers/activity.ts` | `getRelationActivityContent` | Texte für Relationen (s. unten). |
| `activity/actions/label-activity-chip.tsx` | `LabelActivityChip` | Farbpunkt 1.5 + Labelname, Tooltip. |
| `activity/actions/index.ts` | Barrel | – |

**Activity-Typen (`activity.field` → Komponente, Icon, Text)**

| field | Datei | Icon | Text (en, `showIssue=false`) |
|---|---|---|---|
| `null` | `actions/default.tsx` | `WorkItemsOutline` | „created the work item.“ bzw. „created the work item via **<Source>**.“ (Intake-Quelle ≠ IN_APP); sonst „deleted a work item.“ |
| `name` | `actions/name.tsx` | `TextOutline` | „set the name to <neu>.“ |
| `description` | `actions/description.tsx` | `AlignLeftOutline` | „updated the description.“ |
| `state` | `actions/state.tsx` | `StateOutline` | „set the state to **<neu>**.“ |
| `assignees` | `actions/assignee.tsx` | `MembersOutline` | „added a new assignee <Name-Link>.“ / „removed the assignee <Name-Link>.“ |
| `priority` | `actions/priority.tsx` | `PriorityOutline` | „set the priority to **<neu>**.“ |
| `estimate_points`, `estimate_categories`, `estimate_point` | `actions/estimate.tsx` | `EstimateOutline` | „set the estimate point to <neu>.“ / „removed the estimate point<alt>.“ |
| `parent` | `actions/parent.tsx` | `ParentOutline` | „set the parent to **<neu>**.“ / „removed the parent **<alt>**.“ |
| `relates_to`, `duplicate`, `blocked_by`, `blocking` | `actions/relation.tsx` | Relationstyp-Icon | relates_to: „marked that this work item relates to **X**.“ / „removed the relation from **X**.“; duplicate: „marked this work item as duplicate of **X**.“ / „removed this work item as a duplicate of **X**.“; blocked_by: „marked this work item is being blocked by **X**.“ / „removed this work item being blocked by work item **X**.“; blocking: „marked this work item is blocking work item **X**.“ / „removed the blocking work item **X**.“ |
| `start_date` | `actions/start_date.tsx` | `CalendarOutline` | „set the start date to **<Datum>**.“ / „removed the start date .“ |
| `target_date` | `actions/target_date.tsx` | `CalendarOutline` | „set the due date to **<Datum>**.“ / „removed the due date .“ |
| `cycles` | `actions/cycle.tsx` | `CyclesOutline` | created: „added this work item to the cycle <Link>“; updated: „set the cycle to <Link>“; sonst „removed the work item from the cycle <Link>“ (zeigt im Original `new_value` statt `old_value`). Link `/{ws}/projects/{pid}/cycles/{id}`. |
| `modules` | `actions/module.tsx` | `ModuleOutline` | „added this work item to the module …“ / „set the module to …“ / „removed the work item from the module <old>“. |
| `labels` | `actions/label.tsx` | `LabelsOutline` | „added a new label <Chip>“ / „removed the label <Chip>“ (ohne Punkt). |
| `link` | `actions/link.tsx` | `ChatOutline` | „added link.“ / „updated the link.“ / „removed this link.“ (Wort „link“ verlinkt URL). |
| `attachment` | `actions/attachment.tsx` | `AttachOutline` | „uploaded a new attachment.“ / „removed an attachment.“ |
| `archived_at` | `actions/archived-at.tsx` | `RefreshOutline` (restore) / `ArchiveOutline` | „restored the work item.“ / „archived the work item.“ (bei Auto-Archiv Akteur „Plane“). |
| `intake`, `inbox` | `actions/inbox.tsx` | `IntakeOutline` | `new_value` −1: „declined this work item from intake.“; 0: „snoozed this work item.“; 1: „accepted this work item from intake.“; 2: „declined this work item from intake by marking a duplicate work item.“; sonst „updated intake work item status.“ |
| sonst | – | – | nicht gerendert |

**Kommentare (`apps/web/components/comments/`)**

| Datei | Export | Zweck / Verhalten |
|---|---|---|
| `comments.tsx` | `CommentsWrapper` | Generische Kommentarliste (Eingabe oben, Liste darunter). **In CE nirgends importiert** (außerhalb von `apps/web/components/comments/` werden nur `CommentCreate` und `CommentCard` verwendet, von `issue-activity/root.tsx` und `issue-activity/activity-comment-root.tsx`) – Erweiterungspunkt für Kommentare an weiteren Entitäten. |
| `comment-block.tsx` | `CommentBlock` | Zeitleisten-Eintrag: Linie, Icon-Kachel `ReplyOutline`, Karte `mb-2 rounded-lg border border-subtle bg-layer-2 p-3 text-body-sm-regular shadow-raised-100`; DOM-`id` = Kommentar-ID. |
| `comment-create.tsx` | `CommentCreate` | `LiteTextEditor` (Toolbar, Access-Umschalter, `small-font`, `p-2`), Enter (ohne Shift/Ctrl/Meta) sendet, wenn nicht leer und Editor bereit (Uploads fertig); nach Senden Reset `<p></p>`; hochgeladene Assets werden danach per Bulk-Status-Update (`updateBulkProjectAssetsUploadStatus` bzw. Workspace-Variante) bestätigt. Default-Access `INTERNAL`. Mobil sticky unten. |
| `card/root.tsx` | `CommentCard` | `CommentBlock` + `CommentCardDisplay` + `CommentQuickActions`; Prop `enableReplies` wird in CE **nicht ausgewertet** (Antworten = Bezahlfeature, i18n `issue.comments.replies.*` vorhanden). |
| `card/display.tsx` | `CommentCardDisplay` | Kopf: Avatar 2xs, Name (Bots „<Vorname>Bot“), „commented <vor X>“ (+ „ (edited)“, Tooltip „<Datum> at <Zeit>“, Delay 200). Rechts (nicht disabled): Emoji-Picker-Button + Quick-Actions. Access-Icon oben rechts (`LockOutline` intern / `GlobeOutline` öffentlich) wenn aktiviert. Body: read-only `LiteTextEditor`; Hash-Link `#comment-<id>` scrollt hin und hebt 8 s mit `border-accent-strong` hervor. Reaktionen darunter (nur wenn vorhanden und nicht disabled). |
| `card/edit-form.tsx` | `CommentCardEditForm` | Inline-Editor; Enter speichert; Buttons ✓ (`TickOutline`, `border-success-subtle bg-success-subtle`, nur wenn nicht leer) und ✕ (`CloseOutline`, `bg-danger-subtle`, verwirft). |
| `quick-actions.tsx` | `CommentQuickActions` | Menü (`IconButton ghost xs`): „Edit“ (nur Autor), „Copy link“ (wenn erlaubt), „Switch to public comment“/„Switch to private comment“ (wenn Access-Specifier aktiv; toggelt `access` INTERNAL↔EXTERNAL), „Delete“ (nur Autor). Leer → kein Button. |
| `comment-reaction.tsx` | `CommentReactions` | Reaktionsgruppe; „+“ nur wenn bereits Reaktionen vorhanden. |
| `index.ts` | Barrel | – |

### 2.16 Create/Edit-Modal (`apps/web/components/issues/issue-modal/`) und Epic-Modal (`apps/web/components/epic-modal/`)

| Datei | Export | Zweck / Verhalten |
|---|---|---|
| `modal.tsx` | `CreateUpdateIssueModal`, Typ `IssuesModalProps` | Props: `data?, isOpen, onClose, beforeFormSubmit?, onSubmit?, withDraftIssueWrapper=true, storeType?, isDraft=false, fetchIssueDetails=true, moveToIssue=false, modalTitle?, primaryButtonText?, isProjectSelectionDisabled=false, templateId?, allowedProjectIds?, showActionItemsOnUpdate=false`. Vorbelegung aus Route: `cycle_id = data.cycle_id ?? cycleId`, `module_ids = data.module_ids ?? [moduleId]`. Nicht offen → nichts gerendert. |
| `provider.tsx` | `IssueModalProvider` | Context-Werte (CE): `allowedProjectIds = props.allowedProjectIds ?? Projekte mit Create-Recht (user.projectsWithCreatePermissions)`, `selectedParentIssue` (State); **Stubs**: `workItemTemplateId=null`, `isApplyingTemplate=false`, `issuePropertyValues={}`, `getIssueTypeIdOnProjectChange→null`, `getActiveAdditionalPropertiesLength→0`, `handlePropertyValuesValidation→true`, `handleCreateUpdatePropertyValues`, `handleProjectEntitiesFetch`, `handleTemplateChange`, `handleConvert`, `handleCreateSubWorkItem` → no-op. In Bezahl-Editionen: Vorlagen, Work-Item-Typen mit Custom Properties, Konvertierung, Sub-Item-Erzeugung aus Vorlage. |
| `context/issue-modal-context.tsx` | `IssueModalContext`, Typen | Vertragsdefinition aller obigen Hooks (`TPropertyValuesValidationProps`, `TCreateUpdatePropertyValuesProps`, `THandleTemplateChangeProps` …). |
| `context/index.ts` | Barrel | – |
| `base.tsx` | `CreateUpdateIssueModalBase` | Store-Typ: EPIC → PROJECT. `projectId = data.project_id ?? routeProjectId ?? Projekt aus workItem-Identifier im Format „ABC-12“`. Beim Öffnen: Beschreibung laden (`fetchIssue`, wenn `data.id`/`sourceIssueId` und `fetchIssueDetails`), sonst `data.description_html ?? "<p></p>"`; aktives Projekt = `data.project_id` > `projectId` > erstes erlaubtes. **Kein Rendern ohne erlaubte Projekte.** Dialog `size lg`, `disablePointerDismissal` (Klick außerhalb schließt nicht). **Create**: Draft → Draft-Store; Cycle/Modul-Store aber anderer Cycle/Modul → Projekt-Store; sonst Store-`createIssue`. Danach Bulk-Asset-Status, ggf. `addIssueToCycle` (+ `fetchCycleDetails`) und `changeModulesInIssue` (+ `fetchModuleDetails`), Property-Values (Stub), Sub-Item (Stub). Toast „Success“ + „Work item created successfully“ / „Draft created“ inkl. Toast-Aktionen; Fehler „Error“ + `error.error` bzw. „Work item creation failed“/„Draft creation failed“. **Create more**: Modal bleibt offen, Fokus auf Titel. **Update**: Draft-Store oder Store-`updateIssue`, dann sequentiell Cycle-Wechsel (remove/add), Modul-Diff, Property-Values; Toast „Work item updated successfully“ / „Work item could not be updated“; schließt. `handleClose(saveAsDraft)`: legt bei Änderungen ohne `data` einen Entwurf an. |
| `form.tsx` | `IssueFormRoot`, Typ `IssueFormProps` | `react-hook-form` mit `DEFAULT_WORK_ITEM_FORM_VALUES` (`project_id:"", type_id:null, name:"", description_html:"", estimate_point:null, state_id:"", parent_id:null, priority:"none", assignee_ids:[], label_ids:[], cycle_id:null, module_ids:null, start_date:null, target_date:null`). Kopf: Titel „Create new work item“ / „Create a draft“ / „Update“; Projekt-Pill (`IssueProjectSelect`, deaktiviert bei Edit/Kopie/`isProjectSelectionDisabled`); Parent-Tag; Titel-Input. Body (scrollbar): Beschreibung. Fuß (fix): Default-Properties. Aktionen: „Create more“ (Switch sm, nur Create), „Discard“ (nur wenn Editor bereit, sonst Toast „Editor is still processing changes. Please wait before proceeding.“), Primär „Save“/„Save to Drafts“/„Update“ (Loading „Saving“/„Updating“), bei `moveToIssue` zusätzlich „Add to project“ (Draft → Projekt; Fehler „Failed to move work item to project. Please try again.“). Projektwechsel: Formular wird mit `getUpdateFormDataForReset` (projektspezifische Felder geleert) zurückgesetzt; Cycles des neuen Projekts nachgeladen. Edit sendet nur geänderte Felder (`getChangedIssuefields`) + `project_id`, `id`, `description_html`, `type_id`. Submit blockiert, wenn Editor nicht bereit („Editor is not ready to discard changes“). Nach Submit Reset (bei Create-more mit Ausgangsdaten). `onChange` meldet Änderungen nur wenn Titel oder Beschreibung nicht leer (für Draft-Logik). Max-Höhe des Dialogs folgt Formularhöhe (ResizeObserver). |
| `draft-issue-layout.tsx` | `DraftIssueLayout` | Beim Schließen eines **neuen** Work Items mit relevanten Änderungen (bereinigt: leere Werte, `project_id`, `priority none`, leere Beschreibung ohne Bilder ignoriert) → `ConfirmIssueDiscard`; „Save to Drafts“ erstellt Workspace-Draft (Name leer → „Untitled“), Toast „Success!“ + „Draft created“ / „Work item could not be created. Please try again.“ |
| `../confirm-issue-discard.tsx` | `ConfirmIssueDiscard` | Dialog md: „Save this draft?“ / „You can save this work item to Drafts so you can come back to it later.“; Buttons „Discard“ (links), „Cancel“, „Save to Drafts“ („Saving“). |
| `components/project-select.tsx` | `IssueProjectSelect` | `ProjectSelect pill-md` gefiltert auf `allowedProjectIds`, Pflichtfeld. |
| `components/title-input.tsx` | `IssueTitleInput` | `Input size 2xl`, Placeholder „Title“, `autoFocus`; Validierung: Pflicht „Title is required“, nur Leerzeichen → gleich, max. 255 „Title should be less than 255 characters“ (Fehler `text-caption-sm-medium text-danger-primary`). |
| `components/parent-tag.tsx` | `IssueParentTag` | Chip (`rounded-sm bg-surface-2 p-2`): State-Farbpunkt, Identifier, Name (50 Zeichen), „×“. |
| `components/description-editor.tsx` | `IssueDescriptionEditor` | `RichTextEditor` (`id issue-modal-editor`, `min-h-[120px]`, Placeholder via `getDescriptionPlaceholderI18n`, Mention-Suche `workspaceService.searchEntity`, Upload `EFileAssetType.ISSUE_DESCRIPTION` bzw. `DRAFT_ISSUE_DESCRIPTION`), Enter-Shortcut des Editors → Submit-Button klicken; `Escape` schließt (wenn Editor bereit). Rahmen `rounded-lg border-[0.5px] border-subtle-1 bg-layer-2`. Ladezustand: Skeleton. **AI** (nur `instance.config.has_llm_configured`): „I'm feeling lucky“ (nur mit Titel; `aiService.createGptTask` „Generate a proper description for this work item.“; leer → „Work item title isn't informative enough…“, 429 → „You have reached the maximum number of requests of 50 requests per month per user.“) und „AI“-Popover (`GptAssistantPopover`, Antwort an Cursor einfügen). |
| `components/default-properties.tsx` | `IssueDefaultProperties` | Pill-Reihe (`pill-md`): State (leer → Default-State des Projekts angezeigt), Priority, Assignees (`avatar-group-md` wenn gesetzt, Placeholder „Assignees“), Labels („Labels“), Start date („Start date“, `CalendarOutline`, `maxDate`), Due date („Due date“, `minDate`), Cycle (wenn `cycle_view`, „Cycle“, clearable), Modules (wenn `module_view`, „Modules“), Estimate (wenn aktiviert, „Estimate“), Parent: ohne → Pill „Add parent“ (`ParentOutline`); mit → Pill mit Identifier + Menü „Change parent work item“ / „Remove parent work item“. `ParentIssuesListModal` (bei Edit eigenes Issue ausgeschlossen). Tab-Reihenfolge `ISSUE_FORM_TAB_INDICES` (name, description_html, feeling_lucky, state_id, priority, assignee_ids, label_ids, start_date, target_date, cycle_id, module_ids, estimate_point, parent_id, create_more, discard_button, draft_button, submit_button, project_id, remove_parent). |
| `components/index.ts` | Barrel | – |
| `apps/web/components/epic-modal/modal.tsx` | `CreateUpdateEpicModal` | **CE-Stub** (rendert nichts) – Epics sind Bezahlfeature. |
| `apps/web/components/epic-modal/index.ts` | Barrel | – |

### 2.17 Workspace-Entwürfe (`apps/web/components/issues/workspace-draft/`)

| Datei | Export | Zweck / Verhalten |
|---|---|---|
| `root.tsx` | `WorkspaceDraftIssuesRoot` | Seite „Drafts“: SWR `WORKSPACE_DRAFT_ISSUES_${ws}` → `fetchIssues(ws, "init-loader")`; Laden → 14 Skeleton-Zeilen; keine Projekte → „No project“-Empty-State; keine Entwürfe → `WorkspaceDraftEmptyState`; sonst Liste + „Load More ↓“ (`h-11 border-b pl-6 text-13 font-medium text-accent-primary hover:underline`, Cursor-Pagination `EDraftIssuePaginationType.NEXT`). |
| `draft-issue-block.tsx` | `DraftIssueBlock` | Zeile wie List-Block (`min-h-11 py-3 hover:bg-layer-transparent-hover`, Breakpoint `md`/`lg` je Sidebar): Projekt-Identifier (klick-kopierbar), Name (Tooltip), Properties, Quick-Actions. **Doppelklick** öffnet Bearbeiten. Menü: „Edit“, „Make a copy“ (Name „<name> (copy)“, `is_draft:true`), „Move to project“ (öffnet Modal mit `moveToIssue` → Button „Add to project“), „Delete“. Modal mit `storeType WORKSPACE_DRAFT`, `isDraft`, `fetchIssueDetails=false`. |
| `draft-issue-properties.tsx` | `DraftIssueProperties` | Reihenfolge: State, Priority, Labels, Start date, Due date, Assignees, Modules (`module_view`), Cycle (`cycle_view`), Estimate (wenn aktiviert); alle `pill-sm`, Updates via Draft-Store. |
| `quick-action.tsx` | `WorkspaceDraftIssueQuickActions` | „…“-Menü + Rechtsklick-Menü; Titel werden übersetzt (`edit`, `make_a_copy`, `move_to_project`, `delete`). |
| `empty-state.tsx` | `WorkspaceDraftEmptyState` | asset `draft`, „Half-written work items“ / „To try this out, start adding a work item and leave it mid-way or create your first draft below. 😉“, „Create draft work item“ (öffnet Modal im Draft-Modus; Workspace-ADMIN/MEMBER). |
| `loader.tsx` | `WorkspaceDraftIssuesLoader` | n × `ListLoaderItemRow`. |
| `delete-modal.tsx` | `WorkspaceDraftIssueDeleteIssueModal` | `ConfirmDialog` „Delete draft“ / „Are you sure you want to delete this draft? This can't be undone.“, Buttons „Delete“/„Deleting“, „Cancel“; nur Ersteller oder Projekt-Admin, sonst Toast „You don't have permission to perform this action.“; Erfolg „Success!“ + „Draft deleted“; Fehler „Failed to delete work item“. |
| `index.ts` | Barrel | – |

### 2.18 Weitere Einzeldateien in `apps/web/components/issues/`

| Datei | Export | Zweck / Verhalten |
|---|---|---|
| `header.tsx` | `IssuesHeader` | Kopf der Projekt-Work-Items: Breadcrumbs (Projekt → „Work Items“ mit `WorkItemsOutline`), `CountChip` mit Tooltip „There are N work item(s) in this project“, bei veröffentlichtem Projekt (`anchor`) Badge „Public“ (`rounded-sm bg-accent-primary/10 px-2.5 py-1 text-11 font-medium text-accent-primary`, Link auf Space-URL `${SPACE_BASE_URL||origin}${SPACE_BASE_PATH}/issues/${anchor}`, `NewTabOutline` bei Hover). Rechts (ab `md`): `HeaderFilters`; Primärbutton „Add work item“ (mobil „Work item“) → Create-Modal. |
| `filters.tsx` | `HeaderFilters` | Layout-Auswahl (ab `@4xl` Segment, darunter Mobil-Menü) mit allen 5 Layouts → `updateFilters(DISPLAY_FILTERS, {layout})`; Filter-Toggle; „Display“-Dropdown (`PreferencesOutline` als Mini-Icon) mit `DisplayFiltersSelection` (Optionen aus `ISSUE_STORE_TO_FILTERS_MAP[storeType]`); bei Create-Recht Button „Analytics“ (ab `md`, unter `@4xl` nur `BarOutline`) → `WorkItemsModal` (Analytics-Bereich). |
| `archived-issues-header.tsx` | `ArchivedIssuesHeader` | Archiv-Kopf: `ArchiveTabsList` (Tabs Work items/Cycles/Modules, anderer Bereich), Filter-Toggle, „Display“ (nur List-Optionen von `archived_issues`). |
| `archive-issue-modal.tsx` | `ArchiveIssueModal` | `ConfirmDialog variant primary`: Titel „Archive Work item <IDENT> <seq>“, Text „Are you sure you want to archive the work item? All your archived work items can be restored later.“, Buttons „Archive“/„Archiving“, „Cancel“; Toast „Archive success“ / „Your archives can be found in project archives.“ bzw. „Work item could not be archived. Please try again.“ |
| `delete-issue-modal.tsx` | `DeleteIssueModal` | `ConfirmDialog`: „Delete Work item“/„Delete Epic“, Text „Are you sure you want to delete work item **<IDENT>-<seq>** ? All of the data related to the work item will be permanently removed. This action cannot be undone.“. Clientseitige Prüfung: nur Ersteller oder Projekt-ADMIN, sonst Toast „You don't have permission to perform this action.“. Erfolg „Success!“ + „<Work item\|Sub-work item\|Epic> deleted successfully“; Server-Fehler „Only admin or creator can delete the …“ → Berechtigungs-Toast, sonst „Error“/„Failed to delete work item“. |
| `confirm-issue-discard.tsx` | `ConfirmIssueDiscard` | s. 2.16. |
| `create-issue-toast-action-items.tsx` | `useCreateIssueToastActions` | s. 2.7. |
| `title-input.tsx` | `IssueTitleInput` | Titel in Detail/Peek: `TextArea size 2xl surface inline autoResize`, max. 255, Placeholder „Work item title“; Speichern **1,5 s debounced** (`update({name})`), leerer Titel → zurück auf alten Wert; Trim beim Blur; Speichern beim Unmount bei offenen Änderungen; Zeichenzähler „n/255“ unten rechts nur bei Fokus (rot bei 0 oder >255); leer → „Title is required“. Read-only: `text-20 font-medium whitespace-pre-line`. |
| `issue-update-status.tsx` | `NameDescriptionUpdateStatus` | s. 2.12. |
| `issue-type-switcher.tsx` | `IssueTypeSwitcher` | s. 2.12 (CE-Stub). |
| `label.tsx` | `ViewIssueLabel` | Read-only Label-Anzeige: ≤ maxRender → je Label Chip (`rounded-md border border-strong px-2.5 py-1 text-11`, Farbpunkt, Tooltip „Label: <Name>“), sonst Sammel-Chip „N Labels“ (Tooltip „Labels: a, b“). |
| `layout-quick-actions.tsx` | `LayoutQuickActions` | „…“-Menü im Layout-Kopf (`IconButton tertiary md`): „Open in new tab“, „Copy link“ (`<ws>/projects/<pid>/issues|epics`, Toast „Link copied“ / „Work items link copied to clipboard.“) aus `useLayoutMenuItems` (`apps/web/components/common/quick-actions-helper.tsx`). |
| `parent-issues-list-modal.tsx` | `ParentIssuesListModal` | s. 2.13. |
| `parent-select-root.tsx` | `IssueParentSelectRoot` | s. 2.13. |
| `bulk-operations/root.tsx` | `IssueBulkOperationsRoot` | **CE-Upsell-Stub**: bei aktiver Auswahl Banner (sticky unten, `h-20`) „Change state, priority, and more for several work items at once. Save three minutes on an average per operation.“ + Button „Upgrade to One“ (Marketing-Link). Da `useBulkOperationStatus() === false`, ist Auswahl in CE nie aktiv → Banner faktisch unsichtbar. |
| `bulk-operations/index.ts` | Barrel | – |
| `preview-card/root.tsx` | `WorkItemPreviewCard` | Hover-Karte (`w-72 space-y-2`): Identifier (secondary) + State (Icon + Name `text-11 font-medium`), Name (`text-13 wrap-break-word`), Priority-Icon + Datum. |
| `preview-card/date.tsx` | `WorkItemPreviewCardDate` | „<Start> - <Ende>“ (`CalendarOutline`), nur Start (`StartDateOutline`) bzw. nur Ende (`DueDateOutline`); überfällig rot. |
| `preview-card/index.ts` | Barrel | – |

### 2.19 Dropdowns (`apps/web/components/dropdowns/`) und Block-Grundlage (`packages/blocks/src/property-select/`, `packages/blocks/src/select/`)

Die App-Dropdowns sind **dünne, store-gebundene Wrapper** um präsentationale Blocks aus `@plane/blocks/property-select`. Die Blocks basieren auf dem generischen, virtualisierten `Select` (`packages/blocks/src/select/select.tsx`, „Generic, virtualized entity picker built on propel's Combobox“) mit Sync- (`getValues: () => T[]`) und paginiertem Modus (`getValues: (params) => Promise<TPaginatedResponse<T[]>>`).

**Gemeinsame Select-Grundlagen**

| Aspekt | Wert | Quelle |
|---|---|---|
| Trigger-Varianten (`SelectVariant`) | `pill-sm`, `pill-md`, `pill-lg`, `icon-sm`, `icon-md`, `icon-lg`, `select-<ComboboxSize>`, `select-ghost-<ComboboxSize>`, `table-cell`, `breadcrumb`, `search-input`; Member zusätzlich `avatar-group-sm/md/lg` | `packages/blocks/src/select/types.ts`, `packages/blocks/src/property-select/member-select.tsx` |
| Pill-Größen | `sm`: `h-5 gap-1 px-1.5 py-1 text-caption-md-regular`; `md`: `h-6 gap-1 px-1.5 py-1 text-body-xs-regular`; `lg`: `h-7 gap-1 px-2 py-1 text-body-sm-regular`; Basis `rounded-md border border-subtle-1 bg-layer-2 text-secondary hover:border-strong hover:bg-layer-2-hover`; aktiv `border-strong bg-layer-2-active text-primary`; disabled `bg-layer-transparent text-disabled cursor-not-allowed` | `packages/blocks/src/pill-button/helper.tsx` |
| Trigger-Chrome | `breadcrumb` → propel `BreadcrumbTrigger`; `pill`/`table-cell` → `PillButtonContent`; `icon` → nur Prepend-Icon; `select`/`select-ghost` → Plane-Chrome analog propel `comboboxTriggerVariants` (Detail-Sidebar nutzt `select-ghost-md`) | `packages/blocks/src/select/trigger-chrome.tsx` |
| Suche | Debounce `SELECT_SEARCH_DEBOUNCE_MS = 300`; Sync-Modus filtert clientseitig über `getOptionSearchText` (Default Label) | `packages/blocks/src/select/select.constants.ts`, `packages/blocks/src/select/types.ts` |
| Zeilenhöhen | Option 28 px (`SELECT_OPTION_ROW_HEIGHT`), Menüzeile 32 px (`MENU_ROW_HEIGHT`), Menüliste `max-h-48 overflow-y-auto vertical-scrollbar scrollbar-sm p-1` | `packages/blocks/src/select/select.constants.ts` |
| Auswahlmarke | Einzelwahl: Häkchen am Zeilenende; Mehrfachwahl: Checkbox am Zeilenanfang; Auswahl wird standardmäßig oben angepinnt (`pinSelected`, bei State `false`) | `packages/blocks/src/select/types.ts`, `packages/blocks/src/property-select/state-select.tsx` |
| Virtualisierung | eigener `virtual-list-body.tsx`, Skeleton `skeleton.tsx`, Endlos-Laden `use-infinite-options.ts`, Tastatur überspringt deaktivierte Zeilen (`use-skip-disabled-rows.ts`) | `packages/blocks/src/select/` |
| Tooltip | optional `showTooltip` mit Überschrift (Property-Name) + Wert bzw. `tooltipEmptyContent` | `packages/blocks/src/property-select/date-select-shell.tsx` |

**App-Wrapper**

| Datei | Export | Props / Verhalten | Texte (en) |
|---|---|---|---|
| `state/state-select.tsx` | `StateSelect` | `projectId, value, onChange(stateId), variant, disabled, placeholder, onClose, className, tooltip, appendElement, testId, tabIndex`. Lädt Projekt-States beim ersten Öffnen (`fetchProjectStates`), Suche clientseitig. Block: Icon `StateGroupIcon` (Farbe, `percentage = order` für In-Progress-Füllgrad), `pinSelected=false` (Reihenfolge = Workflow-Reihenfolge), optional `showIdentifier`. CE-Hinweis im Code: EE verwendet paginierte „lite“-Ressource mit Workflow-Gating (`typeId`, `isForWorkItemCreation`, `scopedProjectIds`, `allowedStateIds`). | Placeholder „State“, Tooltip „State“ / leer „None“, Suche „Search states...“ |
| `priority/priority-select.tsx` | `PrioritySelect` | Block ohne Suche; Optionen `ISSUE_PRIORITIES` (urgent, high, medium, low, none) mit `PriorityIcon`, Label `t(key)`; leere Auswahl → `"none"`. | Placeholder „Priority“, Tooltip „Priority“ |
| `member/member-select.tsx` | `MemberSelect` | `multiple` oder single; `projectId` → Projektmitglieder, sonst Workspace-Mitglieder; `memberIds` (Einschränkung), `excludeIds`, `variant` (`MemberSelectVariant`), `showLabel`, `clearable`/`clearLabel` (single), `tooltip`. Aktueller Nutzer immer zuerst, Label „<Name> (You)“; suspendierte Mitglieder deaktiviert mit Badge „Suspended“. Suche über `display_name`, `first_name`, `last_name`. CE: kein paginierter EE-Scope. | Tooltip „Members“, Suche „Search members...“, Clear-Zeile „No assignee“ |
| `member/avatar.tsx` | `ButtonAvatars` | Mehrere IDs → `AvatarGroup` max. 2 + „+N“; eine ID → Einzelavatar (Tooltip optional); keine → Fallback-Icon `MembersOutline` (bzw. übergebenes `icon`). | – |
| `label/label-select.tsx` | `LabelSelect` | Projekt-Labels (Farbpunkt), Mehrfachwahl, Suche; **Projekt-ADMIN** kann Label direkt aus dem Suchbegriff anlegen (`createLabel`, Farbe `getRandomLabelColor`, danach ausgewählt). Unbekannte (nicht geladene) IDs bleiben in der Auswahl erhalten. CE-Hinweis: EE unterstützt Label-Scopes (work item / release / initiative / project). | Suche „Search labels...“, Button „Add "{name}" to labels“ (während Anlage „Adding "{name}"“ mit `LoadingOutline animate-spin`), ohne Recht „No matching labels“ (`px-2 py-1.5 text-body-xs-regular text-secondary`) |
| `cycle/cycle-select.tsx` | `CycleSelect` | Statusfilter Default `["current","upcoming","draft"]` – **abgeschlossene Cycles werden nie angeboten**; `clearable` Default `true`; `excludeIds`; `onChange(id \|\| null)`. | Clear „No cycle“, Suche „Search cycles...“ |
| `module/module-select.tsx` | `ModuleSelect` | single/multiple; unbekannte IDs bleiben erhalten. | Suche „Search modules...“ |
| `estimate/estimate-select.tsx` | `EstimateSelect` | Lädt Schätzpunkte lazy beim Öffnen, nur wenn Schätzung im Projekt aktiviert; System `TIME` → Anzeige `convertMinutesToHoursMinutesString`; Clear sendet `null`. | Tooltip „Estimates“, Clear „No estimate“, Suche „Search estimates...“ |
| `project/project-select.tsx` | `ProjectSelect` | `projectList: "joined" \| "all"`, `filterOption`, `excludeProjectId`, `resolveProject`; archivierte Projekte ausgeschlossen; Suche über Name **und** Identifier; Sortierung `sort_order`; Projekt-Logo + Identifier (`shared/project-identifier-element.tsx`). | Suche „Search projects...“ |
| `intake-state/intake-state-select.tsx` | `IntakeStateSelect` | genau eine Intake-State-Option; Default-Variante `select-ghost-md`. | – |
| `layout.tsx` | `LayoutDropDown` | `Select pill-lg` mit Layout-Icons, `disabledLayouts`. | Layout-Namen aus `ISSUE_LAYOUTS` |
| `merged-date.tsx` | `MergedDateDisplay` | Datumsbereich per `formatDateRange`: gleicher Tag „Jan 24, 2025“, gleicher Monat „Jan 24 - 28, 2025“, gleiches Jahr „Jan 24 - Feb 6, 2025“, Jahreswechsel „Dec 28, 2024 - Jan 4, 2025“. | – |

**Datums-Blocks (direkt aus `@plane/blocks/property-select` genutzt, kein App-Wrapper)**

| Datei | Export | Verhalten |
|---|---|---|
| `date-select.tsx` | `DateSelect` | Trigger + propel `Calendar` (`mode single`) im Popover; `minDate`/`maxDate` als Disabled-Matcher; `weekStartsOn` aus Profil; `formatToken` Default `DEFAULT_DATE_FORMAT_TOKEN`; Klick auf bereits gewählten Tag = Abwahl nur wenn `clearable`, sonst ignoriert; Auswahl schließt Popover. |
| `date-range-select.tsx` | `DateRangeSelect` | `mode range`, ein Monat sichtbar; **erster Klick wird nur intern gehalten** (Entwurf), zweiter Klick emittiert `{from,to}` und schließt; `mergeDates` kürzt Label je Token (`MMM dd, yyyy`: „Jun 10 - 24, 2025“ / „Jan 24 - Feb 02, 2025“; `dd/MM/yyyy`: „10 - 24/06/2025“ / „24/01 - 02/02/2025“; `MM/dd/yyyy`: „06/10 - 24/2025“ / „01/24 - 02/02/2025“; `yyyy/MM/dd`: „2025/06/10 - 24“ / „2025/01/24 - 02/02“); andere Tokens volle Daten. Clear → `{from:null,to:null}`. |
| `date-select-shell.tsx` | `DateSelectShell` | Gemeinsamer Trigger (gleiche `SelectVariant`-Skala), Popover (`side` Default `bottom`, `align` Default `start`), optionaler Ghost-Fuß „Clear“ (`t("common.clear")`), Tooltip, `tabIndex`, `defaultOpen`. |
| `date-select.utils.ts` | `buildDisabledMatchers` | min/max → react-day-picker-Matcher. |

### 2.20 Read-only-Anzeigen (`apps/web/components/readonly/`)

Ersatz für interaktive Dropdowns, wenn ein Wert nur angezeigt werden soll. **In CE nirgends importiert** (Suche nach `components/readonly` und den Exportnamen außerhalb des Ordners ohne Treffer) – Erweiterungspunkt (vermutlich für Bezahl-Ansichten mit eingeschränkten Rechten; im Repo nicht belegbar). Jede Komponente lädt ihre Daten selbst (`index.tsx`-Kommentar „These components handle their own data fetching using internal hooks“). Gemeinsames Muster: `div flex items-center gap-1`, Icon `size-4 flex-shrink-0` (abschaltbar via `hideIcon`), Text `flex-grow truncate`, Fallback `placeholder ?? t("common.none")` („None“).

| Datei | Export | Props | Anzeige / Laden |
|---|---|---|---|
| `state.tsx` | `ReadonlyState` | `className, iconSize="size-4", hideIcon, value, placeholder, projectId, workspaceSlug` | Lädt Projekt-States, falls keine im Store (`fetchProjectStates`); währenddessen Skeleton (Kreis 16×16 + Balken 50×16). `StateGroupIcon` (Gruppe Default `backlog`, Farbe des States) + State-Name. Text `text-body-xs-regular`. |
| `priority.tsx` | `ReadonlyPriority` | `className, hideIcon, value, placeholder` | `PriorityIcon` (`value ?? "none"`) + `ISSUE_PRIORITIES[].title` (nicht übersetzt). |
| `member.tsx` | `ReadonlyMember` | `className, icon, hideIcon, value (string \| string[]), placeholder, multiple, projectId` | Keine Mitglieder → `ButtonAvatars` (Fallback-Icon) + „None“; `multiple` → optionales Icon (`h-3 w-3`) + `ButtonAvatars` (max. 2 + „+N“, ohne Tooltip); single → Initiale in Kreis (`size-4 rounded-full bg-layer-1`, erster Buchstabe von `display_name` bzw. `email`, sonst „?“) + Anzeigename/E-Mail. |
| `labels.tsx` | `ReadonlyLabels` | `className, value: string[], projectId, workspaceSlug` | Lädt Projekt-Labels; zeigt immer Sammelchip: Punkt `h-2 w-2 rounded-full bg-accent-primary` + Anzahl `value.length` + „Labels“ (`text-body-xs-bold`); Tooltip (`layout stacked`) „Labels: a, b“ – deaktiviert bei 0 Labels oder Mobilgerät. Hinweis: Zähler nutzt `value.length` (auch unbekannte IDs), Tooltip nur gefundene Labels. |
| `cycle.tsx` | `ReadonlyCycle` | `className, hideIcon, value, placeholder, projectId, workspaceSlug` | `fetchAllCycles` bei vorhandener `projectId`; `CyclesOutline` + Cycle-Name (`text-13`). |
| `module.tsx` | `ReadonlyModule` | `className, hideIcon, value (string \| string[] \| null), placeholder, projectId, multiple, showCount=true, workspaceSlug` | `fetchModules` nur wenn Werte vorhanden; Icon `WorkItemsOutline` (nicht `ModuleOutline`); `multiple` + `showCount` → „<erstes Modul> +N“. |
| `date.tsx` | `ReadonlyDate` | `className, hideIcon, value, placeholder, formatToken` | `CalendarOutline` + `renderFormattedDate(getDate(value), formatToken)` (`text-13`). |
| `estimate.tsx` | `ReadonlyEstimate` | `className, hideIcon, value, placeholder, projectId, workspaceSlug` | Lädt Projekt-Schätzungen; aktiver Schätzungstyp `TIME` → „Xh Ym“ (`convertMinutesToHoursMinutesString`), sonst Punktwert; `EstimateOutline`. |
| `index.tsx` | Barrel | – | Exportiert alle acht Komponenten + Prop-Typen. |

### 2.21 Generisches Layout-Framework (`apps/web/components/base-layouts/`)

Typ-generisches List/Kanban/Gantt-Gerüst (Typen `packages/types/src/base-layouts/base.ts`: `TBaseLayoutType = "list" | "kanban" | "gantt"`, `IBaseLayoutConfig {key, icon, label}`). **In der CE nirgends eingebunden** (Suche nach `components/base-layouts`, `BaseListLayout`, `BaseKanbanLayout`, `BaseGanttLayout`, `LayoutSwitcher`, `GenericLayoutLoader` außerhalb des Ordners ohne Treffer) – vorgesehen für weitere Entitäten (vermutlich Bezahl-Entitäten wie Initiativen oder Teamspaces; Annahme, im Repo nicht belegbar). Für die Migration als **wiederverwendbare Angular-Bausteine** anlegen, weil damit die Bezahlfeatures dieselbe Optik erhalten.

| Datei | Export | Verhalten / Optik |
|---|---|---|
| `constants.ts` | `BASE_LAYOUTS` | `list` (`ListOutline`, Label „List Layout“), `kanban` (`BoardOutline`, „Board Layout“), `gantt` (`TimelineOutline`, „Gantt Layout“). Die Labels werden mit `t()` übersetzt, existieren aber **nicht** als i18n-Keys → Rohtext wird angezeigt. |
| `layout-switcher.tsx` | `LayoutSwitcher` | Segment `flex items-center gap-1 rounded-md bg-layer-3 p-1`; je Layout Button `h-5.5 w-7 rounded-sm hover:bg-layer-transparent-hover`, aktiv `bg-layer-transparent-active`, Icon `size-3.5` (`text-primary` aktiv / `text-secondary`); Tooltip mit Label (nicht mobil), `aria-label`; optional `layouts` zur Einschränkung; Klick auf aktives Layout ohne Wirkung. |
| `hooks/use-layout-state.ts` | `useLayoutState` | Eingeklappte Gruppen intern (`useState`) oder extern (`externalCollapsedGroups` + `externalOnToggleGroup`); optional `autoScrollForElements` am Container. |
| `hooks/use-group-drop-target.ts` | `useGroupDropTarget` | Gruppe als Drop-Ziel (`type GROUP`): nur Items (`type ITEM`) **aus anderen Gruppen**; `isDraggingOver` für Overlay; Drop → `onDrop(itemId, null, sourceGroupId, targetGroupId)` (keine Positionierung innerhalb der Gruppe). |
| `list/layout.tsx` | `BaseListLayout` | Container `relative size-full overflow-auto bg-surface-1`; leere Gruppen standardmäßig **ausgeblendet** (`showEmptyGroups=false`). |
| `list/group.tsx` | `BaseListGroup` | Sticky-Kopf `sticky top-0 z-10 border-b border-subtle bg-layer-1 px-6 py-1 hover:bg-layer-1-hover` (oder `renderGroupHeader`); eingeklappt → keine Items; Drag-Over: Overlay `absolute inset-0 z-[2] border border-strong bg-layer-1/85` mit Text „Drop here to move“. |
| `list/group-header.tsx` | `GroupHeader` | Button: Gruppen-Icon + Name (`text-13 font-medium text-secondary`) + Anzahl (`text-11 text-tertiary`); Klick toggelt. |
| `list/item.tsx` | `BaseListItem` | `draggable` (`{id, type:"ITEM", groupId}`, `canDrag(item)`) + Drop-Ziel; Inhalt per `renderItem(item, groupId)`. |
| `kanban/layout.tsx` | `BaseKanbanLayout` | Container `relative flex h-full w-full gap-2 overflow-x-auto p-3`; leere Gruppen standardmäßig **sichtbar** (`showEmptyGroups=true`). |
| `kanban/group.tsx` | `BaseKanbanGroup` | Spalte `w-[350px] max-h-full overflow-y-auto rounded-md bg-layer-1 p-2 pt-0`; Sticky-Kopf `px-1 py-2`; Items `flex flex-col gap-2 py-2`; leer → „No items in this group“ (`py-8 text-13 text-tertiary`); Drag-Over-Overlay „Drop here to move“. |
| `kanban/group-header.tsx` | `GroupHeader` | wie List-Variante, Icon+Name gruppiert. |
| `kanban/item.tsx` | `BaseKanbanItem` | wie `BaseListItem` (Drop-Daten enthalten zusätzlich `id`). |
| `gantt/layout.tsx` | `BaseGanttLayout` | Wrapper um `GanttChartRoot` (s. 2.5): Gruppen werden **flach** zu `blockIds` zusammengelegt; Flags `enableBlockLeftResize/RightResize/Move/Reorder/AddBlock/Selection/Dependency` (alle Default `false`), `showAllBlocks=false`, `showToday=true`, `border=false`, `title="Items"`, `loaderTitle="items"`, `timelineType` Default `ISSUE`; `onDateUpdate` → `{id,start_date,target_date}[]`; `loadMoreItems("")`. |
| `gantt/sidebar.tsx` | `BaseGanttSidebar` | Zeilen `BLOCK_HEIGHT` hoch, `RenderIfVisible` (Offsets 100/200, Platzhalter `GanttLayoutListItemLoader`), `GanttDnDHOC` für Reorder (`handleOrderChange`), Hover synchronisiert mit Chart (`updateActiveBlockId`), Dauer „N day(s)“ rechts; Blöcke ohne Start/Ende ausgeblendet (außer `showAllBlocks`); Pagination-Sentinel (Skeleton `h-10 md:h-8 animate-pulse`); ohne `blockIds` 4 × 34 px Skeleton. `isPaginating` fest `false` (TODO im Code). |
| `gantt/index.ts` | Barrel | – |
| `loaders/layout-loader.tsx` | `GenericLayoutLoader` | `list` → `ListLayoutLoader`, `kanban` → `KanbanLayoutLoader`, `customLoaders` überschreibbar; `gantt` ohne Default → `console.warn` + nichts. |

### 2.22 Skeleton-Loader der Layouts (`apps/web/components/ui/loader/layouts/`)

| Datei | Export | Aufbau (1:1 nachzubauen) |
|---|---|---|
| `list-layout-loader.tsx` | `ListLayoutLoader`, `ListLoaderItemRow` | 3 Sektionen mit 6/5/2 Zeilen; Sektionskopf sticky `border-b border-subtle bg-surface-2 py-1` mit 24×24- und 96×24-Platzhalter; Zeile `h-11 border-t border-subtle`: links 40×20 + zufällige Breite (`w-32/52/72`), rechts 6 Property-Platzhalter zufällig 20×20 oder 64×20; Farbe `bg-[var(--illustration-fill-tertiary)]`, `animate-pulse`; Variante `renderForPlaceHolder` (`bg-surface-1`/`bg-surface-2`, für Virtualisierungs-Platzhalter). |
| `kanban-layout-loader.tsx` | `KanbanLayoutLoader`, `KanbanColumnLoader`, `KanbanIssueBlockLoader` | 5 Spalten mit 2/3/2/4/3 Karten, `gap-5`; Spaltenkopf `h-9 w-80` (24×24 + 96×24); Karte 100 px hoch `rounded-sm bg-[var(--illustration-fill-secondary)]`; `KanbanIssueBlockLoader` auch als Platzhalter für nicht sichtbare Karten. |
| `spreadsheet-layout-loader.tsx` | `SpreadsheetLayoutLoader`, `SpreadsheetIssueRowLoader` | Tabelle: Kopf 1 × `min-w-[28rem]` + 10 × `min-w-[8rem]` (`h-11 bg-surface-2`), 16 Zeilen; erste Zelle sticky links (40×20 + Zufallsbreite), übrige 80×20 zentriert. |
| `calendar-layout-loader.tsx` | `CalendarLayoutLoader` | Kopf 5 Spalten `h-11`; 6 Wochenzeilen × 5 Tage (`min-h-[9rem]`), je Tag Datumsplatzhalter 24×24 rechts oben und 0–1 Blöcke `h-8`. **Hinweis:** nur 5 Spalten (Wochenenden nicht dargestellt). |
| `gantt-layout-loader.tsx` | `GanttLayoutLoader`, `GanttLayoutListItemLoader` | Kopfleiste `min-h-10`; links Sidebar `w-[25.5rem]` (Kopf 56×20/64×20, 6 Zeilen 24×24 + Zufallsbreite); rechts Zeitleistenkopf (80×20 + 15 × 40×20) und 6 Balken mit zufälligem Einzug 115/208/260 px; Listenzeile `BLOCK_HEIGHT` hoch (32×24 + Zufallsbreite). |
| `members-layout-loader.tsx` | – | nicht Teil dieses Bereichs. |
| `project-inbox/*` | – | Intake-Bereich (nicht Teil dieses Bereichs). |

---

## 3. Verhalten, Logik, Abläufe (inkl. Edge-Cases)

### 3.1 Gemeinsame Layout-Logik (`issue-layouts/utils.tsx`, `hooks/use-group-dragndrop.ts`, `hooks/use-issue-layout-store.ts`)

#### 3.1.1 Store-Typ-Ermittlung (`apps/web/hooks/use-issue-layout-store.ts`)
`IssuesStoreContext` (React-Context) hat Vorrang. Fallback über Route-Parameter in genau dieser Reihenfolge: `globalViewId`→`GLOBAL`, `userId`→`PROFILE`, `teamspaceId+viewId`→`TEAM_VIEW`, `teamspaceId+projectId`→`TEAM_PROJECT_WORK_ITEMS`, `viewId`→`PROJECT_VIEW`, `cycleId`→`CYCLE`, `moduleId`→`MODULE`, `epicId`→`EPIC`, `projectId`→`PROJECT`, `teamspaceId`→`TEAM`, sonst `PROJECT`. `isWorkspaceLevel(type)` = `PROFILE, GLOBAL, TEAM, TEAM_VIEW, TEAM_PROJECT_WORK_ITEMS, WORKSPACE_DRAFT`.

#### 3.1.2 View-Flags je Store (`apps/web/store/issue/*/issue.store.ts`)
| Store | enableQuickAdd | enableIssueCreation | enableInlineEditing |
|---|---|---|---|
| PROJECT (`store/issue/project/issue.store.ts:56`) | true | true | true |
| CYCLE (`store/issue/cycle/issue.store.ts:105`) | true | true | true |
| MODULE (`store/issue/module/issue.store.ts:65`) | true | true | true |
| PROJECT_VIEW (`store/issue/project-views/issue.store.ts:58`) | true | true | true |
| GLOBAL/Workspace (`store/issue/workspace/issue.store.ts:59`) | true | true | true |
| ARCHIVED (`store/issue/archived/issue.store.ts:54`) | false | false | true (aber Root setzt `canEditPropertiesBasedOnProject=()=>false`) |
| PROFILE (`store/issue/profile/issue.store.ts:90`) | false | true (bei `currentView==="subscribed"`: false) | true |
| WORKSPACE_DRAFT (`store/issue/workspace-draft/issue.store.ts:392`) | false | false | false |

#### 3.1.3 Gruppenspalten (`getGroupByColumns`)
Ohne `groupBy` + `includeNone` → eine Gruppe `{id:"All Issues", name:"All work items" | "All Epics", payload:{}}` (Konstante `ALL_ISSUES` in `packages/constants/src/issue/common.ts`). Mapping `groupBy`→Spalten:

| group_by | Spalten-Quelle | Icon | Payload für Neuanlage | Besonderheiten |
|---|---|---|---|---|
| `project` | `joinedProjectIds` | `Logo` (logo_props) in 24×24 | `{project_id}` | nur Workspace-Ebene |
| `cycle` | `getProjectCycleDetails(currentProject)` + „None“ | `CycleGroupIcon` (3.5) nach Status; None: `CyclesOutline` | `{cycle_id}` | Abgeschlossene Cycles: `isDropDisabled=true`, `dropErrorMessage="Work item cannot be moved to completed cycles"` |
| `module` | `getProjectModuleDetails` + „None“ | `ModuleOutline` | `{module_ids:[id]}` | – |
| `state` | `getProjectStates(projectId)` bzw. `projectStates` | `StateGroupIcon` (Farbe, `percentage=state.order`, Größe LG) | `{state_id}` | – |
| `state_detail.group` | `STATE_GROUPS` (backlog, unstarted, started, completed, cancelled) | `StateGroupIcon` | `{}` | DnD nicht erlaubt |
| `priority` | `ISSUE_PRIORITIES` (urgent, high, medium, low, none) | `PriorityIcon` | `{priority}` | – |
| `labels` | Workspace- bzw. Projekt-Labels + `{id:"None", color:"#666"}` | Farbpunkt 12×12 | `{label_ids:[id]}`; None → `{}` | – |
| `assignees` | `getScopeMemberIds` (Workspace-Mitglieder oder Projektmitglieder) + „None“ | `Avatar size xs` (Fallback Initiale) | `{assignee_ids:[id]}` | – |
| `created_by` | `projectMemberIds` | `Avatar xs` | `{}` | Quick-Add & „+“ deaktiviert; DnD nicht erlaubt |
| `team_project` | `getTeamProjectColumns()` → `undefined` (CE-Stub) | – | – | Enterprise-Teamspaces |

`DRAG_ALLOWED_GROUPS = state, priority, assignees, labels, module, cycle` (`packages/constants/src/issue/common.ts`).

#### 3.1.4 Drag-and-Drop-Algorithmus (pragmatic-drag-and-drop)
1. **Quellen/Ziele**: Draggable = Issue-Block (`getInitialData {id, type:"ISSUE", groupId}`; Kanban zusätzlich `subGroupId`). Drop-Targets: Gruppe/Spalte (`type:"COLUMN"`, `groupId`, `subGroupId`, `columnId`), Issue-Block (`type:"ISSUE"`, mit `attachInstruction` aus `@atlaskit/pragmatic-drag-and-drop-hitbox/tree-item`, Modus `standard` bzw. `last-in-group`), Kanban-Löschzone (`type:"DELETE"`).
2. `getSourceFromDropPayload`: aus `location.initial.dropTargets` das COLUMN-Target → `{groupId, subGroupId, columnId, id}`.
3. `getDestinationFromDropPayload`: aus `location.current.dropTargets` COLUMN **oder** DELETE + ggf. ISSUE; `canAddIssueBelow = instruction.type === "reorder-below"`.
4. `useGroupIssuesDragNDrop.handleOnDrop`: Abbruch, wenn gleiche Spalte **und** gleiches Ziel-Issue. Ruft `handleGroupDragDrop(..., shouldAddIssueAtTop = orderBy !== "sort_order")`.
5. `handleGroupDragDrop`: Abbruch wenn keine Source-ID oder bei Sub-Gruppierung fehlende subGroupIds. Neue `sort_order` via `handleSortOrder` (Default-Schritt **65535**):
   - Zielliste leer → `65535`.
   - Index 0 → `first.sort_order − 65535`.
   - Index = Länge (Ende) → `last.sort_order + 65535`.
   - Dazwischen → Mittelwert der Nachbarn.
   - Ziel-Index = Index des Ziel-Issues; ohne Ziel-Issue: 0 wenn `shouldAddIssueAtTop`, sonst Ende; `reorder-below` auf letztem Element → Ende.
   - Bei Gruppenwechsel: Feld aus `ISSUE_FILTER_DEFAULT_DATA[groupBy]` (`apps/web/store/issue/helpers/base-issues.store.ts:129`). Array-Felder (Labels, Assignees, Module): Quellwert entfernen, Ziel hinzufügen (außer „None“), `uniq`. Skalar: Zielwert bzw. `null` bei „None“. `issueUpdates[key] = {ADD:[ziel], REMOVE:[quelle]}` („None“ → `[]`). Analog für Sub-Gruppe.
6. `updateIssueOnDrop`: Cycle-Änderung → `addCycleToIssue`/`removeCycleFromIssue` (eigener Endpoint), Modul-Änderung → `changeModulesInIssue(ADD, REMOVE)`, Rest → `updateIssue(projectId, issueId, data)`. Fehler → Toast „Error!“/„Error while updating work item“; generischer Fehler → `err.detail ?? "Failed to perform this action"`.
7. Nach Drop: `highlightIssueOnDrop(elementId, shouldScroll = orderBy !== "sort_order")` → nach 200 ms CSS-Klasse `highlight` (bzw. `highlight-with-line`) und `smooth-scroll-into-view-if-needed` (`block:"center", duration:1500`). Klasse wird bei Outside-Click entfernt.
8. Gesperrte Ziele: `group.isDropDisabled` oder Workflow-Sperre (`useWorkFlowFDragNDrop`, CE-Stub in `apps/web/components/workflow`) → Drop abgebrochen, Toast `warning` mit `dropErrorMessage`.
9. Overlay-Regel: `canOverlayBeVisible = isWorkflowDropDisabled || orderBy !== "sort_order" || group.isDropDisabled`; wenn Overlay sichtbar ist, sind Drops **auf** Issues verboten (`canDropOverIssue = !canOverlayBeVisible`), es wird ans Gruppenende bzw. -anfang einsortiert. Ausrichtung des Overlay-Texts: Quelle-Index > Ziel-Index → `justify-end`, sonst `justify-start`.

#### 3.1.5 Weitere Utilities
- `getApproximateCardHeight(displayProperties)` (Kanban-Virtualisierungs-Platzhalter): ohne Props 100 px; Basis 46 px; +24 bei `key`; ignoriert `key, sub_issue_count, link, attachment_count, created_on, updated_on`; restliche aktive Properties >3 → +60, >0 → +32.
- `isIssueNew(issue)`: `created_at` < 30 s → sofort rendern (ohne Virtualisierung).
- `getBlockViewDetails(block, bg)` (Gantt): nur Start → Tooltip „From <Datum>“ und Mask `linear-gradient(to right, bg 50%, transparent 95%)`; nur Ziel → „Till <Datum>“, Gradient nach links; beide → „<Start> to <Ende>“.
- `isDisplayFiltersApplied`: true, wenn irgendeine Default-Display-Property (aus `DEFAULT_DISPLAY_PROPERTIES` des Sub-Issue-Filter-Stores) `false` ist oder ein Display-Filter gesetzt ist (Ausnahme `order_by === "-created_at"`).
- `isFiltersApplied`: irgendein Filterwert nicht leer.
- `calculateIdentifierWidth(identLen, maxSeq)` = `identLen*7 + 7 + digits(maxSeq)*7` px (min-width der ID-Spalte, `maxSeq = currentProjectNextSequenceId ?? 1`).
- `getIssueBlockId(issueId, groupId, subGroupId)` = `issue_${issueId}_${groupId}_${subGroupId}`.
- `SPREADSHEET_COLUMNS`: Mapping Display-Property → Spaltenkomponente (s. 2.6). `SpreadSheetPropertyIconMap`: `MembersOutline, CalenderDays→CalendarOutline, DueDateOutline, EstimateOutline, LabelsOutline, ModuleOutline, ContrastIcon→CyclesOutline, PriorityOutline, StartDateOutline, StateOutline, Link2→LinkOutline, AttachOutline, WorkItemsOutline`.
- `useGroupByOptions(options)`: filtert `ISSUE_GROUP_BY_OPTIONS`.

#### 3.1.6 Display-Filter-Optionen je Seite (`packages/constants/src/issue/filter.ts` → `ISSUE_DISPLAY_FILTERS_BY_PAGE`)
| Seite | Layout | group_by | sub_group_by | order_by | extra_options |
|---|---|---|---|---|---|
| `issues` (Projekt/Cycle/Modul/View) | list | state, priority, cycle, module, labels, assignees, created_by, null | – | sort_order, -created_at, -updated_at, start_date, -priority, target_date | show_empty_groups, sub_issue |
| | kanban | state, priority, cycle, module, labels, assignees, created_by | dieselben + null | wie list | show_empty_groups, sub_issue |
| | calendar | – | – | – | sub_issue (Display-Properties nur `key`, `issue_type`) |
| | spreadsheet | – | – | sort_order, -created_at, -updated_at, start_date, -priority | sub_issue |
| | gantt_chart | – | – | sort_order, -created_at, -updated_at, start_date, -priority | sub_issue (Properties `key`, `issue_type`) |
| `profile_issues` | list | state_detail.group, priority, project, labels, null | – | sort_order, -created_at, -updated_at, start_date, -priority | show_empty_groups, sub_issue |
| | kanban | state_detail.group, priority, project, labels | – | dito | show_empty_groups |
| `archived_issues` | list | state, cycle, module, priority, labels, assignees, created_by, null | – | sort_order, -created_at, -updated_at, start_date, -priority | show_empty_groups |
| `my_issues` (Workspace-Views) | spreadsheet | – | – | `[]` | sub_issue |
| | list | – | – | – | `access:false` |
| `sub_work_items` | list | state, priority, assignees, null | – | -created_at, -updated_at, start_date, -priority | sub_issue (Properties: key, assignee, start_date, due_date, priority, state) |

Filter-Properties je Seite (rich filters): `issues`: priority, state_group, state_id, cycle_id, module_id, assignee_id, mention_id, created_by_id, label_id, start_date, target_date. `profile_issues`: priority, state_group, label_id, start_date, target_date. `archived_issues`: priority, state_group, state_id, cycle_id, module_id, assignee_id, created_by_id, label_id, start_date, target_date. `my_issues`: priority, state_group, label_id, assignee_id, created_by_id, subscriber_id, project_id, start_date, target_date. `sub_work_items`: priority, state_id, assignee_id, start_date, target_date.

Order-Labels (`ISSUE_ORDER_BY_OPTIONS`, i18n en): `sort_order`=„Manual“, `-created_at`=„Last created“, `-updated_at`=„Last updated“, `start_date`=„Start date“, `target_date`=„Due date“, `-priority`=„Priority“. Group-Labels (`ISSUE_GROUP_BY_OPTIONS`): state=„States“, state_detail.group=„State groups“, priority, team_project, project, cycle, module, labels, assignees, created_by, null=„None“. Display-Properties-Labels (`ISSUE_DISPLAY_PROPERTIES`): key=„ID“, assignee, start_date=„Start date“, due_date=„Due date“, labels, priority, state, sub_issue_count=„Sub-work item count“, attachment_count=„Attachment count“, link, estimate, modules, cycle (+ `issue_type`=„Work item Type“ nur in EE).

### 3.2 List-Layout – Verhalten im Detail

**Aufbau (von außen nach innen)**: `IssueLayoutHOC(LIST)` → `div.relative.size-full.bg-surface-2` → `List` → `MultipleSelectGroup` → Scroll-Container → je Gruppe `ListGroup` (Header + Blöcke + Load-More + Quick-Add) → unten `IssueBulkOperationsRoot` (sticky).

**Pagination**
- Erstladen: `fetchIssues("init-loader", {canGroup:true, perPageCount: group_by ? 50 : 100}, viewId)` (`list/base-list-root.tsx`).
- Pro Gruppe: `shouldLoadMore = nextPageResults===undefined && count!==undefined ? geladene < groupIssueCount : !!nextPageResults`.
- Mit Gruppierung: Zeile „Load more ↓“ (`h-11 cursor-pointer border-t-subtle-1 bg-surface-1 p-3 pl-8 text-13 font-medium text-accent-primary hover:text-accent-secondary hover:underline`) → `fetchNextIssues(groupId)`; während Laden `ListLoaderItemRow`.
- Ohne Gruppierung: 3 Skeleton-Zeilen, die letzte ist IntersectionObserver-Ziel (`rootMargin "100% 0% 100% 0%"`) → Endlos-Scroll; während `isPaginating` wird der Observer deaktiviert.

**Collapse von Gruppen**: Klick auf Header-Titelzeile toggelt `groupId` in `kanbanFilters.group_by` (persistiert über Filter-Update-API, geteilt mit Kanban). Nach erfolgreichem Drop in eingeklappte Gruppe wird sie aufgeklappt. Inhalt nur gerendert wenn `(count>0 && expanded) || !group_by`.

**Quick-Add-Vorbelegung (`prePopulateQuickAddData`)**: immer `state_id = default state` des Projekts; dann je Gruppierung: state→`state_id=gruppe`, priority→`priority`, labels≠None→`label_ids:[id]`, assignees≠None→`assignee_ids:[id]`, cycle≠None→`cycle_id`, module≠None→`module_ids:[id]`, created_by→nichts, sonst `{[groupKey]: value}`. Quick-Add ausgeblendet bei: `!enableQuickAdd`, `disableIssueCreation`, Gruppierung `created_by`, abgeschlossenem Cycle, Workflow-Sperre.

**Zeile (`list/block.tsx`)**
- Container `ControlLink` (`@plane/blocks/layout/control-link`): normaler Klick → `onClick` = Peek öffnen (nur wenn nicht schon gepeekt), Ctrl/Cmd/Mittelklick → native Navigation zu `generateWorkItemLink(...)` (Format `/{ws}/browse/{IDENT}-{seq}/` bzw. Archiv/Epic-Varianten, siehe `packages/utils`). `disabled` bei `tempId` (optimistisch) oder `is_draft`.
- Peek-Payload: `{workspaceSlug, projectId, issueId, nestingLevel, isArchived: !!archived_at}`.
- Zeilenklassen: `group/list-block relative flex min-h-11 flex-col gap-3 bg-layer-transparent py-3 text-13 transition-colors hover:bg-layer-transparent-hover`; gepeekt + gleiche Ebene → `border-accent-strong`; aktiv (Tastatur) → `border-strong-1`; ausgewählt → `bg-accent-primary/5 hover:bg-accent-primary/10`; beim Ziehen → `bg-layer-1`; Breakpoint für einzeilige Darstellung: `md:` bei eingeklappter App-Sidebar, sonst `lg:` (`flex-row items-center`).
- Links: Checkbox (nur in Projektkontext `projectId` + Edit-Recht + nicht Epic; sichtbar bei Hover/selektiert; bei Issue aus anderem Projekt deaktiviert mit Tooltip „Only work items within the current project can be selected.“), Identifier (`IssueIdentifier size xs variant tertiary`, min-width s. `calculateIdentifierWidth`), Sub-Issue-Chevron (`ChevronRightOutline size-4`, `rotate-90` wenn offen, nur bei `sub_issues_count>0` und nicht Epic), Titel (`truncate text-body-xs-medium text-primary`, Tooltip mit vollem Namen, deaktiviert beim Ziehen/Mobil).
- Expand: Klick auf Chevron → bei `nestingLevel >= 3` öffnet stattdessen Peek, sonst toggelt und lädt beim Öffnen `subIssues.fetchSubIssues(ws, projectId, issueId)`.
- Optimistisch erstellte Zeile (`tempId`): halbtransparentes Pulse-Overlay `animate-pulse bg-surface-1/20`, rechts `Spinner` statt Properties/Quick-Actions.
- Rechts: `IssueProperties` (activeLayout „List“) + Quick-Action-Menü; Quick-Actions erscheinen auf kleinen Viewports in der Titelzeile (eigene Box `rounded-sm border border-strong`), ab `md/lg` am Zeilenende.
- Drag: `draggable` nur wenn `canDrag (Gruppierung in DRAG_ALLOWED_GROUPS bzw. keine Gruppierung, nicht Sub-Issue) && Edit-Recht`. Versuch trotz Sperre (`onDragStart` nativer Event) → Toast warning „Cannot move work item“ mit „You are not allowed to move this work item“ bzw. „Drag and drop is disabled for the current grouping“.
- Sub-Issues sind keine Drop-Targets; beim Ziehen eines Elternteils werden Kinder als „dragging“ markiert.

**Eigenschaftsleiste (`properties/all-properties.tsx`) – Reihenfolge und Regeln**
1. State (`StateSelect variant pill-sm tooltip`) → `updateIssue({state_id})`.
2. Priority (`PrioritySelect pill-sm tooltip`) → `{priority}`.
3. Datumsbereich (`DateRangeSelect mergeDates clearable`, Icon `StartDateOutline`, Tooltip-Heading „Date range“ = `project_cycles.date_range`) **nur wenn** Start- **und** Zieldatum gesetzt **und** beide Display-Properties aktiv; sonst getrennt:
4. Start-Datum (`DateSelect`, `maxDate = target_date`, Placeholder „Start date“, Icon `StartDateOutline`).
5. Fälligkeitsdatum (`DateSelect`, `minDate = start_date`, Placeholder „Due date“, Icon `DueDateOutline`), rot (`text-danger-primary`) wenn `shouldHighlightIssueDueDate(target_date, stateGroup)` (überfällig und nicht completed/cancelled).
6. Assignees (`MemberSelect multiple`, Variante `avatar-group-sm` wenn Zuweisungen vorhanden, sonst `pill-sm`, Placeholder „Assignees“, Tooltip-Heading „Assignees“).
7. Module (`ModuleSelect multiple pill-sm`) – nur wenn `project.module_view` aktiv und nicht Epic; Änderung als Diff (`xor`) → `changeModulesInIssue(add, remove)`.
8. Cycle (`CycleSelect pill-sm`) – nur wenn `project.cycle_view` und nicht Epic; `addCycleToIssue` bzw. `removeCycleFromIssue`.
9. Estimate (`EstimateSelect pill-sm`) – nur wenn **Route-`projectId`** gesetzt und Schätzungen aktiv (`areEstimateEnabledByProjectId(routeProjectId)`) → auf Workspace-Ebene nie sichtbar (Original-Verhalten, beibehalten).
10. Sub-Issue-Zähler (nur >0, nicht Epic): Chip `ViewsOutline 3×3` + Zahl, Tooltip „Sub-work items: N“, Klick → Navigation zu `${workItemLink}#sub-issues`.
11. Attachment-Zähler (nur >0): `AttachOutline`, Tooltip „Attachments: N“.
12. Link-Zähler (nur >0): `LinkOutline`, Tooltip „Links: N“.
13. Labels (`IssuePropertyLabels`, pill-sm).
Alle Wrapper (`h-5`) stoppen `click` und `focus` (verhindert Peek-Öffnung). Read-only → `disabled`. Zähler-Chips: `h-5 rounded-sm border-[0.5px] border-strong px-2.5 py-1`, Text `text-caption-sm-regular`.

### 3.3 Kanban-/Board-Layout – Verhalten im Detail

- **Seitengrößen**: 30 Karten pro Spalte ohne Subgruppierung, 10 pro Zelle mit Subgruppierung (`kanban/base-kanban-root.tsx`).
- **Pflicht-Gruppierung**: Kanban bietet in `ISSUE_DISPLAY_FILTERS_BY_PAGE.issues.layoutOptions.kanban.group_by` **kein** `null`; `sub_group_by` erlaubt `null`. Spalten-Header erscheinen nur bei `sub_group_by === null` (strikter Vergleich; der Store normalisiert auf `null`).
- **DnD-Erlaubnis**: `IssueKanBanViewStore.getCanUserDragDrop(group_by, sub_group_by)` (`apps/web/store/issue/issue_kanban_view.store.ts:63`) – erlaubt, wenn `group_by ∈ DRAG_ALLOWED_GROUPS` und (`sub_group_by` leer oder ebenfalls erlaubt). Zusätzlich pro Karte: kein `tempId`, Edit-Recht. Gesperrter Drag-Versuch → Toast „Cannot move work item“ (Texte wie List).
- **Drag-Status global**: `useKanbanView().setIsDragging(true/false)` steuert die Lösch-Zone. Beim Drop auf die Lösch-Zone: `DeleteIssueModal` mit `dataId = draggedIssueId`; Bestätigen → `removeIssue(project_id, id)`; Modal schließt in beiden Fällen (Erfolg/Fehler).
- **Drop-Logik**: wie 3.1.4; bei Workflow- oder Spalten-Sperre nur Toast, wenn `dropErrorMessage` existiert (sonst stilles Ignorieren). Highlight-ID enthält Subgruppe.
- **Overlay**: wie List; `dragColumnOrientation` fest (`justify-center` ohne Subgruppe, `justify-start` mit).
- **Collapse**: Spalten (`kanbanFilters.group_by`) nur ohne Swimlanes; Swimlanes (`kanbanFilters.sub_group_by`) über Zeilenheader. Eingeklappte Spalte: Header vertikal, Breite 44 px, keine Karten.
- **Quick-Add**: Vorbelegung `state_id = default state`, überschrieben durch Gruppe, danach durch Subgruppe (Kanban setzt bei `cycle`/`module` auch für „None“ den Wert – Abweichung zur List-Variante, die „None“ ausschließt; beim Nachbau beibehalten bzw. als Original-Bug dokumentieren). Ausgeblendet bei `disableIssueCreation` oder Workflow-Sperre (CE-Stub: nie).
- **Karte**: Quick-Action-Trigger ist ein eigener `<button>` (wegen `MenuTrigger render`), Klick toggelt `isMenuActive`, Outside-Click setzt zurück. Klick auf Karte öffnet Peek (Desktop) bzw. navigiert (Mobil). Properties wie List (gleiche Komponente `IssueProperties`).
- **Virtualisierung**: zweistufig – Spalten (`RenderIfVisible` mit `useIdleTime` und approximierter Höhe `n * getApproximateCardHeight`) und Karten (`RenderIfVisible`, erste 11 Karten sofort).

### 3.4 Calendar-Layout – Verhalten im Detail

- **Datenmodell** (`apps/web/store/issue/issue_calendar_view.store.ts`): `calendarFilters {activeMonthDate, activeWeekDate}` (Session-State, **nicht** persistiert), `calendarPayload` (generiert durch `generateCalendarData`, Schlüssel `y-<Jahr>` → `m-<Monat 0..11>` → `w-<Wochenindex>` → Datum → `ICalendarDate{date, is_current_month, …}`), Wochenstart aus Benutzerprofil (`EStartOfTheWeek`, Default Sonntag). Persistiert werden nur `display_filters.calendar.layout` und `.show_weekends`.
- **Zeitfenster-Abfrage**: Monatsansicht lädt von erstem bis letztem sichtbaren Datum (inkl. Randtage benachbarter Monate), **4 Issues pro Tag** pro Seite; Wochenansicht 30 pro Tag. Gruppierung serverseitig über `target_date` (`EIssueGroupByToServerOptions.target_date`). Nur Issues mit Fälligkeitsdatum erscheinen.
- **Drag-and-Drop**: Draggable-Daten `{id, date}` (altes `target_date`), Drop-Target `{date}`. Validierung vor Update: liegt Zieltag vor `start_date` → Toast error „Due date cannot be before the start date of the work item.“ und Abbruch. Nach Drop Highlight ohne Scroll. Fehler beim Update → Toast `err.detail ?? "Failed to perform this action"`. Drag deaktiviert bei abgeschlossenem Cycle (`readOnly`), fehlendem Edit-Recht und in der Mobilansicht.
- **Quick-Add**: Vorbelegung `target_date = Tag`; Sichtbarkeit `viewFlags.enableQuickAdd && viewFlags.enableIssueCreation` (aus PROJECT-Store!) und nicht read-only. Der Calendar-Quick-Add öffnet über ein Menü (neu vs. bestehend), nicht direkt.
- **Hover-Vorschau**: `WorkItemPreviewCard` (`apps/web/components/issues/preview-card/root.tsx`) nach 100 ms Hover.
- **Leerer Zustand**: Calendar zeigt nie den Layout-Empty-State, sondern immer das Raster (`IssueLayoutHOC`, Ausnahme für `CALENDAR`).
- **Mobil (≤768 px bzw. `md:`)**: Raster zeigt nur Tageszahlen; Tippen wählt Tag; darunter Liste des gewählten Tages mit Überschrift; Options-Menü als Drei-Punkte-Icon; Drag deaktiviert.

### 3.5 Gantt/Timeline – Verhalten im Detail

**Timeline-Store** (`apps/web/store/timeline/base-timeline.store.ts`): `blocksMap`, `blockIds`, `isDragging`, `currentView` (Default **„week“**, nicht persistiert), `currentViewData` (aus `VIEWS_LIST`), `activeBlockId` (Hover-Synchronisation), `renderView`. `updateBlocks(getDataById)` baut `IGanttBlock {data, id, name, sort_order, start_date, target_date, meta{type,index,project_id}, position{marginLeft,width}}`; während `isDragging` keine Aktualisierung. `isDependencyEnabled=false`, `getIsCurrentDependencyDragging = false` (CE).

**Positionsberechnung** (`views/helpers.ts`):
- `marginLeft` = Tage(chartStart → start_date) × `dayWidth`; nur Zieldatum → Position(target_date) − 60 + dayWidth (Breite 60 = `DEFAULT_BLOCK_WIDTH`).
- `width` = (|Tage(start→target)| + 1) × `dayWidth`; sonst 60.
- Datum aus Position: `round(px / dayWidth) + offsetDays` Tage ab chartStart.

**Resize/Move (`use-gantt-resizable.ts`)**: nur linke Maustaste. Maus-X relativ zu Container − 360 + `scrollLeft`.
- Links: `marginLeft = round(x/dayWidth)*dayWidth`; Breite = alte Breite + Delta; ohne Zieldatum → Breite 60.
- Rechts: `width = round(x/dayWidth)*dayWidth − marginLeft`; ohne Startdatum → Block 60 px links vom Cursor.
- Move: Raster-Snap mit Offset des Klickpunkts.
- Mindestbreite 1 Tag. Während Scroll wird die letzte Mausposition erneut angewandt. Store-Position wird live mit Deltas aktualisiert.
- MouseUp: `getUpdatedPositionAfterDrag(id, shouldUpdateHalfBlock)` – Startdatum nur, wenn vorhanden oder links am fehlenden Ende gezogen; Zieldatum analog (Position Ende − 1 Tag). Ergebnis → `updateBlockDates([{id, start_date?, target_date?, meta}])` → `issues.updateIssueDates` (Store-Bulk-Update, eigener Endpoint – Details im Store-/API-Bereich). Fehler → Toast „Something went wrong while updating block dates“.
- Beim horizontalen Nachladen links während Drag werden alle Blöcke um die neue Breite verschoben (`updateAllBlocksOnChartChangeWhileDragging`).

**Reorder in der Sidebar**: nur wenn `order_by === "sort_order"` und Edit-Recht; Schrittweite **1000** (anders als List/Kanban mit 65535!).

**Sichtbarkeit**: `showAllBlocks=true` für Issues → auch Issues ohne Datum stehen in der Sidebar (Chart-Zeile zeigt dann „+ Add“-Hover-Button). Ohne `showAllBlocks` (Module-Timeline) werden nur vollständige Blöcke gezeigt.

**Leerzustände/Loader**: `IssueLayoutHOC` → `GanttLayoutLoader` bzw. Empty-State. Sidebar ohne `blockIds` → 4 Skeleton-Zeilen 34 px.

### 3.6 Spreadsheet – Verhalten im Detail

- **Sortierung** (`packages/constants/src/issue/common.ts` → `SPREADSHEET_PROPERTY_DETAILS`):

| Spalte | Titel (i18n) | „asc“-Key / Label | „desc“-Key / Label |
|---|---|---|---|
| assignee | Assignees | `assignees__first_name` „A“ | `-assignees__first_name` „Z“ |
| created_on | Created on | `-created_at` „New“ | `created_at` „Old“ |
| due_date | Due date | `-target_date` „New“ | `target_date` „Old“ |
| estimate | Estimate | `estimate_point__key` „Low“ | `-estimate_point__key` „High“ |
| labels | Labels | `labels__name` „A“ | `-labels__name` „Z“ |
| modules | Modules | `issue_module__module__name` „A“ | `-issue_module__module__name` „Z“ |
| cycle | Cycle | `issue_cycle__cycle__name` „A“ | `-issue_cycle__cycle__name` „Z“ |
| priority | Priority | `priority` „None“ | `-priority` „Urgent“ |
| start_date | Start date | `-start_date` „New“ | `start_date` „Old“ |
| state | State | `state__name` „A“ | `-state__name` „Z“ |
| updated_on | Updated on | `-updated_at` „New“ | `updated_at` „Old“ |
| link | Link | `-link_count` „Most“ | `link_count` „Least“ |
| attachment_count | Attachment | `-attachment_count` „Most“ | `attachment_count` „Least“ |
| sub_issue_count | Sub-work item | `-sub_issues_count` „Most“ | `sub_issues_count` „Least“ |

  Menüeinträge lauten „<asc-Label> → <desc-Label>“ bzw. umgekehrt. Sortier-Icon im Kopf nur für die in localStorage gemerkte aktive Spalte.
- **Tastaturnavigation** (`apps/web/hooks/use-table-keyboard-navigation.tsx`): auf fokussiertem `td/th`: Pfeil links/rechts → Nachbarzelle, hoch/runter → gleiche Spalte in Vor-/Folgezeile (übergreifend zwischen `thead` und `tbody`), danach `focus()` + `scrollIntoView({behavior:"smooth", block:"center", inline:"end"})`. Enter → Klick auf `.clickable` in der Zelle (öffnet Dropdown bzw. Peek). Der Code prüft `e.key == "Space"` (in Browsern ist `e.key === " "`), daher löst Leertaste **nicht** aus – Original-Verhalten.
- **Inline-Editing**: alle Dropdown-Spalten verwenden Variante `table-cell` (volle Zellfläche als Trigger); nach Schließen kehrt der Fokus zur Zelle zurück. Änderungen gehen über `updateIssue(projectId, id, data)`; Cycle/Modul über eigene Endpunkte.
- **Pagination**: 100 pro Seite, Nachladen per IntersectionObserver auf `tfoot`.
- **Virtualisierung**: Zeilen außerhalb (±100 %) werden als leere `td` mit fixer Höhe 43 px gerendert; neue (<30 s) Issues sofort.
- **Sticky**: Kopfzeile oben (`z-[12]`), erste Spalte links (`z-[15]` im Kopf, `z-10` im Body, ab `md`).

### 3.7 Laden, Paginieren und Persistieren von Filtern/Anzeigeoptionen

**Request-Vertrag der Layout-Listen** (`apps/web/store/issue/helpers/issue-filter-helper.store.ts`, `apps/web/services/issue/issue.service.ts`)

| Aspekt | Verhalten |
|---|---|
| Endpunkt | `GET /api/workspaces/{ws}/projects/{pid}/issues/` (bzw. `{serviceType}` = `issues`/`epics`; Cycle/Modul/View/Workspace/Profile über ihre jeweiligen Stores und Services) |
| Display-Parameter | `group_by`, `sub_group_by` (Mapping `EIssueGroupByToServerOptions`), `order_by`, `sub_issue` (Default `true`), nur wenn für das Layout zulässig (`acceptableParamsByLayout`); `layout` immer; Rich-Filter als **JSON-String** im Parameter `filters`; `expand=issue_relation,issue_related` nur bei Gantt **und** `ENABLE_ISSUE_DEPENDENCIES` (CE: `false`) |
| Cursor | Format `"<perPage>:<page>:0"`; erste Seite ungruppiert `"<n>:0:0"`, gruppenweise `"<n>:1:0"`; Folgeseiten `"<n>:<floor(geladen/n)>:0"` bzw. `next_cursor` der Antwort; Parameter `per_page` |
| Gruppenweises Nachladen | `group_by`-Parameter wird entfernt und durch Filter-Parameter der Gruppe ersetzt (`EServerGroupByToFilterOptions[groupBy] = groupId`), analog `sub_group_by` |
| Calendar | `groupedBy = "target_date"`, zusätzlich `target_date = "<after>;after,<before>;before"` |
| Seitengrößen | List 50 (gruppiert) / 100; Kanban 30 / 10 (mit Subgruppen); Calendar 4 (Monat) / 30 (Woche); Gantt 100; Spreadsheet 100; Workspace-Views 100 (`list/base-list-root.tsx`, `kanban/base-kanban-root.tsx`, `calendar/base-calendar-root.tsx`, `gantt/base-gantt-root.tsx`, `spreadsheet/base-spreadsheet-root.tsx`, `roots/all-issue-layout-root.tsx`) |
| Antwort | gruppiert: `results` je Gruppe (+ Subgruppe) mit `total_count`; ungruppiert → Gruppe `ALL_ISSUES = "All Issues"` (`packages/constants/src/issue/common.ts`, `base-issues.store.ts`) |
| Loader-Zustände | `init-loader` (Skeleton des Layouts), `mutation` (Spinner-Kästchen oben rechts, s. 2.1), `pagination` (Platzhalterzeilen), je Gruppe/Subgruppe getrennt (`base-issues.store.ts`) |

**Persistenz der Ansichtseinstellungen (Projekt-Ebene)** (`apps/web/store/issue/project/filter.store.ts`)

| Typ | Speicherort | Wirkung |
|---|---|---|
| Rich-Filter (`richFilters`) | Server `user-properties` (`PATCH/POST /api/workspaces/{ws}/projects/{pid}/user-properties/`, Feld `rich_filters`) | Store sofort gesetzt → `fetchIssuesWithExistingPagination(..., "mutation")` → Server-Update |
| Display-Filter | Server `display_filters` | Regeln: `group_by = null` ⇒ `sub_group_by = null`; Kanban mit `group_by == sub_group_by` ⇒ `sub_group_by = null`; Kanban mit `group_by = null` ⇒ `group_by = "state"`. **Layoutwechsel leert den Issue-Cache** (`getShouldClearIssues`: Schlüssel `layout`); Änderungen an `order_by`, `sub_issue`, `type` lösen Neuladen aus (`getShouldReFetchIssues`); `group_by`-Änderungen laden über die `useEffect`-Abhängigkeiten der Layout-Roots neu |
| Display-Properties | Server `display_properties` | nur Store + Server, kein Neuladen |
| Kanban-Filter (`kanbanFilters.group_by/sub_group_by` = **eingeklappte Gruppen**) | **localStorage** `issue_local_filters` (pro Store-Typ, Workspace, Projekt/View, Nutzer) | nur clientseitig |
| Fehler | jeder Fehler → `fetchFilters` (Rollback auf Serverstand) und Re-throw | – |

Weitere localStorage-Schlüssel dieses Bereichs: `spreadsheetViewSorting`, `spreadsheetViewActiveSortingProperty` (Spreadsheet-Sortiermenü, s. 3.6), `issue_activity_filters`, `activity_sort_order` (Activity, s. 2.15). Peek-Modus wird **nicht** persistiert (s. 2.12).

### 3.8 Rich-Filter-Ablauf (`apps/web/components/rich-filters/*`, `apps/web/components/work-item-filters/*`)

1. Layout-Root umhüllt den Inhalt mit `ProjectLevelWorkItemFiltersHOC` bzw. `WorkspaceLevelWorkItemFiltersHOC`; diese erzeugen per `getOrCreateFilter` eine Filter-Instanz (Schlüssel `entityType` + `entityId`; temporär `TEMP-<id|uuid>`) mit dem Server-Ausdruck als `initialExpression` (s. 2.11).
2. Filter-Button im Seitenkopf (`WorkItemFiltersToggle`): ohne Bedingungen öffnet er direkt das „Add filter“-Dropdown und blendet die Zeile ein; mit Bedingungen toggelt er die Zeile (Icon `SelectedFilterOutline` in Akzentfarbe).
3. „Add filter“: Feld wählen → Bedingung mit erstem zulässigen Operator, Wert `undefined` (Chip erscheint mit Einblend-Animation, Werteingabe öffnet sich automatisch). Bereits verwendete Felder verschwinden aus dem Dropdown, außer Datumsfelder (`allowMultipleFilters`). Sind alle Felder verwendet: „All filters applied“.
4. Operatorwechsel nur bei Feldern mit mehreren Operatoren (Datumsfelder: „is“ ↔ „between“). Mehrfachauswahl zeigt „is“ bei ≤ 1 Wert und „is any of“ bei > 1 Wert (Anzeige, Operator bleibt `in`).
5. Jede Änderung → `onExpressionChange` → `updateFilterExpression` (3.7) → Neuladen mit `mutation`-Loader. Unvollständige Datumsbereiche werden als `[]` übergeben und rot markiert.
6. „Clear all“ entfernt alle Bedingungen; „Save view“ öffnet das View-Modal vorbefüllt; „Update view“ schreibt `rich_filters`, `display_filters`, `display_properties` in die bestehende View (Rechte s. 2.11). Ungültige Bedingungen (gelöschte Property, fehlende Rechte) bleiben als „Invalid filter“-Chip sichtbar und entfernbar.
7. Logische Verknüpfung ausschließlich `AND`; keine Gruppen/ODER, keine Negation (CE, s. 2.11) – Bezahl-Editionen erweitern (s. 5.4).

### 3.9 Peek-Overview – Abläufe (`apps/web/components/issues/peek-overview/*`, `apps/web/hooks/use-issue-peek-overview-redirection.tsx`, `apps/web/hooks/use-peek-overview-outside-click.tsx`, `apps/web/store/issue/issue-details/root.store.ts`)

- **Öffnen**: Klick auf Block/Karte/Zeile → `handleRedirection(ws, issue, isMobile, nestingLevel)`: nur wenn Projekt-ID, ID vorhanden, nicht bereits gepeekt und **kein `tempId`** (optimistisch angelegte Items sind nicht öffnbar). Auf Mobilgeräten Navigation zur Detailseite statt Peek. Ctrl/Cmd/Mittelklick → native Navigation (neuer Tab) über `ControlLink`.
- **Zustand**: `peekIssue {workspaceSlug, projectId, issueId, nestingLevel, isArchived}` liegt nur im MobX-Store (`setPeekIssue`); die URL ändert sich **nicht** (der Router-Getter `peekId` wird in Komponenten nicht verwendet) → kein Deep-Link auf einen Peek.
- **Laden**: SWR-Key `["peek-issue", ws, pid, id]` ohne Revalidierung; Fehler → Fehleransicht „Work item does not exist“.
- **Schließen per Outside-Click** (mousedown auf `document`, ausgewertet über `event.composedPath()`): Klick außerhalb des Panels schließt, **außer** (a) ein Element im Pfad trägt `data-prevent-outside-click` (es sei denn, seine ID steht in der Ausnahmeliste oder das Panel liegt im selben Container), (b) ein Element im Pfad trägt `data-base-ui-portal` (Menüs/Selects/Popover sind an `<body>` portiert), (c) der Klick trifft das Listenelement `#issue-<id>` des gepeekten Items. `data-delay-outside-click` verzögert das Schließen um einen Tick. Offene lokale Modals (Delete/Archive/Duplicate/Edit) blockieren das Schließen.
- **Schließen per `Escape`**: nicht bei `embedIssue`, offenen Modals, fokussiertem `INPUT`, offenen Editor-Dropbars oder Bild-Vollbild; danach Fokus auf `#issue-<id>` (s. 2.12).
- **Operationen** (`peek-overview/root.tsx`): `update` → Store-Update, danach Activity neu laden; Fehler-Toast „Error!“ / „Work item update failed“. `remove` → schließt den Peek. `archive`, `restore` („Restore success“ / „Your work item can be found in project work items.“ bzw. „Work item could not be restored. Please try again.“), `addCycleToIssue`/`addIssueToCycle` (Fehler „Work item could not be added to the cycle. Please try again.“), `removeIssueFromCycle`/`removeIssueFromModule` (Promise-Toast „Removing work item from the cycle|module“ → „Work item removed from the cycle|module successfully.“ / „Work item could not be removed from the cycle|module. Please try again.“), `changeModulesInIssue` (danach Activity).
- **Modi**: Side-Peek (Default, 50 % Breite ab `md`), Modal (5/6 zentriert), Full-Screen (`inset-0 m-4`, zweispaltig mit 400 px Properties-Spalte). Wechsel über Icon-Select im Kopf; Übergang `transition-all duration-300`.
- **Verschachtelung**: Peek innerhalb der Detailseite (Sub-Items/Relationen) mit `nestingLevel`; die Detailseite rendert ihre Widget-Modals nur, wenn kein Peek aktiv ist (`renderWidgetModals = !peekAktiv`, s. 2.13).

### 3.10 Detailseite, Titel/Beschreibung und Widgets – Abläufe

- **Route** `/{ws}/browse/{IDENT}-{seq}/` (Lookup `GET /api/workspaces/{ws}/work-items/{IDENT}-{seq}/`, `retrieveWithIdentifier`); Archiv-Variante; Epic-Variante (Bezahlfeature). Nicht gefunden → Empty-State mit „View other work items“ (s. 2.13).
- **Titel**: Autosave 1,5 s nach letzter Eingabe; leer → Fehler „Title is required“ und Rücksetzen auf alten Wert; > 255 Zeichen gesperrt (Zähler rot); Speichern beim Verlassen (s. 2.18).
- **Beschreibung**: Rich-Text-Editor (`DescriptionInput`, anderer Bereich „Editor“) mit Autosave; Status „Saving...“ → „Saved“ (nach 2 s); während des Speicherns warnt der Browser beim Neuladen; Versionsverlauf (`description-versions`) mit Wiederherstellen.
- **Sidebar-Properties**: jede Änderung sofort per `PATCH .../issues/{id}/`; Cycle über eigene Endpunkte (`cycle-issues`), Module über `changeModulesInIssue` (serialisiert), Parent über Parent-Modal (Suche `projectIssuesSearch` mit `parent: true`).
- **Widgets** (s. 2.14): Aktionsleiste „Add sub-work item“/„Add relation“/„Add link“/„Attach“; Collapsibles öffnen sich nach einer Aktion automatisch (`setLastWidgetAction`); Sub-Items mit eigener Gruppierung/Filterung/Display-Properties; Relationen `relates_to`, `duplicate`, `blocked_by`, `blocking` (CE); Links mit Metadaten (Favicon/Titel); Attachments mit Dropzone und Größenlimit `file_size_limit`.
- **Kopfaktionen**: Subscribe/Unsubscribe, Copy link (absolute URL), Menü (Make a copy, Open in new tab, Archive/Restore, Delete) mit Weiterleitungen nach Löschen/Archivieren (s. 2.13).
- **Mobile** (< 768 px): Properties werden im Hauptinhalt zwischen Widgets und Activity angezeigt; Sidebar ist ein fest positioniertes, ausfahrbares Panel (`issueDetailSidebarCollapsed`).

### 3.11 Create/Edit-Modal und Entwürfe – Abläufe (`apps/web/components/issues/issue-modal/*`, `apps/web/components/issues/workspace-draft/*`)

1. **Öffnen** aus: Seitenkopf „Add work item“, Gruppen-„+“ (Vorbelegung mit dem `payload` der Gruppe aus `getGroupByColumns`, s. Tabelle 3.1.3: `project_id`, `cycle_id`, `module_ids`, `state_id`, `priority`, `label_ids`, `assignee_ids`; `apps/web/components/issues/issue-layouts/list/headers/group-by-card.tsx`, `apps/web/components/issues/issue-layouts/kanban/headers/group-by-card.tsx`), Quick-Action „Edit“/„Make a copy“, Calendar/Gantt-Quick-Add-Erweiterungen, Workspace-Drafts. Route-Kontext ergänzt `cycle_id`/`module_ids`.
2. **Projektwahl**: nur Projekte mit Create-Recht (`allowedProjectIds`); ohne erlaubte Projekte wird das Modal nicht gerendert. Projektwechsel leert projektspezifische Felder (States, Labels, Cycle, Module, Estimate, Parent) und lädt Cycles nach.
3. **Validierung**: Titel Pflicht, nicht nur Leerzeichen, ≤ 255 Zeichen; Submit erst, wenn der Editor bereit ist (Uploads abgeschlossen).
4. **Absenden (Create)**: Draft-Modus → Workspace-Draft; im Cycle-/Modul-Kontext mit abweichendem Ziel → Projekt-Store; danach Asset-Status-Bulk-Update, Cycle-/Modul-Zuordnung, Toast mit Aktionen („Copy link“, Identifier kopieren, „View“; s. 2.7). **Create more** hält das Modal offen und setzt Formular und Fokus zurück.
5. **Absenden (Update)**: nur geänderte Felder (`getChangedIssuefields`) + `project_id`, `id`, `description_html`, `type_id`; Cycle-Wechsel = Entfernen + Hinzufügen; Modul-Diff.
6. **Schließen ohne Speichern** (nur neue Items): Bei relevanten Änderungen fragt `ConfirmIssueDiscard` „Save this draft?“ → „Save to Drafts“ legt Workspace-Draft an (leerer Titel → „Untitled“), „Discard“ verwirft. Klick außerhalb schließt **nicht** (`disablePointerDismissal`).
7. **Entwürfe** (`/{ws}/drafts`): Liste mit Cursor-„Load More“, Inline-Properties, Doppelklick = Bearbeiten, „Move to project“ wandelt per `POST /api/workspaces/{ws}/draft-to-issue/{id}/` um, „Make a copy“, „Delete“ (nur Ersteller/Projekt-Admin).
8. **AI-Hilfe** im Beschreibungseditor nur bei `instance.config.has_llm_configured` („I'm feeling lucky“, „AI“-Popover; Limit-Fehler 429).

### 3.12 Activity & Kommentare – Abläufe (`apps/web/components/issues/issue-detail/issue-activity/*`, `apps/web/components/comments/*`)

- Daten: `GET .../issues/{id}/history/` (Activity) und `GET .../issues/{id}/comments/`, zusammengeführt und nach `created_at` sortiert (`getActivityAndCommentsByIssueId(issueId, sortOrder)`); nach jeder Property-Änderung lädt der Peek/Detail-Kontext die Activity neu.
- Filter (Updates/Comments/State/Assignee) und Sortierung (asc/desc) clientseitig, gespeichert in localStorage; mindestens ein Filter bleibt aktiv; Eintragstyp `DEFAULT` wird immer angezeigt.
- Kommentar anlegen: Enter sendet (Shift/Ctrl/Meta+Enter = Zeilenumbruch), nur wenn nicht leer und alle Uploads fertig; Access-Umschalter intern/öffentlich nur bei veröffentlichtem Projekt (`project.anchor`).
- Kommentar bearbeiten (nur Autor): Inline-Editor, Enter speichert, „(edited)“-Markierung; Löschen (nur Autor); „Copy link“ (`#comment-<id>`, Ziel wird angescrollt und 8 s hervorgehoben); Reaktionen per Emoji-Picker.
- Archivierte Items: Kommentareingabe ausgeblendet, Reaktionen read-only.

### 3.13 Archivieren, Wiederherstellen, Löschen

| Aktion | Voraussetzung (UI) | Ablauf / Texte | Quelle |
|---|---|---|---|
| Archive | Projektrolle ADMIN/MEMBER; Item in State-Gruppe `completed` oder `cancelled` (`ARCHIVABLE_STATE_GROUPS`, `packages/constants/src/state.ts`), sonst Menüeintrag deaktiviert mit Beschreibung „Only completed or canceled work items can be archived“ | `ConfirmDialog` „Archive Work item <IDENT> <seq>“ → `POST .../issues/{id}/archive/`; Toast „Archive success“ / „Your archives can be found in project archives.“ | `apps/web/components/issues/archive-issue-modal.tsx`, `apps/web/components/issues/issue-layouts/quick-action-dropdowns/helper.tsx` |
| Restore | Item archiviert, ADMIN/MEMBER | `DELETE .../issues/{id}/archive/` (`restoreIssue` im Archiv-Service; Archivliste `GET .../archived-issues/`), Toast „Restore success“, auf der Detailseite Weiterleitung zum Item | `apps/web/components/issues/issue-detail/issue-detail-quick-actions.tsx`, `apps/web/services/issue/issue_archive.service.ts` |
| Delete | Menüeintrag für ADMIN/MEMBER (`isDeletingAllowed = isEditingAllowed`); der Dialog erlaubt nur Ersteller **oder** Projekt-ADMIN (clientseitig, Server prüft erneut); im Archiv-Menü ausgeblendet | `ConfirmDialog` „Delete Work item“ → `DELETE .../issues/{id}/`; Peek schließt / Detailseite leitet auf Liste um | `apps/web/components/issues/delete-issue-modal.tsx` |
| Kanban-Delete-Dropzone | Drag einer Karte auf die Zone „Drop here to delete the work item“ (nur wenn Löschen erlaubt) | öffnet den Delete-Dialog | `apps/web/components/issues/issue-layouts/kanban/kanban-delete-drop-zone.tsx` |
| Bulk-Archive/Delete/Subscribe | Endpunkte existieren (`bulk-archive-issues`, `bulk-delete-issues`, `bulk-subscribe-issues`, `bulk-operation-issues`), UI in CE nicht erreichbar | s. 5.4 | `apps/web/services/issue/issue.service.ts` |

### 3.14 Tastatur – Gesamtübersicht

| Kontext | Taste | Wirkung | Quelle |
|---|---|---|---|
| Peek | `Escape` | schließt Peek (Ausnahmen s. 3.9), Fokus zurück auf Listenelement | `apps/web/components/issues/peek-overview/view.tsx` |
| Quick-Add | `Escape` | schließt Formular | `apps/web/components/issues/issue-layouts/quick-add/form/root.tsx` |
| Quick-Add | `Enter` | Formular-Submit (legt Item an, Formular bleibt offen) | `apps/web/components/issues/issue-layouts/quick-add/root.tsx` |
| Create/Edit-Modal | `Escape` | schließt Modal (über Editor-Hook, nur wenn Editor bereit) | `apps/web/components/issues/issue-modal/components/description-editor.tsx` |
| Create/Edit-Modal | Editor-Enter-Shortcut | klickt den Submit-Button | ebd. |
| Create/Edit-Modal | `Tab` | feste Reihenfolge `ISSUE_FORM_TAB_INDICES` (s. 2.16) | `packages/constants/src/tab-indices.ts` |
| Spreadsheet | Pfeiltasten | Zellnavigation inkl. Kopf/Körper, `scrollIntoView` | `apps/web/hooks/use-table-keyboard-navigation.tsx` |
| Spreadsheet | `Enter` | klickt das `.clickable`-Element der Zelle (öffnet Dropdown); `"Space"` wird geprüft, kommt als `e.key` aber nie vor (Leertaste = `" "`) → wirkungslos | ebd. |
| Listen mit Mehrfachauswahl | `↑`/`↓` | aktives Element wechseln; `Shift+↑/↓` Auswahl erweitern; `Shift`+Klick Bereichsauswahl | `apps/web/hooks/use-multiple-select.ts` – in CE deaktiviert (`disabled = !useBulkOperationStatus()`) |
| Kommentar | `Enter` / `Shift+Enter` | senden / Zeilenumbruch | `apps/web/components/comments/comment-create.tsx`, `apps/web/components/comments/card/edit-form.tsx` |
| Menüs in Zeilen | `Enter`/Leertaste | `stopPropagation`, damit die Zeile nicht den Peek öffnet | `apps/web/components/issues/issue-layouts/quick-action-dropdowns/helper.tsx`, `apps/web/components/issues/relations/issue-list-item.tsx`, `apps/web/components/issues/issue-detail-widgets/sub-issues/issues-list/list-item.tsx`, `apps/web/components/issues/attachment/attachment-list-item.tsx` |
| Selects (Blocks) | Pfeiltasten/Enter/Escape | Combobox-Navigation, deaktivierte Zeilen werden übersprungen | `packages/blocks/src/select/use-skip-disabled-rows.ts` |

Globale Tastenkürzel (Command-Palette, Shortcut-Übersicht, Anlegen von Work Items per Tastatur) gehören zum Bereich Command-Palette/Shortcuts und werden dort analysiert.

### 3.15 Gesammelte Edge-Cases und Original-Abweichungen (bewusst 1:1 oder bewusst korrigieren?)

| # | Beobachtung | Quelle |
|---|---|---|
| 1 | Estimate-Property in List/Kanban-Pills nur sichtbar, wenn eine `projectId` aus der Route vorhanden ist (Workspace-Views ohne Estimate-Pill) | `apps/web/components/issues/issue-layouts/properties/all-properties.tsx` |
| 2 | Calendar verwendet in allen Kontexten die View-Flags des PROJECT-Stores; Mobilansicht rendert die Wochen-/Tagesliste zusätzlich | `apps/web/components/issues/issue-layouts/calendar/calendar.tsx` |
| 3 | Spreadsheet: Leertaste in der Tastaturnavigation wirkungslos (`e.key == "Space"`) | `apps/web/hooks/use-table-keyboard-navigation.tsx` |
| 4 | Kanban-Quick-Add-Vorbelegung: Default-State + Gruppenwert; bei `labels`/`assignees` wird „None“ ausgelassen, bei `cycle`/`module` **nicht** (`cycle_id: "None"` bzw. `module_ids: ["None"]` im Payload) | `apps/web/components/issues/issue-layouts/kanban/kanban-group.tsx` |
| 5 | Activity „removed the work item from the cycle“ zeigt `new_value` statt `old_value` | `apps/web/components/issues/issue-detail/issue-activity/activity/actions/cycle.tsx` |
| 6 | Archiv-Ansicht: Delete ausgeblendet, Restore erlaubt | `apps/web/components/issues/issue-layouts/quick-action-dropdowns/archived-issue.tsx` |
| 7 | Sort-Order-Schritte unterschiedlich: Listen/Kanban 65535 bzw. Mittelwert, Gantt-Reorder 1000 | `apps/web/components/issues/issue-layouts/utils.tsx`, `apps/web/components/gantt-chart/sidebar/utils.ts` |
| 8 | Estimate-Bedingung im Peek (Projekt-Schätzung aktiv) vs. Sidebar (`areEstimateEnabledByProjectId`) unterschiedlich implementiert | `apps/web/components/issues/peek-overview/properties.tsx`, `apps/web/components/issues/issue-detail/sidebar.tsx` |
| 9 | Ungenutzter Code: Legacy-Link-Komponenten (`issue-detail/links/root.tsx`, `links.tsx`, `link-detail.tsx`), `IssueRelationSelect` (`issue-detail/relation-select.tsx`, außerhalb der eigenen Datei kein Import), `base-layouts/*`, `readonly/*`, `CommentsWrapper` (`comments/comments.tsx`); Kachel-Attachments (`issues/attachment/root.tsx`, `attachment-upload.tsx`, `attachments-list.tsx`, `attachment-detail.tsx`, `attachment-upload-details.tsx`) nur im Intake | s. 2.13, 2.14, 2.15, 2.20, 2.21 |
| 10 | Toast beim Entfernen aus Modul verwendet teils „cycle“-Texte | s. 2.8 |
| 11 | Kanban-Spaltenkopf mit Collapse nur bei `sub_group_by === null` | `apps/web/components/issues/issue-layouts/kanban/headers/group-by-card.tsx` |
| 12 | ProjectView-Root setzt beim Verlassen die View-Filter zurück | `apps/web/components/issues/issue-layouts/roots/project-view-layout-root.tsx` |
| 13 | Optimistisch angelegte Items (`tempId`) lassen sich nicht peeken | `apps/web/hooks/use-issue-peek-overview-redirection.tsx` |
| 14 | `ReadonlyLabels` zählt auch unbekannte Label-IDs | `apps/web/components/readonly/labels.tsx` |
| 15 | `BASE_LAYOUTS`-Labels sind keine i18n-Keys (Rohtext) | `apps/web/components/base-layouts/constants.ts` |
| 16 | `CalendarLayoutLoader` zeigt nur 5 Tagesspalten | `apps/web/components/ui/loader/layouts/calendar-layout-loader.tsx` |
| 17 | Peek-Zustand nicht in der URL (kein Teilen/Neuladen eines geöffneten Peeks) | `apps/web/store/issue/issue-details/root.store.ts` |

---

## 4. Abhängigkeiten zu anderen Bereichen

### 4.1 Stores und Hooks (State, `apps/web/store/**`, `apps/web/hooks/**`)

| Abhängigkeit | Nutzung in diesem Bereich | Häufigkeit (Importe) | Zugehöriges Analyse-Dokument |
|---|---|---|---|
| `@/hooks/store/use-issues` → `IssueRootStore` mit 13 Listen-Stores (`apps/web/store/issue/{project,cycle,module,project-views,workspace,profile,archived,draft,…}`) | Laden/Paginieren/Gruppieren, `createIssue`, `updateIssue`, `removeIssue`, `archiveIssue`, `quickAddIssue`, `addIssueToCycle`, `changeModulesInIssue`, `issuesFilter.updateFilters` | 44 | `migration/analysis/08-frontend-web-architektur.md` 2.6, 3.4, 3.5 |
| `@/hooks/use-issue-layout-store` (`IssuesStoreContext`, `useIssueStoreType`) | Store-Typ-Ermittlung je Route (3.1.1) | 29 | 08 · 2.6 |
| `@/hooks/use-issues-actions` | einheitliche Aktions-Fassade je Store-Typ (`fetchIssues`, `fetchNextIssues`, `updateFilters`, …) | 7 | 08 · 2.8 |
| `@/hooks/store/use-issue-detail` (`apps/web/store/issue/issue-details/*`: `root.store.ts`, Sub-Issues, Relations, Links, Attachments, Activity, Comments, Reactions, Subscription) | Peek-Zustand, Detail-Fetch, Widgets, Activity, Kommentare | 98 | 08 · 3.6 |
| `@/hooks/store/user` (`useUser`, `useUserPermissions` → `allowPermissions`) | Rollenprüfungen ADMIN/MEMBER/GUEST auf Projekt-/Workspace-Ebene, aktueller Nutzer, Profil-Einstellungen (Wochenstart, Datumsformat) | 60 | 03-api-intern-workspace-projekt-user |
| `@/hooks/store/use-project`, `use-project-state`, `use-label`, `use-member`, `use-cycle`, `use-module`, `estimates`, `use-project-view`, `use-global-view`, `use-workspace` | Stammdaten für Gruppen, Dropdowns, Filteroptionen, Feature-Toggles (`cycle_view`, `module_view`, `issue_views_view`), `anchor` (Veröffentlichung) | 44 / 24 / 8 / 21 / 12 / 6 / 6 / 2 / 2 / 2 | 03, 04 |
| `@/hooks/use-timeline-chart` (`apps/web/store/timeline/*`) | Gantt-Zustand (`blocksMap`, Ansicht, `activeBlockId`, Positionsberechnung) | 20 | dieses Dokument 2.5/3.5 |
| `@/hooks/store/use-calendar-view` (`apps/web/store/issue/issue_calendar_view.store.ts`), `use-kanban-view` | Calendar-Navigation, Kanban-Drag-Zustand (Delete-Dropzone) | 4 / 3 | dieses Dokument |
| `@/hooks/store/work-item-filters/*`, `@/hooks/work-item-filters/use-work-item-filters-config`, `@/hooks/rich-filters/use-filters-operator-configs` | Rich-Filter-Instanzen und Feldkonfiguration (Store in `packages/shared-state`) | 4 / 2 / 1 | dieses Dokument 2.11 |
| `@/hooks/use-multiple-select`, `@/hooks/store/use-multiple-select-store`, `@/hooks/use-bulk-operation-status` | Mehrfachauswahl (CE deaktiviert) | 14 / 1 / 4 | dieses Dokument 3.14, 5.4 |
| `@/hooks/store/workspace-draft` | Workspace-Entwürfe | 5 | dieses Dokument 2.17 |
| `@/hooks/store/use-command-palette` | Öffnen des Create-Modals / Shortcut-Modals aus Leerzuständen | 7 | Bereich Command-Palette |
| `@/hooks/store/use-instance` | `config.file_size_limit` (Attachments), `config.has_llm_configured` (AI im Modal) | 1 (+ indirekt `use-file-size`) | 11-frontend-admin-space (Instanz-Konfiguration) |
| `@/hooks/store/use-editor-asset` | Bulk-Status-Update hochgeladener Editor-Assets nach Create/Comment | 2 | 12-editor-echtzeit-live |
| `@/hooks/store/use-project-inbox` | Intake-Varianten (Labels/Attachments) | 1 | Bereich Intake |
| UI-Hooks: `use-platform-os` (Mobil-Erkennung), `use-issue-peek-overview-redirection`, `use-peek-overview-outside-click`, `use-intersection-observer`, `use-keypress`, `use-window-size`, `use-reload-confirmation`, `use-debounce`, `use-auto-scroller`, `use-local-storage`, `use-table-keyboard-navigation`, `use-group-dragndrop`, `use-app-router`, `use-app-theme`, `use-workspace-issue-properties`/`use-project-issue-properties`/`use-issue-properties` | Verhalten 3.x | 38 / 7 / 1 / 5 / 3 / 3 / 2 / 2 / 1 / 1 / 1 / 2 / 6 / 3 / 3+1+1 | 08 · 2.8 |

### 4.2 Services und API-Endpunkte (`apps/web/services/issue/*`, weitere)

| Service-Methode | Endpunkt | Nutzung |
|---|---|---|
| `IssueService.getIssues`/`getIssuesFromServer` | `GET /api/workspaces/{ws}/projects/{pid}/{issues\|epics}/` bzw. `…/{serviceType}-detail/` | Layout-Listen (3.7) |
| `getIssuesForSync` | `GET …/projects/{pid}/v2/{serviceType}/` | lokale Synchronisation (Store) |
| `retrieve`, `retrieveIssues`, `retrieveWithIdentifier` | `GET …/{serviceType}/{id}/`, `…/{serviceType}/list/`, `GET /api/workspaces/{ws}/work-items/{IDENT}-{seq}/` | Peek/Detail, Nachladen einzelner Items, Detail-Route |
| `createIssue`, `patchIssue`, `deleteIssue` | `POST …/{serviceType}/`, `PATCH …/{serviceType}/{id}/`, `DELETE …/{serviceType}/{id}/` | Modal, Quick-Add, Inline-Edit, Delete |
| `updateIssueDates` | `POST …/projects/{pid}/issue-dates/` (`{updates:[{id,start_date,target_date}]}`) | Gantt-Move/Resize |
| `addIssueToCycle`, `removeIssueFromCycle` | `POST …/cycles/{cid}/cycle-issues/`, `DELETE …/cycles/{cid}/cycle-issues/{bridgeId}/` | Cycle-Zuordnung |
| Modul-Zuordnung (`apps/web/services/module.service.ts`) | `POST …/modules/{mid}/issues/` (Items zu Modul), `POST …/issues/{id}/modules/` (Module zu Item, inkl. Entfernen-Liste) | `changeModulesInIssue` (Bereich Module) |
| `subIssues`, `addSubIssues` | `GET/POST …/{serviceType}/{id}/sub-issues/` (Epics: `/issues/`) | Sub-Item-Widget |
| `fetchIssueLinks`, `createIssueLink`, `updateIssueLink`, `deleteIssueLink` | `…/{id}/issue-links/[{linkId}/]` (Epics: `/links/`) | Links-Widget |
| `createIssueRelation`, `deleteIssueRelation` / `IssueRelationService` | `GET/POST …/issues/{id}/issue-relation/`, `POST …/issues/{id}/remove-relation/` | Relations-Widget |
| `IssueArchiveService` | `POST/DELETE/GET …/{serviceType}/{id}/archive/`, `GET …/archived-issues/` | Archiv |
| `getIssueActivities` / `IssueActivityService` | `GET …/{serviceType}/{id}/history/` | Activity |
| `IssueCommentService` | `…/{serviceType}/{id}/comments/[{cid}/]` | Kommentare |
| `IssueReactionService` | `…/{serviceType}/{id}/reactions/[{reaction}/]`, `…/comments/{cid}/reactions/[{reaction}/]` | Reaktionen |
| `IssueAttachmentService` | `/api/assets/v2/workspaces/{ws}/projects/{pid}/{serviceType}/{id}/attachments/[{aid}/]` | Attachments (Presigned Upload) |
| `WorkItemVersionService` | `…/{serviceType}/{id}/description-versions/[{vid}/]` | Versionsverlauf |
| Subscription | `GET/POST/DELETE …/{serviceType}/{id}/subscribe/` | Subscribe-Button |
| `getIssueMetaFromURL` | `GET …/issues/{id}/meta/` | Link-Metadaten |
| `IssueLabelService` | `…/issue-labels/[{lid}/]`, `/api/workspaces/{ws}/labels/` | Label-Anlage aus Dropdown |
| `WorkspaceDraftService` | `/api/workspaces/{ws}/draft-issues/[{id}/]`, `POST /api/workspaces/{ws}/draft-to-issue/{id}/` | Entwürfe |
| `getIssueDisplayProperties`/`updateIssueDisplayProperties` | `…/projects/{pid}/issue-display-properties/` | Legacy, im Frontend nirgends aufgerufen (Anzeige-Properties laufen über `user-properties`) |
| `ProjectService.getProjectUserProperties`/`updateProjectUserProperties` | `…/projects/{pid}/user-properties/` | Persistenz Filter/Display (3.7) |
| `ProjectService.projectIssuesSearch` | `…/projects/{pid}/search-issues/` (Parameter `search`, `parent`, `epic`, `issue_id`, `workspace_search`, `issue_relation`, `sub_issue`, `cycle`, `module`) | Parent-Modal, Existing-Issues-Modal |
| `WorkspaceService.searchEntity` | Mention-Suche im Editor | Modal-Beschreibung, Kommentare |
| `AIService.createGptTask` | `POST /api/workspaces/{ws}/ai-assistant/` | „I'm feeling lucky“ |
| Bulk (CE ohne UI) | `POST …/bulk-operation-issues/`, `DELETE …/bulk-delete-issues/`, `POST …/bulk-archive-issues/`, `POST …/bulk-subscribe-issues/` | s. 5.4 |
| `getDeletedIssues` | `GET …/projects/{pid}/deleted-issues/` | Sync gelöschter Items |

Quellen: `apps/web/services/issue/issue.service.ts`, `issue_archive.service.ts`, `issue_activity.service.ts`, `issue_attachment.service.ts`, `issue_comment.service.ts`, `issue_label.service.ts`, `issue_reaction.service.ts`, `issue_relation.service.ts`, `work_item_version.service.ts`, `workspace_draft.service.ts`, `apps/web/services/project/project.service.ts`. Server-seitige Semantik: `migration/analysis/04-api-intern-arbeitsobjekte.md`.

### 4.3 Andere UI-Bereiche (Komponenten)

| Komponente | Pfad | Verwendung hier |
|---|---|---|
| Mehrfachauswahl (`MultipleSelectGroup`, `MultipleSelectEntityAction`, `MultipleSelectGroupAction`) | `apps/web/components/core/multiple-select/*` | List, Spreadsheet, Gantt (CE deaktiviert) |
| `RenderIfVisible` | `apps/web/components/core/render-if-visible-HOC.tsx` | Virtualisierung List/Kanban/Gantt-Sidebar |
| `ExistingIssuesListModal`, `IssueSearchModalEmptyState`, `GptAssistantPopover` | `apps/web/components/core/modals/*` | „Add an existing work item“ (Cycle/Modul), Relationen, Sub-Items, AI |
| `DateFilterModal` | `apps/web/components/core/filters/date-filter-modal.tsx` | Legacy-Datumsfilter „Custom“ |
| `DescriptionVersionsRoot` | `apps/web/components/core/description-versions/*` | Versionsverlauf |
| Editor-Wrapper `DescriptionInput`, `RichTextEditor`, `LiteTextEditor` | `apps/web/components/editor/*` (+ `@plane/editor`) | Beschreibung, Kommentare (Bereich 12) |
| `CreateUpdateProjectViewModal`, `CreateUpdateWorkspaceViewModal`, `WorkspaceActiveLayout` | `apps/web/components/views/*`, `apps/web/components/workspace/views/modal.tsx` | Save view, Workspace-Views |
| `TransferIssues`, `TransferIssuesModal` | `apps/web/components/cycles/*` | Cycle-Root (abgeschlossene Cycles) |
| `ModuleGanttSidebarBlock` | `apps/web/components/modules` | Gantt-Sidebar für Module |
| `ArchiveTabsList` | `apps/web/components/archives` | Archiv-Kopf |
| `WorkItemsModal` (Analytics) | `apps/web/components/analytics/work-items/modal` | Button „Analytics“ im Kopf |
| `useWorkFlowFDragNDrop` | `apps/web/components/workflow` | CE-Stub für Workflow-Regeln beim DnD |
| `SidebarPropertyListItem`, `LayoutErrorBoundary`, `CountChip`, `BreadcrumbLink`, `TriggerGuard`, `useLayoutMenuItems`, `EmptyStateDetailed`/`SectionEmptyState` | `apps/web/components/common/*`, `apps/web/components/empty-state/*` | Detail-/Peek-Properties, Fehlergrenze, Kopf, Empty-States |
| Layout-Skeletons | `apps/web/components/ui/loader/layouts/*` | 2.22 |
| Intake | `apps/web/components/inbox/*` | nutzt Kachel-Attachments, Label-Inbox-Variante, `IntakeStateSelect` |

### 4.4 Pakete

| Paket | Nutzung (Importe) | Bemerkung |
|---|---|---|
| `@plane/types` (345), `@plane/constants` (101), `@plane/utils` (138), `@plane/i18n` (133) | Typen (`TIssue`, `IIssueDisplayFilterOptions`, `TWorkItemFilterExpression` …), Konstanten (`ISSUE_DISPLAY_FILTERS_BY_PAGE`, `ISSUE_PRIORITIES`, `ISSUE_LAYOUTS`, `DRAG_ALLOWED_GROUPS`, `ISSUE_FORM_TAB_INDICES` …), Hilfsfunktionen (`generateWorkItemLink`, `renderFormattedDate`, `calculateTimeAgo`, `getChangedIssuefields` …) | framework-neutral → als TS-Libraries übernehmen (08 · 5.1) |
| `@makeplane/propel` (Icons 121, Tooltip 33, Menu 25, Icon 23, IconButton 20, Button 8+6, Avatar 7, Collapsible 6, Dialog 5, Popover 4, CircularProgress 3, Field 2, Combobox 2, AvatarGroup 2, Pill 1+1, TextArea, Switch, InputField, Input, Banner, IconButton-Element) | Primitive | als Angular-Bibliothek mit identischem DOM neu (eigener Bereich) |
| `@plane/blocks` (toast 50, property-select 30, layout 30, skeleton 19, icons 15, context-menu 15, select 14, common 13, empty-state 10, emoji-reaction 7, emoji-icon-picker 6, dialog 4, spinner 3, types, breadcrumb) | Composite-Komponenten | als Angular-Bibliothek neu |
| `@plane/shared-state` (10) | Rich-Filter-Store (`FilterInstance`, Konfigurationsmanager) | framework-neutral (MobX) → Port auf Signals |
| `@plane/editor` (10) | Editor-Typen/-Refs, `EditorRefApi` | Bereich 12 |
| `@plane/hooks` (9) | `useOutsideClickDetector` (7), `useLocalStorage` (1), `useHashScroll` (1) | Angular-Pendants (Direktive/Service) |
| Externe Bibliotheken | `mobx-react` (315), `react-hook-form` (18), `lodash-es` (31), `swr` (9), `@atlaskit/pragmatic-drag-and-drop` (`combine` 16, `element/adapter` 12), `@atlaskit/pragmatic-drag-and-drop-auto-scroll` (6), `@atlaskit/pragmatic-drag-and-drop-hitbox/tree-item` (3), `react-dropzone` (5), `lucide-react` (6), `date-fns` (3), `uuid`, `smooth-scroll-into-view-if-needed`, `@base-ui/react/combobox` (1), `next/navigation` (76, Kompatibilitätsschicht) | Importe gezählt über `grep` in den Bereichsverzeichnissen |

---

## 5. Migrationshinweise (.NET / EF Core / Angular)

Grundlage: ADR-000 (Angular v22, .NET 10, EF Core 10, PostgreSQL), ADR-001 (alle Bezahlfunktionen aktiv, kein Upsell), ADR-003 (API-Verträge fachlich wie Original, `snake_case`), ADR-005 (UI 1:1, visuelle Regression). Allgemeine Frontend-Entscheidungen (Store-Port auf Signals, SWR-Ersatz, Trailing-Slash, Tailwind) stehen in `migration/analysis/08-frontend-web-architektur.md` Abschnitt 5 und werden hier nicht wiederholt.

### 5.1 Was 1:1 übertragbar ist

| Original | Ziel | Hinweis |
|---|---|---|
| Reine Logik in `apps/web/components/issues/issue-layouts/utils.tsx` (`isWorkspaceLevel`, `getGroupByColumns`, `getDisplayPropertiesCount`, `highlightIssueOnDrop`, `getSourceFromDropPayload`, `getDestinationFromDropPayload` inkl. Sort-Order-Berechnung mit `sortOrderDefaultValue = 65535`, `getIssueBlockId`, `handleGroupDragDrop`, `removeNillKeys`, `isSubGrouped`, `isIssueNew`, `getApproximateCardHeight`, `getBlockViewDetails`, `isDisplayFiltersApplied`, `isFiltersApplied`, `calculateIdentifierWidth`, `getScopeMemberIds`, `SPREADSHEET_COLUMNS`, `SpreadSheetPropertyIconMap`; Gantt-Reorder `handleOrderChange` in `apps/web/components/gantt-chart/sidebar/utils.ts` mit ±1000) | TS-Funktionen in einer framework-neutralen Library `work-items-core` | Sort-Order-Schritt 65535 bzw. Mittelwert (3.1.4), Gantt 1000 – exakt übernehmen, sonst abweichende Reihenfolgen |
| `@atlaskit/pragmatic-drag-and-drop` (+ `auto-scroll`, `hitbox/tree-item`, `combine`) | **direkt weiterverwenden** (Vanilla-JS) über Angular-Direktiven `draggable`/`dropTarget`, Registrierung in `afterNextRender`, Ausführung via `NgZone.runOutsideAngular` | gleiche Instruktionen (`reorder-above/below`), gleiche Drop-Ziele (Gruppe, Block, Delete-Zone) – Angular CDK DragDrop **nicht** verwenden (andere Vorschau/Placeholder-Optik, kein Hitbox-Modell) |
| Timeline-Mathematik (`apps/web/store/timeline/base-timeline.store.ts`, `apps/web/components/gantt-chart/views/*`, `helpers/*`) | Signal-Store `TimelineStore` | `dayWidth` 60/20/5 (Woche/Monat/Quartal), Positionsberechnung, Scroll-Erweiterung links/rechts |
| Calendar-Payload (`apps/web/store/issue/issue_calendar_view.store.ts`) | Signal-Store | Wochenstart aus Profil, Keys `y-`/`m-`/`w-` |
| Rich-Filter-Store (`packages/shared-state/src/store/rich-filters/*`, `work-item-filters/*`) | Port von MobX auf Signals, gleiche Klassen-/Methodennamen | Ausdrucksformat (`TWorkItemFilterExpression`) unverändert, weil es als JSON an `filters` geht und in Views gespeichert wird |
| Konstanten `ISSUE_DISPLAY_FILTERS_BY_PAGE`, `ISSUE_LAYOUTS`, `ISSUE_ORDER_BY_OPTIONS`, `ISSUE_PRIORITIES`, `DRAG_ALLOWED_GROUPS`, `ISSUE_FORM_TAB_INDICES`, `SPREADSHEET_PROPERTY_LIST`, `VIEWS_LIST`, Operator-Labels | unverändert übernehmen (`packages/constants`) | steuern Sichtbarkeit von Optionen je Seite/Layout |
| Activity-Textabbildung (2.15) | Angular-Komponente je `field` | Texte wörtlich aus i18n (inkl. Leerzeichen-Eigenheiten wie „removed the start date .“) |
| Klassenstrings, Icons, Abstände | identische Tailwind-Klassen in Templates | Grundlage für ADR-005 |
| localStorage-Keys `issue_local_filters`, `spreadsheetViewSorting`, `spreadsheetViewActiveSortingProperty`, `issue_activity_filters`, `activity_sort_order` | identisch | Format exakt (JSON) |
| Request-Verträge (3.7, 4.2) | `HttpClient`-Services gleicher Methodennamen | Cursor-Format, Gruppenfilter-Parameter, `filters`-JSON |

### 5.2 Was neu gebaut werden muss (Angular)

| Thema | Vorgehen | Fallstrick |
|---|---|---|
| `observer`-Komponenten (MobX) | Standalone-Komponenten mit `ChangeDetectionStrategy.OnPush` und Signals; Zeilen-/Kartenkomponenten erhalten nur IDs und lesen Daten per `computed` aus der normalisierten Issue-Map | sonst Re-Render ganzer Listen bei jeder Property-Änderung (Original rendert gezielt pro Block) |
| Virtualisierung `RenderIfVisible` (`apps/web/components/core/render-if-visible-HOC.tsx`) | eigene Direktive mit `IntersectionObserver` (Root = Scroll-Container, Offsets wie Original, Platzhalterhöhe = zuletzt gemessene Höhe bzw. `getApproximateCardHeight`, `forceRender` beim Drag/Peek) | **kein** `cdk-virtual-scroll-viewport`: variable Höhen, Sticky-Gruppenköpfe, Swimlanes und pixelgleiche DOM-Struktur wären nicht erreichbar |
| Pagination per Sentinel (`useIntersectionObserver`) | Direktive, Root-Margin wie Original (`"100% 0% 100% 0%"` in Gantt) | Doppel-Requests verhindern (Loader `pagination` prüfen) |
| Formulare (`react-hook-form`) | Reactive Forms mit identischen Validierungstexten; `dirty`-Tracking für Draft-Rückfrage und `getChangedIssuefields` | Formular-Reset beim Projektwechsel (`getUpdateFormDataForReset`) |
| Portale (`#full-screen-portal`, `spreadsheet-menu-portal`, Base-UI-Portale) | CDK Overlay/Portal; Overlay-Container mit eigenem Marker-Attribut, das die Outside-Click-Logik des Peeks wie `data-base-ui-portal` behandelt | ohne Marker schließt der Peek beim Klick in Menüs (im Original-Kommentar dokumentierter Fehler) |
| Outside-Click/Escape des Peeks | `HostListener('document:mousedown')` mit `event.composedPath()`; Attribute `data-prevent-outside-click`, `data-delay-outside-click` beibehalten | Reihenfolge der Prüfungen exakt wie 3.9 |
| Rechtsklick-Kontextmenü (`@plane/blocks/context-menu`) | CDK Menu mit Positionierung an Mauskoordinaten, gleiche Einträge wie „…“-Menü | Menü muss Peek-Outside-Click ignorieren |
| Toasts inkl. Promise-Toasts (`setPromiseToast`) und Aktions-Toasts | Toast-Service mit Zuständen loading → success/error | Texte/Titel exakt (2.x) |
| Transitions (`RowTransition`, `ElementTransition`, Peek `duration-300`, Quick-Add-Kalender `scale-95`) | CSS-Klassen-Toggles oder Angular Animations mit gleichen Dauern | visuelle Regression filmt Endzustände; Zwischenzustände manuell prüfen |
| `LayoutErrorBoundary` | Angular kennt keine Error Boundaries → Fehler im Layout-Store/Template per `ErrorHandler` + Fallback-Signal je Layout abfangen | Fallback-Optik aus `apps/web/components/common/layout-error-boundary.tsx` |
| Editor-Einbindung (Beschreibung, Kommentare) | Tiptap-Kern ist framework-neutral; React-Wrapper/NodeViews aus `@plane/editor` müssen portiert werden (Bereich 12) | `isEditorReady`/Upload-Status steuert Submit/Discard |
| Spreadsheet-Sticky-Spalte mit Schatten beim horizontalen Scrollen | Direktive (Scroll-Listener, Klassen-/Style-Toggle) | DOM-Manipulation statt Re-Render wie im Original |
| `usePlatformOS` (Mobil-Erkennung) | Service (`navigator.userAgent`) | steuert Peek vs. Navigation, Tooltips aus |
| `useKeypress` | `HostListener('document:keydown')` | Ausnahmen beim Peek-Escape |
| Dropdown-Blocks (`@plane/blocks/property-select`, `select`) | Angular-Komponentenbibliothek mit identischem DOM (eigener Bereich „Design-System“) | Varianten-Skala `pill-*`, `select-ghost-*`, `table-cell`, Suche 300 ms Debounce, Zeilenhöhe 28 px |
| Emoji-Reaktionen | Komponente mit Emoji-Daten aus `packages/constants` (gebündelt, ADR-004) | API-Format: dezimale Codepoints mit „-“ verbunden |

### 5.3 Anforderungen an Backend (.NET/EF Core) aus Sicht dieses Bereichs

| Anforderung | Detail | Quelle |
|---|---|---|
| Listen-Endpunkte mit Gruppierung/Subgruppierung, Cursor-Pagination und Rich-Filter-JSON | Antwortformat `TIssuesResponse` (`packages/types/src/issues/issue.ts`), Gruppen-ID „None“ für leere Werte, `total_count` je Gruppe | 3.7, 08 · 5.3 |
| `order_by`-Werte inkl. `-`-Präfix und Sortierung nach Relationen (Labels, Assignees, Cycle, Module, Estimate, State-Gruppe, Priorität) | serverseitig identisch, weil Client nur innerhalb geladener Seiten sortiert | `packages/constants/src/issue/common.ts` (`ISSUE_ORDER_BY_OPTIONS`), `apps/web/components/issues/issue-layouts/spreadsheet/*` |
| `sort_order` als `double precision` | Werte aus 65535-Schritten/Mittelwerten; EF-Core-Typ `double` | 3.1.4 |
| Sammel-Update der Daten | `POST …/issue-dates/` mit `{updates:[{id,start_date,target_date}]}` in einer Transaktion | `apps/web/services/issue/issue.service.ts` |
| Pro-Nutzer-Ansichtseinstellungen | Entität `ProjectUserProperty` (bzw. Cycle/Modul/Workspace-View) mit `jsonb`-Spalten `rich_filters`, `display_filters`, `display_properties` (Npgsql `jsonb`-Mapping) | 3.7 |
| Archivregel | nur State-Gruppen `completed`/`cancelled`; Bulk-Fehlertext „Only work items belonging to Completed or Canceled state groups can be archived.“ | `packages/constants/src/state.ts`, `bulk_operations.error_details.invalid_archive_state_group` |
| Löschregel | nur Ersteller oder Projekt-Admin; Fehlertext „Only admin or creator can delete the …“ | 2.18 |
| Relationstypen inkl. Paar-Mapping | Vorwärts/Rückwärts: `blocked_by`↔`blocking`, `relates_to`↔`relates_to`, `duplicate`↔`duplicate`, `start_before`↔`start_after`, `finish_before`↔`finish_after`, `implemented_by`↔`implements` | `apps/api/plane/db/models/issue.py` (`IssueRelationChoices._RELATION_PAIRS`), `apps/api/plane/app/views/issue/relation.py` |
| Entwürfe | eigene Entität Draft (Workspace-Ebene) + Umwandlung `draft-to-issue` | `apps/web/services/issue/workspace_draft.service.ts` |
| Kommentar-Antworten | Datenmodell hat bereits `IssueComment.parent` (`apps/api/plane/db/models/issue.py`); API für Replies neu (ADR-001) | 5.4 |
| Bulk-Endpunkte | CE-Backend registriert nur `bulk-delete-issues` und `bulk-archive-issues` (`apps/api/plane/app/urls/issue.py`); `bulk-operation-issues` und `bulk-subscribe-issues` werden vom Frontend-Service bereits angesprochen und sind **neu** zu implementieren | 5.4 |
| Instanz-Konfiguration | `file_size_limit` (Default 5 MB im Client), `has_llm_configured` (lokaler LLM-Provider, ADR-004) | 2.14, 2.16 |
| Such-Endpunkt `search-issues` | Parameter `search`, `parent`, `epic`, `issue_id`, `workspace_search`, `issue_relation`, `sub_issue`, `cycle`, `module` mit identischer Ausschlusslogik (eigene Items, bereits verknüpfte) | `apps/web/services/project/project.service.ts`, `apps/web/components/core/modals/existing-issues-list-modal.tsx` |

### 5.4 Bezahlfunktionen dieses Bereichs – konkret zu bauen (ADR-001)

| Funktion | Erweiterungspunkt im CE-Code | Zu bauen (Frontend) | Zu bauen (Backend) |
|---|---|---|---|
| **Bulk Operations** (Mehrfachauswahl + Massenänderung) | `useBulkOperationStatus()` → `false` (`apps/web/hooks/use-bulk-operation-status.ts`); `MultipleSelectGroup`/`EntityAction`/`GroupAction` (`apps/web/components/core/multiple-select/*`); `IssueBulkOperationsRoot` (Upsell-Banner, `apps/web/components/issues/bulk-operations/root.tsx`); `enableSelection` im Gantt; Payload `TBulkOperationsPayload {issue_ids, properties: Partial<state_id, priority, label_ids, assignee_ids, start_date, target_date, module_ids, cycle_id, estimate_point>}` | Statt Banner: Aktionsleiste (sticky unten, Höhe wie Banner `h-20`) mit Auswahlzähler, Property-Selects für alle `TBulkIssueProperties`, Archivieren, Löschen, Abonnieren, Auswahl aufheben; Tastatur (↑/↓, Shift+↑/↓, Shift-Klick) aus `use-multiple-select.ts` aktivieren; Gruppen-Checkbox (`isGroupSelected` empty/partial/complete) | `POST bulk-operation-issues` (Validierungen mit Fehlercodes: `invalid_archive_state_group`, `invalid_issue_start_date`, `invalid_issue_target_date`, `invalid_state_transition`), `bulk-subscribe-issues` |
| **Workflows** (erlaubte State-Übergänge) | `useWorkFlowFDragNDrop` → `{workflowDisabledSource, isWorkflowDropDisabled, getIsWorkflowWorkItemCreationDisabled, handleWorkFlowState}` (Stub in `apps/web/components/workflow/use-workflow-drag-n-drop.ts`, genutzt in `list/list-group.tsx`, `kanban/default.tsx`, `kanban/kanban-group.tsx`, `kanban/swimlanes.tsx`); State-Select-Hinweis auf EE-Ressource mit `allowedStateIds` | Drop-Sperre/Overlay für nicht erlaubte Ziel-States, Quick-Add-Sperre je Gruppe, gefilterte State-Optionen im `StateSelect` | Workflow-Definition je Projekt/Typ, serverseitige Prüfung (`invalid_state_transition`) |
| **Teamspaces** | Store-Typen `TEAM`, `TEAM_VIEW`, `TEAM_PROJECT_WORK_ITEMS`; Gruppierung `team_project` (`getTeamProjectColumns()` → `undefined`) | Layout-Roots für Teamspace-Work-Items/-Views, Gruppierung nach Teamspace-Projekt | Teamspace-Listen-Endpunkte (eigener Bereich) |
| **Duplizieren in anderes Projekt** | `createCopyMenuWithDuplication` gibt nur `baseItem` zurück; Prop `setDuplicateWorkItemModal` (`quick-action-dropdowns/copy-menu-helper.tsx`) | Untermenü „Make a copy“ → „In anderes Projekt …“ mit Projekt-Auswahl-Modal | Duplizier-Endpunkt (Kopie inkl. wählbarer Bestandteile) |
| **Epics** | `CreateUpdateEpicModal` rendert nichts (`apps/web/components/epic-modal/modal.tsx`); `ProjectEpicsEmptyState` leer; `EIssuesStoreType.EPIC`; Service-Typ `epics` (Endpunkte `…/epics/…`, Links `/links/`, Kinder `/issues/`); `isEpic`-Zweige in Layouts („All Epics“, „New Epic“, Display-Property `sub_issue_count` ausgeblendet) | Epic-Modal, Epic-Liste/-Layouts, Epic-Detail (eigene Feature-Analyse) | Epic-Endpunkte |
| **Work-Item-Typen, Custom Properties, Vorlagen, Konvertierung** | `IssueModalProvider`-Stubs (`getIssueTypeIdOnProjectChange`, `getActiveAdditionalPropertiesLength`, `handlePropertyValuesValidation`, `handleCreateUpdatePropertyValues`, `handleProjectEntitiesFetch`, `handleTemplateChange`, `handleConvert`, `handleCreateSubWorkItem`, `workItemTemplateId`, `isApplyingTemplate`, `issuePropertyValues`); `IssueTypeSwitcher` zeigt nur Identifier; Formularfeld `type_id` | Typ-Auswahl im Modal-Kopf, dynamische Zusatzfelder (Validierung, Speicherung nach Create/Update), Vorlagenauswahl, Typwechsel im Detail/Peek, „Convert“ (Work Item ↔ Epic) | Typen-/Property-/Template-Endpunkte |
| **Erweiterte Filter** | `EXTENDED_*`-Operatoren leer (`packages/types/src/rich-filters/operators/extended.ts`), `allowNegative = false` (`apps/web/hooks/rich-filters/use-filters-operator-configs.ts`), Negations-Labels (`packages/constants/src/rich-filters/operator-labels/extended.ts`) | zusätzliche Operatoren und Negation im Operator-Select des Filter-Chips, ggf. OR-Verknüpfung | Filter-Parser mit denselben Operatoren |
| **Timeline-Abhängigkeiten** | `isDependencyEnabled = false` (`apps/web/store/timeline/base-timeline.store.ts`), `ENABLE_ISSUE_DEPENDENCIES = false` (`packages/constants/src/issue/filter.ts`), Prop `enableDependency` und Typ `IBlockUpdateDependencyData`, `getIsCurrentDependencyDragging` in `gantt-chart/*`; Relationstypen `start_before`/`start_after`/`finish_before`/`finish_after` im Backend vorhanden, im Frontend-Typ `TIssueRelationTypes` nicht | Verbindungslinien, Ziehen von Abhängigkeiten an Balkenenden, Relationen im Widget, `expand=issue_relation,issue_related` beim Gantt-Fetch | Relations-API inkl. Dependency-Typen, `…-detail/`-Antwort mit Relationen |
| **Relation „implements/implemented by“** | nur Backend (`IssueRelationChoices.IMPLEMENTED_BY`) | Relationstyp in `ISSUE_RELATION_OPTIONS` (`apps/web/components/relations/index.tsx`) und Activity-Text | vorhanden im Modell |
| **Kommentar-Antworten** | Prop `enableReplies` ungenutzt (`apps/web/components/comments/card/root.tsx`); i18n `issue.comments.replies.*` („Add reply“, „Reply created successfully“, „Failed to create reply“, „Reply updated successfully“, „Failed to update reply“, „Reply deleted successfully“, „Failed to delete reply“, „Failed to fetch replies“) | Antwort-Thread unter Kommentaren mit Eingabe „Add reply“ | Replies-Endpunkte auf `IssueComment.parent` |
| **Gescopte/paginierte Selects** | Hinweise in `dropdowns/state/state-select.tsx` (Workflow-Gating), `dropdowns/member/member-select.tsx` (paginierter Scope), `dropdowns/label/label-select.tsx` (Label-Scopes work item/release/initiative/project) | `Select` im Infinite-Modus (`getValues(params)`), Scope-Parameter | paginierte „lite“-Endpunkte |
| **Upsell entfernen** | Banner „Upgrade to One“ (`bulk_operations.upgrade_banner.*`) | entfällt, ersetzt durch echte Leiste | – |

### 5.5 Fallstricke

1. **Store-Kontext statt Route**: Jede Liste ermittelt ihren Store über `IssuesStoreContext` mit Route-Fallback (3.1.1). In Angular per `InjectionToken` je Route-Komponente bereitstellen; falscher Kontext führt zu Updates im falschen Listen-Cache.
2. **View-Flags** (`enableQuickAdd`, `enableIssueCreation`, `enableInlineEditing`) sind pro Store unterschiedlich (3.1.2) und steuern Quick-Add, „+“ und Inline-Edit – Tabelle 3.1.2 als Testmatrix verwenden.
3. **Display-Filter-Regeln** (3.7) sind clientseitig; ein reiner Server-Default reicht nicht (Kanban ohne `group_by` → `state`, `group_by = null` → `sub_group_by = null`, `group_by == sub_group_by` → `sub_group_by = null`).
4. **Layoutwechsel leert den Cache**, `order_by`/`sub_issue`/`type` laden neu, `group_by` lädt über Komponenten-Effekte – beim Port auf Signals dieselben Auslöser einhalten, sonst Doppel-Requests oder veraltete Gruppen.
5. **Optimistische Anlage** (Quick-Add mit `tempId`): Items sind bis zur Serverantwort nicht peek-bar und nicht ziehbar; Fehler entfernen das Item wieder.
6. **Outside-Click-Semantik** des Peeks (3.9) ist fehleranfällig; jede neue Overlay-Komponente muss den Portal-Marker tragen.
7. **Unterschiedliche Leere-Gruppen-Defaults**: List blendet leere Gruppen aus, Kanban zeigt sie (`show_empty_groups`), Base-Layouts ebenso.
8. **Mobile Abweichungen**: Peek → Navigation; Detail-Properties inline < 768 px; Calendar-Mobilansicht; Layout-Auswahl im Kopf unter `@4xl` als Menü. Visuelle Regression mit mindestens den Breakpoints `sm`, `md`, `lg`, `xl`, `2xl`, `3xl`.
9. **Zeitzonen/Datumslogik**: Datumswerte sind Kalendertage (`YYYY-MM-DD`), Calendar-Gruppen nach `target_date`; Datums-Pills berechnen „überfällig“ clientseitig – Serialisierung ohne Zeitanteil (`DateOnly` in .NET).
10. **Texte mit Eigenheiten** (doppelte Leerzeichen, fehlende Punkte, „cycle“-Text bei Modulen) – bei 1:1-Anspruch übernehmen oder bewusst korrigieren (Offene Punkte).
11. **Performance**: Original lädt bis zu 100 Items je Seite und virtualisiert; Angular-Templates mit `@for (…; track id)` und ID-basierten Kindkomponenten bauen.

### 5.6 Teststrategie für diesen Bereich

| Ebene | Inhalt |
|---|---|
| Unit (TS-Core) | `getGroupByColumns` je `group_by`, Sort-Order-Berechnung (oben/unten/zwischen), Drop-Payload-Auswertung, Display-Filter-Regeln, Cursor-Erzeugung, Activity-Textabbildung, `formatDateRange`/`mergeDates` |
| Komponenten | jede Inventarzeile aus Abschnitt 2 mit Zustandsvarianten (leer, Laden, Fehler, disabled, archiviert, mobil) |
| E2E (Playwright) | DnD zwischen Gruppen/Subgruppen, Reorder, Calendar-Datum, Gantt Move/Resize/Reorder, Kanban-Löschzone, Quick-Add je Layout, Peek-Modi + Outside-Click + Escape, Modal-Draft-Rückfrage, Rich-Filter hinzufügen/ändern/speichern, Spreadsheet-Tastatur |
| Visuelle Regression (ADR-005) | Referenz-Screenshots des Originals für alle Layouts × Gruppierungen × Display-Properties, Skeletons (2.22), Empty-States (2.9), Peek/Detail/Modal, Dropdown-Varianten (2.19) |
| Contract | Request-Parameter (3.7) und Antwortformen gegen das Original-Backend |

---

## 6. Offene Punkte

| # | Punkt | Vorschlag / Rückfrage |
|---|---|---|
| O1 | Für die Bezahlfunktionen dieses Bereichs (Bulk-Aktionsleiste, Workflow-Sperren, Epic-Modal/-Layouts, Typ-Auswahl und Custom-Property-Felder im Modal, Vorlagenauswahl, Gantt-Abhängigkeitslinien, Kommentar-Antworten, erweiterte Filteroperatoren, Duplizieren in anderes Projekt) enthält das CE-Repo **keine UI** – nur Erweiterungspunkte (5.4). Ein 1:1-Nachbau ist ohne Referenz nicht möglich. | Rückfrage an Auftraggeber: Zugang zu einer Plane-Business/Enterprise-Referenzinstanz für Screenshots und Abläufe (deckt sich mit O1 in `migration/analysis/08-frontend-web-architektur.md`). Bis dahin Gestaltung aus vorhandenen Bausteinen ableiten (Banner-Fläche `h-20` für die Bulk-Leiste, Operator-Select des Filter-Chips, Relations-Widget). |
| O2 | Welche erweiterten Filteroperatoren (und Negationen) gibt es in den Bezahl-Editionen? `EXTENDED_*` ist in CE leer. | Rückfrage bzw. Ableitung aus Referenzinstanz; Parser im .NET-Backend erweiterbar auslegen. |
| O3 | Edge-Cases 3.15 (insbesondere #3 Leertaste, #5 falscher Wert im Cycle-Activity-Text, #4 „None“-Payload, #10 falscher Toast-Text, #16 Calendar-Skeleton mit 5 Spalten) – 1:1 nachbauen oder korrigieren? | Empfehlung: funktionale Fehler (#3, #4, #5, #10) korrigieren, rein visuelle Eigenheiten (#15, #16) beibehalten; Entscheidung dokumentieren, da ADR-005 Pixelgleichheit fordert. |
| O4 | Peek-Zustand ist nicht in der URL (3.9, #17). | Beibehalten (1:1) oder optional `?peekId=` ergänzen (Router-Getter `peekId` existiert bereits in `apps/web/store/router.store.ts`) – Entscheidung Produkt. |
| O5 | Ungenutzter Code (3.15 #9: Legacy-Links, `IssueRelationSelect`, `base-layouts/*`, `readonly/*`, `CommentsWrapper`, Legacy-Endpunkt `issue-display-properties`). | Empfehlung: `base-layouts/*` und `readonly/*` als generische Bausteine portieren (vermutlich von Bezahl-Entitäten genutzt), übrige Legacy-Teile nicht portieren. |
| O6 | Peek-Modus wird nicht persistiert (immer „Side Peek“ beim Öffnen). | 1:1 beibehalten. |
| O7 | Mehrfachauswahl-Tastatur (`use-multiple-select.ts`) registriert globale `keydown`-Listener auf `window` – Konflikte mit anderen Shortcuts bei aktivierten Bulk Operations. | Beim Aktivieren (ADR-001) Fokus-Scope einführen und gegen globale Shortcuts testen. |
| O8 | Calendar nutzt in allen Kontexten die View-Flags des PROJECT-Stores (#2). | Prüfen, ob in Cycle/Modul/Archiv Quick-Add korrekt gesperrt sein soll; Empfehlung: Flags des aktiven Stores verwenden. |
| O9 | Workflow-Gating im State-Select (EE „lite“-Ressource) – Verhalten bei nicht erlaubten Übergängen (ausgegraut vs. ausgeblendet, Tooltip-Texte) unbekannt. | Referenzinstanz (O1). |
| O10 | AI-Funktionen im Modal hängen an `has_llm_configured`; Limit-Text „50 requests per month per user“ stammt aus der Cloud. | Bei lokalem LLM (ADR-004) Limit konfigurierbar machen oder Text anpassen – Rückfrage. |
| O11 | Visuelle Regression benötigt deterministische Skeletons; Original verwendet Zufallsbreiten/-anzahlen (`getRandomLength`, `getRandomInt`). | In Tests Seed/Mock für Zufallswerte vorsehen. |
