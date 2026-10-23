# 09 – UI-Parität 1:1 & Designsystem-Port (Tailwind/Propel/Blocks → Angular)

> **Status:** verbindlich für das Thema „Designsystem, UI-Parität, visuelle Verifikation“ (Dokument D09 aus Anhang A von `01-zielarchitektur-und-tech-stack.md`).
> **Rangfolge:** `00-grundsatzentscheidungen.md` (ADR-000 … ADR-009) > `01-zielarchitektur-und-tech-stack.md` (ADR-010 … ADR-052, insbesondere ADR-041, ADR-044, §7.17, Spike S10/S11) > **dieses Dokument (D09-ADR-01 ff.)** > eigene Präferenzen. Widerspricht etwas hier dem Rahmen, gilt der Rahmen.
> **Stand:** 23.10.2026. Original: Plane v1.4.2 CE, `@makeplane/propel` **0.7.3**, `@base-ui/react` 1.6.0, Tailwind CSS 4.1.17.
> **Zielrepository:** `funk.` (ADR-009). Alle Zielpfade sind relativ zur Wurzel von `funk.`. `01` §5.1 nennt noch den Arbeitstitel `plane-net/`; maßgeblich ist ADR-009 (`funk.`), die Baumstruktur aus `01` §5.1/§6.1 gilt unverändert darunter (`funk./frontend/…`, `funk./tools/…`, `funk./deploy/…`).
> **Sprache:** Fließtext Deutsch, Bezeichner Englisch.

**Abkürzungen** (wie in `01` und `A13a`): `PROPEL/` = `node_modules/@makeplane/propel/dist/` des npm-Tarballs `@makeplane/propel@0.7.3` (beziehbar per `npm pack @makeplane/propel@0.7.3`, Lizenz AGPL-3.0-only), `TWC/` = `packages/tailwind-config/`, `BLK/` = `packages/blocks/src/`, `UTL/` = `packages/utils/src/`, `WEB/` = `apps/web/`, `ADM/` = `apps/admin/`, `SPC/` = `apps/space/`. Zielkürzel: `FE/` = `funk./frontend/`, `PRP/` = `FE/libs/shared/propel/src/`, `BLKT/` = `FE/libs/shared/blocks/src/`, `TWT/` = `FE/libs/shared/tailwind-config/`. Analyse-Dokumente: `A13a` = `migration/analysis/13a-designsystem-ui-tokens.md`, `A08`, `A09`, `A10a`, `A10b`, `A11`, `A12`, `A13b` analog; `F20` = `migration/features/20-paid-spuren-im-repo.md`, `F30` = `migration/features/30-paid-auswahlliste.md`.

## Inhaltsverzeichnis

1. [Ziel & Scope](#1-ziel--scope)
2. [Entscheidungen (D09-ADR-01 ff.)](#2-entscheidungen-d09-adr-01-ff)
3. [Detaildesign](#3-detaildesign)
4. [Vollständige Mapping-Tabellen Original → Ziel](#4-vollständige-mapping-tabellen-original--ziel)
5. [Code-Skelette](#5-code-skelette)
6. [Erweiterungspunkte für Bezahl-Pakete](#6-erweiterungspunkte-für-bezahl-pakete)
7. [Akzeptanzkriterien & Tests](#7-akzeptanzkriterien--tests)
8. [Risiken & offene Punkte](#8-risiken--offene-punkte)
9. [Abhängigkeiten zu anderen Dokumenten (02–16)](#9-abhängigkeiten-zu-anderen-dokumenten-0216)

---

## 1. Ziel & Scope

### 1.1 Ziel

Die drei Angular-Apps `web`, `admin` und `space` sollen **pixel- und verhaltensgleich** zum Original aussehen (ADR-005). Erreicht wird das nicht über „Nachbauen nach Augenmaß“, sondern über drei harte Gleichheiten:

1. **Gleiches CSS:** Dieselben Quell-CSS-Dateien (Propel-Tokens, `packages/tailwind-config`, App-Globals) werden mit **demselben Compiler** (Tailwind 4.1.17) übersetzt. Das kompilierte CSS von Original und Ziel muss gleich sein (CSS-Diff-Test, §3.2.5).
2. **Gleiches DOM:** Jede Komponente rendert dieselben Elemente, Klassen, `data-*`- und ARIA-Attribute und CSS-Variablen wie Propel/Base UI bzw. Blocks (DOM-Vertrag, §3.4). Gemessen wird das über normalisierte DOM-Snapshots (§3.14.6).
3. **Gleiches Verhalten:** Tastatur, Fokus, Positionierung, Öffnen und Schließen, Animationen und Timings folgen dem Original (Zustandsvertrag aus `A13a` §2.20, Verhaltenstabellen aus `A13a` §3.8/§3.9).

Gleiches CSS und gleiches DOM ergeben gleiche Pixel. Der Pixelvergleich (§3.14.5) bestätigt das nur noch.

### 1.2 Scope

| Im Scope (dieses Dokument) | Quelle (IST) | Nicht im Scope (zuständig) |
|---|---|---|
| Tailwind-v4-Pipeline, Übernahme von `TWC/index.css`, `PROPEL/styles/{propel,variables,animations}.css`, `WEB/styles/{globals,emoji,power-k}.css`, `ADM/styles/globals.css`, `SPC/styles/globals.css` | `A13a` §2.1–§2.15 | Editor-CSS `packages/editor/src/styles/*` (nur als Import-Position hier; Inhalt → `10-editor-angular.md`) |
| Port **aller 68** Propel-Komponenten, **aller 57** Elemente, `base/`, `hooks/`, `internal/` (Rezepte), `state-icons/`, `icons` (919) | `A13a` §2.20–§2.25 | – |
| Port **aller** `packages/blocks`-Module (24 Subpath-Exporte, 137 TSX-Dateien + Logik-Dateien) | `A13a` §2.26–§2.27, `BLK/**` | Fachkomponenten in `apps/web/components/**` (→ `08-frontend-angular-architektur.md`, Domänen-Libs) |
| Icons (Propel, Blocks, Web-Icons, lucide 0.469.0 und 1.34.0, Material Symbols), Schriften, Illustrationen, Raster-Assets aus `apps/*/public` und `apps/*/app/assets` | `A13a` §2.16, §2.25–§2.31; Dateisystem | PDF-Schriften (`WEB/app/assets/fonts/inter/*.ttf`) → `07-realtime-kollaboration-dokumente.md` (ADR-029) |
| Theme-Laufzeit (Light, Dark, HC, Custom, System), `cn()`, Theme-Generator | `A13a` §2.17–§2.18, §3.1–§3.7 | Persistenz `Profile.theme` (Endpunkt) → `03`/`04` |
| Ersatz der Upsell-Elemente (ADR-001) | `F20` §5 (U1–U22) | fachliche Umsetzung der Bezahl-Features (W1–W9) |
| Optik des Keycloak-Login-Themes (CSS-Herkunft, DOM-Vorlage) | ADR-008, S7 | Realm, Clients, FreeMarker-Logik → `05-auth-sicherheit-berechtigungen.md` |
| Verifikationsverfahren: Referenzumgebung, Screenshot-Katalog, Pixel-Diff, DOM-/A11y-Snapshots, Komponenten-Katalog (Galerie), Abnahme pro Screen | ADR-005, ADR-048, S10, S11 | Gesamt-Teststrategie, Contract-Harness für JSON → `15-teststrategie-qualitaet-paritaet.md` |
| Chart-Bausteine (DOM-Vertrag der sechs Blocks-Charts) | `A13a` §2.26, ADR-044 | Fachdiagramme (Burndown, Analytics) → `08`, Spike S6 |
| Gestaltungsregeln für spätere Bezahl-Screens ohne Original-Referenz (§6) | `F30`, `A13a` §1.3 | Fachdesign der Pakete (→ `16-erweiterungspunkte-bezahl-features.md`, später je Welle) |

### 1.3 Abgedeckte CE-Features

| CE-ID | Name (Katalog) | Hier geregelt durch |
|---|---|---|
| CE-I18N-005 | Theme-System und Theme-Varianten | D09-ADR-09, §3.9 |
| CE-I18N-006 | Theme-Auswahl und Server-Persistenz | §3.9 (Laufzeit), Persistenz → `03` |
| CE-I18N-007 | Custom Theme | §3.9.4 |
| CE-I18N-008 | High-Contrast-Themes | §3.9, Token-CSS 1:1 |
| CE-I18N-009 | Farb-Token-System | D09-ADR-01, §3.2 |
| CE-I18N-010 | Editor-Farbpalette | nur CSS-Import-Reihenfolge (§3.2.2); Inhalt → `10` |
| CE-I18N-011 | Typografie | D09-ADR-01, §3.8 |
| CE-I18N-012 | Gebündelte Schriften (Airgap) | D09-ADR-08, §3.8.1 |
| CE-I18N-013 | Icon-System | D09-ADR-07, §3.7, §4.6 |
| CE-I18N-014 | Status-, Zyklus-, Modul- und Prioritäts-Icons | §4.5, §4.8 |
| CE-I18N-015 | Datei-Typ-Icons und Locked-Pill | §4.9 |
| CE-I18N-016 | Logo-Picker (Emoji, Lucide, Material) | §4.7 (`emoji-icon-picker`), D09-ADR-08 |
| CE-I18N-017 | Emoji-Reaktions-Komponenten | §4.7 (`emoji-reaction`) |
| CE-I18N-018 | Empty-State-Illustrationen und theme-abhängige Assets | §3.8.3, §4.7, §4.11 |
| CE-I18N-019 | Propel-Komponentenbibliothek und Varianten | §4.2–§4.5 |
| CE-I18N-020 | Blocks-Composites | §4.7 |
| CE-I18N-021 | Toast-Benachrichtigungen | §3.10 |
| CE-I18N-022 | Diagramm-Bausteine und Farbpaletten | §3.12, §4.7 (`charts/*`) |
| CE-I18N-023 | Animationen | §3.4.3 |
| CE-I18N-024 | Maßsystem, Elevation und Scrollbars | Token-CSS 1:1, `scroll-area` §4.2 |
| CE-I18N-025 | Avatare und Farbwähler | §4.2 (`avatar`, `avatar-group`), §4.7 (`common/color-*`) |
| CE-I18N-026 | Lade-Indikatoren und Navigations-Progressbar | §4.2 (`logo-spinner`), §4.7 (`spinner`, `skeleton`), §3.2 (bprogress-CSS) |
| CE-UIX-001 | Seiten-Header und Breadcrumbs | §4.7 (`layout`, `breadcrumb`) |
| CE-UIX-002 | Leerzustände und Skeletons | §4.7 (`empty-state`, `skeleton`) |
| CE-UIX-003 | Globale Modal-Hosts | §3.5 (Portal-Schicht), Hosts selbst → `08` |
| CE-UIX-004 | Dialog- und Dropdown-Verhalten | §3.5, §4.2 (`dialog`, `menu`, `popover`, `combobox`) |
| CE-UIX-005 | Tab-Reihenfolge in Formularen | §3.6, Test `property-select/tab-index` |
| CE-UIX-009 | Image-Picker und Uploads mit Fortschritt | Assets `cover-images` §4.11, `linear-progress` |
| CE-UIX-010 | 404-, Fehler- und Zugriffsseiten (Web) | Assets §4.11, Screenshot-Katalog §3.14 |
| CE-UIX-013 | Link-Icons und URL-Erkennung | Icons §4.6 |
| CE-LV-042 | Empty-States der Layouts | §4.7, §4.11 |
| CE-WI-006 | Toast-Aktionen nach dem Erstellen | §3.10 |
| CE-INST-012 | Konto-Menü mit Theme-Umschaltung (God Mode) | §3.9 (Admin: nur light/dark/system) |
| CE-SPACE-032 | „Powered by Plane Publish“-Badge | §4.11 (Logos), Katalog Space |
| CE-AUTH-001 (angepasst) | Sign-in-Seite → Keycloak-Login-Theme | D09-ADR-14, §3.13 |

Alle übrigen CE-Screens (CE-WS, CE-PRJ, CE-WI, CE-LV, CE-CYC, CE-MOD, CE-INT, CE-PAGE, CE-HOME, CE-NOTIF, CE-ANA, CE-SRCH, CE-PROF, CE-INST, CE-SPACE) konsumieren das Designsystem. Für sie liefert dieses Dokument das **Verifikationsverfahren** (Screenshot-Katalog, §3.14, Katalog-Einträge §4.14).

### 1.4 Inkrement-Zuordnung (welcher Teil wird wann gebraucht)

Grundsatz: Ein Baustein wird in dem Inkrement **fertig** (Code + Galerie-Story + DOM-/Visual-Test grün), in dem der erste abnahmerelevante Screen ihn braucht. Komponenten, die das Original in keiner App direkt importiert (`A13a` §2.30), werden spätestens in I7 nachgezogen, damit der Komponenten-Katalog vollständig ist; ein Bezahl-Paket darf sie vorziehen.

| Inkrement | Was aus D09 fertig sein muss (abnahmerelevant) | Gate |
|---|---|---|
| **I0 Walking Skeleton** | Tailwind-Pipeline + CSS 1:1 + CSS-Diff-Test (§3.2); Schriften, Favicons, Manifeste; `ThemeService` + Inline-Script (Light/Dark/System); `cn()`; Icon-Codegen (Propel 919, lucide ×2, Blocks-Icons); Präsenz-/Portal-/Positionierungs-Schicht (§3.4, §3.5); Propel: `button`, `icon-button`, `icon`, `tooltip`, `menu`, `input`, `input-field`, `field`, `text-area`, `avatar`, `workspace-avatar`, `scroll-area`, `collapsible`, `breadcrumb`, `dialog`, `combobox`, `popover`, `tabs`, `toast`, `shortcut`, `separator`, `logo-spinner`; Blocks: `layout`, `breadcrumb`, `select` (Engine-Kern), `toast`, `skeleton`, `spinner`, `portal`, `utils`, `types`, `icons`; Keycloak-Login-Theme-CSS (§3.13); Galerie Original + Angular (Gerüst, Leit-Komponenten); Referenzumgebung + Screenshot-Katalog für 5 Seiten (S11) | **S10** (10 Leit-Komponenten + Workspace-Shell, DOM gleich, Visual-Diff ≤ 0,1 %), **S11** |
| **I1 Workspace, Projekte, Konto** | Propel: `alert-dialog`, `switch`, `checkbox`, `checkbox-field`, `radio`, `badge`, `banner`, `anchor-button`, `avatar-group`, `table`, `select`, `pill`, `context-menu`, `text-area-field`, `toggle`; Blocks: `dialog` (ConfirmDialog), `empty-state` (+ 59 Illustrationen), `emoji-icon-picker` (inkl. offline Emojibase), `common` (ColorPicker, ColorSwatchPicker, FavoriteStar, DragHandle, DropIndicator, Sortable), `context-menu`, `card`, `pill-button`, `property-select/member-select`, `virtual-list`; Theme: HC-Varianten, Custom-Theme, Theme-Wechsel mit Reload; Raster-Assets (Empty-States, Onboarding, Cover-Images) | Katalog-Einträge I1 grün (§7) |
| **I2 Work Items & Layouts** | Propel: `calendar`, `circular-progress`, `linear-progress`, `suggestion-menu`, `toolbar`, `preview-card`; Blocks: alle `property-select/*`, `emoji-reaction`, Select-Varianten `pill-*`, `icon-*`, `table-cell`, `search-input`, `avatar-group-*`; State-/Priority-/Cycle-/Module-Icons; Web-Icons (Attachment) | Katalog I2 |
| **I3 Planung** | Blocks `charts/*` (6) nach S6, Burndown-Bausteine (→ `08`) | **S6** |
| **I4 Pages & Realtime** | Editor-Hüllen nutzen `toolbar`, `menu`, `popover`, `suggestion-menu`, `preview-card` (bereits fertig); Page-Lock-Animationen aus `WEB/styles/globals.css` | **S5** (Editor-Visual ≤ 0,5 %) |
| **I5 Überblick** | `power-k.css` + `cmdk`-Attribut-DOM (Komponente → `08`), `animate-notification-bell-ring`, Stickies-Optik | Katalog I5 |
| **I6 Außenwirkung & Administration** | Admin- und Space-Kataloge vollständig (Admin: light/dark; Space: light/dark), OG-Bilder | Katalog I6 |
| **I7 Härtung** | Restliche, im Original nicht importierte Propel-Komponenten (`accordion`, `autocomplete`, `autocomplete-field`, `button-group`, `checkbox-group`, `checkbox-group-field`, `combobox-field`, `csp-provider`, `direction-provider`, `drawer`, `expandable-search`, `fieldset`, `form`, `icon-split-button`, `list`, `navigation-menu`, `number-field`, `otp-field`, `pagination`, `radio-group-field`, `select-field`, `skeleton`, `slider`, `split-button`, `switch-field`); Browser-Matrix Firefox/WebKit; Abnahme **aller** Katalog-Einträge | Gesamtabnahme ADR-005 |
| **W1…W9** | Gestaltungsregeln §6.2, Erweiterungspunkte §6.1; neue Screens ohne Original-Referenz werden gegen die Screen-Schablonen (§6.3) abgenommen | je Welle |

---

## 2. Entscheidungen (D09-ADR-01 ff.)

| ADR | Belang | Entscheidung | Alternativen (verworfen) | Begründung | ab |
|---|---|---|---|---|---|
| **D09-ADR-01** | CSS-Quelle | **Original-CSS wird byte-identisch vendored** (Dateiliste §4.1) und nur über `@import`/`@source`-Pfade angepasst. Compiler exakt `tailwindcss@4.1.17` + `@tailwindcss/postcss@4.1.17` + `@tailwindcss/typography@0.5.19` über Angular-Application-Builder (`.postcssrc.json`). Jede Änderung an vendored CSS ist verboten; Abweichungen nur als zusätzliche Datei `FE/libs/shared/tailwind-config/overrides.css` mit Eintrag in `ui-deviations.yaml` | Tokens neu als SCSS/CSS-Custom-Properties schreiben; neuere Tailwind-4.x | Einzige verlässliche Quelle aller Tokens; die Tailwind-Version bestimmt die erzeugten Utilities (inkl. der Lücken aus `A13a` E-21) | I0 |
| **D09-ADR-02** | Klassenquelle (`@source`) | Tailwind scannt (a) alle Angular-Quellen `FE/{apps,libs}/**/*.{html,ts}` und (b) eine **generierte, eingecheckte Klassenliste** `TWT/propel-dist-classes.txt`, die `tools/propel-port/extract-classes.mjs` aus allen JS-Dateien von `PROPEL/` erzeugt (entspricht `@source "../"` in `propel.css`). Der Tarball wird nur im Werkzeug (Dev, offline gespiegelt, SHA-512 gepinnt) gelesen, nicht ausgeliefert | `@makeplane/propel` als Laufzeit-/Build-Abhängigkeit behalten; nur Angular-Quellen scannen | (b) garantiert denselben Utility-Satz wie im Original, auch wenn Angular-Templates Klassen anders zusammensetzen; keine React-Abhängigkeit im Build | I0 |
| **D09-ADR-03** | Komponentenmodell Angular | **Standalone-Komponenten, `ChangeDetectionStrategy.OnPush`, `ViewEncapsulation.None`, keine Komponenten-Styles** (keine `styles`/`styleUrl`). Primitive mit eigenem Wurzel-Element des Originals = **Attribut-Selektor** auf dem nativen Element (`button[plButton]`, `div[plMenuItem]`); Komposita ohne eigenes Wurzel-Element = Element-Selektor mit `:host { display: contents }` **und** Attribut `data-pl-host` (für die DOM-Normalisierung); Selektor-Präfix `pl` (Rahmen §7.1/§7.17) | Element-Selektoren mit Host-Box; `ViewEncapsulation.Emulated`; Angular Material | Nur so bleiben DOM-Tiefe, `:first-child`, `space-x-*`, `divide-*`, Flex/Grid-Kinder identisch (`A13a` F-02/F-03) | I0 |
| **D09-ADR-04** | Zwei Schichten wie Propel | **`elements` → Attribut-Direktiven** (nur Klassen aus `cva` + statische `data-*`), **`components` → Komponenten**, die das Verhalten (Headless-Schicht, §3.4/§3.5) mit der Element-Direktive komponieren. Apps dürfen beide Schichten nutzen (Original: 25 Importe aus `elements/button`, `elements/combobox` 4 usw.) | Nur eine Schicht | Gleiche Wiederverwendbarkeit wie im Original (Blocks nutzt Elemente direkt, z. B. Combobox-Elemente in der Select-Engine) | I0 |
| **D09-ADR-05** | Varianten | **`class-variance-authority` 0.7.1** (framework-frei) mit **maschinell übertragenen** `variants.ts` (57 Elemente) und `internal/*.ts` (Rezepte): `tools/propel-port/port-variants.mjs` liest `PROPEL/elements/*/variants.js` und `PROPEL/internal/*.js` und erzeugt TS-Dateien mit wortgleichen Klassenstrings; Hand-Edits sind verboten (Header `// GENERATED – do not edit`), Unit-Test vergleicht die Ausgabe aller Varianten-Kombinationen mit dem Original (Node, `import()` des Original-JS) | Klassen von Hand abschreiben; Tailwind-`@apply`-Komponentenklassen | Klassenstrings sind Daten; maschinelle Übertragung ist fehlerfrei und wiederholbar bei Propel-Updates | I0 |
| **D09-ADR-06** | `cn()` | `UTL/common.ts` (`cn` = `twMerge(clsx(…))` mit identischer `extendTailwindMerge`-Konfiguration) wird **1:1 kopiert** nach `FE/libs/shared/utils/src/common.ts` (Teil der 1:1-Kopie von `packages/utils`, `01` §6.2); `tailwind-merge` **3.4.0** exakt, `clsx` 2.1.x. Propel-Port nutzt wie das Original `cx` (kein Merge), Blocks-Port `cn()` | Eigener Merger; neuere tailwind-merge-Version | Ein anderer Merger lässt andere Klassen überleben (`A13a` §3.7, F-05) | I0 |
| **D09-ADR-07** | Icons | **Codegen** aus den Original-Paketen in **tree-shakable Konstanten** (`PlIconDef` = SVG-Knotenbaum als JSON-AST) + **eine** Render-Komponente `svg[plIcon]`, die die Knoten per `Renderer2` im SVG-Namespace erzeugt (kein `innerHTML`, Trusted-Types-/CSP-fest). Quellen: `PROPEL/icons/**` (919), `PROPEL/internal/solid-icons/*`, `lucide@1.34.0` (Propel-intern), `lucide@0.469.0` (Apps/Blocks + 157 persistierte Namen), `BLK/icons/**`, `WEB/components/icons/**` (SVG-Teil). Namen 1:1 (`PaletteOutline`) | 919 einzelne Angular-Komponenten mit Template; SVG-Sprite mit `<use>`; `lucide-angular` | DOM bleibt `<svg …>` wie im Original (kein Host-Element), Bundle enthält nur genutzte Icons, ein Generator für alle Quellen | I0 |
| **D09-ADR-08** | Schriften, Emoji-Daten, Assets | Alles **gebündelt** (ADR-004): `@fontsource-variable/inter` 5.2.8, `@fontsource/ibm-plex-mono` 5.2.7, `@fontsource/material-symbols-rounded` 5.2.30 über `angular.json`-`styles`; Inter-Latin-woff2 als Asset mit festem Namen + `<link rel="preload">`; **Emojibase-Daten** lokal als Asset (Korrektur von `A13a` E-22); Raster-/SVG-Assets aus `apps/*/app/assets` und `apps/*/public` **unverändert** (Liste §4.11) | CDN-Laden; Neuzeichnen | Airgapped-Pflicht, Pixelgleichheit | I0 (Fonts), I1 (Emoji, Illustrationen) |
| **D09-ADR-09** | Theme-Laufzeit | `ThemeService` (Signals `theme`, `resolvedTheme`, `systemTheme`) + **Inline-Script** in jeder `index.html` mit der Logik von `next-themes` 0.4.6 (Schlüssel `localStorage["theme"]`, Attribut `data-theme` an `<html>`, `style.color-scheme` für `light`/`dark`, `matchMedia`-Listener, `storage`-Event); Theme-Listen je App wie Original (Web 5 + system, Admin/Space `light`/`dark` + system); Custom-Theme über 1:1 kopiertes `UTL/theme/*` | `prefers-color-scheme`-Media-Queries; Angular-Material-Theming | `A13a` §3.1–§3.5, F-06; Edge-Cases E-01…E-05, E-14, E-29…E-33 werden **nachgebaut** | I0 (L/D/System), I1 (HC, Custom) |
| **D09-ADR-10** | Headless-Unterbau | **Angular Aria 22.x** für Muster mit passender Semantik (Tabs, Toolbar, Listbox/Combobox-Tastaturmodell, Menu-Tastaturmodell, Accordion), **Angular CDK** nur für a11y (`FocusTrap`, `FocusKeyManager`, `ActiveDescendantKeyManager`, `LiveAnnouncer`, `Directionality`, `InteractivityChecker`), **eigene Schicht** `PRP/headless/` für alles, was Base UI zusätzlich festlegt: Zustandsattribute, Präsenz/Transitions, Portal, Dismissal, Hover-Intent, Delay-Gruppen, Scroll-Lock. **Kein** CDK-Overlay-Container, **keine** CDK-Positionierung | Angular Material; reines CDK; Spartan/ng-primitives; vollständiger Eigenbau | Base UI legt DOM/Attribute fest, die keine Angular-Bibliothek 1:1 erzeugt; Aria/CDK liefern geprüfte Tastatur- und Fokuslogik, die Schicht ergänzt den Vertrag. Fallback bei Lücken (S10, `A13a` O-09): Eigenbau auf CDK a11y | I0 |
| **D09-ADR-11** | Positionierung | **`@floating-ui/dom` 1.7.x** mit Middleware-Kette wie Base UI 1.6.0 (`offset` → `flip` → `shift` → `size` (setzt `--available-width/-height`, `--anchor-width/-height`) → `arrow` → `hide`), `autoUpdate`, Strategie `absolute` (Default `positionMethod`) bzw. `fixed`; CSS-Variable `--transform-origin` und Attribute `data-side`, `data-align`, `data-anchor-hidden` wie Base UI | CDK `FlexibleConnectedPositionStrategy` | Base UI nutzt Floating UI; nur gleiche Logik ergibt gleiche Flip-/Shift-/Size-Ergebnisse (`A13a` §5.3) | I0 |
| **D09-ADR-12** | Präsenz & Animationen | Eigener `PresenceController` (Äquivalent zu Base UIs `useTransitionStatus`/`useOpenChangeComplete`): setzt beim Öffnen einen Frame lang `data-starting-style`, beim Schließen `data-ending-style` und entfernt das Element nach `animationend`/`transitionend` aller laufenden Animationen (`element.getAnimations()`), Fallback-Timeout wie Original (Spinner 250 ms); **keine** `@angular/animations` | `@angular/animations`; `animate.enter/leave` (Angular 20+) | Propel stylt Übergänge ausschließlich per CSS über diese Attribute (`data-starting-style` 22×, `data-ending-style` 38×) | I0 |
| **D09-ADR-13** | Originalfehler in der Optik | **1:1 nachbauen**, nicht reparieren: tote Klassen bleiben im Markup (`A13a` §2.32), Edge-Cases E-01…E-34 gemäß Spalte „Empfehlung“ von `A13a` §3.10. Einzige Korrekturen: E-22 (Emoji-CDN → lokal, ADR-004), Upsell-Ersatz (ADR-001, D09-ADR-15), Login-Varianten (ADR-008). Jede Abweichung steht in `FE/apps/e2e/visual/ui-deviations.yaml` | Fehler korrigieren | ADR-005; reparierte Klassen erzeugen sichtbare Abweichungen; Korrekturen später als eigene Change-Requests | I0 |
| **D09-ADR-14** | Keycloak-Login-Theme | Das Login-Theme `deploy/keycloak/themes/plane/` bekommt sein CSS aus **demselben Tailwind-Build** (Build-Target `keycloak-theme` im Angular-Workspace, Ausgabe `deploy/keycloak/themes/plane/login/resources/css/plane.css`); FreeMarker-Templates bilden das DOM der Original-Sign-in-Seite (`WEB/app/(home)/page.tsx` + `BLK/auth/*`) nach; Fonts aus demselben Paket | Keycloakify (React, Build-Zeit-Node, Fallback laut S7); eigenes CSS | Ein Token-System für App und Login; Visual-Diff ≤ 1 % (S7) | I0 |
| **D09-ADR-15** | Upsell-Elemente (ADR-001) | Upgrade-Badges, Upgrade-Modals, Billing-Seite, „Talk to Sales“, Pro-Icons **entfallen ersatzlos**; wo ein Upsell-Screen eine Funktion bewirbt, erscheint die echte Funktion **erst mit ihrem Paket** (bis dahin ist die Route nicht registriert, Rahmen §7.19); das Sidebar-Editions-Badge wird zu einem nicht interaktiven Versions-Badge. Vollständige Tabelle §4.12 | Upsell-Screens als Platzhalter behalten | ADR-001; keine Platzhalter in abgenommenen Inkrementen (`01` §7.19) | I0 |
| **D09-ADR-16** | Referenz für Pixel und DOM | **Das laufende Original** ist die Referenz: (a) Seiten-Screenshots aus einer per Docker Compose gestarteten Original-Instanz mit deterministischem Seed (`Plane.Tools.ParityHarness`, S11), (b) Komponenten-Screenshots und DOM-Verträge aus einer **Referenz-Galerie** (`funk./tools/reference-gallery/`, React 19 + `@makeplane/propel@0.7.3` + `packages/blocks` aus dem Original-Repo, nur Dev). Beide Galerien lesen **dieselben Story-Definitionen** (`funk./tools/gallery-stories/*.stories.json`) | Figma; handgemachte Referenzbilder; Storybook | Objektiv, wiederholbar, deckt alle Varianten-Kombinationen ab | I0 |
| **D09-ADR-17** | Visueller Vergleich | **Playwright** (`@playwright/test` 1.5x, ein gepinntes Container-Image für Referenz- **und** Ziel-Aufnahmen, Chromium als Gate, Firefox/WebKit ab I7) mit `toHaveScreenshot` gegen importierte Original-Baselines; zusätzlich normalisierter **DOM-Snapshot-Vergleich** und **ARIA-Snapshot-Vergleich** (`locator.ariaSnapshot()`), axe-core als Ratchet. Schwellwerte §3.14.5 | Percy/Chromatic (SaaS, ADR-004); BackstopJS; reine Pixel-Diffs | Lokal/airgapped, Standard-Tooling aus ADR-048; DOM-/ARIA-Vergleich findet Ursachen statt Symptome | I0 |
| **D09-ADR-18** | Charts | Gemäß ADR-044: D3-Module + Angular-SVG; DOM-Vertrag = SVG-Markup und Klassen von `recharts` 2.15.4 in den sechs Blocks-Charts (`recharts-*`-Klassen, Gruppenstruktur), Referenzbilder aus der Referenz-Galerie (Stories mit festen Datensätzen) | ECharts | Parität; S6 entscheidet | I3 |
| **D09-ADR-19** | Gestaltung neuer Bezahl-Screens ohne Original-Referenz | Neue Screens werden **ausschließlich** aus vorhandenen Propel-/Blocks-Bausteinen, vorhandenen Tokens, vorhandenen Icons und Illustrationen und den vorhandenen EE-i18n-Schlüsseln komponiert und gegen **Screen-Schablonen** (§6.3) abgenommen. Neue Tokens, neue Farben und neue Basiskomponenten nur per ADR-Änderung | Freies Design je Paket | Konsistenz mit dem 1:1-Rest, kein Designsystem-Drift (§6.2) | W1 |

---
## 3. Detaildesign

### 3.1 Bibliotheken und Werkzeuge in `funk.`

Die Ablage folgt `01` §6.1. Ergänzt werden nur die Unterordner, die dieses Dokument festlegt.

```text
funk./
├── frontend/
│   ├── .postcssrc.json                         # { "plugins": { "@tailwindcss/postcss": {} } }  (wie TWC/postcss.config.js)
│   ├── apps/
│   │   ├── web/src/
│   │   │   ├── index.html                      # Theme-Inline-Script (§5.8), Font-Preload, Favicons, Manifeste
│   │   │   ├── styles.css                      # Einstieg = Kopie von WEB/styles/globals.css (nur Importzeilen umgeschrieben)
│   │   │   ├── styles/emoji.css                # 1:1 WEB/styles/emoji.css
│   │   │   ├── styles/power-k.css              # 1:1 WEB/styles/power-k.css
│   │   │   └── assets/                         # 1:1 WEB/app/assets/** (ohne fonts/inter → D07), public/** (§4.11)
│   │   ├── admin/src/{index.html,styles.css,assets/}   # styles.css = Kopie ADM/styles/globals.css
│   │   ├── space/src/{index.html,styles.css,assets/}   # styles.css = Kopie SPC/styles/globals.css
│   │   ├── gallery/                            # Angular-Komponenten-Katalog (nur Dev/CI, nicht ausgeliefert), base href "/gallery/"
│   │   ├── keycloak-theme/                     # Build-Target: erzeugt deploy/keycloak/themes/plane/login/resources/css/plane.css
│   │   └── e2e/
│   │       ├── visual/                         # Screenshot-Katalog, Baselines, Diff-Reports (§3.14)
│   │       │   ├── catalog/{web,admin,space,gallery}.catalog.yaml
│   │       │   ├── baselines/<app>/<entry-id>/<theme>-<viewport>.png   # aus dem Original importiert (Git LFS)
│   │       │   ├── dom-contracts/<app>/<entry-id>.dom.html             # normalisiertes Original-DOM
│   │       │   ├── aria-contracts/<app>/<entry-id>.aria.yml            # Original-ARIA-Snapshot
│   │       │   ├── ui-deviations.yaml                                  # alle genehmigten Abweichungen (D09-ADR-13)
│   │       │   └── specs/*.visual.spec.ts
│   │       └── a11y/                           # axe-Ratchet (§3.14.7)
│   └── libs/shared/
│       ├── tailwind-config/                    # TWT/
│       │   ├── index.css                       # 1:1 TWC/index.css (Import-/Source-Zeilen umgeschrieben)
│       │   ├── propel-styles/{propel,variables,animations}.css   # 1:1 PROPEL/styles/*.css
│       │   ├── propel-dist-classes.txt         # generiert (D09-ADR-02)
│       │   ├── overrides.css                   # leer; nur mit Eintrag in ui-deviations.yaml befüllbar
│       │   └── VENDORED.md                     # Herkunft, SHA-256 je Datei, umgeschriebene Zeilen
│       ├── propel/src/                         # PRP/
│       │   ├── internal/                       # generierte Rezepte (*.ts aus PROPEL/internal/*.js) + handgeschriebene Logik (fit-side, avatar-shared …)
│       │   ├── elements/<name>/                # 57 Ordner: variants.ts (generiert) + *.directive.ts
│       │   ├── components/<name>/              # 68 Ordner: *.component.ts/.html, public-api.ts
│       │   ├── base/composite/                 # PlComposite, PlCompositeItem
│       │   ├── hooks/                          # controllable-state.ts (model()-Hilfen)
│       │   ├── headless/                       # §3.4/§3.5: state-attrs, presence, portal, floating, dismiss, focus, delay-group, scroll-lock, ids
│       │   ├── state-icons/                    # PlStateGroupIcon, PlStartedGroupIcon, PlUnstartedGroupIcon
│       │   ├── icons/                          # generiert: <kategorie>/<kebab-name>.ts (PlIconDef-Konstanten), index.ts
│       │   └── styles/ → ../../tailwind-config/propel-styles (nur Verweis, keine Kopie)
│       ├── blocks/src/                         # BLKT/ – Ordner 1:1 wie BLK/ (auth entfällt, §4.7)
│       ├── icons-lucide/src/{v0469,v134}/      # generierte PlIconDef-Konstanten (lucide@0.469.0 / lucide@1.34.0)
│       └── theme/src/                          # ThemeService, THEME_INLINE_SCRIPT, theme-asset-helpers.ts
└── tools/
    ├── propel-port/                            # Node-Werkzeuge (nur Dev, offline-fähig über gespiegelte npm-Registry)
    │   ├── fetch-propel.mjs                    # npm pack @makeplane/propel@0.7.3, SHA-512-Prüfung, Entpacken nach tools/propel-port/.cache/
    │   ├── vendor-css.mjs                      # kopiert CSS, schreibt nur Import-/Source-Zeilen um, schreibt VENDORED.md
    │   ├── extract-classes.mjs                 # PROPEL/**/*.js → propel-dist-classes.txt
    │   ├── port-variants.mjs                   # PROPEL/elements/*/variants.js + internal/*.js → *.ts
    │   ├── port-icons.mjs                      # Propel-, Solid-, lucide-, Blocks-, Web-Icons → PlIconDef
    │   └── port-illustrations.mjs              # BLK/empty-state/assets/**/*.tsx → PlIllustrationDef (59)
    ├── reference-gallery/                      # React-19-App (Vite) gegen Original-Propel/Blocks (D09-ADR-16)
    ├── gallery-stories/*.stories.json          # gemeinsame Story-Definitionen (Original- und Angular-Galerie)
    └── visual/
        ├── capture-reference.ts                # Playwright: Baselines aus Original-Instanz + Referenz-Galerie
        ├── dom-normalize.ts                    # gemeinsame Normalisierung (§3.14.6)
        └── report/                             # HTML-Diff-Report + Abnahme-Export (§3.14.8)
```

Sheriff-Tags (`01` §6.3): `tailwind-config`, `propel`, `blocks`, `icons-lucide`, `theme` tragen `type:ui`; Richtung `propel ← blocks ← editor`; `theme` darf `utils` importieren (Custom-Theme-Generator in `libs/shared/utils/src/theme/*`, 1:1-Kopie von `UTL/theme/*`).

### 3.2 CSS-Pipeline

#### 3.2.1 Vendoring-Regel

`tools/propel-port/vendor-css.mjs` kopiert jede Datei aus §4.1 und ändert **nur** Zeilen, die mit `@import`, `@source`, `@plugin` oder `@reference` beginnen. Jede Änderung steht mit Original- und Zielzeile in `TWT/VENDORED.md`. Ein Unit-Test (`vendor-css.spec.ts`) prüft: Datei ohne diese Zeilen ist byte-gleich zum Original (SHA-256 aus `VENDORED.md`).

#### 3.2.2 Import-Reihenfolge je App (identisch zum Original)

| App | Reihenfolge (Ziel) | Original |
|---|---|---|
| web | `styles.css` (= `WEB/styles/globals.css`): `@import "tailwindcss" source(none)` (über `TWT/index.css`) → `TWT/propel-styles/propel.css` → `TWT/index.css`-Regeln → `FE/libs/shared/editor/styles/index.css` → `./styles/power-k.css` → `./styles/emoji.css` → `@plugin "@tailwindcss/typography"` → restliche Regeln aus `globals.css` | `WEB/styles/globals.css` Z. 1–5 |
| admin | `styles.css` (= `ADM/styles/globals.css`): `TWT/index.css` → (doppelt, wie Original) `TWT/propel-styles/propel.css` → Admin-Regeln (`.shadow-custom`, `.backdrop-blur-custom`, `.progress-bar`, bprogress) | `ADM/styles/globals.css` Z. 1–6 |
| space | `styles.css` (= `SPC/styles/globals.css`): `TWT/index.css` → Editor-Styles → `@plugin "@tailwindcss/typography"` → Space-Regeln | `SPC/styles/globals.css` Z. 1–3 |
| Schriften | `angular.json` → `projects.<app>.architect.build.options.styles`: `@fontsource-variable/inter/index.css`, `@fontsource/ibm-plex-mono/index.css`, `@fontsource/material-symbols-rounded/index.css`, danach `src/styles.css` | `WEB/app/root.tsx` Z. 30–33 (Import vor `globals.css`) |

#### 3.2.3 Quellen-Scan (`@source`)

Umschreibung in `TWT/index.css`: `@import "tailwindcss";` → `@import "tailwindcss" source(none);` (verhindert, dass Tests, Werkzeuge und Story-Dateien Utilities erzeugen, die im Original fehlen). `@source "../**/*.{ts,tsx}";` → drei Zeilen:

```css
@source "../../../apps/*/src/**/*.{html,ts}";
@source "../../**/src/**/*.{html,ts}";
@source not "../../**/*.spec.ts";
```

Umschreibung in `TWT/propel-styles/propel.css`: `@source "../";` → `@source "../propel-dist-classes.txt";`. Beide Formen (`source(none)`, `@source not`, Datei als Quelle) sind Tailwind-4.1-Funktionen ⚠ (in S10 mit 4.1.17 bestätigen; Fallback: Glob-Liste ohne `not`, Spec-Dateien in eigenen Ordner `__tests__/` außerhalb der Globs).

#### 3.2.4 Laufzeit-CSS-Regeln, die mitgezogen werden müssen

- **Keine** Komponenten-Styles (D09-ADR-03). Einzige Ausnahme: `:host{display:contents}` wird **nicht** per Komponenten-CSS gesetzt, sondern global in `TWT/overrides.css` als `[data-pl-host]{display:contents}` (eine Regel, Eintrag `UI-DEV-000` in `ui-deviations.yaml`, weil die Regel im Original-CSS nicht existiert).
- `body` erhält `bg-canvas` über `TWC/index.css`; Web-Root-Container zusätzlich `bg-canvas` (`WEB/app/layout.tsx` Z. 31), Admin `min-h-screen bg-canvas` (`ADM/app/root.tsx` Z. 77) – im Angular-Root-Template wortgleich.
- Progressbar (`@bprogress/core` 1.3.x) mit den CSS-Variablen aus App-Globals (unverändert).

#### 3.2.5 CSS-Diff-Test (Pflicht ab I0)

`tools/visual/css-diff.ts` baut Original (`pnpm --filter web build` im Original-Repo, einmalig, Ergebnis als Artefakt `reference-css/<app>.css` eingecheckt) und Ziel (`ng build <app>`), parst beide mit `postcss` und vergleicht:

| Teil | Regel |
|---|---|
| `@layer theme`, `@layer base`, `@layer components`, unlayered Regeln, `@keyframes`, `@property`, `@font-face` | **identisch** (Menge aus Selektor + Deklarationen, Reihenfolge innerhalb gleicher Spezifität identisch) |
| `@layer utilities` | jede Utility des Originals existiert im Ziel mit identischen Deklarationen (**keine fehlenden**); zusätzliche Utilities im Ziel nur, wenn in `ui-deviations.yaml` (`kind: extra-utility`) gelistet |
| Ergebnis | Report `css-diff.<app>.md`; CI-Gate rot bei jeder fehlenden oder abweichenden Regel |

Damit sind die offenen Punkte `A13a` O-01/O-02 (welche Utilities 4.1.17 tatsächlich erzeugt) automatisch beantwortet: Das Referenz-CSS ist das Inventar.

### 3.3 Angular-Komponentenkonventionen

#### 3.3.1 Abbildung von React-Mustern

| React/Propel-Muster | Angular-Ziel (verbindlich) | Beispiel |
|---|---|---|
| Komponente rendert ein eigenes Element (`useRender` mit `defaultTagName`) | Attribut-Selektor auf dem Default-Tag, zusätzlich auf allen per `render` im Original genutzten Tags | `button[plButton], a[plButton]` |
| `render={<a href/>}` / `nativeButton={false}` | Konsument setzt den Selektor direkt auf das gewünschte Element; Komponente erkennt `nativeButton` über `host.tagName` | `<a plButton href="…">` |
| Kompositum ohne eigenes Element (Root, Provider, Portal) | Element-Selektor `pl-<name>` mit Host-Attribut `data-pl-host` (→ `display: contents`) | `<pl-menu>`, `<pl-tooltip>` |
| Inhalt, der erst bei Öffnen existiert (Popup, Portal) | `<ng-template pl<Name>Content>` + Portal (§3.5) | `<ng-template plMenuContent>` |
| Props (`variant`, `size`, …) | `input()` mit gleichem Namen; Achsen ohne `defaultVariants` → `input.required()` (Propel `StrictVariantProps`) | `variant = input.required<ButtonVariant>()` |
| kontrolliert/unkontrolliert (`value`/`defaultValue`/`onValueChange`, `useControllableState`) | `model()` + `defaultValue = input()`; Helfer `controllableState()` in `PRP/hooks/` | `open = model<boolean>()`, `[(open)]` |
| Callback `onXxx` (nicht Wert) | `output()` mit Namen ohne `on` | `openChangeComplete = output<boolean>()` |
| `icon` als Komponente oder Node | `input<PlIconSource>()` (`PlIconDef \| TemplateRef<unknown>`) | `[icon]="PaletteOutline"` |
| `label`, `title`, `description` als String **oder** ReactNode | String-Input; für Nodes zusätzlich Template-Input `labelTemplate` | – |
| `children` | `<ng-content>` (Reihenfolge der Slots wie Original-JSX) | – |
| `className` (nur Blocks) | Input `className`, verarbeitet mit `cn()` am Wurzel-Element (tailwind-merge-Semantik) | `<pl-card className="p-2">` |
| `className` per `render` an Propel (Base UI `mergeProps` = Verkettung) | `class`-Attribut am Host des Attribut-Selektors (Angular verkettet, keine Merge-Semantik – identisch zu `mergeProps`) | `<button plButton class="w-full">` |
| `createXxxHandle()` (imperative Handles) | Klasse `PlXxxHandle` (`open()`, `close()`, `isOpen` Signal), per `[handle]` verbunden | `PlMenuHandle` |
| React-Context (`FieldOptionSizeProvider`, `MenuRadioMarkerContext`, Dialog-Kontext) | `InjectionToken` + `providers` auf Komposita, gelesen per `inject(…, { optional: true })` | `PL_FIELD_OPTION_SIZE` |
| `useId` | `PlIdService.next('menu')` → `pl-menu-<n>` (Normalisierung §3.14.6) | – |
| `aria-*`, `id`, `data-*` des Konsumenten | landen direkt am Host-Element (Attribut-Selektor) bzw. werden bei Komposita per Input `attrs` an das Wurzel-Element des Templates weitergereicht | – |

#### 3.3.2 Selektor- und Klassennamen

Regel: Exportierter React-Teil `X` → Angular-Klasse `PlX`, Selektor `[plX]` bzw. `pl-x` (kebab-case). Element-Direktiven erhalten das Suffix `El` (`PlButtonEl`, `[plButtonEl]`), wenn eine gleichnamige Komponente existiert; sonst ohne Suffix. Dateinamen kebab-case wie Original (`menu-item.component.ts`). Jede Lib exportiert nur über `public-api.ts`; Unterpfad-Importe wie im Original (`@plane/propel/components/menu`, `@plane/blocks/toast`) werden über `tsconfig.base.json`-Pfade abgebildet.

#### 3.3.3 Lint-Regeln (ESLint, `FE/eslint.config.js`)

| Regel-ID | Inhalt |
|---|---|
| `pl/no-component-styles` | `styles`/`styleUrl(s)` in `@Component` verboten in `libs/shared/{propel,blocks}` und `libs/web/**` |
| `pl/encapsulation-none` | `encapsulation: ViewEncapsulation.None` Pflicht in `libs/shared/{propel,blocks}` |
| `pl/no-generated-edit` | Dateien mit Header `// GENERATED` dürfen nur vom Generator geändert werden (CI vergleicht Neu-Generierung mit Repo-Stand) |
| `pl/no-plan-gating` | Bezeichner `isPro`, `plan`, `subscription`, `upgrade`, `UpgradeBadge`, `ProIcon` verboten (Rahmen §7.18, ADR-001) |
| `pl/icon-source` | `<svg>` mit Inline-Pfaden in Templates verboten außer in generierten Dateien und `state-icons/` (Icons nur über `svg[plIcon]`) |
| `pl/no-cdk-overlay` | Import von `@angular/cdk/overlay` verboten (D09-ADR-10/-11) |

### 3.4 Zustandsvertrag (`data-*`, ARIA, CSS-Variablen) und Präsenz

#### 3.4.1 Attribute und Variablen

Die Headless-Schicht `PRP/headless/state-attrs.ts` setzt die von Base UI 1.6.0 gesetzten Attribute **mit identischer Wertform**: Boolesche Zustände als leeres Attribut (`data-disabled=""`), Aufzählungen als Wert (`data-side="bottom"`, `data-orientation="vertical"`, `data-swipe-direction="right"`), fehlender Zustand = Attribut entfernt. Pflichtumfang:

| Gruppe | Attribute / Variablen (vollständig laut `A13a` §2.20) | gesetzt von |
|---|---|---|
| Interaktion | `data-disabled`, `data-highlighted`, `data-pressed`, `data-active`, `data-hovering`, `data-scrolling`, `data-readonly` | Button, Menu/Listbox-Items, Toggle, Tabs, ScrollArea, Field-Controls |
| Auswahl | `data-checked`, `data-unchecked`, `data-indeterminate`, `data-selected` | Checkbox, Radio, Switch, Menu-Checkbox/Radio, Listbox, Tabs |
| Validierung | `data-invalid` (+ von Base UI Field zusätzlich `data-valid`, `data-touched`, `data-dirty`, `data-filled`, `data-focused`) | Field, alle Controls |
| Öffnen/Präsenz | `data-popup-open`, `data-panel-open`, `data-expanded`, `data-closed`, `data-starting-style`, `data-ending-style`, `data-visible`, `data-placeholder` | Trigger, Collapsible, Accordion, Popups, Toast, Select-Value |
| Positionierung | `data-side`, `data-align`, `data-anchor-hidden`, `--transform-origin`, `--available-height`, `--available-width`, `--anchor-width` (+ `--anchor-height`) | Positioner (§3.5.3) |
| Panels | `--accordion-panel-height`, `--collapsible-panel-height` | Accordion, Collapsible (Messung `scrollHeight`) |
| Navigation-Menu | `--popup-width`, `--popup-height` | NavigationMenu-Viewport |
| Tabs | `--active-tab-left`, `--active-tab-top`, `--active-tab-width` | TabsIndicator |
| Toast | `--toast-index`, `--toast-offset-y`, `--toast-height`, `--toast-frontmost-height`, `--toast-swipe-movement-x`, `--toast-swipe-movement-y`, `data-behind`, `data-limited`, `data-expanded`, `data-swipe-direction` | Toast-Viewport/-Root |
| Scroll-Area | `data-overflow-x-start`, `data-overflow-x-end` (+ y-Varianten), `data-orientation`, `data-hovering`, `data-scrolling` | ScrollArea |
| Propel-eigen | `data-slot`, `data-section`, `data-variant`, `data-size`, `data-theme` (LogoSpinner), `data-list-item-primary`, `data-disclosure-trigger`, `data-auto-resize`; Variablen `--node-size`, `--popup-held-width`, `--skeleton-block-size`, `--skeleton-inline-size`, `--switch-thumb-size`, `--switch-thumb-travel`, `--swatch-fill`, `--gap`, `--peek`, `--scale`, `--shrink`, `--height`, `--offset-y` | jeweilige Propel-Teile |
| ARIA | `role`, `aria-expanded`, `aria-haspopup`, `aria-controls`, `aria-labelledby`, `aria-describedby`, `aria-activedescendant`, `aria-selected`, `aria-checked` (inkl. `mixed`), `aria-disabled`, `aria-busy`, `aria-current="page"`, `aria-orientation`, `aria-valuenow/min/max/text`, `aria-live`, `aria-modal`, `aria-required` | je Muster wie Base UI (DOM-Vertrag) |

Die **exakte** Liste je Komponente (welches Element welches Attribut in welchem Zustand trägt) wird nicht von Hand gepflegt, sondern in S10 aus der Referenz-Galerie als **DOM-Vertrag** aufgezeichnet (`FE/apps/e2e/visual/dom-contracts/gallery/<component>/<story>.dom.html`, je Story und Interaktionsschritt). Der DOM-Vertrag ist für den Implementierungs-Agenten die Spezifikation; der DOM-Vergleichstest (§3.14.6) prüft ihn.

#### 3.4.2 Präsenz (`PresenceController`)

| Phase | Verhalten (wie Base UI 1.6.0) |
|---|---|
| Öffnen | Element wird gemountet mit `data-starting-style`; nach dem nächsten Frame (`requestAnimationFrame` ×1) entfernt → CSS-Transition läuft (`data-starting-style:opacity-0 scale-95`) |
| Offen | `data-open`-äquivalente Zustände am Popup (`data-side` …); Trigger erhält `data-popup-open` |
| Schließen | `data-ending-style` setzen, `data-closed` wo Base UI es setzt; warten bis alle `element.getAnimations()` beendet sind; dann unmounten; `keepMounted` → nicht unmounten, `hidden` setzen |
| Reduzierte Bewegung | Keine eigene Logik: CSS (`motion-reduce:transition-none`, `motion-reduce:animate-none`) macht die Animation leer, `getAnimations()` ist leer → sofort unmounten |
| Fallback | Spinner: Unmount spätestens nach 250 ms (`SPINNER_CONCEAL_TIMEOUT_MS`, `PROPEL/internal/spinner.js`); andere Popups: kein Timeout (wie Base UI) |

#### 3.4.3 Animationen (unverändert über CSS)

Alle 17 Propel-Animationen (`A13a` §2.14: `slide-up`, `slide-in-from-bottom`, `slide-in-from-top`, `slide-out`, `slide-out-down`, `fade-out`, `fade-in`, `spinner-reveal`, `spinner-conceal`, `tour-carousel-slide-in-right/-in-left/-out-right/-out-left`, `tour-carousel-fade-in`, `tour-popover-enter`, `tour-popover-exit`, `progress-indeterminate`, `notification-bell-ring`), die Tailwind-Defaults `spin`, `pulse`, `ping`, `bounce` und die Web-Klassen `.animate-text-slide-in`, `.animate-text-fade-out`, `.animate-lock-icon`, `.animate-unlock-icon`, `.animate-fade-out` (500 ms, Web-Override) und `@keyframes highlight` kommen ausschließlich aus dem vendored CSS. Angular-Code setzt nur Klassen und Präsenz-Attribute. Zeitkonstanten, die im Original **JS** steuert, werden als benannte Konstanten übernommen:

| Konstante (Ziel) | Wert | Original |
|---|---|---|
| `SPINNER_CONCEAL_TIMEOUT_MS` | 250 | `PROPEL/internal/spinner.js` |
| `TOOLTIP_DEFAULT_DELAY_MS` | 600 (Fokus: sofort) | Base-UI-Default, `A13a` §3.8 |
| `NESTED_SUBMENU_OPEN_DELAY_MS` / `…_CLOSE_DELAY_MS` | 100 / 600 | `BLK/select/nested-submenu/nested-submenu.constants.ts` |
| `SELECT_SEARCH_DEBOUNCE_MS` | 300 | `BLK/select/select.constants.ts` |
| `TOAST_HIGH_PRIORITY_TIMEOUT_MS` | 8000 | `PROPEL/components/toast/toast.js` |
| `CUSTOM_THEME_RELOAD_DELAY_MS` | 1500 | `WEB/components/core/theme/custom-theme-selector.tsx` |
| `BREADCRUMB_COLLAPSE_BREAKPOINT_PX` | 640 | `BLK/breadcrumb/breadcrumbs.tsx` |
| `MENU_FIT_FLOOR_PX` | 178 | `PROPEL/components/menu/menu-content.d.ts`, `internal/fit-side.js` |
| `ANIMATED_COUNTER_MS` | 250 | `BLK/emoji-reaction/animated-counter.tsx` |

### 3.5 Overlay-Schicht: Portal, Positionierung, Dismissal, Fokus

#### 3.5.1 Portal (`PRP/headless/portal.ts`)

`PlPortalService.attach(templateRef, ctx)` erzeugt das Portal-Element **so, wie Base UI 1.6.0 es erzeugt** (Container am Ende von `document.body`; Struktur, Attribute und Reihenfolge gemäß DOM-Vertrag aus S10) und rendert das Template per `ViewContainerRef.createEmbeddedView` hinein (Change-Detection bleibt beim Aufrufer). Blocks-`ModalPortal`/`PortalWrapper` nutzen weiterhin den eigenen Container `#full-screen-portal` (`data-portal="true"`, Anlage/Entfernung wie `BLK/portal/*`). z-Index ausschließlich über die Klassen des Originals (`z-50` Positioner/Backdrop/Viewport, `z-70` NestedSubmenu, `MODAL_Z_INDEX` 25/26). Kein `.cdk-overlay-container` (`A13a` F-12).

#### 3.5.2 Dismissal und Popup-Baum

| Regel | Umsetzung |
|---|---|
| Escape | globaler `keydown`-Stack (`PlDismissStack`): nur das oberste offene Popup reagiert; AlertDialog: Escape = Abbruch; Dialog mit `discard.when` → öffnet Discard-AlertDialog |
| Klick außerhalb | `pointerdown` (Capture) auf `document`; ignoriert Ziele innerhalb des Popup-Baums (verschachtelte Popups registrieren sich beim Eltern-Popup, `PlFloatingTree`) und innerhalb `[data-prevent-outside-click]` (Blocks `isDismissalFromPreventedRegion`); AlertDialog schließt **nicht**; `disablePointerDismissal` am Dialog |
| Veto | `openChange`-Ereignis trägt `details.cancel()` (wie Base UI `onOpenChange(open, eventDetails)`) |
| Fokus | Modal: `cdkTrapFocus`-Logik (`FocusTrap` aus CDK) + `initialFocus`/`finalFocus` wie Propel; nicht-modal: Fokus bleibt beim Trigger (Tooltip, PreviewCard) bzw. wandert ins Popup (Menu, Popover) wie Base UI |
| Scroll-Lock (modal) | wie Base UI 1.6.0 (Styles an `<html>`/`<body>` laut DOM-Vertrag, inkl. Scrollbar-Kompensation); einmal je Stapel |
| Außenbereich (modal) | `aria-hidden`/`inert` an Geschwistern des Portals genau wie Base UI (DOM-Vertrag) |
| Hover-Intent | `PlDelayGroup` (TooltipProvider: geteilte Öffnungs-/Schließ-Delays), Menü-Submenüs per Hover nach Base-UI-Defaults, Blocks-`NestedSubmenu` 100/600 ms |

#### 3.5.3 Positionierung (`PRP/headless/floating.ts`)

`computePlPosition(anchor, floating, opts)` kapselt `@floating-ui/dom`: `offset({mainAxis: sideOffset, crossAxis: alignOffset})`, `flip({padding: collisionPadding, fallbackAxisSideDirection: 'end'})`, `shift({padding: collisionPadding, limiter: limitShift()})` (nur wenn `collisionAvoidance` es vorsieht), `size({apply})` (schreibt `--available-width`, `--available-height`, `--anchor-width`, `--anchor-height`), `arrow({element, padding: arrowPadding})`, `hide()` (→ `data-anchor-hidden`); `autoUpdate` solange offen; `sticky=false` → bei verdecktem Anker Popup verbergen (Tooltip). Seitenwerte `top|bottom|left|right|inline-start|inline-end` mit RTL-Auflösung über CDK `Directionality`. Die genaue Middleware-Parametrisierung wird in S10 gegen Base UI 1.6.0 (Quelle `@base-ui/react/esm/utils/useAnchorPositioning.js` im Original-`node_modules`) abgeglichen und als Test `floating.spec.ts` mit 24 Kollisionsfällen (4 Seiten × 3 Ausrichtungen × mit/ohne Kollision) gegen die Referenz-Galerie gemessen (Abweichung Position ≤ 0,5 px). Propel-Spezialfälle: `MenuContent heightBehavior="fit"` (`resolveFitSide`, Floor 178 px, einmal je Öffnen), `OverlayPanel`-Hold-Width (`ResizeObserver` → `--popup-held-width`), Select-`alignItemWithTrigger`.

### 3.6 Formulare

| Thema | Regel |
|---|---|
| Formular-API | **Angular Signal Forms** (Rahmen §10 Glossar: `react-hook-form` → Signal Forms); Propel-Controls implementieren zusätzlich `ControlValueAccessor` (Interop mit Reactive Forms in portierten Altformularen) |
| `PlField` | stellt Kontext-Signal `{ invalid, valid, disabled, touched, dirty, filled, focused }` bereit; Label, Control, Description, Error setzen daraus `data-*` (§3.4.1); `invalid` kommt aus dem Field-Status **oder** Input `invalid` wie Propel `Field invalid` |
| `required` | `InputField`/`TextAreaField`: Sternchen (`FieldLabelRequiredMarker`) + `aria-required`, **kein** natives `required` (`A13a` §3.8) |
| Fehlertexte | `FieldError` zeigt Texte des aufrufenden Formulars; Validatoren und i18n-Schlüssel 1:1 aus den Original-Formularen (`react-hook-form`-Regeln → Signal-Forms-Validatoren, Tabelle je Formular in `08`) |
| Tab-Reihenfolge (CE-UIX-005) | `tabIndex`-Werte aus dem Original-Markup übernehmen; Test-Spezifikation `BLK/property-select/tab-index.test.tsx` wird nach `BLKT/property-select/tab-index.spec.ts` portiert |

### 3.7 Icon-Pipeline

| Schritt | Werkzeug | Ergebnis |
|---|---|---|
| 1 | `fetch-propel.mjs` | `tools/propel-port/.cache/propel/package/dist/**` |
| 2 | `port-icons.mjs --source propel` | liest jede `PROPEL/icons/<kategorie>/<name>.js`, rendert die React-Komponente einmal mit `react-dom/server` (`renderToStaticMarkup`, Props leer) und parst das SVG zu `PlIconDef { name, attrs, children: PlSvgNode[] }`; schreibt `PRP/icons/<kategorie>/<kebab-name>.ts` mit `export const PaletteOutline: PlIconDef = {…}` |
| 3 | `port-icons.mjs --source solid` | `PROPEL/internal/solid-icons/*` → `PRP/internal/solid-icons/*.ts` |
| 4 | `port-icons.mjs --source lucide@1.34.0` / `lucide@0.469.0` | aus dem framework-freien npm-Paket `lucide` (Icon-Knoten-Arrays) → `FE/libs/shared/icons-lucide/src/v134/*.ts` (17 Propel-interne Namen, `A13a` §2.29) bzw. `v0469/*.ts` (alle 181 in Apps/Blocks genutzten Namen + 157 Namen aus `LUCIDE_ICONS_LIST`) |
| 5 | `port-icons.mjs --source blocks` | `BLK/icons/**/*.tsx` (über `@babel/parser` + `renderToStaticMarkup` mit Default-Props) → `BLKT/icons/**/*.ts`; Komponenten mit Logik (`StateGroupIcon`, `PriorityIcon`, `CycleGroupIcon`, `ModuleStatusIcon`, `IntakeStateGroupIcon`, `ProgressCircle`, `DashedCircle`, Fortschritts-Icons) werden **von Hand** als Angular-Komponenten mit identischem SVG portiert (Tabelle §4.8) |
| 6 | `port-icons.mjs --source web` | `WEB/components/icons/attachment/{document,setting,tune}-icon.tsx` → Konstanten; PNG-Icons bleiben `<img>` (§4.9) |
| 7 | Barrel | `PRP/icons/index.ts` exportiert alle 919 Konstanten + `StateGroupIcon`, `StartedGroupIcon`, `UnstartedGroupIcon` und Typen wie `PROPEL/icons/index.d.ts` Z. 922 |
| 8 | Test | `icons.spec.ts`: für jedes Icon ist das von `svg[plIcon]` gerenderte `outerHTML` (normalisiert) gleich dem `renderToStaticMarkup`-Ergebnis des Originals (Golden-Datei `icons.golden.json`, generiert aus dem Original) |

Rendering: `<svg plIcon [icon]="PaletteOutline" class="…">` erzeugt dieselben Attribute wie das Original (`xmlns`, `fill="none"`, `viewBox="0 0 16 16"`, `width="1em"`, `height="1em"`, `aria-hidden="true"` + Konsumenten-Attribute). 63 Icons mit festen Hex-Füllungen bleiben unverändert (Marken). Material Symbols bleiben Font-Ligaturen (`<span class="material-symbols-rounded">name</span>`).

### 3.8 Schriften, Assets, Illustrationen

#### 3.8.1 Schriften

| Schrift | Ziel | Laden | Lizenz |
|---|---|---|---|
| Inter Variable (`@fontsource-variable/inter` 5.2.8) | `angular.json` `styles`; zusätzlich `assets`-Kopie `node_modules/@fontsource-variable/inter/files/inter-latin-wght-normal.woff2` → `/{base}fonts/inter-latin-wght-normal.woff2` | `index.html`: `<link rel="preload" href="fonts/inter-latin-wght-normal.woff2" as="font" type="font/woff2" crossorigin="anonymous">` (wie `WEB/app/root.tsx` Z. 47–53) | OFL-1.1 |
| IBM Plex Mono (`@fontsource/ibm-plex-mono` 5.2.7, Default-Index = 400) | `styles` | – | OFL-1.1 |
| Material Symbols Rounded (`@fontsource/material-symbols-rounded` 5.2.30) | `styles` | Ladeerkennung wie `BLK/emoji-icon-picker/logo.tsx` über `document.fonts.check('normal normal condensed 1em "Material Symbols Rounded"')` + `document.fonts.load` (Äquivalent zu `use-font-face-observer`, Edge-Case E-28 nachbauen) | Apache-2.0 |
| Emoji-Glyphen | **System-Emoji-Font** wie Original (frimousse rendert native Emojis); Test-Container mit gepinnter `Noto Color Emoji` (§3.14.3) | – | OFL-1.1 (nur Test) |
| Inter statisch (PDF) | nicht hier → `07` | – | – |

Subset-Abdeckung für die 22 Locales (`A13a` O-05) wird automatisch geprüft: E2E-Test lädt je Locale die Startseite und prüft per `document.fonts`, dass alle geladenen `@font-face`-Ranges aus dem gebündelten Paket stammen (keine externe URL, Netzwerk-Allowlist = Gateway-Origin).

#### 3.8.2 Emoji-Daten (Korrektur E-22)

`emojibase-data` in der von `frimousse` 0.3.0 per Default geladenen Version ⚠ (Rahmen §8.2) wird nach `FE/apps/{web,space}/src/assets/emojibase/<version>/<locale>/{data,messages}.json` kopiert (alle Locales, die frimousse für die 22 Plane-Sprachen anfordert; Fallback `en`). Der Angular-Emoji-Picker (`BLKT/emoji-icon-picker/emoji/`) lädt nur von dort. Emoji-Speicherformat (Dezimal-Codepoints mit `-`, `emojiToString`/`stringToEmoji`) wird 1:1 kopiert.

#### 3.8.3 Illustrationen und Raster-Assets

- **59 Blocks-Illustrationen** (`HORIZONTAL_STACK_ASSETS` 32, `VERTICAL_STACK_ASSETS` 25, `ILLUSTRATION_ASSETS` 2; `A13a` §2.31) werden von `port-illustrations.mjs` in `PlIllustrationDef`-Konstanten übersetzt (gleiche AST-Form wie Icons, Farben bleiben `var(--illustration-*)`), lazy per `import()` geladen (Original `React.lazy`, Fallback = nichts rendern) und über `svg[plIllustration]` gerendert. Registry-Schlüssel 1:1 (`asset-registry.tsx`).
- **Raster-/SVG-Dateien** aus `apps/*/app/assets/**` und `apps/*/public/**` werden byte-identisch kopiert (vollständige Tabelle §4.11). Referenzen im Code bleiben pfadgleich relativ zum `assets/`-Ordner (`assets/empty-state/cycle/…`).
- **Theme-abhängige Assets:** `FE/libs/shared/theme/src/theme-asset-helpers.ts` exportiert `isLightStrict(resolvedTheme)` (`=== "light"`), `isDarkStrict(resolvedTheme)` (`=== "dark"`) und `resolveGeneralTheme(resolvedTheme)` (`includes("light")`/`includes("dark")`/`"system"`). Jede der 46 Fundstellen aus `A13a` §3.5 verwendet **dasselbe** Muster wie im Original (E-03 nachbauen). Der Port-Agent übernimmt die Fundstellen-Liste als Checkliste in die jeweilige Domänen-Lib.

### 3.9 Theme-Laufzeit

#### 3.9.1 Bausteine

| Baustein | Ort | Inhalt |
|---|---|---|
| `THEME_INLINE_SCRIPT` | `FE/libs/shared/theme/src/inline-script.ts` → per Build-Schritt als `<script>` in `index.html` jeder App (vor allen Bundles; CSP-Nonce per Gateway-Platzhalter `{{CSP_NONCE}}`) | Logik von `next-themes` 0.4.6: `localStorage["theme"]` lesen (Fehler/Ungültig → `defaultTheme="system"`), `system` per `matchMedia("(prefers-color-scheme: dark)")` auflösen, `document.documentElement.setAttribute("data-theme", resolved)`, bei `light`/`dark` `style.colorScheme` setzen (`enableColorScheme`), Werte außerhalb der App-Themes ignorieren |
| `ThemeService` | `FE/libs/shared/theme/src/theme.service.ts` | Signals `theme()`, `resolvedTheme()`, `systemTheme()`, `themes()`; `setTheme(value)` schreibt Attribut + `localStorage` + `colorScheme`; `matchMedia`-Listener; `storage`-Event (tabübergreifend) |
| `PROVIDE_THEME_CONFIG` | `app.config.ts` je App | Web: `themes: ['light','dark','light-contrast','dark-contrast','custom']`, `defaultTheme: 'system'`, `enableSystem: true`; Admin/Space: `themes: ['light','dark']`, sonst gleich |
| Custom-Theme | `FE/libs/shared/utils/src/theme/*` (1:1 `UTL/theme/*`, `chroma-js` 3.2.x) | `applyCustomTheme(brand, neutral, mode)`, `clearCustomTheme()`, Paletten-Generator, Inversion (E-01, E-02, E-14 nachbauen) |
| Profil-Sync (Web) | `libs/web/core` `StoreWrapper`-Äquivalent (→ `08`) | einmal je Benutzer-Sitzung `setTheme(profile.theme.theme \|\| 'system')`; `effect()` wendet Custom-Theme an bzw. entfernt es (E-05) |
| Theme-Wechsel | Profil-Preferences, Power-K, Admin-Menü, Space-Navbar | Abläufe 1:1 aus `A13a` §3.2 inkl. Toast-Folge und `location.reload()` (E-04), Admin-Umschalter (E-33), Space-Umschalter mit `theme` statt `resolvedTheme` (E-29), Admin-Store schreibt denselben Schlüssel (E-32) |

#### 3.9.2 Zustände für die Verifikation

| Theme-ID im Katalog | Einrichtung im Test (vor Navigation per `addInitScript`) |
|---|---|
| `light` | `localStorage.theme = "light"` |
| `dark` | `localStorage.theme = "dark"` |
| `light-contrast` | `localStorage.theme = "light-contrast"` (nur Web) |
| `dark-contrast` | `localStorage.theme = "dark-contrast"` (nur Web) |
| `custom-light` | Profil `theme = { theme: "custom", primary: "#3f76ff", background: "#1a1a1a", darkPalette: false }` per Seed + `localStorage.theme = "custom"` (nur Web) |
| `custom-dark` | wie oben mit `darkPalette: true` (nur Web) |
| `system-light` / `system-dark` | `localStorage.theme = "system"` + Playwright `colorScheme: 'light' \| 'dark'` (nur Shell-Einträge) |

### 3.10 Toast-System

| Ebene | Ziel | Regel |
|---|---|---|
| Propel `toast` | `PRP/components/toast/` | `PlToastManager` (Äquivalent `createToastManager`): `add/update/close/promise`; `data.variant` Pflicht (sonst Fehler); danger/warning → `priority: 'high'`, `timeout: 8000`; Stapel-Variablen (`--toast-index`, `--toast-offset-y`, `--toast-height`, `--toast-frontmost-height`), Attribute (`data-behind`, `data-limited`, `data-expanded`, `data-swipe-direction`, `data-visible`), Expand bei Hover, Swipe-to-dismiss, `aria-live`-Region wie Base UI; max. 2 linke Aktionen + 1 `primaryAction`; `progress` → `PlLinearProgress size="sm" variant="brand"` |
| Blocks-Fassade | `BLKT/toast/toast-manager.ts` (+ `PlPlaneToastProvider` als `<pl-plane-toast-provider>` im App-Root) | API **identisch**: `setToast`, `updateToast`, `setPromiseToast`, `dismissToast`, `toastManager`, Typen `ToastType`, `SetToastProps`, `ToastActionItem`, `PromiseToastOptions`; Typ-Mapping `success→success`, `error→danger`, `warning→warning`, `info→info`, `loading`/`loading-toast`→`neutral` mit `timeout: 0`, Titel-Default „Loading...“ |
| Test | `toast-manager.spec.ts` | 1:1 Port von `BLK/toast/toast-manager.test.ts`; Visual-Stories je Variante × mit/ohne Aktionen × Stapel 1/3/5 |

### 3.11 Blocks-Select-Engine

Die Select-Engine (`BLK/select/**`) ist der größte Einzelbaustein (Basis aller Property-Felder in Listen, Kanban, Spreadsheet, Peek; `A13a` §3.9). Port-Regeln:

1. **Struktur 1:1:** gleiche Dateien (§4.7), gleiche Konstanten (`MENU_LIST_CLASSNAME`, `MENU_ROW_HEIGHT` 32, `SELECT_OPTION_ROW_HEIGHT` 28, `SELECT_SEARCH_DEBOUNCE_MS` 300), gleiche Typen aus `BLK/select/types.ts` (als TS-Datei kopiert, React-Typen durch `TemplateRef`/`PlIconSource` ersetzt).
2. **Lazy-Mount:** bis zur ersten Aktivierung nur `<button aria-haspopup="listbox" aria-expanded="false">` mit identischer Optik; Aktivierung mountet die Combobox und öffnet in einem Schritt. `variant="search-input"`, `defaultOpen` und kontrolliertes `open` mounten sofort.
3. **Unterbau:** Propel-`PlCombobox*` (Komponenten + Elemente) statt Base-UI-`Combobox`; Virtualisierung mit `@tanstack/virtual-core` (`overscan: 8`, Zeilenhöhen wie oben); Infinite-Loading mit Generation-Zähler und IntersectionObserver-Sentinel; Skip-Disabled-Replay (`use-skip-disabled-rows.ts` → `skip-disabled-rows.ts`).
4. **Trigger-Chrome-Varianten** (`pill-{sm,md,lg}`, `icon-{sm,md,lg}`, `select-{md,lg,xl,2xl}`, `select-ghost-{md,lg,xl,2xl}`, `table-cell`, `breadcrumb`, `search-input`, `avatar-group-{sm,md,lg}`, Fallback `pill-sm`) mit wortgleichen Klassen aus `BLK/select/utils.ts` / `trigger-chrome.tsx` (Tabelle `A13a` §2.26).
5. **Tests als Spezifikation:** `select.test.tsx`, `menu-search-input.test.tsx`, `nested-submenu.dismissal.test.tsx`, `property-select/{tab-index,member-select,outside-click,date-select}.test.tsx` werden als `*.spec.ts` mit `@testing-library/angular` portiert; alle müssen grün sein, bevor I2 abgenommen wird.

### 3.12 Charts

Die sechs Blocks-Charts (`bar`, `area`, `line`, `pie`, `radar`, `tree-map`) werden nach ADR-044 als Angular-SVG-Komponenten auf `d3-scale`/`d3-shape`/`d3-array`/`d3-hierarchy` gebaut. DOM-Vertrag: das von `recharts` 2.15.4 erzeugte SVG (Wrapper `div.recharts-responsive-container` › `div.recharts-wrapper` › `svg.recharts-surface` mit Gruppen `g.recharts-cartesian-grid`, `g.recharts-xAxis`, `g.recharts-yAxis`, `g.recharts-bar`/`recharts-area`/`recharts-line`/`recharts-pie`/`recharts-radar`/`recharts-treemap…`, Legenden- und Tooltip-Wrapper), aufgezeichnet aus der Referenz-Galerie mit festen Datensätzen (`tools/gallery-stories/charts.stories.json`). Gemeinsame Bausteine (`charts/components/{legend,tick,tooltip}`) und Konstanten (`packages/constants/src/chart.ts`, 1:1 in `libs/shared/constants`) unverändert. Schwellwert 0,5 % (S6).

### 3.13 Keycloak-Login-Theme (Optik)

| Thema | Regel |
|---|---|
| CSS | Build-Target `FE/apps/keycloak-theme` mit eigenem `styles.css` = `TWT/index.css` + `@source "../../../deploy/keycloak/themes/plane/login/*.ftl"`; Ausgabe `deploy/keycloak/themes/plane/login/resources/css/plane.css` (eingecheckt, CI prüft Aktualität) |
| Fonts | `deploy/keycloak/themes/plane/login/resources/fonts/` (Inter Variable, IBM Plex Mono) aus denselben Fontsource-Paketen |
| DOM-Vorlage | Web/Admin: `WEB/app/(home)/page.tsx`, `WEB/components/auth-screens/**` (Layout, Header mit `PlaneLockup`, Footer mit Kundenlogos `AccentureLogo`, `DolbyLogo`, `SonyLogo`, `ZerodhaLogo` und `dark:text-on-color`), `BLK/auth/password/password-input.tsx` (Passwortfeld mit Show/Hide-Toggle), `BLK/auth/password/indicator.tsx` (nur für `login-update-password.ftl`); Space: `SPC/app/page.tsx` + `SPC/components/account/**`; Hintergrund `assets/auth/background-pattern{,-dark}.svg` |
| Theme-Umschaltung | Keycloak-Seiten lesen `localStorage["theme"]` derselben Origin nicht (andere Origin) → Login folgt `prefers-color-scheme` (light/dark) über ein kleines Inline-Script mit derselben Auflösungslogik; dokumentierte Abweichung `UI-DEV-010` |
| Varianten | Keycloak-Client-Attribut `login_theme_variant = web \| admin \| space` steuert Kopfzeile/Texte (Template-Logik → `05`) |
| Verifikation | Katalog-Einträge `kc-login-web`, `kc-login-space`, `kc-login-error` gegen Original-Sign-in (`/`, `/spaces/`), Schwellwert 1 % (S7); Textunterschiede (Keycloak-Felder statt E-Mail-Check-Schritt) als Masken mit Eintrag `UI-DEV-011` |

### 3.14 Verifikationsverfahren

#### 3.14.1 Überblick

```mermaid
flowchart LR
  subgraph REF["Referenz (Original v1.4.2, unverändert)"]
    O1["compose.reference.yml<br/>web/admin/space/api/live/proxy"] --> O2["ParityHarness seed<br/>visual-seed.v1 + normalize.sql"]
    O2 --> O3["capture-reference.ts<br/>Screenshots · DOM · ARIA"]
    G1["reference-gallery<br/>(React + Propel 0.7.3 + Blocks)"] --> O3
  end
  subgraph TGT["Ziel (funk.)"]
    T1["aspire run / compose"] --> T2["ParityHarness seed<br/>(gleiches Szenario)"]
    T2 --> T3["visual.spec.ts<br/>Screenshots · DOM · ARIA · axe"]
    G2["apps/gallery (Angular)"] --> T3
  end
  S["gallery-stories/*.stories.json<br/>catalog/*.catalog.yaml"] --> O3
  S --> T3
  O3 -->|"Baselines, Verträge (Git LFS)"| C["Vergleich<br/>Pixel · DOM · ARIA · CSS-Diff"]
  T3 --> C
  C --> R["HTML-Report + Abnahme pro Screen"]
```

#### 3.14.2 Referenzumgebung (Original)

| Punkt | Festlegung |
|---|---|
| Quelle | Original-Repo, Commit des Plans (Tag `v1.4.2`, SHA in `tools/visual/reference-env/ORIGINAL_SHA`); Pfad über `PLANE_ORIGINAL_DIR` |
| Start | `docker compose -f tools/visual/reference-env/compose.reference.yml up -d --build`: baut die Original-Images aus den Dockerfiles des Original-Repos (`apps/web`, `apps/admin`, `apps/space`, `apps/api`, `apps/live`, Proxy) und startet sie mit `plane-db`, `plane-redis`, `plane-mq`, `plane-minio` wie `docker-compose.yml` des Originals; Proxy auf `http://localhost:8091`; alle Images per Digest gepinnt und für Airgap-CI in die interne Registry gespiegelt |
| Umgebung | `TZ=UTC`, Telemetrie aus, Instanz-Konfiguration per Seed (SMTP aus, Unsplash aus, LLM aus), `ENABLE_SIGNUP=1` nur während des Seeds |
| Seed | `dotnet run --project src/tools/Plane.Tools.ParityHarness -- seed --target original --base-url http://localhost:8091 --scenario tools/visual/seed/visual-seed.v1.json` (S11): legt über die Original-API Instanz-Admin, 5 Benutzer, Workspace `acme`, Projekte, Work Items, Cycles, Modules, Pages, Views, Intake, Stickies, Kommentare, Reaktionen, Benachrichtigungen, veröffentlichtes Board an (Inhalt §3.14.4); Avatare/Cover aus `tools/visual/fixtures/` |
| Zeit-Normalisierung | danach `psql -f tools/visual/seed/normalize-original.sql`: setzt `created_at`, `updated_at`, `completed_at`, `start_date`, `target_date`, Notification-Zeitstempel usw. auf Werte relativ zu **T0 = 2026-01-15T10:00:00Z** (Tabelle im Szenario), damit relative Zeitangaben („2 days ago“) stabil sind |
| ID-Abbildung | Harness schreibt `seed-map.original.json` (semantischer Schlüssel → UUID/Slug/Anchor), z. B. `project:WEB → 3f…`; Katalog-Routen verwenden nur semantische Schlüssel |
| Ziel | identisches Szenario gegen `funk.` (`--target funk`), Normalisierung `normalize-funk.sql`, Keycloak-Benutzer mit denselben E-Mail-Adressen im Test-Realm (`deploy/keycloak/realms/plane-realm.test.json`) |

#### 3.14.3 Determinismus der Aufnahmen

| Maßnahme | Wert |
|---|---|
| Browser-Container | **ein** Image für Referenz und Ziel: `mcr.microsoft.com/playwright:v1.5x.y-noble` (Digest gepinnt ⚠ zum I0-Start) + `fonts-noto-color-emoji` (gepinnte Version) + feste Monospace-Systemschrift (E-23); Hardware-Beschleunigung aus (`--disable-gpu`), `--font-render-hinting=none` |
| Kontext | `locale: 'en-US'`, `timezoneId: 'UTC'`, `deviceScaleFactor: 1` (Gate; Stichprobe `2` im Nightly), `reducedMotion: 'reduce'`, `colorScheme` passend zum Theme |
| Uhr | `page.clock.setFixedTime(new Date('2026-01-16T09:00:00Z'))` (T0 + 23 h) vor jeder Navigation |
| Animationen | `toHaveScreenshot({ animations: 'disabled', caret: 'hide' })`; zusätzlich Style-Injection `*{scroll-behavior:auto!important}` |
| Warten | `document.fonts.ready`; kein Element mit `[aria-busy="true"]` außer im Zustand gewollt; `networkidle`; zwei `requestAnimationFrame`; zustandsspezifische `wait`-Selektoren aus dem Katalog |
| Masken | nur explizit im Katalog (`mask:`) und nur für Inhalte, die zwischen Original und Ziel fachlich verschieden sein **müssen** (z. B. Versionsnummer, Keycloak-Texte); jede Maske braucht einen Eintrag in `ui-deviations.yaml` |
| Anmeldung | Original: `POST /auth/sign-in/` mit Seed-Passwort → `storageState` je Rolle; Ziel: Keycloak-UI-Login je Rolle einmal pro Worker → `storageState` |

#### 3.14.4 Screenshot-Katalog

Ein Katalog-Eintrag beschreibt **eine Route in einem fachlichen Zustand**. Jeder Eintrag wird in allen für ihn gültigen Themes × Viewports aufgenommen.

| Achse | Werte | Regel |
|---|---|---|
| Themes | Web: `light`, `dark`; zusätzlich `light-contrast`, `dark-contrast`, `custom-light`, `custom-dark` für Einträge mit Tag `theme-full`; Admin/Space: `light`, `dark` | `theme-full` tragen: Workspace-Shell, Home, Projektliste, Work-Item-Liste, Kanban, Spreadsheet, Work-Item-Detail, Cycle-Liste, Page-Editor, Profil-Preferences, Workspace-Settings General (11 Einträge) |
| Viewports | `mobile-390` (390×844), `tablet-768` (768×1024), `laptop-1024` (1024×768), `desktop-1440` (1440×900), `wide-1920` (1920×1080) | Grundzustand jeder Route (`state: base`) in `mobile-390`, `tablet-768`, `laptop-1024`, `desktop-1440`; interaktive Zustände nur `desktop-1440`; `wide-1920` zusätzlich für Kanban, Spreadsheet, Gantt, Kalender |
| Rollen | `admin` (WS-Admin 20), `member` (15), `guest` (5), `anonymous` (Space), `instance-admin` (God Mode) | Standard `admin`; Rollen-Varianten nur, wo sich die Oberfläche unterscheidet (Tag `role-variant`) |

Seed-Inhalt `visual-seed.v1.json` (Pflichtumfang): Benutzer `ada@acme.test` (Instanz-Admin, WS-Admin), `bob@acme.test` (Member), `cyd@acme.test` (Guest), `dee@acme.test` (Member, gesperrt/deaktiviert), `eve@acme.test` (eingeladen, nicht beigetreten); Workspace `acme` „Acme Corp“ mit Logo; Projekte `WEB` (alle Features an, Emoji-Logo, 60 Work Items über alle State-Gruppen/Prioritäten/Labels/Assignees, 3 Ebenen Sub-Items, Relationen aller Typen, Kommentare mit Reaktionen, Links, Anhänge), `MOB` (Material-Icon-Logo, 12 Work Items), `EMPTY` (keine Inhalte, für Empty-States), `OFF` (alle Projekt-Features aus); Cycles in `WEB`: current, upcoming, completed, draft; Modules in allen 6 Status; 5 Labels-Hierarchien mit 20 Labels; Estimates (Punkte); 3 Projekt-Views, 2 Workspace-Views; 6 Pages (öffentlich, privat, gesperrt, archiviert, mit allen Node-Typen aus `A12` §2.5); 5 Intake-Items (pending, accepted, declined, snoozed, duplicate); 3 Stickies; 10 Benachrichtigungen (gelesen/ungelesen/archiviert/snoozed); 2 Drafts; 3 archivierte Work Items/Cycles/Modules; veröffentlichtes Board für `WEB` (Kommentare, Reaktionen, Votes an) mit festem Anchor; 2 Webhooks; 2 API-Tokens; 1 Export.

Vollständige Liste der Katalog-Einträge: §4.14.

#### 3.14.5 Pixel-Diff und Schwellwerte

Vergleich mit Playwright `toHaveScreenshot` (Pixelmatch, `threshold` = Farbabstand je Pixel 0…1) gegen die importierten Original-Baselines; zusätzlich wertet `tools/visual/report/blob-check.ts` das Diff-Bild aus (zusammenhängende Diff-Regionen, 8er-Nachbarschaft).

| Klasse | `threshold` | `maxDiffPixelRatio` | größte zusammenhängende Diff-Region | Quelle |
|---|---|---|---|---|
| Komponenten-Galerie (Chromium) | 0,1 | **0,001** (0,1 %) | ≤ 16 px | S10 |
| Seiten-Screens (Chromium) | 0,1 | **0,002** (0,2 %) | ≤ 64 px | dieses Dokument |
| Editor-Seiten (Page-Detail, Work-Item-Beschreibung) | 0,1 | 0,005 (0,5 %) | ≤ 256 px | S5 |
| Charts | 0,1 | 0,005 (0,5 %) | ≤ 256 px | S6 |
| Keycloak-Login vs. Original-Sign-in | 0,1 | 0,01 (1 %) | – (Masken laut UI-DEV-011) | S7 |
| Firefox/WebKit (ab I7, informativ bis I7, dann Gate) | 0,2 | 0,005 | ≤ 256 px | – |

Ein Eintrag ist **pixel-grün**, wenn alle Theme×Viewport-Bilder die Schwellwerte einhalten. Baselines werden **nie** aus dem Ziel erzeugt (`--update-snapshots` ist im Ziel-Job gesperrt; Baselines entstehen nur durch `capture-reference`).

#### 3.14.6 DOM-Snapshot-Vergleich

`tools/visual/dom-normalize.ts` (gemeinsam für Referenz und Ziel, im Browser per `page.evaluate` ausgeführt):

| Nr. | Normalisierung |
|---|---|
| N1 | Wurzeln: App-Wurzel (`#root` bzw. `app-root` › erstes Kind) **und** alle Portal-Container am Ende von `<body>` in DOM-Reihenfolge |
| N2 | Entfernen: Kommentar-Knoten, `<script>`, `<style>`, `<link>`, Attribute `ng-version`, `_ngcontent-*`, `_nghost-*`, `ng-reflect-*`, `data-pl-host` |
| N3 | Auspacken (Kinder an die Stelle des Elements): Elemente mit `data-pl-host`, `router-outlet` + Geschwister-Kommentar, `<ng-container>`-Reste |
| N4 | IDs: Werte von `id`, `for`, `aria-controls`, `aria-labelledby`, `aria-describedby`, `aria-activedescendant`, `aria-owns`, `aria-errormessage`, `headers`, `list` → `id-1…n` in Reihenfolge des ersten Auftretens (Referenzen konsistent) |
| N5 | `class`: Tokens dedupliziert und sortiert |
| N6 | `style`: Deklarationen sortiert; px-Werte auf 0,5 px gerundet; Variablen `--available-*`, `--anchor-*`, `--transform-origin`, `--popup-held-width`, `--toast-*` mit Toleranz ±1 px |
| N7 | URLs (`href`, `src`, `srcset`, `xlink:href`): Origin entfernt; Seed-IDs → semantische Schlüssel aus `seed-map.*.json`; Bundler-Hashes in Asset-Dateinamen entfernt (`empty-state/cycle/light-AbC12.webp` → `empty-state/cycle/light.webp`) |
| N8 | Text: Whitespace zusammengefasst; Inhalte unverändert (Texte sind Vertrag, i18n 1:1) |
| N9 | Attribute alphabetisch sortiert |

Vergleich: exakte Gleichheit der normalisierten Serialisierung (`*.dom.html`); Unterschiede als Unified-Diff im Report. Ausnahmen nur über `ui-deviations.yaml` (`kind: dom`, `selector`, `ignore: attr:<name> \| subtree`).

#### 3.14.7 ARIA-Snapshot und Accessibility

- `await page.locator('body').ariaSnapshot()` je Zustand; Vergleich Original ↔ Ziel auf **Gleichheit** (YAML, IDs nicht enthalten). Ausnahmen wie bei DOM.
- `@axe-core/playwright` (Regeln `wcag2a`, `wcag2aa`, `wcag21aa`) auf Original und Ziel: Menge der Verstöße im Ziel ⊆ Menge im Original (Regel-ID + normalisierter Selektor) – **Ratchet**: das Ziel darf nicht schlechter sein; neue `critical`/`serious` sind immer rot.
- Tastatur-Szenarien je Komponente (Galerie-Stories mit `steps`: Tab, Pfeiltasten, Home/End, Escape, Enter/Space, Typeahead) vergleichen nach jedem Schritt `document.activeElement` (normalisierter Pfad) und den ARIA-Snapshot.

#### 3.14.8 Abnahme pro Screen

| Status | Bedeutung | Übergang |
|---|---|---|
| `open` | Eintrag existiert, Ziel-Screen noch nicht implementiert oder rot | – |
| `auto-green` | Pixel (§3.14.5), DOM (§3.14.6), ARIA/axe (§3.14.7) grün in allen Themes × Viewports | automatisch durch CI |
| `accepted` | fachliche Sichtprüfung durch den Auftraggeber im HTML-Report (Seite-an-Seite, Überblend-Regler, Diff-Ansicht, Interaktionsschritte) | Eintrag in `FE/apps/e2e/visual/catalog/acceptance/<app>.acceptance.yaml` (`id`, `accepted_by`, `accepted_at`, `report_sha`) per PR |
| `deviation` | Abweichung begründet (ADR-001/-004/-007/-008 oder D09-ADR-13-Korrektur) und genehmigt | Eintrag `UI-DEV-<nnn>` in `ui-deviations.yaml` mit `adr`, `entries`, `kind`, `selector`/`mask`, `approved_by` |

Ein **Screen** (Route) gilt als abgenommen, wenn alle seine Einträge `accepted` oder `deviation`+`accepted` sind. Ein **Inkrement** gilt UI-seitig als abgenommen, wenn alle Katalog-Einträge mit seinem `increment`-Wert abgenommen sind. Regression: Ein einmal abgenommener Eintrag, der rot wird, blockiert jeden PR (CI-Gate).

#### 3.14.9 Komponenten-Katalog (Galerien)

| Punkt | Festlegung |
|---|---|
| Story-Format | `tools/gallery-stories/<component>.stories.json`: `{ "component": "menu", "stories": [ { "id": "neutral-items-open", "props": {…}, "slots": {…}, "steps": [ {"click": "[data-story-trigger]"}, {"press": "ArrowDown"} ], "themes": "all" } ] }` |
| Matrix | `tools/gallery-stories/generate-matrix.mjs` erzeugt aus den `cva`-Achsen jedes Elements automatisch Stories: jede Achsen-Ausprägung mindestens einmal; vollständiges Kreuzprodukt, wenn ≤ 64 Kombinationen (z. B. Button: 6 Varianten × 4 Größen × 2 Stretch = 48); zusätzlich Zustände `default`, `hover`, `focus-visible`, `active`, `disabled`, `loading` (wo vorhanden), `invalid` (Field-Controls), `open` (Popups) |
| Referenz-Galerie | `tools/reference-gallery/` (React 19, Vite, `@makeplane/propel@0.7.3`, `@plane/blocks` per Pfad aus `PLANE_ORIGINAL_DIR/packages/blocks`, CSS = `WEB/styles/globals.css`); Route `/gallery/<component>/<story>`; Theme per `?theme=` |
| Angular-Galerie | `FE/apps/gallery/` mit identischen Routen; rendert Stories über eine Story-Map `<component> → Angular-Template` (`FE/apps/gallery/src/stories/<component>.stories.ts`), Props/Slots aus derselben JSON |
| Umfang (Pflicht) | 68 Komponenten, 57 Elemente, `base/composite`, `state-icons`, Icon-Übersicht (919 + lucide + Blocks, als Raster-Seiten à 120 Icons), alle Blocks-Module (§4.7), 59 Illustrationen, Typografie-Presets (57), Farb-Token-Tafeln je Theme |
| Themes | alle sechs Web-Themes für jede Story |
| Ergebnis | DOM-Verträge (`dom-contracts/gallery/**`), ARIA-Verträge, Baselines; Pflichtquelle für §3.4.1 |

#### 3.14.10 CI-Jobs

| Job | Auslöser | Inhalt | Zeitbudget |
|---|---|---|---|
| `css-diff` | jeder PR mit Änderungen unter `FE/` | §3.2.5 | ≤ 3 min |
| `gallery-visual` | PR mit Änderungen in `libs/shared/{propel,blocks,tailwind-config,theme}` | Galerie-Stories der betroffenen Komponenten (Sheriff-Abhängigkeitsgraph) | ≤ 10 min (4 Shards) |
| `screens-visual` | jeder PR | Katalog-Einträge mit Tag der geänderten Domänen-Libs + alle `accepted`-Einträge mit Tag `smoke` (Shell, 1 Eintrag je Domäne) | ≤ 15 min (4 Shards) |
| `screens-visual-full` | nightly + vor jeder Inkrement-Abnahme | gesamter Katalog, alle Themes/Viewports, `deviceScaleFactor` 1 und 2 | ≤ 120 min |
| `capture-reference` | manuell (Workflow-Dispatch) bei Katalog-/Seed-Änderung | Referenzumgebung starten, seeden, Baselines/Verträge aufnehmen, als PR einchecken | ≤ 90 min |
| `visual-report` | nach jedem Visual-Job | HTML-Report als CI-Artefakt, Statusübersicht je Inkrement | – |

---

## 4. Vollständige Mapping-Tabellen Original → Ziel

Spaltenlegende: **Inkr.** = Inkrement, in dem der Baustein fertig sein muss (§1.4). **CE** = CE-Feature-IDs. Für jede Zeile gilt zusätzlich CE-I18N-019 (Propel) bzw. CE-I18N-020 (Blocks), auch wenn nicht wiederholt.

### 4.1 Style-Dateien

| Original | Ziel (`funk.`) | Übernahme | Inkr. | CE |
|---|---|---|---|---|
| `PROPEL/styles/propel.css` (24 Z.) | `TWT/propel-styles/propel.css` | 1:1, `@source "../"` → `@source "../propel-dist-classes.txt"` | I0 | CE-I18N-009 |
| `PROPEL/styles/variables.css` (1 876 Z.) | `TWT/propel-styles/variables.css` | 1:1 | I0 | CE-I18N-005, -008, -009, -011, -024 |
| `PROPEL/styles/animations.css` (266 Z.) | `TWT/propel-styles/animations.css` | 1:1 | I0 | CE-I18N-023 |
| `TWC/index.css` (241 Z.) | `TWT/index.css` | 1:1, Importe/Source umgeschrieben (§3.2.3) | I0 | CE-I18N-009, -024 |
| `TWC/postcss.config.js` | `FE/.postcssrc.json` | inhaltsgleich als JSON | I0 | – |
| `TWC/AGENTS.md` (Flächenhierarchie) | `FE/libs/shared/tailwind-config/DESIGN-RULES.md` | 1:1 kopiert, Review-Checkliste (§6.2) | I0 | – |
| `WEB/styles/globals.css` (169 Z.) | `FE/apps/web/src/styles.css` | 1:1, Importe umgeschrieben | I0 | CE-I18N-023, -026 |
| `WEB/styles/emoji.css` (53 Z.) | `FE/apps/web/src/styles/emoji.css` | 1:1 (wirkungslos, solange kein `.EmojiPickerReact` gerendert wird – wie Original) | I0 | – |
| `WEB/styles/power-k.css` (27 Z.) | `FE/apps/web/src/styles/power-k.css` | 1:1; Power-K-Komponente rendert `cmdk`-Attribute (`[cmdk-group]`, `[cmdk-group-heading]`, `[cmdk-item]`, `aria-selected`, `aria-disabled`, `data-disabled`) | I0 (CSS), I5 (Komponente) | CE-SRCH (Power-K) |
| `ADM/styles/globals.css` (47 Z.) | `FE/apps/admin/src/styles.css` | 1:1 inkl. doppeltem Propel-Import und Admin-`.progress-bar` (E-27) | I0 | CE-INST |
| `SPC/styles/globals.css` (47 Z.) | `FE/apps/space/src/styles.css` | 1:1 | I0 | CE-SPACE |
| `packages/editor/src/styles/{index,variables,editor,table,drag-drop,title-editor,github-dark}.css` | `FE/libs/shared/editor/styles/*` | 1:1 (Inhalt → `10`) | I2 | CE-I18N-010 |
| `apps/api/plane/static/css/style.css` (leer) | – | entfällt | – | – |
| `@fontsource-variable/inter`, `@fontsource/ibm-plex-mono`, `@fontsource/material-symbols-rounded` (CSS der Pakete) | `angular.json` `styles` | unverändert aus `node_modules` | I0 | CE-I18N-012 |

### 4.2 Propel-Komponenten (68) → Angular

Ziel jeweils `PRP/components/<name>/`; Klassen-/Selektor-Regel §3.3.2 (Teil `X` → `PlX` / `[plX]`; Komposita ohne eigenes Element → `pl-<name>` + `data-pl-host`); Tag je Teil laut DOM-Vertrag (§3.4.1). „Unterbau“ nennt die Headless-Basis (§3.5, D09-ADR-10).

| # | Propel (`PROPEL/components/…`) | Angular-Teile | Unterbau | Inkr. | CE |
|---|---|---|---|---|---|
| 1 | `accordion` | `PlAccordion`, `PlAccordionHeader`, `PlAccordionItem`, `PlAccordionPanel`, `PlAccordionPanelContent`, `PlAccordionTrigger`, `PlAccordionTriggerTitle` | Angular-Aria-Accordion-Tastaturmodell, Höhe `--accordion-panel-height`, `PresenceController` | I7 | – |
| 2 | `alert-dialog` | `PlAlertDialog` (Host), `PlAlertDialogActionGroup`, `PlAlertDialogActions` (`layout`), `PlAlertDialogBody`, `PlAlertDialogClose`, `PlAlertDialogCloseGroup`, `PlAlertDialogContent` (`initialFocus`, `finalFocus`), `PlAlertDialogDescription`, `PlAlertDialogHeader`, `PlAlertDialogIcon` (`variant`), `PlAlertDialogIntro`, `PlAlertDialogTitle`, `PlAlertDialogTrigger`, `PlAlertDialogHandle` (= `createAlertDialogHandle`) | Portal, Backdrop, `FocusTrap`, Dismiss-Stack (kein Outside-Close), Scroll-Lock | I1 | CE-UIX-004, -008 |
| 3 | `anchor-button` | `PlAnchorButton` (`a[plAnchorButton]`; `disabled` entfernt `href`) | – | I1 | CE-UIX-013 |
| 4 | `autocomplete-field` | `PlAutocompleteField` | wie 5 + Field | I7 | – |
| 5 | `autocomplete` | `PlAutocomplete`, `PlAutocompleteCollection`, `PlAutocompleteContent`, `PlAutocompleteEmpty`, `PlAutocompleteGroup`, `PlAutocompleteGroupLabel`, `PlAutocompleteInput`, `PlAutocompleteInputGroup`, `PlAutocompleteItem`, `PlAutocompleteList`, `PlAutocompleteRow`, `PlAutocompleteStatus`; Funktionen `useFilter` → `createPlFilter()`, `useFilteredItems` → `filteredItems()` (Signal) | Angular-Aria-Combobox (Autocomplete-Modus), `ActiveDescendantKeyManager`, Floating | I7 | – |
| 6 | `avatar-group` | `PlAvatarGroup` (`size`, `max`=2, `total`, `label`, `overflowLabel`, `overflowTooltip`; Zähler ≤ +9) | `PlTooltipProvider` | I1 | CE-I18N-025 |
| 7 | `avatar` | `PlAvatar` (`size` Default md bzw. Gruppe; Initialen/Farbe aus `internal/avatar-shared`) | Bild-Ladezustand + `delay` | I0 | CE-I18N-025 |
| 8 | `badge` | `PlBadge`, `PlBadgeLabel` | – | I1 | – |
| 9 | `banner` | `PlBanner`, `PlBannerActions`, `PlBannerBody`, `PlBannerDescription`, `PlBannerIcon`, `PlBannerTitle` | – | I1 | – |
| 10 | `breadcrumb` | `PlBreadcrumb`, `PlBreadcrumbEllipsisTrigger`, `PlBreadcrumbItem`, `PlBreadcrumbLink`, `PlBreadcrumbList`, `PlBreadcrumbMenuTrigger`, `PlBreadcrumbPage`, `PlBreadcrumbSeparator` | Menu (für Trigger-Crumbs) | I0 | CE-UIX-001 |
| 11 | `button-group` | `PlButtonGroup` (`role="group"`, `size`-Kontext), `PlButtonGroupButton` | – | I7 | – |
| 12 | `button` | `PlButton` (`button[plButton], a[plButton]`; `variant`, `size`, `stretch`, `label` Pflicht; `icon`, `iconPosition`, `loading` → Spinner-Slot, `aria-busy`, `focusableWhenDisabled`; `type` Default `button`), `PlButtonLabel` | – | I0 | – |
| 13 | `calendar` | `PlCalendar` (`mode` single\|range, `weekStartsOn` 1, Klassenvertrag `calendarClassNames` aus `elements/calendar`) | Eigenbau mit DOM/Klassen von `react-day-picker` 10.0.1, `date-fns` 4.1 + Locale-Daten | I2 | CE-I18N-003 |
| 14 | `checkbox-field` | `PlCheckboxField` | Field | I1 | – |
| 15 | `checkbox-group-field` | `PlCheckboxGroupField`, `PlCheckboxGroupFieldOption` | Fieldset | I7 | – |
| 16 | `checkbox-group` | `PlCheckboxGroup` (`density`) | – | I7 | – |
| 17 | `checkbox` | `PlCheckbox` (`role="checkbox"`, `aria-checked` inkl. `mixed`), `PlCheckboxIndicator`, `PlCheckboxIndeterminateIndicator`, `PlCheckboxLabel` | CVA/Signal Forms | I1 | – |
| 18 | `circular-progress` | `PlCircularProgress` (`role="progressbar"`, `indeterminate`) | – | I2 | CE-I18N-026 |
| 19 | `collapsible` | `PlCollapsible`, `PlCollapsibleHeader`, `PlCollapsiblePanel` (`keepMounted`, `hiddenUntilFound`), `PlCollapsiblePanelContent`, `PlCollapsibleTrigger`, `PlCollapsibleTriggerTitle`, `PlCollapsibleTriggerTrailing` | `--collapsible-panel-height`, Presence | I0 | – |
| 20 | `combobox-field` | `PlComboboxField` (`selectAllLabel` wirkt auf **alle** `items`) | wie 21 | I7 | – |
| 21 | `combobox` | `PlCombobox`, `PlComboboxChip`, `PlComboboxChips`, `PlComboboxCollection`, `PlComboboxContent` (`side` bottom, `sideOffset` 4, `align` start, `sizing` anchor), `PlComboboxEmpty`, `PlComboboxGroup`, `PlComboboxGroupLabel`, `PlComboboxInputGroup`, `PlComboboxItem` (`selection` check\|checkbox), `PlComboboxItemIndicator`, `PlComboboxList`, `PlComboboxRow`, `PlComboboxSearch` (macht Overlay zum Dialog), `PlComboboxSelectAll`, `PlComboboxSeparator`, `PlComboboxStatus`, `PlComboboxStickyList`, `PlComboboxSubmenu`, `PlComboboxSubmenuContent`, `PlComboboxSubmenuTrigger`, `PlComboboxTrigger`; `createPlFilter()`, `filteredItems()` | Angular-Aria-Combobox/Listbox-Tastaturmodell, `ActiveDescendantKeyManager` (Fokus bleibt im Input), Floating, Portal, `@tanstack/virtual-core` | I0 | CE-UIX-004 |
| 22 | `context-menu` | `PlContextMenu`, `PlContextMenuCheckboxItem`, `PlContextMenuCheckboxItemIndicator`, `PlContextMenuContent`, `PlContextMenuGroup`, `PlContextMenuItem`, `PlContextMenuItemIndicator`, `PlContextMenuItemLabel`, `PlContextMenuLinkItem`, `PlContextMenuPopup`, `PlContextMenuRadioGroup`, `PlContextMenuRadioItem`, `PlContextMenuRadioItemIndicator`, `PlContextMenuSeparator`, `PlContextMenuSubmenu`, `PlContextMenuSubmenuContent`, `PlContextMenuSubmenuTrigger`, `PlContextMenuTrigger`; Typ `MenuRadioMarker` | wie Menu, virtueller Anker an Mausposition | I1 | CE-UIX-004 |
| 23 | `csp-provider` | `PlCspProvider` → Angular `CSP_NONCE`-Token (Provider-Funktion `provideCspNonce()`) | – | I7 | – |
| 24 | `dialog` | `PlDialog` (`discard`), `PlDialogActions`, `PlDialogAside`, `PlDialogBody`, `PlDialogClose`, `PlDialogCloseGroup`, `PlDialogContent` (`size` xs…full, `height`, `density`), `PlDialogDescription`, `PlDialogHeader`, `PlDialogHeading`, `PlDialogInfo`, `PlDialogInfoIcon`, `PlDialogMain`, `PlDialogPanes`, `PlDialogProgression`, `PlDialogTitle`, `PlDialogToolbar`, `PlDialogTrigger`, `PlDialogHandle`; Typen `DialogDiscard`, `DialogImperativeActions` | Portal, Backdrop, `FocusTrap`, Dismiss-Stack, Discard-Guard (AlertDialog, Default-Texte aus `A13a` §2.22) | I0 | CE-UIX-003, -004, -008 |
| 25 | `direction-provider` | `PlDirectionProvider` → CDK `Directionality` (`provideDirection('rtl'\|'ltr')`) | CDK bidi | I7 | – |
| 26 | `drawer` | `PlDrawer` (`modal` false), `PlDrawerBackdrop`, `PlDrawerBody`, `PlDrawerClose`, `PlDrawerContent`, `PlDrawerDescription`, `PlDrawerFooter`, `PlDrawerHandle`, `PlDrawerHeader`, `PlDrawerHeaderActions`, `PlDrawerHeaderContent`, `PlDrawerHeaderIcon`, `PlDrawerHeaderStart`, `PlDrawerIndent`, `PlDrawerIndentBackground`, `PlDrawerInlineHost`, `PlDrawerInlinePortal`, `PlDrawerPanel` (`variant`, `side`, `size`), `PlDrawerPopup`, `PlDrawerProvider`, `PlDrawerSwipeArea`, `PlDrawerTitle`, `PlDrawerTrigger`, `PlDrawerViewport`, `PlDrawerHandle` (= `createDrawerHandle`) | Portal/Inline-Portal, Swipe (Pointer-Events, `data-swipe-direction`), `FocusTrap` (modal) | I7 | – |
| 27 | `expandable-search` | `PlExpandableSearch` (`inert`, Grid-Spaltenanimation) | wie Autocomplete | I7 | – |
| 28 | `field` | `PlField` (`size`, `invalid`), `PlFieldControl`, `PlFieldDescription`, `PlFieldError`, `PlFieldHelperText`, `PlFieldItem`, `PlFieldItemContent`, `PlFieldLabel`, `PlFieldLabelGroup`, `PlFieldValidity` | Signal Forms/CVA, Kontext-Signal (§3.6) | I0 | CE-UIX-005 |
| 29 | `fieldset` | `PlFieldset`, `PlFieldsetBody`, `PlFieldsetDescription`, `PlFieldsetLegend` | – | I7 | – |
| 30 | `form` | `PlForm`, `PlFormActions`, `PlFormBody` | Signal Forms | I7 | – |
| 31 | `icon-button` | `PlIconButton` (`button[plIconButton], a[plIconButton]`; `aria-label` Pflicht, `loading` ersetzt Icon) | – | I0 | – |
| 32 | `icon-split-button` | `PlIconSplitButton` (innerhalb `pl-menu`) | Button + MenuTrigger | I7 | – |
| 33 | `icon` | `PlIcon` (`span[plIcon]`, `aria-hidden`; `tint`, `size`) – rendert `svg[plIcon]` (§3.7) im Node-Slot | – | I0 | CE-I18N-013 |
| 34 | `input-field` | `PlInputField` (`size`, `orientation` Pflicht; `required` ohne natives `required`) | Field | I0 | CE-UIX-005 |
| 35 | `input` | `PlInput` (`input[plInput]`), `PlInputGroup` | CVA/Signal Forms | I0 | – |
| 36 | `linear-progress` | `PlLinearProgress` (`role="progressbar"`) | – | I2 | CE-UIX-009, CE-I18N-026 |
| 37 | `list` | `PlList`, `PlListItem` (`level` 1–5, `density`), `PlListItemButton`, `PlListItemCounter`, `PlListItemDisclosureTrigger`, `PlListItemLabel`, `PlListItemLink`, `PlListSection`, `PlListSectionHeading`, `PlListSectionPanelContent`, `PlListSectionTrigger` | `PlComposite` (Roving-Tabindex), Collapsible | I7 (vorgezogen durch D2, §6.1) | – |
| 38 | `logo-spinner` | `PlLogoSpinner` (`size` sm\|md\|fluid, 4 Bilder, CSS wählt Theme × Motion; GIF/PNG aus `PROPEL/components/logo-spinner/*.{gif,png}` als Assets) | – | I0 | CE-I18N-026 |
| 39 | `menu` | `PlMenu`, `PlMenuCheckboxItem`, `PlMenuCheckboxItemIndicator`, `PlMenuContent` (`side` bottom, `sideOffset` 6, `collisionPadding` 8, `sizing` auto, `heightBehavior` fit), `PlMenuFooter`, `PlMenuGroup`, `PlMenuHandle`, `PlMenuItem` (`variant`, `icon`, `label`, `description`, `secondaryText`, `trailing`, `selected` → `menuitemradio`), `PlMenuItemContent`, `PlMenuItemControl`, `PlMenuItemDescription`, `PlMenuItemIndicator`, `PlMenuItemSecondaryText`, `PlMenuItemTitle`, `PlMenuItemTitleRow`, `PlMenuItemTrailing`, `PlMenuLabel`, `PlMenuLabelMeta`, `PlMenuLabelTitle`, `PlMenuLinkItem`, `PlMenuPopup`, `PlMenuRadioGroup`, `PlMenuRadioItem`, `PlMenuRadioItemIndicator`, `PlMenuSearch`, `PlMenuSearchInput`, `PlMenuSeparator`, `PlMenuSubmenu`, `PlMenuSubmenuContent`, `PlMenuSubmenuTrigger`, `PlMenuTrigger`, `PlMenuViewport`; Typ `MenuRadioMarker` | Angular-Aria-Menu-Tastaturmodell (Typeahead, Pfeiltasten, Submenü →/←), Floating (`fit`-Seitenwahl), Portal, Hover-Intent, Hold-Width | I0 | CE-UIX-004 |
| 40 | `navigation-menu` | `PlNavigationMenu`, `PlNavigationMenuContent`, `PlNavigationMenuContentList`, `PlNavigationMenuIcon`, `PlNavigationMenuItem`, `PlNavigationMenuLink` (`appearance`), `PlNavigationMenuLinkDescription`, `PlNavigationMenuLinkTitle`, `PlNavigationMenuList`, `PlNavigationMenuPanel`, `PlNavigationMenuTrigger`, `PlNavigationMenuTriggerLabel`, `PlNavigationMenuViewport` | Eigenbau (Viewport `--popup-width/height`), Floating | I7 | – |
| 41 | `number-field` | `PlNumberField`, `PlNumberFieldGroup`, `PlNumberFieldInput`, `PlNumberFieldScrubArea`, `PlNumberFieldScrubAreaCursor`; Konstante `numberFieldStepperSize` | Eigenbau (`Intl.NumberFormat`, Pointer-Lock für Scrub) | I7 (vorgezogen durch A1) | – |
| 42 | `otp-field` | `PlOTPField`, `PlOTPFieldInput`, `PlOTPFieldLabel`, `PlOTPFieldSeparator` | Eigenbau | I7 | – |
| 43 | `pagination` | `PlPagination` (Fenster-Algorithmus `A13a` §3.8, Labels-Defaults), Typ `PaginationLabels` | Menu (Per-Page) | I7 (vorgezogen durch E7) | – |
| 44 | `pill` | `PlPill`, `PlIconPill`, `PlPillGroup`, `PlPillLabel` | – | I1 | – |
| 45 | `popover` | `PlPopover` (`modal` false), `PlPopoverBody`, `PlPopoverClose`, `PlPopoverContent` (`variant` rich\|text, `side` bottom, `align` start, `sideOffset` 4, `collisionPadding` 5), `PlPopoverDescription`, `PlPopoverHandle`, `PlPopoverTitle`, `PlPopoverTrigger` | Floating, Portal, Dismiss, optional `FocusTrap` | I0 | CE-UIX-004 |
| 46 | `preview-card` | `PlPreviewCard`, `PlPreviewCardBody`, `PlPreviewCardContent`, `PlPreviewCardDescription`, `PlPreviewCardEyebrow`, `PlPreviewCardEyebrowLabel`, `PlPreviewCardHandle`, `PlPreviewCardImage`, `PlPreviewCardMeta`, `PlPreviewCardPropertyGroup`, `PlPreviewCardTitle`, `PlPreviewCardTrigger` | Floating, Hover-Delays | I2 | CE-UIX-013 |
| 47 | `radio-group-field` | `PlRadioGroupField`, `PlRadioGroupFieldOption` | Fieldset | I7 | – |
| 48 | `radio` | `PlRadio`, `PlRadioGroup` (`density`), `PlRadioIndicator`, `PlRadioRing` | `FocusKeyManager` (Roving) | I1 | – |
| 49 | `scroll-area` | `PlScrollArea` (`orientation` Pflicht, `visibility`, `size`) | Eigenbau nach Base-UI-Logik (Thumb-Größe, `data-scrolling`, `data-hovering`, `data-overflow-*`) | I0 | CE-I18N-024 |
| 50 | `select-field` | `PlSelectField`, Typ `SelectFieldOption` | wie 51 + Field | I7 | – |
| 51 | `select` | `PlSelect`, `PlSelectContent`, `PlSelectField`, `PlSelectGroup`, `PlSelectGroupLabel`, `PlSelectItem`, `PlSelectItemIndicator`, `PlSelectLabel`, `PlSelectList`, `PlSelectTrigger` (`variant`, `size`; `min-w-72`) | Angular-Aria-Select/Listbox, Floating mit `alignItemWithTrigger` | I1 | – |
| 52 | `separator` | `PlSeparator` (`orientation`, `decorative` Pflicht) | – | I0 | – |
| 53 | `shortcut` | `PlShortcut` (`keys`, `size`; `aria-hidden`) | – | I0 | – |
| 54 | `skeleton` | `PlSkeleton` (`aria-label` Pflicht, `role="status"`), `PlSkeletonItem` | – | I7 | CE-UIX-002 |
| 55 | `slider` | `PlSlider`, `PlSliderControl`, `PlSliderHeader`, `PlSliderIndicator`, `PlSliderLabel`, `PlSliderThumb`, `PlSliderTrack`, `PlSliderValue` | Eigenbau (Pointer-Capture, Tastatur-Schritte) | I7 | – |
| 56 | `split-button` | `PlSplitButton` | Button + MenuTrigger | I7 | – |
| 57 | `suggestion-menu` | `PlSuggestionMenu`, `PlSuggestionMenuGroup`, `PlSuggestionMenuItem`; Typ `SuggestionMenuActions` (`handleKeyDown`) | Eigenbau (Fokus bleibt im Eingabefeld, `loopFocus`) | I2 | – |
| 58 | `switch-field` | `PlSwitchField` | Field | I7 | – |
| 59 | `switch` | `PlSwitch` (`role="switch"`, `size` Pflicht), `PlSwitchThumb`, `PlSwitchTrack` | CVA/Signal Forms | I1 | – |
| 60 | `table` | `PlTable` (`variant` Pflicht), `PlTableActionCell`, `PlTableBody`, `PlTableCell`, `PlTableEditableCell`, `PlTableHead`, `PlTableHeadSort`, `PlTableHeader`, `PlTableRow`, `PlTableSelectCell`, `PlTableSelectHead`, `PlTableSkeletonBody`, `PlTableSkeletonCell` | ScrollArea, Sticky/Pinned-Schatten | I1 | – |
| 61 | `tabs` | `PlTabs` (`variant` Pflicht, `stretch`, `layout`), `PlTab`, `PlTabsIndicator` (`--active-tab-*`), `PlTabsList`, `PlTabsListScrollArea`, `PlTabsPanel` | Angular-Aria-Tabs, ScrollArea | I0 | – |
| 62 | `text-area-field` | `PlTextAreaField` | Field | I1 | CE-UIX-005 |
| 63 | `text-area` | `PlTextArea` (`textarea[plTextArea]`; `autoResize`, `maxRows`), `PlTextAreaGroup` | – | I0 | – |
| 64 | `toast` | `PlToast`, `PlToastActionPart`, `PlToastActionButton`, `PlToastActionGroup`, `PlToastActions`, `PlToastCloseGroup`, `PlToastContent`, `PlToastDescription`, `PlToastElement`, `PlToastList`, `PlToastProvider` (`close`), `PlToastStatusIcon`, `PlToastTextGroup`, `PlToastTitle`, `PlToastViewport`; `PlToastManager` (= `createToastManager`), `injectToast()` (= `useToast`), `injectToastManager()` (= `useToastManager`); Typen `ToastAction`, `ToastData` | §3.10 | I0 | CE-I18N-021, CE-WI-006 |
| 65 | `toggle` | `PlToggle`, `PlIconToggle`, `PlToggleLabel` (`data-pressed`) | – | I1 | – |
| 66 | `toolbar` | `PlToolbar` (`size`, `elevation` Pflicht), `PlToolbarButton`, `PlToolbarGroup`, `PlToolbarInput`, `PlToolbarItemLabel`, `PlToolbarLink`, `PlToolbarMenuTrigger`, `PlToolbarMenuTriggerButton`, `PlToolbarMenuTriggerLabel`, `PlToolbarSeparator`, `PlToolbarToggle`, `PlToolbarToggleGroup` | Angular-Aria-Toolbar (Roving Focus) | I2 | – |
| 67 | `tooltip` | `PlTooltip` (Host; `label`, `disabled`, `shortcut`, `layout`, `side` top, `sideOffset` 8, `showArrow`, `delay`), `PlTooltipArrow`, `PlTooltipHandle`, `PlTooltipPopup` (`role="tooltip"`), `PlTooltipProvider` | Floating (`hide` → `data-anchor-hidden:invisible`), Delay-Gruppe, `aria-describedby` am Trigger nur solange Popup gemountet | I0 | – |
| 68 | `workspace-avatar` | `PlWorkspaceAvatar` (Fallback-Icon lucide 1.34 `Building2`) | wie Avatar | I0 | – |

### 4.3 Propel-Elemente (57) → Angular-Direktiven

Ziel `PRP/elements/<name>/`: `variants.ts` (**generiert**, D09-ADR-05) + je Teil eine Attribut-Direktive (`PlXEl`, Selektor `[plXEl]`, wenn eine gleichnamige Komponente existiert, sonst `PlX`/`[plX]`). Die Direktive setzt nur `class` (aus `cva`), statische `data-*` und `role`, keine Logik.

| Element | Angular-Direktiven | Achsen (aus `variants.ts`) | Inkr. |
|---|---|---|---|
| `accordion` | `PlAccordionEl`, `PlAccordionHeaderEl`, `PlAccordionItemEl`, `PlAccordionPanelEl`, `PlAccordionPanelContentEl`, `PlAccordionTriggerEl`, `PlAccordionTriggerTitleEl` | – | I7 |
| `alert-dialog` | `PlAlertDialogActionGroupEl`, `…ActionsEl`, `…BackdropEl`, `…BodyEl`, `…CloseEl`, `…CloseGroupEl`, `…DescriptionEl`, `…HeaderEl`, `…IconEl`, `…IntroEl`, `…PopupEl`, `…TitleEl`, `…ViewportEl` | Icon `variant`; Actions `layout` | I1 |
| `anchor-button` | `PlAnchorButtonEl`, `PlAnchorButtonLabelEl` | `variant`, `size` | I1 |
| `autocomplete` | `PlAutocompleteEmptyEl`, `PlAutocompleteInputEl`, `PlAutocompleteInputGroupEl`, `PlAutocompleteInputGroupClearEl` | InputGroup `size` | I7 |
| `avatar-group` | `PlAvatarGroupEl`, `PlAvatarGroupCounterEl`, `PlAvatarGroupOverflowEl` | Counter `size` | I1 |
| `avatar` | `PlAvatarEl`, `PlAvatarFallbackEl`, `PlAvatarImageEl`; Konstanten `AVATAR_VARIANTS`, `getAvatarVariantSeed`, `getAvatarVariant` | `size`, Fallback `variant` | I0 |
| `badge` | `PlBadgeEl`, `PlBadgeLabelEl` | `size`, `variant` | I1 |
| `banner` | `PlBannerEl`, `PlBannerActionsEl`, `PlBannerBodyEl`, `PlBannerDescriptionEl`, `PlBannerIconEl`, `PlBannerTitleEl` | `placement`, `size`, `variant` | I1 |
| `breadcrumb` | `PlBreadcrumbEl`, `PlBreadcrumbItemEl`, `PlBreadcrumbLinkEl`, `PlBreadcrumbListEl`, `PlBreadcrumbPageEl`, `PlBreadcrumbSeparatorEl`, `PlBreadcrumbTrigger`, `PlBreadcrumbTriggerIndicator` | Trigger `group` | I0 |
| `button-group` | `PlButtonGroupEl`, `PlButtonGroupButtonEl` | `size` | I7 |
| `button` | `PlButtonEl`, `PlButtonLabelEl` | `variant` (6), `size` (4), `stretch` (2) | I0 |
| `calendar` | Konstante `calendarClassNames` (Klassenvertrag für `PlCalendar`) | – | I2 |
| `checkbox-group` | `PlCheckboxGroupEl` | `density` | I7 |
| `checkbox` | `PlCheckboxEl`, `PlCheckboxIndeterminateIndicatorEl`, `PlCheckboxIndicatorEl`, `PlCheckboxLabelEl` | Label `stretch` | I1 |
| `circular-progress` | `PlCircularProgressEl`, `PlCircularProgressIndicator`, `PlCircularProgressSvg`, `PlCircularProgressTrack` | `size`, `variant` | I2 |
| `collapsible` | `PlCollapsibleEl`, `PlCollapsibleHeaderEl`, `PlCollapsiblePanelEl`, `PlCollapsiblePanelContentEl`, `PlCollapsibleTriggerEl`, `PlCollapsibleTriggerTitleEl`, `PlCollapsibleTriggerTrailingEl` | `placement` | I0 |
| `combobox` | `PlComboboxCheckboxItemIndicator`, `PlComboboxChipEl`, `PlComboboxChipOverflow`, `PlComboboxChipsEl`, `PlComboboxEmptyEl`, `PlComboboxInput`, `PlComboboxInputGroupEl`, `PlComboboxInputGroupClear`, `PlComboboxItemEl`, `PlComboboxItemContent`, `PlComboboxItemControl`, `PlComboboxItemIndicatorEl`, `PlComboboxItemTitle`, `PlComboboxItemTrailing`, `PlComboboxPopup`, `PlComboboxSearchEl`, `PlComboboxSearchInput`, `PlComboboxSeparatorEl`, `PlComboboxStickyListEl`, `PlComboboxSubmenuTriggerEl`, `PlComboboxTriggerEl`, `PlComboboxValue` | Frames `variant` u. a. | I0 |
| `context-menu` | `PlContextMenuCheckboxItemEl`, `…CheckboxItemIndicatorEl`, `…ItemEl`, `…ItemContent`, `…ItemDescription`, `…ItemIndicatorEl`, `…ItemLabelEl`, `…ItemTrailing`, `…LinkItemEl`, `…PopupEl`, `…RadioItemEl`, `…RadioItemCheck`, `…RadioItemIndicatorEl`, `…SeparatorEl`, `…SubmenuTriggerEl` | Item `layout`, `variant` | I1 |
| `dialog` | `PlDialogActionsEl`, `PlDialogAsideEl`, `PlDialogBodyEl`, `PlDialogCloseGroupEl`, `PlDialogDescriptionEl`, `PlDialogHeaderEl`, `PlDialogHeadingEl`, `PlDialogInfoEl`, `PlDialogInfoIconEl`, `PlDialogMainEl`, `PlDialogPanesEl`, `PlDialogPopup`, `PlDialogProgressionEl`, `PlDialogTitleEl`, `PlDialogToolbarEl`, `PlDialogViewport` | Popup `size`, `height`, `density` | I0 |
| `drawer` | `PlDrawerBodyEl`, `PlDrawerCloseEl`, `PlDrawerContentEl`, `PlDrawerFooterEl`, `PlDrawerHeaderEl`, `PlDrawerHeaderActionsEl`, `PlDrawerHeaderContentEl`, `PlDrawerHeaderIconEl`, `PlDrawerHeaderStartEl`, `PlDrawerInlineHostEl`, `PlDrawerInlinePortalEl`, `PlDrawerPopupEl`, `PlDrawerViewportEl` | Viewport/Popup `variant`, `side`, `size` | I7 |
| `expandable-search` | `PlExpandableSearchRow`, `PlExpandableSearchTrack`, `PlExpandableSearchTrigger` | Trigger `size` | I7 |
| `field` | `PlFieldEl`, `PlFieldControlContent`, `PlFieldDescriptionEl`, `PlFieldErrorEl`, `PlFieldItemEl`, `PlFieldItemContentEl`, `PlFieldItemControlGroup`, `PlFieldLabelEl`, `PlFieldLabelGroupEl`, `PlFieldLabelRequiredMarker` | `size` | I0 |
| `fieldset` | `PlFieldsetEl`, `PlFieldsetBodyEl`, `PlFieldsetDescriptionEl`, `PlFieldsetLegendEl` | `bordered`, Legend-`size` | I7 |
| `form` | `PlFormEl`, `PlFormActionsEl`, `PlFormBodyEl` | Body `layout`, Actions `layout` | I7 |
| `icon-button` | `PlIconButtonEl` | `variant` (6), `size` (4) | I0 |
| `input-field` | `PlInputFieldEl` | `orientation` | I0 |
| `input` | `PlInputEl`, `PlInputGroupEl` | `size` | I0 |
| `linear-progress` | `PlLinearProgressEl`, `PlLinearProgressIndicator`, `PlLinearProgressLabel`, `PlLinearProgressTrack`, `PlLinearProgressValue` | Track `size`, `variant` | I2 |
| `list` | `PlListEl`, `PlListItemEl`, `PlListItemButtonEl`, `PlListItemCounterEl`, `PlListItemDisclosureTriggerEl`, `PlListItemLabelEl`, `PlListItemLinkEl`, `PlListSectionHeadingEl`, `PlListSectionPanelContentEl`, `PlListSectionTriggerEl` | Item `level`, `density` | I7 |
| `logo-spinner` | `PlLogoSpinnerEl`, `PlLogoSpinnerImage` | Image `size` | I0 |
| `menu` | `PlMenuCheckboxItemEl`, `…CheckboxItemIndicatorEl`, `PlMenuFooterEl`, `PlMenuItemEl`, `PlMenuItemContentEl`, `PlMenuItemControlEl`, `PlMenuItemDescriptionEl`, `PlMenuItemIndicatorEl`, `PlMenuItemSecondaryTextEl`, `PlMenuItemTitleEl`, `PlMenuItemTitleRowEl`, `PlMenuItemTrailingEl`, `PlMenuLabelEl`, `PlMenuLabelMetaEl`, `PlMenuLabelTitleEl`, `PlMenuLinkItemEl`, `PlMenuPopupEl`, `PlMenuRadioItemEl`, `PlMenuRadioItemCheck`, `PlMenuRadioItemIndicatorEl`, `PlMenuSearchEl`, `PlMenuSearchInputEl`, `PlMenuSeparatorEl`, `PlMenuSubmenuTriggerEl` | Item `layout`, `variant`; Popup `elevation` | I0 |
| `navigation-menu` | `PlNavigationMenuContentListEl`, `…IconEl`, `…LinkEl`, `…LinkDescriptionEl`, `…LinkTitleEl`, `…ListEl`, `…Popup`, `…TriggerEl`, `…TriggerLabelEl`, `…ViewportEl` | Link `appearance` | I7 |
| `number-field` | `PlNumberFieldEl`, `PlNumberFieldGroupEl`, `PlNumberFieldInputEl`; `numberFieldStepperSize` | `size` | I7 |
| `otp-field` | `PlOTPFieldEl`, `PlOTPFieldInputEl`, `PlOTPFieldLabelEl`, `PlOTPFieldSeparatorEl` | Input `size` | I7 |
| `pagination` | `PlPaginationEl`, `PlPaginationArrowButton`, `PlPaginationEllipsis`, `PlPaginationItem`, `PlPaginationList`, `PlPaginationPageButton`, `PlPaginationPerPage`, `PlPaginationPerPageLabel`, `PlPaginationPerPageTrigger`, `PlPaginationRange`, `PlPaginationRangeCurrent`, `PlPaginationSpinner` | – | I7 |
| `pill` | `PlIconPillEl`, `PlPillEl`, `PlPillGroupEl`, `PlPillLabelEl` | Pill `size`, `variant` | I1 |
| `popover` | `PlPopoverBodyEl`, `PlPopoverPopup`, `PlPopoverTitleEl` | Popup `variant` | I0 |
| `preview-card` | `PlPreviewCardBodyEl`, `…EyebrowEl`, `…EyebrowLabelEl`, `…ImageEl`, `…MetaEl`, `…Popup`, `…PropertyGroupEl`, `…TitleEl` | – | I2 |
| `radio` | `PlRadioEl`, `PlRadioGroupEl`, `PlRadioIndicatorEl` | Group `density` | I1 |
| `scroll-area` | `PlScrollAreaEl`, `PlScrollAreaCorner`, `PlScrollAreaScrollbar`, `PlScrollAreaThumb`, `PlScrollAreaViewport` | Scrollbar `visibility`, `size` | I0 |
| `select` | `PlSelectFieldEl`, `PlSelectItemIndicatorEl`, `PlSelectLabelEl`, `PlSelectTriggerEl`, `PlSelectValue` | Trigger `variant`, `size` | I1 |
| `separator` | `PlSeparatorEl` | – | I0 |
| `skeleton` | `PlSkeletonEl`, `PlSkeletonItemEl`; `skeletonFrameProps`, `skeletonItemFrameProps` | Frame `layout`, `stretch`; Item `variant` | I7 |
| `slider` | `PlSliderEl`, `PlSliderControlEl`, `PlSliderHeaderEl`, `PlSliderIndicatorEl`, `PlSliderLabelEl`, `PlSliderThumbEl`, `PlSliderTrackEl`, `PlSliderValueEl` | Control/Thumb `size` | I7 |
| `split-button` | `PlSplitButtonEl` | `variant`, `size` | I7 |
| `suggestion-menu` | `PlSuggestionMenuEl`, `PlSuggestionMenuGroupEl`, `PlSuggestionMenuItemEl`, `PlSuggestionMenuItemIcon`, `PlSuggestionMenuItemTitle`, `PlSuggestionMenuItemTrailing`, `PlSuggestionMenuLabel` | – | I2 |
| `swatch` | `PlSwatch` (nur Element, `--swatch-fill`) | – | I1 |
| `switch` | `PlSwitchEl`, `PlSwitchThumbEl` | `size` | I1 |
| `table` | `PlTableEl`, `PlTableBodyEl`, `PlTableCellEl`, `PlTableCellContent`, `PlTableCellLayout`, `PlTableCellTrigger`, `PlTableCellTriggerIndicator`, `PlTableCellTriggerLabel`, `PlTableHeadEl`, `PlTableHeadSortIndicator`, `PlTableHeadSortTrigger`, `PlTableHeadTitle`, `PlTableHeaderEl`, `PlTableRowEl`, `PlTableScrollArea`, `PlTableScrollAreaViewport`, `PlTableSelectLayout`, `PlTableSkeletonBodyEl` | Row `selected`, `interactive`, `section`; Head `variant` | I1 |
| `tabs` | `PlTabEl`, `PlTabUnderlineBar`, `PlTabUnderlineBarTrack`, `PlTabUnderlineLabel`, `PlTabsEl`, `PlTabsIndicatorEl`, `PlTabsListEl`, `PlTabsListScrollAreaEl`, `PlTabsPanelEl` | `variant`, `stretch`, `layout` | I0 |
| `text-area-field` | `PlTextAreaFieldEl` | – | I1 |
| `text-area` | `PlTextAreaEl`, `PlTextAreaGroupEl` | Group `resize`; `size`, `surface` | I0 |
| `toast` | `PlToastEl`, `PlToastActionEl`, `PlToastActionButtonEl`, `PlToastActionGroupEl`, `PlToastActionsEl`, `PlToastCloseGroupEl`, `PlToastContentEl`, `PlToastDescriptionEl`, `PlToastStatusIconEl`, `PlToastTextGroupEl`, `PlToastTitleEl`, `PlToastViewportEl` | StatusIcon `variant` | I0 |
| `toggle` | `PlIconToggleEl`, `PlToggleEl`, `PlToggleLabelEl` | IconToggle `variant`, `size` | I1 |
| `toolbar` | `PlToolbarEl`, `PlToolbarButtonEl`, `PlToolbarGroupEl`, `PlToolbarInputEl`, `PlToolbarItemLabelEl`, `PlToolbarLinkEl`, `PlToolbarMenuTriggerButtonEl`, `PlToolbarMenuTriggerLabelEl`, `PlToolbarSeparatorEl`, `PlToolbarToggleGroupEl` | `elevation`, `size` | I2 |
| `tooltip` | `PlTooltipArrowEl`, `PlTooltipPopupEl` | Popup `layout` | I0 |
| `workspace-avatar` | `PlWorkspaceAvatarEl`, `PlWorkspaceAvatarFallbackEl`, `PlWorkspaceAvatarImageEl` | `size`, Fallback `variant` | I0 |

### 4.4 Propel `internal/` → `PRP/internal/`

„gen“ = von `port-variants.mjs` erzeugt (nur `cva`/Klassen), „Hand“ = handportierte Logik mit Unit-Test gegen das Original-JS.

| Original (`PROPEL/internal/…`) | Ziel | Art | Inhalt |
|---|---|---|---|
| `control-chrome.js` | `control-chrome.ts` | gen | `controlChromeVariants` (6 Varianten) |
| `button-geometry.js` | `button-geometry.ts` | gen | `buttonGeometryVariants` (`size`, `stretch`) |
| `compose-variants.js` | `compose-variants.ts` | Hand (3 Zeilen) | `composeVariants(shared, local)` |
| `variant-props.d.ts` | `variant-props.ts` | Hand | Typ `StrictVariantProps` |
| `control-group.js` | `control-group.ts` | gen | `controlGroupClass`, `controlSize` |
| `control-input.js` | `control-input.ts` | gen | `controlInputClass` |
| `field-control-surface.js` | `field-control-surface.ts` | gen | `fieldControlSurfaceVariants` |
| `surface.js` | `surface.ts` | gen | `surfaceVariants` |
| `popup-surface.js` | `popup-surface.ts` | gen | `popupSurfaceClass` |
| `overlay-panel.js` | `overlay-panel.component.ts` + `held-width.ts` | Hand | `PlOverlayPanel` (Header + ScrollArea + Footer), `useHeldWidth` → `heldWidth()` (ResizeObserver → `--popup-held-width`) |
| `backdrop.js` | `backdrop.directive.ts` | Hand | `PlBackdrop` (Klassen gen) |
| `positioner.js` | `positioner.directive.ts` | Hand | `PlPositioner` (`hideWhenAnchorHidden`) |
| `popup-viewport.js` | `popup-viewport.directive.ts` | gen | `relative` |
| `listbox-popup.js` | `listbox-popup.ts` | gen | `ListboxPopup`-Klassen |
| `listbox-item.js` | `listbox-item.ts` | gen | `layout`, `size` |
| `listbox-empty.js`, `listbox-status.js` | `listbox-empty.ts`, `listbox-status.ts` | gen | `listboxEmptyClass`, `ListboxStatus` |
| `listbox-group-label.js` | `listbox-group-label.ts` | gen | – |
| `menu-row-parts.js` | `menu-row-parts.ts` | gen | `menuListPopupVariants`, `menuRowBaseClass` u. a. |
| `checkbox-box.js` | `checkbox-box.ts` | gen | `checkboxBoxVariants` |
| `radio-circle.js`, `radio-dot.js` | `radio-circle.ts`, `radio-dot.component.ts` | gen / Hand | `radioCircleVariants`, `PlRadioDot` |
| `disclosure-indicator.js` | `disclosure-indicator.ts` | gen | `motion`, `tint` |
| `disclosure-trigger.js` | `disclosure-trigger.ts` | gen | `disclosureTriggerClass`, `…TitleClass` |
| `icon.js` | `icon.component.ts` | Hand | `PlIcon` (`tint`, `size`) |
| `node-slot.js` | `node-slot.ts` + `node-slot.directive.ts` | gen + Hand | `nodeSlotClass`, `PlNodeSlot` |
| `item-indicator.js` | `item-indicator.ts` | gen | – |
| `link-chrome.js` | `link-chrome.ts` | gen | `variant`, `size` |
| `list-item-primary.js` | `list-item-primary.ts` | gen | `data-list-item-primary` |
| `option-group.js` | `option-group.ts` | gen | `density` |
| `overlay-frame.js` | `overlay-frame.ts` | gen | `overlayActionsClass`, `overlayCloseClass` |
| `overlay-title.js`, `overlay-description.js` | `overlay-title.directive.ts`, `overlay-description.directive.ts` | gen + Hand | Tag `h2`/`p` |
| `shortcut.js` | `shortcut.component.ts` | Hand | `PlShortcutInternal` |
| `spinner.js` | `spinner.component.ts` | Hand | `PlSpinner` (`active`, Reveal/Conceal, 250-ms-Fallback) |
| `avatar-shared.js` | `avatar-shared.ts` | Hand | `getAvatarInitials` (`Intl.Segmenter`), `getFirstAvatarInitial`, Farbvarianten, Hash-Funktion (`A13a` §3.8) |
| `fit-side.js` | `fit-side.ts` | Hand | `resolveFitSide`, `usableSpace` |
| `external-link.js` | `external-link.ts` | Hand | `resolveExternalLinkProps` |
| `field-option-size.js` | `field-option-size.ts` | Hand | `PL_FIELD_OPTION_SIZE` (InjectionToken; Fehler wenn weder `size` noch Eltern-Feld) |
| `menu-radio-marker.js` | `menu-radio-marker.ts` | Hand | `PL_MENU_RADIO_MARKER` (Default `check`) |
| `solid-icons/*` | `solid-icons/*.ts` | gen (Icons) | `SolidCircleCheck`, `SolidCircleX`, `SolidInfo`, `SolidTriangleAlert`, `SolidCircleAlert` |

### 4.5 Propel `base/`, `hooks/`, `state-icons/`

| Original | Ziel | Angular | Inkr. | CE |
|---|---|---|---|---|
| `PROPEL/base/composite` (`Composite`, `CompositeItem`) | `PRP/base/composite/` | `PlComposite` (`[plComposite]`, `orientation` Default vertical), `PlCompositeItem` (`[plCompositeItem]`) auf CDK `FocusKeyManager` (Roving-Tabindex) | I0 | – |
| `PROPEL/hooks/use-controllable-state` | `PRP/hooks/controllable-state.ts` | `controllableState({ value, defaultValue, onChange })` für Komponenten ohne `model()` | I0 | – |
| `PROPEL/state-icons` (`StateGroupIcon`, `StartedGroupIcon`, `UnstartedGroupIcon`, Typen) | `PRP/state-icons/` | `PlStateGroupIcon` (`svg[plStateGroupIcon]`; `stateGroup`, `size` xs 10 · sm 12 · md 14 · lg 16 · xl 18, `percentage`), `PlStartedGroupIcon`, `PlUnstartedGroupIcon`; Progress-Glyph-Geometrie 1:1 (`A13a` §2.24) | I2 | CE-I18N-014 |

### 4.6 Propel-Icons (919) → generierte Konstanten

| Kategorie (`PROPEL/icons/<kat>/`) | Dateien | Ziel (`PRP/icons/<kat>/`) | Inkr. |
|---|---|---|---|
| `actions` | 166 | `actions/*.ts` | I0 |
| `arrows` | 77 | `arrows/*.ts` | I0 |
| `charts` | 10 | `charts/*.ts` | I0 |
| `cycle-states` | 3 | `cycle-states/*.ts` | I0 |
| `formatting-and-editors` | 86 | `formatting-and-editors/*.ts` | I0 |
| `initiative-states` | 5 | `initiative-states/*.ts` | I0 (für W5/W6 vorhanden) |
| `layouts` | 30 | `layouts/*.ts` | I0 |
| `milestone-states` | 3 | `milestone-states/*.ts` | I0 |
| `miscellaneous` | 342 | `miscellaneous/*.ts` | I0 |
| `module-states` | 6 | `module-states/*.ts` | I0 |
| `other-products` | 41 | `other-products/*.ts` | I0 |
| `placeholder` | 1 | `placeholder/*.ts` | I0 |
| `project-features` | 20 | `project-features/*.ts` | I0 |
| `properties` | 74 | `properties/*.ts` | I0 |
| `sub-brands` | 8 | `sub-brands/*.ts` | I0 |
| `work-item-states` | 3 | `work-item-states/*.ts` | I0 |
| `workspace-features` | 44 | `workspace-features/*.ts` | I0 |
| **Summe** | **919** | Barrel `PRP/icons/index.ts` (+ State-Icons, Typen) | – |

Die vollständige Namensliste je Kategorie steht in `A13a` §2.25 und wird vom Generator aus den Dateinamen erzeugt; `icons.golden.json` ist das maschinenlesbare Inventar (Prüfsumme: 919 Einträge). Alle Icons werden generiert, auch solche, die nur Bezahl-Features nutzen (`A13a` §1.4).

### 4.7 `@plane/blocks` → `libs/shared/blocks` (alle Dateien)

Ziel `BLKT/<gleicher Pfad>`; `*.tsx` → `*.component.ts` (+ `.html`, wenn Template > 15 Zeilen), reine Logik `*.ts` → `*.ts` (1:1 kopiert, React-Typen ersetzt), `use-*.ts`-Hooks → Funktionen/Services ohne `use`-Präfix. Klassenpräfix `PlBlk`, Selektor `pl-blk-…` bzw. `[plBlk…]` (vermeidet Namenskollisionen mit Propel: `ContextMenu`, `Breadcrumb*`, `Select`, `Skeleton`, `Spinner`, `MenuSearchInput`). Blocks-Komponenten nehmen `className` als Input und verarbeiten ihn mit `cn()`. Subpath-Importe bleiben (`@plane/blocks/<modul>`).

| Original (`BLK/…`) | Ziel-Datei (`BLKT/…`) | Angular-Baustein(e) | Inkr. | CE |
|---|---|---|---|---|
| `auth/oauth/oauth-button.tsx`, `auth/oauth/oauth-options.tsx`, `auth/password/helper.tsx`, `auth/password/indicator.tsx`, `auth/password/password-input.tsx`, `auth/index.ts` | – (kein Angular-Port) | **DOM-/Klassen-Vorlage** für das Keycloak-Login-Theme (`deploy/keycloak/themes/plane/login/*.ftl`, D09-ADR-14); OAuth-Buttons entfallen (ADR-008); Passwortfeld/-Stärke nur in Keycloak-Seiten | I0 | CE-AUTH-001 |
| `breadcrumb/breadcrumbs.tsx` | `breadcrumb/breadcrumbs.component.ts` | `PlBlkBreadcrumbs` (Kollaps ≤ 640 px), `PlBlkBreadcrumbItem`, `PlBlkBreadcrumbIcon`, `PlBlkBreadcrumbLabel`, `PlBlkBreadcrumbSeparator`, `PlBlkBreadcrumbItemWrapper` (E-25), `PlBlkBreadcrumbItemLoader` | I0 | CE-UIX-001 |
| `breadcrumb/breadcrumb-navigation-select.tsx` | `breadcrumb/breadcrumb-navigation-select.component.ts` | `PlBlkBreadcrumbNavigationSelect` | I0 | CE-UIX-001 |
| `breadcrumb/helpers.tsx`, `breadcrumb/breadcrumb-context.ts`, `breadcrumb/index.ts` | `breadcrumb/helpers.ts`, `breadcrumb-context.ts`, `public-api.ts` | `getCollapsedCrumb`; Label-Ermittlung aus projiziertem Inhalt (Textinhalt, Tiefe ≤ 4); `PL_BLK_BREADCRUMB_CONTEXT` | I0 | CE-UIX-001 |
| `card/card.tsx`, `card/helper.tsx`, `card/index.ts` | `card/card.component.ts`, `helper.ts` | `PlBlkCard` (`div[plBlkCard]`; `variant`, `spacing`, `direction`) | I1 | – |
| `charts/area-chart/root.tsx` | `charts/area-chart/area-chart.component.ts` | `PlBlkAreaChart` | I3 | CE-I18N-022 |
| `charts/bar-chart/root.tsx`, `charts/bar-chart/bar.tsx` | `charts/bar-chart/bar-chart.component.ts`, `bar-shape.component.ts` | `PlBlkBarChart`, `PlBlkBarShape` (`bar`, `lollipop`, `lollipop-dotted`) | I3 | CE-I18N-022 |
| `charts/line-chart/root.tsx` | `charts/line-chart/line-chart.component.ts` | `PlBlkLineChart` | I3 | CE-I18N-022 |
| `charts/pie-chart/root.tsx`, `active-shape.tsx`, `tooltip.tsx` | `charts/pie-chart/{pie-chart,active-shape,pie-tooltip}.component.ts` | `PlBlkPieChart`, `PlBlkPieActiveShape`, `PlBlkPieTooltip` | I3 | CE-I18N-022 |
| `charts/radar-chart/root.tsx` | `charts/radar-chart/radar-chart.component.ts` | `PlBlkRadarChart` | I3 | CE-I18N-022 |
| `charts/tree-map/root.tsx`, `map-content.tsx`, `tooltip.tsx` | `charts/tree-map/{tree-map,map-content,tree-map-tooltip}.component.ts` | `PlBlkTreeMapChart`, `PlBlkTreeMapContent`, `PlBlkTreeMapTooltip` | I3 | CE-I18N-022 |
| `charts/components/legend.tsx`, `tick.tsx`, `tooltip.tsx` | `charts/components/{legend,tick,tooltip}.component.ts` | `PlBlkChartLegend`, `PlBlkChartTick`, `PlBlkChartTooltip` | I3 | CE-I18N-022 |
| `charts/*/index.ts` (6) | `charts/*/public-api.ts` | Subpaths `@plane/blocks/charts/{area-chart,bar-chart,line-chart,pie-chart,radar-chart,tree-map}` | I3 | – |
| `common/color-picker/color-picker.tsx` | `common/color-picker/color-picker.component.ts` | `PlBlkColorPicker` (nativer `<input type="color">` hinter `conical-gradient`-Button) | I1 | CE-I18N-025 |
| `common/color-swatch-picker/color-swatch-picker.tsx`, `hex.ts`, `default-swatches.ts` | `common/color-swatch-picker/*` | `PlBlkColorSwatchPicker`, `parseHexColor`, `DEFAULT_SWATCH_COLORS` | I1 | CE-I18N-025 |
| `common/drag-handle.tsx` | `common/drag-handle.component.ts` | `PlBlkDragHandle` | I1 | – |
| `common/drop-indicator.tsx` | `common/drop-indicator.component.ts` | `PlBlkDropIndicator` | I1 | – |
| `common/favorite-star.tsx` | `common/favorite-star.component.ts` | `PlBlkFavoriteStar` | I1 | – |
| `common/sortable/sortable.tsx`, `draggable.tsx` | `common/sortable/{sortable.component,draggable.directive}.ts` | `PlBlkSortable`, `PlBlkDraggable` (auf `libs/shared/dnd`, pragmatic-dnd) | I1 | – |
| `common/popover-menu/helpers.ts`, `common/index.ts` | `common/popover-menu/helpers.ts` (`toSideAndAlign`), `public-api.ts` | – | I1 | – |
| `context-menu/context-menu.tsx`, `context-menu-item.tsx`, `helpers.ts`, `types.ts`, `index.ts` | `context-menu/*` | `PlBlkContextMenu` (`parent`-Input statt `parentRef`, mobil inaktiv), `PlBlkContextMenuItem` (E-26); Typen `TContextMenuItem`, `TContextMenuItemVariant` | I1 | CE-UIX-004 |
| `dialog/confirm-dialog.tsx`, `dialog/index.ts` | `dialog/confirm-dialog.component.ts` | `PlBlkConfirmDialog` (`variant` danger\|primary\|warning) | I1 | CE-UIX-004 |
| `emoji-icon-picker/emoji-picker.tsx` | `emoji-icon-picker/emoji-picker.component.ts` | `PlBlkEmojiPicker` (Popover `rich`, Tabs „Emoji“/„Icon“) | I1 | CE-I18N-016 |
| `emoji-icon-picker/emoji/emoji.tsx` | `emoji-icon-picker/emoji/emoji-panel.component.ts` | `PlBlkEmojiPanel` – Nachbau des `frimousse`-0.3.0-DOM (Suche, Kategorien, Skin-Tone, virtualisiertes Raster) auf lokalen Emojibase-Daten (§3.8.2); tote Klassen `hover:bg-accent`, `data-active:bg-accent` bleiben | I1 | CE-I18N-016 |
| `emoji-icon-picker/icon/icon-root.tsx`, `lucide-root.tsx`, `material-root.tsx` | `emoji-icon-picker/icon/{icon-panel,lucide-grid,material-grid}.component.ts` | `PlBlkIconPanel`, `PlBlkLucideIconGrid`, `PlBlkMaterialIconGrid` | I1 | CE-I18N-016 |
| `emoji-icon-picker/logo.tsx` | `emoji-icon-picker/logo.component.ts` | `PlBlkLogo` (`logo`, `size` 16, `type` material; Skelett bis Font geladen) | I1 | CE-I18N-016 |
| `emoji-icon-picker/lucide-icons.tsx`, `material-icons.tsx` | `emoji-icon-picker/{lucide-icons,material-icons}.ts` | `LUCIDE_ICONS_LIST` (157 `{name, icon: PlIconDef}` aus `icons-lucide/v0469`), `MATERIAL_ICONS_LIST` (200 Namen) – **Datenvertrag** (persistierte Namen) | I1 | CE-I18N-016 |
| `emoji-icon-picker/helper.tsx`, `data.ts`, `random-icon.ts`, `index.ts` | `emoji-icon-picker/{helper,data,random-icon}.ts` | `stringToEmoji`, `emojiToString`, `adjustColorForContrast`, `DEFAULT_COLORS`, `getRandomIconName`; Subpath `@plane/blocks/emoji-icon-picker/data` | I1 | CE-I18N-016 |
| `emoji-reaction/emoji-reaction.tsx` | `emoji-reaction/emoji-reaction.component.ts` | `PlBlkEmojiReaction`, `PlBlkEmojiReactionButton`, `PlBlkEmojiReactionGroup` | I2 | CE-I18N-017 |
| `emoji-reaction/emoji-reaction-picker.tsx` | `emoji-reaction/emoji-reaction-picker.component.ts` | `PlBlkEmojiReactionPicker` | I2 | CE-I18N-017 |
| `emoji-reaction/animated-counter.tsx`, `index.ts` | `emoji-reaction/animated-counter.component.ts` | `PlBlkAnimatedCounter` (250 ms, `slide-*`-Animationen) | I2 | CE-I18N-017, -023 |
| `empty-state/empty-state.tsx`, `compact-empty-state.tsx`, `detailed-empty-state.tsx`, `action-button.tsx`, `types.ts`, `index.ts` | `empty-state/*` | `PlBlkEmptyState` (`type` detailed\|simple), `PlBlkEmptyStateCompact`, `PlBlkEmptyStateDetailed`, `PlBlkEmptyStateActionButton` (Varianten-Mapping auf Propel) | I1 | CE-UIX-002, CE-LV-042, CE-I18N-018 |
| `empty-state/assets/asset-registry.tsx`, `asset-types.ts`, `helper.tsx` | `empty-state/assets/{asset-registry,asset-types,helper}.ts` | Registries `HORIZONTAL_STACK_ASSETS` (32), `VERTICAL_STACK_ASSETS` (25), `ILLUSTRATION_ASSETS` (2), `ILLUSTRATION_COLOR_TOKEN_MAP`; lazy `import()` | I1 | CE-I18N-018 |
| `empty-state/assets/{horizontal-stack,vertical-stack,illustration}/*.tsx` (59) | `empty-state/assets/**/*.ts` (generiert, §3.8.3) | `PlIllustrationDef`-Konstanten, gerendert über `svg[plIllustration]` | I1 | CE-I18N-018 |
| `icons/**` (46 Dateien) | `icons/**` | siehe §4.8 | I0/I2 | CE-I18N-014 |
| `layout/header/header.tsx`, `helper.tsx` | `layout/header/{header.component,helper}.ts` | `PlBlkHeader` (`variant` primary\|secondary\|ternary, `setHeight`, `showOnMobile`), `PlBlkHeaderLeftItem`, `PlBlkHeaderRightItem`; `EHeaderVariant` | I0 | CE-UIX-001 |
| `layout/row/row.tsx`, `helper.tsx` | `layout/row/{row.component,helper}.ts` | `PlBlkRow` (`variant` regular\|hugging); `ERowVariant` | I0 | – |
| `layout/content-wrapper/content-wrapper.tsx` | `layout/content-wrapper/content-wrapper.component.ts` | `PlBlkContentWrapper` | I0 | – |
| `layout/control-link/control-link.tsx`, `layout/index.ts` | `layout/control-link/control-link.directive.ts` | `PlBlkControlLink` (`a[plBlkControlLink]`; Cmd/Ctrl-Klick → neuer Tab, sonst `onClick`, `draggable` false) | I0 | – |
| `pill-button/pill-button.tsx`, `helper.tsx`, `index.ts` | `pill-button/{pill-button.component,helper}.ts` | `PlBlkPillButton` (`button[plBlkPillButton]`), `PlBlkPillButtonContent`; `getPillButtonClassName`, `getPillButtonSizeClassName`, `getPillButtonIconClassName`, `getPillButtonIconSize`, `getPillIconPadding` | I1 | – |
| `portal/modal-portal.tsx`, `portal-wrapper.tsx`, `constants.ts`, `types.ts`, `index.ts` | `portal/*` | `PlBlkModalPortal`, `PlBlkPortalWrapper`; `PORTAL_WIDTH_CLASSES`, `PORTAL_POSITION_CLASSES`, `DEFAULT_PORTAL_ID`, `MODAL_Z_INDEX` (tote `shadow-lg`, `bg-white` bleiben) | I0 | CE-UIX-003 |
| `property-select/cycle-select.tsx` | `property-select/cycle-select.component.ts` | `PlBlkCycleSelect` | I2 | CE-WI, CE-CYC |
| `property-select/date-select.tsx`, `date-select-shell.tsx`, `date-select.utils.ts` | `property-select/{date-select,date-select-shell}.component.ts`, `date-select.utils.ts` | `PlBlkDateSelect`, `PlBlkDateSelectShell` (Popover + `PlCalendar`, Format `MMM dd, yyyy`) | I2 | CE-WI |
| `property-select/date-range-select.tsx` | `property-select/date-range-select.component.ts` | `PlBlkDateRangeSelect` (`MERGE_TOKENS`) | I2 | CE-CYC |
| `property-select/estimate-select.tsx` | `property-select/estimate-select.component.ts` | `PlBlkEstimateSelect` | I2 | CE-WI |
| `property-select/intake-state-select.tsx` | `property-select/intake-state-select.component.ts` | `PlBlkIntakeStateSelect` | I3 | CE-INT |
| `property-select/label-select/label-select.tsx`, `create-label-empty-state.tsx` | `property-select/label-select/*` | `PlBlkLabelSelect`, `PlBlkCreateLabelEmptyState` | I2 | CE-WI |
| `property-select/member-select.tsx` | `property-select/member-select.component.ts` | `PlBlkMemberSelect` (`MAX_TRIGGER_AVATARS` 3, Badge „Suspended“) | I1 | CE-WS, CE-WI |
| `property-select/module-select.tsx` | `property-select/module-select.component.ts` | `PlBlkModuleSelect` | I2 | CE-MOD |
| `property-select/priority-select.tsx` | `property-select/priority-select.component.ts` | `PlBlkPrioritySelect` | I2 | CE-WI |
| `property-select/project-select.tsx`, `shared/project-identifier-element.tsx` | `property-select/project-select.component.ts`, `shared/project-identifier-element.component.ts` | `PlBlkProjectSelect`, `PlBlkProjectIdentifierElement` | I2 | CE-PRJ |
| `property-select/state-select.tsx`, `index.ts` | `property-select/state-select.component.ts` | `PlBlkStateSelect` (`allowedStateIds` – C1-Andockstelle, §6.1) | I2 | CE-WI |
| `select/select.tsx`, `root.tsx` | `select/{select,select-root}.component.ts` | `PlBlkSelect` (Root, Lazy-Mount), Namespaces `Select.Trigger`/`Select.Value` → `PlBlkSelectTrigger`/`PlBlkSelectValue` | I0 | CE-UIX-004 |
| `select/trigger.tsx`, `trigger-chrome.tsx` | `select/{select-trigger,select-trigger-chrome}.component.ts` | `PlBlkSelectTrigger`, `PlBlkSelectTriggerChrome` | I0 | CE-UIX-004 |
| `select/value.tsx` | `select/select-value.component.ts` | `PlBlkSelectValue` | I0 | – |
| `select/select-content.tsx` | `select/select-content.component.ts` | `PlBlkSelectContent` | I0 | – |
| `select/select-list-body.tsx`, `virtual-list-body.tsx` | `select/{select-list-body,virtual-list-body}.component.ts` | `PlBlkSelectListBody`, `PlBlkVirtualListBody` (`overscan` 8) | I0 | – |
| `select/menu-parts.tsx` | `select/menu-parts.component.ts` | `PlBlkMenuPanel` (E-24), `PlBlkMenuRow` | I0 | – |
| `select/menu-search-input.tsx` | `select/menu-search-input.component.ts` | `PlBlkMenuSearchInput` | I0 | – |
| `select/dropdown-placement.tsx` | `select/dropdown-placement.ts` | `PL_BLK_SELECT_DROPDOWN_PLACEMENT` (Token), `injectSelectDropdownPlacement()` | I0 | – |
| `select/skeleton.tsx` | `select/select-skeleton.component.ts` | `PlBlkSelectSkeleton` | I0 | – |
| `select/nested-submenu/nested-submenu-root.tsx`, `nested-submenu-group.tsx` | `select/nested-submenu/*.component.ts` | `PlBlkNestedSubmenu`, `PlBlkNestedSubmenuGroup` | I1 | – |
| `select/nested-submenu/nested-submenu.ts`, `.constants.ts`, `.dismissal.ts`, `.context.ts` | `select/nested-submenu/*.ts` | `submenuLevel()`, `isDismissalFromPreventedRegion`, `preservePanelPointerDefaults`, Delays 100/600 | I1 | – |
| `select/context.ts`, `engine-context.ts` | `select/{select-context,select-engine}.ts` | `PlBlkSelectContext` (Token), `PlBlkSelectEngine` (Service je Instanz) | I0 | – |
| `select/use-infinite-options.ts`, `use-skip-disabled-rows.ts` | `select/{infinite-options,skip-disabled-rows}.ts` | `infiniteOptions()` (Signals, Generation, Debounce 300 ms), `skipDisabledRows()` | I0 | – |
| `select/utils.ts`, `select.constants.ts`, `types.ts`, `index.ts` | `select/{utils,select.constants,types}.ts`, `public-api.ts` | `getSelectClassName`, `splitSelectVariant`, `triggerVariants`, `pinSelected`, `MENU_LIST_CLASSNAME`, `MENU_ROW_HEIGHT`, `SELECT_OPTION_ROW_HEIGHT`, `SELECT_SEARCH_DEBOUNCE_MS` | I0 | – |
| `skeleton/root.tsx`, `loader.tsx`, `index.ts` | `skeleton/{skeleton,loader}.component.ts` | `PlBlkSkeleton` (+ `PlBlkSkeletonItem`), `PlBlkSkeletonRoot`, `PlBlkLoader` (+ `PlBlkLoaderItem`) | I0 | CE-UIX-002 |
| `spinner/circular-spinner.tsx`, `circular-bar-spinner.tsx`, `index.ts` | `spinner/*.component.ts` | `PlBlkSpinner`, `PlBlkCircularBarSpinner` | I0 | CE-I18N-026 |
| `toast/plane-toast-provider.tsx`, `toast-manager.ts`, `index.ts` | `toast/*` | `PlBlkPlaneToastProvider`, `setToast`, `updateToast`, `setPromiseToast`, `dismissToast`, `toastManager` | I0 | CE-I18N-021 |
| `types/index.ts`, `logo.ts`, `icon.ts` | `types/*.ts` | `IconElement` → `PlIconSource`, `TLogoProps` (unverändert) | I0 | – |
| `utils/dot-separator.tsx`, `placement.ts`, `index.ts` | `utils/{dot-separator.component,placement}.ts` | `PlBlkDotSeparator`, `convertPlacementToSideAndAlign` | I0 | – |
| `virtual-list/virtual-list.tsx`, `infinite-virtual-list.tsx`, `list-skeleton.tsx`, `index.ts` | `virtual-list/*` | `PlBlkVirtualList`, `PlBlkInfiniteVirtualList`, `PlBlkVirtualListSkeleton` (`@tanstack/virtual-core`) | I1 | – |
| Tests: `__tests__/dom-scrolling.test.tsx`, `breadcrumb/{breadcrumbs,breadcrumb-navigation-select}.test.tsx`, `common/{common-a11y,sortable/sortable,color-swatch-picker/color-swatch-picker}.test.tsx`, `common/color-swatch-picker/hex.test.ts`, `context-menu/context-menu.test.tsx`, `context-menu/helpers.test.ts`, `dialog/confirm-dialog.test.tsx`, `emoji-icon-picker/{search-a11y,emoji-picker}.test.tsx`, `emoji-reaction/emoji-reaction-picker.test.tsx`, `property-select/{tab-index,member-select,outside-click,date-select}.test.tsx`, `select/{select,menu-search-input}.test.tsx`, `select/nested-submenu/nested-submenu.dismissal.test.tsx`, `toast/toast-manager.test.ts` (21) | gleiche Pfade, `*.spec.ts` | Portierte Verhaltensspezifikation (`@testing-library/angular`, Vitest) | mit Modul | – |

### 4.8 Blocks-Icons (`BLK/icons/**`)

| Original | Ziel (`BLKT/icons/…`) | Art | Angular | Inkr. |
|---|---|---|---|---|
| `state/state-group-icon.tsx`, `state/helper.tsx` | `state/state-group-icon.component.ts`, `helper.ts` | Hand | `PlBlkStateGroupIcon` (`svg`-Attribut-Komponente; `stateGroup`, `color` Default `STATE_GROUP_COLORS`, `percentage`, `size`); `STATE_GROUP_COLORS` | I2 |
| `state/backlog-group-icon.tsx`, `unstarted-group-icon.tsx` (E-16), `started-group-icon.tsx`, `completed-group-icon.tsx`, `cancelled-group-icon.tsx`, `triage-group-icon.tsx` | `state/*.component.ts` | Hand | `PlBlkBacklogGroupIcon`, `PlBlkUnstartedGroupIcon`, `PlBlkStartedGroupIcon`, `PlBlkCompletedGroupIcon`, `PlBlkCancelledGroupIcon`, `PlBlkTriageGroupIcon` | I2 |
| `state/dashed-circle.tsx`, `progress-circle.tsx` | `state/{dashed-circle,progress-circle}.component.ts` | Hand | interne SVG-Teile (`g[plBlkDashedCircle]`, `g[plBlkProgressCircle]`) | I2 |
| `state/intake-state-group-icon.tsx` | `state/intake-state-group-icon.component.ts` | Hand | `PlBlkIntakeStateGroupIcon`, `INTAKE_STATE_GROUP_COLORS` | I3 |
| `cycle/cycle-group-icon.tsx`, `cycle/helper.tsx`, `cycle/circle-dot-full-icon.tsx`, `project/cycle-icon.tsx` | `cycle/*`, `project/cycle-icon.ts` | Hand / gen | `PlBlkCycleGroupIcon`, `CYCLE_GROUP_COLORS`, `CYCLE_GROUP_I18N_LABELS`; `CircleDotFullIcon`, `CycleIcon` (gen) | I2 |
| `module/module-status-icon.tsx`, `module/{backlog,cancelled,completed,in-progress,paused,planned}.tsx` | `module/*` | Hand / gen | `PlBlkModuleStatusIcon` (Fallback planned); 6 Glyphen gen | I3 |
| `priority-icon.tsx` | `priority-icon.component.ts` | Hand | `PlBlkPriorityIcon` (Propel `PriorityUrgent/High/Medium/Low/None`, `text-priority-*`, `size-3.5`) | I2 |
| `blocked-icon.tsx`, `blocker-icon.tsx`, `calendar-after-icon.tsx`, `calendar-before-icon.tsx`, `favorite-folder-icon.tsx`, `layer-stack.tsx`, `monospace-icon.tsx`, `sans-serif-icon.tsx`, `serif-icon.tsx`, `properties/label-icon.tsx` | gleiche Namen `.ts` | gen | `BlockedIcon`, `BlockerIcon`, `CalendarAfterIcon`, `CalendarBeforeIcon`, `FavoriteFolderIcon`, `LayerStackIcon`, `MonospaceIcon`, `SansSerifIcon`, `SerifIcon`, `LabelPropertyIcon` | I0 |
| `brand/plane-logo.tsx`, `brand/plane-lockup.tsx`, `brand/accenture-logo.tsx`, `brand/dolby-logo.tsx`, `brand/sony-logo.tsx`, `brand/zerodha-logo.tsx`, `sub-brand/pi-chat.tsx` | `brand/*.ts`, `sub-brand/pi-chat.ts` | gen | `PlaneLogo`, `PlaneLockup`, `AccentureLogo`, `DolbyLogo`, `SonyLogo`, `ZerodhaLogo`, `PiChatLogo` | I0 |
| `icons/index.ts`, `icons/type.ts` | `icons/public-api.ts`, `type.ts` | – | Barrel `@plane/blocks/icons`, `SvgIconProps` | I0 |

### 4.9 Web-eigene Icons (`WEB/components/icons/**`)

| Original | Ziel (`FE/libs/web/core/icons/…`) | Angular | Inkr. | CE |
|---|---|---|---|---|
| `attachment/attachment-icon.tsx` (`getFileIcon`) | `attachment/attachment-icon.ts` | `getFileIcon(fileType, size = 28)` mit identischer Zuordnung (E-18) | I2 | CE-I18N-015 |
| `attachment/{audio,css,csv,default,doc,figma,html,img,jpg,js,pdf,png,rar,sheet,svg,txt,video,zip}-file-icon.tsx` (18) | `attachment/file-icons.component.ts` | `PlFileIcon` (`img` mit `src` aus `assets/attachment/*-icon.png`, `width`/`height`/`alt` wie Original) | I2 | CE-I18N-015 |
| `attachment/document-icon.tsx`, `setting-icon.tsx`, `tune-icon.tsx` | `attachment/{document,setting,tune}-icon.ts` | gen (`PlIconDef`; feste Farben bleiben) | I2 | – |
| `locked-component.tsx` | `locked-component.component.ts` | `PlLockedComponent` (Pill „Locked“ + optional Tooltip `stacked`) | I4 | CE-I18N-015 |
| `types.d.ts` | `types.ts` | – | – | – |

### 4.10 lucide und Material Symbols

| Quelle | Ziel | Umfang | Inkr. |
|---|---|---|---|
| `lucide-react` 1.34.0 (Propel-intern) | `FE/libs/shared/icons-lucide/src/v134/` aus npm `lucide@1.34.0` | `LoaderCircle`, `ChevronDown`, `ChevronRight`, `ChevronLeft`, `ChevronUp`, `ChevronsUpDown`, `Check`, `Minus`, `Search`, `X`, `Ellipsis`, `MoreHorizontal`, `ArrowLeft`, `ArrowRight`, `ArrowUpRight`, `User`, `Building2` (17) | I0 |
| `lucide-react` 0.469.0 (Apps, Blocks) | `FE/libs/shared/icons-lucide/src/v0469/` aus npm `lucide@0.469.0` | alle 181 im Code genutzten Namen + 157 Einträge `LUCIDE_ICONS_LIST` (Vereinigung; Generator liest die Namen per `grep` aus dem Original) | I0 |
| Material Symbols Rounded (Font) | `@fontsource/material-symbols-rounded` 5.2.30 | 200 Ligatur-Namen `MATERIAL_ICONS_LIST` + alle im Code genutzten | I1 |

### 4.11 Schriften, Bilder, Illustrationen, statische Dateien (`apps/*/public`, `apps/*/app/assets`)

Kopie byte-identisch; Ziel-Unterordner gleichnamig unter `FE/apps/<app>/src/assets/` bzw. `FE/apps/<app>/public/` (Angular-`public`-Ordner wird unverändert an die Basis der App ausgeliefert).

| Original | Dateien | Ziel | Hinweis | Inkr. | CE |
|---|---|---|---|---|---|
| `apps/web/public/favicon/*` (2), `icons/*` (3), `manifest.json`, `site.webmanifest.json`, `favicon/site.webmanifest` | 7 | `FE/apps/web/public/` | Manifeste: `start_url` je Base-Pfad unverändert `/`; Name „Plane“ bleibt (Produktname, ADR-005) | I0 | – |
| `apps/web/public/sw.js`, `sw.js.map`, `workbox-9f2f79cf.js`, `workbox-9f2f79cf.js.map` | 4 | – | **entfallen**: im Original nirgends registriert (kein `serviceWorker.register`), Build-Reste | – | – |
| `apps/admin/public/favicon/*` (2), `site.webmanifest.json` | 3 | `FE/apps/admin/public/` | – | I0 | – |
| `apps/admin/public/.well-known/appspecific/com.chrome.devtools.json` | 1 | – | entfällt (Dev-Hilfe) | – | – |
| `apps/space/public/favicon/*` (2), `site.webmanifest.json` | 3 | `FE/apps/space/public/` | – | I0 | – |
| `apps/web/app/assets/favicon/*` | 4 | `FE/apps/web/src/assets/favicon/` | `<link rel="icon">` wie `WEB/app/root.tsx` | I0 | – |
| `apps/web/app/assets/icons/*` | 2 | `…/web/src/assets/icons/` | Apple-Touch-Icon | I0 | – |
| `apps/web/app/assets/images/logo-spinner-{light,dark}.gif` | 2 | `…/web/src/assets/images/` | Web-`LogoSpinner` (`resolvedTheme === "dark"`-Muster) | I0 | CE-I18N-026 |
| `apps/web/app/assets/auth/*` | 8 | `…/web/src/assets/auth/` | `background-pattern{,-dark}.svg`, `gradient-*.webp` auch im Keycloak-Theme (`deploy/keycloak/themes/plane/login/resources/img/`); `*-not-authorized.svg`, `access-denied.svg`, `unauthorized.svg` für Zugriffsseiten | I0 | CE-AUTH-001, CE-UIX-010 |
| `apps/web/app/assets/logos/*` (gitea, github ×4, gitlab, google) | 7 | – | **entfallen** (OAuth-Login und GitHub/GitLab-Integration entfallen, ADR-007/-008) | – | – |
| `apps/web/app/assets/services/*` (csv, excel, json, github, jira, slack) | 6 | `…/web/src/assets/services/` nur `csv.svg`, `excel.svg`, `json.svg` | Export-Formate (CE-EXP); `github.png`, `jira.svg`, `slack.png` entfallen (Importer/Integrationen nicht CE, F7–F11 nicht gewählt) | I6 | CE-EXP |
| `apps/web/app/assets/attachment/*-icon.png` | 18 | `…/web/src/assets/attachment/` | `getFileIcon` | I2 | CE-I18N-015 |
| `apps/web/app/assets/cover-images/image_*.jpg` | 29 | `…/web/src/assets/cover-images/` | Image-Picker (Projekt-/Profil-Cover) | I1 | CE-UIX-009 |
| `apps/web/app/assets/empty-state/` (26 Dateien direkt + 24 Unterordner: `active-cycle` 12, `all-issues` 12, `analytics` 10, `archived` 6, `cycle` 12, `cycle-issues` 20, `dashboard` 20, `disabled-feature` 10, `draft` 2, `empty-filters` 10, `epics` 4, `estimates` 2, `intake` 10, `module` 2, `module-issues` 20, `onboarding` 34, `profile` 14, `project` 5, `project-settings` 18, `search` 20, `stickies` 4, `wiki` 16, `workspace-draft` 2, `workspace-settings` 20) | 311 | `…/web/src/assets/empty-state/` (vollständig, inkl. `epics`, `wiki`, `dashboard` für spätere Pakete) | Light/Dark-Paare per `resolvedTheme` (§3.8.3) | I1 | CE-I18N-018, CE-LV-042 |
| `apps/web/app/assets/onboarding/*.webp` | 6 | `…/web/src/assets/onboarding/` | – | I1 | CE-WS |
| `apps/web/app/assets/workspace/*.png` | 2 | `…/web/src/assets/workspace/` | `workspace-creation-disabled.png`, `workspace-not-available.png` | I0 | CE-WS-001 |
| `apps/web/app/assets/workspace-active-cycles/cta-*.webp` | 6 | – | entfällt mit Upsell U12 (B4 bringt die echte Seite ohne CTA-Bilder) | – | – |
| `apps/web/app/assets/instance/maintenance-mode-{light,dark}.svg`, `instance-setup-done.webp`, `instance-not-ready.webp`, `plane-takeoff.png` | 5 | `…/web/src/assets/instance/` bzw. Wurzel | Instanzzustände | I0 | CE-INST-006 |
| `apps/web/app/assets/users/*` | 3 | `…/web/src/assets/users/` | Default-Avatare/Profil-Cover | I1 | CE-PROF |
| `apps/web/app/assets/scribble/*`, `emoji/project-emoji.svg`, `user.png`, `mac-command.svg`, `404.svg`, `og-image.png` | 7 | `…/web/src/assets/` | `og-image.png` auch als OG-Fallback im Gateway | I0 | CE-UIX-010 |
| `apps/web/app/assets/fonts/inter/*.ttf` | 18 | `src/documents/Plane.Documents.Pdf/Fonts/` | nur für PDF (→ `07`, ADR-029) | I4 | CE-PAGE-011 |
| `apps/admin/app/assets/favicon/*` | 4 | `FE/apps/admin/src/assets/favicon/` | – | I0 | – |
| `apps/admin/app/assets/images/*` (404.svg, logo-spinner ×2, plane-takeoff.png) | 4 | `…/admin/src/assets/images/` | Admin-`LogoSpinner` mit **inverser** Benennung (`A13a` §3.5) | I0 | CE-INST |
| `apps/admin/app/assets/instance/instance-failure{,-dark}.svg` | 2 | `…/admin/src/assets/instance/` | – | I0 | CE-INST |
| `apps/admin/app/assets/logos/*` (gitea, github ×2, gitlab, google, takeoff-icon ×2) | 7 | nur `takeoff-icon-{light,dark}.svg` | Provider-Logos entfallen (CE-INST-020…-024) | I6 | CE-INST |
| `apps/space/app/assets/favicon/*` | 5 | `FE/apps/space/src/assets/favicon/` | – | I0 | – |
| `apps/space/app/assets/{404,project-not-published,something-went-wrong,user-logged-in}.svg` | 4 | `…/space/src/assets/` | – | I6 | CE-SPACE-014, -031 |
| `apps/space/app/assets/robots.txt` | 1 | `FE/apps/space/public/robots.txt` | – | I6 | – |
| `apps/space/app/assets/auth/background-pattern{,-dark}.svg` | 2 | `…/space/src/assets/auth/` + Keycloak-Theme | – | I0 | CE-AUTH-001 |
| `apps/space/app/assets/instance/*` (failure ×2, intake-sent ×2, instance-not-ready, takeoff) | 6 | `…/space/src/assets/instance/` | – | I6 | CE-SPACE-015 |
| `apps/space/app/assets/images/logo-spinner-{light,dark}.gif` | 2 | `…/space/src/assets/images/` | – | I0 | – |
| `apps/space/app/assets/logos/*` (gitea, github ×4, gitlab, google) | 7 | – | entfallen (CE-SPACE-011) | – | – |
| `PROPEL/components/logo-spinner/logo-spinner-{light,dark}.gif`, `…-still.png` | 4 | `PRP/components/logo-spinner/assets/` (über `angular.json`-Assets je App) | Propel-`LogoSpinner` | I0 | CE-I18N-026 |
| `BLK/empty-state/assets/**` (59 SVG-Komponenten) | 59 | §4.7 | – | I1 | CE-I18N-018 |

### 4.12 Upsell-Elemente (ADR-001) → Ersatz

Vollständig nach `F20` §5 (U1–U22).

| # | Original | Ersatz in `funk.` | Abweichung |
|---|---|---|---|
| U1 | `WEB/components/workspace/upgrade-badge.tsx` (`UpgradeBadge`) | entfällt (Lint `pl/no-plan-gating`) | – |
| U2 | `WEB/components/common/pro-icon.tsx` (`ProIcon`) | entfällt | – |
| U3 | `WEB/components/workspace/edition-badge.tsx` (Button „Community“ → Upgrade-Modal) in der Sidebar-Fußzeile (`sidebar-wrapper.tsx` Z. 85) | Fußzeile `flex h-12 items-center justify-between border-t border-subtle bg-surface-1 p-3` bleibt; statt Button ein **nicht interaktives** `PlBadge size="md" variant="neutral"` mit Label `v{app_version}` (Runtime-Config), umhüllt von `PlTooltip` „Version: v{app_version}“ (Tooltip deaktiviert auf Mobil wie Original) | `UI-DEV-001` (Pixel + DOM in `sidebar-footer`) |
| U4–U10 | `WEB/components/license/modal/**` (`PaidPlanUpgradeModal`, `FreePlanCard`, `PlanUpgradeCard`, `TalkToSalesCard`, `BasePaidPlanCard`, `PlanCheckoutButton`, `DiscountInfo`) | entfallen ersatzlos | – |
| U11 | Billing-Seite `:workspaceSlug/settings/billing` + `WEB/components/workspace/billing/**`, Settings-Eintrag `billing-and-plans` | Route nicht registriert; Settings-Navigation ohne Eintrag (Reihenfolge der übrigen Einträge unverändert); Direktaufruf → 404-Seite wie jede unbekannte Route | `UI-DEV-002` (Settings-Sidebar) |
| U12 | `WEB/components/active-cycles/workspace-active-cycles-upgrade.tsx` (Seite `:workspaceSlug/active-cycles`) | in der CE Route nicht registriert; echte Seite mit Paket **B4** (W5, §6) | `UI-DEV-003` |
| U13 | `UpgradeBadge` im Header `active-cycles/header.tsx` | entfällt (mit B4 ohne Badge) | – |
| U14 | `UpgradeBadge` in `extended-sidebar-item.tsx` (`active_cycles`) | entfällt | – |
| U15 | `UpgradeBadge` in `workspace-menu-item.tsx` (nie gerendert) | entfällt | – |
| U16 | `UpgradeBadge` + Tooltip „Pro feature“ in `project/settings/features-list.tsx` (`isPro`) | entfällt; Bezahl-Projekt-Features erscheinen später als normale Toggles über `SETTINGS_PAGES`/Feature-Liste (§6.1) | – |
| U17 | `UpgradeBadge` + „coming soon“ bei Estimate-System `time` (`estimates/create/stage-one.tsx`) | CE: System `time` bleibt ausgeblendet wie im Original (Filter), **ohne** Badge; mit **A11** sichtbar | `UI-DEV-004` |
| U18 | Bulk-Ops-Banner „Upgrade to One“ (`issues/bulk-operations/root.tsx`) | CE: Banner entfällt, Auswahl bleibt deaktiviert wie Original; echte Leiste mit **A8** | `UI-DEV-005` |
| U19 | `DISPLAY_WORKFLOW_PRO_CTA` (`packages/constants/src/state.ts`) | Konstante entfernt | – |
| U20 | `MARKETING_PRICING_PAGE_LINK`, `MARKETING_CONTACT_US_PAGE_LINK`, `MARKETING_PLANE_ONE_PAGE_LINK` | entfernt | – |
| U21 | `packages/constants/src/{subscription,payment}.ts`, `packages/utils/src/subscription.ts`, `packages/types/src/payment.ts` | nicht kopiert (`01` §6.2) | – |
| U22 | Feature-Flag-Filter-Kommentare in `customize-navigation-dialog.tsx` | Filter auf fachliche Workspace-Feature-Toggles + `SIDEBAR_ITEMS`-Registry (§6.1) | – |
| – | Plan-Tokens `--txt-plans-*`, `--bg-plans-*` (`A13a` §1.4) | **bleiben** im vendored CSS (Kosten null, CSS-Diff-Gleichheit) | – |
| – | i18n-Upsell-Schlüssel (`common.upgrade`, `sidebar.upgrade*`, `…empty_state.upgrade.*` u. a., `F20` §5) | bleiben in den Locale-Dateien (1:1-Kopie), werden aber nicht referenziert | – |

### 4.13 Base-UI-Module (38) → Angular-Basis

| Base-UI-Modul (`@base-ui/react/…`) | Angular-Basis in `PRP/headless/` bzw. Komponente | Aufwand |
|---|---|---|
| `accordion` | Angular-Aria-Accordion-Muster + Presence + Panel-Höhe | M |
| `alert-dialog` | `PlDialogCore` (modal, kein Outside-Close) | M |
| `autocomplete` | `PlComboboxCore` (Autocomplete-Modus) | XL |
| `avatar` | `PlAvatarCore` (Bild-Ladestatus, `delay`) | S |
| `button` | `PlButtonCore` (`focusableWhenDisabled`, `aria-disabled`, `data-disabled`) | S |
| `checkbox`, `checkbox-group` | `PlCheckboxCore`, `PlCheckboxGroupCore` | S |
| `collapsible` | `PlCollapsibleCore` (Panel-Höhe, `hiddenUntilFound`) | M |
| `combobox` | `PlComboboxCore` (`ActiveDescendantKeyManager`, Chips, Gruppen, Status) | XL |
| `context-menu` | `PlMenuCore` + virtueller Anker | L |
| `csp-provider`, `direction-provider` | Angular `CSP_NONCE`, CDK `Directionality` | S |
| `dialog` | `PlDialogCore` (FocusTrap, Scroll-Lock, Dismiss) | M |
| `drawer` | `PlDialogCore` + Swipe + Inline-Portal | L |
| `field`, `fieldset`, `form` | `PlFieldCore` (Kontext-Signal), Signal Forms | M |
| `input` | `PlInputCore` (CVA) | S |
| `menu` | `PlMenuCore` (Angular-Aria-Menu-Modell, Submenüs, Checkbox/Radio-Items, Hover-Intent) | L |
| `navigation-menu` | `PlNavigationMenuCore` | L |
| `number-field` | `PlNumberFieldCore` | M |
| `otp-field` | `PlOtpFieldCore` | M |
| `popover` | `PlPopoverCore` | M |
| `preview-card` | `PlPreviewCardCore` | M |
| `progress` | `PlProgressCore` | S |
| `radio`, `radio-group` | `PlRadioGroupCore` (Roving) | S |
| `scroll-area` | `PlScrollAreaCore` | M |
| `select` | `PlSelectCore` (`alignItemWithTrigger`) | L |
| `separator` | `PlSeparator` (Direktive) | S |
| `slider` | `PlSliderCore` | M |
| `switch` | `PlSwitchCore` | S |
| `tabs` | Angular-Aria-Tabs + Indikator-Messung | M |
| `toast` | `PlToastManager` + Viewport | L |
| `toggle`, `toggle-group` | `PlToggleCore`, `PlToggleGroupCore` | S |
| `toolbar` | Angular-Aria-Toolbar | S |
| `tooltip` | `PlTooltipCore` + `PlDelayGroup` | M |
| Hilfsmodule `merge-props`, `use-render`, `internals/composite` | Host-Bindings/Attribut-Selektoren, `PlComposite` | – |

### 4.14 Screenshot-Katalog: Einträge (vollständig für alle CE-Routen)

Routen-Quelle: `WEB/app/routes/core.ts` (67 `route()`-Einträge + Index), `ADM/app/routes.ts`, `SPC/app/routes.ts`. Parameter in `{…}` sind semantische Seed-Schlüssel (§3.14.2). Jeder Zustand wird in den Themes/Viewports nach §3.14.4 aufgenommen; `base` immer in vier Viewports. Tags: `tf` = `theme-full`, `rv` = `role-variant` (zusätzlich `member`/`guest`), `wide` = zusätzlich `wide-1920`. Redirect-Routen (`:ws/projects/:projectId/settings/*`, `:ws/analytics`, `:ws/settings/api-tokens`, `:ws/projects/:projectId/inbox`, `accounts/sign-up`, `sign-in`, `signin`, `login`, `register`, `profile/*`, `:ws/settings/account/*`) werden **nicht** fotografiert, sondern als Routing-Tests (Ziel-URL) geprüft (→ `08`).

**Web**

| ID | Route | Zustände | Tags | Inkr. | CE |
|---|---|---|---|---|---|
| W-001 | `/{ws:acme}` (Shell) | `base`, `sidebar-collapsed`, `mobile-sidebar-open`, `user-menu-open`, `workspace-switcher-open`, `customize-navigation-dialog`, `favorites-expanded`, `projects-section-collapsed`, `sidebar-footer` (U3) | tf | I0 | CE-WS, CE-UIX-001 |
| W-002 | `/create-workspace` | `base`, `validation-errors`, `slug-taken`, `creation-disabled` | – | I0 | CE-WS-001 |
| W-003 | `/{ws:acme}/projects` | `base`, `list-view`, `filters-open`, `display-open`, `empty` (Workspace ohne Projekte), `create-project-modal`, `create-project-modal-errors`, `join-project` (Guest-Sicht) | tf, rv | I0 (Kern) / I1 | CE-PRJ-004, CE-PRJ |
| W-004 | Zugriffs- und Fehlerseiten: Workspace nicht autorisiert, Projekt nicht autorisiert, `access-denied`, `unauthorized`, `/{unbekannt}` (404, `WEB/app/not-found.tsx`), Fehlerseite (`WEB/app/error/prod.tsx`), Wartungsansicht (`components/instance/maintenance-view.tsx`), Instanz nicht bereit | je ein Zustand `base` | – | I0/I1 | CE-UIX-010, CE-INST-006 |
| W-005 | `/onboarding` | `profile-step`, `role-step`, `workspace-create-step`, `workspace-join-step`, `invite-members-step`, `switch-account-modal` | – | I1 | CE-AUTH (angepasst), CE-WS |
| W-006 | `/invitations` | `base` (2 Einladungen), `empty` | – | I1 | CE-WS |
| W-007 | `/workspace-invitations?…` | `valid`, `expired`, `already-member` | – | I1 | CE-WS |
| W-008 | `/{ws:acme}/settings` | `base`, `logo-picker-open`, `delete-workspace-dialog` | tf | I1 | CE-WS |
| W-009 | `/{ws:acme}/settings/members` | `base`, `invite-dialog`, `role-menu-open`, `remove-confirm`, `search-empty` | rv | I1 | CE-WS |
| W-010 | `/{ws:acme}/settings/exports` | `base` (1 Export), `empty`, `export-running` | – | I6 | CE-EXP |
| W-011 | `/{ws:acme}/settings/webhooks` | `base`, `empty`, `create-dialog`, `secret-shown` | – | I6 | CE-WH |
| W-012 | `/{ws:acme}/settings/webhooks/{webhook:1}` | `base`, `delete-confirm` | – | I6 | CE-WH |
| W-013 | `/{ws:acme}/settings/projects` | `base`, `empty` | – | I1 | CE-PRJ |
| W-014 | `/{ws:acme}/settings/projects/{project:WEB}` | `base`, `cover-picker-open`, `identifier-error`, `archive-confirm`, `delete-confirm` | – | I1 | CE-PRJ |
| W-015 | `…/settings/projects/{project:WEB}/members` | `base`, `add-member-dialog`, `role-menu-open` | rv | I1 | CE-PRJ |
| W-016 | `…/features/cycles`, `…/features/modules`, `…/features/views`, `…/features/pages`, `…/features/intake` | je `on`, `off` | – | I1 | CE-PRJ |
| W-017 | `…/settings/projects/{project:WEB}/states` | `base`, `create-inline`, `edit-inline`, `delete-confirm`, `drag-reorder` | – | I1 | CE-PRJ |
| W-018 | `…/settings/projects/{project:WEB}/labels` | `base`, `create-inline`, `nested-labels`, `color-picker-open`, `empty` (`{project:EMPTY}`) | – | I1 | CE-PRJ |
| W-019 | `…/settings/projects/{project:WEB}/estimates` | `base`, `empty`, `create-stage-one` (U17), `create-stage-two`, `disable-confirm` | – | I1 | CE-PRJ |
| W-020 | `…/settings/projects/{project:WEB}/automations` | `base`, `auto-archive-menu-open`, `auto-close-state-select-open` | – | I3 | CE-PRJ |
| W-021 | `/settings/profile/general` | `base`, `avatar-upload-dialog`, `email-change-dialog`, `deactivate-confirm` | – | I1 | CE-PROF-002…-005 |
| W-022 | `/settings/profile/preferences` | `base`, `theme-select-open`, `custom-theme-form`, `language-select-open`, `timezone-select-open` | tf | I1 | CE-I18N-001, -005…-008, CE-PROF-006 |
| W-023 | `/settings/profile/notifications` | `base` | – | I5 | CE-NOTIF |
| W-024 | `/settings/profile/api-tokens` | `base`, `empty`, `create-dialog`, `token-shown` | – | I6 | CE-API |
| W-025 | `/settings/profile/security` | – (Tab entfällt: Passwortänderung liegt in Keycloak, ADR-008) | – | – | CE-AUTH (entfällt) |
| W-026 | `/{ws:acme}/projects/{project:WEB}/issues` – Layout **List** | `base` (Gruppe State), `group-priority`, `sub-group-none`, `display-props-popover`, `filters-dropdown`, `rich-filter-bar`, `quick-add`, `context-menu-open`, `peek-side`, `peek-modal`, `peek-full`, `empty-filters`, `empty` (`{project:EMPTY}`), `loading-skeleton` | tf, wide | I2 | CE-LV, CE-WI |
| W-027 | dto. Layout **Kanban** | `base`, `sub-grouped`, `collapsed-column`, `drag-over`, `quick-add`, `card-properties-full`, `empty-column-hidden` | tf, wide | I2 | CE-LV |
| W-028 | dto. Layout **Spreadsheet** | `base`, `column-menu-open`, `cell-select-open` (State/Priority/Assignee/Labels/Dates), `row-selected`, `sticky-scroll` | tf, wide | I2 | CE-LV |
| W-029 | dto. Layout **Calendar** | `month`, `week`, `quick-add`, `overflow-more` | wide | I2 | CE-LV |
| W-030 | dto. Layout **Gantt** | `base`, `bar-hover`, `sidebar-collapsed`, `drag-resize` | wide | I2 | CE-LV |
| W-031 | `…/issues/{issue:WEB-1}` (Detail) | `base`, `sub-items-expanded`, `relations`, `activity-all`, `comments-only`, `comment-edit`, `attachments`, `links`, `description-edit`, `property-menus` (je Property), `delete-confirm` | tf | I2 | CE-WI |
| W-032 | `/{ws:acme}/browse/{issue:WEB-1}` | `base` | – | I2 | CE-WI |
| W-033 | Globale Modals (auf `/{ws:acme}/projects/{project:WEB}/issues`): Work Item anlegen, Work Item anlegen mit Fehlern, Bulk-Delete, Work-Item-Suche, Tastenkürzel-Übersicht, Toasts (success/error/warning/info/loading, mit Aktion „View“) | je `base` | – | I2 | CE-UIX-003, CE-WI-006, CE-I18N-021 |
| W-034 | `/{ws:acme}/drafts` | `base`, `empty` | – | I2 | CE-WI |
| W-035 | `…/projects/{project:WEB}/cycles` | `base` (current + upcoming + completed), `active-cycle-expanded`, `draft-section`, `create-dialog`, `date-range-open`, `empty` (`{project:EMPTY}`), `feature-off` (`{project:OFF}`) | tf | I3 | CE-CYC |
| W-036 | `…/cycles/{cycle:current}` | `list-layout`, `kanban-layout`, `analytics-sidebar`, `transfer-dialog` | – | I3 | CE-CYC |
| W-037 | `…/projects/{project:WEB}/modules` | `grid`, `list`, `gantt`, `create-dialog`, `status-menu-open`, `empty` | – | I3 | CE-MOD |
| W-038 | `…/modules/{module:in-progress}` | `base`, `analytics-sidebar`, `links` | – | I3 | CE-MOD |
| W-039 | `…/projects/{project:WEB}/views` | `base`, `create-dialog`, `empty` | – | I3 | CE-LV |
| W-040 | `…/views/{view:1}` | `base`, `filters-changed` | – | I3 | CE-LV |
| W-041 | `/{ws:acme}/workspace-views` | `base` | – | I3 | CE-LV |
| W-042 | `/{ws:acme}/workspace-views/{global-view:all-issues}` (+ `assigned`, `created`, `subscribed`, Custom) | je `base`, `filters-open` | wide | I3 | CE-LV |
| W-043 | `…/projects/{project:WEB}/intake` | `base` (pending), `item-detail`, `filters-open`, `accept-dialog`, `decline-confirm`, `snooze-open`, `duplicate-select`, `create-dialog`, `empty` | – | I3 | CE-INT |
| W-044 | `…/archives/issues`, `…/archives/issues/{archived-issue:1}`, `…/archives/cycles`, `…/archives/modules`, `/{ws:acme}/projects/archives` | je `base`, `empty`; Detail `restore-confirm` | – | I3 (Projekte I1) | CE-WI, CE-CYC, CE-MOD, CE-PRJ |
| W-045 | `…/projects/{project:WEB}/pages` | `public-tab`, `private-tab`, `archived-tab`, `create-dialog`, `quick-actions-open`, `empty`, `feature-off` | – | I4 | CE-PAGE |
| W-046 | `…/pages/{page:all-nodes}` | `read`, `edit-focused`, `slash-menu`, `bubble-menu`, `block-menu`, `outline-pane`, `info-pane`, `version-history`, `locked`, `archived`, `lock-animation` (Endzustand), `mention-suggestion`, `emoji-suggestion` | tf | I4 | CE-PAGE, CE-RT |
| W-047 | `/{ws:acme}` (Home-Inhalt) | `base` (Widgets), `new-user` (leerer Workspace), `quick-link-dialog`, `widget-manage`, `stickies-widget` | tf | I5 | CE-HOME |
| W-048 | `/{ws:acme}/notifications` | `base`, `unread-only`, `archived`, `snoozed`, `peek-open`, `snooze-menu`, `empty` | – | I5 | CE-NOTIF |
| W-049 | `/{ws:acme}/analytics/overview`, `/{ws:acme}/analytics/work-items` | je `base`, `empty`, `filters-open` | – | I5 | CE-ANA |
| W-050 | `/{ws:acme}/profile/{user:ada}` (Summary), `…/{user:ada}/assigned`, `/created`, `/subscribed`, `/activity` | je `base`, `empty` (`{user:cyd}`) | – | I5 | CE-PROF-008…-011 |
| W-051 | `/{ws:acme}/stickies` | `base`, `empty`, `editing`, `color-palette-open` | – | I5 | CE-HOME |
| W-052 | Power-K (`Cmd+K` auf `/{ws:acme}`) | `root`, `search-results`, `theme-page`, `no-results` | – | I5 | CE-SRCH |
| W-053 | Projekt veröffentlichen (Modal auf `…/projects/{project:WEB}/issues`) | `unpublished`, `published`, `settings-open` | – | I6 | CE-SPACE-001, -002 |
| – | `/{ws:acme}/settings/billing` | **nicht registriert** (U11) | – | – | – |
| – | `/{ws:acme}/active-cycles` | **nicht registriert** in CE (U12, kommt mit B4) | – | – | – |
| – | `/`, `/sign-up`, `/accounts/forgot-password`, `/accounts/reset-password`, `/accounts/set-password` | Weiterleitung auf Keycloak bzw. entfallen (ADR-008); Optik über K-001…K-004 | – | I0 | CE-AUTH-001 (angepasst) |

**Admin (God Mode, `/god-mode/`)**

| ID | Route | Zustände | Inkr. | CE |
|---|---|---|---|---|
| A-001 | `/god-mode/` (Home) | `redirect-to-keycloak` (nicht fotografiert), `instance-not-ready`, `instance-failure`, `logo-spinner` | I0 | CE-INST-006 |
| A-002 | `/god-mode/general` | `base`, `sidebar-collapsed`, `mobile-overlay`, `help-popover`, `account-dropdown` (Theme-Umschalter E-33) | I6 | CE-INST, CE-INST-012 |
| A-003 | `/god-mode/workspace` | `base`, `skeleton`, `load-more`, `empty` | I6 | CE-INST |
| A-004 | `/god-mode/workspace/create` | `base`, `validation-errors`, `slug-taken` | I6 | CE-INST |
| A-005 | `/god-mode/email` | `smtp-off`, `smtp-on-form`, `skeleton`, `test-dialog-step-1`, `…-2`, `…-3` | I6 | CE-INST |
| A-006 | `/god-mode/authentication` | `keycloak-status` (angepasst: nur Anzeige des Keycloak-Anschlusses, ADR-008), `skeleton` | I6 | CE-INST (angepasst) |
| A-007 | `/god-mode/ai` | `base`, `filled`, `discard-dialog` | I6 | CE-INST, CE-AI |
| A-008 | `/god-mode/image` | `base`, `filled` | I6 | CE-INST |
| A-009 | `/god-mode/{unbekannt}` (404) | `base` | I6 | CE-INST |
| – | `/god-mode/authentication/{github,gitlab,google,gitea}` | entfallen (CE-INST-020…-024) | – | – |

**Space (`/spaces/`)**

| ID | Route | Zustände | Inkr. | CE |
|---|---|---|---|---|
| S-001 | `/spaces/` | `logged-in-view` (CE-SPACE-014), `instance-failure`, `logo-spinner` | I6 | CE-SPACE-014, -015 |
| S-002 | `/spaces/{ws:acme}/{project:WEB}` | `list` (Gruppen offen/zu), `kanban`, `navbar-anonymous`, `navbar-logged-in`, `navbar-menu-open`, `filters-popover`, `active-filters-bar`, `load-more`, `peek-side`, `peek-modal`, `peek-full`, `comments-empty`, `comments-full`, `composer`, `sign-in-hint`, `reaction-picker`, `votes-active`, `iframe` (CE-SPACE-029), `not-published` | I6 | CE-SPACE-017…-030 |
| S-003 | `/spaces/issues/{anchor:WEB}` | `base` (Board mit Social-Meta) | I6 | CE-SPACE-017 |
| S-004 | `/spaces/{unbekannt}` (404), Board-Fehler, Fehlerseite | je `base` | I6 | CE-SPACE-031 |
| S-005 | „Powered by Plane Publish“-Badge (auf S-002) | `base` | I6 | CE-SPACE-032 |

**Keycloak-Login-Theme**

| ID | Seite (`.ftl`) | Vergleich gegen | Inkr. | CE |
|---|---|---|---|---|
| K-001 | `login.ftl` (Client `plane-web`) | Original `/` (Sign-in, E-Mail-Schritt + Passwort-Schritt) | I0 | CE-AUTH-001 |
| K-002 | `login.ftl` (Client `plane-admin`) | Original `/god-mode/` (Admin-Sign-in) | I0 | CE-AUTH-001 |
| K-003 | `login.ftl` (Client `plane-space`) | Original `/spaces/` (Space-Sign-in) | I0 | CE-AUTH-001 |
| K-004 | `login.ftl` mit Fehlermeldung, `error.ftl`, `login-update-password.ftl` (mit Stärkeanzeige) | Original Auth-Banner und Set-Password-Seite | I0 | CE-AUTH-001 |

**Komponenten-Galerie**: je Propel-Komponente, Propel-Element, Blocks-Modul ein Eintrag `G-<name>` mit allen Stories (§3.14.9); Inkrement = Spalte „Inkr.“ aus §4.2/§4.3/§4.7.

---

## 5. Code-Skelette

Die Skelette legen Konventionen fest; sie sind nicht vollständig. Namen, Pfade und Signaturen sind verbindlich.

### 5.1 CSS-Einstieg und PostCSS

```jsonc
// funk./frontend/.postcssrc.json  (inhaltsgleich zu packages/tailwind-config/postcss.config.js)
{ "plugins": { "@tailwindcss/postcss": {} } }
```

```css
/* funk./frontend/libs/shared/tailwind-config/index.css
 * VENDORED from packages/tailwind-config/index.css (Plane v1.4.2) – SPDX-License-Identifier: AGPL-3.0-only
 * Only @import/@source lines are rewritten (see VENDORED.md). Do not edit anything else. */
@import "tailwindcss" source(none);                      /* orig: @import "tailwindcss"; */
@import "./propel-styles/propel.css";                     /* orig: @import "@makeplane/propel/styles"; */
@source "../../../apps/*/src/**/*.{html,ts}";             /* orig: @source "../**/*.{ts,tsx}"; */
@source "../../**/src/**/*.{html,ts}";
@source not "../../**/*.spec.ts";

* {
  -webkit-text-size-adjust: 100%;
  /* … ab hier byte-identisch zum Original … */
}
```

```css
/* funk./frontend/apps/web/src/styles.css – VENDORED from apps/web/styles/globals.css */
@import "../../../libs/shared/tailwind-config/index.css";  /* orig: @import "@plane/tailwind-config/index.css"; */
@import "../../../libs/shared/editor/styles/index.css";    /* orig: @import "@plane/editor/styles"; */
@import "./styles/power-k.css";
@import "./styles/emoji.css";
@plugin "@tailwindcss/typography";
@import "../../../libs/shared/tailwind-config/overrides.css"; /* einzige Zusatzzeile: [data-pl-host]{display:contents} (UI-DEV-000) */
/* … Rest byte-identisch … */
```

### 5.2 Generierte Varianten (`port-variants.mjs` → `variants.ts`)

```ts
// GENERATED – do not edit. Source: @makeplane/propel@0.7.3 dist/elements/button/variants.js (sha256: …)
// SPDX-License-Identifier: AGPL-3.0-only
import { cva } from 'class-variance-authority';
import { buttonGeometryVariants } from '../../internal/button-geometry';
import { composeVariants } from '../../internal/compose-variants';
import { controlChromeVariants } from '../../internal/control-chrome';

/** The full Button className: the shared control chrome composed with the label-button geometry. */
export const buttonVariants = composeVariants(controlChromeVariants, buttonGeometryVariants);
export const buttonLabelVariants = cva('');

export type ButtonVariant = 'primary' | 'secondary' | 'tertiary' | 'ghost' | 'danger' | 'danger-outline';
export type ButtonSize = 'xs' | 'sm' | 'md' | 'lg';
export type ButtonStretch = 'auto' | 'full';
```

```ts
// funk./tools/propel-port/port-variants.spec.mjs (Node) – Paritätstest der generierten Varianten
import * as orig from '../propel-port/.cache/propel/package/dist/elements/button/variants.js';
import * as port from '../../frontend/libs/shared/propel/src/elements/button/variants.ts'; // via tsx-Loader
for (const variant of ['primary','secondary','tertiary','ghost','danger','danger-outline'])
  for (const size of ['xs','sm','md','lg'])
    for (const stretch of ['auto','full'])
      assert.equal(port.buttonVariants({ variant, size, stretch }), orig.buttonVariants({ variant, size, stretch }));
```

### 5.3 Element-Direktive und Komponente (`button`)

```ts
// PRP/elements/button/button.directive.ts
import { Directive, input } from '@angular/core';
import { buttonVariants, ButtonSize, ButtonStretch, ButtonVariant } from './variants';

/** Styled element only (Propel `elements/button`): classes, no behavior. */
@Directive({
  selector: '[plButtonEl]',
  host: { '[class]': 'classes()' },
})
export class PlButtonEl {
  readonly variant = input.required<ButtonVariant>();
  readonly size = input.required<ButtonSize>();
  readonly stretch = input.required<ButtonStretch>();
  protected readonly classes = () =>
    buttonVariants({ variant: this.variant(), size: this.size(), stretch: this.stretch() });
}
```

```ts
// PRP/components/button/button.component.ts
import { ChangeDetectionStrategy, Component, ElementRef, ViewEncapsulation, booleanAttribute, computed, inject, input } from '@angular/core';
import { NgTemplateOutlet } from '@angular/common';
import { PlButtonEl } from '../../elements/button/button.directive';
import { PlButtonLabelEl } from '../../elements/button/button-label.directive';
import { PlSpinnerSlot } from '../../internal/spinner.component';
import { PlIcon, PlIconSource } from '../../internal/icon.component';
import { LoaderCircle } from '@plane/icons-lucide/v134';

@Component({
  selector: 'button[plButton], a[plButton]',
  changeDetection: ChangeDetectionStrategy.OnPush,
  encapsulation: ViewEncapsulation.None,
  imports: [NgTemplateOutlet, PlButtonLabelEl, PlSpinnerSlot, PlIcon],
  hostDirectives: [{ directive: PlButtonEl, inputs: ['variant', 'size', 'stretch'] }],
  host: {
    '[attr.type]': 'isNative ? type() : null',
    '[attr.disabled]': 'isNative && isDisabled() && !loading() ? "" : null',
    '[attr.aria-disabled]': 'isDisabled() && (loading() || !isNative) ? "true" : null',
    '[attr.data-disabled]': 'isDisabled() ? "" : null',
    '[attr.aria-busy]': 'loading() ? "true" : null',
    '[attr.tabindex]': '!isNative && !isDisabled() ? 0 : null',
  },
  template: `
    @if (iconPosition() === 'start') { <ng-container [ngTemplateOutlet]="slot" /> }
    <span plButtonLabelEl>{{ label() }}</span>
    @if (iconPosition() === 'end') { <ng-container [ngTemplateOutlet]="slot" /> }
    <ng-template #slot>
      @if (icon() && loading()) { <pl-spinner-slot [active]="true" [glyph]="LoaderCircle" /> }
      @else if (icon()) { <span plIcon [icon]="icon()!"></span> }
      @else { <pl-spinner-slot [active]="loading()" [glyph]="LoaderCircle" /> }
    </ng-template>`,
})
export class PlButton {
  protected readonly LoaderCircle = LoaderCircle;
  protected readonly isNative = inject(ElementRef<HTMLElement>).nativeElement.tagName === 'BUTTON';
  readonly label = input.required<string>();
  readonly icon = input<PlIconSource | null>(null);
  readonly iconPosition = input<'start' | 'end'>('start');
  readonly loading = input(false, { transform: booleanAttribute });
  readonly disabled = input(false, { transform: booleanAttribute });
  readonly type = input<'button' | 'submit' | 'reset'>('button');
  /** Propel: `disabled || loading`; while loading the button stays focusable (`focusableWhenDisabled`). */
  protected readonly isDisabled = computed(() => this.disabled() || this.loading());
}
```

Hinweis: Die exakte Attribut-Belegung (`disabled` vs. `aria-disabled`, `tabindex`) wird gegen den DOM-Vertrag `dom-contracts/gallery/button/*.dom.html` geprüft; der Code oben bildet das Base-UI-1.6.0-Verhalten nach (natives `disabled`, außer bei `focusableWhenDisabled`).

### 5.4 Präsenz und Spinner

```ts
// PRP/headless/presence.ts
import { signal } from '@angular/core';

export type PresenceStatus = 'unmounted' | 'starting' | 'open' | 'ending';

/** Base-UI-compatible enter/exit lifecycle: data-starting-style for one frame, data-ending-style until all animations finish. */
export class PresenceController {
  readonly status = signal<PresenceStatus>('unmounted');
  readonly mounted = () => this.status() !== 'unmounted';

  open(): void {
    if (this.status() === 'open' || this.status() === 'starting') return;
    this.status.set('starting');
    requestAnimationFrame(() => this.status.set('open'));
  }

  close(el: HTMLElement | null, fallbackMs?: number): void {
    if (!this.mounted()) return;
    this.status.set('ending');
    const finish = () => { if (this.status() === 'ending') this.status.set('unmounted'); };
    if (!el) return finish();
    requestAnimationFrame(() => {
      const running = el.getAnimations({ subtree: true });
      if (running.length === 0) return finish();
      Promise.allSettled(running.map(a => a.finished)).then(finish);
      if (fallbackMs !== undefined) setTimeout(finish, fallbackMs);
    });
  }

  /** Host-attribute helpers used by every popup part. */
  startingAttr = () => (this.status() === 'starting' ? '' : null);
  endingAttr = () => (this.status() === 'ending' ? '' : null);
}
```

```ts
// PRP/internal/spinner.component.ts  (Propel internal/spinner.js)
@Component({
  selector: 'pl-spinner-slot',
  encapsulation: ViewEncapsulation.None,
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [PlSvgIcon],
  host: { 'data-pl-host': '' },
  template: `
    @if (mounted()) {
      <span aria-hidden="true" [class]="classes()" [attr.data-ending-style]="active() ? null : ''"
            (animationend)="onAnimationEnd($event)">
        <svg plIcon [icon]="glyph()"></svg>
      </span>
    }`,
})
export class PlSpinnerSlot {
  static readonly CONCEAL_TIMEOUT_MS = 250; // SPINNER_CONCEAL_TIMEOUT_MS
  readonly active = input(true);
  readonly glyph = input.required<PlIconDef>();
  protected readonly mounted = signal(false);
  protected readonly classes = computed(() => cx(spinnerVariants(),
    this.active() ? 'animate-spinner-reveal motion-reduce:animate-none'
                  : 'animate-spinner-conceal motion-reduce:animate-none'));
  constructor() {
    effect((onCleanup) => {
      if (this.active()) { this.mounted.set(true); return; }
      if (!untracked(this.mounted)) return;
      const id = setTimeout(() => this.mounted.set(false), PlSpinnerSlot.CONCEAL_TIMEOUT_MS);
      onCleanup(() => clearTimeout(id));
    });
  }
  protected onAnimationEnd(e: AnimationEvent): void {
    if (!this.active() && e.target === e.currentTarget) this.mounted.set(false);
  }
}
```

### 5.5 Positionierung (`@floating-ui/dom`)

```ts
// PRP/headless/floating.ts
import { arrow, autoUpdate, computePosition, flip, hide, limitShift, offset, shift, size, type Placement } from '@floating-ui/dom';

export interface PlPositionOptions {
  side: 'top' | 'bottom' | 'left' | 'right' | 'inline-start' | 'inline-end';
  align: 'start' | 'center' | 'end';
  sideOffset: number;            // Propel-Defaults: Tooltip 8, Menu 6, Popover/Combobox 4
  alignOffset: number;
  collisionPadding: number;      // Tooltip/Popover 5, Menu 8
  arrowPadding?: number;         // Tooltip 5
  sticky: boolean;
  positionMethod: 'absolute' | 'fixed';
  dir: 'ltr' | 'rtl';
  arrowEl?: HTMLElement | null;
}

export function startPlPositioning(anchor: Element, positioner: HTMLElement, popup: HTMLElement, o: PlPositionOptions): () => void {
  const update = async () => {
    const placement = toPlacement(o.side, o.align, o.dir);
    const { x, y, placement: final, middlewareData } = await computePosition(anchor, positioner, {
      strategy: o.positionMethod,
      placement,
      middleware: [
        offset({ mainAxis: o.sideOffset, crossAxis: o.alignOffset }),
        flip({ padding: o.collisionPadding }),
        shift({ padding: o.collisionPadding, limiter: o.sticky ? undefined : limitShift() }),
        size({
          padding: o.collisionPadding,
          apply({ availableWidth, availableHeight, rects }) {
            positioner.style.setProperty('--available-width', `${availableWidth}px`);
            positioner.style.setProperty('--available-height', `${availableHeight}px`);
            positioner.style.setProperty('--anchor-width', `${rects.reference.width}px`);
            positioner.style.setProperty('--anchor-height', `${rects.reference.height}px`);
          },
        }),
        ...(o.arrowEl ? [arrow({ element: o.arrowEl, padding: o.arrowPadding ?? 0 })] : []),
        hide(),
      ],
    });
    Object.assign(positioner.style, { position: o.positionMethod, left: `${x}px`, top: `${y}px` });
    const [side, align = 'center'] = final.split('-') as [string, string?];
    for (const el of [positioner, popup]) { el.dataset['side'] = fromPhysical(side, o); el.dataset['align'] = align; }
    popup.style.setProperty('--transform-origin', transformOrigin(side, align));
    toggleAttr(positioner, 'data-anchor-hidden', !!middlewareData.hide?.referenceHidden);
  };
  return autoUpdate(anchor, positioner, update);
}
// toPlacement, fromPhysical, transformOrigin, toggleAttr: siehe floating.spec.ts (24 Kollisionsfälle gegen Referenz-Galerie)
declare function toPlacement(side: PlPositionOptions['side'], align: PlPositionOptions['align'], dir: 'ltr' | 'rtl'): Placement;
declare function fromPhysical(side: string, o: PlPositionOptions): string;
declare function transformOrigin(side: string, align: string): string;
declare function toggleAttr(el: HTMLElement, name: string, on: boolean): void;
```

### 5.6 Kompositum mit Portal (`tooltip`)

```html
<!-- Verwendung (entspricht <Tooltip label="…" shortcut="…"><IconButton … /></Tooltip>) -->
<pl-tooltip [label]="t('customize_navigation')" side="bottom">
  <button plIconButton plTooltipTrigger variant="ghost" size="sm" [icon]="PreferencesOutline"
          [attr.aria-label]="t('customize_navigation')"></button>
</pl-tooltip>
```

```ts
// PRP/components/tooltip/tooltip.component.ts
@Component({
  selector: 'pl-tooltip',
  encapsulation: ViewEncapsulation.None,
  changeDetection: ChangeDetectionStrategy.OnPush,
  host: { 'data-pl-host': '' },
  providers: [PlTooltipState],
  template: `
    <ng-content />
    <ng-template #popup>
      <div plPositioner [hideWhenAnchorHidden]="!sticky()">
        <div plTooltipPopupEl [layout]="layout()" role="tooltip" [id]="state.popupId"
             [attr.data-starting-style]="state.presence.startingAttr()"
             [attr.data-ending-style]="state.presence.endingAttr()">
          {{ label() }}
          @if (shortcut()) { <kbd plShortcut [keys]="shortcut()!" size="sm"></kbd> }
          @if (showArrow()) { <div plTooltipArrowEl></div> }
        </div>
      </div>
    </ng-template>`,
})
export class PlTooltip {
  protected readonly state = inject(PlTooltipState);   // Delay-Gruppe, Presence, Portal, Floating
  readonly label = input<string | null>(null);
  readonly disabled = input(false);
  readonly shortcut = input<string | string[] | null>(null);
  readonly layout = input<'single' | 'stacked'>('single');
  readonly side = input<PlPositionOptions['side']>('top');
  readonly sideOffset = input(8);
  readonly align = input<PlPositionOptions['align']>('center');
  readonly showArrow = input(false);
  readonly sticky = input(false);
  readonly delay = input<number | undefined>(undefined);  // Default 600 ms über PlTooltipProvider
  /** Propel: no popup markup when label is empty/whitespace or disabled. */
  protected readonly mountable = computed(() => !this.disabled() && !!this.label()?.trim());
}
```

### 5.7 Icons

```ts
// PRP/icons/types.ts
export type PlSvgNode = [tag: string, attrs: Record<string, string>, children?: PlSvgNode[]];
export interface PlIconDef { readonly name: string; readonly attrs: Record<string, string>; readonly children: readonly PlSvgNode[]; }

// PRP/icons/miscellaneous/palette-outline.ts  (GENERATED by tools/propel-port/port-icons.mjs)
export const PaletteOutline: PlIconDef = {
  name: 'PaletteOutline',
  attrs: { xmlns: 'http://www.w3.org/2000/svg', fill: 'none', viewBox: '0 0 16 16', width: '1em', height: '1em', 'aria-hidden': 'true' },
  children: [['path', { fill: 'currentColor', d: 'M…' }]],
};
```

```ts
// PRP/icons/svg-icon.component.ts – renders PlIconDef without innerHTML (Trusted Types safe)
const SVG_NS = 'http://www.w3.org/2000/svg';
@Component({ selector: 'svg[plIcon]', template: '', encapsulation: ViewEncapsulation.None, changeDetection: ChangeDetectionStrategy.OnPush })
export class PlSvgIcon {
  readonly icon = input.required<PlIconDef>({ alias: 'icon' });
  private readonly host = inject(ElementRef<SVGSVGElement>).nativeElement;
  private readonly r = inject(Renderer2);
  constructor() {
    effect(() => {
      const def = this.icon();
      // Original: {...props} folgt nach den Default-Attributen → Konsumenten-Attribute gewinnen
      for (const [k, v] of Object.entries(def.attrs)) if (!this.host.hasAttribute(k)) this.r.setAttribute(this.host, k, v);
      while (this.host.firstChild) this.r.removeChild(this.host, this.host.firstChild);
      const build = ([tag, attrs, kids]: PlSvgNode, parent: Element) => {
        const el = this.r.createElement(tag, SVG_NS);
        for (const [k, v] of Object.entries(attrs)) this.r.setAttribute(el, k, v);
        kids?.forEach(k => build(k, el));
        this.r.appendChild(parent, el);
      };
      def.children.forEach(n => build(n, this.host));
    });
  }
}
```

### 5.8 Theme-Inline-Script und `ThemeService`

```ts
// FE/libs/shared/theme/src/inline-script.ts – wird beim Build als <script nonce="{{CSP_NONCE}}"> in index.html eingesetzt
export const themeInlineScript = (themes: readonly string[], defaultTheme = 'system') => `(() => {
  var d = document.documentElement, themes = ${JSON.stringify(themes)};
  var t; try { t = localStorage.getItem('theme'); } catch (e) {}
  if (!t || (t !== 'system' && themes.indexOf(t) < 0)) t = '${defaultTheme}';
  var r = t === 'system' ? (matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light') : t;
  d.setAttribute('data-theme', r);
  if (r === 'light' || r === 'dark') d.style.colorScheme = r;
})();`;
```

```ts
// FE/libs/shared/theme/src/theme.service.ts
@Injectable({ providedIn: 'root' })
export class ThemeService {
  private readonly cfg = inject(THEME_CONFIG);      // { themes, defaultTheme: 'system', enableSystem: true }
  private readonly mql = matchMedia('(prefers-color-scheme: dark)');
  readonly systemTheme = signal<'light' | 'dark'>(this.mql.matches ? 'dark' : 'light');
  readonly theme = signal<string>(readStoredTheme(this.cfg));
  readonly resolvedTheme = computed(() => (this.theme() === 'system' ? this.systemTheme() : this.theme()));
  readonly themes = computed(() => (this.cfg.enableSystem ? [...this.cfg.themes, 'system'] : this.cfg.themes));

  constructor() {
    this.mql.addEventListener('change', e => this.systemTheme.set(e.matches ? 'dark' : 'light'));
    addEventListener('storage', e => { if (e.key === 'theme') this.theme.set(e.newValue ?? this.cfg.defaultTheme); });
    effect(() => applyToDocument(this.resolvedTheme()));   // data-theme + color-scheme wie next-themes
  }
  setTheme(value: string): void {
    try { localStorage.setItem('theme', value); } catch { /* private mode: ignore like next-themes */ }
    this.theme.set(value);
  }
}
declare function readStoredTheme(cfg: { themes: readonly string[]; defaultTheme: string }): string;
declare function applyToDocument(resolved: string): void;
```

### 5.9 Blocks-Komponente mit `className` und `cn()`

```ts
// BLKT/card/card.component.ts  (BLK/card/card.tsx)
import { cn } from '@plane/utils';
import { getCardDirectionClassName, getCardSpacingClassName, getCardVariantClassName, CardDirection, CardSpacing, CardVariant } from './helper';

@Component({
  selector: 'div[plBlkCard]',
  encapsulation: ViewEncapsulation.None,
  changeDetection: ChangeDetectionStrategy.OnPush,
  host: { '[class]': 'classes()' },
  template: '<ng-content />',
})
export class PlBlkCard {
  readonly variant = input<CardVariant>('with-shadow');
  readonly spacing = input<CardSpacing>('lg');
  readonly direction = input<CardDirection>('column');
  readonly className = input<string>('');
  protected readonly classes = computed(() => cn(
    'bg-surface-1 rounded-lg border-[0.5px] border-subtle w-full flex flex-col',
    getCardDirectionClassName(this.direction()), getCardVariantClassName(this.variant()),
    getCardSpacingClassName(this.spacing()), this.className()));
}
```

### 5.10 Katalog, Abweichungen, Stories

```yaml
# FE/apps/e2e/visual/catalog/web.catalog.yaml
- id: W-026
  app: web
  route: "/{ws:acme}/projects/{project:WEB}/issues"
  role: admin
  increment: I2
  ce: [CE-LV-001, CE-LV-002, CE-WI-001]
  tags: [theme-full, wide, layouts]
  setup:
    localStorage: { "issue_layout_{project:WEB}": "list" }   # Layout per Display-Filter-API im Seed gesetzt
  states:
    - id: base
      wait: ["[data-testid='issue-list-root']"]
    - id: display-props-popover
      steps: [{ click: "button:has-text('Display')" }]
      wait: ["[role='dialog'][data-side]"]
    - id: peek-side
      steps: [{ click: "text=WEB-1" }]
      wait: ["#issue-peek-overview"]
  compare: { pixel: page, dom: true, aria: true, axe: true }
```

```yaml
# FE/apps/e2e/visual/ui-deviations.yaml
- id: UI-DEV-000
  kind: extra-css
  reason: "[data-pl-host]{display:contents} – Angular-Host-Elemente ohne Box (D09-ADR-03)"
  adr: D09-ADR-03
  entries: ["*"]
  approved_by: architecture
- id: UI-DEV-001
  kind: pixel+dom
  reason: "Editions-Badge 'Community' → nicht interaktives Versions-Badge (ADR-001, U3)"
  adr: ADR-001
  entries: [W-001]
  selector: "aside [class~='h-12'][class~='border-t']"
  approved_by: null            # wird bei Abnahme gesetzt
```

```jsonc
// funk./tools/gallery-stories/button.stories.json
{
  "component": "button",
  "matrix": { "source": "elements/button/variants", "axes": ["variant", "size", "stretch"], "fixed": { "label": "Button" } },
  "stories": [
    { "id": "loading", "props": { "variant": "primary", "size": "md", "stretch": "auto", "label": "Saving", "loading": true } },
    { "id": "icon-end", "props": { "variant": "secondary", "size": "sm", "stretch": "auto", "label": "Next", "icon": "ArrowNarrowRightOutline", "iconPosition": "end" } },
    { "id": "focus-visible", "props": { "variant": "primary", "size": "md", "stretch": "auto", "label": "Focus" }, "steps": [{ "press": "Tab" }] }
  ]
}
```

### 5.11 Playwright-Konfiguration und Vergleichsspezifikation

```ts
// FE/apps/e2e/visual/playwright.visual.config.ts
import { defineConfig } from '@playwright/test';
export default defineConfig({
  testDir: './specs',
  snapshotPathTemplate: '{testDir}/../baselines/{arg}{ext}',   // Baselines kommen ausschließlich aus capture-reference
  updateSnapshots: 'none',
  workers: 4,
  use: {
    baseURL: process.env.FUNK_BASE_URL ?? 'http://localhost:8090',
    locale: 'en-US', timezoneId: 'UTC', reducedMotion: 'reduce', deviceScaleFactor: 1,
    launchOptions: { args: ['--disable-gpu', '--font-render-hinting=none'] },
  },
  expect: { toHaveScreenshot: { threshold: 0.1, maxDiffPixelRatio: 0.002, animations: 'disabled', caret: 'hide' } },
  projects: [{ name: 'chromium', use: { browserName: 'chromium' } }],
});
```

```ts
// FE/apps/e2e/visual/specs/catalog.visual.spec.ts
import { expect, test } from '@playwright/test';
import { loadCatalog, resolveRoute, applyTheme, runSteps, waitStable } from '../support/catalog';
import { normalizeDom } from '../../../../../tools/visual/dom-normalize';
import { readContract } from '../support/contracts';

for (const entry of loadCatalog(process.env.CATALOG ?? 'web')) {
  for (const state of entry.states) {
    for (const { theme, viewport } of entry.matrix(state)) {
      test(`${entry.id} ${state.id} ${theme} ${viewport.name}`, async ({ page }) => {
        await page.setViewportSize(viewport);
        await page.clock.setFixedTime(new Date('2026-01-16T09:00:00Z'));
        await applyTheme(page, theme);
        await page.goto(resolveRoute(entry.route, 'funk'));
        await runSteps(page, state.steps);
        await waitStable(page, state.wait);

        const key = `${entry.app}/${entry.id}/${state.id}/${theme}-${viewport.name}`;
        await expect(page).toHaveScreenshot(`${key}.png`, entry.pixelOptions(state));
        if (entry.compare.dom && viewport.name === 'desktop-1440' && theme === 'light') {
          expect(await page.evaluate(normalizeDom, { seedMap: 'funk' })).toBe(readContract('dom', key));
          expect(await page.locator('body').ariaSnapshot()).toBe(readContract('aria', key));
        }
      });
    }
  }
}
```

### 5.12 DOM-Normalisierung (Auszug)

```ts
// funk./tools/visual/dom-normalize.ts – läuft identisch gegen Original und Ziel (page.evaluate)
export function normalizeDom(opts: { seedMap: 'original' | 'funk' }): string {
  const roots = [document.querySelector('#root, app-root')!, ...Array.from(document.body.children).filter(isPortal)];
  const ids = new Map<string, string>();
  const ID_ATTRS = ['id', 'for', 'aria-controls', 'aria-labelledby', 'aria-describedby', 'aria-activedescendant', 'aria-owns', 'aria-errormessage', 'headers', 'list'];
  const out: string[] = [];
  const walk = (n: Node): void => {
    if (n.nodeType === Node.COMMENT_NODE) return;                                  // N2
    if (n.nodeType === Node.TEXT_NODE) { const t = n.textContent!.replace(/\s+/g, ' ').trim(); if (t) out.push(t); return; } // N8
    const el = n as Element;
    if (['SCRIPT', 'STYLE', 'LINK'].includes(el.tagName)) return;                    // N2
    if (el.hasAttribute('data-pl-host') || el.tagName === 'ROUTER-OUTLET') { el.childNodes.forEach(walk); return; } // N3
    const attrs = Array.from(el.attributes)
      .filter(a => !/^(ng-version|_ngcontent-|_nghost-|ng-reflect-|data-pl-host)/.test(a.name))
      .map(a => [a.name, normalizeValue(a.name, a.value, ids, ID_ATTRS, opts)] as const)
      .sort(([a], [b]) => a.localeCompare(b));                                      // N9
    out.push(`<${el.tagName.toLowerCase()}${attrs.map(([k, v]) => ` ${k}="${v}"`).join('')}>`);
    el.childNodes.forEach(walk);
    out.push(`</${el.tagName.toLowerCase()}>`);
  };
  roots.forEach(walk);
  return out.join('\n');
}
// normalizeValue: N4 (IDs → id-n), N5 (class sortiert), N6 (style sortiert/gerundet), N7 (URLs/Seed-IDs/Hashes)
declare function normalizeValue(name: string, value: string, ids: Map<string, string>, idAttrs: string[], o: { seedMap: string }): string;
declare function isPortal(el: Element): boolean;
```

---

