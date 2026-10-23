# 10 – Rich-Text-Editor in Angular (Port von `packages/editor`)

> **Stand:** 23.10.2026. **Status:** Entwurf zur Abnahme. **Verbindlichkeit:** bindend für alle Implementierungs-Agenten, die Editor-Code in `funk.` schreiben oder einbinden; nachrangig zu `00-grundsatzentscheidungen.md` (ADR-000…009), `01-zielarchitektur-und-tech-stack.md` (ADR-010 ff., insbesondere ADR-042) und `17-abgleich-dokumentuebergreifend.md`.
>
> **Kürzel (wie 01/08/16):** Original: `PKG/` = `packages/`, `ED0/` = `packages/editor/src/`, `WEB/` = `apps/web/`, `SPC/` = `apps/space/`, `LIVE/` = `apps/live/src/`, `API/` = `apps/api/plane/`. Ziel (Repository `funk.`, ADR-009): `FE/` = `funk./frontend/`, `ED/` = `FE/libs/shared/editor/`, `EXT/` = `FE/libs/web/extensions/src/`, `BE/` = `funk./src/`. Analyse-Dokumente: `A12` = `migration/analysis/12-editor-echtzeit-live.md`, `A08`, `A13a`, `A13b` analog. Architektur-Dokumente: `D01` … `D17` = `migration/architecture/01-…` … `17-…`. Feature-Dokumente: `F10` = `migration/features/10-ce-feature-katalog.md`, `F30` = `…/30-paid-auswahlliste.md`.
>
> **Maschinenlesbar:** `migration/architecture/_data/10-editor-file-map.json` – Datei-für-Datei-Abbildung aller 225 Dateien von `ED0/` (Kategorie, Ziel, Symbol, Inkrement, CE-IDs); identisch mit Anhang A.

## Inhaltsverzeichnis

1. Ziel & Scope (1.1 Ziel · 1.2 Im Scope · 1.3 Nicht im Scope · 1.4 Inkremente · 1.5 Vertikale Schnitte · 1.6 Quellen)
2. Entscheidungen (D10-ADR-01 … D10-ADR-23)
3. Detaildesign (3.1 Bibliotheksschnitt · 3.2 Versionen/Schema-Freeze · 3.3 Port-Regeln Kern · 3.4 UI-Port · 3.5 Angular-Bindung · 3.6 Varianten und Komponenten-API · 3.7 Lebenszyklus · 3.8 `EditorRefApi` · 3.9 Menüs und Overlays · 3.10 NodeViews · 3.11 Mentions · 3.12 Emoji · 3.13 Tabellen · 3.14 Bilder · 3.15 Kollaboration · 3.16 Titel-Editor · 3.17 Lite-Editor · 3.18 Read-only · 3.19 Markdown/Clipboard · 3.20 Editor-CSS · 3.21 Web-/Space-Hüllen · 3.22 Quirk-Politik · 3.23 Zoneless/Performance · 3.24 Sicherheit)
4. Mapping-Tabellen Original → Ziel (4.1 Extensions · 4.2 Plugins · 4.3 Komponenten · 4.4 Konsumenten · 4.5 CE-IDs)
5. Code-Skelette
6. Erweiterungspunkte für Bezahl-Pakete (inkl. D9-Block-Registry)
7. Akzeptanzkriterien & Tests
8. Risiken & offene Punkte
9. Abhängigkeiten zu anderen Dokumenten (02–16)
- Anhang A – Datei-für-Datei-Abbildung `ED0/` → `ED/` (225 Dateien)
- Anhang B – Prüfprotokoll

---

## 1. Ziel & Scope

### 1.1 Ziel

Der Tiptap-v2-Editor des Originals (`PKG/editor`, 225 Dateien, A12) wird so nach Angular 22 portiert, dass

1. **Schema, JSON, HTML und Yjs-Binärformat identisch** zum Original sind (Schema-Freeze, D01 ADR-042) – nachgewiesen durch Golden-Files (G-SCHEMA, G-DOC, D15 §3.7);
2. **DOM, Klassen, `data-*`-/ARIA-Attribute und Verhalten** aller Editor-Oberflächen (Varianten, Menüs, NodeViews, Tabellen-Handles, Bild-UI) dem Original entsprechen (ADR-005), gemessen über Visual-Regression ≤ 0,5 % (D09, Katalog W-046) und DOM-Parität (D09 §3.14.6);
3. der **framework-agnostische Kern als Quelltext 1:1** übernommen wird und nur die React-Schicht neu entsteht (D01 ADR-042);
4. das Ergebnis **airgapped** lauffähig ist (ADR-004: Emoji-Daten, Highlight-Sprachen, Fonts gebündelt, keine CDN-Abrufe);
5. die strukturrelevanten Bezahl-Pakete und das Paket **D9** später **ohne Umbau** des CE-Editors andocken (Kapitel 6).

### 1.2 Im Scope

| Bereich | Inhalt | Abschnitt |
|---|---|---|
| Editor-Varianten | Rich-Text-Editor, Lite-Text-Editor, Document-Editor (nicht kollaborativ, Versionen), Collaborative-Document-Editor (Pages) mit Titel-Editor; Read-only über `editable=false` | 3.6, 3.16–3.18 |
| Kern | alle Extensions/Nodes/Marks/Plugins/Helper/Konstanten/Typen aus A12 §2.5–§2.25, Konvertierungs-Helfer `yjs-utils`, `parser` | 3.3, 4.1, 4.2 |
| Angular-Bindung | vendorte Bindung (`EditorContent`, `AngularNodeViewRenderer`, `AngularRenderer`, `NodeViewWrapper`/`NodeViewContent`, Bubble-Menü-Direktive, `editorState()`) | 3.5 |
| UI | Slash-Commands, Bubble-Menü, Drag-Handle/Side-Menü, Block-Menü, Link-Ansicht, Tabellen-Handles/-Dropdowns, Bild-Uploader/-Toolbar/-Vollbild, Callout-Logo-/Farbwahl, Code-Block-Kopieren, Mention-/Emoji-Dropdowns | 3.9–3.14 |
| Kollaboration (Client) | `@hocuspocus/provider` 2.15.2, `y-prosemirror`, `y-indexeddb`, Stage-Maschine, Awareness-Token, Stateless-Kanal, REST-Fallback-Schnittstelle | 3.15 |
| Styles | `ED0/styles/*` 1:1, Tiptap-Core-CSS statisch, Import-Position | 3.20 |
| Hüllen | Web-Hüllen (`WEB/components/editor/**`, `WEB/hooks/editor/**`, `use-editor-flagging`, `use-additional-editor-mention`, `use-parse-editor-content`), Space-Hüllen (`SPC/components/editor/**`) | 3.21, 4.4 |
| Tests | G-SCHEMA (Browser-Seite), Editor-Specs (Vitest, Vitest-Browser, Playwright), LT-16, Visual W-046 | 7 |
| Erweiterungspunkte | `EDITOR_*`-Tokens, `EditorUiPort`-Schlüssel, Block-Registry D9, Kontrakt zur Server-Schema-Registry E-11 | 6 |

### 1.3 Nicht im Scope

| Thema | Zuständig |
|---|---|
| Realtime-Server (`Plane.Realtime`/`Plane.Collaboration`, Hocuspocus-Wire-Protokoll, YDotNet, Persistenz, Titel-Sync, Force-Close), serverseitige Konvertierung `Plane.Documents` (C#-Schema, HTML↔JSON↔Yjs), PDF-Renderer `Plane.Documents.Pdf` | `07-realtime-kollaboration-dokumente.md` (D07); D10 liefert nur das Schema-Inventar (§4.1) und den Golden-Vertrag (§3.2) |
| Pages-Fachlogik (Page-Store, Page-Toolbar-Hülle, Navigations-Pane, Versionen-Liste, Export-Dialog, Lock/Archive-Aktionen) | D08 (Stores/Services), Domänen-Lib `FE/libs/web/pages`; D10 liefert die Editor-Schnittstellen |
| HTML-Sanitizing (Allowlist) | D05 §3.17.3; D10 liefert die Liste der Tags/Attribute, die der Editor erzeugt (§3.24) |
| Emoji-Icon-Picker (`PKG/blocks/src/emoji-icon-picker`) | D09 (`PlBlkEmojiPicker`, I1); D10 nutzt ihn im Callout |
| Fachdesign der Bezahl-Pakete | später je Welle; hier nur Andockstellen (Kapitel 6) |
| AI im Editor (G3, nicht gewählt) | entfällt; Flag `ai` bleibt als Andockpunkt (§6.1, G1) |

### 1.4 Was wird in welchem Inkrement gebraucht

| Inkrement (D01 §1.3) | Editor-Ergebnis (abnehmbar) | Bausteine aus diesem Dokument, die fertig sein müssen | CE-IDs | Gate |
|---|---|---|---|---|
| **I0** Walking Skeleton | kein Editor-Screen. Fundament: Versions-Manifest und Pins (§3.2), Editor-CSS in der CSS-Pipeline (§3.20, G-CSS der Shell), Sheriff-Tags/Lint-Regeln der Editor-Lib (§3.1), Golden-Generator-Unterbefehl `schema` (§3.2.4); **Spike S5** im Spike-Track | `ED/styles/*` (Kopie), `ED/VERSIONS.json`, `FE/tools/editor-port/*` (Codemod, Drift-Check), Ordner-Gerüst `ED/{core,angular-binding,components,collaboration,extensibility,styles}` | – (technisch) | G-CSS (Shell), Lint |
| **I1** Workspace/Projekte/Konto | keine Editor-Oberfläche; Voraussetzungen anderer Dokumente: `PlBlkEmojiPicker` (D09, Callout-Logo), Asset-Upload-Basis `Plane.Assets` + `EditorAssetStore`-Gerüst (D08 Nr. 8) | – | – | – |
| **I2** Work Items & Layouts | **Schnitt ED-1** Lite-Editor in Kommentaren; **ED-2** Rich-Text-Editor in Work-Item-Beschreibung, Modal, Peek (mit Slash, Bubble, Drag-Handle, Block-Menü, Tabellen, Bildern, Callouts, Code, Mentions, Emoji, Links); **ED-3** Document-Editor read-only für Beschreibungs-Versionen | kompletter Kern (`ED/core`), Bindung, UI-Port-Implementierung, alle NodeViews/Menüs, Web-Hüllen `FE/libs/web/core/editor`, Tokens mit CE-Defaults, G-SCHEMA (Varianten `rich`, `lite`, `document`, `server`, `server-document`) | CE-PAGE-021…040 (ohne -013…-020), CE-WI-001, -005, -037, -041, -044, CE-UIX-009 (Editor-Teil), CE-I18N-010 | **S5 vollständig grün vor I2-Start** (D10-ADR-15); G-SCHEMA; Visual W-046 (Beschreibung) ≤ 0,5 % |
| **I3** Planung | Intake nutzt dieselben Hüllen (Beschreibung, Anlage-Dialog) – keine neuen Editor-Bausteine | – | CE-INT-004, -005, -010, -012 | Regression der I2-Specs |
| **I4** Pages & Realtime | **Schnitt ED-4** kollaborativer Page-Editor mit Titel-Editor, Offline-Cache, Sync-Status, Stateless-Kanal, REST-Fallback-Schnittstelle, Outline/Info/Assets-Schnittstellen; Schalter `collaboration-cursor` | `ED/collaboration` (`CollaborationSession`, `CollaborationProviderFactory`), `PlEdCollaborativeDocumentEditor`, `PlEdTitleEditor`, Navigation Titel↔Inhalt, G-SCHEMA (`collaborative`, `title`) | CE-PAGE-013…020 (Editor-Teil), CE-RT-002, -003 (Client-Schnittstelle), -004 (Client) | S1, S2, S5 grün; LT-16; Yjs-Browser-Roundtrip (AK-15-14) |
| **I5** Überblick | **Schnitt ED-5** Sticky-Editor (Lite + Sticky-Toolbar) | Web-Hülle `sticky-editor` | CE-HOME-010 | Visual Stickies |
| **I6** Außenwirkung | **Schnitt ED-6** Space: Rich read-only (Peek), Lite-Kommentare mit Bild-Upload, Space-Mentions; `EDITOR_EXTENSIONS` im Space-Scope (S44); GPT-Popover nutzt Rich-Editor (CE-AI-001) | Space-Hüllen `FE/libs/space/editor`, Space-Datei-Handler (Anchor-URLs) | CE-SPACE-024, -025, -030, CE-SPACE-007 (Editor-Teil), CE-AI-001 (Editor-Teil) | Visual Space |
| **I7** Härtung | CSP-Enforce ohne Editor-Brüche (§3.20.4), Airgap-Lauf (keine Fremd-Requests beim Öffnen von Emoji-Suggestion, Callout-Picker, Code-Block), Perf-Härtung | – | CE-OPS (Rest) | Airgap-E2E, CSP-Report leer |
| **W3** | D1/D2 (Dokumenttypen, Seiten-Events), D4 (Presence, Flag), D6 (Embeds/Mentions) docken über Tokens und Block-Registry an | Kapitel 6 | EE-* | Typ-X-Tests |
| **W8** | D7 (Kommentar-Mark), D9 (Blöcke), D10 (Databases) über `EDITOR_BLOCKS` + Server-Schema E-11 | §6.2 | EE-P07-019…039 | Golden je Block |

### 1.5 Vertikale Schnitte (Arbeitspakete des Editors)

Jeder Schnitt liefert Kern-/Komponentencode + Konsumenten-Hülle + Tests und ist einzeln abnehmbar (Schnittregel D01 §1.3). Die IDs werden in `migration/plan/_data/wp-ce.json` übernommen.

| Schnitt | Inkr. | Inhalt | Abnahme (Kurzform, Details §7) | hängt ab von |
|---|---|---|---|---|
| **ED-0** Spike S5 | I0 (Spike-Track) | Kern-Kopie per Codemod, Bindung, 8 NodeView-/Menü-Prototypen (Image mit Upload-Fortschritt, Callout, Mention, Table-View + Handles, Code-Block, Emoji-/Mention-Suggestion, Drag-Handle, Bubble-/Block-Menü), Schema-Snapshot aller Varianten, Yjs-Stabilität mit 2 Clients gegen den Original-Live-Server | Erfolgskriterien S5 (D01 §9) | – |
| **ED-1** Lite-Editor Kommentare | I2 | `PlEdLiteTextEditor`, Enter-Key, Mentions, Emoji, Links, Bilder (Upload), Lite-Toolbars der Web-Hülle, Read-only-Anzeige von Kommentaren | AK-D10-01, -05, -08, -12 | ED-0, `Plane.Assets` (I1) |
| **ED-2** Rich-Text-Beschreibung | I2 | `PlEdRichTextEditor` mit Slash, Bubble, Side-Menü/Drag-Handle, Block-Menü, Tabellen, Callouts, Code-Block, Bild-UI vollständig, Platzhalter, Deep-Link, `value`-Sync, `isMigrationUpdate` | AK-D10-01…-11 | ED-1 |
| **ED-3** Document read-only | I2 | `PlEdDocumentEditor` + `PlEdPageRenderer` + Outline-Extension für Beschreibungs-Versionen (CE-WI-041) | AK-D10-01, -13 | ED-2 |
| **ED-4** Kollaborativer Page-Editor | I4 | `PlEdCollaborativeDocumentEditor`, `PlEdTitleEditor`, `CollaborationSession`, IndexedDB, Stateless, Fallback-Schnittstelle (`setProviderDocument`, `getDocument`) | AK-D10-14…-18 | ED-3, S1 |
| **ED-5** Stickies | I5 | Sticky-Hülle (`sticky-editor`, Toolbar, Farbpalette) | AK-D10-19 | ED-1 |
| **ED-6** Space | I6 | Space-Hüllen, Anchor-Asset-URLs, Space-Mentions | AK-D10-20 | ED-2 |

### 1.6 Quellen

A12 (vollständige Inventare §2, Verhalten §3, Edge-Cases E1–E31 §3.25, Migrationshinweise §5), F10 (CE-PAGE-013…040, CE-RT-001…009, CE-WI-001/-005/-037/-041/-044, CE-HOME-010, CE-SPACE-024/-025/-030), Original-Quelltext `ED0/**`, `WEB/components/editor/**`, `WEB/hooks/editor/**`, `WEB/components/pages/editor/**`, `SPC/components/editor/**`, `pnpm-workspace.yaml`, `pnpm-lock.yaml` (aufgelöste Versionen), D01 (ADR-042, S5, §6), D08 (§3.12, §4.7, §6), D09 (§3.2.2, §3.8.2, Katalog W-046), D15 (§3.7, §7, Anhang B.8), D16 (X13, E-10, E-11, S10–S16, S44–S50, S60), D17 (ABG-016, ABG-026, ABG-029, Z-10, Z-12).

---

## 2. Entscheidungen (D10-ADR-01 ff.)

| ID | Belang | Entscheidung | Alternativen (verworfen) | Begründung | Lizenz | ab |
|---|---|---|---|---|---|---|
| **D10-ADR-01** | Tiptap-Linie und Versions-Pins | Tiptap **2.x** wie Original, und zwar **exakt die im Original-Lockfile aufgelösten Versionen** (nicht die Caret-Bereiche des Catalogs): `@tiptap/core` 2.27.3, `@tiptap/pm` 2.26.1, alle `@tiptap/extension-*`, `starter-kit`, `suggestion` 2.26.1 (StarterKit-Kinder `bold`, `italic`, `strike`, `code`, `code-block`, `paragraph`, `hard-break`, `horizontal-rule`, `bullet-list`, `ordered-list`, `dropcursor`, `gapcursor` 2.26.2 transitiv), `@tiptap/html` 2.26.2, `@tiptap/extension-bubble-menu` 2.26.3 (im Original transitiv über `@tiptap/react`); ProseMirror-Overrides `prosemirror-view` 1.42.6, `prosemirror-model` 1.25.12; vollständige Liste §3.2.1, maschinenlesbar `ED/VERSIONS.json`. Abweichende Auflösung im `funk.`-Lockfile bricht den CI-Check **G-EDPIN** | Tiptap 3 (Schema-/API-Bruch, BubbleMenu ohne tippy); Caret-Bereiche aus dem Catalog (Tiptap-2-Patches können Parse-/Render-Details ändern); einheitlich 2.27.3 für alle Pakete (Original testet diese Kombination nicht) | Identische Abhängigkeitsversionen sind die einzige Garantie für identisches Schema- und Parse-Verhalten; die Goldens werden mit genau diesem Stand erzeugt. npm `v2-latest` ist 2.27.3 (geprüft 23.10.2026) – die 2.x-Linie ist abgeschlossen, Pins veralten nicht durch Upstream-Bugfixes | MIT | I0 |
| **D10-ADR-02** | Bibliotheksschnitt | `ED/` besteht aus sechs Teil-Libs mit eigener `public-api.ts`: `core` (framework-frei), `angular-binding` (vendorte Bindung), `components` (Angular-UI: Varianten, Menüs, NodeViews, Services), `collaboration` (Provider-Kapselung, Session), `extensibility` (Tokens/Typen der Andockstellen), `styles` (CSS). Import-Aliase: `@plane/editor` (= `components` + Re-Exports aus `core`), `@plane/editor/core`, `@plane/editor/collaboration`, `@plane/editor/extensibility`. Richtung: `core ← angular-binding ← components ← collaboration`; `extensibility` darf nur `core` importieren | eine flache Lib (Abhängigkeiten nicht prüfbar); Kern als eigenes npm-Paket (Build-Overhead ohne Nutzen, 01 §6.1 „kein Lib-Build“) | Der Kern bleibt per Lint-Regel frei von Angular/React und damit gegen das Original vergleichbar (Drift-Check, Schema-Test in jsdom). Die Teilung entspricht D01 §6.1 (`core/`, `angular-binding/`, `components/`, `collaboration/`, `styles/`) und ergänzt nur `extensibility/` | – | I0 |
| **D10-ADR-03** | Übernahme des Kerns | **Datei-für-Datei-Kopie mit gleichem relativem Pfad** (`ED0/<pfad>` → `ED/core/src/<pfad>`, `.tsx` → `.ts`), erzeugt durch den Codemod `FE/tools/editor-port/port-core.mjs` (Importpfad-Umschreibung, Typ-Ersetzungen §3.3); jede Datei trägt einen Kopfkommentar `// ported-from: packages/editor/src/<pfad> @ <commit>`. Handänderungen nur in den 24 Dateien der Kategorien K2/NV (Anhang A), jeweils mit Marker `// PORT-DIFF(<grund>)`. Der CI-Check **G-EDCORE** (`FE/tools/editor-port/check-core-drift.mjs`) vergleicht jede K1-Datei normalisiert (Importpfade, Header) mit dem Original und lässt nur markierte Abweichungen zu | freie Neuimplementierung; Git-Submodul auf das Original (React-Abhängigkeiten im Baum) | Der Kern ist ~70 % des Codes und bereits framework-agnostisch (A12 §5.1); eine 1:1-Kopie hält Verhalten, Prioritäten und Edge-Cases exakt; der Drift-Check macht Abweichungen sichtbar | AGPL-3.0 (abgeleitetes Werk, Z-11 entschieden) | I0 (Werkzeug), I2 (Kern) |
| **D10-ADR-04** | React-Renderer im Kern | **UI-Port** statt Framework-Abhängigkeit: Die zehn Kern-Dateien, die `ReactNodeViewRenderer` bzw. `ReactRenderer` aufrufen (Callout, Code-Block, Custom-Image, Legacy-Image, Mention, Slash-Commands, Mention-Dropdown, Emoji-Suggestion, Tabellen-Spalten-/Zeilen-Handle), rufen stattdessen `uiNodeView(<key>)` bzw. `uiRender(editor, <key>, props)` aus `ED/core/src/ui-port/ui-port.ts` auf. Die Angular-Schicht registriert über die Tiptap-Extension `PlaneUiPortExtension` eine Implementierung mit einer Schlüssel→Komponente-Tabelle (§3.4). Ohne registrierten Port (Node/jsdom, Server-Schema-Test) liefern die Aufrufe `null` (keine NodeView, keine Dropdowns) | Extension-Dateien in die Angular-Schicht verschieben (dann hinge `core-without-props.ts` – Quelle des Server-Schemas – über `EmojiExtension` und `Table` an Angular); Injector als Extension-Option durchreichen (ändert alle Fabrik-Signaturen) | Hält den kompletten Extension-Graphen inkl. Server-Schema framework-frei, minimiert Diffs (eine Zeile je Aufrufstelle), erlaubt den S5-Fallback (DOM-NodeViews) und die D9-Blöcke über dieselbe Schlüsseltabelle | – | I2 |
| **D10-ADR-05** | Angular-Bindung | **Vendorte, eigene Bindung** `ED/angular-binding` mit **DOM-Parität zu `@tiptap/react` 2.26.1** (Elementstruktur, Klassen `react-renderer node-<typ>`, `data-node-view-wrapper`, `data-node-view-content`, Inline-Styles `white-space`), Muster (nicht Code-Abhängigkeit) von `ngx-tiptap` 13 (MIT; Peer `@tiptap/core ^2.7.0`, `@angular/core >=20`, geprüft 23.10.2026). Umfang: `EditorContentDirective`, `AngularNodeViewRenderer`, `AngularRenderer`, `NodeViewWrapperDirective`, `NodeViewContentDirective`, `NodeViewDragHandleDirective`, `BubbleMenuDirective`, `editorState()`, `PlaneUiPortExtension` | `ngx-tiptap` 13 als Abhängigkeit (Host-Elemente der Komponenten erzeugen anderes DOM; CSS des Originals adressiert `.node-imageComponent`, `.node-image` in `drag-drop.css`); ngx-tiptap 14/15 (nur Tiptap 3) | DOM-Gleichheit ist Pflicht (ADR-005, CSS-Selektoren); ~600 LOC eigene Bindung (D01 §2.2) entkoppeln von Fremd-Releases | MIT-Muster, eigener Code AGPL | I2 (S5 in I0) |
| **D10-ADR-06** | Hosting von NodeView-Komponenten | NodeView-Komponenten sind **Attribut-Selektor-Komponenten**, die auf das von der Bindung erzeugte Wrapper-Element gesetzt werden (`createComponent(..., { hostElement })`): äußeres Element `div|span.react-renderer.node-<typ>` (von `AngularNodeView`), darin das Wrapper-Element `div[data-node-view-wrapper]` (Host der Komponente, Klassen per Host-Binding), Content-Bereich über `[plEdNodeViewContent]` an beliebiger Stelle des Templates. Komponenten-Präfix `PlEd`, Selektoren `pl-ed-…`/`[plEd…]` (Regel D09-ADR-03) | Element-Selektoren (zusätzliche DOM-Ebene); `NgComponentOutlet` je NodeView (keine Kontrolle über `contentDOM`) | Gleiche DOM-Tiefe wie React (`NodeViewWrapper` erzeugt genau ein Element); kein Fremd-Element zwischen `.react-renderer` und Wrapper | – | I2 |
| **D10-ADR-07** | Floating-UI, Portale, Overlays | Editor-eigene, schmale Nachbildung von `@floating-ui/react` 0.27.20 auf Basis von **`@floating-ui/dom` 1.8.0** in `ED/components/src/floating/`: `PlEdFloatingPortal` (`div[data-floating-ui-portal]#floating-ui-<n>` an `document.body`), `PlEdFloatingOverlay` (fixe Vollfläche, `lockScroll` mit `data-floating-ui-scroll-lock` am `body`), `createFloatingMenu()` (= `useFloating` + `useClick` + `useDismiss` + `useRole` inkl. ARIA-Attributen). Bubble-Menü über `@tiptap/extension-bubble-menu` 2.26.3 + `tippy.js` 6.3.7 (wie Original). Kein `@angular/cdk/overlay` (ABG-026); die Propel-Portal-Schicht (`portal.ts`, Base-UI-Vertrag `data-base-ui-portal`) wird für Editor-Overlays **nicht** verwendet, weil das Original hier den Floating-UI-DOM-Vertrag erzeugt | Angular CDK Overlay (verboten, anderes DOM); Propel-Portal (falscher Marker); tippy für alle Menüs (Original nutzt tippy nur im Bubble-Menü) | DOM-Parität der Portale (D09 N1 „Portal-Container“); Positionierungslogik identisch, weil dieselbe Bibliothek rechnet | MIT | I2 |
| **D10-ADR-08** | Komponenten-API der Varianten | **Inputs = Props des Originals mit gleichem Namen** (`id`, `editable`, `initialValue`, `value`, `disabledExtensions`, `flaggedExtensions`, `fileHandler`, `mentionHandler`, `getEditorMetaData`, `displayConfig`, `placeholder`, …, vollständige Tabelle §3.6.2); Handler-Objekte und Rückruf-Funktionen, deren Rückgabewert der Editor nutzt, bleiben **Inputs vom Funktionstyp**; reine Benachrichtigungen werden **Outputs mit Präfix `editor`** (`editorChange`, `editorFocus`, `editorTransaction`, `editorReady`, `editorEnterKeyPress`, `editorAssetChange`), damit sie nicht mit gleichnamigen nativen DOM-Events (z. B. `change` der Task-Checkbox, das zum Host hochblubbert) kollidieren. Die Ref-API (`EditorRefApi`, `EditorTitleRefApi`) stellt jede Variante als `readonly ref: Signal<EditorRefApi \| null>` bereit (Zugriff über `viewChild`) | alle Callbacks als Outputs (Rückgabewerte von `getEditorMetaData`/`fileHandler.upload` unmöglich); Output-Namen `change`/`focus` (Kollision mit DOM-Events) | 1:1-Port der Konsumenten (Hüllen, Stores) mit minimalen Umbenennungen; Kollisionsfreiheit ist prüfbar | – | I2 |
| **D10-ADR-09** | Lebenszyklus | `EditorInstance` (Komponenten-Provider je Variante) bildet `ED0/hooks/use-editor.ts` exakt nach: Editor wird beim ersten Rendern erzeugt und **nur bei Änderung von `editable` neu aufgebaut** (Extensions werden beim Erstellen fixiert); externer `value`-Sync nur wenn `value != null`, Editor lebt und kein Upload läuft; Cursor danach `min(alte from, docSize-1)`; `assetsUploadStatus` → `updateAssetsUploadStatus`; `assetsList`-Änderung → `editorAssetChange`. `immediatelyRender`/`shouldRerenderOnTransaction` entfallen (React-spezifisch) | Neuaufbau bei jeder Input-Änderung; Signal-Forms-Anbindung (`FormValueControl`) | Exakt dieselben Re-Init-Grenzen vermeiden Cursor-Sprünge und doppelte ID-Vergabe; Formular-Anbindung bietet das Original nicht | – | I2 |
| **D10-ADR-10** | Zoneless und Change Detection | Alle Editor-Ereignisse (`transaction`, `update`, `selectionUpdate`, `focus`, `blur`, Provider-Status) werden **ausschließlich in Signale geschrieben**; `editorState(editor, selector, equal?)` ersetzt `useEditorState` (Neuberechnung bei `transaction`, Gleichheitsprüfung wie React-Variante `deepEqual`-frei per `Object.is` bzw. übergebener Funktion). NodeView-Inputs werden per `ComponentRef.setInput()` gesetzt (markiert die View für Zoneless-CD). Keine `NgZone`-Aufrufe, keine `ChangeDetectorRef.detectChanges()` außer im `AngularRenderer.updateProps` vor synchronen DOM-Messungen (Floating-UI) | zone.js-Kompatibilitätsmodus | Angular 22 ist zoneless per Default (D01); R-D08-03 verlangt Signal-Schreibweise für Drittbibliotheks-Callbacks | – | I2 |
| **D10-ADR-11** | Kollaborations-Client | `@hocuspocus/provider` 2.15.2, `yjs` 13.6.27, `y-prosemirror` 1.3.7, `y-protocols` 1.0.6, `y-indexeddb` 9.0.12 **unverändert**; **einziger** Import von `@hocuspocus/provider` in `ED/collaboration/src/collaboration-provider.factory.ts` (`CollaborationProviderFactory`, R-D08-13); `CollaborationSession` portiert `use-yjs-setup.ts` 1:1 (Stages `initial`, `connecting`, `awaiting-sync`, `synced`, `reconnecting`, `disconnected`, Max-Retries 3, Visibility/Online-Reconnect mit 1-s-Throttle, Close-Codes 4000–4003). Awareness-Token `{id, name, color}` wie Original. Live-Cursor (`collaboration-cursor`) über `@tiptap/extension-collaboration-cursor` **2.26.1** hinter dem Flag `EDITOR_FLAGS` (CE-Default wie Original: deaktiviert; Aktivierung = Entscheidung O-D08-07/FE-ED-01) | eigener WS-Client; y-websocket (nur S1-Fallback) | Browser-Client bleibt Referenzimplementierung des Protokolls (ADR-002); Kapselung macht den S1-Fallback zu einem Ein-Datei-Wechsel | MIT | I4 |
| **D10-ADR-12** | Emoji offline | Editor-Emoji (Suggestion `:`, Shortcodes, Emoticons, Unicode→Node) nutzt wie das Original die **in `@tiptap/extension-emoji` 2.26.1 gebündelten Daten** (`emojis`, `gitHubEmojis`, über `emojibase-data` **15.3.2** zur Build-Zeit im JS-Bundle; keine `fallbackImage`-URLs → keine Bildabrufe). `emojibase-data` wird per Override auf 15.3.2 gepinnt – dieselbe Version wie die Picker-Assets nach ABG-029. Der Callout-Default `data-emoji-url="https://cdn.jsdelivr.net/npm/emoji-datasource-apple/img/apple/64/1f4a1.png"` bleibt **als Attributwert unverändert** (Schema-Default, wird nie geladen, Anzeige nutzt Unicode); der Airgap-Scan erhält dafür einen begründeten Allowlist-Eintrag, der Airgap-E2E beweist „0 Requests“ | Default-URL auf lokales Asset umstellen (Schema- und HTML-Abweichung, G-SCHEMA/G-DOC rot); Emoji-Daten zur Laufzeit aus `assets/emojibase` laden (Original lädt sie nicht) | Schema-Freeze + Airgap gleichzeitig erfüllt; keine zweite Emoji-Datenversion | MIT | I2 |
| **D10-ADR-13** | Editor-CSS | `ED0/styles/*.css` (7 Dateien) **1:1** nach `ED/styles/`; Import-Position nach D09 §3.2.2 (Web und Space, nicht Admin). Tiptap-Core-CSS (`@tiptap/core` 2.27.3 `src/style.ts`) wird **statisch** als `ED/styles/tiptap-core.css` ausgeliefert und `injectCSS: false` gesetzt (kein `<style data-tiptap-style>` zur Laufzeit, CSP-fest); die Datei wird per `FE/tools/editor-port/extract-tiptap-style.mjs` aus dem gepinnten Paket erzeugt und im G-CSS als `kind: extra-css` (Abweichung `FE-ED-07`) registriert | Laufzeit-Injektion mit `injectNonce` (Nonce-Infrastruktur fehlt, Gateway setzt Hash-CSP, ABG-016) | Gleiches berechnetes Styling bei strenger CSP; die DOM-Normalisierung entfernt `<style>` ohnehin (D09 N2) | MIT | I0 (Kopie), I2 (Nutzung) |
| **D10-ADR-14** | Schema-Freeze und Goldens | Das Schema aller Varianten ist eingefroren. Nachweis über **G-SCHEMA** in sieben Varianten (`rich`, `lite`, `document`, `collaborative`, `title`, `server`, `server-document`), je Variante drei Dateien: `*.schema.json` (Nodes/Marks inkl. Attribute, Defaults, Content-Ausdrücke, Gruppen, `parseDOM`-Regeln), `*.extensions.json` (Extension-Name, Typ, Priorität in Registrierungsreihenfolge), `*.plugins.json` (PluginKey-Reihenfolge des `EditorState`). Erzeugung mit `tools/golden/generate.mjs schema` aus dem Original (Node + jsdom), Prüfung im Browser-Build per Vitest (Projekt `shared-dom`) mit demselben Serialisierer `ED/core/src/testing/schema-serializer.ts`. Änderungen nur per Schema-Änderungsverfahren §3.2.5 | nur Schema-JSON ohne Extension-/Plugin-Manifest (Prioritäten und Plugin-Reihenfolge – A12 §5.7 Nr. 6 – blieben ungeprüft); Schema-Vergleich nur serverseitig | Prioritäten (`UniqueID` 10000, `link`/`utility` 1000, Navigation 10) und Plugin-Reihenfolge bestimmen Verhalten; sie sind nur so maschinell prüfbar | – | I2 (Kern-Varianten), I4 (`collaborative`, `title`) |
| **D10-ADR-15** | Inkrement-Schnitt | Der **Rich-Text-Editor mit allen NodeViews und Menüs** und der **Document-Editor (read-only)** gehören zu **I2**, nicht zu I4, weil CE-WI-001/-005 (Beschreibung) und CE-WI-041 (Beschreibungs-Versionen) sie in I2 brauchen; I4 bringt nur Kollaboration, Titel-Editor und die Page-Hüllen. Folge: Spike **S5** muss vor I2 **vollständig** grün sein (nicht nur der „Lite-Teil“); nur das S5-Kriterium „NodeView-Rendering stabil mit Yjs“ darf bis vor I4 nachgeliefert werden | Rich-Editor erst I4 (Work-Item-Beschreibung in I2 nicht 1:1 möglich); Zwischenlösung Lite-Editor als Beschreibung (sichtbare Abweichung) | Nutzungskette und Abnehmbarkeit von I2; Präzisierung von D01 §1.3/ADR-042 („I2 (Lite), I4 (Rich/Document)“), Rückmeldung §9 | – | I2 |
| **D10-ADR-16** | Umgang mit Quirks und Bugs des Originals | Regel Z-12 (D17): optisch 1:1, **funktionale** Fehler werden korrigiert und dokumentiert. Für jeden Editor-Edge-Case E1–E31 (A12 §3.25) ist in §3.22 festgelegt: korrigieren (Abweichung `FE-ED-nn` in `FE/apps/e2e/visual/ui-deviations.yaml` bzw. bei Vertragswirkung in `tests/contracts/deviations.yaml`), beibehalten (mit Begründung) oder Zuständigkeit D07. Schema-/HTML-Quirks (E15, E16, E17, E19) werden **beibehalten**, weil ihre Korrektur Schema/HTML ändert | alle Quirks 1:1 (widerspricht Z-12); alle korrigieren (bricht Schema-Freeze) | Z-12 ist entschieden; Schema-Freeze hat Vorrang vor Komfort-Korrekturen | – | I2 |
| **D10-ADR-17** | Ort der Web-/Space-Hüllen | `WEB/components/editor/**` (Rich-, Lite-, Sticky-, Document-Hüllen, Mention-Embeds), `WEB/hooks/editor/**`, `WEB/hooks/use-editor-flagging.ts`, `use-additional-editor-mention.tsx`, `use-parse-editor-content.ts` → **`FE/libs/web/core/editor/`** (Domäne `core`, von allen Domänen importierbar); `WEB/components/pages/editor/**` → `FE/libs/web/pages/components/pages/editor/**`; `SPC/components/editor/**` → `FE/libs/space/editor/` | Hüllen in `libs/web/pages` (D01 §6.1 Kommentar) – dann müssten `work-items`, `intake`, `stickies`, `comments` die Pages-Domäne importieren (Domänen-Matrix D08) | Die Hüllen sind Querschnitt (Beschreibung, Kommentare, Stickies, GPT-Popover); `core` ist die einzige für alle Domänen erlaubte Web-Lib. Präzisierung von D01 §6.1, Rückmeldung §9 | – | I2 |
| **D10-ADR-18** | Erweiterbarkeit | Die Editor-Tokens `EDITOR_EXTENSIONS`, `EDITOR_BLOCKS`, `EDITOR_MENTION_TYPES`, `EDITOR_FLAGS` werden in **`ED/extensibility/src/tokens.ts` deklariert** (der Editor ist `scope:shared` und darf `EXT` nicht importieren) und von `EXT` (`@plane/web/extensions`) sowie `FE/libs/space/extensions` **re-exportiert**; Pakete importieren weiterhin aus `EXT` (D08 §6.1 bleibt öffentlicher Ort). CE-Defaults über `provideEditorDefaults()`, aufgerufen in `provideWebExtensions()` und `provideSpaceExtensions()`. `PAGE_PANE_EXTENSIONS` bleibt reines Web-Token in `EXT`. Zusätzliche Blöcke laufen ausschließlich über `EditorBlockDefinition` (§6.2) | Tokens nur in `EXT` (Editor könnte sie nicht lesen, Space hätte keine); Props-Durchreichen über alle Hüllen (jede Hülle müsste für D9 geändert werden) | Sheriff-Regeln (`type:ui` shared darf keine App-Libs importieren) und D16-Regel „ohne Umbau“ gleichzeitig erfüllt | – | I2 |
| **D10-ADR-19** | Texte im Editor | Editor-Texte bleiben **englisch und hart codiert** wie im Original (A12 §5.7 Nr. 10: „Press '/' for commands...“, „Untitled“, Slash-Titel, Menü-Labels, Fehlermeldungen); Texte der Hüllen (z. B. Kommentar-Platzhalter `issue.comments.placeholder`) laufen über `TranslationService` (D08) | Editor-Texte übersetzen (sichtbare Abweichung zum Original) | ADR-005 | – | I2 |
| **D10-ADR-20** | Markdown | `convertHTMLToMarkdown` bleibt im Client (`PKG/utils/src/editor/markdown-parser/*` → `FE/libs/shared/utils/src/editor/markdown-parser/*`, 1:1 nach D01 §6.2, Bibliotheken `unified`/`rehype-*`/`remark-*` in Original-Versionen); `tiptap-markdown` 0.8.10 für Paste wie Original | serverseitige Markdown-Erzeugung (Original macht es im Browser) | Parität „Copy as Markdown“ und Markdown-Export | MIT | I2 |
| **D10-ADR-21** | PDF im Web-Client | Der clientseitige PDF-Export `WEB/components/editor/pdf/*` (`@react-pdf/renderer`) wird **nicht** portiert; der Export-Dialog ruft `/live/pdf-export/` auf (D01 ADR-029). Der Editor liefert dafür nur `getDocument()`/`getMarkDown()` | Angular-PDF-Bibliothek im Browser | Ein Renderer statt zwei (A12 O3), kein React zur Laufzeit | – | I4 |
| **D10-ADR-22** | Icons im Kern | Icon-Felder in `constants/common.ts`, `menu-items.ts`, `block-menu-options.ts`, `command-items-list.ts`, `custom-image/utils.ts` werden von React-Komponenten auf **`PlIconDef`-Konstanten** (Datenobjekte, D09-ADR-07) umgestellt; gerendert wird in Komponenten über `svg[plSvgIcon]`. `lucide-react` (`Ban`, `Smile`) → generierte Konstanten aus `FE/libs/shared/icons-lucide/src/v0469` | Icon-Komponenten im Kern (Kern wäre nicht mehr framework-frei) | `PlIconDef` ist reines JSON und darf im Kern liegen; Codegen sichert identisches SVG | – | I2 |
| **D10-ADR-23** | Tests und Browser | Kern-Tests mit Vitest/jsdom (Projekt `shared-dom`), Layout-abhängige Tests (Floating-UI-Positionen, Drag-Handle-Hitbox, Tabellen-Resize, Bild-Resize, Bubble-Menü) im **Vitest-Browser-Modus** (Projekt `browser`), E2E mit Playwright – **nur Chromium** als Gate (Z-10, D17) | Firefox/WebKit-Gates | Auftraggeber-Entscheidung Z-10 | – | I2 |


---

## 3. Detaildesign

### 3.1 Bibliotheksschnitt, Verzeichnisbaum, Modulgrenzen

```text
FE/libs/shared/editor/                       # ← packages/editor (D01 §6.1)
├── VERSIONS.json                            # exakte Pins (D10-ADR-01), generiert aus dem Original-Lockfile
├── README.md                                # Port-Regeln §3.3 in Kurzform, Verweis auf dieses Dokument
├── core/src/                                # framework-frei; Tag editor:core; Alias @plane/editor/core
│   ├── public-api.ts  lib.ts  props.ts
│   ├── components/menus/{menu-items,block-menu-options}.ts   # Logik der Menüs, Icons als PlIconDef (K2)
│   ├── constants/  extensions/  helpers/  plugins/  types/   # gleiche relative Pfade wie ED0/
│   ├── hooks/editor-navigation.ts           # use-editor-navigation.ts als reine Funktionen
│   ├── helpers/dom-builder.ts               # h(tag, attrs, …children) – Ersatz jsx-dom-cjs (D08 §5)
│   ├── ui-port/ui-port.ts                   # EditorUiPort, uiNodeView(), uiRender(), EditorUiKey (D10-ADR-04)
│   ├── extensibility/block-registry.ts      # registerEditorBlocks(), getEditorBlocks(variant) (§6.2)
│   ├── extensibility/editor-block-definition.ts
│   └── testing/{schema-serializer,stub-handlers}.ts           # nur Tests/Golden
├── angular-binding/src/                     # Tag editor:binding; Alias @plane/editor/angular-binding (intern)
│   ├── public-api.ts
│   ├── editor-content.directive.ts          # [plEdEditorContent] – hängt editor.view.dom ein (EditorContent)
│   ├── angular-renderer.ts                  # AngularRenderer (ReactRenderer-Ersatz)
│   ├── angular-node-view-renderer.ts        # AngularNodeView, AngularNodeViewRenderer()
│   ├── node-view-wrapper.directive.ts       # [plEdNodeViewWrapper] (NodeViewWrapper-Ersatz)
│   ├── node-view-content.directive.ts       # [plEdNodeViewContent] (NodeViewContent-Ersatz)
│   ├── node-view-drag-handle.directive.ts   # [plEdNodeViewDragHandle] (data-drag-handle)
│   ├── bubble-menu.directive.ts             # [plEdBubbleMenu] (BubbleMenu-Ersatz, tippy)
│   ├── editor-state.ts                      # editorState() (useEditorState-Ersatz)
│   └── ui-port.extension.ts                 # PlaneUiPortExtension + AngularUiPort
├── components/src/                          # Tag editor:ui; Alias @plane/editor
│   ├── public-api.ts                        # Varianten, Typen, Konstanten (Re-Exports aus core)
│   ├── components/editors/**                # PlEdRichTextEditor, PlEdLiteTextEditor, PlEdDocumentEditor, PlEdCollaborativeDocumentEditor, …
│   ├── components/menus/**  components/links/**  components/document-editor-side-effects.component.ts
│   ├── extensions/**/<name>.component.ts    # NodeViews, Dropdowns, Tabellen-Handles (gleiche Pfade wie ED0/)
│   ├── floating/{floating-portal,floating-overlay,floating-menu}.ts   # D10-ADR-07
│   ├── services/{editor-instance,collaborative-editor-instance,title-editor-instance,file-upload}.ts
│   ├── ui-port/ui-component-map.ts          # EditorUiKey → Komponente (CE-Tabelle §3.4.2)
│   └── provide-editor-ui.ts                 # provideEditorUi() – registriert Map + Block-Komponenten
├── collaboration/src/                       # Tag editor:collab; Alias @plane/editor/collaboration
│   ├── public-api.ts
│   ├── collaboration-provider.factory.ts    # einziger Import von @hocuspocus/provider (R-D08-13)
│   ├── collaboration-session.ts             # use-yjs-setup.ts 1:1 (Signals)
│   └── collaboration-context.ts             # COLLABORATION_SESSION-Token, provideCollaborationSession()
├── extensibility/src/                       # Tag editor:extensibility; Alias @plane/editor/extensibility
│   ├── public-api.ts  tokens.ts             # EDITOR_EXTENSIONS, EDITOR_BLOCKS, EDITOR_MENTION_TYPES, EDITOR_FLAGS
│   └── provide-editor-defaults.ts           # CE-Defaults + Initializer für die Block-Registry
└── styles/                                  # 1:1 aus ED0/styles + tiptap-core.css (D10-ADR-13)
    └── index.css  variables.css  editor.css  table.css  github-dark.css  drag-drop.css  title-editor.css  tiptap-core.css
```

**Werkzeuge (nur Dev, nicht im Build):**

```text
FE/tools/editor-port/
├── port-core.mjs               # Codemod ED0/** → ED/core/src/** (Regeln §3.3), schreibt ported-from-Header
├── check-core-drift.mjs        # G-EDCORE: K1-Dateien normalisiert = Original; PORT-DIFF-Marker zählen
├── check-versions.mjs          # G-EDPIN: frontend/pnpm-lock.yaml ↔ ED/VERSIONS.json
├── extract-tiptap-style.mjs    # @tiptap/core/src/style.ts → ED/styles/tiptap-core.css
└── capture-nodeview-dom.ts     # Playwright gegen das Original: DOM-Goldens der NodeViews/Menüs (S5, §7.3)
```

**Modulgrenzen (Ergänzung zu D08 §3.1.5, Sheriff):**

| Tag | Lib | darf importieren | zusätzlich verboten (ESLint `no-restricted-imports`) |
|---|---|---|---|
| `editor:core` | `ED/core` | `type:types`, `type:constants`, `type:utils` (`@plane/types`, `@plane/constants`, `@plane/utils`), `@plane/propel/icons` (nur `PlIconDef`-Konstanten), `@plane/icons-lucide`, npm: `@tiptap/*` (außer `react`), `prosemirror-*`, `yjs`, `y-prosemirror`, `y-protocols`, `lowlight`, `highlight.js`, `linkifyjs`, `tiptap-markdown`, `emoji-regex`, `is-emoji-supported`, `@floating-ui/dom`, `tippy.js`, `uuid`, `@hocuspocus/provider` **nur als `import type`** | `@angular/*`, `rxjs`, `react`, `react-dom`, `@tiptap/react`, `@floating-ui/react`, `lucide-react`, `jsx-dom-cjs`, `@plane/editor` (Zyklus) |
| `editor:binding` | `ED/angular-binding` | `editor:core`, `@angular/core`, `@angular/common` | `@hocuspocus/provider`, `@plane/propel/components/*` |
| `editor:ui` | `ED/components` | `editor:core`, `editor:binding`, `editor:extensibility`, `type:ui` in Richtung `cdk ← propel ← blocks ← editor` (D08), `type:data` (`i18n`, `state-kit`) | `@hocuspocus/provider` (nur über `editor:collab`) |
| `editor:collab` | `ED/collaboration` | `editor:core`, `editor:ui`, `@hocuspocus/provider`, `y-indexeddb`, `yjs` | – |
| `editor:extensibility` | `ED/extensibility` | `editor:core`, `@angular/core` | `editor:ui`, `editor:collab` |

Alle vier Teil-Libs tragen zusätzlich `scope:shared`, `type:ui` (D08 §3.1.3). Konsumenten außerhalb von `ED/` importieren nur `@plane/editor`, `@plane/editor/collaboration`, `@plane/editor/extensibility` und (für Konverter/Typen) `@plane/editor/core`.

### 3.2 Versionen, Schema-Freeze, Golden-Vertrag

#### 3.2.1 Exakte Pins (`ED/VERSIONS.json`, Quelle: `pnpm-lock.yaml` des Originals, Importer `packages/editor`)

| Paket | Version | Rolle | Lizenz |
|---|---|---|---|
| `@tiptap/core` | 2.27.3 | Editor-Kern | MIT |
| `@tiptap/pm` | 2.26.1 | ProseMirror-Bündel | MIT |
| `@tiptap/starter-kit` | 2.26.1 | Basis-Nodes/Marks | MIT |
| `@tiptap/extension-{blockquote,character-count,collaboration,document,emoji,heading,image,list-item,mention,placeholder,task-item,task-list,text,text-align,text-style,underline,history}` | 2.26.1 | Extensions (Catalog des Originals) | MIT |
| `@tiptap/extension-{bold,italic,strike,code,code-block,paragraph,hard-break,horizontal-rule,bullet-list,ordered-list,dropcursor,gapcursor}` | 2.26.2 | transitiv über StarterKit (per `overrides` erzwungen) | MIT |
| `@tiptap/html` | 2.26.2 | `generateHTML`/`generateJSON` (Konverter im Client, Golden-Werkzeug) | MIT |
| `@tiptap/suggestion` | 2.26.1 | Slash/Mention/Emoji | MIT |
| `@tiptap/extension-bubble-menu` | 2.26.3 | Bubble-Menü (im Original transitiv über `@tiptap/react` 2.26.1) | MIT |
| `@tiptap/extension-collaboration-cursor` | 2.26.1 | **neu**, nur hinter Flag `collaboration-cursor` (D10-ADR-11; Peer `y-prosemirror ^1.2.11`, geprüft 23.10.2026) | MIT |
| `prosemirror-view` / `prosemirror-model` | 1.42.6 / 1.25.12 | Overrides wie Original (`pnpm-workspace.yaml`, eine Kopie im Graphen) | MIT |
| `prosemirror-state`, `-transform`, `-tables`, `-keymap`, `-inputrules`, `-commands`, `-history`, `-dropcursor`, `-gapcursor`, `-markdown` | 1.4.3, 1.10.4, 1.7.1, 1.2.3, 1.5.0, 1.7.1, 1.4.1, 1.8.2, 1.3.2, 1.13.2 | transitiv (Lockfile-Stand) | MIT |
| `prosemirror-codemark` | 0.4.2 | Inline-Code-Cursor | MIT |
| `yjs` / `y-prosemirror` / `y-protocols` / `y-indexeddb` / `lib0` | 13.6.27 / 1.3.7 / 1.0.6 / 9.0.12 / 0.2.114 | CRDT, Binding, Offline | MIT |
| `@hocuspocus/provider` / `@hocuspocus/common` | 2.15.2 / 2.15.3 | WS-Client (unverändert) | MIT |
| `lowlight` / `highlight.js` | 3.3.0 / 11.11.1 | Syntax-Highlighting (`common` + `ts`) | MIT / BSD-3-Clause |
| `linkifyjs` (+ Override `linkify-it` 5.0.2, `markdown-it` 14.3.2) | 4.3.2 | Autolink | MIT |
| `tiptap-markdown` | 0.8.10 | Markdown-Paste | MIT |
| `emoji-regex` / `is-emoji-supported` / `emojibase-data` | 10.5.0 / 0.0.5 / 15.3.2 | Emoji (Daten im Bundle, ABG-029) | MIT |
| `tippy.js` | 6.3.7 | Bubble-Menü-Positionierung | MIT |
| `@floating-ui/dom` | 1.8.0 | Popover/Dropdown-Positionierung | MIT |
| `uuid` | 14.0.0 | IDs | MIT |

**Entfällt:** `@tiptap/react`, `@floating-ui/react`, `lucide-react`, `jsx-dom-cjs`, `react`, `react-dom`, `@react-pdf/renderer`, `react-pdf-html` (A12 §1.2; Ersatz D10-ADR-05/-07/-21/-22).

**Durchsetzung:** (a) `frontend/pnpm-workspace.yaml` Catalog mit den exakten Versionen (ohne `^`) und `overrides` für alle transitiven Tiptap-/ProseMirror-Pakete; (b) Renovate-Regel `packageRules: [{ matchPackagePatterns: ["^@tiptap/", "^prosemirror-", "^y-", "^yjs$", "^@hocuspocus/", "^lowlight$", "^highlight.js$", "^emojibase-data$", "^tiptap-markdown$"], enabled: false }]`; (c) CI-Gate **G-EDPIN** (`check-versions.mjs`): jede im `frontend/pnpm-lock.yaml` aufgelöste Version dieser Pakete muss genau einmal vorkommen und `VERSIONS.json` entsprechen.

#### 3.2.2 Schema-Freeze

Eingefroren sind für jede Variante (§3.2.3): Menge, Reihenfolge und Konfiguration der Extensions; Namen, Gruppen, Content-Ausdrücke, Attribute inkl. Defaults und `parseDOM`-Regeln aller Nodes/Marks; Prioritäten; Reihenfolge der ProseMirror-Plugins; Yjs-Feldnamen `default` (Inhalt) und `title` (Titel). Erlaubt ohne Verfahren sind Änderungen, die keines davon berühren (NodeView-Interna, Menü-Komponenten).

#### 3.2.3 Varianten der Schema-Goldens (G-SCHEMA, Ergänzung zu D15 §3.7.1)

| Variante | Extension-Liste (Original) | Erzeugungsargumente im Generator | Golden-Dateien (`tests/Plane.Documents.Tests/Golden/schema/`) | Prüfer Browser (Vitest) | Prüfer Server (D07) |
|---|---|---|---|---|---|
| `rich` | `CoreEditorExtensions` + `SideMenuExtension({aiEnabled:false, dragDropEnabled})` + `RichTextEditorAdditionalExtensions` (Slash); `dragDropEnabled` wie von der Web-Hülle `WEB/components/editor/rich-text/editor.tsx` übergeben | `disabledExtensions: ["ai","collaboration-cursor"]`, `flaggedExtensions: []`, `editable: true`, `enableHistory: true`, `provider: undefined`, Stub-Handler | `rich.schema.json`, `rich.extensions.json`, `rich.plugins.json` | `ED/core/src/testing/schema-golden.spec.ts` | – |
| `lite` | `CoreEditorExtensions` + `EnterKeyExtension` | wie oben | `lite.*.json` | dto. | – |
| `document` | `CoreEditorExtensions` + `SideMenuExtension({aiEnabled:false, dragDropEnabled:true})` + `HeadingListExtension` + `DocumentEditorAdditionalExtensions` | wie oben | `document.*.json` | dto. | – |
| `collaborative` | wie `document` + `Collaboration({field:"default"})` + `mainEditorNavigation`, `enableHistory: false` | mit leerem `Y.Doc`, Fake-Provider (Objekt mit `document`, ohne Netz) | `collaborative.*.json` | dto. (I4) | – |
| `title` | `TitleExtensions` + `Collaboration({field:"title"})` + `titleEditorNavigation` + `Placeholder("Untitled")` | dto. | `title.*.json` | dto. (I4) | – |
| `server` | `CoreEditorExtensionsWithoutProps` | – | `server.schema.json` | dto. | `Plane.Documents.Tests` (D07, ADR-031) |
| `server-document` | `CoreEditorExtensionsWithoutProps` + `DocumentEditorExtensionsWithoutProps` | – | `server-document.schema.json` | dto. | dto. |

Die Varianten `collaborative`, `title`, `server-document` ergänzen die vier/fünf Varianten aus D15 §3.7.1 (Rückmeldung §9). Serialisierung: §5.9.

#### 3.2.4 Generator-Unterbefehl `tools/golden/generate.mjs schema` (Eigentümer Werkzeug D15, Inhalt D10)

1. Läuft im Original-Repo-Checkout (Node 22, `pnpm install`), importiert `packages/editor/src/**` per `tsx` (ESM) mit `jsdom`-Global; React wird geladen, aber keine NodeView instanziiert (leeres Dokument).
2. Baut je Variante einen Editor `new Editor({ extensions, content: "<p></p>", editable: true, injectCSS: false })`, serialisiert `editor.schema`, `editor.extensionManager.extensions` und `editor.state.plugins` mit `ED/core/src/testing/schema-serializer.ts` (dieselbe Datei wird in den Generator kopiert; Byte-Gleichheit beider Kopien prüft `check-core-drift.mjs`).
3. Schreibt die Dateien sortiert nach Registrierungsreihenfolge (keine Neusortierung), UTF-8, `\n`, 2 Leerzeichen.

#### 3.2.5 Schema-Änderungsverfahren (für CE-Nodes nur mit Auftraggeber-Freigabe; für Paket-Blöcke Standard)

| Schritt | Artefakt | Prüfung |
|---|---|---|
| 1 | Begründung als Eintrag `SCHEMA-nnn` in `ED/SCHEMA-CHANGES.md` (Node/Mark, Attribut, Variante, Motivation, Wirkung auf gespeicherte Dokumente) | Review Editor-CODEOWNER + D07-CODEOWNER |
| 2 | Client: Extension (Kern) bzw. `EditorBlockDefinition` (Paket) | Vitest G-SCHEMA rot → neue Golden-Datei |
| 3 | Server: `IDocumentNodeSpec`/`IDocumentMarkSpec` in `Plane.Documents` (E-11) | `Plane.Documents.Tests` G-SCHEMA `server*` |
| 4 | Sanitizer-Allowlist (D05 §3.17.3) für neue Tags/Attribute | `HtmlSanitizerParityTests` + `allowed-diffs.json` |
| 5 | G-DOC: ≥ 3 Fälle je neuem Node/Mark (minimal, alle Attribute, verschachtelt) | `Plane.Documents.Tests` |
| 6 | PDF-Renderer (D07) und Markdown-Handler (`custom-components-handler.ts`) | G-PDF, Markdown-Spec |
| 7 | Bei CE-Nodes: Abweichungseintrag in `tests/contracts/deviations.yaml` (Vertragswirkung auf `description_html`/`description_json`) | Contract-Gate |

### 3.3 Port-Regeln für den Kern (Codemod `port-core.mjs`)

| Regel | Original | Ziel | Kategorie |
|---|---|---|---|
| R-ED-1 Pfad | `ED0/<pfad>.tsx` / `.ts` | `ED/core/src/<pfad>.ts` (JSX-freie `.tsx` werden `.ts`) | K1 |
| R-ED-2 Pfad-Alias | `@/…` (tsconfig `paths` im Paket) | relative Importe innerhalb `ED/core/src` (Alias `@/` wird im Codemod aufgelöst, damit kein App-Alias kollidiert) | K1 |
| R-ED-3 Plane-Pakete | `@plane/types`, `@plane/constants`, `@plane/utils`, `@plane/hooks` | gleiche Namen (Aliase D08 §3.1.3); `@plane/hooks` → `@plane/cdk` | K1 |
| R-ED-4 Propel-Icons | `import { XOutline } from "@makeplane/propel/icons"` (React-Komponenten) | `import { XOutline } from "@plane/propel/icons"` (`PlIconDef`-Konstanten gleichen Namens, D09-ADR-07); Felder `icon: ComponentType<SVGProps>` → `icon: PlIconDef` | K2 |
| R-ED-5 Lucide | `lucide-react` (`Ban`, `Smile`) | `@plane/icons-lucide` (`v0469`, lucide 0.469.0) | K2 |
| R-ED-6 Blocks-Icons | `@plane/blocks/icons` (`SansSerifIcon`, `SerifIcon`, `MonospaceIcon`, Typ `ISvgIcons`) | `PlIconDef`-Konstanten aus `@plane/blocks/icons` (D09 Hand-Ports) | K2 |
| R-ED-7 React-Typen | `ReactNode`, `ComponentType`, `MutableRefObject<T>`, `CSSProperties`, `React.MouseEvent` | `TEditorRenderable` (§5.2), `PlIconDef`, `{ current: T }` (`TMutableRef<T>`), `Partial<CSSStyleDeclaration>`, `MouseEvent` | K2 |
| R-ED-8 `@tiptap/react`-Typen | `import type { Editor, NodeViewProps, Predicate } from "@tiptap/react"`; Re-Exporte (`findParentNodeClosestToPos`) | `@tiptap/core` (identische Typen/Funktionen, `@tiptap/react` re-exportiert Core) | K2 |
| R-ED-9 NodeView-Fabrik | `addNodeView() { return ReactNodeViewRenderer(Comp, opts) }` | `addNodeView() { return uiNodeView("<key>", opts) }` (§3.4) | NV |
| R-ED-10 Renderer | `new ReactRenderer(Comp, { props, editor })` | `uiRender(editor, "<key>", props)` liefert `EditorUiHandle` mit denselben Feldern (`element`, `ref`, `updateProps`, `destroy`) | NV |
| R-ED-11 JSX-DOM | `h()` aus `jsx-dom-cjs` in `table-view.tsx` | `h()` aus `helpers/dom-builder.ts` (identische Attribut-/Kind-Semantik) | K2 |
| R-ED-12 Modul-Konstanten mit Paket-Beiträgen | `ADDITIONAL_BLOCK_NODE_TYPES`, `ADDITIONAL_ASSETS_META_DATA_RECORD`, `COMBINED_BLOCK_NODE_TYPES` (Modul-Ebene) | Getter `getAdditionalBlockNodeTypes()` usw. über die Block-Registry (§6.2), CE-Ergebnis identisch (`[]`/`{}`) | K1 + `PORT-DIFF(block-registry)` |
| R-ED-13 Header | – | `// ported-from: packages/editor/src/<pfad> @ <commit-sha>` + Lizenz-Header des Originals unverändert (AGPL-3.0-only, Copyright Plane Software) | alle |
| R-ED-14 Verbotenes | – | Keine Umformatierung, keine Umbenennung, keine „Verbesserung“; Formatter (oxfmt/Prettier) für `ED/core/src/**` deaktiviert (`.prettierignore`), damit G-EDCORE byte-nah vergleicht | alle |

### 3.4 UI-Port (D10-ADR-04)

#### 3.4.1 Prinzip

`ED/core/src/ui-port/ui-port.ts` definiert die Schnittstelle `EditorUiPort` mit zwei Operationen: `createNodeView(key, options)` (liefert eine Tiptap-`NodeViewRenderer`-Funktion) und `render(key, props, editor)` (liefert `EditorUiHandle`). Die Angular-Schicht stellt die Implementierung `AngularUiPort` bereit und hängt sie über die Extension `PlaneUiPortExtension` in `editor.storage.planeUiPort` ein; jede Variante fügt diese Extension **als letzte** an (nach `props.extensions`), damit die Extension-Reihenfolge der Original-Extensions unverändert bleibt. Die Extension erzeugt **kein** Plugin und keine Schema-Teile; im Golden-Manifest (`*.extensions.json`) wird sie vom Serialisierer ausgefiltert (Name `planeUiPort` steht auf der Ausschlussliste des Serialisierers).

#### 3.4.2 Schlüsseltabelle der CE (`ED/components/src/ui-port/ui-component-map.ts`)

| `EditorUiKey` | Art | Aufrufer (Kern) | Angular-Komponente | Optionen (wie Original) |
|---|---|---|---|---|
| `callout-block` | NodeView | `extensions/callout/extension.ts` | `PlEdCalloutBlock` | – |
| `code-block` | NodeView | `extensions/code/index.ts` | `PlEdCodeBlockNodeView` | – |
| `custom-image` | NodeView | `extensions/custom-image/extension.ts`, `extensions/image/extension.ts` | `PlEdCustomImageNodeView` | – |
| `mention` | NodeView | `extensions/mentions/extension.ts` | `PlEdMentionNodeView` | Inline (`span`) |
| `slash-commands-menu` | Renderer | `extensions/slash-commands/root.ts` | `PlEdSlashCommandsMenu` | `ref` = `CommandListInstance` (`onKeyDown`) |
| `mentions-list-dropdown` | Renderer | `extensions/mentions/utils.ts` | `PlEdMentionsListDropdown` | dto. |
| `emojis-list-dropdown` | Renderer | `extensions/emoji/suggestion.ts` | `PlEdEmojisListDropdown` | dto. |
| `table-column-drag-handle` | Renderer (Widget-Decoration) | `extensions/table/plugins/drag-handles/column/plugin.ts` | `PlEdTableColumnDragHandle` | – |
| `table-row-drag-handle` | Renderer (Widget-Decoration) | `extensions/table/plugins/drag-handles/row/plugin.ts` | `PlEdTableRowDragHandle` | – |

Weitere Schlüssel (Pakete) registrieren Blöcke über `EditorBlockDefinition.ui` (§6.2); Schlüssel tragen dann das Präfix `<paket>:` (z. B. `d9:drawio`), Kollisionen mit CE-Schlüsseln wirft `provideEditorUi()` beim Start.

#### 3.4.3 Verhalten ohne Port

Ohne registrierten Port (Node-Golden-Generator in der Zielvariante, Schema-Tests, künftige Web-Worker) liefert `uiNodeView` `undefined` (Tiptap nutzt dann `renderHTML`/`toDOM`) und `uiRender` `null`; Suggestion-`onStart` beendet sich still (das Menü erscheint nicht). Die Schema-Goldens sind dadurch unabhängig von Angular.

### 3.5 Angular-Bindung (`ED/angular-binding`)

#### 3.5.1 DOM-Vertrag (Referenz: `@tiptap/react` 2.26.1, verifiziert in S5 mit `capture-nodeview-dom.ts`)

| Baustein | DOM im Original | Angular-Nachbildung |
|---|---|---|
| `EditorContent` | `<div>` (mit durchgereichten Props, z. B. `id`), darin `editor.view.dom` (`div.ProseMirror` mit `CoreEditorProps.attributes.class` und den von ProseMirror/Tiptap gesetzten Attributen) | `div[plEdEditorContent]` hängt `editor.view.dom` per `appendChild` ein, setzt `editor.options.element`, entfernt beim Zerstören |
| NodeView-Außenelement | `div` (Block) bzw. `span` (Inline) mit Klassen `react-renderer node-<typ>` (+ `className`-Option) | `AngularNodeView` erzeugt dasselbe Element mit denselben Klassen (Klassenname `react-renderer` bleibt bewusst – CSS und DOM-Parität) |
| `NodeViewWrapper` | Element (`as`, Default `div`) mit `data-node-view-wrapper=""`, `style="white-space: normal;"` + Props; `onDragStart` → `nodeViewContext.onDragStart` | Host-Element der NodeView-Komponente (`hostElement`), Attribute/Style per `[plEdNodeViewWrapper]`-Logik in `AngularNodeView.mount()`; `dragstart`-Listener ruft `onDragStart` |
| `NodeViewContent` | Element (`as`, Default `div`) mit `data-node-view-content=""`, `style="white-space: pre-wrap;"`; darin das `contentDOM` | `[plEdNodeViewContent]`-Direktive (Attribut `as` entfällt – das Element im Template bestimmt den Tag); verschiebt `contentDOM` hinein |
| `contentDOM` | `div`/`span` mit `data-node-view-content-react=""` ⚠ und `style="white-space: inherit;"` | identisch erzeugt; ⚠ Attributname im S5-DOM-Golden bestätigen |
| Drag-Handle in NodeView | Element mit `data-drag-handle` | `[plEdNodeViewDragHandle]` setzt `data-drag-handle=""` |
| Selektion | Prop `selected` (bei NodeSelection), Klasse `ProseMirror-selectednode` am Außenelement durch ProseMirror | Input `selected` (Signal); Klasse wie Original von ProseMirror gesetzt |
| `ReactRenderer` (Popups/Widgets) | `div.react-renderer` (+ `className`), Inhalt = Komponente; Element wird vom Aufrufer platziert (`document.body` bzw. Widget-Decoration) | `AngularRenderer` erzeugt `div.react-renderer` als `hostElement`, Komponente mit Attribut-Selektor; `updateProps()` → `setInput()` je Feld |
| `BubbleMenu` | `<div style="visibility: hidden">` + `className`, tippy verschiebt es in `div[data-tippy-root] > div.tippy-box > div.tippy-content` | `div[plEdBubbleMenu]` registriert `BubbleMenuPlugin` mit `element` = Host, `pluginKey`, `shouldShow`, `tippyOptions` (Werte A12 §2.11) |

#### 3.5.2 Ereignisse und Lebenszyklus der `AngularNodeView`

| Phase | Tiptap-Hook | Verhalten |
|---|---|---|
| Erzeugen | `mount()` | Außenelement + Wrapper-Host erzeugen; `createComponent(component, { environmentInjector, elementInjector, hostElement: wrapper })`; Inputs `editor`, `node`, `decorations`, `innerDecorations`, `view`, `selected=false`, `extension`, `HTMLAttributes`, `getPos`, `updateAttributes`, `deleteNode` setzen; `appRef.attachView(ref.hostView)`; `contentDOM` vorbereiten (nicht bei Leaf-Nodes) |
| `dom` / `contentDOM` | Getter | Außenelement bzw. `contentDOM` (nur, wenn die Komponente ein `[plEdNodeViewContent]` besitzt; sonst `null`, wie React bei fehlendem `NodeViewContent`) |
| Aktualisieren | `update(node, decorations, innerDecorations)` | wie `ReactNodeView.update`: falscher Typ → `false`; `options.update`-Callback falls gesetzt; sonst Inputs neu setzen, `true` |
| Selektion | `selectNode()`/`deselectNode()` | Input `selected` setzen, Klasse wie Original |
| Events | `stopEvent`, `ignoreMutation` | geerbt aus `NodeView` (`@tiptap/core`) – identische Semantik zu React (gleiche Basisklasse) |
| Zerstören | `destroy()` | `appRef.detachView`, `ref.destroy()`, Listener (`selectionUpdate`) abmelden |

#### 3.5.3 `editorState()`

`editorState<T>(editor: Signal<Editor | null>, selector: (ctx: { editor: Editor }) => T, equal?: (a: T, b: T) => boolean): Signal<T>` – registriert `editor.on("transaction", …)` und schreibt das Ergebnis in ein `signal` (mit `equal`, Default `Object.is`); Abmeldung über `DestroyRef`. Ersetzt jede Nutzung von `useEditorState` (Bubble-Menü-Aktivzustände, Upload-Status, Assetliste in `EditorInstance`).

### 3.6 Varianten und Komponenten-API

#### 3.6.1 Komponenten und DOM-Wurzel

| Variante (Original-Export) | Angular-Klasse, Selektor | DOM-Wurzel | zusätzliche Extensions (A12 §1.3) | Menüs | History |
|---|---|---|---|---|---|
| `RichTextEditorWithRef` | `PlEdRichTextEditor`, `pl-ed-rich-text-editor` (`display:contents`, `data-pl-host`) | `div#editor-container-{id}.editor-container…` (über `PlEdEditorWrapper` → `div[plEdEditorContainer]`) | `SideMenuExtension({aiEnabled:false, dragDropEnabled})`, `RichTextEditorAdditionalExtensions` | Bubble (Default an), Block-Menü (immer gerendert) | Tiptap |
| `LiteTextEditorWithRef` | `PlEdLiteTextEditor`, `pl-ed-lite-text-editor` | dto. | `EnterKeyExtension(onEnterKeyPress)` sofern nicht `"enter-key"` deaktiviert | keine | Tiptap |
| `DocumentEditorWithRef` | `PlEdDocumentEditor`, `pl-ed-document-editor` | `div[plEdPageRenderer].frame-renderer…` | `SideMenuExtension({aiEnabled: !disabled.includes("ai"), dragDropEnabled:true})`, `HeadingListExtension`, `DocumentEditorAdditionalExtensions` | Block-Menü nur editierbar & nicht Touch; kein Bubble | Tiptap |
| `CollaborativeDocumentEditorWithRef` | `PlEdCollaborativeDocumentEditor`, `pl-ed-collaborative-document-editor` | `PlEdPageRenderer` mit Titel-Editor (`PlEdTitleEditor`) + Haupt-Editor | wie Document + `Collaboration(field:"default")` + `mainEditorNavigation`; Titel: `TitleExtensions` + `Collaboration(field:"title")` + `titleEditorNavigation` + `Placeholder("Untitled")` | Bubble + Block-Menü (editierbar, nicht Touch) | y-undo |

Interne Bausteine: `PlEdEditorWrapper` (`pl-ed-editor-wrapper`), `PlEdEditorContainer` (`div[plEdEditorContainer]`, Klick-/Deep-Link-/Mouseleave-Logik A12 §1.4, §3.12, §3.13), `PlEdEditorContentWrapper` (`div[plEdEditorContentWrapper]`, `tabindex`, Fokus-Weiterleitung), `PlEdPageRenderer`, `PlEdDocumentContentLoader` (Skeleton-Maße A12 §1.4), `PlEdLinkContainer`/`PlEdLinkViewContainer`, `PlEdDocumentEditorSideEffects` (CE leer).

#### 3.6.2 Props → Inputs/Outputs (gilt für alle Varianten, soweit das Original die Prop für die Variante kennt)

| Prop (`IEditorProps`, A12 §2.2) | Angular | Typ (Ziel) | Hinweis |
|---|---|---|---|
| `id` | `input.required<string>()` | `string` | Y-Dokumentname bei Collab; Komponente wird bei `id`-Wechsel per `@for … track id` bzw. `@if` neu erzeugt (Original `key={props.id}`) |
| `editable` | `input.required<boolean>()` | `boolean` | Neuaufbau des Editors bei Änderung (D10-ADR-09) |
| `initialValue` | `input.required<string>()` (Rich/Lite) | `string` | nur beim Erzeugen gelesen |
| `value` | `input<string \| null>()` | `string \| null` | externer Sync (§3.7) |
| `autofocus` | `input<boolean>(false)` | | |
| `bubbleMenuEnabled` | `input<boolean>()` | | Default je Variante |
| `containerClassName`, `editorClassName` | `input<string>()` | | |
| `displayConfig` | `input<TDisplayConfig>(DEFAULT_DISPLAY_CONFIG)` | | |
| `disabledExtensions`, `flaggedExtensions` | `input.required<TExtensions[]>()` | | `flaggedExtensions` immer `[]` (ADR-001) |
| `editorProps` | `input<EditorProps>()` | ProseMirror `EditorProps` | Spread nach `CoreEditorProps` |
| `extensions` | `input<Extensions>([])` | | Konsumenten-Extensions (nach Varianten-Extensions) |
| `fileHandler` | `input.required<TFileHandler>()` | | §3.14 |
| `getEditorMetaData` | `input.required<(html: string) => TCustomComponentsMetaData>()` | | Markdown |
| `mentionHandler` | `input.required<TMentionHandler>()` | | §3.11 |
| `placeholder` | `input<string \| ((isFocused: boolean, value: string) => string)>()` | | |
| `showPlaceholderOnEmpty` | `input<boolean>(false)` | | |
| `tabIndex` | `input<number>()` | | beeinflusst `ListKeymap` |
| `isTouchDevice` | `input<boolean>(false)` | | |
| `extendedEditorProps` | `input.required<IEditorPropsExtended>()` | `unknown` (S48, 1:1) | Paket-Andockpunkt (V) |
| `workItemIdentifier` | `input<string \| null>()` | | an `PlEdBlockMenu` (CE ungenutzt) |
| `dragDropEnabled` (Rich, Collab) | `input<boolean>()` | | Collab-Default `true` |
| `forwardedRef` | entfällt → `ref: Signal<EditorRefApi \| null>` | | §3.8 |
| `handleEditorReady(ready)` | `editorReady = output<boolean>()` | | `true` bei `create`, `false` bei `destroy` |
| `onChange(json, html, {isMigrationUpdate})` | `editorChange = output<TEditorChangeEvent>()` | `{ json: JSONContent; html: string; isMigrationUpdate: boolean }` | `isMigrationUpdate = tr.getMeta("uniqueIdOnlyChange") === true` |
| `onEditorFocus()` | `editorFocus = output<void>()` | | |
| `onTransaction()` | `editorTransaction = output<void>()` | | |
| `onEnterKeyPress(e?)` (Lite) | `editorEnterKeyPress = output<KeyboardEvent \| undefined>()` | | nur wenn keine Dropbar offen |
| `onAssetChange(assets)` | `editorAssetChange = output<TEditorAsset[]>()` | | |
| Collab: `realtimeConfig`, `serverHandler`, `user` | `input.required<TRealtimeConfig>()`, `input<TServerHandler>()`, `input.required<TUserDetails>()` | | `serverHandler.onStateChange` bleibt Funktions-Input (Rückruf mit Stage) |
| Collab: `aiHandler`, `documentLoaderClassName`, `titleRef`, `updatePageProperties`, `isFetchingFallbackBinary`, `pageRestorationInProgress`, `extendedDocumentEditorProps` | Inputs gleichen Namens; `titleRef` → `titleRefApi: Signal<EditorTitleRefApi \| null>` | | `aiHandler` wird wie im Original angenommen, aber nicht gerendert |
| Document: `value: Content`, `user?` | `input.required<Content>()`, `input<TUserDetails>()` | | `value` dient als `initialValue` |

### 3.7 Lebenszyklus (`EditorInstance`, Port von `use-editor.ts`)

1. **Erzeugen** im `afterNextRender` der Variante (DOM vorhanden): `new Editor({ editable, autofocus, parseOptions: { preserveWhitespace: true }, injectCSS: false, editorProps: { ...CoreEditorProps({ editorClassName }), ...editorProps }, extensions: [...CoreEditorExtensions(args), ...extensions, PlaneUiPortExtension.configure({ port })], content: initialValue, onCreate, onDestroy, onFocus, onTransaction, onUpdate })`. Reihenfolge exakt wie Original: Core-Extensions zuerst, dann die von der Variante gebildete Liste `extensions` (Rich: `[...externalExtensions, SideMenuExtension(...), ...RichTextEditorAdditionalExtensions(...)]`, Lite: `[...externalExtensions, EnterKeyExtension]`, Document analog `ED0/components/editors/document/editor.tsx`), zuletzt `PlaneUiPortExtension` (§3.4.1).
2. **Neuaufbau** ausschließlich, wenn sich `editable()` ändert (`effect` vergleicht vorherigen Wert); alter Editor `destroy()`, neuer Editor mit aktuellem Inhalt (`getJSON()` des alten ist **nicht** Teil des Originals – das Original erzeugt mit `initialValue` neu und synchronisiert über `value`; genauso hier).
3. **`value`-Sync** (`effect` auf `value`, `editor`, `id`): wenn `value != null`, Editor nicht zerstört und `!editor.storage.utility.uploadInProgress` → `editor.commands.setContent(value, false, { preserveWhitespace: true })`, danach Cursor auf `min(alteFrom, doc.content.size - 1)`.
4. **Upload-Status**: `effect` auf `fileHandler().assetsUploadStatus` → `editor.commands.updateAssetsUploadStatus(status)`.
5. **Assetliste**: `editorState(editor, ({editor}) => editor.storage.utility.assetsList)` → bei Änderung `editorAssetChange.emit`.
6. **Ref-API**: `ref.set(getEditorRefHelpers({ editor, getEditorMetaData, provider }))` nach `onCreate`, `null` nach `onDestroy`.
7. **Zerstören** über `DestroyRef`: `editor.destroy()`, alle Listener abmelden.

### 3.8 `EditorRefApi` und Titel-Ref

Die Implementierung `getEditorRefHelpers()` (`ED/core/src/helpers/editor-ref.ts`) wird 1:1 übernommen; alle Methoden aus A12 §2.4 (`blur`, `clearEditor`, `createSelectionAtCursorPosition`, `getDocument`, `getDocumentInfo`, `getHeadings`, `getMarkDown`, `copyMarkdownToClipboard`, `getSelectedText`, `insertText`, `isAnyDropbarOpen`, `isEditorReadyToDiscard`, `isMenuItemActive`, `executeMenuItemCommand`, `emitRealTimeUpdate`, `listenToRealTimeUpdate`, `onDocumentInfoChange`, `onHeadingChange`, `onStateChange`, `focus`, `undo`, `redo`, `getCoordsFromPos`, `getCurrentCursorPosition`, `getAttributesWithExtendedMark`, `scrollSummary`, `scrollToNodeViaDOMCoordinates`, `setEditorValue`, `setEditorValueAtCursorPosition`, `setFocusAtPosition`, `setProviderDocument`) bleiben in Name, Signatur und Verhalten gleich. Konsumenten erhalten sie über `viewChild.required(PlEdRichTextEditor).ref()`. `EditorTitleRefApi` (`use-title-editor.ts`) liefert `PlEdCollaborativeDocumentEditor.titleRefApi()`.
