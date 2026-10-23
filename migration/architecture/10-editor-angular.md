# 10 – Rich-Text-Editor in Angular (Port von `packages/editor`)

> **Stand:** 23.10.2026 (adversarial reviewt, siehe „Review-Protokoll“ am Ende). **Status:** Entwurf zur Abnahme. **Verbindlichkeit:** bindend für alle Implementierungs-Agenten, die Editor-Code in `funk.` schreiben oder einbinden; nachrangig zu `00-grundsatzentscheidungen.md` (ADR-000…009B), `01-zielarchitektur-und-tech-stack.md` (ADR-010 ff., insbesondere ADR-042) und `17-abgleich-dokumentuebergreifend.md`.
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
- Review-Protokoll (adversarialer Review 23.10.2026)

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
| Angular-Bindung | vendorte Bindung (`EditorContent`, `AngularNodeViewRenderer` inkl. `NodeViewWrapper`-Element, `AngularRenderer`, `NodeViewContent`, Bubble-Menü-Direktive, `editorState()`) | 3.5 |
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
| **CE-IDs ohne Editor-Anteil bzw. mit reinem Server-Anteil** (bewusst ausgeschlossen): CE-PAGE-001…-010, -012 (Page-Liste, Anlegen, Sperren, Zugriff, Archiv, Löschen, Duplizieren, Favoriten, PageLog), CE-RT-001 (Realtime-Server), CE-RT-005 (Persistenz/Titel-Sync), CE-RT-007 (Mehrinstanz), CE-RT-009 (Health), CE-RT-008 (Konvertierung, Server; der Client-Konverter `yjs-utils`/`parser` ist Kern-Kopie, Anhang A) | D07 (Realtime/Konvertierung), D08 (Pages-Stores/-Screens); D10 liefert dafür nur die Editor-Schnittstellen aus §3.8 |

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
| **D10-ADR-03** | Übernahme des Kerns | **Datei-für-Datei-Kopie mit gleichem relativem Pfad** (`ED0/<pfad>` → `ED/core/src/<pfad>`, `.tsx` → `.ts`), erzeugt durch den Codemod `FE/tools/editor-port/port-core.mjs` (Importpfad-Umschreibung, Typ-Ersetzungen §3.3); jede Datei trägt einen Kopfkommentar `// ported-from: packages/editor/src/<pfad> @ 053b2c0` (Referenzstand ADR-006: Branch `funk-referenz-1.4.2`). Handänderungen nur in den 38 Dateien der Kategorien K2/NV (Anhang A), jeweils mit Marker `// PORT-DIFF(<grund>)`. Der CI-Check **G-EDCORE** (`FE/tools/editor-port/check-core-drift.mjs`) vergleicht jede K1-Datei normalisiert (Importpfade, Header) mit dem Original und lässt nur markierte Abweichungen zu | freie Neuimplementierung; Git-Submodul auf das Original (React-Abhängigkeiten im Baum) | Der Kern ist ~70 % des Codes und bereits framework-agnostisch (A12 §5.1); eine 1:1-Kopie hält Verhalten, Prioritäten und Edge-Cases exakt; der Drift-Check macht Abweichungen sichtbar | AGPL-3.0 (abgeleitetes Werk, Z-11 entschieden) | I0 (Werkzeug), I2 (Kern) |
| **D10-ADR-04** | React-Renderer im Kern | **UI-Port** statt Framework-Abhängigkeit: Die zehn Kern-Dateien, die `ReactNodeViewRenderer` bzw. `ReactRenderer` aufrufen (Callout, Code-Block, Custom-Image, Legacy-Image, Mention, Slash-Commands, Mention-Dropdown, Emoji-Suggestion, Tabellen-Spalten-/Zeilen-Handle), rufen stattdessen `uiNodeView(<key>)` bzw. `uiRender(editor, <key>, props)` aus `ED/core/src/ui-port/ui-port.ts` auf. Die Angular-Schicht registriert über die Tiptap-Extension `PlaneUiPortExtension` eine Implementierung mit einer Schlüssel→Komponente-Tabelle (§3.4). Ohne registrierten Port (Node/jsdom, Server-Schema-Test) liefert `uiNodeView` trotzdem eine NodeView-Fabrik, deren Aufruf `null` zurückgibt – ProseMirror rendert dann über `toDOM`/`renderHTML` (`prosemirror-view` 1.42.6 `src/viewdesc.ts` Z. 707: `let dom = spec && spec.dom`); `uiRender` liefert `null` (keine Dropdowns). **Nicht** zulässig ist, dass `addNodeView()` selbst `null` liefert: Tiptap ruft `addNodeView()(props)` je Node auf (`@tiptap/core` 2.27.3 `src/ExtensionManager.ts` Z. 301) und würfe einen `TypeError` | Extension-Dateien in die Angular-Schicht verschieben (dann hinge `core-without-props.ts` – Quelle des Server-Schemas – über `EmojiExtension` und `Table` an Angular); Injector als Extension-Option durchreichen (ändert alle Fabrik-Signaturen) | Hält den kompletten Extension-Graphen inkl. Server-Schema framework-frei, minimiert Diffs (eine Zeile je Aufrufstelle), erlaubt den S5-Fallback (DOM-NodeViews) und die D9-Blöcke über dieselbe Schlüsseltabelle | – | I2 |
| **D10-ADR-05** | Angular-Bindung | **Vendorte, eigene Bindung** `ED/angular-binding` mit **DOM-Parität zu `@tiptap/react` 2.26.1** (Elementstruktur, Klassen `react-renderer node-<typ>`, `data-node-view-wrapper`, `data-node-view-content`, Inline-Styles `white-space`), Muster (nicht Code-Abhängigkeit) von `ngx-tiptap` 13 (MIT; Peer `@tiptap/core ^2.7.0`, `@angular/core >=20`, geprüft 23.10.2026). Umfang: `EditorContentDirective`, `AngularNodeViewRenderer` (erzeugt auch das `NodeViewWrapper`-Element, alle Original-NodeViews nutzen dessen Default-Tag `div`), `AngularRenderer`, `NodeViewContentDirective`, `NodeViewDragHandleDirective`, `BubbleMenuDirective`, `editorState()`, `PlaneUiPortExtension` | `ngx-tiptap` 13 als Abhängigkeit (Host-Elemente der Komponenten erzeugen anderes DOM; CSS des Originals adressiert `.node-imageComponent`, `.node-image` in `drag-drop.css`); ngx-tiptap 14/15 (nur Tiptap 3) | DOM-Gleichheit ist Pflicht (ADR-005, CSS-Selektoren); ~600 LOC eigene Bindung (D01 §2.2) entkoppeln von Fremd-Releases | MIT-Muster, eigener Code AGPL | I2 (S5 in I0) |
| **D10-ADR-06** | Hosting von NodeView-Komponenten | NodeView-Komponenten sind **Attribut-Selektor-Komponenten**, die auf das von der Bindung erzeugte Wrapper-Element gesetzt werden (`createComponent(..., { hostElement })`): äußeres Element `div` bzw. `span` mit Klassen `react-renderer node-<typ>` (von `AngularNodeView`), darin das Wrapper-Element `div[data-node-view-wrapper]` (Host der Komponente, Klassen per Host-Binding), Content-Bereich über `[plEdNodeViewContent]` an beliebiger Stelle des Templates. Komponenten-Präfix `PlEd`, Selektoren `pl-ed-…`/`[plEd…]` (Regel D09-ADR-03) | Element-Selektoren (zusätzliche DOM-Ebene); `NgComponentOutlet` je NodeView (keine Kontrolle über `contentDOM`) | Gleiche DOM-Tiefe wie React (`NodeViewWrapper` erzeugt genau ein Element); kein Fremd-Element zwischen `.react-renderer` und Wrapper | – | I2 |
| **D10-ADR-07** | Floating-UI, Portale, Overlays | Editor-eigene, schmale Nachbildung von `@floating-ui/react` 0.27.20 auf Basis von **`@floating-ui/dom` 1.8.0** in `ED/components/src/floating/`: `PlEdFloatingPortal` (`div[data-floating-ui-portal]#floating-ui-<n>` an `document.body`), `PlEdFloatingOverlay` (fixe Vollfläche, `lockScroll` mit `data-floating-ui-scroll-lock` am `body`), `createFloatingMenu()` (= `useFloating` + `useClick` + `useDismiss` + `useRole` inkl. ARIA-Attributen). Bubble-Menü über `@tiptap/extension-bubble-menu` 2.26.3 + `tippy.js` 6.3.7 (wie Original). Kein `@angular/cdk/overlay` (ABG-026); die Propel-Portal-Schicht (`portal.ts`, Base-UI-Vertrag `data-base-ui-portal`) wird für Editor-Overlays **nicht** verwendet, weil das Original hier den Floating-UI-DOM-Vertrag erzeugt | Angular CDK Overlay (verboten, anderes DOM); Propel-Portal (falscher Marker); tippy für alle Menüs (Original nutzt tippy nur im Bubble-Menü) | DOM-Parität der Portale (D09 N1 „Portal-Container“); Positionierungslogik identisch, weil dieselbe Bibliothek rechnet | MIT | I2 |
| **D10-ADR-08** | Komponenten-API der Varianten | **Inputs = Props des Originals mit gleichem Namen** (`id`, `editable`, `initialValue`, `value`, `disabledExtensions`, `flaggedExtensions`, `fileHandler`, `mentionHandler`, `getEditorMetaData`, `displayConfig`, `placeholder`, …, vollständige Tabelle §3.6.2); Handler-Objekte und Rückruf-Funktionen, deren Rückgabewert der Editor nutzt, bleiben **Inputs vom Funktionstyp**; reine Benachrichtigungen werden **Outputs mit Präfix `editor`** (`editorChange`, `editorFocus`, `editorTransaction`, `editorReady`, `editorEnterKeyPress`, `editorAssetChange`), damit sie nicht mit gleichnamigen nativen DOM-Events (z. B. `change` der Task-Checkbox, das zum Host hochblubbert) kollidieren. Die Ref-API (`EditorRefApi`, `EditorTitleRefApi`) stellt jede Variante als `readonly ref: Signal<EditorRefApi \| null>` bereit (Zugriff über `viewChild`) | alle Callbacks als Outputs (Rückgabewerte von `getEditorMetaData`/`fileHandler.upload` unmöglich); Output-Namen `change`/`focus` (Kollision mit DOM-Events) | 1:1-Port der Konsumenten (Hüllen, Stores) mit minimalen Umbenennungen; Kollisionsfreiheit ist prüfbar | – | I2 |
| **D10-ADR-09** | Lebenszyklus | `EditorInstance` (Komponenten-Provider je Variante) bildet `ED0/hooks/use-editor.ts` exakt nach: Editor wird beim ersten Rendern erzeugt und **nur bei Änderung von `editable` neu aufgebaut** (Extensions werden beim Erstellen fixiert); externer `value`-Sync nur wenn `value != null`, Editor lebt und kein Upload läuft; Cursor danach `min(alte from, docSize-1)`; `assetsUploadStatus` → `updateAssetsUploadStatus`; `assetsList`-Änderung → `editorAssetChange`. `immediatelyRender`/`shouldRerenderOnTransaction` entfallen (React-spezifisch) | Neuaufbau bei jeder Input-Änderung; Signal-Forms-Anbindung (`FormValueControl`) | Exakt dieselben Re-Init-Grenzen vermeiden Cursor-Sprünge und doppelte ID-Vergabe; Formular-Anbindung bietet das Original nicht | – | I2 |
| **D10-ADR-10** | Zoneless und Change Detection | Alle Editor-Ereignisse (`transaction`, `update`, `selectionUpdate`, `focus`, `blur`, Provider-Status) werden **ausschließlich in Signale geschrieben**; `editorState(editor, selector, equal?)` ersetzt `useEditorState` (Neuberechnung bei `transaction`, Gleichheitsprüfung **wie `@tiptap/react` 2.26.1: Default `deepEqual` aus `fast-deep-equal/es6` 3.1.3** – `useEditorState.ts` Z. 2/168 – bzw. übergebene Funktion; mit `Object.is` würden Selektoren, die Objekte liefern, bei jeder Transaktion feuern, z. B. `editorAssetChange`). NodeView-Inputs werden per `ComponentRef.setInput()` gesetzt (markiert die View für Zoneless-CD). Keine `NgZone`-Aufrufe, keine `ChangeDetectorRef.detectChanges()` außer im `AngularRenderer.updateProps` vor synchronen DOM-Messungen (Floating-UI) | zone.js-Kompatibilitätsmodus | Angular 22 ist zoneless per Default (D01); R-D08-03 verlangt Signal-Schreibweise für Drittbibliotheks-Callbacks | – | I2 |
| **D10-ADR-11** | Kollaborations-Client | `@hocuspocus/provider` 2.15.2, `yjs` 13.6.27, `y-prosemirror` 1.3.7, `y-protocols` 1.0.6, `y-indexeddb` 9.0.12 **unverändert**; **einziger** Import von `@hocuspocus/provider` in `ED/collaboration/src/collaboration-provider.factory.ts` (`CollaborationProviderFactory`, R-D08-13); `CollaborationSession` portiert `use-yjs-setup.ts` 1:1 (Stages `initial`, `connecting`, `awaiting-sync`, `synced`, `reconnecting`, `disconnected`, Max-Retries 3, Visibility/Online-Reconnect mit 1-s-Throttle, Close-Codes 4000–4003). Awareness-Token `{id, name, color}` wie Original. Live-Cursor (`collaboration-cursor`) über `@tiptap/extension-collaboration-cursor` **2.26.1** hinter dem Flag `EDITOR_FLAGS` (CE-Default wie Original: deaktiviert; Aktivierung = Entscheidung O-D08-07/FE-ED-01) | eigener WS-Client; y-websocket (nur S1-Fallback) | Browser-Client bleibt Referenzimplementierung des Protokolls (ADR-002); Kapselung macht den S1-Fallback zu einem Ein-Datei-Wechsel | MIT | I4 |
| **D10-ADR-12** | Emoji offline | Editor-Emoji (Suggestion `:`, Shortcodes, Emoticons, Unicode→Node) nutzt wie das Original die **in `@tiptap/extension-emoji` 2.26.1 gebündelten Daten** (`emojis`, `gitHubEmojis`, über `emojibase-data` **15.3.2** zur Build-Zeit im JS-Bundle). Die Datensätze enthalten `fallbackImage`-URLs (1 814 × `https://cdn.jsdelivr.net/npm/emoji-datasource-apple/…`, 19 × `https://github.githubassets.com/images/…` im Dist von `@tiptap/extension-emoji` 2.26.1); `ED0/extensions/emoji/extension.ts` Z. 33–35 filtert Einträge ohne Unicode und **entfernt `fallbackImage` zur Laufzeit** (1:1 übernommen) → keine Bildabrufe; die Literale bleiben im Vendor-Chunk und erhalten einen Airgap-Allowlist-Eintrag (§3.12). `emojibase-data` wird per Override auf 15.3.2 gepinnt – dieselbe Version wie die Picker-Assets nach ABG-029. Der Callout-Default `data-emoji-url="https://cdn.jsdelivr.net/npm/emoji-datasource-apple/img/apple/64/1f4a1.png"` bleibt **als Attributwert unverändert** (Schema-Default, wird nie geladen, Anzeige nutzt Unicode); der Airgap-Scan erhält dafür und für die `fallbackImage`-Literale des Emoji-Datensatzes begründete Allowlist-Einträge (§3.12), der Airgap-E2E beweist „0 Requests“ | Default-URL auf lokales Asset umstellen (Schema- und HTML-Abweichung, G-SCHEMA/G-DOC rot); Emoji-Daten zur Laufzeit aus `assets/emojibase` laden (Original lädt sie nicht) | Schema-Freeze + Airgap gleichzeitig erfüllt; keine zweite Emoji-Datenversion | MIT | I2 |
| **D10-ADR-13** | Editor-CSS | `ED0/styles/*.css` (7 Dateien) **1:1** nach `ED/styles/`; Import-Position nach D09 §3.2.2 (Web und Space, nicht Admin). Tiptap-Core-CSS (`@tiptap/core` 2.27.3 `src/style.ts`) wird **statisch** als `ED/styles/tiptap-core.css` ausgeliefert und `injectCSS: false` gesetzt (kein `<style data-tiptap-style>` zur Laufzeit, CSP-fest); Kaskadenposition: **letzter, ungeschichteter Import** der globalen Styles (das Original hängt das Tag beim ersten Editor-Start ans **Ende** von `<head>`, `@tiptap/core` 2.27.3 `src/utilities/createStyleTag.ts`; §3.20.2); die Datei wird per `FE/tools/editor-port/extract-tiptap-style.mjs` aus dem gepinnten Paket erzeugt und im G-CSS als `kind: extra-css` (Abweichung `FE-ED-07`) registriert | Laufzeit-Injektion mit `injectNonce` (Nonce-Infrastruktur fehlt, Gateway setzt Hash-CSP, ABG-016) | Gleiches berechnetes Styling bei strenger CSP; die DOM-Normalisierung entfernt `<style>` ohnehin (D09 N2) | MIT | I0 (Kopie), I2 (Nutzung) |
| **D10-ADR-14** | Schema-Freeze und Goldens | Das Schema aller Varianten ist eingefroren. Nachweis über **G-SCHEMA**: fünf Browser-Varianten (`rich`, `lite`, `document`, `collaborative`, `title`, Ablage `Golden/schema/browser/`) mit je drei Dateien `*.schema.json` (Nodes/Marks inkl. Attribute, Defaults, Content-Ausdrücke, Gruppen, `parseDOM`-Regeln), `*.extensions.json` (Extension-Name, Typ, Priorität in der **effektiven** Reihenfolge von `editor.extensionManager.extensions` = Registrierungsreihenfolge, stabil nach Priorität sortiert durch `ExtensionManager.sort`, `@tiptap/core` 2.27.3), `*.plugins.json` (PluginKey-Reihenfolge des `EditorState`). sowie der TS-Server-Schema-Export des Kerns gegen die Server-Goldens aus D07 (`rich`, `document`, `title`). Erzeugung mit `tools/golden/generate.mjs schema` aus dem Original-Referenzstand (Node + jsdom), Prüfung im Browser-Build per Vitest (Projekt `shared-dom`) mit demselben Serialisierer `ED/core/src/testing/schema-serializer.ts`. Änderungen nur per Schema-Änderungsverfahren §3.2.5 | nur Schema-JSON ohne Extension-/Plugin-Manifest (Prioritäten und Plugin-Reihenfolge – A12 §5.7 Nr. 6 – blieben ungeprüft); Schema-Vergleich nur serverseitig | Prioritäten (`UniqueID` 10000, `link`/`utility` 1000, Navigation 10) und Plugin-Reihenfolge bestimmen Verhalten; sie sind nur so maschinell prüfbar | – | I2 (Kern-Varianten), I4 (`collaborative`, `title`) |
| **D10-ADR-15** | Inkrement-Schnitt | Der **Rich-Text-Editor mit allen NodeViews und Menüs** und der **Document-Editor (read-only)** gehören zu **I2**, nicht zu I4, weil CE-WI-001/-005 (Beschreibung) und CE-WI-041 (Beschreibungs-Versionen) sie in I2 brauchen; I4 bringt nur Kollaboration, Titel-Editor und die Page-Hüllen. Folge: Spike **S5** muss vor I2 **vollständig** grün sein (nicht nur der „Lite-Teil“); nur das S5-Kriterium „NodeView-Rendering stabil mit Yjs“ darf bis vor I4 nachgeliefert werden | Rich-Editor erst I4 (Work-Item-Beschreibung in I2 nicht 1:1 möglich); Zwischenlösung Lite-Editor als Beschreibung (sichtbare Abweichung) | Nutzungskette und Abnehmbarkeit von I2; Präzisierung von D01 §1.3/ADR-042 („I2 (Lite), I4 (Rich/Document)“), Rückmeldung §9 | – | I2 |
| **D10-ADR-16** | Umgang mit Quirks und Bugs des Originals | Regel Z-12 (D17): optisch 1:1, **funktionale** Fehler werden korrigiert und dokumentiert. Für jeden Editor-Edge-Case E1–E31 (A12 §3.25) ist in §3.22 festgelegt: korrigieren (Abweichung `FE-ED-nn` in `FE/apps/e2e/visual/ui-deviations.yaml` bzw. bei Vertragswirkung in `tests/contracts/deviations.yaml`), beibehalten (mit Begründung) oder Zuständigkeit D07. Schema-/HTML-Quirks (E15, E16, E17, E19) werden **beibehalten**, weil ihre Korrektur Schema/HTML ändert | alle Quirks 1:1 (widerspricht Z-12); alle korrigieren (bricht Schema-Freeze) | Z-12 ist entschieden; Schema-Freeze hat Vorrang vor Komfort-Korrekturen | – | I2 |
| **D10-ADR-17** | Ort der Web-/Space-Hüllen | `WEB/components/editor/**` (Rich-, Lite-, Sticky-, Document-Hüllen, Mention-Embeds), `WEB/hooks/editor/**`, `WEB/hooks/use-editor-flagging.ts`, `use-additional-editor-mention.tsx`, `use-parse-editor-content.ts` → **`FE/libs/web/core/editor/`** (Domäne `core`, von allen Domänen importierbar); `WEB/components/pages/editor/**` → `FE/libs/web/pages/components/pages/editor/**`; `SPC/components/editor/**` → `FE/libs/space/editor/` | Hüllen in `libs/web/pages` (D01 §6.1 Kommentar) – dann müssten `work-items`, `intake`, `stickies`, `comments` die Pages-Domäne importieren (Domänen-Matrix D08) | Die Hüllen sind Querschnitt (Beschreibung, Kommentare, Stickies, GPT-Popover); `core` ist die einzige für alle Domänen erlaubte Web-Lib. Präzisierung von D01 §6.1, Rückmeldung §9 | – | I2 |
| **D10-ADR-18** | Erweiterbarkeit | Die Editor-Tokens `EDITOR_EXTENSIONS`, `EDITOR_BLOCKS`, `EDITOR_MENTION_TYPES`, `EDITOR_FLAGS` werden in **`ED/extensibility/src/tokens.ts` deklariert** (der Editor ist `scope:shared` und darf `EXT` nicht importieren) und von `EXT` (`@plane/web/extensions`) sowie `FE/libs/space/extensions` **re-exportiert**; Pakete importieren weiterhin aus `EXT` (D08 §6.1 bleibt öffentlicher Ort). CE-Defaults über `provideEditorDefaults()`, aufgerufen in `provideWebExtensions()` und `provideSpaceExtensions()`. `PAGE_PANE_EXTENSIONS` bleibt reines Web-Token in `EXT`. Zusätzliche Blöcke laufen ausschließlich über `EditorBlockDefinition` (§6.2) | Tokens nur in `EXT` (Editor könnte sie nicht lesen, Space hätte keine); Props-Durchreichen über alle Hüllen (jede Hülle müsste für D9 geändert werden) | Sheriff-Regeln (`type:ui` shared darf keine App-Libs importieren) und D16-Regel „ohne Umbau“ gleichzeitig erfüllt | – | I2 |
| **D10-ADR-19** | Texte im Editor und Branding | Editor-Texte bleiben **englisch und hart codiert** wie im Original (A12 §5.7 Nr. 10: „Press '/' for commands...“, „Untitled“, Slash-Titel, Menü-Labels, Fehlermeldungen); Texte der Hüllen (z. B. Kommentar-Platzhalter `issue.comments.placeholder`) laufen über `TranslationService` (D08). **ADR-009B (bestätigt durch 17 ABG-148):** `ED0/` enthält keinen sichtbaren Text „Plane“ (geprüft per `grep`, Anhang B) – die hart codierten Editor-Texte bleiben daher unverändert, das Abweichungsregister `BRAND-ED` ist derzeit leer (BR-13); Editor-Platzhalter und Tooltips, die die Hüllen setzen (z. B. `issue.comments.placeholder`), laufen über `TranslationService` und damit über die nach BR-10 ersetzten i18n-Dateien (D08 §3.7); neue Editor-Texte mit Produktnamen nutzen `BRAND.productName` (`@plane/constants`, BR-03) und erhalten einen `BRAND-ED-<nn>`-Eintrag; der interne Clipboard-MIME-Typ `text/plane-editor-html` bleibt als nicht sichtbarer Bezeichner unverändert (BR-02; Kompatibilität Copy/Paste zwischen Editoren) | Editor-Texte übersetzen (sichtbare Abweichung zum Original) | ADR-005 | – | I2 |
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
│   ├── ui-port/ui-props.ts                  # Props-/Ref-Typen der UI-Komponenten, aus den NG-Dateien herausgezogen (R-ED-15)
│   ├── extensibility/block-registry.ts      # registerEditorBlocks(), getEditorBlocks(), sealEditorBlockRegistry() (§5.10, §6.2)
│   ├── extensibility/editor-block-definition.ts
│   └── testing/{schema-serializer,stub-handlers}.ts           # nur Tests/Golden
├── angular-binding/src/                     # Tag editor:binding; Alias @plane/editor/angular-binding (intern)
│   ├── public-api.ts
│   ├── editor-content.directive.ts          # [plEdEditorContent] – hängt editor.view.dom ein (EditorContent)
│   ├── angular-renderer.ts                  # AngularRenderer (ReactRenderer-Ersatz)
│   ├── angular-node-view-renderer.ts        # AngularNodeView, AngularNodeViewRenderer()
│   ├── node-view-context.ts                 # NODE_VIEW_CONTEXT (contentDOM, onDragStart) für Direktiven
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
├── styles/                                  # 1:1 aus ED0/styles + tiptap-core.css (D10-ADR-13)
│   └── index.css  variables.css  editor.css  table.css  github-dark.css  drag-drop.css  title-editor.css  tiptap-core.css
│                                            # (später, nicht CE-I0: collaboration-cursor.css – neu, erst mit FE-ED-01/Paket D4, §3.15.2)
└── packages/<paket>/{core,ui}/src/          # NUR Bezahl-Pakete (D9, D6, D7, D10, B2): Paket-Blöcke, §6.2 Regel 5; in der CE leer
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
| `editor:core` | `ED/core` | `type:types`, `type:constants`, `type:utils` (`@plane/types`, `@plane/constants`, `@plane/utils`), `@plane/propel/icons`, `@plane/blocks/icons` (nur `PlIconDef`-Konstanten), `@plane/icons-lucide`, npm: `@tiptap/*` (außer `react`), `prosemirror-*`, `yjs`, `y-prosemirror`, `y-protocols`, `lowlight`, `highlight.js`, `linkifyjs`, `tiptap-markdown`, `emoji-regex`, `is-emoji-supported`, `@floating-ui/dom`, `tippy.js`, `uuid`, `@hocuspocus/provider` **nur als `import type`** | `@angular/*`, `rxjs`, `react`, `react-dom`, `@tiptap/react`, `@floating-ui/react`, `lucide-react`, `jsx-dom-cjs`, `@plane/editor` (Zyklus) |
| `editor:binding` | `ED/angular-binding` | `editor:core`, `@angular/core`, `@angular/common`, npm `fast-deep-equal` (Default-Gleichheit von `editorState()`), `@tiptap/extension-bubble-menu`, `tippy.js` | `@hocuspocus/provider`, `@plane/propel/components/*` |
| `editor:ui` | `ED/components` | `editor:core`, `editor:binding`, `editor:extensibility`, `type:ui` in Richtung `cdk ← propel ← blocks ← editor` (D08), `type:data` (`i18n`, `state-kit`) | `@hocuspocus/provider` (nur über `editor:collab`) |
| `editor:collab` | `ED/collaboration` | `editor:core`, `editor:ui`, `@hocuspocus/provider`, `y-indexeddb`, `yjs` | – |
| `editor:extensibility` | `ED/extensibility` | `editor:core`, `@angular/core` | `editor:ui`, `editor:collab` |
| `editor:package-core` / `editor:package-ui` | `ED/packages/<paket>/{core,ui}` (nur Pakete, §6.2) | wie `editor:core` bzw. wie `editor:ui` (+ `editor:package-core` des eigenen Pakets) | Import durch CE-Libs (`editor:*`, `domain:*`) verboten; einzige Einbindung über `provide<Paket>Extensions()` |

Alle fünf Teil-Libs tragen zusätzlich `scope:shared`, `type:ui` (D08 §3.1.3).

**Komponentenregeln (Ergänzung zu D09-ADR-03):** Für `ED/components/**`, `ED/angular-binding/**`, `FE/libs/web/core/editor/**` und `FE/libs/space/editor/**` gelten `ChangeDetectionStrategy.OnPush`, `ViewEncapsulation.None` und „keine Komponenten-Styles“ ebenfalls; die Lint-Regel `no-component-styles` (D09 §3.3, D08 §7.6) wird auf diese Pfade erweitert (sonst erzeugt Emulated-Encapsulation `_ngcontent-*`-Attribute in NodeView-DOM und Floating-Menüs). Der Kern-Import `@plane/propel/icons` ist nur zulässig, wenn dieser Einstiegspunkt **ausschließlich `PlIconDef`-Daten** exportiert (keine Re-Exporte von `svg-icon.component.ts`/`@angular/*`); dasselbe gilt für `@plane/blocks/icons` und `@plane/icons-lucide` – geprüft durch AK-D10-04 (Rückmeldung an D09 §3.1, Ordner `PRP/icons/`). Konsumenten außerhalb von `ED/` importieren nur `@plane/editor`, `@plane/editor/collaboration`, `@plane/editor/extensibility` und (für Konverter/Typen) `@plane/editor/core`.

### 3.2 Versionen, Schema-Freeze, Golden-Vertrag

#### 3.2.1 Exakte Pins (`ED/VERSIONS.json`, Quelle: `pnpm-lock.yaml` des Originals, Importer `packages/editor`)

| Paket | Version | Rolle | Lizenz |
|---|---|---|---|
| `@tiptap/core` | 2.27.3 | Editor-Kern | MIT |
| `@tiptap/pm` | 2.26.1 | ProseMirror-Bündel | MIT |
| `@tiptap/starter-kit` | 2.26.1 | Basis-Nodes/Marks | MIT |
| `@tiptap/extension-{blockquote,character-count,collaboration,document,emoji,heading,image,list-item,mention,placeholder,task-item,task-list,text,text-align,text-style,underline}` | 2.26.1 | Extensions (Catalog des Originals) | MIT |
| `@tiptap/extension-history` | 2.26.1 | transitiv über StarterKit | MIT |
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
| `emojibase` | 16.0.0 | Peer von `emojibase-data` 15.3.2 (Lockfile-Stand, nur Typen/Hilfen) | MIT |
| `fast-deep-equal` | 3.1.3 | Default-Gleichheit von `editorState()` (wie `useEditorState` in `@tiptap/react` 2.26.1) | MIT |
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
| `rich` | `CoreEditorExtensions` + `SideMenuExtension({aiEnabled:false, dragDropEnabled})` + `RichTextEditorAdditionalExtensions` (Slash); `dragDropEnabled` wie von der Web-Hülle `WEB/components/editor/rich-text/editor.tsx` übergeben | `disabledExtensions: ["ai","collaboration-cursor"]`, `flaggedExtensions: []`, `editable: true`, `enableHistory: true`, `provider: undefined`, Stub-Handler | `browser/rich.schema.json`, `browser/rich.extensions.json`, `browser/rich.plugins.json` | `ED/core/src/testing/schema-golden.spec.ts` | – |
| `lite` | `CoreEditorExtensions` + `EnterKeyExtension` | wie oben | `browser/lite.*.json` | dto. | – |
| `document` | `CoreEditorExtensions` + `SideMenuExtension({aiEnabled:false, dragDropEnabled:true})` + `HeadingListExtension` + `DocumentEditorAdditionalExtensions` | wie oben | `browser/document.*.json` | dto. | – |
| `collaborative` | wie `document` + `Collaboration({field:"default"})` + `mainEditorNavigation`, `enableHistory: false` | mit leerem `Y.Doc`, Fake-Provider (Objekt mit `document`, ohne Netz) | `browser/collaborative.*.json` | dto. (I4) | – |
| `title` | `TitleExtensions` + `Collaboration({field:"title"})` + `titleEditorNavigation` + `Placeholder("Untitled")` | dto. | `browser/title.*.json` (Schema-Teil zusätzlich = D07 `title.schema.json`) | dto. (I4) | – |
| `server` | `CoreEditorExtensionsWithoutProps` (TS-Export `ED/core/src/lib.ts`, Grundlage der Client-Konverter `yjs-utils`) | – | D07-Golden `rich.schema.json` (Eigentümer D07, AK-07-20) | dto. | `SchemaSnapshotTests` (D07) |
| `server-document` | `CoreEditorExtensionsWithoutProps` + `DocumentEditorExtensionsWithoutProps` | – | D07-Golden `document.schema.json` | dto. | dto. |

Verbindlich nach 17 ABG-119: Server-Goldens (Eigentümer D07) sind genau `{rich,document,title}.schema.json` – **kein** `server.schema.json`; die Zeilen `server`/`server-document` prüfen das TS-Server-Schema gegen die D07-Goldens `rich`/`document`. Ablage aller Dateien unter `tests/Plane.Documents.Tests/Golden/schema/`; die **Browser-Varianten** liegen im Unterordner `browser/` (Namen kollidieren sonst mit den Server-Varianten `rich`/`document`/`title` aus D07 §7.5, die `CoreEditorExtensionsWithoutProps`, `+ DocumentEditorExtensionsWithoutProps` bzw. `TitleExtensions` beschreiben). Die Browser-Varianten und die Manifeste ergänzen D15 §3.7.1 und D07 §7.5 (Rückmeldung §9). Serialisierung: §5.9 – dasselbe JSON-Format wie die Server-Goldens (gemeinsamer Serialisierer im Generator).

#### 3.2.4 Generator-Unterbefehl `tools/golden/generate.mjs schema` (Eigentümer Werkzeug D15, Inhalt D10)

1. Läuft im Original-Repo-Checkout des Referenzstands (Branch `funk-referenz-1.4.2`, Commit `053b2c0`, ADR-006; Node 22, `pnpm install`), importiert `packages/editor/src/**` per `tsx` (ESM) mit `jsdom`-Global; React wird geladen, aber keine NodeView instanziiert (leeres Dokument).
2. Baut je Variante einen Editor `new Editor({ extensions, content: "<p></p>", editable: true, injectCSS: false })`, serialisiert `editor.schema`, `editor.extensionManager.extensions` und `editor.state.plugins` mit `ED/core/src/testing/schema-serializer.ts` (dieselbe Datei wird in den Generator kopiert; Byte-Gleichheit beider Kopien prüft `check-core-drift.mjs`).
3. Schreibt die Listen in der Reihenfolge, die Tiptap liefert (`extensionManager.extensions` ist bereits nach Priorität stabil sortiert; `state.plugins` in Plugin-Reihenfolge; keine eigene Neusortierung), UTF-8, `\n`, 2 Leerzeichen.

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
| R-ED-12 Modul-Konstanten mit Paket-Beiträgen | `ADDITIONAL_BLOCK_NODE_TYPES`, `ADDITIONAL_ASSETS_META_DATA_RECORD`, `COMBINED_BLOCK_NODE_TYPES` sowie die beim **Modul-Import** gebildeten Arrays `CoreEditorExtensionsWithoutProps`/`DocumentEditorExtensionsWithoutProps` (`extensions/core-without-props.ts`) sowie `RICH_TEXT_EDITOR_EXTENSIONS`/`DOCUMENT_EDITOR_EXTENSIONS` (`helpers/yjs-utils.ts`) | Getter `getAdditionalBlockNodeTypes()`, `getAdditionalAssetsMetaDataRecord()`, `getCoreEditorExtensionsWithoutProps()`, `getDocumentEditorExtensionsWithoutProps()`; Leser (UniqueID, `helpers/assets.ts`, `yjs-utils`) rufen die Getter **zur Laufzeit** auf. Die Original-Konstanten bleiben mit CE-Wert exportiert. Grund: Modul-Konstanten werden beim Import ausgewertet – also **vor** `provideAppInitializer` (Registrierung der Paket-Blöcke); ohne Getter fehlten Paket-Nodes im Client-Konverter. CE-Ergebnis identisch (`[]`/`{}`/Original-Liste) | K2 + `PORT-DIFF(block-registry)` |
| R-ED-15 Props-Typen aus UI-Dateien | NV/K2-Kern-Dateien importieren Typen aus React-Dateien (NG): `BlockMenuOption` (`components/menus/block-menu.tsx`), `CustomCalloutNodeViewProps` (`extensions/callout/block.tsx`), `CustomImageNodeViewProps` (`extensions/custom-image/components/node-view.tsx`), `EmojisListDropdownProps`, `EmojiItem` (`extensions/emoji/components/emojis-list.tsx`), `MentionNodeViewProps` (`extensions/mentions/mention-node-view.tsx`), `MentionsListDropdownProps` (`extensions/mentions/mentions-list-dropdown.tsx`), `SlashCommandsMenuProps` (`extensions/slash-commands/command-menu.tsx`), `ColumnDragHandleProps`, `RowDragHandleProps` (`extensions/table/plugins/drag-handles/{column,row}/drag-handle.tsx`) | Typen (Felder 1:1, React-Typen nach R-ED-7) nach `ED/core/src/ui-port/ui-props.ts`; Kern-Dateien importieren von dort, die Angular-Komponenten aus `@plane/editor/core` (Richtung Kern ← UI bleibt erhalten) | K2/NV + `PORT-DIFF(ui-port)` |
| R-ED-13 Header | – | `// ported-from: packages/editor/src/<pfad> @ 053b2c0` (ADR-006) + Lizenz-Header des Originals unverändert (AGPL-3.0-only, Copyright Plane Software) | alle |
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

Ohne registrierten Port (Node-Golden-Generator in der Zielvariante, Schema-Tests, Kern-Unit-Tests in jsdom, künftige Web-Worker) liefert `uiNodeView(...)` **immer eine NodeView-Fabrik**; erst deren Aufruf prüft den Port und gibt ohne Port `null` zurück. ProseMirror rendert den Node dann über `toDOM` (= Tiptap-`renderHTML`) – verifiziert in `prosemirror-view` 1.42.6 `src/viewdesc.ts` Z. 707 (`let dom = spec && spec.dom`, sonst `DOMSerializer.renderSpec`). `uiNodeView` darf **nie selbst `null`** liefern: Tiptap 2.27.3 ruft in `ExtensionManager.nodeViews` (Z. 301) `addNodeView()(props)` für jeden Node auf – ein `null` führte beim ersten Callout/Bild/Code-Block/Mention zu `TypeError: addNodeView(...) is not a function`. `uiRender` liefert ohne Port `null`; Suggestion-`onStart` beendet sich dann still (das Menü erscheint nicht). Die Schema-Goldens und Kern-Unit-Tests mit Dokumenten, die NodeView-Nodes enthalten (z. B. G-DOC-Korpus in jsdom), sind dadurch unabhängig von Angular; Pflicht-Test `ui-port.no-port.spec.ts` (Kern, Vitest `shared-dom`): Dokument mit allen Runtime-Nodes der Variante `document` ohne Port laden → kein Fehler; `view.dom` enthält für `calloutComponent`, `codeBlock`, `imageComponent`, `image`, `mention` jeweils das `renderHTML`-Element (z. B. `div[data-block-type="callout-component"]`, `image-component`, `mention-component`).

### 3.5 Angular-Bindung (`ED/angular-binding`)

#### 3.5.1 DOM-Vertrag (Referenz: `@tiptap/react` 2.26.1, verifiziert in S5 mit `capture-nodeview-dom.ts`)

| Baustein | DOM im Original | Angular-Nachbildung |
|---|---|---|
| `EditorContent` | `<div>` (mit durchgereichten Props, z. B. `id`), darin `editor.view.dom` (`div.ProseMirror` mit `CoreEditorProps.attributes.class` und den von ProseMirror/Tiptap gesetzten Attributen) | `div[plEdEditorContent]` wie `EditorContent.init()` (`@tiptap/react` 2.26.1 `src/EditorContent.tsx` Z. 123–163): verschiebt `editor.options.element.childNodes` in den Host, `editor.setOptions({ element: host })`, danach **`editor.createNodeViews()`** (NodeViews werden einmal im eingehängten DOM neu erzeugt – gleiche Anzahl Mount-Zyklen und korrekte Breitenmessung, z. B. Bild-Erstgröße); beim Zerstören wie `componentWillUnmount`: `view.setProps({ nodeViews: {} })`, Kindknoten in ein neues `div` verschieben, `setOptions({ element })` |
| NodeView-Außenelement | `div` (Block) bzw. `span` (Inline) mit Klassen `react-renderer node-<typ>` (+ `className`-Option) | `AngularNodeView` erzeugt dasselbe Element mit denselben Klassen (Klassenname `react-renderer` bleibt bewusst – CSS und DOM-Parität) |
| `NodeViewWrapper` | Element (`as`, Default `div`) mit `data-node-view-wrapper=""`, `style="white-space: normal;"` + Props; `onDragStart` → `nodeViewContext.onDragStart` | Host-Element der NodeView-Komponente (`hostElement`), von `AngularNodeView` mit Attribut und Style erzeugt (§5.3); `dragstart`-Listener ruft `onDragStart`; die Komponente setzt nur ihre Klassen per Host-Binding |
| `NodeViewContent` | Element (`as`, Default `div`) mit `data-node-view-content=""`, `style="white-space: pre-wrap;"`; darin das `contentDOM` | `[plEdNodeViewContent]`-Direktive (Attribut `as` entfällt – das Element im Template bestimmt den Tag); verschiebt `contentDOM` hinein |
| `contentDOM` | `div`/`span` (bzw. `contentDOMElementTag`) mit `data-node-view-content-react=""` **und** `data-node-view-wrapper=""` sowie `style="white-space: inherit;"` (geprüft: `@tiptap/react` 2.26.1 `src/ReactNodeViewRenderer.tsx` Z. 77–89; `nodeViewContentRef` entfernt `data-node-view-wrapper` nur vom **NodeViewContent**-Element, nicht vom `contentDOM`) | identisch erzeugt (beide Attribute, Reihenfolge `data-node-view-content-react`, `data-node-view-wrapper`) |
| Drag-Handle in NodeView | Element mit `data-drag-handle` | `[plEdNodeViewDragHandle]` setzt `data-drag-handle=""` |
| Selektion | `selectNode()`/`deselectNode()` setzen Prop `selected` **und** die Klasse `ProseMirror-selectednode` am Außenelement (`renderer.element`); zusätzlich ruft `handleSelectionUpdate` (Listener `selectionUpdate`) `selectNode()`, sobald eine **Bereichs**-Selektion den Node vollständig umschließt (`from <= pos && to >= pos + nodeSize`), sonst `deselectNode()` – jeweils nur bei Zustandswechsel | identisch (§5.3): `selectNode()`/`deselectNode()` setzen Input und Klasse; `handleSelectionUpdate` ruft dieselben Methoden mit derselben Wechsel-Prüfung |
| `ReactRenderer` (Popups/Widgets) | `div.react-renderer` (+ `className`), Inhalt = Komponente; Element wird vom Aufrufer platziert (`document.body` bzw. Widget-Decoration) | `AngularRenderer` erzeugt `div.react-renderer` als `hostElement`, Komponente mit Attribut-Selektor; `updateProps()` → `setInput()` je Feld |
| `BubbleMenu` | `<div style="visibility: hidden">` + `className`, tippy verschiebt es in `div[data-tippy-root] > div.tippy-box > div.tippy-content` | `div[plEdBubbleMenu]` registriert `BubbleMenuPlugin` mit `element` = Host, `pluginKey`, `shouldShow`, `tippyOptions` (Werte A12 §2.11) |

#### 3.5.2 Ereignisse und Lebenszyklus der `AngularNodeView`

| Phase | Tiptap-Hook | Verhalten |
|---|---|---|
| Erzeugen | `mount()` (wird vom **Basiskonstruktor** `NodeView` aufgerufen, `@tiptap/core` 2.27.3 `src/NodeView.ts` Z. 55 – deshalb keine Feld-Initialisierer in der Unterklasse, §5.3) | Außenelement + Wrapper-Host erzeugen; `createComponent(component, { environmentInjector, elementInjector, hostElement: wrapper })`; Inputs `editor`, `node`, `decorations`, `innerDecorations`, `view`, `selected=false`, `extension`, `HTMLAttributes`, `getPos`, `updateAttributes`, `deleteNode` setzen; `appRef.attachView(ref.hostView)`; `contentDOM` vorbereiten (nicht bei Leaf-Nodes) |
| `dom` / `contentDOM` | Getter | Außenelement bzw. `contentDOM` (nur, wenn die Komponente ein `[plEdNodeViewContent]` besitzt; sonst `null`, wie React bei fehlendem `NodeViewContent`) |
| Aktualisieren | `update(node, decorations, innerDecorations)` | wie `ReactNodeView.update`: falscher Typ → `false`; `options.update`-Callback falls gesetzt; sonst Inputs neu setzen, `true` |
| Selektion | `selectNode()`/`deselectNode()`, Listener `selectionUpdate` | Input `selected` setzen **und** Klasse `ProseMirror-selectednode` am Außenelement setzen/entfernen; `handleSelectionUpdate` ruft beide nur bei Zustandswechsel (wie `ReactNodeView`) |
| Events | `stopEvent`, `ignoreMutation` | geerbt aus `NodeView` (`@tiptap/core`) – identische Semantik zu React (gleiche Basisklasse) |
| Zerstören | `destroy()` | `appRef.detachView`, `ref.destroy()`, Listener (`selectionUpdate`) abmelden |

#### 3.5.3 `editorState()`

`editorState<T>(editor: Signal<Editor | null>, selector: (ctx: { editor: Editor }) => T, equal?: (a: T, b: T) => boolean): Signal<T | undefined>` – registriert `editor.on("transaction", …)` und schreibt das Ergebnis in ein `signal` (mit `equal`, **Default `deepEqual` aus `fast-deep-equal/es6`** wie `useEditorState` in `@tiptap/react` 2.26.1); Abmeldung über `DestroyRef`. Ersetzt jede Nutzung von `useEditorState` (Bubble-Menü-Aktivzustände, Upload-Status, Assetliste in `EditorInstance`).

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
3. **`value`-Sync** (`effect` auf `value`, `editor`, `id`): wenn `value != null`, Editor nicht zerstört und `!editor.storage.utility.uploadInProgress` → in `try { … } catch (error) { console.error("Error syncing editor content with external value:", error) }`: `editor.commands.setContent(value, false, { preserveWhitespace: true })`, danach – falls `editor.state.selection` existiert – `setTextSelection(min(editor.state.selection.from, doc.content.size - 1))`, wobei `selection.from` **nach** `setContent` gelesen wird (wie `use-editor.ts`; nicht die Position vor dem Ersetzen).
4. **Upload-Status**: `effect` auf `fileHandler().assetsUploadStatus` → `editor.commands.updateAssetsUploadStatus(status)`. Das Signal feuert nur, wenn die Hülle bei jeder Fortschrittsänderung ein **neues** `fileHandler`-Objekt liefert (im Original erzwingt das das MobX-Re-Render); die Web-Hülle bildet `fileHandler` deshalb als `computed(() => editorConfig.getEditorFileHandlers({ … }))`, das `EditorAssetStore.assetsUploadPercentage()` liest (§3.14).
5. **Assetliste**: `editorState(editor, ({editor}) => editor.storage.utility.assetsList)` → bei Änderung `editorAssetChange.emit`.
6. **Ref-API**: `ref.set(getEditorRefHelpers({ editor, getEditorMetaData, provider }))` nach `onCreate`, `null` nach `onDestroy`.
7. **Zerstören** über `DestroyRef`: `editor.destroy()`, alle Listener abmelden.

### 3.8 `EditorRefApi` und Titel-Ref

Die Implementierung `getEditorRefHelpers()` (`ED/core/src/helpers/editor-ref.ts`) wird 1:1 übernommen; alle Methoden aus A12 §2.4 (`blur`, `clearEditor`, `createSelectionAtCursorPosition`, `getDocument`, `getDocumentInfo`, `getHeadings`, `getMarkDown`, `copyMarkdownToClipboard`, `getSelectedText`, `insertText`, `isAnyDropbarOpen`, `isEditorReadyToDiscard`, `isMenuItemActive`, `executeMenuItemCommand`, `emitRealTimeUpdate`, `listenToRealTimeUpdate`, `onDocumentInfoChange`, `onHeadingChange`, `onStateChange`, `focus`, `undo`, `redo`, `getCoordsFromPos`, `getCurrentCursorPosition`, `getAttributesWithExtendedMark`, `scrollSummary`, `scrollToNodeViaDOMCoordinates`, `setEditorValue`, `setEditorValueAtCursorPosition`, `setFocusAtPosition`, `setProviderDocument`) bleiben in Name, Signatur und Verhalten gleich. Konsumenten erhalten sie über `viewChild.required(PlEdRichTextEditor).ref()`. `EditorTitleRefApi` (`use-title-editor.ts`) liefert `PlEdCollaborativeDocumentEditor.titleRefApi()`.

### 3.9 Menüs und Overlays

#### 3.9.1 Floating-Infrastruktur (`ED/components/src/floating/`, D10-ADR-07)

| Original (`@floating-ui/react` 0.27.20) | Ziel | Verhalten (1:1) |
|---|---|---|
| `FloatingPortal` | `PlEdFloatingPortal` (Strukturdirektive `*plEdFloatingPortal`) | erzeugt beim ersten Gebrauch `div#floating-ui-<n>[data-floating-ui-portal]` als Kind von `document.body` und rendert den Inhalt dort; Entfernen beim Zerstören. ID-Zählung wie Floating UI (`useId`), die DOM-Normalisierung nummeriert IDs ohnehin um (D09 N4) |
| `FloatingOverlay` (`lockScroll`) | `div[plEdFloatingOverlay]` mit Input `lockScroll` | `position: fixed; inset: 0; overflow: auto` (Inline-Style per CSSOM wie Original), Klassen des Aufrufers (`z-[99]`); bei `lockScroll`: `body` erhält `overflow: hidden` + `padding-right` = Scrollbar-Breite und Attribut `data-floating-ui-scroll-lock` (Zähler für verschachtelte Overlays); ⚠ Attributfolge im S5-DOM-Golden bestätigen |
| `useFloating` + `autoUpdate` + Middleware | `createFloatingMenu(options)` → `{ reference, floating, open: WritableSignal<boolean>, styles: Signal<Record<string,string>>, destroy() }` | `computePosition(reference, floating, { placement, strategy, middleware })` in `autoUpdate`; Optionen je Aufrufer aus A12 §2.11–§2.15 (z. B. Bubble-Dropdowns `bottom-start`, `flip({ fallbackPlacements: ["top-start","bottom-start","top-end","bottom-end"] })`, `shift({ padding: 8 })`) |
| `useClick`, `useDismiss`, `useRole` | in `createFloatingMenu` integriert | Klick toggelt; Outside-Press (pointerdown außerhalb Referenz/Floating) und `Escape` schließen; ARIA wie `useRole('dialog')`: Referenz `aria-haspopup="dialog"`, `aria-expanded`, `aria-controls`; Floating `role="dialog"`, `id` |
| `helpers/floating-ui.ts` `updateFloatingUIFloaterPosition` | 1:1 im Kern | Suggestion-Menüs: Element an `document.body`, `fixed`, `bottom-start`, `shift()`, `flip()`, `width: max-content` |

**Z-Index-Schichten** (A12 §2.23, unverändert als Klassen im Markup): Bubble-Menü (tippy) 9, Tabellen-Insert-Buttons 9, AI-Handle 5, Bild-Upload-Status/-Toolbar/Tabellen-Handles 20, Vollbild-Bild 50, Overlay 99, Dropdowns/Popover 100.

**Globale DOM-IDs** (A12 §5.7 Nr. 5) bleiben exakt: `#editor-side-menu`, `#drag-handle`, `#ai-handle`, `#slash-command`, `#editor-portal`, `#page-content-container`, `#page-toolbar-container`, `#editor-container-{id}`, `#editor-image-block-{id}`, `#item-{s}-{i}`, `#mention-item-{s}-{i}`. Mehrere Editoren auf einer Seite teilen sie wie im Original (bekanntes Verhalten, nicht korrigiert).

#### 3.9.2 Slash-Commands (CE-PAGE-024)

| Teil | Ort | Umsetzung |
|---|---|---|
| Extension `slash-command` (Suggestion, Trigger `/`, `allow`: nicht im Code-Block) | `ED/core/src/extensions/slash-commands/root.ts` | 1:1; Renderer über `uiRender(editor, "slash-commands-menu", props)`; `onKeyDown` delegiert an `handle.ref.onKeyDown` (`CommandListInstance`), Escape schließt; `DROPDOWN_NAVIGATION_KEYS` |
| Eintragsliste (17 + 9 + 9 Einträge, A12 §2.10) | `ED/core/src/extensions/slash-commands/command-items-list.ts` | 1:1, Icons `PlIconDef`; **E1 korrigiert**: „Default background“ → `unsetBackgroundColor()` (FE-ED-02); Einsortierung `additionalOptions` per `section` + `pushAfter` 1:1 |
| Filter | dto. | `title`/`description` enthält `q` oder ein `searchTerm` enthält `q`; leere Sektionen entfallen; alle leer → kein Menü |
| Menü | `PlEdSlashCommandsMenu` (`ED/components/src/extensions/slash-commands/command-menu.component.ts`) | `div[plEdFloatingOverlay].z-[99]` (`lockScroll`) + `div#slash-command.relative.max-h-80.min-w-[12rem].space-y-2.overflow-y-auto.rounded-md.border-[0.5px].border-strong.bg-surface-1.px-2.py-2.5.shadow-raised-200` (z 100); Sektion-Titel `h6.text-11.font-semibold.text-tertiary`; Auswahlzustand `selectedIndex` als `{ section, item }`-Signal; Scroll des aktiven Eintrags in den sichtbaren Bereich wie Original (`useLayoutEffect` → `afterRenderEffect`) |
| Eintrag | `PlEdSlashCommandMenuItem` (`button[plEdSlashCommandMenuItem]#item-{s}-{i}`) | Klassen 1:1, Icon-Box `grid size-5 place-items-center` mit `iconContainerStyle` (CSSOM), Titel mit Treffer-Hervorhebung (`span.font-medium.text-primary` am ersten Substring-Treffer), optional `badge` |
| Globale Tastatur (E10) | `PlEdSlashCommandsMenu` | Original registriert zusätzlich einen `document`-`keydown`; das Verhalten wird **übernommen**, S5 prüft, ob dadurch Doppelschritte entstehen; falls ja: Korrektur `FE-ED-05` (nur Suggestion-Navigation) |

#### 3.9.3 Bubble-Menü (CE-PAGE-025)

- Direktive `div[plEdBubbleMenu]` (Bindung) mit Inputs `editor`, `pluginKey` (Default `"bubbleMenu"`), `shouldShow`, `tippyOptions`, `updateDelay`; registriert `BubbleMenuPlugin` aus `@tiptap/extension-bubble-menu` 2.26.3 beim Erzeugen, `unregisterPlugin` beim Zerstören (Muster React-`BubbleMenu`).
- `PlEdEditorBubbleMenu` (`ED/components/src/components/menus/bubble-menu/root.component.ts`): `tippyOptions = { moveTransition: "transform 0.15s ease-out", duration: [300, 0], zIndex: 9, onShow, onHide, onHidden }` (A12 §2.11); `onShow` setzt `editor.storage.link.isBubbleMenuOpen = true` und `addActiveDropbarExtension("bubble-menu")`, `onHide`/`onHidden` setzen zurück (`removeActiveDropbarExtension` per `setTimeout(0)`); `shouldShow` = false bei leerer Selektion, nicht editierbar, `image`/`imageComponent` aktiv, `NodeSelection`, `CellSelection`, laufender Maus-Drag (`isSelecting` über `mousedown`/`mousemove`/`mouseup` am `view.dom`).
- Gruppen in Reihenfolge: `PlEdBubbleMenuNodeSelector` (Name des **letzten** aktiven Items bzw. „Multiple“), `PlEdBubbleMenuLinkSelector` (nicht bei Code; Validierung `isValidHttpUrl`, Fehlertext „Please enter a valid URL“), `PlEdBubbleMenuColorSelector` (nicht bei Code; „Text colors“/„Background colors“, 8 + Reset `Ban`), Formatierung (Bold/Italic/Underline/Strikethrough bzw. nur „Code“), `PlEdBubbleMenuAlignmentSelector` (nicht bei Code). Container- und Item-Klassen 1:1 (A12 §2.11). Aktivzustände über `editorState()` (§3.5.3) mit den Prädikaten aus `menu-items.ts`.

#### 3.9.4 Side-Menü, Drag-Handle, Block-Menü (CE-PAGE-026)

- `SideMenuExtension`, `plugins/drag-handle.ts`, `plugins/ai-handle.ts` sind **Vanilla-DOM** und werden 1:1 übernommen (Positionierungsformeln, `elementsFromPoint`-Offset `+50+24`, Selektorliste `generalSelectors`, Autoscroll-Konstanten, Listen-Drop-Umbau, A12 §3.14). Erweiterung der Selektorliste durch Pakete über die Block-Registry (`sideMenuSelectors`, §6.2) – CE: keine.
- `PlEdBlockMenu` (`ED/components/src/components/menus/block-menu.component.ts`): öffnet bei `click`/`contextmenu` auf `#drag-handle`, schließt bei Outside-Click, `Escape`, `scroll` (capture); Position `left-start`, `offset({ crossAxis: -10 })`, `flip()`, `shift()`; Portal `PlEdFloatingPortal`; Einblend-Animation nach 50 ms (`scale-75 opacity-0` → `scale-100 opacity-100`, `origin-top-right transition-all duration-300`, `cubic-bezier(0.16, 1, 0.3, 1)`); Optionen aus `getBlockMenuOptions()` (Kern): `delete`, `duplicate` (nicht für Bilder), `table-full-width` („Fit to width“, nur in Tabellen); registriert `editorSideMenu` als aktive Dropbar.

#### 3.9.5 Link-Ansicht (CE-PAGE-036)

`PlEdLinkViewContainer` (Port `link-view-container.tsx`): `mouseover` auf `a` im Container (nicht bei offenem Bubble-Menü, nicht auf Touch) öffnet `PlEdLinkView` mit Floating-Position `bottom-start`, `flip(top,bottom)`, `shift(5)`, `hide()`, z 100; Schließen 400 ms nach Verlassen. Ansichten `PlEdLinkPreview` (URL > 40 Zeichen gekürzt, Copy, Edit, Unlink) und `PlEdLinkEditView` (Felder „URL“/„Text“, Enter validiert, Unmount ohne Submit bei leerer Initial-URL entfernt den Link). **Andockpunkt F1/F2:** Vor dem Rendern von `PlEdLinkPreview` fragt der Container `INTEGRATION_LINK_PREVIEWS` (D08 §6.1, Token aus `EXT`, über die Web-Hülle als Input `linkPreviewProviders` durchgereicht); CE: leer → Original-Ansicht.

### 3.10 NodeViews

| NodeView (Node) | Angular-Komponente(n) | Wrapper-Klassen (1:1) | Inhalt / Verhalten | Abhängigkeiten |
|---|---|---|---|---|
| Callout (`calloutComponent`) | `PlEdCalloutBlock` (`[plEdCalloutBlock]`), `PlEdCalloutLogoSelector`, `PlEdCalloutColorSelector` | `editor-callout-component group/callout-node relative my-2 flex items-start gap-4 rounded-lg bg-layer-3 p-4 break-words text-primary transition-colors duration-500`; `background-color` = `COLORS_LIST[data-background].backgroundColor` (CSSOM) | Logo-Button `grid size-8 place-items-center rounded-lg text-primary` (+ Hover bei editierbar), `PlBlkEmojiPicker` (`closeOnSelect`, `searchDisabled`, `defaultOpen` = Logo-Typ, `defaultIconColor`); Auswahl Emoji → `data-emoji-unicode` (Dezimal-String), `data-emoji-url` = `undefined`; Icon → `data-icon-name`, `data-icon-color`; `data-logo-in-use`; Persistenz `localStorage` `editor-calloutComponent-logo` (über `sanitizeHTML`) und `editor-calloutComponent-background`; Farbwahl oben rechts `absolute top-2 right-2 z-10`, nur Hover/offen; Inhalt `div[plEdNodeViewContent].w-full.break-words`; Tastatur (Backspace am Anfang, ArrowUp/Down) im Kern | `PlBlkEmojiPicker`, `PlBlkLogo` (D09, I1), `svg[plSvgIcon]` |
| Code-Block (`codeBlock`) | `PlEdCodeBlockNodeView` (`[plEdCodeBlockNodeView]`) | `code-block group/code relative` | Kopier-Button `group/button absolute top-2 right-2 z-10 hidden size-8 … group-hover/code:flex` mit `[plTooltip]="'Copy code'"`; nach Kopieren 1 s `TickOutline` + `bg-success-subtle…`; `pre.my-2.rounded-lg.bg-layer-3.p-4.text-primary > code[plEdNodeViewContent].whitespace-pre-wrap`; Highlighting über Kern-Plugin `lowlight` (Decorations) | `PlTooltip` (D09) |
| Bild (`imageComponent`, Legacy `image`) | `PlEdCustomImageNodeView` (`[plEdCustomImageNodeView]`) → `PlEdImageUploader` \| `PlEdImageBlock` (+ `PlEdImageUploadStatus`, `PlEdImageToolbarRoot` mit `PlEdImageDownloadAction`, `PlEdImageAlignmentAction`, `PlEdImageFullScreenAction` → `PlEdImageFullScreenModal`) | Klassen A12 §2.14 | Zustandslogik aus `node-view.tsx` 1:1 (Quelle laden über `fileHandler.getAssetSrc`, Fehler → einmal `restore` + Neuladen, Duplikation mit automatischem Retry); Erstgröße bei `width === "35%"` → `max(editorWidth*0.35, 100)` px, Seitenverhältnis speichern; Resize-Griff (`MIN_SIZE` 100 px, Ecke je Ausrichtung); Vollbild als Portal nach `#editor-portal` (Fallback `document.body` + `console.warn`), Zoom `[0.5,1,1.5,2]`, Ctrl/Meta+Wheel, Pan, Tasten `Esc`/`+`/`=`/`-`; Upload-Prozent animiert 200 ms easeOutCubic aus `utility.assetsUploadStatus[nodeId]` | `PlTooltip`, `svg[plSvgIcon]`, `FileUploader` (§3.14) |
| Mention (`mention`) | `PlEdMentionNodeView` (`[plEdMentionNodeView]`) | `mention-component inline w-fit` (Außenelement `span.react-renderer.node-mention`) | rendert `extension.options.renderComponent({ entity_identifier, entity_name })` – Rückgabe `TEditorRenderable` → `NgComponentOutlet` mit `inputs`. **Regel:** `NgComponentOutlet` erzeugt das Host-Element aus dem Selektor (Attribut-Selektor ohne Tag → `div`); Render-Komponenten aus `TEditorRenderable` sind deshalb **Element-Selektoren mit `data-pl-host`** (`display: contents`, von der DOM-Normalisierung N3 ausgepackt), weil das Original-`EditorMentionsRoot` kein eigenes Element erzeugt; das innere Element (`div.not-prose.inline…` von `EditorUserMention`) trägt die Attribut-Komponente | Hüllen-Komponenten §3.11 |
| Tabelle (`table`) | **keine** Angular-NodeView: `TableView` (Vanilla, `ED/core/src/extensions/table/table/table-view.ts`) | `div.table-wrapper.editor-full-width-block.horizontal-scrollbar.scrollbar-sm > table > colgroup + tbody` | `updateColumnsOnResize`, `ignoreMutation() → true`; Handles/Dropdowns siehe §3.13 | `helpers/dom-builder.ts` |
| Task-Item (`taskItem`) | **keine**: Tiptap-Default-NodeView (Vanilla) | `li[data-type=taskItem][data-checked]` mit `label > input[type=checkbox] + span`, `div` | 1:1 durch `@tiptap/extension-task-item` 2.26.1 | – |
| Work-Item-Embed (`issue-embed-component`) | in der CE **nicht** registriert (A12 §2.5.1 Nr. 23) | – | nur Schema (`server-document`); Paket D6 liefert die NodeView über `EDITOR_BLOCKS` | – |

**Gemeinsame NodeView-Regeln:** Inputs heißen wie die React-Props (`node`, `editor`, `extension`, `getPos`, `updateAttributes`, `deleteNode`, `selected`, `decorations`, `HTMLAttributes`); `node` ist ein Signal, das bei jedem `update()` ersetzt wird; Zustände (`useState`) werden `signal`s; `useEffect`/`useLayoutEffect` → `effect`/`afterRenderEffect` mit gleicher Abhängigkeitsmenge; `key={attrs.id}` (Neuaufbau bei ID-Wechsel) → `AngularNodeView.update()` zerstört und erzeugt die Komponente neu, wenn sich `node.attrs.id` ändert.

### 3.11 Mentions (CE-PAGE-034, CE-WI-044, CE-SPACE-030)

| Teil | Ort | Umsetzung |
|---|---|---|
| Node-Schema `mention` (`mention-component`, Attribute `id`, `entity_identifier`, `entity_name`, `renderText`) | `ED/core/src/extensions/mentions/extension-config.ts` | 1:1 (Schema-Freeze; HTML-Vertrag mit `page_transaction`, A12 §4.2) |
| Suggestion (`@`, `allowSpaces: true`) | `ED/core/src/extensions/mentions/utils.ts` | 1:1; nur wenn `searchCallback` vorhanden; Renderer `mentions-list-dropdown` |
| Dropdown | `PlEdMentionsListDropdown` | Suche debounced 300 ms; Zustände „Loading...“, „No results“; Sektionen `{key, title, items}`; Item `button#mention-item-{s}-{i}`; Container `w-[14rem] max-h-80`; Auswahl → `command({ ...item, id: uuidv4() })`; aktive Dropbar `mention`; Icon eines Items ist `TEditorRenderable` |
| `TMentionHandler` | `ED/core/src/types/mention.ts` | `renderComponent(props) → TEditorRenderable`, `searchCallback?(query) → Promise<TMentionSection[]>`, `getMentionedEntityDetails?(id) → { display_name }` |
| Web-Hülle | `FE/libs/web/core/editor/embeds/mentions/{root,user}.component.ts`, `EditorMentionService` (Port `use-editor-mention.tsx`; Vertrag D11 §3.5, Ort/Service D11 §3.12: `FE/libs/web/core/editor/editor-mention.service.ts`, 17 ABG-121) | Endpunkt SR-03 `GET /api/workspaces/{slug}/entity-search/` (D11); `searchEntity({ count: 5, query_type: EDITOR_MENTION_TYPES-Werte (CE `["user_mention"]`), query, project_id?, issue_id? })` → Sektion `users` „Users“ mit Avatar-Icon; Anzeige `@{display_name}` mit Hover-Karte (Avatar, Name, Rolle, Link `/{workspaceSlug}/profile/{id}`), eigener Nutzer `bg-label-yellow-bg text-label-yellow-text`, sonst `bg-accent-subtle-active text-accent-primary`, unbekannt „@suspended user“ |
| Space-Hülle | `FE/libs/space/editor/embeds/mentions/{root,user}.component.ts` | „@deactivated user“, eigene Mentions hervorgehoben (CE-SPACE-030) |
| Erweiterung | `EDITOR_MENTION_TYPES` (Multi) + Sektionen-/Render-Provider (`EditorMentionSectionProvider`, §6.1) | CE: nur `user_mention`; H1 (App-Mentions), D6 (Work Items, Projekte, Cycles, Module, Pages) |

### 3.12 Emoji (CE-PAGE-035, offline)

- **Daten:** `emojis`/`gitHubEmojis`/`emojiToShortcode`/`shortcodeToEmoji` aus `@tiptap/extension-emoji` 2.26.1 (Daten aus `emojibase-data` 15.3.2 im JS-Bundle). Der Plane-Fork `ED/core/src/extensions/emoji/emoji.ts` (452 Zeilen) bleibt 1:1: `:shortcode:`-Input/Paste, Emoticons (`enableEmoticons: true`), Unicode→Node per `appendTransaction` (nicht in Code), Doppelklick selektiert, Storage `emojis`, `isSupported`, `forceOpen`.
- **Unterstützungsprüfung:** `is-emoji-supported` 0.0.5 (Canvas-Messung im Browser, keine Netzanfrage).
- **Suggestion:** `ED/core/src/extensions/emoji/suggestion.ts` (`:`, `allowSpaces: false`, `customFindSuggestionMatch` über Mark-Grenzen), Default-Liste `+1, -1, smile, orange_heart, eyes` nur bei `forceOpen` (Slash „Emoji“), Filter Präfix auf `shortcodes`/`tags`, max. 5, Einblenden nach 50 ms; Dropdown `PlEdEmojisListDropdown` (Item: Emoji `size-5 text-14` + `:{name}:` `font-medium`, „No emojis found“); nicht auf Touch.
- **Callout-Logo-Picker:** `PlBlkEmojiPicker` (D09 §3.8.2) mit Daten aus `FE/apps/{web,space}/src/assets/emojibase/15.3.2/<locale>/` (ABG-029); keine Bild-CDN.
- **Callout-Default-URL:** unverändert als Attributwert (D10-ADR-12). Airgap-Scan-Allowlist-Einträge in `FE/tools/ci/airgap-allowlist.json` (gelesen von `airgap-scan.mjs`, D08 AK-D08-03), jeweils mit Begründung und maximaler Trefferzahl, damit neue Literale auffallen:
  1. `{ id: "ED-AIRGAP-01", source: "ED/core/src/extensions/callout/utils.ts", literal: "https://cdn.jsdelivr.net/npm/emoji-datasource-apple/img/apple/64/1f4a1.png", maxHits: 1, reason: "Schema-Default data-emoji-url, wird nie geladen (D10-ADR-12)" }`;
  2. `{ id: "ED-AIRGAP-02", source: "node_modules/@tiptap/extension-emoji@2.26.1", prefix: "https://cdn.jsdelivr.net/npm/emoji-datasource-apple/img/apple/64/", maxHits: 1814, reason: "fallbackImage-Daten des Emoji-Datensatzes; EmojiExtension entfernt fallbackImage zur Laufzeit (ED0/extensions/emoji/extension.ts Z. 33–35)" }`;
  3. `{ id: "ED-AIRGAP-03", source: "node_modules/@tiptap/extension-emoji@2.26.1", prefix: "https://github.githubassets.com/images/icons/emoji/", maxHits: 19, reason: "gitHubCustomEmojis ohne Unicode; von EmojiExtension herausgefiltert" }`.
  Gewertet werden die Einträge nur, wenn der Scan Daten-Literale meldet (D08 AK-D08-03 prüft „ladbare“ Kontexte); Zähler gegen die gebauten Chunks (`dist/{web,space}/browser/*.js`).
- **Emoji-Glyphen:** System-Emoji-Font wie Original (D09 §3.8.1); Test-Container mit gepinnter `Noto Color Emoji`.

### 3.13 Tabellen (CE-PAGE-031)

Kern 1:1 (`ED/core/src/extensions/table/**`: eigene `Table`/`TableRow`/`TableHeader`/`TableCell`, Utilities, Plugins `tableDragState`, `table-insert`, `table-cell-selection-outline`, `tableEditing`/`columnResizing` aus `prosemirror-tables` 1.7.1, Spalten-/Zeilen-Handle-Plugins). Neu in Angular sind nur die vier React-Widgets:

| Original | Angular | Details (1:1, A12 §2.13) |
|---|---|---|
| `drag-handles/column/drag-handle.tsx` | `PlEdTableColumnDragHandle` (über `uiRender("table-column-drag-handle")` in Widget-Decoration) | `div.table-col-handle-container.absolute.top-0.left-0.z-20.flex.w-full.-translate-y-1/2` → Button `rounded-sm border border-strong-1 bg-layer-1 px-1` mit `MoreHorizontalOutline size-4`; MouseDown selektiert Spalte + startet Drag (Marker/Preview aus `marker-utils.ts`), Klick öffnet Dropdown; jede Taste schließt das offene Dropdown (`preventDefault`) |
| `drag-handles/row/drag-handle.tsx` | `PlEdTableRowDragHandle` | `table-row-handle-container … h-full -translate-x-1/2`, Icon 90° gedreht |
| `drag-handles/column/dropdown.tsx`, `row/dropdown.tsx` | `PlEdTableColumnDropdown`, `PlEdTableRowDropdown` | Einträge und Reihenfolge A12 §2.13; Container `max-h-[90vh] w-[12rem] … shadow-raised-200` z 100 über `PlEdFloatingPortal` + `PlEdFloatingOverlay` z 99; aktive Dropbar `table` |
| `drag-handles/color-selector.tsx` | `PlEdTableDragHandleColorSelector` | `PlCollapsible` (defaultOpen, `PaletteOutline`, Trigger „Color“), 8 Kacheln → `updateAttributes("tableCell", { background: color.backgroundColor })` (speichert CSS-Variable, E19 beibehalten), Reset `DeactivatedOutline` → `null` |

Insert-Buttons (`button.table-column-insert-button`, `button.table-row-insert-button`) und Drag-Marker sind Vanilla-DOM im Kern (`insert-handlers/utils.ts`) und bleiben unverändert.

### 3.14 Bilder und Assets (CE-PAGE-032, CE-UIX-009, CE-OPS-013)

- **Kontrakt `TFileHandler`** (Kern, 1:1): `assetsUploadStatus`, `cancel`, `checkIfAssetExists`, `delete`, `getAssetDownloadSrc`, `getAssetSrc`, `restore`, `upload(blockId, file)`, `duplicate(assetId)`, `validation.maxFileSize`, `& TExtendedFileHandler` (Paket-Andockpunkt V).
- **Web-Implementierung** `EditorConfigService.getEditorFileHandlers({ projectId, uploadFile, duplicateFile, workspaceId, workspaceSlug })` (Port `WEB/hooks/editor/use-editor-config.ts`, Ziel `FE/libs/web/core/editor/editor-config.service.ts`): `http…`-Quellen → Alt-Workspace-Assets (`deleteOldWorkspaceAsset`, `restoreOldEditorAsset`), sonst V2-Assets über `getEditorAssetSrc`/`getEditorAssetDownloadSrc` (`FE/libs/shared/utils/src/editor/common.ts`); `assetsUploadStatus` = `EditorAssetStore.assetsUploadPercentage` (D08 Nr. 8, `FE/libs/web/core/state/editor/asset.store.ts`); die Hülle reicht `fileHandler` als `computed(...)` durch, das dieses Signal liest, damit jede Fortschrittsänderung ein neues Objekt erzeugt (§3.7 Nr. 4); `maxFileSize` aus Instanz-Konfiguration; Beiträge `getExtendedEditorFileHandlers()` (S15) über `EDITOR_EXTENSIONS.fileHandlers` (CE leer).
- **Space-Implementierung** (`FE/libs/space/editor/helpers/editor.helper.ts`, Port `SPC/helpers/editor.helper.ts`): Quellen `/api/public/assets/v2/anchor/{anchor}/{assetId}/`; `duplicate` liefert dieselbe ID.
- **Upload-Ablauf** (A12 §3.10) im Kern (`plugins/drop.ts`, `plugins/file/*`, `helpers/file.ts`) und in `FileUploader` (Port `use-file-upload.ts`, `ED/components/src/services/file-upload.ts`): `uploadInProgress=true`, lokale Vorschau `FileReader.readAsDataURL` (unscharf), `status: uploading` → `upload()` → `src`, `status: uploaded`, Cursor-Korrektur, Mehrfachdateien (`uploadFirstFileAndInsertRemaining`). Validierungsfehler über `window.alert` mit den Original-Texten („Invalid file type.“, „File size too large. Please select a file smaller than {n}MB.“, „No file selected. Please select a file to upload.“) – unverändert.
- **Drop-Zone:** Direktive `[plEdDropZone]` (Port `useDropZone`) mit `dragover`/`dragleave`/`drop`, Zustand „Drop image here“.

### 3.15 Kollaboration im Client (CE-PAGE-013, CE-RT-002, -003, -004)

#### 3.15.1 Bausteine

| Baustein | Ort | Aufgabe |
|---|---|---|
| `CollaborationProviderFactory` | `ED/collaboration/src/collaboration-provider.factory.ts` | `create({ name, url, token, document, onAuthenticationFailed, onConnect, onStatus, onSynced, onClose, onStateless })` → `HocuspocusProvider`; zusätzlich `createIndexedDbPersistence(name, document)` → `IndexeddbPersistence` (DB-Name = `docId`) |
| `CollaborationSession` | `ED/collaboration/src/collaboration-session.ts` | Stage-Maschine aus `use-yjs-setup.ts` (A12 §3.2, Diagramm) mit Signalen `stage`, `isCacheReady`, `hasCachedContent`, `isServerSynced`, `isServerDisconnected`, `isDocReady`; zusätzlich `authorizedScope` (`"read-write" \| "readonly" \| undefined`, aus `provider.authorizedScope` – gesetzt in `authenticatedHandler(scope)` vor dem Ereignis `authenticated` (ohne Parameter), 07 §3.3.6, 17 ABG-113) – die Page-Hülle setzt bei `readonly` `editable=false` (Gegenstück zu D07-ADR-05, korrigiert E3 clientseitig); Retry-Zähler (`DEFAULT_MAX_RETRIES = 3`), `pauseProvider()`, `permanentlyStopProvider()`, Visibility/`focus`-Reconnect (Throttle 1 s), `online`-Reconnect, Forced-Close-Erkennung (Codes 4000–4003, Signal `forcedCloseSignal`, `shouldConnect === false`; Original `isForcedCloseCode`: `code >= 4000 && code <= 4003`). Die von D07 zusätzlich eingeführten Codes (D07-ADR-05) sind **keine** Forced-Close-Codes: **4205** (Scope-Wechsel) → regulärer Reconnect, Zähler wird bei `onConnect`/`onSynced` wie im Original auf 0 gesetzt, danach `authorizedScope = "readonly"`; **4403** (Leserecht entzogen) → Reconnect endet mit `PermissionDenied` → `onAuthenticationFailed` → Stage `disconnected` (`auth-failed`) – kein Sonderzweig nötig; beides deckt AK-D10-14 ab |
| `provideCollaborationSession()` / Token `COLLABORATION_SESSION` | `ED/collaboration/src/collaboration-context.ts` | Ersatz `CollaborationProvider`/`useCollaboration`; Komponenten-Provider von `PlEdCollaborativeDocumentEditor` |
| `CollaborativeEditorInstance` | `ED/components/src/services/collaborative-editor-instance.ts` | Port `use-collaborative-editor.ts`: Haupt-Editor (`enableHistory: false`, `Collaboration.configure({ document, field: "default" })`, `mainEditorNavigation`), `UniqueID` mit `provider` (IDs erst nach `synced`) |

#### 3.15.2 Verhalten (1:1)

- **Token:** `JSON.stringify(user)` mit `user = { id, name, color }`; Web setzt `color = hslToHex(generateRandomColor(user.id))`, **kein** Cookie im Token (Cookie geht im WS-Upgrade mit, D01 ADR-022).
- **URL:** baut die Page-Hülle (`FE/libs/web/pages/components/pages/editor/editor-body.component.ts`): `new URL(live_base_url || location.origin)`, Protokoll `wss`/`ws`, Pfad `${live_base_path}/collaboration`, Query `documentType=project_page&projectId=…&workspaceSlug=…` (Werte aus `RUNTIME_CONFIG`, D08 §3.12).
- **Rendering:** Loader (`PlEdDocumentContentLoader`) wenn `(isCacheReady && !hasCachedContent && !isServerSynced)` oder `(isFetchingFallbackBinary && !hasCachedContent && isServerDisconnected)`; solange `!isDocReady` und kein Loader → Inhalt `pointer-events-none opacity-0` mit `transition-opacity duration-200`.
- **Statusweitergabe:** `serverHandler.onStateChange(state)` bei jeder Stage-Änderung; die Page-Hülle mappt `disconnected → "error"`, `synced → "synced"`, sonst `"syncing"` und startet bei `disconnected` den REST-Fallback (`PageFallbackService`, D08) über `ref.setProviderDocument()` und `ref.getDocument()`.
- **Stateless:** `emitRealTimeUpdate(action)` → `provider.sendStateless(serverEventName)`; `listenToRealTimeUpdate()` → `{ on, off }` auf Provider-Event `stateless`. Auswertung der Server-JSON-Events (`error`, `property_updated`, `force_close`, `BroadcastedEvent`) in `RealtimePageEventsService` (D08) – **E5 wird dort korrigiert** (FE-ED-03, Eigentümer D08/D07); der Editor liefert nur den Kanal.
- **Live-Cursor:** Wenn `collaboration-cursor` **nicht** in `disabledExtensions` steht, hängt `CollaborativeEditorInstance` `CollaborationCursor.configure({ provider, user: { name, color } })` an (Paket `@tiptap/extension-collaboration-cursor` 2.26.1; Cursor-Styles: das Original enthält **keine** Datei dafür (`ED0/styles/` hat genau 7 Dateien); `ED/styles/collaboration-cursor.css` ist neu, entsteht erst mit FE-ED-01 bzw. im Fachdesign von Paket D4 und wird nicht über `index.css` der CE importiert – die CE liefert nur die Extension hinter dem Flag). CE-Default: deaktiviert wie Original (`EDITOR_FLAGS`).
- **Undo/Redo:** `y-undo` aus `y-prosemirror` (über `@tiptap/extension-collaboration`), Shortcuts wie Tiptap.

### 3.16 Titel-Editor und Navigation (CE-PAGE-013, CE-PAGE-038)

`PlEdTitleEditor` (intern in `PlEdPageRenderer`) erzeugt über `TitleEditorInstance` (Port `use-title-editor.ts`) einen zweiten Tiptap-Editor auf demselben `Y.Doc` mit `TitleExtensions` (Document `content: "heading"`, Heading Level 1, Text), `Collaboration.configure({ field: "title" })`, `titleEditorNavigation`, `Placeholder` „Untitled“ (auch read-only sichtbar). DOM: `div.relative.w-full.py-3` → `PlEdEditorContainer` (`page-title-editor bg-transparent py-3 border-none`) mit Content-Klasse `no-scrollbar placeholder-placeholder w-full resize-none rounded-none border-none bg-transparent p-0 text-[2rem] leading-[2.375rem] font-bold tracking-[-2%] outline-none`. Navigation (Kern `hooks/editor-navigation.ts`, Priorität 10): Titel ArrowDown/ArrowRight/Enter → Haupt-Editor (Enter fügt Paragraph an Pos 0 ein); Haupt-Editor ArrowUp/ArrowLeft/Backspace an Pos 1 → Titel (Backspace löscht leeren ersten Paragraph).

### 3.17 Lite-Editor für Kommentare und Stickies (CE-PAGE-022, CE-WI-037, CE-HOME-010, CE-SPACE-025)

- **Variante:** `PlEdLiteTextEditor` = Core-Extensions + `EnterKeyExtension(onEnterKeyPress)` (sofern `"enter-key"` nicht deaktiviert); kein Bubble-, Slash- oder Side-Menü. Enter ruft `editorEnterKeyPress` nur, wenn `utility.activeDropbarExtensions` leer ist (Mention-/Emoji-Dropdown offen → Enter wählt aus); Shift-Enter = `first([newlineInCode, splitListItem("listItem"), splitListItem("taskItem"), createParagraphNear, liftEmptyBlock, splitBlock])`.
- **Toolbars** liegen in den Hüllen (nicht im Editor): `FE/libs/web/core/editor/lite-text/{toolbar,lite-toolbar}.component.ts` (Port `WEB/components/editor/lite-text/toolbar.tsx`, `lite-toolbar.tsx`; Varianten `full`/`lite`/`none`, `showToolbarInitially`, `isSubmitting`, `parentClassName`), Sticky-Toolbar `FE/libs/web/core/editor/sticky-editor/toolbar.component.ts`, Space-Toolbar `FE/libs/space/editor/toolbar.component.ts`. Sie nutzen `TOOLBAR_ITEMS.lite` bzw. `.sticky` (Kern) und `ref().executeMenuItemCommand()`/`isMenuItemActive()`; Aktivzustände per `ref().onStateChange()`.
- **Platzhalter:** Kommentare `t("issue.comments.placeholder")` mit `showPlaceholderOnEmpty = true` (Hülle).

### 3.18 Read-only-Rendering (CE-PAGE-021…023, CE-SPACE-024)

Es gibt wie im Original **keine** eigenen Read-only-Komponenten: Read-only = `[editable]="false"` an derselben Variante. Wirkung (A12 §1.3, alle im Kern bzw. CSS): `UniqueID.updateDocument=false`, `TrackFileDeletionPlugin` inaktiv, `CustomImage.selectable/draggable=false`, Bubble-/Block-/Side-Menü inaktiv (`view.editable`), Tabellen-Insert-Buttons entfernt, Platzhalter leer (Titel: „Untitled“ bleibt), Checkboxen `pointer-events:none`. Wechsel `editable` → Editor-Neuaufbau (D10-ADR-09). Anzeigeorte: Kommentar-Karte (`comments/card/display`), Beschreibungs-/Page-Versionen (Document-Editor), Space-Peek (Rich), archivierte/gesperrte Pages (Collaborative mit `editable=false`).

### 3.19 Markdown, Clipboard, Paste (CE-PAGE-037)

| Funktion | Ort | Umsetzung |
|---|---|---|
| Markdown-Paste | `tiptap-markdown` 0.8.10 (`html:true`, `transformCopiedText:false`, `transformPastedText:true`, `breaks:true`) | 1:1 |
| Copy (`text/plain` = Markdown, `text/html` & `text/plane-editor-html` = HTML) | `ED/core/src/plugins/markdown-clipboard.ts` | 1:1 |
| Paste aus einem Editor der Anwendung (`text/plane-editor-html`, Original „Paste aus Plane“) → `processAssetDuplication` → `view.pasteHTML` | `ED/core/src/props.ts`, `helpers/paste-asset.ts`, `helpers/asset-duplication.ts` | 1:1 |
| „Copy as Markdown“, Markdown-Export | `ref().copyMarkdownToClipboard()`, `ref().getMarkDown()` → `convertHTMLToMarkdown` (`FE/libs/shared/utils/src/editor/markdown-parser/*`, D10-ADR-20) | 1:1 |
| VS-Code-Paste → Code-Block mit Sprache; Paste in Inline-Code → Text mit `code`-Mark | `extensions/code/code-block.ts` (Plugin `codeBlockVSCodeHandlerCustom`) | 1:1 |
| URL-Paste über Selektion → Link | `extensions/custom-link/helpers/pasteHandler.ts` | 1:1 |
| Datei-Paste/-Drop → Bild-Upload | `plugins/drop.ts` | 1:1 (Attachment-Zweig leer, E23; Paket D9 über Block-Registry) |

### 3.20 Editor-CSS 1:1 (CE-I18N-010, CE-PAGE-040)

#### 3.20.1 Dateien

| Original | Ziel | Zeilen | Kategorie | Hinweis |
|---|---|---|---|---|
| `ED0/styles/index.css` | `ED/styles/index.css` | 6 | 1:1 | Importreihenfolge `variables` → `editor` → `table` → `github-dark` → `drag-drop` → `title-editor` |
| `ED0/styles/variables.css` | `ED/styles/variables.css` | 305 | 1:1 | Editor-Farben (8 Schlüssel, Light/Dark), Schrift-/Zeilenabstands-Skalen, Inhaltsbreiten 720/1152 px, Container-Queries (E18 ungültige Query bleibt) |
| `ED0/styles/editor.css` | `ED/styles/editor.css` | 508 | 1:1 | `@apply`, `--alpha()` (Tailwind 4.1-Syntax, Compiler D09-ADR-01) |
| `ED0/styles/table.css` | `ED/styles/table.css` | 211 | 1:1 | |
| `ED0/styles/drag-drop.css` | `ED/styles/drag-drop.css` | 117 | 1:1 | Selektoren `.node-imageComponent`, `.node-image` (DOM-Vertrag §3.5.1) |
| `ED0/styles/title-editor.css` | `ED/styles/title-editor.css` | 49 | 1:1 | |
| `ED0/styles/github-dark.css` | `ED/styles/github-dark.css` | 85 | 1:1 | highlight.js-Theme |
| – (Laufzeit-Injektion `@tiptap/core`) | `ED/styles/tiptap-core.css` | – | generiert | D10-ADR-13, Abweichung `FE-ED-07` (`kind: extra-css`) |

#### 3.20.2 Einbindung

Nach D09 §3.2.2: Web `styles.css` importiert `FE/libs/shared/editor/styles/index.css` an der Stelle von `@import "@plane/editor/styles"` (Zeile 2 von `WEB/styles/globals.css`), Space analog (`SPC/styles/globals.css`); Admin importiert keine Editor-Styles. `tiptap-core.css` wird als **letzter Import** von `styles.css` (Web und Space) eingebunden, **außerhalb jeder `@layer`** (ungeschichtet wie das Original-`<style>`). Begründung (geprüft): `createStyleTag()` hängt das `<style data-tiptap-style>` per `head.appendChild` ans **Ende** von `<head>`, also **hinter** die bereits geladenen App-Styles; die Reihenfolge ist relevant, weil `ED/styles/editor.css` Z. 1–4 `.ProseMirror { white-space: pre-wrap }` und Tiptap `.ProseMirror { white-space: break-spaces }` (zweite Deklaration) dieselbe Spezifität haben – im Original gewinnt `break-spaces`. Ein Import vor `index.css` würde das umkehren (andere Umbruchbehandlung von Leerzeichen am Zeilenende). S5 bestätigt per `getComputedStyle` auf `.ProseMirror` (`white-space`), `.ProseMirror-gapcursor`, `img.ProseMirror-separator` und `.tippy-box[data-state=hidden]` (Rückmeldung an D09 §3.2.2, Importliste der Web-/Space-`styles.css`).

#### 3.20.3 Regeln

1. Vendored CSS ist unveränderlich (D09-ADR-01); G-CSS prüft Selektor-/Deklarationsmenge des Builds.
2. Keine Komponenten-Styles in Editor-Komponenten (D09-ADR-03); dynamische Werte (Callout-Hintergrund, Bildbreite, Seitenverhältnis, Floating-Positionen, Upload-Prozent) nur per CSSOM (`[style.x]`-Bindung bzw. `element.style`).
3. Klassen in Templates werden aus dem Original übernommen, inklusive `cn(...)`-Bedingungen (`@plane/utils` `cn` = `clsx` + `tailwind-merge` wie Original).

#### 3.20.4 CSP-Verträglichkeit (Rückmeldung an D05, ABG-016)

ProseMirror serialisiert Node-Attribute mit `style` (Textausrichtung `style="text-align: …"`, Tabellenzellen `style="background-color: …; color: …"`, `customColor` mit Nicht-Listenwerten) über `setAttribute("style", …)`; das unterliegt `style-src-attr`. Ohne `'unsafe-inline'` für **Style-Attribute** würden diese Formatierungen im Enforce-Modus (ab I7) verworfen. Festlegung: Die Gateway-CSP setzt `style-src-attr 'unsafe-inline'` (nur Attribute; `style-src-elem` bleibt ohne `unsafe-inline`, Tiptap-CSS ist statisch, D10-ADR-13). Prüfung: AK-D10-22 (CSP-Report im Editor-E2E leer).

### 3.21 Web- und Space-Hüllen (D10-ADR-17)

| Original | Ziel | Klasse / Funktion | Inkr. |
|---|---|---|---|
| `WEB/components/editor/rich-text/editor.tsx` | `FE/libs/web/core/editor/rich-text/editor.component.ts` | `PlWebRichTextEditor` (`pl-web-rich-text-editor`): verdrahtet `EditorConfigService`, `EditorMentionService`, `EDITOR_FLAGS.richText`, Mention-Render | I2 |
| `WEB/components/editor/rich-text/description-input/{root,loader,index}.tsx` | `FE/libs/web/core/editor/rich-text/description-input/{root,loader}.component.ts` | `PlWebDescriptionInput` (Debounce 1 500 ms, `isMigrationUpdate` → `skip_activity: "true"` beim Speichern), `PlWebDescriptionInputLoader` | I2 |
| `WEB/components/editor/lite-text/{editor,toolbar,lite-toolbar,index}.tsx` | `FE/libs/web/core/editor/lite-text/*.component.ts` | `PlWebLiteTextEditor`, `PlWebIssueCommentToolbar`, `PlWebLiteToolbar` | I2 |
| `WEB/components/editor/document/editor.tsx` | `FE/libs/web/core/editor/document/editor.component.ts` | `PlWebDocumentEditor` (Versionen) | I2 |
| `WEB/components/editor/embeds/mentions/{root,user,index}.tsx` | `FE/libs/web/core/editor/embeds/mentions/*.component.ts` | `PlWebEditorMentionsRoot` (`pl-web-editor-mentions-root`, `data-pl-host` – Render-Ziel von `NgComponentOutlet`, §3.10), `PlWebEditorUserMention` (`div[plWebEditorUserMention]` auf dem Wurzel-`div` von `user.tsx`) | I2 |
| `WEB/components/editor/sticky-editor/{editor,toolbar,color-palette,index}.tsx` | `FE/libs/web/core/editor/sticky-editor/*.component.ts` | `PlWebStickyEditor`, `PlWebStickyEditorToolbar`, `PlWebStickyColorPalette` | I5 |
| `WEB/components/editor/pdf/{document,index}.tsx` | – | entfällt (D10-ADR-21) | – |
| `WEB/hooks/editor/use-editor-config.ts` | `FE/libs/web/core/editor/editor-config.service.ts` | `EditorConfigService.getEditorFileHandlers()` | I2 |
| `WEB/hooks/editor/use-editor-mention.tsx` | `FE/libs/web/core/editor/editor-mention.service.ts` | `EditorMentionService.getMentionHandler({ projectId?, issueId? })` | I2 |
| `WEB/hooks/editor/use-extended-editor-config.ts` | über `EDITOR_EXTENSIONS` (`fileHandlers`-Beiträge, S15) | – | I2 |
| `WEB/hooks/use-editor-flagging.ts` | `EDITOR_FLAGS` (CE-Default §6.1) | `injectEditorFlags(ctx)` | I2 |
| `WEB/hooks/use-additional-editor-mention.tsx` | `EDITOR_MENTION_TYPES` + `EditorMentionSectionProvider` | – | I2 |
| `WEB/hooks/use-parse-editor-content.ts` | `FE/libs/web/core/editor/helpers/parse-editor-content.ts` | `parseEditorContent()` (D08 §4.7; entfernt u. a. `background-color: null; color: null;` aus Export-HTML, E17) | I4 |
| `WEB/hooks/pages/use-extended-editor-extensions.ts`, `use-pages-pane-extensions.ts` | `EDITOR_EXTENSIONS` (Pages-Kontext, S16), `PAGE_PANE_EXTENSIONS` | – | I4 |
| `WEB/components/pages/editor/**` (`page-root`, `editor-body`, `header/*`, `summary/*`, `toolbar/*`, `ai/*`) | `FE/libs/web/pages/components/pages/editor/**` | Page-Hüllen (D08); `ai/*` entfällt (G3) | I4 |
| `SPC/components/editor/{rich-text-editor,lite-text-editor,toolbar}.tsx`, `embeds/mentions/*` | `FE/libs/space/editor/*.component.ts` | `PlSpcRichTextEditor`, `PlSpcLiteTextEditor`, `PlSpcEditorToolbar`, `PlSpcEditorMentionsRoot` (`pl-spc-editor-mentions-root`, `data-pl-host`), `PlSpcEditorUserMention` | I6 |

Beide Apps brauchen in `index.html` das statische `<div id="editor-portal"></div>` direkt in `<body>` (Original: `WEB/app/root.tsx` Z. 75 **und** `SPC/app/root.tsx` Z. 64; Ziel des Bild-Vollbilds, §3.10; festgelegt in D09 §3.14.6 N1 „Admin/Space analog zu deren `root.tsx`“). Selektor-Präfixe der Hüllen: `pl-web-…` (Web), `pl-spc-…` (Space); Klassenpräfix `PlWeb`, `PlSpc` (vermeidet Kollision mit `PlEd…` der Editor-Lib). Die Hüllen setzen `display: contents` + `data-pl-host`, weil die Original-Hüllen kein eigenes Element erzeugen.

### 3.22 Quirk-/Bug-Politik (D10-ADR-16, A12 §3.25)

| Edge-Case | Entscheidung | Abweichungs-ID | Begründung / Zuständigkeit |
|---|---|---|---|
| E1 Slash „Default background“ entfernt Textfarbe | **korrigieren** (`unsetBackgroundColor`) | FE-ED-02 | funktionaler Fehler |
| E2 `convert-document`-Variante vertauscht | Server | – | D07 |
| E3 Rechte nur beim ersten Laden, kein `readonly`-Scope | Server; Client reagiert auf Scope `readonly` mit `editable=false` (Hülle) | – | D07, D05 |
| E4 `page_locked`/`page_archived` nie erzeugt | Server | – | D07 |
| E5 Server-JSON-Events vom Client nicht ausgewertet | **korrigieren** in `RealtimePageEventsService` | FE-ED-03 | D08 (Kanal aus D10) |
| E6 PDF Callout-Emoji als Dezimalstring | Server | – | D07 |
| E7 Titel-Broadcast an Eltern-Page nie aktiv | Server | – | D07 (D2-Andockstelle) |
| E8 `/convert-document` öffentlich | Server | – | D07 |
| E9 Toolbar-Shortcut-Labels Bulleted/Numbered vertauscht | **korrigieren** (Labels Bulleted Cmd+Shift+8, Numbered Cmd+Shift+7) | FE-ED-04 | falsche Information; sichtbarer Tooltip-Text ändert sich (Visual-Maske im Tooltip-Zustand) |
| E10 Slash-Menü globaler Keydown | beibehalten, in S5 prüfen; bei Doppelschritt korrigieren | FE-ED-05 (bedingt) | nur falls funktional fehlerhaft |
| E11 Sender führt eigene Stateless-Aktion doppelt aus | **korrigieren** in `CollaborativePageActionsService` | FE-ED-08 | D08 |
| E12 Heading-Zähler h3–h6 gemeinsam | **korrigieren** (Zähler je Level) | FE-ED-06 | `scrollSummary` springt sonst falsch |
| E13 `HeadingListExtension` emittiert `update` bei jeder Transaktion | beibehalten | – | kein sichtbarer Fehler; LT-16 misst Kosten |
| E14 Live ohne Redis | Server | – | D07 |
| E15 `colwidth` bei `colspan > 1` auf ersten Wert reduziert | beibehalten | – | Schema-/Parse-Parität (G-DOC) |
| E16 `customColor` parst jedes `<span>` | beibehalten | – | Schema-Parität |
| E17 `tableCell` rendert `background-color: null; color: null;` | beibehalten | – | HTML-Parität; Export bereinigt (`parseEditorContent`) |
| E18 ungültige Container-Query | beibehalten | – | CSS unveränderlich |
| E19 Tabellen-Farbe speichert CSS-Variable, Header nicht einfärbbar | beibehalten | – | Datenformat |
| E20 Server-Schema ohne `UniqueID` | beibehalten (entschieden D07-ADR-12) | – | Block-IDs nur im Yjs-Zustand und im Browser-HTML |
| E21 Callout-Default-URL auf CDN | beibehalten als Attributwert, nie geladen | – | D10-ADR-12 |
| E22 `nodeHighlight`-Plugin nicht registriert | beibehalten | – | fehlendes Feature, keine Fehlfunktion; Aktivierung wäre sichtbare Neuerung |
| E23 Attachments bei Drop/Paste verworfen | beibehalten | – | Attachments = Paket D9 (EE-P07-021) |
| E24 `flaggedExtensions` im Drop-Pfad ignoriert | beibehalten | – | ohne Wirkung (immer `[]`) |
| E25 `isValidHttpUrl` akzeptiert beliebige Schemata | beibehalten | – | gefährliche Schemata bleiben blockiert (`isDangerousHref`), Sanitizer filtert serverseitig (D05) |
| E26 Cookie im Query | Server | – | D07/D05 |
| E27 PDF-Mentions-Endpunkt fehlt | Server | – | D07 |
| E28 `UniqueID`-Korrekturen in der Undo-History | beibehalten | – | Verhaltensparität mit Kollaboration |
| E29 `toggleCodeBlock` mehrzeilig über Markdown-Fences | beibehalten | – | Verhaltensparität |
| E30 ungenutzte Typen/Fehlerzustände | beibehalten (Typen 1:1) | – | – |
| E31 deaktivierte Shortcuts (`Mod-Alt-c`, Backspace-`clearNodes`, `Mod-Shift-b`) | beibehalten | – | Aktivierung wäre neues Verhalten |

Jede korrigierte Abweichung erhält einen Eintrag in `FE/apps/e2e/visual/ui-deviations.yaml` mit `id`, `kind` (`behavior` bzw. `extra-css`), `original`, `target`, `reason`, `tests` (Spec-Fall, der das korrigierte Verhalten prüft) und `approved_by`.

### 3.23 Zoneless, Performance, Lazy Loading

| Maßnahme | Ziel |
|---|---|
| Editor-Code nur in Lazy-Chunks: Work-Item-Detail/Peek/Modal (Rich + Lite), Kommentare (Lite), Pages (Collab), Space-Peek | Initial-Bundle-Budget D08 §3.1.2 unberührt; Chunk `editor-core` geteilt |
| `lowlight` mit `common` + `ts` wie Original (keine dynamischen Sprachen) | gleiches Highlighting, keine Netzladevorgänge |
| Keine Signale je ProseMirror-Transaktion außer `editorState()`-Selektoren; `editorChange` nur bei `update` (wie Original) | Tippen ohne Angular-CD-Kosten |
| NodeView-Komponenten `OnPush`, Inputs als Signale; `afterRenderEffect` statt `setTimeout`-Ketten für DOM-Messungen | stabile Selektion |
| LT-16: 5 000 Blöcke, Eingabe-Latenz p95 < 50 ms (Chromium) | AK-D10-11 |
| Speicher: 30 × Editor öffnen/schließen (Peek) ohne wachsende `Editor`-/`ComponentRef`-Anzahl (Heap-Snapshot) | AK-D10-21 |

### 3.24 Sicherheit

1. **Link-Protokolle:** `isDangerousHref` (Parse verwirft, Render schreibt `href=""`; GHSA-v2vv-7wq3-8w2j) und Klick-Blockade `file:`/`about:` 1:1 im Kern (`extensions/custom-link/**`); Regressionstests aus dem Original-Verhalten.
2. **Kein `innerHTML`** in Editor-Komponenten außer dort, wo das Original HTML injiziert (`view.pasteHTML`, `setContent`); Trusted-Types-Richtlinie `plane-editor` für ProseMirror-`DOMParser` falls CSP `require-trusted-types-for` aktiviert wird (heute nicht, D05).
3. **Sanitizer-Vertrag (D05 §3.17.3):** Der Editor erzeugt ausschließlich die Tags/Attribute aus §4.1 (Spalte „renderHTML“). Erweiterungen erfordern die Schritte 4–5 aus §3.2.5.
4. **localStorage:** Callout-Logo wird beim Lesen über `sanitizeHTML` gefiltert (1:1).
5. **Mention-Suche** nur über die berechtigten Endpunkte (`searchEntity`, Berechtigungsprüfung serverseitig nach D05); keine clientseitige Rechteentscheidung.

---

## 4. Mapping-Tabellen Original → Ziel

**Legende Umsetzung:** **A** = Kern-Quelltext 1:1 (`ED/core`, K1/K2); **NV** = Extension 1:1 im Kern, NodeView als Angular-Komponente über den UI-Port; **V** = Vanilla-DOM (NodeView/Widget/Plugin) 1:1 im Kern; **W** = React-Widget/-Popup → Angular-Komponente über `uiRender`; **neu** = in `funk.` hinzugefügt. **Varianten:** R = rich, L = lite, D = document, C = collaborative, T = title, S = server, SD = server-document (§3.2.3). **Server-Spec:** Klassenname in `BE/documents/Plane.Documents/Schema/{Nodes,Marks}/` laut D07 §3.13 (E-11, Eigentümer D07; eine Klasse je Tiptap-Extension, D07-ADR-11).

### 4.1 Extension-Inventar → Angular-Umsetzung (vollständig, A12 §2.5)

#### 4.1.1 Nodes (23)

| # | Node (`CORE_EXTENSIONS`) | Original-Datei(en) (`ED0/`) | Varianten | Umsetzung | Angular-Artefakt | Server-Spec | CE-IDs |
|---|---|---|---|---|---|---|---|
| 1 | `doc` | `extensions/starter-kit.ts` (StarterKit `Document`), `extensions/title-extension.ts` (`content: "heading"`) | R L D C T S SD | A | – | `DocNodeSpec` (+ Variante Titel) | CE-PAGE-021…023 |
| 2 | `paragraph` | `extensions/starter-kit.ts` | R L D C S SD | A | – | `ParagraphNodeSpec` | CE-PAGE-027 |
| 3 | `text` | StarterKit | R L D C T S SD | A | – | `TextNodeSpec` | – |
| 4 | `heading` | `extensions/starter-kit.ts`, `title-extension.ts` (`levels: [1]`) | R L D C T S SD | A | – | `HeadingNodeSpec` | CE-PAGE-027 |
| 5 | `blockquote` | `extensions/quote.ts` | R L D C S SD | A | – | `BlockquoteNodeSpec` | CE-PAGE-027 |
| 6 | `bulletList` | `extensions/starter-kit.ts` | R L D C S SD | A | – | `BulletListNodeSpec` | CE-PAGE-028 |
| 7 | `orderedList` | `extensions/starter-kit.ts` | R L D C S SD | A | – | `OrderedListNodeSpec` | CE-PAGE-028 |
| 8 | `listItem` | `extensions/starter-kit.ts` | R L D C S SD | A | – | `ListItemNodeSpec` | CE-PAGE-028 |
| 9 | `taskList` | `extensions/extensions.ts`, `core-without-props.ts` (`@tiptap/extension-task-list`) | R L D C S SD | A | – | `TaskListNodeSpec` | CE-PAGE-028 |
| 10 | `taskItem` | dto. (`@tiptap/extension-task-item`, `nested: true`; Runtime-Klasse `relative`, Server `flex`) | R L D C S SD | V (Tiptap-Default-NodeView) | – | `TaskItemNodeSpec` | CE-PAGE-028 |
| 11 | `codeBlock` | `extensions/code/{code-block,code-block-lowlight,index,without-props,code-block-node-view}.ts(x)`, `lowlight-plugin.ts` | R L D C S SD | NV (`code-block`) | `PlEdCodeBlockNodeView` | `CodeBlockNodeSpec` | CE-PAGE-030 |
| 12 | `horizontalRule` | `extensions/horizontal-rule.ts` | R L D C S SD | A | – | `HorizontalRuleNodeSpec` | CE-PAGE-027 |
| 13 | `hardBreak` | StarterKit | R L D C S SD | A | – | `HardBreakNodeSpec` | CE-PAGE-022 |
| 14 | `image` (Legacy) | `extensions/image/{extension,extension-config}.tsx` | R L D C (wenn `"image"` nicht deaktiviert) S SD | NV (`custom-image`) | `PlEdCustomImageNodeView` | `ImageNodeSpec` | CE-PAGE-032 |
| 15 | `imageComponent` | `extensions/custom-image/**` | R L D C (dto.) S SD | NV (`custom-image`) | `PlEdCustomImageNodeView` + Unterkomponenten §3.10 | `ImageComponentNodeSpec` | CE-PAGE-032, CE-UIX-009 |
| 16 | `table` | `extensions/table/table/{table,table-view,index,icons}.ts(x)`, `utilities/*` | R L D C S SD | V (`TableView`) | – (Widgets siehe Plugins) | `TableNodeSpec` | CE-PAGE-031 |
| 17 | `tableRow` | `extensions/table/table-row.ts` | R L D C S SD | A | – | `TableRowNodeSpec` | CE-PAGE-031 |
| 18 | `tableHeader` | `extensions/table/table-header.ts` | R L D C S SD | A | – | `TableHeaderNodeSpec` | CE-PAGE-031 |
| 19 | `tableCell` | `extensions/table/table-cell.ts` | R L D C S SD | A | – | `TableCellNodeSpec` | CE-PAGE-031 |
| 20 | `mention` | `extensions/mentions/{extension-config,extension,mention-node-view,mentions-list-dropdown,utils,types}.ts(x)` | R L D C S SD | NV (`mention`) + W (`mentions-list-dropdown`) | `PlEdMentionNodeView`, `PlEdMentionsListDropdown` | `MentionNodeSpec` | CE-PAGE-034, CE-WI-044 |
| 21 | `emoji` | `extensions/emoji/{emoji,extension,suggestion}.ts`, `components/emojis-list.tsx` | R L D C S SD | A + W (`emojis-list-dropdown`) | `PlEdEmojisListDropdown` | `EmojiNodeSpec` | CE-PAGE-035 |
| 22 | `calloutComponent` | `extensions/callout/**` | R L D C S SD | NV (`callout-block`) | `PlEdCalloutBlock`, `PlEdCalloutLogoSelector`, `PlEdCalloutColorSelector` | `CalloutNodeSpec` | CE-PAGE-033 |
| 23 | `issue-embed-component` | `extensions/work-item-embed/{extension-config,types}.ts` | SD (Runtime in CE nicht registriert) | A (nur Config) | – (D6) | `WorkItemEmbedNodeSpec` | CE-PAGE-023 (Schema) |

#### 4.1.2 Marks (8)

| # | Mark | Original-Datei | Varianten | Umsetzung | Server-Spec | CE-IDs |
|---|---|---|---|---|---|---|
| 1 | `bold` | StarterKit | R L D C S SD | A | `BoldMarkSpec` | CE-PAGE-029 |
| 2 | `italic` | StarterKit | R L D C S SD | A | `ItalicMarkSpec` | CE-PAGE-029 |
| 3 | `strike` | StarterKit | R L D C S SD | A | `StrikeMarkSpec` | CE-PAGE-029 |
| 4 | `underline` | `@tiptap/extension-underline` (`extensions/extensions.ts`) | R L D C S SD | A | `UnderlineMarkSpec` | CE-PAGE-029 |
| 5 | `code` | `extensions/code-inline/index.tsx` | R L D C S SD | A | `CodeInlineMarkSpec` | CE-PAGE-029 |
| 6 | `link` | `extensions/custom-link/**` | R L D C S SD | A | `LinkMarkSpec` | CE-PAGE-036 |
| 7 | `textStyle` | `@tiptap/extension-text-style` | R L D C S SD | A | `TextStyleMarkSpec` | CE-PAGE-029 |
| 8 | `customColor` | `extensions/custom-color.ts` | R L D C S SD | A | `CustomColorMarkSpec` | CE-PAGE-029, CE-I18N-010 |

Globale Attribute: `textAlign` (`CustomTextAlignExtension`, Typen `heading`, `paragraph`; serverseitig als globales `AttributeSpec`, D07 §3.12.2); `id` (`UniqueID`, nur Runtime, Typen `BLOCK_NODE_TYPES` + Block-Registry).

#### 4.1.3 Funktionale Extensions (ohne eigene Nodes/Marks)

| # | Extension (Name) | Original-Datei | Varianten | Umsetzung | Angular-Artefakt / Hinweis | CE-IDs |
|---|---|---|---|---|---|---|
| 1 | `dropCursor`, `gapCursor` (StarterKit) | `extensions/starter-kit.ts` | R L D C S SD | A | Dropcursor-Klasse 1:1 | CE-PAGE-026 |
| 2 | `history` (StarterKit) | dto. | R L D S SD (nicht C: `enableHistory:false`) | A | – | CE-PAGE-021 |
| 3 | `uniqueID` (Priorität 10000) | `extensions/unique-id/{extension,plugin,utils}.ts` | R L D C | A | IDs nach `synced` bei Provider; Block-Typen aus Registry (R-ED-12) | CE-PAGE-039 |
| 4 | `textAlign` | `extensions/text-align.ts` | R L D C S SD | A | – | CE-PAGE-027 |
| 5 | `characterCount` | `@tiptap/extension-character-count` | R L D C | A | `getDocumentInfo()` | CE-PAGE-017 |
| 6 | `placeholder` | `extensions/placeholder.ts` (Titel: Tiptap-`Placeholder` „Untitled“) | R L D C T | A | – | CE-PAGE-038 |
| 7 | `markdown` (`tiptap-markdown`) | `extensions/extensions.ts` | R L D C | A | – | CE-PAGE-037 |
| 8 | `typography` | `extensions/typography/{index,inputRules}.ts` | R L D C | A | – | CE-PAGE-029 |
| 9 | `customKeymap` | `extensions/keymap.ts` | R L D C | A | Mod-a zweistufig, `ordered-list-merging` | CE-PAGE-028 |
| 10 | `listKeymap` | `extensions/custom-list-keymap/**` | R L D C | A | `tabIndex` aus Input | CE-PAGE-028 |
| 11 | `utility` (Priorität 1000) | `extensions/utility.ts` | R L D C | A | Storage `assetsList`, `assetsUploadStatus`, `uploadInProgress`, `activeDropbarExtensions`, `isTouchDevice`; Plugins §4.2 | CE-PAGE-032 |
| 12 | `CoreEditorAdditionalExtensions` | `extensions/core/{extensions,without-props}.ts` | R L D C (S: `…WithoutProps`) | A | liefert Beiträge der Block-Registry (CE: `[]`) | – |
| 13 | `slash-command` | `extensions/slash-commands/**`, `additional-slash-command-options.tsx` | R D C | A + W (`slash-commands-menu`) | `PlEdSlashCommandsMenu`, `PlEdSlashCommandMenuItem` | CE-PAGE-024 |
| 14 | `enterKey` | `extensions/enter-key.ts` | L | A | `editorEnterKeyPress` | CE-PAGE-022, CE-WI-037 |
| 15 | `editorSideMenu` | `extensions/side-menu.ts`, `plugins/{drag-handle,ai-handle}.ts` | R D C | V | `PlEdBlockMenu` reagiert auf `#drag-handle` | CE-PAGE-026 |
| 16 | `headingsList` | `extensions/headings-list.ts` | D C | A (E12 korrigiert) | `getHeadings()`, `onHeadingChange()` | CE-PAGE-016 |
| 17 | `collaboration` | `@tiptap/extension-collaboration` 2.26.1 | C (`field: "default"`), T (`field: "title"`) | A | `CollaborativeEditorInstance`, `TitleEditorInstance` | CE-RT-002 |
| 18 | `titleEditorNavigation`, `mainEditorNavigation` (Priorität 10) | `hooks/use-editor-navigation.ts` | T, C | A (reine Funktionen) | `ED/core/src/hooks/editor-navigation.ts` | CE-PAGE-013 |
| 19 | `trailingNode` | `extensions/trailing-node.ts` | – (exportiert, nirgends registriert) | A | Export beibehalten | – |
| 20 | `planeUiPort` | – | R L D C T | **neu** | `PlaneUiPortExtension` (§3.4); vom Golden-Serialisierer ausgefiltert | – |
| 21 | `collaborationCursor` | – (CE deaktiviert) | C (nur wenn Flag aktiv) | **neu (Flag)** | `@tiptap/extension-collaboration-cursor` 2.26.1 | CE-RT-002 (FE-ED-01) |

### 4.2 ProseMirror-Plugins → Umsetzung (vollständig, A12 §2.6)

| PluginKey | Original-Datei | Registriert durch | Umsetzung | Hinweis |
|---|---|---|---|---|
| `codeBlockVSCodeHandlerCustom` | `extensions/code/code-block.ts` | `codeBlock` | A | – |
| `lowlight` | `extensions/code/lowlight-plugin.ts` | `CodeBlockLowlight` | A | `lowlight` 3.3.0 `common` + `ts` |
| `autolink` | `extensions/custom-link/helpers/autolink.ts` | `link` | A | – |
| `handleClickLink` | `extensions/custom-link/helpers/clickHandler.ts` | `link` | A | – |
| `handlePasteLink` | `extensions/custom-link/helpers/pasteHandler.ts` | `link` | A | – |
| `emojiSuggestion` | `extensions/emoji/emoji.ts` + `suggestion.ts` | `emoji` (nicht Touch) | A + W | `PlEdEmojisListDropdown` |
| `emoji` | `extensions/emoji/emoji.ts` | `emoji` (nicht Touch) | A | – |
| `suggestion` (Slash) | `extensions/slash-commands/root.tsx` | `slash-command` | A + W | `PlEdSlashCommandsMenu` |
| `mention` (Tiptap-Default-Key) | `@tiptap/extension-mention` + `extensions/mentions/utils.ts` | `mention` | A + W | `PlEdMentionsListDropdown` |
| `heading-list` | `extensions/headings-list.ts` | `headingsList` | A | – |
| `ordered-list-merging` | `extensions/keymap.ts` | `customKeymap` | A | – |
| `sideMenu` | `extensions/side-menu.ts` | `editorSideMenu` | V | – |
| `uniqueID` | `extensions/unique-id/plugin.ts` | `uniqueID` | A | ignoriert `y-sync$`-Transaktionen |
| `tableDragState` | `extensions/table/plugins/drag-state.ts` | `table` | A | Decoration `content-hidden` |
| `table-insert` | `extensions/table/plugins/insert-handlers/plugin.ts` | `table` | V | „+“-Buttons, Drag-Marker |
| `tableColumnHandlerDecorationPlugin` | `extensions/table/plugins/drag-handles/column/plugin.ts` | `table` | A + W | `PlEdTableColumnDragHandle` |
| `tableRowDragHandlePlugin` | `extensions/table/plugins/drag-handles/row/plugin.ts` | `table` | A + W | `PlEdTableRowDragHandle` |
| `table-cell-selection-outline` | `extensions/table/plugins/selection-outline/plugin.ts` | `tableCell` | A | – |
| `tableEditing`, `columnResizing` | `prosemirror-tables` 1.7.1 via `extensions/table/table/table.ts` | `table` | A | nur editierbar |
| `delete-utility` | `plugins/file/delete.ts` | `utility` | A | ruft `fileHandler.delete` |
| `restore-utility` | `plugins/file/restore.ts` | `utility` | A | `restorePublicImages` beim Erstellen |
| `prosemirror-codemark` | `extensions/utility.ts` | `utility` | A | CSS `.fake-cursor`, `.no-cursor` |
| `markdownClipboard` | `plugins/markdown-clipboard.ts` | `utility` | A | – |
| `drop-handler-plugin` | `plugins/drop.ts` | `utility` | A | Attachment-Zweig über Block-Registry (D9) |
| `nodeHighlight` | `plugins/highlight.ts` | nicht registriert | A | E22 beibehalten |
| `placeholder`, `characterCount`, `dropcursor`, `gapcursor`, `history` | Tiptap | – | A | – |
| `y-sync`, `y-undo` | `y-prosemirror` 1.3.7 via `Collaboration` | C, T | A | – |
| `bubbleMenu` | `@tiptap/extension-bubble-menu` 2.26.3 | `PlEdEditorBubbleMenu` (über `[plEdBubbleMenu]`) | W | im Original durch `@tiptap/react` `BubbleMenu` registriert |
| tiptap-markdown-Plugins | `tiptap-markdown` 0.8.10 | `markdown` | A | – |
| `yCursorPlugin` (Awareness) | `y-prosemirror` via `collaborationCursor` | C (Flag) | neu (Flag) | FE-ED-01 / D4 |

### 4.3 React-Komponenten → Angular-Komponenten (Übersicht; Datei-genau in Anhang A)

| Gruppe | Original (`ED0/`) | Angular (`ED/components/src/`) | Selektor |
|---|---|---|---|
| Varianten | `components/editors/{rich-text,lite-text,document}/editor.tsx`, `document/collaborative-editor.tsx` | `PlEdRichTextEditor`, `PlEdLiteTextEditor`, `PlEdDocumentEditor`, `PlEdCollaborativeDocumentEditor` | `pl-ed-rich-text-editor`, `pl-ed-lite-text-editor`, `pl-ed-document-editor`, `pl-ed-collaborative-document-editor` |
| Hülle | `editor-wrapper.tsx`, `editor-container.tsx`, `editor-content.tsx`, `document/page-renderer.tsx`, `document/loader.tsx`, `link-container.tsx`, `link-view-container.tsx`, `document-editor-side-effects.ts` | `PlEdEditorWrapper`, `PlEdEditorContainer`, `PlEdEditorContentWrapper`, `PlEdPageRenderer`, `PlEdDocumentContentLoader`, `PlEdLinkContainer`, `PlEdLinkViewContainer`, `PlEdDocumentEditorSideEffects` (+ intern `PlEdTitleEditor`) | `pl-ed-editor-wrapper`, `div[plEdEditorContainer]`, `div[plEdEditorContentWrapper]`, `div[plEdPageRenderer]`, `pl-ed-document-content-loader`, `pl-ed-link-container`, `pl-ed-link-view-container`, `pl-ed-document-editor-side-effects`, `pl-ed-title-editor` |
| Links | `components/links/{link-view,link-preview,link-edit-view}.tsx` | `PlEdLinkView`, `PlEdLinkPreview`, `PlEdLinkEditView` | `pl-ed-link-view`, `div[plEdLinkPreview]`, `div[plEdLinkEditView]` |
| Menüs | `components/menus/bubble-menu/{root,node-selector,link-selector,color-selector,alignment-selector}.tsx`, `block-menu.tsx`, `floating-menu/root.tsx` | `PlEdEditorBubbleMenu`, `PlEdBubbleMenuNodeSelector`, `PlEdBubbleMenuLinkSelector`, `PlEdBubbleMenuColorSelector`, `PlEdBubbleMenuAlignmentSelector`, `PlEdBlockMenu`, `PlEdFloatingMenuRoot` | `pl-ed-editor-bubble-menu`, `pl-ed-bubble-menu-*`, `pl-ed-block-menu`, `pl-ed-floating-menu-root` |
| Suggestions | `extensions/slash-commands/{command-menu,command-menu-item}.tsx`, `extensions/mentions/mentions-list-dropdown.tsx`, `extensions/emoji/components/emojis-list.tsx` | `PlEdSlashCommandsMenu`, `PlEdSlashCommandMenuItem`, `PlEdMentionsListDropdown`, `PlEdEmojisListDropdown` | Host `div.react-renderer` (über `AngularRenderer`), `button[plEdSlashCommandMenuItem]` |
| NodeViews | `extensions/callout/{block,logo-selector,color-selector}.tsx`, `extensions/code/code-block-node-view.tsx`, `extensions/custom-image/components/**`, `extensions/mentions/mention-node-view.tsx` | `PlEdCalloutBlock`, `PlEdCalloutLogoSelector`, `PlEdCalloutColorSelector`, `PlEdCodeBlockNodeView`, `PlEdCustomImageNodeView`, `PlEdImageBlock`, `PlEdImageUploader`, `PlEdImageUploadStatus`, `PlEdImageToolbarRoot`, `PlEdImageDownloadAction`, `PlEdImageAlignmentAction`, `PlEdImageFullScreenAction`, `PlEdImageFullScreenModal`, `PlEdMentionNodeView` | Wrapper-Attribut `[plEd…]` (§3.5.1) |
| Tabellen-Widgets | `extensions/table/plugins/drag-handles/{column,row}/{drag-handle,dropdown}.tsx`, `color-selector.tsx` | `PlEdTableColumnDragHandle`, `PlEdTableRowDragHandle`, `PlEdTableColumnDropdown`, `PlEdTableRowDropdown`, `PlEdTableDragHandleColorSelector` | Host `div.react-renderer` bzw. `pl-ed-table-*` |
| Entfällt | `components/menus/ai-menu.tsx`, `extensions/work-item-embed/extension.tsx` | – | G3 nicht gewählt / Paket D6 |

### 4.4 Konsumenten im Original → Ziel (wer bindet den Editor ein)

| Original | Nutzung | Ziel (Hülle) | Inkr. | CE-IDs |
|---|---|---|---|---|
| `WEB/components/issues/issue-modal/{form,components/description-editor,context/issue-modal-context}.tsx` | Rich (Beschreibung), Ref `setEditorValue`, `isEditorReadyToDiscard` | `PlWebRichTextEditor` in `FE/libs/web/work-items/components/issues/issue-modal/**` | I2 | CE-WI-001 |
| `WEB/components/issues/{peek-overview/issue-detail,peek-overview/view,issue-detail/main-content}.tsx` | `PlWebDescriptionInput`, Ref | `FE/libs/web/work-items/components/issues/**` | I2 | CE-WI-005 |
| `WEB/components/comments/{comment-create,card/root,card/edit-form,card/display}.tsx` | Lite (Erstellen/Bearbeiten), Lite read-only (Anzeige) | `FE/libs/web/work-items/components/comments/**` | I2 | CE-WI-037 |
| `WEB/components/core/description-versions/modal.tsx` | Document read-only | `FE/libs/web/core/components/core/description-versions/**` | I2 | CE-WI-041 |
| `WEB/components/inbox/{content/issue-root,modals/create-modal/create-root,modals/create-modal/issue-description}.tsx` | Rich | `FE/libs/web/intake/components/inbox/**` | I3 | CE-INT-004, -005, -010 |
| `WEB/components/pages/editor/{page-root,editor-body}.tsx` | Collaborative + Titel, Stateless, Fallback | `FE/libs/web/pages/components/pages/editor/**` | I4 | CE-PAGE-013 |
| `WEB/components/pages/version/editor.tsx` | Document read-only | `FE/libs/web/pages/components/pages/version/**` | I4 | CE-PAGE-019 |
| `WEB/components/pages/navigation-pane/tab-panels/{assets,info/document-info}.tsx` | `editorAssetChange`, `getDocumentInfo`/`onDocumentInfoChange` | `FE/libs/web/pages/components/pages/navigation-pane/**` | I4 | CE-PAGE-017, -018 |
| `WEB/components/pages/modals/export-page-modal.tsx` | `getMarkDown`, `getDocument` (PDF serverseitig, D10-ADR-21) | `FE/libs/web/pages/components/pages/modals/**` | I4 | CE-PAGE-011 |
| `WEB/components/pages/editor/toolbar/*`, `summary/*` | `executeMenuItemCommand`, `isMenuItemActive`, `onStateChange`, `getHeadings`, `scrollSummary` | `FE/libs/web/pages/components/pages/editor/{toolbar,summary}/**` | I4 | CE-PAGE-014, -016 |
| `WEB/components/stickies/sticky/inputs.tsx` | Sticky-Editor | `FE/libs/web/stickies/components/stickies/sticky/**` | I5 | CE-HOME-010 |
| `WEB/components/core/modals/gpt-assistant-popover.tsx` | Rich (Prompt/Antwort), `setEditorValue` | `FE/libs/web/core/components/core/modals/**` | I6 | CE-AI-001 |
| `WEB/hooks/use-collaborative-page-actions.tsx`, `use-realtime-page-events.tsx`, `use-page-fallback.ts` | `emitRealTimeUpdate`, `listenToRealTimeUpdate`, `setProviderDocument`, `getDocument` | `CollaborativePageActionsService`, `RealtimePageEventsService`, `PageFallbackService` (D08) | I4 | CE-RT-003, -004 |
| `SPC/components/issues/**` (Peek, Kommentare) | Space-Hüllen | `FE/libs/space/issues/**` | I6 | CE-SPACE-024, -025 |

### 4.5 CE-ID → Baustein → Inkrement → Test (Editor-Teil; Spec-Namen aus D15 Anhang B.8)

| CE-ID | Editor-Baustein(e) | Inkr. | Spec / Golden |
|---|---|---|---|
| CE-PAGE-013 | `PlEdCollaborativeDocumentEditor`, `PlEdTitleEditor`, `CollaborationSession` | I4 | `web/pages/page-editor-shell.spec.ts`, `web/editor/editor-variants.spec.ts` (collab) |
| CE-PAGE-014 | `TOOLBAR_ITEMS`, `executeMenuItemCommand`, `isMenuItemActive`, `onStateChange` | I4 | `web/pages/page-editor-shell.spec.ts` |
| CE-PAGE-015 | Sync-/Offline-Badges des Page-Kopfs: Quelle `CollaborationSession.stage` → `serverHandler.onStateChange` (`synced`/`syncing`/`error`, §3.15.2); Rest des Kopfs = D08 | I4 | `page-editor-shell.spec.ts` |
| CE-PAGE-016 | `HeadingListExtension`, `getHeadings`, `onHeadingChange`, `scrollSummary` | I2 (Extension) / I4 (Outline) | `page-editor-shell.spec.ts`, Kern-Spec `headings-list.spec.ts` |
| CE-PAGE-017 | `getDocumentInfo`, `onDocumentInfoChange` | I4 | `page-editor-shell.spec.ts` |
| CE-PAGE-018 | `editorAssetChange`, `utility.assetsList` | I4 | `page-editor-shell.spec.ts` |
| CE-PAGE-020 | `displayConfig` (`wideLayout`), `copyMarkdownToClipboard` | I4 | `page-editor-shell.spec.ts` |
| CE-PAGE-021 | `PlEdRichTextEditor`, `EditorInstance` | I2 | `web/editor/editor-variants.spec.ts`, G-SCHEMA `rich`, LT-16 |
| CE-PAGE-022 | `PlEdLiteTextEditor`, `EnterKeyExtension` | I2 | `editor-variants.spec.ts`, G-SCHEMA `lite` |
| CE-PAGE-023 | `PlEdDocumentEditor`, `PlEdPageRenderer` | I2 | `editor-variants.spec.ts`, G-SCHEMA `document` |
| CE-PAGE-024 | Slash-Commands | I2 | `web/editor/editor-menus.spec.ts` |
| CE-PAGE-025 | Bubble-Menü | I2 | `editor-menus.spec.ts` |
| CE-PAGE-026 | Side-Menü, Drag-Handle, Block-Menü, Block-DnD | I2 | `editor-menus.spec.ts` |
| CE-PAGE-027 … -033 | Nodes/Marks §4.1, NodeViews §3.10, Tabellen §3.13, Bilder §3.14 | I2 | `web/editor/editor-blocks.spec.ts`, G-DOC |
| CE-PAGE-034 … -038 | Mentions, Emoji, Links, Markdown, Platzhalter | I2 | `web/editor/editor-inline.spec.ts`, G-DOC |
| CE-PAGE-039, -040 | Deep-Link (`EditorContainer`), Anzeige-Konfiguration | I2 | `web/editor/editor-config.spec.ts` |
| CE-RT-002 | `CollaborationSession`, `CollaborationProviderFactory`, IndexedDB | I4 | `web/realtime/collaboration.spec.ts`, Vitest `collaboration-session.spec.ts` |
| CE-RT-003 | `setProviderDocument`, `getDocument` (Schnittstelle für `PageFallbackService`) | I4 | `page-fallback.service.spec.ts` (D08) |
| CE-RT-004 | `emitRealTimeUpdate`, `listenToRealTimeUpdate` | I4 | `realtime-page-events.service.spec.ts` (D08) |
| CE-RT-006 (Client-Teil) | Forced-Close-Erkennung 4000–4003 in `CollaborationSession` (Stage `disconnected`/`forced-close`, `pauseProvider()`), Weitergabe der Server-JSON-Events (`error`, `force_close`) über den Stateless-Kanal | I4 | `collaboration-session.spec.ts`, `collaboration.spec.ts` |
| CE-WI-001, -005 | Rich + `PlWebDescriptionInput` | I2 | Spec des Work-Item-Moduls (D15 B.x) + `editor-variants.spec.ts` |
| CE-WI-037 | Lite + Kommentar-Toolbars | I2 | Spec Kommentare (D15) |
| CE-WI-041 | Document read-only | I2 | Spec Beschreibungs-Versionen (D15) |
| CE-WI-044 | `mention`-Node, `mention-component`-HTML | I2 | G-DOC + Backend `page_transaction`/IssueMention-Tests |
| CE-HOME-010 | Sticky-Hülle | I5 | Spec Stickies (D15) |
| CE-SPACE-024, -025, -030 | Space-Hüllen | I6 | Space-Specs (D15) |
| CE-I18N-010 | `ED/styles/variables.css`, `COLORS_LIST` | I0 (CSS) / I2 | G-CSS |
| CE-UIX-009 | Upload-Fortschritt im Editor (`PlEdImageUploadStatus`) | I2 | `editor-blocks.spec.ts` |

---

## 5. Code-Skelette

> Skelette legen Namen, Signaturen und Zuständigkeiten fest; sie sind kein vollständiger Code. ⚠ markiert Details, die Spike S5 gegen das Original-DOM bzw. die gepinnten Bibliotheken bestätigt.

### 5.1 Pfad-Aliase und Sheriff-Ausschnitt

```jsonc
// FE/tsconfig.base.json (Ausschnitt)
{
  "compilerOptions": {
    "paths": {
      "@plane/editor": ["libs/shared/editor/components/src/public-api.ts"],
      "@plane/editor/core": ["libs/shared/editor/core/src/public-api.ts"],
      "@plane/editor/angular-binding": ["libs/shared/editor/angular-binding/src/public-api.ts"],
      "@plane/editor/collaboration": ["libs/shared/editor/collaboration/src/public-api.ts"],
      "@plane/editor/extensibility": ["libs/shared/editor/extensibility/src/public-api.ts"]
    }
  }
}
```

```ts
// FE/sheriff.config.ts (Ausschnitt)
export const config: SheriffConfig = {
  tagging: {
    'libs/shared/editor/core': ['scope:shared', 'type:ui', 'editor:core'],
    'libs/shared/editor/angular-binding': ['scope:shared', 'type:ui', 'editor:binding'],
    'libs/shared/editor/components': ['scope:shared', 'type:ui', 'editor:ui'],
    'libs/shared/editor/collaboration': ['scope:shared', 'type:ui', 'editor:collab'],
    'libs/shared/editor/extensibility': ['scope:shared', 'type:ui', 'editor:extensibility'],
  },
  depRules: {
    // 'propel'/'blocks' nur wegen der Daten-Einstiegspunkte @plane/propel/icons, @plane/blocks/icons;
    // alle anderen Pfade sperrt ESLint no-restricted-imports (§3.1, AK-D10-04)
    'editor:core': ['type:types', 'type:constants', 'type:utils', 'propel', 'blocks', 'icons-lucide'],
    'editor:binding': ['editor:core'],
    'editor:extensibility': ['editor:core'],
    'editor:ui': ['editor:core', 'editor:binding', 'editor:extensibility', 'type:ui', 'type:data'],
    'editor:collab': ['editor:core', 'editor:ui'],
  },
};
```

### 5.2 UI-Port im Kern (`ED/core/src/ui-port/ui-port.ts`)

```ts
import type { Editor, NodeViewRenderer, NodeViewRendererOptions } from "@tiptap/core";

/** Schlüssel der CE (§3.4.2); Paket-Schlüssel tragen ein Präfix "<paket>:". */
export type EditorUiKey =
  | "callout-block" | "code-block" | "custom-image" | "mention"
  | "slash-commands-menu" | "mentions-list-dropdown" | "emojis-list-dropdown"
  | "table-column-drag-handle" | "table-row-drag-handle"
  | `${string}:${string}`;

/** Gleiche Felder wie @tiptap/react ReactRenderer, damit die Aufrufstellen 1:1 bleiben. */
export interface EditorUiHandle<P extends object = Record<string, unknown>, R = unknown> {
  readonly element: HTMLElement;
  readonly ref: R | null;
  updateProps(props: Partial<P>): void;
  destroy(): void;
}

export interface EditorUiNodeViewOptions extends Partial<NodeViewRendererOptions> {
  /** Tag des Außenelements; Default: span für Inline-, div für Block-Nodes (wie ReactNodeViewRenderer). */
  as?: string;
  className?: string;
  /** Tag des NodeViewWrapper-Elements (Default div). */
  wrapperAs?: string;
}

export interface EditorUiPort {
  createNodeView(key: EditorUiKey, options?: EditorUiNodeViewOptions): NodeViewRenderer | null;
  render<P extends object, R = unknown>(
    key: EditorUiKey,
    editor: Editor,
    props: P,
    options?: { as?: string; className?: string },
  ): EditorUiHandle<P, R> | null;
}

/** Interfaces für renderbare Inhalte aus Handlern (ersetzt ReactNode im Kern, R-ED-7). */
export interface TEditorRenderable<C = unknown> {
  readonly component: C;
  readonly inputs?: Readonly<Record<string, unknown>>;
}

export const UI_PORT_EXTENSION_NAME = "planeUiPort";

export function getEditorUiPort(editor: Editor | null | undefined): EditorUiPort | null {
  const storage = editor?.storage as Record<string, { port?: EditorUiPort } | undefined> | undefined;
  return storage?.[UI_PORT_EXTENSION_NAME]?.port ?? null;
}

/**
 * Ersatz für ReactNodeViewRenderer(...) in addNodeView(). Liefert IMMER eine Fabrik (Tiptap ruft addNodeView()(props),
 * ExtensionManager.ts Z. 301). Ohne Port gibt die Fabrik null zurück → ProseMirror rendert per toDOM (viewdesc.ts Z. 707).
 */
export function uiNodeView(editor: Editor, key: EditorUiKey, options?: EditorUiNodeViewOptions): NodeViewRenderer {
  return (props) => {
    const renderer = getEditorUiPort(editor)?.createNodeView(key, options);
    return (renderer ? renderer(props) : null) as ReturnType<NodeViewRenderer>;
  };
}

/** Ersatz für new ReactRenderer(...); ohne Port: null (Suggestion zeigt kein Menü). */
export function uiRender<P extends object, R = unknown>(
  editor: Editor, key: EditorUiKey, props: P, options?: { as?: string; className?: string },
): EditorUiHandle<P, R> | null {
  return getEditorUiPort(editor)?.render<P, R>(key, editor, props, options) ?? null;
}
```

Aufrufstelle (Beispiel `ED/core/src/extensions/callout/extension.ts`, einzige `PORT-DIFF`-Zeile):

```ts
  addNodeView() {
    // PORT-DIFF(ui-port): ReactNodeViewRenderer((props) => <CustomCalloutBlock … />)
    return uiNodeView(this.editor, "callout-block");
  },
```

### 5.3 `AngularNodeViewRenderer` (`ED/angular-binding/src/angular-node-view-renderer.ts`)

```ts
import {
  ApplicationRef, ComponentRef, EnvironmentInjector, Injector, Type, createComponent, reflectComponentType,
} from "@angular/core";
import { NodeView, type DecorationWithType, type Editor, type NodeViewRenderer, type NodeViewRendererProps } from "@tiptap/core";
import type { Node as PMNode } from "@tiptap/pm/model";
import type { DecorationSource } from "@tiptap/pm/view";
import type { EditorUiNodeViewOptions } from "@plane/editor/core";
import { NODE_VIEW_CONTEXT, type NodeViewContext } from "./node-view-context";

export interface AngularNodeViewRendererOptions extends EditorUiNodeViewOptions {
  injector: Injector;
  /** wie ReactNodeViewRendererOptions.contentDOMElementTag (Default span/div) */
  contentDOMElementTag?: string;
  update?: (p: { oldNode: PMNode; newNode: PMNode; oldDecorations: readonly DecorationWithType[];
                 newDecorations: readonly DecorationWithType[]; updateProps: () => void }) => boolean;
}

export class AngularNodeView extends NodeView<Type<unknown>, Editor, AngularNodeViewRendererOptions> {
  // WICHTIG: mount() läuft im Basiskonstruktor (NodeView.ts Z. 55), also VOR den Feld-Initialisierern dieser Klasse.
  // Deshalb nur `declare`-Felder (erzeugen keinen Code) und Initialisierung ausschließlich in mount();
  // Feld-Initialisierer (`= null`, `= new Set()`, Pfeil-Properties) würden die Werte aus mount() überschreiben.
  declare private outer: HTMLElement;
  declare private wrapper: HTMLElement;
  declare private contentDOMElement: HTMLElement | null;
  declare private componentRef: ComponentRef<unknown>;
  declare private inputNames: Set<string>;
  declare private isSelected: boolean;
  declare private onSelectionUpdate: () => void;

  override mount(): void {
    const tag = this.options.as ?? (this.node.isInline ? "span" : "div");
    this.outer = document.createElement(tag);
    // DOM-Parität zu @tiptap/react 2.26.1 (D10-ADR-05): Klassennamen bewusst unverändert
    this.outer.classList.add("react-renderer", ...`node-${this.node.type.name} ${this.options.className ?? ""}`.trim().split(/\s+/));
    this.contentDOMElement = null;
    if (!this.node.isLeaf) {
      this.contentDOMElement = document.createElement(this.options.contentDOMElementTag ?? (this.node.isInline ? "span" : "div"));
      this.contentDOMElement.dataset["nodeViewContentReact"] = ""; // wie ReactNodeViewRenderer.tsx Z. 83
      this.contentDOMElement.dataset["nodeViewWrapper"] = "";      // wie ReactNodeViewRenderer.tsx Z. 84
      this.contentDOMElement.style.whiteSpace = "inherit";
    }
    this.isSelected = false;
    this.onSelectionUpdate = () => this.handleSelectionUpdate();
    this.createComponentInWrapper();
    this.editor.on("selectionUpdate", this.onSelectionUpdate);
  }

  private createComponentInWrapper(): void {
    const { injector } = this.options;
    this.wrapper = document.createElement(this.options.wrapperAs ?? "div");
    this.wrapper.setAttribute("data-node-view-wrapper", "");
    this.wrapper.style.whiteSpace = "normal";
    this.wrapper.addEventListener("dragstart", (event) => this.onDragStart(event));
    this.outer.replaceChildren(this.wrapper);
    const context: NodeViewContext = { contentDOM: this.contentDOMElement };
    this.componentRef = createComponent(this.component, {
      environmentInjector: injector.get(EnvironmentInjector),
      elementInjector: Injector.create({ providers: [{ provide: NODE_VIEW_CONTEXT, useValue: context }], parent: injector }),
      hostElement: this.wrapper,
    });
    this.inputNames = new Set(reflectComponentType(this.component)?.inputs.map((i) => i.templateName) ?? []);
    this.setInputs({
      editor: this.editor, node: this.node, decorations: this.decorations, innerDecorations: this.innerDecorations,
      view: this.view, selected: this.isSelected, extension: this.extension, HTMLAttributes: this.HTMLAttributes,
      getPos: () => this.getPos(), updateAttributes: (a: Record<string, unknown>) => this.updateAttributes(a),
      deleteNode: () => this.deleteNode(),
    });
    injector.get(ApplicationRef).attachView(this.componentRef.hostView);
  }

  private setInputs(values: Record<string, unknown>): void {
    for (const [name, value] of Object.entries(values)) if (this.inputNames.has(name)) this.componentRef.setInput(name, value);
  }

  override get dom(): HTMLElement { return this.outer; }
  override get contentDOM(): HTMLElement | null { return this.node.isLeaf ? null : this.contentDOMElement; }

  /** wie ReactNodeView.handleSelectionUpdate: Bereichs-Selektion um den Node → selectNode(), sonst deselectNode() */
  private handleSelectionUpdate(): void {
    const { from, to } = this.editor.state.selection;
    const pos = this.getPos();
    if (typeof pos !== "number") return;
    if (from <= pos && to >= pos + this.node.nodeSize) { if (!this.isSelected) this.selectNode(); }
    else if (this.isSelected) this.deselectNode();
  }

  update(node: PMNode, decorations: readonly DecorationWithType[], innerDecorations: DecorationSource): boolean {
    if (node.type !== this.node.type) return false;
    const oldNode = this.node;
    const updateProps = () => this.setInputs({ node, decorations, innerDecorations });
    if (typeof this.options.update === "function") {
      const oldDecorations = this.decorations;
      this.node = node; this.decorations = decorations; this.innerDecorations = innerDecorations;
      return this.options.update({ oldNode, newNode: node, oldDecorations, newDecorations: decorations, updateProps });
    }
    if (node === this.node && this.decorations === decorations && this.innerDecorations === innerDecorations) return true;
    this.node = node; this.decorations = decorations; this.innerDecorations = innerDecorations;
    // React: key={attrs.id} am NodeViewWrapper → Neuaufbau des Komponentenbaums bei ID-Wechsel (§3.10)
    if (oldNode.attrs["id"] !== node.attrs["id"]) { this.destroyComponent(); this.createComponentInWrapper(); return true; }
    updateProps();
    return true;
  }

  selectNode(): void { this.isSelected = true; this.setInputs({ selected: true }); this.outer.classList.add("ProseMirror-selectednode"); }
  deselectNode(): void { this.isSelected = false; this.setInputs({ selected: false }); this.outer.classList.remove("ProseMirror-selectednode"); }

  private destroyComponent(): void {
    this.options.injector.get(ApplicationRef).detachView(this.componentRef.hostView);
    this.componentRef.destroy();
  }
  destroy(): void {
    this.editor.off("selectionUpdate", this.onSelectionUpdate);
    this.destroyComponent();
    this.contentDOMElement = null;
  }
}

export function AngularNodeViewRenderer(component: Type<unknown>, options: AngularNodeViewRendererOptions): NodeViewRenderer {
  return (props: NodeViewRendererProps) => new AngularNodeView(component, props, options);
}
```

`[plEdNodeViewContent]` (`node-view-content.directive.ts`) injiziert `NODE_VIEW_CONTEXT`, setzt am Host `data-node-view-content=""` und `style.whiteSpace = "pre-wrap"` und hängt `contentDOM` per `appendChild` ein (Gegenstück zu `nodeViewContentRef` in React).

### 5.4 `AngularRenderer` und Port-Implementierung

```ts
// ED/angular-binding/src/angular-renderer.ts
export class AngularRenderer<C, P extends object> implements EditorUiHandle<P, C> {
  readonly element: HTMLElement;
  readonly ref: C;
  private readonly componentRef: ComponentRef<C>;
  private readonly inputNames: Set<string>;

  constructor(component: Type<C>, private readonly injector: Injector, props: P,
              options: { as?: string; className?: string } = {}) {
    this.element = document.createElement(options.as ?? "div");
    this.element.classList.add("react-renderer", ...(options.className ?? "").split(" ").filter(Boolean));
    this.componentRef = createComponent(component, {
      environmentInjector: injector.get(EnvironmentInjector), elementInjector: injector, hostElement: this.element,
    });
    this.inputNames = new Set(reflectComponentType(component)?.inputs.map((i) => i.templateName) ?? []);
    injector.get(ApplicationRef).attachView(this.componentRef.hostView);
    this.updateProps(props);
    this.ref = this.componentRef.instance;
  }

  updateProps(props: Partial<P>): void {
    for (const [k, v] of Object.entries(props)) if (this.inputNames.has(k)) this.componentRef.setInput(k, v);
    // synchron rendern, weil Aufrufer (floating-ui) direkt danach misst (D10-ADR-10)
    this.componentRef.changeDetectorRef.detectChanges();
  }

  destroy(): void {
    this.injector.get(ApplicationRef).detachView(this.componentRef.hostView);
    this.componentRef.destroy();
    this.element.remove();
  }
}
```

```ts
// ED/angular-binding/src/ui-port.extension.ts
export const PlaneUiPortExtension = Extension.create<{ port: EditorUiPort | null }, { port: EditorUiPort | null }>({
  name: UI_PORT_EXTENSION_NAME,
  addOptions: () => ({ port: null }),
  addStorage() { return { port: this.options.port }; },
});

export class AngularUiPort implements EditorUiPort {
  constructor(private readonly injector: Injector, private readonly components: ReadonlyMap<EditorUiKey, Type<unknown>>) {}
  createNodeView(key: EditorUiKey, options?: EditorUiNodeViewOptions): NodeViewRenderer | null {
    const component = this.components.get(key);
    return component ? AngularNodeViewRenderer(component, { ...options, injector: this.injector }) : null;
  }
  render<P extends object, R>(key: EditorUiKey, _editor: Editor, props: P, options?: { as?: string; className?: string }) {
    const component = this.components.get(key) as Type<R> | undefined;
    return component ? new AngularRenderer<R, P>(component, this.injector, props, options) : null;
  }
}
```

```ts
// ED/components/src/ui-port/ui-component-map.ts
export const CE_EDITOR_UI_COMPONENTS: ReadonlyArray<readonly [EditorUiKey, Type<unknown>]> = [
  ["callout-block", PlEdCalloutBlock],
  ["code-block", PlEdCodeBlockNodeView],
  ["custom-image", PlEdCustomImageNodeView],
  ["mention", PlEdMentionNodeView],
  ["slash-commands-menu", PlEdSlashCommandsMenu],
  ["mentions-list-dropdown", PlEdMentionsListDropdown],
  ["emojis-list-dropdown", PlEdEmojisListDropdown],
  ["table-column-drag-handle", PlEdTableColumnDragHandle],
  ["table-row-drag-handle", PlEdTableRowDragHandle],
];

export const EDITOR_UI_COMPONENTS = new InjectionToken<ReadonlyMap<EditorUiKey, Type<unknown>>>("EDITOR_UI_COMPONENTS", {
  providedIn: "root",
  factory: () => {
    const map = new Map<EditorUiKey, Type<unknown>>(CE_EDITOR_UI_COMPONENTS);
    for (const block of getEditorBlocks()) {
      for (const [key, component] of Object.entries(block.ui ?? {})) {
        if (map.has(key as EditorUiKey)) throw new Error(`Duplicate editor UI key: ${key}`);
        map.set(key as EditorUiKey, component as Type<unknown>);
      }
    }
    return map;
  },
});
```

### 5.5 `EditorContent`-Direktive und `editorState()`

```ts
// ED/angular-binding/src/editor-content.directive.ts
@Directive({ selector: "[plEdEditorContent]" })
export class EditorContentDirective {
  readonly editor = input.required<Editor | null>({ alias: "plEdEditorContent" });
  private readonly host = inject<ElementRef<HTMLElement>>(ElementRef);
  constructor() {
    effect((onCleanup) => {
      const editor = this.editor();
      if (!editor || editor.isDestroyed || !editor.options.element) return;
      const host = this.host.nativeElement;
      // wie EditorContent.init() (@tiptap/react 2.26.1, EditorContent.tsx Z. 123–163)
      host.append(...Array.from(editor.options.element.childNodes));
      editor.setOptions({ element: host });
      editor.createNodeViews(); // NodeViews im eingehängten DOM neu erzeugen (Messungen, gleiche Mount-Zyklen)
      onCleanup(() => {
        // wie componentWillUnmount: NodeViews abbauen, DOM in ein frisches div zurückgeben
        if (!editor.isDestroyed) editor.view.setProps({ nodeViews: {} });
        if (!host.firstChild) return;
        const detached = document.createElement("div");
        detached.append(...Array.from(host.childNodes));
        editor.setOptions({ element: detached });
      });
    });
  }
}

// ED/angular-binding/src/editor-state.ts
import deepEqual from "fast-deep-equal/es6"; // Default wie useEditorState (@tiptap/react 2.26.1, Z. 2/168)

export function editorState<T>(editor: Signal<Editor | null>, selector: (ctx: { editor: Editor }) => T,
                               equal: (a: T, b: T) => boolean = deepEqual): Signal<T | undefined> {
  const state = signal<T | undefined>(undefined, { equal: (a, b) => a !== undefined && b !== undefined && equal(a, b) });
  effect((onCleanup) => {
    const e = editor();
    if (!e) return;
    const update = () => state.set(selector({ editor: e }));
    update();
    e.on("transaction", update);
    onCleanup(() => e.off("transaction", update));
  });
  return state.asReadonly();
}
```

### 5.6 Variante `PlEdRichTextEditor` und `EditorInstance`

```ts
// ED/components/src/components/editors/rich-text/editor.component.ts
@Component({
  selector: "pl-ed-rich-text-editor",
  host: { "data-pl-host": "" }, // display:contents global über [data-pl-host] (D09, UI-DEV-000)
  changeDetection: ChangeDetectionStrategy.OnPush,
  encapsulation: ViewEncapsulation.None,
  providers: [EditorInstance],
  imports: [PlEdEditorWrapper, PlEdEditorBubbleMenu, PlEdBlockMenu],
  template: `
    <pl-ed-editor-wrapper [instance]="instance" [containerClassName]="containerClassName()" [id]="id()"
                          [displayConfig]="displayConfig()" [isTouchDevice]="isTouchDevice()">
      @if (instance.editor(); as editor) {
        @if (bubbleMenuEnabled() && editor.isEditable) { <pl-ed-editor-bubble-menu [editor]="editor" /> }
        <pl-ed-block-menu [editor]="editor" [flaggedExtensions]="flaggedExtensions()"
                          [disabledExtensions]="disabledExtensions()" [workItemIdentifier]="workItemIdentifier()" />
      }
    </pl-ed-editor-wrapper>`,
})
export class PlEdRichTextEditor {
  // Inputs = Props (§3.6.2)
  readonly id = input.required<string>();
  readonly editable = input.required<boolean>();
  readonly initialValue = input.required<string>();
  readonly value = input<string | null>(null);
  readonly disabledExtensions = input.required<TExtensions[]>();
  readonly flaggedExtensions = input.required<TExtensions[]>();
  readonly fileHandler = input.required<TFileHandler>();
  readonly mentionHandler = input.required<TMentionHandler>();
  readonly getEditorMetaData = input.required<(html: string) => TCustomComponentsMetaData>();
  readonly extendedEditorProps = input.required<IEditorPropsExtended>();
  readonly bubbleMenuEnabled = input<boolean>(true);
  readonly dragDropEnabled = input<boolean>(false);
  readonly extensions = input<Extensions>([]);
  readonly displayConfig = input<TDisplayConfig>(DEFAULT_DISPLAY_CONFIG);
  readonly containerClassName = input<string>();
  readonly editorClassName = input<string>();
  readonly placeholder = input<string | ((isFocused: boolean, value: string) => string)>();
  readonly showPlaceholderOnEmpty = input<boolean>(false);
  readonly tabIndex = input<number>();
  readonly isTouchDevice = input<boolean>(false);
  readonly autofocus = input<boolean>(false);
  readonly workItemIdentifier = input<string | null>(null);
  // Outputs (D10-ADR-08)
  readonly editorChange = output<TEditorChangeEvent>();
  readonly editorFocus = output<void>();
  readonly editorTransaction = output<void>();
  readonly editorReady = output<boolean>();
  readonly editorAssetChange = output<TEditorAsset[]>();

  protected readonly instance = inject(EditorInstance);
  /** Ersatz für forwardedRef (EditorRefApi, §3.8) */
  readonly ref = this.instance.ref;

  constructor() {
    this.instance.bind({
      variant: "rich",
      host: this,
      variantExtensions: () => [
        ...this.extensions(),
        SideMenuExtension({ aiEnabled: false, dragDropEnabled: this.dragDropEnabled() }),
        ...RichTextEditorAdditionalExtensions({
          disabledExtensions: this.disabledExtensions(), flaggedExtensions: this.flaggedExtensions(),
          fileHandler: this.fileHandler(), extendedEditorProps: this.extendedEditorProps(),
        }),
      ],
    });
  }
}
```

```ts
// ED/components/src/services/editor-instance.ts (Port use-editor.ts)
@Injectable()
export class EditorInstance {
  private readonly injector = inject(Injector);
  private readonly uiComponents = inject(EDITOR_UI_COMPONENTS);
  private readonly destroyRef = inject(DestroyRef);
  readonly editor = signal<Editor | null>(null);
  readonly ref = signal<EditorRefApi | null>(null);

  bind(cfg: EditorInstanceConfig): void {
    const port = new AngularUiPort(this.injector, this.uiComponents);
    let lastEditable: boolean | undefined;
    // (1)+(2) Erzeugen und Neuaufbau nur bei editable-Wechsel
    afterNextRender(() => {
      effect(() => {
        const editable = cfg.host.editable();
        if (editable === lastEditable) return;
        lastEditable = editable;
        untracked(() => this.recreate(cfg, port, editable));
      }, { injector: this.injector });
    });
    // (3) externer value-Sync
    effect(() => {
      const value = cfg.host.value?.();
      const editor = this.editor();
      cfg.host.id();
      if (value == null || !editor || editor.isDestroyed) return;
      if (editor.storage.utility?.uploadInProgress) return;
      untracked(() => {
        try {
          editor.commands.setContent(value, false, { preserveWhitespace: true });
          if (editor.state.selection) { // Position NACH setContent lesen (use-editor.ts)
            editor.commands.setTextSelection(Math.min(editor.state.selection.from, editor.state.doc.content.size - 1));
          }
        } catch (error) {
          console.error("Error syncing editor content with external value:", error);
        }
      });
    });
    // (4) Upload-Status, (5) Assetliste
    effect(() => { const e = this.editor(); const s = cfg.host.fileHandler().assetsUploadStatus; if (e && s) e.commands.updateAssetsUploadStatus(s); });
    const assets = editorState(this.editor, ({ editor }) => editor.storage.utility?.assetsList as TEditorAsset[] | undefined);
    effect(() => { const a = assets(); if (a) untracked(() => cfg.host.editorAssetChange.emit(a)); });
    this.destroyRef.onDestroy(() => this.editor()?.destroy());
  }

  private recreate(cfg: EditorInstanceConfig, port: AngularUiPort, editable: boolean): void {
    sealEditorBlockRegistry(); // ab dem ersten Editor sind Paket-Registrierungen verboten (§5.10)
    this.editor()?.destroy();
    const h = cfg.host;
    const editor = new Editor({
      editable, autofocus: h.autofocus(), injectCSS: false, parseOptions: { preserveWhitespace: true },
      editorProps: { ...CoreEditorProps({ editorClassName: h.editorClassName() ?? "" }), ...(h.editorProps?.() ?? {}) },
      extensions: [
        ...CoreEditorExtensions({
          disabledExtensions: h.disabledExtensions(), flaggedExtensions: h.flaggedExtensions(), fileHandler: h.fileHandler(),
          getEditorMetaData: h.getEditorMetaData(), isTouchDevice: h.isTouchDevice(), mentionHandler: h.mentionHandler(),
          placeholder: h.placeholder(), showPlaceholderOnEmpty: h.showPlaceholderOnEmpty(), tabIndex: h.tabIndex(),
          extendedEditorProps: h.extendedEditorProps(), enableHistory: cfg.enableHistory ?? true, editable,
          provider: cfg.provider?.() ?? undefined,
        }),
        ...cfg.variantExtensions(),
        PlaneUiPortExtension.configure({ port }),
      ],
      content: h.initialValue?.() ?? cfg.content?.(),
      onCreate: () => h.editorReady.emit(true),
      onDestroy: () => h.editorReady.emit(false),
      onFocus: () => h.editorFocus.emit(),
      onTransaction: () => h.editorTransaction.emit(),
      onUpdate: ({ editor: e, transaction }) => h.editorChange.emit({
        json: e.getJSON(), html: e.getHTML(), isMigrationUpdate: transaction.getMeta("uniqueIdOnlyChange") === true,
      }),
    });
    this.editor.set(editor);
    this.ref.set(getEditorRefHelpers({ editor, getEditorMetaData: h.getEditorMetaData(), provider: cfg.provider?.() }));
  }
}
```

### 5.7 NodeView-Komponente (Beispiel Callout)

```ts
// ED/components/src/extensions/callout/block.component.ts (Port block.tsx)
@Component({
  selector: "[plEdCalloutBlock]",
  changeDetection: ChangeDetectionStrategy.OnPush,
  encapsulation: ViewEncapsulation.None,
  imports: [PlEdCalloutLogoSelector, PlEdCalloutColorSelector, NodeViewContentDirective],
  host: {
    class: "editor-callout-component group/callout-node relative my-2 flex items-start gap-4 rounded-lg bg-layer-3 p-4 break-words text-primary transition-colors duration-500",
    "[style.background-color]": "activeBackgroundColor()",
  },
  template: `
    <pl-ed-callout-logo-selector [blockAttributes]="node().attrs" [disabled]="!editor().isEditable"
      [isOpen]="isEmojiPickerOpen()" (handleOpen)="isEmojiPickerOpen.set($event)" [updateAttributes]="updateAttributes()" />
    <pl-ed-callout-color-selector [disabled]="!editor().isEditable" [isOpen]="isColorPickerOpen()"
      (toggleDropdown)="isColorPickerOpen.update(v => !v)" (selected)="onColorSelect($event)" />
    <div plEdNodeViewContent class="w-full break-words"></div>`,
})
export class PlEdCalloutBlock {
  readonly editor = input.required<Editor>();
  readonly node = input.required<PMNode>();
  readonly updateAttributes = input.required<(attrs: Partial<TCalloutBlockAttributes>) => void>();
  protected readonly isEmojiPickerOpen = signal(false);
  protected readonly isColorPickerOpen = signal(false);
  protected readonly activeBackgroundColor = computed(
    () => COLORS_LIST.find((c) => this.node().attrs["data-background"] === c.key)?.backgroundColor ?? null);
  protected onColorSelect(val: string | null): void {
    this.updateAttributes()({ [ECalloutAttributeNames.BACKGROUND]: val });
    updateStoredBackgroundColor(val);
  }
}
```

⚠ `pl-ed-callout-logo-selector`/`pl-ed-callout-color-selector` sind im Original eigene Elemente (`CalloutBlockLogoSelector` rendert ein Wurzel-`div`); die Angular-Komponenten werden deshalb als Attribut-Selektor auf diesem Wurzel-`div` umgesetzt, sobald das S5-DOM-Golden die Wurzelelemente bestätigt (Regel D09-ADR-03).

### 5.8 `CollaborationSession` (`ED/collaboration/src/collaboration-session.ts`)

```ts
export type CollabStage =
  | { kind: "initial" } | { kind: "connecting" } | { kind: "awaiting-sync" } | { kind: "synced" }
  | { kind: "reconnecting"; attempt: number } | { kind: "disconnected"; error: CollaborationError };

const DEFAULT_MAX_RETRIES = 3;
const FORCED_CLOSE_CODES = new Set([4000, 4001, 4002, 4003]); // LIVE/types/admin-commands.ts

@Injectable()
export class CollaborationSession {
  private readonly factory = inject(CollaborationProviderFactory);
  readonly stage = signal<CollabStage>({ kind: "initial" });
  readonly isCacheReady = signal(false);
  readonly hasCachedContent = signal(false);
  readonly isServerSynced = computed(() => this.stage().kind === "synced");
  readonly isServerDisconnected = computed(() => this.stage().kind === "disconnected");
  readonly isDocReady = computed(() => this.isServerSynced() || this.isServerDisconnected() || (this.isCacheReady() && this.hasCachedContent()));
  readonly authorizedScope = signal<"read-write" | "readonly" | undefined>(undefined); // onAuthenticated: = provider.authorizedScope (17 ABG-113)
  private provider: HocuspocusProviderLike | null = null;
  private retry = 0;
  private disposed = false;

  start(cfg: { docId: string; serverUrl: string; authToken: string; onStateChange?: (s: CollaborationState) => void }): void {
    // 1:1 zu use-yjs-setup.ts: Provider anlegen (Callbacks onAuthenticationFailed/onConnect/onStatus/onSynced/onClose),
    // IndexedDB-Persistenz, observeDeep("default") für hasCachedContent, Listener visibilitychange/focus (Throttle 1 s) und online
  }
  private handleClose(code: number | undefined): void {
    const forced = (code !== undefined && FORCED_CLOSE_CODES.has(code)) || this.provider?.shouldConnect === false;
    if (forced) { this.stage.set({ kind: "disconnected", error: { type: "forced-close", code, message: code ? "Server forced connection close" : "Manually disconnected" } }); if (code) this.pauseProvider(); return; }
    this.retry += 1;
    if (this.retry >= DEFAULT_MAX_RETRIES) { this.stage.set({ kind: "disconnected", error: { type: "max-retries", message: `Failed to connect after ${DEFAULT_MAX_RETRIES} attempts` } }); this.pauseProvider(); return; }
    this.stage.set({ kind: "reconnecting", attempt: this.retry });
  }
  pauseProvider(): void { /* shouldConnect=false; disconnect() */ }
  dispose(): void { this.disposed = true; /* Listener entfernen, permanentlyStopProvider() */ }
}
```

`CollaborationError`/`CollaborationState` sind die Original-Typen aus `ED/core/src/types/collaboration.ts` (1:1); die Signal-Form ist nur die Hülle.

### 5.9 Schema-Serialisierer und Golden-Test

```ts
// ED/core/src/testing/schema-serializer.ts – identische Kopie im Golden-Generator (G-EDCORE prüft)
const EXCLUDED_EXTENSIONS = new Set(["planeUiPort"]);

export interface SerializedEditor {
  schema: { topNode: string; nodes: SerializedSpec[]; marks: SerializedSpec[] };
  extensions: Array<{ name: string; type: string; priority: number }>;
  plugins: string[];
}
interface SerializedSpec { name: string; spec: Record<string, unknown>; attrs: Record<string, { default?: unknown; hasDefault: boolean }> }

export function serializeEditor(editor: Editor): SerializedEditor {
  const s = editor.schema;
  const spec = (name: string, t: NodeType | MarkType): SerializedSpec => ({
    name,
    attrs: Object.fromEntries(Object.entries(t.spec.attrs ?? {}).map(([k, a]) => [k, "default" in a ? { default: a.default, hasDefault: true } : { hasDefault: false }])),
    spec: Object.fromEntries(Object.entries(t.spec)
      .filter(([k]) => !["attrs", "toDOM", "leafText"].includes(k))
      .map(([k, v]) => [k, k === "parseDOM" ? (v as ParseRule[]).map(serializeParseRule) : typeof v === "function" ? "[function]" : v])),
  });
  return {
    schema: { topNode: s.topNodeType.name, nodes: [...s.spec.nodes.keys()].map((n) => spec(n, s.nodes[n])), marks: [...s.spec.marks.keys()].map((m) => spec(m, s.marks[m])) },
    extensions: editor.extensionManager.extensions.filter((e) => !EXCLUDED_EXTENSIONS.has(e.name))
      // getExtensionField löst die extend()-Kette auf (z. B. CustomQuoteExtension = Blockquote.extend); e.config allein verfehlt geerbte Werte
      .map((e) => ({ name: e.name, type: e.type, priority: getExtensionField<number>(e, "priority") ?? 100 })),
    // Plugins ohne PluginKey heißen "plugin$", "plugin$1", … (globaler Zähler in prosemirror-state createKey) –
    // die Nummer hängt davon ab, wie viele Editoren vorher im selben Prozess erzeugt wurden → auf "plugin$" normalisieren.
    // Gleiches gilt für benannte Keys mit Zählerendung ("suggestion$1" bei mehreren Suggestion-Plugins): Suffix entfernen.
    plugins: editor.state.plugins.map((p) => (p as unknown as { key: string }).key.replace(/\$\d*$/, "$")),
  };
}
function serializeParseRule(r: ParseRule): Record<string, unknown> {
  return { tag: (r as TagParseRule).tag, style: (r as StyleParseRule).style, priority: r.priority, context: r.context,
           consuming: r.consuming, preserveWhitespace: (r as TagParseRule).preserveWhitespace, hasGetAttrs: typeof r.getAttrs === "function" };
}
```

```ts
// ED/core/src/testing/schema-golden.spec.ts  (Vitest-Projekt shared-dom)
const GOLDEN_DIR = resolve(__dirname, "../../../../../../../tests/Plane.Documents.Tests/Golden/schema");
describe("G-SCHEMA (CE-PAGE-021, CE-PAGE-022, CE-PAGE-023)", () => {
  it.each(["rich", "lite", "document"] as const)("Browser-Variante %s entspricht dem Original", (variant) => {
    const editor = createSchemaProbe(variant); // Stub-Handler aus testing/stub-handlers.ts, Extension-Liste §3.2.3
    const actual = serializeEditor(editor);
    expect(actual.schema).toEqual(readJson(`${GOLDEN_DIR}/browser/${variant}.schema.json`));
    expect(actual.extensions).toEqual(readJson(`${GOLDEN_DIR}/browser/${variant}.extensions.json`));
    expect(actual.plugins).toEqual(readJson(`${GOLDEN_DIR}/browser/${variant}.plugins.json`));
    editor.destroy();
  });
  it.each([["server", "rich"], ["server-document", "document"]] as const)("TS-Server-Schema %s = D07-Golden %s", (variant, golden) => {
    const editor = createSchemaProbe(variant);
    expect(serializeEditor(editor).schema).toEqual(readJson(`${GOLDEN_DIR}/${golden}.schema.json`));
    editor.destroy();
  });
});
```

### 5.10 Erweiterbarkeit: Block-Registry und Tokens

```ts
// ED/core/src/extensibility/editor-block-definition.ts
export type TEditorBlockKey = `${string}:${string}`; // z. B. "d9:drawio"

export interface EditorBlockDefinition {
  readonly key: TEditorBlockKey;
  /** optionaler Schalter in disabledExtensions/EDITOR_FLAGS (z. B. "d9:drawio") */
  readonly flag?: string;
  /** Tiptap-Extensions je Andockpunkt des Originals */
  readonly extensions?: {
    readonly core?: (p: TCoreAdditionalExtensionsProps) => Extensions;                 // → CoreEditorAdditionalExtensions (alle Varianten)
    readonly richText?: (p: TRichTextEditorAdditionalExtensionsProps) => Extensions;   // → RichTextEditorAdditionalExtensions
    readonly document?: (p: TDocumentEditorAdditionalExtensionsProps) => Extensions;   // → DocumentEditorAdditionalExtensions (S50)
    readonly serverSchema?: () => Extensions;                                          // → CoreEditorAdditionalExtensionsWithoutProps (Golden)
  };
  /** Slash-Einträge mit section + pushAfter (S49) */
  readonly slashCommands?: (p: Pick<IEditorProps, "disabledExtensions" | "flaggedExtensions">) => TSlashCommandAdditionalOption[];
  /** zusätzliche Block-Node-Typen für UniqueID (ADDITIONAL_BLOCK_NODE_TYPES) */
  readonly blockNodeTypes?: readonly string[];
  /** zusätzliche Selektoren für das Drag-Handle (generalSelectors in plugins/drag-handle.ts) */
  readonly sideMenuSelectors?: readonly string[];
  /** Asset-Metadaten je Node (ADDITIONAL_ASSETS_META_DATA_RECORD) */
  readonly assetMetaData?: Readonly<Record<string, TAssetMetaDataRecord>>;
  /** Asset-Extraktion/-Ersetzung für Duplizieren (helpers/parser.ts) */
  readonly extractAssets?: (html: string) => string[];
  readonly replaceAssets?: (html: string, replacements: Readonly<Record<string, string>>) => string;
  /** Datei-Drop/-Paste für nicht-Bild-Dateien (plugins/drop.ts, Attachment-Zweig, E23) */
  readonly fileDropHandlers?: ReadonlyArray<{ accepts: (file: File) => boolean; insert: (args: { editor: Editor; file: File; pos: number }) => boolean }>;
  /** zusätzliche Menü-Items für executeMenuItemCommand/isMenuItemActive (TExtendedEditorCommands) */
  readonly menuItems?: (editor: Editor) => ReadonlyArray<EditorMenuItem<TEditorCommands>>;
  /** zusätzliche Einträge im Block-Menü (Drag-Handle-Menü, components/menus/block-menu-options.ts) */
  readonly blockMenuOptions?: (editor: Editor) => ReadonlyArray<TBlockMenuOption>;
  /** Markdown-Handler für convertHTMLToMarkdown (utils/editor/markdown-parser/custom-components-handler.ts) */
  readonly markdownHandlers?: Readonly<Record<string, unknown>>;
  /** UI-Port-Schlüssel → Angular-Komponente (Typ im Kern unbekannt) */
  readonly ui?: Readonly<Record<TEditorBlockKey, unknown>>;
}

// ED/core/src/extensibility/block-registry.ts
// Lesen ist jederzeit erlaubt (vor der Registrierung: CE-Ergebnis []), versiegelt wird EXPLIZIT beim ersten Editor
// (EditorInstance/TitleEditorInstance.recreate → sealEditorBlockRegistry()). Ein „Versiegeln beim ersten Lesen“ wäre falsch:
// Modul-Importe (z. B. UniqueID, yjs-utils) lesen schon vor provideAppInitializer.
let blocks: readonly EditorBlockDefinition[] = [];
let sealed = false;
export function registerEditorBlocks(defs: readonly EditorBlockDefinition[]): void {
  if (sealed) throw new Error("Editor blocks must be registered before the first editor is created");
  const keys = new Set<string>();
  for (const d of defs) { if (keys.has(d.key)) throw new Error(`Duplicate editor block: ${d.key}`); keys.add(d.key); }
  blocks = Object.freeze([...defs]);
}
export function getEditorBlocks(): readonly EditorBlockDefinition[] { return blocks; }
export function sealEditorBlockRegistry(): void { sealed = true; }
export function isBlockEnabled(b: EditorBlockDefinition, disabled: readonly string[]): boolean { return !b.flag || !disabled.includes(b.flag); }
/** nur Tests */ export function resetEditorBlockRegistryForTests(): void { blocks = []; sealed = false; }
```

Nutzung im Kern (Beispiele, jeweils `PORT-DIFF(block-registry)`):

```ts
// ED/core/src/extensions/core/extensions.ts
export const CoreEditorAdditionalExtensions = (props: TCoreAdditionalExtensionsProps): Extensions =>
  getEditorBlocks().filter((b) => isBlockEnabled(b, props.disabledExtensions)).flatMap((b) => b.extensions?.core?.(props) ?? []);

// ED/core/src/constants/extensions.ts
export enum ADDITIONAL_EXTENSIONS {}
export const getAdditionalBlockNodeTypes = (): string[] => getEditorBlocks().flatMap((b) => b.blockNodeTypes ?? []);
export const ADDITIONAL_BLOCK_NODE_TYPES = [] as string[]; // 1:1 belassen, CE-Wert; Leser nutzen den Getter

// ED/core/src/extensions/core-without-props.ts (K2, R-ED-12) – Original-Konstanten bleiben (CE-Golden), zusätzlich Getter
export const getCoreEditorExtensionsWithoutProps = (): Extensions => [
  ...CoreEditorExtensionsWithoutProps,
  ...getEditorBlocks().flatMap((b) => b.extensions?.serverSchema?.() ?? []),
];
export const getDocumentEditorExtensionsWithoutProps = (): Extensions => [...DocumentEditorExtensionsWithoutProps];

// ED/core/src/helpers/yjs-utils.ts (K2, R-ED-12) – Modul-Konstanten → Aufruf zur Laufzeit
// const RICH_TEXT_EDITOR_EXTENSIONS = CoreEditorExtensionsWithoutProps;            (Original)
const getRichTextEditorExtensions = () => getCoreEditorExtensionsWithoutProps();   // PORT-DIFF(block-registry)
const getDocumentEditorExtensions = () => [...getCoreEditorExtensionsWithoutProps(), ...getDocumentEditorExtensionsWithoutProps()];
```

Damit `CoreEditorExtensionsWithoutProps` selbst unverändert bleibt, liest `ED/core/src/extensions/core/without-props.ts` die Registry **nicht** (die Original-Konstante `CoreEditorAdditionalExtensionsWithoutProps = []` bleibt); Paket-Server-Schema-Extensions fließen ausschließlich über die Getter ein.

```ts
// ED/extensibility/src/tokens.ts
export interface EditorExtensionContribution {
  readonly key: string;
  /** Datei-Handler-Beiträge (S15, getExtendedEditorFileHandlers) */
  readonly fileHandlers?: (ctx: { projectId?: string; workspaceSlug: string }) => Partial<TExtendedFileHandler>;
  /** extendedEditorProps-Beiträge (S16, useExtendedEditorProps) */
  readonly extendedEditorProps?: (ctx: { workspaceSlug: string; projectId?: string; pageId?: string }) => Partial<Record<string, unknown>>;
  /** Seiteneffekt-Komponenten im Document-Editor (S60, DocumentEditorSideEffects) */
  readonly sideEffects?: readonly Type<unknown>[];
  /** Gültigkeitsbereich */
  readonly scope: "web" | "space" | "both";
}
export interface EditorMentionTypeDefinition {
  readonly entityName: TSearchEntities | `${string}:${string}`;
  readonly section: { key: string; title: string };
  readonly toSuggestions: (result: unknown) => TMentionSuggestion[];
  readonly render: (p: { entity_identifier: string; entity_name: string }) => TEditorRenderable<Type<unknown>>;
}
export type EditorFlagsResolver = (ctx: { workspaceSlug: string; projectId?: string; storeType?: string }) => TEditorFlaggingHookReturnType;

export const EDITOR_BLOCKS = new InjectionToken<readonly EditorBlockDefinition[][]>("EDITOR_BLOCKS");          // multi
export const EDITOR_EXTENSIONS = new InjectionToken<readonly EditorExtensionContribution[]>("EDITOR_EXTENSIONS"); // multi
export const EDITOR_MENTION_TYPES = new InjectionToken<readonly EditorMentionTypeDefinition[]>("EDITOR_MENTION_TYPES"); // multi
export const EDITOR_FLAGS = new InjectionToken<EditorFlagsResolver>("EDITOR_FLAGS", { providedIn: "root", factory: () => CE_EDITOR_FLAGS });

export const CE_EDITOR_FLAGS: EditorFlagsResolver = () => ({ // WEB/hooks/use-editor-flagging.ts 1:1
  document: { disabled: ["ai", "collaboration-cursor"], flagged: [] },
  liteText: { disabled: ["ai", "collaboration-cursor"], flagged: [] },
  richText: { disabled: ["ai", "collaboration-cursor"], flagged: [] },
});

// ED/extensibility/src/provide-editor-defaults.ts
export function provideEditorDefaults(): EnvironmentProviders {
  return makeEnvironmentProviders([
    provideAppInitializer(() => {
      const defs = inject(EDITOR_BLOCKS, { optional: true }) ?? [];
      registerEditorBlocks(defs.flat());
    }),
  ]);
}
export function provideEditorBlocks(...defs: EditorBlockDefinition[]): EnvironmentProviders {
  return makeEnvironmentProviders([{ provide: EDITOR_BLOCKS, multi: true, useValue: defs }]);
}
```

Die Web-Hülle stellt den CE-Mention-Typ bereit (`provideWebExtensions()` → `{ provide: EDITOR_MENTION_TYPES, multi: true, useValue: WEB_USER_MENTION_TYPE }` mit `entityName: "user_mention"`, Render-Komponente `PlWebEditorUserMention`); Space analog mit `PlSpcEditorUserMention`. Damit ergibt die Liste der `entityName`-Werte in der CE genau `["user_mention"]` (D08 §6.1).

### 5.11 Server-Gegenstück (Eigentümer D07)

Das Server-Schema (`IDocumentNodeSpec`/`IDocumentMarkSpec`, `AttributeSpec`, `ParseRule`, DI-Sammlung E-11) ist in D07 §3.12.2 festgelegt; die Klassennamen je Node/Mark stehen in D07 §3.13 und in §4.1 dieses Dokuments. Verbindlich zwischen D07 und D10 ist: (a) Menge, Namen und Reihenfolge der Nodes/Marks entsprechen §4.1, (b) das TS-Server-Schema des Kerns (`CoreEditorExtensionsWithoutProps`, `DocumentEditorExtensionsWithoutProps`, `TitleExtensions`) und das C#-Schema serialisieren beide gleich den D07-Goldens `rich`/`document`/`title.schema.json` (Format §5.9), (c) Paket-Blöcke registrieren ihre Specs additiv per DI und ihre TS-Extensions über `EditorBlockDefinition.extensions.serverSchema` (§5.10).

---

## 6. Erweiterungspunkte für Bezahl-Pakete

> Kein Fachdesign. Hier steht nur, **wo** der CE-Editor Pakete andocken lässt, welche Klasse die Andockstelle nach D16 §1.5 hat (P = CE-Pflicht mit Default + Test, V = durch 1:1-Port vorhanden, R = reserviert, S = später additiv) und ab welchem Inkrement sie vorhanden sein muss.

### 6.1 Strukturrelevante Pakete (🧱, F30) – Editor-Bezug

| Paket | Editor-Andockstelle in der CE | Klasse | Ort | ab | CE-Default (= Original-Verhalten) |
|---|---|---|---|---|---|
| **A1** Work-Item-Types & Custom Properties | keine Editor-Änderung; Rich-Text-Properties nutzen die Hülle `PlWebRichTextEditor` als Renderer über `PROPERTY_RENDERERS` (D08) | – | – | – | – |
| **A2** Workspace-Types, Hierarchie | keine | – | – | – | – |
| **A9** Relationen | keine (Work-Item-Embeds gehören zu D6) | – | – | – | – |
| **A17** Governance States/Labels | keine | – | – | – | – |
| **B1** Teamspaces | (a) Dokumenttyp im Realtime-URL-Query (`documentType=teamspace_page`, `teamId`) wird von der Page-Hülle gebaut, Editor unverändert; (b) Typen `TEditorAssetType` (`TEAM_SPACE_DESCRIPTION`), `CommonRealtimeFields.teamspace_id`, `BroadcastedEvent.teamspace_id` bleiben 1:1; (c) `EDITOR_EXTENSIONS.extendedEditorProps` erhält `teamspaceId` im Kontext | V (a, b), P (c: Kontextfeld `teamspaceId?` im Typ, CE `undefined`) | `ED/core/src/types/*`, `ED/extensibility/src/tokens.ts`, Page-Hülle | I4 | `project_page` |
| **B6** Erweiterte Filter/PQL | keine | – | – | – | – |
| **C1** Workflows (nicht gewählt) | keine | – | – | – | – |
| **C3** Automation (nicht gewählt) | keine | – | – | – | – |
| **D1** Wiki & Collections | (a) Dokumenttyp `workspace_page` im URL-Query (Page-Hülle, Server-Registry E-10, D07); (b) Editor-Tokens gelten unabhängig vom Page-Store (`injectPageStore(type)`, D08); (c) `EDITOR_EXTENSIONS.scope` | V (a), P (b, c) | Page-Hülle, `ED/extensibility` | I4 | nur `project_page` |
| **D2** Nested Pages | (a) Stateless-Kanal `listenToRealTimeUpdate()` reicht JSON-`BroadcastedEvent` inkl. `affectedPages` unverändert durch (Auswertung in `RealtimePageEventsService`); (b) Seiteneffekt-Slot `PlEdDocumentEditorSideEffects` rendert `EDITOR_EXTENSIONS.sideEffects` (S60); (c) Input `updatePageProperties` am Collaborative-Editor (1:1) | V (a, c), P (b, CE leer) | `ED/core/src/helpers/editor-ref.ts`, `ED/components/src/components/document-editor-side-effects.component.ts` | I4 | kein Seiteneffekt |
| **E3** IdP Group Sync | keine | – | – | – | – |
| **E5** Rollenmodell | `editable` wird ausschließlich von den Hüllen aus `PermissionService.allowPermissions(...)` bzw. dem Realtime-Scope `readonly` abgeleitet; der Editor kennt keine Rollen | P (Regel, Architekturtest „keine Rollenlogik in `ED/**`“) | Hüllen | I2 | rollenbasiert wie Original |
| **F1** Integrations-Framework | Link-Hover-Vorschau: `PlEdLinkViewContainer` fragt `linkPreviewProviders` (aus `INTEGRATION_LINK_PREVIEWS`, D08) vor der Standardansicht | P | `ED/components/src/components/editors/link-view-container.component.ts`, Hüllen | I2 | leer → `PlEdLinkPreview` |
| **F2** Forgejo | wie F1 (Vorschau für Forgejo-URLs: PR/Issue/Commit); keine weitere Editor-Stelle | P (über F1) | dto. | I2 | dto. |
| **G1** AI-Basis (nicht gewählt) | Flag `ai` in `EDITOR_FLAGS` (CE deaktiviert), `plugins/ai-handle.ts` (Kern, inaktiv), Input `aiHandler` am Document-/Collaborative-Editor (angenommen, nicht gerendert – wie Original) | V | `ED/core`, `ED/extensibility` | I2 | `disabled: ["ai", …]` |
| **H1** OAuth-App-Plattform | `EDITOR_MENTION_TYPES` (App-/Bot-Mentions als weitere `EditorMentionTypeDefinition` mit eigener Render-Komponente); `PlWebEditorUserMention` bleibt 1:1 (das Original wertet `is_bot` in der Mention nicht aus) | P | `ED/extensibility`, `FE/libs/web/core/editor/embeds/mentions` | I2 | nur `user_mention` |
| **H6** Realtime-Event-Server | keine (Pages nutzen den Hocuspocus-Kanal, nicht SignalR) | – | – | – | – |

### 6.2 Block-Registry für zusätzliche Editor-Blöcke (Paket D9, W8)

**Zweck:** D9 („Erweiterte Editor-Blöcke“: Draw.io, Embeds, Attachments, Video, Columns, Tabs, Toggle, Status, Date, LaTeX, Mermaid, HTML-Artifact, TOC, Link pages, Page-Embed, Widget, Block-Links; EE-P07-019…039) – und ebenso D6 (Work-Item-Embed), D7 (Kommentar-Mark), D10 (Databases), B2 (Widget-Embed) – ergänzen Blöcke, ohne eine CE-Datei des Editors zu ändern. Mechanik: `EditorBlockDefinition` (§5.10) + `provideEditorBlocks(...)` im `provide<Paket>Extensions()` des Pakets.

**Abdeckung der Original-Andockpunkte** (jede Zeile ist im Original ein leerer EE-Hook; die CE-Implementierung liest die Registry, CE-Ergebnis identisch zum Original):

| Original-Andockpunkt (`ED0/`) | Feld in `EditorBlockDefinition` | Lesende CE-Stelle (`ED/core/src/…`) | Stub (F20 §6) |
|---|---|---|---|
| `extensions/core/extensions.ts` `CoreEditorAdditionalExtensions` | `extensions.core` | dto. | – |
| `extensions/core/without-props.ts` (`CoreEditorAdditionalExtensionsWithoutProps`, bleibt `[]`) | `extensions.serverSchema` | `getCoreEditorExtensionsWithoutProps()` in `extensions/core-without-props.ts`, gelesen von `helpers/yjs-utils.ts` (R-ED-12) | – |
| `extensions/rich-text-extensions.tsx` Registry | `extensions.richText` | dto. | – |
| `extensions/document-extensions.tsx` Registry | `extensions.document` | dto. | S50 |
| `extensions/additional-slash-command-options.tsx` | `slashCommands` | dto. | S49 |
| `constants/extensions.ts` `ADDITIONAL_BLOCK_NODE_TYPES` | `blockNodeTypes` | `getAdditionalBlockNodeTypes()` → `extensions/unique-id/extension.ts` | – |
| `constants/assets.ts` `ADDITIONAL_ASSETS_META_DATA_RECORD` | `assetMetaData` | `helpers/assets.ts` | – |
| `helpers/parser.ts` `extractAdditionalAssetsFromHTMLContent`, `replaceAdditionalAssetsInHTMLContent` | `extractAssets`, `replaceAssets` | dto. | – |
| `plugins/drag-handle.ts` `generalSelectors` (enthält bereits `.issue-embed`, `.editor-embed-component`, `.editor-drawio-component`) | `sideMenuSelectors` | dto. | – |
| `plugins/drop.ts` Attachment-Zweig (`fileType === "attachment"`, E23) | `fileDropHandlers` | dto. | – |
| `components/menus/menu-items.ts` (`TExtendedEditorCommands`) | `menuItems` | `getEditorMenuItems()` | S48 |
| `components/menus/block-menu-options.tsx` | `blockMenuOptions` | `getBlockMenuOptions()` | – |
| `types/editor-extended.ts` (`IEditorPropsExtended`, `TExtendedEditorCommands`, `TExtendedCommandExtraProps`, `TExtendedEditorRefApi`) | – (Typen bleiben 1:1, V; Pakete erweitern additiv) | – | S48 |
| `PKG/utils/src/editor/markdown-parser/custom-components-handler.ts` | `markdownHandlers` | `convertHTMLToMarkdown` | – |
| React-NodeViews der Pakete | `ui` (Schlüssel `<paket>:<name>` → Komponente) | `EDITOR_UI_COMPONENTS` (§5.4) | – |
| `WEB/hooks/editor/use-extended-editor-config.ts` (`getExtendedEditorFileHandlers`) | `EDITOR_EXTENSIONS.fileHandlers` | `EditorConfigService` | S15 |
| `WEB/hooks/pages/use-extended-editor-extensions.ts` | `EDITOR_EXTENSIONS.extendedEditorProps` | Page-Hülle | S16 |
| `components/document-editor-side-effects.ts` | `EDITOR_EXTENSIONS.sideEffects` | `PlEdDocumentEditorSideEffects` | S60 |
| `SPC/components/editor/*` (`extendedEditorProps={{}}`) | `EDITOR_EXTENSIONS` mit `scope: "space"` | Space-Hüllen | S44 |

**Außerhalb des Frontends** (nur Verweis, Eigentümer in Klammern): Server-Schema `IDocumentNodeSpec`/`IDocumentMarkSpec` je Block (E-11, D07), PDF-Renderer je Block (D07), Sanitizer-Allowlist je neuem Tag/Attribut (D05 §3.17.3), Draw.io-Container hinter `/drawio/` und Link-Preview über `SsrfSafeHttpHandler` (D14 §6.3, D16 D9-Zeile), CSP `frame-src` für Embeds/HTML-Artifact (D05).

**Regeln für Paket-Blöcke:**

1. Schlüssel, Node-Namen, CSS-Klassen und Flags tragen ein Paketpräfix bzw. paketspezifische Namen; Kollision mit CE-Namen (§4.1) bricht `provideEditorUi()` bzw. `registerEditorBlocks()` beim Start.
2. Registrierung nur über `provideEditorBlocks()` in der Bootstrap-Phase (vor dem ersten Editor; Registry versiegelt sich danach).
3. Jeder Block durchläuft das Schema-Änderungsverfahren §3.2.5 (Schritte 2–6); das CE-Schema (Golden ohne Pakete) bleibt unverändert und wird in der Build-Konfiguration `fake-extensions` (D15) gegen die Paket-Liste getrennt geprüft.
4. Paket-Texte laufen über i18n-Namespaces des Pakets (D09 G-09); die CE-Editor-Texte bleiben englisch (D10-ADR-19).
5. **Ablage:** Paket-Blöcke liegen unter `FE/libs/shared/editor/packages/<paket>/core/src/` (framework-freie Tiptap-Extensions, `serverSchema`, Slash-Einträge, Markdown-Handler; Sheriff-Tag `editor:package-core`) und `FE/libs/shared/editor/packages/<paket>/ui/src/` (Angular-NodeViews/Widgets, `provide<Paket>EditorBlocks()`; Tag `editor:package-ui`), Aliase `@plane/editor/packages/<paket>` bzw. `…/<paket>/core`. Sie sind `scope:shared`, damit Web **und** Space (z. B. veröffentlichte Pages, D5) dieselben Blöcke rendern. Keine CE-Lib importiert sie; eingebunden werden sie ausschließlich über `provide<Paket>Extensions()` in `app.config.ts` (Web/Space). In der CE existiert der Ordner `packages/` nicht.

**CE-Pflicht-Tests der Registry (Typ X, D15 §3.15.3)** mit einem Fake-Block `fake:note` (`ED/core/src/testing/fake-block.ts`: Node `fakeNote`, Klasse `.fake-note`, Slash-Eintrag `pushAfter: "callout"`, UI-Schlüssel `fake:note`):

| Test | Erwartung |
|---|---|
| `block-registry.ce-default.spec.ts` | ohne Registrierung: G-SCHEMA aller Varianten unverändert, `getAdditionalBlockNodeTypes()` = `[]`, Slash-Liste = Original |
| `block-registry.fake-block.spec.ts` | mit `fake:note`: Node im Schema der Varianten mit `extensions.core`; Slash-Eintrag direkt nach „Callout“ in Sektion `general`; `UniqueID` vergibt `data-id` an `fakeNote`; Drag-Handle erscheint über `.fake-note` (Vitest-Browser); Flag `fake:note` in `disabledExtensions` entfernt Node und Slash-Eintrag |
| `block-registry.guards.spec.ts` | doppelter Schlüssel → Fehler; Registrierung nach erstem Editor → Fehler; UI-Schlüssel-Kollision mit CE-Schlüssel → Fehler |

Die Tests werden in `tests/extension-points.yaml` (D16 §7, EP-T09) mit ID `EP-ED-01…03` eingetragen.

### 6.3 Weitere (nicht strukturrelevante) Pakete mit Editor-Bezug – Andockweg

| Paket | Andockweg (ohne CE-Änderung) |
|---|---|
| D3 Page-Versionen erweitert | Document-Editor read-only + `getDocument()`; Vergleichsansicht als Paket-Komponente |
| D4 Realtime-Presence | Flag `collaboration-cursor` (D10-ADR-11) + Awareness des Providers; Avatare in der Page-Hülle |
| D5 Page-Publish & Exporte | `getDocument()`, `getMarkDown()`, Space-Scope `EDITOR_EXTENSIONS` (S44) |
| D6 Work-Item-Verknüpfung | `EDITOR_BLOCKS` (Work-Item-Embed `issue-embed-component` – Schema existiert bereits in `server-document`; Runtime-NodeView über `ui`), `EDITOR_MENTION_TYPES` (Work Items, Projekte, Cycles, Module, Pages) |
| D7 Kommentare in Pages | `EDITOR_BLOCKS` (Mark `comment` über `extensions.document` + `serverSchema`), `PAGE_PANE_EXTENSIONS` (D08) |
| D8 Sharing/Labels/Benachrichtigungen | keine Editor-Stelle |
| D10 Databases | `EDITOR_BLOCKS` + Dokumenttyp (E-10, D07) |
| B2 Dashboards | `EDITOR_BLOCKS` (Widget-Embed) |

---

## 7. Akzeptanzkriterien & Tests

### 7.1 Akzeptanzkriterien

| ID | Kriterium (messbar) | Nachweis (Werkzeug, Ort) | Inkr. |
|---|---|---|---|
| AK-D10-01 | **G-SCHEMA:** `schema`, `extensions`, `plugins` aller Varianten sind identisch zu den Goldens des Originals (I2: Browser `rich`, `lite`, `document` + TS-Server-Schema `server`/`server-document` gegen D07-Goldens `rich`/`document`; I4: Browser `collaborative`, `title`) | `ED/core/src/testing/schema-golden.spec.ts` (Vitest `shared-dom`), `tests/Plane.Documents.Tests` (Server, D07) | I2 / I4 |
| AK-D10-02 | **G-EDPIN:** alle Pakete aus §3.2.1 sind im `frontend/pnpm-lock.yaml` genau einmal in der Version aus `ED/VERSIONS.json` aufgelöst; `react`, `react-dom`, `@tiptap/react`, `@floating-ui/react`, `lucide-react`, `jsx-dom-cjs` kommen im Abhängigkeitsgraphen von `apps/{web,space}` nicht vor | `FE/tools/editor-port/check-versions.mjs` (PR-Gate) | I0 |
| AK-D10-03 | **G-EDCORE:** jede K1-Datei aus Anhang A ist nach Normalisierung (Header, Importpfade) byte-gleich zur Original-Datei; `PORT-DIFF`-Marker kommen nur in den 38 K2/NV-Dateien (Anhang A) vor, jeder Marker trägt einen Grund aus der Liste `ui-port`, `icons`, `react-types`, `dom-builder`, `block-registry`, `bugfix:<FE-ED-nn>` | `check-core-drift.mjs` (PR-Gate) | I2 |
| AK-D10-04 | Kern framework-frei: 0 Sheriff-/ESLint-Verstöße der Regeln §3.1; `ED/core` lässt sich in Vitest ohne Angular-TestBed laden | Lint-Gate, `core.smoke.spec.ts` | I2 |
| AK-D10-05 | **NodeView-/Menü-DOM-Parität:** für die 8 S5-Bausteine (Bild inkl. Uploader/Upload-Status/Toolbar, Callout inkl. Logo-/Farbwahl, Mention, Tabelle inkl. Spalten-/Zeilen-Handle und Dropdown, Code-Block, Slash-Menü, Emoji- und Mention-Dropdown, Drag-Handle + Block-Menü, Bubble-Menü inkl. aller vier Dropdowns) ist das normalisierte DOM (D09 N1–N9 + D15 Z1) identisch zum DOM-Golden des Originals (`capture-nodeview-dom.ts`) | Playwright Dual-Target `FE/apps/e2e/web/editor/editor-dom-parity.spec.ts`, Goldens `FE/libs/shared/editor/components/src/__golden__/dom/*.html` | I2 (S5 vorab) |
| AK-D10-06 | **Visual** ≤ 0,5 % Pixelabweichung, Themes light/dark, nur Chromium. **I2:** Katalog W-031 (Work-Item-Detail) Zustände `description-edit`, `comment-edit` sowie die von D10 verlangten Zusatzzustände `description-slash-menu`, `description-bubble-menu`, `description-block-menu`, `description-table-column-dropdown`, `description-image-toolbar`, `description-callout-picker`, `description-code-hover`, `description-mention-suggestion`, `description-emoji-suggestion` (Korpus-Beschreibung „alle Nodes“ im Seed). **I4:** W-046 (Page `{page:all-nodes}`) mit den dort definierten Zuständen plus `table-column-dropdown`, `image-toolbar`, `callout-picker`, `code-hover` (Rückmeldung an D09) | `screens-visual` (D09/D15), nur Chromium (Z-10) | I2 (W-031), I4 (W-046) |
| AK-D10-07 | Slash-Commands: Schlüssel, Titel, Beschreibungen, Suchbegriffe, Reihenfolge und Sektionen je Variante identisch; 12 Filterabfragen (`h`, `head`, `list`, `todo`, `tab`, `img`, `call`, `div`, `emo`, `gray`, `bg`, `xyz`) liefern dieselben Treffer wie das Original; FE-ED-02 (E1) geprüft | `command-items-list.spec.ts` (Golden aus dem Original), `editor-menus.spec.ts` | I2 |
| AK-D10-08 | **Eingabe-Parität:** für jede Zeile aus A12 §2.8 (Tastenkürzel) und §2.9 (Input-/Paste-Regeln) ergibt dasselbe Playwright-Tastaturskript im Original und in `funk.` dasselbe PM-JSON (gelesen über `document.querySelector('.ProseMirror').editor.getJSON()` – Tiptap 2 hängt die Editor-Instanz an `view.dom`, in Original und Ziel gleich; kein Test-Hook nötig) | `editor-blocks.spec.ts`, `editor-inline.spec.ts` (Dual-Target, D15) | I2 |
| AK-D10-09 | Paste/Clipboard: Markdown-Paste, Editor-HTML-Paste (`text/plane-editor-html`) mit Asset-Duplizierung (`status="duplicating"`, neue `id`), VS-Code-Paste, URL-über-Selektion, Copy (`text/plain` = Markdown) identisch zum Original | `editor-inline.spec.ts` | I2 |
| AK-D10-10 | Bilder: Upload-Fortschritt sichtbar und animiert, Erstgröße/Resize/Ausrichtung schreiben dieselben Attribute wie das Original, Vollbild-Zoomstufen `[0.5, 1, 1.5, 2]`, Restore bei Ladefehler genau einmal, Duplikations-Retry automatisch einmal; Validierungstexte identisch; Request-Folge zu `/api/assets/v2/…` identisch (Contract-Recording) | `editor-blocks.spec.ts`, Contract-Szenario `assets.editor.*` (D15) | I2 |
| AK-D10-11 | **LT-16:** Dokument mit 5 000 Blöcken, Tippen von 200 Zeichen: Eingabe-Latenz p95 < 50 ms; kein Angular-Rendering außerhalb des Editors während des Tippens (Render-Zähler der Peek-Komponenten = 0) | Perf-Trace (D15 §3.12, LT-16) | I2 / I4 |
| AK-D10-12 | Lite-Editor: Enter sendet nur ohne offene Dropbar; Shift-Enter-Kette wie Original; Enter in offenem Mention-/Emoji-Dropdown wählt aus | `editor-variants.spec.ts` | I2 |
| AK-D10-13 | Document read-only: Beschreibungs-Version rendert dasselbe HTML wie das Original; bei `editable=false` wird nie `uniqueIdOnlyChange` erzeugt und kein Asset gelöscht | `editor-variants.spec.ts`, Unit `editor-instance.spec.ts` | I2 |
| AK-D10-14 | Kollaboration: 2 Chromium-Clients, 200 zufällige Operationen → identisches PM-JSON; Reload offline zeigt Inhalt aus IndexedDB; Stage-Folgen für die Szenarien Auth-Fehler, 3 Fehlversuche (`max-retries`), Close-Code 4001 (`forced-close`), Tab-Sichtbarkeit (Reconnect nach 1 s Throttle) identisch zum Original; zusätzlich (Server D07-ADR-05, kein Original-Vergleich): Close 4205 → Reconnect und `authorizedScope = "readonly"` → Hülle setzt `editable=false`; Close 4403 → Stage `disconnected` mit `auth-failed` | `web/realtime/collaboration.spec.ts`, `collaboration-session.spec.ts` (Fake-Provider) | I4 |
| AK-D10-15 | Titel-Editor: Navigation (ArrowDown/Right/Enter, ArrowUp/Left/Backspace) wie A12 §2.8; Titel im Y-Fragment `title`; Platzhalter „Untitled“ auch read-only | `page-editor-shell.spec.ts` | I4 |
| AK-D10-16 | Stateless: `lock`, `unlock`, `archive`, `unarchive`, `make-public`, `make-private` erzeugen dieselben WS-Frames wie das Original (Frame-Recording); JSON-Events erreichen `RealtimePageEventsService` | `collaboration.spec.ts`, `realtime-page-events.service.spec.ts` | I4 |
| AK-D10-17 | REST-Fallback-Schnittstelle: `setProviderDocument(update)` merged per CRDT; `getDocument()` liefert `{ binary, html, json }` im Original-Format (PATCH-Body im Contract-Vergleich gleich) | `page-fallback.service.spec.ts`, Contract `pages.description.patch` | I4 |
| AK-D10-18 | Yjs-Browser-Roundtrip: alle G-DOC-Dokumente, vom .NET-Server als `description_binary` geliefert, ergeben im Angular-Editor dasselbe PM-JSON wie im Original-Editor (AK-15-14) | `editor-variants.spec.ts` (Abschnitt Roundtrip) | I4 |
| AK-D10-19 | Sticky-Editor: Toolbar (Bold, Italic, To-do-Liste, Farbpalette, Löschen) und Autosave 500 ms wie Original | Stickies-Spec (D15) | I5 |
| AK-D10-20 | Space: Rich read-only und Lite-Kommentare mit Bild-Upload über Anchor-URLs identisch; Mentions „@deactivated user“ | Space-Specs (D15) | I6 |
| AK-D10-21 | Speicher: 30-mal Peek mit Editor öffnen/schließen → Anzahl lebender `Editor`-Instanzen und NodeView-`ComponentRef`s nach GC = 0 (Heap-Snapshot-Zähler) | Perf-Spec `editor-memory.spec.ts` | I2 |
| AK-D10-22 | CSP: Während aller Editor-E2E-Specs gehen 0 CSP-Reports ein (Report-Only ab I0); im Enforce-Modus (I7) sind alle Editor-Specs grün | Gateway-Report-Endpunkt `POST /csp-report` (ABG-016) | I2 / I7 |
| AK-D10-23 | Airgap: Editor-E2E inkl. Emoji-Suggestion (auch nicht unterstützte Emojis), Callout-Picker, Code-Highlighting erzeugt 0 Requests außerhalb der Base-URL; der Dist-Scan meldet außerhalb der Allowlist-Einträge `ED-AIRGAP-01…03` (§3.12, mit `maxHits`) keine Editor-URL; kein gerendertes `img[src^="https://cdn.jsdelivr.net"]` im Editor-DOM | Netzwerkwächter (D15 §3.9.1), `airgap-scan.mjs` | I2 / I7 |
| AK-D10-24 | Erweiterungspunkte: `EP-ED-01…03` grün; CE-Defaults erzeugen kein zusätzliches DOM (Vergleich mit/ohne `provideEditorDefaults()` DOM-gleich) | Vitest, `tests/extension-points.yaml` | I2 |
| AK-D10-25 | Abweichungen: jede `FE-ED-nn` steht in `ui-deviations.yaml` mit Test-Referenz; DOM-/Visual-Diffs außerhalb dieser Liste = 0 | `ui-deviations`-Prüfer (D09) | I2 ff. |
| AK-D10-26 | Barrierefreiheit: axe-Lauf auf Editor-Seiten ohne neue Verstöße gegenüber der Original-Baseline | a11y-Specs (D15) | I2 / I4 |

### 7.2 Testinventar

| Ebene (D15) | Werkzeug | Ort | Inhalt | Inkr. |
|---|---|---|---|---|
| L1 Unit Kern | Vitest, jsdom (`shared-dom`) | `ED/core/src/**/*.spec.ts` | Schema-Golden, `ui-port.no-port.spec.ts` (§3.4.3), Slash-Liste/-Filter, `headings-list` (E12), `editor-ref`-Helfer, `markdown-clipboard`, `isDangerousHref`/`isValidHttpUrl`, List-Keymap, Typografie-Regeln, `unique-id`, `yjs-utils`, Block-Registry | I2 |
| L2 Komponenten | Vitest, jsdom (`shared-dom`), `@testing-library/angular` | `ED/components/src/**/*.spec.ts`, `ED/angular-binding/src/**/*.spec.ts` | `angular-node-view.spec.ts` (Konstruktor-Reihenfolge: nach `new AngularNodeView(...)` sind `contentDOM`, Inputs und `selectionUpdate`-Listener gesetzt; Bereichs-Selektion setzt `ProseMirror-selectednode`), NodeView-Inputs/-Updates, `key`-Neuaufbau, `editorState` (Default `deepEqual`: identisches Objekt → kein neuer Wert), `EditorContentDirective` (`createNodeViews()` nach dem Einhängen, Rückbau beim Zerstören), Bubble-`shouldShow`, Floating-Dismiss, `EditorInstance` (Neuaufbau nur bei `editable`, `value`-Sync, Upload-Sperre) | I2 |
| L2 Browser | Vitest-Browser-Modus (Chromium) | `ED/components/src/**/*.browser.spec.ts` | Floating-Positionen, Drag-Handle-Position, Tabellen-Resize/Drag, Bild-Resize, Vollbild-Pan/-Zoom, Bubble-Menü (tippy) | I2 |
| L2 Kollaboration | Vitest + Fake-Provider | `ED/collaboration/src/**/*.spec.ts` | Stage-Maschine, Retries, Forced-Close, Visibility/Online | I4 |
| L4 Golden | Vitest / Playwright | `tests/Plane.Documents.Tests/Golden/schema/*`, `FE/libs/shared/editor/components/src/__golden__/dom/*.html` | G-SCHEMA (Browser-Hälfte), NodeView-DOM-Goldens | I2 / I4 |
| L7 E2E Dual-Target | Playwright (Chromium) | `FE/apps/e2e/web/editor/editor-{variants,menus,blocks,inline,config,dom-parity,memory}.spec.ts`, `FE/apps/e2e/web/realtime/collaboration.spec.ts`, `FE/apps/e2e/web/pages/page-editor-shell.spec.ts` | Varianten, Menüs, Blöcke, Inline, Konfiguration, DOM-Parität, Speicher, Kollaboration | I2 / I4 |
| L8 Visual | Playwright-Screenshots | Katalog W-046 (D09) | §7.1 AK-D10-06 | I2 / I4 |
| L9 Last | Perf-Trace, Browser-Zeugen | LT-16 (D15) | Eingabe-Latenz | I2 / I4 |
| Gates | Node-Skripte | `FE/tools/editor-port/check-{versions,core-drift}.mjs` | G-EDPIN, G-EDCORE | I0 / I2 |

Testnamen folgen D15 §3.2 (`describe('CE-PAGE-024 …')`, Tags `@CE-PAGE-024 @I2 @web`). Die Specs `editor-dom-parity.spec.ts` und `editor-memory.spec.ts` sind technische Querschnitts-Specs (`@tech`, `@also:CE-PAGE-021…`).

### 7.3 Spike S5 – präzisierte Erfolgskriterien (Ergänzung zu D01 §9)

| Kriterium | Messung |
|---|---|
| Schema identisch für Rich, Lite, Document, Title (+ Collaborative) | AK-D10-01 im Spike-Branch |
| 8 Bausteine funktional inkl. Bild-Upload-Fortschritt | Playwright-Demo-Seite `FE/apps/gallery` (Editor-Stories) gegen Fake-Upload |
| DOM-Vertrag §3.5.1 bestätigt (`contentDOM` mit `data-node-view-content-react` + `data-node-view-wrapper` – aus dem Quelltext bereits belegt –, `FloatingOverlay`-Attribute, Kaskade `tiptap-core.css` als letzter Import) | `capture-nodeview-dom.ts` gegen das laufende Original, Diff = 0 |
| Visual Editor-Seite ≤ 0,5 % | AK-D10-06 (eine Seite) |
| 5 000 Blöcke ohne Eingabe-Lag | AK-D10-11 |
| NodeViews stabil mit Yjs (2 Clients, gleichzeitige Bild-/Callout-Änderung) | 30-min-Soak gegen den Original-Live-Server (Node), danach gegen `Plane.Realtime` aus S1 |
| Abbruch/Fallback | wie D01 §9: (1) NodeViews als DOM-NodeViews (UI-Port-Implementierung `DomUiPort`, Kern unverändert), (2) ngx-tiptap 13 direkt (nur, wenn DOM-Abweichungen per Deviation abgenommen werden) |

---

## 8. Risiken & offene Punkte

### 8.1 Risiken

| ID | Risiko | Wahrscheinlichkeit / Wirkung | Gegenmaßnahme |
|---|---|---|---|
| R-D10-01 | Angular-`createComponent` mit `hostElement` verhält sich beim Zerstören/Neuaufbau anders als React (Host-Element bleibt/verschwindet, Listener) → DOM-Lecks, Selektionssprünge | mittel / hoch | S5-Test „Neuaufbau bei ID-Wechsel“ und AK-D10-21; Wrapper-Element wird bei Neuaufbau ersetzt (§5.3) |
| R-D10-02 | Zoneless: Callbacks aus ProseMirror/tippy/Floating-UI schreiben in Nicht-Signale → fehlendes Rendering | mittel / mittel | D10-ADR-10, Lint `prefer-signals`, Browser-Tests |
| R-D10-03 | Tiptap 2 ist abgeschlossen (`v2-latest` 2.27.3), Sicherheitskorrekturen kommen nur noch in 3.x | mittel / mittel | Pins + `pnpm patch` für einzelne Fixes mit G-SCHEMA-Nachweis; Advisory-Überwachung (Trivy/npm audit, D14); eine Migration auf Tiptap 3 ist ein eigenes Vorhaben mit Schema-Migration (nicht Teil der CE) |
| R-D10-04 | Abweichende Yjs-Struktur zwischen YDotNet-Konverter und `y-prosemirror` → Merge-Konflikte | mittel / hoch | Eigentümer D07; Editor-Seite liefert AK-D10-18 |
| R-D10-05 | CSP-Enforce ohne `style-src-attr 'unsafe-inline'` bricht Ausrichtung/Farben | hoch (falls nicht umgesetzt) / hoch | §3.20.4, Rückmeldung an D05, AK-D10-22 |
| R-D10-06 | Emoji-Darstellung hängt von System-Fonts ab → Visual-Rauschen | mittel / niedrig | gepinnte Test-Fonts (D09), Masken nur für Emoji-Glyphen |
| R-D10-07 | `pnpm overrides` erfassen nicht alle transitiven Tiptap-Pakete → Schema-Drift | niedrig / hoch | G-EDPIN bricht den Build |
| R-D10-08 | Globale DOM-IDs bei mehreren Editoren (Peek + Kommentar) erzeugen Konflikte | bekannt aus Original / niedrig | 1:1 belassen; E2E mit zwei Editoren auf einer Seite |
| R-D10-09 | Viele Angular-NodeViews (z. B. 2 000 Mentions) verlangsamen das Laden | mittel / mittel | Messung in LT-16-Variante „Mention-dicht“; Fallback: Mention als DOM-NodeView über `DomUiPort` nur für `mention` |
| R-D10-10 | `tippy.js` 6 wird nicht mehr gepflegt | niedrig / niedrig | nur im Bubble-Menü, gepinnt; Ersatz erst mit Tiptap 3 |
| R-D10-11 | Codemod erzeugt subtile Unterschiede (Alias-Auflösung, Barrel-Zyklen) | mittel / mittel | G-EDCORE + Schema-/Eingabe-Parität |

### 8.2 Offene Punkte

| ID | Punkt | Empfehlung | Entscheidet | Bis |
|---|---|---|---|---|
| O-D10-01 | Aktivierung `collaboration-cursor` in der CE (O-D08-07, FE-ED-01) | aktivieren, sobald S1-Awareness grün; sichtbare Abweichung abnehmen lassen | Auftraggeber | Ende I4 |
| O-D10-02 | FE-ED-04: korrigierte Tooltip-Kürzel Bulleted/Numbered (sichtbarer Text ändert sich) | korrigieren (falsche Information = funktionaler Fehler, Z-12) | Auftraggeber | vor I2-Abnahme |
| O-D10-03 | E10 (doppelte Tastatur-Navigation im Slash-Menü) | nach S5-Messung entscheiden (FE-ED-05 bedingt) | Editor-Agent mit Review | S5 |
| O-D10-04 | ~~Server-HTML mit/ohne `data-id` (E20)~~ | **entschieden** durch D07-ADR-12: ohne `data-id` (wie Original) | D07 | – |
| O-D10-05 | DOM-Details ⚠ (`FloatingOverlay`-Attribute; `contentDOM`-Attribute und `tiptap-core.css`-Position sind im Review aus dem Quelltext von `@tiptap/react` 2.26.1 bzw. `@tiptap/core` 2.27.3 belegt, S5 bestätigt nur noch) | in S5 per DOM-Golden festschreiben (der frühere Teil „Feld/Ereignis für `authorizedScope`“ entfällt: `provider.authorizedScope`, 17 ABG-113) | Spike S5 | Ende I0 |
| O-D10-06 | `style-src-attr 'unsafe-inline'` in der Gateway-CSP | übernehmen (§3.20.4) | D05 | vor I2 |

---

## 9. Abhängigkeiten zu anderen Dokumenten (02–16)

| Dokument | Beziehung | Was D10 von dort nutzt | Was D10 dorthin liefert / verlangt |
|---|---|---|---|
| `00-grundsatzentscheidungen.md` | bindend | ADR-001 (Flags statt Gates, `flaggedExtensions` leer), ADR-002 (Browser-Provider unverändert), ADR-004 (Airgap), ADR-005 (UI 1:1), ADR-009 (`funk.`), ADR-009B (Marke „funk.“; im Editor keine sichtbaren Plane-Texte, D10-ADR-19) | – |
| `01-zielarchitektur-und-tech-stack.md` | bindend | ADR-022, ADR-029, ADR-031, ADR-041, ADR-042, S5, §6.1–§6.4, §8.2 | **Präzisierungen (keine ADR-Änderung):** ADR-042 Pins = Lockfile-Stand (`@tiptap/core` 2.27.3, Rest 2.26.1/2.26.2, `@tiptap/html` 2.26.2) statt „2.22.3 (Rest)“; Inkrement „I2 (Lite)“ → „I2 (Lite, Rich, Document read-only), I4 (Collaborative, Titel)“; S5 „Ergebnis vor Start I2“ vollständig (D10-ADR-15); §6.1 Baum `editor/` um `extensibility/`, `VERSIONS.json` ergänzen; Kommentar zu `libs/web/pages` „components/editor (Web-spezifische Editor-Hüllen)“ → Hüllen in `libs/web/core/editor` (D10-ADR-17); §8.2 Zeilen `emojibase-data` = 15.3.2 (ABG-029), `jsx-dom-cjs` streichen, `@tiptap/extension-bubble-menu` 2.26.3 und `@tiptap/extension-collaboration-cursor` 2.26.1 ergänzen – **umgesetzt** (17 ABG-114, ABG-120; §6.1-Baum und Hüllen-Ort nachgezogen in der Prüfung Teil 2, 17 §2.7 N2-11/N2-12) |
| `02-backend-solution-und-konventionen.md` | indirekt | Ort `BE/documents/Plane.Documents` | – |
| `03-datenmodell-efcore.md` | nutzt | D03-ADR-17 (vier Beschreibungsformate `description_html`/`_json`/`_binary`/`_stripped`) | `description_json` folgt dem eingefrorenen Schema (§3.2); D03 §9 Zeile „`10-editor-angular.md` (noch nicht vorhanden)“ → vorhanden |
| `04-api-design-und-endpunktkatalog.md` | nutzt | Asset-Endpunkte `/api/assets/v2/…`, `searchEntity`, Page-Description-Endpunkte | Editor-relevante Abweichungen: keine |
| `05-auth-sicherheit-berechtigungen.md` | nutzt / verlangt | Sanitizer-Allowlist §3.17.3, CSP D05-ADR-23 | **CSP:** `style-src-attr 'unsafe-inline'` (§3.20.4); Tag-/Attribut-Inventar §4.1 als Golden-Korpus-Grundlage; Editor-Erweiterungen erweitern Allowlist + Korpus (§3.2.5) |
| `06-hintergrundjobs-events-benachrichtigungen.md` | – | – | keine Editor-Schnittstelle |
| `07-realtime-kollaboration-dokumente.md` | nutzt / liefert an | Server-Schema und Spec-Klassen (D07 §3.12–§3.13), Server-Goldens `rich`/`document`/`title.schema.json` und Generator (D07 §7.5), Scope je Verbindung (D07-ADR-05), kein `data-id` im Server-HTML (D07-ADR-12), Awareness-Weiterleitung (D07-ADR-25), Stateless-/Server-Ereignisse (D07 §3.7), Close-Codes (D07 §3.8) | Browser-Varianten der G-SCHEMA-Goldens unter `schema/browser/` und gemeinsamer Serialisierer (§3.2.3, §5.9); Client-Erwartung `authorizedScope` → `editable=false` (§3.15.1); D07 §9 Zeile „`10-editor-angular.md` (noch nicht erstellt)“ → vorhanden; ~~Klärung `server.schema.json`~~ – **erledigt (17 ABG-119):** Server-Goldens `{rich,document,title}.schema.json`, `rich` = `CoreEditorExtensionsWithoutProps`, kein `server.schema.json`; Quelle für `authorizedScope` = `provider.authorizedScope` (D07 §3.3.6, 17 ABG-113); Client-Verhalten bei Close 4205/4403 (§3.15.1) als Gegenstück zu D07-ADR-05 |
| `08-frontend-angular-architektur.md` | nutzt / verlangt | Libs, Sheriff, Tokens §6.1, Services §4.7, `EditorAssetStore`, §3.12 | **Präzisierungen:** Editor-Tokens werden in `ED/extensibility` deklariert und von `EXT` re-exportiert (D10-ADR-18); `EDITOR_MENTION_TYPES` ist eine Liste von `EditorMentionTypeDefinition` (CE-`entityName`s = `["user_mention"]`); Hüllen-Ort `FE/libs/web/core/editor` (D10-ADR-17); Lite **und** Rich in I2 (Inkrement-Matrix §1, Zeilen „Lite-Editor“ und „Pages, Rich/Document-Editor“: Rich- und Document-Editor read-only gehören zu I2); §9 Zeile zu `10` („Rich/Document-Editor (I4)“) ebenso; Editor-Hüllen liefern `fileHandler` als `computed` über `EditorAssetStore.assetsUploadPercentage()` (§3.7 Nr. 4) |
| `09-ui-paritaet-designsystem.md` | nutzt | D09-ADR-01/-03/-07, §3.2.2 Import-Position, §3.8.2 Emoji-Daten, Propel `tooltip`, `collapsible`, `popover` (Mention-Hover-Karte der Hülle), `PlBlkEmojiPicker`, `PlBlkLoader`, Katalog W-046, Schwellwert 0,5 % | Editor-CSS 1:1 (§3.20), `tiptap-core.css` als `extra-css` (FE-ED-07), Editor-Overlays nutzen **nicht** die Propel-Portal-Schicht (Floating-UI-DOM-Vertrag, D10-ADR-07), Galerie-Stories der Editor-Menüs (`FE/tools/gallery-stories/editor/*.stories.json`); Editor-CSS-Kopie bereits in **I0** (G-CSS der Shell vergleicht das kompilierte Original-CSS, das die Editor-Styles enthält) – 09 §4.1 Zeile `packages/editor/src/styles/*` „I2“ → „I0“; Status in 09 §9 „offen (10 noch nicht vorhanden)“ → erledigt; **Review-Rückmeldungen:** (a) §3.2.2 Importliste Web/Space: `tiptap-core.css` als **letzter, ungeschichteter** Import (§3.20.2); (b) §3.1 `PRP/icons/index.ts` darf `svg-icon.component.ts` nicht re-exportieren (Daten-Einstiegspunkt für den framework-freien Editor-Kern, §3.1); (c) Lint-Regel `no-component-styles`/`ViewEncapsulation.None` auch für `libs/shared/editor/**` und `libs/space/editor/**`; (d) Katalog W-031 um die Editor-Zustände aus AK-D10-06 ergänzen (I2), W-046 um `table-column-dropdown`, `image-toolbar`, `callout-picker`, `code-hover` |
| `11-suche-und-ai-basis.md` | nutzt | Entity-Suche SR-03 (`GET /api/workspaces/{slug}/entity-search/`), `EditorMentionService` (`FE/libs/web/core/editor/editor-mention.service.ts`), Typ-Freischaltung je Inkrement (I2 `user_mention`, I4 `page`) | Mention-Dropdown-Vertrag §3.11 (Sektionen, Debounce 300 ms, `count: 5`); D11 §9 Zeile „`10-editor-angular.md` (noch nicht erstellt)“ → vorhanden |
| `14-infrastruktur-deployment-betrieb.md` | nutzt | Airgap-Bundle, Gateway-CSP-Auslieferung | Airgap-Allowlist-Eintrag (§3.12); „jsDelivr (Callout-Emoji-URL, frimousse-Emoji-Daten) gebündelt (D09/D10)“ → Callout-URL wird **nicht** gebündelt, sondern nie geladen (D10-ADR-12) |
| `15-teststrategie-qualitaet-paritaet.md` | nutzt / verlangt | Ebenen, Gates, Dual-Target, Golden-Mechanik, B.8-Spec-Namen, LT-16 | G-SCHEMA-Browser-Varianten `rich`, `lite`, `document`, `collaborative`, `title` unter `Golden/schema/browser/` mit Manifesten `*.extensions.json`/`*.plugins.json` (§3.2.3; Server-Varianten bleiben bei D07); D15 §3.7.1 „Varianten Rich, Lite, Document, Title sowie Server-Schema“ entsprechend präzisieren; Inkrement-Tags CE-PAGE-024…040 → I2 (D10-ADR-15); neue Gates G-EDPIN, G-EDCORE; Specs `editor-dom-parity.spec.ts`, `editor-memory.spec.ts`; Typ-X-Tests EP-ED-01…03; Generator-Unterbefehl `schema` (§3.2.4) |
| `16-erweiterungspunkte-bezahl-features.md` | liefert an | X13, E-10, E-11, S10, S14–S16, S44, S48–S50, S60 | `EDITOR_BLOCKS` = `EditorBlockDefinition` mit Abdeckungstabelle §6.2; `EDITOR_*`-Tokens und CE-Defaults §5.10; Editor-Zeilen der 🧱-Tabelle §6.1; Status „`10-editor-angular.md` (noch nicht vorhanden)“ → vorhanden; D9-Zeile „Editor-Lib · `FE/libs/shared/editor` (`extensions/<block>/`)“ präzisieren zu `FE/libs/shared/editor/packages/<paket>/{core,ui}` (§6.2 Regel 5) |
| `17-abgleich-dokumentuebergreifend.md` | bindend | ABG-016 (CSP), ABG-026 (kein CDK-Overlay), ABG-029 (Emoji-Version), Z-10 (nur Chromium), Z-11 (AGPL), Z-12 (Bugfix-Regel); Teil 2: ABG-113, ABG-114, ABG-119, ABG-121, ABG-148 (Abgleich-Protokoll), Z-105, Z-109 | keine neuen Konflikte; Präzisierungen oben sind als Rückmeldungen formuliert |

---

## Anhang A – Datei-für-Datei-Abbildung `ED0/` → `ED/` (225 Dateien)

Kategorien: **K1** Kopie 1:1 (nur Importpfade, R-ED-1…3, -13) · **K2** Kopie mit markierter Anpassung (`PORT-DIFF`: Icons, React-Typen, `dom-builder`, Block-Registry, UI-Props R-ED-15, Bugfix) · **NV** Kern-Datei 1:1, React-Renderer → UI-Port (`uiNodeView`/`uiRender`) · **NG** Neubau als Angular-Komponente/Direktive (DOM/Klassen 1:1) · **SV** Neubau als Service/Funktion (Logik 1:1) · **PA** Barrel/Public-API · **CSS** 1:1 · **EX** entfällt in der CE. Pfade relativ zu `ED0/` = `packages/editor/src/` bzw. `ED/` = `FE/libs/shared/editor/`. Maschinenlesbar: `_data/10-editor-file-map.json`. Summen: K1 101, K2 28, NV 10, NG 45, SV 8, PA 24, CSS 7, EX 2 (Review 23.10.2026: `core-without-props.ts` und `yjs-utils.ts` K1 → K2, `core/without-props.ts` K2 → K1, R-ED-12).

| Original (`ED0/`) | Kat. | Ziel | Symbol / Hinweis | Inkr. | CE-IDs |
|---|---|---|---|---|---|
| `components/document-editor-side-effects.ts` | NG | `ED/components/src/components/document-editor-side-effects.component.ts` | PlEdDocumentEditorSideEffects (rendert Beiträge aus EDITOR_EXTENSIONS.sideEffects, CE leer); EE-Stub S60, CE rendert nichts | I4 | CE-RT-004 |
| `components/editors/document/collaborative-editor.tsx` | NG | `ED/components/src/components/editors/document/collaborative-editor.component.ts` | PlEdCollaborativeDocumentEditor `pl-ed-collaborative-document-editor` | I4 | CE-PAGE-013, CE-RT-002 |
| `components/editors/document/editor.tsx` | NG | `ED/components/src/components/editors/document/editor.component.ts` | PlEdDocumentEditor `pl-ed-document-editor` | I2 | CE-PAGE-023, CE-WI-041 |
| `components/editors/document/index.ts` | PA | `ED/components/src/components/editors/document/index.ts` | Barrel | I2 | Querschnitt (CE-PAGE-021…023) |
| `components/editors/document/loader.tsx` | NG | `ED/components/src/components/editors/document/loader.component.ts` | PlEdDocumentContentLoader `pl-ed-document-content-loader` (nutzt PlBlkLoader) | I2 | CE-PAGE-023, CE-WI-041 |
| `components/editors/document/page-renderer.tsx` | NG | `ED/components/src/components/editors/document/page-renderer.component.ts` | PlEdPageRenderer `div[plEdPageRenderer]`; Titel-Editor-Teil erst I4 | I2 | CE-PAGE-023, CE-WI-041 |
| `components/editors/editor-container.tsx` | NG | `ED/components/src/components/editors/editor-container.component.ts` | PlEdEditorContainer `div[plEdEditorContainer]` | I2 | CE-PAGE-039 |
| `components/editors/editor-content.tsx` | NG | `ED/components/src/components/editors/editor-content.component.ts` | PlEdEditorContentWrapper `div[plEdEditorContentWrapper]` + Binding-Direktive `[plEdEditorContent]` | I2 | Querschnitt (CE-PAGE-021…023) |
| `components/editors/editor-wrapper.tsx` | NG | `ED/components/src/components/editors/editor-wrapper.component.ts` | PlEdEditorWrapper `pl-ed-editor-wrapper` (display:contents, data-pl-host) | I2 | Querschnitt (CE-PAGE-021…023) |
| `components/editors/index.ts` | PA | `ED/components/src/components/editors/index.ts` | Barrel | I2 | Querschnitt (CE-PAGE-021…023) |
| `components/editors/link-view-container.tsx` | NG | `ED/components/src/components/editors/link-view-container.component.ts` | PlEdLinkViewContainer | I2 | CE-PAGE-036 |
| `components/editors/lite-text/editor.tsx` | NG | `ED/components/src/components/editors/lite-text/editor.component.ts` | PlEdLiteTextEditor `pl-ed-lite-text-editor` | I2 | CE-PAGE-022, CE-WI-037 |
| `components/editors/lite-text/index.ts` | PA | `ED/components/src/components/editors/lite-text/index.ts` | Barrel | I2 | CE-PAGE-022, CE-WI-037 |
| `components/editors/rich-text/editor.tsx` | NG | `ED/components/src/components/editors/rich-text/editor.component.ts` | PlEdRichTextEditor `pl-ed-rich-text-editor` | I2 | CE-PAGE-021, CE-WI-005 |
| `components/editors/rich-text/index.ts` | PA | `ED/components/src/components/editors/rich-text/index.ts` | Barrel | I2 | CE-PAGE-021, CE-WI-005 |
| `components/link-container.tsx` | NG | `ED/components/src/components/link-container.component.ts` | PlEdLinkContainer | I2 | CE-PAGE-036 |
| `components/links/index.ts` | PA | `ED/components/src/components/links/index.ts` | Barrel + Typen LinkViews/LinkViewProps (1:1) | I2 | CE-PAGE-036 |
| `components/links/link-edit-view.tsx` | NG | `ED/components/src/components/links/link-edit-view.component.ts` | PlEdLinkEditView | I2 | CE-PAGE-036 |
| `components/links/link-preview.tsx` | NG | `ED/components/src/components/links/link-preview.component.ts` | PlEdLinkPreview | I2 | CE-PAGE-036 |
| `components/links/link-view.tsx` | NG | `ED/components/src/components/links/link-view.component.ts` | PlEdLinkView | I2 | CE-PAGE-036 |
| `components/menus/ai-menu.tsx` | EX | – | –; in CE nicht gerendert; G3 nicht gewählt. Andockpunkt bleibt Input `aiHandler` + Flag `ai` (§6) | – | Querschnitt (CE-PAGE-021…023) |
| `components/menus/block-menu-options.tsx` | K2 | `ED/core/src/components/menus/block-menu-options.ts` | getBlockMenuOptions() (Logik + PlIconDef), Rendering in PlEdBlockMenu; JSX-freie Optionsliste; Icons als PlIconDef | I2 | CE-PAGE-026 |
| `components/menus/block-menu.tsx` | NG | `ED/components/src/components/menus/block-menu.component.ts` | PlEdBlockMenu | I2 | CE-PAGE-026 |
| `components/menus/bubble-menu/alignment-selector.tsx` | NG | `ED/components/src/components/menus/bubble-menu/alignment-selector.component.ts` | PlEdBubbleMenuAlignmentSelector | I2 | CE-PAGE-025 |
| `components/menus/bubble-menu/color-selector.tsx` | NG | `ED/components/src/components/menus/bubble-menu/color-selector.component.ts` | PlEdBubbleMenuColorSelector | I2 | CE-PAGE-025 |
| `components/menus/bubble-menu/index.ts` | PA | `ED/components/src/components/menus/bubble-menu/index.ts` | Barrel | I2 | CE-PAGE-025 |
| `components/menus/bubble-menu/link-selector.tsx` | NG | `ED/components/src/components/menus/bubble-menu/link-selector.component.ts` | PlEdBubbleMenuLinkSelector | I2 | CE-PAGE-025 |
| `components/menus/bubble-menu/node-selector.tsx` | NG | `ED/components/src/components/menus/bubble-menu/node-selector.component.ts` | PlEdBubbleMenuNodeSelector | I2 | CE-PAGE-025 |
| `components/menus/bubble-menu/root.tsx` | NG | `ED/components/src/components/menus/bubble-menu/root.component.ts` | PlEdEditorBubbleMenu (nutzt Direktive `[plEdBubbleMenu]`) | I2 | CE-PAGE-025 |
| `components/menus/floating-menu/root.tsx` | NG | `ED/components/src/components/menus/floating-menu/root.component.ts` | PlEdFloatingMenuRoot (FloatingPortal + FloatingOverlay z 99 + Inhalt z 100) | I2 | Querschnitt (CE-PAGE-021…023) |
| `components/menus/floating-menu/use-floating-menu.ts` | SV | `ED/components/src/components/menus/floating-menu/floating-menu.ts` | createFloatingMenu() (computePosition/autoUpdate, click, dismiss, role) | I2 | Querschnitt (CE-PAGE-021…023) |
| `components/menus/index.ts` | PA | `ED/components/src/components/menus/index.ts` | Barrel | I2 | Querschnitt (CE-PAGE-021…023) |
| `components/menus/menu-items.ts` | K2 | `ED/core/src/components/menus/menu-items.ts` | getEditorMenuItems() 1:1, Icons → PlIconDef | I2 | CE-PAGE-014, CE-WI-037 |
| `constants/assets.ts` | K2 | `ED/core/src/constants/assets.ts` | ADDITIONAL_ASSETS_META_DATA_RECORD → liest EditorBlockRegistry (§6.3); D9-Andockpunkt | I2 | CE-PAGE-032 |
| `constants/common.ts` | K2 | `ED/core/src/constants/common.ts` | TOOLBAR_ITEMS, COLORS_LIST, EDITOR_FONT_STYLES … (Icons → PlIconDef); E9: Shortcut-Labels korrigiert (FE-ED-04) | I2 | CE-PAGE-014, CE-WI-037 |
| `constants/config.ts` | K1 | `ED/core/src/constants/config.ts` | – | I2 | CE-PAGE-040, CE-I18N-010 |
| `constants/document-collaborative-events.ts` | K1 | `ED/core/src/constants/document-collaborative-events.ts` | DocumentCollaborativeEvents | I4 | CE-RT-004 |
| `constants/extension.ts` | K1 | `ED/core/src/constants/extension.ts` | – | I2 | Querschnitt (CE-PAGE-021…023) |
| `constants/extensions.ts` | K2 | `ED/core/src/constants/extensions.ts` | ADDITIONAL_EXTENSIONS (leer), ADDITIONAL_BLOCK_NODE_TYPES → liest EditorBlockRegistry (§6.3); D9-Andockpunkt | I2 | Querschnitt (CE-PAGE-021…023) |
| `constants/meta.ts` | K1 | `ED/core/src/constants/meta.ts` | – | I2 | Querschnitt (CE-PAGE-021…023) |
| `constants/utility.ts` | K1 | `ED/core/src/constants/utility.ts` | – | I2 | Querschnitt (CE-PAGE-021…023) |
| `contexts/collaboration-context.tsx` | SV | `ED/collaboration/src/collaboration-context.ts` | Token COLLABORATION_SESSION + provideCollaborationSession() | I4 | CE-PAGE-013, CE-RT-002 |
| `contexts/index.ts` | PA | `ED/collaboration/src/index.ts` | Barrel | I4 | CE-PAGE-013, CE-RT-002 |
| `extensions/additional-slash-command-options.tsx` | K2 | `ED/core/src/extensions/additional-slash-command-options.ts` | coreEditorAdditionalSlashCommandOptions() → Beiträge aus EditorBlockRegistry; D9-Andockpunkt (S49) | I2 | CE-PAGE-024 |
| `extensions/callout/block.tsx` | NG | `ED/components/src/extensions/callout/block.component.ts` | PlEdCalloutBlock `[plEdCalloutBlock]` (NodeView) | I2 | CE-PAGE-033 |
| `extensions/callout/color-selector.tsx` | NG | `ED/components/src/extensions/callout/color-selector.component.ts` | PlEdCalloutColorSelector | I2 | CE-PAGE-033 |
| `extensions/callout/extension-config.ts` | K1 | `ED/core/src/extensions/callout/extension-config.ts` | CustomCalloutExtensionConfig | I2 | CE-PAGE-033 |
| `extensions/callout/extension.tsx` | NV | `ED/core/src/extensions/callout/extension.ts` | CustomCalloutExtension; addNodeView → uiNodeView('callout-block') | I2 | CE-PAGE-033 |
| `extensions/callout/index.ts` | PA | `ED/core/src/extensions/callout/index.ts` | Barrel | I2 | CE-PAGE-033 |
| `extensions/callout/logo-selector.tsx` | NG | `ED/components/src/extensions/callout/logo-selector.component.ts` | PlEdCalloutLogoSelector (nutzt PlBlkEmojiPicker, PlBlkLogo) | I2 | CE-PAGE-033 |
| `extensions/callout/types.ts` | K1 | `ED/core/src/extensions/callout/types.ts` | – | I2 | CE-PAGE-033 |
| `extensions/callout/utils.ts` | K1 | `ED/core/src/extensions/callout/utils.ts` | DEFAULT_CALLOUT_BLOCK_ATTRIBUTES (EMOJI_URL-String unverändert, D10-ADR-12) | I2 | CE-PAGE-033 |
| `extensions/code-inline/index.tsx` | K1 | `ED/core/src/extensions/code-inline/index.ts` | CustomCodeInlineExtension | I2 | CE-PAGE-029 |
| `extensions/code/code-block-lowlight.ts` | K1 | `ED/core/src/extensions/code/code-block-lowlight.ts` | CodeBlockLowlight | I2 | CE-PAGE-030 |
| `extensions/code/code-block-node-view.tsx` | NG | `ED/components/src/extensions/code/code-block-node-view.component.ts` | PlEdCodeBlockNodeView `[plEdCodeBlockNodeView]` | I2 | CE-PAGE-030 |
| `extensions/code/code-block.ts` | K1 | `ED/core/src/extensions/code/code-block.ts` | CodeBlock (+ Plugin codeBlockVSCodeHandlerCustom) | I2 | CE-PAGE-030 |
| `extensions/code/index.tsx` | NV | `ED/core/src/extensions/code/index.ts` | CustomCodeBlockExtension; addNodeView → uiNodeView('code-block') | I2 | CE-PAGE-030 |
| `extensions/code/lowlight-plugin.ts` | K1 | `ED/core/src/extensions/code/lowlight-plugin.ts` | LowlightPlugin | I2 | CE-PAGE-030 |
| `extensions/code/types.ts` | K1 | `ED/core/src/extensions/code/types.ts` | – | I2 | CE-PAGE-030 |
| `extensions/code/utils/replace-code-block-with-text.ts` | K1 | `ED/core/src/extensions/code/utils/replace-code-block-with-text.ts` | – | I2 | CE-PAGE-030 |
| `extensions/code/without-props.tsx` | K1 | `ED/core/src/extensions/code/without-props.ts` | CustomCodeBlockExtensionWithoutProps | I2 | CE-PAGE-030 |
| `extensions/core-without-props.ts` | K2 | `ED/core/src/extensions/core-without-props.ts` | CoreEditorExtensionsWithoutProps, DocumentEditorExtensionsWithoutProps (unverändert, Quelle Server-Schema-Golden) + Getter `getCoreEditorExtensionsWithoutProps()`, `getDocumentEditorExtensionsWithoutProps()` (`PORT-DIFF(block-registry)`, R-ED-12) | I2 | Querschnitt (CE-PAGE-021…023) |
| `extensions/core/extensions.ts` | K2 | `ED/core/src/extensions/core/extensions.ts` | CoreEditorAdditionalExtensions() → Beiträge aus EditorBlockRegistry; D9-Andockpunkt | I2 | Querschnitt (CE-PAGE-021…023) |
| `extensions/core/index.ts` | PA | `ED/core/src/extensions/core/index.ts` | Barrel | I2 | Querschnitt (CE-PAGE-021…023) |
| `extensions/core/without-props.ts` | K1 | `ED/core/src/extensions/core/without-props.ts` | CoreEditorAdditionalExtensionsWithoutProps (CE leer, unverändert; Paket-Beiträge über den Getter, R-ED-12) | I2 | Querschnitt (CE-PAGE-021…023) |
| `extensions/custom-color.ts` | K1 | `ED/core/src/extensions/custom-color.ts` | CustomColorExtension | I2 | CE-PAGE-029 |
| `extensions/custom-image/components/block.tsx` | NG | `ED/components/src/extensions/custom-image/components/block.component.ts` | PlEdImageBlock | I2 | CE-PAGE-032 |
| `extensions/custom-image/components/node-view.tsx` | NG | `ED/components/src/extensions/custom-image/components/node-view.component.ts` | PlEdCustomImageNodeView `[plEdCustomImageNodeView]` | I2 | CE-PAGE-032 |
| `extensions/custom-image/components/toolbar/alignment.tsx` | NG | `ED/components/src/extensions/custom-image/components/toolbar/alignment.component.ts` | PlEdImageAlignmentAction | I2 | CE-PAGE-032 |
| `extensions/custom-image/components/toolbar/download.tsx` | NG | `ED/components/src/extensions/custom-image/components/toolbar/download.component.ts` | PlEdImageDownloadAction | I2 | CE-PAGE-032 |
| `extensions/custom-image/components/toolbar/full-screen/index.ts` | PA | `ED/components/src/extensions/custom-image/components/toolbar/full-screen/index.ts` | Barrel | I2 | CE-PAGE-032 |
| `extensions/custom-image/components/toolbar/full-screen/modal.tsx` | NG | `ED/components/src/extensions/custom-image/components/toolbar/full-screen/modal.component.ts` | PlEdImageFullScreenModal (Portal nach #editor-portal) | I2 | CE-PAGE-032 |
| `extensions/custom-image/components/toolbar/full-screen/root.tsx` | NG | `ED/components/src/extensions/custom-image/components/toolbar/full-screen/root.component.ts` | PlEdImageFullScreenAction | I2 | CE-PAGE-032 |
| `extensions/custom-image/components/toolbar/index.ts` | PA | `ED/components/src/extensions/custom-image/components/toolbar/index.ts` | Barrel | I2 | CE-PAGE-032 |
| `extensions/custom-image/components/toolbar/root.tsx` | NG | `ED/components/src/extensions/custom-image/components/toolbar/root.component.ts` | PlEdImageToolbarRoot | I2 | CE-PAGE-032 |
| `extensions/custom-image/components/upload-status.tsx` | NG | `ED/components/src/extensions/custom-image/components/upload-status.component.ts` | PlEdImageUploadStatus (editorState-Signal statt useEditorState) | I2 | CE-PAGE-032 |
| `extensions/custom-image/components/uploader.tsx` | NG | `ED/components/src/extensions/custom-image/components/uploader.component.ts` | PlEdImageUploader | I2 | CE-PAGE-032 |
| `extensions/custom-image/extension-config.ts` | K1 | `ED/core/src/extensions/custom-image/extension-config.ts` | CustomImageExtensionConfig | I2 | CE-PAGE-032 |
| `extensions/custom-image/extension.tsx` | NV | `ED/core/src/extensions/custom-image/extension.ts` | CustomImageExtension; addNodeView → uiNodeView('custom-image') | I2 | CE-PAGE-032 |
| `extensions/custom-image/types.ts` | K1 | `ED/core/src/extensions/custom-image/types.ts` | – | I2 | CE-PAGE-032 |
| `extensions/custom-image/utils.ts` | K2 | `ED/core/src/extensions/custom-image/utils.ts` | Ausrichtungs-Optionen mit PlIconDef | I2 | CE-PAGE-032 |
| `extensions/custom-link/extension.tsx` | K1 | `ED/core/src/extensions/custom-link/extension.ts` | CustomLinkExtension | I2 | CE-PAGE-036 |
| `extensions/custom-link/helpers/autolink.ts` | K1 | `ED/core/src/extensions/custom-link/helpers/autolink.ts` | – | I2 | CE-PAGE-036 |
| `extensions/custom-link/helpers/clickHandler.ts` | K1 | `ED/core/src/extensions/custom-link/helpers/clickHandler.ts` | – | I2 | CE-PAGE-036 |
| `extensions/custom-link/helpers/pasteHandler.ts` | K1 | `ED/core/src/extensions/custom-link/helpers/pasteHandler.ts` | – | I2 | CE-PAGE-036 |
| `extensions/custom-link/index.ts` | PA | `ED/core/src/extensions/custom-link/index.ts` | – | I2 | CE-PAGE-036 |
| `extensions/custom-list-keymap/index.ts` | PA | `ED/core/src/extensions/custom-list-keymap/index.ts` | – | I2 | CE-PAGE-028 |
| `extensions/custom-list-keymap/list-helpers.ts` | K1 | `ED/core/src/extensions/custom-list-keymap/list-helpers.ts` | – | I2 | CE-PAGE-028 |
| `extensions/custom-list-keymap/list-keymap.ts` | K1 | `ED/core/src/extensions/custom-list-keymap/list-keymap.ts` | ListKeymap | I2 | CE-PAGE-028 |
| `extensions/document-extensions.tsx` | K2 | `ED/core/src/extensions/document-extensions.ts` | DocumentEditorAdditionalExtensions() (Registry 1:1); S50 | I2 | CE-PAGE-023, CE-WI-041 |
| `extensions/emoji/components/emojis-list.tsx` | NG | `ED/components/src/extensions/emoji/components/emojis-list.component.ts` | PlEdEmojisListDropdown | I2 | CE-PAGE-035 |
| `extensions/emoji/emoji.ts` | K1 | `ED/core/src/extensions/emoji/emoji.ts` | Emoji (Fork) | I2 | CE-PAGE-035 |
| `extensions/emoji/extension.ts` | K1 | `ED/core/src/extensions/emoji/extension.ts` | EmojiExtension; Teil des Server-Schemas | I2 | CE-PAGE-035 |
| `extensions/emoji/suggestion.ts` | NV | `ED/core/src/extensions/emoji/suggestion.ts` | emojiSuggestion; ReactRenderer → uiRender('emojis-list-dropdown') | I2 | CE-PAGE-035 |
| `extensions/enter-key.ts` | K1 | `ED/core/src/extensions/enter-key.ts` | EnterKeyExtension | I2 | CE-PAGE-022, CE-WI-037 |
| `extensions/extensions.ts` | K1 | `ED/core/src/extensions/extensions.ts` | CoreEditorExtensions() 1:1 | I2 | Querschnitt (CE-PAGE-021…023) |
| `extensions/headings-list.ts` | K2 | `ED/core/src/extensions/headings-list.ts` | HeadingListExtension; E12 korrigiert (FE-ED-06) | I2 | CE-PAGE-016 |
| `extensions/horizontal-rule.ts` | K1 | `ED/core/src/extensions/horizontal-rule.ts` | CustomHorizontalRule | I2 | CE-PAGE-027 |
| `extensions/image/extension-config.tsx` | K1 | `ED/core/src/extensions/image/extension-config.ts` | ImageExtensionConfig | I2 | CE-PAGE-032 |
| `extensions/image/extension.tsx` | NV | `ED/core/src/extensions/image/extension.ts` | ImageExtension; addNodeView → uiNodeView('custom-image') | I2 | CE-PAGE-032 |
| `extensions/image/index.ts` | PA | `ED/core/src/extensions/image/index.ts` | Barrel | I2 | CE-PAGE-032 |
| `extensions/index.ts` | PA | `ED/core/src/extensions/index.ts` | Barrel | I2 | Querschnitt (CE-PAGE-021…023) |
| `extensions/keymap.ts` | K1 | `ED/core/src/extensions/keymap.ts` | CustomKeymap | I2 | CE-PAGE-028 |
| `extensions/mentions/extension-config.ts` | K1 | `ED/core/src/extensions/mentions/extension-config.ts` | CustomMentionExtensionConfig | I2 | CE-PAGE-034, CE-WI-044 |
| `extensions/mentions/extension.tsx` | NV | `ED/core/src/extensions/mentions/extension.ts` | CustomMentionExtension; addNodeView → uiNodeView('mention') | I2 | CE-PAGE-034, CE-WI-044 |
| `extensions/mentions/index.ts` | PA | `ED/core/src/extensions/mentions/index.ts` | Barrel | I2 | CE-PAGE-034, CE-WI-044 |
| `extensions/mentions/mention-node-view.tsx` | NG | `ED/components/src/extensions/mentions/mention-node-view.component.ts` | PlEdMentionNodeView `[plEdMentionNodeView]` | I2 | CE-PAGE-034, CE-WI-044 |
| `extensions/mentions/mentions-list-dropdown.tsx` | NG | `ED/components/src/extensions/mentions/mentions-list-dropdown.component.ts` | PlEdMentionsListDropdown | I2 | CE-PAGE-034, CE-WI-044 |
| `extensions/mentions/types.ts` | K1 | `ED/core/src/extensions/mentions/types.ts` | – | I2 | CE-PAGE-034, CE-WI-044 |
| `extensions/mentions/utils.ts` | NV | `ED/core/src/extensions/mentions/utils.ts` | renderMentionsDropdown; ReactRenderer → uiRender('mentions-list-dropdown') | I2 | CE-PAGE-034, CE-WI-044 |
| `extensions/placeholder.ts` | K1 | `ED/core/src/extensions/placeholder.ts` | CustomPlaceholderExtension | I2 | CE-PAGE-038 |
| `extensions/quote.ts` | K1 | `ED/core/src/extensions/quote.ts` | CustomQuoteExtension | I2 | CE-PAGE-027 |
| `extensions/rich-text-extensions.tsx` | K2 | `ED/core/src/extensions/rich-text-extensions.ts` | RichTextEditorAdditionalExtensions() (Registry 1:1) | I2 | CE-PAGE-021, CE-WI-005 |
| `extensions/side-menu.ts` | K1 | `ED/core/src/extensions/side-menu.ts` | SideMenuExtension | I2 | CE-PAGE-026 |
| `extensions/slash-commands/command-items-list.tsx` | K2 | `ED/core/src/extensions/slash-commands/command-items-list.ts` | getSlashCommandFilteredSections() (Icons → PlIconDef, `Smile` → lucide-Konstante); E1 korrigiert (FE-ED-02) | I2 | CE-PAGE-024 |
| `extensions/slash-commands/command-menu-item.tsx` | NG | `ED/components/src/extensions/slash-commands/command-menu-item.component.ts` | PlEdSlashCommandMenuItem `button[plEdSlashCommandMenuItem]` | I2 | CE-PAGE-024 |
| `extensions/slash-commands/command-menu.tsx` | NG | `ED/components/src/extensions/slash-commands/command-menu.component.ts` | PlEdSlashCommandsMenu | I2 | CE-PAGE-024 |
| `extensions/slash-commands/index.ts` | PA | `ED/core/src/extensions/slash-commands/index.ts` | Barrel | I2 | CE-PAGE-024 |
| `extensions/slash-commands/root.tsx` | NV | `ED/core/src/extensions/slash-commands/root.ts` | SlashCommands; ReactRenderer → uiRender('slash-commands-menu') | I2 | CE-PAGE-024 |
| `extensions/starter-kit.ts` | K1 | `ED/core/src/extensions/starter-kit.ts` | CustomStarterKitExtension | I2 | CE-PAGE-027 |
| `extensions/table/index.ts` | PA | `ED/core/src/extensions/table/index.ts` | Barrel | I2 | CE-PAGE-031 |
| `extensions/table/plugins/drag-handles/actions.ts` | K1 | `ED/core/src/extensions/table/plugins/drag-handles/actions.ts` | – | I2 | CE-PAGE-031 |
| `extensions/table/plugins/drag-handles/color-selector.tsx` | NG | `ED/components/src/extensions/table/plugins/drag-handles/color-selector.component.ts` | PlEdTableDragHandleColorSelector (PlCollapsible) | I2 | CE-PAGE-031 |
| `extensions/table/plugins/drag-handles/column/drag-handle.tsx` | NG | `ED/components/src/extensions/table/plugins/drag-handles/column/drag-handle.component.ts` | PlEdTableColumnDragHandle | I2 | CE-PAGE-026 |
| `extensions/table/plugins/drag-handles/column/dropdown.tsx` | NG | `ED/components/src/extensions/table/plugins/drag-handles/column/dropdown.component.ts` | PlEdTableColumnDropdown | I2 | CE-PAGE-031 |
| `extensions/table/plugins/drag-handles/column/plugin.ts` | NV | `ED/core/src/extensions/table/plugins/drag-handles/column/plugin.ts` | TableColumnDragHandlePlugin; ReactRenderer → uiRender('table-column-drag-handle') | I2 | CE-PAGE-031 |
| `extensions/table/plugins/drag-handles/column/utils.ts` | K1 | `ED/core/src/extensions/table/plugins/drag-handles/column/utils.ts` | – | I2 | CE-PAGE-031 |
| `extensions/table/plugins/drag-handles/marker-utils.ts` | K1 | `ED/core/src/extensions/table/plugins/drag-handles/marker-utils.ts` | – | I2 | CE-PAGE-031 |
| `extensions/table/plugins/drag-handles/row/drag-handle.tsx` | NG | `ED/components/src/extensions/table/plugins/drag-handles/row/drag-handle.component.ts` | PlEdTableRowDragHandle | I2 | CE-PAGE-026 |
| `extensions/table/plugins/drag-handles/row/dropdown.tsx` | NG | `ED/components/src/extensions/table/plugins/drag-handles/row/dropdown.component.ts` | PlEdTableRowDropdown | I2 | CE-PAGE-031 |
| `extensions/table/plugins/drag-handles/row/plugin.ts` | NV | `ED/core/src/extensions/table/plugins/drag-handles/row/plugin.ts` | TableRowDragHandlePlugin; ReactRenderer → uiRender('table-row-drag-handle') | I2 | CE-PAGE-031 |
| `extensions/table/plugins/drag-handles/row/utils.ts` | K1 | `ED/core/src/extensions/table/plugins/drag-handles/row/utils.ts` | – | I2 | CE-PAGE-031 |
| `extensions/table/plugins/drag-handles/utils.ts` | K1 | `ED/core/src/extensions/table/plugins/drag-handles/utils.ts` | – | I2 | CE-PAGE-031 |
| `extensions/table/plugins/drag-state.ts` | K1 | `ED/core/src/extensions/table/plugins/drag-state.ts` | – | I2 | CE-PAGE-031 |
| `extensions/table/plugins/insert-handlers/plugin.ts` | K1 | `ED/core/src/extensions/table/plugins/insert-handlers/plugin.ts` | – | I2 | CE-PAGE-031 |
| `extensions/table/plugins/insert-handlers/utils.ts` | K1 | `ED/core/src/extensions/table/plugins/insert-handlers/utils.ts` | – | I2 | CE-PAGE-031 |
| `extensions/table/plugins/selection-outline/plugin.ts` | K1 | `ED/core/src/extensions/table/plugins/selection-outline/plugin.ts` | – | I2 | CE-PAGE-031 |
| `extensions/table/plugins/selection-outline/utils.ts` | K1 | `ED/core/src/extensions/table/plugins/selection-outline/utils.ts` | – | I2 | CE-PAGE-031 |
| `extensions/table/table-cell.ts` | K1 | `ED/core/src/extensions/table/table-cell.ts` | – | I2 | CE-PAGE-031 |
| `extensions/table/table-header.ts` | K1 | `ED/core/src/extensions/table/table-header.ts` | – | I2 | CE-PAGE-031 |
| `extensions/table/table-row.ts` | K1 | `ED/core/src/extensions/table/table-row.ts` | – | I2 | CE-PAGE-031 |
| `extensions/table/table/icons.ts` | K1 | `ED/core/src/extensions/table/table/icons.ts` | – | I2 | CE-PAGE-031 |
| `extensions/table/table/index.ts` | PA | `ED/core/src/extensions/table/table/index.ts` | – | I2 | CE-PAGE-031 |
| `extensions/table/table/table-view.tsx` | K2 | `ED/core/src/extensions/table/table/table-view.ts` | TableView (jsx-dom `h` → helpers/dom-builder.ts) | I2 | CE-PAGE-031 |
| `extensions/table/table/table.ts` | K1 | `ED/core/src/extensions/table/table/table.ts` | Table (Option `View: TableView` – Vanilla-NodeView) | I2 | CE-PAGE-031 |
| `extensions/table/table/utilities/create-cell.ts` | K1 | `ED/core/src/extensions/table/table/utilities/create-cell.ts` | – | I2 | CE-PAGE-031 |
| `extensions/table/table/utilities/create-table.ts` | K1 | `ED/core/src/extensions/table/table/utilities/create-table.ts` | – | I2 | CE-PAGE-031 |
| `extensions/table/table/utilities/delete-column.ts` | K1 | `ED/core/src/extensions/table/table/utilities/delete-column.ts` | – | I2 | CE-PAGE-031 |
| `extensions/table/table/utilities/delete-key-shortcut.ts` | K1 | `ED/core/src/extensions/table/table/utilities/delete-key-shortcut.ts` | – | I2 | CE-PAGE-031 |
| `extensions/table/table/utilities/delete-row.ts` | K1 | `ED/core/src/extensions/table/table/utilities/delete-row.ts` | – | I2 | CE-PAGE-031 |
| `extensions/table/table/utilities/get-table-node-types.ts` | K1 | `ED/core/src/extensions/table/table/utilities/get-table-node-types.ts` | – | I2 | CE-PAGE-031 |
| `extensions/table/table/utilities/helpers.ts` | K1 | `ED/core/src/extensions/table/table/utilities/helpers.ts` | – | I2 | CE-PAGE-031 |
| `extensions/table/table/utilities/insert-line-above-table-action.ts` | K1 | `ED/core/src/extensions/table/table/utilities/insert-line-above-table-action.ts` | – | I2 | CE-PAGE-031 |
| `extensions/table/table/utilities/insert-line-below-table-action.ts` | K1 | `ED/core/src/extensions/table/table/utilities/insert-line-below-table-action.ts` | – | I2 | CE-PAGE-031 |
| `extensions/text-align.ts` | K1 | `ED/core/src/extensions/text-align.ts` | – | I2 | CE-PAGE-027 |
| `extensions/title-extension.ts` | K1 | `ED/core/src/extensions/title-extension.ts` | TitleExtensions | I4 | CE-PAGE-013, CE-PAGE-038 |
| `extensions/trailing-node.ts` | K1 | `ED/core/src/extensions/trailing-node.ts` | – | I2 | CE-PAGE-027 |
| `extensions/typography/index.ts` | K1 | `ED/core/src/extensions/typography/index.ts` | – | I2 | CE-PAGE-029 |
| `extensions/typography/inputRules.ts` | K1 | `ED/core/src/extensions/typography/inputRules.ts` | – | I2 | CE-PAGE-029 |
| `extensions/unique-id/extension.ts` | K2 | `ED/core/src/extensions/unique-id/extension.ts` | COMBINED_BLOCK_NODE_TYPES als Getter (R-ED-12); PORT-DIFF(block-registry) | I2 | CE-PAGE-039 |
| `extensions/unique-id/plugin.ts` | K1 | `ED/core/src/extensions/unique-id/plugin.ts` | – | I2 | CE-PAGE-039 |
| `extensions/unique-id/utils.ts` | K1 | `ED/core/src/extensions/unique-id/utils.ts` | – | I2 | CE-PAGE-039 |
| `extensions/utility.ts` | K1 | `ED/core/src/extensions/utility.ts` | – | I2 | Querschnitt (CE-PAGE-021…023) |
| `extensions/work-item-embed/extension-config.ts` | K1 | `ED/core/src/extensions/work-item-embed/extension-config.ts` | WorkItemEmbedExtensionConfig (nur Server-/Document-Schema); Schema-Freeze | I2 | CE-PAGE-023 (Schema) |
| `extensions/work-item-embed/extension.tsx` | EX | – | –; Runtime in CE nicht registriert; Paket D6 liefert NodeView über EDITOR_BLOCKS | – | CE-PAGE-023 (Schema) |
| `extensions/work-item-embed/index.ts` | PA | `ED/core/src/extensions/work-item-embed/index.ts` | Barrel (nur Config + Typen) | I2 | CE-PAGE-023 (Schema) |
| `extensions/work-item-embed/types.ts` | K1 | `ED/core/src/extensions/work-item-embed/types.ts` | – | I2 | CE-PAGE-023 (Schema) |
| `helpers/asset-duplication.ts` | K1 | `ED/core/src/helpers/asset-duplication.ts` | – | I2 | CE-PAGE-032 |
| `helpers/assets.ts` | K2 | `ED/core/src/helpers/assets.ts` | liest assetMetaData der Block-Registry; PORT-DIFF(block-registry) | I2 | CE-PAGE-032 |
| `helpers/common.ts` | K1 | `ED/core/src/helpers/common.ts` | – | I2 | Querschnitt (CE-PAGE-021…023) |
| `helpers/editor-commands.ts` | K1 | `ED/core/src/helpers/editor-commands.ts` | – | I2 | CE-PAGE-014, CE-WI-037 |
| `helpers/editor-ref.ts` | K1 | `ED/core/src/helpers/editor-ref.ts` | getEditorRefHelpers() → EditorRefApi | I2 | CE-PAGE-016, CE-PAGE-017, CE-PAGE-018, CE-PAGE-037 |
| `helpers/file.ts` | K1 | `ED/core/src/helpers/file.ts` | – | I2 | CE-PAGE-032 |
| `helpers/find-suggestion-match.ts` | K1 | `ED/core/src/helpers/find-suggestion-match.ts` | – | I2 | Querschnitt (CE-PAGE-021…023) |
| `helpers/floating-ui.ts` | K1 | `ED/core/src/helpers/floating-ui.ts` | – | I2 | Querschnitt (CE-PAGE-021…023) |
| `helpers/get-document-server-event.ts` | K1 | `ED/core/src/helpers/get-document-server-event.ts` | – | I4 | CE-RT-004 |
| `helpers/image-helpers.ts` | K1 | `ED/core/src/helpers/image-helpers.ts` | – | I2 | CE-PAGE-032 |
| `helpers/insert-content-at-cursor-position.ts` | K2 | `ED/core/src/helpers/insert-content-at-cursor-position.ts` | Typ-Import `@tiptap/react` → `@tiptap/core` | I2 | Querschnitt (CE-PAGE-021…023) |
| `helpers/insert-empty-paragraph-at-node-boundary.ts` | K1 | `ED/core/src/helpers/insert-empty-paragraph-at-node-boundary.ts` | – | I2 | Querschnitt (CE-PAGE-021…023) |
| `helpers/parser.ts` | K2 | `ED/core/src/helpers/parser.ts` | extract/replaceAdditionalAssets… lesen die Block-Registry; PORT-DIFF(block-registry) | I2 | CE-RT-003, CE-RT-008, CE-PAGE-009 |
| `helpers/paste-asset.ts` | K1 | `ED/core/src/helpers/paste-asset.ts` | – | I2 | CE-PAGE-032 |
| `helpers/scroll-to-node.ts` | K2 | `ED/core/src/helpers/scroll-to-node.ts` | Typ-Import `@tiptap/react` → `@tiptap/core` | I2 | CE-PAGE-039 |
| `helpers/tippy.ts` | K1 | `ED/core/src/helpers/tippy.ts` | – | I2 | Querschnitt (CE-PAGE-021…023) |
| `helpers/yjs-utils.ts` | K2 | `ED/core/src/helpers/yjs-utils.ts` | – (`PORT-DIFF(block-registry)`: Extension-Listen zur Laufzeit über Getter, R-ED-12) | I2 | CE-RT-003, CE-RT-008, CE-PAGE-009 |
| `hooks/use-collaborative-editor.ts` | SV | `ED/components/src/services/collaborative-editor-instance.ts` | CollaborativeEditorInstance (Komponenten-Provider) | I4 | CE-PAGE-013, CE-RT-002 |
| `hooks/use-editor-navigation.ts` | SV | `ED/core/src/hooks/editor-navigation.ts` | createTitleEditorNavigation(), createMainEditorNavigation() (reine Funktionen) | I4 | CE-PAGE-013, CE-PAGE-038 |
| `hooks/use-editor.ts` | SV | `ED/components/src/services/editor-instance.ts` | EditorInstance (useEditor-Semantik, Komponenten-Provider) | I2 | Querschnitt (CE-PAGE-021…023) |
| `hooks/use-file-upload.ts` | SV | `ED/components/src/services/file-upload.ts` | createUploader(), Direktive `[plEdDropZone]` | I2 | CE-PAGE-032 |
| `hooks/use-title-editor.ts` | SV | `ED/components/src/services/title-editor-instance.ts` | TitleEditorInstance | I4 | CE-PAGE-013, CE-PAGE-038 |
| `hooks/use-yjs-setup.ts` | SV | `ED/collaboration/src/collaboration-session.ts` | CollaborationSession (Stage-Maschine 1:1, Signals) | I4 | CE-PAGE-013, CE-RT-002 |
| `index.ts` | PA | `ED/components/src/public-api.ts` | `@plane/editor` (gleiche Export-Namen ohne `WithRef`-Suffix-Komponenten: Komponenten-Klassen) | I2 | Querschnitt (CE-PAGE-021…023) |
| `lib.ts` | PA | `ED/core/src/lib.ts` | `@plane/editor/core` – Server-Schema + Konverter (nur Tests/Golden) | I2 | Querschnitt (CE-PAGE-021…023) |
| `plugins/ai-handle.ts` | K1 | `ED/core/src/plugins/ai-handle.ts` | AIHandlePlugin (nur bei Flag ai); G1/G3-Andockpunkt, CE inaktiv | I2 | CE-PAGE-026 |
| `plugins/drag-handle.ts` | K2 | `ED/core/src/plugins/drag-handle.ts` | DragHandlePlugin (generalSelectors + Beiträge aus EditorBlockRegistry); D9-Andockpunkt | I2 | CE-PAGE-026 |
| `plugins/drop.ts` | K2 | `ED/core/src/plugins/drop.ts` | DropHandlerPlugin (Attachment-Zweig → EditorBlockRegistry.fileDropHandlers); D9-Andockpunkt, E23 | I2 | CE-PAGE-032 |
| `plugins/file/delete.ts` | K1 | `ED/core/src/plugins/file/delete.ts` | – | I2 | CE-PAGE-032 |
| `plugins/file/restore.ts` | K1 | `ED/core/src/plugins/file/restore.ts` | – | I2 | CE-PAGE-032 |
| `plugins/file/root.ts` | K1 | `ED/core/src/plugins/file/root.ts` | – | I2 | CE-PAGE-032 |
| `plugins/file/types.ts` | K1 | `ED/core/src/plugins/file/types.ts` | – | I2 | CE-PAGE-032 |
| `plugins/highlight.ts` | K1 | `ED/core/src/plugins/highlight.ts` | nodeHighlight (wie Original nicht registriert, E22) | I2 | CE-PAGE-039 |
| `plugins/markdown-clipboard.ts` | K1 | `ED/core/src/plugins/markdown-clipboard.ts` | – | I2 | CE-PAGE-037 |
| `props.ts` | K1 | `ED/core/src/props.ts` | CoreEditorProps | I2 | Querschnitt (CE-PAGE-021…023) |
| `styles/drag-drop.css` | CSS | `ED/styles/drag-drop.css` | Import-Position 09 §3.2.2 | I2 | CE-PAGE-026 |
| `styles/editor.css` | CSS | `ED/styles/editor.css` | Import-Position 09 §3.2.2 | I2 | Querschnitt (CE-PAGE-021…023) |
| `styles/github-dark.css` | CSS | `ED/styles/github-dark.css` | Import-Position 09 §3.2.2 | I2 | CE-PAGE-030 |
| `styles/index.css` | CSS | `ED/styles/index.css` | Import-Position 09 §3.2.2 | I2 | Querschnitt (CE-PAGE-021…023) |
| `styles/table.css` | CSS | `ED/styles/table.css` | Import-Position 09 §3.2.2 | I2 | CE-PAGE-031 |
| `styles/title-editor.css` | CSS | `ED/styles/title-editor.css` | Import-Position 09 §3.2.2 | I2 | CE-PAGE-013, CE-PAGE-038 |
| `styles/variables.css` | CSS | `ED/styles/variables.css` | Import-Position 09 §3.2.2 | I2 | CE-PAGE-040, CE-I18N-010 |
| `types/ai.ts` | K2 | `ED/core/src/types/ai.ts` | ReactNode → TEditorRenderable | I2 | Querschnitt (CE-PAGE-021…023) |
| `types/asset.ts` | K1 | `ED/core/src/types/asset.ts` | – | I2 | Querschnitt (CE-PAGE-021…023) |
| `types/collaboration.ts` | K1 | `ED/core/src/types/collaboration.ts` | – | I2 | CE-PAGE-013, CE-RT-002 |
| `types/config.ts` | K1 | `ED/core/src/types/config.ts` | – | I2 | Querschnitt (CE-PAGE-021…023) |
| `types/document-collaborative-events.ts` | K1 | `ED/core/src/types/document-collaborative-events.ts` | – | I4 | CE-RT-004 |
| `types/editor-extended.ts` | K1 | `ED/core/src/types/editor-extended.ts` | 1:1 (D16-ADR-15, S48); V-Andockpunkt | I2 | Querschnitt (CE-PAGE-021…023) |
| `types/editor.ts` | K2 | `ED/core/src/types/editor.ts` | IEditorProps & Co. (MutableRefObject/ReactNode → agnostische Typen, §3.3) | I2 | Querschnitt (CE-PAGE-021…023) |
| `types/embed.ts` | K2 | `ED/core/src/types/embed.ts` | ReactNode → TEditorRenderable | I2 | Querschnitt (CE-PAGE-021…023) |
| `types/extensions.ts` | K1 | `ED/core/src/types/extensions.ts` | – | I2 | Querschnitt (CE-PAGE-021…023) |
| `types/hook.ts` | K1 | `ED/core/src/types/hook.ts` | – | I2 | Querschnitt (CE-PAGE-021…023) |
| `types/index.ts` | PA | `ED/core/src/types/index.ts` | – | I2 | Querschnitt (CE-PAGE-021…023) |
| `types/issue-embed.ts` | K2 | `ED/core/src/types/issue-embed.ts` | ReactNode → TEditorRenderable | I2 | Querschnitt (CE-PAGE-021…023) |
| `types/mention.ts` | K2 | `ED/core/src/types/mention.ts` | TMentionHandler.renderComponent → TEditorRenderable | I2 | Querschnitt (CE-PAGE-021…023) |
| `types/slash-commands-suggestion.ts` | K2 | `ED/core/src/types/slash-commands-suggestion.ts` | CSSProperties → Partial<CSSStyleDeclaration> | I2 | CE-PAGE-024 |
| `types/storage.ts` | K1 | `ED/core/src/types/storage.ts` | – | I2 | Querschnitt (CE-PAGE-021…023) |
| `types/utils.ts` | K1 | `ED/core/src/types/utils.ts` | – | I2 | Querschnitt (CE-PAGE-021…023) |

---

## Anhang B – Prüfprotokoll

> **Stand:** 23.10.2026. Prüfmethode: Quelltext des Originals (`packages/editor/src`, 225 Dateien, per `find` gezählt), Lockfile `pnpm-lock.yaml` (Importer `packages/editor`, aufgelöste Versionen), npm-Registry-Abfragen (`npm view`) sowie die verbindlichen Nachbardokumente 00, 01, 08, 09, 15, 16, 17.

| Behauptung | Prüfung | Ergebnis |
|---|---|---|
| Tiptap-Versionen des Originals | `pnpm-lock.yaml`, Importer `packages/editor` | `@tiptap/core` 2.27.3; Extensions/`pm`/`starter-kit`/`suggestion` 2.26.1; `@tiptap/html` 2.26.2; StarterKit-Kinder 2.26.2; `@tiptap/extension-bubble-menu` 2.26.3 (über `@tiptap/react` 2.26.1). D01 §8.2 nennt „2.22.3 (Rest)“ = Catalog-Untergrenze, nicht die aufgelöste Version → Rückmeldung §9 |
| Tiptap-2-Linie abgeschlossen | `npm view @tiptap/core dist-tags` | `v2-latest` 2.27.3, `latest` 3.32.0 |
| ngx-tiptap 13 | `npm view ngx-tiptap@13` | 13.0.0, MIT, Peers `@tiptap/core ^2.7.0`, `@tiptap/pm ^2.7.0`, `@tiptap/extension-bubble-menu ^2.7.0`, `@tiptap/extension-floating-menu ^2.7.0`, `@angular/core >=20.0.0` |
| Kollaborations-Cursor für Tiptap 2 verfügbar | `npm view @tiptap/extension-collaboration-cursor@2.26.1` | vorhanden, MIT, Peers `@tiptap/core ^2.7.0`, `y-prosemirror ^1.2.11` |
| Emoji-Daten im Editor | `ED0/extensions/emoji/{emoji,extension}.ts`, Lockfile | Daten aus `@tiptap/extension-emoji` (`emojis`, `gitHubEmojis`), Abhängigkeit `emojibase-data` 15.3.2 → deckungsgleich mit ABG-029 |
| Callout-Default-URL | `ED0/extensions/callout/utils.ts` Z. 20 | `https://cdn.jsdelivr.net/npm/emoji-datasource-apple/img/apple/64/1f4a1.png` (Attribut-Default, keine Ladestelle im CE-Code gefunden) |
| CSS adressiert NodeView-Außenelemente | `grep node-imageComponent ED0/styles` | `drag-drop.css` Z. 38, 63, 106 → DOM-Vertrag `react-renderer node-<typ>` nötig (D10-ADR-05) |
| Tiptap-CSS-Injektion im Original | `grep injectCSS` in `packages`, `apps` | nicht gesetzt → Default `true` (Laufzeit-`<style>`), daher D10-ADR-13 |
| React-Renderer-Aufrufstellen | `grep ReactNodeViewRenderer\|ReactRenderer ED0/` | 6 `ReactNodeViewRenderer` (Callout, Custom-Image, Mention, Code, Legacy-Image, Work-Item-Embed) + 5 `ReactRenderer` (Slash, Mention-Dropdown, Emoji-Suggestion, Tabellen-Spalte, -Zeile); ohne Work-Item-Embed (EX) = 10 NV-Dateien |
| Server-Schema hängt an `EmojiExtension` und `Table` | `ED0/extensions/core-without-props.ts`, `table/table/table.ts` | ja → UI-Port statt Verschiebung in die Angular-Schicht (D10-ADR-04) |
| Web-Flags | `WEB/hooks/use-editor-flagging.ts` | alle Varianten `disabled: ["ai", "collaboration-cursor"]`, `flagged: []` |
| Mention-Hover der Web-Hülle | `WEB/components/editor/embeds/mentions/user.tsx` | Propel `PopoverContent variant="rich"`; keine `is_bot`-Auswertung |
| Toolbar-Kürzel (E9) | `ED0/constants/common.ts` vs. Tiptap-Defaults | Labels vertauscht (Bulleted Cmd+Shift+7 / Numbered Cmd+Shift+8; Tiptap: BulletList Mod-Shift-8, OrderedList Mod-Shift-7) |
| Branding (ADR-009B) | `grep -rn '"[^"]*Plane[^"]*"' ED0/` (ohne Importe/PluginKeys) | keine sichtbaren Texte mit „Plane“; nur der interne MIME-Typ `text/plane-editor-html` (BR-02); `BRAND-ED` leer, Gate G-BRAND (15) prüft das gebaute Editor-Bundle |
| Abgleich mit parallel entstandenen Nachbardokumenten | D07 (§3.12–§3.13, §7.5, D07-ADR-05/-11/-12/-25), D11 (§3.5 SR-03, `EditorMentionService`), D03 (D03-ADR-17) | Spec-Klassennamen, Golden-Dateinamen (Browser-Varianten unter `schema/browser/`), Ort `EditorMentionService` und Scope-Verhalten übernommen |

---

## Review-Protokoll

> **Adversarialer Review, 23.10.2026.** Prüfgegenstand: dieses Dokument gegen A12 (§2.5–§2.6, §3.25), F10 (`_data/ce-features.json`, alle 507 IDs auf Editor-Bezug gefiltert), F30 (🧱-Liste), 00/01/08/09/15/16/17 sowie D07 (§3.12–§3.13, §7.5, D07-ADR-05). Technische Aussagen wurden **am Quelltext der gepinnten Pakete** geprüft (`npm pack` aus der npm-Registry: `@tiptap/core` 2.27.3, `@tiptap/react` 2.26.1, `@tiptap/extension-emoji` 2.26.1, `@tiptap/extension-collaboration-cursor` 2.26.1, `prosemirror-view` 1.42.6, `prosemirror-state` 1.4.3, `ngx-tiptap` 13.0.0; TypeScript 5.9.3 für das Klassenfeld-Experiment), die Lockfile-Pins am `pnpm-lock.yaml` des Originals, die Datei-Abbildung per Skript gegen `packages/editor/src` (225/225 Dateien, keine fehlend/zusätzlich).

### R.1 Bestätigt (ohne Änderung)

| Aussage | Prüfung |
|---|---|
| Alle Versions-Pins §3.2.1 (inkl. StarterKit-Kinder 2.26.2, `@tiptap/html` 2.26.2, `bubble-menu` 2.26.3, ProseMirror-Transitiva, `lib0` 0.2.114, `@hocuspocus/common` 2.15.3, `emojibase-data` 15.3.2) | `pnpm-lock.yaml` Importer `packages/editor` und `packages:`-Sektion |
| `v2-latest` = 2.27.3, `latest` = 3.32.0; ngx-tiptap 13.0.0 MIT, Peers `@tiptap/core ^2.7.0`, `@angular/core >=20.0.0`; ngx-tiptap 14/15 nur Tiptap 3 | `npm view` |
| `@tiptap/extension-collaboration-cursor` 2.26.1: MIT, Peers `@tiptap/core ^2.7.0`, `y-prosemirror ^1.2.11` | `package.json` des Tarballs |
| 10 NV-Dateien (11 Aufrufstellen inkl. Work-Item-Embed = EX), Kategorien-Summen der JSON-Datei, 23 Nodes / 8 Marks / 19 funktionale Extensions aus A12 + 2 neue | Skript gegen `packages/editor/src`, A12 §2.5 |
| Toolbar-Labels E9 vertauscht (`constants/common.ts` Z. 136–146) | Quelltext |
| CSS-Zeilenzahlen §3.20.1, Importreihenfolge `index.css` | `wc -l`, Quelltext |
| Kein sichtbarer Text „Plane“ in `ED0/` | `grep` (ohne Copyright-Header, Importe, PluginKeys, MIME-Typ) |
| Alle 17 🧱-Pakete aus F30 in §6.1 behandelt; D9-Registry deckt alle leeren EE-Hooks des Originals ab; kein Fachdesign für Bezahl-Pakete | F30, `ED0/**` (`extensions/core/*`, `additional-slash-command-options.tsx`, `document-extensions.tsx`, `constants/{extensions,assets}.ts`, `helpers/parser.ts`, `plugins/{drop,drag-handle}.ts`) |
| Lizenzen: alle neuen/übernommenen Bibliotheken MIT/BSD (keine kommerziell gewordenen Pakete) | `package.json`/npm |

### R.2 Korrigiert (Fehler mit Wirkung auf die Umsetzung)

| # | Befund | Beleg | Korrektur |
|---|---|---|---|
| K-01 | `uiNodeView()` lieferte ohne Port `null` aus `addNodeView()` – Tiptap ruft `addNodeView()(props)` je Node auf → `TypeError` beim ersten Callout/Bild/Code-Block/Mention in jedem Port-losen Kontext (jsdom-Tests, G-DOC, Generator) | `@tiptap/core` 2.27.3 `ExtensionManager.ts` Z. 282–313 | `uiNodeView` liefert immer eine Fabrik, deren Aufruf ohne Port `null` zurückgibt; ProseMirror fällt dann auf `toDOM` zurück (`prosemirror-view` 1.42.6 `viewdesc.ts` Z. 707). D10-ADR-04, §3.4.3, §5.2; neuer Test `ui-port.no-port.spec.ts` |
| K-02 | `AngularNodeView` nutzte Feld-Initialisierer (`= null`, `= new Set()`, Pfeil-Property); `mount()` läuft aber im **Basiskonstruktor** → `this.handleSelectionUpdate` war beim `editor.on` `undefined`, `inputNames` beim `setInputs` `undefined` (TypeError), `contentDOMElement` wurde nach `mount()` auf `null` zurückgesetzt | `@tiptap/core` `NodeView.ts` Z. 55; Experiment mit `tsc` 5.9.3 (`TypeError: Cannot read properties of undefined (reading 'add')`) | Skelett §5.3 auf `declare`-Felder + Initialisierung in `mount()` umgestellt; Regel in §3.5.2; Test `angular-node-view.spec.ts` |
| K-03 | Selektion: Skelett setzte bei Bereichs-Selektion nur den Input, nicht die Klasse `ProseMirror-selectednode`; React ruft `selectNode()`/`deselectNode()` | `ReactNodeViewRenderer.tsx` (`handleSelectionUpdate`) | §3.5.1, §3.5.2, §5.3 |
| K-04 | `contentDOM`-Attribute: React setzt `data-node-view-content-react` **und** `data-node-view-wrapper`; Dokument nannte nur das erste (⚠) | `ReactNodeViewRenderer.tsx` Z. 83–84 | §3.5.1, §5.3, O-D10-05 |
| K-05 | `EditorContentDirective` hängte nur `view.dom` um; das Original ruft danach `editor.createNodeViews()` und baut beim Unmount NodeViews/Element zurück | `EditorContent.tsx` Z. 123–163, 166–200 | §3.5.1, §5.5 |
| K-06 | `editorState()` mit Default `Object.is` (Dokument behauptete „wie React, deepEqual-frei“) – React-Default ist `deepEqual`; mit `Object.is` feuerten Objekt-Selektoren (Bubble-Menü-Zustände, `editorAssetChange`) bei jeder Transaktion | `useEditorState.ts` Z. 2, 168 | D10-ADR-10, §3.5.3, §5.5; Pin `fast-deep-equal` 3.1.3 |
| K-07 | `value`-Sync las den Cursor **vor** `setContent`; Original liest ihn danach, mit `try/catch` | `ED0/hooks/use-editor.ts` | §3.7 Nr. 3, §5.6 |
| K-08 | `tiptap-core.css` sollte „unmittelbar vor“ `index.css` stehen; das Original hängt das Tag ans **Ende** von `<head>` → kehrte `white-space: break-spaces` (Tiptap) vs. `pre-wrap` (`editor.css` Z. 4) um | `createStyleTag.ts`; `style.ts`; `editor.css` Z. 1–4 | D10-ADR-13, §3.20.2 (letzter, ungeschichteter Import), §7.3 |
| K-09 | Emoji „keine `fallbackImage`-URLs“: der Datensatz enthält 1 814 jsDelivr- und 19 GitHub-Asset-URLs; nur die Plane-Konfiguration entfernt sie zur Laufzeit; Airgap-AK verlangte „nur der Callout-Eintrag“ | Dist `@tiptap/extension-emoji` 2.26.1; `ED0/extensions/emoji/extension.ts` Z. 33–35 | D10-ADR-12, §3.12 (Allowlist `ED-AIRGAP-01…03` mit `maxHits`), AK-D10-23 |
| K-10 | Block-Registry versiegelte beim **ersten Lesen**; Modul-Konstanten (`CoreEditorExtensionsWithoutProps`, `yjs-utils`-Listen, `COMBINED_BLOCK_NODE_TYPES`) werden beim Import – vor `provideAppInitializer` – ausgewertet → Registry wäre beim Bootstrap schon versiegelt bzw. Paket-Nodes fehlten im Client-Konverter | `core-without-props.ts`, `helpers/yjs-utils.ts` Z. 23–24, `unique-id/extension.ts` Z. 19 | explizites `sealEditorBlockRegistry()` beim ersten Editor; Getter (R-ED-12); `core-without-props.ts`, `yjs-utils.ts` K1 → K2, `core/without-props.ts` K2 → K1; Summen K1 101 / K2 28; 38 Handänderungs-Dateien; JSON aktualisiert |
| K-11 | Kern-Dateien (NV/K2) importieren Props-Typen aus React-Dateien (NG) – ohne Regel bliebe der Kern nicht framework-frei bzw. hinge an `ED/components` | `import type … from "./command-menu"` u. a. (10 Typen) | neue Regel R-ED-15, Datei `ED/core/src/ui-port/ui-props.ts` |
| K-12 | Mention-Render über `NgComponentOutlet` mit Attribut-Selektor `[plWebEditorMentionsRoot]` erzeugt ein zusätzliches `div` (Original `EditorMentionsRoot` rendert kein Element) | Angular erzeugt für Attribut-Selektoren ein `div`; `WEB/components/editor/embeds/mentions/root.tsx` | §3.10, §3.21: Element-Selektor + `data-pl-host` (N3) |
| K-13 | Golden-Serialisierer: `e.config.priority` verfehlt geerbte Prioritäten (`extend()`-Kette); Plugin-Keys ohne `PluginKey` tragen prozessweite Zähler (`plugin$1`) → Goldens instabil | `ExtensionManager.sort` (`getExtensionField`), `prosemirror-state` `createKey` | §5.9 (`getExtensionField`, Suffix-Normalisierung), §3.2.3/§3.2.4 (effektive Reihenfolge) |
| K-14 | Sheriff-Tag `propel:icons` existiert in D09 nicht; Kern-Import von `@plane/propel/icons` zieht Angular, falls der Einstieg `svg-icon.component.ts` re-exportiert | D09 §3.1 Baum, Sheriff-Tags D09 Z. 214 | §3.1, §5.1 (Tags `propel`/`blocks` + ESLint-Pfadregel), Rückmeldung D09 |
| K-15 | `upload`-Fortschritt: `effect` auf `fileHandler().assetsUploadStatus` feuert nur bei neuem Objekt | Signal-Semantik vs. MobX-Re-Render | §3.7 Nr. 4, §3.14 (`computed`-Handler) |

### R.3 Ergänzt (Vollständigkeit, Umsetzbarkeit)

- CE-IDs: CE-PAGE-015 (Sync-/Offline-Badges) und CE-RT-006 (Client-Teil Forced-Close) in §4.5; bewusst ausgeschlossene IDs (CE-PAGE-001…-010, -012, CE-RT-001, -005, -007, -008 Server, -009) in §1.3 mit Zuständigkeit.
- Close-Codes 4205/4403 aus D07-ADR-05 im Client (§3.15.1, AK-D10-14).
- Komponentenregeln (`OnPush`, `ViewEncapsulation.None`, keine Styles) für alle Editor-Libs (§3.1).
- Ablage und Sheriff-Tags der Paket-Blöcke `FE/libs/shared/editor/packages/<paket>/{core,ui}` (§3.1, §6.2 Regel 5).
- Visual-Abnahme I2 auf W-031 statt W-046 (W-046 ist die Page-Seite, I4), mit konkreten Zuständen (AK-D10-06).
- `collaboration-cursor.css` als neue (nicht im Original vorhandene) Datei gekennzeichnet (§3.1, §3.15.2).
- `#editor-portal` auch in Space (§3.21, Verweis D09 N1).
- Pins `emojibase` 16.0.0 (Peer) und `fast-deep-equal` 3.1.3; Testinventar um `ui-port.no-port.spec.ts`, `angular-node-view.spec.ts`, `EditorContentDirective`-Tests.

### R.4 Bewusst nicht geändert (mit Begründung)

- **E22** (`nodeHighlight` nicht registriert) bleibt „beibehalten“: Aktivieren ändert die Optik (Hervorhebung), Z-12 verlangt „optisch 1:1“; als Kandidat für eine spätere Abnahme notiert, kein Blocker.
- **Collaboration-Cursor als CE-Abhängigkeit hinter Flag:** deckungsgleich mit D08 O-D08-07 und D16 (D4 „entfernt nur den Eintrag“); Aktivierung bleibt Auftraggeber-Entscheidung O-D10-01.
- **D10-ADR-15** (Rich/Document-Editor in I2) bleibt; die Gegenposition in D01/D08/D15 ist als Konflikt gemeldet (unten), nicht hier aufzulösen.

### R.5 Konflikte mit anderen Dokumenten (an den Orchestrator gemeldet)

1. D01 ADR-042/§1.3 und D08 §9 („Rich/Document-Editor I4“, „S5 (Lite-Teil) vor I2“) vs. D10-ADR-15 (Rich + Document read-only in I2, S5 vollständig vor I2); D15 Anhang B.8 taggt `editor-menus`/`editor-blocks`/`editor-config.spec.ts` mit I4. – **entschieden (17 ABG-114)** zugunsten D10-ADR-15 (Umsetzung in 01/08/15).
2. ~~D09 §3.2.2: Importliste der Web-/Space-`styles.css` ohne `tiptap-core.css` (muss letzter, ungeschichteter Import sein, K-08).~~ – **erledigt (17 ABG-115):** 09 §3.2.2 und §5.1-Snippet führen `tiptap-core.css` als letzten Import außerhalb jeder `@layer`.
3. ~~D09 §3.1: `PRP/icons/` enthält `svg-icon.component.ts` neben den Daten; der Editor-Kern braucht einen reinen Daten-Einstieg (K-14). D09-Lint `no-component-styles` deckt `libs/shared/editor/**`, `libs/space/editor/**` nicht ab.~~ – **erledigt (17 ABG-116):** `PRP/components/svg-icon/`, Regel `icons-data-only`, `no-component-styles` erweitert (09 §3.1, §3.3).
4. ~~D09 Katalog: W-031 ohne Editor-Menü-Zustände (I2), W-046 ohne `table-column-dropdown`, `image-toolbar`, `callout-picker`, `code-hover`.~~ – **erledigt (17 ABG-117):** 09 §4.14 W-031/W-046 ergänzt.
5. ~~D16 D9-Zeile nennt `FE/libs/shared/editor` (`extensions/<block>/`) – D10 legt `FE/libs/shared/editor/packages/<paket>/{core,ui}` fest (keine CE-Datei wird geändert).~~ – **erledigt (17 ABG-118):** 16 D9-Zeile angeglichen.
6. ~~D07 §7.5 erzeugt vier Schema-Goldens inkl. `server.schema.json` (von §3.12 gelesen), AK-07-20 nennt nur Rich/Document/Title – Bedeutung von `server` vs. `rich` ungeklärt.~~ – **erledigt (17 ABG-119):** Server-Goldens `{rich,document,title}.schema.json` (D07), kein `server.schema.json`; Browser-Goldens `browser/{rich,lite,document,collaborative,title}` (D10); die Mark-Rangfolge liest D07 aus `rich`/`document`.
7. ~~D01 §8.2 (Pins „2.22.3 (Rest)“, `emojibase-data`, `jsx-dom-cjs`) – bereits in §9 als Rückmeldung geführt, weiterhin offen.~~ – **erledigt (17 ABG-120):** 01 §8.2/ADR-042 mit Lockfile-Pins nach §3.2.1, `emojibase-data` 15.3.2 in einer Zeile, `jsx-dom-cjs` nicht enthalten.

## Abgleich-Protokoll (Dokument 17)

Umsetzung der verbindlichen Entscheidungen aus `17-abgleich-dokumentuebergreifend.md` **Teil 2** (ABG-101 … ABG-149) bzw. `_data/17-abgleich-teil2.json` (Stand 23.10.2026), soweit ihre `targets` dieses Dokument nennen. Fundstellen per Volltextsuche (Tabellen, Code-Skelette, §8, §9, Anhang B, Review-Protokoll).

| ABG-ID | Thema | Umgesetzt in diesem Dokument |
|---|---|---|
| ABG-113 umgesetzt | `CollaborationSession.authorizedScope` | §3.15.1 Zeile `CollaborationSession`: Scope aus `provider.authorizedScope` (`"read-write"` \| `"readonly"` \| `undefined`, gesetzt in `authenticatedHandler(scope)` vor dem Ereignis `authenticated`, 07 §3.3.6), ⚠ entfernt; §5.8-Skelett Signal `authorizedScope`; O-D10-05 behält nur die DOM-Punkte (Hinweis auf den entfallenen Teil); §9 Zeile `07` |
| ABG-119 umgesetzt | Schema-Goldens | §3.2.3 (Absatz „Verbindlich nach ABG-119“: Server-Goldens `{rich,document,title}.schema.json`, kein `server.schema.json`; Spalten/Zeilen `server`/`server-document` bleiben Prüfer der D07-Goldens `rich`/`document`), R.5 Nr. 6 als erledigt markiert, §9 Zeile `07` (Klärungsbitte geschlossen) |
| ABG-121 umgesetzt | Verweis `EditorMentionService` | §3.11 Web-Hülle: „Vertrag D11 §3.5, Ort/Service D11 §3.12“ (`FE/libs/web/core/editor/editor-mention.service.ts`) |
| ABG-148 umgesetzt | Branding | D10-ADR-19 (Bestätigung „keine sichtbaren Plane-Texte in `ED0/`“ bleibt; Platzhalter/Tooltips der Hüllen über i18n nach BR-10; `BRAND-ED` derzeit leer; neue Texte über `BRAND.productName`), Anhang B Zeile „Branding (ADR-009B)“ (G-BRAND), §9 Zeilen `00` und `17` |
| Nachzug ABG-114 | Inkrement-Schnitt | R.5 Nr. 1 als „entschieden (17 ABG-114) zugunsten D10-ADR-15“ vermerkt; D10-ADR-15 und §1.3 waren bereits angeglichen (Umsetzung in 01/08/15) |

**Branding-Durchgang (ADR-009B, ABG-148, BR-01 … BR-14):** Dieses Dokument legt für die Zielplattform keine nach außen sichtbaren Namen mit „Plane“ fest – die Editor-Texte aus `ED0/` enthalten keinen Produktnamen, Hüllen-Texte kommen aus den nach BR-10 ersetzten i18n-Dateien; unverändert bleiben nach BR-02 Verweise auf das Original (`ED0/…`, „Plane-Fork“, Lizenz-Header „Copyright Plane Software“), interne Bezeichner (`@plane/*`, `planeUiPort`, Trusted-Types-Richtlinie `plane-editor`, `Plane.Documents`) und der MIME-Typ `text/plane-editor-html` (Beschreibungen in §3.19/AK-D10-09 nennen das Ziel neutral „Editor-HTML“).
