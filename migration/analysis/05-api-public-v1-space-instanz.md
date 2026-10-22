# A05 – Öffentliche APIs: Public REST API v1, Public Space API (Deploy-Boards), Instanz-/God-Mode-API, `plane.web`, `plane.analytics`

> **Status:** IST-Analyse Plane v1.4.2 Community Edition (AGPL-3.0)
> **Bindend:** `migration/architecture/00-grundsatzentscheidungen.md` (ADR-000 … ADR-006). Insbesondere ADR-001 (eine Edition, alle Bezahl-Features aktiv, keine Lizenz/kein Edition-Feld), ADR-003 (Greenfield, JSON-Verträge fachlich am Original, `snake_case`), ADR-004 (Self-hosted/Airgapped – keine Telemetrie nach außen, keine Pflicht-Internetzugriffe), ADR-005 (UI 1:1 – God Mode und Space zeigen Backend-Fehlercodes/-texte direkt an).
> **Bereich (vollständig gelesen):**
> - Public API v1: `apps/api/plane/api/{__init__,apps,rate_limit}.py`, `apps/api/plane/api/middleware/api_authentication.py`, `apps/api/plane/api/urls/*.py` (13 Dateien), `apps/api/plane/api/views/*.py` (14 Dateien), `apps/api/plane/api/serializers/*.py` (15 Dateien)
> - OpenAPI: `apps/api/plane/settings/openapi.py`, `apps/api/plane/utils/openapi/{__init__,auth,decorators,hooks,parameters}.py` (`examples.py`/`responses.py` nur Namen/Struktur), `apps/api/plane/urls.py`
> - Public Space API: `apps/api/plane/space/{apps.py,urls/*.py,views/*.py,serializer/*.py,utils/grouper.py}`
> - Instanz-API: `apps/api/plane/license/**` (urls, views, serializers, permissions, models, utils, bgtasks, management commands, Migrationen-Liste)
> - `apps/api/plane/web/*`, `apps/api/plane/analytics/*`
> **Zur Verhaltensklärung zusätzlich gelesen:** `apps/api/plane/app/permissions/{project,workspace}.py` (identisch mit `apps/api/plane/utils/permissions/*`, die nur `WorkspaceMemberPermission` nicht enthalten), `apps/api/plane/utils/{paginator(Teile),cache,order_queryset(Teile),cycle_transfer_issues(Teile),issue_relation_mapper,serializers,otlp_endpoints,constants(Teile)}.py`, `apps/api/plane/utils/instance_config_variables/{__init__,core,extended}.py`, `apps/api/plane/authentication/{session.py(Teile),rate_limit.py,middleware/session.py,adapter/exception.py,adapter/error.py(Teile),adapter/base.py(Teile),utils/login.py,utils/host.py(Teile),views/common.py(Teile)}`, `apps/api/plane/middleware/{logger,request_body_size}.py`, `apps/api/plane/bgtasks/{logger_task,webhook_task(Teile)}.py`, `apps/api/plane/settings/common.py` (Teile), `apps/api/plane/celery.py` (Teile), `apps/api/bin/docker-entrypoint-api.sh`, Modelle `apps/api/plane/db/models/{project,deploy_board,intake,api,asset,workspace(Teile),issue(Teile),module(Teile),base}.py`, App-Serializer `apps/api/plane/app/serializers/{project(DeployBoardSerializer),issue(Teile),intake(Teile),user(UserAdminLiteSerializer)}.py`, App-View `DeployBoardViewSet` (`apps/api/plane/app/views/project/base.py`), Tests `apps/api/plane/tests/contract/api/*.py` (Namen/Docstrings), Frontend-Abgleich über `migration/analysis/11-frontend-admin-space.md`.
> **Konventionen:** `{W}` = `/api/v1/workspaces/{slug}`, `{P}` = `{W}/projects/{project_id}`, `{WI}` = `{P}/work-items/{issue_id}` (Alias `{P}/issues/{issue_id}`), `{A}` = `/api/public/anchor/{anchor}`, `{I}` = `/api/instances`. Quellkürzel: `V1/` = `apps/api/plane/api/`, `V1V/` = `apps/api/plane/api/views/`, `V1S/` = `apps/api/plane/api/serializers/`, `V1U/` = `apps/api/plane/api/urls/`, `SP/` = `apps/api/plane/space/`, `LIC/` = `apps/api/plane/license/`, `OA/` = `apps/api/plane/utils/openapi/`, `PERM/` = `apps/api/plane/app/permissions/`, `M/` = `apps/api/plane/db/models/`, `UT/` = `apps/api/plane/utils/`, `AUTH/` = `apps/api/plane/authentication/`, `SET/` = `apps/api/plane/settings/`. Rollen: **A** = Admin (20), **M** = Member (15), **G** = Guest (5). Zeilenangaben „Z.“ beziehen sich auf die jeweils genannte Datei.

---

## Inhaltsverzeichnis

1. Überblick & Verantwortlichkeiten
   - 1.1 Bereichsabgrenzung
   - 1.2 Authentifizierungsmodelle im Vergleich
   - 1.3 Kennzahlen
   - 1.4 Community- vs. Bezahl-Editionen in diesem Bereich
2. Vollständige Inventare
   - 2.1 v1-Infrastruktur (Basisklassen, Auth, Rate-Limit, Fehler, Paginierung, `fields`/`expand`, Middleware, Permissions, OpenAPI)
   - 2.2 v1-Endpunkt-Inventar (alle Routen)
   - 2.3 v1-Serializer-Inventar
   - 2.4 v1-Response-Shapes (Feldlisten)
   - 2.5 v1-Query-Parameter-Inventar
   - 2.6 Public Space API (`/api/public/`)
   - 2.7 Instanz-API (`/api/instances/`)
   - 2.8 `plane.web`, `plane.analytics`, Schema-Routen
   - 2.9 Abdeckungsvergleich: v1 ↔ interne App-API ↔ Commercial-API
3. Verhalten/Logik/Abläufe im Detail (inkl. Edge-Cases)
4. Abhängigkeiten zu anderen Bereichen
5. Migrationshinweise (.NET Aspire / EF Core / PostgreSQL / Angular)
6. Offene Punkte

---

## 1. Überblick & Verantwortlichkeiten

### 1.1 Bereichsabgrenzung

| Modul | Mount (`apps/api/plane/urls.py`) | Django-App (`SET/common.py` `INSTALLED_APPS`) | Konsumenten | Zweck |
|---|---|---|---|---|
| `plane.api` | `path("api/v1/", include("plane.api.urls"))` (Z. 22) | `"plane.api"` (Z. 113) | **Externe Clients** (Skripte, Integrationen, MCP-Server, Importer). **Kein** CE-Frontend ruft `/api/v1/` auf (grep über `apps/`, `packages/`: keine Treffer außer Backend). | Öffentliche, versionierte REST-API mit API-Key-Auth: Projekte, States, Labels, Work Items (inkl. Links, Kommentare, Aktivitäten, Anhänge, Relationen, Suche), Cycles, Modules, Intake, Mitglieder, Einladungen, Stickies, Assets, aktueller User. **Zusätzlich:** Die v1-Serializer sind das **Payload-Format der Webhooks** (`apps/api/plane/bgtasks/webhook_task.py` Z. 26–36, 58–68). |
| `plane.space` | `path("api/public/", include("plane.space.urls"))` (Z. 20) | `"plane.space"` (Z. 106) | `apps/space` (Public Boards, siehe A11) | Öffentlich lesbare, per `anchor` adressierte Deploy-Boards eines Projekts; schreibend (angemeldet): Kommentare, Reaktionen, Votes, Kommentarbilder, Intake-Einreichungen. |
| `plane.license` | `path("api/instances/", include("plane.license.urls"))` (Z. 21) | `"plane.license"` (Z. 112) | `apps/admin` (God Mode), `apps/web`/`apps/space` (`GET /api/instances/`) | Instanz-Singleton, Erst-Einrichtung (erster Admin), Admin-Login/-Logout, Instanz-Konfiguration (Key/Value inkl. Verschlüsselung), Workspace-Verwaltung durch Instanz-Admins, SMTP-Test, Telemetrie-Task, Registrierungs-/Konfigurations-Management-Commands. |
| `plane.web` | `path("", include("plane.web.urls"))` (Z. 24) | `"plane.web"` (Z. 110) | Health-Checks, Crawler | `GET /` → `{"status": "OK"}`, `GET /robots.txt` → `Disallow: /`. |
| `plane.analytics` | – (keine URLs) | `"plane.analytics"` (Z. 104) | – | Leere App-Hülle (`apps/api/plane/analytics/apps.py`, nur `AppConfig`); die Analytics-Endpunkte liegen in `plane.app` (A03 2.11). |
| drf-spectacular | `api/schema/`, `api/schema/swagger-ui/`, `api/schema/redoc/` nur wenn `ENABLE_DRF_SPECTACULAR=1` (`apps/api/plane/urls.py` Z. 27–40, `SET/common.py` Z. 602–607) | `"drf_spectacular"` (dynamisch) | Entwickler | OpenAPI-3-Schema **nur** der `/api/v1/`-Pfade (Hook `OA/hooks.py`). |

### 1.2 Authentifizierungsmodelle im Vergleich

| Aspekt | v1 (`plane.api`) | Space (`plane.space`) | Instanz (`plane.license`) |
|---|---|---|---|
| Authentifizierung | **nur** `APIKeyAuthentication` (Header `X-Api-Key`, case-insensitiv) (`V1/middleware/api_authentication.py`) | `BaseSessionAuthentication` (Cookie `session-id`; Origin-Check statt CSRF-Token für unsichere Methoden) (`SP/views/base.py` Z. 62, 155; `AUTH/session.py` Z. 56–63) | DRF-Views: `BaseSessionAuthentication`, aber Session-Middleware liest für **jeden Pfad, der `instances` enthält**, das Cookie **`admin-session-id`** (`AUTH/middleware/session.py`; `SET/common.py` Z. 431). Form-Views (Sign-in/-up/-out) sind Django-`View`s mit **Django-CSRF-Token** (`csrfmiddlewaretoken`). |
| Default-Permission | `IsAuthenticated` + Klassen je View | `IsAuthenticated` (ViewSets), `AllowAny` (Lese-Endpunkte) | `InstanceAdminPermission` (`LIC/api/permissions/instance.py`) |
| Rate-Limit | `ApiKeyRateThrottle` (Default `60/minute` je API-Key) **nur** für `BaseAPIView`-Subklassen; ViewSets (Einladungen, Stickies) haben **kein** API-Key-Limit | globaler `AnonRateThrottle` `30/minute` für anonyme Requests (`SET/common.py` Z. 141–145) | Sign-in/Sign-up: `AuthenticationThrottle` (Default `10/minute` je IP, `AUTHENTICATION_RATE_LIMIT`) (`AUTH/rate_limit.py`); sonst `AnonRateThrottle` |
| Fehlerformat | `{"error": "..."}` / DRF `{"detail": "..."}` / Serializer-Fehler `{feld: [..]}`; 429 `{"error_code": 5900, "error_message": "RATE_LIMIT_EXCEEDED"}` | wie v1 (ohne Rate-Limit-Spezialfall außer anonym) | JSON-Views wie v1; Form-Views: **HTTP 302** auf `/god-mode/?error_code=…&error_message=…` |

### 1.3 Kennzahlen

| Kennzahl | Wert | Quelle |
|---|---|---|
| v1: geroutete Methode×Pfad-Kombinationen | **136** (73 ohne Work-Item-Gruppe + 50 Work-Item-Kombinationen inkl. Alt-Präfix `issues/` + 6 Einladungen + 6 Stickies + 1 Router-API-Root) | 2.2 |
| v1: davon reine Aliase | 5 (`project-members/…` ↔ `members/…`) + 24 (`issues/…` ↔ `work-items/…`) | `V1U/member.py`, `V1U/work_item.py` |
| v1: implementierte, aber **nicht geroutete** Handler | 10 (8 × Estimates/Estimate-Points, `IssueDetailAPIEndpoint.put`, `ModuleIssueDetailAPIEndpoint.get`) | 2.2.19 |
| Space: geroutete Methode×Pfad-Kombinationen | 38 (davon 1 defekt: `GET /api/public/workspaces/{slug}/project-boards/`; 2 Alias-Kombinationen `inbox-issues`) | 2.6.2 |
| Instanz: geroutete Methode×Pfad-Kombinationen | 18 (+ 3 versehentlich erreichbare, fehlerhafte Methodenkombinationen) | 2.7.2 |
| InstanceConfiguration-Keys (Seed) | **36** in 9 Kategorien | 2.7.4 |
| Web/Health | 2 | 2.8 |

### 1.4 Community- vs. Bezahl-Editionen in diesem Bereich

Der CE-Code dieses Bereichs enthält **keine** Lizenzprüfung; das Feld `Instance.edition` ist immer `"PLANE_COMMUNITY"` (`LIC/models/instance.py` `InstanceEdition`, `LIC/management/commands/register_instance.py`). Bezahl-Funktionen, die diesen Bereich betreffen, sind in anderen Analyse-Dokumenten vollständig inventarisiert und müssen in der Zielarchitektur **zusätzlich** gebaut werden (ADR-001):

| Bezahl-Funktion (ID) | Bezug zu diesem Bereich | CE-Spur in diesem Bereich | Detailquelle |
|---|---|---|---|
| EE-only Ressourcen der Public API (Customers, Epics, IdP Group Sync, Initiatives, Advanced Search, Work-Item-Types/Properties/Options/Values, Milestones, Pages, Work-Item-Pages, Project-Templates, Project-/Workspace-Features, Project-Labels, Teamspaces, Worklogs, Member-Remove) | v1-Erweiterung (123 Endpunkte) | `IssueSerializer.type_id` (`V1S/issue.py` Z. 60–62), `RelatedIssueSerializer.is_epic` (Z. 667), `ProjectCreateSerializer.is_issue_type_enabled`/`is_time_tracking_enabled` (Z. 81–82) | `migration/features/21-paid-api-referenz-developer-docs.md` |
| Estimates in v1 (CE-teilweise) | v1 | Views/Serializer/URLs vorhanden, URL-Modul nicht eingebunden (2.2.19) | Doc 21 §2.5 |
| PQL / strukturierte Filter für Work-Item-Listen (PF-52) | v1 `GET {P}/work-items/` | Parameter `pql`/`filters` werden mit 400 abgewiesen (`V1V/issue.py` Z. 324–335) | `migration/features/20-paid-spuren-im-repo.md` PF-52 |
| OAuth-Apps/Scopes/Bot-Token (P03-F25), OAuth Bridge (PF-91, P03-F09) | v1-Authentifizierung | nur API-Key; `APIToken.user_type` (Human/Bot), `APIToken.workspace` (nullable, in v1 **nicht** ausgewertet) (`M/api.py` Z. 23–37) | `migration/features/22-paid-architektur-selfhosting-dienste.md` |
| Workspace-Access-Tokens (PF-62) | v1 | `APIToken.workspace`-FK existiert, ungenutzt | Doc 20 PF-62 |
| API-enabled Audit Logs (PF-59) | v1 | `APIActivityLog` + `APITokenLogMiddleware` protokolliert **jeden** Request mit `X-Api-Key` (2.1.7) | Doc 20 PF-59, Doc 22 P03-F44 |
| Publish Views (PF-44), Publish Pages (PF-73/P07-08), Intake Forms (PF-36) | Space-API | `DeployBoard.TYPE_CHOICES` enthält `issue, module, cycle, page, view, intake` (`M/deploy_board.py` Z. 20–28), CE nutzt nur `project`; `packages/types/src/publish.ts` `TPublishEntityType = "project" \| "page"`; `EInboxIssueSource.FORMS`/`EMAIL` (`packages/types/src/inbox.ts`) | Doc 20, `migration/features/26-paid-wissen-pages-wiki.md` §3.8 |
| Intake per E-Mail (PF-37, P03-F23) | Space/Intake | `IntakeIssue.source_email` (`M/intake.py`), `SourceType` nur `IN_APP` | Doc 22 |
| God-Mode-Erweiterungen: SAML/OIDC/LDAP-Konfiguration, Session-Expiry, User-Management, System-Checks, Health-Probes (P03-F03…F07, F34, F35) | Instanz-API | keine Keys für SAML/OIDC/LDAP in `UT/instance_config_variables/core.py`; `ADMIN_SESSION_COOKIE_AGE`/`SESSION_COOKIE_AGE` nur per Env (`SET/common.py` Z. 425–432) | Doc 22 |
| Lizenz/Seats/Billing (P03-F01/F02), Airgapped-Lizenzdatei (P03-F36) | Instanz | `Instance.edition`, `is_verified`, `is_support_required`, `namespace` | **entfällt** (ADR-001) |

---

## 2. Vollständige Inventare

### 2.1 v1-Infrastruktur

#### 2.1.1 Basisklassen (`V1V/base.py`)

| Klasse | Z. | Basen | `authentication_classes` | `permission_classes` (Default) | Throttles | Besonderheiten |
|---|---|---|---|---|---|---|
| `TimezoneMixin` | 38 | – | – | – | – | `initial()`: aktiviert `zoneinfo.ZoneInfo(request.user.user_timezone)` für authentifizierte Nutzer, sonst `timezone.deactivate()` → alle `__date`-Lookups/`timezone.localtime` laufen in **Benutzerzeitzone**. |
| `BaseAPIView` | 52 | `TimezoneMixin, GenericAPIView, ReadReplicaControlMixin, BasePaginator` | `[APIKeyAuthentication]` | `[IsAuthenticated]` | **`get_throttles()` → `[ApiKeyRateThrottle()]`** (Z. 69–70) | `initial()`: bei `POST/PUT/PATCH` muss `request.data` `dict` oder `list` sein, sonst `ParseError("Request body must be a JSON object or array.")` → 400 `{"detail": "Request body must be a JSON object or array."}` (Z. 35, 59–62). `handle_exception` (Z. 72–109), `dispatch` (Z. 111–121), `finalize_response` setzt `X-RateLimit-Remaining`/`X-RateLimit-Reset` aus `request.META` (Z. 123–136). Properties `workspace_slug` (= `kwargs["slug"]`), `project_id` (= `kwargs["project_id"]`, sonst `kwargs["pk"]` wenn URL-Name `"project"`), `fields`, `expand` (kommagetrennte Query-Parameter, leere Einträge entfernt, leer → `None`) (Z. 138–160). `use_read_replica = False` (Views setzen meist `True`; nur Lastverteilung). |
| `BaseViewSet` | 162 | `TimezoneMixin, ReadReplicaControlMixin, ModelViewSet, BasePaginator` | `[APIKeyAuthentication]` | `[IsAuthenticated]` | **keine Überschreibung** → DRF-Default `AnonRateThrottle` (greift nur bei anonymen Requests) ⇒ **kein API-Key-Rate-Limit, keine X-RateLimit-Header** für Einladungen/Stickies | Gleiche Body-Prüfung wie `BaseAPIView` (Z. 171–174); `get_queryset()` → `self.model.objects.all()`; abweichende 404-Meldung „The required object does not exist.“ und Logging (Z. 183–242). |

#### 2.1.2 Authentifizierung `APIKeyAuthentication` (`V1/middleware/api_authentication.py`)

| Schritt | Verhalten | Z. |
|---|---|---|
| Header | `request.headers.get("X-Api-Key")` (OpenAPI dokumentiert `X-API-Key`; Header sind case-insensitiv) | 23–27 |
| Kein Header | `authenticate()` liefert `None` → Request anonym → `IsAuthenticated` scheitert → DRF wirft `NotAuthenticated`; da die Klasse **kein** `authenticate_header()` definiert, setzt DRF zunächst 403, der globale Handler `auth_exception_handler` korrigiert `NotAuthenticated` auf **401** → `401 {"detail": "Authentication credentials were not provided."}` | 45–52; `AUTH/adapter/exception.py` |
| Token-Lookup | `APIToken.objects.get(Q(expired_at__gt=now) \| Q(expired_at__isnull=True), token=token, is_active=True, user__is_active=True)` | 29–37 |
| Ungültig/abgelaufen/inaktiv/User deaktiviert | `AuthenticationFailed("Given API token is not valid")` → **403** `{"detail": "Given API token is not valid"}` (kein WWW-Authenticate ⇒ DRF 403; der Handler korrigiert nur `NotAuthenticated`). Test akzeptiert 401 oder 403 (`apps/api/plane/tests/contract/api/test_authentication.py` Z. 29–45). | 38–39 |
| Erfolg | `api_token.last_used = now; save(update_fields=["last_used"])` (**ein DB-Write pro Request**); Rückgabe `(user, token-string)` | 41–43 |
| Token-Format | `"plane_api_" + uuid4().hex` (`M/api.py` Z. 19–20); `label` default `uuid4().hex`; Felder `label, description, is_active, last_used, token (unique), user, user_type (0 Human/1 Bot), workspace (nullable), expired_at` (`M/api.py` Z. 23–37). Token wird **im Klartext** gespeichert. Verwaltung über die App-API (A03 2.7, `/api/users/api-tokens/`). | |
| Workspace-Bindung | **Keine.** Ein Token wirkt für alle Workspaces des Users; `APIToken.workspace` wird in `plane.api` nicht ausgewertet. | – |
| Session-Cookies | werden in v1 **nicht** akzeptiert (nur `APIKeyAuthentication`). | `V1V/base.py` Z. 53, 165 |

#### 2.1.3 Rate-Limit `ApiKeyRateThrottle` (`V1/rate_limit.py`)

| Aspekt | Verhalten | Quelle |
|---|---|---|
| Rate | `settings.API_KEY_RATE_LIMIT`, Env `API_KEY_RATE_LIMIT`, Default `"60/minute"` (DRF-Format `n/second\|minute\|hour\|day`) | `V1/rate_limit.py` Z. 14; `SET/common.py` Z. 162–163 |
| Schlüssel | `"api_key:{X-Api-Key-Wert}"` (Roh-Token im Redis-Key); ohne Header kein Throttling | Z. 16–23 |
| Speicher | Django-Cache = Redis (`django_redis`) (`SET/common.py` Z. 274–291); Sliding-Window-Historie (DRF `SimpleRateThrottle`) | |
| Reihenfolge | DRF `initial()`: Authentifizierung → Permissions → Throttles. Ungültige Keys scheitern **vor** dem Throttle (403); fehlende Permission ⇒ kein Throttle-Zählerinkrement. | DRF-Standard |
| Erfolgsheader | `X-RateLimit-Remaining = max(0, num_requests - len(history))` (nach Einfügen des aktuellen Requests), `X-RateLimit-Reset = int(now + duration)` (Unix-Sekunden; **Zeitpunkt jetzt + Fensterlänge**, nicht das echte Fensterende) | Z. 25–50; `V1V/base.py` Z. 123–136 |
| Überschreitung | DRF `Throttled` → `auth_exception_handler` ersetzt Body: **429** `{"error_code": 5900, "error_message": "RATE_LIMIT_EXCEEDED"}`; DRF setzt `Retry-After: <Sekunden>`; **keine** X-RateLimit-Header | `AUTH/adapter/exception.py`; `AUTH/adapter/error.py` Z. 73 |
| Geltungsbereich | alle Views auf Basis `BaseAPIView` (alle v1-Endpunkte außer `WorkspaceInvitationsViewset`, `StickyViewSet`) | 2.1.1 |

#### 2.1.4 Fehlerbehandlung (v1)

| Auslöser | `BaseAPIView` (`V1V/base.py` Z. 72–109) | `BaseViewSet` (Z. 183–242) |
|---|---|---|
| jede Unterklasse von `rest_framework.exceptions.APIException` | DRF-Standard über `EXCEPTION_HANDLER = plane.authentication.adapter.exception.auth_exception_handler` (`SET/common.py` Z. 149): Body `{"detail": "..."}` bzw. Serializer-Fehler; `NotAuthenticated` → 401; `Throttled` → 429 + Fehlercode 5900 | identisch |
| `django.db.IntegrityError` | 400 `{"error": "The payload is not valid"}` | 400 `{"error": "The payload is not valid"}` (+ Log) |
| `django.core.exceptions.ValidationError` | 400 `{"error": "Please provide valid detail"}` | dito (+ Warn-Log `VALIDATION_ERROR`) |
| `ObjectDoesNotExist` (alle `Model.DoesNotExist`) | **404 `{"error": "The requested resource does not exist."}`** | **404 `{"error": "The required object does not exist."}`** |
| `KeyError` | 400 `{"error": "The required key does not exist."}` | dito |
| sonstige | 500 `{"error": "Something went wrong please try again later"}` (+ `log_exception`) | dito |
| Body zu groß | `RequestBodySizeLimitMiddleware`: 413 `{"error": "REQUEST_BODY_TOO_LARGE", "detail": "The size of the request body exceeds the maximum allowed size."}` (Grenze `DATA_UPLOAD_MAX_MEMORY_SIZE = FILE_SIZE_LIMIT`, Default 5 242 880 Byte) | `apps/api/plane/middleware/request_body_size.py`; `SET/common.py` Z. 389, 403 |
| HTTP-Methode nicht in `http_method_names` | 405 `{"detail": "Method \"X\" not allowed."}` | DRF |

Endpunktspezifische Fehlertexte stehen in 2.2.

#### 2.1.5 Paginierung (`UT/paginator.py`, `BasePaginator.paginate` Z. 655–745)

| Aspekt | Wert |
|---|---|
| Query `per_page` | Default **1000** (Ausnahme: Stickies 20, Instanz-Workspaces 10); Max = `max(max_per_page, default_per_page)` = 1000 (Instanz-Workspaces 10); Nicht-Integer → 400 `{"detail": "Invalid per_page parameter."}`; zu groß → 400 `{"detail": "Invalid per_page value. Cannot exceed 1000."}` (Z. 643–653) |
| Query `cursor` | Format `"<per_page>:<page>:<is_prev>"` (Default `"{per_page}:0:0"`); ungültig → 400 `{"detail": "Invalid cursor parameter."}`; Paginierungsfehler → 400 `{"detail": "Error in parsing"}` (Z. 677–711) |
| Envelope (alle paginierten v1-Listen) | `{"grouped_by": null, "sub_grouped_by": null, "total_count": n, "next_cursor": "...", "prev_cursor": "...", "next_page_results": bool, "prev_page_results": bool, "count": <Einträge dieser Seite>, "total_pages": n, "total_results": n, "extra_stats": null, "results": [...]}` (Z. 728–743) |
| `total_count_queryset` | nur `GET {P}/work-items/`: `total_count` = alle `Issue.issue_objects` des Projekts (ignoriert sonstige Filter) (`V1V/issue.py` Z. 389, 433–438) |
| Unpaginierte Listen in v1 | `GET {P}/work-items/{id}/attachments/`, `GET {P}/members/`, `GET {W}/members/`, `GET .../relations/`, `GET .../cycles/?cycle_view=current`, `GET {W}/invitations/`, `GET {W}/issues/search/` (eigene Struktur) |

Details zu `OffsetPaginator`/Cursor-Semantik: A03 2.2 (`migration/analysis/03-api-intern-workspace-projekt-user.md`).

#### 2.1.6 Dynamische Felder `fields`/`expand` (`V1S/base.py`)

| Mechanismus | Verhalten | Z. |
|---|---|---|
| `fields=a,b,c` | **Wirksam** (anders als in der App-API, A03 2.3): alle Serializer-Felder, die nicht in `fields` stehen, werden entfernt – auch `id`. Unbekannte Namen werden ignoriert; `?fields=foo` ergibt `{}` je Objekt. Nur dort wirksam, wo die View `fields=self.fields` übergibt (siehe Spalte „fields/expand“ in 2.2). | 23–75 |
| `expand=x,y` | Nur Felder, die **in `self.fields`** stehen, werden expandiert. Mapping: `user, default_assignee, project_lead, created_by, updated_by, actor, owned_by, members` → `UserLiteSerializer`; `workspace` → `WorkspaceLiteSerializer`; `project` → `ProjectLiteSerializer`; `state` → `StateLiteSerializer`; `issue` → `IssueSerializer`; `parent` → `IssueLiteSerializer`; `estimate_point` → `EstimatePointSerializer`. Auflösung über die Instanz: Manager → Liste, Model → Objekt, `None` → `null`; Annotationen/MethodFields gleichen Namens bleiben unverändert. Nicht gemappte Namen → `response[name] = getattr(instance, f"{name}_id", None)`. | 77–141 |
| Sonderfall `IssueSerializer` | `assignees`/`labels` sind write-only `ListField`s; `to_representation` liefert immer Listen von ID-Strings, mit `expand=assignees` → `UserLiteSerializer[]`, mit `expand=labels` → `LabelSerializer[]` (`V1S/issue.py` Z. 322–351) | |
| Sonderfall `IssueExpandSerializer` | liest `expand` aus `self.context["expand"]` (wird nirgends gesetzt ⇒ `labels`/`assignees` immer ID-Listen) (`V1S/issue.py` Z. 842–884) | |

#### 2.1.7 Middleware mit Bezug zu v1 (`SET/common.py` Z. 122–136)

| Middleware | Wirkung | Quelle |
|---|---|---|
| `crum.CurrentRequestUserMiddleware` | `BaseModel.save()` setzt `created_by` (beim Anlegen) bzw. `updated_by` (beim Ändern) aus dem aktuellen Request-User – funktioniert auch mit API-Key, weil DRF `request._request.user` setzt; anonym ⇒ `created_by = updated_by = None` | `M/base.py` Z. 23–43 |
| `plane.middleware.logger.APITokenLogMiddleware` | Für **jeden** Request mit Header `X-Api-Key` (auch außerhalb `/api/v1/`) wird asynchron (`process_logs.delay`) ein `APIActivityLog` gespeichert: `token_identifier = HMAC-SHA256(SECRET_KEY, api_key)`, `path`, `method`, `query_params`, `headers` (mit `[REDACTED]` für `x-api-key`, `authorization`, `cookie`), `body` (Request), `response_body`, `response_code`, `ip_address`, `user_agent`; Binärinhalte (PNG/JPEG/PDF-Signatur) → `"[Binary Content]"`, nicht UTF-8 → `"[Could not decode content]"`. Aufbewahrung `API_ACTIVITY_LOG_RETENTION_DAYS` (Default 14) via Cleanup-Task. | `apps/api/plane/middleware/logger.py` Z. 80–161; `apps/api/plane/bgtasks/logger_task.py`; `SET/common.py` Z. 493; `apps/api/plane/bgtasks/cleanup_task.py` Z. 85–90, 162–166 |
| `plane.middleware.request_body_size.RequestBodySizeLimitMiddleware` | 413 bei zu großem Body (2.1.4) | |
| `plane.middleware.logger.RequestLoggerMiddleware` | strukturiertes Request-Log (`plane.api.request`) | `apps/api/plane/middleware/logger.py` Z. 23–77 |
| `ReadReplicaRoutingMiddleware` (optional) | GET/HEAD/OPTIONS auf Replica, wenn `use_read_replica = True` | `apps/api/plane/middleware/db_routing.py`; A03 |

#### 2.1.8 In v1 verwendete Permission-Klassen (`PERM/project.py`, `PERM/workspace.py`; `apps/api/plane/utils/permissions/*` ist inhaltsgleich)

Alle Klassen geben für anonyme Nutzer `False` zurück. „PM aktiv“ = `ProjectMember(member=user, project_id=view.project_id, workspace__slug=view.workspace_slug, is_active=True)`; „WM aktiv“ = `WorkspaceMember(member=user, workspace__slug=view.workspace_slug, is_active=True)`.

| Klasse | SAFE (GET/HEAD/OPTIONS) | POST | PATCH/PUT/DELETE |
|---|---|---|---|
| `ProjectBasePermission` | WM aktiv (beliebige Rolle) | **WM aktiv mit Rolle A oder M** (kein Projektbezug!) | PM aktiv mit Rolle A **oder** (PM aktiv beliebiger Rolle **und** WM aktiv Rolle A) |
| `ProjectMemberPermission` | PM aktiv | PM aktiv Rolle A/M | PM aktiv Rolle A/M |
| `ProjectEntityPermission` | PM aktiv (bei gesetztem `view.project_identifier`: PM aktiv über `project__identifier`) | PM aktiv Rolle A/M | PM aktiv Rolle A/M |
| `ProjectAdminPermission` | alle Methoden: PM aktiv Rolle A **oder** (PM aktiv beliebiger Rolle und WM aktiv Rolle A) | ← | ← |
| `ProjectLitePermission` | alle Methoden: PM aktiv (jede Rolle) | ← | ← |
| `WorkSpaceAdminPermission` | alle Methoden: WM aktiv Rolle **A oder M** (Name irreführend) | ← | ← |
| `WorkspaceOwnerPermission` | alle Methoden: WM aktiv Rolle A | ← | ← |
| `WorkspaceUserPermission` | alle Methoden: WM aktiv (jede Rolle) | ← | ← |
| `IsAuthenticated` (nur) | gültiger API-Key | ← | ← |

Zusätzlich in Views: `user_has_issue_permission(user_id, project_id, issue, allowed_roles, allow_creator)` (`V1V/issue.py` Z. 167–179): `True`, wenn `allow_creator` und `user_id == issue.created_by_id`; sonst `ProjectMember(project_id, member_id=user_id, is_active=True[, role__in=allowed_roles])` existiert.

#### 2.1.9 OpenAPI-Konfiguration

| Element | Inhalt | Quelle |
|---|---|---|
| Aktivierung | Env `ENABLE_DRF_SPECTACULAR=1` → `REST_FRAMEWORK["DEFAULT_SCHEMA_CLASS"] = "drf_spectacular.openapi.AutoSchema"`, App `drf_spectacular`, Import von `SPECTACULAR_SETTINGS` | `SET/common.py` Z. 602–607 |
| Routen | `GET /api/schema/` (YAML/JSON), `GET /api/schema/swagger-ui/`, `GET /api/schema/redoc/` | `apps/api/plane/urls.py` Z. 27–40 |
| Tote Routen-Datei | `V1U/schema.py` definiert dieselben Routen unter `/api/v1/schema/…`, ist aber **nicht** in `V1U/__init__.py` eingebunden | `V1U/schema.py`, `V1U/__init__.py` |
| Metadaten | `TITLE` „The Plane REST API“, `DESCRIPTION` mit Link developers.plane.so, `CONTACT` (Plane, plane.so, support@plane.so), `VERSION` „0.0.1“, `LICENSE` GNU AGPLv3 | `SET/openapi.py` Z. 11–31 |
| Schema-Optionen | `SERVE_INCLUDE_SCHEMA: False`, `SCHEMA_PATH_PREFIX: "/api/v1/"`, `SCHEMA_CACHE_TIMEOUT: 0`, `COMPONENT_NO_READ_ONLY_REQUIRED: True`, `COMPONENT_SPLIT_REQUEST: True`, `ENUM_NAME_OVERRIDES` (`ModuleStatusEnum` → `plane.db.models.module.ModuleStatus`, `IntakeWorkItemStatusEnum` → `plane.db.models.intake.IntakeIssueStatus`), `AUTHENTICATION_WHITELIST` = nur `APIKeyAuthentication`, `REST_FRAMEWORK["SCHEMA_COERCE_PATH_PK"] = False` (Pfadparameter heißen `pk`, nicht `id`) | `SET/openapi.py` Z. 32–301; `SET/common.py` Z. 151 |
| Server | `http://localhost:8000` („Local“), `https://api.plane.so` („Production“) | `SET/openapi.py` |
| Preprocessing-Hook | `preprocess_filter_api_v1_paths`: nur Pfade mit Präfix `/api/v1/`, **ohne PUT**, **ohne** Pfade mit `server` (⇒ `assets/user-assets/server/…` undokumentiert) | `OA/hooks.py` Z. 14–23 |
| Security-Schema | `ApiKeyAuthentication`: `type: apiKey, in: header, name: X-API-Key` | `OA/auth.py`; registriert in `V1/apps.py` `ready()` |
| Tags (mit Beschreibungstexten) | Assets, Cycles, Intake, Labels, Members, Modules, Projects, States, Users, Work Item Activity, Work Item Attachments, Work Item Comments, Work Item Links, Work Items. Von Decorators zusätzlich verwendet, aber nicht in `TAGS` beschrieben: „Workspaces“, „Work Item Relations“, „Stickies“, „Estimates“, „Estimate Points“ | `SET/openapi.py` `TAGS`; `OA/decorators.py` |
| Decorators | `user_docs, workspace_docs, project_docs, cycle_docs, issue_docs, intake_docs, asset_docs, work_item_docs, label_docs, issue_link_docs, issue_comment_docs, issue_activity_docs, issue_attachment_docs, work_item_relation_docs, module_docs, module_issue_docs, state_docs, sticky_docs, estimate_docs, estimate_point_docs` – setzen Tag, Default-Pfadparameter (`slug`, ggf. `project_id`) und Default-Responses 401/403/404 | `OA/decorators.py` |
| Wiederverwendbare Parameter | Pfad: `slug, project_id, pk (Projekt), project_identifier, issue_identifier, asset_id, cycle_id, module_id, pk (Modul), issue_id, state_id, pk (Label), pk (Kommentar), pk (Link), pk (Anhang), pk (Aktivität), estimate_id`; Query: `cursor, per_page, external_id, external_source, order_by, search (optional), search (Pflicht), limit, workspace_search, project_id, cycle_view, fields, expand` | `OA/parameters.py` |
| `operation_id`s | siehe Spalte „operationId“ in 2.2 | Views |
| Hilfsfunktion | `generate_operation_summary` (nicht in Settings eingehängt, ungenutzt) | `OA/hooks.py` Z. 26–56 |

### 2.2 v1-Endpunkt-Inventar (alle Routen, Präfix `/api/v1/`)

**Legende:** „f/e“ = View reicht `fields`/`expand` an den Serializer durch (✓) oder nicht (–). „RL“ = API-Key-Rate-Limit aktiv. Alle Endpunkte erfordern einen gültigen API-Key. „PM“ = aktives Projektmitglied; Rollen A/M/G wie oben. Wo nicht anders angegeben, gelten zusätzlich die generischen Fehler aus 2.1.4 (insbesondere **404 `{"error": "The requested resource does not exist."}`** bei jedem `.get()` auf ein nicht vorhandenes Objekt).

**Format von Serializer-Fehlern (DRF, gilt für alle Tabellen):** Feldvalidierung → `{"<feld>": ["<Text>"]}`; `ValidationError("<Text>")` aus `validate()` → `{"non_field_errors": ["<Text>"]}`; `ValidationError({...})` aus `validate()` → Werte in Listen gewickelt (`{"project_lead": ["…"]}`); `ValidationError({...})` aus `create()`/`update()` (also während `save()`) → Dict **unverändert** (`{"error": "…"}`), `ValidationError("<Text>")` aus `save()` → `["<Text>"]` (sofern die View sie nicht selbst abfängt). In den Tabellen sind die Texte der Kürze halber teils ohne diese Hülle notiert.

#### 2.2.1 User (`V1U/user.py`)

| ID | Methode | Pfad | View (Datei Z.) | operationId | Berechtigung | Request | Response | Besonderheiten |
|---|---|---|---|---|---|---|---|---|
| V-USR-01 | GET | `/api/v1/users/me/` | `UserEndpoint.get` (`V1V/user.py` Z. 34) | `get_current_user` | `IsAuthenticated`; RL | – | 200 `UserLiteSerializer`: `id, first_name, last_name, email, avatar, avatar_url, display_name` | f/e – |

#### 2.2.2 Projekte (`V1U/project.py`)

| ID | Methode | Pfad | View (Z. in `V1V/project.py`) | operationId | Berechtigung | Request | Response | Seiteneffekte / Besonderheiten |
|---|---|---|---|---|---|---|---|---|
| V-PRJ-01 | GET | `{W}/projects/` | `ProjectListCreateAPIEndpoint.get` (167) | `list_projects` | `ProjectBasePermission` (SAFE: WM aktiv, jede Rolle) | Query: `cursor`, `per_page`, `order_by` ∈ `PROJECT_ORDER_BY_ALLOWLIST` = {`created_at`, `updated_at`, `name`, `network`, `sort_order`} (mit optionalem `-`; ungültig → Default `sort_order`) (`UT/order_queryset.py` Z. 57–63), `fields`, `expand` | 200 paginiert `ProjectSerializer` (2.4.1) | Menge: Projekte des Workspace, in denen der User **aktives** Mitglied ist **oder** `network = 2` (Public); **archivierte Projekte sind enthalten**. Annotationen: `is_member`, `total_members` (aktiv, ohne Bots), `total_cycles`, `total_modules`, `member_role`, `is_deployed` (existiert `DeployBoard` für das Projekt), `sort_order` (aus eigener `ProjectMember`-Zeile; `null` bei Nicht-Mitgliedschaft) (Z. 85–145, 173–196). f/e ✓ |
| V-PRJ-02 | POST | `{W}/projects/` | `…ListCreateAPIEndpoint.post` (224) | `create_project` | `ProjectBasePermission` (POST: WM aktiv Rolle **A oder M**) | `ProjectCreateSerializer` (2.3): `name`, `identifier`, `description`, `project_lead`, `default_assignee`, `icon_prop`, `emoji`, `cover_image`, `module_view`, `cycle_view`, `issue_views_view`, `page_view`, `intake_view`, `guest_view_all_features`, `archive_in` (0–12), `close_in` (0–12), `timezone`, `external_source`, `external_id`, `is_issue_type_enabled`, `is_time_tracking_enabled` (**nicht** schreibbar: `network`, `logo_props`, `description_html`) | 201 `ProjectSerializer` (mit Annotationen); 400 Serializer-Fehler (`"Project name cannot contain special characters."`, `"Project identifier cannot contain special characters."`, `{"project_lead": "The provided user is not a member of this workspace."}`, `"Default assignee should be a user in the workspace"`); 404 `{"error": "Workspace does not exist"}`; 409 `{"name": "The project name is already taken"}`; 409 `{"identifier": "The project identifier is already taken"}` (für **jede** DRF-`ValidationError` aus `create()`, also auch „Project Identifier is required“); 500 `{"error": "An unexpected error occurred"}` | Logik 3.2: Transaktion mit Projekt, Admin-Mitgliedschaft des Erstellers, Admin-Mitgliedschaft des `project_lead`, 6 Default-States; `model_activity("project", created)` nach Commit. f/e – |
| V-PRJ-03 | GET | `{W}/projects-lite/` | `ProjectListLiteAPIEndpoint.get` (394) | `list_projects_lite` | `ProjectBasePermission` (SAFE) | Query: `cursor`, `per_page`, `order_by` (Allowlist wie V-PRJ-01, Default `-created_at`), `include_archived` (`true`/`1`, case-insensitiv; Default `false`) | 200 paginiert `ProjectLiteSerializer`: `id, identifier, name, cover_image, icon_prop, emoji, description, cover_image_url, archived_at`; 404 `{"error": "Provided workspace does not exist"}` | Menge wie V-PRJ-01; archivierte nur mit `include_archived`. f/e – |
| V-PRJ-04 | GET | `{W}/projects/{pk}/` | `ProjectDetailAPIEndpoint.get` (516) | `retrieve_project` | `ProjectBasePermission` (SAFE) | `fields`, `expand` | 200 `ProjectSerializer` (ohne `sort_order`, da nicht annotiert) | Sichtbarkeit wie V-PRJ-01 (sonst 404). f/e ✓ |
| V-PRJ-05 | PATCH | `{W}/projects/{pk}/` | `…DetailAPIEndpoint.patch` (546) | `update_project` | `ProjectBasePermission` (PM Rolle A oder PM + WS-Admin) | `ProjectUpdateSerializer` = Create-Felder + `default_state`, `estimate` | 200 `ProjectSerializer`; 400 `{"error": "Archived project cannot be updated"}`; 400 Serializer-Fehler aus `validate()` (Sonderzeichen, `project_lead`, `default_assignee`); 404 `{"error": "Project does not exist"}`; 409 `{"name": "The project name is already taken"}`; **409 `{"identifier": "The project identifier is already taken"}` auch für die in `update()` geprüften Fehler „Default state should be a state in the project“ und „Estimate should be a estimate in the project“** (die View fängt jede DRF-`ValidationError` aus `save()` so ab, Z. 606–610) | Logik 3.3: Bei `intake_view` true und fehlendem Default-Intake wird `Intake(name="{Projektname} Intake", is_default=True)` angelegt; `model_activity("project", updated)`. Bei `IntegrityError` ohne „already exists“ liefert die View **`None`** → 500. f/e – |
| V-PRJ-06 | DELETE | `{W}/projects/{pk}/` | `…DetailAPIEndpoint.delete` (623) | `delete_project` | `ProjectBasePermission` (wie PATCH) | – | 204 | `UserFavorite(entity_type="project", entity_identifier=pk, project_id=pk)` löschen; `project.delete()` (Soft-Delete, A02a); `webhook_activity(event="project", verb="deleted", event_id=project.id)` |
| V-PRJ-07 | POST | `{W}/projects/{project_id}/archive/` | `ProjectArchiveUnarchiveAPIEndpoint.post` (666) | `archive_project` | `ProjectBasePermission` – **POST-Zweig: jedes aktive WS-Mitglied mit Rolle A/M, ohne Projektbezug** | `{}` | 204 | `archived_at = now`; alle `UserFavorite` des Projekts löschen. Kein Activity/Webhook. |
| V-PRJ-08 | DELETE | `{W}/projects/{project_id}/archive/` | `…ArchiveUnarchiveAPIEndpoint.delete` (690) | `unarchive_project` | `ProjectBasePermission` (PM Rolle A oder PM + WS-Admin) | – | 204 | `archived_at = None` |
| V-PRJ-09 | GET | `{W}/projects/{project_id}/summary/` | `ProjectSummaryAPIEndpoint.get` (718) | (ohne Decorator) | `WorkSpaceAdminPermission` (WM aktiv Rolle A/M; **keine Projektmitgliedschaft nötig**, auch für Secret-Projekte) | Query `fields` ⊆ {`members`, `states`, `labels`, `cycles`, `modules`, `issues`, `intakes`, `pages`} (leer/ungültig → alle) | 200 `{"id", "name", "identifier", "counts": {<feld>: int}}`; 404 `{"error": "Project not found"}` | Zählungen: `members` = aktive `ProjectMember` (inkl. Bots), `states` (Manager ohne Triage-Gruppe), `labels`, `cycles`, `modules`, `issues` = `Issue.objects` ohne State-Gruppe `triage` (Default-Manager), `intakes` = alle `IntakeIssue`, `pages` = `ProjectPage` (Z. 702–815). |

#### 2.2.3 States (`V1U/state.py`)

| ID | Methode | Pfad | View (Z. in `V1V/state.py`) | operationId | Berechtigung | Request | Response | Besonderheiten |
|---|---|---|---|---|---|---|---|---|
| V-STA-01 | GET | `{P}/states/` | `StateListCreateAPIEndpoint.get` (155) | `list_states` | SAFE: `ProjectEntityPermission` (PM) | `cursor`, `per_page`, `fields`, `expand` | 200 paginiert `StateSerializer` (2.4) | Queryset: Projekt, User aktives PM, `is_triage=False`, Projekt nicht archiviert; Manager schließt Gruppe `triage` aus; Sortierung Model-Default `sequence`. f/e ✓ |
| V-STA-02 | POST | `{P}/states/` | `…ListCreate….post` (86) | `create_state` | **`ProjectAdminPermission`** | `StateSerializer`: `name`, `description`, `color`, `sequence`, `group` (≠ `triage`), `default`, `is_triage`, `external_source`, `external_id` | **200** (nicht 201) `StateSerializer`; 400 `"Cannot create triage state"`; 409 `{"error": "State with the same external id and external source already exists", "id"}`; 409 `{"error": "State with the same name already exists in the project", "id"}` (IntegrityError) | `default=true` setzt alle anderen States des Projekts auf `default=false` (Transaktion, `V1S/state.py`); `sequence` wird beim Anlegen auf `max(sequence)+15000` überschrieben (`M/state.py` `save`); `slug = slugify(name)` |
| V-STA-03 | GET | `{P}/states/{state_id}/` | `StateDetailAPIEndpoint.get` (211) | `retrieve_state` | `ProjectEntityPermission` | `fields`, `expand` | 200 `StateSerializer` | f/e ✓ |
| V-STA-04 | PATCH | `{P}/states/{state_id}/` | `…Detail….patch` (283) | `update_state` | `ProjectAdminPermission` | `StateSerializer` partiell | 200; 400; 409 `{"error": "State with the same external id and external source already exists", "id"}` (nur wenn `external_id` gesendet **und** von bisherigem abweichend **und** Kombination mit `external_source` (gesendet oder bisher) existiert) | Umschalten auf `default` wie V-STA-02 |
| V-STA-05 | DELETE | `{P}/states/{state_id}/` | `…Detail….delete` (236) | `delete_state` | `ProjectAdminPermission` | – | 204; 400 `{"error": "Default state cannot be deleted"}`; 400 `{"error": "The state is not empty, only empty states can be deleted"}` (irgendein `Issue` mit diesem State, Default-Manager) | Soft-Delete |

#### 2.2.4 Labels (`V1U/label.py`; Views in `V1V/issue.py`)

| ID | Methode | Pfad | View (Z.) | operationId | Berechtigung | Request | Response | Besonderheiten |
|---|---|---|---|---|---|---|---|---|
| V-LBL-01 | GET | `{P}/labels/` | `LabelListCreateAPIEndpoint.get` (1006) | `list_labels` | SAFE: `ProjectMemberPermission` (PM) | `cursor`, `per_page`, `fields`, `expand` (Doku nennt `order_by`, wird **nicht** ausgewertet) | 200 paginiert `LabelSerializer` (`__all__`) | Queryset: Projekt, User aktives PM, Projekt nicht archiviert, Sortierung `-created_at` (Z. 900–918). f/e ✓ |
| V-LBL-02 | POST | `{P}/labels/` | `….post` (933) | `create_label` | **`ProjectAdminPermission`** | `LabelCreateUpdateSerializer`: `name`, `color`, `description`, `external_source`, `external_id`, `parent`, `sort_order` | 201 `LabelSerializer`; 400; 409 externe ID wie States (`"Label with the same external id and external source already exists"`); 409 `{"error": "Label with the same name already exists in the project", "id"}` | `parent` wird nicht auf gleiches Projekt geprüft |
| V-LBL-03 | GET | `{P}/labels/{pk}/` | `LabelDetailAPIEndpoint.get` (1041) | `get_labels` | `ProjectMemberPermission` | – | 200 `LabelSerializer` | f/e – |
| V-LBL-04 | PATCH | `{P}/labels/{pk}/` | `….patch` (1071) | `update_label` | `ProjectAdminPermission` | `LabelCreateUpdateSerializer` partiell | 200 `LabelSerializer`; 409 externe ID (Prüfung **nur**, wenn `external_id` **und** `external_source` gesendet; schließt eigenes Label aus) | Doppelter Name → IntegrityError → 400 `{"error": "The payload is not valid"}` |
| V-LBL-05 | DELETE | `{P}/labels/{pk}/` | `….delete` (1116) | `delete_label` | `ProjectAdminPermission` | – | 204 | Soft-Delete; keine Bereinigung von `IssueLabel` hier (siehe A02/A04) |

#### 2.2.5 Work Items – Kern (`V1U/work_item.py`; `V1V/issue.py`)

Jede Zeile existiert **zweimal**: Alt-Präfix `{P}/issues/…` (URL-Namen `issue`, `link`, `comment`, `activity`, `attachment`, `issue-attachment`) und neues Präfix `{P}/work-items/…` (URL-Namen `work-item-*`). Ausnahme: Relationen nur unter `work-items/`; Anhänge heißen alt `issue-attachments/`, neu `attachments/`.

| ID | Methode | Pfad (neu / alt) | View (Z.) | operationId | Berechtigung | Request | Response | Seiteneffekte / Besonderheiten |
|---|---|---|---|---|---|---|---|---|
| V-WI-01 | GET | `{P}/work-items/` / `{P}/issues/` | `IssueListCreateAPIEndpoint.get` (317) | `list_work_items` | `ProjectEntityPermission` (PM) | `cursor`, `per_page`, `order_by` (Allowlist `ISSUE_ORDER_BY_ALLOWLIST`: `created_at, updated_at, sequence_id, sort_order, target_date, start_date, completed_at, archived_at, priority, state__name, state__group, assignees__first_name, labels__name, issue_module__module__name`; Default `-created_at`) (`UT/order_queryset.py` Z. 18–33), `external_id` + `external_source`, `fields`, `expand`; **abgewiesen:** `pql`, `filters` | 200 paginiert `IssueSerializer` (2.4.2), `total_count` = alle Work Items des Projekts; **mit `external_id`+`external_source`: einzelnes `IssueSerializer`-Objekt (keine Liste)** bzw. 404; 400 `{"pql": "PQL and structured filters are not supported on this Plane edition. Remove the pql/filters parameter and filter results client-side, or use a Plane edition that supports work item query filtering.", "unsupported_parameters": [...]}` | Menge: `Issue.issue_objects` (ohne Entwürfe, Archivierte, Triage-/abgelehnte Intake-Issues; Manager-Definition A04) des Projekts. Sortierlogik 3.4. Annotationen `cycle_id`, `link_count`, `attachment_count`, `sub_issues_count` werden berechnet, aber vom Serializer **nicht** ausgegeben. f/e ✓ |
| V-WI-02 | POST | `{P}/work-items/` / `{P}/issues/` | `….post` (456) | `create_work_item` | `ProjectEntityPermission` (PM Rolle A/M; Gäste nicht) | `IssueSerializer` (schreibbar: `name`, `description_html`, `description_binary`, `priority` ∈ {`urgent`,`high`,`medium`,`low`,`none`}, `state`, `parent`, `estimate_point`, `point`, `start_date`, `target_date`, `sort_order`, `is_draft`, `type`/`type_id`, `external_source`, `external_id`, `assignees[]`, `labels[]`, `created_by`) + Sonderfelder `created_at`, `created_by` (ISO-Zeit/User-UUID, werden nach dem Speichern direkt gesetzt) | 201 `IssueSerializer` (Daten **vor** dem Überschreiben von `created_at`/`created_by`); 400 Validierungsfehler (3.5); 409 `{"error": "Issue with the same external id and external source already exists", "id"}` | Logik 3.5. `issue_activity("issue.activity.created", notification=True)`, `model_activity("issue", created)` |
| V-WI-03 | GET | `{P}/work-items/{pk}/` / `{P}/issues/{pk}/` | `IssueDetailAPIEndpoint.get` (582) | `retrieve_work_item` | `ProjectEntityPermission` | `fields`, `expand` (Doku nennt zusätzlich `external_id`, `external_source`, `order_by` – ignoriert) | 200 `IssueSerializer` | `Issue.issue_objects` ⇒ archivierte/Entwürfe/Triage → 404. f/e ✓ |
| V-WI-04 | PATCH | `{P}/work-items/{pk}/` / `{P}/issues/{pk}/` | `….patch` (778) | `update_work_item` | `ProjectEntityPermission` (A/M) | `IssueSerializer` partiell; `is_draft` read-only bei Update; `deleted_at`, `archived_at`, `sequence_id`, `completed_at` read-only | 200 `IssueSerializer`; 400; 409 externe ID (Regel wie V-STA-04) | Lädt mit `Issue.objects` (auch archivierte/Entwürfe änderbar!). `issue_activity("issue.activity.updated", requested_data = nur schreibbare Felder (`writable_data`), notification=True)`; `model_activity("issue", updated)` |
| V-WI-05 | DELETE | `{P}/work-items/{pk}/` / `{P}/issues/{pk}/` | `….delete` (852) | `delete_work_item` | `ProjectEntityPermission` (A/M) + View: Ersteller **oder** PM Rolle 20 (WS-Admin-Regel gilt hier **nicht**) | – | 204; 403 `{"error": "Only admin or creator can delete the work item"}` | Soft-Delete; `issue_activity("issue.activity.deleted")`; **kein** `model_activity`/Webhook-Aufruf in der View |
| V-WI-06 | GET | `{W}/work-items/{project_identifier}-{issue_identifier}/` / `{W}/issues/{…}-{…}/` | `WorkspaceIssueAPIEndpoint.get` (236) | `get_workspace_work_item` | `ProjectEntityPermission` mit `project_identifier` (PM des Projekts mit diesem Identifier) | Pfad z. B. `PROJ-42`; `fields`, `expand` | 200 `IssueSerializer`; 404 `{"error": "Work item not found"}` wenn `issue_identifier` nicht dezimal; 404 generisch wenn nicht gefunden | Django-Pfadmuster `<str>-<str>` (Split am **ersten** `-`, Identifier können kein `-` enthalten); Lookup `workspace__slug`, `project__identifier`, `sequence_id`; `issue_objects`. Bei fehlenden Pfadteilen liefert die View `None` (nicht erreichbar über das Muster). |
| V-WI-07 | GET | `{W}/work-items/search/` / `{W}/issues/search/` | `IssueSearchEndpoint.get` (2274) | `search_work_items` | nur `IsAuthenticated`; Scoping im Queryset (PM aktiv) | Query `search` (Pflicht laut Doku), `limit` (Default 10, `int()`; Nicht-Zahl → 500), `workspace_search` (`"false"` Default), `project_id` | 200 `{"issues": [{"name", "id", "sequence_id", "project__identifier", "project_id", "workspace__slug"}]}`; ohne `search` → 200 `{"issues": []}` | Treffer: `name ICONTAINS q` ODER `project__identifier ICONTAINS q` ODER `sequence_id = <jede ganze Zahl im Suchstring>`; nur `issue_objects`, aktive Mitgliedschaft, nicht archivierte Projekte; `project_id` nur wirksam, wenn `workspace_search == "false"`; kein Sortierkriterium (DB-Reihenfolge); `distinct()` |

#### 2.2.6 Work-Item-Links

| ID | Methode | Pfad (neu; alt mit `issues/`) | View (Z.) | operationId | Berechtigung | Request | Response | Seiteneffekte / Besonderheiten |
|---|---|---|---|---|---|---|---|---|
| V-LNK-01 | GET | `{WI}/links/` | `IssueLinkListCreateAPIEndpoint.get` (1171) | `list_work_item_links` | `ProjectEntityPermission` | `cursor`, `per_page`, `fields`, `expand` | 200 paginiert `IssueLinkSerializer` (`__all__`: `id, created_at, updated_at, deleted_at, created_by, updated_by, project, workspace, title, url, issue, metadata`) | Sortierung `-created_at`; Projekt nicht archiviert. f/e ✓ |
| V-LNK-02 | POST | `{WI}/links/` | `….post` (1204) | `create_work_item_link` | `ProjectEntityPermission` (A/M) | `IssueLinkCreateSerializer`: `url` (Pflicht, `URLValidator`, nur `http://`/`https://`), `title`, `issue_id` (wird überschrieben); Sonderfeld `created_by` | 201 `IssueLinkSerializer`; 400 `{"url": ["Invalid URL format."]}` / `{"url": ["Invalid URL scheme."]}` / `{"error": "URL already exists for this Issue"}` | Issue muss im Projekt existieren (`Issue.objects`); `crawl_work_item_link_title.delay(link_id, url)` (Titel/Metadaten asynchron, SSRF-geschützt, A04); `created_by_id` aus Body überschreibbar; `issue_activity("link.activity.created", actor_id=created_by)` |
| V-LNK-03 | GET | `{WI}/links/{pk}/` | `IssueLinkDetailAPIEndpoint.get` (1276) | `retrieve_work_item_link` | `ProjectEntityPermission` | `fields`, `expand` | 200 `IssueLinkSerializer` | Zweig `pk is None` (paginierte Liste) über die URL nicht erreichbar |
| V-LNK-04 | PATCH | `{WI}/links/{pk}/` | `….patch` (1316) | `update_issue_link` | `ProjectEntityPermission` (A/M) | `IssueLinkSerializer` partiell (**ohne** URL-Validierung und **ohne** Duplikatprüfung, da nicht der Update-Serializer verwendet wird) | 200 `IssueLinkSerializer` | Bei geänderter URL erneutes Crawling; `issue_activity("link.activity.updated")` |
| V-LNK-05 | DELETE | `{WI}/links/{pk}/` | `….delete` (1357) | `delete_work_item_link` | `ProjectEntityPermission` (A/M) | – | 204 | `issue_activity("link.activity.deleted")`, dann Soft-Delete |

#### 2.2.7 Work-Item-Kommentare

| ID | Methode | Pfad | View (Z.) | operationId | Berechtigung | Request | Response | Seiteneffekte / Besonderheiten |
|---|---|---|---|---|---|---|---|---|
| V-CMT-01 | GET | `{WI}/comments/` | `IssueCommentListCreateAPIEndpoint.get` (1433) | `list_work_item_comments` | **`ProjectLitePermission`** (PM jeder Rolle) | `cursor`, `per_page`, `fields`, `expand` | 200 paginiert `IssueCommentSerializer` (alle `IssueComment`-Felder außer `comment_stripped`, `comment_json`, + `is_member`) | **Alle** Kommentare (auch `access="INTERNAL"`); Sortierung `-created_at`. f/e ✓ |
| V-CMT-02 | POST | `{WI}/comments/` | `….post` (1467) | `create_work_item_comment` | `ProjectLitePermission` (**auch Gäste**) | `IssueCommentCreateSerializer`: `comment_html`, `comment_json`, `access` (`INTERNAL`/`EXTERNAL`), `external_source`, `external_id`; Sonderfelder `created_at`, `created_by` | 201 `IssueCommentSerializer`; 409 `{"error": "Work item comment with the same external id and external source already exists", "id"}` (Prüfung **vor** Validierung, Scope Projekt) | Issue-Existenz wird **nicht** geprüft (ungültige `issue_id` → IntegrityError → 400 „The payload is not valid“). `created_at`/`created_by` aus Body; `actor_id` wird zwar gesetzt, aber **nicht gespeichert** (`update_fields` ohne `actor`) ⇒ `actor` bleibt der API-User. **Keine HTML-Sanitization** im Create-Serializer (nur `IssueCommentSerializer.validate` sanitisiert, wird hier nicht verwendet). `issue_activity("comment.activity.created", actor_id=created_by)`; `model_activity("issue_comment", created)` |
| V-CMT-03 | GET | `{WI}/comments/{pk}/` | `IssueCommentDetailAPIEndpoint.get` (1585) | `retrieve_work_item_comment` | `ProjectLitePermission` | `fields`, `expand` | 200 `IssueCommentSerializer` | f/e ✓ |
| V-CMT-04 | PATCH | `{WI}/comments/{pk}/` | `….patch` (1616) | `update_work_item_comment` | `ProjectLitePermission` – **keine Autorenprüfung** (jedes PM, auch Gast, darf jeden Kommentar ändern) | `IssueCommentCreateSerializer` partiell | 200; 409 externe ID | `edited_at` wird **nicht** gesetzt; `issue_activity("comment.activity.updated")`; `model_activity("issue_comment", updated)` |
| V-CMT-05 | DELETE | `{WI}/comments/{pk}/` | `….delete` (1685) | `delete_work_item_comment` | `ProjectLitePermission` – **keine Autorenprüfung** | – | 204 | Soft-Delete; `issue_activity("comment.activity.deleted")`; kein Webhook-Aufruf |

#### 2.2.8 Work-Item-Aktivitäten

| ID | Methode | Pfad | View (Z.) | operationId | Berechtigung | Request | Response | Besonderheiten |
|---|---|---|---|---|---|---|---|---|
| V-ACT-01 | GET | `{WI}/activities/` | `IssueActivityListAPIEndpoint.get` (1732) | `list_work_item_activities` | `ProjectEntityPermission` | `cursor`, `per_page`, `order_by` ∈ {`created_at`, `updated_at`} (± ; Default `created_at`), `fields`, `expand` | 200 paginiert `IssueActivitySerializer` (alle `IssueActivity`-Felder außer `created_by`, `updated_by`: `id, created_at, updated_at, deleted_at, project, workspace, issue, verb, field, old_value, new_value, comment, issue_comment, actor, old_identifier, new_identifier, epoch`) | Ausgeschlossen: `field IN ("comment", "vote", "reaction", "draft")`; Projekt nicht archiviert. f/e ✓ |
| V-ACT-02 | GET | `{WI}/activities/{pk}/` | `IssueActivityDetailAPIEndpoint.get` (1789) | `retrieve_work_item_activity` | `ProjectEntityPermission` | `fields`, `expand` | 200 `IssueActivitySerializer`; 404 `{"message": "Activity not found.", "code": "NOT_FOUND"}` | gleiche Ausschlüsse |

#### 2.2.9 Work-Item-Anhänge (neu `attachments/`, alt `issue-attachments/`)

| ID | Methode | Pfad | View (Z.) | operationId | Berechtigung | Request | Response | Seiteneffekte / Besonderheiten |
|---|---|---|---|---|---|---|---|---|
| V-ATT-01 | GET | `{WI}/attachments/` | `IssueAttachmentListCreateAPIEndpoint.get` (2024) | `list_work_item_attachments` | **nur `IsAuthenticated`** – keine Mitgliedschaftsprüfung | – | 200 **unpaginierte** Liste `IssueAttachmentSerializer` (`FileAsset` `__all__`, 2.4) | Filter: `issue_id`, `entity_type=ISSUE_ATTACHMENT`, `workspace__slug`, `project_id`, `is_uploaded=True` |
| V-ATT-02 | POST | `{WI}/attachments/` | `….post` (1898) | `create_work_item_attachment` | `IsAuthenticated` + `user_has_issue_permission(allowed_roles=[A,M,G], allow_creator=True)` | `{name (Pflicht), type (Pflicht, ∈ ATTACHMENT_MIME_TYPES), size (Pflicht, int > 0; Zahl als String erlaubt), external_id, external_source}` | 200 `{"upload_data": {url, fields}, "asset_id", "attachment": IssueAttachmentSerializer, "asset_url"}`; 400 `{"error": "Invalid request.", "status": false}` (Name fehlt oder Größe ≤ 0/ungültig); 400 `{"error": "Invalid file type.", "status": false}`; 403 `{"error": "You are not allowed to upload this attachment"}`; 409 `{"error": "Issue with the same external id and external source already exists", "id"}` | Logik 3.7: Größe auf `FILE_SIZE_LIMIT` begrenzt; Key `"{workspace_id}/{uuid4hex}-{sanitize_filename(name)}"`; `FileAsset(is_uploaded=False)`; Presigned POST (S3/MinIO) |
| V-ATT-03 | GET | `{WI}/attachments/{pk}/` | `IssueAttachmentDetailAPIEndpoint.get` (2135) | `retrieve_work_item_attachment` | `user_has_issue_permission(issue=None, allowed_roles=None, allow_creator=False)` = PM aktiv | – | **302** Redirect auf Presigned-GET-URL (`Content-Disposition: attachment; filename=<name>`); 400 `{"error": "The asset is not uploaded.", "status": false}`; 403 `{"error": "You are not allowed to download this attachment"}` | Lookup **ohne** `issue_id`-Bindung (jede Datei des Projekts über beliebige Issue-ID abrufbar) |
| V-ATT-04 | PATCH | `{WI}/attachments/{pk}/` | `….patch` (2197) | `upload_work_item_attachment` | wie V-ATT-02 | Body wird ignoriert (Doku: `{is_uploaded: true}`) | **204** | Wenn noch nicht hochgeladen: `issue_activity("attachment.activity.created", current_instance=Attachment-JSON, notification=True)`, `is_uploaded=True`, `created_by=request.user`; `get_asset_object_metadata.delay` wenn `storage_metadata` leer. Lookup ohne `issue_id`-Bindung. |
| V-ATT-05 | DELETE | `{WI}/attachments/{pk}/` | `….delete` (2060) | `delete_work_item_attachment` | wie V-ATT-02 | – | 204; 403 `{"error": "You are not allowed to delete this attachment"}` | `is_deleted=True`, `deleted_at=now`; `issue_activity("attachment.activity.deleted", notification=True)`; Metadaten-Task falls leer. Lookup ohne `issue_id`-Bindung. |

#### 2.2.10 Work-Item-Relationen (nur `work-items/`)

| ID | Methode | Pfad | View (Z.) | operationId | Berechtigung | Request | Response | Besonderheiten |
|---|---|---|---|---|---|---|---|---|
| V-REL-01 | GET | `{P}/work-items/{issue_id}/relations/` | `IssueRelationListCreateAPIEndpoint.get` (2394) | `list_work_item_relations` | `ProjectEntityPermission` | – (Doku nennt Pagination/`fields`/`expand` – ignoriert) | 200 `{"blocking": [...], "blocked_by": [...], "duplicate": [...], "relates_to": [...], "start_after": [...], "start_before": [...], "finish_after": [...], "finish_before": [...]}`, Elemente `{"project_id": "<uuid>", "issue_id": "<uuid>"}` | Mapping-Regeln 3.8; Relationstyp `implemented_by` wird **nicht** ausgegeben; Filter nur `workspace__slug` (Relationen über Projektgrenzen) |
| V-REL-02 | POST | `{P}/work-items/{issue_id}/relations/` | `….post` (2529) | `create_work_item_relation` | `ProjectEntityPermission` (A/M) | `IssueRelationCreateSerializer`: `relation_type` ∈ {`blocking`, `blocked_by`, `duplicate`, `relates_to`, `start_before`, `start_after`, `finish_before`, `finish_after`}, `issues` (UUID-Liste, min. 1) | 201 Liste `IssueRelationSerializer` (Vorwärtstypen) bzw. `RelatedIssueSerializer` (Rückwärtstypen `blocking`, `start_after`, `finish_after`); 400 Serializer-Fehler | URL-Issue muss in URL-Projekt existieren (`issue_objects`); Ziel-Issues nur Workspace-gebunden (andere Projekte erlaubt), ungültige IDs werden still verworfen; `bulk_create(ignore_conflicts=True, batch_size=10)`; `issue_activity("issue_relation.activity.created", notification=True)`; `project_id` der Relation = URL-Projekt |

#### 2.2.11 Cycles (`V1U/cycle.py`; `V1V/cycle.py`)

| ID | Methode | Pfad | View (Z.) | operationId | Berechtigung | Request | Response | Seiteneffekte / Besonderheiten |
|---|---|---|---|---|---|---|---|---|
| V-CYC-01 | GET | `{P}/cycles/` | `CycleListCreateAPIEndpoint.get` (191) | `list_cycles` | `ProjectEntityPermission` | `cycle_view` ∈ {`all` (Default), `current`, `upcoming`, `completed`, `draft`, `incomplete`}, `cursor`, `per_page`, `fields`, `expand` (Doku nennt `order_by` – ignoriert) | 200 paginiert `CycleSerializer` (2.4.4); **`cycle_view=current`: unpaginierte Liste** | Nur nicht archivierte Cycles; Filter: `current` = `start_date ≤ now ≤ end_date`; `upcoming` = `start_date > now`; `completed` = `end_date < now`; `draft` = beide Daten `null`; `incomplete` = `end_date ≥ now` oder `null`; unbekannter Wert ⇒ wie `all`. Projekt muss existieren (`Project.objects.get`). Zählannotationen 3.9. f/e ✓ |
| V-CYC-02 | POST | `{P}/cycles/` | `….post` (300) | `create_cycle` | `ProjectEntityPermission` (A/M) | `CycleCreateSerializer`: `name`, `description`, `start_date`, `end_date`, `owned_by`, `external_source`, `external_id`, `timezone` | 201 `CycleSerializer` (ohne Zählfelder); 400 `{"error": "Both start date and end date are either required or are to be null"}`; 400 `"Cycles are not enabled for this project"` / `"Start date cannot exceed end date"` / `"Project not found"`; 409 externe ID (`"Cycle with the same external id and external source already exists"`) | Datumskonvertierung in Projektzeitzone (3.9); `owned_by` Default = API-User; `model_activity("cycle", created)` |
| V-CYC-03 | GET | `{P}/cycles-lite/` | `CycleListLiteAPIEndpoint.get` (381) | `list_cycles_lite` | `ProjectEntityPermission` | `cursor`, `per_page`, `order_by` ∈ `CYCLE_ORDER_BY_ALLOWLIST` {`created_at`, `updated_at`, `name`, `start_date`, `end_date`, `sort_order`} (Default `-created_at`) | 200 paginiert `CycleLiteSerializer` (`__all__` Cycle-Felder) | Nicht archivierte Cycles; **kein** Mitgliedschaftsfilter im Queryset (Permission reicht) |
| V-CYC-04 | GET | `{P}/cycles/{pk}/` | `CycleDetailAPIEndpoint.get` (510) | `retrieve_cycle` | `ProjectEntityPermission` | `fields`, `expand` | 200 `CycleSerializer` | Archivierte → 404. f/e ✓ |
| V-CYC-05 | PATCH | `{P}/cycles/{pk}/` | `….patch` (542) | `update_cycle` | `ProjectEntityPermission` (A/M) | `CycleUpdateSerializer` (= Create-Felder) partiell | 200 `CycleSerializer`; 400 `{"error": "Archived cycle cannot be edited"}`; 400 `{"error": "The Cycle has already been completed so it cannot be edited"}` (abgeschlossen und **ohne** `sort_order` im Body); 409 externe ID | **Bug:** Bei abgeschlossenem Cycle mit `sort_order` im Body wird `request_data` reduziert, der Serializer erhält aber `request.data` ⇒ **alle** Felder werden geändert (Z. 560–572). `owned_by` bleibt, wenn nicht gesendet; explizites `null` → API-User. `model_activity("cycle", updated)` |
| V-CYC-06 | DELETE | `{P}/cycles/{pk}/` | `….delete` (616) | `delete_cycle` | `ProjectEntityPermission` (A/M) + View: Ersteller **oder** `ProjectAdminPermission` | – | 204; 403 `{"error": "Only admin or creator can delete the cycle"}` | `issue_activity("cycle.activity.deleted", requested_data={cycle_id, cycle_name, issues[]})`; Soft-Delete; `UserFavorite` (`entity_type="cycle"`) löschen |
| V-CYC-07 | GET | `{P}/cycles/{cycle_id}/cycle-issues/` | `CycleIssueListCreateAPIEndpoint.get` (891) | `list_cycle_work_items` | `ProjectEntityPermission` | `cursor`, `per_page`, `order_by` (Issue-Allowlist; Default `created_at`), `fields`, `expand` | 200 paginiert `IssueSerializer` | `issue_objects` mit nicht gelöschter `CycleIssue`; Cycle-Existenz nicht geprüft (unbekannt → leere Liste). f/e ✓ |
| V-CYC-08 | POST | `{P}/cycles/{cycle_id}/cycle-issues/` | `….post` (957) | `add_cycle_work_items` | `ProjectEntityPermission` (A/M) | `{"issues": ["<uuid>", ...]}` | 200 **Liste aller** `CycleIssueSerializer` des Cycles (`__all__` + `sub_issues_count`); 400 `{"error": "Work items are required", "code": "MISSING_WORK_ITEMS"}`; 400 `{"code": "CYCLE_COMPLETED", "message": "The Cycle has already been completed so no new issues can be added"}` | Logik 3.10 (Verschieben aus anderen Cycles); `issue_activity("cycle.activity.created", notification=True)` |
| V-CYC-09 | GET | `{P}/cycles/{cycle_id}/cycle-issues/{issue_id}/` | `CycleIssueDetailAPIEndpoint.get` (1117) | `retrieve_cycle_work_item` | `ProjectEntityPermission` | `fields`, `expand` | 200 `CycleIssueSerializer` (`id, created_at, updated_at, deleted_at, created_by, updated_by, project, workspace, issue, cycle` – `sub_issues_count` fehlt, da nicht annotiert) | f/e ✓ |
| V-CYC-10 | DELETE | `{P}/cycles/{cycle_id}/cycle-issues/{issue_id}/` | `….delete` (1140) | `delete_cycle_work_item` | `ProjectEntityPermission` (A/M) | – | 204 | Soft-Delete der Zuordnung; `issue_activity("cycle.activity.deleted", requested_data={cycle_id, issues:[issue_id]})` |
| V-CYC-11 | POST | `{P}/cycles/{cycle_id}/transfer-issues/` | `TransferCycleIssueAPIEndpoint.post` (1221) | `transfer_cycle_work_items` | `ProjectEntityPermission` (A/M) | `{"new_cycle_id": "<uuid>"}` | 200 `{"message": "Success"}`; 400 `{"error": "New Cycle Id is required"}`; 400 `{"error": "The old cycle is not completed yet"}` (nur wenn `end_date` gesetzt **und** > now; Draft-Cycles ohne Datum sind übertragbar); 400 `{"error": "The cycle where the issues are transferred is already completed"}`; 400 `{"error": "Source cycle not found"}` | Logik 3.9 (Progress-Snapshot, nur offene Work Items). Unbekannte `new_cycle_id` → `AttributeError` → 500. |
| V-CYC-12 | POST | `{P}/cycles/{cycle_id}/archive/` | `CycleArchiveUnarchiveAPIEndpoint.post` (800) | `archive_cycle` | `ProjectEntityPermission` (A/M) | `{}` | 204; 400 `{"error": "Only completed cycles can be archived"}` (`end_date` null oder ≥ now) | `archived_at=now`; `UserFavorite` löschen |
| V-CYC-13 | GET | `{P}/archived-cycles/` | `….get` (778) | `list_archived_cycles` | `ProjectEntityPermission` | `cursor`, `per_page`, `fields`, `expand` | 200 paginiert `CycleSerializer` inkl. `total_estimates`, `completed_estimates`, `started_estimates` | Zählungen ohne `distinct` (unkritisch, da alle Aggregate denselben Join-Pfad `issue_cycle → issue` nutzen); Schätzsummen = `Sum(issue_cycle__issue__estimate_point__key)` (`EstimatePoint.key` Integer) |
| V-CYC-14 | DELETE | `{P}/archived-cycles/{cycle_id}/unarchive/` | `….delete` (831) | `unarchive_cycle` | `ProjectEntityPermission` (A/M) | – | 204 | `archived_at=None` (auch für nicht archivierte Cycles) |

#### 2.2.12 Modules (`V1U/module.py`; `V1V/module.py`)

| ID | Methode | Pfad | View (Z.) | operationId | Berechtigung | Request | Response | Seiteneffekte / Besonderheiten |
|---|---|---|---|---|---|---|---|---|
| V-MOD-01 | GET | `{P}/modules/` | `ModuleListCreateAPIEndpoint.get` (266) | `list_modules` | `ProjectEntityPermission` | `cursor`, `per_page`, `fields`, `expand` | 200 paginiert `ModuleSerializer` (2.4.5) | Nicht archivierte Module; Zählannotationen mit `distinct=True`. f/e ✓ |
| V-MOD-02 | POST | `{P}/modules/` | `….post` (194) | `create_module` | `ProjectEntityPermission` (A/M) | `ModuleCreateSerializer`: `name`, `description`, `start_date`, `target_date`, `status` ∈ {`backlog`, `planned`, `in-progress`, `paused`, `completed`, `cancelled`}, `lead`, `members[]`, `external_source`, `external_id` | 201 `ModuleSerializer`; 400 `"Modules are not enabled for this project"`, `"Start date cannot exceed target date"`; 400 `{"id", "code": "MODULE_NAME_ALREADY_EXISTS", "error": "Module with this name already exists", "message": "Module with this name already exists"}`; 409 externe ID (`"Module with the same external id and external source already exists"`) | `members` werden auf Projektmitglieder (beliebiger Status!) gefiltert, ungültige still verworfen; `ModuleMember`-Bulk; `model_activity("module", created)`; `lead` ohne Mitgliedschaftsprüfung |
| V-MOD-03 | GET | `{P}/modules-lite/` | `ModuleListLiteAPIEndpoint.get` (303) | `list_modules_lite` | `ProjectEntityPermission` | `cursor`, `per_page`, `order_by` ∈ `MODULE_ORDER_BY_ALLOWLIST` {`created_at`, `updated_at`, `name`, `start_date`, `target_date`, `status`, `sort_order`} (Default `-created_at`) | 200 paginiert `ModuleLiteSerializer` (`__all__` Module-Felder; `members` als ID-Liste) | nicht archiviert |
| V-MOD-04 | GET | `{P}/modules/{pk}/` | `ModuleDetailAPIEndpoint.get` (518) | `retrieve_module` | `ProjectEntityPermission` | `fields`, `expand` | 200 `ModuleSerializer` | Archivierte → 404. f/e ✓ |
| V-MOD-05 | PATCH | `{P}/modules/{pk}/` | `….patch` (452) | `update_module` | `ProjectEntityPermission` (A/M) | `ModuleUpdateSerializer` partiell | 200 `ModuleSerializer` (**ohne** Zählfelder, da Instanz ohne Annotation); 400 `{"error": "Archived module cannot be edited"}`; 400 `{"error": "Module with this name already exists"}`; 409 externe ID | `members` ersetzt alle `ModuleMember` (hartes Löschen + Bulk-Insert); `model_activity("module", updated)`. Validierung prüft erneut `module_view` des Projekts. |
| V-MOD-06 | DELETE | `{P}/modules/{pk}/` | `….delete` (540) | `delete_module` | `ProjectEntityPermission` (A/M) + View: Ersteller **oder** PM Rolle 20 | – | 204; 403 `{"error": "Only admin or creator can delete the module"}` | `issue_activity("module.activity.deleted", requested_data={module_id, module_name, issues[]}, current_instance={module_name})`; Soft-Delete Modul und `ModuleIssue`s; `UserFavorite` (`entity_type="module"`) löschen |
| V-MOD-07 | GET | `{P}/modules/{module_id}/module-issues/` | `ModuleIssueListCreateAPIEndpoint.get` (644) | `list_module_work_items` | `ProjectEntityPermission` | `cursor`, `per_page`, `order_by` (Issue-Allowlist; Default `created_at`), `fields`, `expand` | 200 paginiert `IssueSerializer` | f/e ✓ |
| V-MOD-08 | POST | `{P}/modules/{module_id}/module-issues/` | `….post` (712) | `add_module_work_items` | `ProjectEntityPermission` (A/M) | `{"issues": ["<uuid>", ...]}` | 200 Liste aller `ModuleIssueSerializer` des Moduls; 400 `{"error": "Issues are required"}` | Logik 3.11 (fehlerhafter Vergleich ⇒ faktisch immer „hinzufügen“, nie „verschieben“); archivierte Module nicht geprüft; `issue_activity("module.activity.created")` |
| V-MOD-09 | DELETE | `{P}/modules/{module_id}/module-issues/{issue_id}/` | `ModuleIssueDetailAPIEndpoint.delete` (914) | `delete_module_work_item` | `ProjectEntityPermission` (A/M) | – | 204 | `issue_activity("module.activity.deleted", requested_data={module_id, issues:[issue_id]}, current_instance={module_name})` |
| V-MOD-10 | POST | `{P}/modules/{pk}/archive/` | `ModuleArchiveUnarchiveAPIEndpoint.post` (1084) | `archive_module` | `ProjectEntityPermission` (A/M) | `{}` | 204; 400 `{"error": "Only completed or cancelled modules can be archived"}` | `archived_at=now`; `UserFavorite` löschen |
| V-MOD-11 | GET | `{P}/archived-modules/` | `….get` (1056) | `list_archived_modules` | `ProjectEntityPermission` | `cursor`, `per_page`, `fields`, `expand` | 200 paginiert `ModuleSerializer` | |
| V-MOD-12 | DELETE | `{P}/archived-modules/{pk}/unarchive/` | `….delete` (1118) | `unarchive_module` | `ProjectEntityPermission` (A/M) | – | 204 | |

#### 2.2.13 Intake (`V1U/intake.py`; `V1V/intake.py`)

| ID | Methode | Pfad | View (Z.) | operationId | Berechtigung | Request | Response | Seiteneffekte / Besonderheiten |
|---|---|---|---|---|---|---|---|---|
| V-INT-01 | GET | `{P}/intake-issues/` | `IntakeIssueListCreateAPIEndpoint.get` (108) | `get_intake_work_items_list` | `ProjectLitePermission` (PM jeder Rolle) | `cursor`, `per_page`, `fields`, `expand` | 200 paginiert `IntakeIssueSerializer` (2.4.6) | Leere Liste, wenn kein Intake existiert **oder** `project.intake_view == False`. Filter: erstes `Intake` des Projekts (nicht zwingend `is_default`), `snoozed_till ≥ now` oder `null` (⇒ abgelaufene Snoozes **ausgeblendet**), Sortierung `-created_at`. Projekt-Existenz via `Project.objects.get` (404). f/e ✓ |
| V-INT-02 | POST | `{P}/intake-issues/` | `….post` (144) | `create_intake_work_item` | `ProjectLitePermission` (**auch Gäste**) | `{"issue": {"name" (Pflicht), "priority" ∈ {low, medium, high, urgent, none} (Default `none`), "description_html" (Default `<p></p>`), "description" oder "description_json"}}` | 201 `IntakeIssueSerializer`; 400 `{"error": "Name is required"}`; 400 `{"error": "Intake is not enabled for this project enable it through the project's api"}` (nur wenn **kein** Intake **und** `intake_view` false); 400 `{"error": "Invalid priority"}` | Triage-State suchen/erzeugen (`name="Triage"`, `group="triage"`, `color="#4E5355"`, `sequence=65000`, `default=False`); `description_html` per `validate_html_content` sanitisiert; `Issue` in Triage-State; `IntakeIssue(status=-2 Default, source="IN_APP")`; `issue_activity("issue.activity.created", intake=<id>)` ohne `notification`. Existiert ein Intake, aber `intake_view=false`, wird trotzdem angelegt; existiert kein Intake, aber `intake_view=true` → `intake.id` auf `None` → 500. |
| V-INT-03 | GET | `{P}/intake-issues/{issue_id}/` | `IntakeIssueDetailAPIEndpoint.get` (278) | `retrieve_intake_work_item` | `ProjectLitePermission` | `fields`, `expand` | 200 `IntakeIssueSerializer` | Pfadparameter ist die **Issue-ID** (nicht IntakeIssue-ID); Snooze-Filter wie Liste |
| V-INT-04 | PATCH | `{P}/intake-issues/{issue_id}/` | `….patch` (309) | `update_intake_work_item` | `ProjectLitePermission` + View-Regeln (3.12) | `IntakeIssueUpdateSerializer`: `status` ∈ {-2, -1, 0, 1, 2}, `snoozed_till`, `duplicate_to`, `source`, `source_email`; optional `issue` {Issue-Felder} | 200 `IntakeIssueSerializer`; 400 `{"error": "You cannot edit intake work items"}` (Gast und nicht Ersteller); 400 `{"status": "Cannot accept intake issue: No default state found for the project"}`; 400 Serializer-Fehler | Gäste: nur `name`, `description_html`, `description_json` des Issues; **Statusänderungen nur Rolle > 15 (= Admin)**; Annahme verschiebt Triage-Issue in Default-State; `issue_activity("issue.activity.updated", intake=…)`, `issue_activity("intake.activity.created", notification=False)` |
| V-INT-05 | DELETE | `{P}/intake-issues/{issue_id}/` | `….delete` (460) | `delete_intake_work_item` | `ProjectLitePermission` + bei Status ∈ {-2, -1, 0, 2}: Issue-Ersteller oder PM Rolle 20 | – | 204; 403 `{"error": "Only admin or creator can delete the work item"}` | Bei nicht angenommenen Status wird auch das Issue (Soft-)gelöscht; angenommene (1) behalten ihr Issue; `IntakeIssue` wird gelöscht. Keine Activity. |

#### 2.2.14 Mitglieder (`V1U/member.py`; `V1V/member.py`)

| ID | Methode | Pfad | View (Z.) | operationId | Berechtigung | Request | Response | Besonderheiten |
|---|---|---|---|---|---|---|---|---|
| V-MEM-01 | GET | `{W}/members/` | `WorkspaceMemberAPIEndpoint.get` (77) | `get_workspace_members` | `WorkSpaceAdminPermission` (WM A/M; **Gäste 403**) | – | 200 **unpaginierte** Liste `UserLiteSerializer` + `role` je Eintrag; 400 `{"error": "Provided workspace does not exist"}` | **Inklusive inaktiver** Mitglieder (kein `is_active`-Filter); keine Sortierung |
| V-MEM-02 | GET | `{W}/members-lite/` | `WorkspaceMemberLiteAPIEndpoint.get` (262) | `get_workspace_members_lite` | `WorkSpaceAdminPermission` | `cursor`, `per_page` | 200 paginiert `WorkspaceMemberLiteAPISerializer`: `id` (= **User-ID**), `first_name, last_name, email, avatar, avatar_url, display_name, role, is_active, is_bot`; 404 `{"error": "Provided workspace does not exist"}` | inkl. inaktiver; Sortierung `-created_at` |
| V-MEM-03 | GET | `{P}/members/` und `{P}/project-members/` | `ProjectMemberListCreateAPIEndpoint.get` (129) | `get_project_members` | GET: `ProjectMemberPermission` (PM) | – | 200 unpaginierte Liste `UserLiteSerializer` (**ohne Rolle**); 400 `{"error": "Provided workspace does not exist"}` | **Inklusive inaktiver** Projektmitglieder |
| V-MEM-04 | POST | `{P}/members/` und `{P}/project-members/` | `….post` (160) | `create_project_member` | `ProjectAdminPermission` | `ProjectMemberSerializer`: `member` (User-UUID, Pflicht, aktives WS-Mitglied), `role` ∈ {20, 15, 5} | 201 `{"id", "member", "role"}`; 400 `{"member": ["Member not found in workspace"]}` / `{"role": ["Invalid role"]}`; 400 `{"error": "The payload is not valid"}` (bereits Mitglied – auch inaktiv – wegen Unique-Constraint) | Rolle des Projektmitglieds wird **nicht** gegen die WS-Rolle begrenzt (Gast im WS kann Projekt-Admin werden) |
| V-MEM-05 | GET | `{P}/members/{pk}/` und `{P}/project-members/{pk}/` | `ProjectMemberDetailAPIEndpoint.get` (183) | `get_project_member` | `ProjectMemberPermission` | – (`pk` = **ProjectMember-ID**) | 200 `UserLiteSerializer` des Users (ohne Rolle) | |
| V-MEM-06 | PATCH | dito | `….patch` (211) | `update_project_member` | `ProjectAdminPermission` | `ProjectMemberSerializer` partiell (`role`, auch `member` änderbar) | 200 `{"id", "member", "role"}`; 400 `{"member": ["Member not found in workspace"]}` (Zielperson nicht mehr aktives WS-Mitglied) | Keine Schutzregel für letzten Admin/eigene Rolle |
| V-MEM-07 | DELETE | dito | `….delete` (231) | `delete_project_member` | `ProjectAdminPermission` | – | 204 | `is_active=False` (keine Löschung, keine Bereinigung von Zuweisungen) |
| V-MEM-08 | GET | `{P}/project-members-lite/` | `ProjectMemberLiteAPIEndpoint.get` (309) | `get_project_members_lite` | `ProjectMemberPermission` | `cursor`, `per_page` | 200 paginiert `ProjectMemberLiteAPISerializer` (Felder wie V-MEM-02); 404 Workspace/`{"error": "Provided project does not exist"}` | inkl. inaktiver; `-created_at` |

#### 2.2.15 Einladungen (`V1U/invite.py`, DRF `DefaultRouter`; `V1V/invite.py`)

| ID | Methode | Pfad | View (Z.) | Berechtigung | Request | Response | Besonderheiten |
|---|---|---|---|---|---|---|---|
| V-INV-01 | GET | `{W}/invitations/` | `WorkspaceInvitationsViewset.list` (55) | `WorkspaceOwnerPermission` (WM Rolle A); **kein RL** | Query-Filter über DjangoFilterBackend: keine `filterset_fields` (wirkungslos) | 200 unpaginierte Liste `WorkspaceInviteSerializer`: `id, email, role, created_at, updated_at, responded_at, accepted` | Sortierung Model-Default `-created_at` |
| V-INV-02 | POST | `{W}/invitations/` | `….create` (89) | dito | `{"email" (Pflicht, `validate_email`), "role" ∈ {20, 15, 5} (Default 5)}` | 201 `WorkspaceInviteSerializer`; 400 `{"email": ["Invalid email address"]}` (Code `INVALID_EMAIL_ADDRESS`), `{"role": ["Invalid role"]}` (`INVALID_WORKSPACE_MEMBER_ROLE`), `{"non_field_errors": ["Email already invited"]}` (`EMAIL_ALREADY_INVITED`) | **Kein Token** (`token=""`), **keine E-Mail**, keine Prüfung, ob die Person bereits Mitglied ist. Die Annahme ist über die App-API (A03) mit leerem Token nicht sinnvoll möglich ⇒ Einladung über v1 faktisch nur als Datensatz. |
| V-INV-03 | GET | `{W}/invitations/{pk}/` | `….retrieve` (75) | dito | – | 200 | |
| V-INV-04 | PATCH | `{W}/invitations/{pk}/` | `….partial_update` (112) | dito | `{"role"}` | 200; 400 `{"error": "Email cannot be updated after invite is created.", "code": "EMAIL_CANNOT_BE_UPDATED"}` (wenn `email` gesendet) | |
| V-INV-05 | PUT | `{W}/invitations/{pk}/` | DRF `ModelViewSet.update` (geerbt, undokumentiert) | dito | vollständiger Body (`email` Pflicht) | 200 | **Umgeht** die E-Mail-Sperre von PATCH; Duplikatprüfung „Email already invited“ greift auch für die eigene E-Mail ⇒ PUT mit gleicher E-Mail → 400 |
| V-INV-06 | DELETE | `{W}/invitations/{pk}/` | `….destroy` (141) | dito | – | 204; 400 `{"error": "Invite already accepted", "code": "INVITE_ALREADY_ACCEPTED"}`; 400 `{"error": "Invite already responded", "code": "INVITE_ALREADY_RESPONDED"}` | Soft-Delete |

#### 2.2.16 Stickies (`V1U/sticky.py`, `DefaultRouter`; `V1V/sticky.py`)

| ID | Methode | Pfad | View (Z.) | operationId | Berechtigung | Request | Response | Besonderheiten |
|---|---|---|---|---|---|---|---|---|
| V-STK-01 | GET | `{W}/stickies/` | `StickyViewSet.list` (66) | `list_stickies` | `WorkspaceUserPermission` (WM jeder Rolle); **kein RL** | `query` (ICONTAINS auf `description_stripped`), `cursor`, `per_page` (Default **20**, Max 1000) | 200 paginiert `StickySerializer` (`__all__`: `id, created_at, updated_at, deleted_at, created_by, updated_by, name, description, description_html, description_stripped, description_binary, logo_props, color, background_color, workspace, owner, sort_order`) | nur eigene Stickies (`owner_id = user`); `-created_at` |
| V-STK-02 | POST | `{W}/stickies/` | `….create` (48) | `create_sticky` | dito | `StickySerializer` (`name` optional, `description_html` sanitisiert, `description_binary` validiert) | 201; 400 `{"error": "html content is not valid"}` / `{"description_binary": "Invalid binary data"}` | `workspace`, `owner` aus Kontext |
| V-STK-03 | GET | `{W}/stickies/{pk}/` | `….retrieve` (85) | `retrieve_sticky` | dito | – | 200; 404 `{"detail": "No Sticky matches the given query."}` (DRF `get_object` → `Http404`; gilt auch für PATCH/PUT/DELETE) | fremde Stickies → 404 |
| V-STK-04 | PATCH | `{W}/stickies/{pk}/` | `….partial_update` (96) | `update_sticky` | dito | partiell | 200 | |
| V-STK-05 | PUT | `{W}/stickies/{pk}/` | geerbtes `ModelViewSet.update` | – | dito | vollständig | 200 | undokumentiert |
| V-STK-06 | DELETE | `{W}/stickies/{pk}/` | `….destroy` (110) | `delete_sticky` | dito | – | 204 | Soft-Delete |

#### 2.2.17 Assets (`V1U/asset.py`; `V1V/asset.py`)

| ID | Methode | Pfad | View (Z.) | operationId | Berechtigung | Request | Response | Besonderheiten |
|---|---|---|---|---|---|---|---|---|
| V-AST-01 | POST | `/api/v1/assets/user-assets/` | `UserAssetEndpoint.post` (112) | `create_user_asset_upload` | `IsAuthenticated` | `{name, type (Default image/jpeg; ∈ image/jpeg, image/png, image/webp, image/jpg, image/gif), size (Default FILE_SIZE_LIMIT; `int()` – Nicht-Zahl → 500), entity_type ∈ {USER_AVATAR, USER_COVER}}` | 200 `{"upload_data", "asset_id", "asset_url"}` (`asset_url` = `/api/assets/v2/static/{id}/`); 400 `{"error": "Invalid entity type.", "status": false}`; 400 `{"error": "Invalid file type. Only JPEG and PNG files are allowed.", "status": false}` | `FileAsset(user=request.user, entity_type, size=min(size, FILE_SIZE_LIMIT))`, Key `"{uuid4hex}-{name}"` (ohne Workspace-Präfix); Presigned POST über Browser-Endpoint (`S3Storage(request)`) |
| V-AST-02 | PATCH | `/api/v1/assets/user-assets/{asset_id}/` | `….patch` (205) | `update_user_asset` | dito (nur eigene Assets: `user_id = request.user`) | `{"attributes": {...}}` optional | 204 | `is_uploaded=True`, `attributes` überschreiben; Metadaten-Task. **Setzt nicht** `User.avatar_asset`/`cover_image_asset` (v1 hat keinen Profil-Update-Endpunkt) |
| V-AST-03 | DELETE | `/api/v1/assets/user-assets/{asset_id}/` | `….delete` (233) | `delete_user_asset` | dito | – | 204 | Soft-Delete; bei `USER_AVATAR` → `user.avatar_asset_id=None`, bei `USER_COVER` → `user.cover_image_asset_id=None` |
| V-AST-04 | POST | `/api/v1/assets/user-assets/server/` | `UserServerAssetEndpoint.post` (284) | `create_user_server_asset_upload` (im Schema ausgefiltert) | dito | wie V-AST-01 | **faktisch 500** `{"error": "Something went wrong please try again later"}` | **Defekt in v1.4.2:** `S3Storage.__init__(self, request=None)` kennt keinen Parameter `is_server` (`SET/storage.py` Z. 28) ⇒ `TypeError` **nach** dem Anlegen des `FileAsset` (verwaister Datensatz). Absicht laut Namen/Kommentar: Presigned-URL gegen den internen Endpoint (`AWS_S3_ENDPOINT_URL`) statt gegen den Request-Host (bei `USE_MINIO=1` wird sonst `{scheme}://{request.get_host()}` verwendet, `SET/storage.py` Z. 42–58). Tests mocken den Konstruktor (`apps/api/plane/tests/contract/api/test_generic_asset.py` Z. 172–176) und decken den Fehler nicht auf. |
| V-AST-05 | PATCH | `/api/v1/assets/user-assets/{asset_id}/server/` | `….patch` (361) | `update_user_server_asset` (ausgefiltert) | dito | wie V-AST-02 | 204 | |
| V-AST-06 | DELETE | `/api/v1/assets/user-assets/{asset_id}/server/` | `….delete` (389) | `delete_user_server_asset` (ausgefiltert) | dito | – | 204 | wie V-AST-03 |
| V-AST-07 | POST | `{W}/assets/` | `GenericAssetEndpoint.post` (507) | `create_generic_asset_upload` | `WorkspaceUserPermission` (WM jeder Rolle) | `GenericAssetUploadSerializer`-Felder: `name` (Pflicht), `type` (Pflicht, ∈ ATTACHMENT_MIME_TYPES), `size` (Default FILE_SIZE_LIMIT; `int()`), `project_id` (optional, **nicht** auf Workspace/Mitgliedschaft geprüft), `external_id`, `external_source` | Soll: 200 `{"upload_data", "asset_id", "asset_url"}`; **Ist: 500** `{"error": "Something went wrong please try again later"}` nach dem Anlegen des `FileAsset` (gleicher `is_server`-Defekt wie V-AST-04); 400 `{"error": "Name and size are required fields.", "status": false}`; 400 `{"error": "Invalid file type.", "status": false}`; 409 `{"message": "Asset with same external id and source already exists", "asset_id", "asset_url"}` | `entity_type=ISSUE_ATTACHMENT` **ohne** `issue_id` ⇒ `asset_url` enthält `.../issues/None/attachments/{id}/`; **kein** v1-Endpunkt bindet das Asset nachträglich an ein Work Item. |
| V-AST-08 | GET | `{W}/assets/{asset_id}/` | `….get` (427) | `get_generic_asset` | `WorkspaceUserPermission` | – | Soll: 200 `{"asset_id", "asset_url" (Presigned GET, `inline` nur für INLINE_SAFE_MIME_TYPES, sonst Download), "asset_name", "asset_type"}`; **Ist für hochgeladene Assets: 500 `{"error": "Internal server error"}`** (`is_server`-Defekt, im `try` abgefangen); 400 `{"error": "Asset not yet uploaded"}`; 404 `{"error": "Workspace not found"}` / `{"error": "Asset not found"}` | jedes Asset des Workspace (alle Entity-Typen, nicht gelöscht) |
| V-AST-09 | PATCH | `{W}/assets/{asset_id}/` | `….patch` (608) | `update_generic_asset` | `WorkspaceUserPermission` | `{"is_uploaded": bool}` (fehlt → unverändert) | 204; 404 `{"error": "Asset not found"}` | jedes Asset des Workspace; Metadaten-Task |

`ATTACHMENT_MIME_TYPES` (`SET/common.py` Z. 505–592, vollständig): `image/jpeg, image/png, image/gif, image/svg+xml, image/webp, image/tiff, image/bmp, application/pdf, application/msword, application/vnd.openxmlformats-officedocument.wordprocessingml.document, application/vnd.ms-excel, application/vnd.openxmlformats-officedocument.spreadsheetml.sheet, application/vnd.ms-powerpoint, application/vnd.openxmlformats-officedocument.presentationml.presentation, text/plain, text/markdown, application/rtf, application/vnd.oasis.opendocument.spreadsheet, application/vnd.oasis.opendocument.text, application/vnd.oasis.opendocument.presentation, application/vnd.oasis.opendocument.graphics, application/vnd.visio, image/x-portable-graymap, image/x-portable-bitmap, image/x-portable-pixmap, application/vnd.oasis.opendocument.database, audio/mpeg, audio/wav, audio/ogg, audio/midi, audio/x-midi, audio/aac, audio/flac, audio/x-m4a, video/mp4, video/mpeg, video/ogg, video/webm, video/quicktime, video/x-msvideo, video/x-ms-wmv, application/zip, application/x-rar, application/x-rar-compressed, application/x-tar, application/gzip, application/x-zip, application/x-zip-compressed, application/x-7z-compressed, application/x-compressed, application/x-compressed-tar, application/x-compressed-tar-gz, application/x-compressed-tar-bz2, application/x-compressed-tar-zip, application/x-compressed-tar-7z, application/x-compressed-tar-rar, model/gltf-binary, model/gltf+json, application/octet-stream, font/ttf, font/otf, font/woff, font/woff2, text/css, text/javascript, application/json, text/xml, text/csv, application/xml, application/x-sql, application/x-gzip` (Duplikate `application/x-compressed-tar-zip`, `text/markdown` im Original). `INLINE_SAFE_MIME_TYPES` = `image/jpeg, image/jpg, image/png, image/gif, image/webp` (Z. 596).

#### 2.2.18 Router-Nebenprodukte (`DefaultRouter` in `V1U/invite.py`, `V1U/sticky.py`)

| ID | Methode | Pfad | Verhalten |
|---|---|---|---|
| V-RTR-01 | GET | `{W}/` | DRF-`APIRootView` (zweimal registriert, erster Treffer gewinnt): DRF-Default-Authentifizierung `SessionAuthentication` + `IsAuthenticated` ⇒ mit API-Key **401/403**; mit gültiger App-Session Link-Liste `{"invitations": "<url>"}`. Ohne fachliche Funktion. |
| V-RTR-02 | alle Methoden der Basisrouten | `{W}/invitations.{format}/`, `{W}/invitations/{pk}.{format}/`, `{W}/stickies.{format}/`, `{W}/stickies/{pk}.{format}/`, `{W}/.{format}` | Format-Suffix-Routen (`include_format_suffixes=True`); mit `json` funktional identisch zu den Basisrouten, andere Formate → 404 (nur `JSONRenderer`) |

#### 2.2.19 Implementiert, aber nicht erreichbar

| ID | Handler | Grund | Quelle |
|---|---|---|---|
| V-DEAD-01…04 | `ProjectEstimateAPIEndpoint.get/post/patch/delete` (`{P}/estimates/`) | `V1U/estimate.py` wird in `V1U/__init__.py` **nicht** importiert | `V1V/estimate.py` Z. 47–135; `V1U/__init__.py` |
| V-DEAD-05…06 | `EstimatePointListCreateAPIEndpoint.get/post` (`{P}/estimates/{estimate_id}/estimate-points/`) | dito | `V1V/estimate.py` Z. 168–237 |
| V-DEAD-07…08 | `EstimatePointDetailAPIEndpoint.patch/delete` (`…/estimate-points/{estimate_point_id}/`) | dito | `V1V/estimate.py` Z. 264–291 |
| V-DEAD-09 | `IssueDetailAPIEndpoint.put` (Upsert per `external_id`+`external_source`) | URL erlaubt nur `get, patch, delete`; Signatur ohne `pk`; im Schema per Hook ausgefiltert | `V1V/issue.py` Z. 623–776 |
| V-DEAD-10 | `ModuleIssueDetailAPIEndpoint.get` (paginierte Liste mit einem Work Item) | URL erlaubt nur `delete` | `V1V/module.py` Z. 850–912; `V1U/module.py` |
| – | `IssueRelationRemoveSerializer` (Entfernen einer Relation) | Kein View/keine Route | `V1S/issue.py` Z. 601–611 |
| – | `V1U/schema.py` | nicht eingebunden (2.1.9) | |

Verhalten der toten Estimate-Endpunkte (für die Zielarchitektur relevant, da Doc 21 §2.5 sie als Commercial-Endpunkte führt): POST legt genau **ein** Estimate je Projekt an (409 `{"error": "An estimate already exists for this project", "id"}`), PATCH erlaubt nur `name`, `description`; Punkte: POST akzeptiert Liste oder `{"estimate_points": [...]}` (400 `{"error": "Estimate points are required"}`), `value` max. 20 Zeichen (`"Value can't be more than 20 characters"`), PATCH nur `key`, `value`, `description`; 404-Texte `"Project not found"`, `"Workspace not found"`, `"Estimate not found"`, `"Estimate point not found"`; Berechtigung `ProjectEntityPermission` (`V1V/estimate.py`, `V1S/estimate.py`).

### 2.3 v1-Serializer-Inventar (`V1S/*.py`)

Basisfelder aller `BaseModel`-Modelle (A02a): `id, created_at, updated_at, deleted_at, created_by, updated_by`; `ProjectBaseModel` zusätzlich `project, workspace`. `__all__` liefert FKs als UUID unter dem Feldnamen ohne `_id` (z. B. `project`, `state`).

| Klasse | Datei Z. | Modell | Ausgabe-/Eingabefelder | Read-only / Write-only | Validierung / Logik | Verwendet in |
|---|---|---|---|---|---|---|
| `BaseSerializer` | `base.py` 16 | – | `id` (PK, RO) | – | `fields`/`expand` (2.1.6) | alle |
| `UserLiteSerializer` | `user.py` 13 | `User` | `id, first_name, last_name, email, avatar, avatar_url, display_name` | alle RO | – | V-USR-01, V-MEM-01/03/05, Expansion |
| `WorkspaceLiteSerializer` | `workspace.py` 10 | `Workspace` | `name, slug, id` | RO | – | Expansion `workspace` |
| `ProjectCreateSerializer` | `project.py` 22 | `Project` | `name, description, project_lead, default_assignee, identifier, icon_prop, emoji, cover_image, module_view, cycle_view, issue_views_view, page_view, intake_view, guest_view_all_features, archive_in, close_in, timezone, external_source, external_id, is_issue_type_enabled, is_time_tracking_enabled` | RO: `id, workspace, created_at, updated_at, created_by, updated_by, logo_props` | `validate`: Name und Identifier dürfen nicht auf `Project.FORBIDDEN_IDENTIFIER_CHARS_PATTERN` = `^.*[&+,:;$^}{*=?@#\|'<>.()%!-].*$` passen (`M/project.py` Z. 145); `project_lead` muss **aktives** WS-Mitglied sein; `default_assignee` WS-Mitglied (beliebiger Status). `create`: Identifier `strip().upper()`, leer → „Project Identifier is required“, existierender `ProjectIdentifier` → „Project Identifier is taken“; `logo_props` = `{"in_use": "icon", "icon": {"name": <zufällig aus 28>, "color": <zufällig aus 8>}}` (Icons: `home, apps, settings, star, favorite, done, check_circle, add_task, create_new_folder, dataset, terminal, key, rocket, public, quiz, mood, gavel, eco, diamond, forest, bolt, sync, cached, library_add, view_timeline, view_kanban, empty_dashboard, cycle`; Farben: `#95999f, #6d7b8a, #5e6ad2, #02b5ed, #02b55c, #f2be02, #e57a00, #f38e82`); legt **keinen** `ProjectIdentifier` an | V-PRJ-02 |
| `ProjectUpdateSerializer` | `project.py` 165 | `Project` | wie Create + `default_state`, `estimate` | wie Create | `update`: Sonderzeichenprüfung erneut; `default_state` muss State des Projekts sein; `estimate` muss Estimate des Projekts sein | V-PRJ-05 |
| `ProjectSerializer` | `project.py` 209 | `Project` | `__all__` + `total_members, total_cycles, total_modules, is_member, sort_order, member_role, is_deployed, cover_image_url` | RO: `id, emoji, workspace, created_at, updated_at, created_by, updated_by, deleted_at, cover_image_url` + deklarierte Annotationen | `validate` (in v1 nie ausgeführt, nur Ausgabe): Sonderzeichen, Lead/Assignee WS-Mitglied, `description_html`-Sanitizing nur für `dict` (Variable `is_valid` sonst undefiniert ⇒ `NameError`); `create` legt `ProjectIdentifier` an (in v1 ungenutzt) | V-PRJ-01/02/04/05, Webhook `project` |
| `ProjectLiteSerializer` | `project.py` 300 | `Project` | `id, identifier, name, cover_image, icon_prop, emoji, description, cover_image_url, archived_at` | RO | – | V-PRJ-03, Expansion `project` |
| `IssueSerializer` | `issue.py` 46 | `Issue` | alle Issue-Felder außer `description_json`, `description_stripped` + `assignees` (WO `ListField` von User-IDs), `labels` (WO `ListField` von Label-IDs), `type_id` (PK `IssueType`, `source="type"`, nullable) | RO: `id, workspace, project, updated_by, updated_at, completed_at, deleted_at, archived_at, sequence_id`; `is_draft` RO bei Update (`get_fields`) | `validate` (Reihenfolge 3.5): Start ≤ Ziel; `description_html` via `lxml.html.fromstring` normalisiert (Fehler → „Invalid HTML passed“) und `validate_html_content` (`{"error": "html content is not valid"}`); `description_binary` via `validate_binary_data` (`{"description_binary": "Invalid binary data"}`); Assignees = aktive PM mit Rolle ≥ 15 (`"Assignees [...] are not active members of this project"`); Labels des Projekts (`"Labels [...] do not belong to this project"`); State des Projekts (`"State is not valid please pass a valid state_id"`); Parent im selben Projekt (`"Parent is not valid issue_id please pass a valid issue_id"`); Estimate-Point des Projekts (`"Estimate point is not valid please pass a valid estimate_point_id"`). `create`: Default-`IssueType` des Projekts (`is_default=True`), Assignees (oder `default_assignee` des Projekts, falls PM Rolle ≥ 15), Labels. `update`: Assignees/Labels werden **komplett ersetzt** (hartes Löschen der Zuordnungen), `updated_at=now`. `to_representation`: `assignees`/`labels` als ID-Strings oder expandiert | V-WI-*, V-CYC-07, V-MOD-07, V-INT-04 (Issue-Teil), Expansion `issue` |
| `IssueLiteSerializer` | `issue.py` 354 | `Issue` | `id, sequence_id, project_id` | RO | – | Expansion `parent` |
| `LabelCreateUpdateSerializer` | `issue.py` 368 | `Label` | `name, color, description, external_source, external_id, parent, sort_order` | – | – | V-LBL-02/04 |
| `LabelSerializer` | `issue.py` 399 | `Label` | `__all__` (`id, created_at, updated_at, deleted_at, created_by, updated_by, workspace, project, parent, name, description, color, sort_order, external_source, external_id`) | RO Audit-Felder, `workspace`, `project` | – | V-LBL-*, `IssueSerializer` (`expand=labels`) |
| `LabelLiteSerializer` | `issue.py` 829 | `Label` | `id, name, color` | – | – | `IssueExpandSerializer` |
| `IssueLinkCreateSerializer` | `issue.py` 422 | `IssueLink` | `title, url, issue_id` | – | `validate_url` (`URLValidator`, Schema http/https); `create`: gleiche URL am selben Issue → `{"error": "URL already exists for this Issue"}` | V-LNK-02 |
| `IssueLinkUpdateSerializer` | `issue.py` 465 | `IssueLink` | wie Create | – | `update`: Duplikat-URL-Prüfung | nur OpenAPI-Doku (View nutzt `IssueLinkSerializer`) |
| `IssueLinkSerializer` | `issue.py` 491 | `IssueLink` | `__all__` | RO Audit, `workspace, project, issue` | – | V-LNK-* |
| `IssueRelationRefSerializer` | `issue.py` 514 | – | `project_id, issue_id` | – | – | Doku |
| `IssueRelationResponseSerializer` | `issue.py` 521 | – | 8 Listen (`blocking … finish_before`) | – | – | Doku V-REL-01 |
| `IssueRelationCreateSerializer` | `issue.py` 563 | – | `relation_type` (Choice, 8 Werte), `issues` (UUID-Liste, `min_length=1`) | – | `"At least one issue ID is required."` | V-REL-02 |
| `IssueRelationRemoveSerializer` | `issue.py` 601 | – | `related_issue` (UUID) | – | – | **ungenutzt** |
| `IssueRelationSerializer` | `issue.py` 614 | `IssueRelation` | `id` (= `related_issue.id`), `project_id`, `sequence_id`, `relation_type`, `name`, `state_id`, `priority` (jeweils vom `related_issue`), `created_by, created_at, updated_at, updated_by` | RO | – | V-REL-02 (Vorwärts) |
| `RelatedIssueSerializer` | `issue.py` 655 | `IssueRelation` | `id, project_id, sequence_id, relation_type, name, type_id, is_epic, state_id, priority` (jeweils vom `issue`), Audit | RO | `type_id`/`is_epic` fehlen bei Issues ohne Typ (SkipField) | V-REL-02 (Rückwärts) |
| `IssueAttachmentSerializer` | `issue.py` 700 | `FileAsset` | `__all__` (`id, created_at, updated_at, deleted_at, created_by, updated_by, attributes, asset, user, workspace, draft_issue, project, issue, comment, page, entity_type, entity_identifier, is_deleted, is_archived, external_id, external_source, size, is_uploaded, storage_metadata`) | RO `id, workspace, project, issue, updated_by, updated_at` | – | V-ATT-* |
| `IssueCommentCreateSerializer` | `issue.py` 721 | `IssueComment` | `comment_json, comment_html, access, external_source, external_id` | – | **keine** HTML-Sanitization | V-CMT-02/04 |
| `IssueCommentSerializer` | `issue.py` 754 | `IssueComment` | alle Felder außer `comment_stripped`, `comment_json` (`id, created_at, updated_at, deleted_at, created_by, updated_by, project, workspace, comment_html, description, issue, actor, access, external_source, external_id, edited_at, parent`) + `is_member` | RO Audit, `workspace, project, issue` | `validate`: `comment_html` sanitisiert | V-CMT-*, Webhook `issue_comment` |
| `IssueActivitySerializer` | `issue.py` 788 | `IssueActivity` | alle außer `created_by, updated_by` | – | – | V-ACT-* |
| `CycleIssueSerializer` / `ModuleIssueSerializer` (in `issue.py` Z. 801/815) | `issue.py` | – (Meta ohne `model`) | `cycle`/`module` | – | – | **toter Code** (verdeckt durch gleichnamige Klassen aus `cycle.py`/`module.py`, `V1S/__init__.py`) |
| `IssueExpandSerializer` | `issue.py` 842 | `Issue` | `__all__` + `cycle` (CycleLite, `source="issue_cycle.cycle"` – auf Reverse-Manager ⇒ **immer weggelassen**), `module` (dito), `labels` (Methode: IDs), `assignees` (Methode: IDs), `state` (StateLite), `description` (= `description_json`) | RO Audit, `completed_at` | – | `IntakeIssueSerializer.issue_detail`, Webhook `issue` |
| `IssueAttachmentUploadSerializer` | `issue.py` 886 | – | `name, type, size, external_id, external_source` | – | – | nur Doku |
| `IssueSearchSerializer` | `issue.py` 906 | – | `id, name, sequence_id, project__identifier, project_id, workspace__slug` | – | – | nur Doku |
| `StateSerializer` | `state.py` 14 | `State` | `__all__` (`id, created_at, updated_at, deleted_at, created_by, updated_by, project, workspace, name, description, color, slug, sequence, group, is_triage, default, external_source, external_id`) | RO `id, created_by, updated_by, created_at, updated_at, workspace, project, deleted_at, slug` | `group == "triage"` → „Cannot create triage state“; `save`: bei `default=true` alle anderen auf `false` (atomar) | V-STA-* |
| `StateLiteSerializer` | `state.py` 51 | `State` | `id, name, color, group` | RO | – | Expansion `state`, `IssueExpandSerializer` |
| `CycleCreateSerializer` | `cycle.py` 15 | `Cycle` | `name, description, start_date, end_date, owned_by, external_source, external_id, timezone` | RO Audit, `workspace, project, deleted_at` | `validate`: `project_id` aus Kontext; Projekt existiert; `cycle_view` aktiv; Start ≤ Ende; beide gesetzt ⇒ `convert_to_utc(date, project_id, is_start_date)` (Projektzeitzone, Start 00:00, Ende 23:59:59 – A04); `owned_by` Default Requester (Create oder explizit `null`) | V-CYC-02 |
| `CycleUpdateSerializer` | `cycle.py` 101 | `Cycle` | wie Create | | wie Create | V-CYC-05 |
| `CycleSerializer` | `cycle.py` 116 | `Cycle` | `__all__` (`id, created_at, updated_at, deleted_at, created_by, updated_by, project, workspace, name, description, start_date, end_date, owned_by, view_props, sort_order, external_source, external_id, progress_snapshot, archived_at, logo_props, timezone, version`) + `total_issues, cancelled_issues, completed_issues, started_issues, unstarted_issues, backlog_issues` (Int), `total_estimates, completed_estimates, started_estimates` (Float) | RO `id, created_at, updated_at, created_by, updated_by, workspace, project, owned_by, deleted_at` + deklarierte Zählfelder | – | V-CYC-01/02/04/05/13, Webhook `cycle` |
| `CycleIssueSerializer` | `cycle.py` 150 | `CycleIssue` | `__all__` + `sub_issues_count` | RO `workspace, project, cycle` | – | V-CYC-08/09, Webhook `cycle_issue` |
| `CycleLiteSerializer` | `cycle.py` 166 | `Cycle` | `__all__` | – | – | V-CYC-03 |
| `CycleIssueRequestSerializer` | `cycle.py` 179 | – | `issues` | – | – | nur Doku |
| `TransferCycleIssueRequestSerializer` | `cycle.py` 190 | – | `new_cycle_id` | – | – | nur Doku |
| `ModuleCreateSerializer` | `module.py` 21 | `Module` | `name, description, start_date, target_date, status, lead, members` (WO) , `external_source, external_id` | RO Audit, `workspace, project, deleted_at` | `validate`: Projekt existiert, `module_view` aktiv, Start ≤ Ziel, `members` ∩ Projektmitglieder; `create`: Name pro Projekt eindeutig (Code `MODULE_NAME_ALREADY_EXISTS`), `ModuleMember`-Bulk (`ignore_conflicts`) | V-MOD-02 |
| `ModuleUpdateSerializer` | `module.py` 124 | `Module` | wie Create | | `update`: Namenskonflikt `{"error": "Module with this name already exists"}`; `members` ersetzt | V-MOD-05 |
| `ModuleSerializer` | `module.py` 169 | `Module` | `__all__` (`id, created_at, updated_at, deleted_at, created_by, updated_by, project, workspace, name, description, description_text, description_html, start_date, target_date, status, lead, view_props, sort_order, external_source, external_id, archived_at, logo_props`) + `members` (immer Liste der Member-IDs als Strings) + 6 Zählfelder | RO Audit | – | V-MOD-*, Webhook `module` |
| `ModuleIssueSerializer` | `module.py` 209 | `ModuleIssue` | `__all__` + `sub_issues_count` | RO Audit, `workspace, project, module` | – | V-MOD-08, Webhook `module_issue` |
| `ModuleLinkSerializer` | `module.py` 233 | `ModuleLink` | `__all__` | | Duplikat-URL | **ungenutzt** in v1 |
| `ModuleLiteSerializer` | `module.py` 261 | `Module` | `__all__` | | | V-MOD-03 |
| `ModuleIssueRequestSerializer` | `module.py` 274 | – | `issues` | | | nur Doku |
| `IssueForIntakeSerializer` | `intake.py` 13 | `Issue` | `name, description (= description_json, deprecated), description_json, description_html, priority` | | | nur Doku |
| `IntakeIssueCreateSerializer` | `intake.py` 43 | `IntakeIssue` | `issue` | | | nur Doku |
| `IntakeIssueSerializer` | `intake.py` 58 | `IntakeIssue` | `__all__` (`id, created_at, updated_at, deleted_at, created_by, updated_by, project, workspace, intake, issue, status, snoozed_till, duplicate_to, source, source_email, external_source, external_id, extra`) + `issue_detail` (`IssueExpandSerializer`), `inbox` (= `intake.id`) | RO `id, workspace, project, issue`, Audit | – | V-INT-*, Webhook `intake_issue` |
| `IntakeIssueUpdateSerializer` | `intake.py` 84 | `IntakeIssue` | `status, snoozed_till, duplicate_to, source, source_email, issue` | RO Audit | `validate`: `snoozed_till` → Tagesbeginn in Projektzeitzone (`snooze_day_start`); Annahme (`status=1`) eines Triage-Issues verlangt Default-State; `update`: bei `status=1` und Triage-State → Issue in Default-State | V-INT-04 |
| `IssueDataSerializer` | `intake.py` 167 | – | `name, description_html, priority` | | | **ungenutzt** |
| `EstimateSerializer` | `estimate.py` 13 | `Estimate` | `__all__` (`id, …, project, workspace, name, description, type, last_used`) | RO `workspace, project, deleted_at` | `create` setzt Workspace/Projekt aus Kontext | tote Endpunkte |
| `EstimatePointSerializer` | `estimate.py` 25 | `EstimatePoint` | `__all__` (`id, …, project, workspace, estimate, key, description, value`) | RO `estimate, workspace, project` | `value` ≤ 20 Zeichen | Expansion `estimate_point`, tote Endpunkte |
| `UserAssetUploadSerializer`, `AssetUpdateSerializer`, `GenericAssetUploadSerializer`, `GenericAssetUpdateSerializer` | `asset.py` 13/45/56/82 | – | siehe 2.2.17 | | | nur Doku (Views lesen `request.data` direkt) |
| `FileAssetSerializer` | `asset.py` 93 | `FileAsset` | `__all__` + `asset_url` | | | **ungenutzt** in v1 |
| `WorkspaceInviteSerializer` | `invite.py` 16 | `WorkspaceMemberInvite` | `id, email, role, created_at, updated_at, responded_at, accepted` | RO `id, workspace, created_at, updated_at, responded_at, accepted` | `validate_email`, `validate_role` ∈ {20,15,5}, `validate`: E-Mail im Workspace bereits eingeladen | V-INV-* |
| `ProjectMemberSerializer` | `member.py` 15 | `ProjectMember` | `id, member, role` | RO `id` | `member` = aktives WS-Mitglied (Code `INVALID_MEMBER`), `role` ∈ {20,15,5} (`INVALID_ROLE`), Kontext `slug` Pflicht (`INVALID_SLUG`) | V-MEM-04/06 |
| `BaseMemberLiteAPISerializer` / `WorkspaceMemberLiteAPISerializer` / `ProjectMemberLiteAPISerializer` | `member.py` 46/74/81 | –/`WorkspaceMember`/`ProjectMember` | `id` (= `member.id`), `first_name, last_name, email, avatar, avatar_url, display_name` (vom User), `role, is_active` (Mitgliedschaft), `is_bot` | RO | – | V-MEM-02/08 |
| `StickySerializer` | `sticky.py` 12 | `Sticky` | `__all__` | RO `workspace, owner`; `name` optional | HTML-Sanitizing (`{"error": "html content is not valid"}`), `validate_binary_data` | V-STK-* |

### 2.4 v1-Response-Shapes (Feldlisten, verbindlich für Contract-Tests)

#### 2.4.1 Projekt (`ProjectSerializer`)

`id, created_at, updated_at, deleted_at, created_by, updated_by, name, description, description_text, description_html, network, workspace, identifier, default_assignee, project_lead, emoji, icon_prop, module_view, cycle_view, issue_views_view, page_view, intake_view, is_time_tracking_enabled, is_issue_type_enabled, guest_view_all_features, cover_image, cover_image_asset, estimate, archive_in, close_in, logo_props, default_state, archived_at, timezone, external_source, external_id` + `total_members, total_cycles, total_modules, is_member, member_role, is_deployed, cover_image_url` + `sort_order` (nur in der Liste V-PRJ-01 annotiert). Deklarierte Read-only-Felder ohne Annotation fehlen in der Antwort (DRF `SkipField`); Create (V-PRJ-02), Update (V-PRJ-05) und Detail (V-PRJ-04) laden über das annotierte `get_queryset()` neu und enthalten daher alle Zählfelder, aber **kein** `sort_order`. `cover_image_url` = `cover_image_asset.asset_url` (`/api/assets/v2/static/{id}/`) sonst `cover_image` sonst `null` (`M/project.py` Z. 129–139).

#### 2.4.2 Work Item (`IssueSerializer`)

`id, created_at, updated_at, deleted_at, created_by, updated_by, project, workspace, parent, state, point, estimate_point, name, description_html, description_binary, priority, start_date, target_date, sequence_id, sort_order, completed_at, archived_at, is_draft, external_source, external_id, type, type_id, assignees, labels`.
- `description_binary` (Django `BinaryField`, kein DRF-Mapping ⇒ `ModelField`-Fallback ⇒ `BinaryField.value_to_string` = **Base64-String** bzw. `null`); Eingabe ebenfalls Base64.
- `assignees`/`labels`: Listen von UUID-Strings, expandiert Objektlisten.
- Mit `expand=state|project|workspace|parent|created_by|updated_by|estimate_point`: Objekt statt UUID (2.1.6); `expand=type` → `type_id`-Wert.

#### 2.4.3 Kommentar, Link, Aktivität, Anhang, State, Label

Siehe Feldlisten in 2.3 (`IssueCommentSerializer`, `IssueLinkSerializer`, `IssueActivitySerializer`, `IssueAttachmentSerializer`, `StateSerializer`, `LabelSerializer`).

#### 2.4.4 Cycle (`CycleSerializer`)

Modellfelder (2.3) + Zählfelder. Zählfelder vorhanden in V-CYC-01/04/13 (Annotation), **fehlen** in V-CYC-02/05 (Neuladen ohne Annotation). `total_estimates`/`completed_estimates`/`started_estimates` (= `Sum(issue_cycle__issue__estimate_point__key)`) nur in V-CYC-13.

#### 2.4.5 Modul (`ModuleSerializer`)

Modellfelder (2.3) + `members` (ID-Strings) + 6 Zählfelder (vorhanden in V-MOD-01/04/11; **fehlen** in V-MOD-02/05).

#### 2.4.6 Intake (`IntakeIssueSerializer`)

`id, created_at, updated_at, deleted_at, created_by, updated_by, project, workspace, intake, issue, status, snoozed_till, duplicate_to, source, source_email, external_source, external_id, extra, issue_detail{IssueExpandSerializer: Issue-Modellfelder inkl. description_json/description_stripped/description_binary + description, labels[], assignees[], state{id,name,color,group}}, inbox`.

#### 2.4.7 Upload-Antworten (Assets/Anhänge)

`upload_data` = Rückgabe von boto3 `generate_presigned_post` über `S3Storage.generate_presigned_post(object_name, file_type, file_size)` = `{"url": "<S3/MinIO-Endpoint>/<bucket>", "fields": {"Content-Type", "key", "policy", + Signaturfelder des Signatur-Verfahrens (z. B. `x-amz-algorithm`, `x-amz-credential`, `x-amz-date`, `x-amz-signature`)}}` mit Bedingungen `bucket`, `["content-length-range", 1, size]`, `Content-Type`, `key`; Ablauf `signed_url_expiration`; bei `ClientError` → `null` (`SET/storage.py` Z. 68–102; A03 2.10). Client lädt per `multipart/form-data` direkt hoch und bestätigt per PATCH.

### 2.5 v1-Query-Parameter-Inventar

| Parameter | Endpunkte | Semantik | Quelle |
|---|---|---|---|
| `cursor` | alle paginierten | 2.1.5 | `UT/paginator.py` |
| `per_page` | alle paginierten | 2.1.5 | dito |
| `fields` | Endpunkte mit f/e ✓; V-PRJ-09 (eigene Semantik: Zählfelder) | 2.1.6 | `V1V/base.py` Z. 152–155 |
| `expand` | Endpunkte mit f/e ✓ | 2.1.6 | Z. 157–160 |
| `order_by` | V-PRJ-01/03, V-WI-01, V-ACT-01/02, V-CYC-03/07, V-MOD-03/07 | Allowlists 2.2; ungültig → Default (kein Fehler) | `UT/order_queryset.py` |
| `external_id`, `external_source` | V-WI-01 | Einzel-Lookup (beide nötig) | `V1V/issue.py` Z. 339–351 |
| `pql`, `filters` | V-WI-01 | nicht unterstützt → 400 | Z. 324–335 |
| `include_archived` | V-PRJ-03 | `true`/`1` | Z. 410–413 |
| `cycle_view` | V-CYC-01 | `all, current, upcoming, completed, draft, incomplete` | `V1V/cycle.py` Z. 199–297 |
| `search`, `limit`, `workspace_search`, `project_id` | V-WI-07 | 2.2.5 | `V1V/issue.py` Z. 2274–2323 |
| `query` | V-STK-01 | ICONTAINS `description_stripped` | `V1V/sticky.py` Z. 66–82 |

### 2.6 Public Space API (`/api/public/`)

#### 2.6.1 Basisklassen und Hilfsfunktionen (`SP/views/base.py`, `SP/views/issue.py`, `SP/views/asset.py`)

| Element | Z. | Verhalten |
|---|---|---|
| `TimezoneMixin` | `base.py` 33 | wie v1 (Benutzerzeitzone bei angemeldetem User) |
| `DeployBoardAnchorMixin.initial` | `base.py` 47–59 | Existiert ein `DeployBoard(anchor=<anchor>, entity_name="project")`, dessen `entity_identifier ≠ project_id`, wird **jeder** Request mit diesem Anchor mit `NotFound` (404 `{"detail": "Not found."}`) abgelehnt („A project board only serves the project it belongs to“). Nicht existierende Anchors passieren den Mixin (Fehler entsteht später in der View). |
| `BaseViewSet` | `base.py` 62 | `ModelViewSet`; `permission_classes = [IsAuthenticated]`; `authentication_classes = [BaseSessionAuthentication]` (Cookie `session-id`, Origin-Check für unsichere Methoden, A03); `filter_backends = (DjangoFilterBackend, SearchFilter)`; Fehlerbehandlung wie v1-`BaseViewSet`, 404-Text „The required object does not exist.“; **kein** Body-Typ-Check, **keine** Pagination-Klasse (Listen unpaginiert) |
| `BaseAPIView` | `base.py` 150 | `APIView`; sonst wie `BaseViewSet`; `project_id` nur aus `kwargs` |
| Anonymer Throttle | `SET/common.py` Z. 141–145 | `AnonRateThrottle` `30/minute` je Client-IP (alle anonymen Space-Requests) |
| `_issue_in_board_scope(issue_id, board)` | `issue.py` 76–87 | `Issue.issue_objects` mit `id`, `project_id = board.project_id`, `workspace_id = board.workspace_id` existiert |
| `_comment_in_board_scope(comment_id, board)` | `issue.py` 90–97 | `IssueComment` mit `id`, Board-Projekt/-Workspace, `access="EXTERNAL"` existiert |
| `_public_comment_content(data)` | `issue.py` 100–103 | übernimmt **nur** `comment_html`, `comment_json` aus dem Body |
| `_is_own_board_comment(comment_id, board, user)` | `asset.py` 26–35 | EXTERNAL-Kommentar im Board-Projekt mit `actor = user` |
| Board-Auflösung | diverse | Je View unterschiedlich: `DeployBoard.objects.get/filter(anchor=…)` **mit** `entity_name="project"` (Settings, Meta, Issues-Liste, Kommentare, Reaktionen, Votes, Intake, Asset-DELETE/Restore/Bulk) bzw. **ohne** (`IssueRetrievePublicEndpoint`, `ProjectCyclesEndpoint`, `ProjectModulesEndpoint`, `ProjectStatesEndpoint`, `ProjectLabelsEndpoint`, `ProjectMembersEndpoint`, Asset-GET/POST/PATCH) |
| `DeployBoard.is_disabled` | `M/deploy_board.py` Z. 39 | wird von **keinem** Space-Endpunkt geprüft |
| `DeployBoard.view_props` | Z. 37 | nur im Frontend ausgewertet (erlaubte Layouts), nicht im Backend |

#### 2.6.2 Endpunkt-Inventar Space (`SP/urls/*.py`)

| ID | Methode | Pfad | View (Datei Z.) | Berechtigung | Request | Response | Seiteneffekte / Besonderheiten |
|---|---|---|---|---|---|---|---|
| S-01 | GET | `{A}/meta/` | `ProjectMetaDataEndpoint.get` (`meta.py` 19) | `AllowAny` | – | 200 Space-`ProjectLiteSerializer`: `id, identifier, name, cover_image, icon_prop, emoji, description`; 404 `{"error": "Project is not published"}` (Board oder Projekt fehlt) | Projekt über `entity_identifier` |
| S-02 | GET | `{A}/settings/` | `ProjectDeployBoardPublicSettingsEndpoint.get` (`project.py` 22) | `AllowAny` | – | 200 App-`DeployBoardSerializer`: alle `DeployBoard`-Felder (`id, created_at, updated_at, deleted_at, created_by, updated_by, workspace, project, entity_identifier, entity_name, anchor, is_comments_enabled, is_reactions_enabled, intake, is_votes_enabled, view_props, is_activity_enabled, is_disabled`) + `project_details{id, identifier, name, cover_image, cover_image_url, logo_props, description}` + `workspace_detail{name, slug, id, logo_url}`; 404 generisch | |
| S-03 | GET | `/api/public/workspaces/{slug}/projects/{project_id}/anchor/` | `WorkspaceProjectAnchorEndpoint.get` (`project.py` 57) | `AllowAny` | – | 200 `DeployBoardSerializer` (wie S-02); 404 generisch | Lookup `workspace__slug`, `project_id`, `entity_identifier=project_id`, `entity_name="project"`; ermöglicht anonymen Abruf des Anchors jedes veröffentlichten Projekts bei bekannter Projekt-ID (Legacy-Route des Space, A11 3.18) |
| S-04 | GET | `/api/public/workspaces/{slug}/project-boards/` | `WorkspaceProjectDeployBoardEndpoint.get` (`project.py` 31) | `AllowAny` | – | **immer 500** | Signatur `get(self, request, anchor)` passt nicht zur URL (`slug`) ⇒ `TypeError`; zusätzlich `.values_list` ohne Aufruf. Defekt, ungenutzt. |
| S-05 | GET | `{A}/issues/` | `ProjectIssuesPublicEndpoint.get` (`issue.py` 109) | `AllowAny` | Filter-Query (`issue_filters`, 3.17), `order_by` (Issue-Allowlist, Default `-created_at`), `group_by`, `sub_group_by` (∈ `ISSUE_GROUP_BY_ALLOWLIST`), `cursor`, `per_page` | 200 Paginierungs-Envelope; ohne Gruppierung `results` = Liste; mit `group_by` `results = {gruppe: {"results": [...], "total_results": n}}`; mit Subgruppe verschachtelt; Felder je Issue: `id, name, state_id, sort_order, estimate_point, priority, start_date, target_date, sequence_id, project_id, parent_id, cycle_id, created_by, state__group, assignee_ids, label_ids, module_ids, vote_items, reaction_items` (`SP/utils/grouper.py`); 400 `{"error": "Group by and sub group by cannot have same parameters"}`; 400 `{"detail": "Invalid group_by field: …"}`; 404 `{"error": "Project is not published"}` | Menge `Issue.issue_objects` des Board-Projekts; `link_count`, `attachment_count`, `sub_issues_count` werden annotiert, aber von `.values()` **nicht** ausgegeben; Gruppen-Zählfilter `count_filter` (Intake-Status 1/-1/2 oder kein Intake, nicht archiviert, kein Entwurf); `group_by ∈ {target_date, start_date, created_by}` → 500 (fehlender Queryset-Parameter in `issue_group_values`) |
| S-06 | GET | `{A}/issues/{issue_id}/` | `IssueRetrievePublicEndpoint.get` (`issue.py` 689) | `AllowAny` | – | 200 Objekt `{id, name, state_id, sort_order, description_json, description_html, description_stripped, description_binary, module_ids, label_ids, assignee_ids, estimate_point, priority, start_date, target_date, sequence_id, project_id, parent_id, cycle_id, created_by, state__group, vote_items[], reaction_items[]}`; **200 `null`**, wenn das Issue nicht (mehr) sichtbar ist; 404 generisch, wenn Anchor unbekannt | `vote_items[i] = {vote, actor_details{id, first_name, last_name, avatar, avatar_url, display_name}}`; `reaction_items[i] = {reaction, actor_details{…}}` – `avatar_url` der Reaktionen wird fälschlich aus `votes__actor__*` berechnet (Z. 803–816); `description_binary` als Rohbytes (Serialisierung siehe 6) |
| S-07 | GET | `{A}/issues/{issue_id}/comments/` | `IssueCommentPublicViewSet.list` (DRF, `issue.py` 247) | `AllowAny` | DjangoFilter `issue__id`, `workspace__id` | 200 unpaginierte Liste App-`IssueCommentSerializer` (`__all__` + `actor_detail`, `issue_detail`, `project_detail`, `workspace_detail`, `comment_reactions[]`, `is_member`) | nur `access="EXTERNAL"`, Sortierung `created_at` aufsteigend; leer, wenn `is_comments_enabled=false` oder Anchor unbekannt |
| S-08 | POST | `{A}/issues/{issue_id}/comments/` | `….create` (291) | `IsAuthenticated` | `{comment_html, comment_json}` (alles andere ignoriert) | 201 Kommentar; 400 `{"error": "Comments are not enabled for this project"}`; 404 `{"error": "Issue not found"}` | `actor=user`, `access="EXTERNAL"`, Board-Projekt; `issue_activity("comment.activity.created")`; `ProjectPublicMember.get_or_create` für Nicht-Projektmitglieder |
| S-09 | GET | `{A}/issues/{issue_id}/comments/{pk}/` | `….retrieve` (DRF) | `AllowAny` | – | 200 Kommentar; 404 `{"detail": "No IssueComment matches the given query."}` | gleicher Queryset-Filter wie S-07 |
| S-10 | PATCH | `{A}/issues/{issue_id}/comments/{pk}/` | `….partial_update` (334) | `IsAuthenticated` | `{comment_html, comment_json}` | 200; 400 Kommentare deaktiviert; 404 (nicht eigener/fremdes Board) | nur eigener EXTERNAL-Kommentar des Board-Projekts; `issue_activity("comment.activity.updated")`; `edited_at` wird **nicht** gesetzt |
| S-11 | DELETE | `{A}/issues/{issue_id}/comments/{pk}/` | `….destroy` (368) | `IsAuthenticated` | – | 204; 400; 404 | `issue_activity("comment.activity.deleted")`, Soft-Delete |
| S-12 | GET | `{A}/issues/{issue_id}/reactions/` | `IssueReactionPublicViewSet.list` (DRF) | `IsAuthenticated` | – | 200 **immer `[]`** | `get_queryset` sucht Board über nicht vorhandene Kwargs `slug`/`project_id` (Z. 402–419) |
| S-13 | POST | `{A}/issues/{issue_id}/reactions/` | `….create` (422) | `IsAuthenticated` | `{"reaction": "<string>"}` | 201 App-`IssueReactionSerializer` (`__all__` + `actor_detail`); 400 `{"error": "Reactions are not enabled for this project board"}`; 404 `{"error": "Issue not found"}`; 400 `{"error": "The payload is not valid"}` (doppelte Reaktion) | `ProjectPublicMember`; `issue_activity("issue_reaction.activity.created")` |
| S-14 | DELETE | `{A}/issues/{issue_id}/reactions/{reaction_code}/` | `….destroy` (463) | `IsAuthenticated` | – | 204; 400 deaktiviert; 404 | eigene Reaktion im Board-Projekt; `issue_activity("issue_reaction.activity.deleted")` |
| S-15 | GET | `{A}/comments/{comment_id}/reactions/` | `CommentReactionPublicViewSet.list` (DRF) | `IsAuthenticated` | – | 200 Liste App-`CommentReactionSerializer` (`id, actor, comment, reaction, display_name, deleted_at, workspace, project, created_at, updated_at, created_by, updated_by`) | nur EXTERNAL-Kommentare des Boards; leer, wenn Reaktionen deaktiviert |
| S-16 | POST | `{A}/comments/{comment_id}/reactions/` | `….create` (519) | `IsAuthenticated` | `{"reaction"}` | 201; 400 `{"error": "Reactions are not enabled for this board"}`; 404 `{"error": "Comment not found"}` | `ProjectPublicMember`; `issue_activity("comment_reaction.activity.created", issue_id=None)` |
| S-17 | DELETE | `{A}/comments/{comment_id}/reactions/{reaction_code}/` | `….destroy` (566) | `IsAuthenticated` | – | 204; 400; 404 | eigene Reaktion auf EXTERNAL-Kommentar; Activity `comment_reaction.activity.deleted` |
| S-18 | GET | `{A}/issues/{issue_id}/votes/` | `IssueVotePublicViewSet.list` (DRF) | `IsAuthenticated` | – | 200 **immer `[]`** | `get_queryset` filtert `workspace__slug=<anchor>` (Z. 607–621) |
| S-19 | POST | `{A}/issues/{issue_id}/votes/` | `….create` (624) | `IsAuthenticated` | `{"vote": 1 \| -1}` (Default 1, **nicht validiert**) | 201 App-`IssueVoteSerializer` (`issue, vote, workspace, project, actor, actor_detail`); 400 `{"error": "Votes are not enabled for this project board"}`; 404 `{"error": "Issue not found"}` | `get_or_create` je (Issue, User) und Überschreiben des Werts; `ProjectPublicMember`; `issue_activity("issue_vote.activity.created")` |
| S-20 | DELETE | `{A}/issues/{issue_id}/votes/` | `….destroy` (665) | `IsAuthenticated` | – | 204; 404 | **ohne** `is_votes_enabled`-Prüfung; `issue_activity("issue_vote.activity.deleted")` |
| S-21 | GET | `{A}/cycles/` | `ProjectCyclesEndpoint.get` (`cycle.py` 18) | `AllowAny` | – | 200 `[{id, name}]` (alle, inkl. archivierter); 404 `{"error": "Invalid anchor"}` | ungenutzt im Frontend |
| S-22 | GET | `{A}/modules/` | `ProjectModulesEndpoint.get` (`module.py` 18) | `AllowAny` | – | 200 `[{id, name}]`; 404 `{"error": "Invalid anchor"}` | ungenutzt |
| S-23 | GET | `{A}/states/` | `ProjectStatesEndpoint.get` (`state.py` 21) | `AllowAny` | – | 200 `[{name, group, color, id, sequence}]`; 404 `{"error": "Invalid anchor"}` | ohne Triage-Gruppe (Manager) und ohne States namens „Triage“ |
| S-24 | GET | `{A}/labels/` | `ProjectLabelsEndpoint.get` (`label.py` 18) | `AllowAny` | – | 200 `[{id, name, color, parent}]`; 404 `{"error": "Invalid anchor"}` | |
| S-25 | GET | `{A}/members/` | `ProjectMembersEndpoint.get` (`project.py` 68) | `AllowAny` | – | 200 `[{id (ProjectMember-ID), member (User-ID), member__display_name, member__avatar}]`; 404 `{"error": "Invalid anchor"}` | nur aktive; ungenutzt im Frontend |
| S-26 | GET | `{A}/intakes/{intake_id}/intake-issues/` (+ Alias `…/inbox-issues/`) | `IntakeIssuePublicViewSet.list` (`intake.py` 57) | `IsAuthenticated` | `issue_filters`-Query | 200 Liste App-`IssueStateIntakeSerializer` (Issue `__all__` + `state_detail`, `project_detail`, `label_details[]`, `assignee_details[]`, `sub_issues_count`, `issue_intake[{id, status, duplicate_to, snoozed_till, source}]`, `bridge_id`); 400 `{"error": "Intake is not enabled for this Project Board"}` (Board ohne `intake`) | **Listet alle Intake-Issues aller Einreicher** des angegebenen Intakes im Board-Projekt (keine Bindung `intake_id == board.intake_id`, keine Einreicher-Filterung); Sortierung `snoozed_till`, `status` |
| S-27 | POST | `{A}/intakes/{intake_id}/intake-issues/` (+ Alias) | `….create` (108) | `IsAuthenticated` | `{"issue": {"name" (Pflicht), "priority" (Check-Default `none`, Speicher-Default **`low`**), "description_html", "description_json"}}` | **200** `IssueStateIntakeSerializer`; 400 `{"error": "Intake is not enabled for this Project Board"}`; 400 `{"error": "Intake does not belong to this Project Board"}`; 400 `{"error": "Name is required"}`; 400 `{"error": "Invalid priority"}` | Triage-State suchen/erzeugen (wie V-INT-02); HTML sanitisiert; `issue_activity("issue.activity.created")`; `IntakeIssue(source="IN_APP")` |
| S-28 | GET | `{A}/intakes/{intake_id}/intake-issues/{pk}/` | `….retrieve` (250) | `IsAuthenticated` | – (`pk` = IntakeIssue-ID) | 200 `IssueStateIntakeSerializer`; 400 Intake deaktiviert | jeder angemeldete Nutzer, keine Einreicherprüfung |
| S-29 | PATCH | `{A}/intakes/{intake_id}/intake-issues/{pk}/` | `….partial_update` (189) | `IsAuthenticated` + Einreicher (`created_by`) | `{"issue": {name, description_html, description_json}}` | 200 App-`IssueCreateSerializer`-Daten; 400 `{"error": "You cannot edit intake issues"}`; 400 Intake deaktiviert | Kontext `allow_triage_state=True`; `issue_activity("issue.activity.updated")`; ohne `issue`-Key → `AttributeError` (`False.get`) → 500 |
| S-30 | DELETE | `{A}/intakes/{intake_id}/intake-issues/{pk}/` | `….destroy` (272) | `IsAuthenticated` + Einreicher | – | 204; 400 `{"error": "You cannot delete intake issue"}` | löscht nur `IntakeIssue` (Issue bleibt) |
| S-31 | POST | `/api/public/assets/v2/anchor/{anchor}/` | `EntityAssetEndpoint.post` (`asset.py` 87) | `IsAuthenticated` | `{name, type (Default image/jpeg), size (int, Default FILE_SIZE_LIMIT), entity_type = "COMMENT_DESCRIPTION", entity_identifier (Kommentar-ID oder "")}` | 200 `{"upload_data", "asset_id", "asset_url"}`; 404 `{"error": "Project is not published"}`; 400 `{"error": "Comments are not enabled for this project"}`; 400 `{"error": "Invalid size.", "status": false}`; 400 `{"error": "Invalid entity type.", "status": false}`; 404 `{"error": "Comment not found"}`; 400 `{"error": "Invalid file type. Only JPEG, PNG, WebP, JPG and GIF files are allowed.", "status": false}` | Größe auf [1, FILE_SIZE_LIMIT] geklemmt; Key `"{workspace_id}/{uuid4hex}-{name}"`; `comment_id` = `entity_identifier` oder `null` |
| S-32 | GET | `/api/public/assets/v2/anchor/{anchor}/{pk}/` | `….get` (46) | `AllowAny` | – | **302** auf Presigned-URL (`inline` nur für INLINE_SAFE_MIME_TYPES); 404 `{"error": "Requested resource could not be found."}` (Anchor) / `{"error": "The requested asset could not be found."}` (nicht hochgeladen) / generisch | nur `ISSUE_DESCRIPTION`/`COMMENT_DESCRIPTION` des Board-Projekts (auch Bilder aus **INTERNAL**-Kommentaren und beliebigen Issues des Projekts) |
| S-33 | PATCH | `/api/public/assets/v2/anchor/{anchor}/{pk}/` | `….patch` (177) | `IsAuthenticated` | `{"attributes": {...}}` | 204; 404 | **beliebiges** Asset des Board-Projekts (keine Eigentümerprüfung): `is_uploaded=True`, `attributes` überschreiben; Metadaten-Task |
| S-34 | DELETE | `/api/public/assets/v2/anchor/{anchor}/{pk}/` | `….delete` (198) | `IsAuthenticated` | – | 204; 404 | **beliebiges** Asset des Board-Projekts: `is_deleted=True` |
| S-35 | POST | `/api/public/assets/v2/anchor/{anchor}/restore/{pk}/` | `AssetRestoreEndpoint.post` (217) | `IsAuthenticated` | – | 204; 404 | **beliebiges** (auch gelöschtes, `all_objects`) Asset des Board-Projekts wiederherstellen |
| S-36 | POST | `/api/public/assets/v2/anchor/{anchor}/{entity_id}/bulk/` | `EntityBulkAssetEndpoint.post` (235) | `IsAuthenticated` + eigener EXTERNAL-Kommentar | `{"asset_ids": [...]}` | 204; 400 `{"error": "No asset ids provided."}`; 400 Kommentare deaktiviert; 404 `{"error": "Comment not found"}` / `{"error": "The requested asset could not be found."}` | bindet nur eigene `COMMENT_DESCRIPTION`-Assets (`comment_id = entity_id`) |
| – | GET/PATCH/DELETE bzw. POST | `assets/v2/anchor/{anchor}/` bzw. `…/{pk}/` | `EntityAssetEndpoint` (ohne `http_method_names`) | – | – | 500 (`TypeError`, fehlendes/überzähliges `pk`) | Nebenprodukt der gemeinsamen View-Klasse |

Gesamt: 36 benannte Kombinationen + 2 Alias-Kombinationen (`inbox-issues` GET/POST) = 38.

#### 2.6.3 Veröffentlichung verwalten (App-API, Querverweis)

Die Veröffentlichung selbst (Anlegen/Ändern/Löschen eines `DeployBoard`) erfolgt über die **interne** App-API `GET/POST {/api/workspaces/{slug}/projects/{project_id}}/project-deploy-boards/` und `GET/PATCH/DELETE …/project-deploy-boards/{pk}/` (`apps/api/plane/app/urls/project.py` Z. 112–121, `DeployBoardViewSet` `apps/api/plane/app/views/project/base.py` Z. 539–590; vollständig in A03 2.6). Relevantes Verhalten für die Space-API:

| Aspekt | Verhalten | Quelle |
|---|---|---|
| Berechtigung | `ProjectMemberPermission` (Lesen: PM; Schreiben: PM Rolle A/M) | `apps/api/plane/app/views/project/base.py` Z. 540 |
| Anlage | `get_or_create(entity_name="project", entity_identifier=project_id, project_id=project_id)`; Werte aus Body: `is_comments_enabled` (Default false), `is_reactions_enabled` (false), `intake` (UUID eines Intakes **desselben** Projekts, sonst 400 `{"error": "Intake is not valid"}`), `is_votes_enabled` (false), `views` → `view_props` (Default `{"list": true, "kanban": true, "calendar": true, "gantt": true, "spreadsheet": true}`); 404 `{"error": "Project does not exist"}` bei Projekt aus anderem Workspace | Z. 552–590 |
| Unveränderlich | `workspace, project, anchor, entity_identifier, entity_name` read-only; `validate_intake` | `apps/api/plane/app/serializers/project.py` Z. 248–262 |
| Anchor | `uuid4().hex` (32 Zeichen, unique) | `M/deploy_board.py` Z. 15–16, 32 |
| Eindeutigkeit | ein Board je (`entity_name`, `entity_identifier`) solange nicht gelöscht | `M/deploy_board.py` Z. 46–53 |
| `ProjectPublicMember` | Tabelle `project_public_members` (`project, workspace, member`), unique je Projekt/User; wird von S-08/S-13/S-16/S-19 befüllt („workspace tracking“); in CE sonst ungenutzt | `M/project.py` Z. 370–389 |

### 2.7 Instanz-API (`/api/instances/`, `LIC/`)

#### 2.7.1 Basisklassen, Permission, Session

| Element | Verhalten | Quelle |
|---|---|---|
| `LIC/api/views/base.py` `BaseAPIView` | `APIView` + `TimezoneMixin` + `BasePaginator`; `permission_classes = [InstanceAdminPermission]`; `authentication_classes = [BaseSessionAuthentication]`; Fehlerbehandlung wie Space (404-Text „The required object does not exist.“) | Z. 26–119 |
| Abweichende Basis | `InstanceEndpoint`, `SignUpScreenVisitedEndpoint` (`LIC/api/views/instance.py`) und `InstanceWorkSpaceAvailabilityCheckEndpoint`, `InstanceWorkSpaceEndpoint` (`LIC/api/views/workspace.py`) erben von **`plane.app.views.BaseAPIView`** (App-Basis, A03 2.1) | Importe |
| Form-Views | `InstanceAdminSignUpEndpoint`, `InstanceAdminSignInEndpoint`, `InstanceAdminSignOutEndpoint` erben von Django `View` – `permission_classes` dort **wirkungslos**; Django `CsrfViewMiddleware` verlangt `csrfmiddlewaretoken` (Token via `GET /auth/get-csrf-token/` → `{"csrf_token"}`); CSRF-Fehler rendern `csrf_failure.html` (`CSRF_FAILURE_VIEW`) | `LIC/api/views/admin.py`; `AUTH/views/common.py` Z. 29–45; `SET/common.py` Z. 437–439 |
| `InstanceAdminPermission` | angemeldet **und** `InstanceAdmin(role >= 15, instance = Instance.objects.first(), user = request.user)` existiert | `LIC/api/permissions/instance.py` |
| Admin-Session-Cookie | Für **alle** Pfade, die die Zeichenkette `instances` enthalten, liest/schreibt `SessionMiddleware` das Cookie **`admin-session-id`** (statt `session-id`); `max_age = ADMIN_SESSION_COOKIE_AGE` (Env, Default **3600 s**); Admin-Login setzt zusätzlich `request.session.set_expiry(ADMIN_SESSION_COOKIE_AGE)` | `AUTH/middleware/session.py`; `AUTH/utils/login.py` Z. 14–28; `SET/common.py` Z. 431–432 |
| Redirect-Basis | `base_host(request, is_admin=True)` = `ADMIN_BASE_URL + ADMIN_BASE_PATH` (Default `/god-mode/`), sonst `WEB_URL`/`APP_BASE_URL` + `ADMIN_BASE_PATH` | `AUTH/utils/host.py` Z. 16–39 |
| Response-Cache | `cache_response(timeout, path=None, user=False)`: Schlüssel = `request.get_full_path()` (inkl. Query-String), gespeichert nur bei 200 und `DEBUG=False`; `invalidate_cache(path, user=False)` löscht genau den Schlüssel `path` **vor** Ausführung der View | `UT/cache.py` |

#### 2.7.2 Endpunkt-Inventar Instanz (`LIC/urls.py`)

| ID | Methode | Pfad | View (Datei Z.) | Berechtigung | Request | Response | Seiteneffekte / Besonderheiten |
|---|---|---|---|---|---|---|---|
| I-01 | GET | `{I}/` | `InstanceEndpoint.get` (`instance.py` 36) | `AllowAny` | – | 200 `{"config": {…}, "instance": {…}}` (2.7.5); ohne Instanz-Datensatz 200 `{"is_activated": false, "is_setup_done": false}` (flach!) | Server-Cache 2 h (Schlüssel `/api/instances/`), `Cache-Control: private, max-age=12` nur bei Cache-Miss (Decorator-Reihenfolge) |
| I-02 | PATCH | `{I}/` | `InstanceEndpoint.patch` (162) | `InstanceAdminPermission` | `InstanceSerializer` partiell: schreibbar sind **alle** Instanzfelder außer `id`, `last_checked_at`, `is_setup_done` und Audit-Feldern (schreibbar: `instance_name`, `whitelist_emails`, `instance_id`, `current_version`, `latest_version`, `edition`, `domain`, `namespace`, `is_telemetry_enabled`, `is_support_required`, `is_signup_screen_visited`, `is_verified`, `is_test`, `is_current_version_deprecated`, `created_by`, `updated_by`, `deleted_at`); Admin-UI sendet `instance_name`, `is_telemetry_enabled` | 200 `InstanceSerializer`; 400 Serializer-Fehler | invalidiert `/api/instances/` |
| I-03 | GET | `{I}/admins/` | `InstanceAdminEndpoint.get` (`admin.py` 73) | `InstanceAdminPermission` | – | 200 Liste `InstanceAdminSerializer` (`id, created_at, updated_at, deleted_at, created_by, updated_by, user, instance, role, is_verified, user_detail{id, first_name, last_name, avatar, avatar_url, is_bot, display_name, email, last_login_medium}`); 403 `{"error": "Instance is not registered yet"}` | Cache 2 h (`/api/instances/admins/`), wird von I-04/I-05 **nicht** invalidiert |
| I-04 | POST | `{I}/admins/` | `InstanceAdminEndpoint.post` (51) | `InstanceAdminPermission` | `{"email" (Pflicht), "role" (Default 20)}` | 201 `InstanceAdminSerializer`; 400 `{"error": "Email is required"}`; 403 `{"error": "Instance is not registered yet"}`; 404 `{"error": "The required object does not exist."}` (kein User mit E-Mail); 400 `{"error": "The payload is not valid"}` (bereits Admin) | `role` beliebige Zahl (Choices nur 20; Permission verlangt ≥ 15); invalidiert `/api/instances/`; keine UI |
| I-05 | DELETE | `{I}/admins/{pk}/` | `InstanceAdminEndpoint.delete` (85) | `InstanceAdminPermission` | – | 204 (auch wenn nicht vorhanden) | Löschen des **eigenen/letzten** Admins möglich; invalidiert `/api/instances/`; keine UI |
| – | GET/POST bzw. DELETE | `{I}/admins/{pk}/` bzw. `{I}/admins/` | `InstanceAdminEndpoint` | – | – | 500 (`TypeError`) | Nebenprodukt gemeinsamer Klasse |
| I-06 | GET | `{I}/admins/me/` | `InstanceAdminUserMeEndpoint.get` (412) | `InstanceAdminPermission` | – | 200 `InstanceAdminMeSerializer`: `id, avatar, avatar_url, cover_image, date_joined, display_name, email, first_name, last_name, is_active, is_bot, is_email_verified, user_timezone, username, is_password_autoset` | |
| I-07 | GET | `{I}/admins/session/` | `InstanceAdminUserSessionEndpoint.get` (420) | `AllowAny` | – | 200 `{"is_authenticated": true, "user": InstanceAdminMeSerializer}` bzw. `{"is_authenticated": false}` | Prüft `InstanceAdmin` **ohne** Instanzbindung und **ohne** Rollenprüfung; keine UI |
| I-08 | POST | `{I}/admins/sign-in/` | `InstanceAdminSignInEndpoint.post` (275) | Django `View`, Throttle `AuthenticationThrottle` | `application/x-www-form-urlencoded`: `csrfmiddlewaretoken`, `email`, `password` | **302** → `{admin_base}general/` bei Erfolg; sonst 302 → `{admin_base}?error_code=<n>&error_message=<CODE>[&email=…]` (Codes 2.7.6) | Ablauf 3.23; invalidiert `/api/instances/` |
| I-09 | POST | `{I}/admins/sign-up/` | `InstanceAdminSignUpEndpoint.post` (96) | Django `View`, Throttle | Form: `csrfmiddlewaretoken`, `email`, `password`, `first_name`, `last_name`, `company_name`, `is_telemetry_enabled` (`"True"`/`"False"`, Default `True`); UI sendet zusätzlich `confirm_password` (ignoriert) | 302 → `{admin_base}general/`; Fehler-302 mit Payload (`email, first_name, last_name, company_name, is_telemetry_enabled`) | Ablauf 3.22 (Row-Lock gegen Doppel-Setup) |
| I-10 | POST | `{I}/admins/sign-out/` | `InstanceAdminSignOutEndpoint.post` (433) | Django `View` (keine Prüfung) | Form `csrfmiddlewaretoken` | 302 → `{admin_base}` | `last_logout_ip`, `last_logout_time` setzen, `logout()`; Fehler (z. B. anonym) ⇒ ebenfalls Redirect |
| I-11 | POST | `{I}/admins/sign-up-screen-visited/` | `SignUpScreenVisitedEndpoint.post` (`instance.py` 176) | **`AllowAny`** | – | 204; 400 `{"error": "Instance is not configured"}` | `is_signup_screen_visited = True` (anonym setzbar); invalidiert `/api/instances/`; keine UI |
| I-12 | GET | `{I}/configurations/` | `InstanceConfigurationEndpoint.get` (`configuration.py` 36) | `InstanceAdminPermission` | – | 200 Liste `InstanceConfigurationSerializer`: `id, created_at, updated_at, deleted_at, created_by, updated_by, key, value, category, is_encrypted` – **verschlüsselte Werte werden entschlüsselt ausgeliefert** | Cache 2 h (`/api/instances/configurations/`) |
| I-13 | PATCH | `{I}/configurations/` | `….patch` (43) | `InstanceAdminPermission` | `{"<KEY>": <wert>, …}` | 200 Liste der **betroffenen** Konfigurationen (entschlüsselt) | Nur existierende Keys; `None` → `""`, sonst `str(v).strip()`; bei `is_encrypted` → `encrypt_data(value)` (leerer String bleibt `""`); `bulk_update`; invalidiert `/api/instances/configurations/` und `/api/instances/` |
| I-14 | DELETE | `{I}/configurations/disable-email-feature/` | `DisableEmailFeatureEndpoint.delete` (66) | `InstanceAdminPermission` | – | 200 (leer); 400 `{"error": "Failed to disable email configuration"}` | `ENABLE_SMTP = "0"`; `EMAIL_HOST`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `EMAIL_PORT`, `EMAIL_FROM` = `""` (`EMAIL_USE_TLS`/`EMAIL_USE_SSL` unverändert); invalidiert nur `/api/instances/` (Konfigurationsliste bis 2 h veraltet) |
| I-15 | POST | `{I}/email-credentials-check/` | `EmailCredentialCheckEndpoint.post` (89) | `InstanceAdminPermission` | `{"receiver_email"}` | 200 `{"message": "Email successfully sent."}`; 400 `{"error": "Receiver email is required"}`; 400 je SMTP-Fehler: `"Invalid email header."`, `"Invalid credentials provided"`, `"Could not connect with the SMTP server."`, `"From address is invalid."`, `"SMTP server disconnected unexpectedly."`, `"All recipient addresses were refused."`, `"Timeout error while trying to connect to the SMTP server."`, `"Network connection error. Please check your internet connection."`, `"Could not send email. Please check your configuration"` | Betreff „Email Notification from Plane“, Text „This is a sample email notification sent from Plane application.“; `int(EMAIL_PORT)` außerhalb des `try` ⇒ leerer Port → 500 |
| I-16 | GET | `{I}/workspace-slug-check/?slug=` | `InstanceWorkSpaceAvailabilityCheckEndpoint.get` (`workspace.py` 22) | `InstanceAdminPermission` | `slug` | 200 `{"status": true}` = verfügbar; 400 `{"error": "Workspace Slug is required"}` | `slug__iexact` vorhanden oder in `RESTRICTED_WORKSPACE_SLUGS` (2.7.8) ⇒ `false` |
| I-17 | GET | `{I}/workspaces/` | `InstanceWorkSpaceEndpoint.get` (40) | `InstanceAdminPermission` | `cursor`, `per_page` (Default/Max **10**), `search` (Name ICONTAINS) | 200 Paginierungs-Envelope mit `WorkspaceSerializer` (`id, created_at, updated_at, deleted_at, created_by, updated_by, name, logo, logo_asset, owner{id, email, first_name, last_name}, slug, organization_size, timezone, background_color, logo_url, total_projects, total_members`) | `total_projects` = alle Projekte (inkl. archivierter), `total_members` = aktive Nicht-Bot-Mitglieder; Sortierung Model-Default |
| I-18 | POST | `{I}/workspaces/` | `InstanceWorkSpaceEndpoint.post` (71) | `InstanceAdminPermission` | `WorkspaceSerializer`-schreibbar: `name`, `slug`, `organization_size`, `timezone`, `background_color`, `logo`, `logo_asset`, `deleted_at`; zusätzlich `company_role` (für die Mitgliedschaft); Admin-UI sendet `name`, `slug`, `organization_size` | 201 `WorkspaceSerializer`; 400 `{"error": "Both name and slug are required"}`; 400 `{"error": "The maximum length for name is 80 and for slug is 48"}`; 400 `{"name": ["Name must not contain URLs"]}` / `{"name": ["Name must contain at least one letter or number"]}` / `{"slug": ["Slug is not valid"]}` / `{"slug": ["Slug is already in use"]}`; 409 `{"slug": "The workspace with the slug already exists"}` | `owner = Admin`; `WorkspaceMember(role=20, company_role)`; **kein** `workspace_seed`-Task (anders als App-Workspace-Create, `apps/api/plane/app/views/workspace/base.py` Z. 138) und **keine** Prüfung von `DISABLE_WORKSPACE_CREATION` |

Gesamt: 18 Methode×Pfad-Kombinationen (+ 3 fehlerhafte Nebenkombinationen). Die Admin-UI ruft außerdem `GET /api/instances/changelog/` auf, das **nicht** existiert (A11 2.7; kein Pattern in `LIC/urls.py`).

#### 2.7.3 Modelle (`LIC/models/instance.py`)

| Modell (Tabelle) | Felder (zusätzlich zu `BaseModel`: `id, created_at, updated_at, deleted_at, created_by, updated_by`) | Bemerkungen |
|---|---|---|
| `Instance` (`instances`) | `instance_name` (255), `whitelist_emails` (Text, null), `instance_id` (255, unique), `current_version` (255), `latest_version` (255, null), `edition` (255, Default `PLANE_COMMUNITY`), `domain` (Text), `last_checked_at` (DateTime), `namespace` (255, null), `is_telemetry_enabled` (Default **true**), `is_support_required` (true), `is_setup_done` (false), `is_signup_screen_visited` (false), `is_verified` (false), `is_test` (false), `is_current_version_deprecated` (false) | Singleton per `Instance.objects.first()`; `ordering = -created_at`. `whitelist_emails`, `namespace`, `is_support_required`, `is_verified`, `is_current_version_deprecated`, `domain` werden in CE **nirgends** ausgewertet (grep). |
| `InstanceAdmin` (`instance_admins`) | `user` (FK User, `SET_NULL`, null), `instance` (FK, CASCADE), `role` (Choices nur `(20, "Admin")`, Default 20), `is_verified` (false) | `unique_together (instance, user)` |
| `InstanceConfiguration` (`instance_configurations`) | `key` (100, unique), `value` (Text, null), `category` (Text), `is_encrypted` (Bool) | Key/Value-Store aller God-Mode-Einstellungen |
| `ChangeLog` (`changelogs`) | `title` (255), `description` (Text), `version` (255), `tags` (JSON, Default `[]`), `release_date` (DateTime, null), `is_release_candidate` (false) | **kein** Endpunkt, keine Nutzung in CE; der In-App-Changelog lädt `config.instance_changelog_url` (`apps/web/components/global/product-updates/changelog.tsx` Z. 27) |
| Migrationen | `0001_initial`, `0002_rename_version_instance_current_version_and_more`, `0003_alter_changelog_title_alter_changelog_version_and_more`, `0004_changelog_deleted_at_instance_deleted_at_and_more`, `0005_rename_product_instance_edition_and_more`, `0006_instance_is_current_version_deprecated` | Greenfield (ADR-003): nicht zu übernehmen |

#### 2.7.4 InstanceConfiguration-Keys (vollständig, Seed aus `UT/instance_config_variables/core.py`; `extended.py` ist leer)

Seed: `python manage.py configure_instance` legt fehlende Keys mit Wert aus der Umgebungsvariablen gleichen Namens (bzw. Default) an; vorhandene Keys bleiben unverändert (`LIC/management/commands/configure_instance.py`). Lesen: `get_configuration_value([{key, default}])` – bei `SKIP_ENV_VAR` (Env, Default `"1"`) aus der DB (entschlüsselt), fehlt der Key in der DB → übergebener Default; bei `SKIP_ENV_VAR="0"` **nur** aus Umgebungsvariablen (`LIC/utils/instance_value.py`; `SET/common.py` Z. 401).

| # | Key | Kategorie | verschlüsselt | Seed-Default | Gelesen von (Backend) | God-Mode-Seite (A11 2.8) |
|---|---|---|---|---|---|---|
| 1 | `ENABLE_SIGNUP` | AUTHENTICATION | nein | `"1"` | `LIC/api/views/instance.py` (`enable_signup`, Lese-Default `"0"`), `AUTH/adapter/base.py` (Sign-up-Sperre `SIGNUP_DISABLED`) | Authentication |
| 2 | `ENABLE_EMAIL_PASSWORD` | AUTHENTICATION | nein | `"1"` | `instance.py` (`is_email_password_enabled`), `AUTH/provider/credentials/email.py` | Authentication |
| 3 | `ENABLE_MAGIC_LINK_LOGIN` | AUTHENTICATION | nein | `"0"` | `instance.py` (`is_magic_login_enabled`, Lese-Default `"1"`), `AUTH/provider/credentials/magic_code.py`, `AUTH/views/app/check.py`, `AUTH/views/space/check.py` | Authentication |
| 4 | `DISABLE_WORKSPACE_CREATION` | WORKSPACE_MANAGEMENT | nein | `"0"` | `instance.py` (`is_workspace_creation_disabled`), `apps/api/plane/app/views/workspace/base.py` | Workspaces |
| 5 | `IS_GOOGLE_ENABLED` | GOOGLE | nein | `"0"` | `instance.py` | Authentication/Google |
| 6 | `GOOGLE_CLIENT_ID` | GOOGLE | nein | – (Env) | `AUTH/provider/oauth/google.py` | Google |
| 7 | `GOOGLE_CLIENT_SECRET` | GOOGLE | **ja** | – | `AUTH/provider/oauth/google.py` | Google |
| 8 | `ENABLE_GOOGLE_SYNC` | GOOGLE | nein | `"0"` | `AUTH/adapter/base.py` `check_sync_enabled` (Profil-/Avatar-Sync bei Login) | Google |
| 9 | `IS_GITHUB_ENABLED` | GITHUB | nein | `"0"` | `instance.py` | GitHub |
| 10 | `GITHUB_CLIENT_ID` | GITHUB | nein | – | `AUTH/provider/oauth/github.py` | GitHub |
| 11 | `GITHUB_CLIENT_SECRET` | GITHUB | **ja** | – | `AUTH/provider/oauth/github.py` | GitHub |
| 12 | `GITHUB_ORGANIZATION_ID` | GITHUB | nein | – | `AUTH/provider/oauth/github.py` (Org-Mitgliedschaftsprüfung) | GitHub |
| 13 | `ENABLE_GITHUB_SYNC` | GITHUB | nein | `"0"` | `AUTH/adapter/base.py` | GitHub |
| 14 | `IS_GITLAB_ENABLED` | GITLAB | nein | `"0"` | `instance.py` | GitLab |
| 15 | `GITLAB_HOST` | GITLAB | nein | – | `AUTH/provider/oauth/gitlab.py` | GitLab |
| 16 | `GITLAB_CLIENT_ID` | GITLAB | nein | – | `AUTH/provider/oauth/gitlab.py` | GitLab |
| 17 | `GITLAB_CLIENT_SECRET` | GITLAB | **ja** | – | `AUTH/provider/oauth/gitlab.py` | GitLab |
| 18 | `ENABLE_GITLAB_SYNC` | GITLAB | nein | `"0"` | `AUTH/adapter/base.py` | GitLab |
| 19 | `IS_GITEA_ENABLED` | GITEA | nein | `"0"` | `instance.py` | Gitea |
| 20 | `GITEA_HOST` | GITEA | nein | – | `AUTH/provider/oauth/gitea.py` | Gitea |
| 21 | `GITEA_CLIENT_ID` | GITEA | nein | – | `AUTH/provider/oauth/gitea.py` | Gitea |
| 22 | `GITEA_CLIENT_SECRET` | GITEA | **ja** | – | `AUTH/provider/oauth/gitea.py` | Gitea |
| 23 | `ENABLE_GITEA_SYNC` | GITEA | nein | `"0"` | `AUTH/adapter/base.py` | Gitea |
| 24 | `ENABLE_SMTP` | SMTP | nein | `"0"` | **nur** von `DisableEmailFeatureEndpoint` geschrieben; kein Backend-Leser (SMTP gilt als konfiguriert, wenn `EMAIL_HOST` gesetzt ist) | Email |
| 25 | `EMAIL_HOST` | SMTP | nein | `""` | `instance.py` (`is_smtp_configured`), `LIC/utils/instance_value.py` `get_email_configuration`, Magic-Code-/Passwort-Views (App, Space) | Email |
| 26 | `EMAIL_HOST_USER` | SMTP | nein | `""` | `get_email_configuration`, `AUTH/views/space/password_management.py` | Email |
| 27 | `EMAIL_HOST_PASSWORD` | SMTP | **ja** | `""` | dito | Email |
| 28 | `EMAIL_PORT` | SMTP | nein | `"587"` | `get_email_configuration` | Email |
| 29 | `EMAIL_FROM` | SMTP | nein | `""` (Lese-Default `"Team Plane <team@mailer.plane.so>"`) | `get_email_configuration` | Email |
| 30 | `EMAIL_USE_TLS` | SMTP | nein | `"1"` | `get_email_configuration` | Email |
| 31 | `EMAIL_USE_SSL` | SMTP | nein | `"0"` | `get_email_configuration` | Email |
| 32 | `LLM_API_KEY` | AI | **ja** | – | `apps/api/plane/app/views/external/base.py`, `instance.py` (`has_llm_configured`) | AI |
| 33 | `LLM_PROVIDER` | AI | nein | `"openai"` | `apps/api/plane/app/views/external/base.py` | AI |
| 34 | `LLM_MODEL` | AI | nein | `"gpt-4o-mini"` | `apps/api/plane/app/views/external/base.py` | AI |
| 35 | `GPT_ENGINE` | AI | nein | `"gpt-3.5-turbo"` | **kein Leser** (Altlast) | – |
| 36 | `UNSPLASH_ACCESS_KEY` | UNSPLASH | **ja** | `""` | `apps/api/plane/app/views/external/base.py`, `instance.py` (`has_unsplash_configured`) | Images |

Zusätzlich **gelesen, aber nicht geseedet** (nur Env-Fallback, da nie in der DB): `SLACK_CLIENT_ID` (→ `config.slack_client_id`), `GITHUB_APP_NAME` (→ `config.github_app_name`) (`LIC/api/views/instance.py` Z. 52–109).

#### 2.7.5 Antwort `GET /api/instances/` (`LIC/api/views/instance.py` Z. 36–160)

| Objekt | Feld | Quelle |
|---|---|---|
| `instance` | alle `Instance`-Felder (2.7.3) + `workspaces_exist` (`Workspace.objects.count() >= 1`) | `InstanceSerializer` (`LIC/api/serializers/instance.py`; `primary_owner_details` wird mangels Attribut stets weggelassen) |
| `config` | `enable_signup` | `ENABLE_SIGNUP == "1"` |
| | `is_workspace_creation_disabled` | `DISABLE_WORKSPACE_CREATION == "1"` |
| | `is_google_enabled`, `is_github_enabled`, `is_gitlab_enabled`, `is_gitea_enabled` | jeweiliger `IS_*_ENABLED == "1"` |
| | `is_magic_login_enabled` | `ENABLE_MAGIC_LINK_LOGIN == "1"` |
| | `is_email_password_enabled` | `ENABLE_EMAIL_PASSWORD == "1"` |
| | `github_app_name` | `str(GITHUB_APP_NAME)` |
| | `slack_client_id` | `SLACK_CLIENT_ID` (oder `null`) |
| | `has_unsplash_configured` | `bool(UNSPLASH_ACCESS_KEY)` |
| | `has_llm_configured` | `bool(LLM_API_KEY)` |
| | `file_size_limit` | `float(Env FILE_SIZE_LIMIT, Default 5242880)` |
| | `is_smtp_configured` | `bool(EMAIL_HOST)` |
| | `admin_base_url`, `space_base_url`, `app_base_url` | `settings.ADMIN_BASE_URL`, `SPACE_BASE_URL`, `APP_BASE_URL` (ungültige URLs → `null`, `SET/common.py` Z. 444–453) |
| | `instance_changelog_url` | `settings.INSTANCE_CHANGELOG_URL` (Env, Default `""`) |
| | `is_self_managed` | `settings.IS_SELF_MANAGED` (= `True`, `SET/common.py` Z. 55) |

`data["is_activated"] = True` wird zwar gesetzt, gelangt aber **nicht** in die Antwort (Z. 47–48 ändern eine Kopie von `serializer.data`, Z. 118 setzt `data = {}`; `instance_data` wird neu aus `serializer.data` gebildet).

#### 2.7.6 Fehlercodes der Admin-Form-Flows (`AUTH/adapter/error.py`)

| Code | Name | Auslöser |
|---|---|---|
| 5000 | `INSTANCE_NOT_CONFIGURED` | Sign-in/Sign-up ohne `Instance` |
| 5021 | `PASSWORD_TOO_WEAK` | Sign-up: `is_password_strong` – zxcvbn-Score ≥ 3 für Anfangs- **oder** Endfenster des Passworts (je 128 Zeichen, `ZXCVBN_MAX_LENGTH`) (`AUTH/utils/password.py` Z. 13–15) |
| 5150 | `ADMIN_ALREADY_EXIST` | Sign-up, wenn `is_setup_done` oder **irgendein** `InstanceAdmin` existiert (auch im Lock erneut geprüft) |
| 5155 | `REQUIRED_ADMIN_EMAIL_PASSWORD_FIRST_NAME` | Sign-up ohne E-Mail/Passwort/Vorname |
| 5160 | `INVALID_ADMIN_EMAIL` | Sign-up/Sign-in: `validate_email` |
| 5165 | `INVALID_ADMIN_PASSWORD` | definiert, ungenutzt |
| 5170 | `REQUIRED_ADMIN_EMAIL_PASSWORD` | Sign-in ohne E-Mail/Passwort |
| 5175 | `ADMIN_AUTHENTICATION_FAILED` | Sign-in: falsches Passwort, Bot-User, kein `InstanceAdmin` |
| 5180 | `ADMIN_USER_ALREADY_EXIST` | Sign-up mit existierender E-Mail |
| 5185 | `ADMIN_USER_DOES_NOT_EXIST` | Sign-in mit unbekannter E-Mail |
| 5190 | `ADMIN_USER_DEACTIVATED` | Sign-in mit `is_active=False` |
| 5900 | `RATE_LIMIT_EXCEEDED` | `AuthenticationThrottle` (Redirect mit `next_path`-Unterstützung) |

Redirect-Format: `urljoin(admin_base, "?" + urlencode({"error_code": n, "error_message": "<NAME>", …payload}))` (`LIC/api/views/admin.py`). Die Anzeige-Texte liefert das Frontend (A11 2.11).

#### 2.7.7 Management-Commands, Start-Sequenz, Telemetrie

| Element | Verhalten | Quelle |
|---|---|---|
| Start-Sequenz API-Container | `wait_for_db` → `wait_for_migrations` → Maschinen-Signatur = SHA-256 über Hostname, MAC, `/proc/cpuinfo`, `free -h`, `df -h` → `register_instance <signature>` → `configure_instance` → `create_bucket` → `clear_cache` → `collectstatic` → gunicorn/uvicorn | `apps/api/bin/docker-entrypoint-api.sh` |
| `register_instance` | Version = Env `APP_VERSION` oder `package.json` `version` (Fallback `v0.1.0`); **neueste Version** über `GET https://api.github.com/repos/makeplane/plane/releases/latest` (10 s Timeout, Fallback aktuelle Version); ohne Instanz: `Instance(instance_name="Plane Community Edition", instance_id=secrets.token_hex(12), current_version, latest_version, last_checked_at=now, is_test=(IS_TEST=="1"), edition="PLANE_COMMUNITY")`; sonst Update dieser Felder; danach `push_instance_metrics.delay()`. Die Signatur wird nur auf Nicht-Leere geprüft, **nicht gespeichert**. | `LIC/management/commands/register_instance.py` |
| `configure_instance` | Pflicht-Env `SECRET_KEY` (sonst `CommandError`); Seed der 36 Keys (2.7.4) | `LIC/management/commands/configure_instance.py` |
| `push_instance_metrics` (Celery-Beat `push-instance-metrics`, Intervall Env `METRICS_PUSH_INTERVAL_MINUTES`, Default 360) | Nur wenn `Instance` existiert **und** `is_telemetry_enabled`. OTLP-Metrics-Export (Protokoll Env `OTLP_METRICS_PROTOCOL`, Default `grpc`; Endpoint Env `OTLP_ENDPOINT`, **Default `https://telemetry.plane.so`**). Resource: `service.name` (Env `SERVICE_NAME`, Default `plane-ce-api`), `instance_id`, `plane.instance.type="self-hosted"`. Gauges Instanz (Attribute `instance_id, instance_name, current_version, latest_version, edition, domain (aus WEB_URL), is_verified, is_setup_done`): `plane_instance_users_total` (ohne Bots), `plane_instance_workspaces_total`, `plane_instance_projects_total`, `plane_instance_issues_total`, `plane_instance_modules_total`, `plane_instance_cycles_total`, `plane_instance_cycle_issues_total`, `plane_instance_module_issues_total`, `plane_instance_pages_total` (ohne Bot-eigene private Pages). Gauges je Workspace (max. 1000, älteste zuerst; Attribute `workspace_id, workspace_slug, instance_id`): `plane_workspace_projects_total`, `plane_workspace_issues_total`, `plane_workspace_modules_total`, `plane_workspace_cycles_total`, `plane_workspace_members_total`, `plane_workspace_pages_total`. Flush-Timeout 30 s, Export-Intervall 20 s. | `LIC/bgtasks/telemetry_metrics.py`; `UT/otlp_endpoints.py`; `apps/api/plane/celery.py` Z. 28–59 |

#### 2.7.8 Verschlüsselung und reservierte Slugs

| Element | Verhalten | Quelle |
|---|---|---|
| `derive_key(secret_key)` | `PBKDF2-HMAC-SHA256(secret_key, salt=b"salt", 100000 Iterationen)` → 32 Byte → URL-safe Base64 = Fernet-Schlüssel | `LIC/utils/encryption.py` |
| `encrypt_data(data)` | leer → `""`; sonst Fernet-Token (AES-128-CBC + HMAC-SHA256, Base64) als String; Fehler → `""` (geloggt) | dito |
| `decrypt_data(token)` | leer → `""`; Fehler (z. B. geänderter `SECRET_KEY`) → `""` (geloggt) | dito |
| `RESTRICTED_WORKSPACE_SLUGS` (vollständig) | `404, accounts, api, create-workspace, god-mode, installations, invitations, onboarding, profile, spaces, workspace-invitations, password, flags, monitor, monitoring, ingest, plane-pro, plane-ultimate, enterprise, plane-enterprise, disco, silo, chat, calendar, drive, channels, upgrade, billing, sign-in, sign-up, signin, signup, config, live, admin, m, import, importers, integrations, integration, configuration, initiatives, initiative, config, workflow, workflows, epics, epic, story, mobile, dashboard, desktop, onload, real-time, one, pages, mobile, business, pro, settings, monitor, license, licenses, instances, instance` (Duplikate `config`, `mobile`, `monitor` im Original) | `UT/constants.py` Z. 5–71 |

### 2.8 `plane.web`, `plane.analytics`, Schema-Routen

| ID | Methode | Pfad | View | Antwort | Quelle |
|---|---|---|---|---|---|
| W-01 | GET | `/` | `health_check` (Funktion) | 200 `{"status": "OK"}` (JSON) | `apps/api/plane/web/views.py`, `apps/api/plane/web/urls.py` |
| W-02 | GET | `/robots.txt` | `robots_txt` | 200 `text/plain` `User-agent: *\nDisallow: /` | dito |
| W-03…05 | GET | `/api/schema/`, `/api/schema/swagger-ui/`, `/api/schema/redoc/` | drf-spectacular (nur `ENABLE_DRF_SPECTACULAR=1`) | OpenAPI 3 bzw. HTML-Viewer (Swagger UI/Redoc laden Assets standardmäßig von CDNs) | `apps/api/plane/urls.py` Z. 27–40 |
| – | – | – | `plane.analytics` | keine Routen, keine Modelle, keine Tasks | `apps/api/plane/analytics/{__init__,apps}.py` |

Zusätzlich: Django `handler404 = "plane.app.views.error_404.custom_404_view"` für alle unbekannten Pfade (A03).

### 2.9 Abdeckungsvergleich: v1 ↔ interne App-API ↔ Commercial-API

„App“ = interne Session-API (`migration/analysis/03-…`, `04-…`); „v1 CE“ = diese Analyse; „Commercial“ = `migration/features/21-paid-api-referenz-developer-docs.md` (Doc 21). ✓ = vorhanden, ◐ = teilweise, – = fehlt.

| Ressource | App | v1 CE | Commercial | Lücke v1 CE gegenüber App (für Ziel-v1 relevant) |
|---|---|---|---|---|
| Aktueller User | ✓ (Profil, Settings, Onboarding, Tokens) | ◐ nur `GET users/me` | ✓ (`AR/user/`) | kein Profil-Update, keine Avatar-Zuordnung |
| Workspace | ✓ CRUD, Slug-Check, Themes | – | ◐ Workspace-Features (EE) | kein Lesen/Ändern des Workspace |
| Workspace-Mitglieder | ✓ Liste, Rollenänderung, Entfernen, Verlassen | ◐ nur Lesen (`members`, `members-lite`) | ◐ + Member-Remove (EE) | keine Rollenpflege |
| Workspace-Einladungen | ✓ inkl. E-Mail-Versand, Token, Annahme | ◐ CRUD **ohne** Token/E-Mail | ✓ | Einladungen über v1 nicht annehmbar |
| Projekte | ✓ inkl. Favoriten, Join, Identifier, Netzwerk | ✓ CRUD, lite, Archiv, Summary | ✓ + Features/Labels/Templates (EE) | `network`/`logo_props` nicht schreibbar |
| Projekt-Mitglieder | ✓ inkl. Join-Requests, Präferenzen | ✓ (Rolle, Hinzufügen, Deaktivieren) | ✓ | – |
| Projekt-Einladungen | ✓ | – | – | – |
| States | ✓ | ✓ | ✓ | – |
| Labels | ✓ (+ Bulk) | ✓ | ✓ | kein Bulk |
| Estimates/Points | ✓ | ◐ Code ohne Route | ✓ | Route einbinden |
| Work Items | ✓ inkl. gruppierter/gefilterter Listen, Bulk, Archiv, Entwürfe, Sub-Issues, Subscriber, Reaktionen, Votes, Versionen, Kopieren | ◐ CRUD, Lookup per Identifier/External-ID, Suche | ✓ + Types/Properties, Epics, Worklogs, Advanced Search, PQL (EE) | kein Archiv/Unarchiv, kein Bulk, keine Filter/PQL, keine Sub-Issue-/Subscriber-/Reaktions-Endpunkte |
| Links | ✓ | ✓ | ✓ | – |
| Kommentare | ✓ inkl. Reaktionen, Antworten (`parent`) | ✓ CRUD | ✓ | keine Reaktionen |
| Aktivitäten/Historie | ✓ (kombiniert mit Kommentaren) | ✓ (ohne Kommentar-/Vote-/Reaction-/Draft-Einträge) | ✓ | – |
| Anhänge | ✓ (v2) | ✓ (Presigned-Flow) | ✓ | – |
| Relationen | ✓ inkl. Entfernen | ◐ Liste/Anlage | ✓ (+ Remove) | kein Entfernen |
| Cycles | ✓ inkl. Favoriten, Analytics, Fortschritt, User-Properties, Datumsprüfung | ✓ CRUD, lite, Issues, Transfer, Archiv | ✓ | keine Analytics/Fortschritt |
| Modules | ✓ inkl. Links, Favoriten, Analytics | ✓ CRUD, lite, Issues, Archiv | ✓ | keine Module-Links |
| Gespeicherte Views | ✓ | – | – (Doc 21 führt keine Views-Ressource) | – |
| Pages | ✓ | – | ✓ (EE) | – |
| Intake | ✓ | ✓ | ✓ (+ deprecated `inbox-issues`) | – |
| Notifications, Webhooks, API-Tokens, Analytics, Export, Favoriten, Recents, Quick Links, Home | ✓ | – | – | – |
| Stickies | ✓ | ✓ | ✓ | – |
| Assets | ✓ | ✓ (User-, Server-, Generic-Assets) | ✓ | keine Bindung Generic-Asset → Work Item |
| Suche | ✓ global/Entitäten | ◐ nur Work Items | ✓ + Advanced Search (EE) | – |
| Veröffentlichung (Deploy Boards) | ✓ | – | – | – |
| Customers, Initiatives, Teamspaces, Milestones, IdP Group Sync, Work-Item-Pages | – | – | ✓ (EE) | vollständig neu (Doc 21) |

---

## 3. Verhalten/Logik/Abläufe im Detail (inkl. Edge-Cases)

### 3.1 Lebenszyklus eines v1-Requests

1. Django-Middleware-Kette (`SET/common.py` Z. 122–136): CORS → Security → WhiteNoise → Session (Cookie irrelevant) → Common → CSRF (DRF-Views sind `csrf_exempt`) → Auth → `crum` (merkt Request) → GZip → Body-Größe (413) → `APITokenLogMiddleware` (liest `request.body` vorab, loggt nach der Antwort asynchron) → `RequestLoggerMiddleware`.
2. DRF `APIView.initial` (über `TimezoneMixin.initial` → `BaseAPIView.initial`): Content-Negotiation → **Authentifizierung** (`APIKeyAuthentication`, inkl. `last_used`-Write) → **Permissions** → **Throttle** (`ApiKeyRateThrottle`, Header-Werte in `request.META`) → Aktivierung der Benutzerzeitzone → **Body-Typ-Prüfung** (Objekt/Array) (`V1V/base.py` Z. 59–62). Die Body-Prüfung kommt also **nach** Permission und Throttle.
3. Handler; Exceptions → `handle_exception` (2.1.4).
4. `finalize_response` kopiert `X-RateLimit-Remaining`/`X-RateLimit-Reset` in die Antwort (auch bei Fehlerantworten nach erfolgreichem Throttle-Check).

### 3.2 Projekt anlegen (V-PRJ-02, `V1V/project.py` Z. 224–354)

1. `Workspace.objects.get(slug)` (fehlt → 404 „Workspace does not exist“).
2. `ProjectCreateSerializer(data={**request.data}, context={"workspace_id"})`; `is_valid()` (Fehler → 400).
3. `transaction.atomic()`:
   1. `serializer.save()` → `create()`: Identifier normalisieren/prüfen (2.3), `logo_props` zufällig, `Project.objects.create(**validated_data, workspace_id)`; `Project.save()` setzt `identifier = strip().upper()` und – wenn kein `timezone` übergeben – die **Workspace-Zeitzone** (`M/project.py` Z. 193–201).
   2. `ProjectMember(project, member=request.user, role=20)`.
   3. Wenn `project_lead_id` gesetzt und ≠ Ersteller: `ProjectMember(member=project_lead, role=20)`.
   4. `State.bulk_create` der 6 `DEFAULT_STATES` (`M/state.py` Z. 24–62): Backlog `#60646C` 15000 `backlog` **default**; Todo `#60646C` 25000 `unstarted`; In Progress `#F59E0B` 35000 `started`; Done `#46A758` 45000 `completed`; Cancelled `#9AA4BC` 55000 `cancelled`; Triage `#4E5355` 65000 `triage` – mit `created_by = request.user` (Bulk umgeht `save()`, daher `slug` leer).
   5. Neu laden über annotiertes `get_queryset()`.
   6. `transaction.on_commit(model_activity.delay(model_name="project", model_id, requested_data=request.data, current_instance=None, actor_id, slug, origin=base_host(is_app=True)), robust=True)` → Webhook „project created“ nur nach erfolgreichem Commit; Dispatch-Fehler werden geloggt, nicht gemeldet.
4. Fehlerzuordnung: `IntegrityError` mit „already exists“ (Name/Identifier-Unique-Constraint) → 409 `{"name": …}`; andere `IntegrityError` → 500 `{"error": "An unexpected error occurred"}`; jede DRF-`ValidationError` aus `save()` → 409 `{"identifier": …}`; sonstige Exceptions → 500.
5. `ProjectMember.save()` legt bei jeder neuen Mitgliedschaft eine `ProjectUserProperty` an (`sort_order` = kleinster vorhandener Wert des Users im Workspace − 10000, sonst 65535) (`M/project.py` Z. 276–291) – gilt für beide APIs.
6. Unterschiede zur App-API (`apps/api/plane/app/views/project/base.py` Z. 258–310): kein `ProjectIdentifier`-Datensatz (App: `apps/api/plane/app/serializers/project.py` Z. 95), `network` nicht schreibbar (Default Public = 2), keine Transaktion/`on_commit` in der App-Variante, App liefert bei Konflikten die Exceptions an die generische Fehlerbehandlung (A03), v1 mappt sie auf 409.
7. Sortierung `sort_order` in V-PRJ-01 nutzt `ProjectMember.sort_order` (Default 65535), **nicht** die Sidebar-Reihenfolge aus `ProjectUserProperty.sort_order`.

### 3.3 Projekt ändern (V-PRJ-05, Z. 546–610)

1. `Workspace.get(slug)` und `Project.get(pk)` (ohne Workspace-Filter; die Permission hat die Mitgliedschaft im URL-Workspace bereits geprüft); `current_instance` = JSON des `ProjectSerializer`.
2. `intake_view` = Body-Wert oder bisheriger Wert (wird immer in die Daten gemischt).
3. Archiviert → 400.
4. `ProjectUpdateSerializer(partial=True)`; nach `save()`: wenn `serializer.data["intake_view"]` wahr und kein `Intake(project, is_default=True)` existiert → `Intake.objects.create(name=f"{project.name} Intake", project, is_default=True)` (Workspace via `ProjectBaseModel.save`).
5. Zeitzonenwechsel: `Project.save()` verschiebt offene Intake-Snoozes auf Mitternacht der neuen Zeitzone (atomar, `M/project.py` Z. 150–227).
6. `model_activity("project", updated, requested_data=request.data, current_instance)`.

### 3.4 Work-Item-Liste (V-WI-01, `V1V/issue.py` Z. 317–438)

1. `pql`/`filters` gesetzt (nicht leer) → 400 (Bezahl-Feature PF-52).
2. `external_id` **und** `external_source` → `Issue.objects.get(…)` (**Default-Manager**, also auch archivierte/Entwürfe) → Einzelobjekt.
3. `order_by` per Allowlist bereinigt, dann:
   - `priority` / `-priority`: Annotation `priority_order = CASE priority WHEN 'urgent' THEN '0' … 'none' THEN '4'` (bzw. umgekehrte Liste), `ORDER BY priority_order` (Werte als String, einstellig ⇒ korrekt); **kein** Tiebreaker.
   - `state__name`, `state__group` (± ): Annotation `state_order` nach Gruppenreihenfolge `backlog, unstarted, started, completed, cancelled` (bei `-` umgekehrt), sonstige Gruppen ans Ende; **auch `state__name` sortiert nach Gruppe**, nicht nach Name.
   - `labels__name`, `assignees__first_name` (± ): `Max(<feld>)` als `max_values`, auf-/absteigend.
   - sonst `ORDER BY <order_by>` (z. B. `-created_at`).
4. Pagination mit `total_count_queryset = Issue.issue_objects(project)`.
5. Ausgabe `IssueSerializer(many=True, fields, expand)`; je Issue zwei Zusatzabfragen (Assignees, Labels) in `to_representation` (N+1, Performance-Hinweis 5).

### 3.5 Work Item anlegen/ändern (V-WI-02/04)

**Anlegen:**
1. `Project.objects.get(pk=project_id)`.
2. `IssueSerializer(data, context={project_id, workspace_id, default_assignee_id})`, `is_valid()` (Prüfungen 2.3 in dieser Reihenfolge: Datumsreihenfolge → HTML-Parse → HTML-Sanitizing → Binary → Assignees → Labels → State → Parent → Estimate-Point).
3. Externe-ID-Konflikt (beide Felder gesetzt und Kombination im Projekt vorhanden, **inkl.** gelöschter? – nein, Default-Manager ohne gelöschte) → 409.
4. `serializer.save()` → `Issue.objects.create(**validated_data, project_id, type=<Default-Typ>)`; `Issue.save()` vergibt `sequence_id`, Default-State, `sort_order` und `completed_at`-Logik (A04 3.x); Assignees bzw. Default-Assignee, Labels (`IntegrityError` still ignoriert).
5. Nachträglich: `issue.created_at = request.data.get("created_at", now)`, `issue.created_by_id = request.data.get("created_by", request.user.id)`, `save(update_fields=["created_at", "created_by"])` (**Importer-Funktion**: Zeitstempel/Ersteller frei setzbar, ohne Mitgliedschaftsprüfung des angegebenen Users; ungültige UUID → `ValidationError`/`IntegrityError` → 400).
6. `issue_activity.delay(type="issue.activity.created", requested_data=json(request.data), actor_id=request.user, issue_id, project_id, current_instance=None, epoch, notification=True, origin)`; `model_activity.delay("issue", created)` → Webhook.
7. Antwort: `serializer.data` aus Schritt 4 (enthält noch das ursprüngliche `created_at`/`created_by`).

**Ändern:** `Issue.objects.get` (auch archivierte/Entwürfe), `current_instance` = JSON vorher, `IssueSerializer(partial=True)`; Externe-ID-Konflikt nur bei geänderter `external_id`; `save()` (Assignees/Labels **ersetzen**, wenn im Body); `writable_data` entfernt read-only Keys aus Activity-/Webhook-Payload (`UT/serializers.py`); `issue_activity("issue.activity.updated", notification=True)`; `model_activity("issue", updated)`.

### 3.6 Löschsemantik

Alle `delete()`-Aufrufe sind Soft-Deletes (`deleted_at`, A02a). Webhook-relevante Unterschiede: Projekt-Löschung ruft `webhook_activity` direkt; Work-Item-, Kommentar-, Cycle-, Modul-, Label-, State-, Link-Löschungen rufen **kein** `model_activity`/`webhook_activity` (nur `issue_activity` bzw. nichts). Intake-Löschung entfernt bei nicht angenommenen Einträgen auch das Work Item.

### 3.7 Anhang-Upload (V-ATT-02 → S3 → V-ATT-04)

1. **Anfordern:** `POST {WI}/attachments/` mit `{name, type, size}` → Prüfungen (2.2.9) → `FileAsset(attributes={name, type, size_limit}, asset=<key>, size=size_limit, workspace, created_by, issue, project, entity_type=ISSUE_ATTACHMENT, external_id, external_source, is_uploaded=False)` → `upload_data` (Presigned POST über **Browser-Endpoint** `S3Storage(request)`).
2. **Hochladen:** Client `POST upload_data.url` mit `multipart/form-data` (`fields` + `file`); S3 erzwingt `content-length-range [1, size_limit]` und `Content-Type`.
3. **Bestätigen:** `PATCH {WI}/attachments/{asset_id}/` → beim ersten Mal Activity `attachment.activity.created` (Benachrichtigung) und `is_uploaded=True`; Metadaten (`storage_metadata` = `{ContentType, ContentLength, LastModified (ISO), ETag, Metadata}` aus S3 `HEAD`, `SET/storage.py` Z. 153–169) asynchron (`get_asset_object_metadata`).
4. **Lesen:** `GET {WI}/attachments/` listet nur hochgeladene; `GET {WI}/attachments/{id}/` → 302 auf kurzlebige Download-URL (`Content-Disposition: attachment`).
5. Nicht bestätigte Uploads bleiben als `is_uploaded=False` liegen und werden vom Beat-Task `delete_unuploaded_file_asset` nach `UNUPLOADED_ASSET_DELETE_DAYS` (Default 7) Tagen (soft-)gelöscht (`apps/api/plane/bgtasks/file_asset_task.py`; `apps/api/plane/celery.py` Z. 74).

### 3.8 Relationen (V-REL-01/02)

| Request-`relation_type` | gespeicherter Typ (`get_actual_relation`) | gespeichert als (`issue` → `related_issue`) | Antwort-Serializer |
|---|---|---|---|
| `blocked_by` | `blocked_by` | URL-Issue → Ziel | `IssueRelationSerializer` (Daten des Ziels) |
| `blocking` | `blocked_by` | Ziel → URL-Issue (Rückwärts) | `RelatedIssueSerializer` (Daten des Ziels) |
| `start_before` | `start_before` | URL → Ziel | Vorwärts |
| `start_after` | `start_before` | Ziel → URL | Rückwärts |
| `finish_before` | `finish_before` | URL → Ziel | Vorwärts |
| `finish_after` | `finish_before` | Ziel → URL | Rückwärts |
| `duplicate` | `duplicate` | URL → Ziel | Vorwärts |
| `relates_to` | `relates_to` | URL → Ziel | Vorwärts |

Liste (GET) für URL-Issue U über alle Zeilen mit `issue=U` oder `related_issue=U` im Workspace:

| gespeicherter Typ | U ist `issue` → Liste | U ist `related_issue` → Liste |
|---|---|---|
| `blocked_by` | `blocked_by` ← related | `blocking` ← issue |
| `start_before` | `start_before` ← related | `start_after` ← issue |
| `finish_before` | `finish_before` ← related | `finish_after` ← issue |
| `duplicate` | `duplicate` ← related (dedupliziert) | `duplicate` ← issue (dedupliziert) |
| `relates_to` | `relates_to` ← related (dedupliziert) | `relates_to` ← issue (dedupliziert) |
| `implemented_by` (nur App/EE) | – | – |

Die Liste prüft weder `deleted_at` des Partner-Issues noch dessen Sichtbarkeit (nur Soft-Delete-Manager der Relation). Es gibt keinen Selbstbezugs-Schutz (U kann mit sich selbst in Relation gesetzt werden, sofern in `issues`).

### 3.9 Cycles

- **Zeitlogik:** Alle Vergleiche gegen `timezone.now()` (UTC-aware). Create/Update konvertiert `start_date`/`end_date` (nur wenn **beide** gesetzt) via `convert_to_utc(date=str(<datum>.date()), project_id, is_start_date)` – d. h. die Uhrzeit des Inputs wird verworfen, Start = Tagesbeginn, Ende = Tagesende in der **Projektzeitzone** (A04). Wird nur eines der Daten im PATCH gesendet, erfolgt **keine** Konvertierung und keine Paarprüfung.
- **Status-Ableitung** (`cycle_view`): siehe V-CYC-01. Ein Cycle ist „abgeschlossen“, wenn `end_date < now`.
- **Zählannotationen** (aktive Liste/Detail): `total_issues` = `CycleIssue` (nicht gelöscht) mit Issue nicht archiviert und kein Entwurf; `completed/cancelled/started/unstarted/backlog_issues` analog je State-Gruppe; Triage-Issues zählen in `total_issues`, aber in keiner Gruppe.
- **Archivieren:** nur `end_date` gesetzt und `< now`; Unarchivieren ohne Prüfung.
- **Transfer** (`UT/cycle_transfer_issues.py` Z. 35–478): Ziel-Cycle laden (fehlt → 500), abgeschlossen → Fehler; Quell-Cycle mit Zählungen laden (fehlt → „Source cycle not found“); Schätzungs-Typ des Projekts ermitteln; Verteilungen (Labels, Assignees, Burn-down via `burndown_plot`, ggf. Schätzpunkte) berechnen und als `progress_snapshot = {total_issues, completed_issues, cancelled_issues, started_issues, unstarted_issues, backlog_issues, distribution: {labels, assignees, completion_chart}, estimate_distribution: {} | {labels, assignees, completion_chart}}` am **Quell**-Cycle speichern; dann alle `CycleIssue` des Quell-Cycles mit Issue nicht archiviert, kein Entwurf, Gruppe ∈ {backlog, unstarted, started} auf den Ziel-Cycle umhängen (`bulk_update`); `issue_activity("cycle.activity.created", current_instance={updated_cycle_issues: [{old_cycle_id, new_cycle_id, issue_id}], created_cycle_issues: []})`. Triage-Issues werden **nicht** übertragen.

### 3.10 Work Items einem Cycle zuordnen (V-CYC-08, `V1V/cycle.py` Z. 957–1064)

1. `issues` leer → 400 `MISSING_WORK_ITEMS`; Cycle laden; abgeschlossen → 400 `CYCLE_COMPLETED` (archivierte Cycles werden nicht geprüft).
2. `cycle_issues` = bestehende `CycleIssue` dieser Issues in **anderen** Cycles desselben Projekts → werden auf diesen Cycle **verschoben** (`bulk_update(cycle_id)`) – ein Work Item gehört also höchstens zu einem Cycle.
3. Übrige IDs, gefiltert auf `Issue.issue_objects` des Projekts → `bulk_create(ignore_conflicts=True)` (bereits im Cycle → ignoriert).
4. Activity `cycle.activity.created` mit `requested_data={"cycles_list": issues}`, `current_instance={updated_cycle_issues, created_cycle_issues (Django-Serializer-JSON)}`, `notification=True`.
5. Antwort: **alle** `CycleIssue` des Cycles (nicht nur die neuen).

### 3.11 Module

- **Anlegen:** `members` werden auf `ProjectMember`-Zeilen des Projekts (auch inaktive) reduziert; `lead` ungeprüft; Name eindeutig je Projekt (case-sensitiv, inkl. archivierter Module).
- **Work Items zuordnen (V-MOD-08):** Ziel-Issues = `Issue.objects` (auch archivierte/Entwürfe) des Projekts. Die Verschiebelogik ist fehlerhaft: Der Vergleich `str(module_issue.issue_id) in issues` prüft einen String gegen eine `ValuesListQuerySet` aus UUIDs (immer falsch), zudem wird nicht pro Issue gefiltert (`V1V/module.py` Z. 731–760). Ergebnis: Es wird **immer** ein neuer `ModuleIssue` angelegt (`ignore_conflicts=True`), ein Work Item kann also in **mehreren Modulen** sein (entspricht dem fachlichen Modell der App-API, A04), es wird nie „verschoben“, `updated_module_issues` ist stets leer. Activity `module.activity.created` mit `requested_data={"modules_list": str(<QuerySet>)}` (String-Repräsentation!).
- **Archivieren:** nur `status ∈ {completed, cancelled}`.
- **Löschen:** Soft-Delete des Moduls und aller `ModuleIssue` (`ModuleIssue.objects.filter(module=pk, project_id).delete()`).

### 3.12 Intake über v1 (V-INT-*)

| Rolle (PM) | Anlegen | Issue-Felder ändern | Intake-Status ändern | Löschen (nicht angenommen) |
|---|---|---|---|---|
| Gast (5) | ✓ | nur eigene Einträge (`created_by`), nur `name`, `description_html`, `description_json` | – (Daten ignoriert) | nur als Issue-Ersteller |
| Member (15) | ✓ | ✓ alle `IssueSerializer`-Felder | **– (Code `role > 15`, Kommentar sagt „admins and members“)** | nur als Issue-Ersteller |
| Admin (20) | ✓ | ✓ | ✓ `status, snoozed_till, duplicate_to, source, source_email` | ✓ |

Statuswerte (`M/intake.py` `IntakeIssueStatus`): `-2` PENDING, `-1` REJECTED, `0` SNOOZED, `1` ACCEPTED, `2` DUPLICATE. Annahme eines Issues im Triage-State verlangt einen Default-State und verschiebt das Issue dorthin. `snoozed_till` wird auf Tagesbeginn in der Projektzeitzone normalisiert. Abgelaufene Snoozes (`snoozed_till < now`) sind in Liste **und** Detail unsichtbar (404), bis der Beat-Task `unsnooze_expired_intake_issues` sie zurücksetzt (Test `apps/api/plane/tests/unit/bg_tasks/test_unsnooze_expired_intake_issues.py`; A04). Ohne `ProjectMember`-Zeile des Aufrufers → `ProjectMember.DoesNotExist` → 404 (durch Permission praktisch ausgeschlossen).

### 3.13 Mitglieder und Einladungen

- `GET {W}/members/` und `GET {P}/members/` liefern auch **deaktivierte** Mitglieder ohne Kennzeichnung (nur die Lite-Varianten liefern `is_active`).
- Projektmitglied hinzufügen: nur aktive WS-Mitglieder; bereits (auch inaktiv) vorhandene Mitgliedschaft → 400 „The payload is not valid“ (Unique-Constraint). Da `ProjectMemberSerializer` `is_active` nicht enthält, kann ein deaktiviertes Projektmitglied über v1 **nicht** reaktiviert werden.
- Entfernen = `is_active=False`; Zuweisungen/Abos bleiben.
- Einladungen: reine Datensätze (2.2.15); Duplikatprüfung pro Workspace über **alle** (nicht gelöschten) Einladungen dieser E-Mail, unabhängig vom Status.

### 3.14 Stickies

Nur eigene Stickies (`owner`). `query` sucht in `description_stripped` (wird vom Model aus `description_html` abgeleitet, A02). Kein Rate-Limit (ViewSet).

### 3.15 Assets (v1)

- **User-Assets** (Avatar/Cover): Upload-Ticket → Upload → PATCH (nur `is_uploaded`, `attributes`). Die Verknüpfung mit dem Profil (`User.avatar_asset`) erfolgt in CE nur über die App-API (A03); v1 kann das Profilbild also **nicht** setzen, nur Assets anlegen/löschen. DELETE entfernt eine bestehende Verknüpfung.
- **Server-Varianten** (`…/server/`): gedacht als identischer Ablauf mit Presigned-URL gegen die interne S3-Adresse (`AWS_S3_ENDPOINT_URL`, ohne Request-Host) für Clients im selben Netz (z. B. Integrationsdienste); **in v1.4.2 defekt** (POST → 500, siehe V-AST-04), PATCH/DELETE funktionieren.
- **Generic Assets:** werkzeugartiger Upload in einen Workspace (z. B. für Importer), Typ `ISSUE_ATTACHMENT` ohne Issue; Download-URL per GET; keine Bindung, keine Activity. **POST und GET sind in v1.4.2 wegen `is_server` defekt** (V-AST-07/08).

### 3.16 Seiteneffekt-Matrix v1 (Background-Tasks)

| Endpunkt | `issue_activity` (Typ, `notification`) | `model_activity`/`webhook_activity` (Webhook-Event) | weitere Tasks |
|---|---|---|---|
| V-PRJ-02 | – | `project` created (on_commit) | – |
| V-PRJ-05 | – | `project` updated | – |
| V-PRJ-06 | – | `webhook_activity(project, deleted)` | – |
| V-WI-02 | `issue.activity.created` (ja) | `issue` created | – |
| V-WI-04 | `issue.activity.updated` (ja) | `issue` updated | – |
| V-WI-05 | `issue.activity.deleted` (nein) | – | – |
| V-LNK-02 | `link.activity.created` | – | `crawl_work_item_link_title` |
| V-LNK-04 | `link.activity.updated` | – | Crawl bei URL-Änderung |
| V-LNK-05 | `link.activity.deleted` | – | – |
| V-CMT-02 | `comment.activity.created` | `issue_comment` created | – |
| V-CMT-04 | `comment.activity.updated` | `issue_comment` updated | – |
| V-CMT-05 | `comment.activity.deleted` | – | – |
| V-ATT-04 | `attachment.activity.created` (ja) | – | `get_asset_object_metadata` |
| V-ATT-05 | `attachment.activity.deleted` (ja) | – | `get_asset_object_metadata` |
| V-REL-02 | `issue_relation.activity.created` (ja) | – | – |
| V-CYC-02/05 | – | `cycle` created/updated | – |
| V-CYC-06 | `cycle.activity.deleted` | – | – |
| V-CYC-08 | `cycle.activity.created` (ja) | – | – |
| V-CYC-10 | `cycle.activity.deleted` | – | – |
| V-CYC-11 | `cycle.activity.created` (ja) | – | Progress-Snapshot (synchron) |
| V-MOD-02/05 | – | `module` created/updated | – |
| V-MOD-06 | `module.activity.deleted` | – | – |
| V-MOD-08 | `module.activity.created` | – | – |
| V-MOD-09 | `module.activity.deleted` | – | – |
| V-INT-02 | `issue.activity.created` (nein, `intake=<id>`) | – | – |
| V-INT-04 | `issue.activity.updated` (`intake`), `intake.activity.created` (nein) | – | – |
| V-AST-02/05/09 | – | – | `get_asset_object_metadata` |
| alle mit `X-Api-Key` | – | – | `process_logs` (`APIActivityLog`) |

Die Webhook-Payloads werden aus den **v1-Serializern** gebaut (`apps/api/plane/bgtasks/webhook_task.py` `SERIALIZER_MAPPER`: `project` → `ProjectSerializer`, `issue` → `IssueExpandSerializer`, `cycle` → `CycleSerializer`, `module` → `ModuleSerializer`, `cycle_issue` → `CycleIssueSerializer`, `module_issue` → `ModuleIssueSerializer`, `issue_comment` → `IssueCommentSerializer`, `user` → `UserLiteSerializer`, `intake_issue` → `IntakeIssueSerializer`). Das Attribut `webhook_event` an den v1-Views wird **nirgends** gelesen.

### 3.17 Space: Board-Auflösung, Issue-Liste, Filter, Gruppierung

1. Anchor-Mixin (2.6.1) → View lädt Board.
2. `issue_filters(request.query_params, "GET")` (`UT/issue_filters.py` Z. 428–465) mit den Schlüsseln: `state, state_group, estimate_point, priority, parent, labels, assignees, mentions, created_by, logged_by, name, created_at, updated_at, start_date, target_date, completed_at, type, project, cycle, module, intake_status, inbox_status, sub_issue, subscriber, start_target_date` (Semantik der einzelnen Filter: A04 2.18). Alle Filter sind **anonym** nutzbar; `project` kann den Board-Projektfilter nur weiter einschränken.
3. `order_issue_queryset` (Allowlist, Priorität/State mit Tiebreaker `-created_at`) (`UT/order_queryset.py` Z. 159ff.).
4. `issue_queryset_grouper` annotiert `assignee_ids`, `label_ids`, `module_ids` (ArrayAgg, ohne gelöschte Zuordnungen; bei Gruppierung nach M2M zusätzlicher Filter auf nicht gelöschte Zuordnungen) (`SP/utils/grouper.py` Z. 21–66).
5. Gruppenwerte (`issue_group_values`): `state_id` → nicht-Triage-States des Projekts; `labels__id` → Labels + `"None"`; `assignees__id` → aktive PM; `issue_module__module_id` → Module + `"None"`; `cycle_id` → Cycles + `"None"`; `project_id` → Board-Projekt; `priority` → `low, medium, high, urgent, none`; `state__group` → `backlog, unstarted, started, completed, cancelled`; `target_date`/`start_date`/`created_by` → **Fehler** (kein Queryset übergeben).
6. `issue_on_results` → `.values(...)` mit `vote_items`/`reaction_items` (ArrayAgg von JSON-Objekten, nur nicht gelöschte; `avatar_url` = `/api/assets/v2/static/{avatar_asset}/` oder `avatar`). Bei Gruppierung nach M2M wird statt des zugehörigen `*_ids`-Feldes das Gruppenfeld ausgegeben (`labels__id` statt `label_ids`, `assignees__id` statt `assignee_ids`, `issue_module__module_id` statt `module_ids`).
7. Pagination (gruppiert/subgruppiert, A04 2.17).

### 3.18 Space: Kommentare, Reaktionen, Votes

| Aktion | Voraussetzung Board | Voraussetzung Objekt | Auth | Besonderheit |
|---|---|---|---|---|
| Kommentare lesen | `is_comments_enabled` | `access="EXTERNAL"`, Board-Projekt, URL-Issue | anonym | `is_member` = Aufrufer aktives PM |
| Kommentar anlegen | dito | Issue sichtbar im Board (`issue_objects`) | angemeldet | nur Inhalt übernommen; `access` fest `EXTERNAL` |
| Kommentar ändern/löschen | dito | eigener EXTERNAL-Kommentar im Board-Projekt **und** URL-Issue | angemeldet | 404 sonst |
| Issue-Reaktion anlegen | `is_reactions_enabled` | Issue sichtbar | angemeldet | Duplikat → 400 |
| Issue-Reaktion löschen | dito | eigene Reaktion mit `reaction_code` | angemeldet | |
| Kommentar-Reaktion anlegen/lesen/löschen | `is_reactions_enabled` | EXTERNAL-Kommentar des Board-Projekts | angemeldet (auch Lesen) | |
| Vote setzen | `is_votes_enabled` | Issue sichtbar | angemeldet | ein Vote je User/Issue; Wert überschreibbar |
| Vote löschen | **keine** Prüfung | eigener Vote | angemeldet | |

Nicht-Projektmitglieder werden bei jeder schreibenden Interaktion als `ProjectPublicMember` erfasst. Reaktionscodes werden nicht validiert (beliebiger Text; das Frontend sendet Dezimal-Codepoints, A11 B19).

### 3.19 Space: öffentliche Intake-Einreichung

Nur wenn `DeployBoard.intake` gesetzt ist; die URL-`intake_id` muss beim **Anlegen** dem Board-Intake entsprechen. Erzeugtes Issue: Triage-State, `priority` Default **`low`** (abweichend von v1/App `none`), `created_by` = angemeldeter User (crum), `IntakeIssue.status = -2`. Lesen/Detail ist für **jeden** angemeldeten User möglich und zeigt alle Einreichungen des Intakes (Datenschutz-Risiko, 6). Das Frontend nutzt diese Endpunkte in CE nicht (A11 2.19); fachlich sind sie die Basis der Bezahl-Funktion „Intake Forms“ (PF-36).

### 3.20 Space: Assets

Upload nur für Kommentarbilder (`COMMENT_DESCRIPTION`) bei aktivierten Kommentaren; Binden an eigenen Kommentar per Bulk-Endpunkt nach dem Anlegen des Kommentars (Ablauf im Frontend: Upload mit `entity_identifier=""` → Kommentar anlegen → Bulk-Bind, A11 B26–B29). PATCH/DELETE/Restore prüfen **keine** Eigentümerschaft (jeder angemeldete Nutzer kann Projekt-Assets eines veröffentlichten Projekts als gelöscht markieren oder wiederherstellen).

### 3.21 Instanz: `GET /api/instances/`

Cache-Hit liefert die gespeicherte Antwort ohne `Cache-Control`-Header; Cache-Miss berechnet `config` aus `get_configuration_value` (13 Keys) und Settings (2.7.5). Da der Endpunkt `AllowAny` ist und `InstanceSerializer` `__all__` nutzt, sind `instance_id`, `whitelist_emails`, `namespace`, `domain`, Versionen und Flags **öffentlich lesbar**.

### 3.22 Erst-Einrichtung (Admin Sign-up, I-09)

1. Throttle (10/min/IP) → sonst Redirect 5900.
2. Keine Instanz → 5000; `is_setup_done` oder irgendein `InstanceAdmin` → 5150.
3. Pflichtfelder E-Mail, Passwort, Vorname → 5155; E-Mail `strip().lower()` + `validate_email` → 5160; E-Mail existiert als User → 5180; Passwortstärke → 5021.
4. `transaction.atomic()` + `Instance.select_for_update()` → erneute Prüfung 5150 → `User(first_name, last_name, email, username=uuid4().hex, password=make_password, is_password_autoset=False)` → `Profile(user, company_name)` → User aktiv, `last_active`, `last_login_time`, `last_login_ip`, `last_login_uagent`, `token_updated_at` → `InstanceAdmin(user, instance)` → `instance.is_setup_done=True`, `instance_name=company_name`, `is_telemetry_enabled=<Form-Wert>`.
5. Außerhalb der Transaktion `user_login(is_admin=True)` (Django-Login, Session-Expiry `ADMIN_SESSION_COOKIE_AGE`, `device_info`) → 302 `general/`.
6. Der neue Admin ist **kein** Workspace-Mitglied; Onboarding-Felder von `User`/`Profile` bleiben auf Default (das Web-App-Onboarding erfolgt separat, A03).

### 3.23 Admin Sign-in (I-08)

Throttle → Instanz vorhanden (5000) → E-Mail/Passwort vorhanden (5170) → E-Mail gültig (5160) → User existiert (5185) → kein Bot (5175) → aktiv (5190) → Passwort korrekt (5175) → `InstanceAdmin(instance, user)` existiert (5175) → Login-Metadaten setzen → `user_login(is_admin=True)` → 302 `general/`. Ein normaler App-Login (Cookie `session-id`) und der Admin-Login (`admin-session-id`) sind unabhängige Sessions desselben Session-Stores (`SESSION_ENGINE = plane.db.models.session`).

### 3.24 Konfiguration speichern (I-13) und Verschlüsselung

Der Client sendet nur geänderte Keys; jeder Wert wird zu String getrimmt (Booleans im Frontend als `"0"`/`"1"`). Verschlüsselte Werte werden mit dem aus `SECRET_KEY` abgeleiteten Fernet-Schlüssel gespeichert; ändert sich `SECRET_KEY`, liefern alle Secrets `""` (still). Lesen über `GET {I}/configurations/` gibt Klartext zurück (das God-Mode-UI zeigt Secrets maskiert, A11).

### 3.25 Caching-Fallstricke (Instanz)

| Schlüssel | gesetzt von | invalidiert von | Folge |
|---|---|---|---|
| `/api/instances/` | I-01 | I-02, I-04, I-05, I-08, I-09, I-11, I-13, I-14 | Invalidierung **vor** der Änderung ⇒ parallele GETs können den alten Stand erneut 2 h cachen (Race) |
| `/api/instances/admins/` | I-03 | – | Admin-Liste bis 2 h veraltet nach I-04/I-05 |
| `/api/instances/configurations/` | I-12 | I-13 | nach I-14 bis 2 h veraltet |
| Alle | – | `python manage.py clear_cache` beim Containerstart | |

Bei `DEBUG=True` wird nicht gecacht.

### 3.26 Sammelliste der Befunde (Entscheidung „1:1 nachbauen“ vs. „korrigieren“)

| # | Bereich | Befund | Quelle | Empfehlung |
|---|---|---|---|---|
| B-01 | v1 | Estimates-Endpunkte implementiert, nicht geroutet | `V1U/__init__.py` | routen (Doc 21 §2.5) |
| B-02 | v1 | `PUT` Upsert-Handler unerreichbar | `V1V/issue.py` Z. 623 | als expliziten Upsert-Endpunkt nachbauen oder weglassen (Offener Punkt 6) |
| B-03 | v1 | Ungültiger API-Key → 403 statt 401 | 2.1.2 | 401 mit `WWW-Authenticate: ApiKey` (Contract-Abweichung dokumentieren) |
| B-04 | v1 | Einladungen/Stickies ohne API-Key-Rate-Limit | 2.1.1 | Rate-Limit global für `/api/v1` |
| B-05 | v1 | `POST …/archive` für jedes WS-Mitglied A/M ohne Projektbezug | 2.1.8 | Projekt-Admin verlangen |
| B-06 | v1 | `GET …/attachments/` ohne Mitgliedschaftsprüfung; Anhang-Detail/Patch/Delete ohne `issue_id`-Bindung | 2.2.9 | korrigieren |
| B-07 | v1 | Kommentar PATCH/DELETE ohne Autorenprüfung; Gäste dürfen schreiben | 2.2.7 | an App-Regeln angleichen (A04) |
| B-08 | v1 | Kommentar-HTML im Create nicht sanitisiert | 2.2.7 | sanitisieren |
| B-09 | v1 | Cycle-PATCH: Einschränkung auf `sort_order` bei abgeschlossenen Cycles wirkungslos | 2.2.11 | korrigieren |
| B-10 | v1 | Modul-Zuordnung: fehlerhafter Vergleich, `modules_list` als String | 3.11 | fachlich wie App-API (Mehrfachzuordnung erlaubt) |
| B-11 | v1 | Intake-Statusänderung nur für Admin (Kommentar sagt Admin+Member) | 3.12 | an App-API (A04) angleichen |
| B-12 | v1 | Intake-POST 500, wenn `intake_view=true`, aber kein Intake | 2.2.13 | Intake automatisch anlegen |
| B-13 | v1 | Projekt-PATCH: `default_state`/`estimate`-Fehler als 409 „identifier taken“ | 2.2.2 | 400 mit Feldfehler |
| B-14 | v1 | Mitgliederlisten enthalten inaktive Mitglieder ohne Kennzeichen | 3.13 | `is_active` ergänzen oder filtern |
| B-15 | v1 | v1-Einladungen ohne Token/E-Mail | 2.2.15 | über gemeinsamen Einladungsdienst inkl. Mail |
| B-16 | v1 | Generic Assets ohne Bindungsmöglichkeit; `asset_url` mit `issues/None` | 2.2.17 | Bindungsendpunkt (Doc 21 Assets) |
| B-17 | v1 | `limit`/`size` mit `int()` ohne Fehlerbehandlung → 500 | 2.2.5, 2.2.17 | 400 |
| B-17a | v1 | `S3Storage(..., is_server=True)` → `TypeError`: `POST assets/user-assets/server/`, `POST {W}/assets/`, `GET {W}/assets/{id}/` liefern 500 (POSTs hinterlassen verwaiste `FileAsset`) | `V1V/asset.py` Z. 338, 449, 576; `SET/storage.py` Z. 28 | funktionsfähig nachbauen (Soll-Verhalten aus Doku/Docstrings) |
| B-18 | v1 | `ProjectSummary` ohne Projektmitgliedschaft (Secret-Projekte zählbar) | 2.2.2 | PM oder WS-Admin verlangen |
| B-19 | Space | Listen Reaktionen/Votes immer leer | 2.6.2 | korrigieren (Frontend-Rollback, A11 K18) |
| B-20 | Space | `project-boards`-Endpunkt immer 500 | S-04 | weglassen oder korrekt implementieren |
| B-21 | Space | Reaktions-`avatar_url` aus Votes berechnet | S-06 | korrigieren |
| B-22 | Space | Issue-Detail 200 `null` statt 404 | S-06 | 404 (Frontend-Verhalten prüfen) |
| B-23 | Space | Vote-Wert unvalidiert; Vote-Löschen ohne Board-Flag | S-19/S-20 | validieren |
| B-24 | Space | Asset PATCH/DELETE/Restore ohne Eigentümerprüfung; GET liefert auch Bilder interner Kommentare | S-32…S-35 | auf eigene/öffentliche Assets beschränken |
| B-25 | Space | Intake-Liste/Detail zeigt alle Einreichungen jedem angemeldeten User | S-26/S-28 | auf eigene Einreichungen beschränken |
| B-26 | Space | `is_disabled` wird nicht ausgewertet | 2.6.1 | als „Board deaktiviert“ auswerten (Offener Punkt) |
| B-27 | Instanz | Öffentliche Ausgabe aller Instanzfelder (`whitelist_emails`, `instance_id`) | 3.21 | Feldmenge auf UI-Bedarf reduzieren |
| B-28 | Instanz | `sign-up-screen-visited` anonym; Admin-Löschen auch des letzten Admins | I-11, I-05 | absichern |
| B-29 | Instanz | Cache-Invalidierung unvollständig/racy | 3.25 | kein Response-Cache (wie A03 empfiehlt) |
| B-30 | Instanz | Admin-Workspace-Anlage ohne Seed-Daten | I-18 | gemeinsamen Workspace-Anlagedienst nutzen |
| B-31 | Instanz | `GET /api/instances/` ohne Instanz liefert flaches Objekt (Endlos-Spinner im UI, A11 K28) | I-01 | Instanz beim Start garantiert anlegen |
| B-32 | Instanz | Telemetrie standardmäßig aktiv mit Ziel `telemetry.plane.so`; GitHub-Versionsabfrage beim Start | 2.7.7 | entfällt (ADR-004) |

---

## 4. Abhängigkeiten zu anderen Bereichen

| Abhängigkeit | Richtung | Details | Quelle / Dokument |
|---|---|---|---|
| Datenmodell (alle Entitäten der v1/Space/Instanz) | dieser Bereich → Modelle | `Project, ProjectMember, ProjectPublicMember, State, Label, Issue, IssueAssignee, IssueLabel, IssueLink, IssueComment, IssueActivity, IssueRelation, IssueReaction, CommentReaction, IssueVote, FileAsset, Cycle, CycleIssue, Module, ModuleIssue, ModuleMember, Intake, IntakeIssue, Estimate, EstimatePoint, Sticky, Workspace, WorkspaceMember, WorkspaceMemberInvite, User, APIToken, APIActivityLog, DeployBoard, UserFavorite, ProjectPage, IssueType, Instance, InstanceAdmin, InstanceConfiguration, ChangeLog`; Soft-Delete-Manager, `issue_objects`-Manager, `crum`-Auditfelder | `M/*`; A02a/A02b |
| Berechtigungsklassen | gemeinsam mit App-API | `PERM/project.py`, `PERM/workspace.py` (identische Kopie unter `UT/permissions/`) | A03 2.4 |
| Paginierung, Grouper, Order-Allowlists, Issue-Filter | gemeinsam | `UT/paginator.py`, `UT/order_queryset.py`, `UT/issue_filters.py`, `SP/utils/grouper.py` | A03 2.2, A04 2.17/2.18 |
| Background-Tasks | dieser Bereich → Worker | `issue_activity` (Activity + Benachrichtigungen), `model_activity`/`webhook_activity` (Webhooks), `crawl_work_item_link_title`, `get_asset_object_metadata`, `process_logs`, `push_instance_metrics`, `delete_unuploaded_file_asset`, `unsnooze_expired_intake_issues`, `delete_api_logs` | A04 1.4, A03 2.14, A01 (Celery-Beat) |
| Webhooks | Webhook-Versand → v1-Serializer | Payload-Format = v1-Serializer (3.16) ⇒ Änderungen an v1-DTOs ändern Webhook-Verträge | `apps/api/plane/bgtasks/webhook_task.py`; A03 2.9 |
| API-Tokens | App-API → v1 | Anlage/Widerruf/Ablauf der Tokens in der App (Profil-Einstellungen) | A03 2.7 |
| Authentifizierung | Instanz/Space → Auth-App | Session-Middleware (Admin-Cookie), `BaseSessionAuthentication` (Origin-Check), `AuthenticationThrottle`, Fehlercodes, `user_login`, OAuth-Provider lesen Instanz-Konfiguration, Magic-Code/Passwort-Views lesen SMTP-Konfiguration | `AUTH/*` |
| Storage (S3/MinIO) | v1/Space → Storage | Presigned POST/GET, `USE_MINIO`-Sonderfall (Request-Host als Endpoint), `SIGNED_URL_EXPIRATION`, Bucket-Erstellung beim Start | `SET/storage.py`; A01, A03 2.10 |
| E-Mail | Instanz → SMTP | Test-Mail, Konfiguration für alle Mails | `LIC/utils/instance_value.py` |
| Frontend God Mode | `apps/admin` → `/api/instances/` | alle Aufrufe A11 2.7; Konfigurationsschlüssel A11 2.8 | A11 |
| Frontend Space | `apps/space` → `/api/public/` | alle Aufrufe A11 2.19 | A11 |
| Frontend Web | `apps/web` → `GET /api/instances/` (`config`), Publish-Modal → App-Deploy-Board-API | A08, A11 4 | A08, A11 |
| Live-Server | – | keine | – |
| Bezahl-Features | Erweiterung dieses Bereichs | Commercial-API-Ressourcen (Doc 21), OAuth-Apps/Scopes, SSO-Konfiguration im God Mode (Doc 22), Publish Views/Pages, Intake Forms/E-Mail (Doc 20, Doc 26) | `migration/features/20-…`, `21-…`, `22-…`, `26-…` |

---

## 5. Migrationshinweise (.NET 10 / Aspire / EF Core 10 / PostgreSQL / Angular)

### 5.1 Schnitt in der Zielarchitektur

| Original | Ziel (.NET) | Hinweis |
|---|---|---|
| `plane.api` (`/api/v1/`) | Endpunktgruppe `PublicApiV1` (Minimal APIs oder Controller) in eigenem Projekt `Plane.PublicApi`, gehostet im API-Host; per Konfiguration zusätzlich als separater Aspire-Service („External API“, P03-F39) startbar | Pfade, Aliase (`issues/` ↔ `work-items/`, `members/` ↔ `project-members/`), Trailing-Slash und `operationId`s beibehalten (Contract-Kompatibilität für Skripte/MCP) |
| `plane.space` (`/api/public/`) | Endpunktgruppe `PublicSpace` | Anchor-Auflösung als Endpoint-Filter (ersetzt `DeployBoardAnchorMixin`) |
| `plane.license` (`/api/instances/`) | Endpunktgruppe `InstanceAdmin` + Domänendienst `InstanceSettings` | kein Lizenz-/Edition-Konzept (ADR-001) |
| `plane.web` | ASP.NET Core Health Checks (`/` → `{"status":"OK"}` beibehalten, zusätzlich Aspire-ServiceDefaults `/health`, `/alive`), statische `robots.txt` | Aspire-Dashboard nutzt eigene Probes |
| `plane.analytics` | entfällt (leer) | – |
| Celery-Tasks | Background-Worker (eigener Aspire-Service) mit dauerhafter Queue in PostgreSQL (Outbox-Tabelle + Hosted Service, alternativ Hangfire/Quartz mit PostgreSQL-Storage) | `transaction.on_commit` ⇒ Transactional Outbox |

### 5.2 Authentifizierung v1 (API-Key)

- Eigener `AuthenticationHandler<ApiKeyOptions>` (Schema „ApiKey“), Header `X-Api-Key` (case-insensitiv), Lookup per EF Core: `IsActive && (ExpiredAt == null || ExpiredAt > now) && User.IsActive`. `last_used` aktualisieren – um einen DB-Write pro Request zu vermeiden, gepuffert (z. B. höchstens einmal pro Minute je Token) schreiben; die Token-Liste der UI zeigt `last_used` (A03) – Minutengenauigkeit genügt.
- Greenfield erlaubt **Hash-Speicherung** (SHA-256 des Tokens + sichtbares Präfix `plane_api_`): Die UI sieht den Token nur in der Antwort auf `POST /api/users/api-tokens/` (A03 AT-01); `PATCH /api/users/api-tokens/{pk}/` liefert ihn im Original erneut aus (A03 AT-04), wird aber vom Frontend nicht aufgerufen ⇒ in der Zielarchitektur AT-04 ohne `token` beantworten. Für das Audit-Log den HMAC-Identifier (`HMAC-SHA256(SECRET_KEY, token)`) übernehmen, damit Log-Korrelation ohne Klartext möglich bleibt.
- Statuscodes: fehlender Key 401 `{"detail": "Authentication credentials were not provided."}`; ungültiger Key im Original 403 `{"detail": "Given API token is not valid"}` – Empfehlung 401 + `WWW-Authenticate: ApiKey` (bewusste, dokumentierte Abweichung; Tests akzeptieren beides).
- Session-Cookies dürfen `/api/v1/` **nicht** authentifizieren (eigene Authentication-Policy für die Gruppe).
- Bezahl-Erweiterung (ADR-001): OAuth 2.0 Authorization Server (z. B. OpenIddict auf PostgreSQL) für App-/Bot-Token mit Scopes laut Doc 21 Kap. 6; `APIToken.workspace` als Workspace-Token (PF-62) auswerten; beides über dieselben Authorization-Policies wie der API-Key.

### 5.3 Autorisierung

- Die Permission-Klassen (2.1.8) als wiederverwendbare `IAuthorizationRequirement`s mit Ressourcenauflösung aus Routenwerten (`slug`, `project_id`/`pk`, `project_identifier`) implementieren und **gemeinsam** mit der App-API nutzen. Achtung: Die Semantik hängt von der HTTP-Methode ab (SAFE/POST/sonstige) – als Tabelle im Code abbilden, nicht als Rollenattribut.
- Für jede Abweichung aus 3.26 (B-05, B-06, B-07, B-18) entscheiden: 1:1 (Contract) oder korrigiert (Sicherheit). Empfehlung: Sicherheitsbefunde korrigieren und in einem ADR „Bewusste Abweichungen v1“ festhalten.

### 5.4 Rate-Limiting

- `Microsoft.AspNetCore.RateLimiting` mit Partition = Token-Hash, **verteilt** (mehrere API-Instanzen): Redis/Valkey-gestützter Sliding-Window-Limiter (wie DRF) oder PostgreSQL-basiert, wenn kein Redis betrieben werden soll. Konfiguration `API_KEY_RATE_LIMIT` (Format `n/second|minute|hour|day`, Default `60/minute`).
- Header `X-RateLimit-Remaining`, `X-RateLimit-Reset` (Unix-Sekunden, Original: jetzt + Fensterlänge) bei Erfolg; bei Überschreitung 429 `{"error_code": 5900, "error_message": "RATE_LIMIT_EXCEEDED"}` + `Retry-After`.
- Für **alle** `/api/v1`-Endpunkte (auch Einladungen/Stickies, B-04).
- Space/anonym: 30/min je Client-IP (`AnonRateThrottle`), Admin-Login/Setup 10/min je IP (`AUTHENTICATION_RATE_LIMIT`); `ForwardedHeaders`-Middleware mit `NUM_PROXIES`-äquivalenter Konfiguration (`KnownProxies`/`ForwardLimit`).

### 5.5 Fehler- und Antwortverträge

- Keine `ProblemDetails`; stattdessen die Original-Bodies (2.1.4, 2.2) über Exception-Mapping je Endpunktgruppe: v1-`BaseAPIView`-Gruppe 404 „The requested resource does not exist.“, ViewSet-Gruppe/Space/Instanz 404 „The required object does not exist.“; Validierungsfehler im DRF-Format (`{"feld": ["…"]}`, `{"non_field_errors": ["…"]}`).
- JSON: `System.Text.Json` mit `JsonNamingPolicy.SnakeCaseLower`, UUIDs als Strings, `DateTimeOffset` ISO-8601 mit Offset (DRF-Default `2024-01-15T10:00:00.123456Z`), Datumsfelder `yyyy-MM-dd`; `description_binary` als Base64.
- Felder, die im Original wegen fehlender Annotation **fehlen** (DRF `SkipField`, 2.4), entweder ebenso weglassen (`JsonIgnoreCondition.WhenWritingNull` reicht nicht, da `null`-Werte sonst verschwinden) oder bewusst immer liefern – Entscheidung im Contract-Test festhalten.

### 5.6 Pagination, `fields`, `expand`

- Gemeinsame Komponente `CursorPagination` (Cursor `per_page:page:is_prev`, Envelope 2.1.5, Fehlertexte) für App-API, v1 und Instanz.
- `fields`: Projektion nach dem Serialisieren (DTO → `JsonObject`, Schlüssel filtern) – einfach und kompatibel; `expand`: Resolver-Map (2.1.6) mit Batch-Loading (keine N+1 wie im Original bei Assignees/Labels).
- Sortierung: Allowlists als Konstanten; ungültige Werte → Default (kein Fehler). Tiebreaker `id`/`created_at` ergänzen, damit Seiten stabil sind (Original ohne Tiebreaker bei `priority`).

### 5.7 OpenAPI

- `Microsoft.AspNetCore.OpenApi` (.NET 10, OpenAPI 3.1) mit Document-Transformern: nur `/api/v1`-Pfade, keine `PUT`, keine `server`-Pfade (Hook 2.1.9), Security-Schema `ApiKeyAuthentication` (Header `X-API-Key`), Tags samt Beschreibungen aus `SET/openapi.py`, `operationId`s wie im Original.
- UI (Swagger UI/Scalar/Redoc) **lokal gebündelt** ausliefern (Airgapped, ADR-004); aktivierbar per Konfiguration (Original: `ENABLE_DRF_SPECTACULAR`).
- Die Schema-Beispiele (`OA/examples.py`) als Beispiel-Payloads in die Doku übernehmen.

### 5.8 Storage-Fallstricke

- Das Frontend und v1-Clients erwarten **Presigned POST** (`upload_data.url` + `fields`, Multipart). Das AWS SDK für .NET bietet nur Presigned GET/PUT; Presigned POST (Policy-Dokument + SigV4) muss selbst implementiert oder über das MinIO-.NET-SDK (`PresignedPostPolicyAsync`, S3-kompatibel) erzeugt werden.
- `USE_MINIO`-Verhalten nachbilden: Presigned-URLs für Browser gegen den öffentlichen Host (Reverse-Proxy leitet den Bucket-Pfad an MinIO), für Server-Clients gegen den internen Endpoint (Soll-Verhalten von `is_server`, B-17a).
- `Content-Disposition`/Content-Type-Pinning (`INLINE_SAFE_MIME_TYPES`) exakt übernehmen (Sicherheitsfix im Original).

### 5.9 Space

- Cookie-Authentifizierung mit `session-id` und Origin-Check wie App (A03); Lese-Endpunkte anonym.
- `DeployBoard`-Lookup zentral (`AnchorResolver`) mit `entity_name == "project"` und Projektbindung; `is_disabled` auswerten (Offener Punkt).
- Gruppierte Issue-Liste über dieselbe Query-Komponente wie die App-Issue-Liste (A04) – nur mit fixer Projektbindung und reduzierter Feldmenge (2.6.2 S-05).
- `vote_items`/`reaction_items`: PostgreSQL `jsonb_agg(jsonb_build_object(...)) FILTER (WHERE ...)` per EF Core `FromSql`/Raw-Projektion oder zweite Abfrage + Gruppierung im Speicher.
- Bezahl-Erweiterungen auf derselben Infrastruktur: Publish Views (`entity_name="view"`), Publish Pages (`"page"`, Doc 26 §3.8), Intake Forms (`"intake"`, PF-36) – das Datenmodell `DeployBoard.entity_name/entity_identifier` ist bereits generisch.

### 5.10 Instanz / God Mode

- **ADR-001:** `edition`, `is_verified`, `is_support_required`, `namespace` und die Lizenzmechanik entfallen; das God-Mode-UI liest aber `instance_id`, `current_version`, `instance_name`, `is_telemetry_enabled`, `is_setup_done`, `workspaces_exist` (`apps/admin/app/(all)/(dashboard)/general/form.tsx`, `sidebar-help-section.tsx`, `apps/admin/store/instance.store.ts`) – diese Felder im DTO behalten. `packages/types/src/instance/base.ts` deklariert zusätzlich `license_key`, `user_count`, `is_activated` (im CE-Backend nicht geliefert).
- **ADR-004:** `push_instance_metrics` und die GitHub-Versionsabfrage (`register_instance`) entfallen bzw. sind standardmäßig aus; `latest_version` = aktuelle Version oder per Offline-Konfiguration. OpenTelemetry nur an den **lokalen** Collector/Aspire-Dashboard. Der UI-Schalter „Telemetrie“ bleibt sichtbar (ADR-005) – Semantik siehe Offener Punkt 6.
- **Instanz-Singleton** beim Start garantiert anlegen (Migration/Seeder), damit `GET /api/instances/` nie das flache Objekt liefert (B-31) – oder das flache Objekt 1:1 beibehalten, wenn das UI-Verhalten (Setup-Weiterleitung) es benötigt (A11 K28).
- **Konfigurations-Store:** Tabelle `instance_configurations` (Key, Value, Category, IsEncrypted) beibehalten; Seed der 36 Keys aus Umgebungsvariablen beim Start (idempotent, nur fehlende Keys). Lesezugriff über einen `IInstanceConfigProvider` mit kurzer In-Memory-Cache-Dauer und Invalidierung beim Speichern (statt 2-h-Response-Cache, B-29).
- **Verschlüsselung:** Greenfield ⇒ ASP.NET Core Data Protection (Schlüsselring in PostgreSQL, `PersistKeysToDbContext`) oder AES-GCM mit aus einem Instanz-Secret abgeleitetem Schlüssel; Fernet-Kompatibilität ist nicht nötig (keine Datenübernahme). Wichtig: Verhalten „Entschlüsselung fehlgeschlagen → leerer String“ bewusst entscheiden (lieber Fehler loggen und Admin-Hinweis anzeigen).
- **Admin-Session:** eigenes Cookie-Schema `admin-session-id` mit `ExpireTimeSpan = ADMIN_SESSION_COOKIE_AGE` (Default 1 h), Pfadregel „enthält `instances`“ als explizite Endpunktgruppe statt Substring-Match.
- **Form-Flows:** Sign-in/Sign-up/Sign-out bleiben **Form-POST + 302-Redirect** mit `error_code`/`error_message`-Query (das Angular-God-Mode-UI liest diese Parameter, A11 2.11); Antiforgery-Token (`csrfmiddlewaretoken` ⇒ ASP.NET Antiforgery mit Feldname `csrfmiddlewaretoken` und Endpunkt `GET /auth/get-csrf-token/` → `{"csrf_token"}`).
- **Workspace-Anlage durch Admins:** gemeinsamen `WorkspaceCreationService` mit App-API nutzen (inkl. Seed-Daten, B-30).
- **Bezahl-Erweiterungen (ADR-001):** God-Mode-Seiten und Keys für SAML, OIDC, LDAP, IdP-Group-Sync, Session-Expiry, User-Management (Doc 22 P03-F03…F08, F35) als zusätzliche `InstanceConfiguration`-Kategorien bzw. eigene Tabellen; Typ-Erweiterungspunkte im Frontend: `TExtendedLoginMediums`, `TExtendedInstanceAuthenticationModeKeys` (`packages/types/src/instance/auth-ee.ts`, in CE `never`).

### 5.11 Übersicht: 1:1 übertragbar vs. neu bauen

| Thema | 1:1 übertragbar | Neu bauen / ändern |
|---|---|---|
| Routen, Methoden, Aliase, `operationId`s | ✓ | tote/defekte Routen (2.2.19, S-04, B-17a) bewusst entscheiden |
| Request-/Response-Feldnamen, Enum-Werte, Fehlertexte | ✓ | Fehlercodes 403/401 (B-03), 409-Fehlzuordnung (B-13) |
| Berechtigungsmatrix | ✓ (als Policy-Tabelle) | Sicherheitskorrekturen B-05…B-08, B-18, B-24, B-25 |
| Pagination/Cursor/Envelope | ✓ | Tiebreaker |
| `fields`/`expand` | ✓ | Batch-Loading |
| Rate-Limit | Semantik ✓ | verteilter Limiter, Abdeckung aller v1-Routen |
| Hintergrundjobs | Ereignistypen/Payloads ✓ | Outbox + Worker statt Celery |
| Webhook-Payloads | ✓ (v1-DTOs) | gemeinsame DTO-Schicht |
| Presigned Uploads | Vertrag ✓ | Presigned-POST-Implementierung (.NET) |
| Instanz-Konfiguration | Keys/Kategorien ✓ | Verschlüsselung, Caching, Telemetrie-Entfall |
| Admin-Form-Flows | ✓ (Redirect-Protokoll) | Antiforgery |
| Space-Endpunkte | ✓ | Bugfixes B-19…B-26 |
| Estimates in v1 | Soll-Verhalten aus totem Code ✓ | Routing |

### 5.12 EF Core / PostgreSQL

| Entität | Hinweis | Original-Constraint |
|---|---|---|
| `ApiToken` | Unique-Index auf `Token` (bzw. `TokenHash`); Index `(UserId, IsActive)`; `ExpiredAt` nullable | `M/api.py` Z. 31 (`unique=True`, `db_index=True`) |
| `ApiActivityLog` | Append-only, hohe Schreiblast ⇒ eigene Tabelle, Index auf `CreatedAt` für Retention-Löschung (`API_ACTIVITY_LOG_RETENTION_DAYS`), optional Zeit-Partitionierung | `M/api.py` Z. 49ff.; `apps/api/plane/bgtasks/cleanup_task.py` |
| `DeployBoard` | Unique **gefilterter** Index `(EntityName, EntityIdentifier) WHERE deleted_at IS NULL` (`HasFilter`); Unique `Anchor` | `M/deploy_board.py` Z. 32, 46–53 |
| `ProjectPublicMember` | Unique gefiltert `(ProjectId, MemberId) WHERE deleted_at IS NULL` | `M/project.py` Z. 377–385 |
| `Instance` | Singleton (Seed beim Start); `InstanceId` unique | `LIC/models/instance.py` |
| `InstanceAdmin` | Unique `(InstanceId, UserId)`; `UserId` `ON DELETE SET NULL` | dito |
| `InstanceConfiguration` | Unique `Key` (max. 100), `Value` text | dito |
| Soft-Delete | globaler Query-Filter `DeletedAt == null` + explizites `IgnoreQueryFilters()` für Restore-Fälle (S-35 nutzt `all_objects`) | A02a |
| Rohabfragen | `vote_items`/`reaction_items`, `ArrayAgg`-Annotationen (`label_ids`, `assignee_ids`, `module_ids`) über `array_agg(...) FILTER (WHERE ...)` bzw. Npgsql-Array-Mapping | `SP/utils/grouper.py`, `SP/views/issue.py` |

### 5.13 Angular-Bezug (Frontends God Mode und Space)

- Die Angular-Ports von `apps/admin` und `apps/space` (A11) sind direkte Konsumenten von `/api/instances/` bzw. `/api/public/`; die Verträge aus 2.6.2/2.7.2 (inkl. Fehlertexte, Redirect-Parameter `error_code`/`error_message`, flaches Objekt ohne Instanz) bestimmen deren Verhalten 1:1 (ADR-005).
- Admin-Sign-in/Setup/Sign-out bleiben **native Form-POSTs** (kein `HttpClient`), damit die 302-Redirects und das Admin-Cookie wie im Original funktionieren; CSRF-Token vorher per `GET /auth/get-csrf-token/` holen.
- Der Trailing-Slash-Interceptor der Original-Services (A11 2.7) muss im Angular-`HttpInterceptor` nachgebildet werden, da alle Backend-Routen mit `/` enden.
- Die Space-Metadaten (`GET {A}/meta/`) werden im Original serverseitig ohne Cookies geladen (A11 B8) ⇒ Angular SSR/Prerendering oder ein schlanker .NET-Endpunkt für `<title>`/OG-Tags.
- Die Web-App liest `GET /api/instances/` → `config` (Login-Methoden, `is_workspace_creation_disabled`, `has_unsplash_configured`, `has_llm_configured`, `file_size_limit`, `instance_changelog_url`) – im Angular-`InstanceStore` zentral cachen.

### 5.14 Tests

Die vorhandenen Contract-Tests sind direkt als Spezifikation für die .NET-Integrationstests (z. B. xUnit + `WebApplicationFactory` + Testcontainers-PostgreSQL) verwendbar: `apps/api/plane/tests/contract/api/{test_api_permission_parity, test_authentication, test_cycle_issue_project_scope, test_cycles, test_cycles_lite, test_generic_asset, test_intake_issue_update, test_issue_assignee_label_validation, test_issue_attachment_size, test_issue_notifications, test_issue_read_only_fields, test_issues, test_labels, test_members_lite, test_modules_lite, test_non_object_json_body, test_project_members_roster_scope, test_projects, test_projects_lite, test_state_admin_scope, test_work_item_link_relation_project_scope}.py` (v1) sowie `apps/api/plane/tests/contract/app/{test_spaces_board_object_scope_app, test_space_asset_comment_scope_app, test_deploy_board_identity_readonly_app, test_deploy_board_project_scope_app}.py` (Space/Publish) und `apps/api/plane/tests/unit/middleware/test_api_authentication.py`, `apps/api/plane/tests/unit/views/test_non_object_json_body.py`. Zusätzlich Contract-Tests gegen das laufende Original (gleiche Requests, Vergleich der JSON-Shapes aus 2.4/2.6.2) empfehlen.

---

## 6. Offene Punkte

| # | Frage | Kontext | Vorschlag |
|---|---|---|---|
| O-01 | Sollen die im Original **defekten** Endpunkte (Server-Assets, Generic-Asset POST/GET, `project-boards`, Reaktions-/Vote-Listen) im Soll-Verhalten gebaut oder weggelassen werden? | B-17a, B-19, B-20 | Soll-Verhalten bauen (Doku/Docstrings, Frontend-Rollback braucht Listen) |
| O-02 | Wird der Upsert per `PUT {P}/work-items/` (externe ID) als Endpunkt angeboten? | V-DEAD-09; Doc 21 nennt `PUT` | Ja, als `PUT {P}/work-items/` (Importer), da Commercial-Doku ihn kennt – Prüfung gegen Doc 21 §2.10 |
| O-03 | Strenge der Sicherheitskorrekturen in v1 (Archiv-Permission, Attachment-Scoping, Kommentar-Autorenschaft, Summary-Scoping) | B-05…B-08, B-18 | korrigieren; ADR „Bewusste Abweichungen“ |
| O-04 | Bedeutung des Telemetrie-Schalters im God Mode unter ADR-004 | 2.7.7, 5.10 | Schalter steuert nur lokale OTel-Metriken (Aspire/Collector); Default aus |
| O-05 | Bedeutung von `DeployBoard.is_disabled` und `is_activity_enabled` | 2.6.1 | `is_disabled` ⇒ alle Space-Endpunkte 404; `is_activity_enabled` ⇒ Aktivitätsanzeige im Space (Frontend prüfen, A11) |
| O-06 | Serialisierung von `description_binary` in `GET {A}/issues/{id}/` (Rohbytes in `.values()`; abhängig vom DB-Treiber `bytes`/`memoryview`, DRF-Encoder dekodiert `bytes` als UTF-8) – im Original möglicherweise 500 bei binären Yjs-Daten | S-06 | Feld im Space weglassen (vom Frontend nicht genutzt, A11 B13) oder Base64 |
| O-07 | Token-Speicherung als Hash: Re-Exposition des Tokens in `PATCH /api/users/api-tokens/{pk}/` (A03 AT-04) entfällt dann – akzeptiert? | 5.2 | Ja (Frontend nutzt AT-04 nicht); Entscheidung im ADR „Bewusste Abweichungen“ |
| O-08 | Admin-Rollen: `InstanceAdmin.role` kennt nur 20; Permission prüft ≥ 15 | 2.7.3 | Rolle beibehalten; EE-User-Management (Doc 22 P03-F03) ggf. weitere Rollen |
| O-09 | v1-Einladungen: E-Mail-Versand und Token nachrüsten? | B-15 | gemeinsamer Einladungsdienst; Commercial-Doku Doc 21 §2.16 abgleichen |
| O-10 | Changelog: `ChangeLog`-Modell ohne Endpunkt; Admin-UI ruft `GET /api/instances/changelog/` (404) | 2.7.3 | Endpunkt mit leerer Liste oder Datenquelle offline (Airgapped) – mit UI-Verhalten (A11) abstimmen |
| O-11 | Projekt-Liste v1 enthält archivierte Projekte, Lite-Liste nicht (ohne Parameter) | V-PRJ-01/03 | 1:1 beibehalten (Contract) |
| O-12 | Intake-Priorität im Space-Create Default `low` statt `none` | S-27 | an `none` angleichen (fachlich konsistent) – Entscheidung Fachseite |
| O-13 | Verhalten bei mehreren Intakes je Projekt (v1 nimmt das erste, nicht `is_default`) | V-INT-01 | `is_default` verwenden |
