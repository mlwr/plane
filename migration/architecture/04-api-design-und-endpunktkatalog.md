# 04 – API-Design und Endpunktkatalog (D04)

> **Status:** verbindlich für das Thema „API-Verträge“ (Fachdokument nach `01` Anhang A: „vollständiger Endpunktkatalog Original → Modul/Handler, Bug-/Sicherheits-Entscheidungstabelle“; baut auf ADR-011, ADR-015, ADR-016, ADR-051, `01` §7.2–7.5, §7.11). Rangfolge nach `17` §1: `00` > `01` > dieses Dokument; Mechanik (Oberflächen, Pipeline, Fehlerfabrik, Paginator, Query-Engine) gehört `02`, Berechtigungs-Semantik `05`, Hintergrundwirkungen (Webhooks, Mails, Activity) `06`, Live-Protokoll `07`, Tests/Gates `15`, Andockstellen `16`.
>
> **Zielrepository:** `funk.` (ADR-009). Pfade für Zielcode sind relativ zur Wurzel von `funk.` (`src/…`, `tests/…`, `frontend/…`). Pfade des Originals sind relativ zu `/home/user/plane` (Referenzstand `053b2c0`, Plane 1.4.2, ADR-006).
>
> **Maschinenlesbar:** `migration/architecture/_data/endpoints.json` (732 Endpunkt-Methoden, je Zeile Oberfläche, Route-Template, Modul, Endpoint-Klasse, Handler, Permission, Status Original/Ziel, Abweichungen, DT, Inkrement, CE-IDs, Pagination, Read-Replica, dokumentierte Fehlerkörper) und `migration/architecture/_data/04-decisions.json` (Entscheidungstabelle `DT-*`). Beide Dateien sind die Soll-Liste für `Plane.Tools.ParityHarness coverage` (`15` §3.6.3) und für `RouteInventoryTests` (§7). In `funk.` liegen sie gespiegelt unter `docs/plan/architecture/_data/` (ADR-006).
>
> **Kürzel:** `{W}` = `/api/workspaces/{slug}`, `{P}` = `{W}/projects/{project_id}`, `{V1W}` = `/api/v1/workspaces/{slug}`, `{V1P}` = `{V1W}/projects/{project_id}`, `{SP}` = `/api/public/anchor/{anchor}`, `{AV2}` = `/api/assets/v2`, `{I}` = `/api/instances`. Datei-Kürzel des Originals wie `05` Anhang B: `V/` = `apps/api/plane/app/views/`, `V1V/` = `apps/api/plane/api/views/`, `SPV/` = `apps/api/plane/space/views/`, `license/V1V/` = `apps/api/plane/license/api/views/`. Analyse-Kürzel: `A03` … `A12` = `migration/analysis/03-…` … `12-…`. Original-IDs werden als `<Dok>:<ID>` geschrieben (`A04:L1` = Zeile L1 in A04, `A06:#5` = Auth-Route Nr. 5, `A05:S-06` = Space-Endpunkt S-06).
>
> **Quellen (geprüft am 23.10.2026):** Endpunkt-Inventare A03 §2.5–§2.11 (216 Zeilen), A04 §2.2–§2.15 (180), A05 §2.2/§2.6/§2.7/§2.8 (175), A06 §2.1/§2.2 (37 + 7), A12 §2.26.2 (4), A07 §2.10 (Webhook-Ausgang); `05-permission-matrix.json` (672 Endpunkt-Methoden aus AST-Extraktion); Original-URL-Konfiguration `apps/api/plane/{app,api,space,license,authentication}/urls*`, `apps/api/plane/urls.py`; Original-Frontend-Services `apps/web/services/**`, `packages/services/src/**`, `apps/space/**`, `apps/admin/**` (267 Pfadmuster); Feature-Katalog `features/_data/ce-features.json` (507 CE-IDs). Die Zusammenführung erfolgte per Skript (Abgleich Methode × normalisierter Pfad × Alias-Regeln, §3.1.4); alle 672 Matrix-Zeilen und alle 571 Analyse-Zeilen sind einer Katalogzeile zugeordnet.

## Inhaltsverzeichnis

1. [Ziel & Scope](#1-ziel--scope)
2. [Entscheidungen (D04-ADR-01 ff.)](#2-entscheidungen-d04-adr-01-ff)
3. [Detaildesign](#3-detaildesign)
   - 3.1 Oberflächen und URL-Struktur · 3.2 Methoden und Statuscodes · 3.3 Request-Konventionen · 3.4 Antwort-Konventionen · 3.5 Fehlerformen · 3.6 Fehlertext-Katalog · 3.7 Pagination · 3.8 Filter-Syntax · 3.9 `expand` und `fields` · 3.10 Bulk-Operationen und Idempotenz · 3.11 API-Keys und Authentisierung je Oberfläche · 3.12 Rate Limits · 3.13 Entscheidungstabelle für Original-Fehler und Sicherheitslücken (DT) · 3.14 OpenAPI · 3.15 TypeScript-Typen und Client für Angular · 3.16 Contract-Tests gegen das Original · 3.17 Webhook-Ausgang · 3.18 Live-Endpunkte · 3.19 Gateway-Kopplungen · 3.20 Branding (ADR-009B) in API-Texten
4. [Vollständige Mapping-Tabellen Original → Ziel](#4-vollständige-mapping-tabellen-original--ziel)
   - 4.1–4.24 je Modul · 4.25 Methoden-Nebenprodukte · 4.26 Frontend-Aufrufe ohne CE-Backend · 4.27 Webhook-Ausgang: Ereignisse → auslösende Endpunkte · 4.28 CE-IDs ohne eigene Endpunktzeile · 4.29 Abweichungs-IDs `DEV-API-*`
5. [Code-Skelette](#5-code-skelette)
6. [Erweiterungspunkte für Bezahl-Pakete](#6-erweiterungspunkte-für-bezahl-pakete)
7. [Akzeptanzkriterien & Tests](#7-akzeptanzkriterien--tests)
8. [Risiken & offene Punkte](#8-risiken--offene-punkte)
9. [Abhängigkeiten zu anderen Dokumenten (02–16)](#9-abhängigkeiten-zu-anderen-dokumenten-0216)

---

## 1. Ziel & Scope

### 1.1 Ziel

Ein Implementierungs-Agent, der einen vertikalen Schnitt (`01` §1.3) umsetzt, findet in diesem Dokument **für jede HTTP-/WebSocket-Route des Originals und jede neue Route der Zielplattform**:

1. ob sie in `funk.` registriert wird, und wenn nicht, mit welchem Status (404/405) sie antwortet und warum (Spalte „Abw./DT“, §3.13),
2. das Ziel-Modul, die Endpoint-Klasse (Datei), den Mediator-Handler (Command/Query) und das Route-Template,
3. den Permission-Key und die Ziel-Prüfung (aus `05` Anhang B übernommen),
4. den Erfolgsstatus im Original und im Ziel,
5. Pagination-Modus, Read-Replica-Eignung, Filter-/`expand`-Unterstützung und die dokumentierten Fehlerkörper (in `endpoints.json`),
6. das Inkrement, in dem der Endpunkt gebaut wird, und die CE-IDs, deren Funktion er trägt.

Außerdem legt das Dokument die **Vertragskonventionen** fest, die über alle Endpunkte gleich sind (URL-Struktur, Methoden, Statuscodes, Fehlerformen, Pagination, Filter-Syntax, `expand`/`fields`, Bulk, Idempotenz, API-Keys, Rate-Limits, OpenAPI, TypeScript-Typen, Contract-Tests), und entscheidet für **jeden dokumentierten Fehler und jede Sicherheitslücke** der Original-API zwischen „1:1“, „korrigieren“ und „nicht portieren“ (Entscheidungstabelle `DT-*`, §3.13).

### 1.2 Scope

| Im Scope | Nicht im Scope (zuständiges Dokument) |
|---|---|
| Interne App-API `/api/` (A03, A04), Public API v1 `/api/v1/` (A05 §2.2), Space-API `/api/public/` (A05 §2.6), Instanz-/God-Mode-API `/api/instances/` (A05 §2.7), Auth `/auth/` (A06 §2.1, `05` §3.2), Root `/`, `/robots.txt`, OpenAPI `/api/schema/…`, Live `/live/…` (A12 §2.26.2), Integrations-Eingang `/api/integrations/…` (🧱 F1), Webhook-**Ausgang** (Vertrag gegenüber Empfängern) | Mechanik der Oberflächen, Pipeline, Fehlerfabrik, Paginator, Query-Engine (`02` §3.3–§3.11) |
| Endpunktkatalog Original → Modul/Klasse/Handler mit Pfaden, Status, CE-IDs, Inkrement | Permission-Semantik, Keycloak, Sessions, CSRF, SSRF (`05`) |
| Konventionen für Status, Fehler, Pagination, Filter, `expand`/`fields`, Bulk, Idempotenz, API-Keys, Rate-Limits, OpenAPI, TS-Typen | Request-/Response-DTO-Felder je Endpunkt im Detail (Quelle bleibt A03–A05 + Golden-Files; DTO-Klassen je Modul nach `02` §5.2.4) |
| Entscheidungstabelle für Original-Bugs und Sicherheitslücken der API (DT) inkl. Abweichungs-IDs `DEV-API-05…62` | Webhook-Zustellung, Trigger-Projektion, Retry, Mails (`06` §3.14); Hocuspocus-Protokoll (`07`) |
| Contract-Test-Abdeckung je Endpunkt (Soll-Liste) | Parity-Harness-Mechanik, Seeds, Gates (`15` §3.6) |
| Erweiterungspunkte der 🧱-Pakete **an der API-Oberfläche** (§6) | Fachdesign der Bezahl-Pakete (später je Welle, `16` §6) |

### 1.3 Was wird in welchem Inkrement gebraucht

| Inkrement | Bausteine dieses Dokuments | registrierte Endpunkt-Methoden | DT-Zeilen mit Umsetzung | Abnahme |
|---|---|---|---|---|
| **I0 Walking Skeleton** | Oberflächen `Root`, `Auth`, `App` (Kern), `Instance` (Kern), `Integrations` (Route ohne Provider), `V1` (nur Schema-Gerüst, keine Route); Trailing-Slash, 404/405-Körper, Fehlerformen (§3.5); `endpoints.json` + `RouteInventoryTests` (nur I0-Zeilen); OpenAPI-Dokument `internal` + `contract-check`-Pipeline (§3.14/§3.15); Parity-Harness mit den 5 I0-Endpunkten EP-0077, EP-0048, EP-0122, EP-0123, EP-0187 (`15` §3.6.7) | **37** (EP-0001, -0002, -0017…-0019, -0023, -0040, -0047…-0049, -0051…-0053, -0055, -0056, -0070…-0072, -0077, -0079, -0083, -0122…-0124, -0138, -0184…-0187, -0189, -0205, -0413, -0414, -0729…-0732) | DT-GEN-01…06, DT-GEN-14, DT-AUTH-01…03, -05…-07, DT-WS-01, DT-WS-02, DT-WS-09, DT-INST-01…04, -06, DT-V1-13 | `RouteInventoryTests` (I0), Parity-Harness 5/5 grün |
| **I1 Workspace, Projekte, Konto** | Cursor-Paginator (§3.7), Rate-Limit-Policies (§3.12), Fehlertext-Katalog je Modul (§3.6), Asset-Upload-Vertrag (Direct/Proxy) | 99 | DT-GEN-07, -08, DT-AUTH-04, -08, -09, -11, DT-WS-03…05, -08, DT-PRJ-01…09, DT-AST-01…03 | Goldens aller I1-Zeilen |
| **I2 Work Items & Layouts** | Filter-Syntax (§3.8), `expand` (§3.9), Bulk (§3.10), Global-Paginator, Sanitizing | 68 | DT-GEN-10, -11, DT-WS-06, -07, DT-WI-01…11, DT-SRCH-01 (Mentions) | Goldens + `WorkItemQueryParityTests` (`02` AK-12) |
| **I3 Planung** | gruppierte Listen in Cycle-/Modul-Kontext, Archiv-Endpunkte | 87 | DT-GEN-15, DT-WI-05/-06, DT-CYC-01/-02, DT-MOD-02, DT-INT-01/-02/-06 | Goldens |
| **I4 Pages & Realtime** | Live-Endpunkte (§3.18), Binär-Endpunkte | 20 | DT-PAGE-01…07, DT-RT-01…03 | Goldens + Protokolltests (`07`) |
| **I5 Überblick** | Benachrichtigungs-Pagination „nur auf Anfrage“, Suche | 50 | DT-NOTIF-01/-02, DT-ANA-01, DT-HOME-01, DT-SRCH-01/-02 | Goldens |
| **I6 Außenwirkung & Administration** | Oberflächen `Space` und `V1` vollständig, API-Keys (§3.11), OpenAPI `v1` öffentlich + Scalar (§3.14), Webhook-Ausgang (§3.17), God-Mode-Vollausbau | 203 | DT-V1-*, DT-SPACE-*, DT-WH-*, DT-INST-05/-07/-08, DT-AI-01, DT-AUTH-10, DT-PRJ-03, DT-AST-04, DT-INT-03…05, DT-CYC-03, DT-MOD-01 | Goldens + `OpenApiDocumentTests` |
| **I7 Härtung** | `ParityHarness coverage --fail-under 100` gegen `endpoints.json` | – | – | 100 % Szenario-Abdeckung aller registrierten Zeilen |

### 1.4 Kennzahlen des Katalogs

| Oberfläche | Zeilen gesamt | registriert | nicht registriert | davon neu (ohne Original) |
|---|---|---|---|---|
| `Auth` (`/auth/`) | 41 | 7 | 34 | 4 |
| `App` (`/api/`) | 444 | 362 | 82 | 3 |
| `Instance` (`/api/instances/`) | 22 | 14 | 8 | 1 |
| `Space` (`/api/public/`) | 42 | 37 | 5 | 0 |
| `Live` (`/live/`) | 5 | 4 | 1 | 1 |
| `V1` (`/api/v1/`) | 171 | 133 | 38 | 0 |
| `OpenApi` (`/api/schema/…`) | 4 | 4 | 0 | 1 |
| `Integrations` (`/api/integrations/`) | 1 | 1 | 0 | 1 |
| `Root` (`/`) | 2 | 2 | 0 | 0 |
| **Summe** | **732** | **564** | **168** | **11** |

Die 168 nicht registrierten Zeilen setzen sich zusammen aus 85 Matrix-Zeilen ohne Analyse-Gegenstück (§4.25: 71 Methoden-Nebenprodukte DT-GEN-03, 8 nicht geroutete v1-Estimate-Methoden DT-V1-01, 3 per `http_method_names` ausgeschlossene v1-Methoden DT-V1-02, 3 Auth-Nebenprodukte DT-AUTH-01) und 83 Zeilen mit Original-ID: 43 Auth-/Konto-Routen, die ADR-008 ersetzt (DT-AUTH-01), 1 Admin-Sign-up (DT-INST-03), 13 PUT-Duplikate (DT-GEN-01), 6 defekte Zuordnungs-Aktionen (DT-GEN-02), 2 Archiv-Nebenaktionen (DT-GEN-03), 7 Legacy-Asset-Routen (DT-AST-01), 10 tote oder defekte Routen (DT-GEN-15 ×3, DT-INT-01 ×2, DT-WS-01, DT-WS-05, DT-WI-10, DT-SPACE-01, DT-V1-03) und `POST /live/convert-document/` (nur noch Management-Port, DT-RT-02).

### 1.5 Lesehilfe: ID-Schemata

| Schema | Bedeutung | Beispiel |
|---|---|---|
| `EP-nnnn` | Katalogzeile dieses Dokuments (stabil; neue Zeilen werden angehängt, nie umnummeriert) | `EP-0178` = `GET {P}/issue-labels/` |
| `<Dok>:<ID>` | Original-Zeile in einem Analyse-Dokument; `neu:<Quelle>` = Route ohne Original | `A04:L1`, `neu:N-01` |
| `DT-<Bereich>-nn` | Zeile der Entscheidungstabelle §3.13 (Anker im Dokument; Verweis aus `deviations.yaml` als `decision: "04#DT-…"`, `15` §3.6.5) | `DT-PAGE-07` |
| `DEV-API-nn` | Abweichungs-ID in `tests/contracts/deviations.yaml` für Abweichungen aus diesem Dokument (01–04 vergeben in `05`/`02`, 05–62 hier) | `DEV-API-17` |
| `SEC-nn`, `HARM-nn` | Sicherheitskorrekturen und Harmonisierungen aus `05` §3.18 (hier nur referenziert) | `SEC-21` |
| `N-nn` | Auth-Ziel-Endpunkte aus `05` §3.2 | `N-13` |

---

## 2. Entscheidungen (D04-ADR-01 ff.)

Spalte „ab“ = Inkrement der ersten Umsetzung. Alle Entscheidungen präzisieren die genannten ADRs aus `00`/`01` bzw. Festlegungen aus `02`/`05`, ohne ihnen zu widersprechen.

| ID | Belang | Entscheidung | Alternativen (verworfen) | Begründung | ab |
|---|---|---|---|---|---|
| **D04-ADR-01** | Katalog als einzige Soll-Liste | `_data/endpoints.json` ist die **einzige** maschinenlesbare Soll-Liste aller Routen. `RouteInventoryTests` (`tests/Plane.AppHost.Tests/Routing/`) vergleicht die `EndpointDataSource` der Hosts `Plane.Api` und `Plane.Realtime` mit allen Zeilen `registered = true` bis zum aktuellen Inkrement (`CURRENT_INCREMENT`, `15` §3.16): jede registrierte Zeile muss existieren (Methode + Route-Template), keine Route darf ohne Katalogzeile existieren, jede Zeile `registered = false` muss 404/405 wie `target_status` liefern. Neue Routen (auch Pakete ab W1) werden **zuerst** im Katalog ergänzt (neue `EP`-Nummer am Ende). | Katalog nur als Markdown; Routen per Attribut-Scan dokumentieren | Agenten arbeiten parallel; nur ein maschinell geprüfter Katalog verhindert stille Abweichungen (01 P2/P3). Der Parity-Harness nutzt dieselbe Datei für `coverage`. | I0 |
| **D04-ADR-02** | Portierungskriterium | Eine Original-Route wird registriert, wenn **mindestens eine** Bedingung gilt: (a) ein Original-Client (web, admin, space, live, `packages/services`) ruft sie auf; (b) sie ist die einzige Trägerin einer CE-ID („nur API“-Features: CE-WS-007, CE-PRJ-010, CE-PRJ-033, CE-HOME-007, CE-ANA-009, CE-WH-010, CE-SPACE-006, CE-WI-046, CE-INST-004); (c) sie gehört zur Public API v1 (öffentlicher Vertrag, CE-API-*); (d) sie ist im Original funktionsfähig und vervollständigt eine Ressource, deren übrige Methoden portiert werden. **Nicht** registriert werden: tote oder defekte Routen ohne fachliche Funktion (immer 4xx/5xx), PUT-Duplikate neben PATCH, Methoden-Nebenprodukte, im Original nicht geroutete Handler, Routen, deren Funktion ADR-008 ersetzt. | alle Original-Routen registrieren (auch defekte); nur Routen mit Client-Aufrufer (02 §3.3.1 Regel 6 wörtlich) | Die CE wird vollständig umgesetzt (Auftrag), „nur API“-Features sind CE-Funktionen; Regel 6 aus `02` gilt für alle übrigen Fälle unverändert. Das Kriterium ist je Zeile in Spalte „Abw./DT“ nachvollziehbar. | I0 |
| **D04-ADR-03** | Antwort nicht registrierter Routen | Nicht registrierte Routen bekommen **keine** Stub-Endpunkte: existiert der Pfad mit einer anderen Methode, antwortet das Routing mit 405 `{"detail": "Method \"<METHOD>\" not allowed."}`, sonst 404 `{"error": "Page not found."}` (beides `StatusCodeBodiesMiddleware`, `02` §3.3.1 Regel 5). `/live/*` antwortet bei unbekannten Pfaden 404 `{"message": "Not Found"}` (`07` §3.4). | Stubs mit 410 Gone; eigene Fehlertexte je entfallener Route | DRF-Verhalten für fehlende Methoden bleibt erhalten; kein toter Code im Ziel; Contract-Tests prüfen den Status je Zeile. | I0 |
| **D04-ADR-04** | v1-Adapter (`Plane.PublicApi`, Regel R6) | v1-Endpunkte liegen in `src/modules/PublicApi/Plane.PublicApi/Endpoints/V1/V1<Ressource>Endpoints.cs` (Hilfsklassen je Ressource unter `V1/<Ressource>/`, z. B. `V1FilterParameterGuard`, `16` §5.5), rufen **öffentliche Contract-Commands/-Queries** der Fach-Module (Records in `Plane.<M>.Contracts/Commands/` bzw. `/Queries/`, implementieren `ICommand<Result<T>>`/`IQuery<T>` aus `Plane.BuildingBlocks`; Handler bleiben `internal` im Fach-Modul) und bilden Ergebnisse über `V1<Ressource>Mapper` (Mapperly) auf die v1-Serializer-Formen ab. Der Adapter darf v1-spezifische **Vorprüfungen per Query** (z. B. `external_id`-Duplikat → 409 mit `id`) und eine **Fehlerumformung** (`V1ErrorMap`) vornehmen, aber keine Schreiblogik. Für Work Items nutzt er die Fassade `IWorkItemCommands` (`16` E-18), die selbst auf denselben Contract-Commands aufsetzt. | v1-Endpunkte im jeweiligen Fach-Modul (`Endpoints/V1/`); Handler `public` | R1/R6/R9 aus `01` §5.2 bleiben erfüllt (kein Zugriff auf interne Typen anderer Module); eine Geschäftslogik für App und v1; die Contract-Commands sind zugleich die Andockstelle für H3/H4 (`16`). Prüfpunkt Spike S0: Mediator-Source-Generator registriert Handler für Commands aus fremden Contracts-Assemblies (Ergänzung zu `17` Z-01). | I6 (Gerüst I0) |
| **D04-ADR-05** | Endpoint-Klassen-Schnitt | Je Modul, Oberfläche und Ressource **eine** Klasse `internal static class <Ressource>Endpoints` mit `Map(PlaneEndpointRouteBuilder)` (`02` D02-ADR-23); Ablage `Endpoints/<Oberfläche>/<Ressource>Endpoints.cs`; Namen laut Spalte „Ziel: Klasse“ in §4. Jede Route trägt `.WithOriginalContract("<Dok>:<ID>")` mit der Original-ID aus §4 (für neue Routen `neu:<Quelle>`) und `.WithName("<EP-nnnn>")` (OpenAPI-/Routing-Name, eindeutig). Alias-Pfade (`issues`↔`work-items`, `inbox-issues`↔`intake-issues`, `inboxes`↔`intakes`, v1 `project-members`↔`members`, v1 `issue-attachments`↔`attachments`) werden als zweite Route auf **denselben** Handler registriert (`.MapAlias(...)`, §5.2). | eine Klasse je Modul; Controller | kleine Dateien, konfliktarme Merges, 1:1-Rückverfolgbarkeit Original ↔ Ziel | I0 |
| **D04-ADR-06** | Statuscodes und Fehler | Erfolgs- und Fehlerstatus **je Endpunkt wie Original** (Spalte „Status Orig→Ziel“; Abweichungen nur über DT-Zeilen). Fehlerkörper ausschließlich über `PlaneErrors` (`02` §3.8) in den Formen von §3.5; Texte als Konstanten in `src/modules/<M>/Plane.<M>/Errors/<M>ErrorTexts.cs` (§3.6). Golden-Files sind für Texte maßgeblich, `documented_bodies` in `endpoints.json` ist die Vorlage. | einheitliche ProblemDetails; Texte inline im Handler | Frontend wertet `error`/`detail`/`error_code` wörtlich aus (ADR-016); zentrale Konstanten erlauben Branding-Ersatz (§3.20) und Katalogtests. | I0 |
| **D04-ADR-07** | Pagination je Endpunkt | Jeder Listen-Endpunkt hat genau einen Modus aus `endpoints.json` (`pagination`): `cursor`, `cursor-grouped`, `cursor-when-requested`, `cursor-required`, `global` oder keiner (unpaginiert). Deklaration per `.WithPagination(PaginationMode.X, defaultPerPage)` (§5.1); Mechanik `02` §3.10/§3.11.6. | Pagination für alle Listen erzwingen | Original paginiert uneinheitlich; Frontend-Stores erwarten die jeweilige Form (Liste vs. Envelope). | I1 |
| **D04-ADR-08** | Filter-Syntax | Zwei Eingabeformen, ein AST (`02` D02-ADR-14): Legacy-Query-Parameter (`A04` §2.18.1) und Rich-Filter `filters=<JSON>` (`A04` §2.18.2) **nur** an den Endpunkten aus §3.8 (Tabelle); v1 akzeptiert keine Rich-Filter (Original-400 über `IV1FilterParameterBinding`, `16` E-19). Neue Filterfelder nur über `IFilterFieldProvider`. | eigene Filtersprache je Endpunkt; OData | Parität + B6-Andockstelle | I2 |
| **D04-ADR-09** | `expand`/`fields` | App: `expand` nur mit den Werten aus §3.9 (Allowlist je Endpunkt, Registry `IExpandProvider`, `16` E-07); `fields` wird akzeptiert und ignoriert (DT-GEN-09). v1: dynamische Felder wie Original (`A05` §2.1.6) an den Endpunkten mit `f/e ✓` (§3.9). | generische GraphQL-artige Projektion | Parität; Erweiterung ohne Umbau für A1/A9 | I2/I6 |
| **D04-ADR-10** | Bulk-Operationen | Nur die Bulk-Endpunkte des Originals (§3.10); jede Bulk-Operation läuft in **einer** Transaktion über die regulären Einzel-Commands (Activity, Outbox, Kaskaden; DT-WI-05). Kein generischer Batch-Endpunkt in der CE. | `/api/batch`; Massen-SQL wie Original | Konsistenz der Activity/Webhooks; Parität des Vertrags | I1/I2 |
| **D04-ADR-11** | Idempotenz | Keine Idempotency-Key-Semantik in der CE (Original kennt sie nicht); der Header `Idempotency-Key` wird **ignoriert** (reserviert für H3, §6). Idempotenz je Methode laut §3.10.2 (PUT entfällt, DELETE idempotent mit Original-Status, POST nicht idempotent außer den dort genannten „Toggle“-Endpunkten). Eingehende Integrations-Webhooks sind über die Delivery-ID idempotent (Inbox, `16` §3.4.3). | Idempotency-Key für alle POST | kein Vertrag im Original, Frontend sendet keinen Key; Andockstelle bleibt frei | I0 |
| **D04-ADR-12** | API-Keys | Header `X-API-Key` (Groß-/Kleinschreibung beliebig), Klartextformat und Speicherung nach `05` §3.12 (SHA-256 `token_hash`), Workspace-Bindung, Rate-Limit-Partition `token_hash`, API-Activity-Log; Bearer (H1) registriert, deaktiviert (DT-V1-13). Details §3.11. | Bearer-Tokens für Menschen | Vertrag mit Bestandsintegrationen; ADR-008 erlaubt API-Keys | I6 (Schema I0) |
| **D04-ADR-13** | Rate-Limits | Policies aus `02` §3.13; Zuordnung je Oberfläche und Sonder-Endpunkt in §3.12. | Limits nur im Gateway | Parität CE-API-002/CE-AUTH-026 | I0/I1/I6 |
| **D04-ADR-14** | OpenAPI | Zwei Dokumente mit `Microsoft.AspNetCore.OpenApi` (ADR-051): `v1` (öffentlich, nur Oberfläche V1, Pfade/Methoden/`operationId`s/Tags wie das Original-Schema, das einmalig per `manage.py spectacular` am `ORIGINAL_SHA` exportiert und als `tests/contracts/openapi/v1.original.json` eingecheckt wird) und `internal` (App, Space, Instance; nur Dev/Test). Beide werden zur Build-Zeit nach `src/hosts/Plane.Api/openapi/{v1,internal}.json` geschrieben und eingecheckt; CI bricht bei Drift. | Swashbuckle/NSwag; OpenAPI zur Laufzeit generieren | lizenz- und airgap-sauber; Drift sichtbar im PR | I0 (internal), I6 (v1) |
| **D04-ADR-15** | TypeScript für Angular | **Kein** generierter Client als Primärquelle (ADR-047): Services werden 1:1 aus dem Original portiert. Aus `internal.json`/`v1.json` erzeugt `openapi-typescript` 7.x in `frontend/tools/contract-check/` Typen (`generated/internal.d.ts`, `generated/v1.d.ts`), die per Typ-Tests gegen `libs/shared/types` geprüft werden (§3.15). | `ng-openapi-gen`/NSwag-Client; OpenAPI aus TS-Typen | Store-Port ohne Umbau; Drift wird automatisch erkannt | I0 |
| **D04-ADR-16** | Contract-Tests | Jede registrierte Katalogzeile hat ≥ 1 Parity-Szenario (`tests/contracts/scenarios/<modul>/<szenario>.yaml`, `15` §3.6.2); die Zuordnung Schritt → Zeile erfolgt über Methode + Pfad gegen `endpoints.json` (`path`, Platzhalter aufgelöst), Alias-Zeilen sind über ihren eigenen Pfad unterscheidbar; jede nicht registrierte Zeile ist in `RouteInventoryTests` (Status 404/405) abgedeckt; jede DT-Zeile mit Vertragswirkung hat einen `deviations.yaml`-Eintrag mit `decision: "04#DT-…"`. | Contract-Tests nur für Stichproben | Z2 aus `15` §1.1 („jeder Endpunkt des Katalogs“) | I0 ff. |
| **D04-ADR-17** | Branding in Verträgen | Nach außen sichtbare **Texte** (Fehlermeldungen mit „Plane“, E-Mail-Betreffs, OpenAPI-Titel/Kontakt, Seitentitel der Scalar-UI) zeigen „funk.“ (ADR-009B, Abweichungen `BRAND-API-*`); **Protokollbezeichner** (`X-Plane-*`-Header, Token-Präfixe `plane_api_`/`plane_wh_`, Cookie `session-id`, JSON-Feldnamen, `error_message`-Schlüssel, Rollenwerte) bleiben als interne Bezeichner im Sinne von ADR-009B unverändert. | alles umbenennen; nichts umbenennen | Bestandsintegrationen und portierter Frontend-Code bleiben lauffähig; sichtbare Marke wie verlangt | I0 |
| **D04-ADR-18** | Vertragsevolution | In der CE nur **additive** Vertragsänderungen nach Merge (neue optionale Felder, neue Endpunkte unter reservierten Präfixen `16` §3.2.2); keine `/api/v2/`-Oberfläche (H3, W9); Entfernen/Umbenennen nur per DT-Zeile vor dem ersten produktiven Release. | Versionierung je Endpunkt | Paketfähigkeit ohne Umbau (01 P7), Parität | I0 |
| **D04-ADR-19** | Entscheidungsregeln für Original-Fehler | Kategorien S/F/T/Q/A/K (§3.13): **S** Sicherheitslücke → immer korrigieren; **F** funktionaler/sichtbarer Fehler → korrigieren und als `DEV-API-*` dokumentieren (Auftraggeber-Entscheidung Z-12, `17`); **T** tote/defekte/redundante Route → nicht registrieren; **Q** Vertrags-Quirk, auf den Clients bauen → 1:1; **A** ADR-bedingt → entfällt/angepasst; **K** technische Korrektur ohne Vertragswirkung → ohne `deviations`-Eintrag. | alles 1:1; alles korrigieren | Vorgabe des Auftrags („Sicherheitslücken immer, sichtbare Fehler korrigieren und dokumentieren“) und Z-12 | I0 |
| **D04-ADR-20** | Webhook-Ausgang als Vertrag | Vertrag gegenüber Empfängern (Ereignisse, Header, Body, Signatur, Retry) wie `06` §3.14 (Projektion der Integration-Events); dieses Dokument legt nur die vertragliche Sicht und die auslösenden Endpunkte fest (§3.17, §4.27). | eigenes Webhook-Design | `06` ist Fachdokument für Webhooks (01 Anhang A) | I6 |
| **D04-ADR-21** | Live-Endpunkte | Pfade, Methoden und Antworten wie `07` §3.4; `POST /live/convert-document/` nur auf dem Management-Port (D07-ADR-19), `/live/events/` (H6) ab I0. | Node-Sidecar | ADR-002, SEC-39 | I0/I4 |

---

## 3. Detaildesign

### 3.1 Oberflächen und URL-Struktur

#### 3.1.1 Oberflächen

Die Mechanik (`ApiSurface`, `PlaneEndpointRouteBuilder`, `SurfaceConventions`) legt `02` §3.3 fest. Die folgende Tabelle ordnet jeder Oberfläche die vertraglichen Eigenschaften zu, die dieses Dokument festlegt (Spalten „Fehlerprofil“ und „OpenAPI-Dokument“ sind die Werte, die `SurfaceConventions.Apply` setzt).

| Oberfläche | Präfix | Host | Authentisierung (Schema) | CSRF | Rate-Limit-Default | Fehlerprofil | OpenAPI-Dokument | Zeilen (reg.) | ab |
|---|---|---|---|---|---|---|---|---|---|
| `Root` | `/` | `Plane.Api` | keine | – | keins | – | – | 2 (2) | I0 |
| `Auth` | `/auth/` | `Plane.Api` | Session-Cookie `session-id` bzw. anonym | Origin + Token (`05` §3.10) | `anon`; Auth-Endpunkte `authentication` | Redirect (`PlaneErrors.Redirect`) für Browser-Flows, sonst Coded | – | 41 (7) | I0 |
| `App` | `/api/` | `Plane.Api` | Session | Origin + Token für unsichere Methoden | `anon` (nur anonym) | App (`error`/`detail`/coded) | `internal` | 444 (362) | I0 |
| `Instance` | `/api/instances/` | `Plane.Api` | Session (Admin: zusätzlich `Plane:Admin`-Rolle, `05` §3.6) | wie App | `anon` | App | `internal` | 22 (14) | I0 |
| `Space` | `/api/public/` | `Plane.Api` | Session optional (anonym erlaubt, wo Original anonym erlaubt) | wie App | `anon` | App | `internal` | 42 (37) | I6 |
| `V1` | `/api/v1/` | `Plane.Api` | `ApiKey` (Header `X-API-Key`); `Bearer` (H1, deaktiviert) | keine (kein Cookie akzeptiert) | `api_key` + `X-RateLimit-*` | V1 (App + `A05` §2.1.4) | `v1` (öffentlich) | 171 (133) | I6 |
| `OpenApi` | `/api/schema/` | `Plane.Api` | keine (Schalter `Plane:OpenApi:Enabled`; `internal` nur Development/Test) | – | `anon` | – | – | 4 (4) | I0/I6 |
| `Integrations` | `/api/integrations/` | `Plane.Api` | Signatur des Providers (`IWebhookIngress`, `16` E-25) | keine | `integration_webhook` (600/min) | Plain | – | 1 (1) | I0 |
| `Live` | `/live/` | `Plane.Realtime` | Session-Cookie (`07` §3.5) | – | keins (Verbindungs-Limits `07`) | `{"message": …}` | – | 5 (4) | I0/I4 |

`OpenApi` und `Live` sind keine `ApiSurface`-Werte aus `02`: `OpenApi` wird in `Plane.PublicApi` über `MapOpenApi()`/Scalar unterhalb von `Root` registriert (§3.14), `Live` in `Plane.Realtime` (`07` §3.4). Für Katalog und `RouteInventoryTests` werden sie als eigene Oberflächen geführt.

#### 3.1.2 Pfadregeln

1. **Pfade wie Original.** Alle Pfadsegmente (inkl. Alias-Varianten, Schreibweisen wie `issue-labels`, `user-favorite-projects`, `last-visited-issues`) werden wörtlich übernommen. Umbenennungen gibt es nicht (D04-ADR-18); `work-items`-Varianten existieren nur dort, wo das Original sie routet.
2. **Trailing Slash** optional, ohne Redirect, für alle Methoden (`02` D02-ADR-07). Route-Templates in `endpoints.json` stehen ohne Präfix und ohne abschließenden Slash (`route_template`); das Präfix ergibt sich aus der Oberfläche.
3. **Pfadparameter** behalten den Original-Namen (`slug`, `project_id`, `pk`, `issue_id`, `work_item_id`, `cycle_id`, `module_id`, `anchor`, `asset_id`, `entity_id`, `token`, `provider`, `connection_id`, `project_identifier`, `issue_identifier`, `uidb64`). Constraints: alle UUID-Parameter `:guid`; `slug`, `anchor`, `token`, `provider`, `project_identifier` und `issue_identifier` ohne Constraint (`issue_identifier` wird im Handler geparst, damit ein nicht ganzzahliger Wert wie im Original 400 `{"error": "Invalid issue identifier"}` ergibt; negative Zahlen sind wie im Original erlaubt). Ein UUID-Pfadparameter mit ungültigem Format trifft keine Route → 404 `{"error": "Page not found."}` (Original: Django-`<uuid:…>`-Konverter, ebenfalls 404) – kein Unterschied.
4. **Workspace-Auflösung.** Jede Route mit `{slug}` trägt `.ResolveWorkspaceOrNotFound()` (`02` §3.5); ein unbekannter Slug ergibt den Original-Status des jeweiligen Endpunkts (meist 403 `{"error": "You don't have the required permissions."}` aus der Permission-Prüfung, bei `AllowAnonymous`-Routen 404) – maßgeblich ist das Golden.
5. **Alias-Pfade** (D04-ADR-05): `issues`↔`work-items` (App: `{P}/issues/…`/`{P}/work-items/…` laut Katalog, v1 vollständig), `inbox-issues`↔`intake-issues`, `inboxes`↔`intakes`, v1 `project-members`↔`members` (nur v1), v1 `issue-attachments`↔`attachments`. In §4 tragen Alias-Zeilen den Vermerk „(Alias)“ und denselben Handler; Contract-Szenarien decken jede Alias-Zeile separat ab.
6. **Reservierte Präfixe** für Pakete (`16` §3.2.2) werden in der CE **nicht** registriert; `RouteReservationTests` (`16`) prüft, dass keine CE-Route in einen reservierten Präfix fällt und dass ein Request dorthin 404 liefert.

#### 3.1.3 Original-ID und Routenname

`.WithOriginalContract("<Dok>:<ID>")` trägt die Original-ID aus Spalte „Original-ID“ (bei mehreren IDs die erste; Alias-Zeilen dieselbe ID wie die Hauptzeile). `.WithName("EP-nnnn")` ist eindeutig und dient als Routenname und als Schlüssel für `RouteInventoryTests`; für v1-Routen ist der OpenAPI-`operationId` getrennt davon die Original-`operationId` (§3.14.3).

#### 3.1.4 Herleitung des Katalogs (nachvollziehbar, wiederholbar)

| Schritt | Eingang | Regel |
|---|---|---|
| 1 | `05` Anhang B / `05-permission-matrix.json` (672 Zeilen, AST-Extraktion aller URL-Konfigurationen) | Basismenge Methode × Pfad |
| 2 | Analyse-Inventare A03, A04, A05, A06, A12 (571 + 37 + 7 + 4 Zeilen) | Zuordnung per Methode × normalisiertem Pfad (Parameter-Namen ignoriert); Alias-Regeln aus §3.1.2 Nr. 5 |
| 3 | Matrix-Zeilen ohne Analyse-Gegenstück (85) | Methoden-Nebenprodukte → §4.25 (DT-GEN-03) |
| 4 | Analyse-Zeilen ohne Matrix-Gegenstück | Auth-Routen (A06 §2.1, außerhalb der Matrix), Live-Routen (A12), OpenAPI- und Root-Routen |
| 5 | neue Ziel-Endpunkte | `05` N-01, N-02, N-06, N-07, N-13 (`/auth/…`), `{W}/active-cycles/` (Frontend-Aufruf ohne CE-Backend, DT-GEN-16), `{AV2}/upload/{token}/` + `{AV2}/files/{token}` (Proxy-Upload, `14`), `/api/integrations/{provider}/webhooks/{connection_id}/` (F1), `/live/events/` (H6) |
| 6 | Portierungskriterium (D04-ADR-02) + DT-Tabelle (§3.13) | `registered`, `target_status`, `dt` |
| 7 | CE-Katalog (507 IDs) | CE-IDs je Zeile aus A03–A05-Spalte „CE“ bzw. Feature-Katalog-Quellen; Rest in §4.28 |

### 3.2 Methoden und Statuscodes

#### 3.2.1 Methoden

| Methode | Semantik im Vertrag | Regel im Ziel |
|---|---|---|
| `GET` | lesen, ohne Seiteneffekt **außer** den Original-Seiteneffekten `recent_visited_task` (Recents, `06`), `last_used` des API-Keys, Lesemarker der Benachrichtigungen (nur wo Original) | Seiteneffekte als Integration-Event/Job nach Antwort (`06`), nie im Read-Pfad blockierend |
| `POST` | anlegen bzw. Aktion (Beispiele: `/archive/`, `/transfer-issues/`, `/leave/`, `/join/`, `/bulk-archive-issues/`, `/mark-read/`; vollständig je Zeile in §4) | Status je Endpunkt laut Katalog (Original nutzt bei Aktionen häufig 200 statt 201) |
| `PATCH` | partielles Update; `Optional<T>`-Binding unterscheidet „nicht gesendet“ und `null` (`02` D02-ADR-10) | Pflichtregeln aus Original-Serializer |
| `PUT` | nur wo das Original **ausschließlich** PUT anbietet (Präferenzen/Einstellungen laut Katalog, z. B. Instanz-Konfiguration, Projekt-Mitglieder-Präferenzen) | PUT-Duplikate neben PATCH entfallen (DT-GEN-01) |
| `DELETE` | löschen (Soft-Delete wie Original, `03`); Bulk-Löschen mit Body (`DELETE {P}/bulk-delete-issues/`, Body `{"issue_ids": [...]}`) | DELETE-Bodies werden gelesen (Kestrel erlaubt Body bei DELETE; `02` Binding `FromBody` auch für DELETE) |
| `OPTIONS`/`HEAD` | nicht Teil des Vertrags; `HEAD` wird von ASP.NET Core für `GET`-Routen nicht automatisch beantwortet | 405 (Original: DRF beantwortet `OPTIONS` mit Metadaten – von keinem Client genutzt; Regel wie DT-GEN-03) |

#### 3.2.2 Erfolgsstatus

Grundregel: `GET` 200, `POST` (anlegen) 201, `PATCH`/`PUT` 200, `DELETE` 204. Spalte „Status Orig→Ziel“ in §4 enthält den Status je Zeile. Abweichungen von der Grundregel im Original sind Vertragsbestandteil (1:1); die folgende Liste ist vollständig aus `endpoints.json` abgeleitet und wird von `RouteInventoryTests.SuccessStatusMatchesCatalog` geprüft (Szenarien prüfen den Status je Zeile):

| Abweichung | Endpunkte (EP) |
|---|---|
| `POST → 200` statt Grundregel | EP-0002, EP-0076, EP-0079, EP-0095, EP-0100, EP-0102, EP-0107, EP-0128, EP-0169, EP-0173, EP-0192, EP-0196, EP-0217, EP-0242, EP-0255, EP-0258, EP-0265, EP-0270, EP-0316, EP-0318, EP-0327, EP-0341, EP-0374, EP-0379, EP-0388, EP-0390, EP-0401, EP-0418, EP-0424, EP-0427, EP-0430, EP-0459, EP-0479, EP-0497, EP-0502, EP-0504, EP-0511, EP-0551, EP-0554, EP-0555, EP-0596, EP-0608, EP-0617, EP-0618, EP-0628, EP-0633, EP-0720, EP-0725, EP-0726, EP-0727 |
| `GET → 302` statt Grundregel | EP-0017, EP-0018, EP-0019, EP-0243, EP-0416, EP-0419, EP-0421, EP-0429, EP-0432, EP-0462, EP-0629, EP-0634 |
| `POST → 302` statt Grundregel | EP-0023, EP-0040, EP-0083 |
| `DELETE → 200` statt Grundregel | EP-0075, EP-0175, EP-0256, EP-0350, EP-0503, EP-0505 |
| `POST → 204` statt Grundregel | EP-0092, EP-0111, EP-0114, EP-0116, EP-0118, EP-0120, EP-0133, EP-0150, EP-0201, EP-0212, EP-0221, EP-0282, EP-0400, EP-0406, EP-0417, EP-0420, EP-0431, EP-0460, EP-0461, EP-0546, EP-0594, EP-0604 |
| `PATCH → 201` statt Grundregel | EP-0207, EP-0209 |
| `PATCH → 204` statt Grundregel | EP-0227, EP-0244, EP-0267, EP-0422, EP-0425, EP-0433, EP-0463, EP-0557, EP-0619, EP-0621, EP-0630, EP-0635 |
| `POST → 202` statt Grundregel | EP-0729 |

Grundregel-konforme Zeilen sind nicht aufgeführt. `GET → 101` (WebSocket-Upgrade) betrifft EP-0410 (`/live/collaboration`) und EP-0414 (`/live/events/`). Fehlerstatus sind in §3.5 geregelt; der jeweils dokumentierte Fehlerkörper steht in `endpoints.json` (`documented_bodies`).

### 3.3 Request-Konventionen

| Belang | Regel | Quelle / Mechanik |
|---|---|---|
| Content-Type | `application/json` für Bodies; `multipart/form-data` nur an den Original-Multipart-Endpunkten: Legacy-Datei-Uploads entfallen (DT-AST-01), verbleibend `POST {P}/issues/{issue_id}/issue-attachments/` (Legacy-Upload `A04:K8`, Felder `asset`, `attributes`) und der Proxy-Upload `POST {AV2}/upload/{token}/` (`14`) | `02` §3.9 |
| Body-Größe | 413 `{"error": "REQUEST_BODY_TOO_LARGE", "detail": "The size of the request body exceeds the maximum allowed size."}` bei Überschreitung von `Plane:Uploads:MaxFileSizeBytes` (Alias `FILE_SIZE_LIMIT`) – 1:1 `RequestBodySizeLimitMiddleware` | `02` §3.4.1 Nr. 4 |
| v1-Bodies | `POST`/`PUT`/`PATCH` müssen ein JSON-Objekt oder -Array sein, sonst 400 `{"detail": "Request body must be a JSON object or array."}` | `A05` §2.1.1; `V1BodyShapeFilter` |
| JSON-Namen | snake_case wie Original; unbekannte Felder werden ignoriert (DRF-Verhalten) | `02` §3.9 |
| `PATCH`-Semantik | `Optional<T>`: nicht gesendet ≠ `null`; nur gesendete Felder ändern; Activity-Diff nur über gesendete Felder | `02` D02-ADR-10 |
| Validierung | Formprüfung per `.Validate<TRequest>()` mit DRF-Feldfehler-Körper `{"<feld>": ["…"]}` und Original-Texten (Beispiele: `This field is required.`, `Ensure this field has no more than 255 characters.`, `"<x>" is not a valid choice.` …); fachliche Prüfungen im Handler | `02` D02-ADR-09 |
| Datum/Zeit | ISO 8601; Datumsfelder `YYYY-MM-DD`; Zeitstempel in UTC mit `Z`-loser Offset-Form wie DRF (`2026-01-01T10:00:00.123456Z` – Converter `02` AK-09); Nutzer-Zeitzone für `__date`-Filter (`TimezoneMiddleware`) | `02` §3.9 |
| UUIDs | Kleinbuchstaben mit Bindestrichen; ungültige UUIDs in **Bodies** → 400 Feldfehler `["\"<x>\" is not a valid UUID."]`; in **Query-CSV-Filtern** werden ungültige Werte wie im Original verworfen | `A04` §2.18.1 |
| Query-Listen | kommagetrennt (`state=a,b`); Literal `null` wird in Legacy-Filtern ignoriert; Rich-Filter als URL-kodiertes JSON (`filters=…`) | §3.8 |
| HTML-Felder | `description_html`, `comment_html` laufen durch `HtmlSanitizer` (Allowlist aus Original), `description_binary` Base64 ≤ 10 MB und Yjs-dekodierbar (DT-WI-11) | `02` §3.9, `07` |

### 3.4 Antwort-Konventionen

1. **Formen:** Objekt, Array oder Pagination-Envelope (§3.7) **wie Original je Endpunkt**; die Frontend-Stores unterscheiden nach Endpunkt, nicht nach Form. Die Antwort-DTOs sind `record`s mit den Original-Feldnamen; Felder, die das Original nur unter Bedingungen liefert (z. B. fehlende Annotationen bei `IssueSerializer`, DT-WI-06), werden über `[JsonIgnore(Condition = WhenWritingNull)]` **nicht** generell ausgelassen, sondern genau dort, wo das Golden sie nicht enthält.
2. **Zähler** (z. B. `sub_issues_count`, `link_count`, `attachment_count`, `member_count`; maßgeblich das Golden je Endpunkt) wie Original, inkl. `null` statt `0` (DT-GEN-10).
3. **`*_detail`-Felder und `expand`** liefern Lite-Objekte (`UserLite`, `StateLite`, `ProjectLite`, `WorkspaceLite`) mit den Original-Feldlisten (`A04` §2.16, `A05` §2.4).
4. **Asset-URLs** (`avatar_url`, `cover_image_url`, `logo_url`, `asset_url`) zeigen auf `/api/assets/v2/…`-Auslieferungsendpunkte (302 auf presigned URL bzw. Proxy-Download, `14`), nie direkt auf den Objektspeicher.
5. **Header:** `Content-Type: application/json`; `Vary: Cookie` auf App/Space/Instance; `X-Frame-Options: DENY`; `Cache-Control` **nur** an den Endpunkten des Originals:

| EP | Endpunkt | `Cache-Control` | Deklaration |
|---|---|---|---|
| EP-0048 | `GET /api/users/me/` | `private, max-age=12` | `.WithCacheControl("private, max-age=12")` |
| EP-0053 | `GET /api/users/me/settings/` | `private, max-age=12` | dto. |
| EP-0059 | `GET /api/users/me/profile/` | `private, max-age=12` | dto. |
| EP-0077 | `GET /api/instances/` | `private, max-age=12` | dto. |
| EP-0057 | `GET /api/timezones/` | `max-age=7200` (+ `Expires`) | `.WithCacheControl("max-age=7200")` |

   Serverseitige Response-Caches (`@cache_response` an Estimates, Labels, States, Workspace-Labels/-Estimates, Einladungen, Mitglieder, Instanz-Admins/-Konfiguration) entfallen; stattdessen benannte Lesemodelle mit Tag-Invalidierung (DT-GEN-07, `02` §3.12).
6. **Sortierung:** Default-Sortierung je Endpunkt wie Original; zusätzlich `id DESC` als letzter Tiebreaker (DT-GEN-08, `DEV-PAG-001`).

### 3.5 Fehlerformen

Alle Fehlerkörper entstehen über `PlaneErrors` (`02` §3.8.1). Welche Form ein Endpunkt bei welchem Fehler liefert, ist **Vertragsbestandteil** (DT-GEN-05, 1:1).

| Form | Körper | typische Herkunft im Original | Fabrik |
|---|---|---|---|
| Plain | `{"error": "<Text>"}` | explizite `Response({"error": …})` in Views; Permission-Fehler der App-Permissions (`allow_permission`) | `PlaneErrors.Plain` |
| Plain + Extra | `{"error": "<Text>", "id": "<uuid>"}` | v1-Duplikate per `external_id` (409) | `PlaneErrors.PlainWith` |
| Detail | `{"detail": "<Text>"}` | DRF-Ausnahmen: 401 `Authentication credentials were not provided.`, 403 `You do not have permission to perform this action.`, 404 `No <Model> matches the given query.`, 405, Pagination-Fehler, JSON-Parse-Fehler | `PlaneErrors.Detail`, `DrfNotFound` |
| Coded | `{"error_code": <int>, "error_message": "<KEY>"[, …payload]}` | `ERROR_CODES` (4091, 4100–4102, 4701, 4702, 5900) und Auth-Codes 5000–5999 | `PlaneErrors.Coded` |
| Feldfehler | `{"<feld>": ["<Text>"], …}` bzw. `{"non_field_errors": ["…"]}` | Serializer-Validierung | `PlaneErrors.Fields` |
| Filterfehler | `{"message": "<Text>", "code": "<code>"[, "errors": {…}]}` | Rich-Filter (`ComplexFilterBackend`) | `PlaneErrors.FilterError` |
| Redirect | 302 mit `error_code`/`error_message` als Query-Parameter | Auth-Flows (`/auth/…`) | `PlaneErrors.Redirect` |
| Live | `{"message": "<Text>"}` | Express-Server (`/live/…`) | `LiveErrors` (`07`) |

**Permission-Ablehnung:** Die Form (Plain vs. Detail) ergibt sich aus `DenyStyle` des `PermissionDescriptor` (`05` §3.4, `02` §5.1.7); die Spalte „Permission · Ziel-Prüfung“ in §4 nennt den Key, `05` Anhang B den DenyStyle. **401 vs. 403** (D05-ADR-20): anonyme Aufrufe an Endpunkte ohne `AllowAnonymous` ergeben immer 401 `{"detail": "Authentication credentials were not provided."}` (`AuthenticatedFilter`, Original `auth_exception_handler`); ungültiger API-Key → 403 `{"detail": "Given API token is not valid"}` (DT-GEN-13, 1:1).

**Generische Fehler je Oberfläche** (immer gleich, nicht je Endpunkt aufgeführt):

| Fall | App / Instance / Space | V1 | Auth | Live |
|---|---|---|---|---|
| Pfad unbekannt | 404 `{"error": "Page not found."}` | dto. | dto. | 404 `{"message": "Not Found"}` |
| Methode nicht erlaubt | 405 `{"detail": "Method \"X\" not allowed."}` | dto. | dto. | 404 `{"message": "Not Found"}` |
| JSON ungültig | 400 `{"detail": "JSON parse error - <Text>"}` (Text `DEV-JSON-001`, `02`) | dto. | dto. | – |
| Objekt fehlt (`ObjectDoesNotExist`) | 404 `{"error": "The required object does not exist."}` | 404 `{"error": "The requested resource does not exist."}` | – | – |
| Integritätsfehler | 400 `{"error": "The payload is not valid"}` (bzw. endpunktspezifisch per `IUniqueViolationMap`) | 409/400 laut `V1ErrorMap` | – | – |
| unerwartet | 500 `{"error": "Something went wrong please try again later"}` | dto. | 302 mit `error_code` 5999 | 500 laut `07` §3.4 |
| Rate-Limit | 429 `{"error_code": 5900, "error_message": "RATE_LIMIT_EXCEEDED"}` + `Retry-After` | dto. | dto. | – |
| Body zu groß | 413 `{"error": "REQUEST_BODY_TOO_LARGE", "detail": "The size of the request body exceeds the maximum allowed size."}` | dto. | dto. | – |

### 3.6 Fehlertext-Katalog

1. Jedes Fach-Modul hat `src/modules/<M>/Plane.<M>/Errors/<M>ErrorTexts.cs` (`internal static class`, `const string`-Felder, Name = Inhalt in PascalCase, z. B. `LabelErrorTexts.LabelNameAlreadyExistsInProject = "Label with the same name already exists in the project"`). Handler verwenden **nur** diese Konstanten; String-Literale in `PlaneErrors.Plain/Detail`-Aufrufen sind durch den Analyzer `PLANE0004` (`02` §3.17) verboten.
2. Vorlage für die Konstanten ist `documented_bodies` in `endpoints.json` (aus den Analyse-Tabellen extrahiert, 1 bis n Körper je Zeile); verbindlich sind die Golden-Files des Parity-Harness (`15` §3.6.4). Abweichende Texte (Tippfehler wie „Estimate should be a estimate in the project“) bleiben wörtlich (Q).
3. Texte mit Produktnamen „Plane“ werden zu „funk.“ (§3.20); diese Konstanten tragen den Kommentar `// BRAND-API-nn`.
4. Neue Texte aus DT-Korrekturen (z. B. DT-V1-10 `Invalid limit`) sind in der DT-Zeile wörtlich festgelegt und erhalten einen `deviations.yaml`-Eintrag.
5. Test `ErrorTextCatalogTests` (je Modul, `tests/Plane.<M>.Tests/Errors/`): jeder Text aus `documented_bodies` der Zeilen des Moduls mit `registered = true` existiert als Konstante (außer Texte aus DT-Zeilen mit Kategorie F/S, deren Verhalten ersetzt wird; Ausnahmeliste `tests/Plane.<M>.Tests/Errors/replaced-texts.txt`).

### 3.7 Pagination

Mechanik `02` §3.10 (Cursor `"<per_page>:<page>:<is_prev>"`, Envelope `next_cursor`, `prev_cursor`, `next_page_results`, `prev_page_results`, `count`, `total_pages`, `total_results`, `extra_stats`, `results`), Global-Paginator `02` §3.10.4, gruppierte Work-Item-Listen `02` §3.11.6. Dieses Dokument legt den **Modus je Endpunkt** fest (`endpoints.json` → `pagination`, `default_per_page`); alle nicht genannten Listen-Endpunkte sind **unpaginiert** (Array).

| Modus | Bedeutung | `per_page` Default/Max | Endpunkte |
|---|---|---|---|
| `cursor` | immer paginiert (Envelope), auch ohne Parameter | 1000/1000 | App: EP-0058, EP-0106, EP-0108, EP-0224, EP-0254, EP-0259, EP-0311, EP-0373, EP-0378; V1: EP-0541, EP-0543, EP-0544, EP-0550, EP-0558, EP-0568, EP-0573, EP-0580, EP-0586, EP-0588, EP-0589, EP-0595, EP-0598, EP-0599, EP-0607, EP-0623, EP-0625, EP-0637, EP-0642, EP-0648, EP-0653, EP-0659, EP-0664 |
| `cursor` (abweichender Default) | wie oben | 20/1000 | EP-0491 (`{W}/stickies/`), EP-0612 (`{V1W}/stickies/`) |
| `cursor` (abweichender Default) | wie oben | 10/1000 | EP-0081 (`{I}/workspaces/`) |
| `cursor-grouped` | Work-Item-Engine: ohne `group_by` Envelope mit Liste, mit `group_by`/`sub_group_by` gruppierte `results` (`02` §3.11.6) | 1000/1000 | EP-0260 (`{P}/issues/`), EP-0298 (`{W}/issues/`), EP-0324 (Cycle-Work-Items), EP-0352 (Modul-Work-Items), EP-0516 (`{SP}/issues/`) |
| `cursor-when-requested` | nur paginiert, wenn **beide** Parameter `per_page` und `cursor` gesetzt sind; sonst Array (`PaginationMode.WhenRequested`) | 1000/1000 | EP-0188 (`{W}/projects/details/`), EP-0496 (`{W}/users/notifications/`) |
| `cursor-required` | ohne `per_page` **und** `cursor` 400 (Original-Text laut Golden) | 1000/1000 | EP-0724 (`{W}/export-issues/`, Exporthistorie) |
| `global` | `GlobalPaginator` (Cursor `"<size>:<page>:<offset>"`) | 1000/1000 | EP-0237, EP-0239 (Work-Item-Beschreibungsversionen), EP-0273 (`{P}/v2/issues/`, Delta-Sync), EP-0383 (Intake-Beschreibungsversionen) |

Regeln: (1) Kein Endpunkt wechselt den Modus gegenüber dem Original. (2) v1-Listen sind immer `cursor` (Original `BaseAPIView.paginate`), außer `cycle_view=current` an EP-0544 (unpaginierte Liste, 1:1) und Endpunkten ohne Pagination im Original (`V1`-Relationen, `members`, Summary). (3) `per_page = 0` beim Global-Paginator → 400 `{"detail": "Invalid per_page parameter."}` statt 500 (DT-GEN-11). (4) Paginierte Endpunkte deklarieren `.WithPagination(PaginationMode.X, defaultPerPage: n)`; `RouteInventoryTests.PaginationMatchesCatalog` vergleicht die Metadaten mit `endpoints.json`.

### 3.8 Filter-Syntax

| Endpunkt (EP) | Legacy-Filter (`A04` §2.18.1) | Rich-Filter `filters=` (`A04` §2.18.2) | `order_by` (Allowlist) | `group_by`/`sub_group_by` |
|---|---|---|---|---|
| EP-0260 `GET {P}/issues/` | ✓ | ✓ | `ISSUE_ORDER_BY_ALLOWLIST` | ✓ |
| EP-0262 `GET {P}/issues/list/` | ✓ | ✓ | dto. | nur Einfluss auf Annotationen (DT-WI-02 korrigiert) |
| EP-0259 `GET {P}/issues-detail/` | ✓ | ✓ | dto. | – |
| EP-0254 `GET {P}/archived-issues/` | ✓ | ✓ | dto. | – |
| EP-0298 `GET {W}/issues/` (Workspace-Views) | ✓ | ✓ | dto. | ✓ |
| EP-0324 Cycle-Work-Items | ✓ | ✓ | dto. | ✓ |
| EP-0352 Modul-Work-Items | ✓ | ✓ | dto. (Default `created_at`) | ✓ |
| EP-0373/EP-0378 Intake-Listen | ✓ (Präfix `issue__`) | – | `INTAKE_ISSUE_ORDER_BY_ALLOWLIST` | – |
| EP-0224 `GET {W}/draft-issues/` | ✓ | – | – | – |
| EP-0264 Sub-Work-Items | – | – | `ISSUE_ORDER_BY_ALLOWLIST` | – |
| EP-0516 `GET {SP}/issues/` | Space-Filter (`A05` §2.6) | – | dto. | ✓ (DT-SPACE-04 korrigiert) |
| EP-0304 `GET {W}/views/` | – | – | `VIEW_ORDER_BY_ALLOWLIST` | – |
| EP-0395 `GET {P}/pages/` | – | – | `PAGE_ORDER_BY_ALLOWLIST` | – |
| v1-Work-Item-Listen EP-0648/EP-0653 | `external_id`, `external_source` | **nein**: `filters` → 400 wie Original (`IV1FilterParameterBinding`, `16` E-19) | `ISSUE_ORDER_BY_ALLOWLIST` | – |
| v1-Projektliste EP-0599 | – | – | `PROJECT_ORDER_BY_ALLOWLIST` | – |
| v1-Aktivitäten EP-0623/EP-0625 | – | – | {`created_at`, `updated_at`} | – |

Semantik, Fehlercodes und AST: `02` §3.11 (`LegacyFilterParser`, `RichFilterParser`, `WorkItemFilterAst`). Unbekannte `order_by`-Werte fallen still auf den Default zurück (1:1). Neue Filterfelder registrieren Pakete über `IFilterFieldProvider` (`16`, 🧱 B6).

### 3.9 `expand` und `fields`

**App-API** (`DynamicBaseSerializer`): `fields` ist wirkungslos (DT-GEN-09, 1:1; der Parameter wird gebunden und ignoriert, schaltet aber an EP-0262 und EP-0339 wie im Original den Antwort-Codepfad). `expand` ist nur an diesen Endpunkten wirksam und nur mit diesen Werten:

| EP | Endpunkt | erlaubte `expand`-Werte (vom Client genutzt **fett**) |
|---|---|---|
| EP-0266 | `GET {P}/issues/{pk}/` | **`issue_reactions`**, **`issue_attachments`**, **`issue_link`**, **`parent`**, `assignees`, `labels`, `state`, `project`, `workspace`, `created_by`, `updated_by`, `issue_cycle`, `issue_relation`, `issue_related`, `issue_intake`, `sub_issues` |
| EP-0274 | `GET {W}/work-items/{project_identifier}-{issue_identifier}/` | wie EP-0266 |
| EP-0269 | `GET {P}/issues/{pk}/archive/` | wie EP-0266 |
| EP-0262 | `GET {P}/issues/list/` | wie EP-0266 (Serializer-Pfad statt `.values()`) |
| EP-0259 | `GET {P}/issues-detail/` | **`issue_relation`**, **`issue_related`** |
| EP-0375/EP-0380 | Intake-Detail | `issue_inbox` (ohne Wirkung, 1:1) |

Unbekannte `expand`-Werte werden ignoriert (1:1). Registry: `IExpandProvider` (`16` E-07, Signatur `string Key` + `ExpandAsync(ids, payloads, ct)`); die erlaubten Schlüssel je Endpunkt deklariert `.WithExpand("issue_reactions", …)` (Metadatum `ExpandAllowlistMetadata`), die CE-Werte sind selbst als Provider registriert (`WorkItemExpandProviders`, je Schlüssel eine Klasse), damit Pakete (🧱 A1 Typen/Properties, A9 Relationen) zusätzliche Schlüssel ohne Umbau ergänzen (Provider registrieren + Allowlist per `IExpandAllowlistContributor` erweitern).

**v1** (`A05` §2.1.6): `fields=a,b` **reduziert** die Felder (auch `id`), `expand=x` expandiert nur Felder, die in `fields` enthalten sind bzw. ohne `fields` alle expandierbaren Felder. Wirksam (Original „f/e ✓“) an EP-0544, EP-0547, EP-0550, EP-0552, EP-0558, EP-0568, EP-0589, EP-0591, EP-0595, EP-0599, EP-0601, EP-0607, EP-0609, EP-0623, EP-0625, EP-0637, EP-0639, EP-0642, EP-0644, EP-0648, EP-0650, EP-0653, EP-0655, EP-0659, EP-0664; an allen anderen v1-Endpunkten werden beide Parameter ignoriert. Umsetzung: `V1FieldSelection` (Parse) + `V1Projection.Apply(JsonObject, V1FieldSelection, IV1ExpandResolver)` im Mapper von `Plane.PublicApi`; `IV1PayloadExtension` (`16` E-07) ergänzt Felder je Ressource. Sonderfälle 1:1: `assignees`/`labels` am Work Item sind ID-Listen, mit `expand` Objekte; `IssueExpandSerializer` liefert immer ID-Listen. `{V1W}/projects/{project_id}/summary/` (V-PRJ-09) nutzt `fields` als Auswahl der Zählbereiche (eigene Semantik, 1:1).

### 3.10 Bulk-Operationen und Idempotenz

#### 3.10.1 Bulk-Endpunkte (vollständig)

| EP | Endpunkt | Body | Ziel-Command | Transaktion | Rückgabe | DT |
|---|---|---|---|---|---|---|
| EP-0177 | `POST {P}/bulk-create-labels/` | `{"label_data": [{name?, description?}]}` | `BulkCreateLabelsCommand` | eine | 201 `{"labels": [...]}` (nur angelegte) | DT-PRJ-09 (1:1 inkl. `ignore_conflicts`) |
| EP-0255 | `POST {P}/bulk-archive-issues/` | `{"issue_ids": [...]}` | `BulkArchiveWorkItemsCommand` → je ID Archiv-Logik des Einzel-Commands | eine | 200 `{"archived_at": "YYYY-MM-DD"}`; 400 `{"error": "Issue IDs are required"}`; 400 coded 4091 | DT-WI-05 |
| EP-0256 | `DELETE {P}/bulk-delete-issues/` | `{"issue_ids": [...]}` | `BulkDeleteWorkItemsCommand` → je ID `DeleteWorkItem` (Kaskaden, Activity) | eine | 200 `{"message": "{n} issues were deleted"}`; 400 `{"error": "Issue IDs are required"}` | DT-WI-05 |
| EP-0258 | `POST {P}/issue-dates/` | `{"updates": [{id, start_date?, target_date?}]}` | `BulkUpdateWorkItemDatesCommand` | eine | 200 `{"message": "Issues updated successfully"}`; 400 `{"message": "Start date cannot exceed target date"}` | DT-WI-05 |
| EP-0265 | `POST {P}/issues/{issue_id}/sub-issues/` | `{"sub_issue_ids": [...]}` | `SetSubWorkItemsCommand` | eine | 200 `{"sub_issues": [...], "state_distribution": {...}}` | – |
| EP-0281 | `POST {P}/issues/{issue_id}/issue-relation/` | `{"relation_type", "issues": [...]}` | `CreateWorkItemRelationsCommand` | eine | 201 | DT-WI-03 |
| EP-0420 | `POST {AV2}/workspaces/{slug}/projects/{project_id}/{entity_id}/bulk/` | `{"asset_ids": [...]}` | `BulkConfirmProjectAssetsCommand` | eine | 204 | – |
| EP-0461 | `POST /api/public/assets/v2/anchor/{anchor}/{entity_id}/bulk/` | `{"asset_ids": [...]}` | `BulkConfirmPublicAssetsCommand` | eine | 204 | DT-AST-04 |
| EP-0128 | `POST {W}/invitations/` | `{"emails": [{email, role}]}` | `CreateWorkspaceInvitationsCommand` | eine | 200 | DT-WS-04 |

Weitere Endpunkte mit Listen-Bodies (Zuordnungen `POST {P}/cycles/{cycle_id}/cycle-issues/`, `POST {P}/modules/{module_id}/issues/`, `POST {P}/issues/{issue_id}/modules/`, Projekt-Mitglieder anlegen, v1-Zuordnungen) sind fachliche Mehrfach-Zuordnungen, keine generischen Bulk-Operationen; sie folgen derselben Regel (eine Transaktion, Einzel-Commands, je Element Activity/Outbox).

Regeln: (1) Alles-oder-nichts je Request (Original teilweise ohne Transaktion, z. B. bleiben bei `bulk-archive-issues` gequeuete Activities eines abgebrochenen Laufs bestehen; Korrektur ohne Vertragswirkung bei Erfolg, K). (2) Keine neue Elementobergrenze (Vertrag wie Original); die Größe ist durch die Body-Grenze (§3.3) beschränkt. (3) Activity, Benachrichtigungen und Webhooks je Element wie bei der Einzeloperation (DT-WI-05 korrigiert die fehlenden Activities/Kaskaden; Webhook-Ereignisse nur, soweit die Einzeloperation sie auslöst, DT-WH-07).

#### 3.10.2 Idempotenz

| Methode | Vertrag |
|---|---|
| `GET` | idempotent (Seiteneffekte nur Recents/`last_used`, §3.2.1) |
| `PATCH` | idempotent bezogen auf den Endzustand; Activity nur bei tatsächlicher Änderung (Diff) |
| `PUT` (nur Einstellungen) | idempotent |
| `DELETE` | idempotent im Zustand; Status beim zweiten Aufruf wie Original (meist 404 `{"error": "The required object does not exist."}`; Toggle-artige Endpunkte wie Favoriten/Reaktionen/Abos laut Golden) |
| `POST` | **nicht** idempotent; Ausnahmen mit Original-Semantik „anlegen oder vorhanden lassen“: Abonnieren (`POST {P}/issues/{issue_id}/subscribe/`), Projekt beitreten, Favorit anlegen (Duplikat → 400 laut Golden), Recents |
| Header `Idempotency-Key` | ignoriert (reserviert für 🧱 H3, §6) |
| v1 `external_id` + `external_source` | Duplikat → 409 `{"error": "<Ressource> with the same external id and external source already exists", "id": "<uuid>"}` (1:1); dient Integrationen als natürliche Idempotenz |
| eingehende Integrations-Webhooks | Inbox-Deduplizierung per Delivery-ID (`16` §3.4.3); Antwort 202 auch bei Duplikat |

### 3.11 API-Keys und Authentisierung je Oberfläche

| Aspekt | Festlegung | Quelle |
|---|---|---|
| Header | `X-API-Key: plane_api_<32 hex>`; Name case-insensitive (HTTP), `02` schreibt `X-Api-Key` – identisch | `A05` §2.1.2 |
| Format/Erzeugung | `plane_api_` + 32 Hex-Zeichen (`RandomNumberGenerator`, 16 Byte), Präfix bleibt (ADR-009B: Protokollbezeichner) | `05` §3.12.3 |
| Speicherung | nur `token_hash` (SHA-256 hex) + `token_prefix` (erste 14 Zeichen, D05-ADR-16); Klartext nur in der Anlage-Antwort (`POST /api/users/api-tokens/` → 201 mit `token`) | DT-AUTH-10, SEC-33, SEC-35, `03` |
| Anzeige | Listen/Detail liefern `APITokenReadSerializer`-Form ohne `token` (1:1); `PATCH` ändert nur `label`/`description` und liefert `token` nicht mehr (SEC-35) | DT-AUTH-10, `05` §3.12.3 |
| Gültigkeit | `is_active`, `expired_at` (null = unbegrenzt), Besitzer aktiv; **workspaceübergreifend** wie Original (`api_tokens.workspace_id` bleibt ungenutzt; Workspace-Tokens sind 🧱 H3) – die Berechtigung ergibt sich aus den Mitgliedschaften des Besitzers | `05` §3.12.2 |
| Fehler | fehlt → 401 `{"detail": "Authentication credentials were not provided."}`; ungültig/abgelaufen → 403 `{"detail": "Given API token is not valid"}` (1:1, DT-GEN-13) | `A05` §2.1.2 |
| Seiteneffekt | `last_used` wird nur geschrieben, wenn älter als 60 s (Original: jeder Request; Korrektur K) | `05` §3.12.2 Nr. 3 |
| Protokoll | `api_activity_logs` je Request (`ApiActivityLogMiddleware`, CE-API-003): `token_identifier = token_hash`, Header `x-api-key`, `authorization`, `cookie` → `[REDACTED]`, Body-Regeln wie Original-`MW/logger.py`, asynchron, Aufbewahrung 14 Tage | `05` §3.12.2 Nr. 6 |
| Rate-Limit | Policy `api_key`, Partition `token_hash`, Header `X-RateLimit-Remaining`, `X-RateLimit-Reset` | §3.12 |
| Bearer (🧱 H1) | Schema registriert, `Plane:Auth:Bearer:Enabled=false` → 401 | DT-V1-13 |
| Cookie an V1 | wird ignoriert (keine Session-Authentisierung an `/api/v1/`) | `A05` §2.1 |
| App/Space/Instance | Session-Cookie `session-id` (Keycloak-gestützte Session, `05` §3.3), CSRF Origin + Token | `05` |
| Auth-Oberfläche | anonym bzw. Session; Fehler als Redirect mit Codes (§3.5) | `05` §3.2 |

### 3.12 Rate Limits

| Policy | Rate (Konfig) | Partition | Endpunkte | Original | ab |
|---|---|---|---|---|---|
| `anon` | 30/min (`Plane:RateLimits:Anon`) | Client-IP | alle anonymen Aufrufe der Oberflächen App, Space, Instance, Auth, OpenApi | `AnonRateThrottle` | I0 |
| `authentication` | 10/min (`Plane:RateLimits:Authentication`) | Client-IP | alle Zeilen der Oberfläche Auth mit `registered = true` außer EP-0001 (`get-csrf-token`) und EP-0002 (Backchannel-Logout, nur intern) | `AuthenticationThrottle` | I0 |
| `asset_duplicate` | 5/min (`Plane:RateLimits:AssetDuplicate`) | Benutzer | Asset-Duplizieren (`POST {AV2}/workspaces/{slug}/duplicate-assets/{asset_id}/` laut Katalog) | `AssetRateThrottle` | I1 |
| `api_key` | 60/min (`Plane:RateLimits:ApiKey`) | `token_hash` | gesamte Oberfläche V1 (inkl. Einladungen/Stickies, DT-V1-05) | `ApiKeyRateThrottle` | I6 |
| `integration_webhook` | 600/min (`Plane:RateLimits:IntegrationWebhook`) | `provider` + `connection_id` | EP-0729 | – (neu, F1) | I0 |

Ablehnung: 429 coded 5900 + `Retry-After` (Sekunden), **ohne** `X-RateLimit-*`-Header; erfolgreiche V1-Antworten tragen `X-RateLimit-Remaining` und `X-RateLimit-Reset` (Unix-Sekunden). Algorithmus und verteilte Umsetzung: `02` §3.13. Live-Verbindungs-Limits: `07`. Gateway-Limits (`14` G-xx) liegen davor und sind großzügiger (Schutz gegen Volumen, nicht Vertrag).

### 3.13 Entscheidungstabelle für Original-Fehler und Sicherheitslücken (DT)

#### 3.13.1 Regeln

| Kategorie | Bedeutung | Entscheidung (Regel, D04-ADR-19) | `deviations.yaml` | Beispiel |
|---|---|---|---|---|
| **S** | Sicherheitslücke (fehlende/zu weite Rechteprüfung, IDOR, Klartext-Secrets, SSRF, CSRF, Mass-Assignment) | **immer korrigieren**; bereits vorhandene Schutzmechanismen des Originals bleiben 1:1 | ja, mit `SEC-nn`/`HARM-nn` aus `05` §3.18 | DT-PRJ-08 |
| **F** | funktionaler, sichtbarer Fehler (500, falsches Ergebnis, verlorene Daten, wirkungslose Option) | **korrigieren und dokumentieren** (Auftraggeber-Entscheidung Z-12); Vertrag bleibt, wo er funktioniert | ja, `DEV-API-nn` | DT-PRJ-01 |
| **T** | tote, defekte oder redundante Route ohne fachliche Funktion | **nicht registrieren** (404/405); Funktion über die funktionierende Route | ja, wenn ein Client/Golden die Route kennt | DT-GEN-01 |
| **Q** | Vertrags-Quirk, auf den Original-Clients bauen | **1:1** übernehmen | nein | DT-GEN-10 |
| **A** | durch ADR bedingt (ADR-008 Keycloak, ADR-004 offline, ADR-026 Storage, ADR-051 OpenAPI) | **entfällt/angepasst** laut ADR | ja | DT-AUTH-01 |
| **K** | technische Korrektur ohne Vertragswirkung (Determinismus, Transaktionen, Format-Details) | korrigieren | nur bei sichtbarer Byte-Abweichung (z. B. `DEV-WH-003`) | DT-GEN-08 |

Die Spalte „Entscheidung“ der Tabelle in §3.13.2 ist für Implementierungs-Agenten bindend; Abweichungen davon brauchen eine neue DT-Zeile (nie stilles Abweichen). Jede DT-Zeile mit Abweichungs-ID wird im Parity-Harness als `deviations.yaml`-Eintrag mit `decision: "04#<DT-ID>"` geführt (`15` §3.6.5). Die Tabelle ist identisch in `_data/04-decisions.json` abgelegt (Felder `id`, `cat`, `area`, `befund`, `quelle`, `entscheidung`, `verhalten`, `dev`, `test`, `ce`, `inc`, `eps`).

#### 3.13.2 Tabelle

| DT-ID | Kat. | Bereich | Befund im Original | Quelle | Entscheidung | Neues Verhalten (Vertrag) | Abweichung (`deviations.yaml`) | Test | CE-IDs | Ink. |
|---|---|---|---|---|---|---|---|---|---|---|
| <a id="DT-GEN-01"></a>**DT-GEN-01** | T | Querschnitt | DRF-Default-`update` (PUT) neben PATCH: Workspace (W-05), Projekt (P-05), Work Item (I7), Kommentar (C4), Cycle (Y4), Modul (M4), Projekt-View (W4), Workspace-View (W10) umgehen Ersteller-/Lock-/Archiv-/Activity-Logik; Label (L4), Work-Item-Link (K4), Modul-Link (M14-PUT), v1-Einladung (V-INV-05) und v1-Sticky (V-STK-05) sind funktionsfähige, aber von keinem Client genutzte PUT-Duplikate | A03 Q-07, A04 §5.1/§5.4, A05 §2.2.15/§2.2.16, 05 SEC-01, ABG-043 | nicht registrieren | 405 `{"detail": "Method \"PUT\" not allowed."}` (StatusCodeBodiesMiddleware, 02 §3.3.1 Regel 5) | DEV-API-01 (SEC-01), DEV-API-04 (L4), DEV-API-05 (K4, M14-PUT, V-INV-05, V-STK-05) | `UnsupportedPutTests` (je Pfad) | CE-WS-003, CE-PRJ-018, CE-WI-003, CE-WI-037, CE-CYC-005, CE-MOD-003, CE-LV-048, CE-LV-053, CE-PRJ-029, CE-WI-035, CE-MOD-005, CE-API-013, CE-API-014 | I0–I6 |
| <a id="DT-GEN-02"></a>**DT-GEN-02** | T | Querschnitt | Geroutete DRF-Default-Aktionen `retrieve`/`update`/`partial_update` auf Zuordnungs-ViewSets (`cycle-issues/{issue_id}/`, `modules/{module_id}/issues/{issue_id}/`) – 500 (erwartet `pk`) bzw. ohne Projektprüfung | A04 Y9, M10, 05 SEC-02 | nicht registrieren | 405 (DELETE bleibt registriert) | DEV-API-03 (SEC-02) | `CycleModuleIssueRoutesTests` | CE-CYC-010, CE-MOD-008 | I3 |
| <a id="DT-GEN-03"></a>**DT-GEN-03** | T | Querschnitt | Methoden-Nebenprodukte: Django-`APIView`-Klassen beantworten jede implementierte Methode auf **allen** ihnen zugeordneten Routen (z. B. `DELETE /api/users/api-tokens/` ohne `pk`, `GET {AV2}/workspaces/{slug}/` ohne `asset_id`); im Original meist 500 (`TypeError`) oder fachlich sinnlos; 85 Kombinationen laut `05-permission-matrix.json` ohne Gegenstück im Analyse-Inventar | A05 §2.7.2 (Instanz-Admins), A04 Y24, 05 Anhang B (AST-Extraktion), §4.25 | nicht registrieren | 405 `{"detail": "Method \"X\" not allowed."}`, wenn der Pfad mit einer anderen Methode existiert, sonst 404 `{"error": "Page not found."}` | DEV-API-06 | `RouteInventoryTests.NoByproductRoutes` (vergleicht `EndpointDataSource` mit `_data/endpoints.json`) | je Ressource (siehe §4.25) | I0–I6 |
| <a id="DT-GEN-04"></a>**DT-GEN-04** | K | Querschnitt | Django `APPEND_SLASH`: Pfade ohne abschließenden Slash → 301 (GET) bzw. 500 (POST/PATCH) | 01 §7.11, D02-ADR-07 | korrigieren | jede Route mit **und** ohne Slash, gleicher Status/Körper, kein Redirect | DEV-API-07 | `RoutingConventionTests` (02 AK-02) | CE-OPS-007 | I0 |
| <a id="DT-GEN-05"></a>**DT-GEN-05** | Q | Querschnitt | Uneinheitliche Fehlerformen (`{"error"}`, `{"detail"}`, `{"error_code","error_message"}`, DRF-Feldfehler, `{"message","code"}` des Rich-Filters) und endpunktspezifische Texte | A04 §2.20, A06 §2.12, 01 ADR-016 | 1:1 | wortgleich über `PlaneErrors` (02 §3.8); Fehlertext-Katalog §3.6 | – | `PlaneErrorsGoldenTests`, Contract-Goldens (N12) | CE-AUTH-014, CE-UIX-001 | I0 |
| <a id="DT-GEN-06"></a>**DT-GEN-06** | Q | Querschnitt | Abweichende Erfolgs-Statuscodes einzelner Endpunkte (z. B. `PATCH {P}/issues/{pk}/` → 204, `POST {P}/cycles/date-check/` → 200 auch bei Konflikt, `POST {W}/invitations/` → 200, `POST {P}/pages/{page_id}/favorite` → 204) | A04 §5.1, A03 §2.5 ff. | 1:1 | Status je Endpunkt laut Spalte „Erfolg“ in §4 bzw. `endpoints.json` (`success`) | – | Contract-Goldens | alle | I0–I6 |
| <a id="DT-GEN-07"></a>**DT-GEN-07** | F | Querschnitt | Response-Cache `@cache_response` (Schlüssel Pfad+User, 1–2 h); Invalidierungen treffen die Schlüssel nicht → veraltete Daten bis 2 h (Workspace-Labels, Instanz, Konfiguration) | A03 Q-30, A06 E-20, A05 B-29 | korrigieren | kein Response-Cache; benannte Lesemodelle mit Tag-Invalidierung (02 D02-ADR-16, §3.12); `Cache-Control`-Header nur wie Original (02 §3.3.1 Regel 8) | DEV-API-08 | `CacheInvalidationTests` (02 AK-16) | CE-WS-006, CE-INST-003, CE-INST-017 | I1 |
| <a id="DT-GEN-08"></a>**DT-GEN-08** | K | Querschnitt | Sortierung ohne eindeutigen Tiebreaker (`-created_at`) → nicht deterministische Seitenränder | A04 O3, 02 D02-ADR-13 | korrigieren | zusätzlicher Tiebreaker `id DESC` | DEV-PAG-001 | `CursorPaginatorTests` | CE-LV-005, CE-LV-044 | I1 |
| <a id="DT-GEN-09"></a>**DT-GEN-09** | Q | Querschnitt | `fields`-Parameter der App-API ohne Wirkung (DynamicBaseSerializer verwirft ihn); `expand` nur für dokumentierte Werte | A04 §5.3 Nr. 20, A04 §2.18.5 | 1:1 | `fields` wird akzeptiert und ignoriert (App); in v1 wirkt `fields`/`expand` wie Original (A05 §2.1.6) | – | `FieldsExpandContractTests` | CE-WI-010, CE-API-017 | I2/I6 |
| <a id="DT-GEN-10"></a>**DT-GEN-10** | Q | Querschnitt | Zähler `sub_issues_count`, `link_count`, `attachment_count` teils `null` statt `0` | A04 O1, §5.3 Nr. 21 | 1:1 | Ausgabe wie Original (`null`, wo die Original-Abfrage `null` liefert); Client behandelt `null` wie 0 | – | Contract-Goldens (N10) | CE-LV-018, CE-WI-032 | I2 |
| <a id="DT-GEN-11"></a>**DT-GEN-11** | F | Querschnitt | `global_paginator` mit `page_size = 0` → `ZeroDivisionError` (500) | A06 E-15 | korrigieren | 400 `{"detail": "Invalid cursor parameter."}` | DEV-API-09 | `GlobalPaginatorTests.ZeroPageSize` | CE-WI-012 | I2 |
| <a id="DT-GEN-12"></a>**DT-GEN-12** | S | Querschnitt | Objektbindungen an URL-Projekt/-Workspace (`issue_in_project`, `workspace__slug`, `project_id=`) als IDOR-Schutz (GHSA-Kommentare), Allowlists für `group_by`/`order_by` (GHSA-wwgj-929g-42cm) | A04 §5.4 „Beibehalten“, 05 §3.18.3 | 1:1 (Schutz erhalten) | jede Fremdreferenz → 404 mit Original-Text; unbekanntes `group_by`/`order_by` → 400 bzw. Default | – | `TenantIsolationTests` je Modul, `OrderByFuzzTests` | CE-LV-005, CE-WS-008 | I0–I6 |
| <a id="DT-GEN-13"></a>**DT-GEN-13** | Q | Querschnitt | Ungültiger API-Key → 403 statt 401 | A05 B-03, 05 §3.18.2 „Bewusst nicht geändert“ | 1:1 | 403 `{"detail": "Given API token is not valid"}` | – | `ApiKeyAuthenticationTests` | CE-API-001 | I6 |
| <a id="DT-GEN-14"></a>**DT-GEN-14** | K | Querschnitt | Syntaktisch ungültiges JSON bzw. falscher `Content-Type` werden in .NET vor der Permission-Prüfung beantwortet (Minimal-API-Binding) | 02 §3.4.2 „Grenze“ | hinnehmen (dokumentiert) | 400 `{"detail": "JSON parse error - …"}` / 415 auch für Gäste | DEV-JSON-002 | `BindingOrderTests` | CE-OPS-019 | I0 |
| <a id="DT-GEN-15"></a>**DT-GEN-15** | T | Querschnitt | Favoriten-Listen `GET {P}/user-favorite-cycles/`, `…/user-favorite-modules/`, `…/user-favorite-views/` immer 500 (`select_related` ungültig), kein Client-Aufrufer (Favoriten kommen aus `GET {W}/user-favorites/`) | A04 Y12, M15, W14 | nicht registrieren | 405 (POST bleibt registriert); 05 führt die Keys `project.cycle.read_favorites`, `project.module.read_favorites`, `project.view.read_favorites` als „entfällt“ (Rückmeldung §9) | DEV-API-10 | `RemovedRoutesTests` | CE-CYC-015, CE-MOD-011, CE-LV-050 | I3 |
| <a id="DT-GEN-16"></a>**DT-GEN-16** | T | Querschnitt | Vom Original-Frontend aufgerufene, im CE-Backend fehlende Endpunkte ohne UI-Pfad (tote Service-Methoden): `GET {P}/archived-pages/`, `POST {P}/bulk-subscribe-issues/`, `GET {W}/my-issues/`, `GET /api/release-notes/`, `GET /api/configs/`, `GET {P}/views/{view_id}/issues/`, `PATCH {W}/sidebar-preferences/{key}/`, `POST {P}/pages/{page_id}/versions/{pk}/restore/`, `GET /api/instances/changelog/` | 16 §4.3, A03 O-02, A11 §2 (Z. 310), Original `apps/web/services/**` | nicht bauen (1:1: 404) | 404 `{"error": "Page not found."}`; Service-Methoden werden 1:1 portiert, aber nirgends aufgerufen (08 AK-D08-16) | – | `DeadFrontendCallsTests` (Liste = Tabelle §4.26) | CE-PAGE-001, CE-WI-043, CE-PROF-009, CE-WS-015, CE-LV-051, CE-WS-021, CE-PAGE-019, CE-INST-010 | I1–I6 |
| <a id="DT-AUTH-01"></a>**DT-AUTH-01** | A | Auth | Eigene Anmeldung (Passwort, Magic-Code, OAuth Google/GitHub/GitLab/Gitea, E-Mail-Check, Passwort vergessen/zurücksetzen/ändern/setzen) in App und Space; Admin-Sign-in; verknüpfte Konten; E-Mail-Änderung | A06 §2.1 #1–#4, #8–#37, AD-2; A03 U-06, U-07, U-10…U-12; 00 ADR-008; 05 §4.2 | entfällt | Routen nicht registriert → 404 `{"error": "Page not found."}` (05 N-14); Login über `/auth/oidc/login/` (N-01) | DEV-API-02 | `RemovedRoutesTests.Adr008` | CE-AUTH-002…011, CE-AUTH-013, CE-AUTH-017…021, CE-PROF-004, CE-PROF-007, CE-INST-007, CE-SPACE-008…011 | I0 |
| <a id="DT-AUTH-02"></a>**DT-AUTH-02** | A | Auth | Lokaler Logout (`POST /auth/sign-out/`, `/auth/spaces/sign-out/`, `/api/instances/admins/sign-out/`) beendet nur die Django-Session | A06 #5, #6, AD-3; 05 N-03…N-05 | angepasst | 302 → Keycloak `end_session_endpoint` (RP-initiated Logout), Rücksprung über `/auth/oidc/signed-out/` (N-06); Admin-Pfad bleibt als BFF-Alias | DEV-API-02 | `OidcLogoutFlowTests` | CE-AUTH-022, CE-INST-008 | I0 |
| <a id="DT-AUTH-03"></a>**DT-AUTH-03** | A | Auth | `GET /api/instances/` liefert Login-Methoden-Flags (`is_google_enabled`, `is_github_enabled`, `is_gitlab_enabled`, `is_gitea_enabled`, `is_magic_login_enabled`, `is_email_password_enabled`, `github_app_name`, `slack_client_id`) | A05 §2.7.5, 02 §3.16.2, 05 §4.4 | angepasst | Flags fest `false` bzw. `""`/`null` (Typ `IInstanceConfig` bleibt), neu `is_oidc_auto_redirect_enabled`, `oidc_account_console_url`, `oidc_provider_name`; in `deviations.yaml` als `kind: replace` (nicht `removed-field`, Rückmeldung an 15 §3.6.5) | DEV-API-02 | `InstanceInfoContractTests` | CE-INST-003, CE-AUTH-013 | I0 |
| <a id="DT-AUTH-04"></a>**DT-AUTH-04** | F | Auth | Post-Login-Workflow legt Projektmitgliedschaften aus angenommenen Projekt-Einladungen ohne `project_id` an → NOT-NULL-Verletzung, 500 bei jedem Login | A06 E-02 | korrigieren | Provisionierungsschritt `AcceptPendingInvitationsStep` (05 §3.7.3) legt Workspace- **und** Projektmitgliedschaften korrekt an | DEV-API-11 | `OidcProvisioningTests.ProjectInvite_JoinsProject` | CE-AUTH-028 | I1 |
| <a id="DT-AUTH-05"></a>**DT-AUTH-05** | S | Auth | CSRF: Auth-JSON-Views verlangen klassisches `X-CSRFToken` (DRF-Default) – 403 für angemeldete Aufrufer ohne Token; Session-Views ohne Origin-Härtung | A06 E-17, §3.14 | korrigieren | Origin-/`Sec-Fetch-Site`-Prüfung für alle unsicheren Cookie-Requests (02 §3.4.1 Nr. 11, D05-ADR-06); Antiforgery-Token nur für Formular-POSTs (`/auth/sign-out/`, `/auth/spaces/sign-out/`, `/api/instances/admins/sign-out/`) | – | `OriginCheckTests`, `AntiforgeryTests` | CE-AUTH-016, CE-AUTH-024 | I0 |
| <a id="DT-AUTH-06"></a>**DT-AUTH-06** | S | Auth | `next_path` bleibt in der Session und wird unkodiert angehängt | A06 E-11, E-27; 05 SEC-50 | korrigieren | `next_path` nur im DP-geschützten OIDC-State je Login, URL-kodiert | SEC-50 | `NextPathValidatorTests` | CE-AUTH-029 | I0 |
| <a id="DT-AUTH-07"></a>**DT-AUTH-07** | A | Auth | `GET /api/users/me/instance-admin/` liest Tabelle `instance_admins` | A03 U-13, 05 §4.2 | angepasst | Ergebnis aus `PlanePrincipal.IsInstanceAdmin` (Keycloak-Rolle `plane-instance-admin`), Antwortform unverändert | – | `InstanceAdminFlagTests` | CE-INST-005 | I0 |
| <a id="DT-AUTH-08"></a>**DT-AUTH-08** | A | Identity | Konto deaktivieren randomisiert das Passwort und meldet ab; „einziger Admin“-Prüfung ist wirkungslos (deaktiviert faktisch immer) | A03 U-03, Q-16; 05 §3.10 | angepasst + korrigieren | Deaktivierung wirkt in Plane (`is_active=false`, Sessions beendet), Sperre des Keycloak-Kontos separat; einziger Workspace-Admin → 400 mit den im Original vorhandenen Texten | DEV-API-12 | `DeactivateUserTests` | CE-PROF-005 | I1 |
| <a id="DT-AUTH-09"></a>**DT-AUTH-09** | S | Identity | Mass-Assignment in `PATCH /api/users/me/` (`is_password_expired`, `bot_type`, `is_email_valid`, `last_login` …) | A03 Q-15, 05 SEC-36 | korrigieren | Whitelist `UpdateCurrentUserRequest`; unbekannte Felder ignoriert | SEC-36 | `UserMassAssignmentTests` | CE-PROF-003 | I1 |
| <a id="DT-AUTH-10"></a>**DT-AUTH-10** | S | Identity | API-Tokens im Klartext gespeichert; `PATCH /api/users/api-tokens/{pk}/` liefert das Token erneut | A03 Q-18, AT-04; 05 SEC-33, SEC-35 | korrigieren | SHA-256-Hash (`token_hash`); Klartext nur einmal in der Antwort von `POST`; `PATCH` ohne `token` | SEC-33, SEC-35 | `ApiKeyStorageTests`, `ApiTokenPatchTests` | CE-WH-012, CE-WH-013, CE-API-001 | I6 |
| <a id="DT-AUTH-11"></a>**DT-AUTH-11** | F | Identity | Zeitzonenliste mit falsch formatierten negativen Halbstunden-Offsets (z. B. `UTC-03:-30`) | A03 Q-29, T-01 | korrigieren | Offsets `UTC-03:30`/`GMT-03:30` | DEV-API-13 | `TimezoneListTests` | CE-PROF-006 | I1 |
| <a id="DT-WS-01"></a>**DT-WS-01** | T | Workspaces | `GET /api/workspaces/` liefert immer 400 (`KeyError` in `allow_permission`); Workspace-Liste kommt aus `GET /api/users/me/workspaces/` | A03 W-02, Q-01 | nicht registrieren | 405 (POST registriert) | DEV-API-14 | `RemovedRoutesTests` | CE-WS-005 | I0 |
| <a id="DT-WS-02"></a>**DT-WS-02** | F | Workspaces | `GET /api/users/last-visited-workspace/` immer 500 | A03 W-23, Q-02 | korrigieren | liefert die Spezifikation aus A03 W-23 (`Profile.last_workspace_id`, Fallback erste Mitgliedschaft) | DEV-API-15 | `LastVisitedWorkspaceTests` | CE-AUTH-029 | I0 |
| <a id="DT-WS-03"></a>**DT-WS-03** | F | Workspaces | Einladung annehmen setzt `user.last_workspace_id` (Feld existiert nur auf `Profile`) – wirkungslos | A03 W-15, Q-03 | korrigieren | `profiles.last_workspace_id` wird gesetzt | DEV-API-16 | `WorkspaceJoinTests` | CE-WS-011 | I1 |
| <a id="DT-WS-04"></a>**DT-WS-04** | F | Workspaces | Erneute Einladung derselben E-Mail wird still ignoriert (`bulk_create(ignore_conflicts=True)`), keine Mail | A03 W-09, Q-38 | korrigieren (ohne UI-Änderung) | offene Einladung wird aktualisiert (Rolle, Token, `updated_at`) und die Mail erneut versendet; Antwort unverändert 200 `{"message": "Emails sent successfully"}` | DEV-API-17 | `WorkspaceInvitationTests.Reinvite_ResendsMail` | CE-WS-010 | I1 |
| <a id="DT-WS-05"></a>**DT-WS-05** | S | Workspaces | `GET {W}/user-favorite-projects/` immer 500; Projekt-Favorit anlegen/löschen ohne Workspace-/Projektbezug | A03 P-27…P-29, Q-11; 05 SEC-11, SEC-12 | korrigieren / nicht registrieren | GET → 405; POST/DELETE mit `WS(A,M,G)+PRJ-MEMBER` bzw. `+OWN` | SEC-11, SEC-12 | `ProjectFavoriteScopeTests` | CE-WS-023, CE-PRJ-012 | I1 |
| <a id="DT-WS-06"></a>**DT-WS-06** | S | Workspaces | Drafts: Lesen nur WS-Admin, Admin darf fremde Drafts löschen, Ersteller-Prüfung gegen falsches Modell | A03 Q-04, Q-05; 05 SEC-15 | korrigieren | Drafts strikt privat (`WS(A,M,G)+OWN`), fremde → 404 | SEC-15 | `DraftPrivacyTests` | CE-WI-049 | I2 |
| <a id="DT-WS-07"></a>**DT-WS-07** | F | Workspaces | Draft → Work Item schreibt Cycle-Activity mit `project_id="None"` | A03 W-53, Q-06 | korrigieren | Activity mit korrekter Projekt-ID | DEV-API-18 | `ConvertDraftTests.CycleActivity` | CE-WI-049 | I2 |
| <a id="DT-WS-08"></a>**DT-WS-08** | F | Workspaces | Relationsfilter über `project_projectmember` zählen soft-gelöschte Mitgliedschaften und erzeugen Duplikate (Projektlisten, Mitgliederlisten) | A03 Q-31 | korrigieren | `deleted_at IS NULL` + `is_active` + `DISTINCT` | DEV-PERM-001 | `MembershipFilterTests` | CE-PRJ-001, CE-WS-009 | I1 |
| <a id="DT-WS-09"></a>**DT-WS-09** | F | Workspaces | Reservierte Workspace-Slugs: Backend-Liste `RESTRICTED_WORKSPACE_SLUGS` (`API/utils/constants.py`) und Frontend-Liste `RESTRICTED_URLS` (`PKG/constants/src/workspace.ts`) weichen voneinander ab; `login` und `register` fehlen in beiden, `signin` nur im Backend (08 FE-E4) – ein Workspace mit diesen Slugs überdeckt App-Routen | 08 §3 E4 (FE-E4), A03 W-01/W-03, A05 I-16/I-18 | korrigieren | eine Liste `ReservedWorkspaceSlugs.All` (`Plane.Workspaces.Contracts`) = Vereinigung beider Original-Listen + `login`, `register`; Slug-Check liefert `{"status": false}` (nicht verfügbar), Anlage 400 `{"slug": ["Slug is not valid"]}` (Original-Text); Frontend nutzt dieselbe Liste (`@plane/constants`, 08) | DEV-API-63 | `ReservedWorkspaceSlugTests` (Backend) + `restricted-urls.spec.ts` (Frontend, gleiche Liste per Golden-Datei `tests/contracts/reserved-slugs.json`) | CE-WS-001, CE-INST-029 | I0 |
| <a id="DT-PRJ-01"></a>**DT-PRJ-01** | F | Projects | `POST {P}/invitations/` immer 500 (`AttributeError` auf QuerySet, `delay` auf Liste) | A03 P-11, Q-09; 05 CE-PRJ-010 („04 entscheidet“) | korrigieren (reparieren) | vorgesehene Logik aus A03 P-11: Rollenabgleich mit WS-Rolle (400 `{"error": "You cannot invite a user with different role than workspace role"}`), Einladungen mit Token, Mail-Job je Empfänger, 200 `{"message": "Email sent successfully"}` | DEV-API-19 | `ProjectInvitationTests.Create` | CE-PRJ-010 | I1 |
| <a id="DT-PRJ-02"></a>**DT-PRJ-02** | S | Projects | Projekt-Einladungen listen/lesen/löschen ohne Rechteprüfung; eigene Projekt-Einladungen ignorieren den URL-Workspace | A03 Q-08, Q-10; 05 SEC-05, SEC-06 | korrigieren | `PRJ(A)` bzw. Filter `workspace.slug == {slug}` | SEC-05, SEC-06 | `ProjectInvitationPermissionTests` | CE-PRJ-010 | I1 |
| <a id="DT-PRJ-03"></a>**DT-PRJ-03** | S | Projects | Deploy-Board-Detail ohne Bindung an das URL-Projekt (IDOR) | A03 Q-12; 05 SEC-16 | korrigieren | Objekt muss `project_id == {project_id}` haben, sonst 404 | SEC-16 | `DeployBoardScopeTests` | CE-SPACE-001 | I6 |
| <a id="DT-PRJ-04"></a>**DT-PRJ-04** | S | Projects | Fremde Member-Präferenzen änderbar | A03 Q-13; 05 SEC-17 | korrigieren | `member_id` = eigene Mitgliedschaft, sonst 403 | SEC-17 | `MemberPreferenceSelfTests` | CE-PRJ-016 | I1 |
| <a id="DT-PRJ-05"></a>**DT-PRJ-05** | F | Projects | `intake_view` nur über den Altnamen `inbox_view` setzbar | A03 P-06, Q-14 | korrigieren | beide Feldnamen werden akzeptiert (`intake_view` hat Vorrang); Antwort enthält `intake_view` wie Original | DEV-API-20 | `ProjectFeatureToggleTests.IntakeView` | CE-PRJ-019, CE-INT-001 | I1 |
| <a id="DT-PRJ-06"></a>**DT-PRJ-06** | K | Projects | Estimate anlegen hinterlässt bei Validierungsfehler der Punkte ein verwaistes Estimate; Estimate-Punkt löschen schreibt Activities vor der 404-Prüfung | A03 Q-19, Q-21 | korrigieren | eine Transaktion, erst validieren, dann schreiben (`TransactionBehavior`) | – | `EstimateCommandTests` | CE-PRJ-035, CE-PRJ-037 | I1 |
| <a id="DT-PRJ-07"></a>**DT-PRJ-07** | F | Projects | Estimate-Punkt mit `key = 0` nicht anlegbar | A03 E-07, Q-20 | korrigieren | `key ≥ 0` zulässig (Frontend sendet 1…n, unverändert) | DEV-API-21 | `EstimatePointValidationTests` | CE-PRJ-036 | I1 |
| <a id="DT-PRJ-08"></a>**DT-PRJ-08** | S | Projects | Projekt-Labels für jedes Workspace-Mitglied lesbar (auch geheime Projekte); Projektmitgliedschaft ohne `is_active` | A04 L1, §5.4; 05 SEC-21 | korrigieren | `PRJ(A,M,G)`, aktive Mitgliedschaft | SEC-21 | `LabelScopeTests` | CE-PRJ-028 | I1 |
| <a id="DT-PRJ-09"></a>**DT-PRJ-09** | Q | Projects | Bulk-Labels: Default-Name „Migrated“, zufällige Farbe, `ignore_conflicts` (nur angelegte Labels in der Antwort), kein `sort_order`-Hochzählen | A04 L7; 02 §5.2.7 | 1:1 mit den in 02 dokumentierten Abweichungen | siehe 02 `DEV-LBL-03`, `-05`, `-06` | DEV-LBL-03, DEV-LBL-05, DEV-LBL-06 | `BulkCreateLabelsTests` | CE-PRJ-033 | I1 |
| <a id="DT-WI-01"></a>**DT-WI-01** | S | WorkItems | Kommentar-Detail und Reaktionslisten ohne Gast-Sichtbarkeit | A04 C3, C7, C10; 05 SEC-04 | korrigieren | `PRJ(A,M,G)+VIS`; fremde → 404 | SEC-04 | `CommentVisibilityTests` | CE-WI-037, CE-WI-038 | I2 |
| <a id="DT-WI-02"></a>**DT-WI-02** | F | WorkItems | `GET {P}/issues/list/?group_by=labels__id` (u. ä.) lässt die Annotation `label_ids` weg → 500 | A04 I1 | korrigieren | ID-Arrays immer annotiert; `group_by` beeinflusst nur ausgelassene M2M-Arrays wie vorgesehen | DEV-API-22 | `WorkItemsByIdsTests.GroupByLabels` | CE-WI-011 | I2 |
| <a id="DT-WI-03"></a>**DT-WI-03** | F | WorkItems | Relation `implements` wird nicht invertiert gespeichert; `implemented_by` fehlt in der Listenantwort | A04 §5.3 Nr. 16, O11 | korrigieren | Speicherung über den Relationstyp-Katalog `work_item_relation_types` mit Gegenrichtung (01 §1.4 A9); Liste enthält `implemented_by` | DEV-API-23 | `WorkItemRelationTests.Implements` | CE-WI-033, CE-API-024 | I2 |
| <a id="DT-WI-04"></a>**DT-WI-04** | F | WorkItems | `GET {P}/issues/{issue_id}/issue-subscribers/` liefert alle Projektmitglieder statt der Abonnenten | A04 S1, O6 | korrigieren | Liste der aktiven Abonnenten in derselben Antwortform (`{"member": UserLite, "id": project_member_id}`) + `is_subscribed` | DEV-API-24 | `WorkItemSubscriberTests` | CE-WI-043 | I2 |
| <a id="DT-WI-05"></a>**DT-WI-05** | F | WorkItems | Bulk-Operationen (`bulk-archive-issues`, `bulk-delete-issues`, `issue-dates`) umgehen Model-Logik (`completed_at`, `updated_by`), Bulk-Delete ohne Kaskade und Activity | A04 A5, A6, A8, §5.3 Nr. 13 | korrigieren | Ausführung über die regulären Commands je Work Item (Kaskade, Activity, Outbox) in einer Transaktion; Antworttexte unverändert | DEV-API-25 | `WorkItemBulkTests` | CE-WI-046, CE-WI-048, CE-LV-030 | I2/I3 |
| <a id="DT-WI-06"></a>**DT-WI-06** | F | WorkItems | Archiv-Detail `GET {P}/issues/{pk}/archive/` liefert weniger Felder als das Detail (`cycle_id`, `module_ids`, `label_ids` … fehlen) | A04 A2, O14 | korrigieren | gleiche Feldmenge wie `GET {P}/issues/{pk}/` (`S-ISSUE-DETAIL`) | DEV-API-26 | `ArchivedWorkItemTests.DetailShape` | CE-WI-045 | I3 |
| <a id="DT-WI-07"></a>**DT-WI-07** | F | WorkItems | `label_ids`/`assignee_ids` enthalten Zuordnungen zu soft-gelöschten Labels/Benutzern (nur gelöschte Zwischenzeilen werden ausgeblendet) | A04 O19 | korrigieren | Zuordnungen auf gelöschte Ziele werden ausgeblendet | DEV-API-27 | `WorkItemListTests.DeletedTargets` | CE-LV-005, CE-WI-020 | I2 |
| <a id="DT-WI-08"></a>**DT-WI-08** | Q | WorkItems | Legacy-Filter `logged_by` → 500; Legacy-`None`-Filter mit Join-Quirk; Gruppierungs-Quirks (0→1-Gruppensumme, fehlende leere M2M-Gruppen, `total_count` zählt Paare) | A04 §5.3 Nr. 1–9; 02 `DEV-FLT-001/-002`, `DEV-GRP-001…005`, O-D02-04 | nach 02; Empfehlung: `DEV-GRP-001` (0→1) nach Z-12 korrigieren (Rückmeldung §9) | siehe 02 §3.11 | DEV-FLT-001, DEV-FLT-002, DEV-GRP-001…005 | `WorkItemQueryParityTests` (02 AK-12) | CE-LV-005, CE-LV-010 | I2 |
| <a id="DT-WI-09"></a>**DT-WI-09** | Q | WorkItems | Datumsfilter „heute“ = UTC-Datum; `__date`-Vergleiche in Nutzer-TZ | A04 §5.3 Nr. 10, O10; 02 D02-ADR-21 | 1:1 | wie 02 D02-ADR-21 | – | `LegacyFilterParserTests` | CE-LV-010 | I2 |
| <a id="DT-WI-10"></a>**DT-WI-10** | T | WorkItems | `GET {P}/issues/{issue_id}/issue-attachments/{pk}/` immer 500 (Methode ohne `pk`) | A04 K9 | nicht registrieren | 405 (DELETE registriert) | DEV-API-28 | `RemovedRoutesTests` | CE-WI-036 | I2 |
| <a id="DT-WI-11"></a>**DT-WI-11** | S | WorkItems | HTML-Felder (`description_html`, `comment_html`) und `description_binary` (Base64, ≤ 10 MB, Yjs-dekodierbar) | A04 §5.4, 01 ADR-030, 05 §3.17.3 | 1:1 (Schutz erhalten) + v1-Lücke schließen | `[SanitizedHtml]` auf allen `*_html`-Request-Feldern, Binärprüfung; v1-Kommentar-Anlage sanitisiert (SEC-54) | SEC-54 | `HtmlFieldsAreSanitized` (Architekturtest) | CE-OPS-017, CE-WI-005, CE-API-021 | I2 |
| <a id="DT-CYC-01"></a>**DT-CYC-01** | F | Cycles | Abgeschlossener Cycle: PATCH mit `sort_order` speichert **alle** gesendeten Felder (App), Einschränkung wirkungslos (v1) | A04 §5.3 Nr. 12, A05 B-09 | korrigieren | bei abgeschlossenem Cycle wird nur `sort_order` übernommen; andere Felder → 400 `{"error": "The Cycle has already been completed so it cannot be edited"}` (Original-Text) | DEV-API-29 | `CompletedCycleEditTests` | CE-CYC-005, CE-API-026 | I3/I6 |
| <a id="DT-CYC-02"></a>**DT-CYC-02** | F | Cycles | `GET /api/workspaces/{slug}/active-cycles/` wird vom CE-Frontend aufgerufen, existiert im CE-Backend nicht | 16 §4.3, D16-ADR-14 | bauen | neuer Endpunkt (Antwortform aus `packages/types` `ICycle[]` paginiert), Basis für B4 | DEV-API-30 | `WorkspaceActiveCyclesTests` | CE-CYC-004 | I3 |
| <a id="DT-CYC-03"></a>**DT-CYC-03** | S | Cycles | v1: Cycle/Modul löschen durch jedes Mitglied; Zuordnungslisten und Archiv für Gäste offen | 05 SEC-20, HARM-02 | korrigieren/harmonisieren | Löschen `PRJ(A)+C:Cycle`/`+C:Module`; Listen `PRJ(A,M)` | SEC-20, HARM-02 | `V1CycleModuleDeleteTests`, `V1CycleModuleListTests` | CE-API-026, CE-API-027, CE-API-029, CE-API-030, CE-API-031 | I6 |
| <a id="DT-MOD-01"></a>**DT-MOD-01** | F | ProjectModules | v1-Modul-Zuordnung: fehlerhafter Vergleich, `modules_list` als String | A05 B-10, §3.11 | korrigieren | fachlich wie App-API (Mehrfachzuordnung erlaubt) | DEV-API-31 | `V1ModuleWorkItemsTests` | CE-API-031 | I6 |
| <a id="DT-MOD-02"></a>**DT-MOD-02** | Q | ProjectModules | `PATCH {P}/modules/{module_id}/module-links/{pk}/` ohne `url` → 400 `{"error": "Invalid URL format."}` | A04 M14 | 1:1 | wie Original (Client sendet `url` immer mit) | – | Contract-Golden | CE-MOD-005 | I3 |
| <a id="DT-INT-01"></a>**DT-INT-01** | T | Intake | `POST {P}/intakes/` (Alias `inboxes/`) defekt (Decorator auf `perform_create`); Intakes entstehen beim Aktivieren von `intake_view` | A04 N2, O7 | nicht registrieren | 405; Default-Intake `"{Projektname} Intake"` (`is_default=true`) beim Aktivieren des Features (CE-PRJ-019); Rückmeldung an 05 (`project.intake.create` → entfällt) | DEV-API-32 | `IntakeLifecycleTests` | CE-INT-001 | I3 |
| <a id="DT-INT-02"></a>**DT-INT-02** | S | Intake | Intake-Objekt lesen/ändern ohne Rollenprüfung | A04 N3, N4; 05 SEC-03 | korrigieren | `PRJ(A,M)` lesen, `PRJ(A)` ändern | SEC-03 | `IntakeObjectPermissionTests` | CE-INT-001 | I3 |
| <a id="DT-INT-03"></a>**DT-INT-03** | F | Intake | v1-Intake-POST → 500, wenn `intake_view=true`, aber kein Intake existiert; bei mehreren Intakes nimmt v1 das erste statt `is_default` | A05 B-12, O-13 | korrigieren | Default-Intake wird bei Bedarf angelegt; Auswahl über `is_default` | DEV-API-33 | `V1IntakeTests` | CE-API-025 | I6 |
| <a id="DT-INT-04"></a>**DT-INT-04** | S | Intake | v1-Intake-Detail/-Ändern/-Löschen weiter als App; Statusänderung nur Admin (Kommentar sagt Admin+Member) | A05 B-11; 05 HARM-01 | harmonisieren | `PRJ(A,M,G)+C:Issue+VIS` (lesen), `PRJ(A)+C:Issue` (ändern/löschen) | HARM-01 | `V1IntakeHarmonizationTests` | CE-API-025 | I6 |
| <a id="DT-INT-05"></a>**DT-INT-05** | F | Intake | Space-Intake-Einreichung speichert Priorität `low` als Default statt `none` | A05 S-27, O-12 | korrigieren | Default `none` (wie Check-Default und App) | DEV-API-34 | `SpaceIntakeSubmitTests` | CE-SPACE-006 | I6 |
| <a id="DT-INT-06"></a>**DT-INT-06** | S | Intake | Space-Intake-Liste/-Detail zeigt alle Einreichungen jedem Angemeldeten; Intake-Erstellung übernimmt Sanitizer-Ergebnis ohne Fehlerprüfung | A05 B-25; 05 SEC-18, SEC-55 | korrigieren | nur eigene Einreichungen; Sanitizer-Fehler → 400 | SEC-18, SEC-55 | `SpaceIntakeOwnerTests`, `IntakeSanitizerTests` | CE-SPACE-006, CE-INT-005 | I3/I6 |
| <a id="DT-PAGE-01"></a>**DT-PAGE-01** | F | Pages | Page-Versionen werden wegen `page.description`-Bug nie erzeugt | A04 O4, §3.18.6; CE-PAGE-019 | korrigieren | Version je Besitzer im 600-s-Merge-Fenster, max. 20 (Instanz-Einstellung, ADR-001) beim Speichern der Beschreibung | DEV-API-35 | `PageVersionTrackingTests` | CE-PAGE-019 | I4 |
| <a id="DT-PAGE-02"></a>**DT-PAGE-02** | F | Pages | Page duplizieren: Labels nicht kopiert, `project_id`-Schleifenvariable | A04 G18, O15 | korrigieren | Labels und Assets im Quellprojekt kopiert; Antwort unverändert 201 `PageDetailSerializer` | DEV-API-36 | `DuplicatePageTests` | CE-PAGE-009 | I4 |
| <a id="DT-PAGE-03"></a>**DT-PAGE-03** | F | Pages | Rekursives Archivieren berücksichtigt soft-gelöschte Kinder; `archived_at` der Archiv-Antwort ist naive Server-Lokalzeit | A04 G9, O16, O17 | korrigieren | nur aktive Nachfahren; `archived_at` als `YYYY-MM-DD` (wie gespeichert) | DEV-API-37 | `ArchivePageTests` | CE-PAGE-007 | I4 |
| <a id="DT-PAGE-04"></a>**DT-PAGE-04** | F | Pages | `PATCH {P}/pages/{page_id}/` liefert bei **jedem** `Page.DoesNotExist` (z. B. ungültiger `parent`) den Text „Access cannot be updated since this page is owned by someone else“ | A04 G5 | korrigieren | ungültiger `parent` → 400 `{"parent": ["Invalid pk \"<id>\" - object does not exist."]}` (DRF-Standardtext); Zugriffsfall unverändert | DEV-API-38 | `UpdatePageTests.InvalidParent` | CE-PAGE-004 | I4 |
| <a id="DT-PAGE-05"></a>**DT-PAGE-05** | S | Pages | `labels` an Pages akzeptieren beliebige Label-IDs (auch fremder Projekte) | A04 §5.4 (G3/G5) | korrigieren | nur Labels des Page-Projekts; sonst 400 `{"labels": ["Invalid pk \"<id>\" - object does not exist."]}` | DEV-API-39 | `PageLabelScopeTests` | CE-PAGE-003, CE-PAGE-004 | I4 |
| <a id="DT-PAGE-06"></a>**DT-PAGE-06** | S | Pages | Page-Zugriff nur über aktive `project_pages`-Verknüpfung (GHSA-g49r-…, GHSA-ghcr-…) | 05 §3.18.3, §3.13.5 | 1:1 (Schutz erhalten) | `PermissionRule.PageAccess` | – | Port `test_page_guest_view_scope_app.py` | CE-PAGE-004, CE-PAGE-006 | I4 |
| <a id="DT-PAGE-07"></a>**DT-PAGE-07** | F | Pages | `POST {P}/pages/`: ungültige Referenzen (`parent` aus fremdem Projekt/nicht existent, fremde `labels`) führen zu `IntegrityError`-Abbildung oder stiller Fehlzuordnung | A04 G3, §5.4 | korrigieren | 400 mit DRF-Feldfehler je Feld (wie DT-PAGE-04/-05) | DEV-API-40 | `CreatePageTests.InvalidReferences` | CE-PAGE-003 | I4 |
| <a id="DT-RT-01"></a>**DT-RT-01** | S | Realtime | Live-Server prüft Dokumentzugriff nur beim ersten Laden, kein Read-only-Scope; Cookie als Query-Parameter; WebSocket ohne Origin-Prüfung | A12 E3, E26; 05 SEC-40…42 | korrigieren | Prüfung je Verbindung (`project.page.read` + `PAGE`), `readonly` ohne `project.page.update`, nur `Cookie`-Header, Origin-Allowlist | SEC-40, SEC-41, SEC-42 | `CollaborationAuthorizationTests`, `WebSocketOriginTests` | CE-RT-001, CE-RT-002 | I4 |
| <a id="DT-RT-02"></a>**DT-RT-02** | S | Realtime | `POST /live/convert-document/` ohne Authentifizierung über den Proxy öffentlich | A12 E8; 05 SEC-39 | entfällt als HTTP-Endpunkt | Konvertierung In-Process (`IDocumentConverter`, `Plane.Documents`); `POST /live/convert-document/` nur noch auf dem Management-Port 8081 (Diagnose/Paritätstest, 07 D07-ADR-19), über das Gateway 404 | SEC-39 | `GatewayRoutingTests.ConvertDocumentNotRouted` | CE-RT-008 | I4 |
| <a id="DT-RT-03"></a>**DT-RT-03** | F | Realtime | PDF-Export: Callout-Emoji als Dezimal-Codepoint („128161“); Mentions zeigen `entity_name` (Mentions-Endpunkt fehlt in CE); `page_locked`/`page_archived` werden nie gesendet | A12 E4, E6, E27 | korrigieren | Emoji-Glyphe; Mentions mit Anzeigenamen (In-Process-Auflösung, kein HTTP-Endpunkt `…/mentions/`); Stateless-Events/Close-Codes bei gesperrter/archivierter Page | DEV-API-41 | `PdfExportTests`, `CollaborationLockTests` | CE-PAGE-011, CE-RT-006 | I4 |
| <a id="DT-NOTIF-01"></a>**DT-NOTIF-01** | F | Notifications | `snoozed=false` zeigt noch gesnoozte; `subscribed`-Subquery vergleicht `IssueAssignee.pk` mit `issue_id` | A03 N-01, Q-22, Q-23 | korrigieren | aktiv gesnoozte (`snoozed_till > now`) ausgeblendet; Subquery über `issue_id` | DEV-API-42 | `NotificationFilterTests` | CE-NOTIF-005 | I5 |
| <a id="DT-NOTIF-02"></a>**DT-NOTIF-02** | F | Notifications | `POST {W}/users/notifications/mark-all-read/`: `type` erwartet `watching` statt `subscribed`, kein Komma-Split | A03 N-10, Q-24 | korrigieren | Komma-Liste mit denselben Werten wie N-01 (`assigned`, `created`, `subscribed`) | DEV-API-43 | `MarkAllReadTests` | CE-NOTIF-006 | I5 |
| <a id="DT-ANA-01"></a>**DT-ANA-01** | F | Analytics | `PATCH {W}/analytic-view/{pk}/` setzt `query` auf `{}`; Default-Analytics summiert Legacy-Feld `point` | A03 AN-05, AN-09, Q-25, Q-26 | korrigieren | `query` aus `query_dict` neu berechnet; Summen über `estimate_point.value` (Schätzsystem `points`) | DEV-API-44 | `LegacyAnalyticsTests` | CE-ANA-009 | I5 |
| <a id="DT-HOME-01"></a>**DT-HOME-01** | F | Home | Recents nach erstem statt letztem Besuch sortiert (`created_at` statt `visited_at`) | A03 W-61, Q-37 | korrigieren (Z-12) | Sortierung `visited_at DESC`; Antwortform unverändert | DEV-API-45 | `RecentVisitsTests.Order` | CE-HOME-005 | I5 |
| <a id="DT-AI-01"></a>**DT-AI-01** | F | Assistant | Unsplash-URL mit `page=$1`, kein Timeout; Anthropic/Gemini-Provider funktionieren nicht, fehlender `prompt` → 500 | A03 EXT-01…03, Q-27, Q-28 | korrigieren | korrekte Seitenzahl, Timeout über SSRF-Client `unsplash`; `IChatClient` mit OpenAI-kompatiblem Provider (`LLM_PROVIDER`, `LLM_BASE_URL`), fehlender `prompt` = `""` | DEV-API-46 | `UnsplashTests`, `AiAssistantTests` | CE-AI-001, CE-AI-002 | I6 |
| <a id="DT-SRCH-01"></a>**DT-SRCH-01** | S | Search | Mention-Suche mit `project_id` ohne Mitgliedschaftsprüfung; inaktive Mitgliedschaften zählen in der globalen Suche | A03 Q-35, Q-36; 05 SEC-56 | korrigieren | `PRJ(A,M,G)` für das angefragte Projekt; Filter `is_active` + `deleted_at IS NULL` | SEC-56 | `SearchScopeTests` | CE-SRCH-001, CE-SRCH-002 | I2/I5 |
| <a id="DT-SRCH-02"></a>**DT-SRCH-02** | Q | Search | Globale Suche begrenzt nur `issue`/`intake` auf 100, alle anderen Typen unbegrenzt | A03 SR-01 | 1:1 | wie Original; Lastgrenze über 15 §3.12 beobachtet | – | Contract-Golden | CE-SRCH-001 | I5 |
| <a id="DT-AST-01"></a>**DT-AST-01** | A | Assets | Legacy-Asset-Endpunkte v1 (`{W}/file-assets/`, `/api/workspaces/file-assets/{workspace_id}/{asset_key}/…`, `/api/users/file-assets/…`) für Altdaten; GET-Varianten 500 | A03 A-01…A-07, Q-32; 00 ADR-003 (Greenfield) | nicht portieren | 404; die Frontend-Aufrufer (`deleteOldWorkspaceAsset`, `restoreOldEditorAsset`, `deleteOldUserAsset`) werden nur für Legacy-URLs ausgelöst, die es in `funk.` nicht gibt | DEV-API-47 | `RemovedRoutesTests.LegacyAssets` | CE-OPS-013 | I1 |
| <a id="DT-AST-02"></a>**DT-AST-02** | S | Assets | Workspace-Asset-Download ohne Projektprüfung; `entity_identifier` nicht validiert | A03 Q-33, Q-34; 05 SEC-56 | korrigieren | Download prüft `project.project.read` des Asset-Projekts; unbekannter `entity_identifier` → 400 `{"error": "Invalid entity identifier"}` | SEC-56 | `AssetScopeTests` | CE-OPS-012, CE-OPS-013 | I1 |
| <a id="DT-AST-03"></a>**DT-AST-03** | A | Assets | Presigned POST direkt an S3/MinIO (silo) mit Request-Host-Trick | 01 ADR-026, 14 §3.7.6 | angepasst (Vertrag gleich) | `upload_data.url/fields` unverändert; zusätzliche Endpunkte `POST /api/assets/v2/upload/{token}/` (Proxy-Modus) und `GET /api/assets/v2/files/{token}/` (Dateisystem-Provider), HMAC mit `Plane:Security:SigningKey` | – | `StorageContractTests` (S8) | CE-OPS-012 | I1 |
| <a id="DT-AST-04"></a>**DT-AST-04** | S | Assets | Space-Assets ändern/löschen/wiederherstellen ohne Eigentümerprüfung; GET liefert Bilder interner Kommentare | A05 B-24; 05 SEC-19, SEC-51 | korrigieren | `AUTH+BOARD+OWN`; GET nur Board-/Work-Item-/EXTERNAL-Kommentar-Assets | SEC-19, SEC-51 | `SpaceAssetOwnerTests`, `SpaceAssetVisibilityTests` | CE-SPACE-007 | I6 |
| <a id="DT-SPACE-01"></a>**DT-SPACE-01** | T | PublicSpace | `GET /api/public/workspaces/{slug}/project-boards/` immer 500 (Signatur passt nicht) | A05 S-04, B-20 | nicht registrieren | 404 | DEV-API-48 | `RemovedRoutesTests` | CE-SPACE-002 | I6 |
| <a id="DT-SPACE-02"></a>**DT-SPACE-02** | F | PublicSpace | Reaktions-/Vote-Listen im Space immer `[]`; Reaktions-`avatar_url` aus Votes berechnet | A05 S-12, S-18, B-19, B-21; A11 K18 | korrigieren | Listen liefern die Einträge des Work Items (Board-Auflösung über `anchor`); `avatar_url` aus dem Reaktions-Akteur | DEV-API-49 | `SpaceReactionVoteListTests` | CE-SPACE-026, CE-SPACE-027, CE-SPACE-028 | I6 |
| <a id="DT-SPACE-03"></a>**DT-SPACE-03** | F | PublicSpace | Space-Issue-Detail liefert 200 `null` statt 404; `description_binary` als Rohbytes in `.values()` (möglicher 500) | A05 S-06, B-22, O-06 | korrigieren | 404 `{"error": "Issue not found"}` (Text aus Space-Views); Feld `description_binary` entfällt (vom Frontend nicht genutzt, A11 B13) | DEV-API-50 | `SpaceWorkItemDetailTests` | CE-SPACE-004 | I6 |
| <a id="DT-SPACE-04"></a>**DT-SPACE-04** | F | PublicSpace | Space-Issue-Liste: `group_by ∈ {target_date, start_date, created_by}` → 500 | A05 S-05 | korrigieren | Gruppierung wie App-Engine (02 §3.11) | DEV-API-51 | `SpaceWorkItemListTests.GroupBy` | CE-SPACE-003 | I6 |
| <a id="DT-SPACE-05"></a>**DT-SPACE-05** | S | PublicSpace | Vote-Wert unvalidiert; Vote-Löschen ohne Board-Schalter; `deploy_boards.is_disabled` nicht ausgewertet | A05 B-23, B-26; 05 SEC-52, SEC-53 | korrigieren | `vote ∈ {-1, 1}` (400 `{"vote": ["Invalid vote."]}`); `BOARD`-Regel auch für DELETE; deaktiviertes Board → 404 `{"error": "Project is not published"}` | SEC-52, SEC-53 | `SpaceVoteTests`, `SpaceBoardDisabledTests` | CE-SPACE-028, CE-SPACE-002 | I6 |
| <a id="DT-SPACE-06"></a>**DT-SPACE-06** | Q | PublicSpace | Anonymer Anchor-Lookup über `/api/public/workspaces/{slug}/projects/{project_id}/anchor/` (Legacy-Redirect) | A05 S-03, A11 §3.18 | 1:1 | unverändert (nur veröffentlichte, nicht deaktivierte Boards) | – | Contract-Golden | CE-SPACE-016 | I6 |
| <a id="DT-INST-01"></a>**DT-INST-01** | A | Instance | `latest_version` über GitHub-API, Telemetrie standardmäßig aktiv | A05 B-32, CE-INST-001; 00 ADR-004 | entfällt/angepasst | `latest_version` = `current_version`; keine ausgehenden Aufrufe; `is_telemetry_enabled` steuert nur lokale OTel-Metriken (Default `false`) | DEV-API-52 | `InstanceInfoContractTests.NoPhoneHome` | CE-INST-001 | I0 |
| <a id="DT-INST-02"></a>**DT-INST-02** | S | Instance | Anonyme Ausgabe aller Instanzfelder (`whitelist_emails`, `instance_id`, `domain` …) | A05 B-27; 05 SEC-49 | korrigieren | anonym reduzierte Feldmenge, Instanz-Admins alle Felder | SEC-49 | `InstanceAnonymousFieldsTests` | CE-INST-003 | I0 |
| <a id="DT-INST-03"></a>**DT-INST-03** | A | Instance | Erst-Einrichtung per Admin-Sign-up (Formular, Passwort); `sign-up-screen-visited` anonym schreibbar | A05 I-09, I-11; 05 N-13, SEC-48 | ersetzt | `POST /api/instances/admins/setup/` (JSON, angemeldeter Instanz-Admin, atomar `FOR UPDATE`); `sign-up-screen-visited` → 404 | DEV-API-02, SEC-48 | `InstanceBootstrapConcurrencyTests` | CE-INST-006 | I0 |
| <a id="DT-INST-04"></a>**DT-INST-04** | A | Instance | Instanz-Admins per API anlegen/löschen (auch den letzten) | A05 I-03…I-05, B-28; 05 N-12 | angepasst | `GET /api/instances/admins/` ist Spiegel der Keycloak-Rolle (+ `"source": "keycloak"`); POST/DELETE → 404 | DEV-API-02, SEC-48 | `InstanceAdminMirrorTests` | CE-INST-004 | I0 |
| <a id="DT-INST-05"></a>**DT-INST-05** | F | Instance | Workspace-Anlage im God Mode ohne Seed-Daten und ohne die Prüfungen der App-Anlage | A05 I-18, B-30 | korrigieren | gemeinsamer Command `CreateWorkspaceCommand` (Plane.Workspaces.Contracts) inkl. Demo-Seed (CE-WS-002) und Slug-Regeln | DEV-API-53 | `InstanceWorkspaceCreateTests` | CE-INST-029, CE-WS-002 | I6 |
| <a id="DT-INST-06"></a>**DT-INST-06** | K | Instance | `GET /api/instances/` ohne Instanz-Datensatz liefert flaches Objekt (Endlos-Spinner) | A05 I-01, B-31 | korrigieren | Migrator legt die Instanz garantiert an (01 §3, `InstanceBootstrap`) | – | `MigratorInstanceBootstrapTests` | CE-INST-003, CE-INST-009 | I0 |
| <a id="DT-INST-07"></a>**DT-INST-07** | S | Instance | God-Mode-Secrets (SMTP-Passwort, LLM-Key, Unsplash-Key) im Klartext an den Browser | A11 O8; 05 SEC-58 | bewusst beibehalten (Parität) | nur `INST`, `Cache-Control: no-store`, Log-Redaktion; Option `Plane:Security:MaskInstanceSecrets` liefert `"********"` | SEC-58 | `InstanceSecretsResponseTests` | CE-INST-018, CE-INST-025, CE-INST-026 | I6 |
| <a id="DT-INST-08"></a>**DT-INST-08** | A | Instance | 36 Instanz-Konfigurationsschlüssel inkl. OAuth-/Passwort-Schlüssel | A05 §2.7.4; 02 §3.16; 05 §4.4 | angepasst | 14 Schlüssel (05 §4.4); `PATCH` mit entfallenem Schlüssel wird wie im Original ignoriert (nur existierende Keys) | DEV-API-02 | `InstanceConfigurationTests` | CE-INST-002, CE-INST-017 | I6 |
| <a id="DT-V1-01"></a>**DT-V1-01** | T | PublicApi | v1-Estimates (`{V1P}/estimates/…`, 8 Methoden) implementiert, aber nicht geroutet (`api/urls/estimate.py` nicht eingebunden); 05-Matrix führt sie als Endpunkte | A05 V-DEAD-01…08, B-01; Original `apps/api/plane/api/urls/__init__.py` | 1:1 (nicht registrieren) | 404; Pfad für eine spätere v1-Erweiterung reserviert (§6); Rückmeldung an 05 (Matrixzeilen als „nicht geroutet“) | – | `V1RouteInventoryTests` | CE-API-009 | I6 |
| <a id="DT-V1-02"></a>**DT-V1-02** | T | PublicApi | `IssueDetailAPIEndpoint.put` (Upsert per `external_id`) und `ModuleIssueDetailAPIEndpoint.get` implementiert, per `http_method_names` nicht erreichbar | A05 V-DEAD-09, V-DEAD-10, B-02 | 1:1 (nicht registrieren) | 405 | – | `V1RouteInventoryTests` | CE-API-017, CE-API-031 | I6 |
| <a id="DT-V1-03"></a>**DT-V1-03** | T | PublicApi | DRF-`APIRootView` `GET {V1W}/` und Format-Suffix-Routen `.json` (DefaultRouter) | A05 V-RTR-01, V-RTR-02 | nicht registrieren | 404 | DEV-API-54 | `V1RouteInventoryTests` | CE-API-013, CE-API-014 | I6 |
| <a id="DT-V1-04"></a>**DT-V1-04** | A | PublicApi | OpenAPI per drf-spectacular (3.0.3), Swagger-UI/Redoc laden Assets vom CDN | A05 §2.1.9, W-03…05; 01 ADR-051 | angepasst | gleiche Pfade `/api/schema/`, `/api/schema/swagger-ui/`, `/api/schema/redoc/`; OpenAPI 3.1 (`Microsoft.AspNetCore.OpenApi`), Scalar offline gebündelt; `operationId` wie Original | DEV-API-55 | `OpenApiDocumentTests` (02 AK-22) | CE-API-004 | I6 |
| <a id="DT-V1-05"></a>**DT-V1-05** | F | PublicApi | v1-Einladungen und -Stickies ohne API-Key-Rate-Limit | A05 B-04; 05 B-04 | korrigieren | Policy `api_key` für die gesamte Oberfläche V1 inkl. Header | DEV-API-56 | `RateLimitTests` (02 AK-15) | CE-API-002 | I6 |
| <a id="DT-V1-06"></a>**DT-V1-06** | S | PublicApi | v1-Berechtigungslücken (Anhänge, Kommentar-Autor, Summary, Stickies, Work-Item-Löschen) und Harmonisierungen (Mitgliederliste, Einladungen, Projekt-Archiv, Projekt ändern/löschen) | A05 B-05…B-08, B-18; 05 SEC-08…10, -13, -14, HARM-03…06 | korrigieren/harmonisieren | siehe 05 §3.18.1 (Spalte „Ziel-Prüfung“ in §4) | SEC-08, SEC-09, SEC-10, SEC-13, SEC-14, HARM-03, HARM-04, HARM-05, HARM-06 | siehe 05 §3.18.1 | CE-API-006…008, CE-API-011, CE-API-013, CE-API-014, CE-API-017, CE-API-021, CE-API-023 | I6 |
| <a id="DT-V1-07"></a>**DT-V1-07** | F | PublicApi | v1-Mitgliederlisten enthalten inaktive Mitglieder ohne Kennzeichen | A05 B-14, §3.13 | korrigieren | nur aktive Mitgliedschaften (wie App-API) | DEV-API-57 | `V1MemberListTests` | CE-API-011, CE-API-012 | I6 |
| <a id="DT-V1-08"></a>**DT-V1-08** | F | PublicApi | v1-Einladungen ohne Token und ohne E-Mail | A05 B-15, O-09 | korrigieren | gemeinsamer Einladungs-Command (`CreateWorkspaceInvitationsCommand`) inkl. Token und Mail-Job; v1-Antwortform unverändert | DEV-API-58 | `V1InvitationTests.SendsMail` | CE-API-013 | I6 |
| <a id="DT-V1-09"></a>**DT-V1-09** | F | PublicApi | v1-Generic-Assets: `asset_url` mit `issues/None`; Server-Assets und Generic-Asset-POST/GET → 500 (`S3Storage(is_server=True)`), POSTs hinterlassen verwaiste Assets | A05 B-16, B-17a, O-01 | korrigieren | Soll-Verhalten aus Docstrings/Doku (Presigned Upload, `asset_url` ohne `None`-Segment); kein verwaistes Asset bei Fehler | DEV-API-59 | `V1AssetTests` | CE-API-015, CE-API-016 | I6 |
| <a id="DT-V1-10"></a>**DT-V1-10** | F | PublicApi | `limit`/`size` per `int()` ohne Fehlerbehandlung → 500 | A05 B-17 | korrigieren | 400 `{"error": "Invalid limit"}` bzw. `{"error": "Invalid size"}` (neue Texte, dokumentiert) | DEV-API-60 | `V1ParameterValidationTests` | CE-API-016, CE-API-019 | I6 |
| <a id="DT-V1-11"></a>**DT-V1-11** | F | PublicApi | v1-Projekt-PATCH meldet Fehler zu `default_state`/`estimate` als 409 „identifier already taken“; `IntegrityError` ohne „already exists“ → 500 (View liefert `None`) | A05 V-PRJ-05, B-13 | korrigieren | 400 `{"default_state": ["Default state should be a state in the project"]}` bzw. `{"estimate": ["Estimate should be a estimate in the project"]}`; sonstige Integritätsfehler → 400 `{"error": "The payload is not valid"}` | DEV-API-61 | `V1ProjectUpdateTests.Errors` | CE-API-006 | I6 |
| <a id="DT-V1-12"></a>**DT-V1-12** | Q | PublicApi | v1-Projektliste enthält archivierte Projekte, Lite-Liste nur mit `include_archived` | A05 O-11 | 1:1 | wie Original | – | Contract-Golden | CE-API-006 | I6 |
| <a id="DT-V1-13"></a>**DT-V1-13** | A | PublicApi | nur API-Key-Authentisierung | 01 ADR-018, 05 D05-ADR-15 | vorbereitet (🧱 H1) | Schema `Bearer` (Keycloak-JWT, Audience `plane-api`) registriert, `Plane:Auth:Bearer:Enabled=false` → `Authorization: Bearer …` ergibt 401 `{"detail": "Authentication credentials were not provided."}` | – | `BearerSchemeDisabledTests` | CE-API-001 | I0 |
| <a id="DT-WH-01"></a>**DT-WH-01** | F | Webhooks | `created`-Events, deren Task vor dem Commit läuft, werden still verworfen (`ObjectDoesNotExist`) | A07 WH1, WH2; 06 D06-ADR-15 | korrigieren | Auslösung als Projektion der Integration-Events aus der Outbox **nach** Commit (06 §3.14.2); bis zur Zustellung gelöschtes Objekt → Zustellung entfällt still (WH2, 1:1) | DEV-API-62 | `WebhookOutboxTests.CreatedAfterCommit` | CE-WH-007 | I6 |
| <a id="DT-WH-02"></a>**DT-WH-02** | Q | Webhooks | `data` ist der DB-Stand zum Zustellzeitpunkt, nicht zum Ereigniszeitpunkt | A07 WH3 | 1:1 | Payload-Laden im Dispatcher (`WebhookPayloadBuilder`) zum Zustellzeitpunkt | – | `WebhookPayloadTests` | CE-WH-008 | I6 |
| <a id="DT-WH-03"></a>**DT-WH-03** | Q | Webhooks | HTTP 4xx/5xx des Empfängers gelten als Erfolg (kein Retry, keine Deaktivierung); Retry nur bei Netzwerkfehlern (max. 6 Versuche, Backoff 0…600 s) | A07 §2.10.4, WH4 | 1:1 | wie Original; Option `Plane:Webhooks:RetryOnServerError` (Default `false`) für Betreiber | – | `WebhookRetryTests` | CE-WH-007, CE-WH-009 | I6 |
| <a id="DT-WH-04"></a>**DT-WH-04** | F | Webhooks | `X-Plane-Delivery` je Versuch neu → Empfänger können Wiederholungen nicht deduplizieren | A07 WH6; 06 §3.14.4 | korrigieren | eine Delivery-ID (UUIDv7) je Zustellung, über alle Versuche stabil | DEV-WH-001 (06) | `WebhookHeaderTests.StableDeliveryId` | CE-WH-008 | I6 |
| <a id="DT-WH-05"></a>**DT-WH-05** | F | Webhooks | Zustellprotokoll speichert Header/Body als Python-Repr; `request_method` enthält die Aktion | A07 WH8, WH9; 06 §3.14.1 | korrigieren (Inhalt), 1:1 (`request_method`) | `request_headers`/`request_body`/`response_headers` als JSON-Text; `request_method` enthält wie im Original die Aktion (`created`/`updated`/`deleted`); `GET {W}/webhook-logs/{webhook_id}/` liefert diese Felder unverändert benannt | DEV-WH-002 (06) | `WebhookLogTests` | CE-WH-010 | I6 |
| <a id="DT-WH-06"></a>**DT-WH-06** | K | Webhooks | Signatur `hex(HMAC-SHA256(secret, json.dumps(payload)))` mit Python-Defaults (Trenner `", "`/`": "`, `ensure_ascii=True`); Body von `requests` mit denselben Defaults erzeugt | A07 §2.10.4; 06 §3.14.4 | Semantik 1:1, Bytes abweichend | Body kompakt mit `System.Text.Json` (snake_case), Signatur `HexLower(HMACSHA256(UTF8(secret), gesendete Bytes))` – Empfänger, die über die Roh-Bytes prüfen (dokumentierter Weg), bleiben kompatibel | DEV-WH-003 (06) | `WebhookSignatureGoldenTests` (D15-SEC-09) | CE-WH-008 | I6 |
| <a id="DT-WH-07"></a>**DT-WH-07** | Q | Webhooks | Nicht ausgelöste Ereignisse (Work-Item-/Cycle-/Modul-/Kommentar-Löschung, Archivierung, Zuordnungen, Intake, Links, Anhänge, Reaktionen); `action` = `created`/`updated`/`deleted` | A07 §2.10.3, WH7 | 1:1 | CE löst genau die Ereignisse aus A07 §2.10.3 aus (Tabelle §4.27); Erweiterung nur über `IWebhookEventSource` (E-08) | – | `WebhookEventMatrixTests` | CE-WH-001, CE-WH-008 | I6 |
| <a id="DT-WH-08"></a>**DT-WH-08** | S | Webhooks | SSRF-Schutz (Blockliste, IP-Pinning, keine Redirects, kein Proxy) und Loop-Guard über Request-Host | A07 §2.11, A06 §2.14; 05 SEC-31 | 1:1 + Härtung | `SsrfSafeHttpHandler` (Client `webhooks`); Loop-Guard aus `Plane:Urls:*` statt `Host`-Header | SEC-31 | `SsrfSafeHttpHandlerTests`, `WebhookLoopGuardTests` | CE-WH-011 | I6 |

Die vergebenen Abweichungs-IDs `DEV-API-05…62` mit Kurzbeschreibung stehen in §4.29. Die Zuordnung DT → Endpunktzeilen steht in §4 (Spalte „Abw./DT“) und in `endpoints.json` (`dt`).

### 3.14 OpenAPI

#### 3.14.1 Dokumente und Endpunkte

| Dokument | Inhalt | Auslieferung | Schalter | Build-Artefakt |
|---|---|---|---|---|
| `v1` | Oberfläche V1 (alle registrierten v1-Zeilen außer Alias-Duplikaten, die das Original-Schema ebenfalls enthält – Abgleich per Golden), Security-Schema `ApiKeyAuthentication` (`apiKey`, Header `X-API-Key`, Beschreibung wie Original) | EP-0711 `GET /api/schema/` (wie drf-spectacular: Default YAML mit `Content-Type: application/vnd.oai.openapi`, `?format=json` → `application/vnd.oai.openapi+json`), EP-0713 `GET /api/schema/swagger-ui/`, EP-0712 `GET /api/schema/redoc/` – beide UIs liefern Scalar (offline gebündelt, keine CDN-Assets, DT-V1-04) | `Plane:OpenApi:Enabled` (Default `false`, wie `ENABLE_DRF_SPECTACULAR=0`); aus → 404 | `src/hosts/Plane.Api/openapi/v1.json` |
| `internal` | Oberflächen App, Space, Instance, Auth (nur JSON-Endpunkte), Integrations | **nicht** ausgeliefert in Produktion; in `Development`/`Test` unter EP-0732 `GET /api/schema/internal/` (JSON) | nur `Development`/`Test` | `src/hosts/Plane.Api/openapi/internal.json` |

Die OpenAPI-Routen stehen in §4.19. Die Auslieferung liest das Dokument über `IOpenApiDocumentProvider` (keyed nach Dokumentname, .NET 10 ⚠ in S0 bestätigen) und serialisiert per `Microsoft.OpenApi` als YAML oder JSON. Die Build-Artefakte erzeugt `dotnet build` über `Microsoft.Extensions.ApiDescription.Server` (`OpenApiGenerateDocumentsOnBuild=true`, `OpenApiDocumentsDirectory=openapi`); CI prüft per `git diff --exit-code src/hosts/Plane.Api/openapi/` (Drift = Fehler, Aktualisierung im selben PR).

#### 3.14.2 Inhalt `v1` (Parität zum Original-Schema)

| Aspekt | Festlegung |
|---|---|
| Version | OpenAPI 3.1 (Original 3.0.3; DT-V1-04, `DEV-API-55`) |
| `info` | `title` „The funk. REST API“, `description` „The funk. REST API“ (ohne Verweis auf developers.plane.so), `version` `0.0.1`, `license` „GNU AGPLv3“ mit URL des `funk.`-Repos, `contact` aus `Plane:OpenApi:Contact` (Default leer) – Branding nach ADR-009B (`BRAND-API-01`) |
| `servers` | aus `Plane:OpenApi:Servers` (Default: `Plane:PublicBaseUrl`); Original-Einträge `localhost:8000`/`api.plane.so` entfallen |
| Pfadfilter | nur `/api/v1/`, **kein** `PUT`, keine Pfade mit `server` (Port `preprocess_filter_api_v1_paths`) |
| Tags | 14 Tags wie Original, gleiche Namen und Reihenfolge: `Assets`, `Cycles`, `Intake`, `Labels`, `Members`, `Modules`, `Projects`, `States`, `Users`, `Work Item Activity`, `Work Item Attachments`, `Work Item Comments`, `Work Item Links`, `Work Items`; Beschreibungen ohne Produktnamen „Plane“ |
| `operationId` | wie Original (`list_work_items`, `create_label`, … – Spalte `operation_id` in `endpoints.json`, wo bekannt); Golden `tests/contracts/openapi/v1.original.json`, einmalig erzeugt per `manage.py spectacular --file v1.original.json` am `ORIGINAL_SHA` mit `ENABLE_DRF_SPECTACULAR=1` |
| Parameter | Pfad- und Query-Parameter mit Original-Namen und -Beschreibungen aus dem Golden (häufigste: `cursor`, `per_page`, `order_by`, `fields`, `expand`, `external_id`, `external_source`, `search`, `limit`, `workspace_search`, `project_id`, `cycle_view`, `module_view`) |
| Schemas | Komponentennamen wie Original-Serializer (Beispiele `Issue`, `IssueRequest`, `Label`, `PaginatedIssueResponse`; vollständige Liste = `components.schemas` des Goldens) über `OpenApiSchemaNameTransformer` (`[OpenApiSchemaName("Issue")]` an den v1-DTOs) |
| Beispiele | aus `utils/openapi/examples.py` übernommen (Werte ohne „Plane“-Produktnamen) |

`OpenApiDocumentTests` (`tests/Plane.PublicApi.Tests/OpenApi/`, `02` AK-22): (1) Menge (Pfad, Methode) von `v1.json` = Menge des Originals minus nicht registrierte Zeilen (DT-V1-01/-02/-03); (2) `operationId`, Tags, Parameternamen je Operation gleich; (3) jede Response-Schema-Eigenschaft des Originals existiert (Typ-Kompatibilität `string`/`integer`/`number`/`boolean`/`array`/`object`, `nullable` → `type: [x, "null"]`); (4) `info`/`servers` gemäß Tabelle.

#### 3.14.3 Konfiguration (Skelett §5.5)

`AddPlaneOpenApi()` in `Plane.PublicApi` registriert `AddOpenApi("v1", …)` und `AddOpenApi("internal", …)` mit `ShouldInclude = d => d.ActionDescriptor.EndpointMetadata.OfType<SurfaceMetadata>().Any(m => m.Surface == ApiSurface.V1)` bzw. `!= V1`, Document-Transformer `V1DocumentInfoTransformer`, Operation-Transformer `OriginalOperationIdTransformer` (liest `OriginalOperationIdMetadata`, gesetzt per `.WithOriginalOperationId("list_work_items")`), `ApiKeySecuritySchemeTransformer` und `RemovePutOperationsTransformer`.

### 3.15 TypeScript-Typen und Client für Angular

| Baustein | Festlegung |
|---|---|
| Services | 1:1-Port der Original-Services (`apps/web/services/**`, `packages/services/src/**`, `apps/space/**/services`, `apps/admin/**/services`) nach `frontend/libs/shared/services/` bzw. `frontend/libs/<app>/services/` (`08` §3.5); keine generierten Services (ADR-047) |
| Typen | 1:1-Port von `packages/types` nach `frontend/libs/shared/types/` (`08`) |
| Generierte Typen | `frontend/tools/contract-check/` (eigenes `package.json`, TypeScript 5.x, `openapi-typescript` 7.x): `pnpm --filter contract-check generate` erzeugt `generated/internal.d.ts` und `generated/v1.d.ts` aus `src/hosts/Plane.Api/openapi/*.json` |
| Typ-Prüfung | `frontend/tools/contract-check/checks/*.check.ts`: je Endpunkt mit Frontend-Aufruf eine Zuweisungsprüfung `AssertAssignable<ResponseOf<"/api/workspaces/{slug}/projects/{project_id}/issue-labels/", "get">, IIssueLabel[]>` (Antwort des Servers muss dem Frontend-Typ zuweisbar sein) und umgekehrt für Request-Bodies; Ausführung `tsc --noEmit` im CI-Job `frontend` (Gate L0, `15` §2) |
| Aufrufinventar | `frontend/tools/contract-check/inventory.ts` extrahiert per `ts-morph` alle Service-Aufrufe (Methode, Pfad-Template, Query-Schlüssel) und schreibt `generated/frontend-calls.json`; `contract-check verify-catalog` prüft: (a) jeder Aufruf trifft eine Zeile in `endpoints.json` mit `registered = true` **oder** steht in §4.26 (bewusst nicht gebaute Aufrufe, Datei `frontend/tools/contract-check/allowed-missing.json`); (b) jede registrierte App-/Space-/Instance-Zeile ohne Aufruf hat in `endpoints.json` eine Begründung (`decision` ≠ `frontend`) |
| Heuristik ablösen | Das Feld `frontend_call_detected` in `endpoints.json` ist eine Erstschätzung per Pfadvergleich; maßgeblich ist ab I0 `generated/frontend-calls.json` (`08` AK-D08-16). Abweichungen werden im Katalog korrigiert (neue Spalte, keine Umnummerierung) |
| Fehlerform im Client | Services werfen `{ response: { status, data, headers } }` wie Axios (`08` AK-D08-16), damit portierter Store-Code `error.response.data` (`error`, `detail`, `error_code`) unverändert liest |

### 3.16 Contract-Tests gegen das Original

| Ebene | Werkzeug | Abdeckung (Soll) | Quelle der Soll-Liste | ab |
|---|---|---|---|---|
| Route-Inventar | `RouteInventoryTests` (`tests/Plane.AppHost.Tests/Routing/`) | 100 % aller Zeilen bis `CURRENT_INCREMENT`: registrierte Zeilen existieren (Methode + Route-Template + Name `EP-nnnn`), keine Route ohne Zeile, nicht registrierte Zeilen liefern `target_status` mit Original-Körper | `endpoints.json` | I0 |
| Metadaten | `RouteInventoryTests.MetadataMatchesCatalog` | Permission-Key, Pagination-Modus, Read-Replica, Rate-Limit-Policy, Cache-Control, `WithOriginalContract` je Zeile | `endpoints.json`, `05-permission-matrix.json` | I0 |
| Parität | Parity-Harness (`15` §3.6) | ≥ 1 Szenario je registrierter Zeile; Fehlerfälle: ≥ 1 Berechtigungsfehler je Permission-Key-Gruppe, ≥ 1 Validierungsfehler je Endpunkt mit Body, jeder Text aus `documented_bodies` mindestens einmal | `endpoints.json`; `coverage --fail-under 100` ab I7 | I0 (5 Endpunkte), danach je Inkrement alle Zeilen des Inkrements |
| Abweichungen | `deviations.yaml` | jede DT-Zeile mit `dev` ≠ „–“ und Vertragswirkung hat ≥ 1 Eintrag; ungenutzte Einträge brechen das Gate | `_data/04-decisions.json` | I0 |
| OpenAPI | `OpenApiDocumentTests` | §3.14.2 | `v1.original.json` | I6 |
| TS-Typen | `contract-check` | §3.15 | `generated/frontend-calls.json` | I0 |
| Webhook-Ausgang | `WebhookContractTests` (`tests/Plane.Webhooks.Tests/Contract/`) | je Ereignis aus §3.17.1 ein Golden des Original-Payloads (aufgezeichnet mit `tools/parity/webhook-sink`), Vergleich nach Normalisierung N1–N12 und Signaturprüfung | `06` §3.14.2 | I6 |
| Live | Protokolltests (`07` §7) | alle Live-Zeilen | `endpoints.json` (Oberfläche Live) | I0/I4 |

Szenario-Konventionen für dieses Dokument (Ergänzung zu `15` §3.6.2): Ordner = Modul in Kleinschreibung ohne `Plane.` (`tests/contracts/scenarios/workitems/…`); Szenario-ID `<modul>.<ressource>-<fall>`; Feld `ce` mit den CE-IDs der abgedeckten Zeilen; v1-Szenarien unter `tests/contracts/scenarios/publicapi/` mit Akteur `{apikey:<key>}`. Beispiel §5.7.

### 3.17 Webhook-Ausgang (Vertrag gegenüber Empfängern)

Mechanik, Datenmodell und Zustellung: `06` §3.14 (bindend). Vertragssicht:

| Aspekt | Vertrag | DT |
|---|---|---|
| Methode/URL | `POST` an `webhooks.url` (http/https, SSRF-geprüft, `05` SEC-31) | DT-WH-08 |
| Header | `Content-Type: application/json`, `User-Agent: Autopilot`, `X-Plane-Delivery: <uuid>` (stabil über alle Versuche einer Zustellung), `X-Plane-Event: <event>`, `X-Plane-Signature: <hex>` (nur bei gesetztem Secret) – Header-Namen bleiben (ADR-009B: Protokollbezeichner) | DT-WH-04 |
| Body | `{"event", "action", "webhook_id", "workspace_id", "workspace_slug", "data", "activity": {"field", "new_value", "old_value", "actor", "old_identifier", "new_identifier"}}`; `action` ∈ `created`, `updated`, `deleted` | DT-WH-02, DT-WH-07 |
| Signatur | `HexLower(HMAC-SHA256(UTF8(secret), gesendete Body-Bytes))`; Body kompakt serialisiert | DT-WH-06 (`DEV-WH-003`) |
| Erfolg/Retry | jede HTTP-Antwort (1xx–5xx) = zugestellt; Retry nur bei Transportfehlern, 6 Versuche, Backoff 0…600 s; nach dem 6. Fehlschlag `is_active = false` + Mail an den Ersteller | DT-WH-03 |
| `data` | Stand zum Zustellzeitpunkt in v1-Serializer-Form; gelöschtes Objekt → Zustellung entfällt still (außer `deleted`-Ereignis mit `{"id"}`) | DT-WH-01, DT-WH-02 |
| Protokoll | `webhook_logs` je Versuch, Header/Body als JSON, `request_method` = Aktion (1:1) | DT-WH-05 (`DEV-WH-002`) |
| Verwaltung | Endpunkte `{W}/webhooks/…` (§4.20), Secret-Regenerierung, Logs-Ansicht | – |

#### 3.17.1 Ereignisse → auslösende Endpunkte

Die vollständige Zuordnung steht in §4.27. Nicht auslösende Operationen (Löschen von Work Items/Cycles/Modulen/Kommentaren, Archivieren, Zuordnungen, Intake, Links, Anhänge, Reaktionen, Bulk-Operationen) bleiben wie im Original ohne Webhook (DT-WH-07, Q); Pakete ergänzen Ereignisse über `IWebhookEventSource` (`16` E-08).

### 3.18 Live-Endpunkte

Verbindlich `07` §3.4; Katalogzeilen §4.11/§4.12.

| EP | Methode · Pfad | Vertrag | Original | Ink. |
|---|---|---|---|---|
| EP-0410 | `GET /live/collaboration` (WebSocket) | Hocuspocus-Protokoll 1:1, Session-Cookie-Authentisierung beim Upgrade, Origin-Prüfung, Read-only-Scope (DT-RT-01) | A12 §2.26.2 | I4 |
| EP-0413 | `GET /live/health/` | 200 `{"status": "OK", "timestamp": "<iso>", "version": "<version>"}` (1:1 `health.controller.ts`) | A12 §2.26.2 | I0 |
| EP-0412 | `POST /live/pdf-export/` | PDF-Export (Body wie Original), 200 `application/pdf` (DT-RT-03) | A12 §2.26.2 | I4 |
| EP-0414 | `GET /live/events/` (SignalR, nur WebSockets) | `LiveEventsHub` (🧱 H6-Vorbereitung, `07`/`16`), in der CE ohne fachliche Nachrichten außer Signalen aus `07` §3.10.4 | neu | I0 |
| EP-0411 | `POST /live/convert-document/` | **nicht** über das Gateway erreichbar: nur Management-Port 8081 von `Plane.Realtime` (D07-ADR-19, SEC-39, DT-RT-02) | A12 §2.26.2 | I4 |

Unbekannte `/live/*`-Pfade → 404 `{"message": "Not Found"}`.

### 3.19 Gateway-Kopplungen

| Gateway-Regel (`14`) | betroffene Katalogzeilen | Festlegung für die API |
|---|---|---|
| G-01 Body-Limit | alle | 413-Körper identisch zur API (§3.5); API prüft zusätzlich (`RequestBodyLimitMiddleware`), weil interne Aufrufe das Gateway umgehen |
| G-03 OG-Meta (`OgMetaMiddleware`) | EP-0520 `GET {SP}/meta/` | anonym aufrufbar, Rate-Limit `anon`, Antwortform 1:1 (`A05` S-01); Gateway ruft intern mit `X-Forwarded-For` des Clients |
| G-06/G-07 Live | §3.18 | `convert-document` nicht über Gateway |
| G-08 Backchannel-Logout | EP-0002 `POST /auth/oidc/backchannel-logout/` | von außen 403 (Gateway), intern von Keycloak; API selbst prüft das Logout-Token (`05`) |
| G-09/G-10 Objektspeicher | Asset-Upload-Endpunkte (§4.13) | Presigned-POST-Vertrag 1:1 (`upload_data.url`, `fields`); die URL zeigt bei `ObjectStore:Mode=Proxy` auf `/{bucket}` (G-10), beim Dateisystem-Storage ohne S3 auf die Proxy-Upload-Route EP-0417 `POST {AV2}/upload/{token}/`; Auslieferung dann über EP-0415 `GET {AV2}/files/{token}/` (HMAC-Token, ADR-026) |
| G-12 `/robots.txt` | EP-0731 | Gateway beantwortet extern; die API-Route bleibt für Direktzugriff (Port 8000, Health-Checks) mit identischem Inhalt |
| Integrations-Eingang | EP-0729 | Gateway reicht `/api/integrations/{**}` ohne Cookie-Prüfung durch (Teil von G-08); Body-Limit G-01 |

### 3.20 Branding (ADR-009B) in API-Texten

| ID | Stelle | Original | funk. |
|---|---|---|---|
| BRAND-API-01 | OpenAPI `info` (§3.14.2) | „The Plane REST API“, Kontakt Plane/support@plane.so, Lizenz-URL makeplane | „The funk. REST API“, Kontakt konfigurierbar, Lizenz-URL `github.com/mlwr/funk.` |
| BRAND-API-02 | Fehler- und Erfolgstexte mit Produktnamen (Fundstellen: `documented_bodies` mit „Plane“, z. B. Instanz-Einrichtung, Einladungs-Texte) | „Plane …“ | „funk. …“ (Konstanten mit `// BRAND-API-02`) |
| BRAND-API-03 | E-Mail-Betreffs, die API-Endpunkte auslösen (Einladungen, Webhook-Deaktivierung, Exporte) | „… on Plane“ | „… on funk.“ (Templates `06`) |
| BRAND-API-04 | Seitentitel der Dokumentations-UI (EP-0712/EP-0713) | „The Plane REST API“ (Swagger-/Redoc-Titel aus `SPECTACULAR_SETTINGS.TITLE`) | „The funk. REST API“ (Scalar) |
| BRAND-API-05 | `GET /api/instances/` → `instance.instance_name` Default | „Plane Community Edition“ (`register_instance`-Kommando) | „funk.“ (Instanz-Seed; vom Admin änderbar) |

**Unverändert (interne Bezeichner im Sinne von ADR-009B):** Header `X-Plane-Delivery`, `X-Plane-Event`, `X-Plane-Signature`; Token-Präfixe `plane_api_`, `plane_wh_`; Cookie `session-id`; Fehlercodes und -schlüssel; JSON-Feldnamen; `User-Agent: Autopilot`; Konfigurationsschlüssel `Plane:*`. Prüfung: `BrandingTests.ApiTexts` durchsucht `openapi/v1.json` und alle `*ErrorTexts.cs` nach `\bPlane\b` (Ausnahmen: Liste der Protokollbezeichner). Die Frage, ob auch die `X-Plane-*`-Header umbenannt werden sollen, ist offen (O-D04-02); die Empfehlung ist „nein“ (Bestandsintegrationen prüfen diese Header).

---

## 4. Vollständige Mapping-Tabellen Original → Ziel

**Spalten:** „EP“ = Katalog-ID; „Original-ID“ = `<Dok>:<ID>` (für `.WithOriginalContract`); „Methode · Pfad (Original)“ mit Kürzeln aus dem Kopf; „Original-View (Datei)“ = Klasse.Aktion mit Datei:Zeile im Referenzstand; „Ziel: Klasse → Handler“ = `<Ressource>Endpoints` (Datei unter dem Ablagepfad des Abschnitts) und Mediator-Request (`…Query`/`…Command`), bei Modulgrenze mit vorangestelltem Ziel-Modul; „Permission · Ziel-Prüfung“ = Permission-Key aus `05` Anhang B und Kurzform der Ziel-Prüfung (`WS(A,M)` = Workspace-Rolle Admin/Member, `PRJ(A,M,G)` = Projektrolle, `AUTH` = angemeldet, `SELF` = eigener Datensatz, `INST` = Instanz-Admin, `BOARD` = veröffentlichtes Board); „Status Orig→Ziel“ = Erfolgsstatus (bei nicht registrierten Zeilen der Ziel-Status 404/405); „Abw./DT“ = Abweichungs-IDs aus `05` (`SEC-`, `HARM-`, `DEV-`) und DT-Zeilen (§3.13); „Ink.“ = Inkrement; „CE-IDs“ = getragene Features. Nicht registrierte Zeilen zeigen in „Ziel“ den Grund. Methoden-Nebenprodukte (Matrix-Zeilen ohne Analyse-Gegenstück) stehen gesammelt in §4.25.

### 4.1 `Plane.Identity` – Auth-Oberfläche `/auth/`, Benutzer, Session, Profil, API-Tokens

Ablage der Endpoint-Klassen: `src/modules/Identity/Plane.Identity/Endpoints/{App,Auth}/<Klasse>.cs`. 65 Zeilen, davon 26 registriert und 39 nicht registriert (Entscheidung in Spalte „Abw./DT“).

| EP | Original-ID | Methode · Pfad (Original) | Original-View (Datei) | Ziel: Klasse → Handler | Permission · Ziel-Prüfung | Status Orig→Ziel | Abw./DT | Ink. | CE-IDs |
|---|---|---|---|---|---|---|---|---|---|
| EP-0001 | A06:#7 | `GET /auth/get-csrf-token/` | `CSRFTokenEndpoint` (authentication/views/common.py) | `AntiforgeryEndpoints` → `GetCsrfToken` | (anonym) | 200 | DT-AUTH-05 | I0 | CE-AUTH-016, CE-AUTH-024 |
| EP-0002 | neu: N-07 | `POST /auth/oidc/backchannel-logout/` | – (N-07) | `BackChannelLogoutEndpoint` → `Handle` | (Logout-Token) | 200 | – | I0 | CE-AUTH-022, CE-AUTH-023, CE-AUTH-027 |
| EP-0003 | A06:#32 | `POST /auth/change-password/` | `ChangePasswordEndpoint` (authentication/views/common.py) | — (entfällt (ADR-008) → 404) | – | 200→404 | DT-AUTH-01 | I0 | CE-AUTH-020 |
| EP-0004 | A06:#26 | `POST /auth/email-check/` | `EmailCheckEndpoint` (authentication/views/app/check.py) | — (entfällt (ADR-008) → 404) | – | 200→404 | DT-AUTH-01 | I0 | CE-AUTH-003 |
| EP-0005 | A06:#28 | `POST /auth/forgot-password/` | `ForgotPasswordEndpoint` (authentication/views/app/password_management.py) | — (entfällt (ADR-008) → 404) | – | 200→404 | DT-AUTH-01 | I0 | CE-AUTH-017 |
| EP-0006 | A06:#34 | `GET /auth/gitea/` | `GiteaOauthInitiateEndpoint` (authentication/views/app/gitea.py) | — (entfällt (ADR-008) → 404) | – | 302→404 | DT-AUTH-01 | I0 | CE-AUTH-011 |
| EP-0007 | A06:#35 | `GET /auth/gitea/callback/` | `GiteaCallbackEndpoint` (authentication/views/app/gitea.py) | — (entfällt (ADR-008) → 404) | – | 302→404 | DT-AUTH-01 | I0 | CE-AUTH-011 |
| EP-0008 | A06:#18 | `GET /auth/github/` | `GitHubOauthInitiateEndpoint` (authentication/views/app/github.py) | — (entfällt (ADR-008) → 404) | – | 302→404 | DT-AUTH-01 | I0 | CE-AUTH-009 |
| EP-0009 | A06:#19 | `GET /auth/github/callback/` | `GitHubCallbackEndpoint` (authentication/views/app/github.py) | — (entfällt (ADR-008) → 404) | – | 302→404 | DT-AUTH-01 | I0 | CE-AUTH-009 |
| EP-0010 | A06:#22 | `GET /auth/gitlab/` | `GitLabOauthInitiateEndpoint` (authentication/views/app/gitlab.py) | — (entfällt (ADR-008) → 404) | – | 302→404 | DT-AUTH-01 | I0 | CE-AUTH-010 |
| EP-0011 | A06:#23 | `GET /auth/gitlab/callback/` | `GitLabCallbackEndpoint` (authentication/views/app/gitlab.py) | — (entfällt (ADR-008) → 404) | – | 302→404 | DT-AUTH-01 | I0 | CE-AUTH-010 |
| EP-0012 | A06:#14 | `GET /auth/google/` | `GoogleOauthInitiateEndpoint` (authentication/views/app/google.py) | — (entfällt (ADR-008) → 404) | – | 302→404 | DT-AUTH-01 | I0 | CE-AUTH-008 |
| EP-0013 | A06:#15 | `GET /auth/google/callback/` | `GoogleCallbackEndpoint` (authentication/views/app/google.py) | — (entfällt (ADR-008) → 404) | – | 302→404 | DT-AUTH-01 | I0 | CE-AUTH-008 |
| EP-0014 | A06:#8 | `POST /auth/magic-generate/` | `MagicGenerateEndpoint` (authentication/views/app/magic.py) | — (entfällt (ADR-008) → 404) | – | 200→404 | DT-AUTH-01 | I0 | CE-AUTH-006 |
| EP-0015 | A06:#9 | `POST /auth/magic-sign-in/` | `MagicSignInEndpoint` (authentication/views/app/magic.py) | — (entfällt (ADR-008) → 404) | – | 302→404 | DT-AUTH-01 | I0 | CE-AUTH-007 |
| EP-0016 | A06:#10 | `POST /auth/magic-sign-up/` | `MagicSignUpEndpoint` (authentication/views/app/magic.py) | — (entfällt (ADR-008) → 404) | – | 302→404 | DT-AUTH-01 | I0 | CE-AUTH-007 |
| EP-0017 | neu: N-02 | `GET /auth/oidc/callback/` | – (N-02) | `OidcBffEndpoints` → `Callback (OIDC-Handler)` | (anonym) | 302 | – | I0 | CE-AUTH-012, CE-AUTH-014, CE-AUTH-024, CE-AUTH-027, CE-AUTH-028, CE-AUTH-029 |
| EP-0018 | neu: N-01 | `GET /auth/oidc/login/` | – (N-01) | `OidcBffEndpoints` → `Login` | (anonym) | 302 | – | I0 | CE-AUTH-001, CE-AUTH-029, CE-SPACE-014 |
| EP-0019 | neu: N-06 | `GET /auth/oidc/signed-out/` | – (N-06) | `OidcBffEndpoints` → `SignedOut` | (anonym) | 302 | – | I0 | CE-AUTH-022 |
| EP-0020 | A06:#29 | `POST /auth/reset-password/{uidb64}/{token}/` | `ResetPasswordEndpoint` (authentication/views/app/password_management.py) | — (entfällt (ADR-008) → 404) | – | 302→404 | DT-AUTH-01 | I0 | CE-AUTH-018 |
| EP-0021 | A06:#33 | `POST /auth/set-password/` | `SetUserPasswordEndpoint` (authentication/views/common.py) | — (entfällt (ADR-008) → 404) | – | 200→404 | DT-AUTH-01 | I0 | CE-AUTH-019 |
| EP-0022 | A06:#1 | `POST /auth/sign-in/` | `SignInAuthEndpoint` (authentication/views/app/email.py) | — (entfällt (ADR-008) → 404) | – | 302→404 | DT-AUTH-01 | I0 | CE-AUTH-004 |
| EP-0023 | A06:#5 | `POST /auth/sign-out/` | `SignOutAuthEndpoint` (authentication/views/app/signout.py) | `OidcBffEndpoints` → `SignOut(app=web)` | (anonym) | 302 | DT-AUTH-02 | I0 | CE-AUTH-022 |
| EP-0024 | A06:#2 | `POST /auth/sign-up/` | `SignUpAuthEndpoint` (authentication/views/app/email.py) | — (entfällt (ADR-008) → 404) | – | 302→404 | DT-AUTH-01 | I0 | CE-AUTH-005 |
| EP-0025 | A06:#27 | `POST /auth/spaces/email-check/` | `EmailCheckSpaceEndpoint` (authentication/views/space/check.py) | — (entfällt (ADR-008) → 404) | – | 200→404 | DT-AUTH-01 | I0 | CE-AUTH-003 |
| EP-0026 | A06:#30 | `POST /auth/spaces/forgot-password/` | `ForgotPasswordSpaceEndpoint` (authentication/views/space/password_management.py) | — (entfällt (ADR-008) → 404) | – | 200→404 | DT-AUTH-01 | I0 | CE-AUTH-017 |
| EP-0027 | A06:#36 | `GET /auth/spaces/gitea/` | `GiteaOauthInitiateSpaceEndpoint` (authentication/views/space/gitea.py) | — (entfällt (ADR-008) → 404) | – | 302→404 | DT-AUTH-01 | I0 | CE-AUTH-011 |
| EP-0028 | A06:#37 | `GET /auth/spaces/gitea/callback/` | `GiteaCallbackSpaceEndpoint` (authentication/views/space/gitea.py) | — (entfällt (ADR-008) → 404) | – | 302→404 | DT-AUTH-01 | I0 | CE-AUTH-011 |
| EP-0029 | A06:#20 | `GET /auth/spaces/github/` | `GitHubOauthInitiateSpaceEndpoint` (authentication/views/space/github.py) | — (entfällt (ADR-008) → 404) | – | 302→404 | DT-AUTH-01 | I0 | CE-AUTH-009 |
| EP-0030 | A06:#21 | `GET /auth/spaces/github/callback/` | `GitHubCallbackSpaceEndpoint` (authentication/views/space/github.py) | — (entfällt (ADR-008) → 404) | – | 302→404 | DT-AUTH-01 | I0 | CE-AUTH-009 |
| EP-0031 | A06:#24 | `GET /auth/spaces/gitlab/` | `GitLabOauthInitiateSpaceEndpoint` (authentication/views/space/gitlab.py) | — (entfällt (ADR-008) → 404) | – | 302→404 | DT-AUTH-01 | I0 | CE-AUTH-010 |
| EP-0032 | A06:#25 | `GET /auth/spaces/gitlab/callback/` | `GitLabCallbackSpaceEndpoint` (authentication/views/space/gitlab.py) | — (entfällt (ADR-008) → 404) | – | 302→404 | DT-AUTH-01 | I0 | CE-AUTH-010 |
| EP-0033 | A06:#16 | `GET /auth/spaces/google/` | `GoogleOauthInitiateSpaceEndpoint` (authentication/views/space/google.py) | — (entfällt (ADR-008) → 404) | – | 302→404 | DT-AUTH-01 | I0 | CE-AUTH-008 |
| EP-0034 | A06:#17 | `GET /auth/spaces/google/callback/` | `GoogleCallbackSpaceEndpoint` (authentication/views/space/google.py) | — (entfällt (ADR-008) → 404) | – | 302→404 | DT-AUTH-01 | I0 | CE-AUTH-008 |
| EP-0035 | A06:#11 | `POST /auth/spaces/magic-generate/` | `MagicGenerateSpaceEndpoint` (authentication/views/space/magic.py) | — (entfällt (ADR-008) → 404) | – | 200→404 | DT-AUTH-01 | I0 | CE-AUTH-006 |
| EP-0036 | A06:#12 | `POST /auth/spaces/magic-sign-in/` | `MagicSignInSpaceEndpoint` (authentication/views/space/magic.py) | — (entfällt (ADR-008) → 404) | – | 302→404 | DT-AUTH-01 | I0 | CE-AUTH-007 |
| EP-0037 | A06:#13 | `POST /auth/spaces/magic-sign-up/` | `MagicSignUpSpaceEndpoint` (authentication/views/space/magic.py) | — (entfällt (ADR-008) → 404) | – | 302→404 | DT-AUTH-01 | I0 | CE-AUTH-007 |
| EP-0038 | A06:#31 | `POST /auth/spaces/reset-password/{uidb64}/{token}/` | `ResetPasswordSpaceEndpoint` (authentication/views/space/password_management.py) | — (entfällt (ADR-008) → 404) | – | 302→404 | DT-AUTH-01 | I0 | CE-AUTH-018 |
| EP-0039 | A06:#3 | `POST /auth/spaces/sign-in/` | `SignInAuthSpaceEndpoint` (authentication/views/space/email.py) | — (entfällt (ADR-008) → 404) | – | 302→404 | DT-AUTH-01 | I0 | CE-AUTH-004 |
| EP-0040 | A06:#6 | `POST /auth/spaces/sign-out/` | `SignOutAuthSpaceEndpoint` (authentication/views/space/signout.py) | `OidcBffEndpoints` → `SignOut(app=space)` | (anonym) | 302 | DT-AUTH-02 | I0 | CE-AUTH-022 |
| EP-0041 | A06:#4 | `POST /auth/spaces/sign-up/` | `SignUpAuthSpaceEndpoint` (authentication/views/space/email.py) | — (entfällt (ADR-008) → 404) | – | 302→404 | DT-AUTH-01 | I0 | CE-AUTH-005 |
| EP-0042 | A03:AT-02 | `GET /api/users/api-tokens/` | `ApiTokenEndpoint.get` (V/api.py:41) | `ApiTokenEndpoints` → `ListApiTokensQuery` | `user.api_token.read` · `AUTH+SELF` | 200 | – | I6 | CE-WH-012 |
| EP-0043 | A03:AT-01 | `POST /api/users/api-tokens/` | `ApiTokenEndpoint.post` (V/api.py:21) | `ApiTokenEndpoints` → `CreateApiTokenCommand` | `user.api_token.create` · `AUTH+SELF` | 201 | DT-AUTH-10 | I6 | CE-WH-013 |
| EP-0044 | A03:AT-03 | `GET /api/users/api-tokens/{pk}/` | `ApiTokenEndpoint.get` (V/api.py:41) | `ApiTokenEndpoints` → `GetApiTokenQuery` | `user.api_token.read` · `AUTH+SELF` | 200 | – | I6 | CE-WH-012 |
| EP-0045 | A03:AT-04 | `PATCH /api/users/api-tokens/{pk}/` | `ApiTokenEndpoint.patch` (V/api.py:56) | `ApiTokenEndpoints` → `UpdateApiTokenCommand` | `user.api_token.update` · `AUTH+SELF` | 200 | DT-AUTH-10 | I6 | CE-WH-012 |
| EP-0046 | A03:AT-05 | `DELETE /api/users/api-tokens/{pk}/` | `ApiTokenEndpoint.delete` (V/api.py:51) | `ApiTokenEndpoints` → `DeleteApiTokenCommand` | `user.api_token.delete` · `AUTH+SELF` | 204 | – | I6 | CE-WH-014 |
| EP-0047 | A03:W-23 | `GET /api/users/last-visited-workspace/` | `UserLastProjectWithWorkspaceEndpoint.get` (V/workspace/user.py:86) | `CurrentUserEndpoints` → `GetLastVisitedWorkspaceQuery` | `user.user.read` · `AUTH+SELF` | 500→200 | DT-WS-02 | I0 | CE-AUTH-029 |
| EP-0048 | A03:U-01 | `GET /api/users/me/` | `UserEndpoint.retrieve` (V/user/base.py:84) | `CurrentUserEndpoints` → `GetCurrentUserQuery` | `user.user.read` · `AUTH+SELF` | 200 | – | I0 | CE-PROF-001, CE-AUTH-025 |
| EP-0049 | A03:U-02 | `PATCH /api/users/me/` | `UserEndpoint.partial_update` (V/user/base.py:99) | `CurrentUserEndpoints` → `UpdateCurrentUserCommand` | `user.user.update` · `AUTH+SELF` | 200 | DT-AUTH-09 | I0 | CE-PROF-003 |
| EP-0050 | A03:U-03 | `DELETE /api/users/me/` | `UserEndpoint.deactivate` (V/user/base.py:278) | `CurrentUserEndpoints` → `DeactivateCurrentUserCommand` | `user.user.deactivate` · `AUTH+SELF` | 204 | DT-AUTH-08 | I1 | CE-PROF-005 |
| EP-0051 | A03:U-13 | `GET /api/users/me/instance-admin/` | `UserEndpoint.retrieve_instance_admin` (V/user/base.py:94) | `CurrentUserEndpoints` → `GetInstanceAdminFlagQuery` | `user.user.read` · `AUTH+SELF` | 200 | DT-AUTH-07 | I0 | CE-INST-005 |
| EP-0052 | A03:U-14 | `PATCH /api/users/me/onboard/` | `UpdateUserOnBoardedEndpoint.patch` (V/user/base.py:392) | `CurrentUserEndpoints` → `UpdateOnboardingStatusCommand` | `user.user.update` · `AUTH+SELF` | 200 | – | I0 | CE-AUTH-030 |
| EP-0053 | A03:U-05 | `GET /api/users/me/settings/` | `UserEndpoint.retrieve_user_settings` (V/user/base.py:90) | `CurrentUserEndpoints` → `GetCurrentUserSettingsQuery` | `user.user.read` · `AUTH+SELF` | 200 | – | I0 | CE-PROF-001, CE-AUTH-029 |
| EP-0054 | A03:U-15 | `PATCH /api/users/me/tour-completed/` | `UpdateUserTourCompletedEndpoint.patch` (V/user/base.py:400) | `CurrentUserEndpoints` → `CompleteProductTourCommand` | `user.user.update` · `AUTH+SELF` | 200 | – | I1 | CE-HOME-006 |
| EP-0055 | A03:U-17 | `GET /api/users/me/workspaces/` | `UserWorkSpacesEndpoint.get` (V/workspace/base.py:181) | `CurrentUserEndpoints` → `ListMyWorkspacesQuery` | `user.user.read` · `AUTH+SELF` | 200 | – | I0 | CE-WS-005 |
| EP-0056 | A03:U-04 | `GET /api/users/session/` | `UserSessionEndpoint.get` (V/user/base.py:380) | `SessionEndpoints` → `GetSessionStatusQuery` | `user.session.read` · `ANON` | 200 | – | I0 | CE-AUTH-025 |
| EP-0057 | A03:T-01 | `GET /api/timezones/` | `TimezoneEndpoint.get` (V/timezone/base.py:24) | `TimezoneEndpoints` → `ListTimezonesQuery` | `user.timezone.read` · `ANON` | 200 | DT-AUTH-11 | I1 | CE-PROF-006 |
| EP-0058 | A03:U-16 | `GET /api/users/me/activities/` | `UserActivityEndpoint.get` (V/user/base.py:408) | `UserActivityEndpoints` → `ListCurrentUserActivitiesQuery` | `user.user_activity.read` · `AUTH+SELF` | 200 | – | I5 | CE-PROF-010 |
| EP-0059 | A03:U-08 | `GET /api/users/me/profile/` | `ProfileEndpoint.get` (V/user/base.py:445) | `UserProfileEndpoints` → `GetCurrentUserProfileQuery` | `user.user_profile.read` · `AUTH+SELF` | 200 | – | I1 | CE-PROF-001 |
| EP-0060 | A03:U-09 | `PATCH /api/users/me/profile/` | `ProfileEndpoint.patch` (V/user/base.py:450) | `UserProfileEndpoints` → `UpdateCurrentUserProfileCommand` | `user.user_profile.update` · `AUTH+SELF` | 200 | – | I1 | CE-PROF-006 |
| EP-0064 | A03:U-10 | `GET /api/users/me/accounts/` | `AccountEndpoint.get` (V/user/base.py:426) | — (entfällt (ADR-008)) | – | 200→404 | DT-AUTH-01 | I1 | CE-PROF-007 |
| EP-0066 | A03:U-11 | `GET /api/users/me/accounts/{pk}/` | `AccountEndpoint.get` (V/user/base.py:426) | — (entfällt (ADR-008)) | – | 200→404 | DT-AUTH-01 | I1 | CE-PROF-007 |
| EP-0067 | A03:U-12 | `DELETE /api/users/me/accounts/{pk}/` | `AccountEndpoint.delete` (V/user/base.py:436) | — (entfällt (ADR-008)) | – | 204→404 | DT-AUTH-01 | I1 | CE-PROF-007 |
| EP-0068 | A03:U-07 | `PATCH /api/users/me/email/` | `UserEndpoint.update_email` (V/user/base.py:191) | — (entfällt (ADR-008)) | – | 200→404 | DT-AUTH-01 | I1 | CE-PROF-004 |
| EP-0069 | A03:U-06 | `POST /api/users/me/email/generate-code/` | `UserEndpoint.generate_email_verification_code` (V/user/base.py:144) | — (entfällt (ADR-008)) | – | 200→404 | DT-AUTH-01 | I1 | CE-PROF-004 |

### 4.2 `Plane.Instance` – Instanz-/God-Mode-API `/api/instances/`

Ablage der Endpoint-Klassen: `src/modules/Instance/Plane.Instance/Endpoints/Instance/<Klasse>.cs`. 19 Zeilen, davon 14 registriert und 5 nicht registriert (Entscheidung in Spalte „Abw./DT“).

| EP | Original-ID | Methode · Pfad (Original) | Original-View (Datei) | Ziel: Klasse → Handler | Permission · Ziel-Prüfung | Status Orig→Ziel | Abw./DT | Ink. | CE-IDs |
|---|---|---|---|---|---|---|---|---|---|
| EP-0070 | A05:I-03 | `GET {I}/admins/` | `InstanceAdminEndpoint.get` (license/V1V/admin.py:73) | `InstanceAdminEndpoints` → `ListInstanceAdminsQuery` | `instance.admin.read` · `INST` | 200 | DT-INST-04 | I0 | CE-INST-004 |
| EP-0071 | A05:I-06 | `GET {I}/admins/me/` | `InstanceAdminUserMeEndpoint.get` (license/V1V/admin.py:412) | `InstanceAdminEndpoints` → `GetCurrentInstanceAdminQuery` | `instance.admin.read` · `INST` | 200 | – | I0 | CE-INST-010 |
| EP-0072 | A05:I-07 | `GET {I}/admins/session/` | `InstanceAdminUserSessionEndpoint.get` (license/V1V/admin.py:420) | `InstanceAdminEndpoints` → `GetInstanceAdminSessionQuery` | `instance.session.read` · `ANON` | 200 | – | I0 | CE-INST-010 |
| EP-0073 | A05:I-12 | `GET {I}/configurations/` | `InstanceConfigurationEndpoint.get` (license/V1V/configuration.py:36) | `InstanceConfigurationEndpoints` → `ListInstanceConfigurationsQuery` | `instance.configuration.read` · `INST` | 200 | DT-INST-07 | I6 | CE-INST-002, CE-INST-017, CE-INST-018, CE-INST-025, CE-INST-026 |
| EP-0074 | A05:I-13 | `PATCH {I}/configurations/` | `InstanceConfigurationEndpoint.patch` (license/V1V/configuration.py:43) | `InstanceConfigurationEndpoints` → `UpdateInstanceConfigurationsCommand` | `instance.configuration.update` · `INST` | 200 | DT-INST-07, DT-INST-08 | I6 | CE-INST-002, CE-INST-017, CE-INST-018, CE-INST-025, CE-INST-026, CE-INST-028 |
| EP-0075 | A05:I-14 | `DELETE {I}/configurations/disable-email-feature/` | `DisableEmailFeatureEndpoint.delete` (license/V1V/configuration.py:66) | `InstanceConfigurationEndpoints` → `DisableEmailFeatureCommand` | `instance.configuration.delete` · `INST` | 200 | – | I6 | CE-INST-018 |
| EP-0076 | A05:I-15 | `POST {I}/email-credentials-check/` | `EmailCredentialCheckEndpoint.post` (license/V1V/configuration.py:89) | `InstanceConfigurationEndpoints` → `SendTestEmailCommand` | `instance.configuration.create` · `INST` | 200 | – | I6 | CE-INST-019 |
| EP-0077 | A05:I-01 | `GET {I}/` | `InstanceEndpoint.get` (license/V1V/instance.py:36) | `InstanceEndpoints` → `GetInstanceInfoQuery` | `instance.settings.read` · `ANON` | 200 | DT-AUTH-03, DT-INST-01, DT-INST-02 | I0 | CE-INST-003, CE-INST-001, CE-AUTH-013, CE-INST-028 |
| EP-0078 | A05:I-02 | `PATCH {I}/` | `InstanceEndpoint.patch` (license/V1V/instance.py:162) | `InstanceEndpoints` → `UpdateInstanceCommand` | `instance.settings.update` · `INST` | 200 | – | I6 | CE-INST-017 |
| EP-0079 | neu: N-13 | `POST {I}/admins/setup/` | – (N-13) | `InstanceEndpoints` → `CompleteInstanceSetupCommand` | instance.settings.update | 200 | – | I0 | CE-INST-006 |
| EP-0080 | A05:I-16 | `GET {I}/workspace-slug-check/` | `InstanceWorkSpaceAvailabilityCheckEndpoint.get` (license/V1V/workspace.py:22) | `InstanceWorkspaceEndpoints` → `CheckWorkspaceSlugQuery` | `instance.workspace.read` · `INST` | 200 | DT-WS-09 | I6 | CE-INST-029 |
| EP-0081 | A05:I-17 | `GET {I}/workspaces/` | `InstanceWorkSpaceEndpoint.get` (license/V1V/workspace.py:40) | `InstanceWorkspaceEndpoints` → `ListInstanceWorkspacesQuery` | `instance.workspace.read` · `INST` | 200 | – | I6 | CE-INST-027 |
| EP-0082 | A05:I-18 | `POST {I}/workspaces/` | `InstanceWorkSpaceEndpoint.post` (license/V1V/workspace.py:71) | `InstanceWorkspaceEndpoints` → `CreateWorkspaceCommand` | `instance.workspace.create` · `INST` | 201 | DT-INST-05, DT-WS-09 | I6 | CE-INST-029 |
| EP-0083 | A05:I-10 | `POST {I}/admins/sign-out/` | `InstanceAdminSignOutEndpoint.post` (license/V1V/admin.py:433) | `Plane.Identity` · `OidcBffEndpoints` → `OidcBffEndpoints.SignOut(app=admin)` | `—` · `**entfällt**` | 302 | DT-AUTH-02 | I0 | CE-INST-008 |
| EP-0084 | A05:I-04 | `POST {I}/admins/` | `InstanceAdminEndpoint.post` (license/V1V/admin.py:51) | — (entfällt (ADR-008)) | – | 201→405 | DT-AUTH-01, DT-INST-04 | I0 | CE-INST-004 |
| EP-0086 | A05:I-08 | `POST {I}/admins/sign-in/` | `InstanceAdminSignInEndpoint.post` (license/V1V/admin.py:275) | — (entfällt (ADR-008)) | – | 302→404 | DT-AUTH-01 | I0 | CE-INST-007 |
| EP-0087 | A05:I-11 | `POST {I}/admins/sign-up-screen-visited/` | `SignUpScreenVisitedEndpoint.post` (license/V1V/instance.py:176) | — (entfällt (ADR-008)) | – | 204→404 | DT-AUTH-01, DT-INST-03 | I0 | CE-INST-006 |
| EP-0088 | A05:I-09 | `POST {I}/admins/sign-up/` | `InstanceAdminSignUpEndpoint.post` (license/V1V/admin.py:96) | — (ersetzt durch N-13) | – | 302→404 | DT-INST-03 | I0 | CE-INST-006 |
| EP-0091 | A05:I-05 | `DELETE {I}/admins/{pk}/` | `InstanceAdminEndpoint.delete` (license/V1V/admin.py:85) | — (entfällt (ADR-008)) | – | 204→404 | DT-AUTH-01, DT-INST-04 | I0 | CE-INST-004 |

### 4.3 `Plane.Workspaces` – Workspaces, Mitglieder, Einladungen, Favoriten, Präferenzen, Mitglieder-Profile

Ablage der Endpoint-Klassen: `src/modules/Workspaces/Plane.Workspaces/Endpoints/App/<Klasse>.cs`. 70 Zeilen, davon 64 registriert und 6 nicht registriert (Entscheidung in Spalte „Abw./DT“).

| EP | Original-ID | Methode · Pfad (Original) | Original-View (Datei) | Ziel: Klasse → Handler | Permission · Ziel-Prüfung | Status Orig→Ziel | Abw./DT | Ink. | CE-IDs |
|---|---|---|---|---|---|---|---|---|---|
| EP-0092 | A04:Y13 | `POST {P}/user-favorite-cycles/` | `CycleFavoriteViewSet.create` (V/cycle/base.py:573) | `CycleFavoriteEndpoints` → `FavoriteCycleCommand` | `project.cycle.favorite` · `PRJ(A,M)` | 204 | – | I3 | CE-CYC-015 |
| EP-0093 | A04:Y14 | `DELETE {P}/user-favorite-cycles/{cycle_id}/` | `CycleFavoriteViewSet.destroy` (V/cycle/base.py:587) | `CycleFavoriteEndpoints` → `UnfavoriteCycleCommand` | `project.cycle.favorite` · `PRJ(A,M)` | 204 | – | I3 | CE-CYC-015 |
| EP-0094 | A03:W-43 | `GET {W}/user-favorites/` | `WorkspaceFavoriteEndpoint.get` (V/workspace/favorite.py:25) | `FavoriteEndpoints` → `ListFavoritesQuery` | `workspace.favorite.read` · `WS(A,M)+VIS` | 200 | – | I1 | CE-WS-023 |
| EP-0095 | A03:W-44 | `POST {W}/user-favorites/` | `WorkspaceFavoriteEndpoint.post` (V/workspace/favorite.py:39) | `FavoriteEndpoints` → `CreateFavoriteCommand` | `workspace.favorite.create` · `WS(A,M)` | 200 | – | I1 | CE-WS-023 |
| EP-0096 | A03:W-45 | `PATCH {W}/user-favorites/{favorite_id}/` | `WorkspaceFavoriteEndpoint.patch` (V/workspace/favorite.py:79) | `FavoriteEndpoints` → `UpdateFavoriteCommand` | `workspace.favorite.update` · `WS(A,M)` | 200 | – | I1 | CE-WS-023 |
| EP-0097 | A03:W-46 | `DELETE {W}/user-favorites/{favorite_id}/` | `WorkspaceFavoriteEndpoint.delete` (V/workspace/favorite.py:90) | `FavoriteEndpoints` → `DeleteFavoriteCommand` | `workspace.favorite.delete` · `WS(A,M)` | 204 | – | I1 | CE-WS-023 |
| EP-0098 | A03:W-47 | `GET {W}/user-favorites/{favorite_id}/group/` | `WorkspaceFavoriteGroupEndpoint.get` (V/workspace/favorite.py:98) | `FavoriteEndpoints` → `ListFavoriteGroupQuery` | `workspace.favorite.read` · `WS(A,M)+VIS` | 200 | – | I1 | CE-WS-023 |
| EP-0099 | A03:W-16 | `GET {W}/invitations/{pk}/join/` | `WorkspaceJoinEndpoint.get` (V/workspace/invite.py:250) | `InvitationJoinEndpoints` → `GetPublicWorkspaceInvitationQuery` | `public.invitation.read` · `ANON` | 200 | – | I1 | CE-WS-011 |
| EP-0100 | A03:W-15 | `POST {W}/invitations/{pk}/join/` | `WorkspaceJoinEndpoint.post` (V/workspace/invite.py:172) | `InvitationJoinEndpoints` → `RespondToWorkspaceInvitationCommand` | `public.invitation.respond` · `ANON` | 200 | DT-WS-03 | I1 | CE-WS-011 |
| EP-0101 | A03:P-18 | `GET {P}/join/{pk}/` | `ProjectJoinEndpoint.get` (V/project/invite.py:292) | `InvitationJoinEndpoints` → `GetPublicProjectInvitationQuery` | `public.invitation.read` · `ANON` | 200 | – | I1 | CE-PRJ-010 |
| EP-0102 | A03:P-17 | `POST {P}/join/{pk}/` | `ProjectJoinEndpoint.post` (V/project/invite.py:195) | `InvitationJoinEndpoints` → `RespondToProjectInvitationCommand` | `public.invitation.respond` · `ANON` | 200 | – | I1 | CE-PRJ-010 |
| EP-0103 | A03:U-18 | `GET /api/users/me/workspaces/{slug}/activity-graph/` | `UserActivityGraphEndpoint.get` (V/workspace/user.py:566) | `MemberProfileEndpoints` → `GetActivityGraphQuery` | `workspace.member_profile.read_own` · `WS(A,M,G)+SELF+VIS` | 200 | – | I5 | CE-HOME-007 |
| EP-0104 | A03:U-20 | `GET /api/users/me/workspaces/{slug}/dashboard/` | `UserWorkspaceDashboardEndpoint.get` (V/workspace/base.py:235) | `MemberProfileEndpoints` → `GetLegacyDashboardQuery` | `workspace.member_profile.read_own` · `WS(A,M,G)+SELF+VIS` | 200 | – | I5 | CE-HOME-007 |
| EP-0105 | A03:U-19 | `GET /api/users/me/workspaces/{slug}/issues-completed-graph/` | `UserIssueCompletedGraphEndpoint.get` (V/workspace/user.py:583) | `MemberProfileEndpoints` → `GetCompletedWorkItemsGraphQuery` | `workspace.member_profile.read_own` · `WS(A,M,G)+SELF+VIS` | 200 | – | I5 | CE-HOME-007 |
| EP-0106 | A03:W-32 | `GET {W}/user-activity/{user_id}/` | `WorkspaceUserActivityEndpoint.get` (V/workspace/user.py:412) | `MemberProfileEndpoints` → `ListMemberActivityQuery` | `workspace.member_profile.read` · `WS(A,M,G)+VIS` | 200 | – | I5 | CE-PROF-010 |
| EP-0107 | A03:W-33 | `POST {W}/user-activity/{user_id}/export/` | `ExportWorkspaceUserActivityEndpoint.post` (V/workspace/base.py:351) | `MemberProfileEndpoints` → `ExportMemberActivityCommand` | `workspace.member_profile.export` · `WS(A,M)` | 200 | – | I5 | CE-PROF-010 |
| EP-0108 | A03:W-35 | `GET {W}/user-issues/{user_id}/` | `WorkspaceUserProfileIssuesEndpoint.get` (V/workspace/user.py:152) | `MemberProfileEndpoints` → `ListMemberWorkItemsQuery` | `workspace.member_profile.read` · `WS(A,M,G)+VIS` | 200 | – | I5 | CE-PROF-009 |
| EP-0109 | A03:W-34 | `GET {W}/user-profile/{user_id}/` | `WorkspaceUserProfileEndpoint.get` (V/workspace/user.py:300) | `MemberProfileEndpoints` → `GetMemberProfileQuery` | `workspace.member_profile.read` · `WS(A,M,G)+VIS` | 200 | – | I5 | CE-PROF-008 |
| EP-0110 | A03:W-31 | `GET {W}/user-stats/{user_id}/` | `WorkspaceUserProfileStatsEndpoint.get` (V/workspace/user.py:441) | `MemberProfileEndpoints` → `GetMemberStatsQuery` | `workspace.member_profile.read` · `WS(A,M,G)+VIS` | 200 | – | I5 | CE-PROF-008 |
| EP-0111 | A04:M16 | `POST {P}/user-favorite-modules/` | `ModuleFavoriteViewSet.create` (V/module/base.py:811) | `ModuleFavoriteEndpoints` → `FavoriteModuleCommand` | `project.module.favorite` · `PRJ(A,M,G)` | 204 | – | I3 | CE-MOD-011 |
| EP-0112 | A04:M17 | `DELETE {P}/user-favorite-modules/{module_id}/` | `ModuleFavoriteViewSet.destroy` (V/module/base.py:824) | `ModuleFavoriteEndpoints` → `UnfavoriteModuleCommand` | `project.module.favorite` · `PRJ(A,M,G)` | 204 | – | I3 | CE-MOD-011 |
| EP-0113 | A03:W-13 | `GET /api/users/me/workspaces/invitations/` | `UserWorkspaceInvitationsViewSet.list` (V/workspace/invite.py) | `MyInvitationEndpoints` → `ListMyWorkspaceInvitationsQuery` | `user.invitation.read` · `AUTH+SELF` | 200 | – | I1 | CE-WS-011 |
| EP-0114 | A03:W-14 | `POST /api/users/me/workspaces/invitations/` | `UserWorkspaceInvitationsViewSet.create` (V/workspace/invite.py:270) | `MyInvitationEndpoints` → `AcceptMyWorkspaceInvitationsCommand` | `user.invitation.accept` · `AUTH+SELF` | 204 | – | I1 | CE-WS-011 |
| EP-0115 | A03:P-14 | `GET /api/users/me/workspaces/{slug}/projects/invitations/` | `UserProjectInvitationsViewset.list` (V/project/invite.py) | `MyInvitationEndpoints` → `ListMyProjectInvitationsQuery` | `user.invitation.read` · `AUTH+SELF` | 200 | SEC-06, DT-PRJ-02 | I1 | CE-PRJ-010 |
| EP-0116 | A04:G7 | `POST {P}/favorite-pages/{page_id}/` | `PageFavoriteViewSet.create` (V/page/base.py:471) | `PageFavoriteEndpoints` → `FavoritePageCommand` | `project.page.favorite` · `PRJ(A,M)` | 204 | – | I4 | CE-PAGE-010 |
| EP-0117 | A04:G8 | `DELETE {P}/favorite-pages/{page_id}/` | `PageFavoriteViewSet.destroy` (V/page/base.py:483) | `PageFavoriteEndpoints` → `UnfavoritePageCommand` | `project.page.favorite` · `PRJ(A,M)` | 204 | – | I4 | CE-PAGE-010 |
| EP-0118 | A03:P-28 | `POST {W}/user-favorite-projects/` | `ProjectFavoritesViewSet.create` (V/project/base.py:515) | `ProjectFavoriteEndpoints` → `FavoriteProjectCommand` | `workspace.project.favorite` · `WS(A,M,G)+PRJ-MEMBER` | 204 | SEC-12, DT-WS-05 | I1 | CE-WS-023, CE-PRJ-012 |
| EP-0119 | A03:P-29 | `DELETE {W}/user-favorite-projects/{project_id}/` | `ProjectFavoritesViewSet.destroy` (V/project/base.py:527) | `ProjectFavoriteEndpoints` → `UnfavoriteProjectCommand` | `workspace.project.favorite` · `WS(A,M,G)+OWN` | 204 | SEC-12, DT-WS-05 | I1 | CE-WS-023, CE-PRJ-012 |
| EP-0120 | A04:W15 | `POST {P}/user-favorite-views/` | `IssueViewFavoriteViewSet.create` (V/view/base.py:421) | `ViewFavoriteEndpoints` → `FavoriteViewCommand` | `project.view.favorite` · `PRJ(A,M)` | 204 | – | I3 | CE-LV-050 |
| EP-0121 | A04:W16 | `DELETE {P}/user-favorite-views/{view_id}/` | `IssueViewFavoriteViewSet.destroy` (V/view/base.py:435) | `ViewFavoriteEndpoints` → `UnfavoriteViewCommand` | `project.view.favorite` · `PRJ(A,M)` | 204 | – | I3 | CE-LV-050 |
| EP-0122 | A03:W-01 | `GET /api/workspace-slug-check/` | `WorkSpaceAvailabilityCheckEndpoint.get` (V/workspace/base.py:216) | `WorkspaceEndpoints` → `CheckWorkspaceSlugQuery` | `user.workspace.create` · `AUTH+SELF` | 200 | DT-WS-09 | I0 | CE-WS-001 |
| EP-0123 | A03:W-03 | `POST /api/workspaces/` | `WorkSpaceViewSet.create` (V/workspace/base.py:82) | `WorkspaceEndpoints` → `CreateWorkspaceCommand` | `user.workspace.create` · `AUTH+SELF` | 201 | DT-WS-09 | I0 | CE-WS-001, CE-WS-002, CE-INST-028 |
| EP-0124 | A03:W-04 | `GET {W}/` | `WorkSpaceViewSet.retrieve` (V/workspace/base.py) | `WorkspaceEndpoints` → `GetWorkspaceQuery` | `workspace.settings.read` · `WS(A,M,G)` | 200 | – | I0 | CE-WS-003 |
| EP-0125 | A03:W-06 | `PATCH {W}/` | `WorkSpaceViewSet.partial_update` (V/workspace/base.py:158) | `WorkspaceEndpoints` → `UpdateWorkspaceCommand` | `workspace.settings.update` · `WS(A)` + Prerequisite(— ⚠ wie DELETE `{W}/`, O-D05-08)` | 200 | – | I1 | CE-WS-003 |
| EP-0126 | A03:W-07 | `DELETE {W}/` | `WorkSpaceViewSet.destroy` (V/workspace/base.py:169) | `WorkspaceEndpoints` → `DeleteWorkspaceCommand` | `workspace.settings.delete` · `WS(A)` + Prerequisite(— ⚠ Vorbedingungs-Key für `WorkSpaceBasePermission` PUT/PATCH/DELETE fehlt in ABG-042; beide Stufen identisch WS(A), wirksam DenyStyle.Detail der Klassenstufe – O-D05-08)` | 204 | – | I1 | CE-WS-004 |
| EP-0127 | A03:W-08 | `GET {W}/invitations/` | `WorkspaceInvitationsViewset.list` (V/workspace/invite.py) | `WorkspaceInvitationEndpoints` → `ListWorkspaceInvitationsQuery` | `workspace.invitation.read` · `WS(A,M)` | 200 | – | I1 | CE-WS-010 |
| EP-0128 | A03:W-09 | `POST {W}/invitations/` | `WorkspaceInvitationsViewset.create` (V/workspace/invite.py:52) | `WorkspaceInvitationEndpoints` → `CreateWorkspaceInvitationsCommand` | `workspace.invitation.create` · `WS(A,M)` | 200 | DT-WS-04 | I1 | CE-WS-010 |
| EP-0129 | A03:W-10 | `GET {W}/invitations/{pk}/` | `WorkspaceInvitationsViewset.retrieve` (V/workspace/invite.py) | `WorkspaceInvitationEndpoints` → `GetWorkspaceInvitationQuery` | `workspace.invitation.read` · `WS(A,M)` | 200 | – | I1 | CE-WS-010 |
| EP-0130 | A03:W-11 | `PATCH {W}/invitations/{pk}/` | `WorkspaceInvitationsViewset.partial_update` (V/workspace/invite.py:130) | `WorkspaceInvitationEndpoints` → `UpdateWorkspaceInvitationCommand` | `workspace.invitation.update` · `WS(A,M)` | 200 | – | I1 | CE-WS-010 |
| EP-0131 | A03:W-12 | `DELETE {W}/invitations/{pk}/` | `WorkspaceInvitationsViewset.destroy` (V/workspace/invite.py:153) | `WorkspaceInvitationEndpoints` → `DeleteWorkspaceInvitationCommand` | `workspace.invitation.delete` · `WS(A,M)` | 204 | – | I1 | CE-WS-010 |
| EP-0132 | A03:W-17 | `GET {W}/members/` | `WorkSpaceMemberViewSet.list` (V/workspace/member.py:62) | `WorkspaceMemberEndpoints` → `ListWorkspaceMembersQuery` | `workspace.member.read` · `WS(A,M,G)` | 200 | – | I1 | CE-WS-009 |
| EP-0133 | A03:W-22 | `POST {W}/members/leave/` | `WorkSpaceMemberViewSet.leave` (V/workspace/member.py:187) | `WorkspaceMemberEndpoints` → `LeaveWorkspaceCommand` | `workspace.member.leave` · `WS(A,M,G)` | 204 | – | I1 | CE-WS-009 |
| EP-0134 | A03:W-19 | `GET {W}/members/{pk}/` | `WorkSpaceMemberViewSet.retrieve` (V/workspace/member.py:74) | `WorkspaceMemberEndpoints` → `GetWorkspaceMemberQuery` | `workspace.member.read` · `WS(A,M,G)` | 200 | – | I1 | CE-WS-009 |
| EP-0135 | A03:W-20 | `PATCH {W}/members/{pk}/` | `WorkSpaceMemberViewSet.partial_update` (V/workspace/member.py:93) | `WorkspaceMemberEndpoints` → `UpdateWorkspaceMemberCommand` | `workspace.member.update` · `WS(A)` | 200 | – | I1 | CE-WS-009 |
| EP-0136 | A03:W-21 | `DELETE {W}/members/{pk}/` | `WorkSpaceMemberViewSet.destroy` (V/workspace/member.py:138) | `WorkspaceMemberEndpoints` → `DeleteWorkspaceMemberCommand` | `workspace.member.delete` · `WS(A)` | 204 | – | I1 | CE-WS-009 |
| EP-0137 | A03:W-18 | `GET {W}/project-members/` | `WorkspaceProjectMemberEndpoint.get` (V/workspace/member.py:256) | `WorkspaceMemberEndpoints` → `ListWorkspaceProjectMembershipsQuery` | `workspace.member.read` · `WS(A,M,G)` | 200 | – | I1 | CE-WS-012 |
| EP-0138 | A03:W-24 | `GET {W}/workspace-members/me/` | `WorkspaceMemberUserEndpoint.get` (V/workspace/member.py:233) | `WorkspaceMemberEndpoints` → `GetMyWorkspaceMembershipQuery` | `workspace.member.read_own` · `WS(A,M,G)+SELF` | 200 | – | I0 | CE-WS-012 |
| EP-0139 | A03:W-42 | `GET {W}/cycles/` | `WorkspaceCyclesEndpoint.get` (V/workspace/cycle.py:22) | `WorkspaceMetadataEndpoints` → `ListWorkspaceCyclesQuery` | `workspace.project_metadata.read` · `WS(A,M,G)` | 200 | – | I3 | CE-WS-006 |
| EP-0140 | A03:W-40 | `GET {W}/estimates/` | `WorkspaceEstimatesEndpoint.get` (V/workspace/estimate.py:22) | `WorkspaceMetadataEndpoints` → `ListWorkspaceEstimatesQuery` | `workspace.project_metadata.read` · `WS(A,M,G)` | 200 | – | I1 | CE-WS-006 |
| EP-0141 | A03:W-36 | `GET {W}/labels/` | `WorkspaceLabelsEndpoint.get` (V/workspace/label.py:22) | `WorkspaceMetadataEndpoints` → `ListWorkspaceLabelsQuery` | `workspace.project_metadata.read` · `WS(A,M,G)` | 200 | – | I1 | CE-WS-006 |
| EP-0142 | A03:W-41 | `GET {W}/modules/` | `WorkspaceModulesEndpoint.get` (V/workspace/module.py:25) | `WorkspaceMetadataEndpoints` → `ListWorkspaceModulesQuery` | `workspace.project_metadata.read` · `WS(A,M,G)` | 200 | – | I3 | CE-WS-006 |
| EP-0143 | A03:W-39 | `GET {W}/states/` | `WorkspaceStatesEndpoint.get` (V/workspace/state.py:21) | `WorkspaceMetadataEndpoints` → `ListWorkspaceStatesQuery` | `workspace.project_metadata.read` · `WS(A,M,G)` | 200 | – | I1 | CE-WS-006 |
| EP-0144 | A03:W-59 | `GET {W}/home-preferences/` | `WorkspaceHomePreferenceViewSet.get` (V/workspace/home.py:24) | `WorkspacePreferenceEndpoints` → `ListHomePreferencesQuery` | `workspace.member_preference.read` · `WS(A,M,G)` | 200 | – | I1 | CE-HOME-001, CE-HOME-002 |
| EP-0145 | A03:W-60 | `PATCH {W}/home-preferences/{key}/` | `WorkspaceHomePreferenceViewSet.patch` (V/workspace/home.py:68) | `WorkspacePreferenceEndpoints` → `UpdateHomePreferenceCommand` | `workspace.member_preference.update` · `WS(A,M,G)` | 200 | – | I1 | CE-HOME-002 |
| EP-0146 | A03:W-67 | `GET {W}/sidebar-preferences/` | `WorkspaceUserPreferenceViewSet.get` (V/workspace/user_preference.py:26) | `WorkspacePreferenceEndpoints` → `ListSidebarPreferencesQuery` | `workspace.member_preference.read` · `WS(A,M,G)` | 200 | – | I1 | CE-WS-021, CE-WS-022 |
| EP-0147 | A03:W-68 | `PATCH {W}/sidebar-preferences/` | `WorkspaceUserPreferenceViewSet.patch` (V/workspace/user_preference.py:82) | `WorkspacePreferenceEndpoints` → `UpdateSidebarPreferencesCommand` | `workspace.member_preference.update` · `WS(A,M,G)` | 200 | – | I1 | CE-WS-021, CE-WS-022 |
| EP-0148 | A03:W-37 | `GET {W}/user-properties/` | `WorkspaceUserPropertiesEndpoint.get` (V/workspace/user.py:288) | `WorkspacePreferenceEndpoints` → `GetWorkspaceUserPropertiesQuery` | `workspace.member_preference.read` · `WS(A,M,G)` | 200 | – | I3 | CE-LV-015 |
| EP-0149 | A03:W-38 | `PATCH {W}/user-properties/` | `WorkspaceUserPropertiesEndpoint.patch` (V/workspace/user.py:274) | `WorkspacePreferenceEndpoints` → `UpdateWorkspaceUserPropertiesCommand` | `workspace.member_preference.update` · `WS(A,M,G)` | 200 | – | I3 | CE-LV-015 |
| EP-0150 | A03:W-25 | `POST {W}/workspace-views/` | `WorkspaceMemberUserViewsEndpoint.post` (V/workspace/member.py:222) | `WorkspacePreferenceEndpoints` → `UpdateWorkspaceViewPreferencesCommand` | `workspace.member_preference.update` · `WS(A,M,G)+SELF` | 204 | – | I3 | CE-LV-052 |
| EP-0151 | A03:W-26 | `GET {W}/workspace-themes/` | `WorkspaceThemeViewSet.list` (V/workspace/base.py) | `WorkspaceThemeEndpoints` → `ListWorkspaceThemesQuery` | `workspace.theme.read` · `WS(A,M)` | 200 | – | I1 | CE-WS-007 |
| EP-0152 | A03:W-27 | `POST {W}/workspace-themes/` | `WorkspaceThemeViewSet.create` (V/workspace/base.py:331) | `WorkspaceThemeEndpoints` → `CreateWorkspaceThemeCommand` | `workspace.theme.create` · `WS(A,M)` | 201 | – | I1 | CE-WS-007 |
| EP-0153 | A03:W-28 | `GET {W}/workspace-themes/{pk}/` | `WorkspaceThemeViewSet.retrieve` (V/workspace/base.py) | `WorkspaceThemeEndpoints` → `GetWorkspaceThemeQuery` | `workspace.theme.read` · `WS(A,M)` | 200 | – | I1 | CE-WS-007 |
| EP-0154 | A03:W-29 | `PATCH {W}/workspace-themes/{pk}/` | `WorkspaceThemeViewSet.partial_update` (V/workspace/base.py) | `WorkspaceThemeEndpoints` → `UpdateWorkspaceThemeCommand` | `workspace.theme.update` · `WS(A,M)` | 200 | – | I1 | CE-WS-007 |
| EP-0155 | A03:W-30 | `DELETE {W}/workspace-themes/{pk}/` | `WorkspaceThemeViewSet.destroy` (V/workspace/base.py) | `WorkspaceThemeEndpoints` → `DeleteWorkspaceThemeCommand` | `workspace.theme.delete` · `WS(A,M)` | 204 | – | I1 | CE-WS-007 |
| EP-0156 | A03:W-02 | `GET /api/workspaces/` | `WorkSpaceViewSet.list` (V/workspace/base.py:154) | — (nicht registriert (DT-WS-01)) | – | 400→405 | DT-WS-01 | I0 | CE-WS-005 |
| EP-0157 | A03:W-05 | `PUT {W}/` | `WorkSpaceViewSet.update` (V/workspace/base.py) | — (entfällt (SEC-01)) | – | 200→405 | SEC-01, DT-GEN-01 | I1 | CE-WS-003 |
| EP-0160 | A04:Y12 | `GET {P}/user-favorite-cycles/` | `CycleFavoriteViewSet.list` (V/cycle/base.py) | — (nicht registriert (DT-GEN-15)) | – | 500→405 | DT-GEN-15 | I3 | CE-CYC-015 |
| EP-0161 | A04:M15 | `GET {P}/user-favorite-modules/` | `ModuleFavoriteViewSet.list` (V/module/base.py) | — (nicht registriert (DT-GEN-15)) | – | 500→405 | DT-GEN-15 | I3 | CE-MOD-011 |
| EP-0162 | A04:W14 | `GET {P}/user-favorite-views/` | `IssueViewFavoriteViewSet.list` (V/view/base.py) | — (nicht registriert (DT-GEN-15)) | – | 500→405 | DT-GEN-15 | I3 | CE-LV-050 |
| EP-0163 | A03:P-27 | `GET {W}/user-favorite-projects/` | `ProjectFavoritesViewSet.list` (V/project/base.py) | — (entfällt (SEC-11)) | – | 500→405 | SEC-11, DT-WS-05 | I1 | CE-WS-023, CE-PRJ-012 |

### 4.4 `Plane.Projects` – Projekte, Mitglieder, Einladungen, States, Labels, Estimates, Präferenzen

Ablage der Endpoint-Klassen: `src/modules/Projects/Plane.Projects/Endpoints/App/<Klasse>.cs`. 56 Zeilen, davon 54 registriert und 2 nicht registriert (Entscheidung in Spalte „Abw./DT“).

| EP | Original-ID | Methode · Pfad (Original) | Original-View (Datei) | Ziel: Klasse → Handler | Permission · Ziel-Prüfung | Status Orig→Ziel | Abw./DT | Ink. | CE-IDs |
|---|---|---|---|---|---|---|---|---|---|
| EP-0168 | A03:E-02 | `GET {P}/estimates/` | `BulkEstimatePointEndpoint.list` (V/estimate/base.py:54) | `EstimateEndpoints` → `ListEstimatesQuery` | `project.estimate.read` · `PRJ(A,M,G)` | 200 | – | I1 | CE-PRJ-034 |
| EP-0169 | A03:E-03 | `POST {P}/estimates/` | `BulkEstimatePointEndpoint.create` (V/estimate/base.py:64) | `EstimateEndpoints` → `CreateEstimateCommand` | `project.estimate.create` · `PRJ(A,M)` | 200 | DT-PRJ-06 | I1 | CE-PRJ-035, CE-PRJ-036 |
| EP-0170 | A03:E-04 | `GET {P}/estimates/{estimate_id}/` | `BulkEstimatePointEndpoint.retrieve` (V/estimate/base.py:103) | `EstimateEndpoints` → `GetEstimateQuery` | `project.estimate.read` · `PRJ(A,M,G)` | 200 | – | I1 | CE-PRJ-034 |
| EP-0171 | A03:E-05 | `PATCH {P}/estimates/{estimate_id}/` | `BulkEstimatePointEndpoint.partial_update` (V/estimate/base.py:109) | `EstimateEndpoints` → `UpdateEstimateCommand` | `project.estimate.update` · `PRJ(A,M)` | 200 | – | I1 | CE-PRJ-035, CE-PRJ-036 |
| EP-0172 | A03:E-06 | `DELETE {P}/estimates/{estimate_id}/` | `BulkEstimatePointEndpoint.destroy` (V/estimate/base.py:147) | `EstimateEndpoints` → `DeleteEstimateCommand` | `project.estimate.delete` · `PRJ(A,M)` | 204 | – | I1 | CE-PRJ-038 |
| EP-0173 | A03:E-07 | `POST {P}/estimates/{estimate_id}/estimate-points/` | `EstimatePointEndpoint.create` (V/estimate/base.py:155) | `EstimateEndpoints` → `CreateEstimatePointCommand` | `project.estimate.create` · `PRJ(A,M)` | 200 | DT-PRJ-07 | I1 | CE-PRJ-036, CE-PRJ-037 |
| EP-0174 | A03:E-08 | `PATCH {P}/estimates/{estimate_id}/estimate-points/{estimate_point_id}/` | `EstimatePointEndpoint.partial_update` (V/estimate/base.py:182) | `EstimateEndpoints` → `UpdateEstimatePointCommand` | `project.estimate.update` · `PRJ(A,M)` | 200 | – | I1 | CE-PRJ-036, CE-PRJ-037 |
| EP-0175 | A03:E-09 | `DELETE {P}/estimates/{estimate_id}/estimate-points/{estimate_point_id}/` | `EstimatePointEndpoint.destroy` (V/estimate/base.py:197) | `EstimateEndpoints` → `DeleteEstimatePointCommand` | `project.estimate.delete` · `PRJ(A,M)` | 200 | DT-PRJ-06 | I1 | CE-PRJ-036, CE-PRJ-037 |
| EP-0176 | A03:E-01 | `GET {P}/project-estimates/` | `ProjectEstimatePointEndpoint.get` (V/estimate/base.py:36) | `EstimateEndpoints` → `ListProjectEstimatePointsQuery` | `project.estimate.read_points` · `PRJ(A,M)` | 200 | – | I1 | CE-PRJ-034 |
| EP-0177 | A04:L7 | `POST {P}/bulk-create-labels/` | `BulkCreateIssueLabelsEndpoint.post` (V/issue/label.py:92) | `LabelEndpoints` → `BulkCreateLabelsCommand` | `project.label.create` · `PRJ(A)` | 201 | DT-PRJ-09 | I1 | CE-PRJ-033 |
| EP-0178 | A04:L1 | `GET {P}/issue-labels/` | `LabelViewSet.list` (V/issue/label.py) | `LabelEndpoints` → `ListLabelsQuery` | `project.label.read` · `PRJ(A,M,G)` | 200 | SEC-21, DT-PRJ-08 | I1 | CE-PRJ-028 |
| EP-0179 | A04:L2 | `POST {P}/issue-labels/` | `LabelViewSet.create` (V/issue/label.py:44) | `LabelEndpoints` → `CreateLabelCommand` | `project.label.create` · `PRJ(A)` + Prerequisite(`workspace.project_base.create`)` | 201 | – | I1 | CE-PRJ-029 |
| EP-0180 | A04:L3 | `GET {P}/issue-labels/{pk}/` | `LabelViewSet.retrieve` (V/issue/label.py) | `LabelEndpoints` → `GetLabelQuery` | `project.label.read` · `PRJ(A,M,G)` | 200 | SEC-21, DT-PRJ-08 | I1 | CE-PRJ-028 |
| EP-0181 | A04:L5 | `PATCH {P}/issue-labels/{pk}/` | `LabelViewSet.partial_update` (V/issue/label.py:59) | `LabelEndpoints` → `UpdateLabelCommand` | `project.label.update` · `PRJ(A)` + Prerequisite(`project.project_base.write`)` | 200 | – | I1 | CE-PRJ-029, CE-PRJ-030, CE-PRJ-031 |
| EP-0182 | A04:L6 | `DELETE {P}/issue-labels/{pk}/` | `LabelViewSet.destroy` (V/issue/label.py:86) | `LabelEndpoints` → `DeleteLabelCommand` | `project.label.delete` · `PRJ(A)` + Prerequisite(`project.project_base.write`)` | 204 | – | I1 | CE-PRJ-032 |
| EP-0183 | A03:P-16 | `GET /api/users/me/workspaces/{slug}/project-roles/` | `UserProjectRolesEndpoint.get` (V/project/member.py:370) | `ProjectEndpoints` → `ListMyProjectRolesQuery` | `workspace.project.read` · `WS(A,M,G)` | 200 | – | I1 | CE-WS-012 |
| EP-0184 | A03:P-08 | `GET {W}/project-identifiers/` | `ProjectIdentifierEndpoint.get` (V/project/base.py:447) | `ProjectEndpoints` → `CheckProjectIdentifierQuery` | `workspace.project.check_identifier` · `WS(A,M)` | 200 | – | I0 | CE-PRJ-005 |
| EP-0185 | A03:P-09 | `DELETE {W}/project-identifiers/` | `ProjectIdentifierEndpoint.delete` (V/project/base.py:458) | `ProjectEndpoints` → `ReleaseProjectIdentifierCommand` | `workspace.project.release_identifier` · `WS(A,M)` | 204 | – | I0 | CE-PRJ-005 |
| EP-0186 | A03:P-01 | `GET {W}/projects/` | `ProjectViewSet.list` (V/project/base.py:147) | `ProjectEndpoints` → `ListProjectsQuery` | `workspace.project.read` · `WS(A,M,G)` | 200 | DT-WS-08 | I0 | CE-PRJ-001 |
| EP-0187 | A03:P-02 | `POST {W}/projects/` | `ProjectViewSet.create` (V/project/base.py:259) | `ProjectEndpoints` → `CreateProjectCommand` | `workspace.project.create` · `WS(A,M)` | 201 | – | I0 | CE-PRJ-004 |
| EP-0188 | A03:P-03 | `GET {W}/projects/details/` | `ProjectViewSet.list_detail` (V/project/base.py:103) | `ProjectEndpoints` → `ListProjectDetailsQuery` | `workspace.project.read` · `WS(A,M,G)` | 200 | DT-WS-08 | I1 | CE-PRJ-001, CE-PRJ-002 |
| EP-0189 | A03:P-04 | `GET {W}/projects/{pk}/` | `ProjectViewSet.retrieve` (V/project/base.py:227) | `ProjectEndpoints` → `GetProjectQuery` | `project.project.read` · `WS(A,M,G)` | 200 | – | I0 | CE-PRJ-006 |
| EP-0190 | A03:P-06 | `PATCH {W}/projects/{pk}/` | `ProjectViewSet.partial_update` (V/project/base.py:315) | `ProjectEndpoints` → `UpdateProjectCommand` | `project.project.update` · `WSA\|PA` | 200 | DT-PRJ-05 | I1 | CE-PRJ-018, CE-PRJ-019, CE-PRJ-022, CE-PRJ-039, CE-PRJ-040 |
| EP-0191 | A03:P-07 | `DELETE {W}/projects/{pk}/` | `ProjectViewSet.destroy` (V/project/base.py:383) | `ProjectEndpoints` → `DeleteProjectCommand` | `project.project.delete` · `WSA\|PA` | 204 | – | I1 | CE-PRJ-009 |
| EP-0192 | A03:P-35 | `POST {P}/archive/` | `ProjectArchiveUnarchiveEndpoint.post` (V/project/base.py:430) | `ProjectEndpoints` → `ArchiveProjectCommand` | `project.project.archive` · `PRJ(A,M)` | 200 | – | I1 | CE-PRJ-008 |
| EP-0193 | A03:P-36 | `DELETE {P}/archive/` | `ProjectArchiveUnarchiveEndpoint.delete` (V/project/base.py:438) | `ProjectEndpoints` → `UnarchiveProjectCommand` | `project.project.unarchive` · `PRJ(A,M)` | 204 | – | I1 | CE-PRJ-008 |
| EP-0194 | A03:P-15 | `POST /api/users/me/workspaces/{slug}/projects/invitations/` | `UserProjectInvitationsViewset.create` (V/project/invite.py:131) | `ProjectInvitationEndpoints` → `AcceptMyProjectInvitationsCommand` | `workspace.project_invitation.accept` · `WS(A,M)` | 201 | – | I1 | CE-PRJ-010 |
| EP-0195 | A03:P-10 | `GET {P}/invitations/` | `ProjectInvitationsViewset.list` (V/project/invite.py) | `ProjectInvitationEndpoints` → `ListProjectInvitationsQuery` | `project.invitation.read` · `PRJ(A)` | 200 | SEC-05, DT-PRJ-02 | I1 | CE-PRJ-010 |
| EP-0196 | A03:P-11 | `POST {P}/invitations/` | `ProjectInvitationsViewset.create` (V/project/invite.py:56) | `ProjectInvitationEndpoints` → `CreateProjectInvitationsCommand` | `project.invitation.create` · `PRJ(A)` | 500→200 | DT-PRJ-01 | I1 | CE-PRJ-010 |
| EP-0197 | A03:P-12 | `GET {P}/invitations/{pk}/` | `ProjectInvitationsViewset.retrieve` (V/project/invite.py) | `ProjectInvitationEndpoints` → `GetProjectInvitationQuery` | `project.invitation.read` · `PRJ(A)` | 200 | SEC-05, DT-PRJ-02 | I1 | CE-PRJ-010 |
| EP-0198 | A03:P-13 | `DELETE {P}/invitations/{pk}/` | `ProjectInvitationsViewset.destroy` (V/project/invite.py) | `ProjectInvitationEndpoints` → `DeleteProjectInvitationCommand` | `project.invitation.delete` · `PRJ(A)` | 204 | SEC-05, DT-PRJ-02 | I1 | CE-PRJ-010 |
| EP-0199 | A03:P-19 | `GET {P}/members/` | `ProjectMemberViewSet.list` (V/project/member.py:157) | `ProjectMemberEndpoints` → `ListProjectMembersQuery` | `project.member.read` · `PRJ(A,M,G)` | 200 | – | I1 | CE-PRJ-021 |
| EP-0200 | A03:P-20 | `POST {P}/members/` | `ProjectMemberViewSet.create` (V/project/member.py:47) | `ProjectMemberEndpoints` → `CreateProjectMemberCommand` | `project.member.create` · `PRJ(A)` | 201 | – | I1 | CE-PRJ-021 |
| EP-0201 | A03:P-24 | `POST {P}/members/leave/` | `ProjectMemberViewSet.leave` (V/project/member.py:325) | `ProjectMemberEndpoints` → `LeaveProjectCommand` | `project.member.leave` · `PRJ(A,M,G)` | 204 | – | I1 | CE-PRJ-007 |
| EP-0202 | A03:P-21 | `GET {P}/members/{pk}/` | `ProjectMemberViewSet.retrieve` (V/project/member.py:172) | `ProjectMemberEndpoints` → `GetProjectMemberQuery` | `project.member.read` · `PRJ(A,M,G)` | 200 | – | I1 | CE-PRJ-021 |
| EP-0203 | A03:P-22 | `PATCH {P}/members/{pk}/` | `ProjectMemberViewSet.partial_update` (V/project/member.py:207) | `ProjectMemberEndpoints` → `UpdateProjectMemberCommand` | `project.member.update` · `PRJ(A)` | 200 | – | I1 | CE-PRJ-021 |
| EP-0204 | A03:P-23 | `DELETE {P}/members/{pk}/` | `ProjectMemberViewSet.destroy` (V/project/member.py:292) | `ProjectMemberEndpoints` → `DeleteProjectMemberCommand` | `project.member.delete` · `PRJ(A)` | 204 | – | I1 | CE-PRJ-021 |
| EP-0205 | A03:P-26 | `GET {P}/project-members/me/` | `ProjectMemberUserEndpoint.get` (V/project/member.py:354) | `ProjectMemberEndpoints` → `GetMyProjectMembershipQuery` | `project.member.read_own` · `PRJ(A,M,G)+SELF` | 200 | – | I0 | CE-PRJ-006, CE-PRJ-021 |
| EP-0206 | A04:Y16 | `GET {P}/cycles/{cycle_id}/user-properties/` | `CycleUserPropertiesEndpoint.get` (V/cycle/base.py:652) | `ProjectPreferenceEndpoints` → `GetCycleUserPropertiesQuery` | `project.member_preference.read` · `PRJ(A,M,G)` | 200 | – | I3 | CE-LV-016 |
| EP-0207 | A04:Y17 | `PATCH {P}/cycles/{cycle_id}/user-properties/` | `CycleUserPropertiesEndpoint.patch` (V/cycle/base.py:632) | `ProjectPreferenceEndpoints` → `UpdateCycleUserPropertiesCommand` | `project.member_preference.update` · `PRJ(A,M,G)` | 201 | – | I3 | CE-LV-016 |
| EP-0208 | A04:M18 | `GET {P}/modules/{module_id}/user-properties/` | `ModuleUserPropertiesEndpoint.get` (V/module/base.py:858) | `ProjectPreferenceEndpoints` → `GetModuleUserPropertiesQuery` | `project.member_preference.read` · `PRJ(A,M,G)` | 200 | – | I3 | CE-LV-016 |
| EP-0209 | A04:M19 | `PATCH {P}/modules/{module_id}/user-properties/` | `ModuleUserPropertiesEndpoint.patch` (V/module/base.py:838) | `ProjectPreferenceEndpoints` → `UpdateModuleUserPropertiesCommand` | `project.member_preference.update` · `PRJ(A,M,G)` | 201 | – | I3 | CE-LV-016 |
| EP-0210 | A03:P-37 | `GET {P}/preferences/member/{member_id}/` | `ProjectMemberPreferenceEndpoint.get` (V/project/member.py:404) | `ProjectPreferenceEndpoints` → `GetProjectMemberPreferencesQuery` | `project.member_preference.read` · `PRJ(A,M,G)` | 200 | – | I1 | CE-PRJ-016 |
| EP-0211 | A03:P-38 | `PATCH {P}/preferences/member/{member_id}/` | `ProjectMemberPreferenceEndpoint.patch` (V/project/member.py:392) | `ProjectPreferenceEndpoints` → `UpdateProjectMemberPreferencesCommand` | `project.member_preference.update` · `PRJ(A,M,G)+SELF` | 200 | SEC-17, DT-PRJ-04 | I1 | CE-PRJ-016 |
| EP-0212 | A03:P-25 | `POST {P}/project-views/` | `ProjectUserViewsEndpoint.post` (V/project/base.py:476) | `ProjectPreferenceEndpoints` → `UpdateProjectViewPreferencesCommand` | `project.member_preference.update` · `PRJ(A,M,G)+SELF` | 204 | – | I1 | CE-PRJ-016 |
| EP-0213 | A04:I10 | `GET {P}/user-properties/` | `ProjectUserDisplayPropertyEndpoint.get` (V/issue/base.py:769) | `ProjectPreferenceEndpoints` → `GetProjectUserPropertiesQuery` | `project.member_preference.read` · `PRJ(A,M,G)` | 200 | – | I2 | CE-LV-014 |
| EP-0214 | A04:I11 | `PATCH {P}/user-properties/` | `ProjectUserDisplayPropertyEndpoint.patch` (V/issue/base.py:747) | `ProjectPreferenceEndpoints` → `UpdateProjectUserPropertiesCommand` | `project.member_preference.update` · `PRJ(A,M,G)` | 200 | – | I2 | CE-LV-014 |
| EP-0215 | A03:S-06 | `GET {P}/intake-state/` | `IntakeStateEndpoint.get` (V/state/base.py:143) | `StateEndpoints` → `GetIntakeStateQuery` | `project.state.read` · `PRJ(A,M,G)` | 200 | – | I3 | CE-INT-001 |
| EP-0216 | A03:S-01 | `GET {P}/states/` | `StateViewSet.list` (V/state/base.py:81) | `StateEndpoints` → `ListStatesQuery` | `project.state.read` · `PRJ(A,M,G)` | 200 | – | I1 | CE-PRJ-023 |
| EP-0217 | A03:S-02 | `POST {P}/states/` | `StateViewSet.create` (V/state/base.py:48) | `StateEndpoints` → `CreateStateCommand` | `project.state.create` · `PRJ(A)` | 200 | – | I1 | CE-PRJ-024 |
| EP-0218 | A03:S-03 | `GET {P}/states/{pk}/` | `StateViewSet.retrieve` (V/state/base.py) | `StateEndpoints` → `GetStateQuery` | `project.state.read` · `PRJ(A,M,G)` | 200 | – | I1 | CE-PRJ-023 |
| EP-0219 | A03:S-04 | `PATCH {P}/states/{pk}/` | `StateViewSet.partial_update` (V/state/base.py:64) | `StateEndpoints` → `UpdateStateCommand` | `project.state.update` · `PRJ(A)` | 200 | – | I1 | CE-PRJ-024, CE-PRJ-025 |
| EP-0220 | A03:S-05 | `DELETE {P}/states/{pk}/` | `StateViewSet.destroy` (V/state/base.py:119) | `StateEndpoints` → `DeleteStateCommand` | `project.state.delete` · `PRJ(A)` | 204 | – | I1 | CE-PRJ-027 |
| EP-0221 | A03:S-07 | `POST {P}/states/{pk}/mark-default/` | `StateViewSet.mark_as_default` (V/state/base.py:109) | `StateEndpoints` → `MarkDefaultStateCommand` | `project.state.update` · `PRJ(A)` | 204 | – | I1 | CE-PRJ-026 |
| EP-0222 | A03:P-05 | `PUT {W}/projects/{pk}/` | `ProjectViewSet.update` (V/project/base.py) | — (entfällt (SEC-01)) | – | 200→405 | SEC-01, DT-GEN-01 | I1 | CE-PRJ-018, CE-PRJ-019, CE-PRJ-022, CE-PRJ-039, CE-PRJ-040 |
| EP-0223 | A04:L4 | `PUT {P}/issue-labels/{pk}/` | `LabelViewSet.update` (V/issue/label.py) | — (entfällt (ABG-043)) | – | 200→405 | DT-GEN-01 | I1 | CE-PRJ-029, CE-PRJ-030, CE-PRJ-031 |

### 4.5 `Plane.WorkItems` – Work Items, Kommentare, Reaktionen, Links, Anhänge, Relationen, Abos, Versionen, Drafts

Ablage der Endpoint-Klassen: `src/modules/WorkItems/Plane.WorkItems/Endpoints/App/<Klasse>.cs`. 69 Zeilen, davon 65 registriert und 4 nicht registriert (Entscheidung in Spalte „Abw./DT“).

| EP | Original-ID | Methode · Pfad (Original) | Original-View (Datei) | Ziel: Klasse → Handler | Permission · Ziel-Prüfung | Status Orig→Ziel | Abw./DT | Ink. | CE-IDs |
|---|---|---|---|---|---|---|---|---|---|
| EP-0224 | A03:W-48, A04:D1 | `GET {W}/draft-issues/` | `WorkspaceDraftIssueViewSet.list` (V/workspace/draft.py:120) | `DraftWorkItemEndpoints` → `ListDraftWorkItemsQuery` | `workspace.draft_work_item.read` · `WS(A,M,G)+OWN` | 200 | – | I2 | CE-WI-049 |
| EP-0225 | A03:W-49, A04:D2 | `POST {W}/draft-issues/` | `WorkspaceDraftIssueViewSet.create` (V/workspace/draft.py:133) | `DraftWorkItemEndpoints` → `CreateDraftWorkItemCommand` | `workspace.draft_work_item.create` · `WS(A,M,G)` | 201 | – | I2 | CE-WI-049 |
| EP-0226 | A03:W-50, A04:D3 | `GET {W}/draft-issues/{pk}/` | `WorkspaceDraftIssueViewSet.retrieve` (V/workspace/draft.py:224) | `DraftWorkItemEndpoints` → `GetDraftWorkItemQuery` | `workspace.draft_work_item.read` · `WS(A,M,G)+OWN` | 200 | SEC-15, DT-WS-06 | I2 | CE-WI-049 |
| EP-0227 | A03:W-51, A04:D4 | `PATCH {W}/draft-issues/{pk}/` | `WorkspaceDraftIssueViewSet.partial_update` (V/workspace/draft.py:190) | `DraftWorkItemEndpoints` → `UpdateDraftWorkItemCommand` | `workspace.draft_work_item.update` · `WS(A,M,G)+OWN` | 204 | SEC-15, DT-WS-06 | I2 | CE-WI-049 |
| EP-0228 | A03:W-52, A04:D5 | `DELETE {W}/draft-issues/{pk}/` | `WorkspaceDraftIssueViewSet.destroy` (V/workspace/draft.py:237) | `DraftWorkItemEndpoints` → `DeleteDraftWorkItemCommand` | `workspace.draft_work_item.delete` · `WS(A,M,G)+OWN` | 204 | SEC-15, DT-WS-06 | I2 | CE-WI-049 |
| EP-0229 | A03:W-53, A04:D6 | `POST {W}/draft-to-issue/{draft_id}/` | `WorkspaceDraftIssueViewSet.create_draft_to_issue` (V/workspace/draft.py:243) | `DraftWorkItemEndpoints` → `ConvertDraftWorkItemCommand` | `workspace.draft_work_item.convert` · `WS(A,M)` | 201 | DT-WS-07 | I2 | CE-WI-049 |
| EP-0230 | A04:C10 | `GET {P}/comments/{comment_id}/reactions/` | `CommentReactionViewSet.list` (V/issue/comment.py) | `ReactionEndpoints` → `ListCommentReactionsQuery` | `project.reaction.read` · `PRJ(A,M,G)+VIS` | 200 | SEC-04, DT-WI-01 | I2 | CE-WI-038 |
| EP-0231 | A04:C11 | `POST {P}/comments/{comment_id}/reactions/` | `CommentReactionViewSet.create` (V/issue/comment.py:209) | `ReactionEndpoints` → `AddCommentReactionCommand` | `project.reaction.create` · `PRJ(A,M,G)` | 201 | – | I2 | CE-WI-038 |
| EP-0232 | A04:C12 | `DELETE {P}/comments/{comment_id}/reactions/{reaction_code}/` | `CommentReactionViewSet.destroy` (V/issue/comment.py:240) | `ReactionEndpoints` → `RemoveCommentReactionCommand` | `project.reaction.delete` · `PRJ(A,M,G)` | 204 | – | I2 | CE-WI-038 |
| EP-0233 | A04:C7 | `GET {P}/issues/{issue_id}/reactions/` | `IssueReactionViewSet.list` (V/issue/reaction.py) | `ReactionEndpoints` → `ListWorkItemReactionsQuery` | `project.reaction.read` · `PRJ(A,M,G)+VIS` | 200 | SEC-04, DT-WI-01 | I2 | CE-WI-038 |
| EP-0234 | A04:C8 | `POST {P}/issues/{issue_id}/reactions/` | `IssueReactionViewSet.create` (V/issue/reaction.py:46) | `ReactionEndpoints` → `AddWorkItemReactionCommand` | `project.reaction.create` · `PRJ(A,M,G)` | 201 | – | I2 | CE-WI-038 |
| EP-0235 | A04:C9 | `DELETE {P}/issues/{issue_id}/reactions/{reaction_code}/` | `IssueReactionViewSet.destroy` (V/issue/reaction.py:67) | `ReactionEndpoints` → `RemoveWorkItemReactionCommand` | `project.reaction.delete` · `PRJ(A,M,G)` | 204 | – | I2 | CE-WI-038 |
| EP-0236 | A04:C13 | `GET {P}/issues/{issue_id}/history/` | `IssueActivityEndpoint.get` (V/issue/activity.py:31) | `WorkItemActivityEndpoints` → `ListWorkItemHistoryQuery` | `project.work_item_activity.read` · `PRJ(A,M,G)+VIS` + Prerequisite(`project.project_entity.read`)` | 200 | – | I2 | CE-WI-039, CE-WI-040 |
| EP-0237 | A04:V1 | `GET {P}/issues/{issue_id}/versions/` | `IssueVersionEndpoint.get` (V/issue/version.py:37) | `WorkItemActivityEndpoints` → `ListWorkItemVersionsQuery` | `project.work_item_activity.read` · `PRJ(A,M,G)+VIS` | 200 | – | I2 | CE-WI-042 |
| EP-0238 | A04:V2 | `GET {P}/issues/{issue_id}/versions/{pk}/` | `IssueVersionEndpoint.get` (V/issue/version.py:37) | `WorkItemActivityEndpoints` → `GetWorkItemVersionQuery` | `project.work_item_activity.read` · `PRJ(A,M,G)+VIS` | 200 | – | I2 | CE-WI-042 |
| EP-0239 | A04:V3 | `GET {P}/work-items/{work_item_id}/description-versions/` | `WorkItemDescriptionVersionEndpoint.get` (V/issue/version.py:87) | `WorkItemActivityEndpoints` → `ListWorkItemDescriptionVersionsQuery` | `project.work_item_activity.read` · `PRJ(A,M,G)+VIS` | 200 | – | I2 | CE-WI-041 |
| EP-0240 | A04:V4 | `GET {P}/work-items/{work_item_id}/description-versions/{pk}/` | `WorkItemDescriptionVersionEndpoint.get` (V/issue/version.py:87) | `WorkItemActivityEndpoints` → `GetWorkItemDescriptionVersionQuery` | `project.work_item_activity.read` · `PRJ(A,M,G)+VIS` | 200 | – | I2 | CE-WI-041 |
| EP-0241 | A04:K11 | `GET {AV2}/workspaces/{slug}/projects/{project_id}/issues/{issue_id}/attachments/` | `IssueAttachmentV2Endpoint.get` (V/issue/attachment.py:178) | `WorkItemAttachmentEndpoints` → `ListWorkItemAttachmentsQuery` | `project.work_item_attachment.read` · `PRJ(A,M,G)` | 200 | – | I2 | CE-WI-036, CE-OPS-012 |
| EP-0242 | A04:K13 | `POST {AV2}/workspaces/{slug}/projects/{project_id}/issues/{issue_id}/attachments/` | `IssueAttachmentV2Endpoint.post` (V/issue/attachment.py:102) | `WorkItemAttachmentEndpoints` → `CreateWorkItemAttachmentUploadCommand` | `project.work_item_attachment.create` · `PRJ(A,M,G)` | 200 | – | I2 | CE-WI-036, CE-OPS-012 |
| EP-0243 | A04:K12 | `GET {AV2}/workspaces/{slug}/projects/{project_id}/issues/{issue_id}/attachments/{pk}/` | `IssueAttachmentV2Endpoint.get` (V/issue/attachment.py:178) | `WorkItemAttachmentEndpoints` → `GetWorkItemAttachmentRedirectQuery` | `project.work_item_attachment.read` · `PRJ(A,M,G)` | 302 | – | I2 | CE-WI-036, CE-OPS-012 |
| EP-0244 | A04:K14 | `PATCH {AV2}/workspaces/{slug}/projects/{project_id}/issues/{issue_id}/attachments/{pk}/` | `IssueAttachmentV2Endpoint.patch` (V/issue/attachment.py:211) | `WorkItemAttachmentEndpoints` → `ConfirmWorkItemAttachmentUploadCommand` | `project.work_item_attachment.update` · `PRJ(A,M,G)` | 204 | – | I2 | CE-WI-036, CE-OPS-012 |
| EP-0245 | A04:K15 | `DELETE {AV2}/workspaces/{slug}/projects/{project_id}/issues/{issue_id}/attachments/{pk}/` | `IssueAttachmentV2Endpoint.delete` (V/issue/attachment.py:155) | `WorkItemAttachmentEndpoints` → `DeleteWorkItemAttachmentCommand` | `project.work_item_attachment.delete` · `PRJ(A)+C:FileAsset` | 204 | – | I2 | CE-WI-036, CE-OPS-012 |
| EP-0246 | A04:K7 | `GET {P}/issues/{issue_id}/issue-attachments/` | `IssueAttachmentEndpoint.get` (V/issue/attachment.py:91) | `WorkItemAttachmentEndpoints` → `ListWorkItemAttachmentsQuery` | `project.work_item_attachment.read` · `PRJ(A,M,G)` | 200 | – | I2 | CE-WI-036 |
| EP-0247 | A04:K8 | `POST {P}/issues/{issue_id}/issue-attachments/` | `IssueAttachmentEndpoint.post` (V/issue/attachment.py:38) | `WorkItemAttachmentEndpoints` → `CreateWorkItemAttachmentCommand` | `project.work_item_attachment.create` · `PRJ(A,M,G)` | 201 | – | I2 | CE-WI-036 |
| EP-0248 | A04:K10 | `DELETE {P}/issues/{issue_id}/issue-attachments/{pk}/` | `IssueAttachmentEndpoint.delete` (V/issue/attachment.py:65) | `WorkItemAttachmentEndpoints` → `DeleteWorkItemAttachmentCommand` | `project.work_item_attachment.delete` · `PRJ(A)+C:FileAsset` | 204 | – | I2 | CE-WI-036 |
| EP-0249 | A04:C1 | `GET {P}/issues/{issue_id}/comments/` | `IssueCommentViewSet.list` (V/issue/comment.py:69) | `WorkItemCommentEndpoints` → `ListWorkItemCommentsQuery` | `project.work_item_comment.read` · `PRJ(A,M,G)+VIS` | 200 | – | I2 | CE-WI-037, CE-WI-044 |
| EP-0250 | A04:C2 | `POST {P}/issues/{issue_id}/comments/` | `IssueCommentViewSet.create` (V/issue/comment.py:76) | `WorkItemCommentEndpoints` → `CreateWorkItemCommentCommand` | `project.work_item_comment.create` · `PRJ(A,M,G)` | 201 | – | I2 | CE-WI-037, CE-WI-044 |
| EP-0251 | A04:C3 | `GET {P}/issues/{issue_id}/comments/{pk}/` | `IssueCommentViewSet.retrieve` (V/issue/comment.py) | `WorkItemCommentEndpoints` → `GetWorkItemCommentQuery` | `project.work_item_comment.read` · `PRJ(A,M,G)+VIS` | 200 | SEC-04, DT-WI-01 | I2 | CE-WI-037, CE-WI-044 |
| EP-0252 | A04:C5 | `PATCH {P}/issues/{issue_id}/comments/{pk}/` | `IssueCommentViewSet.partial_update` (V/issue/comment.py:130) | `WorkItemCommentEndpoints` → `UpdateWorkItemCommentCommand` | `project.work_item_comment.update` · `PRJ(A)+C:IssueComment` | 200 | – | I2 | CE-WI-037, CE-WI-044 |
| EP-0253 | A04:C6 | `DELETE {P}/issues/{issue_id}/comments/{pk}/` | `IssueCommentViewSet.destroy` (V/issue/comment.py:168) | `WorkItemCommentEndpoints` → `DeleteWorkItemCommentCommand` | `project.work_item_comment.delete` · `PRJ(A)+C:IssueComment` | 204 | – | I2 | CE-WI-037, CE-WI-044 |
| EP-0254 | A04:A1 | `GET {P}/archived-issues/` | `IssueArchiveViewSet.list` (V/issue/archive.py:107) | `WorkItemEndpoints` → `ListArchivedWorkItemsQuery` | `project.work_item.read_archived` · `PRJ(A,M)+VIS` | 200 | – | I3 | CE-WI-045, CE-LV-046 |
| EP-0255 | A04:A5 | `POST {P}/bulk-archive-issues/` | `BulkArchiveIssuesEndpoint.post` (V/issue/archive.py:309) | `WorkItemEndpoints` → `BulkArchiveWorkItemsCommand` | `project.work_item.archive` · `PRJ(A,M)` + Prerequisite(`project.project_entity.write`)` | 200 | DT-WI-05 | I3 | CE-WI-046 |
| EP-0256 | A04:A6 | `DELETE {P}/bulk-delete-issues/` | `BulkDeleteIssuesEndpoint.delete` (V/issue/base.py:777) | `WorkItemEndpoints` → `BulkDeleteWorkItemsCommand` | `project.work_item.delete` · `PRJ(A)` | 200 | DT-WI-05 | I2 | CE-WI-048 |
| EP-0257 | A04:A7 | `GET {P}/deleted-issues/` | `DeletedIssuesListViewSet.get` (V/issue/base.py:804) | `WorkItemEndpoints` → `ListDeletedWorkItemIdsQuery` | `project.work_item.read` · `PRJ(A,M,G)+VIS` | 200 | – | I2 | CE-WI-012 |
| EP-0258 | A04:A8 | `POST {P}/issue-dates/` | `IssueBulkUpdateDateEndpoint.post` (V/issue/base.py:1129) | `WorkItemEndpoints` → `BulkUpdateWorkItemDatesCommand` | `project.work_item.update` · `PRJ(A,M)` | 200 | DT-WI-05 | I2 | CE-LV-030 |
| EP-0259 | A04:I4 | `GET {P}/issues-detail/` | `IssueDetailEndpoint.get` (V/issue/base.py:1030) | `WorkItemEndpoints` → `ListWorkItemDetailsQuery` | `project.work_item.read` · `PRJ(A,M,G)+VIS` | 200 | – | I2 | CE-LV-033 |
| EP-0260 | A04:I2 | `GET {P}/issues/` | `IssueViewSet.list` (V/issue/base.py:267) | `WorkItemEndpoints` → `ListWorkItemsQuery` | `project.work_item.read` · `PRJ(A,M,G)+VIS` | 200 | DT-WI-07 | I2 | CE-LV-005, CE-LV-006, CE-LV-010 |
| EP-0261 | A04:I3 | `POST {P}/issues/` | `IssueViewSet.create` (V/issue/base.py:406) | `WorkItemEndpoints` → `CreateWorkItemCommand` | `project.work_item.create` · `PRJ(A,M)` | 201 | – | I2 | CE-WI-001, CE-WI-002 |
| EP-0262 | A04:I1 | `GET {P}/issues/list/` | `IssueListEndpoint.get` (V/issue/base.py:86) | `WorkItemEndpoints` → `ListWorkItemsByIdsQuery` | `project.work_item.read` · `PRJ(A,M,G)+VIS` | 200 | DT-WI-02 | I2 | CE-WI-011 |
| EP-0263 | A04:I12 | `GET {P}/issues/{issue_id}/meta/` | `IssueMetaEndpoint.get` (V/issue/base.py:1190) | `WorkItemEndpoints` → `GetWorkItemMetaQuery` | `project.work_item.read` · `PRJ(A,M,G)+VIS` | 200 | – | I2 | CE-WI-011 |
| EP-0264 | A04:R4 | `GET {P}/issues/{issue_id}/sub-issues/` | `SubIssuesEndpoint.get` (V/issue/sub_issue.py:37) | `WorkItemEndpoints` → `ListSubWorkItemsQuery` | `project.work_item.read` · `PRJ(A,M,G)+VIS` | 200 | – | I2 | CE-WI-032, CE-WI-031 |
| EP-0265 | A04:R5 | `POST {P}/issues/{issue_id}/sub-issues/` | `SubIssuesEndpoint.post` (V/issue/sub_issue.py:210) | `WorkItemEndpoints` → `SetSubWorkItemsCommand` | `project.work_item.update` · `PRJ(A,M)` | 200 | – | I2 | CE-WI-032, CE-WI-031 |
| EP-0266 | A04:I6 | `GET {P}/issues/{pk}/` | `IssueViewSet.retrieve` (V/issue/base.py:494) | `WorkItemEndpoints` → `GetWorkItemQuery` | `project.work_item.read` · `PRJ(A,M,G)+C:Issue+VIS` | 200 | – | I2 | CE-WI-010, CE-WI-015 |
| EP-0267 | A04:I8 | `PATCH {P}/issues/{pk}/` | `IssueViewSet.partial_update` (V/issue/base.py:629) | `WorkItemEndpoints` → `UpdateWorkItemCommand` | `project.work_item.update` · `PRJ(A,M)+C:Issue` | 204 | – | I2 | CE-WI-003, CE-WI-004, CE-WI-005, CE-WI-020 |
| EP-0268 | A04:I9 | `DELETE {P}/issues/{pk}/` | `IssueViewSet.destroy` (V/issue/base.py:719) | `WorkItemEndpoints` → `DeleteWorkItemCommand` | `project.work_item.delete` · `PRJ(A)+C:Issue` | 204 | – | I2 | CE-WI-047 |
| EP-0269 | A04:A2 | `GET {P}/issues/{pk}/archive/` | `IssueArchiveViewSet.retrieve` (V/issue/archive.py:221) | `WorkItemEndpoints` → `GetArchivedWorkItemQuery` | `project.work_item.read_archived` · `PRJ(A,M)+VIS` | 200 | DT-WI-06 | I3 | CE-WI-045 |
| EP-0270 | A04:A3 | `POST {P}/issues/{pk}/archive/` | `IssueArchiveViewSet.archive` (V/issue/archive.py:257) | `WorkItemEndpoints` → `ArchiveWorkItemCommand` | `project.work_item.archive` · `PRJ(A,M)` | 200 | – | I3 | CE-WI-045 |
| EP-0271 | A04:A4 | `DELETE {P}/issues/{pk}/archive/` | `IssueArchiveViewSet.unarchive` (V/issue/archive.py:281) | `WorkItemEndpoints` → `UnarchiveWorkItemCommand` | `project.work_item.unarchive` · `PRJ(A,M)` | 204 | – | I3 | CE-WI-045 |
| EP-0272 | A03:SR-02 | `GET {P}/search-issues/` | `IssueSearchEndpoint.get` (V/search/issue.py:100) | `WorkItemEndpoints` → `SearchWorkItemsForPickerQuery` | `project.work_item.search` · `PRJ(A,M,G)+VIS` | 200 | – | I2 | CE-SRCH-003, CE-WI-008 |
| EP-0273 | A04:I5 | `GET {P}/v2/issues/` | `IssuePaginatedViewSet.list` (V/issue/base.py:867) | `WorkItemEndpoints` → `SyncWorkItemsQuery` | `project.work_item.read` · `PRJ(A,M,G)+VIS` | 200 | DT-GEN-11 | I2 | CE-WI-012 |
| EP-0274 | A04:I13 | `GET {W}/work-items/{project_identifier}-{issue_identifier}/` | `IssueDetailIdentifierEndpoint.get` (V/issue/base.py:1209) | `WorkItemEndpoints` → `GetWorkItemByIdentifierQuery` | `project.work_item.read` · `PRJ(A,M,G)+VIS` | 200 | – | I2 | CE-WI-009 |
| EP-0275 | A04:K1 | `GET {P}/issues/{issue_id}/issue-links/` | `IssueLinkViewSet.list` (V/issue/link.py) | `WorkItemLinkEndpoints` → `ListWorkItemLinksQuery` | `project.work_item_link.read` · `PRJ(A,M,G)` | 200 | – | I2 | CE-WI-035 |
| EP-0276 | A04:K2 | `POST {P}/issues/{issue_id}/issue-links/` | `IssueLinkViewSet.create` (V/issue/link.py:48) | `WorkItemLinkEndpoints` → `CreateWorkItemLinkCommand` | `project.work_item_link.create` · `PRJ(A,M)` | 201 | – | I2 | CE-WI-035 |
| EP-0277 | A04:K3 | `GET {P}/issues/{issue_id}/issue-links/{pk}/` | `IssueLinkViewSet.retrieve` (V/issue/link.py) | `WorkItemLinkEndpoints` → `GetWorkItemLinkQuery` | `project.work_item_link.read` · `PRJ(A,M,G)` | 200 | – | I2 | CE-WI-035 |
| EP-0278 | A04:K5 | `PATCH {P}/issues/{issue_id}/issue-links/{pk}/` | `IssueLinkViewSet.partial_update` (V/issue/link.py:73) | `WorkItemLinkEndpoints` → `UpdateWorkItemLinkCommand` | `project.work_item_link.update` · `PRJ(A,M)` | 200 | – | I2 | CE-WI-035 |
| EP-0279 | A04:K6 | `DELETE {P}/issues/{issue_id}/issue-links/{pk}/` | `IssueLinkViewSet.destroy` (V/issue/link.py:104) | `WorkItemLinkEndpoints` → `DeleteWorkItemLinkCommand` | `project.work_item_link.delete` · `PRJ(A,M)` | 204 | – | I2 | CE-WI-035 |
| EP-0280 | A04:R1 | `GET {P}/issues/{issue_id}/issue-relation/` | `IssueRelationViewSet.list` (V/issue/relation.py:61) | `WorkItemRelationEndpoints` → `ListWorkItemRelationsQuery` | `project.work_item_relation.read` · `PRJ(A,M,G)` | 200 | DT-WI-03 | I2 | CE-WI-033 |
| EP-0281 | A04:R2 | `POST {P}/issues/{issue_id}/issue-relation/` | `IssueRelationViewSet.create` (V/issue/relation.py:240) | `WorkItemRelationEndpoints` → `CreateWorkItemRelationsCommand` | `project.work_item_relation.create` · `PRJ(A,M)` | 201 | DT-WI-03 | I2 | CE-WI-033 |
| EP-0282 | A04:R3 | `POST {P}/issues/{issue_id}/remove-relation/` | `IssueRelationViewSet.remove_relation` (V/issue/relation.py:309) | `WorkItemRelationEndpoints` → `RemoveWorkItemRelationCommand` | `project.work_item_relation.delete` · `PRJ(A,M)` | 204 | – | I2 | CE-WI-033 |
| EP-0283 | A04:S1 | `GET {P}/issues/{issue_id}/issue-subscribers/` | `IssueSubscriberViewSet.list` (V/issue/subscriber.py:67) | `WorkItemSubscriptionEndpoints` → `ListWorkItemSubscribersQuery` | `project.work_item_subscription.read` · `PRJ(A,M,G)` | 200 | DT-WI-04 | I2 | CE-WI-043 |
| EP-0284 | A04:S2 | `POST {P}/issues/{issue_id}/issue-subscribers/` | `IssueSubscriberViewSet.create` (V/issue/subscriber.py) | `WorkItemSubscriptionEndpoints` → `AddWorkItemSubscriberCommand` | `project.work_item_subscription.manage` · `PRJ(A,M)` | 201 | – | I2 | CE-WI-043 |
| EP-0285 | A04:S3 | `DELETE {P}/issues/{issue_id}/issue-subscribers/{subscriber_id}/` | `IssueSubscriberViewSet.destroy` (V/issue/subscriber.py:74) | `WorkItemSubscriptionEndpoints` → `RemoveWorkItemSubscriberCommand` | `project.work_item_subscription.manage` · `PRJ(A,M)` | 204 | – | I2 | CE-WI-043 |
| EP-0286 | A04:S4 | `GET {P}/issues/{issue_id}/subscribe/` | `IssueSubscriberViewSet.subscription_status` (V/issue/subscriber.py:113) | `WorkItemSubscriptionEndpoints` → `GetWorkItemSubscriptionStatusQuery` | `project.work_item_subscription.read` · `PRJ(A,M,G)` | 200 | – | I2 | CE-WI-043 |
| EP-0287 | A04:S5 | `POST {P}/issues/{issue_id}/subscribe/` | `IssueSubscriberViewSet.subscribe` (V/issue/subscriber.py:84) | `WorkItemSubscriptionEndpoints` → `SubscribeWorkItemCommand` | `project.work_item_subscription.subscribe` · `PRJ(A,M,G)` | 201 | – | I2 | CE-WI-043 |
| EP-0288 | A04:S6 | `DELETE {P}/issues/{issue_id}/subscribe/` | `IssueSubscriberViewSet.unsubscribe` (V/issue/subscriber.py:103) | `WorkItemSubscriptionEndpoints` → `UnsubscribeWorkItemCommand` | `project.work_item_subscription.subscribe` · `PRJ(A,M,G)` | 204 | – | I2 | CE-WI-043 |
| EP-0292 | A04:C4 | `PUT {P}/issues/{issue_id}/comments/{pk}/` | `IssueCommentViewSet.update` (V/issue/comment.py) | — (entfällt (SEC-01)) | – | 200→405 | SEC-01, DT-GEN-01 | I2 | CE-WI-037, CE-WI-044 |
| EP-0294 | A04:K9 | `GET {P}/issues/{issue_id}/issue-attachments/{pk}/` | `IssueAttachmentEndpoint.get` (V/issue/attachment.py:91) | — (nicht registriert (DT-WI-10)) | – | 500→405 | DT-WI-10 | I2 | CE-WI-036 |
| EP-0296 | A04:K4 | `PUT {P}/issues/{issue_id}/issue-links/{pk}/` | `IssueLinkViewSet.update` (V/issue/link.py) | — (nicht registriert (DT-GEN-01)) | – | 200→405 | DT-GEN-01 | I2 | CE-WI-035 |
| EP-0297 | A04:I7 | `PUT {P}/issues/{pk}/` | `IssueViewSet.update` (V/issue/base.py) | — (entfällt (SEC-01)) | – | 200→405 | SEC-01, DT-GEN-01 | I2 | CE-WI-003, CE-WI-004, CE-WI-005, CE-WI-020 |

### 4.6 `Plane.Views` – Projekt- und Workspace-Views

Ablage der Endpoint-Klassen: `src/modules/Views/Plane.Views/Endpoints/App/<Klasse>.cs`. 13 Zeilen, davon 11 registriert und 2 nicht registriert (Entscheidung in Spalte „Abw./DT“).

| EP | Original-ID | Methode · Pfad (Original) | Original-View (Datei) | Ziel: Klasse → Handler | Permission · Ziel-Prüfung | Status Orig→Ziel | Abw./DT | Ink. | CE-IDs |
|---|---|---|---|---|---|---|---|---|---|
| EP-0298 | A04:W13 | `GET {W}/issues/` | `WorkspaceViewIssuesViewSet.list` (V/view/base.py:224) | `ViewEndpoints` → `ListWorkspaceViewWorkItemsQuery` | `workspace.view.read` · `WS(A,M,G)+VIS` | 200 | – | I3 | CE-LV-054 |
| EP-0299 | A04:W1 | `GET {P}/views/` | `IssueViewViewSet.list` (V/view/base.py:297) | `ViewEndpoints` → `ListProjectViewsQuery` | `project.view.read` · `PRJ(A,M,G)+VIS` | 200 | – | I3 | CE-LV-047 |
| EP-0300 | A04:W2 | `POST {P}/views/` | `IssueViewViewSet.create` (V/view/base.py) | `ViewEndpoints` → `CreateProjectViewCommand` | `project.view.create` · `PRJ(A,M)` | 201 | SEC-07 | I3 | CE-LV-048, CE-LV-011 |
| EP-0301 | A04:W3 | `GET {P}/views/{pk}/` | `IssueViewViewSet.retrieve` (V/view/base.py:316) | `ViewEndpoints` → `GetProjectViewQuery` | `project.view.read` · `PRJ(A,M,G)+VIS` | 200 | – | I3 | CE-LV-051 |
| EP-0302 | A04:W5 | `PATCH {P}/views/{pk}/` | `IssueViewViewSet.partial_update` (V/view/base.py:351) | `ViewEndpoints` → `UpdateProjectViewCommand` | `project.view.update` · `PRJ(A,M,G)+C:IssueView` | 200 | – | I3 | CE-LV-048, CE-LV-011 |
| EP-0303 | A04:W6 | `DELETE {P}/views/{pk}/` | `IssueViewViewSet.destroy` (V/view/base.py:373) | `ViewEndpoints` → `DeleteProjectViewCommand` | `project.view.delete` · `PRJ(A)+C:IssueView` | 204 | – | I3 | CE-LV-049 |
| EP-0304 | A04:W7 | `GET {W}/views/` | `WorkspaceViewViewSet.list` (V/view/base.py:79) | `ViewEndpoints` → `ListWorkspaceViewsQuery` | `workspace.view.read` · `WS(A,M,G)+VIS` | 200 | – | I3 | CE-LV-052 |
| EP-0305 | A04:W8 | `POST {W}/views/` | `WorkspaceViewViewSet.create` (V/view/base.py) | `ViewEndpoints` → `CreateWorkspaceViewCommand` | `workspace.view.create` · `WS(A,M)` | 201 | SEC-07 | I3 | CE-LV-053, CE-LV-011 |
| EP-0306 | A04:W9 | `GET {W}/views/{pk}/` | `WorkspaceViewViewSet.retrieve` (V/view/base.py:109) | `ViewEndpoints` → `GetWorkspaceViewQuery` | `workspace.view.read` · `WS(A,M,G)+VIS` | 200 | SEC-07 | I3 | CE-LV-052 |
| EP-0307 | A04:W11 | `PATCH {W}/views/{pk}/` | `WorkspaceViewViewSet.partial_update` (V/view/base.py:88) | `ViewEndpoints` → `UpdateWorkspaceViewCommand` | `workspace.view.update` · `WS(A,M,G)+C:IssueView` | 200 | – | I3 | CE-LV-053, CE-LV-011 |
| EP-0308 | A04:W12 | `DELETE {W}/views/{pk}/` | `WorkspaceViewViewSet.destroy` (V/view/base.py:122) | `ViewEndpoints` → `DeleteWorkspaceViewCommand` | `workspace.view.delete` · `WS(A)+C:IssueView` | 204 | – | I3 | CE-LV-053, CE-LV-011 |
| EP-0309 | A04:W4 | `PUT {P}/views/{pk}/` | `IssueViewViewSet.update` (V/view/base.py) | — (entfällt (SEC-01)) | – | 200→405 | SEC-01, DT-GEN-01 | I3 | CE-LV-048, CE-LV-011 |
| EP-0310 | A04:W10 | `PUT {W}/views/{pk}/` | `WorkspaceViewViewSet.update` (V/view/base.py) | — (entfällt (SEC-01)) | – | 200→405 | SEC-01, DT-GEN-01 | I3 | CE-LV-053, CE-LV-011 |

### 4.7 `Plane.Cycles` – Cycles

Ablage der Endpoint-Klassen: `src/modules/Cycles/Plane.Cycles/Endpoints/App/<Klasse>.cs`. 23 Zeilen, davon 17 registriert und 6 nicht registriert (Entscheidung in Spalte „Abw./DT“).

| EP | Original-ID | Methode · Pfad (Original) | Original-View (Datei) | Ziel: Klasse → Handler | Permission · Ziel-Prüfung | Status Orig→Ziel | Abw./DT | Ink. | CE-IDs |
|---|---|---|---|---|---|---|---|---|---|
| EP-0311 | neu: D16-ADR-14 | `GET {W}/active-cycles/` | – (D16-ADR-14) | `CycleEndpoints` → `ListWorkspaceActiveCyclesQuery` | workspace.cycle.read_active | 200 | DT-CYC-02 | I3 | CE-CYC-004 |
| EP-0312 | A04:Y20 | `GET {P}/archived-cycles/` | `CycleArchiveUnarchiveEndpoint.get` (V/cycle/archive.py:272) | `CycleEndpoints` → `ListArchivedCyclesQuery` | `project.cycle.read_archived` · `PRJ(A,M)` | 200 | – | I3 | CE-CYC-012 |
| EP-0313 | A04:Y21 | `GET {P}/archived-cycles/{pk}/` | `CycleArchiveUnarchiveEndpoint.get` (V/cycle/archive.py:272) | `CycleEndpoints` → `GetArchivedCycleQuery` | `project.cycle.read_archived` · `PRJ(A,M)` | 200 | – | I3 | CE-CYC-012 |
| EP-0314 | A04:Y1 | `GET {P}/cycles/` | `CycleViewSet.list` (V/cycle/base.py:185) | `CycleEndpoints` → `ListCyclesQuery` | `project.cycle.read` · `PRJ(A,M,G)` | 200 | – | I3 | CE-CYC-001, CE-CYC-002, CE-CYC-003 |
| EP-0315 | A04:Y2 | `POST {P}/cycles/` | `CycleViewSet.create` (V/cycle/base.py:272) | `CycleEndpoints` → `CreateCycleCommand` | `project.cycle.create` · `PRJ(A,M)` | 201 | – | I3 | CE-CYC-005 |
| EP-0316 | A04:Y11 | `POST {P}/cycles/date-check/` | `CycleDateCheckEndpoint.post` (V/cycle/base.py:523) | `CycleEndpoints` → `CheckCycleDatesQuery` | `project.cycle.create` · `PRJ(A,M)` | 200 | – | I3 | CE-CYC-006 |
| EP-0317 | A04:Y23 | `GET {P}/cycles/{cycle_id}/analytics/` | `CycleAnalyticsEndpoint.get` (V/cycle/base.py:793) | `CycleEndpoints` → `GetCycleAnalyticsQuery` | `project.cycle.read` · `PRJ(A,M,G)` | 200 | – | I3 | CE-CYC-008 |
| EP-0318 | A04:Y18 | `POST {P}/cycles/{cycle_id}/archive/` | `CycleArchiveUnarchiveEndpoint.post` (V/cycle/archive.py:587) | `CycleEndpoints` → `ArchiveCycleCommand` | `project.cycle.archive` · `PRJ(A,M)` | 200 | – | I3 | CE-CYC-012 |
| EP-0319 | A04:Y19 | `DELETE {P}/cycles/{cycle_id}/archive/` | `CycleArchiveUnarchiveEndpoint.delete` (V/cycle/archive.py:607) | `CycleEndpoints` → `UnarchiveCycleCommand` | `project.cycle.unarchive` · `PRJ(A,M)` | 204 | – | I3 | CE-CYC-012 |
| EP-0320 | A04:Y22 | `GET {P}/cycles/{cycle_id}/progress/` | `CycleProgressEndpoint.get` (V/cycle/base.py:665) | `CycleEndpoints` → `GetCycleProgressQuery` | `project.cycle.read` · `PRJ(A,M,G)` | 200 | – | I3 | CE-CYC-008 |
| EP-0321 | A04:Y3 | `GET {P}/cycles/{pk}/` | `CycleViewSet.retrieve` (V/cycle/base.py:412) | `CycleEndpoints` → `GetCycleQuery` | `project.cycle.read_detail` · `PRJ(A,M)` | 200 | – | I3 | CE-CYC-007, CE-CYC-009 |
| EP-0322 | A04:Y5 | `PATCH {P}/cycles/{pk}/` | `CycleViewSet.partial_update` (V/cycle/base.py:337) | `CycleEndpoints` → `UpdateCycleCommand` | `project.cycle.update` · `PRJ(A,M)` | 200 | DT-CYC-01 | I3 | CE-CYC-005 |
| EP-0323 | A04:Y6 | `DELETE {P}/cycles/{pk}/` | `CycleViewSet.destroy` (V/cycle/base.py:479) | `CycleEndpoints` → `DeleteCycleCommand` | `project.cycle.delete` · `PRJ(A)+C:Cycle` | 204 | – | I3 | CE-CYC-013 |
| EP-0324 | A04:Y7 | `GET {P}/cycles/{cycle_id}/cycle-issues/` | `CycleIssueViewSet.list` (V/cycle/issue.py:110) | `CycleWorkItemEndpoints` → `ListCycleWorkItemsQuery` | `project.cycle_work_item.read` · `PRJ(A,M)` | 200 | – | I3 | CE-CYC-010 |
| EP-0325 | A04:Y8 | `POST {P}/cycles/{cycle_id}/cycle-issues/` | `CycleIssueViewSet.create` (V/cycle/issue.py:224) | `CycleWorkItemEndpoints` → `AddCycleWorkItemsCommand` | `project.cycle_work_item.create` · `PRJ(A,M)` | 201 | – | I3 | CE-CYC-010 |
| EP-0326 | A04:Y10 | `DELETE {P}/cycles/{cycle_id}/cycle-issues/{issue_id}/` | `CycleIssueViewSet.destroy` (V/cycle/issue.py:320) | `CycleWorkItemEndpoints` → `RemoveCycleWorkItemCommand` | `project.cycle_work_item.delete` · `PRJ(A,M)` | 204 | – | I3 | CE-CYC-010 |
| EP-0327 | A04:Y15 | `POST {P}/cycles/{cycle_id}/transfer-issues/` | `TransferCycleIssueEndpoint.post` (V/cycle/base.py:601) | `CycleWorkItemEndpoints` → `TransferCycleWorkItemsCommand` | `project.cycle_work_item.transfer` · `PRJ(A,M)` | 200 | – | I3 | CE-CYC-011 |
| EP-0330 | A04:Y24 | `POST {P}/archived-cycles/{pk}/` | `CycleArchiveUnarchiveEndpoint.post` (V/cycle/archive.py:587) | — (nicht registriert (DT-GEN-03)) | – | 500→405 | DT-GEN-03 | I3 | CE-CYC-012 |
| EP-0331 | A04:Y24 | `DELETE {P}/archived-cycles/{pk}/` | `CycleArchiveUnarchiveEndpoint.delete` (V/cycle/archive.py:607) | — (nicht registriert (DT-GEN-03)) | – | 500→405 | DT-GEN-03 | I3 | CE-CYC-012 |
| EP-0333 | A04:Y9 | `GET {P}/cycles/{cycle_id}/cycle-issues/{issue_id}/` | `CycleIssueViewSet.retrieve` (V/cycle/issue.py) | — (entfällt (SEC-02)) | – | 500→405 | SEC-02, DT-GEN-02 | I3 | CE-CYC-010 |
| EP-0334 | A04:Y9 | `PATCH {P}/cycles/{cycle_id}/cycle-issues/{issue_id}/` | `CycleIssueViewSet.partial_update` (V/cycle/issue.py) | — (entfällt (SEC-02)) | – | 500→405 | SEC-02, DT-GEN-02 | I3 | CE-CYC-010 |
| EP-0335 | A04:Y9 | `PUT {P}/cycles/{cycle_id}/cycle-issues/{issue_id}/` | `CycleIssueViewSet.update` (V/cycle/issue.py) | — (entfällt (SEC-02)) | – | 500→405 | SEC-02, DT-GEN-02 | I3 | CE-CYC-010 |
| EP-0336 | A04:Y4 | `PUT {P}/cycles/{pk}/` | `CycleViewSet.update` (V/cycle/base.py) | — (entfällt (SEC-01)) | – | 200→405 | SEC-01, DT-GEN-01 | I3 | CE-CYC-005 |

### 4.8 `Plane.ProjectModules` – Modules (Fachobjekt)

Ablage der Endpoint-Klassen: `src/modules/ProjectModules/Plane.ProjectModules/Endpoints/App/<Klasse>.cs`. 23 Zeilen, davon 18 registriert und 5 nicht registriert (Entscheidung in Spalte „Abw./DT“).

| EP | Original-ID | Methode · Pfad (Original) | Original-View (Datei) | Ziel: Klasse → Handler | Permission · Ziel-Prüfung | Status Orig→Ziel | Abw./DT | Ink. | CE-IDs |
|---|---|---|---|---|---|---|---|---|---|
| EP-0337 | A04:M22 | `GET {P}/archived-modules/` | `ModuleArchiveUnarchiveEndpoint.get` (V/module/archive.py:258) | `ModuleEndpoints` → `ListArchivedModulesQuery` | `project.module.read_archived` · `PRJ(A,M,G)` | 200 | – | I3 | CE-MOD-009 |
| EP-0338 | A04:M23 | `GET {P}/archived-modules/{pk}/` | `ModuleArchiveUnarchiveEndpoint.get` (V/module/archive.py:258) | `ModuleEndpoints` → `GetArchivedModuleQuery` | `project.module.read_archived` · `PRJ(A,M,G)` | 200 | – | I3 | CE-MOD-009 |
| EP-0339 | A04:M1 | `GET {P}/modules/` | `ModuleViewSet.list` (V/module/base.py:355) | `ModuleEndpoints` → `ListModulesQuery` | `project.module.read` · `PRJ(A,M,G)` | 200 | – | I3 | CE-MOD-001, CE-MOD-002 |
| EP-0340 | A04:M2 | `POST {P}/modules/` | `ModuleViewSet.create` (V/module/base.py:296) | `ModuleEndpoints` → `CreateModuleCommand` | `project.module.create` · `PRJ(A,M)` | 201 | – | I3 | CE-MOD-003 |
| EP-0341 | A04:M20 | `POST {P}/modules/{module_id}/archive/` | `ModuleArchiveUnarchiveEndpoint.post` (V/module/archive.py:544) | `ModuleEndpoints` → `ArchiveModuleCommand` | `project.module.archive` · `PRJ(A,M)` | 200 | – | I3 | CE-MOD-009 |
| EP-0342 | A04:M21 | `DELETE {P}/modules/{module_id}/archive/` | `ModuleArchiveUnarchiveEndpoint.delete` (V/module/archive.py:561) | `ModuleEndpoints` → `UnarchiveModuleCommand` | `project.module.unarchive` · `PRJ(A,M)` | 204 | – | I3 | CE-MOD-009 |
| EP-0343 | A04:M3 | `GET {P}/modules/{pk}/` | `ModuleViewSet.retrieve` (V/module/base.py:397) | `ModuleEndpoints` → `GetModuleQuery` | `project.module.read_detail` · `PRJ(A,M)` | 200 | – | I3 | CE-MOD-006, CE-MOD-007 |
| EP-0344 | A04:M5 | `PATCH {P}/modules/{pk}/` | `ModuleViewSet.partial_update` (V/module/base.py:653) | `ModuleEndpoints` → `UpdateModuleCommand` | `project.module.update` · `PRJ(A,M)` | 200 | – | I3 | CE-MOD-003, CE-MOD-004 |
| EP-0345 | A04:M6 | `DELETE {P}/modules/{pk}/` | `ModuleViewSet.destroy` (V/module/base.py:725) | `ModuleEndpoints` → `DeleteModuleCommand` | `project.module.delete` · `PRJ(A)+C:Module` | 204 | – | I3 | CE-MOD-010 |
| EP-0346 | A04:M12 | `GET {P}/modules/{module_id}/module-links/` | `ModuleLinkViewSet.list` (V/module/base.py) | `ModuleLinkEndpoints` → `ListModuleLinksQuery` | `project.module_link.read` · `PRJ(A,M,G)` | 200 | – | I3 | CE-MOD-005 |
| EP-0347 | A04:M13 | `POST {P}/modules/{module_id}/module-links/` | `ModuleLinkViewSet.create` (V/module/base.py) | `ModuleLinkEndpoints` → `CreateModuleLinkCommand` | `project.module_link.create` · `PRJ(A,M)` | 201 | – | I3 | CE-MOD-005 |
| EP-0348 | A04:M14 | `GET {P}/modules/{module_id}/module-links/{pk}/` | `ModuleLinkViewSet.retrieve` (V/module/base.py) | `ModuleLinkEndpoints` → `GetModuleLinkQuery` | `project.module_link.read` · `PRJ(A,M,G)` | 200 | – | I3 | CE-MOD-005 |
| EP-0349 | A04:M14 | `PATCH {P}/modules/{module_id}/module-links/{pk}/` | `ModuleLinkViewSet.partial_update` (V/module/base.py) | `ModuleLinkEndpoints` → `UpdateModuleLinkCommand` | `project.module_link.update` · `PRJ(A,M)` | 200 | – | I3 | CE-MOD-005 |
| EP-0350 | A04:M14 | `DELETE {P}/modules/{module_id}/module-links/{pk}/` | `ModuleLinkViewSet.destroy` (V/module/base.py) | `ModuleLinkEndpoints` → `DeleteModuleLinkCommand` | `project.module_link.delete` · `PRJ(A,M)` | 200 | – | I3 | CE-MOD-005 |
| EP-0351 | A04:M7 | `POST {P}/issues/{issue_id}/modules/` | `ModuleIssueViewSet.create_issue_modules` (V/module/issue.py:261) | `ModuleWorkItemEndpoints` → `SetWorkItemModulesCommand` | `project.module_work_item.create` · `PRJ(A,M)` | 201 | – | I3 | CE-MOD-008, CE-WI-026 |
| EP-0352 | A04:M8 | `GET {P}/modules/{module_id}/issues/` | `ModuleIssueViewSet.list` (V/module/issue.py:97) | `ModuleWorkItemEndpoints` → `ListModuleWorkItemsQuery` | `project.module_work_item.read` · `PRJ(A,M)` | 200 | – | I3 | CE-MOD-008 |
| EP-0353 | A04:M9 | `POST {P}/modules/{module_id}/issues/` | `ModuleIssueViewSet.create_module_issues` (V/module/issue.py:212) | `ModuleWorkItemEndpoints` → `AddModuleWorkItemsCommand` | `project.module_work_item.create` · `PRJ(A,M)` | 201 | – | I3 | CE-MOD-008 |
| EP-0354 | A04:M11 | `DELETE {P}/modules/{module_id}/issues/{issue_id}/` | `ModuleIssueViewSet.destroy` (V/module/issue.py:338) | `ModuleWorkItemEndpoints` → `RemoveModuleWorkItemCommand` | `project.module_work_item.delete` · `PRJ(A,M)` | 204 | – | I3 | CE-MOD-008 |
| EP-0360 | A04:M10 | `GET {P}/modules/{module_id}/issues/{issue_id}/` | `ModuleIssueViewSet.retrieve` (V/module/issue.py) | — (entfällt (SEC-02)) | – | 500→405 | SEC-02, DT-GEN-02 | I3 | CE-MOD-008 |
| EP-0361 | A04:M10 | `PATCH {P}/modules/{module_id}/issues/{issue_id}/` | `ModuleIssueViewSet.partial_update` (V/module/issue.py) | — (entfällt (SEC-02)) | – | 500→405 | SEC-02, DT-GEN-02 | I3 | CE-MOD-008 |
| EP-0362 | A04:M10 | `PUT {P}/modules/{module_id}/issues/{issue_id}/` | `ModuleIssueViewSet.update` (V/module/issue.py) | — (entfällt (SEC-02)) | – | 500→405 | SEC-02, DT-GEN-02 | I3 | CE-MOD-008 |
| EP-0363 | A04:M14 | `PUT {P}/modules/{module_id}/module-links/{pk}/` | `ModuleLinkViewSet.update` (V/module/base.py) | — (nicht registriert (DT-GEN-01)) | – | 200→405 | DT-GEN-01 | I3 | CE-MOD-005 |
| EP-0364 | A04:M4 | `PUT {P}/modules/{pk}/` | `ModuleViewSet.update` (V/module/base.py) | — (entfällt (SEC-01)) | – | 200→405 | SEC-01, DT-GEN-01 | I3 | CE-MOD-003, CE-MOD-004 |

### 4.9 `Plane.Intake` – Intake (App und öffentliche Einreichung)

Ablage der Endpoint-Klassen: `src/modules/Intake/Plane.Intake/Endpoints/{App,Space}/<Klasse>.cs`. 29 Zeilen, davon 27 registriert und 2 nicht registriert (Entscheidung in Spalte „Abw./DT“).

| EP | Original-ID | Methode · Pfad (Original) | Original-View (Datei) | Ziel: Klasse → Handler | Permission · Ziel-Prüfung | Status Orig→Ziel | Abw./DT | Ink. | CE-IDs |
|---|---|---|---|---|---|---|---|---|---|
| EP-0365 | A04:N1 | `GET {P}/inboxes/` | `IntakeViewSet.list` (V/intake/base.py:75) | `IntakeEndpoints` → `ListIntakesQuery` | `project.intake.read` · `PRJ(A,M)` | 200 | – | I3 | CE-INT-001 |
| EP-0366 | A04:N3 | `GET {P}/inboxes/{pk}/` | `IntakeViewSet.retrieve` (V/intake/base.py) | `IntakeEndpoints` → `GetIntakeQuery` | `project.intake.read` · `PRJ(A,M)` | 200 | SEC-03, DT-INT-02 | I3 | CE-INT-001 |
| EP-0367 | A04:N4 | `PATCH {P}/inboxes/{pk}/` | `IntakeViewSet.partial_update` (V/intake/base.py) | `IntakeEndpoints` → `UpdateIntakeCommand` | `project.intake.update` · `PRJ(A)` | 200 | SEC-03, DT-INT-02 | I3 | CE-INT-001 |
| EP-0368 | A04:N5 | `DELETE {P}/inboxes/{pk}/` | `IntakeViewSet.destroy` (V/intake/base.py:84) | `IntakeEndpoints` → `DeleteIntakeCommand` | `project.intake.delete` · `PRJ(A,M)` | 204 | – | I3 | CE-INT-001 |
| EP-0369 | A04:N1 | `GET {P}/intakes/` | `IntakeViewSet.list` (V/intake/base.py:75) | `IntakeEndpoints` → `ListIntakesQuery` | `project.intake.read` · `PRJ(A,M)` | 200 | – | I3 | CE-INT-001 |
| EP-0370 | A04:N3 | `GET {P}/intakes/{pk}/` | `IntakeViewSet.retrieve` (V/intake/base.py) | `IntakeEndpoints` → `GetIntakeQuery` | `project.intake.read` · `PRJ(A,M)` | 200 | SEC-03, DT-INT-02 | I3 | CE-INT-001 |
| EP-0371 | A04:N4 | `PATCH {P}/intakes/{pk}/` | `IntakeViewSet.partial_update` (V/intake/base.py) | `IntakeEndpoints` → `UpdateIntakeCommand` | `project.intake.update` · `PRJ(A)` | 200 | SEC-03, DT-INT-02 | I3 | CE-INT-001 |
| EP-0372 | A04:N5 | `DELETE {P}/intakes/{pk}/` | `IntakeViewSet.destroy` (V/intake/base.py:84) | `IntakeEndpoints` → `DeleteIntakeCommand` | `project.intake.delete` · `PRJ(A,M)` | 204 | – | I3 | CE-INT-001 |
| EP-0373 | A04:N6 | `GET {P}/inbox-issues/` | `IntakeIssueViewSet.list` (V/intake/base.py:179) | `IntakeWorkItemEndpoints` → `ListIntakeWorkItemsQuery` | `project.intake_work_item.read` · `PRJ(A,M,G)+VIS` | 200 | – | I3 | CE-INT-002, CE-INT-003 |
| EP-0374 | A04:N7 | `POST {P}/inbox-issues/` | `IntakeIssueViewSet.create` (V/intake/base.py:230) | `IntakeWorkItemEndpoints` → `CreateIntakeWorkItemCommand` | `project.intake_work_item.create` · `PRJ(A,M,G)` | 200 | – | I3 | CE-INT-005 |
| EP-0375 | A04:N8 | `GET {P}/inbox-issues/{pk}/` | `IntakeIssueViewSet.retrieve` (V/intake/base.py:508) | `IntakeWorkItemEndpoints` → `GetIntakeWorkItemQuery` | `project.intake_work_item.read` · `PRJ(A,M,G)+C:Issue+VIS` | 200 | – | I3 | CE-INT-004, CE-INT-012 |
| EP-0376 | A04:N9 | `PATCH {P}/inbox-issues/{pk}/` | `IntakeIssueViewSet.partial_update` (V/intake/base.py:336) | `IntakeWorkItemEndpoints` → `UpdateIntakeWorkItemCommand` | `project.intake_work_item.update` · `PRJ(A)+C:Issue` | 200 | – | I3 | CE-INT-006, CE-INT-007, CE-INT-008, CE-INT-009, CE-INT-010 |
| EP-0377 | A04:N10 | `DELETE {P}/inbox-issues/{pk}/` | `IntakeIssueViewSet.destroy` (V/intake/base.py:555) | `IntakeWorkItemEndpoints` → `DeleteIntakeWorkItemCommand` | `project.intake_work_item.delete` · `PRJ(A)+C:Issue` | 204 | – | I3 | CE-INT-010 |
| EP-0378 | A04:N6 | `GET {P}/intake-issues/` | `IntakeIssueViewSet.list` (V/intake/base.py:179) | `IntakeWorkItemEndpoints` → `ListIntakeWorkItemsQuery` | `project.intake_work_item.read` · `PRJ(A,M,G)+VIS` | 200 | – | I3 | CE-INT-002, CE-INT-003 |
| EP-0379 | A04:N7 | `POST {P}/intake-issues/` | `IntakeIssueViewSet.create` (V/intake/base.py:230) | `IntakeWorkItemEndpoints` → `CreateIntakeWorkItemCommand` | `project.intake_work_item.create` · `PRJ(A,M,G)` | 200 | – | I3 | CE-INT-005 |
| EP-0380 | A04:N8 | `GET {P}/intake-issues/{pk}/` | `IntakeIssueViewSet.retrieve` (V/intake/base.py:508) | `IntakeWorkItemEndpoints` → `GetIntakeWorkItemQuery` | `project.intake_work_item.read` · `PRJ(A,M,G)+C:Issue+VIS` | 200 | – | I3 | CE-INT-004, CE-INT-012 |
| EP-0381 | A04:N9 | `PATCH {P}/intake-issues/{pk}/` | `IntakeIssueViewSet.partial_update` (V/intake/base.py:336) | `IntakeWorkItemEndpoints` → `UpdateIntakeWorkItemCommand` | `project.intake_work_item.update` · `PRJ(A)+C:Issue` | 200 | – | I3 | CE-INT-006, CE-INT-007, CE-INT-008, CE-INT-009, CE-INT-010 |
| EP-0382 | A04:N10 | `DELETE {P}/intake-issues/{pk}/` | `IntakeIssueViewSet.destroy` (V/intake/base.py:555) | `IntakeWorkItemEndpoints` → `DeleteIntakeWorkItemCommand` | `project.intake_work_item.delete` · `PRJ(A)+C:Issue` | 204 | – | I3 | CE-INT-010 |
| EP-0383 | A04:N11 | `GET {P}/intake-work-items/{work_item_id}/description-versions/` | `IntakeWorkItemDescriptionVersionEndpoint.get` (V/intake/base.py:584) | `IntakeWorkItemEndpoints` → `ListIntakeDescriptionVersionsQuery` | `project.intake_work_item.read` · `PRJ(A,M,G)+VIS` | 200 | – | I3 | CE-INT-004, CE-WI-041 |
| EP-0384 | A04:N12 | `GET {P}/intake-work-items/{work_item_id}/description-versions/{pk}/` | `IntakeWorkItemDescriptionVersionEndpoint.get` (V/intake/base.py:584) | `IntakeWorkItemEndpoints` → `GetIntakeDescriptionVersionQuery` | `project.intake_work_item.read` · `PRJ(A,M,G)+VIS` | 200 | – | I3 | CE-INT-004, CE-WI-041 |
| EP-0385 | A04:N2 | `POST {P}/inboxes/` | `IntakeViewSet.create` (V/intake/base.py) | — (nicht registriert (DT-INT-01)) | – | 400→405 | SEC-03, DT-INT-01 | I3 | CE-INT-001 |
| EP-0386 | A04:N2 | `POST {P}/intakes/` | `IntakeViewSet.create` (V/intake/base.py) | — (nicht registriert (DT-INT-01)) | – | 400→405 | SEC-03, DT-INT-01 | I3 | CE-INT-001 |
| EP-0387 | A05:S-26 | `GET {SP}/intakes/{intake_id}/inbox-issues/` | `IntakeIssuePublicViewSet.list` (SPV/intake.py:57) | `PublicIntakeEndpoints` → `ListPublicIntakeWorkItemsQuery` | `public.intake.read` · `AUTH+BOARD+OWN` | 200 | SEC-18, DT-INT-06 | I6 | CE-SPACE-006 |
| EP-0388 | A05:S-27 | `POST {SP}/intakes/{intake_id}/inbox-issues/` | `IntakeIssuePublicViewSet.create` (SPV/intake.py:108) | `PublicIntakeEndpoints` → `CreatePublicIntakeWorkItemCommand` | `public.intake.create` · `AUTH+BOARD` | 200 | DT-INT-05 | I6 | CE-SPACE-006 |
| EP-0389 | A05:S-26 | `GET {SP}/intakes/{intake_id}/intake-issues/` | `IntakeIssuePublicViewSet.list` (SPV/intake.py:57) | `PublicIntakeEndpoints` → `ListPublicIntakeWorkItemsQuery` | `public.intake.read` · `AUTH+BOARD+OWN` | 200 | SEC-18, DT-INT-06 | I6 | CE-SPACE-006 |
| EP-0390 | A05:S-27 | `POST {SP}/intakes/{intake_id}/intake-issues/` | `IntakeIssuePublicViewSet.create` (SPV/intake.py:108) | `PublicIntakeEndpoints` → `CreatePublicIntakeWorkItemCommand` | `public.intake.create` · `AUTH+BOARD` | 200 | DT-INT-05 | I6 | CE-SPACE-006 |
| EP-0391 | A05:S-28 | `GET {SP}/intakes/{intake_id}/intake-issues/{pk}/` | `IntakeIssuePublicViewSet.retrieve` (SPV/intake.py:250) | `PublicIntakeEndpoints` → `GetPublicIntakeWorkItemQuery` | `public.intake.read` · `AUTH+BOARD+OWN` | 200 | SEC-18, DT-INT-06 | I6 | CE-SPACE-006 |
| EP-0392 | A05:S-29 | `PATCH {SP}/intakes/{intake_id}/intake-issues/{pk}/` | `IntakeIssuePublicViewSet.partial_update` (SPV/intake.py:189) | `PublicIntakeEndpoints` → `UpdatePublicIntakeWorkItemCommand` | `public.intake.update` · `AUTH+BOARD` | 200 | – | I6 | CE-SPACE-006 |
| EP-0393 | A05:S-30 | `DELETE {SP}/intakes/{intake_id}/intake-issues/{pk}/` | `IntakeIssuePublicViewSet.destroy` (SPV/intake.py:272) | `PublicIntakeEndpoints` → `DeletePublicIntakeWorkItemCommand` | `public.intake.delete` · `AUTH+BOARD` | 204 | – | I6 | CE-SPACE-006 |

### 4.10 `Plane.Pages` – Pages

Ablage der Endpoint-Klassen: `src/modules/Pages/Plane.Pages/Endpoints/App/<Klasse>.cs`. 16 Zeilen, davon 16 registriert und 0 nicht registriert (Entscheidung in Spalte „Abw./DT“).

| EP | Original-ID | Methode · Pfad (Original) | Original-View (Datei) | Ziel: Klasse → Handler | Permission · Ziel-Prüfung | Status Orig→Ziel | Abw./DT | Ink. | CE-IDs |
|---|---|---|---|---|---|---|---|---|---|
| EP-0394 | A04:G1 | `GET {P}/pages-summary/` | `PageViewSet.summary` (V/page/base.py:416) | `PageEndpoints` → `GetPagesSummaryQuery` | `project.page.read` · `PRJ(A,M,G)+PAGE+VIS` | 200 | – | I4 | CE-PAGE-001 |
| EP-0395 | A04:G2 | `GET {P}/pages/` | `PageViewSet.list` (V/page/base.py:286) | `PageEndpoints` → `ListPagesQuery` | `project.page.read` · `PRJ(A,M,G)+PAGE+VIS` | 200 | – | I4 | CE-PAGE-001, CE-PAGE-002 |
| EP-0396 | A04:G3 | `POST {P}/pages/` | `PageViewSet.create` (V/page/base.py:145) | `PageEndpoints` → `CreatePageCommand` | `project.page.create` · `PRJ(A,M)+PAGE` | 201 | DT-PAGE-05, DT-PAGE-07 | I4 | CE-PAGE-003, CE-PAGE-012 |
| EP-0397 | A04:G4 | `GET {P}/pages/{page_id}/` | `PageViewSet.retrieve` (V/page/base.py:218) | `PageEndpoints` → `GetPageQuery` | `project.page.read` · `PRJ(A,M,G)+PAGE+VIS` | 200 | – | I4 | CE-PAGE-004 |
| EP-0398 | A04:G5 | `PATCH {P}/pages/{page_id}/` | `PageViewSet.partial_update` (V/page/base.py:170) | `PageEndpoints` → `UpdatePageCommand` | `project.page.update` · `PRJ(A,M)+PAGE` | 200 | DT-PAGE-04, DT-PAGE-05 | I4 | CE-PAGE-004, CE-RT-005 |
| EP-0399 | A04:G6 | `DELETE {P}/pages/{page_id}/` | `PageViewSet.destroy` (V/page/base.py:363) | `PageEndpoints` → `DeletePageCommand` | `project.page.delete` · `PRJ(A)+PAGE` | 204 | – | I4 | CE-PAGE-008 |
| EP-0400 | A04:G13 | `POST {P}/pages/{page_id}/access/` | `PageViewSet.access` (V/page/base.py:266) | `PageEndpoints` → `ChangePageAccessCommand` | `project.page.change_access` · `PRJ(A,M)+PAGE` | 204 | – | I4 | CE-PAGE-006 |
| EP-0401 | A04:G9 | `POST {P}/pages/{page_id}/archive/` | `PageViewSet.archive` (V/page/base.py:303) | `PageEndpoints` → `ArchivePageCommand` | `project.page.archive` · `PRJ(A,M)+PAGE` | 200 | DT-PAGE-03 | I4 | CE-PAGE-007 |
| EP-0402 | A04:G10 | `DELETE {P}/pages/{page_id}/archive/` | `PageViewSet.unarchive` (V/page/base.py:334) | `PageEndpoints` → `UnarchivePageCommand` | `project.page.unarchive` · `PRJ(A)+PAGE` | 204 | DT-PAGE-03 | I4 | CE-PAGE-007 |
| EP-0403 | A04:G14 | `GET {P}/pages/{page_id}/description/` | `PagesDescriptionViewSet.retrieve` (V/page/base.py:498) | `PageEndpoints` → `GetPageDescriptionBinaryQuery` | `project.page.read` · `PRJ(A,M,G)+PAGE+VIS` | 200 | – | I4 | CE-RT-003, CE-RT-005, CE-PAGE-012 |
| EP-0404 | A04:G15 | `PATCH {P}/pages/{page_id}/description/` | `PagesDescriptionViewSet.partial_update` (V/page/base.py:518) | `PageEndpoints` → `UpdatePageDescriptionCommand` | `project.page.update` · `PRJ(A,M)+PAGE` | 200 | DT-PAGE-01 | I4 | CE-RT-003, CE-RT-005, CE-PAGE-012 |
| EP-0405 | A04:G18 | `POST {P}/pages/{page_id}/duplicate/` | `PageDuplicateEndpoint.post` (V/page/base.py:578) | `PageEndpoints` → `DuplicatePageCommand` | `project.page.create` · `PRJ(A,M)+PAGE` | 201 | DT-PAGE-02 | I4 | CE-PAGE-009 |
| EP-0406 | A04:G11 | `POST {P}/pages/{page_id}/lock/` | `PageViewSet.lock` (V/page/base.py:241) | `PageEndpoints` → `LockPageCommand` | `project.page.lock` · `PRJ(A,M)+PAGE` | 204 | – | I4 | CE-PAGE-005 |
| EP-0407 | A04:G12 | `DELETE {P}/pages/{page_id}/lock/` | `PageViewSet.unlock` (V/page/base.py:253) | `PageEndpoints` → `UnlockPageCommand` | `project.page.unlock` · `PRJ(A)+PAGE` | 204 | – | I4 | CE-PAGE-005 |
| EP-0408 | A04:G16 | `GET {P}/pages/{page_id}/versions/` | `PageVersionEndpoint.get` (V/page/version.py:19) | `PageVersionEndpoints` → `ListPageVersionsQuery` | `project.page_version.read` · `PRJ(A,M,G)+PAGE` | 200 | DT-PAGE-01 | I4 | CE-PAGE-019 |
| EP-0409 | A04:G17 | `GET {P}/pages/{page_id}/versions/{pk}/` | `PageVersionEndpoint.get` (V/page/version.py:19) | `PageVersionEndpoints` → `GetPageVersionQuery` | `project.page_version.read` · `PRJ(A,M,G)+PAGE` | 200 | DT-PAGE-01 | I4 | CE-PAGE-019 |

### 4.11 `Plane.Collaboration` – Live-Endpunkte `/live/` (Host `Plane.Realtime`)

Ablage der Endpoint-Klassen: `src/modules/Collaboration/Plane.Collaboration/Endpoints/Live/<Klasse>.cs`. 4 Zeilen, davon 3 registriert und 1 nicht registriert (Entscheidung in Spalte „Abw./DT“).

| EP | Original-ID | Methode · Pfad (Original) | Original-View (Datei) | Ziel: Klasse → Handler | Permission · Ziel-Prüfung | Status Orig→Ziel | Abw./DT | Ink. | CE-IDs |
|---|---|---|---|---|---|---|---|---|---|
| EP-0410 | A12:§2.26.2-WS | `GET /live/collaboration` | `collaboration.controller.ts` (WebSocket-Upgrade, Hocuspocus) | `CollaborationEndpoint` → `Upgrade` | project.page.read (+PAGE) | 101 | DT-RT-01 | I4 | CE-RT-001, CE-RT-002, CE-RT-004, CE-RT-005, CE-RT-006, CE-RT-007 |
| EP-0411 | A12:§2.26.2-CONV | `POST /live/convert-document/` | `document.controller.ts` | — (nur Management-Port 8081 (SEC-39, D07-ADR-19), über Gateway 404) | – | 200→404 | DT-RT-02 | I4 | CE-RT-008 |
| EP-0412 | A12:§2.26.2-PDF | `POST /live/pdf-export/` | `pdf-export.controller.ts` | `PdfExportEndpoint` → `Post` | project.page.read | 200 | DT-RT-03 | I4 | CE-PAGE-011 |
| EP-0413 | A12:§2.26.2-HEALTH | `GET /live/health/` | `health.controller.ts` | `RealtimeHealthEndpoint` → `Get` | (anonym) | 200 | – | I0 | CE-RT-009 |

### 4.12 `Plane.RealtimeEvents` – Live-Events-Hub (🧱 H6, Host `Plane.Realtime`)

Ablage der Endpoint-Klassen: `src/modules/RealtimeEvents/Plane.RealtimeEvents/Hubs/<Klasse>.cs`. 1 Zeilen, davon 1 registriert und 0 nicht registriert (Entscheidung in Spalte „Abw./DT“).

| EP | Original-ID | Methode · Pfad (Original) | Original-View (Datei) | Ziel: Klasse → Handler | Permission · Ziel-Prüfung | Status Orig→Ziel | Abw./DT | Ink. | CE-IDs |
|---|---|---|---|---|---|---|---|---|---|
| EP-0414 | neu: H6 / ADR-023 | `GET /live/events/` | – (H6 / ADR-023) | `LiveEventsHub` → `LiveEventsHub (SignalR, nur WebSockets)` | (Session-Cookie) | 101 | – | I0 | CE-NOTIF-004 |

### 4.13 `Plane.Assets` – Datei-Assets (App, Space, Auslieferung)

Ablage der Endpoint-Klassen: `src/modules/Assets/Plane.Assets/Endpoints/{App,Space}/<Klasse>.cs`. 33 Zeilen, davon 26 registriert und 7 nicht registriert (Entscheidung in Spalte „Abw./DT“).

| EP | Original-ID | Methode · Pfad (Original) | Original-View (Datei) | Ziel: Klasse → Handler | Permission · Ziel-Prüfung | Status Orig→Ziel | Abw./DT | Ink. | CE-IDs |
|---|---|---|---|---|---|---|---|---|---|
| EP-0415 | neu: ADR-026 | `GET {AV2}/files/{token}/` | – (ADR-026) | `AssetDeliveryEndpoints` → `GetFileSystemAssetQuery` | (HMAC-Download-Token) | 200 | DT-AST-03 | I1 | CE-OPS-012 |
| EP-0416 | A03:A-16 | `GET {AV2}/static/{asset_id}/` | `StaticFileAssetEndpoint.get` (V/asset/v2.py:546) | `AssetDeliveryEndpoints` → `GetStaticAssetRedirectQuery` | `user.asset.read_static` · `ANON` | 302 | – | I1 | CE-OPS-012 |
| EP-0417 | neu: ADR-026 | `POST {AV2}/upload/{token}/` | – (ADR-026) | `AssetDeliveryEndpoints` → `ProxyUploadAssetCommand` | (HMAC-Upload-Token) | 204 | DT-AST-03 | I1 | CE-OPS-012 |
| EP-0418 | A03:A-17 | `POST {AV2}/workspaces/{slug}/projects/{project_id}/` | `ProjectAssetEndpoint.post` (V/asset/v2.py:633) | `ProjectAssetEndpoints` → `CreateProjectAssetUploadCommand` | `project.asset.create` · `PRJ(A,M,G)` | 200 | – | I2 | CE-PAGE-032, CE-OPS-012, CE-OPS-013 |
| EP-0419 | A03:A-25 | `GET {AV2}/workspaces/{slug}/projects/{project_id}/download/{asset_id}/` | `ProjectAssetDownloadEndpoint.get` (V/asset/v2.py:968) | `ProjectAssetEndpoints` → `GetProjectAssetDownloadQuery` | `project.asset.read` · `PRJ(A,M,G)` | 302 | – | I2 | CE-OPS-012 |
| EP-0420 | A03:A-21 | `POST {AV2}/workspaces/{slug}/projects/{project_id}/{entity_id}/bulk/` | `ProjectBulkAssetEndpoint.post` (V/asset/v2.py:767) | `ProjectAssetEndpoints` → `BulkConfirmProjectAssetsCommand` | `project.asset.create` · `PRJ(A,M,G)` | 204 | – | I2 | CE-PAGE-032, CE-OPS-012, CE-OPS-013 |
| EP-0421 | A03:A-20 | `GET {AV2}/workspaces/{slug}/projects/{project_id}/{pk}/` | `ProjectAssetEndpoint.get` (V/asset/v2.py:737) | `ProjectAssetEndpoints` → `GetProjectAssetRedirectQuery` | `project.asset.read` · `PRJ(A,M,G)` | 302 | – | I2 | CE-PAGE-032, CE-OPS-012, CE-OPS-013 |
| EP-0422 | A03:A-18 | `PATCH {AV2}/workspaces/{slug}/projects/{project_id}/{pk}/` | `ProjectAssetEndpoint.patch` (V/asset/v2.py:700) | `ProjectAssetEndpoints` → `ConfirmProjectAssetUploadCommand` | `project.asset.update` · `PRJ(A,M,G)` | 204 | – | I2 | CE-PAGE-032, CE-OPS-012, CE-OPS-013 |
| EP-0423 | A03:A-19 | `DELETE {AV2}/workspaces/{slug}/projects/{project_id}/{pk}/` | `ProjectAssetEndpoint.delete` (V/asset/v2.py:721) | `ProjectAssetEndpoints` → `DeleteProjectAssetCommand` | `project.asset.delete` · `PRJ(A,M,G)` | 204 | – | I2 | CE-PAGE-032, CE-OPS-012, CE-OPS-013 |
| EP-0424 | A03:A-12 | `POST {AV2}/user-assets/` | `UserAssetsV2Endpoint.post` (V/asset/v2.py:151) | `UserAssetEndpoints` → `CreateUserAssetUploadCommand` | `user.user_asset.create` · `AUTH+SELF` | 200 | – | I1 | CE-PROF-003, CE-OPS-013 |
| EP-0425 | A03:A-13 | `PATCH {AV2}/user-assets/{asset_id}/` | `UserAssetsV2Endpoint.patch` (V/asset/v2.py:212) | `UserAssetEndpoints` → `ConfirmUserAssetUploadCommand` | `user.user_asset.update` · `AUTH+SELF` | 204 | – | I1 | CE-PROF-003, CE-OPS-013 |
| EP-0426 | A03:A-14 | `DELETE {AV2}/user-assets/{asset_id}/` | `UserAssetsV2Endpoint.delete` (V/asset/v2.py:233) | `UserAssetEndpoints` → `DeleteUserAssetCommand` | `user.user_asset.delete` · `AUTH+SELF` | 204 | – | I1 | CE-PROF-003, CE-OPS-013 |
| EP-0427 | A03:A-08 | `POST {AV2}/workspaces/{slug}/` | `WorkspaceFileAssetEndpoint.post` (V/asset/v2.py:381) | `WorkspaceAssetEndpoints` → `CreateWorkspaceAssetUploadCommand` | `workspace.asset.create` · `WS(A,M,G)` | 200 | DT-AST-02 | I1 | CE-WS-003, CE-OPS-012, CE-OPS-013 |
| EP-0428 | A03:A-22 | `GET {AV2}/workspaces/{slug}/check/{asset_id}/` | `AssetCheckEndpoint.get` (V/asset/v2.py:843) | `WorkspaceAssetEndpoints` → `CheckAssetExistsQuery` | `workspace.asset.read` · `WS(A,M,G)` | 200 | – | I1 | CE-OPS-012 |
| EP-0429 | A03:A-24 | `GET {AV2}/workspaces/{slug}/download/{asset_id}/` | `WorkspaceAssetDownloadEndpoint.get` (V/asset/v2.py:941) | `WorkspaceAssetEndpoints` → `GetWorkspaceAssetDownloadQuery` | `workspace.asset.read` · `WS(A,M,G)` | 302 | DT-AST-02 | I1 | CE-OPS-012 |
| EP-0430 | A03:A-23 | `POST {AV2}/workspaces/{slug}/duplicate-assets/{asset_id}/` | `DuplicateAssetEndpoint.post` (V/asset/v2.py:885) | `WorkspaceAssetEndpoints` → `DuplicateAssetCommand` | `workspace.asset.create` · `WS(A,M,G)` | 200 | – | I1 | CE-OPS-013 |
| EP-0431 | A03:A-15 | `POST {AV2}/workspaces/{slug}/restore/{asset_id}/` | `AssetRestoreEndpoint.post` (V/asset/v2.py:587) | `WorkspaceAssetEndpoints` → `RestoreAssetCommand` | `workspace.asset.update` · `WS(A,M,G)` | 204 | – | I1 | CE-OPS-013 |
| EP-0432 | A03:A-11 | `GET {AV2}/workspaces/{slug}/{asset_id}/` | `WorkspaceFileAssetEndpoint.get` (V/asset/v2.py:512) | `WorkspaceAssetEndpoints` → `GetWorkspaceAssetRedirectQuery` | `workspace.asset.read` · `WS(A,M,G)` | 302 | – | I1 | CE-WS-003, CE-OPS-012, CE-OPS-013 |
| EP-0433 | A03:A-09 | `PATCH {AV2}/workspaces/{slug}/{asset_id}/` | `WorkspaceFileAssetEndpoint.patch` (V/asset/v2.py:458) | `WorkspaceAssetEndpoints` → `ConfirmWorkspaceAssetUploadCommand` | `workspace.asset.update` · `WS(A,M,G)` | 204 | – | I1 | CE-WS-003, CE-OPS-012, CE-OPS-013 |
| EP-0434 | A03:A-10 | `DELETE {AV2}/workspaces/{slug}/{asset_id}/` | `WorkspaceFileAssetEndpoint.delete` (V/asset/v2.py:491) | `WorkspaceAssetEndpoints` → `DeleteWorkspaceAssetCommand` | `workspace.asset.delete` · `WS(A,M,G)` | 204 | – | I1 | CE-WS-003, CE-OPS-012, CE-OPS-013 |
| EP-0447 | A03:A-05 | `POST /api/users/file-assets/` | `UserAssetsEndpoint.post` (V/asset/base.py:92) | — (nicht registriert (DT-AST-01)) | – | 201→404 | DT-AST-01 | I1 | CE-OPS-013 |
| EP-0449 | A03:A-06 | `GET /api/users/file-assets/{asset_key}/` | `UserAssetsEndpoint.get` (V/asset/base.py:81) | — (nicht registriert (DT-AST-01)) | – | 200→404 | DT-AST-01 | I1 | CE-OPS-013 |
| EP-0451 | A03:A-07 | `DELETE /api/users/file-assets/{asset_key}/` | `UserAssetsEndpoint.delete` (V/asset/base.py:99) | — (nicht registriert (DT-AST-01)) | – | 204→404 | DT-AST-01 | I1 | CE-OPS-013 |
| EP-0452 | A03:A-02 | `GET /api/workspaces/file-assets/{workspace_id}/{asset_key}/` | `FileAssetEndpoint.get` (V/asset/base.py:27) | — (nicht registriert (DT-AST-01)) | – | 200→404 | DT-AST-01 | I1 | CE-OPS-013 |
| EP-0454 | A03:A-03 | `DELETE /api/workspaces/file-assets/{workspace_id}/{asset_key}/` | `FileAssetEndpoint.delete` (V/asset/base.py:49) | — (nicht registriert (DT-AST-01)) | – | 204→404 | DT-AST-01 | I1 | CE-OPS-013 |
| EP-0455 | A03:A-04 | `POST /api/workspaces/file-assets/{workspace_id}/{asset_key}/restore/` | `FileAssetViewSet.restore` (V/asset/base.py:65) | — (nicht registriert (DT-AST-01)) | – | 204→404 | DT-AST-01 | I1 | CE-OPS-013 |
| EP-0457 | A03:A-01 | `POST {W}/file-assets/` | `FileAssetEndpoint.post` (V/asset/base.py:39) | — (nicht registriert (DT-AST-01)) | – | 201→404 | DT-AST-01 | I1 | CE-OPS-013 |
| EP-0459 | A05:S-31 | `POST /api/public/assets/v2/anchor/{anchor}/` | `EntityAssetEndpoint.post` (SPV/asset.py:87) | `PublicAssetEndpoints` → `CreatePublicAssetUploadCommand` | `public.asset.create` · `AUTH+BOARD` | 200 | – | I6 | CE-SPACE-007 |
| EP-0460 | A05:S-35 | `POST /api/public/assets/v2/anchor/{anchor}/restore/{pk}/` | `AssetRestoreEndpoint.post` (SPV/asset.py:217) | `PublicAssetEndpoints` → `RestorePublicAssetCommand` | `public.asset.create` · `AUTH+BOARD+OWN` | 204 | SEC-19, DT-AST-04 | I6 | CE-SPACE-007 |
| EP-0461 | A05:S-36 | `POST /api/public/assets/v2/anchor/{anchor}/{entity_id}/bulk/` | `EntityBulkAssetEndpoint.post` (SPV/asset.py:235) | `PublicAssetEndpoints` → `BulkConfirmPublicAssetsCommand` | `public.asset.create` · `AUTH+BOARD` | 204 | – | I6 | CE-SPACE-007 |
| EP-0462 | A05:S-32 | `GET /api/public/assets/v2/anchor/{anchor}/{pk}/` | `EntityAssetEndpoint.get` (SPV/asset.py:46) | `PublicAssetEndpoints` → `GetPublicAssetRedirectQuery` | `public.asset.read` · `ANON` | 302 | DT-AST-04 | I6 | CE-SPACE-007 |
| EP-0463 | A05:S-33 | `PATCH /api/public/assets/v2/anchor/{anchor}/{pk}/` | `EntityAssetEndpoint.patch` (SPV/asset.py:177) | `PublicAssetEndpoints` → `ConfirmPublicAssetUploadCommand` | `public.asset.update` · `AUTH+BOARD+OWN` | 204 | SEC-19, DT-AST-04 | I6 | CE-SPACE-007 |
| EP-0464 | A05:S-34 | `DELETE /api/public/assets/v2/anchor/{anchor}/{pk}/` | `EntityAssetEndpoint.delete` (SPV/asset.py:198) | `PublicAssetEndpoints` → `DeletePublicAssetCommand` | `public.asset.delete` · `AUTH+BOARD+OWN` | 204 | SEC-19, DT-AST-04 | I6 | CE-SPACE-007 |

### 4.14 `Plane.Analytics` – Analytics

Ablage der Endpoint-Klassen: `src/modules/Analytics/Plane.Analytics/Endpoints/App/<Klasse>.cs`. 16 Zeilen, davon 16 registriert und 0 nicht registriert (Entscheidung in Spalte „Abw./DT“).

| EP | Original-ID | Methode · Pfad (Original) | Original-View (Datei) | Ziel: Klasse → Handler | Permission · Ziel-Prüfung | Status Orig→Ziel | Abw./DT | Ink. | CE-IDs |
|---|---|---|---|---|---|---|---|---|---|
| EP-0469 | A03:AN-02 | `GET {W}/analytic-view/` | `AnalyticViewViewset.list` (V/analytic/base.py) | `AnalyticViewEndpoints` → `ListAnalyticViewsQuery` | `workspace.analytics_view.read` · `WS(A,M)` | 200 | – | I5 | CE-ANA-009 |
| EP-0470 | A03:AN-03 | `POST {W}/analytic-view/` | `AnalyticViewViewset.create` (V/analytic/base.py) | `AnalyticViewEndpoints` → `CreateAnalyticViewCommand` | `workspace.analytics_view.create` · `WS(A,M)` | 201 | – | I5 | CE-ANA-009 |
| EP-0471 | A03:AN-04 | `GET {W}/analytic-view/{pk}/` | `AnalyticViewViewset.retrieve` (V/analytic/base.py) | `AnalyticViewEndpoints` → `GetAnalyticViewQuery` | `workspace.analytics_view.read` · `WS(A,M)` | 200 | – | I5 | CE-ANA-009 |
| EP-0472 | A03:AN-05 | `PATCH {W}/analytic-view/{pk}/` | `AnalyticViewViewset.partial_update` (V/analytic/base.py) | `AnalyticViewEndpoints` → `UpdateAnalyticViewCommand` | `workspace.analytics_view.update` · `WS(A,M)` | 200 | DT-ANA-01 | I5 | CE-ANA-009 |
| EP-0473 | A03:AN-06 | `DELETE {W}/analytic-view/{pk}/` | `AnalyticViewViewset.destroy` (V/analytic/base.py) | `AnalyticViewEndpoints` → `DeleteAnalyticViewCommand` | `workspace.analytics_view.delete` · `WS(A,M)` | 204 | – | I5 | CE-ANA-009 |
| EP-0474 | A03:AN-13 | `GET {W}/advance-analytics-charts/` | `AdvanceAnalyticsChartEndpoint.get` (V/analytic/advance.py:288) | `AnalyticsEndpoints` → `GetAdvanceAnalyticsChartQuery` | `workspace.analytics.read` · `WS(A,M)` | 200 | – | I5 | CE-ANA-005, CE-ANA-006 |
| EP-0475 | A03:AN-12 | `GET {W}/advance-analytics-stats/` | `AdvanceAnalyticsStatsEndpoint.get` (V/analytic/advance.py:161) | `AnalyticsEndpoints` → `GetAdvanceAnalyticsStatsQuery` | `workspace.analytics.read` · `WS(A,M)` | 200 | – | I5 | CE-ANA-003, CE-ANA-007 |
| EP-0476 | A03:AN-11 | `GET {W}/advance-analytics/` | `AdvanceAnalyticsEndpoint.get` (V/analytic/advance.py:107) | `AnalyticsEndpoints` → `GetAdvanceAnalyticsQuery` | `workspace.analytics.read` · `WS(A,M)` | 200 | – | I5 | CE-ANA-001, CE-ANA-002, CE-ANA-004 |
| EP-0477 | A03:AN-01 | `GET {W}/analytics/` | `AnalyticsEndpoint.get` (V/analytic/base.py:40) | `AnalyticsEndpoints` → `GetLegacyAnalyticsPlotQuery` | `workspace.analytics.read` · `WS(A,M)` | 200 | – | I5 | CE-ANA-009 |
| EP-0478 | A03:AN-09 | `GET {W}/default-analytics/` | `DefaultAnalyticsEndpoint.get` (V/analytic/base.py:266) | `AnalyticsEndpoints` → `GetDefaultAnalyticsQuery` | `workspace.analytics.read_basic` · `WS(A,M,G)` | 200 | DT-ANA-01 | I5 | CE-ANA-009 |
| EP-0479 | A03:AN-08 | `POST {W}/export-analytics/` | `ExportAnalyticsEndpoint.post` (V/analytic/base.py:237) | `AnalyticsEndpoints` → `ExportAnalyticsCommand` | `workspace.analytics.export` · `WS(A,M)` | 200 | – | I5 | CE-ANA-009 |
| EP-0480 | A03:AN-10 | `GET {W}/project-stats/` | `ProjectStatsEndpoint.get` (V/analytic/base.py:412) | `AnalyticsEndpoints` → `ListProjectStatsQuery` | `workspace.analytics.read_basic` · `WS(A,M,G)` | 200 | – | I5 | CE-PRJ-003 |
| EP-0481 | A03:AN-16 | `GET {P}/advance-analytics-charts/` | `ProjectAdvanceAnalyticsChartEndpoint.get` (V/analytic/project_analytics.py:318) | `AnalyticsEndpoints` → `GetProjectAdvanceAnalyticsChartQuery` | `project.analytics.read_charts` · `PRJ(A,M,G)` | 200 | – | I5 | CE-ANA-008 |
| EP-0482 | A03:AN-15 | `GET {P}/advance-analytics-stats/` | `ProjectAdvanceAnalyticsStatsEndpoint.get` (V/analytic/project_analytics.py:166) | `AnalyticsEndpoints` → `GetProjectAdvanceAnalyticsStatsQuery` | `project.analytics.read` · `PRJ(A,M)` | 200 | – | I5 | CE-ANA-008 |
| EP-0483 | A03:AN-14 | `GET {P}/advance-analytics/` | `ProjectAdvanceAnalyticsEndpoint.get` (V/analytic/project_analytics.py:85) | `AnalyticsEndpoints` → `GetProjectAdvanceAnalyticsQuery` | `project.analytics.read` · `PRJ(A,M)` | 200 | – | I5 | CE-ANA-008 |
| EP-0484 | A03:AN-07 | `GET {W}/saved-analytic-view/{analytic_id}/` | `SavedAnalyticEndpoint.get` (V/analytic/base.py:198) | `AnalyticsEndpoints` → `GetSavedAnalyticsQuery` | `workspace.analytics.read` · `WS(A,M)` | 200 | – | I5 | CE-ANA-009 |

### 4.15 `Plane.Home` – Home, Quick Links, Recents, Stickies

Ablage der Endpoint-Klassen: `src/modules/Home/Plane.Home/Endpoints/App/<Klasse>.cs`. 11 Zeilen, davon 11 registriert und 0 nicht registriert (Entscheidung in Spalte „Abw./DT“).

| EP | Original-ID | Methode · Pfad (Original) | Original-View (Datei) | Ziel: Klasse → Handler | Permission · Ziel-Prüfung | Status Orig→Ziel | Abw./DT | Ink. | CE-IDs |
|---|---|---|---|---|---|---|---|---|---|
| EP-0485 | A03:W-54 | `GET {W}/quick-links/` | `QuickLinkViewSet.list` (V/workspace/quick_link.py:61) | `QuickLinkEndpoints` → `ListQuickLinksQuery` | `workspace.quick_link.read` · `WS(A,M,G)` | 200 | – | I5 | CE-HOME-004 |
| EP-0486 | A03:W-55 | `POST {W}/quick-links/` | `QuickLinkViewSet.create` (V/workspace/quick_link.py:24) | `QuickLinkEndpoints` → `CreateQuickLinkCommand` | `workspace.quick_link.create` · `WS(A,M,G)` | 201 | – | I5 | CE-HOME-004 |
| EP-0487 | A03:W-56 | `GET {W}/quick-links/{pk}/` | `QuickLinkViewSet.retrieve` (V/workspace/quick_link.py:46) | `QuickLinkEndpoints` → `GetQuickLinkQuery` | `workspace.quick_link.read` · `WS(A,M,G)` | 200 | – | I5 | CE-HOME-004 |
| EP-0488 | A03:W-57 | `PATCH {W}/quick-links/{pk}/` | `QuickLinkViewSet.partial_update` (V/workspace/quick_link.py:34) | `QuickLinkEndpoints` → `UpdateQuickLinkCommand` | `workspace.quick_link.update` · `WS(A,M,G)` | 200 | – | I5 | CE-HOME-004 |
| EP-0489 | A03:W-58 | `DELETE {W}/quick-links/{pk}/` | `QuickLinkViewSet.destroy` (V/workspace/quick_link.py:55) | `QuickLinkEndpoints` → `DeleteQuickLinkCommand` | `workspace.quick_link.delete` · `WS(A,M,G)` | 204 | – | I5 | CE-HOME-004 |
| EP-0490 | A03:W-61 | `GET {W}/recent-visits/` | `UserRecentVisitViewSet.list` (V/workspace/recent_visit.py:25) | `RecentVisitEndpoints` → `ListRecentVisitsQuery` | `workspace.recent_visit.read` · `WS(A,M,G)` | 200 | DT-HOME-01 | I5 | CE-HOME-005 |
| EP-0491 | A03:W-62 | `GET {W}/stickies/` | `WorkspaceStickyViewSet.list` (V/workspace/sticky.py:41) | `StickyEndpoints` → `ListStickiesQuery` | `workspace.sticky.read` · `WS(A,M,G)+OWN` | 200 | – | I5 | CE-HOME-008, CE-HOME-009 |
| EP-0492 | A03:W-63 | `POST {W}/stickies/` | `WorkspaceStickyViewSet.create` (V/workspace/sticky.py:32) | `StickyEndpoints` → `CreateStickyCommand` | `workspace.sticky.create` · `WS(A,M,G)` | 201 | – | I5 | CE-HOME-010 |
| EP-0493 | A03:W-64 | `GET {W}/stickies/{pk}/` | `WorkspaceStickyViewSet.retrieve` (V/workspace/sticky.py) | `StickyEndpoints` → `GetStickyQuery` | `workspace.sticky.read` · `WS(A,M,G)+OWN` | 200 | – | I5 | CE-HOME-010 |
| EP-0494 | A03:W-65 | `PATCH {W}/stickies/{pk}/` | `WorkspaceStickyViewSet.partial_update` (V/workspace/sticky.py:55) | `StickyEndpoints` → `UpdateStickyCommand` | `workspace.sticky.update` · `WS(A,M,G)+C:Sticky` | 200 | – | I5 | CE-HOME-010 |
| EP-0495 | A03:W-66 | `DELETE {W}/stickies/{pk}/` | `WorkspaceStickyViewSet.destroy` (V/workspace/sticky.py:59) | `StickyEndpoints` → `DeleteStickyCommand` | `workspace.sticky.delete` · `WS(A,M,G)+C:Sticky` | 204 | – | I5 | CE-HOME-010 |

### 4.16 `Plane.Notifications` – Benachrichtigungen

Ablage der Endpoint-Klassen: `src/modules/Notifications/Plane.Notifications/Endpoints/App/<Klasse>.cs`. 12 Zeilen, davon 12 registriert und 0 nicht registriert (Entscheidung in Spalte „Abw./DT“).

| EP | Original-ID | Methode · Pfad (Original) | Original-View (Datei) | Ziel: Klasse → Handler | Permission · Ziel-Prüfung | Status Orig→Ziel | Abw./DT | Ink. | CE-IDs |
|---|---|---|---|---|---|---|---|---|---|
| EP-0496 | A03:N-01 | `GET {W}/users/notifications/` | `NotificationViewSet.list` (V/notification/base.py:49) | `NotificationEndpoints` → `ListNotificationsQuery` | `workspace.notification.read` · `WS(A,M,G)` | 200 | DT-NOTIF-01 | I5 | CE-NOTIF-004, CE-NOTIF-005 |
| EP-0497 | A03:N-10 | `POST {W}/users/notifications/mark-all-read/` | `MarkAllReadNotificationViewSet.create` (V/notification/base.py:239) | `NotificationEndpoints` → `MarkAllNotificationsReadCommand` | `workspace.notification.update` · `WS(A,M,G)` | 200 | DT-NOTIF-02 | I5 | CE-NOTIF-006 |
| EP-0498 | A03:N-09 | `GET {W}/users/notifications/unread/` | `UnreadNotificationEndpoint.get` (V/notification/base.py:205) | `NotificationEndpoints` → `GetUnreadNotificationCountsQuery` | `workspace.notification.read` · `WS(A,M,G)` | 200 | – | I5 | CE-NOTIF-004 |
| EP-0499 | A03:N-02 | `GET {W}/users/notifications/{pk}/` | `NotificationViewSet.retrieve` (V/notification/base.py) | `NotificationEndpoints` → `GetNotificationQuery` | `workspace.notification.read` · `WS(A,M,G)+OWN` | 200 | – | I5 | CE-NOTIF-007 |
| EP-0500 | A03:N-03 | `PATCH {W}/users/notifications/{pk}/` | `NotificationViewSet.partial_update` (V/notification/base.py:157) | `NotificationEndpoints` → `UpdateNotificationCommand` | `workspace.notification.update` · `WS(A,M,G)` | 200 | – | I5 | CE-NOTIF-007 |
| EP-0501 | A03:N-04 | `DELETE {W}/users/notifications/{pk}/` | `NotificationViewSet.destroy` (V/notification/base.py) | `NotificationEndpoints` → `DeleteNotificationCommand` | `workspace.notification.delete` · `WS(A,M,G)+OWN` | 204 | – | I5 | CE-NOTIF-007 |
| EP-0502 | A03:N-07 | `POST {W}/users/notifications/{pk}/archive/` | `NotificationViewSet.archive` (V/notification/base.py:185) | `NotificationEndpoints` → `ArchiveNotificationCommand` | `workspace.notification.update` · `WS(A,M,G)` | 200 | – | I5 | CE-NOTIF-006 |
| EP-0503 | A03:N-08 | `DELETE {W}/users/notifications/{pk}/archive/` | `NotificationViewSet.unarchive` (V/notification/base.py:193) | `NotificationEndpoints` → `UnarchiveNotificationCommand` | `workspace.notification.update` · `WS(A,M,G)` | 200 | – | I5 | CE-NOTIF-006 |
| EP-0504 | A03:N-05 | `POST {W}/users/notifications/{pk}/read/` | `NotificationViewSet.mark_read` (V/notification/base.py:169) | `NotificationEndpoints` → `MarkNotificationReadCommand` | `workspace.notification.update` · `WS(A,M,G)` | 200 | – | I5 | CE-NOTIF-006 |
| EP-0505 | A03:N-06 | `DELETE {W}/users/notifications/{pk}/read/` | `NotificationViewSet.mark_unread` (V/notification/base.py:177) | `NotificationEndpoints` → `MarkNotificationUnreadCommand` | `workspace.notification.delete` · `WS(A,M,G)` | 200 | – | I5 | CE-NOTIF-006 |
| EP-0506 | A03:N-11 | `GET /api/users/me/notification-preferences/` | `UserNotificationPreferenceEndpoint.get` (V/notification/base.py:301) | `NotificationPreferenceEndpoints` → `GetNotificationPreferencesQuery` | `user.notification_preference.read` · `AUTH+SELF` | 200 | – | I5 | CE-NOTIF-009 |
| EP-0507 | A03:N-12 | `PATCH /api/users/me/notification-preferences/` | `UserNotificationPreferenceEndpoint.patch` (V/notification/base.py:307) | `NotificationPreferenceEndpoints` → `UpdateNotificationPreferencesCommand` | `user.notification_preference.update` · `AUTH+SELF` | 200 | – | I5 | CE-NOTIF-009 |

### 4.17 `Plane.Search` – Suche

Ablage der Endpoint-Klassen: `src/modules/Search/Plane.Search/Endpoints/App/<Klasse>.cs`. 2 Zeilen, davon 2 registriert und 0 nicht registriert (Entscheidung in Spalte „Abw./DT“).

| EP | Original-ID | Methode · Pfad (Original) | Original-View (Datei) | Ziel: Klasse → Handler | Permission · Ziel-Prüfung | Status Orig→Ziel | Abw./DT | Ink. | CE-IDs |
|---|---|---|---|---|---|---|---|---|---|
| EP-0508 | A03:SR-03 | `GET {W}/entity-search/` | `SearchEndpoint.get` (V/search/base.py:332) | `SearchEndpoints` → `SearchEntitiesQuery` | `workspace.search.read` · `WS(A,M,G)+VIS` | 200 | DT-SRCH-01 | I5 | CE-SRCH-002, CE-WI-044 |
| EP-0509 | A03:SR-01 | `GET {W}/search/` | `GlobalSearchEndpoint.get` (V/search/base.py:295) | `SearchEndpoints` → `GlobalSearchQuery` | `workspace.search.read` · `WS(A,M,G)+VIS` | 200 | DT-SRCH-01 | I5 | CE-SRCH-001, CE-SRCH-004 |

### 4.18 `Plane.PublicSpace` – Veröffentlichung (App) und Space-API `/api/public/`

Ablage der Endpoint-Klassen: `src/modules/PublicSpace/Plane.PublicSpace/Endpoints/{App,Space}/<Klasse>.cs`. 30 Zeilen, davon 29 registriert und 1 nicht registriert (Entscheidung in Spalte „Abw./DT“).

| EP | Original-ID | Methode · Pfad (Original) | Original-View (Datei) | Ziel: Klasse → Handler | Permission · Ziel-Prüfung | Status Orig→Ziel | Abw./DT | Ink. | CE-IDs |
|---|---|---|---|---|---|---|---|---|---|
| EP-0510 | A03:P-30 | `GET {P}/project-deploy-boards/` | `DeployBoardViewSet.list` (V/project/base.py:544) | `DeployBoardEndpoints` → `ListDeployBoardsQuery` | `project.publish.read` · `PRJ(A,M,G)` | 200 | – | I6 | CE-SPACE-001, CE-SPACE-002 |
| EP-0511 | A03:P-31 | `POST {P}/project-deploy-boards/` | `DeployBoardViewSet.create` (V/project/base.py:552) | `DeployBoardEndpoints` → `CreateDeployBoardCommand` | `project.publish.create` · `PRJ(A,M)` | 200 | – | I6 | CE-SPACE-001, CE-SPACE-002 |
| EP-0512 | A03:P-32 | `GET {P}/project-deploy-boards/{pk}/` | `DeployBoardViewSet.retrieve` (V/project/base.py) | `DeployBoardEndpoints` → `GetDeployBoardQuery` | `project.publish.read` · `PRJ(A,M,G)` | 200 | SEC-16, DT-PRJ-03 | I6 | CE-SPACE-001, CE-SPACE-002 |
| EP-0513 | A03:P-33 | `PATCH {P}/project-deploy-boards/{pk}/` | `DeployBoardViewSet.partial_update` (V/project/base.py) | `DeployBoardEndpoints` → `UpdateDeployBoardCommand` | `project.publish.update` · `PRJ(A,M)` | 200 | SEC-16, DT-PRJ-03 | I6 | CE-SPACE-001, CE-SPACE-002 |
| EP-0514 | A03:P-34 | `DELETE {P}/project-deploy-boards/{pk}/` | `DeployBoardViewSet.destroy` (V/project/base.py) | `DeployBoardEndpoints` → `DeleteDeployBoardCommand` | `project.publish.delete` · `PRJ(A,M)` | 204 | SEC-16, DT-PRJ-03 | I6 | CE-SPACE-001, CE-SPACE-002 |
| EP-0515 | A05:S-21 | `GET {SP}/cycles/` | `ProjectCyclesEndpoint.get` (SPV/cycle.py:18) | `PublicBoardEndpoints` → `ListBoardCyclesQuery` | `public.board.read` · `ANON` | 200 | – | I6 | CE-SPACE-005 |
| EP-0516 | A05:S-05 | `GET {SP}/issues/` | `ProjectIssuesPublicEndpoint.get` (SPV/issue.py:109) | `PublicBoardEndpoints` → `ListBoardWorkItemsQuery` | `public.board.read` · `ANON` | 200 | DT-SPACE-04 | I6 | CE-SPACE-003, CE-SPACE-019, CE-SPACE-020, CE-SPACE-022 |
| EP-0517 | A05:S-06 | `GET {SP}/issues/{issue_id}/` | `IssueRetrievePublicEndpoint.get` (SPV/issue.py:689) | `PublicBoardEndpoints` → `GetBoardWorkItemQuery` | `public.board.read` · `ANON` | 200 | DT-SPACE-02, DT-SPACE-03 | I6 | CE-SPACE-004, CE-SPACE-024 |
| EP-0518 | A05:S-24 | `GET {SP}/labels/` | `ProjectLabelsEndpoint.get` (SPV/label.py:18) | `PublicBoardEndpoints` → `ListBoardLabelsQuery` | `public.board.read` · `ANON` | 200 | – | I6 | CE-SPACE-005 |
| EP-0519 | A05:S-25 | `GET {SP}/members/` | `ProjectMembersEndpoint.get` (SPV/project.py:68) | `PublicBoardEndpoints` → `ListBoardMembersQuery` | `public.board.read` · `ANON` | 200 | – | I6 | CE-SPACE-005 |
| EP-0520 | A05:S-01 | `GET {SP}/meta/` | `ProjectMetaDataEndpoint.get` (SPV/meta.py:19) | `PublicBoardEndpoints` → `GetBoardMetaQuery` | `public.board.read` · `ANON` | 200 | – | I6 | CE-SPACE-002, CE-SPACE-017 |
| EP-0521 | A05:S-22 | `GET {SP}/modules/` | `ProjectModulesEndpoint.get` (SPV/module.py:18) | `PublicBoardEndpoints` → `ListBoardModulesQuery` | `public.board.read` · `ANON` | 200 | – | I6 | CE-SPACE-005 |
| EP-0522 | A05:S-02 | `GET {SP}/settings/` | `ProjectDeployBoardPublicSettingsEndpoint.get` (SPV/project.py:22) | `PublicBoardEndpoints` → `GetBoardSettingsQuery` | `public.board.read` · `ANON` | 200 | – | I6 | CE-SPACE-002, CE-SPACE-017 |
| EP-0523 | A05:S-23 | `GET {SP}/states/` | `ProjectStatesEndpoint.get` (SPV/state.py:21) | `PublicBoardEndpoints` → `ListBoardStatesQuery` | `public.board.read` · `ANON` | 200 | – | I6 | CE-SPACE-005 |
| EP-0524 | A05:S-03 | `GET /api/public/workspaces/{slug}/projects/{project_id}/anchor/` | `WorkspaceProjectAnchorEndpoint.get` (SPV/project.py:57) | `PublicBoardEndpoints` → `GetBoardAnchorQuery` | `public.board.read` · `ANON` | 200 | – | I6 | CE-SPACE-016 |
| EP-0525 | A05:S-07 | `GET {SP}/issues/{issue_id}/comments/` | `IssueCommentPublicViewSet.list` (SPV/issue.py) | `PublicCommentEndpoints` → `ListPublicCommentsQuery` | `public.comment.read` · `ANON+BOARD` | 200 | – | I6 | CE-SPACE-025 |
| EP-0526 | A05:S-08 | `POST {SP}/issues/{issue_id}/comments/` | `IssueCommentPublicViewSet.create` (SPV/issue.py:291) | `PublicCommentEndpoints` → `CreatePublicCommentCommand` | `public.comment.create` · `AUTH+BOARD` | 201 | – | I6 | CE-SPACE-025 |
| EP-0527 | A05:S-09 | `GET {SP}/issues/{issue_id}/comments/{pk}/` | `IssueCommentPublicViewSet.retrieve` (SPV/issue.py) | `PublicCommentEndpoints` → `GetPublicCommentQuery` | `public.comment.read` · `ANON+BOARD` | 200 | – | I6 | CE-SPACE-025 |
| EP-0528 | A05:S-10 | `PATCH {SP}/issues/{issue_id}/comments/{pk}/` | `IssueCommentPublicViewSet.partial_update` (SPV/issue.py:334) | `PublicCommentEndpoints` → `UpdatePublicCommentCommand` | `public.comment.update` · `AUTH+BOARD` | 200 | – | I6 | CE-SPACE-025 |
| EP-0529 | A05:S-11 | `DELETE {SP}/issues/{issue_id}/comments/{pk}/` | `IssueCommentPublicViewSet.destroy` (SPV/issue.py:368) | `PublicCommentEndpoints` → `DeletePublicCommentCommand` | `public.comment.delete` · `AUTH+BOARD` | 204 | – | I6 | CE-SPACE-025 |
| EP-0530 | A05:S-15 | `GET {SP}/comments/{comment_id}/reactions/` | `CommentReactionPublicViewSet.list` (SPV/issue.py) | `PublicReactionEndpoints` → `ListPublicCommentReactionsQuery` | `public.reaction.read` · `AUTH+BOARD` | 200 | – | I6 | CE-SPACE-026 |
| EP-0531 | A05:S-16 | `POST {SP}/comments/{comment_id}/reactions/` | `CommentReactionPublicViewSet.create` (SPV/issue.py:519) | `PublicReactionEndpoints` → `AddPublicCommentReactionCommand` | `public.reaction.create` · `AUTH+BOARD` | 201 | – | I6 | CE-SPACE-026 |
| EP-0532 | A05:S-17 | `DELETE {SP}/comments/{comment_id}/reactions/{reaction_code}/` | `CommentReactionPublicViewSet.destroy` (SPV/issue.py:566) | `PublicReactionEndpoints` → `RemovePublicCommentReactionCommand` | `public.reaction.delete` · `AUTH+BOARD` | 204 | – | I6 | CE-SPACE-026 |
| EP-0533 | A05:S-12 | `GET {SP}/issues/{issue_id}/reactions/` | `IssueReactionPublicViewSet.list` (SPV/issue.py) | `PublicReactionEndpoints` → `ListPublicWorkItemReactionsQuery` | `public.reaction.read` · `AUTH+BOARD` | 200 | DT-SPACE-02 | I6 | CE-SPACE-027 |
| EP-0534 | A05:S-13 | `POST {SP}/issues/{issue_id}/reactions/` | `IssueReactionPublicViewSet.create` (SPV/issue.py:422) | `PublicReactionEndpoints` → `AddPublicWorkItemReactionCommand` | `public.reaction.create` · `AUTH+BOARD` | 201 | – | I6 | CE-SPACE-027 |
| EP-0535 | A05:S-14 | `DELETE {SP}/issues/{issue_id}/reactions/{reaction_code}/` | `IssueReactionPublicViewSet.destroy` (SPV/issue.py:463) | `PublicReactionEndpoints` → `RemovePublicWorkItemReactionCommand` | `public.reaction.delete` · `AUTH+BOARD` | 204 | – | I6 | CE-SPACE-027 |
| EP-0536 | A05:S-18 | `GET {SP}/issues/{issue_id}/votes/` | `IssueVotePublicViewSet.list` (SPV/issue.py) | `PublicVoteEndpoints` → `ListVotesQuery` | `public.vote.read` · `AUTH+BOARD` | 200 | DT-SPACE-02 | I6 | CE-SPACE-028 |
| EP-0537 | A05:S-19 | `POST {SP}/issues/{issue_id}/votes/` | `IssueVotePublicViewSet.create` (SPV/issue.py:624) | `PublicVoteEndpoints` → `CastVoteCommand` | `public.vote.create` · `AUTH+BOARD` | 201 | DT-SPACE-05 | I6 | CE-SPACE-028 |
| EP-0538 | A05:S-20 | `DELETE {SP}/issues/{issue_id}/votes/` | `IssueVotePublicViewSet.destroy` (SPV/issue.py:665) | `PublicVoteEndpoints` → `RemoveVoteCommand` | `public.vote.delete` · `AUTH+BOARD` | 204 | DT-SPACE-05 | I6 | CE-SPACE-028 |
| EP-0539 | A05:S-04 | `GET /api/public/workspaces/{slug}/project-boards/` | `WorkspaceProjectDeployBoardEndpoint.get` (SPV/project.py:31) | — (nicht registriert (DT-SPACE-01)) | – | 500→404 | DT-SPACE-01 | I6 | CE-SPACE-002 |

### 4.19 `Plane.PublicApi` – Public API v1 `/api/v1/` und OpenAPI

Ablage der Endpoint-Klassen: `src/modules/PublicApi/Plane.PublicApi/Endpoints/V1/<Klasse>.cs` (OpenAPI: `Endpoints/OpenApi/OpenApiEndpoints.cs`). 140 Zeilen, davon 137 registriert und 3 nicht registriert (Entscheidung in Spalte „Abw./DT“).

| EP | Original-ID | Methode · Pfad (Original) | Original-View (Datei) | Ziel: Klasse → Handler | Permission · Ziel-Prüfung | Status Orig→Ziel | Abw./DT | Ink. | CE-IDs |
|---|---|---|---|---|---|---|---|---|---|
| EP-0540 | A05:V-USR-01 | `GET /api/v1/users/me/` | `UserEndpoint.get` (V1V/user.py:34) | `V1CurrentUserEndpoints` → `GetCurrentUserQuery` | `user.user.read` · `AUTH+SELF` | 200 | – | I6 | CE-API-005 |
| EP-0541 | A05:V-CYC-13 | `GET {V1P}/archived-cycles/` | `CycleArchiveUnarchiveAPIEndpoint.get` (V1V/cycle.py:778) | `V1CycleEndpoints` → `ListArchivedCyclesQuery` | `project.cycle.read_archived` · `PRJ(A,M)` | 200 | HARM-02 | I6 | CE-API-029 |
| EP-0542 | A05:V-CYC-14 | `DELETE {V1P}/archived-cycles/{cycle_id}/unarchive/` | `CycleArchiveUnarchiveAPIEndpoint.delete` (V1V/cycle.py:831) | `V1CycleEndpoints` → `UnarchiveCycleCommand` | `project.cycle.unarchive` · `PRJ(A,M)` | 204 | – | I6 | CE-API-029 |
| EP-0543 | A05:V-CYC-03 | `GET {V1P}/cycles-lite/` | `CycleListLiteAPIEndpoint.get` (V1V/cycle.py:381) | `V1CycleEndpoints` → `ListCyclesLiteQuery` | `project.cycle.read` · `PRJ(A,M,G)` | 200 | – | I6 | CE-API-026 |
| EP-0544 | A05:V-CYC-01 | `GET {V1P}/cycles/` | `CycleListCreateAPIEndpoint.get` (V1V/cycle.py:191) | `V1CycleEndpoints` → `ListCyclesQuery` | `project.cycle.read` · `PRJ(A,M,G)` | 200 | – | I6 | CE-API-026 |
| EP-0545 | A05:V-CYC-02 | `POST {V1P}/cycles/` | `CycleListCreateAPIEndpoint.post` (V1V/cycle.py:300) | `V1CycleEndpoints` → `CreateCycleCommand` | `project.cycle.create` · `PRJ(A,M)` | 201 | – | I6 | CE-API-026 |
| EP-0546 | A05:V-CYC-12 | `POST {V1P}/cycles/{cycle_id}/archive/` | `CycleArchiveUnarchiveAPIEndpoint.post` (V1V/cycle.py:800) | `V1CycleEndpoints` → `ArchiveCycleCommand` | `project.cycle.archive` · `PRJ(A,M)` | 204 | – | I6 | CE-API-029 |
| EP-0547 | A05:V-CYC-04 | `GET {V1P}/cycles/{pk}/` | `CycleDetailAPIEndpoint.get` (V1V/cycle.py:510) | `V1CycleEndpoints` → `GetCycleQuery` | `project.cycle.read` · `PRJ(A,M,G)` | 200 | – | I6 | CE-API-026 |
| EP-0548 | A05:V-CYC-05 | `PATCH {V1P}/cycles/{pk}/` | `CycleDetailAPIEndpoint.patch` (V1V/cycle.py:542) | `V1CycleEndpoints` → `UpdateCycleCommand` | `project.cycle.update` · `PRJ(A,M)` | 200 | DT-CYC-01 | I6 | CE-API-026 |
| EP-0549 | A05:V-CYC-06 | `DELETE {V1P}/cycles/{pk}/` | `CycleDetailAPIEndpoint.delete` (V1V/cycle.py:616) | `V1CycleEndpoints` → `DeleteCycleCommand` | `project.cycle.delete` · `PRJ(A)+C:Cycle` | 204 | SEC-20 | I6 | CE-API-026 |
| EP-0550 | A05:V-CYC-07 | `GET {V1P}/cycles/{cycle_id}/cycle-issues/` | `CycleIssueListCreateAPIEndpoint.get` (V1V/cycle.py:891) | `V1CycleWorkItemEndpoints` → `ListCycleWorkItemsQuery` | `project.cycle_work_item.read` · `PRJ(A,M)` | 200 | HARM-02 | I6 | CE-API-027 |
| EP-0551 | A05:V-CYC-08 | `POST {V1P}/cycles/{cycle_id}/cycle-issues/` | `CycleIssueListCreateAPIEndpoint.post` (V1V/cycle.py:957) | `V1CycleWorkItemEndpoints` → `AddCycleWorkItemsCommand` | `project.cycle_work_item.create` · `PRJ(A,M)` | 200 | – | I6 | CE-API-027 |
| EP-0552 | A05:V-CYC-09 | `GET {V1P}/cycles/{cycle_id}/cycle-issues/{issue_id}/` | `CycleIssueDetailAPIEndpoint.get` (V1V/cycle.py:1117) | `V1CycleWorkItemEndpoints` → `GetCycleWorkItemQuery` | `project.cycle_work_item.read` · `PRJ(A,M)` | 200 | HARM-02 | I6 | CE-API-027 |
| EP-0553 | A05:V-CYC-10 | `DELETE {V1P}/cycles/{cycle_id}/cycle-issues/{issue_id}/` | `CycleIssueDetailAPIEndpoint.delete` (V1V/cycle.py:1140) | `V1CycleWorkItemEndpoints` → `RemoveCycleWorkItemCommand` | `project.cycle_work_item.delete` · `PRJ(A,M)` | 204 | – | I6 | CE-API-027 |
| EP-0554 | A05:V-CYC-11 | `POST {V1P}/cycles/{cycle_id}/transfer-issues/` | `TransferCycleIssueAPIEndpoint.post` (V1V/cycle.py:1221) | `V1CycleWorkItemEndpoints` → `TransferCycleWorkItemsCommand` | `project.cycle_work_item.transfer` · `PRJ(A,M)` | 200 | – | I6 | CE-API-028 |
| EP-0555 | A05:V-AST-07 | `POST {V1W}/assets/` | `GenericAssetEndpoint.post` (V1V/asset.py:507) | `V1GenericAssetEndpoints` → `CreateGenericAssetUploadCommand` | `workspace.asset.create` · `WS(A,M,G)` | 200 | DT-V1-09, DT-V1-10 | I6 | CE-API-016 |
| EP-0556 | A05:V-AST-08 | `GET {V1W}/assets/{asset_id}/` | `GenericAssetEndpoint.get` (V1V/asset.py:427) | `V1GenericAssetEndpoints` → `GetGenericAssetQuery` | `workspace.asset.read` · `WS(A,M,G)` | 200 | DT-V1-09 | I6 | CE-API-016 |
| EP-0557 | A05:V-AST-09 | `PATCH {V1W}/assets/{asset_id}/` | `GenericAssetEndpoint.patch` (V1V/asset.py:608) | `V1GenericAssetEndpoints` → `ConfirmGenericAssetUploadCommand` | `workspace.asset.update` · `WS(A,M,G)` | 204 | – | I6 | CE-API-016 |
| EP-0558 | A05:V-INT-01 | `GET {V1P}/intake-issues/` | `IntakeIssueListCreateAPIEndpoint.get` (V1V/intake.py:108) | `V1IntakeWorkItemEndpoints` → `ListIntakeWorkItemsQuery` | `project.intake_work_item.read` · `PRJ(A,M,G)+VIS` | 200 | DT-INT-03 | I6 | CE-API-025 |
| EP-0559 | A05:V-INT-02 | `POST {V1P}/intake-issues/` | `IntakeIssueListCreateAPIEndpoint.post` (V1V/intake.py:144) | `V1IntakeWorkItemEndpoints` → `CreateIntakeWorkItemCommand` | `project.intake_work_item.create` · `PRJ(A,M,G)` | 201 | DT-INT-03 | I6 | CE-API-025 |
| EP-0560 | A05:V-INT-03 | `GET {V1P}/intake-issues/{issue_id}/` | `IntakeIssueDetailAPIEndpoint.get` (V1V/intake.py:278) | `V1IntakeWorkItemEndpoints` → `GetIntakeWorkItemQuery` | `project.intake_work_item.read` · `PRJ(A,M,G)+C:Issue+VIS` | 200 | HARM-01, DT-INT-04 | I6 | CE-API-025 |
| EP-0561 | A05:V-INT-04 | `PATCH {V1P}/intake-issues/{issue_id}/` | `IntakeIssueDetailAPIEndpoint.patch` (V1V/intake.py:309) | `V1IntakeWorkItemEndpoints` → `UpdateIntakeWorkItemCommand` | `project.intake_work_item.update` · `PRJ(A)+C:Issue` | 200 | HARM-01, DT-INT-04 | I6 | CE-API-025 |
| EP-0562 | A05:V-INT-05 | `DELETE {V1P}/intake-issues/{issue_id}/` | `IntakeIssueDetailAPIEndpoint.delete` (V1V/intake.py:460) | `V1IntakeWorkItemEndpoints` → `DeleteIntakeWorkItemCommand` | `project.intake_work_item.delete` · `PRJ(A)+C:Issue` | 204 | HARM-01, DT-INT-04 | I6 | CE-API-025 |
| EP-0563 | A05:V-INV-01 | `GET {V1W}/invitations/` | `WorkspaceInvitationsViewset.list` (V1V/invite.py) | `V1InvitationEndpoints` → `ListWorkspaceInvitationsQuery` | `workspace.invitation.read` · `WS(A,M)` | 200 | HARM-04, DT-V1-05 | I6 | CE-API-013 |
| EP-0564 | A05:V-INV-02 | `POST {V1W}/invitations/` | `WorkspaceInvitationsViewset.create` (V1V/invite.py) | `V1InvitationEndpoints` → `CreateWorkspaceInvitationsCommand` | `workspace.invitation.create` · `WS(A,M)` | 201 | HARM-04, DT-V1-08 | I6 | CE-API-013 |
| EP-0565 | A05:V-INV-03 | `GET {V1W}/invitations/{pk}/` | `WorkspaceInvitationsViewset.retrieve` (V1V/invite.py) | `V1InvitationEndpoints` → `GetWorkspaceInvitationQuery` | `workspace.invitation.read` · `WS(A,M)` | 200 | HARM-04 | I6 | CE-API-013 |
| EP-0566 | A05:V-INV-04 | `PATCH {V1W}/invitations/{pk}/` | `WorkspaceInvitationsViewset.partial_update` (V1V/invite.py) | `V1InvitationEndpoints` → `UpdateWorkspaceInvitationCommand` | `workspace.invitation.update` · `WS(A,M)` | 200 | HARM-04 | I6 | CE-API-013 |
| EP-0567 | A05:V-INV-06 | `DELETE {V1W}/invitations/{pk}/` | `WorkspaceInvitationsViewset.destroy` (V1V/invite.py) | `V1InvitationEndpoints` → `DeleteWorkspaceInvitationCommand` | `workspace.invitation.delete` · `WS(A,M)` | 204 | HARM-04 | I6 | CE-API-013 |
| EP-0568 | A05:V-LBL-01 | `GET {V1P}/labels/` | `LabelListCreateAPIEndpoint.get` (V1V/issue.py:1006) | `V1LabelEndpoints` → `ListLabelsQuery` | `project.label.read` · `PRJ(A,M,G)` | 200 | – | I6 | CE-API-010 |
| EP-0569 | A05:V-LBL-02 | `POST {V1P}/labels/` | `LabelListCreateAPIEndpoint.post` (V1V/issue.py:933) | `V1LabelEndpoints` → `CreateLabelCommand` | `project.label.create` · `PRJ(A)` | 201 | – | I6 | CE-API-010 |
| EP-0570 | A05:V-LBL-03 | `GET {V1P}/labels/{pk}/` | `LabelDetailAPIEndpoint.get` (V1V/issue.py:1041) | `V1LabelEndpoints` → `GetLabelQuery` | `project.label.read` · `PRJ(A,M,G)` | 200 | – | I6 | CE-API-010 |
| EP-0571 | A05:V-LBL-04 | `PATCH {V1P}/labels/{pk}/` | `LabelDetailAPIEndpoint.patch` (V1V/issue.py:1071) | `V1LabelEndpoints` → `UpdateLabelCommand` | `project.label.update` · `PRJ(A)` | 200 | – | I6 | CE-API-010 |
| EP-0572 | A05:V-LBL-05 | `DELETE {V1P}/labels/{pk}/` | `LabelDetailAPIEndpoint.delete` (V1V/issue.py:1116) | `V1LabelEndpoints` → `DeleteLabelCommand` | `project.label.delete` · `PRJ(A)` | 204 | – | I6 | CE-API-010 |
| EP-0573 | A05:V-MEM-02 | `GET {V1W}/members-lite/` | `WorkspaceMemberLiteAPIEndpoint.get` (V1V/member.py:262) | `V1MemberEndpoints` → `ListWorkspaceMembersLiteQuery` | `workspace.member.read` · `WS(A,M,G)` | 200 | HARM-03, DT-V1-07 | I6 | CE-API-011 |
| EP-0574 | A05:V-MEM-01 | `GET {V1W}/members/` | `WorkspaceMemberAPIEndpoint.get` (V1V/member.py:77) | `V1MemberEndpoints` → `ListWorkspaceMembersQuery` | `workspace.member.read` · `WS(A,M,G)` | 200 | HARM-03, DT-V1-07 | I6 | CE-API-011 |
| EP-0575 | A05:V-MEM-03 | `GET {V1P}/members/` | `ProjectMemberListCreateAPIEndpoint.get` (V1V/member.py:129) | `V1MemberEndpoints` → `ListProjectMembersQuery` | `project.member.read` · `PRJ(A,M,G)` | 200 | DT-V1-07 | I6 | CE-API-012 |
| EP-0576 | A05:V-MEM-04 | `POST {V1P}/members/` | `ProjectMemberListCreateAPIEndpoint.post` (V1V/member.py:160) | `V1MemberEndpoints` → `CreateProjectMemberCommand` | `project.member.create` · `PRJ(A)` | 201 | – | I6 | CE-API-012 |
| EP-0577 | A05:V-MEM-05 | `GET {V1P}/members/{pk}/` | `ProjectMemberDetailAPIEndpoint.get` (V1V/member.py:183) | `V1MemberEndpoints` → `GetProjectMemberQuery` | `project.member.read` · `PRJ(A,M,G)` | 200 | – | I6 | CE-API-012 |
| EP-0578 | A05:V-MEM-06 | `PATCH {V1P}/members/{pk}/` | `ProjectMemberDetailAPIEndpoint.patch` (V1V/member.py:211) | `V1MemberEndpoints` → `UpdateProjectMemberCommand` | `project.member.update` · `PRJ(A)` | 200 | – | I6 | CE-API-012 |
| EP-0579 | A05:V-MEM-07 | `DELETE {V1P}/members/{pk}/` | `ProjectMemberDetailAPIEndpoint.delete` (V1V/member.py:231) | `V1MemberEndpoints` → `DeleteProjectMemberCommand` | `project.member.delete` · `PRJ(A)` | 204 | – | I6 | CE-API-012 |
| EP-0580 | A05:V-MEM-08 | `GET {V1P}/project-members-lite/` | `ProjectMemberLiteAPIEndpoint.get` (V1V/member.py:309) | `V1MemberEndpoints` → `ListProjectMembersLiteQuery` | `project.member.read` · `PRJ(A,M,G)` | 200 | DT-V1-07 | I6 | CE-API-012 |
| EP-0581 | A05:V-MEM-03 | `GET {V1P}/project-members/` | `ProjectMemberListCreateAPIEndpoint.get` (V1V/member.py:129) | `V1MemberEndpoints` → `ListProjectMembersQuery` | `project.member.read` · `PRJ(A,M,G)` | 200 | DT-V1-07 | I6 | CE-API-012 |
| EP-0582 | A05:V-MEM-04 | `POST {V1P}/project-members/` | `ProjectMemberListCreateAPIEndpoint.post` (V1V/member.py:160) | `V1MemberEndpoints` → `CreateProjectMemberCommand` | `project.member.create` · `PRJ(A)` | 201 | – | I6 | CE-API-012 |
| EP-0583 | A05:V-MEM-05 | `GET {V1P}/project-members/{pk}/` | `ProjectMemberDetailAPIEndpoint.get` (V1V/member.py:183) | `V1MemberEndpoints` → `GetProjectMemberQuery` | `project.member.read` · `PRJ(A,M,G)` | 200 | – | I6 | CE-API-012 |
| EP-0584 | A05:V-MEM-06 | `PATCH {V1P}/project-members/{pk}/` | `ProjectMemberDetailAPIEndpoint.patch` (V1V/member.py:211) | `V1MemberEndpoints` → `UpdateProjectMemberCommand` | `project.member.update` · `PRJ(A)` | 200 | – | I6 | CE-API-012 |
| EP-0585 | A05:V-MEM-07 | `DELETE {V1P}/project-members/{pk}/` | `ProjectMemberDetailAPIEndpoint.delete` (V1V/member.py:231) | `V1MemberEndpoints` → `DeleteProjectMemberCommand` | `project.member.delete` · `PRJ(A)` | 204 | – | I6 | CE-API-012 |
| EP-0586 | A05:V-MOD-11 | `GET {V1P}/archived-modules/` | `ModuleArchiveUnarchiveAPIEndpoint.get` (V1V/module.py:1056) | `V1ModuleEndpoints` → `ListArchivedModulesQuery` | `project.module.read_archived` · `PRJ(A,M,G)` | 200 | – | I6 | CE-API-032 |
| EP-0587 | A05:V-MOD-12 | `DELETE {V1P}/archived-modules/{pk}/unarchive/` | `ModuleArchiveUnarchiveAPIEndpoint.delete` (V1V/module.py:1118) | `V1ModuleEndpoints` → `UnarchiveModuleCommand` | `project.module.unarchive` · `PRJ(A,M)` | 204 | – | I6 | CE-API-032 |
| EP-0588 | A05:V-MOD-03 | `GET {V1P}/modules-lite/` | `ModuleListLiteAPIEndpoint.get` (V1V/module.py:303) | `V1ModuleEndpoints` → `ListModulesLiteQuery` | `project.module.read` · `PRJ(A,M,G)` | 200 | – | I6 | CE-API-030 |
| EP-0589 | A05:V-MOD-01 | `GET {V1P}/modules/` | `ModuleListCreateAPIEndpoint.get` (V1V/module.py:266) | `V1ModuleEndpoints` → `ListModulesQuery` | `project.module.read` · `PRJ(A,M,G)` | 200 | – | I6 | CE-API-030 |
| EP-0590 | A05:V-MOD-02 | `POST {V1P}/modules/` | `ModuleListCreateAPIEndpoint.post` (V1V/module.py:194) | `V1ModuleEndpoints` → `CreateModuleCommand` | `project.module.create` · `PRJ(A,M)` | 201 | – | I6 | CE-API-030 |
| EP-0591 | A05:V-MOD-04 | `GET {V1P}/modules/{pk}/` | `ModuleDetailAPIEndpoint.get` (V1V/module.py:518) | `V1ModuleEndpoints` → `GetModuleQuery` | `project.module.read` · `PRJ(A,M,G)` | 200 | – | I6 | CE-API-030 |
| EP-0592 | A05:V-MOD-05 | `PATCH {V1P}/modules/{pk}/` | `ModuleDetailAPIEndpoint.patch` (V1V/module.py:452) | `V1ModuleEndpoints` → `UpdateModuleCommand` | `project.module.update` · `PRJ(A,M)` | 200 | – | I6 | CE-API-030 |
| EP-0593 | A05:V-MOD-06 | `DELETE {V1P}/modules/{pk}/` | `ModuleDetailAPIEndpoint.delete` (V1V/module.py:540) | `V1ModuleEndpoints` → `DeleteModuleCommand` | `project.module.delete` · `PRJ(A)+C:Module` | 204 | SEC-20 | I6 | CE-API-030 |
| EP-0594 | A05:V-MOD-10 | `POST {V1P}/modules/{pk}/archive/` | `ModuleArchiveUnarchiveAPIEndpoint.post` (V1V/module.py:1084) | `V1ModuleEndpoints` → `ArchiveModuleCommand` | `project.module.archive` · `PRJ(A,M)` | 204 | – | I6 | CE-API-032 |
| EP-0595 | A05:V-MOD-07 | `GET {V1P}/modules/{module_id}/module-issues/` | `ModuleIssueListCreateAPIEndpoint.get` (V1V/module.py:644) | `V1ModuleWorkItemEndpoints` → `ListModuleWorkItemsQuery` | `project.module_work_item.read` · `PRJ(A,M)` | 200 | HARM-02 | I6 | CE-API-031 |
| EP-0596 | A05:V-MOD-08 | `POST {V1P}/modules/{module_id}/module-issues/` | `ModuleIssueListCreateAPIEndpoint.post` (V1V/module.py:712) | `V1ModuleWorkItemEndpoints` → `AddModuleWorkItemsCommand` | `project.module_work_item.create` · `PRJ(A,M)` | 200 | DT-MOD-01 | I6 | CE-API-031 |
| EP-0597 | A05:V-MOD-09 | `DELETE {V1P}/modules/{module_id}/module-issues/{issue_id}/` | `ModuleIssueDetailAPIEndpoint.delete` (V1V/module.py:914) | `V1ModuleWorkItemEndpoints` → `RemoveModuleWorkItemCommand` | `project.module_work_item.delete` · `PRJ(A,M)` | 204 | – | I6 | CE-API-031 |
| EP-0598 | A05:V-PRJ-03 | `GET {V1W}/projects-lite/` | `ProjectListLiteAPIEndpoint.get` (V1V/project.py:394) | `V1ProjectEndpoints` → `ListProjectsLiteQuery` | `workspace.project.read` · `WS(A,M,G)` | 200 | – | I6 | CE-API-006 |
| EP-0599 | A05:V-PRJ-01 | `GET {V1W}/projects/` | `ProjectListCreateAPIEndpoint.get` (V1V/project.py:167) | `V1ProjectEndpoints` → `ListProjectsQuery` | `workspace.project.read` · `WS(A,M,G)` | 200 | – | I6 | CE-API-006 |
| EP-0600 | A05:V-PRJ-02 | `POST {V1W}/projects/` | `ProjectListCreateAPIEndpoint.post` (V1V/project.py:224) | `V1ProjectEndpoints` → `CreateProjectCommand` | `workspace.project.create` · `WS(A,M)` | 201 | – | I6 | CE-API-006 |
| EP-0601 | A05:V-PRJ-04 | `GET {V1W}/projects/{pk}/` | `ProjectDetailAPIEndpoint.get` (V1V/project.py:516) | `V1ProjectEndpoints` → `GetProjectQuery` | `project.project.read` · `WS(A,M,G)` | 200 | – | I6 | CE-API-006 |
| EP-0602 | A05:V-PRJ-05 | `PATCH {V1W}/projects/{pk}/` | `ProjectDetailAPIEndpoint.patch` (V1V/project.py:546) | `V1ProjectEndpoints` → `UpdateProjectCommand` | `project.project.update` · `WSA\|PA` | 200 | HARM-06, DT-V1-11 | I6 | CE-API-006 |
| EP-0603 | A05:V-PRJ-06 | `DELETE {V1W}/projects/{pk}/` | `ProjectDetailAPIEndpoint.delete` (V1V/project.py:623) | `V1ProjectEndpoints` → `DeleteProjectCommand` | `project.project.delete` · `WSA\|PA` | 204 | HARM-06 | I6 | CE-API-006 |
| EP-0604 | A05:V-PRJ-07 | `POST {V1P}/archive/` | `ProjectArchiveUnarchiveAPIEndpoint.post` (V1V/project.py:666) | `V1ProjectEndpoints` → `ArchiveProjectCommand` | `project.project.archive` · `PRJ(A,M)` | 204 | HARM-05 | I6 | CE-API-007 |
| EP-0605 | A05:V-PRJ-08 | `DELETE {V1P}/archive/` | `ProjectArchiveUnarchiveAPIEndpoint.delete` (V1V/project.py:690) | `V1ProjectEndpoints` → `UnarchiveProjectCommand` | `project.project.unarchive` · `PRJ(A,M)` | 204 | HARM-05 | I6 | CE-API-007 |
| EP-0606 | A05:V-PRJ-09 | `GET {V1P}/summary/` | `ProjectSummaryAPIEndpoint.get` (V1V/project.py:718) | `V1ProjectEndpoints` → `GetProjectSummaryQuery` | `project.project.read_summary` · `PRJ(A,M)` | 200 | SEC-10 | I6 | CE-API-008 |
| EP-0607 | A05:V-STA-01 | `GET {V1P}/states/` | `StateListCreateAPIEndpoint.get` (V1V/state.py:155) | `V1StateEndpoints` → `ListStatesQuery` | `project.state.read` · `PRJ(A,M,G)` | 200 | – | I6 | CE-API-009 |
| EP-0608 | A05:V-STA-02 | `POST {V1P}/states/` | `StateListCreateAPIEndpoint.post` (V1V/state.py:86) | `V1StateEndpoints` → `CreateStateCommand` | `project.state.create` · `PRJ(A)` | 200 | – | I6 | CE-API-009 |
| EP-0609 | A05:V-STA-03 | `GET {V1P}/states/{state_id}/` | `StateDetailAPIEndpoint.get` (V1V/state.py:211) | `V1StateEndpoints` → `GetStateQuery` | `project.state.read` · `PRJ(A,M,G)` | 200 | – | I6 | CE-API-009 |
| EP-0610 | A05:V-STA-04 | `PATCH {V1P}/states/{state_id}/` | `StateDetailAPIEndpoint.patch` (V1V/state.py:283) | `V1StateEndpoints` → `UpdateStateCommand` | `project.state.update` · `PRJ(A)` | 200 | – | I6 | CE-API-009 |
| EP-0611 | A05:V-STA-05 | `DELETE {V1P}/states/{state_id}/` | `StateDetailAPIEndpoint.delete` (V1V/state.py:236) | `V1StateEndpoints` → `DeleteStateCommand` | `project.state.delete` · `PRJ(A)` | 204 | – | I6 | CE-API-009 |
| EP-0612 | A05:V-STK-01 | `GET {V1W}/stickies/` | `StickyViewSet.list` (V1V/sticky.py) | `V1StickyEndpoints` → `ListStickiesQuery` | `workspace.sticky.read` · `WS(A,M,G)+OWN` | 200 | DT-V1-05 | I6 | CE-API-014 |
| EP-0613 | A05:V-STK-02 | `POST {V1W}/stickies/` | `StickyViewSet.create` (V1V/sticky.py) | `V1StickyEndpoints` → `CreateStickyCommand` | `workspace.sticky.create` · `WS(A,M,G)` | 201 | – | I6 | CE-API-014 |
| EP-0614 | A05:V-STK-03 | `GET {V1W}/stickies/{pk}/` | `StickyViewSet.retrieve` (V1V/sticky.py) | `V1StickyEndpoints` → `GetStickyQuery` | `workspace.sticky.read` · `WS(A,M,G)+OWN` | 200 | – | I6 | CE-API-014 |
| EP-0615 | A05:V-STK-04 | `PATCH {V1W}/stickies/{pk}/` | `StickyViewSet.partial_update` (V1V/sticky.py) | `V1StickyEndpoints` → `UpdateStickyCommand` | `workspace.sticky.update` · `WS(A,M,G)+C:Sticky` | 200 | SEC-13 | I6 | CE-API-014 |
| EP-0616 | A05:V-STK-06 | `DELETE {V1W}/stickies/{pk}/` | `StickyViewSet.destroy` (V1V/sticky.py) | `V1StickyEndpoints` → `DeleteStickyCommand` | `workspace.sticky.delete` · `WS(A,M,G)+C:Sticky` | 204 | SEC-13 | I6 | CE-API-014 |
| EP-0617 | A05:V-AST-01 | `POST /api/v1/assets/user-assets/` | `UserAssetEndpoint.post` (V1V/asset.py:112) | `V1UserAssetEndpoints` → `CreateUserAssetUploadCommand` | `user.user_asset.create` · `AUTH+SELF` | 200 | – | I6 | CE-API-015 |
| EP-0618 | A05:V-AST-04 | `POST /api/v1/assets/user-assets/server/` | `UserServerAssetEndpoint.post` (V1V/asset.py:284) | `V1UserAssetEndpoints` → `CreateUserServerAssetUploadCommand` | `user.user_asset.create` · `AUTH+SELF` | 500→200 | DT-V1-09 | I6 | CE-API-015 |
| EP-0619 | A05:V-AST-02 | `PATCH /api/v1/assets/user-assets/{asset_id}/` | `UserAssetEndpoint.patch` (V1V/asset.py:205) | `V1UserAssetEndpoints` → `ConfirmUserAssetUploadCommand` | `user.user_asset.update` · `AUTH+SELF` | 204 | – | I6 | CE-API-015 |
| EP-0620 | A05:V-AST-03 | `DELETE /api/v1/assets/user-assets/{asset_id}/` | `UserAssetEndpoint.delete` (V1V/asset.py:233) | `V1UserAssetEndpoints` → `DeleteUserAssetCommand` | `user.user_asset.delete` · `AUTH+SELF` | 204 | – | I6 | CE-API-015 |
| EP-0621 | A05:V-AST-05 | `PATCH /api/v1/assets/user-assets/{asset_id}/server/` | `UserServerAssetEndpoint.patch` (V1V/asset.py:361) | `V1UserAssetEndpoints` → `ConfirmUserServerAssetUploadCommand` | `user.user_asset.update` · `AUTH+SELF` | 204 | DT-V1-09 | I6 | CE-API-015 |
| EP-0622 | A05:V-AST-06 | `DELETE /api/v1/assets/user-assets/{asset_id}/server/` | `UserServerAssetEndpoint.delete` (V1V/asset.py:389) | `V1UserAssetEndpoints` → `DeleteUserServerAssetCommand` | `user.user_asset.delete` · `AUTH+SELF` | 204 | DT-V1-09 | I6 | CE-API-015 |
| EP-0623 | A05:V-ACT-01 | `GET {V1P}/issues/{issue_id}/activities/` | `IssueActivityListAPIEndpoint.get` (V1V/issue.py:1732) | `V1WorkItemActivityEndpoints` → `ListWorkItemActivitiesQuery` | `project.work_item_activity.read` · `PRJ(A,M,G)+VIS` | 200 | – | I6 | CE-API-022 |
| EP-0624 | A05:V-ACT-02 | `GET {V1P}/issues/{issue_id}/activities/{pk}/` | `IssueActivityDetailAPIEndpoint.get` (V1V/issue.py:1789) | `V1WorkItemActivityEndpoints` → `GetWorkItemActivityQuery` | `project.work_item_activity.read` · `PRJ(A,M,G)+VIS` | 200 | – | I6 | CE-API-022 |
| EP-0625 | A05:V-ACT-01 | `GET {V1P}/work-items/{issue_id}/activities/` | `IssueActivityListAPIEndpoint.get` (V1V/issue.py:1732) | `V1WorkItemActivityEndpoints` → `ListWorkItemActivitiesQuery` | `project.work_item_activity.read` · `PRJ(A,M,G)+VIS` | 200 | – | I6 | CE-API-022 |
| EP-0626 | A05:V-ACT-02 | `GET {V1P}/work-items/{issue_id}/activities/{pk}/` | `IssueActivityDetailAPIEndpoint.get` (V1V/issue.py:1789) | `V1WorkItemActivityEndpoints` → `GetWorkItemActivityQuery` | `project.work_item_activity.read` · `PRJ(A,M,G)+VIS` | 200 | – | I6 | CE-API-022 |
| EP-0627 | A05:V-ATT-01 | `GET {V1P}/issues/{issue_id}/issue-attachments/` | `IssueAttachmentListCreateAPIEndpoint.get` (V1V/issue.py:2024) | `V1WorkItemAttachmentEndpoints` → `ListWorkItemAttachmentsQuery` | `project.work_item_attachment.read` · `PRJ(A,M,G)+VIS` | 200 | SEC-08 | I6 | CE-API-023 |
| EP-0628 | A05:V-ATT-02 | `POST {V1P}/issues/{issue_id}/issue-attachments/` | `IssueAttachmentListCreateAPIEndpoint.post` (V1V/issue.py:1898) | `V1WorkItemAttachmentEndpoints` → `CreateWorkItemAttachmentUploadCommand` | `project.work_item_attachment.create` · `PRJ(A,M,G)` | 200 | SEC-08 | I6 | CE-API-023 |
| EP-0629 | A05:V-ATT-03 | `GET {V1P}/issues/{issue_id}/issue-attachments/{pk}/` | `IssueAttachmentDetailAPIEndpoint.get` (V1V/issue.py:2135) | `V1WorkItemAttachmentEndpoints` → `GetWorkItemAttachmentQuery` | `project.work_item_attachment.read` · `PRJ(A,M,G)+VIS` | 302 | SEC-08 | I6 | CE-API-023 |
| EP-0630 | A05:V-ATT-04 | `PATCH {V1P}/issues/{issue_id}/issue-attachments/{pk}/` | `IssueAttachmentDetailAPIEndpoint.patch` (V1V/issue.py:2197) | `V1WorkItemAttachmentEndpoints` → `ConfirmWorkItemAttachmentUploadCommand` | `project.work_item_attachment.update` · `PRJ(A,M,G)` | 204 | SEC-08 | I6 | CE-API-023 |
| EP-0631 | A05:V-ATT-05 | `DELETE {V1P}/issues/{issue_id}/issue-attachments/{pk}/` | `IssueAttachmentDetailAPIEndpoint.delete` (V1V/issue.py:2060) | `V1WorkItemAttachmentEndpoints` → `DeleteWorkItemAttachmentCommand` | `project.work_item_attachment.delete` · `PRJ(A)+C:FileAsset` | 204 | SEC-08 | I6 | CE-API-023 |
| EP-0632 | A05:V-ATT-01 | `GET {V1P}/work-items/{issue_id}/attachments/` | `IssueAttachmentListCreateAPIEndpoint.get` (V1V/issue.py:2024) | `V1WorkItemAttachmentEndpoints` → `ListWorkItemAttachmentsQuery` | `project.work_item_attachment.read` · `PRJ(A,M,G)+VIS` | 200 | SEC-08 | I6 | CE-API-023 |
| EP-0633 | A05:V-ATT-02 | `POST {V1P}/work-items/{issue_id}/attachments/` | `IssueAttachmentListCreateAPIEndpoint.post` (V1V/issue.py:1898) | `V1WorkItemAttachmentEndpoints` → `CreateWorkItemAttachmentUploadCommand` | `project.work_item_attachment.create` · `PRJ(A,M,G)` | 200 | SEC-08 | I6 | CE-API-023 |
| EP-0634 | A05:V-ATT-03 | `GET {V1P}/work-items/{issue_id}/attachments/{pk}/` | `IssueAttachmentDetailAPIEndpoint.get` (V1V/issue.py:2135) | `V1WorkItemAttachmentEndpoints` → `GetWorkItemAttachmentQuery` | `project.work_item_attachment.read` · `PRJ(A,M,G)+VIS` | 302 | SEC-08 | I6 | CE-API-023 |
| EP-0635 | A05:V-ATT-04 | `PATCH {V1P}/work-items/{issue_id}/attachments/{pk}/` | `IssueAttachmentDetailAPIEndpoint.patch` (V1V/issue.py:2197) | `V1WorkItemAttachmentEndpoints` → `ConfirmWorkItemAttachmentUploadCommand` | `project.work_item_attachment.update` · `PRJ(A,M,G)` | 204 | SEC-08 | I6 | CE-API-023 |
| EP-0636 | A05:V-ATT-05 | `DELETE {V1P}/work-items/{issue_id}/attachments/{pk}/` | `IssueAttachmentDetailAPIEndpoint.delete` (V1V/issue.py:2060) | `V1WorkItemAttachmentEndpoints` → `DeleteWorkItemAttachmentCommand` | `project.work_item_attachment.delete` · `PRJ(A)+C:FileAsset` | 204 | SEC-08 | I6 | CE-API-023 |
| EP-0637 | A05:V-CMT-01 | `GET {V1P}/issues/{issue_id}/comments/` | `IssueCommentListCreateAPIEndpoint.get` (V1V/issue.py:1433) | `V1WorkItemCommentEndpoints` → `ListWorkItemCommentsQuery` | `project.work_item_comment.read` · `PRJ(A,M,G)+VIS` | 200 | – | I6 | CE-API-021 |
| EP-0638 | A05:V-CMT-02 | `POST {V1P}/issues/{issue_id}/comments/` | `IssueCommentListCreateAPIEndpoint.post` (V1V/issue.py:1467) | `V1WorkItemCommentEndpoints` → `CreateWorkItemCommentCommand` | `project.work_item_comment.create` · `PRJ(A,M,G)` | 201 | – | I6 | CE-API-021 |
| EP-0639 | A05:V-CMT-03 | `GET {V1P}/issues/{issue_id}/comments/{pk}/` | `IssueCommentDetailAPIEndpoint.get` (V1V/issue.py:1585) | `V1WorkItemCommentEndpoints` → `GetWorkItemCommentQuery` | `project.work_item_comment.read` · `PRJ(A,M,G)+VIS` | 200 | – | I6 | CE-API-021 |
| EP-0640 | A05:V-CMT-04 | `PATCH {V1P}/issues/{issue_id}/comments/{pk}/` | `IssueCommentDetailAPIEndpoint.patch` (V1V/issue.py:1616) | `V1WorkItemCommentEndpoints` → `UpdateWorkItemCommentCommand` | `project.work_item_comment.update` · `PRJ(A)+C:IssueComment` | 200 | SEC-09 | I6 | CE-API-021 |
| EP-0641 | A05:V-CMT-05 | `DELETE {V1P}/issues/{issue_id}/comments/{pk}/` | `IssueCommentDetailAPIEndpoint.delete` (V1V/issue.py:1685) | `V1WorkItemCommentEndpoints` → `DeleteWorkItemCommentCommand` | `project.work_item_comment.delete` · `PRJ(A)+C:IssueComment` | 204 | SEC-09 | I6 | CE-API-021 |
| EP-0642 | A05:V-CMT-01 | `GET {V1P}/work-items/{issue_id}/comments/` | `IssueCommentListCreateAPIEndpoint.get` (V1V/issue.py:1433) | `V1WorkItemCommentEndpoints` → `ListWorkItemCommentsQuery` | `project.work_item_comment.read` · `PRJ(A,M,G)+VIS` | 200 | – | I6 | CE-API-021 |
| EP-0643 | A05:V-CMT-02 | `POST {V1P}/work-items/{issue_id}/comments/` | `IssueCommentListCreateAPIEndpoint.post` (V1V/issue.py:1467) | `V1WorkItemCommentEndpoints` → `CreateWorkItemCommentCommand` | `project.work_item_comment.create` · `PRJ(A,M,G)` | 201 | – | I6 | CE-API-021 |
| EP-0644 | A05:V-CMT-03 | `GET {V1P}/work-items/{issue_id}/comments/{pk}/` | `IssueCommentDetailAPIEndpoint.get` (V1V/issue.py:1585) | `V1WorkItemCommentEndpoints` → `GetWorkItemCommentQuery` | `project.work_item_comment.read` · `PRJ(A,M,G)+VIS` | 200 | – | I6 | CE-API-021 |
| EP-0645 | A05:V-CMT-04 | `PATCH {V1P}/work-items/{issue_id}/comments/{pk}/` | `IssueCommentDetailAPIEndpoint.patch` (V1V/issue.py:1616) | `V1WorkItemCommentEndpoints` → `UpdateWorkItemCommentCommand` | `project.work_item_comment.update` · `PRJ(A)+C:IssueComment` | 200 | SEC-09 | I6 | CE-API-021 |
| EP-0646 | A05:V-CMT-05 | `DELETE {V1P}/work-items/{issue_id}/comments/{pk}/` | `IssueCommentDetailAPIEndpoint.delete` (V1V/issue.py:1685) | `V1WorkItemCommentEndpoints` → `DeleteWorkItemCommentCommand` | `project.work_item_comment.delete` · `PRJ(A)+C:IssueComment` | 204 | SEC-09 | I6 | CE-API-021 |
| EP-0647 | A05:V-WI-06 | `GET {V1W}/issues/{project_identifier}-{issue_identifier}/` | `WorkspaceIssueAPIEndpoint.get` (V1V/issue.py:236) | `V1WorkItemEndpoints` → `GetWorkItemByIdentifierQuery` | `project.work_item.read` · `PRJ(A,M,G)+VIS` | 200 | – | I6 | CE-API-018 |
| EP-0648 | A05:V-WI-01 | `GET {V1P}/issues/` | `IssueListCreateAPIEndpoint.get` (V1V/issue.py:317) | `V1WorkItemEndpoints` → `ListWorkItemsQuery` | `project.work_item.read` · `PRJ(A,M,G)+VIS` | 200 | – | I6 | CE-API-017 |
| EP-0649 | A05:V-WI-02 | `POST {V1P}/issues/` | `IssueListCreateAPIEndpoint.post` (V1V/issue.py:456) | `V1WorkItemEndpoints` → `CreateWorkItemCommand` | `project.work_item.create` · `PRJ(A,M)` | 201 | – | I6 | CE-API-017 |
| EP-0650 | A05:V-WI-03 | `GET {V1P}/issues/{pk}/` | `IssueDetailAPIEndpoint.get` (V1V/issue.py:582) | `V1WorkItemEndpoints` → `GetWorkItemQuery` | `project.work_item.read` · `PRJ(A,M,G)+VIS` | 200 | – | I6 | CE-API-017 |
| EP-0651 | A05:V-WI-04 | `PATCH {V1P}/issues/{pk}/` | `IssueDetailAPIEndpoint.patch` (V1V/issue.py:778) | `V1WorkItemEndpoints` → `UpdateWorkItemCommand` | `project.work_item.update` · `PRJ(A,M)` | 200 | – | I6 | CE-API-017 |
| EP-0652 | A05:V-WI-05 | `DELETE {V1P}/issues/{pk}/` | `IssueDetailAPIEndpoint.delete` (V1V/issue.py:852) | `V1WorkItemEndpoints` → `DeleteWorkItemCommand` | `project.work_item.delete` · `PRJ(A)+C:Issue` | 204 | SEC-14 | I6 | CE-API-017 |
| EP-0653 | A05:V-WI-01 | `GET {V1P}/work-items/` | `IssueListCreateAPIEndpoint.get` (V1V/issue.py:317) | `V1WorkItemEndpoints` → `ListWorkItemsQuery` | `project.work_item.read` · `PRJ(A,M,G)+VIS` | 200 | – | I6 | CE-API-017 |
| EP-0654 | A05:V-WI-02 | `POST {V1P}/work-items/` | `IssueListCreateAPIEndpoint.post` (V1V/issue.py:456) | `V1WorkItemEndpoints` → `CreateWorkItemCommand` | `project.work_item.create` · `PRJ(A,M)` | 201 | – | I6 | CE-API-017 |
| EP-0655 | A05:V-WI-03 | `GET {V1P}/work-items/{pk}/` | `IssueDetailAPIEndpoint.get` (V1V/issue.py:582) | `V1WorkItemEndpoints` → `GetWorkItemQuery` | `project.work_item.read` · `PRJ(A,M,G)+VIS` | 200 | – | I6 | CE-API-017 |
| EP-0656 | A05:V-WI-04 | `PATCH {V1P}/work-items/{pk}/` | `IssueDetailAPIEndpoint.patch` (V1V/issue.py:778) | `V1WorkItemEndpoints` → `UpdateWorkItemCommand` | `project.work_item.update` · `PRJ(A,M)` | 200 | – | I6 | CE-API-017 |
| EP-0657 | A05:V-WI-05 | `DELETE {V1P}/work-items/{pk}/` | `IssueDetailAPIEndpoint.delete` (V1V/issue.py:852) | `V1WorkItemEndpoints` → `DeleteWorkItemCommand` | `project.work_item.delete` · `PRJ(A)+C:Issue` | 204 | SEC-14 | I6 | CE-API-017 |
| EP-0658 | A05:V-WI-06 | `GET {V1W}/work-items/{project_identifier}-{issue_identifier}/` | `WorkspaceIssueAPIEndpoint.get` (V1V/issue.py:236) | `V1WorkItemEndpoints` → `GetWorkItemByIdentifierQuery` | `project.work_item.read` · `PRJ(A,M,G)+VIS` | 200 | – | I6 | CE-API-018 |
| EP-0659 | A05:V-LNK-01 | `GET {V1P}/issues/{issue_id}/links/` | `IssueLinkListCreateAPIEndpoint.get` (V1V/issue.py:1171) | `V1WorkItemLinkEndpoints` → `ListWorkItemLinksQuery` | `project.work_item_link.read` · `PRJ(A,M,G)` | 200 | – | I6 | CE-API-020 |
| EP-0660 | A05:V-LNK-02 | `POST {V1P}/issues/{issue_id}/links/` | `IssueLinkListCreateAPIEndpoint.post` (V1V/issue.py:1204) | `V1WorkItemLinkEndpoints` → `CreateWorkItemLinkCommand` | `project.work_item_link.create` · `PRJ(A,M)` | 201 | – | I6 | CE-API-020 |
| EP-0661 | A05:V-LNK-03 | `GET {V1P}/issues/{issue_id}/links/{pk}/` | `IssueLinkDetailAPIEndpoint.get` (V1V/issue.py:1276) | `V1WorkItemLinkEndpoints` → `GetWorkItemLinkQuery` | `project.work_item_link.read` · `PRJ(A,M,G)` | 200 | – | I6 | CE-API-020 |
| EP-0662 | A05:V-LNK-04 | `PATCH {V1P}/issues/{issue_id}/links/{pk}/` | `IssueLinkDetailAPIEndpoint.patch` (V1V/issue.py:1316) | `V1WorkItemLinkEndpoints` → `UpdateWorkItemLinkCommand` | `project.work_item_link.update` · `PRJ(A,M)` | 200 | – | I6 | CE-API-020 |
| EP-0663 | A05:V-LNK-05 | `DELETE {V1P}/issues/{issue_id}/links/{pk}/` | `IssueLinkDetailAPIEndpoint.delete` (V1V/issue.py:1357) | `V1WorkItemLinkEndpoints` → `DeleteWorkItemLinkCommand` | `project.work_item_link.delete` · `PRJ(A,M)` | 204 | – | I6 | CE-API-020 |
| EP-0664 | A05:V-LNK-01 | `GET {V1P}/work-items/{issue_id}/links/` | `IssueLinkListCreateAPIEndpoint.get` (V1V/issue.py:1171) | `V1WorkItemLinkEndpoints` → `ListWorkItemLinksQuery` | `project.work_item_link.read` · `PRJ(A,M,G)` | 200 | – | I6 | CE-API-020 |
| EP-0665 | A05:V-LNK-02 | `POST {V1P}/work-items/{issue_id}/links/` | `IssueLinkListCreateAPIEndpoint.post` (V1V/issue.py:1204) | `V1WorkItemLinkEndpoints` → `CreateWorkItemLinkCommand` | `project.work_item_link.create` · `PRJ(A,M)` | 201 | – | I6 | CE-API-020 |
| EP-0666 | A05:V-LNK-03 | `GET {V1P}/work-items/{issue_id}/links/{pk}/` | `IssueLinkDetailAPIEndpoint.get` (V1V/issue.py:1276) | `V1WorkItemLinkEndpoints` → `GetWorkItemLinkQuery` | `project.work_item_link.read` · `PRJ(A,M,G)` | 200 | – | I6 | CE-API-020 |
| EP-0667 | A05:V-LNK-04 | `PATCH {V1P}/work-items/{issue_id}/links/{pk}/` | `IssueLinkDetailAPIEndpoint.patch` (V1V/issue.py:1316) | `V1WorkItemLinkEndpoints` → `UpdateWorkItemLinkCommand` | `project.work_item_link.update` · `PRJ(A,M)` | 200 | – | I6 | CE-API-020 |
| EP-0668 | A05:V-LNK-05 | `DELETE {V1P}/work-items/{issue_id}/links/{pk}/` | `IssueLinkDetailAPIEndpoint.delete` (V1V/issue.py:1357) | `V1WorkItemLinkEndpoints` → `DeleteWorkItemLinkCommand` | `project.work_item_link.delete` · `PRJ(A,M)` | 204 | – | I6 | CE-API-020 |
| EP-0669 | A05:V-REL-01 | `GET {V1P}/work-items/{issue_id}/relations/` | `IssueRelationListCreateAPIEndpoint.get` (V1V/issue.py:2394) | `V1WorkItemRelationEndpoints` → `ListWorkItemRelationsQuery` | `project.work_item_relation.read` · `PRJ(A,M,G)` | 200 | DT-WI-03 | I6 | CE-API-024 |
| EP-0670 | A05:V-REL-02 | `POST {V1P}/work-items/{issue_id}/relations/` | `IssueRelationListCreateAPIEndpoint.post` (V1V/issue.py:2529) | `V1WorkItemRelationEndpoints` → `CreateWorkItemRelationsCommand` | `project.work_item_relation.create` · `PRJ(A,M)` | 201 | DT-WI-03 | I6 | CE-API-024 |
| EP-0671 | A05:V-WI-07 | `GET {V1W}/issues/search/` | `IssueSearchEndpoint.get` (V1V/issue.py:2274) | `V1WorkItemSearchEndpoints` → `SearchWorkItemsQuery` | `workspace.search.read` · `WS(A,M,G)+VIS` | 200 | DT-V1-10 | I6 | CE-API-019 |
| EP-0672 | A05:V-WI-07 | `GET {V1W}/work-items/search/` | `IssueSearchEndpoint.get` (V1V/issue.py:2274) | `V1WorkItemSearchEndpoints` → `SearchWorkItemsQuery` | `workspace.search.read` · `WS(A,M,G)+VIS` | 200 | DT-V1-10 | I6 | CE-API-019 |
| EP-0679 | A05:V-RTR-01 | `GET {V1W}/` | DRF `APIRootView` (DefaultRouter) | — (nicht registriert (Router-Nebenprodukt)) | – | 401→404 | DT-V1-03 | I6 | CE-API-001 |
| EP-0683 | A05:V-INV-05 | `PUT {V1W}/invitations/{pk}/` | `WorkspaceInvitationsViewset.update` (V1V/invite.py, geerbt) | — (entfällt (PUT-Duplikat)) | – | 200→405 | DT-GEN-01 | I6 | CE-API-013 |
| EP-0710 | A05:V-STK-05 | `PUT {V1W}/stickies/{pk}/` | `StickyViewSet.update` (V1V/sticky.py, geerbt) | — (entfällt (PUT-Duplikat)) | – | 200→405 | DT-GEN-01 | I6 | CE-API-014 |
| EP-0711 | A05:W-03 | `GET /api/schema/` | drf-spectacular (`ENABLE_DRF_SPECTACULAR=1`) | `OpenApiEndpoints` → `OpenApiDocumentEndpoint(v1)` | (anonym, nur mit Plane:OpenApi:Enabled) | 200 | DT-V1-04 | I6 | CE-API-004 |
| EP-0712 | A05:W-05 | `GET /api/schema/redoc/` | drf-spectacular (`ENABLE_DRF_SPECTACULAR=1`) | `OpenApiEndpoints` → `ScalarUi` | (anonym, nur mit Plane:OpenApi:Enabled) | 200 | DT-V1-04 | I6 | CE-API-004 |
| EP-0713 | A05:W-04 | `GET /api/schema/swagger-ui/` | drf-spectacular (`ENABLE_DRF_SPECTACULAR=1`) | `OpenApiEndpoints` → `ScalarUi` | (anonym, nur mit Plane:OpenApi:Enabled) | 200 | DT-V1-04 | I6 | CE-API-004 |
| EP-0732 | neu: D04-ADR-14 | `GET /api/schema/internal/` | – (neu) | `OpenApiEndpoints` → `OpenApiDocumentEndpoint(internal)` | (anonym, nur Development/Test) | 200 | – | I0 | CE-API-004 |

### 4.20 `Plane.Webhooks` – Webhook-Verwaltung

Ablage der Endpoint-Klassen: `src/modules/Webhooks/Plane.Webhooks/Endpoints/App/<Klasse>.cs`. 7 Zeilen, davon 7 registriert und 0 nicht registriert (Entscheidung in Spalte „Abw./DT“).

| EP | Original-ID | Methode · Pfad (Original) | Original-View (Datei) | Ziel: Klasse → Handler | Permission · Ziel-Prüfung | Status Orig→Ziel | Abw./DT | Ink. | CE-IDs |
|---|---|---|---|---|---|---|---|---|---|
| EP-0714 | A03:WH-07 | `GET {W}/webhook-logs/{webhook_id}/` | `WebhookLogsEndpoint.get` (V/webhook/base.py:126) | `WebhookEndpoints` → `ListWebhookLogsQuery` | `workspace.webhook.read` · `WS(A)` | 200 | DT-WH-05 | I6 | CE-WH-010 |
| EP-0715 | A03:WH-01 | `GET {W}/webhooks/` | `WebhookEndpoint.get` (V/webhook/base.py:42) | `WebhookEndpoints` → `ListWebhooksQuery` | `workspace.webhook.read` · `WS(A)` | 200 | – | I6 | CE-WH-002 |
| EP-0716 | A03:WH-02 | `POST {W}/webhooks/` | `WebhookEndpoint.post` (V/webhook/base.py:22) | `WebhookEndpoints` → `CreateWebhookCommand` | `workspace.webhook.create` · `WS(A)` | 201 | DT-WH-08 | I6 | CE-WH-003, CE-WH-011 |
| EP-0717 | A03:WH-03 | `GET {W}/webhooks/{pk}/` | `WebhookEndpoint.get` (V/webhook/base.py:42) | `WebhookEndpoints` → `GetWebhookQuery` | `workspace.webhook.read` · `WS(A)` | 200 | – | I6 | CE-WH-004, CE-WH-005 |
| EP-0718 | A03:WH-04 | `PATCH {W}/webhooks/{pk}/` | `WebhookEndpoint.patch` (V/webhook/base.py:82) | `WebhookEndpoints` → `UpdateWebhookCommand` | `workspace.webhook.update` · `WS(A)` | 200 | DT-WH-08 | I6 | CE-WH-005, CE-WH-011 |
| EP-0719 | A03:WH-05 | `DELETE {W}/webhooks/{pk}/` | `WebhookEndpoint.delete` (V/webhook/base.py:108) | `WebhookEndpoints` → `DeleteWebhookCommand` | `workspace.webhook.delete` · `WS(A)` | 204 | – | I6 | CE-WH-006 |
| EP-0720 | A03:WH-06 | `POST {W}/webhooks/{pk}/regenerate/` | `WebhookSecretRegenerateEndpoint.post` (V/webhook/base.py:116) | `WebhookEndpoints` → `RegenerateWebhookSecretCommand` | `workspace.webhook.create` · `WS(A)` | 200 | – | I6 | CE-WH-004 |

### 4.21 `Plane.Exports` – Exporte

Ablage der Endpoint-Klassen: `src/modules/Exports/Plane.Exports/Endpoints/App/<Klasse>.cs`. 2 Zeilen, davon 2 registriert und 0 nicht registriert (Entscheidung in Spalte „Abw./DT“).

| EP | Original-ID | Methode · Pfad (Original) | Original-View (Datei) | Ziel: Klasse → Handler | Permission · Ziel-Prüfung | Status Orig→Ziel | Abw./DT | Ink. | CE-IDs |
|---|---|---|---|---|---|---|---|---|---|
| EP-0724 | A03:X-02 | `GET {W}/export-issues/` | `ExportIssuesEndpoint.get` (V/exporter/base.py:69) | `ExportEndpoints` → `ListExportsQuery` | `workspace.export.read` · `WS(A,M)` | 200 | – | I6 | CE-EXP-001, CE-EXP-002 |
| EP-0725 | A03:X-01 | `POST {W}/export-issues/` | `ExportIssuesEndpoint.post` (V/exporter/base.py:24) | `ExportEndpoints` → `CreateWorkItemExportCommand` | `workspace.export.create` · `WS(A,M)+VIS` | 200 | – | I6 | CE-EXP-001, CE-EXP-002 |

### 4.22 `Plane.Assistant` – KI-Assistent, Unsplash

Ablage der Endpoint-Klassen: `src/modules/Assistant/Plane.Assistant/Endpoints/App/<Klasse>.cs`. 3 Zeilen, davon 3 registriert und 0 nicht registriert (Entscheidung in Spalte „Abw./DT“).

| EP | Original-ID | Methode · Pfad (Original) | Original-View (Datei) | Ziel: Klasse → Handler | Permission · Ziel-Prüfung | Status Orig→Ziel | Abw./DT | Ink. | CE-IDs |
|---|---|---|---|---|---|---|---|---|---|
| EP-0726 | A03:EXT-03 | `POST {W}/ai-assistant/` | `WorkspaceGPTIntegrationEndpoint.post` (V/external/base.py:186) | `AiAssistantEndpoints` → `RunWorkspaceAiAssistantCommand` | `workspace.ai_assistant.use` · `WS(A,M)` | 200 | DT-AI-01 | I6 | CE-AI-001 |
| EP-0727 | A03:EXT-02 | `POST {P}/ai-assistant/` | `GPTIntegrationEndpoint.post` (V/external/base.py:150) | `AiAssistantEndpoints` → `RunProjectAiAssistantCommand` | `project.ai_assistant.use` · `PRJ(A,M)` | 200 | DT-AI-01 | I6 | CE-AI-001 |
| EP-0728 | A03:EXT-01 | `GET /api/unsplash/` | `UnsplashEndpoint.get` (V/external/base.py:216) | `UnsplashImageEndpoints` → `SearchUnsplashQuery` | `user.unsplash.read` · `AUTH+SELF` | 200 | DT-AI-01 | I6 | CE-AI-002 |

### 4.23 `Plane.BuildingBlocks.Web` – Integrations-Oberfläche `/api/integrations/` (🧱 F1)

Ablage der Endpoint-Klassen: `src/building-blocks/Plane.BuildingBlocks.Web/Integrations/<Klasse>.cs`. 1 Zeilen, davon 1 registriert und 0 nicht registriert (Entscheidung in Spalte „Abw./DT“).

| EP | Original-ID | Methode · Pfad (Original) | Original-View (Datei) | Ziel: Klasse → Handler | Permission · Ziel-Prüfung | Status Orig→Ziel | Abw./DT | Ink. | CE-IDs |
|---|---|---|---|---|---|---|---|---|---|
| EP-0729 | neu: F1 / D16-ADR-09 | `POST /api/integrations/{provider}/webhooks/{connection_id}/` | – (F1 / D16-ADR-09) | `IntegrationWebhookEndpoints` → `IntegrationWebhookEndpoint → IWebhookIngress` | (Signatur, IWebhookSignatureVerifier) | 202 | – | I0 | CE-OPS-018 |

### 4.24 `Plane.BuildingBlocks.Web` – Root-Oberfläche `/`

Ablage der Endpoint-Klassen: `src/building-blocks/Plane.BuildingBlocks.Web/Surfaces/RootEndpoints.cs<Klasse>.cs`. 2 Zeilen, davon 2 registriert und 0 nicht registriert (Entscheidung in Spalte „Abw./DT“).

| EP | Original-ID | Methode · Pfad (Original) | Original-View (Datei) | Ziel: Klasse → Handler | Permission · Ziel-Prüfung | Status Orig→Ziel | Abw./DT | Ink. | CE-IDs |
|---|---|---|---|---|---|---|---|---|---|
| EP-0730 | A05:W-01 | `GET /` | `health_check` (web/views.py) | `RootEndpoints` → `RootEndpoints.HealthOk` | (anonym) | 200 | – | I0 | CE-OPS-008 |
| EP-0731 | A05:W-02 | `GET /robots.txt` | `robots_txt` (web/views.py) | `RootEndpoints` → `RootEndpoints.RobotsTxt` | (anonym) | 200 | – | I0 | CE-OPS-008 |

### 4.25 Methoden-Nebenprodukte (nicht registriert; DT-GEN-03, DT-V1-01, DT-V1-02, DT-AUTH-01)

Kombinationen Methode × Pfad, die das Original technisch beantwortet (Django-`APIView`-Methoden auf allen der Klasse zugeordneten Routen), die aber keine fachliche Funktion haben. Alle sind in der Zielplattform nicht registriert; `RouteInventoryTests.NoByproductRoutes` prüft den Ziel-Status. Die Spalte „CE-IDs“ nennt die Ressource, zu der die Kombination gehört (die Funktion liegt auf der registrierten Schwester-Route).

| EP | Modul | Methode · Pfad | Original-Klasse.Aktion (Datei) | Original-Verhalten | Ziel | DT | CE-IDs |
|---|---|---|---|---|---|---|---|
| EP-0061 | Identity | `PATCH /api/users/api-tokens/` | `ApiTokenEndpoint.patch` (V/api.py:56) | 500 (TypeError, Methode ohne passende URL-Parameter) bzw. fachlich undefiniert | 405 | DT-GEN-03 | CE-WH-012 |
| EP-0062 | Identity | `DELETE /api/users/api-tokens/` | `ApiTokenEndpoint.delete` (V/api.py:51) | 500 (TypeError, Methode ohne passende URL-Parameter) bzw. fachlich undefiniert | 405 | DT-GEN-03 | CE-WH-014 |
| EP-0063 | Identity | `POST /api/users/api-tokens/{pk}/` | `ApiTokenEndpoint.post` (V/api.py:21) | 500 (TypeError, Methode ohne passende URL-Parameter) bzw. fachlich undefiniert | 405 | DT-GEN-03 | CE-WH-013 |
| EP-0065 | Identity | `DELETE /api/users/me/accounts/` | `AccountEndpoint.delete` (V/user/base.py:436) | 500 (TypeError, Methode ohne passende URL-Parameter) bzw. fachlich undefiniert | 404 | DT-AUTH-01 | CE-PROF-007 |
| EP-0085 | Instance | `DELETE {I}/admins/` | `InstanceAdminEndpoint.delete` (license/V1V/admin.py:85) | 500 (TypeError, Methode ohne passende URL-Parameter) bzw. fachlich undefiniert | 405 | DT-AUTH-01 | CE-INST-004 |
| EP-0089 | Instance | `GET {I}/admins/{pk}/` | `InstanceAdminEndpoint.get` (license/V1V/admin.py:73) | 500 (TypeError, Methode ohne passende URL-Parameter) bzw. fachlich undefiniert | 404 | DT-GEN-03 | CE-INST-004 |
| EP-0090 | Instance | `POST {I}/admins/{pk}/` | `InstanceAdminEndpoint.post` (license/V1V/admin.py:51) | 500 (TypeError, Methode ohne passende URL-Parameter) bzw. fachlich undefiniert | 404 | DT-AUTH-01 | CE-INST-004 |
| EP-0158 | Workspaces | `PATCH {W}/home-preferences/` | `WorkspaceHomePreferenceViewSet.patch` (V/workspace/home.py:68) | 500 (TypeError, Methode ohne passende URL-Parameter) bzw. fachlich undefiniert | 405 | DT-GEN-03 | CE-HOME-002 |
| EP-0159 | Workspaces | `GET {W}/home-preferences/{key}/` | `WorkspaceHomePreferenceViewSet.get` (V/workspace/home.py:24) | 500 (TypeError, Methode ohne passende URL-Parameter) bzw. fachlich undefiniert | 405 | DT-GEN-03 | CE-HOME-002 |
| EP-0164 | Workspaces | `PATCH {W}/user-favorites/` | `WorkspaceFavoriteEndpoint.patch` (V/workspace/favorite.py:79) | 500 (TypeError, Methode ohne passende URL-Parameter) bzw. fachlich undefiniert | 405 | DT-GEN-03 | CE-WS-023 |
| EP-0165 | Workspaces | `DELETE {W}/user-favorites/` | `WorkspaceFavoriteEndpoint.delete` (V/workspace/favorite.py:90) | 500 (TypeError, Methode ohne passende URL-Parameter) bzw. fachlich undefiniert | 405 | DT-GEN-03 | CE-WS-023 |
| EP-0166 | Workspaces | `GET {W}/user-favorites/{favorite_id}/` | `WorkspaceFavoriteEndpoint.get` (V/workspace/favorite.py:25) | 500 (TypeError, Methode ohne passende URL-Parameter) bzw. fachlich undefiniert | 405 | DT-GEN-03 | CE-WS-023 |
| EP-0167 | Workspaces | `POST {W}/user-favorites/{favorite_id}/` | `WorkspaceFavoriteEndpoint.post` (V/workspace/favorite.py:39) | 500 (TypeError, Methode ohne passende URL-Parameter) bzw. fachlich undefiniert | 405 | DT-GEN-03 | CE-WS-023 |
| EP-0289 | WorkItems | `PATCH {AV2}/workspaces/{slug}/projects/{project_id}/issues/{issue_id}/attachments/` | `IssueAttachmentV2Endpoint.patch` (V/issue/attachment.py:211) | 500 (TypeError, Methode ohne passende URL-Parameter) bzw. fachlich undefiniert | 405 | DT-GEN-03 | CE-WI-036, CE-OPS-012 |
| EP-0290 | WorkItems | `DELETE {AV2}/workspaces/{slug}/projects/{project_id}/issues/{issue_id}/attachments/` | `IssueAttachmentV2Endpoint.delete` (V/issue/attachment.py:155) | 500 (TypeError, Methode ohne passende URL-Parameter) bzw. fachlich undefiniert | 405 | DT-GEN-03 | CE-WI-036, CE-OPS-012 |
| EP-0291 | WorkItems | `POST {AV2}/workspaces/{slug}/projects/{project_id}/issues/{issue_id}/attachments/{pk}/` | `IssueAttachmentV2Endpoint.post` (V/issue/attachment.py:102) | 500 (TypeError, Methode ohne passende URL-Parameter) bzw. fachlich undefiniert | 405 | DT-GEN-03 | CE-WI-036, CE-OPS-012 |
| EP-0293 | WorkItems | `DELETE {P}/issues/{issue_id}/issue-attachments/` | `IssueAttachmentEndpoint.delete` (V/issue/attachment.py:65) | 500 (TypeError, Methode ohne passende URL-Parameter) bzw. fachlich undefiniert | 405 | DT-GEN-03 | CE-WI-036 |
| EP-0295 | WorkItems | `POST {P}/issues/{issue_id}/issue-attachments/{pk}/` | `IssueAttachmentEndpoint.post` (V/issue/attachment.py:38) | 500 (TypeError, Methode ohne passende URL-Parameter) bzw. fachlich undefiniert | 405 | DT-GEN-03 | CE-WI-036 |
| EP-0328 | Cycles | `POST {P}/archived-cycles/` | `CycleArchiveUnarchiveEndpoint.post` (V/cycle/archive.py:587) | 500 (TypeError, Methode ohne passende URL-Parameter) bzw. fachlich undefiniert | 405 | DT-GEN-03 | CE-CYC-012 |
| EP-0329 | Cycles | `DELETE {P}/archived-cycles/` | `CycleArchiveUnarchiveEndpoint.delete` (V/cycle/archive.py:607) | 500 (TypeError, Methode ohne passende URL-Parameter) bzw. fachlich undefiniert | 405 | DT-GEN-03 | CE-CYC-012 |
| EP-0332 | Cycles | `GET {P}/cycles/{cycle_id}/archive/` | `CycleArchiveUnarchiveEndpoint.get` (V/cycle/archive.py:272) | 500 (TypeError, Methode ohne passende URL-Parameter) bzw. fachlich undefiniert | 405 | DT-GEN-03 | CE-CYC-012 |
| EP-0355 | ProjectModules | `POST {P}/archived-modules/` | `ModuleArchiveUnarchiveEndpoint.post` (V/module/archive.py:544) | 500 (TypeError, Methode ohne passende URL-Parameter) bzw. fachlich undefiniert | 405 | DT-GEN-03 | CE-MOD-009 |
| EP-0356 | ProjectModules | `DELETE {P}/archived-modules/` | `ModuleArchiveUnarchiveEndpoint.delete` (V/module/archive.py:561) | 500 (TypeError, Methode ohne passende URL-Parameter) bzw. fachlich undefiniert | 405 | DT-GEN-03 | CE-MOD-009 |
| EP-0357 | ProjectModules | `POST {P}/archived-modules/{pk}/` | `ModuleArchiveUnarchiveEndpoint.post` (V/module/archive.py:544) | 500 (TypeError, Methode ohne passende URL-Parameter) bzw. fachlich undefiniert | 405 | DT-GEN-03 | CE-MOD-009 |
| EP-0358 | ProjectModules | `DELETE {P}/archived-modules/{pk}/` | `ModuleArchiveUnarchiveEndpoint.delete` (V/module/archive.py:561) | 500 (TypeError, Methode ohne passende URL-Parameter) bzw. fachlich undefiniert | 405 | DT-GEN-03 | CE-MOD-009 |
| EP-0359 | ProjectModules | `GET {P}/modules/{module_id}/archive/` | `ModuleArchiveUnarchiveEndpoint.get` (V/module/archive.py:258) | 500 (TypeError, Methode ohne passende URL-Parameter) bzw. fachlich undefiniert | 405 | DT-GEN-03 | CE-MOD-009 |
| EP-0435 | Assets | `PATCH {AV2}/user-assets/` | `UserAssetsV2Endpoint.patch` (V/asset/v2.py:212) | 500 (TypeError, Methode ohne passende URL-Parameter) bzw. fachlich undefiniert | 405 | DT-GEN-03 | CE-PROF-003, CE-OPS-013 |
| EP-0436 | Assets | `DELETE {AV2}/user-assets/` | `UserAssetsV2Endpoint.delete` (V/asset/v2.py:233) | 500 (TypeError, Methode ohne passende URL-Parameter) bzw. fachlich undefiniert | 405 | DT-GEN-03 | CE-PROF-003, CE-OPS-013 |
| EP-0437 | Assets | `POST {AV2}/user-assets/{asset_id}/` | `UserAssetsV2Endpoint.post` (V/asset/v2.py:151) | 500 (TypeError, Methode ohne passende URL-Parameter) bzw. fachlich undefiniert | 405 | DT-GEN-03 | CE-PROF-003, CE-OPS-013 |
| EP-0438 | Assets | `GET {AV2}/workspaces/{slug}/` | `WorkspaceFileAssetEndpoint.get` (V/asset/v2.py:512) | 500 (TypeError, Methode ohne passende URL-Parameter) bzw. fachlich undefiniert | 405 | DT-GEN-03 | CE-WS-003, CE-OPS-012, CE-OPS-013 |
| EP-0439 | Assets | `PATCH {AV2}/workspaces/{slug}/` | `WorkspaceFileAssetEndpoint.patch` (V/asset/v2.py:458) | 500 (TypeError, Methode ohne passende URL-Parameter) bzw. fachlich undefiniert | 405 | DT-GEN-03 | CE-WS-003, CE-OPS-012, CE-OPS-013 |
| EP-0440 | Assets | `DELETE {AV2}/workspaces/{slug}/` | `WorkspaceFileAssetEndpoint.delete` (V/asset/v2.py:491) | 500 (TypeError, Methode ohne passende URL-Parameter) bzw. fachlich undefiniert | 405 | DT-GEN-03 | CE-WS-003, CE-OPS-012, CE-OPS-013 |
| EP-0441 | Assets | `GET {AV2}/workspaces/{slug}/projects/{project_id}/` | `ProjectAssetEndpoint.get` (V/asset/v2.py:737) | 500 (TypeError, Methode ohne passende URL-Parameter) bzw. fachlich undefiniert | 405 | DT-GEN-03 | CE-PAGE-032, CE-OPS-012, CE-OPS-013 |
| EP-0442 | Assets | `PATCH {AV2}/workspaces/{slug}/projects/{project_id}/` | `ProjectAssetEndpoint.patch` (V/asset/v2.py:700) | 500 (TypeError, Methode ohne passende URL-Parameter) bzw. fachlich undefiniert | 405 | DT-GEN-03 | CE-PAGE-032, CE-OPS-012, CE-OPS-013 |
| EP-0443 | Assets | `DELETE {AV2}/workspaces/{slug}/projects/{project_id}/` | `ProjectAssetEndpoint.delete` (V/asset/v2.py:721) | 500 (TypeError, Methode ohne passende URL-Parameter) bzw. fachlich undefiniert | 405 | DT-GEN-03 | CE-PAGE-032, CE-OPS-012, CE-OPS-013 |
| EP-0444 | Assets | `POST {AV2}/workspaces/{slug}/projects/{project_id}/{pk}/` | `ProjectAssetEndpoint.post` (V/asset/v2.py:633) | 500 (TypeError, Methode ohne passende URL-Parameter) bzw. fachlich undefiniert | 405 | DT-GEN-03 | CE-PAGE-032, CE-OPS-012, CE-OPS-013 |
| EP-0445 | Assets | `POST {AV2}/workspaces/{slug}/{asset_id}/` | `WorkspaceFileAssetEndpoint.post` (V/asset/v2.py:381) | 500 (TypeError, Methode ohne passende URL-Parameter) bzw. fachlich undefiniert | 405 | DT-GEN-03 | CE-WS-003, CE-OPS-012, CE-OPS-013 |
| EP-0446 | Assets | `GET /api/users/file-assets/` | `UserAssetsEndpoint.get` (V/asset/base.py:81) | 500 (TypeError, Methode ohne passende URL-Parameter) bzw. fachlich undefiniert | 404 | DT-GEN-03 | CE-OPS-013 |
| EP-0448 | Assets | `DELETE /api/users/file-assets/` | `UserAssetsEndpoint.delete` (V/asset/base.py:99) | 500 (TypeError, Methode ohne passende URL-Parameter) bzw. fachlich undefiniert | 404 | DT-GEN-03 | CE-OPS-013 |
| EP-0450 | Assets | `POST /api/users/file-assets/{asset_key}/` | `UserAssetsEndpoint.post` (V/asset/base.py:92) | 500 (TypeError, Methode ohne passende URL-Parameter) bzw. fachlich undefiniert | 404 | DT-GEN-03 | CE-OPS-013 |
| EP-0453 | Assets | `POST /api/workspaces/file-assets/{workspace_id}/{asset_key}/` | `FileAssetEndpoint.post` (V/asset/base.py:39) | 500 (TypeError, Methode ohne passende URL-Parameter) bzw. fachlich undefiniert | 404 | DT-GEN-03 | CE-OPS-013 |
| EP-0456 | Assets | `GET {W}/file-assets/` | `FileAssetEndpoint.get` (V/asset/base.py:27) | 500 (TypeError, Methode ohne passende URL-Parameter) bzw. fachlich undefiniert | 404 | DT-GEN-03 | CE-OPS-013 |
| EP-0458 | Assets | `DELETE {W}/file-assets/` | `FileAssetEndpoint.delete` (V/asset/base.py:49) | 500 (TypeError, Methode ohne passende URL-Parameter) bzw. fachlich undefiniert | 404 | DT-GEN-03 | CE-OPS-013 |
| EP-0465 | Assets | `GET /api/public/assets/v2/anchor/{anchor}/` | `EntityAssetEndpoint.get` (SPV/asset.py:46) | 500 (TypeError, Methode ohne passende URL-Parameter) bzw. fachlich undefiniert | 405 | DT-GEN-03 | CE-SPACE-007 |
| EP-0466 | Assets | `PATCH /api/public/assets/v2/anchor/{anchor}/` | `EntityAssetEndpoint.patch` (SPV/asset.py:177) | 500 (TypeError, Methode ohne passende URL-Parameter) bzw. fachlich undefiniert | 405 | DT-GEN-03 | CE-SPACE-007 |
| EP-0467 | Assets | `DELETE /api/public/assets/v2/anchor/{anchor}/` | `EntityAssetEndpoint.delete` (SPV/asset.py:198) | 500 (TypeError, Methode ohne passende URL-Parameter) bzw. fachlich undefiniert | 405 | DT-GEN-03 | CE-SPACE-007 |
| EP-0468 | Assets | `POST /api/public/assets/v2/anchor/{anchor}/{pk}/` | `EntityAssetEndpoint.post` (SPV/asset.py:87) | 500 (TypeError, Methode ohne passende URL-Parameter) bzw. fachlich undefiniert | 405 | DT-GEN-03 | CE-SPACE-007 |
| EP-0673 | Assets | `PATCH /api/v1/assets/user-assets/` | `UserAssetEndpoint.patch` (V1V/asset.py:205) | 500 (TypeError, Methode ohne passende URL-Parameter) bzw. fachlich undefiniert | 405 | DT-GEN-03 | CE-API-015 |
| EP-0674 | Assets | `DELETE /api/v1/assets/user-assets/` | `UserAssetEndpoint.delete` (V1V/asset.py:233) | 500 (TypeError, Methode ohne passende URL-Parameter) bzw. fachlich undefiniert | 405 | DT-GEN-03 | CE-API-015 |
| EP-0675 | Assets | `PATCH /api/v1/assets/user-assets/server/` | `UserServerAssetEndpoint.patch` (V1V/asset.py:361) | 500 (TypeError, Methode ohne passende URL-Parameter) bzw. fachlich undefiniert | 405 | DT-GEN-03 | CE-API-015 |
| EP-0676 | Assets | `DELETE /api/v1/assets/user-assets/server/` | `UserServerAssetEndpoint.delete` (V1V/asset.py:389) | 500 (TypeError, Methode ohne passende URL-Parameter) bzw. fachlich undefiniert | 405 | DT-GEN-03 | CE-API-015 |
| EP-0677 | Assets | `POST /api/v1/assets/user-assets/{asset_id}/` | `UserAssetEndpoint.post` (V1V/asset.py:112) | 500 (TypeError, Methode ohne passende URL-Parameter) bzw. fachlich undefiniert | 405 | DT-GEN-03 | CE-API-015 |
| EP-0678 | Assets | `POST /api/v1/assets/user-assets/{asset_id}/server/` | `UserServerAssetEndpoint.post` (V1V/asset.py:284) | 500 (TypeError, Methode ohne passende URL-Parameter) bzw. fachlich undefiniert | 405 | DT-GEN-03 | CE-API-015 |
| EP-0680 | Assets | `GET {V1W}/assets/` | `GenericAssetEndpoint.get` (V1V/asset.py:427) | 500 (TypeError, Methode ohne passende URL-Parameter) bzw. fachlich undefiniert | 405 | DT-GEN-03 | CE-API-016 |
| EP-0681 | Assets | `PATCH {V1W}/assets/` | `GenericAssetEndpoint.patch` (V1V/asset.py:608) | 500 (TypeError, Methode ohne passende URL-Parameter) bzw. fachlich undefiniert | 405 | DT-GEN-03 | CE-API-016 |
| EP-0682 | Assets | `POST {V1W}/assets/{asset_id}/` | `GenericAssetEndpoint.post` (V1V/asset.py:507) | 500 (TypeError, Methode ohne passende URL-Parameter) bzw. fachlich undefiniert | 405 | DT-GEN-03 | CE-API-016 |
| EP-0684 | Cycles | `POST {V1P}/archived-cycles/` | `CycleArchiveUnarchiveAPIEndpoint.post` (V1V/cycle.py:800) | 500 (TypeError, Methode ohne passende URL-Parameter) bzw. fachlich undefiniert | 405 | DT-GEN-03 | CE-API-029 |
| EP-0685 | Cycles | `DELETE {V1P}/archived-cycles/` | `CycleArchiveUnarchiveAPIEndpoint.delete` (V1V/cycle.py:831) | 500 (TypeError, Methode ohne passende URL-Parameter) bzw. fachlich undefiniert | 405 | DT-GEN-03 | CE-API-029 |
| EP-0686 | Cycles | `GET {V1P}/archived-cycles/{cycle_id}/unarchive/` | `CycleArchiveUnarchiveAPIEndpoint.get` (V1V/cycle.py:778) | 500 (TypeError, Methode ohne passende URL-Parameter) bzw. fachlich undefiniert | 405 | DT-GEN-03 | CE-API-029 |
| EP-0687 | Cycles | `POST {V1P}/archived-cycles/{cycle_id}/unarchive/` | `CycleArchiveUnarchiveAPIEndpoint.post` (V1V/cycle.py:800) | 500 (TypeError, Methode ohne passende URL-Parameter) bzw. fachlich undefiniert | 405 | DT-GEN-03 | CE-API-029 |
| EP-0688 | ProjectModules | `POST {V1P}/archived-modules/` | `ModuleArchiveUnarchiveAPIEndpoint.post` (V1V/module.py:1084) | 500 (TypeError, Methode ohne passende URL-Parameter) bzw. fachlich undefiniert | 405 | DT-GEN-03 | CE-API-032 |
| EP-0689 | ProjectModules | `DELETE {V1P}/archived-modules/` | `ModuleArchiveUnarchiveAPIEndpoint.delete` (V1V/module.py:1118) | 500 (TypeError, Methode ohne passende URL-Parameter) bzw. fachlich undefiniert | 405 | DT-GEN-03 | CE-API-032 |
| EP-0690 | ProjectModules | `GET {V1P}/archived-modules/{pk}/unarchive/` | `ModuleArchiveUnarchiveAPIEndpoint.get` (V1V/module.py:1056) | 500 (TypeError, Methode ohne passende URL-Parameter) bzw. fachlich undefiniert | 405 | DT-GEN-03 | CE-API-032 |
| EP-0691 | ProjectModules | `POST {V1P}/archived-modules/{pk}/unarchive/` | `ModuleArchiveUnarchiveAPIEndpoint.post` (V1V/module.py:1084) | 500 (TypeError, Methode ohne passende URL-Parameter) bzw. fachlich undefiniert | 405 | DT-GEN-03 | CE-API-032 |
| EP-0692 | Cycles | `GET {V1P}/cycles/{cycle_id}/archive/` | `CycleArchiveUnarchiveAPIEndpoint.get` (V1V/cycle.py:778) | 500 (TypeError, Methode ohne passende URL-Parameter) bzw. fachlich undefiniert | 405 | DT-GEN-03 | CE-API-029 |
| EP-0693 | Cycles | `DELETE {V1P}/cycles/{cycle_id}/archive/` | `CycleArchiveUnarchiveAPIEndpoint.delete` (V1V/cycle.py:831) | 500 (TypeError, Methode ohne passende URL-Parameter) bzw. fachlich undefiniert | 405 | DT-GEN-03 | CE-API-029 |
| EP-0694 | Projects | `GET {V1P}/estimates/` | `ProjectEstimateAPIEndpoint.get` (V1V/estimate.py:83) | nicht geroutet (404) | 404 | DT-V1-01 | CE-API-009 |
| EP-0695 | Projects | `POST {V1P}/estimates/` | `ProjectEstimateAPIEndpoint.post` (V1V/estimate.py:47) | nicht geroutet (404) | 404 | DT-V1-01 | CE-API-009 |
| EP-0696 | Projects | `PATCH {V1P}/estimates/` | `ProjectEstimateAPIEndpoint.patch` (V1V/estimate.py:106) | nicht geroutet (404) | 404 | DT-V1-01 | CE-API-009 |
| EP-0697 | Projects | `DELETE {V1P}/estimates/` | `ProjectEstimateAPIEndpoint.delete` (V1V/estimate.py:129) | nicht geroutet (404) | 404 | DT-V1-01 | CE-API-009 |
| EP-0698 | Projects | `GET {V1P}/estimates/{estimate_id}/estimate-points/` | `EstimatePointListCreateAPIEndpoint.get` (V1V/estimate.py:168) | nicht geroutet (404) | 404 | DT-V1-01 | CE-API-009 |
| EP-0699 | Projects | `POST {V1P}/estimates/{estimate_id}/estimate-points/` | `EstimatePointListCreateAPIEndpoint.post` (V1V/estimate.py:196) | nicht geroutet (404) | 404 | DT-V1-01 | CE-API-009 |
| EP-0700 | Projects | `PATCH {V1P}/estimates/{estimate_id}/estimate-points/{estimate_point_id}/` | `EstimatePointDetailAPIEndpoint.patch` (V1V/estimate.py:264) | nicht geroutet (404) | 404 | DT-V1-01 | CE-API-009 |
| EP-0701 | Projects | `DELETE {V1P}/estimates/{estimate_id}/estimate-points/{estimate_point_id}/` | `EstimatePointDetailAPIEndpoint.delete` (V1V/estimate.py:286) | nicht geroutet (404) | 404 | DT-V1-01 | CE-API-009 |
| EP-0702 | WorkItems | `PUT {V1P}/issues/{pk}/` | `IssueDetailAPIEndpoint.put` (V1V/issue.py:623) | per `http_method_names` ausgeschlossen (405) | 405 | DT-V1-02 | CE-API-017 |
| EP-0703 | Projects | `POST {V1P}/labels/{pk}/` | `LabelDetailAPIEndpoint.post` (V1V/issue.py:933) | 500 (TypeError, Methode ohne passende URL-Parameter) bzw. fachlich undefiniert | 405 | DT-GEN-03 | CE-API-010 |
| EP-0704 | Projects | `POST {V1P}/members/{pk}/` | `ProjectMemberDetailAPIEndpoint.post` (V1V/member.py:160) | 500 (TypeError, Methode ohne passende URL-Parameter) bzw. fachlich undefiniert | 405 | DT-GEN-03 | CE-API-012 |
| EP-0705 | ProjectModules | `GET {V1P}/modules/{module_id}/module-issues/{issue_id}/` | `ModuleIssueDetailAPIEndpoint.get` (V1V/module.py:850) | per `http_method_names` ausgeschlossen (405) | 405 | DT-V1-02 | CE-API-031 |
| EP-0706 | ProjectModules | `GET {V1P}/modules/{pk}/archive/` | `ModuleArchiveUnarchiveAPIEndpoint.get` (V1V/module.py:1056) | 500 (TypeError, Methode ohne passende URL-Parameter) bzw. fachlich undefiniert | 405 | DT-GEN-03 | CE-API-032 |
| EP-0707 | ProjectModules | `DELETE {V1P}/modules/{pk}/archive/` | `ModuleArchiveUnarchiveAPIEndpoint.delete` (V1V/module.py:1118) | 500 (TypeError, Methode ohne passende URL-Parameter) bzw. fachlich undefiniert | 405 | DT-GEN-03 | CE-API-032 |
| EP-0708 | Projects | `POST {V1P}/project-members/{pk}/` | `ProjectMemberDetailAPIEndpoint.post` (V1V/member.py:160) | 500 (TypeError, Methode ohne passende URL-Parameter) bzw. fachlich undefiniert | 405 | DT-GEN-03 | CE-API-012 |
| EP-0709 | WorkItems | `PUT {V1P}/work-items/{pk}/` | `IssueDetailAPIEndpoint.put` (V1V/issue.py:623) | per `http_method_names` ausgeschlossen (405) | 405 | DT-V1-02 | CE-API-017 |
| EP-0721 | Webhooks | `PATCH {W}/webhooks/` | `WebhookEndpoint.patch` (V/webhook/base.py:82) | 500 (TypeError, Methode ohne passende URL-Parameter) bzw. fachlich undefiniert | 405 | DT-GEN-03 | CE-WH-005, CE-WH-011 |
| EP-0722 | Webhooks | `DELETE {W}/webhooks/` | `WebhookEndpoint.delete` (V/webhook/base.py:108) | 500 (TypeError, Methode ohne passende URL-Parameter) bzw. fachlich undefiniert | 405 | DT-GEN-03 | CE-WH-006 |
| EP-0723 | Webhooks | `POST {W}/webhooks/{pk}/` | `WebhookEndpoint.post` (V/webhook/base.py:22) | 500 (TypeError, Methode ohne passende URL-Parameter) bzw. fachlich undefiniert | 405 | DT-GEN-03 | CE-WH-002 |

### 4.26 Frontend-Aufrufe ohne CE-Backend

| Original-Aufruf (Service, Datei:Zeile) | Methode · Pfad | Entscheidung | Ziel-Status | DT | Hinweis |
|---|---|---|---|---|---|
| `CycleService.workspaceActiveCycles` (`apps/web/services/cycle.service.ts:69`, `packages/services/src/cycle/cycle.service.ts:34`) | `GET {W}/active-cycles/` | **bauen** (EP-0311, Modus `cursor`) | 200 | DT-CYC-02 | Workspace-Seite „Active Cycles“ ist im CE-Frontend erreichbar (`workspace-menu.tsx:49`); ohne Backend 404 |
| `ProjectPageService.fetchArchived…` (`apps/web/services/page/project-page.service.ts:106`) | `GET {P}/archived-pages/` | nicht bauen | 404 | DT-GEN-16 | Archivliste kommt aus `GET {P}/pages/?type=archived` |
| `IssueService.bulkSubscribe…` (`apps/web/services/issue/issue.service.ts:417`) | `POST {P}/bulk-subscribe-issues/` | nicht bauen | 404 | DT-GEN-16 | kein UI-Aufrufer |
| `UserService.…myIssues` (`apps/web/services/user.service.ts:46`) | `GET {W}/my-issues/` | nicht bauen | 404 | DT-GEN-16 | Profilseiten nutzen `GET {W}/user-issues/{user_id}/` |
| `WorkspaceService.fetchReleaseNotes` (`apps/web/services/workspace.service.ts:225`) | `GET /api/release-notes/` | nicht bauen | 404 | DT-GEN-16 | „What's new“ nutzt `instance_changelog_url` |
| `AppConfigService.envConfig` (`apps/web/services/app_config.service.ts:21`) | `GET /api/configs/` | nicht bauen | 404 | DT-GEN-16 | Konfiguration kommt aus `GET /api/instances/` und `runtime-config.json` (`14` G-13) |
| `ViewService.getViewIssues` (`apps/web/services/view.service.ts:59`) | `GET {P}/views/{view_id}/issues/` | nicht bauen | 404 | DT-GEN-16 | Views filtern über `GET {P}/issues/` |
| `WorkspaceService.updateSidebarPreference` (`apps/web/services/workspace.service.ts:390`) | `PATCH {W}/sidebar-preferences/{key}/` | nicht bauen | 404 | DT-GEN-16 | Schreiben über `PATCH {W}/sidebar-preferences/` (Zeile in §4.3) |
| `ProjectPageVersionService.restoreVersion` (`apps/web/services/page/project-page-version.service.ts:42`) | `POST {P}/pages/{page_id}/versions/{pk}/restore/` | nicht bauen | 404 | DT-GEN-16 | Wiederherstellen erfolgt im Editor über Live (`07`) |
| `InstanceService.getChangelog` (`packages/services/src/instance/instance.service.ts:54`) | `GET /api/instances/changelog/` | nicht bauen | 404 | DT-GEN-16 | – |
| `FileService.restoreOldEditorAsset` (`apps/web/services/file.service.ts:261`, `packages/services/src/file/file.service.ts:68`) | `POST /api/workspaces/file-assets/{workspace_id}/{asset_key}/restore/` | nicht portieren | 404 | DT-AST-01 | Legacy-Assets; Altdaten-Migration statt Legacy-Endpunkt |

Die Liste ist zugleich `frontend/tools/contract-check/allowed-missing.json` (§3.15) und die Datenquelle von `DeadFrontendCallsTests` (`tests/Plane.AppHost.Tests/Routing/`). Die zugehörigen Service-Methoden werden 1:1 portiert (`08` R-D08-01), aber von keinem Store aufgerufen.

### 4.27 Webhook-Ausgang: Ereignisse → auslösende Endpunkte

Grundlage `06` §3.14.2 (`WebhookTriggerMap`). Spalte „`old_value`-Quelle“ beantwortet `06` O-D06-07: Die `before`-Form für `Changes` ist je Origin die Form, die das Original als `current_instance` übergibt.

| Integration-Event | `X-Plane-Event` / `action` | auslösende Endpunkte App | auslösende Endpunkte V1 | `old_value`-Quelle (before-Form) | Original-Stellen (A07) |
|---|---|---|---|---|---|
| `plane.project.created.v1` | `project` / `created` | EP-0187 | EP-0600 | – (`activity.field = null`) | W11, W21 |
| `plane.project.updated.v1` | `project` / `updated` | EP-0190 | EP-0602 | App: `ProjectSerializer`-Form vor dem Update; V1: v1-`ProjectSerializer` | W12, W22 |
| `plane.project.deleted.v1` | `project` / `deleted` | EP-0191 | EP-0603 | – (`data = {"id"}`) | WD1, WD2 |
| `plane.work_item.created.v1` | `issue` / `created` | EP-0261 | EP-0649, EP-0654 | – | W3, W15 (W5 `put_create` entfällt, DT-V1-02) |
| `plane.work_item.updated.v1` | `issue` / `updated` | EP-0267 | EP-0651, EP-0656 | App: `IssueDetailSerializer`-Form (`current_instance`); V1: v1-`IssueSerializer` | W6, W16 (W4 `put` entfällt, DT-V1-02) |
| `plane.cycle.created.v1` | `cycle` / `created` | EP-0315 | EP-0545 | – | W1, W13 |
| `plane.cycle.updated.v1` | `cycle` / `updated` | EP-0322 | EP-0548 | App: `CycleSerializer`-Form; V1: v1-`CycleSerializer` | W2, W14 |
| `plane.module.created.v1` | `module` / `created` | EP-0340 | EP-0590 | – | W9, W19 |
| `plane.module.updated.v1` | `module` / `updated` | EP-0344 | EP-0592 | App: `ModuleWriteSerializer`-Form; V1: v1-`ModuleSerializer` | W10, W20 |
| `plane.work_item_comment.created.v1` | `issue_comment` / `created` | EP-0250 | EP-0638, EP-0643 | – | W7, W17 |
| `plane.work_item_comment.updated.v1` | `issue_comment` / `updated` | EP-0252 | EP-0640, EP-0645 | App: `IssueCommentSerializer`-Form; V1: v1-`IssueCommentSerializer` | W8, W18 |

Die Upsert-Variante `put`/`put_create` des Originals (`IssueDetailAPIEndpoint.put`) ist nicht geroutet (DT-V1-02); `UpsertWorkItemCommand` existiert daher in der CE nicht, die Operationswerte `put`/`put_create` der Trigger-Tabelle in `06` bleiben ohne Auslöser (Rückmeldung an `06`, §9). Keine Webhook-Auslösung durch: EP-0268/EP-0652/EP-0657 (Work Item löschen), EP-0323/EP-0549 (Cycle löschen), EP-0345/EP-0593 (Modul löschen), EP-0253/EP-0641/EP-0646 (Kommentar löschen), Archiv-, Bulk-, Zuordnungs-, Intake-, Link-, Anhang- und Reaktions-Endpunkte (DT-WH-07).

### 4.28 CE-IDs ohne eigene Endpunktzeile

Von 507 CE-IDs tragen 301 mindestens eine Katalogzeile (Spalte „CE-IDs“ in §4.1–§4.25). 124 IDs sind reine Darstellungs-/Frontend-Features, deren Daten über die Endpunkte ihres Bereichs kommen (Feature-Katalog-Bereiche CE-WS-013, -014, -016…020, CE-PRJ-011…015, -017, -020, CE-LV-001…004, -007…009, -012, -013, -017…032, -034…046, CE-PAGE-013…018, -020…040, CE-SRCH-004…009, CE-I18N-001…026, CE-UIX-001…013); 5 davon tragen zusätzlich eine Katalogzeile, 119 nicht. Die übrigen 87 IDs haben keine eigene Endpunktzeile, weil sie Querschnitt, Job, Live, Gateway, Betrieb, ein reines Frontend-Element außerhalb dieser Bereiche oder durch ADR-008 entfallen sind; sie stehen mit Träger und Bezug in der folgenden Tabelle (301 + 119 + 87 = 507). `CeCoverageTests` (`tests/Plane.AppHost.Tests/Catalog/`) prüft diese Summe gegen `features/_data/ce-features.json`.

| CE-ID | Name | Träger | Bezug |
|---|---|---|---|
| CE-WS-008 | Rollen- und Berechtigungsmodell (Admin/Member/Guest) | Querschnitt | Permission-Evaluator für alle Endpunkte (§3.5, 05 §3.13); Rollenwerte `role: 20/15/5` in allen Mitglieder-DTOs |
| CE-WS-015 | What's new? (Produkt-Changelog) | Frontend | iframe auf `INSTANCE_CHANGELOG_URL` aus `GET /api/instances/` (EP-0077); `GET /api/release-notes/` nicht gebaut (DT-GEN-16) |
| CE-WS-024 | Workspace-Settings-Rahmen | Frontend | Settings-Rahmen; Rechte aus `GET {W}/workspace-members/me/` (EP-0138) |
| CE-WI-006 | Toast-Aktionen nach dem Erstellen | Frontend | UI des Work-Item-Detail/-Modals; Daten über §4.5 (`GET {P}/issues/{pk}/`, Stammdaten-Endpunkte §4.3/§4.4) |
| CE-WI-007 | Draft-Rückfrage beim Schließen | Frontend | UI des Work-Item-Detail/-Modals; Daten über §4.5 (`GET {P}/issues/{pk}/`, Stammdaten-Endpunkte §4.3/§4.4) |
| CE-WI-013 | Identifier mit Klick-zum-Kopieren | Frontend | UI des Work-Item-Detail/-Modals; Daten über §4.5 (`GET {P}/issues/{pk}/`, Stammdaten-Endpunkte §4.3/§4.4) |
| CE-WI-014 | Detail-Kopfaktionen | Frontend | UI des Work-Item-Detail/-Modals; Daten über §4.5 (`GET {P}/issues/{pk}/`, Stammdaten-Endpunkte §4.3/§4.4) |
| CE-WI-016 | Peek-Inhalt | Frontend | UI des Work-Item-Detail/-Modals; Daten über §4.5 (`GET {P}/issues/{pk}/`, Stammdaten-Endpunkte §4.3/§4.4) |
| CE-WI-017 | Peek schließen per Outside-Click/Escape | Frontend | UI des Work-Item-Detail/-Modals; Daten über §4.5 (`GET {P}/issues/{pk}/`, Stammdaten-Endpunkte §4.3/§4.4) |
| CE-WI-018 | Peek-Fehler- und Ladezustand | Frontend | UI des Work-Item-Detail/-Modals; Daten über §4.5 (`GET {P}/issues/{pk}/`, Stammdaten-Endpunkte §4.3/§4.4) |
| CE-WI-019 | Hover-Vorschaukarte | Frontend | UI des Work-Item-Detail/-Modals; Daten über §4.5 (`GET {P}/issues/{pk}/`, Stammdaten-Endpunkte §4.3/§4.4) |
| CE-WI-021 | State-Dropdown | Frontend | UI des Work-Item-Detail/-Modals; Daten über §4.5 (`GET {P}/issues/{pk}/`, Stammdaten-Endpunkte §4.3/§4.4) |
| CE-WI-022 | Prioritäten und Priority-Dropdown | Frontend | UI des Work-Item-Detail/-Modals; Daten über §4.5 (`GET {P}/issues/{pk}/`, Stammdaten-Endpunkte §4.3/§4.4) |
| CE-WI-023 | Member-Dropdown (Assignees) | Frontend | UI des Work-Item-Detail/-Modals; Daten über §4.5 (`GET {P}/issues/{pk}/`, Stammdaten-Endpunkte §4.3/§4.4) |
| CE-WI-024 | Label-Dropdown mit Anlage | Frontend | UI des Work-Item-Detail/-Modals; Daten über §4.5 (`GET {P}/issues/{pk}/`, Stammdaten-Endpunkte §4.3/§4.4) |
| CE-WI-025 | Cycle-Dropdown | Frontend | UI des Work-Item-Detail/-Modals; Daten über §4.5 (`GET {P}/issues/{pk}/`, Stammdaten-Endpunkte §4.3/§4.4) |
| CE-WI-027 | Estimate-Dropdown | Frontend | UI des Work-Item-Detail/-Modals; Daten über §4.5 (`GET {P}/issues/{pk}/`, Stammdaten-Endpunkte §4.3/§4.4) |
| CE-WI-028 | Projekt-Dropdown | Frontend | UI des Work-Item-Detail/-Modals; Daten über §4.5 (`GET {P}/issues/{pk}/`, Stammdaten-Endpunkte §4.3/§4.4) |
| CE-WI-029 | Datums- und Datumsbereichsauswahl | Frontend | UI des Work-Item-Detail/-Modals; Daten über §4.5 (`GET {P}/issues/{pk}/`, Stammdaten-Endpunkte §4.3/§4.4) |
| CE-WI-030 | Read-only-Label-Anzeige | Frontend | UI des Work-Item-Detail/-Modals; Daten über §4.5 (`GET {P}/issues/{pk}/`, Stammdaten-Endpunkte §4.3/§4.4) |
| CE-WI-034 | Widget-Aktionsleiste | Frontend | UI des Work-Item-Detail/-Modals; Daten über §4.5 (`GET {P}/issues/{pk}/`, Stammdaten-Endpunkte §4.3/§4.4) |
| CE-CYC-014 | Cycle-Kontextmenü | Frontend | Kontextmenü ruft Cycle-Endpunkte (§4.7) |
| CE-INT-011 | Intake-Navigation | Frontend | Navigation über `GET {P}/intake-issues/` (EP-0378) |
| CE-HOME-003 | Quickstart-Guide | Frontend | Quickstart-Status aus `GET /api/users/me/profile/` (EP-0059) bzw. `PATCH /api/users/me/onboard/` |
| CE-NOTIF-001 | Erzeugung von In-App-Benachrichtigungen | Job/Event (06) | Activity-Consumer erzeugt Notifications; Auslieferung über `GET {W}/users/notifications/` (EP-0496), Zähler-Push `/live/events/` |
| CE-NOTIF-002 | Erwähnungs-Benachrichtigungen | Job/Event (06) | Mention-Erkennung im Activity-Consumer |
| CE-NOTIF-003 | Automatisches Abonnieren | Job/Event (06) | Auto-Abo in Work-Item-Commands (Ersteller, Assignees, Kommentierende) |
| CE-NOTIF-008 | E-Mail-Benachrichtigungen (5-Minuten-Bündelung) | Job (06) | E-Mail-Bündelung 5 min (Cron `email_notification`) |
| CE-PROF-002 | Profil-Einstellungen (Modal und Seite) | Frontend | Profil-Modal/-Seite über `GET/PATCH /api/users/me/` und `/api/users/me/profile/` |
| CE-PROF-011 | Profil-Sidebar | Frontend | Profil-Sidebar über `GET {W}/user-profile/{user_id}/` (EP-0109) |
| CE-AUTH-002 | Sign-up-Seite | entfällt (ADR-008) | Registrierung in Keycloak (optional), JIT-Anlage im Callback |
| CE-AUTH-015 | AGB-Hinweis und Auth-Fuß | Frontend/Keycloak-Theme | AGB-Hinweis im Login-Theme (05 §3.16) |
| CE-AUTH-021 | Passwortstärke-Anzeige | entfällt (ADR-008) | Passwortregeln in Keycloak |
| CE-AUTH-026 | Rate-Limits gegen Brute-Force und Missbrauch | Querschnitt | Rate-Limit-Policies `authentication`, `anon`, `api_key` (§3.12) |
| CE-INST-009 | Instanzfehler-Ansicht (God Mode) | Frontend | Fehleransicht bei nicht erreichbarem `GET /api/instances/` |
| CE-INST-011 | Header mit Breadcrumb | Frontend | God-Mode-Header |
| CE-INST-012 | Konto-Menü mit Theme-Umschaltung | Frontend | Konto-Menü, Theme lokal |
| CE-INST-013 | Hilfe-Bereich der Admin-Sidebar | Frontend | Hilfe-Links |
| CE-INST-014 | Dialog für ungespeicherte Änderungen (God Mode) | Frontend | Dialog ungespeicherter Änderungen |
| CE-INST-015 | Kopierfelder für Plane-URLs | Frontend | URLs aus `GET /api/instances/` `config` |
| CE-INST-016 | 404-Seite und Fehlerbehandlung (God Mode) | Frontend | 404-Seite God Mode |
| CE-INST-020 | Authentifizierungsmethoden-Übersicht | entfällt (ADR-008) | Auth-Methoden-Übersicht → Hinweis auf Keycloak-Admin-Konsole |
| CE-INST-021 | Google-OAuth-Konfiguration | entfällt (ADR-008) | Provider-Konfiguration in Keycloak |
| CE-INST-022 | GitHub-OAuth-Konfiguration | entfällt (ADR-008) | dto. |
| CE-INST-023 | GitLab-OAuth-Konfiguration | entfällt (ADR-008) | dto. |
| CE-INST-024 | Gitea-OAuth-Konfiguration | entfällt (ADR-008) | dto. |
| CE-INST-030 | Willkommens-Popup 'Create workspace' | Frontend | Popup nach Erst-Einrichtung (`GET /api/instances/admins/me/`) |
| CE-SPACE-008 | Space-Login: E-Mail-Check | entfällt (ADR-008) | Space-Login über `/auth/oidc/login/?app=space` |
| CE-SPACE-009 | Space-Login und -Sign-up mit Passwort | entfällt (ADR-008) | dto. |
| CE-SPACE-010 | Space-Login mit Unique Code | entfällt (ADR-008) | dto. |
| CE-SPACE-011 | OAuth-Buttons im Space | entfällt (ADR-008) | dto. |
| CE-SPACE-012 | Fehlerbanner aus Auth-Redirects (Space) | Frontend | Banner aus `error_code`/`error_message` der Callback-Redirects (05 §4.3) |
| CE-SPACE-013 | Rechtshinweis Terms/Privacy (Space) | Frontend | Rechtshinweis |
| CE-SPACE-015 | Instanzfehler-Ansicht (Space) | Frontend | Instanzfehler-Ansicht |
| CE-SPACE-018 | Board-Navbar | Frontend | Navbar aus `GET {SP}/settings/` |
| CE-SPACE-021 | Eigenschafts-Chips | Frontend | Chips aus Board-Stammdaten |
| CE-SPACE-023 | Leiste aktiver Filter | Frontend | Filterleiste |
| CE-SPACE-029 | iframe-Einbettung | Gateway (14) | `frame-ancestors` für Board-Routen (05 D05-ADR-23) |
| CE-SPACE-030 | Mention-Darstellung (Space) | Frontend | Mention-Darstellung aus `GET {SP}/members/` |
| CE-SPACE-031 | Fehler- und 404-Seiten (Space) | Frontend | Fehlerseiten |
| CE-SPACE-032 | 'Powered by Plane Publish'-Badge | Frontend | Badge |
| CE-API-002 | Rate-Limiting je API-Key | Querschnitt | Policy `api_key` + Header `X-RateLimit-*` auf allen V1-Antworten (§3.12) |
| CE-API-003 | API-Aktivitätsprotokoll | Querschnitt | `ApiActivityLogMiddleware` (02 §3.4.1 Nr. 14) für alle V1-Requests |
| CE-WH-001 | Webhook-Datenmodell und Event-Typen | Webhook-Ausgang | §3.17, §4.27 (Ereignis-Katalog) |
| CE-WH-007 | Webhook-Zustellung | Webhook-Ausgang | §3.17 (Zustellung, Verweis 06 §3.14.4) |
| CE-WH-008 | Webhook-Payload-Format | Webhook-Ausgang | §3.17 (Payload/Header) |
| CE-WH-009 | Webhook-Deaktivierungs-Mail | Webhook-Ausgang | §3.17 (Deaktivierungs-Mail, 06) |
| CE-OPS-001 | Self-Hosting-CLI | Betrieb (14) | `plane-cli` |
| CE-OPS-002 | Daten-Restore | Betrieb (14) | Restore |
| CE-OPS-003 | Docker-Swarm-Deployment | Betrieb (14) | Swarm |
| CE-OPS-004 | All-in-One-Container | Betrieb (14) | AIO |
| CE-OPS-005 | Reverse-Proxy mit automatischem HTTPS | Gateway (14) | TLS/ACME |
| CE-OPS-006 | Statische Frontend-Auslieferung | Gateway (14) | statische Auslieferung G-03/G-05/G-16 |
| CE-OPS-007 | Konfigurierbare Base-URLs und -Paths | Gateway (14) | `/runtime-config.json` (G-13, 01 §7.12) |
| CE-OPS-009 | Upload-Größenlimit mit 413-Fehler | Querschnitt | 413-Körper (§3.5) |
| CE-OPS-010 | Read-Replica-Unterstützung | Querschnitt | `.UseReadReplica()` an den Lese-Endpunkten laut 02 D02-ADR-22 (Spalte `read_replica` in `endpoints.json`) |
| CE-OPS-011 | Redis mit TLS | Betrieb (14) | Valkey-TLS |
| CE-OPS-014 | Soft-Delete und endgültige Löschung | Querschnitt | Soft-Delete-Semantik aller DELETE-Endpunkte (02 D02-ADR-03) |
| CE-OPS-015 | Aufbewahrung und Bereinigung | Job (06) | Bereinigungs-Jobs |
| CE-OPS-016 | Zeitgesteuerte Jobs (Beat-Plan) | Job (06) | Cron-Plan |
| CE-OPS-017 | Rich-Text-Sanitizing und Binary-Prüfung | Querschnitt | `[SanitizedHtml]` (DT-WI-11) |
| CE-OPS-019 | Strukturiertes Request-Logging | Querschnitt | Request-Log (02 §3.14) |
| CE-OPS-020 | Betriebs-CLI (Management-Commands) | Betrieb (14) | CLI |
| CE-OPS-021 | Lokale Entwicklungsumgebung | Betrieb (14) | Aspire `dev` |
| CE-OPS-022 | Isolierter Test-Stack und Testsuites | Tests (15) | Profil `test` |
| CE-OPS-023 | CI/CD-Pipelines | Betrieb (14) | CI/CD |
| CE-OPS-024 | Dummy-Daten-Generator | Betrieb (14) | `plane-cli create-dummy-data` |

### 4.29 Abweichungs-IDs `DEV-API-*`

`DEV-API-01…04` vergibt `05` (Anhang B); `DEV-API-05…63` vergibt dieses Dokument. Jede ID wird in `tests/contracts/deviations.yaml` mit `decision: "04#<DT-ID>"` geführt, sobald der zugehörige Endpunkt im Harness aufgezeichnet wird. Weitere in den DT-Zeilen genannte IDs gehören anderen Dokumenten: `DEV-PAG-001`, `DEV-JSON-001/-002`, `DEV-FLT-*`, `DEV-GRP-*`, `DEV-LBL-*`, `DEV-RL-001` (`02`), `DEV-PERM-001` (`02`/`05`), `DEV-WH-001…003` (`06`), `DEV-07-*` (`07`), `SEC-*`/`HARM-*` (`05`).

| ID | DT | Kurzbeschreibung |
|---|---|---|
| `DEV-API-05` | DT-GEN-01 | DRF-Default-`update` (PUT) neben PATCH: Workspace (W-05), Projekt (P-05), Work Item (I7), Kommentar (C4), Cycle (Y4), Modul (M4), Projekt-View (W4), Workspace-View (W10) umgehen Er… |
| `DEV-API-06` | DT-GEN-03 | Methoden-Nebenprodukte: Django-`APIView`-Klassen beantworten jede implementierte Methode auf **allen** ihnen zugeordneten Routen (z. B. `DELETE /api/users/api-tokens/` ohne `pk`, `… |
| `DEV-API-07` | DT-GEN-04 | Django `APPEND_SLASH`: Pfade ohne abschließenden Slash → 301 (GET) bzw. 500 (POST/PATCH) |
| `DEV-API-08` | DT-GEN-07 | Response-Cache `@cache_response` (Schlüssel Pfad+User, 1–2 h); Invalidierungen treffen die Schlüssel nicht → veraltete Daten bis 2 h (Workspace-Labels, Instanz, Konfiguration) |
| `DEV-API-09` | DT-GEN-11 | `global_paginator` mit `page_size = 0` → `ZeroDivisionError` (500) |
| `DEV-API-10` | DT-GEN-15 | Favoriten-Listen `GET {P}/user-favorite-cycles/`, `…/user-favorite-modules/`, `…/user-favorite-views/` immer 500 (`select_related` ungültig), kein Client-Aufrufer (Favoriten kommen… |
| `DEV-API-11` | DT-AUTH-04 | Post-Login-Workflow legt Projektmitgliedschaften aus angenommenen Projekt-Einladungen ohne `project_id` an → NOT-NULL-Verletzung, 500 bei jedem Login |
| `DEV-API-12` | DT-AUTH-08 | Konto deaktivieren randomisiert das Passwort und meldet ab; „einziger Admin“-Prüfung ist wirkungslos (deaktiviert faktisch immer) |
| `DEV-API-13` | DT-AUTH-11 | Zeitzonenliste mit falsch formatierten negativen Halbstunden-Offsets (z. B. `UTC-03:-30`) |
| `DEV-API-14` | DT-WS-01 | `GET /api/workspaces/` liefert immer 400 (`KeyError` in `allow_permission`); Workspace-Liste kommt aus `GET /api/users/me/workspaces/` |
| `DEV-API-15` | DT-WS-02 | `GET /api/users/last-visited-workspace/` immer 500 |
| `DEV-API-16` | DT-WS-03 | Einladung annehmen setzt `user.last_workspace_id` (Feld existiert nur auf `Profile`) – wirkungslos |
| `DEV-API-17` | DT-WS-04 | Erneute Einladung derselben E-Mail wird still ignoriert (`bulk_create(ignore_conflicts=True)`), keine Mail |
| `DEV-API-18` | DT-WS-07 | Draft → Work Item schreibt Cycle-Activity mit `project_id="None"` |
| `DEV-API-19` | DT-PRJ-01 | `POST {P}/invitations/` immer 500 (`AttributeError` auf QuerySet, `delay` auf Liste) |
| `DEV-API-20` | DT-PRJ-05 | `intake_view` nur über den Altnamen `inbox_view` setzbar |
| `DEV-API-21` | DT-PRJ-07 | Estimate-Punkt mit `key = 0` nicht anlegbar |
| `DEV-API-22` | DT-WI-02 | `GET {P}/issues/list/?group_by=labels__id` (u. ä.) lässt die Annotation `label_ids` weg → 500 |
| `DEV-API-23` | DT-WI-03 | Relation `implements` wird nicht invertiert gespeichert; `implemented_by` fehlt in der Listenantwort |
| `DEV-API-24` | DT-WI-04 | `GET {P}/issues/{issue_id}/issue-subscribers/` liefert alle Projektmitglieder statt der Abonnenten |
| `DEV-API-25` | DT-WI-05 | Bulk-Operationen (`bulk-archive-issues`, `bulk-delete-issues`, `issue-dates`) umgehen Model-Logik (`completed_at`, `updated_by`), Bulk-Delete ohne Kaskade und Activity |
| `DEV-API-26` | DT-WI-06 | Archiv-Detail `GET {P}/issues/{pk}/archive/` liefert weniger Felder als das Detail (`cycle_id`, `module_ids`, `label_ids` … fehlen) |
| `DEV-API-27` | DT-WI-07 | `label_ids`/`assignee_ids` enthalten Zuordnungen zu soft-gelöschten Labels/Benutzern (nur gelöschte Zwischenzeilen werden ausgeblendet) |
| `DEV-API-28` | DT-WI-10 | `GET {P}/issues/{issue_id}/issue-attachments/{pk}/` immer 500 (Methode ohne `pk`) |
| `DEV-API-29` | DT-CYC-01 | Abgeschlossener Cycle: PATCH mit `sort_order` speichert **alle** gesendeten Felder (App), Einschränkung wirkungslos (v1) |
| `DEV-API-30` | DT-CYC-02 | `GET /api/workspaces/{slug}/active-cycles/` wird vom CE-Frontend aufgerufen, existiert im CE-Backend nicht |
| `DEV-API-31` | DT-MOD-01 | v1-Modul-Zuordnung: fehlerhafter Vergleich, `modules_list` als String |
| `DEV-API-32` | DT-INT-01 | `POST {P}/intakes/` (Alias `inboxes/`) defekt (Decorator auf `perform_create`); Intakes entstehen beim Aktivieren von `intake_view` |
| `DEV-API-33` | DT-INT-03 | v1-Intake-POST → 500, wenn `intake_view=true`, aber kein Intake existiert; bei mehreren Intakes nimmt v1 das erste statt `is_default` |
| `DEV-API-34` | DT-INT-05 | Space-Intake-Einreichung speichert Priorität `low` als Default statt `none` |
| `DEV-API-35` | DT-PAGE-01 | Page-Versionen werden wegen `page.description`-Bug nie erzeugt |
| `DEV-API-36` | DT-PAGE-02 | Page duplizieren: Labels nicht kopiert, `project_id`-Schleifenvariable |
| `DEV-API-37` | DT-PAGE-03 | Rekursives Archivieren berücksichtigt soft-gelöschte Kinder; `archived_at` der Archiv-Antwort ist naive Server-Lokalzeit |
| `DEV-API-38` | DT-PAGE-04 | `PATCH {P}/pages/{page_id}/` liefert bei **jedem** `Page.DoesNotExist` (z. B. ungültiger `parent`) den Text „Access cannot be updated since this page is owned by someone else“ |
| `DEV-API-39` | DT-PAGE-05 | `labels` an Pages akzeptieren beliebige Label-IDs (auch fremder Projekte) |
| `DEV-API-40` | DT-PAGE-07 | `POST {P}/pages/`: ungültige Referenzen (`parent` aus fremdem Projekt/nicht existent, fremde `labels`) führen zu `IntegrityError`-Abbildung oder stiller Fehlzuordnung |
| `DEV-API-41` | DT-RT-03 | PDF-Export: Callout-Emoji als Dezimal-Codepoint („128161“); Mentions zeigen `entity_name` (Mentions-Endpunkt fehlt in CE); `page_locked`/`page_archived` werden nie gesendet |
| `DEV-API-42` | DT-NOTIF-01 | `snoozed=false` zeigt noch gesnoozte; `subscribed`-Subquery vergleicht `IssueAssignee.pk` mit `issue_id` |
| `DEV-API-43` | DT-NOTIF-02 | `POST {W}/users/notifications/mark-all-read/`: `type` erwartet `watching` statt `subscribed`, kein Komma-Split |
| `DEV-API-44` | DT-ANA-01 | `PATCH {W}/analytic-view/{pk}/` setzt `query` auf `{}`; Default-Analytics summiert Legacy-Feld `point` |
| `DEV-API-45` | DT-HOME-01 | Recents nach erstem statt letztem Besuch sortiert (`created_at` statt `visited_at`) |
| `DEV-API-46` | DT-AI-01 | Unsplash-URL mit `page=$1`, kein Timeout; Anthropic/Gemini-Provider funktionieren nicht, fehlender `prompt` → 500 |
| `DEV-API-47` | DT-AST-01 | Legacy-Asset-Endpunkte v1 (`{W}/file-assets/`, `/api/workspaces/file-assets/{workspace_id}/{asset_key}/…`, `/api/users/file-assets/…`) für Altdaten; GET-Varianten 500 |
| `DEV-API-48` | DT-SPACE-01 | `GET /api/public/workspaces/{slug}/project-boards/` immer 500 (Signatur passt nicht) |
| `DEV-API-49` | DT-SPACE-02 | Reaktions-/Vote-Listen im Space immer `[]`; Reaktions-`avatar_url` aus Votes berechnet |
| `DEV-API-50` | DT-SPACE-03 | Space-Issue-Detail liefert 200 `null` statt 404; `description_binary` als Rohbytes in `.values()` (möglicher 500) |
| `DEV-API-51` | DT-SPACE-04 | Space-Issue-Liste: `group_by ∈ {target_date, start_date, created_by}` → 500 |
| `DEV-API-52` | DT-INST-01 | `latest_version` über GitHub-API, Telemetrie standardmäßig aktiv |
| `DEV-API-53` | DT-INST-05 | Workspace-Anlage im God Mode ohne Seed-Daten und ohne die Prüfungen der App-Anlage |
| `DEV-API-54` | DT-V1-03 | DRF-`APIRootView` `GET {V1W}/` und Format-Suffix-Routen `.json` (DefaultRouter) |
| `DEV-API-55` | DT-V1-04 | OpenAPI per drf-spectacular (3.0.3), Swagger-UI/Redoc laden Assets vom CDN |
| `DEV-API-56` | DT-V1-05 | v1-Einladungen und -Stickies ohne API-Key-Rate-Limit |
| `DEV-API-57` | DT-V1-07 | v1-Mitgliederlisten enthalten inaktive Mitglieder ohne Kennzeichen |
| `DEV-API-58` | DT-V1-08 | v1-Einladungen ohne Token und ohne E-Mail |
| `DEV-API-59` | DT-V1-09 | v1-Generic-Assets: `asset_url` mit `issues/None`; Server-Assets und Generic-Asset-POST/GET → 500 (`S3Storage(is_server=True)`), POSTs hinterlassen verwaiste Assets |
| `DEV-API-60` | DT-V1-10 | `limit`/`size` per `int()` ohne Fehlerbehandlung → 500 |
| `DEV-API-61` | DT-V1-11 | v1-Projekt-PATCH meldet Fehler zu `default_state`/`estimate` als 409 „identifier already taken“; `IntegrityError` ohne „already exists“ → 500 (View liefert `None`) |
| `DEV-API-62` | DT-WH-01 | `created`-Events, deren Task vor dem Commit läuft, werden still verworfen (`ObjectDoesNotExist`) |
| `DEV-API-63` | DT-WS-09 | Reservierte Workspace-Slugs zwischen Backend und Frontend uneinheitlich; `login`/`register` fehlen |

---

## 5. Code-Skelette

Die Skelette ergänzen `02` §5 (Modul-Schablone, `LabelEndpoints`) um die in diesem Dokument festgelegten Bausteine. Namen sind verbindlich, Implementierungsdetails (Methodenrümpfe) Beispiel.

### 5.1 Endpunkt-Metadaten – `src/building-blocks/Plane.BuildingBlocks.Web/Endpoints/CatalogMetadata.cs`

```csharp
namespace Plane.BuildingBlocks.Web.Endpoints;

public enum PaginationMode { None, Cursor, CursorGrouped, WhenRequested, Required, Global }

public sealed record OriginalContractMetadata(string OriginalId);          // "A04:L1" | "neu:N-01"
public sealed record PaginationMetadata(PaginationMode Mode, int DefaultPerPage, int MaxPerPage);
public sealed record ExpandAllowlistMetadata(IReadOnlyList<string> Keys);
public sealed record OriginalOperationIdMetadata(string OperationId);       // nur V1 (OpenAPI)
public sealed record CacheControlMetadata(string Value);

public static class CatalogEndpointConventions
{
    // D04-ADR-05: Original-ID im Format <Dok>:<ID>; Analyzer PLANE0005 erzwingt das Format (Regex ^(A0[3-9]|A1[0-2]|neu):.+$)
    public static TBuilder WithOriginalContract<TBuilder>(this TBuilder b, string originalId) where TBuilder : IEndpointConventionBuilder
        => b.WithMetadata(new OriginalContractMetadata(originalId));

    public static TBuilder WithPagination<TBuilder>(this TBuilder b, PaginationMode mode, int defaultPerPage = 1000, int maxPerPage = 1000)
        where TBuilder : IEndpointConventionBuilder
        => b.WithMetadata(new PaginationMetadata(mode, defaultPerPage, maxPerPage));

    public static TBuilder WithExpand<TBuilder>(this TBuilder b, params string[] keys) where TBuilder : IEndpointConventionBuilder
        => b.WithMetadata(new ExpandAllowlistMetadata(keys));

    public static TBuilder WithOriginalOperationId<TBuilder>(this TBuilder b, string operationId) where TBuilder : IEndpointConventionBuilder
        => b.WithMetadata(new OriginalOperationIdMetadata(operationId));

    // D04-ADR-05: Alias-Pfad auf denselben Handler (issues ↔ work-items, inbox-issues ↔ intake-issues, inboxes ↔ intakes, v1 project-members ↔ members, v1 issue-attachments ↔ attachments)
    public static RouteHandlerBuilder MapAlias(this RouteGroupBuilder g, string method, string pattern, Delegate handler, string epName)
        => g.MapMethods(pattern, [method], handler).WithName(epName);
}
```

### 5.2 App-Endpunkt mit Katalog-Metadaten – `src/modules/WorkItems/Plane.WorkItems/Endpoints/App/WorkItemEndpoints.cs` (Auszug)

```csharp
internal static class WorkItemEndpoints
{
    public static void Map(PlaneEndpointRouteBuilder e)
    {
        var p = e.App("workspaces/{slug}/projects/{project_id:guid}").WithTags("Work Items");

        // EP-0260 GET {P}/issues/  – A04:I2, cursor-grouped, Read-Replica
        p.MapGet("issues", List).WithName("EP-0260").WithOriginalContract("A04:I2")
         .RequirePermission(WorkItemsPermissions.ProjectWorkItemRead)
         .WithPagination(PaginationMode.CursorGrouped).UseReadReplica();

        // EP-0266 GET {P}/issues/{pk}/ – A04:I6, expand-Allowlist (§3.9)
        p.MapGet("issues/{pk:guid}", Get).WithName("EP-0266").WithOriginalContract("A04:I6")
         .RequirePermission(WorkItemsPermissions.ProjectWorkItemRead)
         .WithExpand("issue_reactions", "issue_attachments", "issue_link", "parent", "assignees", "labels", "state",
                     "project", "workspace", "created_by", "updated_by", "issue_cycle", "issue_relation", "issue_related",
                     "issue_intake", "sub_issues");

        // EP-0267 PATCH {P}/issues/{pk}/ – Original 204 (DT-GEN-06, 1:1)
        p.MapPatch("issues/{pk:guid}", Update).WithName("EP-0267").WithOriginalContract("A04:I8")
         .RequirePermission(WorkItemsPermissions.ProjectWorkItemUpdate).Validate<UpdateWorkItemRequest>();

        // EP-0256 DELETE {P}/bulk-delete-issues/ – Body im DELETE, eine Transaktion (DT-WI-05)
        p.MapDelete("bulk-delete-issues", BulkDelete).WithName("EP-0256").WithOriginalContract("A04:A6")
         .RequirePermission(WorkItemsPermissions.ProjectWorkItemDelete).Validate<BulkDeleteWorkItemsRequest>();
    }

    static async Task<IResult> Update(IRequestScope scope, Guid pk, UpdateWorkItemRequest body, ISender sender, CancellationToken ct)
        => (await sender.Send(new UpdateWorkItemCommand(scope.Project, pk, body, Origin.App), ct)).ToNoContent();

    static async Task<IResult> BulkDelete(IRequestScope scope, [FromBody] BulkDeleteWorkItemsRequest body, ISender sender, CancellationToken ct)
        => (await sender.Send(new BulkDeleteWorkItemsCommand(scope.Project, body.IssueIds), ct))
           .ToOk(n => new { message = $"{n} issues were deleted" });
    // List/Get analog (02 §5.2.9)
}
```

Die Original-ID `A04:I8` für `PATCH {P}/issues/{pk}/` und alle übrigen IDs stehen in §4; der Analyzer `PLANE0006` (Erweiterung von `02` §3.17) meldet Routen ohne `WithName("EP-…")`/`WithOriginalContract`.

### 5.3 v1-Adapter mit Contract-Command (D04-ADR-04)

```csharp
// src/modules/Projects/Plane.Projects.Contracts/Commands/CreateLabelCommand.cs  – öffentlich, nur BCL-/Contracts-Typen (R2)
public sealed record CreateLabelCommand(ProjectRef Project, CreateLabelInput Input, Origin Origin)
    : ICommand<Result<LabelDto>>;
public sealed record CreateLabelInput(string Name, string? Color, Guid? Parent, string? Description,
                                      double? SortOrder, string? ExternalId, string? ExternalSource);

// src/modules/Projects/Plane.Projects.Contracts/Queries/FindLabelByExternalIdQuery.cs
public sealed record FindLabelByExternalIdQuery(ProjectRef Project, string ExternalId, string ExternalSource)
    : IQuery<Guid?>;

// src/modules/Projects/Plane.Projects/Labels/CreateLabelHandler.cs – Handler bleibt internal (R6)
internal sealed class CreateLabelHandler(ProjectsDbContext db, IUniqueViolationMap map)
    : ICommandHandler<CreateLabelCommand, Result<LabelDto>> { /* App- und v1-Logik identisch */ }

// src/modules/PublicApi/Plane.PublicApi/Endpoints/V1/V1LabelEndpoints.cs
internal static class V1LabelEndpoints
{
    public static void Map(PlaneEndpointRouteBuilder e)
    {
        var g = e.V1("workspaces/{slug}/projects/{project_id:guid}/labels").WithTags("Labels");
        g.MapPost("", Create).WithName("EP-0569").WithOriginalContract("A05:V-LBL-02")
         .WithOriginalOperationId("create_label")
         .RequirePermission(ProjectsPermissions.ProjectLabelCreate).Validate<V1LabelCreateRequest>();
    }

    static async Task<IResult> Create(IRequestScope scope, V1LabelCreateRequest body, ISender sender, CancellationToken ct)
    {
        // v1-Vorprüfung per Query (A05 V-LBL-02): Duplikat external_id/external_source → 409 mit id
        if (body.ExternalId is { Length: > 0 } && body.ExternalSource is { Length: > 0 }
            && await sender.Send(new FindLabelByExternalIdQuery(scope.Project, body.ExternalId, body.ExternalSource), ct) is { } existing)
            return PlaneErrors.PlainWith(409, V1ErrorTexts.LabelExternalIdExists, new Dictionary<string, object?> { ["id"] = existing })
                              .ToResult();

        var result = await sender.Send(new CreateLabelCommand(scope.Project, V1LabelMapper.ToInput(body), Origin.V1), ct);
        return V1ErrorMap.Map(result, V1LabelMapper.ToV1)          // 400 Name-Duplikat → 409 {"error", "id"} wie Original
                         .ToCreated();
    }
}
```

EP-Nummer und Original-ID entsprechen §4.19 (EP-0569 = `POST {V1P}/labels/`, `A05:V-LBL-02`). Prüfpunkt Spike S0: Der Mediator-Source-Generator (Abschnitt `02` §3.6) erzeugt Dispatch-Code für `CreateLabelCommand` aus `Plane.Projects.Contracts`, obwohl der Handler `internal` in `Plane.Projects` liegt (Generator läuft im Host-Projekt, das beide referenziert; Sichtbarkeit über `InternalsVisibleTo("Plane.Api")` laut `02`). Fällt S0 negativ aus, gilt die Rückfalloption aus §8 (R-D04-01).

### 5.4 Route-Inventar-Test – `tests/Plane.AppHost.Tests/Routing/RouteInventoryTests.cs`

```csharp
public sealed class RouteInventoryTests(PlaneApiFactory factory) : IClassFixture<PlaneApiFactory>
{
    static readonly Catalog Catalog = Catalog.Load("docs/plan/architecture/_data/endpoints.json");   // Spiegel von migration/…

    [Fact]
    public void Every_registered_row_exists_and_no_route_is_uncatalogued()
    {
        var routes = factory.Services.GetRequiredService<EndpointDataSource>().Endpoints.OfType<RouteEndpoint>()
            .Select(r => new RouteKey(r.Metadata.GetMetadata<HttpMethodMetadata>()!.HttpMethods.Single(),
                                      Normalize(r.RoutePattern.RawText!), r.Metadata.GetMetadata<EndpointNameMetadata>()?.EndpointName))
            .ToHashSet();
        var expected = Catalog.Rows.Where(x => x.Registered && x.Increment <= Increments.Current && x.Surface != "Live")
            .Select(x => new RouteKey(x.Method, x.FullTemplate, x.Ep)).ToHashSet();

        routes.Except(expected).Should().BeEmpty("jede Route braucht eine Katalogzeile (D04-ADR-01)");
        expected.Except(routes).Should().BeEmpty("jede registrierte Katalogzeile muss existieren");
    }

    [Theory, MemberData(nameof(UnregisteredRows))]
    public async Task Unregistered_row_answers_404_or_405(CatalogRow row)
    {
        using var client = factory.CreateAuthenticatedClient("admin@acme");
        var res = await client.SendAsync(new HttpRequestMessage(new HttpMethod(row.Method), row.SamplePath()));
        ((int)res.StatusCode).Should().Be(row.TargetStatus);
        (await res.Content.ReadAsStringAsync()).Should().Be(row.TargetStatus == 405
            ? $"{{\"detail\":\"Method \\\"{row.Method}\\\" not allowed.\"}}" : "{\"error\":\"Page not found.\"}");
    }

    [Fact]
    public void Metadata_matches_catalog() { /* Permission-Key, PaginationMetadata, ReadReplica, Rate-Limit-Policy, CacheControl, OriginalContract */ }

    public static TheoryData<CatalogRow> UnregisteredRows()
        => new(Catalog.Rows.Where(x => !x.Registered && x.Surface is not "Live"));
}
```

`Plane.Realtime` hat einen gleichartigen `RealtimeRouteInventoryTests` (Oberfläche Live). `CatalogRow.SamplePath()` setzt Seed-IDs aus `tests/seed/parity-seed.yaml` in die Platzhalter ein.

### 5.5 OpenAPI-Registrierung – `src/modules/PublicApi/Plane.PublicApi/OpenApi/OpenApiRegistration.cs`

```csharp
public static class OpenApiRegistration
{
    public static IServiceCollection AddPlaneOpenApi(this IServiceCollection s)
    {
        s.AddOpenApi("v1", o =>
        {
            o.OpenApiVersion = Microsoft.OpenApi.OpenApiSpecVersion.OpenApi3_1;
            o.ShouldInclude = d => d.ActionDescriptor.EndpointMetadata.OfType<SurfaceMetadata>().Any(m => m.Surface == ApiSurface.V1)
                                   && !string.Equals(d.HttpMethod, "PUT", StringComparison.OrdinalIgnoreCase)
                                   && d.RelativePath?.Contains("server", StringComparison.OrdinalIgnoreCase) != true;
            o.AddDocumentTransformer<V1DocumentInfoTransformer>();      // Titel "The funk. REST API", Tags (14), Servers (BRAND-API-01)
            o.AddDocumentTransformer<ApiKeySecuritySchemeTransformer>(); // "ApiKeyAuthentication": apiKey, header X-API-Key
            o.AddOperationTransformer<OriginalOperationIdTransformer>(); // OriginalOperationIdMetadata → operationId
            o.AddSchemaTransformer<OpenApiSchemaNameTransformer>();      // [OpenApiSchemaName("Issue")]
        });
        s.AddOpenApi("internal", o =>
            o.ShouldInclude = d => d.ActionDescriptor.EndpointMetadata.OfType<SurfaceMetadata>().Any(m => m.Surface != ApiSurface.V1));
        return s;
    }
}

// src/modules/PublicApi/Plane.PublicApi/Endpoints/OpenApi/OpenApiEndpoints.cs – EP-0711…0713, EP-0732
internal static class OpenApiEndpoints
{
    public static void Map(PlaneEndpointRouteBuilder e, IHostEnvironment env, IOptions<PlaneOpenApiOptions> opt)
    {
        if (opt.Value.Enabled)
        {
            var g = e.Root("api/schema");
            g.MapGet("", V1Document).WithName("EP-0711").WithOriginalContract("A05:W-03").AllowAnonymous().ExcludeFromDescription();
            g.MapGet("redoc", ScalarUi).WithName("EP-0712").WithOriginalContract("A05:W-05").AllowAnonymous().ExcludeFromDescription();
            g.MapGet("swagger-ui", ScalarUi).WithName("EP-0713").WithOriginalContract("A05:W-04").AllowAnonymous().ExcludeFromDescription();
        }
        if (env.IsDevelopment() || env.IsEnvironment("Test"))
            e.Root("api/schema/internal").MapGet("", InternalDocument).WithName("EP-0732")
             .WithOriginalContract("neu:D04-ADR-14").AllowAnonymous().ExcludeFromDescription();
    }
    // V1Document: format=json → JSON, sonst YAML (drf-spectacular-Default); Quelle IOpenApiDocumentProvider ("v1")
    // ScalarUi: statisches HTML aus eingebetteter Ressource (Scalar-Bundle, offline), Titel "The funk. REST API" (BRAND-API-04)
}
```

### 5.6 Erweiterungs-Interfaces an der API-Oberfläche

```csharp
// src/modules/WorkItems/Plane.WorkItems.Contracts/Query/IExpandProvider.cs (Signatur aus 16 §5.3, E-07)
public interface IExpandProvider { string Key { get; } ValueTask ExpandAsync(IReadOnlyList<Guid> ids, IDictionary<Guid, JsonObject> payloads, CancellationToken ct); }

// src/modules/WorkItems/Plane.WorkItems.Contracts/Query/IExpandAllowlistContributor.cs – Pakete ergänzen erlaubte Schlüssel je EP
public interface IExpandAllowlistContributor { IEnumerable<(string EndpointName, string Key)> Contribute(); }

// src/modules/WorkItems/Plane.WorkItems.Contracts/PublicApi/IV1PayloadExtension.cs (E-07) – ergänzt v1-Antworten additiv
public enum V1Resource { Project, State, Label, WorkItem, WorkItemComment, WorkItemLink, WorkItemActivity, Cycle, Module, Intake, Member }
public interface IV1PayloadExtension
{
    V1Resource Resource { get; }
    ValueTask ExtendAsync(IReadOnlyList<Guid> ids, IDictionary<Guid, JsonObject> payloads, CancellationToken ct);  // nur neue Felder
}

// src/modules/WorkItems/Plane.WorkItems.Contracts/Query/IV1FilterParameterBinding.cs (16 §5.5, E-19) – CE: keine Implementierung
public interface IV1FilterParameterBinding { string QueryParameter { get; } string ParserName { get; } }
```

Regel für alle Erweiterungs-Interfaces: Die CE registriert für `IV1PayloadExtension` und `IV1FilterParameterBinding` **keine** Implementierung (Antworten 1:1 Original); `ExtensionNoopTests` (`tests/Plane.PublicApi.Tests/`) prüft, dass v1-Goldens ohne Paket unverändert bleiben (`16` AK-16-xx).

### 5.7 Parity-Szenario und Abweichungseintrag

```yaml
# tests/contracts/scenarios/projects/project-invitations.yaml   (DT-PRJ-01: Original 500 → funk. 201 + Mail)
id: projects.project-invitations-create
ce: [CE-PRJ-010]
inc: I1
seed: parity
steps:
  - name: invite-member
    as: admin@acme
    request:
      method: POST
      path: /api/workspaces/{ws:acme}/projects/{prj:acme/WEB}/invitations/
      json: { emails: [ { email: "new.member@example.test", role: 15 } ] }
    expect: { status: 200 }
  - name: invite-as-guest
    as: guest@acme
    request: { method: POST, path: /api/workspaces/{ws:acme}/projects/{prj:acme/WEB}/invitations/, json: { emails: [] } }
    expect: { status: 403 }
```

```yaml
# tests/contracts/deviations.yaml (Auszug)
- id: DEV-API-19
  scope: "POST /api/workspaces/{slug}/projects/{project_id}/invitations/"
  kind: status-change
  from: 500
  to: 200
  reason: "Original wirft AttributeError (QuerySet ohne Einladungsobjekt); repariert, Mail-Job T33 wird ausgelöst"
  decision: "04#DT-PRJ-01"
  approved_by: "auftraggeber/2026-10-23 (Z-12)"
- id: DEV-API-63
  scope: "GET /api/workspace-slug-check/"
  kind: replace
  path: "$.status"
  reason: "reservierte Slugs vereinheitlicht (login, register, signin)"
  decision: "04#DT-WS-09"
```

Der Erfolgsstatus 200 von `POST {P}/invitations/` (EP-0196, Spalte „Status Orig→Ziel“ `500→200`) folgt dem Workspace-Pendant EP-0128. Da das Original für diese Route kein Golden liefern kann (500), wird der Schritt `invite-member` als Ziel-Golden aufgezeichnet (`record --target funk`, Kennzeichnung `golden_source: target` mit Verweis auf DEV-API-19, `15` §3.6.5 Regel 1).

### 5.8 TS-Vertragsprüfung – `frontend/tools/contract-check/checks/labels.check.ts`

```ts
import type { paths } from '../generated/internal';
import type { IIssueLabel } from '@plane/types';            // Pfad-Alias auf frontend/libs/shared/types
import type { AssertAssignable, ResponseOf, RequestOf } from '../lib/assert';

// EP-0178 GET {P}/issue-labels/
type ListLabels = ResponseOf<paths, '/api/workspaces/{slug}/projects/{project_id}/issue-labels/', 'get'>;
export type _ep0178 = AssertAssignable<ListLabels, IIssueLabel[]>;

// EP-0179 POST {P}/issue-labels/
type CreateLabelBody = RequestOf<paths, '/api/workspaces/{slug}/projects/{project_id}/issue-labels/', 'post'>;
export type _ep0179 = AssertAssignable<Partial<IIssueLabel>, CreateLabelBody>;   // Frontend-Body passt zum Server-Body
```

`lib/assert.ts`: `type AssertAssignable<A, B> = [A] extends [B] ? true : { error: 'not assignable'; from: A; to: B }` und Export-Prüfung `const _: true = null! as _ep0178` je Datei (Fehler beim `tsc --noEmit`). Die Prüfdateien entstehen je Inkrement für alle Endpunkte mit Frontend-Aufruf.

---

## 6. Erweiterungspunkte für Bezahl-Pakete

Kein Fachdesign; nur die **API-seitigen** Andockstellen der strukturell relevanten Pakete, damit die CE-Verträge sie ohne Umbau aufnehmen. Paketnamen und Wellen nach `16` §4. Allgemein gilt: (1) neue Routen nur unter den in `16` §3.2.2 reservierten Präfixen, jeweils mit neuer Katalogzeile (`EP-nnnn` am Ende, D04-ADR-01); (2) bestehende Antworten nur **additiv** (neue Felder über `IWorkItemPayloadExtension`/`IProjectPayloadExtension`/`IV1PayloadExtension`, nie Umbenennung, D04-ADR-18); (3) neue Fehlercodes in den reservierten Bereichen (`02` §3.8.3; Auth 5200–5299); (4) `deviations.yaml` erlaubt ab W1 nur `added-field`/`added-endpoint` mit `decision: "F30#<Paket>"` (`15` §3.6.5). Abgleich der reservierten Präfixe mit dem Katalog am 23.10.2026: keine registrierte CE-Route liegt darunter (Treffer per Teilstring wie `project-roles`, `pages/{page_id}/duplicate/`, Space-`votes` und die eigene Oberfläche `Integrations` sind keine Präfix-Überschneidungen).

| Paket | API-Andockstelle in der CE | betroffene Katalogzeilen | bleibt in der CE unverändert |
|---|---|---|---|
| **A1** Work-Item-Types & Custom Properties | `type_id` wie Original: App-Work-Item-DTOs ohne `type_id` (Original-App-Serializer liefern es nicht), v1-`IssueSerializer` mit `type_id` (lesend und schreibend, CE-Wert immer `null`, `A05` §2.4); Paket ergänzt App-`type_id` und Property-Werte über `IWorkItemPayloadExtension` (App) bzw. `IV1PayloadExtension` (V1); schreibend gilt in der CE wie im Original: `type_id` ≠ `null` → Feldfehler `Invalid pk "<id>" - object does not exist.` (es gibt keine Typen); neue `expand`-Schlüssel (`type`, `properties`) über `IExpandProvider` + `IExpandAllowlistContributor` (§5.6); Filterfelder `type_id`, `property__<id>` über `IFilterFieldProvider`; Routen unter `{P}/work-item-types/`, `{P}/work-item-properties/`, `{P}/issues/{issue_id}/property-values/` | EP-0260…EP-0274 (Work-Item-Listen/Details), EP-0648…EP-0657 (v1) | CE-Goldens ohne Paket identisch (`ExtensionNoopTests`) |
| **A2** Workspace-Types, Hierarchie | Routen `{W}/work-item-types/`, `{W}/work-item-properties/`; Typ-Scope über `ScopeRef` | – | – |
| **A9** Relationen & Abhängigkeiten | Relationstyp-Katalog (`16` §5.3) speist Validierung von `relation_type` an EP-0281 und v1-Relationen; neue Typen erscheinen in der Listen-Antwort von EP-0280 als zusätzliche Schlüssel (additiv); Routen `{W}/relation-types/`, `{P}/issues/{issue_id}/dependencies/` | EP-0280…EP-0283, v1-Relationen §4.19 | Antwortschlüssel der 10 CE-Typen (`blocking` … `implemented_by`) |
| **A17** Workspace-Governance States/Labels | CE registriert `GET {W}/states/` und `GET {W}/labels/` nur lesend; schreibende Methoden unter diesen Pfaden sind reserviert (ergeben in der CE 405) | Lese-Zeilen in §4.3/§4.4 | Lese-Antworten |
| **B1** Teamspaces | Query-Parameter `teamspace_id` an Views/Pages/Favoriten wird in der CE **ignoriert** (nicht abgelehnt), damit Paket-Frontends ohne Versionsweiche aufrufen können; Scope-Auflösung über `IScopeAncestorContributor`; Route `{W}/teamspaces/` | Views §4.6, Pages §4.10, Favoriten §4.3 | Antworten ohne `teamspace_id` |
| **B6** Erweiterte Filter, PQL | App: Rich-Filter-Parser-Registry (`IFilterParser`), neue Operatoren additiv; V1: `IV1FilterParameterBinding` hebt die Original-400 für `pql`/`filters` auf (`16` §5.5); Routen `{W}/pql/`, `{W}/advanced-search/` | EP-0260, EP-0298, EP-0324, EP-0352 (Rich-Filter), EP-0648/EP-0653 (v1) | Fehlercodes der Rich-Filter-Validierung |
| **C1** Workflows | alle State-Wechsel aller Endpunkte (App, V1, Intake, Cycle-Transfer, Bulk) laufen über `IWorkItemStateChanger`; ein `IStateTransitionGuard` liefert Ablehnungen als `PlaneErrors.Coded` mit neuem Code im reservierten Bereich; Route `{P}/workflows/` | EP-0267, EP-0255, EP-0651/EP-0656, Intake-Statuswechsel §4.9, Cycle-Transfer §4.7 | CE-Statuswechsel ohne Guard |
| **C3** Automation-Engine | konsumiert Integration-Events (`16` §3.2.4); API-seitig nur Routen `{W}/automations/`, `{P}/automations/`; automatisch ausgelöste Änderungen tragen `Origin.Automation` (Activity, Webhook-`actor`) | – | Webhook-Payloads der CE-Ereignisse |
| **D1** Wiki & Collections | Page-DTOs enthalten `workspace`-Bezug wie Original; Workspace-Pages-Routen `{W}/pages/`, `{W}/wiki/`, `{W}/collections/` reserviert; Page-Zugriff über `PageAccessRule` (`05`) | Pages §4.10 | Projekt-Page-Verträge |
| **D2** Nested Pages | Feld `parent_id` an Page-DTOs bleibt wie Original (CE setzt es, DT-PAGE-07 validiert es); Route `…/pages/{page_id}/move/` reserviert | EP-0395 ff. (§4.10) | – |
| **E3** IdP Group Sync, SCIM | eigene Oberfläche `/api/scim/v2/` mit eigener Authentisierung (Präfix reserviert, `16` §3.2.2); `{W}/group-sync/` | – | Mitglieder-Endpunkte §4.3 |
| **E5** RBAC/Custom Roles | Rollenwerte `role: 20/15/5` in allen Mitglieder-DTOs bleiben; Custom Roles erscheinen zusätzlich als `role_id` (additiv); Permission-Keys aller Zeilen (Spalte „Permission“) sind die Grants (`05` §3.13); Routen `{W}/roles/`, `{W}/permission-schemes/`, `{W}/permissions/me/` | alle Zeilen (Permission-Key) | DenyStyle und Fehlerkörper |
| **F1** Integrations-Framework | Oberfläche `Integrations` und Route EP-0729 ab I0 (ohne Provider 404 `{"error": "Page not found."}`), `IWebhookIngress`/`IWebhookSignatureVerifier`, Rate-Limit `integration_webhook`, Inbox-Idempotenz; Work-Item-Detail-Feld für externe Links über `IIntegrationLinkProvider` (CE `[]`, nicht im CE-DTO) | EP-0729 | – |
| **F2** Forgejo | Provider `forgejo` auf EP-0729 (`/api/integrations/forgejo/webhooks/{connection_id}/`), Verwaltungsrouten `{W}/integrations/forgejo/…` | EP-0729 | – |
| **G1** AI-Basis | CE-Endpunkte EP-0726/EP-0727 (`ai-assistant`) bleiben Original-Vertrag; Such-Provider-Austausch über `ISearchProvider` ohne Vertragsänderung an EP-0509/EP-0508/EP-0272/EP-0671/EP-0672; Route `{W}/ai/` reserviert | §4.17, §4.22 | Antwortformen der Suche |
| **H1** OAuth-App-Plattform | Bearer-Schema an V1 (`Plane:Auth:Bearer:Enabled`), `Permission.ApiScope` je V1-Zeile ergänzbar (Spalte Permission), Security-Schema `OAuth2` im `v1`-OpenAPI-Dokument additiv; Routen `{W}/apps/`, `/api/users/me/app-authorizations/`, `/api/marketplace/` | alle V1-Zeilen | API-Key-Vertrag |
| **H6** Realtime-Event-Server | EP-0414 `/live/events/` ab I0 registriert (SignalR, nur WebSockets, Gruppen-Autorisierung per `IPermissionEvaluator`); REST-Antworten bleiben unverändert (Events sind zusätzliche Kanäle, keine Ersatz-Antworten) | EP-0414 | alle REST-Verträge |

**Nicht in der CE:** `Idempotency-Key`-Semantik und `/api/v2/` (H3, `16` §4), GraphQL, MCP (H4). Die CE-Pipeline ignoriert `Idempotency-Key` (D04-ADR-11); H3 aktiviert ihn nur auf der eigenen Oberfläche `V2`.

---

## 7. Akzeptanzkriterien & Tests

| ID | Kriterium (messbar) | Test (Projekt / Klasse) | Ink. |
|---|---|---|---|
| AK-D04-01 | Jede Zeile von `endpoints.json` mit `registered = true` und `increment ≤ CURRENT_INCREMENT` existiert als Route mit Methode, Route-Template und Name `EP-nnnn`; keine Route ohne Katalogzeile (0 Abweichungen) | `tests/Plane.AppHost.Tests/Routing/RouteInventoryTests.Every_registered_row_exists_and_no_route_is_uncatalogued`; `tests/Plane.Realtime.Tests/Routing/RealtimeRouteInventoryTests` | I0 ff. |
| AK-D04-02 | Jede Zeile mit `registered = false` liefert `target_status` (404/405) mit exakt dem Körper aus §3.5; die 85 Nebenprodukte aus §4.25 eingeschlossen | `RouteInventoryTests.Unregistered_row_answers_404_or_405` | I0 ff. |
| AK-D04-03 | Metadaten je Route (Permission-Key, Pagination-Modus + Default, `UseReadReplica` bei den 79 Read-Replica-Zeilen, Rate-Limit-Policy, `Cache-Control` an den 5 Zeilen aus §3.4, `WithOriginalContract`) stimmen mit `endpoints.json` überein | `RouteInventoryTests.Metadata_matches_catalog` | I0 ff. |
| AK-D04-04 | Parity-Harness: 100 % der registrierten Zeilen bis `CURRENT_INCREMENT` haben ≥ 1 Szenario; Replay ohne nicht genehmigte Abweichung | `Plane.Tools.ParityHarness coverage --fail-under 100` (ab I7 Gate; davor Report), `replay` je Modul | I0 (5 EP), I1–I7 |
| AK-D04-05 | Jede DT-Zeile mit Abweichungs-ID und Vertragswirkung hat ≥ 1 `deviations.yaml`-Eintrag mit `decision: "04#<DT-ID>"`; kein Eintrag ohne DT-Zeile oder ADR | `DeviationCatalogTests` (`tests/Plane.Tools.ParityHarness.Tests/`) gegen `_data/04-decisions.json` | I0 ff. |
| AK-D04-06 | Jede DT-Zeile der Kategorie S hat einen Test, der den Angriffsfall (fremder Workspace/Projekt, Gast, anonym) mit dem Ziel-Status prüft (Testname in Spalte „Test“) | Tests laut DT-Tabelle; `SecurityRegressionSuite` (Trait `Category=Security`) | je Ink. der DT-Zeile |
| AK-D04-07 | Fehlertexte: jeder Text aus `documented_bodies` registrierter Zeilen existiert als Konstante in `<M>ErrorTexts` (Ausnahmen nur über `replaced-texts.txt` mit DT-Verweis); kein String-Literal in `PlaneErrors.*`-Aufrufen | `ErrorTextCatalogTests` je Modul; Analyzer `PLANE0004` | I1 ff. |
| AK-D04-08 | Pagination: alle Zeilen mit `pagination ≠ null` liefern das Envelope gemäß Modus; `cursor-when-requested` liefert ohne beide Parameter ein Array; `cursor-required` liefert ohne beide Parameter 400; `global` mit `per_page=0` → 400 (DT-GEN-11) | `PaginationModeTests` (`tests/Plane.BuildingBlocks.Tests/Pagination/`) + Szenarien | I1/I2 |
| AK-D04-09 | `expand`: nur die Werte aus §3.9 wirken; unbekannte Werte werden ignoriert; v1-`fields` reduziert Felder an den 25 Zeilen aus §3.9 und wirkt an keiner anderen v1-Zeile | `ExpandAllowlistTests`, `V1FieldSelectionTests` | I2/I6 |
| AK-D04-10 | Rate-Limits: `anon` 30/min, `authentication` 10/min an allen registrierten Auth-Zeilen außer EP-0001/EP-0002, `api_key` 60/min an allen V1-Zeilen mit `X-RateLimit-*`, `asset_duplicate` 5/min an EP-0430, `integration_webhook` 600/min an EP-0729; 429-Körper coded 5900 | `RateLimitTests` (`02` AK-15) mit Katalog-Datenquelle | I0/I1/I6 |
| AK-D04-11 | API-Keys: Header-Name case-insensitiv; ohne Header 401, ungültig 403 `{"detail": "Given API token is not valid"}`; Token nur in der Anlage-Antwort; `token_hash` gespeichert, kein Klartext in DB (Prüfung per SQL auf `api_tokens`) | `ApiKeyAuthenticationTests` (`tests/Plane.Identity.Tests/`) | I6 (Schema I0) |
| AK-D04-12 | OpenAPI `v1`: (Pfad, Methode)-Menge = Original-Golden minus DT-V1-01/-02/-03; `operationId`, Tags (14) und Parameternamen gleich; `info.title` = „The funk. REST API“; Build-Artefakt ohne Drift | `OpenApiDocumentTests` (`tests/Plane.PublicApi.Tests/OpenApi/`), CI-Schritt `git diff --exit-code src/hosts/Plane.Api/openapi/` | I6 (internal: I0) |
| AK-D04-13 | TS-Verträge: `contract-check` erzeugt Typen aus beiden Dokumenten, alle `*.check.ts` kompilieren; jeder Frontend-Aufruf aus `generated/frontend-calls.json` trifft eine registrierte Zeile oder steht in §4.26 | `pnpm --filter contract-check test` (CI-Job `frontend`) | I0 ff. |
| AK-D04-14 | Webhook-Ausgang: je Ereignis aus §4.27 löst jeder genannte App- und V1-Endpunkt genau die dort genannte Zustellung aus; nicht genannte Endpunkte lösen keine aus; Header/Body/Signatur wie §3.17 | `WebhookContractTests` (`tests/Plane.Webhooks.Tests/Contract/`), `WebhookTriggerCoverageTests` | I6 |
| AK-D04-15 | Branding: kein `\bPlane\b` in `openapi/v1.json`, `*ErrorTexts.cs` und Mail-Betreffs außer Protokollbezeichnern (§3.20) | `BrandingTests.ApiTexts` | I0 ff. |
| AK-D04-16 | CE-Abdeckung: 301 + 119 + 87 = 507 (§4.28); jede CE-ID aus `ce-features.json` ist einer Katalogzeile, der Frontend-Bereichsliste oder einer Zeile in §4.28 zugeordnet | `CeCoverageTests` (`tests/Plane.AppHost.Tests/Catalog/`) | I0 |
| AK-D04-17 | Reservierte Präfixe (`16` §3.2.2) enthalten keine CE-Route; Requests dorthin → 404 | `RouteReservationTests` (`16`) mit `endpoints.json` als zweiter Quelle | I0 |
| AK-D04-18 | Tote Frontend-Aufrufe (§4.26, außer `active-cycles`) liefern 404 `{"error": "Page not found."}` | `DeadFrontendCallsTests` | I1–I6 |

**Testprojekte (neu oder ergänzt durch dieses Dokument):** `tests/Plane.AppHost.Tests` (Ordner `Routing/`, `Catalog/`), `tests/Plane.Realtime.Tests/Routing/`, `tests/Plane.PublicApi.Tests` (`OpenApi/`, `V1/`), `tests/Plane.Webhooks.Tests/Contract/`, `tests/Plane.<M>.Tests/Errors/` je Modul, `tests/Plane.Tools.ParityHarness.Tests/`, `frontend/tools/contract-check/` (Vitest + `tsc`). Testdaten: `tests/contracts/scenarios/**`, `tests/contracts/deviations.yaml`, `tests/contracts/openapi/v1.original.json`, `tests/contracts/reserved-slugs.json`.

---

## 8. Risiken & offene Punkte

### 8.1 Risiken

| ID | Risiko | Eintritt / Wirkung | Gegenmaßnahme |
|---|---|---|---|
| R-D04-01 | Mediator-Source-Generator erzeugt keinen Dispatch für Contract-Commands aus fremden Assemblies mit `internal` Handlern (D04-ADR-04) | mittel / hoch (v1-Adapter blockiert) | Spike S0 (Ergänzung zu `17` Z-01); Rückfall: Fach-Module exportieren je Contract-Command eine `public static class <M>CommandDispatch` mit typisierten Methoden (`Task<Result<LabelDto>> CreateLabelAsync(...)`), die intern den Handler aufrufen – gleiche Contracts, kein Zugriff auf interne Typen |
| R-D04-02 | Heuristische Frontend-Erkennung (`frontend_call_detected`) übersieht dynamisch gebaute Pfade; Portierungskriterium (a) falsch angewendet | mittel / mittel | maßgeblich ist `contract-check` ab I0 (§3.15); Korrektur der Katalogzeile vor Umsetzung des Inkrements; Nicht-Registrierung nur bei T-Zeilen mit nachgewiesener Fehlfunktion |
| R-D04-03 | Pagination-Modus einzelner Listen falsch klassifiziert (z. B. Original paginiert nur bei bestimmten Query-Parametern) | mittel / mittel | Goldens mit und ohne `per_page`/`cursor` für jede Listen-Zeile; Abweichung → Katalogkorrektur |
| R-D04-04 | `operationId`s des Original-Schemas nicht deterministisch (drf-spectacular erzeugt Namen aus Views, wenn `@extend_schema` fehlt) | niedrig / mittel | Golden `v1.original.json` einmalig erzeugen und einchecken; Vergleich gegen die Datei, nicht gegen einen Neu-Export |
| R-D04-05 | `documented_bodies` stammt aus Analyse-Tabellen; Statuszuordnung teilweise ungenau (z. B. 204 mit Fehlertext an EP-0420) | hoch / niedrig | Golden ist maßgeblich (§3.6 Nr. 2); `ErrorTextCatalogTests` prüft nur Existenz der Texte, nicht Status |
| R-D04-06 | Korrigierte Original-Fehler (F) ohne Golden (Original liefert 500) | hoch / mittel | Ziel-Goldens mit `golden_source: target` + Verweis auf DEV-ID (§5.7); Review durch Auftraggeber-Vertretung je Inkrement |
| R-D04-07 | Alias-Routen verdoppeln Szenario-Aufwand (v1 `issues`/`work-items`, App `inbox`/`intake`) | hoch / niedrig | Szenario-Vorlagen mit Pfad-Matrix (`paths: [...]` je Schritt), Harness-Erweiterung in `15` (§9) |
| R-D04-08 | `.NET`-Binding beantwortet ungültiges JSON vor der Permission-Prüfung (DT-GEN-14) – Statusreihenfolge 400 vs. 403 weicht ab | niedrig / niedrig | dokumentiert (`DEV-JSON-002`), Goldens prüfen nur mit gültigem JSON auf 403 |
| R-D04-09 | Neue Routen in Paketen ohne Katalogzeile | mittel / mittel | `RouteInventoryTests` bricht; Katalog ist Teil der Paket-Definition of Done (`16`) |

### 8.2 Offene Punkte

| ID | Frage | Empfehlung | Entscheider | bis |
|---|---|---|---|---|
| O-D04-01 | Ergebnis Spike S0 zum Contract-Command-Dispatch (R-D04-01) | Variante Contract-Commands; Rückfall `<M>CommandDispatch` | Architektur | Ende S0 |
| O-D04-02 | Umbenennung der Protokollbezeichner `X-Plane-*`, `plane_api_`, `plane_wh_` im Zuge von ADR-009B | **nicht** umbenennen (Bestandsintegrationen) | Auftraggeber | vor I6 |
| O-D04-03 | Soll `GET /api/schema/` ohne `Plane:OpenApi:Enabled` 404 liefern (Original-Default) oder in `funk.` standardmäßig an sein | Original-Default (aus) beibehalten | Auftraggeber | vor I6 |
| O-D04-04 | Gruppensummen-Quirk `DEV-GRP-001` (0→1) korrigieren (Z-12) | korrigieren (Empfehlung an `02` O-D02-04) | Auftraggeber über `02` | vor I2 |
| O-D04-05 | Status nach Reparatur von `POST {P}/invitations/` (200 wie Workspace-Pendant oder 201) | 200 (Frontend erwartet keine 201-Unterscheidung) | Architektur | vor I1 |
| O-D04-06 | Ziel-Goldens für im Original fehlschlagende Routen (Mechanik im Harness) | `golden_source: target` als Szenario-Feld (`15`) | Test-Architektur | vor I1 |
| O-D04-07 | Interne OpenAPI auch in Produktion abrufbar (für Betreiber-Integrationen)? | nein (nur Dev/Test) | Auftraggeber | vor I6 |

---

## 9. Abhängigkeiten zu anderen Dokumenten (02–16)

| Dokument | Richtung | was dieses Dokument nutzt | was dieses Dokument liefert / Rückmeldung |
|---|---|---|---|
| `02-backend-solution-und-konventionen.md` | nutzt + liefert | Oberflächen, `PlaneEndpointRouteBuilder`, Pipeline, `PlaneErrors`, Paginator, Query-Engine, Rate-Limit-Policies, Analyzer | Katalog je Endpunkt; **Rückmeldungen:** (1) `.WithOriginalContract` im Format `<Dok>:<ID>` (02-Beispiel `"L1"` → `"A04:L1"`), Analyzer `PLANE0005`/`PLANE0006`; (2) `PaginationMode` um `CursorGrouped`, `Required`, `Global` ergänzen und `.WithPagination(...)`/`.WithExpand(...)`/`.WithOriginalOperationId(...)` in `Plane.BuildingBlocks.Web/Endpoints/CatalogMetadata.cs` aufnehmen (§5.1); (3) v1-Adapter über öffentliche Contract-Commands (D04-ADR-04) in die Modul-Schablone übernehmen; (4) Handler-Namen laut Katalog (z. B. `ListLabelsQuery` statt `ListProjectLabelsQuery` im 02-Beispiel); (5) `DEV-GRP-001` (0→1) korrigieren (O-D02-04); (6) Header-Schreibweise `X-API-Key` wie Original-OpenAPI (02 nennt `X-Api-Key`, funktional gleich) |
| `03-datenmodell-efcore.md` | liefert an | Tabellen-/Spaltennamen für DTO-Projektionen | `api_tokens.token_hash` + `token_prefix` (D05-ADR-16), `webhook_logs` mit JSON-Spalten (DEV-WH-002), `reserved`-Slug-Liste ist Code, keine Tabelle; Antwort auf A02a-#22: `WorkspaceProjectDeployBoardEndpoint` (DT-SPACE-01) wird nicht registriert |
| `05-auth-sicherheit-berechtigungen.md` | nutzt + liefert | Permission-Keys und Ziel-Prüfung je Endpunkt (Anhang B), SEC-/HARM-Korrekturen, Auth-Endpunkte N-01…N-14, API-Key-Prüfung | **Rückmeldungen:** (1) Anhang B führt 8 v1-Estimate-Zeilen, die im Original nicht geroutet sind (DT-V1-01) – als „entfällt“ markieren; (2) als „entfällt“ markieren: `project.intake.create` (`A04:N2`, DT-INT-01), `project.cycle/module/view.read_favorites` (`Y12`/`M15`/`W14`, DT-GEN-15), Anhang-Detail-GET `K9` (DT-WI-10), Modul-Link-PUT `M14` (DT-GEN-01), alle Nebenprodukt-Zeilen §4.25; (3) Header-Schreibweise `X-API-Key` |
| `06-hintergrundjobs-events-benachrichtigungen.md` | nutzt + liefert | Trigger-Tabelle Webhooks, Zustellung, Mail-Jobs, Recents/Activity | auslösende Endpunkte je Webhook-Ereignis + before-Form (§4.27, beantwortet O-D06-07); **Rückmeldungen:** (1) Mail-Job T33 (Projekt-Einladung) erhält mit der Reparatur DT-PRJ-01 einen Auslöser; (2) Operationswerte `put`/`put_create` (`UpsertWorkItemCommand`) haben in der CE keinen Auslöser (DT-V1-02) |
| `07-realtime-kollaboration-dokumente.md` | nutzt | Live-Endpunkte, Management-Port, Page-Dokumentverhalten | Katalogzeilen §4.10–§4.12, DT-RT-01…03 |
| `08-frontend-angular-architektur.md` | nutzt + liefert | Service-Port, `contract-check`, AK-D08-16 | **Rückmeldungen:** (1) `contract-check` erzeugt zusätzlich `generated/frontend-calls.json` und prüft gegen `endpoints.json` (§3.15); (2) FE-E4 serverseitig umgesetzt als DT-WS-09 (eine Slug-Liste, Golden `tests/contracts/reserved-slugs.json`); (3) `GET {P}/issues/{issue_id}/meta/` (Legacy-Redirect) ist EP-0263 |
| `09-ui-paritaet-designsystem.md` | liefert an | – | Profil-/Theme-Endpunkte (§4.1), `GET /api/instances/` (EP-0077), Asset-URLs (§3.4 Nr. 4) |
| `10-editor-angular.md` | liefert an | – | Asset-Endpunkte §4.13, Entity-Suche EP-0508, Page-Description-Endpunkte §4.10 |
| `11-suche-und-ai-basis.md` | liefert an | Such-Provider-Abstraktion | Verträge SR-01/-02/-03 (EP-0509, EP-0272, EP-0508), v1-Suche EP-0671/EP-0672, AI/Unsplash EP-0726…EP-0728 (§4.22) inkl. DT-AI-01 |
| `12`/`13` (Fachdokumente laut `01` Anhang A, soweit vorhanden) | – | – | Katalogzeilen ihrer Module (§4) |
| `14-infrastruktur-deployment-betrieb.md` | nutzt + liefert | Gateway-Regeln G-01…G-17, Body-Limit, OG-Meta | öffentliche Sonder-Endpunkte (§3.19): EP-0520 (OG-Meta), EP-0729 (Integrations), EP-0002 (Backchannel, extern gesperrt), EP-0415/EP-0417 (Proxy-Upload), EP-0731 |
| `15-teststrategie-qualitaet-paritaet.md` | nutzt + liefert | Parity-Harness, Szenario-Format, `deviations.yaml` | `endpoints.json` als `coverage`-Quelle (stabile Schlüssel `ep` + Methode + `route_template`), DT-IDs; **Rückmeldungen:** (1) Beispiel `DEV-0001` (`is_google_enabled`) als `kind: replace` statt `removed-field` führen, weil DT-AUTH-03 die Flags mit `false` beibehält; (2) DT-PAGE-07 ist jetzt definiert (ungültige Referenzen → 400); (3) Szenario-Feld `golden_source: target` für im Original fehlschlagende Routen (O-D04-06); (4) optionale Pfad-Matrix für Alias-Zeilen (R-D04-07) |
| `16-erweiterungspunkte-bezahl-features.md` | nutzt + liefert | X8, reservierte Präfixe §3.2.2, E-01/E-07/E-08/E-13/E-19/E-25 | §6 (API-Andockstellen), `IExpandAllowlistContributor` als Ergänzung zu E-07, `IV1PayloadExtension`-Signatur (§5.6), Liste toter Aufrufe (§4.26, Antwort auf `16` §4.3); **Rückmeldung:** v1-Estimates sind im Original nicht geroutet – kein Paket muss sie „reservieren“, ein späteres Paket kann sie als neue Zeilen ergänzen |
| `17-abgleich-dokumentuebergreifend.md` | nutzt | Z-12 (sichtbare Bugs korrigieren), ABG-011, ABG-043 | ABG-011 für 04 erledigt (`_data/endpoints.json` liegt vor); ABG-043 entschieden: `PUT {P}/issue-labels/{pk}/` nicht registriert (DT-GEN-01, EP-0223, 405) |
