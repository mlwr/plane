# 21 – Bezahl-Features laut öffentlicher API-Referenz (Developer-Docs) – IST-Analyse (Cluster P02)

> **Status:** IST-Analyse, keine Implementierung. Bindend sind zusätzlich die Grundsatzentscheidungen in `migration/architecture/00-grundsatzentscheidungen.md` (ADR-000 … ADR-006): eine Edition ohne Plan-Stufen (ADR-001), Greenfield-Schema bei fachlich gleicher Semantik (ADR-003), Self-hosted/Airgapped (ADR-004), UI 1:1 (ADR-005).
>
> **Abkürzungen für Quellpfade**
>
> | Kürzel | Bedeutung |
> |---|---|
> | `AR/` | `/home/user/makeplane/developer-docs/docs/api-reference/` (öffentliche REST-Referenz der Commercial Edition, offline) |
> | `DD/` | `/home/user/makeplane/developer-docs/docs/` (restliche Developer-Docs, offline) |
> | `HC/` | `/home/user/makeplane/helm-charts/charts/` (Helm-Charts, offline) |
> | ohne Präfix | Pfad relativ zum Repo-Root `/home/user/plane` (Community Edition v1.4.2) |
> | `WEB:` | per WebSearch gefundene öffentliche Quelle (URL); docs.plane.so/plane.so selbst waren per Netzwerk nicht abrufbar (`getaddrinfo ENOTFOUND plane.so`), es liegen nur Such-Snippets vor |
> | `V2/` | `/tmp/claude-0/-home-user-plane/fe89ae79-d9fa-54e4-b848-1dc9726b58d0/scratchpad/devdocs-v2/repo/docs/api-reference/v2/` – Partial-Clone des Branches `docs/api-reference-v2` von `https://github.com/makeplane/developer-docs.git`, Commit `b89c72c80aba383fe5b8bfeb36301649bc9ca79d` (11.08.2026, „docs(api-v2): add the artifacts surface (4 endpoints) missing from the committed spec“); im Verifikationslauf ausgewertet (Kap. 9) |
> | `PU/` | `/tmp/claude-0/-home-user-plane/fe89ae79-d9fa-54e4-b848-1dc9726b58d0/scratchpad/devdocs-pu/repo/docs/api-reference/` – Clone des Branches `docs-page-update-api` desselben Repos, Commit `1c6e5542d0f2a574c96a657071c6c4414826141a` (20.08.2026); im Verifikationslauf ausgewertet (Kap. 10) |
>
> **Stand der Offline-Doku:** `AR/`/`DD/` entsprechen Branch `master`, Commit `1fe7033905ab613441a37f07032c6aea730921f4` (01.09.2026). Dieser Stand enthält **nur API v1**. API v2 und die Page-API-Erweiterungen liegen auf den nicht gemergten Branches `V2/` und `PU/` (Verifikations-Protokoll V.3).
>
> **Status-Legende CE-Abgleich**
>
> | Wert | Bedeutung |
> |---|---|
> | **CE** | Endpunkt existiert in der CE-Public-API (`apps/api/plane/api/urls/*`) mit gleicher Methode/gleichem Pfad |
> | **CE (abweichend)** | Endpunkt existiert, aber Request/Response weichen von der Commercial-Doku ab |
> | **CE-teilweise** | Code (View/Serializer/Model) existiert im CE, ist aber nicht geroutet oder unvollständig |
> | **EE-only** | Kein Endpunkt in der CE-Public-API; Funktion nur in der Commercial Edition |
> | **entfällt** | in der Doku als deprecated markiert bzw. durch ADR-001 obsolet |

---

## 1. Überblick & Quellenlage

### 1.1 Zweck und Umfang

Dieses Dokument inventarisiert **vollständig** die öffentliche REST-API der Commercial Edition (Plane Cloud / Commercial Self-hosted), wie sie in den offline vorliegenden Developer-Docs beschrieben ist (`AR/`, 270 Markdown-Dateien, alle gelesen), gleicht **jeden** Endpunkt gegen die CE-Public-API (`apps/api/plane/api/urls/`, `apps/api/plane/api/views/`, `apps/api/plane/api/serializers/`) ab und extrahiert für jede Ressource, die nur in den Bezahl-Editionen existiert, das Datenmodell (Felder/Typen/Enums), Endpunkte, Berechtigungen (OAuth-Scopes, Rollen), Pagination und – soweit belegbar – UI/Verhalten. Da der Code der Commercial Edition closed-source ist, ist die API-Referenz die **Primärquelle für das Datenmodell der Bezahl-Features**. Im Verifikationslauf wurden zusätzlich die nicht gemergten Doku-Branches für **API v2** (387 Endpunkte, Kap. 9) und die **Page-API-Erweiterung v1** (36 Endpunkte, Kap. 10) ausgewertet; Tier- und CE-Status-Angaben wurden gegen Repo, Schwester-Dokumente und WebSearch geprüft (Verifikations-Protokoll). Ergänzend wurden herangezogen:

| # | Quelle | Pfad / URL | Umfang | Verwendung |
|---|---|---|---|---|
| Q1 | REST-API-Referenz v1 | `AR/` (32 Ressourcen-Ordner, davon `issue-types/` mit 4 Unterordnern `types`, `properties`, `options`, `values`, + `introduction.md`) | 270 Dateien, vollständig gelesen | Endpunkte, Felder, Scopes |
| Q2 | OAuth-Scope-Liste | `DD/dev-tools/build-plane-app/oauth-scopes.md` | vollständig | Scope-Inventar (Kap. 6) |
| Q3 | MCP-Server-Tool-Referenz (28 Tools, 183 Actions) | `DD/dev-tools/mcp-server-tools.md` | vollständig | Präzisierung von Parametern, Enums, Verhalten, die in Q1 fehlen (z. B. Body der `remove`-Endpunkte, Customer-Stage-Werte, Formula/Release-Property-Typen, Releases) |
| Q4 | Editions-Erklärung | `DD/self-hosting/editions-and-versions.md` | vollständig | CE ↔ Commercial-Abgrenzung |
| Q5 | Advanced Search / OpenSearch | `DD/self-hosting/govern/advanced-search.md` | gelesen | Plan-Badge „Pro“, Funktionsumfang |
| Q6 | Plan-Badges in Self-Hosting-Docs | `DD/self-hosting/govern/*.md` (`<Badge …>`) | per grep | Plan-Zuordnung (Intake-Email = Business, LDAP = Enterprise Grid, Integrationen = Pro) |
| Q7 | CE-Plan-Vergleichstabelle (im CE-Repo enthalten!) | `apps/web/components/workspace/billing/comparison/plans.tsx` | gelesen | Plan-Abstufungen Free/One/Pro/Business/Enterprise |
| Q8 | CE-Plan-Feature-Listen | `packages/constants/src/subscription.ts` | gelesen | Plan-Abstufungen |
| Q9 | CE-i18n mit EE-Texten | `packages/i18n/src/locales/en/*.json`; ausgewertet: `workspace-settings.json`, `project-settings.json`, `work-item-type.json`, `wiki.json`, `template.json`, `workflow.json`, `update.json`, `empty-state.json`, `common.json`, `page.json` (Verifikationslauf zusätzlich `work-item.json`) | gezielt gelesen | UI-Texte der Bezahl-Features (für 1:1-UI) |
| Q10 | CE-Leer-Zustands-Illustrationen für EE-Features | `packages/blocks/src/empty-state/assets/{horizontal-stack,vertical-stack}/*.tsx` | Dateiliste | UI-Assets (customer, initiative, teamspace, milestone, worklog, group-syncing, custom-properties, property, epic, template, workflow, changelog, update) |
| Q11 | Helm-Chart Commercial | `HC/plane-enterprise/templates/workloads/*.yaml`, `HC/plane-enterprise/Chart.yaml` (`appVersion: "3.3.3"`) | Dateiliste | Dienste der Commercial Edition (`external-api`, `opensearch`, `pi-api`, `silo`, `automation-consumer`, `outbox-poller` …) |
| Q12 | WebSearch-Snippets | siehe jeweilige Abschnitte | punktuell | Plan-Zuordnung, UI-Verhalten |
| Q13 | REST-API-Referenz **v2** (Branch `docs/api-reference-v2`) | `V2/` (67 Ressourcen-Ordner + 9 Querschnittsseiten `introduction.md`, `authentication.md`, `errors.md`, `pagination.md`, `sparse-fields.md`, `expanding-relations.md`, `filtering-and-ordering.md`, `migrating-from-v1.md`, `work-item-type-modes.md`) | 463 Markdown-Dateien; Endpunkte per Skript aus den `api-endpoint-badge`-Blöcken extrahiert (387 distinkte Methode+Pfad), Querschnittsseiten und Overviews der v2-only-Ressourcen gelesen | Kap. 9 (Verifikationslauf) |
| Q14 | Page-API-Erweiterung v1 (Branch `docs-page-update-api`) | `PU/` (`page/`, `collection/`, `work-item-pages/`) | 46 Markdown-Dateien, 36 Endpunkte per Skript extrahiert | Kap. 10 (Verifikationslauf); Detailspezifikation in `migration/features/26-paid-wissen-pages-wiki.md` (G1–G15) |
| Q15 | Schwester-Dokumente | `migration/features/20-*.md` … `28-*.md` | für Tier- und CE-Status-Abgleich gelesen | Verifikations-Protokoll |

> **Hinweis „Hinweis aus Q7/Q9“:** Das CE-Repo enthält bereits Upsell-Tabellen und i18n-Texte der Bezahl-Features. Diese sind keine Implementierung, liefern aber die **exakten UI-Texte** für die 1:1-Nachbildung und die vom Hersteller selbst veröffentlichte Plan-Matrix.

### 1.2 Allgemeine API-Konventionen (gelten für alle Ressourcen)

| Thema | Commercial-Doku | CE-Abgleich | Migrationshinweis (.NET) |
|---|---|---|---|
| Base-URL | `https://api.plane.so/` + `/api/v1/…`; Self-hosted: eigene Domain (`AR/introduction.md`) | CE mountet `api/v1/` → `plane.api.urls` (`apps/api/plane/urls.py:22`) | Minimal-API/Controller-Gruppe `/api/v1` beibehalten (Contract-Kompatibilität, ADR-003-Konsequenz) |
| Auth API-Key | Header `X-API-Key: plane_api_<token>`; Token unter *Profile Settings → Personal Access Tokens*, mit Titel, Beschreibung, optionalem Ablauf (`AR/introduction.md`) | CE identisch (`APIToken`-Modell `apps/api/plane/db/models/api.py:23`) | eigener `AuthenticationHandler` „ApiKey“ |
| Auth OAuth | `Authorization: Bearer <token>`; Scope-basiert (`AR/introduction.md`, Q2) | **CE: kein OAuth-App-/Scope-System in der Public-API** (keine Scope-Prüfung in `apps/api/plane/api/views/base.py`) | OAuth2-Authorization-Server (z. B. OpenIddict) mit Scope-Policies laut Kap. 6 |
| HTTP-Verben | GET, POST, PATCH, DELETE (`AR/introduction.md`) | gleich; CE kennt zusätzlich `PUT` auf `IssueDetailAPIEndpoint.put` (`apps/api/plane/api/views/issue.py:623`) | – |
| Statuscodes | 200, 201, 204; Fehler 400, 401, 404, 429, 500, 502, 503, 504 (`AR/introduction.md`) | gleich | ProblemDetails nur, wenn Body-Format kompatibel bleibt (Original: `{"error": "..."}` / `{"detail": "..."}`) |
| Pagination | Cursor `value:offset:is_prev` (value = Seitengröße, offset = Seitennummer ab 0, is_prev = 1/0); Query `per_page` (Doku Einleitung: Default 100, Max 100; Endpunkt-Seiten: „default: 20, max: 100“), `cursor`; Response-Felder `next_cursor`, `prev_cursor`, `next_page_results`, `prev_page_results`, `count`, `total_pages`, `total_results`, `extra_stats`, `results` – in den Endpunkt-Beispielen zusätzlich `grouped_by`, `sub_grouped_by`, `total_count` (`AR/introduction.md`, z. B. `AR/customer/list-customers.md`) | CE-Paginator: Default/Max `per_page` = **1000** (`apps/api/plane/utils/paginator.py:643-653`), Cursor-Format identisch (`…:679`) | Default/Max als Konfiguration; Response-Envelope exakt übernehmen |
| Rate-Limit | 60 Requests/Minute pro API-Key; Header `X-RateLimit-Remaining`, `X-RateLimit-Reset` (UTC-Epoch-Sekunden) (`AR/introduction.md`) | CE: `ApiKeyRateThrottle`, Rate aus `settings.API_KEY_RATE_LIMIT` (`apps/api/plane/api/rate_limit.py:12-20`) | ASP.NET Core Rate-Limiting (Fixed Window, Partition = API-Key), Header setzen |
| `fields` / `expand` | kommagetrennt; ungültige Felder → Fehlerantwort (`AR/introduction.md`) | CE `BaseAPIView.fields/expand` (`apps/api/plane/api/views/base.py:152-160`) | Sparse-Fieldsets serverseitig |

### 1.3 Qualitätsvorbehalte der Commercial-Doku (vollständige Liste der festgestellten Fehler/Inkonsistenzen)

Die Referenz ist aus OpenAPI generiert und enthält Platzhalter-Beispiele. Implementierungs-Agenten dürfen **Response-Beispiele nicht blind als Schema übernehmen**. Festgestellt:

| # | Fundstelle | Problem |
|---|---|---|
| D1 | `AR/customer/add-customer-request.md`, `get-customer-request-detail.md`, `list-customer-requests.md`, `update-customer-request-detail.md` | Response-Beispiel zeigt **Customer-Felder** (`email`, `domain`, `revenue`, …) statt Request-Felder; `list` zeigt kein Paginierungs-Envelope |
| D2 | `AR/customer/get-customer-property-value.md`, `list-customer-property-values.md`, `list-customer-work-items.md` | Response nur `{"detail": "… retrieved successfully"}` – echtes Schema undokumentiert |
| D3 | `AR/customer/delete-customer-property.md`, `get-customer-property-detail.md`, `update-customer-property-detail.md` | Pfad nutzt `{property_id}`, Parameterliste nennt `resource_id` |
| D4 | `AR/inbox-issue/*.md` | Response-Beispiele zeigen ein **Projekt**-Objekt; Pfade ohne abschließenden Slash |
| D5 | `AR/initiative/list-initiatives.md`, `list-initiative-labels.md`, `AR/teamspace/list-teamspaces.md`, `AR/sticky/list-stickies.md`, `AR/members/get-project-members.md`, `AR/issue/advanced-search-work-items.md`, `AR/work-item-relations/create-work-item-relation.md` | Response in zusätzliches Array gewickelt (`[ { …envelope… } ]` bzw. `[[…]]`) – vermutlich Generator-Artefakt |
| D6 | `AR/initiative/remove-*.md`, `AR/teamspace/remove-*.md` | DELETE ohne dokumentierten Body; MCP-Doku zeigt `project_ids` als Pflicht (`DD/dev-tools/mcp-server-tools.md:303`) |
| D7 | `AR/initiative/list-initiatives.md` vs. `DD/dev-tools/mcp-server-tools.md:296` | REST-Doku: paginiert (`cursor`, `per_page`); MCP: „returns every initiative; this endpoint does not paginate“ |
| D8 | `AR/issue-types/values/overview.md` | „Values Object“-Beispiel ist ein **Option**-Objekt (mit `project_ids`) |
| D9 | `AR/issue-types/properties/add-property.md` | curl-Beispiel sendet `name` statt Pflichtfeld `display_name` |
| D10 | `AR/epics/list-epic-work-items.md` | Scope `projects.work-items:read` (Bindestrich) statt `projects.work_items:read` |
| D11 | `AR/work-item-pages/delete-work-item-page.md` vs. `DD/dev-tools/mcp-server-tools.md:459` | REST-Pfad `…/pages/{page_id}/`; MCP: „workitem_page_id is the link id … not the page id“ |
| D12 | `AR/issue-attachments/get-attachment-detail.md` | Beschreibung „Returns a redirect to the presigned download URL“, Beispiel zeigt 401 |
| D13 | `AR/issue-attachments/get-upload-credentials.md` | Response-Beispiel `{"detail": …}` statt Upload-Daten (vgl. `AR/assets/create-workspace-asset-upload.md`) |
| D14 | `AR/cycle/transfer-cycle-work-items.md` vs. `DD/dev-tools/mcp-server-tools.md:249` | REST: „transfers only unfinished work items“; MCP: „moves everything to new_cycle_id“ |
| D15 | `AR/work-item-relations/list-work-item-relations.md` | Response: Listen von UUID-Strings; CE liefert Objekte `{project_id, issue_id}` (`apps/api/plane/api/serializers/issue.py:514-561`) |
| D16 | `AR/issue/overview.md` | `estimate_point` als „integer 0–7“ beschrieben; in Wahrheit UUID eines `EstimatePoint` (`apps/api/plane/db/models/issue.py`, Feld `estimate_point` FK) |
| D17 | `AR/milestones/*.md`, `AR/work-item-pages/*.md`, `AR/issue/advanced-search-work-items.md` | kein Scope angegeben („API key authentication or an OAuth token with equivalent access“); Q2 kennt `projects.milestones:*` |
| D18 | Q2 (`oauth-scopes.md`) | enthält **nicht** `projects.estimates:*` und `workspaces.group_sync:*`, obwohl Q1 sie verwendet |
| D19 | `AR/module/add-module.md`, `update-module-detail.md` | curl sendet `end_date`, Parameter heißt `target_date` |
| D20 | `AR/module/list-modules.md` | Status `in_progress` im Beispiel, Enum ist `in-progress` |
| D21 | `AR/inbox-issue/overview.md` | sagt „PATCH … `inbox_view:true`“; aktuelles Feld heißt `intake_view` (`AR/intake-issue/overview.md`) |
| D22 | `V2/introduction.md` („88 operations across these resources“, 13 Ressourcen) vs. Ordner `V2/` | Die Einleitung nennt 88 Operationen; der Branch dokumentiert 387 distinkte Endpunkte in 67 Ordnern (Kap. 9). Die Einleitung ist veraltet. |
| D23 | `V2/migrating-from-v1.md` Abschnitt „11. Not yet in v2“ | Listet Projekte, Pages, Intake, Teamspaces, Initiativen, Epics, Estimates, Customers, Stickies, Attachments, Links, Worklogs, Relations, Activity, Milestones, Invitations als „v1-only“. Zu fast allen gibt es im selben Branch v2-Endpunkte (Kap. 9.3). Ausnahme: Epics haben keinen v2-Ordner. |
| D24 | `V2/members/overview.md` | Text: „Members are read-only in v2. There are no v2 endpoints to invite, update, or remove a member“. Dieselbe Seite listet `POST …/members/remove/` sowie `POST/PATCH/DELETE …/projects/{project_id}/members/…`. |
| D25 | `V2/authentication.md` (Info-Box „The catalog is larger than this table“) | Sagt, Scopes für Pages, Customers, Initiatives, Releases, Teamspaces, Templates, Webhooks, Assets seien „not live in v2 yet“. Der Branch dokumentiert für alle diese Bereiche Endpunkte mit genau diesen Scopes (Kap. 9.4). |
| D26 | `V2/errors.md` | `402 payment_required` steht als Standardzeile in den Fehlertabellen fast aller v2-Endpunkte, auch bei States und Stickies (Befund Dok. 26 Kap. 3.45/Anhang). Das ist **kein** Beleg, dass die Ressource kostenpflichtig ist. |
| D27 | `AR/introduction.md` (`X-API-Key`) vs. `V2/authentication.md` (`X-Api-Key`) | Unterschiedliche Schreibweise desselben Headers. Header-Namen sind case-insensitiv (`V2/authentication.md`, Warnbox „Header casing“). |
| D28 | `V2/members/overview.md` („Members are one of only two v2 resources that accept `?expand=` — the other is work items“) und `V2/migrating-from-v1.md` §5 vs. `V2/expanding-relations.md` | `expanding-relations.md` nennt eine Allowlist mit 14 Zeilen (vollständig in Kap. 9.2, Zeile `?expand=`). Maßgeblich ist laut Einleitung das OpenAPI-Schema `GET /api/v2/schema/`. |
| D29 | `V2/project-automations/overview.md` | Abschnitt „The project automation object“ listet die Felder eines **Activity**-Eintrags (`automation_run_id`, `node_execution_id`, `verb`, `old_value`, `new_value`, `epoch` …); die Request-Bodies (`create-project-automation.md`: `name`*, `scope`*, `description`, `project_ids`) passen nicht dazu. |

### 1.4 Ergebnis in Zahlen

| Kennzahl | Wert | Quelle |
|---|---|---|
| Dokumentierte Ressourcen-Ordner | 32 (+ `introduction.md`; `issue-types/` mit 4 Unterordnern) – korrigiert im Verifikationslauf, vorher „33“ | `AR/` (`ls -d */`) |
| Dokumentierte, distinkte Endpunkte (Methode + Pfad, ohne S3-Upload) | 231 | Kap. 2 |
| davon **CE** / **CE (abweichend)** | 94 | Kap. 2 (Assets 6, Cycles 12, Intake 5, Work Items 7, Activity 2, Attachments 5, Comments 5, Links 5, Relations 2, Labels 5, Members 6, Modules 11, Projects 7, States 5, Stickies 5, User 1, Invitations 5) |
| davon **CE-teilweise** (Code ohne Route) | 9 (8 × Estimates, 1 × Relation-Remove) | `apps/api/plane/api/urls/__init__.py`, `apps/api/plane/api/serializers/issue.py:601` |
| davon **EE-only** | 123 | Kap. 2 (Customers 21, Epics 7, IdP Group Sync 12, Initiatives 19, Advanced Search 1, Types/Properties/Options/Values 20, Member-Remove 1, Milestones 6, Pages 6, Work-Item-Pages 4, Project-Template 1, Project-Features 2, Project-Labels 5, Teamspaces 11, Worklogs 5, Workspace-Features 2) |
| davon **entfällt** (deprecated `inbox-issues`) | 5 | `AR/inbox-issue/overview.md` |
| API **v2**: distinkte Endpunkte (Methode + Pfad) in 67 Ressourcen-Ordnern | 387; **alle EE-only**, die CE kennt kein `/api/v2/` (`apps/api/plane/urls.py:19-24` mountet nur `api/`, `api/public/`, `api/instances/`, `api/v1/`, `auth/`, `""`) | Kap. 9; `V2/` |
| davon v2-Ressourcen **ohne** v1-Pendant in `AR/` | 29 Ordner, zusätzlich `collections` (nur im Branch `PU/` als v1 vorhanden) (Artifacts, Audit-Logs, Permission-Schemes, Permissions, Project-/Workspace-Automations, Project-/Workspace-Views, Project-/Workspace-Work-Item-Templates, Release-Comments/-Labels/-Links/-Tags, Releases, Roles, Webhooks, Webhook-Logs, Work-Item-Dependencies, Work-Item-Property-Contexts, Work-Item-Relation-Definitions, Work-Item-Type-Properties, Workflows, Workflow-States, Workflow-Transitions, Workspace-Work-Item-Types/-Properties/-Property-Options/-Type-Properties) | Kap. 9.3 |
| Page-API-Branch `docs-page-update-api`: Endpunkte | 36, davon 26 nicht in `AR/` (Update/Archive/Restore/Delete von Projekt- und Wiki-Seiten, Page-Attachments, Collections) | Kap. 10; `PU/` |

---

## 2. Vollständiges Endpunkt-Inventar mit CE-Abgleich

Alle Pfade relativ zu `/api/v1/`. `{ws}` = `{workspace_slug}` bzw. `{slug}`, `{pid}` = `{project_id}`, `{wid}` = `{work_item_id}`. „Scope“ = OAuth-Scope laut Doku. „CE-Beleg“ = Datei in `apps/api/plane/api/urls/`.

### 2.1 Assets (`AR/assets/`)

| # | Methode | Pfad | Zweck | Scope | Status | CE-Beleg |
|---|---|---|---|---|---|---|
| A1 | POST | `assets/user-assets/` | Presigned-Upload für Avatar/Cover; Body `name`* (string), `type` (`image/jpeg`,`image/png`,`image/webp`,`image/jpg`,`image/gif`), `size`* (int Bytes), `entity_type`* (`USER_AVATAR`,`USER_COVER`) → 200 `{asset_id, asset_url, upload_data{url, fields{Content-Type,key,x-amz-algorithm,x-amz-credential,x-amz-date,policy,x-amz-signature}}}` | `assets:write` | CE | `asset.py` (`UserAssetEndpoint` post) |
| A2 | PATCH | `assets/user-assets/{asset_id}/` | als hochgeladen markieren; Body `attributes` (object) → 204 | `assets:write` | CE | `asset.py` |
| A3 | DELETE | `assets/user-assets/{asset_id}/` | Soft-Delete, Referenz am Profil entfernen → 204 | `assets:write` | CE | `asset.py` |
| A4 | POST | `workspaces/{ws}/assets/` | generischer Upload; Body `name`*, `type`, `size`*, `project_id`, `external_id`, `external_source` → 200 wie A1 | `assets:write` | CE | `asset.py` (`GenericAssetEndpoint`) |
| A5 | GET | `workspaces/{ws}/assets/{asset_id}/` | Download-URL → `{id,name,type,asset_url,attributes{entity_type}}` | `assets:read` | CE | `asset.py` |
| A6 | PATCH | `workspaces/{ws}/assets/{asset_id}/` | Body `is_uploaded` (bool) → 204 | `assets:write` | CE | `asset.py` |
| – | POST/PATCH/DELETE | `assets/user-assets/server/`, `assets/user-assets/{id}/server/` | nur CE-Code, nicht dokumentiert | – | CE (undokumentiert) | `asset.py` (`UserServerAssetEndpoint`) |

### 2.2 Customers (`AR/customer/`) – vollständig EE-only

| # | Methode | Pfad | Zweck | Scope | Status |
|---|---|---|---|---|---|
| C1 | GET | `workspaces/{ws}/customers/` | Liste, „optional search filtering“ (MCP: `query`, `cursor`, `per_page`), paginiert | `customers:read` | EE-only |
| C2 | POST | `workspaces/{ws}/customers/` | anlegen → 201 | `customers:write` | EE-only |
| C3 | GET | `workspaces/{ws}/customers/{customer_id}/` | Detail | `customers:read` | EE-only |
| C4 | PATCH | `workspaces/{ws}/customers/{customer_id}/` | ändern → 200 | `customers:write` | EE-only |
| C5 | DELETE | `workspaces/{ws}/customers/{customer_id}/` | „Permanently delete“ → 204 | `customers:write` | EE-only |
| C6 | GET | `workspaces/{ws}/customers/{customer_id}/requests/` | Requests eines Kunden, mit Suche (MCP `query`) | `customers.requests:read` | EE-only |
| C7 | POST | `workspaces/{ws}/customers/{customer_id}/requests/` | Request anlegen → 201 | `customers.requests:write` | EE-only |
| C8 | GET | `workspaces/{ws}/customers/{customer_id}/requests/{request_id}/` | Detail | `customers.requests:read` | EE-only |
| C9 | PATCH | `workspaces/{ws}/customers/{customer_id}/requests/{request_id}/` | ändern → 200 | `customers.requests:write` | EE-only |
| C10 | DELETE | `workspaces/{ws}/customers/{customer_id}/requests/{request_id}/` | löschen **und verknüpfte Work Items entkoppeln** → 204 | `customers.requests:write` | EE-only |
| C11 | GET | `workspaces/{ws}/customers/{customer_id}/issues/` | verknüpfte Work Items, „filtering by request“ (MCP `customer_request_id`, `search`) | `customers.work_items:read` | EE-only |
| C12 | POST | `workspaces/{ws}/customers/{customer_id}/issues/` | Work Items verknüpfen, Body `issue_ids`* (array UUID), „optionally within a specific customer request“ → 201 `{"detail":"Issues linked successfully"}` | `customers.work_items:write` | EE-only |
| C13 | DELETE | `workspaces/{ws}/customers/{customer_id}/issues/{wid}/` | Verknüpfung lösen (Kunde bzw. Kunden-Request) → 204 | `customers.work_items:write` | EE-only |
| C14 | GET | `workspaces/{ws}/customer-properties/` | Custom-Properties für Kunden, paginiert | `customers.properties:read` | EE-only |
| C15 | POST | `workspaces/{ws}/customer-properties/` | anlegen → 201 | `customers.properties:write` | EE-only |
| C16 | GET | `workspaces/{ws}/customer-properties/{property_id}/` | Detail | `customers.properties:read` | EE-only |
| C17 | PATCH | `workspaces/{ws}/customer-properties/{property_id}/` | ändern → 200 | `customers.properties:write` | EE-only |
| C18 | DELETE | `workspaces/{ws}/customer-properties/{property_id}/` | löschen → 204 | `customers.properties:write` | EE-only |
| C19 | GET | `workspaces/{ws}/customers/{customer_id}/property-values/` | alle Property-Werte eines Kunden | `customers.property_values:read` | EE-only |
| C20 | GET | `workspaces/{ws}/customers/{customer_id}/property-values/{property_id}/` | Werte einer Property | `customers.property_values:read` | EE-only |
| C21 | PATCH | `workspaces/{ws}/customers/{customer_id}/property-values/{property_id}/` | Body `values`* (array) → 204 | `customers.property_values:write` | EE-only |

### 2.3 Cycles (`AR/cycle/`)

| # | Methode | Pfad | Zweck | Scope | Status | CE-Beleg |
|---|---|---|---|---|---|---|
| CY1 | GET | `…/projects/{pid}/cycles/` | Liste; Query `cursor`, `cycle_view` (Status-Filter: current, upcoming, completed, draft; MCP zusätzlich `incomplete`), `expand`, `fields`, `order_by`, `per_page` | `projects.cycles:read` | CE | `cycle.py` |
| CY2 | POST | `…/projects/{pid}/cycles/` | Body `name`*, `description`, `start_date`, `end_date`, `owned_by` (Default aktueller User), `external_source`, `external_id`, `timezone` (433 IANA-Zonen) → 201 inkl. Zählern `total_issues`, `completed_issues`, `cancelled_issues`, `started_issues`, `unstarted_issues`, `backlog_issues`, `status` | `projects.cycles:write` | CE | `cycle.py` |
| CY3 | GET | `…/cycles/{cycle_id}/` | Detail | `projects.cycles:read` | CE | `cycle.py` |
| CY4 | PATCH | `…/cycles/{cycle_id}/` | ändern; „Completed cycles can only have their sort order changed“ | `projects.cycles:write` | CE | `cycle.py` |
| CY5 | DELETE | `…/cycles/{cycle_id}/` | löschen inkl. Zuordnungen | `projects.cycles:write` | CE | `cycle.py` |
| CY6 | GET | `…/cycles/{cycle_id}/cycle-issues/` | Work Items im Cycle (Objekte `{id,cycle,issue,sub_issues_count,created_at}`) | `projects.cycles:read` | CE | `cycle.py` |
| CY7 | POST | `…/cycles/{cycle_id}/cycle-issues/` | Body `issues`* (array UUID) → 200 Array CycleIssue | `projects.cycles:write` | CE | `cycle.py` |
| CY8 | DELETE | `…/cycles/{cycle_id}/cycle-issues/{wid}/` | entfernen | `projects.cycles:write` | CE | `cycle.py` |
| CY9 | POST | `…/cycles/{cycle_id}/transfer-issues/` | Body `new_cycle_id`*; Fortschritts-Snapshot, nur unerledigte Items (s. D14) → 200 `{"message":"Success"}` | `projects.cycles:write` | CE | `cycle.py` |
| CY10 | POST | `…/cycles/{cycle_id}/archive/` | archivieren; nur beendete Cycles → 204 | `projects.cycles:write` | CE | `cycle.py` |
| CY11 | GET | `…/projects/{pid}/archived-cycles/` | archivierte Cycles | `projects.cycles:read` | CE | `cycle.py` |
| CY12 | DELETE | `…/archived-cycles/{cycle_id}/unarchive/` | wiederherstellen → 204 | `projects.cycles:write` | CE | `cycle.py` |
| – | GET | `…/cycles-lite/`, GET `…/cycle-issues/{issue_id}/` | nur CE, undokumentiert | – | CE (undokumentiert) | `cycle.py` |

### 2.4 Epics (`AR/epics/`) – vollständig EE-only

| # | Methode | Pfad | Zweck | Scope | Status |
|---|---|---|---|---|---|
| E1 | GET | `workspaces/{ws}/projects/{pid}/epics/` | Liste, paginiert (`cursor`, `per_page`) | `projects.epics:read` | EE-only |
| E2 | POST | `workspaces/{slug}/projects/{pid}/epics/` | anlegen → 201 | `projects.epics:write` | EE-only |
| E3 | GET | `workspaces/{ws}/projects/{pid}/epics/{epic_id}/` | Detail; Query `fields` | `projects.epics:read` | EE-only |
| E4 | PATCH | `workspaces/{slug}/projects/{pid}/epics/{epic_id}/` | ändern; „Supports external ID validation to prevent conflicts“ | `projects.epics:write` | EE-only |
| E5 | DELETE | `workspaces/{slug}/projects/{pid}/epics/{epic_id}/` | löschen; **Kinder verlieren `parent`** → 204 | `projects.epics:write` | EE-only |
| E6 | GET | `workspaces/{slug}/projects/{pid}/epics/{epic_id}/issues/` | Kinder des Epics, paginiert | `projects.epics:read` + `projects.work_items:read` (D10) | EE-only |
| E7 | POST | `workspaces/{slug}/projects/{pid}/epics/{epic_id}/issues/` | Body `work_item_ids`*; setzt `parent`, „Validates type hierarchy“ → 200 Array Work Items | `projects.epics:write` | EE-only |

### 2.5 Estimates (`AR/estimate/`) – CE-teilweise

| # | Methode | Pfad | Zweck | Scope | Status | CE-Beleg |
|---|---|---|---|---|---|---|
| ES1 | GET | `…/projects/{pid}/estimates/` | das (eine) Estimate des Projekts | `projects.estimates:read` | CE-teilweise | View `apps/api/plane/api/views/estimate.py:30-135`, URL-Modul `apps/api/plane/api/urls/estimate.py`, **nicht** in `apps/api/plane/api/urls/__init__.py` eingebunden |
| ES2 | POST | `…/projects/{pid}/estimates/` | Body `name`*, `description`, `type` (`categories`,`points`,`time`), `last_used`, `external_id`, `external_source` → 201 | `projects.estimates:write` | CE-teilweise (Typ `time` EE, s. F21) | wie ES1 |
| ES3 | PATCH | `…/projects/{pid}/estimates/` | Body `name`, `description`, `external_id`, `external_source` | `projects.estimates:write` | CE-teilweise | wie ES1 |
| ES4 | DELETE | `…/projects/{pid}/estimates/` | löschen | `projects.estimates:write` | CE-teilweise | wie ES1 |
| ES5 | GET | `…/estimates/{estimate_id}/estimate-points/` | Punkte | `projects.estimates:read` | CE-teilweise | `views/estimate.py:137-232` |
| ES6 | POST | `…/estimates/{estimate_id}/estimate-points/` | Body: JSON-Array **oder** `{estimate_points:[…]}`; je Punkt `value`* (≤ 20 Zeichen), `key` (int), `description`, `external_id`, `external_source` → 201 Array | `projects.estimates:write` | CE-teilweise | wie ES5 |
| ES7 | PATCH | `…/estimate-points/{estimate_point_id}/` | Body `key`, `value`, `description`, `external_id`, `external_source` | `projects.estimates:write` | CE-teilweise | `views/estimate.py:234-291` |
| ES8 | DELETE | `…/estimate-points/{estimate_point_id}/` | löschen | `projects.estimates:write` | CE-teilweise | wie ES7 |

### 2.6 IdP Group Sync (`AR/idp-group-sync/`) – vollständig EE-only

| # | Methode | Pfad | Zweck | Scope | Status |
|---|---|---|---|---|---|
| G1 | GET | `workspaces/{ws}/group-sync/config/` | Konfiguration; **legt bei erstem Zugriff mit Defaults an** | `workspaces.group_sync:read` | EE-only |
| G2 | PATCH | `workspaces/{ws}/group-sync/config/` | Teil-Update | `workspaces.group_sync:write` | EE-only |
| G3 | GET | `workspaces/{ws}/group-sync/workspace-mappings/` | Liste (nicht paginiert, Array) | `workspaces.group_sync:read` | EE-only |
| G4 | POST | `workspaces/{ws}/group-sync/workspace-mappings/` | Body `idp_group_name`*, `role`* → 201 | `workspaces.group_sync:write` | EE-only |
| G5 | GET | `…/workspace-mappings/{mapping_id}/` | Detail | `workspaces.group_sync:read` | EE-only |
| G6 | PATCH | `…/workspace-mappings/{mapping_id}/` | Teil-Update | `workspaces.group_sync:write` | EE-only |
| G7 | DELETE | `…/workspace-mappings/{mapping_id}/` | löschen → 204 | `workspaces.group_sync:write` | EE-only |
| G8 | GET | `workspaces/{ws}/group-sync/project-mappings/` | Liste (Array) | `workspaces.group_sync:read` | EE-only |
| G9 | POST | `workspaces/{ws}/group-sync/project-mappings/` | Body `idp_group_name`*, `role`*, `project` **xor** `all_projects` → 201 | `workspaces.group_sync:write` | EE-only |
| G10 | GET | `…/project-mappings/{mapping_id}/` | Detail | `workspaces.group_sync:read` | EE-only |
| G11 | PATCH | `…/project-mappings/{mapping_id}/` | Teil-Update | `workspaces.group_sync:write` | EE-only |
| G12 | DELETE | `…/project-mappings/{mapping_id}/` | löschen → 204 | `workspaces.group_sync:write` | EE-only |

### 2.7 Inbox Issues (`AR/inbox-issue/`) – deprecated

| # | Methode | Pfad | Status |
|---|---|---|---|
| IB1 | GET | `…/projects/{pid}/inbox-issues/` | entfällt (Support-Ende 31.03.2025, ersetzt durch `intake-issues`; `AR/inbox-issue/overview.md`); CE hat keine Route |
| IB2 | POST | `…/projects/{pid}/inbox-issues/` | entfällt |
| IB3 | GET | `…/projects/{pid}/inbox-issues/{issue_id}` | entfällt |
| IB4 | PATCH | `…/projects/{pid}/inbox-issues/{issue_id}` | entfällt |
| IB5 | DELETE | `…/projects/{pid}/inbox-issues/{issue_id}` | entfällt |

### 2.8 Initiatives (`AR/initiative/`) – vollständig EE-only

| # | Methode | Pfad | Zweck | Scope | Status |
|---|---|---|---|---|---|
| I1 | GET | `workspaces/{ws}/initiatives/` | Liste (s. D7) | `initiatives:read` | EE-only |
| I2 | POST | `workspaces/{ws}/initiatives/` | anlegen → 201 | `initiatives:write` | EE-only |
| I3 | GET | `workspaces/{ws}/initiatives/{initiative_id}/` | Detail | `initiatives:read` | EE-only |
| I4 | PATCH | `workspaces/{ws}/initiatives/{initiative_id}/` | ändern | `initiatives:write` | EE-only |
| I5 | DELETE | `workspaces/{ws}/initiatives/{initiative_id}/` | löschen → 204 | `initiatives:write` | EE-only |
| I6 | GET | `workspaces/{ws}/initiatives/labels/` | Initiative-Label-Katalog des Workspace, paginiert | `initiatives.labels:read` | EE-only |
| I7 | POST | `workspaces/{ws}/initiatives/labels/` | Label anlegen → 201 | `initiatives.labels:write` | EE-only |
| I8 | GET | `workspaces/{ws}/initiatives/labels/{label_id}/` | Label-Detail | `initiatives.labels:read` | EE-only |
| I9 | PATCH | `workspaces/{ws}/initiatives/labels/{label_id}/` | Label ändern | `initiatives.labels:write` | EE-only |
| I10 | DELETE | `workspaces/{ws}/initiatives/labels/{label_id}/` | Label löschen → 204 | `initiatives.labels:write` | EE-only |
| I11 | GET | `workspaces/{ws}/initiatives/{initiative_id}/labels/` | Labels einer Initiative, paginiert | `initiatives.labels:read` | EE-only |
| I12 | POST | `workspaces/{ws}/initiatives/{initiative_id}/labels/` | Body `label_ids` → 200 | `initiatives.labels:write` | EE-only |
| I13 | DELETE | `workspaces/{ws}/initiatives/{initiative_id}/labels/` | Labels entfernen (Body vermutl. `label_ids`, D6) → 204 | `initiatives.labels:write` | EE-only |
| I14 | GET | `workspaces/{ws}/initiatives/{initiative_id}/projects/` | Projekte der Initiative, paginiert | `initiatives.projects:read` | EE-only |
| I15 | POST | `workspaces/{ws}/initiatives/{initiative_id}/projects/` | Body `project_ids` → 200 | `initiatives.projects:write` | EE-only |
| I16 | DELETE | `workspaces/{ws}/initiatives/{initiative_id}/projects/` | Body `project_ids` (MCP) → 204 | `initiatives.projects:write` | EE-only |
| I17 | GET | `workspaces/{ws}/initiatives/{initiative_id}/epics/` | Epics der Initiative, paginiert, `state` expandiert | `initiatives.epics:read` | EE-only |
| I18 | POST | `workspaces/{ws}/initiatives/{initiative_id}/epics/` | Body `epic_ids` → 200 | `initiatives.epics:write` | EE-only |
| I19 | DELETE | `workspaces/{ws}/initiatives/{initiative_id}/epics/` | Epics entfernen (Body vermutl. `epic_ids`, D6) → 204 | `initiatives.epics:write` | EE-only |

> Routing-Hinweis: `initiatives/labels/` muss **vor** `initiatives/{initiative_id}/` gematcht werden (Literal vs. UUID).

### 2.9 Intake (`AR/intake-issue/`)

| # | Methode | Pfad | Zweck | Scope | Status | CE-Beleg |
|---|---|---|---|---|---|---|
| IN1 | GET | `…/projects/{pid}/intake-issues/` | Liste; `cursor`, `expand`, `fields`, `per_page` | `projects.intakes:read` | CE | `intake.py` |
| IN2 | POST | `…/projects/{pid}/intake-issues/` | Body `issue`* (object mit `name`*, `description`, `priority`) → 201 `{id,status,source,issue{id,name,description,priority,sequence_id},created_at,updated_at}` | `projects.intakes:write` | CE | `intake.py` |
| IN3 | GET | `…/intake-issues/{wid}/` | Detail (Pfad-ID = `issue`-ID, nicht Intake-Record-ID; MCP `DD/dev-tools/mcp-server-tools.md:446`) | `projects.intakes:read` | CE | `intake.py` |
| IN4 | PATCH | `…/intake-issues/{wid}/` | Body `status` (-2 Pending, -1 Rejected, 0 Snoozed, 1 Accepted, 2 Duplicate), `snoozed_till`, `duplicate_to`, `source`, `source_email`, `issue` (object) | `projects.intakes:write` | CE | `intake.py` |
| IN5 | DELETE | `…/intake-issues/{wid}/` | löschen; löscht auch das Work Item, falls nicht akzeptiert | `projects.intakes:write` | CE | `intake.py` |

### 2.10 Work Items (`AR/issue/`)

| # | Methode | Pfad | Zweck | Scope | Status | CE-Beleg |
|---|---|---|---|---|---|---|
| W1 | GET | `…/projects/{pid}/work-items/` | Liste; `cursor`, `expand`, `external_id`, `external_source`, `fields`, `order_by`, `per_page`; MCP zusätzlich `pql` (`DD/dev-tools/mcp-server-tools.md:44-48`) | `projects.work_items:read` | CE (abweichend: CE lehnt Query-Parameter `pql` und `filters` mit **400** ab – Body `{"pql": "PQL and structured filters are not supported on this Plane edition. …", "unsupported_parameters": [...]}`, `apps/api/plane/api/views/issue.py:324-335`) | `work_item.py` |
| W2 | POST | `…/projects/{pid}/work-items/` | Body: `assignees`, `labels`, `type_id`, `parent`, `deleted_at`, `point` (int), `name`*, `description_html`, `description_stripped`, `priority` (`urgent`,`high`,`medium`,`low`,`none`), `start_date`, `target_date`, `sequence_id`, `sort_order`, `completed_at`, `archived_at`, `last_activity_at`, `is_draft`, `external_source`, `external_id`, `created_by`, `state`, `estimate_point`, `type` | `projects.work_items:write` | CE (abweichend: `type_id` wirkt im CE nur auf vorhandene `IssueType`-Zeilen, `apps/api/plane/api/serializers/issue.py:65-67,190-196`) | `work_item.py` |
| W3 | GET | `…/work-items/{wid}/` | Detail; `expand` (`type`,`module`,`labels`,`assignees`,`state`,`project`), `external_id`, `external_source`, `fields`, `order_by` | `projects.work_items:read` | CE | `work_item.py` |
| W4 | PATCH | `…/work-items/{wid}/` | wie W2 (alle optional) | `projects.work_items:write` | CE | `work_item.py` |
| W5 | DELETE | `…/work-items/{wid}/` | nur Admins oder Ersteller | `projects.work_items:write` | CE | `work_item.py` |
| W6 | GET | `workspaces/{ws}/work-items/{project_identifier}-{issue_identifier}/` | per Kennung `ENG-42` | `projects.work_items:read` | CE | `work_item.py` |
| W7 | GET | `workspaces/{ws}/work-items/search/` | Query `search`*, `limit`, `project_id`, `workspace_search` → `{issues:[{id,name,sequence_id,project__identifier,project_id,workspace__slug}]}` | `projects.work_items:read` | CE | `work_item.py` |
| W8 | POST | `workspaces/{ws}/work-items/advanced-search/` | Body `query`, `filters` (IssueFilterSet-JSON), `limit`, `workspace_search`, `project_id` | – (D17) | **EE-only** (F20) | – |
| – | GET/POST/… | `…/issues/…` (alte Pfade) | CE hält Legacy-Pfade parallel (`old_url_patterns`) | – | CE (undokumentiert) | `work_item.py` |

### 2.11 Work-Item-Activity, -Attachments, -Comments, -Links, -Relations (`AR/issue-activity/`, `AR/issue-attachments/`, `AR/issue-comment/`, `AR/link/`, `AR/work-item-relations/`)

| # | Methode | Pfad | Zweck | Scope | Status | CE-Beleg |
|---|---|---|---|---|---|---|
| WA1 | GET | `…/work-items/{wid}/activities/` | Aktivitäten; `cursor`,`expand`,`fields`,`order_by`,`per_page` | `projects.work_items.activities:read` | CE | `work_item.py` |
| WA2 | GET | `…/work-items/{wid}/activities/{activity_id}/` | Detail | `projects.work_items.activities:read` | CE | `work_item.py` |
| WT1 | POST | `…/work-items/{wid}/attachments/` | Upload-Credentials; Body `name`*,`type`,`size`*,`external_id`,`external_source` | `projects.work_items.attachments:write` | CE | `work_item.py` |
| WT2 | PATCH | `…/work-items/{wid}/attachments/{attachment_id}/` | `is_uploaded` → 204 (doppelt dokumentiert als „Complete upload“ und „Update an attachment“) | `projects.work_items.attachments:write` | CE | `work_item.py` |
| WT3 | GET | `…/work-items/{wid}/attachments/` | Liste | `projects.work_items.attachments:read` | CE | `work_item.py` |
| WT4 | GET | `…/work-items/{wid}/attachments/{attachment_id}/` | Redirect auf Presigned-URL (D12) | `projects.work_items.attachments:read` | CE | `work_item.py` |
| WT5 | DELETE | `…/work-items/{wid}/attachments/{attachment_id}/` | löschen, Activity | `projects.work_items.attachments:write` | CE | `work_item.py` |
| WT6 | POST | `https://planefs-uploads.s3.amazonaws.com/` | Multipart-Upload mit Presigned-Feldern (`Content-Type`,`key`,`policy`,`x-amz-signature`,`file`) – kein Plane-Endpunkt | – | Storage | – |
| WC1 | GET | `…/work-items/{wid}/comments/` | Liste | `projects.work_items.comments:read` | CE | `work_item.py` |
| WC2 | POST | `…/work-items/{wid}/comments/` | Body `comment_json`,`comment_html`,`access` (`INTERNAL`,`EXTERNAL`),`external_source`,`external_id`,`parent` (Antwort-Thread) → 201 inkl. `actor{id,first_name,last_name,display_name,avatar}` | `projects.work_items.comments:write` | CE | `work_item.py`; `parent` in Modell `apps/api/plane/db/models/issue.py:475` |
| WC3 | GET | `…/work-items/{wid}/comments/{comment_id}/` | Detail | `projects.work_items.comments:read` | CE | `work_item.py` |
| WC4 | PATCH | `…/work-items/{wid}/comments/{comment_id}/` | wie WC2 | `projects.work_items.comments:write` | CE | `work_item.py` |
| WC5 | DELETE | `…/work-items/{wid}/comments/{comment_id}/` | löschen, Activity | `projects.work_items.comments:write` | CE | `work_item.py` |
| WL1 | GET | `…/work-items/{wid}/links/` | Liste | `projects.work_items.links:read` | CE | `work_item.py` |
| WL2 | POST | `…/work-items/{wid}/links/` | Body `url`*, `title` → `metadata{title,description,image}` | `projects.work_items.links:write` | CE | `work_item.py` |
| WL3 | GET | `…/work-items/{wid}/links/{link_id}/` | Detail | `projects.work_items.links:read` | CE | `work_item.py` |
| WL4 | PATCH | `…/work-items/{wid}/links/{link_id}/` | Body `url`, `title` | `projects.work_items.links:write` | CE | `work_item.py` |
| WL5 | DELETE | `…/work-items/{wid}/links/{link_id}/` | löschen | `projects.work_items.links:write` | CE | `work_item.py` |
| WR1 | GET | `…/work-items/{wid}/relations/` | gruppiert nach `blocking`,`blocked_by`,`duplicate`,`relates_to`,`start_after`,`start_before`,`finish_after`,`finish_before` | `projects.work_items:read` | CE (abweichend, D15) | `work_item.py:150`, View `apps/api/plane/api/views/issue.py:2326-2615` |
| WR2 | POST | `…/work-items/{wid}/relations/` | Body `relation_type`* (8 Werte wie WR1), `issues`* (array) → 201 Array mit `id,name,sequence_id,project_id,relation_type,state_id,priority,type_id,is_epic,created_at,updated_at,created_by,updated_by` | `projects.work_items:write` | CE (abweichend: CE-Response ohne `type_id`,`is_epic`) | `work_item.py:150`; Serializer `apps/api/plane/api/serializers/issue.py:563-598` |
| WR3 | POST | `…/work-items/{wid}/relations/remove/` | Body `related_issue`* → 204 | `projects.work_items:write` | **CE-teilweise** (nur `IssueRelationRemoveSerializer` `apps/api/plane/api/serializers/issue.py:601-611`, keine View-Methode/Route) | – |

### 2.12 Work Item Types, Properties, Options, Values (`AR/issue-types/`) – vollständig EE-only

| # | Methode | Pfad | Zweck | Scope | Status |
|---|---|---|---|---|---|
| T1 | GET | `…/projects/{pid}/work-item-types/` | Typen des Projekts (Array, nicht paginiert) | `projects.work_item_types:read` | EE-only |
| T2 | POST | `…/projects/{pid}/work-item-types/` | Body `name`*,`description`,`is_epic`,`is_active`,`external_source`,`external_id` → 201 | `projects.work_item_types:write` | EE-only |
| T3 | GET | `…/work-item-types/{type_id}/` | Detail | `projects.work_item_types:read` | EE-only |
| T4 | PATCH | `…/work-item-types/{type_id}/` | wie T2 optional | `projects.work_item_types:write` | EE-only |
| T5 | DELETE | `…/work-item-types/{type_id}/` | löschen → 204 | `projects.work_item_types:write` | EE-only |
| T6 | GET | `…/projects/{pid}/work-item-types/schema/` | Feld-Schema für LLM/MCP; Query `type_id`, `include` (`members`,`labels`) | `projects.work_item_types:read` | EE-only |
| P1 | GET | `…/work-item-types/{type_id}/work-item-properties/` | Properties eines Typs (Array) | `projects.work_item_properties:read` | EE-only |
| P2 | POST | `…/work-item-types/{type_id}/work-item-properties/` | anlegen (inkl. `options`) → 201 | `projects.work_item_properties:write` | EE-only |
| P3 | GET | `…/work-item-properties/{property_id}/` (unter Typ) | Detail | `projects.work_item_properties:read` | EE-only |
| P4 | PATCH | `…/work-item-properties/{property_id}/` (unter Typ) | ändern | `projects.work_item_properties:write` | EE-only |
| P5 | DELETE | `…/work-item-properties/{property_id}/` (unter Typ) | löschen → 204 | `projects.work_item_properties:write` | EE-only |
| O1 | GET | `…/projects/{pid}/work-item-properties/{property_id}/options/` | Optionen (Array) | `projects.work_item_property_options:read` | EE-only |
| O2 | POST | `…/work-item-properties/{property_id}/options/` | Body `name`*,`description`,`is_active`,`is_default`,`external_source`,`external_id`,`parent` → 201 | `projects.work_item_property_options:write` | EE-only |
| O3 | GET | `…/options/{option_id}/` | Detail | `projects.work_item_property_options:read` | EE-only |
| O4 | PATCH | `…/options/{option_id}/` | ändern | `projects.work_item_property_options:write` | EE-only |
| O5 | DELETE | `…/options/{option_id}/` | löschen → 204 | `projects.work_item_property_options:write` | EE-only |
| V1 | GET | `…/projects/{pid}/work-items/{wid}/work-item-properties/{property_id}/values/` | Wert(e) – Einzelwert oder Liste (is_multi); in Doku zweimal („List“/„Get“) | `projects.work_item_property_values:read` | EE-only |
| V2 | POST | `…/values/` | **Upsert**; Body `value`*,`external_id`,`external_source` → 200 | `projects.work_item_property_values:write` | EE-only |
| V3 | PATCH | `…/values/` | Teil-Update `value`,`external_id`,`external_source` → 200 | `projects.work_item_property_values:write` | EE-only |
| V4 | DELETE | `…/values/` | löscht alle Werte (auch Multi) → 204 | `projects.work_item_property_values:write` | EE-only |

### 2.13 Labels (`AR/label/`), Members (`AR/members/`), Milestones (`AR/milestones/`), Modules (`AR/module/`)

| # | Methode | Pfad | Zweck | Scope | Status | CE-Beleg |
|---|---|---|---|---|---|---|
| L1 | GET | `…/projects/{pid}/labels/` | Liste | `projects.labels:read` | CE | `label.py` |
| L2 | POST | `…/projects/{pid}/labels/` | Body `name`*,`color`,`description`,`external_source`,`external_id`,`parent`,`sort_order` | `projects.labels:write` | CE | `label.py` |
| L3 | GET | `…/labels/{label_id}/` | Detail | `projects.labels:read` | CE | `label.py` |
| L4 | PATCH | `…/labels/{label_id}/` | ändern | `projects.labels:write` | CE | `label.py` |
| L5 | DELETE | `…/labels/{label_id}/` | löschen | `projects.labels:write` | CE | `label.py` |
| M1 | GET | `…/projects/{pid}/project-members/` | Projektmitglieder (User-Lite + Rolle) | `projects.members:read` | CE | `member.py` |
| M2 | POST | `…/projects/{pid}/project-members/` | Body `member`*, `role` (20 Admin, 15 Member, 5 Guest) | `projects.members:write` | CE | `member.py` |
| M3 | GET | `…/project-members/{member_id}/` | Detail | `projects.members:read` | CE | `member.py` |
| M4 | PATCH | `…/project-members/{member_id}/` | Body `member`,`role` | `projects.members:write` | CE | `member.py` |
| M5 | DELETE | `…/project-members/{member_id}/` | entfernen | `projects.members:write` | CE | `member.py` |
| M6 | GET | `workspaces/{ws}/members/` | Workspace-Mitglieder inkl. `role` | `workspaces.members:read` | CE | `member.py` (`WorkSpaceAdminPermission`) |
| M7 | POST | `workspaces/{ws}/members/remove/` | Mitglied entfernen, in allen Projekten deaktivieren, **Seat-Anzahl reduzieren**; Body in `AR/` undokumentiert, laut v2-Pendant `email`* (string, E-Mail) und `remove_seat` (bool, optional), Antwort ohne Body (`V2/members/remove-workspace-member.md`) | `workspaces.members:write` | **EE-only** in der Public-API (F23); Fachlogik im CE über die interne App-API `DELETE /api/workspaces/{slug}/members/{pk}/` vorhanden (`apps/api/plane/app/urls/workspace.py:98`, `apps/api/plane/app/views/workspace/member.py:138-176`) | – |
| MS1 | GET | `…/projects/{pid}/milestones/` | Liste (Array; MCP: `cursor`,`per_page`) | – (D17) | EE-only | – |
| MS2 | POST | `…/projects/{pid}/milestones/` | Body `title`*,`target_date`,`external_id`,`external_source` → 201 | – | EE-only | – |
| MS3 | GET | `…/milestones/{milestone_id}/` | Detail | – | EE-only | – |
| MS4 | PATCH | `…/milestones/{milestone_id}/` | ändern | – | EE-only | – |
| MS5 | DELETE | `…/milestones/{milestone_id}/` | löschen → 204 | – | EE-only | – |
| MS6 | GET | `…/milestones/{milestone_id}/work-items/` | Zuordnungen `[{id,issue,milestone}]` | – | EE-only | – |
| MO1 | GET | `…/projects/{pid}/modules/` | Liste | `projects.modules:read` | CE | `module.py` |
| MO2 | POST | `…/projects/{pid}/modules/` | Body `name`*,`description`,`start_date`,`target_date`,`status` (`backlog`,`planned`,`in-progress`,`paused`,`completed`,`cancelled`),`lead`,`members`,`external_source`,`external_id` | `projects.modules:write` | CE | `module.py` |
| MO3 | GET | `…/modules/{module_id}/` | Detail | `projects.modules:read` | CE | `module.py` |
| MO4 | PATCH | `…/modules/{module_id}/` | ändern | `projects.modules:write` | CE | `module.py` |
| MO5 | DELETE | `…/modules/{module_id}/` | löschen | `projects.modules:write` | CE | `module.py` |
| MO6 | GET | `…/modules/{module_id}/module-issues/` | Work Items | `projects.modules:read` | CE | `module.py` |
| MO7 | POST | `…/modules/{module_id}/module-issues/` | Body `issues`* | `projects.modules:write` | CE | `module.py` |
| MO8 | DELETE | `…/module-issues/{wid}/` | entfernen | `projects.modules:write` | CE | `module.py` |
| MO9 | POST | `…/modules/{module_id}/archive/` | archivieren | `projects.modules:write` | CE | `module.py` |
| MO10 | GET | `…/projects/{pid}/archived-modules/` | archivierte | `projects.modules:read` | CE | `module.py` |
| MO11 | DELETE | `…/archived-modules/{module_id}/unarchive/` | wiederherstellen | `projects.modules:write` | CE | `module.py` |
| – | GET | `…/modules-lite/`, `…/project-members-lite/`, `…/members-lite/`, `…/projects/{pid}/members/` | nur CE, undokumentiert | – | CE (undokumentiert) | `module.py`, `member.py` |

### 2.14 Pages (`AR/page/`), Work-Item-Pages (`AR/work-item-pages/`)

| # | Methode | Pfad | Zweck | Scope | Status |
|---|---|---|---|---|---|
| PG1 | GET | `…/projects/{pid}/pages/` | Projektseiten; Query `type` (`all` Default, `public`, `private`, `shared`, `archived`), `search` (Titel, case-insensitive), `per_page` (Default 20, Max 100), `cursor` | `projects.pages:read` | EE-only (CE nur interne App-API `apps/api/plane/app/urls/page.py`) |
| PG2 | POST | `…/projects/{pid}/pages/` | Body `name`*, `access` (0 Public, 1 Private), `color`, `is_locked`, `archived_at`, `view_props`, `logo_props`, `external_id`, `external_source`, `description_html`* → 201 | `projects.pages:write` | EE-only |
| PG3 | GET | `…/projects/{pid}/pages/{page_id}/` | Detail | `projects.pages:read` | EE-only |
| PG4 | GET | `workspaces/{ws}/pages/` | **Wiki-Seiten** des Workspace (Query wie PG1) | `wiki.pages:read` | EE-only |
| PG5 | POST | `workspaces/{ws}/pages/` | Wiki-Seite anlegen (Body wie PG2) → 201 inkl. `owned_by` | `wiki.pages:write` | EE-only |
| PG6 | GET | `workspaces/{ws}/pages/{page_id}/` | Detail | `wiki.pages:read` | EE-only |
| WP1 | GET | `…/work-items/{wid}/pages/` | Page-Links eines Work Items; `cursor`,`order_by`,`per_page` | – (D17) | EE-only |
| WP2 | POST | `…/work-items/{wid}/pages/` | Body `page_id`* → 201 Link-Objekt | – | EE-only |
| WP3 | GET | `…/work-items/{wid}/pages/{page_id}/` | Detail (D11) | – | EE-only |
| WP4 | DELETE | `…/work-items/{wid}/pages/{page_id}/` | Link entfernen → 204 (D11) | – | EE-only |

### 2.15 Projects (`AR/project/`), Project Features (`AR/project-features/`), Project Labels (`AR/project-labels/`)

| # | Methode | Pfad | Zweck | Scope | Status | CE-Beleg |
|---|---|---|---|---|---|---|
| PR1 | GET | `workspaces/{ws}/projects/` | Liste; `cursor`,`expand`,`fields`,`order_by`,`per_page` | `projects:read` | CE | `project.py` |
| PR2 | POST | `workspaces/{ws}/projects/` | Body `name`*,`description`,`project_lead`,`default_assignee`,`identifier`*,`icon_prop`,`emoji`,`cover_image`,`module_view`,`cycle_view`,`issue_views_view`,`page_view`,`intake_view`,`guest_view_all_features`,`archive_in`,`close_in`,`timezone`,`external_source`,`external_id`,`is_issue_type_enabled`,`is_time_tracking_enabled` | `projects:write` | CE (Flags `is_issue_type_enabled`/`is_time_tracking_enabled` ohne Funktion, `apps/api/plane/api/serializers/project.py:93-94`) | `project.py` |
| PR3 | GET | `workspaces/{ws}/projects/{project_id}/` | Detail | `projects:read` | CE | `project.py` |
| PR4 | PATCH | `workspaces/{ws}/projects/{project_id}/` | wie PR2 + `default_state`, `estimate` | `projects:write` | CE | `project.py` |
| PR5 | DELETE | `workspaces/{ws}/projects/{project_id}/` | löschen | `projects:write` | CE | `project.py` |
| PR6 | POST | `…/projects/{pid}/archive/` | archivieren → 204 | `projects:write` | CE | `project.py` |
| PR7 | DELETE | `…/projects/{pid}/archive/` | wiederherstellen → 204 | `projects:write` | CE | `project.py` |
| PR8 | POST | `workspaces/{ws}/projects/templates/use/` | Projekt aus Template | `write` oder `projects:write` | **EE-only** (F19) | – |
| PF1 | GET | `…/projects/{pid}/features/` | Feature-Toggles | `projects.features:read` | **EE-only** (F16) | – |
| PF2 | PATCH | `…/projects/{pid}/features/` | Feature-Toggles setzen | `projects.features:write` | **EE-only** (F16) | – |
| PL1 | GET | `workspaces/{ws}/project-labels/` | Projekt-Label-Katalog, paginiert | `projects.labels:read` | **EE-only** (F18) | – |
| PL2 | POST | `workspaces/{ws}/project-labels/` | Body `name`*,`description`,`color`,`sort_order` → 201 | `projects.labels:write` | EE-only | – |
| PL3 | GET | `workspaces/{ws}/project-labels/{label_id}/` | Detail | `projects.labels:read` | EE-only | – |
| PL4 | PATCH | `workspaces/{ws}/project-labels/{label_id}/` | ändern | `projects.labels:write` | EE-only | – |
| PL5 | DELETE | `workspaces/{ws}/project-labels/{label_id}/` | löschen → 204 | `projects.labels:write` | EE-only | – |
| – | GET | `workspaces/{ws}/projects-lite/`, `…/projects/{pid}/summary/` | nur CE, undokumentiert | – | CE (undokumentiert) | `project.py` |

### 2.16 States (`AR/state/`), Stickies (`AR/sticky/`), User (`AR/user/`), Invitations (`AR/workspace-invitations/`)

| # | Methode | Pfad | Zweck | Scope | Status | CE-Beleg |
|---|---|---|---|---|---|---|
| S1 | GET | `…/projects/{pid}/states/` | Liste | `projects.states:read` | CE | `state.py` |
| S2 | POST | `…/projects/{pid}/states/` | Body `name`*,`description`,`color`*,`sequence`,`group` (`backlog`,`unstarted`,`started`,`completed`,`cancelled`,`triage`),`is_triage`,`default`,`external_source`,`external_id` → **200** | `projects.states:write` | CE (`triage` im CE-Modell `apps/api/plane/db/models/state.py:20,90`) | `state.py` |
| S3 | GET | `…/states/{state_id}/` | Detail | `projects.states:read` | CE | `state.py` |
| S4 | PATCH | `…/states/{state_id}/` | ändern | `projects.states:write` | CE | `state.py` |
| S5 | DELETE | `…/states/{state_id}/` | Default-States und States mit Work Items nicht löschbar | `projects.states:write` | CE | `state.py` |
| ST1 | GET | `workspaces/{ws}/stickies/` | Liste | `stickies:read` | CE | `sticky.py` |
| ST2 | POST | `workspaces/{ws}/stickies/` | Body `deleted_at`,`name`,`description` (object),`description_html`,`description_stripped`,`logo_props`,`color`,`background_color`,`sort_order`,`created_by`,`updated_by` | `stickies:write` | CE | `sticky.py` |
| ST3 | GET | `workspaces/{ws}/stickies/{sticky_id}/` | Detail | `stickies:read` | CE | `sticky.py` |
| ST4 | PATCH | `workspaces/{ws}/stickies/{sticky_id}/` | ändern | `stickies:write` | CE | `sticky.py` |
| ST5 | DELETE | `workspaces/{ws}/stickies/{sticky_id}/` | löschen | `stickies:write` | CE | `sticky.py` |
| U1 | GET | `users/me/` | aktueller Nutzer `{id,first_name,last_name,email,avatar,avatar_url,display_name}` | `profile:read` | CE | `user.py` |
| WI1 | GET | `workspaces/{ws}/invitations/` | Einladungen | „Workspace admin or owner“ | CE | `invite.py` (`WorkspaceOwnerPermission`, `apps/api/plane/api/views/invite.py:32-34`) |
| WI2 | POST | `workspaces/{ws}/invitations/` | Body `email`*, `role` (20/15/5) → 201 `{id,email,role,created_at,updated_at,responded_at,accepted}` | dto. | CE | `invite.py` |
| WI3 | GET | `workspaces/{ws}/invitations/{invitation_id}/` | Detail | dto. | CE | `invite.py` |
| WI4 | PATCH | `workspaces/{ws}/invitations/{invitation_id}/` | Body `email`,`role` | dto. | CE | `invite.py` |
| WI5 | DELETE | `workspaces/{ws}/invitations/{invitation_id}/` | löschen | dto. | CE | `invite.py` |

### 2.17 Teamspaces (`AR/teamspace/`), Worklogs (`AR/worklogs/`), Workspace Features (`AR/workspace-features/`) – vollständig EE-only

| # | Methode | Pfad | Zweck | Scope | Status |
|---|---|---|---|---|---|
| TS1 | GET | `workspaces/{ws}/teamspaces/` | Liste, paginiert | `teamspaces:read` | EE-only |
| TS2 | POST | `workspaces/{ws}/teamspaces/` | Body `logo_props`,`name`*,`description_json`,`description_html`,`description_stripped`,`created_by`,`updated_by`,`lead` → 201 | `teamspaces:write` | EE-only |
| TS3 | GET | `workspaces/{ws}/teamspaces/{teamspace_id}/` | Detail | `teamspaces:read` | EE-only |
| TS4 | PATCH | `workspaces/{ws}/teamspaces/{teamspace_id}/` | ändern | `teamspaces:write` | EE-only |
| TS5 | DELETE | `workspaces/{ws}/teamspaces/{teamspace_id}/` | löschen → 204 | `teamspaces:write` | EE-only |
| TS6 | GET | `…/teamspaces/{teamspace_id}/members/` | Mitglieder, paginiert | `teamspaces.members:read` | EE-only |
| TS7 | POST | `…/teamspaces/{teamspace_id}/members/` | Body `member_ids` → 200 User-Objekt(e) | `teamspaces.members:write` | EE-only |
| TS8 | DELETE | `…/teamspaces/{teamspace_id}/members/` | Mitglieder entfernen (Body vermutl. `member_ids`, D6) → 204 | `teamspaces.members:write` | EE-only |
| TS9 | GET | `…/teamspaces/{teamspace_id}/projects/` | Projekte | `teamspaces.projects:read` | EE-only |
| TS10 | POST | `…/teamspaces/{teamspace_id}/projects/` | Body `project_ids` → 200 Projekt-Objekt(e) | `teamspaces.projects:write` | EE-only |
| TS11 | DELETE | `…/teamspaces/{teamspace_id}/projects/` | Projekte entfernen (Body vermutl. `project_ids`, D6) → 204 | `teamspaces.projects:write` | EE-only |
| WG1 | GET | `…/work-items/{wid}/worklogs/` | Worklogs eines Work Items (Array; MCP `cursor`,`per_page`) | `projects.work_items.worklogs:read` | EE-only |
| WG2 | POST | `…/work-items/{wid}/worklogs/` | Body `description`,`duration` (Minuten),`created_by`,`updated_by` → 201 | `projects.work_items.worklogs:write` | EE-only |
| WG3 | PATCH | `…/work-items/{wid}/worklogs/{worklog_id}/` | ändern | `projects.work_items.worklogs:write` | EE-only |
| WG4 | DELETE | `…/work-items/{wid}/worklogs/{worklog_id}/` | löschen → 204 | `projects.work_items.worklogs:write` | EE-only |
| WG5 | GET | `…/projects/{pid}/total-worklogs/` | Summe je Work Item `[{issue_id,duration}]` | `projects.work_items.worklogs:read` | EE-only |
| WF1 | GET | `workspaces/{ws}/features/` | Workspace-Feature-Toggles | `workspaces.features:read` | EE-only |
| WF2 | PATCH | `workspaces/{ws}/features/` | setzen | `workspaces.features:write` | EE-only |

---

## 3. Feature-Tabelle (Bezahl-Features, die aus der API-Referenz hervorgehen)

Plan-Bezeichnungen: **Free** (= CE-Umfang, `DD/self-hosting/editions-and-versions.md`), **One** (Legacy-Self-hosted-Einmallizenz, „Plane one plan is not longer available“, `apps/web/components/workspace/billing/comparison/base.tsx:29-30`), **Pro**, **Business**, **Enterprise** (Spalte `enterprise` in `plans.tsx`), **Enterprise Grid** (heutiger Top-Plan; Doku-Badges `[Enterprise Grid]` in `DD/self-hosting/govern/ldap.md`, `DD/self-hosting/methods/airgapped-edition.md`, `DD/self-hosting/methods/fips-deployment.md`; WEB: https://plane.so/blog/introducing-enterprise-grid, 12.06.2026, „on top of everything in Business“). Wo die ältere Matrix `plans.tsx` und die aktuelle Nutzer-Doku sich widersprechen, gilt die aktuellere/spezifischere Quelle; der Widerspruch steht in der Spalte „Abstufung“. Nach ADR-001 sind in der Zielplattform **alle** Features immer aktiv; die Plan-Spalten dienen nur der Nachvollziehbarkeit „was ist Bezahl-Feature“.

| ID | Feature | ab Plan | Abstufung je Plan | CE-Status | Quelle |
|---|---|---|---|---|---|
| F01 | **Epics** (Work-Item-Typ „Epic“, Epic-API, Epic-Kinder) | Pro | Free/One: nein; Pro/Business/Enterprise: ja | Stub/UI-Hülle im CE | `AR/epics/*`; `apps/web/components/workspace/billing/comparison/plans.tsx:261-270`; `packages/types/src/issues/issue.ts:23-27` (`EIssueServiceType.EPICS`); WEB: https://docs.plane.so/work-items/epics (Label „Pro“) |
| F02 | **Initiatives** (inkl. Verknüpfung Projekte/Epics bzw. Work Items) | Pro | Pro/Business/Enterprise: ja (`plans.tsx:272-282`, `comingSoon: true`; Plane-University-Kurs 05 „Pro“). **Widerspruch:** eine andere University-Seite ordnet Epics/Initiatives Business zu (Dok. 23 WP-13, Dok. 20 W-V2). Sub-Initiativen „nur Enterprise“ (plane.so/plane-vs-linear) ist **UNVERIFIZIERT** – im Verifikationslauf nicht bestätigt | Stub/UI-Hülle im CE (Theme-Store `initiativesSidebarCollapsed`/`toggleInitiativesSidebar`, Asset-Typ `INITIATIVE_DESCRIPTION`, reservierte Slugs, Leerzustand) – korrigiert, vorher „fehlt“ | `AR/initiative/*`; `V2/initiatives/*`; `plans.tsx:272-282`; `apps/web/store/theme.store.ts:20,32,181-187`; `packages/types/src/enums.ts:72`; WEB: https://university.plane.so/courses/201-the-growth/05-intro-to-initiatives.html, https://docs.plane.so/core-concepts/projects/initiatives |
| F03 | **Initiative-Labels** (Workspace-Katalog + Zuordnung) | wie F02 | wie F02 | fehlt | `AR/initiative/*label*`; `apps/web/components/dropdowns/label/label-select.tsx:48` (EE-Scope „initiative“) |
| F04 | **Customers** (Kunden, Requests, Custom-Properties, Werte, Work-Item-Links) | Business | Free/One/Pro: nein; Business/Enterprise: ja | fehlt | `AR/customer/*`; WEB: https://docs.plane.so/customers, https://plane.so/blog/introducing-plane-business, https://university.plane.so/courses/202-the-power-relay/02-intro-to-customers.html |
| F05 | **Teamspaces** (Mitglieder, Projekte) | Pro | Pro/Business/Enterprise: ja (`PRO_PLAN_FEATURES` „Teamspaces“, `packages/constants/src/subscription.ts:28`; plane.so/pro laut Dok. 24 WS3); zusätzlich „Teamspace Cycles“ erst ab Business (`plans.tsx:381-390`). **Korrektur:** Die frühere Angabe „Pro: Basic; Business/Enterprise: Advanced“ ist in keiner Quelle belegt (`plans.tsx` hat keine Teamspaces-Zeile) und wurde entfernt | Stub/UI-Hülle im CE | `AR/teamspace/*`; `packages/constants/src/subscription.ts:28`; `plans.tsx:381-390`; WEB: https://docs.plane.so/core-concepts/workspaces/teamspaces |
| F06 | **Milestones** (Projekt-Meilensteine + Work-Item-Zuordnung) | Pro (korrigiert, vorher „unklar“) | Doku-Seite mit Label „Pro“, University-Kurs 07 „Pro-tier feature“; nicht in `plans.tsx` (die Zeile „Checkpoints“ `plans.tsx:284-295` ist ein anderes, nicht ausgeliefertes Feature, Dok. 23 WM-13); eingeführt v1.16.0 (05.11.2025) | Stub/UI-Hülle im CE | `AR/milestones/*`; `V2/milestones/*`; `packages/i18n/src/locales/en/project-settings.json:420-426`; WEB: https://docs.plane.so/core-concepts/projects/milestones, https://university.plane.so/courses/201-the-growth/07-intro-to-milestones.html, https://plane.so/changelog/release-v-1-16-0-introducing-milestones-and-recurring-cycles; Dok. 23 WM-14/WP-07 |
| F07 | **Time Tracking / Worklogs** | Pro (korrigiert, vorher „One“) | **Widerspruch:** `plans.tsx:183-191` One „Basic“, Pro „Historical timesheets“, Business/Enterprise „Historical timesheets and approvals“; aktuelle Doku-Seite Label „Pro“. One ist nicht mehr erhältlich (`base.tsx:29-30`) → niedrigster heute erhältlicher Plan Pro | teilweise im CE (nur Flag/Typen) | `AR/worklogs/*`; `V2/work-item-worklogs/*`; `plans.tsx:183-191`; `apps/api/plane/db/models/project.py:100`; WEB: https://docs.plane.so/core-concepts/issues/time-tracking (Label „Pro“; Dok. 23 WP-10) |
| F08 | **Work Item Types** | Pro | Pro/Business/Enterprise: ja | teilweise im CE (Modelle ohne API/UI) | `AR/issue-types/types/*`; `plans.tsx:205-213`; `apps/api/plane/db/models/issue_type.py:14-55` |
| F09 | **Custom Properties** (Properties, Dropdown-Optionen, Werte) | Pro | Pro: „Project-level custom properties“; Business/Enterprise: „Workspace-level properties and roll-ups“ (Workspace-Ebene siehe F40/F43) | Stub/UI-Hülle im CE (Work-Item-Modal-Kontext mit `issuePropertyValues`, `getActiveAdditionalPropertiesLength`, `handlePropertyValuesValidation`, `handleCreateUpdatePropertyValues`, `apps/web/components/issues/issue-modal/context/issue-modal-context.tsx:14-74`, Provider mit leeren Werten `provider.tsx:43`; Activity-Typ `ISSUE_ADDITIONAL_PROPERTIES_ACTIVITY`, `packages/types/src/issues/activity/base.ts:87`) – korrigiert, vorher „fehlt“; übereinstimmend Dok. 20 PF-06, Dok. 23 WM-03 | `AR/issue-types/{properties,options,values}/*`; `V2/work-item-properties/*`, `V2/work-item-property-options/*`, `V2/work-item-type-properties/*`; `plans.tsx:216-224`; `packages/types/src/issues/issue-property-values.ts` |
| F10 | **Formula-Properties** (`property_type=FORMULA`) | Pro (Konfidenz mittel; korrigiert, vorher „unklar (Business oder Enterprise)“) | Blog „Introducing Releases“ (13.05.2026): Release picker und Formula als neue Property-Typen der „advanced custom properties“, diese ab Pro (nur Such-Zusammenfassung). **Korrektur:** Die Matrix-Zeile „Databases + Formulas“ (`plans.tsx:909-919`, Sektion `knowledge-management`: „Put databases and formulas into a page …“) betrifft **Pages**, nicht Work-Item-Properties; sie gehört zu Dok. 26 P07-20 / Dok. 20 PF-77 | fehlt | `AR/issue-types/properties/add-property.md`; `DD/dev-tools/mcp-server-tools.md:511`; `packages/i18n/src/locales/en/work-item-type.json` (`formula`); WEB: https://plane.so/blog/introducing-releases |
| F11 | **Work-Item-Type-Schema-Endpunkt** (für LLM/MCP) | Pro (wie F08/F09) | v1 `…/work-item-types/schema/?type_id=`, v2 `…/work-item-types/{pk}/schema/` | fehlt | `AR/issue-types/types/get-work-item-type-schema.md`; `V2/work-item-types/*` |
| F12 | **IdP Group Sync** (OIDC-Gruppen → Workspace-/Projektrollen) | Enterprise Grid (korrigiert, vorher „unklar“) | Doku-Seite mit Tag „Enterprise Grid“; nur Self-hosted Commercial, nur OIDC (SAML/LDAP „coming soon“); Whitepaper „LDAP, SCIM, IdP group synchronization … Enterprise Grid“ (Dok. 20 PF-98), Dok. 27 P08-05 | fehlt (nur 33 i18n-Texte `workspace_settings.settings.group_syncing.*` + Illustration `group-syncing.tsx`; kein Code-Verweis außerhalb von `locales/`) – korrigiert, vorher „Stub/UI-Hülle“ | `AR/idp-group-sync/*`; `V2/group-sync/*`; `packages/i18n/src/locales/en/workspace-settings.json:192-256`; `packages/blocks/src/empty-state/assets/horizontal-stack/group-syncing.tsx`; WEB: https://docs.plane.so/authentication/group-sync, https://plane.so/blog/introducing-enterprise-grid |
| F13 | **Work-Item ↔ Page-Links** | Pro (korrigiert, vorher „One“) | historisch One (`plans.tsx:842-851`; `ONE_PLAN_FEATURES` „Link pages in issues and vice-versa“, `packages/constants/src/subscription.ts:38`); One nicht mehr erhältlich (`base.tsx:29-30`); Changelog „Pro“ (Dok. 26 P07-13) | fehlt (nur i18n `issue.pages.*`) | `AR/work-item-pages/*`; `PU/work-item-pages/*`; `plans.tsx:842-851`; Dok. 26 P07-13 |
| F14 | **Pages-Public-API + Wiki (Workspace-Seiten)** | Wiki: Pro (korrigiert, vorher „One bzw. Pro“); Projektseiten: Free | **Widerspruch:** `plans.tsx:865-874` Wiki ab One; aktueller und spezifischer: Upsell-Text „Upgrade to unlock Wiki … with Plane Pro.“ (`packages/i18n/src/locales/en/wiki.json:89-91`), `PRO_PLAN_FEATURES` „Wikis“ (`subscription.ts:30`), Doku „Wiki Pro“ (Dok. 26 P07-01, Dok. 20 PF-74). Weitere Abstufungen laut `plans.tsx:809-931`: Real-time Collab, Work-Item-Embeds, Publish historisch One+ (heute Pro, Dok. 26 P07-07/08/11); Nested Pages Business+; Versionen Pro 2 Tage / Business 3 Monate / Enterprise unbegrenzt; Seiten-Templates Pro+; Exports Pro „One download at a time“, Business+ „Queued downloads“ | teilweise im CE (Projektseiten nur interne API) | `AR/page/*`; `PU/page/*`; `V2/project-pages/*`, `V2/workspace-pages/*`; `plans.tsx:809-931`; `apps/api/plane/db/models/page.py:23-80` (`is_global`, `parent`) |
| F15 | **Geteilte private Seiten** (`type=shared`, Page-Sharing) | Business (korrigiert, vorher „unklar“) | Doku: „On the Business plan and above, you can selectively share private Wiki pages …“ (Dok. 26 P07-16). **Widerspruch:** CE-Upsell-Text v1.4.2 nennt „shared pages … with Plane Pro“ (`wiki.json:91`) – ältere Quelle | Stub/UI-Hülle im CE (`isPageSharingEnabled: false`, `apps/web/hooks/use-page-flag.ts:12-22`) – korrigiert, vorher „fehlt“ | `AR/page/list-project-pages.md`; `apps/web/hooks/use-page-flag.ts`; Dok. 26 P07-16 |
| F16 | **Projekt-Feature-API** (`/features/` inkl. `epics`, `work_item_types`; MCP zusätzlich `parallel_cycles`, `project_updates`, `workflows`) | kein eigenes Plan-Feature (steuert Bezahl-Features) | – | teilweise im CE (Einzelfelder am Projekt) | `AR/project-features/*`; `DD/dev-tools/mcp-server-tools.md:377`; `apps/api/plane/db/models/project.py:95-102` |
| F17 | **Workspace-Feature-API** (`project_grouping`, `initiatives`, `teams`, `customers`, `wiki`, `pi`) | kein eigenes Plan-Feature | – | fehlt | `AR/workspace-features/*` |
| F18 | **Project Grouping: Projekt-States + Projekt-Labels** | Pro (Projekt-States) | Plan-Tabelle „State Of Projects“: Pro+ (`plans.tsx:343-352`), University „Pro“; **Projekt-Labels: Plan nicht belegt** (Doku-Seite docs.plane.so/core-concepts/projects/project-labels ohne Plan-Angabe in der Such-Zusammenfassung; Dok. 23 WM-38 „unklar“) | fehlt (nur i18n `workspace_settings.settings.project_states`/`projects`; die CE-Treffer `projectStates` in `apps/web/components/automation/auto-close-automation.tsx:44` betreffen Work-Item-States) – korrigiert, vorher „Stub/UI-Hülle“ | `AR/project-labels/*`; `plans.tsx:343-352`; `packages/i18n/src/locales/en/workspace-settings.json:258-271`; WEB: https://university.plane.so/courses/201-the-growth/11-intro-to-project-states.html, https://docs.plane.so/core-concepts/projects/project-labels |
| F19 | **Project Templates** (`templates/use`) | Business | Business/Enterprise: ja | Stub/UI-Hülle im CE (Prop `templateId` ohne Wirkung in `apps/web/components/project/create-project-modal.tsx:27,36,82`; i18n `template.json`) | `AR/project/create-project-with-template.md`; `plans.tsx:392-401`; `packages/constants/src/subscription.ts:17`; WEB: https://plane.so/changelog/cloud-april-28-2025 |
| F20 | **Advanced Search** (OpenSearch-gestützt) | Pro | – | fehlt (CE hat einfache Suche W7) | `AR/issue/advanced-search-work-items.md`; `DD/self-hosting/govern/advanced-search.md:7` (Badge „Pro“) |
| F21 | **Zeitbasierte Estimates** (`type=time`) | Pro | Estimates Free/One „Basic“, Pro+ „Advanced“ | Stub/UI-Hülle im CE | `AR/estimate/overview.md`; `packages/constants/src/estimates.ts:15,121-141` (`is_ee: true`); `apps/api/plane/db/models/estimate.py:13-15` (nur `categories`,`points`); `plans.tsx:145-153` |
| F22 | **Custom Relation Definitions** (eigene Relationstypen, Workspace-Settings „Relations“) | Enterprise Grid (korrigiert, vorher „unklar“) | Doku-Seite docs.plane.so/work-items/custom-relations mit Label „Enterprise Grid“; Workspace-Admin legt unter Workspace Settings → Relations → „Add relation“ Titel und Inward-Name an | fehlt (CE-Enum kennt nur die festen Typen inkl. `implemented_by`/`implements`, `apps/api/plane/db/models/issue.py:272-293`; Forum: Relation-Definition-Endpunkte liefern auf CE 404) | `DD/dev-tools/mcp-server-tools.md:142-156`; `V2/work-item-relation-definitions/*`; `packages/i18n/src/locales/en/workspace-settings.json:277-281`; WEB: https://docs.plane.so/work-items/custom-relations, https://forum.plane.so/t/work-item-relation-tools-list-work-item-relation-definitions-list-work-item-relations-return-404-via-mcp-server-on-self-hosted-ce/274 |
| F23 | **Workspace-Mitglied per API entfernen inkl. Seat-Reduktion** | unklar (kein Plan-Feature; Commercial-API v1/v2; korrigiert, vorher „Cloud-only“ – die Seat-Reduktion betrifft auch Commercial-Self-hosted-Lizenzen) | Seat-Logik entfällt (ADR-001) | teilweise im CE (gleiche Fachlogik ohne Seats in der internen App-API `DELETE /api/workspaces/{slug}/members/{pk}/`, `apps/api/plane/app/views/workspace/member.py:138-176`; Public-API-Route fehlt) – korrigiert, vorher „fehlt“ | `AR/members/remove-workspace-member.md`; `V2/members/remove-workspace-member.md` |
| F24 | **Releases** (Release, Tags, Labels, Links, Kommentare, Changelog, Release-Property-Typ; Workspace- und Projekt-Releases) | Business (korrigiert, vorher „unklar“) | Doku-Seiten „Releases“ und „Project Releases“ mit Label „Business“ (Dok. 23 WP-08 und eigene WebSearch); Workspace-Feature `is_release_enabled` (`V2/workspace-features/overview.md`) | fehlt | `DD/dev-tools/mcp-server-tools.md:307-356`; `V2/releases/*`, `V2/release-{comments,labels,links,tags}/*`; WEB: https://plane.so/blog/introducing-releases, https://docs.plane.so/releases, https://docs.plane.so/projects/project-releases |
| F25 | **PQL** (Plane Query Language als Filter) | Pro | Pro/Business/Enterprise (`plans.tsx:658-667`) | Stub/UI-Hülle im CE (Public-API lehnt `pql`/`filters` explizit mit 400 ab, `apps/api/plane/api/views/issue.py:324-335`; Dok. 20 PF-52) – korrigiert, vorher „fehlt“ | `plans.tsx:658-667`; `DD/dev-tools/mcp-server-tools.md:44-48`; `apps/api/plane/api/views/issue.py:324-335` |
| F26 | **Rollen-Slugs / RBAC / Rollen- und Berechtigungs-API** (Rollen mit Namespace workspace/project, Permission-Schemes, effektive Berechtigungen) | Business (RBAC), Enterprise (GAC) | Free/One „Basic“, Pro „Pre-defined roles“, Business „RBAC“, Enterprise „GAC“ (`plans.tsx:695-703`) | fehlt (CE: feste Integer-Rollen `ROLE_CHOICES = ((20, "Admin"), (15, "Member"), (5, "Guest"))`, `apps/api/plane/db/models/workspace.py:19`, `apps/api/plane/db/models/project.py:21`; keine Slugs, keine Custom Roles) | `plans.tsx:695-703`; `DD/dev-tools/mcp-server-tools.md:409-421`; `AR/idp-group-sync/*` (Rollen-Slugs); `V2/roles/*`, `V2/permission-schemes/*`, `V2/permissions/*`, `V2/members/overview.md` |
| F27 | **Work-Item-/Projekt-Updates** (Status ON-TRACK/OFF-TRACK/AT-RISK) | Pro (schwacher Beleg; vorher „unklar“) | nur in der auskommentierten Matrix-Zeile „Project Updates“ Pro/Business/Enterprise (`plans.tsx:354-366`, Coming soon); so auch Dok. 20 PF-23, Dok. 23 WM-40; Projekt-Feature-Flag v2 `is_project_updates_enabled` (`V2/project-features/overview.md`); keine v2-Ressource für Updates | Stub/UI-Hülle im CE | `packages/types/src/enums.ts:87-91`; `packages/i18n/src/locales/en/update.json`; `plans.tsx:355-366`; WEB: https://forum.plane.so/t/epics-is-becoming-a-work-item-type-ships-tuesday-may-26/136 |
| F28 | **Intake per E-Mail** (`source_email`) | Business | Business/Enterprise (`plans.tsx:458-467`, Coming soon; Doku-Badge „Business“) | teilweise im CE (nur Feld `IntakeIssue.source_email`; Dok. 20 PF-37 und Dok. 23 WM-46 werten dasselbe als „Stub/UI-Hülle“) | `AR/intake-issue/update-intake-issue-detail.md`; `apps/api/plane/db/models/intake.py:77`; `plans.tsx:458-467`; `DD/self-hosting/govern/configure-dns-email-service.md:7` (Badge „Business“) |
| F29 | **Plane Intelligence / AI** (Workspace-Feature `pi` bzw. v2 `is_pi_enabled`, Dienste `pi-api`, `pi-worker`) | Pro (Konfidenz niedrig; vorher „unklar“) | Dok. 20 PF-82: Pro „1,000 AI credits/Seat/Monat“ (WebSearch); Self-hosted: Badge „Commercial Edition“ (`DD/self-hosting/govern/plane-ai/configure-plane-ai.md:7`), Plan nicht belegt; Detail Cluster P09 (Dok. 28) | fehlt | `AR/workspace-features/overview.md`; `V2/workspace-features/overview.md`; `HC/plane-enterprise/templates/workloads/pi-api.deployment.yaml` |
| F30 | **Agent Runs** (OAuth-Scopes `agents.runs:*`, `agents.run_activities:*`; Endpunkte `…/workspaces/{slug}/runs/…` laut Node-SDK) | unklar (Commercial Edition, Beta) | Dok. 28 P09-F50 | fehlt (nur Scope-Beschreibungstext `workspace_settings.settings.applications.scope_description.agents` und Propel-Icons; Dok. 28 wertet dies als „Stub“) – vorher „fehlt“, bestätigt | `DD/dev-tools/build-plane-app/oauth-scopes.md`; `DD/dev-tools/agents/*.md`; Dok. 28 Kap. „Agents“ (REST-Tabelle aus `plane-node-sdk`) |
| F31 | **OAuth-Apps mit Scopes** (Bearer-Token für Public-API; `/auth/o/authorize/`, `/auth/o/token/`) | unklar (Commercial Edition, Beta) | „OAuth application registration is available on Plane Cloud and Plane Commercial Edition; Plane Community Edition does not include it“ (`DD/dev-tools/mcp-server-self-host.md:18-21`) | fehlt (CE Public-API nur API-Key; kein OAuth-Provider in `apps/api/plane/urls.py`; nur i18n `workspace_settings.settings.applications.*`) | `AR/introduction.md`; `V2/authentication.md`; `DD/dev-tools/build-plane-app/*.md`; WEB: https://developers.plane.so/dev-tools/build-plane-app, https://github.com/makeplane/plane/issues/8782 |
| F32 | **Public API v2** (Plattform: `/api/v2/`, PATCH-only, problem+json, Offset-/Cursor-Pagination, sparse reads, `?fields=`/`?expand=`, Bulk-/Upsert-Endpunkte, Identity-Filter, globale Scopes `read`/`write`, OpenAPI `GET /api/v2/schema/`) | unklar (Commercial Edition/Cloud; Plan-Gating je Ressource über `402`) | nicht in `plans.tsx`; öffentliche Verfügbarkeit von developers.plane.so/api-reference/v2 nur über WebSearch-URLs aus Dok. 26 (W24, W25, W39) belegt, eigene Suche ohne Treffer – **UNVERIFIZIERT** | fehlt (CE kennt nur `/api/v1/`, `apps/api/plane/urls.py:22`) | Kap. 9; `V2/introduction.md`, `V2/authentication.md`, `V2/errors.md`, `V2/pagination.md`, `V2/migrating-from-v1.md` |
| F33 | **Page-API-Erweiterungen v1** (Update/Archive/Restore/Delete von Projekt- und Wiki-Seiten, Page-Attachments, Wiki-Collections inkl. Mitglieder und Seiten) | wie F14/F15 (Wiki Pro, Collections Pro, Private Collections Business laut Dok. 26 P07-02/03) | – | fehlt in der Public-API (CE: Projektseiten-CRUD nur intern, `apps/api/plane/app/urls/page.py`) | Kap. 10; `PU/page/*`, `PU/collection/*`; Dok. 26 G1–G15 |
| F34 | **Audit-Log-API** (`GET …/audit-logs/`, `…/{pk}/`; Kategorien, Outcome, Source, Actor, Target, old/new value) | Business (Matrix „API-enabled Audit Logs“, Coming soon) – Widerspruch Enterprise Grid laut WebSearch (Dok. 20 PF-59) | Detail Dok. 27 | fehlt | `V2/audit-logs/*`; `plans.tsx:751-760` |
| F35 | **Automations-API** (Projekt- und Workspace-Automationen mit Nodes, Edges, Activities, Status, `regenerate-webhook-secret`) | Business (Projekt-Automationen) / Enterprise Grid (globale Automationen) – laut Dok. 25 F09/F13 | – | fehlt | `V2/project-automations/*`, `V2/workspace-automations/*`; Dok. 25 |
| F36 | **Views-API** (Projekt- und Workspace-Views in der Public-API, inkl. `filters`) | unklar (Views selbst sind Free, `plans.tsx:487-497`; die Public-API dafür existiert nur in v2) | Shared/Publish Views Pro (`plans.tsx:498-519`) | teilweise im CE (Views vollständig über interne App-API; keine Public-API) | `V2/project-views/*`, `V2/workspace-views/*` |
| F37 | **Work-Item-Templates-API** (Projekt-/Workspace-Templates, `…/{pk}/use/`) | Pro (`planHighlights.pro` „Work item templates“, `plans.tsx:1306`) | Detail Dok. 25 F21 | fehlt | `V2/project-work-item-templates/*`, `V2/workspace-work-item-templates/*` |
| F38 | **Webhooks-API v2 + Webhook-Logs** (Webhook-CRUD, `regenerate`, Delivery-Logs) | unklar (Dok. 28 P09-F51) | – | teilweise im CE (Webhook-CRUD, `regenerate` und Log-Liste `webhook-logs/{webhook_id}/` existieren in der internen App-API, `apps/api/plane/app/urls/webhook.py`, Modell `WebhookLog` `apps/api/plane/db/models/webhook.py:65`; keine Public-API, kein Log-Detail-Endpunkt, keine v2-Events) | `V2/webhooks/*`, `V2/webhook-logs/*`; Dok. 28 P09-F51 |
| F39 | **Work-Item-Dependencies-API** (eigene Ressource für `blocking`/`blocked_by`/`start_*`/`finish_*`) | Pro (Matrix „Dependencies in Gantt“, `plans.tsx:227-236`) | – | teilweise im CE (Relationstypen werden über v1-Relations gespeichert, Dok. 23 WM-26) | `V2/work-item-dependencies/*` |
| F40 | **Property Contexts** (kontextabhängige Regeln einer Workspace-Property je Projekt-/Typ-Menge: `is_required`, `is_multi`, `default_value`, `settings`, eigene Optionen) | Business (Workspace-Level-Properties, `plans.tsx:216-224`) – Widerspruch Enterprise Grid (Workspace-Typen laut Doku, Dok. 23 WP-01) | – | fehlt | `V2/work-item-property-contexts/*` |
| F41 | **Artifacts / Applets** (versionierte HTML-Dokumente für AI-Dashboards, publish per Anchor) | unklar (Plan-Feature „Applets“, sonst 402) | Detail Dok. 28 P09-F44 | fehlt | `V2/artifacts/*` |
| F42 | **Workflows-API** (Workflows, Workflow-States, State-Transitions; Fehlercode `workflow_transition_denied`) | Business (Default-Workflow) / Enterprise Grid (typ-spezifisch) – laut Dok. 25 F01/F02 | – | Stub/UI-Hülle im CE (Dok. 25: No-op-Hooks, i18n); keine API | `V2/workflows/*`, `V2/workflow-states/*`, `V2/workflow-transitions/*`; `V2/errors.md` |
| F43 | **Workspace-Mode für Work Item Types/Properties** (Workspace-Typen, Import in Projekte, `enable`, `mark-default`, Attach/Detach von Properties, Fehlercodes `work_item_types_managed_at_*`) | Enterprise Grid (Doku: Typen im Enterprise Grid auf Workspace-Ebene, WEB + Dok. 23 WP-01; Plane Compose „workspace-level WIT definitions (Enterprise)“, `DD/dev-tools/plane-compose.md:1003`) – Widerspruch Business (`plans.tsx:222`) | – | fehlt | `V2/work-item-type-modes.md`; `V2/workspace-work-item-*/*`; `V2/work-item-types/*` |

---

## 4. Feature-Abschnitte

Gemeinsame Konventionen für die Datenmodell-Tabellen: „R/W“ = RO (nur Response), W (Request-Body), RW (beides); „Pflicht“ bezieht sich auf POST. Typen nach JSON-Beispielen; `uuid` = String-UUID; `datetime` = ISO-8601 mit Zone; `date` = `YYYY-MM-DD`. Alle EE-Entitäten tragen nach Plane-Muster die Audit-Felder `created_at`, `updated_at`, `created_by`, `updated_by` und (Soft-Delete) `deleted_at` (vgl. CE-`BaseModel`, `apps/api/plane/db/models/base.py:17`).

### 4.1 F01 – Epics

**Funktionsbeschreibung.** Epics bündeln zusammengehörige Work Items als übergeordnetes Work Item (`AR/epics/overview.md`). Technisch ist ein Epic ein **Work Item, dessen Typ `is_epic=true` ist** (Feld `type` im Epic-Objekt = ID des Work-Item-Typs; `AR/epics/overview.md`; `is_epic` am Typ, `AR/issue-types/types/overview.md`). Seit 26.05.2026 ist „Epic“ in der Cloud ein normaler, konfigurierbarer Work-Item-Typ; die separate Epic-Oberfläche wurde in die Work-Item-Liste gefaltet, Kommentare/Updates/Sub-Items/Initiative-Verknüpfung bleiben erhalten (WEB: https://plane.so/blog/epics-is-becoming-a-work-item-type-in-plane; https://plane.so/changelog/2026-05-31-epics-work-item-type-publish-mcp-apps). Die MCP-Doku beschreibt den Workflow: Typ „Epic“ via `workitem_type resolve` holen, dann `workitem create` mit `type_id`; Kinder über `parent` (`DD/dev-tools/mcp-server-tools.md:50-58`). Verhalten:
- Beim Hinzufügen von Kindern (E7) wird die **Typ-Hierarchie validiert** und `parent` gesetzt (`AR/epics/add-epic-work-items.md`); seit 31.05.2026 können Eltern-Kind-Beziehungen zwischen Typen auf Workspace-Ebene definiert werden (WEB: Changelog 2026-05-31; i18n `work_item_type_hierarchy` in `packages/i18n/src/locales/en/work-item-type.json`).
- Löschen eines Epics setzt bei allen Kindern `parent = null` (`AR/epics/delete-epic.md`).
- `PATCH` prüft `external_id`-Konflikte (`AR/epics/update-epic.md`).
- Epics können Initiativen zugeordnet werden (I17–I19) und erscheinen in Relationen mit `is_epic` (WR2).

**Datenmodell (Epic-Objekt, `AR/epics/overview.md`, `create-epic.md`, `update-epic.md`)**

| Feld | Typ | R/W | Pflicht | Bemerkung |
|---|---|---|---|---|
| `id` | uuid | RO | – | |
| `name` | string | RW | ja | |
| `description` | object | RO | – | JSON-Repräsentation (leer `{}` im Beispiel) |
| `description_html` | string | RW | – | |
| `description_stripped` | string | RO | – | Plain Text |
| `description_binary` | string/null | RO | – | Yjs-Binary |
| `state` | uuid | RO | – | Request-Feld heißt `state_id` |
| `state_id` | uuid | W | – | |
| `priority` | enum | RW | – | `none`,`urgent`,`high`,`medium`,`low` |
| `assignees` | uuid[] | RO | – | Request-Feld `assignee_ids` |
| `assignee_ids` | uuid[] | W | – | |
| `labels` | uuid[] | RO | – | Request-Feld `label_ids` |
| `label_ids` | uuid[] | W | – | |
| `type` | uuid | RO | – | Work-Item-Typ (Epic-Typ) |
| `estimate_point` | uuid/null | RW | – | |
| `point` | int/null | RO | – | |
| `start_date` | date | RW | – | |
| `target_date` | date | RW | – | |
| `parent` | uuid/null | RO | – | Request-Feld `parent_id` |
| `parent_id` | uuid | W | – | |
| `sequence_id` | int | RO | – | projektweite laufende Nummer |
| `sort_order` | number | RO | – | |
| `is_draft` | bool | RO | – | |
| `completed_at` | datetime/null | RO | – | |
| `archived_at` | datetime/null | RO | – | |
| `project`, `workspace` | uuid | RO | – | |
| `external_id`, `external_source` | string/null | RW | – | |
| `deleted_at`, `created_at`, `updated_at` | datetime | RO | – | |
| `created_by`, `updated_by` | uuid | RO | – | |

Kind-Work-Items in E6/E7 enthalten zusätzlich `type_id` und `last_activity_at` (`AR/epics/list-epic-work-items.md`).

**API-Hinweise.** Endpunkte E1–E7 (Kap. 2.4). Pagination E1/E6 Cursor (Default 20, Max 100). Scopes `projects.epics:read/write`. Projekt-Feature-Toggle `epics` (F16) und Work-Item-Typen müssen aktiv sein.

**UI-Hinweise.** CE enthält bereits client-seitige Hüllen: Service-Typ `EIssueServiceType.EPICS` = `"epics"` (`packages/types/src/issues/issue.ts:23-27`), interne Pfade `/api/workspaces/{slug}/projects/{pid}/epics/…` inkl. `…/epics/{id}/issues/` (statt `sub-issues`) und `…/epics/{id}/links/` (statt `issue-links`) in `apps/web/services/issue/issue.service.ts:33-303`; Store-Typ `EIssuesStoreType.EPIC` (`packages/constants/src/issue/common.ts:110`); Epic-Verzweigungen in Peek-Overview, Listen, Kanban, Relationen, Sub-Issues (Dateiliste: `apps/web/components/issues/peek-overview/root.tsx`, `…/issue-layouts/list/block.tsx`, `…/kanban/block.tsx`, `…/issue-detail-widgets/relations/content.tsx`, `…/sub-issues/title.tsx`). Leerzustand-Illustration `packages/blocks/src/empty-state/assets/{horizontal,vertical}-stack/epic.tsx`. Reservierte Workspace-Slugs `epics`, `epic` (`packages/constants/src/workspace.ts`).

**Migrationshinweis.** Epic = `WorkItem` mit `WorkItemType.IsEpic`; **keine** separate Tabelle. REST-Fassade `/epics/` mappt `state_id→state`, `assignee_ids→assignees`, `label_ids→labels`, `parent_id→parent` (Datenmodell-Tabelle oben). Hierarchie-Validierung zentral im Domain-Service (Typ-Level-Regeln).

**Konfidenz:** hoch (Datenmodell), mittel (Hierarchie-Regeln).

### 4.2 F02/F03 – Initiatives und Initiative-Labels

**Funktionsbeschreibung.** Workspace-weite strategische Ziele, die Arbeit über Projekte, Epics und Work Items bündeln und Fortschritt messen (`AR/initiative/overview.md`). Lebenszyklus über `state`. Verknüpfungen: Projekte (I14–I16), Epics (I17–I19; seit Mai 2026 jedes Work Item, WEB Forum-Ankündigung), Labels (I11–I13) aus einem eigenen Workspace-Label-Katalog (I6–I10). Updates mit Status (F27). „Sub-initiatives only on Enterprise“ (WEB: https://plane.so/plane-vs-linear) ist **UNVERIFIZIERT**: Im Verifikationslauf fand die Suche keine Bestätigung (WEB: https://docs.plane.so/core-concepts/projects/initiatives, https://university.plane.so/courses/201-the-growth/05-intro-to-initiatives.html; ebenso Dok. 23 WP-13). Aktivierung: Workspace Settings → Tab „Initiatives“ → „Enable Initiatives“, danach Eintrag „Initiatives“ in der Sidebar unter „Workspace“ (WEB: docs.plane.so/core-concepts/projects/initiatives). Workspace-Feature `initiatives` (F17) bzw. v2 `is_initiative_enabled` (`V2/workspace-features/overview.md`). **v2-Abweichung:** Das Initiative-Objekt trägt `label_ids`, `project_ids`, `lead_id`; Verknüpfungen laufen über `POST …/initiatives/{pk}/labels/`, `…/projects/`, `…/work-items/` mit Body `{add: [uuid], remove: [uuid]}` (`V2/initiatives/manage-initiative-{labels,projects,work-items}.md`) – Work Items statt Epics bestätigt die Mai-2026-Semantik.

**Datenmodell Initiative (`AR/initiative/overview.md`, `add-initiative.md`)**

| Feld | Typ | R/W | Pflicht | Bemerkung |
|---|---|---|---|---|
| `id` | uuid | RO | | |
| `name` | string | RW | ja | |
| `description` | string | RW | | Plain Text (anders als Customer: object) |
| `description_html` | string | RW | | |
| `description_stripped` | string | RW | | |
| `description_binary` | string | RO | | |
| `lead` | uuid | RW | | User-ID |
| `start_date` | date | RW | | (Request-Beispiel mit datetime) |
| `end_date` | date | RW | | |
| `logo_props` | object | RW | | Icon/Emoji-Props (Plane-Standardstruktur) |
| `state` | enum | RW | | `DRAFT`,`PLANNED`,`ACTIVE`,`COMPLETED`,`CLOSED` |
| `archived_at` | datetime | RW | | |
| `workspace` | uuid | RO | | |
| `created_at`,`updated_at` | datetime | RO | | |
| `created_by`,`updated_by` | uuid | RW (Doku lässt Body zu) | | |

**Datenmodell Initiative-Label (`AR/initiative/add-initiative-label.md`)**: `id` uuid RO, `name` string Pflicht, `description` string, `color` string (Hex), `sort_order` number, `created_at` RO (+ implizit `workspace`).

**Verknüpfungs-Responses:** I15 liefert Projekt-Lite `{id,name,description,identifier,network,project_lead,created_at,updated_at}`; I14 `{id,name,description,identifier,network}`; I17 Epic-Lite `{id,name,description,priority,sequence_id,state{id,name,group},assignees,labels,created_at}`; I12/I11 Label-Lite.

**API-Hinweise.** Scopes `initiatives:*`, `initiatives.labels:*`, `initiatives.projects:*`, `initiatives.epics:*`. MCP-Create/Update akzeptiert `name`, `description_html`, `start_date`, `end_date`, `state`, `lead` (`DD/dev-tools/mcp-server-tools.md:290-305`). Pagination: I6, I11, I14, I17 Cursor; I1 widersprüchlich (D7).

**UI-Hinweise.** CE: Sidebar-Collapse-State `initiativesSidebarCollapsed` + `localStorage`-Key `initiatives_sidebar_collapsed` (`apps/web/store/theme.store.ts:20-187`) – zeigt, dass die Initiative-Detailseite eine einklappbare rechte Sidebar hat; Editor-Asset-Typ `INITIATIVE_DESCRIPTION` (`packages/types/src/enums.ts:72`); Leerzustand `packages/blocks/src/empty-state/assets/vertical-stack/initiative.tsx`; reservierte Slugs `initiatives`/`initiative` (`packages/constants/src/workspace.ts`, `apps/api/plane/utils/constants.py:47-48`). Weitere UI-Details sind nicht belegbar → Screenshots/andere Cluster.

**Migrationshinweis.** Tabellen `initiatives`, `initiative_labels`, `initiative_label_assignments`, `initiative_projects`, `initiative_work_items` (statt nur Epics, da Mai-2026-Semantik), optional `parent_initiative_id` (Sub-Initiativen). Beschreibung als Rich-Text (Yjs) wie Work Items.

**Konfidenz:** hoch (Felder/Endpunkte), mittel (Sub-Initiativen, beliebige Work Items).

### 4.3 F04 – Customers

**Funktionsbeschreibung.** Verwaltung von Kundenbeziehungen im Workspace: Kundenprofile, Kunden-Requests (Feature-Wünsche/Anfragen) und deren Verknüpfung mit Work Items sowie frei definierbare Kunden-Properties (`AR/customer/overview.md`). Laut Hersteller: Requests nach Kunde filtern, nach Umsatz/Vertragsstatus priorisieren; verknüpfte Work Items zeigen die Kunden dahinter; Aktivierung in den Workspace-Settings (WEB: https://plane.so/blog/introducing-plane-business, https://plane.so/customer-requests, https://university.plane.so/courses/202-the-power-relay/02-intro-to-customers.html). Workspace-Feature `customers` (F17). MCP-`create` ist ein **Upsert**: Treffer über `external_source`+`external_id`, sonst über `name` – erzeugt nie Duplikate; `delete` adressierbar über `customer_id` **oder** `external_source`+`external_id` (`DD/dev-tools/mcp-server-tools.md:475-477`).

**Datenmodell Customer (Union aus `AR/customer/add-customer.md`, `overview.md`, MCP)**

| Feld | Typ | R/W | Pflicht | Bemerkung |
|---|---|---|---|---|
| `id` | uuid | RO | | |
| `name` | string | RW | ja | |
| `description` | object | RW | | JSON-Dokument |
| `description_html` | string | RW | | |
| `description_stripped` | string | RW | | |
| `description_binary` | string | RO | | |
| `email` | string | RW | | |
| `website_url` | string | RW | | URL |
| `logo_props` | object | RW | | |
| `logo_asset` | uuid | RW | | FileAsset-ID |
| `logo_url` | string | RO | | abgeleitet aus Asset |
| `domain` | string | RW | | **UI-Label „Industry“** (Branche), nicht Web-Domain (`DD/dev-tools/mcp-server-tools.md:481`) |
| `employees` | integer | RW | | |
| `stage` | string | RW | | Freitext, UI kennt `lead`, `sales_qualified_lead`, `contract_negotiation`, `closed_won`, `closed_lost`; andere Werte werden gespeichert, aber nicht angezeigt |
| `contract_status` | string | RW | | UI kennt `active`, `pre_contract`, `signed`, `inactive` (dto.) |
| `revenue` | string | RW | | Jahresumsatz als String |
| `archived_at` | datetime | RW | | |
| `customer_request_count` | integer | RO | | Zähler |
| `external_source`,`external_id` | string | RW | | (MCP) |
| `workspace` | uuid | RO | | |
| `created_at`,`updated_at`,`deleted_at` | datetime | RO | | |
| `created_by`,`updated_by` | uuid | RW (Doku lässt Body zu) | | |

**Datenmodell Customer Request (`AR/customer/add-customer-request.md`, MCP `:483-495`)**: `id` uuid RO (impl.), `name` string Pflicht, `description` object, `description_html` string, `description_stripped` RO (impl.), `link` string (URL), `work_item_ids` uuid[] **write-only, nur bei Create wirksam, nie zurückgegeben** (Änderung danach über C12/C13 mit Request-Kontext), Audit-Felder, impl. `customer`, `workspace`. Delete entkoppelt verknüpfte Work Items (C10). Response-Beispiele der Doku fehlerhaft (D1).

**Datenmodell Customer Property (`AR/customer/add-customer-property.md`, MCP `:497-511`)**

| Feld | Typ | R/W | Pflicht | Bemerkung |
|---|---|---|---|---|
| `id` | uuid | RO | | |
| `name` | string | RO | | aus `display_name` abgeleitet |
| `display_name` | string | RW | ja | **workspaceweit eindeutig** |
| `description` | string | RW | | |
| `logo_props` | object | RW | | |
| `sort_order` | number | RW | | |
| `property_type` | enum | RW | ja | `TEXT`,`DATETIME`,`DECIMAL`,`BOOLEAN`,`OPTION`,`RELATION`,`URL`,`EMAIL`,`FILE` (MCP zusätzlich `FORMULA`) |
| `relation_type` | enum | RW | bei RELATION | `ISSUE`,`USER` (MCP zusätzlich `RELEASE`,`RICH_TEXT`) |
| `is_required` | bool | RW | | |
| `default_value` | array | RW | | Strings |
| `settings` | object | RW | | dokumentierter Schlüssel: `display_format`, weitere nicht dokumentiert (MCP: Pflicht für TEXT: `single-line`,`multi-line`,`readonly`; DATETIME: `MMM dd, yyyy`,`dd/MM/yyyy`,`MM/dd/yyyy`,`yyyy/MM/dd`) |
| `is_active` | bool | RW | | |
| `is_multi` | bool | RW | | |
| `validation_rules` | object | RW | | |
| `options` | array | W | | MCP: `[{name, description, is_default}]` |
| `external_source`,`external_id` | string | RW | | |
| Audit + `deleted_at` | | RO | | |

**Property-Werte (C19–C21):** PATCH-Body `{"values": ["…"]}` → 204; MCP: jeder Wert ist ein **String** unabhängig vom Typ, Ein-Element-Liste außer bei `is_multi`; `set_values` ersetzt nur die genannten Properties (`DD/dev-tools/mcp-server-tools.md:509-511`). GET-Schema undokumentiert (D2).

**Work-Item-Links (C11–C13):** Body `issue_ids`; optional Request-Kontext (MCP `customer_request_id`); Liste filterbar nach Request und `search`. v2 (Verifikationslauf): `POST …/customers/{pk}/work-items/` mit `{add, remove}`, `POST …/customers/upsert/`, Property-Werte per `GET`/`POST …/customers/{customer_id}/property-values/` (`V2/customers/*`, `V2/customer-property-values/*`).

**Tier (Verifikationslauf).** Business bestätigt (Plane University 202 „Business tier“, Blog „Introducing Plane Business“; übereinstimmend Dok. 20 PF-41 und Dok. 23 WM-16/WP-06). Die frühere Pro-Angabe „customer profiles“ (plane.so/pricing) ist UNVERIFIZIERT (Dok. 20 K01).

**UI-Hinweise.** Nicht im CE-i18n; nur Illustrationen `packages/blocks/src/empty-state/assets/{horizontal-stack,vertical-stack}/customer.tsx`. Felder „Industry“, „Stage“, „Contract status“, „Revenue“, „Employees“, „Website“, „Email“ ergeben sich aus MCP-Hinweisen.

**Migrationshinweis.** Tabellen `customers`, `customer_requests`, `customer_request_work_items`/`customer_work_items` (Link mit optionaler Request-ID), `customer_properties`, `customer_property_options`, `customer_property_values`. Custom-Property-Engine **gemeinsam** mit F09 implementieren (gleiche Typen/Settings), nur anderer „Owner“ (Customer statt Work Item).

**Konfidenz:** hoch (Customer/Property-Felder), mittel (Request-Schema, Werte-Schema).

### 4.4 F05 – Teamspaces

**Funktionsbeschreibung.** Abbildung realer Teams: Mitglieder und Projekte werden einem Teamspace zugeordnet, Arbeit nach Teams verfolgt (`AR/teamspace/overview.md`; WEB: https://docs.plane.so/core-concepts/workspaces/teamspaces). Ab Business „Teamspace Cycles“ (mehrere Cycles mehrerer Projekte gleichzeitig, `plans.tsx:381-390`). Seiten können in Teamspaces verschoben werden (i18n `page.json`: „Private and shared pages cannot be moved to a teamspace.“, „Search for projects and teamspaces“). Teamspace-Kommentare existieren (Asset-Typ `TEAM_SPACE_COMMENT_DESCRIPTION`, `packages/types/src/enums.ts:74`). Workspace-Feature `teams` (F17).

**Datenmodell Teamspace (`AR/teamspace/overview.md`, `add-teamspace.md`)**: `id` uuid RO; `name` string Pflicht; `description_json` object; `description_html` string; `description_stripped` string; `description_binary` string RO; `logo_props` object; `lead` uuid; `workspace` uuid RO; Audit-Felder (`created_by`/`updated_by` im Body erlaubt). Mitglieder-Response: User `{id,first_name,last_name,email,avatar,avatar_url,display_name}` (`AR/teamspace/add-teamspace-members.md`); Projekt-Response: Projekt-Lite.

**API-Hinweise.** TS1–TS11; Scopes `teamspaces:*`, `teamspaces.members:*`, `teamspaces.projects:*`; Pagination TS1/TS6 Cursor. MCP-Server bietet **kein** Teamspace-Tool (`DD/dev-tools/mcp-server-tools.md:9-13`, 28 Tools). v2 (Verifikationslauf): nur CRUD `…/teamspaces/` (5 Endpunkte, Scope `teamspaces:*`); das Objekt trägt `member_ids` und `project_ids`, Mitglieder und Projekte werden per `PATCH` gesetzt; weitere Felder `id`, `name`, `description_html`, `lead_id`, `logo_props`, `created_at`, `created_by_id`; `?expand=lead` (`V2/teamspaces/overview.md`, `V2/teamspaces/update-teamspace.md`).

**UI-Hinweise.** CE-Hüllen: Router-Getter `teamspaceId` aus Query (`apps/web/store/router.store.ts:18,83-84`), `teamspaceId` im Issue-Root-Store (`apps/web/store/issue/root.store.ts:46,114`), Filter-Entitätstyp „teamspace“ (`apps/web/components/work-item-filters/filters-hoc/shared.ts:13`), EE-Member-Dropdown mit Scope `teamspaceId` (`apps/web/components/dropdowns/member/member-select.tsx:62`), Realtime-Event-Feld `teamspace_id` (`packages/editor/src/types/document-collaborative-events.ts:43,60,75`), i18n `common.members_and_teamspaces` (`packages/i18n/src/locales/en/common.json:715`), Illustration `packages/blocks/src/empty-state/assets/vertical-stack/teamspace.tsx`. Das CE-Modell `Team` (`apps/api/plane/db/models/workspace.py:261-283`) ist ein Legacy-Rest ohne Mitglieder und **nicht** der Teamspace.

**Migrationshinweis.** Tabellen `teamspaces`, `teamspace_members`, `teamspace_projects`, ggf. `teamspace_comments`; Seiten-Zuordnung (`page.teamspace_id`) und Realtime-Dokument-Kontext berücksichtigen.

**Konfidenz:** hoch (API), niedrig–mittel (Advanced-Funktionen).

### 4.5 F06 – Milestones

**Funktionsbeschreibung.** Zeitbasierte Checkpoints im Projekt, die Work Items (laut Changelog auch Cycles/Module) unter einem gemeinsamen Termin bündeln (`AR/milestones/overview.md`; WEB: https://plane.so/changelog/release-v-1-16-0-introducing-milestones-and-recurring-cycles). Projekt-Feature mit Toggle „Enable milestones – Organize work items by milestone deadlines.“ (`packages/i18n/src/locales/en/project-settings.json:420-426`). Work Items lassen sich nach `milestone_id` gruppieren und per PQL-Feld `milestone` filtern (`DD/dev-tools/mcp-server-tools.md:48,91`). Zuordnung per MCP `milestone manage_workitems` (`add_ids`, `remove_ids`) – **REST-Endpunkt dafür ist nicht dokumentiert** (`DD/dev-tools/mcp-server-tools.md:274-288`).

**Datenmodell Milestone (`AR/milestones/overview.md`)**: `id` string/uuid RO; `title` string Pflicht; `target_date` date; `external_id`, `external_source` string; `created_at`, `updated_at` RO; impl. `project`, `workspace`. Zuordnungsobjekt (MS6): `{id, issue, milestone}` → n:m- oder 1:n-Link (offen, s. Kap. 8).

**Tier (Verifikationslauf).** Pro: Doku-Seite mit Label „Pro“ und University-Kurs 07 „Pro-tier feature“ (WEB: https://docs.plane.so/core-concepts/projects/milestones, https://university.plane.so/courses/201-the-growth/07-intro-to-milestones.html; übereinstimmend Dok. 23 WP-07). Laut Doku: Aktivierung unter Project Settings → Features, danach Abschnitt „Milestones“ auf der Projekt-Overview; Anlage mit Titel, Beschreibung, Zieldatum und verknüpften Work Items; Fortschritt in Prozent, steigt bei erledigten **oder abgebrochenen** Work Items; im Timeline-Layout als gestrichelte vertikale Linie am Fälligkeitsdatum (WEB, Such-Zusammenfassung). Das Feld „Beschreibung“ fehlt in v1 und v2 (`AR/milestones/overview.md`, `V2/milestones/overview.md`) – offen (Dok. 23 O-11).

**API-Hinweise.** MS1–MS6; Scope laut Q2 `projects.milestones:read/write`. Projekt-Feature-Flag `milestones` fehlt im v1-Feature-Objekt (PF1); in v2 existiert `is_milestone_enabled` (`V2/project-features/overview.md`). v2 ergänzt `POST …/milestones/bulk/`, `POST …/milestones/upsert/` und die bisher fehlende REST-Zuordnung `POST …/milestones/{pk}/work-items/` mit Body `{add: [uuid], remove: [uuid]}` (`V2/milestones/manage-milestone-work-items.md`); das v2-Objekt enthält zusätzlich `archived_at` und `created_by_id` (`V2/milestones/overview.md`).

**UI-Hinweise.** Projekt-Übersicht mit einklappbarer Sektion `"milestones"` (Default offen) (`apps/web/store/project/project.store.ts:21,86`); i18n `common.milestones`, `milestones_description` (`packages/i18n/src/locales/en/common.json:717,844-845`); Illustration `packages/blocks/src/empty-state/assets/vertical-stack/milestone.tsx`; Fetch-Key in `packages/constants/src/fetch-keys.ts`.

**Konfidenz:** mittel.

### 4.6 F07 – Time Tracking / Worklogs

**Funktionsbeschreibung.** Zeiterfassung pro Work Item in **Minuten** mit Beschreibung (`AR/worklogs/overview.md`). Projekt-Admin aktiviert per Projekt-Settings → Features → „Time tracking“ („Log time spent on work items and projects.“ / „Project members will be able to log time worked.“, `packages/i18n/src/locales/en/project-settings.json:413-419`). Im Work Item: „Log work“ mit Stunden, Minuten, Beschreibung; Einträge in der Activity bearbeit-/löschbar; Property „Tracked time“ aktualisiert sich (WEB: https://docs.plane.so/core-concepts/issues/time-tracking). Workspace-Settings → „Worklogs“: „Download worklogs AKA timesheets for anyone in any project.“ mit Filtern Nutzer/Projekte/Zeitraum (`packages/i18n/src/locales/en/workspace-settings.json:187-191`; WEB: https://university.plane.so/courses/201-the-growth/16-intro-to-time-tracking.html). Leerzustand „Track timesheets for all members“ (`packages/i18n/src/locales/en/empty-state.json:248-251`). Abstufung One „Basic“ → Pro „Historical timesheets“ → Business/Enterprise „… and approvals“ (`plans.tsx:183-191`). **Tier (Verifikationslauf):** Pro, weil die aktuelle Doku-Seite das Label „Pro“ trägt und One nicht mehr erhältlich ist (`apps/web/components/workspace/billing/comparison/base.tsx:29-30`); Widerspruch zur Matrix dokumentiert in Kap. 3. v2: `GET …/worklogs/summary/` ersetzt `total-worklogs/`, zusätzlich `GET …/worklogs/{pk}/` (`V2/work-item-worklogs/*`).

**Datenmodell Worklog (`AR/worklogs/overview.md`)**

| Feld | Typ | R/W | Bemerkung |
|---|---|---|---|
| `id` | uuid | RO | |
| `description` | string | RW | Default `""` |
| `duration` | integer | RW | Minuten (MCP-Pflichtfeld bei Create) |
| `logged_by` | uuid | RO | protokollierender Nutzer |
| `project_id`, `workspace_id` | uuid | RO | |
| `created_at`,`updated_at`,`deleted_at` | datetime | RO | |
| `created_by`,`updated_by` | uuid | RW | Body erlaubt (Erfassung für Dritte, vgl. „record time by members and guests“, WEB) |

Projekt-Summe (WG5): `[{issue_id: uuid, duration: int}]`.

**CE-Stand.** `Project.is_time_tracking_enabled` (`apps/api/plane/db/models/project.py:100`) und Public-API-Feld (`apps/api/plane/api/serializers/project.py:94`); Activity-Typ `WORKLOG` (`packages/types/src/issues/activity/base.ts:82`); Illustration `packages/blocks/src/empty-state/assets/horizontal-stack/worklog.tsx`; i18n `common.no_worklogs`, `common.worklogs` (`common.json:58,710`). Kein Modell, keine Endpunkte.

**Migrationshinweis.** Tabelle `work_item_worklogs`; Activity-Einträge `WORKLOG`; Export (CSV/XLSX) im Workspace-Settings-Bereich; Approvals (Business) → eigener Status-Workflow (Details in anderem Cluster).

**Konfidenz:** hoch (API), mittel (Approvals).

### 4.7 F08/F09/F10/F11 – Work Item Types und Custom Properties

**Funktionsbeschreibung.** Projekte (und – laut MCP – der Workspace) definieren Work-Item-Typen („Task“, „Bug“, „Feature“, `AR/issue-types/types/overview.md`). Jeder Typ hat Standardfelder und eigene Properties; Properties erscheinen automatisch an allen Work Items des Typs; „Mandatory“/„Active“ je Property (WEB: https://docs.plane.so/work-item-types). Ein Typ ist Default (`is_default`), Default-Typ kann nicht gelöscht/inaktiv gesetzt werden (i18n `work_item_types.settings.cant_delete_default_message`, `cant_set_default_inactive_message`, `packages/i18n/src/locales/en/work-item-type.json`). Workspace-Governance-Modus: Typ-/Property-Vokabular zentral im Workspace, projektbezogene Writes werden abgelehnt, Typen werden per `import_to_project` verknüpft (`DD/dev-tools/mcp-server-tools.md:38-42,175-189`); Typ-Hierarchie-Level (`level`, i18n `work_item_type_hierarchy`). **Präzisierung aus v2 (F43):** Ein Workspace arbeitet in genau einem Modus; Diskriminator ist `is_work_item_types_enabled` der Workspace-Features (`true` = Workspace-Modus); Schreiben auf die falsche Oberfläche liefert `409` mit `work_item_types_managed_at_workspace` bzw. `work_item_types_managed_at_project`; Lesen funktioniert in beiden Modi; Projekt-Modus: `POST …/projects/{pid}/work-item-types/enable/` legt den Default-Typ „Task“ an (idempotent); Workspace-Modus: Typen unter `…/workspaces/{slug}/work-item-types/` anlegen und per `POST …/projects/{pid}/work-item-types/import/` ins Projekt holen; Properties werden typunabhängig angelegt und per `POST …/work-item-types/{type_id}/properties/` angehängt, `DELETE` hängt ab, ohne zu löschen; das Schema wird immer auf der Projekt-Oberfläche gelesen (`V2/work-item-type-modes.md`). Tier Workspace-Modus: Enterprise Grid (Doku, Dok. 23 WP-01; `DD/dev-tools/plane-compose.md:1003` „workspace-level WIT definitions (Enterprise)“), Widerspruch Business (`plans.tsx:222`). Neue Work Items ohne `type_id` erhalten den Default-Typ (so bereits CE: `apps/api/plane/api/serializers/issue.py:190-196`). Projekt-Toggle `work_item_types` (PF1) bzw. CE-Feld `is_issue_type_enabled` (`apps/api/plane/db/models/project.py:101`). Forum-Hinweis: Aktivieren der Typen per REST kann die native Epic-Typ-Anlage verhindern (WEB: https://forum.plane.so/t/enabling-work-item-types-via-rest-api-silently-and-permanently-prevents-the-project-from-ever-having-the-native-epic-type/291).

**Datenmodell Work Item Type (`AR/issue-types/types/overview.md`, `add-issue-type.md`)**

| Feld | Typ | R/W | Pflicht | Bemerkung |
|---|---|---|---|---|
| `id` | uuid | RO | | |
| `name` | string | RW | ja | |
| `description` | string | RW | | |
| `logo_props` | object | RO (Doku-Body ohne) | | |
| `is_epic` | bool | RW | | |
| `is_default` | bool | RO | | |
| `is_active` | bool | RW | | |
| `level` | number | RO | | Hierarchie-Level (CE: `float` am Typ, `PositiveInteger` an `ProjectIssueType`, `apps/api/plane/db/models/issue_type.py:22,37`) |
| `project_ids` | uuid[] | RO (MCP: RW) | | Projekte, die den Typ nutzen |
| `workspace`, `project` | uuid | RO | | |
| `external_id`,`external_source` | string | RW | | |
| Audit + `deleted_at` | | RO | | |

**Datenmodell Property (`AR/issue-types/properties/overview.md`, `add-property.md`, MCP `:191-212`)**

| Feld | Typ | R/W | Pflicht | Bemerkung |
|---|---|---|---|---|
| `id` | uuid | RO | | |
| `name` | string | RO | | abgeleitet (Slug, Beispiel `first-issue-property`) |
| `display_name` | string | RW | ja | max. 255 (i18n `errors.name.max_length`) |
| `description` | string | RW | | |
| `logo_props` | object | RO | | |
| `sort_order` | number | RO | | |
| `property_type` | enum | RW | ja | `TEXT`,`DATETIME`,`DECIMAL`,`BOOLEAN`,`OPTION`,`RELATION`,`URL`,`EMAIL`,`FILE`,`FORMULA` |
| `relation_type` | enum/null | RW | | `ISSUE`,`USER` (MCP zusätzlich `RELEASE`,`RICH_TEXT`) |
| `is_required` | bool | RW | | |
| `default_value` | array | RW | | |
| `settings` | object | RW | | dokumentierter Schlüssel: `display_format` (s. Customer-Properties); weitere Schlüssel nicht dokumentiert |
| `is_active` | bool | RW | | |
| `is_multi` | bool | RW | | |
| `validation_rules` | object | RW | | |
| `formula_config` | string | RW | | nur `FORMULA` |
| `options` | array | W | | bei `OPTION`: `[{name, description?, is_default?, external_id?, external_source?}]` (MCP: `color`) |
| `issue_type` | uuid | RO | | Zuordnung zum Typ (MCP: n:m via `manage_type_properties attach_ids/detach_ids`; Detach löscht Property nicht) |
| `workspace`, `project` | uuid | RO | | |
| `external_id`,`external_source` | string | RW | | |
| Audit + `deleted_at` | | RO | | |

Formula-Tier (Verifikationslauf): Der Blog „Introducing Releases“ (13.05.2026) führt Release picker und Formula als neue Typen der „advanced custom properties“ ab Pro ein (WEB: https://plane.so/blog/introducing-releases, Such-Zusammenfassung). Die Matrix-Zeile „Databases + Formulas“ (`plans.tsx:909-919`) gehört zur Sektion `knowledge-management` (Pages) und ist **kein** Beleg für Formula-Properties (frühere Zuordnung in diesem Dokument korrigiert). UI-Mapping der Property-Typen (i18n `work_item_types.settings.properties.property_type`): Text, Number (`DECIMAL`), Dropdown (`OPTION`), Boolean, Date (`DATETIME`), Member picker (`RELATION`/`USER`), Formula; Attribute: Text „Single line“/„Paragraph“/„Read only“, Relation „Single select“/„Multi select“, Boolean „True | False“ (`packages/i18n/src/locales/en/work-item-type.json`). Formel-Syntax: `{Field Name}`-Referenzen mit Operatoren `+ - * / &`, Test-Button, Validierungsfehler „Circular reference detected…“, „Formula references non-existent property.“ (dto., Schlüssel `properties.formula`, `create_update.errors.formula`). Mandatory-Logik: Pflicht + Default-Option schließen sich aus (`mandate_confirmation`). Löschen bietet „disable instead“ an (`delete_confirmation`). Projekt-Settings: „Import from workspace“ (`properties.project.add_button.import_from_workspace`).

**Datenmodell Option (`AR/issue-types/options/overview.md`)**: `id`, `name` (Pflicht, innerhalb Property eindeutig – i18n „Option with same name already exists.“), `description`, `sort_order` (number, Beispiel 10000.0), `logo_props`, `is_active`, `is_default`, `parent` (uuid/null, hierarchische Optionen), `property` (uuid), `external_*`, `workspace`, `project`, Audit, `deleted_at`.

**Datenmodell Value (`AR/issue-types/values/*.md`)**: `id`, `property_id`, `issue_id`, `value` (typabhängig: String für TEXT/URL/EMAIL/FILE; UUID oder UUID-Liste für RELATION/OPTION (Liste nur bei `is_multi`); `YYYY-MM-DD` (MCP auch `YYYY-MM-DD HH:MM:SS`) für DATETIME; Zahl für DECIMAL; Bool für BOOLEAN), `value_type` (string), `external_id`, `external_source`, `created_at`, `updated_at`. Semantik: **eine** Wertzeile je (Work Item, Property), bei Multi mehrere; POST = Upsert (MCP: ersetzt bei Multi alle Werte), DELETE entfernt alle (`AR/issue-types/values/add-property-values.md`, `delete-property-value.md`). Wertänderungen erzeugen Activity `ISSUE_ADDITIONAL_PROPERTIES_ACTIVITY` (`packages/types/src/issues/activity/base.ts:87`).

**Schema-Endpunkt T6 (`AR/issue-types/types/get-work-item-type-schema.md`)**: Response `{type_id, type_name, type_description, type_logo_props, fields{…}, custom_fields{…}}`. Standardfelder immer: `name` (`{type:"string",required:true,max_length:255}`), `description_html`, `priority` (Optionen `{value,label}`), `state_id` (Optionen `{id,name,group}` immer), `assignee_ids`, `label_ids` (Optionen nur mit `?include=members,labels`), `start_date`, `target_date`, `parent_id`, `estimate_point_id` (Optionen, wenn Estimates konfiguriert). Custom-Felder nur, wenn Feature ISSUE_TYPES aktiv **und** `type_id` gegeben oder Default-Typ existiert; Schlüssel z. B. `custom_field_severity` mit `{id,type,name,display_name,required,is_multi,options[{id,name}]}`.

**Pagination.** T1, P1, O1 liefern Arrays ohne Envelope; MCP-List mit `cursor`/`per_page`.

**CE-Stand.** `IssueType`, `ProjectIssueType` (`apps/api/plane/db/models/issue_type.py:14-55`), `Issue.type` (`apps/api/plane/db/models/issue.py:164`), `type_id` im Public-Serializer; Typen-Konstante `TIssuePropertyValues = Record<string, unknown>` (`packages/types/src/issues/issue-property-values.ts`); Filter-Backend-Bezug in `apps/api/plane/utils/filters/filter_backend.py`; Illustrationen `custom-properties.tsx`, `property.tsx`. Keine Property-Modelle, keine Endpunkte, keine Settings-UI. Extension-Points im Work-Item-Modal (Verifikationslauf): `TPropertyValuesValidationProps`, `TActiveAdditionalPropertiesProps`, `TCreateUpdatePropertyValuesProps` und die Kontext-Funktionen `getActiveAdditionalPropertiesLength`, `handlePropertyValuesValidation`, `handleCreateUpdatePropertyValues` (`apps/web/components/issues/issue-modal/context/issue-modal-context.tsx:14-74`), im CE-Provider mit leeren Werten (`apps/web/components/issues/issue-modal/provider.tsx:43`).

**Migrationshinweis.** Generische Custom-Property-Engine (EAV mit typisierten Spalten oder `jsonb` + Generated Columns) für Work Items **und** Customers; Formel-Auswertung serverseitig (Parser für `{Field}`-Syntax, Zyklus-Erkennung); Indexierung für PQL `cf["<id>"]` (`DD/dev-tools/mcp-server-tools.md:212`).

**Konfidenz:** hoch (Felder, Typen), mittel (Formula, Workspace-Governance, Roll-ups).

### 4.8 F12 – IdP Group Sync

**Funktionsbeschreibung.** Workspace-Admins verknüpfen IdP-Gruppen mit Workspace-Rollen und Projekten/-rollen; Mitgliedschaften werden beim Login (und optional offline) provisioniert (`AR/idp-group-sync/overview.md`). Nur Self-hosted Commercial, nur **OIDC** (Gruppen-Claim im Token erforderlich), SAML/LDAP „coming soon“; Settings unter Workspace Settings → Group syncing (WEB: https://docs.plane.so/authentication/group-sync). UI-Texte vollständig im CE-i18n (`packages/i18n/src/locales/en/workspace-settings.json:192-256`): Enable-Toggle „Enable group syncing“; Config „Sync on login“ (Default an), „Offline sync – Runs sync every six hours automatically …“ (Default aus), „Auto remove – Automatically remove users from projects when they no longer match the group.“ (Default aus), „Group attribute key“ (Placeholder „Groups“); „Group mapping“ mit Button „Add new group sync“; Modal-Felder „User group“, „Project“, „Project role“; Lösch-Modal „Delete group sync – New users from this identity group will no longer be added to the project. Users already added will keep their current role.“; Leerzustand „No group mappings yet“ (`empty-state.json:252-254`).

**Datenmodell**

| Objekt | Feld | Typ | Bemerkung |
|---|---|---|---|
| Config | `id` | uuid | 1:1 je Workspace, **auto-create** bei erstem GET |
| | `is_enabled` | bool | |
| | `sync_on_login` | bool | |
| | `auto_remove` | bool | entfernt Nutzer aus Projekten/Workspace bei Gruppenaustritt |
| | `sync_offline` | bool | 6-Stunden-Job |
| | `group_attribute_key` | string | Claim-Name, z. B. `groups` |
| | `default_workspace_role` | string | Rollen-**Slug**, z. B. `member` |
| | `created_at`,`updated_at` | datetime | |
| Workspace-Mapping | `id` | uuid | |
| | `idp_group_name` | string | Pflicht |
| | `role` | string | Workspace-Rollen-Slug (`member`, `admin`) |
| | `created_at`,`updated_at` | datetime | |
| Projekt-Mapping | `id` | uuid | |
| | `idp_group_name` | string | Pflicht |
| | `project` | string/null | **Projekt-Identifier** (z. B. `ENG`), nicht UUID; `null` bei `all_projects` |
| | `all_projects` | bool | XOR mit `project` |
| | `role` | string | Projekt-Rollen-Slug (`member`, `admin`, `guest`) |
| | `created_at`,`updated_at` | datetime | |

**Berechtigungen.** Alle Endpunkte Workspace-Admin (`AR/idp-group-sync/overview.md`); Scopes `workspaces.group_sync:read/write` (nicht in Q2, D18; in v2 gelistet, `V2/authentication.md`). v2 bildet G1–G12 1:1 ab (`V2/group-sync/*`, 12 Endpunkte).

**Tier und CE-Stand (Verifikationslauf).** Enterprise Grid: Die Doku-Seite trägt das Tag „Enterprise Grid“ (WEB: https://docs.plane.so/authentication/group-sync); übereinstimmend Dok. 20 PF-98 (Whitepaper) und Dok. 27 P08-05. CE: keine Verwendung der 33 i18n-Schlüssel `workspace_settings.settings.group_syncing.*` außerhalb von `packages/i18n/src/locales/` (`grep -rn "group_sync" apps packages`, nur Locale-Treffer), dazu nur die Illustration `packages/blocks/src/empty-state/assets/horizontal-stack/group-syncing.tsx` → CE-Status „fehlt“ (vorher „Stub/UI-Hülle“).

**Migrationshinweis.** OIDC-Login-Hook (Claim lesen → Mappings anwenden), Hangfire/Quartz-Job alle 6 h für Offline-Sync (benötigt IdP-Gruppenabfrage – bei reinem OIDC nur über Token/Userinfo möglich; offen), Rollen-Slugs → Mapping auf Ziel-Rollenmodell (F26).

**Konfidenz:** hoch (API/UI-Texte), mittel (Offline-Sync-Mechanik).

### 4.9 F13 – Work-Item ↔ Page-Links

**Funktionsbeschreibung.** Verknüpft Wiki-/Projektseiten mit Work Items, sodass Dokumentation „nahe an der Ausführung“ bleibt; eigener Abschnitt in den Work-Item-Details („Link pages in work items in a separate section“, `plans.tsx:842-851`; `AR/work-item-pages/overview.md`).

**Datenmodell Link-Objekt:** `id` uuid; `page` `{id, name, description_html, created_at, updated_at, created_by, is_global, logo_props}` (Lite-Serializer); `issue`, `project`, `workspace` uuid; `created_at`, `updated_at`, `created_by`. `is_global=true` kennzeichnet Wiki-Seiten (CE-Feld `apps/api/plane/db/models/page.py:51`).

**API.** WP1–WP4; Pagination WP1 Cursor + `order_by`; Pfad-ID beim Löschen widersprüchlich (D11).

**Konfidenz:** hoch.

### 4.10 F14/F15 – Pages-Public-API und Wiki

**Funktionsbeschreibung.** Seiten auf Workspace- (Wiki, projektunabhängig) und Projektebene (`AR/page/overview.md`). Listenfilter `type`: `all` (alle zugänglichen), `public` (öffentlich, ohne archivierte), `private` (eigene, nicht geteilte, ohne archivierte), `shared` (explizit mit mir geteilte private Seiten), `archived` (`AR/page/list-project-pages.md`). Listeneinträge enthalten `parent_id` (verschachtelte Seiten). EE-Wiki kennt „Wiki collections“ (vordefiniert General/Private/Shared/Archived, eigene Collections, Seiten hinzufügen/entfernen, Löschen mit Transfer) – UI-Texte in `packages/i18n/src/locales/en/wiki.json`. Seiten-Suche über Wiki-Collections, Projekte und Teamspaces (`packages/i18n/src/locales/en/page.json:85-91`).

**Datenmodell (Create-Body/Response):** `id`, `name` (Pflicht), `description_html` (Pflicht), `owned_by` uuid, `access` (0 Public, 1 Private), `color`, `is_locked`, `archived_at` (date), `view_props` object, `logo_props` object, `external_id`, `external_source`, `workspace`, `parent_id`, Audit. Der Stand `AR/` (master) bietet **kein** Update/Delete/Archive/Lock. **Korrektur (Verifikationslauf):** Der Branch `docs-page-update-api` dokumentiert `PUT`, `DELETE`, `POST …/archive/`, `DELETE …/archive/` (Restore) für Projekt- und Wiki-Seiten, Page-Attachments und Wiki-Collections (Kap. 10, F33); v2 bietet `GET/POST/PATCH/DELETE` für `…/pages/` und `…/projects/{pid}/pages/` (Kap. 9). Lock bleibt in allen Varianten ohne Public-Endpunkt.

**Tier (Verifikationslauf).** Wiki Pro (Upsell-Text `packages/i18n/src/locales/en/wiki.json:89-91` „… with Plane Pro“, `PRO_PLAN_FEATURES` „Wikis“, Dok. 26 P07-01); geteilte private Seiten Business (Dok. 26 P07-16, Doku-Zitat „On the Business plan and above, you can selectively share private Wiki pages“), CE-Flag `isPageSharingEnabled: false` (`apps/web/hooks/use-page-flag.ts:12-22`).

**CE-Stand.** `Page` mit `is_global`, `parent`, `access`, `moved_to_page/project`, `sort_order` (`apps/api/plane/db/models/page.py:23-80`), `ProjectPage` (`…:135-155`), interne Projektseiten-API inkl. archive/lock/access/description/versions/duplicate (`apps/api/plane/app/urls/page.py`); globale Seiten nur in der Suche referenziert (`apps/api/plane/app/views/search/base.py:757`). Keine Public-API, keine Wiki-UI.

**Konfidenz:** hoch (API), mittel (Collections/Sharing-Semantik).

### 4.11 F16/F17 – Feature-Toggles (Projekt und Workspace)

**Projekt-Features (`AR/project-features/*`)** – Objekt `{epics, modules, cycles, views, pages, intakes, work_item_types}` (alle bool); MCP `update_features` zusätzlich `parallel_cycles`, `project_updates`, `workflows` und benennt `workitem_types` (`DD/dev-tools/mcp-server-tools.md:377`). i18n ergänzt `time_tracking`, `milestones`, Intake-Unteroptionen (Forms, Assignees) (`packages/i18n/src/locales/en/project-settings.json:325-426`). Mapping auf CE-Felder: `modules`↔`module_view`, `cycles`↔`cycle_view`, `views`↔`issue_views_view`, `pages`↔`page_view`, `intakes`↔`intake_view`, `work_item_types`↔`is_issue_type_enabled` (`apps/api/plane/db/models/project.py:95-101`); `epics`, `parallel_cycles`, `project_updates`, `workflows`, `milestones` ohne CE-Pendant.

**Workspace-Features (`AR/workspace-features/*`)** – `{project_grouping, initiatives, teams, customers, wiki, pi}` (alle bool).

**v2-Feature-Objekte (Verifikationslauf, `V2/workspace-features/overview.md`, `V2/project-features/overview.md`).** Workspace: `id`, `is_work_item_types_enabled` (Modus-Diskriminator, F43), `work_item_type_default_level` (integer, ohne Enum), `is_workitem_hierarchy_enabled` („Whether work items can be nested into a parent and child hierarchy“), `is_project_grouping_enabled`, `is_teams_enabled`, `is_wiki_enabled`, `is_initiative_enabled`, `is_customer_enabled`, `is_release_enabled`, `is_state_duration_enabled` („Whether Plane records how long work items spend in each state“ – Time-in-State, Business laut Dok. 25 F06), `is_pi_enabled`, `created_at`. Projekt: `is_automated_cycle_enabled`, `is_epic_enabled`, `is_manually_start_end_cycles_enabled`, `is_milestone_enabled`, `is_parallel_cycles_enabled`, `is_project_updates_enabled`, `is_workflow_enabled` (Beispielwerte alle `false`). Gegenüber v1 neu: `work_item_type_default_level`, `is_workitem_hierarchy_enabled`, `is_release_enabled`, `is_state_duration_enabled`, `is_automated_cycle_enabled`, `is_manually_start_end_cycles_enabled`, `is_milestone_enabled`; `time_tracking` fehlt auch in v2 (O8). „A flag being `true` is necessary, not sufficient. Features also have to be available on the workspace's plan.“ (Dok. 26 G15) → nach ADR-001 nur das Flag.

**Migrationshinweis.** ADR-001: Toggles bleiben als fachliche Einstellungen erhalten; Tabelle `project_features`/`workspace_features` oder Spalten; Default nach Original (unbekannt → Kap. 8).

**Konfidenz:** hoch.

### 4.12 F18 – Project Grouping (Projekt-States, Projekt-Labels)

**Funktionsbeschreibung.** Workspace-Settings → „Projects“ mit Tabs „Project states“ und „Project labels“ („Manage project states, and enable project labels, and other configuration.“); Projekt-States: „Project States is a Plane-only feature for tracking progress of all your projects by any project property.“ (`packages/i18n/src/locales/en/workspace-settings.json:258-271`). Default-Projekt-States Draft, Planning, Execution, Monitoring, Completed, Cancelled, erweiterbar (WEB: https://university.plane.so/courses/201-the-growth/11-intro-to-project-states.html). Workspace-Feature `project_grouping`.

**Datenmodell Projekt-Label (`AR/project-labels/overview.md`)**: `id`, `name` (Pflicht), `description`, `color` (Hex), `sort_order` (number, Default-Beispiel 65535), `workspace`, `created_at`, `updated_at`, `created_by`, `updated_by`. Projekt-States: **keine** API in `AR/` (nur UI-Belege).

**Hinweis.** Gleicher Scope `projects.labels:*` wie Work-Item-Labels. Laut Doku: Projekt-Labels sind Workspace-Tags, ein Projekt kann mehrere tragen; Anlage unter Workspace Settings → Projects → Tab „Project labels“ mit Name und Farbe oder direkt im Label-Picker; in Board/List lassen sich Projekte nach Label gruppieren, ohne Label in der Gruppe „No Label“ (WEB: https://docs.plane.so/core-concepts/projects/project-labels, Such-Zusammenfassung). Tier der Projekt-Labels nicht belegt (Kap. 3). Keine v2-Ressource für Projekt-Labels im Branch `V2/`.

**CE-Stand (Verifikationslauf).** Nur i18n-Texte; keine Store-, Service- oder Komponenten-Spur → „fehlt“ (vorher „Stub/UI-Hülle“).

**Konfidenz:** hoch (Labels), mittel (States).

### 4.13 F19 – Project Templates

**Funktionsbeschreibung.** Projekt aus Template erzeugen; kopiert States, Labels, Estimates, Module und Work Items; Body-Felder überschreiben Template-Defaults; Lead wird Projekt-Admin; Template muss zum gleichen Workspace gehören (`AR/project/create-project-with-template.md`). Templates enthalten Projekt-Eigenschaften (Sichtbarkeit, Leads, Daten), States/Labels, aktivierte Features und Work-Item-Typen (WEB: https://plane.so/changelog/cloud-april-28-2025). UI-Texte `packages/i18n/src/locales/en/template.json` (`new_project_template`, `new_work_item_template`, `new_page_template`, `use_template`, …) und Leerzustand „No templates yet“ (`empty-state.json`).

**API.** PR8: Body `template_id`* (uuid), `name`, `identifier`, `description`, `network` (0 secret, 2 public), `project_lead` → 201 Projekt-Lite; Projekt-Objekt trägt `template_id` (`AR/project/overview.md`). Template-CRUD selbst ist **nicht** in `AR/` dokumentiert.

**Konfidenz:** hoch (Use-Endpunkt), niedrig (Template-Verwaltung).

### 4.14 F20 – Advanced Search

**Funktionsbeschreibung.** Volltext mit Fuzzy-Matching, Autocomplete, Multi-Entity über Work Items, Projekte, Cycles, Module, Pages; Zugang über Cmd/Ctrl+K (`DD/self-hosting/govern/advanced-search.md`). Backend OpenSearch ≥ 2.19 (`OPENSEARCH_ENABLED`, `OPENSEARCH_URL`, `OPENSEARCH_USERNAME`, `OPENSEARCH_PASSWORD`, `OPENSEARCH_INDEX_PREFIX`; Index-Rebuild `manage_search_index`).

**API W8.** Body `query` (string), `filters` (object, an IssueFilterSet), `limit` (int), `workspace_search` (bool), `project_id` (uuid) → Liste `{id, name, sequence_id, project_identifier, project_id, workspace_id, type_id, state_id, priority, target_date, start_date}`.

**Migrationshinweis (ADR-004).** Kein OpenSearch-Zwang: PostgreSQL-FTS (`tsvector`, `websearch_to_tsquery`) + `pg_trgm` für Fuzzy/Autocomplete; optional pgvector für semantische Suche.

**Konfidenz:** hoch.

### 4.15 F21 – Zeitbasierte Estimates

Estimate-Typ `time` (Template „Hours“ 1–6) ist im CE nur als Konstante mit `is_ee: true` vorhanden (`packages/constants/src/estimates.ts:121-141`), das CE-Modell kennt nur `categories`/`points` (`apps/api/plane/db/models/estimate.py:13-15`). Die API (ES2) akzeptiert `time`. Zusätzlich gilt: Estimate-Public-API im CE vorhanden, aber nicht geroutet (Kap. 2.5). Werte: `value` max. 20 Zeichen (`MAX_ESTIMATE_POINT_INPUT_LENGTH`, `packages/constants/src/estimates.ts:10`), 2–6 Punkte (`estimateCount`, `…:24-27`). **Konfidenz:** hoch.

### 4.16 F22 – Custom Relation Definitions

MCP `workitem_relation` kennt neben den eingebauten Abhängigkeiten (`blocking`, `blocked_by`, `start_before`, `start_after`, `finish_before`, `finish_after`) **eigene Relationsdefinitionen**: `list_definitions(is_default, is_active)`, `create_definition(name*, outward, inward, is_active, color)`, `update_definition`, `delete_definition`; Relation-Create mit `relation_definition_id` + `relation_definition_label` (Richtung über outward/inward-Label); Delete mit `is_dependency` (Dependencies und Custom-Relationen sind unabhängig) (`DD/dev-tools/mcp-server-tools.md:142-156`). Workspace-Settings „Relations – Create and manage relation types that connect work items across your workspace.“ (`packages/i18n/src/locales/en/workspace-settings.json:277-281`). CE-Modell kennt zusätzlich `implemented_by`/`implements` (`apps/api/plane/db/models/issue.py:272-293`), das die Public-API nicht anbietet. **Verifikationslauf:** Tier Enterprise Grid (Doku-Seite https://docs.plane.so/work-items/custom-relations mit Label „Enterprise Grid“; Workspace-Ebene; Workspace Settings → Relations → „Add relation“ mit Titel und Inward-Name; Anzeige auf beiden Work Items mit Inward- bzw. Outward-Label). v2 dokumentiert die REST-Ressource `…/workspaces/{slug}/work-item-relation-definitions/` (GET/POST, GET/PATCH/DELETE `{pk}`; Felder `id`, `name`, `outward`, `inward`, `color`, `description`, `is_active`, `is_default` – Setzen entfernt das Flag am bisherigen Default –, `logo_props`, `sort_order`, `external_id`, `external_source`, `created_at`, `created_by_id`; Scope `workspaces.work_item_relation_definitions:read|write`; `V2/work-item-relation-definitions/overview.md`) sowie getrennte Dependency-Endpunkte `…/work-items/{id}/dependencies/` (F39) und Relations-`DELETE …/relations/{related_work_item_id}/` statt `relations/remove/`. Ein Forum-Bericht meldet 404 dieser Endpunkte auf der CE (WEB: https://forum.plane.so/t/work-item-relation-tools-list-work-item-relation-definitions-list-work-item-relations-return-404-via-mcp-server-on-self-hosted-ce/274). **Konfidenz:** mittel (Semantik), hoch (Endpunkte).

### 4.17 F23 – Workspace-Mitglied entfernen (M7)

POST `members/remove/` entfernt das Mitglied, deaktiviert es in allen Projekten und reduziert die Seat-Anzahl (`AR/members/remove-workspace-member.md`); Body in v1 undokumentiert, laut v2-Pendant `email`* (string, E-Mail) und `remove_seat` (bool, optional), Antwort ohne Body (`V2/members/remove-workspace-member.md`). Seat-Logik entfällt (ADR-001); `remove_seat` wird akzeptiert und ignoriert. **CE-Stand:** Die interne App-API enthält dieselbe Fachlogik (`DELETE /api/workspaces/{slug}/members/{pk}/`, `apps/api/plane/app/views/workspace/member.py:138-176`): Fehler 400 bei Selbstentfernung („You cannot remove yourself from the workspace. Please use leave workspace“), bei höherer Rolle des Ziels („You cannot remove a user having role higher than you“) und wenn das Ziel alleiniger Admin eines Projekts ist; danach `ProjectMember.is_active=False` für alle Projekte und `WorkspaceMember.is_active=False` → 204. **Konfidenz:** hoch (Body aus v2), hoch (CE-Logik).

### 4.18 F24 – Releases (nur MCP-Doku)

Workspace-Releases mit `name`*, `description_html`, `status` (`unreleased` Default, `released`, `cancelled`), `release_date` (UI „Target date“), `target_date` (separat gespeichert, in UI nicht sichtbar), `tag_id`, `lead_id`, `is_prerelease`, `external_*`; Changelog (Rich-Text, wird leer mit dem Release angelegt; `get_changelog`/`update_changelog` mit `description_html`/`description_stripped`); Work-Item-Zuordnung (`add_ids`/`remove_ids`); Release-Tags (`version`*, `description`, `commit_hash`, `git_tag`); Release-Labels (Workspace-Palette `name`*, `color`, `sort_order`; `attach`/`detach`) (`DD/dev-tools/mcp-server-tools.md:307-356`). Property-Typen „Release picker“ und „Formula“ (WEB: https://plane.so/blog/introducing-releases). Gruppierungsschlüssel `release_work_items__release_id` (`…:91`). Nicht in `AR/`. **Verifikationslauf:** Tier Business (Doku-Seiten „Releases“ und „Project Releases“ mit Label „Business“; Dok. 23 WP-08). Laut Doku: Aktivierung unter Workspace Settings → Releases → „Enable Releases“; danach sehen Mitglieder Releases in der Sidebar, Owner und Admins dürfen anlegen, bearbeiten, löschen; Deaktivieren blendet nur aus und behält die Daten. Zusätzlich gibt es **Projekt-Releases**, die pro Projekt unter Project settings → Features eingeschaltet werden und auf die Work Items eines Projekts beschränkt sind (WEB: https://docs.plane.so/releases, https://docs.plane.so/projects/project-releases, Such-Zusammenfassung; API-seitig nicht belegt). v2 dokumentiert die REST-Ressourcen `releases/` (CRUD, `…/{pk}/changelog/` GET/PATCH, `…/{pk}/labels/` und `…/{pk}/work-items/` mit `{add, remove}`), `releases/tags/`, `releases/labels/`, `releases/{release_id}/links/`, `releases/{release_id}/comments/` (je CRUD) mit Scopes `releases:*`, `releases.tags:*`, `releases.labels:*`, `releases.links:*`, `releases.comments:*` (Kap. 9.4). Release-Links und Release-Kommentare waren aus der MCP-Doku nicht bekannt. **Konfidenz:** hoch (Endpunkte), mittel (Projekt-Releases).

### 4.19 F25/F26/F27/F28/F29/F30/F31 – weitere aus der API ableitbare Bezahl-Merkmale

| Feature | Belegte Fakten | Quelle | Konfidenz |
|---|---|---|---|
| F25 PQL | `pql`-Filter in Work-Item-, Cycle-, Modul-Listen; UUID-basierte Felder project, assignee, state, label, cycle, module, type, milestone, creator; Funktionen `currentUser()`, `openStates()`, `isOverdue()`, `childOf("PROJ-12")`, `cf["<property id>"]`; `state__group` als Filter verboten. CE-Public-API: `GET …/work-items/?pql=…` bzw. `?filters=…` → 400 mit Schlüsseln `pql` (Text „PQL and structured filters are not supported on this Plane edition. Remove the pql/filters parameter and filter results client-side, or use a Plane edition that supports work item query filtering.“) und `unsupported_parameters` | `DD/dev-tools/mcp-server-tools.md:44-48,91,254`; `apps/api/plane/api/views/issue.py:324-335` | mittel (Sprache), hoch (CE-Stub) |
| F26 Rollen-Slugs | Namespace `workspace` (Owner/Admin/Member/Guest) und `project` (Admin/Contributor/Commenter/Guest); Slug stabil, aber nur mit Namespace eindeutig; Member-Filter `role_slug`, `is_active`, `is_bot` | `DD/dev-tools/mcp-server-tools.md:409-421` | mittel |
| F27 Updates | `EUpdateStatus` `OFF-TRACK`,`ON-TRACK`,`AT-RISK`; UI „Add update“, Reaktionen, Fortschritt „since last update“ | `packages/types/src/enums.ts:87-91`; `packages/i18n/src/locales/en/update.json` | mittel |
| F28 Intake-E-Mail | `source_email` an Intake-Issue; DNS-Konfiguration „Intake Email“ (Business) | `AR/intake-issue/update-intake-issue-detail.md`; `apps/api/plane/db/models/intake.py:77`; `DD/self-hosting/govern/configure-dns-email-service.md` | hoch |
| F29 PI | Workspace-Feature `pi`; Dienste `pi-api`, `pi-worker`, `pi-beat`, `pi-migrator` | `AR/workspace-features/overview.md`; `HC/plane-enterprise/templates/workloads/` | niedrig |
| F30 Agent Runs | Scopes `agents.runs:read/write`, `agents.run_activities:read/write` | `DD/dev-tools/build-plane-app/oauth-scopes.md` | niedrig |
| F31 OAuth-Apps | Bearer-Token, Scope-Liste Kap. 6 | `AR/introduction.md`; Q2 | hoch |

---

## 5. Abweichungen an CE-Ressourcen (EE-Erweiterungen in „gemeinsamen“ Endpunkten)

| Ressource | Commercial-Doku | CE-Stand | Quelle |
|---|---|---|---|
| Work Item | `type_id`/`type`, `expand=type,module`, `last_activity_at`, MCP: `archive`/`list_archived`, `count` mit `group_by`/`sub_group_by` (state_id, state__group, priority, project_id, type_id, labels__id, assignees__id, issue_module__module_id, release_work_items__release_id, cycle_id, milestone_id, created_by, target_date, start_date), `manage_assignee`/`manage_label` (merge, Removals zuerst) | `type_id` vorhanden; kein Archiv/Count in Public-API | `AR/issue/*`; `DD/dev-tools/mcp-server-tools.md:72-91`; `apps/api/plane/api/serializers/issue.py` |
| Work-Item-Liste | Filter `pql` (MCP) und strukturierte `filters` | CE antwortet mit 400 und Hinweis auf eine andere Edition (Stub) | `DD/dev-tools/mcp-server-tools.md:44-48`; `apps/api/plane/api/views/issue.py:324-335` |
| Kommentare | `parent` (Threads), `access` INTERNAL/EXTERNAL | Modell hat `parent` und `access` | `AR/issue-comment/*`; `apps/api/plane/db/models/issue.py:451-480` |
| States | Gruppe `triage`, `is_triage` | vorhanden (Triage-States vom Default-Manager ausgeblendet) | `apps/api/plane/db/models/state.py:14-90` |
| Projekte | `is_issue_type_enabled`, `is_time_tracking_enabled`, `guest_view_all_features`, `timezone`, `template_id` | erste vier vorhanden, `template_id` fehlt | `apps/api/plane/db/models/project.py:95-119` |
| Intake | `source_email` | Feld vorhanden, keine E-Mail-Annahme | `apps/api/plane/db/models/intake.py:77` |
| Relationen | Response als UUID-Listen, `type_id`/`is_epic`, Remove-Endpunkt | Objekt-Paare, kein Remove | Kap. 2.11 |
| Estimates | `time`, Public-API, MCP `link` (aktives Estimate setzen) | Modell ohne `time`, API nicht geroutet | Kap. 2.5; `DD/dev-tools/mcp-server-tools.md:214-230` |
| Cycles | MCP `complete` (end_date = heute), `archive` beendet laufende Cycles zuerst | CE: Archiv nur beendeter Cycles | `DD/dev-tools/mcp-server-tools.md:250-251`; `AR/cycle/archive-cycle.md` |
| Members | `members/remove/` | fehlt | Kap. 2.13 |
| Attachments | MCP `upload_from_url` (serverseitiger Abruf, keine privaten Adressen), `read` (Bilder ≤ 5 MB, Text ≤ 1 MB) | fehlt | `DD/dev-tools/mcp-server-tools.md:116-128` |

---

## 6. OAuth-Scope-Inventar (vollständig, Q2 + in Q1 zusätzlich verwendete)

| Gruppe | Scopes | Quelle |
|---|---|---|
| Project | `projects:read/write`, `projects.features:*`, `projects.members:*`, `projects.states:*`, `projects.labels:*`, `projects.intakes:*`, `projects.epics:*`, `projects.cycles:*`, `projects.pages:*`, `projects.modules:*`, `projects.work_items:*`, `projects.work_items.comments:*`, `projects.work_items.attachments:*`, `projects.work_items.links:*`, `projects.work_items.relations:*`, `projects.work_items.activities:*`, `projects.work_items.worklogs:*`, `projects.work_item_types:*`, `projects.work_item_properties:*`, `projects.work_item_property_options:*`, `projects.work_item_property_values:*`, `projects.milestones:*` (jeweils `:read` und `:write`) | `DD/dev-tools/build-plane-app/oauth-scopes.md` |
| Wiki | `wiki.pages:read/write` | dto. |
| Customer | `customers:*`, `customers.requests:*`, `customers.properties:*`, `customers.property_values:*`, `customers.work_items:*` | dto. |
| Initiatives | `initiatives:*`, `initiatives.projects:*`, `initiatives.epics:*`, `initiatives.labels:*` | dto. |
| Workspace | `workspaces.members:*`, `workspaces.features:*` | dto. |
| Stickies | `stickies:*` | dto. |
| Teamspaces | `teamspaces:*`, `teamspaces.projects:*`, `teamspaces.members:*` | dto. |
| Profile | `profile:read` | dto. |
| Assets | `assets:read/write` | dto. |
| Agent Run | `agents.runs:*`, `agents.run_activities:*` | dto. |
| nur in Q1 | `projects.estimates:read/write`, `workspaces.group_sync:read/write`, `write` (Template-Use) | `AR/estimate/*`, `AR/idp-group-sync/*`, `AR/project/create-project-with-template.md` |
| v2: globale Stufe | `read` (Lesen aller Ressourcen), `write` (Schreiben aller Ressourcen); eine Operation ist erfüllt durch globalen **oder** feingranularen Scope (OR-Logik); `GET /api/v2/users/me/` braucht bei OAuth den globalen `read`-Scope; API-Keys sind nicht scope-begrenzt, aber an die Rechte des Besitzers gebunden | `V2/authentication.md` („The scope model“, „Who am I“, Warnbox „API keys are not scope-limited“) |
| v2: feingranular, gegenüber Q2 **neu** | `automations:read/write`, `projects.views:read/write`, `projects.workflows:read/write`, `releases:read/write`, `releases.comments:read/write`, `releases.labels:read/write`, `releases.links:read/write`, `releases.tags:read/write`, `templates.work_items:read/write`, `webhooks:read/write`, `workspaces.artifacts:read/write`, `workspaces.audit_logs:read`, `workspaces.roles:read`, `workspaces.views:read/write`, `workspaces.work_item_properties:read/write`, `workspaces.work_item_relation_definitions:read/write`, `workspaces.work_item_types:read/write`, `projects.estimates:read/write`, `workspaces.group_sync:read/write` | `V2/authentication.md` (Tabelle „Fine-grained scopes for live endpoints“, 97 Einträge) |
| v2: in Q2, aber **nicht** in der v2-Tabelle | `projects.epics:*`, `projects.work_item_property_options:*`, `projects.work_item_property_values:*`, `initiatives.projects:*`, `initiatives.epics:*`, `customers.work_items:*`, `teamspaces.projects:*`, `teamspaces.members:*`, `agents.runs:*`, `agents.run_activities:*`, `profile:read` (v2 regelt Optionen über `projects.work_item_properties:*`, Customer-/Initiative-Verknüpfungen über `customers:write`/`initiatives:write`, `users/me` über globales `read`) | Abgleich Q2 ↔ `V2/authentication.md` und Scope-Zeilen der Endpunktseiten (Kap. 9.4) |
| v2: Token-Klassen für Rate-Limits | API-Keys, OAuth-Tokens, Workspace-Tokens, Service-Tokens, External-Tokens (je eigener Bucket; `429 rate_limited` mit `Retry-After`) | `V2/errors.md` („Rate limiting“) |

---

## 7. Querschnittliche Migrationshinweise (.NET Aspire / EF Core / PostgreSQL / Angular)

| Thema | Empfehlung | Begründung/Quelle |
|---|---|---|
| Public-API-Vertrag | `snake_case`-JSON, Pfade/Statuscodes 1:1, Pagination-Envelope aus Kap. 1.2 | ADR-003-Konsequenz |
| Public-API v2 | zweite Endpunktgruppe `/api/v2` mit `ProblemDetails` (Erweiterungen `code`, `errors[]`, ohne `status`/`title` im Body), PATCH-only, Offset-/Cursor-Pagination, `?fields=`/`?expand=` nach Allowlist, Upsert mit Header `X-Plane-Upsert`, Bulk mit Savepoint je Zeile; Umfang nach Entscheidung O16 | Kap. 9; `V2/*.md` |
| OAuth-Scopes | Policy je Scope (Kap. 6), API-Key = Vollzugriff des Nutzers | `AR/introduction.md` |
| Custom Properties | eine generische Engine für Work Items und Customers | F04/F09 |
| Suche | Postgres-FTS + `pg_trgm` (+ pgvector) statt OpenSearch | ADR-004, F20 |
| Epics | WorkItemType-Flag statt Tabelle | F01 |
| Seats/Billing | `members/remove` ohne Seat-Logik; keine Plan-Gates; Feature-Toggles bleiben | ADR-001 |
| Group Sync | OIDC-Claim-Auswertung im Login, periodischer Job | F12, ADR-004 |
| UI | i18n-Texte aus `packages/i18n/src/locales/*/` (EE-Dateien `work-item-type.json`, `wiki.json`, `template.json`, `workflow.json`, `update.json`, `automation.json`, `integration.json` und EE-Schlüssel in `workspace-settings.json`, `project-settings.json`, `empty-state.json`) und Illustrationen aus `packages/blocks/src/empty-state/assets/` übernehmen; Upsell-Schlüssel (`empty_state.get_pro`, `empty_state.upgrade`) entfallen | ADR-001, ADR-005 |

---

## 8. Offene Punkte / Unklarheiten

| # | Thema | Offene Frage | Vorschlag |
|---|---|---|---|
| O1 | Plan-Tier PI, Agent Runs, OAuth-Apps, Projekt-Labels, Artifacts, API v2 | Kein offizieller, abrufbarer Beleg. **Im Verifikationslauf geklärt:** Milestones Pro, IdP Group Sync Enterprise Grid, Custom Relations Enterprise Grid, Releases Business, Shared Pages Business, Formula Pro (mittel) – Kap. 3 | für Migration irrelevant (ADR-001); nur dokumentarisch nachpflegen |
| O2 | Initiatives Tier | Plan-Tabelle und University-Kurs 05 Pro vs. eine andere University-Seite Business (Dok. 23 WP-13) | Pro (Matrix + Kurs 05) |
| O3 | Body der DELETE-Massenendpunkte (I13, I16, I19, TS8, TS11) | in v1 undokumentiert; v2 löst Verknüpfungen einheitlich über `POST …/{pk}/labels/`, `…/{pk}/projects/` bzw. `…/{pk}/work-items/` mit `{add: [uuid], remove: [uuid]}` (Initiativen, Customers, Releases, Cycles, Module, Milestones) bzw. über `member_ids`/`project_ids` im Teamspace-`PATCH` (`V2/teamspaces/update-teamspace.md`) | v1: Arrays `label_ids`/`project_ids`/`epic_ids`/`member_ids` im JSON-Body (MCP-Analogie); v2-Muster `{add, remove}` zusätzlich anbieten |
| O4 | Body `members/remove/` | **geklärt** durch v2: `email`* + `remove_seat` (`V2/members/remove-workspace-member.md`) | `email` Pflicht; `remove_seat` akzeptieren und ignorieren (ADR-001) |
| O5 | Customer-Request-, Property-Value-, Customer-Work-Item-Response-Schemas | Platzhalter in Doku (D1, D2) | aus Request-Feldern + Audit ableiten; UI-Analyse (anderer Cluster) prüfen |
| O6 | Milestone ↔ Work Item Kardinalität | `{id, issue, milestone}` lässt n:m zu; PQL/Gruppierung `milestone_id` deutet auf 1 Milestone je Work Item | 1:n (ein Milestone je Work Item) mit Link-Tabelle und Unique(issue) |
| O7 | Milestone-REST-Zuordnung | **geklärt** durch v2: `POST …/milestones/{pk}/work-items/` mit `{add, remove}` (`V2/milestones/manage-milestone-work-items.md`) | v2-Vertrag übernehmen; v1 zusätzlich `GET …/milestones/{id}/work-items/` (MS6) |
| O8 | Projekt-Feature-Flag `milestones`, `time_tracking` | `milestones` in v2 vorhanden (`is_milestone_enabled`); `time_tracking` weder in v1 noch in v2 (`V2/project-features/overview.md`), CE-Feld `Project.is_time_tracking_enabled` existiert | `is_milestone_enabled` übernehmen; Time-Tracking über `is_time_tracking_enabled` am Projekt |
| O9 | Initiative-Liste paginiert? | D7 | paginiert (Envelope), `per_page` großzügig |
| O10 | Work-Item-Page-Delete per Page-ID oder Link-ID | D11 | beide akzeptieren |
| O11 | Workspace-Governance-Modus für Typen/Properties | wie aktiviert, welche Defaults | eigene Analyse UI-Cluster; Datenmodell: Typ/Property mit `project_id` nullable |
| O12 | Offline-Group-Sync ohne IdP-API | wie werden Gruppen ohne Login abgefragt? | optionaler OIDC-Provider-Adapter (Graph/Keycloak-Admin-API), sonst deaktiviert |
| O13 | Default-Werte der Feature-Toggles | unbekannt | CE-Defaults übernehmen (`module_view=False`, `cycle_view=False`, `page_view=True`, …, `apps/api/plane/db/models/project.py:95-102`); EE-Toggles Default `false` |
| O14 | Formel-Engine | Datentypen, Operatoren außer `+ - * / &`, Roll-ups | eigener Spike |
| O15 | Rollenmodell | CE Integer-Rollen vs. EE Slugs/RBAC; v2 liefert `role` als offenen Slug-String (als Built-ins genannt: `owner`, `member`, `contributor`; vollständige Built-in-Liste nicht dokumentiert; Custom Roles mit eigenem Slug), Rollen-Objekt mit `namespace`, `level`, `is_system`, `status`; Permission-Schemes mit `permissions[]` (`V2/members/overview.md`, `V2/roles/overview.md`, `V2/permission-schemes/overview.md`) | Architektur-Entscheidung nötig (ADR) – Slugs + Mapping auf 20/15/5 |
| O16 | Umfang der Ziel-Public-API | v1 (231 Endpunkte, `AR/`) und v2 (387 Endpunkte, Branch `V2/`) laufen beim Hersteller parallel („v1 remains available and supported … but it is in maintenance“, `V2/introduction.md`); v2 ist nicht auf `master` gemergt (Stand 01.09.2026) | **Rückfrage an den Auftraggeber:** v1 allein, v1 + v2 oder nur v2 nachbauen? Vorschlag: v1 vertragskompatibel (CE-Integrationen, MCP-Server) und v2 als zweite Minimal-API-Gruppe auf denselben Application-Services |
| O17 | `402 payment_required` in v2 | Steht auf fast jeder v2-Seite (D26); nach ADR-001 gibt es keine Pläne | 402 nur noch bei abgeschaltetem Feature-Flag, mit gleichem problem+json-Body; Alternative `403`/`404` widerspräche dem dokumentierten Vertrag (Dok. 26 verweist diese Entscheidung an dieses Dokument) |
| O18 | Öffentliche Verfügbarkeit von v2 | WebSearch fand keine v2-Seite (Verifikations-Protokoll V.2, Suche S1/S9); Dok. 26 nennt v2-URLs unter developers.plane.so aus früheren Such-Zusammenfassungen | Branch-Stand `b89c72c` als Spezifikationsbasis verwenden; vor Implementierung `GET /api/v2/schema/` einer lizenzierten Instanz abgleichen |
| O19 | Projekt-Releases | Doku nennt projektbezogene Releases (Project settings → Features), v2 kennt nur Workspace-Releases (`V2/releases/*`) und kein Projekt-Feature-Flag dafür | eigene Analyse im Cluster P04 (Dok. 23 WM-15) |

---

## 9. API v2 (Branch `docs/api-reference-v2`) – im Verifikationslauf ergänzt

### 9.1 Quelle und Status

| Punkt | Befund | Quelle |
|---|---|---|
| Fundort | Branch `docs/api-reference-v2` des Repos `makeplane/developer-docs`, Commit `b89c72c` vom 11.08.2026; der Offline-Stand `AR/` (Branch `master`, 01.09.2026) enthält v2 **nicht** | `V2/`; `git log` beider Klone |
| Selbstverständnis | „API v2 is the current, recommended REST interface to Plane … API v1 remains available and supported for existing integrations, but it is in maintenance — build new integrations on v2.“ v1 und v2 laufen parallel, Migration ressourcenweise möglich | `V2/introduction.md`; `V2/migrating-from-v1.md` |
| Weiterleitung | `docs/api-reference/index.md` des Branches leitet auf `/api-reference/v2/introduction` um; v1 liegt dort unter `/api-reference/v1/…` | `V2/../index.md` |
| Umfang | 387 distinkte Endpunkte in 67 Ressourcen-Ordnern; die Einleitung nennt veraltet 88 Operationen (D22) | Kap. 9.3/9.4 |
| CE | keine v2-Route (`apps/api/plane/urls.py:19-24`) → jeder v2-Endpunkt ist EE-only | Repo |
| Öffentlich abrufbar? | UNVERIFIZIERT (O18): eigene WebSearch ohne v2-Treffer; Dok. 26 nennt v2-URLs unter `developers.plane.so/api-reference/v2/…` aus früheren Such-Zusammenfassungen | Verifikations-Protokoll V.2 |
| Maschinenlesbares Schema | `GET /api/v2/schema/` („the authority for every field, enum, and scope“) | `V2/introduction.md` |

### 9.2 Querschnitts-Konventionen v2 (gelten für alle v2-Ressourcen)

| Thema | v2-Regel | Unterschied zu v1 | Quelle |
|---|---|---|---|
| Basis-Pfad | `/api/v2/…`, **jede** URL endet mit `/` | v1 `/api/v1/…` | `V2/introduction.md` |
| Auth | `X-Api-Key: <token>` (PAT, volle Rechte des Besitzers, nicht scope-begrenzt) oder `Authorization: Bearer <token>` (OAuth 2.0 Authorization-Code, `/auth/o/authorize/`, `/auth/o/token/`; Token „fail closed“ auf gewährte Scopes, Prüfung vor der Permission-Engine) | Header-Schreibweise (D27); sonst gleich | `V2/authentication.md` |
| Scopes | zwei Stufen, OR-verknüpft: global `read`/`write` oder feingranular `<resource>:read` bzw. `<resource>:write` | v1 kennt nur feingranulare Scopes (plus `write` bei Template-Use) | `V2/authentication.md`; Kap. 6 |
| Who am I | `GET /api/v2/users/me/` → `{id, email, display_name, principal_kind ∈ {oauth, api_key, other}, scopes[]}` | v1 `users/me/` liefert Profilfelder | `V2/authentication.md` |
| Verben | `POST` legt an, `PATCH` ändert partiell (weggelassen ≠ `null`), **kein `PUT`** (→ `405 method_not_allowed`), `DELETE` → `204`, Löschen ist soft | v1 erlaubt `PUT` und `PATCH` | `V2/introduction.md`; `V2/migrating-from-v1.md` §3 |
| Writes | Relationen nur über `*_id`/`*_ids` (`state_id`, `parent_id`, `lead_id`, `assignee_ids`, `label_ids`); fremde IDs → `400`; Audit-Felder (`created_at`, `created_by_id` …) read-only | v1 lässt `created_by`/`updated_by` im Body zu (z. B. TS2, WG2, ST2) | `V2/migrating-from-v1.md` §6 |
| Reads | sparse: To-one als `<name>_id`, To-many als `<name>_ids`; keine eingebetteten Objekte | v1 bettet Objekte ein | `V2/expanding-relations.md` |
| `?expand=` | **separate key**: `?expand=state` behält `state_id` und fügt `state` hinzu; Allowlist je Ressource: Work Items `state`, `type`, `parent`, `assignees`, `labels`, `cycle`, `modules`; Projects `project_lead`, `default_assignee`; Cycles `owned_by`; Modules `lead`, `members`; Initiatives `lead`; Teamspaces `lead`; Releases `lead`, `tag`; Estimates `points`; Comments und Work-Item-Activities `actor`; Worklogs `logged_by`; Projekt-/Workspace-Pages `owned_by`, `parent`; Collections `owned_by`; Projekt-/Workspace-Views `owned_by`; Workspace-/Projekt-/Collection-Members `member`; unbekannter Wert → `400` | v1 ersetzt die ID durch das Objekt | `V2/expanding-relations.md` (D28) |
| `?fields=` | unangeforderte Schlüssel werden **weggelassen** (nicht `null`), `id` immer enthalten, `all` = alle anforderbaren Felder; unbekannter Name → `400` mit Vorschlag; Listen lassen „deferred fields“ wie `description_html` standardmäßig weg | v1 ignoriert unbekannte Felder still | `V2/sparse-fields.md`; `V2/migrating-from-v1.md` §5 |
| Pagination | Envelope immer Objekt mit `data` und `pagination.style`; **Offset** (Default): `next`/`previous` als Integer-Offsets, `total_count` (entfällt bei `?count=false`), `per_page` Default 50/Max 200 (darüber wird gekappt), `offset` Max 10000; **Cursor** (`?paginate=cursor`): `next_cursor`, `has_more`, kein `total_count`, nur vorwärts, nur cursor-fähige `order_by` (Work Items: `created_at`, `updated_at`, `sequence_id`, `id`), sonst `400 ordering_not_cursor_eligible` | v1: `results`, Cursor-Strings `value:offset:is_prev`, `per_page` Default 100 (Kap. 1.2) | `V2/pagination.md` |
| Filter | Formen `<name>`, `<name>__in` (kommagetrennt), `<name>__isnull`, `<name>__gte`/`__lte` (inklusiv); Relationen über `*_id` (Work Items `state_id`, `assignee_id`, `label_id`, `parent_id`, `cycle_id`, `module_id`, `type_id`; Cycles `owned_by_id`; Modules `lead_id`; Labels `parent_id`; Members `member_id`); Identitätsfilter `?name=` (case-insensitiv, exakt), `?key=` (Projekte → `identifier`, Estimate-Points), `?url=` (Webhooks, Work-Item-Links); Freitext `?search=`; Filter wirken nur nach der Autorisierung | v1: wenige Query-Filter (`external_id`, `external_source`, `cycle_view`, `type` …) | `V2/filtering-and-ordering.md` |
| Pfad-IDs | nur IDs, Ausnahmen: Workspace-Slug, Projekt-Identifier (`…/projects/ENG/`), Work-Item-Kennung `PROJ-123` | v1: `project_id` nur UUID | `V2/introduction.md`; `V2/milestones/create-milestone.md` |
| Mandantentrennung | fremde Workspace-/Projekt-/Datensatz-ID → `404 not_found`, nie `403` | – | `V2/introduction.md`; `V2/authentication.md` („Tenancy“) |
| Fehler | `application/problem+json` mit `type` (geschlossene Menge: `invalid_request` 400, `unauthorized` 401, `payment_required` 402, `forbidden` 403, `not_found` 404, `method_not_allowed` 405, `not_acceptable` 406, `conflict` 409, `payload_too_large` 413, `unsupported_media_type` 415, `rate_limited` 429, `server_error` 500, `service_unavailable` 502/503/504), `code` (offen; dokumentiert: `count_pagination_disabled`, `ordering_not_cursor_eligible`, `workflow_transition_denied`, `states_managed_at_workspace`, `work_item_types_managed_at_workspace`, `work_item_types_managed_at_project`, `governance_migration_in_progress`, `listing_authorization_misconfigured`), `detail`; bei `invalid_request` zusätzlich `errors[]` mit `field`, `code` (`required`, `invalid`, `unique`, `invalid_choice`, `max_length`, `does_not_exist`), `message`; **kein** `status`/`title` im Body | v1: `{"error": …}`/`{"detail": …}` | `V2/errors.md` |
| Feature-Gating | `402 payment_required` („This feature is not available on your current plan.“), wenn Feature nicht im Plan **oder** nicht eingeschaltet; die Doku nennt als betroffen (nicht abschließend, „Affected surfaces include …“) Customers, Releases, Workflows, Automations, Worklogs, Custom Relation Definitions | v1: undokumentiert | `V2/errors.md` („Feature gating — 402“); O17 |
| Rate-Limit | je Token, getrennte Buckets für API-Keys, OAuth-, Workspace-, Service-, External-Tokens; `429` mit `Retry-After` | v1: 60/min je API-Key, Header `X-RateLimit-*` | `V2/errors.md`; `AR/introduction.md` |
| Upsert | `POST …/upsert/` mit Pflicht `external_source` + `external_id`; `201` + Header `X-Plane-Upsert: created` bzw. `200` + `X-Plane-Upsert: updated`; nur für sequenzielle Importer sicher (parallele Upserts desselben Schlüssels können doppelt anlegen) – bei Work Items, Projects, States, Labels, Cycles, Modules, Milestones, Estimates, Estimate-Points, Comments, Customers | neu | `V2/work-items/upsert-work-item.md`; Kap. 9.4 |
| Bulk | `POST …/bulk/` mit `{"items": [...], "upsert": bool}`, max. 100 Zeilen, Antwort immer `200` mit `succeeded`/`failed` und Zeilenstatus; jede Zeile eigener Savepoint; `?fields=` gilt nicht – bei Work Items, Projects, States, Labels, Cycles, Modules, Milestones, Estimates, Estimate-Points, Comments, Invitations | neu | `V2/work-items/bulk-work-items.md`; Kap. 9.4 |
| Verknüpfungen | einheitlich `POST …/{pk}/<relation>/` mit `{"add": [uuid], "remove": [uuid]}` (Initiativen: `labels/`, `projects/`, `work-items/`; Customers, Releases, Cycles, Modules, Milestones: `work-items/`; Releases: `labels/`; Collections: `members/`, `pages/`) | v1: getrennte POST/DELETE-Endpunkte, DELETE-Bodies undokumentiert (O3) | `V2/initiatives/manage-initiative-*.md`, `V2/milestones/manage-milestone-work-items.md`, `V2/cycles/manage-cycle-work-items.md`, `V2/releases/manage-release-work-items.md`, `V2/customers/manage-customer-work-items.md` |
| Feldänderungen ggü. v1 | States `default` → `is_default`; States/Work Items ohne `updated_at`, `updated_by`, `project`, `workspace`; Work Items: `description_html` **write-only**, `custom_fields` nur in Einzelobjekt-Antworten; State-Gruppe `triage` | – | `V2/migrating-from-v1.md` §8 |
| Evolution | innerhalb v2 nur additive Änderungen; Clients sollen unbekannte Felder/Enum-Werte tolerieren | – | `V2/introduction.md` |
| Work-Item-Type-Modi | siehe Kap. 4.7 (F43) | – | `V2/work-item-type-modes.md` |

**Migrationshinweis (.NET).** v2 ist die vom Hersteller empfohlene Oberfläche und in vielen Punkten näher an ASP.NET-Core-Standards (problem+json = `ProblemDetails` mit Erweiterungen `code`/`errors`, PATCH-only, Offset/Cursor). Vorschlag: eine Application-Service-Schicht, zwei Minimal-API-Gruppen `/api/v1` (Vertrag aus Kap. 2) und `/api/v2` (Vertrag aus Kap. 9); OpenAPI-Dokument je Version; Entscheidung über den Umfang → O16.

### 9.3 Ressourcen-Übersicht API v2 (alle 67 Ordner)

Pfade relativ zu `/api/v2/`; `{ws}` = `workspaces/{slug}`, `{P}` = `projects/{project_id}` (akzeptiert UUID **oder** Projekt-Identifier wie `ENG`, z. B. `V2/milestones/create-milestone.md`). „v1-Pendant“ verweist auf die IDs in Kap. 2. „CE (fachlich)“ = Stand der zugrunde liegenden Funktion in der CE; die v2-Endpunkte selbst fehlen in der CE ausnahmslos.

| # | Ordner (`V2/…`) | Endpunkte | v1-Pendant | Neu bzw. geändert in v2 | Feature | CE (fachlich) |
|---|---|---|---|---|---|---|
| 9.3.1 | `artifacts` | 4 | – | neu: create, read, `publish`, `update` (hängt Version an); kein List/Delete | F41 (Dok. 28 P09-F44) | fehlt |
| 9.3.2 | `audit-logs` | 2 | – | neu: nur Lesen (Liste, Detail) | F34 (Dok. 27) | fehlt |
| 9.3.3 | `collections` | 9 | nur Branch `PU/collection/` (Kap. 10) | v2: Mitglieder/Seiten über `POST …/members/` bzw. `…/pages/` mit `add`/`remove`; `pages-search/` | F33/F14 (Dok. 26 P07-02/03) | fehlt |
| 9.3.4 | `customer-properties` | 5 | C14–C18 | gleich (CRUD) | F04 | fehlt |
| 9.3.5 | `customer-property-values` | 2 | C19–C21 | v2: `GET` Liste und `POST` Setzen statt `GET …/{property_id}/` und `PATCH` | F04 | fehlt |
| 9.3.6 | `customer-requests` | 5 | C6–C10 | gleich (CRUD) | F04 | fehlt |
| 9.3.7 | `customers` | 7 | C1–C5, C11–C13 | neu: `upsert/`; Work-Item-Verknüpfung `POST …/{pk}/work-items/` mit `add`/`remove` statt `issues/` | F04 | fehlt |
| 9.3.8 | `cycles` | 9 | CY1–CY12 | neu: `bulk/`, `upsert/`, `…/{pk}/work-items/` (`add`/`remove`), `…/{pk}/transfer/`; Archiv nicht in v2 (D23) | CE-Ressource | Ressource im CE (v1) |
| 9.3.9 | `estimate-points` | 7 | ES5–ES8 | Pfad `…/estimates/{id}/points/` statt `estimate-points/`; neu: `bulk/`, `upsert/`, `GET {pk}` | F21 / CE-teilweise | teilweise im CE (v1 nicht geroutet) |
| 9.3.10 | `estimates` | 7 | ES1–ES4 | v2: Liste + `{pk}` statt Singleton; neu: `bulk/`, `upsert/` | F21 / CE-teilweise | teilweise im CE (v1 nicht geroutet) |
| 9.3.11 | `group-sync` | 12 | G1–G12 | gleich | F12 | fehlt |
| 9.3.12 | `initiative-labels` | 5 | I6–I10 | gleich | F03 | fehlt |
| 9.3.13 | `initiatives` | 8 | I1–I5, I11–I19 | Verknüpfungen über `POST …/{pk}/labels/`, `…/projects/`, `…/work-items/` mit `add`/`remove`; Work Items statt Epics | F02/F03 | Stub/UI-Hülle im CE |
| 9.3.14 | `intake-work-items` | 5 | IN1–IN5 | gleich (Pfad `intake-issues/`) | CE-Ressource | Ressource im CE (v1) |
| 9.3.15 | `invitations` | 5 | WI1–WI5 | neu: `bulk/`; kein `PATCH` | CE-Ressource | Ressource im CE (v1) |
| 9.3.16 | `labels` | 7 | L1–L5 | neu: `bulk/`, `upsert/` | CE-Ressource | Ressource im CE (v1) |
| 9.3.17 | `members` | 8 | M1–M7 | neu: `project-role-distribution/`; `role` als Slug; Pfad `…/projects/{pid}/members/` | CE-Ressource; F23; F26 | Ressource im CE (v1); M7 teilweise |
| 9.3.18 | `milestones` | 8 | MS1–MS6 | neu: `bulk/`, `upsert/`, `…/{pk}/work-items/` (`add`/`remove`); kein `GET …/work-items/` | F06 | Stub/UI-Hülle im CE |
| 9.3.19 | `modules` | 8 | MO1–MO11 | neu: `bulk/`, `upsert/`, `…/{pk}/work-items/` (`add`/`remove`); Archiv nicht in v2 | CE-Ressource | Ressource im CE (v1) |
| 9.3.20 | `permission-schemes` | 2 | – | neu: Lesen (Liste, Detail) | F26 | fehlt |
| 9.3.21 | `permissions` | 2 | – | neu: effektive Rechte `permissions/me/` je Workspace und Projekt | F26 | fehlt |
| 9.3.22 | `project-automations` | 19 | – | neu: Automationen mit Nodes, Edges, Activities, `status/`, `regenerate-webhook-secret/` | F35 (Dok. 25) | fehlt |
| 9.3.23 | `project-features` | 2 | PF1–PF2 | Feldnamen `is_*_enabled` (Kap. 4.11) | F16 | teilweise im CE |
| 9.3.24 | `project-pages` | 5 | PG1–PG3 | neu: `PATCH`, `DELETE` | F14 | teilweise im CE (nur interne API) |
| 9.3.25 | `project-views` | 5 | – | neu: Projekt-Views in der Public-API | F36 | teilweise im CE (nur interne API) |
| 9.3.26 | `project-work-item-templates` | 6 | – | neu: CRUD + `…/{pk}/use/` | F37 (Dok. 25 F21) | fehlt |
| 9.3.27 | `projects` | 10 | PR1–PR7 | neu: `bulk/`, `upsert/`, `…/{pk}/summary/`, `…/{pk}/unarchive/` (POST statt `DELETE …/archive/`); kein `templates/use/` | CE-Ressource | Ressource im CE (v1) |
| 9.3.28 | `release-comments` | 5 | – | neu | F24 | fehlt |
| 9.3.29 | `release-labels` | 5 | – | neu (bisher nur MCP) | F24 | fehlt |
| 9.3.30 | `release-links` | 5 | – | neu | F24 | fehlt |
| 9.3.31 | `release-tags` | 5 | – | neu (bisher nur MCP) | F24 | fehlt |
| 9.3.32 | `releases` | 9 | – | neu (bisher nur MCP): CRUD, Changelog GET/PATCH, `labels/` und `work-items/` mit `add`/`remove` | F24 | fehlt |
| 9.3.33 | `roles` | 2 | – | neu: Lesen (System- und Custom-Rollen) | F26 | fehlt |
| 9.3.34 | `states` | 7 | S1–S5 | neu: `bulk/`, `upsert/`; `default` → `is_default` | CE-Ressource | Ressource im CE (v1) |
| 9.3.35 | `stickies` | 5 | ST1–ST5 | gleich | CE-Ressource | Ressource im CE (v1) |
| 9.3.36 | `teamspaces` | 5 | TS1–TS11 | `member_ids`/`project_ids` im Objekt (PATCH) statt eigener Unterressourcen | F05 | Stub/UI-Hülle im CE |
| 9.3.37 | `user-assets` | 5 | A1–A3 | Pfad `users/me/assets/`; neu: `GET` Liste und Detail | CE-Ressource | Ressource im CE (v1) |
| 9.3.38 | `users` | 1 | U1 | Antwort `{id, email, display_name, principal_kind, scopes}` | CE-Ressource | Ressource im CE (v1) |
| 9.3.39 | `webhook-logs` | 2 | – | neu in der Public-API | F38 (Dok. 28 P09-F51) | teilweise im CE (interne API) |
| 9.3.40 | `webhooks` | 6 | – | neu in der Public-API: CRUD + `regenerate/` | F38 (Dok. 28 P09-F51) | teilweise im CE (interne API) |
| 9.3.41 | `work-item-activities` | 2 | WA1–WA2 | gleich | CE-Ressource | Ressource im CE (v1) |
| 9.3.42 | `work-item-attachments` | 5 | WT1–WT5 | gleich | CE-Ressource | Ressource im CE (v1) |
| 9.3.43 | `work-item-comments` | 7 | WC1–WC5 | neu: `bulk/`, `upsert/` | CE-Ressource | Ressource im CE (v1) |
| 9.3.44 | `work-item-dependencies` | 3 | Teil von WR1–WR3 | neu als eigene Ressource | F39 | teilweise im CE |
| 9.3.45 | `work-item-links` | 5 | WL1–WL5 | gleich | CE-Ressource | Ressource im CE (v1) |
| 9.3.46 | `work-item-properties` | 5 | P1–P5 | Properties projektweit, unabhängig vom Typ (`…/projects/{pid}/work-item-properties/`) | F09 | fehlt |
| 9.3.47 | `work-item-property-contexts` | 5 | – | neu: Kontexte je Workspace-Property | F40 | fehlt |
| 9.3.48 | `work-item-property-options` | 5 | O1–O5 | gleich | F09 | fehlt |
| 9.3.49 | `work-item-relation-definitions` | 5 | – (nur MCP) | neu als REST-Ressource | F22 | fehlt |
| 9.3.50 | `work-item-relations` | 3 | WR1–WR3 | `DELETE …/relations/{related_work_item_id}/` statt `POST …/relations/remove/` | CE-Ressource; F22 | Ressource im CE (v1, abweichend) |
| 9.3.51 | `work-item-type-properties` | 4 | – (v1: Properties unter Typ) | neu: Attach/Detach von Properties an Typen | F08/F09 | fehlt |
| 9.3.52 | `work-item-types` | 9 | T1–T6 | neu: `enable/`, `import/`, `…/{pk}/mark-default/`; Schema unter `…/{pk}/schema/` | F08/F11/F43 | teilweise im CE |
| 9.3.53 | `work-item-worklogs` | 6 | WG1–WG5 | `worklogs/summary/` statt `total-worklogs/`; neu: `GET {pk}` | F07 | teilweise im CE |
| 9.3.54 | `work-items` | 11 | W1–W7 | neu: `bulk/`, `upsert/`, `…/{pk}/archive/`, `…/{pk}/unarchive/`, Workspace-Liste `work-items/`; `search/` und `advanced-search/` (W7, W8) nicht in v2 | CE-Ressource | Ressource im CE (v1) |
| 9.3.55 | `workflow-states` | 5 | – | neu | F42 (Dok. 25) | Stub/UI-Hülle im CE |
| 9.3.56 | `workflow-transitions` | 5 | – | neu | F42 (Dok. 25) | Stub/UI-Hülle im CE |
| 9.3.57 | `workflows` | 5 | – | neu | F42 (Dok. 25) | Stub/UI-Hülle im CE |
| 9.3.58 | `workspace-assets` | 5 | A4–A6 | Pfad `…/assets/`; neu: `GET` Liste, `DELETE` | CE-Ressource | Ressource im CE (v1) |
| 9.3.59 | `workspace-automations` | 19 | – | neu (Workspace-/globale Automationen) | F35 (Dok. 25) | fehlt |
| 9.3.60 | `workspace-features` | 2 | WF1–WF2 | Feldnamen `is_*_enabled` + neue Flags (Kap. 4.11) | F17 | fehlt |
| 9.3.61 | `workspace-pages` | 5 | PG4–PG6 | neu: `PATCH`, `DELETE` | F14 | fehlt |
| 9.3.62 | `workspace-views` | 5 | – | neu: Workspace-Views in der Public-API | F36 | teilweise im CE (nur interne API) |
| 9.3.63 | `workspace-work-item-properties` | 5 | – | neu (Workspace-Modus) | F43 | fehlt |
| 9.3.64 | `workspace-work-item-property-options` | 5 | – | neu (Workspace-Modus) | F43 | fehlt |
| 9.3.65 | `workspace-work-item-templates` | 5 | – | neu: CRUD | F37 (Dok. 25 F21) | fehlt |
| 9.3.66 | `workspace-work-item-type-properties` | 4 | – | neu (Workspace-Modus) | F43 | fehlt |
| 9.3.67 | `workspace-work-item-types` | 6 | – | neu (Workspace-Modus) inkl. `mark-default/` | F43 | fehlt |

Summe: 387 Endpunkte in 67 Ordnern (Skript-Extraktion der `api-endpoint-badge`-Blöcke; keine Dubletten über Methode+Pfad).

### 9.4 Vollständiges Endpunkt-Inventar API v2

Quelle je Zeile: `V2/<Ordner>/<Datei>`. Scope = Inhalt des Abschnitts „Scopes“ der Endpunktseite (jeweils auch durch globales `read` bzw. `write` erfüllbar, `V2/authentication.md`). Leere Scope-Zelle = Seite nennt keinen Scope (`users/get-current-user.md`: API-Key immer, OAuth braucht globales `read`; `permissions/*`; `work-item-worklogs/get-project-worklog-summary.md`).

| # | Ordner | Datei | Methode | Pfad | Titel | Scope |
|---|---|---|---|---|---|---|
| V1 | `artifacts` | `create-artifact.md` | POST | `{ws}/artifacts/` | Create an artifact | `workspaces.artifacts:write` |
| V2 | `artifacts` | `get-artifact.md` | GET | `{ws}/artifacts/{artifact_id}/` | Get an artifact | `workspaces.artifacts:read` |
| V3 | `artifacts` | `publish-artifact.md` | POST | `{ws}/artifacts/{artifact_id}/publish/` | Publish an artifact | `workspaces.artifacts:write` |
| V4 | `artifacts` | `update-artifact.md` | PATCH | `{ws}/artifacts/{artifact_id}/update/` | Append a new version | `workspaces.artifacts:write` |
| V5 | `audit-logs` | `list-audit-logs.md` | GET | `{ws}/audit-logs/` | List audit logs | `workspaces.audit_logs:read` |
| V6 | `audit-logs` | `get-audit-log.md` | GET | `{ws}/audit-logs/{pk}/` | Get an audit log | `workspaces.audit_logs:read` |
| V7 | `collections` | `list-collections.md` | GET | `{ws}/collections/` | List collections | `wiki.pages:read` |
| V8 | `collections` | `create-collection.md` | POST | `{ws}/collections/` | Create a collection | `wiki.pages:write` |
| V9 | `collections` | `get-collection.md` | GET | `{ws}/collections/{pk}/` | Get a collection | `wiki.pages:read` |
| V10 | `collections` | `update-collection.md` | PATCH | `{ws}/collections/{pk}/` | Update a collection | `wiki.pages:write` |
| V11 | `collections` | `delete-collection.md` | DELETE | `{ws}/collections/{pk}/` | Delete a collection | `wiki.pages:write` |
| V12 | `collections` | `list-collection-members.md` | GET | `{ws}/collections/{pk}/members/` | List collection members | `wiki.pages:read` |
| V13 | `collections` | `manage-collection-members.md` | POST | `{ws}/collections/{pk}/members/` | Add or remove collection members | `wiki.pages:write` |
| V14 | `collections` | `search-collection-pages.md` | GET | `{ws}/collections/{pk}/pages-search/` | Search pages for a collection | `wiki.pages:read` |
| V15 | `collections` | `manage-collection-pages.md` | POST | `{ws}/collections/{pk}/pages/` | Add or remove pages in a collection | `wiki.pages:write` |
| V16 | `customer-properties` | `list-customer-properties.md` | GET | `{ws}/customer-properties/` | List customer properties | `customers.properties:read` |
| V17 | `customer-properties` | `create-customer-property.md` | POST | `{ws}/customer-properties/` | Create a customer property | `customers.properties:write` |
| V18 | `customer-properties` | `get-customer-property.md` | GET | `{ws}/customer-properties/{pk}/` | Get a customer property | `customers.properties:read` |
| V19 | `customer-properties` | `update-customer-property.md` | PATCH | `{ws}/customer-properties/{pk}/` | Update a customer property | `customers.properties:write` |
| V20 | `customer-properties` | `delete-customer-property.md` | DELETE | `{ws}/customer-properties/{pk}/` | Delete a customer property | `customers.properties:write` |
| V21 | `customer-property-values` | `list-customer-property-values.md` | GET | `{ws}/customers/{customer_id}/property-values/` | List customer property values | `customers.property_values:read` |
| V22 | `customer-property-values` | `set-customer-property-values.md` | POST | `{ws}/customers/{customer_id}/property-values/` | Set customer property values | `customers.property_values:write` |
| V23 | `customer-requests` | `list-customer-requests.md` | GET | `{ws}/customers/{customer_id}/requests/` | List customer requests | `customers.requests:read` |
| V24 | `customer-requests` | `create-customer-request.md` | POST | `{ws}/customers/{customer_id}/requests/` | Create a customer request | `customers.requests:write` |
| V25 | `customer-requests` | `get-customer-request.md` | GET | `{ws}/customers/{customer_id}/requests/{pk}/` | Get a customer request | `customers.requests:read` |
| V26 | `customer-requests` | `update-customer-request.md` | PATCH | `{ws}/customers/{customer_id}/requests/{pk}/` | Update a customer request | `customers.requests:write` |
| V27 | `customer-requests` | `delete-customer-request.md` | DELETE | `{ws}/customers/{customer_id}/requests/{pk}/` | Delete a customer request | `customers.requests:write` |
| V28 | `customers` | `list-customers.md` | GET | `{ws}/customers/` | List customers | `customers:read` |
| V29 | `customers` | `create-customer.md` | POST | `{ws}/customers/` | Create a customer | `customers:write` |
| V30 | `customers` | `upsert-customer.md` | POST | `{ws}/customers/upsert/` | Upsert a customer | `customers:write` |
| V31 | `customers` | `get-customer.md` | GET | `{ws}/customers/{pk}/` | Get a customer | `customers:read` |
| V32 | `customers` | `update-customer.md` | PATCH | `{ws}/customers/{pk}/` | Update a customer | `customers:write` |
| V33 | `customers` | `delete-customer.md` | DELETE | `{ws}/customers/{pk}/` | Delete a customer | `customers:write` |
| V34 | `customers` | `manage-customer-work-items.md` | POST | `{ws}/customers/{pk}/work-items/` | Link or unlink customer work items | `customers:write` |
| V35 | `cycles` | `list-cycles.md` | GET | `{ws}/{P}/cycles/` | List cycles | `projects.cycles:read` |
| V36 | `cycles` | `create-cycle.md` | POST | `{ws}/{P}/cycles/` | Create a cycle | `projects.cycles:write` |
| V37 | `cycles` | `bulk-cycles.md` | POST | `{ws}/{P}/cycles/bulk/` | Bulk write cycles | `projects.cycles:write` |
| V38 | `cycles` | `upsert-cycle.md` | POST | `{ws}/{P}/cycles/upsert/` | Upsert a cycle | `projects.cycles:write` |
| V39 | `cycles` | `get-cycle.md` | GET | `{ws}/{P}/cycles/{pk}/` | Get a cycle | `projects.cycles:read` |
| V40 | `cycles` | `update-cycle.md` | PATCH | `{ws}/{P}/cycles/{pk}/` | Update a cycle | `projects.cycles:write` |
| V41 | `cycles` | `delete-cycle.md` | DELETE | `{ws}/{P}/cycles/{pk}/` | Delete a cycle | `projects.cycles:write` |
| V42 | `cycles` | `transfer-cycle-work-items.md` | POST | `{ws}/{P}/cycles/{pk}/transfer/` | Transfer work items between cycles | `projects.cycles:write` |
| V43 | `cycles` | `manage-cycle-work-items.md` | POST | `{ws}/{P}/cycles/{pk}/work-items/` | Add or remove cycle work items | `projects.cycles:write` |
| V44 | `estimate-points` | `list-estimate-points.md` | GET | `{ws}/{P}/estimates/{estimate_id}/points/` | List estimate points | `projects.estimates:read` |
| V45 | `estimate-points` | `create-estimate-point.md` | POST | `{ws}/{P}/estimates/{estimate_id}/points/` | Create a estimate point | `projects.estimates:write` |
| V46 | `estimate-points` | `bulk-estimate-points.md` | POST | `{ws}/{P}/estimates/{estimate_id}/points/bulk/` | Bulk write estimate points | `projects.estimates:write` |
| V47 | `estimate-points` | `upsert-estimate-point.md` | POST | `{ws}/{P}/estimates/{estimate_id}/points/upsert/` | Upsert a estimate point | `projects.estimates:write` |
| V48 | `estimate-points` | `get-estimate-point.md` | GET | `{ws}/{P}/estimates/{estimate_id}/points/{pk}/` | Get a estimate point | `projects.estimates:read` |
| V49 | `estimate-points` | `update-estimate-point.md` | PATCH | `{ws}/{P}/estimates/{estimate_id}/points/{pk}/` | Update a estimate point | `projects.estimates:write` |
| V50 | `estimate-points` | `delete-estimate-point.md` | DELETE | `{ws}/{P}/estimates/{estimate_id}/points/{pk}/` | Delete a estimate point | `projects.estimates:write` |
| V51 | `estimates` | `list-estimates.md` | GET | `{ws}/{P}/estimates/` | List estimates | `projects.estimates:read` |
| V52 | `estimates` | `create-estimate.md` | POST | `{ws}/{P}/estimates/` | Create a estimate | `projects.estimates:write` |
| V53 | `estimates` | `bulk-estimates.md` | POST | `{ws}/{P}/estimates/bulk/` | Bulk write estimates | `projects.estimates:write` |
| V54 | `estimates` | `upsert-estimate.md` | POST | `{ws}/{P}/estimates/upsert/` | Upsert a estimate | `projects.estimates:write` |
| V55 | `estimates` | `get-estimate.md` | GET | `{ws}/{P}/estimates/{pk}/` | Get a estimate | `projects.estimates:read` |
| V56 | `estimates` | `update-estimate.md` | PATCH | `{ws}/{P}/estimates/{pk}/` | Update a estimate | `projects.estimates:write` |
| V57 | `estimates` | `delete-estimate.md` | DELETE | `{ws}/{P}/estimates/{pk}/` | Delete a estimate | `projects.estimates:write` |
| V58 | `group-sync` | `get-group-sync-config.md` | GET | `{ws}/group-sync/config/` | Get the group sync configuration | `workspaces.group_sync:read` |
| V59 | `group-sync` | `update-group-sync-config.md` | PATCH | `{ws}/group-sync/config/` | Update the group sync configuration | `workspaces.group_sync:write` |
| V60 | `group-sync` | `list-project-mappings.md` | GET | `{ws}/group-sync/project-mappings/` | List project mappings | `workspaces.group_sync:read` |
| V61 | `group-sync` | `create-project-mapping.md` | POST | `{ws}/group-sync/project-mappings/` | Create a project mapping | `workspaces.group_sync:write` |
| V62 | `group-sync` | `get-project-mapping.md` | GET | `{ws}/group-sync/project-mappings/{pk}/` | Get a project mapping | `workspaces.group_sync:read` |
| V63 | `group-sync` | `update-project-mapping.md` | PATCH | `{ws}/group-sync/project-mappings/{pk}/` | Update a project mapping | `workspaces.group_sync:write` |
| V64 | `group-sync` | `delete-project-mapping.md` | DELETE | `{ws}/group-sync/project-mappings/{pk}/` | Delete a project mapping | `workspaces.group_sync:write` |
| V65 | `group-sync` | `list-workspace-mappings.md` | GET | `{ws}/group-sync/workspace-mappings/` | List workspace mappings | `workspaces.group_sync:read` |
| V66 | `group-sync` | `create-workspace-mapping.md` | POST | `{ws}/group-sync/workspace-mappings/` | Create a workspace mapping | `workspaces.group_sync:write` |
| V67 | `group-sync` | `get-workspace-mapping.md` | GET | `{ws}/group-sync/workspace-mappings/{pk}/` | Get a workspace mapping | `workspaces.group_sync:read` |
| V68 | `group-sync` | `update-workspace-mapping.md` | PATCH | `{ws}/group-sync/workspace-mappings/{pk}/` | Update a workspace mapping | `workspaces.group_sync:write` |
| V69 | `group-sync` | `delete-workspace-mapping.md` | DELETE | `{ws}/group-sync/workspace-mappings/{pk}/` | Delete a workspace mapping | `workspaces.group_sync:write` |
| V70 | `initiative-labels` | `list-initiative-labels.md` | GET | `{ws}/initiatives/labels/` | List initiative labels | `initiatives.labels:read` |
| V71 | `initiative-labels` | `create-initiative-label.md` | POST | `{ws}/initiatives/labels/` | Create a initiative label | `initiatives.labels:write` |
| V72 | `initiative-labels` | `get-initiative-label.md` | GET | `{ws}/initiatives/labels/{pk}/` | Get a initiative label | `initiatives.labels:read` |
| V73 | `initiative-labels` | `update-initiative-label.md` | PATCH | `{ws}/initiatives/labels/{pk}/` | Update a initiative label | `initiatives.labels:write` |
| V74 | `initiative-labels` | `delete-initiative-label.md` | DELETE | `{ws}/initiatives/labels/{pk}/` | Delete a initiative label | `initiatives.labels:write` |
| V75 | `initiatives` | `list-initiatives.md` | GET | `{ws}/initiatives/` | List initiatives | `initiatives:read` |
| V76 | `initiatives` | `create-initiative.md` | POST | `{ws}/initiatives/` | Create a initiative | `initiatives:write` |
| V77 | `initiatives` | `get-initiative.md` | GET | `{ws}/initiatives/{pk}/` | Get a initiative | `initiatives:read` |
| V78 | `initiatives` | `update-initiative.md` | PATCH | `{ws}/initiatives/{pk}/` | Update a initiative | `initiatives:write` |
| V79 | `initiatives` | `delete-initiative.md` | DELETE | `{ws}/initiatives/{pk}/` | Delete a initiative | `initiatives:write` |
| V80 | `initiatives` | `manage-initiative-labels.md` | POST | `{ws}/initiatives/{pk}/labels/` | Add or remove initiative labels | `initiatives:write` |
| V81 | `initiatives` | `manage-initiative-projects.md` | POST | `{ws}/initiatives/{pk}/projects/` | Add or remove initiative projects | `initiatives:write` |
| V82 | `initiatives` | `manage-initiative-work-items.md` | POST | `{ws}/initiatives/{pk}/work-items/` | Add or remove initiative work items | `initiatives:write` |
| V83 | `intake-work-items` | `list-intake-work-items.md` | GET | `{ws}/{P}/intake-issues/` | List intake work items | `projects.intakes:read` |
| V84 | `intake-work-items` | `create-intake-work-item.md` | POST | `{ws}/{P}/intake-issues/` | Create a intake work item | `projects.intakes:write` |
| V85 | `intake-work-items` | `get-intake-work-item.md` | GET | `{ws}/{P}/intake-issues/{pk}/` | Get a intake work item | `projects.intakes:read` |
| V86 | `intake-work-items` | `update-intake-work-item.md` | PATCH | `{ws}/{P}/intake-issues/{pk}/` | Update a intake work item | `projects.intakes:write` |
| V87 | `intake-work-items` | `delete-intake-work-item.md` | DELETE | `{ws}/{P}/intake-issues/{pk}/` | Delete a intake work item | `projects.intakes:write` |
| V88 | `invitations` | `list-invitations.md` | GET | `{ws}/invitations/` | List invitations | `workspaces.members:read` |
| V89 | `invitations` | `create-invitation.md` | POST | `{ws}/invitations/` | Create a invitation | `workspaces.members:write` |
| V90 | `invitations` | `bulk-invitations.md` | POST | `{ws}/invitations/bulk/` | Bulk write invitations | `workspaces.members:write` |
| V91 | `invitations` | `get-invitation.md` | GET | `{ws}/invitations/{pk}/` | Get a invitation | `workspaces.members:read` |
| V92 | `invitations` | `delete-invitation.md` | DELETE | `{ws}/invitations/{pk}/` | Delete a invitation | `workspaces.members:write` |
| V93 | `labels` | `list-labels.md` | GET | `{ws}/{P}/labels/` | List labels | `projects.labels:read` |
| V94 | `labels` | `create-label.md` | POST | `{ws}/{P}/labels/` | Create a label | `projects.labels:write` |
| V95 | `labels` | `bulk-labels.md` | POST | `{ws}/{P}/labels/bulk/` | Bulk write labels | `projects.labels:write` |
| V96 | `labels` | `upsert-label.md` | POST | `{ws}/{P}/labels/upsert/` | Upsert a label | `projects.labels:write` |
| V97 | `labels` | `get-label.md` | GET | `{ws}/{P}/labels/{pk}/` | Get a label | `projects.labels:read` |
| V98 | `labels` | `update-label.md` | PATCH | `{ws}/{P}/labels/{pk}/` | Update a label | `projects.labels:write` |
| V99 | `labels` | `delete-label.md` | DELETE | `{ws}/{P}/labels/{pk}/` | Delete a label | `projects.labels:write` |
| V100 | `members` | `list-workspace-members.md` | GET | `{ws}/members/` | List workspace members | `workspaces.members:read` |
| V101 | `members` | `remove-workspace-member.md` | POST | `{ws}/members/remove/` | Remove a workspace member | `workspaces.members:write` |
| V102 | `members` | `get-project-role-distribution.md` | GET | `{ws}/project-role-distribution/` | Get project role distribution | `workspaces.members:read` |
| V103 | `members` | `list-project-members.md` | GET | `{ws}/{P}/members/` | List project members | `projects.members:read` |
| V104 | `members` | `create-project-member.md` | POST | `{ws}/{P}/members/` | Create a project member | `projects.members:write` |
| V105 | `members` | `get-project-member.md` | GET | `{ws}/{P}/members/{pk}/` | Get a project member | `projects.members:read` |
| V106 | `members` | `update-project-member.md` | PATCH | `{ws}/{P}/members/{pk}/` | Update a project member | `projects.members:write` |
| V107 | `members` | `delete-project-member.md` | DELETE | `{ws}/{P}/members/{pk}/` | Delete a project member | `projects.members:write` |
| V108 | `milestones` | `list-milestones.md` | GET | `{ws}/{P}/milestones/` | List milestones | `projects.milestones:read` |
| V109 | `milestones` | `create-milestone.md` | POST | `{ws}/{P}/milestones/` | Create a milestone | `projects.milestones:write` |
| V110 | `milestones` | `bulk-milestones.md` | POST | `{ws}/{P}/milestones/bulk/` | Bulk write milestones | `projects.milestones:write` |
| V111 | `milestones` | `upsert-milestone.md` | POST | `{ws}/{P}/milestones/upsert/` | Upsert a milestone | `projects.milestones:write` |
| V112 | `milestones` | `get-milestone.md` | GET | `{ws}/{P}/milestones/{pk}/` | Get a milestone | `projects.milestones:read` |
| V113 | `milestones` | `update-milestone.md` | PATCH | `{ws}/{P}/milestones/{pk}/` | Update a milestone | `projects.milestones:write` |
| V114 | `milestones` | `delete-milestone.md` | DELETE | `{ws}/{P}/milestones/{pk}/` | Delete a milestone | `projects.milestones:write` |
| V115 | `milestones` | `manage-milestone-work-items.md` | POST | `{ws}/{P}/milestones/{pk}/work-items/` | Add or remove milestone work items | `projects.milestones:write` |
| V116 | `modules` | `list-modules.md` | GET | `{ws}/{P}/modules/` | List modules | `projects.modules:read` |
| V117 | `modules` | `create-module.md` | POST | `{ws}/{P}/modules/` | Create a module | `projects.modules:write` |
| V118 | `modules` | `bulk-modules.md` | POST | `{ws}/{P}/modules/bulk/` | Bulk write modules | `projects.modules:write` |
| V119 | `modules` | `upsert-module.md` | POST | `{ws}/{P}/modules/upsert/` | Upsert a module | `projects.modules:write` |
| V120 | `modules` | `get-module.md` | GET | `{ws}/{P}/modules/{pk}/` | Get a module | `projects.modules:read` |
| V121 | `modules` | `update-module.md` | PATCH | `{ws}/{P}/modules/{pk}/` | Update a module | `projects.modules:write` |
| V122 | `modules` | `delete-module.md` | DELETE | `{ws}/{P}/modules/{pk}/` | Delete a module | `projects.modules:write` |
| V123 | `modules` | `manage-module-work-items.md` | POST | `{ws}/{P}/modules/{pk}/work-items/` | Add or remove module work items | `projects.modules:write` |
| V124 | `permission-schemes` | `list-permission-schemes.md` | GET | `{ws}/permission-schemes/` | List permission schemes | `workspaces.roles:read` |
| V125 | `permission-schemes` | `get-permission-scheme.md` | GET | `{ws}/permission-schemes/{pk}/` | Get a permission scheme | `workspaces.roles:read` |
| V126 | `permissions` | `get-workspace-permissions.md` | GET | `{ws}/permissions/me/` | Get your effective workspace permissions | – |
| V127 | `permissions` | `get-project-permissions.md` | GET | `{ws}/{P}/permissions/me/` | Get your effective project permissions | – |
| V128 | `project-automations` | `list-project-automations.md` | GET | `{ws}/{P}/automations/` | List project automations | `automations:read` |
| V129 | `project-automations` | `create-project-automation.md` | POST | `{ws}/{P}/automations/` | Create a project automation | `automations:write` |
| V130 | `project-automations` | `list-automation-activities.md` | GET | `{ws}/{P}/automations/{automation_id}/activities/` | List automation activities | `automations:read` |
| V131 | `project-automations` | `get-automation-activity.md` | GET | `{ws}/{P}/automations/{automation_id}/activities/{pk}/` | Get a automation activity | `automations:read` |
| V132 | `project-automations` | `list-automation-edges.md` | GET | `{ws}/{P}/automations/{automation_id}/edges/` | List automation edges | `automations:read` |
| V133 | `project-automations` | `create-automation-edge.md` | POST | `{ws}/{P}/automations/{automation_id}/edges/` | Create a automation edge | `automations:write` |
| V134 | `project-automations` | `get-automation-edge.md` | GET | `{ws}/{P}/automations/{automation_id}/edges/{pk}/` | Get a automation edge | `automations:read` |
| V135 | `project-automations` | `update-automation-edge.md` | PATCH | `{ws}/{P}/automations/{automation_id}/edges/{pk}/` | Update a automation edge | `automations:write` |
| V136 | `project-automations` | `delete-automation-edge.md` | DELETE | `{ws}/{P}/automations/{automation_id}/edges/{pk}/` | Delete a automation edge | `automations:write` |
| V137 | `project-automations` | `list-automation-nodes.md` | GET | `{ws}/{P}/automations/{automation_id}/nodes/` | List automation nodes | `automations:read` |
| V138 | `project-automations` | `create-automation-node.md` | POST | `{ws}/{P}/automations/{automation_id}/nodes/` | Create a automation node | `automations:write` |
| V139 | `project-automations` | `get-automation-node.md` | GET | `{ws}/{P}/automations/{automation_id}/nodes/{pk}/` | Get a automation node | `automations:read` |
| V140 | `project-automations` | `update-automation-node.md` | PATCH | `{ws}/{P}/automations/{automation_id}/nodes/{pk}/` | Update a automation node | `automations:write` |
| V141 | `project-automations` | `delete-automation-node.md` | DELETE | `{ws}/{P}/automations/{automation_id}/nodes/{pk}/` | Delete a automation node | `automations:write` |
| V142 | `project-automations` | `regenerate-node-webhook-secret.md` | POST | `{ws}/{P}/automations/{automation_id}/nodes/{pk}/regenerate-webhook-secret/` | Regenerate an automation node webhook secret | `automations:write` |
| V143 | `project-automations` | `get-project-automation.md` | GET | `{ws}/{P}/automations/{pk}/` | Get a project automation | `automations:read` |
| V144 | `project-automations` | `update-project-automation.md` | PATCH | `{ws}/{P}/automations/{pk}/` | Update a project automation | `automations:write` |
| V145 | `project-automations` | `delete-project-automation.md` | DELETE | `{ws}/{P}/automations/{pk}/` | Delete a project automation | `automations:write` |
| V146 | `project-automations` | `set-project-automation-status.md` | POST | `{ws}/{P}/automations/{pk}/status/` | Enable or disable a project automation | `automations:write` |
| V147 | `project-features` | `get-project-features.md` | GET | `{ws}/{P}/features/` | Get project features | `projects.features:read` |
| V148 | `project-features` | `update-project-features.md` | PATCH | `{ws}/{P}/features/` | Update project features | `projects.features:write` |
| V149 | `project-pages` | `list-project-pages.md` | GET | `{ws}/{P}/pages/` | List project pages | `projects.pages:read` |
| V150 | `project-pages` | `create-project-page.md` | POST | `{ws}/{P}/pages/` | Create a project page | `projects.pages:write` |
| V151 | `project-pages` | `get-project-page.md` | GET | `{ws}/{P}/pages/{pk}/` | Get a project page | `projects.pages:read` |
| V152 | `project-pages` | `update-project-page.md` | PATCH | `{ws}/{P}/pages/{pk}/` | Update a project page | `projects.pages:write` |
| V153 | `project-pages` | `delete-project-page.md` | DELETE | `{ws}/{P}/pages/{pk}/` | Delete a project page | `projects.pages:write` |
| V154 | `project-views` | `list-project-views.md` | GET | `{ws}/{P}/views/` | List project views | `projects.views:read` |
| V155 | `project-views` | `create-project-view.md` | POST | `{ws}/{P}/views/` | Create a project view | `projects.views:write` |
| V156 | `project-views` | `get-project-view.md` | GET | `{ws}/{P}/views/{pk}/` | Get a project view | `projects.views:read` |
| V157 | `project-views` | `update-project-view.md` | PATCH | `{ws}/{P}/views/{pk}/` | Update a project view | `projects.views:write` |
| V158 | `project-views` | `delete-project-view.md` | DELETE | `{ws}/{P}/views/{pk}/` | Delete a project view | `projects.views:write` |
| V159 | `project-work-item-templates` | `list-project-work-item-templates.md` | GET | `{ws}/{P}/work-item-templates/` | List project work item templates | `templates.work_items:read` |
| V160 | `project-work-item-templates` | `create-project-work-item-template.md` | POST | `{ws}/{P}/work-item-templates/` | Create a project work item template | `templates.work_items:write` |
| V161 | `project-work-item-templates` | `get-project-work-item-template.md` | GET | `{ws}/{P}/work-item-templates/{pk}/` | Get a project work item template | `templates.work_items:read` |
| V162 | `project-work-item-templates` | `update-project-work-item-template.md` | PATCH | `{ws}/{P}/work-item-templates/{pk}/` | Update a project work item template | `templates.work_items:write` |
| V163 | `project-work-item-templates` | `delete-project-work-item-template.md` | DELETE | `{ws}/{P}/work-item-templates/{pk}/` | Delete a project work item template | `templates.work_items:write` |
| V164 | `project-work-item-templates` | `use-work-item-template.md` | POST | `{ws}/{P}/work-item-templates/{pk}/use/` | Create a work item from a template | `templates.work_items:write` |
| V165 | `projects` | `list-projects.md` | GET | `{ws}/projects/` | List projects | `projects:read` |
| V166 | `projects` | `create-project.md` | POST | `{ws}/projects/` | Create a project | `projects:write` |
| V167 | `projects` | `bulk-projects.md` | POST | `{ws}/projects/bulk/` | Bulk write projects | `projects:write` |
| V168 | `projects` | `upsert-project.md` | POST | `{ws}/projects/upsert/` | Upsert a project | `projects:write` |
| V169 | `projects` | `get-project.md` | GET | `{ws}/projects/{pk}/` | Get a project | `projects:read` |
| V170 | `projects` | `update-project.md` | PATCH | `{ws}/projects/{pk}/` | Update a project | `projects:write` |
| V171 | `projects` | `delete-project.md` | DELETE | `{ws}/projects/{pk}/` | Delete a project | `projects:write` |
| V172 | `projects` | `archive-project.md` | POST | `{ws}/projects/{pk}/archive/` | Archive a project | `projects:write` |
| V173 | `projects` | `get-project-summary.md` | GET | `{ws}/projects/{pk}/summary/` | Get a project summary | `projects:read` |
| V174 | `projects` | `unarchive-project.md` | POST | `{ws}/projects/{pk}/unarchive/` | Unarchive a project | `projects:write` |
| V175 | `release-comments` | `list-release-comments.md` | GET | `{ws}/releases/{release_id}/comments/` | List release comments | `releases.comments:read` |
| V176 | `release-comments` | `create-release-comment.md` | POST | `{ws}/releases/{release_id}/comments/` | Create a release comment | `releases.comments:write` |
| V177 | `release-comments` | `get-release-comment.md` | GET | `{ws}/releases/{release_id}/comments/{pk}/` | Get a release comment | `releases.comments:read` |
| V178 | `release-comments` | `update-release-comment.md` | PATCH | `{ws}/releases/{release_id}/comments/{pk}/` | Update a release comment | `releases.comments:write` |
| V179 | `release-comments` | `delete-release-comment.md` | DELETE | `{ws}/releases/{release_id}/comments/{pk}/` | Delete a release comment | `releases.comments:write` |
| V180 | `release-labels` | `list-release-labels.md` | GET | `{ws}/releases/labels/` | List release labels | `releases.labels:read` |
| V181 | `release-labels` | `create-release-label.md` | POST | `{ws}/releases/labels/` | Create a release label | `releases.labels:write` |
| V182 | `release-labels` | `get-release-label.md` | GET | `{ws}/releases/labels/{pk}/` | Get a release label | `releases.labels:read` |
| V183 | `release-labels` | `update-release-label.md` | PATCH | `{ws}/releases/labels/{pk}/` | Update a release label | `releases.labels:write` |
| V184 | `release-labels` | `delete-release-label.md` | DELETE | `{ws}/releases/labels/{pk}/` | Delete a release label | `releases.labels:write` |
| V185 | `release-links` | `list-release-links.md` | GET | `{ws}/releases/{release_id}/links/` | List release links | `releases.links:read` |
| V186 | `release-links` | `create-release-link.md` | POST | `{ws}/releases/{release_id}/links/` | Create a release link | `releases.links:write` |
| V187 | `release-links` | `get-release-link.md` | GET | `{ws}/releases/{release_id}/links/{pk}/` | Get a release link | `releases.links:read` |
| V188 | `release-links` | `update-release-link.md` | PATCH | `{ws}/releases/{release_id}/links/{pk}/` | Update a release link | `releases.links:write` |
| V189 | `release-links` | `delete-release-link.md` | DELETE | `{ws}/releases/{release_id}/links/{pk}/` | Delete a release link | `releases.links:write` |
| V190 | `release-tags` | `list-release-tags.md` | GET | `{ws}/releases/tags/` | List release tags | `releases.tags:read` |
| V191 | `release-tags` | `create-release-tag.md` | POST | `{ws}/releases/tags/` | Create a release tag | `releases.tags:write` |
| V192 | `release-tags` | `get-release-tag.md` | GET | `{ws}/releases/tags/{pk}/` | Get a release tag | `releases.tags:read` |
| V193 | `release-tags` | `update-release-tag.md` | PATCH | `{ws}/releases/tags/{pk}/` | Update a release tag | `releases.tags:write` |
| V194 | `release-tags` | `delete-release-tag.md` | DELETE | `{ws}/releases/tags/{pk}/` | Delete a release tag | `releases.tags:write` |
| V195 | `releases` | `list-releases.md` | GET | `{ws}/releases/` | List releases | `releases:read` |
| V196 | `releases` | `create-release.md` | POST | `{ws}/releases/` | Create a release | `releases:write` |
| V197 | `releases` | `get-release.md` | GET | `{ws}/releases/{pk}/` | Get a release | `releases:read` |
| V198 | `releases` | `update-release.md` | PATCH | `{ws}/releases/{pk}/` | Update a release | `releases:write` |
| V199 | `releases` | `delete-release.md` | DELETE | `{ws}/releases/{pk}/` | Delete a release | `releases:write` |
| V200 | `releases` | `get-release-changelog.md` | GET | `{ws}/releases/{pk}/changelog/` | Get a release changelog | `releases:read` |
| V201 | `releases` | `update-release-changelog.md` | PATCH | `{ws}/releases/{pk}/changelog/` | Update a release changelog | `releases:write` |
| V202 | `releases` | `manage-release-labels.md` | POST | `{ws}/releases/{pk}/labels/` | Add or remove release labels | `releases:write` |
| V203 | `releases` | `manage-release-work-items.md` | POST | `{ws}/releases/{pk}/work-items/` | Add or remove release work items | `releases:write` |
| V204 | `roles` | `list-roles.md` | GET | `{ws}/roles/` | List roles | `workspaces.roles:read` |
| V205 | `roles` | `get-role.md` | GET | `{ws}/roles/{pk}/` | Get a role | `workspaces.roles:read` |
| V206 | `states` | `list-states.md` | GET | `{ws}/{P}/states/` | List states | `projects.states:read` |
| V207 | `states` | `create-state.md` | POST | `{ws}/{P}/states/` | Create a state | `projects.states:write` |
| V208 | `states` | `bulk-states.md` | POST | `{ws}/{P}/states/bulk/` | Bulk write states | `projects.states:write` |
| V209 | `states` | `upsert-state.md` | POST | `{ws}/{P}/states/upsert/` | Upsert a state | `projects.states:write` |
| V210 | `states` | `get-state.md` | GET | `{ws}/{P}/states/{pk}/` | Get a state | `projects.states:read` |
| V211 | `states` | `update-state.md` | PATCH | `{ws}/{P}/states/{pk}/` | Update a state | `projects.states:write` |
| V212 | `states` | `delete-state.md` | DELETE | `{ws}/{P}/states/{pk}/` | Delete a state | `projects.states:write` |
| V213 | `stickies` | `list-stickies.md` | GET | `{ws}/stickies/` | List stickies | `stickies:read` |
| V214 | `stickies` | `create-sticky.md` | POST | `{ws}/stickies/` | Create a sticky | `stickies:write` |
| V215 | `stickies` | `get-sticky.md` | GET | `{ws}/stickies/{pk}/` | Get a sticky | `stickies:read` |
| V216 | `stickies` | `update-sticky.md` | PATCH | `{ws}/stickies/{pk}/` | Update a sticky | `stickies:write` |
| V217 | `stickies` | `delete-sticky.md` | DELETE | `{ws}/stickies/{pk}/` | Delete a sticky | `stickies:write` |
| V218 | `teamspaces` | `list-teamspaces.md` | GET | `{ws}/teamspaces/` | List teamspaces | `teamspaces:read` |
| V219 | `teamspaces` | `create-teamspace.md` | POST | `{ws}/teamspaces/` | Create a teamspace | `teamspaces:write` |
| V220 | `teamspaces` | `get-teamspace.md` | GET | `{ws}/teamspaces/{pk}/` | Get a teamspace | `teamspaces:read` |
| V221 | `teamspaces` | `update-teamspace.md` | PATCH | `{ws}/teamspaces/{pk}/` | Update a teamspace | `teamspaces:write` |
| V222 | `teamspaces` | `delete-teamspace.md` | DELETE | `{ws}/teamspaces/{pk}/` | Delete a teamspace | `teamspaces:write` |
| V223 | `user-assets` | `list-user-assets.md` | GET | `users/me/assets/` | List user assets | `assets:read` |
| V224 | `user-assets` | `create-user-asset.md` | POST | `users/me/assets/` | Create a user asset upload | `assets:write` |
| V225 | `user-assets` | `get-user-asset.md` | GET | `users/me/assets/{pk}/` | Get a user asset | `assets:read` |
| V226 | `user-assets` | `confirm-user-asset.md` | PATCH | `users/me/assets/{pk}/` | Confirm a user asset upload | `assets:write` |
| V227 | `user-assets` | `delete-user-asset.md` | DELETE | `users/me/assets/{pk}/` | Delete a user asset | `assets:write` |
| V228 | `users` | `get-current-user.md` | GET | `users/me/` | Get current user | – |
| V229 | `webhook-logs` | `list-webhook-logs.md` | GET | `{ws}/webhook-logs/{webhook_id}/` | List webhook logs | `webhooks:read` |
| V230 | `webhook-logs` | `get-webhook-log.md` | GET | `{ws}/webhook-logs/{webhook_id}/{pk}/` | Get a webhook log | `webhooks:read` |
| V231 | `webhooks` | `list-webhooks.md` | GET | `{ws}/webhooks/` | List webhooks | `webhooks:read` |
| V232 | `webhooks` | `create-webhook.md` | POST | `{ws}/webhooks/` | Create a webhook | `webhooks:write` |
| V233 | `webhooks` | `get-webhook.md` | GET | `{ws}/webhooks/{pk}/` | Get a webhook | `webhooks:read` |
| V234 | `webhooks` | `update-webhook.md` | PATCH | `{ws}/webhooks/{pk}/` | Update a webhook | `webhooks:write` |
| V235 | `webhooks` | `delete-webhook.md` | DELETE | `{ws}/webhooks/{pk}/` | Delete a webhook | `webhooks:write` |
| V236 | `webhooks` | `regenerate-webhook-secret.md` | POST | `{ws}/webhooks/{pk}/regenerate/` | Regenerate a webhook secret | `webhooks:write` |
| V237 | `work-item-activities` | `list-activities.md` | GET | `{ws}/{P}/work-items/{work_item_id}/activities/` | List activities | `projects.work_items.activities:read` |
| V238 | `work-item-activities` | `get-activity.md` | GET | `{ws}/{P}/work-items/{work_item_id}/activities/{pk}/` | Get a activity | `projects.work_items.activities:read` |
| V239 | `work-item-attachments` | `list-attachments.md` | GET | `{ws}/{P}/work-items/{work_item_id}/attachments/` | List attachments | `projects.work_items.attachments:read` |
| V240 | `work-item-attachments` | `create-attachment-upload.md` | POST | `{ws}/{P}/work-items/{work_item_id}/attachments/` | Create a work item attachment upload | `projects.work_items.attachments:write` |
| V241 | `work-item-attachments` | `get-attachment.md` | GET | `{ws}/{P}/work-items/{work_item_id}/attachments/{pk}/` | Get a attachment | `projects.work_items.attachments:read` |
| V242 | `work-item-attachments` | `confirm-attachment-upload.md` | PATCH | `{ws}/{P}/work-items/{work_item_id}/attachments/{pk}/` | Confirm a work item attachment upload | `projects.work_items.attachments:write` |
| V243 | `work-item-attachments` | `delete-attachment.md` | DELETE | `{ws}/{P}/work-items/{work_item_id}/attachments/{pk}/` | Delete a attachment | `projects.work_items.attachments:write` |
| V244 | `work-item-comments` | `list-comments.md` | GET | `{ws}/{P}/work-items/{work_item_id}/comments/` | List comments | `projects.work_items.comments:read` |
| V245 | `work-item-comments` | `create-comment.md` | POST | `{ws}/{P}/work-items/{work_item_id}/comments/` | Create a comment | `projects.work_items.comments:write` |
| V246 | `work-item-comments` | `bulk-comments.md` | POST | `{ws}/{P}/work-items/{work_item_id}/comments/bulk/` | Bulk write comments | `projects.work_items.comments:write` |
| V247 | `work-item-comments` | `upsert-comment.md` | POST | `{ws}/{P}/work-items/{work_item_id}/comments/upsert/` | Upsert a comment | `projects.work_items.comments:write` |
| V248 | `work-item-comments` | `get-comment.md` | GET | `{ws}/{P}/work-items/{work_item_id}/comments/{pk}/` | Get a comment | `projects.work_items.comments:read` |
| V249 | `work-item-comments` | `update-comment.md` | PATCH | `{ws}/{P}/work-items/{work_item_id}/comments/{pk}/` | Update a comment | `projects.work_items.comments:write` |
| V250 | `work-item-comments` | `delete-comment.md` | DELETE | `{ws}/{P}/work-items/{work_item_id}/comments/{pk}/` | Delete a comment | `projects.work_items.comments:write` |
| V251 | `work-item-dependencies` | `list-work-item-dependencies.md` | GET | `{ws}/{P}/work-items/{work_item_id}/dependencies/` | List work item dependencies | `projects.work_items.relations:read` |
| V252 | `work-item-dependencies` | `create-work-item-dependencies.md` | POST | `{ws}/{P}/work-items/{work_item_id}/dependencies/` | Create work item dependencies | `projects.work_items.relations:write` |
| V253 | `work-item-dependencies` | `delete-work-item-dependency.md` | DELETE | `{ws}/{P}/work-items/{work_item_id}/dependencies/{related_work_item_id}/` | Delete a work item dependency | `projects.work_items.relations:write` |
| V254 | `work-item-links` | `list-links.md` | GET | `{ws}/{P}/work-items/{work_item_id}/links/` | List links | `projects.work_items.links:read` |
| V255 | `work-item-links` | `create-link.md` | POST | `{ws}/{P}/work-items/{work_item_id}/links/` | Create a link | `projects.work_items.links:write` |
| V256 | `work-item-links` | `get-link.md` | GET | `{ws}/{P}/work-items/{work_item_id}/links/{pk}/` | Get a link | `projects.work_items.links:read` |
| V257 | `work-item-links` | `update-link.md` | PATCH | `{ws}/{P}/work-items/{work_item_id}/links/{pk}/` | Update a link | `projects.work_items.links:write` |
| V258 | `work-item-links` | `delete-link.md` | DELETE | `{ws}/{P}/work-items/{work_item_id}/links/{pk}/` | Delete a link | `projects.work_items.links:write` |
| V259 | `work-item-properties` | `list-work-item-properties.md` | GET | `{ws}/{P}/work-item-properties/` | List work item properties | `projects.work_item_properties:read` |
| V260 | `work-item-properties` | `create-work-item-property.md` | POST | `{ws}/{P}/work-item-properties/` | Create a work item property | `projects.work_item_properties:write` |
| V261 | `work-item-properties` | `get-work-item-property.md` | GET | `{ws}/{P}/work-item-properties/{pk}/` | Get a work item property | `projects.work_item_properties:read` |
| V262 | `work-item-properties` | `update-work-item-property.md` | PATCH | `{ws}/{P}/work-item-properties/{pk}/` | Update a work item property | `projects.work_item_properties:write` |
| V263 | `work-item-properties` | `delete-work-item-property.md` | DELETE | `{ws}/{P}/work-item-properties/{pk}/` | Delete a work item property | `projects.work_item_properties:write` |
| V264 | `work-item-property-contexts` | `list-property-contexts.md` | GET | `{ws}/work-item-properties/{property_id}/contexts/` | List property contexts | `workspaces.work_item_properties:read` |
| V265 | `work-item-property-contexts` | `create-property-context.md` | POST | `{ws}/work-item-properties/{property_id}/contexts/` | Create a property context | `workspaces.work_item_properties:write` |
| V266 | `work-item-property-contexts` | `get-property-context.md` | GET | `{ws}/work-item-properties/{property_id}/contexts/{pk}/` | Get a property context | `workspaces.work_item_properties:read` |
| V267 | `work-item-property-contexts` | `update-property-context.md` | PATCH | `{ws}/work-item-properties/{property_id}/contexts/{pk}/` | Update a property context | `workspaces.work_item_properties:write` |
| V268 | `work-item-property-contexts` | `delete-property-context.md` | DELETE | `{ws}/work-item-properties/{property_id}/contexts/{pk}/` | Delete a property context | `workspaces.work_item_properties:write` |
| V269 | `work-item-property-options` | `list-property-options.md` | GET | `{ws}/{P}/work-item-properties/{property_id}/options/` | List property options | `projects.work_item_properties:read` |
| V270 | `work-item-property-options` | `create-property-option.md` | POST | `{ws}/{P}/work-item-properties/{property_id}/options/` | Create a property option | `projects.work_item_properties:write` |
| V271 | `work-item-property-options` | `get-property-option.md` | GET | `{ws}/{P}/work-item-properties/{property_id}/options/{pk}/` | Get a property option | `projects.work_item_properties:read` |
| V272 | `work-item-property-options` | `update-property-option.md` | PATCH | `{ws}/{P}/work-item-properties/{property_id}/options/{pk}/` | Update a property option | `projects.work_item_properties:write` |
| V273 | `work-item-property-options` | `delete-property-option.md` | DELETE | `{ws}/{P}/work-item-properties/{property_id}/options/{pk}/` | Delete a property option | `projects.work_item_properties:write` |
| V274 | `work-item-relation-definitions` | `list-relation-definitions.md` | GET | `{ws}/work-item-relation-definitions/` | List relation definitions | `workspaces.work_item_relation_definitions:read` |
| V275 | `work-item-relation-definitions` | `create-relation-definition.md` | POST | `{ws}/work-item-relation-definitions/` | Create a relation definition | `workspaces.work_item_relation_definitions:write` |
| V276 | `work-item-relation-definitions` | `get-relation-definition.md` | GET | `{ws}/work-item-relation-definitions/{pk}/` | Get a relation definition | `workspaces.work_item_relation_definitions:read` |
| V277 | `work-item-relation-definitions` | `update-relation-definition.md` | PATCH | `{ws}/work-item-relation-definitions/{pk}/` | Update a relation definition | `workspaces.work_item_relation_definitions:write` |
| V278 | `work-item-relation-definitions` | `delete-relation-definition.md` | DELETE | `{ws}/work-item-relation-definitions/{pk}/` | Delete a relation definition | `workspaces.work_item_relation_definitions:write` |
| V279 | `work-item-relations` | `list-work-item-relations.md` | GET | `{ws}/{P}/work-items/{work_item_id}/relations/` | List work item relations | `projects.work_items.relations:read` |
| V280 | `work-item-relations` | `create-work-item-relations.md` | POST | `{ws}/{P}/work-items/{work_item_id}/relations/` | Create work item relations | `projects.work_items.relations:write` |
| V281 | `work-item-relations` | `delete-work-item-relation.md` | DELETE | `{ws}/{P}/work-items/{work_item_id}/relations/{related_work_item_id}/` | Delete a work item relation | `projects.work_items.relations:write` |
| V282 | `work-item-type-properties` | `list-type-properties.md` | GET | `{ws}/{P}/work-item-types/{type_id}/properties/` | List type properties | `projects.work_item_types:read` |
| V283 | `work-item-type-properties` | `attach-type-property.md` | POST | `{ws}/{P}/work-item-types/{type_id}/properties/` | Attach a property to a type | `projects.work_item_types:write` |
| V284 | `work-item-type-properties` | `get-type-property.md` | GET | `{ws}/{P}/work-item-types/{type_id}/properties/{pk}/` | Get a type property | `projects.work_item_types:read` |
| V285 | `work-item-type-properties` | `detach-type-property.md` | DELETE | `{ws}/{P}/work-item-types/{type_id}/properties/{pk}/` | Detach a property from a type | `projects.work_item_types:write` |
| V286 | `work-item-types` | `list-work-item-types.md` | GET | `{ws}/{P}/work-item-types/` | List work item types | `projects.work_item_types:read` |
| V287 | `work-item-types` | `create-work-item-type.md` | POST | `{ws}/{P}/work-item-types/` | Create a work item type | `projects.work_item_types:write` |
| V288 | `work-item-types` | `enable-work-item-types.md` | POST | `{ws}/{P}/work-item-types/enable/` | Enable work item types | `projects.work_item_types:write` |
| V289 | `work-item-types` | `import-work-item-types.md` | POST | `{ws}/{P}/work-item-types/import/` | Import work item types | `projects.work_item_types:write` |
| V290 | `work-item-types` | `get-work-item-type.md` | GET | `{ws}/{P}/work-item-types/{pk}/` | Get a work item type | `projects.work_item_types:read` |
| V291 | `work-item-types` | `update-work-item-type.md` | PATCH | `{ws}/{P}/work-item-types/{pk}/` | Update a work item type | `projects.work_item_types:write` |
| V292 | `work-item-types` | `delete-work-item-type.md` | DELETE | `{ws}/{P}/work-item-types/{pk}/` | Delete a work item type | `projects.work_item_types:write` |
| V293 | `work-item-types` | `mark-default-work-item-type.md` | POST | `{ws}/{P}/work-item-types/{pk}/mark-default/` | Mark a work item type as default | `projects.work_item_types:write` |
| V294 | `work-item-types` | `get-work-item-type-schema.md` | GET | `{ws}/{P}/work-item-types/{pk}/schema/` | Get a work item type schema | `projects.work_item_types:read` |
| V295 | `work-item-worklogs` | `list-worklogs.md` | GET | `{ws}/{P}/work-items/{work_item_id}/worklogs/` | List worklogs | `projects.work_items.worklogs:read` |
| V296 | `work-item-worklogs` | `create-worklog.md` | POST | `{ws}/{P}/work-items/{work_item_id}/worklogs/` | Create a worklog | `projects.work_items.worklogs:write` |
| V297 | `work-item-worklogs` | `get-worklog.md` | GET | `{ws}/{P}/work-items/{work_item_id}/worklogs/{pk}/` | Get a worklog | `projects.work_items.worklogs:read` |
| V298 | `work-item-worklogs` | `update-worklog.md` | PATCH | `{ws}/{P}/work-items/{work_item_id}/worklogs/{pk}/` | Update a worklog | `projects.work_items.worklogs:write` |
| V299 | `work-item-worklogs` | `delete-worklog.md` | DELETE | `{ws}/{P}/work-items/{work_item_id}/worklogs/{pk}/` | Delete a worklog | `projects.work_items.worklogs:write` |
| V300 | `work-item-worklogs` | `get-project-worklog-summary.md` | GET | `{ws}/{P}/worklogs/summary/` | Get the project worklog summary | – |
| V301 | `work-items` | `list-workspace-work-items.md` | GET | `{ws}/work-items/` | List work items across a workspace | `projects.work_items:read` |
| V302 | `work-items` | `get-work-item-by-identifier.md` | GET | `{ws}/work-items/{identifier}/` | Get a work item by identifier | `projects.work_items:read` |
| V303 | `work-items` | `list-work-items.md` | GET | `{ws}/{P}/work-items/` | List work items | `projects.work_items:read` |
| V304 | `work-items` | `create-work-item.md` | POST | `{ws}/{P}/work-items/` | Create a work item | `projects.work_items:write` |
| V305 | `work-items` | `bulk-work-items.md` | POST | `{ws}/{P}/work-items/bulk/` | Bulk write work items | `projects.work_items:write` |
| V306 | `work-items` | `upsert-work-item.md` | POST | `{ws}/{P}/work-items/upsert/` | Upsert a work item | `projects.work_items:write` |
| V307 | `work-items` | `get-work-item.md` | GET | `{ws}/{P}/work-items/{pk}/` | Get a work item | `projects.work_items:read` |
| V308 | `work-items` | `update-work-item.md` | PATCH | `{ws}/{P}/work-items/{pk}/` | Update a work item | `projects.work_items:write` |
| V309 | `work-items` | `delete-work-item.md` | DELETE | `{ws}/{P}/work-items/{pk}/` | Delete a work item | `projects.work_items:write` |
| V310 | `work-items` | `archive-work-item.md` | POST | `{ws}/{P}/work-items/{pk}/archive/` | Archive a work item | `projects.work_items:write` |
| V311 | `work-items` | `unarchive-work-item.md` | POST | `{ws}/{P}/work-items/{pk}/unarchive/` | Unarchive a work item | `projects.work_items:write` |
| V312 | `workflow-states` | `list-workflow-states.md` | GET | `{ws}/{P}/workflows/{workflow_id}/states/` | List workflow states | `projects.workflows:read` |
| V313 | `workflow-states` | `create-workflow-state.md` | POST | `{ws}/{P}/workflows/{workflow_id}/states/` | Create a workflow state | `projects.workflows:write` |
| V314 | `workflow-states` | `get-workflow-state.md` | GET | `{ws}/{P}/workflows/{workflow_id}/states/{pk}/` | Get a workflow state | `projects.workflows:read` |
| V315 | `workflow-states` | `update-workflow-state.md` | PATCH | `{ws}/{P}/workflows/{workflow_id}/states/{pk}/` | Update a workflow state | `projects.workflows:write` |
| V316 | `workflow-states` | `delete-workflow-state.md` | DELETE | `{ws}/{P}/workflows/{workflow_id}/states/{pk}/` | Delete a workflow state | `projects.workflows:write` |
| V317 | `workflow-transitions` | `list-workflow-transitions.md` | GET | `{ws}/{P}/workflows/{workflow_id}/state-transitions/` | List workflow transitions | `projects.workflows:read` |
| V318 | `workflow-transitions` | `create-workflow-transition.md` | POST | `{ws}/{P}/workflows/{workflow_id}/state-transitions/` | Create a workflow transition | `projects.workflows:write` |
| V319 | `workflow-transitions` | `get-workflow-transition.md` | GET | `{ws}/{P}/workflows/{workflow_id}/state-transitions/{pk}/` | Get a workflow transition | `projects.workflows:read` |
| V320 | `workflow-transitions` | `update-workflow-transition.md` | PATCH | `{ws}/{P}/workflows/{workflow_id}/state-transitions/{pk}/` | Update a workflow transition | `projects.workflows:write` |
| V321 | `workflow-transitions` | `delete-workflow-transition.md` | DELETE | `{ws}/{P}/workflows/{workflow_id}/state-transitions/{pk}/` | Delete a workflow transition | `projects.workflows:write` |
| V322 | `workflows` | `list-workflows.md` | GET | `{ws}/{P}/workflows/` | List workflows | `projects.workflows:read` |
| V323 | `workflows` | `create-workflow.md` | POST | `{ws}/{P}/workflows/` | Create a workflow | `projects.workflows:write` |
| V324 | `workflows` | `get-workflow.md` | GET | `{ws}/{P}/workflows/{pk}/` | Get a workflow | `projects.workflows:read` |
| V325 | `workflows` | `update-workflow.md` | PATCH | `{ws}/{P}/workflows/{pk}/` | Update a workflow | `projects.workflows:write` |
| V326 | `workflows` | `delete-workflow.md` | DELETE | `{ws}/{P}/workflows/{pk}/` | Delete a workflow | `projects.workflows:write` |
| V327 | `workspace-assets` | `list-workspace-assets.md` | GET | `{ws}/assets/` | List workspace assets | `assets:read` |
| V328 | `workspace-assets` | `create-workspace-asset.md` | POST | `{ws}/assets/` | Create a workspace asset upload | `assets:write` |
| V329 | `workspace-assets` | `get-asset.md` | GET | `{ws}/assets/{pk}/` | Get a asset | `assets:read` |
| V330 | `workspace-assets` | `confirm-workspace-asset.md` | PATCH | `{ws}/assets/{pk}/` | Confirm a workspace asset upload | `assets:write` |
| V331 | `workspace-assets` | `delete-asset.md` | DELETE | `{ws}/assets/{pk}/` | Delete a asset | `assets:write` |
| V332 | `workspace-automations` | `list-workspace-automations.md` | GET | `{ws}/automations/` | List workspace automations | `automations:read` |
| V333 | `workspace-automations` | `create-workspace-automation.md` | POST | `{ws}/automations/` | Create a workspace automation | `automations:write` |
| V334 | `workspace-automations` | `list-automation-activities.md` | GET | `{ws}/automations/{automation_id}/activities/` | List automation activities | `automations:read` |
| V335 | `workspace-automations` | `get-automation-activity.md` | GET | `{ws}/automations/{automation_id}/activities/{pk}/` | Get a automation activity | `automations:read` |
| V336 | `workspace-automations` | `list-automation-edges.md` | GET | `{ws}/automations/{automation_id}/edges/` | List automation edges | `automations:read` |
| V337 | `workspace-automations` | `create-automation-edge.md` | POST | `{ws}/automations/{automation_id}/edges/` | Create a automation edge | `automations:write` |
| V338 | `workspace-automations` | `get-automation-edge.md` | GET | `{ws}/automations/{automation_id}/edges/{pk}/` | Get a automation edge | `automations:read` |
| V339 | `workspace-automations` | `update-automation-edge.md` | PATCH | `{ws}/automations/{automation_id}/edges/{pk}/` | Update a automation edge | `automations:write` |
| V340 | `workspace-automations` | `delete-automation-edge.md` | DELETE | `{ws}/automations/{automation_id}/edges/{pk}/` | Delete a automation edge | `automations:write` |
| V341 | `workspace-automations` | `list-automation-nodes.md` | GET | `{ws}/automations/{automation_id}/nodes/` | List automation nodes | `automations:read` |
| V342 | `workspace-automations` | `create-automation-node.md` | POST | `{ws}/automations/{automation_id}/nodes/` | Create a automation node | `automations:write` |
| V343 | `workspace-automations` | `get-automation-node.md` | GET | `{ws}/automations/{automation_id}/nodes/{pk}/` | Get a automation node | `automations:read` |
| V344 | `workspace-automations` | `update-automation-node.md` | PATCH | `{ws}/automations/{automation_id}/nodes/{pk}/` | Update a automation node | `automations:write` |
| V345 | `workspace-automations` | `delete-automation-node.md` | DELETE | `{ws}/automations/{automation_id}/nodes/{pk}/` | Delete a automation node | `automations:write` |
| V346 | `workspace-automations` | `regenerate-node-webhook-secret.md` | POST | `{ws}/automations/{automation_id}/nodes/{pk}/regenerate-webhook-secret/` | Regenerate an automation node webhook secret | `automations:write` |
| V347 | `workspace-automations` | `get-workspace-automation.md` | GET | `{ws}/automations/{pk}/` | Get a workspace automation | `automations:read` |
| V348 | `workspace-automations` | `update-workspace-automation.md` | PATCH | `{ws}/automations/{pk}/` | Update a workspace automation | `automations:write` |
| V349 | `workspace-automations` | `delete-workspace-automation.md` | DELETE | `{ws}/automations/{pk}/` | Delete a workspace automation | `automations:write` |
| V350 | `workspace-automations` | `set-workspace-automation-status.md` | POST | `{ws}/automations/{pk}/status/` | Enable or disable a workspace automation | `automations:write` |
| V351 | `workspace-features` | `get-workspace-features.md` | GET | `{ws}/features/` | Get workspace features | `workspaces.features:read` |
| V352 | `workspace-features` | `update-workspace-features.md` | PATCH | `{ws}/features/` | Update workspace features | `workspaces.features:write` |
| V353 | `workspace-pages` | `list-workspace-pages.md` | GET | `{ws}/pages/` | List workspace pages | `wiki.pages:read` |
| V354 | `workspace-pages` | `create-workspace-page.md` | POST | `{ws}/pages/` | Create a workspace page | `wiki.pages:write` |
| V355 | `workspace-pages` | `get-workspace-page.md` | GET | `{ws}/pages/{pk}/` | Get a workspace page | `wiki.pages:read` |
| V356 | `workspace-pages` | `update-workspace-page.md` | PATCH | `{ws}/pages/{pk}/` | Update a workspace page | `wiki.pages:write` |
| V357 | `workspace-pages` | `delete-workspace-page.md` | DELETE | `{ws}/pages/{pk}/` | Delete a workspace page | `wiki.pages:write` |
| V358 | `workspace-views` | `list-workspace-views.md` | GET | `{ws}/views/` | List workspace views | `workspaces.views:read` |
| V359 | `workspace-views` | `create-workspace-view.md` | POST | `{ws}/views/` | Create a workspace view | `workspaces.views:write` |
| V360 | `workspace-views` | `get-workspace-view.md` | GET | `{ws}/views/{pk}/` | Get a workspace view | `workspaces.views:read` |
| V361 | `workspace-views` | `update-workspace-view.md` | PATCH | `{ws}/views/{pk}/` | Update a workspace view | `workspaces.views:write` |
| V362 | `workspace-views` | `delete-workspace-view.md` | DELETE | `{ws}/views/{pk}/` | Delete a workspace view | `workspaces.views:write` |
| V363 | `workspace-work-item-properties` | `list-workspace-work-item-properties.md` | GET | `{ws}/work-item-properties/` | List workspace work item properties | `workspaces.work_item_properties:read` |
| V364 | `workspace-work-item-properties` | `create-workspace-work-item-property.md` | POST | `{ws}/work-item-properties/` | Create a workspace work item property | `workspaces.work_item_properties:write` |
| V365 | `workspace-work-item-properties` | `get-workspace-work-item-property.md` | GET | `{ws}/work-item-properties/{pk}/` | Get a workspace work item property | `workspaces.work_item_properties:read` |
| V366 | `workspace-work-item-properties` | `update-workspace-work-item-property.md` | PATCH | `{ws}/work-item-properties/{pk}/` | Update a workspace work item property | `workspaces.work_item_properties:write` |
| V367 | `workspace-work-item-properties` | `delete-workspace-work-item-property.md` | DELETE | `{ws}/work-item-properties/{pk}/` | Delete a workspace work item property | `workspaces.work_item_properties:write` |
| V368 | `workspace-work-item-property-options` | `list-workspace-property-options.md` | GET | `{ws}/work-item-properties/{property_id}/options/` | List workspace property options | `workspaces.work_item_properties:read` |
| V369 | `workspace-work-item-property-options` | `create-workspace-property-option.md` | POST | `{ws}/work-item-properties/{property_id}/options/` | Create a workspace property option | `workspaces.work_item_properties:write` |
| V370 | `workspace-work-item-property-options` | `get-workspace-property-option.md` | GET | `{ws}/work-item-properties/{property_id}/options/{pk}/` | Get a workspace property option | `workspaces.work_item_properties:read` |
| V371 | `workspace-work-item-property-options` | `update-workspace-property-option.md` | PATCH | `{ws}/work-item-properties/{property_id}/options/{pk}/` | Update a workspace property option | `workspaces.work_item_properties:write` |
| V372 | `workspace-work-item-property-options` | `delete-workspace-property-option.md` | DELETE | `{ws}/work-item-properties/{property_id}/options/{pk}/` | Delete a workspace property option | `workspaces.work_item_properties:write` |
| V373 | `workspace-work-item-templates` | `list-workspace-work-item-templates.md` | GET | `{ws}/work-item-templates/` | List workspace work item templates | `templates.work_items:read` |
| V374 | `workspace-work-item-templates` | `create-workspace-work-item-template.md` | POST | `{ws}/work-item-templates/` | Create a workspace work item template | `templates.work_items:write` |
| V375 | `workspace-work-item-templates` | `get-workspace-work-item-template.md` | GET | `{ws}/work-item-templates/{pk}/` | Get a workspace work item template | `templates.work_items:read` |
| V376 | `workspace-work-item-templates` | `update-workspace-work-item-template.md` | PATCH | `{ws}/work-item-templates/{pk}/` | Update a workspace work item template | `templates.work_items:write` |
| V377 | `workspace-work-item-templates` | `delete-workspace-work-item-template.md` | DELETE | `{ws}/work-item-templates/{pk}/` | Delete a workspace work item template | `templates.work_items:write` |
| V378 | `workspace-work-item-type-properties` | `list-workspace-type-properties.md` | GET | `{ws}/work-item-types/{type_id}/properties/` | List properties on a workspace type | `workspaces.work_item_types:read` |
| V379 | `workspace-work-item-type-properties` | `attach-workspace-type-property.md` | POST | `{ws}/work-item-types/{type_id}/properties/` | Attach properties to a workspace type | `workspaces.work_item_types:write` |
| V380 | `workspace-work-item-type-properties` | `get-workspace-type-property.md` | GET | `{ws}/work-item-types/{type_id}/properties/{pk}/` | Get a property on a workspace type | `workspaces.work_item_types:read` |
| V381 | `workspace-work-item-type-properties` | `detach-workspace-type-property.md` | DELETE | `{ws}/work-item-types/{type_id}/properties/{pk}/` | Detach a property from a workspace type | `workspaces.work_item_types:write` |
| V382 | `workspace-work-item-types` | `list-workspace-work-item-types.md` | GET | `{ws}/work-item-types/` | List workspace work item types | `workspaces.work_item_types:read` |
| V383 | `workspace-work-item-types` | `create-workspace-work-item-type.md` | POST | `{ws}/work-item-types/` | Create a workspace work item type | `workspaces.work_item_types:write` |
| V384 | `workspace-work-item-types` | `get-workspace-work-item-type.md` | GET | `{ws}/work-item-types/{pk}/` | Get a workspace work item type | `workspaces.work_item_types:read` |
| V385 | `workspace-work-item-types` | `update-workspace-work-item-type.md` | PATCH | `{ws}/work-item-types/{pk}/` | Update a workspace work item type | `workspaces.work_item_types:write` |
| V386 | `workspace-work-item-types` | `delete-workspace-work-item-type.md` | DELETE | `{ws}/work-item-types/{pk}/` | Delete a workspace work item type | `workspaces.work_item_types:write` |
| V387 | `workspace-work-item-types` | `mark-default-workspace-work-item-type.md` | POST | `{ws}/work-item-types/{pk}/mark-default/` | Mark a workspace work item type as default | `workspaces.work_item_types:write` |

---

## 10. Page-API-Erweiterung v1 (Branch `docs-page-update-api`) – im Verifikationslauf ergänzt

Der Branch `docs-page-update-api` (Commit `1c6e554`, 20.08.2026) erweitert die v1-Referenz um Schreib-, Archiv- und Attachment-Endpunkte für Seiten sowie die Collections-Ressource. 36 Endpunkte, davon 26 nicht im Stand `AR/` (Abgleich per Skript über Methode + normalisierten Pfad). Felder, Statuscodes und Regeln (z. B. Löschen nur archivierter Seiten → sonst 400; Restore = `DELETE …/archive/`, 400 bei archiviertem Parent; `PUT` wirkt auf das kollaborative Dokument, 502/503 bei Fehler des Collaborative-Service; Collection-`access` 0/1/2; `DELETE collections/{id}/?archive_pages=true|false`; `PATCH …/pages/{page_collection_id}/` mit `placement` `append`/`before`/`after`) sind in `migration/features/26-paid-wissen-pages-wiki.md` (Quellen G1–G15, Kap. 3.2/3.3/3.45) spezifiziert und werden hier nicht dupliziert. Feature: F33 (Kap. 3). CE: keine Public-API für Seiten; Projektseiten-Funktionen nur in der internen App-API (`apps/api/plane/app/urls/page.py`).

| # | Datei (`PU/…`) | Methode | Pfad (relativ zu `/api/v1/workspaces/{workspace_slug}/`) | in `AR/` (master)? |
|---|---|---|---|---|
| PU1 | `page/add-project-page.md` | POST | `projects/{project_id}/pages/` | ja |
| PU2 | `page/add-workspace-page.md` | POST | `pages/` | ja |
| PU3 | `page/archive-project-page.md` | POST | `projects/{project_id}/pages/{page_id}/archive/` | **nein** (neu) |
| PU4 | `page/archive-workspace-page.md` | POST | `pages/{page_id}/archive/` | **nein** (neu) |
| PU5 | `page/confirm-workspace-page-attachment-upload.md` | PATCH | `pages/{page_id}/attachments/{attachment_id}/` | **nein** (neu) |
| PU6 | `page/delete-project-page.md` | DELETE | `projects/{project_id}/pages/{page_id}/` | **nein** (neu) |
| PU7 | `page/delete-workspace-page-attachment.md` | DELETE | `pages/{page_id}/attachments/{attachment_id}/` | **nein** (neu) |
| PU8 | `page/delete-workspace-page.md` | DELETE | `pages/{page_id}/` | **nein** (neu) |
| PU9 | `page/download-workspace-page-attachment.md` | GET | `pages/{page_id}/attachments/{attachment_id}/download/` | **nein** (neu) |
| PU10 | `page/get-project-page.md` | GET | `projects/{project_id}/pages/{page_id}/` | ja |
| PU11 | `page/get-workspace-page-attachment.md` | GET | `pages/{page_id}/attachments/{attachment_id}/` | **nein** (neu) |
| PU12 | `page/get-workspace-page.md` | GET | `pages/{page_id}/` | ja |
| PU13 | `page/list-project-pages.md` | GET | `projects/{project_id}/pages/` | ja |
| PU14 | `page/list-workspace-pages.md` | GET | `pages/` | ja |
| PU15 | `page/restore-project-page.md` | DELETE | `projects/{project_id}/pages/{page_id}/archive/` | **nein** (neu) |
| PU16 | `page/restore-workspace-page.md` | DELETE | `pages/{page_id}/archive/` | **nein** (neu) |
| PU17 | `page/update-project-page.md` | PUT | `projects/{project_id}/pages/{page_id}/` | **nein** (neu) |
| PU18 | `page/update-workspace-page.md` | PUT | `pages/{page_id}/` | **nein** (neu) |
| PU19 | `collection/add-collection-member.md` | POST | `collections/{collection_id}/members/` | **nein** (neu) |
| PU20 | `collection/add-collection-pages.md` | POST | `collections/{collection_id}/pages/` | **nein** (neu) |
| PU21 | `collection/create-collection.md` | POST | `collections/` | **nein** (neu) |
| PU22 | `collection/delete-collection.md` | DELETE | `collections/{collection_id}/` | **nein** (neu) |
| PU23 | `collection/list-collection-members.md` | GET | `collections/{collection_id}/members/` | **nein** (neu) |
| PU24 | `collection/list-collection-pages.md` | GET | `collections/{collection_id}/pages/` | **nein** (neu) |
| PU25 | `collection/list-collections.md` | GET | `collections/` | **nein** (neu) |
| PU26 | `collection/move-or-reorder-collection-page.md` | PATCH | `collections/{collection_id}/pages/{page_collection_id}/` | **nein** (neu) |
| PU27 | `collection/remove-collection-member.md` | DELETE | `collections/{collection_id}/members/{member_id}/` | **nein** (neu) |
| PU28 | `collection/remove-collection-page.md` | DELETE | `collections/{collection_id}/pages/{page_collection_id}/` | **nein** (neu) |
| PU29 | `collection/retrieve-collection.md` | GET | `collections/{collection_id}/` | **nein** (neu) |
| PU30 | `collection/search-collection-pages.md` | GET | `collections/{collection_id}/pages-search/` | **nein** (neu) |
| PU31 | `collection/update-collection-member.md` | PATCH | `collections/{collection_id}/members/{member_id}/` | **nein** (neu) |
| PU32 | `collection/update-collection.md` | PATCH | `collections/{collection_id}/` | **nein** (neu) |
| PU33 | `work-item-pages/add-work-item-page.md` | POST | `projects/{project_id}/work-items/{work_item_id}/pages/` | ja |
| PU34 | `work-item-pages/delete-work-item-page.md` | DELETE | `projects/{project_id}/work-items/{work_item_id}/pages/{page_id}/` | ja |
| PU35 | `work-item-pages/get-work-item-page-detail.md` | GET | `projects/{project_id}/work-items/{work_item_id}/pages/{page_id}/` | ja |
| PU36 | `work-item-pages/list-work-item-pages.md` | GET | `projects/{project_id}/work-items/{work_item_id}/pages/` | ja |

---

## Verifikations-Protokoll

Verifikationslauf vom 22.10.2026 (Skeptiker/Verifizierer Cluster P02). Geprüft wurden (a) jede Tier-Zuordnung gegen `apps/web/components/workspace/billing/comparison/plans.tsx`, `packages/constants/src/subscription.ts`, die Schwester-Dokumente `migration/features/20-*.md` bis `28-*.md` und gezielte WebSearch-Abfragen, (b) jeder CE-Status per `grep`/Lesen im Repo `/home/user/plane`, (c) die Vollständigkeit des Clusters gegen alle erreichbaren Fassungen der Developer-Docs, (d) Beschreibungen auf unbelegte oder übertriebene Aussagen. Korrekturen sind direkt im Text eingearbeitet und mit „korrigiert“ bzw. „Verifikationslauf“ markiert.

### V.1 Nachgezählte Kennzahlen

| Aussage | Prüfung | Ergebnis |
|---|---|---|
| 270 Dateien in `AR/` | `find AR -name "*.md" \| wc -l` | bestätigt (270) |
| „33 Ressourcen-Ordner“ | `ls -d AR/*/ \| wc -l` | **falsch: 32** (korrigiert in Q1 und Kap. 1.4) |
| 231 distinkte Endpunkte ohne S3-Upload | Skript über alle `api-endpoint-badge`-Blöcke inkl. `issue-types/*/`: 234 Badges, 2 Dubletten (`GET …/values/` als „List“ und „Get“, `PATCH …/attachments/{id}/` doppelt), 1 S3-Upload | bestätigt (231) |
| Aufteilung 94 CE / 9 CE-teilweise / 123 EE-only / 5 entfällt | Summenprüfung der Teilzahlen und Dateizahlen je Ordner (z. B. `customer/` 22 Dateien − Overview = 21, `initiative/` 19, `teamspace/` 11, `idp-group-sync/` 12) | bestätigt |
| Estimate-API im CE nicht geroutet | `apps/api/plane/api/urls/__init__.py` importiert 12 Module ohne `estimate` | bestätigt |
| CE ohne OAuth-Provider und ohne v2 | `apps/api/plane/urls.py:19-24` | bestätigt |

### V.2 WebSearch-Abfragen (11 von 15 erlaubten)

| # | Abfrage | Befund (Such-Zusammenfassung) | Wirkung |
|---|---|---|---|
| S1 | Plane API v2 developers.plane.so api-reference v2 introduction | kein v2-Treffer; Treffer `https://docs.plane.com/reference/introduction.md` (Basis-URL `https://api.plane.com`) und `https://university.plane.so/courses/202-the-power-relay/09-intro-to-plane-api.html` | O18 (v2-Verfügbarkeit UNVERIFIZIERT); Hinweis auf neue Domain `plane.com` (nicht weiter belegt) |
| S2 | Plane initiatives plan Pro Business university.plane.so intro to initiatives | nur themenfremde Treffer | keine |
| S3 | docs.plane.so group sync IdP Enterprise Grid plan | Seite https://docs.plane.so/authentication/group-sync mit Tag „Enterprise Grid“; nur Self-hosted Commercial, nur OIDC; Sync on login an, Offline-Sync (6 h) und Auto remove aus; https://plane.so/blog/introducing-enterprise-grid (12.06.2026) „on top of everything in Business“; https://developers.plane.so/api-reference/idp-group-sync/overview | F12 → Enterprise Grid |
| S4 | Plane custom relations … plan Business docs.plane.so | https://docs.plane.so/work-items/custom-relations mit Label „Enterprise Grid“; Workspace Settings → Relations → „Add relation“ (Title, Inward name); Forum-Thread 274: Relation-Definition-Endpunkte 404 auf CE | F22 → Enterprise Grid |
| S5 | Plane "formula" property work item type plan | https://plane.so/blog/introducing-releases (13.05.2026): Release picker und Formula als „advanced custom properties“, ab Pro; https://docs.plane.so/work-item-types „Pro“, Typen im Enterprise Grid auf Workspace-Ebene | F10 → Pro (mittel); F43 bestätigt |
| S6 | docs.plane.so initiatives Pro plan enable initiatives … sub-initiatives | https://docs.plane.so/core-concepts/projects/initiatives: Workspace settings → Initiatives → „Enable Initiatives“, danach Sidebar-Eintrag unter „Workspace“; University-Kurs 05: Pro; Sub-Initiativen nicht gefunden | F02 Pro bestätigt; Sub-Initiativen UNVERIFIZIERT; Zuordnung „University = Business“ zum Kurs 05 war falsch |
| S7 | Plane project labels workspace settings projects plan | https://docs.plane.so/core-concepts/projects/project-labels: Workspace Settings → Projects → „Project labels“, Name + Farbe, Gruppierung nach Label mit „No Label“; kein Plan genannt | F18: Projekt-Labels Tier unklar |
| S8 | Plane agents build your own app OAuth application plan … | https://developers.plane.so/dev-tools/build-plane-app: Apps „beta“, Bot-Token- und User-Token-Flow, Registrierung unter Workspace Settings → Integrations → „Build your own“; https://github.com/makeplane/plane/issues/8782: OAuth-App-Endpunkte nur Cloud, nicht CE | F30/F31: „Commercial Edition, Beta“, Tier unklar |
| S9 | "api/v2" Plane REST API problem+json X-Api-Key | nur v1-Treffer (https://developers.plane.so/api-reference/introduction, https://docs.plane.so/apis/introduction, https://docs.plane.com/reference/errors) | O18 |
| S10 | docs.plane.so milestones project feature Pro plan … | https://docs.plane.so/core-concepts/projects/milestones mit Label „Pro“; University-Kurs 07 „Pro-tier feature“; Fortschritt aus verknüpften Work Items (completed oder cancelled), Timeline als gestrichelte Linien | F06 → Pro |
| S11 | docs.plane.so releases Business plan enable releases | https://docs.plane.so/releases; https://docs.plane.so/projects/project-releases mit Titel „Project Releases Business“; Owner/Admins verwalten, Mitglieder sehen; Deaktivieren behält Daten; Projekt-Releases pro Projekt | F24 → Business; O19 |

### V.3 Quellenstand der Developer-Docs

| Fassung | Pfad | Commit / Datum | Inhalt |
|---|---|---|---|
| `master` (Offline, Primärquelle des Autors) | `/home/user/makeplane/developer-docs` | `1fe7033` / 01.09.2026 | nur API v1 (`AR/`) |
| `docs/api-reference-v2` | `V2/` | `b89c72c` / 11.08.2026 | API v2, 463 Dateien (Kap. 9) |
| `docs-page-update-api` | `PU/` | `1c6e554` / 20.08.2026 | v1-Pages/Collections-Erweiterung, 46 Dateien (Kap. 10) |

Die Branch-Klone lagen bereits im Scratchpad (angelegt im Lauf zu Dok. 26/28); im Verifikationslauf wurden sie nur gelesen.

### V.4 Korrekturen (vorher → nachher)

| # | Stelle | vorher | nachher | Beleg |
|---|---|---|---|---|
| K01 | Q1, Kap. 1.4 | 33 Ressourcen-Ordner | 32 | V.1 |
| K02 | F02 Initiatives CE-Status | fehlt | Stub/UI-Hülle im CE | `apps/web/store/theme.store.ts:20,32,181-187`; `packages/types/src/enums.ts:72`; Dok. 20 PF-15, Dok. 23 WM-11 |
| K03 | F02 Tier-Konflikt | „Business laut Plane University“ mit Kurs 05 als Beleg | Kurs 05 = Pro; Business stammt von einer anderen University-Seite; Sub-Initiativen UNVERIFIZIERT | S6; Dok. 23 WP-13 |
| K04 | F05 Teamspaces Abstufung | „Pro: Basic; Business/Enterprise: Advanced“ | entfernt (in keiner Quelle belegt); Teamspace Cycles ab Business | `plans.tsx` (keine Teamspaces-Zeile), `plans.tsx:381-390` |
| K05 | F06 Milestones Tier | unklar | Pro | S10; Dok. 23 WP-07 |
| K06 | F07 Time Tracking Tier | One | Pro (One historisch „Basic“, nicht mehr erhältlich) | Doku-Label „Pro“ (Dok. 23 WP-10); `base.tsx:29-30` |
| K07 | F09 Custom Properties CE-Status | fehlt | Stub/UI-Hülle im CE | `issue-modal-context.tsx:14-74`; `provider.tsx:43`; `activity/base.ts:87` |
| K08 | F10 Formula Tier und Beleg | unklar (Business/Enterprise) mit Beleg „Databases + Formulas“ | Pro (mittel); „Databases + Formulas“ betrifft Pages (`plans.tsx:909-919`, Sektion `knowledge-management`) | S5 |
| K09 | F12 IdP Group Sync | Tier unklar; CE „Stub/UI-Hülle“ | Enterprise Grid; CE „fehlt“ (nur i18n + Illustration) | S3; `grep group_sync` nur Locale-Treffer; Dok. 20 PF-98 |
| K10 | F13 Work-Item↔Page-Links Tier | One | Pro (One historisch) | Dok. 26 P07-13; `base.tsx:29-30` |
| K11 | F14 Wiki Tier | „One bzw. Pro“ | Pro | `wiki.json:89-91`; `subscription.ts:30`; Dok. 20 PF-74; Dok. 26 P07-01 |
| K12 | F14 Pages-API | „Public-API bietet kein Update/Delete/Archive/Lock“ | gilt nur für `master`; Branch `PU/` und v2 bieten Update/Delete/Archive/Restore | Kap. 10; Kap. 9 |
| K13 | F15 Shared Pages | Tier unklar; CE fehlt | Business; CE Stub (`isPageSharingEnabled: false`) | Dok. 26 P07-16; `apps/web/hooks/use-page-flag.ts:12-22` |
| K14 | F18 Project Grouping CE-Status | Stub/UI-Hülle (i18n) | fehlt (nur i18n); Projekt-Labels Tier unklar | grep; S7; Dok. 23 WM-37/38 |
| K15 | F19 Project Templates CE-Beleg | „(i18n)“ | Prop `templateId` in `create-project-modal.tsx:27,36,82` | Repo |
| K16 | F22 Custom Relations Tier | unklar | Enterprise Grid | S4 |
| K17 | F23 Member-Remove | Tier „Cloud-only“; CE „fehlt“; Body undokumentiert | Tier unklar (Commercial-API, Seats auch Self-hosted); CE „teilweise“ (interne App-API mit gleicher Logik); Body `email`*, `remove_seat` | `apps/api/plane/app/views/workspace/member.py:138-176`; `V2/members/remove-workspace-member.md` |
| K18 | F24 Releases Tier | unklar | Business | S11; Dok. 23 WP-08 |
| K19 | F25 PQL CE-Status | fehlt | Stub/UI-Hülle im CE (400-Ablehnung von `pql`/`filters`) | `apps/api/plane/api/views/issue.py:324-335`; Dok. 20 PF-52 |
| K20 | F27 Updates Tier | unklar | Pro (schwacher Beleg) | `plans.tsx:354-366` (auskommentiert); Dok. 20 PF-23; Dok. 23 WM-40 |
| K21 | F29 PI Tier | unklar | Pro (niedrig) | Dok. 20 PF-82 |
| K22 | Kap. 2.10 W1 | ohne CE-Abweichung | CE lehnt `pql`/`filters` mit 400 ab | wie K19 |
| K23 | Kap. 2.13 M7 | Body undokumentiert; CE-Logik nicht erwähnt | Body aus v2; CE-interne Route | wie K17 |
| K24 | Kap. 4.7 `settings` | „u. a. `display_format`“ | „dokumentierter Schlüssel `display_format`, weitere nicht dokumentiert“ | `AR/issue-types/properties/overview.md`; `DD/dev-tools/mcp-server-tools.md:511` |
| K25 | Kap. 4.1 Migrationshinweis | „mappt `state_id→state` usw.“ | vollständige Mapping-Liste | Datenmodell-Tabelle 4.1 |
| K26 | Kap. 8 O1, O2, O3, O4, O7, O8, O15 | offen | teilweise bzw. vollständig durch v2 geklärt | Kap. 9 |

### V.5 Bestätigte Aussagen (Stichproben mit Repo-Beleg)

| Aussage | Beleg |
|---|---|
| CE-Paginator Default/Max 1000, Überschreitung → `ParseError` | `apps/api/plane/utils/paginator.py:643-653` |
| `Project.is_time_tracking_enabled` existiert ohne Worklog-Modell | `apps/api/plane/db/models/project.py:100`; `apps/api/plane/api/serializers/project.py:94`; einziger „worklog“-Treffer in `apps/api/plane/db/models/` ist die Export-Choice in `exporter.py` |
| CE-Rollen 20/15/5 | `apps/api/plane/db/models/workspace.py:19`; `apps/api/plane/db/models/project.py:21` |
| Initiative-Spuren im CE | `apps/web/store/theme.store.ts:20-187`; `apps/api/plane/utils/constants.py:47-48`; `packages/constants/src/workspace.ts:54-55`; `packages/blocks/src/empty-state/assets/asset-types.ts:55` |
| Webhook-Logs im CE intern vorhanden | `apps/api/plane/app/urls/webhook.py`; `apps/api/plane/db/models/webhook.py:65` |
| OAuth-Apps nicht in CE | `DD/dev-tools/mcp-server-self-host.md:18-21`; keine `/auth/o/`-Route in `apps/api/plane/urls.py` |

### V.6 Dokumentierte Widersprüche zwischen Quellen

| Thema | Quelle A | Quelle B | Entscheidung |
|---|---|---|---|
| Time Tracking | `plans.tsx:183-191` One „Basic“ | Doku „Pro“ | Pro (aktueller; One nicht erhältlich) |
| Wiki | `plans.tsx:865-874` One | Upsell-Text, `PRO_PLAN_FEATURES`, Doku „Pro“ | Pro |
| Link-to-work-items | `plans.tsx:842-851` One | Changelog „Pro“ (Dok. 26) | Pro |
| Shared Pages | `wiki.json:91` „with Plane Pro“ | Doku „Business plan and above“ (Dok. 26) | Business |
| Initiatives | `plans.tsx`, University-Kurs 05: Pro | andere University-Seite: Business | Pro |
| Customers | University 202, Launch-Blog: Business | frühere Pricing-Zusammenfassung „Pro customer profiles“ (UNVERIFIZIERT, Dok. 20 K01) | Business |
| Workspace-Level Typen/Properties | `plans.tsx:222` Business | Doku/Plane Compose: Enterprise Grid | Enterprise Grid für den Workspace-Modus (F43); Workspace-Properties (F40) Business mit Konflikt |
| Audit-Log-API | `plans.tsx:751-760` Business | WebSearch „Enterprise Grid API audit logs“ (Dok. 20 PF-59) | Business (Matrix), Konflikt offen |
| Time Tracking CE-Status | Dok. 21/23: teilweise | Dok. 20 PF-03: Stub | teilweise (Flag in Modell und Public-API-Serializer, `apps/api/plane/api/serializers/project.py:94`) |
| Intake-E-Mail CE-Status | Dok. 21: teilweise | Dok. 20 PF-37, Dok. 23 WM-46: Stub | teilweise (Modellfeld `source_email`) |

### V.7 Ergänzungen

| # | Ergänzung | Ort |
|---|---|---|
| E01 | Quellen Q13–Q15, Kürzel `V2/`, `PU/`, Quellenstand | Kopf, Kap. 1.1 |
| E02 | Doku-Inkonsistenzen D22–D28 | Kap. 1.3 |
| E03 | Kennzahlen v2 und Page-Branch | Kap. 1.4 |
| E04 | Features F32–F43 (Public API v2, Page-API-Erweiterungen, Audit-Log-API, Automations-API, Views-API, Work-Item-Templates-API, Webhooks-API v2, Dependencies-API, Property Contexts, Artifacts, Workflows-API, Workspace-Mode für Typen) | Kap. 3 |
| E05 | v2-Feature-Flags (Workspace/Projekt) | Kap. 4.11 |
| E06 | v2-Präzisierungen zu Initiatives, Customers, Teamspaces, Milestones, Worklogs, Work Item Types, Group Sync, Custom Relations, Releases | Kap. 4 |
| E07 | v2-Scopes, globale Scopes, Token-Klassen | Kap. 6 |
| E08 | offene Punkte O16–O19 | Kap. 8 |
| E09 | Kap. 9 API v2 (Status, Konventionen, 67 Ressourcen, 387 Endpunkte) | Kap. 9 |
| E10 | Kap. 10 Page-API-Branch (36 Endpunkte) | Kap. 10 |
| E11 | Finale Feature-Liste: 43 Einträge (30 Autoren-Einträge korrigiert, F15 „Geteilte private Seiten“ als eigener Eintrag nachgetragen – fehlte in der Autoren-JSON –, 12 neue Einträge F32–F43) | `migration/features/_data/P02.paid.json` |
| E12 | Doku-Inkonsistenz D29 (Automation-Overview) | Kap. 1.3 |

### V.8 Restunsicherheiten

- Alle Web-Befunde sind Suchmaschinen-Zusammenfassungen; die Seiten selbst waren nicht abrufbar (Konfidenz höchstens „mittel“ für reine Web-Belege).
- Ob der v2-Branch dem ausgelieferten Produkt entspricht, ist nicht belegt (O18).
- Tier offen: Agent Runs, OAuth-Apps, Artifacts, Projekt-Labels, API v2, Views-API, Webhooks-API, Member-Remove.
- Sub-Initiativen: kein Beleg.
