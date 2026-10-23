# -*- coding: utf-8 -*-
"""Arbeitspakete I1–I3 (siehe wp_spec.py)."""
from wp_spec import W, rng

# =====================================================================================
# I1 – Workspace, Projekte, Konto
# =====================================================================================
M0 = "WP-I0-999"

W("WP-I1-101", "Messaging produktiv: Retry, Dead-Letter, Worker-Pools, Beat-Plan, Soft-/Hard-Delete, Retention", "B", "M", True,
  ["CE-OPS-014", "CE-OPS-015", "CE-OPS-016"], [M0, "WP-I0-912"],
  "Job-Queue mit Retry-Policies, Dead-Letter, benannten Worker-Pools (`Funk:Worker:Queues`), Scheduler mit Leader-Lock und dem vollständigen Cron-Plan (11 übernommene Original-Einträge mit identischer UTC-Zeit, 7 neue), Soft-Delete-Kaskaden-Registry, Hard-Delete inkl. Objektspeicher-Dateien und Retention-Jobs.",
  be=["`src/building-blocks/Funk.BuildingBlocks.Messaging` (Retry, DLQ, Pools)", "`src/hosts/Funk.Worker`", "`src/building-blocks/Funk.BuildingBlocks.Persistence/SoftDelete/`", "`tests/Funk.Worker.Tests` (`CronRegistrationTests`)"],
  arch=["06 §3.5, §3.6, §3.16, §4.2, D06-ADR-06…-08, -18", "03 §3.5", "02 §3.2"],
  ak=["`CronRegistrationTests`: 11 Original-Einträge mit identischer UTC-Zeit, B3/B13 als entfallen, 7 neue Einträge (AK-D06-05).",
      "Kaskaden-Registry deckt 03 §3.5.4 vollständig ab (`SoftDeleteRegistryTests`).",
      "Hard-Delete löscht nach `HARD_DELETE_AFTER_DAYS` auch die Objektspeicher-Dateien (DEV-OPS-002)."])

W("WP-I1-102", "Mail-Plattform: MailKit, Fluid-Templates, Mailpit, G-MAIL", "B", "M", True,
  [], [M0, "WP-I1-101"],
  "Versand über MailKit, Templates als 1:1-Port der Django-Templates nach Liquid (Fluid) mit `DjangoHtmlEncoder`, gebrandete Betreffzeilen und Logos (CID-Inline), Mailpit im Dev/Test, Golden-Tests G-MAIL. Templates M5, M7, M8, M9 in diesem Inkrement.",
  be=["`src/platform/Funk.Platform.Mail` (`IMailSender`, `MailTemplateRenderer`, `Templates/**.liquid`, `Assets/logo-{white,dark}.png`)", "`tests/Funk.Platform.Tests/Mail/`"],
  arch=["06 §3.13, §4.9, §5.11, D06-ADR-13, -14, -24, -25", "15 §3.7 (G-MAIL)", "17 ABG-105"],
  orig=["`apps/api/templates/emails/`", "`apps/api/plane/bgtasks/`(Mail-Tasks)"],
  ak=["G-MAIL: HTML normalisiert gleich, Text-Teil byte-gleich zur gebrandeten Original-Referenz je Template; keine externen Bild-URLs (BRAND-MAIL-05).",
      "Sprache der Mails nach Entscheidung OP-PLAN-05 (plan/04) – bis dahin Englisch wie Original."])

W("WP-I1-103", "Objektspeicher, Datei-Assets und Uploads mit Fortschritt (Image-Picker)", "V", "M", True,
  ["CE-OPS-012", "CE-OPS-013", "CE-UIX-009"], [M0, "WP-I0-908", "WP-I0-913"],
  "`IObjectStorage` (S3/Dateisystem), Upload-Policy (Presigned POST bzw. Proxy-Modus nach S8), `file_assets` mit Bestätigung, Metadaten-Job und Cleanup unbestätigter Assets, Gateway-Routen `/uploads`, Frontend Image-Picker und Upload-Fortschritt.",
  be=["`src/platform/Funk.Platform.Storage`", "`src/modules/Assets/Funk.Assets`, `Funk.Assets.Contracts`", "`src/hosts/Funk.Gateway` (Upload-Routen)", "`tests/modules/Funk.Assets.Tests`"],
  fe=["`frontend/libs/web/core/assets`", "`frontend/libs/shared/blocks` (image-picker)"],
  arch=["04 §4.13", "03 §3.4.11", "05 §3.17.4", "14 §3.7.6", "06 §1.3 Zeile I1"],
  ak=["`ObjectStorageContractTests` grün für Default-Backend und Dateisystem; Upload > Limit → 413/Original-Fehler; MIME-/Größenprüfung wie 05 §3.17.4."])

W("WP-I1-104", "Valkey: HybridCache L2, verteilte Rate-Limits, TLS", "I", "S", True,
  ["CE-OPS-011"], [M0],
  "Valkey als optionale Ressource: HybridCache-L2 mit Tag-Invalidierung, verteilte Rate-Limiter, TLS-Verbindung (`rediss://`); Einzelknoten-Profil ohne Valkey bleibt lauffähig (O-05).",
  be=["`src/platform/Funk.Platform.Caching`", "`src/building-blocks/Funk.BuildingBlocks.Web/RateLimiting/`", "`tests/Funk.Platform.Tests/Caching/`"],
  arch=["02 §3.12, §3.13", "14 §3.1.1, §3.9", "01 O-05"],
  ak=["Cache-Tests mit und ohne Valkey; TLS-Verbindung im Testprofil mit selbstsigniertem Zertifikat."])

W("WP-I1-105", "Designsystem-Ausbau: Status-/Prioritäts-Icons, Datei-Icons, Logo-Picker, Illustrationen, Propel-Vollbestand, Blocks", "F", "L", True,
  ["CE-I18N-014", "CE-I18N-015", "CE-I18N-016", "CE-I18N-018", "CE-I18N-019", "CE-I18N-020"], [M0],
  "Alle 68 Propel-Komponenten und 57 Elemente, die Blocks-Composites (außer Charts), State-/Cycle-/Modul-/Prioritäts-Icons, Datei-Typ-Icons und Locked-Pill, Logo-Picker (Emoji, Lucide, Material) und die 59 Empty-State-Illustrationen inkl. theme-abhängiger Assets stehen in der Galerie DOM- und pixelgleich.",
  fe=["`frontend/libs/shared/propel` (Vollbestand)", "`frontend/libs/shared/blocks`", "`frontend/libs/shared/propel/state-icons`"],
  arch=["09 §4.2–§4.13, §3.7, §3.8, §3.11", "09 §7.3 (DoD je Baustein)"],
  ak=["Jede Komponente aus 09 §4.2/§4.3/§4.7 hat einen Galerie-Eintrag mit allen Varianten; DOM-Vertrag = Referenz-Galerie; Visual ≤ 0,1 %.",
      "Emoji-Daten offline gebündelt; `emojibase-data`-Version beim ersten `capture-reference`-Lauf festgeschrieben (Z-04)."])

W("WP-I1-201", "Erweiterungspunkt A17: IStateCatalog/ILabelCatalog als einzige Lesewege, Catalog-Sources", "X", "S", False,
  [], [M0],
  "States und Labels werden von allen Modulen ausschließlich über `IStateCatalog`/`ILabelCatalog` gelesen; Quellen `IStateCatalogSource`/`ILabelCatalogSource` (E-21, CE: Projekt-Quelle Order 100); `IScopedCatalogEntry` an `State`/`Label`.",
  be=["`src/modules/Projects/Funk.Projects.Contracts/Catalogs/`", "`src/modules/Projects/Funk.Projects/Catalogs/ProjectStateCatalogSource.cs`"],
  arch=["16 §5.2, §3.3.0 E-21", "02 §5.2.4", "01 §1.4 Zeile A17"],
  ep="01 §1.4 A17; 16 §3.3.0 E-21; 16 §4.6 (Träger CE-PRJ-023…033)",
  ak=["Architekturtest: kein Modul außer `Funk.Projects` greift direkt auf `states`/`labels` zu.",
      "Fake-Quelle (Order 50) liefert zusätzliche Workspace-States ohne CE-Änderung (Typ X)."])

W("WP-I1-202", "Erweiterungspunkt Feature-Kataloge: IProjectFeatureCatalog, IWorkspaceFeatureCatalog, Contributors, PROJECT_FEATURES", "X", "S", False,
  [], [M0],
  "Projekt- und Workspace-Feature-Toggles laufen über Kataloge (E-01, E-26) mit Tabellen `project_feature_settings`/`workspace_feature_settings` und `IProjectPayloadExtension`; Frontend-Tokens `PROJECT_FEATURES`/`WORKSPACE_FEATURES` (E-02, CE: `PROJECT_FEATURES_LIST` des Originals).",
  be=["`src/modules/Projects/Funk.Projects.Contracts/Features/`", "`src/modules/Workspaces/Funk.Workspaces.Contracts/Features/`"],
  fe=["`frontend/libs/web/extensions/src/features.ts`"],
  arch=["16 §3.2.6, §5.1, §3.3.0 E-01/E-02/E-26, D16-ADR-05"],
  ep="16 §3.3.0 E-01, E-02, E-26; 16 §4.6 (Träger CE-PRJ-019, CE-PRJ-020)",
  ak=["Die fünf CE-Toggles (`cycle_view`, `module_view`, `issue_views_view`, `page_view`, `intake_view`) verhalten sich wie das Original (Contract-Golden des Projekt-Payloads unverändert).",
      "Fake-Contributor fügt einen Schalter hinzu, der in der Settings-Liste erscheint und im Payload ausgegeben wird – ohne CE-Änderung (Typ X)."])

W("WP-I1-203", "Erweiterungspunkte UI-Registries I1: SETTINGS_PAGES, SIDEBAR_ITEMS (dynamisch), FAVORITE_ENTITY_RENDERERS, MEMBER_ROW_DECORATORS, ROLE_OPTIONS, GLOBAL_MODALS, ESTIMATE_SYSTEM_FLAGS", "X", "S", False,
  [], [M0],
  "Die Frontend-Registries des Inkrements I1 sind gebaut und von der CE selbst befüllt (Original-Einträge), sodass Pakete Settings-Seiten, Sidebar-Einträge, Favoriten-Typen, Mitgliederzeilen-Dekoratoren, Rollenoptionen, globale Modals und Estimate-Systeme additiv ergänzen.",
  fe=["`frontend/libs/web/extensions/src/{settings,sidebar,favorites,members,roles,modals,estimates}.ts`"],
  arch=["08 §6.1, §6.4, §6.5", "16 §3.3.0 E-14 (I1-Teil), §1.4 Zeile I1", "17 ABG-030"],
  ep="16 §1.4 Zeile I1; 16 §4.6 (Träger CE-WS-023, CE-WS-010, CE-PRJ-019, CE-PRJ-034/-035)",
  ak=["`extension-registry-check` meldet für jede Registry CE-Einträge und einen Fake-Eintrag-Test (Typ X)."])

W("WP-I1-204", "Erweiterungspunkt Activity-Grundgerüst: IActivityRecorder, IActivityFieldResolver-Registry, reservierte Felder", "X", "S", False,
  [], [M0, "WP-I0-201"],
  "Activity-Pipeline-Gerüst (synchron in derselben Transaktion, Event `funk.work_item_activity.recorded.v1`), Registry `IActivityFieldResolver`, reservierte Activity-Feldnamen (16 §3.2.3); Referenzbeitrag `LabelActivityFieldResolver`.",
  be=["`src/modules/WorkItems/Funk.WorkItems.Contracts/Services/IActivityRecorder.cs`", "`src/modules/Projects/Funk.Projects/Activity/LabelActivityFieldResolver.cs`"],
  arch=["06 §3.9, §5.6, D06-ADR-09", "02 §3.19, §5.2.10, D02-ADR-25", "16 §3.2.3"],
  ep="16 §1.4 Zeile I1; 16 §4.6 (Träger CE-WI-039/-040, Gerüst ab I1)",
  ak=["Fake-Field-Resolver liefert Anzeigewerte für ein Paketfeld ohne CE-Änderung (Typ X); reservierte Feldnamen kollidieren nicht (Kollisionstest)."])

W("WP-I1-205", "Erweiterungspunkte IInstanceConfigKeyProvider und B1-Schema-Vorhalte (teamspace_id)", "X", "S", True,
  [], [M0],
  "Zusätzliche Instanz-Konfigurationsschlüssel über `IInstanceConfigKeyProvider` (E-12, ersetzt `instance_config_variables/extended.py`); nullable Spalten `teamspace_id` in den in 16 §3.3 B1 genannten Tabellen (Views, Pages, Kommentare) per Migration.",
  be=["`src/modules/Instance/Funk.Instance.Contracts/IInstanceConfigKeyProvider.cs`", "`src/data/Funk.Data/Migrations/…_Teamspaces_ScopeColumns`"],
  arch=["16 §3.3.0 E-12, §3.3.2 (B1), §5.4", "02 §4.10", "01 §1.4 Zeile B1 (ABG-058)"],
  ep="16 §3.3.0 E-12; 01 §1.4 B1 (I1-Teil); 16 §4.6 (Träger CE-INST-002)",
  ak=["Fake-Key-Provider ergänzt einen Instanz-Key, der in `GET /api/instances/` (Admin) erscheint – ohne CE-Änderung (Typ X).",
      "Spalten `teamspace_id` existieren nullable, werden in CE-Verträgen nicht ausgegeben (Contract-Goldens unverändert)."])

W("WP-I1-001", "Workspace-Einstellungen (General, Löschen, Settings-Rahmen, Stammdatenlisten, Themes-API)", "V", "M", True,
  ["CE-WS-003", "CE-WS-004", "CE-WS-006", "CE-WS-007", "CE-WS-024"], [M0, "WP-I1-203", "WP-I1-103"],
  "Workspace-Settings-Rahmen mit Navigation (über `SETTINGS_PAGES`), Seite General (Name, Logo, Organisationsgröße), Workspace löschen mit Bestätigung, workspace-weite Stammdatenlisten und die Themes-API.",
  be=["`src/modules/Workspaces/Funk.Workspaces`"], fe=["`frontend/libs/web/workspace`, `frontend/libs/web/settings`"],
  arch=["04 §4.3", "03 §3.4.3", "08 §4.1", "09 §4.14"])

W("WP-I1-002", "Mitglieder, Rollen, Einladungen (inkl. automatischer Beitritt beim Login)", "V", "L", True,
  ["CE-WS-008", "CE-WS-009", "CE-WS-010", "CE-WS-011", "CE-WS-012", "CE-AUTH-028"], [M0, "WP-I1-102", "WP-I1-203"],
  "Rollen- und Berechtigungsmodell Admin/Member/Guest, Mitgliederverwaltung, Einladungen per E-Mail (Template M5), Annehmen/Ablehnen, eigene Mitgliedschaft und Rollen-Maps; offene Einladungen werden beim ersten Keycloak-Login über die E-Mail-Adresse zugeordnet (Provisioning-Schritt).",
  be=["`src/modules/Workspaces/Funk.Workspaces` (Members, Invitations)", "`src/modules/Identity/Funk.Identity/Provisioning/AcceptPendingInvitationsStep.cs`"],
  fe=["`frontend/libs/web/workspace` (members, invitations)", "`frontend/apps/web/src/pages/(all)/invitations/`"],
  arch=["04 §4.3", "05 §3.7.5, §3.13, §3.18.1", "06 §3.13", "03 §3.4.3"],
  ak=["Permission-Matrix-Tests für alle Mitglieder-/Einladungs-Endpunkte inkl. HARM-00 (WS-Admin-Override) grün.",
      "Einladungs-Mail (M5) besteht G-MAIL; Annahme über Link und automatische Zuordnung beim Login führen zur gleichen Mitgliedschaft."])

W("WP-I1-003", "Shell-Ergänzungen und Navigation: Hilfe-Menü, What's new, Star-Link, Sidebar „More“, Customize navigation", "V", "M", True,
  ["CE-WS-014", "CE-WS-015", "CE-WS-017", "CE-WS-021", "CE-WS-022"], [M0, "WP-I1-203"],
  "Hilfe-Menü, Changelog (What's new) und Star-Link mit konfigurierbaren bzw. entfallenden externen Zielen (ADR-004, ADR-009B), erweiterte Sidebar „More“ mit Pin/Sortierung und „Customize navigation“ mit Persistenz.",
  be=["`src/modules/Workspaces/Funk.Workspaces` (Sidebar-Präferenzen)"], fe=["`frontend/libs/web/core/sidebar`, `frontend/libs/web/core/navigation`"],
  arch=["08 §4.1, §3.16 (Branding)", "09 §4.11.1", "00 ADR-009B (externe Links)"],
  ak=["Kein Link zeigt auf plane.so, docs.plane.so oder Plane-GitHub (G-BRAND, `no-external-urls`); nicht konfigurierte Ziele blenden den Eintrag aus (dokumentiert in `ui-deviations.yaml`)."])

W("WP-I1-004", "Favoriten mit Ordnern", "V", "M", True,
  ["CE-WS-023"], ["WP-I1-005", "WP-I1-203"],
  "Favoriten (Projekte, Views, Cycles, Module, Pages) mit Ordnern, Drag-and-Drop-Sortierung und Sidebar-Darstellung über `FAVORITE_ENTITY_RENDERERS`; Entitätstypen späterer Inkremente werden mit deren Schnitt registriert.",
  be=["`src/modules/Workspaces/Funk.Workspaces` (Favorites)"], fe=["`frontend/libs/web/favorites`"],
  arch=["04 §4.3", "03 §3.4.3", "08 §4.5 (favorite.store)"])

W("WP-I1-005", "Projektliste, Projektkarten, Projekt-Statistiken", "V", "M", True,
  ["CE-PRJ-001", "CE-PRJ-002", "CE-PRJ-003"], [M0, "WP-I1-105"],
  "Projektliste mit Filtern/Sortierung/Suche, Projektkarten (Cover, Logo, Mitglieder, Beitreten) und Projekt-Statistiken.",
  be=["`src/modules/Projects/Funk.Projects`"], fe=["`frontend/libs/web/project`"],
  arch=["04 §4.4", "03 §3.4.4", "02 §3.10 (Cursor-Paginator)"])

W("WP-I1-006", "Projekt-Detail, Zugriffsschutz, Beitreten/Verlassen, Projekt-Einladungen per E-Mail", "V", "M", True,
  ["CE-PRJ-006", "CE-PRJ-007", "CE-PRJ-010"], ["WP-I1-002", "WP-I1-005"],
  "Projekt-Detail mit `ProjectAuthWrapper` (Zugriff je Rolle/Netzwerk), Beitreten/Verlassen öffentlicher Projekte; die im Original defekte Projekt-Einladung per E-Mail wird repariert (DT-PRJ-01: 500 → 200 + Mail, O-D04-05).",
  be=["`src/modules/Projects/Funk.Projects`"], fe=["`frontend/libs/web/project`", "`frontend/libs/web/core/wrappers/project-auth-wrapper`"],
  arch=["04 §4.4, §3.13 (DT-PRJ-01)", "05 §3.13", "08 §3.3.4"],
  ak=["Contract-Szenario `projects/project-invitations.yaml` mit `golden_source: target` und Abweichung DEV-API-… (04 §5.7) grün."])

W("WP-I1-007", "Projekt archivieren/wiederherstellen und löschen", "V", "S", True,
  ["CE-PRJ-008", "CE-PRJ-009"], ["WP-I1-005", "WP-I1-101"],
  "Archivieren und Wiederherstellen von Projekten sowie Löschen mit Soft-Delete-Kaskade (Deferred für Projekt-Wurzel).",
  be=["`src/modules/Projects/Funk.Projects`"], fe=["`frontend/libs/web/project`, `frontend/libs/web/archives`"],
  arch=["04 §4.4", "03 §3.5.4", "02 R-D02-04"])

W("WP-I1-008", "Projekt-Sidebar, Kontextmenü, erweiterte Sidebar, Feature-Navigation, Tabs", "V", "M", True,
  ["CE-PRJ-011", "CE-PRJ-012", "CE-PRJ-013", "CE-PRJ-014", "CE-PRJ-015"], ["WP-I1-005", "WP-I1-202"],
  "Projektliste in der Sidebar mit Kontextmenü und Sortierung, erweiterte Projekt-Sidebar, Feature-Navigation je aktiviertem Feature (über `PROJECT_FEATURES`) und Tab-Navigation (TABBED).",
  fe=["`frontend/libs/web/project` (sidebar)", "`frontend/libs/web/core/sidebar`"],
  arch=["08 §4.1, §4.4", "16 §3.2.6"],
  note="Feature-Einträge erscheinen erst, wenn der Ziel-Screen abgenommen ist (01 §7.19); bis I4 sind z. B. Pages/Intake/Cycles ausgeblendet.")

W("WP-I1-009", "Projekt-Settings-Rahmen, General, Benutzerpräferenzen", "V", "M", True,
  ["CE-PRJ-016", "CE-PRJ-017", "CE-PRJ-018"], ["WP-I1-005", "WP-I1-203"],
  "Projekt-Settings-Rahmen mit Navigation (über `SETTINGS_PAGES`), Seite General (Name, Identifier, Beschreibung, Cover, Logo, Netzwerk, Zeitzone) und Projekt-Benutzerpräferenzen.",
  be=["`src/modules/Projects/Funk.Projects`"], fe=["`frontend/libs/web/project-settings`"],
  arch=["04 §4.4", "03 §3.4.4", "08 §4.1"])

W("WP-I1-010", "Projekt-Features (Toggles), Disabled-Zustände, Projektmitglieder, Gastzugriff", "V", "M", True,
  ["CE-PRJ-019", "CE-PRJ-020", "CE-PRJ-021", "CE-PRJ-022"], ["WP-I1-009", "WP-I1-202", "WP-I1-002"],
  "Feature-Toggles über den Feature-Katalog, Disabled-Feature-Zustände, Projektmitglieder verwalten und `guest_view_all_features`.",
  be=["`src/modules/Projects/Funk.Projects`"], fe=["`frontend/libs/web/project-settings`"],
  arch=["04 §4.4", "05 §3.14 (Gast-Sichtbarkeit)", "16 §3.2.6"])

W("WP-I1-011", "States: Gruppen, Anlage/Bearbeitung, Reihenfolge per DnD, Default-State, Löschen", "V", "M", True,
  ["CE-PRJ-023", "CE-PRJ-024", "CE-PRJ-025", "CE-PRJ-026", "CE-PRJ-027"], ["WP-I1-009", "WP-I1-201", "WP-I0-913"],
  "State-Verwaltung nach dem Muster des Referenzmoduls (02 §5.2) über `IStateCatalog`.",
  be=["`src/modules/Projects/Funk.Projects` (States)"], fe=["`frontend/libs/web/project-settings` (project-states)"],
  arch=["04 §4.4", "03 §3.4.4", "02 §5.2", "16 §5.2"])

W("WP-I1-012", "Labels – Referenzmodul (Hierarchie, Anlage, DnD-Gruppierung, Löschen, Bulk-Import)", "V", "M", True,
  ["CE-PRJ-028", "CE-PRJ-029", "CE-PRJ-030", "CE-PRJ-031", "CE-PRJ-032", "CE-PRJ-033"], ["WP-I1-009", "WP-I1-201", "WP-I1-204", "WP-I0-913"],
  "Vollständige Umsetzung des in 02 §5.2 ausgearbeiteten Referenzmoduls Labels – Vorlage für alle weiteren Module (Dateinamen, Commands, Validatoren, Endpunkte, Activity-Beitrag, Tests).",
  be=["`src/modules/Projects/Funk.Projects` (Label*, siehe 02 §5.2.1–§5.2.13)", "`tests/modules/Funk.Projects.Tests` (02 §5.2.13)"],
  fe=["`frontend/libs/web/project-settings` (labels)", "`frontend/tools/contract-check/checks/labels.check.ts`"],
  arch=["02 §5.2 (vollständig)", "04 §4.4, §5.7, §5.8", "03 §3.4.4", "15 §3.6.2 (Szenario labels-crud)"],
  ak=["Code entspricht den Skeletten 02 §5.2 (Review-Checkliste); O-D02-05 (View-Filter-Bereinigung) im Harness geprüft und entschieden."])

W("WP-I1-013", "Estimates: Einstellungen, Schätzsystem anlegen/ändern/löschen, Validierung", "V", "M", True,
  ["CE-PRJ-034", "CE-PRJ-035", "CE-PRJ-036", "CE-PRJ-037", "CE-PRJ-038"], ["WP-I1-009", "WP-I1-203"],
  "Estimates-Einstellungen mit Schätzsystemen (Punkte, Kategorien; Zeit über `ESTIMATE_SYSTEM_FLAGS` aus), Schätzwert-Validierung, Ändern/Löschen von Punkten und Systemen.",
  be=["`src/modules/Projects/Funk.Projects` (Estimates)"], fe=["`frontend/libs/web/project-settings` (estimates)"],
  arch=["04 §4.4", "03 §3.4.4", "16 §3.3.0 E-14"])

W("WP-I1-014", "Profil und persönliche Einstellungen (inkl. angepasster E-Mail-Änderung und Konto-Deaktivierung)", "V", "M", True,
  ["CE-PROF-001", "CE-PROF-002", "CE-PROF-003", "CE-PROF-004", "CE-PROF-005", "CE-PROF-006"], [M0, "WP-I1-103"],
  "Profil-Datenmodell, Profil-Einstellungen (Modal und Seite), Profil bearbeiten, Sprache/Zeitzone/Wochenstart; E-Mail-Änderung öffnet die Keycloak-Kontokonsole (DEV-UI-04), Konto deaktivieren wirkt in funk., Sperre in Keycloak.",
  be=["`src/modules/Identity/Funk.Identity` (Profile, Preferences)"], fe=["`frontend/libs/web/profile`"],
  arch=["05 §3.10, §4.1, D05-ADR-08", "04 §4.1", "03 §3.4.1"])

W("WP-I1-015", "Onboarding", "V", "M", True,
  ["CE-AUTH-030"], ["WP-I1-014", "WP-I1-002"],
  "Onboarding-Ablauf nach dem ersten Login (Profil, Workspace anlegen oder Einladung annehmen) wie Original, ohne Passwortschritt.",
  be=["`src/modules/Identity/Funk.Identity`"], fe=["`frontend/libs/web/auth` (onboarding)"],
  arch=["05 §4.1", "08 §4.1"])

W("WP-I1-016", "Rate-Limits gegen Brute-Force und Missbrauch", "B", "S", True,
  ["CE-AUTH-026"], ["WP-I1-104"],
  "Rate-Limit-Policies (`anon`, `user`, Callback-Limiter `AuthCallbackRateLimiter`, Integrations) mit Original-Grenzwerten und Header-Verhalten.",
  be=["`src/building-blocks/Funk.BuildingBlocks.Web/RateLimiting/`", "`src/modules/Identity/Funk.Identity/Authentication/AuthCallbackRateLimiter.cs`"],
  arch=["05 §3.17.6", "02 §3.13, O-D02-07", "04 §3.12"],
  ak=["`RateLimitPolicyTests` inkl. `Callback_11thRequest_Redirects5900`; Grenzwert ±1 gegen Original (DEV-RL-001)."])

W("WP-I1-017", "Sprachen de/en, Übersetzungen mit Fallback/ICU, Datums-/Zeitdarstellung, Zeitzonen", "F", "M", True,
  ["CE-I18N-001", "CE-I18N-002", "CE-I18N-003", "CE-I18N-004"], ["WP-I1-014"],
  "Sprachauswahl (nur Deutsch und Englisch, Standard Deutsch, ADR-009D) mit Server-Persistenz, `TranslationService` mit Fallback und ICU-Plural, deutsche Texte aus `packages/i18n/src/locales/de` gebrandet (BR-10) und fehlende Schlüssel ergänzt; Datums-/Zeitdarstellung und Zeitzonen-Umrechnung wie Original.",
  fe=["`frontend/libs/shared/i18n` (`locales/de`, `locales/en`, `brand/{de,en}.json`)", "`frontend/tools/i18n-sync-check`"],
  arch=["08 §3.7, §5.13, O-D08-08", "00 ADR-009D", "17 Z-113"],
  ak=["`i18n-sync-check`: jeder in `en` vorhandene Schlüssel existiert in `de` (fehlende ergänzt, Liste in `ui-deviations.yaml`); Sprachauswahl zeigt genau zwei Sprachen.",
      "Datumsformat nach Entscheidung OP-PLAN-06 (plan/04)."])

W("WP-I1-018", "Themes: Varianten, Auswahl mit Server-Persistenz, Custom Theme, High Contrast, Farb-Tokens", "F", "M", True,
  ["CE-I18N-005", "CE-I18N-006", "CE-I18N-007", "CE-I18N-008", "CE-I18N-009"], ["WP-I1-014"],
  "Theme-System mit hell/dunkel/system, High-Contrast-Varianten, Custom Theme und Server-Persistenz; Farb-Token-System 1:1.",
  fe=["`frontend/libs/shared/theme`", "`frontend/libs/web/settings` (appearance)"],
  arch=["08 §3.8, §5.1", "09 §3.9, §5.8", "17 ABG-031"])

W("WP-I1-019", "UI-Querschnitt 1: Seiten-Header, Breadcrumbs, Leerzustände, Modal-Hosts, Dialog-/Dropdown-Verhalten, Tab-Reihenfolge", "F", "M", True,
  ["CE-UIX-001", "CE-UIX-002", "CE-UIX-003", "CE-UIX-004", "CE-UIX-005"], [M0, "WP-I1-105", "WP-I1-203"],
  "Querschnittliche UI-Bausteine, die alle folgenden Screens verwenden.",
  fe=["`frontend/libs/web/core/{breadcrumbs,empty-state,modals,common}`"],
  arch=["08 §4.10", "09 §3.5"])

W("WP-I1-020", "UI-Querschnitt 2: LocalStorage-Präferenzen, Zwischenablage/CSV, ungespeicherte Änderungen, Fehlerseiten, Stale-Chunk, Legacy-Redirects, Link-Icons", "F", "M", True,
  ["CE-UIX-006", "CE-UIX-007", "CE-UIX-008", "CE-UIX-010", "CE-UIX-011", "CE-UIX-012", "CE-UIX-013"], [M0],
  "Weitere Querschnittsfunktionen des Web-Frontends.",
  fe=["`frontend/libs/shared/cdk`", "`frontend/libs/web/core/{common,lib}`", "`frontend/apps/web/src/pages/routes/redirects/`"],
  arch=["08 §3.3.5, §3.14, §3.15, §4.10, §5.4", "08 O-D08-09"])

W("WP-I1-999", "Abnahme I1 – Workspace, Projekte, Konto (G5)", "A", "S", False,
  [], ["WP-I1-%03d" % i for i in range(1, 21)] + ["WP-I1-101", "WP-I1-102", "WP-I1-103", "WP-I1-104", "WP-I1-105", "WP-I1-201", "WP-I1-202", "WP-I1-203", "WP-I1-204", "WP-I1-205"],
  "Inkrement-Abnahme I1 nach G5 und Meilenstein M1 (plan/01-roadmap-ce.md §4).",
  arch=["plan/01-roadmap-ce.md §4 (M1)", "15 §3.16 Zeile I1"],
  ak=["Alle Abnahmekriterien M1 erfüllt; `docs/acceptance/I1.md` generiert."], tests=["G5 `--inc I1`."])

# =====================================================================================
# I2 – Work Items & Layouts
# =====================================================================================
M1 = "WP-I1-999"

W("WP-I2-101", "Funk.Documents Teil A: Server-Schema, HTML↔PM-JSON, Text-Extraktion, Sanitizing, Yjs-Update-Validierung", "D", "L", True,
  ["CE-OPS-017"], [M0, "WP-I0-902"],
  "Server-Schema aller Nodes/Marks, `HtmlSerializer`, `HtmlParser`, PM-JSON-Modell, `HtmlTextExtractor` (`description_stripped`), `YjsUpdateValidator`, `DocumentReferenceExtractor` (Mentions) und das HtmlSanitizer-Profil (Port von `nh3`) mit Binärprüfung.",
  be=["`src/documents/Funk.Documents`", "`src/platform/Funk.Platform.Security/Sanitizing/`", "`tests/Funk.Documents.Tests`"],
  arch=["07 §1.4 Zeile I2, §3.12, §3.13", "05 §3.17.3, R-08", "15 §3.7 (G-DOC, G-SANITIZE)"],
  orig=["`apps/api/plane/utils/content_validator.py`", "`packages/editor/src/core/extensions/`"],
  ak=["G-DOC (HTML↔JSON) und G-SANITIZE grün; Abweichungen des Sanitizers gegenüber `nh3` mit Begründung in `deviations.yaml`."])

W("WP-I2-102", "SSRF-sicherer HTTP-Client und Link-Crawler", "B", "S", True,
  ["CE-OPS-018"], [M1],
  "`SsrfSafeHttpHandler` mit Ziel-Allowlists, IP-Pinning, ohne Redirects/Proxy; benannte Clients (`webhooks`, `link-crawler`, `integrations`, `forgejo`, `llm`, `unsplash`); Link-Crawler-Job für Work-Item-Links.",
  be=["`src/platform/Funk.Platform.Security/Ssrf/`", "`tests/Funk.Platform.Tests/Ssrf/`"],
  arch=["05 §3.17.2, §5.9", "17 ABG-040"],
  orig=["`apps/api/plane/bgtasks/work_item_link_task.py`", "`apps/api/plane/utils/url.py`"])

W("WP-I2-103", "Dummy-Daten-Generator und Volumen-Seeder (S/M/L/XL)", "I", "S", True,
  ["CE-OPS-024"], ["WP-I2-001"],
  "`funk-cli create-dummy-data` (Port des Management-Commands) und die Volumenprofile aus `tests/seed/volume-profiles.yaml` für Last- und Performancetests.",
  be=["`src/tools/Funk.Cli` (create-dummy-data)", "`tests/seed/volume-profiles.yaml`"],
  arch=["03 §3.15", "15 §3.14.3", "14 §3.1.2 Zeile I2/I3"],
  orig=["`apps/api/plane/db/management/commands/create_dummy_data.py`"])

W("WP-I2-201", "Erweiterungspunkt B6/A1: Filter-AST, Parser-Liste, Feld-/Gruppen-/Sortier-Registries, Payload-Extension, Basismengen-Filter", "X", "M", False,
  [], [M1, "WP-I0-909"],
  "Filter-AST (`FilterExpression` And/Or/Not/Condition) mit erweiterbarem Operator-Katalog als einzige Abfragesprache, `IFilterParser`-Liste (legacy, rich), `IFilterFieldProvider`, `IGroupKeyProvider`, `IOrderKeyProvider`, `IWorkItemPayloadExtension`, `IWorkItemBaseSetFilter` (E-04).",
  be=["`src/modules/WorkItems/Funk.WorkItems.Contracts/Query/`", "`src/modules/WorkItems/Funk.WorkItems/Query/`"],
  arch=["02 §3.11", "16 §5.5, §3.3.0 E-04", "01 §1.4 Zeilen A1, B6"],
  ep="01 §1.4 A1/B6; 16 §3.3.0 E-04; 16 §4.6 (Träger CE-LV-006…010, CE-LV-017, CE-LV-046)",
  ak=["Property-Test: Legacy- und Rich-Parser erzeugen für äquivalente Eingaben denselben AST.",
      "Fake-Feld-Provider ergänzt ein filter-, gruppier- und sortierbares Feld ohne CE-Änderung (Typ X)."])

W("WP-I2-202", "Erweiterungspunkt A1: work_items.type_id, Minimal-Tabelle work_item_types, IWorkItemTypeResolver", "X", "S", False,
  [], [M1],
  "Nullable FK `work_items.type_id` auf die leere Minimal-Tabelle `work_item_types` (`id`, `workspace_id`, `project_id` nullable, `name`, `is_default`, Audit) und `IWorkItemTypeResolver` (E-03, CE liefert `null`).",
  be=["`src/data/Funk.Data/Entities/WorkItems/WorkItemType.cs`", "`src/modules/WorkItems/Funk.WorkItems.Contracts/IWorkItemTypeResolver.cs`"],
  arch=["16 §5.1, §3.3.0 E-03", "01 §1.4 Zeile A1", "03 §3.4.5"],
  ep="01 §1.4 A1; 16 §3.3.0 E-03; 16 §4.6 (Träger CE-WI-001, CE-WI-049)",
  ak=["Contract-Goldens der Work-Item-Payloads unverändert (Feld `type_id` wie Original); Fake-Resolver setzt einen Default-Typ ohne CE-Änderung (Typ X)."])

W("WP-I2-203", "Erweiterungspunkt A9: Relationstyp-Katalog, IWorkItemHierarchyPolicy, IRelatedScopeCheck, RELATION_TYPES, TIMELINE_FLAGS", "X", "S", False,
  [], [M1],
  "Katalogtabelle `work_item_relation_types` mit 10 Seeds statt Enum, projektübergreifende Relationen im Schema zulässig, `IWorkItemHierarchyPolicy` (E-05, CE: gleiches Projekt, kein Zyklus), `IRelatedScopeCheck`; Frontend `RELATION_TYPES`, `TIMELINE_FLAGS`.",
  be=["`src/modules/WorkItems/Funk.WorkItems` (Relations)", "`src/data/Funk.Data/Seeds/RelationTypes.cs`"],
  fe=["`frontend/libs/web/extensions/src/relations.ts`"],
  arch=["16 §5.3, §3.3.0 E-05", "01 §1.4 Zeile A9"],
  ep="01 §1.4 A9; 16 §3.3.0 E-05; 16 §4.6 (Träger CE-WI-031…033, CE-LV-033, CE-API-024)",
  ak=["Seeds entsprechen `IssueRelationChoices`; Fake-Relationstyp erscheint in Dropdown und Gantt ohne CE-Änderung (Typ X)."])

W("WP-I2-204", "Erweiterungspunkt C1: State-Change-Pipeline IWorkItemStateChanger mit Guards/Hooks, WORKFLOW_GUARD", "X", "S", False,
  [], [M1, "WP-I1-201"],
  "Jeder State-Wechsel (UI, API, Intake, Cycle-Transfer, Auto-Close, Integrationen) läuft durch `IWorkItemStateChanger` mit `IStateTransitionGuard`/`IStateTransitionHook` und `StateChangeOrigin`; Frontend-Token `WORKFLOW_GUARD`.",
  be=["`src/modules/WorkItems/Funk.WorkItems.Contracts/StateChanges/`"], fe=["`frontend/libs/web/extensions/src/workflow.ts`"],
  arch=["16 §5.9", "01 §1.4 Zeile C1", "06 §6.1"],
  ep="01 §1.4 C1; 16 §4.6 (Träger CE-WI-021, CE-WI-003; weitere Origins in I3/I6)",
  ak=["Architekturtest: kein Schreibzugriff auf `work_items.state_id` außerhalb der Pipeline.", "Fake-Guard verhindert einen Übergang mit Original-Fehlerform; Fake-Hook wird aufgerufen (Typ X)."])

W("WP-I2-205", "Erweiterungspunkte Work-Item-Fassaden: IWorkItemReferenceResolver, IWorkItemCommands, IIntegrationLinkProvider + external_links, IExpandProvider", "X", "S", False,
  [], [M1, "WP-I0-205"],
  "Zentraler Resolver `<IDENTIFIER>-<sequence>` (E-06), Contracts-Fassade `IWorkItemCommands` (E-18, von Intake und Public API selbst genutzt), Lesefassade `IIntegrationLinkProvider` (E-13, CE `[]`), leere Tabelle `external_links` (FK auf `work_items`/`work_item_comments`, ABG-141) und `IExpandProvider` für den `expand`-Parameter der Work-Item-Endpunkte (E-07, Teil I2).",
  be=["`src/modules/WorkItems/Funk.WorkItems.Contracts/Services/`", "`src/data/Funk.Data/Entities/Integrations/ExternalLink.cs`", "Migration `…_Integrations_ExternalLinks`"],
  arch=["16 §5.16, §3.3.0 E-06/E-13/E-18, D16-ADR-11", "16 §3.4.2", "17 ABG-141"],
  ep="16 §3.3.0 E-06, E-07 (Teil `expand`), E-13, E-18; 16 §4.6 (Träger CE-WI-009, CE-WI-002, CE-WI-001, CE-WI-010)",
  ak=["Resolver löst case-insensitiv, respektiert Archiv/Löschung/Gast-Sichtbarkeit; Fake-Link-Provider liefert Einträge, die im Detail über `INTEGRATION_LINK_PREVIEWS` erscheinen (Typ X)."])

W("WP-I2-206", "Erweiterungspunkte Work-Item-UI-Registries (Property-Renderer bis Duplicate-Detection)", "X", "M", False,
  [], [M1],
  "Frontend-Registries `PROPERTY_RENDERERS`, `WORK_ITEM_IDENTIFIER_DECORATORS`, `SPREADSHEET_COLUMNS`, `GROUP_BY_OPTIONS`, `FILTER_FIELDS`, `FILTER_OPERATORS`, `ISSUE_MODAL_CONTEXT`, `WORK_ITEM_PROPERTIES_LOADER`, `WORK_ITEM_DETAIL_WIDGETS`, `WORK_ITEM_ACTIONS`, `ACTIVITY_RENDERERS`, `INTEGRATION_LINK_PREVIEWS`, `DUPLICATE_DETECTION` mit CE-Einträgen (S5–S19, S29, S62–S65).",
  fe=["`frontend/libs/web/extensions/src/work-items/`"],
  arch=["08 §6.1, §6.4, §6.5", "16 §1.4 Zeile I2", "17 ABG-030"],
  ep="16 §1.4 Zeile I2 (Frontend); 16 §4.6 (Träger CE-WI-001/-010/-014/-034, CE-LV-008/-017…037)",
  ak=["Jede Registry hat CE-Einträge (Original-Verhalten) und einen Fake-Eintrag-Test (Typ X)."])

W("WP-I2-207", "Erweiterungspunkt Editor/Dokument-Schema: IDocumentNodeSpec/IDocumentMarkSpec, EDITOR_EXTENSIONS, EDITOR_FLAGS (Lite)", "X", "S", False,
  [], [M0, "WP-I0-905"],
  "Server-Schema aus `IEnumerable<IDocumentNodeSpec>`/`IEnumerable<IDocumentMarkSpec>` (E-11) und Editor-Tokens `EDITOR_EXTENSIONS`/`EDITOR_FLAGS` mit CE-Defaults.",
  be=["`src/documents/Funk.Documents/Schema/`"], fe=["`frontend/libs/shared/editor/extensibility`"],
  arch=["10 §5.10, §6.1", "07 §5.7", "16 §3.3.0 E-11"],
  ep="16 §3.3.0 E-11; 16 §4.6 (Träger CE-WI-037, CE-WI-044)",
  ak=["G-SCHEMA unverändert mit CE-Defaults; Fake-Node erweitert Client- und Server-Schema ohne CE-Änderung (Typ X)."])

W("WP-I2-021", "Editor ED-1: Lite-Text-Editor (Kommentare), Mentions, Emojis, Links", "D", "M", False,
  ["CE-PAGE-022", "CE-PAGE-034", "CE-PAGE-035", "CE-PAGE-036"], ["WP-I1-103", "WP-I0-905", "WP-I2-101", "WP-I2-207"],
  "`PlEdLiteTextEditor` mit Enter-Key-Verhalten, Mentions, Emoji-Suggestion (offline), Links, Bild-Upload und Lite-Toolbars der Web-Hülle; Read-only-Anzeige von Kommentaren.",
  fe=["`frontend/libs/shared/editor/{core,angular-binding,components}`", "`frontend/libs/web/core/editor` (Hüllen)"],
  arch=["10 §1.5 (ED-1), §3.6, §3.11, §3.12, §3.17, §3.21"],
  ak=["AK-D10-01, -05, -08, -12 grün; Visual Kommentar-Editor ≤ 0,5 %."])

W("WP-I2-022", "Editor ED-2a: Rich-Text-Kern (Textstruktur, Listen, Formatierung/Farben, Markdown, Platzhalter, Deep-Links, Anzeige-Konfiguration)", "D", "L", False,
  ["CE-PAGE-021", "CE-PAGE-027", "CE-PAGE-028", "CE-PAGE-029", "CE-PAGE-037", "CE-PAGE-038", "CE-PAGE-039", "CE-PAGE-040", "CE-I18N-010"], ["WP-I2-021"],
  "`PlEdRichTextEditor` mit vollständigem Kern, Markdown-Funktionen, Clipboard/Paste, Platzhaltern, Deep-Links zu Blöcken, Anzeige-Konfiguration und Editor-Farbpalette; `value`-Sync und `isMigrationUpdate`.",
  fe=["`frontend/libs/shared/editor`", "`frontend/libs/shared/editor/styles` (CSS 1:1)"],
  arch=["10 §1.5 (ED-2, Teil Kern), §3.6–§3.8, §3.16, §3.19, §3.20, §3.22"],
  note="Verfeinerung von 10 §1.5: ED-2 wird in ED-2a (Kern) und ED-2b (Menüs/Blöcke) geteilt, damit jedes Paket ≤ L bleibt.",
  ak=["AK-D10-01…-04 grün; G-SCHEMA (rich) unverändert."])

W("WP-I2-023", "Editor ED-2b: Menüs und Blöcke (Slash, Bubble, Drag-Handle/Block-Menü, Code-Block, Tabellen, Bilder, Callouts)", "D", "L", False,
  ["CE-PAGE-024", "CE-PAGE-025", "CE-PAGE-026", "CE-PAGE-030", "CE-PAGE-031", "CE-PAGE-032", "CE-PAGE-033"], ["WP-I2-022"],
  "Slash-Command-Menü, Bubble-Menü, Side-Menü mit Drag-Handle und Block-Menü, Code-Block mit Syntax-Highlighting, Tabellen inkl. Handles, Bilder mit Upload-UI, Callouts mit Emoji-/Icon-Logo.",
  fe=["`frontend/libs/shared/editor/components` (Menüs, NodeViews)"],
  arch=["10 §1.5 (ED-2, Teil Menüs/Blöcke), §3.9, §3.10, §3.13, §3.14"],
  ak=["AK-D10-05…-11 grün; Visual W-046 (Beschreibung) ≤ 0,5 %."])

W("WP-I2-024", "Editor ED-3: Document-Editor read-only (Beschreibungs-Versionen)", "D", "S", False,
  ["CE-PAGE-023"], ["WP-I2-023"],
  "`PlEdDocumentEditor` + `PlEdPageRenderer` + Outline-Extension für die Anzeige von Beschreibungs-Versionen.",
  fe=["`frontend/libs/shared/editor/components`"], arch=["10 §1.5 (ED-3), §3.18"],
  ak=["AK-D10-01, -13 grün."])

W("WP-I2-001", "Work Item anlegen und bearbeiten (Modal, fortlaufende ID, Autosave, Toasts, Drafts-Rückfrage, Bestehende hinzufügen)", "V", "L", False,
  rng("CE-WI", 1, 8), [M1, "WP-I2-202", "WP-I2-204", "WP-I2-205", "WP-I2-206", "WP-I2-022"],
  "Work-Item-Modal (Anlage/Bearbeitung), nebenläufigkeitssichere `sequence_id` je Projekt (`SequenceAllocator`), Titel- und Beschreibungs-Autosave, Toast-Aktionen, Draft-Rückfrage und Dialog „Bestehende Work Items hinzufügen“; Issue-Store-Grundgerüst (IssueRootStore) 1:1.",
  be=["`src/modules/WorkItems/Funk.WorkItems`, `Funk.WorkItems.Contracts`", "`src/data/Funk.Data/Entities/WorkItems/`, `Sequences/PostgresSequenceAllocator.cs`", "`tests/modules/Funk.WorkItems.Tests`"],
  fe=["`frontend/libs/web/work-items` (issue-modal, store/issue)"],
  arch=["04 §4.5", "03 §3.4.5, §3.6, §5.4, §5.5", "08 §3.4.6, §5.10", "06 §3.9"],
  ak=["Concurrency-Test: 100 parallele Anlagen erzeugen lückenlose, eindeutige `sequence_id` (01 §7.6).",
      "Store-Paritätsprüfung (`store-parity-check`) für IssueRootStore-Teile dieses Schnitts grün."])

W("WP-I2-002", "Work-Item-Detailseite (Identifier, Detaildaten, Meta, Delta-Sync, Kopfaktionen)", "V", "M", False,
  rng("CE-WI", 9, 14), ["WP-I2-001", "WP-I2-205"],
  "Detailseite per Identifier (`browse/:workItem`), Detaildaten, Meta und Mehrfachabruf, Delta-Sync für den Client-Cache (`GlobalPaginator`), Identifier mit Klick-zum-Kopieren, Kopfaktionen.",
  be=["`src/modules/WorkItems/Funk.WorkItems`"], fe=["`frontend/libs/web/work-items` (issue-detail)"],
  arch=["04 §4.5", "02 §3.10.4", "08 §4.1"])

W("WP-I2-003", "Peek-Overview und Hover-Vorschau", "V", "M", True,
  rng("CE-WI", 15, 19), ["WP-I2-002"],
  "Peek mit drei Modi (Side, Modal, Full), Inhalt, Schließen per Outside-Click/Escape, Fehler-/Ladezustand, Hover-Vorschaukarte.",
  fe=["`frontend/libs/web/work-items` (peek-overview)"], arch=["08 §3.9, §4.1", "09 §4.14"])

W("WP-I2-004", "Sidebar-Properties und Dropdowns (State, Priority, Assignees, Labels, Estimate, Projekt, Datum, Read-only-Labels)", "V", "L", True,
  ["CE-WI-020", "CE-WI-021", "CE-WI-022", "CE-WI-023", "CE-WI-024", "CE-WI-027", "CE-WI-028", "CE-WI-029", "CE-WI-030"], ["WP-I2-001"],
  "Property-Sidebar und alle Dropdowns außer Cycle/Modul (diese folgen mit I3); State-Wechsel über die State-Change-Pipeline; Date-Picker (Propel `Calendar`).",
  fe=["`frontend/libs/web/work-items` (dropdowns)"], be=["`src/modules/WorkItems/Funk.WorkItems`"],
  arch=["04 §4.5", "08 §1.3 (Date-Picker I2)", "16 §5.9"],
  note="CE-WI-025 (Cycle-Dropdown) und CE-WI-026 (Module-Dropdown) liegen in WP-I3-007 bzw. WP-I3-010, weil Cycles/Module erst in I3 existieren (Abweichung von 15 Anhang B, plan/04 OP-PLAN-03).")

W("WP-I2-005", "Hierarchie und Relationen (Parent, Sub-Work-Items, Relationen, Widget-Aktionsleiste)", "V", "M", True,
  rng("CE-WI", 31, 34), ["WP-I2-002", "WP-I2-203"],
  "Parent setzen/ändern/entfernen mit `IWorkItemHierarchyPolicy`, Sub-Work-Items, Relationen über den Relationstyp-Katalog, Widget-Aktionsleiste.",
  be=["`src/modules/WorkItems/Funk.WorkItems` (Relations, Hierarchy)"], fe=["`frontend/libs/web/work-items` (relations, sub-issues)"],
  arch=["04 §4.5", "16 §5.3"])

W("WP-I2-006", "Links und Anhänge an Work Items", "V", "M", True,
  ["CE-WI-035", "CE-WI-036"], ["WP-I2-002", "WP-I2-102"],
  "Links mit Metadaten-Crawling (SSRF-sicher) und Anhänge über Datei-Assets.",
  be=["`src/modules/WorkItems/Funk.WorkItems` (Links, Attachments)", "`src/modules/Assets/Funk.Assets`"], fe=["`frontend/libs/web/work-items` (links, attachments)"],
  arch=["04 §4.5, §4.13", "06 §3.18"])

W("WP-I2-007", "Kommentare, Emoji-Reaktionen, Mentions", "V", "M", True,
  ["CE-WI-037", "CE-WI-038", "CE-WI-044", "CE-I18N-017"], ["WP-I2-008", "WP-I2-021"],
  "Kommentare mit Lite-Editor, Emoji-Reaktionen auf Work Items und Kommentare (Reaktions-Komponenten), @Mentions in Beschreibung und Kommentaren mit `work_item_mentions`.",
  be=["`src/modules/WorkItems/Funk.WorkItems` (Comments, Reactions, Mentions)"], fe=["`frontend/libs/web/work-items` (comments)", "`frontend/libs/shared/blocks` (emoji-reaction)"],
  arch=["04 §4.5", "06 §3.9.5", "10 §3.11, §3.17"])

W("WP-I2-008", "Aktivitätsverlauf, Activity-Filter, Beschreibungs-Versionen, Eigenschafts-Historie, Abonnements", "V", "L", True,
  rng("CE-WI", 39, 43), ["WP-I2-002", "WP-I2-024", "WP-I1-204"],
  "Vollständige Activity-Pipeline (38 Varianten, 78 Aufrufstellen nach `_data/06-jobs.json`), Activity-Filter und -Sortierung, Beschreibungs-Versionshistorie (ED-3), Eigenschafts-Historie (`work_item_versions`, Aufbewahrung Default 20, 17 Z-114) und Abonnements.",
  be=["`src/modules/WorkItems/Funk.WorkItems/Activity/`"], fe=["`frontend/libs/web/work-items` (activity)"],
  arch=["06 §3.9, §4.4–§4.7", "03 §3.9.2", "06 R-D06-03"],
  ak=["Golden je Activity-Variante A1…A38 (AK-D06-10); jede Aufrufstelle C1…C78 aus `_data/06-jobs.json` ist einem Test zugeordnet."])

W("WP-I2-009", "Work Items archivieren/wiederherstellen und löschen (einzeln und Bulk)", "V", "M", True,
  rng("CE-WI", 45, 48), ["WP-I2-002"],
  "Archivieren und Wiederherstellen, Bulk-Archivieren (Backend), Löschen einzeln und mehrfach mit Soft-Delete-Kaskade.",
  be=["`src/modules/WorkItems/Funk.WorkItems`"], fe=["`frontend/libs/web/work-items`"],
  arch=["04 §4.5, §3.10.1 (Bulk)", "03 §3.5"])

W("WP-I2-010", "Workspace-Drafts", "V", "M", True,
  ["CE-WI-049"], ["WP-I2-001"],
  "Workspace-Drafts mit Anlage, Bearbeitung, Umwandlung in Work Items und Liste.",
  be=["`src/modules/WorkItems/Funk.WorkItems` (Drafts)"], fe=["`frontend/libs/web/work-items` (drafts)"],
  arch=["04 §4.5", "03 §3.4.5"])

W("WP-I2-011", "Layout-Umschaltung, Projekt-Work-Items-Seite und Kopf, Layout-Kontextmenü", "V", "M", False,
  ["CE-LV-001", "CE-LV-002", "CE-LV-003"], ["WP-I2-012"],
  "Projekt-Work-Items-Seite mit Kopf, Layout-Umschaltung und Layout-Kontextmenü; Layout-Kontexte Cycle/Modul/View/Archiv/Profil folgen mit WP-I3-001.",
  fe=["`frontend/libs/web/work-items` (issue-layouts/roots, headers)"], arch=["08 §4.1, §3.4.6", "09 §4.14"])

W("WP-I2-012", "Work-Item-Liste mit Gruppierung/Pagination (Backend), Rich-Filter (AND/OR/NOT), Filterzeile, Filterwerte, Filterfelder", "V", "L", False,
  rng("CE-LV", 5, 10), ["WP-I2-201", "WP-I0-909", "WP-I2-001"],
  "Gruppierte und sub-gruppierte Pagination (Port `GroupedOffsetPaginator`), Rich-Filter-Ausdrücke über den Filter-AST, Rich-Filter-Zeile, Filterwert-Eingaben, ungültige Bedingungen, Filterfelder.",
  be=["`src/modules/WorkItems/Funk.WorkItems/Query/`"], fe=["`frontend/libs/web/work-items` (rich-filters)", "`frontend/libs/shared/shared-state` (work-item-filters)"],
  arch=["02 §3.11", "04 §3.8", "08 §3.4.6"],
  ak=["Lasttests LT-01…LT-03 mit Volumenprofil L im Zielbereich von S9."])

W("WP-I2-013", "Klassische Filter, Applied-Filter-Chips, Display-Dropdown, Anzeige-Einstellungen je Nutzer/Projekt und Workspace", "V", "M", True,
  ["CE-LV-012", "CE-LV-013", "CE-LV-014", "CE-LV-015"], ["WP-I2-012"],
  "Klassische Filter-Sektionen mit Chips, Display-Dropdown, Anzeige-Einstellungen je Nutzer und Projekt sowie workspace-weit.",
  be=["`src/modules/WorkItems/Funk.WorkItems` (Display-Properties)"], fe=["`frontend/libs/web/work-items` (filters, display)"], arch=["04 §4.5", "08 §3.4.6"])

W("WP-I2-014", "List-Layout mit Gruppierung, Inline-Properties, Sub-Work-Items aufklappen", "V", "M", True,
  rng("CE-LV", 17, 19), ["WP-I2-011"],
  "List-Layout inklusive Gruppen, Inline-Property-Zeilen und aufklappbarer Sub-Work-Items mit Virtualisierung (`*plRenderIfVisible`).",
  fe=["`frontend/libs/web/work-items` (issue-layouts/list)"], arch=["08 §3.9, §5.11"])

W("WP-I2-015", "Kanban-Board, Swimlanes, Karte, Löschzone, Drag-and-Drop", "V", "L", True,
  rng("CE-LV", 20, 24), ["WP-I2-011", "WP-I0-904"],
  "Kanban mit Swimlanes, Karte, Löschzone und DnD zwischen Gruppen inkl. `sort_order` wie Original.",
  fe=["`frontend/libs/web/work-items` (issue-layouts/kanban)", "`frontend/libs/shared/dnd`"], arch=["08 §3.9, §5.12", "01 §9 S4"],
  ak=["LT-14 (Drag ≥ 55 fps mit 1 000 Karten) grün."])

W("WP-I2-016", "Calendar-Layout (Monat/Woche, Drag, Eintrag, Quick-Add)", "V", "M", True,
  rng("CE-LV", 25, 28), ["WP-I2-011"],
  "Calendar-Layout mit Monats- und Wochenansicht, Drag auf anderen Tag, Eintrag und Quick-Add je Tag.",
  fe=["`frontend/libs/web/work-items` (issue-layouts/calendar)"], arch=["08 §3.9"])

W("WP-I2-017", "Gantt/Timeline (Verschieben, Dauer, Datum setzen, Sidebar-Reorder, Relationen)", "V", "L", True,
  rng("CE-LV", 29, 33), ["WP-I2-011", "WP-I0-904", "WP-I2-203"],
  "Gantt-Ansicht mit Verschieben/Größe ändern, Datum für Items ohne Datum, Sidebar-Reorder und Timeline-Daten mit Relationen.",
  fe=["`frontend/libs/web/work-items` (gantt-chart)"], be=["`src/modules/WorkItems/Funk.WorkItems` (issues-detail)"], arch=["08 §3.9", "16 §5.3 (TIMELINE_FLAGS)"],
  ak=["LT-15 (Gantt-Interaktion) grün."])

W("WP-I2-018", "Spreadsheet (Tabelle, Sortierung, Tastaturnavigation, Mehrfachauswahl, Sprung zu Sub-Items)", "V", "L", True,
  rng("CE-LV", 34, 37), ["WP-I2-011"],
  "Spreadsheet-Layout mit Spalten über `SPREADSHEET_COLUMNS`, Sortierung, Tastaturnavigation, Mehrfachauswahl und Sprung zu Sub-Work-Items.",
  fe=["`frontend/libs/web/work-items` (issue-layouts/spreadsheet)"], arch=["08 §3.9", "16 §1.4 Zeile I2"])

W("WP-I2-019", "Inline-Property-Leiste, Quick-Add je Layout, Gruppen-„+“, Quick-Action- und Kontextmenü", "V", "M", True,
  rng("CE-LV", 38, 41), ["WP-I2-014"],
  "Inline-Property-Leiste, Quick-Add in allen Layouts, Gruppen-„+“ mit „Create work item“/„Add an existing work item“, Quick-Action-Menü und Rechtsklick-Kontextmenü (über `WORK_ITEM_ACTIONS`).",
  fe=["`frontend/libs/web/work-items` (quick-add, quick-action-dropdowns)"], arch=["08 §6.4", "16 §1.4 Zeile I2"])

W("WP-I2-020", "Layout-Zustände: Empty-States, Skeleton-Loader, Virtualisierung/Endlos-Laden, Fehlergrenze", "V", "M", True,
  rng("CE-LV", 42, 45), ["WP-I2-014"],
  "Empty-States, Skeleton-Loader je Layout, Virtualisierung mit Sentinel-Pagination und Layout-Fehlergrenze.",
  fe=["`frontend/libs/web/work-items` (issue-layouts)"], arch=["08 §3.9, §3.13"])

W("WP-I2-999", "Abnahme I2 – Work Items & Layouts (G5)", "A", "S", False,
  [], ["WP-I2-%03d" % i for i in range(1, 21)] + ["WP-I2-021", "WP-I2-022", "WP-I2-023", "WP-I2-024", "WP-I2-101", "WP-I2-102", "WP-I2-103"] + ["WP-I2-%03d" % i for i in range(201, 208)],
  "Inkrement-Abnahme I2 nach G5 und Meilenstein M2.",
  arch=["plan/01-roadmap-ce.md §4 (M2)", "15 §3.16 Zeile I2"],
  ak=["Alle Abnahmekriterien M2 erfüllt; `docs/acceptance/I2.md` generiert."], tests=["G5 `--inc I2`."])

# =====================================================================================
# I3 – Planung
# =====================================================================================
M2 = "WP-I2-999"

W("WP-I3-101", "Chart-Bausteine (Bar, Pie, Area, Line, Radar, TreeMap, Burndown) und Farbpaletten", "F", "M", True,
  ["CE-I18N-022"], [M2, "WP-I0-906"],
  "Die Diagramm-Bausteine aus `packages/blocks/src/charts` in D3 + Angular-SVG nach dem Ergebnis von S6, mit Farbpaletten, Tooltip und Legende.",
  fe=["`frontend/libs/shared/blocks/charts/{area,bar,line,pie,radar,tree-map}`"], arch=["09 §3.12, §4.7", "01 §9 S6"],
  ak=["Galerie-Visual je Diagrammtyp ≤ 0,5 % (hell/dunkel)."])

W("WP-I3-201", "Erweiterungspunkte Planung: ICycleSchedulingPolicy, CYCLE_FLAGS, ENTITY_QUICK_ACTIONS", "X", "S", False,
  [], [M2],
  "`ICycleSchedulingPolicy` (E-15, CE: keine Überschneidung), Token `CYCLE_FLAGS` (`parallelCycles: false`) und `ENTITY_QUICK_ACTIONS` (E-14, Quick Actions für cycle/module/view/layout/intake-header).",
  be=["`src/modules/Cycles/Funk.Cycles.Contracts/ICycleSchedulingPolicy.cs`"], fe=["`frontend/libs/web/extensions/src/{cycles,quick-actions}.ts`"],
  arch=["16 §5.15, §3.3.0 E-14/E-15"],
  ep="16 §3.3.0 E-14 (I3-Teil), E-15; 16 §4.6 (Träger CE-CYC-002…013, CE-MOD-011, CE-LV-050)",
  ak=["Fake-Policy erlaubt parallele Cycles ohne CE-Änderung; Fake-Quick-Action erscheint im Cycle-Menü (Typ X)."])

W("WP-I3-001", "Projekt-Archive und Layout-Kontexte (Cycle, Modul, View, Archiv, Profil)", "V", "M", True,
  ["CE-LV-004", "CE-LV-046"], [M2],
  "Projekt-Archive (Kopf, Tabs für Work Items, Cycles, Module) und die Layout-Kontexte, in denen die I2-Layouts wiederverwendet werden.",
  fe=["`frontend/libs/web/archives`", "`frontend/libs/web/work-items` (Layout-Kontexte)"], arch=["08 §4.1", "02 §3.11.4 (Basismengen)"],
  note="CE-LV-004 wurde von I2 nach I3 verschoben, weil die Kontexte erst mit Cycles/Modulen/Views existieren (plan/04 OP-PLAN-03).")

W("WP-I3-002", "Projekt-Views (Liste, Anlage/Bearbeitung, Löschen, Kontextmenü/Favoriten, Detail, Speichern aus Filtern)", "V", "L", True,
  ["CE-LV-011", "CE-LV-047", "CE-LV-048", "CE-LV-049", "CE-LV-050", "CE-LV-051"], [M2, "WP-I3-201"],
  "Projekt-Views auf Basis des Filter-AST inkl. „View aus Filtern speichern/aktualisieren“.",
  be=["`src/modules/Views/Funk.Views`", "`tests/modules/Funk.Views.Tests`"], fe=["`frontend/libs/web/views`"],
  arch=["04 §4.6", "03 §3.4.8"])

W("WP-I3-003", "Workspace-Views (Übersicht, Anlage/Bearbeitung/Löschen, All work items)", "V", "M", True,
  ["CE-LV-052", "CE-LV-053", "CE-LV-054"], ["WP-I3-002"],
  "Workspace-Views inklusive der Standard-Views und der Detailseite „All work items“.",
  be=["`src/modules/Views/Funk.Views`"], fe=["`frontend/libs/web/views`"], arch=["04 §4.6", "08 §4.1"])

W("WP-I3-004", "Cycle-Liste mit Gruppen, Suche/Filter, Inline-Dashboard, Workspace-weite Active Cycles", "V", "M", True,
  rng("CE-CYC", 1, 4), ["WP-I3-005", "WP-I3-101"],
  "Cycle-Liste (aktiv, kommend, abgeschlossen), Suche und Filter, Inline-Dashboard des aktiven Cycles und workspace-weite Active Cycles (vorgezogen nach D16-ADR-14).",
  be=["`src/modules/Cycles/Funk.Cycles`"], fe=["`frontend/libs/web/cycles`"], arch=["04 §4.7", "16 D16-ADR-14"])

W("WP-I3-005", "Cycles anlegen/bearbeiten, Datumsüberschneidung, archivieren, löschen, Kontextmenü, Favoriten", "V", "L", True,
  ["CE-CYC-005", "CE-CYC-006", "CE-CYC-012", "CE-CYC-013", "CE-CYC-014", "CE-CYC-015"], [M2, "WP-I3-201"],
  "Cycle-CRUD mit Überschneidungsprüfung über `ICycleSchedulingPolicy`, Archiv, Löschen, Kontextmenü und Favoriten; Cycle-Events und Abschluss-Erkennung (`cycles.completion_detection`).",
  be=["`src/modules/Cycles/Funk.Cycles`, `Funk.Cycles.Contracts`", "`tests/modules/Funk.Cycles.Tests`"], fe=["`frontend/libs/web/cycles`"],
  arch=["04 §4.7", "03 §3.4.6", "06 §3.17.4, O-D06-06"])

W("WP-I3-006", "Cycle-Peek/Detail, Fortschritt, Verteilungen, Burndown, Anzeige je Cycle und Modul", "V", "L", True,
  ["CE-CYC-007", "CE-CYC-008", "CE-CYC-009", "CE-LV-016"], ["WP-I3-005", "WP-I3-101"],
  "Cycle-Peek und Detail-Sidebar, Fortschritt, Verteilungen und Burndown (`progress_snapshot`), Cycle-Detailseite und Anzeige-Einstellungen je Cycle und Modul.",
  be=["`src/modules/Cycles/Funk.Cycles`"], fe=["`frontend/libs/web/cycles`"], arch=["04 §4.7", "03 §3.4.6"],
  note="CE-LV-016 aus I2 hierher verschoben (plan/04 OP-PLAN-03).")

W("WP-I3-007", "Work Items Cycles zuordnen, unvollständige übertragen, Cycle-Dropdown", "V", "M", True,
  ["CE-CYC-010", "CE-CYC-011", "CE-WI-025"], ["WP-I3-005"],
  "Zuordnung von Work Items zu Cycles, Transfer unvollständiger Work Items (State-Change-Origin `CycleTransfer`) und Cycle-Dropdown in den Work-Item-Properties.",
  be=["`src/modules/Cycles/Funk.Cycles`"], fe=["`frontend/libs/web/cycles`", "`frontend/libs/web/work-items` (dropdowns)"],
  arch=["04 §4.7", "16 §5.9"])

W("WP-I3-008", "Modul-Übersicht in drei Layouts, Suche/Filter/Sortierung, Kontextmenü und Favoriten", "V", "M", True,
  ["CE-MOD-001", "CE-MOD-002", "CE-MOD-011"], ["WP-I3-009"],
  "Modul-Übersicht (Liste, Galerie, Gantt), Suche/Filter/Sortierung, Kontextmenü und Favoriten.",
  fe=["`frontend/libs/web/modules`"], be=["`src/modules/ProjectModules/Funk.ProjectModules`"], arch=["04 §4.8"])

W("WP-I3-009", "Module anlegen/bearbeiten, Status, Links, Sidebar, archivieren, löschen", "V", "L", True,
  ["CE-MOD-003", "CE-MOD-004", "CE-MOD-005", "CE-MOD-006", "CE-MOD-009", "CE-MOD-010"], [M2, "WP-I3-201"],
  "Modul-CRUD mit Status, Links, Sidebar (Lead, Mitglieder, Fortschritt), Archiv und Löschen.",
  be=["`src/modules/ProjectModules/Funk.ProjectModules`, `Funk.ProjectModules.Contracts`", "`tests/modules/Funk.ProjectModules.Tests`"],
  fe=["`frontend/libs/web/modules`"], arch=["04 §4.8", "03 §3.4.7"])

W("WP-I3-010", "Modul-Detailseite, Work Items zuordnen, Module-Dropdown", "V", "M", True,
  ["CE-MOD-007", "CE-MOD-008", "CE-WI-026"], ["WP-I3-009", "WP-I3-101"],
  "Modul-Detailseite mit Work-Item-Layouts, Zuordnung von Work Items und Module-Dropdown in den Properties.",
  be=["`src/modules/ProjectModules/Funk.ProjectModules`"], fe=["`frontend/libs/web/modules`", "`frontend/libs/web/work-items` (dropdowns)"], arch=["04 §4.8"])

W("WP-I3-011", "Intake: je Projekt mit Triage-State, Seite Open/Closed, Filter/Sortierung, Detail, Anlage", "V", "L", True,
  rng("CE-INT", 1, 5), [M2],
  "Intake je Projekt mit Triage-State, Intake-Seite mit Tabs, Filter/Sortierung, Detail (Editor-Hüllen aus I2) und Anlage.",
  be=["`src/modules/Intake/Funk.Intake`, `Funk.Intake.Contracts`", "`tests/modules/Funk.Intake.Tests`"], fe=["`frontend/libs/web/intake`"],
  arch=["04 §4.9", "03 §3.4.9", "10 §1.4 Zeile I3"])

W("WP-I3-012", "Intake-Aktionen: annehmen, ablehnen, zurückstellen, Duplikat, bearbeiten/löschen, Navigation, Benachrichtigungs-Detail", "V", "L", True,
  rng("CE-INT", 6, 12), ["WP-I3-011"],
  "Annehmen (über `IWorkItemCommands` und State-Pipeline mit Origin `Intake`), Ablehnen, Snooze mit Unsnooze-Cron, Duplikat, Bearbeiten/Löschen, Navigation und Intake-Detail in Benachrichtigungen.",
  be=["`src/modules/Intake/Funk.Intake`"], fe=["`frontend/libs/web/intake`"], arch=["04 §4.9", "06 §3.17.2", "16 §5.16"])

W("WP-I3-013", "Automationen Auto-Archive und Auto-Close", "B", "M", True,
  ["CE-PRJ-039", "CE-PRJ-040"], [M2],
  "Projekt-Einstellung und Cron `work_items.auto_archive_close` (`0 1 * * *`); Auto-Close über `IWorkItemStateChanger` (Origin `AutoClose`) mit projektbezogenem Close-State-Fallback (DEV-AUTO-001/-002).",
  be=["`src/modules/WorkItems/Funk.WorkItems/Application/Jobs/AutoArchiveAndCloseJob.cs`"], fe=["`frontend/libs/web/project-settings` (automations)"],
  arch=["06 §3.17.1, §5.10, D06-ADR-19", "17 ABG-056"])

W("WP-I3-999", "Abnahme I3 – Planung (G5)", "A", "S", False,
  [], ["WP-I3-%03d" % i for i in range(1, 14)] + ["WP-I3-101", "WP-I3-201"],
  "Inkrement-Abnahme I3 nach G5 und Meilenstein M3.",
  arch=["plan/01-roadmap-ce.md §4 (M3)", "15 §3.16 Zeile I3"],
  ak=["Alle Abnahmekriterien M3 erfüllt; `docs/acceptance/I3.md` generiert."], tests=["G5 `--inc I3`."])
