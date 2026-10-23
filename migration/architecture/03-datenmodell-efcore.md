# 03 – Datenmodell mit Entity Framework Core 10 (alle CE-Entitäten)

> **Status:** verbindlich für das Datenmodell (01 Anhang A: „alle Entitäten, Tabellen, Indizes, Migrationen, Seeds“; baut auf ADR-037, ADR-038, 01 §7.6–7.8, §7.14).
> **Rangfolge:** `00-grundsatzentscheidungen.md` > `01-zielarchitektur-und-tech-stack.md` > `17-abgleich-dokumentuebergreifend.md` (verbindliche Abgleich-Entscheidungen) > Nachbardokumente 02, 05, 08, 09, 14, 15, 16 in ihrem Fachgebiet > dieses Dokument > eigene Präferenzen. Bei Widerspruch zu einem Nachbarn gilt dessen Text in seinem Fachgebiet; die Abweichung steht in §9 als Rückmeldung.
> **Stand:** 23.10.2026. Original-Referenz: Plane v1.4.2 Community Edition (`/home/user/plane`), Django-Modelle unter `apps/api/plane/db/models/` und `apps/api/plane/license/models/`.
> **Sprache:** Fließtext Deutsch, Bezeichner Englisch. Pfade für Zielcode relativ zur Wurzel des neuen Repositorys `funk.` (ADR-009).
> **Maschinenlesbar:** `migration/architecture/_data/03-datenmodell.json` (Tabellen, Eigentümer, Inkrement, Herkunft, `FloatField`-Liste, Referenztabellen für `TablesToIgnore`, Soft-Delete-Kaskaden).

Kürzel wie in 01: `API/` = `apps/api/plane/`, `M/` = `apps/api/plane/db/models/`, `MIG/` = `apps/api/plane/db/migrations/`, `LIC/` = `apps/api/plane/license/models/`, `WEB/` = `apps/web/`, `PKG/` = `packages/`. `A02a`/`A02b` = `migration/analysis/02a-datenmodell-kern.md` / `02b-datenmodell-arbeitsobjekte.md`; `Qn` = Quirk-Nummer aus A02b §3.14; `A02a-#n` = Quirk aus A02a §3.22. `D02`, `D05`, `D14`, `D15`, `D16` = Architekturdokumente 02, 05, 14, 15, 16. `BE/` = `funk./src/`.

## Inhaltsverzeichnis

1. [Ziel & Scope](#1-ziel--scope)
2. [Entscheidungen (D03-ADR-01 ff.)](#2-entscheidungen-d03-adr-01-ff)
3. [Detaildesign](#3-detaildesign)
   - 3.1 Basistypen, Namens- und Typkonventionen
   - 3.2 Typabbildung Django → PostgreSQL → C#
   - 3.3 Tabellenverzeichnis (Eigentümer, Inkrement, Herkunft)
   - 3.4 Tabellen je Modul (Spalten, Schlüssel, Indizes, Checks)
   - 3.5 Löschen: Soft-Delete-Filter, Join-Regeln, Kaskaden-Registry, Hard-Delete
   - 3.6 Nebenläufigkeitssichere Work-Item-Nummer (`sequence_id`)
   - 3.7 Sortierfelder (`sort_order`, `sequence`)
   - 3.8 JSONB-Spalten: Lesemodelle und Defaults
   - 3.9 Beschreibungsformate, Versionen, Yjs-Binärdaten
   - 3.10 Volltext- und Trigram-Suche
   - 3.11 Enums und Check-Constraints
   - 3.12 Mermaid-ER-Diagramme je Modul
   - 3.13 Migrationsstrategie
   - 3.14 Seeds
   - 3.15 Testdaten-Generator
4. [Vollständige Mapping-Tabellen Original → Ziel](#4-vollständige-mapping-tabellen-original--ziel)
5. [Code-Skelette](#5-code-skelette)
6. [Erweiterungspunkte für Bezahl-Pakete](#6-erweiterungspunkte-für-bezahl-pakete)
7. [Akzeptanzkriterien & Tests](#7-akzeptanzkriterien--tests)
8. [Risiken & offene Punkte](#8-risiken--offene-punkte)
9. [Abhängigkeiten zu anderen Dokumenten (02–16)](#9-abhängigkeiten-zu-anderen-dokumenten-0216)

---

## 1. Ziel & Scope

### 1.1 Ziel

Dieses Dokument legt das **vollständige relationale Zielschema** der Community Edition (CE) fest: für jede der 47 + 49 konkreten Django-Modelle des Originals (A02a §2.2, A02b §2.2) die Entscheidung „übernommen / angepasst / ersetzt / entfällt“, für jede übernommene Entität die Zieltabelle mit allen Spalten (Name, PostgreSQL-Typ, Null, Default, C#-Typ), Schlüssel, Fremdschlüssel mit Lösch-Verhalten, Unique- und partielle Indizes, Check-Constraints, JSONB-Lesemodelle, Enum-Werte und Sortierregeln. Dazu kommen die neuen Infrastruktur-Tabellen der Zielarchitektur (Sessions, Rollen, Outbox/Inbox/Jobs, Key-Ring, Feature-Einstellungen, Integrations- und Suchtabellen) sowie Migrations-, Seed- und Testdatenstrategie.

Ein Implementierungs-Agent kann aus §3.4 je Tabelle die Entitätsklasse und die `IEntityTypeConfiguration<T>` direkt schreiben (Skelette §5), aus §3.13 die Migrationen je Inkrement erzeugen und aus §7 die Abnahmetests ableiten.

### 1.2 Im Scope

| Bereich | Inhalt | Abschnitt |
|---|---|---|
| Entitäten | alle CE-genutzten Modelle aus `M/*.py` und `LIC/instance.py`; Zuordnung zu Modulen (01 §5.4) und `[OwnedBy]` (Regel R3) | §3.3, §3.4 |
| Neue Tabellen | `user_identities`, `user_sessions` (Form aus D05), `roles`, `role_permissions`, `data_protection_keys`, `project_feature_settings`, `workspace_feature_settings`, `work_item_relation_types`, `work_item_sequences`, `work_item_types` (Minimal-Schema), `outbox_messages`, `inbox_messages`, `jobs`, `recurring_jobs`, `integration_connections`, `external_links`, `search_documents` | §3.4.18 ff. |
| Querschnitt | UUIDv7, `snake_case`, Audit, Soft-Delete-Filter inkl. Join-Entscheidung, Mandanten-Scope-FKs, Kaskaden, Hard-Delete, Sequenzvergabe, Sortierfelder, JSONB, Enums, Checks, Beschreibungsformate, Versionen, Yjs, FTS/Trigram | §3.1, §3.5–§3.11 |
| Migrationen | EF-Migrationshistorie je Inkrement, Ausführung durch `Plane.Migrator` (Aspire-Ressource mit `WaitForCompletion`), Expand/Contract, Drift-Gate | §3.13 |
| Seeds | Referenzdaten (`BaseSeeds`), Laufzeit-Seeds (Default-States, Default-Intake, Benutzer-Defaults), Instanz-Konfiguration, Demo-Workspace aus `API/seeds/data` | §3.14 |
| Testdaten | `ParitySeedLoader` (D15), Volumen-Generator (`VolumeSeeder`, CE-OPS-024) | §3.15 |
| Andockstellen | Schema-Vorhalte für die 🧱-Pakete (A1, A2, A9, A17, B1, B6, C1, C3, D1, D2, E3, E5, F1, F2, G1, H1, H6) | §6 |

### 1.3 Nicht im Scope

- Fachliches Design der Bezahl-Pakete (Spalten von `work_item_properties`, `teamspaces`, `worklogs` …) – nur Andockstellen (§6); Detailplanung kurz vor der jeweiligen Welle (D16 §6).
- Endpunkt-Verträge und DTO-Formen (`04-api-design-und-endpunktkatalog.md`); hier nur, welche Spalten ein Vertrag braucht.
- Fachlogik der Commands (Modul-Dokumente/D02); hier nur datenmodellnahe Invarianten (Sequenz, Sortierung, Default-State, Snooze-Normalisierung).
- Job-Inventar und Event-Katalog (`06-…`); hier nur die Tabellenform von Outbox/Inbox/Jobs.
- Keycloak-Datenbank und Forgejo-Datenbank (eigene Datenbanken auf demselben PostgreSQL-Server, D14 §3.2).

### 1.4 Was wird in welchem Inkrement gebraucht

Jede Tabelle entsteht in der Migration des Inkrements, in dem ihr erster vertikaler Schnitt sie braucht (01 §1.3, Schnittregel). Bis zum ersten produktiven CE-Release darf je Inkrement gesquasht werden (01 §7.14).

| Inkrement | Migration(en) (`YYYYMMDDHHmm_<Modul>_<Beschreibung>`) | Tabellen | Seeds | Weitere Bausteine dieses Dokuments |
|---|---|---|---|---|
| **I0 Walking Skeleton** | `…_Platform_Extensions`, `…_Messaging_Initial`, `…_Instance_Initial`, `…_Identity_Initial`, `…_Authorization_Roles`, `…_Workspaces_Initial`, `…_Projects_Initial`, `…_Integrations_Connections` | Extensions `pg_trgm`, `unaccent`, `vector`; Funktion `plane_unaccent`; `outbox_messages`, `inbox_messages`, `jobs`, `recurring_jobs`, `data_protection_keys`, `instances`, `instance_admins`, `instance_configurations`, `users`, `profiles`, `user_identities`, `user_sessions`, `roles`, `role_permissions`, `workspaces`, `workspace_members`, `projects`, `project_identifiers`, `project_members`, `project_user_properties`, `states`, `integration_connections` | `BaseSeeds`: System-Rollen (6), Instanz-Datensatz, Instanz-Konfiguration aus ENV; Laufzeit: Default-States bei Projektanlage | Basistypen §3.1, Konventionen §3.2, Scope-FKs, Interceptors (D02), Drift-Gate, `PlaneRespawner`-Liste §4.6, `ParitySeedLoader`-Grundform |
| **I1 Workspace, Projekte, Konto** | `…_Workspaces_InvitesPreferences`, `…_Projects_LabelsEstimates`, `…_Projects_FeatureSettings`, `…_Assets_Initial`, `…_Identity_ApiTokens`, `…_Notifications_Preferences` | `workspace_member_invites`, `workspace_themes`, `workspace_user_properties`, `workspace_user_preferences`, `workspace_feature_settings`, `user_favorites`, `project_member_invites`, `project_feature_settings`, `labels`, `estimates`, `estimate_points`, `file_assets`, `api_tokens`, `user_notification_preferences` | Demo-Workspace-Seed (CE-WS-002) Teil 1 (Projekt, States, Labels) | Kaskaden-Registry vollständig für I0/I1-Tabellen, Hard-Delete-Job |
| **I2 Work Items & Layouts** | `…_WorkItems_Initial`, `…_Properties_WorkItemTypesMinimal`, `…_Integrations_ExternalLinks` | `work_items`, `work_item_sequences`, `work_item_assignees`, `work_item_labels`, `work_item_relation_types`, `work_item_relations`, `work_item_mentions`, `work_item_subscribers`, `work_item_links`, `work_item_comments`, `work_item_reactions`, `work_item_comment_reactions`, `work_item_activities`, `work_item_description_versions`, `work_item_versions`, `draft_work_items`, `draft_work_item_assignees`, `draft_work_item_labels`, `work_item_types`, `external_links`; Trigram-Indizes `work_items.name`, `projects.name/identifier`, `workspaces.name` | `work_item_relation_types` (10 Typen); Demo-Seed Teil 2 (Work Items) | `SequenceAllocator` §3.6, Beschreibungsformate §3.9 |
| **I3 Planung** | `…_Cycles_Initial`, `…_ProjectModules_Initial`, `…_Intake_Initial`, `…_Views_Initial`, `…_WorkItems_DraftPlanningLinks` | `cycles`, `cycle_work_items`, `cycle_user_properties`, `modules`, `module_members`, `module_work_items`, `module_links`, `module_user_properties`, `intakes`, `intake_work_items`, `views`, `draft_work_item_cycles`, `draft_work_item_modules` | Demo-Seed Teil 3 (Cycles, Module, View); Laufzeit: Default-Intake beim Aktivieren | Snooze-Index, Cycle-Überschneidungsindex |
| **I4 Pages & Realtime** | `…_Pages_Initial` | `pages`, `project_pages`, `page_labels`, `page_logs`, `page_versions` | Demo-Seed Teil 4 (Pages) | Yjs-Binärfeld, Versionsaufbewahrung |
| **I5 Überblick** | `…_Home_Initial`, `…_Notifications_Inbox`, `…_Analytics_Views`, `…_Search_Documents` | `workspace_home_preferences`, `workspace_user_links`, `user_recent_visits`, `stickies`, `notifications`, `email_notification_logs`, `analytic_views`, `search_documents`; Trigram-Indizes übrige Suchfelder | – | FTS §3.10 |
| **I6 Außenwirkung & Administration** | `…_PublicSpace_Initial`, `…_Webhooks_Initial`, `…_Exports_Initial`, `…_Identity_ApiActivityLogs`, `…_WorkItems_Votes` | `deploy_boards`, `project_public_members`, `work_item_votes`, `webhooks`, `webhook_logs`, `exports`, `api_activity_logs` | – | Aufbewahrungsindizes |
| **I7 Härtung & Betrieb** | Squash der Historie zu `…_CE_Baseline` (einmalig vor Release 1.0), danach nur additive Migrationen | – | – | Expand/Contract-Gate, Migrations-Lasttest, Backup/Restore-Test |
| **W1 … W9** | `W<n>_<Paket>_<Beschreibung>` (D16-ADR-06) | Paket-Tabellen | Paket-Seeds (Fragmente `scope: ee`, D15 EP-T03) | §6 |

### 1.5 Legende

| Begriff | Bedeutung |
|---|---|
| **übernommen** | Tabelle/Spalten fachlich wie Original (Namen ggf. nach D03-ADR-02) |
| **angepasst** | gleiche Semantik, andere Technik (z. B. Hash statt Klartext, FK statt String) |
| **korrigiert** | funktionaler Fehler des Originals wird behoben, Eintrag `DEV-DM-nn` in `tests/contracts/deviations.yaml` (Auftraggeber-Entscheidung Z-12: optisch 1:1, funktionale Fehler korrigieren und dokumentieren) |
| **ersetzt** | Original-Tabelle durch neue Form ersetzt (z. B. `sessions` → `user_sessions`) |
| **entfällt** | nicht portiert (Grund angegeben) |
| **minimal** | Andockstelle mit Minimal-Schema, in der CE leer (01 §1.4) |
| **P / V / R / S** | Klassen der Andockstellen nach D16 §1.5 |

---

## 2. Entscheidungen (D03-ADR-01 ff.)

Alle Entscheidungen präzisieren ADR-037/-038 und 01 §7.6–7.8/§7.14; Spalte „ab“ = erstes Inkrement.

| ID | Belang | Entscheidung | Alternativen (verworfen) | Begründung | ab |
|---|---|---|---|---|---|
| **D03-ADR-01** | Kontext und Ablage | **Ein** `PlaneDbContext` (+ `PlaneReadDbContext`, D02-ADR-22/-26) im Projekt `BE/data/Plane.Data`; Entitäten in `Plane.Data/Entities/<Modul>/<Entity>.cs`, Konfigurationen in `Plane.Data/Configurations/<Modul>/<Entity>Configuration.cs`, aufgenommen per `ApplyConfigurationsFromAssembly`; jede Entität trägt `[OwnedBy("<Modul>")]` (R3). Infrastruktur-Tabellen gehören den Pseudo-Modulen `Messaging` (Outbox/Inbox/Jobs) und `Instance` (Key-Ring). | Kontext je Modul; Schema je Modul (`pg schema`) | Work-Item-Listen joinen States, Labels, Cycles, Module, Assignees, Intake in einer Abfrage (ADR-037); Schreibeigentum sichert R3 maschinell | I0 |
| **D03-ADR-02** | Tabellen- und Spaltennamen | `snake_case` über `UseSnakeCaseNamingConvention()` (EFCore.NamingConventions 10.0.1); Tabellen im Plural; das Fachobjekt heißt **Work Item**: jede Original-Tabelle `issue_*`/`*_issues` wird `work_item_*`/`*_work_items`, jede FK-Spalte `issue_id` wird `work_item_id`, `draft_issue_id` → `draft_work_item_id`, `related_issue_id` → `related_work_item_id`, `issue_comment_id` → `comment_id` (01 §7.1). **Ausnahmen mit Begründung:** `issue_views` → `views` (Modul `Plane.Views`, Entität `View`), `exporters` → `exports`, `sessions` → `user_sessions` (D05), `issue_sequences` → `work_item_sequences` (andere Form, §3.6); Spaltennamen, die als JSON-Feld 1:1 in den Vertrag gehen und keine FKs sind, bleiben (`webhooks.issue`, `exports.project`, `projects.issue_views_view`). JSON-Felder und URL-Segmente behalten die Original-Namen (`issue`, `issue_id`), die Abbildung leisten die DTOs (04). Alias-Tabelle für Nachbardokumente: §4.5 | Original-Tabellennamen 1:1; reine Umbenennung nur in C# | 01 §7.1 ist verbindlich; ein konsistentes Schema ist für Agenten und Raw-SQL (D02 §3.11.6) eindeutiger; Vertrag hängt nicht an Tabellennamen (ADR-003) | I0 |
| **D03-ADR-03** | Namen von Constraints und Indizes | Primärschlüssel `pk_<tabelle>`, FKs `fk_<tabelle>_<ziel>_<spalte>` (EF-Default mit Snake-Case), Indizes `ix_<tabelle>_<spalten>`, Unique `ux_<tabelle>_<spalten>`, Checks `ck_<tabelle>_<regel>`, Alternate Keys `ak_<tabelle>_<spalten>`. **Partielle Unique-Constraints des Originals behalten ihren Original-Namen** (z. B. `state_unique_name_project_when_deleted_at_null`), weil `IUniqueViolationMap` (D02 §3.19) Unique-Verletzungen über den Constraint-Namen auf die endpunktspezifische Original-Fehlermeldung abbildet und die Namen in A02a §2.6/A02b §2.7 dokumentiert sind | durchgängig generierte Namen | Fehlerabbildung bleibt nachvollziehbar zum Original; neue Constraints folgen dem Schema | I0 |
| **D03-ADR-04** | Primärschlüssel | `uuid`, in der Anwendung als **UUIDv7** erzeugt (`IIdGenerator` → `Guid.CreateVersion7(clock.UtcNow)`; R8), `ValueGeneratedNever()`, **kein** DB-Default. Ausnahmen: `project_identifiers.id` `bigint GENERATED BY DEFAULT AS IDENTITY` (API liefert die Ganzzahl, `ProjectIdentifierEndpoint`), `data_protection_keys.id` `integer` Identity (Framework-Entität), `user_sessions.id` `varchar(64)` (D05 §3.4.1), Katalogtabellen mit fachlichem Schlüssel (`work_item_relation_types.key`, `work_item_sequences.project_id`, `*_feature_settings (…_id, key)`, `inbox_messages (consumer, message_id)`, `recurring_jobs.name`). Seeds und Testdaten nutzen **UUIDv5** (D15-ADR-07/-16) bzw. feste UUIDv7-Konstanten (System-Rollen, D05 §3.13.3) | DB-seitiges `uuidv7()` (PG 18) oder `gen_random_uuid()`; Snowflake/`bigint` | Monoton steigende Schlüssel → B-Tree-freundlich, ohne Roundtrip; App-seitige Erzeugung ist Voraussetzung für Domain-Events vor `SaveChanges` und für deterministische Testdaten | I0 |
| **D03-ADR-05** | Mandanten-Konsistenz in der DB | Jede Tabelle mit `workspace_id` **und** `project_id` erhält statt der Einzel-FK auf `projects` einen **zusammengesetzten Scope-FK** `fk_<tabelle>_project_scope (project_id, workspace_id) → projects (id, workspace_id)` (Alternate Key `ak_projects_id_workspace_id`), zusätzlich die Einzel-FK `workspace_id → workspaces`. Bei `project_id IS NULL` (Workspace-Entitäten) greift der FK nicht (`MATCH SIMPLE`). Der `ScopeConsistencyInterceptor` (D02 §3.2.2 Nr. 4) bleibt als frühe, verständliche Fehlerquelle | nur Interceptor (D02); Trigger | Schutz gegen Mandantenvermischung auch bei Raw-SQL, `ExecuteUpdate` und Fehlern im Interceptor (Empfehlung A02a §5.2); kostet einen zusätzlichen Unique-Index auf `projects` | I0 |
| **D03-ADR-06** | Lösch-Verhalten der FKs | DB-FKs bilden das Original-`on_delete` für **harte** Löschungen ab (`CASCADE`, `SET NULL`), weil Soft-Delete nie die DB-Kaskade auslöst; Abweichungen nur, wo das Original Daten verliert oder bricht: (a) `DO_NOTHING` der Activities → `work_item_id` `CASCADE`, `comment_id` `SET NULL` (Q3); (b) Benutzer-FKs siehe D03-ADR-07; (c) Drafts hängen nicht mehr kaskadierend an State/Parent (Q17, DEV-DM-07); (d) polymorphe Referenzen (`entity_identifier`, `moved_to_*`, `webhook_logs.webhook_id`, `profiles.last_workspace_id`) bleiben ohne FK wie im Original. Soft-Delete-Kaskaden laufen über die `SoftDeleteCascadeRegistry` (D02-ADR-03), vollständige Liste §3.5.4 | alle FKs `RESTRICT` und Löschen nur in Code; DB-Kaskaden auch für Soft-Delete per Trigger | Hard-Delete-Job (`HardDeleteJob`) kann dann mit einem `DELETE` je Wurzel arbeiten (A02a §5.2 „DB-FKs passend zu `on_delete`“); Original-Verhalten bleibt sichtbar gleich | I0 |
| **D03-ADR-07** | Benutzer-Referenzen | Zeilen in `users` werden **nie hart gelöscht** (CE kennt nur Deaktivierung, CE-PROF-005, D05 §3.18). Daraus: Audit-Spalten `created_by_id`/`updated_by_id` → `SET NULL`; persönliche Datensätze (Sessions, Identitäten, Tokens, Präferenzen, Favoriten, Besuche, Benachrichtigungen des Empfängers, Mitgliedschaften, Reaktionen) → `CASCADE`; **Besitz-Referenzen geteilter Objekte** (`workspaces.owner_id`, `cycles.owned_by_id`, `views.owned_by_id`, `pages.owned_by_id`) → `RESTRICT` (Original `CASCADE` hätte geteilte Objekte mitgelöscht, A02a-#5); Zuständigkeiten (`projects.default_assignee_id`, `projects.project_lead_id`, `modules.lead_id`, `work_item_comments.actor_id`, `notifications.triggered_by_id`, Versions-`owned_by_id`) → `SET NULL` | Original-`CASCADE` überall | verhindert Datenverlust, falls ein Betreiber per SQL/CLI doch einen Benutzer entfernt; ohne Wirkung auf API-Verträge | I0 |
| **D03-ADR-08** | Soft-Delete und Joins (**bewusste Entscheidung**) | Alle `ISoftDeletable`-Entitäten erhalten den benannten Filter `soft_delete` (EF 10, `HasQueryFilter(name, …)`, Microsoft Learn „Global Query Filters – named filters“). **Joins:** (1) EF wendet den Filter auch auf Navigationen/`Include`/Joins an – anders als Django, das über Vorwärts-FKs gelöschte Eltern lädt (A02a §3.2 f). Das ist **gewollt**: weil Kaskaden inline (bzw. für Workspace/Projekt deferred) laufen, existiert in einem konsistenten Zustand kein aktives Kind eines gelöschten Elternteils, außer bei bewusst verbleibenden Verweisen; (2) die Fälle, in denen das Original gelöschte Join-Zeilen sichtbar mitliest, sind abschließend in §3.5.2 gelistet und werden **explizit** mit `IgnoreQueryFilters([QueryFilterNames.SoftDelete])` bzw. im SQL-Baustein (D02 §3.11.6) ohne Filter umgesetzt; (3) Pflicht-Navigationen von Kind zu soft-löschbarem Elternteil werden **nicht** als `IsRequired`-Navigation modelliert (nur FK-Property + optionale Navigation), damit EF-Warnung 10622 nicht unterdrückt werden muss; (4) Join-Tabellen (Assignees, Labels, Cycle-/Modul-Zuordnungen) sind soft-löschbar wie im Original, Abfragen über M2M lesen deshalb nur aktive Zuordnungen | Filter nur auf Wurzel-Entitäten; kein globaler Filter (explizite Prädikate überall) | Explizit statt „magisch“ unterschiedlich je Codepfad (Q1); Abweichungen vom Original sind aufgezählt und testbar | I0 |
| **D03-ADR-09** | Audit-Felder | Wie D02 §3.2.1 (`created_at`, `updated_at`, `created_by_id`, `updated_by_id`, `deleted_at`; Anlage: `updated_by_id = NULL`). Zusätzlich Interface **`ITimestamped`** (`CreatedAt`, `UpdatedAt`) für Entitäten ohne Benutzer-Audit (`users`, `profiles`, Original `TimeAuditModel`), vom `AuditInterceptor` gleich behandelt. Fachliche Historie ausschließlich über `work_item_activities` (01 §7.8). Soft-Delete-Kaskaden setzen `updated_at`, aber **nicht** `updated_by_id = NULL` (Korrektur A02a-#10) | Audit-Shadow-Properties; Temporal Tables | Golden-Files des Originals bleiben vergleichbar; der Audit-NULL-Bug wird nicht übernommen | I0 |
| **D03-ADR-10** | Zeittypen | `DateTimeOffset` → `timestamptz` mit Präzision 6, `DateOnly` → `date`; Original-`DateField`s bleiben `date` (**auch** `work_items.archived_at`, `pages.archived_at`, `work_item_versions.archived_at`), Original-`DateTimeField`s `timestamptz` (`cycles.start_date/end_date`, `modules.archived_at`) | alles `timestamptz` | Tagesgenauigkeit ist Vertrag (A02b §3.13); Mischtypen werden in der Spaltentabelle je Feld ausgewiesen | I0 |
| **D03-ADR-11** | Zahlen | Original `FloatField` → `double precision`/`double` (Ausgabe mit Dezimalteil, `PythonFloatConverter`, D02-ADR-11; Liste §4.4 für D15 R-D15-04); `IntegerField` → `integer`, `PositiveSmallIntegerField` → `smallint` + Check `>= 0`, `BigIntegerField` → `bigint`; kein `numeric` | `numeric` für `sort_order`; `real` | Wert- und lexikalische Gleichheit mit DRF (`65535.0`); Drag-&-Drop-Mittelwerte brauchen `double` | I0 |
| **D03-ADR-12** | Texte | `varchar(n)` genau dort, wo das Original `max_length` hat (gleiche Länge, D02 §3.2.3), sonst `text`; `URLField` ohne Länge → `varchar(200)` (Django-Default, Validierungsgrenze Q22); Original-`JSONField` mit HTML-Strings (`projects.description_html`, `modules.description_html`, A02a-#4) → `text`; zu kurze Original-Spalten mit Überlaufrisiko (`*_member_invites.token`, A02a-#17) → `text` | überall `text` + Validator | Validierungsfehlertexte der DRF-Längenprüfung bleiben 1:1 ableitbar; DB-Länge ist Sicherheitsnetz | I0 |
| **D03-ADR-13** | JSONB | Alle Original-`JSONField`s → `jsonb`. **C#-Typ `JsonObject`** (bzw. `JsonNode` für Nicht-Objekte, `JsonArray` für Listen) mit Value-Converter `JsonNodeValueConverter` und `ValueComparer` auf `JsonNode.DeepEquals` – **Durchreichen unbekannter Schlüssel** ist Pflicht (Frontend schreibt vollständige Objekte, Pakete ergänzen Schlüssel, D16 A7). Für Strukturen, die der Server selbst liest/schreibt, existiert ein **Lesemodell** (`sealed record` in `Plane.Data/Json/`, §3.8), deserialisiert mit `PlaneJsonContext` bei Bedarf. Kein EF-`ToJson()`-Mapping in der CE; Abfragen in JSON-Inhalte nur über benannte SQL-Bausteine. DB-Defaults = Original-Literal (`'{}'::jsonb` bzw. konstante Default-Objekte, §3.8.2) | EF-10-Complex-Types `ToJson()` (verliert unbekannte Schlüssel, Schema-Migrationen bei jedem Frontend-Feld); `JsonDocument` (immutable, `IDisposable`); `string` | Parität bei beliebigen Frontend-Strukturen; Lesemodelle geben Typsicherheit dort, wo Logik existiert | I0 |
| **D03-ADR-14** | Enums | Zahlen-Enums (`role` 20/15/5, `network` 0/2, `access`, `intake status` −2…2, `vote` ±1, `start_of_the_week`, `user_type`) als `smallint`/`integer` mit C#-`enum` (explizite Werte) und **Check-Constraint**; String-Enums (`priority`, `state.group`, `module.status`, `estimate.type`, `comment.access`, `exports.provider/status`, `deploy_boards.entity_name`, Navigation-Präferenz) als `varchar` mit `HasConversion<string>()` über `[EnumValue("…")]` und Check-Constraint (Korrektur Q19). **Keine** DB-Checks für Wertelisten, die Pakete erweitern (`file_assets.entity_type`, `user_favorites.entity_type`, `user_recent_visits.entity_name`, `exports.type`, `workspace_user_preferences.key`, `workspace_home_preferences.key`, `users.bot_type`, `notifications.entity_name`) – dort validiert der Fachcode gegen eine Registry | PostgreSQL-`ENUM`-Typen; keine Checks | Checks sind per Expand-Migration erweiterbar, PG-Enums nicht transaktional änderbar; Registry-Werte bleiben paketerweiterbar (D16-ADR-06) | I0 |
| **D03-ADR-15** | M2M | Jede Original-M2M (`through`-Modell) ist eine **explizite Join-Entität** mit eigenem `id`, Audit und Soft-Delete (Original-Semantik, API liefert teils Zeilen-IDs); keine EF-Skip-Navigationen. Fehlende Unique-Regeln des Originals werden als partielle Unique-Indizes ergänzt (`work_item_labels`, `draft_work_item_labels`, `page_labels`, A02b §2.7 d) | Skip-Navigationen mit implizitem Join-Typ | Soft-Delete der Zuordnung, Activity und Kaskaden brauchen die Zeile als Entität | I0 |
| **D03-ADR-16** | Work-Item-Nummer | Zählertabelle `work_item_sequences (project_id PK, last_value)`; Vergabe per `INSERT … ON CONFLICT (project_id) DO UPDATE SET last_value = work_item_sequences.last_value + 1 RETURNING last_value` **in der Command-Transaktion** (Zeilensperre bis Commit → nebenläufigkeitssicher, bei Rollback lückenlos); zusätzlich `UNIQUE (project_id, sequence_id)` auf `work_items` (Korrektur Q4) | Original: Advisory-Lock + `MAX(sequence)` aus `issue_sequences`; PostgreSQL-`SEQUENCE` je Projekt (nicht lückenlos, DDL je Projekt); `MAX(sequence_id)+1` mit Retry | Eine Zeile je Projekt statt einer Zeile je Work Item, keine Advisory-Lock-Hashfunktion, deterministisch testbar (01 §7.6, Concurrency-Test) | I2 |
| **D03-ADR-17** | Beschreibungen und Versionen | Jede beschreibbare Entität behält die vier Original-Formate (`description_html` text, `description_json` jsonb, `description_binary` bytea, `description_stripped` text, §3.9); `*_stripped` wird **serverseitig** mit **einer** Implementierung `HtmlText.StripTags` (Port der Plane-Variante aus `API/utils/html_processor.py`) berechnet (Korrektur Q14). Versionstabellen `work_item_description_versions`, `page_versions`, `work_item_versions` mit 600-s-Merge-Regel; Aufbewahrung als Instanz-Einstellung (ADR-001, Default 20); Original-Defekte Q10/Q11 korrigiert (DEV-DM-06, DEV-DM-10). Der Kommentar-Spiegel `descriptions`/`description_versions` entfällt (Q15) | `descriptions` als Owned Entity übernehmen | Weniger Tabellen, kein verwaister Spiegel; Vertragsfeld `description` des Kommentars wird `null` (DEV-DM-03) | I2 |
| **D03-ADR-18** | Yjs-Binärdaten | `bytea` ohne Kompression; für **Pages** kanonisch (Hocuspocus-Persistenz über `IPageDocumentStore`, ADR-022), für Work Items/Drafts/Stickies nur gespeicherter Nebenstand (kein kollaborativer Editor); Größenlimit 10 MiB als Check-Constraint und Validierung (`validate_binary_data`, A02b §3.5 c) | Large Objects; separate Tabelle `documents` | Original-Vertrag (Base64 in JSON, `application/octet-stream`); 10 MiB passt in TOAST | I2/I4 |
| **D03-ADR-19** | Suche | (a) **Parität:** `ILIKE`-Suchen des Originals (`name__icontains` u. a., §3.10.1) erhalten **GIN-Trigram-Indizes** (`gin_trgm_ops`, Npgsql `HasMethod("gin").HasOperators("gin_trgm_ops")`); (b) **Ranking/G1/B6:** eine Tabelle `search_documents` mit `search_vector tsvector GENERATED ALWAYS AS (…) STORED` über `plane_unaccent()` (IMMUTABLE-Wrapper, weil `unaccent()` nur STABLE ist und Generated Columns IMMUTABLE verlangen) und Konfiguration `simple`; befüllt vom `IIndexingPipeline`-Consumer (I5). **Keine** `tsvector`-Spalten an den Fachtabellen | `tsvector`-Generated-Columns an `work_items`/`pages`; externer Suchdienst | Fachtabellen bleiben schlank; ein Index für Workspace-weite Suche über mehrere Entitätstypen; G1 hängt später Embeddings an dieselbe Pipeline (§6) | I2 (Trigram), I5 (FTS) |
| **D03-ADR-20** | Erweiterungs-Spalten | Spalten, die der Original-Vertrag enthält und die Pakete nutzen (Klasse V, D16-ADR-06), legt die CE an; reine Paket-Vorhalte (Klasse P) nur dort, wo 01 §1.4/D16 sie verlangen: `work_items.type_id`, `draft_work_items.type_id`, `work_item_types` (minimal), `work_item_relation_types`, `teamspace_id` (ohne FK) an `views`, `pages`, `work_item_comments`, `user_favorites`, `roles`/`role_permissions`, `*_feature_settings`, `integration_connections`, `external_links`, `search_documents`. Alles Weitere fügen Pakete **additiv** hinzu | „vorsorglich“ weitere Spalten | Strategie „schlanker Gesamtrahmen“; Andockstellen ohne Fachdesign | I0–I5 |
| **D03-ADR-21** | Migrationsausführung | EF-Migrationen werden **ausschließlich** von `Plane.Migrator` (Aspire-Ressource, Hosts `WaitForCompletion`, D14-ADR-16) per `MigrateAsync()` unter `pg_advisory_lock(7356001)` angewandt, gefolgt von Extension-Check, Seeds, Instanz-Init. Das **EF-Migration-Bundle** (`dotnet ef migrations bundle`) wird **nicht** als Laufzeitartefakt genutzt; CI erzeugt stattdessen je Release das **idempotente SQL-Skript** `artifacts/migrations/plane-<version>.sql` (`dotnet ef migrations script --idempotent`) für Betreiber mit DBA-Freigabeprozess | `efbundle` als eigener Compose-Job; `Database.EnsureCreated`; Selbstmigration der Api | Bundle kann weder Seeds noch Lock noch Extension-Check; ein Migrator-Image deckt Compose, Helm (Job je Revision) und AIO ab (D14 §3.15) | I0 |
| **D03-ADR-22** | Migrationsform | Eine Historie in `Plane.Data/Migrations` (01 §7.14), Namen `YYYYMMDDHHmm_<Modul>_<Beschreibung>`; **Expand/Contract** nach D14 §3.17 mit Attribut `[ContractPhase("vX.Y")]` an jeder Migration mit `DropColumn`/`DropTable`/`RenameColumn`/`AlterColumn` (Typ oder Null-Fähigkeit); Index-Anlagen auf bestehenden großen Tabellen **nach** Release 1.0 mit `CREATE INDEX CONCURRENTLY` in eigener, nicht-transaktionaler Migration (`migrationBuilder.Sql(…, suppressTransaction: true)`, Muster `MIG/0124`); Extensions/Funktionen per `migrationBuilder.Sql` mit `IF NOT EXISTS`; Snapshot nie von Hand | mehrere Historien je Modul | 01 §7.14, D14 §3.17; Zero-Downtime-Rolling (Helm) braucht additive Schritte | I0 |
| **D03-ADR-23** | Seeds | Drei Klassen: **(A) Referenz-Seeds** (`BaseSeeds`: System-Rollen, Relationstyp-Katalog, Instanz-Datensatz, Instanz-Konfiguration) idempotent im Migrator mit festen IDs, Tabellen in `TablesToIgnore` (§4.6); **(B) Laufzeit-Seeds** im Fachcode (Default-States/Triage bei Projektanlage, Default-Intake, Profil/Benachrichtigungs-Präferenzen bei JIT, Demo-Workspace CE-WS-002 als Job) – **nie** im Migrator; **(C) Testdaten** (`ParitySeedLoader`, `VolumeSeeder`) nur in Test/Dev, über Commands (D15). Kein `HasData` für Referenz-Seeds | EF `HasData` (erzeugt Migrations-Diffs bei jeder Wertänderung, keine Upserts mit Bedingungen) | Seeds bleiben änderbar ohne Schema-Migration; Laufzeit-Seeds laufen durch dieselben Invarianten wie Benutzeraktionen | I0 |
| **D03-ADR-24** | Concurrency-Token | Keine Row-Version (D02 §3.2.3, Lost-Update-Semantik wie Original); Ausnahmen: Zeilensperren für `work_item_sequences` (§3.6) und `SELECT … FOR UPDATE` beim Snooze-Retiming (`intake_work_items`, A02a §3.4); Page-Binärdaten serialisiert der Realtime-Host je Dokument (ADR-022) | `xmin` als Token überall | Parität; kein 409 dort, wo das Original keinen kennt | I0 |
| **D03-ADR-25** | Messaging-Tabellen | `outbox_messages` mit den Kontextspalten aus ABG-053, `inbox_messages (consumer, message_id)`, `jobs` (Queue, `run_at`, Versuche, Dead-Letter, `dedupe_key`), `recurring_jobs` (Cron-Zustand); alle im `PlaneDbContext`, Eigentümer `Messaging`, ohne Soft-Delete (Form §3.4.19) | eigener Kontext; Broker | ADR-020: gleiche Transaktion wie Fachdaten | I0 |
| **D03-ADR-26** | Entfallene Modelle | Nicht portiert: `Account`, `Session` (→ `user_sessions`), `Device`, `DeviceSession`, `SocialLoginConnection`, `Team`, `ProjectDeployBoard`, `ProjectWebhook`, `Integration`, `WorkspaceIntegration`, `GithubRepository`, `GithubRepositorySync`, `GithubIssueSync`, `GithubCommentSync`, `SlackProjectSync`, `Importer`, `ChangeLog`, `IssueBlocker`, `IssueAttachment`, `IssueSequence` (→ Zähler), `ProjectIssueType`, `Description`, `DescriptionVersion`; `IssueType` nur minimal (§4.1) | Übernahme „für später“ | Greenfield (ADR-003), CE ungenutzt (A02a §1.3, A02b §1.3), ADR-007/-008 | I0 |
| **D03-ADR-27** | Volumen-Testdaten | `VolumeSeeder` (`Plane.BuildingBlocks.Testing/Seed`) mit **Bogus** (MIT, Seed fest), schreibt Bulk per Npgsql-`COPY` (binär) unter Umgehung der Commands, aber mit denselben Invarianten-Helfern (Sequenz, Sortierung, Default-State); Profile `volume-S/M/L` | nur über Commands (zu langsam für 100k Work Items); Datenbank-Dump | Lasttests (D15 LT-*) brauchen 10⁵–10⁶ Zeilen in Minuten | I2 |

---

## 3. Detaildesign

### 3.1 Basistypen, Namens- und Typkonventionen

#### 3.1.1 Basistypen (Definition in D02 §3.2.1/§5.1.1, hier nur die Spaltensicht)

| Kürzel in §3.4 | C#-Basis (`Plane.BuildingBlocks.Persistence/Entities`) | Spalten (in dieser Reihenfolge am Tabellenanfang) | Original |
|---|---|---|---|
| **E** | `Entity` | `id uuid NOT NULL` (PK) | `BaseModel.id` |
| **A** | `AuditableEntity : Entity, IAuditable, ISoftDeletable` | `id`, `created_at timestamptz(6) NOT NULL`, `updated_at timestamptz(6) NOT NULL`, `created_by_id uuid NULL` (FK `users` SET NULL), `updated_by_id uuid NULL` (FK `users` SET NULL), `deleted_at timestamptz(6) NULL` | `BaseModel` (= `AuditModel` + `id`) |
| **W** | `WorkspaceEntity : AuditableEntity, IWorkspaceScoped` | A + `workspace_id uuid NOT NULL` (FK `workspaces` CASCADE), `project_id uuid NULL` (Scope-FK, D03-ADR-05) | `WorkspaceBaseModel` |
| **P** | `ProjectEntity : AuditableEntity, IWorkspaceScoped, IProjectScoped` | A + `workspace_id uuid NOT NULL` (FK `workspaces` CASCADE), `project_id uuid NOT NULL` (Scope-FK `(project_id, workspace_id) → projects(id, workspace_id)` CASCADE) | `ProjectBaseModel` |
| **X** | eigene Form | Spalten vollständig in §3.4 | – |

Ergänzende Marker (D02): `IExternallyReferenced` (`external_source varchar(255) NULL`, `external_id varchar(255) NULL`), `ISortable` (`sort_order double precision NOT NULL DEFAULT 65535`), `IScopedCatalogEntry` (`State`, `Label`, `WorkItemType`; berechnetes `Scope`, `[NotMapped]`), `IHasDomainEvents`.

#### 3.1.2 Neu in diesem Dokument

| Typ | Ort | Zweck |
|---|---|---|
| `ITimestamped { DateTimeOffset CreatedAt; DateTimeOffset UpdatedAt; }` | `Plane.BuildingBlocks.Persistence/Entities/ITimestamped.cs` | Entitäten mit Zeitstempeln, aber ohne Benutzer-Audit und Soft-Delete (`User`, `Profile` – Original `TimeAuditModel`); `IAuditable : ITimestamped` (Erweiterung des D02-Interfaces, Rückmeldung §9). Der `AuditInterceptor` setzt die Zeitstempel über `ITimestamped`, die Benutzer über `IAuditable` |
| `IHardDeletable` (Marker) | dto. | Entitäten, die der Fachcode **hart** löscht wie das Original (`UserFavorite`, `UserRecentVisit`, Cleanup-Jobs); `SoftDeleteInterceptor` lässt `EntityState.Deleted` für sie unverändert, wenn der Aufrufer `IHardDelete.Remove(entity)` nutzt (D02-ADR-03) |
| `[ContractPhase("vX.Y")]` | `Plane.Data/Migrations/ContractPhaseAttribute.cs` | Kennzeichnet Contract-Schritte (Drop/Rename/Typänderung); Architekturtest `MigrationsAreExpandOnly` (D14 §3.17) |
| `QueryFilterNames` | `Plane.BuildingBlocks.Persistence/QueryFilterNames.cs` | Konstanten `SoftDelete = "soft_delete"`, `WorkspaceTenant = "workspace_tenant"` (01 ADR-037) |
| `JsonNodeValueConverter<T>` + `JsonNodeComparer<T>` | `Plane.Data/Conventions/Json/` | `JsonObject`/`JsonNode`/`JsonArray` ↔ `jsonb` (D03-ADR-13) |
| `ScopeForeignKeyConvention` | `Plane.Data/Conventions/ScopeForeignKeyConvention.cs` | legt für jede Entität mit `WorkspaceId` + `ProjectId` den Scope-FK an (D03-ADR-05); wird nach `ApplyConfigurationsFromAssembly` und vor `AuditForeignKeyConvention` (D02 §5.1.3) ausgeführt |
| `TrigramIndexExtensions.HasTrigramIndex(...)` | `Plane.Data/Conventions/` | `HasIndex(x => x.Name).HasMethod("gin").HasOperators("gin_trgm_ops").HasDatabaseName("ix_<t>_<c>_trgm")` |
| `PlaneDbFunctions.Unaccent(string)` | `Plane.Data/Functions/` | Abbildung der SQL-Funktion `plane_unaccent(text)` für LINQ |

#### 3.1.3 Namensregeln (D03-ADR-02/-03)

| Element | Regel | Beispiel |
|---|---|---|
| Tabelle | Plural, `snake_case`, Fachobjekt **Work Item** | `work_items`, `work_item_comments`, `cycle_work_items` |
| Entität | Singular PascalCase, `WorkItem…` | `WorkItemComment`, `CycleWorkItem` |
| FK-Spalte | `<ziel>_id`; Rollen-FKs mit Rollenname wie Original | `work_item_id`, `assignee_id`, `owned_by_id`, `duplicate_to_id` |
| Bool-Spalten | Original-Namen (`is_*`, Feature-Toggles `cycle_view` …) | `is_triage`, `guest_view_all_features` |
| SQL-Schlüsselwörter | bleiben als Spaltennamen, EF quotet; Raw-SQL muss quoten | `states."group"`, `states."default"`, `page_logs."transaction"` |
| Constraint/Index | `pk_`, `fk_`, `ix_`, `ux_`, `ck_`, `ak_`; Original-Namen partieller Unique-Constraints bleiben | `ux_work_items_project_sequence_id`, `state_unique_name_project_when_deleted_at_null` |
| C#-Property für Nicht-FK-Spalten mit `_id`-ähnlicher Kollision | `HasColumnName` | `Webhook.ProjectEvents` → Spalte `project` |

### 3.2 Typabbildung Django → PostgreSQL → C#

| Django-Feld | PostgreSQL | C# | Regel |
|---|---|---|---|
| `UUIDField(primary_key)` | `uuid` | `Guid` | UUIDv7 aus `IIdGenerator` (D03-ADR-04) |
| `UUIDField` | `uuid` | `Guid`/`Guid?` | polymorphe Referenzen ohne FK |
| `ForeignKey`/`OneToOneField` | `uuid` | `Guid`/`Guid?` | Spalte `<name>_id`; `OneToOne` zusätzlich Unique-Index |
| `CharField(max_length=n)`, `SlugField(max_length=n)` | `varchar(n)` | `string`/`string?` | Länge 1:1 |
| `URLField` | `varchar(max_length ?? 200)` | `string` | Django-Default 200 |
| `TextField` | `text` | `string`/`string?` | `blank=True` ohne `null` → `NOT NULL DEFAULT ''` nur, wenn das Original einen Default hat; sonst setzt der Fachcode `""` |
| `BooleanField` | `boolean` | `bool` | DB-Default = Original-Default |
| `IntegerField` / `PositiveIntegerField` | `integer` | `int` | Positive* → Check `>= 0`; Validatoren `Min/Max` → Check |
| `PositiveSmallIntegerField` | `smallint` | `short` bzw. C#-`enum : short` | Choices → Check |
| `BigIntegerField` / `PositiveBigIntegerField` | `bigint` | `long` | – |
| `FloatField` | `double precision` | `double` | JSON mit Dezimalteil (§4.4) |
| `DateTimeField` | `timestamptz` (6) | `DateTimeOffset`/`DateTimeOffset?` | `auto_now(_add)` → `AuditInterceptor`/Fachcode, kein DB-Default |
| `DateField` | `date` | `DateOnly`/`DateOnly?` | – |
| `JSONField` | `jsonb` | `JsonObject` (Default), `JsonNode`, `JsonArray` | D03-ADR-13, §3.8 |
| `BinaryField` | `bytea` | `byte[]?` | Größen-Check bei Beschreibungen |
| `ArrayField(UUIDField)` | `uuid[]` | `List<Guid>` | Npgsql-Array-Mapping |
| `ArrayField(URLField)` | `text[]` | `List<string>` | Original `varchar(200)[]` |
| `GenericIPAddressField` | `inet` | `IPAddress?` | Npgsql-Mapping |
| `FileField(max_length=n)` | `varchar(n)` | `string` | speichert den Objekt-Key, nie Binärdaten |
| `default=callable` | – bzw. Literal | Fabrik/`JsonDefaults` | zufällige/zeitabhängige Defaults setzt der Code (`ColorGenerator`, `TokenGenerator`, `AnchorGenerator`); konstante JSON-Defaults als `JsonDefaults.<Quelle>.<Name>` **und** gleiches DB-Literal |

### 3.3 Tabellenverzeichnis (Eigentümer, Inkrement, Herkunft)

Vollständige Liste aller Zieltabellen des `PlaneDbContext` (ohne `__EFMigrationsHistory`). „Basis“ siehe §3.1.1. Die Spalte „Eigentümer-Modul“ ist der Wert von `[OwnedBy]` (R3); nur dieses Modul legt Zeilen an, ändert oder löscht sie (Ausnahme: deklarierte Soft-Delete-Kaskaden, D02 §5.2.3). Die Liste ist maschinenlesbar in `_data/03-datenmodell.json` (`tables[]`).

| Nr. | Tabelle | Entität | Eigentümer-Modul | Basis | ab | Original | Status | CE-IDs (Haupt) | Detail |
|---|---|---|---|---|---|---|---|---|---|
| T001 | `users` | `User` | `Identity` | X | I0 | `User` (`M/user.py`) | angepasst | CE-AUTH-012, CE-AUTH-024, CE-AUTH-027, CE-PROF-001, CE-PROF-003, CE-PROF-004, CE-PROF-005, CE-PROF-006 | §3.4.1.1 |
| T002 | `profiles` | `Profile` | `Identity` | X | I0 | `Profile` (`M/user.py`) | angepasst | CE-PROF-001, CE-PROF-006, CE-AUTH-030, CE-HOME-003, CE-HOME-006 | §3.4.1.2 |
| T003 | `user_sessions` | `UserSession` | `Identity` | X | I0 | `Session` (`M/session.py`) | ersetzt | CE-AUTH-022, CE-AUTH-023, CE-AUTH-024, CE-AUTH-025 | §3.4.1.3 |
| T004 | `api_tokens` | `ApiToken` | `Identity` | A | I1 | `APIToken` (`M/api.py`) | angepasst | CE-WH-012, CE-WH-013, CE-WH-014, CE-API-001 | §3.4.1.4 |
| T005 | `api_activity_logs` | `ApiActivityLog` | `Identity` | A | I6 | `APIActivityLog` (`M/api.py`) | angepasst | CE-API-003, CE-OPS-015 | §3.4.1.5 |
| T006 | `instances` | `Instance` | `Instance` | A | I0 | `Instance` (`LIC/instance.py`) | angepasst | CE-INST-001, CE-INST-003, CE-INST-005, CE-INST-006 | §3.4.2.1 |
| T007 | `instance_admins` | `InstanceAdminMirror` | `Instance` | A | I0 | `InstanceAdmin` (`LIC/instance.py`) | angepasst | CE-INST-004 (angepasst: Spiegel der Keycloak-Rolle) | §3.4.2.2 |
| T008 | `instance_configurations` | `InstanceConfiguration` | `Instance` | A | I0 | `InstanceConfiguration` (`LIC/instance.py`) | angepasst | CE-INST-002, CE-INST-017, CE-INST-018, CE-INST-025, CE-INST-026, CE-INST-028 | §3.4.2.3 |
| T009 | `workspaces` | `Workspace` | `Workspaces` | A | I0 | `Workspace` (`M/workspace.py`) | angepasst | CE-WS-001, CE-WS-003, CE-WS-004, CE-WS-005, CE-INST-027, CE-INST-029 | §3.4.3.1 |
| T010 | `workspace_members` | `WorkspaceMember` | `Workspaces` | A | I0 | `WorkspaceMember` (`M/workspace.py`) | angepasst | CE-WS-008, CE-WS-009, CE-WS-012, CE-LV-015, CE-PROF-008 | §3.4.3.2 |
| T011 | `workspace_member_invites` | `WorkspaceMemberInvite` | `Workspaces` | A | I1 | `WorkspaceMemberInvite` (`M/workspace.py`) | übernommen | CE-WS-010, CE-WS-011, CE-AUTH-028, CE-API-013 | §3.4.3.3 |
| T012 | `workspace_themes` | `WorkspaceTheme` | `Workspaces` | A | I1 | `WorkspaceTheme` (`M/workspace.py`) | übernommen | CE-WS-007 | §3.4.3.4 |
| T013 | `workspace_user_properties` | `WorkspaceUserProperties` | `Workspaces` | A | I1 | `WorkspaceUserProperties` (`M/workspace.py`) | übernommen | CE-LV-015, CE-WS-022 | §3.4.3.5 |
| T014 | `workspace_user_preferences` | `WorkspaceUserPreference` | `Workspaces` | A | I1 | `WorkspaceUserPreference` (`M/workspace.py`) | übernommen | CE-WS-021, CE-WS-022 | §3.4.3.6 |
| T015 | `user_favorites` | `UserFavorite` | `Workspaces` | W | I1 | `UserFavorite` (`M/favorite.py`) | übernommen | CE-WS-023, CE-CYC-015, CE-MOD-011, CE-LV-050, CE-PAGE-010 | §3.4.3.7 |
| T016 | `projects` | `Project` | `Projects` | A | I0 | `Project` (`M/project.py`) | angepasst | CE-PRJ-001…CE-PRJ-010, CE-PRJ-016, CE-PRJ-018, CE-PRJ-019, CE-PRJ-022, CE-PRJ-026, CE-PRJ-039, CE-PRJ-040, CE-API-006…CE-API-008 | §3.4.4.1 |
| T017 | `project_identifiers` | `ProjectIdentifier` | `Projects` | X | I0 | `ProjectIdentifier` (`M/project.py`) | übernommen | CE-PRJ-005 | §3.4.4.2 |
| T018 | `project_members` | `ProjectMember` | `Projects` | P | I0 | `ProjectMember` (`M/project.py`) | angepasst | CE-PRJ-006, CE-PRJ-007, CE-PRJ-021, CE-API-012, CE-WS-008 | §3.4.4.3 |
| T019 | `project_member_invites` | `ProjectMemberInvite` | `Projects` | P | I1 | `ProjectMemberInvite` (`M/project.py`) | übernommen | CE-PRJ-010 (defekt, nur API – Vertrag erhalten) | §3.4.4.4 |
| T020 | `project_user_properties` | `ProjectUserProperty` | `Projects` | P | I0 | `ProjectUserProperty` (`M/project.py`) | übernommen | CE-PRJ-016, CE-LV-014, CE-PRJ-011, CE-PRJ-015 | §3.4.4.5 |
| T021 | `states` | `State` | `Projects` | P | I0 | `State` (`M/state.py`) | angepasst | CE-PRJ-023…CE-PRJ-027, CE-INT-001, CE-API-009 | §3.4.4.6 |
| T022 | `labels` | `Label` | `Projects` | W | I1 | `Label` (`M/label.py`) | angepasst | CE-PRJ-028…CE-PRJ-033, CE-WI-024, CE-API-010 | §3.4.4.7 |
| T023 | `estimates` | `Estimate` | `Projects` | P | I1 | `Estimate` (`M/estimate.py`) | übernommen | CE-PRJ-034…CE-PRJ-038, CE-WI-027 | §3.4.4.8 |
| T024 | `estimate_points` | `EstimatePoint` | `Projects` | P | I1 | `EstimatePoint` (`M/estimate.py`) | übernommen | CE-PRJ-035…CE-PRJ-037, CE-WI-027 | §3.4.4.9 |
| T025 | `work_items` | `WorkItem` | `WorkItems` | P | I2 | `Issue` (`M/issue.py`) | angepasst | CE-WI-001…CE-WI-049, CE-LV-005, CE-API-017…CE-API-019 | §3.4.5.1 |
| T026 | `work_item_sequences` | `WorkItemSequence` | `WorkItems` | X | I2 | `IssueSequence` (`M/issue.py`) | ersetzt | CE-WI-002 | §3.4.5.2 |
| T027 | `work_item_assignees` | `WorkItemAssignee` | `WorkItems` | P | I2 | `IssueAssignee` (`M/issue.py`) | übernommen | CE-WI-023, CE-LV-010 | §3.4.5.3 |
| T028 | `work_item_labels` | `WorkItemLabel` | `WorkItems` | P | I2 | `IssueLabel` (`M/issue.py`) | angepasst | CE-WI-024, CE-LV-010 | §3.4.5.4 |
| T029 | `work_item_relations` | `WorkItemRelation` | `WorkItems` | P | I2 | `IssueRelation` (`M/issue.py`) | angepasst | CE-WI-033, CE-LV-033, CE-API-024 | §3.4.5.5 |
| T030 | `work_item_mentions` | `WorkItemMention` | `WorkItems` | P | I2 | `IssueMention` (`M/issue.py`) | übernommen | CE-WI-044, CE-NOTIF-002 | §3.4.5.6 |
| T031 | `work_item_subscribers` | `WorkItemSubscriber` | `WorkItems` | P | I2 | `IssueSubscriber` (`M/issue.py`) | übernommen | CE-WI-043, CE-NOTIF-003 | §3.4.5.7 |
| T032 | `work_item_links` | `WorkItemLink` | `WorkItems` | P | I2 | `IssueLink` (`M/issue.py`) | übernommen | CE-WI-035, CE-API-020 | §3.4.5.8 |
| T033 | `work_item_comments` | `WorkItemComment` | `WorkItems` | P | I2 | `IssueComment` (`M/issue.py`) | angepasst | CE-WI-037, CE-WI-044, CE-API-021, CE-SPACE-025 | §3.4.5.9 |
| T034 | `work_item_reactions` | `WorkItemReaction` | `WorkItems` | P | I2 | `IssueReaction` (`M/issue.py`) | übernommen | CE-WI-038, CE-SPACE-027 | §3.4.5.10 |
| T035 | `work_item_comment_reactions` | `WorkItemCommentReaction` | `WorkItems` | P | I2 | `CommentReaction` (`M/issue.py`) | übernommen | CE-WI-038, CE-SPACE-026 | §3.4.5.11 |
| T036 | `work_item_votes` | `WorkItemVote` | `WorkItems` | P | I6 | `IssueVote` (`M/issue.py`) | übernommen | CE-SPACE-028 | §3.4.5.12 |
| T037 | `work_item_activities` | `WorkItemActivity` | `WorkItems` | P | I2 | `IssueActivity` (`M/issue.py`) | angepasst | CE-WI-039, CE-WI-040, CE-API-022, CE-PROF-010, CE-NOTIF-001 | §3.4.5.13 |
| T038 | `work_item_description_versions` | `WorkItemDescriptionVersion` | `WorkItems` | P | I2 | `IssueDescriptionVersion` (`M/issue.py`) | übernommen | CE-WI-041 | §3.4.5.14 |
| T039 | `work_item_versions` | `WorkItemVersion` | `WorkItems` | P | I2 | `IssueVersion` (`M/issue.py`) | korrigiert | CE-WI-042 | §3.4.5.15 |
| T040 | `draft_work_items` | `DraftWorkItem` | `WorkItems` | W | I2 | `DraftIssue` (`M/draft.py`) | angepasst | CE-WI-049, CE-WI-007 | §3.4.5.16 |
| T041 | `draft_work_item_assignees` | `DraftWorkItemAssignee` | `WorkItems` | W | I2 | `DraftIssueAssignee` (`M/draft.py`) | übernommen | CE-WI-049 | §3.4.5.17 |
| T042 | `draft_work_item_labels` | `DraftWorkItemLabel` | `WorkItems` | W | I2 | `DraftIssueLabel` (`M/draft.py`) | angepasst | CE-WI-049 | §3.4.5.18 |
| T043 | `draft_work_item_modules` | `DraftWorkItemModule` | `WorkItems` | W | I3 | `DraftIssueModule` (`M/draft.py`) | übernommen | CE-WI-049 | §3.4.5.19 |
| T044 | `draft_work_item_cycles` | `DraftWorkItemCycle` | `WorkItems` | W | I3 | `DraftIssueCycle` (`M/draft.py`) | übernommen | CE-WI-049 | §3.4.5.20 |
| T045 | `work_item_types` | `WorkItemType` | `Properties` | W | I2 | `IssueType` (`M/issue_type.py`) | minimal | – (A1-Andockstelle; CE liest nur `NULL`) | §3.4.5.21 |
| T046 | `cycles` | `Cycle` | `Cycles` | P | I3 | `Cycle` (`M/cycle.py`) | übernommen | CE-CYC-001…CE-CYC-015, CE-API-026…CE-API-029, CE-ANA-008 | §3.4.6.1 |
| T047 | `cycle_work_items` | `CycleWorkItem` | `Cycles` | P | I3 | `CycleIssue` (`M/cycle.py`) | angepasst | CE-CYC-010, CE-CYC-011, CE-API-027, CE-WI-025 | §3.4.6.2 |
| T048 | `cycle_user_properties` | `CycleUserProperties` | `Cycles` | P | I3 | `CycleUserProperties` (`M/cycle.py`) | übernommen | CE-LV-016 | §3.4.6.3 |
| T049 | `modules` | `Module` | `ProjectModules` | P | I3 | `Module` (`M/module.py`) | angepasst | CE-MOD-001…CE-MOD-011, CE-API-030…CE-API-032, CE-ANA-008 | §3.4.7.1 |
| T050 | `module_members` | `ModuleMember` | `ProjectModules` | P | I3 | `ModuleMember` (`M/module.py`) | übernommen | CE-MOD-006 | §3.4.7.2 |
| T051 | `module_work_items` | `ModuleWorkItem` | `ProjectModules` | P | I3 | `ModuleIssue` (`M/module.py`) | übernommen | CE-MOD-008, CE-API-031, CE-WI-026 | §3.4.7.3 |
| T052 | `module_links` | `ModuleLink` | `ProjectModules` | P | I3 | `ModuleLink` (`M/module.py`) | übernommen | CE-MOD-005 | §3.4.7.4 |
| T053 | `module_user_properties` | `ModuleUserProperties` | `ProjectModules` | P | I3 | `ModuleUserProperties` (`M/module.py`) | übernommen | CE-LV-016 | §3.4.7.5 |
| T054 | `views` | `View` | `Views` | W | I3 | `IssueView` (`M/view.py`) | angepasst | CE-LV-011, CE-LV-047…CE-LV-054 | §3.4.8.1 |
| T055 | `intakes` | `Intake` | `Intake` | P | I3 | `Intake` (`M/intake.py`) | übernommen | CE-INT-001, CE-API-025 | §3.4.9.1 |
| T056 | `intake_work_items` | `IntakeWorkItem` | `Intake` | P | I3 | `IntakeIssue` (`M/intake.py`) | angepasst | CE-INT-002…CE-INT-012, CE-SPACE-006, CE-API-025 | §3.4.9.2 |
| T057 | `pages` | `Page` | `Pages` | X | I4 | `Page` (`M/page.py`) | angepasst | CE-PAGE-001…CE-PAGE-012, CE-PAGE-019, CE-RT-003, CE-RT-005 | §3.4.10.1 |
| T058 | `project_pages` | `ProjectPage` | `Pages` | X | I4 | `ProjectPage` (`M/page.py`) | übernommen | CE-PAGE-001, CE-PAGE-003, CE-PAGE-009 | §3.4.10.2 |
| T059 | `page_labels` | `PageLabel` | `Pages` | X | I4 | `PageLabel` (`M/page.py`) | übernommen | CE-PAGE-004 | §3.4.10.3 |
| T060 | `page_logs` | `PageLog` | `Pages` | X | I4 | `PageLog` (`M/page.py`) | korrigiert | CE-PAGE-012 | §3.4.10.4 |
| T061 | `page_versions` | `PageVersion` | `Pages` | X | I4 | `PageVersion` (`M/page.py`) | korrigiert | CE-PAGE-019 | §3.4.10.5 |
| T062 | `file_assets` | `FileAsset` | `Assets` | X | I1 | `FileAsset` (`M/asset.py`) | angepasst | CE-OPS-012, CE-OPS-013, CE-WI-036, CE-PAGE-018, CE-SPACE-007, CE-API-015, CE-API-016 | §3.4.11.1 |
| T063 | `workspace_home_preferences` | `WorkspaceHomePreference` | `Home` | A | I5 | `WorkspaceHomePreference` (`M/workspace.py`) | übernommen | CE-HOME-001, CE-HOME-002 | §3.4.12.1 |
| T064 | `workspace_user_links` | `WorkspaceUserLink` | `Home` | W | I5 | `WorkspaceUserLink` (`M/workspace.py`) | übernommen | CE-HOME-004 | §3.4.12.2 |
| T065 | `user_recent_visits` | `UserRecentVisit` | `Home` | W | I5 | `UserRecentVisit` (`M/recent_visit.py`) | angepasst | CE-HOME-005 | §3.4.12.3 |
| T066 | `stickies` | `Sticky` | `Home` | X | I5 | `Sticky` (`M/sticky.py`) | übernommen | CE-HOME-008…CE-HOME-010, CE-API-014 | §3.4.12.4 |
| T067 | `analytic_views` | `AnalyticView` | `Analytics` | X | I5 | `AnalyticView` (`M/analytic.py`) | angepasst | CE-ANA-009 | §3.4.13.1 |
| T068 | `notifications` | `Notification` | `Notifications` | X | I5 | `Notification` (`M/notification.py`) | übernommen | CE-NOTIF-001…CE-NOTIF-007, CE-INT-012 | §3.4.14.1 |
| T069 | `user_notification_preferences` | `UserNotificationPreference` | `Notifications` | A | I1 | `UserNotificationPreference` (`M/notification.py`) | angepasst | CE-NOTIF-008, CE-NOTIF-009 | §3.4.14.2 |
| T070 | `email_notification_logs` | `EmailNotificationLog` | `Notifications` | A | I5 | `EmailNotificationLog` (`M/notification.py`) | übernommen | CE-NOTIF-008, CE-OPS-015 | §3.4.14.3 |
| T071 | `deploy_boards` | `DeployBoard` | `PublicSpace` | W | I6 | `DeployBoard` (`M/deploy_board.py`) | übernommen | CE-SPACE-001…CE-SPACE-005, CE-SPACE-017 | §3.4.15.1 |
| T072 | `project_public_members` | `ProjectPublicMember` | `PublicSpace` | P | I6 | `ProjectPublicMember` (`M/project.py`) | übernommen | CE-SPACE-025, CE-SPACE-026, CE-SPACE-027, CE-SPACE-028 | §3.4.15.2 |
| T073 | `webhooks` | `Webhook` | `Webhooks` | X | I6 | `Webhook` (`M/webhook.py`) | angepasst | CE-WH-001…CE-WH-006, CE-WH-009, CE-WH-011 | §3.4.16.1 |
| T074 | `webhook_logs` | `WebhookLog` | `Webhooks` | X | I6 | `WebhookLog` (`M/webhook.py`) | übernommen | CE-WH-007, CE-WH-010, CE-OPS-015 | §3.4.16.2 |
| T075 | `exports` | `ExportJob` | `Exports` | X | I6 | `ExporterHistory` (`M/exporter.py`) | angepasst | CE-EXP-001, CE-EXP-002 | §3.4.17.1 |
| T076 | `user_identities` | `UserIdentity` | `Identity` | X | I0 | – (neu, D05 §3.7.1) | neu | CE-AUTH-012, CE-AUTH-022, CE-AUTH-028 | §3.4.18 |
| T077 | `roles` | `Role` | `Authorization` | X | I0 | – (neu, D05 §3.13.3) | neu | CE-WS-008 | §3.4.18 |
| T078 | `role_permissions` | `RolePermission` | `Authorization` | X | I0 | – (neu, E5-Vorhalt, CE leer) | minimal | – | §3.4.18 |
| T079 | `data_protection_keys` | `DataProtectionKey` | `Instance` | X | I0 | – (neu, D05-ADR-25) | neu | CE-OPS-018 (Basis), CE-AUTH-024 | §3.4.18 |
| T080 | `workspace_feature_settings` | `WorkspaceFeatureSetting` | `Workspaces` | X | I1 | – (neu, D16 E-01) | minimal | – | §3.4.18 |
| T081 | `project_feature_settings` | `ProjectFeatureSetting` | `Projects` | X | I1 | – (neu, D16 E-01) | minimal | CE-PRJ-019 (Katalog) | §3.4.18 |
| T082 | `work_item_relation_types` | `WorkItemRelationType` | `WorkItems` | X | I2 | `IssueRelationChoices` (`M/issue.py` Z. 272–293) | neu (Katalog) | CE-WI-033 | §3.4.18 |
| T083 | `outbox_messages` | `OutboxMessage` | `Messaging` | X | I0 | – (neu, ADR-020, ABG-053) | neu | CE-OPS-016 (Basis) | §3.4.18 |
| T084 | `inbox_messages` | `InboxMessage` | `Messaging` | X | I0 | – (neu, ADR-020) | neu | CE-OPS-016 (Basis) | §3.4.18 |
| T085 | `jobs` | `Job` | `Messaging` | X | I0 | – (ersetzt Celery/RabbitMQ) | neu | CE-OPS-016 | §3.4.18 |
| T086 | `recurring_jobs` | `RecurringJob` | `Messaging` | X | I0 | – (ersetzt `django_celery_beat`) | neu | CE-OPS-016 | §3.4.18 |
| T087 | `integration_connections` | `IntegrationConnection` | `Integrations` | X | I0 | – (neu, D16 §3.4.2) | minimal | – | §3.4.18 |
| T088 | `external_links` | `ExternalLink` | `Integrations` | X | I2 | – (neu, D16 §3.4.2) | minimal | – | §3.4.18 |
| T089 | `search_documents` | `SearchDocument` | `Search` | X | I5 | – (neu, D16 §3.3.7 G1, ADR-024) | neu | CE-SRCH-001, CE-SRCH-002, CE-SRCH-003 | §3.4.18 |

Summe: 89 Tabellen

### 3.4 Tabellen je Modul (Spalten, Schlüssel, Indizes, Checks)

**Lesehilfe.** Je Tabelle: Kopfzeile mit Entität, Eigentümer, Basis, Inkrement, Status, CE-IDs; dann alle **fachlichen** Spalten in Original-Reihenfolge (Basis-Spalten nach §3.1.1 sind nicht wiederholt, außer bei Basis X). „Default“: DB-Default (`DEFAULT …` in der Migration); „C#:“ = nur im Code gesetzt; `JsonDefaults.*` = konstantes Literal (§3.8.2), zugleich DB-Default. FK-Angaben nennen das Lösch-Verhalten der **DB** (harte Löschung); das Soft-Delete-Verhalten steht in §3.5.4. Durchgestrichene Spalten entfallen. Zusätzlich gilt für alle Basen W/P der Scope-FK (D03-ADR-05) und für alle Basen A/W/P der Index `ix_<tabelle>_workspace_id`/`ix_<tabelle>_project_id`, den EF für FKs automatisch anlegt.

#### 3.4.1 Modul Identity (Benutzer, Sessions, API-Tokens)

##### 3.4.1.1 `users` ← `User` (`M/user.py` Z. 56–197)

Entität `User` · `[OwnedBy("Identity")]` · Basis eigene Form (Spalten vollständig gelistet) · ab **I0** · Status **angepasst** · CE-IDs: CE-AUTH-012, CE-AUTH-024, CE-AUTH-027, CE-PROF-001, CE-PROF-003, CE-PROF-004, CE-PROF-005, CE-PROF-006

| Spalte | PostgreSQL | Null | Default | C#-Property: Typ | Herkunft / Regel |
|---|---|---|---|---|---|
| `id` | `uuid` | nein | – (App: UUIDv7) | Id: `Guid` | PK, UUIDv7 (`IIdGenerator`) |
| `username` | `varchar(128)` | nein | – | Username: `string` | bei JIT-Anlage `uuid4().hex`-Format (32 Hex) wie Original; unique |
| `mobile_number` | `varchar(255)` | ja | – | MobileNumber: `string?` | 1:1 |
| `email` | `varchar(255)` | nein | – | Email: `string` | Original nullable; Ziel NOT NULL (JIT nur mit verifizierter E-Mail, Bots mit synthetischer Adresse); lowercase; unique voll (Benutzer werden nie soft-gelöscht) |
| `display_name` | `varchar(255)` | nein | `''` | DisplayName: `string` | 1:1 |
| `first_name` | `varchar(255)` | nein | – | FirstName: `string` | 1:1 |
| `last_name` | `varchar(255)` | nein | – | LastName: `string` | 1:1 |
| `avatar` | `text` | nein | – | Avatar: `string` | 1:1 |
| `avatar_asset_id` | `uuid` | ja | – | AvatarAssetId: `Guid?` | FK `file_assets` ON DELETE SET NULL |
| `cover_image` | `varchar(800)` | ja | – | CoverImage: `string?` | 1:1 |
| `cover_image_asset_id` | `uuid` | ja | – | CoverImageAssetId: `Guid?` | FK `file_assets` ON DELETE SET NULL |
| `date_joined` | `timestamptz` | nein | – | DateJoined: `DateTimeOffset` | setzt Fachcode bei Anlage (= `created_at`) |
| `created_at` | `timestamptz` | nein | – | CreatedAt: `DateTimeOffset` | `AuditInterceptor` über `ITimestamped` (§3.1.2) |
| `updated_at` | `timestamptz` | nein | – | UpdatedAt: `DateTimeOffset` | `AuditInterceptor` |
| `last_location` | `varchar(255)` | nein | – | LastLocation: `string` | 1:1 |
| `created_location` | `varchar(255)` | nein | – | CreatedLocation: `string` | 1:1 |
| ~~`is_superuser`~~ | – | – | – | – | entfällt: Django-Admin-Konzept; DTO liefert konstant `false` (D05 §3.7.1-Muster) |
| `is_managed` | `boolean` | nein | false | IsManaged: `bool` | 1:1 |
| ~~`is_password_expired`~~ | – | – | – | – | entfällt: ADR-008 (D05 §4.8); DTO konstant `false` |
| `is_active` | `boolean` | nein | true | IsActive: `bool` | 1:1 |
| ~~`is_staff`~~ | – | – | – | – | entfällt: Django-Admin-Konzept; DTO liefert konstant `false` |
| `is_email_verified` | `boolean` | nein | false | IsEmailVerified: `bool` | 1:1 |
| ~~`is_password_autoset`~~ | – | – | – | – | entfällt: ADR-008; DTO konstant `false` (D05 §3.7.1) |
| ~~`is_password_reset_required`~~ | – | – | – | – | entfällt: ADR-008; DTO konstant `false` |
| ~~`token`~~ | – | – | – | – | entfällt: ADR-008 (D05 §4.8); Original rotiert es bei jedem Save (02a §3.22 #21) |
| `last_active` | `timestamptz` | ja | `now()` | LastActive: `DateTimeOffset?` | 1:1 |
| `last_login_time` | `timestamptz` | ja | – | LastLoginTime: `DateTimeOffset?` | 1:1 |
| `last_logout_time` | `timestamptz` | ja | – | LastLogoutTime: `DateTimeOffset?` | 1:1 |
| `last_login_ip` | `varchar(255)` | nein | – | LastLoginIp: `string` | 1:1 |
| `last_logout_ip` | `varchar(255)` | nein | – | LastLogoutIp: `string` | 1:1 |
| `last_login_medium` | `varchar(20)` | nein | `'oidc'` | LastLoginMedium: `string` | neu immer `"oidc"` (D05 §3.7.1); DB-Default `oidc` statt Original `email` |
| `last_login_uagent` | `text` | nein | – | LastLoginUagent: `string` | 1:1 |
| ~~`token_updated_at`~~ | – | – | – | – | entfällt: ADR-008 |
| `is_bot` | `boolean` | nein | false | IsBot: `bool` | 1:1 |
| `bot_type` | `varchar(30)` | ja | – | BotType: `string?` | `WORKSPACE_SEED` (Seed-Bot), reserviert `integration` (D16-ADR-12), `app` (H1) |
| `user_timezone` | `varchar(255)` | nein | `'UTC'` | UserTimezone: `string` | IANA-Name, Check gegen Liste `pytz.common_timezones` nur im Validator (`TimeZoneCatalog`), nicht als DB-Check |
| `is_email_valid` | `boolean` | nein | false | IsEmailValid: `bool` | 1:1 |
| `masked_at` | `timestamptz` | ja | – | MaskedAt: `DateTimeOffset?` | 1:1 |
| `password` | – | – | – | – | entfällt (ADR-008); ebenso `last_login` aus `AbstractBaseUser` und die M2M-Tabellen `users_groups`/`users_user_permissions` aus `PermissionsMixin` |

**Indizes/Unique:** `ux_users_email` UNIQUE (`email`); `ux_users_username` UNIQUE (`username`); GIN-Trigram `ix_users_display_name_trgm`, `ix_users_first_name_trgm`, `ix_users_last_name_trgm` (`gin_trgm_ops`, Mention-Suche CE-SRCH-002, ab I5).

**Checks:** `ck_users_email_lowercase` CHECK (`email = lower(email)`).

**Hinweise:** Kein Soft-Delete (Original `User` erbt nicht von `SoftDeleteModel`); Konten werden deaktiviert (`is_active=false`, CE-PROF-005). Benutzerzeilen werden **nie** hart gelöscht (D03-ADR-07). Implementiert nur `ITimestamped` (`created_at`/`updated_at`, keine `created_by_id`-Spalte, wie Original).

##### 3.4.1.2 `profiles` ← `Profile` (`M/user.py` Z. 200–268)

Entität `Profile` · `[OwnedBy("Identity")]` · Basis eigene Form (Spalten vollständig gelistet) · ab **I0** · Status **angepasst** · CE-IDs: CE-PROF-001, CE-PROF-006, CE-AUTH-030, CE-HOME-003, CE-HOME-006

| Spalte | PostgreSQL | Null | Default | C#-Property: Typ | Herkunft / Regel |
|---|---|---|---|---|---|
| `id` | `uuid` | nein | – (App: UUIDv7) | Id: `Guid` | PK (UUIDv7, `IIdGenerator`) |
| `user_id` | `uuid` | nein | – | UserId: `Guid` | FK `users` ON DELETE CASCADE; 1:1 (unique) |
| `theme` | `jsonb` | nein | `'{}'::jsonb` | Theme: `JsonObject` | Lesemodell `ProfileTheme` |
| `is_app_rail_docked` | `boolean` | nein | true | IsAppRailDocked: `bool` | 1:1 |
| `is_tour_completed` | `boolean` | nein | false | IsTourCompleted: `bool` | 1:1 |
| `onboarding_step` | `jsonb` | nein | `JsonDefaults.Onboarding` (DB-Default = gleiches Literal) | OnboardingStep: `JsonObject` | Lesemodell `OnboardingSteps` |
| `use_case` | `text` | ja | – | UseCase: `string?` | 1:1 |
| `role` | `varchar(300)` | ja | – | Role: `string?` | 1:1 |
| `is_onboarded` | `boolean` | nein | false | IsOnboarded: `bool` | 1:1 |
| `last_workspace_id` | `uuid` | ja | – | LastWorkspaceId: `Guid?` | bewusst ohne FK wie Original (wird beim Workspace-Löschen per Handler genullt, 02a §3.3) |
| ~~`billing_address_country`~~ | – | – | – | – | entfällt: ADR-001 (Billing entfällt); DTO liefert `"INDIA"` konstant, falls Vertrag es verlangt |
| ~~`billing_address`~~ | – | – | – | – | entfällt: ADR-001; DTO konstant `null` |
| ~~`has_billing_address`~~ | – | – | – | – | entfällt: ADR-001; DTO konstant `false` |
| `company_name` | `varchar(255)` | nein | – | CompanyName: `string` | 1:1 |
| `notification_view_mode` | `varchar(255)` | nein | `'full'` | NotificationViewMode: `string` | Choices: NotificationViewMode.choices |
| `is_smooth_cursor_enabled` | `boolean` | nein | false | IsSmoothCursorEnabled: `bool` | 1:1 |
| `is_mobile_onboarded` | `boolean` | nein | false | IsMobileOnboarded: `bool` | 1:1 |
| `mobile_onboarding_step` | `jsonb` | nein | `JsonDefaults.MobileOnboarding` (DB-Default = gleiches Literal) | MobileOnboardingStep: `JsonObject` | Lesemodell `MobileOnboardingSteps` |
| `mobile_timezone_auto_set` | `boolean` | nein | false | MobileTimezoneAutoSet: `bool` | 1:1 |
| `language` | `varchar(255)` | nein | `'en'` | Language: `string` | 1:1 |
| `start_of_the_week` | `smallint` | nein | `0` | StartOfTheWeek: `short` | 0=Sunday … 6=Saturday |
| `goals` | `jsonb` | nein | `'{}'::jsonb` | Goals: `JsonObject` | frei |
| `background_color` | `varchar(255)` | nein | C#: `ColorGenerator.Random()` | BackgroundColor: `string` | Default per `ColorGenerator.Random()` (Port `get_random_color`, Großbuchstaben-Hex – Korrektur 02a §3.22 #18) |
| `is_navigation_tour_completed` | `boolean` | nein | false | IsNavigationTourCompleted: `bool` | 1:1 |
| `has_marketing_email_consent` | `boolean` | nein | false | HasMarketingEmailConsent: `bool` | 1:1 |
| `is_subscribed_to_changelog` | `boolean` | nein | false | IsSubscribedToChangelog: `bool` | 1:1 |
| `product_tour` | `jsonb` | nein | `JsonDefaults.ProductTour` (DB-Default = gleiches Literal) | ProductTour: `JsonObject` | Lesemodell `ProductTour` |

**Indizes/Unique:** `ux_profiles_user_id` UNIQUE (`user_id`).

**Checks:** `ck_profiles_start_of_the_week` CHECK (`start_of_the_week BETWEEN 0 AND 6`); `ck_profiles_notification_view_mode` CHECK (`notification_view_mode IN ('full','compact')`).

**Hinweise:** Basis Original `TimeAuditModel` → `ITimestamped` (`created_at`/`updated_at`), kein Soft-Delete, keine Audit-Benutzer.

##### 3.4.1.3 `user_sessions` ← `Session` (`M/session.py` Z. 17–27)

Entität `UserSession` · `[OwnedBy("Identity")]` · Basis eigene Form (Spalten vollständig gelistet) · ab **I0** · Status **ersetzt** · CE-IDs: CE-AUTH-022, CE-AUTH-023, CE-AUTH-024, CE-AUTH-025

Spalten verbindlich aus D05 §3.4.1: `id varchar(64)` PK, `user_id uuid` FK `users` ON DELETE CASCADE, `app varchar(16)`, `keycloak_sid varchar(128)`, `keycloak_sub varchar(255)`, `ticket bytea` (DP-Zweck `Plane.Identity.SessionTicket.v1`), `device_info jsonb` (`SessionDeviceInfo`), `auth_time timestamptz NULL`, `created_at`, `last_seen_at`, `revalidated_at`, `expires_at` (alle `timestamptz NOT NULL` außer `auth_time`). Indizes `(user_id)`, `(keycloak_sid)`, `(keycloak_sub)`, `(expires_at)`. Kein Soft-Delete, keine Audit-Spalten. Check `ck_user_sessions_app` (`app IN ('web','admin','space')`).

##### 3.4.1.4 `api_tokens` ← `APIToken` (`M/api.py` Z. 23–46)

Entität `ApiToken` · `[OwnedBy("Identity")]` · Basis `AuditableEntity` (`id`, `created_at`, `updated_at`, `created_by_id`, `updated_by_id`, `deleted_at`) · ab **I1** · Status **angepasst** · CE-IDs: CE-WH-012, CE-WH-013, CE-WH-014, CE-API-001

| Spalte | PostgreSQL | Null | Default | C#-Property: Typ | Herkunft / Regel |
|---|---|---|---|---|---|
| `label` | `varchar(255)` | nein | C#: `Guid.CreateVersion7().ToString("N")` | Label: `string` | 1:1 |
| `description` | `text` | nein | – | Description: `string` | 1:1 |
| `is_active` | `boolean` | nein | true | IsActive: `bool` | 1:1 |
| `last_used` | `timestamptz` | ja | – | LastUsed: `DateTimeOffset?` | höchstens 1 Update/60 s (D05-ADR-16) |
| ~~`token`~~ | – | – | – | – | entfällt: ersetzt durch `token_hash` + `token_prefix` (D05-ADR-16) |
| `user_id` | `uuid` | nein | – | UserId: `Guid` | FK `users` ON DELETE CASCADE |
| `user_type` | `smallint` | nein | 0 | UserType: `short` | 0 = Human, 1 = Bot |
| `workspace_id` | `uuid` | ja | – | WorkspaceId: `Guid?` | FK `workspaces` ON DELETE CASCADE; ungenutzt wie Original (Workspace-Tokens = Paket H3) |
| `expired_at` | `timestamptz` | ja | – | ExpiredAt: `DateTimeOffset?` | 1:1 |
| `token_hash` | `char(64)` | nein | – | `TokenHash: string` | SHA-256-Hex des Klartext-Tokens `plane_api_<32hex>`; UNIQUE |
| `token_prefix` | `varchar(14)` | nein | – | `TokenPrefix: string` | erste 14 Zeichen (Anzeige/Log) |

**Indizes/Unique:** `ux_api_tokens_token_hash` UNIQUE (`token_hash`); `ix_api_tokens_user_id` (`user_id`).

**Checks:** `ck_api_tokens_user_type` CHECK (`user_type IN (0,1)`).

##### 3.4.1.5 `api_activity_logs` ← `APIActivityLog` (`M/api.py` Z. 49–74)

Entität `ApiActivityLog` · `[OwnedBy("Identity")]` · Basis `AuditableEntity` (`id`, `created_at`, `updated_at`, `created_by_id`, `updated_by_id`, `deleted_at`) · ab **I6** · Status **angepasst** · CE-IDs: CE-API-003, CE-OPS-015

| Spalte | PostgreSQL | Null | Default | C#-Property: Typ | Herkunft / Regel |
|---|---|---|---|---|---|
| `token_identifier` | `varchar(255)` | nein | – | TokenIdentifier: `string` | = `token_hash` (D05 §4.8) |
| `path` | `varchar(255)` | nein | – | Path: `string` | 1:1 |
| `method` | `varchar(10)` | nein | – | Method: `string` | 1:1 |
| `query_params` | `text` | ja | – | QueryParams: `string?` | 1:1 |
| `headers` | `text` | ja | – | Headers: `string?` | 1:1 |
| `body` | `text` | ja | – | Body: `string?` | 1:1 |
| `response_code` | `integer` | nein | – | ResponseCode: `int` | 1:1 |
| `response_body` | `text` | ja | – | ResponseBody: `string?` | 1:1 |
| `ip_address` | `inet` | ja | – | IpAddress: `IPAddress?` | Original `GenericIPAddressField` → `inet` |
| `user_agent` | `varchar(512)` | ja | – | UserAgent: `string?` | 1:1 |

**Indizes/Unique:** `ix_api_activity_logs_created_at` (`created_at`) – Cleanup-Job 14 Tage.

**Hinweise:** Append-only; Hard-Delete durch Aufbewahrungs-Job (`ApiActivityLogCleanupJob`, D06). Soft-Delete-Spalte bleibt aus der Basis vorhanden, wird nie gesetzt.

#### 3.4.2 Modul Instance (Instanz, Admins, Konfiguration)

##### 3.4.2.1 `instances` ← `Instance` (`API/license/models/instance.py` Z. 22–50)

Entität `Instance` · `[OwnedBy("Instance")]` · Basis `AuditableEntity` (`id`, `created_at`, `updated_at`, `created_by_id`, `updated_by_id`, `deleted_at`) · ab **I0** · Status **angepasst** · CE-IDs: CE-INST-001, CE-INST-003, CE-INST-005, CE-INST-006

| Spalte | PostgreSQL | Null | Default | C#-Property: Typ | Herkunft / Regel |
|---|---|---|---|---|---|
| `instance_name` | `varchar(255)` | nein | – | InstanceName: `string` | 1:1 |
| `whitelist_emails` | `text` | ja | – | WhitelistEmails: `string?` | 1:1 |
| `instance_id` | `varchar(255)` | nein | – | InstanceId: `string` | 1:1 |
| `current_version` | `varchar(255)` | nein | – | CurrentVersion: `string` | 1:1 |
| `latest_version` | `varchar(255)` | ja | – | LatestVersion: `string?` | = `current_version` (kein Netzaufruf, ADR-004; D14 §3.15 Schritt 6) |
| ~~`edition`~~ | – | – | – | – | entfällt: ADR-001; `GET /api/instances/` liefert `edition` nur, falls der Vertrag es verlangt, als Konstante (D04) |
| `domain` | `text` | nein | – | Domain: `string` | 1:1 |
| `last_checked_at` | `timestamptz` | nein | – | LastCheckedAt: `DateTimeOffset` | vom Migrator gesetzt |
| `namespace` | `varchar(255)` | ja | – | Namespace: `string?` | 1:1 |
| `is_telemetry_enabled` | `boolean` | nein | false | IsTelemetryEnabled: `bool` | Default `false` (ADR-004) statt `true` |
| `is_support_required` | `boolean` | nein | true | IsSupportRequired: `bool` | Vertragsfeld, ohne Wirkung |
| `is_setup_done` | `boolean` | nein | false | IsSetupDone: `bool` | 1:1 |
| `is_signup_screen_visited` | `boolean` | nein | false | IsSignupScreenVisited: `bool` | 1:1 |
| `is_verified` | `boolean` | nein | false | IsVerified: `bool` | 1:1 |
| `is_test` | `boolean` | nein | false | IsTest: `bool` | 1:1 |
| `is_current_version_deprecated` | `boolean` | nein | false | IsCurrentVersionDeprecated: `bool` | 1:1 |

**Indizes/Unique:** `ux_instances_instance_id` UNIQUE (`instance_id`); `ux_instances_singleton` UNIQUE ((`true`)) – genau eine Zeile (Ausdrucksindex).

**Hinweise:** Genau ein Datensatz; angelegt/aktualisiert durch `InstanceBootstrapper` (D14 §3.15 Schritt 6). Referenztabelle für `TablesToIgnore`.

##### 3.4.2.2 `instance_admins` ← `InstanceAdmin` (`API/license/models/instance.py` Z. 53–69)

Entität `InstanceAdminMirror` · `[OwnedBy("Instance")]` · Basis `AuditableEntity` (`id`, `created_at`, `updated_at`, `created_by_id`, `updated_by_id`, `deleted_at`) · ab **I0** · Status **angepasst** · CE-IDs: CE-INST-004 (angepasst: Spiegel der Keycloak-Rolle)

| Spalte | PostgreSQL | Null | Default | C#-Property: Typ | Herkunft / Regel |
|---|---|---|---|---|---|
| `user_id` | `uuid` | nein | – | UserId: `Guid` | FK `users` ON DELETE CASCADE (Original SET NULL); Original `SET_NULL`/nullable; Spiegel ohne Benutzer ist sinnlos |
| `instance_id` | `uuid` | nein | – | InstanceId: `Guid` | FK `instances` ON DELETE CASCADE |
| `role` | `integer` | nein | 20 | Role: `int` | immer 20 |
| `is_verified` | `boolean` | nein | false | IsVerified: `bool` | Vertragsfeld, immer `true` bei Spiegelung |
| `source` | `varchar(20)` | nein | `'keycloak'` | `Source: string` | D05 §3.7 (Spiegelquelle) |
| `synced_at` | `timestamptz` | nein | – | `SyncedAt: DateTimeOffset` | letzter Abgleich beim Login (`MirrorInstanceAdminStep`, Order 700) |

**Indizes/Unique:** `ux_instance_admins_user_id` UNIQUE (`user_id`) (D05 §3.7.4).

**Checks:** `ck_instance_admins_role` CHECK (`role = 20`).

##### 3.4.2.3 `instance_configurations` ← `InstanceConfiguration` (`API/license/models/instance.py` Z. 72–83)

Entität `InstanceConfiguration` · `[OwnedBy("Instance")]` · Basis `AuditableEntity` (`id`, `created_at`, `updated_at`, `created_by_id`, `updated_by_id`, `deleted_at`) · ab **I0** · Status **angepasst** · CE-IDs: CE-INST-002, CE-INST-017, CE-INST-018, CE-INST-025, CE-INST-026, CE-INST-028

| Spalte | PostgreSQL | Null | Default | C#-Property: Typ | Herkunft / Regel |
|---|---|---|---|---|---|
| `key` | `varchar(100)` | nein | – | Key: `string` | 1:1 |
| `value` | `text` | ja | NULL | Value: `string?` | bei `is_encrypted=true` Base64 eines DP-geschützten Werts (Zweck `Plane.Instance.Configuration.v1`, D02 §3.16) |
| `category` | `varchar(100)` | nein | – | Category: `string` | Original `text`; Werte aus Katalog `InstanceConfigurationKeys` |
| `is_encrypted` | `boolean` | nein | false | IsEncrypted: `bool` | 1:1 |

**Indizes/Unique:** `ux_instance_configurations_key` UNIQUE (`key`).

**Hinweise:** Seed nur fehlender Schlüssel durch `InstanceConfigurationSeeder` (D14 §3.15 Schritt 7). OAuth-/Passwort-Schlüssel entfallen (ADR-008).

#### 3.4.3 Modul Workspaces

##### 3.4.3.1 `workspaces` ← `Workspace` (`M/workspace.py` Z. 119–182)

Entität `Workspace` · `[OwnedBy("Workspaces")]` · Basis `AuditableEntity` (`id`, `created_at`, `updated_at`, `created_by_id`, `updated_by_id`, `deleted_at`) · ab **I0** · Status **angepasst** · CE-IDs: CE-WS-001, CE-WS-003, CE-WS-004, CE-WS-005, CE-INST-027, CE-INST-029

| Spalte | PostgreSQL | Null | Default | C#-Property: Typ | Herkunft / Regel |
|---|---|---|---|---|---|
| `name` | `varchar(80)` | nein | – | Name: `string` | 1:1 |
| `logo` | `text` | ja | – | Logo: `string?` | 1:1 |
| `logo_asset_id` | `uuid` | ja | – | LogoAssetId: `Guid?` | FK `file_assets` ON DELETE SET NULL |
| `owner_id` | `uuid` | nein | – | OwnerId: `Guid` | FK `users` ON DELETE RESTRICT (Original CASCADE); Original `CASCADE`; Benutzer werden nie hart gelöscht (D03-ADR-07) |
| `slug` | `varchar(48)` | nein | – | Slug: `string` | Regex `^[a-zA-Z0-9_-]+$`, ≤ 48, case-sensitiv (D02 §3.5.3); partieller Unique statt Suffix `__<epoch>` (Korrektur 02a §3.3) |
| `organization_size` | `varchar(20)` | ja | – | OrganizationSize: `string?` | Werte aus `ORGANIZATION_SIZE` (`packages/constants/src/workspace.ts`), nur Validator |
| `timezone` | `varchar(255)` | nein | `'UTC'` | Timezone: `string` | 1:1 |
| `background_color` | `varchar(255)` | nein | C#: `ColorGenerator.Random()` | BackgroundColor: `string` | Default per `ColorGenerator.Random()` |

**Indizes/Unique:** `workspace_slug_unique_when_deleted_at_null` UNIQUE (`slug`) WHERE `deleted_at IS NULL` (neu; DEV-DM-01); GIN-Trigram `ix_workspaces_name_trgm` (CE-SRCH-001).

**Hinweise:** Soft-Delete eines Workspace kaskadiert **Deferred** (D02-ADR-03). Das Slug-Suffix des Originals entfällt, weil der partielle Unique-Index den Slug sofort freigibt.

##### 3.4.3.2 `workspace_members` ← `WorkspaceMember` (`M/workspace.py` Z. 198–231)

Entität `WorkspaceMember` · `[OwnedBy("Workspaces")]` · Basis `AuditableEntity` (`id`, `created_at`, `updated_at`, `created_by_id`, `updated_by_id`, `deleted_at`) · ab **I0** · Status **angepasst** · CE-IDs: CE-WS-008, CE-WS-009, CE-WS-012, CE-LV-015, CE-PROF-008

| Spalte | PostgreSQL | Null | Default | C#-Property: Typ | Herkunft / Regel |
|---|---|---|---|---|---|
| `workspace_id` | `uuid` | nein | – | WorkspaceId: `Guid` | FK `workspaces` ON DELETE CASCADE |
| `member_id` | `uuid` | nein | – | MemberId: `Guid` | FK `users` ON DELETE CASCADE |
| `role` | `smallint` | nein | 5 | Role: `short` | denormalisierte Kopie von `roles.level` (D05 §3.13.3); nur `IWorkspaceMembershipService` schreibt |
| `company_role` | `text` | ja | – | CompanyRole: `string?` | 1:1 |
| `view_props` | `jsonb` | nein | `JsonDefaults.WorkspaceViewProps` (DB-Default = gleiches Literal) | ViewProps: `JsonObject` | Lesemodell `WorkspaceViewProps` |
| `default_props` | `jsonb` | nein | `JsonDefaults.WorkspaceViewProps` (DB-Default = gleiches Literal) | DefaultProps: `JsonObject` | Lesemodell `WorkspaceViewProps` |
| `issue_props` | `jsonb` | nein | `JsonDefaults.WorkspaceIssueProps` (DB-Default = gleiches Literal) | IssueProps: `JsonObject` | Lesemodell `WorkspaceIssueProps` |
| `is_active` | `boolean` | nein | true | IsActive: `bool` | 1:1 |
| `getting_started_checklist` | `jsonb` | nein | `'{}'::jsonb` | GettingStartedChecklist: `JsonObject` | frei, CE ungenutzt |
| `tips` | `jsonb` | nein | `'{}'::jsonb` | Tips: `JsonObject` | frei |
| `explored_features` | `jsonb` | nein | `'{}'::jsonb` | ExploredFeatures: `JsonObject` | frei |
| `role_id` | `uuid` | nein | – | `RoleId: Guid` | FK `roles` ON DELETE RESTRICT (E5, D05 §3.13.3) |

**Indizes/Unique:** `workspace_member_unique_workspace_member_when_deleted_at_null` UNIQUE (`workspace_id`, `member_id`) WHERE `deleted_at IS NULL`; `ix_workspace_members_member_id` (`member_id`) – „meine Workspaces“.

**Checks:** `ck_workspace_members_role` CHECK (`role IN (5,15,20)`).

##### 3.4.3.3 `workspace_member_invites` ← `WorkspaceMemberInvite` (`M/workspace.py` Z. 234–258)

Entität `WorkspaceMemberInvite` · `[OwnedBy("Workspaces")]` · Basis `AuditableEntity` (`id`, `created_at`, `updated_at`, `created_by_id`, `updated_by_id`, `deleted_at`) · ab **I1** · Status **übernommen** · CE-IDs: CE-WS-010, CE-WS-011, CE-AUTH-028, CE-API-013

| Spalte | PostgreSQL | Null | Default | C#-Property: Typ | Herkunft / Regel |
|---|---|---|---|---|---|
| `workspace_id` | `uuid` | nein | – | WorkspaceId: `Guid` | FK `workspaces` ON DELETE CASCADE |
| `email` | `varchar(255)` | nein | – | Email: `string` | lowercase |
| `accepted` | `boolean` | nein | false | Accepted: `bool` | 1:1 |
| `token` | `text` | nein | – | Token: `string` | Original `varchar(255)` mit JWT → Überlauf möglich (02a §3.22 #17); Ziel `text` |
| `message` | `text` | ja | – | Message: `string?` | 1:1 |
| `responded_at` | `timestamptz` | ja | – | RespondedAt: `DateTimeOffset?` | 1:1 |
| `role` | `smallint` | nein | 5 | Role: `short` | 20/15/5 (Anzeige- und Übernahmewert) |
| `role_id` | `uuid` | nein | – | `RoleId: Guid` | FK `roles` ON DELETE RESTRICT; gesetzt aus `role` |

**Indizes/Unique:** `workspace_member_invite_unique_email_workspace_when_deleted_at_null` UNIQUE (`email`, `workspace_id`) WHERE `deleted_at IS NULL`; `ix_workspace_member_invites_email` (`email`) – JIT-Zuordnung (CE-AUTH-028).

**Checks:** `ck_workspace_member_invites_role` CHECK (`role IN (5,15,20)`).

##### 3.4.3.4 `workspace_themes` ← `WorkspaceTheme` (`M/workspace.py` Z. 286–307)

Entität `WorkspaceTheme` · `[OwnedBy("Workspaces")]` · Basis `AuditableEntity` (`id`, `created_at`, `updated_at`, `created_by_id`, `updated_by_id`, `deleted_at`) · ab **I1** · Status **übernommen** · CE-IDs: CE-WS-007

| Spalte | PostgreSQL | Null | Default | C#-Property: Typ | Herkunft / Regel |
|---|---|---|---|---|---|
| `workspace_id` | `uuid` | nein | – | WorkspaceId: `Guid` | FK `workspaces` ON DELETE CASCADE |
| `name` | `varchar(300)` | nein | – | Name: `string` | 1:1 |
| `actor_id` | `uuid` | nein | – | ActorId: `Guid` | FK `users` ON DELETE CASCADE |
| `colors` | `jsonb` | nein | `'{}'::jsonb` | Colors: `JsonObject` | frei |

**Indizes/Unique:** `workspace_theme_unique_workspace_name_when_deleted_at_null` UNIQUE (`workspace_id`, `name`) WHERE `deleted_at IS NULL`.

##### 3.4.3.5 `workspace_user_properties` ← `WorkspaceUserProperties` (`M/workspace.py` Z. 310–351)

Entität `WorkspaceUserProperties` · `[OwnedBy("Workspaces")]` · Basis `AuditableEntity` (`id`, `created_at`, `updated_at`, `created_by_id`, `updated_by_id`, `deleted_at`) · ab **I1** · Status **übernommen** · CE-IDs: CE-LV-015, CE-WS-022

| Spalte | PostgreSQL | Null | Default | C#-Property: Typ | Herkunft / Regel |
|---|---|---|---|---|---|
| `workspace_id` | `uuid` | nein | – | WorkspaceId: `Guid` | FK `workspaces` ON DELETE CASCADE |
| `user_id` | `uuid` | nein | – | UserId: `Guid` | FK `users` ON DELETE CASCADE |
| `filters` | `jsonb` | nein | `JsonDefaults.LegacyFilters` (DB-Default = gleiches Literal) | Filters: `JsonObject` | Lesemodell `LegacyIssueFilters` |
| `display_filters` | `jsonb` | nein | `JsonDefaults.WorkspaceNestedDisplayFilters` (DB-Default = gleiches Literal) | DisplayFilters: `JsonObject` | Original-Default **verschachtelt** `{"display_filters": {…}}`, 02a §3.22 #1 – Vertrag, nicht korrigieren |
| `display_properties` | `jsonb` | nein | `JsonDefaults.WorkspaceNestedDisplayProperties` (DB-Default = gleiches Literal) | DisplayProperties: `JsonObject` | verschachtelt wie oben |
| `rich_filters` | `jsonb` | nein | `'{}'::jsonb` | RichFilters: `JsonObject` | Lesemodell `RichFilterNode` |
| `navigation_project_limit` | `integer` | nein | 10 | NavigationProjectLimit: `int` | 1:1 |
| `navigation_control_preference` | `varchar(25)` | nein | `'ACCORDION'` | NavigationControlPreference: `string` | `ACCORDION` \\| `TABBED` |

**Indizes/Unique:** `workspace_user_properties_unique_workspace_user_when_deleted_at_null` UNIQUE (`workspace_id`, `user_id`) WHERE `deleted_at IS NULL`.

**Checks:** `ck_workspace_user_properties_nav_pref` CHECK (`navigation_control_preference IN ('ACCORDION','TABBED')`).

##### 3.4.3.6 `workspace_user_preferences` ← `WorkspaceUserPreference` (`M/workspace.py` Z. 417–455)

Entität `WorkspaceUserPreference` · `[OwnedBy("Workspaces")]` · Basis `AuditableEntity` (`id`, `created_at`, `updated_at`, `created_by_id`, `updated_by_id`, `deleted_at`) · ab **I1** · Status **übernommen** · CE-IDs: CE-WS-021, CE-WS-022

| Spalte | PostgreSQL | Null | Default | C#-Property: Typ | Herkunft / Regel |
|---|---|---|---|---|---|
| `workspace_id` | `uuid` | nein | – | WorkspaceId: `Guid` | FK `workspaces` ON DELETE CASCADE |
| `user_id` | `uuid` | nein | – | UserId: `Guid` | FK `users` ON DELETE CASCADE |
| `key` | `varchar(255)` | nein | – | Key: `string` | `views`, `active_cycles`, `analytics`, `drafts`, `your_work`, `archives`, `stickies` (nur Validator, kein DB-Check: Pakete ergänzen Schlüssel) |
| `is_pinned` | `boolean` | nein | false | IsPinned: `bool` | 1:1 |
| `sort_order` | `double precision` | nein | 65535 | SortOrder: `double` | 1:1 |

**Indizes/Unique:** `workspace_user_preferences_unique_workspace_user_key_when_deleted_at_null` UNIQUE (`workspace_id`, `user_id`, `key`) WHERE `deleted_at IS NULL`.

##### 3.4.3.7 `user_favorites` ← `UserFavorite` (`M/favorite.py` Z. 14–69)

Entität `UserFavorite` · `[OwnedBy("Workspaces")]` · Basis `WorkspaceEntity` (Audit-Basis + `workspace_id` NOT NULL, `project_id` NULL) · ab **I1** · Status **übernommen** · CE-IDs: CE-WS-023, CE-CYC-015, CE-MOD-011, CE-LV-050, CE-PAGE-010

| Spalte | PostgreSQL | Null | Default | C#-Property: Typ | Herkunft / Regel |
|---|---|---|---|---|---|
| `user_id` | `uuid` | nein | – | UserId: `Guid` | FK `users` ON DELETE CASCADE |
| `entity_type` | `varchar(100)` | nein | – | EntityType: `string` | `cycle`, `issue`, `module`, `view`, `page`, `project`, `folder` (Validator; Pakete ergänzen) |
| `entity_identifier` | `uuid` | ja | – | EntityIdentifier: `Guid?` | polymorph, **kein FK** (wie Original); Aufräumen über Handler des Eigentümers |
| `name` | `varchar(255)` | ja | – | Name: `string?` | 1:1 |
| `is_folder` | `boolean` | nein | false | IsFolder: `bool` | 1:1 |
| `sequence` | `double precision` | nein | 65535 | Sequence: `double` | Sortierung (`min − 10000`, 02a §3.6) |
| `parent_id` | `uuid` | ja | – | ParentId: `Guid?` | FK `user_favorites` ON DELETE CASCADE |
| `teamspace_id` | `uuid` | ja | NULL | `TeamspaceId: Guid?` | B1-Vorhalt (01 §1.4), ohne FK, CE immer `NULL` |

**Indizes/Unique:** `user_favorite_unique_entity_type_entity_identifier_user_when_deleted_at_null` UNIQUE (`entity_type`, `entity_identifier`, `user_id`) WHERE `deleted_at IS NULL`; `fav_entity_type_idx` (`entity_type`); `fav_entity_identifier_idx` (`entity_identifier`); `fav_entity_idx` (`entity_type`, `entity_identifier`); `ix_user_favorites_teamspace_id` (`teamspace_id`) WHERE `teamspace_id IS NOT NULL`.

**Hinweise:** Favoriten-Löschung ist im Original **hart** (`favorite.delete(soft=False)`); der Handler nutzt dafür `IHardDelete` (D02-ADR-03).

#### 3.4.4 Modul Projects (Projekte, Mitglieder, States, Labels, Estimates)

##### 3.4.4.1 `projects` ← `Project` (`M/project.py` Z. 68–227)

Entität `Project` · `[OwnedBy("Projects")]` · Basis `AuditableEntity` (`id`, `created_at`, `updated_at`, `created_by_id`, `updated_by_id`, `deleted_at`) · ab **I0** · Status **angepasst** · CE-IDs: CE-PRJ-001…CE-PRJ-010, CE-PRJ-016, CE-PRJ-018, CE-PRJ-019, CE-PRJ-022, CE-PRJ-026, CE-PRJ-039, CE-PRJ-040, CE-API-006…CE-API-008

| Spalte | PostgreSQL | Null | Default | C#-Property: Typ | Herkunft / Regel |
|---|---|---|---|---|---|
| `name` | `varchar(255)` | nein | – | Name: `string` | 1:1 |
| `description` | `text` | nein | – | Description: `string` | 1:1 |
| `description_text` | `jsonb` | ja | – | DescriptionText: `JsonObject?` | Legacy, bleibt für Vertrag |
| `description_html` | `text` | ja | – | DescriptionHtml: `string?` | Original `JSONField` mit HTML-String (02a §3.22 #4) → Ziel `text`; API-Vertrag (String) unverändert |
| `network` | `smallint` | nein | 2 | Network: `short` | 0 = Secret, 2 = Public (kein Wert 1) |
| `workspace_id` | `uuid` | nein | – | WorkspaceId: `Guid` | FK `workspaces` ON DELETE CASCADE |
| `identifier` | `varchar(12)` | nein | – | Identifier: `string` | `strip().upper()` im Domain-Code (`ProjectIdentifierRules`), ≤ 12, Muster `FORBIDDEN_IDENTIFIER_CHARS_PATTERN` im Validator |
| `default_assignee_id` | `uuid` | ja | – | DefaultAssigneeId: `Guid?` | FK `users` ON DELETE SET NULL (Original CASCADE); Original `CASCADE` (02a §3.22 #5) → `SET NULL` |
| `project_lead_id` | `uuid` | ja | – | ProjectLeadId: `Guid?` | FK `users` ON DELETE SET NULL (Original CASCADE); Original `CASCADE` → `SET NULL` |
| `emoji` | `varchar(255)` | ja | – | Emoji: `string?` | 1:1 |
| `icon_prop` | `jsonb` | ja | – | IconProp: `JsonObject?` | Legacy |
| `module_view` | `boolean` | nein | false | ModuleView: `bool` | CE-Feature-Toggle (D16 §3.2.6) |
| `cycle_view` | `boolean` | nein | false | CycleView: `bool` | CE-Feature-Toggle |
| `issue_views_view` | `boolean` | nein | false | IssueViewsView: `bool` | CE-Feature-Toggle |
| `page_view` | `boolean` | nein | true | PageView: `bool` | CE-Feature-Toggle |
| `intake_view` | `boolean` | nein | false | IntakeView: `bool` | CE-Feature-Toggle |
| `is_time_tracking_enabled` | `boolean` | nein | false | IsTimeTrackingEnabled: `bool` | V-Spalte (A10), CE immer `false` (D16 §3.2.6) |
| `is_issue_type_enabled` | `boolean` | nein | false | IsIssueTypeEnabled: `bool` | V-Spalte (A1), CE immer `false` |
| `guest_view_all_features` | `boolean` | nein | false | GuestViewAllFeatures: `bool` | 1:1 |
| `cover_image` | `text` | ja | – | CoverImage: `string?` | 1:1 |
| `cover_image_asset_id` | `uuid` | ja | – | CoverImageAssetId: `Guid?` | FK `file_assets` ON DELETE SET NULL |
| `estimate_id` | `uuid` | ja | – | EstimateId: `Guid?` | FK `estimates` ON DELETE SET NULL; aktives Schätzsystem (zirkuläre FK, Migration legt sie nach `estimates` an) |
| `archive_in` | `integer` | nein | 0 | ArchiveIn: `int` | Monate 0–12 (0 = aus) |
| `close_in` | `integer` | nein | 0 | CloseIn: `int` | Monate 0–12 |
| `logo_props` | `jsonb` | nein | `'{}'::jsonb` | LogoProps: `JsonObject` | Lesemodell `LogoProps` |
| `default_state_id` | `uuid` | ja | – | DefaultStateId: `Guid?` | FK `states` ON DELETE SET NULL; Auto-Close-Zielstatus (CE-PRJ-040); zirkuläre FK |
| `archived_at` | `timestamptz` | ja | – | ArchivedAt: `DateTimeOffset?` | 1:1 |
| `timezone` | `varchar(255)` | nein | `'UTC'` | Timezone: `string` | bei Anlage ohne Angabe = `workspaces.timezone` (Domain-Fabrik) |
| `external_source` | `varchar(255)` | ja | – | ExternalSource: `string?` | 1:1 |
| `external_id` | `varchar(255)` | ja | – | ExternalId: `string?` | 1:1 |

**Indizes/Unique:** `project_unique_identifier_workspace_when_deleted_at_null` UNIQUE (`identifier`, `workspace_id`) WHERE `deleted_at IS NULL`; `project_unique_name_workspace_when_deleted_at_null` UNIQUE (`name`, `workspace_id`) WHERE `deleted_at IS NULL`; `ak_projects_id_workspace_id` UNIQUE (`id`, `workspace_id`) – Ziel der Scope-FKs (D03-ADR-05); GIN-Trigram `ix_projects_name_trgm`, `ix_projects_identifier_trgm` (CE-SRCH-001).

**Checks:** `ck_projects_network` CHECK (`network IN (0,2)`); `ck_projects_archive_in` CHECK (`archive_in BETWEEN 0 AND 12`); `ck_projects_close_in` CHECK (`close_in BETWEEN 0 AND 12`); `ck_projects_identifier_upper` CHECK (`identifier = upper(identifier)`).

**Hinweise:** Zeitzonenwechsel retimed Snoozes von `intake_work_items` in derselben Transaktion (`Project.ChangeTimezone`, `SELECT … FOR UPDATE`, 02a §3.4) über `IIntakeSnoozeRetimer` (Contracts von `Plane.Intake`, R5). Soft-Delete kaskadiert **Deferred**.

##### 3.4.4.2 `project_identifiers` ← `ProjectIdentifier` (`M/project.py` Z. 314–331)

Entität `ProjectIdentifier` · `[OwnedBy("Projects")]` · Basis eigene Form (Spalten vollständig gelistet) · ab **I0** · Status **übernommen** · CE-IDs: CE-PRJ-005

| Spalte | PostgreSQL | Null | Default | C#-Property: Typ | Herkunft / Regel |
|---|---|---|---|---|---|
| `id` | `bigint GENERATED BY DEFAULT AS IDENTITY` | nein | Identity | `Id: long` | Ausnahme von UUIDv7: API liefert `id` als Ganzzahl (`ProjectIdentifierEndpoint.get`) |
| `workspace_id` | `uuid` | ja | – | `WorkspaceId: Guid?` | FK `workspaces` ON DELETE CASCADE (Original nullable) |
| `project_id` | `uuid` | nein | – | `ProjectId: Guid` | FK `projects` ON DELETE CASCADE, 1:1 (unique) |
| `name` | `varchar(12)` | nein | – | `Name: string` | reservierter Identifier (uppercase) |
| `created_at, updated_at, created_by_id, updated_by_id, deleted_at` | wie `AuditableEntity` | – | – | – | Original `AuditModel` (ohne `BaseModel.id`) |

**Indizes/Unique:** `unique_name_workspace_when_deleted_at_null` UNIQUE (`name`, `workspace_id`) WHERE `deleted_at IS NULL`; `ux_project_identifiers_project_id` UNIQUE (`project_id`).

**Hinweise:** Entität erbt **nicht** von `Entity` (eigener `long`-Schlüssel), implementiert `IAuditable`, `ISoftDeletable`, `IWorkspaceScoped`. `DELETE …/project-identifiers/` löscht soft wie Original.

##### 3.4.4.3 `project_members` ← `ProjectMember` (`M/project.py` Z. 260–310)

Entität `ProjectMember` · `[OwnedBy("Projects")]` · Basis `ProjectEntity` (Audit-Basis + `workspace_id`, `project_id` NOT NULL; Scope-FK) · ab **I0** · Status **angepasst** · CE-IDs: CE-PRJ-006, CE-PRJ-007, CE-PRJ-021, CE-API-012, CE-WS-008

| Spalte | PostgreSQL | Null | Default | C#-Property: Typ | Herkunft / Regel |
|---|---|---|---|---|---|
| `member_id` | `uuid` | nein | – | MemberId: `Guid` | FK `users` ON DELETE CASCADE; Original nullable, fachlich nie NULL (02a §3.22 #6) |
| `comment` | `text` | ja | – | Comment: `string?` | 1:1 |
| `role` | `smallint` | nein | 5 | Role: `short` | denormalisiert = `roles.level` |
| `view_props` | `jsonb` | nein | `JsonDefaults.ProjectViewProps` (DB-Default = gleiches Literal) | ViewProps: `JsonObject` | Lesemodell `ProjectViewProps` |
| `default_props` | `jsonb` | nein | `JsonDefaults.ProjectViewProps` (DB-Default = gleiches Literal) | DefaultProps: `JsonObject` | Lesemodell `ProjectViewProps` |
| `preferences` | `jsonb` | nein | `JsonDefaults.ProjectPreferences` (DB-Default = gleiches Literal) | Preferences: `JsonObject` | Lesemodell `ProjectMemberPreferences` |
| `sort_order` | `double precision` | nein | 65535 | SortOrder: `double` | Doppelhaltung zu `project_user_properties.sort_order` bleibt (Vertrag) |
| `is_active` | `boolean` | nein | true | IsActive: `bool` | 1:1 |
| `role_id` | `uuid` | nein | – | `RoleId: Guid` | FK `roles` ON DELETE RESTRICT (E5) |

**Indizes/Unique:** `project_member_unique_project_member_when_deleted_at_null` UNIQUE (`project_id`, `member_id`) WHERE `deleted_at IS NULL`; `ix_project_members_member_id_is_active` (`member_id`, `is_active`) WHERE `deleted_at IS NULL`.

**Checks:** `ck_project_members_role` CHECK (`role IN (5,15,20)`).

**Hinweise:** Anlage legt im selben Command eine `project_user_properties`-Zeile an (`ON CONFLICT DO NOTHING`, Sortierung `min − 10000`, 02a §3.5).

##### 3.4.4.4 `project_member_invites` ← `ProjectMemberInvite` (`M/project.py` Z. 242–257)

Entität `ProjectMemberInvite` · `[OwnedBy("Projects")]` · Basis `ProjectEntity` (Audit-Basis + `workspace_id`, `project_id` NOT NULL; Scope-FK) · ab **I1** · Status **übernommen** · CE-IDs: CE-PRJ-010 (defekt, nur API – Vertrag erhalten)

| Spalte | PostgreSQL | Null | Default | C#-Property: Typ | Herkunft / Regel |
|---|---|---|---|---|---|
| `email` | `varchar(255)` | nein | – | Email: `string` | 1:1 |
| `accepted` | `boolean` | nein | false | Accepted: `bool` | 1:1 |
| `token` | `text` | nein | – | Token: `string` | wie Workspace-Einladung |
| `message` | `text` | ja | – | Message: `string?` | 1:1 |
| `responded_at` | `timestamptz` | ja | – | RespondedAt: `DateTimeOffset?` | 1:1 |
| `role` | `smallint` | nein | 5 | Role: `short` | Choices: ROLE_CHOICES |
| `role_id` | `uuid` | nein | – | `RoleId: Guid` | FK `roles` ON DELETE RESTRICT |

**Checks:** `ck_project_member_invites_role` CHECK (`role IN (5,15,20)`).

##### 3.4.4.5 `project_user_properties` ← `ProjectUserProperty` (`M/project.py` Z. 392–423)

Entität `ProjectUserProperty` · `[OwnedBy("Projects")]` · Basis `ProjectEntity` (Audit-Basis + `workspace_id`, `project_id` NOT NULL; Scope-FK) · ab **I0** · Status **übernommen** · CE-IDs: CE-PRJ-016, CE-LV-014, CE-PRJ-011, CE-PRJ-015

| Spalte | PostgreSQL | Null | Default | C#-Property: Typ | Herkunft / Regel |
|---|---|---|---|---|---|
| `user_id` | `uuid` | nein | – | UserId: `Guid` | FK `users` ON DELETE CASCADE |
| `filters` | `jsonb` | nein | `JsonDefaults.LegacyFilters` (DB-Default = gleiches Literal) | Filters: `JsonObject` | Lesemodell `LegacyIssueFilters` |
| `display_filters` | `jsonb` | nein | `JsonDefaults.DisplayFilters` (DB-Default = gleiches Literal) | DisplayFilters: `JsonObject` | Lesemodell `DisplayFilters` |
| `display_properties` | `jsonb` | nein | `JsonDefaults.DisplayProperties` (DB-Default = gleiches Literal) | DisplayProperties: `JsonObject` | Lesemodell `DisplayProperties` |
| `rich_filters` | `jsonb` | nein | `'{}'::jsonb` | RichFilters: `JsonObject` | Lesemodell `RichFilterNode` |
| `preferences` | `jsonb` | nein | `JsonDefaults.ProjectPreferences` (DB-Default = gleiches Literal) | Preferences: `JsonObject` | Lesemodell `ProjectMemberPreferences` |
| `sort_order` | `double precision` | nein | 65535 | SortOrder: `double` | Projektreihenfolge in der Sidebar (`min − 10000`) |

**Indizes/Unique:** `project_user_property_unique_user_project_when_deleted_at_null` UNIQUE (`user_id`, `project_id`) WHERE `deleted_at IS NULL`.

##### 3.4.4.6 `states` ← `State` (`M/state.py` Z. 79–126)

Entität `State` · `[OwnedBy("Projects")]` · Basis `ProjectEntity` (Audit-Basis + `workspace_id`, `project_id` NOT NULL; Scope-FK) · ab **I0** · Status **angepasst** · CE-IDs: CE-PRJ-023…CE-PRJ-027, CE-INT-001, CE-API-009

| Spalte | PostgreSQL | Null | Default | C#-Property: Typ | Herkunft / Regel |
|---|---|---|---|---|---|
| `name` | `varchar(255)` | nein | – | Name: `string` | 1:1 |
| `description` | `text` | nein | – | Description: `string` | 1:1 |
| `color` | `varchar(255)` | nein | – | Color: `string` | 1:1 |
| `slug` | `varchar(100)` | nein | – | Slug: `string` | `slugify(name)` im Domain-Code |
| `sequence` | `double precision` | nein | 65535 | Sequence: `double` | Anlage: `max(nicht-Triage) + 15000`; Triage immer 65000 (Korrektur Q12) |
| `group` | `varchar(20)` | nein | `'backlog'` | Group: `string` | `backlog`, `unstarted`, `started`, `completed`, `cancelled`, `triage` |
| `is_triage` | `boolean` | nein | false | IsTriage: `bool` | abgeleitet: wird gleich `group = triage` gesetzt (Korrektur Q12); Lesecode nutzt `group` |
| `default` | `boolean` | nein | false | Default: `bool` | genau ein Default je Projekt (partieller Unique, neu) |
| `external_source` | `varchar(255)` | ja | – | ExternalSource: `string?` | 1:1 |
| `external_id` | `varchar(255)` | ja | – | ExternalId: `string?` | 1:1 |

**Indizes/Unique:** `state_unique_name_project_when_deleted_at_null` UNIQUE (`name`, `project_id`) WHERE `deleted_at IS NULL`; `ux_states_project_default` UNIQUE (`project_id`) WHERE `"default" AND deleted_at IS NULL` (neu, DEV-DM-04); `ux_states_project_triage` UNIQUE (`project_id`) WHERE `"group" = 'triage' AND deleted_at IS NULL` (Invariante seit `MIG/0112`, neu als DB-Regel); `ix_states_project_sequence` (`project_id`, `sequence`); `ix_states_project_external` (`project_id`, `external_source`, `external_id`).

**Checks:** `ck_states_group` CHECK (`"group" IN ('backlog','unstarted','started','completed','cancelled','triage')`); `ck_states_triage_flag` CHECK (`is_triage = ("group" = 'triage')`).

**Hinweise:** Implementiert `IScopedCatalogEntry` (A17; `project_id` bleibt NOT NULL, W6 lockert per Expand-Migration). Spaltenname `group`/`default` sind SQL-Schlüsselwörter → EF quotet automatisch; Raw-SQL muss `"group"`/`"default"` quoten.

##### 3.4.4.7 `labels` ← `Label` (`M/label.py` Z. 11–57)

Entität `Label` · `[OwnedBy("Projects")]` · Basis `WorkspaceEntity` (Audit-Basis + `workspace_id` NOT NULL, `project_id` NULL) · ab **I1** · Status **angepasst** · CE-IDs: CE-PRJ-028…CE-PRJ-033, CE-WI-024, CE-API-010

| Spalte | PostgreSQL | Null | Default | C#-Property: Typ | Herkunft / Regel |
|---|---|---|---|---|---|
| `parent_id` | `uuid` | ja | – | ParentId: `Guid?` | FK `labels` ON DELETE CASCADE |
| `name` | `varchar(255)` | nein | – | Name: `string` | 1:1 |
| `description` | `text` | nein | – | Description: `string` | 1:1 |
| `color` | `varchar(255)` | nein | – | Color: `string` | 1:1 |
| `sort_order` | `double precision` | nein | 65535 | SortOrder: `double` | Anlage `max(project) + 10000` (D02 §5.2.6) |
| `external_source` | `varchar(255)` | ja | – | ExternalSource: `string?` | 1:1 |
| `external_id` | `varchar(255)` | ja | – | ExternalId: `string?` | 1:1 |

**Indizes/Unique:** `unique_name_when_project_null_and_not_deleted` UNIQUE (`workspace_id`, `name`) WHERE `project_id IS NULL AND deleted_at IS NULL` (Original nur `name` – DEV-LBL-04); `unique_project_name_when_not_deleted` UNIQUE (`project_id`, `name`) WHERE `project_id IS NOT NULL AND deleted_at IS NULL`; `ix_labels_project_sort_order` (`project_id`, `sort_order`); `ix_labels_project_external` (`project_id`, `external_source`, `external_id`).

**Hinweise:** Referenzimplementierung in D02 §5.2 (Entität, Konfiguration, Kaskaden). `IScopedCatalogEntry` (A17).

##### 3.4.4.8 `estimates` ← `Estimate` (`M/estimate.py` Z. 18–40)

Entität `Estimate` · `[OwnedBy("Projects")]` · Basis `ProjectEntity` (Audit-Basis + `workspace_id`, `project_id` NOT NULL; Scope-FK) · ab **I1** · Status **übernommen** · CE-IDs: CE-PRJ-034…CE-PRJ-038, CE-WI-027

| Spalte | PostgreSQL | Null | Default | C#-Property: Typ | Herkunft / Regel |
|---|---|---|---|---|---|
| `name` | `varchar(255)` | nein | – | Name: `string` | 1:1 |
| `description` | `text` | nein | – | Description: `string` | 1:1 |
| `type` | `varchar(255)` | nein | `'categories'` | Type: `string` | `categories` \\| `points`; `time` ist für Paket A11 zulässig (V, D16 §3.3.1) |
| `last_used` | `boolean` | nein | false | LastUsed: `bool` | 1:1 |

**Indizes/Unique:** `estimate_unique_name_project_when_deleted_at_null` UNIQUE (`name`, `project_id`) WHERE `deleted_at IS NULL`.

**Checks:** `ck_estimates_type` CHECK (`type IN ('categories','points','time')`).

##### 3.4.4.9 `estimate_points` ← `EstimatePoint` (`M/estimate.py` Z. 43–57)

Entität `EstimatePoint` · `[OwnedBy("Projects")]` · Basis `ProjectEntity` (Audit-Basis + `workspace_id`, `project_id` NOT NULL; Scope-FK) · ab **I1** · Status **übernommen** · CE-IDs: CE-PRJ-035…CE-PRJ-037, CE-WI-027

| Spalte | PostgreSQL | Null | Default | C#-Property: Typ | Herkunft / Regel |
|---|---|---|---|---|---|
| `estimate_id` | `uuid` | nein | – | EstimateId: `Guid` | FK `estimates` ON DELETE CASCADE |
| `key` | `integer` | nein | 0 | Key: `int` | 1:1 |
| `description` | `text` | nein | – | Description: `string` | 1:1 |
| `value` | `varchar(255)` | nein | – | Value: `string` | Anzeige-Wert (String); Sortierung alphabetisch wie Original (Q9) |

**Indizes/Unique:** `ix_estimate_points_estimate_id` (`estimate_id`).

**Checks:** `ck_estimate_points_key` CHECK (`key >= 0`).

#### 3.4.5 Modul WorkItems

##### 3.4.5.1 `work_items` ← `Issue` (`M/issue.py` Z. 104–255)

Entität `WorkItem` · `[OwnedBy("WorkItems")]` · Basis `ProjectEntity` (Audit-Basis + `workspace_id`, `project_id` NOT NULL; Scope-FK) · ab **I2** · Status **angepasst** · CE-IDs: CE-WI-001…CE-WI-049, CE-LV-005, CE-API-017…CE-API-019

| Spalte | PostgreSQL | Null | Default | C#-Property: Typ | Herkunft / Regel |
|---|---|---|---|---|---|
| `parent_id` | `uuid` | ja | – | ParentId: `Guid?` | FK `work_items` ON DELETE CASCADE; Zyklenfreiheit/gleiches Projekt über `IWorkItemHierarchyPolicy` (E-05) |
| `state_id` | `uuid` | ja | – | StateId: `Guid?` | FK `states` ON DELETE CASCADE; Default-State bei Anlage (`_ensure_default_state`), Schreiben nur über `IWorkItemStateChanger` (C1) |
| `point` | `smallint` | ja | – | Point: `short?` | Legacy (Original `Sum("point")`-Analytics, Q23); Spalte bleibt für Vertrag (`fields="__all__"`) |
| `estimate_point_id` | `uuid` | ja | – | EstimatePointId: `Guid?` | FK `estimate_points` ON DELETE SET NULL |
| `name` | `varchar(255)` | nein | – | Name: `string` | 1:1 |
| `description_json` | `jsonb` | nein | `'{}'::jsonb` | DescriptionJson: `JsonObject` | Lesemodell `ProseMirrorDoc` |
| `description_html` | `text` | nein | `'<p></p>'` | DescriptionHtml: `string` | 1:1 |
| `description_stripped` | `text` | ja | – | DescriptionStripped: `string?` | serverseitig aus HTML (`HtmlText.StripTags`, eine Implementierung, Q14) |
| `description_binary` | `bytea` | ja | – | DescriptionBinary: `byte[]?` | Yjs-Update (Rich-Text-Schema), nicht kanonisch für Work Items |
| `priority` | `varchar(30)` | nein | `'none'` | Priority: `string` | `urgent`, `high`, `medium`, `low`, `none` |
| `start_date` | `date` | ja | – | StartDate: `DateOnly?` | 1:1 |
| `target_date` | `date` | ja | – | TargetDate: `DateOnly?` | 1:1 |
| `sequence_id` | `integer` | nein | 1 | SequenceId: `int` | aus `ISequenceAllocator` (§3.6); unique je Projekt (Korrektur Q4) |
| `sort_order` | `double precision` | nein | 65535 | SortOrder: `double` | Anlage `max(project, state) + 10000` |
| `completed_at` | `timestamptz` | ja | – | CompletedAt: `DateTimeOffset?` | gesetzt/geleert bei State-Wechsel in/aus Gruppe `completed` |
| `archived_at` | `date` | ja | – | ArchivedAt: `DateOnly?` | **`date`** wie Original (Tagesgenauigkeit) |
| `is_draft` | `boolean` | nein | false | IsDraft: `bool` | Legacy-Flag, nach Anlage unveränderlich; Drafts liegen in `draft_work_items` |
| `external_source` | `varchar(255)` | ja | – | ExternalSource: `string?` | 1:1 |
| `external_id` | `varchar(255)` | ja | – | ExternalId: `string?` | 1:1 |
| `type_id` | `uuid` | ja | – | TypeId: `Guid?` | FK `work_item_types` ON DELETE SET NULL; A1-Andockstelle (P); CE immer `NULL` |

M2M des Originals als explizite Join-Entitäten: `assignees` → `work_item_assignees`, `labels` → `work_item_labels`.

**Indizes/Unique:** `ux_work_items_project_sequence_id` UNIQUE (`project_id`, `sequence_id`) – voll (Nummern werden nie wiederverwendet; Korrektur Q4, DEV-DM-05); `ix_work_items_project_state` (`project_id`, `state_id`) WHERE `deleted_at IS NULL`; `ix_work_items_project_created_at` (`project_id`, `created_at` DESC) WHERE `deleted_at IS NULL` – Default-Sortierung `-created_at`; `ix_work_items_workspace_updated_at` (`workspace_id`, `updated_at`) – Delta-Sync (CE-WI-012); `ix_work_items_parent_id` (`parent_id`) WHERE `parent_id IS NOT NULL`; `ix_work_items_type_id` (`type_id`) WHERE `type_id IS NOT NULL` (D16 §5.1); `ix_work_items_project_external` (`project_id`, `external_source`, `external_id`); GIN-Trigram `ix_work_items_name_trgm` (`name gin_trgm_ops`) – `name__icontains` (Suche, Filter `name`).

**Checks:** `ck_work_items_priority` CHECK (`priority IN ('urgent','high','medium','low','none')`); `ck_work_items_point` CHECK (`point IS NULL OR point BETWEEN 0 AND 12`); `ck_work_items_sequence_id` CHECK (`sequence_id >= 1`); `ck_work_items_not_own_parent` CHECK (`parent_id IS NULL OR parent_id <> id`); `ck_work_items_description_binary_size` CHECK (`description_binary IS NULL OR octet_length(description_binary) <= 10485760`).

**Hinweise:** Basismengen (`IssueObjects`, `AllObjects`, …) sind **Query-Spezifikationen** (D02 §3.11.4), kein globaler Filter (Korrektur Q1). Soft-Delete kaskadiert Inline (§3.5).

##### 3.4.5.2 `work_item_sequences` ← `IssueSequence` (`M/issue.py` Z. 557–571)

Entität `WorkItemSequence` · `[OwnedBy("WorkItems")]` · Basis eigene Form (Spalten vollständig gelistet) · ab **I2** · Status **ersetzt** · CE-IDs: CE-WI-002

| Spalte | PostgreSQL | Null | Default | C#-Property: Typ | Herkunft / Regel |
|---|---|---|---|---|---|
| `project_id` | `uuid` | nein | – | `ProjectId: Guid` | PK; FK `projects` ON DELETE CASCADE |
| `last_value` | `bigint` | nein | `0` | `LastValue: long` | zuletzt vergebene `sequence_id` |
| `updated_at` | `timestamptz` | nein | `now()` | `UpdatedAt: DateTimeOffset` | Diagnose |

**Checks:** `ck_work_item_sequences_last_value` CHECK (`last_value >= 0`).

**Hinweise:** Ersetzt die Zeile-je-Issue-Tabelle `issue_sequences` und den Advisory-Lock durch einen Zähler je Projekt (§3.6). Kein Soft-Delete, keine Audit-Spalten.

##### 3.4.5.3 `work_item_assignees` ← `IssueAssignee` (`M/issue.py` Z. 345–368)

Entität `WorkItemAssignee` · `[OwnedBy("WorkItems")]` · Basis `ProjectEntity` (Audit-Basis + `workspace_id`, `project_id` NOT NULL; Scope-FK) · ab **I2** · Status **übernommen** · CE-IDs: CE-WI-023, CE-LV-010

| Spalte | PostgreSQL | Null | Default | C#-Property: Typ | Herkunft / Regel |
|---|---|---|---|---|---|
| `work_item_id` | `uuid` | nein | – | WorkItemId: `Guid` | FK `work_items` ON DELETE CASCADE; Original `issue_id` |
| `assignee_id` | `uuid` | nein | – | AssigneeId: `Guid` | FK `users` ON DELETE CASCADE |

**Indizes/Unique:** `issue_assignee_unique_issue_assignee_when_deleted_at_null` UNIQUE (`work_item_id`, `assignee_id`) WHERE `deleted_at IS NULL`; `ix_work_item_assignees_assignee` (`assignee_id`) WHERE `deleted_at IS NULL` – „Assigned to me“, Gruppierung `assignees__id`.

##### 3.4.5.4 `work_item_labels` ← `IssueLabel` (`M/issue.py` Z. 543–554)

Entität `WorkItemLabel` · `[OwnedBy("WorkItems")]` · Basis `ProjectEntity` (Audit-Basis + `workspace_id`, `project_id` NOT NULL; Scope-FK) · ab **I2** · Status **angepasst** · CE-IDs: CE-WI-024, CE-LV-010

| Spalte | PostgreSQL | Null | Default | C#-Property: Typ | Herkunft / Regel |
|---|---|---|---|---|---|
| `work_item_id` | `uuid` | nein | – | WorkItemId: `Guid` | FK `work_items` ON DELETE CASCADE; Original `issue_id` |
| `label_id` | `uuid` | nein | – | LabelId: `Guid` | FK `labels` ON DELETE CASCADE |

**Indizes/Unique:** `ux_work_item_labels_work_item_label` UNIQUE (`work_item_id`, `label_id`) WHERE `deleted_at IS NULL` (neu; Original ohne Unique, 02b §2.7 d); `ix_work_item_labels_label` (`label_id`) WHERE `deleted_at IS NULL`.

##### 3.4.5.5 `work_item_relations` ← `IssueRelation` (`M/issue.py` Z. 296–320)

Entität `WorkItemRelation` · `[OwnedBy("WorkItems")]` · Basis `ProjectEntity` (Audit-Basis + `workspace_id`, `project_id` NOT NULL; Scope-FK) · ab **I2** · Status **angepasst** · CE-IDs: CE-WI-033, CE-LV-033, CE-API-024

| Spalte | PostgreSQL | Null | Default | C#-Property: Typ | Herkunft / Regel |
|---|---|---|---|---|---|
| `work_item_id` | `uuid` | nein | – | WorkItemId: `Guid` | FK `work_items` ON DELETE CASCADE; Original `issue_id` |
| `related_work_item_id` | `uuid` | nein | – | RelatedWorkItemId: `Guid` | FK `work_items` ON DELETE CASCADE; projektübergreifend zulässig (nur gleicher Workspace, A9); Original `related_issue_id` |
| `relation_type` | `varchar(30)` | nein | `'blocked_by'` | RelationType: `string` | FK auf Katalogschlüssel (A9) statt freier String (Korrektur Q19); gespeichert wird die Vorwärtsrichtung aus Sicht von `work_item_id` |

**Indizes/Unique:** `issue_relation_unique_issue_related_issue_when_deleted_at_null` UNIQUE (`work_item_id`, `related_work_item_id`) WHERE `deleted_at IS NULL`; `ix_work_item_relations_related` (`related_work_item_id`) WHERE `deleted_at IS NULL`.

**Checks:** `ck_work_item_relations_not_self` CHECK (`work_item_id <> related_work_item_id`).

**Hinweise:** `project_id`/`workspace_id` = Projekt des `work_item_id` (Original-Semantik). Eine Zeile je gerichtetem Paar; Gegenrichtung über `work_item_relation_types.reverse_key`.

##### 3.4.5.6 `work_item_mentions` ← `IssueMention` (`M/issue.py` Z. 323–342)

Entität `WorkItemMention` · `[OwnedBy("WorkItems")]` · Basis `ProjectEntity` (Audit-Basis + `workspace_id`, `project_id` NOT NULL; Scope-FK) · ab **I2** · Status **übernommen** · CE-IDs: CE-WI-044, CE-NOTIF-002

| Spalte | PostgreSQL | Null | Default | C#-Property: Typ | Herkunft / Regel |
|---|---|---|---|---|---|
| `work_item_id` | `uuid` | nein | – | WorkItemId: `Guid` | FK `work_items` ON DELETE CASCADE; Original `issue_id` |
| `mention_id` | `uuid` | nein | – | MentionId: `Guid` | FK `users` ON DELETE CASCADE |

**Indizes/Unique:** `issue_mention_unique_issue_mention_when_deleted_at_null` UNIQUE (`work_item_id`, `mention_id`) WHERE `deleted_at IS NULL`.

##### 3.4.5.7 `work_item_subscribers` ← `IssueSubscriber` (`M/issue.py` Z. 574–597)

Entität `WorkItemSubscriber` · `[OwnedBy("WorkItems")]` · Basis `ProjectEntity` (Audit-Basis + `workspace_id`, `project_id` NOT NULL; Scope-FK) · ab **I2** · Status **übernommen** · CE-IDs: CE-WI-043, CE-NOTIF-003

| Spalte | PostgreSQL | Null | Default | C#-Property: Typ | Herkunft / Regel |
|---|---|---|---|---|---|
| `work_item_id` | `uuid` | nein | – | WorkItemId: `Guid` | FK `work_items` ON DELETE CASCADE; Original `issue_id` |
| `subscriber_id` | `uuid` | nein | – | SubscriberId: `Guid` | FK `users` ON DELETE CASCADE |

**Indizes/Unique:** `issue_subscriber_unique_issue_subscriber_when_deleted_at_null` UNIQUE (`work_item_id`, `subscriber_id`) WHERE `deleted_at IS NULL`; `ix_work_item_subscribers_subscriber` (`subscriber_id`) WHERE `deleted_at IS NULL`.

##### 3.4.5.8 `work_item_links` ← `IssueLink` (`M/issue.py` Z. 371–384)

Entität `WorkItemLink` · `[OwnedBy("WorkItems")]` · Basis `ProjectEntity` (Audit-Basis + `workspace_id`, `project_id` NOT NULL; Scope-FK) · ab **I2** · Status **übernommen** · CE-IDs: CE-WI-035, CE-API-020

| Spalte | PostgreSQL | Null | Default | C#-Property: Typ | Herkunft / Regel |
|---|---|---|---|---|---|
| `title` | `varchar(255)` | ja | – | Title: `string?` | 1:1 |
| `url` | `text` | nein | – | Url: `string` | 1:1 |
| `work_item_id` | `uuid` | nein | – | WorkItemId: `Guid` | FK `work_items` ON DELETE CASCADE; Original `issue_id` |
| `metadata` | `jsonb` | nein | `'{}'::jsonb` | Metadata: `JsonObject` | Lesemodell `LinkMetadata` |

**Indizes/Unique:** `ix_work_item_links_work_item_id` (`work_item_id`) WHERE `deleted_at IS NULL`.

##### 3.4.5.9 `work_item_comments` ← `IssueComment` (`M/issue.py` Z. 451–540)

Entität `WorkItemComment` · `[OwnedBy("WorkItems")]` · Basis `ProjectEntity` (Audit-Basis + `workspace_id`, `project_id` NOT NULL; Scope-FK) · ab **I2** · Status **angepasst** · CE-IDs: CE-WI-037, CE-WI-044, CE-API-021, CE-SPACE-025

| Spalte | PostgreSQL | Null | Default | C#-Property: Typ | Herkunft / Regel |
|---|---|---|---|---|---|
| `comment_stripped` | `text` | nein | – | CommentStripped: `string` | `HtmlText.StripTags` |
| `comment_json` | `jsonb` | nein | `'{}'::jsonb` | CommentJson: `JsonObject` | Lesemodell `ProseMirrorDoc` |
| `comment_html` | `text` | nein | `'<p></p>'` | CommentHtml: `string` | 1:1 |
| ~~`description`~~ | – | – | – | – | entfällt: 1:1-Spiegel `descriptions` entfällt (Q15); DTO liefert `description: null` (DEV-DM-03) |
| `attachments` | `text[]` | nein | `'{}'` | Attachments: `List<string>` | Legacy-URL-Liste |
| `work_item_id` | `uuid` | nein | – | WorkItemId: `Guid` | FK `work_items` ON DELETE CASCADE; Original `issue_id` |
| `actor_id` | `uuid` | ja | – | ActorId: `Guid?` | FK `users` ON DELETE SET NULL (Original CASCADE); Original `CASCADE`; Benutzer werden nie gelöscht |
| `access` | `varchar(100)` | nein | `'INTERNAL'` | Access: `string` | `INTERNAL` \\| `EXTERNAL` (Space) |
| `external_source` | `varchar(255)` | ja | – | ExternalSource: `string?` | 1:1 |
| `external_id` | `varchar(255)` | ja | – | ExternalId: `string?` | 1:1 |
| `edited_at` | `timestamptz` | ja | – | EditedAt: `DateTimeOffset?` | vom Update-Handler gesetzt |
| `parent_id` | `uuid` | ja | – | ParentId: `Guid?` | FK `work_item_comments` ON DELETE CASCADE; V-Spalte (A16), CE nicht schreibbar |
| `teamspace_id` | `uuid` | ja | NULL | `TeamspaceId: Guid?` | B1-Vorhalt, ohne FK, CE immer `NULL` |

**Indizes/Unique:** `ix_work_item_comments_work_item_created` (`work_item_id`, `created_at`) WHERE `deleted_at IS NULL`; `ix_work_item_comments_teamspace_id` (`teamspace_id`) WHERE `teamspace_id IS NOT NULL`.

**Checks:** `ck_work_item_comments_access` CHECK (`access IN ('INTERNAL','EXTERNAL')`).

##### 3.4.5.10 `work_item_reactions` ← `IssueReaction` (`M/issue.py` Z. 600–624)

Entität `WorkItemReaction` · `[OwnedBy("WorkItems")]` · Basis `ProjectEntity` (Audit-Basis + `workspace_id`, `project_id` NOT NULL; Scope-FK) · ab **I2** · Status **übernommen** · CE-IDs: CE-WI-038, CE-SPACE-027

| Spalte | PostgreSQL | Null | Default | C#-Property: Typ | Herkunft / Regel |
|---|---|---|---|---|---|
| `actor_id` | `uuid` | nein | – | ActorId: `Guid` | FK `users` ON DELETE CASCADE |
| `work_item_id` | `uuid` | nein | – | WorkItemId: `Guid` | FK `work_items` ON DELETE CASCADE; Original `issue_id` |
| `reaction` | `text` | nein | – | Reaction: `string` | 1:1 |

**Indizes/Unique:** `issue_reaction_unique_issue_actor_reaction_when_deleted_at_null` UNIQUE (`work_item_id`, `actor_id`, `reaction`) WHERE `deleted_at IS NULL`.

##### 3.4.5.11 `work_item_comment_reactions` ← `CommentReaction` (`M/issue.py` Z. 627–651)

Entität `WorkItemCommentReaction` · `[OwnedBy("WorkItems")]` · Basis `ProjectEntity` (Audit-Basis + `workspace_id`, `project_id` NOT NULL; Scope-FK) · ab **I2** · Status **übernommen** · CE-IDs: CE-WI-038, CE-SPACE-026

| Spalte | PostgreSQL | Null | Default | C#-Property: Typ | Herkunft / Regel |
|---|---|---|---|---|---|
| `actor_id` | `uuid` | nein | – | ActorId: `Guid` | FK `users` ON DELETE CASCADE |
| `comment_id` | `uuid` | nein | – | CommentId: `Guid` | FK `work_item_comments` ON DELETE CASCADE |
| `reaction` | `text` | nein | – | Reaction: `string` | 1:1 |

**Indizes/Unique:** `comment_reaction_unique_comment_actor_reaction_when_deleted_at_null` UNIQUE (`comment_id`, `actor_id`, `reaction`) WHERE `deleted_at IS NULL`.

##### 3.4.5.12 `work_item_votes` ← `IssueVote` (`M/issue.py` Z. 654–674)

Entität `WorkItemVote` · `[OwnedBy("WorkItems")]` · Basis `ProjectEntity` (Audit-Basis + `workspace_id`, `project_id` NOT NULL; Scope-FK) · ab **I6** · Status **übernommen** · CE-IDs: CE-SPACE-028

| Spalte | PostgreSQL | Null | Default | C#-Property: Typ | Herkunft / Regel |
|---|---|---|---|---|---|
| `work_item_id` | `uuid` | nein | – | WorkItemId: `Guid` | FK `work_items` ON DELETE CASCADE; Original `issue_id` |
| `actor_id` | `uuid` | nein | – | ActorId: `Guid` | FK `users` ON DELETE CASCADE |
| `vote` | `integer` | nein | 1 | Vote: `int` | -1 \\| 1 |

**Indizes/Unique:** `issue_vote_unique_issue_actor_when_deleted_at_null` UNIQUE (`work_item_id`, `actor_id`) WHERE `deleted_at IS NULL`.

**Checks:** `ck_work_item_votes_vote` CHECK (`vote IN (-1,1)`).

**Hinweise:** Geschrieben vom Modul `Plane.PublicSpace` über `IWorkItemCommands` (R5).

##### 3.4.5.13 `work_item_activities` ← `IssueActivity` (`M/issue.py` Z. 415–448)

Entität `WorkItemActivity` · `[OwnedBy("WorkItems")]` · Basis `ProjectEntity` (Audit-Basis + `workspace_id`, `project_id` NOT NULL; Scope-FK) · ab **I2** · Status **angepasst** · CE-IDs: CE-WI-039, CE-WI-040, CE-API-022, CE-PROF-010, CE-NOTIF-001

| Spalte | PostgreSQL | Null | Default | C#-Property: Typ | Herkunft / Regel |
|---|---|---|---|---|---|
| `work_item_id` | `uuid` | ja | – | WorkItemId: `Guid?` | FK `work_items` ON DELETE CASCADE (Original DO NOTHING); Original `DO_NOTHING` → Hard-Delete brach ab (Q3); Ziel: Kaskade nur beim **Hard**-Delete, Soft-Delete lässt Activity stehen (NoSoftCascade); Original `issue_id` |
| `verb` | `varchar(255)` | nein | `'created'` | Verb: `string` | 1:1 |
| `field` | `varchar(255)` | ja | – | Field: `string?` | Feldname; reserviert `forgejo_branch`, `forgejo_commit`, `forgejo_pull_request` (F2, D02 §6) |
| `old_value` | `text` | ja | – | OldValue: `string?` | 1:1 |
| `new_value` | `text` | ja | – | NewValue: `string?` | 1:1 |
| `comment` | `text` | nein | – | Comment: `string` | 1:1 |
| `attachments` | `text[]` | nein | `'{}'` | Attachments: `List<string>` | Legacy-URL-Liste (`varchar(200)[]` im Original, max. 10) |
| `comment_id` | `uuid` | ja | – | CommentId: `Guid?` | FK `work_item_comments` ON DELETE SET NULL (Original DO NOTHING); Original `DO_NOTHING`; Original `issue_comment_id` |
| `actor_id` | `uuid` | ja | – | ActorId: `Guid?` | FK `users` ON DELETE SET NULL |
| `old_identifier` | `uuid` | ja | – | OldIdentifier: `Guid?` | 1:1 |
| `new_identifier` | `uuid` | ja | – | NewIdentifier: `Guid?` | 1:1 |
| `epoch` | `double precision` | ja | – | Epoch: `double?` | Unix-Sekunden als Float (Vertrag) |

**Indizes/Unique:** `ix_work_item_activities_work_item_created` (`work_item_id`, `created_at`); `ix_work_item_activities_workspace_actor_created` (`workspace_id`, `actor_id`, `created_at` DESC) – Profil-Aktivität (CE-PROF-010); `ix_work_item_activities_project_created` (`project_id`, `created_at` DESC) – Projekt-/Workspace-Aktivität.

**Hinweise:** Wird ausschließlich vom `ActivityRecorder` im selben `SaveChanges` geschrieben (01 §7.8, D02-ADR-25). Append-only.

##### 3.4.5.14 `work_item_description_versions` ← `IssueDescriptionVersion` (`M/issue.py` Z. 782–822)

Entität `WorkItemDescriptionVersion` · `[OwnedBy("WorkItems")]` · Basis `ProjectEntity` (Audit-Basis + `workspace_id`, `project_id` NOT NULL; Scope-FK) · ab **I2** · Status **übernommen** · CE-IDs: CE-WI-041

| Spalte | PostgreSQL | Null | Default | C#-Property: Typ | Herkunft / Regel |
|---|---|---|---|---|---|
| `work_item_id` | `uuid` | nein | – | WorkItemId: `Guid` | FK `work_items` ON DELETE CASCADE; Original `issue_id` |
| `description_binary` | `bytea` | ja | – | DescriptionBinary: `byte[]?` | 1:1 |
| `description_html` | `text` | nein | `'<p></p>'` | DescriptionHtml: `string` | 1:1 |
| `description_stripped` | `text` | ja | – | DescriptionStripped: `string?` | 1:1 |
| `description_json` | `jsonb` | nein | `'{}'::jsonb` | DescriptionJson: `JsonObject` | Lesemodell `ProseMirrorDoc` |
| `last_saved_at` | `timestamptz` | nein | `now()` | LastSavedAt: `DateTimeOffset` | 1:1 |
| `owned_by_id` | `uuid` | nein | – | OwnedById: `Guid` | FK `users` ON DELETE SET NULL (Original CASCADE); Original `CASCADE` |

**Indizes/Unique:** `ix_work_item_description_versions_work_item_last_saved` (`work_item_id`, `last_saved_at` DESC).

**Hinweise:** Merge-Regel: jüngste Version desselben Nutzers ≤ 600 s → überschreiben (02b §3.6). Aufbewahrung: je Work Item die 20 neuesten (Instanz-Einstellung `Plane:Retention:WorkItemDescriptionVersions`, Default 20), Hard-Delete-Job täglich 03:15 UTC.

##### 3.4.5.15 `work_item_versions` ← `IssueVersion` (`M/issue.py` Z. 677–779)

Entität `WorkItemVersion` · `[OwnedBy("WorkItems")]` · Basis `ProjectEntity` (Audit-Basis + `workspace_id`, `project_id` NOT NULL; Scope-FK) · ab **I2** · Status **korrigiert** · CE-IDs: CE-WI-042

| Spalte | PostgreSQL | Null | Default | C#-Property: Typ | Herkunft / Regel |
|---|---|---|---|---|---|
| `parent` | `uuid` | ja | – | Parent: `Guid?` | Snapshot-ID, kein FK |
| `state` | `uuid` | ja | – | State: `Guid?` | Snapshot-ID, kein FK |
| `estimate_point` | `uuid` | ja | – | EstimatePoint: `Guid?` | Snapshot-ID |
| `name` | `varchar(255)` | nein | – | Name: `string` | 1:1 |
| `priority` | `varchar(30)` | nein | `'none'` | Priority: `string` | Choices: PRIORITY_CHOICES |
| `start_date` | `date` | ja | – | StartDate: `DateOnly?` | 1:1 |
| `target_date` | `date` | ja | – | TargetDate: `DateOnly?` | 1:1 |
| `assignees` | `uuid[]` | nein | `'{}'` | Assignees: `List<Guid>` | 1:1 |
| `sequence_id` | `integer` | nein | 1 | SequenceId: `int` | 1:1 |
| `labels` | `uuid[]` | nein | `'{}'` | Labels: `List<Guid>` | 1:1 |
| `sort_order` | `double precision` | nein | 65535 | SortOrder: `double` | 1:1 |
| `completed_at` | `timestamptz` | ja | – | CompletedAt: `DateTimeOffset?` | 1:1 |
| `archived_at` | `date` | ja | – | ArchivedAt: `DateOnly?` | `date` wie `work_items` |
| `is_draft` | `boolean` | nein | false | IsDraft: `bool` | 1:1 |
| `external_source` | `varchar(255)` | ja | – | ExternalSource: `string?` | 1:1 |
| `external_id` | `varchar(255)` | ja | – | ExternalId: `string?` | 1:1 |
| `type` | `uuid` | ja | – | Type: `Guid?` | Snapshot-ID |
| `cycle` | `uuid` | ja | – | Cycle: `Guid?` | Snapshot-ID |
| `modules` | `uuid[]` | nein | `'{}'` | Modules: `List<Guid>` | 1:1 |
| `properties` | `jsonb` | nein | `'{}'::jsonb` | Properties: `JsonObject` | CE `{}` |
| `meta` | `jsonb` | nein | `'{}'::jsonb` | Meta: `JsonObject` | CE `{}` |
| `last_saved_at` | `timestamptz` | nein | `now()` | LastSavedAt: `DateTimeOffset` | 1:1 |
| `work_item_id` | `uuid` | nein | – | WorkItemId: `Guid` | FK `work_items` ON DELETE CASCADE; Original `issue_id` |
| `activity_id` | `uuid` | ja | – | ActivityId: `Guid?` | FK `work_item_activities` ON DELETE SET NULL |
| `owned_by_id` | `uuid` | nein | – | OwnedById: `Guid` | FK `users` ON DELETE SET NULL (Original CASCADE); Original `CASCADE` |

**Indizes/Unique:** `ix_work_item_versions_work_item_last_saved` (`work_item_id`, `last_saved_at` DESC).

**Hinweise:** Original schreibt nie Versionen (`log_issue_version` scheitert, Q11). Ziel: `WorkItemVersionRecorder` schreibt bei jeder Property-Änderung (Merge-Regel 600 s/gleicher Owner wie `issue_task`) – Korrektur (DEV-DM-06).

##### 3.4.5.16 `draft_work_items` ← `DraftIssue` (`M/draft.py` Z. 16–136)

Entität `DraftWorkItem` · `[OwnedBy("WorkItems")]` · Basis `WorkspaceEntity` (Audit-Basis + `workspace_id` NOT NULL, `project_id` NULL) · ab **I2** · Status **angepasst** · CE-IDs: CE-WI-049, CE-WI-007

| Spalte | PostgreSQL | Null | Default | C#-Property: Typ | Herkunft / Regel |
|---|---|---|---|---|---|
| `parent_id` | `uuid` | ja | – | ParentId: `Guid?` | FK `work_items` ON DELETE SET NULL (Original CASCADE); Original `CASCADE` (Löschen eines Work Items löschte Drafts, 02b §3.1 b) → `SET NULL` (DEV-DM-07) |
| `state_id` | `uuid` | ja | – | StateId: `Guid?` | FK `states` ON DELETE SET NULL (Original CASCADE); Original `CASCADE` (State-Löschung löschte Drafts ungeprüft, Q17) → `SET NULL` |
| `estimate_point_id` | `uuid` | ja | – | EstimatePointId: `Guid?` | FK `estimate_points` ON DELETE SET NULL |
| `name` | `varchar(255)` | ja | – | Name: `string?` | 1:1 |
| `description_json` | `jsonb` | nein | `'{}'::jsonb` | DescriptionJson: `JsonObject` | Lesemodell `ProseMirrorDoc` |
| `description_html` | `text` | nein | `'<p></p>'` | DescriptionHtml: `string` | 1:1 |
| `description_stripped` | `text` | ja | – | DescriptionStripped: `string?` | 1:1 |
| `description_binary` | `bytea` | ja | – | DescriptionBinary: `byte[]?` | 1:1 |
| `priority` | `varchar(30)` | nein | `'none'` | Priority: `string` | Choices: PRIORITY_CHOICES |
| `start_date` | `date` | ja | – | StartDate: `DateOnly?` | 1:1 |
| `target_date` | `date` | ja | – | TargetDate: `DateOnly?` | 1:1 |
| `sort_order` | `double precision` | nein | 65535 | SortOrder: `double` | 1:1 |
| `completed_at` | `timestamptz` | ja | – | CompletedAt: `DateTimeOffset?` | nur bei State-Wechsel neu gesetzt (Korrektur Q13) |
| `external_source` | `varchar(255)` | ja | – | ExternalSource: `string?` | 1:1 |
| `external_id` | `varchar(255)` | ja | – | ExternalId: `string?` | 1:1 |
| `type_id` | `uuid` | ja | – | TypeId: `Guid?` | FK `work_item_types` ON DELETE SET NULL; A1 (P) |

M2M des Originals als explizite Join-Entitäten: `assignees` → `draft_work_item_assignees`, `labels` → `draft_work_item_labels`.

**Indizes/Unique:** `ix_draft_work_items_workspace_created_by` (`workspace_id`, `created_by_id`) WHERE `deleted_at IS NULL` – „meine Drafts“; `ix_draft_work_items_type_id` (`type_id`) WHERE `type_id IS NOT NULL`.

**Checks:** `ck_draft_work_items_priority` CHECK (`priority IN ('urgent','high','medium','low','none')`).

**Hinweise:** Drafts verbrauchen **keine** `sequence_id`; bei Umwandlung in ein Work Item wird eine neue Nummer vergeben.

##### 3.4.5.17 `draft_work_item_assignees` ← `DraftIssueAssignee` (`M/draft.py` Z. 139–162)

Entität `DraftWorkItemAssignee` · `[OwnedBy("WorkItems")]` · Basis `WorkspaceEntity` (Audit-Basis + `workspace_id` NOT NULL, `project_id` NULL) · ab **I2** · Status **übernommen** · CE-IDs: CE-WI-049

| Spalte | PostgreSQL | Null | Default | C#-Property: Typ | Herkunft / Regel |
|---|---|---|---|---|---|
| `draft_work_item_id` | `uuid` | nein | – | DraftWorkItemId: `Guid` | FK `draft_work_items` ON DELETE CASCADE; Original `draft_issue_id` |
| `assignee_id` | `uuid` | nein | – | AssigneeId: `Guid` | FK `users` ON DELETE CASCADE |

**Indizes/Unique:** `draft_issue_assignee_unique_issue_assignee_when_deleted_at_null` UNIQUE (`draft_work_item_id`, `assignee_id`) WHERE `deleted_at IS NULL`.

##### 3.4.5.18 `draft_work_item_labels` ← `DraftIssueLabel` (`M/draft.py` Z. 165–176)

Entität `DraftWorkItemLabel` · `[OwnedBy("WorkItems")]` · Basis `WorkspaceEntity` (Audit-Basis + `workspace_id` NOT NULL, `project_id` NULL) · ab **I2** · Status **angepasst** · CE-IDs: CE-WI-049

| Spalte | PostgreSQL | Null | Default | C#-Property: Typ | Herkunft / Regel |
|---|---|---|---|---|---|
| `draft_work_item_id` | `uuid` | nein | – | DraftWorkItemId: `Guid` | FK `draft_work_items` ON DELETE CASCADE; Original `draft_issue_id` |
| `label_id` | `uuid` | nein | – | LabelId: `Guid` | FK `labels` ON DELETE CASCADE |

**Indizes/Unique:** `ux_draft_work_item_labels` UNIQUE (`draft_work_item_id`, `label_id`) WHERE `deleted_at IS NULL` (neu).

##### 3.4.5.19 `draft_work_item_modules` ← `DraftIssueModule` (`M/draft.py` Z. 179–198)

Entität `DraftWorkItemModule` · `[OwnedBy("WorkItems")]` · Basis `WorkspaceEntity` (Audit-Basis + `workspace_id` NOT NULL, `project_id` NULL) · ab **I3** · Status **übernommen** · CE-IDs: CE-WI-049

| Spalte | PostgreSQL | Null | Default | C#-Property: Typ | Herkunft / Regel |
|---|---|---|---|---|---|
| `module_id` | `uuid` | nein | – | ModuleId: `Guid` | FK `modules` ON DELETE CASCADE |
| `draft_work_item_id` | `uuid` | nein | – | DraftWorkItemId: `Guid` | FK `draft_work_items` ON DELETE CASCADE; Original `draft_issue_id` |

**Indizes/Unique:** `module_draft_issue_unique_issue_module_when_deleted_at_null` UNIQUE (`draft_work_item_id`, `module_id`) WHERE `deleted_at IS NULL`.

##### 3.4.5.20 `draft_work_item_cycles` ← `DraftIssueCycle` (`M/draft.py` Z. 201–224)

Entität `DraftWorkItemCycle` · `[OwnedBy("WorkItems")]` · Basis `WorkspaceEntity` (Audit-Basis + `workspace_id` NOT NULL, `project_id` NULL) · ab **I3** · Status **übernommen** · CE-IDs: CE-WI-049

| Spalte | PostgreSQL | Null | Default | C#-Property: Typ | Herkunft / Regel |
|---|---|---|---|---|---|
| `draft_work_item_id` | `uuid` | nein | – | DraftWorkItemId: `Guid` | FK `draft_work_items` ON DELETE CASCADE; Original `draft_issue_id` |
| `cycle_id` | `uuid` | nein | – | CycleId: `Guid` | FK `cycles` ON DELETE CASCADE |

**Indizes/Unique:** `draft_issue_cycle_when_deleted_at_null` UNIQUE (`draft_work_item_id`, `cycle_id`) WHERE `deleted_at IS NULL`.

##### 3.4.5.21 `work_item_types` ← `IssueType` (`M/issue_type.py` Z. 14–32)

Entität `WorkItemType` · `[OwnedBy("Properties")]` · Basis `WorkspaceEntity` (Audit-Basis + `workspace_id` NOT NULL, `project_id` NULL) · ab **I2** · Status **minimal** · CE-IDs: – (A1-Andockstelle; CE liest nur `NULL`)

| Spalte | PostgreSQL | Null | Default | C#-Property: Typ | Herkunft / Regel |
|---|---|---|---|---|---|
| `workspace_id` | `uuid` | nein | – | WorkspaceId: `Guid` | FK `workspaces` ON DELETE CASCADE |
| `name` | `varchar(255)` | nein | – | Name: `string` | 1:1 |
| ~~`description`~~ | – | – | – | – | entfällt: fachliche Spalte, erst mit W2 (D16 §5.1) |
| ~~`logo_props`~~ | – | – | – | – | entfällt: W2 |
| ~~`is_epic`~~ | – | – | – | – | entfällt: W2 (A3) |
| `is_default` | `boolean` | nein | false | IsDefault: `bool` | 1:1 |
| ~~`is_active`~~ | – | – | – | – | entfällt: W2 |
| ~~`level`~~ | – | – | – | – | entfällt: W2 |
| ~~`external_source`~~ | – | – | – | – | entfällt: W2 |
| ~~`external_id`~~ | – | – | – | – | entfällt: W2 |

**Indizes/Unique:** `ix_work_item_types_workspace_project` (`workspace_id`, `project_id`).

**Hinweise:** Minimal-Schema nach 01 §1.4 / D16 §5.1: `id`, `workspace_id`, `project_id` (nullable, A2), `name`, `is_default` + Audit. `[OwnedBy("Properties")]`; in der CE schreibt niemand (Tabelle leer). Original-Basis `BaseModel` + `workspace`; Ziel `WorkspaceEntity` (bringt `project_id` nullable mit).

#### 3.4.6 Modul Cycles

##### 3.4.6.1 `cycles` ← `Cycle` (`M/cycle.py` Z. 60–101)

Entität `Cycle` · `[OwnedBy("Cycles")]` · Basis `ProjectEntity` (Audit-Basis + `workspace_id`, `project_id` NOT NULL; Scope-FK) · ab **I3** · Status **übernommen** · CE-IDs: CE-CYC-001…CE-CYC-015, CE-API-026…CE-API-029, CE-ANA-008

| Spalte | PostgreSQL | Null | Default | C#-Property: Typ | Herkunft / Regel |
|---|---|---|---|---|---|
| `name` | `varchar(255)` | nein | – | Name: `string` | 1:1 |
| `description` | `text` | nein | – | Description: `string` | 1:1 |
| `start_date` | `timestamptz` | ja | – | StartDate: `DateTimeOffset?` | `timestamptz` (Eingabe in Projekt-TZ interpretiert) |
| `end_date` | `timestamptz` | ja | – | EndDate: `DateTimeOffset?` | `timestamptz` |
| `owned_by_id` | `uuid` | nein | – | OwnedById: `Guid` | FK `users` ON DELETE RESTRICT (Original CASCADE); Original `CASCADE` |
| `view_props` | `jsonb` | nein | `'{}'::jsonb` | ViewProps: `JsonObject` | Legacy `{filters}` |
| `sort_order` | `double precision` | nein | 65535 | SortOrder: `double` | Anlage `min(project) − 10000` |
| `external_source` | `varchar(255)` | ja | – | ExternalSource: `string?` | 1:1 |
| `external_id` | `varchar(255)` | ja | – | ExternalId: `string?` | 1:1 |
| `progress_snapshot` | `jsonb` | nein | `'{}'::jsonb` | ProgressSnapshot: `JsonObject` | Lesemodell `CycleProgressSnapshot` |
| `archived_at` | `timestamptz` | ja | – | ArchivedAt: `DateTimeOffset?` | 1:1 |
| `logo_props` | `jsonb` | nein | `'{}'::jsonb` | LogoProps: `JsonObject` | Lesemodell `LogoProps` |
| `timezone` | `varchar(255)` | nein | `'UTC'` | Timezone: `string` | Vertragsfeld; Logik nutzt `projects.timezone` |
| `version` | `integer` | nein | 1 | Version: `int` | 1 (CE); 2 = Fortschritt aus `progress`-Array (B3/B4) |

**Indizes/Unique:** `ix_cycles_project_dates` (`project_id`, `start_date`, `end_date`) WHERE `deleted_at IS NULL` – Überschneidungsprüfung CE-CYC-006, Status; GIN-Trigram `ix_cycles_name_trgm`.

**Checks:** `ck_cycles_dates` CHECK (`start_date IS NULL OR end_date IS NULL OR start_date <= end_date`).

##### 3.4.6.2 `cycle_work_items` ← `CycleIssue` (`M/cycle.py` Z. 104–127)

Entität `CycleWorkItem` · `[OwnedBy("Cycles")]` · Basis `ProjectEntity` (Audit-Basis + `workspace_id`, `project_id` NOT NULL; Scope-FK) · ab **I3** · Status **angepasst** · CE-IDs: CE-CYC-010, CE-CYC-011, CE-API-027, CE-WI-025

| Spalte | PostgreSQL | Null | Default | C#-Property: Typ | Herkunft / Regel |
|---|---|---|---|---|---|
| `work_item_id` | `uuid` | nein | – | WorkItemId: `Guid` | FK `work_items` ON DELETE CASCADE; Original `issue_id` |
| `cycle_id` | `uuid` | nein | – | CycleId: `Guid` | FK `cycles` ON DELETE CASCADE |

**Indizes/Unique:** `cycle_issue_when_deleted_at_null` UNIQUE (`cycle_id`, `work_item_id`) WHERE `deleted_at IS NULL`; `ux_cycle_work_items_work_item` UNIQUE (`work_item_id`) WHERE `deleted_at IS NULL` (neu: höchstens ein aktiver Cycle je Work Item – fachliche Regel „Zuordnen verschiebt“, DEV-DM-08).

##### 3.4.6.3 `cycle_user_properties` ← `CycleUserProperties` (`M/cycle.py` Z. 130–157)

Entität `CycleUserProperties` · `[OwnedBy("Cycles")]` · Basis `ProjectEntity` (Audit-Basis + `workspace_id`, `project_id` NOT NULL; Scope-FK) · ab **I3** · Status **übernommen** · CE-IDs: CE-LV-016

| Spalte | PostgreSQL | Null | Default | C#-Property: Typ | Herkunft / Regel |
|---|---|---|---|---|---|
| `cycle_id` | `uuid` | nein | – | CycleId: `Guid` | FK `cycles` ON DELETE CASCADE |
| `user_id` | `uuid` | nein | – | UserId: `Guid` | FK `users` ON DELETE CASCADE |
| `filters` | `jsonb` | nein | `JsonDefaults.LegacyFilters` (DB-Default = gleiches Literal) | Filters: `JsonObject` | Lesemodell `LegacyIssueFilters` |
| `display_filters` | `jsonb` | nein | `JsonDefaults.DisplayFilters` (DB-Default = gleiches Literal) | DisplayFilters: `JsonObject` | Lesemodell `DisplayFilters` |
| `display_properties` | `jsonb` | nein | `JsonDefaults.DisplayProperties` (DB-Default = gleiches Literal) | DisplayProperties: `JsonObject` | Lesemodell `DisplayProperties` |
| `rich_filters` | `jsonb` | nein | `'{}'::jsonb` | RichFilters: `JsonObject` | Lesemodell `RichFilterNode` |

**Indizes/Unique:** `cycle_user_properties_unique_cycle_user_when_deleted_at_null` UNIQUE (`cycle_id`, `user_id`) WHERE `deleted_at IS NULL`.

#### 3.4.7 Modul ProjectModules (Plane-„Modules“)

##### 3.4.7.1 `modules` ← `Module` (`M/module.py` Z. 67–127)

Entität `Module` · `[OwnedBy("ProjectModules")]` · Basis `ProjectEntity` (Audit-Basis + `workspace_id`, `project_id` NOT NULL; Scope-FK) · ab **I3** · Status **angepasst** · CE-IDs: CE-MOD-001…CE-MOD-011, CE-API-030…CE-API-032, CE-ANA-008

| Spalte | PostgreSQL | Null | Default | C#-Property: Typ | Herkunft / Regel |
|---|---|---|---|---|---|
| `name` | `varchar(255)` | nein | – | Name: `string` | 1:1 |
| `description` | `text` | nein | – | Description: `string` | 1:1 |
| `description_text` | `jsonb` | ja | – | DescriptionText: `JsonObject?` | Legacy |
| `description_html` | `text` | ja | – | DescriptionHtml: `string?` | Original `JSONField` (wie `projects`) → `text` |
| `start_date` | `date` | ja | – | StartDate: `DateOnly?` | 1:1 |
| `target_date` | `date` | ja | – | TargetDate: `DateOnly?` | 1:1 |
| `status` | `varchar(20)` | nein | `'planned'` | Status: `string` | `backlog`, `planned`, `in-progress`, `paused`, `completed`, `cancelled` |
| `lead_id` | `uuid` | ja | – | LeadId: `Guid?` | FK `users` ON DELETE SET NULL |
| `view_props` | `jsonb` | nein | `'{}'::jsonb` | ViewProps: `JsonObject` | Legacy |
| `sort_order` | `double precision` | nein | 65535 | SortOrder: `double` | Anlage `min(project) − 10000` |
| `external_source` | `varchar(255)` | ja | – | ExternalSource: `string?` | 1:1 |
| `external_id` | `varchar(255)` | ja | – | ExternalId: `string?` | 1:1 |
| `archived_at` | `timestamptz` | ja | – | ArchivedAt: `DateTimeOffset?` | 1:1 |
| `logo_props` | `jsonb` | nein | `'{}'::jsonb` | LogoProps: `JsonObject` | Lesemodell `LogoProps` |

M2M des Originals als explizite Join-Entitäten: `members` → `module_members`.

**Indizes/Unique:** `module_unique_name_project_when_deleted_at_null` UNIQUE (`name`, `project_id`) WHERE `deleted_at IS NULL`; GIN-Trigram `ix_modules_name_trgm`.

**Checks:** `ck_modules_status` CHECK (`status IN ('backlog','planned','in-progress','paused','completed','cancelled')`); `ck_modules_dates` CHECK (`start_date IS NULL OR target_date IS NULL OR start_date <= target_date`).

##### 3.4.7.2 `module_members` ← `ModuleMember` (`M/module.py` Z. 130–149)

Entität `ModuleMember` · `[OwnedBy("ProjectModules")]` · Basis `ProjectEntity` (Audit-Basis + `workspace_id`, `project_id` NOT NULL; Scope-FK) · ab **I3** · Status **übernommen** · CE-IDs: CE-MOD-006

| Spalte | PostgreSQL | Null | Default | C#-Property: Typ | Herkunft / Regel |
|---|---|---|---|---|---|
| `module_id` | `uuid` | nein | – | ModuleId: `Guid` | FK `modules` ON DELETE CASCADE |
| `member_id` | `uuid` | nein | – | MemberId: `Guid` | FK `users` ON DELETE CASCADE |

**Indizes/Unique:** `module_member_unique_module_member_when_deleted_at_null` UNIQUE (`module_id`, `member_id`) WHERE `deleted_at IS NULL`.

##### 3.4.7.3 `module_work_items` ← `ModuleIssue` (`M/module.py` Z. 152–171)

Entität `ModuleWorkItem` · `[OwnedBy("ProjectModules")]` · Basis `ProjectEntity` (Audit-Basis + `workspace_id`, `project_id` NOT NULL; Scope-FK) · ab **I3** · Status **übernommen** · CE-IDs: CE-MOD-008, CE-API-031, CE-WI-026

| Spalte | PostgreSQL | Null | Default | C#-Property: Typ | Herkunft / Regel |
|---|---|---|---|---|---|
| `module_id` | `uuid` | nein | – | ModuleId: `Guid` | FK `modules` ON DELETE CASCADE |
| `work_item_id` | `uuid` | nein | – | WorkItemId: `Guid` | FK `work_items` ON DELETE CASCADE; Original `issue_id` |

**Indizes/Unique:** `module_issue_unique_issue_module_when_deleted_at_null` UNIQUE (`work_item_id`, `module_id`) WHERE `deleted_at IS NULL`; `ix_module_work_items_module` (`module_id`) WHERE `deleted_at IS NULL`.

##### 3.4.7.4 `module_links` ← `ModuleLink` (`M/module.py` Z. 174–187)

Entität `ModuleLink` · `[OwnedBy("ProjectModules")]` · Basis `ProjectEntity` (Audit-Basis + `workspace_id`, `project_id` NOT NULL; Scope-FK) · ab **I3** · Status **übernommen** · CE-IDs: CE-MOD-005

| Spalte | PostgreSQL | Null | Default | C#-Property: Typ | Herkunft / Regel |
|---|---|---|---|---|---|
| `title` | `varchar(255)` | ja | – | Title: `string?` | 1:1 |
| `url` | `varchar(200)` | nein | – | Url: `string` | Original `URLField` → `varchar(200)` (Q22, Validierungsgrenze bleibt) |
| `module_id` | `uuid` | nein | – | ModuleId: `Guid` | FK `modules` ON DELETE CASCADE |
| `metadata` | `jsonb` | nein | `'{}'::jsonb` | Metadata: `JsonObject` | 1:1 |

##### 3.4.7.5 `module_user_properties` ← `ModuleUserProperties` (`M/module.py` Z. 190–217)

Entität `ModuleUserProperties` · `[OwnedBy("ProjectModules")]` · Basis `ProjectEntity` (Audit-Basis + `workspace_id`, `project_id` NOT NULL; Scope-FK) · ab **I3** · Status **übernommen** · CE-IDs: CE-LV-016

| Spalte | PostgreSQL | Null | Default | C#-Property: Typ | Herkunft / Regel |
|---|---|---|---|---|---|
| `module_id` | `uuid` | nein | – | ModuleId: `Guid` | FK `modules` ON DELETE CASCADE |
| `user_id` | `uuid` | nein | – | UserId: `Guid` | FK `users` ON DELETE CASCADE |
| `filters` | `jsonb` | nein | `JsonDefaults.LegacyFilters` (DB-Default = gleiches Literal) | Filters: `JsonObject` | Lesemodell `LegacyIssueFilters` |
| `display_filters` | `jsonb` | nein | `JsonDefaults.DisplayFilters` (DB-Default = gleiches Literal) | DisplayFilters: `JsonObject` | Lesemodell `DisplayFilters` |
| `display_properties` | `jsonb` | nein | `JsonDefaults.DisplayProperties` (DB-Default = gleiches Literal) | DisplayProperties: `JsonObject` | Lesemodell `DisplayProperties` |
| `rich_filters` | `jsonb` | nein | `'{}'::jsonb` | RichFilters: `JsonObject` | Lesemodell `RichFilterNode` |

**Indizes/Unique:** `module_user_properties_unique_module_user_when_deleted_at_null` UNIQUE (`module_id`, `user_id`) WHERE `deleted_at IS NULL`.

#### 3.4.8 Modul Views

##### 3.4.8.1 `views` ← `IssueView` (`M/view.py` Z. 58–99)

Entität `View` · `[OwnedBy("Views")]` · Basis `WorkspaceEntity` (Audit-Basis + `workspace_id` NOT NULL, `project_id` NULL) · ab **I3** · Status **angepasst** · CE-IDs: CE-LV-011, CE-LV-047…CE-LV-054

| Spalte | PostgreSQL | Null | Default | C#-Property: Typ | Herkunft / Regel |
|---|---|---|---|---|---|
| `name` | `varchar(255)` | nein | – | Name: `string` | 1:1 |
| `description` | `text` | nein | – | Description: `string` | 1:1 |
| `query` | `jsonb` | nein | – | Query: `JsonObject` | Legacy-Lookup-Cache, aus `filters` abgeleitet; nur Vertrag |
| `filters` | `jsonb` | nein | `'{}'::jsonb` | Filters: `JsonObject` | Lesemodell `LegacyIssueFilters` |
| `display_filters` | `jsonb` | nein | `JsonDefaults.DisplayFilters` (DB-Default = gleiches Literal) | DisplayFilters: `JsonObject` | Lesemodell `DisplayFilters` |
| `display_properties` | `jsonb` | nein | `JsonDefaults.DisplayProperties` (DB-Default = gleiches Literal) | DisplayProperties: `JsonObject` | Lesemodell `DisplayProperties` |
| `rich_filters` | `jsonb` | nein | `'{}'::jsonb` | RichFilters: `JsonObject` | Lesemodell `RichFilterNode` |
| `access` | `smallint` | nein | 1 | Access: `short` | 0 = Private, 1 = Public (**umgekehrt** zu `pages.access`, Q8) |
| `sort_order` | `double precision` | nein | 65535 | SortOrder: `double` | Anlage `max + 10000` je Projekt bzw. Workspace |
| `logo_props` | `jsonb` | nein | `'{}'::jsonb` | LogoProps: `JsonObject` | Lesemodell `LogoProps` |
| `owned_by_id` | `uuid` | nein | – | OwnedById: `Guid` | FK `users` ON DELETE RESTRICT (Original CASCADE); Original `CASCADE` |
| `is_locked` | `boolean` | nein | false | IsLocked: `bool` | 1:1 |
| `archived_at` | `timestamptz` | ja | – | ArchivedAt: `DateTimeOffset?` | 1:1 |
| `teamspace_id` | `uuid` | ja | NULL | `TeamspaceId: Guid?` | B1-Vorhalt, ohne FK, CE `NULL` |

**Indizes/Unique:** `ix_views_workspace_project` (`workspace_id`, `project_id`) WHERE `deleted_at IS NULL` – `project_id IS NULL` = Workspace-View; `ix_views_teamspace_id` (`teamspace_id`) WHERE `teamspace_id IS NOT NULL`; GIN-Trigram `ix_views_name_trgm`.

**Checks:** `ck_views_access` CHECK (`access IN (0,1)`).

**Hinweise:** Tabellenname `views` statt `issue_views` (D03-ADR-02; Alias für D16 §5.4). `query` ist bei jedem Speichern aus `filters` neu berechnet (02b §3.10).

#### 3.4.9 Modul Intake

##### 3.4.9.1 `intakes` ← `Intake` (`M/intake.py` Z. 16–39)

Entität `Intake` · `[OwnedBy("Intake")]` · Basis `ProjectEntity` (Audit-Basis + `workspace_id`, `project_id` NOT NULL; Scope-FK) · ab **I3** · Status **übernommen** · CE-IDs: CE-INT-001, CE-API-025

| Spalte | PostgreSQL | Null | Default | C#-Property: Typ | Herkunft / Regel |
|---|---|---|---|---|---|
| `name` | `varchar(255)` | nein | – | Name: `string` | 1:1 |
| `description` | `text` | nein | – | Description: `string` | 1:1 |
| `is_default` | `boolean` | nein | false | IsDefault: `bool` | 1:1 |
| `view_props` | `jsonb` | nein | `'{}'::jsonb` | ViewProps: `JsonObject` | 1:1 |
| `logo_props` | `jsonb` | nein | `'{}'::jsonb` | LogoProps: `JsonObject` | Lesemodell `LogoProps` |

**Indizes/Unique:** `intake_unique_name_project_when_deleted_at_null` UNIQUE (`name`, `project_id`) WHERE `deleted_at IS NULL`; `ux_intakes_project_default` UNIQUE (`project_id`) WHERE `is_default AND deleted_at IS NULL` (neu).

##### 3.4.9.2 `intake_work_items` ← `IntakeIssue` (`M/intake.py` Z. 54–110)

Entität `IntakeWorkItem` · `[OwnedBy("Intake")]` · Basis `ProjectEntity` (Audit-Basis + `workspace_id`, `project_id` NOT NULL; Scope-FK) · ab **I3** · Status **angepasst** · CE-IDs: CE-INT-002…CE-INT-012, CE-SPACE-006, CE-API-025

| Spalte | PostgreSQL | Null | Default | C#-Property: Typ | Herkunft / Regel |
|---|---|---|---|---|---|
| `intake_id` | `uuid` | nein | – | IntakeId: `Guid` | FK `intakes` ON DELETE CASCADE |
| `work_item_id` | `uuid` | nein | – | WorkItemId: `Guid` | FK `work_items` ON DELETE CASCADE; Original `issue_id` |
| `status` | `integer` | nein | -2 | Status: `int` | -2 Pending, -1 Rejected, 0 Snoozed, 1 Accepted, 2 Duplicate |
| `snoozed_till` | `timestamptz` | ja | – | SnoozedTill: `DateTimeOffset?` | immer 00:00 der Projekt-TZ (02b §3.8) |
| `duplicate_to_id` | `uuid` | ja | – | DuplicateToId: `Guid?` | FK `work_items` ON DELETE SET NULL |
| `source` | `varchar(255)` | ja | `'IN_APP'` | Source: `string?` | `IN_APP` (CE); `FORMS`, `EMAIL` für A15 (V) |
| `source_email` | `text` | ja | – | SourceEmail: `string?` | 1:1 |
| `external_source` | `varchar(255)` | ja | – | ExternalSource: `string?` | 1:1 |
| `external_id` | `varchar(255)` | ja | – | ExternalId: `string?` | 1:1 |
| `extra` | `jsonb` | nein | `'{}'::jsonb` | Extra: `JsonObject` | A15-Metadaten, CE `{}` |

**Indizes/Unique:** `intake_issue_snoozed_till_idx` (`snoozed_till`) WHERE `status = 0`; `ux_intake_work_items_work_item` UNIQUE (`work_item_id`) WHERE `deleted_at IS NULL` (neu; fachlich 1:1, 02b §3.8); `ix_intake_work_items_intake_status` (`intake_id`, `status`) WHERE `deleted_at IS NULL`.

**Checks:** `ck_intake_work_items_status` CHECK (`status IN (-2,-1,0,1,2)`); `ck_intake_work_items_source` CHECK (`source IS NULL OR source IN ('IN_APP','FORMS','EMAIL')`).

#### 3.4.10 Modul Pages

##### 3.4.10.1 `pages` ← `Page` (`M/page.py` Z. 23–77)

Entität `Page` · `[OwnedBy("Pages")]` · Basis eigene Form (Spalten vollständig gelistet) · ab **I4** · Status **angepasst** · CE-IDs: CE-PAGE-001…CE-PAGE-012, CE-PAGE-019, CE-RT-003, CE-RT-005

| Spalte | PostgreSQL | Null | Default | C#-Property: Typ | Herkunft / Regel |
|---|---|---|---|---|---|
| `id, created_at, updated_at, created_by_id, updated_by_id, deleted_at` | wie `AuditableEntity` | – | – | – | Basis `AuditableEntity` + `IWorkspaceScoped` (kein `project_id` – Projektbezug **nur** über `project_pages`, D1) |
| `workspace_id` | `uuid` | nein | – | WorkspaceId: `Guid` | FK `workspaces` ON DELETE CASCADE |
| `name` | `text` | nein | – | Name: `string` | 1:1 |
| `description_json` | `jsonb` | nein | `'{}'::jsonb` | DescriptionJson: `JsonObject` | Lesemodell `ProseMirrorDoc` |
| `description_binary` | `bytea` | ja | – | DescriptionBinary: `byte[]?` | **kanonisch** für Pages: Yjs-Update, Fragmente `default` und `title` (ADR-022) |
| `description_html` | `text` | nein | `'<p></p>'` | DescriptionHtml: `string` | 1:1 |
| `description_stripped` | `text` | ja | – | DescriptionStripped: `string?` | 1:1 |
| `owned_by_id` | `uuid` | nein | – | OwnedById: `Guid` | FK `users` ON DELETE RESTRICT (Original CASCADE); Original `CASCADE` |
| `access` | `smallint` | nein | 0 | Access: `short` | 0 = Public, 1 = Private |
| `color` | `varchar(255)` | nein | `''` | Color: `string` | 1:1 |
| `parent_id` | `uuid` | ja | – | ParentId: `Guid?` | FK `pages` ON DELETE CASCADE; D2-Andockstelle (V/P), CE immer `NULL` |
| `archived_at` | `date` | ja | – | ArchivedAt: `DateOnly?` | `date` wie Original |
| `is_locked` | `boolean` | nein | false | IsLocked: `bool` | 1:1 |
| `view_props` | `jsonb` | nein | `JsonDefaults.PageViewProps` (DB-Default = gleiches Literal) | ViewProps: `JsonObject` | Lesemodell `PageViewProps` |
| `logo_props` | `jsonb` | nein | `'{}'::jsonb` | LogoProps: `JsonObject` | Lesemodell `LogoProps` |
| `is_global` | `boolean` | nein | false | IsGlobal: `bool` | V (D1) |
| `moved_to_page` | `uuid` | ja | – | MovedToPage: `Guid?` | V (D2), ohne FK |
| `moved_to_project` | `uuid` | ja | – | MovedToProject: `Guid?` | V (D2), ohne FK |
| `sort_order` | `double precision` | nein | 65535 | SortOrder: `double` | 1:1 |
| `external_id` | `varchar(255)` | ja | – | ExternalId: `string?` | 1:1 |
| `external_source` | `varchar(255)` | ja | – | ExternalSource: `string?` | 1:1 |
| `teamspace_id` | `uuid` | ja | NULL | `TeamspaceId: Guid?` | B1-Vorhalt, ohne FK, CE `NULL` |

M2M des Originals als explizite Join-Entitäten: `labels` → `page_labels`, `projects` → `project_pages`.

**Indizes/Unique:** `ix_pages_workspace_owned_by` (`workspace_id`, `owned_by_id`) WHERE `deleted_at IS NULL`; `ix_pages_parent_id` (`parent_id`) WHERE `parent_id IS NOT NULL`; `ix_pages_teamspace_id` (`teamspace_id`) WHERE `teamspace_id IS NOT NULL`; GIN-Trigram `ix_pages_name_trgm`.

**Checks:** `ck_pages_access` CHECK (`access IN (0,1)`); `ck_pages_not_own_parent` CHECK (`parent_id IS NULL OR parent_id <> id`); `ck_pages_description_binary_size` CHECK (`description_binary IS NULL OR octet_length(description_binary) <= 10485760`).

**Hinweise:** Entität `Page : AuditableEntity, IWorkspaceScoped` (nicht `WorkspaceEntity`, weil das Original **kein** `project_id` an `pages` hat). Soft-Delete kaskadiert Inline auf `project_pages`, `page_labels`, `page_logs`, `page_versions`, `file_assets(page_id)`; Kind-Pages (`parent_id`) als **Deferred**-Eintrag vorbereitet (D16 §3.3.4 D2).

##### 3.4.10.2 `project_pages` ← `ProjectPage` (`M/page.py` Z. 135–155)

Entität `ProjectPage` · `[OwnedBy("Pages")]` · Basis eigene Form (Spalten vollständig gelistet) · ab **I4** · Status **übernommen** · CE-IDs: CE-PAGE-001, CE-PAGE-003, CE-PAGE-009

| Spalte | PostgreSQL | Null | Default | C#-Property: Typ | Herkunft / Regel |
|---|---|---|---|---|---|
| `id, created_at, updated_at, created_by_id, updated_by_id, deleted_at` | wie `AuditableEntity` | – | – | – | Basis `AuditableEntity` + `IWorkspaceScoped`; Scope-FK (`project_id`, `workspace_id`) → `projects` |
| `project_id` | `uuid` | nein | – | ProjectId: `Guid` | FK `projects` ON DELETE CASCADE |
| `page_id` | `uuid` | nein | – | PageId: `Guid` | FK `pages` ON DELETE CASCADE |
| `workspace_id` | `uuid` | nein | – | WorkspaceId: `Guid` | FK `workspaces` ON DELETE CASCADE |

**Indizes/Unique:** `project_page_unique_project_page_when_deleted_at_null` UNIQUE (`project_id`, `page_id`) WHERE `deleted_at IS NULL`; `ix_project_pages_page_id` (`page_id`).

**Hinweise:** D1-Andockstelle: einzige Projektzuordnung von Pages (01 §1.4).

##### 3.4.10.3 `page_labels` ← `PageLabel` (`M/page.py` Z. 120–132)

Entität `PageLabel` · `[OwnedBy("Pages")]` · Basis eigene Form (Spalten vollständig gelistet) · ab **I4** · Status **übernommen** · CE-IDs: CE-PAGE-004

| Spalte | PostgreSQL | Null | Default | C#-Property: Typ | Herkunft / Regel |
|---|---|---|---|---|---|
| `id, created_at, updated_at, created_by_id, updated_by_id, deleted_at` | wie `AuditableEntity` | – | – | – | Basis `AuditableEntity` + `IWorkspaceScoped` |
| `label_id` | `uuid` | nein | – | LabelId: `Guid` | FK `labels` ON DELETE CASCADE |
| `page_id` | `uuid` | nein | – | PageId: `Guid` | FK `pages` ON DELETE CASCADE |
| `workspace_id` | `uuid` | nein | – | WorkspaceId: `Guid` | FK `workspaces` ON DELETE CASCADE |

**Indizes/Unique:** `ux_page_labels_page_label` UNIQUE (`page_id`, `label_id`) WHERE `deleted_at IS NULL` (neu).

##### 3.4.10.4 `page_logs` ← `PageLog` (`M/page.py` Z. 80–117)

Entität `PageLog` · `[OwnedBy("Pages")]` · Basis eigene Form (Spalten vollständig gelistet) · ab **I4** · Status **korrigiert** · CE-IDs: CE-PAGE-012

| Spalte | PostgreSQL | Null | Default | C#-Property: Typ | Herkunft / Regel |
|---|---|---|---|---|---|
| `id, created_at, updated_at, created_by_id, updated_by_id, deleted_at` | wie `AuditableEntity` | – | – | – | Basis `AuditableEntity` + `IWorkspaceScoped` |
| `transaction` | `uuid` | nein | C#: `Guid.CreateVersion7()` über `IIdGenerator` | Transaction: `Guid` | Komponenten-ID aus HTML (`mention-component`/`image-component`) |
| `page_id` | `uuid` | nein | – | PageId: `Guid` | FK `pages` ON DELETE CASCADE |
| `entity_identifier` | `uuid` | ja | – | EntityIdentifier: `Guid?` | polymorph, kein FK |
| `entity_name` | `varchar(30)` | nein | – | EntityName: `string` | `image`, `user_mention`, … (02b §2.5) |
| `entity_type` | `varchar(30)` | ja | – | EntityType: `string?` | 1:1 |
| `workspace_id` | `uuid` | nein | – | WorkspaceId: `Guid` | FK `workspaces` ON DELETE CASCADE |

**Indizes/Unique:** `ux_page_logs_page_transaction` UNIQUE (`page_id`, `transaction`) WHERE `deleted_at IS NULL` (Original voll eindeutig – Korrektur Q16, DEV-DM-09); `pagelog_entity_type_idx` (`entity_type`); `pagelog_entity_id_idx` (`entity_identifier`); `pagelog_entity_name_idx` (`entity_name`); `pagelog_type_id_idx` (`entity_type`, `entity_identifier`); `pagelog_name_id_idx` (`entity_name`, `entity_identifier`).

**Hinweise:** Löschen verschwundener Komponenten **mit** `page_id`-Filter (Korrektur Q16). `transaction`/`entity_identifier` bleiben `uuid`; Nicht-UUID-Werte werden übersprungen statt den Batch abzubrechen.

##### 3.4.10.5 `page_versions` ← `PageVersion` (`M/page.py` Z. 158–182)

Entität `PageVersion` · `[OwnedBy("Pages")]` · Basis eigene Form (Spalten vollständig gelistet) · ab **I4** · Status **korrigiert** · CE-IDs: CE-PAGE-019

| Spalte | PostgreSQL | Null | Default | C#-Property: Typ | Herkunft / Regel |
|---|---|---|---|---|---|
| `id, created_at, updated_at, created_by_id, updated_by_id, deleted_at` | wie `AuditableEntity` | – | – | – | Basis `AuditableEntity` + `IWorkspaceScoped` |
| `workspace_id` | `uuid` | nein | – | WorkspaceId: `Guid` | FK `workspaces` ON DELETE CASCADE |
| `page_id` | `uuid` | nein | – | PageId: `Guid` | FK `pages` ON DELETE CASCADE |
| `last_saved_at` | `timestamptz` | nein | `now()` | LastSavedAt: `DateTimeOffset` | 1:1 |
| `owned_by_id` | `uuid` | nein | – | OwnedById: `Guid` | FK `users` ON DELETE SET NULL (Original CASCADE); Original `CASCADE` |
| `description_binary` | `bytea` | ja | – | DescriptionBinary: `byte[]?` | 1:1 |
| `description_html` | `text` | nein | `'<p></p>'` | DescriptionHtml: `string` | 1:1 |
| `description_stripped` | `text` | ja | – | DescriptionStripped: `string?` | 1:1 |
| `description_json` | `jsonb` | nein | `'{}'::jsonb` | DescriptionJson: `JsonObject` | Lesemodell `ProseMirrorDoc` |
| `sub_pages_data` | `jsonb` | nein | `'{}'::jsonb` | SubPagesData: `JsonObject` | V, D2; CE `{}` |

**Indizes/Unique:** `ix_page_versions_page_last_saved` (`page_id`, `last_saved_at` DESC).

**Hinweise:** Original erzeugt wegen `page.description` nie Versionen (Q10) – Ziel schreibt sie (`PageVersionRecorder`, 600-s-Merge, Limit 20 je Page als Instanz-Einstellung `Plane:Retention:PageVersions`), DEV-DM-10.

#### 3.4.11 Modul Assets

##### 3.4.11.1 `file_assets` ← `FileAsset` (`M/asset.py` Z. 31–103)

Entität `FileAsset` · `[OwnedBy("Assets")]` · Basis eigene Form (Spalten vollständig gelistet) · ab **I1** · Status **angepasst** · CE-IDs: CE-OPS-012, CE-OPS-013, CE-WI-036, CE-PAGE-018, CE-SPACE-007, CE-API-015, CE-API-016

| Spalte | PostgreSQL | Null | Default | C#-Property: Typ | Herkunft / Regel |
|---|---|---|---|---|---|
| `id, created_at, updated_at, created_by_id, updated_by_id, deleted_at` | wie `AuditableEntity` | – | – | – | Basis `AuditableEntity`; `workspace_id` nullable (Benutzer-Avatare) → kein `IWorkspaceScoped`-Tenant-Filter, eigener Filter im Modul |
| `attributes` | `jsonb` | nein | `'{}'::jsonb` | Attributes: `JsonObject` | Lesemodell `FileAssetAttributes` |
| `asset` | `varchar(800)` | nein | – | Asset: `string` | Objekt-Key (`<workspace_id>/<uuidhex>-<name>` bzw. `user-<uuidhex>-<name>`) |
| `user_id` | `uuid` | ja | – | UserId: `Guid?` | FK `users` ON DELETE CASCADE |
| `workspace_id` | `uuid` | ja | – | WorkspaceId: `Guid?` | FK `workspaces` ON DELETE CASCADE |
| `draft_work_item_id` | `uuid` | ja | – | DraftWorkItemId: `Guid?` | FK `draft_work_items` ON DELETE CASCADE; Original `draft_issue_id` |
| `project_id` | `uuid` | ja | – | ProjectId: `Guid?` | FK `projects` ON DELETE CASCADE |
| `work_item_id` | `uuid` | ja | – | WorkItemId: `Guid?` | FK `work_items` ON DELETE CASCADE; Original `issue_id` |
| `comment_id` | `uuid` | ja | – | CommentId: `Guid?` | FK `work_item_comments` ON DELETE CASCADE |
| `page_id` | `uuid` | ja | – | PageId: `Guid?` | FK `pages` ON DELETE CASCADE |
| `entity_type` | `varchar(255)` | ja | – | EntityType: `string?` | `EntityTypeContext` (10 Werte, 02a §2.4); Pakete ergänzen → kein DB-Check |
| `entity_identifier` | `varchar(255)` | ja | – | EntityIdentifier: `string?` | 1:1 |
| `is_deleted` | `boolean` | nein | false | IsDeleted: `bool` | Vertragsfeld (Original), unabhängig von `deleted_at` |
| `is_archived` | `boolean` | nein | false | IsArchived: `bool` | 1:1 |
| `external_id` | `varchar(255)` | ja | – | ExternalId: `string?` | 1:1 |
| `external_source` | `varchar(255)` | ja | – | ExternalSource: `string?` | 1:1 |
| `size` | `double precision` | nein | 0 | Size: `double` | Bytes als Float (Vertrag), begrenzt auf `FILE_SIZE_LIMIT` |
| `is_uploaded` | `boolean` | nein | false | IsUploaded: `bool` | 1:1 |
| `storage_metadata` | `jsonb` | ja | `'{}'::jsonb` | StorageMetadata: `JsonObject?` | Lesemodell `StorageMetadata` |

**Indizes/Unique:** `asset_entity_type_idx` (`entity_type`); `asset_entity_identifier_idx` (`entity_identifier`); `asset_entity_idx` (`entity_type`, `entity_identifier`); `asset_asset_idx` (`asset`); `ix_file_assets_unuploaded` (`created_at`) WHERE `NOT is_uploaded AND deleted_at IS NULL` – Bereinigungs-Job; `ix_file_assets_work_item` (`work_item_id`) WHERE `work_item_id IS NOT NULL`; `ix_file_assets_page` (`page_id`) WHERE `page_id IS NOT NULL`.

**Hinweise:** Hard-Delete löscht zusätzlich das Objekt im Speicher (`IObjectStorage`, Verbesserung 02a §5.2) über `FileAssetPurgeConsumer`.

#### 3.4.12 Modul Home

##### 3.4.12.1 `workspace_home_preferences` ← `WorkspaceHomePreference` (`M/workspace.py` Z. 374–414)

Entität `WorkspaceHomePreference` · `[OwnedBy("Home")]` · Basis `AuditableEntity` (`id`, `created_at`, `updated_at`, `created_by_id`, `updated_by_id`, `deleted_at`) · ab **I5** · Status **übernommen** · CE-IDs: CE-HOME-001, CE-HOME-002

| Spalte | PostgreSQL | Null | Default | C#-Property: Typ | Herkunft / Regel |
|---|---|---|---|---|---|
| `workspace_id` | `uuid` | nein | – | WorkspaceId: `Guid` | FK `workspaces` ON DELETE CASCADE |
| `user_id` | `uuid` | nein | – | UserId: `Guid` | FK `users` ON DELETE CASCADE |
| `key` | `varchar(255)` | nein | – | Key: `string` | `quick_links`, `recents`, `my_stickies`, `new_at_plane`, `quick_tutorial` |
| `is_enabled` | `boolean` | nein | true | IsEnabled: `bool` | 1:1 |
| `config` | `jsonb` | nein | `'{}'::jsonb` | Config: `JsonObject` | 1:1 |
| `sort_order` | `double precision` | nein | 65535 | SortOrder: `double` | 1:1 |

**Indizes/Unique:** `workspace_user_home_preferences_unique_workspace_user_key_when_deleted_at_null` UNIQUE (`workspace_id`, `user_id`, `key`) WHERE `deleted_at IS NULL`.

##### 3.4.12.2 `workspace_user_links` ← `WorkspaceUserLink` (`M/workspace.py` Z. 354–371)

Entität `WorkspaceUserLink` · `[OwnedBy("Home")]` · Basis `WorkspaceEntity` (Audit-Basis + `workspace_id` NOT NULL, `project_id` NULL) · ab **I5** · Status **übernommen** · CE-IDs: CE-HOME-004

| Spalte | PostgreSQL | Null | Default | C#-Property: Typ | Herkunft / Regel |
|---|---|---|---|---|---|
| `title` | `varchar(255)` | ja | – | Title: `string?` | 1:1 |
| `url` | `text` | nein | – | Url: `string` | 1:1 |
| `metadata` | `jsonb` | nein | `'{}'::jsonb` | Metadata: `JsonObject` | 1:1 |
| `owner_id` | `uuid` | nein | – | OwnerId: `Guid` | FK `users` ON DELETE CASCADE |

**Indizes/Unique:** `ix_workspace_user_links_workspace_owner` (`workspace_id`, `owner_id`) WHERE `deleted_at IS NULL`.

##### 3.4.12.3 `user_recent_visits` ← `UserRecentVisit` (`M/recent_visit.py` Z. 22–39)

Entität `UserRecentVisit` · `[OwnedBy("Home")]` · Basis `WorkspaceEntity` (Audit-Basis + `workspace_id` NOT NULL, `project_id` NULL) · ab **I5** · Status **angepasst** · CE-IDs: CE-HOME-005

| Spalte | PostgreSQL | Null | Default | C#-Property: Typ | Herkunft / Regel |
|---|---|---|---|---|---|
| `entity_identifier` | `uuid` | ja | – | EntityIdentifier: `Guid?` | polymorph, kein FK |
| `entity_name` | `varchar(30)` | nein | – | EntityName: `string` | kleingeschrieben: `project`, `issue`, `page`, `view`, `cycle`, `module` |
| `user_id` | `uuid` | nein | – | UserId: `Guid` | FK `users` ON DELETE CASCADE |
| `visited_at` | `timestamptz` | nein | – | VisitedAt: `DateTimeOffset` | beim Upsert gesetzt |

**Indizes/Unique:** `ux_user_recent_visits_user_entity` UNIQUE (`workspace_id`, `user_id`, `entity_name`, `entity_identifier`) WHERE `deleted_at IS NULL` (neu: Upsert statt Duplikate); `ix_user_recent_visits_user_visited` (`user_id`, `visited_at` DESC).

**Hinweise:** Original lässt `created_by` immer `NULL` (02a §3.22 #9) – Ziel setzt den Akteur (ohne Vertragswirkung). Hartes Löschen über `IHardDelete` (D02-ADR-03).

##### 3.4.12.4 `stickies` ← `Sticky` (`M/sticky.py` Z. 16–57)

Entität `Sticky` · `[OwnedBy("Home")]` · Basis eigene Form (Spalten vollständig gelistet) · ab **I5** · Status **übernommen** · CE-IDs: CE-HOME-008…CE-HOME-010, CE-API-014

| Spalte | PostgreSQL | Null | Default | C#-Property: Typ | Herkunft / Regel |
|---|---|---|---|---|---|
| `id, created_at, updated_at, created_by_id, updated_by_id, deleted_at` | wie `AuditableEntity` | – | – | – | Basis `AuditableEntity` + `IWorkspaceScoped` |
| `name` | `text` | ja | – | Name: `string?` | 1:1 |
| `description` | `jsonb` | nein | `'{}'::jsonb` | Description: `JsonObject` | Lesemodell `ProseMirrorDoc` |
| `description_html` | `text` | nein | `'<p></p>'` | DescriptionHtml: `string` | 1:1 |
| `description_stripped` | `text` | ja | – | DescriptionStripped: `string?` | 1:1 |
| `description_binary` | `bytea` | ja | – | DescriptionBinary: `byte[]?` | 1:1 |
| `logo_props` | `jsonb` | nein | `'{}'::jsonb` | LogoProps: `JsonObject` | Lesemodell `LogoProps` |
| `color` | `varchar(255)` | ja | – | Color: `string?` | 1:1 |
| `background_color` | `varchar(255)` | ja | – | BackgroundColor: `string?` | 1:1 |
| `workspace_id` | `uuid` | nein | – | WorkspaceId: `Guid` | FK `workspaces` ON DELETE CASCADE |
| `owner_id` | `uuid` | nein | – | OwnerId: `Guid` | FK `users` ON DELETE CASCADE |
| `sort_order` | `double precision` | nein | 65535 | SortOrder: `double` | Anlage `max + 10000` (02a §3.6) |

**Indizes/Unique:** `ix_stickies_workspace_owner` (`workspace_id`, `owner_id`) WHERE `deleted_at IS NULL`; GIN-Trigram `ix_stickies_description_stripped_trgm` (`description_stripped__icontains`).

#### 3.4.13 Modul Analytics

##### 3.4.13.1 `analytic_views` ← `AnalyticView` (`M/analytic.py` Z. 11–26)

Entität `AnalyticView` · `[OwnedBy("Analytics")]` · Basis eigene Form (Spalten vollständig gelistet) · ab **I5** · Status **angepasst** · CE-IDs: CE-ANA-009

| Spalte | PostgreSQL | Null | Default | C#-Property: Typ | Herkunft / Regel |
|---|---|---|---|---|---|
| `id, created_at, updated_at, created_by_id, updated_by_id, deleted_at` | wie `AuditableEntity` | – | – | – | Basis `AuditableEntity` + `IWorkspaceScoped` |
| `workspace_id` | `uuid` | nein | – | WorkspaceId: `Guid` | FK `workspaces` ON DELETE CASCADE |
| `name` | `varchar(255)` | nein | – | Name: `string` | 1:1 |
| `description` | `text` | nein | – | Description: `string` | 1:1 |
| `query` | `jsonb` | nein | – | Query: `JsonObject` | Legacy, Ziel speichert nur noch, Abruf nutzt `query_dict` |
| `query_dict` | `jsonb` | nein | `'{}'::jsonb` | QueryDict: `JsonObject` | Lesemodell `AnalyticQuery` |

#### 3.4.14 Modul Notifications

##### 3.4.14.1 `notifications` ← `Notification` (`M/notification.py` Z. 13–69)

Entität `Notification` · `[OwnedBy("Notifications")]` · Basis eigene Form (Spalten vollständig gelistet) · ab **I5** · Status **übernommen** · CE-IDs: CE-NOTIF-001…CE-NOTIF-007, CE-INT-012

| Spalte | PostgreSQL | Null | Default | C#-Property: Typ | Herkunft / Regel |
|---|---|---|---|---|---|
| `id, created_at, updated_at, created_by_id, updated_by_id, deleted_at` | wie `AuditableEntity` | – | – | – | Basis `AuditableEntity` + `IWorkspaceScoped` |
| `workspace_id` | `uuid` | nein | – | WorkspaceId: `Guid` | FK `workspaces` ON DELETE CASCADE |
| `project_id` | `uuid` | ja | – | ProjectId: `Guid?` | FK `projects` ON DELETE CASCADE |
| `data` | `jsonb` | ja | – | Data: `JsonObject?` | Lesemodell `NotificationData` |
| `entity_identifier` | `uuid` | ja | – | EntityIdentifier: `Guid?` | 1:1 |
| `entity_name` | `varchar(255)` | nein | – | EntityName: `string` | CE: `issue` |
| `title` | `text` | nein | – | Title: `string` | 1:1 |
| `message` | `jsonb` | ja | – | Message: `JsonNode?` | Original speichert einen JSON-**String** |
| `message_html` | `text` | nein | `'<p></p>'` | MessageHtml: `string` | 1:1 |
| `message_stripped` | `text` | ja | – | MessageStripped: `string?` | 1:1 |
| `sender` | `varchar(255)` | nein | – | Sender: `string` | `in_app:issue_activities:created\|assigned\|subscribed\|mentioned` |
| `triggered_by_id` | `uuid` | ja | – | TriggeredById: `Guid?` | FK `users` ON DELETE SET NULL |
| `receiver_id` | `uuid` | nein | – | ReceiverId: `Guid` | FK `users` ON DELETE CASCADE |
| `read_at` | `timestamptz` | ja | – | ReadAt: `DateTimeOffset?` | 1:1 |
| `snoozed_till` | `timestamptz` | ja | – | SnoozedTill: `DateTimeOffset?` | 1:1 |
| `archived_at` | `timestamptz` | ja | – | ArchivedAt: `DateTimeOffset?` | 1:1 |

**Indizes/Unique:** `notif_entity_identifier_idx` (`entity_identifier`); `notif_entity_name_idx` (`entity_name`); `notif_read_at_idx` (`read_at`); `notif_entity_idx` (`receiver_id`, `read_at`); `notif_receiver_status_idx` (`receiver_id`, `workspace_id`, `read_at`, `created_at`); `notif_receiver_entity_idx` (`receiver_id`, `workspace_id`, `entity_name`, `read_at`); `notif_receiver_state_idx` (`receiver_id`, `workspace_id`, `snoozed_till`, `archived_at`); `notif_receiver_sender_idx` (`receiver_id`, `workspace_id`, `sender`); `notif_entity_lookup_idx` (`workspace_id`, `entity_identifier`, `entity_name`).

##### 3.4.14.2 `user_notification_preferences` ← `UserNotificationPreference` (`M/notification.py` Z. 81–118)

Entität `UserNotificationPreference` · `[OwnedBy("Notifications")]` · Basis `AuditableEntity` (`id`, `created_at`, `updated_at`, `created_by_id`, `updated_by_id`, `deleted_at`) · ab **I1** · Status **angepasst** · CE-IDs: CE-NOTIF-008, CE-NOTIF-009

| Spalte | PostgreSQL | Null | Default | C#-Property: Typ | Herkunft / Regel |
|---|---|---|---|---|---|
| `user_id` | `uuid` | nein | – | UserId: `Guid` | FK `users` ON DELETE CASCADE |
| `workspace_id` | `uuid` | ja | – | WorkspaceId: `Guid?` | FK `workspaces` ON DELETE CASCADE; CE immer `NULL` (globale Zeile) |
| `project_id` | `uuid` | ja | – | ProjectId: `Guid?` | FK `projects` ON DELETE CASCADE; CE immer `NULL` |
| `property_change` | `boolean` | nein | true | PropertyChange: `bool` | 1:1 |
| `state_change` | `boolean` | nein | true | StateChange: `bool` | 1:1 |
| `comment` | `boolean` | nein | true | Comment: `bool` | 1:1 |
| `mention` | `boolean` | nein | true | Mention: `bool` | 1:1 |
| `issue_completed` | `boolean` | nein | true | IssueCompleted: `bool` | 1:1 |

**Indizes/Unique:** `ux_user_notification_preferences_global` UNIQUE (`user_id`) WHERE `workspace_id IS NULL AND project_id IS NULL AND deleted_at IS NULL` (neu, Q20).

**Hinweise:** Wird bei der JIT-Anlage eines Benutzers angelegt (`CreateUserStep`, Ersatz für das `post_save`-Signal, 02a §3.8).

##### 3.4.14.3 `email_notification_logs` ← `EmailNotificationLog` (`M/notification.py` Z. 121–149)

Entität `EmailNotificationLog` · `[OwnedBy("Notifications")]` · Basis `AuditableEntity` (`id`, `created_at`, `updated_at`, `created_by_id`, `updated_by_id`, `deleted_at`) · ab **I5** · Status **übernommen** · CE-IDs: CE-NOTIF-008, CE-OPS-015

| Spalte | PostgreSQL | Null | Default | C#-Property: Typ | Herkunft / Regel |
|---|---|---|---|---|---|
| `receiver_id` | `uuid` | nein | – | ReceiverId: `Guid` | FK `users` ON DELETE CASCADE |
| `triggered_by_id` | `uuid` | nein | – | TriggeredById: `Guid` | FK `users` ON DELETE CASCADE |
| `entity_identifier` | `uuid` | ja | – | EntityIdentifier: `Guid?` | 1:1 |
| `entity_name` | `varchar(255)` | nein | – | EntityName: `string` | 1:1 |
| `data` | `jsonb` | ja | – | Data: `JsonObject?` | Lesemodell `EmailNotificationData` |
| `processed_at` | `timestamptz` | ja | – | ProcessedAt: `DateTimeOffset?` | 1:1 |
| `sent_at` | `timestamptz` | ja | – | SentAt: `DateTimeOffset?` | 1:1 |
| `entity` | `varchar(200)` | nein | – | Entity: `string` | 1:1 |
| `old_value` | `varchar(300)` | ja | – | OldValue: `string?` | 1:1 |
| `new_value` | `varchar(300)` | ja | – | NewValue: `string?` | 1:1 |

**Indizes/Unique:** `ix_email_notification_logs_unprocessed` (`receiver_id`, `created_at`) WHERE `processed_at IS NULL` – 5-Minuten-Bündelung; `ix_email_notification_logs_sent_at` (`sent_at`) – Aufbewahrung 7 Tage.

#### 3.4.15 Modul PublicSpace

##### 3.4.15.1 `deploy_boards` ← `DeployBoard` (`M/deploy_board.py` Z. 19–57)

Entität `DeployBoard` · `[OwnedBy("PublicSpace")]` · Basis `WorkspaceEntity` (Audit-Basis + `workspace_id` NOT NULL, `project_id` NULL) · ab **I6** · Status **übernommen** · CE-IDs: CE-SPACE-001…CE-SPACE-005, CE-SPACE-017

| Spalte | PostgreSQL | Null | Default | C#-Property: Typ | Herkunft / Regel |
|---|---|---|---|---|---|
| `entity_identifier` | `uuid` | ja | – | EntityIdentifier: `Guid?` | polymorph (CE: Projekt-ID), kein FK |
| `entity_name` | `varchar(30)` | ja | – | EntityName: `string?` | `project`, `issue`, `module`, `cycle`, `page`, `view`, `intake` (V, D16) |
| `anchor` | `varchar(255)` | nein | C#: `AnchorGenerator.Create()` (32 Hex) | Anchor: `string` | `uuid4().hex` (32 Hex), global eindeutig (auch gelöschte, wie Original) |
| `is_comments_enabled` | `boolean` | nein | false | IsCommentsEnabled: `bool` | 1:1 |
| `is_reactions_enabled` | `boolean` | nein | false | IsReactionsEnabled: `bool` | 1:1 |
| `intake_id` | `uuid` | ja | – | IntakeId: `Guid?` | FK `intakes` ON DELETE SET NULL |
| `is_votes_enabled` | `boolean` | nein | false | IsVotesEnabled: `bool` | 1:1 |
| `view_props` | `jsonb` | nein | `'{}'::jsonb` | ViewProps: `JsonObject` | Lesemodell `PublishViewProps` |
| `is_activity_enabled` | `boolean` | nein | true | IsActivityEnabled: `bool` | 1:1 |
| `is_disabled` | `boolean` | nein | false | IsDisabled: `bool` | 1:1 |

**Indizes/Unique:** `ux_deploy_boards_anchor` UNIQUE (`anchor`); `deploy_board_unique_entity_name_entity_identifier_when_deleted_at_null` UNIQUE (`entity_name`, `entity_identifier`) WHERE `deleted_at IS NULL`.

**Checks:** `ck_deploy_boards_entity_name` CHECK (`entity_name IS NULL OR entity_name IN ('project','issue','module','cycle','page','view','intake')`).

##### 3.4.15.2 `project_public_members` ← `ProjectPublicMember` (`M/project.py` Z. 370–389)

Entität `ProjectPublicMember` · `[OwnedBy("PublicSpace")]` · Basis `ProjectEntity` (Audit-Basis + `workspace_id`, `project_id` NOT NULL; Scope-FK) · ab **I6** · Status **übernommen** · CE-IDs: CE-SPACE-025, CE-SPACE-026, CE-SPACE-027, CE-SPACE-028

| Spalte | PostgreSQL | Null | Default | C#-Property: Typ | Herkunft / Regel |
|---|---|---|---|---|---|
| `member_id` | `uuid` | nein | – | MemberId: `Guid` | FK `users` ON DELETE CASCADE |

**Indizes/Unique:** `project_public_member_unique_project_member_when_deleted_at_null` UNIQUE (`project_id`, `member_id`) WHERE `deleted_at IS NULL`.

**Hinweise:** Tracking-Tabelle: Space-Kommentare/-Reaktionen/-Votes eines Nicht-Mitglieds legen idempotent eine Zeile an (`space/views/issue.py` Z. 327 ff.).

#### 3.4.16 Modul Webhooks

##### 3.4.16.1 `webhooks` ← `Webhook` (`M/webhook.py` Z. 34–62)

Entität `Webhook` · `[OwnedBy("Webhooks")]` · Basis eigene Form (Spalten vollständig gelistet) · ab **I6** · Status **angepasst** · CE-IDs: CE-WH-001…CE-WH-006, CE-WH-009, CE-WH-011

| Spalte | PostgreSQL | Null | Default | C#-Property: Typ | Herkunft / Regel |
|---|---|---|---|---|---|
| `id, created_at, updated_at, created_by_id, updated_by_id, deleted_at` | wie `AuditableEntity` | – | – | – | Basis `AuditableEntity` + `IWorkspaceScoped` |
| `workspace_id` | `uuid` | nein | – | WorkspaceId: `Guid` | FK `workspaces` ON DELETE CASCADE |
| `url` | `varchar(1024)` | nein | – | Url: `string` | SSRF-Prüfung beim Speichern (D05) |
| `is_active` | `boolean` | nein | true | IsActive: `bool` | 1:1 |
| ~~`secret_key`~~ | – | – | – | – | entfällt: ersetzt durch `secret_key_protected` (DP-Zweck `Plane.Webhooks.Secret.v1`, D05 §3.17.5) |
| `project` | `boolean` | nein | false | Project: `bool` | Event-Flag (bool), **kein** FK – Spaltenname wie Original |
| `issue` | `boolean` | nein | false | Issue: `bool` | Event-Flag |
| `module` | `boolean` | nein | false | Module: `bool` | Event-Flag |
| `cycle` | `boolean` | nein | false | Cycle: `bool` | Event-Flag |
| `issue_comment` | `boolean` | nein | false | IssueComment: `bool` | Event-Flag |
| `is_internal` | `boolean` | nein | false | IsInternal: `bool` | 1:1 |
| `version` | `varchar(50)` | nein | `'v1'` | Version: `string` | 1:1 |
| `secret_key_protected` | `bytea` | nein | – | `SecretKeyProtected: byte[]` | DP-geschütztes `plane_wh_<32hex>`; Klartext nur bei Anlage/Regenerierung |

**Indizes/Unique:** `webhook_url_unique_url_when_deleted_at_null` UNIQUE (`workspace_id`, `url`) WHERE `deleted_at IS NULL`.

**Hinweise:** Die Bool-Spalte `project` kollidiert namentlich mit der Konvention `<ziel>_id` nicht (kein `_id`-Suffix); C#-Property `ProjectEvents` mit `HasColumnName("project")`, analog `IssueEvents`, `ModuleEvents`, `CycleEvents`, `IssueCommentEvents`.

##### 3.4.16.2 `webhook_logs` ← `WebhookLog` (`M/webhook.py` Z. 65–91)

Entität `WebhookLog` · `[OwnedBy("Webhooks")]` · Basis eigene Form (Spalten vollständig gelistet) · ab **I6** · Status **übernommen** · CE-IDs: CE-WH-007, CE-WH-010, CE-OPS-015

| Spalte | PostgreSQL | Null | Default | C#-Property: Typ | Herkunft / Regel |
|---|---|---|---|---|---|
| `id, created_at, updated_at, created_by_id, updated_by_id, deleted_at` | wie `AuditableEntity` | – | – | – | Basis `AuditableEntity` + `IWorkspaceScoped` |
| `workspace_id` | `uuid` | nein | – | WorkspaceId: `Guid` | FK `workspaces` ON DELETE CASCADE |
| `webhook_id` | `uuid` | nein | – | WebhookId: `Guid` | bewusst **ohne** FK (Logs überleben gelöschte Webhooks, 02a §3.22 #7); Original `webhook` |
| `event_type` | `varchar(255)` | ja | – | EventType: `string?` | 1:1 |
| `request_method` | `varchar(10)` | ja | – | RequestMethod: `string?` | 1:1 |
| `request_headers` | `text` | ja | – | RequestHeaders: `string?` | 1:1 |
| `request_body` | `text` | ja | – | RequestBody: `string?` | 1:1 |
| `response_status` | `text` | ja | – | ResponseStatus: `string?` | 1:1 |
| `response_headers` | `text` | ja | – | ResponseHeaders: `string?` | 1:1 |
| `response_body` | `text` | ja | – | ResponseBody: `string?` | 1:1 |
| `retry_count` | `smallint` | nein | 0 | RetryCount: `short` | 1:1 |

**Indizes/Unique:** `ix_webhook_logs_webhook_created` (`webhook_id`, `created_at` DESC); `ix_webhook_logs_created_at` (`created_at`) – Aufbewahrung 14 Tage.

#### 3.4.17 Modul Exports

##### 3.4.17.1 `exports` ← `ExporterHistory` (`M/exporter.py` Z. 24–67)

Entität `ExportJob` · `[OwnedBy("Exports")]` · Basis eigene Form (Spalten vollständig gelistet) · ab **I6** · Status **angepasst** · CE-IDs: CE-EXP-001, CE-EXP-002

| Spalte | PostgreSQL | Null | Default | C#-Property: Typ | Herkunft / Regel |
|---|---|---|---|---|---|
| `id, created_at, updated_at, created_by_id, updated_by_id, deleted_at` | wie `AuditableEntity` | – | – | – | Basis `AuditableEntity` + `IWorkspaceScoped` |
| `name` | `varchar(255)` | ja | – | Name: `string?` | 1:1 |
| `type` | `varchar(50)` | nein | `'issue_exports'` | Type: `string` | `issue_exports`; `issue_worklogs` über `IExportTypeProvider` (E-16) – kein DB-Check |
| `workspace_id` | `uuid` | nein | – | WorkspaceId: `Guid` | FK `workspaces` ON DELETE CASCADE |
| `project` | `uuid[]` | ja | – | Project: `List<Guid>?` | Liste von Projekt-IDs (Spaltenname wie Original, Vertrag) |
| `provider` | `varchar(50)` | nein | – | Provider: `string` | `json`, `csv`, `xlsx` |
| `status` | `varchar(50)` | nein | `'queued'` | Status: `string` | `queued`, `processing`, `completed`, `failed` |
| `reason` | `text` | nein | – | Reason: `string` | 1:1 |
| `key` | `text` | nein | – | Key: `string` | 1:1 |
| `url` | `varchar(800)` | ja | – | Url: `string?` | 1:1 |
| `token` | `varchar(255)` | nein | C#: `TokenGenerator.Create(prefix)` | Token: `string` | `uuid4().hex`-artiger Download-Token, unique |
| `initiated_by_id` | `uuid` | nein | – | InitiatedById: `Guid` | FK `users` ON DELETE CASCADE |
| `filters` | `jsonb` | ja | – | Filters: `JsonObject?` | CE ungenutzt |
| `rich_filters` | `jsonb` | ja | `'{}'::jsonb` | RichFilters: `JsonObject?` | Lesemodell `RichFilterNode` |

**Indizes/Unique:** `ux_exports_token` UNIQUE (`token`); `ix_exports_workspace_created` (`workspace_id`, `created_at` DESC); `ix_exports_expiry` (`created_at`) WHERE `url IS NOT NULL` – Ablauf-Job 8 Tage.

**Checks:** `ck_exports_provider` CHECK (`provider IN ('json','csv','xlsx')`); `ck_exports_status` CHECK (`status IN ('queued','processing','completed','failed')`).

**Hinweise:** Tabelle `exports` statt `exporters` (D03-ADR-02).

#### 3.4.18 Neue Tabellen ohne Original-Modell

##### 3.4.18.1 `user_identities` (Eigentümer `Identity`, ab I0, D05 §3.7.1)

| Spalte | PostgreSQL | Null | Default | C#-Property: Typ | Regel |
|---|---|---|---|---|---|
| `id` | `uuid` | nein | – (App: UUIDv7) | Id: `Guid` | PK |
| `user_id` | `uuid` | nein | – | UserId: `Guid` | FK `users` ON DELETE CASCADE |
| `provider` | `varchar(32)` | nein | `'keycloak'` | Provider: `string` | einziger CE-Wert `keycloak` |
| `issuer` | `varchar(512)` | nein | – | Issuer: `string` | Claim `iss` |
| `subject` | `varchar(255)` | nein | – | Subject: `string` | Claim `sub` (feste Verknüpfung, ADR-008) |
| `email_at_link` | `varchar(255)` | nein | – | EmailAtLink: `string` | E-Mail zum Verknüpfungszeitpunkt |
| `created_at` | `timestamptz` | nein | – | CreatedAt: `DateTimeOffset` | `ITimestamped` |
| `updated_at` | `timestamptz` | nein | – | UpdatedAt: `DateTimeOffset` | `ITimestamped` |
| `last_login_at` | `timestamptz` | ja | – | LastLoginAt: `DateTimeOffset?` | je Login gesetzt |

**Indizes/Unique:** `ux_user_identities_issuer_subject` UNIQUE (`issuer`, `subject`); `ux_user_identities_user_provider` UNIQUE (`user_id`, `provider`). Kein Soft-Delete (Historie bleibt bei Keycloak-Löschung, D05 §3.18).

##### 3.4.18.2 `roles` und `role_permissions` (Eigentümer `Authorization`, ab I0, D05 §3.13.3, Andockstelle E5)

| Spalte (`roles`) | PostgreSQL | Null | Default | C#-Property: Typ | Regel |
|---|---|---|---|---|---|
| `id` | `uuid` | nein | – | Id: `Guid` | System-Rollen: feste UUIDv7-Konstanten `SystemRoles.*` |
| `workspace_id` | `uuid` | ja | NULL | WorkspaceId: `Guid?` | FK `workspaces` ON DELETE CASCADE; `NULL` = System-Rolle |
| `namespace` | `varchar(20)` | nein | – | Namespace: `RoleNamespace` | `workspace` \| `project` \| `instance`; reserviert `teamspace` (B1, D05 §6.1) |
| `slug` | `varchar(64)` | nein | – | Slug: `string` | `admin`, `member`, `guest` |
| `name` | `varchar(255)` | nein | – | Name: `string` | Anzeigename |
| `level` | `smallint` | nein | – | Level: `short` | 20/15/5 (API-Feld `role`, ABG-038) |
| `is_system` | `boolean` | nein | `false` | IsSystem: `bool` | System-Rollen `true` |
| `sort_order` | `double precision` | nein | `65535` | SortOrder: `double` | – |
| `created_at`, `updated_at`, `created_by_id`, `updated_by_id`, `deleted_at` | wie A | | | | Basis `AuditableEntity` |

**Indizes/Unique:** `ux_roles_system_namespace_slug` UNIQUE (`namespace`, `slug`) WHERE `workspace_id IS NULL AND deleted_at IS NULL`; `ux_roles_workspace_namespace_slug` UNIQUE (`workspace_id`, `namespace`, `slug`) WHERE `workspace_id IS NOT NULL AND deleted_at IS NULL`. **Checks:** `ck_roles_namespace` CHECK (`namespace IN ('workspace','project','instance','teamspace')`); `ck_roles_level` CHECK (`level BETWEEN 0 AND 100`).

| Spalte (`role_permissions`) | PostgreSQL | Null | Default | C#-Property: Typ | Regel |
|---|---|---|---|---|---|
| `role_id` | `uuid` | nein | – | RoleId: `Guid` | PK-Teil; FK `roles` ON DELETE CASCADE |
| `permission_key` | `varchar(128)` | nein | – | PermissionKey: `string` | PK-Teil; Schlüssel aus dem Permission-Katalog (`<ebene>.<ressource>.<aktion>`) |
| `created_at` | `timestamptz` | nein | – | CreatedAt: `DateTimeOffset` | – |

PK `pk_role_permissions` (`role_id`, `permission_key`). In der CE **leer**: Grants der System-Rollen entstehen aus dem Code (`SystemRoleGrants.g.cs`, D05 §3.13.3).

##### 3.4.18.3 `data_protection_keys` (Eigentümer `Instance`, ab I0, D05-ADR-25)

Entität `Microsoft.AspNetCore.DataProtection.EntityFrameworkCore.DataProtectionKey`, `PlaneDbContext : IDataProtectionKeyContext`. Spalten nach Snake-Case-Konvention: `id integer GENERATED BY DEFAULT AS IDENTITY` (PK), `friendly_name text NULL`, `xml text NULL`. Kein `[OwnedBy]`-Attribut möglich (Fremdtyp) → Eintrag in `OwnershipRegistry.External["data_protection_keys"] = "Instance"`; geschrieben nur vom Data-Protection-Framework. Referenztabelle für `TablesToIgnore`.

##### 3.4.18.4 `workspace_feature_settings` / `project_feature_settings` (Eigentümer `Workspaces` / `Projects`, ab I1, D16 E-01)

| Spalte | PostgreSQL | Null | Default | C#-Property: Typ | Regel |
|---|---|---|---|---|---|
| `workspace_id` bzw. `project_id` | `uuid` | nein | – | WorkspaceId/ProjectId: `Guid` | PK-Teil; FK `workspaces` bzw. `projects` ON DELETE CASCADE |
| `key` | `varchar(64)` | nein | – | Key: `string` | PK-Teil; Katalogschlüssel (`IProjectFeatureCatalog`/`IWorkspaceFeatureCatalog`) |
| `enabled` | `boolean` | nein | `false` | Enabled: `bool` | – |
| `config` | `jsonb` | nein | `'{}'::jsonb` | Config: `JsonObject` | paketspezifisch |
| `updated_at` | `timestamptz` | nein | – | UpdatedAt: `DateTimeOffset` | – |
| `updated_by_id` | `uuid` | ja | – | UpdatedById: `Guid?` | FK `users` ON DELETE SET NULL |

Form exakt nach D16 §5.1 (SQL-Skizze). In der CE leer; die fünf CE-Toggles bleiben Spalten an `projects` (`cycle_view`, `module_view`, `issue_views_view`, `page_view`, `intake_view`), ebenso die V-Spalten `is_issue_type_enabled`, `is_time_tracking_enabled`.

##### 3.4.18.5 `work_item_relation_types` (Eigentümer `WorkItems`, ab I2, Andockstelle A9)

| Spalte | PostgreSQL | Null | Default | C#-Property: Typ | Regel |
|---|---|---|---|---|---|
| `key` | `varchar(30)` | nein | – | Key: `string` | PK (z. B. `blocked_by`) |
| `reverse_key` | `varchar(30)` | nein | – | ReverseKey: `string` | FK `work_item_relation_types(key)` DEFERRABLE INITIALLY DEFERRED (Paare werden zusammen eingefügt); symmetrisch = `key` |
| `workspace_id` | `uuid` | ja | NULL | WorkspaceId: `Guid?` | FK `workspaces` ON DELETE CASCADE; `NULL` = System (A9: workspace-eigene Typen) |
| `is_system` | `boolean` | nein | `false` | IsSystem: `bool` | Seeds `true` |
| `category` | `smallint` | nein | `0` | Category: `RelationCategory` | 0 Relation, 1 Dependency, 2 Implementation |
| `label` | `varchar(100)` | nein | – | Label: `string` | Original-Label |
| `sort_order` | `integer` | nein | – | SortOrder: `int` | Anzeige |

**Checks:** `ck_work_item_relation_types_category` CHECK (`category IN (0,1,2)`). Kein Soft-Delete, keine Audit-Benutzer (Referenzkatalog, `TablesToIgnore`). Seed-Werte §3.14.1 (10 Zeilen, D16 §5.3). `work_item_relations.relation_type` referenziert `key` mit `ON DELETE RESTRICT`. Ein Paket-Typ mit gleichem `key` in einem Workspace ist durch den PK ausgeschlossen; Paket A9 erweitert den PK bei Bedarf additiv um eine Surrogat-ID (Expand/Contract, Fachdesign W2).

##### 3.4.18.6 `outbox_messages`, `inbox_messages`, `jobs`, `recurring_jobs` (Eigentümer `Messaging`, ab I0, ADR-020)

`outbox_messages` (Spaltenliste verbindlich nach ABG-053 / D02 §3.2.2 Nr. 5):

| Spalte | PostgreSQL | Null | Default | C#-Property: Typ | Regel |
|---|---|---|---|---|---|
| `id` | `uuid` | nein | – | Id: `Guid` | PK = `EventContext.MessageId` (UUIDv7 → Reihenfolge) |
| `event_type` | `varchar(200)` | nein | – | EventType: `string` | `plane.<aggregat>.<ereignis>.v<n>` |
| `payload` | `jsonb` | nein | – | Payload: `JsonObject` | serialisiertes Integration-Event (`PlaneJsonContext`) |
| `occurred_at` | `timestamptz` | nein | – | OccurredAt: `DateTimeOffset` | `IClock` beim `SaveChanges` |
| `traceparent` | `varchar(55)` | ja | – | TraceParent: `string?` | W3C Trace Context |
| `actor_id` | `uuid` | ja | – | ActorId: `Guid?` | aus `ICurrentActor` (ohne FK – Nachrichten überleben alles) |
| `actor_kind` | `smallint` | ja | – | ActorKind: `PrincipalKind?` | 0 User, 1 ApiKey, 2 App, 3 Bot |
| `origin` | `varchar(40)` | nein | – | Origin: `string` | `StateChangeOrigin`-Name bzw. `ApiSurface` bzw. `worker` |
| `workspace_id` | `uuid` | ja | – | WorkspaceId: `Guid?` | ohne FK |
| `project_id` | `uuid` | ja | – | ProjectId: `Guid?` | ohne FK |
| `correlation_id` | `varchar(100)` | ja | – | CorrelationId: `string?` | – |
| `causation_depth` | `integer` | nein | `0` | CausationDepth: `int` | > 5 → verwerfen |
| `dispatched_at` | `timestamptz` | ja | – | DispatchedAt: `DateTimeOffset?` | gesetzt vom Dispatcher |
| `attempts` | `integer` | nein | `0` | Attempts: `int` | Dispatch-Versuche |
| `last_error` | `text` | ja | – | LastError: `string?` | – |

**Indizes:** `ix_outbox_messages_pending` (`id`) WHERE `dispatched_at IS NULL` (Dispatcher `FOR UPDATE SKIP LOCKED … ORDER BY id`); `ix_outbox_messages_dispatched_at` (`dispatched_at`) WHERE `dispatched_at IS NOT NULL` (Aufräumen nach `Plane:Messaging:OutboxRetentionDays`, Default 7). Trigger-freier Weckruf: der `OutboxInterceptor` sendet nach Commit `NOTIFY plane_outbox` (Post-Commit-Aktion).

`inbox_messages`: `consumer varchar(200)` + `message_id uuid` (PK zusammen), `processed_at timestamptz NOT NULL`; Index `ix_inbox_messages_processed_at` (Aufräumen nach 14 Tagen).

`jobs`:

| Spalte | PostgreSQL | Null | Default | Regel |
|---|---|---|---|---|
| `id` | `uuid` | nein | – | PK (UUIDv7) |
| `queue` | `varchar(50)` | nein | `'default'` | benannte Queues (D16 §3.2.5) |
| `job_type` | `varchar(200)` | nein | – | CLR-Typname des `IJob` (Katalog) |
| `payload` | `jsonb` | nein | `'{}'::jsonb` | Job-Daten |
| `run_at` | `timestamptz` | nein | – | frühester Start |
| `status` | `smallint` | nein | `0` | 0 Pending, 1 Running, 2 Succeeded, 3 Failed (Retry geplant), 4 DeadLetter |
| `attempts` | `integer` | nein | `0` | – |
| `max_attempts` | `integer` | nein | `5` | Webhook-Policy wie Original (ADR-020) |
| `locked_until` | `timestamptz` | ja | – | Lease des Workers |
| `locked_by` | `varchar(100)` | ja | – | Worker-Instanz |
| `dedupe_key` | `varchar(200)` | ja | – | `IJobScheduler.EnqueueAsync(dedupeKey)` |
| `last_error` | `text` | ja | – | – |
| `created_at` | `timestamptz` | nein | – | – |
| `completed_at` | `timestamptz` | ja | – | – |
| `actor_id`, `workspace_id`, `traceparent` | `uuid`/`uuid`/`varchar(55)` | ja | – | Kontext wie Outbox |

**Indizes:** `ix_jobs_due` (`queue`, `run_at`) WHERE `status IN (0,3)`; `ux_jobs_dedupe_key` UNIQUE (`dedupe_key`) WHERE `dedupe_key IS NOT NULL AND status IN (0,1,3)`; **Check** `ck_jobs_status` CHECK (`status BETWEEN 0 AND 4`).

`recurring_jobs`: `name varchar(100)` PK, `cron varchar(100) NOT NULL` (UTC), `last_run_at timestamptz NULL`, `next_run_at timestamptz NULL`, `last_status smallint NULL`. Leader-Wahl über `pg_try_advisory_lock` (keine Tabelle). Zeilen werden beim Start des Workers aus `IRecurringJobRegistry` synchronisiert (keine Seeds).

##### 3.4.18.7 `integration_connections` (ab I0) und `external_links` (ab I2) (Eigentümer `Integrations`, Andockstelle F1/F2)

Spalten und Schlüssel **verbindlich nach D16 §3.4.2**; hier die Typen:

| Tabelle.Spalte | PostgreSQL | Null | Default | Regel |
|---|---|---|---|---|
| `integration_connections.id` | `uuid` | nein | – | PK |
| `.workspace_id` | `uuid` | nein | – | FK `workspaces` CASCADE |
| `.provider` | `varchar(32)` | nein | – | `forgejo` |
| `.base_url` | `varchar(1024)` | nein | – | Forgejo-Basis-URL |
| `.external_account_id` / `.external_account_name` | `varchar(255)` | nein / ja | – | Forgejo-Org bzw. Instanz-Kennung |
| `.status` | `varchar(20)` | nein | `'active'` | Check `IN ('active','disconnected','error')` |
| `.bot_user_id` | `uuid` | ja | – | FK `users` RESTRICT (`is_bot = true`, `bot_type = 'integration'`) |
| `.config` | `jsonb` | nein | `'{}'::jsonb` | nicht geheim |
| `.connected_by_id` | `uuid` | ja | – | FK `users` SET NULL |
| `.connected_at` | `timestamptz` | nein | – | – |
| `.last_error` | `text` | ja | – | – |
| Audit + `deleted_at` | wie A | | | Basis `AuditableEntity` + `IWorkspaceScoped` |
| `external_links.id` | `uuid` | nein | – | PK |
| `.workspace_id`, `.project_id` | `uuid` | nein | – | Scope-FK (Basis P) |
| `.work_item_id` | `uuid` | nein | – | FK `work_items` CASCADE |
| `.comment_id` | `uuid` | ja | – | FK `work_item_comments` CASCADE |
| `.connection_id` | `uuid` | nein | – | FK `integration_connections` CASCADE |
| `.provider` | `varchar(32)` | nein | – | – |
| `.external_type` | `varchar(30)` | nein | – | Check `IN ('issue','pull_request','branch','commit','check','comment')` |
| `.external_id` | `varchar(255)` | nein | – | ID/SHA/Branch |
| `.external_key` | `varchar(512)` | nein | – | `owner/repo#12` usw. |
| `.url` | `varchar(2048)` | nein | – | – |
| `.title` | `text` | ja | – | – |
| `.state` | `varchar(20)` | ja | – | Check `IN ('open','draft','merged','closed','success','failure','pending','deleted')` |
| `.metadata` | `jsonb` | nein | `'{}'::jsonb` | – |
| `.sync_hash` | `varchar(64)` | ja | – | Echo-Unterdrückung |
| `.external_updated_at`, `.last_synced_at` | `timestamptz` | ja | – | – |
| Audit + `deleted_at` | wie A | | | Basis `ProjectEntity` |

**Indizes:** `ux_integration_connections_account` UNIQUE (`provider`, `base_url`, `external_account_id`) WHERE `deleted_at IS NULL`; `ix_integration_connections_workspace_provider` (`workspace_id`, `provider`); `ux_external_links_identity` UNIQUE (`connection_id`, `external_type`, `external_id`, `work_item_id`, `comment_id`) **NULLS NOT DISTINCT** (Npgsql `AreNullsDistinct(false)`, PostgreSQL ≥ 15) WHERE `deleted_at IS NULL`; `ix_external_links_work_item` (`work_item_id`); `ix_external_links_lookup` (`connection_id`, `external_type`, `external_id`). **Abweichung zu D16 E-13:** `external_links` entsteht erst in I2 (FK auf `work_items`), `integration_connections` in I0 (Rückmeldung §9). In der CE leer.

##### 3.4.18.8 `search_documents` (Eigentümer `Search`, ab I5, Andockstelle G1/B6)

| Spalte | PostgreSQL | Null | Default | C#-Property: Typ | Regel |
|---|---|---|---|---|---|
| `entity_type` | `varchar(30)` | nein | – | EntityType: `string` | PK-Teil: `work_item`, `page`, `project`, `cycle`, `module`, `view`, `comment` |
| `entity_id` | `uuid` | nein | – | EntityId: `Guid` | PK-Teil (ohne FK, polymorph) |
| `workspace_id` | `uuid` | nein | – | WorkspaceId: `Guid` | FK `workspaces` CASCADE |
| `project_id` | `uuid` | ja | – | ProjectId: `Guid?` | ohne FK (Pages haben mehrere Projekte → `facets`) |
| `title` | `text` | nein | `''` | Title: `string` | – |
| `body` | `text` | ja | – | Body: `string?` | `*_stripped`, max. 1 MiB (Pipeline kürzt) |
| `facets` | `jsonb` | nein | `'{}'::jsonb` | Facets: `JsonObject` | `IndexDocument.Facets` (z. B. `project_ids`, `state_group`, `identifier`) |
| `search_vector` | `tsvector` | – | GENERATED | SearchVector: `NpgsqlTsVector` | `GENERATED ALWAYS AS (setweight(to_tsvector('simple', plane_unaccent(coalesce(title,''))), 'A') \|\| setweight(to_tsvector('simple', plane_unaccent(coalesce(body,''))), 'B')) STORED` (per `HasComputedColumnSql(..., stored: true)`) |
| `updated_at` | `timestamptz` | nein | – | UpdatedAt: `DateTimeOffset` | Quelle |
| `indexed_at` | `timestamptz` | nein | – | IndexedAt: `DateTimeOffset` | Pipeline |

**Indizes:** PK (`entity_type`, `entity_id`); `ix_search_documents_vector` GIN (`search_vector`); `ix_search_documents_title_trgm` GIN (`title gin_trgm_ops`); `ix_search_documents_workspace_type` (`workspace_id`, `entity_type`). Kein Soft-Delete: gelöschte Entitäten entfernt `IIndexingPipeline.RemoveAsync`. **Keine** `embedding`-Spalte in der CE (D16 §3.3.7); G1 ergänzt eine eigene Tabelle (§6).

### 3.5 Löschen: Soft-Delete-Filter, Join-Regeln, Kaskaden-Registry, Hard-Delete

#### 3.5.1 Filter

| Filter | Gilt für | Ausdruck | Abschalten |
|---|---|---|---|
| `soft_delete` | alle `ISoftDeletable` (Basen A/W/P sowie X-Tabellen mit `deleted_at`) | `e => e.DeletedAt == null` | `IgnoreQueryFilters([QueryFilterNames.SoftDelete])` (= Original `all_objects`); nur in den Fällen §3.5.2, im Hard-Delete-Job, in Restore-Pfaden und in Admin-Abfragen (`plane-cli`) |
| `workspace_tenant` | alle `IWorkspaceScoped` | `e => !_tenant.IsBound \|\| e.WorkspaceId == _tenant.WorkspaceId` (D02 §3.5.4) | nie im Fachcode; `IgnoreQueryFilters()` ohne Argument ist außerhalb von `Plane.Data`, Migrator und Tests verboten (Banned-API, D02 §5.1.3) |

Tabellen **ohne** Soft-Delete (harte Löschung ist fachlich gewollt oder Zeilen sind unveränderlich): `users`, `profiles`, `user_identities`, `user_sessions`, `role_permissions`, `data_protection_keys`, `work_item_sequences`, `work_item_relation_types`, `*_feature_settings`, `outbox_messages`, `inbox_messages`, `jobs`, `recurring_jobs`, `search_documents`.

#### 3.5.2 Join-Ausnahmen (Original liest gelöschte Zeilen mit) – abschließende Liste

| Nr. | Stelle (Original) | Original-Verhalten | Umsetzung im Ziel | Status |
|---|---|---|---|---|
| J1 | Sortierung `labels__name`, `assignees__first_name`, `issue_module__module__name` (`API/utils/order_queryset.py`) | `MIN(...)` über M2M **ohne** `deleted_at`-Filter der Join-Tabelle | SQL-Baustein der Query-Engine ohne Filter auf `work_item_labels`/`work_item_assignees`/`module_work_items` (D02 §3.11.5) | 1:1 |
| J2 | `count_filter` der gruppierten Pagination | `LEFT JOIN intake_issues` ohne `deleted_at`-Filter | `GroupedPageSqlBuilder` joint `intake_work_items` ohne Filter (D02 §3.11.4) | 1:1 |
| J3 | Vorwärts-FK `issue.state`, `issue.estimate_point`, `issue.parent` (Django-Base-Manager) | lädt auch soft-gelöschte Ziele | Projektionen lesen `state_id`/`estimate_point_id`/`parent_id` als Wert; Anzeige-Felder (`state__group`, `state__name`) per Join **mit** `IgnoreQueryFilters([SoftDelete])` auf `states` in der Work-Item-Projektion (`WorkItemProjections.ListItem`), weil ein gelöschter State nur bei leerem State möglich ist und Drafts dann `NULL` haben | 1:1 |
| J4 | Activity-Liste mit Kommentar-Bezug | `issue_comment` zeigt ggf. auf gelöschten Kommentar | Activity-Projektion liest `comment_id` als Wert ohne Join; Kommentarliste filtert gelöschte | 1:1 |
| J5 | Mitgliedschaftsprüfung `workspace__slug=` (Join `workspace_members → workspaces` ohne Filter auf `workspaces`) | Mitglied eines gelöschten Workspace bleibt bis zum Ende der asynchronen Kaskade berechtigt | `ScopeBindingFilter` filtert `workspaces.deleted_at IS NULL` (D02 §3.5.2) → sofort „kein Workspace“ | korrigiert (DEV-DM-11) |
| J6 | Favoriten/Recents/Deploy-Boards auf gelöschte Entitäten (polymorph, kein FK) | Einträge bleiben, Listen-Views filtern über Existenz-Subqueries | gleiche Existenz-Prädikate in den Listen-Queries (`EntityExistsPredicates`) | 1:1 |
| J7 | Work-Item-Detail eines Work Items mit soft-gelöschtem Parent | `parent` wird über Vorwärts-FK geladen | durch Inline-Kaskade nicht erreichbar (Kind wird mitgelöscht) | – |

Jede neue Abfrage mit `IgnoreQueryFilters([SoftDelete])` braucht einen Eintrag in dieser Tabelle (Architekturtest `SoftDeleteBypassIsDocumented` zählt die Aufrufstellen gegen `tests/Plane.ArchitectureTests/soft-delete-bypass.yaml`).

#### 3.5.3 Soft-Delete-Semantik

1. `db.Remove(entity)` auf eine `ISoftDeletable`-Entität → `SoftDeleteInterceptor` setzt `deleted_at = updated_at = now`, `updated_by_id = Akteur` (wie `SoftDeleteModel.delete` → `save()`), Status `Modified`.
2. Die Registry (§3.5.4) wird für die Entität ausgewertet: **Inline**-Einträge als set-basiertes `ExecuteUpdateAsync` (`deleted_at`, `updated_at`; `updated_by_id` bleibt – Korrektur A02a-#10) rekursiv; **SetNull**-Einträge als `ExecuteUpdateAsync(x => x.<Fk>, null)` auf **alle** referenzierenden Zeilen (Korrektur Q2: Original nullte nur Zeilen, die der Default-Manager sah); **Deferred**-Einträge als `SoftDeleteCascadeJob` (Outbox im selben Commit).
3. `QuerySet.delete()`-Stellen des Originals (Massen-Soft-Delete ohne Kaskade, A02a §3.2 c) werden als `ExecuteUpdateAsync(deleted_at = now)` **ohne** Registry umgesetzt; die Stellen stehen im jeweiligen Command mit Kommentar `// Original: QuerySet.delete() – keine Kaskade`.
4. Wiederherstellen (`SoftDeleteRestoreService`, D02 §4.1) setzt `deleted_at = NULL` für die Wurzel und die per Inline-Kaskade **im selben Zeitstempel** gelöschten Kinder; SetNull-Wirkungen werden **nicht** zurückgenommen (wie Original, A02a-#11). Original-`restore_related_objects` ist ein leerer Stub – die CE nutzt Restore nur bei Archiv-Funktionen, die nicht über Soft-Delete laufen (Archiv = `archived_at`).
5. Unique-Indizes sind partiell (`WHERE deleted_at IS NULL`) → Neuanlage nach Löschung möglich; **voll** eindeutig bleiben bewusst: `users.email`, `users.username`, `deploy_boards.anchor`, `api_tokens.token_hash`, `exports.token`, `instance_configurations.key`, `work_items (project_id, sequence_id)`.

#### 3.5.4 Kaskaden-Registry (vollständig, Registrierung je Eigentümer-Modul in `IModule.AddServices`)

Abgeleitet aus allen FKs mit Original-`CASCADE`/`SET NULL` (DB-Lösch-Verhalten §3.4) auf soft-löschbare Ziele; Ziele ohne Soft-Delete (`users`, `instances`) erzeugen keine Einträge. Maschinenlesbar in `_data/03-datenmodell.json` (`soft_delete_cascades[]`). Ein Architekturtest prüft, dass jede FK mit `OnDelete(Cascade|SetNull)` auf eine `ISoftDeletable`-Entität genau einen Registry-Eintrag oder einen `NoSoftCascade`-Vermerk hat (D02 §3.2.2).

| Gelöschte Wurzel (Soft-Delete) | Modus | betroffene Tabelle.Spalte (Aktion) |
|---|---|---|
| `file_assets` | Inline | `users.avatar_asset_id` → sofort `NULL`; `users.cover_image_asset_id` → sofort `NULL`; `workspaces.logo_asset_id` → sofort `NULL`; `projects.cover_image_asset_id` → sofort `NULL` |
| `workspaces` | **Deferred** (`SoftDeleteCascadeJob`, Queue `default`) | alle Zeilen mit `workspace_id` in: `analytic_views`, `api_tokens`, `cycle_user_properties`, `cycle_work_items`, `cycles`, `deploy_boards`, `draft_work_item_assignees`, `draft_work_item_cycles`, `draft_work_item_labels`, `draft_work_item_modules`, `draft_work_items`, `estimate_points`, `estimates`, `exports`, `external_links`, `file_assets`, `intake_work_items`, `intakes`, `integration_connections`, `labels`, `module_links`, `module_members`, `module_user_properties`, `module_work_items`, `modules`, `notifications`, `page_labels`, `page_logs`, `page_versions`, `pages`, `project_member_invites`, `project_members`, `project_pages`, `project_public_members`, `project_user_properties`, `projects`, `roles`, `states`, `stickies`, `user_favorites`, `user_notification_preferences`, `user_recent_visits`, `views`, `webhook_logs`, `webhooks`, `work_item_activities`, `work_item_assignees`, `work_item_comment_reactions`, `work_item_comments`, `work_item_description_versions`, `work_item_labels`, `work_item_links`, `work_item_mentions`, `work_item_reactions`, `work_item_relations`, `work_item_subscribers`, `work_item_types`, `work_item_versions`, `work_item_votes`, `work_items`, `workspace_home_preferences`, `workspace_member_invites`, `workspace_members`, `workspace_themes`, `workspace_user_links`, `workspace_user_preferences`, `workspace_user_properties`; **nur Hard-Delete** (keine Soft-Spalte): `search_documents`, `workspace_feature_settings` |
| `user_favorites` | Inline | `user_favorites.parent_id` → soft-löschen (rekursiv) |
| `projects` | **Deferred** (`SoftDeleteCascadeJob`, Queue `default`) | alle Zeilen mit `project_id` in: `cycle_user_properties`, `cycle_work_items`, `cycles`, `deploy_boards`, `draft_work_item_assignees`, `draft_work_item_cycles`, `draft_work_item_labels`, `draft_work_item_modules`, `draft_work_items`, `estimate_points`, `estimates`, `external_links`, `file_assets`, `intake_work_items`, `intakes`, `labels`, `module_links`, `module_members`, `module_user_properties`, `module_work_items`, `modules`, `notifications`, `project_identifiers`, `project_member_invites`, `project_members`, `project_pages`, `project_public_members`, `project_user_properties`, `states`, `user_favorites`, `user_notification_preferences`, `user_recent_visits`, `views`, `work_item_activities`, `work_item_assignees`, `work_item_comment_reactions`, `work_item_comments`, `work_item_description_versions`, `work_item_labels`, `work_item_links`, `work_item_mentions`, `work_item_reactions`, `work_item_relations`, `work_item_subscribers`, `work_item_types`, `work_item_versions`, `work_item_votes`, `work_items`, `workspace_user_links`; **nur Hard-Delete** (keine Soft-Spalte): `project_feature_settings`, `work_item_sequences` |
| `estimates` | Inline | `projects.estimate_id` → sofort `NULL`; `estimate_points.estimate_id` → soft-löschen (rekursiv) |
| `states` | Inline | `projects.default_state_id` → sofort `NULL`; `work_items.state_id` → soft-löschen; praktisch nie erreicht, weil nur leere States löschbar sind (Guard); `draft_work_items.state_id` → sofort `NULL` |
| `labels` | Inline | `labels.parent_id` → soft-löschen (rekursiv); `work_item_labels.label_id` → soft-löschen (rekursiv); `draft_work_item_labels.label_id` → soft-löschen (rekursiv); `page_labels.label_id` → soft-löschen (rekursiv) |
| `work_items` | Inline | `work_items.parent_id` → soft-löschen (rekursiv); `work_item_assignees.work_item_id` → soft-löschen (rekursiv); `work_item_labels.work_item_id` → soft-löschen (rekursiv); `work_item_relations.work_item_id` → soft-löschen (rekursiv); `work_item_relations.related_work_item_id` → soft-löschen (rekursiv); `work_item_mentions.work_item_id` → soft-löschen (rekursiv); `work_item_subscribers.work_item_id` → soft-löschen (rekursiv); `work_item_links.work_item_id` → soft-löschen (rekursiv); `work_item_comments.work_item_id` → soft-löschen (rekursiv); `work_item_reactions.work_item_id` → soft-löschen (rekursiv); `work_item_votes.work_item_id` → soft-löschen (rekursiv); `work_item_activities.work_item_id` → NoSoftCascade (Verlauf bleibt, Hard-Delete kaskadiert); `work_item_description_versions.work_item_id` → soft-löschen (rekursiv); `work_item_versions.work_item_id` → soft-löschen (rekursiv); `draft_work_items.parent_id` → sofort `NULL`; `cycle_work_items.work_item_id` → soft-löschen (rekursiv); `module_work_items.work_item_id` → soft-löschen (rekursiv); `intake_work_items.work_item_id` → soft-löschen (rekursiv); `intake_work_items.duplicate_to_id` → sofort `NULL`; `file_assets.work_item_id` → soft-löschen (rekursiv); `external_links.work_item_id` → soft-löschen (rekursiv) |
| `estimate_points` | Inline | `work_items.estimate_point_id` → sofort `NULL`; `draft_work_items.estimate_point_id` → sofort `NULL` |
| `work_item_types` | Inline | `work_items.type_id` → sofort `NULL`; `draft_work_items.type_id` → sofort `NULL` |
| `work_item_comments` | Inline | `work_item_comments.parent_id` → soft-löschen (rekursiv); `work_item_comment_reactions.comment_id` → soft-löschen (rekursiv); `work_item_activities.comment_id` → sofort `NULL`; `file_assets.comment_id` → soft-löschen (rekursiv); `external_links.comment_id` → soft-löschen (rekursiv) |
| `work_item_activities` | Inline | `work_item_versions.activity_id` → sofort `NULL` |
| `draft_work_items` | Inline | `draft_work_item_assignees.draft_work_item_id` → soft-löschen (rekursiv); `draft_work_item_labels.draft_work_item_id` → soft-löschen (rekursiv); `draft_work_item_modules.draft_work_item_id` → soft-löschen (rekursiv); `draft_work_item_cycles.draft_work_item_id` → soft-löschen (rekursiv); `file_assets.draft_work_item_id` → soft-löschen (rekursiv) |
| `modules` | Inline | `draft_work_item_modules.module_id` → soft-löschen (rekursiv); `module_members.module_id` → soft-löschen (rekursiv); `module_work_items.module_id` → soft-löschen (rekursiv); `module_links.module_id` → soft-löschen (rekursiv); `module_user_properties.module_id` → soft-löschen (rekursiv) |
| `cycles` | Inline | `draft_work_item_cycles.cycle_id` → soft-löschen (rekursiv); `cycle_work_items.cycle_id` → soft-löschen (rekursiv); `cycle_user_properties.cycle_id` → soft-löschen (rekursiv) |
| `intakes` | Inline | `intake_work_items.intake_id` → soft-löschen (rekursiv); `deploy_boards.intake_id` → sofort `NULL` |
| `pages` | Inline | `pages.parent_id` → Deferred (D2-Vorbereitung; CE: `parent_id` immer NULL); `project_pages.page_id` → soft-löschen (rekursiv); `page_labels.page_id` → soft-löschen (rekursiv); `page_logs.page_id` → soft-löschen (rekursiv); `page_versions.page_id` → soft-löschen (rekursiv); `file_assets.page_id` → soft-löschen (rekursiv) |
| `integration_connections` | Inline | `external_links.connection_id` → soft-löschen (rekursiv) |

Registrierungsbeispiel (Eigentümer `WorkItems`):

```csharp
// src/modules/WorkItems/Plane.WorkItems/WorkItemsModule.cs (Ausschnitt)
cascade.Cascade<WorkItem, WorkItem>(c => c.ParentId, CascadeMode.Inline);                 // Sub-Work-Items (Original CASCADE parent)
cascade.Cascade<WorkItem, WorkItemAssignee>(c => c.WorkItemId, CascadeMode.Inline);
cascade.Cascade<WorkItem, WorkItemLabel>(c => c.WorkItemId, CascadeMode.Inline);
cascade.Cascade<WorkItem, WorkItemRelation>(c => c.WorkItemId, CascadeMode.Inline);
cascade.Cascade<WorkItem, WorkItemRelation>(c => c.RelatedWorkItemId, CascadeMode.Inline);
cascade.Cascade<WorkItem, WorkItemComment>(c => c.WorkItemId, CascadeMode.Inline);         // → rekursiv Reaktionen, Antworten, file_assets(comment)
cascade.Cascade<WorkItem, CycleWorkItem>(c => c.WorkItemId, CascadeMode.Inline);           // fremder Eigentümer (Cycles) – deklarierte Kaskade
cascade.Cascade<WorkItem, ModuleWorkItem>(c => c.WorkItemId, CascadeMode.Inline);
cascade.Cascade<WorkItem, IntakeWorkItem>(c => c.WorkItemId, CascadeMode.Inline);
cascade.SetNull<WorkItem, IntakeWorkItem>(c => c.DuplicateToId);
cascade.SetNull<WorkItem, DraftWorkItem>(c => c.ParentId);                                 // DEV-DM-07 (Original CASCADE)
cascade.NoSoftCascade<WorkItem, WorkItemActivity>(c => c.WorkItemId, reason: "Verlauf bleibt (Original DO_NOTHING); Hard-Delete kaskadiert per FK");
```

#### 3.5.5 Hard-Delete und Aufbewahrung

| Job (Name in `IRecurringJobRegistry`) | Cron (UTC) | Wirkung | Konfiguration (Default) | Original |
|---|---|---|---|---|
| `retention.hard_delete` (`HardDeleteJob`) | `0 0 * * *` | je Wurzeltabelle in FK-sicherer Reihenfolge `DELETE … WHERE deleted_at < now() - interval` in Batches à 1000; DB-Kaskaden (`ON DELETE CASCADE/SET NULL`) erledigen Kinder; anschließend `FileAssetPurgeConsumer` entfernt Objekte gelöschter `file_assets` aus dem Speicher | `Plane:Retention:HardDeleteDays` (60, Alias `HARD_DELETE_AFTER_DAYS`) | `deletion_task.hard_delete`; Abbruch-Bug Q3 behoben, Objektlöschung neu |
| `retention.api_activity_logs` | `30 2 * * *` | `DELETE api_activity_logs WHERE created_at <= now() - 14 d` | `Plane:Retention:ApiActivityLogDays` (14) | `cleanup_task.delete_api_logs` |
| `retention.webhook_logs` | `30 3 * * *` | dto. `webhook_logs` | `Plane:Retention:WebhookLogDays` (14) | `cleanup_task.delete_webhook_logs` |
| `retention.email_notification_logs` | `45 2 * * *` | `sent_at <= now() - 7 d` | `Plane:Retention:EmailLogDays` (7, Alias `EMAIL_LOG_RETENTION_DAYS`) | `cleanup_task` |
| `retention.page_versions` | `0 3 * * *` | je Page alles außer den 20 neuesten (`created_at`) hart löschen | `Plane:Retention:PageVersions` (20) | `cleanup_task.delete_page_versions` |
| `retention.work_item_description_versions` | `15 3 * * *` | je Work Item alles außer den 20 neuesten | `Plane:Retention:WorkItemDescriptionVersions` (20) | `cleanup_task.delete_issue_description_versions` |
| `retention.unuploaded_assets` | `0 2 * * *` | `file_assets` mit `is_uploaded = false` und älter als n Tage **soft** löschen | `Plane:Retention:UnuploadedAssetDays` (7, Alias `UNUPLOADED_ASSET_DELETE_DAYS`) | `file_asset_task.delete_unuploaded_file_asset` |
| `retention.export_links` | `30 1 * * *` | `exports.url IS NOT NULL AND created_at <= now() - 8 d` → Objekt löschen, `url = NULL` (einmal statt doppelt eingeplant, A02a-#13) | `Plane:Retention:ExportLinkDays` (8) | `exporter_expired_task.delete_old_s3_link` |
| `retention.messaging` | `0 4 * * *` | `outbox_messages` dispatched > 7 d, `inbox_messages` > 14 d, `jobs` erfolgreich > 7 d löschen | `Plane:Messaging:*RetentionDays` | – (neu) |
| `retention.user_sessions` | `*/30 * * * *` | `user_sessions WHERE expires_at < now()` | – | Django-`clearsessions` (implizit) |

Die Job-Klassen, Queues und Fehlerbehandlung definiert `06-hintergrundjobs-events-benachrichtigungen.md`; Namen und Spalten hier sind verbindlich für die Indizes in §3.4.

