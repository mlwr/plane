# A04 – Interne App-API Teil 2: Arbeitsobjekte (Work Items/Issues, Intake, Cycles, Modules, Views, Pages)

> **Status:** IST-Analyse Plane v1.4.2 Community Edition (AGPL-3.0)
> **Bereich:** `apps/api/plane/app/urls/{issue,intake,cycle,module,views,page}.py`, alle Views in `apps/api/plane/app/views/{issue,intake,cycle,module,view,page}/`, zugehörige Serializer (`apps/api/plane/app/serializers/{issue,intake,cycle,module,view,page,base}.py`) und die Abfrage-Infrastruktur `apps/api/plane/utils/{grouper,order_queryset,paginator,global_paginator,issue_filters}.py` + `apps/api/plane/utils/filters/*`.
> **Bindend:** `migration/architecture/00-grundsatzentscheidungen.md` (ADR-000 … ADR-006). Insbesondere ADR-001 (alle Bezahl-Features aktiv), ADR-002 (Realtime in .NET), ADR-003 (Greenfield, API-Verträge fachlich am Original), ADR-004 (airgapped).
> **Konvention:** `{P}` = `/api/workspaces/{slug}/projects/{project_id}`, `{W}` = `/api/workspaces/{slug}`. Alle Pfade dieses Bereichs hängen unter dem Präfix `/api/` (`apps/api/plane/urls.py`: `path("api/", include("plane.app.urls"))`). Quellpfade sind relativ zum Repo-Root.

---

## Inhaltsverzeichnis

1. Überblick & Verantwortlichkeiten
2. Vollständige Inventare (Tabellen)
   - 2.1 Legende (Berechtigungen, Kürzel, Standard-Antwortformen)
   - 2.2 Work Items / Issues – Kern (`urls/issue.py`)
   - 2.3 Labels
   - 2.4 Kommentare & Reaktionen
   - 2.5 Links & Attachments
   - 2.6 Relationen & Sub-Issues
   - 2.7 Subscriber
   - 2.8 Archiv, Bulk, Deleted-Sync, Datum-Bulk
   - 2.9 Versionen (Issue-Versionen, Description-Versionen)
   - 2.10 Intake (`urls/intake.py`)
   - 2.11 Cycles (`urls/cycle.py`)
   - 2.12 Modules (`urls/module.py`)
   - 2.13 Views (`urls/views.py`)
   - 2.14 Pages (`urls/page.py`)
   - 2.15 Draft-Issues (Querverweis, `urls/workspace.py`)
   - 2.16 Serializer-Inventar
   - 2.17 Antwort-Formen (Shapes)
   - 2.18 Query-Parameter-Inventar (Legacy-Filter, Rich-Filter, group_by, order_by, Paginierung, expand/fields)
   - 2.19 Activity-Typen (`issue_activity`) und weitere Hintergrund-Tasks
   - 2.20 Fehlermeldungs-Inventar (wortgleich)
3. Verhalten / Logik / Abläufe im Detail
4. Abhängigkeiten zu anderen Bereichen
5. Migrationshinweise für .NET / EF Core / Angular
6. Offene Punkte

---

## 1. Überblick & Verantwortlichkeiten

### 1.1 Was dieser Bereich abdeckt

Dieser Bereich ist das fachliche Herz der internen App-API (vom Web-Client `apps/web` und vom Live-Server `apps/live` genutzt, **nicht** die öffentliche `api/v1`). Er umfasst:

| Domäne | URL-Datei | View-Dateien | Hauptmodelle (`apps/api/plane/db/models/…`) |
|---|---|---|---|
| Work Items (Issues) inkl. Labels, Kommentare, Reaktionen, Links, Attachments, Relationen, Sub-Issues, Subscriber, Archiv, Bulk, Versionen, Meta | `apps/api/plane/app/urls/issue.py` | `apps/api/plane/app/views/issue/{base,activity,archive,attachment,comment,label,link,reaction,relation,sub_issue,subscriber,version}.py` | `issue.py` (`Issue`, `IssueAssignee`, `IssueLabel`, `IssueLink`, `IssueComment`, `IssueActivity`, `IssueRelation`, `IssueMention`, `IssueSubscriber`, `IssueReaction`, `CommentReaction`, `IssueVote`, `IssueSequence`, `IssueVersion`, `IssueDescriptionVersion`), `label.py`, `asset.py` (`FileAsset`), `project.py` (`ProjectUserProperty`) |
| Intake (früher „Inbox“) | `apps/api/plane/app/urls/intake.py` | `apps/api/plane/app/views/intake/base.py` | `intake.py` (`Intake`, `IntakeIssue`, `IntakeIssueStatus`, `SourceType`) |
| Cycles | `apps/api/plane/app/urls/cycle.py` | `apps/api/plane/app/views/cycle/{base,issue,archive}.py` | `cycle.py` (`Cycle`, `CycleIssue`, `CycleUserProperties`), `favorite.py` (`UserFavorite`) |
| Modules | `apps/api/plane/app/urls/module.py` | `apps/api/plane/app/views/module/{base,issue,archive}.py` | `module.py` (`Module`, `ModuleMember`, `ModuleIssue`, `ModuleLink`, `ModuleUserProperties`) |
| Views (gespeicherte Ansichten, Projekt + Workspace) | `apps/api/plane/app/urls/views.py` | `apps/api/plane/app/views/view/base.py` | `view.py` (`IssueView`) |
| Pages (Projekt-Seiten) | `apps/api/plane/app/urls/page.py` | `apps/api/plane/app/views/page/{base,version}.py` | `page.py` (`Page`, `PageLog`, `PageLabel`, `ProjectPage`, `PageVersion`) |

Zusätzlich implementiert dieser Bereich die **zentrale Issue-Listen-Abfrage** (Filter → Sortierung → Gruppierung → Paginierung), die von Projekt-Issues, Archiv, Cycle-Issues, Module-Issues, Workspace-View-Issues, Issue-Detail-Listen und indirekt von Profil-/Workspace-Endpunkten (anderer Bereich) wiederverwendet wird (`apps/api/plane/utils/grouper.py`, `apps/api/plane/utils/order_queryset.py`, `apps/api/plane/utils/paginator.py`, `apps/api/plane/utils/issue_filters.py`, `apps/api/plane/utils/filters/filter_backend.py`, `apps/api/plane/utils/filters/filterset.py`).

**Umfang des Inventars (Abschnitt 2):** 164 Methode/Pfad-Kombinationen aus den sechs URL-Dateien (Issues-Kern 13, Labels 7, Kommentare/Reaktionen/Verlauf 13, Links/Attachments 15, Relationen/Sub-Issues 5, Subscriber 6, Archiv/Bulk/Sync 8, Versionen 4, Intake 12 (+ Aliase), Cycles 24, Modules 23, Views 16, Pages 18) zuzüglich 6 Draft-Endpunkten als Querverweis. Jede Zeile trägt eine ID (I…, L…, C…, K…, R…, S…, A…, V…, N…, Y…, M…, W…, G…, D…), auf die die Abschnitte 3–6 verweisen.

### 1.2 Gemeinsame technische Basis

| Aspekt | Verhalten | Quelle |
|---|---|---|
| Basisklassen | `BaseViewSet` (DRF `ModelViewSet` + `BasePaginator`) und `BaseAPIView` (DRF `APIView` + `BasePaginator`); beide mit `TimezoneMixin` und `ReadReplicaControlMixin` | `apps/api/plane/app/views/base.py` |
| Authentifizierung | `BaseSessionAuthentication` (Session-Cookie); Default-Permission `IsAuthenticated` | `apps/api/plane/app/views/base.py`, `apps/api/plane/settings/common.py` (`REST_FRAMEWORK`) |
| Zeitzone | `TimezoneMixin.initial()` aktiviert pro Request `request.user.user_timezone` → beeinflusst alle `__date`-Lookups (z. B. `created_at__date`) | `apps/api/plane/app/views/base.py` |
| Fehlerabbildung | `IntegrityError` → 400 `{"error": "The payload is not valid"}`; Django `ValidationError` → 400 `{"error": "Please provide valid detail"}`; `ObjectDoesNotExist` (jedes `.get()`-Miss) → 404 `{"error": "The required object does not exist."}`; `KeyError` → 400 `{"error": "The required key does not exist."}`; sonst 500 `{"error": "Something went wrong please try again later"}`. DRF-Exceptions (z. B. `ParseError`) werden normal als `{"detail": "..."}` gerendert; `NotAuthenticated` → 401; Throttling → 429 | `apps/api/plane/app/views/base.py` (`handle_exception`), `apps/api/plane/authentication/adapter/exception.py` |
| `fields` / `expand` Query-Parameter | Kommagetrennt; `BaseViewSet.fields`/`expand` liefern Listen oder `None` | `apps/api/plane/app/views/base.py` |
| Filter-Backends (Default) | `BaseViewSet`/`BaseAPIView`: `(DjangoFilterBackend, SearchFilter)`; `SearchFilter` nutzt `?search=` auf `search_fields`. Views mit Issue-Listen überschreiben auf `(ComplexFilterBackend,)` | `apps/api/plane/app/views/base.py` |
| DRF-Default-Pagination | **keine** (`REST_FRAMEWORK` hat kein `DEFAULT_PAGINATION_CLASS`) → Standard-`list()` von `ModelViewSet` liefert ein **unpaginiertes Array** | `apps/api/plane/settings/common.py` |
| Kompression | Viele Listen-Endpunkte mit `@method_decorator(gzip_page)` | z. B. `apps/api/plane/app/views/issue/base.py` |
| Read Replica | `use_read_replica` (Default False in Basis, `IssueActivityEndpoint` = True) | `apps/api/plane/utils/core/mixins/view.py`, `apps/api/plane/app/views/issue/activity.py` |
| Audit-Felder | `BaseModel.save()` setzt `created_by` (bei Insert) bzw. `updated_by` (bei Update) aus dem Thread-lokalen Request-User (`crum.get_current_user`). **`bulk_create`/`bulk_update`/`QuerySet.update` umgehen das** – dort werden IDs explizit gesetzt | `apps/api/plane/db/models/base.py` |
| Projektbasis | `ProjectBaseModel.save()` setzt `workspace = project.workspace` (nicht bei Bulk-Operationen) | `apps/api/plane/db/models/project.py` |
| Soft Delete | `instance.delete()` setzt `deleted_at` und startet `soft_delete_related_objects` (rekursive Kaskade gemäß `on_delete`); `QuerySet.delete()` setzt nur `deleted_at` per `UPDATE` (**keine Kaskade**); `delete(soft=False)` = harter Delete. Default-Manager (`objects`) filtert `deleted_at IS NULL` (auch in Subqueries wie `CycleIssue.objects.filter(...)`), `all_objects` nicht; **Relations-Lookups** (`labels__id`, `issue_intake__status`, …) wenden den Manager-Filter **nicht** an – daher die expliziten `…__deleted_at__isnull=True`-Bedingungen. Endgültiges Löschen nach `HARD_DELETE_AFTER_DAYS` durch `hard_delete`-Task (`apps/api/plane/bgtasks/deletion_task.py`) | `apps/api/plane/db/mixins.py`, `apps/api/plane/bgtasks/deletion_task.py` |

### 1.3 Berechtigungsmodell (Kurzfassung; Details in 2.1)

- Rollen: `ADMIN = 20`, `MEMBER = 15`, `GUEST = 5` (`apps/api/plane/app/permissions/base.py`, `ROLE`).
- **Decorator `allow_permission(allowed_roles, level="PROJECT", creator=False, model=None)`** (`apps/api/plane/app/permissions/base.py`):
  1. Wenn `creator=True` und `model` gesetzt: Nutzer muss aktives Workspace-Mitglied sein (sonst 403) und – bei `level != "WORKSPACE"` – aktives Projektmitglied (sonst 403). Ist `model.objects.filter(id=kwargs["pk"], created_by=user)` vorhanden → **Zugriff erlaubt, unabhängig von der Rolle**.
  2. `level="WORKSPACE"`: aktives `WorkspaceMember` mit Rolle ∈ `allowed_roles`.
  3. `level="PROJECT"` (Default): aktives `ProjectMember` mit Rolle ∈ `allowed_roles` **oder** (aktives Projektmitglied mit beliebiger Rolle **und** Workspace-Admin).
  4. Sonst 403 `{"error": "You don't have the required permissions."}`.
- DRF-Permission-Klassen (`apps/api/plane/app/permissions/project.py`, `workspace.py`, `page.py`) werden **zusätzlich** zum Decorator ausgewertet (Klasse zuerst, dann Decorator).
- **Gast-Einschränkung:** Ist der Nutzer Gast (`role=5`) und `Project.guest_view_all_features == False`, sieht er in fast allen Listen/Details nur Objekte mit `created_by = user` (Issues, Intake-Issues, Views: `owned_by`, Pages: `owned_by`). Diese Logik ist pro Endpunkt einzeln implementiert (siehe Tabellen).

### 1.4 Seiteneffekt-Infrastruktur (Kurzfassung; Details in 2.19 / 3.x)

| Mechanismus | Zweck | Quelle |
|---|---|---|
| `issue_activity.delay(type=…, requested_data, current_instance, issue_id, actor_id, project_id, epoch, subscriber=True, notification=False, origin, intake)` | Erzeugt `IssueActivity`-Zeilen (Verlauf), aktualisiert immer `issue.updated_at`, legt `origin` in Redis ab (600 s), und stößt bei `notification=True` den `notifications`-Task (In-App/E-Mail-Benachrichtigungen, Subscriber-Logik) an | `apps/api/plane/bgtasks/issue_activities_task.py` |
| `model_activity.delay(model_name, model_id, requested_data, current_instance, actor_id, slug, origin)` | Webhooks: bei `current_instance=None` ein `created`-Event, sonst pro geändertem Feld ein `updated`-Event (`webhook_activity`) | `apps/api/plane/bgtasks/webhook_task.py` |
| `issue_description_version_task.delay(updated_issue, issue_id, user_id, is_creating)` | Description-Versionierung von Work Items (Merge-Fenster 600 s pro Nutzer) | `apps/api/plane/bgtasks/issue_description_version_task.py` |
| `recent_visited_task.delay(slug, entity_name, entity_identifier, user_id, project_id)` | „Zuletzt besucht“ (max. 20 je Nutzer/Workspace, ältester wird gelöscht) | `apps/api/plane/bgtasks/recent_visited_task.py` |
| `page_transaction.delay(new_description_html, old_description_html, page_id)` | Extrahiert `mention-component`/`image-component` aus Page-HTML in `PageLog` | `apps/api/plane/bgtasks/page_transaction_task.py` |
| `track_page_version.delay(page_id, existing_instance, user_id)` | Page-Versionierung (Merge-Fenster 600 s, max. 20 Versionen) | `apps/api/plane/bgtasks/page_version_task.py` |
| `crawl_work_item_link_title.delay(id, url)` | Holt `<title>` und Favicon (Base64) eines Links in `IssueLink.metadata` | `apps/api/plane/bgtasks/work_item_link_task.py` |
| `copy_s3_objects_of_description_and_assets.delay(...)` | Kopiert eingebettete Bilder beim Page-Duplizieren und lässt den Live-Server `description_binary` neu erzeugen | `apps/api/plane/bgtasks/copy_s3_object.py` |
| `get_asset_object_metadata.delay(asset_id)` | Liest Storage-Metadaten eines Uploads | `apps/api/plane/bgtasks/storage_metadata_task.py` |
| `invalidate_cache(path="/api/workspaces/:slug/labels/", …)` | Invalidiert den Workspace-Label-Cache bei Label-Änderungen | `apps/api/plane/utils/cache.py` |

> Hinweis: Das Klassenattribut `webhook_event` (z. B. `IssueViewSet.webhook_event = "issue"`) und `bulk = True` werden im Code **nirgends ausgewertet** (tote Attribute; `grep` über `apps/api/plane`). Webhooks entstehen ausschließlich über `model_activity`.

---
## 2. Vollständige Inventare

### 2.1 Legende

**Berechtigungs-Kürzel**

| Kürzel | Bedeutung | Quelle |
|---|---|---|
| `AUTH` | Nur `IsAuthenticated` – **keine** Mitgliedschaftsprüfung außer evtl. Queryset-Filter (Sicherheitslücke, siehe 5.4) | `apps/api/plane/app/views/base.py` |
| `AP[A,M,G]` | `allow_permission([ADMIN, MEMBER, GUEST])` Projekt-Ebene (inkl. Workspace-Admin-Bypass bei aktiver Projektmitgliedschaft) | `apps/api/plane/app/permissions/base.py` |
| `AP[A,M]`, `AP[A]` | analog mit eingeschränkten Rollen | ebd. |
| `AP[…]+C(Model)` | wie oben **plus** Ersteller-Bypass: wenn `Model.created_by == user` für `kwargs["pk"]` → erlaubt | ebd. |
| `APW[…]` | `allow_permission(..., level="WORKSPACE")` – Rolle in `WorkspaceMember` | ebd. |
| `AP[]+C(Model)` | `allowed_roles=[]` → **nur** der Ersteller (`created_by`) | `apps/api/plane/app/views/view/base.py` |
| `PEP` | `ProjectEntityPermission`: GET/HEAD/OPTIONS → aktives Projektmitglied (jede Rolle); sonst Rolle ∈ {A, M} | `apps/api/plane/app/permissions/project.py` |
| `PBP` | `ProjectBasePermission`: GET → aktives **Workspace**-Mitglied; POST → Workspace-Rolle ∈ {A, M}; PUT/PATCH/DELETE → Projekt-Admin oder (Projektmitglied + Workspace-Admin) | ebd. |
| `PLP` | `ProjectLitePermission`: aktives Projektmitglied (jede Rolle, jede Methode) | ebd. |
| `PPP` | `ProjectPagePermission` (siehe 3.18.1) | `apps/api/plane/app/permissions/page.py` |
| „Gast-Filter“ | Gast (`role=5`) ohne `project.guest_view_all_features` sieht nur eigene Objekte (`created_by`/`owned_by`) | pro View |

**Antwort-Kürzel** (Details in 2.17)

| Kürzel | Bedeutung |
|---|---|
| `S-ISSUE-LIST` | Standard-Issue-Listenobjekt (flaches Dict aus `issue_on_results`) |
| `S-ISSUE-VALUES` | Issue-Dict aus `.values(...)` in `IssueViewSet.create`/`IssueListEndpoint` (wie S-ISSUE-LIST, aber **ohne** `state__group`, **mit** `deleted_at`, Datumsfelder in Nutzer-TZ) |
| `S-ISSUE-DETAIL` | `IssueDetailSerializer` |
| `ENV-PAGINATED` | Envelope von `BasePaginator.paginate` (`apps/api/plane/utils/paginator.py`) |
| `ENV-GLOBAL` | Envelope von `plane.utils.global_paginator.paginate` |
| `ENV-GROUPED` / `ENV-SUBGROUPED` | `ENV-PAGINATED`, dessen `results` ein Gruppen-Dict ist |

### 2.2 Work Items / Issues – Kern

Quelle URL: `apps/api/plane/app/urls/issue.py`; Views: `apps/api/plane/app/views/issue/base.py`.

| # | Methode | Pfad | View.Methode | Berechtigung | Request-Body | Query-Parameter | Response | Seiteneffekte / Besonderheiten |
|---|---|---|---|---|---|---|---|---|
| I1 | GET | `{P}/issues/list/` | `IssueListEndpoint.get` | `AP[A,M,G]` + Gast-Filter | – | `issues` (**Pflicht**, CSV von Issue-IDs), `filters` (Rich-JSON), alle Legacy-Filter (2.18.1), `order_by` (Default `-created_at`), `group_by`, `sub_group_by` (nur Einfluss auf ausgelassene M2M-Annotationen), `fields`, `expand` | 200: Array `S-ISSUE-VALUES` (Datumsfelder `created_at`/`updated_at` in Nutzer-TZ). Mit `fields` oder `expand`: Array `IssueSerializer(fields, expand)` | `recent_visited_task(entity_name="project", entity_identifier=project_id)`. Basis `Issue.issue_objects` + `state__deleted_at IS NULL`. 400 `{"error": "Issues are required"}` ohne `issues`. **Bug:** `group_by=labels__id` (o. ä.) lässt die Annotation `label_ids` weg, die `.values()` aber verlangt → 500 |
| I2 | GET | `{P}/issues/` | `IssueViewSet.list` (gzip) | `AP[A,M,G]` + Gast-Filter | – | `filters`, Legacy-Filter, `updated_at__gt`, `order_by` (Default `-created_at`), `group_by`, `sub_group_by`, `cursor`, `per_page` (Default 1000, Max 1000) | 200: `ENV-PAGINATED` mit Array `S-ISSUE-LIST` bzw. `ENV-GROUPED`/`ENV-SUBGROUPED` | `recent_visited_task(project)`. 400 `{"error": "Group by and sub group by cannot have same parameters"}`. 400 `{"detail": "Invalid group_by field: …"}` / `Invalid sub_group_by field: …`. Algorithmus: 3.1 |
| I3 | POST | `{P}/issues/` | `IssueViewSet.create` | `AP[A,M]` | `IssueCreateSerializer` (2.16): `name` (Pflicht), `description_html`, `description_json`, `description_binary`, `priority`, `state_id`, `parent_id`, `estimate_point`, `start_date`, `target_date`, `label_ids[]`, `assignee_ids[]`, `sort_order`, `is_draft`, `type`, `point`, `external_source`, `external_id` | – | 201: `S-ISSUE-VALUES` des neuen Issues | `issue_activity("issue.activity.created", requested_data=Request-Body, notification=True)`; `model_activity("issue", created)`; `issue_description_version_task(is_creating=True)`. Logik 3.4 |
| I4 | GET | `{P}/issues-detail/` | `IssueDetailEndpoint.get` | `AP[A,M,G]`; Rechte zusätzlich per `Exists(permission_subquery)` (Rolle > Gast, oder Gast mit `guest_view_all_features`, oder Gast + `created_by=user`) | – | `filters`, Legacy-Filter, `order_by`, `expand` ∈ {`issue_relation`, `issue_related`}, `fields` (ohne Wirkung), `cursor`, `per_page` | 200: `ENV-PAGINATED` mit `IssueListDetailSerializer` (2.16) – **keine** Gruppierung | Wird vom Client verwendet, wenn `expand` `issue_relation` enthält und kein `group_by` (Gantt mit Abhängigkeiten, `apps/web/services/issue/issue.service.ts` `getIssuesFromServer`) |
| I5 | GET | `{P}/v2/issues/` | `IssuePaginatedViewSet.list` | `AP[A,M,G]` + Gast-Filter | – | `cursor` (Format `page_size:page:offset`, Default `1000:0:0`), `description` (`true` → `description_html` mitliefern), `updated_at__gt` | 200: `ENV-GLOBAL`, `results` = Liste mit Feldern `id, name, state_id, state__group, sort_order, completed_at, estimate_point, priority, start_date, target_date, sequence_id, project_id, parent_id, cycle_id, created_at, updated_at, created_by, updated_by, is_draft, archived_at, module_ids, label_ids, assignee_ids, link_count, attachment_count, sub_issues_count` (+ `description_html`) | Sortierung `updated_at ASC` (Delta-Sync für den lokalen Client-Cache, `getIssuesForSync`) |
| I6 | GET | `{P}/issues/{pk}/` | `IssueViewSet.retrieve` | `AP[A,M,G]+C(Issue)` + Gast-Prüfung (403 `{"error": "You are not allowed to view this issue"}`) | – | `expand` (2.18.5; vom Client genutzt: `issue_reactions,issue_attachments,issue_link,parent`) | 200: `S-ISSUE-DETAIL` (ohne `is_intake`, da hier nicht annotiert); 404 `{"error": "The required object does not exist."}` | Basis `Issue.objects` (**inkl.** archivierte, Draft-, Triage-Issues). `recent_visited_task(entity_name="issue")` |
| I7 | PUT | `{P}/issues/{pk}/` | DRF-Default `update` (nicht überschrieben) | `AUTH` (!) | `IssueCreateSerializer` (voll) ohne `context` | – | 200 Serializer-Daten | **Keine** Activity/Webhooks; Kontext fehlt → bei `assignee_ids` 400 (KeyError). Sicherheitslücke (5.4); nicht vom Client genutzt |
| I8 | PATCH | `{P}/issues/{pk}/` | `IssueViewSet.partial_update` | `AP[A,M]+C(Issue)` | partielle `IssueCreateSerializer`-Felder (+ `skip_activity: bool`); `is_draft` ist hier read-only | – | 204 (leer); 404 `{"error": "Issue not found"}`; 400 Serializer-Fehler | Wenn **nicht** (`skip_activity` **und** `description_html` gesetzt): `issue_activity("issue.activity.updated", requested_data=writable_data, current_instance=IssueDetailSerializer(alt), notification=True)`, `model_activity("issue", updated)`, `issue_description_version_task(updated_issue=alter Zustand)`. Basis `issue_objects` (archivierte/Triage-Issues → 404) |
| I9 | DELETE | `{P}/issues/{pk}/` | `IssueViewSet.destroy` | `AP[A]+C(Issue)` | – | – | 204 | Soft-Delete (`issue.delete()` → Kaskade-Task); `UserRecentVisit` (entity `issue`) **hart** gelöscht; `issue_activity("issue.activity.deleted", requested_data={"issue_id"}, current_instance={}, notification=True, subscriber=False)`. **Kein** Webhook |
| I10 | GET | `{P}/user-properties/` | `ProjectUserDisplayPropertyEndpoint.get` | `AP[A,M,G]` | – | – | 200 `ProjectUserPropertySerializer` (alle Felder: `id, created_at, updated_at, deleted_at, filters, display_filters, display_properties, rich_filters, preferences, sort_order, created_by, updated_by, project, workspace, user`) | `get_or_create` (Defaults: `apps/api/plane/db/models/issue.py` `get_default_*`, `project.py` `get_default_preferences`) |
| I11 | PATCH | `{P}/user-properties/` | `ProjectUserDisplayPropertyEndpoint.patch` | `AP[A,M,G]` | partiell: `filters`, `display_filters`, `display_properties`, `rich_filters`, `preferences`, `sort_order` (read-only: `user, workspace, project`) | – | 200 Serializer | Objekt wird bei Bedarf erzeugt; JSON-Felder werden **komplett ersetzt** (kein Deep-Merge) |
| I12 | GET | `{P}/issues/{issue_id}/meta/` | `IssueMetaEndpoint.get` | `AP[A,M,G]` | – | – | 200 `{"sequence_id": int, "project_identifier": str}` | Basis `issue_objects`; 404 bei archiviert/Triage |
| I13 | GET | `{W}/work-items/{project_identifier}-{issue_identifier}/` | `IssueDetailIdentifierEndpoint.get` | `AUTH` + explizit: aktives Projektmitglied (403 `{"error": "You are not allowed to view this issue"}`) + Gast-Prüfung | – | `expand` | 200 `S-ISSUE-DETAIL` inkl. `is_intake` (Intake-Status ∈ {-2, 0}) ; 400 `{"error": "Invalid issue identifier"}` (nicht-ganzzahlig; negative Zahl erlaubt); 404 | Projekt per `identifier__iexact`; Basis `Issue.objects` (inkl. archiviert/Triage); `recent_visited_task(issue)` |

### 2.3 Labels

Views: `apps/api/plane/app/views/issue/label.py`; Serializer `LabelSerializer` (`apps/api/plane/app/serializers/issue.py`).

| # | Methode | Pfad | View.Methode | Berechtigung | Request-Body | Query | Response | Seiteneffekte / Besonderheiten |
|---|---|---|---|---|---|---|---|---|
| L1 | GET | `{P}/issue-labels/` | `LabelViewSet.list` (Default) | `PBP` (aktives Workspace-Mitglied); Queryset: `project__project_projectmember__member=user` (**ohne** `is_active`) | – | `search` (ohne Wirkung, keine `search_fields`) | 200 Array `LabelSerializer` (`parent, name, color, id, project_id, workspace_id, sort_order`), sortiert `sort_order ASC` | – |
| L2 | POST | `{P}/issue-labels/` | `LabelViewSet.create` | `PBP` (Workspace-Rolle A/M) **und** `AP[A]` | `name` (Pflicht), `color`, `parent`, `sort_order` | – | 201 Label | Duplikatprüfung `name__iexact` im Projekt → 400 `{"name": ["LABEL_NAME_ALREADY_EXISTS"]}`; `IntegrityError` → 400 `{"error": "Label with the same name already exists in the project"}`; `sort_order` = max+10000 (Model-`save`); Cache-Invalidierung Workspace-Labels (`multiple=True`) |
| L3 | GET | `{P}/issue-labels/{pk}/` | Default `retrieve` | `PBP` | – | – | 200 Label | – |
| L4 | PUT | `{P}/issue-labels/{pk}/` | Default `update` | `PBP` (Projekt-Admin bzw. WS-Admin+Mitglied) | Label-Felder | – | 200 | ohne Cache-Invalidierung |
| L5 | PATCH | `{P}/issue-labels/{pk}/` | `LabelViewSet.partial_update` | `PBP` + `AP[A]` | partielle Felder | – | 200 Label | Namensprüfung **case-sensitive** (`name=`) → 400 `{"error": "Label with the same name already exists in the project"}`, danach Serializer-Prüfung `iexact`; Cache-Invalidierung |
| L6 | DELETE | `{P}/issue-labels/{pk}/` | `LabelViewSet.destroy` | `PBP` + `AP[A]` | – | – | 204 | Soft-Delete + Kaskade (inkl. `IssueLabel`, `PageLabel`); Cache-Invalidierung |
| L7 | POST | `{P}/bulk-create-labels/` | `BulkCreateIssueLabelsEndpoint.post` | `AP[A]` | `label_data: [{name?, description?}]` | – | 201 `{"labels": [LabelSerializer…]}` | Default-Name `"Migrated"`, Default-Beschreibung `"Migrated Issue"`, Farbe zufällig `#RRGGBB`; `bulk_create(ignore_conflicts=True, batch_size=50)` (kein `sort_order`-Hochzählen) |

### 2.4 Kommentare & Reaktionen

Views: `apps/api/plane/app/views/issue/comment.py`, `apps/api/plane/app/views/issue/reaction.py`.

| # | Methode | Pfad | View.Methode | Berechtigung | Request-Body | Query | Response | Seiteneffekte / Besonderheiten |
|---|---|---|---|---|---|---|---|---|
| C1 | GET | `{P}/issues/{issue_id}/comments/` | `IssueCommentViewSet.list` → Default-`list` | `AP[A,M,G]`; Issue muss im Projekt liegen (`Issue.objects`, inkl. archiviert) sonst 404 `{"error": "Issue not found"}` | – | `issue__id`, `workspace__id` (DjangoFilter, praktisch redundant) | 200 Array `IssueCommentSerializer` (unpaginiert, Model-Ordering `-created_at`) | Queryset nur für aktive Projektmitglieder eines nicht archivierten Projekts; Annotation `is_member` |
| C2 | POST | `{P}/issues/{issue_id}/comments/` | `IssueCommentViewSet.create` | `AP[A,M,G]`; Gast ohne `guest_view_all_features` darf nur eigene Issues kommentieren → **400** `{"error": "You are not allowed to comment on the issue"}` | nur `comment_html`, `comment_json`, `access` (`INTERNAL`/`EXTERNAL`) werden übernommen (`COMMENT_WRITABLE_FIELDS`) | – | 201 `IssueCommentSerializer` | HTML-Sanitizing (`validate_html_content`, 400 `{"comment_html": "HTML content is not valid"}`); `actor=user`; Model-`save` erzeugt `Description`-Zeile und `comment_stripped`; `issue_activity("comment.activity.created", notification=True)`; `model_activity("issue_comment", created)`; 404 `{"error": "Issue not found"}` wenn Issue nicht im Projekt |
| C3 | GET | `{P}/issues/{issue_id}/comments/{pk}/` | Default `retrieve` | `AUTH` + Queryset (aktives Projektmitglied) | – | – | 200 | – |
| C4 | PUT | `{P}/issues/{issue_id}/comments/{pk}/` | Default `update` | `AUTH` + Queryset | alle Serializer-Felder | – | 200 | **Umgeht** Ersteller-Prüfung, `COMMENT_WRITABLE_FIELDS` und Activity (Sicherheitslücke, 5.4) |
| C5 | PATCH | `{P}/issues/{issue_id}/comments/{pk}/` | `IssueCommentViewSet.partial_update` | `AP[A]+C(IssueComment)` | `comment_html`, `comment_json`, `access` | – | 200 Serializer | `edited_at = now()` nur wenn `comment_html` sich ändert; `issue_activity("comment.activity.updated")`; `model_activity("issue_comment", updated)` |
| C6 | DELETE | `{P}/issues/{issue_id}/comments/{pk}/` | `IssueCommentViewSet.destroy` | `AP[A]+C(IssueComment)` | – | – | 204 | Soft-Delete; `issue_activity("comment.activity.deleted", requested_data={"comment_id"})`. **Kein** Webhook |
| C7 | GET | `{P}/issues/{issue_id}/reactions/` | Default `list` | `AUTH` + Queryset (aktives Projektmitglied, nicht archiviertes Projekt) | – | – | 200 Array `IssueReactionSerializer` | – |
| C8 | POST | `{P}/issues/{issue_id}/reactions/` | `IssueReactionViewSet.create` | `AP[A,M,G]` | `reaction` (Text, i. d. R. Emoji-Codepoint-String) | – | 201 `IssueReactionSerializer` | 404 wenn Issue nicht im Projekt; Duplikat (Unique `issue, actor, reaction`) → 400 `{"error": "The payload is not valid"}`; `issue_activity("issue_reaction.activity.created")` |
| C9 | DELETE | `{P}/issues/{issue_id}/reactions/{reaction_code}/` | `IssueReactionViewSet.destroy` | `AP[A,M,G]`; nur **eigene** Reaktion | – | – | 204; 404 | `issue_activity("issue_reaction.activity.deleted", current_instance={"reaction", "identifier"})`, danach Soft-Delete |
| C10 | GET | `{P}/comments/{comment_id}/reactions/` | Default `list` | `AUTH` + Queryset | – | – | 200 Array `CommentReactionSerializer` | – |
| C11 | POST | `{P}/comments/{comment_id}/reactions/` | `CommentReactionViewSet.create` | `AP[A,M,G]` | `reaction` | – | 201 | Kommentar muss in Workspace+Projekt liegen (404); Duplikat → 400 `{"error": "Reaction already exists for the user"}`; `issue_activity("comment_reaction.activity.created", issue_id=None)` |
| C12 | DELETE | `{P}/comments/{comment_id}/reactions/{reaction_code}/` | `CommentReactionViewSet.destroy` | `AP[A,M,G]`; nur eigene | – | – | 204 | `issue_activity("comment_reaction.activity.deleted", current_instance={"reaction","identifier","comment_id"})` |
| C13 | GET | `{P}/issues/{issue_id}/history/` | `IssueActivityEndpoint.get` (gzip) | `PEP` + `AP[A,M,G]`; Issue muss im Projekt liegen (inkl. archiviert) sonst 404 `{"error": "Issue not found"}` | – | `created_at__gt` (Datum/Zeit), `activity_type` ∈ {`issue-property`, `issue-comment`} | 200: ohne `activity_type` = **gemischtes** Array aus `IssueActivitySerializer` und `IssueCommentSerializer`, sortiert nach `created_at` (String-Vergleich); `issue-property` → nur Activities (mit `source_data` aus `IntakeIssue`); `issue-comment` → nur Kommentare | Activities ohne `field ∈ {comment, vote, reaction, draft}`; nur aktive Projektmitglieder; Read-Replica |

### 2.5 Links & Attachments

Views: `apps/api/plane/app/views/issue/link.py`, `apps/api/plane/app/views/issue/attachment.py`.

| # | Methode | Pfad | View.Methode | Berechtigung | Request-Body | Query | Response | Seiteneffekte / Besonderheiten |
|---|---|---|---|---|---|---|---|---|
| K1 | GET | `{P}/issues/{issue_id}/issue-links/` | Default `list` | `PEP` | – | – | 200 Array `IssueLinkSerializer` (sortiert `-created_at`) | – |
| K2 | POST | `{P}/issues/{issue_id}/issue-links/` | `IssueLinkViewSet.create` | `PEP` (A/M) | `url` (Pflicht), `title`, `metadata` | – | 201 `IssueLinkSerializer` (inkl. `created_by_detail`) | URL ohne Schema → `http://` vorangestellt; `URLValidator` → 400 mit Feldfehler unter `url` (Inhalt `{"error": "Invalid URL format."}`); Duplikat (gleiche URL am Issue) → 400 `{"error": "URL already exists for this Issue"}`; `crawl_work_item_link_title`; `issue_activity("link.activity.created")`; 404 wenn Issue nicht im Projekt |
| K3 | GET | `{P}/issues/{issue_id}/issue-links/{pk}/` | Default `retrieve` | `PEP` | – | – | 200 | – |
| K4 | PUT | `{P}/issues/{issue_id}/issue-links/{pk}/` | Default `update` | `PEP` (A/M) | Link-Felder | – | 200 | ohne Activity/Crawl |
| K5 | PATCH | `{P}/issues/{issue_id}/issue-links/{pk}/` | `IssueLinkViewSet.partial_update` | `PEP` (A/M) | `url`, `title`, `metadata` | – | 200 | Crawl nur bei geänderter URL; `issue_activity("link.activity.updated")` |
| K6 | DELETE | `{P}/issues/{issue_id}/issue-links/{pk}/` | `IssueLinkViewSet.destroy` | `PEP` (A/M) | – | – | 204 | `issue_activity("link.activity.deleted", requested_data={"link_id"})`, Soft-Delete |
| K7 | GET | `{P}/issues/{issue_id}/issue-attachments/` | `IssueAttachmentEndpoint.get` (v1, Legacy) | `AP[A,M,G]` | – | – | 200 Array `IssueAttachmentSerializer` | **Alle** `FileAsset` des Issues (jede `entity_type`, auch nicht hochgeladene) |
| K8 | POST | `{P}/issues/{issue_id}/issue-attachments/` | `IssueAttachmentEndpoint.post` (Multipart) | `AP[A,M,G]` | Multipart `asset` (Datei), `attributes` | – | 201 `IssueAttachmentSerializer` | Direkt-Upload über Django-Storage; `entity_type=ISSUE_ATTACHMENT`; `issue_activity("attachment.activity.created")` |
| K9 | GET | `{P}/issues/{issue_id}/issue-attachments/{pk}/` | `IssueAttachmentEndpoint.get` | – | – | – | **500** (Methode akzeptiert kein `pk`) | toter Pfad |
| K10 | DELETE | `{P}/issues/{issue_id}/issue-attachments/{pk}/` | `IssueAttachmentEndpoint.delete` | `AP[A]+C(FileAsset)` | – | – | 204; 404 `{"error": "Issue attachment not found."}` | Datei im Storage gelöscht, Record soft-deleted; `issue_activity("attachment.activity.deleted")` |
| K11 | GET | `/api/assets/v2/workspaces/{slug}/projects/{project_id}/issues/{issue_id}/attachments/` | `IssueAttachmentV2Endpoint.get` | `AP[A,M,G]` | – | – | 200 Array `IssueAttachmentSerializer` (nur `entity_type=ISSUE_ATTACHMENT`, `is_uploaded=True`) | – |
| K12 | GET | `…/attachments/{pk}/` | `IssueAttachmentV2Endpoint.get` | `AP[A,M,G]` | – | – | **302** Redirect auf presigned URL (`Content-Disposition: attachment; filename=<attributes.name>`); 400 `{"error": "The asset is not uploaded.", "status": false}` | – |
| K13 | POST | `…/attachments/` | `IssueAttachmentV2Endpoint.post` | `AP[A,M,G]` | `name`, `type` (MIME, Pflicht, aus `settings.ATTACHMENT_MIME_TYPES`), `size` (Default `FILE_SIZE_LIMIT`) | – | 200 `{"upload_data": <presigned POST>, "asset_id": str, "attachment": IssueAttachmentSerializer, "asset_url": str}`; 400 `{"error": "Invalid file type.", "status": false}` | Dateiname via `sanitize_filename` (Fallback `"unnamed"`); Key `"{workspace_id}/{uuid4hex}-{name}"`; `size = min(size, FILE_SIZE_LIMIT)` (Default 5 MiB, `apps/api/plane/settings/common.py`); `is_uploaded=False` |
| K14 | PATCH | `…/attachments/{pk}/` | `IssueAttachmentV2Endpoint.patch` | `AP[A,M,G]` | – (Body ignoriert) | – | 204 | Bestätigt Upload: setzt `is_uploaded=True` und erzeugt **nur beim ersten Mal** `issue_activity("attachment.activity.created")`; `get_asset_object_metadata` falls `storage_metadata` leer; `created_by` bleibt unverändert |
| K15 | DELETE | `…/attachments/{pk}/` | `IssueAttachmentV2Endpoint.delete` | `AP[A]+C(FileAsset)` | – | – | 204 | `is_deleted=True`, `deleted_at=now()` (Datei bleibt im Storage); `issue_activity("attachment.activity.deleted")` |

### 2.6 Relationen & Sub-Issues

Views: `apps/api/plane/app/views/issue/relation.py`, `apps/api/plane/app/views/issue/sub_issue.py`; Mapping `apps/api/plane/utils/issue_relation_mapper.py`.

| # | Methode | Pfad | View.Methode | Berechtigung | Request-Body | Query | Response | Seiteneffekte / Besonderheiten |
|---|---|---|---|---|---|---|---|---|
| R1 | GET | `{P}/issues/{issue_id}/issue-relation/` | `IssueRelationViewSet.list` | `PEP`; Issue im Projekt (inkl. archiviert) sonst 404 `{"error": "Issue not found"}` | – | – | 200 Objekt mit **genau 8** Schlüsseln: `blocking`, `blocked_by`, `duplicate`, `relates_to`, `start_after`, `start_before`, `finish_after`, `finish_before`; je Array mit `id, name, state_id, sort_order, priority, sequence_id, project_id, label_ids, assignee_ids, created_at, updated_at, created_by, updated_by, relation_type` | Relationen workspace-weit (projektübergreifend); Ziel-Issues aus `issue_objects` (archivierte/Triage-Ziele fehlen). **`implemented_by`/`implements` werden gespeichert, aber nicht ausgeliefert.** Mapping-Tabelle in 3.7 |
| R2 | POST | `{P}/issues/{issue_id}/issue-relation/` | `IssueRelationViewSet.create` | `PEP` (A/M) | `relation_type` (Pflicht) ∈ {`blocking`, `blocked_by`, `duplicate`, `relates_to`, `start_before`, `start_after`, `finish_before`, `finish_after`, `implemented_by`, `implements`}, `issues[]` | – | 201 Array `RelatedIssueSerializer` (bei `blocking`, `start_after`, `finish_after`) bzw. `IssueRelationSerializer`; 400 `{"message": "Issue relation type is required"}`; 404 `{"error": "Issue not found"}` | Ziel-IDs auf Workspace (`issue_objects`) begrenzt; `bulk_create(ignore_conflicts=True)`; Richtung/Typ gemäß 3.7; `issue_activity("issue_relation.activity.created", requested_data={"relation_type","issues"})` |
| R3 | POST | `{P}/issues/{issue_id}/remove-relation/` | `IssueRelationViewSet.remove_relation` | `PEP` (A/M) | `related_issue` (UUID) | – | 204; 404 `{"error": "Issue not found"}` / `{"error": "Issue relation not found"}` | Löscht **die erste** Relation in beide Richtungen (`issue↔related_issue`) unabhängig vom Typ (Soft-Delete); `issue_activity("issue_relation.activity.deleted", requested_data=Body, current_instance=IssueRelationSerializer)` |
| R4 | GET | `{P}/issues/{issue_id}/sub-issues/` | `SubIssuesEndpoint.get` (gzip) | `PEP` | – | `order_by` (Default `-created_at`, Allowlist 2.18.3), `group_by` (beliebiger Schlüssel der Ergebniszeile; Spezialwert `assignees__ids`) | 200 `{"sub_issues": [S-ISSUE-LIST-ähnlich + state_group] \| {group: [...]}, "state_distribution": {state_group: [issue_id,…]}}` | Nur direkte Kinder in **diesem** Projekt (`issue_objects`); Zähler mit `Coalesce(…, 0)`; Datumsfelder in Nutzer-TZ; Gruppierung in Python (3.8). Unbekannter `group_by` → 400 `{"error": "The required key does not exist."}` |
| R5 | POST | `{P}/issues/{issue_id}/sub-issues/` | `SubIssuesEndpoint.post` | `PEP` (A/M) | `sub_issue_ids[]` (Pflicht) | – | 200 `{"sub_issues": IssueSerializer[], "state_distribution": {...}}`; 404 `{"error": "Parent issue not found"}`; 400 `{"error": "Sub Issue IDs are required"}` | Nur Issues desselben Projekts (`issue_objects`) werden umgehängt (`bulk_update parent`); **keine Zyklenprüfung**; pro umgehängtem Issue `issue_activity("issue.activity.updated", requested_data={"parent": parent_id}, current_instance={"parent": sub_issue_id})` |

### 2.7 Subscriber

View: `apps/api/plane/app/views/issue/subscriber.py`.

| # | Methode | Pfad | View.Methode | Berechtigung | Request-Body | Query | Response | Seiteneffekte / Besonderheiten |
|---|---|---|---|---|---|---|---|---|
| S1 | GET | `{P}/issues/{issue_id}/issue-subscribers/` | `IssueSubscriberViewSet.list` | `PEP` | – | – | 200 Array `ProjectMemberLiteSerializer` **aller aktiven Projektmitglieder** (`{"member": UserLite, "id": project_member_id}`; `is_subscribed` wird mangels Attribut ausgelassen) | Liefert **nicht** die Subscriber, sondern die Mitgliederliste; S1–S3 werden vom Web-Client nicht aufgerufen (O6) |
| S2 | POST | `{P}/issues/{issue_id}/issue-subscribers/` | Default `create` + `perform_create` | `PEP` (A/M) | `subscriber` (User-UUID) | – | 201 `IssueSubscriberSerializer` | 404 wenn Issue nicht im Projekt; 400 `{"error": "Subscriber must be a member of the project."}`; Duplikat → 400 `{"error": "The payload is not valid"}` |
| S3 | DELETE | `{P}/issues/{issue_id}/issue-subscribers/{subscriber_id}/` | `IssueSubscriberViewSet.destroy` | `PEP` (A/M) | – | – | 204; 404 | Soft-Delete |
| S4 | GET | `{P}/issues/{issue_id}/subscribe/` | `subscription_status` | `PLP` | – | – | 200 `{"subscribed": bool}` | – |
| S5 | POST | `{P}/issues/{issue_id}/subscribe/` | `subscribe` | `PLP` | – | – | 201 `IssueSubscriberSerializer`; 400 `{"message": "User already subscribed to the issue."}`; 404 | – |
| S6 | DELETE | `{P}/issues/{issue_id}/subscribe/` | `unsubscribe` | `PLP` | – | – | 204; 404 | Soft-Delete |

### 2.8 Archiv, Bulk, Deleted-Sync, Datum-Bulk

Views: `apps/api/plane/app/views/issue/archive.py`, `apps/api/plane/app/views/issue/base.py`.

| # | Methode | Pfad | View.Methode | Berechtigung | Request-Body | Query | Response | Seiteneffekte / Besonderheiten |
|---|---|---|---|---|---|---|---|---|
| A1 | GET | `{P}/archived-issues/` | `IssueArchiveViewSet.list` (gzip) | `AP[A,M]` (Gäste: 403) | – | `show_sub_issues` (Default `"true"`; sonst nur `parent IS NULL`), `filters`, Legacy-Filter, `order_by`, `group_by`, `sub_group_by`, `cursor`, `per_page` | 200 `ENV-PAGINATED` / `ENV-GROUPED` / `ENV-SUBGROUPED` | Basis `Issue.objects` mit `archived_at IS NOT NULL` und (`type IS NULL` oder `type.is_epic=False`). **Bug:** `group_by`/`sub_group_by` ∈ {`target_date`, `start_date`, `created_by`} → 500 (kein `queryset` an `issue_group_values`) |
| A2 | GET | `{P}/issues/{pk}/archive/` | `IssueArchiveViewSet.retrieve` | `AP[A,M]` | – | `expand` | 200 `S-ISSUE-DETAIL` **ohne** die nicht annotierten Felder (`cycle_id`, `module_ids`, `label_ids`, `assignee_ids`, `sub_issues_count`, `attachment_count`, `link_count`, `is_intake` fehlen, da DRF read-only-Felder ohne Attribut per `SkipField` auslässt); 404 | Nur `is_subscribed` wird annotiert (`apps/api/plane/app/views/issue/archive.py`) |
| A3 | POST | `{P}/issues/{pk}/archive/` | `IssueArchiveViewSet.archive` | `AP[A,M]` | – | – | 200 `{"archived_at": "YYYY-MM-DD"}`; 400 `{"error": "Can only archive completed or cancelled state group issue"}`; 404 | `issue_activity("issue.activity.updated", requested_data={"archived_at": date, "automation": false}, current_instance=IssueSerializer)`; `archived_at = heute (Datum)` |
| A4 | DELETE | `{P}/issues/{pk}/archive/` | `IssueArchiveViewSet.unarchive` | `AP[A,M]` | – | – | 204; 404 | `issue_activity("issue.activity.updated", requested_data={"archived_at": null})`; `archived_at = null` |
| A5 | POST | `{P}/bulk-archive-issues/` | `BulkArchiveIssuesEndpoint.post` | `PEP` + `AP[A,M]` | `issue_ids[]` | – | 200 `{"archived_at": "YYYY-MM-DD"}`; 400 `{"error": "Issue IDs are required"}`; 400 `{"error_code": 4091, "error_message": "INVALID_ARCHIVE_STATE_GROUP"}` | Abbruch beim ersten ungültigen Issue – **zuvor gequeuete Activities bleiben bestehen**, aber nichts wird gespeichert; `bulk_update(["archived_at"])` |
| A6 | DELETE | `{P}/bulk-delete-issues/` | `BulkDeleteIssuesEndpoint.delete` | `AP[A]` | `issue_ids[]` (im DELETE-Body) | – | 200 `{"message": "{n} issues were deleted"}`; 400 `{"error": "Issue IDs are required"}` | Nur `issue_objects`; `CycleIssue`/`ModuleIssue` per QuerySet soft-deleted, dann Issues per QuerySet soft-deleted (**keine** Kaskade für Kommentare/Links/…, **keine** Activity, **keine** Benachrichtigung) |
| A7 | GET | `{P}/deleted-issues/` | `DeletedIssuesListViewSet.get` | `AP[A,M,G]` | – | `updated_at__gt` | 200 Array von UUIDs (archiviert **oder** gelöscht) | Für Client-Cache-Sync (`Issue.all_objects`) |
| A8 | POST | `{P}/issue-dates/` | `IssueBulkUpdateDateEndpoint.post` | `AP[A,M]` | `updates: [{id, start_date?, target_date?}]` (Datum `YYYY-MM-DD`) | – | 200 `{"message": "Issues updated successfully"}`; 400 `{"message": "Start date cannot exceed target date"}` | Unbekannte IDs werden ignoriert; pro gesetztem Feld `issue_activity("issue.activity.updated", notification=False)`; `bulk_update(["start_date","target_date"])` (Model-`save` umgangen). Leere Werte (`null`) werden **nicht** gesetzt (kein Entfernen möglich) |

### 2.9 Versionen

View: `apps/api/plane/app/views/issue/version.py`.

| # | Methode | Pfad | View.Methode | Berechtigung | Request | Query | Response | Besonderheiten |
|---|---|---|---|---|---|---|---|---|
| V1 | GET | `{P}/issues/{issue_id}/versions/` | `IssueVersionEndpoint.get` | `AP[A,M,G]` | – | `cursor` | 200 `ENV-GLOBAL`; `results`: `id, workspace, project, issue, last_saved_at, owned_by, created_at, updated_at, created_by, updated_by` | Keine Gast-Prüfung; `IssueVersion` wird im CE nur per Management-Command `sync_issue_version` befüllt (`apps/api/plane/bgtasks/issue_version_sync.py`; `issue_task` wird nirgends aufgerufen) |
| V2 | GET | `{P}/issues/{issue_id}/versions/{pk}/` | `IssueVersionEndpoint.get` | `AP[A,M,G]` | – | – | 200 `IssueVersionDetailSerializer` | – |
| V3 | GET | `{P}/work-items/{work_item_id}/description-versions/` | `WorkItemDescriptionVersionEndpoint.get` | `AP[A,M,G]` + Gast-Prüfung (403) | – | `cursor` | 200 `ENV-GLOBAL` (Felder wie V1), sortiert `-created_at` | 404 wenn Issue nicht im Projekt |
| V4 | GET | `{P}/work-items/{work_item_id}/description-versions/{pk}/` | `WorkItemDescriptionVersionEndpoint.get` | wie V3 | – | – | 200 `IssueDescriptionVersionDetailSerializer` (`description_binary` als Base64-String) | – |

### 2.10 Intake

URL: `apps/api/plane/app/urls/intake.py`; View: `apps/api/plane/app/views/intake/base.py`; Serializer: `apps/api/plane/app/serializers/intake.py`. **Alle Pfade existieren doppelt** (`intakes`/`inboxes`, `intake-issues`/`inbox-issues`) mit identischer Logik. Der Pfadparameter `{pk}` bei `intake-issues` ist die **Issue-ID** (nicht die IntakeIssue-ID).

| # | Methode | Pfad (+ Alias) | View.Methode | Berechtigung | Request-Body | Query | Response | Seiteneffekte / Besonderheiten |
|---|---|---|---|---|---|---|---|---|
| N1 | GET | `{P}/intakes/` (`{P}/inboxes/`) | `IntakeViewSet.list` | `AP[A,M]` | – | – | 200 **ein Objekt** (erstes Intake des Projekts) `IntakeSerializer` inkl. `project_detail`, `pending_issue_count` (Anzahl `status=-2`); ohne Intake: Default-Objekt des Serializers | Gäste erhalten 403 |
| N2 | POST | `{P}/intakes/` | Default `create` → dekoriertes `perform_create` | – | `name`, `description`, `is_default`, `view_props`, `logo_props` | – | **Fehlerhaft**: `allow_permission` auf `perform_create(serializer)` interpretiert den Serializer als Request → Exception (400/500) | Intakes werden beim Setzen von `intake_view` in `ProjectViewSet.partial_update` angelegt (`name="{project.name} Intake"`, `is_default=True`; `apps/api/plane/app/views/project/base.py`) |
| N3 | GET | `{P}/intakes/{pk}/` | Default `retrieve` | `AUTH` (!) | – | – | 200 `IntakeSerializer` | Queryset nur Workspace+Projekt-Filter |
| N4 | PATCH | `{P}/intakes/{pk}/` | Default `partial_update` | `AUTH` (!) | Intake-Felder | – | 200 | Sicherheitslücke (5.4) |
| N5 | DELETE | `{P}/intakes/{pk}/` | `IntakeViewSet.destroy` | `AP[A,M]` | – | – | 204; 400 `{"error": "You cannot delete the default intake"}` | Soft-Delete + Kaskade; `None`-Intake → 500 |
| N6 | GET | `{P}/intake-issues/` (`{P}/inbox-issues/`) | `IntakeIssueViewSet.list` | `AP[A,M,G]` + Gast-Filter (`created_by`) | – | `status` (CSV von Ints, Default `-2`; `null` wird ignoriert), `order_by` (Allowlist `INTAKE_ISSUE_ORDER_BY_ALLOWLIST`, Default `-issue__created_at`), Legacy-Filter mit Präfix `issue__` (z. B. `priority`, `labels`, `assignees`, `created_by`, `state`, …), `cursor`, `per_page` | 200 `ENV-PAGINATED` mit `IntakeIssueSerializer`: `id, status, duplicate_to, snoozed_till, source, created_by, issue{id, name, priority, sequence_id, project_id, created_at, label_ids, created_by}` | 404 `{"error": "Intake not found"}` |
| N7 | POST | `{P}/intake-issues/` | `IntakeIssueViewSet.create` | `AP[A,M,G]` | `{"issue": {"name" (Pflicht), "priority" ∈ {low, medium, high, urgent, none}, "description_html", "description_json", "description_binary", "label_ids", "assignee_ids", "start_date", "target_date", "parent_id", "estimate_point", …}}` | – | **200** `IntakeIssueDetailSerializer` (`id, status, duplicate_to, snoozed_till, duplicate_issue_detail, source, issue{S-ISSUE-DETAIL-Teilmenge + assignee_ids, label_ids}`); 400 `{"error": "Name is required"}` / `{"error": "Invalid priority"}` | Triage-State des Projekts wird gesucht oder erzeugt (`name="Triage"`, `group="triage"`, `color="#4E5355"`, `sequence=65000`, `default=False`); Issue mit `state_id=Triage` (`allow_triage_state=True`); `IntakeIssue(status=-2, source="IN_APP")`; `issue_activity("issue.activity.created", requested_data=gesamter Body, notification=True, intake=intake_issue_id)`; `issue_description_version_task(is_creating=True)` |
| N8 | GET | `{P}/intake-issues/{pk}/` | `IntakeIssueViewSet.retrieve` | `AP[A,M,G]+C(Issue)` + Gast-Prüfung (`intake_issue.created_by`), 403 `{"error": "You are not allowed to view this issue"}` | – | `expand` (Client sendet `expand=issue_inbox`, ohne Wirkung) | 200 `IntakeIssueDetailSerializer` | 404 |
| N9 | PATCH | `{P}/intake-issues/{pk}/` | `IntakeIssueViewSet.partial_update` | `AP[A]+C(Issue)`; intern: Projektmitglied **oder** Workspace-Admin (sonst 403 `{"error": "Only admin or creator can update the intake work items"}`); Gast/Nicht-Ersteller → 400 `{"error": "You cannot edit intake issues"}` | `issue` (Objekt, optional), `status`, `duplicate_to`, `snoozed_till`, `source`, `skip_activity` | – | 200 `IntakeIssueDetailSerializer` | Details 3.14: Gäste dürfen nur `name`/`description_html`/`description_json`; Status-Felder nur Projekt-Admin (Rolle 20) oder Workspace-Admin; Annahme (`status=1`) setzt State von Triage auf Default-State (400 `{"status": "Cannot accept intake issue: No default state found for the project"}`); `snoozed_till` wird auf 00:00 Projekt-TZ normalisiert; Activities `issue.activity.updated` (Issue-Felder) und `intake.activity.created` (Status, `notification=False`) |
| N10 | DELETE | `{P}/intake-issues/{pk}/` | `IntakeIssueViewSet.destroy` | `AP[A]+C(Issue)` | – | – | 204 | Bei Status ∈ {-2, -1, 0, 2} wird auch das **Issue** soft-gelöscht; bei `1` (accepted) nur der IntakeIssue-Eintrag |
| N11 | GET | `{P}/intake-work-items/{work_item_id}/description-versions/` | `IntakeWorkItemDescriptionVersionEndpoint.get` | `AP[A,M,G]` + Gast-Prüfung | – | `cursor` | 200 `ENV-GLOBAL` | **Ohne** explizite Sortierung (Model hat kein `ordering`) – Reihenfolge undefiniert |
| N12 | GET | `{P}/intake-work-items/{work_item_id}/description-versions/{pk}/` | wie N11 | wie N11 | – | – | 200 `IssueDescriptionVersionDetailSerializer` | – |

### 2.11 Cycles

URL: `apps/api/plane/app/urls/cycle.py`; Views: `apps/api/plane/app/views/cycle/{base,issue,archive}.py`; Transfer: `apps/api/plane/utils/cycle_transfer_issues.py`; Burndown: `apps/api/plane/utils/analytics_plot.py`.

| # | Methode | Pfad | View.Methode | Berechtigung | Request-Body | Query | Response | Seiteneffekte / Besonderheiten |
|---|---|---|---|---|---|---|---|---|
| Y1 | GET | `{P}/cycles/` | `CycleViewSet.list` | `AP[A,M,G]` | – | `cycle_view` ∈ {`all` (Default), `current`} | 200 Array (`S-CYCLE-LIST`, 2.17): `id, workspace_id, project_id, name, description, start_date, end_date, owned_by_id, view_props, sort_order, external_source, external_id, progress_snapshot, logo_props, is_favorite, total_issues, cancelled_issues, completed_issues, assignee_ids, status, version, created_by`; `start_date`/`end_date` in **Projekt-TZ** | Nur nicht archivierte; Sortierung `-is_favorite, -created_at`; bei `current` ohne Treffer fällt die Antwort auf die **komplette** Liste zurück |
| Y2 | POST | `{P}/cycles/` | `CycleViewSet.create` | `AP[A,M]` | `name` (Pflicht), `description`, `start_date`, `end_date` (beide oder keines), `view_props`, `sort_order`, `logo_props`, `external_source`, `external_id`, `timezone`, `version`, `progress_snapshot` | – | 201 Cycle-Dict (ohne `cancelled_issues`); 400 `{"error": "Both start date and end date are either required or are to be null"}`; 400 `{"non_field_errors": ["Start date cannot exceed end date"]}` | `owned_by = user`; Datumsumrechnung `convert_to_utc` (3.15.2); `sort_order` = min−10000; `model_activity("cycle", created)` |
| Y3 | GET | `{P}/cycles/{pk}/` | `CycleViewSet.retrieve` | `AP[A,M]` (Gäste 403) | – | – | 200 Cycle-Dict + `sub_issues` (Anzahl Sub-Issues im Cycle); 404 `{"error": "Cycle not found"}` | Archivierte → 404; `recent_visited_task(cycle)` |
| Y4 | PUT | `{P}/cycles/{pk}/` | Default `update` | `AUTH` + Queryset (aktives Projektmitglied, inkl. Gäste) | `CycleWriteSerializer` | – | 200 | ohne Abschluss-/Archiv-Prüfung, ohne Webhook (5.4) |
| Y5 | PATCH | `{P}/cycles/{pk}/` | `CycleViewSet.partial_update` | `AP[A,M]` | partielle Cycle-Felder | – | 200 Cycle-Dict; 400 `{"error": "Archived cycle cannot be updated"}`; 400 `{"error": "The Cycle has already been completed so it cannot be edited"}` | Abgeschlossene Cycles (`end_date < now`) nur editierbar, wenn `sort_order` im Body enthalten ist – **dann werden trotzdem alle übergebenen Felder gespeichert** (Bug: `request.data` statt `request_data`); `model_activity("cycle", updated)` |
| Y6 | DELETE | `{P}/cycles/{pk}/` | `CycleViewSet.destroy` | `AP[A]+C(Cycle)` | – | – | 204 | `issue_activity("cycle.activity.deleted", requested_data={"cycle_id","cycle_name","issues":[…]}, issue_id=<Cycle-ID>!)`; Soft-Delete + Kaskade (CycleIssue); **eigener** Favorit gelöscht (andere Nutzer behalten Favoriten); `UserRecentVisit` hart gelöscht |
| Y7 | GET | `{P}/cycles/{cycle_id}/cycle-issues/` | `CycleIssueViewSet.list` (gzip) | `AP[A,M]` | – | wie I2 | wie I2 | Basis `issue_objects` mit `issue_cycle__cycle_id`. Client nutzt dies nur für „Active Cycle“-Kachel (`priority=urgent,high`); reguläre Cycle-Ansicht nutzt I2 mit `?cycle=<id>`. `group_by` ∈ {`target_date`,`start_date`,`created_by`} → 500 |
| Y8 | POST | `{P}/cycles/{cycle_id}/cycle-issues/` | `CycleIssueViewSet.create` | `AP[A,M]` | `issues[]` (Pflicht) | – | 201 `{"message": "success"}`; 400 `{"error": "Issues are required"}`; 400 `{"error": "The Cycle has already been completed so no new issues can be added"}` | Ein Issue gehört zu **höchstens einem** Cycle: bestehende `CycleIssue` anderer Cycles werden auf diesen Cycle umgehängt, neue angelegt; `issue_activity("cycle.activity.created", requested_data={"cycles_list": issues}, current_instance={"updated_cycle_issues": [...], "created_cycle_issues": <Django-Serializer-JSON>}, issue_id=None)` |
| Y9 | GET/PUT/PATCH | `{P}/cycles/{cycle_id}/cycle-issues/{issue_id}/` | Default | – | – | – | **500** (DRF erwartet `pk`) | tote Routen |
| Y10 | DELETE | `{P}/cycles/{cycle_id}/cycle-issues/{issue_id}/` | `CycleIssueViewSet.destroy` | `AP[A,M]` | – | – | 204 | `issue_activity("cycle.activity.deleted", requested_data={"cycle_id","issues":[issue_id]})`; QuerySet-Soft-Delete |
| Y11 | POST | `{P}/cycles/date-check/` | `CycleDateCheckEndpoint.post` | `AP[A,M]` | `start_date`, `end_date` (Pflicht), `cycle_id` (optional, ausgeschlossen) | – | 200 `{"status": true}` **oder** 200 `{"error": "You have a cycle already on the given dates, if you want to create a draft cycle you can do that by removing dates", "status": false}`; 400 `{"error": "Start date and end date both are required"}` | Überlappungsprüfung nach UTC-Umrechnung (3.15.3); berücksichtigt auch archivierte Cycles |
| Y12 | GET | `{P}/user-favorite-cycles/` | Default `list` | `AUTH` | – | – | **500** (`select_related("cycle")` auf `UserFavorite` ungültig, kein `serializer_class`) | tote Route; Favoriten-Liste kommt aus Workspace-Favoriten (anderer Bereich) |
| Y13 | POST | `{P}/user-favorite-cycles/` | `CycleFavoriteViewSet.create` | `AP[A,M]` | `cycle` (UUID) | – | 204; 404 wenn Cycle nicht sichtbar | `UserFavorite(entity_type="cycle")`; Duplikat → 400 `{"error": "The payload is not valid"}` |
| Y14 | DELETE | `{P}/user-favorite-cycles/{cycle_id}/` | `CycleFavoriteViewSet.destroy` | `AP[A,M]` | – | – | 204; 404 | **harter** Delete |
| Y15 | POST | `{P}/cycles/{cycle_id}/transfer-issues/` | `TransferCycleIssueEndpoint.post` | `AP[A,M]` | `new_cycle_id` (Pflicht) | – | 200 `{"message": "Success"}`; 400 `{"error": "New Cycle Id is required"}` / `{"error": "The cycle where the issues are transferred is already completed"}` / `{"error": "Source cycle not found"}` | Snapshot + Umhängen unvollständiger Issues, Details 3.15.5 |
| Y16 | GET | `{P}/cycles/{cycle_id}/user-properties/` | `CycleUserPropertiesEndpoint.get` | `AP[A,M,G]` | – | – | 200 `CycleUserPropertiesSerializer` (`filters, display_filters, display_properties, rich_filters` + Audit/IDs) | `get_or_create` |
| Y17 | PATCH | `{P}/cycles/{cycle_id}/user-properties/` | `CycleUserPropertiesEndpoint.patch` | `AP[A,M,G]` | `filters`, `rich_filters`, `display_filters`, `display_properties` (jeweils komplett ersetzt) | – | **201** Serializer; 404 wenn noch nicht per GET angelegt | – |
| Y18 | POST | `{P}/cycles/{cycle_id}/archive/` | `CycleArchiveUnarchiveEndpoint.post` | `AP[A,M]` | – | – | 200 `{"archived_at": "<ISO-Datetime>"}`; 400 `{"error": "Only completed cycles can be archived"}` | Nur wenn `end_date < now`; Favoriten **aller** Nutzer für den Cycle gelöscht (Soft) |
| Y19 | DELETE | `{P}/cycles/{cycle_id}/archive/` | `CycleArchiveUnarchiveEndpoint.delete` | `AP[A,M]` | – | – | 204 | `archived_at = null` |
| Y20 | GET | `{P}/archived-cycles/` | `CycleArchiveUnarchiveEndpoint.get` (`pk=None`) | `AP[A,M]` | – | – | 200 Array: Cycle-Felder (ohne `logo_props`, `version`, `created_by`) + `total_issues, is_favorite, cancelled_issues, completed_issues, started_issues, unstarted_issues, backlog_issues, assignee_ids, status, archived_at` | Sortierung `-is_favorite, -created_at`; Datumsfelder **nicht** in Projekt-TZ umgerechnet |
| Y21 | GET | `{P}/archived-cycles/{pk}/` | `CycleArchiveUnarchiveEndpoint.get` | `AP[A,M]` | – | – | 200 Detail inkl. `sub_issues`, `completed_estimate_points`, `total_estimate_points`, `distribution{assignees, labels, completion_chart}`, `estimate_distribution{assignees, labels, completion_chart}` | Nicht archivierter Cycle → 500 (`data` ist `None`) |
| Y22 | GET | `{P}/cycles/{cycle_id}/progress/` | `CycleProgressEndpoint.get` | `AP[A,M,G]` | – | – | 200 `{backlog_estimate_points, unstarted_estimate_points, started_estimate_points, cancelled_estimate_points, completed_estimate_points, total_estimate_points, backlog_issues, total_issues, completed_issues, cancelled_issues, started_issues, unstarted_issues}`; 404 `{"error": "Cycle not found"}` | Issue-Zahlen aus `progress_snapshot`, wenn vorhanden, sonst live; Schätzpunkte immer live (nur Schätzungen vom Typ `points`) |
| Y23 | GET | `{P}/cycles/{cycle_id}/analytics/` | `CycleAnalyticsEndpoint.get` | `AP[A,M,G]` | – | `type` ∈ {`issues` (Default), `points`} | 200 `{"assignees": [...], "labels": [...], "completion_chart": {"YYYY-MM-DD": number\|null}}`; 400 `{"error": "Cycle has no start or end date"}` | Mit `progress_snapshot` → Werte aus `distribution` (unabhängig von `type`!). Details 3.15.6 |
| Y24 | POST/DELETE | `{P}/archived-cycles/{pk}/` | `CycleArchiveUnarchiveEndpoint.post/delete` | – | – | – | **500** (Signatur erwartet `cycle_id`) | tote Kombination; ebenso GET auf `{P}/cycles/{cycle_id}/archive/` → 500 |

### 2.12 Modules

URL: `apps/api/plane/app/urls/module.py`; Views: `apps/api/plane/app/views/module/{base,issue,archive}.py`; Serializer: `apps/api/plane/app/serializers/module.py`.

| # | Methode | Pfad | View.Methode | Berechtigung | Request-Body | Query | Response | Seiteneffekte / Besonderheiten |
|---|---|---|---|---|---|---|---|---|
| M1 | GET | `{P}/modules/` | `ModuleViewSet.list` | `AP[A,M,G]` | – | `fields` (wenn gesetzt → `ModuleSerializer` komplett, Feldfilter wirkt nicht) | 200 Array `S-MODULE-LIST`: `id, workspace_id, project_id, name, description, description_text, description_html, start_date, target_date, status, lead_id, member_ids, view_props, sort_order, external_source, external_id, logo_props, completed_estimate_points, total_estimate_points, total_issues, is_favorite, cancelled_issues, completed_issues, started_issues, unstarted_issues, backlog_issues, created_at, updated_at` (`created_at`/`updated_at` in Nutzer-TZ) | Nur nicht archivierte; Sortierung `-is_favorite, -created_at` |
| M2 | POST | `{P}/modules/` | `ModuleViewSet.create` | `AP[A,M]` | `name` (Pflicht, eindeutig im Projekt), `description`, `description_text`, `description_html`, `start_date`, `target_date`, `status` ∈ {`backlog`, `planned` (Default), `in-progress`, `paused`, `completed`, `cancelled`}, `lead_id`, `member_ids[]`, `view_props`, `sort_order`, `logo_props`, `external_source`, `external_id` | – | 201 Module-Dict (gleiche Feldmenge wie M1); 400 `{"error": "Module with this name already exists"}`; 400 `{"non_field_errors": ["Start date cannot exceed target date"]}` | `sort_order` = min−10000; `ModuleMember` bulk; `model_activity("module", created)` |
| M3 | GET | `{P}/modules/{pk}/` | `ModuleViewSet.retrieve` | `AP[A,M]` (Gäste 403) | – | – | 200 `ModuleDetailSerializer` + `link_module`, `sub_issues`, `backlog/unstarted/started/cancelled_estimate_points` + `distribution{assignees, labels, completion_chart}` + `estimate_distribution{assignees, labels, completion_chart?}`; 404 `{"error": "Module not found"}` | `completion_chart` nur wenn `start_date`, `target_date` und `total_issues > 0`; `recent_visited_task(module)` |
| M4 | PUT | `{P}/modules/{pk}/` | Default `update` | `AUTH` (!) – Queryset ohne Mitgliedschaftsfilter | `ModuleWriteSerializer` | – | 200 | Sicherheitslücke (5.4) |
| M5 | PATCH | `{P}/modules/{pk}/` | `ModuleViewSet.partial_update` | `AP[A,M]` | partielle Felder | – | 200 Module-Dict; 404 `{"error": "Module not found"}`; 400 `{"error": "Archived module cannot be updated"}` | `member_ids` ersetzt alle `ModuleMember`; `model_activity("module", updated)` |
| M6 | DELETE | `{P}/modules/{pk}/` | `ModuleViewSet.destroy` | `AP[A]+C(Module)` | – | – | 204 | pro Issue `issue_activity("module.activity.deleted", current_instance={"module_name"})`; Module soft-deleted (+ Kaskade), `ModuleIssue` per QuerySet soft-deleted; **eigener** Favorit gelöscht; `UserRecentVisit` hart gelöscht |
| M7 | POST | `{P}/issues/{issue_id}/modules/` | `ModuleIssueViewSet.create_issue_modules` | `AP[A,M]` | `modules[]`, `removed_modules[]` | – | 201 `{"message": "success"}` | Hinzufügen nur für Module im Projekt (`bulk_create(ignore_conflicts)`), pro Modul `issue_activity("module.activity.created", requested_data={"module_id"})`; Entfernen pro ID `issue_activity("module.activity.deleted")` + QuerySet-Soft-Delete (auch wenn keine Zuordnung existiert) |
| M8 | GET | `{P}/modules/{module_id}/issues/` | `ModuleIssueViewSet.list` (gzip) | `AP[A,M]` | – | wie I2; **Default `order_by=created_at` (aufsteigend!)** | wie I2 | Client nutzt i. d. R. I2 mit `?module=<id>` |
| M9 | POST | `{P}/modules/{module_id}/issues/` | `ModuleIssueViewSet.create_module_issues` | `AP[A,M]` | `issues[]` (Pflicht) | – | 201 `{"message": "success"}`; 400 `{"error": "Issues are required"}` | Mehrfachzugehörigkeit erlaubt (Issue ↔ n Module); pro Issue `issue_activity("module.activity.created")` |
| M10 | GET/PUT/PATCH | `{P}/modules/{module_id}/issues/{issue_id}/` | Default | – | – | – | 500 (kein `pk`) | tote Routen |
| M11 | DELETE | `{P}/modules/{module_id}/issues/{issue_id}/` | `ModuleIssueViewSet.destroy` | `AP[A,M]` | – | – | 204 (idempotent) | `issue_activity("module.activity.deleted", current_instance={"module_name"})` |
| M12 | GET | `{P}/modules/{module_id}/module-links/` | Default `list` | `PEP` | – | – | 200 Array `ModuleLinkSerializer` | – |
| M13 | POST | `{P}/modules/{module_id}/module-links/` | Default `create` + `perform_create` | `PEP` (A/M) | `url` (Pflicht), `title`, `metadata` | – | 201 | `http://`-Präfix; `URLValidator`; Duplikat → 400 `{"error": "URL already exists."}`; 404 wenn Modul nicht im Projekt; **keine** Activity, **kein** Crawl |
| M14 | GET/PUT/PATCH/DELETE | `{P}/modules/{module_id}/module-links/{pk}/` | Default | `PEP` | Link-Felder | – | 200/204 | Update-Duplikat → 400 `{"error": "URL already exists for this Issue"}`; PATCH ohne `url` → `validate_url(None)` in `update()` → 400 `{"error": "Invalid URL format."}` (URL muss bei jedem Update mitgesendet werden) |
| M15 | GET | `{P}/user-favorite-modules/` | Default `list` | `PLP` | – | – | 500 (`select_related("module")` ungültig) | tote Route |
| M16 | POST | `{P}/user-favorite-modules/` | `ModuleFavoriteViewSet.create` | `PLP` (auch Gäste) | `module` (UUID) | – | 204; 404 | – |
| M17 | DELETE | `{P}/user-favorite-modules/{module_id}/` | `ModuleFavoriteViewSet.destroy` | `PLP` | – | – | 204; 404 | harter Delete |
| M18 | GET | `{P}/modules/{module_id}/user-properties/` | `ModuleUserPropertiesEndpoint.get` | `AP[A,M,G]` | – | – | 200 | `get_or_create` |
| M19 | PATCH | `{P}/modules/{module_id}/user-properties/` | `ModuleUserPropertiesEndpoint.patch` | `AP[A,M,G]` | `filters`, `rich_filters`, `display_filters`, `display_properties` | – | **201** | wie Y17 |
| M20 | POST | `{P}/modules/{module_id}/archive/` | `ModuleArchiveUnarchiveEndpoint.post` | `PEP` (A/M) | – | – | 200 `{"archived_at": "<ISO>"}`; 400 `{"error": "Only completed or cancelled modules can be archived"}` | Bedingung: `module.status ∈ {completed, cancelled}` (nicht Datum!); Favoriten aller Nutzer gelöscht |
| M21 | DELETE | `{P}/modules/{module_id}/archive/` | `ModuleArchiveUnarchiveEndpoint.delete` | `PEP` (A/M) | – | – | 204 | – |
| M22 | GET | `{P}/archived-modules/` | `ModuleArchiveUnarchiveEndpoint.get` | `PEP` (alle Rollen) | – | – | 200 Array (Felder wie M1 ohne `logo_props`, Schätzpunkte; plus `archived_at`) | Datumsfelder in Nutzer-TZ |
| M23 | GET | `{P}/archived-modules/{pk}/` | `ModuleArchiveUnarchiveEndpoint.get` | `PEP` | – | – | 200 wie M3 | **Ohne** `total_issues > 0`-Bedingung für `completion_chart`; Label-Schätzverteilung **ohne** `issue_module__deleted_at`-Filter |

### 2.13 Views (gespeicherte Ansichten)

URL: `apps/api/plane/app/urls/views.py`; View: `apps/api/plane/app/views/view/base.py`; Serializer: `apps/api/plane/app/serializers/view.py`.

| # | Methode | Pfad | View.Methode | Berechtigung | Request-Body | Query | Response | Seiteneffekte / Besonderheiten |
|---|---|---|---|---|---|---|---|---|
| W1 | GET | `{P}/views/` | `IssueViewViewSet.list` | `AP[A,M,G]` + Gast-Filter (`owned_by`) | – | `fields` (wirkungslos, s. 2.16) | 200 Array `IssueViewSerializer` (alle Felder + `is_favorite`) | Sichtbar: eigene **oder** `access=1` (public); Sortierung `-is_favorite, name` |
| W2 | POST | `{P}/views/` | Default `create` + `perform_create` | `AUTH` (!) | `name` (Pflicht), `description`, `filters`, `display_filters`, `display_properties`, `rich_filters`, `sort_order`, `logo_props`, `archived_at` (read-only: `workspace, project, query, owned_by, access, is_locked`) | – | 201 `IssueViewSerializer` | `owned_by=user`; `query` aus `filters` per `issue_filters(..., "POST")`; `sort_order` = max+10000 |
| W3 | GET | `{P}/views/{pk}/` | `IssueViewViewSet.retrieve` | `AP[A,M,G]` + Gast-Prüfung (403 `{"error": "You are not allowed to view this issue"}`) | – | – | 200 `IssueViewSerializer` | `recent_visited_task(view)`; nicht gefunden → leeres Serializer-Objekt (Nicht-Gast) bzw. 500 (Gast) |
| W4 | PUT | `{P}/views/{pk}/` | Default `update` | `AUTH` + Queryset | – | – | 200 | umgeht Lock- und Owner-Prüfung (5.4) |
| W5 | PATCH | `{P}/views/{pk}/` | `IssueViewViewSet.partial_update` | `AP[]+C(IssueView)` (nur Ersteller) | partielle Felder | – | 200; 400 `{"error": "view is locked"}`; 400 `{"error": "Only the owner of the view can update the view"}` | `SELECT … FOR UPDATE` in Transaktion; `query` wird neu berechnet |
| W6 | DELETE | `{P}/views/{pk}/` | `IssueViewViewSet.destroy` | `AP[A]+C(IssueView)`; intern Projekt-Admin oder Owner (sonst 400 `{"error": "Only admin or owner can delete the view"}`) | – | – | 204 | Favoriten **aller** Nutzer und RecentVisits gelöscht |
| W7 | GET | `{W}/views/` | `WorkspaceViewViewSet.list` | `APW[A,M,G]`; Workspace-Gast nur eigene | – | `order_by` (Allowlist `created_at`, `updated_at`, `name`), `fields` | 200 Array `IssueViewSerializer` | Nur `project IS NULL`; eigene oder public |
| W8 | POST | `{W}/views/` | Default `create` + `perform_create` | `AUTH` (!) | wie W2 | – | 201 | `workspace_id` aus Slug, `owned_by=user` |
| W9 | GET | `{W}/views/{pk}/` | `WorkspaceViewViewSet.retrieve` | `AUTH` (!) | – | – | 200 | `recent_visited_task(view, project_id=None)` |
| W10 | PUT | `{W}/views/{pk}/` | Default `update` | `AUTH` (!) | – | – | 200 | 5.4 |
| W11 | PATCH | `{W}/views/{pk}/` | `WorkspaceViewViewSet.partial_update` | `AP[]+C(IssueView)` auf Workspace-Ebene | partielle Felder | – | 200; 400 locked/owner (wie W5) | – |
| W12 | DELETE | `{W}/views/{pk}/` | `WorkspaceViewViewSet.destroy` | `APW[A]+C(IssueView)`; intern Workspace-Admin oder Owner | – | – | 204; 400 `{"error": "Only admin or owner can delete the view"}` | Favoriten (`project IS NULL`) gelöscht |
| W13 | GET | `{W}/issues/` | `WorkspaceViewIssuesViewSet.list` (gzip) | `APW[A,M,G]`; pro Projekt Rollenfilter (Gast ohne `guest_view_all_features` nur eigene) | – | `filters`, Legacy-Filter, `order_by`, `cursor`, `per_page` (**kein** `group_by`) | 200 `ENV-PAGINATED`, `results` = `ViewIssueListSerializer` (wie `S-ISSUE-LIST` inkl. `state__group`) | Für Workspace-Views/„All work items“ |
| W14 | GET | `{P}/user-favorite-views/` | Default `list` | `AUTH` | – | – | 500 (`select_related("view")`) | tote Route |
| W15 | POST | `{P}/user-favorite-views/` | `IssueViewFavoriteViewSet.create` | `AP[A,M]` | `view` (UUID) | – | 204; 404 | Sichtbarkeit via `get_favorite_entities("view")` |
| W16 | DELETE | `{P}/user-favorite-views/{view_id}/` | `IssueViewFavoriteViewSet.destroy` | `AP[A,M]` | – | – | 204 | harter Delete |

### 2.14 Pages

URL: `apps/api/plane/app/urls/page.py`; Views: `apps/api/plane/app/views/page/{base,version}.py`; Serializer: `apps/api/plane/app/serializers/page.py`; Permission: `apps/api/plane/app/permissions/page.py`. `access`: `0 = public`, `1 = private` (`Page.PUBLIC_ACCESS`/`PRIVATE_ACCESS`).

| # | Methode | Pfad | View.Methode | Berechtigung | Request-Body | Query | Response | Seiteneffekte / Besonderheiten |
|---|---|---|---|---|---|---|---|---|
| G1 | GET | `{P}/pages-summary/` | `PageViewSet.summary` | `PPP` | – | – | 200 `{"public_pages": n, "private_pages": n, "archived_pages": n}` | nur Root-Pages (`parent IS NULL`), eigene oder public; Gast-Filter |
| G2 | GET | `{P}/pages/` | `PageViewSet.list` | `PPP` + Gast-Filter (`owned_by`) | – | `search` (Name, `icontains` über `SearchFilter`), `order_by` (Allowlist `created_at`, `updated_at`, `name`, `sort_order`; Default `-created_at`) | 200 Array `PageSerializer` (**ohne** `description_html`) inkl. archivierter Pages | Nur Root-Pages; eigene oder public; Sortierung `-is_favorite, <order_by>, id` |
| G3 | POST | `{P}/pages/` | `PageViewSet.create` | `PPP` (POST: A/M) | `name`, `access`, `color`, `labels[]` (Label-IDs), `parent`, `view_props`, `logo_props`, `is_locked`, `archived_at`, `description_html` (Default `<p></p>`), `description_json`, `description_binary` | – | 201 `PageDetailSerializer` | `owned_by=user`; `ProjectPage`-Verknüpfung; `PageLabel`s; `page_transaction(new=description_html, old=None)` |
| G4 | GET | `{P}/pages/{page_id}/` | `PageViewSet.retrieve` | `PPP` | – | `track_visit` (Default `true`) | 200 `PageDetailSerializer` + `issue_ids` (aus `PageLog` mit `entity_name="issue"`); 404 `{"error": "Page not found"}` | Nur Root-Pages auffindbar (Kind-Pages → 404); `recent_visited_task(page)` falls `track_visit` |
| G5 | PATCH | `{P}/pages/{page_id}/` | `PageViewSet.partial_update` | `PPP` (A/M oder Owner) | `PageDetailSerializer`-Felder (inkl. `description_html`, `name`, `access`, `parent`, `labels`, `logo_props`, `view_props`, `color`, `is_locked`, `archived_at`) | – | 200 `PageDetailSerializer`; 400 `{"error": "Page is locked"}`; 400 `{"error": "Access cannot be updated since this page is owned by someone else"}` (auch bei **jedem** `Page.DoesNotExist`, z. B. ungültiger `parent`) | `page_transaction` falls `description_html` gesetzt. Wird auch vom Live-Server für Titel-Sync genutzt (`apps/live/src/services/page/core.service.ts`) |
| G6 | DELETE | `{P}/pages/{page_id}/` | `PageViewSet.destroy` | `PPP` (DELETE: A oder Owner) | – | – | 204; 400 `{"error": "The page should be archived before deleting"}`; 403 `{"error": "Only admin or owner can delete the page"}` | Kinder: `parent=None`; Soft-Delete; Favoriten aller Nutzer; RecentVisits hart |
| G7 | POST | `{P}/favorite-pages/{page_id}/` | `PageFavoriteViewSet.create` | `AP[A,M]` | – | – | 204; 404 | `UserFavorite(entity_type="page")` |
| G8 | DELETE | `{P}/favorite-pages/{page_id}/` | `PageFavoriteViewSet.destroy` | `AP[A,M]` | – | – | 204; 404 | harter Delete |
| G9 | POST | `{P}/pages/{page_id}/archive/` | `PageViewSet.archive` | `PPP` (POST: A/M oder Owner) + intern: Mitglied/Gast (Rolle ≤ 15) nur als Owner (sonst 400 `{"error": "Only the owner or admin can archive the page"}`) | – | – | 200 `{"archived_at": "<naive lokale Server-Zeit als String>"}` | Favoriten aller Nutzer gelöscht; **rekursives** Archivieren aller Nachfahren per CTE (3.18.4) |
| G10 | DELETE | `{P}/pages/{page_id}/archive/` | `PageViewSet.unarchive` | `PPP` (DELETE: A oder Owner) + intern wie G9 (`"Only the owner or admin can un archive the page"`) | – | – | 204 | Archivierter Parent → `parent=None`; rekursives Entarchivieren |
| G11 | POST | `{P}/pages/{page_id}/lock/` | `PageViewSet.lock` | `PPP` (A/M oder Owner) | – | – | 204 | `is_locked=True` |
| G12 | DELETE | `{P}/pages/{page_id}/lock/` | `PageViewSet.unlock` | `PPP` (A oder Owner) | – | – | 204 | `is_locked=False` |
| G13 | POST | `{P}/pages/{page_id}/access/` | `PageViewSet.access` | `PPP` (A/M oder Owner) | `access` (0/1, Default 0) | – | 204; 400 `{"error": "Access cannot be updated since this page is owned by someone else"}` | nur Owner darf ändern |
| G14 | GET | `{P}/pages/{page_id}/description/` | `PagesDescriptionViewSet.retrieve` | `PPP` | – | – | 200 `application/octet-stream`, `Content-Disposition: attachment; filename="page_description.bin"`, Body = `description_binary` (Yjs-Update) oder leer | Vom Live-Server (Hocuspocus `onLoadDocument`) und Client genutzt |
| G15 | PATCH | `{P}/pages/{page_id}/description/` | `PagesDescriptionViewSet.partial_update` | `PPP` (A/M oder Owner) | `description_binary` (Base64-String), `description_html`, `description_json` | – | 200 `{"message": "Updated successfully"}`; 400 `{"error_code": 4701, "error_message": "PAGE_LOCKED"}`; 400 `{"error_code": 4702, "error_message": "PAGE_ARCHIVED"}` | Validierung: Base64 + `validate_binary_data` (≤ 10 MB), HTML-Sanitizing (`nh3`); `page_transaction`; `track_page_version` (3.18.6) |
| G16 | GET | `{P}/pages/{page_id}/versions/` | `PageVersionEndpoint.get` | `PPP` | – | – | 200 Array `PageVersionSerializer` (`id, workspace, page, last_saved_at, owned_by, created_at, updated_at, created_by, updated_by`), Model-Ordering `-created_at`, **unpaginiert** | – |
| G17 | GET | `{P}/pages/{page_id}/versions/{pk}/` | `PageVersionEndpoint.get` | `PPP` | – | – | 200 `PageVersionDetailSerializer` (+ `description_binary` Base64, `description_html`, `description_json`) | – |
| G18 | POST | `{P}/pages/{page_id}/duplicate/` | `PageDuplicateEndpoint.post` | `PPP` (A/M oder Owner) | – | – | 201 `PageDetailSerializer` (mit `project_ids`); 403 `{"error": "Permission denied"}` (private fremde Page) | Kopie: `name + " (Copy)"`, `description_binary=None`, `owned_by=user`, alle `ProjectPage`-Verknüpfungen kopiert, Labels **nicht** kopiert; `page_transaction`; `copy_s3_objects_of_description_and_assets` (Bilder duplizieren, Live-Server `/convert-document/` für `description_binary`/`description_json`) |

### 2.15 Draft-Issues (Querverweis)

Draft-Issues liegen technisch im Workspace-Bereich (`apps/api/plane/app/urls/workspace.py`, `apps/api/plane/app/views/workspace/draft.py`, `apps/api/plane/app/serializers/draft.py`; Modell `DraftIssue` u. a. in `apps/api/plane/db/models/draft.py`) und werden ausführlich im Workspace-Analysedokument behandelt. Für dieses Dokument relevant:

| # | Methode | Pfad | View.Methode | Berechtigung | Kurzbeschreibung |
|---|---|---|---|---|---|
| D1 | GET | `{W}/draft-issues/` | `WorkspaceDraftIssueViewSet.list` | `APW[A,M,G]` | Nur eigene Drafts (`created_by=user`), Legacy-Filter, `ENV-PAGINATED` mit `DraftIssueSerializer` |
| D2 | POST | `{W}/draft-issues/` | `create` | `APW[A,M,G]` + `can_write_project` falls `project_id` | Draft anlegen (`DraftIssueCreateSerializer`) |
| D3 | GET | `{W}/draft-issues/{pk}/` | `retrieve` | `APW[A]+C(Issue)` | Nur eigene |
| D4 | PATCH | `{W}/draft-issues/{pk}/` | `partial_update` | `APW[A,M]+C(Issue)` + `can_write_project` | 204 |
| D5 | DELETE | `{W}/draft-issues/{pk}/` | `destroy` | `APW[A]+C(DraftIssue)` | Soft-Delete |
| D6 | POST | `{W}/draft-to-issue/{draft_id}/` | `create_draft_to_issue` | `APW[A,M]` + `can_write_project` | Konvertiert in echtes Issue über `IssueCreateSerializer` (wie I3): `issue.activity.created`, optional `CycleIssue` + `cycle.activity.created`, `ModuleIssue`s + `module.activity.created`; `FileAsset` (draft) → `ISSUE_DESCRIPTION`; Draft wird gelöscht |

Zusätzlich existiert das **Legacy-Flag `Issue.is_draft`** (`apps/api/plane/db/models/issue.py`): `IssueManager` blendet `is_draft=True` aus; `IssueCreateSerializer.get_fields()` macht `is_draft` nach dem Anlegen read-only; `count_filter` der Gruppierung schließt `is_draft=True` aus; Activity-Felder `draft` werden in `history` ausgeblendet.

### 2.16 Serializer-Inventar

Basis: `BaseSerializer` (`id` read-only), `DynamicBaseSerializer` (`expand`-Mechanik) in `apps/api/plane/app/serializers/base.py`. Audit-Felder aller Modelle: `id, created_at, updated_at, deleted_at, created_by, updated_by` (+ `project`, `workspace` bei `ProjectBaseModel`).

> **Wichtig (`fields`-Parameter):** `DynamicBaseSerializer.__init__` verwirft das übergebene `fields`-Argument (`fields = self.expand`). Ein `?fields=`-Parameter **reduziert die Felder nicht**; er schaltet in einigen Views nur den Codepfad um (z. B. I1 → Serializer statt `.values()`, M1 → `ModuleSerializer`). Nur `expand` fügt Felder hinzu.

| Serializer | Datei | Felder (Ausgabe) | Schreibbar / Validierung | Verwendet von |
|---|---|---|---|---|
| `IssueFlatSerializer` | `serializers/issue.py` | `id, name, description_json, description_html, priority, start_date, target_date, sequence_id, sort_order, is_draft` | – | `IssueArchiveViewSet.serializer_class`, `issue_detail` in Activity/Comment |
| `IssueCreateSerializer` | `serializers/issue.py` | alle `Issue`-Felder (`id, created_at, updated_at, deleted_at, created_by, updated_by, project, workspace, parent, state, point, estimate_point, name, description_json, description_html, description_stripped, description_binary, priority, start_date, target_date, sequence_id, sort_order, completed_at, archived_at, is_draft, external_source, external_id, type`) + `state_id`, `parent_id`, `project_id`, `workspace_id`; `to_representation` setzt `assignee_ids`/`label_ids` aus `initial_data` | write-only `label_ids[]`, `assignee_ids[]`; read-only: `workspace, project, created_by, updated_by, created_at, updated_at, completed_at, deleted_at, archived_at, sequence_id` (+ `is_draft` bei Update). Validierung 3.4.1 | I3, I7, I8, N7, N9, D6 |
| `IssueSerializer` | `serializers/issue.py` | `id, name, state_id, sort_order, completed_at, estimate_point, priority, start_date, target_date, sequence_id, project_id, parent_id, cycle_id, module_ids, label_ids, assignee_ids, sub_issues_count, created_at, updated_at, created_by, updated_by, attachment_count, link_count, is_draft, archived_at` (alle read-only; fehlende Annotationen werden ausgelassen) | – | I1 (mit `fields`/`expand`), R5, Activity-`current_instance` bei Archiv |
| `IssueDetailSerializer` | `serializers/issue.py` | `IssueSerializer`-Felder + `description_html, is_subscribed, is_intake` | – | I6, I13, A2, `IntakeIssueDetailSerializer.issue`, `current_instance` bei I8/N9 |
| `IssueListDetailSerializer` | `serializers/issue.py` | `id, name, state_id, sort_order, completed_at, estimate_point (=estimate_point_id), priority, start_date, target_date, sequence_id, project_id, parent_id, created_at, updated_at, created_by, updated_by, is_draft, archived_at, cycle_id, module_ids, label_ids, assignee_ids, sub_issues_count, attachment_count, link_count`; mit `expand`: `issue_relation[]` / `issue_related[]` je `{id, project_id, sequence_id, name, relation_type, state_id, priority, created_by, created_at, updated_at, updated_by}` | – | I4 (`module_ids`/`label_ids`/`assignee_ids` aus Prefetch **ohne** Soft-Delete-/Archiv-Filter) |
| `IssueLiteSerializer` | `serializers/issue.py` | `id, sequence_id, project_id` | – | `expand=parent`, `expand=sub_issues` |
| `IssueIntakeSerializer` | `serializers/issue.py` | `id, name, priority, sequence_id, project_id, created_at, label_ids, created_by` | read-only | `IntakeIssueSerializer.issue`, `duplicate_issue_detail` |
| `IssueStateSerializer` | `serializers/issue.py` | alle Issue-Felder + `label_details, state_detail, project_detail, assignee_details, sub_issues_count, attachment_count, link_count` | – | `CycleIssueSerializer.issue_detail` |
| `IssueActivitySerializer` | `serializers/issue.py` | alle `IssueActivity`-Felder (`id, created_at, updated_at, deleted_at, issue, verb, field, old_value, new_value, comment, attachments, issue_comment, actor, old_identifier, new_identifier, epoch, created_by, updated_by, project, workspace`) + `actor_detail` (UserLite), `issue_detail` (IssueFlat), `project_detail` (ProjectLite), `workspace_detail` (WorkspaceLite), `source_data` (`{source, source_email, extra}` aus erstem `IntakeIssue` oder `null`) | – | C13 |
| `IssueCommentSerializer` | `serializers/issue.py` | alle `IssueComment`-Felder (`id, created_at, updated_at, deleted_at, comment_stripped, comment_json, comment_html, description, attachments, issue, actor, access, external_source, external_id, edited_at, parent, created_by, updated_by, project, workspace`) + `actor_detail, issue_detail, project_detail, workspace_detail, comment_reactions[] (CommentReactionSerializer), is_member` | read-only: `workspace, project, issue, created_by, updated_by, created_at, updated_at`; HTML-Sanitizing `comment_html` | C1–C6, C13 |
| `CommentReactionSerializer` | `serializers/issue.py` | `id, actor, comment, reaction, display_name, deleted_at, workspace, project, created_at, updated_at, created_by, updated_by` | schreibbar: `reaction` | C10–C12 |
| `IssueReactionSerializer` | `serializers/issue.py` | alle `IssueReaction`-Felder (`id, created_at, updated_at, deleted_at, reaction, created_by, updated_by, project, workspace, issue, actor`) + `actor_detail` | read-only: `workspace, project, issue, actor, deleted_at` | C7–C9 |
| `IssueReactionLiteSerializer` | `serializers/issue.py` | `id, actor, issue, reaction, display_name` | – | `expand=issue_reactions` |
| `IssueVoteSerializer` | `serializers/issue.py` | `issue, vote, workspace, project, actor, actor_detail` | – | (Space-Bereich) |
| `LabelSerializer` | `serializers/issue.py` | `parent, name, color, id, project_id, workspace_id, sort_order` | `validate_name`: `name__iexact` eindeutig im Projekt → `LABEL_NAME_ALREADY_EXISTS` | L1–L7, `expand=labels` |
| `LabelLiteSerializer` | `serializers/issue.py` | `id, name, color` | – | `IssueStateSerializer` |
| `IssueRelationSerializer` | `serializers/issue.py` | `id (=related_issue.id), project_id, sequence_id, relation_type, name, state_id, priority, created_by, created_at, updated_at, updated_by` (`assignee_ids` write-only, nie ausgegeben) | – | R2, R3, `expand=issue_relation` |
| `RelatedIssueSerializer` | `serializers/issue.py` | wie oben, aber Quelle `issue.*` | – | R2, `expand=issue_related` |
| `IssueLinkSerializer` | `serializers/issue.py` | alle `IssueLink`-Felder (`id, created_at, updated_at, deleted_at, title, url, issue, metadata, created_by, updated_by, project, workspace`) + `created_by_detail` | read-only: `workspace, project, created_by, updated_by, created_at, updated_at, issue`; URL-Normalisierung/Validierung/Duplikat (3.11) | K1–K6 |
| `IssueLinkLiteSerializer` | `serializers/issue.py` | `id, issue_id, title, url, metadata, created_by_id, created_at` | – | `expand=issue_link` |
| `IssueAttachmentSerializer` | `serializers/issue.py` | alle `FileAsset`-Felder (`id, created_at, updated_at, deleted_at, attributes, asset, user, workspace, draft_issue, project, issue, comment, page, entity_type, entity_identifier, is_deleted, is_archived, external_id, external_source, size, is_uploaded, storage_metadata, created_by, updated_by`) + `asset_url` | read-only: `created_by, updated_by, created_at, updated_at, workspace, project, issue` | K7–K15 |
| `IssueAttachmentLiteSerializer` | `serializers/issue.py` | `id, asset, attributes, created_by, updated_at, updated_by, asset_url` | – | `expand=issue_attachments` |
| `IssueSubscriberSerializer` | `serializers/issue.py` | alle `IssueSubscriber`-Felder (`id, created_at, updated_at, deleted_at, issue, subscriber, created_by, updated_by, project, workspace`) | read-only: `workspace, project, issue` | S2, S5 |
| `IssueVersionDetailSerializer` | `serializers/issue.py` | `id, workspace, project, issue, parent, state, estimate_point, name, priority, start_date, target_date, assignees, sequence_id, labels, sort_order, completed_at, archived_at, is_draft, external_source, external_id, type, cycle, modules, meta, last_saved_at, owned_by, created_at, updated_at, created_by, updated_by` | – | V2 |
| `IssueDescriptionVersionDetailSerializer` | `serializers/issue.py` | `id, workspace, project, issue, description_binary (Base64), description_html, description_stripped, description_json, last_saved_at, owned_by, created_at, updated_at, created_by, updated_by` | – | V4, N12 |
| `ProjectUserPropertySerializer` | `serializers/issue.py` | alle `ProjectUserProperty`-Felder | read-only: `user, workspace, project` | I10, I11 |
| `IntakeSerializer` | `serializers/intake.py` | alle `Intake`-Felder (`id, …, name, description, is_default, view_props, logo_props, project, workspace`) + `project_detail, pending_issue_count` | read-only: `project, workspace` | N1–N5 |
| `IntakeIssueSerializer` | `serializers/intake.py` | `id, status, duplicate_to, snoozed_till, source, issue (IssueIntakeSerializer), created_by` | Validierung `snoozed_till` (00:00 Projekt-TZ), `status=1` erfordert Default-State; `update()` überführt Triage → Default-State | N6, N9 |
| `IntakeIssueDetailSerializer` | `serializers/intake.py` | `id, status, duplicate_to, snoozed_till, duplicate_issue_detail (IssueIntakeSerializer), source, issue (IssueDetailSerializer)` | – | N7–N9 |
| `IntakeIssueLiteSerializer` | `serializers/intake.py` | `id, status, duplicate_to, snoozed_till, source` | – | `expand=issue_intake` |
| `CycleWriteSerializer` | `serializers/cycle.py` | alle `Cycle`-Felder | read-only: `workspace, project, owned_by, archived_at`; Start ≤ Ende; UTC-Umrechnung (3.15.2) | Y2, Y4, Y5 |
| `CycleSerializer` | `serializers/cycle.py` | `id, workspace_id, project_id, name, description, start_date, end_date, owned_by_id, view_props, sort_order, external_source, external_id, progress_snapshot, logo_props, is_favorite, total_issues, cancelled_issues, completed_issues, started_issues, unstarted_issues, backlog_issues, status` | read-only | `current_instance` für Webhooks (Y5) |
| `CycleIssueSerializer` | `serializers/cycle.py` | alle `CycleIssue`-Felder + `issue_detail` (IssueState), `sub_issues_count` | – | `expand=issue_cycle` |
| `CycleUserPropertiesSerializer` | `serializers/cycle.py` | alle Felder | read-only `workspace, project, cycle, user` | Y16, Y17 |
| `ModuleWriteSerializer` | `serializers/module.py` | alle `Module`-Felder + `lead_id`, `member_ids` (Ausgabe als Strings) | write-only `member_ids[]`; Namens-Duplikat → `{"error": "Module with this name already exists"}`; Start ≤ Ziel | M2, M4, M5 |
| `ModuleSerializer` | `serializers/module.py` | `id, workspace_id, project_id, name, description, description_text, description_html, start_date, target_date, status, lead_id, member_ids, view_props, sort_order, external_source, external_id, logo_props, total_estimate_points, completed_estimate_points, is_favorite, total_issues, cancelled_issues, completed_issues, started_issues, unstarted_issues, backlog_issues, created_at, updated_at, archived_at` | read-only | M1 (`fields`), `current_instance` (M5) |
| `ModuleDetailSerializer` | `serializers/module.py` | `ModuleSerializer` + `link_module[] (ModuleLinkSerializer), sub_issues, backlog_estimate_points, unstarted_estimate_points, started_estimate_points, cancelled_estimate_points` | – | M3, M23 |
| `ModuleLinkSerializer` | `serializers/module.py` | alle `ModuleLink`-Felder (`id, …, title, url, module, metadata`) | read-only `workspace, project, created_by, updated_by, created_at, updated_at, module`; URL-Präfix/Validierung/Duplikat | M12–M14 |
| `ModuleIssueSerializer` | `serializers/module.py` | alle `ModuleIssue`-Felder + `module_detail`, `issue_detail`, `sub_issues_count` | – | (Default-Routen, tot) |
| `ModuleUserPropertiesSerializer` | `serializers/module.py` | alle Felder | read-only `workspace, project, module, user` | M18, M19 |
| `IssueViewSerializer` | `serializers/view.py` | alle `IssueView`-Felder (`id, …, name, description, query, filters, display_filters, display_properties, rich_filters, access, sort_order, logo_props, owned_by, is_locked, archived_at, workspace, project`) + `is_favorite` | read-only: `workspace, project, query, owned_by, access, is_locked`; `create/update` berechnen `query` aus `filters` | W1–W12 |
| `ViewIssueListSerializer` | `serializers/view.py` | `S-ISSUE-LIST`-Felder inkl. `state__group`, `estimate_point` (=ID) | – | W13 |
| `PageSerializer` | `serializers/page.py` | `id, name, owned_by, access, color, labels (write-only), parent, is_favorite, is_locked, archived_at, workspace, created_at, updated_at, created_by, updated_by, view_props, logo_props, label_ids, project_ids` | read-only `workspace, owned_by`; `labels` = beliebige Label-PKs (keine Projektprüfung) | G2, G3 |
| `PageDetailSerializer` | `serializers/page.py` | `PageSerializer` + `description_html` | – | G3–G5, G18 |
| `PageBinaryUpdateSerializer` | `serializers/page.py` | – (`description_binary` Base64→Bytes, `description_html` sanitisiert, `description_json`) | Base64-Dekodierung (400 `"Failed to decode base64 data"`), `validate_binary_data`, `validate_html_content` | G15 |
| `PageVersionSerializer` / `PageVersionDetailSerializer` | `serializers/page.py` | siehe G16/G17 | – | G16, G17 |
| `ProjectMemberLiteSerializer` | `serializers/project.py` | `member (UserLite), id, is_subscribed` | – | S1 |
| `UserLiteSerializer` | `serializers/user.py` | `id, first_name, last_name, avatar, avatar_url, is_bot, display_name` | – | `*_detail`, `expand` |
| `StateLiteSerializer` | `serializers/state.py` | `id, name, color, group` | – | `expand=state` |
| `ProjectLiteSerializer` | `serializers/project.py` | `id, identifier, name, cover_image, cover_image_url, logo_props, description` | – | `project_detail`, `expand=project` |
| `WorkspaceLiteSerializer` | `serializers/workspace.py` | `name, slug, id, logo_url` | – | `workspace_detail`, `expand=workspace` |

### 2.17 Antwort-Formen (Shapes)

#### 2.17.1 `S-ISSUE-LIST` (Liste aus `issue_on_results`, `apps/api/plane/utils/grouper.py`)

| Feld | Typ | Herkunft / Bemerkung |
|---|---|---|
| `id` | UUID | – |
| `name` | string | – |
| `state_id` | UUID \| null | – |
| `sort_order` | float | Default 65535 |
| `completed_at` | ISO-Datetime \| null | gesetzt, wenn State-Gruppe `completed` |
| `estimate_point` | UUID \| null | FK-ID auf `EstimatePoint` |
| `priority` | `urgent` \| `high` \| `medium` \| `low` \| `none` | – |
| `start_date`, `target_date` | `YYYY-MM-DD` \| null | – |
| `sequence_id` | int | projektweite laufende Nummer |
| `project_id`, `parent_id`, `created_by`, `updated_by` | UUID \| null | – |
| `cycle_id` | UUID \| null | erste aktive `CycleIssue` (Subquery `LIMIT 1`, Model-Ordering `-created_at`) |
| `sub_issues_count`, `attachment_count`, `link_count` | int **\| null** | Subqueries ohne `Coalesce` → `null` statt 0, wenn keine Treffer (I2, A1, Y7, M8, W13, I4). Nur R4 liefert 0 |
| `created_at`, `updated_at` | ISO-Datetime | in UTC (`Z`) – **keine** Nutzer-TZ-Umrechnung im grouper-Pfad |
| `is_draft` | bool | – |
| `archived_at` | `YYYY-MM-DD` \| null | `DateField` |
| `state__group` | string | Join auf State |
| `assignee_ids`, `label_ids`, `module_ids` | UUID[] | Bei Gruppierung nach M2M-Feld wird das jeweilige Feld durch den Gruppenschlüssel ersetzt (`labels__id` → `label_ids` aus der Seiten-Zuordnung, siehe 3.1.5) |

`S-ISSUE-VALUES` (I1, I3): wie oben **ohne** `state__group`, **mit** `deleted_at`, `created_at`/`updated_at` in Nutzer-TZ (`user_timezone_converter`, ISO mit Offset).

#### 2.17.2 `ENV-PAGINATED` (`BasePaginator.paginate`, `apps/api/plane/utils/paginator.py`)

```json
{
  "grouped_by": "state_id | null",
  "sub_grouped_by": "priority | null",
  "total_count": 123,
  "next_cursor": "50:1:0",
  "prev_cursor": "50:-1:1",
  "next_page_results": true,
  "prev_page_results": false,
  "count": 50,
  "total_pages": 3,
  "total_results": 123,
  "extra_stats": null,
  "results": "<Array | Gruppen-Dict | Untergruppen-Dict>"
}
```

- Ungruppiert: `results` = Array; `total_count = total_results = total_count_queryset.count()`; `count = len(results)`.
- `ENV-GROUPED`: `results = { "<group_key>": { "results": [S-ISSUE-LIST…], "total_results": n }, … }`.
- `ENV-SUBGROUPED`: `results = { "<group_key>": { "results": { "<sub_key>": { "results": [...], "total_results": n } }, "total_results": n }, … }`.
- Gruppenschlüssel sind **Strings**: `str(UUID)`, `"None"` für null, `"YYYY-MM-DD"` für Datum, Prioritäts-/Gruppennamen.
- Bei Gruppierung ist `count` die Anzahl der zurückgegebenen Zeilen (vor Gruppierung, Duplikate bei M2M inkl.), `total_count` = Anzahl Zeilen des fensterannotierten Querysets (bei M2M-Gruppierung = Anzahl (Issue, Gruppenwert)-Paare).

#### 2.17.3 `ENV-GLOBAL` (`apps/api/plane/utils/global_paginator.py`)

```json
{
  "prev_cursor": "1000:-1:0",
  "cursor": "1000:0:0",
  "next_cursor": "1000:1:0 | null",
  "prev_page_results": false,
  "next_page_results": true,
  "page_count": 1000,
  "total_results": 2500,
  "total_pages": 3,
  "results": []
}
```

#### 2.17.4 `S-CYCLE-LIST`, Cycle-Detail, Distribution

| Feld | Bemerkung |
|---|---|
| `status` | `CURRENT` (start ≤ jetzt ≤ end), `UPCOMING` (start > jetzt), `COMPLETED` (end < jetzt), `DRAFT` (sonst / ohne Daten). Vergleich gegen „jetzt“ in UTC (`apps/api/plane/app/views/cycle/base.py`) |
| `total_issues` | Distinct Issues in nicht gelöschten `CycleIssue`, Issue nicht archiviert, kein Draft, nicht gelöscht (**inkl.** Triage-Issues, da direkter Join) |
| `completed_issues`, `cancelled_issues` | wie oben, State-Gruppe `completed` bzw. `cancelled` |
| `assignee_ids` | Distinct Assignees aller Cycle-Issues (aktive Zuordnungen) |
| `is_favorite` | `UserFavorite(entity_type="cycle")` des Nutzers existiert |
| `progress_snapshot` | JSON, gesetzt beim Transfer (3.15.5) |
| `start_date`, `end_date` | Datetime, Ausgabe in **Projekt-Zeitzone** (`user_timezone_converter(data, ["start_date","end_date"], project.timezone)`) |
| `distribution.assignees[]` | `{display_name, assignee_id, avatar_url, total_issues, completed_issues, pending_issues}` (Archiv-Detail zusätzlich `first_name, last_name`) |
| `distribution.labels[]` | `{label_name, color, label_id, total_issues, completed_issues, pending_issues}` |
| `estimate_distribution.assignees[]` / `.labels[]` | analog mit `total_estimates, completed_estimates, pending_estimates` |
| `completion_chart` | `{ "YYYY-MM-DD": verbleibend \| null }` für jeden Tag von Start bis Ende; zukünftige Tage `null` (3.15.7) |
| `avatar_url` | `"/api/assets/v2/static/{avatar_asset}/"` falls `avatar_asset`, sonst `avatar` |

### 2.18 Query-Parameter-Inventar

#### 2.18.1 Legacy-Filter (`issue_filters(query_params, "GET", prefix="")`, `apps/api/plane/utils/issue_filters.py`)

Wird von I1, I2, I4, A1, Y7, M8, W13, N6 (mit Präfix `issue__`) und D1 ausgewertet. Mehrere Parameter werden **AND**-verknüpft. Werte kommagetrennt; das Literal `null` wird ignoriert.

| Parameter | Werte | Erzeugter ORM-Filter | Besonderheiten |
|---|---|---|---|
| `state` | UUID-CSV | `state__in` | ungültige UUIDs verworfen |
| `state_group` | CSV von `backlog, unstarted, started, completed, cancelled` | `state__group__in` | – |
| `estimate_point` | CSV | `estimate_point__in` | – |
| `priority` | CSV | `priority__in` | – |
| `parent` | UUID-CSV, `None` | `None` → `parent__isnull=True`; UUIDs → `parent__in` | beide gleichzeitig = UND (leer) |
| `labels` | UUID-CSV, `None` | `labels__isnull=True` / `labels__in`; **immer** zusätzlich `label_issue__deleted_at__isnull=True` | Join-Duplikate (distinct nötig) |
| `assignees` | UUID-CSV, `None` | `assignees__isnull=True` / `assignees__in`; immer `issue_assignee__deleted_at__isnull=True` | – |
| `mentions` | UUID-CSV | `issue_mention__mention__id__in` | – |
| `created_by` | UUID-CSV, `None` | `created_by__isnull` / `created_by__in` | – |
| `logged_by` | UUID-CSV, `None` | `logged_by__…` | **Feld existiert nicht am Issue → 500** |
| `name` | Text | `name__icontains` | – |
| `created_at`, `updated_at`, `completed_at` | Datumsausdrücke (3.3) | `<feld>__date__gte/__lte/__contains` | `__date` in Nutzer-TZ |
| `start_date`, `target_date` | Datumsausdrücke | `<feld>__gte/__lte/__contains` | Kalender sendet `target_date=<after>;after,<before>;before` |
| `type` | `backlog` \| `active` \| sonst | `state__group__in` = `[backlog]` \| `[unstarted, started]` \| alle 5 | Issues ohne State werden immer ausgeschlossen, sobald `type` übergeben wird |
| `project` | UUID-CSV | `project__in` | – |
| `cycle` | UUID-CSV, `None` | `issue_cycle__cycle_id__isnull` / `issue_cycle__cycle_id__in`; immer `issue_cycle__deleted_at__isnull=True` | Hauptweg der Cycle-Ansicht im Client (`apps/web/store/issue/cycle/filter.store.ts`) |
| `module` | UUID-CSV, `None` | `issue_module__module_id__isnull` / `__in`; immer `issue_module__deleted_at__isnull=True` | Hauptweg der Module-Ansicht |
| `intake_status` | Int-CSV | `issue_intake__status__in` | – |
| `inbox_status` | Int-CSV | `issue_intake__status__in` | Alias |
| `sub_issue` | `true` \| `false` | `false` → `parent__isnull=True` | Client sendet immer (Default `true`) |
| `subscriber` | UUID-CSV | `issue_subscribers__subscriber_id__in` + `issue_subscribers__deleted_at__isnull=True` | – |
| `start_target_date` | `true` | `start_date` und `target_date` nicht null | – |

#### 2.18.2 Rich-Filter (`filters`-Parameter, `ComplexFilterBackend` + `IssueFilterSet`)

Quelle: `apps/api/plane/utils/filters/filter_backend.py`, `apps/api/plane/utils/filters/filterset.py`. Format: JSON-Baum (URL-encodiert im Query-Parameter `filters`). Knoten: `{"and": [..]}`, `{"or": [..]}`, `{"not": {..}}` (case-insensitive) oder Blatt `{"<feld>__<op>": wert, …}` (mehrere Schlüssel im Blatt = AND). Max. Tiefe 5. Werte: Skalar, `null` oder Liste von Skalaren; der Client sendet Listen als CSV-String (`"uuid1,uuid2"`), Bereiche als `"YYYY-MM-DD,YYYY-MM-DD"`.

**Erlaubte Schlüssel** (`IssueFilterSet.base_filters` inkl. automatisch erzeugter `__exact`-Varianten aus `BaseFilterSet.get_filters`):

| Schlüssel | Semantik |
|---|---|
| `assignee_id`, `assignee_id__exact`, `assignee_id__in` | `issue_assignee.assignee_id` (=/in) **und** `issue_assignee.deleted_at IS NULL` |
| `cycle_id`, `cycle_id__exact`, `cycle_id__in` | `issue_cycle.cycle_id` + `deleted_at IS NULL` |
| `module_id`, `module_id__exact`, `module_id__in` | `issue_module.module_id` + `deleted_at IS NULL` |
| `mention_id`, `mention_id__exact`, `mention_id__in` | `issue_mention.mention_id` + `deleted_at IS NULL` |
| `label_id`, `label_id__exact`, `label_id__in` | `label_issue.label_id` + `deleted_at IS NULL` |
| `subscriber_id`, `subscriber_id__exact`, `subscriber_id__in` | `issue_subscribers.subscriber_id` + `deleted_at IS NULL` |
| `created_by_id`, `created_by_id__exact`, `created_by_id__in` | `created_by_id` |
| `state_id`, `state_id__exact`, `state_id__in` | `state_id` |
| `state_group`, `state_group__exact`, `state_group__in` | `state.group` |
| `project_id`, `project_id__exact`, `project_id__in` | `project_id` |
| `priority`, `priority__exact`, `priority__in` | `priority` |
| `is_draft`, `is_draft__exact` | `is_draft` |
| `is_archived`, `is_archived__exact` | `true` → `archived_at IS NOT NULL`, `false` → `archived_at IS NULL` |
| `start_date`, `start_date__exact`, `start_date__range` | `DateField` exakt / Bereich inklusiv |
| `target_date`, `target_date__exact`, `target_date__range` | dto. |
| `created_at`, `created_at__exact`, `created_at__range` | Vergleich der **Datumskomponente** (`created_at__date`, Nutzer-TZ); Range inklusiv ganzer Tage |
| `updated_at`, `updated_at__exact`, `updated_at__range` | dto. |

Fehler (400, Body `{"message", "code"[, "errors"]}`): `invalid_json`, `invalid_filter_type`, `max_depth_exceeded`, `invalid_filter_node`, `empty_filter_object`, `multiple_logical_operators`, `mixed_operator_and_fields`, `invalid_operator_children`, `invalid_operator_child_type`, `invalid_not_child`, `invalid_leaf`, `operator_in_leaf`, `empty_list_value`, `non_scalar_list_item`, `invalid_value_type`, `filtering_not_enabled`, `invalid_filter_field` (`"Filtering on field '<f>' is not allowed"`), `filterset_missing`, `invalid_filterset` (mit `errors`), `missing_build_combined_q`.

Vom Web-Client genutzte Eigenschaften (`WORK_ITEM_FILTER_PROPERTY_KEYS`, `packages/types/src/view-props.ts`): `state_group, priority, start_date, target_date, assignee_id, mention_id, created_by_id, subscriber_id, label_id, state_id, cycle_id, module_id, project_id, created_at, updated_at` mit Operatoren `exact`, `in`, `range` (`packages/types/src/rich-filters/operators/`). Nur `and` wird vom Client erzeugt (`TWorkItemFilterAndGroup`), `or`/`not` unterstützt der Server zusätzlich.

`LegacyToRichFiltersConverter` (`apps/api/plane/utils/filters/converters.py`) wurde nur in Migration `0107_migrate_filters_to_rich_filters` genutzt (Greenfield: nicht portieren).

#### 2.18.3 `order_by` (Allowlists, `apps/api/plane/utils/order_queryset.py`)

`sanitize_order_by`: höchstens ein führendes `-`; unbekannte Werte → Default (still, ohne Fehler).

| Allowlist | Werte | Default | Verwendet in |
|---|---|---|---|
| `ISSUE_ORDER_BY_ALLOWLIST` | `created_at, updated_at, sequence_id, sort_order, target_date, start_date, completed_at, archived_at, priority, state__name, state__group, assignees__first_name, labels__name, issue_module__module__name` (je mit/ohne `-`) | `-created_at` | I1, I2, I4, A1, Y7, M8 (Default `created_at`), W13, R4 |
| `INTAKE_ISSUE_ORDER_BY_ALLOWLIST` | `issue__created_at, issue__updated_at, issue__sequence_id, issue__sort_order, issue__target_date, issue__start_date, issue__priority, issue__state__name, created_at, updated_at, status` | `-issue__created_at` | N6 (direktes `order_by`, `issue__priority` alphabetisch!) |
| `VIEW_ORDER_BY_ALLOWLIST` | `created_at, updated_at, name` | `-created_at` | W7 |
| `PAGE_ORDER_BY_ALLOWLIST` | `created_at, updated_at, name, sort_order` | `-created_at` | G2 |
| `CYCLE_ORDER_BY_ALLOWLIST`, `MODULE_ORDER_BY_ALLOWLIST`, `PROJECT_…`, `NOTIFICATION_…`, `ACTIVITY_…`, `EXPORTER_HISTORY_…` | definiert, in diesem Bereich **nicht** genutzt | – | andere Bereiche |

Vom UI angebotene Sortierungen (`ISSUE_ORDER_BY_OPTIONS`, `packages/constants/src/issue/common.ts`): `sort_order` (manuell), `-created_at`, `-updated_at`, `start_date`, `target_date`, `-priority`.

#### 2.18.4 `group_by` / `sub_group_by`

`ISSUE_GROUP_BY_ALLOWLIST` (`apps/api/plane/utils/order_queryset.py`, geprüft in `BasePaginator.paginate`): `state_id, state__group, priority, labels__id, assignees__id, issue_module__module_id, cycle_id, project_id, created_by, target_date, start_date`.

Client-Mapping (`EIssueGroupByToServerOptions`, `packages/constants/src/issue/common.ts`): `state→state_id`, `priority→priority`, `labels→labels__id`, `state_detail.group→state__group`, `assignees→assignees__id`, `cycle→cycle_id`, `module→issue_module__module_id`, `target_date→target_date`, `project→project_id`, `team_project→project_id`, `created_by→created_by`. Rückweg für „Mehr laden“ in einer Gruppe (`EServerGroupByToFilterOptions`, `packages/constants/src/issue/filter.ts`): `state_id→state`, `priority→priority`, `labels__id→labels`, `state__group→state_group`, `assignees__id→assignees`, `cycle_id→cycle`, `issue_module__module_id→module`, `target_date→target_date`, `project_id→project`, `created_by→created_by` (Legacy-Filter!).

#### 2.18.5 Paginierung, `expand`, sonstige

| Parameter | Bedeutung | Quelle |
|---|---|---|
| `per_page` | Default 1000, Max 1000 (`ParseError "Invalid per_page value. Cannot exceed 1000."`, `"Invalid per_page parameter."`) | `BasePaginator.get_per_page` |
| `cursor` (BasePaginator) | `"<value>:<offset>:<is_prev>"`; `value` int oder float; Default `"{per_page}:0:0"`; ungültig → 400 `{"detail": "Invalid cursor parameter."}`; negatives Offset → 400 `{"detail": "Error in parsing"}` | `Cursor.from_string` |
| `cursor` (Global) | `"<page_size>:<page>:<offset>"`, Default `1000:0:0` | `PaginateCursor` |
| Client-Seitengrößen | Liste: 50 (gruppiert) / 100; Kanban: 30 bzw. 10 (mit Sub-Gruppe); Kalender: 4 (Monat) / 30 (Woche), `group_by=target_date`; Spreadsheet/Gantt: 100; „Mehr laden in Gruppe“: Cursor `"{per_page}:1:0"` + Gruppen-Filter | `apps/web/components/issues/issue-layouts/*/base-*-root.tsx`, `apps/web/store/issue/helpers/issue-filter-helper.store.ts` |
| `expand` (DynamicBaseSerializer) | Schlüssel: `user, workspace, project, default_assignee, project_lead, state, created_by, updated_by, issue, actor, owned_by, members, assignees, labels, issue_cycle, parent, issue_relation, issue_intake, issue_related, issue_reactions, issue_link, sub_issues`; Spezialfall `issue_attachments` (lädt `FileAsset` ISSUE_ATTACHMENT). Many-Felder: `members, assignees, labels, issue_cycle, issue_relation, issue_intake, issue_reactions, issue_link, sub_issues, issue_related` | `apps/api/plane/app/serializers/base.py` |
| `expand` (IssueListDetailSerializer) | `issue_relation`, `issue_related` | `apps/api/plane/app/serializers/issue.py` |
| `layout` | Wird vom Client mitgesendet, **vom Server ignoriert** | `apps/web/store/issue/helpers/issue-filter-helper.store.ts` |
| `show_empty_groups` | reine Client-Anzeigeoption (nicht gesendet) | `packages/constants/src/issue/filter.ts` |
| `updated_at__gt` / `created_at__gt` | Delta-Sync (I2, I5, A7) / History (C13) | – |
| `search` | `SearchFilter` (nur Pages: `name`) | `apps/api/plane/app/views/page/base.py` |

### 2.19 Activity-Typen und Hintergrund-Tasks

`ACTIVITY_MAPPER` in `apps/api/plane/bgtasks/issue_activities_task.py`:

| `type` | Ausgelöst von (dieser Bereich) | `notification` |
|---|---|---|
| `issue.activity.created` | I3, N7, D6 | True |
| `issue.activity.updated` | I8, A3, A4, A5, A8 (False), R5, N9 | True (A8: False) |
| `issue.activity.deleted` | I9 (`subscriber=False`) | True |
| `comment.activity.created` / `.updated` / `.deleted` | C2 / C5 / C6 | True |
| `cycle.activity.created` / `.deleted` | Y8, Y15, D6 / Y6, Y10 | True |
| `module.activity.created` / `.deleted` | M7, M9, D6 / M6, M7, M11 | True |
| `link.activity.created` / `.updated` / `.deleted` | K2 / K5 / K6 | True |
| `attachment.activity.created` / `.deleted` | K8, K14 / K10, K15 | True |
| `issue_relation.activity.created` / `.deleted` | R2 / R3 | True |
| `issue_reaction.activity.created` / `.deleted` | C8 / C9 | True |
| `comment_reaction.activity.created` / `.deleted` | C11 / C12 | True |
| `issue_vote.activity.*`, `issue_draft.activity.*` | anderer Bereich (Space/Drafts) | – |
| `intake.activity.created` | N9 (Statuswechsel) | False |

Das Feld-Mapping für `issue.activity.updated` (`ISSUE_ACTIVITY_MAPPER`): `name, parent_id, priority, state_id, description_html, target_date, start_date, label_ids, assignee_ids, estimate_point, archived_at, closed_to` (+ Aliase `parent, state, assignees, labels`). Andere Felder (z. B. `sort_order`, `type`) erzeugen **keine** Activity.

Webhooks (`model_activity`): `issue` (I3 created, I8 updated), `issue_comment` (C2, C5), `cycle` (Y2, Y5), `module` (M2, M5). Deletes in diesem Bereich erzeugen **keine** Webhooks.

### 2.20 Fehlermeldungs-Inventar (wortgleich übernehmen)

| HTTP | Body | Endpunkte |
|---|---|---|
| 400 | `{"error": "Issues are required"}` | I1, Y8, M9 |
| 400 | `{"error": "Group by and sub group by cannot have same parameters"}` | I2, A1, Y7, M8 |
| 400 | `{"detail": "Invalid group_by field: <f>"}` / `{"detail": "Invalid sub_group_by field: <f>"}` | alle gruppierten Listen |
| 403 | `{"error": "You don't have the required permissions."}` | `allow_permission` |
| 403 | `{"error": "You are not allowed to view this issue"}` | I6, I13, V3, N8, N11, W3 |
| 404 | `{"error": "The required object does not exist."}` | I6, I13, generisch |
| 404 | `{"error": "Issue not found"}` | I8, C1, C2, C13, R1–R3 |
| 400 | `{"error": "Issue IDs are required"}` | A5, A6 |
| 400 | `{"error_code": 4091, "error_message": "INVALID_ARCHIVE_STATE_GROUP"}` | A5 |
| 400 | `{"error": "Can only archive completed or cancelled state group issue"}` | A3 |
| 400 | `{"message": "Start date cannot exceed target date"}` | A8 |
| 400 | `{"non_field_errors": ["Start date cannot exceed target date"]}` | I3, I8, M2, M5 |
| 400 | `{"non_field_errors": ["State is not valid please pass a valid state_id"]}` | I3, I8 |
| 400 | `{"non_field_errors": ["Parent is not valid issue_id please pass a valid issue_id"]}` | I3, I8 |
| 400 | `{"non_field_errors": ["Estimate point is not valid please pass a valid estimate_point_id"]}` | I3, I8 |
| 400 | `{"error": ["html content is not valid"]}` | I3, I8, N7, N9 |
| 400 | `{"description_binary": ["Invalid binary data"]}` | I3, I8 |
| 400 | `{"message": "Issue relation type is required"}` | R2 |
| 404 | `{"error": "Issue relation not found"}` | R3 |
| 404 | `{"error": "Parent issue not found"}` / 400 `{"error": "Sub Issue IDs are required"}` | R5 |
| 400 | `{"error": "You are not allowed to comment on the issue"}` | C2 |
| 400 | `{"comment_html": ["HTML content is not valid"]}` | C2, C5 |
| 400 | `{"error": "Reaction already exists for the user"}` | C11 |
| 400 | `{"error": "URL already exists for this Issue"}` | K2, K5, M14 |
| 400 | `{"error": "URL already exists."}` | M13 |
| 400 | `{"url": {"error": "Invalid URL format."}}` (Feldvalidierung) bzw. `{"error": "Invalid URL format."}` (in `update()`/`create()` des ModuleLinkSerializers) | K2, K5, M13, M14 |
| 404 | `{"error": "Issue attachment not found."}` | K10 |
| 400 | `{"error": "Invalid file type.", "status": false}` | K13 |
| 400 | `{"error": "The asset is not uploaded.", "status": false}` | K12 |
| 400 | `{"error": "Subscriber must be a member of the project."}` | S2 |
| 400 | `{"message": "User already subscribed to the issue."}` | S5 |
| 400 | `{"name": ["LABEL_NAME_ALREADY_EXISTS"]}` / `{"error": "Label with the same name already exists in the project"}` | L2, L5 |
| 404 | `{"error": "Intake not found"}` | N6 |
| 400 | `{"error": "Name is required"}` / `{"error": "Invalid priority"}` | N7 |
| 403 | `{"error": "Only admin or creator can update the intake work items"}` | N9 |
| 400 | `{"error": "You cannot edit intake issues"}` | N9 |
| 400 | `{"status": ["Cannot accept intake issue: No default state found for the project"]}` | N9 |
| 400 | `{"error": "You cannot delete the default intake"}` | N5 |
| 400 | `{"error": "Both start date and end date are either required or are to be null"}` | Y2 |
| 400 | `{"non_field_errors": ["Start date cannot exceed end date"]}` | Y2, Y5 |
| 400 | `{"error": "Archived cycle cannot be updated"}` / `{"error": "The Cycle has already been completed so it cannot be edited"}` | Y5 |
| 404 | `{"error": "Cycle not found"}` | Y3, Y22 |
| 400 | `{"error": "The Cycle has already been completed so no new issues can be added"}` | Y8 |
| 400 | `{"error": "Start date and end date both are required"}` | Y11 |
| 200 | `{"error": "You have a cycle already on the given dates, if you want to create a draft cycle you can do that by removing dates", "status": false}` | Y11 |
| 400 | `{"error": "New Cycle Id is required"}` / `{"error": "The cycle where the issues are transferred is already completed"}` / `{"error": "Source cycle not found"}` | Y15 |
| 400 | `{"error": "Only completed cycles can be archived"}` | Y18 |
| 400 | `{"error": "Cycle has no start or end date"}` | Y23 |
| 400 | `{"error": "Module with this name already exists"}` | M2, M5 |
| 404 | `{"error": "Module not found"}` | M3, M5 |
| 400 | `{"error": "Archived module cannot be updated"}` | M5 |
| 400 | `{"error": "Only completed or cancelled modules can be archived"}` | M20 |
| 400 | `{"error": "view is locked"}` / `{"error": "Only the owner of the view can update the view"}` | W5, W11 |
| 400 | `{"error": "Only admin or owner can delete the view"}` | W6, W12 |
| 404 | `{"error": "Page not found"}` | G4 |
| 400 | `{"error": "Page is locked"}` | G5 |
| 400 | `{"error": "Access cannot be updated since this page is owned by someone else"}` | G5, G13 |
| 400 | `{"error": "The page should be archived before deleting"}` | G6 |
| 403 | `{"error": "Only admin or owner can delete the page"}` | G6 |
| 400 | `{"error": "Only the owner or admin can archive the page"}` / `{"error": "Only the owner or admin can un archive the page"}` | G9, G10 |
| 400 | `{"error_code": 4701, "error_message": "PAGE_LOCKED"}` / `{"error_code": 4702, "error_message": "PAGE_ARCHIVED"}` | G15 |
| 403 | `{"error": "Permission denied"}` | G18 |

---

## 3. Verhalten / Logik / Abläufe im Detail

### 3.1 Die Issue-Listen-Abfrage (Kernalgorithmus, nachbaubar in EF Core)

Referenzimplementierung: `IssueViewSet.list` (`apps/api/plane/app/views/issue/base.py`). Die anderen Listen (A1, Y7, M8, W13, I4, I1) sind Varianten (Tabelle 3.1.10).

#### 3.1.1 Pipeline (exakte Reihenfolge)

| Schritt | Aktion | Quelle |
|---|---|---|
| 1 | `filters = issue_filters(query_params, "GET")` (Legacy-Dict), `order_by_param = GET.order_by or "-created_at"` | `apps/api/plane/utils/issue_filters.py` |
| 2 | Basismenge `B0 = Issue.issue_objects.filter(project_id, workspace__slug).distinct()` | `IssueViewSet.get_queryset`, `IssueManager` in `apps/api/plane/db/models/issue.py` |
| 3 | Rich-Filter: `ComplexFilterBackend.filter_queryset` → **ein** kombiniertes `Q` | `apps/api/plane/utils/filters/filter_backend.py` |
| 4 | Legacy-Filter `B.filter(**filters, **extra)` (`extra = {"updated_at__gt": …}` falls gesetzt) – **ein** `filter()`-Aufruf (Joins werden innerhalb geteilt) | `IssueViewSet.list` |
| 5 | Snapshot `T = deepcopy(B)` (für `total_count` und für `issue_group_values` der Felder `target_date`, `start_date`, `created_by`) | ebd. |
| 6 | Annotationen `cycle_id`, `link_count`, `attachment_count`, `sub_issues_count` (3.1.2) | `IssueViewSet.apply_annotations` |
| 7 | Sortierung `order_issue_queryset` → liefert `(qs, key)` (3.1.3) | `apps/api/plane/utils/order_queryset.py` |
| 8 | `issue_queryset_grouper(qs, group_by, sub_group_by)`: bei M2M-Gruppierung Filter auf aktive Zwischenzeile; Annotation der ID-Arrays `assignee_ids`, `label_ids`, `module_ids` **außer** dem gruppierten Feld | `apps/api/plane/utils/grouper.py` |
| 9 | `recent_visited_task(entity_name="project")` | `apps/api/plane/bgtasks/recent_visited_task.py` |
| 10 | Gast-Filter: wenn aktives Gast-Mitglied **und** `not project.guest_view_all_features` → `qs` und `T` zusätzlich `created_by = user` | `IssueViewSet.list` |
| 11 | Validierung `group_by == sub_group_by` → 400 | ebd. |
| 12 | Paginierung: ungruppiert (`OffsetPaginator`), gruppiert (`GroupedOffsetPaginator`) oder untergruppiert (`SubGroupedOffsetPaginator`); `group_by`/`sub_group_by` gegen `ISSUE_GROUP_BY_ALLOWLIST` (400) | `apps/api/plane/utils/paginator.py` |
| 13 | `on_results` = `issue_on_results(...)` → `.values(...)` → `S-ISSUE-LIST`; bei Gruppierung `process_results` | `apps/api/plane/utils/grouper.py`, `paginator.py` |

#### 3.1.2 Basismenge und Annotationen als SQL

```sql
-- B0: Issue.issue_objects (SoftDeletionManager + IssueManager)
SELECT DISTINCT i.*
FROM issues i
LEFT JOIN states   s ON s.id = i.state_id
JOIN      projects p ON p.id = i.project_id
JOIN      workspaces w ON w.id = i.workspace_id
WHERE i.deleted_at IS NULL
  AND NOT (s."group" = 'triage' AND s."group" IS NOT NULL)   -- Issues ohne State bleiben enthalten
  AND i.archived_at IS NULL
  AND p.archived_at IS NULL
  AND i.is_draft = FALSE
  AND i.project_id = :project_id
  AND w.slug = :slug;

-- Annotationen (pro Zeile, korrelierte Subqueries)
cycle_id         = (SELECT ci.cycle_id FROM cycle_issues ci
                    WHERE ci.issue_id = i.id AND ci.deleted_at IS NULL
                    ORDER BY ci.created_at DESC LIMIT 1)
link_count       = (SELECT COUNT(l.id) FROM issue_links l
                    WHERE l.issue_id = i.id AND l.deleted_at IS NULL GROUP BY l.issue_id)        -- NULL wenn keine
attachment_count = (SELECT COUNT(f.id) FROM file_assets f
                    WHERE f.issue_id = i.id AND f.entity_type = 'ISSUE_ATTACHMENT'
                      AND f.deleted_at IS NULL GROUP BY f.issue_id)                              -- zählt auch is_uploaded=false
sub_issues_count = (SELECT COUNT(c.id) FROM issues c LEFT JOIN states cs ON cs.id = c.state_id JOIN projects cp ON cp.id = c.project_id
                    WHERE c.parent_id = i.id AND c.deleted_at IS NULL AND NOT (cs."group" = 'triage')
                      AND c.archived_at IS NULL AND cp.archived_at IS NULL AND c.is_draft = FALSE
                    GROUP BY c.parent_id)                                                        -- NULL wenn keine
-- issue_queryset_grouper (nur wenn nicht nach dem jeweiligen Feld gruppiert wird)
assignee_ids = COALESCE((SELECT ARRAY_AGG(DISTINCT ia.assignee_id) FROM issue_assignees ia
                         WHERE ia.issue_id = i.id AND ia.deleted_at IS NULL), '{}')
label_ids    = COALESCE((SELECT ARRAY_AGG(DISTINCT il.label_id) FROM issue_labels il
                         WHERE il.issue_id = i.id AND il.deleted_at IS NULL), '{}')
module_ids   = COALESCE((SELECT ARRAY_AGG(DISTINCT mi.module_id) FROM module_issues mi JOIN modules m ON m.id = mi.module_id
                         WHERE mi.issue_id = i.id AND mi.deleted_at IS NULL AND m.archived_at IS NULL), '{}')
state__group = s."group"
```

Hinweise:
- Label-/Assignee-Zuordnungen auf **soft-gelöschte** Labels/Nutzer werden nicht gesondert ausgefiltert (nur die Zwischenzeile `deleted_at`).
- Die Detail-Endpunkte (I6, I8, I13, Intake) filtern Assignees zusätzlich mit `assignees__member_project__is_active=True` (der Nutzer hat **irgendeine** aktive Projektmitgliedschaft – nicht zwingend in diesem Projekt). Der Listen-Pfad (grouper) tut das **nicht**.

#### 3.1.3 Sortierung (`order_issue_queryset`) und effektive `ORDER BY`

`sanitize_order_by` → Wert ∈ Allowlist sonst `-created_at`. Danach:

| Eingabe `order_by` | Annotation | Rückgabe-`key` (für Paginator) | Effektive Ordnung |
|---|---|---|---|
| `priority` | `priority_order = CASE priority WHEN 'urgent' THEN '0' WHEN 'high' THEN '1' WHEN 'medium' THEN '2' WHEN 'low' THEN '3' WHEN 'none' THEN '4' END` (**Text**) | `-priority_order` | `priority_order DESC NULLS LAST, created_at DESC` → none, low, medium, high, urgent |
| `-priority` (UI-Option „Priority“) | wie oben | `priority_order` | `ASC NULLS LAST` → urgent, high, medium, low, none |
| `state__group` | `state_order = CASE s.group WHEN 'backlog' THEN '0' … WHEN 'cancelled' THEN '4' ELSE '5' END` | `state_order` | backlog → unstarted → started → completed → cancelled → (Triage/ohne State) |
| `-state__group` | `state_order` mit **umgekehrter** Liste (`cancelled`=0 … `backlog`=4, sonst 5) | `-state_order` | DESC → (sonstige `'5'`) zuerst, dann backlog → … → cancelled (Quirk: gleiche Gruppenreihenfolge wie aufsteigend) |
| `labels__name`, `assignees__first_name`, `issue_module__module__name` | `min_values = MIN(<pfad>)` (Aggregat → `GROUP BY` über Issue-Spalten; Join über M2M **ohne** Soft-Delete-Filter) | `min_values` | `ASC NULLS LAST` |
| `-labels__name`, `-assignees__first_name`, `-issue_module__module__name` | `min_values = MIN(<pfad>)` | `-min_values` | `DESC NULLS LAST` |
| alle anderen (`created_at`, `updated_at`, `sequence_id`, `sort_order`, `target_date`, `start_date`, `completed_at`, `archived_at`, `state__name`, je ±) | – | unverändert | `<feld> ASC/DESC NULLS LAST, created_at DESC` |

Der Paginator **überschreibt** die Ordnung des Querysets immer mit `F(key).asc/desc(nulls_last=True), "-created_at"` (`OffsetPaginator.get_result`, Window-`order_by` der Gruppen-Paginatoren). Der Tiebreaker ist immer `created_at DESC` (kein `id` → bei identischem `created_at` nicht deterministisch).

#### 3.1.4 Ungruppierte Paginierung (`OffsetPaginator`)

```
limit  = min(per_page, 1000)
page   = cursor.offset                     # 2. Teil des Cursors
offset = page * limit                      # NICHT cursor.value
rows   = ordered[offset : offset + limit + 1]
results = rows[:limit]
next_cursor = f"{limit}:{page+1}:0", next_page_results = len(rows) > limit
prev_cursor = f"{limit}:{page-1}:1", prev_page_results = page > 0
total_count = total_results = T.count()    # T = Snapshot (Schritt 5) inkl. Gast-Filter
total_pages = ceil(total_count / limit)
count       = len(results)
```

#### 3.1.5 Gruppierte Paginierung (`GroupedOffsetPaginator`)

```
limit  = min(per_page, 1000)
page   = cursor.offset ; size = cursor.value (Fallback limit, wenn 0)
offset = page * size   ; stop = offset + size + 1
Q = qs + row_number = ROW_NUMBER() OVER (PARTITION BY <group_expr>
                                         ORDER BY <key> [ASC|DESC] NULLS LAST, created_at DESC)
results  = Q WHERE row_number > offset AND row_number < stop
           ORDER BY <key> NULLS LAST, created_at DESC          -- d. h. pro Gruppe die Zeilen offset+1 … offset+size
next_page_results = EXISTS(Q WHERE row_number >= stop)          -- irgendeine Gruppe hat weitere Zeilen
prev_page_results = page > 0
total_count = total_results = COUNT(*) FROM Q                   -- Zeilen, bei M2M-Gruppierung (Issue, Wert)-Paare
total_pages = results leer ? 0 : ceil( MAX_g COUNT(DISTINCT id) FILTER (WHERE count_filter) / limit )
```

`<group_expr>` je Gruppierfeld:

| `group_by` | SQL-Ausdruck / Join | Wert „leer“ |
|---|---|---|
| `state_id` | `i.state_id` | `None` |
| `state__group` | `s."group"` | `None` |
| `priority` | `i.priority` | – |
| `cycle_id` | Annotation `cycle_id` (Subquery) | `None` |
| `project_id` | `i.project_id` | – |
| `created_by` | `i.created_by_id` | `None` |
| `target_date`, `start_date` | Spalte | `None` |
| `labels__id` | `LEFT JOIN issue_labels il ON il.issue_id = i.id LEFT JOIN labels l ON l.id = il.label_id` → `l.id`; Grouper-Filter `il.deleted_at IS NULL` (eigener Join-Alias, siehe 5.3) | `None` (Issue ohne Label) |
| `assignees__id` | analog über `issue_assignees` → `users.id`; Filter `deleted_at IS NULL` | `None` |
| `issue_module__module_id` | `LEFT JOIN module_issues mi ON mi.issue_id = i.id` → `mi.module_id`; Filter `mi.deleted_at IS NULL` | `None` |

`count_filter` (identisch in allen gruppierten Listen):
```sql
( ii.status IN (1, -1, 2) OR ii.id IS NULL )  -- LEFT JOIN intake_issues ii ON ii.issue_id = i.id (ohne deleted_at-Filter)
AND i.archived_at IS NULL AND i.is_draft = FALSE
```

**Gruppensummen** (`__get_total_dict`): `SELECT <group_expr>, COUNT(DISTINCT i.id) FILTER (WHERE count_filter) … GROUP BY <group_expr>`; Schlüssel `str(wert)`; **Quirk:** Ist die Summe 0, wird 1 eingetragen (`1 if count == 0 else count`).

**`process_results`**:

- *Nicht-M2M-Gruppierung* (`__query_grouper`): Ausgabe enthält **jeden** Wert aus `group_by_fields` (Reihenfolge der Liste, 3.1.7) als Schlüssel mit `{"results": [], "total_results": totals.get(key, 0)}`; Zeilen werden per `str(row[group_field])` einsortiert; Zeilen mit Schlüssel außerhalb von `group_by_fields` werden **verworfen** (z. B. `state_id` eines Triage-States, `None`-State).
- *M2M-Gruppierung* (`__query_multi_grouper`, Felder `labels__id`, `assignees__id`, `issue_module__module_id`): Ausgabe enthält **nur Gruppen, die auf dieser Seite Zeilen haben** (keine leeren Gruppen); jede Issue-Zeile wird pro Gruppe einmal eingefügt (Duplikatprüfung per `id`); das Feld `label_ids`/`assignee_ids`/`module_ids` der Zeile wird auf die Menge der Gruppen gesetzt, in denen das Issue **auf dieser Seite** vorkommt (oder `[]`, wenn `"None"` darunter ist). `total_results` = Gruppensumme.

#### 3.1.6 Untergruppierte Paginierung (`SubGroupedOffsetPaginator`)

- Fenster: `ROW_NUMBER() OVER (PARTITION BY <group_expr>, <sub_group_expr> ORDER BY <key> NULLS LAST, created_at DESC)`; Seitengröße pro (Gruppe, Untergruppe) = `cursor.value`.
- `total_pages` wie 3.1.5, aber nur über die **Hauptgruppe**.
- Gruppensummen: wie 3.1.5 (inkl. 0→1-Quirk); Untergruppensummen: `COUNT(DISTINCT id) FILTER (count_filter) GROUP BY group, sub_group` (ohne Quirk).
- Gerüst (`__get_field_dict`): für **jeden** Wert aus `group_by_fields` ein Eintrag; darin **nur die Untergruppen-Schlüssel, die in den Untergruppensummen für diese Gruppe vorkommen** (`sub_group_by_fields` wird **nicht** verwendet!), jeweils `{"results": [], "total_results": n}`.
- Nicht-M2M: Zeile wird direkt in `processed[group][sub_group]` eingefügt (fehlt der Gruppenschlüssel im Gerüst → `KeyError` → 400 `{"error": "The required key does not exist."}`).
- M2M (Gruppe oder Untergruppe M2M): Einfügen nur, wenn Gruppe und Untergruppe im Gerüst existieren; ID-Listen wie in 3.1.5 gesetzt.
- Edge-Case: `group_by=assignees__id` mit `sub_group_by` → `group_by_fields` enthält **kein** `"None"` → nicht zugewiesene Issues verschwinden aus der Swimlane-Ansicht.

#### 3.1.7 Gruppenwerte (`issue_group_values`)

| Feld | Werteliste (Reihenfolge = JSON-Schlüsselreihenfolge) |
|---|---|
| `state_id` | IDs aller `State.objects` (ohne Triage-Gruppe, nicht gelöscht) mit `is_triage=False` im Projekt (DB-Reihenfolge) |
| `labels__id` | IDs aller Labels des Projekts + `"None"` |
| `assignees__id` | `member_id` aller aktiven Projektmitglieder (kein `"None"`) |
| `issue_module__module_id` | IDs aller Module des Projekts (inkl. archivierte) + `"None"` |
| `cycle_id` | IDs aller Cycles des Projekts (inkl. archivierte) + `"None"` |
| `project_id` | Projekt-ID |
| `priority` | `["low", "medium", "high", "urgent", "none"]` |
| `state__group` | `["backlog", "unstarted", "started", "completed", "cancelled"]` |
| `target_date`, `start_date`, `created_by` | `DISTINCT` Werte aus dem Snapshot `T` (inkl. `None`); **ohne** `queryset`-Argument → `AttributeError` (A1, Y7) |
| sonst | `[]` |

Workspace-Variante (`project_id=None`, `user=…`): Projekte = aktive Mitgliedschaften des Nutzers; `assignees__id` = alle aktiven Workspace-Mitglieder (genutzt in anderen Bereichen, z. B. Profil-Issues).

#### 3.1.8 Zusammenspiel mit dem Web-Client

| Situation | Request | Quelle |
|---|---|---|
| Erste Seite (Liste gruppiert) | `GET {P}/issues/?group_by=state_id&order_by=sort_order&sub_issue=true&filters=<json>&layout=list&cursor=50:0:0&per_page=50` | `apps/web/store/issue/helpers/issue-filter-helper.store.ts`, `apps/web/components/issues/issue-layouts/list/base-list-root.tsx` |
| Mehr laden in einer Gruppe | gleicher Request **ohne** `group_by`, dafür Legacy-Filter des Gruppenwerts (`state=<id>`, `labels=<id>` oder `labels=None`, `priority=high`, `state_group=started`, `cycle=None`, `target_date=YYYY-MM-DD`, …) und `cursor=50:1:0` bzw. `next_cursor` | `getPaginationParams` |
| Kanban mit Swimlanes | `group_by` + `sub_group_by`, `per_page=10`; „mehr laden“ in Zelle mit beiden Gruppenfiltern | `apps/web/components/issues/issue-layouts/kanban/base-kanban-root.tsx` |
| Kalender | `group_by=target_date`, `target_date=<after>;after,<before>;before`, `per_page=4` (Monat) / 30 (Woche) | `apps/web/components/issues/issue-layouts/calendar/base-calendar-root.tsx` |
| Spreadsheet / Gantt | ungruppiert, `per_page=100`; Gantt mit Abhängigkeiten (`ENABLE_ISSUE_DEPENDENCIES`) → `expand=issue_relation,issue_related` → Endpunkt I4 | `packages/constants/src/issue/filter.ts` (`ENABLE_ISSUE_DEPENDENCIES = false` im CE) |
| Cycle-/Module-Ansicht | I2 mit `cycle=<id>` bzw. `module=<id>` (Legacy-Filter) | `apps/web/store/issue/cycle/filter.store.ts`, `module/filter.store.ts` |
| Projekt-View | I2 mit den `rich_filters` der View | `apps/web/store/issue/project-views/filter.store.ts` |
| Workspace-Views / All Work Items | W13 | `apps/web/store/issue/workspace/issue.store.ts` |
| Antwortverarbeitung | Array → Gruppe `"All Issues"`; Dict → `groupedIssueIds[group]`, `groupedIssueCount[group] = total_results` | `apps/web/store/issue/helpers/base-issues.store.ts` |

#### 3.1.9 Rechte-Varianten

- `IssueDetailEndpoint` (I4): `EXISTS`-Subquery über `project__project_projectmember` mit drei Alternativen (Rolle > 5; Gast mit `guest_view_all_features`; Gast + `created_by = user`).
- `WorkspaceViewIssuesViewSet` (W13): Filter direkt über `project__project_projectmember__member = user AND is_active AND (role > 5 OR (role = 5 AND guest_view_all_features) OR (role = 5 AND NOT guest_view_all_features AND created_by = user))`.
- `IssueListEndpoint` (I1): Gast-Filter wie I2.

#### 3.1.10 Varianten-Übersicht

| Endpunkt | Basismenge | Gast-Filter | Gruppierung | Snapshot für Datumsgruppen | Default `order_by` | Serializer der Ergebnisse |
|---|---|---|---|---|---|---|
| I2 `IssueViewSet.list` | `issue_objects` im Projekt | ja | ja | ja | `-created_at` | `issue_on_results` |
| A1 `IssueArchiveViewSet.list` | `Issue.objects`, `archived_at IS NOT NULL`, kein Epic; `show_sub_issues=false` → `parent IS NULL` | (Gäste ausgeschlossen) | ja | **nein** | `-created_at` | `issue_on_results` |
| Y7 `CycleIssueViewSet.list` | `issue_objects` + aktive `CycleIssue` | (Gäste ausgeschlossen) | ja | **nein** | `-created_at` | `issue_on_results` |
| M8 `ModuleIssueViewSet.list` | `issue_objects` + aktive `ModuleIssue`, `distinct` | (Gäste ausgeschlossen) | ja | ja | `created_at` | `issue_on_results` |
| W13 `WorkspaceViewIssuesViewSet.list` | `issue_objects` im Workspace + Rollenfilter | ja (pro Projekt) | nein | – | `-created_at` | `ViewIssueListSerializer` |
| I4 `IssueDetailEndpoint.get` | `issue_objects` + Rechte-Subquery | ja | nein | – | `-created_at` | `IssueListDetailSerializer` |
| I1 `IssueListEndpoint.get` | `issue_objects` + `pk IN issues` + `state.deleted_at IS NULL` | ja | nein (nur Annotationen) | – | `-created_at` | `.values()` / `IssueSerializer` |

### 3.2 Legacy-Datumsfilter-Grammatik (`date_filter`)

Eingabe: kommagetrennte Liste von Termen; jeder Term `teil0;teil1[;teil2]`. Für `created_at`, `updated_at`, `completed_at` wird das Ziel `<feld>__date` verwendet (Datumsvergleich in Nutzer-TZ), für `start_date`/`target_date` das Feld direkt.

| Term | Ergebnis |
|---|---|
| `YYYY-MM-DD;after` | `<ziel>__gte = Datum` |
| `YYYY-MM-DD;before` (bzw. alles ohne `after`) | `<ziel>__lte = Datum` |
| `N_weeks;after;fromnow` | `__gte = heute + N Wochen` |
| `N_weeks;after;<anderes>` | `__gte = heute − N Wochen` |
| `N_weeks;before;fromnow` | `__lte = heute + N Wochen` |
| `N_weeks;before;<anderes>` | `__lte = heute − N Wochen` |
| `N_months;…` | wie Wochen, mit `N × 30 Tagen` |
| `N_weeks;after` (nur 2 Teile, relatives Muster) | **ignoriert** |
| `YYYY-MM-DD` (ohne `;`) | `<ziel>__contains = 'YYYY-MM-DD'` (Text-Contains; wirkt wie Gleichheit) |

„heute“ = `timezone.now().date()` (UTC-Datum, nicht Nutzer-TZ). Mehrere Terme gleicher Richtung überschreiben sich (Dict-Schlüssel). Ein Term mit leerem Wert in der CSV (`"" in liste`) deaktiviert den Filter komplett.

### 3.3 Rich-Filter-Auswertung

1. `filters`-String → `json.loads` (400 `invalid_json`).
2. Strukturvalidierung rekursiv (Tiefe ≤ 5; genau ein logischer Operator je Objekt; keine Mischung Operator/Feld; `and`/`or` nicht-leere Liste von Objekten; `not` ein Objekt; Blätter nicht leer; Werte Skalar/`null`/Liste von Skalaren, Listen nicht leer).
3. Feld-Allowlist: alle Blatt-Schlüssel müssen in `IssueFilterSet.base_filters` stehen (2.18.2).
4. Auswertung: Blatt → `QueryDict` (Listen → mehrere Werte; `null` → `""`) → `IssueFilterSet(data, queryset).is_valid()` (400 `invalid_filterset`) → `build_combined_q()` (AND aller **übergebenen** Schlüssel; Custom-Methoden liefern `Q`); `and` → `Q() & …`, `or` → `Q() | …`, `not` → `~Q`.
5. Ein einziges `queryset.filter(combined_q)`.

Achtung bei `not` über Relationen (z. B. `{"not": {"label_id__in": "a"}}`): Django übersetzt `~Q(label_issue__label_id__in=…, label_issue__deleted_at__isnull=True)` in eine `NOT EXISTS`/Subquery-Semantik („hat kein aktives Label a“). In .NET explizit als `!issue.Labels.Any(l => l.DeletedAt == null && ids.Contains(l.LabelId))` umsetzen.

### 3.4 Issue anlegen / ändern

#### 3.4.1 Validierung (`IssueCreateSerializer.validate`)

| Regel | Fehler |
|---|---|
| `start_date > target_date` (beide gesetzt) | `non_field_errors: "Start date cannot exceed target date"` |
| `description_html` → `validate_html_content` (nh3-Sanitizing, ≤ 10 MB); bereinigtes HTML ersetzt Eingabe | `{"error": "html content is not valid"}` |
| `description_binary` → `validate_binary_data` (Base64/Größe ≤ 10 MB/Mindestlänge 4/verdächtige Muster) | `{"description_binary": "Invalid binary data"}` |
| `assignee_ids` → auf aktive Projektmitglieder mit Rolle ≥ 15 reduziert (stilles Verwerfen von Gästen/Fremden) | – |
| `label_ids` → auf Labels des Projekts reduziert (still) | – |
| `state` muss im Projekt liegen (`State.objects` ohne Triage; bei `allow_triage_state` nur Triage-States) | `"State is not valid please pass a valid state_id"` |
| `parent` muss im **selben Projekt** liegen (`Issue.objects`, inkl. archiviert) | `"Parent is not valid issue_id please pass a valid issue_id"` |
| `estimate_point` muss im Projekt liegen | `"Estimate point is not valid please pass a valid estimate_point_id"` |

#### 3.4.2 Anlegen (`IssueCreateSerializer.create` + `Issue.save`)

1. `Issue.objects.create(**validated, project_id)`.
2. `Issue.save()` (`apps/api/plane/db/models/issue.py`):
   - `_ensure_default_state`: ohne State → Default-State des Projekts (`default=True`, nicht Triage) oder erster Nicht-Triage-State.
   - `_sync_completed_at`: bei Insert bzw. geändertem `state_id` → `completed_at = now()` wenn State-Gruppe `completed`, sonst `null`.
   - In Transaktion mit `pg_advisory_xact_lock(convert_uuid_to_integer(project.id))`: `sequence_id = MAX(IssueSequence.sequence) + 1` (oder 1); `description_stripped = strip_tags(description_html)`; `sort_order = MAX(sort_order der Issues gleichen Projekts **und gleichen States**) + 10000` (falls vorhanden, sonst 65535); Insert; `IssueSequence(issue, sequence, project)` anlegen.
3. Assignees: wenn `assignee_ids` nicht leer → `bulk_create IssueAssignee` (IntegrityError ignoriert); **sonst** Default-Assignee des Projekts (`project.default_assignee_id`), falls aktives Mitglied mit Rolle ≥ 15.
4. Labels: `bulk_create IssueLabel`.
5. Antwort: Neu-Selektion über `get_queryset()` + Annotationen + Grouper → `S-ISSUE-VALUES`.

#### 3.4.3 Ändern (`partial_update` + `IssueCreateSerializer.update`)

1. `skip_activity` wird aus dem Body entfernt; `is_description_update = description_html is not None`.
2. Issue aus `issue_objects` + Annotationen + `label_ids/assignee_ids/module_ids` (per `ArrayAgg` mit Filtern) → `current_instance = IssueDetailSerializer(issue)` (JSON).
3. `update()`: wenn `assignee_ids` übergeben → **alle** `IssueAssignee` des Issues soft-löschen (QuerySet) und neu anlegen (`ignore_conflicts`); analog `label_ids`. Leere Liste = alle entfernen. `updated_at = now()`.
4. `Issue.save()`: `completed_at`-Sync bei State-Wechsel; `description_stripped`.
5. Seiteneffekte nur, wenn **nicht** (`skip_activity` und Beschreibungs-Update) – Zweck: Migrationen/Backfills der Beschreibung ohne Verlaufseintrag (Live-Server/Editor).
6. `writable_data` entfernt read-only Schlüssel aus `requested_data` (keine Scheinänderungen im Verlauf/Webhook).

#### 3.4.4 Detail (`retrieve`, `IssueDetailSerializer`, `expand`)

- Annotiert: `cycle_id` (Soft-Delete-Filter implizit über `CycleIssue.objects`), Zähler, `label_ids`, `assignee_ids` (mit `member_project__is_active`), `module_ids` (nicht archivierte Module), `is_subscribed`; Prefetch `issue_reactions` (mit `actor`), `issue_link` (mit `created_by`).
- `expand=issue_reactions` → `IssueReactionLiteSerializer[]`; `expand=issue_link` → `IssueLinkLiteSerializer[]`; `expand=issue_attachments` → `IssueAttachmentLiteSerializer[]` (alle `ISSUE_ATTACHMENT`-Assets, auch nicht hochgeladene); `expand=parent` → `{id, sequence_id, project_id}`; weitere Schlüssel aus 2.18.5. Nullable-Relation → `null`.

### 3.5 Löschen & Soft-Delete

| Aktion | Mechanik | Kaskade |
|---|---|---|
| I9 Issue löschen | `issue.delete()` → `deleted_at`, Task `soft_delete_related_objects` | rekursiv über alle Reverse-Relationen mit `CASCADE` (Kommentare, Links, Assignees, Labels, CycleIssue, ModuleIssue, Relationen, Subscriber, Reaktionen, Versionen, IntakeIssue, Sub-Issues (`parent` CASCADE!) …); `SET_NULL`-Relationen werden auf `NULL` gesetzt (`IssueSequence.issue`); `DO_NOTHING` (`IssueActivity.issue`) bleibt |
| A6 Bulk-Delete | `QuerySet.delete()` = `UPDATE … SET deleted_at` | nur CycleIssue/ModuleIssue explizit; sonst **keine** Kaskade |
| UserRecentVisit | `delete(soft=False)` | hart |
| UserFavorite in Favoriten-Endpunkten | `delete(soft=False)` | hart |
| UserFavorite bei Archiv/Löschen | `QuerySet.delete()` | soft |

Hinweis: Da Sub-Issues per `parent` **CASCADE** verbunden sind, löscht der Kaskaden-Task beim Löschen eines Eltern-Issues auch alle Kinder (soft).

### 3.6 Archivierung (Work Items)

- Voraussetzung: State-Gruppe `completed` oder `cancelled` (A3, A5). `archived_at` ist ein **Datum** (`DateField`).
- Archivierte Issues sind aus `issue_objects` ausgeschlossen (Listen, Zähler, Sub-Issue-Zähler, Relationen-Ziele, Cycle-/Module-Zähler über `issue_objects`), bleiben aber über `Issue.objects` abrufbar (I6, I13, C1, C13, R1).
- Unarchivieren (A4) setzt nur `archived_at = null`; keine State-Prüfung.
- Projekt-Automatisierung „Auto-Archive/Auto-Close“ (anderer Bereich, `apps/api/plane/bgtasks/issue_automation_task.py`) nutzt dasselbe Feld mit `"automation": true` in der Activity.

### 3.7 Relationen (Typen, Speicherung, Anzeige)

Gespeichert wird **immer** ein Datensatz `IssueRelation(issue, related_issue, relation_type)` mit `relation_type` ∈ {`duplicate`, `relates_to`, `blocked_by`, `start_before`, `finish_before`, `implemented_by`} (`IssueRelationChoices`, `apps/api/plane/db/models/issue.py`). Eindeutig: (`issue`, `related_issue`) bei `deleted_at IS NULL` – d. h. zwischen zwei Issues kann pro Richtung nur **eine** Relation existieren.

**Anlegen (R2)** für URL-Issue `X` und Ziel `Y`:

| Eingabe `relation_type` | gespeichert `issue` | gespeichert `related_issue` | gespeichert `relation_type` | Antwort-Serializer |
|---|---|---|---|---|
| `blocked_by` | X | Y | `blocked_by` | `IssueRelationSerializer` (zeigt Y) |
| `blocking` | **Y** | **X** | `blocked_by` | `RelatedIssueSerializer` (zeigt Y) |
| `start_before` | X | Y | `start_before` | `IssueRelationSerializer` |
| `start_after` | Y | X | `start_before` | `RelatedIssueSerializer` |
| `finish_before` | X | Y | `finish_before` | `IssueRelationSerializer` |
| `finish_after` | Y | X | `finish_before` | `RelatedIssueSerializer` |
| `relates_to` | X | Y | `relates_to` | `IssueRelationSerializer` |
| `duplicate` | X | Y | `duplicate` | `IssueRelationSerializer` |
| `implemented_by` | X | Y | `implemented_by` | `IssueRelationSerializer` |
| `implements` | X (!) | Y | `implemented_by` | `IssueRelationSerializer` (**Bug**: Richtung wird nicht getauscht, da `implements` nicht in der Tausch-Liste steht) |
| beliebiger anderer Text | X | Y | unverändert gespeichert | `IssueRelationSerializer` |

**Anzeige (R1)** für Issue `X`:

| Antwort-Schlüssel | Bedingung |
|---|---|
| `blocking` | `relation_type='blocked_by' AND related_issue=X` → zeige `issue` |
| `blocked_by` | `relation_type='blocked_by' AND issue=X` → zeige `related_issue` |
| `duplicate` | `duplicate` in beide Richtungen (UNION) |
| `relates_to` | `relates_to` in beide Richtungen |
| `start_after` | `start_before AND related_issue=X` → zeige `issue` |
| `start_before` | `start_before AND issue=X` → zeige `related_issue` |
| `finish_after` | `finish_before AND related_issue=X` → zeige `issue` |
| `finish_before` | `finish_before AND issue=X` → zeige `related_issue` |
| (fehlend) | `implemented_by`/`implements` werden nicht geliefert |

Die Zielmenge stammt aus `Issue.issue_objects` im **Workspace** (projektübergreifend), annotiert mit `label_ids`/`assignee_ids` (ArrayAgg) – archivierte/Draft/Triage-Ziele erscheinen nicht. Activity-Verarbeitung (`create_issue_relation_activity`) erzeugt Einträge für beide Seiten mit inversem Typ (`get_inverse_relation`, `apps/api/plane/utils/issue_relation_mapper.py`; Details im Activity-Analysedokument).

Client: CE-UI kennt `blocking`, `blocked_by`, `duplicate`, `relates_to` (`packages/types/src/issues/issue_relation.ts`); `start_*`/`finish_*` sind Gantt-Abhängigkeiten (in CE hinter `ENABLE_ISSUE_DEPENDENCIES=false`, nach ADR-001 zu aktivieren); `implemented_by`/`implements` sind EE-Funktionen.

### 3.8 Sub-Issues

- **Lesen (R4):** direkte Kinder (`parent_id = issue_id`) aus `issue_objects` im URL-Projekt; Felder wie `S-ISSUE-LIST` + `state_group`; `state_distribution = {state_group: [ids]}` über **alle** Kinder; `group_by`:
  - `assignees__ids` → je Assignee-ID ein Eintrag; Issues mit leerer Liste unter `"None"`.
  - jeder andere Schlüssel `k` der Zeile → `str(row[k])` (z. B. `state_id`, `priority`); fehlender Schlüssel → 400.
  - Antwort dann `{"sub_issues": {key: [rows]}, "state_distribution": …}`.
- **Zuordnen (R5):** setzt `parent` für alle übergebenen IDs desselben Projekts (keine Prüfung auf Zyklus, Selbstreferenz oder Tiefe; `bulk_update` umgeht `Issue.save`). Entfernen eines Parents erfolgt über I8 (`parent_id: null`).
- Kein eigener „Sub-Issue entfernen“-Endpunkt.

### 3.9 Kommentare & Verlauf

- `IssueComment.save()` (`apps/api/plane/db/models/issue.py`): `comment_stripped = strip_tags(comment_html)`; erzeugt/aktualisiert in derselben Transaktion eine `Description`-Zeile (`description_html/json/stripped`) und verknüpft sie (`description_id`).
- `access`: `INTERNAL` (Default) / `EXTERNAL` (für öffentlich geteilte Boards/Space relevant).
- `edited_at`: nur bei inhaltlicher HTML-Änderung via PATCH.
- `parent` (Antworten/Threads) existiert im Modell, wird von diesen Endpunkten aber nicht gesetzt (nicht in `COMMENT_WRITABLE_FIELDS`).
- **Verlauf (C13):** zwei getrennt sortierte Mengen (`created_at ASC`), danach zusammengeführt und nach `created_at` (ISO-String) sortiert. Activities mit `field ∈ {comment, vote, reaction, draft}` werden ausgeblendet (diese erscheinen über die Kommentar-Objekte bzw. gar nicht).

### 3.10 Reaktionen

- Issue-Reaktion: eindeutig (`issue`, `actor`, `reaction`) bei aktivem Datensatz; Löschen per `reaction_code` im Pfad (URL-kodiertes Emoji/Codepoint-String), nur eigene.
- Kommentar-Reaktion: analog über `comment_id`; Activity ohne `issue_id`.
- Reaktionen werden im Issue-Detail per `expand=issue_reactions` bzw. im Kommentar-Serializer (`comment_reactions`) ausgeliefert.

### 3.11 Links (Work Items)

1. `to_internal_value`: URL ohne `http://`/`https://` → `"http://" + url`.
2. `validate_url`: Django `URLValidator`.
3. `create`: Duplikat (gleiche `url` + `issue_id`; `issue_id` gelangt über `serializer.save(issue_id=…)` in `validated_data`) → `{"error": "URL already exists for this Issue"}`. `update`: gleiche Prüfung gegen andere Links desselben Issues.
4. `crawl_work_item_link_title` (`apps/api/plane/bgtasks/work_item_link_task.py`): HTTP-GET mit SSRF-Schutz (`validate_url_ip`, gepinnte Auflösung), Timeout 1 s, liest `<title>`; Favicon über `<link rel=icon…>`-Selektoren oder `/favicon.ico` (HEAD, Timeout 2 s), als Data-URI Base64; Fehler → Default-SVG-Favicon. Ergebnis `metadata = {"title": str|null, "favicon": "data:<mime>;base64,…", "url": <Original-URL>, "favicon_url": str|null}`; bei unerwartetem Fehler `{"error": "Unexpected error: …", "title": null, "favicon": null, "url": …}`. Max. Redirects `MAX_REDIRECTS`, Browser-User-Agent.
5. ADR-004: Crawl ist eine **ausgehende** Verbindung → in airgapped Umgebungen abschaltbar machen.

### 3.12 Attachments (Upload-Flow v2)

```
Client → POST …/attachments/ {name, type, size}
       ← {upload_data: {url, fields}, asset_id, attachment, asset_url}
Client → POST upload_data.url (multipart, direkt an S3/MinIO, presigned POST mit Content-Type/Größenbedingung)
Client → PATCH …/attachments/{asset_id}/   (bestätigt Upload → is_uploaded=true, Activity einmalig)
Lesen  → GET …/attachments/{id}/ → 302 presigned GET (Download, Content-Disposition attachment)
Löschen→ DELETE …/attachments/{id}/ (soft, Datei bleibt; Aufräumen durch Hintergrundjob, anderer Bereich)
```

- Erlaubte MIME-Typen: `settings.ATTACHMENT_MIME_TYPES` (`apps/api/plane/settings/common.py`, Bilder, Office/ODF, PDF, Text/Markdown/RTF, Audio, Video, Archive, 3D-Modelle, Fonts, `application/octet-stream` …).
- Größe: `min(size, FILE_SIZE_LIMIT)` (Env `FILE_SIZE_LIMIT`, Default 5 242 880 Byte).
- `asset_url` = `/api/assets/v2/workspaces/{slug}/projects/{project_id}/issues/{issue_id}/attachments/{id}/` (`FileAsset.asset_url`).
- v1 (K7/K8/K10) ist Legacy (Multipart direkt an Django). Für Greenfield genügt v2 (Client nutzt v2: `apps/web/services/issue/issue_attachment.service.ts`).

### 3.13 Description-Versionen (Work Items)

`issue_description_version_task` (`apps/api/plane/bgtasks/issue_description_version_task.py`):

1. Abbruch, wenn `updated_issue.description_html == issue.description_html` und nicht `is_creating` (bei I8 wird der **alte** Zustand übergeben → Version nur bei echter Änderung).
2. Neueste Version (`ORDER BY last_saved_at DESC`) laden.
3. Wenn diese dem gleichen Nutzer gehört und ≤ 600 s alt ist → **überschreiben** (`description_json/html/binary/stripped`, `last_saved_at`).
4. Sonst neue `IssueDescriptionVersion` (Kopie der aktuellen Beschreibung, `owned_by=user`).
5. Kein Limit der Anzahl (anders als Pages). Wiederherstellen erfolgt clientseitig durch PATCH der Beschreibung (kein Restore-Endpunkt).

`IssueVersion` (Eigenschafts-Snapshots): im CE nur Backfill (`sync_issue_version` Management-Command); der Update-Task `issue_task` wird nicht aufgerufen → Liste V1 ist i. d. R. leer.

### 3.14 Intake (Ablauf & Zustandsmaschine)

Status (`IntakeIssueStatus`, `apps/api/plane/db/models/intake.py`): `-2 PENDING` (Default), `-1 REJECTED`, `0 SNOOZED`, `1 ACCEPTED`, `2 DUPLICATE`.

```
             create (N7)                     PATCH status (N9, nur Projekt-Admin / WS-Admin)
  ──────────────────────────▶ PENDING(-2) ──┬──▶ ACCEPTED(1)  : State Triage → Default-State (Issue erscheint in Listen)
  Issue im Triage-State                      ├──▶ REJECTED(-1)  : Issue bleibt im Triage-State (unsichtbar in Listen)
  (unsichtbar in issue_objects)              ├──▶ SNOOZED(0)   + snoozed_till (00:00 Projekt-TZ); Beat-Task setzt zurück (anderer Bereich)
                                             └──▶ DUPLICATE(2) + duplicate_to = Issue-ID
```

- Jeder Statuswechsel ist frei (keine Übergangsregeln im Backend); Annahme schlägt fehl ohne Default-State.
- Rechte in N9 (Reihenfolge):
  1. Decorator `AP[A]+C(Issue)` (Projekt-Admin, WS-Admin+Mitglied oder Ersteller des Issues).
  2. Kein Projektmitglied und kein WS-Admin → 403.
  3. Rolle ≤ Gast **und** nicht WS-Admin **und** nicht Ersteller → 400 „You cannot edit intake issues“.
  4. Issue-Daten: Gäste nur `name`, `description_html`, `description_json` (Rest wird durch aktuelle Werte ersetzt); andere alle Felder (`allow_triage_state=True`).
  5. Intake-Felder (`status`, `duplicate_to`, `snoozed_till`, `source`) nur wenn Rolle > 15 (Admin) oder WS-Admin.
- Listen-Default `status=-2`: Der Client fragt den Tab „Open“ mit `status=-2` (bzw. Filter `-2`/`0` für Snoozed) und „Closed“ mit `status=1,-1,2` ab; Sortierung `±issue__created_at` (Default `-issue__created_at`), `±issue__updated_at`, `±issue__sequence_id`; weitere Filter als Legacy-CSV (`priority`, `labels`, `assignees`, `created_by`, `state`, Datumsfilter) (`apps/web/store/inbox/project-inbox.store.ts`).
- Löschen: nicht angenommene Intake-Issues löschen auch das Issue; angenommene nur den Intake-Eintrag.
- `IssueDetailIdentifierEndpoint` liefert `is_intake = true`, solange Status ∈ {-2, 0}.
- Gruppen-`count_filter` (3.1.5) zählt Issues mit Intake-Status ∈ {1, -1, 2} oder ohne Intake.

### 3.15 Cycles

#### 3.15.1 Status-Berechnung

`CURRENT` wenn `start_date ≤ jetzt ≤ end_date`; `UPCOMING` wenn `start_date > jetzt`; `COMPLETED` wenn `end_date < jetzt`; sonst `DRAFT`. „jetzt“ = aktuelle UTC-Zeit (die Projekt-TZ-Umrechnung im Code ist ein No-Op, da wieder in UTC zurückgerechnet). Ein Cycle mit nur einem Datum kann nicht entstehen (Y2), wohl aber über PATCH.

#### 3.15.2 Datumsumrechnung beim Schreiben (`CycleWriteSerializer.validate` → `convert_to_utc`, `apps/api/plane/utils/timezone_converter.py`)

Nur wenn **beide** Daten im Request gesetzt sind:
- `start_date`: Datum (Tag) in Projekt-TZ um 00:00 lokalisieren, +1 s; **wenn dieser Tag heute (Projekt-TZ) ist → aktuelle Zeit (UTC)**; sonst lokal 00:00:01 → UTC.
- `end_date`: Datum in Projekt-TZ um 23:59:00 → UTC.
- Vorherige Prüfung `start > end` erfolgt auf den Roh-Datetimes.
- Ausgabe in Listen/Detail: Rückumrechnung in Projekt-TZ (`user_timezone_converter(..., project.timezone)`).

#### 3.15.3 Date-Check (Y11)

Umrechnung wie 3.15.2; Konflikt, wenn ein anderer Cycle des Projekts (auch archiviert; gelöschte nicht) `[start, end]` überlappt: `(s ≤ start ≤ e) OR (s ≤ end ≤ e) OR (start ≤ s AND e ≤ end)`. Antwort bei Konflikt mit HTTP 200 und `status: false`.

#### 3.15.4 Issues zuordnen (Y8) / entfernen (Y10)

- Abgeschlossene Cycles (`end_date < now`) lehnen neue Issues ab.
- Ein Issue hat höchstens eine aktive `CycleIssue`: vorhandene Zuordnungen zu anderen Cycles werden umgehängt (Activity `updated_cycle_issues: [{old_cycle_id, new_cycle_id, issue_id}]`), neue angelegt (`created_cycle_issues` als Django-`serializers.serialize("json")`-String).
- Nicht im Projekt liegende IDs werden still ignoriert.

#### 3.15.5 Transfer (Y15, `transfer_cycle_issues`)

1. Ziel-Cycle laden; ist er abgeschlossen → Fehler. (Nicht gefunden → 500.)
2. Quell-Cycle mit Zählern (`total/completed/cancelled/started/unstarted/backlog_issues`; Zählung über `issue_cycle`-Zeilen, nicht distinct).
3. Wenn Projekt-Schätzung vom Typ `points`: Schätz-Verteilungen (Assignees/Labels mit `total/completed/pending_estimates`) und Burndown `points`.
4. Issue-Verteilungen (Assignees: `display_name, assignee_id, avatar_url, total_issues, completed_issues, pending_issues`; Labels: `label_name, color, label_id, …`) und Burndown `issues`.
5. `progress_snapshot` des **Quell**-Cycles wird (über)schrieben:
   ```json
   {"total_issues": n, "completed_issues": n, "cancelled_issues": n, "started_issues": n, "unstarted_issues": n, "backlog_issues": n,
    "distribution": {"labels": [...], "assignees": [...], "completion_chart": {...}},
    "estimate_distribution": {} | {"labels": [...], "assignees": [...], "completion_chart": {...}}}
   ```
6. Alle `CycleIssue` mit Issue nicht archiviert, kein Draft, State-Gruppe ∈ {backlog, unstarted, started} werden auf den Ziel-Cycle umgehängt (`bulk_update`). `completed`/`cancelled` bleiben.
7. Eine Activity `cycle.activity.created` mit `updated_cycle_issues`.

Ab jetzt liefern Y22 (Issue-Zahlen) und Y23 (komplette Analytics) die eingefrorenen Snapshot-Werte.

#### 3.15.6 Progress (Y22) und Analytics (Y23)

- Schätzpunkte: `SUM(CAST(estimate_point.value AS float))` je State-Gruppe für Issues mit Schätzung vom Typ `points` (immer live).
- Analytics `type=issues`: Assignee-Verteilung über Join `assignees` (ein Issue mit 2 Assignees zählt bei beiden; ohne Assignee → Eintrag mit `assignee_id=null`), `total_issues = COUNT(assignee_id …)` (zählt Nicht-Null-Werte, daher 0 für die Null-Zeile), `completed_issues` (`completed_at IS NOT NULL`), `pending_issues`; Labels analog; sortiert nach `display_name` bzw. `label_name`.
- `type=points`: nur wenn Projekt-Schätzung `points`; sonst leere Arrays und `{}`.
- Ohne Start-/Enddatum → 400.

#### 3.15.7 Burndown (`burndown_plot`, `apps/api/plane/utils/analytics_plot.py`)

```
dates = alle Tage von start_date.date() bis end_date.date() (inklusive)
für jeden Tag d:
  issues: verbleibend(d) = total_issues(cycle) − Anzahl Issues mit DATE(completed_at) ≤ d
  points: verbleibend(d) = Σ Schätzwerte aller geschätzten Cycle-Issues − Σ Schätzwerte mit DATE(completed_at) ≤ d
  d > heute (UTC-Datum) → null
```
`total_issues` stammt aus der Annotation des aufrufenden Querysets (Archiv-/Draft-/gelöschte Issues ausgeschlossen); die Erledigt-Zählung nutzt `issue_objects`. Module: identisch mit `start_date`/`target_date` (Date-Felder).

#### 3.15.8 Archivieren / Löschen

- Archivieren nur abgeschlossener Cycles (`end_date < now`); entfernt Favoriten **aller** Nutzer. Archivierte Cycles sind in Y1/Y3 unsichtbar und nicht editierbar (Y5).
- Löschen (Y6): Activity mit `issue_id = Cycle-ID` (der Activity-Task findet kein Issue und aktualisiert nichts, erzeugt aber Activities für die Issues aus `requested_data.issues`).

### 3.16 Modules

- Status-Werte: `backlog, planned (Default), in-progress, paused, completed, cancelled` – rein manuell, keine Ableitung aus Daten.
- Namen sind je Projekt eindeutig (DB-Constraint + Serializer-Prüfung, case-sensitive).
- Zähler (`total_issues`, `completed_issues`, …) über `issue_objects` (archivierte/Triage-Issues ausgeschlossen), Schätzpunkte nur Typ `points`.
- `member_ids`: über `ModuleMember` (aktiv); `lead_id` FK.
- `description_text`/`description_html` sind JSON-Felder (Legacy-Rich-Text), `description` Text.
- Mehrfachzugehörigkeit Issue ↔ Module erlaubt (`ModuleIssue`, eindeutig je aktivem Paar).
- Archivieren nur bei `status ∈ {completed, cancelled}`; Archivierte nicht editierbar.
- Burndown nur wenn `start_date` und `target_date` (und im aktiven Detail `total_issues > 0`).

### 3.17 Views

- `access`: `0 = private`, `1 = public` (**umgekehrt** zu Pages!). Im CE über diese Endpunkte **nicht änderbar** (read-only im Serializer) – Default `1`.
- `is_locked`: read-only im CE (kein Lock-Endpunkt) – gesperrte Views können nicht per PATCH geändert werden.
- `query` wird beim Speichern aus `filters` (Legacy-Format) per `issue_filters(..., "POST")` berechnet (Model-`save` und Serializer). Die eigentliche Filterung nutzt der Client über `rich_filters` (an I2/W13 durchgereicht).
- Sortierung beim Anlegen: `sort_order = MAX + 10000` (Projekt- bzw. Workspace-Views getrennt).
- Sichtbarkeit: eigene + public; Gäste ohne `guest_view_all_features` (Projekt) bzw. Workspace-Gäste nur eigene.

### 3.18 Pages

#### 3.18.1 `ProjectPagePermission`

```
anonym → 403
role = aktive ProjectMember-Rolle im URL-Projekt; keine → 403
wenn page_id im Pfad:
   page = Page(id, workspace, aktive ProjectPage-Verknüpfung zum URL-Projekt); keine → 403
   page.owned_by == user → ERLAUBT (jede Methode)
   role == GUEST und project.guest_view_all_features == False → 403
   page.access == PRIVATE → 403 (CE; EE-Hook _has_private_page_action_access für geteilte Pages)
Methodenmatrix (für Nicht-Owner bzw. ohne page_id):
   POST        → ADMIN, MEMBER
   GET/HEAD/OPTIONS → ADMIN, MEMBER, GUEST
   PUT/PATCH   → ADMIN, MEMBER
   DELETE      → ADMIN
   sonst       → 403
```

Wirkung: `DELETE …/lock/` (Unlock), `DELETE …/archive/` (Unarchive) und `DELETE …/pages/{id}/` nur für Admins **oder** Owner; Workspace-Admins ohne Projekt-Admin-Rolle haben **keinen** Bypass.

#### 3.18.2 Liste / Detail

- Nur **Root-Pages** (`parent IS NULL`) erscheinen in Liste, Summary und **Detail** (Kind-Pages sind im CE nicht direkt abrufbar – „Nested Pages“ ist ein Bezahl-Feature, siehe 5.6).
- Sichtbar: `owned_by = user OR access = 0`; nur Projekte mit aktiver Mitgliedschaft und nicht archiviert; Verknüpfung über `ProjectPage`.
- Annotationen: `is_favorite`, `label_ids` (aus `PageLabel`), `project_ids` (alle verknüpften Projekte).
- Archivierte Pages sind in der Liste enthalten (`archived_at` gesetzt); der Client trennt Tabs (Public/Private/Archived) selbst.

#### 3.18.3 Update / Lock / Access

- PATCH bei `is_locked` → 400. Zugriffsänderung nur Owner. `parent` muss eine Page desselben Projekts sein.
- Lock/Unlock ohne Owner-Prüfung (nur Permission-Matrix).
- `access`-Endpunkt (G13) setzt `access` auf den Body-Wert (Default 0) – auch wenn gleich.

#### 3.18.4 Archivieren (rekursiv)

```sql
WITH RECURSIVE descendants AS (
  SELECT id FROM pages WHERE id = :page_id
  UNION ALL
  SELECT pages.id FROM pages, descendants WHERE pages.parent_id = descendants.id
)
UPDATE pages SET archived_at = :value WHERE id IN (SELECT id FROM descendants);
```
`:value` = `datetime.now()` (naive Server-Lokalzeit; Spalte ist `DateField` → Datum). Beim Entarchivieren: hängt die Page aus einem archivierten Parent aus (`parent = None`), dann rekursiv `archived_at = NULL`. Favoriten aller Nutzer werden beim Archivieren gelöscht. Hinweis: Die Rekursion umfasst auch soft-gelöschte Kinder.

#### 3.18.5 Löschen

Nur archivierte Pages; Kinder werden abgehängt (`parent = None`, **nicht** gelöscht); Soft-Delete der Page (+ Kaskade: `ProjectPage`, `PageLabel`, `PageLog`, `PageVersion`).

#### 3.18.6 Beschreibung (Binary) und Versionen

- GET liefert das rohe Yjs-Update (`description_binary`, `BinaryField`).
- PATCH (vom Live-Server beim Speichern des Y.Doc, `apps/live/src/services/page/core.service.ts` `updateDescriptionBinary`): Base64 → Bytes, HTML sanitisiert, JSON direkt; gesperrt/archiviert → Fehlercodes 4701/4702.
- `track_page_version` (`apps/api/plane/bgtasks/page_version_task.py`): Version nur bei geändertem `description_html`; letzte Version desselben Nutzers ≤ 600 s → überschreiben, sonst neu; max. 20 Versionen (älteste gelöscht). **Achtung:** Der Task greift auf `page.description` zu, das am `Page`-Modell **nicht existiert** → `AttributeError`, abgefangen und geloggt → im CE werden über diesen Pfad **keine Page-Versionen erzeugt** (Bug). Für die Migration ist das *intendierte* Verhalten (Versionen mit `description_json = page.description_json`) umzusetzen.
- Versionen lesen: G16/G17; Wiederherstellen (`…/versions/{id}/restore/`) ruft der Client auf, existiert im CE-Backend aber nicht (EE).

#### 3.18.7 PageLog (`page_transaction`)

- Parst altes und neues HTML (BeautifulSoup) nach `<mention-component id entity_identifier entity_name entity_type>` und `<image-component id src>`.
- Neue Komponenten-IDs → `PageLog(transaction=id, entity_identifier, entity_name, entity_type)`; Bilder: `entity_name="image"`, `entity_identifier=src`; Mentions: `entity_name` aus Attribut (z. B. `user_mention`, `issue`).
- Entfernte IDs → `PageLog` gelöscht. Bei vorhandenen Logs werden bereits bekannte IDs übersprungen.
- G4 liefert `issue_ids` = alle `PageLog.entity_identifier` mit `entity_name="issue"`.

#### 3.18.8 Duplizieren

1. Zugriff: private fremde Page → 403.
2. Kopie per `pk=None; save()` (alle Felder inkl. `description_html`, `description_json`, `access`, `parent`, `is_locked`, `archived_at`, `view_props`, `logo_props`, `color`, `sort_order`), Name `"<name> (Copy)"`, `description_binary = None`, Owner/Ersteller = Nutzer.
3. Alle `ProjectPage`-Verknüpfungen der Quelle kopiert. Labels/Favoriten/Versionen nicht.
4. `page_transaction` für das HTML.
5. `copy_s3_objects_of_description_and_assets(entity_name="PAGE")`: alle `image-component`-Assets kopieren (neue `FileAsset`, Storage-Copy), `src`-IDs im HTML ersetzen, dann Live-Server `POST {LIVE_URL}/convert-document/` mit `{description_html, variant: "rich"}` → `description_json`, `description_binary` (Base64) setzen. **Bug:** übergibt als `project_id` die Schleifenvariable der letzten `ProjectPage`.

### 3.19 Favoriten, Recent Visits, User-Properties

- Favoriten (`UserFavorite`, `apps/api/plane/db/models/favorite.py`): `entity_type` ∈ {`cycle`, `module`, `view`, `page`} (+ `project` u. a. im Workspace-Bereich), `entity_identifier`, `project`, `user`; eindeutig je aktivem (`entity_type`, `entity_identifier`, `user`). Sichtbarkeitsprüfung beim Anlegen über `get_favorite_entities` (`apps/api/plane/app/serializers/favorite.py`: Projekt aktiv/Mitglied; private Pages/Views nur Owner; eingeschränkte Gäste nur eigene). Die Favoriten-Liste/Ordner liefert der Workspace-Bereich (`WorkspaceFavoriteEndpoint`).
- Recent Visits: `entity_name` ∈ {`project` (bei Issue-Listen), `issue`, `cycle`, `module`, `view`, `page`}; Upsert `visited_at`; bei 20 Einträgen wird der älteste (`created_at`) gelöscht (soft).
- User-Properties: Projekt (I10/I11), Cycle (Y16/Y17), Module (M18/M19) – je Nutzer ein Datensatz mit `filters` (Legacy, Default alle `None`), `display_filters` (Default `group_by: None, order_by: "-created_at", type: None, sub_issue: True, show_empty_groups: True, layout: "list", calendar_date_range: ""`), `display_properties` (Default alle 13 Eigenschaften `True`: `assignee, attachment_count, created_on, due_date, estimate, key, labels, link, priority, start_date, state, sub_issue_count, updated_on`), `rich_filters` (`{}`); Projekt zusätzlich `preferences` (`{"pages": {"block_display": True}, "navigation": {"default_tab": "work_items", "hide_in_more_menu": []}}`) und `sort_order`.

---

## 4. Abhängigkeiten zu anderen Bereichen

| Bereich | Art der Abhängigkeit | Konkrete Berührungspunkte |
|---|---|---|
| Datenmodell (Kern) – `migration/analysis/02a-datenmodell-kern.md` | Modelle, Manager, Constraints | `Issue`/`IssueManager`, `CycleIssue`, `ModuleIssue`, `Page`/`ProjectPage`, Soft-Delete-Mixins (`apps/api/plane/db/mixins.py`), `IssueSequence` + Advisory Lock |
| Projekte & Mitglieder (interne API Teil 1) | Rollen, Projekteinstellungen | `ProjectMember.role/is_active`, `Project.guest_view_all_features`, `Project.default_assignee_id`, `Project.timezone` (Cycles, Snooze), `Project.archived_at`, Feature-Toggles (`cycle_view`, `module_view`, `issue_views_view`, `page_view`, `intake_view` – schalten im Client die Bereiche frei; die Intake-Anlage passiert beim Aktivieren), `ProjectUserProperty` |
| Workspace | Favoriten, Recent Visits, Drafts, Workspace-Labels-Cache | `UserFavorite` (Liste/Ordner: `WorkspaceFavoriteEndpoint`), `UserRecentVisit` (Anzeige: `UserRecentVisitViewSet`), `WorkspaceDraftIssueViewSet`, `invalidate_cache("/api/workspaces/:slug/labels/")`, Profil-/„My Issues“-Listen nutzen `issue_group_values(user=…)` |
| States | Default-/Triage-State | `State.objects` vs. `State.triage_objects`, `default=True`; `completed_at`-Logik an State-Gruppe |
| Estimates | Schätzpunkte | `EstimatePoint.value` (String → Float-Cast), `Estimate.type == "points"` für Progress/Analytics/Burndown |
| Activity, Benachrichtigungen, E-Mail | Verlauf, Inbox, Mails | `apps/api/plane/bgtasks/issue_activities_task.py` (Feld-Tracker, Mentions, Subscriber-Autoanlage), `notification_task.py`, `email_notification_task.py` |
| Webhooks | Auslieferung | `model_activity` → `webhook_activity` (`apps/api/plane/bgtasks/webhook_task.py`) |
| Assets/Storage | Uploads, presigned URLs, Kopieren | `S3Storage` (`apps/api/plane/settings/storage.py`), `FileAsset`, `storage_metadata_task.py`, `copy_s3_object.py`, Asset-Endpunkte (`apps/api/plane/app/views/asset/v2.py`) für Beschreibungs-Bilder |
| Editor/Realtime – `migration/analysis/12-editor-echtzeit-live.md` | Page-Beschreibung | Live-Server lädt/speichert `pages/{id}/description/`, synchronisiert Titel via PATCH `pages/{id}/`, `convert-document` für Duplikate (`apps/live/src/services/page/*`) |
| Suche | Issue-/Page-Suche für Relationen, Sub-Issues, Mentions | `apps/api/plane/app/views/search/{base,issue}.py` |
| Public API v1 (`apps/api/plane/api/`) | parallele Implementierung derselben Fachobjekte | eigene Views/Serializer; teilt Modelle, Tasks (`ISSUE_ACTIVITY_MAPPER` enthält deren Feldnamen `parent`, `state`, `assignees`, `labels`) |
| Space/Public Boards (`apps/api/plane/space/`) | Kommentare `access=EXTERNAL`, Reaktionen, Votes | `IssueVote`, `IssuePublicSerializer` |
| Analytics/Export | gemeinsame Filter-/Gruppierungs-Utilities | `apps/api/plane/utils/analytics_plot.py` (`build_graph_plot`), `rich_filters` im Exporter |
| Automationen (Beat) | Auto-Archiv/Auto-Close, Unsnooze | `issue_automation_task.py`, Intake-Unsnooze (Index `intake_issue_snoozed_till_idx`) |
| Authentifizierung/Session | Cookie-Session, User-TZ | `BaseSessionAuthentication`, `User.user_timezone` |
| Web-Client (`apps/web`) | Stores/Services, Paginierungslogik | `apps/web/store/issue/**`, `apps/web/services/issue/**`, `apps/web/services/{cycle,module,view}*.ts`, `apps/web/services/page/*`, `apps/web/services/inbox/*`; Konstanten `packages/constants/src/issue/*`, Typen `packages/types/src/*` |

---

## 5. Migrationshinweise für .NET / EF Core / Angular

### 5.1 Vertragsstrategie (ADR-003)

| Kategorie | Empfehlung |
|---|---|
| Pfade | 1:1 inkl. abschließendem `/`, Aliase (`inboxes`, `inbox-issues`) und `{W}/work-items/{IDENT}-{SEQ}/` (ASP.NET-Route mit eigenem Constraint, da `-` Trennzeichen: Projekt-Identifier enthält kein `-`, Sequenz ist Integer, optional negativ). |
| JSON | `snake_case`, Feldnamen exakt wie in 2.16/2.17 inkl. `state__group`, `grouped_by`, `sub_grouped_by`; Gruppenschlüssel als Strings (`"None"`); Datumsfelder `YYYY-MM-DD`, Datetimes ISO 8601. |
| Fehlerkörper | wortgleich (2.20) – der Client wertet u. a. `error`, `error_code`, `message` aus (`apps/web/store/**`). |
| Statuscodes | wie Original (z. B. Y11 Konflikt mit 200, N7 mit 200, Y17/M19 mit 201). |
| Tote/defekte Routen (I7, K9, N2, N3, N4, Y4, Y9, Y12, Y24, M4, M10, M15, W4, W10, W14, C4, L4 ohne Client-Nutzung) | **nicht** portieren bzw. mit 405 beantworten; Ausnahme: N2 (Intake anlegen) korrekt implementieren, falls der Projekt-Bereich es benötigt. |
| Bugs mit fachlicher Wirkung | korrigieren und als bewusste Abweichung dokumentieren (Liste 5.3); Verhalten, auf das der Client sich verlässt, beibehalten. |

### 5.2 Umsetzung der Issue-Listen-Abfrage in EF Core 10 / Npgsql

1. **Basis-Query als wiederverwendbare Spezifikation**: `IQueryable<Issue> IssueObjects(this DbSet<Issue>)` = Soft-Delete (globaler Query-Filter `DeletedAt == null`) + `State == null || State.Group != Triage` + `ArchivedAt == null` + `!Project.ArchivedAt.HasValue` + `!IsDraft`. Für `Issue.objects`-Pfade (Detail, Archiv) ohne die drei letzten Bedingungen.
2. **Filter-AST**: Legacy-Parameter (2.18.1) und Rich-JSON (2.18.2) in **einen** gemeinsamen Ausdrucksbaum übersetzen (`Expression<Func<Issue,bool>>`), Relationen als `Any(...)` mit `DeletedAt == null`:
   - `label_id__in` → `i.IssueLabels.Any(l => l.DeletedAt == null && ids.Contains(l.LabelId))`
   - Legacy `labels=None` → `!i.IssueLabels.Any(l => l.DeletedAt == null)` (intendierte Semantik; siehe 5.3 Punkt 2)
   - `created_at` (Datum) → Vergleich auf `DateOnly` in **Nutzer-TZ**: `NpgsqlFunctions`/`AT TIME ZONE` via `EF.Functions` bzw. vorab berechnete UTC-Grenzen `[tagesbeginn_utc, tagesende_utc)` (bevorzugt, indexfreundlich).
   - Allowlist der Schlüssel und Strukturvalidierung inkl. identischer Fehlercodes (2.18.2).
3. **Sortierung**: Mapping-Tabelle 3.1.3 als `switch` mit `CASE`-Ausdrücken (`i.Priority == "urgent" ? 0 : …`); `NULLS LAST` über `OrderBy(x => x.Key == null).ThenBy(x => x.Key)`; Tiebreaker `CreatedAt DESC` und zusätzlich `Id` (Determinismus; Abweichung dokumentieren).
4. **Ungruppiert**: `Skip(page*limit).Take(limit+1)` + separates `CountAsync()` auf dem gefilterten Query.
5. **Gruppiert / untergruppiert**: EF Core übersetzt `ROW_NUMBER() OVER (PARTITION BY …)` nicht nativ. Empfohlen: SQL-Baustein mit CTE (Npgsql `FromSql` mit interpoliertem, aber **allowlist-geprüftem** Gruppenausdruck) der nur `(issue_id, group_key, sub_group_key, rn)` liefert; danach Projektion der Issue-Felder per EF (`WHERE id = ANY(@ids)`) und In-Memory-Gruppierung wie `process_results`. Alternativ `linq2db.EntityFrameworkCore` (Window-Funktionen). Gruppenschlüssel für M2M über `LEFT JOIN issue_labels … WHERE deleted_at IS NULL` (eine Zeile pro aktiver Zuordnung, `NULL` → `"None"`).
6. **Gruppensummen**: `COUNT(DISTINCT i.id) FILTER (WHERE count_filter)` je Gruppenausdruck; `count_filter` exakt aus 3.1.5. Entscheidung zum 0→1-Quirk siehe 6.
7. **ID-Arrays**: Npgsql `EF.Functions.ArrayAgg(...)` bzw. Projektion `i.IssueAssignees.Where(a => a.DeletedAt == null).Select(a => a.AssigneeId).ToArray()` (korrelierte Subquery); für 1 000 Zeilen Split-Query vermeiden → eine zweite Abfrage `issue_id → ids` und Merge im Speicher.
8. **Zähler**: `link_count`, `attachment_count`, `sub_issues_count` als korrelierte `Count()`-Subqueries (EF liefert 0, nicht `null` → siehe 6).
9. **Gast-Filter** und Rechte-Subqueries (3.1.9) als Policy-Filter vor Zählung/Paginierung.
10. **Cursor/Envelope**: Formate exakt (2.17.2/2.17.3), inkl. `prev_cursor` mit `page-1` (auch `-1`).
11. **Performance**: Indizes auf `issues(project_id, deleted_at, archived_at, is_draft)`, `issue_labels(issue_id, deleted_at)`, `issue_assignees(issue_id, deleted_at)`, `cycle_issues(issue_id, deleted_at)`, `module_issues(issue_id, deleted_at)`, `issues(parent_id)`; Antwortkompression (`ResponseCompression` mit gzip) für Listen.

### 5.3 Fallstricke (Original-Verhalten, das leicht falsch nachgebaut wird)

1. **Mehrfachzeilen durch Joins**: Django-`filter()` über M2M erzeugt Joins; `labels__id` (über `labels`) und `label_issue__deleted_at` (über `label_issue`) sind **verschiedene** Join-Pfade auf `issue_labels` → potenzielle Zeilenvervielfachung und Einbeziehung soft-gelöschter Label-Zuordnungen in der Gruppierung. Intendierte Semantik nachbauen (eine Zeile je aktiver Zuordnung) und Abweichung im Contract-Test berücksichtigen.
2. **Legacy-`None`-Filter** (`labels=None`, `cycle=None`, `module=None`, `assignees=None`) prüfen im Original `isnull` **und** `deleted_at IS NULL` auf demselben LEFT JOIN → Issues, deren einzige Zuordnung soft-gelöscht ist, fallen heraus. Intendiert: „keine aktive Zuordnung“.
3. **`priority`-Sortierung** ist über Text-CASE gelöst; aufsteigend „priority“ ergibt none→urgent, das UI nutzt nur `-priority` (urgent→none).
4. **`-state__group`** liefert praktisch dieselbe Gruppenreihenfolge wie aufsteigend (nur Nicht-Standard-Gruppen zuerst).
5. **Leere Gruppen**: Bei Nicht-M2M-Gruppierung immer alle Gruppen aus `issue_group_values` (auch leer, mit `total_results` 0); bei M2M nur Gruppen mit Treffern auf der Seite. Der Client zeigt leere Gruppen über `show_empty_groups` und eigene Stammdaten (States, Labels, Mitglieder) an – beide Formen müssen akzeptiert werden.
6. **`total_results` 0→1-Quirk** in Gruppen-Summen (3.1.5).
7. **Seitengröße in Gruppen** stammt aus `cursor.value`, nicht aus `per_page` (Client sendet konsistent).
8. **`total_count` bei M2M-Gruppierung** zählt (Issue, Wert)-Paare.
9. **`state_id`-Gruppenwerte** enthalten keine Triage-States; Issues ohne State fallen aus der Gruppierung.
10. **Datumsfilter** „heute“ = UTC-Datum; `__date`-Vergleiche in Nutzer-TZ (`TimezoneMixin`).
11. **Cycle-Daten**: Start heute → aktuelle Uhrzeit; Ende 23:59 lokal; Ausgabe in Projekt-TZ; Status gegen UTC-Jetzt.
12. **Completed-Cycle-Edit**: Original speichert bei enthaltenem `sort_order` alle Felder (Bug) – fachlich korrekt: nur `sort_order`.
13. **Bulk-Operationen** umgehen Model-Logik (`completed_at`, `updated_by`, `workspace`), Bulk-Delete ohne Kaskade/Activity.
14. **Advisory Lock** für `sequence_id` (pro Projekt serialisiert); in .NET: `SELECT pg_advisory_xact_lock(hash)` in derselben Transaktion oder Sequenztabelle mit `UPDATE … RETURNING`.
15. **`sort_order` neuer Issues** = Max je (Projekt, State) + 10 000; Cycles/Modules = Min − 10 000 (neue oben); Labels/Views = Max + 10 000.
16. **Relationen**: `implements` wird nicht invertiert gespeichert (Bug); `implemented_by` fehlt in der Listenantwort.
17. **Page-Zugriff**: `access` 0 = public (Pages) vs. Views 1 = public.
18. **Page-Archiv** ist rekursiv; Löschen hängt Kinder ab (nicht rekursiv löschen).
19. **Intake-Pfad-ID** ist die Issue-ID; Löschen eines nicht angenommenen Intake-Eintrags löscht das Issue mit.
20. **`fields`-Parameter** filtert nicht (DynamicBaseSerializer verwirft ihn).
21. **`sub_issues_count` u. a.** können `null` sein (Original); Client behandelt `null` wie 0.
22. **`history`-Merge** sortiert per String-Vergleich der ISO-Zeitstempel (gleiche Formatierung nötig).
23. **Zeitzonen**: IANA-Namen aus pytz (`Project.timezone`, `User.user_timezone`) – in .NET `TimeZoneInfo.FindSystemTimeZoneById` (Linux/ICU) oder NodaTime; tzdata im Container bündeln (ADR-004).

### 5.4 Sicherheit (nicht 1:1 übernehmen)

Die folgenden Original-Routen prüfen keine oder unzureichende Rechte; in .NET mit expliziter Policy absichern oder entfernen:

| Route | Problem | Empfehlung |
|---|---|---|
| I7 `PUT issues/{pk}/` | nur Login | entfernen oder wie I8 |
| C3/C4 `GET/PUT comments/{pk}/` | PUT umgeht Ersteller-Prüfung | GET mit `AP[A,M,G]`, PUT entfernen |
| C7, C10 Reaktions-Listen | nur Login + Queryset | `AP[A,M,G]` |
| N3/N4 `intakes/{pk}/` | nur Login, kein Mitgliedsfilter | `AP[A]` (Admin) |
| Y4 `PUT cycles/{pk}/` | Gäste könnten ändern | entfernen |
| M4 `PUT modules/{pk}/` | nur Login, kein Mitgliedsfilter | entfernen |
| W2/W8 `POST views/` | nur Login (Projekt/Workspace beliebig) | `AP[A,M]` bzw. `APW[A,M]` |
| W4/W10 `PUT views/{pk}/` | umgeht Lock/Owner | entfernen |
| W9 `GET {W}/views/{pk}/` | kein Mitgliedschaftscheck | `APW[A,M,G]` + Sichtbarkeit |
| L1 Label-Liste | Projektmitgliedschaft ohne `is_active` | aktive Mitgliedschaft |
| G3/G5 `labels` an Pages | beliebige Label-IDs (auch fremde Projekte) | auf Projekt-Labels einschränken |

Beibehalten: alle `issue_in_project`-/Workspace-/Projekt-Bindungen (IDOR-Schutz, GHSA-Kommentare im Code), `ISSUE_GROUP_BY_ALLOWLIST`/Order-Allowlists, `writable_data` (keine read-only Felder in Activities), SSRF-Schutz des Link-Crawlers, HTML-Sanitizing (in .NET z. B. `HtmlSanitizer` mit identischer Tag-/Attribut-Allowlist aus `apps/api/plane/utils/content_validator.py`).

### 5.5 Hintergrundverarbeitung

- Celery-Tasks (`issue_activity`, `model_activity`/`webhook_activity`, `notifications`, `issue_description_version_task`, `recent_visited_task`, `page_transaction`, `track_page_version`, `crawl_work_item_link_title`, `copy_s3_objects_of_description_and_assets`, `get_asset_object_metadata`, `soft_delete_related_objects`) → .NET: Transactional Outbox in PostgreSQL + `BackgroundService`-Worker (ohne externe Broker, ADR-004); als eigenes Aspire-Projekt („worker“) skalierbar.
- Empfehlung: `IssueActivity`-Zeilen **synchron in derselben Transaktion** erzeugen (keine Race Conditions mit `current_instance`-Snapshots), Benachrichtigungen/Webhooks/E-Mails asynchron.
- `origin` in Redis (600 s) dient nur E-Mail-Links → als Spalte im Outbox-Eintrag speichern.
- Kaskaden-Soft-Delete deterministisch im selben Request (EF: explizite Domain-Logik je Aggregat) statt generischer Reflection.

### 5.6 Bezahl-Funktionen in diesem Bereich (ADR-001: immer aktiv)

Belege im CE-Code, wo Bezahl-Editionen andocken bzw. der Client Endpunkte erwartet, die das CE-Backend nicht hat. Die fachliche Spezifikation dieser Funktionen gehört in das Analyse-Dokument der Bezahl-Features; hier die Schnittstellenpunkte:

| Funktion | Beleg im CE | Benötigte Endpunkte / Erweiterung |
|---|---|---|
| Work-Item-Abhängigkeiten im Gantt (start/finish before/after) | `ENABLE_ISSUE_DEPENDENCIES = false` (`packages/constants/src/issue/filter.ts`); Relationstypen bereits im Backend (3.7) | I4 mit `expand=issue_relation,issue_related`; UI aktivieren |
| Relationstyp „implemented by / implements“ | `IssueRelationChoices.IMPLEMENTED_BY`, Mapping in `apps/api/plane/utils/issue_relation_mapper.py` | R1 um Schlüssel `implemented_by`/`implements` erweitern; Richtungs-Bug korrigieren |
| Epics / Work-Item-Typen | `Issue.type` (FK `IssueType`), `type__is_epic` in A1; Client `EIssueServiceType.EPICS` (`/epics/…`, `…/epics/{id}/issues/`, `…/links/`) | komplette Epic-Endpunktfamilie analog `issues` |
| Benutzerdefinierte Eigenschaften in Filtern | Hook `ComplexFilterBackend._preprocess_leaf_conditions` (Kommentar „customproperty_<id>__<lookup>“) | Rich-Filter-Erweiterung |
| Geteilte private Pages / erweiterte Page-Rechte | Hook `ProjectPagePermission._has_private_page_action_access`, `_check_access_and_get_role` | Page-Sharing-Modell + Endpunkte |
| Verschachtelte Pages | `Page.parent`, `PageVersion.sub_pages_data`, Root-Filter `parent IS NULL` in G2/G4 | Kind-Pages abrufbar machen |
| Page verschieben | Client `POST {P}/pages/{id}/move/` (`apps/web/services/page/project-page.service.ts`) | neuer Endpunkt |
| Page-Version wiederherstellen | Client `POST {P}/pages/{id}/versions/{vid}/restore/` (`apps/web/services/page/project-page-version.service.ts`) | neuer Endpunkt |
| Archivierte Pages / Favoriten-Liste | Client `GET {P}/archived-pages/`, `GET {P}/favorite-pages/` | neue Endpunkte (oder Client auf G2 umstellen) |
| Page-Mentions für Live-Server | Live `GET {P}/pages/{id}/mentions/?mention_type=user_mention` (`apps/live/src/services/page/core.service.ts`) | neuer Endpunkt (bzw. in-process im .NET-Realtime) |
| Bulk-Operationen (Mehrfachauswahl im Spreadsheet) | Client `POST {P}/bulk-operation-issues/` | neuer Endpunkt |
| Bulk-Abonnieren | Client `POST {P}/bulk-subscribe-issues/` | neuer Endpunkt |
| Relation per ID löschen | Client `DELETE …/issue-relation/{relationId}/` (`apps/web/services/issue/issue.service.ts`) | neuer Endpunkt (CE nutzt R3) |
| Projekt-View-Issues direkt | Client `GET {P}/views/{id}/issues/` (`apps/web/services/view.service.ts`) | neuer Endpunkt (CE-UI nutzt I2) |
| Cycle-Fortschritt erweitert / Workspace Active Cycles | Client `…/cycles/{id}/cycle-progress/`, `{W}/active-cycles/` | neue Endpunkte |
| View sperren / Zugriff ändern / veröffentlichen | `IssueView.is_locked`, `access` read-only im CE-Serializer | Lock-/Access-/Publish-Endpunkte |
| Intake-Quellen (E-Mail, Formulare) | `SourceType` nur `IN_APP`, Felder `source_email`, `extra` | Intake-Kanäle |
| Display-Properties-Endpunkt | Client `GET/POST {P}/issue-display-properties/` | Altlast; I10/I11 decken das ab – Client-Aufrufer prüfen |

### 5.7 Angular-Hinweise

- Services und MobX-Stores des Originals (`apps/web/store/issue/helpers/base-issues.store.ts`, `issue-filter-helper.store.ts`) sind die Referenz für Request-Aufbau (Cursor-Konstruktion, Gruppenfilter beim „Mehr laden“, `layout`/`sub_issue`-Parameter) und Antwortverarbeitung (`ALL_ISSUES`, `groupedIssueCount`). In Angular als Signal-Stores/Services 1:1 nachbilden.
- Seitengrößen je Layout (2.18.5) beibehalten (beeinflusst sichtbares Ladeverhalten → 1:1-UI).
- Optimistische Updates des Originals (z. B. Relationen, Reaktionen, Sub-Issues) setzen die hier dokumentierten Antwortformen voraus (z. B. R2 liefert Liste mit `relation_type`, R5 `state_distribution`).
- Upload-Flow v2 (3.12) mit presigned POST bleibt clientseitig identisch; Storage in airgapped Umgebungen: S3-kompatibel (MinIO) über Aspire-Ressource.

### 5.8 Tests

- Contract-Tests je Endpunkt (Statuscode, Body-Shape, Fehlertexte) gegen das Original-Repo als Orakel; Datenbank-Fixtures für Rollen (Admin/Member/Guest, WS-Admin, Nicht-Mitglied) und `guest_view_all_features` an/aus.
- Property-basierte Tests der Listen-Abfrage (zufällige Filterbäume, `group_by`×`sub_group_by`×`order_by`, Seitenwechsel) mit Vergleich der ID-Mengen je Gruppe gegen das Original (unter Berücksichtigung der dokumentierten Abweichungen 5.3).
- Zeitzonen-Tests (Cycles, Snooze, `created_at`-Datumsfilter) für mindestens UTC, `Europe/Berlin`, `America/Los_Angeles`, `Asia/Kolkata`.

---

## 6. Offene Punkte

| # | Frage | Kontext / Vorschlag |
|---|---|---|
| O1 | `sub_issues_count`/`link_count`/`attachment_count`: `null` (Original) oder `0` ausliefern? | Vorschlag `0`; Client-Kompatibilität bei Portierung der Stores prüfen |
| O2 | 0→1-Quirk der Gruppensummen und fehlende leere M2M-Gruppen: bug-kompatibel oder korrigiert? | Vorschlag: korrigieren (echte 0, alle Gruppen) – UI-Effekt (Zähler-Badges) prüfen |
| O3 | Deterministische Sortierung (`id` als zusätzlicher Tiebreaker) zulässig? | Vorschlag: ja |
| O4 | Page-Versionierung: Original erzeugt wegen `page.description`-Bug keine Versionen. Intendiertes Verhalten (≤ 600 s Merge, max. 20) umsetzen? Limit unter ADR-001 konfigurierbar? | Vorschlag: umsetzen, Limit als Instanz-Einstellung |
| O5 | `IssueVersion` (Eigenschafts-Historie): im CE nur Backfill. Bei jeder Änderung versionieren (wie vermutlich in Bezahl-Editionen)? | Spezifikation aus Bezahl-Feature-Analyse abwarten |
| O6 | Subscriber-Liste S1 liefert alle Projektmitglieder statt Subscriber; `issue-subscribers/` (S1–S3) wird von `apps/web`/`packages` **nicht** aufgerufen (nur `subscribe/`, S4–S6) | Vorschlag: S1–S3 nur portieren, wenn Bezahl-Features sie benötigen (z. B. Subscriber verwalten) – dann mit echter Subscriber-Liste |
| O7 | Intake anlegen (N2) ist defekt; wie entsteht das Intake? | Beim Aktivieren von `intake_view` legt `ProjectViewSet.partial_update` ein Default-Intake `"{project.name} Intake"` (`is_default=True`) an (`apps/api/plane/app/views/project/base.py`). N2 daher nicht portieren, außer für Mehrfach-Intakes (Bezahl-Feature?) |
| O8 | Unterstützung des Legacy-Filterformats insgesamt beibehalten? | Notwendig, da Client für Cycle/Module/„Mehr laden“ Legacy-Parameter nutzt; `logged_by` streichen |
| O9 | Sollen `or`/`not` im Rich-Filter weiterhin unterstützt werden? | Server unterstützt; CE-UI nutzt nur `and`; Bezahl-UI evtl. mehr – beibehalten |
| O10 | Datumsfilter „heute“ in UTC oder Nutzer-TZ? | Original UTC; Vorschlag Nutzer-TZ (dokumentierte Abweichung) |
| O11 | Bug `implements` (keine Richtungsumkehr) korrigieren? | Vorschlag: korrigieren, mit EE-Spezifikation abgleichen |
| O12 | `PUT`-Routen ersatzlos entfernen? | Vorschlag: ja (kein Client-Aufruf gefunden) |
| O13 | Kalender-„Mehr laden“ nutzt `target_date=YYYY-MM-DD` → `__contains`; exakte Gleichheit implementieren? | Vorschlag: Gleichheit |
| O14 | Archiv-Detail A2 liefert weniger Felder als I6 – angleichen? | Vorschlag: angleichen (Client lädt Archiv-Detail über A2) |
| O15 | Page-Duplikat: `project_id`-Schleifenvariable und Labels nicht kopiert – Original-Verhalten? | Vorschlag: Assets im Quellprojekt kopieren, Labels übernehmen (EE prüfen) |
| O16 | Rekursives Page-Archiv berücksichtigt soft-gelöschte Kinder – beibehalten? | Vorschlag: nur aktive Kinder |
| O17 | `archived_at` der Page-Archiv-Antwort ist naive Server-Lokalzeit – Format? | Vorschlag: ISO-Datum (`YYYY-MM-DD`) wie gespeichert |
| O18 | Legacy-Flag `Issue.is_draft` (neben `DraftIssue`) im Greenfield-Schema behalten? | Vorschlag: entfernen, Filter/Count-Filter entsprechend vereinfachen; Client-Felder `is_draft=false` weiter ausliefern |
| O19 | Zuordnungen auf soft-gelöschte Labels/Nutzer in `label_ids`/`assignee_ids` ausblenden? | Original blendet nur gelöschte Zwischenzeilen aus; Vorschlag: auch gelöschte Ziele ausblenden |
| O20 | Detaillierte Feldsemantik der Activity-Erzeugung (welche `IssueActivity`-Zeilen pro Feldänderung) | gehört zum Activity/Notification-Analysedokument; dieses Dokument referenziert nur die Auslöser |
