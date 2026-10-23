# 11 – Suche und AI-Basis (CE)

> **Status:** Entwurf zur Abnahme (Fachdokument D11). Verbindlich innerhalb seines Themas; nachrangig zu `00-grundsatzentscheidungen.md` (ADR-000 … ADR-009), `01-zielarchitektur-und-tech-stack.md` (ADR-010 … ADR-052) und `17-abgleich-dokumentuebergreifend.md`. Bei Widerspruch gilt 00 > 01 > 17 > dieses Dokument. Namen und Schnittstellen der fertigen Nachbardokumente 02, 05, 08, 09, 14, 15, 16 sind übernommen; wo dieses Dokument sie präzisiert, steht ein Änderungsauftrag in §9.2.
> **Stand:** 23.10.2026. Versionsangaben mit „⚠“ werden in Spike S0 per NuGet-/npm-Metadaten bestätigt (Regel 01 §8).
> **Zielrepository:** Alle Pfade für Zielcode sind relativ zur Wurzel des neuen Repositorys **`funk.`** (ADR-009). `BE/` = `funk./src/`, `FE/` = `funk./frontend/`, `T/` = `funk./tests/`. Pfade des Originals: `API/` = `apps/api/plane/`, `WEB/` = `apps/web/`, `ADM/` = `apps/admin/`, `PKG/` = `packages/` (Referenz `/home/user/plane`, ADR-006).
> **Quellen (gelesen):** A03 §2.11, §3.14, §3.17, §3.19 (Q-27, Q-28, Q-35, Q-36); A06 §2.13 (`issue_search`); A05 (v1-Suche); CE-Katalog `features/_data/ce-features.json` (CE-SRCH-001…009, CE-AI-001/-002, CE-API-019, CE-INST-025/-026, CE-UIX-009, CE-PAGE-034, CE-WI-008/-031/-044/-048); Originalcode `API/app/views/search/{base,issue}.py`, `API/utils/issue_search.py`, `API/app/views/external/base.py`, `API/api/views/issue.py` (`IssueSearchEndpoint`), `API/utils/instance_config_variables/core.py`, `API/license/api/views/instance.py`, `WEB/components/power-k/**`, `WEB/services/{workspace,ai,file}.service.ts`, `WEB/services/project/project.service.ts`, `WEB/components/core/modals/{gpt-assistant-popover,existing-issues-list-modal,bulk-delete-issues-modal}.tsx`, `WEB/components/issues/issue-modal/components/description-editor.tsx`, `WEB/hooks/{use-editor-flagging.ts,editor/use-editor-mention.tsx}`, `ADM/app/(all)/(dashboard)/{ai,image}/*`; Commercial-API-Referenz `developer-docs/docs/api-reference/issue/advanced-search-work-items.md`.
> **Sprache:** Fließtext Deutsch, Bezeichner Englisch.

## Inhaltsverzeichnis

1. [Ziel & Scope](#1-ziel--scope)
2. [Entscheidungen (D11-ADR-01 ff.)](#2-entscheidungen-d11-adr-01-ff)
3. [Detaildesign](#3-detaildesign)
   - 3.1 Bausteine und Projektschnitt
   - 3.2 Textabgleich-Semantik (Port `icontains`, Sequenz-IDs, DRF-`SearchFilter`)
   - 3.3 Such-Abstraktion (`ISearchProvider`, Profile, Routing, Hydrierung)
   - 3.4 Globale Suche SR-01 (CE-SRCH-001)
   - 3.5 Entity-Suche SR-03 (CE-SRCH-002)
   - 3.6 Work-Item-Picker-Suche SR-02 (CE-SRCH-003)
   - 3.7 Public-API-Suche v1 (CE-API-019)
   - 3.8 Sichtbarkeit und Berechtigungen
   - 3.9 Trigramm-Indizes und SQL-Pläne
   - 3.10 Indexierungs-Pipeline (`search_documents`)
   - 3.11 Frontend: Power-K-Suche
   - 3.12 Frontend: Mentions und Picker
   - 3.13 AI-Konfiguration (Instanz-Keys, Provider-Auflösung)
   - 3.14 AI-Client-Aufbau (`Microsoft.Extensions.AI`, SSRF-Client, Laufzeitwechsel)
   - 3.15 KI-Assistent EXT-03/EXT-02 (CE-AI-001)
   - 3.16 Unsplash EXT-01 (CE-AI-002)
   - 3.17 Frontend: KI-Assistent, Bild-Picker, God-Mode-Formulare
   - 3.18 Options-Klassen
   - 3.19 Observability, Datenschutz, Betrieb
4. [Vollständige Mapping-Tabellen Original → Ziel](#4-vollständige-mapping-tabellen-original--ziel)
5. [Code-Skelette](#5-code-skelette)
6. [Erweiterungspunkte für Bezahl-Pakete](#6-erweiterungspunkte-für-bezahl-pakete)
7. [Akzeptanzkriterien & Tests](#7-akzeptanzkriterien--tests)
8. [Risiken & offene Punkte](#8-risiken--offene-punkte)
9. [Abhängigkeiten zu anderen Dokumenten (02–16)](#9-abhängigkeiten-zu-anderen-dokumenten-0216)

---

## 1. Ziel & Scope

### 1.1 Ziel

Dieses Dokument legt fest, wie die Suche und die KI-Funktionen der Community Edition in `funk.` gebaut werden, sodass ein Implementierungs-Agent ohne weitere Recherche Endpunkte, Abfragen, Indizes, Frontend-Bausteine und Tests erzeugen kann. Es liefert drei Dinge:

1. **Parität der CE-Suche:** globale Suche (Command-Palette „Power K“), Entity-Suche (Mentions, Entity-Picker), Work-Item-Picker-Suche und Public-API-Suche liefern dieselben Treffer und Antwortformen wie das Original. Die Trefferlogik ist die des Originals (`icontains` = Teilstring, groß-/kleinschreibungsunabhängig, plus exakte Sequenznummern), umgesetzt mit PostgreSQL `ILIKE` und `pg_trgm`-GIN-Indizes (ADR-024).
2. **Parität der CE-KI:** KI-Assistent („I'm feeling lucky“, GPT-Popover) über `Microsoft.Extensions.AI` mit konfigurierbarem OpenAI-kompatiblem Endpunkt (`LLM_BASE_URL`, lokal z. B. Ollama/vLLM/LocalAI, Airgapped-fähig, ADR-004/ADR-025) und Unsplash-Proxy für den Bild-Picker.
3. **Andockstellen für B6/G1 (🧱):** eine Such-Abstraktion, die später PQL/Advanced Search aufnimmt, eine in der CE bereits laufende Indexierungs-Pipeline über Integration-Events in `search_documents` (`tsvector`) und ein festgelegtes, reserviertes Embedding-Schema mit pgvector (Dimension konfigurierbar, HNSW). Fachdesign der Bezahl-Pakete erfolgt **nicht** (01 P7).

### 1.2 Im Scope

| Bereich | CE-IDs | Original-Endpunkte (A03/A05) |
|---|---|---|
| Globale Suche | CE-SRCH-001 | SR-01 `GET /api/workspaces/{slug}/search/` |
| Entity-Suche (Mentions, Entity-Picker) | CE-SRCH-002, Nutzer: CE-PAGE-034, CE-WI-044, CE-WI-001, CE-WI-005, CE-INT (Intake-Beschreibung) | SR-03 `GET /api/workspaces/{slug}/entity-search/` |
| Work-Item-Picker-Suche | CE-SRCH-003, Nutzer: CE-WI-008, CE-WI-031, CE-WI-048, Intake-Duplikatauswahl (`WEB/components/inbox/modals/select-duplicate.tsx`, CE-INT), „Existing work items“-Dialoge in Cycle-/Modul-Leerzuständen und Gruppenköpfen (CE-WI-008) | SR-02 `GET /api/workspaces/{slug}/projects/{project_id}/search-issues/` |
| Power-K-Suchseite (Frontend) | CE-SRCH-004 (Suchanteil); CE-SRCH-005…009 nur als Rahmen (Eigentümer 08 §3.10) | nutzt SR-01 |
| Public-API-Suche | CE-API-019 | `GET /api/v1/workspaces/{slug}/issues/search/`, `GET /api/v1/workspaces/{slug}/work-items/search/` |
| Querschnitt Textsuche in Listen (`?search=`, `query=`) | Helfer für CE-WS-005, CE-WS-009, CE-PRJ-021, CE-PAGE-002 (Backend-Anteil), CE-WI (IssueViewSet-Liste), CE-HOME-009, CE-API-014, CE-INST-027 | DRF-`SearchFilter` (`search_fields`), `description_stripped__icontains`, `name__icontains` |
| KI-Assistent | CE-AI-001 | EXT-03 `POST /api/workspaces/{slug}/ai-assistant/` (EXT-02 Projektvariante: D11-ADR-16) |
| Unsplash-Bildsuche | CE-AI-002, CE-UIX-009 (Unsplash-Tab) | EXT-01 `GET /api/unsplash/` |
| God-Mode-Einstellungen AI/Bilder | CE-INST-025, CE-INST-026 (Formulare; Speicherung über `Plane.Instance`) | `PATCH /api/instances/configurations/` (Eigentümer `Plane.Instance`) |
| Instanz-Flags | CE-INST-003 (Felder `has_llm_configured`, `has_unsplash_configured`) | `GET /api/instances/` (Eigentümer `Plane.Instance`) |
| Andockstellen | B6, G1 (🧱) sowie berührte 🧱-Pakete A1, A2, B1, D1, D2, E5, F1/F2, H1 | – |

### 1.3 Nicht im Scope

- Power-K-Befehle, Shortcuts, Kontext-Erkennung und `pl-command` (Eigentümer 08 §3.10, D08-ADR-17); hier nur die Suchseite der Palette.
- Filter-AST, Rich-Filter, Legacy-Filter `name` (Eigentümer 02 §3.11); dieses Dokument nutzt nur `LikePattern` dort.
- Seiten-Editor-KI-Menü (`rephrase-grammar`, Pi) und alle Pakete G1–G3 fachlich (nicht gewählt); nur Andockstellen §6.
- Speicherung der Instanz-Konfiguration, Verschlüsselung, Maskierung (Eigentümer 02 §3.16, 05 §3.17.5); dieses Dokument legt nur die AI-Schlüssel fest (Auftrag aus 05 §4.4 und 02 §4.10).
- Mitglieder-/Projekt-/Page-Listen selbst (Eigentümer jeweils Modul); dieses Dokument liefert nur den Such-Helfer.

### 1.4 Was wird in welchem Inkrement gebraucht

| Inkrement | Bausteine aus diesem Dokument | CE-IDs | Abnahme-Nachweis |
|---|---|---|---|
| **I0 Walking Skeleton** | Extensions `pg_trgm`, `unaccent`, `vector` im Postgres-Image und `ExtensionCheck` (14 §3.15); Spike-S0-Teil `PgvectorSmokeTests` (EF 10 + `Pgvector.EntityFrameworkCore`, HNSW, `CosineDistance`); Projekte `Plane.Platform.Search` und `Plane.Platform.Ai` als leere Gerüste mit Architekturtest; Instanz-Key `LLM_BASE_URL` im Seed-Katalog; Routen-Reservierungen §6.4 in `Reservations.cs` | – | `PgvectorSmokeTests`, `ExtensionCheckTests`, `RouteReservationTests` grün |
| **I1 Workspace/Projekte/Konto** | `LikePattern`, `DrfSearchFilter` (Port DRF-`SearchFilter`), Trigramm-Indizes `workspaces.name`, `projects.name`, `projects.identifier`, `users.{display_name,first_name,last_name}` | CE-WS-005, CE-WS-009, CE-PRJ-021 (je Suchparameter) | `DrfSearchFilterTests` (Golden aus DRF 3.17.2), Contract-Goldens der Mitgliederlisten mit `?search=` |
| **I2 Work Items & Layouts** | Modul `Plane.Search` (Gerüst), SR-03 mit Typen `user_mention`, `project`, `issue`; SR-02 mit Ausschlussparametern `parent`, `issue_relation`, `sub_issue`, `target_date`; `ParitySearchProvider` mit Quellen `UserMention`, `Project`, `WorkItem`; `SearchVisibilityFilter` für Work Items; Trigramm-Index `work_items.name`; Frontend `searchEntity`/`projectIssuesSearch` 1:1, Mentions im Lite-Editor, Parent-/Relation-/Sub-Issue-Picker, Bulk-Delete-Dialog | CE-SRCH-002 (Teil), CE-SRCH-003 (Teil), CE-WI-008, CE-WI-031, CE-WI-044, CE-WI-048 | `EntitySearchContractTests`, `WorkItemPickerSearchContractTests`, `SearchGuestScopeAppTests` (A-051, Teil Work Items) |
| **I3 Planung** | SR-02-Parameter `cycle`, `module`; SR-03-Typen `cycle`, `module`; Quellen `Cycle`, `Module`, `View`, `Intake`; Indizes `cycles.name`, `modules.name`, `issue_views.name` | CE-SRCH-002 (Teil), CE-SRCH-003 (Rest), Picker in Cycle/Module-Leerzuständen | Contract-Goldens SR-02/SR-03 je Parameter |
| **I4 Pages & Realtime** | SR-03-Typ `page`; Quelle `Page`; Index `pages.name`; Mentions im Rich/Document-Editor | CE-PAGE-034, CE-SRCH-002 (Rest) | `EntitySearchContractTests.Page_*` |
| **I5 Überblick** | SR-01 vollständig; Power-K-Suchseite; `SEARCH_RESULT_RENDERERS`; Indexierungs-Pipeline (`search_documents`, Consumer, Queue `indexing`, Jobs `indexing.*`, CLI `plane-cli search reindex`); `IIndexDocumentEnricher`; `NullEmbeddingGenerator` registriert; Index `stickies.description_stripped` (Home-Modul nutzt `LikePattern`); Lasttest LT-09 | CE-SRCH-001, CE-SRCH-004 (Suchanteil), CE-HOME-009 (Suchparameter) | `GlobalSearchContractTests`, `IndexingPipelineTests`, `web/search/search.spec.ts`, `web/search/power-k.spec.ts` (Suchteil), LT-09 p95 < 300 ms |
| **I6 Außenwirkung & Administration** | Public-API-Suche (Adapter in `Plane.PublicApi`), `Plane.Assistant` (EXT-03, EXT-01), `Plane.Platform.Ai` vollständig (`ILlmSettingsResolver`, `DynamicChatClient`, SSRF-Client `llm`), God-Mode-Formular AI mit Feld „Base URL“, Bild-Formular, `has_llm_configured`/`has_unsplash_configured` | CE-API-019, CE-API-014 (Suchparameter), CE-AI-001, CE-AI-002, CE-INST-025, CE-INST-026, CE-INST-027 (Suchparameter) | `PublicApiWorkItemSearchContractTests`, `AssistantEndpointTests` (WireMock „OpenAI-kompatibel“), `UnsplashEndpointTests`, `web/ai/ai-unsplash.spec.ts`, `admin/admin-settings.spec.ts` |
| **I7 Härtung** | Airgap-E2E mit lokalem LLM-Stub (WireMock im Profil `test`) und gesperrtem Egress; Index-Reconcile im Lasttest LT-08 | – | Airgap-Lauf grün, kein Egress außer Allowlist |
| **W5 (B6)** | dockt an §6.1 an | – | – |

> **Präzisierung zu 01 §5.4:** Das Modul `Plane.Search` entsteht bereits in **I2** (Work-Item-Picker und Mentions sind Teil der vertikalen Schnitte von I2), nicht erst in I5; die Spalte „ab“ in 01 §5.4 lautet damit „I2/I5“ (Änderungsauftrag §9.2).

---

## 2. Entscheidungen (D11-ADR-01 ff.)

| ADR | Belang | Entscheidung | Alternativen (verworfen) | Begründung | ab |
|---|---|---|---|---|---|
| **D11-ADR-01** | Projektschnitt | Abstraktionen und datenbankunabhängige Helfer in `Plane.Platform.Search` (`ISearchProvider`, `SearchQuery`, `SearchResult`, `IIndexingPipeline`, `IndexDocument`, `IIndexDocumentEnricher`, `LikePattern`, `SequenceIdExtractor`, `DrfSearchFilter`, `SearchText`); **Implementierungen mit Fachdatenbezug** (`ParitySearchProvider`, Such-Quellen, `IndexingPipeline`, `search_documents`-Schreiber) im Modul `Plane.Search`. `Plane.Platform.Ai` enthält Provider-Auflösung, `DynamicChatClient`, `NullEmbeddingGenerator`; `Plane.Assistant` die Endpunkte EXT-01/EXT-03. Der in 01 §5.1 unter `Plane.Platform.Search` genannte `PostgresSearchProvider` heißt `ParitySearchProvider` und liegt in `Plane.Search` (Präzisierung) | Provider in `Plane.Platform.Search` mit Roh-SQL auf Fachtabellen; eigener Such-Dienst | Regel R7 (01 §5.2): `platform/*` kennt keine Fachmodule und kein `Plane.Data`; die Suche braucht aber Joins über Work Items, Projekte, Mitgliedschaften und die Sichtbarkeitsfilter aus `Plane.Authorization` | I0/I2 |
| **D11-ADR-02** | Trefferlogik der CE-Endpunkte | **Original-Semantik**: `icontains` → `ILIKE '%' || escape(q) || '%'` (Escape `\`, `%`, `_` wie Django), Sequenznummern als exakte Ganzzahlvergleiche; Abfrage direkt auf den Fachtabellen mit **`pg_trgm`-GIN-Indizes** (`gin_trgm_ops`); die CE-Endpunkte lesen **nicht** aus `search_documents` | Volltextsuche (`tsvector @@ tsquery`) für die CE-Endpunkte; Lesen aus `search_documents` | `tsquery` findet Wortpräfixe, aber keine Teilstrings mitten im Wort („plan“ in „Replanning“) – Paritätsbruch; Sichtbarkeit hängt am aktuellen Mitgliedschaftsstand und wird ohnehin über Fachtabellen geprüft | I1/I2 |
| **D11-ADR-03** | Reihenfolge und Ranking | Wo das Original sortiert (`-created_at`), wird identisch sortiert (+ Tiebreaker `id DESC`, D02-ADR-13). Wo das Original **keine** Reihenfolge festlegt (SR-01 `issue`, SR-02, v1-Suche), gilt eine **deterministische Relevanzreihenfolge**: (1) exakter Sequenztreffer, (2) `similarity(name, q)` absteigend (`pg_trgm`), (3) `created_at DESC`, (4) `id DESC`; ohne Suchtext nur (3), (4). Präzisierung von ADR-024: das dort genannte `tsvector`-Ranking gilt für Index-basierte Provider (B6/G1), in der CE ersetzt Trigramm-Ähnlichkeit das Ranking, weil die Treffermenge Teilstring-basiert ist | `ts_rank` über `search_documents`; DB-Reihenfolge wie Original | Undefinierte Reihenfolge + `LIMIT 100` macht schon die Treffermenge nicht reproduzierbar (Contract-Tests, Nutzer sieht wechselnde Ergebnisse); `ts_rank` wäre für Teilstring-Treffer häufig 0 | I2 |
| **D11-ADR-04** | Such-Abstraktion | `ISearchProvider` bleibt **unverändert** (01 §5.5: `SearchAsync(SearchQuery)`); Auswahl je **Suchprofil** (`SearchProfile`: `Global`, `Entity`, `WorkItemPicker`, `PublicApiWorkItems`) über Keyed Services und Option `Plane:Search:Routing` (Default für alle Profile `parity`). Zwei Phasen: der Provider liefert nur `(entityType, id, score)`-Treffer; die Antwortform erzeugt der profilabhängige **Hydrator** im Modul `Plane.Search` (Original-Projektionen). B6 registriert einen weiteren Provider (`advanced`) und ein neues Profil, ohne CE-Code zu ändern | Ein Provider-Interface je Endpunkt; Provider liefert fertige DTOs | Provider-Tausch (Postgres-FTS, OpenSearch-ähnlich, Hybrid mit Embeddings) darf die Antwortverträge nicht berühren; Hydrator wendet die Sichtbarkeit ein zweites Mal an (Defense in Depth) | I2 |
| **D11-ADR-05** | Sichtbarkeit | Jede Kandidatenabfrage **und** jede Hydrierung wendet die `IVisibilityFilter<T>` aus `Plane.Authorization/Visibility/` an (05 §3.14 `SearchVisibilityFilter`: Work Items, Intake, Pages, Views); Mitgliedschaften immer `is_active = true` **und** `deleted_at IS NULL` (02 `DEV-PERM-001`); Korrekturen SEC-56 (Q-35, Q-36) und Gastregel auch in der v1-Suche | Sichtbarkeit nur im Provider | Ein getauschter Provider (B6/G1) könnte sonst unsichtbare Inhalte liefern (05 §6, G1-Zeile) | I2 |
| **D11-ADR-06** | Indexierungs-Pipeline | **In der CE aktiv** (16 X14): `SearchIndexingConsumer` (`IEventConsumer` für die Work-Item-, Kommentar-, Page-, Projekt-, Cycle-, Modul-, View- und Intake-Events aus 16 §3.2.4) plant `IndexEntityJob` in Queue `indexing` mit Dedupe-Schlüssel und Entprellung; der Job lädt den **aktuellen** Zustand, baut ein `IndexDocument`, ruft die `IIndexDocumentEnricher` und schreibt per Upsert in `search_documents` (`tsvector` als generierte Spalte, Konfiguration `simple` über `plane_unaccent`). Nachtjob `indexing.reconcile`, CLI `plane-cli search reindex`. Die CE-Endpunkte lesen den Index nicht (D11-ADR-02) | Index erst mit B6/G1 bauen; Trigger in PostgreSQL | Pakete B6/G1 starten ohne Backfill-Projekt und ohne CE-Umbau; Events sind ohnehin Pflicht (C3/H6); Trigger würden Modulgrenzen und Text-Extraktion (HTML) in SQL verlagern | I5 |
| **D11-ADR-07** | Embeddings | In der CE: `CREATE EXTENSION vector` (I0), `IEmbeddingGenerator<string, Embedding<float>>` = `NullEmbeddingGenerator`, **keine** Embedding-Tabelle (16 G1-Zeile). Das Schema für G1 ist hier **reserviert und festgelegt** (§6.2): Tabelle `search_embeddings` mit **dimensionsloser** Spalte `embedding vector`, Spalten `model_key`, `dimensions`; je aktivem Modell ein **partieller Ausdrucks-HNSW-Index** `((embedding::vector(n)) vector_cosine_ops) WHERE model_key = '<key>'` – Dimension damit zur Laufzeit konfigurierbar (`Plane:Ai:EmbeddingDimensions`, Default 1536) | `vector(1536)` fest in einer CE-Migration; separate Vektor-DB | Modellwechsel (andere Dimension) ohne Tabellenmigration; HNSW verlangt feste Dimension je Index, was der partielle Ausdrucksindex erfüllt (pgvector-Doku „Can I store vectors with different dimensions in the same column?“) | I0 (Extension), G1 |
| **D11-ADR-08** | Querschnitt `?search=` | Port des DRF-`SearchFilter` (DRF 3.17.2) als `DrfSearchFilter.Apply(query, search, fields…)`: Begriffe per `search_smart_split` (Leerzeichen/Komma, Anführungszeichen-Phrasen), **jeder** Begriff muss in **irgendeinem** Feld per `icontains` treffen, NUL-Zeichen entfernt, `DISTINCT` bei Mehrfach-Joins; Pflicht für alle Original-Views mit `search_fields` | Eigene Ad-hoc-Implementierungen je Modul | Gleiche Semantik an sechs Stellen, ein Golden-Test | I1 |
| **D11-ADR-09** | AI-Abstraktion und Transport | **`Microsoft.Extensions.AI`** (`IChatClient`, `IEmbeddingGenerator`) mit **`Microsoft.Extensions.AI.OpenAI`** über das offizielle OpenAI-.NET-SDK; **ein** Transport für alle Provider: Chat-Completions-Protokoll gegen eine konfigurierbare Basis-URL (OpenAI, OpenAI-kompatibel lokal, Anthropic- und Gemini-Kompatibilitätsendpunkte) | Semantic Kernel; `Microsoft.Extensions.AI.Ollama` (Preview, eingestellt); eigene HTTP-Clients je Provider | Provider-neutral (ADR-025), lokal betreibbar (ADR-004), ein Codepfad, MIT-lizenziert | I6 |
| **D11-ADR-10** | AI-Konfiguration | Instanz-Keys `LLM_API_KEY` (verschlüsselt), `LLM_PROVIDER` (`openai` Default, `openai-compatible`, `anthropic`, `gemini`), `LLM_MODEL`, **neu `LLM_BASE_URL`** (Kategorie `AI`, unverschlüsselt, Seed `""`, ENV `LLM_BASE_URL`); Modell-Whitelist des Originals entfällt; API-Key optional, wenn `LLM_BASE_URL` gesetzt ist; `GPT_ENGINE` entfällt (02 §4.10). `has_llm_configured` = Auflösung ergibt eine nutzbare Konfiguration | Provider-Konfiguration nur per ENV; Whitelist beibehalten | Q-28 (A03): Anthropic/Gemini funktionierten im Original nie, Whitelist ist veraltet; lokale Server brauchen keinen Key | I0 (Seed), I6 |
| **D11-ADR-11** | Ausgehende LLM-/Unsplash-Aufrufe | Das OpenAI-SDK läuft über den **SSRF-geschützten Named Client `llm`** (05 §3.17.2: 120 s, 0 Redirects, 8 MiB, Allowlist `Plane:Ai:AllowedInternalHosts`) via `HttpClientPipelineTransport`; SDK-eigene Wiederholungen aus (`ClientRetryPolicy(maxRetries: 0)`), Netzwerk-Timeout 120 s. Unsplash über Named Client `unsplash` (10 s, 5 Redirects, 2 MiB) | SDK-Standard-HttpClient; Standard-Resilience | Kein Aufruf an Nutzer-/Betreiber-URLs ohne SSRF-Schutz (D05-ADR-24, ABG-040); keine automatischen Wiederholungen | I6 |
| **D11-ADR-12** | Laufzeitwechsel der Konfiguration | `DynamicChatClient : IChatClient` liest bei jedem Aufruf die aufgelösten Einstellungen (`ILlmSettingsSource`, gecacht über den Instanz-Konfigurations-Cache `plane:instance:config`) und verwendet einen pro Einstellungs-Fingerabdruck gecachten inneren Client; Änderungen im God Mode wirken ohne Neustart | Singleton-Client beim Start | God-Mode-Änderung soll sofort greifen (Original liest je Request) | I6 |
| **D11-ADR-13** | KI-Assistent-Vertrag | Prompt = `task + "\n" + prompt` als **eine** `user`-Nachricht (1:1), keine weiteren Chat-Optionen; Antworten `{"response", "response_html"}` 1:1; Korrekturen: fehlender `prompt` → `""` (Original 500), leere/`null`-Antwort → `""` (Original 500), `response_html` = HTML-kodierter Text mit `\n` → `<br/>` (Original ohne Kodierung) | Systemprompt ergänzen; Markdown-Rendering | Parität des Verhaltens; Kodierung verhindert, dass Modellausgaben als HTML in den Editor gelangen (Sicherheitskorrektur ohne sichtbare Änderung bei Klartext-Antworten) | I6 |
| **D11-ADR-14** | Unsplash-Proxy | Durchreichen von Status und JSON (1:1); Korrekturen Q-27: `page` ohne `$`, Query URL-kodiert, Access-Key im Header `Authorization: Client-ID <key>` statt in der URL, Timeout 10 s, 2 MiB | 1:1 inklusive Fehler | Funktionale Fehler korrigieren (Auftraggeber, 17 Z-12); Key nicht in URLs/Logs | I6 |
| **D11-ADR-15** | God-Mode-Formular AI | Formular `/god-mode/ai` 1:1 plus **ein** zusätzliches Feld „Base URL“ (`LLM_BASE_URL`) als drittes Feld im bestehenden 3-Spalten-Raster; der Hinweis-Kasten „If you have a preferred AI models vendor, please get in touch with us.“ entfällt (ADR-001, Kontakt-CTA). `LLM_PROVIDER` bleibt wie im Original nur per ENV/API setzbar | Provider-Auswahlfeld zusätzlich; Formular unverändert | Minimale sichtbare Abweichung, die ADR-004 erzwingt (`DEV-UI-D11-01`, `DEV-UI-D11-02`) | I6 |
| **D11-ADR-16** | Nicht registrierte Original-Routen | `POST {P}/ai-assistant/` (EXT-02) hat keinen Client-Aufrufer → nach 02 §3.3.1 Regel 6 **nicht registriert** (405, `DEV-AI-008`); Permission `project.ai_assistant.use` bleibt im Katalog (generiert, 05), ohne Endpunkt. `POST {W}/rephrase-grammar/` existiert in der CE nicht (404 wie Original); das Editor-KI-Menü bleibt über `EDITOR_FLAGS` (`ai` deaktiviert) unsichtbar | Beide Routen bauen | Parität und Regel 6; Editor-KI gehört zu G3 (nicht gewählt) | I6 |
| **D11-ADR-17** | Frontend-Port Suche | Power-K-Suchseite, Ergebnisgruppen und Services **1:1** (Debounce 500 ms, Gruppen-Map → Registry `SEARCH_RESULT_RENDERERS`, Client-Filter der Palette `includes` auf dem Item-`value`); Korrektur: veraltete Antworten werden verworfen (laufende Anfrage wird bei neuem Suchbegriff abgebrochen), Original-Darstellungsfehler (Page-Identifier) bleibt optisch 1:1 | eigene Ergebnisdarstellung | ADR-005; Race-Condition ist funktionaler Fehler ohne optische Wirkung | I5 |
| **D11-ADR-18** | Unbegrenzte Ergebnislisten | SR-01 liefert für `workspace`, `project`, `cycle`, `module`, `issue_view`, `page` im Original **alle** Treffer; Ziel: Obergrenze `Plane:Search:MaxUnboundedResults` = 1000 je Entitätstyp (0 = unbegrenzt) | 1:1 unbegrenzt | Schutz vor Antworten mit Zehntausenden Einträgen bei Ein-Zeichen-Suchen; UI zeigt ohnehin Listen dieser Größe nicht sinnvoll (`DEV-SRCH-002`) | I5 |

