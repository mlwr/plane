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

Dieses Dokument inventarisiert **vollständig** die öffentliche REST-API der Commercial Edition (Plane Cloud / Commercial Self-hosted), wie sie in den offline vorliegenden Developer-Docs beschrieben ist (`AR/`, 270 Markdown-Dateien, alle gelesen), gleicht **jeden** Endpunkt gegen die CE-Public-API (`apps/api/plane/api/urls/`, `apps/api/plane/api/views/`, `apps/api/plane/api/serializers/`) ab und extrahiert für jede Ressource, die nur in den Bezahl-Editionen existiert, das Datenmodell (Felder/Typen/Enums), Endpunkte, Berechtigungen (OAuth-Scopes, Rollen), Pagination und – soweit belegbar – UI/Verhalten. Da der Code der Commercial Edition closed-source ist, ist die API-Referenz die **Primärquelle für das Datenmodell der Bezahl-Features**; ergänzend wurden herangezogen:

| # | Quelle | Pfad / URL | Umfang | Verwendung |
|---|---|---|---|---|
| Q1 | REST-API-Referenz | `AR/` (33 Ressourcen-Ordner + `introduction.md`) | 270 Dateien, vollständig gelesen | Endpunkte, Felder, Scopes |
| Q2 | OAuth-Scope-Liste | `DD/dev-tools/build-plane-app/oauth-scopes.md` | vollständig | Scope-Inventar (Kap. 6) |
| Q3 | MCP-Server-Tool-Referenz (28 Tools, 183 Actions) | `DD/dev-tools/mcp-server-tools.md` | vollständig | Präzisierung von Parametern, Enums, Verhalten, die in Q1 fehlen (z. B. Body der `remove`-Endpunkte, Customer-Stage-Werte, Formula/Release-Property-Typen, Releases) |
| Q4 | Editions-Erklärung | `DD/self-hosting/editions-and-versions.md` | vollständig | CE ↔ Commercial-Abgrenzung |
| Q5 | Advanced Search / OpenSearch | `DD/self-hosting/govern/advanced-search.md` | gelesen | Plan-Badge „Pro“, Funktionsumfang |
| Q6 | Plan-Badges in Self-Hosting-Docs | `DD/self-hosting/govern/*.md` (`<Badge …>`) | per grep | Plan-Zuordnung (Intake-Email = Business, LDAP = Enterprise Grid, Integrationen = Pro) |
| Q7 | CE-Plan-Vergleichstabelle (im CE-Repo enthalten!) | `apps/web/components/workspace/billing/comparison/plans.tsx` | gelesen | Plan-Abstufungen Free/One/Pro/Business/Enterprise |
| Q8 | CE-Plan-Feature-Listen | `packages/constants/src/subscription.ts` | gelesen | Plan-Abstufungen |
| Q9 | CE-i18n mit EE-Texten | `packages/i18n/src/locales/en/*.json` (u. a. `workspace-settings.json`, `project-settings.json`, `work-item-type.json`, `wiki.json`, `template.json`, `workflow.json`, `update.json`, `empty-state.json`) | gezielt gelesen | UI-Texte der Bezahl-Features (für 1:1-UI) |
| Q10 | CE-Leer-Zustands-Illustrationen für EE-Features | `packages/blocks/src/empty-state/assets/{horizontal-stack,vertical-stack}/*.tsx` | Dateiliste | UI-Assets (customer, initiative, teamspace, milestone, worklog, group-syncing, custom-properties, property, epic, template, workflow, changelog, update) |
| Q11 | Helm-Chart Commercial | `HC/plane-enterprise/templates/workloads/*.yaml`, `HC/plane-enterprise/Chart.yaml` (`appVersion: "3.3.3"`) | Dateiliste | Dienste der Commercial Edition (`external-api`, `opensearch`, `pi-api`, `silo`, `automation-consumer`, `outbox-poller` …) |
| Q12 | WebSearch-Snippets | siehe jeweilige Abschnitte | punktuell | Plan-Zuordnung, UI-Verhalten |

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

### 1.4 Ergebnis in Zahlen

| Kennzahl | Wert | Quelle |
|---|---|---|
| Dokumentierte Ressourcen-Ordner | 33 (+ `introduction.md`) | `AR/` |
| Dokumentierte, distinkte Endpunkte (Methode + Pfad, ohne S3-Upload) | 231 | Kap. 2 |
| davon **CE** / **CE (abweichend)** | 94 | Kap. 2 (Assets 6, Cycles 12, Intake 5, Work Items 7, Activity 2, Attachments 5, Comments 5, Links 5, Relations 2, Labels 5, Members 6, Modules 11, Projects 7, States 5, Stickies 5, User 1, Invitations 5) |
| davon **CE-teilweise** (Code ohne Route) | 9 (8 × Estimates, 1 × Relation-Remove) | `apps/api/plane/api/urls/__init__.py`, `apps/api/plane/api/serializers/issue.py:601` |
| davon **EE-only** | 123 | Kap. 2 (Customers 21, Epics 7, IdP Group Sync 12, Initiatives 19, Advanced Search 1, Types/Properties/Options/Values 20, Member-Remove 1, Milestones 6, Pages 6, Work-Item-Pages 4, Project-Template 1, Project-Features 2, Project-Labels 5, Teamspaces 11, Worklogs 5, Workspace-Features 2) |
| davon **entfällt** (deprecated `inbox-issues`) | 5 | `AR/inbox-issue/overview.md` |

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
| W1 | GET | `…/projects/{pid}/work-items/` | Liste; `cursor`, `expand`, `external_id`, `external_source`, `fields`, `order_by`, `per_page` | `projects.work_items:read` | CE | `work_item.py` |
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
| M7 | POST | `workspaces/{ws}/members/remove/` | Mitglied entfernen, in allen Projekten deaktivieren, **Seat-Anzahl reduzieren**; Body undokumentiert | `workspaces.members:write` | **EE-only** (F23) | – |
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

Plan-Bezeichnungen: **Free** (= CE-Umfang, `DD/self-hosting/editions-and-versions.md`), **One** (Legacy-Self-hosted-Einmallizenz), **Pro**, **Business**, **Enterprise** (= „Enterprise Grid“ in den Self-Hosting-Badges). Nach ADR-001 sind in der Zielplattform **alle** Features immer aktiv; die Plan-Spalten dienen nur der Nachvollziehbarkeit „was ist Bezahl-Feature“.

| ID | Feature | ab Plan | Abstufung je Plan | CE-Status | Quelle |
|---|---|---|---|---|---|
| F01 | **Epics** (Work-Item-Typ „Epic“, Epic-API, Epic-Kinder) | Pro | Free/One: nein; Pro/Business/Enterprise: ja | Stub/UI-Hülle im CE | `AR/epics/*`; `apps/web/components/workspace/billing/comparison/plans.tsx:261-270`; `packages/types/src/issues/issue.ts:23-27` (`EIssueServiceType.EPICS`); WEB: https://docs.plane.so/work-items/epics (Label „Pro“) |
| F02 | **Initiatives** (inkl. Verknüpfung Projekte/Epics) | Pro (laut Plan-Tabelle; Konflikt: Business laut Plane University) | Pro/Business/Enterprise: ja; **Sub-Initiativen nur Enterprise** | fehlt | `AR/initiative/*`; `plans.tsx:272-282` (`comingSoon: true`); WEB: https://university.plane.so/courses/201-the-growth/05-intro-to-initiatives.html, https://plane.so/plane-vs-linear |
| F03 | **Initiative-Labels** (Workspace-Katalog + Zuordnung) | wie F02 | wie F02 | fehlt | `AR/initiative/*label*`; `apps/web/components/dropdowns/label/label-select.tsx:48` (EE-Scope „initiative“) |
| F04 | **Customers** (Kunden, Requests, Custom-Properties, Werte, Work-Item-Links) | Business | Free/One/Pro: nein; Business/Enterprise: ja | fehlt | `AR/customer/*`; WEB: https://docs.plane.so/customers, https://plane.so/blog/introducing-plane-business, https://university.plane.so/courses/202-the-power-relay/02-intro-to-customers.html |
| F05 | **Teamspaces** (Mitglieder, Projekte) | Pro | Pro: „Basic“; Business/Enterprise: „Advanced“ (u. a. „Teamspace Cycles“ ab Business) | Stub/UI-Hülle im CE | `AR/teamspace/*`; `packages/constants/src/subscription.ts:28`; `plans.tsx:381-390`; WEB: https://docs.plane.so/core-concepts/workspaces/teamspaces |
| F06 | **Milestones** (Projekt-Meilensteine + Work-Item-Zuordnung) | unklar | unbekannt (seit Self-hosted v1.16.0, 05.11.2025) | Stub/UI-Hülle im CE | `AR/milestones/*`; `packages/i18n/src/locales/en/project-settings.json:420-426`; WEB: https://plane.so/changelog/release-v-1-16-0-introducing-milestones-and-recurring-cycles |
| F07 | **Time Tracking / Worklogs** | One | One: „Basic“; Pro: „Historical timesheets“; Business/Enterprise: „Historical timesheets and approvals“ | teilweise im CE (nur Flag/Typen) | `AR/worklogs/*`; `plans.tsx:183-191`; `apps/api/plane/db/models/project.py:100`; WEB: https://docs.plane.so/core-concepts/issues/time-tracking (Label „Pro“) |
| F08 | **Work Item Types** | Pro | Pro/Business/Enterprise: ja | teilweise im CE (Modelle ohne API/UI) | `AR/issue-types/types/*`; `plans.tsx:205-213`; `apps/api/plane/db/models/issue_type.py:14-55` |
| F09 | **Custom Properties** (Properties, Dropdown-Optionen, Werte) | Pro | Pro: „Project-level custom properties“; Business/Enterprise: „Workspace-level properties and roll-ups“ | fehlt | `AR/issue-types/{properties,options,values}/*`; `plans.tsx:216-224`; `packages/types/src/issues/issue-property-values.ts` |
| F10 | **Formula-Properties** (`property_type=FORMULA`) | unklar (Business oder Enterprise) | „Databases + Formulas“: Plan-Tabelle Business+Enterprise, Enterprise-Feature-Liste nennt es als Enterprise-Merkmal | fehlt | `AR/issue-types/properties/add-property.md`; `plans.tsx:909-918`; `packages/constants/src/subscription.ts:7-14`; `packages/i18n/src/locales/en/work-item-type.json` (`formula`) |
| F11 | **Work-Item-Type-Schema-Endpunkt** (für LLM/MCP) | wie F08/F09 | – | fehlt | `AR/issue-types/types/get-work-item-type-schema.md` |
| F12 | **IdP Group Sync** (OIDC-Gruppen → Workspace-/Projektrollen) | unklar (Commercial Self-hosted; vermutl. Enterprise) | nur Self-hosted Commercial, nur OIDC (SAML/LDAP „coming soon“) | Stub/UI-Hülle im CE (nur i18n + Illustration) | `AR/idp-group-sync/*`; `packages/i18n/src/locales/en/workspace-settings.json:192-256`; WEB: https://docs.plane.so/authentication/group-sync |
| F13 | **Work-Item ↔ Page-Links** | One | One/Pro/Business/Enterprise: ja | fehlt | `AR/work-item-pages/*`; `plans.tsx:842-851`; `packages/constants/src/subscription.ts:38` |
| F14 | **Pages-Public-API + Wiki (Workspace-Seiten)** | Wiki: One (Plan-Tabelle) bzw. Pro (`PRO_PLAN_FEATURES` „Wikis“); Pages: Free | Wiki One+/Pro+; Real-time Collab, Work-Item-Embeds, Publish One+; Nested Pages Business+; Versionen Pro 2 Tage / Business 3 Monate / Enterprise unbegrenzt; Seiten-Templates Pro+; Exports Pro „One download at a time“, Business+ „Queued downloads“ | teilweise im CE (Projektseiten nur interne API) | `AR/page/*`; `plans.tsx:809-931`; `packages/constants/src/subscription.ts:30`; `apps/api/plane/db/models/page.py:23-80` (`is_global`, `parent`) |
| F15 | **Geteilte private Seiten** (`type=shared`) | unklar | – | fehlt | `AR/page/list-project-pages.md` |
| F16 | **Projekt-Feature-API** (`/features/` inkl. `epics`, `work_item_types`; MCP zusätzlich `parallel_cycles`, `project_updates`, `workflows`) | kein eigenes Plan-Feature (steuert Bezahl-Features) | – | teilweise im CE (Einzelfelder am Projekt) | `AR/project-features/*`; `DD/dev-tools/mcp-server-tools.md:377`; `apps/api/plane/db/models/project.py:95-102` |
| F17 | **Workspace-Feature-API** (`project_grouping`, `initiatives`, `teams`, `customers`, `wiki`, `pi`) | kein eigenes Plan-Feature | – | fehlt | `AR/workspace-features/*` |
| F18 | **Project Grouping: Projekt-States + Projekt-Labels** | Pro (Projekt-States laut Plane University) | Plan-Tabelle „State Of Projects“: Pro+ | Stub/UI-Hülle im CE (i18n) | `AR/project-labels/*`; `plans.tsx:343-352`; `packages/i18n/src/locales/en/workspace-settings.json:258-271`; WEB: https://university.plane.so/courses/201-the-growth/11-intro-to-project-states.html |
| F19 | **Project Templates** (`templates/use`) | Business | Business/Enterprise: ja | Stub/UI-Hülle im CE (i18n) | `AR/project/create-project-with-template.md`; `plans.tsx:392-401`; `packages/constants/src/subscription.ts:17`; WEB: https://plane.so/changelog/cloud-april-28-2025 |
| F20 | **Advanced Search** (OpenSearch-gestützt) | Pro | – | fehlt (CE hat einfache Suche W7) | `AR/issue/advanced-search-work-items.md`; `DD/self-hosting/govern/advanced-search.md:7` (Badge „Pro“) |
| F21 | **Zeitbasierte Estimates** (`type=time`) | Pro | Estimates Free/One „Basic“, Pro+ „Advanced“ | Stub/UI-Hülle im CE | `AR/estimate/overview.md`; `packages/constants/src/estimates.ts:15,121-141` (`is_ee: true`); `apps/api/plane/db/models/estimate.py:13-15` (nur `categories`,`points`); `plans.tsx:145-153` |
| F22 | **Custom Relation Definitions** (eigene Relationstypen, Workspace-Settings „Relations“) | unklar | – | fehlt | `DD/dev-tools/mcp-server-tools.md:142-156`; `packages/i18n/src/locales/en/workspace-settings.json:277-281` |
| F23 | **Workspace-Mitglied per API entfernen inkl. Seat-Reduktion** | kein Plan-Feature (Commercial-API) | Seat-Logik entfällt (ADR-001) | fehlt | `AR/members/remove-workspace-member.md` |
| F24 | **Releases** (Release, Tags, Labels, Changelog, Release-Property-Typ) | unklar | – | fehlt | `DD/dev-tools/mcp-server-tools.md:307-356`; WEB: https://plane.so/blog/introducing-releases |
| F25 | **PQL** (Plane Query Language als Filter) | Pro | Pro/Business/Enterprise | fehlt | `plans.tsx:658-667`; `DD/dev-tools/mcp-server-tools.md:44-48` |
| F26 | **Rollen-Slugs / RBAC** (Rollen mit Namespace workspace/project) | Business (RBAC), Enterprise (GAC) | Free/One „Basic“, Pro „Pre-defined roles“, Business „RBAC“, Enterprise „GAC“ | fehlt (CE: Integer-Rollen 20/15/5) | `plans.tsx:695-703`; `DD/dev-tools/mcp-server-tools.md:409-421`; `AR/idp-group-sync/*` (Rollen-Slugs) |
| F27 | **Work-Item-/Projekt-Updates** (Status ON-TRACK/OFF-TRACK/AT-RISK) | unklar („Project Updates“ in Plan-Tabelle auskommentiert) | – | Stub/UI-Hülle im CE | `packages/types/src/enums.ts:87-91`; `packages/i18n/src/locales/en/update.json`; `plans.tsx:355-366`; WEB: https://forum.plane.so/t/epics-is-becoming-a-work-item-type-ships-tuesday-may-26/136 |
| F28 | **Intake per E-Mail** (`source_email`) | Business | Business/Enterprise | teilweise im CE (nur Feld) | `AR/intake-issue/update-intake-issue-detail.md`; `apps/api/plane/db/models/intake.py:77`; `plans.tsx:458-467`; `DD/self-hosting/govern/configure-dns-email-service.md:7` (Badge „Business“) |
| F29 | **Plane Intelligence / AI** (Workspace-Feature `pi`, Dienste `pi-api`, `pi-worker`) | unklar | – | fehlt | `AR/workspace-features/overview.md`; `HC/plane-enterprise/templates/workloads/pi-api.deployment.yaml` |
| F30 | **Agent Runs** (OAuth-Scopes `agents.runs:*`, `agents.run_activities:*`) | unklar | – | fehlt | `DD/dev-tools/build-plane-app/oauth-scopes.md` |
| F31 | **OAuth-Apps mit Scopes** (Bearer-Token für Public-API) | unklar | – | fehlt (CE Public-API nur API-Key) | `AR/introduction.md`; `DD/dev-tools/build-plane-app/oauth-scopes.md` |

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

**Migrationshinweis.** Epic = `WorkItem` mit `WorkItemType.IsEpic`; **keine** separate Tabelle. REST-Fassade `/epics/` mappt `state_id→state` usw. Hierarchie-Validierung zentral im Domain-Service (Typ-Level-Regeln).

**Konfidenz:** hoch (Datenmodell), mittel (Hierarchie-Regeln).

### 4.2 F02/F03 – Initiatives und Initiative-Labels

**Funktionsbeschreibung.** Workspace-weite strategische Ziele, die Arbeit über Projekte, Epics und Work Items bündeln und Fortschritt messen (`AR/initiative/overview.md`). Lebenszyklus über `state`. Verknüpfungen: Projekte (I14–I16), Epics (I17–I19; seit Mai 2026 jedes Work Item, WEB Forum-Ankündigung), Labels (I11–I13) aus einem eigenen Workspace-Label-Katalog (I6–I10). Updates mit Status (F27) und „Sub-initiatives only on Enterprise“ (WEB: https://plane.so/plane-vs-linear). Workspace-Feature `initiatives` (F17).

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
| `settings` | object | RW | | enthält u. a. `display_format` (MCP: Pflicht für TEXT: `single-line`,`multi-line`,`readonly`; DATETIME: `MMM dd, yyyy`,`dd/MM/yyyy`,`MM/dd/yyyy`,`yyyy/MM/dd`) |
| `is_active` | bool | RW | | |
| `is_multi` | bool | RW | | |
| `validation_rules` | object | RW | | |
| `options` | array | W | | MCP: `[{name, description, is_default}]` |
| `external_source`,`external_id` | string | RW | | |
| Audit + `deleted_at` | | RO | | |

**Property-Werte (C19–C21):** PATCH-Body `{"values": ["…"]}` → 204; MCP: jeder Wert ist ein **String** unabhängig vom Typ, Ein-Element-Liste außer bei `is_multi`; `set_values` ersetzt nur die genannten Properties (`DD/dev-tools/mcp-server-tools.md:509-511`). GET-Schema undokumentiert (D2).

**Work-Item-Links (C11–C13):** Body `issue_ids`; optional Request-Kontext (MCP `customer_request_id`); Liste filterbar nach Request und `search`.

**UI-Hinweise.** Nicht im CE-i18n; nur Illustrationen `packages/blocks/src/empty-state/assets/{horizontal-stack,vertical-stack}/customer.tsx`. Felder „Industry“, „Stage“, „Contract status“, „Revenue“, „Employees“, „Website“, „Email“ ergeben sich aus MCP-Hinweisen.

**Migrationshinweis.** Tabellen `customers`, `customer_requests`, `customer_request_work_items`/`customer_work_items` (Link mit optionaler Request-ID), `customer_properties`, `customer_property_options`, `customer_property_values`. Custom-Property-Engine **gemeinsam** mit F09 implementieren (gleiche Typen/Settings), nur anderer „Owner“ (Customer statt Work Item).

**Konfidenz:** hoch (Customer/Property-Felder), mittel (Request-Schema, Werte-Schema).

### 4.4 F05 – Teamspaces

**Funktionsbeschreibung.** Abbildung realer Teams: Mitglieder und Projekte werden einem Teamspace zugeordnet, Arbeit nach Teams verfolgt (`AR/teamspace/overview.md`; WEB: https://docs.plane.so/core-concepts/workspaces/teamspaces). Ab Business „Teamspace Cycles“ (mehrere Cycles mehrerer Projekte gleichzeitig, `plans.tsx:381-390`). Seiten können in Teamspaces verschoben werden (i18n `page.json`: „Private and shared pages cannot be moved to a teamspace.“, „Search for projects and teamspaces“). Teamspace-Kommentare existieren (Asset-Typ `TEAM_SPACE_COMMENT_DESCRIPTION`, `packages/types/src/enums.ts:74`). Workspace-Feature `teams` (F17).

**Datenmodell Teamspace (`AR/teamspace/overview.md`, `add-teamspace.md`)**: `id` uuid RO; `name` string Pflicht; `description_json` object; `description_html` string; `description_stripped` string; `description_binary` string RO; `logo_props` object; `lead` uuid; `workspace` uuid RO; Audit-Felder (`created_by`/`updated_by` im Body erlaubt). Mitglieder-Response: User `{id,first_name,last_name,email,avatar,avatar_url,display_name}` (`AR/teamspace/add-teamspace-members.md`); Projekt-Response: Projekt-Lite.

**API-Hinweise.** TS1–TS11; Scopes `teamspaces:*`, `teamspaces.members:*`, `teamspaces.projects:*`; Pagination TS1/TS6 Cursor. MCP-Server bietet **kein** Teamspace-Tool (`DD/dev-tools/mcp-server-tools.md:9-13`, 28 Tools).

**UI-Hinweise.** CE-Hüllen: Router-Getter `teamspaceId` aus Query (`apps/web/store/router.store.ts:18,83-84`), `teamspaceId` im Issue-Root-Store (`apps/web/store/issue/root.store.ts:46,114`), Filter-Entitätstyp „teamspace“ (`apps/web/components/work-item-filters/filters-hoc/shared.ts:13`), EE-Member-Dropdown mit Scope `teamspaceId` (`apps/web/components/dropdowns/member/member-select.tsx:62`), Realtime-Event-Feld `teamspace_id` (`packages/editor/src/types/document-collaborative-events.ts:43,60,75`), i18n `common.members_and_teamspaces` (`packages/i18n/src/locales/en/common.json:715`), Illustration `packages/blocks/src/empty-state/assets/vertical-stack/teamspace.tsx`. Das CE-Modell `Team` (`apps/api/plane/db/models/workspace.py:261-283`) ist ein Legacy-Rest ohne Mitglieder und **nicht** der Teamspace.

**Migrationshinweis.** Tabellen `teamspaces`, `teamspace_members`, `teamspace_projects`, ggf. `teamspace_comments`; Seiten-Zuordnung (`page.teamspace_id`) und Realtime-Dokument-Kontext berücksichtigen.

**Konfidenz:** hoch (API), niedrig–mittel (Advanced-Funktionen).

### 4.5 F06 – Milestones

**Funktionsbeschreibung.** Zeitbasierte Checkpoints im Projekt, die Work Items (laut Changelog auch Cycles/Module) unter einem gemeinsamen Termin bündeln (`AR/milestones/overview.md`; WEB: https://plane.so/changelog/release-v-1-16-0-introducing-milestones-and-recurring-cycles). Projekt-Feature mit Toggle „Enable milestones – Organize work items by milestone deadlines.“ (`packages/i18n/src/locales/en/project-settings.json:420-426`). Work Items lassen sich nach `milestone_id` gruppieren und per PQL-Feld `milestone` filtern (`DD/dev-tools/mcp-server-tools.md:48,91`). Zuordnung per MCP `milestone manage_workitems` (`add_ids`, `remove_ids`) – **REST-Endpunkt dafür ist nicht dokumentiert** (`DD/dev-tools/mcp-server-tools.md:274-288`).

**Datenmodell Milestone (`AR/milestones/overview.md`)**: `id` string/uuid RO; `title` string Pflicht; `target_date` date; `external_id`, `external_source` string; `created_at`, `updated_at` RO; impl. `project`, `workspace`. Zuordnungsobjekt (MS6): `{id, issue, milestone}` → n:m- oder 1:n-Link (offen, s. Kap. 8).

**API-Hinweise.** MS1–MS6; Scope laut Q2 `projects.milestones:read/write`. Projekt-Feature-Flag `milestones` fehlt im Feature-Objekt (PF1) – Widerspruch zur i18n (offen).

**UI-Hinweise.** Projekt-Übersicht mit einklappbarer Sektion `"milestones"` (Default offen) (`apps/web/store/project/project.store.ts:21,86`); i18n `common.milestones`, `milestones_description` (`packages/i18n/src/locales/en/common.json:717,844-845`); Illustration `packages/blocks/src/empty-state/assets/vertical-stack/milestone.tsx`; Fetch-Key in `packages/constants/src/fetch-keys.ts`.

**Konfidenz:** mittel.

### 4.6 F07 – Time Tracking / Worklogs

**Funktionsbeschreibung.** Zeiterfassung pro Work Item in **Minuten** mit Beschreibung (`AR/worklogs/overview.md`). Projekt-Admin aktiviert per Projekt-Settings → Features → „Time tracking“ („Log time spent on work items and projects.“ / „Project members will be able to log time worked.“, `packages/i18n/src/locales/en/project-settings.json:413-419`). Im Work Item: „Log work“ mit Stunden, Minuten, Beschreibung; Einträge in der Activity bearbeit-/löschbar; Property „Tracked time“ aktualisiert sich (WEB: https://docs.plane.so/core-concepts/issues/time-tracking). Workspace-Settings → „Worklogs“: „Download worklogs AKA timesheets for anyone in any project.“ mit Filtern Nutzer/Projekte/Zeitraum (`packages/i18n/src/locales/en/workspace-settings.json:187-191`; WEB: https://university.plane.so/courses/201-the-growth/16-intro-to-time-tracking.html). Leerzustand „Track timesheets for all members“ (`packages/i18n/src/locales/en/empty-state.json:248-251`). Abstufung One „Basic“ → Pro „Historical timesheets“ → Business/Enterprise „… and approvals“ (`plans.tsx:183-191`).

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

**Funktionsbeschreibung.** Projekte (und – laut MCP – der Workspace) definieren Work-Item-Typen („Task“, „Bug“, „Feature“, `AR/issue-types/types/overview.md`). Jeder Typ hat Standardfelder und eigene Properties; Properties erscheinen automatisch an allen Work Items des Typs; „Mandatory“/„Active“ je Property (WEB: https://docs.plane.so/work-item-types). Ein Typ ist Default (`is_default`), Default-Typ kann nicht gelöscht/inaktiv gesetzt werden (i18n `work_item_types.settings.cant_delete_default_message`, `cant_set_default_inactive_message`, `packages/i18n/src/locales/en/work-item-type.json`). Workspace-Governance-Modus: Typ-/Property-Vokabular zentral im Workspace, projektbezogene Writes werden abgelehnt, Typen werden per `import_to_project` verknüpft (`DD/dev-tools/mcp-server-tools.md:38-42,175-189`); Typ-Hierarchie-Level (`level`, i18n `work_item_type_hierarchy`). Neue Work Items ohne `type_id` erhalten den Default-Typ (so bereits CE: `apps/api/plane/api/serializers/issue.py:190-196`). Projekt-Toggle `work_item_types` (PF1) bzw. CE-Feld `is_issue_type_enabled` (`apps/api/plane/db/models/project.py:101`). Forum-Hinweis: Aktivieren der Typen per REST kann die native Epic-Typ-Anlage verhindern (WEB: https://forum.plane.so/t/enabling-work-item-types-via-rest-api-silently-and-permanently-prevents-the-project-from-ever-having-the-native-epic-type/291).

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
| `settings` | object | RW | | u. a. `display_format` (s. Customer-Properties) |
| `is_active` | bool | RW | | |
| `is_multi` | bool | RW | | |
| `validation_rules` | object | RW | | |
| `formula_config` | string | RW | | nur `FORMULA` |
| `options` | array | W | | bei `OPTION`: `[{name, description?, is_default?, external_id?, external_source?}]` (MCP: `color`) |
| `issue_type` | uuid | RO | | Zuordnung zum Typ (MCP: n:m via `manage_type_properties attach_ids/detach_ids`; Detach löscht Property nicht) |
| `workspace`, `project` | uuid | RO | | |
| `external_id`,`external_source` | string | RW | | |
| Audit + `deleted_at` | | RO | | |

UI-Mapping der Property-Typen (i18n `work_item_types.settings.properties.property_type`): Text, Number (`DECIMAL`), Dropdown (`OPTION`), Boolean, Date (`DATETIME`), Member picker (`RELATION`/`USER`), Formula; Attribute: Text „Single line“/„Paragraph“/„Read only“, Relation „Single select“/„Multi select“, Boolean „True | False“ (`packages/i18n/src/locales/en/work-item-type.json`). Formel-Syntax: `{Field Name}`-Referenzen mit Operatoren `+ - * / &`, Test-Button, Validierungsfehler „Circular reference detected…“, „Formula references non-existent property.“ (dto., Schlüssel `properties.formula`, `create_update.errors.formula`). Mandatory-Logik: Pflicht + Default-Option schließen sich aus (`mandate_confirmation`). Löschen bietet „disable instead“ an (`delete_confirmation`). Projekt-Settings: „Import from workspace“ (`properties.project.add_button.import_from_workspace`).

**Datenmodell Option (`AR/issue-types/options/overview.md`)**: `id`, `name` (Pflicht, innerhalb Property eindeutig – i18n „Option with same name already exists.“), `description`, `sort_order` (number, Beispiel 10000.0), `logo_props`, `is_active`, `is_default`, `parent` (uuid/null, hierarchische Optionen), `property` (uuid), `external_*`, `workspace`, `project`, Audit, `deleted_at`.

**Datenmodell Value (`AR/issue-types/values/*.md`)**: `id`, `property_id`, `issue_id`, `value` (typabhängig: String für TEXT/URL/EMAIL/FILE; UUID oder UUID-Liste für RELATION/OPTION (Liste nur bei `is_multi`); `YYYY-MM-DD` (MCP auch `YYYY-MM-DD HH:MM:SS`) für DATETIME; Zahl für DECIMAL; Bool für BOOLEAN), `value_type` (string), `external_id`, `external_source`, `created_at`, `updated_at`. Semantik: **eine** Wertzeile je (Work Item, Property), bei Multi mehrere; POST = Upsert (MCP: ersetzt bei Multi alle Werte), DELETE entfernt alle (`AR/issue-types/values/add-property-values.md`, `delete-property-value.md`). Wertänderungen erzeugen Activity `ISSUE_ADDITIONAL_PROPERTIES_ACTIVITY` (`packages/types/src/issues/activity/base.ts:87`).

**Schema-Endpunkt T6 (`AR/issue-types/types/get-work-item-type-schema.md`)**: Response `{type_id, type_name, type_description, type_logo_props, fields{…}, custom_fields{…}}`. Standardfelder immer: `name` (`{type:"string",required:true,max_length:255}`), `description_html`, `priority` (Optionen `{value,label}`), `state_id` (Optionen `{id,name,group}` immer), `assignee_ids`, `label_ids` (Optionen nur mit `?include=members,labels`), `start_date`, `target_date`, `parent_id`, `estimate_point_id` (Optionen, wenn Estimates konfiguriert). Custom-Felder nur, wenn Feature ISSUE_TYPES aktiv **und** `type_id` gegeben oder Default-Typ existiert; Schlüssel z. B. `custom_field_severity` mit `{id,type,name,display_name,required,is_multi,options[{id,name}]}`.

**Pagination.** T1, P1, O1 liefern Arrays ohne Envelope; MCP-List mit `cursor`/`per_page`.

**CE-Stand.** `IssueType`, `ProjectIssueType` (`apps/api/plane/db/models/issue_type.py:14-55`), `Issue.type` (`apps/api/plane/db/models/issue.py:164`), `type_id` im Public-Serializer; Typen-Konstante `TIssuePropertyValues = Record<string, unknown>` (`packages/types/src/issues/issue-property-values.ts`); Filter-Backend-Bezug in `apps/api/plane/utils/filters/filter_backend.py`; Illustrationen `custom-properties.tsx`, `property.tsx`. Keine Property-Modelle, keine Endpunkte, keine Settings-UI.

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

**Berechtigungen.** Alle Endpunkte Workspace-Admin (`AR/idp-group-sync/overview.md`); Scopes `workspaces.group_sync:read/write` (nicht in Q2, D18).

**Migrationshinweis.** OIDC-Login-Hook (Claim lesen → Mappings anwenden), Hangfire/Quartz-Job alle 6 h für Offline-Sync (benötigt IdP-Gruppenabfrage – bei reinem OIDC nur über Token/Userinfo möglich; offen), Rollen-Slugs → Mapping auf Ziel-Rollenmodell (F26).

**Konfidenz:** hoch (API/UI-Texte), mittel (Offline-Sync-Mechanik).

### 4.9 F13 – Work-Item ↔ Page-Links

**Funktionsbeschreibung.** Verknüpft Wiki-/Projektseiten mit Work Items, sodass Dokumentation „nahe an der Ausführung“ bleibt; eigener Abschnitt in den Work-Item-Details („Link pages in work items in a separate section“, `plans.tsx:842-851`; `AR/work-item-pages/overview.md`).

**Datenmodell Link-Objekt:** `id` uuid; `page` `{id, name, description_html, created_at, updated_at, created_by, is_global, logo_props}` (Lite-Serializer); `issue`, `project`, `workspace` uuid; `created_at`, `updated_at`, `created_by`. `is_global=true` kennzeichnet Wiki-Seiten (CE-Feld `apps/api/plane/db/models/page.py:51`).

**API.** WP1–WP4; Pagination WP1 Cursor + `order_by`; Pfad-ID beim Löschen widersprüchlich (D11).

**Konfidenz:** hoch.

### 4.10 F14/F15 – Pages-Public-API und Wiki

**Funktionsbeschreibung.** Seiten auf Workspace- (Wiki, projektunabhängig) und Projektebene (`AR/page/overview.md`). Listenfilter `type`: `all` (alle zugänglichen), `public` (öffentlich, ohne archivierte), `private` (eigene, nicht geteilte, ohne archivierte), `shared` (explizit mit mir geteilte private Seiten), `archived` (`AR/page/list-project-pages.md`). Listeneinträge enthalten `parent_id` (verschachtelte Seiten). EE-Wiki kennt „Wiki collections“ (vordefiniert General/Private/Shared/Archived, eigene Collections, Seiten hinzufügen/entfernen, Löschen mit Transfer) – UI-Texte in `packages/i18n/src/locales/en/wiki.json`. Seiten-Suche über Wiki-Collections, Projekte und Teamspaces (`packages/i18n/src/locales/en/page.json:85-91`).

**Datenmodell (Create-Body/Response):** `id`, `name` (Pflicht), `description_html` (Pflicht), `owned_by` uuid, `access` (0 Public, 1 Private), `color`, `is_locked`, `archived_at` (date), `view_props` object, `logo_props` object, `external_id`, `external_source`, `workspace`, `parent_id`, Audit. Public-API bietet **kein** Update/Delete/Archive/Lock (nur interne API).

**CE-Stand.** `Page` mit `is_global`, `parent`, `access`, `moved_to_page/project`, `sort_order` (`apps/api/plane/db/models/page.py:23-80`), `ProjectPage` (`…:135-155`), interne Projektseiten-API inkl. archive/lock/access/description/versions/duplicate (`apps/api/plane/app/urls/page.py`); globale Seiten nur in der Suche referenziert (`apps/api/plane/app/views/search/base.py:757`). Keine Public-API, keine Wiki-UI.

**Konfidenz:** hoch (API), mittel (Collections/Sharing-Semantik).

### 4.11 F16/F17 – Feature-Toggles (Projekt und Workspace)

**Projekt-Features (`AR/project-features/*`)** – Objekt `{epics, modules, cycles, views, pages, intakes, work_item_types}` (alle bool); MCP `update_features` zusätzlich `parallel_cycles`, `project_updates`, `workflows` und benennt `workitem_types` (`DD/dev-tools/mcp-server-tools.md:377`). i18n ergänzt `time_tracking`, `milestones`, Intake-Unteroptionen (Forms, Assignees) (`packages/i18n/src/locales/en/project-settings.json:325-426`). Mapping auf CE-Felder: `modules`↔`module_view`, `cycles`↔`cycle_view`, `views`↔`issue_views_view`, `pages`↔`page_view`, `intakes`↔`intake_view`, `work_item_types`↔`is_issue_type_enabled` (`apps/api/plane/db/models/project.py:95-101`); `epics`, `parallel_cycles`, `project_updates`, `workflows`, `milestones` ohne CE-Pendant.

**Workspace-Features (`AR/workspace-features/*`)** – `{project_grouping, initiatives, teams, customers, wiki, pi}` (alle bool).

**Migrationshinweis.** ADR-001: Toggles bleiben als fachliche Einstellungen erhalten; Tabelle `project_features`/`workspace_features` oder Spalten; Default nach Original (unbekannt → Kap. 8).

**Konfidenz:** hoch.

### 4.12 F18 – Project Grouping (Projekt-States, Projekt-Labels)

**Funktionsbeschreibung.** Workspace-Settings → „Projects“ mit Tabs „Project states“ und „Project labels“ („Manage project states, and enable project labels, and other configuration.“); Projekt-States: „Project States is a Plane-only feature for tracking progress of all your projects by any project property.“ (`packages/i18n/src/locales/en/workspace-settings.json:258-271`). Default-Projekt-States Draft, Planning, Execution, Monitoring, Completed, Cancelled, erweiterbar (WEB: https://university.plane.so/courses/201-the-growth/11-intro-to-project-states.html). Workspace-Feature `project_grouping`.

**Datenmodell Projekt-Label (`AR/project-labels/overview.md`)**: `id`, `name` (Pflicht), `description`, `color` (Hex), `sort_order` (number, Default-Beispiel 65535), `workspace`, `created_at`, `updated_at`, `created_by`, `updated_by`. Projekt-States: **keine** API in `AR/` (nur UI-Belege).

**Hinweis.** Gleicher Scope `projects.labels:*` wie Work-Item-Labels.

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

MCP `workitem_relation` kennt neben den eingebauten Abhängigkeiten (`blocking`, `blocked_by`, `start_before`, `start_after`, `finish_before`, `finish_after`) **eigene Relationsdefinitionen**: `list_definitions(is_default, is_active)`, `create_definition(name*, outward, inward, is_active, color)`, `update_definition`, `delete_definition`; Relation-Create mit `relation_definition_id` + `relation_definition_label` (Richtung über outward/inward-Label); Delete mit `is_dependency` (Dependencies und Custom-Relationen sind unabhängig) (`DD/dev-tools/mcp-server-tools.md:142-156`). Workspace-Settings „Relations – Create and manage relation types that connect work items across your workspace.“ (`packages/i18n/src/locales/en/workspace-settings.json:277-281`). CE-Modell kennt zusätzlich `implemented_by`/`implements` (`apps/api/plane/db/models/issue.py:272-293`), das die Public-API nicht anbietet. **Konfidenz:** mittel.

### 4.17 F23 – Workspace-Mitglied entfernen (M7)

POST `members/remove/` entfernt das Mitglied, deaktiviert es in allen Projekten und reduziert die Seat-Anzahl (`AR/members/remove-workspace-member.md`); Body undokumentiert (vermutl. `email` oder `member_id`). Seat-Logik entfällt (ADR-001). **Konfidenz:** mittel.

### 4.18 F24 – Releases (nur MCP-Doku)

Workspace-Releases mit `name`*, `description_html`, `status` (`unreleased` Default, `released`, `cancelled`), `release_date` (UI „Target date“), `target_date` (separat gespeichert, in UI nicht sichtbar), `tag_id`, `lead_id`, `is_prerelease`, `external_*`; Changelog (Rich-Text, wird leer mit dem Release angelegt; `get_changelog`/`update_changelog` mit `description_html`/`description_stripped`); Work-Item-Zuordnung (`add_ids`/`remove_ids`); Release-Tags (`version`*, `description`, `commit_hash`, `git_tag`); Release-Labels (Workspace-Palette `name`*, `color`, `sort_order`; `attach`/`detach`) (`DD/dev-tools/mcp-server-tools.md:307-356`). Property-Typen „Release picker“ und „Formula“ (WEB: https://plane.so/blog/introducing-releases). Gruppierungsschlüssel `release_work_items__release_id` (`…:91`). Nicht in `AR/`. **Konfidenz:** mittel.

### 4.19 F25/F26/F27/F28/F29/F30/F31 – weitere aus der API ableitbare Bezahl-Merkmale

| Feature | Belegte Fakten | Quelle | Konfidenz |
|---|---|---|---|
| F25 PQL | `pql`-Filter in Work-Item-, Cycle-, Modul-Listen; UUID-basierte Felder project, assignee, state, label, cycle, module, type, milestone, creator; Funktionen `currentUser()`, `openStates()`, `isOverdue()`, `childOf("PROJ-12")`, `cf["<property id>"]`; `state__group` als Filter verboten | `DD/dev-tools/mcp-server-tools.md:44-48,91,254` | mittel |
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

---

## 7. Querschnittliche Migrationshinweise (.NET Aspire / EF Core / PostgreSQL / Angular)

| Thema | Empfehlung | Begründung/Quelle |
|---|---|---|
| Public-API-Vertrag | `snake_case`-JSON, Pfade/Statuscodes 1:1, Pagination-Envelope aus Kap. 1.2 | ADR-003-Konsequenz |
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
| O1 | Plan-Tier Milestones, IdP Group Sync, Custom Relations, Releases, Shared Pages, PI, Agent Runs, Formula | Kein offizieller, abrufbarer Beleg (plane.so nicht erreichbar) | für Migration irrelevant (ADR-001); nur dokumentarisch nachpflegen |
| O2 | Initiatives Tier | Plan-Tabelle Pro vs. Plane University Business | Pro annehmen (Hersteller-Tabelle `plans.tsx`) |
| O3 | Body der DELETE-Massenendpunkte (I13, I16, I19, TS8, TS11) | undokumentiert | Arrays `label_ids`/`project_ids`/`epic_ids`/`member_ids` im JSON-Body (MCP-Analogie) |
| O4 | Body `members/remove/` | undokumentiert | `email` **oder** `member_id` akzeptieren |
| O5 | Customer-Request-, Property-Value-, Customer-Work-Item-Response-Schemas | Platzhalter in Doku (D1, D2) | aus Request-Feldern + Audit ableiten; UI-Analyse (anderer Cluster) prüfen |
| O6 | Milestone ↔ Work Item Kardinalität | `{id, issue, milestone}` lässt n:m zu; PQL/Gruppierung `milestone_id` deutet auf 1 Milestone je Work Item | 1:n (ein Milestone je Work Item) mit Link-Tabelle und Unique(issue) |
| O7 | Milestone-REST-Zuordnung | nur MCP `manage_workitems` | eigener Endpunkt `POST/DELETE …/milestones/{id}/work-items/` |
| O8 | Projekt-Feature-Flag `milestones`, `time_tracking` | nicht im Feature-Objekt PF1, aber im UI | in Feature-Objekt aufnehmen |
| O9 | Initiative-Liste paginiert? | D7 | paginiert (Envelope), `per_page` großzügig |
| O10 | Work-Item-Page-Delete per Page-ID oder Link-ID | D11 | beide akzeptieren |
| O11 | Workspace-Governance-Modus für Typen/Properties | wie aktiviert, welche Defaults | eigene Analyse UI-Cluster; Datenmodell: Typ/Property mit `project_id` nullable |
| O12 | Offline-Group-Sync ohne IdP-API | wie werden Gruppen ohne Login abgefragt? | optionaler OIDC-Provider-Adapter (Graph/Keycloak-Admin-API), sonst deaktiviert |
| O13 | Default-Werte der Feature-Toggles | unbekannt | CE-Defaults übernehmen (`module_view=False`, `cycle_view=False`, `page_view=True`, …, `apps/api/plane/db/models/project.py:95-102`); EE-Toggles Default `false` |
| O14 | Formel-Engine | Datentypen, Operatoren außer `+ - * / &`, Roll-ups | eigener Spike |
| O15 | Rollenmodell | CE Integer-Rollen vs. EE Slugs/RBAC | Architektur-Entscheidung nötig (ADR) – Slugs + Mapping auf 20/15/5 |
