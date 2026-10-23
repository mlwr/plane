# -*- coding: utf-8 -*-
"""Arbeitspakete I4–I7 (siehe wp_spec.py)."""
from wp_spec import W, rng

# =====================================================================================
# I4 – Pages & Realtime
# =====================================================================================
M3 = "WP-I3-999"

W("WP-I4-101", "Funk.Documents Teil B: Yjs ⇄ ProseMirror, YjsUpdateWriter, Document-Variante, Markdown", "D", "L", True,
  [], ["WP-I2-999", "WP-I0-901", "WP-I0-902"],
  "Yjs-Abbildung (Port `y-prosemirror` 1.3.7) mit `YjsUpdateWriter`, Typ-Rückwandlung beim Lesen, Document-Variante des Schemas sowie `HtmlToMarkdownConverter` und `MarkdownRenderer`.",
  be=["`src/documents/Funk.Documents/Yjs/`, `Markdown/`", "`tests/Funk.Documents.Tests/Golden/Yjs/`"],
  arch=["07 §3.12.5, §3.12.6, §3.14, §5.8", "15 §3.7 (G-DOC Yjs, G-MD)", "17 Z-102"],
  ak=["G-DOC (Yjs-Teil) und G-MD grün; Browser-Roundtrip Yjs (AK-15-14)."])

W("WP-I4-201", "Erweiterungspunkte D1/D2: Pages ohne Projektpflicht, project_pages, parent_id, IPageHierarchy(+Queries), IPageAccessExtension, PAGE_*-Tokens", "X", "S", False,
  [], ["WP-I2-999"],
  "`pages.workspace_id` mit Projektzuordnung über `project_pages`, `pages.parent_id` (CE immer `null`), `IPageHierarchy` und `IPageHierarchyQueries` (E-23, CE flach/`[]`), `IPageAccessExtension` (Default `false`) und die zentrale Prüfstelle `IPageAccessPolicy` mit der CE-Regel aus 05 §3.13.5 (öffentlich/privat, Eigentümer, Gastregel, DELETE nur Admin), die REST (WP-I4-002) und Kollaboration (WP-I4-006) gemeinsam nutzen; Frontend `PAGE_STORES`, `PAGE_TREE`, `PAGE_FLAGS`, `PAGE_PANE_EXTENSIONS`. Vorlauf-Paket des Dokument-/Realtime-Tracks (plan/01 L-8): registriert weder Route noch Screen.",
  be=["`src/modules/Pages/Funk.Pages.Contracts/Hierarchy/`",
      "`src/data/Funk.Data/Entities/Pages/`",
      "`src/modules/Pages/Funk.Pages.Contracts/Access/IPageAccessPolicy.cs`, `src/modules/Pages/Funk.Pages/Access/ProjectPageAccessPolicy.cs`"], fe=["`frontend/libs/web/extensions/src/pages.ts`"],
  arch=["16 §5.13, §3.3.0 E-23",
      "01 §1.4 Zeilen D1, D2",
      "03 §3.4.10",
      "05 §3.13.5 (Page-Zugriffsregel)",
      "07 §3.5 (`ICollaborationDocumentType.AuthorizeAsync`), 17 ABG-107"],
  ep="01 §1.4 D1/D2; 16 §3.3.0 E-23; 16 §4.6 (Träger CE-PAGE-001/-003/-004/-006/-007)",
  ak=["Contract-Goldens der Page-Payloads unverändert; Fake-Hierarchie liefert Kinder, die im `PAGE_TREE` erscheinen (Typ X).",
      "`IPageAccessPolicy` ist die einzige Prüfstelle für Page-Zugriff: Architekturtest – kein Endpunkt und kein `ICollaborationDocumentType` prüft `pages.access`/`owned_by_id` selbst; L3-Matrix (öffentlich/privat × Eigentümer/Admin/Member/Guest mit und ohne `guest_view_all_features`) = Original-Verhalten aus 05 §3.13.5."],
  tests=["16 §7.2: `PageHierarchyDefaultsTests`, `PageAccessExtensionTests` (`Funk.Pages.Tests`)."])

W("WP-I4-202", "Erweiterungspunkte Kollaboration: ICollaborationDocumentType, affectedPages, EDITOR_BLOCKS, EDITOR_MENTION_TYPES", "X", "S", False,
  [], ["WP-I2-999", "WP-I4-101", "WP-I4-201"],
  "Registry der Hocuspocus-`documentType`-Werte (E-10, CE: `ProjectPageDocumentType` = `project_page`), server-seitig erzeugbares Realtime-Event `affectedPages`, Editor-Tokens `EDITOR_BLOCKS` und `EDITOR_MENTION_TYPES`.",
  be=["`src/modules/Collaboration/Funk.Collaboration.Contracts/ICollaborationDocumentType.cs`"], fe=["`frontend/libs/shared/editor/extensibility`"],
  arch=["07 §5.2, §5.3, §3.7.2", "10 §5.10, §6.2", "16 §3.3.0 E-10"],
  ep="16 §3.3.0 E-10; 16 §4.6 (Träger CE-RT-001, CE-RT-004, CE-RT-005)",
  ak=["Fake-Dokumenttyp wird über das Protokoll geladen/gespeichert ohne CE-Änderung; Fake-Block erscheint im Slash-Menü (Typ X).",
      "AK-16-15: Hocuspocus-Verbindung mit `documentType=fake_page` und registriertem `FakeCollaborationDocumentType` synchronisiert; ohne Registrierung Original-Fehler „Invalid document type …“."],
  tests=["16 §7.2: `CollaborationDocumentTypeRegistryTests` (`Funk.Collaboration.Tests`), `DocumentSchemaRegistryTests` (Yjs-Teil, `Funk.Documents.Tests`)."])

W("WP-I4-006", "Realtime-Kollaborationsserver: Protokoll, Dokument-Lebenszyklus, Persistenz, Titel-Sync, Fehler/Force-Close, Konvertierung", "D", "L", False,
  ["CE-RT-001", "CE-RT-005", "CE-RT-006", "CE-RT-008"], ["WP-I4-101", "WP-I4-202", "WP-I0-107", "WP-I0-901", "WP-I4-201"],
  "`Funk.Collaboration` (+ `.Protocol`) nach dem Ergebnis von S1: Wire-Protokoll, Zustandsautomaten, Auth über Session-Ticket, Laden/Migration HTML→Binary, Merge-on-Store mit 10-s-Debounce, Titel-Sync, Stateless-Ereignisse, Fehler-Broadcast, Force-Close, Admin-Kanal, Graceful Shutdown und `/live/convert-document/`.",
  be=["`src/modules/Collaboration/Funk.Collaboration`, `.Protocol`, `.Contracts`", "`src/modules/Pages/Funk.Pages/Documents/IPageDocumentStore` (Merge-on-Store)", "`tests/Funk.Collaboration.Tests`"],
  arch=["07 §3.1–§3.9, §3.11, §5.1–§5.6, §7.3", "05 §3.11", "17 Z-101"],
  ak=["Protokollfälle P-01…P-30 mit dem Original-Provider im Browser grün (`ProviderConformanceTests`).",
      "LT-16…LT-18 im Zielbereich.",
      "Die Verbindungsprüfung je Dokument läuft über `ICollaborationDocumentType.AuthorizeAsync` → `IPageAccessPolicy` (WP-I4-201); Token-Mismatch → nur `PermissionDenied`, Rechteentzug in der Sitzung → `PermissionDenied` + Close 4403, `read-write` → `readonly` → 4205, Upgrade ohne Session-Cookie → 403 (17 ABG-107; je Fall ein `ProviderConformanceTests`-Schritt)."])

W("WP-I4-007", "Client-Kollaboration: Echtzeit-Editor-Bindung, Offline-Cache, REST-Fallback, Seitenereignisse (ED-4-Kern)", "D", "L", False,
  ["CE-RT-002", "CE-RT-003", "CE-RT-004"], ["WP-I4-006", "WP-I2-024", "WP-I4-002"],
  "`CollaborationSession` mit `HocuspocusProvider` 2.15.2, IndexedDB-Offline-Cache, Sync-Status, Stateless-Kanal, REST-Fallback-Speicherung (`setProviderDocument`, `getDocument`) und Echtzeit-Seitenereignisse; `collaboration-cursor` aktiv, sobald S1-Awareness grün ist (Z-109).",
  fe=["`frontend/libs/shared/editor/collaboration`"], be=["`src/modules/Pages/Funk.Pages` (REST-Fallback)"],
  arch=["10 §1.5 (ED-4), §3.15, §5.8", "07 §3.7, §3.11", "08 §3.12", "17 Z-109"],
  ak=["AK-D10-14…-18 grün; Abweichung `collaboration-cursor` als FE-ED-01 in `ui-deviations.yaml` dokumentiert und vom Auftraggeber abgenommen."],
  note="Kein Vorlauf-Paket: Der REST-Fallback nutzt die Page-Endpunkte und Zugriffsregeln aus WP-I4-001/-002; die Client-Bindung kann gegen den Vorlauf-Server (WP-I4-006) vorentwickelt, aber erst nach WP-I4-002 gemergt werden.")

W("WP-I4-008", "Horizontale Skalierung des Realtime-Servers (Valkey-Backplane, PostgreSQL-Signale)", "B", "M", True,
  ["CE-RT-007"], ["WP-I4-006"],
  "Valkey-Backplane (`BackplaneEnvelope`), In-Memory-Backplane für Einzelknoten/AIO, PostgreSQL-Signale (`CollaborationSignalListener`), Multi-Instanz-Setup (2 × `realtime`) im Profil `test`.",
  be=["`src/modules/Collaboration/Funk.Collaboration/Backplane/`"], arch=["07 §3.10, §5.9", "14 §3.1.2 Zeile I4"],
  ak=["Zwei Realtime-Instanzen konvergieren (Konvergenztest), LT-19/LT-20 im Zielbereich; Speicherdruck-Watchdog nach LT-20 entschieden (O-07-05)."])

W("WP-I4-001", "Page-Liste mit Tabs, Suche/Filter/Sortierung, Anlage, Favoriten", "V", "M", False,
  ["CE-PAGE-001", "CE-PAGE-002", "CE-PAGE-003", "CE-PAGE-010"], [M3, "WP-I4-201"],
  "Page-Liste (öffentlich, privat, archiviert), Suche, Filter, Sortierung, Page anlegen und favorisieren.",
  be=["`src/modules/Pages/Funk.Pages`, `Funk.Pages.Contracts`", "`tests/modules/Funk.Pages.Tests`"], fe=["`frontend/libs/web/pages`"],
  arch=["04 §4.10", "03 §3.4.10"],
  ak=["Tabs Public, Private, Archived (Query `type`) mit den Root-Pages des Projekts (eigene und öffentliche, Gast-Filter über `IPageAccessPolicy`), Favoriten zuerst; `summary` liefert die Zähler public/private/archived wie das Original-Golden.",
      "„Add page“ legt mit genau einem POST eine leere Page an und öffnet sie (E2E); Suche, Filter (Favorites, Created date, Created by) und Sortierung wie Original; Favoriten über `FAVORITE_ENTITY_RENDERERS` (Typ `page`)."])

W("WP-I4-002", "Page-Aktionen: Daten/Detail, sperren, Zugriff, archivieren, löschen, duplizieren, Referenzprotokoll", "V", "L", True,
  ["CE-PAGE-004", "CE-PAGE-005", "CE-PAGE-006", "CE-PAGE-007", "CE-PAGE-008", "CE-PAGE-009", "CE-PAGE-012"], ["WP-I4-001", "WP-I4-101"],
  "Page-Detail, Sperren/Entsperren, Zugriff öffentlich/privat (Page-Zugriffsregel 05 §3.13.5), Archivieren/Wiederherstellen, Löschen, Duplizieren mit Asset-Umschreibung und PageLog (synchron über `PageReferenceIndexer`).",
  be=["`src/modules/Pages/Funk.Pages`"], fe=["`frontend/libs/web/pages`"],
  arch=["04 §4.10", "05 §3.13.5", "07 §3.11", "06 D06-ADR-02 (PageLog)", "17 ABG-108"],
  ak=["Alle Page-Endpunkte prüfen den Zugriff über `IPageAccessPolicy` (WP-I4-201, 05 §3.13.5): private Pages nur für den Eigentümer, Gastregel, DELETE nur Admin (Permission-Matrix inkl. Fake-`IPageAccessExtension`).",
      "Lock/Unlock nur Owner oder Admin; Archivieren/Wiederherstellen rekursiv inkl. Nachkommen; Löschen nur archivierter Pages, Kinder werden abgehängt (L3, Golden).",
      "Duplizieren erzeugt „(Copy)“, kopiert eingebettete Bilder in neue Assets, schreibt das HTML um (Golden: keine Asset-ID der Quelle im Ergebnis) und erzeugt JSON/Binary in-process über `Funk.Documents` (kein Live-Server-Aufruf); `PageReferenceIndexer` indiziert `mention-component`/`image-component` synchron je Speichern (L3)."])

W("WP-I4-003", "Page-Export als PDF und Markdown", "D", "M", True,
  ["CE-PAGE-011"], ["WP-I4-002", "WP-I0-903", "WP-I4-101"],
  "`Funk.Documents.Pdf` mit den Stilprofilen `live` und `web` nach dem Ergebnis von S3, Endpunkt `POST /live/pdf-export/`, Markdown-Export.",
  be=["`src/documents/Funk.Documents.Pdf`", "`tests/Funk.Documents.Pdf.Tests`"], fe=["`frontend/libs/web/pages` (export)"],
  arch=["07 §3.15, §5.10", "17 Z-103, Z-116"],
  ak=["G-PDF, G-PDF-web und G-MD grün; Web-PDF-Kursiv wie Original (Z-116, bis Auftraggeber anders entscheidet)."])

W("WP-I4-004", "Kollaborativer Page-Editor (Seite, Toolbar, Kopf, Outline, Info-, Assets-Panel, Anzeigeoptionen) – ED-4-Hüllen", "V", "L", False,
  ["CE-PAGE-013", "CE-PAGE-014", "CE-PAGE-015", "CE-PAGE-016", "CE-PAGE-017", "CE-PAGE-018", "CE-PAGE-020"], ["WP-I4-007", "WP-I4-002", "WP-I4-005"],
  "Page-Seite mit `PlEdCollaborativeDocumentEditor`, `PlEdTitleEditor`, Navigation Titel↔Inhalt, Toolbar, Kopf, Outline, Info-Panel, Assets-Panel und Anzeigeoptionen.",
  fe=["`frontend/libs/web/pages`", "`frontend/libs/web/core/editor` (Page-Hüllen)"], arch=["10 §1.5 (ED-4), §3.16, §3.21", "08 §4.1"],
  ak=["Titel-Editor mit Platzhalter „Untitled“ und Tastaturnavigation Titel↔Inhalt wie Original (Playwright); das Inhaltslimit-Banner erscheint bei Überschreitung des Original-Limits.",
      "Outline listet alle Überschriften in Dokumentreihenfolge, Klick scrollt dorthin; das Info-Panel zählt Words, Characters, Paragraphs und Read time für 5 Referenzdokumente identisch zum Original und zeigt die Versionsliste aus WP-I4-005; das Assets-Panel listet alle eingebetteten Bilder.",
      "Anzeigeoptionen Full width, Sticky toolbar, Copy markdown und Version history persistieren wie Original; Visual der Editor-Seite ≤ 0,5 % (S5-Schwelle)."])

W("WP-I4-005", "Page-Versionshistorie", "V", "M", True,
  ["CE-PAGE-019"], ["WP-I4-006", "WP-I4-002"],
  "Versionierung beim Speichern (Fix CE-PAGE-019 laut 07), Versionsliste und -anzeige mit Document-Editor read-only, Versions-Cleanup.",
  be=["`src/modules/Pages/Funk.Pages` (Versions)"], fe=["`frontend/libs/web/pages` (version-history)"], arch=["07 §3.6.4, §3.20", "06 §1.3 Zeile I4"],
  ak=["Versionen entstehen beim Speichern in 600-s-Merge-Fenstern je Besitzer, höchstens 20 je Page (Korrektur des Original-Fehlers, dass nie Versionen entstehen; Eintrag laut 07 §3.20): `FixedClock` – 3 Speicherungen in 10 min → 1 Version, eine weitere nach 11 min → 2 Versionen, die 21. Version verdrängt die älteste.",
      "Versionsliste und read-only-Anzeige über den Document-Editor (ED-3); „Wiederherstellen“ ersetzt den Editorinhalt und erzeugt eine neue Version (E2E); `GET …/versions/` und `…/versions/{pk}/` entsprechen dem Ziel-Golden (`golden_source: target`)."])

W("WP-I4-009", "Demo-Inhalte bei Workspace-Anlage (vollständiger Seed inkl. Cycles, Module, Views, Pages)", "B", "M", True,
  ["CE-WS-002"], ["WP-I4-002"],
  "`WorkspaceDemoSeedJob` legt die acht Original-Seed-Dateien über die Contracts-Commands der Eigentümer-Module an (Bot-Benutzer, Projekt, States, Labels, Cycles, Module, Work Items, View, Pages), lädt die gebündelten Bilder in den Objektspeicher und ersetzt Branding.",
  be=["`src/modules/Workspaces/Funk.Workspaces/Application/Jobs/WorkspaceDemoSeedJob.cs`", "`src/data/Funk.Data/Seeds/Demo/`"],
  arch=["03 §3.14.3", "06 §3.18.1", "17 Z-114 (Seed-Bilder)"],
  note="Abweichung von 15 Anhang B (Inkrement I0/I1): Der Seed braucht Cycles, Module, Views und Pages; er wird deshalb in I4 vollständig abgenommen (plan/04 OP-PLAN-03).",
  ak=["`WorkspaceDemoSeedTests` vergleicht gegen das gebrandete Golden und prüft `NOT ILIKE '%plane%'` auf allen Seed-Textspalten."])

W("WP-I4-999", "Abnahme I4 – Pages & Realtime (G5)", "A", "S", False,
  [], ["WP-I4-%03d" % i for i in range(1, 10)] + ["WP-I4-101", "WP-I4-201", "WP-I4-202"],
  "Inkrement-Abnahme I4 nach G5 und Meilenstein M4.",
  arch=["plan/01-roadmap-ce.md §4 (M4)", "15 §3.16 Zeile I4"],
  ak=["Alle Abnahmekriterien M4 erfüllt; `docs/acceptance/I4.md` generiert.",
      "AK-16-02 (Zwischenstand I4): Contract-Replay und Visual-Suite der I0–I4-Screens mit CE-Defaults = ohne Andockstellen-Registrierung (0 Abweichungen)."], tests=["G5 `--inc I4`."])

# =====================================================================================
# I5 – Überblick
# =====================================================================================
M4 = "WP-I4-999"

W("WP-I5-201", "Erweiterungspunkt G1/B6: ISearchProvider, IIndexingPipeline, search_documents, vector, NullEmbeddingGenerator, IIndexDocumentEnricher", "X", "M", False,
  [], [M4],
  "Such-Abstraktion `ISearchProvider` (`PostgresSearchProvider`), Indexierungs-Pipeline als `IEventConsumer` auf der CE-Queue `indexing`, Tabelle `search_documents` (`tsvector`, Surrogat-PK `id`), Extension `vector` aktiv, `IEmbeddingGenerator<string, Embedding<float>>` mit `NullEmbeddingGenerator`, `IIndexDocumentEnricher` (E-24), `SearchVisibilityFilter`.",
  be=["`src/platform/Funk.Platform.Search`", "`src/platform/Funk.Platform.Ai`", "`src/modules/Search/Funk.Search`"],
  arch=["11 §3.3, §3.10, §5.1, §5.6, §6", "16 §5.14, §3.2.7, §3.3.0 E-24", "17 ABG-122, ABG-125"],
  ep="01 §1.4 G1/B6; 16 §3.3.0 E-24; 16 §4.6 (Träger CE-SRCH-001…003)",
  ak=["Index-Konsistenz-Job `indexing.reconcile` repariert absichtlich gelöschte Index-Zeilen; Fake-Enricher ergänzt Felder ohne CE-Änderung (Typ X)."],
  tests=["16 §7.2: `IndexingPipelineConsumerTests`, `NullEmbeddingGeneratorTests`, `IndexEnricherTests` (`Funk.Search.Tests`, `Funk.Platform.Tests`)."])

W("WP-I5-202", "Erweiterungspunkte UI I5: HOME_WIDGETS, POWER_K_COMMANDS, SEARCH_RESULT_RENDERERS, erste Nutzung LIVE_EVENT_HANDLERS", "X", "S", False,
  [], [M4],
  "Frontend-Registries für Home-Widgets (E-14, CE-Widgets aus `apps/web/core/components/home/widgets`), Power-K-Befehle und Such-Ergebnis-Renderer; erste Handler für `LIVE_EVENT_HANDLERS` (Notification-Zähler).",
  fe=["`frontend/libs/web/extensions/src/{home,power-k,search}.ts`", "`frontend/libs/web/notifications/src/live/`"],
  arch=["08 §6.4", "16 §1.4 Zeile I5", "06 §5.12"],
  ep="16 §1.4 Zeile I5; 16 §4.6 (Träger CE-HOME-001/-002, CE-NOTIF-001, CE-SRCH-004)",
  ak=["Fake-Widget, Fake-Befehl und Fake-Renderer erscheinen ohne CE-Änderung (Typ X).",
      "AK-16-16 für `HOME_WIDGETS` (CE-Widgets aus `WEB/components/home/widgets`; Fake-Widget erscheint in „Manage widgets“)."])

W("WP-I5-001", "Workspace-Analytics: Tabs, Kennzahlen, Project Insights, Active Projects, Created vs Resolved, Customized Insights, Insight-Tabelle mit CSV", "V", "L", True,
  rng("CE-ANA", 1, 7), [M4, "WP-I3-101"],
  "Analytics-Seite mit allen CE-Tabs und Diagrammen, Insight-Tabelle mit CSV-Export.",
  be=["`src/modules/Analytics/Funk.Analytics`", "`tests/modules/Funk.Analytics.Tests`"], fe=["`frontend/libs/web/analytics`"],
  arch=["04 §4.14", "03 §3.4.13", "09 §3.12"],
  ak=["Kennzahlen, Project Insights (Radar), Active Projects (grün > 50 %, sonst rot), Created vs Resolved und Customized Insights liefern auf dem Parity-Seed für „letzte 7 Tage“, einen Custom-Bereich und zwei Projektauswahlen dieselben Zahlen wie das Original-Golden.",
      "Charts (Radar, Area, Bar) Visual ≤ 0,5 % (S6-Schwelle); Insight-Tabelle mit Suche in der ersten Spalte; der clientseitige CSV-Export ist byte-gleich zum Original-Export derselben Daten."])

W("WP-I5-002", "Analytics-Panel (Projekt, Cycle, Modul), Legacy-Analytics, gespeicherte Analytics-Views, Export per E-Mail", "V", "M", True,
  ["CE-ANA-008", "CE-ANA-009"], ["WP-I5-001", "WP-I1-102"],
  "Analytics-Panel in Projekt-, Cycle- und Modul-Kontexten, Legacy-Analytics, gespeicherte Analytics-Views und Export per E-Mail (Template M11).",
  be=["`src/modules/Analytics/Funk.Analytics`"], fe=["`frontend/libs/web/analytics`"], arch=["04 §4.14", "06 §3.15.2"],
  ak=["Das Analytics-Panel in Projekt-, Cycle- und Modul-Kontext (auch im Vollbild) zeigt den gefilterten Work-Items-Tab; Tagesreihe für Cycle/Modul, Monatsreihe für Projekt wie Original-Golden; der Button „Analytics“ in den Layout-Köpfen erscheint mit diesem Paket.",
      "Legacy-Analytics (x/y-Achsen, Segment), gespeicherte Analytics-Views (`query_dict`) und Export per E-Mail (Template M11 mit CSV-Anhang, G-MAIL) entsprechen dem Original (Contract-Golden, nur API)."])

W("WP-I5-003", "Workspace-Home: Widgets, Widget-Verwaltung, Quickstart, Quick links, Recents, Produkt-Tour, Legacy-Dashboard", "V", "L", True,
  rng("CE-HOME", 1, 7), [M4, "WP-I5-202"],
  "Home mit Widgets über `HOME_WIDGETS`, Widget-Verwaltung, Quickstart-Guide, Quick links, Recents (Recent-Visits-Job), Produkt-Tour und Legacy-Dashboard/Aktivitätsgraphen (nur API).",
  be=["`src/modules/Home/Funk.Home`", "`tests/modules/Funk.Home.Tests`"], fe=["`frontend/libs/web/home`"],
  arch=["04 §4.15", "03 §3.4.12", "06 O-D06-09"],
  ak=["`HOME_WIDGETS` enthält die CE-Widgets quick_links, recents, my_stickies; „Manage widgets“ schaltet und sortiert per Drag&Drop; `WorkspaceHomePreference` wird beim ersten Abruf lazy angelegt (Golden).",
      "Recents: Besuche von Projekten, Work Items, Cycles, Modulen, Views und Pages werden per Job erfasst, höchstens 20 je Nutzer und Workspace (L3: 25 Besuche → 20 Einträge, die ältesten verdrängt); Filter All/Work items/Pages/Projects.",
      "Quick links: `http://` wird ergänzt, ungültige URL und Duplikat je Owner → Original-Fehler; Quickstart-Fortschritt nur in `localStorage` (`quickstart-guide-{ws}`); Produkt-Tour mit fünf Schritten und `tour-completed`; Legacy-Dashboard-Endpunkte wie in 04 (`decision`) entschieden.",
      "Texte mit „Plane“ erscheinen als „funk.“ (ADR-009B, z. B. „Make funk. yours“, Widget „New at funk.“); das Changelog-Widget zeigt nur eine konfigurierte Quelle und entfällt ohne Ziel (wie WP-I1-003); G-BRAND grün."])

W("WP-I5-004", "Stickies: Widget, Seite, Bearbeitung (ED-5)", "V", "M", True,
  rng("CE-HOME", 8, 10), ["WP-I5-003"],
  "Stickies-Widget, Stickies-Seite mit Masonry und Sticky-Editor (Lite + Sticky-Toolbar, Farbpalette).",
  be=["`src/modules/Home/Funk.Home` (Stickies)"], fe=["`frontend/libs/web/stickies`", "`frontend/libs/web/core/editor` (sticky-editor)"],
  arch=["04 §4.15", "10 §1.5 (ED-5)"],
  ak=["Der Sticky-Editor speichert per Autosave nach 500 ms (Request-Zählung im E2E); das Backend sanitisiert HTML und prüft das Binary (G-SANITIZE-Fälle).",
      "Stickies-Seite: Suche über `description_stripped`, Masonry 2–6 Spalten je Breakpoint, Infinite Scroll (Frontend 30 je Seite, Backend-Default 20), Drag&Drop-Sortierung, neue Notizen oben; nur der Owner hat Zugriff (fremder Zugriff → Original-Fehler)."])

W("WP-I5-005", "Benachrichtigungen erzeugen: In-App, Mentions, automatisches Abonnieren, Zähler-Push", "B", "M", False,
  rng("CE-NOTIF", 1, 3), [M4, "WP-I5-202", "WP-I0-207"],
  "`ActivityNotificationConsumer` (Queue `notifications`) aus `funk.work_item_activity.recorded.v1` mit Original-Algorithmus, Mention-Benachrichtigungen, Auto-Subscribe; `funk.notification.created.v1` → `RealtimeFanOutConsumer` → Zähler-Push über SignalR.",
  be=["`src/modules/Notifications/Funk.Notifications`", "`src/modules/RealtimeEvents/Funk.RealtimeEvents/Consumers/RealtimeFanOutConsumer.cs`"],
  arch=["06 §3.10, §3.12, §5.7, D06-ADR-10, -12", "07 §3.16.4", "17 ABG-106"],
  ak=["`LiveEventLatencyTests`: Zähler-Push < 2 s mit und ohne Valkey (Z-104); Notification-Daten (`data`-JSON) byte-gleich zum Original-Golden."])

W("WP-I5-006", "Inbox: Seite, Liste, Filter/Optionen, lesen/archivieren/snoozen, Detail", "V", "L", True,
  rng("CE-NOTIF", 4, 7), ["WP-I5-005"],
  "Inbox-Seite mit Benachrichtigungsliste, Filtern und Optionen, Lesen/Archivieren/Snoozen und Detail.",
  be=["`src/modules/Notifications/Funk.Notifications`"], fe=["`frontend/libs/web/notifications`"], arch=["04 §4.16", "03 §3.4.14"],
  ak=["Tabs All/Mentions mit Ungelesen-Zählern; das Badge in der Top-Navigation aktualisiert sich über `LIVE_EVENT_HANDLERS` < 2 s nach dem auslösenden Commit (`LiveEventLatencyTests`, mit und ohne Valkey).",
      "Optionen Show unread/archived/snoozed und Filter Assigned to me/Created by me/Subscribed by me liefern dieselben Listen wie das Original-Golden; „Mark all as read“ setzt `read_at` für genau die gefilterte Menge.",
      "Snooze 1 day, 3 days, 5 days, 1 week, 2 weeks, Custom (Datum + Uhrzeit) setzt `snoozed_till` wie Original; Klick auf eine Benachrichtigung markiert sie als gelesen und zeigt Work Item bzw. Intake-Inhalt im eingebetteten Peek."])

W("WP-I5-007", "E-Mail-Benachrichtigungen mit 5-Minuten-Bündelung und Einstellungen", "B", "M", True,
  ["CE-NOTIF-008", "CE-NOTIF-009"], ["WP-I5-005", "WP-I1-102"],
  "Cron `notifications.email_digest` (alle 5 min) gruppiert je (Empfänger, Work Item), Versand-Job mit genau den IDs der Gruppe, Template M12, Benachrichtigungseinstellungen.",
  be=["`src/modules/Notifications/Funk.Notifications`"], fe=["`frontend/libs/web/settings` (notifications)"], arch=["06 §3.11, D06-ADR-11"],
  ak=["Cron `notifications.email_digest` (alle 5 min, UTC) gruppiert `email_notification_logs` je (Empfänger, Work Item) und sendet genau eine Mail „issue-updates“ (M12) je Gruppe mit genau den IDs der Gruppe (L3 mit `FixedClock`; ein Doppellauf versendet nichts doppelt).",
      "Die Profil-Schalter property_change, state_change, issue_completed, comment, mention unterdrücken jeweils genau ihren Mail-Typ (5 L3-Fälle); M12 besteht G-MAIL in der nach OE-01 festgelegten Sprache."])

W("WP-I5-008", "Suche: Globale Suche, Entity-Suche für Mentions/Picker, Work-Item-Picker", "V", "M", True,
  rng("CE-SRCH", 1, 3), ["WP-I5-201"],
  "Endpunkte SR-01 (global), SR-03 (Entity) und SR-02 (Work-Item-Picker) mit `icontains`→`ILIKE`-Semantik, Trigramm-Indizes und Sichtbarkeitsprädikaten.",
  be=["`src/modules/Search/Funk.Search`", "`tests/modules/Funk.Search.Tests`"], fe=["`frontend/libs/web/core` (search services)"],
  arch=["11 §3.2, §3.4–§3.6, §3.8, §3.9, §5.3–§5.5", "04 §4.17"],
  ak=["SQL-Pläne ohne Seq-Scan bei Workspace-Filter (11 §3.9); 403 für Nicht-Mitglieder (O-D11-01, DEV-SRCH-011)."])

W("WP-I5-009", "Power-K Command Palette mit Navigations-, Erstell-, Kontext-, Account-/Preferences-/Hilfebefehlen und Shortcuts", "F", "L", True,
  rng("CE-SRCH", 4, 9), ["WP-I5-008", "WP-I5-202"],
  "Power-K (cmdk-DOM nachgebaut) mit allen CE-Befehlsgruppen über `POWER_K_COMMANDS` und Tastatur-Shortcuts.",
  fe=["`frontend/libs/web/power-k`"], arch=["08 §3.10", "11 §3.11", "09 §4.14"],
  note="Power-K zeigt bei Pages den Projekt-Identifier nicht an (Original-Defekt `project__identifiers`, O-D11-04) – optisch 1:1 belassen, Eintrag in `ui-deviations.yaml`.",
  ak=["Ctrl/⌘ K öffnet die Palette; DOM (Gruppen, Überschriften, Items mit Fokus-/Auswahl-/Disabled-Zustand) gleich zur cmdk-Struktur des Originals, Visual ≤ 0,2 %.",
      "Alle Befehle aus CE-SRCH-005 … -008 sind über `POWER_K_COMMANDS` registriert (Tabellentest Befehl → Ziel/Aktion gegen die Original-Befehlsliste); Kontextbefehle erscheinen nur im passenden Kontext (Work Item, Cycle, Module, Page); der Theme-Befehl nutzt die Theme-Auswahl aus WP-I1-018.",
      "Shortcut-Sequenzen (G+…) werden innerhalb von 1 000 ms erkannt und in Eingabefeldern ignoriert (Vitest mit Fake-Timern); „Keyboard shortcuts“ listet dieselben Kürzel wie das Original; der Identifier-Defekt bei Pages bleibt 1:1 (OE-10)."])

W("WP-I5-010", "Your work: Summary, Work-Item-Tabs, Activity, Profil-Sidebar", "V", "M", True,
  rng("CE-PROF", 8, 11), [M4],
  "Profilseiten „Your work“ mit Zusammenfassung, Work-Item-Tabs (Layout-Kontext Profil), Activity und Profil-Sidebar.",
  be=["`src/modules/Workspaces/Funk.Workspaces` (Member-Profile)"], fe=["`frontend/libs/web/profile`"], arch=["04 §4.3", "08 §4.1"],
  ak=["Summary-Kennzahlen (Created/Assigned/Subscribed), Workload je State-Gruppe und Charts nach Priorität/Zustand zählen nur für den Betrachter sichtbare Work Items (L3: ohne Projektzugang 0 für dieses Projekt; Golden).",
      "Work-Item-Tabs Assigned/Created/Subscribed in List/Kanban nur für Admin/Member; Activity paginiert mit „Load more“; „Download today's activity“ erzeugt eine CSV mit den Original-Spalten.",
      "Die Profil-Sidebar zeigt Zeitzone mit aktueller Uhrzeit und Projekt-Statistiken (Fertigstellungsgrad, Created/Assigned/Due/Completed) wie Original (Visual)."])

W("WP-I5-999", "Abnahme I5 – Überblick (G5)", "A", "S", False,
  [], ["WP-I5-%03d" % i for i in range(1, 11)] + ["WP-I5-201", "WP-I5-202"],
  "Inkrement-Abnahme I5 nach G5 und Meilenstein M5.",
  arch=["plan/01-roadmap-ce.md §4 (M5)", "15 §3.16 Zeile I5"],
  ak=["Alle Abnahmekriterien M5 erfüllt; `docs/acceptance/I5.md` generiert."], tests=["G5 `--inc I5`."])

# =====================================================================================
# I6 – Außenwirkung & Administration
# =====================================================================================
M5 = "WP-I5-999"

W("WP-I6-201", "Erweiterungspunkte Public API: IV1PayloadExtension, IV1FilterParameterBinding, erweiterbare OpenAPI-Gruppen", "X", "S", False,
  [], [M5],
  "`IV1PayloadExtension` (Typ-/Property-Felder in v1-Antworten, E-07 Teil v1; `IExpandProvider` liegt seit WP-I2-205 vor und wird für v1-`expand` mitbenutzt), `IV1FilterParameterBinding` (E-19, ohne Bindung Original-400 für `pql`/`filters`), erweiterbare OpenAPI-Dokumentgruppen.",
  be=["`src/modules/PublicApi/Funk.PublicApi/Extensions/`", "`src/modules/WorkItems/Funk.WorkItems.Contracts/Query/IV1FilterParameterBinding.cs`"],
  arch=["04 §5.6", "16 §3.3.0 E-07/E-19"],
  ep="16 §3.3.0 E-07, E-19; 16 §4.6 (Träger CE-API-017, CE-API-019)",
  ak=["OpenAPI-Golden `v1.original.json` unverändert mit CE-Defaults; Fake-Payload-Extension ergänzt ein Feld ohne CE-Änderung (Typ X)."],
  tests=["16 §7.2: `V1PayloadExtensionTests`, `V1FilterParameterGuardTests` (Original-400-Körper für `pql`/`filters`) (`Funk.PublicApi.Tests`)."])

W("WP-I6-202", "Erweiterungspunkte IWebhookEventSource und IExportTypeProvider", "X", "S", False,
  [], [M5],
  "Zusätzliche Webhook-Ereignisarten über `IWebhookEventSource` (E-08, CE: `project`, `issue`, `module`, `cycle`, `issue_comment`) und Exporttypen über `IExportTypeProvider` (E-16).",
  be=["`src/modules/Webhooks/Funk.Webhooks.Contracts`", "`src/modules/Exports/Funk.Exports.Contracts`"],
  arch=["06 §5.9", "16 §3.3.0 E-08/E-16"],
  ep="16 §3.3.0 E-08, E-16; 16 §4.6 (Träger CE-WH-001/-007/-008, CE-EXP-001/-002)",
  ak=["Fake-Quelle erzeugt eine neue Webhook-Ereignisart, Fake-Exporttyp erscheint in der Export-Auswahl (Typ X)."],
  tests=["16 §7.2: `WebhookEventSourceTests` (`Funk.Webhooks.Tests`), `ExportTypeProviderTests` (`Funk.Exports.Tests`)."])

W("WP-I6-203", "Erweiterungspunkte Space/Admin: SPACE_ROUTE_EXTENSIONS, EDITOR_EXTENSIONS (Space), ADMIN-Registries mit CE-Inhalt", "X", "S", False,
  [], [M5],
  "Space-Routen-Registry, Editor-Erweiterungen im Space-Scope (S44) und Befüllung der Admin-Registries (`ADMIN_SETTINGS_PAGES`, `ADMIN_ROUTE_EXTENSIONS`, `ADMIN_HEADER_SEGMENT_LABELS`) mit allen CE-Seiten.",
  fe=["`frontend/libs/space/extensions`", "`frontend/libs/admin/extensions`"], arch=["08 §6.4", "16 §1.4 Zeile I6", "17 ABG-023"],
  ep="16 §1.4 Zeile I6; 16 §4.6 (Träger CE-SPACE-001/-018/-025, CE-INST-003/-025)",
  ak=["Fake-Space-Route und Fake-Admin-Seite erscheinen ohne CE-Änderung (Typ X)."])

W("WP-I6-001", "God Mode: Abmeldung, Fehleransicht, Dashboard-Shell, Header, Konto-Menü, Hilfe, Seite „Authentication“ (Keycloak), Unsaved-Dialog, Kopierfelder, 404", "V", "L", True,
  rng("CE-INST", 8, 16), [M5, "WP-I6-203"],
  "Vollständige Admin-Shell mit Sidebar, Breadcrumb-Header, Konto-Menü mit Theme-Umschaltung, Hilfe-Bereich, Dialog für ungespeicherte Änderungen, Kopierfeldern für funk.-URLs, Fehler- und 404-Seiten.",
  fe=["`frontend/apps/admin`", "`frontend/libs/admin/{core,common}`"], be=["`src/modules/Instance/Funk.Instance`"],
  arch=["08 §4.2", "05 §3.8", "09 §4.14"],
  ak=["Admin-Sidebar mit genau 6 Einträgen (General, Email, Authentication, Workspaces, Artificial intelligence, Images in funk.) aus `ADMIN_SETTINGS_PAGES`; 290/70 px, mobil Overlay mit Auto-Collapse ab 768 px, Zustand in `localStorage.god_mode_sidebar_collapsed` (Visual, Vitest).",
      "Die Seite „Authentication“ ist die `AuthenticationStatusPageComponent` (08 §4.2 R6, 05 §4.4): Karte „Keycloak“ (Issuer, Realm, Discovery-Status, Link zur Admin-Konsole), Schalter „Allow anyone to sign up even without an invite“ (`ENABLE_SIGNUP`) und die Kopierfelder (CE-INST-015) Redirect URI, Post-logout redirect URI, Back-channel logout URL; die Provider-Routen leiten auf `/god-mode/authentication/` um (`admin/routes.spec.ts`).",
      "Der Unsaved-Changes-Dialog (CE-INST-014) greift als `canDeactivate` + `beforeunload` an den God-Mode-Formularen mit geänderten Werten (08 §4.2); Statuskonflikt zu 05 (dort „entfällt“) siehe plan/04 N-P13.",
      "„Sign out“ löst den RP-Logout über `/auth/sign-out/?app=admin` aus und setzt Stores und Theme auf `system` zurück (E2E); Hilfe-Bereich mit „Redirect to funk.“ und Version `v{current_version}`, externe Links nur auf konfigurierte Ziele (G-BRAND, `no-external-urls`); 404 mit „Go to general settings“, Instanzfehler-Ansicht mit Retry (Visual)."])

W("WP-I6-002", "God Mode: Allgemeine Einstellungen, SMTP, Test-E-Mail, AI-Einstellungen, Bildbibliotheken", "V", "M", True,
  ["CE-INST-017", "CE-INST-018", "CE-INST-019", "CE-INST-025", "CE-INST-026"], ["WP-I6-001", "WP-I1-102"],
  "Instanz-Einstellungen General, SMTP mit Test-E-Mail, AI-Einstellungen (OpenAI-kompatibler Endpunkt, lokal betreibbar) und Unsplash; Secrets maskiert (`MaskInstanceSecrets = true`).",
  fe=["`frontend/libs/admin/instance`"], be=["`src/modules/Instance/Funk.Instance`"],
  arch=["05 §4.4", "11 §3.13, §3.17", "04 §4.2", "17 Z-112"],
  ak=["Instanzname per `PATCH /api/instances/`; Admin-E-Mail (erster Spiegel-Admin) und Instance-ID read-only; der Telemetrie-Schalter wird gespeichert, ein Export nach außen findet nicht statt (Netzwerk-Allowlist-Test, ADR-004).",
      "SMTP: Ausschalten leert die Konfiguration per `DELETE …/disable-email-feature/`, Speichern setzt `ENABLE_SMTP=1`; das Passwort ist verschlüsselt und in jeder API-Antwort maskiert (`MaskInstanceSecrets = true`, Z-112; L3 prüft, dass kein Klartext ausgeliefert wird).",
      "Test-E-Mail-Dialog in 3 Schritten; `POST /api/instances/email-credentials-check/` liefert die differenzierten Original-Fehlermeldungen für Verbindungs-, Anmelde- und TLS-Fehler (Mailpit-/Fehler-Fälle).",
      "AI-Einstellungen akzeptieren neben OpenAI einen OpenAI-kompatiblen Basis-Endpunkt (lokal betreibbar, ADR-004); `has_llm_configured` wird daraus berechnet (Golden); der Unsplash Access Key ist Pflichtfeld."])

W("WP-I6-003", "God Mode: Workspace-Liste, Workspace-Anlage sperren, Workspace anlegen, Willkommens-Popup", "V", "M", True,
  rng("CE-INST", 27, 30), ["WP-I6-001"],
  "Workspace-Verwaltung der Instanz.",
  fe=["`frontend/libs/admin/workspace`"], be=["`src/modules/Instance/Funk.Instance`", "`src/modules/Workspaces/Funk.Workspaces.Contracts`"], arch=["04 §4.2", "08 §4.2"],
  ak=["Workspace-Liste der Instanz mit Logo, Name, Slug, Owner, Projekt- und Mitgliederzahl, „Load more“ mit 10 je Seite und Suche (Contract-Golden).",
      "„Prevent anyone else from creating a workspace.“ setzt `DISABLE_WORKSPACE_CREATION`; danach zeigt `/create-workspace` für Nicht-Instanz-Admins den Original-Hinweis (E2E, Bezug WP-I0-002).",
      "Workspace-Anlage im God Mode mit automatisch erzeugtem, prüfbarem Slug nach denselben Regeln wie WP-I0-002; das Willkommens-Popup erscheint genau solange keine Workspaces existieren (E2E)."])

W("WP-I6-004", "Projekt veröffentlichen (Publish-Modal, Board-Einstellungen, Metadaten)", "V", "M", True,
  ["CE-SPACE-001", "CE-SPACE-002"], [M5, "WP-I6-203"],
  "Publish-Modal im Web und Board-Einstellungen/-Metadaten (`deploy_boards`, Anchor als 32-Zeichen-Hex).",
  be=["`src/modules/PublicSpace/Funk.PublicSpace`, `Funk.PublicSpace.Contracts`"], fe=["`frontend/libs/web/project-publish`"],
  arch=["04 §4.18", "03 §3.4.15"],
  ak=["Der Publish-Dialog speichert Layouts, Kommentare, Reaktionen, Voting und Intake in `deploy_boards`; der Anchor besteht aus 32 Hex-Zeichen und ist eindeutig; „Unpublish“ macht die öffentliche URL ungültig (Original-404).",
      "Board-Settings und Projekt-Metadaten per Anchor sowie die Anchor-Ermittlung per Projekt-ID entsprechen dem Original-Golden; nur Projekt-Admins veröffentlichen (Permission-Matrix)."])

W("WP-I6-005", "Space-App: Shell, Login-Einstieg über Keycloak, Fehler-/404-Seiten, Legacy-Redirects, Social-Meta, iframe, Badge (inkl. Nachweis entfallener Space-Logins)", "V", "L", True,
  ["CE-SPACE-008", "CE-SPACE-009", "CE-SPACE-010", "CE-SPACE-011", "CE-SPACE-012", "CE-SPACE-013", "CE-SPACE-014", "CE-SPACE-015", "CE-SPACE-016", "CE-SPACE-017", "CE-SPACE-029", "CE-SPACE-031", "CE-SPACE-032"],
  ["WP-I6-004", "WP-I6-203"],
  "Space-App unter `/spaces/`: Keycloak-Anmeldung (Client `funk-space`, Theme `funk-space`) mit Rücksprung inkl. Peek-Query, Fehlerbanner, Rechtshinweis, Eingeloggt-Ansicht, Instanzfehler, Legacy-URL-Weiterleitung, OG-Meta-Middleware im Gateway, iframe-Einbettung, Fehler-/404-Seiten und Badge „Powered by funk.“. Die Space-Login-Varianten des Originals entfallen (ADR-008) und sind mit `OidcLoginFlowTests.SpaceLogin_*` belegt.",
  fe=["`frontend/apps/space`", "`frontend/libs/space/core`"], be=["`src/hosts/Funk.Gateway` (OgMetaMiddleware)", "`src/modules/PublicSpace/Funk.PublicSpace`"],
  arch=["08 §4.3", "05 §3.3.2, O-D05-05", "14 §3.7.5", "09 §4.14"],
  ak=["Space-Boards bleiben anonym lesbar; Startseite zeigt Anmelde-Button, kein Auto-Redirect (O-D05-05)."])

W("WP-I6-006", "Space-Board: öffentliche Issue-Liste, Stammdaten, Navbar, List/Kanban read-only, Chips, Filter-Popover, aktive Filter", "V", "L", True,
  ["CE-SPACE-003", "CE-SPACE-005", "CE-SPACE-018", "CE-SPACE-019", "CE-SPACE-020", "CE-SPACE-021", "CE-SPACE-022", "CE-SPACE-023"], ["WP-I6-005"],
  "Öffentliches Board mit List- und Kanban-Layout (read-only), Eigenschafts-Chips, Filtern und Navbar.",
  be=["`src/modules/PublicSpace/Funk.PublicSpace` (`/api/public/`)"], fe=["`frontend/libs/space/issues`, `frontend/libs/space/views`"], arch=["04 §4.18", "08 §4.3, §4.6"],
  ak=["Die anonyme öffentliche Issue-Liste mit Filter, Sortierung, Gruppierung und Sub-Gruppierung entspricht dem Original-Golden; nicht veröffentlichte Projekte → Original-404.",
      "Die Navbar synchronisiert `board` und Filter mit der URL (Reload stellt den Zustand her, E2E); List und Kanban sind read-only (kein Schreib-Request im Netzwerkprotokoll); Kanban-Spalten 350 px mit Infinite Scroll je Spalte.",
      "Filter-Popover mit Priorität und State (Label-Filter wie im Original nicht angeboten); Chips mit Fälligkeitsdatum und Überfällig-Hervorhebung (Visual)."])

W("WP-I6-007", "Space: öffentliches Issue-Detail, Peek, Kommentarbilder/Asset-Auslieferung, Mentions (ED-6)", "V", "M", True,
  ["CE-SPACE-004", "CE-SPACE-007", "CE-SPACE-024", "CE-SPACE-030"], ["WP-I6-006"],
  "Issue-Detail und Peek mit Rich-Editor read-only, Space-Datei-Handler (Anchor-Asset-URLs) und Space-Mentions.",
  fe=["`frontend/libs/space/editor`, `frontend/libs/space/issues`"], be=["`src/modules/Assets/Funk.Assets` (Space-Auslieferung)"],
  arch=["10 §1.5 (ED-6)", "04 §4.13, §4.18"],
  ak=["Öffentliches Issue-Detail und Peek (Side, Modal, Full Screen) mit Beschreibung read-only (ED-6), Escape/Outside-Click und Fokusfalle (Playwright-Tastaturtest).",
      "Kommentarbilder: MIME-Erkennung über die Datei-Signatur (Datei mit falscher Endung wird nach Inhalt erkannt bzw. abgewiesen), Bindung an eigene Kommentare, Auslieferung per Redirect über Anchor-Asset-URLs; fremde Assets → Original-Fehler.",
      "Mentions zeigen `@Name` bzw. „@deactivated user“, eigene Mentions hervorgehoben (DOM-Snapshot)."])

W("WP-I6-008", "Space-Interaktionen: Kommentare, Reaktionen, Votes, öffentliche Intake-Einreichung", "V", "M", True,
  ["CE-SPACE-006", "CE-SPACE-025", "CE-SPACE-026", "CE-SPACE-027", "CE-SPACE-028"], ["WP-I6-007"],
  "Öffentliche Kommentare (Lite-Editor mit Bild-Upload), Kommentar- und Work-Item-Reaktionen, Up-/Downvotes (Keycloak-Anmeldung erforderlich) und die öffentliche Intake-Einreichung (nur API).",
  be=["`src/modules/PublicSpace/Funk.PublicSpace`", "`src/modules/Intake/Funk.Intake` (öffentliche Einreichung)"], fe=["`frontend/libs/space/issues`"],
  arch=["04 §4.9, §4.18", "00 ADR-008 (Space)"],
  ak=["Anonyme Nutzer lesen EXTERNAL-Kommentare; Schreiben, Reagieren und Voten erfordern die Keycloak-Anmeldung über `funk-space` (anonymer Klick → Login mit Rücksprung, E2E).",
      "Votes −1/1 eindeutig je Akteur und Work Item, Umschalten und Wechsel wie Original (L3, Golden); Reaktionen auf Work Items und EXTERNAL-Kommentare mit Picker und Umschalten eigener Reaktionen.",
      "Öffentliche Intake-Einreichung (nur API): angemeldete Nutzer reichen nur bei am Board aktiviertem Intake ein und sehen, ändern und löschen nur eigene Einreichungen (Permission-Matrix)."])

W("WP-I6-016", "API-Tokens: Liste, Anlage, Löschung", "V", "M", True,
  rng("CE-WH", 12, 14), [M5],
  "Persönliche API-Tokens (`funk_api_`-Präfix) mit Liste, Anlage (einmalige Anzeige) und Löschung.",
  be=["`src/modules/Identity/Funk.Identity` (ApiTokens)"], fe=["`frontend/libs/web/settings` (api-token)"], arch=["05 §3.12.3", "04 §4.1"],
  ak=["Der Token-Klartext mit Präfix `funk_api_` wird genau einmal (Antwort der Anlage) angezeigt; kein späterer Abruf liefert ihn (L3); Speicherung nach 05 §3.12.3.",
      "Ablaufoptionen 1 week, 1 month, 3 months, 1 year, Custom, Never expires; `is_active` wird aus dem Ablauf berechnet (`FixedClock`: Active → Expired); der CSV-Download enthält die Original-Spalten; nach dem Widerruf liefert der nächste v1-Request 401."])

W("WP-I6-009", "Public API v1: API-Key-Authentifizierung, Rate-Limit je Key, Aktivitätsprotokoll, OpenAPI, aktueller Benutzer", "B", "M", False,
  rng("CE-API", 1, 5), ["WP-I6-016", "WP-I6-201"],
  "Oberfläche `/api/v1/` mit `X-Api-Key`, Rate-Limit je Key, API-Activity-Log (Queue), OpenAPI (Scalar offline, Default aus, im God Mode einschaltbar, Z-112) und `GET …/users/me/`.",
  be=["`src/modules/PublicApi/Funk.PublicApi`", "`tests/modules/Funk.PublicApi.Tests`"], arch=["04 §3.11, §3.14, §4.19", "05 §3.12", "06 O-D06-08"],
  ak=["`OpenApiDocumentTests` gegen `v1.original.json`; LT-10 im Zielbereich."])

W("WP-I6-010", "Public API v1: Projekte, Archiv, Summary, States, Labels, Mitglieder, Einladungen", "B", "L", True,
  rng("CE-API", 6, 13), ["WP-I6-009"],
  "v1-Adapter auf die Contracts-Commands der Fachmodule (R6), inkl. HARM-03/-04/-06.",
  be=["`src/modules/PublicApi/Funk.PublicApi`"], arch=["04 §4.19, §5.3", "05 §3.18.1"],
  ak=["Alle v1-Endpunkte dieses Pakets bestehen die Contract-Szenarien gegen `v1.original.json` und die Original-Goldens (Erfolg, 400, 403/404, 409 bei Namens-/External-ID-Konflikt).",
      "Projektanlage über v1 legt Default-States, Admin-Mitgliedschaft und bei `intake_view` den Default-Intake an und löst die Webhook-Ereignisse aus (L3 mit Webhook-Recorder); Archivieren löscht die Favoriten.",
      "HARM-03/-04/-06 sind umgesetzt und in `deviations.yaml` mit Verweis auf 17 Z-09 dokumentiert; Einladungs-Endpunkte senden keine Mail und geben kein Token aus (wie Original)."])

W("WP-I6-011", "Public API v1: Stickies, User-Assets, Generic Workspace Assets", "B", "S", True,
  rng("CE-API", 14, 16), ["WP-I6-009"],
  "v1-Endpunkte für Stickies und Assets.",
  be=["`src/modules/PublicApi/Funk.PublicApi`"], arch=["04 §4.19"],
  ak=["Stickies-CRUD nur auf eigene Stickies mit Volltextsuche über `query` (Golden); fremde Stickies → Original-404.",
      "Die im Original v1.4.2 defekten Varianten (User-Assets Server-Variante, Generic Workspace Assets POST/GET) funktionieren korrigiert mit `golden_source: target` und `DEV-*`-Eintrag (17 Z-12); die Upload-Bestätigung setzt `is_uploaded`."])

W("WP-I6-012", "Public API v1: Work Items, Identifier, Suche, Links, Kommentare, Aktivitäten, Anhänge, Relationen, Intake", "B", "L", True,
  rng("CE-API", 17, 25), ["WP-I6-010"],
  "v1-Work-Item-Endpunkte inkl. Alias-Routen `issues`/`work-items`, State-Wechsel mit Origin `PublicApi`.",
  be=["`src/modules/PublicApi/Funk.PublicApi`"], arch=["04 §4.19, R-D04-07", "11 §3.7", "16 §5.9"],
  ak=["Die Alias-Routen `issues` und `work-items` liefern identische Antworten (Contract-Test je Endpunkt mit beiden Präfixen).",
      "Anlage mit Override von `created_at`/`created_by`, Default-Assignee und Default-Typ (`IWorkItemTypeResolver`) wie Original; State-Wechsel mit Origin `PublicApi` (AK-16-06); `GET {W}/work-items/{PROJ}-{seq}/` über `IWorkItemReferenceResolver`.",
      "Aktivitätsliste ohne Kommentar-, Vote-, Reaction- und Draft-Einträge; Relationen gruppiert nach den 8 v1-Typen mit Mapping auf die gespeicherte Richtung; Anhänge per Presigned POST mit MIME-Allowlist und 302-Download (Golden)."])

W("WP-I6-013", "Public API v1: Cycles, Work Items in Cycles, Transfer, Cycle-Archiv, Modules, Work Items in Modulen, Modul-Archiv", "B", "M", True,
  rng("CE-API", 26, 32), ["WP-I6-012"],
  "v1-Endpunkte für Cycles und Module.",
  be=["`src/modules/PublicApi/Funk.PublicApi`"], arch=["04 §4.19"],
  ak=["Filter `cycle_view` (all/current/upcoming/completed/draft/incomplete) liefert auf dem Parity-Seed dieselben Mengen wie das Original; Datumsangaben in Projekt-Zeitzone (Golden).",
      "Work Items werden aus anderen Cycles verschoben; der Cycle-Transfer friert den `progress_snapshot` ein und nutzt Origin `CycleTransfer` (AK-16-06); Cycle-/Modul-Archiv nur für abgeschlossene bzw. completed/cancelled Objekte (sonst Original-Fehler)."])

W("WP-I6-014", "Webhook-Verwaltung: Liste, Anlage, Secret anzeigen/regenerieren/herunterladen, Bearbeitung, Löschung", "V", "M", True,
  rng("CE-WH", 2, 6), [M5, "WP-I6-202"],
  "Settings-Seiten für Webhooks mit Secret-Verwaltung (`funk_wh_`-Präfix).",
  be=["`src/modules/Webhooks/Funk.Webhooks`"], fe=["`frontend/libs/web/settings` (web-hooks)"], arch=["04 §4.20", "03 §3.4.16"],
  ak=["Die Webhook-Anlage prüft die Payload-URL serverseitig nach den `SsrfSafeHttpHandler`-Regeln (internes Ziel → Original-Validierungsfehler); Ereignisauswahl „alle“ oder einzeln aus den über `IWebhookEventSource` registrierten CE-Arten (`project`, `issue`, `module`, `cycle`, `issue_comment`).",
      "Das Secret mit Präfix `funk_wh_` ist nur bei Anlage und Regenerierung sichtbar; der CSV-Download enthält URL, Ereignisse und Secret wie das Original; Regenerieren macht das alte Secret ungültig (nächste Zustellung trägt die neue Signatur `X-Funk-Signature`).",
      "Liste, Detailseite, Aktiv-Schalter und Löschen nur für Workspace-Admins (Permission-Matrix)."])

W("WP-I6-015", "Webhook-Zustellung: Datenmodell/Event-Typen, Zustellung, Payload, Deaktivierungs-Mail, Protokoll, SSRF-Schutz", "B", "L", True,
  ["CE-WH-001", "CE-WH-007", "CE-WH-008", "CE-WH-009", "CE-WH-010", "CE-WH-011"], ["WP-I6-014", "WP-I6-202"],
  "`WebhookEventConsumer` (Trigger-Tabelle: 24 Original-Stellen + 6 Auslöser, ABG-137), Job `webhooks.deliver` mit `X-Funk-Signature` (HMAC-SHA256 über die gesendeten Bytes), stabiler `X-Funk-Delivery`, 6 Versuche, Deaktivierung + Mail M10, Zustellprotokoll, SSRF-Client `webhooks`.",
  be=["`src/modules/Webhooks/Funk.Webhooks`"], arch=["06 §3.14, §5.8, D06-ADR-15, -16", "05 §3.17.2", "04 §3.17, §4.27"],
  ak=["`WebhookTriggerCoverageTests` grün; Payload-Golden je Ereignis gegen das Original (Header-Namen gemäß ADR-009C, Abweichung dokumentiert)."])

W("WP-I6-017", "Work-Item-Export (CSV/XLSX/JSON), Export-Historie und Download", "B", "M", True,
  ["CE-EXP-001", "CE-EXP-002"], ["WP-I6-202"],
  "Job `exports.work_items` mit Spalten/Reihenfolge/Kopfzeilen/Formel-Schutz wie `API/utils/porters/**` (CsvHelper, ClosedXML), Ablage im Objektspeicher, Download-Link 7 Tage, Historie.",
  be=["`src/modules/Exports/Funk.Exports`"], fe=["`frontend/libs/web/settings` (exporter)"], arch=["06 §3.15.1, §4.12, D06-ADR-17"],
  ak=["G-EXPORT (28 Spalten, 06 §4.12) grün."])

W("WP-I6-018", "KI-Assistent im Work-Item-Modal und Unsplash-Bildsuche", "V", "M", True,
  ["CE-AI-001", "CE-AI-002"], [M5, "WP-I6-002"],
  "KI-Assistent über `IChatClient` (Microsoft.Extensions.AI, OpenAI-kompatibler Endpunkt, lokal betreibbar) und Unsplash-Suche; beides optional und abschaltbar (ADR-004).",
  be=["`src/modules/Assistant/Funk.Assistant`", "`src/platform/Funk.Platform.Ai`"], fe=["`frontend/libs/web/work-items` (gpt-assistant)", "`frontend/libs/shared/blocks` (image-picker Unsplash-Tab)"],
  arch=["11 §3.13–§3.17, §5.7, §5.8", "04 §4.22", "17 Z-111"],
  ak=["Ohne konfigurierten Provider ist `has_llm_configured = false` und die KI-UI unsichtbar; mit einem WireMock-OpenAI-kompatiblen Endpunkt liefern „I'm feeling lucky“ und der Assistent die Antwort für `task`+`prompt` in der Antwortform des Originals (Golden).",
      "Ausgehende Aufrufe nur über die benannten Clients `llm` und `unsplash` mit SSRF-Schutz (OE-11); ohne Unsplash-Key liefert die Suche eine leere Liste; ohne beide Dienste ist die Anwendung im Airgap-Profil voll bedienbar (E2E ohne Egress)."])

W("WP-I6-999", "Abnahme I6 – Außenwirkung & Administration (G5)", "A", "S", False,
  [], ["WP-I6-%03d" % i for i in range(1, 19)] + ["WP-I6-201", "WP-I6-202", "WP-I6-203"],
  "Inkrement-Abnahme I6 nach G5 und Meilenstein M6.",
  arch=["plan/01-roadmap-ce.md §4 (M6)", "15 §3.16 Zeile I6"],
  ak=["Alle Abnahmekriterien M6 erfüllt; `docs/acceptance/I6.md` generiert."], tests=["G5 `--inc I6`."])

# =====================================================================================
# I7 – Härtung & Betrieb
# =====================================================================================
M6 = "WP-I6-999"

W("WP-I7-101", "funk-cli: Self-Hosting-CLI, Backup/Restore, Betriebs-Commands", "B", "L", True,
  ["CE-OPS-001", "CE-OPS-002", "CE-OPS-020"], [M6],
  "`funk-cli` mit `install`, `init`, `config check`, `migrate`, `seed`, `backup`, `restore [--include-secrets]`, `test-email`, `clear-cache`, `reset-instance-admin-mapping`, `identities relink`, `realtime …`; Backup = `pg_dump` + Objektspeicher + Key-Ring.",
  be=["`src/tools/Funk.Cli`", "`tests/Funk.Cli.Tests`", "`tests/deploy/`"], arch=["14 §3.11.3, §3.16, §3.22", "05 §4.6", "07 §3.8.4"],
  orig=["`deployments/cli/community/install.sh`", "`apps/api/plane/db/management/commands/`"],
  ak=["Backup/Restore-Test (G6): Restore auf leerer Instanz reproduziert Daten, Dateien und Login-Fähigkeit."])

W("WP-I7-102", "Docker Compose (Aspire-Publisher) und Docker-Swarm-Deployment", "I", "M", True,
  ["CE-OPS-003"], [M6],
  "Generierte `deploy/compose/docker-compose.yaml` mit Profilen (`bundled-s3`, `forgejo`, `valkey`, `acme`, `observability`, `tools`), Swarm-Kompatibilität und Smoke-Test.",
  be=["`deploy/compose/`", "`tests/deploy/compose/`"], arch=["14 §3.11"], ak=["Compose- und Swarm-Smoke grün; Compose-Drift-Gate leer."])

W("WP-I7-103", "All-in-One-Container funk-aio", "I", "M", True,
  ["CE-OPS-004"], [M6],
  "`Funk.AllInOne` (Gateway+Api+Realtime+Worker in einem Prozess, In-Memory-Backplane) und Image `funk-aio` mit generierter `docker-compose.aio.yaml`.",
  be=["`src/hosts/Funk.AllInOne`"], arch=["14 §3.13", "07 §1.4 Zeile I7", "17 ABG-019"],
  ak=["`funk-aio` startet Gateway, Api, Realtime und Worker in einem Prozess, führt die Migration unter Advisory-Lock aus und meldet erst danach Ready; `docker-compose.aio.yaml` (postgres, keycloak, keycloak-config, funk-aio) besteht den `@smoke`-Satz.",
      "Der Start bricht mit Exit-Code ≠ 0 und Log-Meldung ab, wenn `WEB_URL`/`DOMAIN_NAME` fehlen oder ungültig sind (FQDN ≤ 253 Zeichen oder IPv4), Secrets Bekannt-Defaults sind oder `ExpectMultipleInstances=true` gesetzt ist (je Fall ein Container-Test).",
      "Alle Queues inkl. `live` laufen im Prozess: Notification-Zähler-Push < 2 s ohne Valkey (`LiveEventLatencyTests` gegen AIO)."])

W("WP-I7-104", "Read-Replica-Unterstützung", "B", "S", True,
  ["CE-OPS-010"], [M6],
  "Zweite Verbindung für lesende Endpunkte mit `read_replica: true` laut Endpunktkatalog.",
  be=["`src/building-blocks/Funk.BuildingBlocks.Persistence/ReadReplica/`"], arch=["04 §4 (Spalte `read_replica`)", "14 §3.18"],
  ak=["Mit gesetztem `ConnectionStrings__funk-replica` gehen GET/HEAD/OPTIONS genau der Endpunkte mit `read_replica: true` (Katalog 04) an die Replica, alle Schreibzugriffe und Migrationen an die Primary (L3 mit zwei Datenbanken und Abfrage-Zähler je Verbindung).",
      "Ohne Replica-Konfiguration nutzen alle Endpunkte die Primary; Architekturtest: kein schreibender Handler trägt `read_replica: true`."])

W("WP-I7-105", "TLS-Modi und Reverse-Proxy mit automatischem HTTPS (ACME)", "I", "M", True,
  ["CE-OPS-005"], [M6],
  "TLS-Modi des Gateways (aus, eigenes Zertifikat, ACME) und Compose-Profil `acme`; Zertifikatspflicht für Data Protection in Produktion.",
  be=["`src/hosts/Funk.Gateway` (TLS)", "`deploy/compose/` (Profil acme)"], arch=["14 §3.8"],
  note="Abweichung von 15 Anhang B (I0): Das Gateway-Grundrouting ist I0 (WP-I0-103), automatisches HTTPS gehört nach 14 §3.1.2 zu I7 (plan/04 OP-PLAN-03).",
  ak=["Modus `None`: nur HTTP 8080, HSTS nur hinter vertrautem Proxy mit `X-Forwarded-Proto=https`; Modus `Certificate`: 8443 mit PEM/PFX, 8080 → 308 (außer `/.well-known/acme-challenge/`), Zertifikatswechsel ohne Neustart (Datei ersetzen → neue Verbindung erhält das neue Zertifikat < 10 s).",
      "Das Compose-Profil `acme` mit gepinntem `caddy` erhält gegen eine Test-ACME-CA (nur Test) ein Zertifikat und leitet auf das Gateway weiter (Compose-Smoke); Header- und Body-Limits wie Original.",
      "Eine eigene CA unter `/etc/funk/ca/*.crt` wird von .NET, Keycloak und Forgejo vertraut (AK-14-26); in Produktion startet funk. ohne Zertifikat für Data Protection nicht (Konfigurationstest)."])

W("WP-I7-106", "Helm-Chart deploy/helm/funk", "I", "M", True,
  [], [M6],
  "Helm-Chart mit allen Diensten, Keycloak (Deployment für Einzelknoten, Operator-Hinweis für HA), Secrets und `NOTES.txt` (G-BRAND).",
  be=["`deploy/helm/funk/`"], arch=["14 §3.12, O-14-08"], ak=["`helm lint`, `helm template | kubeconform` und Kind-Smoke grün."])

W("WP-I7-107", "Airgapped-Bundle und Egress-gesperrter E2E-Lauf", "I", "M", True,
  [], [M6, "WP-I7-101", "WP-I7-102", "WP-I7-103", "WP-I7-105", "WP-I7-106"],
  "`funk-airgap-<version>-<arch>.tar.zst` mit vollständiger Image-Liste (inkl. Forgejo, Keycloak), Prüfliste „keine externen Calls“ und E2E-Lauf mit gesperrtem Egress in CI.",
  be=["`deploy/airgap/`"], arch=["14 §3.14", "00 ADR-004", "01 P6"], ak=["Airgap-E2E grün, CSP-Report leer, keine DNS-Anfragen nach außen."])

W("WP-I7-108", "Sicherheitshärtung: CSP-Enforce, ZAP, Permission-Matrix 100 %, Upgrade-Pfad", "I", "M", True,
  [], [M6],
  "CSP von Report-Only auf Enforce (Z-108), ZAP-API-Scan, Permission-Matrix für 100 % der Endpunkte, Upgrade-Test (Migrator auf Dump der Vorversion), Image-Signaturen.",
  be=["`tests/security/`", "`.github/workflows/images.yml` (cosign)"], arch=["05 §3.17.7, R-12", "15 §3.13", "14 §3.17, §3.21"],
  ak=["0 ungenehmigte Matrix-Abweichungen; keine Critical/High-CVE mit verfügbarem Fix."])

W("WP-I7-109", "Last-, Soak- und Performance-Abnahme (LT-08, LT-13, LT-21, Worker-Kill-Tests)", "I", "M", True,
  [], [M6],
  "Restliche Lastziele aus `tests/load/thresholds.yaml` sowie Worker-Ausfalltests (LT-12) und Revalidierungslast auf Keycloak (LT-13).",
  be=["`tests/load/`"], arch=["15 §3.12", "06 §1.3 Zeile I7", "05 R-06"],
  ak=["LT-08 (XL, 200 VU, 30 min): p95 < 500 ms, p99 < 1 s, Fehler < 0,1 %, CPU `api` < 70 %, DB-Verbindungen < 60 % von `max_connections`; LT-13 (50 Logins/s): p95 Callback < 300 ms ohne Keycloak-Zeit; LT-21 (Einzelknoten 2 vCPU/4 GB, 60 min): p95 Listen < 500 ms, RSS nach 60 min ≤ 110 % des 10-min-Werts – jeweils auf Runner `perf` (`artifacts/load/<LT>.json`).",
      "Worker-Kill-Test im LT-12-Aufbau: `kill -9` eines von 3 Workern bei 1 000 Jobs/s verliert keine Nachricht und verarbeitet keine doppelt (Inbox-Nachweis).",
      "Volumenprofil XL (20 Projekte, 200 000 Items, 500 Benutzer, 2 000 Pages, 1 Mio. Activities) entsteht in < 20 min und wird als Dump zwischengespeichert (15 §3.14.3)."])

W("WP-I7-110", "Paritäts-Gesamtabnahme aller Screens, Endpunkt-Abdeckung 100 %, Abweichungsliste", "I", "M", False,
  [], [M6, "WP-I7-107", "WP-I7-108"],
  "Visual-/DOM-Abnahme aller Einträge des Screenshot-Katalogs (09 §4.14), `coverage --fail-under 100` für Endpunkte, konsolidierte Abweichungsliste (`deviations.yaml`, `ui-deviations.yaml`, `BRAND-*`) zur Abnahme durch den Auftraggeber.",
  arch=["15 §3.10, §3.16 Zeile I7", "09 §3.14.8", "04 §4.29"],
  ak=["Jeder Eintrag des Screenshot-Katalogs (09 §4.14) liegt innerhalb der Schwellwerte 15 §3.10.3 (Chromium) oder hat einen genehmigten `ui-deviations.yaml`-Eintrag; Visual-Quote 100 %.",
      "`coverage --fail-under 100` für alle 564 registrierten Endpunkte (`_data/wp-endpoints.json`); 0 Abweichungen ohne Entscheidung in `deviations.yaml`, `ui-deviations.yaml` und `BRAND-*`.",
      "Die konsolidierte Abweichungsliste liegt als `docs/acceptance/deviations-I7.md` vor und trägt den Freigabevermerk des Auftraggebers."])

W("WP-I7-201", "Erweiterungspunkte stabilisieren: Contract-Snapshots aller Erweiterungs-Interfaces, Airgap-Test mit Forgejo", "X", "S", True,
  [], [M6, "WP-I7-107"],
  "C#-Snapshot per `PublicApiGenerator` + Verify (`ExtensionContractsSnapshotTests`), TS-Snapshot per `api-extractor` von `libs/web/extensions/public-api.ts`, Airgap-Lauf mit gebündeltem Forgejo.",
  be=["`tests/Funk.ArchitectureTests/ExtensionContractsSnapshotTests.cs`"], fe=["`frontend/libs/web/extensions/api-report.md`"],
  arch=["16 D16-ADR-07, §1.4 Zeile I7, §7"],
  ep="16 §1.4 Zeile I7; 16 §4.6 (Träger CE-OPS-023)",
  ak=["Jede nicht additive Änderung an einem Erweiterungs-Interface bricht den Snapshot-Test.",
      "AK-16-05: `ExtensionContractsSnapshotTests` und der `api-extractor`-Report von `libs/web/extensions/public-api.ts` lassen nur additive Diffs zu (Testfixture: entfernter Member bricht den Build).",
      "AK-16-02: Contract-Replay und Visual-Suite mit allen CE-Default-Registrierungen = Lauf ohne Andockstellen-Registrierung (0 Abweichungen); Airgap-Lauf mit gebündeltem Forgejo aus dem Bundle von WP-I7-107 grün."])

W("WP-I7-999", "Abnahme I7 – CE-Release-Kandidat (G5 + G6)", "A", "S", False,
  [], ["WP-I7-%03d" % i for i in range(101, 111)] + ["WP-I7-201"],
  "Inkrement-Abnahme I7 und Release-Gate G6 – Meilenstein M7 (CE-Release).",
  arch=["plan/01-roadmap-ce.md §4 (M7)", "15 §3.15.1 (G6)"],
  ak=["Alle Abnahmekriterien M7 erfüllt; `docs/acceptance/I7.md` und Release-Bericht generiert."], tests=["G5 `--inc I7`, G6."])
