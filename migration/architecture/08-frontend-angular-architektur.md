# 08 – Frontend-Architektur Angular (web, admin, space)

> **Status:** verbindlich für das Thema Frontend (Fachdokument zu `01-zielarchitektur-und-tech-stack.md`, Anhang A: „Routen-Mapping, Store-Mapping, Library-Mapping, Registries“).
> **Rangfolge:** `00-grundsatzentscheidungen.md` (ADR-000 … ADR-009) > `01-zielarchitektur-und-tech-stack.md` (ADR-010 … ADR-052) > **dieses Dokument (D08-ADR-01 ff.)** > eigene Präferenzen. Bei Widerspruch gilt 01 bis zur ADR-Änderung; Ergänzungen dieses Dokuments, die 01 präzisieren, sind in Abschnitt 2 als solche markiert.
> **Stand:** 23.10.2026. **Zielrepository:** `funk.` (ADR-009). Alle Zielpfade sind relativ zu dessen Wurzel; der Angular-Workspace liegt unter `frontend/` (01 §6.1). *Hinweis:* 01 §5.1 nennt noch den Arbeitstitel `plane-net/`; maßgeblich ist ADR-009 (`funk.`), die Verzeichnisstruktur unterhalb der Wurzel bleibt unverändert.
> **Sprache:** Fließtext Deutsch, Bezeichner Englisch.
> **Kürzel für Original-Pfade** (wie 01): `WEB/` = `apps/web/`, `ADM/` = `apps/admin/`, `SPC/` = `apps/space/`, `PKG/` = `packages/`. Analyse-Dokumente: `A08` = `migration/analysis/08-frontend-web-architektur.md`, `A09` = `…/09-frontend-arbeitsobjekte-layouts.md`, `A10a`/`A10b` = Screens, `A11` = Admin/Space, `A12` = Editor/Live, `A13a` = Designsystem, `A13b` = Shared Packages/i18n. Ziel-Kürzel: `FE/` = `funk./frontend/`.

## Inhaltsverzeichnis

1. [Ziel & Scope](#1-ziel--scope)
2. [Entscheidungen (D08-ADR-01 ff.)](#2-entscheidungen-d08-adr-01-ff)
3. [Detaildesign](#3-detaildesign)
   - 3.1 Workspace, Apps, Base-Paths, Libraries, Modulgrenzen
   - 3.2 Bootstrap & Provider-Kette
   - 3.3 Routing (Reihenfolge, Trailing Slash, In-Place-Guard-States, Redirects, Titel/Meta)
   - 3.4 State-Management (MobX → Signal-Stores, Issue-Store)
   - 3.5 Datenzugriff (HttpClient, Interceptors, QueryCache als SWR-Ersatz)
   - 3.6 Formulare
   - 3.7 i18n
   - 3.8 Theming
   - 3.9 Interaktions- und Layout-Bausteine (DnD, Virtualisierung, Command-Palette, Picker, Charts, Gantt, Kanban, Spreadsheet, Kalender, Masonry, Dropzone, Overlays)
   - 3.10 Shortcuts
   - 3.11 Runtime-Config
   - 3.12 Realtime im Frontend (Hocuspocus, Live-Events)
   - 3.13 Performance
   - 3.14 Fehlerbehandlung, Status- und Fehlerseiten
   - 3.15 Browser-Storage
4. [Vollständige Mapping-Tabellen Original → Ziel](#4-vollständige-mapping-tabellen-original--ziel)
5. [Code-Skelette](#5-code-skelette)
6. [Erweiterungspunkte für Bezahl-Pakete](#6-erweiterungspunkte-für-bezahl-pakete)
7. [Akzeptanzkriterien & Tests](#7-akzeptanzkriterien--tests)
8. [Risiken & offene Punkte](#8-risiken--offene-punkte)
9. [Abhängigkeiten zu anderen Dokumenten (02–16)](#9-abhängigkeiten-zu-anderen-dokumenten-0216)

---

## 1. Ziel & Scope

### 1.1 Ziel

Die drei React-SPAs des Originals (`apps/web`, `apps/admin`, `apps/space`, Plane v1.4.2 CE) werden als **ein Angular-22-Workspace mit drei Apps** nachgebaut, sodass

1. **Routen, Layout-Verschachtelung, Guards, Redirects und Trailing-Slash-Verhalten** identisch sind (gleiche URLs, gleiche Zustände bei Direktaufruf, gleiche Weiterleitungsziele inkl. Query und abschließendem `/`),
2. **jeder MobX-Store** strukturgleich (gleicher Dateiname, Klassenname, Feld-, Computed- und Methodenname, gleiche Optimismus-/Revert-Semantik) als Signal-Store existiert und die **reinen TS-Algorithmen** (Gruppierung, Sortierung, Pagination, Sort-Order, Distribution-Updates, Rich-Filter) **unverändert** übernommen werden,
3. die **HTTP-Verträge** (Pfade, Methoden, Query-Parameter, Fehlerauswertung) mit dem Original übereinstimmen (ADR-003, ADR-047),
4. das **DOM** pixelgleich ist (ADR-005, 01 §7.17) – geprüft durch Visual- und DOM-Snapshot-Tests,
5. der Workspace **ohne Laufzeit-Node** und **ohne externe Ressourcen** (Airgap, ADR-004) ausgeliefert wird,
6. die 🧱-Erweiterungspunkte (01 §1.4, §6.4) im Frontend **ab dem genannten Inkrement** existieren, ohne Bezahl-Features fachlich vorzuplanen.

### 1.2 Scope

| Im Scope | Nicht im Scope (anderes Dokument) |
|---|---|
| Workspace-Aufbau, Apps, Base-Paths, Libraries, Sheriff-Regeln | Komponenten-Port Propel/Blocks im Detail (Variantentabellen) → `09-ui-paritaet-designsystem.md` |
| Routing aller drei Apps (vollständige Tabellen §4.1–§4.3) | Editor-Extensions, NodeViews, Schema-Freeze → `10-editor-angular.md` |
| State-Management inkl. Mapping **aller** 100 Store-Dateien aus `WEB/store`, 5 aus `ADM/store`, 16 aus `SPC/store`, `PKG/shared-state` | Suche/Power-K-**Backend**, AI-Provider → `11-suche-und-ai-basis.md` |
| Datenzugriff (HttpClient, Interceptors, QueryCache), Upload-Client | API-Endpunktkatalog → `04-api-design-und-endpunktkatalog.md` |
| Formulare, i18n, Theming, Shortcuts, Runtime-Config, Performance, Fehlerseiten | Keycloak-Realm, Login-Theme, Permission-Matrix → `05-auth-sicherheit-berechtigungen.md` |
| Interaktionsbausteine (DnD, Virtualisierung, Command-Palette, Emoji-/Date-Picker, Charts, Gantt, Kanban, Spreadsheet) – **Architektur** und Bibliothekswahl | Hocuspocus-Serverprotokoll → `07-realtime-kollaboration-dokumente.md` |
| Library-Mapping **jeder** Abhängigkeit aus `apps/*/package.json` und `packages/*/package.json` (inkl. Root) | Testpyramide/Quality-Gates gesamt → `15-teststrategie-qualitaet-paritaet.md` |
| Frontend-Erweiterungspunkte (Registries) für 🧱-Pakete | Fachdesign der Bezahl-Pakete → je Welle W1…W9, Andockstellen gesamt → `16-erweiterungspunkte-bezahl-features.md` |

### 1.3 Welcher Teil wird in welchem Inkrement gebraucht

Inkremente gemäß 01 §1.3. Ein Baustein wird **im genannten Inkrement vollständig** gebaut (mit Tests), vorher existiert er nicht (01 §7.19: keine Platzhalter-Routen).

| Baustein (Abschnitt) | I0 | I1 | I2 | I3 | I4 | I5 | I6 | I7 |
|---|---|---|---|---|---|---|---|---|
| Workspace, Sheriff, Lint, Vitest, Playwright-Gerüst (§3.1, §7) | ● | | | | | | | |
| `libs/shared/{types,constants,utils,i18n,tailwind-config,state-kit,runtime-config,cdk}` (§3.1) | ● | | | | | | | |
| `libs/shared/services` (APIService-Basis + Auth/User/Workspace/Instance/Project) | ● | ◐ | ◐ | ◐ | ◐ | ◐ | ◐ | |
| Bootstrap, Inline-Theme-Script, ThemeService, TitleStrategy, Progressbar, Stale-Chunk-Recovery (§3.2, §3.8, §3.14) | ● | | | | | | | |
| Routing-Kern: Trailing-Slash, `AppRouter`, `PathnameService`, RouterStore, Splat-Matcher (§3.3) | ● | | | | | | | |
| Wrapper `AuthenticationWrapper`, `InstanceWrapper`, `StoreWrapper`, `WorkspaceAuthWrapper` (§3.3.4) | ● | | | | | | | |
| `ProjectAuthWrapper` | ◐ (Projekt-Kern) | ● | | | | | | |
| QueryCache (SWR-Ersatz), Interceptors, Fehler-Mapping (§3.5) | ● | | | | | | | |
| Workspace-Shell (Top-Navigation, Sidebar, Header, `ContentWrapper`), Propel-Primitive Button/Input/Menu/Tooltip/Avatar | ● | | | | | | | |
| Signal Forms + Formular-Bausteine (§3.6) | ◐ (Create-Workspace/-Project) | ● | | | | | | |
| i18n Sprachwechsel, Profil-Sync (§3.7) | ◐ (Laden, `t`) | ● | | | | | | |
| Custom Theme, High Contrast, Theme-Persistenz (§3.8) | ◐ (light/dark/system) | ● | | | | | | |
| Settings-Rahmen, Settings-Registry `SETTINGS_PAGES` | | ● | | | | | | |
| Sidebar-Registry `SIDEBAR_ITEMS`, Favoriten | ◐ (statische Items) | ● | | | | | | |
| Issue-Store (IssueRootStore, 9 CE-Listen-Stores, Detail-Store), `work-items-core` (§3.4.6) | | | ● | | | | | |
| DnD-Direktiven, `RenderIfVisible`, Sentinel-Pagination (§3.9) | | ◐ (Labels-DnD) | ● | | | | | |
| List/Kanban/Spreadsheet/Calendar/Gantt (§3.9) | | | ● | | | | | |
| Rich-Filter (`libs/shared/shared-state`), `FILTER_FIELDS`, `PROPERTY_RENDERERS`, `RELATION_TYPES` | | | ● | | | | | |
| Lite-Editor (Kommentare/Beschreibung) | | | ● | | | | | |
| Charts (D3) | | | | ● | | | | |
| Date-Picker (Propel `Calendar`) | | | ● | | | | | |
| Emoji-/Icon-Picker, Emoji-Reaktionen | | ◐ (Logo-Picker Projekt) | ● | | | | | |
| Pages, Rich/Document-Editor, Hocuspocus-Provider (§3.12) | | | | | ● | | | |
| Power-K, Shortcuts (§3.10) | ◐ (`cmd+k` öffnet leere Palette nicht – erst I5) | | | | | ● | | |
| Live-Events (SignalR, H6-Andockstelle) | ● (Service, ohne Handler) | | | | | ● (Notification-Zähler) | | |
| Masonry (Stickies) | | | | | | ● | | |
| Admin-App vollständig | ◐ (Einstieg, General) | | | | | | ● | |
| Space-App | | | | | | | ● | |
| Airgap-Prüfungen, Bundle-Budgets final, Visual-Abnahme aller Screens | | | | | | | | ● |

● = in diesem Inkrement fertig · ◐ = Teilumfang (in Klammern)

---

## 2. Entscheidungen (D08-ADR-01 ff.)

| ID | Belang | Entscheidung | Alternativen (verworfen) | Begründung | ab |
|---|---|---|---|---|---|
| **D08-ADR-01** | Workspace-Werkzeug | Angular-CLI-Multi-Project-Workspace + pnpm + Sheriff (bestätigt ADR-039). Libraries ohne eigenen Build (TS-Path-Mapping), Apps `web`, `admin`, `space`; Builder `@angular/build:application` | Nx; separate Lib-Builds mit ng-packagr | 01 verbindlich; keine Lib-Builds = schnellere Agenten-Zyklen | I0 |
| **D08-ADR-02** | Ablage der Stores und Services (Präzisierung 01 §6.2/§6.3) | Stores liegen gemäß 01 in `libs/web/<domäne>/state/`, Services in `libs/web/<domäne>/services/`. **Sheriff-Ebenen**: `layer:state` und `layer:services` bilden je einen Cluster, in dem jede Domäne jede andere über deren `state/public-api.ts` bzw. `services/public-api.ts` importieren darf (entspricht dem Objektgraphen des Original-`RootStore`); nur `layer:ui` folgt der Domänen-Matrix (§3.1.5) | alle Stores in einer Lib `libs/web/state` (bricht 01-Ablage); strenge Matrix auch für Stores (unmöglich: Issue-Root ↔ Cycle ↔ Module ↔ Project sind zyklisch verknüpft) | Store-Code wird 1:1 portiert, inklusive seiner Querbezüge; Zyklen sind nur zur Laufzeit (über `inject()`), nicht bei Modul-Auswertung vorhanden | I0 |
| **D08-ADR-03** | Signal-Store-Form | Klassen-Stores als `@Injectable({providedIn:'root'})` (Singleton wie `store-context.tsx`); Unter-Stores (z. B. 13 Issue-Listen-Stores, Page-Instanzen, Estimate-Instanzen) als **plain classes**, die vom Eltern-Store mit `new` erzeugt werden (wie Original) | NgRx SignalStore (`signalStore()`), Store je Route | 1:1-Portierbarkeit (ADR-040); Unterinstanzen entstehen im Original ebenfalls per `new` | I0 |
| **D08-ADR-04** | MobX-Primitive → Signal-Primitive | Feste Übersetzungstabelle (§3.4.2) mit Bausteinen aus `libs/shared/state-kit`: `signal` (observable.ref), `EntityMap<T>` (observable Record/Map normalisierter Objekte, ein Signal je Schlüssel), `DeepState<T>` (tief verschachtelte observables, s. ADR-05), `memoizedComputed` (`computedFn`), `reactionEffect` (`reaction`), `effect` (`autorun`), `untilSignal` (`when`), `persisted()` (localStorage-gebundene Signale) | manuelle Neuentwicklung je Store | Mechanisch anwendbar, review-bar gegen Original-Datei | I0 |
| **D08-ADR-05** | Tiefe, pfadbasierte Mutationen (lodash `set`/`update`/`unset` auf observables) | **`DeepState<T>`**: hält ein mutables Plain-Objekt + Versions-Signal; Schreib-API `set(path, v)`, `update(path, fn)`, `unset(path)` (lodash-Semantik, ersetzt Blatt-Referenzen) inkrementiert die Version; Lese-API `get(path)` liest Version + Pfad; pro Pfad memoisierte `select(path)`-Signale mit `Object.is`-Gleichheit liefern nur bei geänderter Blatt-Referenz neue Werte | Immer/immutable Copy-on-Write (Rewrite der Store-Algorithmen, Kosten bei 10k Items); strukturiertes Klonen (zu teuer) | Original-Code (`set(this.groupedIssueIds, …)`, `update(this.issuesMap, …)`) bleibt fast wörtlich erhalten; feingranulare Updates je Gruppe bleiben erhalten | I0 (state-kit), I2 (Issue-Store) |
| **D08-ADR-06** | Zugriff zwischen Stores (`this.rootStore.x.y`) | `this.rootStore.<pfad>` wird zu einem per `inject()` gehaltenen Feld (`private readonly cycle = inject(CycleStore)`); Zyklen über `injectLazy(() => X)` (state-kit, `Injector.get` beim ersten Zugriff). Es gibt einen dünnen `RootStore` in `libs/web/core/state/root.store.ts` nur für `resetOnSignOut()` und als Kompatibilitätsfassade (Getter auf die Stores, nur für portierten Code, der den Root als Ganzes übergibt) | ein God-Object-RootStore mit allen Stores als Felder (erzwingt `core` → alle Domänen) | Hält `core` frei von Domänen-Imports (Sheriff), Laufzeitgraph identisch | I0 |
| **D08-ADR-07** | `resetOnSignOut()` | Setzt `localStorage.theme = "system"` und Sprache `en` wie Original und löst den Formular-POST `/auth/sign-out/` aus; Stores werden **nicht** neu instanziiert, weil der Sign-out eine Vollnavigation (Server-Redirect → Keycloak-Logout → Neuladen) ist | Session-Injector, der Stores verwirft | Gleiches beobachtbares Verhalten bei weniger Mechanik | I0 |
| **D08-ADR-08** | Datenabruf (SWR-Ersatz) | Eigener **`QueryCache`** in `libs/shared/state-kit` mit SWR-2.4-Semantik: globale Schlüssel (`fetch-keys.ts` + Literal-Keys unverändert), Deduplizierung 2 000 ms, `revalidateOnFocus` (Throttle 5 000 ms), `revalidateOnReconnect`, `revalidateIfStale`, `revalidateOnMount`, `refreshInterval`, `refreshWhenHidden`, `errorRetryCount` mit exponentiellem Backoff (Basis 5 000 ms), `shouldRetryOnError`, globales `mutate(key)`; Konsum per `injectQuery(keyFn, fetcher, options)` in Komponenten/Wrappern. Die Fetcher rufen **Store-Actions** wie im Original | `@tanstack/angular-query-experimental` (Status „experimental“, andere Semantik); `httpResource` (kein globaler Key-Cache, keine Fokus-Revalidierung) | Gleiche Ladezeitpunkte und Refetch-Auslöser wie Original (A08 §2.3.4/§2.3.5 inkl. Rollen im Key) | I0 |
| **D08-ADR-09** | HTTP | `APIService`-Basisklasse auf `HttpClient` mit **Promise**-API und gleichen Methoden `get/post/put/patch/delete/request` (ADR-047); Interceptor-Kette §3.5.2; Fehler werden wie im Original als `error.response.data` weitergeworfen (`HttpErrorResponse.error`) | Observable-API in Services; generierter Client | Store-Code bleibt `async/await` | I0 |
| **D08-ADR-10** | Routen-Reihenfolge | Angular „first match“ wird durch eine **feste Deklarationsreihenfolge** an das Ranking von React Router angeglichen: (1) Redirect-Routen mit statischem Präfix, (2) statische Top-Level-Routen, (3) Pfade mit statischem Segment vor dynamischem auf gleicher Ebene, (4) `:workspaceSlug`-Baum, (5) `**`. Ein Routing-Contract-Test prüft jede URL der Tabellen §4.1–§4.3 | eigener `UrlMatcher` mit React-Ranking | Explizit, testbar, kein Eigenbau eines Rankings | I0 |
| **D08-ADR-11** | Trailing Slash | `TrailingSlashPathLocationStrategy` aus `@angular/common` (stabil, in 22.x enthalten) schreibt jede Browser-URL mit `/`; die erste Navigation ersetzt eine URL ohne Slash per `replaceState` (Äquivalent zum 308 der `clientMiddleware`). Für Vergleiche wie `pathname === \`${base}/settings/\`` liefert `PathnameService.pathname()` den **Browser**-Pfad mit Slash (`Location.path()` normalisiert ohne Slash). `AppRouter.push/replace` hängen `/` an und verzögern um `setTimeout(0)` (E22, Parität) | eigener `UrlSerializer`; Server-Redirect im Gateway | Framework-Bordmittel; Original verhält sich ebenfalls rein clientseitig | I0 |
| **D08-ADR-12** | Guards als In-Place-Zustände | Die Original-Wrapper werden als **Wrapper-Komponenten** mit Content-Projection portiert (`<pl-authentication-wrapper pageType="AUTHENTICATED"><router-outlet/></…>`), die Spinner, Fehler- und Leerzustände **ohne URL-Wechsel** rendern und Redirects per `AppRouter` auslösen. Funktionale Guards nur für (a) Redirect-Routen (`redirectTo`-Funktionen), (b) Legacy-Loader-Redirects (`canActivate` mit `UrlTree`), (c) Splat-Matcher | Redirect-Guards (`canActivate`) für die Auth-Matrix | Original zeigt erst Spinner und dann Redirect bzw. Zustandsseite in derselben URL; Guard-Variante würde die URL nicht stehen lassen | I0 |
| **D08-ADR-13** | Formulare | **Angular Signal Forms** (stabil seit v22) für alle `react-hook-form`-Formulare; Validierungstexte, `dirty`-Logik und `reset`-Zeitpunkte 1:1; Adapter `plFormControl` für Propel-Felder. Entry-Point/Direktivname (`@angular/forms/signals`) in S0 bestätigen ⚠ | Reactive Forms (Fallback, falls S0 rot); Template-driven | 01 Glossar verbindlich; Signals passen zum Store-Modell | I0 (Gerüst), I1 |
| **D08-ADR-14** | i18n | i18next + i18next-icu + i18next-resources-to-backend unverändert (ADR-046); Locales als statische Assets `/{base}/i18n/{lng}/{ns}.json`; `TranslationService` (Signal `currentLocale`), Pipe `t`, Funktion `t()`; Init per `provideAppInitializer` vor dem ersten Routing | Transloco, `@angular/localize` | Gleiche Fallback-Kette (`defaultNS` → `fallbackNS` → `fallbackLng`), ICU-Plurale | I0 |
| **D08-ADR-15** | Theme | Inline-Script in `index.html` (Logik von next-themes 0.4.6, s. §5.1) + `ThemeService` (Signals `theme`, `resolvedTheme`, `systemTheme`); Attribut `data-theme`, Schlüssel `localStorage.theme`, `color-scheme` nur bei `light`/`dark` | CSS-only `prefers-color-scheme`; Angular-Material-Theming | Kein Theme-Flash, gleiche Selektoren `[data-theme*="dark"]` | I0 |
| **D08-ADR-16** | Virtualisierung | Port von `RenderIfVisible` als Struktur-Direktive `*plRenderIfVisible` (IntersectionObserver, Offsets wie Original); `@tanstack/virtual-core` nur dort, wo das Original `@tanstack/react-virtual` nutzt (`PKG/blocks` `select`, `virtual-list`) | CDK Virtual Scroll | Variable Höhen, Sticky-Header, Swimlanes, DOM-Parität (A09 §5.2) | I2 |
| **D08-ADR-17** | Command-Palette | Eigene Komponente `pl-command` (Root/Input/List/Group/Item/Empty) mit **cmdk-DOM-Attributen** (`cmdk-root`, `cmdk-input`, `cmdk-list`, `cmdk-group`, `cmdk-group-heading`, `cmdk-item`, `data-selected`, `aria-selected`, `data-disabled`) und cmdk-Filterlogik (`command-score`-Port); `power-k.css` unverändert; Power-K-Kern (`registry.ts`, `shortcut-handler.ts`, `context-detector.ts`) als TS 1:1 | Angular CDK Listbox pur; Fremd-Lib | Parität von Markup, Sortierung und Tastatur | I5 |
| **D08-ADR-18** | Charts | D3-Module + Angular-SVG-Komponenten, die recharts-2.15.4-Markup nachbilden (bestätigt ADR-044) | ECharts | Pixelparität | I3 |
| **D08-ADR-19** | DnD | `@atlaskit/pragmatic-drag-and-drop` 1.7.4 unverändert; Direktiven `plDraggable`, `plDropTarget`, `plMonitor`, `plAutoScroll` registrieren in `afterNextRender`, Cleanup in `DestroyRef` (bestätigt ADR-043) | CDK DragDrop | Gleiches Hitbox-/Instruction-Modell | I1 (Labels), I2 |
| **D08-ADR-20** | Emoji-Picker | Port der Blocks-Komponente `emoji-icon-picker` (Original: `frimousse` 0.3) als Angular-Komponente mit **identischem DOM** auf Basis gebündelter `emojibase-data` (Version wie von frimousse 0.3 genutzt ⚠), Daten aus `/{base}/assets/emoji/` statt jsDelivr; `emoji-picker-react` entfällt (im Quelltext ungenutzt) | Fremd-Picker | Airgap (ADR-004), DOM-Parität | I2 |
| **D08-ADR-21** | Date-Picker | Eigene Komponente `pl-calendar` mit **Klassenvertrag** von Propel `calendar` (react-day-picker 10.0.1, `PROPEL/elements/calendar/variants.js`); Wochenstart Default Montag (Propel) bzw. Profil (`start_of_the_week`) wo das Original es übergibt; `date-fns` 4.1 | Angular-Material-Datepicker | DOM-Parität | I2 |
| **D08-ADR-22** | Realtime-Events (H6) | `LiveEventsService` (`@microsoft/signalr` 10.x) in `libs/web/core/live-events`, verbindet nach Login lazy mit `/live/events/`, verteilt Events an Multi-Provider `LIVE_EVENT_HANDLERS`; CE nutzt ihn ab I5 für den Notification-Zähler | Polling | 01 ADR-023 / §1.4 H6 | I0 (Gerüst), I5 |
| **D08-ADR-23** | Change Detection | Zoneless (Default v22), OnPush (Default v22); keine `zone.js`-Abhängigkeit. Drittbibliotheken mit DOM-Events (pragmatic-dnd, tippy, floating-ui) brauchen kein `runOutsideAngular`, Signalschreibungen lösen Rendering aus | Zone-basiert | Performance, v22-Defaults | I0 |
| **D08-ADR-24** | Seitentitel & Meta | `PlaneTitleStrategy` setzt `route.title` **wörtlich** (ohne Suffix); `PageHeadDirective`/`PageTitleService` für Laufzeit-Titel (Ersatz `PageHead`); Route-`data.robots` → `Meta`-Service (`noindex, nofollow` bzw. `index, nofollow`) | Titel-Suffix-Strategie | Titel exakt wie Layout-`meta` des Originals | I0 |
| **D08-ADR-25** | Lazy Loading | Jede Page- und Layout-Komponente per `loadComponent`; Domänen-Libs werden dadurch automatisch in Chunks geteilt; keine `loadChildren`-Routendateien je Domäne (Routen bleiben in `app.routes.ts`, 1:1-Review gegen `core.ts`) | Routendatei je Domäne | Routenbaum an einer Stelle prüfbar | I0 |
| **D08-ADR-26** | Space-SSR | Space wird **CSR** gebaut; Social-Meta für `/spaces/issues/:anchor` erzeugt das Gateway (01 ADR-033); im Client setzt ein Resolver nur `document.title`/`description` | Angular SSR (Node zur Laufzeit, verletzt ADR-002) | Kein Node | I6 |
| **D08-ADR-27** | Tests Frontend | Vitest (Angular-22-Builder) + `@testing-library/angular` für Unit/Komponenten; Playwright für E2E, Visual Regression (Referenz-Screenshots des Originals) und DOM-Snapshots; Original-Unit-Tests aus `PKG/blocks` (21) und `PKG/services` (`url.test.ts`) werden als Spezifikation portiert | Jest, Cypress | 01 ADR-048 | I0 |
| **D08-ADR-28** | Edge-Cases des Originals (A08 §3.10) | Funktionale Fehler werden korrigiert und in `tests/contracts/deviations.yaml` (Bereich `frontend`) dokumentiert; rein optische/textliche Eigenheiten bleiben (Entscheidungen je Fall §4.9) | alles 1:1 | 01 P1/§7.20 | I0…I6 |

---
## 3. Detaildesign

### 3.1 Workspace, Apps, Base-Paths, Libraries, Modulgrenzen

#### 3.1.1 Verzeichnisbaum (Präzisierung von 01 §6.1)

```text
frontend/
├── package.json  pnpm-workspace.yaml  angular.json  tsconfig.base.json  sheriff.config.ts
├── eslint.config.js  .prettierrc  vitest.workspace.ts  playwright.config.ts
├── apps/
│   ├── web/                               # base href "/"
│   │   ├── public/                        # ← WEB/public (favicon/*, icons/*, site.webmanifest.json, manifest.json); sw.js/workbox entfallen (E19)
│   │   └── src/
│   │       ├── index.html                 # Inline-Theme-Script (§5.1), Portale #context-menu-portal, #editor-portal
│   │       ├── main.ts                    # bootstrapApplication(AppComponent, appConfig)
│   │       ├── app.component.ts           # <router-outlet/> (entspricht root.tsx `Root`)
│   │       ├── app.config.ts              # Provider-Kette (§3.2)
│   │       ├── app.routes.ts              # Routenbaum (§4.1), Reihenfolge D08-ADR-10
│   │       ├── styles.css                 # @import tailwind-config, propel styles, globals.css, power-k.css, emoji.css, editor styles
│   │       ├── styles/                    # ← WEB/styles/{globals,power-k,emoji}.css (1:1)
│   │       └── pages/                     # ← WEB/app/** (gleiche Ordnernamen inkl. "(all)", "[workspaceSlug]")
│   │           ├── layout.component.ts    # L0 AppShellLayoutComponent
│   │           ├── not-found.page.ts
│   │           ├── (home)/{layout.component.ts,page.ts}
│   │           ├── (all)/…                # je Original-Ordner: layout.component.ts, page.ts, header.component.ts, mobile-header.component.ts
│   │           └── routes/redirects/      # Redirect-Funktionen (redirects.ts) – Ersatz für routes/redirects/core/*.tsx
│   ├── admin/                             # base href "/god-mode/", src/pages ← ADM/app/(all)/**
│   ├── space/                             # base href "/spaces/",  src/pages ← SPC/app/**
│   └── e2e/                               # Playwright: web/, admin/, space/, visual/, dom/, a11y/, routing/
├── libs/
│   ├── shared/                            # scope:shared (01 §6.1, unverändert)
│   │   ├── types/ constants/ utils/ i18n/ services/ shared-state/ cdk/ state-kit/ runtime-config/
│   │   ├── tailwind-config/ propel/ blocks/ editor/ dnd/
│   │   └── work-items-core/               # NEU (A09 §5.1): reine TS-Logik aus WEB/components/issues/issue-layouts/utils.tsx,
│   │                                      #   WEB/components/gantt-chart/sidebar/utils.ts, WEB/store/issue/helpers/base-issues-utils.ts
│   ├── web/                               # scope:web; je Domäne: state/ services/ components/ (+ public-api.ts je Unterordner)
│   │   ├── core/ extensions/ auth/ workspace/ project/ project-settings/ work-items/ views/ cycles/ modules/ intake/
│   │   ├── pages/ analytics/ home/ stickies/ notifications/ power-k/ profile/ settings/ favorites/ archives/ project-publish/
│   ├── admin/                             # scope:admin: core/ authentication/ instance/ workspace/ common/
│   └── space/                             # scope:space: core/ issues/ views/ editor/ account/
└── tools/
    ├── icons-codegen/  contract-check/  i18n-sync-check/  i18n-generate-types/
    └── golden-ui/                         # Erzeugung der Referenz-Screenshots/DOM-Snapshots aus dem Original (Node, nur Dev)
```

**Begriffsabgleich mit dem Auftrag:** „ui/propel-Port“ = `libs/shared/propel`; „blocks“ = `libs/shared/blocks`; „editor“ = `libs/shared/editor`; „i18n“ = `libs/shared/i18n`; „types“, „constants“, „utils“ = gleichnamige `libs/shared/*`; „api-client“ = `libs/shared/services` (Paket-Services) + `libs/web/<domäne>/services` (App-Services); „state“ = `libs/shared/state-kit` (Primitive, QueryCache) + `libs/web/<domäne>/state` (Stores); „Feature-Libs je Domäne“ = `libs/web/<domäne>/components`.

#### 3.1.2 Apps, Base-Paths, Builds

| App | `angular.json`-Projekt | Base-Href (`baseHref`) | Dev-Port (Aspire `PORT`) | Gateway-Pfad (01 ADR-033) | Output | Themes |
|---|---|---|---|---|---|---|
| web | `web` | `/` | 3000 | `/` (SPA-Fallback auf `index.html` außer `/api/`, `/auth/`, `/live/`, `/god-mode/`, `/spaces/`, Bucket) | `dist/web/browser` | light, dark, light-contrast, dark-contrast, custom, system |
| admin | `admin` | `/god-mode/` | 3001 | `/god-mode/` (301 `/god-mode` → `/god-mode/`) | `dist/admin/browser` | light, dark, system |
| space | `space` | `/spaces/` | 3002 | `/spaces/` (301 `/spaces` → `/spaces/`) | `dist/space/browser` | light, dark, system |

- Build-Optionen je App: `outputHashing: all`, `optimization: true`, `sourceMap: hidden` (Prod), `subresourceIntegrity: false` (Gateway setzt CSP), `inlineStyleLanguage: css`, PostCSS mit `@tailwindcss/postcss` 4.1.17. **Keine** Build-Zeit-Umgebungsvariablen (§3.11).
- Assets: `@fontsource*`-Dateien werden über `styles.css`-Imports gebündelt (gleiche Woff2-Dateien wie Original); `public/` 1:1; Emoji-Daten (`emojibase-data`) und Locale-JSON als statische Assets (`/{base}/assets/emoji/…`, `/{base}/i18n/{lng}/{ns}.json`).
- Dev: `ng serve web --port ${PORT}` hinter dem Gateway (same-origin, Cookie-Session). Proxy-Config wird **nicht** genutzt (Gateway übernimmt).
- Bundle-Budgets (`angular.json`, verbindlich ab I2, Fehler bei Überschreitung): web `initial` ≤ 650 kB (gzip ≤ 210 kB), jede Lazy-Chunk-Gruppe ≤ 400 kB; admin/space `initial` ≤ 450 kB. Werte werden in I0 gegen das Original-Bundle (`build/client`) gemessen und dann ± 10 % festgeschrieben (⚠ Messung S0).

#### 3.1.3 Library-Inventar mit Tags

| Lib (`FE/libs/…`) | Import-Alias (`tsconfig.base.json`) | Herkunft | Sheriff-Tags | ab |
|---|---|---|---|---|
| `shared/types` | `@plane/types` | `PKG/types` (Kopie; React-Typen `React.ReactNode` etc. → `unknown`/Angular-Typen, Liste A13b §2.3.4) | `scope:shared`, `type:types` | I0 |
| `shared/constants` | `@plane/constants` | `PKG/constants` (ohne `subscription.ts`, `payment.ts`, `MARKETING_*`) | `scope:shared`, `type:constants` | I0 |
| `shared/utils` | `@plane/utils` | `PKG/utils` (React-Hilfen nach `cdk`) | `scope:shared`, `type:utils` | I0 |
| `shared/i18n` | `@plane/i18n` | `PKG/i18n` (Locales 1:1, Core 1:1, Provider/Hook → Service/Pipe) | `scope:shared`, `type:data` | I0 |
| `shared/services` | `@plane/services` | `PKG/services` | `scope:shared`, `type:data` | I0 |
| `shared/shared-state` | `@plane/shared-state` | `PKG/shared-state` (rich-filters, work-item-filters) | `scope:shared`, `type:data` | I2 |
| `shared/state-kit` | `@plane/state-kit` | neu | `scope:shared`, `type:data` | I0 |
| `shared/runtime-config` | `@plane/runtime-config` | neu | `scope:shared`, `type:data` | I0 |
| `shared/cdk` | `@plane/cdk` | `PKG/hooks` + App-Hooks ohne Store-Bezug | `scope:shared`, `type:ui` | I0 |
| `shared/tailwind-config` | `@plane/tailwind-config` | `PKG/tailwind-config` (CSS 1:1) | `scope:shared`, `type:ui` | I0 |
| `shared/propel` | `@plane/propel/{components,elements,icons,…}/*` | `@makeplane/propel@0.7.3` | `scope:shared`, `type:ui` | I0…I3 |
| `shared/blocks` | `@plane/blocks/*` | `PKG/blocks` | `scope:shared`, `type:ui` | I0…I3 |
| `shared/editor` | `@plane/editor`, `@plane/editor/core` | `PKG/editor` | `scope:shared`, `type:ui` | I2/I4 |
| `shared/dnd` | `@plane/dnd` | neu (Direktiven um pragmatic-dnd) | `scope:shared`, `type:ui` | I1 |
| `shared/work-items-core` | `@plane/work-items-core` | neu (reine Funktionen, A09 §5.1) | `scope:shared`, `type:utils` | I2 |
| `web/core` | `@plane/web/core` | Wrapper, Layout-Basis, Router/Theme/Instance/User/Permission/CommandPalette-Stores, Interceptors, Modal-Hosts, Navigation, Sidebar, Breadcrumbs | `scope:web`, `domain:core` | I0 |
| `web/extensions` | `@plane/web/extensions` | Registry-Tokens (§6) | `scope:web`, `domain:extensions` | I0 |
| `web/<domäne>` (19 Domänen, Tabelle 01 §6.1) | `@plane/web/<domäne>`, `…/state`, `…/services` | `WEB/components/*`, `WEB/store/*`, `WEB/services/*` | `scope:web`, `domain:<d>`, `layer:ui\|state\|services` | I0…I6 |
| `admin/*`, `space/*` | `@plane/admin/*`, `@plane/space/*` | `ADM/*`, `SPC/*` | `scope:admin`/`scope:space` | I0/I6 |

#### 3.1.4 Ablage-Regel je Original-Datei

| Original | Ziel | Regel |
|---|---|---|
| `WEB/app/**/page.tsx` | `FE/apps/web/src/pages/**/page.ts` | Klasse `<Zweck>PageComponent`, Selektor `pl-page-<zweck>`; Page enthält nur Komposition + Titel |
| `WEB/app/**/layout.tsx` | `FE/apps/web/src/pages/**/layout.component.ts` | Klasse `<Zweck>LayoutComponent`; enthält `<router-outlet/>` an der Stelle von `<Outlet/>` |
| `WEB/app/**/header.tsx`, `mobile-header.tsx` | gleicher Ordner, `header.component.ts`, `mobile-header.component.ts` | – |
| `WEB/components/<x>/<datei>.tsx` | `FE/libs/web/<domäne>/components/<x>/<datei>.component.{ts,html}` | gleicher Dateistamm, kebab-case; Domänenzuordnung Tabelle 01 §6.1 |
| `WEB/store/<pfad>.ts` | `FE/libs/web/<domäne>/state/<pfad>.ts` | Dateiname, Klasse, Felder, Methoden gleich (Tabelle §4.5) |
| `WEB/services/<pfad>.ts` | `FE/libs/web/<domäne>/services/<pfad>.ts` | Methoden/Pfade gleich |
| `WEB/hooks/store/use-*.ts` | entfällt → `inject(<Store>)` | Tabelle §4.7 |
| `WEB/hooks/*.tsx` (Fach-/UI-Hooks) | Service, Direktive oder Signal-Funktion `inject<Name>()` | Tabelle §4.7 |
| `WEB/helpers/*`, `WEB/lib/*` | `FE/libs/web/core/{helpers,lib}/*` | 1:1 |
| `WEB/layouts/auth-layout/*` | `FE/libs/web/core/wrappers/*` | Wrapper-Komponenten (§3.3.4) |
| `WEB/app/compat/next/*` | entfällt → `AppRouter`, `PathnameService`, `pl-link`-Direktive (`[plLink]`) | §3.3.2 |

#### 3.1.5 Sheriff-Regeln (`sheriff.config.ts`)

Ergänzt 01 §6.3 um die Ebenen aus D08-ADR-02 und die Domänen-Matrix.

| Von (Tag) | darf importieren |
|---|---|
| `type:types` | – |
| `type:constants` | `type:types` |
| `type:utils` | `type:types`, `type:constants` |
| `type:data` (shared) | `type:types`, `type:constants`, `type:utils`, `type:data` |
| `type:ui` (shared) | `type:types`, `type:constants`, `type:utils`, `type:data` (nur `i18n`, `state-kit`, `runtime-config`), `type:ui` in Richtung `cdk ← propel ← blocks ← editor`, `dnd` |
| `layer:services` (web) | `scope:shared` (ohne `type:ui`), `layer:services` jeder Domäne |
| `layer:state` (web) | `scope:shared` (ohne `type:ui`), `layer:services` jeder Domäne, `layer:state` jeder Domäne, `domain:extensions` |
| `domain:core`, `layer:ui` | `scope:shared`, `domain:extensions`, alle `layer:state`/`layer:services` |
| `domain:<d>`, `layer:ui` | `scope:shared`, `domain:core`, `domain:extensions`, alle `layer:state`/`layer:services`, **`layer:ui` nur der in der Matrix genannten Domänen** |
| `type:app` | eigene Scope-Libs, `scope:shared` |

**Domänen-Matrix `layer:ui`** (Zeile darf Spalte importieren; zusätzlich immer `core`, `extensions`):

| Domäne | workspace | auth | project | project-settings | work-items | cycles | modules | views | intake | pages | stickies |
|---|---|---|---|---|---|---|---|---|---|---|---|
| workspace | – | | | | | | | | | | |
| auth | ✓ | – | | | | | | | | | |
| project | ✓ | | – | | | | | | | | |
| project-settings | ✓ | | ✓ | – | | | | | | | |
| work-items | ✓ | | ✓ | | – | | | | | | |
| cycles, modules, views, intake | ✓ | | ✓ | | ✓ | – | – | – | – | | |
| archives | ✓ | | ✓ | | ✓ | ✓ | ✓ | | | | |
| pages | ✓ | | ✓ | | ✓ | | | | | – | |
| analytics | ✓ | | ✓ | | ✓ | ✓ | ✓ | | | | |
| stickies | ✓ | | | | | | | | | | – |
| home | ✓ | | ✓ | | ✓ | | | | | ✓ | ✓ |
| notifications, profile | ✓ | | ✓ | | ✓ | | | | | | |
| settings, project-publish | ✓ | | ✓ | | | | | | | | |
| favorites | ✓ | | ✓ | | | ✓ | ✓ | ✓ | | ✓ | |
| power-k | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |

Alle Dropdowns aus `WEB/components/dropdowns/*` (inkl. Cycle-/Module-Dropdown) liegen in `work-items` und lesen Cycle/Module-Daten über `layer:state` – damit braucht `work-items` keine UI-Abhängigkeit zu `cycles`/`modules`.

### 3.2 Bootstrap & Provider-Kette

Original (A08 §2.4): `entry.client.tsx` (Polyfills, Stale-Asset-Listener, `await initPromise`) → `root.tsx` (`Layout`, `ThemeProvider`, `HydrateFallback`, `ErrorBoundary`) → `layout.tsx` (Trailing-Slash-Middleware, `AppProvider`) → `provider.tsx` (`StoreProvider` → `AppProgressBar` → `TranslationProvider` → `PlaneToastProvider` → `StoreWrapper` → `InstanceWrapper` → `SWRConfig`).

| Reihenfolge | Ziel (web) | Datei | Ersetzt |
|---|---|---|---|
| 0 | Inline-Script setzt `data-theme`/`color-scheme` vor dem ersten Paint; statischer Spinner-Platzhalter im `<body>` (wie `HydrateFallback`, erst nach aufgelöstem Theme sichtbar) | `apps/web/src/index.html` | next-themes-Script, `HydrateFallback` |
| 1 | `provideAppInitializer(loadRuntimeConfig)` – lädt `runtime-config.json` (§3.11), bricht bei Fehler **nicht** ab (Defaults = same-origin) | `libs/shared/runtime-config` | `VITE_*` |
| 2 | `provideAppInitializer(() => inject(TranslationService).init())` – entspricht `await initPromise`; Fehler → `catch(() => {})` | `libs/shared/i18n` | `initPromise` |
| 3 | `provideRouter(routes, withComponentInputBinding(), withRouterConfig({ paramsInheritanceStrategy: 'always', onSameUrlNavigation: 'ignore' }), withInMemoryScrolling({ scrollPositionRestoration: 'disabled' }), withNavigationErrorHandler(staleChunkHandler))` + `{ provide: LocationStrategy, useClass: TrailingSlashPathLocationStrategy }` + `{ provide: TitleStrategy, useClass: PlaneTitleStrategy }` | `apps/web/src/app.config.ts` | `routes.ts`, `clientMiddleware` |
| 4 | `provideHttpClient(withFetch(), withInterceptors([trailingSlashInterceptor, credentialsInterceptor, csrfInterceptor, unauthorizedInterceptor]))` | `libs/web/core/http` | Axios-Instanzen |
| 5 | `provideZonelessChangeDetection()` (Default v22, explizit zur Dokumentation), `provideBrowserGlobalErrorListeners()` | – | – |
| 6 | `{ provide: ErrorHandler, useClass: PlaneErrorHandler }` (Stale-Chunk-Recovery + Fehlerseite) | `libs/web/core/errors` | `ErrorBoundary`, `entry.client`-Listener |
| 7 | `provideAppInitializer(() => inject(ProgressBarService).attach())` (Router-Events → `@bprogress/core`, `minimum 0.1, speed 400, trickleSpeed 800, showSpinner false`) | `libs/web/core/lib/b-progress` | `AppProgressBar` |
| 8 | Toast-Viewport `<pl-toast-viewport>` im `AppShellLayoutComponent` (innerhalb der i18n-Bereitschaft) | `libs/shared/blocks/toast` | `PlaneToastProvider` |
| 9 | `AppShellLayoutComponent` (L0) rendert `<pl-store-wrapper><pl-instance-wrapper><router-outlet/></…></…>` | `apps/web/src/pages/layout.component.ts` | `AppProvider`, `StoreWrapper`, `InstanceWrapper` |
| 10 | `QueryCache`-Defaults `WEB_SWR_CONFIG` (`refreshWhenHidden:false, revalidateIfStale:true, revalidateOnFocus:true, revalidateOnMount:true, errorRetryCount:3`) per `provideQueryCacheConfig(WEB_SWR_CONFIG)` | `libs/shared/state-kit` | `SWRConfig` |

Admin: gleiche Kette mit `ADMIN_SWR_CONFIG` (`refreshWhenHidden:false, revalidateIfStale:false, revalidateOnFocus:false, revalidateOnMount:true, refreshInterval:600000, errorRetryCount:3`, A11 §2.14), Themes nur `light|dark|system`, Wrapper `InstanceProvider`/`UserProvider` als Komponenten. Space: gleiche Kette inklusive Progressbar (`@bprogress/core` ist in `SPC/package.json`), ohne `unauthorizedInterceptor`, Themes `light|dark|system`.

**Polyfills:** `requestIdleCallback`-Fallback (`WEB/lib/idle-task.ts`, `runIdleTask` Timeout 300 ms) als `libs/web/core/lib/idle-task.ts`, wird in `main.ts` vor `bootstrapApplication` importiert.

### 3.3 Routing

#### 3.3.1 Grundregeln

1. **Struktur 1:1:** React-`layout(file, children)` ⇒ Angular `{ path: '', component: <Layout>, children }` (pfadlose Layout-Route). React-`route(path, file)` ⇒ `{ path: <relativer Pfad>, loadComponent }`. Pfade, die im Original absolut unter einer Layout-Gruppe stehen (`:workspaceSlug/…`), werden in Angular unter **eine** Route `:workspaceSlug` gruppiert, deren Kinder relative Pfade tragen; die Layout-Kette bleibt identisch (Tabelle §4.4).
2. **Reihenfolge** nach D08-ADR-10. Pflicht-Reihenfolgen (aus A08 §5.2, ergänzt):
   - Alle statischen Top-Level-Pfade (`sign-up`, `accounts/*`, `create-workspace`, `onboarding`, `invitations`, `workspace-invitations`, `settings/profile/:profileTabId`, `sign-in`, `signin`, `login`, `register`, `profile/**`, `accounts/sign-up`) **vor** `:workspaceSlug`.
   - `:workspaceSlug/projects/:projectId/settings/**`, `:workspaceSlug/projects/:projectId/inbox`, `:workspaceSlug/analytics`, `:workspaceSlug/settings/api-tokens`, `:workspaceSlug/settings/account/**`, `:workspaceSlug/settings/billing` (neu, Redirect) **vor** dem `:workspaceSlug`-Baum.
   - Im Profil `activity` vor `:profileViewId`; `projects/archives` vor `projects/:projectId/…`; Projekt-Archive (`projects/:projectId/archives/…`) vor `projects/:projectId` (LPD); `settings/projects` vor `settings` (LWSET).
3. **`pathMatch: 'full'`** für alle leeren Index-Routen (`''` mit Page) und für Redirects ohne Splat.
4. **Parameter:** `paramsInheritanceStrategy: 'always'`, damit jede Page `workspaceSlug`, `projectId` … per `input()` erhält (`withComponentInputBinding`); der `RouterStore` liest die zusammengeführten Parameter (§3.3.3).
5. **Lazy Loading:** jede Page/Layout per `loadComponent` (D08-ADR-25).
6. **Keine Platzhalter-Routen:** Routen eines noch nicht gebauten Inkrements sind nicht registriert (01 §7.19). Die Spalte „Ink.“ in §4.1 legt fest, wann eine Route in `app.routes.ts` aufgenommen wird; bis dahin greift die 404-Seite.
7. **Query-Parameter** bleiben bei Redirects erhalten, wo das Original sie überträgt (`profile/*`, `settings/account/*`: immer `?` + Query, E15 beibehalten; Legacy-Issue: keine Query).

#### 3.3.2 Navigation, Links, Pfad

| Original | Ziel | Verhalten |
|---|---|---|
| `useRouter()` aus `next/navigation`-Shim (`push/replace/back/forward/refresh/prefetch`) | `AppRouter` (`libs/web/core/lib/app-router.ts`) | `push(url)`/`replace(url)` → `ensureTrailingSlash(url)` → `setTimeout(() => router.navigateByUrl(url, {replaceUrl}), 0)` (E22 Parität); `back()`/`forward()` → `history`; `refresh()` → `location.reload()`; `prefetch()` no-op |
| `next/link`-Shim `Link` (Trailing Slash, ignoriert `prefetch/scroll/shallow`) | Direktive `a[plLink]` | setzt `href` mit Slash, interne Navigation per `AppRouter.push` ohne Verzögerung bei Klick (wie Link-Komponente: sofortige Navigation), `target`/Modifier-Klicks → Browser-Standard |
| `usePathname()` | `PathnameService.pathname` (Signal, liest `window.location.pathname` nach `NavigationEnd`) | enthält Trailing Slash wie Browser-URL |
| `useSearchParams()` | `PathnameService.searchParams` (Signal `URLSearchParams`) | nur lesen |
| `useParams()` | Komponenten-`input()`s bzw. `RouterStore` | – |
| `ensureTrailingSlash` (`WEB/app/compat/next/helper.ts`) | `libs/web/core/lib/url.ts` (Kopie) | gleiche Regeln (Query/Hash erhalten, `/` unverändert) |
| Space: direkte `react-router`-`Link` **ohne** Slash-Logik | `a[plLink]` mit `[trailingSlash]="false"` | Parität (A11 §2.15) |
| `next/image`, `next/script` | `<img>` (bzw. `NgOptimizedImage` **nicht**, DOM-Parität), Script-Injektion entfällt | – |

#### 3.3.3 RouterStore

`WEB/store/router.store.ts` → `libs/web/core/state/router.store.ts` (`RouterStore`). `query` ist ein Signal mit den **zusammengeführten Pfad- und Query-Parametern**; gesetzt von `StoreWrapperComponent` bei jedem `NavigationEnd` (Original: `router.setQuery(params)` in `StoreWrapper`). Computeds gleichnamig: `workspaceSlug, teamspaceId, projectId, cycleId, moduleId, viewId, globalViewId, profileViewId, userId, peekId, issueId, inboxId, webhookId, epicId` (alle Signale). `teamspaceId`/`epicId` bleiben (B1/Epics-Andockstelle, in CE immer `undefined`).

#### 3.3.4 Wrapper & In-Place-Guard-States

| Wrapper (Original) | Ziel-Komponente (`FE/libs/web/core/wrappers/…`) | Ladeauslöser (QueryCache-Key → Action) | In-Place-Zustände (URL bleibt) | Redirects (über `AppRouter`) |
|---|---|---|---|---|
| `AuthenticationWrapper(pageType)` (`WEB/lib/wrappers/authentication-wrapper.tsx`) | `AuthenticationWrapperComponent` `pl-authentication-wrapper` (`input pageType: EPageTypes`) | `USER_INFORMATION` → `user.fetchCurrentUser()` (`revalidateOnFocus:false, shouldRetryOnError:false`) | Vollbild-`LogoSpinner` solange User/Workspaces laden | Matrix A08 §2.3.1: `NON_AUTHENTICATED` + eingeloggt → `/onboarding` bzw. `getWorkspaceRedirectionUrl()`; `ONBOARDING`/`AUTHENTICATED` nicht eingeloggt → `/?next_path=<pathname>`; `AUTHENTICATED` nicht onboarded → `/onboarding`; `ONBOARDING` onboarded → `replace(redirect)`; `SET_PASSWORD` entfällt (ADR-008) |
| `InstanceWrapper` | `InstanceWrapperComponent` | `INSTANCE_INFORMATION` → `instance.fetchInstanceInfo()` | Spinner; Fehler → `MaintenanceView`; `is_setup_done === false` → `InstanceNotReady` (Button „Get started“ → `GOD_MODE_URL`) | – |
| `StoreWrapper` | `StoreWrapperComponent` | – | – | – (setzt `RouterStore.query`, Sidebar-Collapse aus `localStorage.app_sidebar_collapsed` falls `theme.sidebarCollapsed === undefined`, Theme-Sync einmal je User-Sitzung, Custom-Theme anwenden/entfernen) |
| `WorkspaceAuthWrapper` (`WEB/layouts/auth-layout/workspace-wrapper.tsx`) | `WorkspaceAuthWrapperComponent` | 8 Keys aus A08 §2.3.4 (`WORKSPACE_MEMBER_ME_INFORMATION_{WS}`, `WORKSPACE_PROJECTS_ROLES_INFORMATION_{WS}`, `WORKSPACE_PARTIAL_PROJECTS_{WS}`, `WORKSPACE_MEMBERS_{WS}`, `WORKSPACE_FAVORITE_{WS}` (nur Admin/Member), `WORKSPACE_STATES_{WS}`, `WORKSPACE_SIDEBAR_PREFERENCES_{WS}`, `WORKSPACE_PROJECT_NAVIGATION_PREFERENCES_{WS}`), alle `revalidateIfStale:false, revalidateOnFocus:false` | (a) Spinner; (b) „Workspace not found“; (c) „Not Authorized!“; (d) Kinder | – |
| `ProjectAuthWrapper` (`WEB/layouts/auth-layout/project-wrapper.tsx`) | `ProjectAuthWrapperComponent` | 11 Keys aus A08 §2.3.5 inkl. `{role}`-Suffix (Rollenwechsel ⇒ neuer Key ⇒ Refetch); `useTimeLineChart(MODULE).initGantt()` beim Erzeugen | `null` während Projekt-Load (E26 beibehalten); keine Projektrolle → `ProjectAccessRestriction` (409 bzw. 403+WS-Admin → „Join project“; 403 → „restricted“; sonst „invalid project“) | – |
| Settings-Rechteprüfung `LWSET` (`WORKSPACE_SETTINGS_ACCESS[pathnameToAccessKey(pathname)]`) | `WorkspaceSettingsLayoutComponent` | – | `NotAuthorizedView` | – |
| `LPSET` (ohne `projectId` → erstes joined Projekt) | `ProjectSettingsRootLayoutComponent` | – | – | `/${ws}/settings/projects/${joinedProjectIds[0]}/` falls vorhanden |
| Disabled-Feature-Zustände (Seiten 27, 29, 31, 33, 34) | jeweilige Page | – | `DetailedEmptyState` (Bild `disabled-feature/*`) | Button → `/${ws}/settings/projects/${pid}/features/<feature>/` (**E1 korrigiert**) |
| Admin Dashboard-Guard (`ADM/app/(all)/(dashboard)/layout.tsx`) | `DashboardLayoutComponent` (admin) | `CURRENT_USER` → `user.fetchCurrentUser()` (jetzt `GET /api/instances/admins/me/` auf Basis der Keycloak-Session) | Spinner bei `isUserLoggedIn === undefined` | `false` → `replace('/')` (Admin-Home zeigt „Mit Keycloak anmelden“ bzw. „keine Admin-Rolle“) |
| Space-Startseite (`SPC/app/page.tsx`) | `SpaceHomePageComponent` | `fetchCurrentUser` | Spinner, `UserLoggedIn`, Login-Einstieg | eingeloggt + gültiger `next_path` → `replace(next_path)` |

**Umsetzungsmuster:** Die Wrapper-Komponente hält ein `state`-`computed` (`'loading' | 'not-found' | 'not-authorized' | 'content' …`) und rendert per `@switch`; Redirects werden in einem `effect()` ausgelöst, der erst nach abgeschlossenem Laden feuert (gleicher Zeitpunkt wie Original-`useEffect`). Kinder (`<ng-content/>` bzw. `<router-outlet/>`) werden nur im Zustand `content` gerendert – dadurch werden Kind-Pages erst nach erfolgreichem Bootstrap instanziiert (wie React).

#### 3.3.5 Redirect-Routen

Alle Redirects aus A08 §2.2.8 werden als `redirectTo`-**Funktionen** (`RedirectFunction`, Zugriff auf `params`, `queryParams`) in `FE/apps/web/src/pages/routes/redirects/redirects.ts` implementiert. Splat-Pfade (`*` im Original) nutzen `splatMatcher(prefix)` (§5.4), das die Restsegmente als `posParams.splat` liefert. Ziel-URLs immer **mit** abschließendem `/` exakt wie Original. Die Legacy-Detail-URL `/:ws/projects/:pid/issues/:issueId` ist kein reiner Redirect (Daten-Abruf) → `legacyIssueRedirectGuard` (`canActivate`, ruft `GET …/issues/{id}/meta/`, liefert `UrlTree` auf `/${ws}/browse/${identifier}-${sequence_id}/`; Fehler → `true`, Page zeigt EmptyState). Gleiches Muster für Space `/:workspaceSlug/:projectId` (`spaceLegacyAnchorGuard`, Fehler → `UrlTree('/404')`).

**ADR-008-Folgen für Auth-Routen (CE-AUTH-002…-021 entfallen):** `/sign-up`, `/accounts/forgot-password`, `/accounts/reset-password`, `/accounts/set-password` werden **Redirects auf `/`** (Legacy-Links aus E-Mails/Bookmarks bleiben benutzbar, CE-UIX-012); `/accounts/sign-up` und `/register` zeigen ebenfalls direkt auf `/` (Original: `/sign-up/`). Die Seite `/` ist der Einstieg „Mit Keycloak anmelden“ (CE-AUTH-001 angepasst): Button → Vollnavigation `${api_base_url}/auth/oidc/login/?app=web&next_path=<next_path>`; Fehlercodes aus Query `error_code` werden weiterhin als Banner gezeigt (CE-AUTH-014 angepasst). Ob `/` automatisch weiterleitet (Instanz-Option), entscheidet `05-auth-sicherheit-berechtigungen.md` – das Frontend unterstützt beide Varianten über `instance.config` (Feld wird in 05 benannt).

#### 3.3.6 Titel, Meta, Scroll

- `title` je Layout-Route exakt wie Original-Layout-`meta` (z. B. `"Sign up - Plane"`, `"Create Workspace"`, `"Onboarding"`, `"Invitations"`, `"Workspace Invitations"`); Default-Titel `APP_TITLE = "Plane | Simple, extensible, open-source project management tool."` in `index.html`. Laufzeit-Titel (`${ws} - Home`, `${project} - Work items`, …) setzt die Page über `PageTitleService.set()` – Ersatz für `PageHead`.
- `data: { robots }` für `LALL` (`noindex, nofollow`) und `LH` (`index, nofollow`); OG-/Twitter-Meta des Original-`root.tsx` stehen statisch in `index.html` (`og:url` → konfigurierbar über Gateway-Templating, Default entfernt wegen ADR-004).
- Scroll-Wiederherstellung **aus** (Original: React Router SPA ohne `ScrollRestoration`); Scroll-Container sind innere `ContentWrapper`.

### 3.4 State-Management

#### 3.4.1 Konventionen

1. **Ein Store = eine Datei = eine Klasse**, Name und Pfad wie Original (§4.5). Interface-Typen (`ICycleStore`) bleiben erhalten und werden von der Klasse implementiert; Felder, die im Original `observable` sind, werden zu **readonly Signal-Feldern** gleichen Namens.
2. **Lesen** in Templates und `computed`: `store.cycleMap.get(id)()` bzw. Getter-Methoden; **Schreiben** ausschließlich in Store-Methoden (Lint-Regel: kein `.set(` auf Store-Signalen außerhalb der Store-Klasse → `@plane/eslint-rules/no-external-store-mutation`).
3. **Computeds** (`computed` im Original) → `readonly x = computed(() => …)`; Aufrufstellen `store.x` werden zu `store.x()`.
4. **`computedFn`** (mobx-utils, parametrisierte Computeds) → `readonly getX = memoizedComputed((a, b) => …)`: Aufruf `store.getX(a, b)` liefert den **Wert** (wie Original), intern je Argument-Schlüssel ein gecachtes `computed` (LRU 1 000 Einträge je Funktion).
5. **Actions** → `async`-Methoden gleichen Namens und gleicher Signatur; `runInAction` entfällt.
6. **Persistenz** (`localStorage`) nur über `persisted(key, initial, {raw?})` mit identischem Schlüssel und Format (§3.15).
7. **Reset:** jede Store-Klasse mit `reset()` im Original behält `reset()`.
8. **Fehler:** Stores werfen wie Original weiter (`throw error`), Komponenten zeigen Toasts.

#### 3.4.2 Übersetzungstabelle MobX → Signals (verbindlich, mechanisch)

| MobX / mobx-utils / mobx-react | Ziel (`@plane/state-kit` bzw. Angular) | Hinweis |
|---|---|---|
| `observable.ref` / primitives `observable` | `signal<T>(init)` | Gleichheit `Object.is` |
| `observable` auf Record normalisierter Entitäten (`cycleMap: Record<string, ICycle>`) | `entityMap<T>()` → `EntityMap<T>` (`get(id)` → `Signal<T \| undefined>`, `has`, `set`, `patch(id, partial)`, `delete`, `upsertMany(list, idFn)`, `keys()`, `values()`, `entries()`, `clear()`) | ein Signal je Schlüssel + Schlüsselmengen-Signal |
| `observable` auf tief verschachtelten Strukturen (`groupedIssueIds`, `issuePaginationData`, `loader{groupKey}`, `filters{ws→…}`, `workspaceUserInfo`, `kanBanToggle`, `calendarPayload`) | `deepState<T>(init)` → `DeepState<T>` (`get(path?)`, `select(path)`, `set(path, v)`, `update(path, fn)`, `unset(path)`, `replace(v)`) | D08-ADR-05 |
| `observable.shallow` (Arrays/Maps) | `signal<T[]>` mit neuer Referenz bei Änderung | – |
| `Map` observable (`workItemFilters.filters: Map`) | `signal(new Map())` + Kopie bei Änderung oder `EntityMap` | – |
| `computed` | `computed` | – |
| `computedFn(fn)` | `memoizedComputed(fn, {maxEntries?})` | – |
| `action`, `action.bound`, `runInAction` | normale Methode | Batching übernimmt Signal-Graph |
| `reaction(expr, effect, {delay, fireImmediately, equals})` | `reactionEffect(expr, effect, {delay, fireImmediately, equals, injector})` | gleiche Semantik (nur bei Wertänderung, Debounce `delay`) |
| `autorun(fn)` | `effect(fn, {injector})` | Unter-Stores ohne Injection-Context: `injector` des Eltern-Stores übergeben |
| `when(pred)` | `untilSignal(pred): Promise<void>` | – |
| `toJS(x)` | `cloneDeep(x)` (lodash) | – |
| `set(obj, key, v)` (mobx) / `lodash.set` auf observable | `entityMap.set` / `deepState.set` | – |
| `makeObservable(this, {...})` | entfällt (Felder sind Signale) | Liste dient als Checkliste beim Review |
| `enableStaticRendering` | entfällt | – |
| `observer(Component)` | Standalone-Komponente, OnPush, Signale im Template | – |
| `StoreContext` + `useXxx()` | `inject(XxxStore)` | Tabelle §4.7 |

#### 3.4.3 Store-Graph und Root

```mermaid
flowchart LR
  subgraph core["libs/web/core/state"]
    RS[RootStore<br/>resetOnSignOut, Fassade] --- RT[RouterStore] & TH[ThemeStore] & IN[InstanceStore] & US[UserStore → UserProfileStore, UserSettingsStore, UserPermissionStore] & CP[CommandPaletteStore] & PK[PowerKStore] & MS[MultipleSelectStore] & EA[EditorAssetStore] & MR[MemberRootStore]
  end
  subgraph dom["libs/web/<domäne>/state"]
    WS[WorkspaceRootStore → WebhookStore, ApiTokenStore, HomeStore → WorkspaceLinkStore]
    PR[ProjectRootStore → ProjectStore, ProjectFilterStore, ProjectPublishStore]
    WM[WorkspaceMemberStore → WorkspaceMemberFiltersStore]
    PM[ProjectMemberStore → ProjectMemberFiltersStore]
    CY[CycleStore] --- CF[CycleFilterStore]
    MO[ModuleStore] --- MF[ModuleFilterStore]
    ST[StateStore] & LB[LabelStore] & ES[ProjectEstimateStore] & PV[ProjectViewStore] & GV[GlobalViewStore] & FV[FavoriteStore] & SK[StickyStore] & PP[ProjectPageStore] & IB[ProjectInboxStore] & NT[WorkspaceNotificationStore] & AN[AnalyticsStore] & TL[TimeLineStore]
    IR[IssueRootStore → IssueStore, 9 Listen-Stores + Filter, IssueDetail, KanBanView, CalendarView]
  end
  MR --> WM & PM
  IR -.inject.-> ST & LB & PR & MO & CY & MR
  WF[WorkItemFilterStore<br/>libs/shared/shared-state]
  IR -.-> WF
```

Die Original-`RootStore`-Felder (`rootStore.cycle`, `rootStore.issue.issues` …) existieren als Getter in der Fassade `RootStore` (D08-ADR-06), damit Funktionen, die im Original den Root übergeben bekommen (z. B. `new ProjectPage(store, page)`), unverändert portierbar bleiben. Neue Codezeilen nutzen direkt `inject()`.

#### 3.4.4 `MemberRootStore` und Unter-Stores

`WEB/store/member/index.ts` (`MemberRootStore` mit `memberMap`, `getMemberIds`, `getUserDetails`, Kinder `workspace`, `project`) liegt in `libs/web/core/state/member/member-root.store.ts` (Store-Cluster, D08-ADR-02). Die Kinder `workspace` (`WorkspaceMemberStore`) und `project` (`ProjectMemberStore`) liegen in `libs/web/workspace/state/member/…` bzw. `libs/web/project/state/member/…` und werden per `injectLazy` als Getter `workspace`/`project` angeboten (Zugriffspfad `memberRoot.workspace.xxx` bleibt).

#### 3.4.5 Unter-Instanzen

| Original-Unterinstanz | Erzeugt durch | Ziel |
|---|---|---|
| `ProjectPage` (`pages/project-page.ts` extends `BasePage`, `ExtendedBasePage`), `PageEditorInstance` | `ProjectPageStore` (`new ProjectPage(store, page)`) | plain class mit Signal-Feldern; `reaction` (Titel 2 s Debounce) → `reactionEffect` mit `injector` des Stores; `cleanup()` zerstört Effekt (`EffectRef.destroy`) |
| `InboxIssueStore` (`inbox/inbox-issue.store.ts`) | `ProjectInboxStore` | plain class |
| `Estimate`, `EstimatePoint` | `ProjectEstimateStore` | plain class |
| `Notification` (`notifications/notification.ts`) | `WorkspaceNotificationStore` | plain class |
| Issue-Listen-Stores (`project/issue.store.ts` …) + Filter-Stores, `IssueStore`, `IssueDetail` (2 Instanzen: `issueDetail`, `epicDetail`), `IssueKanBanViewStore`, `CalendarStore` | `IssueRootStore` (Konstruktor) | plain classes |
| `IssuesTimeLineStore`, `ModulesTimeLineStore`, (`projectTimeLineStore`, `groupedTimeLineStore`) | `TimeLineStore` | plain classes; `autorun`-Synchronisation → `effect` mit `injector` |
| `FilterInstance` (`PKG/shared-state/src/store/rich-filters/filter.ts`), `FilterConfigManager` | `WorkItemFilterStore` | plain classes |
| `PublishStore` (space) | `PublishListStore` | plain class |

#### 3.4.6 Issue-Store (Gruppierung, Pagination, Optimistic Updates)

Ziel: **1:1-Port** von `WEB/store/issue/**` (59 Dateien). Aufteilung:

| Teil | Original | Ziel | Portierung |
|---|---|---|---|
| Reine Funktionen | `issue/helpers/base-issues-utils.ts` (`getGroupKey`, `getGroupIssueKeyActions`, `getSubGroupIssueKeyActions`, `getDifference`, `getSortOrderToFilterEmptyValues`, `getIssueIds`, `checkIssueDateFilter`, `getPreviousIssuesState`, `getFilteredWorkItems`, `getOrderedWorkItems`, `getGroupedWorkItemIds`, `updateSubWorkItemFilters`) | `libs/shared/work-items-core/src/base-issues-utils.ts` | **Kopie ohne Änderung** (nur Importpfade); bestehende Semantik ist Spezifikation |
| Konstanten | `ISSUE_GROUP_BY_KEY`, `ISSUE_FILTER_DEFAULT_DATA`, `EIssueGroupedAction` (in `base-issues.store.ts`) | `libs/shared/work-items-core/src/base-issues.constants.ts` | Kopie |
| Layout-Logik | `WEB/components/issues/issue-layouts/utils.tsx` (reine Teile, A09 §5.1), `WEB/components/gantt-chart/sidebar/utils.ts` | `libs/shared/work-items-core/src/layout-utils.ts`, `gantt-utils.ts` | Kopie; React-Rückgaben (Icons als JSX) → Icon-Schlüssel |
| Abstrakter Listen-Store | `issue/helpers/base-issues.store.ts` (`BaseIssuesStore`) | `libs/web/work-items/state/issue/helpers/base-issues.store.ts` | Klasse 1:1: Felder `loader`, `groupedIssueIds`, `groupedIssueCount`, `issuePaginationData`, `paginationOptions` als `DeepState`/`signal`; Methoden `issueUpdate`, `createIssue`, `removeIssue`, `issueArchive`, `issueQuickAdd`, `removeBulkIssues`, `bulkArchiveIssues`, `bulkUpdateProperties`, `updateIssueDates`, `add/removeIssueToCycle`, `addCycleToIssue`, `removeCycleFromIssue`, `add/removeIssuesToModule`, `addModulesToIssue`, `changeModulesInIssue`, `addIssue`, `clear`, `addIssueToList`, `removeIssueFromList`, `updateIssueList`, `processIssueResponse`, `updateGroupedIssueIds`, `updateIssueGroup`, `accumulateIssueUpdates`, `updateUpdateAccumulator`, `updateIssueCount`, `getUpdateDetails`, `getOrderByUpdateDetails`, `getArrayStringArray`, `populateIssueDataForSorting`, `issuesSortWithOrderBy`, `storePreviousPaginationValues`, `getNextCursor`, `onfetchIssues`, `onfetchNexIssues` (Tippfehler im Namen bleibt) **wörtlich**, lodash-Aufrufe auf `this.groupedIssueIds` werden zu `this.groupedIssueIds.set/update/unset(path, …)` |
| Abbruch | `AbortController` in `clear()` | gleich (`HttpClient` mit `fetch`-Backend unterstützt `AbortSignal` über `HttpContext`-Token `ABORT_SIGNAL`; APIService reicht `signal` durch) | – |
| Normalisierte Map | `issue/issue.store.ts` (`issuesMap`, `issuesIdentifierMap`) | `EntityMap<TIssue>` + `EntityMap<string>` | `updateIssue(id, data)` = `patch` (setzt nur übergebene Schlüssel, wie lodash `set` je Key) |
| Filter-Helper | `issue/helpers/issue-filter-helper.store.ts` | gleicher Pfad | `computedFilteredParams`, `getPaginationParams`, `handleIssuesLocalFilters` (`localStorage.issue_local_filters`, E20 korrigiert) |
| Listen-Stores | `project/`, `cycle/`, `module/`, `project-views/`, `archived/`, `profile/`, `workspace/`, `workspace-draft/` (je `issue.store.ts`, `filter.store.ts`, `index.ts`) | gleiche Pfade | 1:1; E7 (falscher `clear`) und E8 (Draft-Key `PROFILE`) korrigiert |
| Kanban/Kalender-UI-State | `issue_kanban_view.store.ts`, `issue_calendar_view.store.ts` | gleiche Pfade | 1:1 |
| Detail-Store | `issue-details/*.ts` (12 Dateien) | gleiche Pfade | 1:1 |
| Toter Code | `issue_gantt_view.store.ts` | – | nicht portieren (E18) |

**Reaktivität der Listen:** Listen-Komponenten erhalten nur IDs (`getIssueIds(groupId, subGroupId)` = `memoizedComputed`, liefert dieselbe Array-Referenz, solange die Gruppe unverändert ist); Zeilen/Karten lesen `issuesMap.get(id)()` – Änderung eines Issues rendert nur dessen Zeile neu (A09 §5.2). `@for (id of ids(); track id)`.

**Optimistic-Update-Vertrag** (Test-Spezifikation, aus `issueUpdate` des Originals): (1) Snapshot `clone(issue)`; (2) `issues.updateIssue` + `updateIssueList(neu, alt)`; (3) wenn `shouldSync === false` Ende; (4) `updateParentStats(alt, neu)`; (5) `PATCH`; (6) `fetchParentStats`; Fehler ⇒ Map und Liste auf Snapshot zurück, Fehler weiterwerfen. Gleiches Muster für `removeIssue`, `issueQuickAdd` (temporäre Client-UUID), `updateProjectNavigationPreferences`, `updateUserTheme`, `updateUserProfile`, Favoriten-Reorder.

**Store-Typ-Kontext:** `IssuesStoreContext` → `InjectionToken<EIssuesStoreType> ISSUES_STORE_TYPE`, bereitgestellt von jeder Layout-Root-Komponente (`providers: [{provide: ISSUES_STORE_TYPE, useValue: EIssuesStoreType.CYCLE}]`); Fallback-Auflösung über Router-Parameter in der Reihenfolge aus A08 §2.6.2 (`useIssueStoreType` → `injectIssueStoreType()`). `useIssues(storeType)` → `inject(IssueRootStore).getIssuesStore(storeType)` (liefert `{issueMap, issues, issuesFilter}`). `useIssuesActions(storeType)` → `injectIssuesActions(storeType)` (gleiche Aktionsfassade).

### 3.5 Datenzugriff

#### 3.5.1 Service-Schicht

- **`APIService`** (`libs/shared/services/src/api.service.ts` und Web-Variante `libs/web/core/services/api.service.ts`): Konstruktor `(baseURL: string)`; Methoden `get<T>(url, params?, config?)`, `post(url, data?, config?)`, `put`, `patch`, `delete(url, data?, config?)`, `request(config)`; Rückgabe `Promise<{ data: T; status: number; headers }>` (Axios-Form, damit `.then(res => res?.data)` unverändert bleibt). `config` unterstützt `params`, `headers`, `signal`, `withCredentials`, `responseType`, `onUploadProgress` (→ `HttpClient` `reportProgress`/`observe:'events'`).
- **Fehlerform:** Bei HTTP-Fehler wird ein Objekt `{ response: { status, data, headers } }` geworfen (Axios-kompatibel), damit `err?.response?.data`, `err?.response`, `error.error`, `error.detail`, `error.error_code` in Stores/Komponenten unverändert funktionieren. Netzwerkfehler: `{ message, code: 'ERR_NETWORK' }`.
- Alle Service-Klassen (Tabelle A08 §2.7.2, 46 Web-Services + `PKG/services`) werden Methode für Methode übernommen; Basis-URL aus `RuntimeConfig.api_base_url` (Default `""`).
- **Uploads** (3 Schritte, A08 §2.7.1): `FileUploadService.uploadFile(url, formData, onProgress, signal)` ohne Credentials-Interceptor (`withCredentials:false`, `HttpContext SKIP_CREDENTIALS`), Fortschritt aus `HttpEventType.UploadProgress`; Proxy-Modus (01 ADR-026) ist transparent (gleiche Formularfelder, andere URL).

#### 3.5.2 Interceptor-Kette (Reihenfolge verbindlich)

| # | Interceptor | Datei | Verhalten (Original-Quelle) |
|---|---|---|---|
| 1 | `trailingSlashInterceptor` | `libs/shared/services/src/helpers/url.interceptor.ts` | `normalizeAPIRequestURL(url, baseURL)` aus `PKG/services/src/helpers/url.ts` **1:1** (relative und same-origin Pfade erhalten `/`, Query/Hash bleiben, fremde Origins (Presigned-URLs) unverändert); Tests `url.test.ts` portiert |
| 2 | `credentialsInterceptor` | `libs/web/core/http/credentials.interceptor.ts` | `withCredentials: true` außer `SKIP_CREDENTIALS` |
| 3 | `csrfInterceptor` | `libs/web/core/http/csrf.interceptor.ts` | nur für Requests mit Kontext `WITH_CSRF`: Header `X-CSRFTOKEN` aus `GET /auth/get-csrf-token/` (gecacht je Seitenaufruf) – Original nutzt CSRF nur für Formular-Flows; ADR-017 prüft Origin/Referer, daher kein globaler Header |
| 4 | `unauthorizedInterceptor` | `libs/web/core/http/unauthorized.interceptor.ts` | **nur web** (Original: nur `WEB/services/api.service.ts`): HTTP 401 und `location.pathname !== "/"` → `window.location.replace("/?next_path=" + encodeURIComponent(pathname))`; `PKG/services`-Aufrufe ohne diesen Effekt (Kontext `SKIP_401_REDIRECT`), Admin/Space ohne |
| 5 | `abortInterceptor` | `libs/shared/services/src/helpers/abort.interceptor.ts` | koppelt `AbortSignal` aus `config.signal` an die Subscription |

#### 3.5.3 QueryCache (SWR-Ersatz)

| Merkmal | SWR 2.4.2 (Original) | `QueryCache` (`libs/shared/state-kit/src/query-cache/`) |
|---|---|---|
| Schlüssel | String-Keys aus `PKG/constants/src/fetch-keys.ts` + Literal-Keys (A08 §2.11) | identische Strings; Key-Funktion darf `null` liefern (kein Abruf), wie bedingte SWR-Keys |
| API | `useSWR(key, fetcher, options)` → `{data, error, isLoading, isValidating, mutate}` | `injectQuery(() => key, fetcher, options)` im Injection-Context → `QueryRef` mit Signalen `data`, `error`, `isLoading`, `isValidating` und `mutate(data?, {revalidate?})`; `QueryCache.mutate(key \| predicate)` global |
| Deduplizierung | `dedupingInterval` 2 000 ms | gleich (laufender Promise je Key wird geteilt; Abruf innerhalb 2 s nach letztem Start wird nicht wiederholt) |
| Fokus | `revalidateOnFocus` (Throttle 5 000 ms) | `visibilitychange`/`focus`-Listener, Throttle 5 000 ms |
| Reconnect | `revalidateOnReconnect` | `online`-Event |
| Mount | `revalidateOnMount`, `revalidateIfStale` | gleich: vorhandene Daten werden sofort geliefert, Revalidierung nur wenn erlaubt |
| Polling | `refreshInterval`, `refreshWhenHidden` | gleich (Admin 600 000 ms) |
| Fehler-Retry | `errorRetryCount`, `shouldRetryOnError`, Backoff `~ (0.5 + random) · 2^min(n,8) · 5000 ms` | gleich |
| Lebensdauer | Cache global, Abos je Komponente | Cache global (`providedIn: 'root'`), Abo endet mit `DestroyRef` der Komponente |
| Konfiguration | `SWRConfig value` | `provideQueryCacheConfig(config)` + Optionen je Aufruf |

Fetcher rufen wie im Original **Store-Actions** (`() => store.fetchProjectDetails(ws, pid)`); der Store bleibt die Datenquelle für Templates, `QueryRef.data` wird nur dort gelesen, wo das Original `data` aus `useSWR` direkt verwendet (z. B. Einladungsseiten, `TIMEZONES_LIST`).

#### 3.5.4 Abwägung `httpResource`/`resource`

`httpResource` (stabil seit v22) wird **nicht** für Store-Daten verwendet (kein globaler Key-Cache, keine Fokus-Revalidierung, keine Kopplung an Store-Actions). Zulässig ist `resource()` für rein lokale, komponenteninterne Abrufe ohne SWR-Vorbild im Original (z. B. Vorschau eines Links in einem Modal), wenn kein Store betroffen ist.

### 3.6 Formulare

| `react-hook-form` (7.84) | Angular Signal Forms (⚠ API-Namen in S0 bestätigen) | Hinweis |
|---|---|---|
| `useForm({ defaultValues, mode })` | `form(signal(defaultValues), schema)` in der Komponente | `mode: 'onChange'`/`'onSubmit'` → Validierungszeitpunkt über `touched`/Submit-Flag |
| `register("name", { required, maxLength, validate })` | Schema-Funktionen `required(p.name, {message})`, `maxLength(...)`, `validate(...)` | Meldungstexte **wörtlich** (inkl. i18n-Keys) |
| `Controller` / `useController` (Propel-Felder, Dropdowns) | Direktive `[plFormField]` auf Propel-/Blocks-Komponenten (implementiert Signal-Forms-Kontrakt `FormValueControl`) | DOM unverändert |
| `formState.{isDirty, dirtyFields, isSubmitting, errors}` | `form().dirty()`, abgeleitete `dirtyFields` (Hilfsfunktion `getDirtyFields(form, defaults)`), lokales `isSubmitting`-Signal, `errors()` | `getChangedIssuefields` (A09) nutzt `dirtyFields` |
| `reset(values)` / `setValue` / `watch` | `model.set(values)` + `reset()`, `model.update`, `computed` | Reset-Zeitpunkte wie Original (z. B. Projektwechsel im Issue-Modal) |
| `handleSubmit(fn)` | `(submit)`-Handler mit `submit(form, fn)` | – |
| `getNestedError` (`WEB/helpers/react-hook-form.helper.ts`) | `libs/web/core/helpers/form.helper.ts` | gleiche Signatur gegen Signal-Forms-Errors |

Fallback (S0 rot): Reactive Forms (`FormGroup`, `ControlValueAccessor` auf denselben Komponenten) – Template-/DOM-Struktur bleibt gleich.

### 3.7 i18n

- **Dateien:** `PKG/i18n/src/locales/{22 Sprachen}/{28 Namespaces}.json` → `FE/libs/shared/i18n/src/locales/**` (1:1, gleiche Ordner `bg, cs, de, en, es, fr, id, it, ja, ka-ge, ko, nl, pl, pt-BR, ro, ru, sk, tr-TR, ua, vi-VN, zh-CN, zh-TW`). Build kopiert sie als Assets nach `/{base}/i18n/` (alle drei Apps). EE-Namespaces (`automation`, `template`, `wiki`, `work-item-type`, `workflow`, …) werden mitkopiert (Texte für spätere Pakete, A13b §2.1.8).
- **Instanz:** `PKG/i18n/src/core/instance.ts` 1:1 (Optionen A13b §2.1.2: `fallbackLng "en"`, `supportedLngs`, `ns` = 28, `defaultNS "common"`, `fallbackNS` = übrige, `keySeparator "."`, `nsSeparator false`, `interpolation.escapeValue false`, `returnNull/returnEmptyString false`, Plugin `ICU`), Backend: `resourcesToBackend((lng, ns) => fetch(\`${base}i18n/${lng}/${ns}.json\`).then(r => r.json()))`; `initReactI18next` entfällt.
- **API** (`TranslationService`, `libs/shared/i18n/src/translation.service.ts`): `t(key, params?)` inkl. `coerceToString`, Signal `currentLocale`, `changeLanguage(lng)` (fire-and-forget, `console.error` bei Fehler), `languages = SUPPORTED_LANGUAGES`, `setLanguage(lng): Promise<void>` (`localStorage.userLanguage`, `<html lang>`). Pipe `t` (`{{ 'workspace.title' | t: {name} }}`) ist `pure: false` und liest das Signal `currentLocale()`; ein Sprachwechsel markiert dadurch alle Templates mit `t` als geändert (zoneless), ohne Neuladen.
- **Typisierung:** `tools/i18n-generate-types` (Port von `PKG/i18n/scripts/generate-types.ts`) erzeugt `TTranslationKeys`; `t()` ist auf `TTranslationKeys` typisiert (Verbesserung ohne UI-Wirkung, A13b §5.2).
- **ICU/Plural:** ausschließlich i18next-icu (`intl-messageformat`, `Intl.PluralRules`); Sonderfall `ua` → en-US-Regeln wie Original (A13b §2.1.3).
- **Profil-Sync:** wie A13b §3.1 (Profil-Fetch → `setLanguage(profile.language)`; Update optimistisch; Sign-out → `en`).
- **Datumsformate** bleiben wie Original **englisch** (date-fns ohne Locale, `Intl.DateTimeFormat("en-US")`, A13b §3.1 Pkt. 7) – keine Lokalisierung, die das Original nicht hat.
- **QA:** `tools/i18n-sync-check` (Port `sync-check.ts`, `--ci`) im CI; Skill `translate` aus dem Original-Repo gilt für neue Keys.

### 3.8 Theming

| Anforderung | Umsetzung |
|---|---|
| Kein Theme-Flash | Inline-Script in `index.html` (§5.1): liest `localStorage.theme` (fehlt → `system`), ungültiger Wert (nicht in Theme-Liste der App) → `system`, löst `system` per `matchMedia('(prefers-color-scheme: dark)')` auf, setzt `document.documentElement.dataset.theme` und `style.colorScheme` **nur** für `light`/`dark` (next-themes `enableColorScheme`) |
| `ThemeService` (`libs/web/core/theme/theme.service.ts`, Admin/Space eigene Instanz mit eingeschränkter Liste) | Signale `theme`, `resolvedTheme`, `systemTheme`; `setTheme(value)` schreibt Attribut + `localStorage`; Listener `matchMedia` (System-Wechsel) und `storage` (Tab-übergreifend) |
| Server-Sync | `StoreWrapperComponent`: einmal je User-Sitzung `setTheme(profile.theme.theme \|\| 'system')`; danach führt `localStorage` |
| Custom Theme | `applyCustomTheme(primary, background, 'dark'\|'light')`/`clearCustomTheme()` aus `@plane/utils` (unverändert, Inline-Styles am `<html>`), Effekt bei Änderung von `profile.theme` |
| Wechsel durch Nutzer | `ThemeSwitcherComponent`: `setTheme` → ggf. `applyCustomTheme` → `updateUserTheme` mit Promise-Toast → `window.location.reload()` (Parität, A13a §3.2) |
| High Contrast | rein CSS (Selektoren `[data-theme="light-contrast"]`, `[data-theme="dark-contrast"]` aus Propel-Styles) |
| Theme-abhängige Raster-Assets | Hilfsfunktionen `isLightStrict`, `isDarkStrict`, `resolveGeneralTheme` (`libs/web/core/theme/theme-assets.ts`), je Fundstelle dasselbe Muster wie Original |
| Admin/Space | Themes `light`, `dark`, `system`; gleicher Storage-Schlüssel `theme` (gleiche Origin teilt den Wert wie im Original) |
| Sign-out | `localStorage.theme = "system"` (RootStore.resetOnSignOut) |
| CSP | Inline-Script per Hash in der CSP des Gateways (`script-src 'self' 'sha256-…'`); Hash wird im Build berechnet und als `theme-script.sha256` neben `index.html` abgelegt (Gateway liest ihn) |

### 3.9 Interaktions- und Layout-Bausteine

| Baustein | Original | Ziel (Bibliothek/Datei) | Architekturregel | ab |
|---|---|---|---|---|
| **Drag & Drop** | `@atlaskit/pragmatic-drag-and-drop` 1.7.4 (+ `-auto-scroll` 1.4.0, `-hitbox` 1.1.0; `combine`, `tree-item`-Instruktionen) | gleiche Pakete; `libs/shared/dnd`: `[plDraggable]` (`getInitialData`, `onDragStart`, `onDrop`, `canDrag`), `[plDropTarget]` (`getData` inkl. `attachInstruction`, `canDrop`, `onDragEnter/Leave/Drop`), `[plDndMonitor]`, `[plAutoScroll]`; `DropIndicatorComponent` 1:1 | Registrierung in `afterNextRender`, Cleanup über `DestroyRef`; Algorithmen (`handleGroupDragDrop`, Sort-Order 65535/Mittelwert, Gantt ±1000, Sidebar-Reorder ±10000) aus `work-items-core`; `highlightIssueOnDrop` + `smooth-scroll-into-view-if-needed` (`block:"center", duration:1500`) | I1/I2 |
| **Virtualisierung** | `RenderIfVisible` (`WEB/components/core/render-if-visible-HOC.tsx`), `@tanstack/react-virtual` in `PKG/blocks/{select,virtual-list}` | `*plRenderIfVisible` (Inputs `root`, `verticalOffset`, `horizontalOffset`, `defaultHeight`, `placeholder: TemplateRef`, `shouldRecordHeights`, `defaultValue`, `useIdleTime`, `as`), `@tanstack/virtual-core` 3.13 in Blocks-`select`/`virtual-list` | Platzhalterhöhe = zuletzt gemessene Höhe bzw. `getApproximateCardHeight`; neue Issues (< 30 s) sofort; `forceRender` bei Drag/Peek | I2 |
| **Pagination-Sentinel** | `useIntersectionObserver` | `[plIntersection]` (`rootMargin`, `disabled`) | Loader `pagination` verhindert Doppel-Requests | I2 |
| **Command-Palette (Power K)** | `cmdk` 1.1.1, `WEB/components/power-k/**` | `pl-command` (D08-ADR-17), `libs/web/power-k` (core 1:1, `config/*` Befehle 1:1, `menus/*`, `ui/*` als Komponenten); `PowerKStore` in core | Registry `POWER_K_COMMANDS` (§6) speist dieselbe `PowerKCommandRegistry`; Kontext-Erkennung `context-detector.ts` 1:1 | I5 |
| **Emoji-/Icon-/Logo-Picker** | `PKG/blocks/src/emoji-icon-picker` (frimousse 0.3, Lucide- und Material-Icons, `use-font-face-observer`) | `libs/shared/blocks/emoji-icon-picker` (D08-ADR-20); `FontFaceObserver` → `document.fonts.load('1em "Material Symbols Rounded"')` | Emoji-Daten gebündelt; Suche/Skin-Tone wie frimousse; DOM-Snapshot-Test gegen Original | I2 (I1 Logo-Picker im Projekt-Formular) |
| **Emoji-Reaktionen** | `PKG/blocks/src/emoji-reaction` | `libs/shared/blocks/emoji-reaction` | API-Format dezimale Codepoints mit „-“ | I2 |
| **Date-Picker** | Propel `Calendar` (react-day-picker 10.0.1), Blocks `DateSelect`/`DateRangeSelect` | `pl-calendar` (D08-ADR-21), `libs/shared/blocks/property-select/date-select*` | Format `MMM dd, yyyy`, `MERGE_TOKENS` 1:1 | I2 |
| **Charts** | `recharts` 2.15.4 (`PKG/blocks/src/charts/{area,bar,line,pie,radar,tree-map}`, Burndown, Analytics) | `libs/shared/blocks/charts/*` mit D3 (D08-ADR-18), Tooltip/Legende als Angular-Komponenten | Spike S6; RadarChart lazy wie Original | I3 |
| **Gantt/Timeline** | `WEB/components/gantt-chart/**`, `WEB/store/timeline/*`, `base-layouts/gantt` | `libs/web/work-items/components/gantt-chart/**`, `TimeLineStore` + Unter-Stores | `dayWidth` 60/20/5, Scroll-Erweiterung links/rechts, Block 44 px, Sidebar-Reorder mit `GanttDnDHOC` → Direktive; `isDependencyEnabled = false` (A9-Andockstelle §6) | I2 (Issues), I3 (Modules) |
| **Kanban** | `WEB/components/issues/issue-layouts/kanban/**` | `libs/web/work-items/components/issue-layouts/kanban/**` | zweistufige Virtualisierung (Spalten + Karten), `KanBanView`-Store, Löschzone, Swimlanes | I2 |
| **Spreadsheet** | `issue-layouts/spreadsheet/**`, `use-table-keyboard-navigation` | gleiche Ordner; Sticky-Spalten-Schatten als Direktive `[plStickyColumnShadow]`; Tastaturnavigation `[plTableKeyboardNavigation]` | `SPREADSHEET_COLUMNS`/`SPREADSHEET_PROPERTY_LIST` + Registry `SPREADSHEET_COLUMNS` (A1-Andockstelle §6) | I2 |
| **Kalender-Layout** | `issue-layouts/calendar/**`, `issue_calendar_view.store.ts` | gleiche Ordner | Wochenstart aus Profil, Keys `y-`/`m-`/`w-` | I2 |
| **Insight-Tabelle** | `@tanstack/react-table` 8.21.3 (`WEB/components/analytics/insight-table/*`) | `@tanstack/angular-table` 8.21.x | – | I5 |
| **Masonry (Stickies)** | `react-masonry-component` 6.3 (`WEB/components/stickies/layout/stickies-list.tsx`) | `masonry-layout` 4.2.2 (MIT, die von react-masonry-component gekapselte Bibliothek) in Direktive `[plMasonry]` mit gleichen Optionen | `layout()` nach Inhaltsänderung (ResizeObserver) | I5 |
| **Dropzone** | `react-dropzone` 14.2 (Attachments, Workspace-Logo-Upload) | Direktive `[plDropzone]` (`accept`, `maxSize`, `multiple`, `noClick`, `onDrop(accepted, rejected)`), MIME-Prüfung wie `attr-accept` | Fehlercodes `file-too-large`, `file-invalid-type` wie react-dropzone (Toasts lesen sie) | I2 (I1 Logo) |
| **Overlays/Portale** | Base-UI-Portale, `#full-screen-portal`, `#context-menu-portal`, `#editor-portal`, `spreadsheet-menu-portal` | CDK Overlay mit eigenem Container an `document.body`; Marker-Attribut `data-base-ui-portal` am Overlay-Container (Outside-Click-Logik des Peeks, A09 §5.2) | Positionierung `@floating-ui/dom` 1.7 | I0 |
| **Toasts** | `PKG/blocks/src/toast` (`setToast`, `setPromiseToast`) | `libs/shared/blocks/toast` (`ToastService` + Funktionen `setToast`/`setPromiseToast` als dünne Fassade) | Texte/Typen 1:1 | I0 |
| **Zwischenablage/CSV** | `copyUrlToClipboard`, `export-to-csv` | `@plane/utils` 1:1, `export-to-csv` 1.4 | – | I1/I5 |
| **Ungespeicherte Änderungen** | `use-reload-confirmation` | `ReloadConfirmationService` (`beforeunload` + Anker-Klick-Abfang, Text 1:1) + `canDeactivate`-Guard für Router-Navigationen | Parität CE-UIX-008 | I1 |

### 3.10 Shortcuts

- **Kern 1:1:** `WEB/components/power-k/core/shortcut-handler.ts` (`ShortcutHandler`, `resolveShortcutKey`, `formatModifierShortcut`, `isTypingInInput`, `loadKeyboardLayoutMap`, Sequenzen mit Timeout) und `registry.ts` werden **unverändert** übernommen (nur `computedFn` → `memoizedComputed`, React-Icon-Typen → Angular-Komponententyp).
- **Bindung:** `GlobalShortcutsService` (Ersatz `global-shortcuts.tsx`) registriert einen `document:keydown`-Listener nach dem Login im `ProjectsAppPowerKProvider`-Äquivalent (`ProjectsAppPowerKComponent`, eingebunden in `LPRJ`, `LSET`, `LPROF`), Kontext aus `context-detector.ts` + `RouterStore`.
- **Befehle** (aus `power-k/config/**`, vollständig zu übernehmen): Navigation `ow, gh, gx, gy, op, gp, ga, gj, gr, os, gs, gi, oc, gc, om, gm, ov, gv, gd, gk`; Erstellen `ni, nd, nv, nc, nm, np`; Modifier `cmd+k` (Palette), `cmd+b`, `cmd+shift+c`, `cmd+f`, `cmd+/`; Kontextbefehle je `TPowerKContextType` (`work-item`, `page`, `cycle`, `module`). Anzeige der Badges (`ShortcutBadge`, `KeySequenceBadge`) mit Mac-/Nicht-Mac-Glyphen wie Original.
- **Weitere Tastaturpfade** (A09 §3.14): Peek-Escape mit Ausnahmen, Spreadsheet-Pfeiltasten, Mehrfachauswahl (`use-multiple-select`), Editor-Shortcuts (Tiptap, Dokument 10), `use-auto-save` (Ctrl/Cmd+S, 30 s) – jeweils als Service/Direktive mit gleicher Prioritätsreihenfolge; Prüfung `isTypingInInput` bleibt die einzige Quelle für „Eingabefokus“.
- Konflikte mit Browser-Shortcuts: Original ruft `preventDefault` nur bei gefundenem Befehl – identisch.

### 3.11 Runtime-Config

| Feld (`runtime-config.json`, 01 §7.12) | Original | Nutzung |
|---|---|---|
| `api_base_url`, `api_base_path` | `VITE_API_BASE_URL`, `VITE_API_BASE_PATH` | `API_BASE_URL`/`API_URL` in `@plane/constants` (`endpoints.ts`) |
| `web_base_url`, `web_base_path` | `VITE_WEB_BASE_URL/PATH` | `WEB_URL` |
| `admin_base_url`, `admin_base_path` | `VITE_ADMIN_BASE_URL/PATH` (Default `/god-mode`) | `GOD_MODE_URL` |
| `space_base_url`, `space_base_path` | `VITE_SPACE_BASE_URL/PATH` (Default `/spaces`) | `SITES_URL` |
| `live_base_url`, `live_base_path` | `VITE_LIVE_BASE_URL/PATH` (Default `/live`) | Hocuspocus-URL, SignalR-URL |
| `app_version` | – | Hilfe-Menü „Version“ (CE-WS-014) |
| `enable_session_recorder` | – | immer `false` (ADR-004) |
| **neu (präzisiert 01 §7.12):** `website_url`, `support_email`, `external_links_enabled` | `VITE_WEBSITE_URL`, `VITE_SUPPORT_EMAIL`, hartcodierte Links (GitHub-Star, Forum, Status-Page, X) | Default `website_url: ""`, `support_email: ""`, `external_links_enabled: false` (Airgap, A08 O8) |

- **Bereitstellung:** `RUNTIME_CONFIG`-Token (`libs/shared/runtime-config`), geladen vor allen anderen Initializern; `@plane/constants/endpoints.ts` wird so angepasst, dass die Konstanten **Getter** auf das Token-Objekt sind (`export const API_BASE_URL = runtimeConfig.api_base_url` würde zur Importzeit auswerten → stattdessen `getApiBaseUrl()`; die Abweichung ist auf `endpoints.ts` und dessen ≈ 30 Verwender begrenzt und wird mechanisch per Codemod angepasst).
- Gateway liefert die Datei je App unter `/{base}runtime-config.json` mit `Cache-Control: no-store`.

### 3.12 Realtime im Frontend

| Thema | Ziel | Quelle |
|---|---|---|
| Kollaboration Pages | `@hocuspocus/provider` 2.15.2 unverändert in `libs/shared/editor/collaboration`; URL `${live_base_url \|\| origin}${live_base_path}/collaboration?documentType=project_page&projectId=…&workspaceSlug=…`; Token-JSON `{id}`; Cookie über same-origin | `WEB/components/pages/editor/editor-body.tsx`, ADR-022 |
| Offline-Cache | `y-indexeddb` 9.0.12 | `PKG/editor` |
| Stateless-Seitenereignisse | `RealtimePageEventsService` (Port `use-realtime-page-events.tsx`, `use-collaborative-page-actions.tsx`) | A08 §2.8.2 |
| REST-Fallback | `PageFallbackService` (Port `use-page-fallback.ts`) + `AutoSaveService` | CE-RT-003 |
| Live-Events (H6) | `LiveEventsService` (D08-ADR-22) + Multi-Provider `LIVE_EVENT_HANDLERS` | 01 §1.4 |

### 3.13 Performance

| Maßnahme | Ziel/Messung |
|---|---|
| Zoneless + OnPush + Signale; Zeilen/Karten lesen nur ihr Issue-Signal | Änderung eines Issues rendert ≤ 1 Zeile/Karte neu (Test über `ComponentFixture`-Render-Zähler) |
| `@for … track id` überall in Listen | Lint-Regel `@angular-eslint/template/use-track-by-function`-Äquivalent für Control Flow (`track $index` verboten in Listen von Entitäten) |
| Virtualisierung wie Original (§3.9) | Kanban 1 000 Karten/8 Spalten ≥ 55 fps beim Drag (S4) |
| Lazy Loading je Page/Layout, RadarChart, Profil-Settings-Tabs, `ProfileSettingsModal`, Editor (Rich/Document) | Initial-Bundle-Budget §3.1.2 |
| `memoizedComputed` mit LRU | kein unbegrenztes Wachstum (Test 10 000 Keys → ≤ 1 000 gecachte) |
| Request-Abbruch beim Layoutwechsel (`AbortController`) | kein veralteter Response überschreibt neuere Liste (E2E schneller Layoutwechsel) |
| Idle-Rendering (`useIdleTime`, `runIdleTask`) | wie Original |
| Fonts: Inter-Woff2-Preload (`<link rel=preload>` im `index.html`) | wie `root.tsx` |
| Keine Zone-/Polyfill-Last, `withFetch()` | – |
| Messgrößen (CI, Lighthouse lokal, Airgap) | LCP Workspace-Home ≤ Original + 10 %, TBT ≤ Original + 10 % (Referenz gemessen in I0 gegen Original-Build) |

### 3.14 Fehlerbehandlung, Status- und Fehlerseiten

| Seite/Mechanismus | Ziel | Original |
|---|---|---|
| 404 (`**`) | `NotFoundPageComponent` (Bild `404.svg`, „Go to Home“ `/`, Meta `noindex`) | `WEB/app/not-found.tsx` |
| Globale Fehlerseite | `PlaneErrorHandler` → `ErrorPageService.show(error)`; DEV-Variante (Route Error/Stack) bei `isDevMode()`, PROD-Variante mit Links nur bei `external_links_enabled` (Support-Mail aus `support_email`) | `WEB/app/error/{dev,prod,index}.tsx` |
| Layout-Fehlergrenze | Komponente `pl-layout-error-boundary` mit Fallback-Signal; Fehler aus Layout-Stores/Templates werden über `ErrorHandler` + `catchError` im Layout-Root abgefangen | `layout-error-boundary.tsx` |
| Stale-Chunk | `isStaleAssetError` (Signaturen aus `WEB/lib/stale-asset-error.ts` + Angular-Varianten „Failed to fetch dynamically imported module“, „Loading chunk“), max. 1 Reload je 30 s über `sessionStorage.__plane_chunk_reload`; Quellen: `withNavigationErrorHandler`, `ErrorHandler`, `window` `error`/`unhandledrejection` | `WEB/lib/stale-asset-error.ts`, `entry.client.tsx` |
| Maintenance / Instance not ready / Workspace not found / Not authorized / Project access / Disabled feature | Wrapper-Zustände §3.3.4 | A08 §2.12 |

### 3.15 Browser-Storage

Alle Schlüssel und Formate aus A08 §2.10 (web), A11 §2.14 (admin: `theme`, `god_mode_sidebar_collapsed`) und A11 §2.26 (space) werden **identisch** übernommen und ausschließlich über `persisted()` bzw. `@plane/cdk` `LocalStorageService` (Port `use-local-storage.tsx` inkl. Custom-Event `local-storage:${key}`) gelesen/geschrieben. Formate exakt (JSON vs. String, z. B. `module_sidebar_collapsed` als JSON-String `"true"`, E10 beibehalten). `lib/local-storage.ts` (leere Objekte/falsy werden nicht gespeichert) 1:1. Die acht nur geschriebenen `*_collapsed`-Schlüssel des Theme-Stores (E14) werden ebenfalls nur geschrieben. IndexedDB nur durch `y-indexeddb`.

---
## 4. Vollständige Mapping-Tabellen Original → Ziel

### 4.1 Routen `web` (vollständig, Reihenfolge = Deklarationsreihenfolge in `FE/apps/web/src/app.routes.ts`)

Spalten: **#** = Nummer aus A08 §2.2 (R = neu/geändert) · **React-Route** (`WEB/app/routes/core.ts`) · **Angular-Eintrag** (Pfad relativ zur Elternroute, `›` = Kind) · **Komponente/Redirect** (Pfad relativ `FE/apps/web/src/pages/`) · **Wrapper/Guard/Resolver** · **Ink.** · **CE-IDs**. Alle Pages per `loadComponent`. Layout-Kürzel und Komponenten siehe §4.4.

**Ebene L0 (`AppShellLayoutComponent`, Pfad `''`), Block A – Redirects mit statischem Präfix (vor allem anderen):**

| # | React-Route | Angular-Eintrag | Komponente / Redirect | Wrapper/Guard | Ink. | CE-IDs |
|---|---|---|---|---|---|---|
| 62 | `accounts/sign-up` | `accounts/sign-up` | `redirectTo: '/'` (Original: `/sign-up/`; ADR-008) | – | I0 | CE-UIX-012, CE-AUTH-002 (entfällt) |
| 63 | `sign-in` | `sign-in` | `redirectTo: '/'` | – | I0 | CE-UIX-012 |
| 64 | `signin` | `signin` | `redirectTo: '/'` | – | I0 | CE-UIX-012 |
| 65 | `login` | `login` | `redirectTo: '/'` | – | I0 | CE-UIX-012 |
| 66 | `register` | `register` | `redirectTo: '/'` (Original: `/sign-up/`) | – | I0 | CE-UIX-012 |
| 67 | `profile/*` | `{ matcher: splatMatcher('profile') }` | `redirectToProfileSettings`: `/settings/profile/{splat \|\| "general"}?{query}` (immer `?`, E15) | – | I1 | CE-UIX-012 |
| 2 | `sign-up` (L `(all)/sign-up/layout.tsx`) | `sign-up` | `redirectTo: '/'` (CE-AUTH-002/-005 entfallen) | – | I0 | CE-AUTH-002 (entfällt) |
| 3 | `accounts/forgot-password` | `accounts/forgot-password` | `redirectTo: '/'` | – | I0 | CE-AUTH-017 (entfällt) |
| 4 | `accounts/reset-password` | `accounts/reset-password` | `redirectTo: '/'` | – | I0 | CE-AUTH-018 (entfällt) |
| 5 | `accounts/set-password` | `accounts/set-password` | `redirectTo: '/'` | – | I0 | CE-AUTH-019 (entfällt) |

**Block B – statische Top-Level-Routen (vor `:workspaceSlug`):**

| # | React-Route | Angular-Eintrag | Komponente | Wrapper/Guard | Ink. | CE-IDs |
|---|---|---|---|---|---|---|
| 1 | index (L `(home)/layout.tsx`) | `''` (`pathMatch:'full'`, `HomeLayoutComponent`, `data.robots: 'index, nofollow'`) › `''` | `(home)/page.ts` → `SignInPageComponent` (Einstieg „Mit Keycloak anmelden“, Fehler-Banner aus `error_code`) | `AuthenticationWrapper` `NON_AUTHENTICATED` | I0 | CE-AUTH-001 (angepasst), CE-AUTH-014 (angepasst), CE-AUTH-029, CE-AUTH-015 |
| 6 | `create-workspace` | `create-workspace` (`CreateWorkspaceLayoutComponent`, `title: 'Create Workspace'`) › `''` | `(all)/create-workspace/page.ts` → `CreateWorkspacePageComponent` | `AuthenticationWrapper` `AUTHENTICATED`; Zustand `is_workspace_creation_disabled` in-place | I0 | CE-WS-001, CE-INST-028 |
| 7 | `onboarding` | `onboarding` (`OnboardingLayoutComponent`, `title: 'Onboarding'`) › `''` | `(all)/onboarding/page.ts` → `OnboardingPageComponent` | `ONBOARDING`; Query-Key `USER_WORKSPACES_LIST` | I1 | CE-AUTH-030 (angepasst: ohne Passwortschritt) |
| 8 | `invitations` | `invitations` (`InvitationsLayoutComponent`, `title: 'Invitations'`) › `''` | `(all)/invitations/page.ts` → `InvitationsPageComponent` | `AUTHENTICATED`; Keys `USER_WORKSPACE_INVITATIONS` | I1 | CE-WS-011 |
| 9 | `workspace-invitations` | `workspace-invitations` (`WorkspaceInvitationsLayoutComponent`, `title: 'Workspace Invitations'`) › `''` | `(all)/workspace-invitations/page.ts` → `WorkspaceInvitationsPageComponent` | `PUBLIC`; Key `WORKSPACE_INVITATION_${id}`; externe Links nur bei `external_links_enabled` | I1 | CE-WS-011, CE-AUTH-028 |

**Block C – Redirects mit `:workspaceSlug`-Präfix (vor dem Workspace-Baum):**

| # | React-Route | Angular-Eintrag | Redirect-Ziel | Ink. | CE-IDs |
|---|---|---|---|---|---|
| 58 | `:workspaceSlug/projects/:projectId/settings/*` | `{ matcher: splatMatcher(':workspaceSlug/projects/:projectId/settings') }` | `/:ws/settings/projects/:projectId/{splat}/` bzw. ohne Splat `/:ws/settings/projects/:projectId/` | I1 | CE-UIX-012 |
| 59 | `:workspaceSlug/analytics` | `':workspaceSlug/analytics'` (`pathMatch:'full'`) | `/:ws/analytics/overview/` | I5 | CE-UIX-012, CE-ANA-001 |
| 60 | `:workspaceSlug/settings/api-tokens` | `':workspaceSlug/settings/api-tokens'` | `/settings/profile/api-tokens/` | I6 | CE-UIX-012, CE-WH-012 |
| 61 | `:workspaceSlug/projects/:projectId/inbox` | `':workspaceSlug/projects/:projectId/inbox'` | `/:ws/projects/:projectId/intake/` | I3 | CE-UIX-012, CE-INT-002 |
| 68 | `:workspaceSlug/settings/account/*` | `{ matcher: splatMatcher(':workspaceSlug/settings/account') }` | `/settings/profile/{splat \|\| "general"}?{query}` | I1 | CE-UIX-012 |
| R1 | `:workspaceSlug/settings/billing` (Route 41, entfällt nach ADR-001) | `':workspaceSlug/settings/billing'` | `/:ws/settings/` | I1 | – (ADR-001) |
| R2 | (E1) `/:ws/settings/projects/:pid/features` (im Original ohne Route → 404) | `':workspaceSlug/settings/projects/:projectId/features'` (`pathMatch:'full'`) | `/:ws/settings/projects/:projectId/features/cycles/` (**Korrektur E1**, `deviations.yaml` FE-E1) | I1 | CE-PRJ-019, CE-PRJ-020 |

**Block D – `AllLayoutComponent` (LALL, Pfad `''`, `data.robots: 'noindex, nofollow'`):**

| # | React-Route | Angular-Eintrag | Komponente | Wrapper/Guard | Ink. | CE-IDs |
|---|---|---|---|---|---|---|
| 57 | `settings/profile/:profileTabId` | `settings/profile` (`ProfileSettingsLayoutComponent` = LPROF) › `':profileTabId'` | `(all)/settings/profile/[profileTabId]/page.ts` → `ProfileSettingsPageComponent` (Tabs `general, security, preferences, notifications, api-tokens`; `security` zeigt nur Keycloak-Verweis, Passwort ändern entfällt) | LPROF: `ProjectsAppPowerKComponent`, `AuthenticationWrapper` `AUTHENTICATED`; ungültiger Tab → Redirect `general` (**Korrektur E13**, FE-E13) | I1 (`api-tokens`-Tab I6) | CE-PROF-002, CE-PROF-003, CE-PROF-006, CE-NOTIF-009, CE-WH-012, CE-I18N-001, CE-AUTH-020 (entfällt) |
| – | `:workspaceSlug` (L `[workspaceSlug]/layout.tsx`) | `':workspaceSlug'` (`WorkspaceLayoutComponent` = LWS) | – | `AuthenticationWrapper` `AUTHENTICATED` → `WorkspaceAuthWrapper` → AppRail (aus) → `WorkspaceContentWrapper` → `GlobalModals` | I0 | CE-WS-013, CE-WS-012, CE-WS-008 |

**Block E – unter `:workspaceSlug` › `''` (`ProjectsAppLayoutComponent` = LPRJ):**

| # | React-Route | Angular-Eintrag (relativ) | Komponente (`(all)/[workspaceSlug]/(projects)/…`) | Header-Layout / Besonderheit | Ink. | CE-IDs |
|---|---|---|---|---|---|---|
| 10 | `:workspaceSlug` | `''` (`pathMatch:'full'`) | `page.ts` → `WorkspaceHomePageComponent` (rendert `AppHeader` „Home“ selbst) | Titel `${ws} - Home` | I0 (Shell, Home ohne Widgets) · I5 (Widgets) | CE-WS-013, CE-HOME-001…-006, CE-HOME-008 |
| 11 | `:workspaceSlug/active-cycles` | `active-cycles` (`ActiveCyclesLayoutComponent`) › `''` | `active-cycles/page.ts` → `WorkspaceActiveCyclesPageComponent` – **echte Ansicht statt Upsell (ADR-001)** aus CE-Bausteinen (`GET /api/workspaces/{ws}/active-cycles/`, Inline-Dashboard CE-CYC-003); `UpgradeBadge` entfällt | – | I3 | CE-CYC-004, CE-CYC-003 |
| 12 | `:workspaceSlug/analytics/:tabId` | `analytics/:tabId` (`AnalyticsTabLayoutComponent`) › `''` | `analytics/[tabId]/page.ts` → `WorkspaceAnalyticsPageComponent` | ungültige `tabId` → keine Tab-Inhalte (E13 beibehalten) | I5 | CE-ANA-001…-007 |
| 13 | `:workspaceSlug/browse/:workItem` | `browse/:workItem` (`BrowseWorkItemLayoutComponent`) › `''` | `browse/[workItem]/page.ts` → `WorkItemBrowsePageComponent` (`ProjectAuthWrapper` innen) | Intake-Item → Redirect `/${ws}/projects/${pid}/intake/?currentTab=open&inboxIssueId=${id}`; Fehler → EmptyState | I2 | CE-WI-009 |
| 14 | `:workspaceSlug/drafts` | `drafts` (`DraftsLayoutComponent`) › `''` | `drafts/page.ts` → `WorkspaceDraftsPageComponent` | Titel „Workspace Draft“ | I2 | CE-WI-049 |
| 15 | `:workspaceSlug/notifications` | `notifications` (`NotificationsLayoutComponent`) › `''` | `notifications/page.ts` → `WorkspaceNotificationsPageComponent` | Sidebar ausgeblendet (`PathnameService` enthält `/${ws}/notifications`) | I5 | CE-NOTIF-004…-007 |
| 16 | `:workspaceSlug/profile/:userId` | `profile/:userId` (`UserProfileLayoutComponent`) › `''` (`pathMatch:'full'`) | `profile/[userId]/page.ts` → `UserProfileOverviewPageComponent` | – | I5 | CE-PROF-008, CE-PROF-011 |
| 18 | `:workspaceSlug/profile/:userId/activity` | › `activity` (**vor** `:profileViewId`) | `profile/[userId]/activity/page.ts` → `UserProfileActivityPageComponent` | Cursor `100:{i}:0` | I5 | CE-PROF-010 |
| 17 | `:workspaceSlug/profile/:userId/:profileViewId` | › `':profileViewId'` | `profile/[userId]/[profileViewId]/page.ts` → `UserProfileIssuesPageComponent` | ungültig → leer (E13 beibehalten); Gast → Hinweistext | I5 | CE-PROF-009 |
| 19 | `:workspaceSlug/stickies` | `stickies` (`StickiesLayoutComponent`) › `''` | `stickies/page.ts` → `StickiesPageComponent` | Titel „Your stickies“ | I5 | CE-HOME-009, CE-HOME-010 |
| 20 | `:workspaceSlug/workspace-views` | `workspace-views` (`WorkspaceViewsLayoutComponent`) › `''` (`pathMatch:'full'`) | `workspace-views/page.ts` → `WorkspaceViewsPageComponent` | – | I3 | CE-LV-052, CE-LV-053 |
| 21 | `:workspaceSlug/workspace-views/:globalViewId` | › `':globalViewId'` | `workspace-views/[globalViewId]/page.ts` → `WorkspaceViewDetailPageComponent` | `ISSUES_STORE_TYPE = GLOBAL` | I3 | CE-LV-054, CE-LV-015 |
| 22 | `:workspaceSlug/projects/archives` | `projects/archives` (`ArchivedProjectsLayoutComponent`) › `''` | `projects/(detail)/archives/page.ts` → `ArchivedProjectsPageComponent` | liegt nicht unter LPD | I1 | CE-PRJ-008, CE-PRJ-001 |
| 23 | `:workspaceSlug/projects` | `projects` (`pathMatch` über Kind `''`, `ProjectListLayoutComponent`) › `''` | `projects/(list)/page.ts` → `ProjectListPageComponent` | – | I0 (Liste + Anlegen) · I1 (Karten, Filter, Statistiken) | CE-PRJ-001…-004 |
| 35 | `:ws/projects/:projectId/archives/issues` | `projects/:projectId/archives/issues` (`ArchivedIssuesListLayoutComponent`) › `''` | `projects/(detail)/[projectId]/archives/issues/(list)/page.ts` → `ArchivedIssuesPageComponent` | **E5 korrigiert:** `ProjectBootstrapComponent` (lädt Projekt-Stammdaten wie `ProjectAuthWrapper`, ohne Tab-Leiste) (FE-E5) | I3 | CE-WI-045, CE-LV-046 |
| 36 | `:ws/projects/:projectId/archives/issues/:archivedIssueId` | `projects/:projectId/archives/issues/:archivedIssueId` (`ArchivedIssueDetailLayoutComponent`) › `''` | `…/archives/issues/(detail)/[archivedIssueId]/page.ts` → `ArchivedIssueDetailPageComponent` | E6 (leeres Fragment bis Daten) beibehalten; Bootstrap wie 35 | I3 | CE-WI-045 |
| 37 | `:ws/projects/:projectId/archives/cycles` | `projects/:projectId/archives/cycles` (`ArchivedCyclesLayoutComponent`) › `''` | `…/archives/cycles/page.ts` → `ArchivedCyclesPageComponent` | Bootstrap wie 35 | I3 | CE-CYC-012, CE-LV-046 |
| 38 | `:ws/projects/:projectId/archives/modules` | `projects/:projectId/archives/modules` (`ArchivedModulesLayoutComponent`) › `''` | `…/archives/modules/page.ts` → `ArchivedModulesPageComponent` | Bootstrap wie 35 | I3 | CE-MOD-009, CE-LV-046 |
| – | (L `projects/(detail)/[projectId]/layout.tsx`) | `projects/:projectId` (`ProjectDetailLayoutComponent` = LPD) | – | Tab-Leiste bei `TABBED`; `ProjectAuthWrapper` | I0 (Kern) · I1 | CE-PRJ-006, CE-PRJ-007, CE-PRJ-014, CE-PRJ-015 |

**Block F – unter `projects/:projectId` (LPD):**

| # | React-Route | Angular-Eintrag (relativ) | Komponente (`…/projects/(detail)/[projectId]/…`) | Besonderheit | Ink. | CE-IDs |
|---|---|---|---|---|---|---|
| 24 | `…/issues` | `issues` (`ProjectIssuesListLayoutComponent`) › `''` (`pathMatch:'full'`) | `issues/(list)/page.ts` → `ProjectIssuesPageComponent` | Titel `${project} - Work items`; `ISSUES_STORE_TYPE = PROJECT` | I2 | CE-LV-001, CE-LV-002, CE-LV-005, CE-LV-017…, CE-WI-001 |
| 25 | `…/issues/:issueId` | `issues/:issueId` | `issues/(detail)/[issueId]/page.ts` → `LegacyIssueRedirectPageComponent` (EmptyState bei Fehler) | `canActivate: [legacyIssueRedirectGuard]` | I2 | CE-WI-009, CE-UIX-012 |
| 26 | `…/cycles/:cycleId` | `cycles/:cycleId` (`CycleDetailLayoutComponent`) › `''` | `cycles/(detail)/[cycleId]/page.ts` → `CycleDetailPageComponent` | `cycle_sidebar_collapsed` (JSON-Bool) | I3 | CE-CYC-007…-011, CE-LV-016 |
| 27 | `…/cycles` | `cycles` (`CycleListLayoutComponent`) › `''` (`pathMatch:'full'`) | `cycles/(list)/page.ts` → `CycleListPageComponent` | Disabled-Feature-Zustand (E1 korrigiert) | I3 | CE-CYC-001, CE-CYC-002, CE-CYC-005, CE-PRJ-020 |
| 28 | `…/modules/:moduleId` | `modules/:moduleId` (`ModuleDetailLayoutComponent`) › `''` | `modules/(detail)/[moduleId]/page.ts` → `ModuleDetailPageComponent` | `module_sidebar_collapsed` (JSON-String, E10) | I3 | CE-MOD-006, CE-MOD-007, CE-MOD-008 |
| 29 | `…/modules` | `modules` (`ModuleListLayoutComponent`) › `''` (`pathMatch:'full'`) | `modules/(list)/page.ts` → `ModuleListPageComponent` | Disabled-Feature | I3 | CE-MOD-001…-005, CE-PRJ-020 |
| 30 | `…/views/:viewId` | `views/:viewId` (`ProjectViewDetailLayoutComponent`) › `''` | `views/(detail)/[viewId]/page.ts` → `ProjectViewDetailPageComponent` | Key `VIEW_DETAILS_${viewId}` | I3 | CE-LV-051 |
| 31 | `…/views` | `views` (`ProjectViewListLayoutComponent`) › `''` (`pathMatch:'full'`) | `views/(list)/page.ts` → `ProjectViewListPageComponent` | Disabled-Feature | I3 | CE-LV-047…-050, CE-PRJ-020 |
| 32 | `…/pages/:pageId` | `pages/:pageId` (`PageDetailLayoutComponent`) › `''` | `pages/(detail)/[pageId]/page.ts` → `PageDetailPageComponent` | Key `PAGE_DETAILS_${pageId}` mit Fokus-/Reconnect-Revalidierung | I4 | CE-PAGE-004, CE-PAGE-013…-020, CE-RT-002…-004 |
| 33 | `…/pages?type=…` | `pages` (`PageListLayoutComponent`) › `''` (`pathMatch:'full'`) | `pages/(list)/page.ts` → `PageListPageComponent` | `type` fehlt/ungültig → `public` | I4 | CE-PAGE-001…-003, CE-PRJ-020 |
| 34 | `…/intake?currentTab&inboxIssueId` | `intake` (`IntakeLayoutComponent`) › `''` | `intake/page.ts` → `IntakePageComponent` | Disabled-Feature | I3 | CE-INT-001…-011, CE-PRJ-020 |

**Block G – unter `:workspaceSlug` › `''` (`SettingsLayoutComponent` = LSET):**

| # | React-Route | Angular-Eintrag (relativ) | Komponente (`(all)/[workspaceSlug]/(settings)/settings/…`) | Rechteprüfung | Ink. | CE-IDs |
|---|---|---|---|---|---|---|
| – | (L `settings/projects/layout.tsx`) | `settings/projects` (`ProjectSettingsRootLayoutComponent` = LPSET) | – | Redirect auf erstes joined Projekt | I1 | CE-PRJ-017 |
| 45 | `:ws/settings/projects` | › `''` (`pathMatch:'full'`) | `projects/page.ts` → `ProjectSettingsEmptyPageComponent` | – | I1 | CE-PRJ-017 |
| – | (L `settings/projects/[projectId]/layout.tsx`) | › `':projectId'` (`ProjectSettingsDetailLayoutComponent` = LPSETD) | – | `ProjectAuthWrapper`, Sidebar-Registry `SETTINGS_PAGES` (project) | I1 | CE-PRJ-017 |
| 46 | `…/:projectId` | ›› `''` (`pathMatch:'full'`) | `projects/[projectId]/page.ts` → `ProjectGeneralSettingsPageComponent` | Nicht-Admin `opacity-60` | I1 | CE-PRJ-018, CE-PRJ-008, CE-PRJ-009 |
| 47 | `…/members` | ›› `members` | `…/members/page.ts` → `ProjectMembersSettingsPageComponent` | PRJ Admin/Member oder WS-Admin | I1 | CE-PRJ-021, CE-PRJ-022 |
| 48 | `…/features/cycles` | ›› `features/cycles` | `…/features/cycles/page.ts` → `ProjectFeatureCyclesPageComponent` | PRJ Admin | I1 | CE-PRJ-019 |
| 49 | `…/features/modules` | ›› `features/modules` | `…/features/modules/page.ts` → `ProjectFeatureModulesPageComponent` | PRJ Admin | I1 | CE-PRJ-019 |
| 50 | `…/features/views` | ›› `features/views` | `…/features/views/page.ts` → `ProjectFeatureViewsPageComponent` | PRJ Admin | I1 | CE-PRJ-019 |
| 51 | `…/features/pages` | ›› `features/pages` | `…/features/pages/page.ts` → `ProjectFeaturePagesPageComponent` | PRJ Admin | I1 | CE-PRJ-019 |
| 52 | `…/features/intake` | ›› `features/intake` | `…/features/intake/page.ts` → `ProjectFeatureIntakePageComponent` | PRJ Admin | I1 | CE-PRJ-019 |
| 53 | `…/states` | ›› `states` | `…/states/page.ts` → `ProjectStatesSettingsPageComponent` | PRJ Admin/Member | I1 | CE-PRJ-023…-027 |
| 54 | `…/labels` | ›› `labels` | `…/labels/page.ts` → `ProjectLabelsSettingsPageComponent` (DnD + Auto-Scroll) | PRJ Admin/Member | I1 | CE-PRJ-028…-032 |
| 55 | `…/estimates` | ›› `estimates` | `…/estimates/page.ts` → `ProjectEstimatesSettingsPageComponent` | PRJ Admin | I1 | CE-PRJ-034…-038 |
| 56 | `…/automations` (L `automations/layout.tsx`) | ›› `automations` (`ProjectAutomationsLayoutComponent`) › `''` | `…/automations/page.ts` → `ProjectAutomationsSettingsPageComponent` | PRJ Admin | I3 | CE-PRJ-039, CE-PRJ-040 |
| – | (L `settings/(workspace)/layout.tsx`) | `settings` (`WorkspaceSettingsLayoutComponent` = LWSET) | – | `WORKSPACE_SETTINGS_ACCESS[pathnameToAccessKey]` → `NotAuthorizedView`; Sidebar-Registry `SETTINGS_PAGES` (workspace) | I1 | CE-WS-024 |
| 39 | `:ws/settings` | › `''` (`pathMatch:'full'`) | `(workspace)/page.ts` → `WorkspaceGeneralSettingsPageComponent` | Admin, Member | I1 | CE-WS-003, CE-WS-004 |
| 40 | `:ws/settings/members` | › `members` | `(workspace)/members/page.ts` → `WorkspaceMembersSettingsPageComponent` | Admin, Member | I1 | CE-WS-009, CE-WS-010 |
| 41 | `:ws/settings/billing` | **entfällt** (ADR-001; Redirect R1) | – | – | – | – |
| 42 | `:ws/settings/exports` | › `exports` | `(workspace)/exports/page.ts` → `WorkspaceExportsSettingsPageComponent` | Admin, Member | I6 | CE-EXP-001, CE-EXP-002 |
| 43 | `:ws/settings/webhooks` | › `webhooks` (`pathMatch:'full'`) | `(workspace)/webhooks/page.ts` → `WorkspaceWebhooksSettingsPageComponent` | Admin | I6 | CE-WH-002…-004, CE-WH-006 |
| 44 | `:ws/settings/webhooks/:webhookId` | › `webhooks/:webhookId` | `(workspace)/webhooks/[webhookId]/page.ts` → `WorkspaceWebhookDetailSettingsPageComponent` | Admin | I6 | CE-WH-005, CE-WH-006 |
| – | (`settings/(workspace)/integrations/page.tsx`, ohne Route, E2) | **nicht portiert** (ADR-007: GitHub/Slack entfallen; Forgejo-Einstellungen kommen mit F2/W1 über `SETTINGS_PAGES`) | – | – | – | – |

**Block H – Catch-all (letzte Route unter L0):**

| # | React-Route | Angular-Eintrag | Komponente | Ink. | CE-IDs |
|---|---|---|---|---|---|
| 69 | `*` | `**` | `not-found.page.ts` → `NotFoundPageComponent` | I0 | CE-UIX-010 |

**Reihenfolge-Regeln, die durch den Routing-Contract-Test (§7.2) abgesichert werden:** `/onboarding/` darf nie als Workspace-Slug „onboarding“ erkannt werden; `/ws/profile/u1/activity/` → Activity-Page; `/ws/projects/archives/` → Archiv-Projekte; `/ws/settings/projects/p1/` → LPSETD; `/settings/profile/general/` → LPROF; `/ws/projects/p1/archives/issues/` → Archiv-Layout ohne Tab-Leiste.

### 4.2 Routen `admin` (Base-Path `/god-mode/`)

| # (A11) | React-Route (`ADM/app/routes.ts`) | Angular-Eintrag | Komponente (`FE/apps/admin/src/pages/(all)/…`) | Guard / Zustände | Ink. | CE-IDs |
|---|---|---|---|---|---|---|
| R1 | index (L `(home)/layout.tsx`) | `''` (`HomeLayoutComponent`) › `''` (`pathMatch:'full'`) | `(home)/page.ts` → `AdminHomePageComponent`: Spinner → Instanzfehler → **Erst-Einrichtung ohne Admin-Konto** (`is_setup_done=false`, CE-INST-006 angepasst) → „Mit Keycloak anmelden“ (`/auth/oidc/login/?app=admin&next_path=/god-mode/general/`) bzw. Hinweis „keine Instanz-Admin-Rolle“ | eingeloggt **und** Admin-Rolle → `replace('/general/')` | I0 | CE-INST-006 (angepasst), CE-INST-007 (entfällt), CE-INST-009 |
| – | (L `(dashboard)/layout.tsx`) | `''` (`DashboardLayoutComponent`: Sidebar, Header mit Breadcrumb, `NewUserPopup`) | – | `isUserLoggedIn === false` → `replace('/')`; `undefined` → Spinner | I0 | CE-INST-010…-013 |
| R2 | `general` | › `general` | `(dashboard)/general/page.ts` → `GeneralSettingsPageComponent` | – | I0 | CE-INST-017, CE-INST-015 |
| R3 | `workspace` | › `workspace` (`pathMatch:'full'`) | `(dashboard)/workspace/page.ts` → `InstanceWorkspacesPageComponent` | Key `INSTANCE_WORKSPACES` | I6 | CE-INST-027, CE-INST-028 |
| R4 | `workspace/create` | › `workspace/create` | `(dashboard)/workspace/create/page.ts` → `InstanceWorkspaceCreatePageComponent` | – | I6 | CE-INST-029, CE-INST-030 |
| R5 | `email` | › `email` | `(dashboard)/email/page.ts` → `EmailSettingsPageComponent` (+ `TestEmailModal`) | Key `INSTANCE_CONFIGURATIONS` | I6 | CE-INST-018, CE-INST-019 |
| R6 | `authentication` | › `authentication` (`pathMatch:'full'`) | `(dashboard)/authentication/page.ts` → `AuthenticationStatusPageComponent` (nur Keycloak-Status: Issuer, Clients, Admin-Rolle, Link zur Keycloak-Admin-Konsole; keine Provider-Schalter) | – | I6 | CE-INST-020 (angepasst), CE-AUTH-013 (entfällt) |
| R7–R10 | `authentication/{github,gitlab,google,gitea}` | **entfallen** (ADR-008); Angular-Eintrag `authentication/:provider` → `redirectTo: '/authentication/'` | – | – | I6 | CE-INST-021…-024 (entfallen) |
| R11 | `ai` | › `ai` | `(dashboard)/ai/page.ts` → `AiSettingsPageComponent` | – | I6 | CE-INST-025 |
| R12 | `image` | › `image` | `(dashboard)/image/page.ts` → `ImageSettingsPageComponent` | – | I6 | CE-INST-026 |
| R13 | `*` | `**` | `components/404.component.ts` → `AdminNotFoundComponent` („Go to general settings“ → `/general/`) | – | I0 | CE-INST-016 |

Admin-Abmeldung (CE-INST-008, angepasst): Formular-POST `/auth/sign-out/?app=admin` (RP-initiated Logout, ADR-017); Unsaved-Changes-Dialog (CE-INST-014) als `canDeactivate` + `beforeunload`.

### 4.3 Routen `space` (Base-Path `/spaces/`)

| # (A11) | React-Route (`SPC/app/routes.ts`) | Angular-Eintrag | Komponente (`FE/apps/space/src/pages/…`) | Guard / Resolver | Ink. | CE-IDs |
|---|---|---|---|---|---|---|
| S1 | index | `''` (`pathMatch:'full'`) | `page.ts` → `SpaceHomePageComponent` (Spinner; eingeloggt + `next_path` → `replace`; eingeloggt → `UserLoggedIn`; sonst „Mit Keycloak anmelden“ `app=space`) | Gateway setzt `X-Frame-Options: SAMEORIGIN` nur für `/spaces/` | I6 | CE-SPACE-014, CE-SPACE-015, CE-SPACE-012 (angepasst), CE-SPACE-008…-011 (entfallen) |
| S2 | `:workspaceSlug/:projectId` | `':workspaceSlug/:projectId'` | `[workspaceSlug]/[projectId]/page.ts` → `SpaceLegacyRedirectPageComponent` (Spinner `h-screen min-h-[500px]`) | `canActivate: [spaceLegacyAnchorGuard]` → `UrlTree('/issues/{anchor}[?board&peekId]')` bzw. `'/404'` | I6 | CE-SPACE-016 |
| S3 | `issues/:anchor` (L `issues/[anchor]/layout.tsx`) | `issues/:anchor` (`AnchorLayoutComponent`) › `''` | `issues/[anchor]/page.ts` → `PublishedBoardPageComponent` | `resolve: { meta: anchorMetaResolver }` (nur `document.title`/`description`; OG-Tags liefert das Gateway, D08-ADR-26); Anchor-Regex `^[a-zA-Z0-9_-]+$` | I6 | CE-SPACE-017…-030, CE-SPACE-032 |
| S4 | `*` | `**` | `not-found.page.ts` → `SpaceNotFoundPageComponent` („That didn't work“, auch Ziel von `/404`) | – | I6 | CE-SPACE-031 |

### 4.4 Layouts und Wrapper (web)

| Kürzel | Original | Ziel (`FE/apps/web/src/pages/…`) | Klasse | Inhalt |
|---|---|---|---|---|
| L0 | `WEB/app/layout.tsx` | `layout.component.ts` | `AppShellLayoutComponent` | Container `relative flex h-screen w-full flex-col overflow-hidden bg-canvas desktop-app-container`, `StoreWrapper`, `InstanceWrapper`, Toast-Viewport |
| LH | `(home)/layout.tsx` | `(home)/layout.component.ts` | `HomeLayoutComponent` | Meta `index, nofollow` |
| LALL | `(all)/layout.tsx` | `(all)/layout.component.ts` | `AllLayoutComponent` | Meta `noindex, nofollow`; `PreloadResources` entfällt (leer) |
| LWS | `(all)/[workspaceSlug]/layout.tsx` | `(all)/[workspaceSlug]/layout.component.ts` | `WorkspaceLayoutComponent` | `AuthenticationWrapper` → `WorkspaceAuthWrapper` → AppRail (`isEnabled=false`) → `WorkspaceContentWrapper` (TopNavigation) → `GlobalModals` (lazy `ProfileSettingsModal`) |
| LPRJ | `(all)/[workspaceSlug]/(projects)/layout.tsx` | `…/(projects)/layout.component.ts` | `ProjectsAppLayoutComponent` | `ProjectsAppPowerKComponent`, `#full-screen-portal`, `ProjectAppSidebar` (resizable), `ExtendedProjectSidebar`, `<main>` |
| LPD | `…/projects/(detail)/[projectId]/layout.tsx` | `…/projects/(detail)/[projectId]/layout.component.ts` | `ProjectDetailLayoutComponent` | `TabNavigationRoot` bei `TABBED`, `ProjectAuthWrapper` |
| LSET | `…/(settings)/layout.tsx` | `…/(settings)/layout.component.ts` | `SettingsLayoutComponent` | `ProjectsAppPowerKComponent`, Rahmen, `ContentWrapper` |
| LWSET | `…/(settings)/settings/(workspace)/layout.tsx` | gleich | `WorkspaceSettingsLayoutComponent` | Mobile-Nav, `WorkspaceSettingsSidebarRoot`, Rechteprüfung |
| LPSET | `…/(settings)/settings/projects/layout.tsx` | gleich | `ProjectSettingsRootLayoutComponent` | Redirect erstes Projekt |
| LPSETD | `…/(settings)/settings/projects/[projectId]/layout.tsx` | gleich | `ProjectSettingsDetailLayoutComponent` | Mobile-Nav, `ProjectSettingsSidebarRoot`, `ProjectAuthWrapper` |
| LPROF | `(all)/settings/profile/layout.tsx` | gleich | `ProfileSettingsLayoutComponent` | `ProjectsAppPowerKComponent`, `AuthenticationWrapper`, Rahmen |
| HL:* | je Feature `layout.tsx` + `header.tsx` + `mobile-header.tsx` | gleicher Ordner | `<Feature>LayoutComponent`, `<Feature>HeaderComponent`, `<Feature>MobileHeaderComponent` | `AppHeader` (`h-11 border-b border-subtle bg-surface-1 z-[18]`) + `ContentWrapper` |
| Wrapper | `WEB/lib/wrappers/*.tsx`, `WEB/layouts/auth-layout/*.tsx` | `FE/libs/web/core/wrappers/*.component.ts` | `AuthenticationWrapperComponent`, `InstanceWrapperComponent`, `StoreWrapperComponent`, `WorkspaceAuthWrapperComponent`, `ProjectAuthWrapperComponent`, `ProjectBootstrapComponent` (neu, E5) | §3.3.4 |
| Default-Layout | `WEB/layouts/default-layout/index.tsx` | `FE/libs/web/core/layouts/default-layout.component.ts` | `DefaultLayoutComponent` | `h-screen w-full overflow-hidden bg-surface-1` (+ `gradient`) |

### 4.5 Store-Mapping `apps/web/store` (alle 100 Dateien)

Regeln: Klassenname bleibt; `@Injectable({providedIn:'root'})` nur für Stores, die im Original direkt vom `CoreRootStore` per `new` erzeugt werden („Root“); alle anderen sind plain classes („Kind“, erzeugt vom genannten Eltern-Store). `Base*`-Klassen bleiben als Basisklassen erhalten (EE-Erweiterungsmuster des Originals) und werden mit dem CE-Namen als DI-Token registriert (`{provide: CommandPaletteStore, useClass: CommandPaletteStore}`, §6.3). Spalte „Hinweise“ nennt die Abbildung der MobX-Felder nach §3.4.2 und Abweichungen.

| # | Original (`WEB/store/…`) | Klasse(n) | Ziel (`FE/libs/web/…`) | Art | Hinweise | Ink. |
|---|---|---|---|---|---|---|
| 1 | `root.store.ts` | `CoreRootStore` (exportiert als `RootStore`) | `core/state/root.store.ts` | Root | Fassade + `resetOnSignOut()` (D08-ADR-06/07) | I0 |
| 2 | `router.store.ts` | `RouterStore` | `core/state/router.store.ts` | Root | `query` = `signal`; 14 Computeds | I0 |
| 3 | `base-command-palette.store.ts` | `BaseCommandPaletteStore`, `CommandPaletteStore` | `core/state/base-command-palette.store.ts` | Root | 13 Modal-Flags als `signal`, `projectListOpenMap` als `EntityMap<boolean>`, `isAnyModalOpen` `computed` | I0 |
| 4 | `base-power-k.store.ts` | `BasePowerKStore` (als `PowerKStore`) | `core/state/base-power-k.store.ts` | Root | `commandRegistry` = Instanz `PowerKCommandRegistry` aus `power-k/core` (über Token `POWER_K_REGISTRY` in `core`, um `core → power-k` zu vermeiden); `topNavInputRef` = `signal<HTMLElement \| null>` | I0 (Store) / I5 |
| 5 | `instance.store.ts` | `InstanceStore` | `core/state/instance.store.ts` | Root | `isLoading, instance, config, error` als `signal` | I0 |
| 6 | `theme.store.ts` | `ThemeStore` | `core/state/theme.store.ts` | Root | 11 Panel-Flags als `signal`, `toggle*` schreiben `localStorage` wie Original (E14) | I0 |
| 7 | `multiple_select.store.ts` | `MultipleSelectStore` | `core/state/multiple_select.store.ts` | Root | `selectedEntityDetails` als `signal<TEntityDetails[]>`; `memoizedComputed` für `getIsEntitySelected` | I2 |
| 8 | `editor/asset.store.ts` | `EditorAssetStore` | `core/state/editor/asset.store.ts` | Root | `assetsUploadPercentage` als `EntityMap<number>` | I2 |
| 9 | `user/index.ts` | `UserStore` | `core/state/user/index.ts` | Root | `canPerformAnyCreateAction`, `projectsWithCreatePermissions` `computed`; `handleSetPassword`, `changePassword` **entfallen** (ADR-008); `signOut` = Formular-POST + `resetOnSignOut` | I0 |
| 10 | `user/profile.store.ts` | `ProfileStore` | `core/state/user/profile.store.ts` | Kind von `UserStore` | `updateUserTheme`, `updateUserProfile` optimistisch + Rollback; `setLanguage` nach Fetch | I0 |
| 11 | `user/settings.store.ts` | `UserSettingsStore` | `core/state/user/settings.store.ts` | Kind | `fetchCurrentUserSettings(bustCache)` (`?t=`) | I0 |
| 12 | `user/base-permissions.store.ts` | `BaseUserPermissionStore` | `core/state/user/base-permissions.store.ts` | Kind | `workspaceUserInfo`, `projectUserInfo`, `workspaceProjectsPermissions` als `DeepState`; `allowPermissions` unverändert (inkl. `parseInt`, `onAllowed`), hinter `PermissionService` (§6) | I0 |
| 13 | `user/account.store.ts` | `AccountStore` | – | – | **entfällt** (verknüpfte OAuth-Konten, CE-PROF-007, ADR-008) | – |
| 14 | `member/index.ts` | `MemberRootStore` | `core/state/member/index.ts` | Root | `memberMap` `EntityMap<IUserLite>`; Kinder per `injectLazy` (§3.4.4) | I0 |
| 15 | `member/utils.ts` | – (Funktionen) | `core/state/member/utils.ts` | – | Kopie | I0 |
| 16 | `member/workspace/workspace-member.store.ts` | `WorkspaceMemberStore` | `workspace/state/member/workspace/workspace-member.store.ts` | Kind von `MemberRootStore` | `workspaceMemberMap` `DeepState`, `memoizedComputed` für `getWorkspaceMemberIds` u. a. | I0 (Liste) / I1 |
| 17 | `member/workspace/workspace-member-filters.store.ts` | `WorkspaceMemberFiltersStore` | `workspace/state/member/workspace/workspace-member-filters.store.ts` | Kind | – | I1 |
| 18 | `member/project/base-project-member.store.ts` | `BaseProjectMemberStore` | `project/state/member/project/base-project-member.store.ts` | Kind von `MemberRootStore` | `projectMemberMap`, `projectUserPropertiesMap` `DeepState` | I0 (Kern) / I1 |
| 19 | `member/project/project-member-filters.store.ts` | `ProjectMemberFiltersStore` | `project/state/member/project/project-member-filters.store.ts` | Kind | – | I1 |
| 20 | `workspace/index.ts` | `BaseWorkspaceRootStore` (`WorkspaceRootStore`) | `workspace/state/workspace/index.ts` | Root | `workspaces` `EntityMap<IWorkspace>`, `currentWorkspace` `computed`; `updateProjectNavigationPreferences` optimistisch + Revert | I0 |
| 21 | `workspace/webhook.store.ts` | `WebhookStore` | `settings/state/workspace/webhook.store.ts` | Kind von `WorkspaceRootStore` (`webhook`, per `injectLazy`) | – | I6 |
| 22 | `workspace/api-token.store.ts` | `ApiTokenStore` | `settings/state/workspace/api-token.store.ts` | Kind (`apiToken`) | Service aus `@plane/services` | I6 |
| 23 | `workspace/home.ts` | `HomeStore` | `home/state/workspace/home.ts` | Kind (`home`) | `widgetsMap` `EntityMap`, `orderedWidgets` `computed`, `reorderWidget` | I5 |
| 24 | `workspace/link.store.ts` | `WorkspaceLinkStore` | `home/state/workspace/link.store.ts` | Kind von `HomeStore` (`quickLinks`) | – | I5 |
| 25 | `project/index.ts` | `ProjectRootStore` | `project/state/project/index.ts` | Root | Kinder `project`, `projectFilter`, `publish` (letzteres per `injectLazy`) | I0 |
| 26 | `project/project.store.ts` | `ProjectStore` | `project/state/project/project.store.ts` | Kind | `projectMap` `EntityMap<TProject>`; `filteredProjectIds`, `joinedProjectIds` … `computed`; `updateProjectView` optimistisch | I0 (Kern) / I1 |
| 27 | `project/project_filter.store.ts` | `ProjectFilterStore` | `project/state/project/project_filter.store.ts` | Kind | `reaction` auf Workspace-Wechsel → `reactionEffect` | I1 |
| 28 | `project/project-publish.store.ts` | `ProjectPublishStore` | `project-publish/state/project/project-publish.store.ts` | Kind | – | I6 |
| 29 | `cycle.store.ts` | `CycleStore` | `cycles/state/cycle.store.ts` | Root | Skelett 01 §6.5; `fetchActiveCycleProgressPro` bleibt (A08 §2.16) | I2 (Lesen) / I3 |
| 30 | `cycle_filter.store.ts` | `CycleFilterStore` | `cycles/state/cycle_filter.store.ts` | Root | `reaction` auf `router.projectId` | I3 |
| 31 | `module.store.ts` | `ModulesStore` | `modules/state/module.store.ts` | Root | – | I2 (Lesen) / I3 |
| 32 | `module_filter.store.ts` | `ModuleFilterStore` | `modules/state/module_filter.store.ts` | Root | `persisted('module_display_filters')`, `persisted('module_filters')` debounced | I3 |
| 33 | `project-view.store.ts` | `ProjectViewStore` | `views/state/project-view.store.ts` | Root | – | I3 |
| 34 | `global-view.store.ts` | `GlobalViewStore` | `views/state/global-view.store.ts` | Root | – | I3 |
| 35 | `state.store.ts` | `StateStore` | `project/state/state.store.ts` | Root | Zugriff künftig über `IStateCatalog`-Fassade (A17, §6) | I1 |
| 36 | `label.store.ts` | `LabelStore` | `project/state/label.store.ts` | Root | `projectLabelsTree` `computed`; Fassade `ILabelCatalog` (A17) | I1 |
| 37 | `dashboard.store.ts` | `DashboardStore` | – | – | **nicht portieren** (toter Code, E18) | – |
| 38 | `analytics.store.ts` | `BaseAnalyticsStore` (`AnalyticsStore`) | `analytics/state/analytics.store.ts` | Root | bleibt bei `resetOnSignOut` erhalten (wie Original) | I5 |
| 39 | `pages/project-page.store.ts` | `ProjectPageStore` | `pages/state/pages/project-page.store.ts` | Root | `data` `EntityMap<ProjectPage>` | I4 |
| 40 | `pages/base-page.ts` | `BasePage` | `pages/state/pages/base-page.ts` | Kind | Titel-`reaction` 2 s → `reactionEffect`; **E9 korrigiert** (`update` sendet Nachher-Daten, FE-E9) | I4 |
| 41 | `pages/project-page.ts` | `ProjectPage` | `pages/state/pages/project-page.ts` | Kind | 10 Rechte-Computeds 1:1 | I4 |
| 42 | `pages/extended-base-page.ts` | `ExtendedBasePage` | `pages/state/pages/extended-base-page.ts` | Kind | `asJSONExtended → {}` (D1/D2-Andockstelle) | I4 |
| 43 | `pages/page-editor-info.ts` | `PageEditorInstance` | `pages/state/pages/page-editor-info.ts` | Kind | – | I4 |
| 44 | `inbox/project-inbox.store.ts` | `ProjectInboxStore` | `intake/state/inbox/project-inbox.store.ts` | Root | `PER_PAGE_COUNT=10` | I3 |
| 45 | `inbox/inbox-issue.store.ts` | `InboxIssueStore` | `intake/state/inbox/inbox-issue.store.ts` | Kind | State-Wechsel über C1-Pipeline nur serverseitig (keine Frontend-Änderung) | I3 |
| 46 | `estimates/project-estimate.store.ts` | `ProjectEstimateStore` | `project/state/estimates/project-estimate.store.ts` | Root | – | I1 |
| 47 | `estimates/estimate.ts` | `Estimate` | `project/state/estimates/estimate.ts` | Kind | `creteEstimatePoint` (Tippfehler bleibt) | I1 |
| 48 | `estimates/estimate-point.ts` | `EstimatePoint` | `project/state/estimates/estimate-point.ts` | Kind | – | I1 |
| 49 | `notifications/workspace-notifications.store.ts` | `WorkspaceNotificationStore` | `notifications/state/notifications/workspace-notifications.store.ts` | Root | `setUnreadNotificationsCount` zusätzlich aus `LIVE_EVENT_HANDLERS` (I5) | I5 |
| 50 | `notifications/notification.ts` | `Notification` | `notifications/state/notifications/notification.ts` | Kind | – | I5 |
| 51 | `favorite.store.ts` | `FavoriteStore` | `favorites/state/favorite.store.ts` | Root | `reOrderFavorite` optimistisch | I1 |
| 52 | `sticky/sticky.store.ts` | `StickyStore` | `stickies/state/sticky/sticky.store.ts` | Root | `STICKIES_PER_PAGE=30` | I5 |
| 53 | `timeline/timeline.store.ts` | `TimeLineStore` | `work-items/state/timeline/timeline.store.ts` | Root | erzeugt Kinder 54–56 | I2 |
| 54 | `timeline/base-timeline.store.ts` | `BaseTimeLineStore` | `work-items/state/timeline/base-timeline.store.ts` | Basis | `isDependencyEnabled = false` (A9-Andockstelle) | I2 |
| 55 | `timeline/issues-timeline.store.ts` | `IssuesTimeLineStore` | `work-items/state/timeline/issues-timeline.store.ts` | Kind | `autorun` → `effect({injector})` | I2 |
| 56 | `timeline/modules-timeline.store.ts` | `ModulesTimeLineStore` | `work-items/state/timeline/modules-timeline.store.ts` | Kind | – | I3 |
| 57 | `issue/root.store.ts` | `IssueRootStore` | `work-items/state/issue/root.store.ts` | Root | gespiegelte Router-IDs und Maps als `computed` (statt `autorun`); erzeugt 58–96; `teamIssues`, `teamViewIssues`, `teamProjectWorkItems`, `projectEpics`, `epicDetail` bleiben als Felder (B1/Epics-Andockstelle) | I2 |
| 58 | `issue/issue.store.ts` | `IssueStore` | `work-items/state/issue/issue.store.ts` | Kind (`issues`) | `issuesMap` `EntityMap<TIssue>`, `issuesIdentifierMap` `EntityMap<string>` | I2 |
| 59 | `issue/helpers/base-issues.store.ts` | `BaseIssuesStore` | `work-items/state/issue/helpers/base-issues.store.ts` | Basis | §3.4.6 | I2 |
| 60 | `issue/helpers/base-issues-utils.ts` | – | `shared/work-items-core/src/base-issues-utils.ts` | – | Kopie | I2 |
| 61 | `issue/helpers/issue-filter-helper.store.ts` | `IssueFilterHelperStore` | `work-items/state/issue/helpers/issue-filter-helper.store.ts` | Basis | E20 korrigiert | I2 |
| 62 | `issue/project/issue.store.ts` | `ProjectIssues` | `work-items/state/issue/project/issue.store.ts` | Kind | – | I2 |
| 63 | `issue/project/filter.store.ts` | `ProjectIssuesFilter` | `work-items/state/issue/project/filter.store.ts` | Kind | Persistenz `PATCH …/user-properties/` | I2 |
| 64 | `issue/project/index.ts` | – | `work-items/state/issue/project/index.ts` | – | Barrel | I2 |
| 65 | `issue/cycle/issue.store.ts` | `CycleIssues` | `work-items/state/issue/cycle/issue.store.ts` | Kind | `fetchActiveCycleProgressPro` bei `cycle_sidebar_collapsed === false` | I3 |
| 66 | `issue/cycle/filter.store.ts` | `CycleIssuesFilter` | `work-items/state/issue/cycle/filter.store.ts` | Kind | – | I3 |
| 67 | `issue/cycle/index.ts` | – | `work-items/state/issue/cycle/index.ts` | – | Barrel | I3 |
| 68 | `issue/module/issue.store.ts` | `ModuleIssues` | `work-items/state/issue/module/issue.store.ts` | Kind | – | I3 |
| 69 | `issue/module/filter.store.ts` | `ModuleIssuesFilter` | `work-items/state/issue/module/filter.store.ts` | Kind | – | I3 |
| 70 | `issue/module/index.ts` | – | `work-items/state/issue/module/index.ts` | – | Barrel | I3 |
| 71 | `issue/project-views/issue.store.ts` | `ProjectViewIssues` | `work-items/state/issue/project-views/issue.store.ts` | Kind | – | I3 |
| 72 | `issue/project-views/filter.store.ts` | `ProjectViewIssuesFilter` | `work-items/state/issue/project-views/filter.store.ts` | Kind | **E7 korrigiert** (`projectViewIssues.clear(true)`, FE-E7) | I3 |
| 73 | `issue/project-views/index.ts` | – | `work-items/state/issue/project-views/index.ts` | – | Barrel | I3 |
| 74 | `issue/archived/issue.store.ts` | `ArchivedIssues` | `work-items/state/issue/archived/issue.store.ts` | Kind | `restoreIssue` | I3 |
| 75 | `issue/archived/filter.store.ts` | `ArchivedIssuesFilter` | `work-items/state/issue/archived/filter.store.ts` | Kind | `issue_local_filters` (`ARCHIVED`) | I3 |
| 76 | `issue/archived/index.ts` | – | `work-items/state/issue/archived/index.ts` | – | Barrel | I3 |
| 77 | `issue/profile/issue.store.ts` | `ProfileIssues` | `work-items/state/issue/profile/issue.store.ts` | Kind | – | I5 |
| 78 | `issue/profile/filter.store.ts` | `ProfileIssuesFilter` | `work-items/state/issue/profile/filter.store.ts` | Kind | – | I5 |
| 79 | `issue/profile/index.ts` | – | `work-items/state/issue/profile/index.ts` | – | Barrel | I5 |
| 80 | `issue/workspace/issue.store.ts` | `WorkspaceIssues` | `work-items/state/issue/workspace/issue.store.ts` | Kind | – | I3 |
| 81 | `issue/workspace/filter.store.ts` | `WorkspaceIssuesFilter` | `work-items/state/issue/workspace/filter.store.ts` | Kind | Static Views (A08 §2.6.3) | I3 |
| 82 | `issue/workspace/index.ts` | – | `work-items/state/issue/workspace/index.ts` | – | Barrel | I3 |
| 83 | `issue/workspace-draft/issue.store.ts` | `WorkspaceDraftIssues` | `work-items/state/issue/workspace-draft/issue.store.ts` | Kind | – | I2 |
| 84 | `issue/workspace-draft/filter.store.ts` | `WorkspaceDraftIssuesFilter` | `work-items/state/issue/workspace-draft/filter.store.ts` | Kind | **E8 korrigiert** (Key `WORKSPACE_DRAFT`, Refetch Drafts, FE-E8) | I2 |
| 85 | `issue/workspace-draft/index.ts` | – | `work-items/state/issue/workspace-draft/index.ts` | – | Barrel | I2 |
| 86 | `issue/issue_kanban_view.store.ts` | `IssueKanBanViewStore` | `work-items/state/issue/issue_kanban_view.store.ts` | Kind | `canUserDragDropVertically/Horizontally` = `false` bleibt | I2 |
| 87 | `issue/issue_calendar_view.store.ts` | `CalendarStore` | `work-items/state/issue/issue_calendar_view.store.ts` | Kind | – | I2 |
| 88 | `issue/issue_gantt_view.store.ts` | `GanttStore` | – | – | **nicht portieren** (E18) | – |
| 89 | `issue/issue-details/root.store.ts` | `IssueDetail` | `work-items/state/issue/issue-details/root.store.ts` | Kind (2 Instanzen) | `peekIssue`, Modal-Flags als `signal` | I2 |
| 90 | `issue/issue-details/issue.store.ts` | `IssueStore` (Detail) | `work-items/state/issue/issue-details/issue.store.ts` | Kind | E24 beibehalten (harmlos) | I2 |
| 91 | `issue/issue-details/activity.store.ts` | `IssueActivityStore` | `work-items/state/issue/issue-details/activity.store.ts` | Kind | Activity-Typen über `ACTIVITY_RENDERERS` erweiterbar (§6) | I2 |
| 92 | `issue/issue-details/attachment.store.ts` | `IssueAttachmentStore` | `work-items/state/issue/issue-details/attachment.store.ts` | Kind | Upload-Fortschritt `EntityMap<number>` | I2 |
| 93 | `issue/issue-details/comment.store.ts` | `IssueCommentStore` | `work-items/state/issue/issue-details/comment.store.ts` | Kind | – | I2 |
| 94 | `issue/issue-details/comment_reaction.store.ts` | `IssueCommentReactionStore` | `work-items/state/issue/issue-details/comment_reaction.store.ts` | Kind | – | I2 |
| 95 | `issue/issue-details/link.store.ts` | `IssueLinkStore` | `work-items/state/issue/issue-details/link.store.ts` | Kind | – | I2 |
| 96 | `issue/issue-details/reaction.store.ts` | `IssueReactionStore` | `work-items/state/issue/issue-details/reaction.store.ts` | Kind | – | I2 |
| 97 | `issue/issue-details/relation.store.ts` | `IssueRelationStore` | `work-items/state/issue/issue-details/relation.store.ts` | Kind | Relationstypen aus `RELATION_TYPES`-Registry (A9, §6) | I2 |
| 98 | `issue/issue-details/sub_issues.store.ts` | `IssueSubIssuesStore` | `work-items/state/issue/issue-details/sub_issues.store.ts` | Kind | – | I2 |
| 99 | `issue/issue-details/sub_issues_filter.store.ts` | `WorkItemSubIssueFiltersStore` | `work-items/state/issue/issue-details/sub_issues_filter.store.ts` | Kind | – | I2 |
| 100 | `issue/issue-details/subscription.store.ts` | `IssueSubscriptionStore` | `work-items/state/issue/issue-details/subscription.store.ts` | Kind | – | I2 |

### 4.6 Store-Mapping `apps/admin/store`, `apps/space/store`, `packages/shared-state`

| Original | Klasse | Ziel (`FE/libs/…`) | Hinweise | Ink. |
|---|---|---|---|---|
| `ADM/store/root.store.ts` | `RootStore` | `admin/core/state/root.store.ts` | `hydrate` entfällt (kein SSR); `resetOnSignOut` wie web | I0 |
| `ADM/store/instance.store.ts` | `InstanceStore` | `admin/core/state/instance.store.ts` | `config` wird **Signal** (Original nicht observable – kein sichtbarer Unterschied, da nur einmal gesetzt); Bug `updateInstanceInfo` (`instance.instance`) **korrigiert** (FE-A1); `disableEmail` mit Rethrow korrigiert (FE-A2) | I0/I6 |
| `ADM/store/theme.store.ts` | `ThemeStore` | `admin/core/state/theme.store.ts` | `god_mode_sidebar_collapsed` (String) | I0 |
| `ADM/store/user.store.ts` | `UserStore` | `admin/core/state/user.store.ts` | `fetchCurrentUser` → `GET /api/instances/admins/me/` (Session aus Keycloak-Login); 403 → `isUserLoggedIn=false` + Status `NO_ADMIN_ROLE` (neu, für Hinweis auf Home) | I0 |
| `ADM/store/workspace.store.ts` | `WorkspaceStore` | `admin/workspace/state/workspace.store.ts` | Pagination wie Original | I6 |
| `SPC/store/root.store.ts` | `RootStore` | `space/core/state/root.store.ts` | `hydrate` entfällt | I6 |
| `SPC/store/instance.store.ts` | `InstanceStore` | `space/core/state/instance.store.ts` | – | I6 |
| `SPC/store/user.store.ts` | `UserStore` | `space/core/state/user.store.ts` | `currentActor` `computed` | I6 |
| `SPC/store/profile.store.ts` | `ProfileStore` | `space/core/state/profile.store.ts` | – | I6 |
| `SPC/store/publish/publish_list.store.ts` | `PublishListStore` | `space/core/state/publish/publish_list.store.ts` | `publishMap` `EntityMap<PublishStore>` | I6 |
| `SPC/store/publish/publish.store.ts` | `PublishStore` | `space/core/state/publish/publish.store.ts` | plain class | I6 |
| `SPC/store/issue-filters.store.ts` | `IssueFilterStore` | `space/issues/state/issue-filters.store.ts` | – | I6 |
| `SPC/store/issue.store.ts` | `IssueStore` | `space/issues/state/issue.store.ts` | extends Space-`BaseIssuesStore` | I6 |
| `SPC/store/helpers/base-issues.store.ts` | `BaseIssuesStore` (Space) | `space/issues/state/helpers/base-issues.store.ts` | eigene, kleinere Variante des Originals – **nicht** mit Web-Variante zusammenführen (Parität) | I6 |
| `SPC/store/helpers/filter.helpers.ts` | – | `space/issues/state/helpers/filter.helpers.ts` | Kopie | I6 |
| `SPC/store/issue-detail.store.ts` | `IssueDetailStore` | `space/issues/state/issue-detail.store.ts` | optimistische Reaktionen/Votes 1:1; Kommentieren nur mit Keycloak-Login (ADR-008) | I6 |
| `SPC/store/state.store.ts` | `StateStore` | `space/issues/state/state.store.ts` | – | I6 |
| `SPC/store/label.store.ts` | `LabelStore` | `space/issues/state/label.store.ts` | – | I6 |
| `SPC/store/members.store.ts` | `MemberStore` | `space/issues/state/members.store.ts` | im Original nie aufgerufen – portieren (klein, API vorhanden), aber nicht aufrufen | I6 |
| `SPC/store/module.store.ts` | `ModuleStore` | `space/issues/state/module.store.ts` | wie oben | I6 |
| `SPC/store/cycle.store.ts` | `CycleStore` | `space/issues/state/cycle.store.ts` | wie oben | I6 |
| `PKG/shared-state/src/store/rich-filters/filter.ts` | `FilterInstance` | `shared/shared-state/src/store/rich-filters/filter.ts` | Ausdrucksformat `TWorkItemFilterExpression` unverändert (B6-Andockstelle) | I2 |
| `…/rich-filters/config-manager.ts` | `FilterConfigManager` | gleich | Operator-Konfig über `FILTER_OPERATORS`-Registry erweiterbar (§6) | I2 |
| `…/rich-filters/config.ts` | `FilterConfig` | gleich | – | I2 |
| `…/rich-filters/filter-helpers.ts` | `FilterInstanceHelper` | gleich | – | I2 |
| `…/rich-filters/adapter.ts` | `FilterAdapter` | gleich | – | I2 |
| `…/rich-filters/index.ts`, `store/index.ts`, `src/index.ts` | – | gleich | Barrels | I2 |
| `…/work-item-filters/filter.store.ts` | `WorkItemFilterStore` | gleich, `@Injectable` Root | `filters: Map` → `EntityMap<FilterInstance>` | I2 |
| `…/work-item-filters/adapter.ts`, `shared.ts`, `index.ts` | – | gleich | – | I2 |
| `PKG/shared-state/src/utils/{rich-filter.helper,work-item-filters.helper,index}.ts` | – | gleich | Kopie | I2 |
| `PKG/shared-state/src/store/user.store.ts`, `workspace.store.ts` | `UserStore`, `WorkspaceStore` | – | **nicht portieren** (ungenutzt) | – |

### 4.7 Hooks-Mapping (`WEB/hooks`)

| Original | Ziel | Art |
|---|---|---|
| alle Store-Hooks `hooks/store/*` (Dateien `use-analytics`, `use-app-theme`, `use-calendar-view`, `use-command-palette`, `use-cycle-filter`, `use-cycle`, `use-editor-asset`, `use-favorite`, `use-global-view`, `use-home`, `use-inbox-issues`, `use-instance`, `use-issue-detail`, `use-issues`, `use-kanban-view`, `use-label`, `use-member`, `use-module-filter`, `use-module`, `use-multiple-select-store`, `use-page-store`, `use-page`, `use-power-k`, `use-project-filter`, `use-project-inbox`, `use-project-publish`, `use-project-state`, `use-project-view`, `use-project`, `use-router-params`, `use-webhook`, `use-workspace`, `user/{user-user,user-user-profile,user-user-settings,user-permissions}`, `estimates/{use-project-estimate,use-estimate,use-estimate-point}`, `notifications/{use-workspace-notifications,use-notification}`, `work-item-filters/{use-work-item-filters,use-work-item-filter-instance}`, `workspace-draft/{use-workspace-draft-issue,use-workspace-draft-issue-filters}`) sowie `use-stickies.tsx` | `inject(<Store>)` bzw. Instanz-Getter (`inject(ProjectPageStore).getPageById(id)`) | – |
| `useDashboard` | – | entfällt (E18) |
| `use-app-router.tsx` | `AppRouter` | Service |
| `use-auto-save.tsx` | `AutoSaveService` (30 s, Ctrl/Cmd+S, 500 ms Debounce) | Service je Komponente (`providers`) |
| `use-auto-scroller.tsx` | `[plAutoScroller]` | Direktive |
| `use-bulk-operation-status.ts` | `BULK_OPERATIONS_ENABLED` Token (CE `false`) | Token (§6) |
| `use-collaborative-page-actions.tsx`, `use-realtime-page-events.tsx`, `use-page-fallback.ts` | `CollaborativePageActionsService`, `RealtimePageEventsService`, `PageFallbackService` | Services |
| `use-current-time.tsx` | `currentTime()` Signal (60 s) | Signal-Funktion |
| `use-debounce.tsx` | `debouncedSignal(src, ms)` (`state-kit`) | Signal-Funktion |
| `use-debounced-duplicate-issues.tsx` | Token `DUPLICATE_DETECTION` (CE: liefert `[]`) | Token (§6, G1) |
| `use-editor-flagging.ts` | Token `EDITOR_FLAGS` (CE: `disabled: ["ai","collaboration-cursor"]` – „collaboration-cursor“ wird in CE aktiviert, wenn S1 Awareness grün; ADR-001) | Token |
| `use-expandable-search.ts` | `[plExpandableSearch]` | Direktive |
| `use-extended-sidebar-overview-outside-click.tsx`, `use-peek-overview-outside-click.tsx` | `[plOutsideClick]` mit Ausnahme-Selektoren | Direktive (`@plane/cdk`) |
| `use-favorite-item-details.tsx`, `use-additional-favorite-item-details.tsx` | `FavoriteItemDetailsService` + Registry `FAVORITE_ENTITY_RENDERERS` | Service + Token (§6) |
| `use-file-size.ts` | `fileSizeLimit()` computed aus `InstanceStore` | Signal |
| `use-group-dragndrop.ts` | `GroupDragDropService` | Service |
| `use-integration-popup.tsx` | – | entfällt (GitHub/Slack, ADR-007); Forgejo-OAuth in F2 |
| `use-intersection-observer.ts` | `[plIntersection]` | Direktive |
| `use-issue-layout-store.ts` | `ISSUES_STORE_TYPE`, `injectIssueStoreType()`, `injectIssuesStore()` | Token + Funktionen |
| `use-issue-peek-overview-redirection.tsx` | `IssuePeekRedirectionService` | Service |
| `use-issue-properties.tsx` | Token `WORK_ITEM_PROPERTIES_LOADER` (CE no-op) | Token (§6, A1) |
| `use-issues-actions.tsx` | `injectIssuesActions(storeType)` | Funktion |
| `use-keypress.tsx` | `[plKeypress]` / `KeypressService` | Direktive |
| `use-local-storage.tsx` | `LocalStorageService`, `persisted()` | Service |
| `use-multiple-select.ts` | `MultipleSelectService` | Service |
| `use-navigation-preferences.ts` | `NavigationPreferencesService` (4 Teilfunktionen gleichen Namens) | Service |
| `use-notification-preview.tsx` | `NotificationPreviewService` | Service |
| `use-online-status.ts` | `onlineStatus()` Signal | Signal |
| `use-page-filters.ts` | `PageFiltersService` (`pages_config`) | Service |
| `use-page-flag.ts` | Token `PAGE_FLAGS` (CE: `isMovePageEnabled:false, isPageSharingEnabled:false`) | Token (§6, D2/D8) |
| `use-page-operations.ts` | `PageOperationsService` | Service |
| `use-parse-editor-content.ts` | `parseEditorContent()` (reine Funktion) | Funktion |
| `use-platform-os.tsx` | `PlatformService` (`isMobile`, `platform`) | Service |
| `use-project-issue-properties.ts`, `use-workspace-issue-properties.ts` | `ProjectIssuePropertiesService`, `WorkspaceIssuePropertiesService` (+ Token `WORKSPACE_ISSUE_PROPERTIES_EXTENDED`, CE no-op) | Services |
| `use-query-params.ts` | `updateQueryParams()` (Funktion) | Funktion |
| `use-reload-confirmation.tsx` | `ReloadConfirmationService` | Service |
| `use-table-keyboard-navigation.tsx` | `[plTableKeyboardNavigation]` | Direktive |
| `use-timeline-chart.ts` | `inject(TimeLineStore).get(type)` | – |
| `use-timer.tsx` | `countdown(seconds)` Signal | Signal |
| `use-timezone-converter.tsx`, `use-timezone.tsx` | `TimezoneConverterService`, `TimezoneService` (Key `TIMEZONES_LIST`) | Services |
| `use-window-size.tsx` | `windowSize()` Signal | Signal |
| `use-workspace-invitation.tsx` | `WorkspaceInvitationFormService` | Service |
| `use-workspace-paths.ts` | `WorkspacePathsService` (`isSettingsPath`, `isWikiPath`, `isAiPath`, `isProjectsPath`, `isNotificationsPath`) | Service |
| `context/use-issue-modal.tsx` | `ISSUE_MODAL_CONTEXT` Token + `IssueModalContext`-Klasse (Stubs aus A09 §5.4 als CE-Default) | Token (§6, A1) |
| `editor/use-editor-config.ts`, `editor/use-editor-mention.tsx`, `editor/use-extended-editor-config.ts`, `pages/use-extended-editor-extensions.ts`, `pages/use-pages-pane-extensions.ts`, `use-additional-editor-mention.tsx` | `EditorConfigService`, `EditorMentionService`, Tokens `EDITOR_EXTENSIONS`, `PAGE_PANE_EXTENSIONS`, `EDITOR_MENTION_TYPES` (CE-Defaults) | Services + Tokens (§6) |
| `oauth/core.tsx`, `oauth/extended.tsx`, `oauth/index.ts` | – | entfallen (ADR-008) |
| `rich-filters/use-filters-operator-configs.ts` | Token `FILTER_OPERATORS` (CE: `CORE_OPERATORS`, `allowNegative:false`) | Token (§6, B6) |
| `work-item-filters/use-work-item-filters-config.tsx` | `WorkItemFiltersConfigService` + `FILTER_FIELDS` | Service + Token |

### 4.8 Library-Mapping (jede Abhängigkeit aus `apps/*/package.json`, `packages/*/package.json`, Root-`package.json`)

Versionen des Originals aus `pnpm-workspace.yaml` (Catalog). „Nutzung“ = Paket(e), die es deklarieren (`W` web, `A` admin, `S` space, `L` live, `B` blocks, `E` editor, `U` utils, `SV` services, `SS` shared-state, `I` i18n, `H` hooks, `C` constants, `T` types, `TC` tailwind-config, `LG` logger, `D` decorators, `CM` codemods, `R` Root). Lizenzen der Zielpakete gemäß 01 §8.2; neue Pakete sind mit Lizenz angegeben.

#### 4.8.1 Laufzeit-Abhängigkeiten der Frontends und Pakete

| Original-Paket (Version) | Nutzung | Ziel | Art |
|---|---|---|---|
| `react`, `react-dom` (19.2.8) | W, A, S, B, E, H, I, U (peer T) | `@angular/core`, `@angular/common`, `@angular/platform-browser` 22.x | ersetzt |
| `react-router` (8.3.0) | W, A, S | `@angular/router` 22.x | ersetzt |
| `@react-router/node`, `@react-router/serve` (8.3.0) | W, A / S | – (Gateway liefert statisch aus) | entfällt |
| `isbot` (^5.1.31) | W, A, S | – (nur SSR-Entry, im Quelltext ungenutzt) | entfällt |
| `serve` (14.2.5) | W, A | – (`Plane.Gateway`) | entfällt |
| `mobx` (6.12.0), `mobx-react` (9.2.2), `mobx-utils` (6.0.8) | W, A, S, SS | Angular Signals + `@plane/state-kit` (§3.4.2) | ersetzt |
| `swr` (2.4.2) | W, A, S | `QueryCache` in `@plane/state-kit` (D08-ADR-08) | ersetzt |
| `axios` (1.20.0) | W, S, SV, L | `HttpClient` (`withFetch`) + `APIService` (D08-ADR-09) | ersetzt |
| `next-themes` (0.4.6) | W, A, S | `ThemeService` + Inline-Script (D08-ADR-15) | ersetzt |
| `react-hook-form` (^7.84.0) | W, A, S | Angular Signal Forms (`@angular/forms` 22.x) (D08-ADR-13) | ersetzt |
| `@base-ui/react` (1.6.0) | W, B | `@angular/aria` 22.x + `@angular/cdk` 22.x + `@floating-ui/dom` (ADR-041) | ersetzt |
| `@makeplane/propel` (0.7.3) | W, A, S, B, E, U, TC | `libs/shared/propel` (Port; `styles/` 1:1; Icons per `tools/icons-codegen`) | portiert |
| Propel-interne Abhängigkeiten `react-day-picker` 10.0.1, `lucide-react` 1.34.0 (Kopie in Propel) | über Propel | `pl-calendar` (D08-ADR-21); Lucide-Icons der Propel-Kopie per Codegen | ersetzt |
| `lucide-react` (0.469.0) | W, A, S, B, E, U | `lucide` 0.469.x (statische SVG-Daten, ISC) → Codegen zu Angular-Icon-Komponenten mit identischem SVG | ersetzt |
| `@floating-ui/dom` (^1.7.1) | E | `@floating-ui/dom` 1.7.x | übernommen |
| `@floating-ui/react` (^0.27.20) | E | `@floating-ui/dom` + `FloatingService` (`computePosition`, `autoUpdate`, Middlewares wie Original) | ersetzt |
| `@atlaskit/pragmatic-drag-and-drop` (1.7.4), `…-auto-scroll` (1.4.0), `…-hitbox` (1.1.0) | W, B (ohne auto-scroll) | gleiche Pakete und Versionen + `libs/shared/dnd` | übernommen |
| `@bprogress/core` (^1.3.4) | W, A, S | gleich | übernommen |
| `@fontsource-variable/inter` (5.2.8), `@fontsource/ibm-plex-mono` (5.2.7), `@fontsource/material-symbols-rounded` (5.2.30) | W, A, S | gleich | übernommen |
| `@tanstack/react-table` (^8.21.3) | W | `@tanstack/angular-table` 8.21.x | ersetzt |
| `@tanstack/react-virtual` (^3.13.12) | B | `@tanstack/virtual-core` 3.13.x | ersetzt |
| `class-variance-authority` (0.7.1) | B | gleich | übernommen |
| `clsx` (^2.1.1) | W, S, B, U | gleich | übernommen |
| `tailwind-merge` (3.4.0) | U | gleich | übernommen |
| `cmdk` (^1.1.1) | W | `pl-command` (D08-ADR-17) | ersetzt |
| `comlink` (^4.4.1) | W | – (im Quelltext ungenutzt) | entfällt |
| `date-fns` (^4.1.0) | W, S, B, U | gleich | übernommen |
| `emoji-picker-react` (^4.5.16) | W | – (im Quelltext ungenutzt) | entfällt |
| `frimousse` (^0.3.0) | B | eigener Emoji-Picker + `emojibase-data` (MIT, Version ⚠ wie frimousse 0.3) (D08-ADR-20) | ersetzt |
| `export-to-csv` (^1.4.0) | W | gleich | übernommen |
| `lodash-es` (4.18.1) | W, A, S, B, E, SS, U | gleich (`@types/lodash-es` dev) | übernommen |
| `react-dropzone` (^14.2.3) | W, S | Direktive `[plDropzone]` (§3.9) | ersetzt |
| `react-fast-compare` (^3.2.2) | W | – (ungenutzt) | entfällt |
| `react-is` (^19.2.8) | W | – (nur Peer/Override) | entfällt |
| `react-markdown` (^10.1.0) | W | – (`WEB/components/ui/markdown-to-component.tsx` ohne Verwender, nicht portieren) | entfällt |
| `react-masonry-component` (^6.3.0) | W | `masonry-layout` 4.2.2 (MIT) + `[plMasonry]` | ersetzt |
| `react-pdf-html` (^2.1.2), `@react-pdf/renderer` (^4.8.1) | W (und L) | – Frontend ruft serverseitigen PDF-Export `/live/pdf-export/` (01 ADR-029) | entfällt |
| `smooth-scroll-into-view-if-needed` (^2.0.2) | W | gleich | übernommen |
| `use-font-face-observer` (^1.3.0) | B | `FontFaceObserverService` (`document.fonts.load`) | ersetzt |
| `uuid` (14.0.0) | W, A, S, E, SS, U | gleich | übernommen |
| `@tiptap/core` (^2.27.3), `@tiptap/pm`, `@tiptap/starter-kit`, `@tiptap/html`, `@tiptap/suggestion`, `@tiptap/extension-{blockquote,character-count,collaboration,document,emoji,heading,image,list-item,mention,placeholder,task-item,task-list,text,text-align,text-style,underline}` (^2.22.3) | E (L: core/html) | gleiche Pakete/Versionen (Schema-Freeze, ADR-042) | übernommen |
| `@tiptap/react` (^2.22.3) | E | `libs/shared/editor/angular-binding` (vendored, ngx-tiptap-13-Muster) | ersetzt |
| `@hocuspocus/provider` (2.15.2) | E | gleich | übernommen |
| `yjs` (^13.6.20), `y-prosemirror` (^1.3.7), `y-protocols` (^1.0.6), `y-indexeddb` (^9.0.12) | E (L: yjs, y-prosemirror, y-protocols) | gleich | übernommen |
| `prosemirror-codemark` (^0.4.2), `tippy.js` (^6.3.7), `tiptap-markdown` (^0.8.10), `linkifyjs` (^4.3.2), `lowlight` (^3.0.0), `highlight.js` (^11.8.0), `emoji-regex` (^10.3.0), `is-emoji-supported` (^0.0.5) | E | gleich | übernommen |
| `jsx-dom-cjs` (^8.0.3) | E (`table-view.tsx`) | `libs/shared/editor/core/helpers/dom-builder.ts` (`h(tag, attrs, …children)` mit identischem DOM) | ersetzt |
| `buffer` (^6.0.3) | E (`yjs-utils.ts`) | gleich (Browser-Polyfill, MIT) | übernommen |
| `i18next` (25.10.9), `i18next-icu` (2.4.3), `i18next-resources-to-backend` (1.2.1) | I | gleich | übernommen |
| `react-i18next` (16.6.6) | I | `TranslationService` + Pipe `t` | ersetzt |
| `file-type` (^21.3.1) | SV | gleich (`fileTypeFromBlob`) | übernommen |
| `zod` (^3.25.76) | SS, L | – (in `PKG/shared-state` ungenutzt) | entfällt |
| `chroma-js` (^3.2.0) | U | gleich | übernommen |
| `sanitize-html` (2.17.7) | U | gleich (Browser-Bundle, MIT) | übernommen |
| `unified` (^11.0.5), `rehype-parse` (^9.0.1), `rehype-remark` (^10.0.1), `remark-gfm` (^4.0.1), `remark-stringify` (^11.0.0), `hast-util-to-mdast` (^10.1.2), `hast` (^1.0.0), `mdast` (^3.0.0) | U | gleich | übernommen |
| `@plane/blocks`, `@plane/constants`, `@plane/editor`, `@plane/hooks`, `@plane/i18n`, `@plane/services`, `@plane/shared-state`, `@plane/types`, `@plane/utils` (`workspace:*`) | W, A, S, Pakete | `libs/shared/*` (§3.1.3) | portiert |
| `@plane/tailwind-config` (`workspace:*`) | W, A, S (dev) | `libs/shared/tailwind-config` | portiert |
| `@plane/typescript-config` (`workspace:*`) | alle (dev) | `FE/tsconfig.base.json` | ersetzt |
| `@plane/logger` (`workspace:*`; `winston` ^3.17.0, `express-winston` ^4.2.0) | L | – (Backend: `ILogger`, 01 ADR-035) | entfällt |
| `@plane/decorators` (`workspace:*`; `reflect-metadata` ^0.2.2) | L | – (Live-Server-Controller → .NET) | entfällt |

#### 4.8.2 `apps/live` (Node-Laufzeit entfällt, ADR-002 – Zuordnung zu .NET nur zur Vollständigkeit)

| Original-Paket | Ziel (Details `07-realtime-kollaboration-dokumente.md`) |
|---|---|
| `@hocuspocus/server`, `@hocuspocus/extension-database`, `@hocuspocus/extension-logger`, `@hocuspocus/extension-redis`, `@hocuspocus/transformer` (2.15.2) | `Plane.Realtime`/`Plane.Collaboration` (YDotNet, eigenes Protokoll, Valkey-Fan-out), `Plane.Documents` |
| `express` (4.22.0), `express-ws` (^5.0.2), `ws` (8.21.0), `helmet` (^7.1.0), `cors` (^2.8.5), `compression` (1.8.2) | ASP.NET Core (Kestrel, WebSockets, Middleware) |
| `ioredis` (5.7.0) | StackExchange.Redis (Valkey) |
| `effect` (3.20.0), `@effect/platform` (^0.94.0), `@effect/platform-node` (^0.104.0) | .NET (`Task`, Options, Resilience) |
| `sharp` (^0.35.5) | SkiaSharp (ADR-032) |
| `@react-pdf/renderer` (^4.8.1), `@react-pdf/types` (^2.13.1), `@fontsource/inter` (5.2.8) | PDFsharp/MigraDoc `[6.2.4]` + gebündelte Inter (ADR-029) |
| `@tiptap/core`, `@tiptap/html`, `y-prosemirror`, `y-protocols`, `yjs`, `@plane/editor`, `@plane/services`, `@plane/types`, `@plane/utils`, `uuid`, `axios`, `zod`, `dotenv`, `react` | `Plane.Documents` (C#-Schema-Port, Fallback Jint), `HttpClient`, Options |
| Dev: `vitest`, `@vitest/coverage-v8`, `pdf-parse` (^2.4.5), `@types/*`, `tsdown`, `typescript` | xUnit/Verify (Golden-PDF-Tests); `pdf-parse`-Fälle als Spezifikation (21 Tests) |

#### 4.8.3 Entwicklungs- und Build-Abhängigkeiten

| Original-Paket (Version) | Nutzung | Ziel | Art |
|---|---|---|---|
| `vite` (8.0.16), `vite-tsconfig-paths` (^5.1.4), `@react-router/dev` (8.3.0) | W, A, S | `@angular/build` 22.x (esbuild + Vite-Dev-Server intern), `tsconfig.base.json`-Paths | ersetzt |
| `typescript` (5.8.3) | alle | `typescript` 6.0.x (ADR-039, O-10) | ersetzt |
| `tsdown` (0.16.0) | Pakete | – (keine Lib-Builds, D08-ADR-01) | entfällt |
| `tsx` (4.20.6) | I | `tsx` (nur `tools/i18n-*`, Node zur Build-Zeit) | übernommen (Dev) |
| `tailwindcss` (4.1.17), `@tailwindcss/postcss` (4.1.17), `@tailwindcss/typography` (0.5.19), `postcss` (8.5.25) | W, A, S, TC, E | gleich | übernommen |
| `dotenv` (16.4.7) | W, A, S, L | – (Runtime-Config) | entfällt |
| `@types/react`, `@types/react-dom`, `@types/node` | div. | – bzw. `@types/node` nur in `tools/` | entfällt |
| `@types/lodash-es`, `@types/chroma-js`, `@types/hast`, `@types/mdast`, `@types/sanitize-html` | W, A, S, U, B, E, SS | gleich | übernommen |
| `vitest` (^4.1.11), `@vitest/coverage-v8` | B, SV, CM, L | gleich (Angular-Builder `unit-test` mit Vitest) | übernommen |
| `@testing-library/react` (16.3.3) | B | `@testing-library/angular` 19.x | ersetzt |
| `@testing-library/user-event` (14.6.1) | B | gleich | übernommen |
| `jsdom` (23.2.0) | B | `jsdom` (aktuelle Major, vom Angular-Vitest-Runner unterstützt ⚠) | übernommen |
| `jscodeshift` (^17.3.0), `@hypermod/utils` (^0.7.1), `ast-types` (0.14.2), `@types/jscodeshift` | CM | – (Original-Codemods); eigener TS-6-Codemod (O-10) in `tools/` nach Bedarf mit `ts-morph` (MIT) | entfällt |
| `turbo` (2.10.11) | R | pnpm-Skripte + Angular-CLI-Cache + CI-Cache | ersetzt |
| `oxlint` (1.51.0), `oxfmt` (0.35.0) | R | `eslint` 9 + `angular-eslint` 22 + `typescript-eslint` + Sheriff-Plugin, `prettier` 3 (ADR-039) | ersetzt |
| `husky` (9.1.7), `lint-staged` (16.2.7) | R | gleich | übernommen |
| `react-doctor` (^0.4.2) | R | – | entfällt |
| Storybook-Pakete (nur Catalog, keine Deklaration in `apps/*`/`packages/*`) | – | – (Komponenten-Galerie für Visual Tests als eigene Angular-App `apps/e2e/gallery`, §7) | entfällt |

#### 4.8.4 Neue Frontend-Pakete (nicht im Original)

| Paket | Version | Lizenz | Zweck |
|---|---|---|---|
| `@angular/{core,common,router,forms,platform-browser,compiler,animations}`, `@angular/cdk`, `@angular/aria`, `@angular/build`, `@angular/cli` | 22.x | MIT | Framework |
| `@microsoft/signalr` | 10.0.x | MIT | Live-Events (H6) |
| `masonry-layout` | 4.2.2 | MIT | Stickies-Masonry |
| `emojibase-data` | ⚠ (Version wie frimousse 0.3) | MIT | Emoji-Daten offline |
| `lucide` | 0.469.x | ISC | Icon-Quelldaten (Codegen) |
| `d3-scale`, `d3-shape`, `d3-array`, `d3-hierarchy`, `d3-format` | 4.x/3.x | ISC | Charts |
| `@tanstack/angular-table`, `@tanstack/virtual-core` | 8.21.x / 3.13.x | MIT | Tabellen, Virtualisierung |
| `@softarc/sheriff-core`, `@softarc/eslint-plugin-sheriff` | 0.20.x | MIT | Modulgrenzen (Dev) |
| `@playwright/test`, `@axe-core/playwright` | 1.5x / 4.x | Apache-2.0 / MPL-2.0 (Dev) | E2E, Visual, a11y |
| `ts-morph` (optional) | 2x | MIT | Codemods (Dev) |

### 4.9 Edge-Cases des Originals – Entscheidung (A08 §3.10, A11 §3.31 Auszug)

| # | Befund | Entscheidung | Kennung `deviations.yaml` |
|---|---|---|---|
| E1 | Disabled-Feature-Buttons → `/settings/projects/:pid/features` (keine Route) | **korrigieren**: Redirect-Route R2 auf `features/cycles/`; Buttons verlinken direkt auf das jeweilige Feature | FE-E1 |
| E2 | Integrations-Seite ohne Route | nicht portieren (ADR-007) | – |
| E3 | doppelte Redirect-Definition | nur eine Quelle (`redirects.ts`) | – (intern) |
| E4 | `login`, `register`, `signin` nicht in `RESTRICTED_URLS` | **korrigieren** in `@plane/constants` (Frontend-Prüfung) und Backend (04) | FE-E4 |
| E5 | Projekt-Archiv-Routen ohne Bootstrap | **korrigieren** (`ProjectBootstrapComponent`) | FE-E5 |
| E6 | archiviertes Detail ohne Loader | beibehalten | – |
| E7 | Project-View-Filter leert falschen Store | **korrigieren** | FE-E7 |
| E8 | Draft-Filter unter Key `PROFILE` | **korrigieren** | FE-E8 |
| E9 | `BasePage.update` sendet Vorher-Snapshot | **korrigieren** | FE-E9 |
| E10 | `module_sidebar_collapsed` String vs. Bool | beibehalten (Formate unverändert, keine Nutzerwirkung) | – |
| E11 | invertierter Name `isSmallerScreen` | beibehalten (Verhalten) | – |
| E12 | „Go home“ auf `/invitations` → `/` | beibehalten | – |
| E13 | ungültige Tabs/Views ohne 404 | `/settings/profile/:invalid` → **Redirect `general`** (Dauer-Spinner ist Fehler); übrige beibehalten | FE-E13 |
| E14 | Theme-Store schreibt, liest nicht | beibehalten | – |
| E15 | Redirect hängt `?` an | beibehalten | – |
| E16 | fehlendes Label für `/features/*` in Mobile-Nav | **korrigieren** (Label aus `PROJECT_SETTINGS`) | FE-E16 |
| E17 | WS-Admin ohne Projektmitgliedschaft → „Join“ | beibehalten (gewollt) | – |
| E18 | toter Code (`dashboard.store`, `issue_gantt_view.store`, `use-dashboard`, `dashboard.helper`) | nicht portieren | – |
| E19 | `sw.js`, abweichendes `manifest.json` | `sw.js`/Workbox nicht ausliefern; `apps/web/manifest.json` (nicht ausgeliefert) nicht portieren | – |
| E20 | wirkungslose Bedingung in `handleIssuesLocalFilters.get` | **korrigieren** (gleiches Ergebnis, lesbarer Code) | FE-E20 |
| E21 | completed Cycle ohne „Add work item“ | beibehalten (fachlich) | – |
| E22 | `router.push` verzögert | beibehalten (`AppRouter`) | – |
| E23 | Fehlerzweig Einladung praktisch unerreichbar | beibehalten | – |
| E24 | doppelte Übernahme in `fetchIssueWithIdentifier` | beibehalten | – |
| E25 | Badge zählt Mentions statt Gesamt | beibehalten (fachlich) | – |
| E26 | `ProjectAuthWrapper` rendert `null` | beibehalten | – |
| A1 | Admin `updateInstanceInfo` legt Antwort unter `instance.instance` ab | **korrigieren** | FE-A1 |
| A2 | Admin `disableEmail` ohne Rethrow (Fehler-Toast nie sichtbar) | **korrigieren** | FE-A2 |

Die Kennungen werden in `tests/contracts/deviations.yaml` (01 §7.20) unter `frontend:` geführt; Visual-/E2E-Tests der betroffenen Szenarien referenzieren die Kennung.

---
## 5. Code-Skelette

Die Skelette legen Namen, Signaturen und Semantik fest; Implementierungsdetails folgen dem jeweils genannten Original.

### 5.1 `apps/web/src/index.html` – Inline-Theme-Script (Logik next-themes 0.4.6)

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>Plane | Simple, extensible, open-source project management tool.</title>
  <base href="/" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <meta name="theme-color" content="#fff" />
  <!-- PWA-/OG-/Twitter-Meta wie WEB/app/root.tsx (og:url entfällt, ADR-004) -->
  <link rel="icon" type="image/png" sizes="32x32" href="favicon/favicon-32x32.png" />
  <link rel="manifest" href="/site.webmanifest.json" />
  <link rel="preload" href="media/inter-latin-wght-normal.woff2" as="font" type="font/woff2" crossorigin="anonymous" />
  <script>
    (function () {
      var THEMES = ["light", "dark", "light-contrast", "dark-contrast", "custom"]; // admin/space: ["light","dark"]
      var d = document.documentElement;
      var stored = null;
      try { stored = localStorage.getItem("theme"); } catch (e) {}
      var theme = stored && (stored === "system" || THEMES.indexOf(stored) !== -1) ? stored : "system";
      var resolved = theme === "system"
        ? (window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light")
        : theme;
      d.setAttribute("data-theme", resolved);
      if (resolved === "light" || resolved === "dark") d.style.colorScheme = resolved;
    })();
  </script>
</head>
<body>
  <div id="context-menu-portal"></div>
  <div id="editor-portal"></div>
  <pl-root>
    <!-- statischer HydrateFallback: LogoSpinner-Markup aus WEB/components/common/logo-spinner -->
    <div class="relative flex h-screen w-full items-center justify-center bg-canvas"><!-- spinner svg --></div>
  </pl-root>
</body>
</html>
```

### 5.2 `apps/web/src/app.config.ts`

```ts
export const appConfig: ApplicationConfig = {
  providers: [
    provideBrowserGlobalErrorListeners(),
    provideZonelessChangeDetection(),
    provideAppInitializer(() => inject(RuntimeConfigLoader).load()),       // 1
    provideAppInitializer(() => inject(TranslationService).init()),        // 2 (= await initPromise)
    provideRouter(
      routes,
      withComponentInputBinding(),
      withRouterConfig({ paramsInheritanceStrategy: 'always' }),
      withInMemoryScrolling({ scrollPositionRestoration: 'disabled' }),
      withNavigationErrorHandler(staleChunkNavigationErrorHandler),
    ),
    { provide: LocationStrategy, useClass: TrailingSlashPathLocationStrategy },
    { provide: TitleStrategy, useClass: PlaneTitleStrategy },
    provideHttpClient(
      withFetch(),
      withInterceptors([trailingSlashInterceptor, credentialsInterceptor, csrfInterceptor, unauthorizedInterceptor, abortInterceptor]),
    ),
    provideQueryCacheConfig(WEB_SWR_CONFIG),
    { provide: ErrorHandler, useClass: PlaneErrorHandler },
    provideAppInitializer(() => inject(ProgressBarService).attach()),
    provideWebStoreOverrides(),       // §6.3 – CE: Base*-Stores unter CE-Namen
    provideWebExtensions(),           // §6 – CE-Defaults aller Registries
  ],
};
```

### 5.3 `apps/web/src/app.routes.ts` – Struktur (Ausschnitt, Reihenfolge verbindlich)

```ts
const page = (l: () => Promise<Type<unknown>>) => ({ loadComponent: l });

export const routes: Routes = [
  {
    path: '',
    loadComponent: () => import('./pages/layout.component').then(m => m.AppShellLayoutComponent), // L0
    children: [
      // A – statische Redirects
      { path: 'accounts/sign-up', redirectTo: '/' },
      { path: 'sign-in', redirectTo: '/' },
      { path: 'signin', redirectTo: '/' },
      { path: 'login', redirectTo: '/' },
      { path: 'register', redirectTo: '/' },
      { matcher: splatMatcher('profile'), redirectTo: redirectToProfileSettings },
      { path: 'sign-up', redirectTo: '/' },
      { path: 'accounts/forgot-password', redirectTo: '/' },
      { path: 'accounts/reset-password', redirectTo: '/' },
      { path: 'accounts/set-password', redirectTo: '/' },
      // B – statische Top-Level-Routen
      {
        path: '', pathMatch: 'full', data: { robots: 'index, nofollow' },
        loadComponent: () => import('./pages/(home)/layout.component').then(m => m.HomeLayoutComponent),
        children: [{ path: '', ...page(() => import('./pages/(home)/page').then(m => m.SignInPageComponent)) }],
      },
      {
        path: 'create-workspace', title: 'Create Workspace',
        loadComponent: () => import('./pages/(all)/create-workspace/layout.component').then(m => m.CreateWorkspaceLayoutComponent),
        children: [{ path: '', ...page(() => import('./pages/(all)/create-workspace/page').then(m => m.CreateWorkspacePageComponent)) }],
      },
      // … onboarding, invitations, workspace-invitations (ab I1)
      // C – Redirects mit Workspace-Präfix
      { matcher: splatMatcher(':workspaceSlug/projects/:projectId/settings'), redirectTo: redirectToProjectSettings },
      { path: ':workspaceSlug/analytics', pathMatch: 'full', redirectTo: ({ params }) => `/${params['workspaceSlug']}/analytics/overview/` },
      { path: ':workspaceSlug/settings/api-tokens', redirectTo: '/settings/profile/api-tokens/' },
      { path: ':workspaceSlug/projects/:projectId/inbox', redirectTo: ({ params }) => `/${params['workspaceSlug']}/projects/${params['projectId']}/intake/` },
      { matcher: splatMatcher(':workspaceSlug/settings/account'), redirectTo: redirectToProfileSettings },
      { path: ':workspaceSlug/settings/billing', redirectTo: ({ params }) => `/${params['workspaceSlug']}/settings/` },
      { path: ':workspaceSlug/settings/projects/:projectId/features', pathMatch: 'full',
        redirectTo: ({ params }) => `/${params['workspaceSlug']}/settings/projects/${params['projectId']}/features/cycles/` },
      // D – LALL
      {
        path: '', data: { robots: 'noindex, nofollow' },
        loadComponent: () => import('./pages/(all)/layout.component').then(m => m.AllLayoutComponent),
        children: [
          { path: 'settings/profile', loadComponent: () => import('./pages/(all)/settings/profile/layout.component').then(m => m.ProfileSettingsLayoutComponent),
            children: [{ path: ':profileTabId', ...page(() => import('./pages/(all)/settings/profile/[profileTabId]/page').then(m => m.ProfileSettingsPageComponent)) }] },
          {
            path: ':workspaceSlug',
            loadComponent: () => import('./pages/(all)/[workspaceSlug]/layout.component').then(m => m.WorkspaceLayoutComponent), // LWS
            children: [
              { path: '', loadComponent: () => import('./pages/(all)/[workspaceSlug]/(projects)/layout.component').then(m => m.ProjectsAppLayoutComponent), // LPRJ
                children: [
                  { path: '', pathMatch: 'full', ...page(() => import('./pages/(all)/[workspaceSlug]/(projects)/page').then(m => m.WorkspaceHomePageComponent)) },
                  // E – profile/:userId › '' | activity | :profileViewId  (activity VOR :profileViewId)
                  // E – projects/archives, projects (''), projects/:projectId/archives/…, dann projects/:projectId (LPD) › F
                ] },
              { path: '', loadComponent: () => import('./pages/(all)/[workspaceSlug]/(settings)/layout.component').then(m => m.SettingsLayoutComponent), // LSET
                children: [ /* G – settings/projects VOR settings */ ] },
            ],
          },
        ],
      },
      // H – Catch-all
      { path: '**', ...page(() => import('./pages/not-found.page').then(m => m.NotFoundPageComponent)) },
    ],
  },
];
```

### 5.4 Splat-Matcher, Redirect-Funktionen, Legacy-Guard (`pages/routes/redirects/redirects.ts`)

```ts
/** Matcht `prefix/**`; Platzhalter `:name` im Präfix werden zu posParams, Rest als `splat`. */
export function splatMatcher(prefix: string): UrlMatcher {
  const parts = prefix.split('/');
  return (segments) => {
    if (segments.length < parts.length) return null;
    const posParams: Record<string, UrlSegment> = {};
    for (let i = 0; i < parts.length; i++) {
      const p = parts[i];
      if (p.startsWith(':')) posParams[p.slice(1)] = segments[i];
      else if (p !== segments[i].path) return null;
    }
    const rest = segments.slice(parts.length).map(s => s.path).join('/');
    posParams['splat'] = new UrlSegment(rest, {});
    return { consumed: segments, posParams };
  };
}

export const redirectToProfileSettings: RedirectFunction = ({ params, queryParams }) => {
  const splat = params['splat'] || 'general';
  const query = new URLSearchParams(queryParams as Record<string, string>).toString();
  return `/settings/profile/${splat}?${query}`; // „?“ immer (E15)
};

export const redirectToProjectSettings: RedirectFunction = ({ params }) =>
  params['splat']
    ? `/${params['workspaceSlug']}/settings/projects/${params['projectId']}/${params['splat']}/`
    : `/${params['workspaceSlug']}/settings/projects/${params['projectId']}/`;

export const legacyIssueRedirectGuard: CanActivateFn = async (route) => {
  const { workspaceSlug, projectId, issueId } = route.params;
  try {
    const meta = await inject(IssueService).getIssueMetaFromURL(workspaceSlug, projectId, issueId);
    return inject(Router).parseUrl(`/${workspaceSlug}/browse/${meta.project_identifier}-${meta.sequence_id}/`);
  } catch {
    return true; // Page zeigt EmptyState → /${ws}/workspace-views/all-issues/
  }
};
```

### 5.5 `AppRouter` und `PathnameService` (`libs/web/core/lib/`)

```ts
@Injectable({ providedIn: 'root' })
export class PathnameService {
  private readonly router = inject(Router);
  readonly pathname = signal(window.location.pathname);
  readonly searchParams = signal(new URLSearchParams(window.location.search));
  constructor() {
    this.router.events.pipe(filter(e => e instanceof NavigationEnd), takeUntilDestroyed()).subscribe(() => {
      // nach replaceState durch TrailingSlashPathLocationStrategy: Browser-Pfad inkl. "/"
      this.pathname.set(window.location.pathname);
      this.searchParams.set(new URLSearchParams(window.location.search));
    });
  }
}

@Injectable({ providedIn: 'root' })
export class AppRouter {
  private readonly router = inject(Router);
  push(href: string): void { setTimeout(() => void this.router.navigateByUrl(ensureTrailingSlash(href)), 0); }
  replace(href: string): void { setTimeout(() => void this.router.navigateByUrl(ensureTrailingSlash(href), { replaceUrl: true }), 0); }
  back(): void { history.back(); }
  forward(): void { history.forward(); }
  refresh(): void { location.reload(); }
  prefetch(): void { /* no-op wie Shim */ }
}
```

### 5.6 Wrapper-Komponente (`libs/web/core/wrappers/authentication-wrapper.component.ts`)

```ts
@Component({
  selector: 'pl-authentication-wrapper',
  template: `
    @switch (state()) {
      @case ('loading') { <div class="relative flex h-screen w-full items-center justify-center"><pl-logo-spinner /></div> }
      @case ('content') { <ng-content /> }
    }`,
})
export class AuthenticationWrapperComponent {
  readonly pageType = input<EPageTypes>(EPageTypes.AUTHENTICATED);
  private readonly user = inject(UserStore);
  private readonly workspaceRoot = inject(WorkspaceRootStore);
  private readonly appRouter = inject(AppRouter);
  private readonly pathname = inject(PathnameService).pathname;

  private readonly query = injectQuery(() => 'USER_INFORMATION', () => this.user.fetchCurrentUser(),
    { revalidateOnFocus: false, shouldRetryOnError: false });

  readonly state = computed<'loading' | 'redirect' | 'content'>(() => {
    if (this.user.isLoading() || (this.user.data() && this.workspaceRoot.loader())) return 'loading';
    return this.redirectTarget() ? 'redirect' : 'content';
  });

  /** Matrix A08 §2.3.1 – 1:1 aus authentication-wrapper.tsx */
  private readonly redirectTarget = computed<string | null>(() => { /* … */ return null; });

  constructor() {
    effect(() => {
      const target = this.redirectTarget();
      if (this.state() === 'redirect' && target) untracked(() => this.appRouter.push(target));
    });
  }
}
```

### 5.7 `@plane/state-kit` – Primitive (Signaturen)

```ts
// entity-map.ts
export interface EntityMap<T> {
  get(id: string): Signal<T | undefined>;
  peek(id: string): T | undefined;                // ohne Tracking
  has(id: string): boolean;
  set(id: string, value: T): void;
  patch(id: string, partial: Partial<T>): void;   // wie lodash set je Schlüssel
  delete(id: string): void;
  upsertMany(values: T[], idOf: (v: T) => string): void;
  keys: Signal<string[]>;
  values: Signal<T[]>;
  entries: Signal<[string, T][]>;
  clear(): void;
}
export function entityMap<T>(init?: Record<string, T>): EntityMap<T>;

// deep-state.ts (D08-ADR-05)
export interface DeepState<T extends object> {
  get<V = unknown>(path?: PropertyPath): V;       // trackt Version
  select<V = unknown>(path: PropertyPath): Signal<V>; // memoisiert je Pfad, Object.is
  set(path: PropertyPath, value: unknown): void;  // lodash.set + version++
  update(path: PropertyPath, fn: (v: any) => unknown): void;
  unset(path: PropertyPath): void;
  replace(next: T): void;
  raw(): T;                                        // nur für portierte Algorithmen innerhalb des Stores
}
export function deepState<T extends object>(init: T): DeepState<T>;

// memoized-computed.ts (computedFn)
export function memoizedComputed<A extends unknown[], R>(fn: (...args: A) => R, opts?: { maxEntries?: number; key?: (...args: A) => string }): (...args: A) => R;

// reaction-effect.ts (mobx reaction)
export function reactionEffect<T>(expr: () => T, effectFn: (value: T, prev: T | undefined) => void,
  opts?: { delay?: number; fireImmediately?: boolean; equals?: (a: T, b: T) => boolean; injector?: Injector }): EffectRef;

export function untilSignal(predicate: () => boolean, injector?: Injector): Promise<void>;          // mobx when
export function persisted<T>(key: string, initial: T, opts?: { raw?: boolean }): WritableSignal<T>; // localStorage, try/catch
export function injectLazy<T>(token: ProviderToken<T>): () => T;                                    // Zyklen zwischen Stores
export function debouncedSignal<T>(source: Signal<T>, ms: number): Signal<T>;
```

### 5.8 QueryCache (`@plane/state-kit/query-cache`)

```ts
export interface QueryOptions {
  dedupingInterval?: number;     // 2000
  revalidateOnFocus?: boolean;   // Throttle focusThrottleInterval 5000
  revalidateOnReconnect?: boolean;
  revalidateIfStale?: boolean;
  revalidateOnMount?: boolean;
  refreshInterval?: number;
  refreshWhenHidden?: boolean;
  errorRetryCount?: number;
  errorRetryInterval?: number;   // 5000
  shouldRetryOnError?: boolean;
}
export interface QueryRef<T> {
  data: Signal<T | undefined>;
  error: Signal<unknown>;
  isLoading: Signal<boolean>;
  isValidating: Signal<boolean>;
  mutate(data?: T | ((cur: T | undefined) => T), opts?: { revalidate?: boolean }): Promise<T | undefined>;
}
/** Im Injection-Context aufrufen; key() === null ⇒ kein Abruf (bedingter SWR-Key). */
export function injectQuery<T>(key: () => string | null, fetcher: (key: string) => Promise<T>, options?: QueryOptions): QueryRef<T>;

@Injectable({ providedIn: 'root' })
export class QueryCache {
  mutate(keyOrPredicate: string | ((key: string) => boolean), data?: unknown, opts?: { revalidate?: boolean }): Promise<void>;
}
export function provideQueryCacheConfig(config: QueryOptions): EnvironmentProviders;
```

### 5.9 `APIService` und 401-Interceptor

```ts
export type ApiResponse<T> = { data: T; status: number; headers: HttpHeaders };
export type ApiRequestConfig = { params?: Record<string, unknown>; headers?: Record<string, string>; signal?: AbortSignal;
  withCredentials?: boolean; responseType?: 'json' | 'blob' | 'text'; onUploadProgress?: (e: { loaded: number; total?: number }) => void };

export abstract class APIService {
  protected readonly http = inject(HttpClient);
  protected constructor(protected readonly baseURL: string) {}
  get<T = any>(url: string, params: Record<string, unknown> = {}, config: ApiRequestConfig = {}): Promise<ApiResponse<T>> {
    return this.request<T>('GET', url, undefined, { ...config, params: { ...params, ...(config.params ?? {}) } });
  }
  post<T = any>(url: string, data: unknown = {}, config: ApiRequestConfig = {}) { return this.request<T>('POST', url, data, config); }
  put<T = any>(url: string, data: unknown = {}, config: ApiRequestConfig = {}) { return this.request<T>('PUT', url, data, config); }
  patch<T = any>(url: string, data: unknown = {}, config: ApiRequestConfig = {}) { return this.request<T>('PATCH', url, data, config); }
  delete<T = any>(url: string, data?: unknown, config: ApiRequestConfig = {}) { return this.request<T>('DELETE', url, data, config); }
  request<T>(method: string, url: string, body: unknown, config: ApiRequestConfig): Promise<ApiResponse<T>> {
    /* HttpClient.request(...) → firstValueFrom; Fehler → throw { response: { status, data: err.error, headers } } */
    throw new Error('skeleton');
  }
}

export const unauthorizedInterceptor: HttpInterceptorFn = (req, next) =>
  next(req).pipe(catchError((err: HttpErrorResponse) => {
    if (err.status === 401 && !req.context.get(SKIP_401_REDIRECT) && window.location.pathname !== '/') {
      window.location.replace(`/?next_path=${encodeURIComponent(window.location.pathname)}`);
    }
    return throwError(() => err);
  }));
```

### 5.10 `BaseIssuesStore.issueUpdate` (Ausschnitt, 1:1-Port)

```ts
export abstract class BaseIssuesStore implements IBaseIssuesStore {
  readonly loader = deepState<Record<string, TLoader>>({});
  readonly groupedIssueIds = deepState<{ value: TGroupedIssues | TSubGroupedIssues | string[] | undefined }>({ value: undefined });
  readonly groupedIssueCount = deepState<Record<string, number>>({});
  readonly issuePaginationData = deepState<Record<string, TPaginationData>>({});
  readonly paginationOptions = signal<IssuePaginationOptions | undefined>(undefined);

  constructor(protected readonly rootIssueStore: IIssueRootStore, protected readonly issueFilterStore: IBaseIssueFilterStore,
              protected readonly issueService: IssueService, protected readonly injector: Injector) {}

  async issueUpdate(workspaceSlug: string, projectId: string, issueId: string, data: Partial<TIssue>, shouldSync = true) {
    const issueBeforeUpdate = clone(this.rootIssueStore.issues.getIssueById(issueId));
    try {
      this.rootIssueStore.issues.updateIssue(issueId, data);
      this.updateIssueList({ ...issueBeforeUpdate, ...data } as TIssue, issueBeforeUpdate);
      if (!shouldSync) return;
      this.updateParentStats(issueBeforeUpdate, { ...issueBeforeUpdate, ...data } as TIssue);
      await this.issueService.patchIssue(workspaceSlug, projectId, issueId, data);
      this.fetchParentStats(workspaceSlug, projectId);
    } catch (error) {
      this.rootIssueStore.issues.updateIssue(issueId, issueBeforeUpdate ?? {});
      this.updateIssueList(issueBeforeUpdate, { ...issueBeforeUpdate, ...data } as TIssue);
      throw error;
    }
  }

  /** memoisiert je (groupId, subGroupId): gleiche Array-Referenz solange Gruppe unverändert */
  readonly getIssueIds = memoizedComputed((groupId?: string, subGroupId?: string) => { /* 1:1 aus Original */ return undefined as string[] | undefined; });
}
```

### 5.11 `*plRenderIfVisible` (`libs/web/core/components/render-if-visible.directive.ts`)

```ts
@Directive({ selector: '[plRenderIfVisible]' })
export class RenderIfVisibleDirective implements OnDestroy {
  readonly root = input<HTMLElement | null>(null, { alias: 'plRenderIfVisibleRoot' });
  readonly verticalOffset = input(50, { alias: 'plRenderIfVisibleVerticalOffset' });      // Prozent wie Original
  readonly horizontalOffset = input(0, { alias: 'plRenderIfVisibleHorizontalOffset' });
  readonly defaultHeight = input<string | number>('300px', { alias: 'plRenderIfVisibleDefaultHeight' });
  readonly defaultValue = input(false, { alias: 'plRenderIfVisibleDefaultValue' });       // z. B. isIssueNew
  readonly shouldRecordHeights = input(true, { alias: 'plRenderIfVisibleShouldRecordHeights' });
  readonly placeholder = input<TemplateRef<unknown> | null>(null, { alias: 'plRenderIfVisiblePlaceholder' });
  readonly forceRender = input(false, { alias: 'plRenderIfVisibleForceRender' });
  // IntersectionObserver mit rootMargin `${v}% ${h}% ${v}% ${h}%`; bei Austritt: gemessene Höhe merken,
  // Platzhalter mit dieser Höhe rendern (Original render-if-visible-HOC.tsx), idle-Callback bei useIdleTime
  ngOnDestroy(): void { /* observer.disconnect() */ }
}
```

### 5.12 DnD-Direktive (`libs/shared/dnd/draggable.directive.ts`)

```ts
@Directive({ selector: '[plDraggable]' })
export class DraggableDirective {
  readonly getInitialData = input<() => Record<string, unknown>>(() => ({}), { alias: 'plDraggable' });
  readonly canDrag = input<boolean>(true);
  readonly dragHandle = input<HTMLElement | null>(null);
  readonly dragStart = output<BaseEventPayload<ElementDragType>>();
  readonly dropped = output<BaseEventPayload<ElementDragType>>();
  private readonly host = inject(ElementRef<HTMLElement>);
  private readonly destroyRef = inject(DestroyRef);
  constructor() {
    afterNextRender(() => {
      const cleanup = combine(draggable({
        element: this.host.nativeElement,
        dragHandle: this.dragHandle() ?? undefined,
        canDrag: () => this.canDrag(),
        getInitialData: () => this.getInitialData()(),
        onDragStart: (p) => this.dragStart.emit(p),
        onDrop: (p) => this.dropped.emit(p),
      }));
      this.destroyRef.onDestroy(cleanup);
    });
  }
}
```

### 5.13 `TranslationService` und Pipe `t`

```ts
@Injectable({ providedIn: 'root' })
export class TranslationService {
  readonly currentLocale = signal<TLanguage>(FALLBACK_LANGUAGE);
  readonly languages = SUPPORTED_LANGUAGES;
  init(): Promise<void> {
    return initPromise.then(() => this.currentLocale.set(i18nInstance.language as TLanguage)).catch(() => {});
  }
  t(key: TTranslationKeys, params?: Record<string, unknown>): string {
    this.currentLocale(); // Abhängigkeit für computed/Templates
    return coerceToString(key, i18nInstance.t(key, params));
  }
  changeLanguage(lng: TLanguage): void {
    void setLanguage(lng).then(() => this.currentLocale.set(lng)).catch(err => console.error('Failed to change language:', err));
  }
}

@Pipe({ name: 't', pure: false })   // liest Signal; Neuberechnung nur bei CD-Lauf (zoneless: bei Signaländerung)
export class TranslatePipe implements PipeTransform {
  private readonly i18n = inject(TranslationService);
  transform(key: TTranslationKeys, params?: Record<string, unknown>): string { return this.i18n.t(key, params); }
}
```

---
## 6. Erweiterungspunkte für Bezahl-Pakete

**Grundsatz (01 P7, §1.4, §6.4):** Hier werden ausschließlich **Andockstellen** festgelegt – Token, Schnittstelle, CE-Default, Test. Kein Fachdesign der Pakete. Alle Tokens liegen in `FE/libs/web/extensions/src/` (Tag `domain:extensions`, importiert nur `scope:shared`), die CE-Defaults stellt `provideWebExtensions()` bereit. Ein Paket dockt an, indem es in seiner eigenen Lib (`FE/libs/web/<paket>/`) einen `provide<Paket>Extensions()`-Provider liefert, der in `app.config.ts` **hinter** `provideWebExtensions()` registriert wird – CE-Code wird dafür nicht geändert.

### 6.1 Übersicht Registry → 🧱-Paket → Ort im CE-Code

| Registry / Token | Art | CE-Default | Gelesen von (CE-Komponente) | 🧱-Pakete (weitere) | ab |
|---|---|---|---|---|---|
| `ROUTE_EXTENSIONS` | Multi `RouteExtension` | keine | Router-Konfiguration (`ROUTES`-Factory, §6.2) | B1, D1, F1, F2, H1 (A3…A7, B4 u. a.) | I0 |
| `SIDEBAR_ITEMS` | Multi `SidebarItemDefinition` | Einträge aus `WORKSPACE_SIDEBAR_STATIC_NAVIGATION_ITEMS`, `WORKSPACE_SIDEBAR_DYNAMIC_NAVIGATION_ITEMS`, Projekt-Navigation (Einträge aus `WEB/components/navigation/use-navigation-items.ts`: Work items, Cycles, Modules, Views, Pages, Intake) | `ProjectAppSidebar`, `ExtendedSidebar`, `TabNavigationRoot`, Customize-Navigation | B1, D1 (A4) | I0 (statisch) / I1 |
| `APP_RAIL_ENABLED` | Token `boolean` | `false` (wie `AppRailVisibilityProvider`) | `WorkspaceLayoutComponent` | D1 (Wiki-App), G1 (nicht gewählt) | I0 |
| `SETTINGS_PAGES` | Multi `SettingsPageDefinition` | Einträge aus `WORKSPACE_SETTINGS` (ohne `billing-and-plans`), `PROJECT_SETTINGS`, `PROFILE_SETTINGS` | Settings-Sidebars, `WORKSPACE_SETTINGS_ACCESS`-Prüfung in LWSET, Mobile-Nav, Power-K „open settings“ | E5, F1, F2, H1, A1 | I1 |
| `ADMIN_SETTINGS_PAGES` | Multi | Admin-Sidebar-Einträge (A11 §2.4) | Admin-Sidebar, Breadcrumbs | E3 (Group-Sync-Status), E5 | I0 |
| `PROPERTY_RENDERERS` | Multi `PropertyRendererDefinition` | keine (Standard-Properties bleiben eingebaut) | List-/Kanban-Properties (`IssueProperties`), Spreadsheet-Zellen, Peek-/Detail-Sidebar, Issue-Modal, Rich-Filter-Wertauswahl | A1, A2 | I2 |
| `SPREADSHEET_COLUMNS` | Multi `SpreadsheetColumnDefinition` | keine (Spalten aus `SPREADSHEET_PROPERTY_LIST` eingebaut) | `SpreadsheetHeader`, `SpreadsheetIssueRow`, Display-Properties-Menü | A1 | I2 |
| `GROUP_BY_OPTIONS` | Multi `GroupByOptionDefinition` (`key`, `serverKey`, `issueField`, `columns(ctx)`, `dragAllowed`) | keine (CE-Optionen aus `ISSUE_GROUP_BY_KEY`/`EIssueGroupByToServerOptions`) | `getGroupByColumns`, Display-Dropdown, `ISSUE_GROUP_BY_KEY`-Lookup (Fallback auf Registry) | A1, B1 (`team_project`) | I2 |
| `FILTER_FIELDS` | Multi `FilterFieldDefinition` | keine (CE-Felder aus `PKG/utils/src/work-item-filters/configs`) | `WorkItemFiltersConfigService` | A1, B6 | I2 |
| `FILTER_OPERATORS` | Token `FilterOperatorConfig` | `{ operators: CORE_OPERATORS, allowNegative: false }` | `FilterConfigManager`, Operator-Select | B6 | I2 |
| `RELATION_TYPES` | Multi `RelationTypeDefinition` (`key`, `reverseKey`, `i18nLabel`, `icon`, `className`) | Werte aus `ISSUE_RELATION_OPTIONS` (`WEB/components/relations/index.tsx`): `relates_to`, `duplicate`, `blocked_by`, `blocking` | Relations-Widget, Activity-Text, Relation-Modal | A9 | I2 |
| `TIMELINE_FLAGS` | Token `{ isDependencyEnabled: boolean }` | `false` (`ENABLE_ISSUE_DEPENDENCIES`) | `BaseTimeLineStore`, Gantt-Fetch (`expand=issue_relation,issue_related`) | A9 | I2 |
| `ISSUE_MODAL_CONTEXT` | Token `IssueModalContext`-Fabrik | CE-Stubs aus A09 §5.4 (`getIssueTypeIdOnProjectChange`, `getActiveAdditionalPropertiesLength → 0`, `handlePropertyValuesValidation → true`, `handleCreateUpdatePropertyValues → noop`, `handleProjectEntitiesFetch → noop`, `handleTemplateChange → noop`, `handleConvert → noop`, `handleCreateSubWorkItem → noop`, `workItemTemplateId → undefined`, `isApplyingTemplate → false`, `issuePropertyValues → {}`) | Issue-Modal | A1 (C2 nicht gewählt) | I2 |
| `WORK_ITEM_PROPERTIES_LOADER`, `WORKSPACE_ISSUE_PROPERTIES_EXTENDED` | Token Funktion | no-op | `useWorkItemProperties`-/`useWorkspaceIssuePropertiesExtended`-Ersatz in Layout-Roots | A1, A2 | I2 |
| `WORK_ITEM_DETAIL_WIDGETS` | Multi `DetailWidgetDefinition` (`key`, `order`, `component`, `visible(ctx)`) | CE-Widgets Sub-Work-Items, Relations, Links, Attachments | Detail-Seite, Peek | F1, F2 (A10, A14) | I2 |
| `WORK_ITEM_ACTIONS` | Multi `WorkItemActionDefinition` (Quick-Action-/Kontextmenü-Einträge) | CE-Einträge aus `quick-action-dropdowns/*` | „…“-Menü, Rechtsklick-Menü, Peek-Header | F2 („Branch-Namen kopieren“, „PR öffnen“) | I2 |
| `ACTIVITY_RENDERERS` | Multi `ActivityRendererDefinition` (`field`/`verb` → Komponente) | CE-Abbildung aller `field`-Werte (A09 §2.15) | Activity-Feed | F2 (Branch/Commit/PR), A1, C1 | I2 |
| `WORKFLOW_GUARD` | Token (`workflowDisabledSource`, `isWorkflowDropDisabled`, `getIsWorkflowWorkItemCreationDisabled`, `handleWorkFlowState`, `allowedStateIds(ctx)`) | Stub aus `WEB/components/workflow/use-workflow-drag-n-drop.ts` (alles erlaubt) | `list-group`, `kanban/default`, `kanban-group`, `swimlanes`, `StateSelect` | C1 (nicht gewählt) | I2 |
| `BULK_OPERATIONS_ENABLED` | Token `boolean` | `false` | Multiple-Select-Leiste | (A-Paket Bulk Ops) | I2 |
| `PERMISSION_EVALUATOR` | Token `PermissionEvaluator` (kein Multi) | `RoleBasedPermissionEvaluator` (Logik `BaseUserPermissionStore.allowPermissions`/`getProjectRole`/`hasPageAccess`) | `PermissionService.allowPermissions(...)` (einzige Prüf-API in Komponenten) | E5, B1 | I0 |
| `SCOPE_LEVELS` | Token `readonly ScopeLevel[]` | `['workspace','project']` | `PermissionService`, `RouterStore`-Scope-Ableitung | B1 (`teamspace`), A2 | I0 |
| `LIVE_EVENT_HANDLERS` | Multi `LiveEventHandler` (`eventType`, `handle(evt)`) | CE ab I5: Notification-Zähler | `LiveEventsService` | H6, F2 | I0 / I5 |
| `POWER_K_COMMANDS` | Multi `TPowerKCommandConfig[]` | CE-Befehle aus `power-k/config/**` | `PowerKCommandRegistry` | alle | I5 |
| `SEARCH_RESULT_RENDERERS` | Multi (`entityType` → Komponente) | CE-Typen der globalen Suche | Power-K-Suchseite | B6, G1 | I5 |
| `EDITOR_EXTENSIONS`, `EDITOR_BLOCKS`, `EDITOR_MENTION_TYPES`, `EDITOR_FLAGS`, `PAGE_PANE_EXTENSIONS` | Multi/Token | `{}` bzw. `["user_mention"]`, Flags `disabled:["ai"]` | Editor-Komponenten, Pages-Navigationspane | D1, D2, H1 (D9) | I2 / I4 |
| `PAGE_FLAGS` | Token `{ isMovePageEnabled, isPageSharingEnabled }` | `false`, `false` | Page-Aktionen, Page-Header | D2, (D8) | I4 |
| `PAGE_STORES` | Multi (`EPageStoreType` → Store-Token) | `PROJECT → ProjectPageStore` | `usePageStore`-Ersatz `injectPageStore(type)` | D1 (Workspace-/Wiki-Pages), B1 (Teamspace-Pages) | I4 |
| `PAGE_TREE` | Token `PageHierarchyClient` (`getChildren`, `getAncestors`) | flach (`parent_id` immer `null`) | Page-Liste, Breadcrumb | D2 | I4 |
| `FAVORITE_ENTITY_RENDERERS` | Multi (`entity_type` → Icon/Titel/Link) | CE-Typen (`project`, `cycle`, `module`, `view`, `page`, `folder`) | Favoriten-Sidebar | D1, B1 | I1 |
| `DUPLICATE_DETECTION` | Token Funktion `(title, projectId) => Signal<TDeDupeIssue[]>` | liefert `[]` | Issue-Modal | G1 (nicht gewählt) | I2 |
| `INTEGRATION_LINK_PREVIEWS` | Multi (`urlPattern` → Vorschau-Komponente) | keine | Link-Widget, Editor-Link-Hover | F1, F2 | I2 |

### 6.2 `ROUTE_EXTENSIONS` – Mechanik (Ersatz `routes/extended.ts` + `mergeRoutes`)

```ts
// libs/web/extensions/src/routes.ts
export type RouteKey = 'L0' | 'LALL' | 'LWS' | 'LPRJ' | 'LPD' | 'LSET' | 'LWSET' | 'LPSET' | 'LPSETD' | 'LPROF'
  | 'ADM_DASHBOARD' | 'SPC_ROOT';
export interface RouteExtension {
  parentKey: RouteKey;                       // Layout-Route, unter der eingehängt wird (data.routeKey)
  routes: Routes;
  /** 'before-dynamic' (Default): vor dem ersten Kind mit ':param'/'**' einfügen; 'end': ans Ende */
  position?: 'before-dynamic' | 'end';
  /** gleicher routeKey eines Kindes ⇒ Kinder werden rekursiv gemergt, Erweiterung gewinnt (wie helper.ts) */
}
export const ROUTE_EXTENSIONS = new InjectionToken<RouteExtension[][]>('ROUTE_EXTENSIONS');

// apps/web/src/app.config.ts – statt provideRouter(routes):
provideRouter([] /* Root leer */, withComponentInputBinding() /* … */),
{ provide: ROUTES, multi: true, useFactory: () => mergeRoutes(coreRoutes, (inject(ROUTE_EXTENSIONS, { optional: true }) ?? []).flat()) },
```

- Jede Layout-Route in `coreRoutes` trägt `data.routeKey` (Tabelle §4.4-Kürzel). `mergeRoutes` (Port von `WEB/app/routes/helper.ts`) arbeitet über `routeKey` statt `file`.
- Erweiterungsrouten unterliegen denselben Regeln (Lazy `loadComponent`, Reihenfolge, Trailing Slash, Titel). Der Routing-Contract-Test (§7.2) läuft mit allen registrierten Erweiterungen.
- Redirect-Erweiterungen (`extendedRedirectRoutes`) nutzen `parentKey: 'L0'`, `position: 'before-dynamic'`.

### 6.3 Store-Erweiterung per DI (Muster `Base*`-Klassen des Originals)

Das Original hält für EE-fähige Stores Basisklassen (`BaseCommandPaletteStore`, `BasePowerKStore`, `BaseAnalyticsStore`, `BaseUserPermissionStore`, `BaseWorkspaceRootStore`, `BaseProjectMemberStore`, `BaseTimeLineStore`, `ExtendedBasePage`). Ziel: Diese Klassen bleiben; die CE registriert sie unter dem CE-Token (`provideWebStoreOverrides()`):

```ts
export function provideWebStoreOverrides(): Provider[] {
  return [
    { provide: CommandPaletteStore, useClass: CommandPaletteStore },   // CommandPaletteStore extends BaseCommandPaletteStore
    { provide: PowerKStore, useClass: BasePowerKStore },
    { provide: AnalyticsStore, useClass: BaseAnalyticsStore },
    { provide: WorkspaceRootStore, useClass: BaseWorkspaceRootStore },
    { provide: TimeLineStore, useClass: TimeLineStore },
  ];
}
```

Ein Paket ersetzt einen Store, indem es eine Unterklasse mit **zusätzlichen** Feldern/Methoden registriert (`{ provide: WorkspaceRootStore, useClass: TeamspaceAwareWorkspaceRootStore }`). Bestehende Methoden dürfen nur erweitert, nicht in ihrer Semantik geändert werden (Store-Unit-Tests der CE laufen gegen die Unterklasse weiter).

### 6.4 Paketbezogene Andockstellen im Frontend (vollständig für die 17 🧱-Pakete)

| Paket | Andockstelle im Angular-Fundament (CE-Pflicht) | ab |
|---|---|---|
| **A1** Work-Item-Types & Custom Properties | `PROPERTY_RENDERERS`, `SPREADSHEET_COLUMNS`, `GROUP_BY_OPTIONS`, `FILTER_FIELDS`, `ISSUE_MODAL_CONTEXT`, `WORK_ITEM_PROPERTIES_LOADER`, `ACTIVITY_RENDERERS`, `SETTINGS_PAGES` (Projekt); Typ-Feld `type_id` ist in `TIssue` (`PKG/types/src/issues/issue.ts`) bereits vorhanden und wird in allen Formularen/Payloads durchgereicht (nie entfernt); `IssueTypeSwitcher` zeigt in CE nur den Identifier | I2 |
| **A2** Workspace-Types, Hierarchie, Roll-ups | wie A1; `PropertyRendererDefinition.scope?: ScopeLevel` (Feld vorhanden, CE ignoriert); `SCOPE_LEVELS` | I2 |
| **A9** Relationen & Abhängigkeiten | `RELATION_TYPES` (Relationstypen nie als Literal-Union im UI-Code vergleichen, nur über Registry), `TIMELINE_FLAGS`, Gantt-Dependency-Layer als leerer `<ng-container>`-Slot `ganttDependencyLayer` im Chart-Template | I2 |
| **A17** Governance States/Labels | Komponenten lesen States/Labels **nur** über `StateStore`-/`LabelStore`-Getter (`getStateById`, `getProjectStates`, `getProjectStateIds`, `getProjectLabels`, `getLabelById`, `workspaceStates`, `workspaceLabels`) – Lint-Regel verbietet Zugriff auf `stateMap`/`labelMap` außerhalb der Stores; Settings-Seiten über `SETTINGS_PAGES` (Workspace-Kategorie) | I1 |
| **B1** Teamspaces | `ROUTE_EXTENSIONS` (`LWS`, `LPRJ`), `SIDEBAR_ITEMS`, `RouterStore.teamspaceId`, Issue-Store-Typen `TEAM`, `TEAM_VIEW`, `TEAM_PROJECT_WORK_ITEMS` als Felder im `IssueRootStore`, Store-Typ-Auflösung (A08 §2.6.2) inkl. Teamspace-Zweigen, `GROUP_BY_OPTIONS` (`team_project`), `PERMISSION_EVALUATOR` + `SCOPE_LEVELS`, `PAGE_STORES`, `FAVORITE_ENTITY_RENDERERS` | I0 (Router) / I2 |
| **B6** Erweiterte Filter, PQL | Filter-Ausdrucksformat `TWorkItemFilterExpression` unverändert (einzige Wire-Form), `FILTER_OPERATORS`, `FILTER_FIELDS`, Slot `filterInputMode` in `WorkItemFiltersRow` (CE: nur Chip-Editor; PQL-Editor dockt als alternative Eingabe an), `SEARCH_RESULT_RENDERERS` | I2 |
| **C1** Workflows (nicht gewählt) | `WORKFLOW_GUARD` (alle Drop-/Create-/State-Select-Stellen fragen ihn), Fehlertoast für `invalid_state_transition` aus Backend wird generisch angezeigt | I2 |
| **C3** Automation-Engine (nicht gewählt) | Frontend: nur `SETTINGS_PAGES` und `ACTIVITY_RENDERERS` (Automation-Aktor in Activity); keine weitere Andockstelle nötig (Event-Katalog serverseitig) | I1 / I2 |
| **D1** Wiki & Collections | `ROUTE_EXTENSIONS` (`LWS`), `APP_RAIL_ENABLED`, `SIDEBAR_ITEMS`, `PAGE_STORES` (Workspace-Pages), `WorkspacePathsService.isWikiPath`, Editor-Tokens; Page-Komponenten erhalten den Store über `injectPageStore(type)` statt fest `ProjectPageStore` | I4 |
| **D2** Nested Pages | `PAGE_TREE`, `PAGE_FLAGS.isMovePageEnabled`, `ExtendedBasePage.asJSONExtended`, Realtime-Event `affectedPages` wird im `RealtimePageEventsService` durchgereicht (CE ignoriert) | I4 |
| **E3** IdP Group Sync | Frontend: `ADMIN_SETTINGS_PAGES`; Mitglieder-Listen zeigen Rollen aus API unverändert (Badge „synced“ dockt über `MEMBER_ROW_DECORATORS` an – Multi-Token, CE leer) | I1 |
| **E5** Rollenmodell | `PERMISSION_EVALUATOR`, `PermissionService` als **einzige** Rechteprüfung (Lint-Regel: keine Vergleiche mit `EUserPermissions`/Rollenzahlen außerhalb `libs/web/core/permissions`), Rollen-Dropdowns lesen Rollenliste aus `ROLE_OPTIONS`-Token (CE: Admin/Member/Guest aus `ROLE`-Konstanten), `SETTINGS_PAGES` | I0 |
| **F1** Integrations-Framework | `SETTINGS_PAGES` (Workspace „Integrations“), `WORK_ITEM_DETAIL_WIDGETS`, `INTEGRATION_LINK_PREVIEWS`, `ACTIVITY_RENDERERS`, `ROUTE_EXTENSIONS` (OAuth-Callback-Seiten unter `LWSET`) | I2 |
| **F2** Forgejo | wie F1 + `WORK_ITEM_ACTIONS`, `LIVE_EVENT_HANDLERS` (PR-/Check-Status), Profil-Tab „Verbundene Konten“ über `SETTINGS_PAGES` (Scope `profile`) | I2 |
| **G1** AI-Basis (nicht gewählt) | `DUPLICATE_DETECTION`, `EDITOR_FLAGS` (`ai`), `SEARCH_RESULT_RENDERERS`, `APP_RAIL_ENABLED` | I2 / I5 |
| **H1** OAuth-App-Plattform | `SETTINGS_PAGES` (Workspace „Apps“, Profil), `EDITOR_MENTION_TYPES` (App-Mentions), Anzeige von Bot-Nutzern (`is_bot`) im Member-/Avatar-Baustein als CE-Funktion (Feld existiert im Original) | I1 / I4 |
| **H6** Realtime-Event-Server | `LiveEventsService` + `LIVE_EVENT_HANDLERS`; Stores bieten für Fremd-Updates Methoden mit `shouldSync=false` (existieren im Original, z. B. `issueUpdate(…, shouldSync)`), Handler nutzen ausschließlich diese | I0 / I5 |

### 6.5 Skelett der Registry-Typen (`libs/web/extensions/src/`)

```ts
export interface SidebarItemDefinition extends IWorkspaceSidebarNavigationItem {  // key, labelTranslationKey, href, access, highlight
  scope: 'workspace-static' | 'workspace-dynamic' | 'project';
  icon: Type<unknown>;
  sortOrder: number;
  isVisible?: (ctx: ExtensionContext) => boolean;        // z. B. Projekt-Feature-Toggle
}
export interface SettingsPageDefinition {
  key: string; scope: 'workspace' | 'project' | 'profile';
  category: string;                                     // WORKSPACE_SETTINGS_CATEGORY | PROJECT_SETTINGS_CATEGORY | PROFILE_SETTINGS_CATEGORY
  i18nLabel: string; href: string;                      // relativ, mit "/" am Ende
  access: EUserPermissions[];                            // Prüfung über PermissionService
  highlight: (pathname: string, url: string) => boolean;
}
export interface PropertyRendererDefinition {
  propertyType: string;                                 // z. B. "TEXT", "OPTION" – vom Paket definiert
  contexts: ReadonlyArray<'list' | 'kanban' | 'spreadsheet' | 'peek' | 'detail' | 'modal' | 'filter-value'>;
  component: Type<PropertyRenderer>;
  scope?: ScopeLevel;
}
export interface PropertyRenderer {                     // Input-Vertrag jeder Renderer-Komponente
  workItemId: InputSignal<string>;
  propertyId: InputSignal<string>;
  value: InputSignal<unknown>;
  disabled: InputSignal<boolean>;
  valueChange: OutputEmitterRef<unknown>;
}
export interface ExtensionContext { workspaceSlug?: string; projectId?: string; teamspaceId?: string; pathname: string; }

export const SIDEBAR_ITEMS = new InjectionToken<SidebarItemDefinition[][]>('SIDEBAR_ITEMS');
export const SETTINGS_PAGES = new InjectionToken<SettingsPageDefinition[][]>('SETTINGS_PAGES');
export const PROPERTY_RENDERERS = new InjectionToken<PropertyRendererDefinition[][]>('PROPERTY_RENDERERS');
export const PERMISSION_EVALUATOR = new InjectionToken<PermissionEvaluator>('PERMISSION_EVALUATOR');
// … alle weiteren Tokens aus §6.1 analog; je Token ein Lese-Helfer injectRegistry(TOKEN) → flach + sortiert
```

**Tests der Andockstellen (Pflicht, 01 P7):** je Token ein Test „CE-Default liefert Original-Verhalten“ (z. B. Sidebar mit CE-Registry = DOM-Snapshot des Originals) und ein Test „Fake-Erweiterung erscheint an der richtigen Stelle“ (z. B. Fake-Route unter `LPRJ` vor `:param`-Kindern, Fake-Settings-Seite mit Rechteprüfung, Fake-Property-Renderer in Spreadsheet-Spalte).

---
