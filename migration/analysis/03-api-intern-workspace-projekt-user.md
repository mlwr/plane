# A03 – Interne App-API Teil 1: Workspace, Projekt, User & Querschnitt (Assets, Suche, Analytics, Export, Notifications, Webhooks, AI)

> **Status:** IST-Analyse Plane v1.4.2 Community Edition (AGPL-3.0)
> **Bindend:** `migration/architecture/00-grundsatzentscheidungen.md` (ADR-000 … ADR-006). Insbesondere ADR-001 (eine Edition, alle Bezahl-Features aktiv, kein Upsell), ADR-003 (Greenfield, JSON-Verträge fachlich am Original, `snake_case`), ADR-004 (Self-hosted/Airgapped, externe Dienste optional), ADR-005 (UI 1:1 – das Frontend zeigt Fehlertexte des Backends teils direkt an).
> **Bereich (vollständig gelesen):**
> - URL-Konfiguration: `apps/api/plane/app/urls/{workspace,project,user,state,estimate,timezone,notification,webhook,api,asset,search,exporter,analytic,external}.py`, `apps/api/plane/app/urls/__init__.py`, `apps/api/plane/urls.py`
> - Views: `apps/api/plane/app/views/{workspace,project,user,state,estimate,timezone,notification,webhook,asset,search,exporter,analytic,external}/*.py`, `apps/api/plane/app/views/{api,base,error_404,__init__}.py`
> - Serializer: `apps/api/plane/app/serializers/{base,workspace,project,user,state,estimate,notification,webhook,asset,api,exporter,analytic,favorite,draft}.py` sowie die hier verwendeten Klassen aus `cycle.py` (`CycleSerializer`), `module.py` (`ModuleSerializer`), `issue.py` (`LabelSerializer`, `IssueActivitySerializer`, `IssueFlatSerializer`)
> - Permissions: `apps/api/plane/app/permissions/{__init__,base,workspace,project,page}.py`
> **Zur Verhaltensklärung zusätzlich gelesen:** `apps/api/plane/utils/{paginator,cache,order_queryset,analytics_plot,build_chart,date_utils,url,constants,content_validator(Teile),path_validator(Teile),ip_address(Teile),host(Teile),issue_search,grouper(Teile),exception_logger}.py`, `apps/api/plane/utils/core/mixins/view.py`, `apps/api/plane/middleware/db_routing.py`, `apps/api/plane/authentication/{session,rate_limit}.py`, `apps/api/plane/authentication/adapter/exception.py`, `apps/api/plane/settings/{common,storage}.py` (Teile), `apps/api/plane/license/utils/instance_value.py`, `apps/api/plane/utils/instance_config_variables/core.py` (LLM/Unsplash), `apps/api/plane/throttles/asset.py`, Modelle `apps/api/plane/db/models/{workspace,project,user,state,estimate,notification,webhook,api,asset,sticky,favorite,recent_visit,exporter,analytic,deploy_board,draft}.py`, `apps/api/plane/db/mixins.py`, Background-Tasks `apps/api/plane/bgtasks/{recent_visited_task,workspace_seed_task(Teile),workspace_invitation_task(Teile),webhook_task(Teile),export_task(Teile),storage_metadata_task,deletion_task(Teile)}.py`, Frontend-Aufrufer `apps/web/services/*.ts`, `packages/services/src/**`, ausgewählte Stores/Komponenten (jeweils zitiert).
> **Konventionen:** `{W}` = `/api/workspaces/{slug}`, `{P}` = `/api/workspaces/{slug}/projects/{project_id}`, `{U}` = `/api/users`. Alle Pfade dieses Bereichs hängen unter dem Präfix `/api/` (`apps/api/plane/urls.py`: `path("api/", include("plane.app.urls"))`). Abkürzungen für Quellpfade: `V/` = `apps/api/plane/app/views/`, `S/` = `apps/api/plane/app/serializers/`, `PERM/` = `apps/api/plane/app/permissions/`, `M/` = `apps/api/plane/db/models/`, `UT/` = `apps/api/plane/utils/`, `BG/` = `apps/api/plane/bgtasks/`, `URL/` = `apps/api/plane/app/urls/`, `WEB/` = `apps/web/`, `SVC/` = `packages/services/src/`. Rollen: **A** = Admin (20), **M** = Member (15), **G** = Guest (5).

---

## Inhaltsverzeichnis

1. Überblick & Verantwortlichkeiten
2. Vollständige Inventare
   - 2.1 Request-Pipeline & Basisklassen (`V/base.py`, `V/error_404.py`)
   - 2.2 Pagination (`UT/paginator.py`)
   - 2.3 Serializer-Basis (`S/base.py`: `fields`/`expand`)
   - 2.4 Berechtigungen (`PERM/*`) und Hilfs-Prädikate
   - 2.5 Endpunkt-Inventar Workspace (`URL/workspace.py`)
   - 2.6 Endpunkt-Inventar Projekt (`URL/project.py`)
   - 2.7 Endpunkt-Inventar User (`URL/user.py`) & API-Tokens (`URL/api.py`)
   - 2.8 Endpunkt-Inventar States, Estimates, Timezones
   - 2.9 Endpunkt-Inventar Notifications & Webhooks
   - 2.10 Endpunkt-Inventar Assets (`URL/asset.py`)
   - 2.11 Endpunkt-Inventar Suche, Export, Analytics, External (AI/Unsplash)
   - 2.12 Serializer-Inventar
   - 2.13 Modellfelder der `__all__`-Serializer (Response-Shapes)
   - 2.14 Seiteneffekte: Celery-Tasks, Cache-Invalidierung, Activity/Webhooks
   - 2.15 Frontend-Abdeckung & Lücken (Frontend ruft Endpunkte, die im CE-Backend fehlen)
   - 2.16 Bezüge zu den Bezahl-Editionen in diesem Bereich
3. Verhalten/Logik/Abläufe im Detail (inkl. Edge-Cases)
4. Abhängigkeiten zu anderen Bereichen
5. Migrationshinweise (.NET Aspire / EF Core / PostgreSQL / Angular)
6. Offene Punkte

---

## 1. Überblick & Verantwortlichkeiten

Der Bereich A03 umfasst die **sitzungsbasierte interne REST-API**, die ausschließlich vom Web-Frontend (`apps/web`) und – für einzelne Endpunkte – von `apps/admin`/`apps/space`/`apps/live` aufgerufen wird. Er deckt folgende fachliche Domänen ab:

| Domäne | URL-Datei | View-Dateien | Kernaufgaben |
|---|---|---|---|
| Workspace | `URL/workspace.py` | `V/workspace/{base,member,invite,user,cycle,module,label,state,estimate,favorite,draft,home,quick_link,recent_visit,sticky,user_preference}.py` | Workspace-CRUD, Slug-Prüfung, Mitglieder/Rollen, Einladungen, Workspace-weite Listen (Labels, States, Estimates, Cycles, Modules), Benutzerprofil im Workspace (Stats, Aktivitäten, Issues), Favoriten, Entwürfe (Draft Issues), Home (Widgets, Quick Links, Recents, Stickies), Sidebar-Präferenzen, Themes |
| Projekt | `URL/project.py` | `V/project/{base,member,invite}.py` | Projekt-CRUD, Sichtbarkeit (Netzwerk public/secret), Identifier, Archivierung, Mitglieder, Einladungen/Beitritt, Projekt-Favoriten (Legacy), Veröffentlichung (Deploy Boards), Mitglieder-Präferenzen |
| User | `URL/user.py`, `URL/api.py` | `V/user/base.py`, `V/workspace/{base,user}.py` (Graphen/Dashboard), `V/api.py` | „Ich“-Ressourcen: Profil, Einstellungen, E-Mail-Wechsel mit Code, Konto-Deaktivierung, Onboarding/Tour, verknüpfte OAuth-Accounts, Instanz-Admin-Status, Aktivitäten, eigene Workspaces, persönliche API-Tokens |
| States | `URL/state.py` | `V/state/base.py` | Projekt-Status-CRUD, Default-State, Intake-/Triage-State |
| Estimates | `URL/estimate.py` | `V/estimate/base.py` | Schätzsysteme (categories/points) und Schätzpunkte inkl. Umhängen betroffener Issues |
| Timezones | `URL/timezone.py` | `V/timezone/base.py` | Statische Zeitzonenliste für Auswahlfelder |
| Notifications | `URL/notification.py` | `V/notification/base.py` | Inbox (Liste, Filter, gelesen/ungelesen, archivieren, snoozen), Ungelesen-Zähler, „alle als gelesen“, E-Mail-Benachrichtigungs-Präferenzen |
| Webhooks | `URL/webhook.py` | `V/webhook/base.py` | Webhook-CRUD inkl. SSRF-Prüfung, Secret-Regeneration, Logs |
| Assets | `URL/asset.py` | `V/asset/{base,v2}.py` | Upload via Presigned-POST (S3/MinIO), Bestätigung, Löschen/Wiederherstellen, Download/Static-Redirects, Duplizieren, Bulk-Zuordnung; Legacy-Upload (v1) |
| Suche | `URL/search.py` | `V/search/{base,issue}.py` | Globale Suche (Command-Palette), Entity-Suche (Mentions/Picker), Issue-Suche (Parent/Relation/Sub-Issue/Cycle/Module-Picker) |
| Export | `URL/exporter.py` | `V/exporter/base.py` | Issue-Export (CSV/XLSX/JSON, asynchron) und Export-Historie |
| Analytics | `URL/analytic.py` | `V/analytic/{base,advance,project_analytics}.py` | Legacy-Analytics (x/y-Achse), gespeicherte Analytics-Views, CSV-Export per E-Mail, Default-Analytics, Projekt-Statistiken, „Advance Analytics“ (Workspace & Projekt: Overview, Work Items, Charts) |
| External | `URL/external.py` | `V/external/base.py` | KI-Assistent (LLM über OpenAI-SDK), Unsplash-Proxy |
| Querschnitt | – | `V/base.py`, `V/error_404.py`, `PERM/*`, `S/base.py` | Basisklassen, Fehlerbehandlung, Pagination, Berechtigungs-Decorator, dynamische Serializer |

**Größenordnung:** 216 Methode×Pfad-Kombinationen (Inventar-IDs in Abschnitt 2.5–2.11: Workspace W-01 … W-68, Projekt P-01 … P-38, User U-01 … U-20, API-Tokens AT-01 … AT-05, States S-01 … S-07, Estimates E-01 … E-09, Timezones T-01, Notifications N-01 … N-12, Webhooks WH-01 … WH-07, Assets A-01 … A-25, Suche SR-01 … SR-03, Export X-01 … X-02, Analytics AN-01 … AN-16, External EXT-01 … EXT-03).

**Authentifizierung:** Alle Views erben `BaseSessionAuthentication` (`apps/api/plane/authentication/session.py`) – Django-Session-Cookie, **kein** Django-CSRF-Token; stattdessen prüft `enforce_csrf` bei nicht-sicheren Methoden den `Origin`-Header gegen die eigene Host-Adresse bzw. `WEB_URL`, `APP_BASE_URL`, `ADMIN_BASE_URL`, `SPACE_BASE_URL`, `LIVE_BASE_URL`, `CORS_ALLOWED_ORIGINS`, `CSRF_TRUSTED_ORIGINS`. Fehlender `Origin` wird akzeptiert (Nicht-Browser-Clients wie der Live-Server); `Origin: null` wird abgelehnt → 403 `{"detail": "CSRF Failed: origin not allowed"}`. Ausnahme: `TimezoneEndpoint` erbt direkt von DRF `APIView` und nutzt daher die DRF-Default-Authentifizierung `rest_framework.authentication.SessionAuthentication` (`settings/common.py` `REST_FRAMEWORK`), ist aber `AllowAny`.

**Antwortformat:** Ausschließlich JSON (`DEFAULT_RENDERER_CLASSES = JSONRenderer`), Ausnahmen: CSV-Download (`ExportWorkspaceUserActivityEndpoint`) und HTTP-302-Redirects auf Presigned-URLs (Asset-Download/Static). Feldnamen `snake_case`, UUIDs als Strings, Datumswerte ISO-8601 (Django-REST-Default mit Zeitzonenoffset; DB in UTC, `USE_TZ = True`, `TIME_ZONE = "UTC"`).

---

## 2. Vollständige Inventare

### 2.1 Request-Pipeline & Basisklassen (`V/base.py`, `V/error_404.py`)

#### 2.1.1 Klassenhierarchie

| Klasse | Quelle | Basisklassen (MRO-Reihenfolge) | Default-Attribute |
|---|---|---|---|
| `TimezoneMixin` | `V/base.py` | – | `initial()`: wenn authentifiziert → `timezone.activate(zoneinfo.ZoneInfo(request.user.user_timezone))`, sonst `timezone.deactivate()` |
| `BaseViewSet` | `V/base.py` | `TimezoneMixin`, `ReadReplicaControlMixin`, DRF `ModelViewSet`, `BasePaginator` | `model = None`, `permission_classes = [IsAuthenticated]`, `filter_backends = (DjangoFilterBackend, SearchFilter)`, `authentication_classes = [BaseSessionAuthentication]`, `filterset_fields = []`, `search_fields = []`, `use_read_replica = False` |
| `BaseAPIView` | `V/base.py` | `TimezoneMixin`, `ReadReplicaControlMixin`, DRF `APIView`, `BasePaginator` | wie oben (ohne `model`); eigene `filter_queryset()` iteriert über alle `filter_backends` |
| `ReadReplicaControlMixin` | `UT/core/mixins/view.py` | – | Klassenattribut `use_read_replica` (Default im Mixin `True`, in beiden Basisklassen auf `False` überschrieben) |
| `TimezoneEndpoint` | `V/timezone/base.py` | DRF `APIView` (nicht `BaseAPIView`!) | `permission_classes = [AllowAny]` |

**Wirkung der Zeitzonen-Aktivierung:** Alle Django-Datumsfunktionen, die auf die „aktuelle Zeitzone“ zugreifen, rechnen in der **Benutzerzeitzone** (`User.user_timezone`): `__date`-Lookups (z. B. `created_at__date=` in `ExportWorkspaceUserActivityEndpoint`, `created_at__date__gte` in Analytics), `TruncMonth`, `TruncDate`, `ExtractMonth`, `ExtractWeek`, `ExtractDay`, `Cast(..., DateField())`. Die .NET-Implementierung muss Datumsgruppierungen deshalb in der Benutzerzeitzone durchführen (PostgreSQL: `(created_at AT TIME ZONE :tz)::date`).

**Read-Replica-Routing:** `apps/api/plane/middleware/db_routing.py` (`ReadReplicaRoutingMiddleware`, nur aktiv wenn konfiguriert, `settings/common.py` Zeile ~245) leitet GET/HEAD/OPTIONS an die Replica, wenn die View `use_read_replica = True` hat. Views mit `use_read_replica = True` in diesem Bereich: `UserWorkSpacesEndpoint`, `WorkSpaceMemberViewSet`, `WorkspaceMemberUserEndpoint`, `WorkspaceEstimatesEndpoint`, `WorkspaceFavoriteEndpoint`, `WorkspaceLabelsEndpoint`, `QuickLinkViewSet`, `UserRecentVisitViewSet`, `WorkspaceStatesEndpoint`, `WorkspaceStickyViewSet`, `WorkspaceUserPreferenceViewSet`, `ProjectViewSet`, `UserProjectRolesEndpoint`, `UserEndpoint`, `UnreadNotificationEndpoint`. Fachlich irrelevant (reine Lastverteilung).

#### 2.1.2 Ablauf eines Requests

1. Django-Middleware (`settings/common.py` `MIDDLEWARE`): CORS → Security → WhiteNoise → `plane.authentication.middleware.session.SessionMiddleware` → `CommonMiddleware` (**`APPEND_SLASH` = Django-Default `True`**: GET ohne Slash → 301 auf `…/`) → CSRF-Middleware (für DRF-Views wirkungslos, DRF ist `csrf_exempt`) → Auth → Clickjacking → `crum.CurrentRequestUserMiddleware` (setzt „current user“ für `BaseModel.save()` → `created_by`/`updated_by`) → GZip → `RequestBodySizeLimitMiddleware` → `APITokenLogMiddleware` → `RequestLoggerMiddleware`.
2. `dispatch()` (überschrieben in `BaseViewSet`/`BaseAPIView`): ruft DRF-`dispatch`, fängt **jede** Exception und leitet sie an `handle_exception`. In `DEBUG` wird zusätzlich die Query-Anzahl geloggt.
3. DRF `initial()`: Authentifizierung (Session) → `TimezoneMixin.initial` → Permission-Klassen (`has_permission`) → Throttles (global `AnonRateThrottle` 30/min **nur für anonyme** Requests; zusätzlich View-spezifische Throttles, siehe 2.1.4).
4. Handler-Methode, ggf. mit Decorators `@allow_permission`, `@invalidate_cache`, `@cache_response`, `method_decorator(cache_control/vary_on_cookie/gzip_page/cache_page)`.
5. Ausnahmebehandlung (siehe 2.1.3).

#### 2.1.3 Fehlerbehandlung (`handle_exception`)

`BaseViewSet.handle_exception` und `BaseAPIView.handle_exception` rufen zuerst DRFs `handle_exception` (behandelt alle `APIException`-Subklassen, `Http404`, `django.core.exceptions.PermissionDenied` über den konfigurierten Handler `plane.authentication.adapter.exception.auth_exception_handler`). Wird dort re-raised (alle übrigen Exceptions), gilt folgende Abbildung:

| Exception-Typ | HTTP | Body (exakt) | Bemerkung |
|---|---|---|---|
| `django.db.IntegrityError` | 400 | `{"error": "The payload is not valid"}` | z. B. Unique-Constraint-Verletzungen ohne eigene Behandlung |
| `django.core.exceptions.ValidationError` | 400 | `{"error": "Please provide valid detail"}` | Modell-Validatoren, ungültige UUID in Filtern |
| `django.core.exceptions.ObjectDoesNotExist` (inkl. `Model.DoesNotExist`) | 404 | `{"error": "The required object does not exist."}` | **häufigster 404-Pfad** (`Model.objects.get(...)`) |
| `KeyError` | 400 | `{"error": "The required key does not exist."}` | z. B. `allow_permission` ohne `slug` in URL, ungültiger `snoozed`-Wert |
| alle anderen (`AttributeError`, `TypeError`, `AssertionError`, …) | 500 | `{"error": "Something went wrong please try again later"}` | wird via `log_exception` (`UT/exception_logger.py`, Logger `plane.exception`) geloggt |

`BaseViewSet` druckt zusätzlich `print(e, traceback)` in DEBUG bzw. `"Server Error"`; `BaseViewSet` loggt `KeyError` (BaseAPIView nicht). Funktional identisch.

**DRF-Standardfehler (vom `auth_exception_handler`, `apps/api/plane/authentication/adapter/exception.py`):**

| Auslöser | HTTP | Body |
|---|---|---|
| Nicht authentifiziert (`NotAuthenticated`) | **401** (Handler überschreibt DRFs 403) | `{"detail": "Authentication credentials were not provided."}` |
| Permission-Klasse liefert `False` | 403 | `{"detail": "You do not have permission to perform this action."}` |
| CSRF-Origin abgelehnt | 403 | `{"detail": "CSRF Failed: origin not allowed"}` |
| Throttle (`Throttled`) | 429 | `{"error_code": 5900, "error_message": "RATE_LIMIT_EXCEEDED"}` |
| `serializer.is_valid(raise_exception=True)` schlägt fehl | 400 | DRF-Fehlerobjekt `{"<feld>": ["<meldung>"], "non_field_errors": [...]}` |
| Methode nicht gemappt (ViewSet) | 405 | `{"detail": "Method \"PUT\" not allowed."}` |
| `get_object()`/`Http404` | 404 | `{"detail": "No <Model> matches the given query."}` bzw. `{"detail": "Not found."}` (DRF-Version-abhängig) |
| `ParseError` (Pagination) | 400 | `{"detail": "Invalid cursor parameter."}` / `{"detail": "Invalid per_page parameter."}` / `{"detail": "Invalid per_page value. Cannot exceed 1000."}` / `{"detail": "Error in parsing"}` / `{"detail": "Invalid group_by field: <x>"}` |

**Unbekannte URL:** `handler404 = "plane.app.views.error_404.custom_404_view"` (`apps/api/plane/urls.py`) → 404 `{"error": "Page not found."}` (`V/error_404.py`). Gilt auch für alle vom Frontend aufgerufenen, im CE-Backend fehlenden Endpunkte (Abschnitt 2.15).

**Methode/Pfad-Mismatch bei `APIView`-Klassen:** Viele `BaseAPIView`-Klassen sind an zwei URL-Muster gebunden (mit/ohne `{pk}`). Ein Request mit einer Methode, deren Signatur nicht zum Pfad passt (z. B. `POST {W}/webhooks/{pk}/`, `GET {W}/file-assets/`), endet in `TypeError` → **500** `{"error": "Something went wrong please try again later"}`. In .NET sind diese Kombinationen schlicht nicht zu routen (→ 404/405); die Abweichung ist zulässig, da kein Client sie nutzt.

#### 2.1.4 Throttles in diesem Bereich

| Throttle | Quelle | Rate | Schlüssel | Verwendet in |
|---|---|---|---|---|
| `AnonRateThrottle` (global) | `settings/common.py` | `30/minute` | Client-IP (unter Berücksichtigung `NUM_PROXIES`) | alle Views, nur für **anonyme** Requests (relevant für `AllowAny`-Endpunkte: `TimezoneEndpoint`, `UserSessionEndpoint`, `WorkspaceJoinEndpoint`, `ProjectJoinEndpoint`, `StaticFileAssetEndpoint`) |
| `EmailVerificationThrottle` | `apps/api/plane/authentication/rate_limit.py` | `3/hour` | User-ID (UserRateThrottle) | `UserEndpoint.generate_email_verification_code` |
| `AuthenticationThrottle` | dito | env `AUTHENTICATION_RATE_LIMIT`, Default `10/minute` | Client-IP | `UserEndpoint.generate_email_verification_code`, `UserEndpoint.update_email` |
| `AssetRateThrottle` | `apps/api/plane/throttles/asset.py` | Scope `asset_id` = `5/minute` | `throttle_asset_{asset_id}` (pro Quell-Asset, nicht pro User!) | `DuplicateAssetEndpoint` |

Bei Überschreitung der beiden Auth-Throttles liefert `throttle_failure_view` bzw. der globale Handler 429 `{"error_code": 5900, "error_message": "RATE_LIMIT_EXCEEDED"}`.

#### 2.1.5 Hilfs-Properties der Basisklassen

| Property | `BaseViewSet` | `BaseAPIView` |
|---|---|---|
| `workspace_slug` | `kwargs["slug"]` oder `None` | identisch |
| `project_id` | `kwargs["project_id"]`; wenn nicht vorhanden **und** URL-Name == `"project"` → `kwargs["pk"]` (damit greifen Projekt-Permissions auf `projects/{pk}/`) | nur `kwargs["project_id"]` |
| `fields` | Query `?fields=a,b` → Liste oder `None` | identisch |
| `expand` | Query `?expand=a,b` → Liste oder `None` | identisch |

`fields`/`expand` werden in **diesem Bereich nicht ausgewertet** (die Views lesen `request.GET["fields"]` teils selbst und reichen es an `DynamicBaseSerializer` weiter, wo es wirkungslos ist – siehe 2.3).

#### 2.1.6 Response-Cache-Decorators (`UT/cache.py`)

| Decorator | Verhalten |
|---|---|
| `cache_response(timeout=3600, path=None, user=True)` | Schlüssel = `"{request.get_full_path()}:{user_id}"` (bei `user=True`). Cache-Hit → `Response(data, status)`. Gespeichert wird nur bei Status 200 **und** `settings.DEBUG == False`. Verwendet: `WorkspaceLabelsEndpoint.get`, `WorkspaceEstimatesEndpoint.get` (jeweils `60*60*2` = 2 h). |
| `invalidate_cache(path, url_params=False, user=True, multiple=False)` / `invalidate_cache_directly(...)` | Ersetzt `:<kwarg>` im Pfad durch URL-Parameter, Schlüssel = Pfad bzw. `Pfad:{user_id}`. `multiple=True` → `cache.delete_many(cache.keys("*<key>*"))`, sonst `cache.delete(key)`. Wird **vor** der View ausgeführt. |

**Wichtig (Edge-Case):** Die Invalidierungen dieses Bereichs treffen die Schlüssel von `cache_response` überwiegend **nicht** (z. B. `BulkEstimatePointEndpoint` invalidiert `"/api/workspaces/{slug}/estimates/"` ohne User-Suffix und ohne `multiple`, gespeichert ist aber `"/api/workspaces/{slug}/estimates/:{user_id}"`; `StateViewSet` invalidiert `"workspaces/{slug}/states/"` ohne führenden Slash für einen Endpunkt, der gar nicht gecacht wird). Effekt in Produktion: `GET {W}/estimates/` und `GET {W}/labels/` können bis zu 2 h veraltet sein. Für .NET wird **kein** Response-Caching empfohlen (siehe Abschnitt 5).

Zusätzliche HTTP-Cache-Header:
- `UserEndpoint.retrieve`, `UserEndpoint.retrieve_user_settings`, `ProfileEndpoint.get`: `Cache-Control: private, max-age=12` + `Vary: Cookie` (Django `cache_control`, `vary_on_cookie`). Das Frontend umgeht dies bei Bedarf mit `?t=<timestamp>` (`WEB/services/user.service.ts` `currentUserSettings(bustCache)`).
- `TimezoneEndpoint.get`: Django `cache_page(60*60*2)` (serverseitiger Seitencache 2 h + `Cache-Control: max-age=7200`).
- `WorkspaceDraftIssueViewSet.list`: `gzip_page` (GZip-Kompression).

### 2.2 Pagination (`UT/paginator.py`)

`BasePaginator.paginate(...)` ist in jeder View verfügbar (Mixin). Konfiguration:

| Parameter | Default | Bedeutung |
|---|---|---|
| Query `per_page` | `default_per_page` (1000, `WorkspaceStickyViewSet.list`: 20) | Seitengröße; nicht-int → 400 `Invalid per_page parameter.`; `> max(max_per_page, default_per_page)` (1000) → 400 |
| Query `cursor` | `"{per_page}:0:0"` | Format **`value:offset:is_prev`**; `value` = Seitengröße (int, bei `.` float), `offset` = **Seitenindex** (0-basiert), `is_prev` = `0`/`1`. Falsches Format → 400 `Invalid cursor parameter.` |
| `order_by` (Code) | `None` | Bei gesetztem Feld: `ORDER BY <feld> [DESC] NULLS LAST, created_at DESC` |

**Algorithmus `OffsetPaginator.get_result`:** `limit = min(per_page, 1000)`; `offset = cursor.offset * limit`; lädt `limit+1` Zeilen ab `offset`; `next.has_results = (Anzahl geladener Zeilen > limit)`; `prev.has_results = offset_page > 0`; `total_count` = `total_count_queryset.count()` oder `queryset.count()`; `total_pages = ceil(count / limit)`. Negativer Offset → 400 `Error in parsing`.

**Antwortobjekt (alle paginierten Endpunkte, exakt):**

```json
{
  "grouped_by": null,
  "sub_grouped_by": null,
  "total_count": 123,
  "next_cursor": "50:1:0",
  "prev_cursor": "50:-1:1",
  "next_page_results": true,
  "prev_page_results": false,
  "count": 50,
  "total_pages": 3,
  "total_results": 123,
  "extra_stats": null,
  "results": [ ... ]
}
```

Hinweise: `next_cursor` = `"{limit}:{page+1}:0"`, `prev_cursor` = `"{limit}:{page-1}:1"` (auch negativ auf Seite 0). `count` = Anzahl Ergebnisse der aktuellen Seite. `results` ist bei Gruppierung ein Objekt (siehe unten).

**Gruppierte Pagination** (nur `WorkspaceUserProfileIssuesEndpoint` in diesem Bereich): `GroupedOffsetPaginator` / `SubGroupedOffsetPaginator` paginieren **pro Gruppe** via `ROW_NUMBER() OVER (PARTITION BY <group> ORDER BY <key>, created_at DESC)`; `group_by`/`sub_group_by` müssen in `ISSUE_GROUP_BY_ALLOWLIST` (`UT/order_queryset.py`: `state_id`, `state__group`, `priority`, `labels__id`, `assignees__id`, `issue_module__module_id`, `cycle_id`, `project_id`, `created_by`, `target_date`, `start_date`) liegen, sonst 400. `results` = `{ "<gruppenwert>": {"results": [...], "total_results": n} }` bzw. bei Subgruppen `{ "<g>": {"results": {"<sg>": {"results": [...], "total_results": n}}, "total_results": n} }`. M2M-Gruppen (`labels__id`, `assignees__id`, `issue_module__module_id`) erzeugen Mehrfachzuordnung; Details siehe A04 (`migration/analysis/04-api-intern-arbeitsobjekte.md`), das die Paginatoren für Issue-Listen vollständig beschreibt.

**`order_by`-Allowlists** (`UT/order_queryset.py` `sanitize_order_by`: höchstens ein führendes `-`, Feld muss in der Liste sein, sonst Default):

| Konstante | Felder | Verwendet in diesem Bereich |
|---|---|---|
| `ACTIVITY_ORDER_BY_ALLOWLIST` | `created_at`, `updated_at` | `WorkspaceUserActivityEndpoint`, `UserActivityEndpoint` |
| `PROJECT_ORDER_BY_ALLOWLIST` | `created_at`, `updated_at`, `name`, `network`, `sort_order` | `ProjectViewSet.list_detail` (nur paginiert) |
| `NOTIFICATION_ORDER_BY_ALLOWLIST` | `created_at`, `updated_at` | `NotificationViewSet.list` (nur paginiert) |
| `EXPORTER_HISTORY_ORDER_BY_ALLOWLIST` | `created_at`, `updated_at` | `ExportIssuesEndpoint.get` |
| `ISSUE_ORDER_BY_ALLOWLIST` | siehe A04 | `WorkspaceUserProfileIssuesEndpoint` (via `order_issue_queryset`) |

### 2.3 Serializer-Basis (`S/base.py`)

| Klasse | Verhalten |
|---|---|
| `BaseSerializer(ModelSerializer)` | `id = PrimaryKeyRelatedField(read_only=True)` |
| `DynamicBaseSerializer(BaseSerializer)` | `__init__` entfernt `fields`-kwarg, **überschreibt die Variable aber sofort mit `self.expand`** → das `fields=`-Argument ist **wirkungslos**. `_filter_fields` fügt nur Expansions-Serializer hinzu und entfernt **nie** Felder. `to_representation`: für jedes `expand`-Feld, das in `get_expansion_mapper()` steht (`user`, `workspace`, `project`, `default_assignee`, `project_lead`, `state`, `created_by`, `updated_by`, `issue`, `actor`, `owned_by`, `members`, `assignees`, `labels`, `issue_cycle`, `parent`, `issue_relation`, `issue_intake`, `issue_related`, `issue_reactions`, `issue_link`, `sub_issues`), wird die Relation serialisiert (Manager → Liste, Model → Objekt, `None` → `null`); `issue_attachments` wird über `FileAsset` (`entity_type=ISSUE_ATTACHMENT`) geladen. |

**Konsequenz (Contract!):** Überall, wo Views `fields=(...)` übergeben (z. B. `WorkSpaceMemberViewSet.list` mit `("id","member","role")`, `WebhookEndpoint.get`), werden **alle** Serializer-Felder ausgeliefert. Das Frontend **verlässt sich darauf**: `WEB/store/member/workspace/workspace-member.store.ts` liest `member.is_active` und `member.created_at` (als `joining_date`) aus `GET {W}/members/`. Die .NET-API muss daher die **vollständigen** Feldmengen liefern, nicht die vermeintlich beschränkten. Der Kommentar in `S/webhook.py` (`to_representation`) dokumentiert das ausdrücklich.

**DRF-Verhalten bei fehlenden Annotationen:** Read-only-Felder ohne Quelle (z. B. `CycleSerializer.is_favorite`/`status`, `ModuleSerializer.is_favorite`/`total_estimate_points`/`completed_estimate_points`, `WorkSpaceSerializer.role` in `retrieve`) werden **aus der Antwort weggelassen** (`SkipField`), nicht als `null` geliefert.

**`BinaryField`-Abbildung:** Modellfelder `description_binary` (z. B. `Sticky`, `DraftIssue`) werden von DRF als `ModelField` behandelt → JSON-Wert ist ein **Base64-String** (lesend und schreibend).

### 2.4 Berechtigungen (`PERM/*`) und Hilfs-Prädikate

#### 2.4.1 Rollen

`ROLE` (Enum) existiert doppelt mit identischen Werten: `PERM/base.py` und `M/project.py`. `ADMIN = 20`, `MEMBER = 15`, `GUEST = 5`. `ROLE_CHOICES = ((20,"Admin"),(15,"Member"),(5,"Guest"))` in `M/workspace.py` und `M/project.py`. Rollen werden numerisch verglichen (`role > 5`, `role >= 15`, `role__lt=15`, `role__gt=GUEST`).

#### 2.4.2 Decorator `allow_permission(allowed_roles, level="PROJECT", creator=False, model=None)` (`PERM/base.py`)

Algorithmus (exakt in dieser Reihenfolge):

1. **Creator-Zweig** (nur wenn `creator=True` **und** `model` gesetzt):
   1. Kein aktives `WorkspaceMember` (`member=user`, `workspace__slug=kwargs["slug"]`, `is_active=True`) → 403.
   2. Wenn `level != "WORKSPACE"`: kein aktives `ProjectMember` im URL-Projekt (`project_id=kwargs["project_id"]`) → 403.
   3. Existiert `model.objects.filter(id=kwargs["pk"], created_by=user)` → **erlaubt**. Sonst weiter mit Schritt 2.
2. `allowed_role_values` = Werte der übergebenen Rollen.
3. `level == "WORKSPACE"`: aktives `WorkspaceMember` mit `role IN allowed` → erlaubt.
4. sonst (PROJECT): aktives `ProjectMember` (`workspace__slug`, `project_id`, `role IN allowed`) → erlaubt; **oder** aktives `ProjectMember` beliebiger Rolle **und** aktives `WorkspaceMember` mit Rolle 20 → erlaubt („Workspace-Admins gelten in Projekten, denen sie angehören, als Admin“).
5. Sonst 403 `{"error": "You don't have the required permissions."}`.

Fehlt `kwargs["slug"]` (bzw. `project_id`, `pk` im Creator-Zweig) → `KeyError` → 400 `{"error": "The required key does not exist."}` (relevant: W-02 `GET /api/workspaces/`).

Besonderheiten: `allowed_roles=[]` mit `creator=True` (Stickies) bedeutet „nur Ersteller“. Prüfungen laufen **zusätzlich** zu `permission_classes` (Default `IsAuthenticated`).

#### 2.4.3 Permission-Klassen

| Klasse | Quelle | anonym | sichere Methoden (GET/HEAD/OPTIONS) | POST | PUT/PATCH | DELETE |
|---|---|---|---|---|---|---|
| `WorkSpaceBasePermission` | `PERM/workspace.py` | ✗ | ✓ (jeder Authentifizierte; Scoping im Queryset) | ✓ (jeder Authentifizierte → Workspace anlegen) | aktives WS-Mitglied Rolle 20 | aktives WS-Mitglied Rolle 20 |
| `WorkspaceOwnerPermission` | `PERM/workspace.py` | ✗ | WS-Rolle 20 | WS-Rolle 20 | WS-Rolle 20 | WS-Rolle 20 |
| `WorkSpaceAdminPermission` | `PERM/workspace.py` | ✗ | WS-Rolle 20 **oder 15** (Name irreführend) | dito | dito | dito |
| `WorkspaceEntityPermission` | `PERM/workspace.py` | ✗ | jedes aktive WS-Mitglied | WS-Rolle 20/15 | WS-Rolle 20/15 | WS-Rolle 20/15 |
| `WorkspaceViewerPermission` | `PERM/workspace.py` | ✗ | jedes aktive WS-Mitglied | dito | dito | dito |
| `WorkspaceUserPermission` | `PERM/workspace.py` | ✗ | jedes aktive WS-Mitglied | dito | dito | dito |
| `WorkspaceMemberPermission` | `PERM/workspace.py` | ✗ | aktives WS-Mitglied; Workspace über `kwargs["workspace_id"]` **oder** `kwargs["slug"]`; ohne beides ✗ | dito | dito | dito |
| `ProjectBasePermission` | `PERM/project.py` | ✗ | aktives WS-Mitglied | WS-Rolle 20/15 | Projekt-Admin **oder** (Projektmitglied **und** WS-Admin) | wie PUT |
| `ProjectMemberPermission` | `PERM/project.py` | ✗ | aktives Projektmitglied (URL-Projekt) | Projektrolle 20/15 (URL-Projekt) | Projektrolle 20/15 | Projektrolle 20/15 |
| `ProjectEntityPermission` | `PERM/project.py` | ✗ | aktives Projektmitglied (bzw. via `view.project_identifier`) | Projektrolle 20/15 | Projektrolle 20/15 | Projektrolle 20/15 |
| `ProjectAdminPermission` | `PERM/project.py` | ✗ | Projekt-Admin oder (Projektmitglied & WS-Admin) | dito | dito | dito |
| `ProjectLitePermission` | `PERM/project.py` | ✗ | aktives Projektmitglied | dito | dito | dito |
| `ProjectPagePermission` | `PERM/page.py` | ✗ | siehe unten | siehe unten | siehe unten | siehe unten |

Fehlschlag einer Permission-Klasse → 403 `{"detail": "You do not have permission to perform this action."}` (DRF-Text, **nicht** der `allow_permission`-Text).

**`ProjectPagePermission`** (in diesem Bereich definiert, genutzt von Page-Views in A04): (1) anonym ✗; (2) Rolle = aktive Projektrolle im URL-Projekt, sonst ✗; (3) bei `page_id` in der URL: Page muss in `workspace__slug` liegen **und** einen aktiven `ProjectPage`-Link (`project_pages__project_id=project_id`, `project_pages__deleted_at__isnull=True`) haben, sonst ✗; Eigentümer (`owned_by`) ✓; Gast ohne `Project.guest_view_all_features` ✗; `access == 1` (privat) → `_has_private_page_action_access` liefert in CE immer ✗ (Hook für Bezahl-Feature „geteilte private Seiten“); (4) Methodenmatrix: POST → A/M; GET/HEAD/OPTIONS → A/M/G; PUT/PATCH → A/M; DELETE → **nur A**; sonst ✗.

#### 2.4.4 Hilfs-Prädikate (fachliche Sichtbarkeitsregeln)

| Funktion | Quelle | Regel |
|---|---|---|
| `_visible_issues_q(user, prefix="")` | `V/workspace/user.py` | Issue sichtbar, wenn User **aktives, nicht soft-gelöschtes** Mitglied des Issue-Projekts ist **und** (Projektrolle > 5 **oder** `project.guest_view_all_features` **oder** `issue.created_by == user`). Muss in **einem** `filter()` stehen (gleicher Join). Verwendet in Profil-Stats/-Issues/-Aktivität/-Export, `WorkspaceUserProfileEndpoint`. |
| `is_sole_admin_of_any_project(slug, user_id)` | `V/workspace/member.py` | Existiert ein (nicht soft-gelöschtes) Projekt im Workspace mit **genau einem** `ProjectMember`-Eintrag und dieser Eintrag ist der User mit Rolle 20. Die Zählung läuft per `Count("project_projectmember")` über die Relation und erfasst daher **alle** Zeilen inkl. inaktiver (`is_active=False`) und soft-gelöschter Mitgliedschaften; `is_active` des Users wird nicht geprüft. |
| `can_write_project(user, slug, project_id)` | `V/workspace/draft.py` | aktives `ProjectMember` existiert **und** (Rolle ∈ {20,15} **oder** User ist aktiver WS-Admin). |
| `can_modify_asset(user, asset)` | `V/asset/v2.py` | siehe Matrix in 3.13 |
| `get_favorite_entities(entity_type, user_id, project_id)` | `S/favorite.py` | Sichtbare Entitäten für Favoriten: aktives Mitglied des (nicht archivierten) Projekts; `page`: über aktive `ProjectPage`-Links; `project`: `id=project_id`; Pages/Views: eigene **oder** öffentliche (`page.access=0`, `view.access=1`), öffentliche aber nicht für Gäste ohne `guest_view_all_features`; Workspace-Views (`entity_type="view"`, `project_id=None`): aktives WS-Mitglied, eigene oder (öffentlich und Nicht-Gast). |

**Generelle Fallgrube (betrifft viele Views):** Filter über Relationen wie `project__project_projectmember__member=user, …__is_active=True` wenden den Soft-Delete-Manager **nicht** an. Soft-gelöschte `ProjectMember`-Zeilen (`deleted_at IS NOT NULL`) zählen dort mit, sofern nicht explizit `…__deleted_at__isnull=True` ergänzt ist (ergänzt in: `_visible_issues_q`, Suche, Analytics-Default/Legacy, Export-Task; **nicht** ergänzt in: Workspace-Labels/States/Cycles/Modules, Projektlisten, Favoriten-Filter, `get_analytics_filters`). Zusätzlich entstehen ohne `distinct()` Duplikate (z. B. `WorkspaceLabelsEndpoint`, `WorkspaceStatesEndpoint`, `WorkspaceModulesEndpoint`). Für .NET: Mitgliedschaft immer über `deleted_at IS NULL AND is_active` prüfen; Ergebnisse deduplizieren.

### 2.5 Endpunkt-Inventar Workspace (`URL/workspace.py`)

Legende Request: **B** = JSON-Body, **Q** = Query-Parameter. „Paginiert“ = Antwortobjekt aus 2.2. Spalte FE: aufrufende Frontend-Datei (`—` = vom Frontend nicht aufgerufen).

| ID | Methode & Pfad | View.Methode (Quelle) | Berechtigung | Request | Response | Seiteneffekte / Besonderheiten | FE |
|---|---|---|---|---|---|---|---|
| W-01 | `GET /api/workspace-slug-check/` | `WorkSpaceAvailabilityCheckEndpoint.get` (`V/workspace/base.py`) | authentifiziert | Q: `slug` (Pflicht) | 200 `{"status": true\|false}` (true = frei) | frei = kein nicht-gelöschter Workspace mit Slug **und** Slug ∉ `RESTRICTED_WORKSPACE_SLUGS` (`UT/constants.py`). Leer → 400 `{"error": "Workspace Slug is required"}`. Soft-gelöschte Workspaces haben umbenannten Slug (`slug__<epoch>`), ihr alter Slug ist wieder frei. | `WEB/services/workspace.service.ts` `workspaceSlugCheck`, `SVC/workspace/workspace.service.ts` |
| W-02 | `GET /api/workspaces/` | `WorkSpaceViewSet.list` (`V/workspace/base.py`) | `WorkSpaceBasePermission` + `allow_permission([A,M,G], WORKSPACE)` | Q: `search` (name), `owner` | **immer 400** `{"error": "The required key does not exist."}` | `allow_permission` greift auf `kwargs["slug"]` zu, das in dieser Route fehlt → `KeyError`. Endpunkt faktisch tot; Workspace-Liste kommt aus U-17. | — |
| W-03 | `POST /api/workspaces/` | `WorkSpaceViewSet.create` | `WorkSpaceBasePermission` (jeder Authentifizierte) | B: `name` (Pflicht, ≤ 80, keine URL, ≥ 1 alphanumerisches Zeichen), `slug` (Pflicht, ≤ 48, `^[a-zA-Z0-9_-]+$`, nicht reserviert, eindeutig), optional `organization_size`, `timezone`, `background_color`, `logo`, `logo_asset`, `company_role` (→ Mitgliedseintrag) | 201 WorkSpaceSerializer-Felder + `total_members` (int) + `role: 20` | Reihenfolge: (1) `DISABLE_WORKSPACE_CREATION == "1"` (Instanz-Config/ENV) → 403 `{"error": "Workspace creation is not allowed"}`; (2) fehlend → 400 `{"error": "Both name and slug are required"}`; (3) Länge → 400 `{"error": "The maximum length for name is 80 and for slug is 48"}`; (4) URL im Namen → 400 `{"error": "Name cannot contain a URL"}`; (5) Serializer (`raise_exception=True` → DRF-Feldfehler, z. B. `{"name": ["Name must not contain URLs"]}`, `{"name": ["Name must contain at least one letter or number"]}`, `{"slug": ["Slug is not valid"]}`, `{"slug": ["Slug can only contain letters, numbers, hyphens (-), and underscores (_)"]}`); (6) `IntegrityError` mit „already exists“ → **409** `{"slug": "The workspace with the slug already exists"}`. Danach: `owner = user`; `WorkspaceMember(role=20, company_role)`; Celery `workspace_seed.delay(workspace_id)` (`BG/workspace_seed_task.py`: Bot-User „Plane“, Demo-Projekt mit States/Labels/Cycles/Modules/Issues/Pages/Views). | `WEB/services/workspace.service.ts` `createWorkspace` |
| W-04 | `GET /api/workspaces/{slug}/` | `WorkSpaceViewSet.retrieve` (DRF-Default, `lookup_field="slug"`) | `WorkSpaceBasePermission` (GET ✓) | – | 200 WorkSpaceSerializer + `total_members` (ohne `role`, da nicht annotiert) | Queryset nur Workspaces mit aktiver Mitgliedschaft des Users, `total_members` = aktive Nicht-Bot-Mitglieder. Nicht-Mitglied → 404 (DRF `{"detail": …}`). | `WEB/services/workspace.service.ts` `getWorkspace` |
| W-05 | `PUT /api/workspaces/{slug}/` | `WorkSpaceViewSet.update` (DRF-Default) | `WorkSpaceBasePermission` (WS-Admin) | B: alle Pflichtfelder (`name`, `slug`, …) | 200 WorkSpaceSerializer | Vollupdate inkl. `slug`. | — |
| W-06 | `PATCH /api/workspaces/{slug}/` | `WorkSpaceViewSet.partial_update` | `allow_permission([A], WORKSPACE)` + `WorkSpaceBasePermission` | B: beliebige beschreibbare Workspace-Felder: `name`, `slug`, `logo`, `logo_asset`, `organization_size`, `timezone` (pytz `common_timezones`), `background_color` | 200 WorkSpaceSerializer + `total_members` | Validierungen wie W-03 (Serializer). **`slug` ist änderbar** (kein Schutz). | `WEB/services/workspace.service.ts` `updateWorkspace` |
| W-07 | `DELETE /api/workspaces/{slug}/` | `WorkSpaceViewSet.destroy` | `allow_permission([A], WORKSPACE)` | – | 204 | (1) alle `Profile.last_workspace_id == id` → `NULL`; (2) Soft-Delete (`deleted_at`), danach Slug → `"{slug}__{int(deleted_at.timestamp())}"` (`M/workspace.py` `Workspace.delete`); (3) Celery `soft_delete_related_objects` (`BG/deletion_task.py`) kaskadiert rekursiv über alle Reverse-Relationen (CASCADE → soft delete, SET_NULL → NULL setzen, DO_NOTHING → nichts). | `WEB/services/workspace.service.ts` `deleteWorkspace` |
| W-08 | `GET {W}/invitations/` | `WorkspaceInvitationsViewset.list` (DRF-Default) | `WorkSpaceAdminPermission` (A/M) | – | 200 `[WorkSpaceMemberInviteSerializer]` (unpaginiert) | enthält `token` und `invite_link` (`/workspace-invitations/?invitation_id={id}&slug={slug}&token={token}`). | `WEB/services/workspace.service.ts` `workspaceInvitations` |
| W-09 | `POST {W}/invitations/` | `WorkspaceInvitationsViewset.create` | `WorkSpaceAdminPermission` (A/M) | B: `emails: [{"email": str, "role": 5\|15\|20}]` (role Default 5) | 200 `{"message": "Emails sent successfully"}` | Fehler: leer → 400 `{"error": "Emails are required"}`; `int(role) > eigene WS-Rolle` → 400 `{"error": "You cannot invite a user with higher role"}`; E-Mail gehört aktivem Mitglied → 400 `{"error": "Some users are already member of workspace", "workspace_users": [WorkSpaceMemberSerializer…]}`; ungültige E-Mail → 400 `{"error": "Invalid email - {email} provided a valid email address is required to send the invite"}` (`{email}` = Python-Dict-Darstellung des Eintrags). E-Mail wird `strip().lower()` gespeichert; `token` = JWT HS256 (`SECRET_KEY`) über `{"email": <dict>, "timestamp": now}`. `bulk_create(ignore_conflicts=True)` → bestehende offene Einladung derselben E-Mail wird **still ignoriert**. Pro Eintrag Celery `workspace_invitation.delay(email, workspace_id, token, current_site, inviter_email)` (`BG/workspace_invitation_task.py`, E-Mail-Template `emails/invitations/workspace_invitation.html`, Betreff „{Vorname/Displayname/E-Mail} has invited you to join them in {Workspace} on Plane“); bei ignorierten Konflikten findet der Task die Einladung nicht und bricht still ab. `role` wird nicht gegen die Choices validiert. | `WEB/services/workspace.service.ts` `inviteWorkspace` |
| W-10 | `GET {W}/invitations/{pk}/` | `WorkspaceInvitationsViewset.retrieve` (DRF-Default) | A/M | – | 200 WorkSpaceMemberInviteSerializer | – | — |
| W-11 | `PATCH {W}/invitations/{pk}/` | `WorkspaceInvitationsViewset.partial_update` | A/M | B: **genau** `{"role": int}` | 200 WorkSpaceMemberInviteSerializer | andere/zusätzliche Keys → 400 `{"error": "Only the role of an invitation can be updated"}`; Rolle > eigene → 400 `{"error": "You cannot invite a user with higher role"}`. | `WEB/services/workspace.service.ts` `updateWorkspaceInvitation` |
| W-12 | `DELETE {W}/invitations/{pk}/` | `WorkspaceInvitationsViewset.destroy` | A/M | – | 204 | Soft-Delete der Einladung. | `WEB/services/workspace.service.ts` `deleteWorkspaceInvitations` |
| W-13 | `GET /api/users/me/workspaces/invitations/` | `UserWorkspaceInvitationsViewSet.list` (DRF-Default) | authentifiziert | – | 200 `[WorkSpaceMemberInviteSerializer]` | alle offenen Einladungen mit `email == user.email` (exakter Vergleich, Einladungs-E-Mail ist lowercase, User-E-Mail ebenfalls durch `User.save`). | `WEB/services/workspace.service.ts` `userWorkspaceInvitations` |
| W-14 | `POST /api/users/me/workspaces/invitations/` | `UserWorkspaceInvitationsViewSet.create` | authentifiziert | B: `invitations: [invite_id…]` | 204 | Nur Einladungen mit `email == user.email`. Pro Einladung: Cache-Invalidierung `"/api/workspaces/{slug}/members/"` (multiple); vorhandene (auch inaktive) Mitgliedschaft → `is_active=True, role=invite.role`; danach `bulk_create(WorkspaceMember(role=invite.role, created_by=user), ignore_conflicts=True)`; Einladungen soft-gelöscht. Keine Prüfung von `accepted`/`responded_at`; `last_workspace_id` wird **nicht** gesetzt. | `WEB/services/workspace.service.ts` `joinWorkspaces` |
| W-15 | `POST {W}/invitations/{pk}/join/` | `WorkspaceJoinEndpoint.post` | `AllowAny` + eigene Prüfung | B: `token` (Pflicht), `accepted` (bool, Default false) | 200 `{"message": "Workspace Invitation Accepted"}` bzw. `{"message": "Workspace Invitation was not accepted"}` | Reihenfolge: Token fehlt/≠ → 403 `{"error": "You do not have permission to join the workspace"}`; nicht angemeldet → **401** `{"error": "Authentication required to accept workspace invitation"}`; `user.email.lower() != invite.email.lower()` → 403 `{"error": "You do not have permission to accept this invitation"}`; bereits beantwortet → 400 `{"error": "You have already responded to the invitation request"}`. Sonst `accepted`, `responded_at=now` speichern; bei `accepted`: Mitgliedschaft reaktivieren (`is_active=True`, `role=invite.role`) oder anlegen; `user.last_workspace_id = …; user.save()` (**wirkungslos**, Feld existiert nur auf `Profile`); Einladung soft-löschen. Bei Ablehnung bleibt die Einladung bestehen (mit `responded_at`). Cache-Invalidierungen: `/api/workspaces/`, `/api/users/me/workspaces/` (multiple), `/api/workspaces/:slug/members/` (multiple), `/api/users/me/settings/` (multiple). | `WEB/services/workspace.service.ts` `joinWorkspace`, `SVC/workspace/invitation.service.ts` |
| W-16 | `GET {W}/invitations/{pk}/join/` | `WorkspaceJoinEndpoint.get` | `AllowAny` | – | 200 WorkSpaceMemberInvitePublicSerializer (`id, email, workspace{name,slug,id,logo_url}, role, message, accepted, responded_at, created_at, updated_at, created_by`) | **ohne** `token`/`invite_link` (GHSA-86mg-259g-pwgg). Unbekannt → 404 `{"error": "The required object does not exist."}`. | `WEB/services/workspace.service.ts` `getWorkspaceInvitation` |
| W-17 | `GET {W}/members/` | `WorkSpaceMemberViewSet.list` (`V/workspace/member.py`) | `allow_permission([A,M,G], WORKSPACE)` | Q: `search` (`member__display_name`, `member__first_name`, icontains) | 200 `[WorkspaceMember-Objekt]` (unpaginiert) | **Alle** Mitgliedschaften des Workspaces inkl. **inaktiver** (`is_active=false`) und Bot-User (Seed-Bot). Anfragender Rolle > 5 → `WorkspaceMemberAdminSerializer` (`member` = UserAdminLite inkl. `email`, `last_login_medium`), Gast → `WorkSpaceMemberSerializer` (`member` = UserLite). `fields=("id","member","role")` ist wirkungslos → alle WorkspaceMember-Felder. | `WEB/services/workspace.service.ts` `fetchWorkspaceMembers` |
| W-18 | `GET {W}/project-members/` | `WorkspaceProjectMemberEndpoint.get` | `WorkspaceEntityPermission` | – | 200 `{"<project_id>": [{"id","role","member","original_role","created_at"}]}` | Projekte = alle Projekte (workspace-übergreifend), in denen der User aktives Mitglied ist, gefiltert auf `workspace__slug`; je Projekt alle aktiven Mitglieder (inkl. Bots). | — |
| W-19 | `GET {W}/members/{pk}/` | `WorkSpaceMemberViewSet.retrieve` | `allow_permission([A,M,G], WORKSPACE)` | `pk` = **WorkspaceMember-ID** | 200 wie W-17 (ein Objekt) | nicht gefunden → 404 `{"error": "Workspace member not found"}`. | — |
| W-20 | `PATCH {W}/members/{pk}/` | `WorkSpaceMemberViewSet.partial_update` | `allow_permission([A], WORKSPACE)` | B: **genau** `{"role": 5\|15\|20}` | 200 WorkSpaceMemberSerializer (`member` = UserLite) | Ziel muss aktiv und kein Bot sein (sonst 404 `The required object does not exist.`). Eigene Rolle → 400 `{"error": "You cannot update your own role"}`; andere Keys → 400 `{"error": "Only the role of a workspace member can be updated"}`; Serializer-Fehler → 400 (z. B. `{"role": ["\"7\" is not a valid choice."]}`); Herabstufung zu Gast und `is_sole_admin_of_any_project` → 400 `{"error": "User is a part of some projects where they are the only admin, they should either leave that project or promote another user to admin."}`. Transaktion: bei Gast werden **alle** `ProjectMember` des Users im Workspace (auch inaktive) auf Rolle 5 gesetzt; dann `save(update_fields=["role","updated_at","updated_by"])`. Admins dürfen andere Admins herabstufen. | `WEB/services/workspace.service.ts` `updateWorkspaceMember`, `SVC/workspace/member.service.ts` |
| W-21 | `DELETE {W}/members/{pk}/` | `WorkSpaceMemberViewSet.destroy` | `allow_permission([A], WORKSPACE)` | – | 204 | Ziel aktiv & kein Bot (sonst 404). Sich selbst → 400 `{"error": "You cannot remove yourself from the workspace. Please use leave workspace"}`; Ziel-Rolle > eigene → 400 `{"error": "You cannot remove a user having role higher than you"}`; einziger Admin eines Projekts → 400 (Text wie W-20). Effekt: alle aktiven `ProjectMember` des Users im Workspace → `is_active=False`; `WorkspaceMember.is_active=False` (kein Löschen). | `WEB/services/workspace.service.ts` `deleteWorkspaceMember` |
| W-22 | `POST {W}/members/leave/` | `WorkSpaceMemberViewSet.leave` | `allow_permission([A,M,G], WORKSPACE)` | – | 204 | Letzter aktiver Admin → 400 `{"error": "You cannot leave the workspace as you are the only admin of the workspace you will have to either delete the workspace or promote another user to admin."}`; einziger Projekt-Admin → 400 `{"error": "You are a part of some projects where you are the only admin, you should either leave the project or promote another user to admin."}`. Effekt wie W-21 für sich selbst. Cache-Invalidierung `/api/workspaces/:slug/members/` (multiple), `/api/users/me/settings/`, `api/users/me/workspaces/` (multiple). | `WEB/services/user.service.ts` `leaveWorkspace` |
| W-23 | `GET /api/users/last-visited-workspace/` | `UserLastProjectWithWorkspaceEndpoint.get` (`V/workspace/user.py`) | authentifiziert | – | **immer 500** | Liest `User.last_workspace_id`, das nicht existiert (Feld liegt auf `Profile`) → `AttributeError`. Vorgesehen: `{"workspace_details": WorkSpaceSerializer, "project_details": [ProjectMemberSerializer]}` bzw. `{"project_details": [], "workspace_details": {}}`. | `WEB/services/workspace.service.ts` `getLastActiveWorkspaceAndProjects` (definiert, aber nirgends aufgerufen) |
| W-24 | `GET {W}/workspace-members/me/` | `WorkspaceMemberUserEndpoint.get` | authentifiziert | – | 200 alle WorkspaceMember-Felder + `draft_issue_count` (int, eigene Drafts im Workspace, Coalesce 0) | Nicht-Mitglied: `.first()` = `None` → Serializer liefert ein Objekt aus Initialwerten (kein Fehler!). | `WEB/services/workspace.service.ts` `workspaceMemberMe`, `SVC/workspace/member.service.ts` |
| W-25 | `POST {W}/workspace-views/` | `WorkspaceMemberUserViewsEndpoint.post` | authentifiziert (Mitgliedschaft per `get` → sonst 404) | B: `view_props` (JSON; fehlt → `{}`) | 204 | überschreibt `WorkspaceMember.view_props` vollständig. | `WEB/services/workspace.service.ts` `updateWorkspaceView` |
| W-26 | `GET {W}/workspace-themes/` | `WorkspaceThemeViewSet.list` (DRF-Default) | `WorkSpaceAdminPermission` (A/M) | – | 200 `[WorkspaceThemeSerializer]` | – | — |
| W-27 | `POST {W}/workspace-themes/` | `WorkspaceThemeViewSet.create` | A/M | B: `name` (Pflicht, ≤ 300), `colors` (JSON) | 201 WorkspaceThemeSerializer | `workspace`, `actor = user`. Doppelter Name → `IntegrityError` → 400 `{"error": "The payload is not valid"}`. Serializer-Fehler → 400 Feldfehler. | — |
| W-28 | `GET {W}/workspace-themes/{pk}/` | `WorkspaceThemeViewSet.retrieve` | A/M | – | 200 | – | — |
| W-29 | `PATCH {W}/workspace-themes/{pk}/` | `WorkspaceThemeViewSet.partial_update` | A/M | B: `name`, `colors` | 200 | – | — |
| W-30 | `DELETE {W}/workspace-themes/{pk}/` | `WorkspaceThemeViewSet.destroy` | A/M | – | 204 | Soft-Delete. | — |
| W-31 | `GET {W}/user-stats/{user_id}/` | `WorkspaceUserProfileStatsEndpoint.get` (`V/workspace/user.py`) | `WorkspaceViewerPermission` | Q: Legacy-Issue-Filter (`issue_filters`, siehe 3.4.1) | 200 `{"state_distribution": [{"state_group","state_count"}], "priority_distribution": [{"priority","priority_count","priority_order"}], "created_issues": int, "assigned_issues": int, "completed_issues": int, "pending_issues": int, "subscribed_issues": int, "present_cycles": [{"cycle__name","cycle__id","cycle__project_id"}], "upcoming_cycles": [...]}` | Alle Zählungen nur über für den **Anfragenden** sichtbare Issues (`_visible_issues_q`) und `Issue.issue_objects` (ohne Archiv/Draft/Triage-Intake, siehe A04). Zuweisungen mit `issue_assignee__deleted_at IS NULL`. `priority_order`: urgent=0, high=1, medium=2, low=3, none=4. `pending` = State-Gruppe ∉ {completed, cancelled}. `subscribed_issues` nur nicht archivierte Projekte. Cycles: Issue zugewiesen an Ziel-User, Cycle im Issue-Projekt; „present“ = `start_date < now < end_date`, „upcoming“ = `start_date > now` (Duplikate möglich). Ziel-User muss nicht Mitglied sein. | `WEB/services/user.service.ts` |
| W-32 | `GET {W}/user-activity/{user_id}/` | `WorkspaceUserActivityEndpoint.get` | `WorkspaceEntityPermission` | Q: `project` (mehrfach), `order_by` (`ACTIVITY_ORDER_BY_ALLOWLIST`, Default `-created_at`), `per_page`, `cursor` | 200 paginiert, `results` = `[IssueActivitySerializer]` | `actor = user_id`, Felder ≠ `comment`, `vote`, `reaction`, `draft`; Projekt nicht archiviert; nur sichtbare Issues des Anfragenden. | `WEB/services/user.service.ts` |
| W-33 | `POST {W}/user-activity/{user_id}/export/` | `ExportWorkspaceUserActivityEndpoint.post` | `WorkspaceEntityPermission` (POST → A/M) | B: `date` (`YYYY-MM-DD`, Pflicht) | 200 `text/csv`, `Content-Disposition: attachment; filename="workspace-user-activity.csv"` | fehlt → 400 `{"error": "Date is required"}`. Max. 10 000 Zeilen, `QUOTE_ALL`, Zeilen durch `sanitize_csv_row` (`UT/csv_utils.py`, CSV-Injection-Schutz). Spalten: `Actor name` (display_name), `Issue ID` (`"{identifier} - {sequence_id}"`), `Project`, `Created at`, `Updated at`, `Action` (verb), `Field`, `Old value`, `New value`. `created_at__date` in **Benutzerzeitzone**. Archivierte Projekte werden hier **nicht** ausgeschlossen. | `WEB/services/user.service.ts` |
| W-34 | `GET {W}/user-profile/{user_id}/` | `WorkspaceUserProfileEndpoint.get` | authentifiziert; Anfragender **und** Ziel müssen aktive WS-Mitglieder sein (sonst 404 `The required object does not exist.`) | – | 200 `{"project_data": [{"id","logo_props","created_issues","assigned_issues","completed_issues","pending_issues"}], "user_data": {"email","first_name","last_name","avatar_url","cover_image_url","date_joined","user_timezone","display_name"}}` | `project_data` nur, wenn Anfragender Rolle ≥ 15; Projekte = nicht archivierte Projekte, in denen der **Anfragende** aktives Mitglied ist; Zählungen nur über für ihn sichtbare Issues (Rolle > Gast oder `guest_view_all_features` oder selbst erstellt), ohne Archiv/Draft. `completed_issues` = `completed_at IS NOT NULL`; `pending_issues` = State-Gruppe ∈ {backlog, unstarted, started}. | `WEB/store/user/profile.store.ts`, `WEB/app/(all)/[workspaceSlug]/(projects)/profile/[userId]/layout.tsx` |
| W-35 | `GET {W}/user-issues/{user_id}/` | `WorkspaceUserProfileIssuesEndpoint.get` | `WorkspaceViewerPermission` | Q: `filters` (JSON für `ComplexFilterBackend`/`IssueFilterSet`, `UT/filters/*`), Legacy-Filter (`issue_filters`), `order_by` (Default `-created_at`, `ISSUE_ORDER_BY_ALLOWLIST`), `group_by`, `sub_group_by`, `per_page`, `cursor` | 200 paginiert (ggf. gruppiert); Ergebnis-Elemente = Issue-Wertobjekte aus `issue_on_results` (`UT/grouper.py`): `id, name, state_id, sort_order, completed_at, estimate_point, priority, start_date, target_date, sequence_id, project_id, parent_id, cycle_id, sub_issues_count, created_at, updated_at, created_by, updated_by, attachment_count, link_count, is_draft, archived_at, state__group, assignee_ids, label_ids, module_ids` | Issues, bei denen Ziel-User zugewiesen, Ersteller oder Abonnent ist, sichtbar für Anfragenden. `group_by == sub_group_by` → 400 `{"error": "Group by and sub group by cannot have same parameters"}`. `count_filter` der Gruppen: Intake-Status ∈ {1,-1,2} oder kein Intake, nicht archiviert, kein Draft. | `WEB/store/issue/profile/issue.store.ts` |
| W-36 | `GET {W}/labels/` | `WorkspaceLabelsEndpoint.get` | `WorkspaceViewerPermission` | – | 200 `[LabelSerializer]` (`parent, name, color, id, project_id, workspace_id, sort_order`) | Labels aller nicht archivierten Projekte mit aktiver Mitgliedschaft; **gecacht 2 h pro User** (nur Prod), Invalidierung siehe 2.1.6; kein `distinct`. | `WEB/services/issue/issue_label.service.ts` |
| W-37 | `GET {W}/user-properties/` | `WorkspaceUserPropertiesEndpoint.get` | `WorkspaceViewerPermission` | – | 200 WorkspaceUserPropertiesSerializer | `get_or_create` (legt Defaults an, siehe 2.13). | `WEB/services/workspace.service.ts` `fetchWorkspaceFilters` |
| W-38 | `PATCH {W}/user-properties/` | `WorkspaceUserPropertiesEndpoint.patch` | `WorkspaceViewerPermission` | B: `filters`, `display_filters`, `display_properties`, `rich_filters`, `navigation_project_limit` (int), `navigation_control_preference` (`ACCORDION`\|`TABBED`) | 200 WorkspaceUserPropertiesSerializer | JSON-Felder werden **ersetzt**, nicht gemergt. | `WEB/services/workspace.service.ts` `patchWorkspaceFilters` |
| W-39 | `GET {W}/states/` | `WorkspaceStatesEndpoint.get` | `WorkspaceEntityPermission` | – | 200 `[StateSerializer]` inkl. berechnetem `order` | States (`is_triage=False`, Gruppe ≠ triage) aller nicht archivierten Projekte mit Mitgliedschaft; `order` = `index/anzahl` innerhalb der State-Gruppe (Reihenfolge = Queryset-Reihenfolge `sequence`, aber über alle Projekte gemischt). | `WEB/services/project/project-state.service.ts` |
| W-40 | `GET {W}/estimates/` | `WorkspaceEstimatesEndpoint.get` | `WorkspaceEntityPermission` | – | 200 `[WorkspaceEstimateSerializer]` (Estimate-Felder + `points: [EstimatePoint]`) | alle **aktiven** Estimates (`Project.estimate`) **aller** Projekte des Workspaces (keine Mitgliedschaftsprüfung). Gecacht 2 h pro User. | `WEB/services/estimate.service.ts` |
| W-41 | `GET {W}/modules/` | `WorkspaceModulesEndpoint.get` | `WorkspaceViewerPermission` | – | 200 `[ModuleSerializer]` (ohne `is_favorite`, `total_estimate_points`, `completed_estimate_points`) | nicht archivierte Module nicht archivierter Mitgliedsprojekte; Zähler `total_issues`, `completed_issues`, `cancelled_issues`, `started_issues`, `unstarted_issues`, `backlog_issues` (distinct, ohne archivierte/Draft-Issues, ohne soft-gelöschte Zuordnungen), `member_ids`; Sortierung **immer** `-created_at` (`self.kwargs.get("order_by")` ist nie gesetzt). | `WEB/services/module.service.ts` |
| W-42 | `GET {W}/cycles/` | `WorkspaceCyclesEndpoint.get` | `WorkspaceViewerPermission` | – | 200 `[CycleSerializer]` (ohne `is_favorite`, `status`) | wie W-41 für Cycles (Zähler ohne `distinct` aber mit `.distinct()` auf Queryset), Sortierung `-created_at`. | `WEB/services/cycle.service.ts` |
| W-43 | `GET {W}/user-favorites/` | `WorkspaceFavoriteEndpoint.get` (`V/workspace/favorite.py`) | `allow_permission([A,M], WORKSPACE)` (**Gäste 403**) | – | 200 `[UserFavoriteSerializer]` | nur Top-Level (`parent IS NULL`) des Users; Filter: (`project IS NULL` und `entity_type != "page"`) **oder** (`project` gesetzt und User aktives Projektmitglied). `entity_data` siehe 2.12. | `WEB/services/favorite/favorite.service.ts`, `SVC/user/favorite.service.ts` |
| W-44 | `POST {W}/user-favorites/` | `WorkspaceFavoriteEndpoint.post` | A/M | B: `entity_type` (`project`\|`cycle`\|`module`\|`view`\|`page`\|`issue`\|`folder`), `entity_identifier` (UUID, bei folder leer), `name` (Ordnername), `is_folder`, `sequence`, `parent` (Ordner-ID), `project_id` | **200** UserFavoriteSerializer (auch bei Neuanlage) | Existiert bereits (`entity_type`+`entity_identifier` des Users) → 200 bestehender Favorit. Für Entity-Typen mit Modell: Entität muss in diesem Workspace und sichtbar sein (`get_favorite_entities(...).get(pk, workspace)`) → sonst 404 `{"error": "The required object does not exist."}`. `sequence` beim Anlegen = max(`sequence` im Workspace) + 10000 (`M/favorite.py` `save`). `IntegrityError` → 400 `{"error": "Favorite already exists"}`. | wie W-43 |
| W-45 | `PATCH {W}/user-favorites/{favorite_id}/` | `WorkspaceFavoriteEndpoint.patch` | A/M | B: nur `name`, `sequence`, `parent` (andere Keys ignoriert) | 200 UserFavoriteSerializer | nur eigene Favoriten (sonst 404). | wie W-43 |
| W-46 | `DELETE {W}/user-favorites/{favorite_id}/` | `WorkspaceFavoriteEndpoint.delete` | A/M | – | 204 | **Hard-Delete** (`delete(soft=False)`) → DB-Kaskade löscht Kinder eines Ordners. | wie W-43 |
| W-47 | `GET {W}/user-favorites/{favorite_id}/group/` | `WorkspaceFavoriteGroupEndpoint.get` | A/M | – | 200 `[UserFavoriteSerializer]` | Kinder eines Ordners (`parent_id`), Projektfilter wie W-43 (ohne page-Ausschluss). | wie W-43 |
| W-48 | `GET {W}/draft-issues/` | `WorkspaceDraftIssueViewSet.list` (`V/workspace/draft.py`) | `allow_permission([A,M,G], WORKSPACE)`; `gzip_page` | Q: Legacy-Issue-Filter, `per_page` (Default 1000), `cursor` | 200 paginiert, `results` = `[DraftIssueSerializer]` | nur eigene Drafts (`created_by=user`), sortiert `-created_at`. | `WEB/services/issue/workspace_draft.service.ts` |
| W-49 | `POST {W}/draft-issues/` | `WorkspaceDraftIssueViewSet.create` | A/M/G (WS) + bei `project_id` `can_write_project` (sonst 403 `{"error": "You don't have the required permissions."}`) | B: `project_id`, `name`, `description_html`, `description_binary` (Base64), `description_json`, `priority` (`urgent`\|`high`\|`medium`\|`low`\|`none`), `start_date`, `target_date`, `state_id`, `parent_id`, `estimate_point`, `label_ids[]`, `assignee_ids[]`, `cycle_id`, `module_ids[]`, `sort_order`, `type`, `completed_at`, `external_source`, `external_id` | 201 Wertobjekt: `id, name, state_id, sort_order, completed_at, estimate_point, priority, start_date, target_date, project_id, parent_id, cycle_id, module_ids, label_ids, assignee_ids, created_at, updated_at, created_by, updated_by, type_id, description_html` | Validierung `DraftIssueCreateSerializer` (2.12). `state` leer → Default-State bzw. erster State des Projekts (`M/draft.py` `save`); `completed_at` = now bei completed-State; `sort_order` = max im (Projekt, State) + 10000. Assignees werden auf aktive Projektmitglieder mit Rolle ≥ 15 gefiltert, Labels auf Projekt-Labels (still). | `WEB/services/issue/workspace_draft.service.ts` |
| W-50 | `GET {W}/draft-issues/{pk}/` | `WorkspaceDraftIssueViewSet.retrieve` | `allow_permission([A], creator=True, model=Issue, WORKSPACE)` | – | 200 DraftIssueDetailSerializer | **Bug:** Creator-Prüfung gegen `Issue` statt `DraftIssue` → nie erfüllt → nur **Workspace-Admins** (und nur eigene Drafts wegen `created_by`-Filter). Nicht gefunden → 404 `{"error": "The required object does not exist."}`. | `WEB/services/issue/workspace_draft.service.ts` `getIssue` (vom Store nicht verwendet) |
| W-51 | `PATCH {W}/draft-issues/{pk}/` | `WorkspaceDraftIssueViewSet.partial_update` | `allow_permission([A,M], creator=True, model=Issue, WORKSPACE)` (Creator-Zweig wirkungslos) | B: wie W-49 (Projekt kann **nicht** geändert werden) | **204** ohne Body | eigener Draft (sonst 404 `{"error": "Issue not found"}`); `can_write_project` für Draft-Projekt und ggf. übergebenes `project_id`; Validierung gegen Draft-Projekt; `assignee_ids`/`label_ids`/`module_ids` ersetzen vollständig (Delete + Insert), `cycle_id` nur wenn im Body (auch `null` entfernt Cycle). | `WEB/services/issue/workspace_draft.service.ts` |
| W-52 | `DELETE {W}/draft-issues/{pk}/` | `WorkspaceDraftIssueViewSet.destroy` | `allow_permission([A], creator=True, model=DraftIssue, WORKSPACE)` | – | 204 | Ersteller **oder** WS-Admin; Admin kann **jeden** Draft des Workspaces löschen (kein `created_by`-Filter). Soft-Delete. | `WEB/services/issue/workspace_draft.service.ts` |
| W-53 | `POST {W}/draft-to-issue/{draft_id}/` | `WorkspaceDraftIssueViewSet.create_draft_to_issue` | `allow_permission([A,M], WORKSPACE)` + eigener Draft + `can_write_project` | B: Issue-Felder (`IssueCreateSerializer`, siehe A04), zusätzlich `cycle_id`, `module_ids[]` | 201 IssueCreateSerializer-Daten | Fehler: nicht eigener/fehlender Draft → 404 `{"error": "The required object does not exist."}`; Draft ohne Projekt → 400 `{"error": "Project is required to create an issue."}`; Cycle/Module nicht im Projekt → 400 `["Cycle is not valid please pass a valid cycle_id"]` / `["Modules are not valid please pass valid module_ids"]`. Effekte: Issue anlegen (Default-Assignee des Projekts), Celery `issue_activity("issue.activity.created", notification=True)`, ggf. `CycleIssue` + Activity `cycle.activity.created` (mit `project_id="None"` – Bug), `ModuleIssue`-Bulk + je Modul `module.activity.created`; `FileAsset` mit `draft_issue_id` → `issue_id`, `entity_type=ISSUE_DESCRIPTION`; Draft soft-löschen. | `WEB/services/issue/workspace_draft.service.ts` `moveIssue` |
| W-54 | `GET {W}/quick-links/` | `QuickLinkViewSet.list` (`V/workspace/quick_link.py`) | A/M/G (WS) | – | 200 `[WorkspaceUserLinkSerializer]` | nur eigene Links (`owner=user`), Sortierung `-created_at`. | `WEB/services/workspace.service.ts` `fetchWorkspaceLinks` |
| W-55 | `POST {W}/quick-links/` | `QuickLinkViewSet.create` | A/M/G | B: `url` (Pflicht), `title`, `metadata` | 201 | URL ohne `http(s)://` → `http://` vorangestellt; Django-`URLValidator` → 400 `{"url": {"error": "Invalid URL format."}}`; gleiche URL für (Workspace, Owner) → 400 `{"error": "URL already exists for this workspace and owner"}`. | `WEB/services/workspace.service.ts` |
| W-56 | `GET {W}/quick-links/{pk}/` | `QuickLinkViewSet.retrieve` | A/M/G | – | 200 / 404 `{"error": "Quick link not found."}` | nur eigene. | — |
| W-57 | `PATCH {W}/quick-links/{pk}/` | `QuickLinkViewSet.partial_update` | A/M/G | B: `title`, `url`, `metadata` | 200 / 404 `{"detail": "Quick link not found."}` (Achtung: `detail` statt `error`) | Duplikatprüfung wie W-55 (exkl. sich selbst). | `WEB/services/workspace.service.ts` |
| W-58 | `DELETE {W}/quick-links/{pk}/` | `QuickLinkViewSet.destroy` | A/M/G | – | 204 / 404 `The required object does not exist.` | Soft-Delete. | `WEB/services/workspace.service.ts` |
| W-59 | `GET {W}/home-preferences/` | `WorkspaceHomePreferenceViewSet.get` (`V/workspace/home.py`) | A/M/G (WS) | – | 200 `[{"key","is_enabled","config","sort_order"}]` | Seeding fehlender Keys (alle `HomeWidgetKeys` außer `quick_tutorial`, `new_at_plane` → effektiv `quick_links`, `recents`, `my_stickies`) mit `is_enabled=True`, `sort_order` 999, 998, 997 in Reihenfolge der fehlenden Keys (`ignore_conflicts`). Sortierung der Antwort: Model-Default `-created_at`. | `WEB/services/workspace.service.ts` `fetchWorkspaceWidgets` |
| W-60 | `PATCH {W}/home-preferences/{key}/` | `WorkspaceHomePreferenceViewSet.patch` | A/M/G | B: `is_enabled`, `sort_order` (auch `key` beschreibbar; `config` **nicht**) | 200 `{"key","is_enabled","sort_order"}` | unbekannter Key → **400** `{"detail": "Preference not found"}`. | `WEB/services/workspace.service.ts` `updateWorkspaceWidget` |
| W-61 | `GET {W}/recent-visits/` | `UserRecentVisitViewSet.list` (`V/workspace/recent_visit.py`) | A/M/G | Q: `entity_name` (`issue`\|`page`\|`project`) | 200 `[{"id","entity_name","entity_identifier","entity_data","visited_at"}]` (max. 20) | nur `entity_name ∈ {issue,page,project}`; Sortierung Model-Default **`-created_at`** (erster Besuch), nicht `visited_at`. `entity_data`: Issue → `{id,name,state,priority,assignees[ids],type,sequence_id,project_id,project_identifier}`, Project → `{id,name,logo_props,project_members[ids],identifier}`, Page → `{id,name,logo_props,project_id,owned_by,project_identifier}`, gelöscht → `null`. Kein Berechtigungsfilter auf `entity_data`. | `WEB/services/workspace.service.ts` `fetchWorkspaceRecents` |
| W-62 | `GET {W}/stickies/` | `WorkspaceStickyViewSet.list` (`V/workspace/sticky.py`) | A/M/G | Q: `query` (icontains auf `description_stripped`), `per_page` (Default **20**), `cursor` | 200 paginiert, `results` = `[StickySerializer]` | nur eigene; Sortierung `-sort_order`. | `WEB/services/sticky.service.ts` |
| W-63 | `POST {W}/stickies/` | `WorkspaceStickyViewSet.create` | A/M/G | B: `name`, `description` (JSON), `description_html`, `description_binary` (Base64), `logo_props`, `color`, `background_color`, `sort_order` | 201 StickySerializer | HTML-Sanitizing (`validate_html_content`) → ungültig 400 `{"error": "html content is not valid"}`; Binärprüfung → 400 `{"description_binary": "Invalid binary data"}`. `description_stripped` aus HTML; `sort_order` = max im Workspace + 10000 (`M/sticky.py`). | `WEB/services/sticky.service.ts` |
| W-64 | `GET {W}/stickies/{pk}/` | `WorkspaceStickyViewSet.retrieve` (DRF-Default) | authentifiziert; Queryset nur eigene | – | 200 / 404 | – | `WEB/services/sticky.service.ts` `getSticky` |
| W-65 | `PATCH {W}/stickies/{pk}/` | `WorkspaceStickyViewSet.partial_update` | `allow_permission([], creator=True, model=Sticky, WORKSPACE)` → **nur Ersteller** | B: wie W-63 | 200 | – | `WEB/services/sticky.service.ts` |
| W-66 | `DELETE {W}/stickies/{pk}/` | `WorkspaceStickyViewSet.destroy` | nur Ersteller | – | 204 | Soft-Delete. | `WEB/services/sticky.service.ts` |
| W-67 | `GET {W}/sidebar-preferences/` | `WorkspaceUserPreferenceViewSet.get` (`V/workspace/user_preference.py`) | A/M/G | – | 200 `{"<key>": {"is_pinned": bool, "sort_order": float}}` sortiert nach `sort_order` | Seeding fehlender Keys `views`, `active_cycles`, `analytics`, `drafts`, `your_work`, `archives`, `stickies`: `sort_order = 65535 + i*10000` (i = Index in der Liste fehlender Keys), `is_pinned = true` nur für `drafts`, `your_work`, `stickies`. | `WEB/services/workspace.service.ts` `fetchSidebarNavigationPreferences` |
| W-68 | `PATCH {W}/sidebar-preferences/` | `WorkspaceUserPreferenceViewSet.patch` | A/M/G | B: **Array** `[{"key": str, "is_pinned"?: bool, "sort_order"?: float}]` | 200 `{"message": "Successfully updated"}` | Einträge ohne `key` oder unbekannte Keys werden übersprungen. | `WEB/services/workspace.service.ts` `updateBulkSidebarPreferences` |

**Nicht vorhanden, aber vom Frontend aufgerufen:** `PATCH {W}/sidebar-preferences/{key}/` (`WEB/services/workspace.service.ts` `updateSidebarPreference`, Store `WEB/store/workspace/index.ts`) → im CE-Backend 404 `{"error": "Page not found."}`. Siehe 2.15.

### 2.6 Endpunkt-Inventar Projekt (`URL/project.py`)

| ID | Methode & Pfad | View.Methode (Quelle) | Berechtigung | Request | Response | Seiteneffekte / Besonderheiten | FE |
|---|---|---|---|---|---|---|---|
| P-01 | `GET {W}/projects/` | `ProjectViewSet.list` (`V/project/base.py`) | `allow_permission([A,M,G], WORKSPACE)` | – | 200 Array von Wertobjekten: `id, name, identifier, sort_order, logo_props, member_role, intake_count, archived_at, workspace, cycle_view, issue_views_view, module_view, page_view, inbox_view, guest_view_all_features, project_lead, network, created_at, updated_at, created_by, updated_by` | Sichtbarkeit (inkl. archivierter Projekte): WS-Admin → alle Projekte des Workspaces; WS-Member → Projekte mit aktiver eigener Mitgliedschaft **oder** `network = 2` (public); WS-Gast → nur Projekte mit aktiver Mitgliedschaft. `member_role` = eigene aktive Projektrolle oder `null`; `sort_order` = eigener `ProjectUserProperty.sort_order`; `intake_count` = Anzahl Intake-Issues mit Status `-2` (PENDING), nicht soft-gelöscht; `inbox_view` = `intake_view`. Keine explizite Sortierung. | `WEB/services/project/project.service.ts` `getProjectsLite` |
| P-02 | `POST {W}/projects/` | `ProjectViewSet.create` | `allow_permission([A,M], WORKSPACE)` | B: `name` (Pflicht, ≤ 255), `identifier` (Pflicht, ≤ 12), `description`, `description_text`, `description_html`, `network` (0\|2, Default 2), `default_assignee`, `project_lead`, `emoji`, `icon_prop`, `module_view`, `cycle_view`, `issue_views_view`, `page_view`, `intake_view`, `is_time_tracking_enabled`, `is_issue_type_enabled`, `guest_view_all_features`, `cover_image`, `cover_image_asset`, `estimate`, `archive_in` (0–12), `close_in` (0–12), `logo_props`, `default_state`, `timezone`, `external_source`, `external_id` | 201 ProjectListSerializer | Validierung (`S/project.py`): Name/Identifier mit Zeichen aus `&+,:;$^}{*=?@#\|'<>.()%!-` → `{"name": ["PROJECT_NAME_CANNOT_CONTAIN_SPECIAL_CHARACTERS"]}` / `{"identifier": ["PROJECT_IDENTIFIER_CANNOT_CONTAIN_SPECIAL_CHARACTERS"]}`; Duplikat im Workspace → `{"name": ["PROJECT_NAME_ALREADY_EXIST"]}` / `{"identifier": ["PROJECT_IDENTIFIER_ALREADY_EXIST"]}` (Frontend wertet diese Codes aus: `WEB/components/projects/create/root.tsx`, `WEB/components/project/form.tsx`); `description_html` wird sanitisiert, ungültig → `{"error": "html content is not valid"}`. Identifier wird beim Speichern `strip().upper()` (`M/project.py`) – die Duplikatprüfung erfolgt vorher case-sensitiv, ein Konflikt nach Upper-Case endet als `IntegrityError` → 400 `{"error": "The payload is not valid"}`. `timezone` fehlt → Workspace-Zeitzone. Effekte: `ProjectIdentifier(name=identifier)`; Ersteller als `ProjectMember(role=20)` (+ `ProjectUserProperty` mit `sort_order = min(eigene) - 10000` bzw. 65535 über `ProjectMember.save`); `project_lead` ≠ Ersteller → zusätzlich Admin-Mitglied; Default-States aus `DEFAULT_STATES` (`M/state.py`: Backlog `#60646C` 15000 default, Todo `#60646C` 25000, In Progress `#F59E0B` 35000, Done `#46A758` 45000, Cancelled `#9AA4BC` 55000, Triage `#4E5355` 65000 Gruppe `triage`); Celery `model_activity(model_name="project", current_instance=None)` → `webhook_activity(event="project", verb="created")`. | `WEB/services/project/project.service.ts` `createProject` |
| P-03 | `GET {W}/projects/details/` | `ProjectViewSet.list_detail` | `allow_permission([A,M,G], WORKSPACE)` | Q: `fields` (wirkungslos), `per_page`+`cursor` (beide nötig für Pagination), `order_by` (`PROJECT_ORDER_BY_ALLOWLIST`) | 200 `[ProjectListSerializer]` sortiert `sort_order, name`; paginiert nur wenn `per_page` **und** `cursor` | Sichtbarkeit wie P-01. Felder: alle Project-Felder + `is_favorite`, `sort_order`, `member_role`, `anchor` (Deploy-Board-Anchor oder `null`), `members` (IDs aktiver Nicht-Bot-Mitglieder), `cover_image_url`, `inbox_view`, `next_work_item_sequence` (max `IssueSequence.sequence` + 1, sonst 1). | `WEB/services/project/project.service.ts` `getProjects` |
| P-04 | `GET {W}/projects/{pk}/` | `ProjectViewSet.retrieve` | `allow_permission([A,M,G], WORKSPACE)` | – | 200 ProjectListSerializer | archiviert/nicht vorhanden → 404 `{"error": "Project does not exist"}`; User nicht aktives Mitglied: `network = 0` (secret) → 403 `{"error": "You do not have permission"}`, sonst **409** `{"error": "You are not a member of this project"}` (Frontend zeigt daraufhin „Projekt beitreten“). Effekt: Celery `recent_visited_task(entity_name="project")` (`BG/recent_visited_task.py`: aktualisiert `visited_at` oder legt Eintrag an; bei genau 20 Einträgen wird der älteste (`created_at`) gelöscht). | `WEB/services/project/project.service.ts` `getProject` |
| P-05 | `PUT {W}/projects/{pk}/` | `ProjectViewSet.update` (DRF-Default, **nicht überschrieben**) | nur `IsAuthenticated` (!) | B: vollständige ProjectListSerializer-Felder | 200 | **Sicherheitslücke:** keine Rollenprüfung, Serializer ohne Read-only-Felder (sogar `workspace` beschreibbar). Nicht portieren (siehe 5.3). | — |
| P-06 | `PATCH {W}/projects/{pk}/` | `ProjectViewSet.partial_update` | WS-Admin (aktiv) **oder** aktiver Projekt-Admin (Projektmitgliedschaft für WS-Admin **nicht** nötig) → sonst 403 `{"error": "You don't have the required permissions."}` | B: Felder wie P-02 (partiell) + `inbox_view` | 200 ProjectListSerializer | archiviert → 400 `{"error": "Archived projects cannot be updated"}`. `intake_view` wird **immer** aus `inbox_view` (bzw. bisherigem Wert) übernommen – ein gesendetes `intake_view` ohne `inbox_view` wird überschrieben. `intake_view` wahr und kein Default-Intake → `Intake(name="{Projektname} Intake", is_default=True)` anlegen. Zeitzonenwechsel retimet offene Intake-Snoozes (`M/project.py` `_retime_intake_snoozes`). Celery `model_activity` mit `current_instance` (JSON des ProjectSerializer vorher) → pro geändertem Key `webhook_activity(verb="updated", field=key)`. | `WEB/services/project/project.service.ts` `updateProject` |
| P-07 | `DELETE {W}/projects/{pk}/` | `ProjectViewSet.destroy` | WS-Admin oder Projekt-Admin, sonst 403 `{"error": "You don't have the required permissions."}` | – | 204 | Soft-Delete (Kaskade via Celery), Celery `webhook_activity(event="project", verb="deleted")`, `DeployBoard` des Projekts soft-löschen, alle `UserFavorite` des Projekts (aller User) soft-löschen. | `WEB/services/project/project.service.ts` `deleteProject` |
| P-08 | `GET {W}/project-identifiers/` | `ProjectIdentifierEndpoint.get` | `allow_permission([A,M], WORKSPACE)` | Q: `name` (wird `strip().upper()`) | 200 `{"exists": int, "identifiers": [{"id","name","project"}]}` | leer → 400 `{"error": "Name is required"}`. Reservierte Identifier bleiben nach Projektlöschung in `ProjectIdentifier` bestehen (bis P-09). | `WEB/services/project/project.service.ts` `checkProjectIdentifierAvailability` |
| P-09 | `DELETE {W}/project-identifiers/` | `ProjectIdentifierEndpoint.delete` | A/M (WS) | B: `name` | 204 | leer → 400 `{"error": "Name is required"}`; Projekt mit Identifier existiert → 400 `{"error": "Cannot delete an identifier of an existing project"}`; sonst `ProjectIdentifier` soft-löschen. | — |
| P-10 | `GET {P}/invitations/` | `ProjectInvitationsViewset.list` (DRF-Default) | nur `IsAuthenticated` (!) | – | 200 `[ProjectMemberInviteSerializer]` (inkl. `token`) | **Sicherheitslücke** (jeder Authentifizierte, der Slug+Projekt-ID kennt). | — |
| P-11 | `POST {P}/invitations/` | `ProjectInvitationsViewset.create` | `allow_permission([A])` | B: `emails: [{"email","role"}]` | **immer 500** | Bug 1: `WorkspaceMember.objects.filter(...).role` auf QuerySet → `AttributeError`. Bug 2: `project_invitations.delay(...)` auf Liste. Vorgesehene Logik: WS-Rolle 5/20 ≠ gewünschte Rolle → Fehler `{"error": "You cannot invite a user with different role than workspace role"}`; Einladungen mit JWT-Token; Mail-Task; 200 `{"message": "Email sent successfully"}`. | — |
| P-12 | `GET {P}/invitations/{pk}/` | `ProjectInvitationsViewset.retrieve` | nur `IsAuthenticated` | – | 200 ProjectMemberInviteSerializer | – | — |
| P-13 | `DELETE {P}/invitations/{pk}/` | `ProjectInvitationsViewset.destroy` | nur `IsAuthenticated` (!) | – | 204 | Soft-Delete; keine Rollenprüfung. | — |
| P-14 | `GET /api/users/me/workspaces/{slug}/projects/invitations/` | `UserProjectInvitationsViewset.list` (DRF-Default) | authentifiziert | – | 200 `[ProjectMemberInviteSerializer]` | **alle** Projekt-Einladungen mit `email == user.email` – der `slug` wird **ignoriert**. | — |
| P-15 | `POST /api/users/me/workspaces/{slug}/projects/invitations/` | `UserProjectInvitationsViewset.create` („Projekten beitreten“) | `allow_permission([A,M], WORKSPACE)` | B: `project_ids: [uuid…]` | 201 `{"message": "Projects joined successfully"}` | nur Projekte dieses Workspaces; ein `network = 0`-Projekt und User nicht WS-Admin → 403 `{"error": "Only workspace admins can join private project"}`. Inaktive Mitgliedschaften → reaktiviert mit **Rolle = WS-Rolle** (alte Projektrolle nicht wiederhergestellt); neue `ProjectMember(role=WS-Rolle)` + `ProjectUserProperty` (Default `sort_order` 65535) per `bulk_create(ignore_conflicts=True)`. | `WEB/services/user.service.ts` `joinProject` |
| P-16 | `GET /api/users/me/workspaces/{slug}/project-roles/` | `UserProjectRolesEndpoint.get` | `WorkspaceUserPermission` | – | 200 `{"<project_id>": role}` | nur aktive Mitgliedschaften und nur solange WS-Mitgliedschaft aktiv. | `WEB/services/workspace.service.ts` `getWorkspaceUserProjectsRole`, `SVC/workspace/member.service.ts` |
| P-17 | `POST {P}/join/{pk}/` | `ProjectJoinEndpoint.post` | `AllowAny` + eigene Prüfung | B: `token`, `accepted` (**strikt bool**) | 200 `{"message": "Project Invitation Accepted"}` / `{"message": "Project Invitation was not accepted"}` | Token fehlt/≠ → 403 `{"error": "You do not have permission to join the project"}`; anonym → 401 `{"error": "Authentication required to accept project invitation"}`; E-Mail ≠ → 403 `{"error": "You do not have permission to accept this invitation"}`; `accepted` kein bool → 400 ``{"error": "`accepted` must be a boolean"}``; schon beantwortet → 400 `{"error": "You have already responded to the invitation request"}`. Bei Annahme: fehlende WS-Mitgliedschaft → anlegen mit Rolle `min(15, invite.role)` (bzw. invite.role wenn < 15); vorhandene → `is_active=True` (Rolle unverändert); `ProjectMember` (nur dieses Projekts) anlegen bzw. reaktivieren mit `role = invite.role`. Einladung wird **nicht** gelöscht. | — |
| P-18 | `GET {P}/join/{pk}/` | `ProjectJoinEndpoint.get` | `AllowAny` | – | 200 ProjectMemberInvitePublicSerializer (`id, project{Lite}, workspace{Lite}, role, message, accepted, responded_at`) | ohne E-Mail/Token. | — |
| P-19 | `GET {P}/members/` | `ProjectMemberViewSet.list` (`V/project/member.py`) | `allow_permission([A,M,G])` (PROJECT) | – | 200 `[{"id","role","member","project","original_role","created_at"}]` | aktive Nicht-Bot-Mitglieder, die zusätzlich aktive WS-Mitglieder sind. `member`, `project` = UUIDs; `original_role` = `role`. | `WEB/services/project/project-member.service.ts` `fetchProjectMembers` |
| P-20 | `POST {P}/members/` | `ProjectMemberViewSet.create` | `allow_permission([A])` | B: `members: [{"member_id": uuid, "role": 5\|15\|20}]` | 201 `[ProjectMemberRoleSerializer]` für alle angefragten Member | leer → 400 `{"error": "At least one member is required"}`; Ziel kein aktives WS-Mitglied → 404 `{"error": "The required object does not exist."}`; WS-Admin mit Projektrolle 5/15 → 400 `{"error": "You cannot add a user with role lower than the workspace role"}`; WS-Gast mit 15/20 → 400 `{"error": "You cannot add a user with role higher than the workspace role"}`. Bestehende Zeilen (auch inaktive) → Rolle + `is_active=True` (bulk_update); neue `ProjectMember` + `ProjectUserProperty` (`sort_order = min(User-sort_order im Workspace) - 10000` bzw. 65535) per `bulk_create(ignore_conflicts=True)`. Pro Mitglied Celery `project_add_user_email.delay(current_site, project_member_id, inviter_id)` (auch für bereits vorhandene). `member_id` nicht in kanonischer UUID-Schreibweise → `KeyError` → 400. | `WEB/services/project/project-member.service.ts` `bulkAddMembersToProject` |
| P-21 | `GET {P}/members/{pk}/` | `ProjectMemberViewSet.retrieve` | `allow_permission([A,M,G])` | `pk` = ProjectMember-ID | 200: Anfragender Rolle > 5 → ProjectMemberAdminSerializer (alle Felder, `workspace`/`project` Lite, `member` = UserAdminLite); Gast → `{"id","role","member","project","original_role","created_at"}` | nicht gefunden → 404 `{"error": "Project member not found"}`. | `WEB/services/project/project-member.service.ts` |
| P-22 | `PATCH {P}/members/{pk}/` | `ProjectMemberViewSet.partial_update` | `allow_permission([A])` | B: `role`, `is_active`, `view_props`, `default_props`, `preferences`, `sort_order`, `comment` | 200 ProjectMemberSerializer | Ziel aktiv; WS-Rollen von Ziel und Anfragendem werden geladen (fehlend → 404). Nicht-WS-Admin ändert eigene Rolle → 400 `{"error": "You cannot update your own role"}`. Bei `role`: Anfragender Projektrolle < 20 (ohne WS-Admin) → 403 `{"error": "You do not have permission to update roles"}`; Ziel-Rolle ≥ eigene → 403 `{"error": "You cannot update the role of a member with a role equal to or higher than your own"}`; neue Rolle ≥ eigene → 403 `{"error": "You cannot assign a role equal to or higher than your own"}` (alle drei entfallen für WS-Admins); WS-Gast bekommt 15/20 → 400 `{"error": "You cannot add a user with role higher than the workspace role"}`. Bei `is_active`: analog 403 `{"error": "You do not have permission to update member status"}` / `{"error": "You cannot update the status of a member with a role equal to or higher than your own"}`. **Konsequenz:** ein Projekt-Admin (ohne WS-Admin) kann niemanden zum Admin machen und keine anderen Admins ändern. | `WEB/services/project/project-member.service.ts` |
| P-23 | `DELETE {P}/members/{pk}/` | `ProjectMemberViewSet.destroy` | `allow_permission([A])` | – | 204 | sich selbst → 400 `{"error": "You cannot remove yourself from the workspace. Please use leave workspace"}` (sic, „workspace“); Ziel-Rolle > eigene → 400 `{"error": "You cannot remove a user having role higher than you"}`. Effekt `is_active=False`. | `WEB/services/project/project-member.service.ts` |
| P-24 | `POST {P}/members/leave/` | `ProjectMemberViewSet.leave` | `allow_permission([A,M,G])` | – | 204 | letzter aktiver Admin → 400 `{"error": "You cannot leave the project as your the only admin of the project you will have to either delete the project or create an another admin"}`. | `WEB/services/user.service.ts` `leaveProject` |
| P-25 | `POST {P}/project-views/` | `ProjectUserViewsEndpoint.post` | authentifiziert; aktives Projektmitglied sonst 403 `{"error": "Forbidden"}`; Projekt fehlt → 404 | B: `view_props`, `default_props`, `preferences`, `sort_order` (je optional) | 204 | überschreibt die übergebenen Felder des eigenen `ProjectMember`. | — |
| P-26 | `GET {P}/project-members/me/` | `ProjectMemberUserEndpoint.get` | authentifiziert; kein aktives Mitglied → 404 | – | 200 ProjectMemberSerializer (alle Felder, `workspace`/`project`/`member` Lite) | – | `WEB/services/project/project-member.service.ts` `projectMemberMe` |
| P-27 | `GET {W}/user-favorite-projects/` | `ProjectFavoritesViewSet.list` (DRF-Default) | authentifiziert | – | **immer 500** | ViewSet hat **keine** `serializer_class` → `AssertionError`. | `WEB/services/project/project.service.ts` `getUserProjectFavorites` (ungenutzt) |
| P-28 | `POST {W}/user-favorite-projects/` | `ProjectFavoritesViewSet.create` | authentifiziert (keine Rollenprüfung, auch Gäste) | B: `project` (UUID) | 204 | Projekt muss im Workspace und sichtbar sein (`get_favorite_entities`) → sonst 404. Legt `UserFavorite(entity_type="project")` an; Duplikat → 400 `{"error": "The payload is not valid"}`. | `WEB/services/project/project.service.ts` `addProjectToFavorites` (Store nutzt stattdessen W-44) |
| P-29 | `DELETE {W}/user-favorite-projects/{project_id}/` | `ProjectFavoritesViewSet.destroy` | authentifiziert | – | 204 / 404 | Hard-Delete. | `WEB/services/project/project.service.ts` `removeProjectFromFavorites` (Store nutzt stattdessen W-46) |
| P-30 | `GET {P}/project-deploy-boards/` | `DeployBoardViewSet.list` | `ProjectMemberPermission` (GET → aktives Projektmitglied) | – | 200 **Objekt** DeployBoardSerializer des Projekt-Boards; ohne Board ein Objekt aus Initialwerten der beschreibbaren Felder (ohne `id`/`anchor`) | – | `WEB/services/project/project-publish.service.ts` `fetchPublishSettings` |
| P-31 | `POST {P}/project-deploy-boards/` | `DeployBoardViewSet.create` („Projekt veröffentlichen“) | `ProjectMemberPermission` (POST → Projektrolle 20/15) | B: `is_comments_enabled` (Default false), `is_reactions_enabled` (false), `is_votes_enabled` (false), `intake` (UUID\|null), `views` (Default `{"list":true,"kanban":true,"calendar":true,"gantt":true,"spreadsheet":true}`) | **200** DeployBoardSerializer (inkl. `anchor`) | Projekt nicht im Workspace → 404 `{"error": "Project does not exist"}`; Intake nicht aus diesem Projekt → 400 `{"error": "Intake is not valid"}`. `get_or_create(entity_name="project", entity_identifier=project_id, project_id)`; Werte werden **immer** überschrieben (`view_props = views`). `anchor` = `uuid4().hex`. | `WEB/services/project/project-publish.service.ts` `publishProject` |
| P-32 | `GET {P}/project-deploy-boards/{pk}/` | `DeployBoardViewSet.retrieve` (DRF-Default) | `ProjectMemberPermission` | – | 200 DeployBoardSerializer | Queryset **nicht** projektbezogen (`DeployBoard.objects.all()`) → Board eines fremden Projekts per ID lesbar (IDOR, nicht portieren). | — |
| P-33 | `PATCH {P}/project-deploy-boards/{pk}/` | `DeployBoardViewSet.partial_update` (DRF-Default) | `ProjectMemberPermission` (20/15) | B: `is_comments_enabled`, `is_reactions_enabled`, `is_votes_enabled`, `intake` (muss zum Board-Projekt gehören → `{"intake": ["Intake is not valid please pass a valid intake"]}`), `view_props`, `is_activity_enabled`, `is_disabled` | 200 DeployBoardSerializer | gleiche IDOR-Problematik wie P-32. | `WEB/services/project/project-publish.service.ts` `updatePublishSettings` |
| P-34 | `DELETE {P}/project-deploy-boards/{pk}/` | `DeployBoardViewSet.destroy` (DRF-Default) | `ProjectMemberPermission` (20/15) | – | 204 | „Veröffentlichung aufheben“ (Soft-Delete); IDOR wie P-32. | `WEB/services/project/project-publish.service.ts` `unpublishProject` |
| P-35 | `POST {P}/archive/` | `ProjectArchiveUnarchiveEndpoint.post` | `allow_permission([A,M])` (PROJECT) | – | 200 `{"archived_at": "<str(datetime)>"}` (Python-`str()`, Format `YYYY-MM-DD HH:MM:SS.ffffff+00:00`) | setzt `archived_at = now`; soft-löscht alle `UserFavorite` des Projekts. Archivierte Projekte: nicht in Workspace-Listen W-36/W-39/W-41/W-42, Suche, Analytics; `PATCH` verboten (P-06). | `WEB/services/project/project-archive.service.ts` |
| P-36 | `DELETE {P}/archive/` | `ProjectArchiveUnarchiveEndpoint.delete` | A/M (PROJECT) | – | 204 | `archived_at = NULL` (Favoriten bleiben gelöscht). | `WEB/services/project/project-archive.service.ts` |
| P-37 | `GET {P}/preferences/member/{member_id}/` | `ProjectMemberPreferenceEndpoint.get` | `allow_permission([A,M,G])` | `member_id` = **User-ID** | 200 `{"preferences": {...}, "project_id", "member_id", "workspace_id"}` | beliebiger `member_id` (nicht auf sich selbst beschränkt). Kein Eintrag → 404. | — |
| P-38 | `PATCH {P}/preferences/member/{member_id}/` | `ProjectMemberPreferenceEndpoint.patch` | `allow_permission([A,M,G])` | B: **gesamter Body** = Preferences-Teilobjekt (z. B. `{"pages": {"block_display": false}}`) | 200 `{"preferences": {...}}` | flacher Merge (`dict.update`) in `ProjectMember.preferences` (Default `{"pages": {"block_display": true}, "navigation": {"default_tab": "work_items", "hide_in_more_menu": []}}`). **Kann Präferenzen anderer Mitglieder ändern** (kein Self-Check). | — |

### 2.7 Endpunkt-Inventar User (`URL/user.py`) & API-Tokens (`URL/api.py`)

| ID | Methode & Pfad | View.Methode (Quelle) | Berechtigung | Request | Response | Seiteneffekte / Besonderheiten | FE |
|---|---|---|---|---|---|---|---|
| U-01 | `GET {U}/me/` | `UserEndpoint.retrieve` (`V/user/base.py`) | authentifiziert | – | 200 UserMeSerializer: `id, avatar, cover_image, avatar_url, cover_image_url, date_joined, display_name, email, first_name, last_name, is_active, is_bot, is_email_verified, user_timezone, username, is_password_autoset, last_login_medium, last_login_time` | `Cache-Control: private, max-age=12`, `Vary: Cookie`. `avatar_url` = `/api/assets/v2/static/{avatar_asset_id}/` oder Legacy-`avatar`-URL oder `null` (analog `cover_image_url`). | `WEB/services/user.service.ts` `currentUser` (mit `validateStatus: null`), `SVC/user/user.service.ts` |
| U-02 | `PATCH {U}/me/` | `UserEndpoint.partial_update` (DRF) | authentifiziert | B: beschreibbar sind alle User-Felder außer Passwort und den Read-only-Feldern (2.12) – fachlich genutzt: `first_name`, `last_name`, `display_name`, `user_timezone`, `avatar`, `avatar_asset`, `cover_image`, `cover_image_asset` | 200 UserSerializer (**alle** User-Felder außer `password`, inkl. `token`, `last_login_ip`, `last_login_uagent`, …) | `first_name`/`last_name` mit URL → 400 `{"first_name": ["First name cannot contain a URL."]}` / `{"last_name": ["Last name cannot contain a URL."]}`; `avatar_asset`/`cover_image_asset` müssen eigene Assets des passenden Typs (`USER_AVATAR`/`USER_COVER`) sein, sonst `{"avatar_asset": ["Invalid asset."]}`. Mass-Assignment-Risiko: auch `is_password_expired`, `is_password_reset_required`, `bot_type`, `is_email_valid`, `masked_at`, `last_login` beschreibbar (nicht portieren, 5.3). `User.save` setzt `display_name` = E-Mail-Präfix, falls leer. | `WEB/services/user.service.ts` `updateUser`, `SVC/user/user.service.ts` |
| U-03 | `DELETE {U}/me/` | `UserEndpoint.deactivate` | authentifiziert | – | 204 | Instanz-Admin → 400 `{"error": "You cannot deactivate your account since you are an instance admin"}`. Für jede aktive Projektmitgliedschaft: wenn ein anderer aktiver Admin existiert **oder** User einziges Mitglied ist → deaktivieren, sonst 400 `{"error": "You cannot deactivate account as you are the only admin in some projects."}`; analog Workspaces → `{"error": "You cannot deactivate account as you are the only admin in some workspaces."}`. (Hinweis: die Annotationen werden pro eigener `ProjectMember`-/`WorkspaceMember`-Zeile gruppiert; `Count(Case(When(…, then=1), default=0))` zählt auch den Wert 0, `other_admin_exists` ist daher immer 1 und `total_members` immer 1 → **jede** Mitgliedschaft wird deaktiviert, die beiden Fehlerpfade sind unerreichbar. Fachlich gewollt ist die Prüfung „anderer aktiver Admin vorhanden oder einziges Mitglied“.) Danach: Workspace-Einladungen der E-Mail soft-löschen; **alle Sessions** löschen; Profile zurücksetzen (`last_workspace_id=None`, `is_tour_completed=False`, `is_onboarded=False`, `onboarding_step={"workspace_join":false,"profile_complete":false,"workspace_create":false,"workspace_invite":false}`); zufälliges Passwort + `is_password_autoset=True`; `is_active=False`, `last_logout_ip`, `last_logout_time`; Celery `user_deactivation_email`; Logout. | `WEB/services/user.service.ts` `deactivateAccount` |
| U-04 | `GET {U}/session/` | `UserSessionEndpoint.get` | `AllowAny` | – | 200 `{"is_authenticated": true, "user": UserMe}` bzw. `{"is_authenticated": false}` | – | — (u. a. für Live/Space gedacht) |
| U-05 | `GET {U}/me/settings/` | `UserEndpoint.retrieve_user_settings` | authentifiziert | Q: `t` (Cache-Busting, ignoriert) | 200 `{"id","email","workspace": {...}}` | `workspace`: wenn `Profile.last_workspace_id` auf Workspace mit aktiver Mitgliedschaft zeigt: `{"last_workspace_id","last_workspace_slug","last_workspace_name","last_workspace_logo" (asset_url oder ""),"fallback_workspace_id" (= last),"fallback_workspace_slug","invites" (Anzahl offener Einladungen der E-Mail)}`, sonst `{"last_workspace_id": null, "last_workspace_slug": null, "fallback_workspace_id" (ältester Workspace mit aktiver Mitgliedschaft oder null), "fallback_workspace_slug", "invites"}`. Steuert den Redirect nach Login. `Cache-Control: private, max-age=12`. | `WEB/services/user.service.ts` `currentUserSettings` |
| U-06 | `POST {U}/me/email/generate-code/` | `UserEndpoint.generate_email_verification_code` | authentifiziert; Throttles `EmailVerificationThrottle` (3/h/User) + `AuthenticationThrottle` (10/min/IP) | B: `email` | 200 `{"message": "Verification code sent to email"}` | E-Mail `strip().lower()`; Fehler: leer → 400 `{"error": "Email is required"}`, Format → `{"error": "Invalid email format"}`, gleich alter → `{"error": "New email must be different from current email"}`, vergeben → `{"error": "An account with this email already exists"}`. Pro Ziel-Adresse max. 5 Codes/3600 s (`email_update_issued:{email}`) → sonst 429. Code = 6-stellig (`secrets.randbelow(900000)+100000`), Cache `magic_email_update_{user_id}_{email}` = `{"token": code}` 600 s, Versuchszähler zurücksetzen. Celery `send_email_update_magic_code(email, token)`. Fehler beim Generieren → 400 `{"error": "Failed to generate verification code. Please try again."}`. | `WEB/services/user.service.ts` `generateEmailCode` |
| U-07 | `PATCH {U}/me/email/` | `UserEndpoint.update_email` | authentifiziert; `AuthenticationThrottle` | B: `email`, `code` | 200 UserMeSerializer (neuer Stand) | Validierung wie U-06; Code fehlt → 400 `{"error": "Verification code is required"}`; Versuchszähler `…:verify_attempts` (600 s) wird **vor** dem Vergleich erhöht; Code abgelaufen → 400 `{"error": "Verification code has expired or is invalid"}`; > 5 Versuche (`MagicCodeProvider.MAX_VERIFY_ATTEMPTS = 5`) oder falsch → 400 `{"error": "Invalid verification code"}` (bei Erreichen von 5 werden Code+Zähler gelöscht); Cache-Fehler → 400 `{"error": "Failed to verify code. Please try again."}`; erneute Eindeutigkeitsprüfung. Effekt: `email` ersetzt, `is_email_verified=False`, Cache-Code löschen, **Logout**, Celery `send_email_update_confirmation` an neue **und** alte Adresse. | `WEB/services/user.service.ts` `verifyEmailCode` |
| U-08 | `GET {U}/me/profile/` | `ProfileEndpoint.get` | authentifiziert | – | 200 ProfileSerializer (alle Profile-Felder, 2.13) | `Cache-Control: private, max-age=12`. | `WEB/services/user.service.ts` `getCurrentUserProfile`, `SVC/user/user.service.ts` |
| U-09 | `PATCH {U}/me/profile/` | `ProfileEndpoint.patch` | authentifiziert | B: alle Profile-Felder außer `user` (u. a. `theme`, `is_app_rail_docked`, `onboarding_step`, `use_case`, `role`, `last_workspace_id`, `language`, `start_of_the_week`, `notification_view_mode`, `is_smooth_cursor_enabled`, `is_navigation_tour_completed`, `product_tour`, `goals`, …) | 200 ProfileSerializer | JSON-Felder werden ersetzt. | `WEB/services/user.service.ts` `updateCurrentUserProfile` |
| U-10 | `GET {U}/me/accounts/` | `AccountEndpoint.get` | authentifiziert | – | 200 `[AccountSerializer]` (alle Felder **inkl.** `access_token`, `refresh_token`, `id_token`) | verknüpfte OAuth-Konten. Token-Exposition → in .NET weglassen (5.3). | `WEB/services/user.service.ts` `getCurrentUserAccounts` |
| U-11 | `GET {U}/me/accounts/{pk}/` | `AccountEndpoint.get` | authentifiziert, eigenes Konto | – | 200 AccountSerializer | – | — |
| U-12 | `DELETE {U}/me/accounts/{pk}/` | `AccountEndpoint.delete` | authentifiziert, eigenes Konto | – | 204 | Hard-Delete (`Account` ist nicht soft-löschbar). | — |
| U-13 | `GET {U}/me/instance-admin/` | `UserEndpoint.retrieve_instance_admin` | authentifiziert | – | 200 `{"is_instance_admin": bool}` | `InstanceAdmin` der ersten `Instance`. | `WEB/services/user.service.ts` `currentUserInstanceAdminStatus` |
| U-14 | `PATCH {U}/me/onboard/` | `UpdateUserOnBoardedEndpoint.patch` | authentifiziert | B: `is_onboarded` (Default false) | 200 `{"message": "Updated successfully"}` | setzt `Profile.is_onboarded`. | `WEB/services/user.service.ts` `updateUserOnBoard` |
| U-15 | `PATCH {U}/me/tour-completed/` | `UpdateUserTourCompletedEndpoint.patch` | authentifiziert | B: `is_tour_completed` | 200 `{"message": "Updated successfully"}` | setzt `Profile.is_tour_completed`. | `WEB/services/user.service.ts` `updateUserTourCompleted` |
| U-16 | `GET {U}/me/activities/` | `UserActivityEndpoint.get` | authentifiziert | Q: `order_by`, `per_page`, `cursor` | 200 paginiert `[IssueActivitySerializer]` | alle Aktivitäten mit `actor = user` über **alle** Workspaces, ohne Sichtbarkeitsfilter. | — |
| U-17 | `GET {U}/me/workspaces/` | `UserWorkSpacesEndpoint.get` (`V/workspace/base.py`) | authentifiziert | Q: `fields` (wirkungslos), `search` (name), `owner`, `v` (Cache-Busting) | 200 `[WorkSpaceSerializer + role + total_members]` | Workspaces mit aktiver eigener Mitgliedschaft (distinct), `role` = eigene WS-Rolle, `total_members` = aktive Nicht-Bot-Mitglieder. | `WEB/services/workspace.service.ts` `userWorkspaces`, `SVC/workspace/workspace.service.ts` |
| U-18 | `GET {U}/me/workspaces/{slug}/activity-graph/` | `UserActivityGraphEndpoint.get` (`V/workspace/user.py`) | authentifiziert (keine Mitgliedschaftsprüfung) | – | 200 `[{"created_date": "YYYY-MM-DD", "activity_count": int}]` | eigene `IssueActivity` der letzten 6 Monate im Workspace, gruppiert nach Datum (Benutzerzeitzone). | — |
| U-19 | `GET {U}/me/workspaces/{slug}/issues-completed-graph/` | `UserIssueCompletedGraphEndpoint.get` | authentifiziert | Q: `month` (1–12, Default 1) | 200 `[{"week": int, "completed_count": int}]` | eigene zugewiesene, abgeschlossene Issues des Monats (jedes Jahr!), `week = ISO-Woche % 4`. | — |
| U-20 | `GET {U}/me/workspaces/{slug}/dashboard/` | `UserWorkspaceDashboardEndpoint.get` (`V/workspace/base.py`) | authentifiziert | Q: `month` (Default 1) | 200 `{"issue_activities": [{"created_date","activity_count"}], "completed_issues": [{"week_in_month","completed_count"}], "assigned_issues_count", "pending_issues_count", "completed_issues_count", "issues_due_week_count", "state_distribution": [{"state_group","state_count"}], "overdue_issues": [{"id","name","workspace__slug","project_id","target_date"}], "upcoming_issues": [{"id","name","workspace__slug","project_id","start_date"}]}` | Legacy-Dashboard: Aktivitäten 3 Monate; `week_in_month = floor((Tag-1)/7)+1`; `issues_due_week` = Ziel-Datum in aktueller ISO-Woche (jahresübergreifend!); überfällig = nicht completed/cancelled, `target_date < now`, `completed_at IS NULL`; anstehend = `start_date >= now`. | — |
| AT-01 | `POST {U}/api-tokens/` | `ApiTokenEndpoint.post` (`V/api.py`) | authentifiziert | B: `label` (Default `uuid4().hex`), `description` (Default `""`), `expired_at` (ISO-Datetime\|null) | 201 APITokenSerializer **inkl. `token`** (`plane_api_<32 hex>`) – einzige Gelegenheit, den Token zu sehen | `user_type = 1` wenn `user.is_bot`, sonst 0; `workspace = NULL` (Token gilt für alle Workspaces des Users, Nutzung in `/api/v1/`, siehe A05). | `SVC/developer/api-token.service.ts` |
| AT-02 | `GET {U}/api-tokens/` | `ApiTokenEndpoint.get` | authentifiziert | – | 200 `[APITokenReadSerializer]` (alle Felder **außer** `token`; `is_active` berechnet: `expired_at IS NULL` oder `now < expired_at`) | nur eigene. | `SVC/developer/api-token.service.ts` |
| AT-03 | `GET {U}/api-tokens/{pk}/` | `ApiTokenEndpoint.get` | authentifiziert, eigenes | – | 200 APITokenReadSerializer | – | `SVC/developer/api-token.service.ts` (ruft **ohne** Trailing Slash → 301-Redirect) |
| AT-04 | `PATCH {U}/api-tokens/{pk}/` | `ApiTokenEndpoint.patch` | authentifiziert, eigenes | B: `label`, `description` (`expired_at`, `is_active`, `token` read-only) | 200 APITokenSerializer **inkl. `token`** (Re-Exposition!) | – | — |
| AT-05 | `DELETE {U}/api-tokens/{pk}/` | `ApiTokenEndpoint.delete` | authentifiziert, eigenes | – | 204 | Soft-Delete (Token danach ungültig, da Auth über Default-Manager). | `SVC/developer/api-token.service.ts` (ohne Trailing Slash) |

### 2.8 Endpunkt-Inventar States (`URL/state.py`), Estimates (`URL/estimate.py`), Timezones (`URL/timezone.py`)

| ID | Methode & Pfad | View.Methode (Quelle) | Berechtigung | Request | Response | Seiteneffekte / Besonderheiten | FE |
|---|---|---|---|---|---|---|---|
| S-01 | `GET {P}/states/` | `StateViewSet.list` (`V/state/base.py`) | `allow_permission([A,M,G])` | Q: `grouped=true` | 200 `[StateSerializer]` (mit `order`) bzw. bei `grouped=true` `{"backlog": [...], "cancelled": [...], "completed": [...], "started": [...], "unstarted": [...]}` (nur vorhandene Gruppen, Schlüssel alphabetisch sortiert) | Queryset: Projekt muss nicht archiviert sein und User aktives Mitglied; `is_triage=False` und Gruppe ≠ `triage` (Manager `StateManager`). Sortierung `sequence`. `order` = Position/Anzahl je Gruppe (1-basiert, z. B. 0.5, 1.0). | `WEB/services/project/project-state.service.ts` `getStates` |
| S-02 | `POST {P}/states/` | `StateViewSet.create` | `allow_permission([A])` | B: `name` (Pflicht, ≤ 255, eindeutig im Projekt), `color` (Pflicht), `group` (`backlog`\|`unstarted`\|`started`\|`completed`\|`cancelled`; Default `backlog`), `description`, `sequence` | **200** StateSerializer | `group = "triage"` → 400 `{"non_field_errors": ["Cannot create triage state"]}`; Name vergeben → 400 `{"name": "The state name is already taken"}`. `default` ist read-only. `slug = slugify(name)`. `sequence` wird überschrieben mit `max(sequence im Projekt) + 15000`, sobald States existieren (`M/state.py`). Cache-Invalidierung (wirkungslos). | `WEB/services/project/project-state.service.ts` `createState` |
| S-03 | `GET {P}/states/{pk}/` | `StateViewSet.retrieve` (DRF-Default) | authentifiziert; Queryset-Scoping wie S-01 | – | 200 StateSerializer | – | `WEB/services/project/project-state.service.ts` `getState` |
| S-04 | `PATCH {P}/states/{pk}/` | `StateViewSet.partial_update` | `allow_permission([A])` | B: `name`, `color`, `group`, `description`, `sequence` | 200 StateSerializer | Name vergeben → 400 `{"name": "The state name is already taken"}`. Reihenfolge-Änderung per Drag&Drop setzt `sequence`. | `WEB/services/project/project-state.service.ts` `patchState` |
| S-05 | `DELETE {P}/states/{pk}/` | `StateViewSet.destroy` | `allow_permission([A])` | – | 204 | `default` → 400 `{"error": "Default state cannot be deleted"}`; existiert ein (nicht soft-gelöschtes) Issue mit diesem State (inkl. archivierter/Draft) → 400 `{"error": "The state is not empty, only empty states can be deleted"}`. Soft-Delete. | `WEB/services/project/project-state.service.ts` `deleteState` |
| S-06 | `GET {P}/intake-state/` | `IntakeStateEndpoint.get` | `allow_permission([A,M,G])` | – | 200 StateSerializer des Triage-States | kein Triage-State → 404 `{"error": "Triage state not found"}`. | `WEB/services/project/project-state.service.ts` `getIntakeState` |
| S-07 | `POST {P}/states/{pk}/mark-default/` | `StateViewSet.mark_as_default` | `allow_permission([A])` | B: `{}` | 204 | **eine** UPDATE-Anweisung: `default = (pk == state.pk)` für alle Nicht-Triage-States des Projekts (verhindert 0 oder 2 Defaults bei Nebenläufigkeit). | `WEB/services/project/project-state.service.ts` `markDefault` |
| — | `PUT {P}/states/{pk}/` | nicht gemappt | – | – | 405 | Frontend definiert `updateState` (PUT), Store nutzt aber `patchState`. | (`updateState` ungenutzt) |
| E-01 | `GET {P}/project-estimates/` | `ProjectEstimatePointEndpoint.get` (`V/estimate/base.py`) | `allow_permission([A,M])` | – | 200 `[EstimatePointSerializer]` des aktiven Estimates oder `[]` | – | — |
| E-02 | `GET {P}/estimates/` | `BulkEstimatePointEndpoint.list` | `ProjectEntityPermission` (GET → Mitglied) | – | 200 `[EstimateReadSerializer]` (alle Estimate-Felder + `points`) | **alle** Estimates des Projekts (auch inaktive). Sortierung `name`. | `WEB/services/estimate.service.ts` `fetchProjectEstimates` |
| E-03 | `POST {P}/estimates/` | `BulkEstimatePointEndpoint.create` | `ProjectEntityPermission` (POST → 20/15) | B: `estimate: {"name" (Default zufällig 10 Kleinbuchstaben), "type" (`categories`\|`points`, Default `categories`), "last_used" (bool)}`, `estimate_points: [{"key": int, "value": str (≤ 20), "description"}]` | 200 EstimateReadSerializer | **Reihenfolge-Bug:** Estimate wird **vor** der Punkt-Validierung angelegt → bei ungültigen Punkten (400 Feldfehler, z. B. `{"non_field_errors": ["Value can't be more than 20 characters"]}`) bleibt ein Estimate ohne Punkte zurück. `estimate` fehlt → 500. Name doppelt → 400 `{"error": "The payload is not valid"}`. Punkte per `bulk_create(ignore_conflicts=True)`. Aktiviert das Estimate **nicht** (Aktivierung über `PATCH {W}/projects/{id}/` mit `estimate`). Cache-Invalidierung (wirkungslos). | `WEB/services/estimate.service.ts` `createEstimate` |
| E-04 | `GET {P}/estimates/{estimate_id}/` | `BulkEstimatePointEndpoint.retrieve` | `ProjectEntityPermission` | – | 200 EstimateReadSerializer | – | `WEB/services/estimate.service.ts` `fetchEstimateById` |
| E-05 | `PATCH {P}/estimates/{estimate_id}/` | `BulkEstimatePointEndpoint.partial_update` | `ProjectEntityPermission` (20/15) | B: `estimate?: {"name","type"}`, `estimate_points: [{"id","key","value"}]` (Pflicht, nicht leer) | 200 EstimateReadSerializer | leer → 400 `{"error": "Estimate points are required"}`. Nur Punkte mit passender `id` (dieses Estimate) werden aktualisiert; neue Punkte werden **nicht** angelegt. | (Frontend nutzt E-07/E-08 einzeln) |
| E-06 | `DELETE {P}/estimates/{estimate_id}/` | `BulkEstimatePointEndpoint.destroy` | `ProjectEntityPermission` (20/15) | – | 204 | Soft-Delete; Celery-Kaskade setzt `Project.estimate = NULL` (SET_NULL) und soft-löscht Punkte. | `WEB/services/estimate.service.ts` `deleteEstimate` |
| E-07 | `POST {P}/estimates/{estimate_id}/estimate-points/` | `EstimatePointEndpoint.create` | `allow_permission([A,M])` | B: `key` (int), `value` (str) | 200 EstimatePointSerializer | `key` oder `value` falsy → 400 `{"error": "Key and value are required"}` (**Key 0 nicht anlegbar**); Estimate nicht in Projekt → 404 `{"error": "Estimate not found"}`. Keine Längenprüfung von `value` (nur via Serializer in E-03/E-08). Doppelte Keys möglich. | `WEB/services/estimate.service.ts` `createEstimatePoint` (Store `creteEstimatePoint`, Komponente `WEB/components/estimates/points/create.tsx`) |
| E-08 | `PATCH {P}/estimates/{estimate_id}/estimate-points/{estimate_point_id}/` | `EstimatePointEndpoint.partial_update` | `allow_permission([A,M])` | B: `key`, `value`, `description` | 200 EstimatePointSerializer | `value` > 20 → 400 `{"non_field_errors": ["Value can't be more than 20 characters"]}`; leerer Body → 400 `{"non_field_errors": ["Estimate points are required"]}`. | `WEB/services/estimate.service.ts` `updateEstimatePoint` |
| E-09 | `DELETE {P}/estimates/{estimate_id}/estimate-points/{estimate_point_id}/` | `EstimatePointEndpoint.destroy` | `allow_permission([A,M])` | B: `new_estimate_id` (= ID des **Ersatz-Punkts**, optional) | 200 `[EstimatePointSerializer]` (nur die neu nummerierten Punkte) | Für jedes Issue mit diesem Punkt: Celery `issue_activity("issue.activity.updated", {"estimate_point": new\|null})` (ohne `notification`/`origin`); mit Ersatz → `Issue.estimate_point = new_estimate_id` (Bulk-Update); ohne Ersatz bleibt die FK bis zur Celery-Kaskade (SET_NULL) stehen. Punkt nicht gefunden → 404 `{"error": "Estimate point not found"}` (erst **nach** den Activities!). Alle Punkte mit größerem `key` → `key - 1`. Soft-Delete. | — (kein Service-Aufruf im CE; „Estimate bearbeiten“ mit Punkt-Löschung/Umhängen fehlt in der CE-UI, `WEB/components/estimates/estimate-list-item-buttons.tsx` bietet nur Löschen des ganzen Estimates) |
| T-01 | `GET /api/timezones/` | `TimezoneEndpoint.get` (`V/timezone/base.py`) | `AllowAny` | – | 200 `{"timezones": [{"utc_offset": "UTC+05:30", "gmt_offset": "GMT+05:30", "value": "Asia/Kolkata", "label": "Kolkata"}]}` | 120 feste Einträge (Liste 3.18), aktueller Offset (DST-abhängig) aus `pytz` zum Anfragezeitpunkt, sortiert nach Offset (int aus `%z`) dann Label; `offset` wird entfernt. `cache_page` 2 h. Bug: bei negativen Halbstunden-Offsets falsche Darstellung (3.18). | `WEB/services/timezone.service.ts` |

### 2.9 Endpunkt-Inventar Notifications (`URL/notification.py`) & Webhooks (`URL/webhook.py`)

| ID | Methode & Pfad | View.Methode (Quelle) | Berechtigung | Request | Response | Seiteneffekte / Besonderheiten | FE |
|---|---|---|---|---|---|---|---|
| N-01 | `GET {W}/users/notifications/` | `NotificationViewSet.list` (`V/notification/base.py`) | `allow_permission([A,M,G], WORKSPACE)` | Q: `snoozed` (`true`\|`false`, Default `false`), `archived` (`true`\|`false`, Default `false`), `read` (`true`\|`false`\|fehlt), `type` (kommagetrennt aus `subscribed`, `assigned`, `created`; Default `all`), `mentioned` (jeder nicht-leere Wert = wahr), `per_page`, `cursor`, `order_by` | 200 `[NotificationSerializer]` bzw. paginiert, wenn `per_page` **und** `cursor` | Filterlogik siehe 3.8. Nur `entity_name = "issue"`, nur eigene. Unpaginiert sortiert `snoozed_till ASC, created_at DESC`; paginiert gemäß `order_by` (Default `-created_at`). Ungültiger `snoozed`/`archived`-Wert → `KeyError` → 400 `{"error": "The required key does not exist."}`. | `WEB/services/workspace-notification.service.ts` `fetchNotifications`, `SVC/workspace/notification.service.ts` |
| N-02 | `GET {W}/users/notifications/{pk}/` | `NotificationViewSet.retrieve` (DRF-Default) | authentifiziert; Queryset eigene | – | 200 NotificationSerializer | – | — |
| N-03 | `PATCH {W}/users/notifications/{pk}/` | `NotificationViewSet.partial_update` | A/M/G (WS) | B: `snoozed_till` (ISO-Datetime\|null; **fehlt → null** = Snooze aufheben) | 200 NotificationSerializer | alle anderen Felder werden ignoriert. | `WEB/services/workspace-notification.service.ts` `updateNotificationById` |
| N-04 | `DELETE {W}/users/notifications/{pk}/` | `NotificationViewSet.destroy` (DRF-Default) | authentifiziert; eigene | – | 204 | Soft-Delete. | — |
| N-05 | `POST {W}/users/notifications/{pk}/read/` | `NotificationViewSet.mark_read` | A/M/G | – | 200 NotificationSerializer | `read_at = now`. | `…markNotificationAsRead` |
| N-06 | `DELETE {W}/users/notifications/{pk}/read/` | `NotificationViewSet.mark_unread` | A/M/G | – | 200 NotificationSerializer | `read_at = NULL`. | `…markNotificationAsUnread` |
| N-07 | `POST {W}/users/notifications/{pk}/archive/` | `NotificationViewSet.archive` | A/M/G | – | 200 NotificationSerializer | `archived_at = now`. | `…markNotificationAsArchived` |
| N-08 | `DELETE {W}/users/notifications/{pk}/archive/` | `NotificationViewSet.unarchive` | A/M/G | – | 200 NotificationSerializer | `archived_at = NULL`. | `…markNotificationAsUnArchived` |
| N-09 | `GET {W}/users/notifications/unread/` | `UnreadNotificationEndpoint.get` | A/M/G | – | 200 `{"total_unread_notifications_count": int, "mention_unread_notifications_count": int}` | ungelesen, nicht archiviert, `snoozed_till IS NULL`; „mention“ = `sender ILIKE '%mentioned%'`, „total“ schließt Mentions **aus**. Alle `entity_name`. | `…fetchUnreadNotificationsCount` |
| N-10 | `POST {W}/users/notifications/mark-all-read/` | `MarkAllReadNotificationViewSet.create` | A/M/G | B: `snoozed` (bool), `archived` (bool), `type` (`watching`\|`assigned`\|`created`; Default `all`), (`read` wird ignoriert) | 200 `{"message": "Successful"}` | alle ungelesenen eigenen Notifications nach Snooze-/Archiv-Filter; `type` wird als **einzelner** Wert verglichen – das Frontend sendet kommagetrennte Werte aus `subscribed,assigned,created` (`WEB/store/notifications/workspace-notifications.store.ts`), wodurch nur exakt `assigned` bzw. `created` filtern, `subscribed`/Kombinationen markieren **alle**. Gast + `created` → nichts. Keine Einschränkung auf `entity_name`/Mentions. `bulk_update(read_at)`. | `…markAllNotificationsAsRead` |
| N-11 | `GET {U}/me/notification-preferences/` | `UserNotificationPreferenceEndpoint.get` | authentifiziert | – | 200 `{"id","property_change","state_change","comment","mention","issue_completed","user","workspace","project","created_at","updated_at","deleted_at","created_by","updated_by"}` | Datensatz wird bei User-Anlage per Signal erstellt (`M/user.py` `create_user_notification`, nicht für Bots); fehlt → 404. Steuert **E-Mail**-Benachrichtigungen (A-Task `email_notification_task`). | `WEB/services/user.service.ts` `currentUserEmailNotificationSettings` |
| N-12 | `PATCH {U}/me/notification-preferences/` | `UserNotificationPreferenceEndpoint.patch` | authentifiziert | B: `property_change`, `state_change`, `comment`, `mention`, `issue_completed` (bool) | 200 wie N-11 | – | `WEB/services/user.service.ts` `updateCurrentUserEmailNotificationSettings` |
| WH-01 | `GET {W}/webhooks/` | `WebhookEndpoint.get` (`V/webhook/base.py`) | `allow_permission([A], WORKSPACE)` | – | 200 `[WebhookSerializer]` **ohne** `secret_key`: `id, url, is_active, project, issue, module, cycle, issue_comment, is_internal, version, workspace, created_at, updated_at, deleted_at, created_by, updated_by` | `fields=`-Liste wirkungslos (alle Felder). Enthält auch `is_internal`-Webhooks. | `WEB/services/webhook.service.ts` |
| WH-02 | `POST {W}/webhooks/` | `WebhookEndpoint.post` | A (WS) | B: `url` (Pflicht, ≤ 1024), `is_active` (Default true), `project`, `issue`, `module`, `cycle`, `issue_comment` (bool, Default false) | 201 WebhookSerializer **inkl. `secret_key`** (`plane_wh_<32 hex>`) | Validierung: DRF-`URLField` (Django-`URLValidator`: Hostname braucht TLD, außer `localhost`/IP) → Schema nur http/https (`"Invalid schema. Only HTTP and HTTPS are allowed."`), Domain ≠ `localhost`/`127.0.0.1` (`"Local URLs are not allowed."`); SSRF-Prüfung `UT/ip_address.py` `validate_url` (DNS-Auflösung, private/loopback/reservierte IPs verboten, außer `WEBHOOK_ALLOWED_IPS`; `WEBHOOK_ALLOWED_HOSTS` umgeht IP-Prüfung) → 400 `{"url": "Invalid or disallowed webhook URL."}`; Host in `WEBHOOK_DISALLOWED_DOMAINS` oder = eigener Request-Host (inkl. Subdomains) → 400 `{"url": "URL domain or its subdomain is not allowed."}`. Doppelte URL im Workspace → **409** `{"error": "URL already exists for the workspace"}`. | `WEB/services/webhook.service.ts` `createWebhook` |
| WH-03 | `GET {W}/webhooks/{pk}/` | `WebhookEndpoint.get` | A | – | 200 WebhookSerializer ohne Secret | – | `WEB/services/webhook.service.ts` |
| WH-04 | `PATCH {W}/webhooks/{pk}/` | `WebhookEndpoint.patch` | A | B: wie WH-02 (partiell) | 200 ohne Secret | URL-Prüfungen nur, wenn `url` gesendet. Doppelte URL → `IntegrityError` → 400 `{"error": "The payload is not valid"}` (nicht 409). | `WEB/services/webhook.service.ts` |
| WH-05 | `DELETE {W}/webhooks/{pk}/` | `WebhookEndpoint.delete` | A | – | 204 | Soft-Delete. | `WEB/services/webhook.service.ts` |
| WH-06 | `POST {W}/webhooks/{pk}/regenerate/` | `WebhookSecretRegenerateEndpoint.post` | A | – | 200 WebhookSerializer **inkl. neuem `secret_key`** | – | `WEB/services/webhook.service.ts` `regenerateSecretKey` |
| WH-07 | `GET {W}/webhook-logs/{webhook_id}/` | `WebhookLogsEndpoint.get` | A | – | 200 `[WebhookLogSerializer]` (alle Felder: `id, workspace, webhook, event_type, request_method, request_headers, request_body, response_status, response_headers, response_body, retry_count, created_at, updated_at, deleted_at, created_by, updated_by`), unpaginiert | Aufbewahrung `WEBHOOK_LOG_RETENTION_DAYS` (Default 14) per Cleanup-Task. | — |

### 2.10 Endpunkt-Inventar Assets (`URL/asset.py`)

Allgemein (v2): Upload ist ein **Drei-Schritt-Verfahren** (Details 3.13): (1) `POST` legt `FileAsset` an und liefert ein Presigned-POST-Formular für S3/MinIO; (2) Browser lädt direkt in den Bucket; (3) `PATCH` bestätigt (`is_uploaded=True`) und verknüpft die Entität. Erlaubte MIME-Typen bei allen v2-Upload-Endpunkten dieses Bereichs: `image/jpeg`, `image/png`, `image/webp`, `image/jpg`, `image/gif` (Fehler 400 `{"error": "Invalid file type. Only JPEG, PNG, WebP, JPG and GIF files are allowed.", "status": false}`). Größe: `size_limit = min(size, FILE_SIZE_LIMIT)` (ENV `FILE_SIZE_LIMIT`, Default 5 242 880 Byte), wird als `content-length-range [1, size_limit]` in die Upload-Policy geschrieben. Dateiname: `sanitize_filename` (`UT/path_validator.py`: Steuerzeichen entfernen, `\`→`/`, Basename, `..` entfernen, trim, führende Punkte entfernen; leer → `"unnamed"`). `entity_type`-Werte (`M/asset.py` `FileAsset.EntityTypeContext`): `ISSUE_ATTACHMENT`, `ISSUE_DESCRIPTION`, `COMMENT_DESCRIPTION`, `PAGE_DESCRIPTION`, `USER_COVER`, `USER_AVATAR`, `WORKSPACE_LOGO`, `PROJECT_COVER`, `DRAFT_ISSUE_ATTACHMENT`, `DRAFT_ISSUE_DESCRIPTION`.

Upload-Antwort (A-07, A-11, A-16):
```json
{
  "upload_data": { "url": "https://<bucket-endpoint>/<bucket>", "fields": { "Content-Type": "image/png", "key": "<asset_key>", "x-amz-algorithm": "...", "x-amz-credential": "...", "x-amz-date": "...", "policy": "...", "x-amz-signature": "..." } },
  "asset_id": "<uuid>",
  "asset_url": "/api/assets/v2/static/<uuid>/"
}
```
`upload_data` ist bei S3-Fehler `null`. `asset_url` (`M/asset.py` `FileAsset.asset_url`): `WORKSPACE_LOGO`, `USER_AVATAR`, `USER_COVER`, `PROJECT_COVER` → `/api/assets/v2/static/{id}/`; `ISSUE_ATTACHMENT` → `/api/assets/v2/workspaces/{slug}/projects/{project_id}/issues/{issue_id}/attachments/{id}/`; `ISSUE_DESCRIPTION`, `COMMENT_DESCRIPTION`, `PAGE_DESCRIPTION`, `DRAFT_ISSUE_DESCRIPTION` → `/api/assets/v2/workspaces/{slug}/projects/{project_id}/{id}/`; sonst `null`.

| ID | Methode & Pfad | View.Methode (Quelle) | Berechtigung | Request | Response | Seiteneffekte / Besonderheiten | FE |
|---|---|---|---|---|---|---|---|
| A-01 | `POST {W}/file-assets/` | `FileAssetEndpoint.post` (`V/asset/base.py`, Legacy v1) | `IsAuthenticated` + `WorkspaceMemberPermission` | Multipart/Form/JSON: `asset` (Datei), `attributes` | 201 FileAssetSerializer (alle Felder) | Speicherung über `django-storages` (`upload_to` → `"{workspace_id}/{uuid}-{name}"`). | — |
| A-02 | `GET /api/workspaces/file-assets/{workspace_id}/{asset_key}/` | `FileAssetEndpoint.get` | `IsAuthenticated` + `WorkspaceMemberPermission` (über `workspace_id`) | – | 200 `{"data": [FileAssetSerializer], "status": true}` bzw. 200 `{"error": "Asset key does not exist", "status": false}` | Schlüssel = `"{workspace_id}/{asset_key}"`. | — |
| A-03 | `DELETE /api/workspaces/file-assets/{workspace_id}/{asset_key}/` | `FileAssetEndpoint.delete` | dito + `can_modify_asset` (sonst 403 `{"error": "You don't have the required permissions."}`) | – | 204 | `is_deleted = True` (kein `deleted_at`). | `WEB/services/file.service.ts` `deleteOldWorkspaceAsset`, `SVC/file/file.service.ts` |
| A-04 | `POST /api/workspaces/file-assets/{workspace_id}/{asset_key}/restore/` | `FileAssetViewSet.restore` | dito + `can_modify_asset` | – | 204 | `is_deleted = False`. | `WEB/services/file.service.ts` `restoreOldEditorAsset`, `SVC/file/file.service.ts` |
| A-05 | `POST /api/users/file-assets/` | `UserAssetsEndpoint.post` (Legacy) | authentifiziert | Multipart: `asset`, `attributes` | 201 FileAssetSerializer | ohne Workspace (`upload_to` → `"user-{uuid}-{name}"`). `GET` auf diesen Pfad → 500 (fehlendes `asset_key`). | — |
| A-06 | `GET /api/users/file-assets/{asset_key}/` | `UserAssetsEndpoint.get` | authentifiziert | – | **500** bei Treffer (Serializer ohne `many=True` auf QuerySet), sonst 200 `{"error": "Asset key does not exist", "status": false}` | – | — |
| A-07 | `DELETE /api/users/file-assets/{asset_key}/` | `UserAssetsEndpoint.delete` | authentifiziert, eigenes (`created_by`) | – | 204 / 404 | `is_deleted = True`. | `WEB/services/file.service.ts` `deleteOldUserAsset` |
| A-08 | `POST /api/assets/v2/workspaces/{slug}/` | `WorkspaceFileAssetEndpoint.post` (`V/asset/v2.py`) | `allow_permission([A,M,G], WORKSPACE)`; `WORKSPACE_LOGO` nur WS-Admin (403 `{"error": "Only workspace admins can upload a workspace logo."}`) | B: `name`, `type` (Default `image/jpeg`), `size` (Default `FILE_SIZE_LIMIT`), `entity_type` (Pflicht, ∈ Liste), `entity_identifier` | 200 Upload-Antwort | ungültiger `entity_type` → 400 `{"error": "Invalid entity type.", "status": false}`. Key `"{workspace_id}/{uuid4.hex}-{name}"`. `entity_identifier` → FK je Typ: `WORKSPACE_LOGO`→`workspace_id`, `PROJECT_COVER`→`project_id`, `USER_AVATAR`/`USER_COVER`→`user_id`, `ISSUE_ATTACHMENT`/`ISSUE_DESCRIPTION`→`issue_id`, `PAGE_DESCRIPTION`→`page_id`, `COMMENT_DESCRIPTION`→`comment_id` (Draft-Typen → keine FK). `entity_identifier` wird **nicht** auf Zugehörigkeit geprüft. `attributes = {"name","type","size"}`. | `WEB/services/file.service.ts` `uploadWorkspaceAsset` |
| A-09 | `PATCH /api/assets/v2/workspaces/{slug}/{asset_id}/` | `WorkspaceFileAssetEndpoint.patch` | A/M/G (WS) + Projektmitgliedschaft bei projektgebundenem Asset (403 `{"error": "You don't have access to this asset."}`) + `can_modify_asset` | B: `attributes` (optional, ersetzt) | 204 | `is_uploaded = True`; fehlen `storage_metadata` → Celery `get_asset_object_metadata` (`BG/storage_metadata_task.py`: S3 `HEAD` → `{ContentType, ContentLength, LastModified, ETag, Metadata}`). `WORKSPACE_LOGO`: altes Logo-Asset `is_deleted`, `workspace.logo = ""`, `logo_asset_id = asset`, Cache-Invalidierung `/api/workspaces/`, `/api/users/me/workspaces/`, `/api/instances/`. `PROJECT_COVER`: altes Cover-Asset gelöscht, `project.cover_image = ""`, `cover_image_asset_id = asset`. | `WEB/services/file.service.ts` (intern nach Upload) |
| A-10 | `DELETE /api/assets/v2/workspaces/{slug}/{asset_id}/` | `WorkspaceFileAssetEndpoint.delete` | wie A-09 | – | 204 | `is_deleted = True`, `deleted_at = now` (dadurch für Default-Manager unsichtbar); `WORKSPACE_LOGO` → `workspace.logo_asset_id = NULL` (+ Caches); `PROJECT_COVER` → `project.cover_image_asset_id = NULL`. | `WEB/services/file.service.ts` `deleteWorkspaceAsset` |
| A-11 | `GET /api/assets/v2/workspaces/{slug}/{asset_id}/` | `WorkspaceFileAssetEndpoint.get` | A/M/G + Projektzugriff | – | **302** auf Presigned-GET (`Content-Disposition: attachment; filename*=UTF-8''<name>`) | nicht hochgeladen → 404 `{"error": "The requested asset could not be found."}`. | (Editor-Bilder) |
| A-12 | `POST /api/assets/v2/user-assets/` | `UserAssetsV2Endpoint.post` | authentifiziert | B: `name`, `type`, `size`, `entity_type` (`USER_AVATAR`\|`USER_COVER`) | 200 Upload-Antwort | anderer Typ → 400 `{"error": "Invalid entity type.", "status": false}`. Key `"{uuid4.hex}-{name}"` (ohne Workspace-Präfix), `user = request.user`. | `WEB/services/file.service.ts` `uploadUserAsset` |
| A-13 | `PATCH /api/assets/v2/user-assets/{asset_id}/` | `UserAssetsV2Endpoint.patch` | authentifiziert, eigenes (`user_id`) | B: `attributes` | 204 | `is_uploaded`, Metadaten-Task; `USER_AVATAR`: `user.avatar = ""`, altes Avatar-Asset (nur wenn dem User gehörig) `is_deleted`+`deleted_at`, `avatar_asset_id = asset`; `USER_COVER` analog (`cover_image = None`); Cache-Invalidierung `/api/users/me/`, `/api/users/me/settings/`. | `WEB/services/file.service.ts` (intern) |
| A-14 | `DELETE /api/assets/v2/user-assets/{asset_id}/` | `UserAssetsV2Endpoint.delete` | authentifiziert, eigenes | – | 204 | `is_deleted`, `deleted_at`; `avatar_asset_id`/`cover_image_asset_id = NULL`; Caches. | `WEB/services/file.service.ts` `deleteUserAsset` |
| A-15 | `POST /api/assets/v2/workspaces/{slug}/restore/{asset_id}/` | `AssetRestoreEndpoint.post` | A/M/G (WS) + `can_modify_asset` | – | 204 | sucht über `all_objects` (auch soft-gelöscht); `is_deleted = False`, `deleted_at = NULL`. | `WEB/services/file.service.ts` `restoreNewAsset` |
| A-16 | `GET /api/assets/v2/static/{asset_id}/` | `StaticFileAssetEndpoint.get` | `AllowAny` (anonym: 30/min) | – | **302** auf Presigned-GET; inline nur bei `attributes.type` ∈ `INLINE_SAFE_MIME_TYPES` (`image/jpeg`, `image/jpg`, `image/png`, `image/gif`, `image/webp`; dann `ResponseContentType` gepinnt), sonst attachment | nicht hochgeladen → 404 `{"error": "The requested asset could not be found."}`; Typ ∉ {`USER_AVATAR`, `USER_COVER`, `WORKSPACE_LOGO`, `PROJECT_COVER`} → 400 `{"error": "Invalid entity type.", "status": false}`. Öffentlich, damit `<img src>` ohne Auth funktioniert. | (alle `avatar_url`/`logo_url`/`cover_image_url`) |
| A-17 | `POST /api/assets/v2/workspaces/{slug}/projects/{project_id}/` | `ProjectAssetEndpoint.post` | `allow_permission([A,M,G])` (PROJECT) | B: `name`, `type`, `size`, `entity_type` (∈ Liste), `entity_identifier` | 200 Upload-Antwort | wie A-08, zusätzlich `project_id` gesetzt und `DRAFT_ISSUE_DESCRIPTION` → `draft_issue_id`. | `WEB/services/file.service.ts` `uploadProjectAsset` |
| A-18 | `PATCH /api/assets/v2/workspaces/{slug}/projects/{project_id}/{pk}/` | `ProjectAssetEndpoint.patch` | A/M/G (PROJECT) + `can_modify_asset` | B: `attributes` | 204 | `is_uploaded`, Metadaten-Task (keine Entitätsverknüpfung). | `WEB/services/file.service.ts` (intern) |
| A-19 | `DELETE /api/assets/v2/workspaces/{slug}/projects/{project_id}/{pk}/` | `ProjectAssetEndpoint.delete` | A/M/G + `can_modify_asset` | – | 204 | `is_deleted`, `deleted_at`. | `WEB/services/file.service.ts` `deleteNewAsset` (über `asset_url`) |
| A-20 | `GET /api/assets/v2/workspaces/{slug}/projects/{project_id}/{pk}/` | `ProjectAssetEndpoint.get` | A/M/G (PROJECT) | – | 302 Presigned-GET (attachment) / 404 | – | (Editor-Bilder über `asset_url`) |
| A-21 | `POST /api/assets/v2/workspaces/{slug}/projects/{project_id}/{entity_id}/bulk/` | `ProjectBulkAssetEndpoint.post` | A/M/G (PROJECT) | B: `asset_ids: [uuid…]` | 204 | leer → 400 `{"error": "No asset ids provided."}`. Nur **eigene** Assets (`created_by`) des Workspaces mit `project_id = URL-Projekt` oder `NULL`; keines → 404 `{"error": "The requested asset could not be found."}`. Typ des **ersten** Assets bestimmt die Aktion: `PROJECT_COVER` → `can_modify_asset` gegen Ziel-Projekt (403), `project_id` setzen, `project.cover_image_asset_id` setzen; `ISSUE_DESCRIPTION` → `issue_id=entity_id, project_id`; `COMMENT_DESCRIPTION` → `comment_id`; `PAGE_DESCRIPTION` → `page_id`; `DRAFT_ISSUE_DESCRIPTION` → `draft_issue_id` (IntegrityErrors bei gelöschter Entität werden verschluckt). | `WEB/services/file.service.ts` `updateBulkProjectAssetsUploadStatus` |
| A-22 | `GET /api/assets/v2/workspaces/{slug}/check/{asset_id}/` | `AssetCheckEndpoint.get` | A/M/G (WS) | – | 200 `{"exists": bool}` | nicht soft-gelöscht (`deleted_at IS NULL`), unabhängig von `is_deleted`/`is_uploaded`. | `WEB/services/file.service.ts` `checkIfAssetExists` |
| A-23 | `POST /api/assets/v2/workspaces/{slug}/duplicate-assets/{asset_id}/` | `DuplicateAssetEndpoint.post` | A/M/G (WS); Throttle 5/min **pro Quell-Asset** | B: `entity_type` (Pflicht, ∈ Liste), `entity_id`, `project_id` | 200 `{"asset_id": "<neue uuid>"}` | ungültiger Typ → 400 `{"error": "Invalid entity type or entity id"}`; `project_id` nicht im Workspace → 404 `{"error": "Project not found"}`; Quelle muss hochgeladen und im **selben** Workspace sein → sonst 404 `{"error": "Asset not found"}`. Neuer Key `"{workspace_id}/{uuid}-{sanitized name}"`, Attribute/`size`/`storage_metadata` kopiert, FK je Typ wie A-08, S3 `copy_object`, danach `is_uploaded = True`. | `WEB/services/file.service.ts` `duplicateAsset` |
| A-24 | `GET /api/assets/v2/workspaces/{slug}/download/{asset_id}/` | `WorkspaceAssetDownloadEndpoint.get` | A/M/G (WS) | – | 302 Presigned-GET attachment (Dateiname = `attributes.name` oder zufällig) | nicht hochgeladen → 404 `{"error": "The requested asset could not be found."}`. **Keine** Projektzugriffsprüfung (im Gegensatz zu A-11). | `packages/utils/src/editor/common.ts` (Download-Link) |
| A-25 | `GET /api/assets/v2/workspaces/{slug}/projects/{project_id}/download/{asset_id}/` | `ProjectAssetDownloadEndpoint.get` | `allow_permission([A,M,G], PROJECT)` | – | 302 Presigned-GET attachment | – | `packages/utils/src/editor/common.ts` |

**Vom Frontend aufgerufen, im CE-Backend nicht vorhanden:** `POST /api/assets/v2/workspaces/{slug}/{entity_id}/bulk/` (`WEB/services/file.service.ts` `updateBulkWorkspaceAssetsUploadStatus`, genutzt von `WEB/components/comments/comment-create.tsx` für Kommentare **ohne** Projekt) und `POST /api/assets/v2/workspaces/{slug}/duplicate-assets/` (Batch, `SVC/file/file.service.ts` `duplicateAssets`, im Code nicht aufgerufen) → 404.

### 2.11 Endpunkt-Inventar Suche (`URL/search.py`), Export (`URL/exporter.py`), Analytics (`URL/analytic.py`), External (`URL/external.py`)

| ID | Methode & Pfad | View.Methode (Quelle) | Berechtigung | Request | Response | Seiteneffekte / Besonderheiten | FE |
|---|---|---|---|---|---|---|---|
| SR-01 | `GET {W}/search/` | `GlobalSearchEndpoint.get` (`V/search/base.py`) | nur `IsAuthenticated` (Scoping in den Abfragen) | Q: `search` (Suchtext), `entities` (kommagetrennt aus `workspace`, `project`, `issue`, `cycle`, `module`, `issue_view`, `page`, `intake`; Default alle; unbekannte ignoriert), `workspace_search` (`"true"`\|`"false"`, Default `"false"`), `project_id` | 200 `{"results": {"workspace": [{"name","id","slug"}], "project": [{"name","id","identifier","workspace__slug"}], "issue": [{"name","id","sequence_id","project__identifier","project_id","workspace__slug"}], "cycle": [{"name","id","project_id","project__identifier","workspace__slug"}], "module": [...wie cycle], "issue_view": [...wie cycle], "page": [{"name","id","project_ids","project_identifiers","workspace__slug"}], "intake": [...wie issue]}}` | Details 3.14. Nur `issue`/`intake` sind auf 100 begrenzt, alle anderen **unbegrenzt**; ohne `search` werden alle sichtbaren Objekte geliefert. | `WEB/services/workspace.service.ts` `searchWorkspace`, `SVC/workspace/workspace.service.ts` |
| SR-02 | `GET {P}/search-issues/` | `IssueSearchEndpoint.get` (`V/search/issue.py`) | nur `IsAuthenticated` (Scoping in Abfrage) | Q: `search`, `workspace_search` (Default `"false"`), `parent` (`"true"`), `issue_relation` (`"true"`), `sub_issue` (`"true"`), `cycle` (`"true"`), `module` (Modul-UUID), `target_date` (`"none"`), `issue_id` | 200 (max. 100) `[{"name","id","start_date","sequence_id","project__name","project__identifier","project_id","workspace__slug","state__name","state__group","state__color"}]` | Picker für Parent/Relation/Sub-Issue/Cycle/Module/Gantt (3.14.3). Keine Sortierung (DB-Reihenfolge). `sub_issue=true` mit unbekannter `issue_id` → 500. | `WEB/services/project/project.service.ts` `projectIssuesSearch` |
| SR-03 | `GET {W}/entity-search/` | `SearchEndpoint.get` (`V/search/base.py`) | `WorkspaceUserPermission` | Q: `query`, `query_type` (kommagetrennt aus `user_mention`, `project`, `issue`, `cycle`, `module`, `page`; Default `user_mention`), `count` (int, Default 5), `project_id` (optional), (`team_id`, `issue_id` vom Frontend gesendet, ignoriert) | 200 `{"user_mention": [{"member__avatar_url","member__display_name","member__id"}], "project": [{"name","id","identifier","logo_props","workspace__slug"}], "issue": [{"name","id","sequence_id","project__identifier","project_id","priority","state_id","type_id"}], "cycle": [{"name","id","project_id","project__identifier","status","workspace__slug"}], "module": [{"name","id","project_id","project__identifier","status","workspace__slug"}], "page": [{"name","id","logo_props","projects__id","workspace__slug"}]}` (nur angefragte Typen) | Mentions im Editor, Entity-Picker. Details 3.14.2. `count` nicht-int → 500. | `WEB/services/workspace.service.ts` `searchEntity` |
| X-01 | `POST {W}/export-issues/` | `ExportIssuesEndpoint.post` (`V/exporter/base.py`) | `allow_permission([A,M], WORKSPACE)` | B: `provider` (`csv`\|`xlsx`\|`json`, Pflicht), `project` (UUID-Liste, optional), `multiple` (bool: eine Datei je Projekt) | 200 `{"message": "Once the export is ready you will be able to download it"}` | anderer Provider → 400 `{"error": "Provider '<provider>' not found."}`. Ohne `project`: alle nicht archivierten Projekte mit aktiver Mitgliedschaft. `ExporterHistory(type="issue_exports", status="queued", initiated_by=user, project=[…])`. Celery `issue_export_task` (`BG/export_task.py`): Status `processing`, Issues der Projekte, in denen der Initiator **aktives** Mitglied ist (Gäste ohne `guest_view_all_features` nur eigene), Datei(en) via `DataExporter` (`UT/porters/*`), ZIP, Upload `"{workspace_id}/export-{slug}-{token[:6]}-{date}.zip"`, Presigned-URL **7 Tage** → `status="completed"`, `url`, `key` (bzw. `failed`). Übergebene `project`-IDs werden in der View nicht geprüft (Task filtert über Mitgliedschaft). | `WEB/services/project/project-export.service.ts` |
| X-02 | `GET {W}/export-issues/` | `ExportIssuesEndpoint.get` | A/M (WS) | Q: `per_page` **und** `cursor` (Pflicht), `order_by` (`created_at`\|`updated_at`, Default `-created_at`) | 200 paginiert `[ExporterHistorySerializer]` (`id, created_at, updated_at, project, provider, status, url, initiated_by, initiated_by_detail{UserLite}, token, created_by, updated_by`) | ohne beide Parameter → 400 `{"error": "per_page and cursor are required"}`. Liefert **alle** Exporte des Workspaces (aller User). | `WEB/services/integrations/integration.service.ts` (ohne Trailing Slash) |
| AN-01 | `GET {W}/analytics/` | `AnalyticsEndpoint.get` (`V/analytic/base.py`) | A/M (WS) | Q: `x_axis` (Pflicht, ∈ `VALID_ANALYTICS_FIELDS`), `y_axis` (Pflicht, `issue_count`\|`estimate`), `segment` (∈ `VALID_ANALYTICS_FIELDS`, ≠ `x_axis`), Legacy-Issue-Filter | 200 `{"total": int, "distribution": {"<dimension>": [{"dimension", "segment"?, "count"\|"estimate"}]}, "extras": {"state_details": [{"state_id","state__name","state__color"}], "assignee_details": [{"assignees__avatar_url","assignees__display_name","assignees__first_name","assignees__last_name","assignees__id"}], "label_details": [{"labels__id","labels__color","labels__name"}], "cycle_details": [{"issue_cycle__cycle_id","issue_cycle__cycle__name"}], "module_details": [{"issue_module__module_id","issue_module__module__name"}]}}` | Fehler 400 `{"error": "x-axis and y-axis dimensions are required and the values should be valid"}` / `{"error": "Both segment and x axis cannot be same and segment should be valid"}`. `extras.*` nur gefüllt, wenn Achse/Segment das jeweilige Feld ist, sonst `{}`. Plot-Logik 3.15.1. Legacy (UI nutzt AN-11 ff.). | — |
| AN-02 | `GET {W}/analytic-view/` | `AnalyticViewViewset.list` (DRF-Default) | `WorkSpaceAdminPermission` (A/M) | – | 200 `[AnalyticViewSerializer]` (`id, workspace, name, description, query, query_dict, created_at, updated_at, deleted_at, created_by, updated_by`) | – | — |
| AN-03 | `POST {W}/analytic-view/` | `AnalyticViewViewset.create` | A/M | B: `name` (Pflicht), `description`, `query_dict` (Filter-Dict) | 201 | `query = issue_filters(query_dict, "POST")` (serverseitig berechnete ORM-Filter). | — |
| AN-04 | `GET {W}/analytic-view/{pk}/` | `AnalyticViewViewset.retrieve` | A/M | – | 200 | – | — |
| AN-05 | `PATCH {W}/analytic-view/{pk}/` | `AnalyticViewViewset.partial_update` | A/M | B: `name`, `description`, `query_dict` | 200 | **Bug:** liest `validated_data["query_data"]` (existiert nicht) → `query` wird bei **jedem** Update auf `{}` zurückgesetzt. | — |
| AN-06 | `DELETE {W}/analytic-view/{pk}/` | `AnalyticViewViewset.destroy` | A/M | – | 204 | Soft-Delete. | — |
| AN-07 | `GET {W}/saved-analytic-view/{analytic_id}/` | `SavedAnalyticEndpoint.get` | A/M (WS) | Q: `segment` | 200 `{"total": int, "distribution": {...}}` | Filter = gespeichertes `query`; Achsen aus `query_dict["x_axis"/"y_axis"]`; Fehlertexte wie AN-01. | — |
| AN-08 | `POST {W}/export-analytics/` | `ExportAnalyticsEndpoint.post` | A/M (WS) | B: `x_axis`, `y_axis`, `segment`, Filter | 200 `{"message": "Once the export is ready it will be emailed to you at <email>"}` | Validierung wie AN-01. Celery `analytic_export_task(email, data, slug, user_id)` (`BG/analytic_plot_export.py`): CSV (segmentiert/nicht segmentiert) per E-Mail. | — |
| AN-09 | `GET {W}/default-analytics/` | `DefaultAnalyticsEndpoint.get` | A/M/G (WS) | Q: Legacy-Issue-Filter | 200 `{"total_issues", "total_issues_classified": [{"state_group","state_count"}], "open_issues", "open_issues_classified": [...], "issue_completed_month_wise": [{"month","count"}], "most_issue_created_user": [{"created_by__first_name","created_by__last_name","created_by__display_name","created_by__id","count","created_by__avatar_url"}] (Top 5), "most_issue_closed_user": [{"assignees__…","count"}] (Top 5), "pending_issue_user": [...], "open_estimate_sum", "total_estimate_sum"}` | Basis: `Issue.issue_objects` aktiver Mitgliedsprojekte. `open` = Gruppen backlog/unstarted/started; Monatsstatistik nur laufendes Jahr. `*_estimate_sum` summieren das **Legacy-Feld `Issue.point`** (praktisch `null`). | — |
| AN-10 | `GET {W}/project-stats/` | `ProjectStatsEndpoint.get` | A/M/G (WS) | Q: `fields` (kommagetrennt aus `total_issues`, `completed_issues`, `total_members`, `total_cycles`, `total_modules`; leer/ungültig → alle), `project_ids` (kommagetrennt) | 200 `[{"id", <angefragte Felder>}]` | Sichtbarkeit wie Projektliste (Admin alle, Member eigene + public, Gast eigene). `completed_issues` zählt **completed + cancelled**; `total_members` = aktive Nicht-Bot-Mitglieder; Cycles/Modules inkl. archivierter. | `WEB/services/project/project.service.ts` `getProjectAnalyticsCount` |
| AN-11 | `GET {W}/advance-analytics/` | `AdvanceAnalyticsEndpoint.get` (`V/analytic/advance.py`) | A/M (WS) | Q: `tab` (`overview`\|`work-items`, Default `overview`), `date_filter` (`yesterday`\|`last_7_days`\|`last_30_days`\|`last_3_months`; `custom` ohne Start/Ende → wirkungslos), `project_ids` (kommagetrennt) | 200 `overview`: `{"total_users":{"count"}, "total_admins", "total_members", "total_guests", "total_projects", "total_work_items", "total_cycles", "total_intake"}`; `work-items`: `{"total_work_items":{"count"}, "started_work_items", "backlog_work_items", "un_started_work_items", "completed_work_items"}` | sonst 400 `{"message": "Invalid tab"}`. Details 3.15.2. | `WEB/services/analytics.service.ts` `getAdvanceAnalytics` |
| AN-12 | `GET {W}/advance-analytics-stats/` | `AdvanceAnalyticsStatsEndpoint.get` | A/M (WS) | Q: `type` (`work-items`, Default), `date_filter` (hier **ohne Wirkung**), `project_ids` | 200 `[{"project_id","project__name","cancelled_work_items","completed_work_items","backlog_work_items","un_started_work_items","started_work_items"}]` sortiert nach `project_id` | sonst 400 `{"message": "Invalid type"}`. | `WEB/services/analytics.service.ts` `getAdvanceAnalyticsStats` |
| AN-13 | `GET {W}/advance-analytics-charts/` | `AdvanceAnalyticsChartEndpoint.get` | A/M (WS) | Q: `type` (`projects` Default\|`custom-work-items`\|`work-items`), `x_axis` (Default `PRIORITY`), `group_by`, `date_filter`, `project_ids` | 200 `projects`: `[{"key","name","count"}]` für `work_items, cycles, modules, intake, members, pages, views`; `custom-work-items`: `{"data": [...], "schema": {...}}` (3.15.3); `work-items`: `{"data": [{"key","name","count","completed_issues","created_issues"}], "schema": {"completed_issues": "completed_issues", "created_issues": "created_issues"}}` | sonst 400 `{"message": "Invalid type"}`; ungültige `x_axis`/`group_by` → 400 `["Invalid x_axis field: <x>"]` bzw. `["Invalid group_by field: <x>"]`. | `WEB/services/analytics.service.ts` `getAdvanceAnalyticsCharts` |
| AN-14 | `GET {P}/advance-analytics/` | `ProjectAdvanceAnalyticsEndpoint.get` (`V/analytic/project_analytics.py`) | `allow_permission([A,M])` (PROJECT) | Q: `cycle_id`, `module_id`, `date_filter`, `project_ids`, (`tab` ignoriert) | 200 `{"total_work_items":{"count"}, "started_work_items", "backlog_work_items", "un_started_work_items", "completed_work_items"}` | Peek-View (Cycle/Module/Projekt). Bei `cycle_id`/`module_id` Issues über `CycleIssue`/`ModuleIssue` (gefiltert über Basisfilter), sonst Projekt. | `WEB/services/analytics.service.ts` (Peek-View: `isPeekView` → Projekt-Pfad aus erstem `project_ids`) |
| AN-15 | `GET {P}/advance-analytics-stats/` | `ProjectAdvanceAnalyticsStatsEndpoint.get` | `allow_permission([A,M])` | Q: `type` (`work-items`), `cycle_id`, `module_id`, `date_filter`, `project_ids` | 200 `[{"display_name","assignee_id","avatar_url","cancelled_work_items","completed_work_items","backlog_work_items","un_started_work_items","started_work_items"}]` sortiert nach `display_name` (eine Zeile `display_name=null` für nicht zugewiesene) | sonst 400 `{"message": "Invalid type"}`. Zählung `distinct`. | `WEB/services/analytics.service.ts` |
| AN-16 | `GET {P}/advance-analytics-charts/` | `ProjectAdvanceAnalyticsChartEndpoint.get` | `allow_permission([A,M,G])` | Q: `type` (`custom-work-items`\|`work-items`; Default `projects` → 400), `x_axis`, `group_by`, `cycle_id`, `module_id`, `date_filter`, `project_ids` | 200 wie AN-13 (`custom-work-items`, `work-items`) | `work-items` mit Cycle/Module: **Tagesreihe** von Start- bis Enddatum, „created“ = Datum, an dem das Issue dem Cycle/Modul **hinzugefügt** wurde (`CycleIssue.created_at`), `count = created + completed`; Cycle/Modul ohne Startdatum → `{"data": [], "schema": {}}`. Ohne: **Monatsreihe** ab Projekt-Erstellungsmonat bis aktueller Monat. | `WEB/services/analytics.service.ts` |
| EXT-01 | `GET /api/unsplash/` | `UnsplashEndpoint.get` (`V/external/base.py`) | authentifiziert | Q: `query`, `page` (Default 1), `per_page` (Default 20) | Status und JSON der Unsplash-API **unverändert durchgereicht**; ohne Access-Key 200 `[]` | mit `query`: `https://api.unsplash.com/search/photos/?client_id=…&query=…&page=$<page>&per_page=…` (**Bug: `$` vor page**), sonst `https://api.unsplash.com/photos/?client_id=…&page=…&per_page=…`. Kein Timeout. Key aus `UNSPLASH_ACCESS_KEY` (Instanz-Config, verschlüsselt) bzw. ENV. Frontend liest `res.data.results ?? res.data`. | `WEB/services/file.service.ts` `getUnsplashImages` |
| EXT-02 | `POST {P}/ai-assistant/` | `GPTIntegrationEndpoint.post` | `allow_permission([A,M])` (PROJECT) | B: `task` (Pflicht), `prompt` | 200 `{"response": str, "response_html": str ("\n"→"<br/>"), "project_detail": ProjectLite, "workspace_detail": WorkspaceLite}` | LLM-Aufruf 3.17. Fehler: Konfiguration fehlt → 400 `{"error": "LLM provider API key and model are required"}`; `task` fehlt → 400 `{"error": "Task is required"}`; LLM-Fehler → 500 `{"error": "An internal error has occurred."}`. | — |
| EXT-03 | `POST {W}/ai-assistant/` | `WorkspaceGPTIntegrationEndpoint.post` | `allow_permission([A,M], WORKSPACE)` | B: `task` (Pflicht), `prompt` | 200 `{"response", "response_html"}` | wie EXT-02. Frontend: „Beschreibung generieren“ im Issue-Modal (`task = "Generate a proper description for this work item."`, `prompt = Titel`; `response == ""` → Toast „Work item title isn't informative enough …“) und GPT-Assistent-Popover (`WEB/components/core/modals/gpt-assistant-popover.tsx`); 429 wird im Frontend als „maximum number of requests of 50 requests per month per user“ angezeigt (Cloud-Limit, Backend CE liefert nie 429 hier). Anzeige nur bei `config.has_llm_configured`. | `WEB/services/ai.service.ts` `createGptTask` |

**Vom Frontend aufgerufen, im CE-Backend nicht vorhanden:** `POST {W}/rephrase-grammar/` (`WEB/services/ai.service.ts` `performEditorTask`, `SVC/ai/ai.service.ts`; genutzt vom Seiten-Editor-KI-Menü `WEB/components/pages/editor/ai/menu.tsx`, Payload `{task: "ASK_ANYTHING", text_input, casual_score?, formal_score?}`, Antwort `{response}`) → 404. Siehe 2.15 und 5.2.

### 2.12 Serializer-Inventar

„BaseModel-Felder“ = `id, created_at, updated_at, deleted_at, created_by, updated_by` (`M/base.py`, `apps/api/plane/db/mixins.py`). FK-Felder werden als UUID serialisiert (Feldname ohne `_id`, z. B. `workspace`), sofern nicht anders angegeben.

| Serializer | Quelle | Basis | Felder (Ausgabe) | Read-only / Write-Regeln | Validierung / Logik |
|---|---|---|---|---|---|
| `WorkSpaceSerializer` | `S/workspace.py` | Dynamic | alle Workspace-Felder (2.13) + `total_members` (int), `logo_url` (str), `role` (int) | RO: `id, created_by, updated_by, created_at, updated_at, owner, logo_url, deleted_at` (+ die drei Zusatzfelder) | `validate_name`: keine URL (`UT/url.py` `contains_url`: http(s)-URLs, `www.`-Hosts, Domains mit TLD 2–6, IPv4; Eingaben > 1000 Zeichen → nicht geprüft), mind. ein Unicode-Buchstabe/-Ziffer (`has_alphanumeric`); `validate_slug`: nicht reserviert, `^[a-zA-Z0-9_-]+$` |
| `WorkspaceLiteSerializer` | `S/workspace.py` | Base | `name, slug, id, logo_url` | alle RO | – |
| `WorkSpaceMemberSerializer` | `S/workspace.py` | Dynamic | alle WorkspaceMember-Felder, `member` = `UserLiteSerializer` | RO: `id, workspace, is_active, created_by, updated_by, created_at, updated_at, deleted_at`, `member` | – |
| `WorkspaceMemberAdminSerializer` | `S/workspace.py` | ↑ | wie oben, `member` = `UserAdminLiteSerializer` | – | – |
| `WorkspaceMemberMeSerializer` | `S/workspace.py` | Base | alle WorkspaceMember-Felder (`member` als UUID) + `draft_issue_count` | – | – |
| `WorkSpaceMemberInviteSerializer` | `S/workspace.py` | Base | alle Invite-Felder, `workspace` = Lite, `invite_link` | RO: `id, email, token, workspace, message, responded_at, created_at, updated_at, invite_link` | `invite_link` = `/workspace-invitations/?invitation_id={id}&slug={slug}&token={token}` |
| `WorkSpaceMemberInvitePublicSerializer` | `S/workspace.py` | Base | `id, email, workspace (Lite), role, message, accepted, responded_at, created_at, updated_at, created_by` | alle RO | – |
| `WorkspaceThemeSerializer` | `S/workspace.py` | Base | alle WorkspaceTheme-Felder | RO: `workspace, actor` | – |
| `WorkspaceUserPropertiesSerializer` | `S/workspace.py` | Base | alle WorkspaceUserProperties-Felder | RO: `workspace, user` | – |
| `WorkspaceUserLinkSerializer` | `S/workspace.py` | Base | alle WorkspaceUserLink-Felder | RO: `workspace, owner` | `to_internal_value`: `url` ohne `http://`/`https://` → `"http://" + url`; `validate_url`: Django-`URLValidator`; `create`/`update`: Duplikat (`url`, Workspace, Owner) → `{"error": "URL already exists for this workspace and owner"}` |
| `IssueRecentVisitSerializer` | `S/workspace.py` | ModelSerializer | `id, name, state, priority, assignees (IDs aktiver Zuordnungen), type, sequence_id, project_id, project_identifier` | – | – |
| `ProjectRecentVisitSerializer` | `S/workspace.py` | ModelSerializer | `id, name, logo_props, project_members (IDs aktiver Nicht-Bot-Mitglieder), identifier` | – | – |
| `PageRecentVisitSerializer` | `S/workspace.py` | ModelSerializer | `id, name, logo_props, project_id (erstes verknüpftes Projekt), owned_by, project_identifier` | – | – |
| `WorkspaceRecentVisitSerializer` | `S/workspace.py` | Base | `id, entity_name, entity_identifier, entity_data, visited_at` | – | `entity_data` per `get_entity_model_and_serializer` (issue/page/project), Objekt per `objects.get(pk)` (Soft-Delete-gefiltert, **ohne** Rechteprüfung), fehlt → `null` |
| `WorkspaceHomePreferenceSerializer` | `S/workspace.py` | Base | `key, is_enabled, sort_order` | `read_only_fields` nennt nur nicht enthaltene Felder → `key` beschreibbar | – |
| `StickySerializer` | `S/workspace.py` | Base | alle Sticky-Felder | RO: `workspace, owner`; `name` optional | `validate`: `description_html` via `validate_html_content` (Sanitizing, ungültig → `{"error": "html content is not valid"}`), `description_binary` via `validate_binary_data` (Base64, ≤ 10 MB, ≥ 4 Byte, keine verdächtigen HTML/JS-Muster → `{"description_binary": "Invalid binary data"}`) |
| `WorkspaceUserPreferenceSerializer` | `S/workspace.py` | Base | `key, is_pinned, sort_order` | – | (nur `get_serializer_class`, nicht aktiv genutzt) |
| `ProjectSerializer` | `S/project.py` | Base | alle Project-Felder + `workspace_detail` (Lite, RO), `inbox_view` (RO, Quelle `intake_view`) | RO: `workspace, deleted_at` | `validate_name`/`validate_identifier`: Sonderzeichen-Regex `Project.FORBIDDEN_IDENTIFIER_CHARS_PATTERN = ^.*[&+,:;$^}{*=?@#\|'<>.()%!-].*$`, Eindeutigkeit im Workspace (Kontext `workspace_id`, beim Update exkl. sich selbst); `validate`: `description_html` sanitisieren; `create`: Projekt + `ProjectIdentifier` |
| `ProjectLiteSerializer` | `S/project.py` | Base | `id, identifier, name, cover_image, cover_image_url, logo_props, description` | alle RO | – |
| `ProjectListSerializer` | `S/project.py` | Dynamic | alle Project-Felder + `is_favorite`, `sort_order`, `member_role`, `anchor`, `members` (UUID-Liste), `cover_image_url`, `inbox_view`, `next_work_item_sequence` | Zusatzfelder RO; Modellfelder **alle beschreibbar** (relevant für P-05) | `members` aus Prefetch `members_list` (aktiv, kein Bot); `next_work_item_sequence` = `max(IssueSequence.sequence)+1` bzw. 1 (eine Query pro Projekt!) |
| `ProjectDetailSerializer` | `S/project.py` | Base | alle Project-Felder, `default_assignee`/`project_lead` als UserLite, `is_favorite`, `sort_order`, `member_role`, `anchor` | – | in diesem Bereich ungenutzt |
| `ProjectMemberSerializer` | `S/project.py` | Base | alle ProjectMember-Felder, `workspace`/`project`/`member` als Lite-Objekte | RO: `deleted_at, created_by, updated_by` + verschachtelte | – |
| `ProjectMemberAdminSerializer` | `S/project.py` | Base | wie oben, `member` = UserAdminLite | – | – |
| `ProjectMemberRoleSerializer` | `S/project.py` | Dynamic | `id, role, member, project, original_role, created_at` | RO: `original_role, created_at` | – |
| `ProjectMemberPreferenceSerializer` | `S/project.py` | Base | `preferences, project_id, member_id, workspace_id` | – | `validate_preferences`: `instance.preferences.update(value)` (flacher Merge) |
| `ProjectMemberInviteSerializer` | `S/project.py` | Base | alle ProjectMemberInvite-Felder (inkl. `token`), `project`/`workspace` Lite | – | – |
| `ProjectMemberInvitePublicSerializer` | `S/project.py` | Base | `id, project, workspace, role, message, accepted, responded_at` | alle RO | – |
| `ProjectIdentifierSerializer` | `S/project.py` | Base | alle Felder | – | ungenutzt |
| `ProjectMemberLiteSerializer` | `S/project.py` | Base | `member (UserLite), id, is_subscribed` | RO | in A04 genutzt |
| `DeployBoardSerializer` | `S/project.py` | Base | alle DeployBoard-Felder + `project_details` (ProjectLite), `workspace_detail` (WorkspaceLite) | RO: `workspace, project, anchor, entity_identifier, entity_name` | `validate_intake`: Intake muss zum Projekt der Instanz gehören → `"Intake is not valid please pass a valid intake"` |
| `ProjectPublicMemberSerializer` | `S/project.py` | Base | alle Felder | RO: `workspace, project, member` | Space-Bereich |
| `UserSerializer` | `S/user.py` | Base | alle `User`-Felder außer `password` | RO: `id, username, mobile_number, email, token, created_at, updated_at, is_superuser, is_staff, is_managed, last_active, last_login_time, last_logout_time, last_login_ip, last_logout_ip, last_login_uagent, last_location, last_login_medium, created_location, is_bot, is_password_autoset, is_email_verified, is_active, token_updated_at` (`date_joined` implizit RO) | `validate_first_name`/`validate_last_name`: keine URL; `validate_avatar_asset`/`validate_cover_image_asset`: `None` oder eigenes Asset (`asset.user_id == instance.id`) passenden Typs, sonst `"Invalid asset."` |
| `UserMeSerializer` | `S/user.py` | Base | siehe U-01 | alle RO | – |
| `UserMeSettingsSerializer` | `S/user.py` | Base | `id, email, workspace` | alle RO | `get_workspace` siehe U-05 |
| `UserLiteSerializer` | `S/user.py` | Base | `id, first_name, last_name, avatar, avatar_url, is_bot, display_name` | RO: `id, is_bot` | – |
| `UserAdminLiteSerializer` | `S/user.py` | Base | `id, first_name, last_name, avatar, avatar_url, is_bot, display_name, email, last_login_medium` | RO: `id, is_bot` | – |
| `ChangePasswordSerializer`, `ResetPasswordSerializer` | `S/user.py` | Serializer | `old_password, new_password (≥8), confirm_password (≥8)` bzw. `new_password` | – | gleich alt → `{"error": "New password cannot be same as old password."}`; Bestätigung ≠ → `{"error": "Confirm password should be same as the new password."}` (genutzt im Auth-Bereich) |
| `ProfileSerializer` | `S/user.py` | Base | alle Profile-Felder | RO: `user` | – |
| `AccountSerializer` | `S/user.py` | Base | alle Account-Felder (inkl. Tokens) | RO: `user` | – |
| `StateSerializer` | `S/state.py` | Base | `id, project_id, workspace_id, name, color, group, default, description, sequence, order` | RO: `workspace, project, default`; `order` optional (nicht persistiert) | `validate`: `group == "triage"` → `"Cannot create triage state"` |
| `StateLiteSerializer` | `S/state.py` | Base | `id, name, color, group` | alle RO | – |
| `EstimateSerializer` | `S/estimate.py` | Base | alle Estimate-Felder | RO: `workspace, project` | – |
| `EstimatePointSerializer` | `S/estimate.py` | Base | alle EstimatePoint-Felder | RO: `estimate, workspace, project` | `validate`: leer → `"Estimate points are required"`; `value` > 20 Zeichen → `"Value can't be more than 20 characters"` |
| `EstimateReadSerializer` / `WorkspaceEstimateSerializer` | `S/estimate.py` | Base | alle Estimate-Felder + `points` (Liste EstimatePointSerializer) | RO: `points, name, description` | – |
| `NotificationSerializer` | `S/notification.py` | Base | alle Notification-Felder + `triggered_by_details` (UserLite), `is_inbox_issue`, `is_intake_issue`, `is_mentioned_notification` (nur in N-01 annotiert, sonst weggelassen) | – | – |
| `UserNotificationPreferenceSerializer` | `S/notification.py` | Base | alle Felder | RO: `user, workspace, project, created_by, updated_by, deleted_at` | – |
| `WebhookSerializer` | `S/webhook.py` | Dynamic | alle Webhook-Felder; `secret_key` **nur** mit Kontext `show_secret_key=True` | RO: `workspace, secret_key, deleted_at` | `url`: `URLField` + `validate_schema` + `validate_domain`; `create`/`update`: `_validate_webhook_url` (SSRF, erlaubte/verbotene Hosts, eigener Host) |
| `WebhookLogSerializer` | `S/webhook.py` | Dynamic | alle WebhookLog-Felder | RO: `workspace, webhook` | – |
| `FileAssetSerializer` | `S/asset.py` | Base | alle FileAsset-Felder | RO: `created_by, updated_by, created_at, updated_at` | – |
| `APITokenSerializer` | `S/api.py` | Base | alle APIToken-Felder (inkl. `token`) | RO: `token, expired_at, created_at, updated_at, workspace, user, is_active, last_used, user_type` | – |
| `APITokenReadSerializer` | `S/api.py` | Base | alle außer `token`; `is_active` berechnet | – | `is_active = expired_at is None or now < expired_at` |
| `ExporterHistorySerializer` | `S/exporter.py` | Base | siehe X-02 | alle RO | – |
| `AnalyticViewSerializer` | `S/analytic.py` | Base | alle AnalyticView-Felder | RO: `workspace, query` | `create`: `query = issue_filters(query_dict, "POST")` bzw. `{}`; `update`: Bug (immer `{}`) |
| `UserFavoriteSerializer` | `S/favorite.py` | ModelSerializer | `id, entity_type, entity_identifier, entity_data, name, is_folder, sequence, parent, workspace_id, project_id` | RO: `workspace, created_by, updated_by` | `entity_data` via `get_favorite_entities(...).get(pk, workspace_id)` → `cycle`/`module`/`view`: `{id, name, logo_props, project_id}`, `page`: `{id, name, logo_props, project_id (= Favoriten-Projekt)}`, `project`: `{id, name, logo_props}`, `issue`/`folder`: `null`; unsichtbar/gelöscht → `null` |
| `DraftIssueCreateSerializer` | `S/draft.py` | Base | alle DraftIssue-Felder + `state_id`, `parent_id` (PK-Felder), `label_ids`, `assignee_ids` (write-only Listen); Ausgabe ergänzt `assignee_ids`/`label_ids` aus `initial_data` | RO: `workspace, project, created_by, updated_by, created_at, updated_at` | `validate`: `start_date > target_date` → `"Start date cannot exceed target date"`; HTML/Binary wie Sticky; Assignees auf aktive Projektmitglieder Rolle ≥ 15 filtern; Labels auf Projekt filtern; State/Parent/Estimate-Point müssen zum Projekt gehören → `"State is not valid please pass a valid state_id"`, `"Parent is not valid issue_id please pass a valid issue_id"`, `"Estimate point is not valid please pass a valid estimate_point_id"`; `check_cycle_and_modules` (Cycle/Module im Projekt/Workspace) → `"Cycle is not valid please pass a valid cycle_id"`, `"Modules are not valid please pass valid module_ids"`. `create`/`update` siehe W-49/W-51 |
| `DraftIssueSerializer` | `S/draft.py` | Base | `id, name, state_id, sort_order, completed_at, estimate_point, priority, start_date, target_date, project_id, parent_id, cycle_id, module_ids, label_ids, assignee_ids, created_at, updated_at, created_by, updated_by, type_id, description_html` | alle RO | – |
| `DraftIssueDetailSerializer` | `S/draft.py` | ↑ | wie oben (+ `description_html` doppelt) | alle RO | – |
| `CycleSerializer` | `S/cycle.py` | Base | `id, workspace_id, project_id, name, description, start_date, end_date, owned_by_id, view_props, sort_order, external_source, external_id, progress_snapshot, logo_props, is_favorite, total_issues, cancelled_issues, completed_issues, started_issues, unstarted_issues, backlog_issues, status` | alle RO | – |
| `ModuleSerializer` | `S/module.py` | Dynamic | `id, workspace_id, project_id, name, description, description_text, description_html, start_date, target_date, status, lead_id, member_ids, view_props, sort_order, external_source, external_id, logo_props, total_estimate_points, completed_estimate_points, is_favorite, total_issues, cancelled_issues, completed_issues, started_issues, unstarted_issues, backlog_issues, created_at, updated_at, archived_at` | alle RO | – |
| `LabelSerializer` | `S/issue.py` | Base | `parent, name, color, id, project_id, workspace_id, sort_order` | RO: `workspace, project` | `validate_name`: case-insensitiv eindeutig im Projekt → `LABEL_NAME_ALREADY_EXISTS` (A04) |
| `IssueActivitySerializer` | `S/issue.py` | Base | alle IssueActivity-Felder + `actor_detail` (UserLite), `issue_detail` (`IssueFlatSerializer`: `id, name, description_json, description_html, priority, start_date, target_date, sequence_id, sort_order, is_draft`), `project_detail` (ProjectLite), `workspace_detail` (WorkspaceLite), `source_data` (`{source, source_email, extra}` aus Prefetch `issue.source_data`, sonst `null`) | – | – |

### 2.13 Modellfelder der `__all__`-Serializer (Response-Shapes)

Vollständige Modellbeschreibung inkl. Constraints: A02a (`migration/analysis/02a-datenmodell-kern.md`). Hier nur die für die JSON-Verträge nötigen Feldlisten (BaseModel-Felder jeweils zusätzlich, außer wo vermerkt).

| Modell (Quelle) | Felder (Default) |
|---|---|
| `Workspace` (`M/workspace.py`) | `name` (≤80), `logo` (Text, Legacy-URL), `logo_asset` (FK FileAsset), `owner` (FK User), `slug` (≤48, unique), `organization_size` (≤20), `timezone` (Default `"UTC"`), `background_color` (zufällige Farbe `UT/color.py`) |
| `WorkspaceMember` (`M/workspace.py`) | `workspace`, `member`, `role` (Default 5), `company_role`, `view_props` (Default siehe unten), `default_props` (dito), `issue_props` (`{"subscribed": true, "assigned": true, "created": true, "all_issues": true}`), `is_active` (true), `getting_started_checklist` ({}), `tips` ({}), `explored_features` ({}) |
| Default `view_props`/`default_props` (Workspace) | `{"filters": {"priority": null, "state": null, "state_group": null, "assignees": null, "created_by": null, "labels": null, "start_date": null, "target_date": null, "subscriber": null}, "display_filters": {"group_by": null, "order_by": "-created_at", "type": null, "sub_issue": true, "show_empty_groups": true, "layout": "list", "calendar_date_range": ""}, "display_properties": {"assignee": true, "attachment_count": true, "created_on": true, "due_date": true, "estimate": true, "key": true, "labels": true, "link": true, "priority": true, "start_date": true, "state": true, "sub_issue_count": true, "updated_on": true}}` |
| `WorkspaceMemberInvite` | `workspace`, `email`, `accepted` (false), `token`, `message`, `responded_at`, `role` (5) |
| `WorkspaceTheme` | `workspace`, `name` (≤300), `actor`, `colors` ({}) |
| `WorkspaceUserProperties` | `workspace`, `user`, `filters` (Filter-Dict wie oben), `display_filters` (**verschachtelt**: `{"display_filters": {...}}`), `display_properties` (**verschachtelt**: `{"display_properties": {...}}`), `rich_filters` ({}), `navigation_project_limit` (10), `navigation_control_preference` (`"ACCORDION"`\|`"TABBED"`) |
| `WorkspaceUserLink` | `workspace`, `project` (null), `title`, `url`, `metadata` ({}), `owner` |
| `WorkspaceHomePreference` | `workspace`, `user`, `key`, `is_enabled` (true), `config` ({}), `sort_order` (65535) |
| `WorkspaceUserPreference` | `workspace`, `user`, `key`, `is_pinned` (false), `sort_order` (65535) |
| `Sticky` (`M/sticky.py`) | `name`, `description` ({}), `description_html` (`"<p></p>"`), `description_stripped`, `description_binary` (Base64), `logo_props` ({}), `color`, `background_color`, `workspace`, `owner`, `sort_order` (65535) |
| `UserFavorite` (`M/favorite.py`) | `workspace`, `project`, `user`, `entity_type`, `entity_identifier`, `name`, `is_folder` (false), `sequence` (65535), `parent` (Self-FK, CASCADE) |
| `UserRecentVisit` (`M/recent_visit.py`) | `workspace`, `project`, `entity_identifier`, `entity_name`, `user`, `visited_at` (auto_now) |
| `Project` (`M/project.py`) | `name`, `description`, `description_text` (JSON), `description_html` (JSON), `network` (2), `workspace`, `identifier` (≤12, upper), `default_assignee`, `project_lead`, `emoji`, `icon_prop`, `module_view` (false), `cycle_view` (false), `issue_views_view` (false), `page_view` (true), `intake_view` (false), `is_time_tracking_enabled` (false), `is_issue_type_enabled` (false), `guest_view_all_features` (false), `cover_image`, `cover_image_asset`, `estimate`, `archive_in` (0), `close_in` (0), `logo_props` ({}), `default_state`, `archived_at`, `timezone` (Workspace-TZ), `external_source`, `external_id` |
| `ProjectMember` | `project`, `workspace`, `member`, `comment`, `role` (5), `view_props`/`default_props` (Projekt-Default: `filters` + `display_filters` wie oben, **ohne** `display_properties`), `preferences` (`{"pages": {"block_display": true}, "navigation": {"default_tab": "work_items", "hide_in_more_menu": []}}`), `sort_order` (65535), `is_active` (true) |
| `ProjectMemberInvite` | `project`, `workspace`, `email`, `accepted`, `token`, `message`, `responded_at`, `role` (5) |
| `DeployBoard` (`M/deploy_board.py`) | `workspace`, `project`, `entity_identifier`, `entity_name` (`project`\|`issue`\|`module`\|`cycle`\|`page`\|`view`\|`intake`), `anchor` (32 hex, unique), `is_comments_enabled`, `is_reactions_enabled`, `intake`, `is_votes_enabled` (alle false), `view_props` ({}), `is_activity_enabled` (true), `is_disabled` (false) |
| `User` (`M/user.py`, **kein** BaseModel) | `id`, `username`, `mobile_number`, `email`, `display_name`, `first_name`, `last_name`, `avatar`, `avatar_asset`, `cover_image`, `cover_image_asset`, `date_joined`, `created_at`, `updated_at`, `last_location`, `created_location`, `is_superuser`, `is_managed`, `is_password_expired`, `is_active`, `is_staff`, `is_email_verified`, `is_password_autoset`, `is_password_reset_required`, `token`, `last_active`, `last_login_time`, `last_logout_time`, `last_login_ip`, `last_logout_ip`, `last_login_medium` (`"email"`), `last_login_uagent`, `token_updated_at`, `is_bot`, `bot_type`, `user_timezone` (`"UTC"`), `is_email_valid`, `masked_at`, `last_login` (AbstractBaseUser) |
| `Profile` (`M/user.py`, nur Zeitstempel, **kein** `created_by`/`deleted_at`) | `id`, `created_at`, `updated_at`, `user`, `theme` ({}), `is_app_rail_docked` (true), `is_tour_completed` (false), `onboarding_step` (`{"profile_complete": false, "workspace_create": false, "workspace_invite": false, "workspace_join": false}`), `use_case`, `role`, `is_onboarded` (false), `last_workspace_id`, `billing_address_country` (`"INDIA"`), `billing_address`, `has_billing_address`, `company_name`, `notification_view_mode` (`"full"`\|`"compact"`), `is_smooth_cursor_enabled` (false), `is_mobile_onboarded`, `mobile_onboarding_step` (`{"profile_complete": false, "workspace_create": false, "workspace_join": false}`), `mobile_timezone_auto_set`, `language` (`"en"`), `start_of_the_week` (0=Sonntag … 6=Samstag), `goals` ({}), `background_color`, `is_navigation_tour_completed`, `has_marketing_email_consent`, `is_subscribed_to_changelog`, `product_tour` (`{"work_items": false, "cycles": false, "modules": false, "intake": false, "pages": false}`) |
| `Account` (`M/user.py`, nur Zeitstempel) | `id`, `created_at`, `updated_at`, `user`, `provider_account_id`, `provider` (`google`\|`github`\|`gitlab`), `access_token`, `access_token_expired_at`, `refresh_token`, `refresh_token_expired_at`, `last_connected_at`, `id_token`, `metadata` |
| `Estimate` (`M/estimate.py`) | `project`, `workspace`, `name`, `description`, `type` (`categories`\|`points`), `last_used` (false) |
| `EstimatePoint` | `project`, `workspace`, `estimate`, `key` (int ≥ 0), `description`, `value` (≤255, API ≤ 20) |
| `Notification` (`M/notification.py`) | `workspace`, `project`, `data` (JSON), `entity_identifier`, `entity_name`, `title`, `message` (JSON), `message_html` (`"<p></p>"`), `message_stripped`, `sender` (`"in_app:issue_activities:created"`, `"in_app:issue_activities:assigned"`, `"in_app:issue_activities:subscribed"`, `"in_app:issue_activities:mentioned"`; `BG/notification_task.py`), `triggered_by`, `receiver`, `read_at`, `snoozed_till`, `archived_at` |
| `UserNotificationPreference` | `user`, `workspace`, `project`, `property_change`, `state_change`, `comment`, `mention`, `issue_completed` (alle true) |
| `Webhook` (`M/webhook.py`) | `workspace`, `url`, `is_active` (true), `secret_key`, `project`, `issue`, `module`, `cycle`, `issue_comment` (Event-Flags, false), `is_internal` (false), `version` (`"v1"`) |
| `WebhookLog` | `workspace`, `webhook` (UUID, keine FK), `event_type`, `request_method`, `request_headers`, `request_body`, `response_status`, `response_headers`, `response_body`, `retry_count` |
| `FileAsset` (`M/asset.py`) | `attributes` ({}), `asset` (Objekt-Key), `user`, `workspace`, `draft_issue`, `project`, `issue`, `comment`, `page`, `entity_type`, `entity_identifier`, `is_deleted`, `is_archived`, `external_id`, `external_source`, `size` (float), `is_uploaded`, `storage_metadata` |
| `APIToken` (`M/api.py`) | `label`, `description`, `is_active` (true), `last_used`, `token` (`plane_api_<hex>`), `user`, `user_type` (0 Human, 1 Bot), `workspace` (null), `expired_at` |
| `ExporterHistory` (`M/exporter.py`) | `name`, `type` (`issue_exports`\|`issue_worklogs`), `workspace`, `project` (UUID-Array), `provider`, `status` (`queued`\|`processing`\|`completed`\|`failed`), `reason`, `key`, `url`, `token` (32 hex), `initiated_by`, `filters`, `rich_filters` |
| `AnalyticView` (`M/analytic.py`) | `workspace`, `name`, `description`, `query` (JSON), `query_dict` (JSON) |
| `IssueActivity` (`M/issue.py`) | `workspace`, `project`, `issue`, `verb` (`"created"`), `field`, `old_value`, `new_value`, `comment`, `attachments` (URL-Array), `issue_comment`, `actor`, `old_identifier`, `new_identifier`, `epoch` |

### 2.14 Seiteneffekte: Celery-Tasks, Cache-Invalidierung, Activity/Webhooks

| Auslöser (ID) | Task / Effekt (Quelle) | Inhalt |
|---|---|---|
| W-03 | `workspace_seed.delay(workspace_id)` (`BG/workspace_seed_task.py`) | Bot-User (`username=bot_user_{ws_id}`, `display_name="Plane"`, `is_bot`, `bot_type="WORKSPACE_SEED"`, E-Mail `bot_user_{ws_id}@<WEB_URL-Host>`), Bot als WS-Admin, Demo-Daten aus `apps/api/plane/seeds/data/*` (Projekte, States, Labels, Cycles, Modules, Issues, Pages, Views). Details A02a. |
| W-09 | `workspace_invitation.delay(email, workspace_id, token, current_site, inviter_email)` (`BG/workspace_invitation_task.py`) | Einladungs-E-Mail mit Link `{WEB_URL}/workspace-invitations/?invitation_id=…&slug=…&token=…` |
| W-53 | `issue_activity.delay(...)` (`BG/issue_activities_task.py`, A04) | `issue.activity.created`, `cycle.activity.created`, `module.activity.created` (+ Notifications) |
| P-02, P-06 | `model_activity.delay(model_name="project", …)` (`BG/webhook_task.py`) | → `webhook_activity` (created bzw. pro geändertem Feld updated) → Webhook-Versand an Workspace-Webhooks mit `project=true` |
| P-07 | `webhook_activity.delay(event="project", verb="deleted")` | Webhook-Versand |
| P-04 | `recent_visited_task.delay(entity_name="project", …)` (`BG/recent_visited_task.py`) | Recent-Visit upsert, max. 20 je User/Workspace (ältester nach `created_at` wird gelöscht) |
| P-20 | `project_add_user_email.delay(current_site, project_member_id, invitor_id)` (`BG/project_add_user_email_task.py`) | E-Mail „zu Projekt hinzugefügt“ |
| U-03 | `user_deactivation_email.delay(current_site, user_id)` | Bestätigungsmail |
| U-06 | `send_email_update_magic_code.delay(email, token)` (`BG/user_email_update_task.py`) | Code-Mail an neue Adresse |
| U-07 | `send_email_update_confirmation.delay(new)` + `.delay(old)` | Bestätigung an beide Adressen |
| E-09 | `issue_activity.delay(type="issue.activity.updated", …)` je betroffenem Issue | Activity-Einträge „estimate_point geändert“ |
| X-01 | `issue_export_task.delay(...)` (`BG/export_task.py`) | Export → ZIP → S3 → Presigned-URL (7 Tage) |
| AN-08 | `analytic_export_task.delay(email, data, slug, user_id)` (`BG/analytic_plot_export.py`) | CSV per E-Mail |
| A-09, A-13, A-18 | `get_asset_object_metadata.delay(asset_id)` (`BG/storage_metadata_task.py`) | S3 `HEAD` → `storage_metadata` |
| alle `Model.delete()` (soft) | `soft_delete_related_objects.delay(app_label, model_name, pk)` (`BG/deletion_task.py`) | rekursive Soft-Delete-Kaskade |
| Cache | `invalidate_cache`/`invalidate_cache_directly` | W-14, W-15, W-22, A-09/A-10 (Workspace-Logo), A-13/A-14 (User-Assets), S-02/S-05/S-07, E-03/E-05/E-06 – Schlüssel siehe 2.1.6 (überwiegend wirkungslos) |

### 2.15 Frontend-Abdeckung & Lücken

**A) Frontend ruft Endpunkte auf, die im CE-Backend nicht existieren** (→ 404 `{"error": "Page not found."}`; Kandidaten für Bezahl-Features bzw. neu zu bauende Funktionen gemäß ADR-001):

| Aufruf | Aufrufer | Zweck (aus Frontend ableitbar) |
|---|---|---|
| `PATCH {W}/sidebar-preferences/{key}/` | `WEB/services/workspace.service.ts` `updateSidebarPreference`, `WEB/store/workspace/index.ts` | Einzelnen Sidebar-Eintrag pinnen/sortieren (Body `{is_pinned?, sort_order?}`); im CE nur Bulk (W-68) |
| `POST {W}/rephrase-grammar/` | `WEB/services/ai.service.ts` `performEditorTask`, `WEB/components/pages/editor/ai/menu.tsx` | KI-Menü im Seiten-Editor („Pi“, Task `ASK_ANYTHING`, Tonalität `casual_score`/`formal_score`), Antwort `{response}` |
| `POST /api/assets/v2/workspaces/{slug}/{entity_id}/bulk/` | `WEB/services/file.service.ts` `updateBulkWorkspaceAssetsUploadStatus`, `WEB/components/comments/comment-create.tsx` | Asset-Zuordnung für Kommentare ohne Projektkontext (Workspace-Ebene) |
| `POST /api/assets/v2/workspaces/{slug}/duplicate-assets/` | `SVC/file/file.service.ts` `duplicateAssets` | Batch-Duplizieren (nicht aufgerufen) |
| `GET {W}/dashboard/`, `GET {W}/dashboard/{id}/`, `GET /api/dashboard/{id}/`, `PATCH /api/dashboard/{id}/widgets/{id}/` | `WEB/services/dashboard.service.ts`, `WEB/store/dashboard.store.ts` (Hook `useDashboard` ohne Aufrufer) | Legacy-Home-Dashboard (tot) |

Weitere Lücken außerhalb dieses Bereichs (z. B. `{W}/active-cycles/`, `{W}/importers/…`, `{W}/workspace-integrations/…`, `/api/instances/workspace-slug-check/`, `/api/release-notes/`) werden in den jeweils zuständigen Analysen behandelt.

**B) Backend-Endpunkte dieses Bereichs ohne Frontend-Aufrufer:** W-02, W-05, W-10, W-18, W-19, W-23 (nur definiert), W-26 … W-30 (Themes), W-56, P-05, P-09 … P-14, P-17, P-18 (Projekt-Einladungen insgesamt), P-25, P-27, P-29 (Services definiert, Store nutzt W-43 ff.), P-32, P-37, P-38, U-04, U-11, U-12, U-16, U-18 … U-20, AT-04, S-03 (nur definiert), E-01, E-05, N-02, N-04, WH-07, A-01, A-02, A-05, A-06, AN-01 … AN-09, EXT-02. Fachlich trotzdem zu portieren, sofern sie Teil eines Features sind (Projekt-Einladungen per E-Mail, Themes, Webhook-Logs – siehe 5.2).

**C) Trailing-Slash-Abweichungen im Frontend:** `GET/DELETE {U}/api-tokens/{id}` (`SVC/developer/api-token.service.ts`), `GET/DELETE {W}/stickies/{id}` (`WEB/services/sticky.service.ts`), `GET {W}/project-identifiers` (`WEB/services/project/project.service.ts`), `GET {W}/export-issues` (`WEB/services/integrations/integration.service.ts`, Export-Historie) → Django leitet per `APPEND_SLASH` (301) um. Die .NET-Routen müssen beide Schreibweisen akzeptieren.


### 2.16 Bezüge zu den Bezahl-Editionen in diesem Bereich (Evidenz im CE-Code)

Der CE-Code enthält keine EE-Implementierungen, aber eindeutige Andockpunkte. Sie sind für ADR-001 (alle Features aktiv) relevant und werden in der Bezahl-Feature-Analyse fachlich spezifiziert; hier nur die Evidenz aus diesem Bereich:

| Evidenz | Quelle | Einordnung für die Migration |
|---|---|---|
| Frontend-Aufrufe ohne CE-Backend: `rephrase-grammar`, `sidebar-preferences/{key}`, Workspace-Bulk-Assets, Batch-Duplicate | 2.15 A | neu bauen (5.2) |
| `ProjectPagePermission._has_private_page_action_access` liefert immer `False` („Override for feature flag logic“), `_check_access_and_get_role` als „Hook for extended access checking“ | `PERM/page.py` | Zugriff auf **private Seiten anderer** (Teilen/Freigeben) ist eine EE-Erweiterung → in .NET als echte Regel implementieren (Spezifikation aus Pages-/Bezahl-Analyse) |
| Reservierte Workspace-Slugs u. a. `plane-pro`, `plane-ultimate`, `enterprise`, `plane-enterprise`, `business`, `pro`, `initiatives`, `initiative`, `epics`, `epic`, `story`, `workflow`, `workflows`, `silo`, `importers`, `integrations`, `dashboard`, `chat`, `drive`, `calendar`, `channels`, `disco`, `upgrade`, `billing`, `license`, `licenses` | `UT/constants.py` | Hinweise auf Top-Level-Routen der Bezahl-Produkte (Initiatives, Epics, Workflows, Dashboards, Integrationen/Importer via „Silo“); Liste 1:1 übernehmen, damit spätere Routen kollisionsfrei bleiben |
| Projekt-Flags `is_time_tracking_enabled`, `is_issue_type_enabled` (in diesem Bereich ohne Logik, nur durchgereicht) | `M/project.py` | Time-Tracking/Worklogs und Work-Item-Typen (Bezahl-Features) – Flags bleiben fachliche Toggles (ADR-001) |
| `ExporterHistory.type` kennt `issue_worklogs` | `M/exporter.py` | Worklog-Export (Bezahl-Feature) – Export-Endpunkt X-01 unterstützt im CE nur `issue_exports` |
| `DeployBoard.entity_name` erlaubt `issue`, `module`, `cycle`, `page`, `view`, `intake` – CE veröffentlicht nur `project` | `M/deploy_board.py`, `V/project/base.py` | Veröffentlichung von Views/Pages/Intake-Formularen (Bezahl-Features) |
| Sidebar-Keys `active_cycles`, `analytics`, `archives`, `views`, `drafts`, `your_work`, `stickies`; Frontend ruft `{W}/active-cycles/` (fehlt) | `M/workspace.py` `WorkspaceUserPreference.UserPreferenceKeys`, `WEB/services/cycle.service.ts` | Workspace-weite „Active Cycles“-Ansicht (Bezahl-Feature, Cycle-Analyse) |
| `Webhook.is_internal`, `Webhook.version` | `M/webhook.py` | interne Webhooks für Integrationsdienst („Silo“) |
| `APIToken.workspace` (im CE immer `NULL`), `APIToken.user_type` Bot | `M/api.py`, `V/api.py` | workspace-gebundene Tokens/Bots (Integrationen) |
| 429-Text „You have reached the maximum number of requests of 50 requests per month per user.“ | `WEB/components/issues/issue-modal/components/description-editor.tsx`, `WEB/components/core/modals/gpt-assistant-popover.tsx` | Cloud-Kontingent → entfällt (ADR-001/004); Text kann im Angular-Code bleiben, wird nie ausgelöst |
| `AI_EDITOR_TASKS.ASK_ANYTHING`, Ladetext „Pi is generating response“ | `packages/constants/src/ai.ts` | Plane-AI „Pi“ im Editor (Bezahl-Feature) → `rephrase-grammar` (5.2) |
| `Profile.billing_address_country`, `billing_address`, `has_billing_address`, `company_name` | `M/user.py` | Billing → entfällt (ADR-001); Felder können ungenutzt im Vertrag bleiben (Frontend-Typen) |

---

## 3. Verhalten/Logik/Abläufe im Detail (inkl. Edge-Cases)

### 3.1 Workspace-Lebenszyklus

1. **Slug-Prüfung (W-01):** Das Frontend (`WEB/components/workspace/create-workspace-form.tsx`, `WEB/components/onboarding/steps/workspace/create.tsx`) prüft vor dem Anlegen `res.status === true` **und** clientseitig gegen `RESTRICTED_URLS`. Die Server-Liste `RESTRICTED_WORKSPACE_SLUGS` (`UT/constants.py`) umfasst exakt: `404, accounts, api, create-workspace, god-mode, installations, invitations, onboarding, profile, spaces, workspace-invitations, password, flags, monitor, monitoring, ingest, plane-pro, plane-ultimate, enterprise, plane-enterprise, disco, silo, chat, calendar, drive, channels, upgrade, billing, sign-in, sign-up, signin, signup, config, live, admin, m, import, importers, integrations, integration, configuration, initiatives, initiative, workflow, workflows, epics, epic, story, mobile, dashboard, desktop, onload, real-time, one, pages, business, pro, settings, license, licenses, instances, instance` (Duplikate `config`, `mobile`, `monitor` im Original). Vergleich case-sensitiv.
2. **Anlegen (W-03):** Validierungsreihenfolge und Fehlertexte siehe Tabelle. `DISABLE_WORKSPACE_CREATION` wird über `get_configuration_value` gelesen (`apps/api/plane/license/utils/instance_value.py`: bei `SKIP_ENV_VAR=1` (Default) aus `InstanceConfiguration`, sonst ENV). Anschließend Owner-Mitgliedschaft (Rolle 20, `company_role` aus Body) und asynchroner Seed. Die Antwort enthält `total_members` = Anzahl **aller** Mitgliedschaften zum Zeitpunkt (1) und `role = 20`.
3. **Ändern (W-06):** Nur WS-Admins. `logo_asset` wird normalerweise über den Asset-Flow (A-09) gesetzt, nicht per PATCH.
4. **Löschen (W-07):** Soft-Delete + Slug-Umbenennung, sodass der Slug wiederverwendbar ist; `Profile.last_workspace_id` aller betroffenen User wird geleert (U-05 liefert danach den Fallback-Workspace).
5. **Workspace-Liste:** ausschließlich U-17 (`/api/users/me/workspaces/`), da W-02 defekt ist.

### 3.2 Einladungen & Beitritt

**Workspace (W-08 … W-16):**

```
Admin/Member ──POST invitations──▶ WorkspaceMemberInvite(token=JWT, role≤eigene) ──Celery──▶ E-Mail mit Link
Empfänger (eingeloggt, gleiche E-Mail) ──GET …/join/ (öffentliche Details)──▶ Anzeige
   a) Einzel:  POST …/{id}/join/ {token, accepted} ──▶ Mitglied (Rolle aus Einladung), Einladung gelöscht
   b) Bulk:    POST /users/me/workspaces/invitations/ {invitations:[ids]} ──▶ Mitglied je Einladung (ohne Token!)
```

Edge-Cases: (1) Variante b) benötigt **kein** Token – es genügt, dass die Einladung an die eigene E-Mail adressiert ist. (2) Ablehnung (`accepted=false`) markiert nur `responded_at`; eine erneute Einladung derselben E-Mail scheitert still an der Unique-Constraint (`email, workspace` bei `deleted_at IS NULL`), bis die alte Einladung gelöscht wird. (3) Die Rolle einer Einladung wird beim Beitritt **ungeprüft** übernommen (Ersteller konnte nur ≤ eigene Rolle vergeben). (4) Reaktivierung eines früher entfernten Mitglieds setzt die Rolle der Einladung (W-15, W-14).

**Projekt (P-10 … P-18):** E-Mail-Einladungen an Projekte sind im CE **funktionsunfähig** (P-11 immer 500) und vom Frontend nicht angebunden. Projektmitglieder werden stattdessen direkt hinzugefügt (P-20, nur bestehende WS-Mitglieder) oder treten selbst bei (P-15, öffentliche Projekte bzw. als WS-Admin auch geheime). Der Annahme-Endpunkt P-17 ist funktionsfähig (für Einladungen, die z. B. per Datenimport existieren).

### 3.3 Rollenmodell & Mitgliederverwaltung

#### 3.3.1 Workspace-Rollen – Wirkungsmatrix (aus den Endpunkt-Berechtigungen abgeleitet)

| Aktion | Admin (20) | Member (15) | Guest (5) | Quelle |
|---|---|---|---|---|
| Workspace ansehen | ✓ | ✓ | ✓ | W-04 |
| Workspace-Einstellungen ändern / löschen | ✓ | ✗ | ✗ | W-06, W-07 |
| Mitglieder einladen (Rolle ≤ eigene) / Einladungen verwalten | ✓ | ✓ | ✗ | W-08 … W-12 |
| Rollen ändern / Mitglieder entfernen | ✓ | ✗ | ✗ | W-20, W-21 |
| Mitgliederliste mit E-Mail-Adressen | ✓ | ✓ | ✗ (ohne E-Mail) | W-17 |
| Projekte anlegen | ✓ | ✓ | ✗ | P-02 |
| alle Projekte sehen (auch geheime, ohne Mitgliedschaft) | ✓ | nur eigene + öffentliche | nur eigene | P-01, P-03 |
| geheimen Projekten selbst beitreten | ✓ | ✗ | ✗ | P-15 |
| Projekte bearbeiten/löschen ohne Projektmitgliedschaft | ✓ | ✗ | ✗ | P-06, P-07 |
| Favoriten (workspace-weit) | ✓ | ✓ | ✗ | W-43 … W-47 |
| Webhooks | ✓ | ✗ | ✗ | WH-* |
| Exporte | ✓ | ✓ | ✗ | X-* |
| Analytics (Advance, Legacy) | ✓ | ✓ | ✗ (nur AN-09, AN-10, AN-16) | AN-* |
| KI-Assistent | ✓ | ✓ | ✗ | EXT-02, EXT-03 |
| Drafts anlegen | ✓ | ✓ | ✓ (ohne Projekt bzw. Projektschreibrecht nötig) | W-49 |
| Workspace-Logo hochladen | ✓ | ✗ | ✗ | A-08 |
| Stickies, Quick Links, Home, Sidebar, Recents | ✓ | ✓ | ✓ | W-54 … W-68 |
| Notifications „created“-Filter | ✓ | ✓ | ✗ (leer) | N-01, N-10 |

#### 3.3.2 Projekt-Rollen – Regeln

- Workspace-Admin, der Projektmitglied (beliebige Rolle) ist, gilt in `allow_permission` als Projekt-Admin.
- Projektrolle eines WS-Gastes kann nicht über 5 gehoben werden (P-20, P-22); WS-Admins können nur als Projekt-Admin hinzugefügt werden (P-20).
- Herabstufung eines WS-Mitglieds zum Gast stuft **alle** seine Projektmitgliedschaften auf Gast (W-20, transaktional).
- Entfernen aus dem Workspace (W-21) oder Verlassen (W-22) deaktiviert alle Projektmitgliedschaften (keine Löschung; Reaktivierung über Einladung/Join setzt die Rolle neu).
- „Einziger Admin“-Schutz: Workspace verlassen (letzter aktiver Admin), Projekt verlassen (letzter aktiver Admin), Entfernen/Herabstufen (einziges Mitglied eines Projekts und Admin dort).
- Bei Projektrollenänderung durch Nicht-WS-Admins gilt die strikte Hierarchie „nur Rollen unterhalb der eigenen, nur an Mitglieder unterhalb der eigenen“.

#### 3.3.3 Konto-Deaktivierung (U-03)

Ablauf exakt: Instanz-Admin-Sperre → (theoretische) Einziger-Admin-Prüfung → alle aktiven Projekt- und Workspace-Mitgliedschaften `is_active=False` → alle Workspace-Einladungen an die E-Mail soft-löschen → alle Sessions löschen → Profile-Reset → Passwort randomisieren (`is_password_autoset=True`) → User `is_active=False`, Logout-IP/-Zeit → Mail → `logout(request)` → 204. Reaktivierung erfolgt im Auth-Bereich (erneute Anmeldung reaktiviert, siehe A-Auth-Analyse).

### 3.4 Workspace-Benutzerprofil (W-31 … W-35)

- **Sichtbarkeitsprinzip:** Alle Profil-Statistiken zählen nur Issues, die der **Anfragende** sehen darf (`_visible_issues_q`). Damit unterscheiden sich die Zahlen je Betrachter.
- **`user-profile`:** `project_data` nur für Betrachter mit WS-Rolle ≥ 15. Die Projektliste ist die des **Betrachters** (nicht des Profilinhabers).
- **`user-issues`:** Menge = zugewiesen ∪ erstellt ∪ abonniert (Ziel-User). Unterstützt Gruppierung/Subgruppierung/Pagination wie die Projekt-Issue-Liste (A04).
- **`user-activity` + Export:** Exportiert nur den gewählten Tag (Benutzerzeitzone), max. 10 000 Zeilen.

#### 3.4.1 Legacy-Issue-Filter (`UT/issue_filters.py` `issue_filters`)

Unterstützte Query-Keys (GET: kommagetrennt, `null`-Einträge ignoriert): `state`, `state_group`, `estimate_point`, `priority`, `parent`, `labels`, `assignees`, `mentions`, `created_by`, `logged_by`, `name`, `created_at`, `updated_at`, `start_date`, `target_date`, `completed_at`, `type`, `project`, `cycle`, `module`, `intake_status`, `inbox_status`, `sub_issue`, `subscriber`, `start_target_date`. Datumsfilter im Format `YYYY-MM-DD;after|before` oder `<n>_weeks|<n>_months;after|before;fromnow|ago`. Exakte Semantik: A04 (`migration/analysis/04-api-intern-arbeitsobjekte.md`). Verwendet in W-31, W-35, W-48, AN-01, AN-03 (POST-Modus), AN-09.

### 3.5 Projekt-Lebenszyklus & Sichtbarkeit

1. **Netzwerk:** `network = 2` (Public: jedes WS-Mitglied ≥ Member sieht das Projekt in der Liste und kann beitreten), `network = 0` (Secret: nur Mitglieder und WS-Admins sehen es; Beitritt nur WS-Admins).
2. **Liste (P-01) vs. Details (P-03):** P-01 ist die schlanke Variante (Werte-Dict, mit `intake_count`), P-03 die vollständige (Serializer, `members`, `anchor`, `is_favorite`, `next_work_item_sequence`). Beide enthalten archivierte Projekte (`archived_at`).
3. **Detail (P-04):** archivierte Projekte → 404 (Archiv-UI nutzt Listen). Nicht-Mitglied: 403 (secret) bzw. 409 (public) – das Frontend unterscheidet daran „kein Zugriff“ vs. „beitreten“.
4. **Anlegen (P-02):** Ersteller = Admin, optional Lead = Admin, sechs Default-States (inkl. Triage-State für Intake), Identifier-Reservierung. Die Antwort ist die Detail-Form (P-03-Felder).
5. **Feature-Toggles:** `module_view`, `cycle_view`, `issue_views_view`, `page_view`, `intake_view`/`inbox_view`, `is_time_tracking_enabled`, `is_issue_type_enabled`, `guest_view_all_features` – fachliche Einstellungen (bleiben gemäß ADR-001). Aktivieren von Intake legt den Default-Intake an.
6. **Archivieren (P-35/P-36):** nur Projekt-Admin/-Member; entfernt alle Favoriten des Projekts dauerhaft; Unarchive stellt Favoriten **nicht** wieder her.
7. **Löschen (P-07):** Soft-Delete inkl. Celery-Kaskade; Deploy-Board und Favoriten werden explizit gelöscht; Identifier bleibt in `ProjectIdentifier` reserviert, bis P-09 ihn freigibt (der Projekt-Erstellungsdialog bietet das bei Konflikt an).
8. **Projekt-Identifier (P-08):** Verfügbarkeitsprüfung auf `ProjectIdentifier` (auch gelöschter Projekte), nicht auf `Project`.
9. **Veröffentlichung (P-30 … P-34):** genau ein Board pro Projekt (`entity_name="project"`); `anchor` ist der öffentliche Schlüssel für `apps/space` (A11). `view_props` steuert die im Space erlaubten Layouts.
10. **Sortierung in der Sidebar:** `ProjectUserProperty.sort_order` je User; neue Mitgliedschaften erhalten `min - 10000` (erscheinen oben), Self-Join (P-15) erhält 65535.

### 3.6 User, Profil, Einstellungen

- **Login-Redirect-Logik (U-05):** Frontend leitet nach Login zu `last_workspace_slug`, sonst `fallback_workspace_slug`, sonst Onboarding/Einladungen (`invites`-Zähler).
- **E-Mail-Wechsel (U-06/U-07):** Zwei-Phasen mit 6-stelligem Code (10 min gültig), Limits: 3 Code-Anforderungen/h/User, 10 Requests/min/IP, 5 Codes/h pro Zieladresse, 5 Prüfversuche pro Code. Nach Erfolg Logout (Session wird beendet), `is_email_verified=false`.
- **Profil (U-08/U-09):** frei beschreibbar (außer `user`), enthält UI-Zustände (Theme, App-Rail, Tour-Flags, Sprache, Wochenstart, Smooth-Cursor, Notification-View-Mode).
- **Onboarding (U-14/U-15):** setzen jeweils ein Boolean, Default `false` bei fehlendem Body-Feld.

### 3.7 Home, Sidebar, Quick Links, Recents, Stickies

- **Lazy Seeding:** Home-Widgets (W-59) und Sidebar-Einträge (W-67) werden beim ersten GET pro User/Workspace angelegt; die Default-Reihenfolge ergibt sich aus der Reihenfolge der fehlenden Keys (Werte siehe W-59 und W-67).
- **Recents (W-61):** Befüllung ausschließlich über `recent_visited_task` (in diesem Bereich durch P-04; Issues/Pages in A04). Maximal 20 Einträge je User/Workspace; Rückgabe max. 20, gefiltert auf Issue/Page/Project.
- **Quick Links (W-54 … W-58):** persönliche Links; URL-Normalisierung `http://`-Präfix.
- **Stickies (W-62 … W-66):** persönliche Notizen mit Rich-Text (HTML + Yjs-Binary), Farben; Suche über `description_stripped`; neue Stickies erhalten `max(sort_order)+10000` → erscheinen bei `-sort_order` oben.

### 3.8 Notifications – Filtersemantik (N-01, N-09, N-10)

N-01 wendet nacheinander an:

| Schritt | Bedingung |
|---|---|
| Basis | `workspace = slug`, `receiver = user`, `entity_name = "issue"`; Annotation `is_inbox_issue` = `is_intake_issue` = existiert Issue mit Intake-Status ∈ {0 (snoozed), 2 (duplicate), -2 (pending)}; `is_mentioned_notification = sender ILIKE '%mentioned%'` |
| `snoozed=true` | `snoozed_till < now OR snoozed_till IS NOT NULL` (= alle je gesnoozten) |
| `snoozed=false` | `snoozed_till >= now OR snoozed_till IS NULL` (= nie gesnoozt **oder noch** gesnoozt (!) – Snooze-Zukunft wird **nicht** ausgeblendet) |
| `archived=true/false` | `archived_at IS NOT NULL` / `IS NULL` |
| `read=false` / `read=true` | `read_at IS NULL` / `IS NOT NULL`; fehlt → beide |
| `mentioned` gesetzt (beliebiger Wert) | nur `sender ILIKE '%mentioned%'`; **sonst** Mentions ausgeschlossen |
| `type` enthält `subscribed` | ODER: Issues, die der User abonniert, aber weder erstellt noch zugewiesen hat (Achtung: `assigned`-Subquery vergleicht `IssueAssignee.pk` mit `issue_id` – fachlich fehlerhaft, filtert praktisch nicht) |
| `type` enthält `assigned` | ODER: Issues mit Zuweisung an User |
| `type` enthält `created` | WS-Gast → **leeres** Ergebnis; sonst ODER: vom User erstellte Issues |
| `type = all` | kein Typfilter |

Frontend (`WEB/store/notifications/workspace-notifications.store.ts`): sendet `type` = aktivierte Filter kommagetrennt, `snoozed`, `archived` (Booleans → `"true"`/`"false"`), `read=false` nur wenn Filter „ungelesen“ aktiv, `mentioned=true` im Mentions-Tab, Pagination mit `per_page` und Cursor `"{per_page}:0:0"` initial.

Unread-Zähler N-09 nutzt eine **andere** Snooze-Definition (`snoozed_till IS NULL`) und keinen `entity_name`-Filter. Mark-All-Read N-10 nutzt `type ∈ {watching, assigned, created}` (Einzelwert).

### 3.9 Favoriten (W-43 … W-47, P-28/P-29)

- Ein Favorit ist ein `UserFavorite` mit `entity_type` und `entity_identifier`; Ordner sind `entity_type="folder"`, `is_folder=true`, Name in `name`; Verschachtelung über `parent`.
- Reihenfolge: `sequence` (Float), Default `max+10000`; Drag&Drop setzt `sequence` und/oder `parent` per PATCH.
- Eindeutigkeit: `(entity_type, entity_identifier, user)` bei `deleted_at IS NULL`. Ein zweites POST liefert den bestehenden Eintrag (200).
- Sichtbarkeit: Liste blendet Favoriten aus Projekten ohne aktive Mitgliedschaft aus; `entity_data = null`, wenn Entität unsichtbar/gelöscht. Seiten-Favoriten ohne Projekt werden auf Top-Level ausgeblendet.
- Löschen ist hart und kaskadiert auf Kinder.
- Archivieren/Löschen eines Projekts entfernt alle Projekt-Favoriten (alle User).

### 3.10 Drafts (W-48 … W-53)

- Drafts sind private Entwürfe eines Users (Workspace-weit, optional mit Projekt). Assignees/Labels/Cycle/Module werden in eigenen Zwischentabellen (`DraftIssueAssignee`, `DraftIssueLabel`, `DraftIssueCycle`, `DraftIssueModule`) gehalten.
- Umwandlung (W-53) erzeugt ein echtes Issue (Validierung `IssueCreateSerializer`, A04) mit den im **Request** gesendeten Feldern (nicht automatisch aus dem Draft – das Frontend sendet die Draft-Daten mit), übernimmt Beschreibungs-Assets und löscht den Draft.
- Sidebar-Zähler: `draft_issue_count` aus W-24.

### 3.11 States & Estimates

- **State-Gruppen:** `backlog`, `unstarted`, `started`, `completed`, `cancelled`, `triage` (letztere nur systemseitig, für Intake). Genau ein `default` pro Projekt (S-07). Neue Issues ohne State bekommen den Default-State (A04).
- **`order`-Feld** (S-01, W-39) ist berechnet (Position innerhalb der Gruppe / Gruppengröße) und wird vom Frontend für Fortschrittsdarstellungen genutzt.
- **Estimates:** Pro Projekt mehrere Estimate-Systeme möglich, aktiv ist `Project.estimate`. Typen: `categories` (Werte wie XS/S/M) und `points` (numerische Werte als String). Punkte werden über `key` (Reihenfolge, 1…n) sortiert; Löschen eines Punktes nummeriert nachfolgende Keys um und kann Issues auf einen Ersatzpunkt umhängen (E-09).

### 3.12 Webhooks & API-Tokens

- **Webhook-Events:** Flags `project`, `issue`, `module`, `cycle`, `issue_comment`; Versand und Signatur (HMAC mit `secret_key`) in `BG/webhook_task.py` (A-Bereich Hintergrundjobs). Secret nur bei Erstellung/Regeneration sichtbar.
- **SSRF-Schutz:** DNS-Auflösung zur Validierungszeit; Versand pinnt die IP (`UT/url_security.py` `pinned_fetch`, laut Kommentar in `UT/ip_address.py`). Konfiguration: `WEBHOOK_ALLOWED_IPS` (CIDR-Liste), `WEBHOOK_ALLOWED_HOSTS`, `WEBHOOK_DISALLOWED_DOMAINS`. Für Airgapped-Betrieb mit internen Zielen sind diese Variablen essentiell.
- **API-Tokens:** persönliche Tokens (`plane_api_…`) für die öffentliche API `/api/v1/` (A05); optional mit Ablaufdatum; Anzeige des Klartexts nur bei Erstellung.

### 3.13 Assets – Upload-Flow und Berechtigungsmatrix

**Upload-Flow (v2):**

```
1. POST /api/assets/v2/workspaces/{slug}/[projects/{pid}/]  {name,type,size,entity_type,entity_identifier}
      → FileAsset(is_uploaded=false, asset="<ws_id>/<uuid>-<name>")  + Presigned POST (Policy: bucket, Content-Type, content-length-range 1..size_limit, key)
2. Browser: multipart POST an upload_data.url mit upload_data.fields + file   (direkt zu S3/MinIO)
3. PATCH /api/assets/v2/workspaces/{slug}/[projects/{pid}/]{asset_id}/  {attributes?}
      → is_uploaded=true, Metadaten-Task, Entitätsverknüpfung (Logo/Cover)
4. (Editor) POST …/projects/{pid}/{entity_id}/bulk/ {asset_ids}  → Zuordnung zu Issue/Kommentar/Page/Draft nach dem Speichern der Entität
```

MinIO-Spezialfall (`apps/api/plane/settings/storage.py`): bei `USE_MINIO=1` wird der Presigned-Endpoint auf `"{scheme}://{request.get_host()}"` gesetzt (Upload läuft über den Reverse-Proxy des Plane-Hosts), Protokoll `https` wenn `MINIO_ENDPOINT_SSL=1`, sonst Request-Schema. Presigned-GET-Gültigkeit `SIGNED_URL_EXPIRATION` (Default 3600 s).

**`can_modify_asset(user, asset)`** (`V/asset/v2.py`):

| Asset-Typ | Erlaubt, wenn |
|---|---|
| `WORKSPACE_LOGO` | aktiver WS-Admin |
| `PROJECT_COVER` (mit `project_id`) | Projekt-Admin (WS-Admin mit Projektmitgliedschaft zählt als Admin) |
| `ISSUE_ATTACHMENT` | Uploader (mit aktiver Projektmitgliedschaft, falls Projekt) **oder** Projekt-Admin |
| alle anderen | Uploader mit Mitgliedschaft (Projekt bzw. Workspace) **oder** Rolle ∈ {Admin, Member} (Projektrolle bei Projekt-Assets, sonst WS-Rolle) |

Zusätzlich: WS-Endpunkte A-09/A-10/A-11 prüfen bei projektgebundenen Assets aktive Projektmitgliedschaft (`has_project_asset_access`). A-24 (Download) prüft das **nicht**.

**Löschsemantik:** v2 setzt `is_deleted=True` **und** `deleted_at` (für Default-Manager unsichtbar, A-15 stellt beides zurück); Legacy v1 setzt nur `is_deleted`. Physisches Löschen im Bucket erfolgt durch Aufräum-Tasks (`BG/file_asset_task.py`, A02a/A01).

### 3.14 Suche im Detail

#### 3.14.1 Globale Suche (SR-01, Command-Palette)

| Entität | Suchfelder (`ILIKE '%q%'`) | Scope | Limit | Sortierung |
|---|---|---|---|---|
| `workspace` | `name` | Workspaces mit Mitgliedschaft (**ohne** `is_active`-Prüfung) | – | `-created_at` |
| `project` | `name`, `identifier` | aktive Mitgliedschaft, nicht archiviert, im Workspace | – | `-created_at` |
| `issue` | `name`, `project__identifier`; zusätzlich jede ganze Zahl im Suchtext (`\b\d+\b`) als exakte `sequence_id` | `Issue.issue_objects`, aktive nicht gelöschte Mitgliedschaft, Projekt nicht archiviert; Gäste ohne `guest_view_all_features` nur eigene | 100 | keine |
| `cycle` | `name` | aktive Mitgliedschaft, Projekt nicht archiviert | – | `-created_at` |
| `module` | `name` | dito | – | `-created_at` |
| `issue_view` | `name` | dito, Gast-Regel wie Issues, private Views (`access=0`) nur eigene | – | `-created_at` |
| `page` | `name` | über verknüpfte Projekte, Gast-Regel, private Pages (`access=1`) nur eigene; liefert `project_ids`/`project_identifiers` aller verknüpften Projekte | – | `-created_at` |
| `intake` | wie `issue` | `Issue.objects` mit Intake-Status ∈ {0, -2} | 100 | `-created_at` |

`workspace_search == "false"` **und** `project_id` gesetzt → alle projektbezogenen Entitäten auf dieses Projekt beschränkt (Pages über `ProjectPage`). Ohne `search` → keine Textbedingung (alle sichtbaren Objekte). Hinweis: Die Filter `~Q(projects__id=True)` in den Page-`ArrayAgg`s sind wirkungslos.

#### 3.14.2 Entity-Suche (SR-03, Mentions & Picker)

| `query_type` | mit `project_id` | ohne `project_id` | Felder / Besonderheiten |
|---|---|---|---|
| `user_mention` | aktive `ProjectMember` (kein Bot) des angegebenen Projekts (Mitgliedschaft des Suchenden wird **nicht** geprüft) | aktive `WorkspaceMember` (kein Bot) | Suche in `first_name`, `last_name`, `display_name`; `member__avatar_url` = `/api/assets/v2/static/{asset}/` oder Legacy-Avatar; Sortierung `-created_at` (Mitgliedschaft) |
| `project` | wie ohne | Projekte mit Mitgliedschaft (auch inaktiv/soft-gelöscht!) **oder** `network=2`, inkl. archivierter | `name`, `identifier` |
| `issue` | Issues des Projekts | alle sichtbaren Issues des Workspaces (inkl. archivierter Projekte) | `name`, `project__identifier`, `sequence_id`-Zahlen; Gast-Regel |
| `cycle` | Cycles des Projekts | Cycles aller Mitgliedsprojekte | `status` berechnet: `CURRENT` (start ≤ now ≤ end), `UPCOMING` (start > now), `COMPLETED` (end < now), sonst `DRAFT` |
| `module` | Module des Projekts | Module aller Mitgliedsprojekte | `status` = Modul-Status (`backlog`, `planned`, `in-progress`, `paused`, `completed`, `cancelled`) |
| `page` | öffentliche Pages (`access=0`) des Projekts | öffentliche **globale** Pages (`is_global=True`) | Gast-Regel; `projects__id` (ein Projekt je Zeile) |

Alle Ergebnisse auf `count` (Default 5) begrenzt.

#### 3.14.3 Issue-Suche für Picker (SR-02)

Basis: sichtbare Issues (Gast-Regel), Projekt nicht archiviert, `Issue.issue_objects`. Reihenfolge der Filter:

| Parameter | Wirkung |
|---|---|
| `workspace_search != "true"` | nur URL-Projekt |
| `search` | `search_issues` (`UT/issue_search.py`): `name ILIKE`, `project__identifier ILIKE`, bei Suchtext ≤ 20 Zeichen jede ganze Zahl als `sequence_id`, sonst `sequence_id ILIKE` |
| `parent=true` + `issue_id` | schließt das Issue selbst, seinen Parent und seine direkten Kinder aus (Parent-Picker) |
| `issue_relation=true` + `issue_id` | schließt das Issue und alle bereits in Relation stehenden Issues aus |
| `sub_issue=true` + `issue_id` | nur Root-Issues (`parent IS NULL`) ohne das Issue selbst und ohne dessen Parent (Sub-Issue-Picker) |
| `cycle=true` | schließt Issues mit aktiver Cycle-Zuordnung aus |
| `module=<id>` | schließt Issues dieses Moduls aus |
| `target_date=none` | nur Issues ohne Zieldatum (Gantt/Kalender-Picker) |

### 3.15 Analytics im Detail

#### 3.15.1 Legacy-Plot (`UT/analytics_plot.py` `build_graph_plot`)

- `VALID_ANALYTICS_FIELDS` = `state_id`, `state__group`, `labels__id`, `assignees__id`, `estimate_point__value`, `issue_cycle__cycle_id`, `issue_module__module_id`, `priority`, `start_date`, `target_date`, `created_at`, `completed_at`; `VALID_YAXIS` = `issue_count`, `estimate`.
- Datumsachsen (`created_at`, `start_date`, `target_date`, `completed_at`) → Dimension `"{Jahr}-{Monat}"` (ohne führende Null, z. B. `"2024-3"`); `NULL`-Dimensionen werden ausgeschlossen.
- `issue_count`: `COUNT(*)` je (Dimension[, Segment]); `estimate`: `SUM(CAST(estimate_point.value AS float))`.
- Ergebnis gruppiert nach Dimension (String); Sortierung: bei `priority` feste Reihenfolge `low, medium, high, urgent, none`, sonst alphabetisch mit `"none"` zuletzt.

#### 3.15.2 Advance Analytics (`UT/date_utils.py` `get_analytics_filters`)

- Basisfilter Issues/Cycles/Modules/Pages/Views: `workspace__slug`, User aktives Projektmitglied (`project__project_projectmember__member=user, is_active=True` – ohne `deleted_at`-Prüfung), Projekt nicht gelöscht/archiviert, optional `project_id IN project_ids`.
- `date_filter` (Typ „analytics“, AN-11/AN-14): `yesterday` (gestern 00:00–23:59:59.999999), `last_7_days` (heute-7 … heute), `last_30_days`, `last_3_months` (90 Tage), `custom` (benötigt `start_date`/`end_date`, die von den Views **nicht** übergeben werden → wirkungslos). Gefiltert wird auf `created_at` des jeweiligen Objekts (bei Mitgliedern: Beitrittsdatum). Die berechneten Vorperioden (`previous`) werden **nicht** ausgeliefert (`filter_count` auskommentiert).
- `date_filter` (Typ „chart“, AN-12/AN-13/AN-15/AN-16): Datumsbereich `(start, end)` als Datumswerte (`created_at__date` in Benutzerzeitzone); unbekannt → kein Filter.
- `total_intake` (AN-11) zählt Issues mit beliebigem Intake-Status (`-2, -1, 0, 1, 2`, als Strings).
- `work_item_completion_chart` (AN-13 `work-items`): Monatsreihe vom Erstellungsmonat des **Workspaces** bis zum aktuellen Monat (bzw. ab Filterstart), je Monat `created_count` (erstellt im Monat) und `completed_count` (davon aktuell in Gruppe `completed`).

#### 3.15.3 Benutzerdefinierte Charts (`UT/build_chart.py` `build_analytics_chart`)

| `x_axis` / `group_by` | ID-Feld | Namensfeld | Zusatzfilter |
|---|---|---|---|
| `STATES` | `state__id` | `state__name` | – |
| `STATE_GROUPS` | `state__group` | `state__group` | – |
| `LABELS` | `labels__id` | `labels__name` | `label_issue__deleted_at IS NULL` |
| `ASSIGNEES` | `assignees__id` | `assignees__display_name` | `issue_assignee__deleted_at IS NULL` |
| `ESTIMATE_POINTS` | `estimate_point__key` | `estimate_point__value` | – |
| `CYCLES` | `issue_cycle__cycle_id` | `issue_cycle__cycle__name` | `issue_cycle__deleted_at IS NULL` |
| `MODULES` | `issue_module__module_id` | `issue_module__module__name` | `issue_module__deleted_at IS NULL` |
| `PRIORITY` | `priority` | `priority` | – |
| `START_DATE` | `start_date` | `start_date` | – |
| `TARGET_DATE` | `target_date` | `target_date` | – |
| `CREATED_AT` | `created_at__date` | `created_at__date` | – |
| `COMPLETED_AT` | `completed_at__date` | `completed_at__date` | – |
| `CREATED_BY` | `created_by_id` | `created_by__display_name` | – |

Ohne `group_by`: `data = [{"key": <id\|"None">, "name": <name\|"None">, "count": COUNT(DISTINCT id)}]` sortiert nach `key`, `schema = {}`. Mit `group_by`: je x-Wert ein Objekt `{"key": <id\|"none">, "name": <name\|"None">, "count": Summe, "<group_key\|none>": count, …}`, `schema = {"<group_key\|none>": "<group_name\|None>"}`; Sortierung nach `count` absteigend (Reihenfolge des ersten Auftretens). Achtung: Zusatzfilter (z. B. `label_issue__deleted_at IS NULL`) entfernen Issues **ohne** Label aus dem Ergebnis.

### 3.16 Export

Siehe X-01. Dateinamen im ZIP und Spaltenlayout bestimmt `DataExporter`/`IssueExportSerializer` (`UT/porters/*`, Analyse Hintergrundjobs). Frontend zeigt die Historie (X-02) mit Download-Link `url` (Presigned, 7 Tage gültig; nach 8 Tagen löscht der periodische Task `BG/exporter_expired_task.py` `delete_old_s3_link` das S3-Objekt und entfernt die URL).

### 3.17 External: KI-Assistent und Unsplash

**LLM-Konfiguration (`get_llm_config`, `V/external/base.py`):** Werte `LLM_API_KEY` (verschlüsselt in `InstanceConfiguration`), `LLM_PROVIDER` (Default `openai`), `LLM_MODEL` (Instanz-Default `gpt-4o-mini`; `GPT_ENGINE` ist deprecated). Unterstützte Provider/Modelle (Whitelist):

| Provider-Key | Name | Modelle | Default |
|---|---|---|---|
| `openai` | OpenAI | `gpt-3.5-turbo`, `gpt-4o-mini`, `gpt-4o`, `o1-mini`, `o1-preview` | `gpt-4o-mini` |
| `anthropic` | Anthropic | `claude-3-5-sonnet-20240620`, `claude-3-haiku-20240307`, `claude-3-opus-20240229`, `claude-3-sonnet-20240229`, `claude-2.1`, `claude-2`, `claude-instant-1.2`, `claude-instant-1` | `claude-3-sonnet-20240229` |
| `gemini` | Gemini | `gemini-pro`, `gemini-1.5-pro-latest`, `gemini-pro-vision` | `gemini-pro` |

Unbekannter Provider, fehlender Key oder Modell außerhalb der Whitelist → `(None, None, None)` → 400 `{"error": "LLM provider API key and model are required"}` (Ursache nur im Log).

**Aufruf (`get_llm_response`):** Prompt = `task + "\n" + prompt` als **eine** `user`-Nachricht (fehlt `prompt` im Body, ist er `False` → `TypeError` bei der String-Verkettung außerhalb des `try` → 500 `{"error": "Something went wrong please try again later"}`; das Frontend sendet immer `prompt || ""`); Client ist **immer** `openai.OpenAI(api_key=…)` ohne `base_url` – Anthropic- und Gemini-Konfigurationen schicken die Anfrage daher an die OpenAI-API (Gemini mit Modellpräfix `gemini/`, LiteLLM-Stil) und scheitern. Fehlerklassen `AuthenticationError`/`RateLimitError`/sonst werden geloggt; Antwort an Client stets 500 `{"error": "An internal error has occurred."}`. `response_html` ersetzt nur Zeilenumbrüche durch `<br/>` (kein Markdown-Rendering, kein Escaping).

**Frontend-Konfigurationsflag:** `has_llm_configured` / `has_unsplash_configured` aus der Instanz-Konfiguration (`packages/types/src/instance/base.ts`, Backend `apps/api/plane/license/api/views/instance.py`, A-Admin-Analyse) steuern die Sichtbarkeit der KI-Schaltflächen und des Unsplash-Tabs im Bild-Picker (`WEB/components/core/image-picker-popover.tsx`).

**Unsplash (EXT-01):** reiner Proxy; Response ist bei Suche `{"total", "total_pages", "results": [...]}` bzw. ohne Suche ein Array; das Frontend normalisiert (`res.data.results ?? res.data`). Ohne Key → `[]`.

### 3.18 Timezones (T-01) – vollständige Liste

Format je Eintrag `label = value` (Reihenfolge im Code; Ausgabe sortiert nach aktuellem Offset, dann Label): Midway Island = Pacific/Midway; American Samoa = Pacific/Pago_Pago; Hawaii = Pacific/Honolulu; Aleutian Islands = America/Adak; Marquesas Islands = Pacific/Marquesas; Alaska = America/Anchorage; Gambier Islands = Pacific/Gambier; Pacific Time (US and Canada) = America/Los_Angeles; Baja California = America/Tijuana; Mountain Time (US and Canada) = America/Denver; Arizona = America/Phoenix; Chihuahua, Mazatlan = America/Chihuahua; Central Time (US and Canada) = America/Chicago; Saskatchewan = America/Regina; Guadalajara, Mexico City, Monterrey = America/Mexico_City; Tegucigalpa, Honduras = America/Tegucigalpa; Costa Rica = America/Costa_Rica; Eastern Time (US and Canada) = America/New_York; Lima = America/Lima; Bogota = America/Bogota; Quito = America/Guayaquil; Chetumal = America/Cancun; Caracas (Old Venezuela Time) = America/Caracas; Atlantic Time (Canada) = America/Halifax; Caracas = America/Caracas; Santiago = America/Santiago; La Paz = America/La_Paz; Manaus = America/Manaus; Georgetown = America/Guyana; Bermuda = Atlantic/Bermuda; Newfoundland Time (Canada) = America/St_Johns; Buenos Aires = America/Argentina/Buenos_Aires; Brasilia = America/Sao_Paulo; Greenland = America/Godthab; Montevideo = America/Montevideo; Falkland Islands = Atlantic/Stanley; South Georgia and the South Sandwich Islands = Atlantic/South_Georgia; Azores = Atlantic/Azores; Cape Verde Islands = Atlantic/Cape_Verde; Dublin = Europe/Dublin; Reykjavik = Atlantic/Reykjavik; Lisbon = Europe/Lisbon; Monrovia = Africa/Monrovia; Casablanca = Africa/Casablanca; Central European Time (Berlin, Rome, Paris) = Europe/Paris; West Central Africa = Africa/Lagos; Algiers = Africa/Algiers; Lagos = Africa/Lagos; Tunis = Africa/Tunis; Eastern European Time (Cairo, Helsinki, Kyiv) = Europe/Kyiv; Athens = Europe/Athens; Jerusalem = Asia/Jerusalem; Johannesburg = Africa/Johannesburg; Harare, Pretoria = Africa/Harare; Moscow Time = Europe/Moscow; Baghdad = Asia/Baghdad; Nairobi = Africa/Nairobi; Kuwait, Riyadh = Asia/Riyadh; Tehran = Asia/Tehran; Abu Dhabi = Asia/Dubai; Baku = Asia/Baku; Yerevan = Asia/Yerevan; Astrakhan = Europe/Astrakhan; Tbilisi = Asia/Tbilisi; Mauritius = Indian/Mauritius; Kabul = Asia/Kabul; Islamabad = Asia/Karachi; Karachi = Asia/Karachi; Tashkent = Asia/Tashkent; Yekaterinburg = Asia/Yekaterinburg; Maldives = Indian/Maldives; Chagos = Indian/Chagos; Chennai = Asia/Kolkata; Kolkata = Asia/Kolkata; Mumbai = Asia/Kolkata; New Delhi = Asia/Kolkata; Sri Jayawardenepura = Asia/Colombo; Kathmandu = Asia/Kathmandu; Dhaka = Asia/Dhaka; Almaty = Asia/Almaty; Bishkek = Asia/Bishkek; Thimphu = Asia/Thimphu; Yangon (Rangoon) = Asia/Yangon; Cocos Islands = Indian/Cocos; Bangkok = Asia/Bangkok; Hanoi = Asia/Ho_Chi_Minh; Jakarta = Asia/Jakarta; Novosibirsk = Asia/Novosibirsk; Krasnoyarsk = Asia/Krasnoyarsk; Beijing = Asia/Shanghai; Singapore = Asia/Singapore; Perth = Australia/Perth; Hong Kong = Asia/Hong_Kong; Ulaanbaatar = Asia/Ulaanbaatar; Palau = Pacific/Palau; Eucla = Australia/Eucla; Tokyo = Asia/Tokyo; Seoul = Asia/Seoul; Yakutsk = Asia/Yakutsk; Adelaide = Australia/Adelaide; Darwin = Australia/Darwin; Sydney = Australia/Sydney; Brisbane = Australia/Brisbane; Guam = Pacific/Guam; Vladivostok = Asia/Vladivostok; Tahiti = Pacific/Tahiti; Lord Howe Island = Australia/Lord_Howe; Solomon Islands = Pacific/Guadalcanal; Magadan = Asia/Magadan; Norfolk Island = Pacific/Norfolk; Bougainville Island = Pacific/Bougainville; Chokurdakh = Asia/Srednekolymsk; Auckland = Pacific/Auckland; Wellington = Pacific/Auckland; Fiji Islands = Pacific/Fiji; Anadyr = Asia/Anadyr; Chatham Islands = Pacific/Chatham; Nuku'alofa = Pacific/Tongatapu; Samoa = Pacific/Apia; Kiritimati Island = Pacific/Kiritimati. (120 Einträge; `Caracas` und `Lagos` mehrfach mit unterschiedlichen Labels; `Pacific/Tahiti` ist real UTC−10 trotz Kommentar „UTC+10“.)

**Offset-Formatierung (Bug):** `hours = total_seconds // 3600` (Floor-Division), `minutes = abs(total_seconds % 3600) // 60`. Für negative Halbstunden-Offsets entsteht eine falsche Anzeige: Marquesas (−09:30) → `"UTC-10:30"`, Newfoundland (−03:30, ohne DST) → `"UTC-04:30"`. Positive Offsets sind korrekt. Die .NET-Implementierung sollte das korrigieren (Abweichung von 1:1 ist ein Bugfix; in `migration/` als Entscheidung dokumentieren) – siehe 6.

### 3.19 Konsolidierte Liste bekannter Bugs/Quirks dieses Bereichs

| # | Stelle | Verhalten im Original | Empfehlung .NET |
|---|---|---|---|
| Q-01 | W-02 `GET /api/workspaces/` | immer 400 (KeyError) | nicht anbieten oder wie U-17 |
| Q-02 | W-23 `last-visited-workspace` | immer 500 | Feld aus `Profile` lesen (Spezifikation siehe W-23) |
| Q-03 | W-15 `user.last_workspace_id` | wird nicht persistiert | `Profile.last_workspace_id` setzen (fachlich beabsichtigt) |
| Q-04 | W-50 Draft-Retrieve | nur WS-Admins | Ersteller + (A/M) erlauben |
| Q-05 | W-51/W-52 Creator-Prüfung | gegen falsches Modell bzw. Admin darf fremde Drafts löschen | Drafts strikt privat (nur Ersteller) |
| Q-06 | W-53 Cycle-Activity | `project_id="None"` | korrekte Projekt-ID |
| Q-07 | P-05 `PUT projects/{pk}/` | keine Rechteprüfung | nicht anbieten |
| Q-08 | P-10/P-12/P-13 Projekt-Einladungen | ohne Rechteprüfung | Projekt-Admin |
| Q-09 | P-11 Projekt-Einladung anlegen | immer 500 | Funktion implementieren (siehe 5.2) |
| Q-10 | P-14 Einladungsliste | ignoriert `slug` | auf Workspace filtern |
| Q-11 | P-27 Favoriten-Projekte | immer 500 | nicht anbieten (W-43 ersetzt) |
| Q-12 | P-32 … P-34 Deploy-Board-Detail | IDOR (fremde Boards) | auf URL-Projekt scopen |
| Q-13 | P-37/P-38 Member-Präferenzen | fremde Präferenzen änderbar | nur eigener `member_id` (oder Admin) |
| Q-14 | P-06 `intake_view` | nur über `inbox_view` setzbar | beide Namen akzeptieren |
| Q-15 | U-02 Mass-Assignment | sicherheitsrelevante User-Felder beschreibbar | Whitelist |
| Q-16 | U-03 Einziger-Admin-Prüfung | unwirksam | fachlich korrekt prüfen (oder bewusst weglassen; Entscheidung 6) |
| Q-17 | U-10 OAuth-Tokens | im Klartext ausgeliefert | Tokens nie ausliefern |
| Q-18 | AT-04 PATCH | liefert Token erneut | Token nicht ausliefern |
| Q-19 | E-03 Estimate anlegen | Waisen-Estimate bei Validierungsfehler | Transaktion, erst validieren |
| Q-20 | E-07 Key 0 | nicht anlegbar | `key` ≥ 0 erlauben (Frontend nutzt 1…n) |
| Q-21 | E-09 Reihenfolge | Activities vor 404-Prüfung | erst prüfen |
| Q-22 | N-01 Snooze-Filter | `snoozed=false` zeigt noch gesnoozte | „aktiv gesnoozt“ ausblenden (`snoozed_till > now`) – Entscheidung 6 |
| Q-23 | N-01 `subscribed`-Subquery | `IssueAssignee.pk = issue_id` | korrekt `issue_id` |
| Q-24 | N-10 `type` | `watching` statt `subscribed`, kein Komma-Split | Komma-Liste mit gleichen Werten wie N-01 |
| Q-25 | AN-05 Analytics-View-Update | `query` → `{}` | aus `query_dict` neu berechnen |
| Q-26 | AN-09 Estimate-Summen | Legacy-Feld `point` | Summe über `estimate_point.value` (bei Typ `points`) oder entfernen |
| Q-27 | EXT-01 Unsplash-URL | `page=$1` | korrekt; Timeout setzen |
| Q-28 | EXT-02/03 Provider | Anthropic/Gemini funktionieren nicht; fehlender `prompt` → 500 | OpenAI-kompatibler Client mit `base_url`; fehlender Prompt = `""` |
| Q-29 | T-01 Offsets | falsche negative Halbstunden-Offsets | korrekt formatieren |
| Q-30 | 2.1.6 Response-Cache | Invalidierung wirkungslos (stale bis 2 h) | kein Response-Cache |
| Q-31 | Relationsfilter über `project_projectmember` | soft-gelöschte Mitgliedschaften zählen, Duplikate | `deleted_at IS NULL`, `DISTINCT` |
| Q-32 | A-06 / A-05 GET | 500 | nicht anbieten (Legacy) |
| Q-33 | A-24 Workspace-Download | keine Projektprüfung | wie A-11 prüfen |
| Q-34 | A-08 `entity_identifier` | nicht validiert | Zugehörigkeit prüfen |
| Q-35 | SR-03 `user_mention` mit `project_id` | Mitgliedschaft des Suchenden ungeprüft | prüfen |
| Q-36 | SR-01 Workspace-Treffer | inaktive Mitgliedschaften zählen | `is_active` prüfen |
| Q-37 | W-61 Recents-Sortierung | nach `created_at` statt `visited_at` | **1:1 übernehmen** (UI-Reihenfolge), Entscheidung 6 |
| Q-38 | W-09 Re-Invite | still ignoriert | 1:1 übernehmen (keine Fehlermeldung im UI vorgesehen) |

---

## 4. Abhängigkeiten zu anderen Bereichen

| Bereich | Richtung | Berührungspunkte (Quelle) |
|---|---|---|
| A01 Gesamtarchitektur & Infrastruktur (`migration/analysis/01-gesamtarchitektur-infrastruktur.md`) | nutzt | Middleware-Kette, Session-Auth/Origin-Prüfung (`apps/api/plane/authentication/session.py`), Throttles, Redis-Cache (`UT/cache.py`), Celery-Broker, S3/MinIO (`apps/api/plane/settings/storage.py`), Read-Replica-Routing, `FILE_SIZE_LIMIT`, `SIGNED_URL_EXPIRATION`, `WEBHOOK_*`-Variablen |
| A02a Datenmodell Kern (`migration/analysis/02a-datenmodell-kern.md`) | nutzt | alle Modelle aus 2.13, Soft-Delete-Mechanik (`apps/api/plane/db/mixins.py`), Kaskaden-Task (`BG/deletion_task.py`), Seed-Daten (`apps/api/plane/seeds/data/*`), `ProjectMember.save` (ProjectUserProperty), `Workspace.delete` (Slug-Umbenennung), `Project.save` (Identifier/Zeitzone/Intake-Snoozes) |
| A04 Interne App-API Arbeitsobjekte (`migration/analysis/04-api-intern-arbeitsobjekte.md`) | nutzt / wird genutzt | Legacy-Filter `issue_filters`, `ComplexFilterBackend`/`IssueFilterSet`, `order_issue_queryset`, `issue_queryset_grouper`, `issue_on_results`, `issue_group_values`, Grouped-Paginatoren (W-35); `IssueCreateSerializer` und `issue_activity` (W-53, E-09); Labels-/Cycle-/Module-/Page-/View-Endpunkte (Workspace-Listen W-36, W-41, W-42 liefern deren Serializer); `ProjectPagePermission` wird dort verwendet; `recent_visited_task` für Issues/Pages |
| Öffentliche API `/api/v1/` (`apps/api/plane/api/*`) | wird genutzt | API-Tokens (AT-01 … AT-05) authentifizieren dort (`apps/api/plane/api/middleware/api_authentication.py`) |
| Authentifizierung (`apps/api/plane/authentication/*`) | gemeinsam | Session-Erzeugung/Logout, Magic-Code-Konstanten (`MagicCodeProvider.MAX_VERIFY_ATTEMPTS`), Passwortwechsel (`/auth/change-password/`), Reaktivierung deaktivierter Konten, `user_ip` |
| Instanz/Lizenz/God-Mode (`apps/api/plane/license/*`, A11) | nutzt | `get_configuration_value` (`DISABLE_WORKSPACE_CREATION`, `LLM_*`, `UNSPLASH_ACCESS_KEY`), `InstanceAdmin` (U-03, U-13), Konfig-Flags `has_llm_configured`/`has_unsplash_configured`, Cache `/api/instances/` (A-09) |
| Space/Public (`apps/api/plane/space/*`, A11) | wird genutzt | Deploy Boards (P-30 … P-34) liefern `anchor` für `/api/public/anchor/{anchor}/…`; Static-Assets (A-16) für öffentliche Avatare/Logos |
| Hintergrundjobs (`apps/api/plane/bgtasks/*`) | löst aus | alle Tasks aus 2.14 (E-Mail-Versand mit Templates in `apps/api/templates/emails/*`, Webhook-Versand/-Signatur, Export, Analytics-Export, Notifications) |
| Realtime/Live (`apps/live`, A12) | wird genutzt | `GET /api/users/me/` und Session-Prüfung durch den Live-Server (Cookie-Weitergabe, kein `Origin`-Header → CSRF-Ausnahme); Sticky-/Draft-`description_binary` (Yjs-Binärformat) |
| Editor (`packages/editor`, A12) | wird genutzt | Mentions (`entity-search`, `query_type=user_mention`), Asset-Upload/-Restore/-Check/-Duplicate (A-08 ff.), KI-Menü (`rephrase-grammar`, fehlt), Download-URLs (A-24/A-25 aus `packages/utils/src/editor/common.ts`) |
| Web-Frontend (`apps/web`) | Konsument | Services `WEB/services/*.ts`, `SVC/**`; Stores `WEB/store/{workspace,member,project,user,notifications,estimates,issue/workspace-draft,…}` |

---

## 5. Migrationshinweise (.NET Aspire / EF Core / PostgreSQL / Angular)

### 5.1 1:1 übertragbar (Vertrag = Original)

1. **Routen:** alle 216 Methode×Pfad-Kombinationen aus 2.5–2.11 (außer den in 5.3 als „nicht portieren“ markierten) mit identischen Pfaden unter `/api/`; Trailing Slash optional akzeptieren (z. B. ASP.NET-Routing mit `{**rest}` oder Middleware, die `…/` und `…` gleich behandelt), weil das Frontend beide Formen nutzt (2.15 C).
2. **JSON-Verträge:** Feldnamen `snake_case` (System.Text.Json `JsonNamingPolicy.SnakeCaseLower`), UUIDs als Strings, FKs als nackte UUID unter dem Relationsnamen (`workspace`, `project`, `member`, `owner`, …) bzw. mit `_id`-Suffix, wo der Serializer explizit `*_id` nennt (`project_id`, `workspace_id`, `state_id`, `lead_id`, `owned_by_id`, `type_id`). Datumswerte ISO-8601 mit Offset; `DateField` als `YYYY-MM-DD`. `BinaryField` als Base64.
3. **Vollständige Feldmengen** gemäß 2.12/2.13 – insbesondere dort, wo das Original `fields=` übergibt (wirkungslos). Read-only-Zusatzfelder, die im Original nicht annotiert sind, **weglassen** (nicht `null`), z. B. `role` in W-04, `status`/`is_favorite` in W-42.
4. **Statuscodes und Fehlertexte** exakt (das Frontend zeigt `error`/`detail` teils direkt in Toasts an und wertet Codes wie `PROJECT_NAME_ALREADY_EXIST`, 409 bei P-04, `status === true` bei W-01 aus). Uneinheitliche Formen beibehalten: `{"error": …}`, `{"detail": …}`, `{"message": …}`, DRF-Feldfehler `{"feld": ["…"]}`, Listen `["…"]`, `{"error_code": 5900, "error_message": "RATE_LIMIT_EXCEEDED"}`. Abweichende Erfolgscodes beibehalten (z. B. 200 statt 201 bei S-02, W-44, P-31, E-03; 204 bei W-51, P-28).
5. **Pagination:** Cursor-Format `value:offset:is_prev`, Antwortobjekt aus 2.2 (alle 12 Schlüssel), `per_page`-Grenzen (1000), Fehlertexte. Implementierung als generischer `PaginateAsync<T>(IQueryable<T>, orderBy, perPage, cursor)`-Helper mit `ORDER BY <key> NULLS LAST, created_at DESC` und `LIMIT perPage+1 OFFSET page*perPage`; gruppierte Variante per `ROW_NUMBER() OVER (PARTITION BY …)` (Details A04).
6. **Berechtigungsmodell:** `allow_permission` als ASP.NET-Core-Authorization-Requirement (`RoleRequirement(roles, level, creatorOf<TEntity>?)`) mit Handler, der exakt den Algorithmus aus 2.4.2 umsetzt (inkl. „WS-Admin + Projektmitglied = Projekt-Admin“). Die DRF-Permission-Klassen aus 2.4.3 als eigene Policies. Fehlerkörper unterscheiden: Decorator → `{"error": "You don't have the required permissions."}`, Klassen → `{"detail": "You do not have permission to perform this action."}`.
7. **Sichtbarkeitsprädikate** (`_visible_issues_q`, Gast-Regel `guest_view_all_features`, Page/View-Zugriff) als wiederverwendbare `Expression<Func<…,bool>>`-Bausteine.
8. **Defaults & Seeding:** Default-States (P-02), Default-JSONs (2.13), Home-/Sidebar-Seeding (W-59, W-67) inkl. `sort_order`-Formeln, Sortier-Arithmetik (`max+10000`, `min-10000`, `65535`), `sequence +15000` bei States.
9. **Zeitzonen:** Datumsextraktion/-gruppierung in `User.user_timezone` (`AT TIME ZONE`), DB in UTC (`timestamptz`), Zeitzonenliste T-01 als statische Ressource (NodaTime/TimeZoneInfo für aktuelle Offsets; .NET nutzt IANA-IDs nativ ab .NET 6).
10. **Validierungen:** Slug-/Namensregeln (W-03), Projekt-Sonderzeichen-Regex, URL-Erkennung `contains_url` (Regex aus `UT/url.py` 1:1 übernehmen, inkl. 1000/500-Zeichen-Grenzen), `has_alphanumeric` (Unicode `\p{L}\p{N}`), `sanitize_filename`, Webhook-URL-/SSRF-Regeln, MIME-Allowlist, `FILE_SIZE_LIMIT`.

### 5.2 Neu zu bauen bzw. zu vervollständigen (ADR-001: alle Features aktiv)

| Thema | Grundlage | Hinweise |
|---|---|---|
| `PATCH {W}/sidebar-preferences/{key}/` | Frontend `WEB/store/workspace/index.ts` | Body `{is_pinned?, sort_order?}`, Antwort analog W-67-Eintrag (Shape aus `IWorkspaceSidebarNavigationItem`, `packages/types`) – Vertrag aus Frontend-Typen ableiten |
| `POST {W}/rephrase-grammar/` (Editor-KI, „Pi“) | `WEB/components/pages/editor/ai/menu.tsx`, `WEB/services/ai.service.ts` | Request `{task: "ASK_ANYTHING", text_input, casual_score?, formal_score?}`, Response `{response}`; über denselben LLM-Provider wie EXT-03; Prompt-Design neu (kein Original vorhanden) – in der Bezahl-Feature-Analyse spezifizieren |
| Workspace-Bulk-Asset-Zuordnung `POST /api/assets/v2/workspaces/{slug}/{entity_id}/bulk/` | `WEB/components/comments/comment-create.tsx` | Semantik analog A-21 ohne Projekt (für workspace-weite Entitäten wie Teamspace-/Initiativ-Kommentare der Bezahl-Editionen) |
| Projekt-Einladungen per E-Mail (P-11 reparieren) | `V/project/invite.py` | vorgesehene Regeln aus P-11 + E-Mail-Task analog `workspace_invitation`; UI im CE nicht vorhanden → nur nötig, wenn die Bezahl-UI es nutzt |
| LLM-Provider-Abstraktion | `V/external/base.py` | **OpenAI-kompatibler** Client mit konfigurierbarer `base_url` (ADR-004: Ollama/vLLM/LM Studio lokal), Modell frei konfigurierbar statt Whitelist (Whitelist nur als UI-Vorschlag); optionale native Adapter für Anthropic/Gemini (z. B. über `Microsoft.Extensions.AI`); deaktivierbar → `has_llm_configured=false` blendet UI aus. Keine Monats-Limits (Cloud-Feature entfällt). |
| Unsplash | `V/external/base.py` | optional; im Airgapped-Betrieb Key leer → `[]` (UI zeigt dann nur Upload/Preset-Bilder). HTTP-Client mit Timeout und Proxy-Unterstützung. |
| Storage-Abstraktion | `apps/api/plane/settings/storage.py` | `IObjectStorage` mit S3/MinIO-Implementierung (Presigned POST/GET, Copy, Head, Delete). Für Installationen ohne S3: lokaler Provider, der einen eigenen Upload-Endpunkt mit S3-kompatiblem POST-Formular (`url` + `fields` inkl. signierter Policy) bereitstellt, damit das Frontend unverändert bleibt. |
| Hintergrundjobs | 2.14 | Celery-Tasks als .NET-Jobs (z. B. Outbox-Tabelle in PostgreSQL + `BackgroundService`, oder Hangfire/Quartz mit PostgreSQL-Storage – Entscheidung im Architektur-Dokument); Jobs: Workspace-Seed, E-Mails (Einladung, Projekt hinzugefügt, Deaktivierung, E-Mail-Wechsel), Webhook-Events, Issue-Activities, Export, Analytics-CSV, Asset-Metadaten, Soft-Delete-Kaskade, Recent-Visits |
| Webhook-Logs-UI | WH-07 | Endpunkt vorhanden, Frontend ruft ihn nicht – Bezahl-UI prüfen |
| Workspace-Themes | W-26 … W-30 | Endpunkte vorhanden, kein Frontend – nur bei Bedarf der Bezahl-UI |

### 5.3 Nicht portieren / bewusst korrigieren (Sicherheit, tote Pfade)

- Nicht anbieten: W-02 (oder sinnvoll implementieren), W-05 (PUT Workspace, ungenutzt), P-05 (PUT Projekt ohne Rechte), P-27, A-05/A-06 GET (500), U-04 nur falls Live/Space ihn nicht brauchen (laut A12 prüfen).
- Härtungen (Verhaltensänderung nur bei bisher unberechtigten Zugriffen, UI unverändert): Q-07, Q-08, Q-10, Q-12, Q-13, Q-15, Q-17, Q-18, Q-31, Q-33, Q-34, Q-35, Q-36 aus 3.19.
- Bugfixes mit sichtbarer Wirkung (benötigen Freigabe, da Abweichung vom 1:1-Verhalten): Q-02, Q-03, Q-04, Q-16, Q-22, Q-24, Q-25, Q-26, Q-28, Q-29 (siehe Abschnitt 6).

### 5.4 Fallstricke bei der Umsetzung

1. **Soft-Delete & Unique-Constraints:** Alle Unique-Constraints sind partiell (`WHERE deleted_at IS NULL`) → EF Core `HasIndex(...).IsUnique().HasFilter("deleted_at IS NULL")`. Soft-Delete per Global Query Filter – Achtung: EF-Filter wirken auch in Navigationen/Joins, das Original **nicht** (siehe Q-31). Das ist eine gewollte Korrektur, aber Zählungen (z. B. `is_sole_admin_of_any_project`, das soft-gelöschte Zeilen mitzählt) bewusst entscheiden.
2. **Workspace-Löschung:** Slug-Umbenennung `slug__<epoch>` nachbauen, sonst bleibt der Slug blockiert (W-01).
3. **Default-Sortierung:** Viele Endpunkte ohne explizites `ORDER BY` liefern in Model-Default-Reihenfolge (`-created_at`; `State`: `sequence`; `Estimate`: `name`; `EstimatePoint`: `value`). In .NET explizit setzen, sonst nichtdeterministisch.
4. **`ignore_conflicts`-Bulk-Inserts** (W-09, W-14, P-15, P-20, Seeding) → PostgreSQL `INSERT … ON CONFLICT DO NOTHING` (EF Core: `ExecuteSql` oder `EFCore.BulkExtensions`/`linq2db`), Semantik „still ignorieren“ beibehalten.
5. **Atomare Updates:** S-07 (eine UPDATE-Anweisung mit CASE) → `ExecuteUpdateAsync(s => s.SetProperty(x => x.Default, x => x.Id == pk))`. W-20 in Transaktion.
6. **Django-Validierungsreihenfolge:** Feldvalidatoren laufen vor `validate()`; einige View-Prüfungen laufen **vor** dem Serializer (W-03). Reihenfolge der Fehlermeldungen beibehalten, da das UI jeweils nur die erste anzeigt.
7. **CSRF-Äquivalent:** Keine Antiforgery-Tokens; stattdessen Origin-Allowlist-Middleware für unsichere Methoden mit Cookie-Auth (2.1 Authentifizierung). Fehlender `Origin` erlaubt (Live-Server).
8. **Rate-Limits:** ASP.NET Core Rate Limiter: global anonym 30/min (IP), `email_verification` 3/h (User), `authentication` 10/min (IP, konfigurierbar), `asset_id` 5/min (pro Asset-ID); Antwort 429 `{"error_code": 5900, "error_message": "RATE_LIMIT_EXCEEDED"}`. Zusätzlich Cache-basierte Zähler für E-Mail-Codes (Redis optional → `IDistributedCache`/PostgreSQL).
9. **Presigned POST:** AWS SDK for .NET bzw. MinIO-.NET-SDK (`PresignedPostPolicyAsync`) oder eigene SigV4-POST-Policy-Signatur; Bedingungen exakt: `bucket`, `["content-length-range", 1, size_limit]`, `Content-Type`, `key`. MinIO-Host-Umschreibung (Upload über Plane-Host) beachten.
10. **Redirect-Endpunkte** (A-11, A-16, A-20, A-24, A-25) liefern 302 – Angular lädt diese über `<img src>`/`<a href>`; `HttpClient` darf sie nicht abfangen.
11. **CSV-Export (W-33):** `QUOTE_ALL`, Formel-Injection-Schutz wie `sanitize_csv_row` (`UT/csv_utils.py`), Dateiname fix.
12. **Zufallswerte/Formate:** Tokens `plane_api_` + 32 Hex, `plane_wh_` + 32 Hex, Anchor 32 Hex, Einladungstoken (JWT HS256 – in .NET kann ein kryptographisch zufälliger Token verwendet werden, da er nur verglichen wird; Länge ≤ 255).
13. **Frontend-Parameter-Serialisierung:** Axios serialisiert Booleans als `"true"`/`"false"`; das Backend vergleicht Strings (`workspace_search == "false"`, `grouped == "true"`, `snoozed`-Dict). Angular-`HttpParams` erzeugen dieselben Strings – Server muss **String**-Vergleich behalten (z. B. `mentioned=false` gilt im Original als wahr!).
14. **`is_active`-Semantik:** Mitgliedschaften werden nie gelöscht, nur deaktiviert; fast alle Abfragen filtern `is_active = true`. Ausnahme W-17 (liefert inaktive mit `is_active=false`, das UI zeigt „suspended/removed“).
15. **Cache-Header:** `Cache-Control: private, max-age=12` + `Vary: Cookie` (U-01, U-05, U-08) und 2 h Seitencache (T-01) übernehmen; Response-Caching mit Invalidierung (2.1.6) **nicht** nachbauen.

### 5.5 Angular-Hinweise

- Die Services aus `WEB/services/{workspace,user,project/*,workspace-notification,webhook,file,sticky,estimate,timezone,analytics,ai,favorite/favorite,issue/workspace_draft}.service.ts` und `SVC/{workspace,user,file,developer,ai}/*` als Angular-Services 1:1 nachbilden (gleiche Methodennamen erleichtern das Portieren der Stores). Fehlerbehandlung: das Original wirft `error.response.data` bzw. `error.response` weiter – Komponenten lesen `err.error`, `err.status`, `err.data.error`.
- Upload-Ablauf (3.13) inkl. Fortschritt/Abbruch (`cancelUpload` in `WEB/services/file.service.ts`) und anschließendem `PATCH`.
- Notifications-Pagination: Cursor-String aus `next_cursor` unverändert zurückgeben.
- Analytics-Peek-View: Projekt-Pfad wird aus dem ersten Wert von `project_ids` gebildet (`WEB/services/analytics.service.ts` `processUrl`).

---

## 6. Offene Punkte

| # | Frage | Kontext | Vorschlag |
|---|---|---|---|
| O-01 | Sollen sichtbare Bugs des Originals korrigiert werden (Q-02, Q-03, Q-04, Q-16, Q-22, Q-24, Q-25, Q-26, Q-28, Q-29)? | ADR-005 verlangt 1:1-Verhalten der UI; die Korrekturen ändern Daten/Anzeigen geringfügig (z. B. Notification-Snooze-Filter, Zeitzonen-Labels) | Korrigieren und je Punkt im Changelog der Migration dokumentieren; visuelle Regressionstests mit korrigierten Referenzen |
| O-02 | Spezifikation der im CE fehlenden Endpunkte (`rephrase-grammar`, `sidebar-preferences/{key}`, Workspace-Bulk-Assets) | Kein Backend-Code im Repo; nur Frontend-Aufrufe | Aus Frontend-Typen/Komponenten und Bezahl-Feature-Analyse ableiten; ggf. Rückfrage beim Auftraggeber zu erwartetem Verhalten von „Pi“/Rephrase |
| O-03 | Projekt-Einladungen per E-Mail (P-11) – gibt es dafür eine UI in den Bezahl-Editionen? | CE-UI nutzt nur Direktzuordnung (P-20) | Ergebnis der Bezahl-Feature-Analyse abwarten; Endpunkt in reparierter Form bereitstellen |
| O-04 | Legacy-Endpunkte ohne Frontend (Analytics v1 AN-01 … AN-09, Dashboard U-20, Graphen U-18/U-19, Themes, Legacy-Assets v1) portieren? | Kein UI-Aufrufer in CE | Portieren nur, wenn Bezahl-UI oder öffentliche API sie nutzt; sonst weglassen (spart Aufwand) |
| O-05 | Recents-Reihenfolge (Q-37) | Sortierung nach erstem Besuch statt letztem | 1:1 lassen, bis UI-Vergleich entscheidet |
| O-06 | Konto-Deaktivierung: Einziger-Admin-Prüfung (Q-16) | Original deaktiviert faktisch immer | Fachliche Prüfung einführen (Fehlertexte existieren bereits) – Freigabe nötig |
| O-07 | `UserSessionEndpoint` (U-04) – wird er von Live/Space genutzt? | Kein Web-Aufrufer gefunden | In A11/A12 gegenprüfen; Endpunkt beibehalten (gering) |
| O-08 | Zielformat des LLM-Providers im Airgapped-Betrieb | ADR-004 | OpenAI-kompatibler Endpoint als Standard, konfigurierbar im God-Mode (`LLM_BASE_URL` als neue Instanz-Einstellung) – Admin-Analyse ergänzen |
