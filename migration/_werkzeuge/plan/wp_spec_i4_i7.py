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
  [], [M3],
  "`pages.workspace_id` mit Projektzuordnung über `project_pages`, `pages.parent_id` (CE immer `null`), `IPageHierarchy` und `IPageHierarchyQueries` (E-23, CE flach/`[]`), `IPageAccessExtension` (Default `false`); Frontend `PAGE_STORES`, `PAGE_TREE`, `PAGE_FLAGS`, `PAGE_PANE_EXTENSIONS`.",
  be=["`src/modules/Pages/Funk.Pages.Contracts/Hierarchy/`", "`src/data/Funk.Data/Entities/Pages/`"], fe=["`frontend/libs/web/extensions/src/pages.ts`"],
  arch=["16 §5.13, §3.3.0 E-23", "01 §1.4 Zeilen D1, D2", "03 §3.4.10"],
  ep="01 §1.4 D1/D2; 16 §3.3.0 E-23; 16 §4.6 (Träger CE-PAGE-001/-003/-004/-006/-007)",
  ak=["Contract-Goldens der Page-Payloads unverändert; Fake-Hierarchie liefert Kinder, die im `PAGE_TREE` erscheinen (Typ X)."])

W("WP-I4-202", "Erweiterungspunkte Kollaboration: ICollaborationDocumentType, affectedPages, EDITOR_BLOCKS, EDITOR_MENTION_TYPES", "X", "S", False,
  [], ["WP-I2-999", "WP-I4-101"],
  "Registry der Hocuspocus-`documentType`-Werte (E-10, CE: `ProjectPageDocumentType` = `project_page`), server-seitig erzeugbares Realtime-Event `affectedPages`, Editor-Tokens `EDITOR_BLOCKS` und `EDITOR_MENTION_TYPES`.",
  be=["`src/modules/Collaboration/Funk.Collaboration.Contracts/ICollaborationDocumentType.cs`"], fe=["`frontend/libs/shared/editor/extensibility`"],
  arch=["07 §5.2, §5.3, §3.7.2", "10 §5.10, §6.2", "16 §3.3.0 E-10"],
  ep="16 §3.3.0 E-10; 16 §4.6 (Träger CE-RT-001, CE-RT-004, CE-RT-005)",
  ak=["Fake-Dokumenttyp wird über das Protokoll geladen/gespeichert ohne CE-Änderung; Fake-Block erscheint im Slash-Menü (Typ X)."])

W("WP-I4-006", "Realtime-Kollaborationsserver: Protokoll, Dokument-Lebenszyklus, Persistenz, Titel-Sync, Fehler/Force-Close, Konvertierung", "D", "L", False,
  ["CE-RT-001", "CE-RT-005", "CE-RT-006", "CE-RT-008"], ["WP-I4-101", "WP-I4-202", "WP-I0-107", "WP-I0-901"],
  "`Funk.Collaboration` (+ `.Protocol`) nach dem Ergebnis von S1: Wire-Protokoll, Zustandsautomaten, Auth über Session-Ticket, Laden/Migration HTML→Binary, Merge-on-Store mit 10-s-Debounce, Titel-Sync, Stateless-Ereignisse, Fehler-Broadcast, Force-Close, Admin-Kanal, Graceful Shutdown und `/live/convert-document/`.",
  be=["`src/modules/Collaboration/Funk.Collaboration`, `.Protocol`, `.Contracts`", "`src/modules/Pages/Funk.Pages/Documents/IPageDocumentStore` (Merge-on-Store)", "`tests/Funk.Collaboration.Tests`"],
  arch=["07 §3.1–§3.9, §3.11, §5.1–§5.6, §7.3", "05 §3.11", "17 Z-101"],
  ak=["Protokollfälle P-01…P-30 mit dem Original-Provider im Browser grün (`ProviderConformanceTests`).", "LT-16…LT-18 im Zielbereich."])

W("WP-I4-007", "Client-Kollaboration: Echtzeit-Editor-Bindung, Offline-Cache, REST-Fallback, Seitenereignisse (ED-4-Kern)", "D", "L", False,
  ["CE-RT-002", "CE-RT-003", "CE-RT-004"], ["WP-I4-006", "WP-I2-024"],
  "`CollaborationSession` mit `HocuspocusProvider` 2.15.2, IndexedDB-Offline-Cache, Sync-Status, Stateless-Kanal, REST-Fallback-Speicherung (`setProviderDocument`, `getDocument`) und Echtzeit-Seitenereignisse; `collaboration-cursor` aktiv, sobald S1-Awareness grün ist (Z-109).",
  fe=["`frontend/libs/shared/editor/collaboration`"], be=["`src/modules/Pages/Funk.Pages` (REST-Fallback)"],
  arch=["10 §1.5 (ED-4), §3.15, §5.8", "07 §3.7, §3.11", "08 §3.12", "17 Z-109"],
  ak=["AK-D10-14…-18 grün; Abweichung `collaboration-cursor` als FE-ED-01 in `ui-deviations.yaml` dokumentiert und vom Auftraggeber abgenommen."])

W("WP-I4-008", "Horizontale Skalierung des Realtime-Servers (Valkey-Backplane, PostgreSQL-Signale)", "B", "M", True,
  ["CE-RT-007"], ["WP-I4-006"],
  "Valkey-Backplane (`BackplaneEnvelope`), In-Memory-Backplane für Einzelknoten/AIO, PostgreSQL-Signale (`CollaborationSignalListener`), Multi-Instanz-Setup (2 × `realtime`) im Profil `test`.",
  be=["`src/modules/Collaboration/Funk.Collaboration/Backplane/`"], arch=["07 §3.10, §5.9", "14 §3.1.2 Zeile I4"],
  ak=["Zwei Realtime-Instanzen konvergieren (Konvergenztest), LT-19/LT-20 im Zielbereich; Speicherdruck-Watchdog nach LT-20 entschieden (O-07-05)."])

W("WP-I4-001", "Page-Liste mit Tabs, Suche/Filter/Sortierung, Anlage, Favoriten", "V", "M", False,
  ["CE-PAGE-001", "CE-PAGE-002", "CE-PAGE-003", "CE-PAGE-010"], [M3, "WP-I4-201"],
  "Page-Liste (öffentlich, privat, archiviert), Suche, Filter, Sortierung, Page anlegen und favorisieren.",
  be=["`src/modules/Pages/Funk.Pages`, `Funk.Pages.Contracts`", "`tests/modules/Funk.Pages.Tests`"], fe=["`frontend/libs/web/pages`"],
  arch=["04 §4.10", "03 §3.4.10"])

W("WP-I4-002", "Page-Aktionen: Daten/Detail, sperren, Zugriff, archivieren, löschen, duplizieren, Referenzprotokoll", "V", "L", True,
  ["CE-PAGE-004", "CE-PAGE-005", "CE-PAGE-006", "CE-PAGE-007", "CE-PAGE-008", "CE-PAGE-009", "CE-PAGE-012"], ["WP-I4-001"],
  "Page-Detail, Sperren/Entsperren, Zugriff öffentlich/privat (Page-Zugriffsregel 05 §3.13.5), Archivieren/Wiederherstellen, Löschen, Duplizieren mit Asset-Umschreibung und PageLog (synchron über `PageReferenceIndexer`).",
  be=["`src/modules/Pages/Funk.Pages`"], fe=["`frontend/libs/web/pages`"],
  arch=["04 §4.10", "05 §3.13.5", "07 §3.11", "06 D06-ADR-02 (PageLog)", "17 ABG-108"])

W("WP-I4-003", "Page-Export als PDF und Markdown", "D", "M", True,
  ["CE-PAGE-011"], ["WP-I4-002", "WP-I0-903", "WP-I4-101"],
  "`Funk.Documents.Pdf` mit den Stilprofilen `live` und `web` nach dem Ergebnis von S3, Endpunkt `POST /live/pdf-export/`, Markdown-Export.",
  be=["`src/documents/Funk.Documents.Pdf`", "`tests/Funk.Documents.Pdf.Tests`"], fe=["`frontend/libs/web/pages` (export)"],
  arch=["07 §3.15, §5.10", "17 Z-103, Z-116"],
  ak=["G-PDF, G-PDF-web und G-MD grün; Web-PDF-Kursiv wie Original (Z-116, bis Auftraggeber anders entscheidet)."])

W("WP-I4-004", "Kollaborativer Page-Editor (Seite, Toolbar, Kopf, Outline, Info-, Assets-Panel, Anzeigeoptionen) – ED-4-Hüllen", "V", "L", False,
  ["CE-PAGE-013", "CE-PAGE-014", "CE-PAGE-015", "CE-PAGE-016", "CE-PAGE-017", "CE-PAGE-018", "CE-PAGE-020"], ["WP-I4-007", "WP-I4-002"],
  "Page-Seite mit `PlEdCollaborativeDocumentEditor`, `PlEdTitleEditor`, Navigation Titel↔Inhalt, Toolbar, Kopf, Outline, Info-Panel, Assets-Panel und Anzeigeoptionen.",
  fe=["`frontend/libs/web/pages`", "`frontend/libs/web/core/editor` (Page-Hüllen)"], arch=["10 §1.5 (ED-4), §3.16, §3.21", "08 §4.1"])

W("WP-I4-005", "Page-Versionshistorie", "V", "M", True,
  ["CE-PAGE-019"], ["WP-I4-006"],
  "Versionierung beim Speichern (Fix CE-PAGE-019 laut 07), Versionsliste und -anzeige mit Document-Editor read-only, Versions-Cleanup.",
  be=["`src/modules/Pages/Funk.Pages` (Versions)"], fe=["`frontend/libs/web/pages` (version-history)"], arch=["07 §3.6.4, §3.20", "06 §1.3 Zeile I4"])

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
  ak=["Alle Abnahmekriterien M4 erfüllt; `docs/acceptance/I4.md` generiert."], tests=["G5 `--inc I4`."])

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
  ak=["Index-Konsistenz-Job `indexing.reconcile` repariert absichtlich gelöschte Index-Zeilen; Fake-Enricher ergänzt Felder ohne CE-Änderung (Typ X)."])

W("WP-I5-202", "Erweiterungspunkte UI I5: HOME_WIDGETS, POWER_K_COMMANDS, SEARCH_RESULT_RENDERERS, erste Nutzung LIVE_EVENT_HANDLERS", "X", "S", False,
  [], [M4],
  "Frontend-Registries für Home-Widgets (E-14, CE-Widgets aus `apps/web/core/components/home/widgets`), Power-K-Befehle und Such-Ergebnis-Renderer; erste Handler für `LIVE_EVENT_HANDLERS` (Notification-Zähler).",
  fe=["`frontend/libs/web/extensions/src/{home,power-k,search}.ts`", "`frontend/libs/web/notifications/src/live/`"],
  arch=["08 §6.4", "16 §1.4 Zeile I5", "06 §5.12"],
  ep="16 §1.4 Zeile I5; 16 §4.6 (Träger CE-HOME-001/-002, CE-NOTIF-001, CE-SRCH-004)",
  ak=["Fake-Widget, Fake-Befehl und Fake-Renderer erscheinen ohne CE-Änderung (Typ X)."])

W("WP-I5-001", "Workspace-Analytics: Tabs, Kennzahlen, Project Insights, Active Projects, Created vs Resolved, Customized Insights, Insight-Tabelle mit CSV", "V", "L", True,
  rng("CE-ANA", 1, 7), [M4, "WP-I3-101"],
  "Analytics-Seite mit allen CE-Tabs und Diagrammen, Insight-Tabelle mit CSV-Export.",
  be=["`src/modules/Analytics/Funk.Analytics`", "`tests/modules/Funk.Analytics.Tests`"], fe=["`frontend/libs/web/analytics`"],
  arch=["04 §4.14", "03 §3.4.13", "09 §3.12"])

W("WP-I5-002", "Analytics-Panel (Projekt, Cycle, Modul), Legacy-Analytics, gespeicherte Analytics-Views, Export per E-Mail", "V", "M", True,
  ["CE-ANA-008", "CE-ANA-009"], ["WP-I5-001", "WP-I1-102"],
  "Analytics-Panel in Projekt-, Cycle- und Modul-Kontexten, Legacy-Analytics, gespeicherte Analytics-Views und Export per E-Mail (Template M11).",
  be=["`src/modules/Analytics/Funk.Analytics`"], fe=["`frontend/libs/web/analytics`"], arch=["04 §4.14", "06 §3.15.2"])

W("WP-I5-003", "Workspace-Home: Widgets, Widget-Verwaltung, Quickstart, Quick links, Recents, Produkt-Tour, Legacy-Dashboard", "V", "L", True,
  rng("CE-HOME", 1, 7), [M4, "WP-I5-202"],
  "Home mit Widgets über `HOME_WIDGETS`, Widget-Verwaltung, Quickstart-Guide, Quick links, Recents (Recent-Visits-Job), Produkt-Tour und Legacy-Dashboard/Aktivitätsgraphen (nur API).",
  be=["`src/modules/Home/Funk.Home`", "`tests/modules/Funk.Home.Tests`"], fe=["`frontend/libs/web/home`"],
  arch=["04 §4.15", "03 §3.4.12", "06 O-D06-09"])

W("WP-I5-004", "Stickies: Widget, Seite, Bearbeitung (ED-5)", "V", "M", True,
  rng("CE-HOME", 8, 10), ["WP-I5-003"],
  "Stickies-Widget, Stickies-Seite mit Masonry und Sticky-Editor (Lite + Sticky-Toolbar, Farbpalette).",
  be=["`src/modules/Home/Funk.Home` (Stickies)"], fe=["`frontend/libs/web/stickies`", "`frontend/libs/web/core/editor` (sticky-editor)"],
  arch=["04 §4.15", "10 §1.5 (ED-5)"])

W("WP-I5-005", "Benachrichtigungen erzeugen: In-App, Mentions, automatisches Abonnieren, Zähler-Push", "B", "M", False,
  rng("CE-NOTIF", 1, 3), [M4, "WP-I5-202", "WP-I0-207"],
  "`ActivityNotificationConsumer` (Queue `notifications`) aus `funk.work_item_activity.recorded.v1` mit Original-Algorithmus, Mention-Benachrichtigungen, Auto-Subscribe; `funk.notification.created.v1` → `RealtimeFanOutConsumer` → Zähler-Push über SignalR.",
  be=["`src/modules/Notifications/Funk.Notifications`", "`src/modules/RealtimeEvents/Funk.RealtimeEvents/Consumers/RealtimeFanOutConsumer.cs`"],
  arch=["06 §3.10, §3.12, §5.7, D06-ADR-10, -12", "07 §3.16.4", "17 ABG-106"],
  ak=["`LiveEventLatencyTests`: Zähler-Push < 2 s mit und ohne Valkey (Z-104); Notification-Daten (`data`-JSON) byte-gleich zum Original-Golden."])

W("WP-I5-006", "Inbox: Seite, Liste, Filter/Optionen, lesen/archivieren/snoozen, Detail", "V", "L", True,
  rng("CE-NOTIF", 4, 7), ["WP-I5-005"],
  "Inbox-Seite mit Benachrichtigungsliste, Filtern und Optionen, Lesen/Archivieren/Snoozen und Detail.",
  be=["`src/modules/Notifications/Funk.Notifications`"], fe=["`frontend/libs/web/notifications`"], arch=["04 §4.16", "03 §3.4.14"])

W("WP-I5-007", "E-Mail-Benachrichtigungen mit 5-Minuten-Bündelung und Einstellungen", "B", "M", True,
  ["CE-NOTIF-008", "CE-NOTIF-009"], ["WP-I5-005", "WP-I1-102"],
  "Cron `notifications.email_digest` (alle 5 min) gruppiert je (Empfänger, Work Item), Versand-Job mit genau den IDs der Gruppe, Template M12, Benachrichtigungseinstellungen.",
  be=["`src/modules/Notifications/Funk.Notifications`"], fe=["`frontend/libs/web/settings` (notifications)"], arch=["06 §3.11, D06-ADR-11"])

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
  note="Power-K zeigt bei Pages den Projekt-Identifier nicht an (Original-Defekt `project__identifiers`, O-D11-04) – optisch 1:1 belassen, Eintrag in `ui-deviations.yaml`.")

W("WP-I5-010", "Your work: Summary, Work-Item-Tabs, Activity, Profil-Sidebar", "V", "M", True,
  rng("CE-PROF", 8, 11), [M4],
  "Profilseiten „Your work“ mit Zusammenfassung, Work-Item-Tabs (Layout-Kontext Profil), Activity und Profil-Sidebar.",
  be=["`src/modules/Workspaces/Funk.Workspaces` (Member-Profile)"], fe=["`frontend/libs/web/profile`"], arch=["04 §4.3", "08 §4.1"])

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
  ak=["OpenAPI-Golden `v1.original.json` unverändert mit CE-Defaults; Fake-Payload-Extension ergänzt ein Feld ohne CE-Änderung (Typ X)."])

W("WP-I6-202", "Erweiterungspunkte IWebhookEventSource und IExportTypeProvider", "X", "S", False,
  [], [M5],
  "Zusätzliche Webhook-Ereignisarten über `IWebhookEventSource` (E-08, CE: `project`, `issue`, `module`, `cycle`, `issue_comment`) und Exporttypen über `IExportTypeProvider` (E-16).",
  be=["`src/modules/Webhooks/Funk.Webhooks.Contracts`", "`src/modules/Exports/Funk.Exports.Contracts`"],
  arch=["06 §5.9", "16 §3.3.0 E-08/E-16"],
  ep="16 §3.3.0 E-08, E-16; 16 §4.6 (Träger CE-WH-001/-007/-008, CE-EXP-001/-002)",
  ak=["Fake-Quelle erzeugt eine neue Webhook-Ereignisart, Fake-Exporttyp erscheint in der Export-Auswahl (Typ X)."])

W("WP-I6-203", "Erweiterungspunkte Space/Admin: SPACE_ROUTE_EXTENSIONS, EDITOR_EXTENSIONS (Space), ADMIN-Registries mit CE-Inhalt", "X", "S", False,
  [], [M5],
  "Space-Routen-Registry, Editor-Erweiterungen im Space-Scope (S44) und Befüllung der Admin-Registries (`ADMIN_SETTINGS_PAGES`, `ADMIN_ROUTE_EXTENSIONS`, `ADMIN_HEADER_SEGMENT_LABELS`) mit allen CE-Seiten.",
  fe=["`frontend/libs/space/extensions`", "`frontend/libs/admin/extensions`"], arch=["08 §6.4", "16 §1.4 Zeile I6", "17 ABG-023"],
  ep="16 §1.4 Zeile I6; 16 §4.6 (Träger CE-SPACE-001/-018/-025, CE-INST-003/-025)",
  ak=["Fake-Space-Route und Fake-Admin-Seite erscheinen ohne CE-Änderung (Typ X)."])

W("WP-I6-001", "God Mode: Abmeldung, Fehleransicht, Dashboard-Shell, Header, Konto-Menü, Hilfe, Unsaved-Dialog, Kopierfelder, 404", "V", "L", True,
  rng("CE-INST", 8, 16), [M5, "WP-I6-203"],
  "Vollständige Admin-Shell mit Sidebar, Breadcrumb-Header, Konto-Menü mit Theme-Umschaltung, Hilfe-Bereich, Dialog für ungespeicherte Änderungen, Kopierfeldern für funk.-URLs, Fehler- und 404-Seiten.",
  fe=["`frontend/apps/admin`", "`frontend/libs/admin/{core,common}`"], be=["`src/modules/Instance/Funk.Instance`"],
  arch=["08 §4.2", "05 §3.8", "09 §4.14"])

W("WP-I6-002", "God Mode: Allgemeine Einstellungen, SMTP, Test-E-Mail, AI-Einstellungen, Bildbibliotheken", "V", "M", True,
  ["CE-INST-017", "CE-INST-018", "CE-INST-019", "CE-INST-025", "CE-INST-026"], ["WP-I6-001", "WP-I1-102"],
  "Instanz-Einstellungen General, SMTP mit Test-E-Mail, AI-Einstellungen (OpenAI-kompatibler Endpunkt, lokal betreibbar) und Unsplash; Secrets maskiert (`MaskInstanceSecrets = true`).",
  fe=["`frontend/libs/admin/instance`"], be=["`src/modules/Instance/Funk.Instance`"],
  arch=["05 §4.4", "11 §3.13, §3.17", "04 §4.2", "17 Z-112"])

W("WP-I6-003", "God Mode: Workspace-Liste, Workspace-Anlage sperren, Workspace anlegen, Willkommens-Popup", "V", "M", True,
  rng("CE-INST", 27, 30), ["WP-I6-001"],
  "Workspace-Verwaltung der Instanz.",
  fe=["`frontend/libs/admin/workspace`"], be=["`src/modules/Instance/Funk.Instance`", "`src/modules/Workspaces/Funk.Workspaces.Contracts`"], arch=["04 §4.2", "08 §4.2"])

W("WP-I6-004", "Projekt veröffentlichen (Publish-Modal, Board-Einstellungen, Metadaten)", "V", "M", True,
  ["CE-SPACE-001", "CE-SPACE-002"], [M5],
  "Publish-Modal im Web und Board-Einstellungen/-Metadaten (`deploy_boards`, Anchor als 32-Zeichen-Hex).",
  be=["`src/modules/PublicSpace/Funk.PublicSpace`, `Funk.PublicSpace.Contracts`"], fe=["`frontend/libs/web/project-publish`"],
  arch=["04 §4.18", "03 §3.4.15"])

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
  be=["`src/modules/PublicSpace/Funk.PublicSpace` (`/api/public/`)"], fe=["`frontend/libs/space/issues`, `frontend/libs/space/views`"], arch=["04 §4.18", "08 §4.3, §4.6"])

W("WP-I6-007", "Space: öffentliches Issue-Detail, Peek, Kommentarbilder/Asset-Auslieferung, Mentions (ED-6)", "V", "M", True,
  ["CE-SPACE-004", "CE-SPACE-007", "CE-SPACE-024", "CE-SPACE-030"], ["WP-I6-006"],
  "Issue-Detail und Peek mit Rich-Editor read-only, Space-Datei-Handler (Anchor-Asset-URLs) und Space-Mentions.",
  fe=["`frontend/libs/space/editor`, `frontend/libs/space/issues`"], be=["`src/modules/Assets/Funk.Assets` (Space-Auslieferung)"],
  arch=["10 §1.5 (ED-6)", "04 §4.13, §4.18"])

W("WP-I6-008", "Space-Interaktionen: Kommentare, Reaktionen, Votes, öffentliche Intake-Einreichung", "V", "M", True,
  ["CE-SPACE-006", "CE-SPACE-025", "CE-SPACE-026", "CE-SPACE-027", "CE-SPACE-028"], ["WP-I6-007"],
  "Öffentliche Kommentare (Lite-Editor mit Bild-Upload), Kommentar- und Work-Item-Reaktionen, Up-/Downvotes (Keycloak-Anmeldung erforderlich) und die öffentliche Intake-Einreichung (nur API).",
  be=["`src/modules/PublicSpace/Funk.PublicSpace`", "`src/modules/Intake/Funk.Intake` (öffentliche Einreichung)"], fe=["`frontend/libs/space/issues`"],
  arch=["04 §4.9, §4.18", "00 ADR-008 (Space)"])

W("WP-I6-016", "API-Tokens: Liste, Anlage, Löschung", "V", "M", True,
  rng("CE-WH", 12, 14), [M5],
  "Persönliche API-Tokens (`funk_api_`-Präfix) mit Liste, Anlage (einmalige Anzeige) und Löschung.",
  be=["`src/modules/Identity/Funk.Identity` (ApiTokens)"], fe=["`frontend/libs/web/settings` (api-token)"], arch=["05 §3.12.3", "04 §4.1"])

W("WP-I6-009", "Public API v1: API-Key-Authentifizierung, Rate-Limit je Key, Aktivitätsprotokoll, OpenAPI, aktueller Benutzer", "B", "M", False,
  rng("CE-API", 1, 5), ["WP-I6-016", "WP-I6-201"],
  "Oberfläche `/api/v1/` mit `X-Api-Key`, Rate-Limit je Key, API-Activity-Log (Queue), OpenAPI (Scalar offline, Default aus, im God Mode einschaltbar, Z-112) und `GET …/users/me/`.",
  be=["`src/modules/PublicApi/Funk.PublicApi`", "`tests/modules/Funk.PublicApi.Tests`"], arch=["04 §3.11, §3.14, §4.19", "05 §3.12", "06 O-D06-08"],
  ak=["`OpenApiDocumentTests` gegen `v1.original.json`; LT-10 im Zielbereich."])

W("WP-I6-010", "Public API v1: Projekte, Archiv, Summary, States, Labels, Mitglieder, Einladungen", "B", "L", True,
  rng("CE-API", 6, 13), ["WP-I6-009"],
  "v1-Adapter auf die Contracts-Commands der Fachmodule (R6), inkl. HARM-03/-04/-06.",
  be=["`src/modules/PublicApi/Funk.PublicApi`"], arch=["04 §4.19, §5.3", "05 §3.18.1"])

W("WP-I6-011", "Public API v1: Stickies, User-Assets, Generic Workspace Assets", "B", "S", True,
  rng("CE-API", 14, 16), ["WP-I6-009"],
  "v1-Endpunkte für Stickies und Assets.",
  be=["`src/modules/PublicApi/Funk.PublicApi`"], arch=["04 §4.19"])

W("WP-I6-012", "Public API v1: Work Items, Identifier, Suche, Links, Kommentare, Aktivitäten, Anhänge, Relationen, Intake", "B", "L", True,
  rng("CE-API", 17, 25), ["WP-I6-010"],
  "v1-Work-Item-Endpunkte inkl. Alias-Routen `issues`/`work-items`, State-Wechsel mit Origin `PublicApi`.",
  be=["`src/modules/PublicApi/Funk.PublicApi`"], arch=["04 §4.19, R-D04-07", "11 §3.7", "16 §5.9"])

W("WP-I6-013", "Public API v1: Cycles, Work Items in Cycles, Transfer, Cycle-Archiv, Modules, Work Items in Modulen, Modul-Archiv", "B", "M", True,
  rng("CE-API", 26, 32), ["WP-I6-012"],
  "v1-Endpunkte für Cycles und Module.",
  be=["`src/modules/PublicApi/Funk.PublicApi`"], arch=["04 §4.19"])

W("WP-I6-014", "Webhook-Verwaltung: Liste, Anlage, Secret anzeigen/regenerieren/herunterladen, Bearbeitung, Löschung", "V", "M", True,
  rng("CE-WH", 2, 6), [M5],
  "Settings-Seiten für Webhooks mit Secret-Verwaltung (`funk_wh_`-Präfix).",
  be=["`src/modules/Webhooks/Funk.Webhooks`"], fe=["`frontend/libs/web/settings` (web-hooks)"], arch=["04 §4.20", "03 §3.4.16"])

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
  ["CE-AI-001", "CE-AI-002"], [M5],
  "KI-Assistent über `IChatClient` (Microsoft.Extensions.AI, OpenAI-kompatibler Endpunkt, lokal betreibbar) und Unsplash-Suche; beides optional und abschaltbar (ADR-004).",
  be=["`src/modules/Assistant/Funk.Assistant`", "`src/platform/Funk.Platform.Ai`"], fe=["`frontend/libs/web/work-items` (gpt-assistant)", "`frontend/libs/shared/blocks` (image-picker Unsplash-Tab)"],
  arch=["11 §3.13–§3.17, §5.7, §5.8", "04 §4.22", "17 Z-111"])

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
  be=["`src/hosts/Funk.AllInOne`"], arch=["14 §3.13", "07 §1.4 Zeile I7", "17 ABG-019"])

W("WP-I7-104", "Read-Replica-Unterstützung", "B", "S", True,
  ["CE-OPS-010"], [M6],
  "Zweite Verbindung für lesende Endpunkte mit `read_replica: true` laut Endpunktkatalog.",
  be=["`src/building-blocks/Funk.BuildingBlocks.Persistence/ReadReplica/`"], arch=["04 §4 (Spalte `read_replica`)", "14 §3.18"])

W("WP-I7-105", "TLS-Modi und Reverse-Proxy mit automatischem HTTPS (ACME)", "I", "M", True,
  ["CE-OPS-005"], [M6],
  "TLS-Modi des Gateways (aus, eigenes Zertifikat, ACME) und Compose-Profil `acme`; Zertifikatspflicht für Data Protection in Produktion.",
  be=["`src/hosts/Funk.Gateway` (TLS)", "`deploy/compose/` (Profil acme)"], arch=["14 §3.8"],
  note="Abweichung von 15 Anhang B (I0): Das Gateway-Grundrouting ist I0 (WP-I0-103), automatisches HTTPS gehört nach 14 §3.1.2 zu I7 (plan/04 OP-PLAN-03).")

W("WP-I7-106", "Helm-Chart deploy/helm/funk", "I", "M", True,
  [], [M6],
  "Helm-Chart mit allen Diensten, Keycloak (Deployment für Einzelknoten, Operator-Hinweis für HA), Secrets und `NOTES.txt` (G-BRAND).",
  be=["`deploy/helm/funk/`"], arch=["14 §3.12, O-14-08"], ak=["`helm lint`, `helm template | kubeconform` und Kind-Smoke grün."])

W("WP-I7-107", "Airgapped-Bundle und Egress-gesperrter E2E-Lauf", "I", "M", True,
  [], [M6],
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
  be=["`tests/load/`"], arch=["15 §3.12", "06 §1.3 Zeile I7", "05 R-06"])

W("WP-I7-110", "Paritäts-Gesamtabnahme aller Screens, Endpunkt-Abdeckung 100 %, Abweichungsliste", "I", "M", False,
  [], [M6, "WP-I7-107", "WP-I7-108"],
  "Visual-/DOM-Abnahme aller Einträge des Screenshot-Katalogs (09 §4.14), `coverage --fail-under 100` für Endpunkte, konsolidierte Abweichungsliste (`deviations.yaml`, `ui-deviations.yaml`, `BRAND-*`) zur Abnahme durch den Auftraggeber.",
  arch=["15 §3.10, §3.16 Zeile I7", "09 §3.14.8", "04 §4.29"])

W("WP-I7-201", "Erweiterungspunkte stabilisieren: Contract-Snapshots aller Erweiterungs-Interfaces, Airgap-Test mit Forgejo", "X", "S", True,
  [], [M6],
  "C#-Snapshot per `PublicApiGenerator` + Verify (`ExtensionContractsSnapshotTests`), TS-Snapshot per `api-extractor` von `libs/web/extensions/public-api.ts`, Airgap-Lauf mit gebündeltem Forgejo.",
  be=["`tests/Funk.ArchitectureTests/ExtensionContractsSnapshotTests.cs`"], fe=["`frontend/libs/web/extensions/api-report.md`"],
  arch=["16 D16-ADR-07, §1.4 Zeile I7, §7"],
  ep="16 §1.4 Zeile I7; 16 §4.6 (Träger CE-OPS-023)",
  ak=["Jede nicht additive Änderung an einem Erweiterungs-Interface bricht den Snapshot-Test."])

W("WP-I7-999", "Abnahme I7 – CE-Release-Kandidat (G5 + G6)", "A", "S", False,
  [], ["WP-I7-%03d" % i for i in range(101, 111)] + ["WP-I7-201"],
  "Inkrement-Abnahme I7 und Release-Gate G6 – Meilenstein M7 (CE-Release).",
  arch=["plan/01-roadmap-ce.md §4 (M7)", "15 §3.15.1 (G6)"],
  ak=["Alle Abnahmekriterien M7 erfüllt; `docs/acceptance/I7.md` und Release-Bericht generiert."], tests=["G5 `--inc I7`, G6."])
