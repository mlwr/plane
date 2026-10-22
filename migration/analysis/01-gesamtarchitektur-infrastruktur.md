# A01 – Gesamtarchitektur & Infrastruktur (IST-Analyse)

> **Status:** IST-Analyse (Plane v1.4.2 Community Edition, Repo-Stand dieses Workspaces, `package.json` → `"version": "1.4.2"`)
> **Bindende Leitplanken:** `migration/architecture/00-grundsatzentscheidungen.md` (ADR-000 … ADR-006)
> **Analysierte Quellen (gelesen):** `package.json`, `pnpm-workspace.yaml`, `turbo.json`, `.npmrc`, `.node-version`, `.mise.toml`, `.oxlintrc.json`, `.oxfmtrc.json`, `.dockerignore`, `.gitattributes`, `.prettierignore`, `.trivyignore`, `.husky/pre-commit`, `CODEOWNERS`, `AGENTS.md`, `CONTRIBUTING.md`, `README.md`, `.env.example`, `setup.sh`, `docker-compose.yml`, `docker-compose-local.yml`, `docker-compose-test.yml`, alle Dateien unter `deployments/` (`aio/community/*`, `cli/community/*`, `kubernetes/community/README.md`, `swarm/community/swarm.sh`), `apps/proxy/*`, alle `Dockerfile*` unter `apps/*`, alle `apps/*/.env.example`, `apps/web|admin/caddy/Caddyfile`, `apps/space/nginx/nginx.conf`, `apps/*/package.json`, `apps/*/vite.config.ts`, `apps/*/react-router.config.ts`, `apps/api/pyproject.toml`, `apps/api/pytest.ini`, `apps/api/ruff.toml`, `apps/api/run_tests.py`, `apps/api/run_tests.sh`, `apps/api/bin/*`, `apps/api/plane/settings/*.py` (alle 8), `apps/api/plane/celery.py`, `apps/api/plane/__init__.py`, `apps/api/plane/urls.py`, `apps/api/plane/asgi.py`, `apps/api/plane/wsgi.py`, `apps/api/manage.py`, `apps/api/plane/middleware/*`, `apps/api/plane/authentication/middleware/session.py`, `apps/api/plane/authentication/session.py`, `apps/api/plane/authentication/rate_limit.py`, `apps/api/plane/authentication/utils/host.py`, `apps/api/plane/api/rate_limit.py`, `apps/api/plane/api/views/base.py`, `apps/api/plane/api/middleware/api_authentication.py`, `apps/api/plane/throttles/asset.py`, `apps/api/plane/utils/core/*`, `apps/api/plane/utils/cache.py`, `apps/api/plane/utils/ip_address.py`, `apps/api/plane/utils/logging.py`, `apps/api/plane/utils/exception_logger.py`, `apps/api/plane/utils/otlp_endpoints.py`, `apps/api/plane/utils/instance_config_variables/*`, `apps/api/plane/license/utils/*`, `apps/api/plane/license/bgtasks/telemetry_metrics.py`, `apps/api/plane/license/management/commands/*`, `apps/api/plane/db/management/commands/{wait_for_db,wait_for_migrations,create_bucket,clear_cache}.py`, `apps/api/plane/db/models/session.py`, `apps/api/plane/license/api/views/instance.py` (GET-Konfig), `apps/api/plane/web/*`, `apps/api/plane/bgtasks/{cleanup_task,logger_task,copy_s3_object,email_notification_task}.py` (Infrastruktur-Teile), `apps/api/plane/tests/**` (Konfig + Inventar aller 113 Testdateien), `apps/api/tests/RUNNING_TESTS.md`, `apps/api/docs/django-5.2-migration-plan.md`, `apps/live/src/{env,start,server,hocuspocus,redis}.ts`, `apps/live/src/controllers/*`, `apps/live/src/lib/{auth,auth-middleware}.ts`, `apps/live/src/extensions/{index,redis}.ts`, `apps/live/src/services/**` (Endpunkt-Aufrufe), `apps/live/{vitest,tsdown}.config.ts`, `apps/live/tests/**`, `packages/*/package.json`, `packages/constants/src/endpoints.ts`, `packages/services/src/{api.service,live.service}.ts`, `packages/services/src/helpers/url.ts`, `packages/logger/src/*`, `packages/blocks/vitest.config.ts`, alle 10 Workflows unter `.github/workflows/`, `.github/instructions/*`, `.github/ISSUE_TEMPLATE/*`, `.github/pull_request_template.md`, `docs/linting.md`, `package.json` von `@makeplane/propel@0.7.3` (nur gelesen).
> Alle Pfade relativ zum Repo-Root. Abkürzungen: `API/` = `apps/api/plane/`, `LIVE/` = `apps/live/src/`, `DEP/` = `deployments/`.

---

## Inhaltsverzeichnis

1. Überblick & Verantwortlichkeiten
   - 1.1 Zweck des Bereichs
   - 1.2 Komponentendiagramm (Mermaid)
   - 1.3 Zentrale Kommunikationsflüsse (Mermaid-Sequenzen)
   - 1.4 Verantwortlichkeiten je Komponente
2. Vollständige Inventare
   - 2.1 Monorepo-Aufbau (Root-Dateien, Workspace, Scripts, Turbo-Tasks, pnpm-Einstellungen)
   - 2.2 Apps-Inventar
   - 2.3 Packages-Inventar
   - 2.4 pnpm-Catalog (alle Versionen) + Overrides
   - 2.5 Python-Abhängigkeiten (`apps/api/pyproject.toml`)
   - 2.6 Service-/Container-Tabelle (alle Compose-/Deployment-Varianten)
   - 2.7 Ports & Base-Paths (Dev / Docker / AIO)
   - 2.8 Proxy-Routing-Regeln (alle Caddy-/nginx-Konfigurationen)
   - 2.9 Dockerfiles
   - 2.10 Entrypoint-Skripte & Start-Kommandos
   - 2.11 Vollständige ENV-Tabelle
   - 2.12 Django-Settings ohne ENV-Bezug (Konstanten)
   - 2.13 Middleware-Kette (API)
   - 2.14 Authentifizierungsklassen je URL-Bereich
   - 2.15 Rate-Limits / Throttles
   - 2.16 Cookies & Sessions
   - 2.17 Celery: Broker, Konfiguration, Beat-Schedule, Task-Inventar
   - 2.18 Redis-/Cache-Nutzung
   - 2.19 Objektspeicher (S3/MinIO)
   - 2.20 OpenAPI (drf-spectacular)
   - 2.21 Top-Level-URL-Routing des API-Servers
   - 2.22 Live-Server (Realtime) – Infrastrukturschnittstellen
   - 2.23 Logging & Telemetrie
   - 2.24 CI-Pipeline (GitHub Actions)
   - 2.25 Test-Infrastruktur
   - 2.26 Deployment-Varianten & Betriebsskripte
   - 2.27 Laufzeitabhängigkeiten (Versionen)
   - 2.28 Externe Netzwerkziele (Airgapped-Relevanz)
   - 2.29 Dokumentation & Repo-Metadaten
3. Verhalten / Logik / Abläufe im Detail (inkl. Edge-Cases)
4. Abhängigkeiten zu anderen Bereichen
5. Migrationshinweise für .NET / EF Core / Angular
6. Offene Punkte

---

## 1. Überblick & Verantwortlichkeiten

### 1.1 Zweck des Bereichs

Plane ist ein **pnpm/Turbo-Monorepo** (`pnpm-workspace.yaml`, `turbo.json`) mit sechs Anwendungen unter `apps/` und 14 Paketen unter `packages/`. Laufzeitseitig besteht eine Installation aus:

- **API-Server** `apps/api` (Django 5.2.17 + DRF 3.17.2, ASGI via gunicorn+uvicorn) – einziger Python-Dienst; liefert REST unter `/api/`, `/api/public/`, `/api/instances/`, `/api/v1/`, Auth-Flows unter `/auth/`, Django-Static unter `/static/` (WhiteNoise) und den Health-Check unter `/` (`API/urls.py`, `API/web/urls.py`).
- **Worker** und **Beat-Worker** – derselbe Container-Code wie die API, aber mit `celery -A plane worker` bzw. `celery -A plane beat` (`apps/api/bin/docker-entrypoint-worker.sh`, `apps/api/bin/docker-entrypoint-beat.sh`).
- **Migrator** – einmaliger Job `python manage.py migrate` (`apps/api/bin/docker-entrypoint-migrator.sh`).
- **web** (`apps/web`) – Haupt-SPA (React 19 + React Router 8, `ssr: false`), statisch per Caddy ausgeliefert (`apps/web/react-router.config.ts`, `apps/web/Dockerfile.web`).
- **admin** (`apps/admin`) – „God-Mode“-SPA unter `/god-mode` (`ssr: false`, `basename` aus `VITE_ADMIN_BASE_PATH`), statisch per Caddy (`apps/admin/react-router.config.ts`, `apps/admin/Dockerfile.admin`).
- **space** (`apps/space`) – öffentliche Boards unter `/spaces` mit **SSR** (`ssr: true`) über `react-router-serve` (Node) (`apps/space/react-router.config.ts`, `apps/space/Dockerfile.space`).
- **live** (`apps/live`) – Node/Express + Hocuspocus 2.15.2 (Yjs) unter `/live` für kollaboratives Editieren von Seiten, plus HTML→Yjs-Konvertierung und PDF-Export (`LIVE/server.ts`, `LIVE/controllers/*`).
- **proxy** (`apps/proxy`) – Caddy 2.11 (Custom-Build) als Reverse-Proxy/TLS-Terminator auf Port 80/443 mit pfadbasiertem Routing (`apps/proxy/Caddyfile.ce`).
- **Infrastrukturdienste:** PostgreSQL 15.7, Valkey 7.2.11 (Redis-kompatibel), RabbitMQ 3.13.6 (Celery-Broker), S3-kompatibler Objektspeicher „silo“ (MinIO-Fork, Image `docker.io/pgsty/silo:RELEASE.2026-09-16T00-00-00Z`) (`docker-compose.yml`).

Dieser Bereich (A01) beschreibt Aufbau, Konfiguration, Verkabelung, Betrieb, Build/CI und Test-Infrastruktur dieser Komponenten. Fachlogik (Auth-Flows, Work Items, Seiten, …) ist in den jeweiligen Fachbereichs-Analysen beschrieben; hier werden nur die infrastrukturellen Schnittstellen dazu inventarisiert.

**Edition:** Das Repo ist ausschließlich die Community Edition. Infrastrukturseitig gibt es **keine** Bezahl-Komponenten im Code; Bezahl-Editionen werden nur referenziert: `deployments/cli/community/restore-airgapped.sh` (Restore für „Plane Commercial Air-Gapped“, erwartet `~/planeairgapped/docker-compose.yml` und Datenordner `data/{db,redis,minio/uploads,mq}`), `deployments/cli/community/README.md` (Abschnitt „Restore for Commercial Air-Gapped“), Beispiel-Hostname `silo` in `API/settings/common.py` (Kommentar zu `WEBHOOK_ALLOWED_HOSTS`; „Silo“ ist Planes Integrationsdienst der kommerziellen Editionen), `Instance.edition` mit einzigem Enum-Wert `PLANE_COMMUNITY` (`API/license/models/instance.py`), `MARKETING_PLANE_ONE_PAGE_LINK`/`MARKETING_PRICING_PAGE_LINK` (`packages/constants/src/endpoints.ts`). Gemäß ADR-001 entfällt jede Editions-/Lizenzunterscheidung.

### 1.2 Komponentendiagramm (Mermaid)

Produktionsaufbau gemäß `deployments/cli/community/docker-compose.yml` (kanonische Self-Hosting-Variante) und `apps/proxy/Caddyfile.ce`:

```mermaid
flowchart LR
  subgraph Browser["Browser"]
    WEBSPA["web SPA (React Router, ssr:false) Pfad /"]
    ADMINSPA["admin SPA (God-Mode) Pfad /god-mode/"]
    SPACEUI["space (SSR-Hydration) Pfad /spaces/"]
  end

  PROXY["proxy: Caddy 2.11 (Custom-Build)<br/>:80 / :443, ACME, request_body max_size=FILE_SIZE_LIMIT"]

  subgraph Frontends["Frontend-Container"]
    WEB["web: Caddy :3000<br/>statische Dateien /usr/share/caddy/html<br/>SPA-Fallback /index.html, rate_limit 300/min/IP"]
    ADMIN["admin: Caddy :3000<br/>statisch unter /god-mode<br/>Fallback /god-mode/index.html"]
    SPACE["space: Node react-router-serve :3000<br/>SSR, basename /spaces"]
  end

  subgraph Backend["Backend (ein Image makeplane/plane-backend)"]
    API["api: gunicorn -k uvicorn.workers.UvicornWorker :8000<br/>Django 5.2 + DRF, WhiteNoise /static"]
    WORKER["worker: celery -A plane worker"]
    BEAT["beat-worker: celery -A plane beat<br/>DatabaseScheduler"]
    MIGRATOR["migrator: manage.py migrate (einmalig)"]
  end

  LIVE["live: Node Express + Hocuspocus :3000<br/>Basis /live, WS /live/collaboration"]

  subgraph Infra["Infrastruktur"]
    PG[("plane-db: PostgreSQL 15.7<br/>max_connections=1000")]
    REDIS[("plane-redis: Valkey 7.2.11")]
    MQ[("plane-mq: RabbitMQ 3.13.6<br/>AMQP 5672")]
    S3[("plane-minio: silo (MinIO-Fork)<br/>S3 :9000, Konsole :9090<br/>Bucket 'uploads'")]
  end

  EXT["Externe Dienste (optional)<br/>SMTP, OAuth (Google/GitHub/GitLab/Gitea),<br/>LLM (OpenAI/Anthropic/Gemini), Unsplash,<br/>telemetry.plane.so, api.github.com"]

  WEBSPA & ADMINSPA & SPACEUI -->|HTTPS| PROXY
  PROXY -->|"/spaces/*"| SPACE
  PROXY -->|"/god-mode/*"| ADMIN
  PROXY -->|"/live/* (inkl. WebSocket)"| LIVE
  PROXY -->|"/api/*, /auth/*, /static/*"| API
  PROXY -->|"/uploads, /uploads/*"| S3
  PROXY -->|"/* (Rest)"| WEB

  SPACE -->|"SSR-Fetch /api/public/... (VITE_API_BASE_URL)"| API
  LIVE -->|"HTTP mit Cookie des Users<br/>/api/users/me/, /api/workspaces/.../pages/..."| API
  API -->|"POST {LIVE_URL}/convert-document/"| LIVE
  LIVE <-->|"Pub/Sub (Hocuspocus-Redis-Extension,<br/>Kanal hocuspocus:admin)"| REDIS

  API --> PG
  API --> REDIS
  API -->|"Celery .delay()"| MQ
  API -->|"boto3 S3 (head/copy/delete/presign)"| S3
  WORKER --> MQ
  WORKER --> PG
  WORKER --> REDIS
  WORKER --> S3
  BEAT --> MQ
  BEAT --> PG
  MIGRATOR --> PG
  WORKER --> EXT
  API --> EXT
```

Hinweise zum Diagramm:
- Die Browser laden Uploads **direkt** per Presigned POST/GET vom Objektspeicher über den Proxy-Pfad `/{BUCKET_NAME}/…` (`apps/proxy/Caddyfile.ce`, `API/settings/storage.py`), nicht über die API.
- Der Live-Server hat **keinen** Datenbankzugriff; er persistiert ausschließlich über die API mit dem weitergereichten Session-Cookie des Benutzers (`LIVE/services/page/project-page.service.ts`, `LIVE/lib/auth.ts`).
- Der Live-Server benötigt zwingend Redis/Valkey; ohne Redis bricht sein Start ab (`LIVE/redis.ts`, `LIVE/extensions/redis.ts`, Abschnitt 3.7).

### 1.3 Zentrale Kommunikationsflüsse (Mermaid-Sequenzen)

**(a) Start einer Installation (CLI-Compose)** – `deployments/cli/community/install.sh` (`startServices`), `apps/api/bin/*`:

```mermaid
sequenceDiagram
  participant Op as Betreiber (setup.sh start)
  participant DC as docker compose
  participant MIG as migrator
  participant API as api
  participant WK as worker / beat-worker
  participant PG as PostgreSQL
  Op->>DC: up -d --pull if_not_present --quiet-pull
  DC->>MIG: start (restart_policy on-failure)
  MIG->>PG: wait_for_db, dann migrate
  DC->>API: start
  API->>PG: wait_for_db, wait_for_migrations (Polling alle 10 s)
  API->>API: register_instance MACHINE_SIGNATURE (GitHub-Release-Check, Telemetrie-Task)
  API->>API: configure_instance (InstanceConfiguration-Keys anlegen)
  API->>API: create_bucket, clear_cache, collectstatic
  API->>API: exec gunicorn :8000
  DC->>WK: start
  WK->>PG: wait_for_db, wait_for_migrations
  WK->>WK: celery worker / celery beat
  Op->>DC: wartet bis der migrator-Container beendet ist und prüft den ExitCode
  Op->>API: docker exec python3 urllib GET http://localhost:8000/ (max. 300 s)
```

**(b) Datei-Upload (Presigned POST über Proxy)** – `API/settings/storage.py`, `apps/proxy/Caddyfile.ce`, `packages/services/src/helpers/url.ts`:

```mermaid
sequenceDiagram
  participant B as Browser (web)
  participant P as proxy (Caddy)
  participant A as api
  participant S as silo/MinIO
  B->>P: POST /api/.../assets/ (Metadaten: name, type, size)
  P->>A: weiterleiten
  A->>A: S3Storage(request).generate_presigned_post(key, type, size)
  Note over A: USE_MINIO=1: endpoint = {scheme}://{request.get_host()}<br/>(https erzwungen bei MINIO_ENDPOINT_SSL=1)
  A-->>B: {upload_data: {url, fields}, asset_id, ...}
  B->>P: POST {host}/uploads (multipart, Felder + Datei)
  P->>S: reverse_proxy /uploads → plane-minio:9000 (Host-Header bleibt erhalten → Signatur gültig)
  S-->>B: 204
  B->>P: PATCH /api/.../assets/{id}/ (Upload bestätigen)
  P->>A: weiterleiten → Asset als hochgeladen markieren, Celery-Task get_asset_object_metadata (head_object im Worker)
```

**(c) Kollaboratives Editieren (WebSocket)** – `apps/web/components/pages/editor/editor-body.tsx`, `LIVE/controllers/collaboration.controller.ts`, `LIVE/lib/auth.ts`, `LIVE/extensions/database.ts`:

```mermaid
sequenceDiagram
  participant B as Browser (HocuspocusProvider)
  participant P as proxy
  participant L as live (Hocuspocus)
  participant A as api
  participant R as Redis/Valkey
  B->>P: WS ws(s)://{LIVE_BASE_URL|origin}{LIVE_BASE_PATH}/collaboration?documentType=project_page&projectId=…&workspaceSlug=…
  P->>L: /live/collaboration (Upgrade)
  B->>L: Auth-Token = JSON {id, cookie}
  L->>A: GET /api/users/me/ (Header Cookie)
  A-->>L: User → id muss mit token.id übereinstimmen
  L->>A: GET /api/workspaces/{slug}/projects/{pid}/pages/{pageId}/description/ (Binary)
  L->>R: Abo Dokument-Kanal (Multi-Instanz-Sync)
  B-->>L: Yjs-Updates
  L->>A: PATCH .../pages/{pageId}/description/ (debounce 10 000 ms)
```

**(d) API → Live (HTML→Yjs-Konvertierung beim Kopieren)** – `API/bgtasks/copy_s3_object.py` (`sync_with_external_service`): `POST {LIVE_URL}/convert-document/` mit `{"description_html", "variant": "rich"|"document"}` ohne Authentifizierung; bei `LIVE_BASE_URL` leer wird `{}` zurückgegeben und die Konvertierung entfällt.

### 1.4 Verantwortlichkeiten je Komponente

| Komponente | Verantwortung | Technologie | Persistenz | Quelle |
|---|---|---|---|---|
| proxy | TLS (ACME/Let’s Encrypt oder DNS-Challenge), Pfad-Routing, Body-Größenlimit, Client-IP-Ermittlung (`client_ip_headers X-Forwarded-For X-Real-IP`, `trusted_proxies`) | Caddy 2.11.4-alpine mit xcaddy-Modulen `caddy-dns/cloudflare`, `caddy-dns/digitalocean`, `mholt/caddy-l4` | Volumes `proxy_config:/config`, `proxy_data:/data` (Zertifikate) | `apps/proxy/Dockerfile.ce`, `apps/proxy/Caddyfile.ce`, `DEP/cli/community/docker-compose.yml` |
| web | Haupt-UI (Workspaces, Projekte, Work Items, Cycles, Module, Seiten, Views, Analytics, Einstellungen, Profil) | React 19.2.8, React Router 8.3.0 (SPA), MobX, SWR, Tailwind 4.1.17, `@makeplane/propel` 0.7.3 | keine (Browser: localStorage/IndexedDB) | `apps/web/package.json`, `apps/web/react-router.config.ts` |
| admin | Instanz-Administration (God-Mode): Setup, Admin-Login, Auth-Provider, SMTP, AI, Images, Workspaces | wie web, `basename=/god-mode/` | keine | `apps/admin/package.json`, `apps/admin/react-router.config.ts` |
| space | Öffentliche Ansicht veröffentlichter Projekte/Seiten, Gast-Login | React Router 8 **mit SSR**, `react-router-serve` | keine | `apps/space/package.json`, `apps/space/react-router.config.ts` |
| live | Yjs-Realtime-Sync (Hocuspocus), Titel-Sync, Force-Close, HTML→JSON/Binary-Konvertierung, PDF-Export | Node 22, Express 4.22.0 + express-ws, Hocuspocus 2.15.2, ioredis 5.7.0, `@react-pdf/renderer`, effect 3.20.0 | keine eigene; via API | `apps/live/package.json`, `LIVE/server.ts` |
| api | Alle REST-Endpunkte, Auth (Session/Cookie, API-Key), Instanz-Konfiguration, Presigned-URLs, Webhook-Versand-Trigger, E-Mail-Trigger | Python 3.12, Django 5.2.17, DRF 3.17.2, channels 4.3.2 (nur HTTP), gunicorn 23 + uvicorn 0.29 | PostgreSQL, Redis-Cache, S3 | `apps/api/pyproject.toml`, `API/settings/common.py` |
| worker | Asynchrone Jobs (E-Mails, Aktivitäten, Webhooks, Exporte, Versionierung, Benachrichtigungen, Seeds) | Celery 5.5.3, Broker RabbitMQ (AMQP) | PostgreSQL, Redis, S3 | `API/celery.py`, `API/bgtasks/*` |
| beat-worker | Zeitgesteuerte Jobs (13 Einträge, siehe 2.17) | Celery Beat, `django_celery_beat.schedulers.DatabaseScheduler` | Tabellen von `django_celery_beat` | `API/celery.py` |
| migrator | Schema-Migration vor Start | `manage.py migrate` | PostgreSQL | `apps/api/bin/docker-entrypoint-migrator.sh` |
| plane-db | Relationale Datenhaltung inkl. Sessions (`sessions`-Tabelle), Instanz-Konfiguration, API-Logs, Beat-Schedules | PostgreSQL 15.7-alpine | Volume `pgdata` | `docker-compose.yml` |
| plane-redis | Django-Cache (Response-Cache, Throttle-Historien, Magic-Codes), Locks, Hocuspocus-Pub/Sub | Valkey 7.2.11-alpine | Volume `redisdata` | `docker-compose.yml`, `API/settings/common.py`, `LIVE/redis.ts` |
| plane-mq | Celery-Broker | RabbitMQ 3.13.6-management-alpine | Volume `rabbitmq_data` | `docker-compose.yml`, `API/settings/common.py` |
| plane-minio | Objektspeicher für alle Assets (Avatare, Cover, Anhänge, Editor-Bilder, Exporte) | silo (MinIO-Fork), S3 API | Volume `uploads:/export` | `docker-compose.yml` |

---

## 2. Vollständige Inventare

### 2.1 Monorepo-Aufbau

#### 2.1.1 Root-Dateien

| Datei | Inhalt / Zweck | Quelle |
|---|---|---|
| `package.json` | Name `plane`, Version `1.4.2`, `private: true`, Lizenz `AGPL-3.0`, `engines.node >=22.22.0`, `packageManager pnpm@11.10.0+sha512…`; Root-Scripts (2.1.3); devDependencies `husky`, `lint-staged`, `oxfmt`, `oxlint`, `turbo` (alle `catalog:`), `react-doctor ^0.4.2`; `lint-staged`: `*.{js,jsx,ts,tsx,cjs,mjs,cts,mts,json,css,md}` → `pnpm exec oxfmt --no-error-on-unmatched-pattern`, `*.{js,jsx,ts,tsx,cjs,mjs,cts,mts}` → `pnpm exec oxlint --fix --deny-warnings` | `package.json` |
| `pnpm-workspace.yaml` | Workspace `apps/*`, `packages/*`, **ausgenommen** `apps/api`, `apps/proxy`; `catalog`, `overrides`, `allowBuilds`, `minimumReleaseAgeExclude`, `peerDependencyRules` (2.4) | `pnpm-workspace.yaml` |
| `pnpm-lock.yaml` | Lockfile (≈ 498 KB) | `pnpm-lock.yaml` |
| `turbo.json` | Turbo-Tasks + `globalEnv` + `globalDependencies` (2.1.4) | `turbo.json` |
| `.npmrc` | pnpm-Verhalten (2.1.5) | `.npmrc` |
| `.node-version` | `22.22.0` | `.node-version` |
| `.mise.toml` | `[tools] node = "22.22.0"` | `.mise.toml` |
| `.oxlintrc.json` | OxLint-Plugins `react, typescript, jsx-a11y, import, promise, unicorn, oxc`; Kategorien `correctness/suspicious/perf` = `warn`; env browser/node/es2024; React-Version `19.0`; `jsx-a11y.polymorphicPropName = "as"`; ignorePatterns `.cache/**, .next/**, .react-router/**, .storybook/**, .turbo/**, .vite/**, *.config.{js,mjs,cjs,ts}, build/**, coverage/**, dist/**, **/public/**, storybook-static/**`; Regeln aus: `react/react-in-jsx-scope`, `react/prop-types`, `unicorn/filename-case`, `unicorn/no-null`, `unicorn/prevent-abbreviations`; `no-unused-vars` warn mit `_`-Ignore-Patterns | `.oxlintrc.json` |
| `.oxfmtrc.json` | `printWidth 120`, `tabWidth 2`, `trailingComma es5`, Tailwind-Klassensortierung mit Stylesheet `packages/tailwind-config/index.css` und Funktionen `cn, clsx, cva`; Override `packages/codemods/**/*` → `printWidth 80` | `.oxfmtrc.json` |
| `.prettierignore` | `.next/ .react-router/ .turbo/ .vite/ build/ dist/ node_modules/ out/ pnpm-lock.yaml storybook-static/` | `.prettierignore` |
| `.gitattributes` | `*.sh text eol=lf` | `.gitattributes` |
| `.dockerignore` | Build-Kontext-Ausschlüsse (vollständige Liste: `.git`, `*.pyc`, `.env`, `venv`, `.venv`, `node_modules/`, `**/node_modules/`, `npm-debug.log`, `.next/`, `**/.next/`, `.turbo/`, `**/.turbo/`, `build/`, `**/build/`, `out/`, `**/out/`, `dist/`, `**/dist/`, `npm-debug.log*`, `pnpm-debug.log*`, `.pnpm-debug.log*`, `yarn-debug.log*`, `yarn-error.log*`, `.DS_Store`, `Thumbs.db`, `.vscode`, `.idea`, `coverage/`, `**/coverage/`, `*.lcov`, `.junit/`, `test-results/`, `.cache/`, `**/.cache/`, `storybook-static/`, `*storybook.log`, `*.tsbuildinfo`, `.env.local`, `.env.development.local`, `.env.test.local`, `.env.production.local`, `.secrets`, `tmp/`, `temp/`, `*.rdb`, `*.rdb.gz`, `*.pem`, `*.key`, `.react-router/`, `README.md`) | `.dockerignore` |
| `.trivyignore` | Unterdrückt `CVE-2026-30242` (False Positive: Trivy matcht Distribution „Plane“) | `.trivyignore` |
| `.husky/pre-commit` | `pnpm lint-staged` | `.husky/pre-commit` |
| `.env.example` | Root-ENV für Infrastruktur-Container + Proxy (2.11) | `.env.example` |
| `setup.sh` | Kopiert `.env.example` → `.env` für Root, `web`, `api`, `space`, `admin`, `live`; hängt `SECRET_KEY` (50 Zeichen `[a-z0-9]`) an `apps/api/.env` an; generiert `AWS_ACCESS_KEY_ID` (20 Zeichen) und `AWS_SECRET_ACCESS_KEY` (40 Zeichen) `[A-Za-z0-9]` in `./.env` und `./apps/api/.env`; `corepack enable pnpm`; `pnpm install` | `setup.sh` |
| `docker-compose.yml` | Build-basierter Komplett-Stack aus dem Quellcode (2.6) | `docker-compose.yml` |
| `docker-compose-local.yml` | Lokale Entwicklung: Infrastruktur + API/Worker/Beat/Migrator im Container (Bind-Mount), Frontends via `pnpm dev` auf dem Host (2.6) | `docker-compose-local.yml` |
| `docker-compose-test.yml` | Isolierter pytest-Stack (2.25) | `docker-compose-test.yml` |
| `AGENTS.md` | Agenten-/Entwickler-Leitfaden (Kommandos, Code-Style, uv, Backend-Tests) | `AGENTS.md` |
| `CODEOWNERS` | `.oxlintrc.json`, `.oxfmtrc.json`, `apps/web/`, `apps/space/`, `apps/admin/` → `@sriramveeraghanta`; `apps/api/` → `@dheeru0198 @pablohashescobar`; `apps/live/` → `@saivallampati`; `deployments/` → `@mguptahub` | `CODEOWNERS` |
| `LICENSE.txt`, `COPYRIGHT.txt`, `COPYRIGHT_CHECK.md` | AGPL-3.0; Header-Vorlage für `addlicense` (CI 2.24) | `COPYRIGHT.txt` |
| `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`, `README.md` | Projekt-Doku; lokaler Setup-Ablauf: `./setup.sh` → `docker compose -f docker-compose-local.yml up` → `pnpm dev` → `http://localhost:3001/god-mode/` (Instanz-Admin registrieren) → `http://localhost:3000` | `CONTRIBUTING.md` Z. 58–80 |
| `.claude/` | Agenten-Skills (kein Laufzeitbezug) | `.claude/` |

#### 2.1.2 Workspace-Definition

| Eintrag | Bedeutung | Quelle |
|---|---|---|
| `apps/*` | Alle Apps sind pnpm-Workspaces … | `pnpm-workspace.yaml` |
| `packages/*` | … ebenso alle Pakete | `pnpm-workspace.yaml` |
| `!apps/api` | Python-App, nur Pseudo-`package.json` (`plane-api`, Version `1.4.2`) | `pnpm-workspace.yaml`, `apps/api/package.json` |
| `!apps/proxy` | Nur Caddyfiles + Dockerfile | `pnpm-workspace.yaml` |

#### 2.1.3 Root-Scripts (`package.json`)

| Script | Kommando |
|---|---|
| `build` | `turbo run build` |
| `dev` | `turbo run dev --concurrency=18` |
| `start` | `turbo run start` |
| `clean` | `turbo run clean && rm -rf .turbo && rm -rf .next && rm -rf node_modules && rm -rf dist` |
| `fix` | `turbo run fix` |
| `fix:format` | `turbo run fix:format` |
| `fix:lint` | `turbo run fix:lint` |
| `check` | `turbo run check` |
| `check:lint` | `turbo run check:lint` |
| `check:format` | `turbo run check:format` |
| `check:types` | `turbo run check:types` |
| `prepare` | `husky` |
| `doctor` | `npx react-doctor@latest` |

#### 2.1.4 Turbo (`turbo.json`)

`globalDependencies`: `.npmrc`, `.oxfmtrc.json`, `.oxlintrc.json`. `remoteCache.enabled = false`.

| Task | `dependsOn` | `inputs` | `outputs` | Besonderheiten |
|---|---|---|---|---|
| `build` | `^build` | `$TURBO_DEFAULT$`, `.env*` | `dist/**`, `build/**`, `.react-router/**` | – |
| `build-storybook` | `^build` | – | `storybook-static/**` | – |
| `check` | `check:format`, `check:lint`, `check:types` | – | – | – |
| `check:format` | – | `$TURBO_DEFAULT$` | `[]` | – |
| `check:lint` | – | `$TURBO_DEFAULT$`, `!**/*.md` | `[]` | – |
| `check:types` | `^build` | `$TURBO_DEFAULT$`, `!**/*.md` | `[]` | – |
| `clean` | – | – | – | `cache: false` |
| `dev` | `^build` | – | – | `cache: false`, `persistent: true` |
| `fix` | `fix:format`, `fix:lint` | – | – | `cache: false` |
| `fix:format` | – | `$TURBO_DEFAULT$` | `[]` | – |
| `fix:lint` | – | `$TURBO_DEFAULT$`, `!**/*.md` | `[]` | – |
| `start` | – | – | – | `cache: false`, `persistent: true` |
| `test` | `^build` | – | `[]` | – |

`globalEnv` (beeinflusst Turbo-Cache-Hash): `APP_VERSION`, `DEV`, `PROD`, `LOG_LEVEL`, `NODE_ENV`, `SENTRY_DSN`, `SENTRY_ENVIRONMENT`, `SENTRY_TRACES_SAMPLE_RATE`, `VITE_ADMIN_BASE_PATH`, `VITE_ADMIN_BASE_URL`, `VITE_API_BASE_PATH`, `VITE_API_BASE_URL`, `VITE_APP_VERSION`, `VITE_LIVE_BASE_PATH`, `VITE_LIVE_BASE_URL`, `VITE_SENTRY_DSN`, `VITE_SENTRY_ENVIRONMENT`, `VITE_SENTRY_PROFILES_SAMPLE_RATE`, `VITE_SENTRY_REPLAYS_ON_ERROR_SAMPLE_RATE`, `VITE_SENTRY_REPLAYS_SESSION_SAMPLE_RATE`, `VITE_SENTRY_SEND_DEFAULT_PII`, `VITE_SENTRY_TRACES_SAMPLE_RATE`, `VITE_SPACE_BASE_PATH`, `VITE_SPACE_BASE_URL`, `VITE_SUPPORT_EMAIL`, `VITE_WEB_BASE_PATH`, `VITE_WEB_BASE_URL`, `VITE_WEBSITE_URL` (`turbo.json`). **Hinweis:** Keine der `SENTRY_*`/`VITE_SENTRY_*`/`VITE_APP_VERSION`-Variablen wird im Code gelesen (Suche `process.env.` in `apps/web|admin|space`, `packages/*/src` liefert nur die in 2.11.4 gelisteten).

#### 2.1.5 pnpm-Einstellungen (`.npmrc`)

| Schlüssel | Wert |
|---|---|
| `prefer-workspace-packages` | `true` |
| `link-workspace-packages` | `true` |
| `shared-workspace-lockfile` | `true` |
| `save-workspace-protocol` | `true` |
| `resolution-mode` | `highest` |
| `auto-install-peers` | `true` |
| `strict-peer-dependencies` | `false` |
| `side-effects-cache` | `true` |
| `prefer-offline` | `true` |
| `prefer-frozen-lockfile` | `true` |
| `node-linker` | `isolated` |
| `public-hoist-pattern[]` | `typescript`, `eslint`, `*@plane/*`, `vite`, `turbo` |

### 2.2 Apps-Inventar

| App | Pfad | Paketname / Version | Technologie | Rendering | Dev-Kommando / Port | Build-Ausgabe | Laufzeit im Container | Docker-Image (Hub) | Quelle |
|---|---|---|---|---|---|---|---|---|---|
| web | `apps/web` | `web` 1.4.2 | React 19.2.8, React Router 8.3.0 (Vite 8.0.16), MobX, SWR | Client-only SPA (`ssr: false`, `appDirectory: "app"`, `future.unstable_optimizeDeps: true`) | `react-router dev --port 3000` (Vite-Host `127.0.0.1`) | `build/client` | Caddy :3000, Root `/usr/share/caddy/html` | `makeplane/plane-frontend` | `apps/web/package.json`, `apps/web/react-router.config.ts`, `apps/web/vite.config.ts`, `apps/web/Dockerfile.web` |
| admin | `apps/admin` | `admin` 1.4.2 | wie web | SPA (`ssr: false`), `basename` = `joinUrlPath(VITE_ADMIN_BASE_PATH, "/")` (Default `/`), Vite `base` = dasselbe | `react-router dev --port 3001` | `build/client` | Caddy :3000, Dateien unter `/usr/share/caddy/html/god-mode` | `makeplane/plane-admin` | `apps/admin/package.json`, `apps/admin/react-router.config.ts`, `apps/admin/vite.config.ts`, `apps/admin/Dockerfile.admin` |
| space | `apps/space` | `space` 1.4.2 | wie web + `@react-router/serve` | **SSR** (`ssr: true`), `basename` = `joinUrlPath(VITE_SPACE_BASE_PATH, "/")` | `react-router dev --port 3002`; `start`: `PORT=3002 react-router-serve ./build/server/index.js` | `build/client` + `build/server/index.js` | Node `./node_modules/.bin/react-router-serve ./build/server/index.js` (Port aus `PORT`, Default der Lib 3000) | `makeplane/plane-space` | `apps/space/package.json`, `apps/space/react-router.config.ts`, `apps/space/Dockerfile.space` |
| live | `apps/live` | `live` 1.4.2 (`type: module`, `main ./dist/start.mjs`) | Node 22, Express 4.22.0, express-ws, Hocuspocus 2.15.2, ioredis, effect, `@react-pdf/renderer`, sharp | Server | `tsdown --watch --no-clean --onSuccess "node --env-file=.env ."`; Port aus `PORT` (`.env.example`: 3100) | `dist/start.mjs` (tsdown, ESM, Entry `src/start.ts`) | `node apps/live` (Port-Default `"3000"`) | `makeplane/plane-live` | `apps/live/package.json`, `apps/live/tsdown.config.ts`, `LIVE/env.ts`, `apps/live/Dockerfile.live` |
| api | `apps/api` | `plane-api` 1.4.2 (Pseudo-Paket), Python-Projekt `Plane` 1.4.2 | Python `>=3.12,<3.13`, Django 5.2.17, DRF, Celery | Server | `./bin/docker-entrypoint-api-local.sh` → `runserver 0.0.0.0:8000 --settings=plane.settings.local` | – | gunicorn + UvicornWorker :8000 | `makeplane/plane-backend` | `apps/api/pyproject.toml`, `apps/api/bin/*`, `apps/api/Dockerfile.api` |
| proxy | `apps/proxy` | – | Caddy 2.11 | – | – | – | `caddy` mit `/etc/caddy/Caddyfile` (= `Caddyfile.ce`) | `makeplane/plane-proxy` | `apps/proxy/Dockerfile.ce` |

Abhängigkeiten der Apps zu Workspace-Paketen (`apps/*/package.json`):

| App | `@plane/*` (workspace) | wichtigste externe (alle `catalog:`) |
|---|---|---|
| web | `blocks`, `constants`, `editor`, `hooks`, `i18n`, `services`, `shared-state`, `types`, `utils`; dev: `tailwind-config`, `typescript-config` | `@atlaskit/pragmatic-drag-and-drop(-auto-scroll,-hitbox)`, `@base-ui/react`, `@bprogress/core`, `@fontsource-variable/inter`, `@fontsource/ibm-plex-mono`, `@fontsource/material-symbols-rounded`, `@makeplane/propel`, `@react-pdf/renderer`, `@react-router/node`, `@tanstack/react-table`, `axios`, `clsx`, `cmdk`, `comlink`, `date-fns`, `emoji-picker-react`, `export-to-csv`, `isbot`, `lodash-es`, `lucide-react`, `mobx`, `mobx-react`, `mobx-utils`, `next-themes`, `react`, `react-dom`, `react-dropzone`, `react-fast-compare`, `react-hook-form`, `react-is`, `react-markdown`, `react-masonry-component`, `react-pdf-html`, `react-router`, `recharts`, `serve`, `smooth-scroll-into-view-if-needed`, `swr`, `use-font-face-observer`, `uuid`; dev: `@react-router/dev`, `@tailwindcss/postcss`, `@tailwindcss/typography`, `@types/*`, `dotenv`, `typescript`, `vite`, `vite-tsconfig-paths` |
| admin | `blocks`, `constants`, `hooks`, `i18n`, `services`, `types`, `utils`; dev: `tailwind-config`, `typescript-config` | `@bprogress/core`, Fonts (3), `@makeplane/propel`, `@react-router/node`, `isbot`, `lodash-es`, `lucide-react`, `mobx`, `mobx-react`, `next-themes`, `react`, `react-dom`, `react-hook-form`, `react-router`, `serve`, `swr`, `uuid` |
| space | `blocks`, `constants`, `editor`, `i18n`, `services`, `types`, `utils`; dev: `tailwind-config`, `typescript-config` | `@bprogress/core`, Fonts (3), `@makeplane/propel`, `@react-router/node`, `@react-router/serve`, `axios`, `clsx`, `date-fns`, `isbot`, `lodash-es`, `lucide-react`, `mobx`, `mobx-react`, `mobx-utils`, `next-themes`, `react`, `react-dom`, `react-dropzone`, `react-hook-form`, `react-router`, `swr`, `uuid` |
| live | `decorators`, `editor`, `logger`, `services`, `types`, `utils`; dev: `typescript-config` | `@effect/platform`, `@effect/platform-node`, `@fontsource/inter`, `@hocuspocus/extension-database`, `@hocuspocus/extension-logger`, `@hocuspocus/extension-redis`, `@hocuspocus/server`, `@hocuspocus/transformer`, `@react-pdf/renderer`, `@react-pdf/types`, `@tiptap/core`, `@tiptap/html`, `axios`, `compression`, `cors`, `dotenv`, `effect`, `express`, `express-ws`, `helmet`, `ioredis`, `react`, `sharp`, `uuid`, `ws`, `y-prosemirror`, `y-protocols`, `yjs`, `zod`; dev: `@vitest/coverage-v8`, `pdf-parse`, `tsdown`, `typescript`, `vitest` |

App-Scripts (vollständig, `apps/*/package.json`):

| App | Scripts |
|---|---|
| web | `dev`, `build` (`react-router build`), `preview` (`react-router build && serve -s build/client -l 3000`), `start` (`serve -s build/client -l 3000`), `clean`, `check:lint` (`oxlint --max-warnings=11957 .`), `check:types` (`react-router typegen && tsc --noEmit`), `check:format` (`oxfmt --check .`), `fix:lint`, `fix:format` |
| admin | `dev`, `build`, `preview` (`… serve -s build/client -l 3001`), `start` (`serve -s build/client -l 3001`), `clean`, `check:lint` (`--max-warnings=759`), `check:types`, `check:format`, `fix:lint`, `fix:format` |
| space | `dev`, `build`, `preview` (`… PORT=3002 react-router-serve ./build/server/index.js`), `start`, `clean`, `check:lint` (`--max-warnings=676`), `check:types`, `check:format`, `fix:lint`, `fix:format` |
| live | `build` (`tsc --noEmit && tsdown`), `dev`, `start` (`node --env-file=.env .`), `test` (`vitest run`), `test:watch`, `test:coverage`, `check:lint` (`--max-warnings=119`), `check:types`, `check:format`, `fix:lint`, `fix:format`, `clean` |

Vite-Konfiguration (alle drei Frontends identisch im Muster, `apps/{web,admin,space}/vite.config.ts`): `dotenv.config({ path: <app>/.env })`; alle `VITE_*`-Variablen aus `process.env` werden per `define: { "process.env": JSON.stringify(viteEnv) }` **zur Build-Zeit** eingebettet; `build.assetsInlineLimit: 0` (keine Inline-Assets); `resolve.dedupe: ["react","react-dom"]`; Aliase für Next.js-Kompatibilitäts-Shims (`next/link`, `next/navigation`, bei web zusätzlich `next/script`; space nur `next/navigation`) auf `app/compat/next/*`; `server.host: "127.0.0.1"`.

### 2.3 Packages-Inventar

| Paket | Name / Version | Zweck | Build | Exports | Workspace-Abhängigkeiten | Externe Laufzeit-Abhängigkeiten | Tests | Konsumenten |
|---|---|---|---|---|---|---|---|---|
| `packages/blocks` | `@plane/blocks` 1.4.2 | Composite-/Plane-spezifische UI-Bausteine auf Basis `@makeplane/propel` | `tsdown` | Subpaths (nur diese): `./auth`, `./breadcrumb`, `./card`, `./charts/area-chart`, `./charts/bar-chart`, `./charts/line-chart`, `./charts/pie-chart`, `./charts/radar-chart`, `./charts/tree-map`, `./common`, `./context-menu`, `./dialog`, `./emoji-icon-picker`, `./emoji-icon-picker/data`, `./emoji-reaction`, `./empty-state`, `./icons`, `./layout`, `./pill-button`, `./portal`, `./property-select`, `./select`, `./skeleton`, `./spinner`, `./toast`, `./types`, `./utils`, `./virtual-list`, `./package.json` | `constants`, `hooks`, `i18n`, `types`, `utils`, `tailwind-config`, `typescript-config` | `@atlaskit/pragmatic-drag-and-drop`, `-hitbox`, `@base-ui/react`, `@makeplane/propel`, `@tanstack/react-virtual`, `class-variance-authority`, `clsx`, `date-fns`, `frimousse`, `lodash-es`, `lucide-react`, `react`, `react-dom`, `recharts`, `use-font-face-observer` | `vitest run --project=unit --project=dom` (21 Testdateien, 2.25) | web, admin, space, editor |
| `packages/codemods` | `@plane/codemods` 1.4.2 | jscodeshift-Transformationen (`function-declaration.ts`, `remove-directives.ts`) | – | – | – | – (dev: jscodeshift) | `vitest run` (2 Spec-Dateien) | Entwickler |
| `packages/constants` | `@plane/constants` 1.4.2 | Konstanten; Module in `src/`: `ai.ts`, `analytics/`, `auth/`, `calendar.ts`, `chart.ts`, `cycle.ts`, `dashboard.ts`, `emoji.ts`, `endpoints.ts` (alle Basis-URLs, 2.11.4), `estimates.ts`, `fetch-keys.ts`, `file.ts`, `filter.ts`, `gantt-chart.ts`, `graph.ts`, `icon.ts`, `index.ts`, `instance.ts`, `intake.ts`, `issue/`, `label.ts`, `members.ts`, `metadata.ts`, `module.ts`, `notification.ts`, `page.ts`, `payment.ts`, `profile.ts`, `project.ts`, `rich-filters/`, `settings/`, `sidebar-favorites.ts`, `sidebar.ts`, `spreadsheet.ts`, `state.ts`, `stickies.ts`, `subscription.ts`, `swr.ts`, `tab-indices.ts`, `themes.ts`, `user.ts`, `views.ts`, `workspace-drafts.ts`, `workspace.ts` | `tsdown` | `.` | `types`, `typescript-config` | – | – | alle Frontends, blocks, editor, services, shared-state, utils |
| `packages/decorators` | `@plane/decorators` 0.1.0 | Controller-/Route-/WebSocket-Decorators für Express (`controller.ts`, `rest.ts`, `websocket.ts`) | `tsdown` | `.` | `typescript-config` | – | – | live |
| `packages/editor` | `@plane/editor` 1.4.2 | Tiptap-2-Editor (Rich-Text/Dokument), Collaboration-Provider, HTML/JSON/Binary-Konvertierung | `tsc && tsdown` | `.`, `./lib`, `./package.json`, `./styles.css`, `./styles` | `blocks`, `constants`, `hooks`, `types`, `utils`, `tailwind-config`, `typescript-config` | `@floating-ui/dom`, `@floating-ui/react`, `@hocuspocus/provider`, `@makeplane/propel`, 22 `@tiptap/*` (`core`, `extension-blockquote`, `extension-character-count`, `extension-collaboration`, `extension-document`, `extension-emoji`, `extension-heading`, `extension-image`, `extension-list-item`, `extension-mention`, `extension-placeholder`, `extension-task-item`, `extension-task-list`, `extension-text`, `extension-text-align`, `extension-text-style`, `extension-underline`, `html`, `pm`, `react`, `starter-kit`, `suggestion`), `buffer`, `emoji-regex`, `highlight.js`, `is-emoji-supported`, `jsx-dom-cjs`, `linkifyjs`, `lodash-es`, `lowlight`, `lucide-react`, `prosemirror-codemark`, `tippy.js`, `tiptap-markdown`, `uuid`, `y-indexeddb`, `y-prosemirror`, `y-protocols`, `yjs` | – | web, space, live |
| `packages/hooks` | `@plane/hooks` 1.4.2 | React-Hooks (`use-dialog-dismissal`, `use-hash-scroll`, `use-local-storage`, `use-outside-click-detector`, `use-platform-os`) | `tsdown` | `.` | `typescript-config` | `react` | – | web, admin, blocks, editor |
| `packages/i18n` | `@plane/i18n` 1.4.2 | i18next-Setup + 22 Locales (`bg, cs, de, en, es, fr, id, it, ja, ka-ge, ko, nl, pl, pt-BR, ro, ru, sk, tr-TR, ua, vi-VN, zh-CN, zh-TW`) | `pnpm run generate:types && tsdown` | `.` | `typescript-config` | `i18next`, `i18next-icu`, `i18next-resources-to-backend`, `react`, `react-i18next` | `sync:check`/`check:sync` (Skript `scripts/sync-check.ts`) | web, admin, space, blocks |
| `packages/logger` | `@plane/logger` 1.4.2 | winston-Logger (JSON, Level `LOG_LEVEL` Default `info`, Timestamp `YYYY-MM-DD HH:mm:ss:ms`, Console-Transport) + `express-winston`-Middleware (`{{req.method}} {{req.url}} {{res.statusCode}} {{res.responseTime}}ms`) | `tsdown` | `.` | `typescript-config` | `express-winston`, `winston` | – | live |
| `packages/services` | `@plane/services` 1.4.2 | Axios-basierte API-Service-Klassen (`APIService` mit `withCredentials: true`, Trailing-Slash-Interceptor), `LiveService` | `tsdown` | `.` | `constants`, `types`, `typescript-config` | `axios`, `file-type` | `vitest run` (`src/helpers/url.test.ts`) | web, admin, space, live |
| `packages/shared-state` | `@plane/shared-state` 1.4.2 | Gemeinsame MobX-Stores | `tsdown` | `.` | `constants`, `types`, `utils`, `typescript-config` | `lodash-es`, `mobx`, `mobx-utils`, `uuid`, `zod` | – | web |
| `packages/tailwind-config` | `@plane/tailwind-config` 1.4.2 | Tailwind-4-Theme (`index.css`), PostCSS-Config | – | `./index.css`, `./postcss.config.js` | – | `@makeplane/propel`, `@tailwindcss/postcss`, `postcss` | – | alle Frontends, blocks, editor |
| `packages/types` | `@plane/types` 1.4.2 | TypeScript-Typen aller Domänen | `tsdown` | `.` | `typescript-config` | – | – | alle |
| `packages/typescript-config` | `@plane/typescript-config` 1.4.2 | tsconfig-Presets `base.json`, `nextjs.json`, `node-library.json`, `react-library.json`, `react-router.json` | – | – | – | – | – | alle |
| `packages/utils` | `@plane/utils` 1.4.2 | Hilfsfunktionen; Module in `src/`: `array.ts`, `attachment.ts`, `auth.ts`, `calendar.ts`, `color.ts`, `common.ts`, `cycle.ts`, `datetime.ts`, `distribution-update.ts`, `editor/`, `emoji.ts`, `estimates.ts`, `file.ts`, `filter.ts`, `get-icon-for-link.ts`, `index.ts`, `intake.ts`, `loader.ts`, `math.ts`, `module.ts`, `notification.ts`, `page.ts`, `permission/`, `project-views.ts`, `project.ts`, `rich-filters/`, `router.ts`, `string.ts` (enthält `joinUrlPath`), `subscription.ts`, `tab-indices.ts`, `theme/`, `theme-legacy.ts`, `tlds.ts`, `url.ts`, `validation.ts`, `work-item/`, `work-item-filters/`, `workspace.ts` | `tsdown` | `.` | `constants`, `types`, `typescript-config` | `@makeplane/propel`, `chroma-js`, `clsx`, `date-fns`, `hast`, `hast-util-to-mdast`, `lodash-es`, `lucide-react`, `mdast`, `react`, `rehype-parse`, `rehype-remark`, `remark-gfm`, `remark-stringify`, `sanitize-html`, `tailwind-merge`, `unified`, `uuid` | – | alle Frontends, live |

Externes UI-Primitive-Paket: `@makeplane/propel` **0.7.3** (npm, Lizenz `AGPL-3.0-only`, „Plane's React component library built on Base UI and Tailwind CSS v4“), Dependencies `@base-ui/react ^1.6.0`, `class-variance-authority ^0.7.1`, `lucide-react ^1.23.0`, `react-day-picker ^10.0.1`; Peers `react ^18||^19`, `react-dom ^18||^19`, `tailwindcss ^4.0.0`; Export-Subpaths `./base/*`, `./components/*`, `./components/logo-spinner/*.gif`, `./components/logo-spinner/*.png`, `./elements/*`, `./hooks/*`, `./icons`, `./package.json`, `./styles`, `./styles/*` (gelesen aus dem entpackten Paket `propel-pkg/package/package.json`). Detailanalyse siehe UI-Bereich.

### 2.4 pnpm-Catalog (alle Einträge) und Overrides

Alle Versionen aus `pnpm-workspace.yaml` → `catalog:` (vollständig, nach Domäne gruppiert).

| Domäne | Paket = Version |
|---|---|
| Build/Tooling | `turbo` 2.10.11 · `typescript` 5.8.3 · `vite` 8.0.16 · `vite-tsconfig-paths` ^5.1.4 · `tsdown` 0.16.0 · `tsx` 4.20.6 · `oxlint` 1.51.0 · `oxfmt` 0.35.0 · `husky` 9.1.7 · `lint-staged` 16.2.7 · `dotenv` 16.4.7 · `serve` 14.2.5 · `jscodeshift` ^17.3.0 · `@types/jscodeshift` ^17.3.0 · `ast-types` 0.14.2 · `@hypermod/utils` ^0.7.1 · `reflect-metadata` ^0.2.2 |
| CSS | `tailwindcss` 4.1.17 · `@tailwindcss/postcss` 4.1.17 · `@tailwindcss/typography` 0.5.19 · `postcss` 8.5.25 · `postcss-cli` ^11.0.0 · `postcss-nested` ^6.0.1 · `autoprefixer` ^10.4.19 · `tailwind-merge` 3.4.0 · `class-variance-authority` 0.7.1 · `clsx` ^2.1.1 |
| React/Routing | `react` 19.2.8 · `react-dom` 19.2.8 · `react-is` ^19.2.8 · `@types/react` 19.2.17 · `@types/react-dom` 19.2.3 · `react-router` 8.3.0 · `@react-router/dev` 8.3.0 · `@react-router/node` 8.3.0 · `@react-router/serve` 8.3.0 · `isbot` ^5.1.31 |
| State/Daten/Netzwerk | `mobx` 6.12.0 · `mobx-react` 9.2.2 · `mobx-utils` 6.0.8 · `swr` 2.4.2 · `axios` 1.20.0 · `zod` ^3.25.76 · `lodash-es` 4.18.1 · `@types/lodash-es` 4.17.12 · `uuid` 14.0.0 · `date-fns` ^4.1.0 · `comlink` ^4.4.1 · `react-hook-form` ^7.84.0 · `react-fast-compare` ^3.2.2 · `effect` 3.20.0 · `@effect/platform` ^0.94.0 · `@effect/platform-node` ^0.104.0 |
| UI-Primitives/Komponenten | `@makeplane/propel` 0.7.3 · `@base-ui/react` 1.6.0 · `@radix-ui/react-scroll-area` ^1.2.3 · `@floating-ui/dom` ^1.7.1 · `@floating-ui/react` ^0.27.20 · `lucide-react` 0.469.0 · `cmdk` ^1.1.1 · `next-themes` 0.4.6 · `@bprogress/core` ^1.3.4 · `recharts` ^2.15.4 · `@tanstack/react-table` ^8.21.3 · `@tanstack/react-virtual` ^3.13.12 · `@tanstack/virtual-core` ^3.13.12 · `@atlaskit/pragmatic-drag-and-drop` 1.7.4 · `@atlaskit/pragmatic-drag-and-drop-auto-scroll` 1.4.0 · `@atlaskit/pragmatic-drag-and-drop-hitbox` 1.1.0 · `react-dropzone` ^14.2.3 · `react-masonry-component` ^6.3.0 · `smooth-scroll-into-view-if-needed` ^2.0.2 · `emoji-picker-react` ^4.5.16 · `frimousse` ^0.3.0 · `emoji-regex` ^10.3.0 · `is-emoji-supported` ^0.0.5 · `use-font-face-observer` ^1.3.0 · `chroma-js` ^3.2.0 · `@types/chroma-js` ^3.1.2 · `tippy.js` ^6.3.7 · `react-markdown` ^10.1.0 |
| Fonts | `@fontsource-variable/inter` 5.2.8 · `@fontsource/inter` 5.2.8 · `@fontsource/ibm-plex-mono` 5.2.7 · `@fontsource/material-symbols-rounded` 5.2.30 |
| Editor (Tiptap 2) | `@tiptap/core` ^2.27.3 (Kommentar: 2.27.3 backportet den `mergeAttributes`-`__proto__`-Fix GHSA-cp6q-959q-f8rh) · `@tiptap/extension-blockquote` ^2.22.3 · `@tiptap/extension-character-count` ^2.22.3 · `@tiptap/extension-collaboration` ^2.22.3 · `@tiptap/extension-document` ^2.22.3 · `@tiptap/extension-emoji` ^2.22.3 · `@tiptap/extension-heading` ^2.22.3 · `@tiptap/extension-image` ^2.22.3 · `@tiptap/extension-list-item` ^2.22.3 · `@tiptap/extension-mention` ^2.22.3 · `@tiptap/extension-placeholder` ^2.22.3 · `@tiptap/extension-task-item` ^2.22.3 · `@tiptap/extension-task-list` ^2.22.3 · `@tiptap/extension-text` ^2.22.3 · `@tiptap/extension-text-align` ^2.22.3 · `@tiptap/extension-text-style` ^2.22.3 · `@tiptap/extension-underline` ^2.22.3 · `@tiptap/html` ^2.22.3 · `@tiptap/pm` ^2.22.3 · `@tiptap/react` ^2.22.3 · `@tiptap/starter-kit` ^2.22.3 · `@tiptap/suggestion` ^2.22.3 · `prosemirror-codemark` ^0.4.2 · `tiptap-markdown` ^0.8.10 · `highlight.js` ^11.8.0 · `lowlight` ^3.0.0 · `linkifyjs` ^4.3.2 · `jsx-dom-cjs` ^8.0.3 · `buffer` ^6.0.3 |
| Realtime | `yjs` ^13.6.20 · `y-prosemirror` ^1.3.7 · `y-protocols` ^1.0.6 · `y-indexeddb` ^9.0.12 · `@hocuspocus/server` 2.15.2 · `@hocuspocus/provider` 2.15.2 · `@hocuspocus/extension-database` 2.15.2 · `@hocuspocus/extension-logger` 2.15.2 · `@hocuspocus/extension-redis` 2.15.2 · `@hocuspocus/transformer` 2.15.2 · `ws` 8.21.0 · `@types/ws` ^8.18.1 · `ioredis` 5.7.0 |
| Node-Server (live) | `express` 4.22.0 · `@types/express` 4.17.23 · `express-ws` ^5.0.2 · `@types/express-ws` ^3.0.5 · `compression` 1.8.2 · `@types/compression` 1.8.1 · `cors` ^2.8.5 · `@types/cors` ^2.8.17 · `helmet` ^7.1.0 · `winston` ^3.17.0 · `express-winston` ^4.2.0 · `sharp` ^0.35.5 · `@types/node` 22.12.0 |
| PDF/Export | `@react-pdf/renderer` ^4.8.1 · `@react-pdf/types` ^2.13.1 · `react-pdf-html` ^2.1.2 · `pdf-parse` ^2.4.5 · `@types/pdf-parse` ^1.1.5 · `export-to-csv` ^1.4.0 |
| Markdown/HTML | `unified` ^11.0.5 · `rehype-parse` ^9.0.1 · `rehype-remark` ^10.0.1 · `remark-gfm` ^4.0.1 · `remark-stringify` ^11.0.0 · `hast` ^1.0.0 · `hast-util-to-mdast` ^10.1.2 · `mdast` ^3.0.0 · `@types/hast` ^3.0.4 · `@types/mdast` ^4.0.4 · `sanitize-html` 2.17.7 · `@types/sanitize-html` 2.16.0 · `file-type` ^21.3.1 |
| i18n | `i18next` 25.10.9 · `i18next-icu` 2.4.3 · `i18next-resources-to-backend` 1.2.1 · `react-i18next` 16.6.6 |
| Test/Storybook | `vitest` ^4.1.11 · `@vitest/coverage-v8` ^4.1.11 · `jsdom` 23.2.0 · `@testing-library/react` 16.3.3 · `@testing-library/user-event` 14.6.1 · `storybook` 10.4.6 · `@storybook/addon-designs` 11.1.3 · `@storybook/addon-docs` 10.4.6 · `@storybook/addon-links` 10.4.6 · `@storybook/addon-onboarding` 10.4.6 · `@storybook/addon-styling-webpack` 3.0.2 · `@storybook/addon-webpack5-compiler-swc` 4.0.3 · `@storybook/react` 10.4.6 · `@storybook/react-vite` 10.4.6 · `@storybook/react-webpack5` 10.4.6 · `@chromatic-com/storybook` 5.2.1 |

**`overrides`** (vollständig, `pnpm-workspace.yaml`): `react`, `react-dom`, `react-is`, `@types/react`, `@types/react-dom` → `catalog:` (genau eine React-Kopie; Kommentar: zweite Kopie würde „invalid hook call“ erzeugen); `@base-ui/react` → `catalog:` (propel und blocks müssen dieselbe Base-UI-Kopie teilen); `express` → `catalog:`; `@react-router/serve>express` → `^5.2.1` (React-Router-Serve v8 braucht Express 5, `apps/live` bleibt wegen `express-ws` auf Express 4); `mdast-util-to-hast` 13.2.1; `valibot` 1.4.2; `glob` 11.1.0; `brace-expansion` 5.0.12; `nanoid` 3.3.18; `esbuild` 0.28.1; `@babel/core` 7.29.7; `@babel/helpers` 7.29.7; `@babel/runtime` 7.29.7; `chokidar` 3.6.0; `prosemirror-view` 1.42.6; `prosemirror-model` 1.25.12 (eine Model-Kopie, sonst brechen `instanceof`-Checks); `@types/express` 4.17.23; `typescript` → `catalog:`; `vite` → `catalog:`; `qs` 6.16.0; `diff` 5.2.2; `webpack` 5.104.1; `lodash-es` → `catalog:`; `lodash` 4.18.1; `markdown-it` 14.3.2; `rollup` 4.59.0; `minimatch@3` 3.1.4; `minimatch@10` 10.2.3; `serialize-javascript` 7.0.5; `ajv@6` 6.14.0; `ajv@8` 8.18.0; `undici@7` 7.30.0; `flatted` 3.4.2; `picomatch` 2.3.2; `yaml@1` 1.10.3; `yaml@2` 2.8.3; `path-to-regexp` 0.1.13 (Express 4); `router>path-to-regexp` ^8.4.2 (Express 5); `defu` 6.1.5; `postcss` 8.5.25; `postcss-selector-parser` 7.1.6; `axios` → `catalog:`; `follow-redirects` 1.16.0; `uuid` → `catalog:`; `fast-uri` 3.1.8; `js-yaml@4` 4.3.2; `linkify-it` 5.0.2; `body-parser` 1.20.6; `tmp` 0.2.7; `form-data` 4.0.6; `ws@8` 8.21.0; `ws@7` 7.5.11; `@opentelemetry/core` 2.8.0; `@opentelemetry/resources` 2.8.0; `@opentelemetry/sdk-trace-base` 2.8.0; `morgan` 1.12.1; `browserslist` >=4.28.7; `toml` >=4.2.0 <5; `compression` → `catalog:`; `proxy-addr` >=2.0.8 <3; `source-map-js` >=1.2.2 <2; `tinypool@2` >=2.1.2 <3.

**`allowBuilds`:** `@parcel/watcher` true, `@swc/core` true, `esbuild` true, `msgpackr-extract` true, `turbo` true, `sharp` **false** (keine nativen Build-Skripte für sharp). **`minimumReleaseAgeExclude`:** `@storybook/addon-docs@10.4.6`, `@storybook/builder-vite@10.4.6`, `@storybook/csf-plugin@10.4.6`, `@storybook/react-dom-shim@10.4.6`, `@storybook/react-vite@10.4.6`, `@storybook/react@10.4.6`, `storybook@10.4.6`, `@makeplane/propel@0.7.3`. **`peerDependencyRules.allowedVersions`:** `react-masonry-component>react: "19"`, `use-font-face-observer>react: "19"`.

### 2.5 Python-Abhängigkeiten (`apps/api/pyproject.toml`)

`[project] name = "Plane"`, `version = "1.4.2"`, `requires-python = ">=3.12,<3.13"`. `[tool.uv] required-version = "==0.12.21"`, `package = false`, `default-groups = ["dev", "test"]`. Lockfile `apps/api/uv.lock`.

| Gruppe | Paket = Version | Zweck (Kommentar in pyproject) |
|---|---|---|
| Basis | `Django==5.2.17` | Framework |
| Basis | `djangorestframework==3.17.2` | REST |
| Basis | `psycopg==3.3.4` | Postgres-Treiber (Implementierung aus Gruppe) |
| Basis | `dj-database-url==3.0.1` | `DATABASE_URL`-Parsing |
| Basis | `redis==5.0.4` | Redis-Client |
| Basis | `django-redis==7.0.0` | Cache-Backend |
| Basis | `django-cors-headers==4.9.0` | CORS |
| Basis | `celery==5.5.3` | Task-Queue |
| Basis | `django_celery_beat==2.9.0` | DB-Scheduler |
| Basis | `django-celery-results==2.6.0` | (installiert, aber **nicht** in `INSTALLED_APPS`; kein Result-Backend konfiguriert, `API/settings/common.py`) |
| Basis | `whitenoise==6.12.0` | Static-Files |
| Basis | `faker==25.0.0` | Dummy-Daten |
| Basis | `django-filter==25.2` | Filter-Backend |
| Basis | `jsonmodels==2.7.0` | JSON-Modelle |
| Basis | `django-storages==1.14.6` | S3-Storage-Basis |
| Basis | `django-crum==0.7.9` | Current-Request-User |
| Basis | `uvicorn==0.29.0` | ASGI-Worker |
| Basis | `channels==4.3.2` | ASGI-Router (nur HTTP) |
| Basis | `openai==1.63.2` | LLM-Client |
| Basis | `slack-sdk==3.27.1` | Slack |
| Basis | `scout-apm==3.5.3` | APM (nur `production.py`) |
| Basis | `openpyxl==3.1.2` | XLSX-Export |
| Basis | `python-json-logger==4.0.0` | JSON-Logs |
| Basis | `beautifulsoup4==4.12.3` | HTML-Parser |
| Basis | `cryptography==50.0.0` | Fernet |
| Basis | `lxml==6.1.0` | HTML-Validator |
| Basis | `boto3==1.34.96` | S3 |
| Basis | `urllib3>=2.8.0` | CVE-Pin |
| Basis | `requests==2.33.0` | Webhooks/Link-Unfurl (SSRF-IP-Pinning-Hook) |
| Basis | `zxcvbn==4.4.28` | Passwortstärke |
| Basis | `pytz==2024.1` | Zeitzonen |
| Basis | `PyJWT==2.15.1` | JWT |
| Basis | `opentelemetry-api==1.28.1`, `opentelemetry-sdk==1.28.1`, `opentelemetry-instrumentation-django==0.49b1`, `opentelemetry-exporter-otlp==1.28.1`, `opentelemetry-exporter-otlp-proto-grpc==1.28.1` | Telemetrie-Metriken (2.23) |
| Basis | `drf-spectacular==0.29.0` | OpenAPI |
| Basis | `nh3==0.2.18` | HTML-Sanitizer |
| `production` | `gunicorn==23.0.0`, `psycopg-c==3.3.4` | Server, C-Treiber (aus Quellcode gebaut) |
| `dev` | `psycopg-binary==3.3.4`, `django-debug-toolbar==6.0.0`, `ruff==0.9.7` | Entwicklung |
| `test` | `psycopg-binary==3.3.4`, `pytest==9.0.3`, `pytest-django==4.12.0`, `pytest-cov==4.1.0`, `pytest-xdist==3.3.1`, `pytest-mock==3.11.1`, `factory-boy==3.3.0`, `freezegun==1.2.2`, `coverage==7.2.7`, `httpx==0.28.1` | Tests |

Ruff (`apps/api/ruff.toml`): `target-version = "py312"`, `line-length = 120`, `indent-width = 4`, Format `quote-style = "double"`, `indent-style = "space"`, `line-ending = "auto"`; Lint `select = ["E","F"]`, `fixable = ["ALL"]`, `dummy-variable-rgx`, `per-file-ignores`: `tests/*` → `E402, F401, F811`, `__init__.py` → `F401`; `mccabe.max-complexity = 10`; isort `known-first-party = ["plane"]`, `known-third-party = ["rest_framework"]`; `flake8-tidy-imports.ban-relative-imports = "parents"`; `pycodestyle.max-doc-length = 88`; `pydocstyle.convention = "google"`; `pylint.max-args = 8`, `max-statements = 50`; Excludes inkl. `**/migrations/*`.

### 2.6 Service-/Container-Tabelle (alle Compose-/Deployment-Varianten)

#### 2.6.1 `docker-compose.yml` (Root, Build aus Quellcode)

| Service | `container_name` | Build / Image | Kommando | env_file / environment | depends_on | Restart | Ports | Volumes |
|---|---|---|---|---|---|---|---|---|
| `web` | `web` | Build `.` / `apps/web/Dockerfile.web` (Arg `DOCKER_BUILDKIT: 1`) | Image-CMD (Caddy) | – | `api` | `always` | – | – |
| `admin` | `admin` | Build `.` / `apps/admin/Dockerfile.admin` | Image-CMD (Caddy) | – | `api`, `web` | `always` | – | – |
| `space` | `space` | Build `.` / `apps/space/Dockerfile.space` | Image-CMD (react-router-serve) | – | `api`, `web` | `always` | – | – |
| `api` | `api` | Build `./apps/api` / `Dockerfile.api` | `./bin/docker-entrypoint-api.sh` | `./apps/api/.env` | `plane-db`, `plane-redis` | `always` | – | – |
| `worker` | `bgworker` | wie api | `./bin/docker-entrypoint-worker.sh` | `./apps/api/.env` | `api`, `plane-db`, `plane-redis` | `always` | – | – |
| `beat-worker` | `beatworker` | wie api | `./bin/docker-entrypoint-beat.sh` | `./apps/api/.env` | `api`, `plane-db`, `plane-redis` | `always` | – | – |
| `migrator` | `plane-migrator` | wie api | `./bin/docker-entrypoint-migrator.sh` | `./apps/api/.env` | `plane-db`, `plane-redis` | `no` | – | – |
| `live` | `plane-live` | Build `.` / `apps/live/Dockerfile.live` | Image-CMD (`node apps/live`) | **keine** (siehe Edge-Case E-01) | – | `always` | – | – |
| `plane-db` | `plane-db` | `postgres:15.7-alpine` | `postgres -c 'max_connections=1000'` | `.env`; `POSTGRES_USER`, `POSTGRES_DB`, `POSTGRES_PASSWORD`, `PGDATA=/var/lib/postgresql/data` | – | `always` | – | `pgdata:/var/lib/postgresql/data` |
| `plane-redis` | `plane-redis` | `valkey/valkey:7.2.11-alpine` | Default | – | – | `always` | – | `redisdata:/data` |
| `plane-mq` | `plane-mq` | `rabbitmq:3.13.6-management-alpine` | Default | `.env`; `RABBITMQ_DEFAULT_USER=${RABBITMQ_USER}`, `RABBITMQ_DEFAULT_PASS=${RABBITMQ_PASSWORD}`, `RABBITMQ_DEFAULT_VHOST=${RABBITMQ_VHOST}` | – | `always` | – | `rabbitmq_data:/var/lib/rabbitmq` |
| `plane-minio` | `plane-minio` | `docker.io/pgsty/silo:RELEASE.2026-09-16T00-00-00Z` | `server /export --console-address ":9090"` | `MINIO_ROOT_USER=${AWS_ACCESS_KEY_ID}`, `MINIO_ROOT_PASSWORD=${AWS_SECRET_ACCESS_KEY}` | – | `always` | – | `uploads:/export` |
| `proxy` | `proxy` | Build `./apps/proxy` / `Dockerfile.ce` | Image-CMD | `FILE_SIZE_LIMIT=${FILE_SIZE_LIMIT:-5242880}`, `BUCKET_NAME=${AWS_S3_BUCKET_NAME:-uploads}` | `web`, `api`, `space`, `admin` | `always` | `${LISTEN_HTTP_PORT}:80`, `${LISTEN_HTTPS_PORT}:443` | – |

Volumes: `pgdata`, `redisdata`, `uploads`, `rabbitmq_data`.

#### 2.6.2 `docker-compose-local.yml` (Entwicklung)

Netzwerk `dev_env` (bridge). Volumes `redisdata`, `uploads`, `pgdata`, `rabbitmq_data`.

| Service | Image / Build | Kommando | Env | depends_on | Restart | Host-Ports | Volumes |
|---|---|---|---|---|---|---|---|
| `plane-redis` | `valkey/valkey:7.2.11-alpine` | Default | – | – | `unless-stopped` | `6379:6379` | `redisdata:/data` |
| `plane-mq` | `rabbitmq:3.13.6-management-alpine` | Default | `.env` + `RABBITMQ_DEFAULT_*` | – | `unless-stopped` | **keine** | `rabbitmq_data:/var/lib/rabbitmq` |
| `plane-minio` | silo-Image | Entrypoint-Shell: `mkdir -p /export/${AWS_S3_BUCKET_NAME}`; `silo server /export --console-address ':9090' &`; `sleep 5`; `mc alias set myminio http://localhost:9000 …`; `mc mb myminio/${AWS_S3_BUCKET_NAME} -p \|\| true`; `tail -f /dev/null` | `.env` + `MINIO_ROOT_USER/PASSWORD` | – | `unless-stopped` | `9000:9000`, `9090:9090` | `uploads:/export` |
| `plane-db` | `postgres:15.7-alpine` | `postgres -c 'max_connections=1000'` | `.env` + `PGDATA` | – | `unless-stopped` | `5432:5432` | `pgdata:/var/lib/postgresql/data` |
| `api` | Build `./apps/api` / `Dockerfile.dev` | `./bin/docker-entrypoint-api-local.sh` | `./apps/api/.env` | `plane-db`, `plane-redis`, `plane-mq` | `unless-stopped` | `8000:8000` | `./apps/api:/code` |
| `worker` | wie api | `./bin/docker-entrypoint-worker.sh` | `./apps/api/.env` | `api`, `plane-db`, `plane-redis` | `unless-stopped` | – | `./apps/api:/code` |
| `beat-worker` | wie api | `./bin/docker-entrypoint-beat.sh` | `./apps/api/.env` | `api`, `plane-db`, `plane-redis` | `unless-stopped` | – | `./apps/api:/code` |
| `migrator` | wie api | `./bin/docker-entrypoint-migrator.sh --settings=plane.settings.local` | `./apps/api/.env` | `plane-db`, `plane-redis` | `"no"` | – | `./apps/api:/code` |

Frontends und `live` laufen in diesem Modus **nicht** im Container, sondern per `pnpm dev` (Turbo, `--concurrency=18`) auf dem Host (`CONTRIBUTING.md` Z. 70–80).

#### 2.6.3 `deployments/cli/community/docker-compose.yml` (kanonisches Self-Hosting, Images aus Docker Hub)

YAML-Anker (`x-…`) mit Defaults: `x-db-env` (`PGHOST` plane-db, `PGDATABASE` plane, `POSTGRES_USER` plane, `POSTGRES_PASSWORD` plane, `POSTGRES_DB` plane, `POSTGRES_PORT` 5432, `PGDATA` /var/lib/postgresql/data), `x-redis-env` (`REDIS_HOST` plane-redis, `REDIS_PORT` 6379, `REDIS_URL` redis://plane-redis:6379/, `REDIS_SSL_CERT_REQS` required, `REDIS_SSL_CA_CERTS` leer), `x-minio-env` (`MINIO_ROOT_USER=${AWS_ACCESS_KEY_ID:-access-key}`, `MINIO_ROOT_PASSWORD=${AWS_SECRET_ACCESS_KEY:-secret-key}`), `x-aws-s3-env` (`AWS_REGION` leer, `AWS_ACCESS_KEY_ID` access-key, `AWS_SECRET_ACCESS_KEY` secret-key, `AWS_S3_ENDPOINT_URL` http://plane-minio:9000, `AWS_S3_BUCKET_NAME` uploads), `x-proxy-env` (`APP_DOMAIN` localhost, `FILE_SIZE_LIMIT` 5242880, `CERT_EMAIL`, `CERT_ACME_CA`, `CERT_ACME_DNS`, `LISTEN_HTTP_PORT` 80, `LISTEN_HTTPS_PORT` 443, `BUCKET_NAME=${AWS_S3_BUCKET_NAME:-uploads}`, `SITE_ADDRESS` :80, `TRUSTED_PROXIES` 0.0.0.0/0), `x-mq-env` (`RABBITMQ_HOST` plane-mq, `RABBITMQ_PORT` 5672, `RABBITMQ_DEFAULT_USER/PASS/VHOST` plane, `RABBITMQ_VHOST` plane), `x-live-env` (`API_BASE_URL` http://api:8000, `LIVE_SERVER_SECRET_KEY`), `x-app-env` (`WEB_URL` http://localhost, `DEBUG` 0, `CORS_ALLOWED_ORIGINS`, `GUNICORN_WORKERS` **fest 1**, `USE_MINIO` 1, `DATABASE_URL` postgresql://plane:plane@plane-db/plane, `SECRET_KEY`, `AMQP_URL` amqp://plane:plane@plane-mq:5672/plane, `API_KEY_RATE_LIMIT` 60/minute, `NUM_PROXIES`, `MINIO_ENDPOINT_SSL` 0, `LIVE_SERVER_SECRET_KEY`, `WEBHOOK_ALLOWED_IPS`, `WEBHOOK_ALLOWED_HOSTS`).

| Service | Image | Kommando | Environment | Replicas-Variable | Restart-Policy | depends_on | Volumes |
|---|---|---|---|---|---|---|---|
| `web` | `makeplane/plane-frontend:${APP_RELEASE:-stable}` | Image | – | `WEB_REPLICAS` (1) | `any` | `api`, `worker` | – |
| `space` | `makeplane/plane-space:…` | Image | – | `SPACE_REPLICAS` (1) | `any` | `api`, `worker`, `web` | – |
| `admin` | `makeplane/plane-admin:…` | Image | – | `ADMIN_REPLICAS` (1) | `any` | `api`, `web` | – |
| `live` | `makeplane/plane-live:…` | Image | `live-env` + `redis-env` | `LIVE_REPLICAS` (1) | `any` | `api`, `web` | – |
| `api` | `makeplane/plane-backend:…` | `./bin/docker-entrypoint-api.sh` | `app-env`, `db-env`, `redis-env`, `minio-env`, `aws-s3-env`, `proxy-env` | `API_REPLICAS` (1) | `any` | `plane-db`, `plane-redis`, `plane-mq` | `logs_api:/code/plane/logs` |
| `worker` | dto. | `./bin/docker-entrypoint-worker.sh` | dto. | `WORKER_REPLICAS` (1) | `any` | `api`, `plane-db`, `plane-redis`, `plane-mq` | `logs_worker:/code/plane/logs` |
| `beat-worker` | dto. | `./bin/docker-entrypoint-beat.sh` | dto. | `BEAT_WORKER_REPLICAS` (1) | `any` | dto. | `logs_beat-worker:/code/plane/logs` |
| `migrator` | dto. | `./bin/docker-entrypoint-migrator.sh` | dto. | fest 1 | `on-failure` | `plane-db`, `plane-redis` | `logs_migrator:/code/plane/logs` |
| `plane-db` | `postgres:15.7-alpine` | `postgres -c 'max_connections=1000'` | `db-env` | 1 | `any` | – | `pgdata` |
| `plane-redis` | `valkey/valkey:7.2.11-alpine` | Default | – | 1 | `any` | – | `redisdata:/data` |
| `plane-mq` | `rabbitmq:3.13.6-management-alpine` | Default | `mq-env` | 1 | `any` | – | `rabbitmq_data:/var/lib/rabbitmq` |
| `plane-minio` | silo-Image | `server /export --console-address ":9090"` | `minio-env` | 1 | `any` | – | `uploads:/export` |
| `proxy` | `makeplane/plane-proxy:…` | Image | `proxy-env` | 1 | `any` | `web`, `api`, `space`, `admin`, `live` | `proxy_config:/config`, `proxy_data:/data`; Ports `80→${LISTEN_HTTP_PORT:-80}`, `443→${LISTEN_HTTPS_PORT:-443}` (`mode: host`) |

Volumes: `pgdata`, `redisdata`, `uploads`, `logs_api`, `logs_worker`, `logs_beat-worker`, `logs_migrator`, `rabbitmq_data`, `proxy_config`, `proxy_data`. Kommentare im File: „Comment this if you already have a database running“ (plane-db), „… using any external s3 compatible storage“ (plane-minio), „… already have a reverse proxy running“ (proxy).

`deployments/cli/community/build.yml`: lokale Builds aller sechs Images mit Tag `${DOCKERHUB_USER:-local}/plane-{frontend,space,admin,live,backend,proxy}:${APP_RELEASE:-latest}`.

#### 2.6.4 AIO-Image (`deployments/aio/community/`)

Ein Container (`python:3.12.12-alpine` + Node aus `node:22-alpine`) mit **supervisord**; erwartet externe PostgreSQL, Redis, RabbitMQ und S3 (`DEP/aio/community/README.md`, `start.sh`).

| Programm (supervisor.conf) | Verzeichnis | Kommando | Env | Priority | autorestart | Logs |
|---|---|---|---|---|---|---|
| `migrator` | `/app/backend` | `./bin/docker-entrypoint-migrator.sh` | – | 10 | `unexpected` | `/app/logs/access/migrator.log`, `/app/logs/error/migrator.err.log` |
| `space` | `/app/space/apps/space` | `./node_modules/.bin/react-router-serve ./build/server/index.js` | `PORT=3002,HOSTNAME=0.0.0.0` | 15 | `true` | `space.log`, `space.err.log` |
| `api` | `/app/backend` | `./bin/docker-entrypoint-api.sh` | `PORT=3004,HOSTNAME=0.0.0.0` | 15 | `true` | `api.log`, `api.err.log` |
| `worker` | `/app/backend` | `./bin/docker-entrypoint-worker.sh` | – | 20 | `true` | `worker.log`, `worker.err.log` |
| `beat` | `/app/backend` | `./bin/docker-entrypoint-beat.sh` | – | 20 | `true` | `beat.log`, `beat.err.log` |
| `live` | – | `node /app/live/apps/live` | `PORT=3005,HOSTNAME=0.0.0.0` | 20 | `true` | `live.log`, `live.err.log` |
| `proxy` | `/app/proxy` | `caddy run --config /app/proxy/Caddyfile` (= `Caddyfile.aio.ce`) | – | 20 | `true` | `proxy.log`, `proxy.err.log` |

web und admin werden im AIO **nicht** als Prozess betrieben, sondern als statische Dateien `/app/web` bzw. `/app/admin` direkt von Caddy ausgeliefert (`DEP/aio/community/Dockerfile`, `apps/proxy/Caddyfile.aio.ce`). Volumes `/app/data`, `/app/logs`; Ports 80, 443.

#### 2.6.5 Docker Swarm / Kubernetes

- Swarm: `deployments/swarm/community/swarm.sh` lädt dieselbe `docker-compose.yml` + `variables.env` aus dem GitHub-Release (Fallback `raw.githubusercontent.com/makeplane/plane/$BRANCH/deployments/cli/community`) und führt `docker stack deploy -c … $stack_name` aus (Details 2.26).
- Kubernetes: nur Verweis auf das Helm-Chart `makeplane/plane-ce` auf Artifact Hub (`deployments/kubernetes/community/README.md`); kein Chart im Repo.

### 2.7 Ports & Base-Paths

| Komponente | Base-Path (Default) | Dev-Port (Host, `pnpm dev`) | Container-Port (Docker) | AIO-Port | Konfiguration | Quelle |
|---|---|---|---|---|---|---|
| proxy | – | – | 80, 443 (publiziert über `LISTEN_HTTP_PORT`/`LISTEN_HTTPS_PORT`) | 80, 443 | `SITE_ADDRESS` (Default `:80`) | `apps/proxy/Caddyfile.ce`, `docker-compose.yml` |
| web | `/` | 3000 | 3000 (Caddy) | statisch | `VITE_WEB_BASE_URL`, `VITE_WEB_BASE_PATH` (nur Konstante, kein Vite-`base`) | `apps/web/package.json`, `apps/web/caddy/Caddyfile` |
| admin | `/god-mode` (Router-`basename` → `/god-mode/`) | 3001 | 3000 (Caddy, Dateien unter `/god-mode`) | statisch `/app/admin` | `VITE_ADMIN_BASE_URL`, `VITE_ADMIN_BASE_PATH` | `apps/admin/*` |
| space | `/spaces` (→ `/spaces/`) | 3002 | 3000 (react-router-serve) | 3002 | `VITE_SPACE_BASE_URL`, `VITE_SPACE_BASE_PATH` | `apps/space/*` |
| live | `/live` | 3100 (`apps/live/.env.example` `PORT=3100`) | 3000 (`PORT`-Default) | 3005 | `PORT`, `LIVE_BASE_PATH` | `LIVE/env.ts` |
| api | `/api`, `/auth`, `/static`, `/` | 8000 (`runserver`, auch in local-compose publiziert) | 8000 (`PORT`, Default 8000) | 3004 | `PORT` | `apps/api/bin/docker-entrypoint-api.sh` |
| api/OpenAPI | `/api/schema/`, `/api/schema/swagger-ui/`, `/api/schema/redoc/` | – | – | – | `ENABLE_DRF_SPECTACULAR=1` | `API/urls.py` |
| plane-db | – | 5432 (local-compose) | 5432 | extern | – | `docker-compose-local.yml` |
| plane-redis | – | 6379 (local-compose) | 6379 | extern | – | dto. |
| plane-mq | – | nicht publiziert | 5672 (AMQP), Management-Plugin im Image | extern | – | dto. |
| plane-minio | Bucket-Pfad `/uploads` (= `AWS_S3_BUCKET_NAME`) | 9000 (S3), 9090 (Konsole) | 9000/9090 | extern | – | dto. |

Abweichende Port-Angaben in Dev-Dockerfiles (nicht genutzt durch Compose): `apps/admin/Dockerfile.dev` `EXPOSE 3000` (Dev-Script nutzt 3001), `apps/space/Dockerfile.dev` `EXPOSE 3002`, `apps/live/Dockerfile.dev` `EXPOSE 3003`, `apps/web/Dockerfile.dev` `EXPOSE 3000`. Die AIO-README nennt „Web App (Port 3001)“ und „Admin (Port 3003)“, was nicht mehr dem Caddyfile entspricht (statische Auslieferung) (`DEP/aio/community/README.md`).

### 2.8 Proxy-Routing-Regeln

#### 2.8.1 `apps/proxy/Caddyfile.ce` (Produktion, in `apps/proxy/Dockerfile.ce` nach `/etc/caddy/Caddyfile` kopiert)

Snippet `(plane_proxy)`, importiert in `{$SITE_ADDRESS} { import plane_proxy }`. Reihenfolge der Direktiven im Snippet (Caddy sortiert `redir` vor `reverse_proxy`; bei mehreren `reverse_proxy` gewinnt der spezifischste Matcher gemäß Caddy-Direktivensortierung nach Pfadlänge):

| # | Direktive | Matcher | Ziel | Wirkung |
|---|---|---|---|---|
| 1 | `request_body { max_size {$FILE_SIZE_LIMIT} }` | alle | – | Request-Bodys > `FILE_SIZE_LIMIT` Bytes werden abgewiesen (HTTP 413) |
| 2 | `redir /spaces /spaces/ permanent` | exakt `/spaces` | – | 301 (permanent) auf `/spaces/` |
| 3 | `reverse_proxy /spaces/*` | `/spaces/*` | `space:3000` | Space-SSR |
| 4 | `redir /god-mode /god-mode/ permanent` | exakt `/god-mode` | – | 301 (permanent) auf `/god-mode/` |
| 5 | `reverse_proxy /god-mode/*` | `/god-mode/*` | `admin:3000` | Admin-SPA |
| 6 | `reverse_proxy /live/*` | `/live/*` | `live:3000` | HTTP + WebSocket |
| 7 | `reverse_proxy /api/*` | `/api/*` | `api:8000` | REST |
| 8 | `reverse_proxy /auth/*` | `/auth/*` | `api:8000` | Auth-Flows |
| 9 | `reverse_proxy /static/*` | `/static/*` | `api:8000` | Django-Static (WhiteNoise) |
| 10 | `reverse_proxy /{$BUCKET_NAME}/*` | `/uploads/*` (Default) | `plane-minio:9000` | Objekt-GET/Presigned |
| 11 | `reverse_proxy /{$BUCKET_NAME}` | exakt `/uploads` | `plane-minio:9000` | Presigned-POST (Bucket-Root) |
| 12 | `reverse_proxy /*` | Rest | `web:3000` | Web-SPA |

Globale Optionen: `{$CERT_EMAIL}` (Zeile wird als `email …`-Direktive erwartet: Kommentar in `.env.example` „set CERT_EMAIl="email <EMAIL_ADDRESS>"“), `acme_ca {$CERT_ACME_CA:https://acme-v02.api.letsencrypt.org/directory}`, `{$CERT_ACME_DNS}` (z. B. `acme_dns <provider> <api-key>`), `servers { max_header_size 25MB; client_ip_headers X-Forwarded-For X-Real-IP; trusted_proxies static {$TRUSTED_PROXIES:0.0.0.0/0} }`. Nicht geroutet: `/robots.txt` geht an **web** (nicht an die API-View `robots_txt`), `/` geht an web (API-Health-Check `/` nur intern erreichbar).

#### 2.8.2 `apps/proxy/Caddyfile.aio.ce` (AIO)

| Direktive | Matcher | Ziel |
|---|---|---|
| `request_body { max_size {$FILE_SIZE_LIMIT} }` | alle | – |
| `handle /spaces/*` | `/spaces/*` | `reverse_proxy localhost:3002` |
| `handle /live/*` | `/live/*` | `reverse_proxy localhost:3005` |
| `handle /api/*` | `/api/*` | `reverse_proxy localhost:3004` |
| `handle /auth/*` | `/auth/*` | `reverse_proxy localhost:3004` |
| `handle_path /god-mode*` | `/god-mode*` (Präfix wird entfernt) | `root * /app/admin`, `try_files {path} {path}/ /index.html`, `file_server` |
| `handle_path /*` | Rest | `root * /app/web`, `try_files {path} {path}/ /index.html`, `file_server` |

Globale Optionen identisch zu 2.8.1. **Fehlend** gegenüber `Caddyfile.ce`: Redirects `/spaces`→`/spaces/` und `/god-mode`→`/god-mode/` (bei `/god-mode` greift `handle_path /god-mode*` ohnehin), Route `/static/*` (Django-Static nicht erreichbar), Bucket-Route (AIO setzt `USE_MINIO=0`, externe S3-URL) (`apps/proxy/Caddyfile.aio.ce`, `DEP/aio/community/start.sh`).

#### 2.8.3 Container-interne Webserver

| Datei | Listener | Regeln | Quelle |
|---|---|---|---|
| `apps/web/caddy/Caddyfile` | `:3000`, Root `/usr/share/caddy/html` | `servers { trusted_proxies static private_ranges }`, `order rate_limit before file_server`; `rate_limit` Zone `static`, Key `{client_ip}`, **300 Events / 1 m**; Header `X-Frame-Options "DENY"`, `X-Content-Type-Options "nosniff"`, `X-XSS-Protection "1; mode=block"` (HSTS am TLS-Terminator); `try_files {path} /index.html`; `file_server`; Log stdout `format console` | `apps/web/caddy/Caddyfile` |
| `apps/admin/caddy/Caddyfile` | `:3000`, Root `/usr/share/caddy/html` | identisch zu web, aber `try_files {path} /god-mode/index.html` | `apps/admin/caddy/Caddyfile` |
| `apps/space/nginx/nginx.conf` | `listen 3000` | `worker_processes 4`, `worker_connections 1024`, `set_real_ip_from 0.0.0.0/0`, `real_ip_header X-Forwarded-For`, `real_ip_recursive on`, `limit_req_zone $binary_remote_addr zone=mylimit:10m rate=10r/s` (Zone definiert, aber nirgends angewandt), `location /` → `root /usr/share/nginx/html`, `try_files $uri $uri/ /spaces/index.html`. **Wird von keinem Dockerfile verwendet** (Space läuft per `react-router-serve`) – Altlast. | `apps/space/nginx/nginx.conf`, `apps/space/Dockerfile.space` |

### 2.9 Dockerfiles

| Datei | Stages | Basis-Images | Build-Args (Default) | Laufzeit / CMD | EXPOSE | HEALTHCHECK | Besonderheiten |
|---|---|---|---|---|---|---|---|
| `apps/api/Dockerfile.api` | `uv` (ghcr.io/astral-sh/uv:0.12.21@sha256:a7ae…), Haupt | `python:3.12.12-alpine` | `APK_SECURITY_PATCH=2026-09-07` | `./bin/docker-entrypoint-api.sh` | 8000 | – | ENV `PYTHONDONTWRITEBYTECODE=1`, `PYTHONUNBUFFERED=1`, `PIP_DISABLE_PIP_VERSION_CHECK=1`, `INSTANCE_CHANGELOG_URL=https://sites.plane.so/pages/691ef037bcfe416a902e48cb55f59891/`, `UV_PROJECT_ENVIRONMENT=/usr/local`, `UV_PYTHON_DOWNLOADS=never`, `UV_COMPILE_BYTECODE=1`, `UV_NO_CACHE=1`; apk `libpq libxslt xmlsec ca-certificates openssl libffi-dev bash~=5.3`; Build-Deps temporär (`g++ gcc cargo git make postgresql-dev libc-dev linux-headers`); `uv sync --locked --inexact --no-default-groups --group production`; kopiert `manage.py`, `plane/`, `templates/`, `package.json`, `bin/`; `mkdir /code/plane/logs`; `chmod -R 777 /code` |
| `apps/api/Dockerfile.dev` | `uv`, `backend` | `python:3.12.5-alpine` | – | `./bin/docker-entrypoint-api-local.sh` | 8000 | – | zusätzlich `nodejs-current`; `uv sync --locked --inexact` (Gruppen dev+test); `COPY . .` |
| `apps/web/Dockerfile.web` | `base` (node:22-alpine, corepack), `builder` (`turbo prune --scope=web --docker`, `TURBO_VERSION=2.10.11`), `installer` (`pnpm fetch` + `pnpm install --offline --frozen-lockfile`, Build `pnpm turbo run build --filter=web`), `caddy-builder` (caddy:2.11.7-builder-alpine, `xcaddy build --with github.com/mholt/caddy-ratelimit`, Upgrade `x/crypto v0.57.0`, `x/net v0.60.0`, `x/text v0.42.0`, `grpc v1.83.2`, `otel v1.46.0`), `production` (caddy:2.11.4-alpine) | s. Stages | `VITE_API_BASE_URL=""`, `VITE_ADMIN_BASE_URL=""`, `VITE_ADMIN_BASE_PATH="/god-mode"`, `VITE_LIVE_BASE_URL=""`, `VITE_LIVE_BASE_PATH="/live"`, `VITE_SPACE_BASE_URL=""`, `VITE_SPACE_BASE_PATH="/spaces"`, `VITE_WEB_BASE_URL=""`, `APK_SECURITY_PATCH` | `caddy run --config /etc/caddy/Caddyfile` | 3000 | `curl -fsS http://127.0.0.1:3000/` (30 s/5 s/10 s/3) | ENV `NEXT_TELEMETRY_DISABLED=1`, `TURBO_TELEMETRY_DISABLED=1`; kopiert `apps/web/build/client` → `/usr/share/caddy/html`; Assert, dass Caddy-Binary grpc v1.83.2 enthält |
| `apps/web/Dockerfile.dev` | eine | `node:22-alpine` | – | `pnpm dev --filter=web` | 3000 | – | `pnpm add -g turbo` (unversioniert), `pnpm install` |
| `apps/admin/Dockerfile.admin` | `base`, `builder` (`turbo prune --scope=admin`), `installer` (`NODE_ENV=production`, `--prod=false`), `caddy-builder`, `production` | node:22-alpine, caddy | `VITE_API_BASE_URL=""`, `VITE_API_BASE_PATH="/api"`, `VITE_ADMIN_BASE_URL=""`, `VITE_ADMIN_BASE_PATH="/god-mode"`, `VITE_SPACE_BASE_URL=""`, `VITE_SPACE_BASE_PATH="/spaces"`, `VITE_LIVE_BASE_URL=""`, `VITE_LIVE_BASE_PATH="/live"`, `VITE_WEB_BASE_URL=""`, `VITE_WEB_BASE_PATH=""`, `VITE_WEBSITE_URL="https://plane.so"`, `VITE_SUPPORT_EMAIL="support@plane.so"`, `APK_SECURITY_PATCH` | Caddy | 3000 | `curl -fsS http://127.0.0.1:3000/god-mode` | ENV `TURBO_TELEMETRY_DISABLED=1`, `CI=1`; kopiert `apps/admin/build/client` → `/usr/share/caddy/html/god-mode` |
| `apps/admin/Dockerfile.dev` | eine | node:22-alpine | – | `pnpm dev --filter=admin` | 3000 | – | ENV `VITE_ADMIN_BASE_PATH="/god-mode"` |
| `apps/space/Dockerfile.space` | `base`, `builder`, `installer` (Build-Args wie admin), `runner` | node:22-alpine | wie admin | `./node_modules/.bin/react-router-serve ./build/server/index.js` (WORKDIR `/app/apps/space`) | 3000 | `curl -fsS http://127.0.0.1:3000/spaces/` | `NODE_ENV=production`; `apk del go`; npm/npx entfernt; esbuild/tsgolint-Binaries gelöscht; kopiert `apps/space/build`, `apps/space/node_modules`, `node_modules` |
| `apps/space/Dockerfile.dev` | eine | node:22-alpine | – | `pnpm dev --filter=space` | 3002 | – | ENV `VITE_SPACE_BASE_PATH="/spaces"` |
| `apps/live/Dockerfile.live` | `base`, `builder` (`turbo prune --scope=live`), `installer` (Build `--filter=live`), `runner` | node:22-alpine | `TURBO_VERSION=2.10.11`, `APK_SECURITY_PATCH` | `node apps/live` (WORKDIR `/app`) | 3000 | – | kopiert `packages/`, `apps/live/dist`, `apps/live/node_modules`, `node_modules`, `apps/live/package.json`; npm entfernt |
| `apps/live/Dockerfile.dev` | eine | node:22-alpine | – | `pnpm dev --filter=live` | 3003 | – | – |
| `apps/proxy/Dockerfile.ce` | `caddy-builder` (caddy:2.11.7-builder-alpine; Module `caddy-dns/cloudflare@v0.2.1`, `caddy-dns/digitalocean@04bde28…`, `mholt/caddy-l4@6faae83…`, `go-jose/v3@v3.0.5`, `go-jose/v4@v4.1.5`, `grpc@v1.83.2`, `otel@v1.46.0`, `otel/sdk@v1.46.0`; Build-Tags `nobadger,nomysql,nopgx`), Laufzeit `caddy:2.11.4-alpine` | – | `APK_SECURITY_PATCH` | Caddy-Default (`/etc/caddy/Caddyfile`) | (80/443 via Caddy) | – | apk `nss-tools bash curl`; kopiert `Caddyfile.ce` |
| `deployments/aio/community/Dockerfile` | `binfmt`, `node`, Bild-Stages aus `makeplane/plane-{frontend,backend,space,admin,live,proxy}:${PLANE_VERSION}` (Default `v0.27.1`), `runner` (python:3.12.12-alpine) | – | `PLANE_VERSION`, `APK_SECURITY_PATCH` | `/app/start.sh` | 80, 443 | – | apk `libstdc++ libgcc libpq libxslt xmlsec nss-tools bash curl uuidgen ncdu vim`; `pip install supervisor`; kopiert `dist/Caddyfile`, `dist/plane.env` |

### 2.10 Entrypoint-Skripte & Start-Kommandos (`apps/api/bin/`)

| Skript | Schritte (in Reihenfolge) |
|---|---|
| `docker-entrypoint-api.sh` | `set -e`; `python manage.py wait_for_db`; `python manage.py wait_for_migrations`; Maschinen-Signatur = SHA-256 über `hostname`, erste MAC (`ip link show`), `/proc/cpuinfo`, `free -h`, `df -h` → `export MACHINE_SIGNATURE`; `python manage.py register_instance "$MACHINE_SIGNATURE"`; `python manage.py configure_instance`; `python manage.py create_bucket`; `python manage.py clear_cache`; `python manage.py collectstatic --noinput`; `exec gunicorn -w "$GUNICORN_WORKERS" -k uvicorn.workers.UvicornWorker plane.asgi:application --bind 0.0.0.0:"${PORT:-8000}" --max-requests 1200 --max-requests-jitter 1000 --access-logfile -` |
| `docker-entrypoint-api-local.sh` | wie oben bis `clear_cache` (ohne `collectstatic`), dann `python manage.py runserver 0.0.0.0:8000 --settings=plane.settings.local` |
| `docker-entrypoint-worker.sh` | `set -e`; `wait_for_db`; `wait_for_migrations`; `celery -A plane worker -l info` |
| `docker-entrypoint-beat.sh` | `set -e`; `wait_for_db`; `wait_for_migrations`; `celery -A plane beat -l info` |
| `docker-entrypoint-migrator.sh` | `set -e`; `python manage.py wait_for_db $1`; `python manage.py migrate $1` (`$1` z. B. `--settings=plane.settings.local`) |

Management-Commands mit Startbezug (Verhalten in Abschnitt 3.1): `wait_for_db` (`API/db/management/commands/wait_for_db.py`), `wait_for_migrations` (`…/wait_for_migrations.py`), `register_instance` (`API/license/management/commands/register_instance.py`), `configure_instance` (`…/configure_instance.py`), `create_bucket` (`API/db/management/commands/create_bucket.py`), `clear_cache` (`…/clear_cache.py`, optional `--key`). Weitere Commands (fachlich, siehe Datenmodell-Analyse A02a): `activate_user`, `copy_issue_comment_to_description`, `create_dummy_data`, `create_instance_admin`, `create_project_member`, `fix_duplicate_sequences`, `reactivate_workspace_member`, `reset_password`, `sync_issue_description_version`, `sync_issue_version`, `test_email`, `update_bucket`, `update_deleted_workspace_slug` (`API/db/management/commands/`).

### 2.11 Vollständige ENV-Tabelle

Legende: „Code-Default“ = Wert, wenn Variable fehlt; „Template“ = Wert in `apps/api/.env.example` (API), `apps/live/.env.example`, `apps/{web,admin,space}/.env.example`, Root-`.env.example` bzw. `deployments/cli/community/variables.env` (CLI). `S/` = `API/settings/`.

#### 2.11.1 API-Server: Kern-Einstellungen (Django-Settings & direkte `os.environ`-Zugriffe)

| Variable | Code-Default | Template | Gelesen in | Bedeutung / Effekt |
|---|---|---|---|---|
| `DJANGO_SETTINGS_MODULE` | `plane.settings.production` (gesetzt durch `os.environ.setdefault` in `API/celery.py`, `API/asgi.py`, `API/wsgi.py`, `apps/api/manage.py`; `API/__init__.py` importiert `celery` → Default greift bei jedem Import von `plane`) | Test: `plane.settings.test` (`pytest.ini`, `docker-compose-test.yml`) | s. links | Wahl der Settings: `production`, `local`, `test` |
| `SECRET_KEY` | zufällig pro Prozess (`get_random_secret_key()`; auch bei leerem String) | API-Template: wird von `setup.sh` angehängt (50 Zeichen); CLI: `change-this-key-on-deployment` | `S/common.py`; Pflicht in `configure_instance` (`CommandError` wenn leer) | Django-Signaturen (Sessions, CSRF, Password-Reset), **Schlüsselableitung für Fernet-Verschlüsselung der Instanz-Konfiguration** (`API/license/utils/encryption.py`), HMAC-Token-Identifier im API-Log (`API/middleware/logger.py`); kritischer Log, wenn Wert `60gp0byfz2dvffa45cxl20p1scy9xbpf6d8c5y0geejgkyp1b5` oder `change-this-key-on-deployment` |
| `DEBUG` | `0` (common/production: `int(...)`/`== 1`); `local.py`: `"1"` | `0` | `S/common.py`, `S/production.py`, `S/local.py` | Debug-Modus; in `local` + DEBUG: `debug_toolbar` (App + Middleware, `/__debug__/`); bei DEBUG kein Response-Cache (`API/utils/cache.py`), Query-Count-Ausgabe (`API/api/views/base.py`), Datei-Log `plane-debug.log` statt `plane-error.log` |
| `ALLOWED_HOSTS` | `*` | – | `S/common.py` | Komma-getrennt |
| `WEBHOOK_ALLOWED_IPS` | leer | CLI: leer | `S/common.py` | Komma-getrennte IPs/CIDRs, die trotz privater Adresse als Webhook-/Link-Ziel erlaubt sind; ungültige Einträge → Warnung, übersprungen |
| `WEBHOOK_ALLOWED_HOSTS` | leer | CLI: leer | `S/common.py` | Hostnamen (lowercase, ohne Punkt am Ende), die den Private-IP-SSRF-Check umgehen |
| `WEBHOOK_DISALLOWED_DOMAINS` | leer | – | `S/common.py` | Gesperrte Domains inkl. Subdomains (Request-Host wird bei Validierung immer ergänzt) |
| `NUM_PROXIES` | nicht gesetzt (DRF-Default `None`) | API: auskommentiert; CLI: leer | `S/common.py` | Nur dezimal, max. 3 Ziffern, sonst Warnung + ignoriert; DRF-Throttle-Client-IP aus `X-Forwarded-For` |
| `API_KEY_RATE_LIMIT` | `60/minute` | `60/minute` | `S/common.py` → `API/api/rate_limit.py` | Rate für `/api/v1/` pro API-Key |
| `AUTHENTICATION_RATE_LIMIT` | `10/minute` | CLI/AIO: `10/minute` | `API/authentication/rate_limit.py` | Rate pro Client-IP für Auth-Endpunkte |
| `CORS_ALLOWED_ORIGINS` | leer → `CORS_ALLOW_ALL_ORIGINS = True` | `http://localhost:3000,http://localhost:3001,http://localhost:3002,http://localhost:3100`; CLI: `http://${APP_DOMAIN}` | `S/common.py` | Komma-getrennt; zugleich `CSRF_TRUSTED_ORIGINS`; Basis für Secure-Cookie-Ermittlung und Origin-Check (`API/authentication/session.py`) |
| `DATABASE_URL` | – | `postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}`; CLI: leer (Compose-Default `postgresql://plane:plane@plane-db/plane`) | `S/common.py` (`dj_database_url.config()`) | Hat Vorrang vor `POSTGRES_*` |
| `POSTGRES_DB` / `POSTGRES_USER` / `POSTGRES_PASSWORD` / `POSTGRES_HOST` | – | `plane` / `plane` / `plane` / `plane-db` | `S/common.py` | Nur wenn `DATABASE_URL` leer; Engine `django.db.backends.postgresql` |
| `POSTGRES_PORT` | `5432` | `5432` | `S/common.py` | dto. |
| `ENABLE_READ_REPLICA` | `0` | – | `S/common.py` | `1` → DB-Alias `replica`, Router `plane.utils.core.dbrouters.ReadReplicaRouter`, Middleware `ReadReplicaRoutingMiddleware` am Ende angehängt |
| `DATABASE_READ_REPLICA_URL` | – | – | `S/common.py` | Replica per URL (Vorrang) |
| `POSTGRES_READ_REPLICA_DB` / `_USER` / `_PASSWORD` / `_HOST` | – | – | `S/common.py` | Replica-Einzelwerte |
| `POSTGRES_READ_REPLICA_PORT` | `5432` | – | `S/common.py` | dto. |
| `REDIS_URL` | – (None) | `redis://${REDIS_HOST}:6379/`; CLI: leer (Compose-Default `redis://plane-redis:6379/`) | `S/common.py`, `S/redis.py`, `S/local.py` | Django-Cache (`django_redis`), direkter Client `redis_instance()` (db=0); `rediss://` aktiviert TLS |
| `REDIS_HOST` / `REDIS_PORT` | – | `plane-redis` / `6379` | nur Templates/Compose (API-Code liest sie **nicht**) | Nur zur Komposition von `REDIS_URL` |
| `REDIS_SSL_CERT_REQS` | effektiv `required` (Query-Parameter `ssl_cert_reqs` in der URL hat Vorrang) | `required` | `S/common.py` (`_redis_ssl_kwargs`) | `none` deaktiviert Zertifikats- und Hostname-Prüfung |
| `REDIS_SSL_CA_CERTS` | – | leer | `S/common.py` | Pfad zu CA-Bundle (im Container) |
| `USE_MINIO` | `0` | API: `0`; Root/CLI: `1`; AIO: `0` | `S/common.py`, `S/storage.py` | `1` → Presigned-URLs mit Endpoint = aktueller Request-Host; `AWS_S3_CUSTOM_DOMAIN = {WEB_URL.netloc}/{bucket}`; kritischer Log bei `AWS_SECRET_ACCESS_KEY == "secret-key"` |
| `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` | – (boto3-Default-Chain) | `access-key` / `secret-key` (durch `setup.sh`/`install.sh` ersetzt) | `S/common.py`, `S/storage.py`, `create_bucket`, `update_bucket` | S3-Zugang; identisch mit `MINIO_ROOT_USER/PASSWORD` |
| `AWS_S3_BUCKET_NAME` | `uploads` (`S/common.py`); **kein** Default in `S/storage.py`/`create_bucket` | `uploads` | dto. | Bucket; muss mit Proxy-`BUCKET_NAME` übereinstimmen |
| `AWS_REGION` | `""` | `""` | dto. | Region |
| `AWS_S3_ENDPOINT_URL` | – | API: `http://localhost:9000`; Root/CLI: `http://plane-minio:9000`; AIO: `https://s3.${AWS_REGION}.amazonaws.com` | dto. | S3-Endpoint |
| `MINIO_ENDPOINT_URL` | – | – | `S/common.py`, `S/storage.py` | Fallback für `AWS_S3_ENDPOINT_URL` |
| `MINIO_ENDPOINT_SSL` | – | `0` | `S/storage.py` | `1` erzwingt `https` beim MinIO-Endpoint aus Request-Host |
| `SIGNED_URL_EXPIRATION` | `3600` | `3600` | `S/storage.py` | Gültigkeit Presigned-URLs (Sekunden) |
| `FILE_SIZE_LIMIT` | `5242880` | `5242880` | `S/common.py` (`FILE_SIZE_LIMIT`, `DATA_UPLOAD_MAX_MEMORY_SIZE`), `API/license/api/views/instance.py` (`file_size_limit` in Instanz-Config) | Max. Upload-/Request-Body-Größe (Bytes) |
| `WEB_URL` | – | API: `http://localhost:8000`; CLI: `http://${APP_DOMAIN}` | `S/common.py`, `API/authentication/utils/host.py`, `API/license/bgtasks/telemetry_metrics.py` | Basis-Origin für Redirects/E-Mails, MinIO-Custom-Domain, Secure-Cookie-Ermittlung, Telemetrie-Domain |
| `APP_BASE_URL` | – (ungültige URL → None) | `http://localhost:3000` | `S/common.py` | Basis-URL web; Fallback für `WEB_URL` |
| `APP_BASE_PATH` | `/` | `""` | `S/common.py` | Wird im Code **nicht weiter verwendet** |
| `ADMIN_BASE_URL` | – | `http://localhost:3001` | `S/common.py`, `host.py` | Redirect-Ziel God-Mode |
| `ADMIN_BASE_PATH` | `/god-mode/` | `/god-mode` | `S/common.py`, `host.py` (normalisiert auf führenden/abschließenden `/`) | dto. |
| `SPACE_BASE_URL` | – | `http://localhost:3002` | `S/common.py`, `host.py` | Redirect-Ziel Space |
| `SPACE_BASE_PATH` | `/spaces/` | `/spaces` | dto. | dto. |
| `LIVE_BASE_URL` | – | `http://localhost:3100` | `S/common.py` → `LIVE_URL = urljoin(LIVE_BASE_URL, LIVE_BASE_PATH)` | Ziel für `convert-document` (`API/bgtasks/copy_s3_object.py`); leer → Konvertierung übersprungen |
| `LIVE_BASE_PATH` | `/live/` | `/live` | dto. | dto. |
| `LIVE_SERVER_SECRET_KEY` | – | `secret-key`; CLI/AIO: `change-this-key-on-deployment` | **Nicht** im API-Code gelesen (nur in Templates/Compose) | Nur vom Live-Server genutzt |
| `RABBITMQ_HOST` | `localhost` | `plane-mq` | `S/common.py` | Celery-Broker-URL (wenn `AMQP_URL` leer) |
| `RABBITMQ_PORT` | `5672` | `5672` | dto. | dto. |
| `RABBITMQ_USER` / `RABBITMQ_PASSWORD` | `guest` / `guest` | `plane` / `plane` | dto. | dto. |
| `RABBITMQ_VHOST` | `/` | `plane` | dto. | dto. |
| `AMQP_URL` | – | CLI: leer (Compose-Default `amqp://plane:plane@plane-mq:5672/plane`) | dto. | Vorrang vor `RABBITMQ_*` |
| `SESSION_COOKIE_AGE` | `604800` (7 Tage) | – | `S/common.py` | Laufzeit Benutzer-Session |
| `SESSION_COOKIE_NAME` | `session-id` | – | dto. | Cookie-Name web/space |
| `COOKIE_DOMAIN` | None | – | dto. | `SESSION_COOKIE_DOMAIN` und `CSRF_COOKIE_DOMAIN` |
| `SESSION_SAVE_EVERY_REQUEST` | `0` | – | dto. | Sliding Session |
| `ADMIN_SESSION_COOKIE_AGE` | `3600` | – | dto. | Laufzeit Admin-Cookie (`admin-session-id`) |
| `HARD_DELETE_AFTER_DAYS` | `60` | `60` | `S/common.py` → `deletion_task.hard_delete` | Endgültiges Löschen soft-gelöschter Datensätze |
| `API_ACTIVITY_LOG_RETENTION_DAYS` | `14` (ungültig/negativ → Default) | – | `S/common.py` (`_retention_days`) | Aufbewahrung `APIActivityLog` |
| `WEBHOOK_LOG_RETENTION_DAYS` | `14` | – | dto. | Aufbewahrung `WebhookLog` |
| `EMAIL_LOG_RETENTION_DAYS` | `7` | – | dto. | Aufbewahrung `EmailNotificationLog` (nach `sent_at`) |
| `UNUPLOADED_ASSET_DELETE_DAYS` | `7` | – | `API/bgtasks/file_asset_task.py` | Löschen nie hochgeladener Assets |
| `INSTANCE_CHANGELOG_URL` | `""`; Docker-Image-ENV: `https://sites.plane.so/pages/691ef037bcfe416a902e48cb55f59891/` | – | `S/common.py` → Instanz-Config `instance_changelog_url` | iframe-Quelle des Changelogs in web (`apps/web/components/global/product-updates/changelog.tsx`, 15-s-Timeout → Fallback) |
| `ENABLE_DRF_SPECTACULAR` | `0` | – | `S/common.py`, `API/urls.py` | `1` → `drf_spectacular` + Routen `/api/schema/…` |
| `SKIP_ENV_VAR` | `1` | – | `S/common.py` → `API/license/utils/instance_value.py` | `1`: Konfigurationswerte aus Tabelle `InstanceConfiguration` (Fallback Default); `0`: direkt aus ENV |
| `UNSPLASH_ACCESS_KEY` | – | – | `S/common.py` (`UNSPLASH_ACCESS_KEY`), `API/app/views/external/base.py`, Instanz-Config | Unsplash-Bildsuche |
| `GITHUB_ACCESS_TOKEN` | `False` | – | `S/common.py` | Im Code **nicht weiter verwendet** |
| `ANALYTICS_SECRET_KEY` / `ANALYTICS_BASE_API` | `False` | – | `S/common.py` | Im Code **nicht weiter verwendet** |
| `EMAIL_BACKEND` | prod/common: `django.core.mail.backends.smtp.EmailBackend` (fest); local: ENV, Default `django.core.mail.backends.console.EmailBackend`; test: `locmem` (fest) | – | `S/local.py` | Mail-Backend |
| `SCOUT_MONITOR` / `SCOUT_KEY` | `False` / `""` | – | `S/production.py` (`SCOUT_NAME = "Plane"`, App `scout_apm.django`) | Scout-APM |
| `GUNICORN_WORKERS` | **kein** Default (leerer Wert → gunicorn-Fehler) | `2`; CLI/AIO: `1` (CLI-Compose fest `1`) | `apps/api/bin/docker-entrypoint-api.sh` | gunicorn-Worker |
| `PORT` | `8000` | AIO: `3004` | dto. | gunicorn-Bind-Port |
| `MACHINE_SIGNATURE` | berechnet | – | `docker-entrypoint-api*.sh` | Argument für `register_instance` (wird im Command nicht gespeichert) |
| `APP_VERSION` | – → `package.json` `version` → `v0.1.0` | AIO: Release-Version | `API/license/management/commands/register_instance.py` | `Instance.current_version` |
| `IS_TEST` | `0` | – | dto. | `Instance.is_test` |
| `METRICS_PUSH_INTERVAL_MINUTES` | `360` (gültig `1…10 000 000`, sonst 360) | – | `API/celery.py` | Intervall Telemetrie-Push |
| `OTLP_ENDPOINT` | `https://telemetry.plane.so` | – | `API/utils/otlp_endpoints.py` | Telemetrie-Collector (gRPC `host:443` bei https, `host:4317` sonst; HTTP: `…/v1/metrics`) |
| `OTLP_METRICS_PROTOCOL` | `grpc` | – | `API/license/bgtasks/telemetry_metrics.py` | `grpc` oder `http` |
| `OTEL_EXPORTER_OTLP_METRICS_INSECURE` | `""` | – | dto. | `true` → unsicherer gRPC-Kanal |
| `SERVICE_NAME` | `plane-ce-api` | – | dto. | OTel-Resource `service.name` |
| `LLM_API_KEY` / `LLM_PROVIDER` / `LLM_MODEL` | – / `openai` / – (Provider-Default) | – | `API/app/views/external/base.py` (+ Instanz-Config) | KI-Provider (`openai`, `anthropic`, `gemini`) |
| `DISABLE_WORKSPACE_CREATION` | `0` | – | `API/app/views/workspace/base.py` (+ Instanz-Config) | Workspace-Erstellung sperren |
| `ENABLE_SIGNUP` | `1` (`API/authentication/adapter/base.py`), `0` (`API/license/api/views/instance.py`) | – | dto. (+ Instanz-Config) | Selbstregistrierung (siehe Edge-Case E-12) |
| `ENABLE_EMAIL_PASSWORD` | `1` (instance view), ohne Default (`API/authentication/provider/credentials/email.py`) | – | dto. | E-Mail/Passwort-Login |
| `ENABLE_MAGIC_LINK_LOGIN` | `1` (`check.py` app/space, `magic_code.py`, instance view) | – | dto. | Magic-Code-Login |
| `EMAIL_HOST` | `""`/None | Test-Compose: `test-smtp.invalid` | `magic_code.py`, `check.py`, `password_management.py`, `instance_value.py`, instance view | SMTP-Host; leer = SMTP nicht konfiguriert |
| `EMAIL_HOST_USER` / `EMAIL_HOST_PASSWORD` | None | – | `instance_value.py`, `views/space/password_management.py` | SMTP-Login |
| `EMAIL_PORT` | `587` | – | `instance_value.py` | SMTP-Port |
| `EMAIL_USE_TLS` / `EMAIL_USE_SSL` | `1` / `0` | – | dto. | TLS/SSL |
| `EMAIL_FROM` | `Team Plane <team@mailer.plane.so>` (`get_email_configuration`), `""` (`core.py`) | – | dto. | Absender |
| `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET` | – | – | `API/authentication/provider/oauth/google.py` | OAuth Google |
| `GITHUB_CLIENT_ID` / `GITHUB_CLIENT_SECRET` / `GITHUB_ORGANIZATION_ID` | – | – | `…/oauth/github.py` | OAuth GitHub (+ Org-Einschränkung) |
| `GITLAB_CLIENT_ID` / `GITLAB_CLIENT_SECRET` / `GITLAB_HOST` | – / – / `https://gitlab.com` | – | `…/oauth/gitlab.py` | OAuth GitLab |
| `GITEA_CLIENT_ID` / `GITEA_CLIENT_SECRET` / `GITEA_HOST` | – | – | `…/oauth/gitea.py` | OAuth Gitea |
| `IS_GOOGLE_ENABLED` / `IS_GITHUB_ENABLED` / `IS_GITLAB_ENABLED` / `IS_GITEA_ENABLED` | `0` | – | nur `API/license/api/views/instance.py` (→ `is_*_enabled` im Instanz-Config-Response; Frontends blenden danach Login-Buttons ein) | Provider aktivieren |
| `ENABLE_GOOGLE_SYNC` / `ENABLE_GITHUB_SYNC` / `ENABLE_GITLAB_SYNC` / `ENABLE_GITEA_SYNC` | `0` | – | `API/authentication/adapter/base.py` (`check_sync_enabled`, Default `os.environ.get(config_key, "0")`) | Profil-Sync (`sync_user_data`: Vor-/Nachname, Display-Name, Avatar) vom OAuth-Provider bei jedem Login außer Signup |
| `GITHUB_APP_NAME` | `""` | – | instance view | Name der GitHub-App (Integration) |
| `SLACK_CLIENT_ID` | None | – | instance view | Slack-Integration (Client-ID an Frontend) |

#### 2.11.2 Instanz-Konfiguration (Tabelle `InstanceConfiguration`, initial aus ENV)

`configure_instance` legt beim API-Start jeden Schlüssel **nur an, wenn er noch nicht existiert** (`get_or_create`); vorhandene Werte werden **nie** aus ENV aktualisiert (`API/license/management/commands/configure_instance.py`). Verschlüsselte Werte: Fernet mit Schlüssel `urlsafe_b64encode(pbkdf2_hmac("sha256", SECRET_KEY, b"salt", 100000))` (`API/license/utils/encryption.py`). `extended_config_variables = []` (`API/utils/instance_config_variables/extended.py`).

| Key | Kategorie | ENV-Initialwert (Default) | verschlüsselt | Quelle |
|---|---|---|---|---|
| `ENABLE_SIGNUP` | AUTHENTICATION | `1` | nein | `API/utils/instance_config_variables/core.py` |
| `ENABLE_EMAIL_PASSWORD` | AUTHENTICATION | `1` | nein | dto. |
| `ENABLE_MAGIC_LINK_LOGIN` | AUTHENTICATION | `0` | nein | dto. |
| `DISABLE_WORKSPACE_CREATION` | WORKSPACE_MANAGEMENT | `0` | nein | dto. |
| `IS_GOOGLE_ENABLED` | GOOGLE | `0` | nein | dto. |
| `GOOGLE_CLIENT_ID` | GOOGLE | None | nein | dto. |
| `GOOGLE_CLIENT_SECRET` | GOOGLE | None | **ja** | dto. |
| `ENABLE_GOOGLE_SYNC` | GOOGLE | `0` | nein | dto. |
| `IS_GITHUB_ENABLED` | GITHUB | `0` | nein | dto. |
| `GITHUB_CLIENT_ID` | GITHUB | None | nein | dto. |
| `GITHUB_CLIENT_SECRET` | GITHUB | None | **ja** | dto. |
| `GITHUB_ORGANIZATION_ID` | GITHUB | None | nein | dto. |
| `ENABLE_GITHUB_SYNC` | GITHUB | `0` | nein | dto. |
| `IS_GITLAB_ENABLED` | GITLAB | `0` | nein | dto. |
| `GITLAB_HOST` | GITLAB | None | nein | dto. |
| `GITLAB_CLIENT_ID` | GITLAB | None | nein | dto. |
| `GITLAB_CLIENT_SECRET` | GITLAB | None | **ja** | dto. |
| `ENABLE_GITLAB_SYNC` | GITLAB | `0` | nein | dto. |
| `IS_GITEA_ENABLED` | GITEA | `0` | nein | dto. |
| `GITEA_HOST` | GITEA | None | nein | dto. |
| `GITEA_CLIENT_ID` | GITEA | None | nein | dto. |
| `GITEA_CLIENT_SECRET` | GITEA | None | **ja** | dto. |
| `ENABLE_GITEA_SYNC` | GITEA | `0` | nein | dto. |
| `ENABLE_SMTP` | SMTP | `0` | nein | dto. |
| `EMAIL_HOST` | SMTP | `""` | nein | dto. |
| `EMAIL_HOST_USER` | SMTP | `""` | nein | dto. |
| `EMAIL_HOST_PASSWORD` | SMTP | `""` | **ja** | dto. |
| `EMAIL_PORT` | SMTP | `587` | nein | dto. |
| `EMAIL_FROM` | SMTP | `""` | nein | dto. |
| `EMAIL_USE_TLS` | SMTP | `1` | nein | dto. |
| `EMAIL_USE_SSL` | SMTP | `0` | nein | dto. |
| `LLM_API_KEY` | AI | None | **ja** | dto. |
| `LLM_PROVIDER` | AI | `openai` | nein | dto. |
| `LLM_MODEL` | AI | `gpt-4o-mini` | nein | dto. |
| `GPT_ENGINE` | AI | `gpt-3.5-turbo` (deprecated, „use LLM_MODEL“) | nein | dto. |
| `UNSPLASH_ACCESS_KEY` | UNSPLASH | `""` | **ja** | dto. |

Öffentlich über `GET /api/instances/` ausgegebene Konfiguration (`API/license/api/views/instance.py`, Cache 2 h serverseitig + `Cache-Control: private, max-age=12`): `enable_signup`, `is_workspace_creation_disabled`, `is_google_enabled`, `is_github_enabled`, `is_gitlab_enabled`, `is_gitea_enabled`, `is_magic_login_enabled`, `is_email_password_enabled`, `github_app_name`, `slack_client_id`, `has_unsplash_configured`, `has_llm_configured`, `file_size_limit` (float aus ENV `FILE_SIZE_LIMIT`), `is_smtp_configured`, `admin_base_url`, `space_base_url`, `app_base_url`, `instance_changelog_url`, `is_self_managed` (`IS_SELF_MANAGED = True`) sowie `instance` (Serializer + `workspaces_exist`). Ohne Instanz: `{"is_activated": false, "is_setup_done": false}`. Details siehe God-Mode-/Instanz-Analyse.

#### 2.11.3 Live-Server (`LIVE/env.ts`, zod-validiert; bei Fehler `process.exit(1)`)

| Variable | Default | Template (`apps/live/.env.example` / CLI) | Bedeutung |
|---|---|---|---|
| `APP_VERSION` | `1.0.0` | – | Version im Health-Check |
| `HOSTNAME` | – (optional) | AIO: `0.0.0.0` | Hocuspocus-Servername; sonst `uuidv4()` (`LIVE/hocuspocus.ts`) |
| `PORT` | `3000` | `3100`; AIO: `3005` | HTTP-Port |
| `API_BASE_URL` | **Pflicht** (`z.string().url()`) | `http://localhost:8000`; CLI: `http://api:8000`; AIO: `http://localhost:3004` | Basis aller API-Aufrufe (`LIVE/services/api.service.ts`, Timeout 20 000 ms, `withCredentials: true`) |
| `CORS_ALLOWED_ORIGINS` | `""` | – | Komma-getrennt; CORS mit `credentials: true`, Methoden `GET, POST, PUT, DELETE, OPTIONS`, Header `Content-Type, Authorization, x-api-key` |
| `LIVE_BASE_PATH` | `/live` | `/live` | Express-Router-Mount |
| `COMPRESSION_LEVEL` | `6` | – | `compression`-Level |
| `COMPRESSION_THRESHOLD` | `5000` | – | Bytes |
| `LIVE_SERVER_SECRET_KEY` | **Pflicht** | `secret-key`; CLI: `change-this-key-on-deployment` | Header-Prüfung `live-server-secret-key` in `requireSecretKey` (`LIVE/lib/auth-middleware.ts`) – in CE an keinem Controller angewandt |
| `REDIS_HOST` | – | `localhost` | Fallback-URL `redis://{host}:{port}` |
| `REDIS_PORT` | `6379` | `6379` | dto. |
| `REDIS_URL` | – | `redis://localhost:6379/` | Vorrang; ohne URL/Host: Redis deaktiviert (Warnung), Hocuspocus-Redis-Extension wirft dann beim Init `Redis client not initialized` |
| `LOG_LEVEL` | `info` | – | winston (`packages/logger/src/config.ts`) |
| `WEB_BASE_URL`, `LIVE_BASE_URL` | – | in `.env.example` vorhanden | **nicht** im Schema, ungenutzt |

#### 2.11.4 Frontends (Build-Zeit, `process.env.VITE_*` → `packages/constants/src/endpoints.ts`)

| Variable | Code-Default | Template (`apps/{web,admin,space}/.env.example`) | Dockerfile-Default (web / admin / space) | Verwendung |
|---|---|---|---|---|
| `VITE_API_BASE_URL` | `""` (→ relative URLs) | `http://localhost:8000` | `""` / `""` / `""` | `API_BASE_URL`; Basis aller Service-Aufrufe; SSR-Fetch in `apps/space/app/issues/[anchor]/layout.tsx` (`/api/public/anchor/{anchor}/meta/`); GitHub-Integration (`apps/web/components/integration/github/select-repository.tsx`) |
| `VITE_API_BASE_PATH` | `""` | – | – / `/api` / `/api` | `API_BASE_PATH`/`API_URL` – **nirgends verwendet** (Services hängen `/api/…` selbst an) |
| `VITE_ADMIN_BASE_URL` | `""` | `http://localhost:3001` | `""` | `GOD_MODE_URL` (4 Verwendungen) |
| `VITE_ADMIN_BASE_PATH` | `""` | `/god-mode` | `/god-mode` | `GOD_MODE_URL`; admin: Vite-`base` + Router-`basename` (`joinUrlPath(…, "/")`, `packages/utils/src/string.ts`) |
| `VITE_SPACE_BASE_URL` | `""` | `http://localhost:3002` | `""` | `SPACE_BASE_URL` (6 Verwendungen) |
| `VITE_SPACE_BASE_PATH` | `""` | `/spaces` | `/spaces` | space: Vite-`base` + `basename`; Links (8 Verwendungen) |
| `VITE_LIVE_BASE_URL` | `""` (→ `window.location.origin`) | `http://localhost:3100` | `""` | WebSocket-URL (`apps/web/components/pages/editor/editor-body.tsx`) |
| `VITE_LIVE_BASE_PATH` | `""` | `/live` | `/live` | WS-Pfad `{LIVE_BASE_PATH}/collaboration` |
| `VITE_WEB_BASE_URL` | `""` | `http://localhost:3000` | `""` | `WEB_BASE_URL` (7 Verwendungen, Links aus admin/space zur web-App) |
| `VITE_WEB_BASE_PATH` | `""` | – | – / `""` / `""` | ungenutzt |
| `VITE_WEBSITE_URL` | `https://plane.so` | – | – / `https://plane.so` / `https://plane.so` | Marketing-Links (3 Verwendungen) |
| `VITE_SUPPORT_EMAIL` | `support@plane.so` | – | – / `support@plane.so` / `support@plane.so` | Support-Links (6 Verwendungen) |
| `NODE_ENV` | – | – | admin/space-Installer: `production` | `packages/i18n/src/hooks/use-translation.ts` (Warnungen außerhalb production) |
| `LOG_LEVEL` | `info` | – | – | `packages/logger` (nur live) |
| `NEXT_TELEMETRY_DISABLED`, `TURBO_TELEMETRY_DISABLED`, `CI` | – | – | `1` | Build-Telemetrie aus |

Konstanten ohne ENV in `endpoints.ts`: `MARKETING_PRICING_PAGE_LINK = https://plane.so/pricing`, `MARKETING_CONTACT_US_PAGE_LINK = https://plane.so/contact`, `MARKETING_PLANE_ONE_PAGE_LINK = https://plane.so/one` (Upsell, ADR-001: entfällt).

#### 2.11.5 Proxy (Caddy)

| Variable | Default | Bedeutung | Quelle |
|---|---|---|---|
| `SITE_ADDRESS` | Template `:80` | Caddy-Site-Adresse (Domain → automatisches HTTPS) | `apps/proxy/Caddyfile.ce` |
| `FILE_SIZE_LIMIT` | Compose `5242880` | `request_body max_size` | dto. |
| `BUCKET_NAME` | Compose `${AWS_S3_BUCKET_NAME:-uploads}` | Pfad-Präfix zum Objektspeicher | dto. |
| `CERT_EMAIL` | leer | ACME-E-Mail (als komplette Direktive `email …`) | dto. |
| `CERT_ACME_CA` | `https://acme-v02.api.letsencrypt.org/directory` | ACME-Server | dto. |
| `CERT_ACME_DNS` | leer | DNS-Challenge-Direktive (Module Cloudflare, DigitalOcean) | dto. |
| `TRUSTED_PROXIES` | `0.0.0.0/0` | vertrauenswürdige Proxies (`private_ranges` empfohlen, `DEP/cli/community/README.md`) | dto. |
| `LISTEN_HTTP_PORT` / `LISTEN_HTTPS_PORT` | `80` / `443` | Host-Port-Mapping (Compose) | `docker-compose.yml` |
| `APP_DOMAIN` | `localhost` | nur zur Komposition von `WEB_URL`/`CORS_ALLOWED_ORIGINS` in `variables.env`; im Caddyfile ungenutzt | `DEP/cli/community/variables.env` |

#### 2.11.6 Infrastruktur-Container

| Variable | Default (Template) | Container | Quelle |
|---|---|---|---|
| `POSTGRES_USER` / `POSTGRES_PASSWORD` / `POSTGRES_DB` | `plane` / `plane` / `plane` | plane-db | `.env.example`, `docker-compose.yml` |
| `PGDATA` | `/var/lib/postgresql/data` | plane-db | dto. |
| `PGHOST` / `PGDATABASE` | `plane-db` / `plane` | (CLI `db-env`, an API/Worker übergeben) | `DEP/cli/community/docker-compose.yml` |
| `RABBITMQ_DEFAULT_USER` / `_PASS` / `_VHOST` | aus `RABBITMQ_USER`/`RABBITMQ_PASSWORD`/`RABBITMQ_VHOST` (`plane`) | plane-mq | dto. |
| `MINIO_ROOT_USER` / `MINIO_ROOT_PASSWORD` | aus `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` | plane-minio | dto. |

#### 2.11.7 Deployment-Skripte (CLI, Swarm, AIO)

| Variable | Default | Verwendung | Quelle |
|---|---|---|---|
| `APP_RELEASE` | `stable` (Install löst auf neueste GitHub-Release-Tag auf) | Image-Tag | `DEP/cli/community/install.sh`, `variables.env` |
| `WEB_REPLICAS`, `SPACE_REPLICAS`, `ADMIN_REPLICAS`, `API_REPLICAS`, `WORKER_REPLICAS`, `BEAT_WORKER_REPLICAS`, `LIVE_REPLICAS` | `1` | `deploy.replicas` | `variables.env` |
| `DOCKERHUB_USER` | `makeplane` (Custom-Build: `myplane`) | Image-Owner | `install.sh` |
| `PULL_POLICY` | `if_not_present` (Custom-Build: `never`) | Pull-Verhalten | dto. |
| `CUSTOM_BUILD` | `false` | lokaler Build aktiv | dto. |
| `DOCKER_PLATFORM` | auskommentiert (`linux/amd64`) | ARM64-Fallback | `variables.env` |
| `BRANCH` | `master` | Fallback-Download-Branch | `install.sh`, `swarm.sh` |
| `GH_REPO`, `RELEASE_DOWNLOAD_URL`, `FALLBACK_DOWNLOAD_URL` | `makeplane/plane`, `https://github.com/$GH_REPO/releases/download`, `https://raw.githubusercontent.com/$GH_REPO/$BRANCH/deployments/cli/community` | Download der Compose-/Env-Dateien | dto. |
| `DOMAIN_NAME` | **Pflicht** (FQDN oder IPv4) | AIO: `WEB_URL`, `APP_DOMAIN`, `CORS_ALLOWED_ORIGINS=http://$DOMAIN_NAME,https://$DOMAIN_NAME` | `DEP/aio/community/start.sh` |
| `APP_PROTOCOL` | `http` | AIO: Schema von `WEB_URL` | dto. |
| AIO-Pflicht | `DATABASE_URL`, `REDIS_URL`, `AMQP_URL`, `AWS_REGION`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_S3_BUCKET_NAME`; `SECRET_KEY` und `LIVE_SERVER_SECRET_KEY` nicht leer und nicht `60gp0byfz2dvffa45cxl20p1scy9xbpf6d8c5y0geejgkyp1b5`, `htbqvBJAgpm9bzvf3r4urJer0ENReatceh`, `change-this-key-on-deployment` | Start-Abbruch sonst | dto. |
| `APP_RELEASE_VERSION` | Build-Argument `--release` | AIO-`plane.env` (`APP_RELEASE_VERSION`, `APP_RELEASE`, `APP_VERSION`, `API_BASE_URL=http://localhost:3004`, `SITE_ADDRESS=:80`) | `DEP/aio/community/build.sh` |
| `IMAGE_NAME`, `DIST_DIR` | `makeplane/plane-aio-community`, `./dist` | AIO-Build | dto. |

#### 2.11.8 Veraltete / ungenutzte Variablen in Templates

| Variable | Template | Status |
|---|---|---|
| `OPENAI_API_BASE`, `OPENAI_API_KEY` | Root `.env.example` (Kommentar „deprecated“) | Im Code nicht gelesen |
| `GPT_ENGINE` | Root `.env.example` | nur als Initialwert der Instanz-Config (deprecated) |
| `DOCKERIZED` | Root + API `.env.example` („deprecated“) | Im Code nicht gelesen |
| `REDIS_HOST`, `REDIS_PORT` | Root + API | Vom API-Code nicht gelesen (nur Live) |
| `LIVE_SERVER_SECRET_KEY` | API `.env.example` | Vom API-Code nicht gelesen |
| `APP_BASE_PATH` | API | gelesen, aber ungenutzt |
| `WEB_BASE_URL`, `LIVE_BASE_URL` | Live `.env.example` | nicht im Live-Schema |
| `VITE_API_BASE_PATH`, `VITE_WEB_BASE_PATH` | Dockerfiles | Konstanten ungenutzt |
| alle `SENTRY_*`, `VITE_SENTRY_*`, `VITE_APP_VERSION`, `DEV`, `PROD` | `turbo.json` `globalEnv` | im Code nicht gelesen |

### 2.12 Django-Settings ohne ENV-Bezug (Konstanten, `API/settings/common.py`)

| Setting | Wert |
|---|---|
| `IS_SELF_MANAGED` | `True` |
| `INSTALLED_APPS` | `django.contrib.auth`, `django.contrib.contenttypes`, `django.contrib.sessions`, `django.contrib.staticfiles`, `plane.analytics`, `plane.app`, `plane.space`, `plane.bgtasks`, `plane.db`, `plane.utils`, `plane.web`, `plane.middleware`, `plane.license`, `plane.api`, `plane.authentication`, `rest_framework`, `corsheaders`, `django_celery_beat`; + `drf_spectacular` (bei `ENABLE_DRF_SPECTACULAR`); + `scout_apm.django` (`production.py`); + `debug_toolbar` (`local.py` bei DEBUG); + `plane.tests` (`test.py`) |
| `REST_FRAMEWORK` | `DEFAULT_AUTHENTICATION_CLASSES = (rest_framework.authentication.SessionAuthentication,)`; `DEFAULT_THROTTLE_CLASSES = (rest_framework.throttling.AnonRateThrottle,)`; `DEFAULT_THROTTLE_RATES = {"anon": "30/minute", "asset_id": "5/minute"}`; `DEFAULT_PERMISSION_CLASSES = (IsAuthenticated,)`; `DEFAULT_RENDERER_CLASSES = (JSONRenderer,)` (kein Browsable API); `DEFAULT_FILTER_BACKENDS = (DjangoFilterBackend,)`; `EXCEPTION_HANDLER = plane.authentication.adapter.exception.auth_exception_handler` (NotAuthenticated → 401; Throttled → 429 mit `{"error_code": 5900, "error_message": "RATE_LIMIT_EXCEEDED"}`, `API/authentication/adapter/error.py`); `SCHEMA_COERCE_PATH_PK = False`; optional `NUM_PROXIES`; optional `DEFAULT_SCHEMA_CLASS = drf_spectacular.openapi.AutoSchema` |
| `AUTHENTICATION_BACKENDS` | `django.contrib.auth.backends.ModelBackend` |
| `ROOT_URLCONF` | `plane.urls`; `handler404 = plane.app.views.error_404.custom_404_view` → `{"error": "Page not found."}` (404) |
| `TEMPLATES` | DjangoTemplates, `DIRS = ["templates"]`, `APP_DIRS = True`, Context-Prozessoren `debug`, `request`, `auth`, `messages` |
| `CORS_ALLOW_CREDENTIALS` | `True` |
| `CORS_ALLOW_HEADERS` | `corsheaders.defaults.default_headers` + `X-API-Key` |
| `WSGI_APPLICATION` / `ASGI_APPLICATION` | `plane.wsgi.application` / `plane.asgi.application` (`ProtocolTypeRouter({"http": get_asgi_application()})`, kein WebSocket) |
| `SITE_ID` | `1` |
| `AUTH_USER_MODEL` | `db.User` |
| `CACHES.default` | `django_redis.cache.RedisCache`, `LOCATION = REDIS_URL`, `CLIENT_CLASS = django_redis.client.DefaultClient`; bei `rediss` zusätzlich `CONNECTION_POOL_KWARGS = REDIS_SSL_KWARGS` (in `local.py` ohne SSL-Kwargs überschrieben) |
| `AUTH_PASSWORD_VALIDATORS` | `UserAttributeSimilarityValidator`, `MinimumLengthValidator`, `CommonPasswordValidator`, `NumericPasswordValidator` |
| `PASSWORD_RESET_TIMEOUT` | `3600` |
| `STATIC_URL` / `STATIC_ROOT` / `STATICFILES_DIRS` | `/static/` / `plane/static-assets/collected-static` / `plane/static` (enthält `css/style.css`, `js/script.js`, `humans.txt`, `logos/{Logo.png, github_32px.png, linkedin_32px.png, twitter_32px.png, website_32px.png}`) |
| `MEDIA_ROOT` / `MEDIA_URL` | `mediafiles` / `/media/` (local: `plane/uploads`, `/uploads/`) |
| `LANGUAGE_CODE` / `USE_I18N` / `USE_TZ` / `TIME_ZONE` | `en-us` / `True` / `True` / `UTC` |
| `DEFAULT_AUTO_FIELD` | `django.db.models.BigAutoField` |
| `EMAIL_BACKEND` | `django.core.mail.backends.smtp.EmailBackend` |
| `STORAGES` | `staticfiles`: `whitenoise.storage.CompressedManifestStaticFilesStorage`; `default`: `plane.settings.storage.S3Storage` |
| `AWS_DEFAULT_ACL` / `AWS_QUERYSTRING_AUTH` / `AWS_S3_FILE_OVERWRITE` | `public-read` / `False` / `False` |
| `AWS_S3_CUSTOM_DOMAIN` / `AWS_S3_URL_PROTOCOL` | nur bei Endpoint + `USE_MINIO`: `{WEB_URL.netloc}/{bucket}` / `{WEB_URL.scheme}:` |
| `CELERY_BROKER_URL` | `AMQP_URL` oder `amqp://{RABBITMQ_USER}:{RABBITMQ_PASSWORD}@{RABBITMQ_HOST}:{RABBITMQ_PORT}/{RABBITMQ_VHOST}` |
| `CELERY_TIMEZONE` / `CELERY_TASK_SERIALIZER` / `CELERY_RESULT_SERIALIZER` / `CELERY_ACCEPT_CONTENT` | `UTC` / `json` / `json` / `["application/json"]` |
| `CELERY_IMPORTS` | `plane.bgtasks.issue_automation_task`, `plane.bgtasks.exporter_expired_task`, `plane.bgtasks.file_asset_task`, `plane.bgtasks.email_notification_task`, `plane.bgtasks.cleanup_task`, `plane.license.bgtasks.telemetry_metrics`, `plane.bgtasks.dummy_data_task`, `plane.bgtasks.issue_version_sync`, `plane.bgtasks.issue_description_version_sync` |
| `SESSION_COOKIE_HTTPONLY` / `SESSION_ENGINE` | `True` / `plane.db.models.session` |
| `ADMIN_SESSION_COOKIE_NAME` | `admin-session-id` |
| `CSRF_COOKIE_SECURE` / `CSRF_COOKIE_HTTPONLY` / `CSRF_TRUSTED_ORIGINS` / `CSRF_FAILURE_VIEW` | = `SESSION_COOKIE_SECURE` / `True` / = CORS-Origins / `plane.authentication.views.common.csrf_failure` (rendert `templates/csrf_failure.html` mit `reason`, `root_url`) |
| `SEED_DIR` | `plane/seeds` |
| `ATTACHMENT_MIME_TYPES` | `image/jpeg`, `image/png`, `image/gif`, `image/svg+xml`, `image/webp`, `image/tiff`, `image/bmp`, `application/pdf`, `application/msword`, `application/vnd.openxmlformats-officedocument.wordprocessingml.document`, `application/vnd.ms-excel`, `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`, `application/vnd.ms-powerpoint`, `application/vnd.openxmlformats-officedocument.presentationml.presentation`, `text/plain`, `text/markdown`, `application/rtf`, `application/vnd.oasis.opendocument.spreadsheet`, `application/vnd.oasis.opendocument.text`, `application/vnd.oasis.opendocument.presentation`, `application/vnd.oasis.opendocument.graphics`, `application/vnd.visio`, `image/x-portable-graymap`, `image/x-portable-bitmap`, `image/x-portable-pixmap`, `application/vnd.oasis.opendocument.database`, `audio/mpeg`, `audio/wav`, `audio/ogg`, `audio/midi`, `audio/x-midi`, `audio/aac`, `audio/flac`, `audio/x-m4a`, `video/mp4`, `video/mpeg`, `video/ogg`, `video/webm`, `video/quicktime`, `video/x-msvideo`, `video/x-ms-wmv`, `application/zip`, `application/x-rar`, `application/x-rar-compressed`, `application/x-tar`, `application/gzip`, `application/x-zip`, `application/x-zip-compressed`, `application/x-7z-compressed`, `application/x-compressed`, `application/x-compressed-tar`, `application/x-compressed-tar-gz`, `application/x-compressed-tar-bz2`, `application/x-compressed-tar-zip`, `application/x-compressed-tar-7z`, `application/x-compressed-tar-rar`, `application/x-compressed-tar-zip` (doppelt), `model/gltf-binary`, `model/gltf+json`, `application/octet-stream`, `font/ttf`, `font/otf`, `font/woff`, `font/woff2`, `text/css`, `text/javascript`, `application/json`, `text/xml`, `text/csv`, `application/xml`, `application/x-sql`, `application/x-gzip`, `text/markdown` (doppelt) |
| `INLINE_SAFE_MIME_TYPES` | `image/jpeg`, `image/jpg`, `image/png`, `image/gif`, `image/webp` (nur diese werden inline ausgeliefert; alles andere inkl. SVG/HTML als `attachment`) |
| `SECURE_PROXY_SSL_HEADER` (`production.py`) | `("HTTP_X_FORWARDED_PROTO", "https")` |
| `INTERNAL_IPS` (`local.py`) | `("127.0.0.1",)`; `DEBUG_TOOLBAR_PATCH_SETTINGS = False` |

`LOGGING` siehe 2.23.

### 2.13 Middleware-Kette (API, `MIDDLEWARE` in `API/settings/common.py`, Reihenfolge = Ausführungsreihenfolge)

| # | Middleware | Verhalten | Quelle |
|---|---|---|---|
| 1 | `corsheaders.middleware.CorsMiddleware` | CORS gemäß 2.11.1 | Bibliothek |
| 2 | `django.middleware.security.SecurityMiddleware` | Standard (keine `SECURE_*`-Settings außer Proxy-Header in production) | Django |
| 3 | `whitenoise.middleware.WhiteNoiseMiddleware` | Ausliefern von `/static/` | Bibliothek |
| 4 | `plane.authentication.middleware.session.SessionMiddleware` | Eigene Session-Middleware: Cookie-Name `admin-session-id`, wenn `"instances"` im Pfad vorkommt, sonst `session-id`; Max-Age Admin = `ADMIN_SESSION_COOKIE_AGE`, sonst `get_expiry_age()`; speichert nur bei Status < 500; löscht Cookie bei leerer Session; `Vary: Cookie` | `API/authentication/middleware/session.py` |
| 5 | `django.middleware.common.CommonMiddleware` | `APPEND_SLASH` (Default True) → Frontends erzwingen Trailing Slash (`packages/services/src/helpers/url.ts`) | Django |
| 6 | `django.middleware.csrf.CsrfViewMiddleware` | Für Nicht-DRF-Views (Formular-POST-Auth-Flows unter `/auth/`); Token über `GET /auth/get-csrf-token/` → `{"csrf_token": …}` (`API/authentication/views/common.py`) | Django |
| 7 | `django.contrib.auth.middleware.AuthenticationMiddleware` | `request.user` | Django |
| 8 | `django.middleware.clickjacking.XFrameOptionsMiddleware` | `X-Frame-Options: DENY` (Django-Default) | Django |
| 9 | `crum.CurrentRequestUserMiddleware` | Thread-lokaler aktueller User (für `created_by`/`updated_by`) | django-crum |
| 10 | `django.middleware.gzip.GZipMiddleware` | Gzip | Django |
| 11 | `plane.middleware.request_body_size.RequestBodySizeLimitMiddleware` | Liest `request.body`; `RequestDataTooBig` → **413** `{"error": "REQUEST_BODY_TOO_LARGE", "detail": "The size of the request body exceeds the maximum allowed size."}` | `API/middleware/request_body_size.py` |
| 12 | `plane.middleware.logger.APITokenLogMiddleware` | Nur bei Header `X-Api-Key`: Celery-Task `process_logs` mit `token_identifier = HMAC-SHA256(SECRET_KEY, api_key)`, `path`, `method`, `query_params`, `headers` (`x-api-key`, `authorization`, `cookie` → `[REDACTED]`), `body`/`response_body` (Binär-Signaturen PNG/JPEG/PDF → `[Binary Content]`, nicht UTF-8 → `[Could not decode content]`), `response_code`, `ip_address`, `user_agent` → Tabelle `APIActivityLog` | `API/middleware/logger.py`, `API/bgtasks/logger_task.py` |
| 13 | `plane.middleware.logger.RequestLoggerMiddleware` | Logger `plane.api.request`: `"{METHOD} {full_path} {status}"` mit `extra` `path, method, status_code, duration_ms, remote_addr, user_agent, user_id`; **nicht** für `GET /` (Health-Check) | `API/middleware/logger.py` |
| 14 (optional) | `plane.middleware.db_routing.ReadReplicaRoutingMiddleware` | Nur bei `ENABLE_READ_REPLICA=1`: Nicht-GET/HEAD/OPTIONS → Primary; GET/HEAD/OPTIONS → Replica nur wenn View `use_read_replica = True` (Funktions-View, `view_class` oder DRF `cls`); Kontext (`asgiref.local.Local`) wird in `finally` und `process_exception` gelöscht | `API/middleware/db_routing.py`, `API/utils/core/request_scope.py` |
| 15 (optional) | `debug_toolbar.middleware.DebugToolbarMiddleware` | `local.py` + DEBUG | `API/settings/local.py` |

Client-IP-Ermittlung für Logs: erstes Element von `X-Forwarded-For`, sonst `REMOTE_ADDR` (`API/utils/ip_address.py` `get_client_ip`).

### 2.14 Authentifizierungsklassen je URL-Bereich

| URL-Präfix | Django-App / URL-Modul | Auth-Klasse | Cookie | Throttle | Quelle |
|---|---|---|---|---|---|
| `/api/` | `plane.app` (`API/app/urls/*.py`, 233 `path()`-Einträge in 20 Modulen: `analytic`, `api`, `asset`, `cycle`, `estimate`, `exporter`, `external`, `intake`, `issue`, `module`, `notification`, `page`, `project`, `search`, `state`, `timezone`, `user`, `views`, `webhook`, `workspace`) | `BaseSessionAuthentication` (Session; CSRF ersetzt durch Origin-Check) | `session-id` | Default `AnonRateThrottle` (30/min für Anonyme), punktuell `AssetRateThrottle` | `API/app/views/base.py` |
| `/api/public/` | `plane.space` (`API/space/urls/*.py`, 25 Einträge in `asset`, `intake`, `issue`, `project`) | `BaseSessionAuthentication` | `session-id` | `AnonRateThrottle` | `API/space/views/base.py` |
| `/api/instances/` | `plane.license` (`API/license/urls.py`, 14 Einträge) | `BaseSessionAuthentication` | `admin-session-id` | `AnonRateThrottle` | `API/license/api/views/base.py` |
| `/api/v1/` | `plane.api` (`API/api/urls/*.py`, 75 Einträge in `asset`, `cycle`, `estimate`, `intake`, `invite`, `label`, `member`, `module`, `project`, `schema`, `state`, `sticky`, `user`, `work_item`) | `APIKeyAuthentication` (Header `X-Api-Key`; Token aktiv, nicht abgelaufen, User aktiv; aktualisiert `last_used`) | – | nur `ApiKeyRateThrottle` (`get_throttles` überschrieben) | `API/api/views/base.py`, `API/api/middleware/api_authentication.py` |
| `/auth/` | `plane.authentication` (`API/authentication/urls.py`, 37 Einträge) | gemischt: Django-`View` (Formular-POST + Redirect), DRF-`APIView` mit Default `SessionAuthentication` | `session-id` (Instanz-Admin-Login liegt **nicht** hier, sondern unter `/api/instances/admins/sign-in/`, `…/sign-up/`, `…/sign-out/` mit `admin-session-id`) | `AuthenticationThrottle` (bei den in 2.15 genannten Views) | `API/authentication/views/*` |
| `/` , `/robots.txt` | `plane.web` | keine | – | – | `API/web/urls.py`, `API/web/views.py` (`{"status": "OK"}`; `User-agent: *\nDisallow: /`) |
| `/api/schema/…` | drf-spectacular | – | – | – | `API/urls.py` |
| `/__debug__/` | debug_toolbar | – | – | – | `API/urls.py` |

Origin-Check (`API/authentication/session.py`, `BaseSessionAuthentication.enforce_csrf`): Für Nicht-`GET/HEAD/OPTIONS/TRACE` mit Cookie-Auth gilt: kein `Origin`-Header → erlaubt (Nicht-Browser-Clients wie der Live-Server); `Origin: null`/unparsebar → 403; gleicher `host[:port]` wie `request.get_host()` → erlaubt (Schema wird bewusst ignoriert); sonst muss Origin in `{WEB_URL, APP_BASE_URL, ADMIN_BASE_URL, SPACE_BASE_URL, LIVE_BASE_URL} ∪ CORS_ALLOWED_ORIGINS ∪ CSRF_TRUSTED_ORIGINS` (normalisiert `scheme://host[:port]`, lowercase, `lru_cache`) liegen, sonst `PermissionDenied("CSRF Failed: origin not allowed")`.

### 2.15 Rate-Limits / Throttles

| Name | Klasse | Scope / Rate | Schlüssel | Antwort bei Überschreitung | Quelle |
|---|---|---|---|---|---|
| Anonym global | `rest_framework.throttling.AnonRateThrottle` | `anon` = 30/minute | Client-IP (nur nicht authentifizierte Requests) | 429 `{"error_code": 5900, "error_message": "RATE_LIMIT_EXCEEDED"}` (Exception-Handler) | `S/common.py` |
| Asset-Abruf | `plane.throttles.asset.AssetRateThrottle` | `asset_id` = 5/minute | `throttle_asset_{asset_id}` (pro Asset, nicht pro Client) | 429 (s. o.) | `API/throttles/asset.py`, `API/app/views/asset/v2.py` Z. 849 |
| API-Key | `plane.api.rate_limit.ApiKeyRateThrottle` | `api_key` = `API_KEY_RATE_LIMIT` (60/minute) | `api_key:{X-Api-Key}`; ohne Key kein Limit | 429; bei Erfolg Header `X-RateLimit-Remaining`, `X-RateLimit-Reset` (Unix-Zeit `now + duration`) | `API/api/rate_limit.py`, `API/api/views/base.py` |
| Authentifizierung | `plane.authentication.rate_limit.AuthenticationThrottle` | `authentication` = `AUTHENTICATION_RATE_LIMIT` (10/minute) | Client-IP für alle (angemeldet oder nicht) | DRF: 429 + Fehler-Dict; Redirect-Views (`throttle_auth_redirect`): Redirect auf Auth-Fehlerseite mit `error_code`/`error_message` | `API/authentication/rate_limit.py` |
| E-Mail-Verifizierung | `EmailVerificationThrottle(UserRateThrottle)` | `email_verification` = 3/hour | User | 429 + Fehler-Dict | dto. |
| Statische Frontends | Caddy `rate_limit` | 300 Events/1 min | `{client_ip}` | 429 (Caddy) | `apps/web/caddy/Caddyfile`, `apps/admin/caddy/Caddyfile` |

Alle DRF-Throttles speichern ihre Historie im Django-Cache (Redis).

### 2.16 Cookies & Sessions

| Cookie | Name | Lebensdauer | Flags | Domain | Ermittlung `Secure` | Quelle |
|---|---|---|---|---|---|---|
| Benutzer-Session (web, space) | `session-id` (`SESSION_COOKIE_NAME`) | `SESSION_COOKIE_AGE` = 604 800 s | HttpOnly, SameSite = Django-Default (`Lax`), Path `/` | `COOKIE_DOMAIN` | `True`, wenn `WEB_URL` (Fallback `APP_BASE_URL`) mit `https://` beginnt **oder** alle CORS-Origins nicht `http:` enthalten (und mindestens einer existiert) | `S/common.py` (`_cookies_secure`) |
| Admin-Session (God-Mode) | `admin-session-id` | `ADMIN_SESSION_COOKIE_AGE` = 3 600 s | wie oben | dto. | dto. | `API/authentication/middleware/session.py` |
| CSRF | `csrftoken` (Django-Default) | Django-Default | HttpOnly, Secure wie Session | `COOKIE_DOMAIN` | dto. | `S/common.py` |

Session-Speicher: DB-Tabelle `sessions` (Model `plane.db.models.session.Session`: `session_key` CharField(128, PK), `session_data`, `expire_date`, `device_info` JSON, `user_id` CharField(50, Index)); Schlüssel = 128 Zeichen aus `[a-z0-9]`; `device_info` und `user_id` (`_auth_user_id`) werden beim Speichern übernommen (`API/db/models/session.py`). Details zum Login siehe Auth-Analyse.

### 2.17 Celery

#### 2.17.1 Konfiguration (`API/celery.py`)

- App `Celery("plane")`, `config_from_object("django.conf:settings", namespace="CELERY")`, `autodiscover_tasks()`, `beat_scheduler = "django_celery_beat.schedulers.DatabaseScheduler"`.
- Logging: Signale `after_setup_logger`/`after_setup_task_logger` hängen `StreamHandler` mit `JsonFormatter('"%(levelname)s %(asctime)s %(module)s %(name)s %(message)s')` an (führendes `"` im Formatstring ist Tippfehler im Original).
- Beim Import wird `ri = redis_instance()` erzeugt (ungenutzt).
- Kein Result-Backend, keine Queues/Routing (`task_routes` nicht gesetzt), Standard-Queue `celery`.
- Retry-Konfiguration nur bei `webhook_send_task`: `bind=True`, `autoretry_for=(requests.RequestException,)`, `retry_backoff=600`, `max_retries=5`, `retry_jitter=True` (`API/bgtasks/webhook_task.py`).

#### 2.17.2 Beat-Schedule (vollständig, UTC)

| Name | Task | Zeitplan |
|---|---|---|
| `check-every-five-minutes-to-send-email-notifications` | `plane.bgtasks.email_notification_task.stack_email_notification` | `crontab(minute="*/5")` |
| `check-every-five-minutes-to-unsnooze-intake-issues` | `plane.bgtasks.issue_automation_task.unsnooze_expired_intake_issues` | `crontab(minute="*/5")` |
| `push-instance-metrics` | `plane.license.bgtasks.telemetry_metrics.push_instance_metrics` | `schedule(run_every=timedelta(minutes=METRICS_PUSH_INTERVAL_MINUTES))` (360 min) |
| `check-every-day-to-delete-hard-delete` | `plane.bgtasks.deletion_task.hard_delete` | 00:00 |
| `check-every-day-to-archive-and-close` | `plane.bgtasks.issue_automation_task.archive_and_close_old_issues` | 01:00 |
| `check-every-day-to-delete_exporter_history` | `plane.bgtasks.exporter_expired_task.delete_old_s3_link` | 01:30 |
| `check-every-day-to-delete-file-asset` | `plane.bgtasks.file_asset_task.delete_unuploaded_file_asset` | 02:00 |
| `check-every-day-to-delete-api-logs` | `plane.bgtasks.cleanup_task.delete_api_logs` | 02:30 |
| `check-every-day-to-delete-email-notification-logs` | `plane.bgtasks.cleanup_task.delete_email_notification_logs` | 02:45 |
| `check-every-day-to-delete-page-versions` | `plane.bgtasks.cleanup_task.delete_page_versions` | 03:00 |
| `check-every-day-to-delete-issue-description-versions` | `plane.bgtasks.cleanup_task.delete_issue_description_versions` | 03:15 |
| `check-every-day-to-delete-webhook-logs` | `plane.bgtasks.cleanup_task.delete_webhook_logs` | 03:30 |
| `check-every-day-to-delete-exporter-history` | `plane.bgtasks.exporter_expired_task.delete_old_s3_link` (**zweiter** Eintrag für denselben Task) | 03:45 |

Cleanup-Semantik (`API/bgtasks/cleanup_task.py`): Batch-Größe 500, harte Löschung über `all_objects`; fehlerhafte Batches werden geloggt und übersprungen. `delete_api_logs`: `APIActivityLog.created_at <= now − API_ACTIVITY_LOG_RETENTION_DAYS`; `delete_email_notification_logs`: `EmailNotificationLog.sent_at <= now − EMAIL_LOG_RETENTION_DAYS`; `delete_page_versions`: je Seite alle `PageVersion` über die neuesten **20** hinaus; `delete_issue_description_versions`: je Issue über die neuesten **20** hinaus; `delete_webhook_logs`: `WebhookLog.created_at <= now − WEBHOOK_LOG_RETENTION_DAYS`.

#### 2.17.3 Task-Inventar (alle `@shared_task`, `API/bgtasks/*`, `API/license/bgtasks/*`)

| Modul | Task-Funktion(en) | Auslöser | Fachbereich |
|---|---|---|---|
| `analytic_plot_export.py` | `analytic_export_task(email, data, slug, user_id)`, `export_analytics_to_csv_email(data, headers, keys, email, slug)` | Analytics-Export-API | Analytics |
| `cleanup_task.py` | `delete_api_logs`, `delete_email_notification_logs`, `delete_page_versions`, `delete_issue_description_versions`, `delete_webhook_logs` | Beat | Betrieb |
| `copy_s3_object.py` | `copy_s3_objects_of_description_and_assets(entity_name, entity_identifier, project_id, slug, user_id)` | Duplizieren von Seiten/Issues | Assets/Pages |
| `deletion_task.py` | `soft_delete_related_objects(app_label, model_name, instance_pk, using=None)`, `restore_related_objects(…)`, `hard_delete()` | Soft-Delete-Mixin (`API/db/mixins.py`), Beat | Datenmodell |
| `dummy_data_task.py` | `create_dummy_data(…)` | Command `create_dummy_data` | Entwicklung |
| `email_notification_task.py` | `stack_email_notification()`, `send_email_notification(issue_id, notification_data, receiver_id, email_notification_ids)` | Beat (5 min) | Benachrichtigungen |
| `export_task.py` | `issue_export_task(…)` | Export-API | Export |
| `exporter_expired_task.py` | `delete_old_s3_link()` | Beat | Export |
| `file_asset_task.py` | `delete_unuploaded_file_asset()` | Beat | Assets |
| `forgot_password_task.py` | `forgot_password(first_name, email, uidb64, token, current_site)` | Auth | Auth/E-Mail |
| `issue_activities_task.py` | `issue_activity(…)` | Work-Item-Änderungen | Aktivitäten |
| `issue_automation_task.py` | `archive_and_close_old_issues()`, `unsnooze_expired_intake_issues()` | Beat | Automationen/Intake |
| `issue_description_version_sync.py` | `sync_issue_description_version(batch_size=5000, offset=0, countdown=300)`, `schedule_issue_description_version(batch_size=5000, countdown=300)` | Command | Versionierung |
| `issue_description_version_task.py` | `issue_description_version_task(updated_issue, issue_id, user_id, is_creating=False)` | Work-Item-Update | Versionierung |
| `issue_version_sync.py` | `issue_task(updated_issue, issue_id, user_id)`, `sync_issue_version(…)`, `schedule_issue_version(…)` | Command | Versionierung |
| `logger_task.py` | `process_logs(log_data, **_)` | `APITokenLogMiddleware` | Betrieb |
| `magic_link_code_task.py` | `magic_link(email, key, token)` | Auth | Auth/E-Mail |
| `notification_task.py` | `notifications(…)` | Aktivitäten | Benachrichtigungen |
| `page_transaction_task.py` | `page_transaction(new_description_html, old_description_html, page_id)` | Seiten-Update | Pages |
| `page_version_task.py` | `track_page_version(page_id, existing_instance, user_id)` | Seiten-Update | Pages |
| `project_add_user_email_task.py` | `project_add_user_email(current_site, project_member_id, invitor_id)` | Projektmitglied | E-Mail |
| `project_invitation_task.py` | `project_invitation(email, project_id, token, current_site, invitor)` | Einladung | E-Mail |
| `recent_visited_task.py` | `recent_visited_task(entity_name, entity_identifier, user_id, project_id, slug)` | Detail-Aufrufe | Home/Recents |
| `storage_metadata_task.py` | `get_asset_object_metadata(asset_id)` | Upload-Bestätigung | Assets |
| `user_activation_email_task.py` | `user_activation_email(current_site, user_id)` | God-Mode | E-Mail |
| `user_deactivation_email_task.py` | `user_deactivation_email(current_site, user_id)` | Konto | E-Mail |
| `user_email_update_task.py` | `send_email_update_magic_code(email, token)`, `send_email_update_confirmation(email)` | Profil | E-Mail |
| `webhook_task.py` | `send_webhook_deactivation_email(webhook_id, receiver_id, current_site, reason)`, `webhook_send_task(self, webhook_id, slug, event, event_data, action, current_site, activity)`, `webhook_activity(…)`, `model_activity(model_name, model_id, requested_data, current_instance, actor_id, slug, origin=None)` | Modelländerungen | Webhooks |
| `work_item_link_task.py` | `crawl_work_item_link_title(id, url)` | Link anlegen | Work Items |
| `workspace_invitation_task.py` | `workspace_invitation(email, workspace_id, token, current_site, inviter)` | Einladung | E-Mail |
| `workspace_seed_task.py` | `workspace_seed(workspace_id)` | Workspace-Erstellung | Onboarding |
| `license/bgtasks/telemetry_metrics.py` | `push_instance_metrics()` | Beat, `register_instance` | Telemetrie |

Registrierung: Tasks aus `CELERY_IMPORTS` werden explizit geladen; alle übrigen Task-Module (`analytic_plot_export`, `copy_s3_object`, `deletion_task`, `export_task`, `forgot_password_task`, `issue_activities_task`, `issue_description_version_task`, `logger_task`, `magic_link_code_task`, `notification_task`, `page_transaction_task`, `page_version_task`, `project_add_user_email_task`, `project_invitation_task`, `recent_visited_task`, `storage_metadata_task`, `user_activation_email_task`, `user_deactivation_email_task`, `user_email_update_task`, `webhook_task`, `work_item_link_task`, `workspace_invitation_task`, `workspace_seed_task`) werden nur indirekt importiert – `deletion_task` über `API/db/mixins.py`, der Rest über Views/Utils, die beim Worker-Start durch Celerys Django-Fixup (`run_checks()` → URL-Check lädt `ROOT_URLCONF`) importiert werden (Celery-Interna, nicht im Repo; zu verifizieren). `autodiscover_tasks()` findet keine `tasks.py`-Module.

### 2.18 Redis-/Cache-Nutzung

| Nutzung | Mechanismus | Schlüssel / Kanal | TTL | Quelle |
|---|---|---|---|---|
| Response-Cache | `@cache_response(timeout, path, user)` (nur Status 200, nicht bei DEBUG); Invalidation `@invalidate_cache` / `invalidate_cache_directly` (optional `delete_many(keys("*{key}*"))`) | `{path}` oder `{path}:{user_id}` | Default 3600 s (Instanz: 7200 s) | `API/utils/cache.py`, `API/license/api/views/instance.py` |
| DRF-Throttle-Historien | Django-Cache | `throttle_{scope}_{ident}`, `api_key:{key}`, `throttle_asset_{asset_id}` | Rate-Dauer | 2.15 |
| Magic-Code-Login | `redis_instance()` direkt | Schlüssel aus E-Mail, JSON `{current_attempt, email, token}`; Zähler `…verify_attempts…` | 600 s | `API/authentication/provider/credentials/magic_code.py` |
| E-Mail-Änderungscode | Django-Cache `add`/`incr`/`set` | Code-Key, `{key}:verify_attempts`, Issued-Counter | 600 s / Fenster | `API/app/views/user/base.py` |
| Lock für E-Mail-Benachrichtigungen | `SET lock_id true NX EX 300` | Lock-ID | 300 s | `API/bgtasks/email_notification_task.py` |
| Origin für E-Mail-Links | `SET issue_id origin EX 600` | `str(issue_id)` | 600 s | `API/bgtasks/issue_activities_task.py` Z. 1575–1577, Lesen in `email_notification_task.py` Z. 163–164 |
| Cache-Reset beim Start | `clear_cache` (gesamter Cache, `cache.clear()`) | alle | – | `API/db/management/commands/clear_cache.py` |
| Hocuspocus Multi-Instanz-Sync | `@hocuspocus/extension-redis` (Pub/Sub, `pub`/`sub`-Duplikate) | Dokument-Kanäle (Präfix der Extension), Admin-Kanal `hocuspocus:admin` | – | `LIVE/extensions/redis.ts` |
| Live-Redis-Client | ioredis (`keepAlive 30000`, `connectTimeout 10000`, `maxRetriesPerRequest 3`, `enableOfflineQueue true`, Backoff `min(times*50, 2000)` ms) | – | – | `LIVE/redis.ts` |

### 2.19 Objektspeicher (S3/MinIO) – `S3Storage` (`API/settings/storage.py`)

| Methode | Verhalten |
|---|---|
| `__init__(request=None)` | Liest `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_S3_BUCKET_NAME`, `AWS_REGION`, `AWS_S3_ENDPOINT_URL`/`MINIO_ENDPOINT_URL`, `SIGNED_URL_EXPIRATION` direkt aus ENV. `USE_MINIO == "1"`: Endpoint = `{https wenn MINIO_ENDPOINT_SSL=="1", sonst request.scheme}://{request.get_host()}` (ohne Request: `AWS_S3_ENDPOINT_URL`); sonst `AWS_S3_ENDPOINT_URL`. Signatur `s3v4`. |
| `url(name, …)` | Gibt den Key unverändert zurück (keine öffentliche URL) |
| `generate_presigned_post(object_name, file_type, file_size, expiration=None)` | Felder `Content-Type`; Bedingungen `{"bucket": …}`, `["content-length-range", 1, file_size]`, `{"Content-Type": file_type}`, Key exakt (oder `starts-with $key`, wenn `object_name` mit `${filename}` beginnt); Fehler → `None` (print) |
| `generate_presigned_url(object_name, expiration=None, http_method="GET", disposition="inline", filename=None, content_type=None)` | `inline` nur, wenn `content_type` (ohne Parameter, lowercase) ∈ `INLINE_SAFE_MIME_TYPES` → `ResponseContentType` gepinnt; sonst `attachment`; `ResponseContentDisposition = "{disposition}; filename*=UTF-8''{quote(filename)}"`, Dateiname bei fehlendem/leerem String = `uuid4().hex` |
| `get_object_metadata(object_name)` | `head_object` → `{ContentType, ContentLength, LastModified (ISO), ETag, Metadata}`; 404/NoSuchKey → `None` ohne Log |
| `copy_object(object_name, new_object_name)` | Kopie im selben Bucket |
| `upload_file(file_obj, object_name, content_type=None, extra_args={})` | `upload_fileobj` (mutable Default-Argument im Original) |
| `delete_files(object_names)` | `delete_objects` (Batch) |

Bucket-Anlage beim Start: `create_bucket` → `head_bucket`; 404 → `create_bucket`; 403 → Fehlermeldung; andere Fehler werden nur ausgegeben (kein Abbruch) (`API/db/management/commands/create_bucket.py`). Die CLI-README zeigt noch „Public read access policy set for bucket 'uploads'“ – im aktuellen `create_bucket` wird **keine** Policy gesetzt.

### 2.20 OpenAPI (drf-spectacular, `API/settings/openapi.py`)

Aktiv nur mit `ENABLE_DRF_SPECTACULAR=1`. `TITLE` „The Plane REST API“, `VERSION` `0.0.1`, Kontakt `support@plane.so`, Lizenz GNU AGPLv3, `SERVE_INCLUDE_SCHEMA False`, `SCHEMA_PATH_PREFIX "/api/v1/"`, `SCHEMA_CACHE_TIMEOUT 0`, `PREPROCESSING_HOOKS ["plane.utils.openapi.hooks.preprocess_filter_api_v1_paths"]` (nur `/api/v1/`), `SERVERS` `http://localhost:8000` (Local), `https://api.plane.so` (Production), `AUTHENTICATION_WHITELIST ["plane.api.middleware.api_authentication.APIKeyAuthentication"]`, `COMPONENT_NO_READ_ONLY_REQUIRED True`, `COMPONENT_SPLIT_REQUEST True`, `ENUM_NAME_OVERRIDES {"ModuleStatusEnum": "plane.db.models.module.ModuleStatus", "IntakeWorkItemStatusEnum": "plane.db.models.intake.IntakeIssueStatus"}`. Tags (14): Assets, Cycles, Intake, Labels, Members, Modules, Projects, States, Users, Work Item Activity, Work Item Attachments, Work Item Comments, Work Item Links, Work Items. Auth-Erweiterung für Spectacular wird in `API/api/apps.py` (`ready()` importiert `plane.utils.openapi.auth`) registriert. Routen: `/api/schema/` (Schema), `/api/schema/swagger-ui/`, `/api/schema/redoc/` (`API/urls.py`).

### 2.21 Top-Level-URL-Routing des API-Servers (`API/urls.py`)

| Präfix | include | Anzahl `path()` (gezählt) |
|---|---|---|
| `api/` | `plane.app.urls` | 233 |
| `api/public/` | `plane.space.urls` | 25 |
| `api/instances/` | `plane.license.urls` | 14 |
| `api/v1/` | `plane.api.urls` | 75 |
| `auth/` | `plane.authentication.urls` | 37 |
| `""` | `plane.web.urls` (`robots.txt`, `""`) | 2 |
| `api/schema/`, `api/schema/swagger-ui/`, `api/schema/redoc/` | drf-spectacular (bedingt) | 3 |
| `^__debug__/` | debug_toolbar (bedingt, `DEBUG` + App installiert) | 1 |

Hinweis: `api/` wird vor `api/public/`, `api/instances/`, `api/v1/` eingebunden; Django prüft Muster der Reihe nach, die `plane.app.urls` enthalten keine kollidierenden Präfixe (Endpunkt-Details in den Fachbereichs-Analysen).

### 2.22 Live-Server – Infrastrukturschnittstellen

| Element | Detail | Quelle |
|---|---|---|
| Express-Middleware (Reihenfolge) | `helmet()`, `compression({level, threshold})`, `loggerMiddleware` (express-winston), `express.json()`, `express.urlencoded({extended: true})`, `cors(…)`; Router unter `LIVE_BASE_PATH`; 404-Handler `{"message": "Not Found"}` | `LIVE/server.ts` |
| Controller | `GET {base}/health/` → `{status: "OK", timestamp, version: APP_VERSION}`; `WS {base}/collaboration/` → `hocuspocus.handleConnection(ws, req)` (Fehler → Close 1011); `POST {base}/convert-document/` (Body `description_html` nicht leer/HTML, `variant` `rich`\|`document`) → `{description_json, description_binary}` bzw. 400 `{message: "Validation error", context: {validationErrors}}`/500 – **ohne Authentifizierung**; `POST {base}/pdf-export/` (Cookie-Header Pflicht, Body `pageId, workspaceSlug, projectId, title, author, subject, pageSize, pageOrientation, fileName, noAssets`) → `application/pdf` (`Content-Disposition: attachment; filename="…"; filename*=UTF-8''…`); Fehler-Mapping: Validation 400, Authentication 401, ContentFetch 404 („not found“) sonst 502, Timeout 504, Generation 500, Metadata/ImageProcessing 502 | `LIVE/controllers/*.ts` |
| Hocuspocus | `name = HOSTNAME \|\| uuid`, `debounce: 10000`, `onAuthenticate`, `onStateless`, Extensions (Reihenfolge) `Logger`, `Database`, `Redis`, `TitleSyncExtension`, `ForceCloseHandler` | `LIVE/hocuspocus.ts`, `LIVE/extensions/index.ts` |
| Authentifizierung | Token = JSON `{id, cookie}`; Fallback Cookie aus Request-Headern; `GET {API_BASE_URL}/api/users/me/` mit Cookie; `user.id !== token.id` → Fehler `AUTH_USER_MISMATCH`; Kontext `cookie`, `documentType`, `projectId`, `userId`, `workspaceSlug` aus Query-Parametern | `LIVE/lib/auth.ts` |
| Dokumenttypen | nur `project_page` → `ProjectPageService` mit Basis `/api/workspaces/{slug}/projects/{projectId}`; sonst Fehler `Invalid document type` | `LIVE/services/page/handler.ts` |
| Aufgerufene API-Endpunkte | `GET …/pages/{id}/`, `GET …/pages/{id}/description/` (Binary), `PATCH …/pages/{id}/`, `PATCH …/pages/{id}/description/`, `GET …/pages/{id}/mentions/`, Asset-URL-Auflösung (`resolveImageAssetUrl`) | `LIVE/services/page/core.service.ts` |
| Graceful Shutdown | `SIGTERM`: `closeConnections()`, Redis `quit`, HTTP-Server `close` → Exit 0; `SIGINT`: dto. → Exit 1; `unhandledRejection`/`uncaughtException` nur loggen | `LIVE/start.ts`, `LIVE/server.ts` |
| Admin-Kommandos | Redis-Kanal `hocuspocus:admin`, JSON `{command, …}`; `ForceCloseReason`: `critical_error`, `memory_leak`, `document_too_large`, `admin_request`, `server_shutdown`, `security_violation`, `corruption_detected`; eigene Close-Codes `4000` FORCE_CLOSE, `4001` DOCUMENT_TOO_LARGE, weitere im Enum | `LIVE/types/admin-commands.ts`, `LIVE/extensions/redis.ts` |
| Web-Client-URL | `new URL(LIVE_BASE_URL.trim() \|\| window.location.origin)`, Protokoll `wss` wenn Seite `https:`, sonst `ws`; `pathname = {LIVE_BASE_PATH}/collaboration`; Query-Parameter aus `webhookConnectionParams` (nur nicht-null) | `apps/web/components/pages/editor/editor-body.tsx` |
| PDF in web | web erzeugt PDFs **clientseitig** (`apps/web/components/pages/modals/export-page-modal.tsx` → `@/components/editor/pdf`, `@react-pdf/renderer`); der Live-Endpunkt `pdf-export` wird vom CE-Frontend nicht aufgerufen | Suche `pdf-export` in `apps/web` |

Detailverhalten (Sync-Protokoll, Titel-Sync, Force-Close, PDF-Rendering) siehe Realtime-/Pages-Analyse.

### 2.23 Logging & Telemetrie

| Aspekt | Detail | Quelle |
|---|---|---|
| Logger-Namen (API) | `plane.api.request`, `plane.api`, `plane.worker`, `plane.exception`, `plane.external`, `plane.authentication`, `plane.migrations` (+ `plane.db`, `plane` ohne eigene Handler) | `S/local.py`, `S/production.py` |
| Formatter | `verbose` und `json` (`pythonjsonlogger.json.JsonFormatter`, `"%(levelname)s %(asctime)s %(module)s %(name)s %(message)s"`) | dto. |
| Handler production | `console` (StreamHandler, json, INFO); `file` (`plane.utils.logging.SizedTimedRotatingFileHandler`, `plane/logs/plane-debug.log` bei DEBUG sonst `plane-error.log`, `when="s"`, `interval=1`, `maxBytes=1 MiB`, `backupCount=5`, Level DEBUG bzw. ERROR) – nur `plane.exception` schreibt in `file` | `S/production.py`, `API/utils/logging.py` |
| Level production | alle `plane.*` INFO (DEBUG bei DEBUG), `plane.exception` ERROR (DEBUG bei DEBUG), `plane.external` immer INFO; `disable_existing_loggers: True` | `S/production.py` |
| Handler local | nur `console` (json, DEBUG); Level INFO, `plane.exception` ERROR | `S/local.py` |
| `log_exception(e, warning=False)` | `plane.exception` `warning` oder `exception`; bei DEBUG zusätzlich Traceback als debug | `API/utils/exception_logger.py` |
| gunicorn | `--access-logfile -` (stdout) | `apps/api/bin/docker-entrypoint-api.sh` |
| Live/Node | winston JSON auf Console, Level `LOG_LEVEL` | `packages/logger/src/*` |
| Caddy | stdout, `format console` (web/admin) | `apps/{web,admin}/caddy/Caddyfile` |
| Telemetrie (Instanz-Metriken) | Celery-Task `push_instance_metrics`: nur wenn `Instance` existiert **und** `instance.is_telemetry_enabled` (Model-Default `True`); OTel-`MeterProvider` je Lauf, `PeriodicExportingMetricReader` (`export_interval_millis=20000`), `force_flush(30000)`; Resource `service.name`, `instance_id`, `plane.instance.type="self-hosted"`; Gauges Instanz: `plane_instance_users_total` (ohne Bots), `_workspaces_total`, `_projects_total`, `_issues_total`, `_modules_total`, `_cycles_total`, `_cycle_issues_total`, `_module_issues_total`, `_pages_total` (ohne Bot-eigene private Seiten `access=1`), Attribute `instance_id, instance_name, current_version, latest_version, edition, domain (aus WEB_URL), is_verified, is_setup_done`; Gauges je Workspace (max. 1 000 nach `created_at`): `plane_workspace_projects_total`, `_issues_total`, `_modules_total`, `_cycles_total`, `_members_total`, `_pages_total` mit `workspace_id, workspace_slug, instance_id`; Ziel `OTLP_ENDPOINT` (Default `https://telemetry.plane.so`); Fehler werden geloggt, nicht erneut ausgelöst | `API/license/bgtasks/telemetry_metrics.py`, `API/utils/otlp_endpoints.py`, `API/license/models/instance.py` |
| APM | Scout APM (`scout_apm.django`, aktiv nur bei `SCOUT_MONITOR`) | `S/production.py` |
| Frontend-Telemetrie | keine (keine Sentry/PostHog-Integration im Code trotz `turbo.json`-Variablen) | Suche in `apps/*`, `packages/*/src` |

### 2.24 CI-Pipeline (GitHub Actions, `.github/workflows/`)

| Workflow | Datei | Trigger | Jobs / Schritte | Bemerkungen |
|---|---|---|---|---|
| Branch Build CE | `build-branch.yml` | `workflow_dispatch` (Inputs `build_type` Build\|Release, `releaseVersion` Default `v0.0.0`, `isPrerelease`, `arm64`, `aio_build`), `push` auf `preview`, `canary`; `concurrency` je Ref mit Abbruch | `branch_build_setup` (Matrix amd64 `ubuntu-24.04` + optional arm64 `ubuntu-24.04-arm` – arm64 bei `arm64=true` oder Release ohne Prerelease; Image-Namen `plane-frontend`, `plane-space`, `plane-admin`, `plane-live`, `plane-backend`, `plane-proxy`, `plane-aio-community`; SemVer-Prüfung `^v(\d+)\.(\d+)\.(\d+)(-[a-zA-Z0-9]+(-[a-zA-Z0-9]+)*)?$`; Release erzwingt AIO-Build); je Image `branch_build_push_<img>` (Action `makeplane/actions/build-push@v1.6.0`, `push-by-digest`, buildx `docker-container`, Cache-Suffix je Arch) + `branch_merge_<img>` (`makeplane/actions/merge-manifest@v1.6.0`); `prepare_aio_assets` (`deployments/aio/community/build.sh --release …`, Artefakt `aio-assets-dist`); `branch_build_push_aio` (nach allen Merges), `branch_merge_aio`; `upload_build_assets` (`install.sh` → `setup.sh`, `${APP_RELEASE:-stable}` → Release-Version in `docker-compose.yml`; Artefakt `community-assets`: `setup.sh`, `restore.sh`, `restore-airgapped.sh`, `docker-compose.yml`, `variables.env`, `swarm.sh`); `publish_release` (nur Release; `softprops/action-gh-release@v2.6.1`, `generate_release_notes`, gleiche sechs Dateien) | Secrets `DOCKERHUB_USERNAME`, `DOCKERHUB_TOKEN`; Release hängt nicht vom AIO-Merge ab (Kommentar) |
| Version Change Before Release | `check-version.yml` | `pull_request` → `master` | Node aus `.node-version`; `apps/api/pyproject.toml`-Version muss = `package.json`-Version sein; PR-Version muss ≠ `master`-Version sein | – |
| CodeQL | `codeql.yml` | `workflow_dispatch`, `push`/`pull_request` auf `preview`, `canary`, `master` | Matrix `python`, `javascript`: init, autobuild, analyze (`github/codeql-action@v4`) | `CODEQL_ACTION_FILE_COVERAGE_ON_PRS=false` |
| Copy Right Check | `copyright-check.yml` | `workflow_dispatch`, `pull_request` → `preview` (opened, synchronize, ready_for_review, review_requested, reopened) | Go 1.22, `go install github.com/google/addlicense@latest`; `addlicense -check -f COPYRIGHT.txt -ignore "**/migrations/**"` für alle `*.py`; für `*.ts`, `*.tsx` mit Ignore `**/*.config.ts`, `**/*.d.ts` | Header-Pflicht |
| Feature Preview | `feature-deployment.yml` | `workflow_dispatch` (Input `base_tag_name`, Default `preview`) | `branch_build_setup` (Input-Sanitizing gegen Output-Injection), `full_build_push` (`docker/build-push-action@v7.0.0`, **Datei `./aio/Dockerfile-app` existiert im Repo nicht**), `feature-deploy` (Tailscale, kubectl, Helm-Upgrade in Namespace `vars.FEATURE_PREVIEW_NAMESPACE`, Domain Default `feature.plane.tools`) | Plane-intern, für Migration irrelevant |
| i18n sync check | `i18n-sync-check.yml` | `workflow_dispatch`, `pull_request` → `preview` (Pfade `packages/i18n/**`), `push` → `preview` | Node 22.22.0, `pnpm dlx tsx packages/i18n/scripts/sync-check.ts --ci` | Locale-Konsistenz |
| Migration check | `migration-check.yml` | `workflow_dispatch`, `pull_request` → `preview`, `canary`, `master` (Pfade `apps/api/**`) | `astral-sh/setup-uv@v7` (Version aus `pyproject.toml`, Python 3.12.12); `uv sync --locked --no-default-groups --group production`; `manage.py check`; `manage.py makemigrations --check --dry-run`; Guard: Änderungen/Löschungen/Umbenennungen bestehender Migrationen (`git diff --diff-filter=MDR HEAD^1 HEAD -- 'apps/api/*/migrations/*.py'`) schlagen fehl, außer Label `migration-history-override` | ENV `DJANGO_SETTINGS_MODULE=plane.settings.production`, `SECRET_KEY=ci-migration-check`, `REDIS_URL=redis://127.0.0.1:6379/0`, `DATABASE_URL=postgresql://ci:ci@127.0.0.1:5432/ci` (keine echte DB) |
| Build and lint API | `pull-request-build-lint-api.yml` | `workflow_dispatch`, `pull_request` → `preview` (Pfade `apps/api/**`), nur nicht-Draft **mit** angefragten Reviewern | `uv sync --locked --only-group dev`; `uv run --no-sync ruff check .` | nur Lint |
| Build and lint web apps | `pull-request-build-lint-web-apps.yml` | `workflow_dispatch`, `pull_request` → `preview`; nicht-Draft mit Reviewern | `check-format` (`pnpm turbo run check:format --affected`), `build` (`pnpm turbo run build --affected`, Turbo-Cache in `actions/cache`), `check-lint` (`check:lint --affected`), `check-types` (nach `build`, `check:types --affected`); `NODE_OPTIONS=--max-old-space-size=4096`; `TURBO_SCM_BASE/HEAD` = PR-Base/Head | – |
| React Doctor | `react-doctor.yml` | `pull_request` (opened, synchronize, reopened, ready_for_review), `push` → `preview` | `actions/checkout@v5` (`fetch-depth: 0`, `persist-credentials: false`), `millionco/react-doctor@v2` | Permissions `contents: read`, `pull-requests: write`, `issues: write`, `statuses: write` |

**Wichtig:** Kein Workflow führt die pytest-Suite (`apps/api`), die Vitest-Suites (`apps/live`, `packages/blocks`, `packages/services`, `packages/codemods`) oder Docker-basierte Integrationstests aus (Suche nach `pytest`/`vitest`/`test` in `.github/workflows/`; bestätigt in `apps/api/docs/django-5.2-migration-plan.md`, Abschnitt „Current state“).

### 2.25 Test-Infrastruktur

#### 2.25.1 API (pytest)

| Aspekt | Detail | Quelle |
|---|---|---|
| Konfiguration | `DJANGO_SETTINGS_MODULE = plane.settings.test`; `python_files = test_*.py`, `python_classes = Test*`, `python_functions = test_*`; Marker `unit`, `contract`, `smoke`, `slow` (`--strict-markers`); `addopts = --strict-markers --reuse-db --nomigrations -vs` | `apps/api/pytest.ini` |
| Test-Settings | erbt `common`; `DEBUG = True`; `EMAIL_BACKEND = locmem`; `INSTALLED_APPS += plane.tests` | `API/settings/test.py` |
| Docker-Stack | `docker-compose-test.yml`: `test-db` (Postgres 15.7, tmpfs, `pg_isready`), `test-redis` (Valkey, tmpfs, `valkey-cli ping`), `test-mq` (RabbitMQ, tmpfs, `rabbitmq-diagnostics -q ping`), `test-minio` (silo + `mc mb`, tmpfs, `mc ready local`), `api-tests` (Build `Dockerfile.dev`; ENV-Overrides `DJANGO_SETTINGS_MODULE=plane.settings.test`, `POSTGRES_HOST=test-db`, `DATABASE_URL=postgresql://…@test-db:5432/…`, `REDIS_HOST=test-redis`, `REDIS_URL=redis://test-redis:6379/`, `RABBITMQ_HOST=test-mq`, `AWS_S3_ENDPOINT_URL=http://test-minio:9000`, `EMAIL_HOST=test-smtp.invalid`; Entrypoint prüft `uv`, `uv sync --locked --inexact`, `mkdir -p plane/static-assets/collected-static`, `exec "$@"`; Default-Kommando `pytest`); Netzwerk `test_env`; keine Host-Ports | `docker-compose-test.yml` |
| Kommandos | Voll: `docker compose -f docker-compose-test.yml up --build --abort-on-container-exit --exit-code-from api-tests`; Teilmenge: `… run --rm --build api-tests pytest -m unit`; Teardown `… down -v` | `AGENTS.md`, `apps/api/tests/RUNNING_TESTS.md` |
| Helfer | `apps/api/run_tests.py` (`-u/--unit`, `-c/--contract`, `-s/--smoke`, `-o/--coverage` mit `--cov=plane --cov-report=term --cov-report=html` und `coverage report --fail-under=90`, `-p/--parallel` = `-n auto`, `-v`); `apps/api/run_tests.sh` ruft `tests/run_tests.sh` auf (**Datei existiert nicht**) | `apps/api/run_tests.py`, `apps/api/run_tests.sh` |
| Fixtures (`conftest.py`) | `django_db_setup` (Session), `api_client` (DRF `APIClient`), `user_data` (`test@plane.so`/`test-password`/`Test`/`User`), `create_user`, `api_token` (Token `test-api-token-12345`), `api_key_client` (`HTTP_X_API_KEY`), `session_client` (`force_authenticate`), `create_bot_user`, `api_token_data`, `create_api_token_for_user` (`user_type=0`), `plane_server` (= `live_server`), `workspace` (Slug `test-workspace`, Owner-Mitgliedschaft Rolle 20) | `API/tests/conftest.py` |
| Fixtures extern | `mock_redis` (patcht `plane.settings.redis.redis_instance`), `mock_elasticsearch` (patcht `elasticsearch.Elasticsearch` – Elasticsearch ist keine Abhängigkeit), `mock_celery` (patcht `celery.app.task.Task.delay`) | `API/tests/conftest_external.py` |
| Factories | `UserFactory`, `WorkspaceFactory`, `WorkspaceMemberFactory`, `ProjectFactory`, `ProjectMemberFactory` (factory-boy) | `API/tests/factories.py` |
| Doku | `API/tests/README.md`, `API/tests/TESTING_GUIDE.md`, `apps/api/tests/RUNNING_TESTS.md` (AGENTS.md verweist auf `apps/api/tests/TESTING_GUIDE.md`, die Datei liegt aber unter `apps/api/plane/tests/TESTING_GUIDE.md`) | – |
| Umfang | 113 Testdateien, 771 Testfunktionen: `contract/app` 50 Dateien/381 Tests, `contract/api` 21/98, `unit/utils` 14/98, `unit/bg_tasks` 8/87, `unit/middleware` 3/31, `unit/settings` 5/29, `unit/serializers` 5/24, `unit/views` 4/12, `unit/models` 2/9, `smoke` 1/2 (gezählt per AST) | `API/tests/**` |

Vollständiges Inventar der API-Testdateien (Anzahl = `def test_*`; Beschreibung = Modul- bzw. erste Klassen-Docstring-Zeile, Originalsprache):

| Datei | Tests | Marker | Prüfgegenstand |
|---|---|---|---|
| `apps/api/plane/tests/contract/api/test_api_permission_parity.py` | 10 | contract | Contract tests: v1 cycle, label and project-member writes follow the app API's rules. |
| `apps/api/plane/tests/contract/api/test_authentication.py` | 2 | contract | Contract tests for external API key authentication. |
| `apps/api/plane/tests/contract/api/test_cycle_issue_project_scope.py` | 1 | contract | POST /api/v1/.../cycles/<cycle_id>/cycle-issues/ only moves work items of the URL project. |
| `apps/api/plane/tests/contract/api/test_cycles.py` | 14 | contract | Test Cycle List and Create API Endpoint |
| `apps/api/plane/tests/contract/api/test_cycles_lite.py` | 1 | contract | Contract tests for the cycles-lite endpoint. |
| `apps/api/plane/tests/contract/api/test_generic_asset.py` | 5 | contract | Contract tests for the public REST API ``GenericAssetEndpoint``. |
| `apps/api/plane/tests/contract/api/test_intake_issue_update.py` | 3 | contract | Contract: updating the work item behind an intake issue through the external |
| `apps/api/plane/tests/contract/api/test_issue_assignee_label_validation.py` | 5 | contract | Contract: creating/updating a work item through the external REST API |
| `apps/api/plane/tests/contract/api/test_issue_attachment_size.py` | 4 | contract | POST /api/v1/.../issues/{issue_id}/issue-attachments/ with ``size`` as a string. |
| `apps/api/plane/tests/contract/api/test_issue_notifications.py` | 3 | contract | Contract: creating and updating/assigning a work item through the external |
| `apps/api/plane/tests/contract/api/test_issue_read_only_fields.py` | 2 | contract | ``deleted_at``, ``archived_at``, ``sequence_id`` and ``is_draft`` are read-only on work item PATCH. |
| `apps/api/plane/tests/contract/api/test_issues.py` | 6 | contract | Regression tests for GHSA-p885-6jpg-cr2p on the work-item list |
| `apps/api/plane/tests/contract/api/test_labels.py` | 10 | contract | Test Label List and Create API Endpoint |
| `apps/api/plane/tests/contract/api/test_members_lite.py` | 5 | contract | Contract tests for the workspace/project members-lite endpoints. |
| `apps/api/plane/tests/contract/api/test_modules_lite.py` | 1 | contract | Contract tests for the modules-lite endpoint. |
| `apps/api/plane/tests/contract/api/test_non_object_json_body.py` | 3 | contract | v1 write endpoints reject a JSON body that is not an object or array. |
| `apps/api/plane/tests/contract/api/test_project_members_roster_scope.py` | 2 | contract | Contract tests for ``ProjectMemberListCreateAPIEndpoint`` (v1) authorization. |
| `apps/api/plane/tests/contract/api/test_projects.py` | 11 | contract | Contract tests for POST /api/v1/workspaces/{slug}/projects/. |
| `apps/api/plane/tests/contract/api/test_projects_lite.py` | 5 | contract | Contract tests for the projects-lite endpoint. |
| `apps/api/plane/tests/contract/api/test_state_admin_scope.py` | 3 | contract | Contract tests for the v1 state endpoints' write authorization and default handling. |
| `apps/api/plane/tests/contract/api/test_work_item_link_relation_project_scope.py` | 2 | contract | v1 work item link and relation creates bind the URL ``issue_id`` to the URL |
| `apps/api/plane/tests/contract/app/test_api_token.py` | 20 | contract | Test cases for ApiTokenEndpoint |
| `apps/api/plane/tests/contract/app/test_asset_role_scope_app.py` | 13 | contract | Contract tests for role rules on asset confirm/update/delete/restore. |
| `apps/api/plane/tests/contract/app/test_authentication.py` | 41 | contract | Test magic link generation functionality |
| `apps/api/plane/tests/contract/app/test_avatar_url_annotation.py` | 9 | contract | Regression tests for the ``avatar_url`` annotation used by the assignee |
| `apps/api/plane/tests/contract/app/test_creator_project_membership_app.py` | 5 | contract | The ``allow_permission(creator=True)`` shortcut on project routes applies only |
| `apps/api/plane/tests/contract/app/test_cycle_issue_app.py` | 2 | contract | Regression test for GHSA-4w5x-wc9w-f47x. |
| `apps/api/plane/tests/contract/app/test_deploy_board_identity_readonly_app.py` | 11 | contract | Contract tests for ``DeployBoardViewSet`` partial_update. |
| `apps/api/plane/tests/contract/app/test_deploy_board_project_scope_app.py` | 6 | contract | Contract tests for ``DeployBoardViewSet`` authorization. |
| `apps/api/plane/tests/contract/app/test_draft_to_issue_owner_scope_app.py` | 2 | contract | Contract tests for draft-to-issue conversion ownership scoping. |
| `apps/api/plane/tests/contract/app/test_export_order_by_allowlist_app.py` | 2 | contract | ExportIssuesEndpoint.get sanitizes the order_by query param against |
| `apps/api/plane/tests/contract/app/test_favorite_entity_scope_app.py` | 15 | contract | Favorites only point at entities the user can see. |
| `apps/api/plane/tests/contract/app/test_intake_issue_read_only_fields_app.py` | 1 | contract | Read-only work item fields sent through ``IntakeIssueViewSet.partial_update`` are |
| `apps/api/plane/tests/contract/app/test_issue_history_app.py` | 1 | contract | ``IssueActivityEndpoint`` without ``activity_type`` merges activities and comments. |
| `apps/api/plane/tests/contract/app/test_issue_history_scope_app.py` | 3 | contract | Issue history and comment list only return rows for an issue in the URL project. |
| `apps/api/plane/tests/contract/app/test_issue_id_project_scope_app.py` | 3 | contract | Issue sub-resource creates bind the URL ``issue_id`` / ``comment_id`` to the URL |
| `apps/api/plane/tests/contract/app/test_issue_list_guest_scope_app.py` | 3 | contract | Contract tests for ``IssueListEndpoint`` guest scoping. |
| `apps/api/plane/tests/contract/app/test_issue_read_only_fields_app.py` | 2 | contract | ``deleted_at``, ``archived_at``, ``sequence_id`` and ``is_draft`` are read-only on ``IssueViewSet.partial_update``. |
| `apps/api/plane/tests/contract/app/test_issue_subresource_scope_app.py` | 22 | contract | Contract tests for issue sub-resource scoping on comment + relation endpoints. |
| `apps/api/plane/tests/contract/app/test_module_issue_destroy_app.py` | 2 | contract | DELETE .../modules/{module_id}/issues/{issue_id}/ when the link is already gone. |
| `apps/api/plane/tests/contract/app/test_module_project_scope_app.py` | 4 | contract | Module write endpoints bind the path module_id / issue_id to the URL project. |
| `apps/api/plane/tests/contract/app/test_oauth_callback_state_app.py` | 5 | contract | The OAuth callback proceeds only when the state matches the non-empty one stored in the session. |
| `apps/api/plane/tests/contract/app/test_page_guest_view_scope_app.py` | 3 | contract | ProjectPagePermission applies the guest_view_all_features rule to every |
| `apps/api/plane/tests/contract/app/test_page_order_by_allowlist_app.py` | 4 | contract | Regression tests for page order_by ORM injection (WEB-8110). |
| `apps/api/plane/tests/contract/app/test_page_version_project_scope_app.py` | 5 | contract | Regression tests for GHSA-g49r-p85q-qq2w / GHSA-ghcr-frqr-6pqr. |
| `apps/api/plane/tests/contract/app/test_password_strength_input_bound_app.py` | 3 | contract | Password strength checks score at most ZXCVBN_MAX_LENGTH characters from each end |
| `apps/api/plane/tests/contract/app/test_project_app.py` | 25 | contract | Test project POST operations |
| `apps/api/plane/tests/contract/app/test_project_join_cross_project_activation.py` | 3 | contract | Regression tests for SECUR-234. |
| `apps/api/plane/tests/contract/app/test_project_member_is_active_authz.py` | 9 | contract | Regression tests for GHSA-hpgm-9r34-c4x5 / GHSA-25gg-cxm8-g7h9. |
| `apps/api/plane/tests/contract/app/test_project_self_join_role_app.py` | 3 | contract | Self-joining a public project (``UserProjectInvitationsViewset.create``) grants |
| `apps/api/plane/tests/contract/app/test_search_guest_scope_app.py` | 5 | contract | Contract tests for guest scoping in the search endpoints. |
| `apps/api/plane/tests/contract/app/test_session_origin_check_app.py` | 2 | contract | Cookie-Schreibzugriff von fremdem Origin wird abgewiesen; eigener Origin bzw. ohne Origin erfolgreich (`TestSessionWriteOriginCheck`). |
| `apps/api/plane/tests/contract/app/test_space_asset_comment_scope_app.py` | 9 | contract | Contract tests for public Space comment-image assets. |
| `apps/api/plane/tests/contract/app/test_spaces_board_object_scope_app.py` | 27 | contract | Contract tests for public Spaces board object-ID scoping. |
| `apps/api/plane/tests/contract/app/test_state_admin_scope_app.py` | 6 | contract | Contract tests for StateViewSet write authorization and default-state handling. |
| `apps/api/plane/tests/contract/app/test_static_asset_disposition_app.py` | 3 | contract | Asset URLs are served inline only for allow-listed image types, with the response |
| `apps/api/plane/tests/contract/app/test_sub_issue_cross_project_scope_app.py` | 5 | contract | Contract tests for ``SubIssuesEndpoint`` cross-project scoping. |
| `apps/api/plane/tests/contract/app/test_user_email_change_app.py` | 7 | contract | The email-change code allows MAX_VERIFY_ATTEMPTS tries and both endpoints are throttled per IP. |
| `apps/api/plane/tests/contract/app/test_user_owned_fk_scope_app.py` | 7 | contract | Contract tests for user-scoped foreign keys on the ``users/me`` endpoints. |
| `apps/api/plane/tests/contract/app/test_webhook_secret_key_scope_app.py` | 6 | contract | Regression tests for WEB-8103. |
| `apps/api/plane/tests/contract/app/test_workspace_analytics_project_scope_app.py` | 9 | contract | Contract tests for project-scoping of the workspace analytics endpoints. |
| `apps/api/plane/tests/contract/app/test_workspace_app.py` | 3 | contract | Test workspace CRUD operations |
| `apps/api/plane/tests/contract/app/test_workspace_cycles_modules_project_scope_app.py` | 4 | contract | Contract tests for workspace-wide cycles/modules project-scoping. |
| `apps/api/plane/tests/contract/app/test_workspace_draft_project_membership_app.py` | 19 | contract | Contract tests for project scope on workspace drafts (INFRA-1125, INFRA-1136). |
| `apps/api/plane/tests/contract/app/test_workspace_file_asset_project_scope_app.py` | 5 | contract | Contract tests for ``WorkspaceFileAssetEndpoint`` project-scoping. |
| `apps/api/plane/tests/contract/app/test_workspace_invitation_update_app.py` | 4 | contract | Invitation updates (``PATCH /api/workspaces/<slug>/invitations/<pk>/``) may only |
| `apps/api/plane/tests/contract/app/test_workspace_member_mass_assignment_app.py` | 9 | contract | Regression tests for WEB-8332. |
| `apps/api/plane/tests/contract/app/test_workspace_stats_grouping_project_scope_app.py` | 7 | contract | Contract tests for project scoping of workspace-level stats and issue grouping. |
| `apps/api/plane/tests/contract/app/test_workspace_update_admin_scope_app.py` | 3 | contract | Contract tests for WorkSpaceViewSet updates. |
| `apps/api/plane/tests/contract/app/test_workspace_user_preference_app.py` | 2 | contract | Contract tests for the sidebar preference PATCH endpoint. |
| `apps/api/plane/tests/contract/app/test_workspace_user_profile_scope_app.py` | 12 | contract | Contract tests for workspace user-profile endpoint scoping. |
| `apps/api/plane/tests/smoke/test_auth_smoke.py` | 2 | smoke | Smoke tests for authentication endpoints |
| `apps/api/plane/tests/unit/bg_tasks/test_cleanup_task.py` | 7 | unit | Unit tests for the log cleanup tasks. |
| `apps/api/plane/tests/unit/bg_tasks/test_copy_s3_objects.py` | 5 | unit | Test the copy_s3_objects_of_description_and_assets function |
| `apps/api/plane/tests/unit/bg_tasks/test_export_task_guest_scope.py` | 1 | unit | issue_export_task: guests only export issues they created unless guest_view_all_features. |
| `apps/api/plane/tests/unit/bg_tasks/test_issue_activity_scope.py` | 11 | unit | issue_activity only records objects from the activity's own project/workspace; |
| `apps/api/plane/tests/unit/bg_tasks/test_ssrf_advisories.py` | 12 | unit | Per-advisory SSRF regression tests. |
| `apps/api/plane/tests/unit/bg_tasks/test_unsnooze_expired_intake_issues.py` | 7 | unit | Lapsed intake snoozes return to PENDING; snoozes are day-granular in the project timezone. |
| `apps/api/plane/tests/unit/bg_tasks/test_url_security.py` | 24 | unit | SSRF-protection tests for the webhook + link-unfurling clusters (advisories A/B/C): |
| `apps/api/plane/tests/unit/bg_tasks/test_work_item_link_task.py` | 20 | unit | Test validate_url_ip blocks private/internal IPs. |
| `apps/api/plane/tests/unit/middleware/test_api_authentication.py` | 2 | unit | Unit tests for APIKeyAuthentication. |
| `apps/api/plane/tests/unit/middleware/test_db_routing.py` | 26 | unit | Unit tests for ReadReplicaRoutingMiddleware. |
| `apps/api/plane/tests/unit/middleware/test_logger.py` | 3 | unit | Unit tests for APITokenLogMiddleware. |
| `apps/api/plane/tests/unit/models/test_issue_comment_modal.py` | 7 | unit | Test the IssueComment model |
| `apps/api/plane/tests/unit/models/test_workspace_model.py` | 2 | unit | Test the Workspace model |
| `apps/api/plane/tests/unit/serializers/test_expand.py` | 10 | unit | Regression tests for the ``expand`` query parameter. |
| `apps/api/plane/tests/unit/serializers/test_issue_recent_visit.py` | 1 | unit | Test the IssueRecentVisitSerializer |
| `apps/api/plane/tests/unit/serializers/test_issue_serializer_api.py` | 3 | unit | Test that IssueSerializer rejects invalid assignees/labels instead of silently dropping them |
| `apps/api/plane/tests/unit/serializers/test_label.py` | 2 | unit | Test the LabelSerializer |
| `apps/api/plane/tests/unit/serializers/test_workspace.py` | 8 | unit | Test the WorkspaceLiteSerializer |
| `apps/api/plane/tests/unit/settings/test_cookie_secure.py` | 11 | unit | Unit tests for deriving the session/CSRF cookie Secure flag. |
| `apps/api/plane/tests/unit/settings/test_num_proxies.py` | 2 | unit | Unit tests for the optional NUM_PROXIES setting. |
| `apps/api/plane/tests/unit/settings/test_retention.py` | 5 | unit | Unit tests for the log-retention env parsing helper. |
| `apps/api/plane/tests/unit/settings/test_storage.py` | 9 | unit | Test the configurable signed URL expiration in S3Storage |
| `apps/api/plane/tests/unit/settings/test_storage_credentials.py` | 2 | unit | Unit tests for the object-storage credential settings in plane.settings.common. |
| `apps/api/plane/tests/unit/utils/test_csv_export_sanitization.py` | 3 | unit | CSV exports must not emit formula-triggering values, including in header rows. |
| `apps/api/plane/tests/unit/utils/test_email.py` | 6 | unit | Covers the HTML-to-plain-text conversion used for the text/plain part of emails. |
| `apps/api/plane/tests/unit/utils/test_grouper.py` | 1 | unit | `issue_group_values` verlangt Projekt oder User. |
| `apps/api/plane/tests/unit/utils/test_issue_datetime_filters.py` | 7 | unit | Regression tests for created_at / updated_at rich-filter lookups (WEB-8477 Bug 5). |
| `apps/api/plane/tests/unit/utils/test_issue_filters.py` | 5 | unit | Regression test for the "Updated At" filter bug — the filter was |
| `apps/api/plane/tests/unit/utils/test_order_by_sanitize.py` | 7 | unit | Regression tests for order_by injection on the external REST API. |
| `apps/api/plane/tests/unit/utils/test_order_queryset.py` | 4 | unit | Regression tests for GHSA-wwgj-929g-42cm. |
| `apps/api/plane/tests/unit/utils/test_paginator.py` | 5 | unit | Stand-in for GroupedOffsetPaginator/SubGroupedOffsetPaginator that |
| `apps/api/plane/tests/unit/utils/test_path_validator.py` | 5 | unit | Regression test for authority-relative open-redirect via next_path. |
| `apps/api/plane/tests/unit/utils/test_redis.py` | 12 | filterwarnings,unit | `_redis_ssl_kwargs` (ENV → SSL-Kwargs, TLS-Pool für rediss) und `redis_instance` (URL-Credentials, DB-Auswahl, Passwort-URLs, Zertifikats-/Hostname-Prüfung, CA-Bundle, Abschaltung, URL-Optionen). |
| `apps/api/plane/tests/unit/utils/test_url.py` | 28 | unit | Test the contains_url function |
| `apps/api/plane/tests/unit/utils/test_uuid.py` | 4 | unit | Test the UUID utilities |
| `apps/api/plane/tests/unit/utils/test_xlsx_export_sanitization.py` | 10 | unit | XLSX issue exports must not store user-controlled values as formula cells. |
| `apps/api/plane/tests/unit/utils/test_zxcvbn_imports.py` | 1 | unit | Password strength is scored only through plane.authentication.utils.password. |
| `apps/api/plane/tests/unit/views/test_base_dispatch.py` | 1 | unit | Regression tests for the ``dispatch()`` exception handling on the shared |
| `apps/api/plane/tests/unit/views/test_issue_link.py` | 4 | unit | Unit regression tests for IssueLinkViewSet.partial_update. |
| `apps/api/plane/tests/unit/views/test_non_object_json_body.py` | 2 | unit | Both v1 base classes reject scalar write bodies and allow objects and arrays. |
| `apps/api/plane/tests/unit/views/test_session_origin_check.py` | 5 | unit | Cookie-authenticated writes must come from the request's own origin or a configured Plane origin. |

#### 2.25.2 TypeScript (Vitest)

| Paket | Konfiguration | Dateien (Tests) | Prüfgegenstand | Quelle |
|---|---|---|---|---|
| `apps/live` | `environment: "node"`, `globals: true`, `include: tests/**/*.test.ts, tests/**/*.spec.ts`, Coverage v8 (`text, json, html`, `src/**/*.ts` ohne `*.d.ts`, `types.ts`), Alias `@` → `src` | `tests/lib/pdf/pdf-rendering.test.ts` (21): `renderPlaneDocToPdfBuffer` – leeres Dokument, Titel, Überschriften, Absätze, Bullet-/Ordered-/Task-Listen, Codeblock, Blockquote, Tabelle, Horizontal Rule, Marks (bold/italic), Links, Seitengrößen, Querformat, Author-/Subject-Metadaten, Mentions mit aufgelöstem Display-Namen, gemischtes Dokument, tief verschachtelte Listen, `noAssets`; `tests/services/pdf-export/effect-utils.test.ts` (11): `withTimeoutAndRetry`, `recoverWithDefault`, `tryAsync` | PDF-Export | `apps/live/vitest.config.ts`, `apps/live/tests/**` |
| `packages/blocks` | Projekte `unit` (`src/**/*.test.ts`, node) und `dom` (`src/**/*.test.tsx`, jsdom, Setup `vitest.setup.dom.ts`); Coverage v8 ohne Stories/Index/Types | `__tests__/dom-scrolling.test.tsx` (1), `breadcrumb/breadcrumb-navigation-select.test.tsx` (20), `breadcrumb/breadcrumbs.test.tsx` (20), `common/color-swatch-picker/color-swatch-picker.test.tsx` (7), `common/color-swatch-picker/hex.test.ts` (4), `common/common-a11y.test.tsx` (6), `common/sortable/sortable.test.tsx` (5), `context-menu/context-menu.test.tsx` (19), `context-menu/helpers.test.ts` (9), `dialog/confirm-dialog.test.tsx` (17), `emoji-icon-picker/emoji-picker.test.tsx` (2), `emoji-icon-picker/search-a11y.test.tsx` (3), `emoji-reaction/emoji-reaction-picker.test.tsx` (2), `property-select/date-select.test.tsx` (20), `property-select/member-select.test.tsx` (4), `property-select/outside-click.test.tsx` (3), `property-select/tab-index.test.tsx` (2 × `it.each`), `select/menu-search-input.test.tsx` (2), `select/nested-submenu/nested-submenu.dismissal.test.tsx` (6), `select/select.test.tsx` (77), `toast/toast-manager.test.ts` (22) | UI-Verhalten (Öffnen/Anker, Tastatur, a11y, Dismissal, Toast-Manager) – relevante Referenz für 1:1-Verhalten der Angular-Komponenten | `packages/blocks/vitest.config.ts`, `packages/blocks/src/**` |
| `packages/services` | Default (`vitest run`) | `src/helpers/url.test.ts` (5): `ensureAPITrailingSlash`/`normalizeAPIRequestURL` | Trailing-Slash-Regeln | `packages/services/src/helpers/url.test.ts` |
| `packages/codemods` | `environment: "node"` | `tests/function-declaration.spec.ts` (23), `tests/remove-directives.spec.ts` (10) | jscodeshift-Transforms | `packages/codemods/*` |

`apps/web`, `apps/admin`, `apps/space` besitzen **keine** Tests (keine `test`-Scripts in `apps/{web,admin,space}/package.json`).

### 2.26 Deployment-Varianten & Betriebsskripte

| Skript / Datei | Aktionen | Detailverhalten | Quelle |
|---|---|---|---|
| `deployments/cli/community/install.sh` (als Release-Asset `setup.sh`) | Menü `1) Install`, `2) Start`, `3) Stop`, `4) Restart`, `5) Upgrade`, `6) View Logs`, `7) Backup Data`, `8) Exit` (Default 2); auch als Argument `install`, `start`, `stop`, `restart`, `upgrade`, `logs`, `backup` | **Install:** `APP_RELEASE=stable` → neueste Release-Tag über `https://api.github.com/repos/makeplane/plane/releases/latest`; prüft per `docker manifest inspect makeplane/plane-proxy:<tag>` die CPU-Architektur (amd64/arm64), sonst Angebot zum lokalen Build (`git clone --depth 1` nach `~/tmp/plane`, `build.yml`, `DOCKERHUB_USER=myplane`, `APP_RELEASE=local`, `PULL_POLICY=never`); lädt `docker-compose.yml` und `variables.env` vom Release (Fallback raw GitHub), archiviert alte Dateien unter `plane-app/archive/<ts>.*`, übernimmt Werte aus `plane.env.bak` (`syncEnvFile`), generiert/rotiert MinIO-Credentials (nur wenn `USE_MINIO=1` und Endpoint `http://plane-minio:9000` und Secret noch `secret-key`/leer), `pull --policy always`. **Start:** `up -d --pull if_not_present --quiet-pull`; wartet auf Ende des Containers `plane-app-migrator`, Abbruch bei ExitCode ≠ 0; wartet bis `python3 -c "urllib.request.urlopen('http://localhost:8000/', timeout=3)"` im API-Container erfolgreich ist (max. 300 s; danach Warnung). **Stop:** `down`. **Restart:** Stop + Start. **Upgrade:** vergleicht Release-Tag, Bestätigung, Stop, Install. **Logs:** Auswahl `web, space, api, worker, beat-worker, migrator, proxy, plane-redis, plane-db, plane-minio, plane-mq` (kein `live`, kein `admin`). **Backup:** `docker cp` aus laufenden Containern `plane-db:/var/lib/postgresql/data` → `pgdata.tar.gz`, `plane-minio:/export` → `uploads.tar.gz`, `plane-mq:/var/lib/rabbitmq` → `rabbitmq_data.tar.gz`, `plane-redis:/data` → `redisdata.tar.gz` nach `plane-app/backup/<YYYYMMDD-HHMM>/` | `DEP/cli/community/install.sh` |
| `deployments/cli/community/restore.sh` | `./restore.sh <backup-ordner>` | Bricht ab, wenn Compose-Projekt `plane-app` läuft (`jq` nötig); für jede `*.tar.gz`: Volume `plane-app_<name>` löschen, neu anlegen, per `busybox` entpacken (Suffixe `_pgdata`, `_redisdata`, `_uploads`, `_rabbitmq_data`) | `DEP/cli/community/restore.sh` |
| `deployments/cli/community/restore-airgapped.sh` | Restore in „Plane Commercial Air-Gapped“ | Fragt Backup-Ordner und Installationspfad (Default `~/planeairgapped`), prüft `docker-compose.yml` und dass Projekt `plane-airgapped` nicht läuft; entpackt nach `data/` und benennt `pgdata→db`, `redisdata→redis`, `uploads→minio/uploads`, `rabbitmq_data→mq` mit Rollback (`replaceDir`); `chown` | `DEP/cli/community/restore-airgapped.sh` |
| `deployments/cli/community/migration-0.13-0.14.sh` | Einmalige Volume-Migration v0.13.2 → v0.14 | Kopiert Volumes `*_pgdata`, `*_uploads`, `*_redisdata` zwischen Präfixen | `DEP/cli/community/migration-0.13-0.14.sh` |
| `deployments/swarm/community/swarm.sh` | Menü `1) Deploy Stack`, `2) Remove Stack`, `3) View Stack Status`, `4) Redeploy Stack`, `5) Upgrade`, `6) View Logs`, `7) Exit` (Default 3) | Stack-Name wird abgefragt; `docker stack deploy -c docker-compose.yml <stack>` nach `source plane.env`; wartet auf Migrator (ExitCode-Prüfung) und auf Logzeile `Application Startup Complete` im API-Container; `docker stack rm`; `docker stack ps`; Logs per `docker service logs` | `DEP/swarm/community/swarm.sh` |
| `deployments/aio/community/build.sh` | `./build.sh --release=<vX.Y.Z> [--image-name=…]` | Installiert ggf. `yq`; erzeugt `dist/plane.env` (aus `variables.env` + `APP_RELEASE_VERSION`, `APP_RELEASE`, `APP_VERSION`, `API_BASE_URL=http://localhost:3004`, `SITE_ADDRESS=:80`) und `dist/Caddyfile` (= `apps/proxy/Caddyfile.aio.ce`); gibt `docker build`-Kommando aus | `DEP/aio/community/build.sh` |
| `deployments/aio/community/start.sh` | Container-Entrypoint | Prüft Pflicht-ENV und Secrets (2.11.7), validiert `DOMAIN_NAME` (IPv4 oder FQDN ≤ 253 Zeichen), schreibt `plane.env` (`WEB_URL`, `CORS_ALLOWED_ORIGINS`, `DATABASE_URL`, `REDIS_URL`, `REDIS_SSL_*`, `AMQP_URL`, AWS-Werte, `AWS_S3_ENDPOINT_URL` Default `https://s3.${AWS_REGION}.amazonaws.com`, `BUCKET_NAME`, `USE_MINIO=0`, `SECRET_KEY`, `FILE_SIZE_LIMIT`, `LIVE_SERVER_SECRET_KEY`, `API_KEY_RATE_LIMIT`), exportiert alle Zeilen wörtlich, startet `supervisord` | `DEP/aio/community/start.sh` |
| `deployments/kubernetes/community/README.md` | – | Link auf Helm-Chart `plane-ce` (Artifact Hub) | dto. |

Systemanforderungen laut Doku: min. 2 vCPU / 4 GB RAM (Cloud-Server) (`DEP/cli/community/README.md`); lokale Entwicklung mit 8 GB RAM kann scheitern (`CONTRIBUTING.md` Z. 45). Client-IP hinter Proxies: `TRUSTED_PROXIES=private_ranges` + `NUM_PROXIES=1`, pro zusätzlichem LB/CDN-Hop `NUM_PROXIES` +1 (`DEP/cli/community/README.md`).

### 2.27 Laufzeitabhängigkeiten (Versionen)

| Komponente | Version / Image | Verwendet von | Quelle |
|---|---|---|---|
| PostgreSQL | `postgres:15.7-alpine`, `max_connections=1000`; Django 5.2 verlangt ≥ 14 | API, Worker, Beat, Migrator | `docker-compose*.yml`, `apps/api/docs/django-5.2-migration-plan.md` |
| Redis-kompatibel | `valkey/valkey:7.2.11-alpine` | API (Cache, Locks, Throttles), Live (Pub/Sub, Pflicht) | dto. |
| RabbitMQ | `rabbitmq:3.13.6-management-alpine` (AMQP 5672) | Celery-Broker | dto. |
| S3-Objektspeicher | `docker.io/pgsty/silo:RELEASE.2026-09-16T00-00-00Z` (MinIO-kompatibel; `mc`-Client im Image) | Assets | dto. |
| Reverse-Proxy | Builder `caddy:2.11.7-builder-alpine`, Laufzeit `caddy:2.11.4-alpine` | proxy, web, admin | `apps/proxy/Dockerfile.ce`, `apps/web/Dockerfile.web`, `apps/admin/Dockerfile.admin` |
| Python | 3.12.12 (prod), 3.12.5 (dev/test) | API | `apps/api/Dockerfile.api`, `apps/api/Dockerfile.dev` |
| uv | 0.12.21 (Digest `sha256:a7aed3216253ee804de3e2d8afa5073baa1a177335345d43845cd4165e43b711`) | Build | dto. |
| Node.js | `node:22-alpine` (Images), `>=22.22.0` (engines), 22.22.0 (`.node-version`, `.mise.toml`) | web/admin/space-Build, space-SSR, live | `package.json`, Dockerfiles |
| pnpm | 11.10.0 (corepack) | Build | `package.json` |
| Turbo | 2.10.11 | Build | `pnpm-workspace.yaml`, Dockerfiles |
| supervisord | `pip install supervisor` (unversioniert) | AIO | `DEP/aio/community/Dockerfile` |

### 2.28 Externe Netzwerkziele (Airgapped-Relevanz)

| Ziel | Zweck | Zeitpunkt | Verhalten ohne Internet | Quelle |
|---|---|---|---|---|
| `https://api.github.com/repos/makeplane/plane/releases/latest` | `Instance.latest_version` | jeder API-Start (`register_instance`, Timeout 10 s) | Fallback = aktuelle Version, Meldung „Error checking for latest version“ | `API/license/management/commands/register_instance.py` |
| `https://telemetry.plane.so` (OTLP gRPC :443) | Instanz-Metriken | beim Start (`push_instance_metrics.delay()`) und alle 360 min, solange `is_telemetry_enabled` | Exception geloggt | `API/license/bgtasks/telemetry_metrics.py`, `API/utils/otlp_endpoints.py` |
| `https://sites.plane.so/pages/691ef037…/` | Changelog-iframe (über `INSTANCE_CHANGELOG_URL` im Image) | beim Öffnen „Product updates“ | 15-s-Timeout → Fallback-Ansicht | `apps/api/Dockerfile.api`, `apps/web/components/global/product-updates/changelog.tsx` |
| `https://acme-v02.api.letsencrypt.org/directory` | TLS-Zertifikate | bei Domain in `SITE_ADDRESS` | Zertifikatsbezug scheitert | `apps/proxy/Caddyfile.ce` |
| `https://cdn.jsdelivr.net/npm/emoji-datasource-apple/img/apple/64/1f4a1.png` | Default-Emoji-URL der Callout-Erweiterung | Editor-Callout | Bild lädt nicht | `packages/editor/src/extensions/callout/utils.ts` Z. 20 |
| Emoji-Daten von `frimousse` | `EmojiPicker.Root` ohne `emojibaseUrl` (Bibliotheks-Default lädt Emojibase-Daten von jsDelivr) | Öffnen Emoji-Picker | Picker leer (zu verifizieren) | `packages/blocks/src/emoji-icon-picker/emoji/emoji.tsx` |
| OAuth-Provider (Google, GitHub, GitLab Default `https://gitlab.com`, Gitea) | Login | Login | nicht nutzbar | `API/authentication/provider/oauth/*` |
| LLM-Provider (OpenAI, Anthropic, Gemini) | KI-Funktionen | auf Anforderung | nicht nutzbar | `API/app/views/external/base.py` |
| Unsplash | Cover-Bilder | auf Anforderung | nicht nutzbar | `API/app/views/external/base.py` Z. 221 |
| SMTP-Server | E-Mails | Worker | Fehler geloggt | `API/license/utils/instance_value.py` |
| Webhook-Ziele, Link-Titel-Crawling | Webhooks, Link-Unfurl | Worker | Fehler/Retry | `API/bgtasks/webhook_task.py`, `API/bgtasks/work_item_link_task.py` |
| Docker Hub, GitHub Releases, raw.githubusercontent.com | Installation/Upgrade | Betreiber | Installation nicht möglich (außer lokaler Build) | `DEP/cli/community/install.sh` |
| Links (nur `href`, kein Laden): `plane.so`, `go.plane.so`, `docs.plane.so`, `developers.plane.so`, `forum.plane.so`, `status.plane.so`, `app.plane.so` (OG-URL), `sites.plane.so` (OG-URL Space) | Doku/Support/Marketing | Klick | Link tot | alle Fundstellen: `apps/admin/app/(all)/(dashboard)/ai/form.tsx`, `apps/admin/app/(all)/(dashboard)/general/form.tsx`, `apps/admin/app/(all)/(dashboard)/sidebar-help-section.tsx`, `apps/admin/app/root.tsx`, `apps/admin/components/instance/setup-form.tsx`, `apps/space/app/error.tsx`, `apps/space/app/root.tsx`, `apps/space/components/account/terms-and-conditions.tsx`, `apps/web/app/(all)/[workspaceSlug]/(settings)/settings/projects/page.tsx`, `apps/web/app/(all)/workspace-invitations/page.tsx`, `apps/web/app/error/prod.tsx`, `apps/web/app/root.tsx`, `apps/web/components/account/terms-and-conditions.tsx`, `apps/web/components/common/latest-feature-block.tsx`, `apps/web/components/estimates/root.tsx`, `apps/web/components/global/product-updates/fallback.tsx`, `apps/web/components/global/product-updates/footer.tsx`, `apps/web/components/power-k/config/help-commands.ts`, `apps/web/components/workspace/billing/comparison/plans.tsx`, `apps/web/components/workspace/sidebar/help-section/root.tsx`, `packages/constants/src/endpoints.ts`, `packages/constants/src/metadata.ts`, `packages/constants/src/payment.ts` |

Fonts (`@fontsource-variable/inter`, `@fontsource/ibm-plex-mono`, `@fontsource/material-symbols-rounded`) sind gebündelt (`apps/web/app/root.tsx`), es gibt keine Google-Fonts-/CDN-Stylesheets in den Frontends.

### 2.29 Dokumentation & Repo-Metadaten

| Datei | Inhalt | Migrationsrelevanz |
|---|---|---|
| `docs/linting.md` | OxLint-Leitfaden (Root-Config, Kommandos, VS-Code-Extension, Pre-Commit). Tabelle nennt `correctness` = **error**, `.oxlintrc.json` setzt `warn` (Inkonsistenz) | gering |
| `AGENTS.md` | Kommandos, Code-Style (`workspace:*`, `catalog:`, oxfmt, OxLint, MobX in `packages/shared-state`, Tests Pflicht, Primitives aus `@makeplane/propel`, Composite in `@plane/blocks` nur über Subpath-Imports), uv-Regeln (`--inexact` in Containern), Docker-Test-Kommandos | Vorbild für Agenten-Leitfaden des Zielsystems |
| `.github/instructions/bash.instructions.md` | pnpm-only, Turbo, Projektstruktur | gering |
| `.github/instructions/typescript.instructions.md` | TS-5.0–5.8-Leitlinien | gering |
| `.github/ISSUE_TEMPLATE/--bug-report.yaml`, `--feature-request.yaml`, `config.yaml` | Bug-Report (Felder: existing issue, current behavior, steps, environment, browser, edition, version; Labels `🐛bug`, `plane`), Feature-Request (Labels `✨feature`, `plane`), Kontakt-Links (Forum/Discussions, `mailto:support@plane.so`) | keine |
| `.github/pull_request_template.md` | Abschnitte Description, Type of Change (6 Checkboxen), Screenshots, Test Scenarios, References | keine |
| `apps/api/docs/django-5.2-migration-plan.md` | Durchgeführter Upgrade-Plan Django 4.2 → 5.2 (393 Tests grün, PG ≥ 14, state-only Migration `0122`) | Hinweis auf Testumfang/-stabilität |
| `apps/api/templates/` | `base.html`, `csrf_failure.html`, `admin/base_site.html`, E-Mail-Templates `emails/auth/{forgot_password,magic_signin}.html`, `emails/exports/analytics.html`, `emails/invitations/{project_invitation,workspace_invitation}.html`, `emails/notifications/{issue-updates,project_addition,webhook-deactivate}.html`, `emails/user/{email_updated,user_activation,user_deactivation}.html`, `emails/test_email.html` | Vorlagen für E-Mail-Bereich |
| `apps/api/plane/seeds/data/` | `cycles.json`, `issues.json`, `labels.json`, `modules.json`, `pages.json`, `projects.json`, `states.json`, `views.json` | Workspace-Seed (A02a) |

---

## 3. Verhalten / Logik / Abläufe im Detail (inkl. Edge-Cases)

### 3.1 Startsequenz des Backends

1. **Migrator** (`docker-entrypoint-migrator.sh`): `wait_for_db` → `migrate`. Im CLI-Compose `restart_policy: on-failure`; `install.sh` wartet auf das Ende des Containers `plane-app-migrator` und bricht bei ExitCode ≠ 0 mit „Plane Server failed to start ❌“ ab (`DEP/cli/community/install.sh` `startServices`).
2. **`wait_for_db`** holt lediglich `connections["default"]` (Connection-Handler) und fängt `OperationalError`. Da der Handler-Zugriff keine Verbindung öffnet, wartet der Befehl faktisch **nicht** auf die Datenbank (`API/db/management/commands/wait_for_db.py`). Das eigentliche Warten erledigt `wait_for_migrations` bzw. der Neustart des Containers.
3. **`wait_for_migrations`** (API, Worker, Beat): baut `MigrationExecutor` auf `default` und schläft 10 s, solange `migration_plan(leaf_nodes)` nicht leer ist (`…/wait_for_migrations.py`). Ist die DB nicht erreichbar, wirft der Executor → Skript endet (`set -e`) → Container-Neustart.
4. **`register_instance <signature>`** (nur API): ermittelt `current_version` (`APP_VERSION` → `package.json` → `v0.1.0`) und `latest_version` (GitHub-API, Fallback current). Existiert keine `Instance`: Anlage mit `instance_name="Plane Community Edition"`, `instance_id=secrets.token_hex(12)` (24 Hex-Zeichen), `current_version`, `latest_version`, `last_checked_at=now`, `is_test=(IS_TEST=="1")`, `edition="PLANE_COMMUNITY"`; sonst Update von `last_checked_at`, `current_version`, `latest_version`, `is_test`, `edition`. Danach immer `push_instance_metrics.delay()` (Broker muss erreichbar sein) (`API/license/management/commands/register_instance.py`).
5. **`configure_instance`**: Abbruch (`CommandError`), wenn `SECRET_KEY` fehlt/leer. Für jeden Schlüssel aus 2.11.2: `get_or_create(key)`; **nur bei Neuanlage** werden `category`, `is_encrypted`, `value` (ggf. verschlüsselt) gesetzt, sonst Meldung „configuration already exists“.
6. **`create_bucket`**: Bucket prüfen/anlegen, Fehler nur ausgeben.
7. **`clear_cache`**: `cache.clear()` (django-redis → leert die gesamte Redis-DB aus `REDIS_URL`, inkl. Magic-Codes, Throttle-Historien, Locks, Issue-Origin-Keys); Fehler → „Failed to clear cache“, kein Abbruch.
8. **`collectstatic --noinput`** (nur Produktion) → `plane/static-assets/collected-static`.
9. **gunicorn** mit `GUNICORN_WORKERS` Worker-Prozessen, `UvicornWorker` (ASGI), Recycling nach 1 200 ± 1 000 Requests, Access-Log auf stdout. Health-Check: `GET /` → `{"status": "OK"}` (nicht geloggt).

Worker/Beat starten parallel und warten nur auf Migrationen; Beat nutzt den `DatabaseScheduler` (Schedule aus `app.conf.beat_schedule` wird in die `django_celery_beat`-Tabellen übernommen).

### 3.2 Konfigurationsauflösung (ENV ↔ Datenbank)

- `get_configuration_value(keys)` (`API/license/utils/instance_value.py`): Bei `SKIP_ENV_VAR=1` (Default) werden bei **jedem Aufruf alle** `InstanceConfiguration`-Zeilen (`key, value, is_encrypted`) geladen; je angefragtem Key: Treffer → Wert (entschlüsselt, falls `is_encrypted`), kein Treffer → mitgegebener `default` (meist der ENV-Wert). Bei `SKIP_ENV_VAR=0`: ausschließlich `os.environ.get(key, default)`.
- **Konsequenz:** Nach dem ersten Start sind ENV-Änderungen für alle 36 Instanz-Keys wirkungslos; Änderungen erfolgen über God-Mode (`PATCH /api/instances/configurations/`, siehe God-Mode-Analyse).
- Verschlüsselung: Fernet; Schlüssel aus `SECRET_KEY` via PBKDF2-HMAC-SHA256, Salt konstant `b"salt"`, 100 000 Iterationen; leere Werte → `""`; Fehler (z. B. nach Änderung von `SECRET_KEY`) → `log_exception` und Rückgabe `""` (still) (`API/license/utils/encryption.py`).
- `get_email_configuration()` liefert Tupel `(EMAIL_HOST, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD, EMAIL_PORT, EMAIL_USE_TLS, EMAIL_USE_SSL, EMAIL_FROM)` mit ENV-Defaults (Absender-Default `Team Plane <team@mailer.plane.so>`).

### 3.3 Request-Weg Browser → Proxy → Dienste

- Produktions-Images werden mit leeren `VITE_*_BASE_URL` gebaut → alle Frontends rufen die API **relativ** (gleicher Origin) auf; der Proxy verteilt nach Pfad (2.8.1). Domain-Wechsel erfordert keinen Rebuild; Änderung der Base-Paths (`/god-mode`, `/spaces`, `/live`) dagegen schon (Vite-`base`, Router-`basename`, Konstanten sind Build-Zeit-Werte) (`apps/*/vite.config.ts`).
- Alle Axios-Aufrufe der Frontends und des Live-Servers erzwingen einen abschließenden `/` im Pfad (außer bei fremden absoluten URLs wie Presigned-S3-URLs, deren Signatur sonst bricht) (`packages/services/src/helpers/url.ts`), passend zu Djangos `APPEND_SLASH`.
- `withCredentials: true` → Session-Cookie wird mitgesendet; Schreibzugriffe werden per Origin-Check (2.14) statt CSRF-Token abgesichert.
- **Space-SSR:** Der einzige Server-Loader (`apps/space/app/issues/[anchor]/layout.tsx`) lädt OG-Metadaten über `fetch(\`${process.env.VITE_API_BASE_URL}/api/public/anchor/${anchor}/meta/\`)` (Anchor-Regex `^[a-zA-Z0-9_-]+$`). Mit dem Docker-Default `VITE_API_BASE_URL=""` ist die URL relativ und schlägt in Node fehl → Fallback auf Default-Titel/-Beschreibung (Fehler wird abgefangen). Die übrigen Space-Routen (`index`, `:workspaceSlug/:projectId` mit `clientLoader`, `issues/:anchor`, `*`) laden Daten clientseitig (`apps/space/app/routes.ts`).

### 3.4 Session-Cookie-Auswahl und Secure-Flag

- Die Session-Middleware wählt das Cookie anhand der **Teilzeichenkette** `"instances"` im Pfad (`API/authentication/middleware/session.py`). Edge-Case: Jeder Pfad, der „instances“ enthält (etwa ein Workspace-Slug `team-instances` → `/api/workspaces/team-instances/…`; nur die exakten Slugs `instances`/`instance` sind in `RESTRICTED_WORKSPACE_SLUGS` gesperrt, `API/utils/constants.py`), wird mit dem **Admin**-Cookie bedient (Benutzer erscheint nicht angemeldet). Im Zielsystem: strikt präfixbasiert (`/api/instances/`) umsetzen und als bewusste Abweichung dokumentieren.
- Secure-Flag: siehe 2.16; reine HTTP-Installationen erhalten nicht-sichere Cookies; ein einziger `http:`-Origin in `CORS_ALLOWED_ORIGINS` deaktiviert Secure, sofern `WEB_URL` nicht `https://` ist (`API/tests/unit/settings/test_cookie_secure.py`, 11 Tests).
- Gespeichert wird nur bei `status < 500`; bei gleichzeitigem Logout → `SessionInterrupted`.

### 3.5 Rate-Limits hinter Proxies

- DRF ermittelt die Client-Identität ohne `NUM_PROXIES` aus dem **gesamten** `X-Forwarded-For`-Header (Whitespace entfernt), sonst `REMOTE_ADDR` (DRF-Standardverhalten). Da Caddy mit `trusted_proxies 0.0.0.0/0` clientseitige `X-Forwarded-For`-Werte übernimmt und anhängt, kann ein Client ohne `NUM_PROXIES` seinen Throttle-Schlüssel frei wählen. Empfohlen: `TRUSTED_PROXIES=private_ranges` und `NUM_PROXIES=1` (`DEP/cli/community/README.md`, `API/tests/unit/settings/test_num_proxies.py`).
- `AnonRateThrottle` (30/min) gilt für **alle** anonymen DRF-Requests, also auch öffentliche Space-Seiten und `GET /api/instances/`.
- `AssetRateThrottle` schlüsselt nach Asset-ID (5/min pro Asset, global über alle Clients).
- `ApiKeyRateThrottle.rate` wird beim Import aus `settings.API_KEY_RATE_LIMIT` gelesen.

### 3.6 Objektspeicher-Abläufe

- Upload: Presigned POST mit `content-length-range 1..min(size, FILE_SIZE_LIMIT)` und fixiertem `Content-Type` (`API/settings/storage.py`, `API/app/views/asset/v2.py`). Bei `USE_MINIO=1` zeigt die URL auf den **Host des API-Requests** (Proxy), Pfad `/{bucket}`; Caddy leitet `/{BUCKET_NAME}` und `/{BUCKET_NAME}/*` an MinIO weiter und lässt den `Host`-Header unverändert (Voraussetzung für gültige v4-Signaturen).
- Edge-Case: Der Proxy begrenzt **jeden** Request-Body auf `FILE_SIZE_LIMIT`; ein Multipart-POST einer Datei nahe am Limit enthält zusätzlich Formularfelder und kann daher mit 413 am Proxy scheitern, obwohl die Datei selbst das Limit einhält.
- Serverseitige S3-Aufrufe ohne Request (Worker: `get_asset_object_metadata`, `copy_object`, Exporte) verwenden `AWS_S3_ENDPOINT_URL` (intern `http://plane-minio:9000`). Im Root-`docker-compose.yml` und in `docker-compose-local.yml` liefert `apps/api/.env.example` aber `AWS_S3_ENDPOINT_URL="http://localhost:9000"` und `USE_MINIO=0` → aus dem Container heraus ist `localhost:9000` nicht MinIO (Edge-Case E-02/E-03).
- Download: Presigned GET; inline nur für `INLINE_SAFE_MIME_TYPES` mit gepinntem `ResponseContentType`, sonst `attachment` (`API/tests/contract/app/test_static_asset_disposition_app.py`).
- Bucket-Policy: keine; `AWS_DEFAULT_ACL = "public-read"` wird von den Presigned-Flows nicht genutzt (Presigned-POST-Felder enthalten nur `Content-Type`/`key`).

### 3.7 Live-Server-Abläufe (infrastrukturell)

- Start: `redisManager.initialize()` (ohne URL: Warnung, aber anschließend scheitert `new Redis()`-Extension mit „Redis client not initialized“ → Exit 1) → Hocuspocus-Instanz → Controller-Registrierung über `@plane/decorators` → 404-Handler → `listen(PORT)` (`LIVE/server.ts`, `LIVE/extensions/redis.ts`). Redis ist damit **Pflicht**.
- `CORS_ALLOWED_ORIGINS=""` ergibt `[""]` (Länge 1) → `cors({origin: [""]})` → kein Origin wird erlaubt; für Same-Origin-Betrieb hinter dem Proxy und für WebSockets irrelevant.
- `POST /live/convert-document/` ist ohne Authentifizierung und wird vom Proxy öffentlich unter `/live/*` ausgeliefert (CPU-intensive Konvertierung durch Dritte möglich).
- `LIVE_SERVER_SECRET_KEY` ist Pflicht-ENV, aber `requireSecretKey` ist an keinem CE-Controller angebracht (`LIVE/lib/auth-middleware.ts`, `LIVE/controllers/*`).
- Persistenz ausschließlich über API mit Benutzer-Cookie; Debounce 10 s; Multi-Instanz über Redis-Pub/Sub.

### 3.8 Telemetrie & „Phone home“

- Instanz-Telemetrie ist **standardmäßig aktiv** (`Instance.is_telemetry_enabled` Default `True`) und sendet alle 6 h Metriken (Zählwerte, Workspace-Slugs, Domain aus `WEB_URL`, Versionen) an `telemetry.plane.so` (2.23). Abschaltbar nur über das Instanz-Flag (God-Mode).
- Bei jedem API-Start: GitHub-Release-Abfrage (2.28).
- ADR-004 verlangt: keine Telemetrie nach außen → im Zielsystem **entfällt** der externe Push; OpenTelemetry nur gegen lokal konfigurierte Collector (Aspire-Dashboard/OTLP-Endpoint des Betreibers).

### 3.9 Celery-Besonderheiten

- `delete_old_s3_link` ist zweimal täglich eingeplant (01:30 und 03:45 UTC) unter zwei Namen (`check-every-day-to-delete_exporter_history`, `check-every-day-to-delete-exporter-history`) (`API/celery.py`).
- `METRICS_PUSH_INTERVAL_MINUTES` außerhalb `1…10 000 000` oder unparsebar → 360.
- Keine Ergebnis-Speicherung; Fehler werden pro Task geloggt; nur `webhook_send_task` hat Auto-Retry.
- Celery-Logger erhält zusätzlich JSON-StreamHandler (doppelte Ausgabe neben Celerys eigenem Handler möglich).

### 3.10 Edge-Cases & Inkonsistenzen (nummeriert, für Tests und bewusste Entscheidungen)

| Nr. | Befund | Quelle | Empfehlung Zielsystem |
|---|---|---|---|
| E-01 | Root-`docker-compose.yml`: Service `live` ohne `env_file`/`environment` → zod-Validierung (`API_BASE_URL`, `LIVE_SERVER_SECRET_KEY` Pflicht) beendet den Prozess, `restart: always` → Crash-Loop | `docker-compose.yml`, `LIVE/env.ts` | Aspire-AppHost verdrahtet alle Pflicht-Konfigurationen; Start-Validierung (`ValidateOnStart`) mit klarer Meldung |
| E-02 | Root-Compose nutzt `apps/api/.env` (`USE_MINIO=0`, `AWS_S3_ENDPOINT_URL=http://localhost:9000`) → serverseitige S3-Aufrufe aus dem Container schlagen fehl; Presigned-URLs zeigen auf `localhost:9000` | `docker-compose.yml`, `apps/api/.env.example` | getrennte interne/öffentliche S3-Endpoints als explizite Optionen |
| E-03 | Local-Compose: identischer Effekt für API/Worker im Container (Browser-Uploads funktionieren über publizierten Port 9000) | `docker-compose-local.yml` | dto. |
| E-04 | `wait_for_db` prüft keine echte Verbindung | `API/db/management/commands/wait_for_db.py` | Aspire `WaitFor(postgres)` + Health-Checks |
| E-05 | `GUNICORN_WORKERS` ohne Default | `apps/api/bin/docker-entrypoint-api.sh` | Kestrel ohne Worker-Konzept; ggf. Replikas |
| E-06 | ENV-Änderungen an Instanz-Keys nach Erststart wirkungslos | `configure_instance.py` | Bewusst übernehmen (DB = Wahrheit) oder ENV-Override-Regel definieren; dokumentieren |
| E-07 | `SECRET_KEY`-Wechsel macht verschlüsselte Konfiguration still unlesbar und alle Sessions ungültig | `encryption.py` | ASP.NET Data Protection mit persistiertem Key-Ring (Postgres), Rotation unterstützt |
| E-08 | Fehlt `SECRET_KEY` in Worker/Beat, erzeugt jeder Prozess einen eigenen Zufallsschlüssel (nur die API bricht in `configure_instance` ab) → Worker kann z. B. SMTP-Passwort nicht entschlüsseln (leer) | `S/common.py`, `encryption.py` | gemeinsamer Key-Ring für alle Dienste |
| E-09 | Admin-Cookie-Auswahl per Substring `"instances"` | `API/authentication/middleware/session.py` | präfixbasiert |
| E-10 | Leeres `CORS_ALLOWED_ORIGINS` → `CORS_ALLOW_ALL_ORIGINS=True` **mit** `CORS_ALLOW_CREDENTIALS=True` | `S/common.py` | Default: nur eigene Origins |
| E-11 | Throttle-Identität ohne `NUM_PROXIES` aus vollständigem, vom Client beeinflussbarem `X-Forwarded-For` | `S/common.py`, DRF | ASP.NET `ForwardedHeaders` mit `KnownProxies/KnownNetworks`, RateLimiter auf `RemoteIpAddress` |
| E-12 | `ENABLE_SIGNUP`-Defaults: `1` (Adapter, Config-Seed), `0` (Instanz-Endpoint) | `adapter/base.py`, `license/api/views/instance.py`, `core.py` | ein Default (`1`) zentral |
| E-13 | `ENABLE_MAGIC_LINK_LOGIN`: Config-Seed `0`, Views-Defaults `1` → nach Erststart ist Magic-Login aus, solange ENV nicht gesetzt | `core.py`, `check.py` | ein Default zentral (Seed-Wert `0` übernehmen, da er nach Erststart wirksam ist) |
| E-14 | `delete_old_s3_link` doppelt im Beat-Schedule | `API/celery.py` | einmal einplanen |
| E-15 | `/robots.txt` landet im Proxy bei web, nicht bei der API-View | `apps/proxy/Caddyfile.ce` | Verhalten 1:1 (web liefert, falls vorhanden, `public/robots.txt`) – zu prüfen |
| E-16 | AIO-Caddyfile ohne `/static/*`, ohne `/spaces`-Redirect; AIO-README-Ports veraltet | `apps/proxy/Caddyfile.aio.ce`, `DEP/aio/community/README.md` | AIO-Variante im Zielsystem aus derselben Routing-Definition generieren |
| E-17 | `swarm.sh`: Menü-Regex `^[1-6]$` lässt „7) Exit“ nicht zu; Warte-Schleifen prüfen `docker service ls \| grep running` (Spalten von `docker service ls` enthalten „running“ nicht) und suchen „Application Startup Complete“ (uvicorn schreibt „Application startup complete.“) | `DEP/swarm/community/swarm.sh` | nicht portieren (Deployment neu) |
| E-18 | `apps/api/run_tests.sh` verweist auf fehlendes `tests/run_tests.sh`; `AGENTS.md` verweist auf `apps/api/tests/TESTING_GUIDE.md` (liegt in `apps/api/plane/tests/`) | `apps/api/run_tests.sh`, `AGENTS.md` | – |
| E-19 | `feature-deployment.yml` baut `./aio/Dockerfile-app` (nicht vorhanden) | `.github/workflows/feature-deployment.yml` | nicht portieren |
| E-20 | CI führt keine Tests aus | `.github/workflows/*` | Zielsystem: Tests sind CI-Pflicht |
| E-21 | `install.sh`-Log-Menü ohne `live`/`admin` | `DEP/cli/community/install.sh` | – |
| E-22 | CLI-README behauptet Bucket-Policy „public read“; Code setzt keine | `DEP/cli/community/README.md`, `create_bucket.py` | privat + Presigned |
| E-23 | `POST /live/convert-document/` unauthentifiziert und öffentlich geroutet | `LIVE/controllers/document.controller.ts`, `apps/proxy/Caddyfile.ce` | im Zielsystem In-Process-Aufruf (kein HTTP-Endpunkt) oder internes Secret |
| E-24 | Proxy-Body-Limit = Dateilimit, Multipart-Overhead | `apps/proxy/Caddyfile.ce` | Gateway-Limit = Dateilimit + Puffer (z. B. +1 MiB) – bewusste Abweichung festhalten |
| E-25 | `django-celery-results` installiert, ungenutzt | `apps/api/pyproject.toml` | entfällt |
| E-26 | `apps/space/nginx/nginx.conf` ungenutzt | `apps/space/Dockerfile.space` | entfällt |
| E-27 | `register_instance` ruft `push_instance_metrics.delay()` → Broker-Abhängigkeit beim API-Start (Root-Compose: `api` hängt nicht von `plane-mq` ab) | `register_instance.py`, `docker-compose.yml` | entfällt (keine externe Telemetrie) |
| E-28 | `LIVE_SERVER_SECRET_KEY` Pflicht, aber ungenutzt | `LIVE/env.ts` | Shared Secret für interne Aufrufe Realtime ↔ API tatsächlich nutzen oder weglassen |
| E-29 | Space-SSR-Metadaten in Docker-Images funktionslos (relative URL in Node) | `apps/space/app/issues/[anchor]/layout.tsx` | Angular-SSR nur falls OG-Metadaten gewünscht; dann serverseitig korrekte interne API-URL |
| E-30 | `docs/linting.md` nennt `correctness = error`, Config sagt `warn` | `docs/linting.md`, `.oxlintrc.json` | – |
| E-31 | Celery-JSON-Formatstring beginnt mit `"` | `API/celery.py` | – |
| E-32 | `apps/api/Dockerfile.dev` nutzt Python 3.12.5, Produktion 3.12.12 | Dockerfiles | einheitliche SDK-Version (`global.json`) |
| E-33 | `docker-compose-local.yml` publiziert RabbitMQ-Port nicht; Worker/Beat laufen nur im Container | `docker-compose-local.yml` | Aspire startet alles lokal |
| E-34 | Turbo-`globalEnv` listet Sentry-Variablen ohne Code-Nutzung | `turbo.json` | entfällt |
| E-35 | `ADMIN_BASE_PATH`/`SPACE_BASE_PATH`: Settings-Default mit, Templates ohne abschließenden `/`; `base_host` normalisiert | `S/common.py`, `API/authentication/utils/host.py` | Normalisierung übernehmen |

---

## 4. Abhängigkeiten zu anderen Bereichen

| Bereich (Analyse-Dokument) | Nutzt aus A01 | A01 hängt ab von | Schnittstellen-Details |
|---|---|---|---|
| Datenmodell (A02a ff.) | DB-Konfiguration, Read-Replica-Router, `sessions`-Tabelle, `instances`/`instance_configurations`, `django_celery_beat`-Tabellen, `APIActivityLog`, Retention-Settings | Modelle `Instance`, `InstanceConfiguration`, `Session`, `APIActivityLog`, `WebhookLog`, `EmailNotificationLog`, `PageVersion`, `IssueDescriptionVersion`, `FileAsset` | 2.12, 2.16, 2.17.2 |
| Authentifizierung | Session-Middleware, Cookie-Namen/-Lebensdauer, Origin-Check, CSRF-Endpoint, `AuthenticationThrottle`, `EmailVerificationThrottle`, Redis für Magic-Codes, OAuth-ENV, `base_host`-Redirect-Logik | Auth-Views, Adapter, Fehlercodes (`AUTHENTICATION_ERROR_CODES`) | 2.13–2.16, 2.18 |
| God-Mode / Instanz-Administration | `GET/PATCH /api/instances/`, Instanz-Konfiguration (ENV-Seeding, Verschlüsselung), Admin-Cookie, Telemetrie-Flag, Changelog-URL | Admin-UI, `InstanceAdmin` | 2.11.2, 3.2, 3.8 |
| Assets / Dateien | `S3Storage`, `FILE_SIZE_LIMIT`, MIME-Listen, Proxy-Bucket-Route, `AssetRateThrottle`, Cleanup-Tasks | Asset-Endpunkte (`API/app/views/asset/v2.py`) | 2.19, 3.6 |
| Seiten / Editor / Realtime | Live-Server-Prozess, Redis-Pub/Sub, WS-URL-Konstruktion, `LIVE_URL` + `convert-document`, PDF-Export, Debounce | Pages-API (`…/pages/{id}/description/`), `@plane/editor` | 2.22, 3.7 |
| Webhooks | `WEBHOOK_ALLOWED_IPS/HOSTS`, `WEBHOOK_DISALLOWED_DOMAINS`, Celery-Retry von `webhook_send_task`, Log-Retention | Webhook-Modelle/Tasks | 2.11.1, 2.17 |
| Benachrichtigungen / E-Mail | SMTP-Konfiguration, Beat-Job alle 5 min mit Redis-Lock, E-Mail-Templates, Retention | Notification-Tasks | 2.11.2, 2.17, 2.18 |
| Export / Analytics | Celery-Tasks, Exporter-Ablauf-Job, S3 | Export-Endpunkte | 2.17.3 |
| Public REST API v1 | API-Key-Auth, `ApiKeyRateThrottle` + Header, API-Activity-Log, OpenAPI-Settings | v1-Views | 2.13, 2.14, 2.15, 2.20 |
| Space (öffentliche Boards) | Base-Path `/spaces`, SSR-Loader, Anon-Throttle | Space-Endpunkte `/api/public/` | 2.7, 3.3 |
| Intake / Automationen | Beat-Jobs `unsnooze_expired_intake_issues`, `archive_and_close_old_issues` | Fachlogik | 2.17.2 |
| Versionierung (Seiten/Beschreibungen) | Cleanup „max. 20 Versionen“ | Version-Tasks | 2.17.2 |
| UI / Design-System | `@makeplane/propel` 0.7.3, `packages/tailwind-config`, Fonts, Vite-Build, Base-Paths | – | 2.3, 2.4 |
| i18n | `packages/i18n` (22 Locales), CI-Sync-Check | – | 2.3, 2.24 |
| KI / Integrationen | LLM-/Unsplash-/Slack-/GitHub-App-Konfiguration | Fachlogik | 2.11.1, 2.11.2 |

---

## 5. Migrationshinweise für .NET / EF Core / Angular

### 5.1 Zielbild-Mapping (Original → Ziel)

| Original | Ziel (.NET 10 / Aspire / Angular) | Bemerkung |
|---|---|---|
| pnpm/Turbo-Monorepo (`apps/*`, `packages/*`) | Eine .NET-Solution (Projekte `Plane.AppHost`, `Plane.ServiceDefaults`, `Plane.Api`, `Plane.Worker`, `Plane.Realtime`, `Plane.Migrator`, `Plane.Gateway`, Shared-Libraries `Plane.Domain`, `Plane.Infrastructure`, `Plane.Contracts`) + ein Angular-Workspace mit Applikationen `web`, `admin`, `space` und Libraries entsprechend `packages/*` (`constants`, `types`, `i18n`, `services`, `shared-state`, `utils`, `hooks`→Directives/Services, `blocks`, `editor`, `tailwind-config`) | Paket-Grenzen 1:1 übernehmen erleichtert die Portierung „Datei für Datei“ |
| Django-API (`apps/api`, gunicorn/uvicorn) | `Plane.Api` (ASP.NET Core, Kestrel), EF Core 10 + Npgsql | JSON `snake_case` (System.Text.Json `JsonNamingPolicy.SnakeCaseLower`), Routen mit abschließendem `/` (ADR-003-Konsequenz) |
| Celery-Worker + Beat + RabbitMQ | `Plane.Worker` (Generic Host) mit persistenter Job-Queue und Cron-Scheduler; Kandidaten: Hangfire mit PostgreSQL-Storage, Quartz.NET (+ Postgres JobStore), MassTransit/Wolverine mit PostgreSQL-Transport; RabbitMQ optional über Aspire | Offener Punkt O-01; 13 Beat-Einträge (2.17.2) und 48 Task-Funktionen (`@shared_task`, 2.17.3) als Inventar |
| Valkey/Redis | Aspire-Ressource Redis/Valkey; `StackExchange.Redis` für Pub/Sub (Realtime-Fan-out, Admin-Kanal), `HybridCache`/`IDistributedCache` für Response-Cache, Redis-gestützte Rate-Limits, Magic-Codes | Alternativ PostgreSQL (`LISTEN/NOTIFY`, Tabellen) – O-03 |
| silo/MinIO (S3) | Aspire-Container-Ressource (MinIO-kompatibles Image), Zugriff per S3-SDK | Presigned-POST mit Policy-Bedingungen erforderlich (5.5 F-04) |
| Live-Server (Node, Hocuspocus) | `Plane.Realtime` (ASP.NET Core WebSockets + YDotNet, ADR-002), HTML↔Yjs-Konvertierung und PDF-Export in .NET | Protokollkompatibilität zum `@hocuspocus/provider` 2.15.2 im Browser (5.5 F-07) |
| Caddy-Proxy | `Plane.Gateway` (YARP) mit identischen Pfadregeln (2.8.1) + Auslieferung der drei Angular-Builds (Static Files + SPA-Fallback), optional vorgeschalteter Caddy/Ingress für ACME | Airgapped: TLS mit Betreiber-Zertifikat (Kestrel), ACME optional – O-02 |
| web/admin (React SPA, Caddy) | Angular-CSR-Apps; `base href` `/` bzw. `/god-mode/` | Runtime-Konfiguration (`/config.json` o. ä.) statt Build-Zeit-`VITE_*` empfohlen |
| space (React SSR, Node) | Angular-CSR unter `/spaces/`; OG-Metadaten für `/spaces/issues/{anchor}` serverseitig durch .NET (Index-HTML-Templating) | Angular-SSR würde Node zur Laufzeit erfordern (Widerspruch zu ADR-002-Konsequenz „Kein Node.js zur Laufzeit“) – O-04 |
| `manage.py migrate` (Migrator-Container) | `Plane.Migrator` (EF-Core-Migrations, als Aspire-Projekt mit `WaitForCompletion` vor API/Worker/Realtime) oder EF-Migration-Bundle | – |
| `register_instance`, `configure_instance`, `create_bucket`, `clear_cache` | Startup-Tasks im Migrator bzw. `IHostedService` | GitHub-Versionscheck und Telemetrie-Push entfallen/abschaltbar (ADR-004) |
| Django-Settings / ENV | Options-Pattern (`IOptions<T>` + `ValidateOnStart`), Konfigurationsquellen ENV/`appsettings.json`/Aspire-Parameter | Mapping 5.6 |
| Django DB-Sessions | Cookie-Authentifizierung mit serverseitigem `ITicketStore` in PostgreSQL (Sitzungsliste, `device_info`, Revocation) | Cookie-Namen `session-id`, `admin-session-id`; Laufzeiten 604 800 s / 3 600 s |
| Fernet-verschlüsselte Instanz-Konfiguration | ASP.NET Core Data Protection (Key-Ring persistiert in PostgreSQL, alle Dienste teilen ihn) | Greenfield (ADR-003): keine Kompatibilität zu Fernet nötig |
| DRF-Throttles | `Microsoft.AspNetCore.RateLimiting` mit verteiltem Store (Redis), Policies gemäß 2.15 | `X-RateLimit-Remaining`/`X-RateLimit-Reset` für `/api/v1/` beibehalten |
| drf-spectacular | `Microsoft.AspNetCore.OpenApi` (.NET 10) + offline gebündelte UI (Swagger UI oder Scalar), nur `/api/v1/`, per Option abschaltbar (Default aus) | – |
| Logging (python-json-logger, winston) | `Microsoft.Extensions.Logging` mit JSON-Console + OpenTelemetry (Aspire ServiceDefaults), Kategorien analog `plane.api.request`, `plane.worker`, `plane.exception`, … | Datei-Log mit Rotation optional |
| Scout APM, externe OTLP-Telemetrie | entfällt; OTel nur gegen lokal konfigurierten Collector/Aspire-Dashboard | ADR-004 |
| GitHub Actions (Build/Lint/Release) | CI für `dotnet build/test`, Angular `lint/test/build`, Playwright-Visual-Regression, Container-Build (amd64/arm64), SBOM/Scan | Tests verpflichtend (E-20) |
| pytest-/Vitest-Suites | xUnit (+ `WebApplicationFactory`, Testcontainers für PostgreSQL/pgvector, Redis, MinIO), Angular-Unit-Tests (Vitest/Jest + Testing Library), Playwright-E2E | API-Contract-Tests aus 2.25.1 als Akzeptanzkriterien |

### 5.2 Aspire-AppHost (Entwurf der Ressourcen und Abhängigkeiten)

| Ressource | Typ | Abhängigkeiten / Reihenfolge | Entspricht |
|---|---|---|---|
| `postgres` + Datenbank `plane` | PostgreSQL-Container mit pgvector (z. B. Image `pgvector/pgvector` in aktueller PG-Major), Volume | – | `plane-db` (PG 15.7, `max_connections=1000`) |
| `redis` | Redis/Valkey-Container, Volume | – | `plane-redis` |
| `objectstore` | MinIO-kompatibler Container (Ports 9000/9090), Bucket-Init | – | `plane-minio` |
| `mq` (optional) | RabbitMQ | – | `plane-mq` |
| `migrator` | .NET-Projekt | `WaitFor(postgres)`; führt EF-Migrationen, Instanz-Registrierung, Konfigurations-Seeding, Bucket-Anlage aus | `migrator` + Teile des API-Entrypoints |
| `api` | .NET-Projekt | `WaitForCompletion(migrator)`, Referenzen postgres/redis/objectstore(/mq) | `api` |
| `worker` | .NET-Projekt | `WaitForCompletion(migrator)` | `worker` + `beat-worker` (Scheduler-Leader-Wahl bei mehreren Instanzen beachten) |
| `realtime` | .NET-Projekt | `WaitFor(api)`, Redis | `live` |
| `gateway` | .NET-Projekt (YARP) | Referenzen api/realtime/objectstore; liefert Angular-Builds aus | `proxy` + web/admin/space-Container |
| `web`, `admin`, `space` (nur Entwicklung) | JavaScript-App-Ressourcen (Angular-Dev-Server) | – | `pnpm dev` |

Publikation: Aspire-Publisher für Docker Compose bzw. Kubernetes; für Airgapped alle Images in eine private Registry spiegeln; keine Laufzeit-Downloads (Fonts, Emoji-Daten, Swagger-UI gebündelt).

### 5.3 1:1 übertragbar (fachlich/vertraglich identisch halten)

1. **URL-Layout & Base-Paths:** `/` (web), `/god-mode/` (admin), `/spaces/` (space), `/live/` (Realtime, WS `/live/collaboration`), `/api/`, `/api/public/`, `/api/instances/`, `/api/v1/`, `/auth/`, Bucket-Pfad `/{bucket}`; Redirects `/spaces`→`/spaces/`, `/god-mode`→`/god-mode/` (2.8.1).
2. **Health-Endpunkte:** `GET /` → `{"status": "OK"}`; `GET /live/health/` → `{status, timestamp, version}`; `robots.txt`-Inhalt (2.14).
3. **Fehlerformate:** 413 `{"error": "REQUEST_BODY_TOO_LARGE", "detail": "…"}`; 404 `{"error": "Page not found."}`; 429 `{"error_code": 5900, "error_message": "RATE_LIMIT_EXCEEDED"}`; v1-Fehlertexte aus `API/api/views/base.py` (`"The payload is not valid"`, `"Please provide valid detail"`, `"The requested resource does not exist."`, `"The required key does not exist."`, `"Something went wrong please try again later"`).
4. **Header:** `X-Api-Key` (CORS-erlaubt), `X-RateLimit-Remaining`, `X-RateLimit-Reset`, Live-CORS-Header `Content-Type, Authorization, x-api-key`.
5. **Cookie-Namen, Laufzeiten, Secure-Ermittlung** (2.16) und **Origin-Check-Regeln** (2.14).
6. **Rate-Limit-Werte und -Schlüssel** (2.15).
7. **MIME-Listen** `ATTACHMENT_MIME_TYPES`, `INLINE_SAFE_MIME_TYPES` und Content-Disposition-Format (2.12, 2.19).
8. **Retention-Defaults:** Hard-Delete 60 Tage, API-Logs 14, Webhook-Logs 14, E-Mail-Logs 7, nicht hochgeladene Assets 7, Versionen max. 20 je Seite/Issue (2.17.2).
9. **Beat-Zeitplan** (UTC-Uhrzeiten, 5-Minuten-Jobs) (2.17.2).
10. **Instanz-Konfigurationsschlüssel** (36 Keys, Kategorien, Verschlüsselungs-Flag) und Response-Format von `GET /api/instances/` (2.11.2).
11. **API-Activity-Log-Felder** inkl. Redaktion und HMAC-Token-Identifier (2.13).
12. **Trailing-Slash-Konvention** (Client normalisiert, Server akzeptiert mit Slash).
13. **WS-URL-Konstruktion** und Query-Parameter (`documentType`, `projectId`, `workspaceSlug`) sowie Auth-Token `{id, cookie}` (2.22).
14. **ENV-Variablennamen** als Betreiber-Schnittstelle (empfohlen; Mapping 5.6), insbesondere `FILE_SIZE_LIMIT`, `WEB_URL`, `CORS_ALLOWED_ORIGINS`, `*_BASE_URL/_PATH`, Retention-Variablen, Webhook-Allowlists.

### 5.4 Neu zu bauen

1. Konfigurationsschicht (Options + Validierung + ENV-Aliasse), inkl. konsistenter Defaults für E-12/E-13.
2. Session-/Cookie-Infrastruktur mit DB-Ticket-Store und Pfad-Präfix-Regel für den Admin-Cookie.
3. Origin-Check-Middleware (ersetzt DRF-`enforce_csrf`) und CSRF-Token-Endpunkt für Formular-Flows (`GET /auth/get-csrf-token/`).
4. Middleware-Kette gemäß 2.13 (Body-Limit → 413, API-Key-Logging, Request-Logging ohne Health-Check, optionale Replica-Weiche).
5. Rate-Limiter-Policies (2.15) mit korrekter Client-IP-Ermittlung (`ForwardedHeadersOptions`, `KnownProxies`/`KnownNetworks`).
6. Job-System (Queue + Cron), Retry-Policy für Webhooks (5 Versuche, Backoff ab 600 s mit Jitter), verteilte Locks (Redis `SET NX EX 300`).
7. Storage-Service mit Presigned POST (Policy), Presigned GET (Disposition/Content-Type-Pinning), Head/Copy/Delete/Upload und Unterscheidung interner vs. öffentlicher Endpoint (statt Request-Host-Trick).
8. Realtime-Server (YDotNet) inkl. Redis-Fan-out, Admin-Kanal, Force-Close-Codes, Persistenz-Debounce, HTML→Yjs-Konvertierung (In-Process statt HTTP-Endpunkt).
9. Gateway (YARP) mit Pfadregeln, Body-Limit, WebSocket-Weiterleitung, Static-Hosting der Angular-Apps (SPA-Fallback `index.html` bzw. `/god-mode/index.html`), Security-Header (`X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`, `X-XSS-Protection: 1; mode=block`), Static-Rate-Limit 300/min.
10. Angular-Runtime-Konfiguration (ersetzt `process.env.VITE_*`), Base-Href je App.
11. Startup-Tasks (Instanz-Registrierung ohne Netzwerkzugriff, Seeding, Bucket).
12. Betriebs-Tooling: Install/Upgrade/Backup/Restore für die neue Plattform (Backup über `pg_dump` + Objektspeicher-Mirror statt Volume-Tarballs).
13. Test-Infrastruktur (Testcontainers-Stack analog `docker-compose-test.yml`) und CI mit Test-Pflicht.

### 5.5 Fallstricke

| Nr. | Fallstrick | Hinweis |
|---|---|---|
| F-01 | **Host-Header beim Proxy auf den Objektspeicher:** Presigned-Signaturen (SigV4) enthalten den Host. Caddy erhält den Host; YARP setzt standardmäßig den Ziel-Host. | YARP-Transform `RequestHeaderOriginalHost: true` für die Bucket-Route, oder Presigned-URLs direkt auf die öffentliche Objektspeicher-URL ausstellen |
| F-02 | Body-Limit gilt global (Proxy + Django `DATA_UPLOAD_MAX_MEMORY_SIZE`) | Kestrel `MaxRequestBodySize` pro Endpunkt; Multipart-Overhead (E-24) |
| F-03 | WebSocket-Proxying und Timeouts (Hocuspocus-Verbindungen sind langlebig) | YARP-WebSocket-Support, Idle-Timeouts großzügig |
| F-04 | Presigned **POST** mit `content-length-range` | Unterstützung im gewählten S3-SDK prüfen (Minio-.NET-SDK bietet Post-Policy; bei AWSSDK.S3 versionsabhängig) – sonst SigV4-POST-Policy selbst implementieren |
| F-05 | Build-Zeit-Konfiguration der Frontends | Angular `environment.ts` ist ebenfalls Build-Zeit → Runtime-`config.json` laden (APP_INITIALIZER) |
| F-06 | Angular-SSR benötigt Node | Space als CSR; OG-Meta per .NET (O-04) |
| F-07 | Hocuspocus-Protokoll ist nicht identisch mit purem y-websocket (Dokumentname-Präfix je Nachricht, Auth-/Stateless-/Close-Nachrichten) | Kompatibilitäts-Spike gegen `@hocuspocus/provider` 2.15.2 (ADR-002 verlangt Spike) |
| F-08 | Gemeinsamer Schlüssel für Verschlüsselung/Signaturen über alle Dienste (E-07/E-08) | Data-Protection-Key-Ring zentral |
| F-09 | Throttle-Identität hinter Proxies (E-11) | ForwardedHeaders strikt konfigurieren |
| F-10 | Cache-Clear beim Start leert gesamten Redis (inkl. laufender Magic-Codes) | Im Zielsystem nur eigene Cache-Präfixe invalidieren |
| F-11 | Zwei Beat-Einträge für denselben Job; Scheduler-Mehrfachstart bei Skalierung | Cron-Leader/Distributed-Lock |
| F-12 | DB-Verbindungen: Original erlaubt 1 000 Verbindungen; Npgsql-Pooling je Dienst | Pool-Größen und `max_connections` abstimmen |
| F-13 | Externe Defaults (Telemetrie an, GitHub-Check, Changelog-iframe, jsDelivr-Emoji) widersprechen ADR-004 | Default „aus“/gebündelt; 2.28 als Checkliste |
| F-14 | `X-Frame-Options: DENY` an Django **und** Caddy | iframe-Einbettungen (falls fachlich nötig) bewusst freischalten |
| F-15 | `APPEND_SLASH`-Semantik (Redirect bei fehlendem Slash) | ASP.NET-Routen mit und ohne Slash akzeptieren, keine 301 für POST |
| F-16 | Zeitzone UTC für Scheduler und Speicherung | `DateTimeOffset`/`timestamptz`, Cron in UTC |

### 5.6 ENV-Mapping (Vorschlag)

| Original | Ziel-Konfigurationsschlüssel (Vorschlag) | Bemerkung |
|---|---|---|
| `DATABASE_URL` / `POSTGRES_*` | `ConnectionStrings__plane` (Aspire) + Alias `DATABASE_URL` | URL→Npgsql-Connection-String-Konvertierung |
| `ENABLE_READ_REPLICA`, `DATABASE_READ_REPLICA_URL`, `POSTGRES_READ_REPLICA_*` | `Plane__Database__ReadReplica__Enabled`, `ConnectionStrings__plane-replica` | – |
| `REDIS_URL`, `REDIS_SSL_CERT_REQS`, `REDIS_SSL_CA_CERTS` | `ConnectionStrings__redis` (+ TLS-Optionen) | – |
| `AMQP_URL` / `RABBITMQ_*` | `ConnectionStrings__mq` (nur bei RabbitMQ-Variante) | O-01 |
| `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION`, `AWS_S3_ENDPOINT_URL`, `AWS_S3_BUCKET_NAME`, `USE_MINIO`, `MINIO_ENDPOINT_SSL`, `SIGNED_URL_EXPIRATION` | `Plane__Storage__{AccessKey, SecretKey, Region, InternalEndpoint, PublicEndpoint, Bucket, PresignExpirySeconds}` | `USE_MINIO`-Request-Host-Logik durch `PublicEndpoint` ersetzen |
| `FILE_SIZE_LIMIT` | `Plane__Uploads__MaxFileSizeBytes` (+ Alias) | auch Gateway-Limit |
| `SECRET_KEY` | Data-Protection-Key-Ring (kein String-Secret nötig) | – |
| `WEB_URL`, `APP_BASE_URL`, `ADMIN_BASE_URL/PATH`, `SPACE_BASE_URL/PATH`, `LIVE_BASE_URL/PATH` | `Plane__Urls__{Web, App, Admin, AdminPath, Space, SpacePath, Live, LivePath}` | gleichzeitig Quelle für Angular-Runtime-Config |
| `CORS_ALLOWED_ORIGINS` | `Plane__Cors__AllowedOrigins` | Default nur eigene Origins (E-10) |
| `ALLOWED_HOSTS` | `AllowedHosts` (ASP.NET) | – |
| `NUM_PROXIES`, `TRUSTED_PROXIES` | `Plane__ForwardedHeaders__{ForwardLimit, KnownNetworks}` | – |
| `API_KEY_RATE_LIMIT`, `AUTHENTICATION_RATE_LIMIT` | `Plane__RateLimits__{ApiKey, Authentication}` (Format `n/period` beibehalten) | weitere fixe Raten aus 2.15 als Defaults |
| `SESSION_COOKIE_AGE`, `SESSION_COOKIE_NAME`, `COOKIE_DOMAIN`, `SESSION_SAVE_EVERY_REQUEST`, `ADMIN_SESSION_COOKIE_AGE` | `Plane__Session__{LifetimeSeconds, CookieName, CookieDomain, Sliding, AdminLifetimeSeconds}` | – |
| `HARD_DELETE_AFTER_DAYS`, `API_ACTIVITY_LOG_RETENTION_DAYS`, `WEBHOOK_LOG_RETENTION_DAYS`, `EMAIL_LOG_RETENTION_DAYS`, `UNUPLOADED_ASSET_DELETE_DAYS` | `Plane__Retention__{HardDeleteDays, ApiActivityLogDays, WebhookLogDays, EmailLogDays, UnuploadedAssetDays}` | ungültig/negativ → Default (wie `_retention_days`) |
| `WEBHOOK_ALLOWED_IPS`, `WEBHOOK_ALLOWED_HOSTS`, `WEBHOOK_DISALLOWED_DOMAINS` | `Plane__Webhooks__{AllowedNetworks, AllowedHosts, DisallowedDomains}` | – |
| `ENABLE_DRF_SPECTACULAR` | `Plane__OpenApi__Enabled` | – |
| `SKIP_ENV_VAR` + Instanz-Keys | `Plane__InstanceConfig__Source` (`Database`/`Environment`) | E-06 |
| `INSTANCE_CHANGELOG_URL` | `Plane__Instance__ChangelogUrl` (Default leer, ADR-004) | – |
| `OTLP_*`, `METRICS_PUSH_INTERVAL_MINUTES`, `SERVICE_NAME` | entfällt (Standard-`OTEL_EXPORTER_OTLP_ENDPOINT` der ServiceDefaults) | – |
| `LIVE_SERVER_SECRET_KEY` | `Plane__Realtime__InternalSecret` (falls interne Aufrufe) | E-28 |
| `PORT`, `GUNICORN_WORKERS` | `ASPNETCORE_URLS`/`HTTP_PORTS`; entfällt | – |
| `VITE_*` | Angular-Runtime-Config aus `Plane__Urls__*` | – |

### 5.7 Bezug zu Bezahl-Editionen (Infrastruktur)

Im Repo sind keine Infrastruktur-Komponenten der Bezahl-Editionen enthalten. Indirekte Hinweise: Restore-Skript für „Plane Commercial Air-Gapped“ (Datenlayout `data/{db,redis,minio/uploads,mq}`), Hostname-Beispiel `silo` (Integrationsdienst), reservierte Workspace-Slugs `plane-pro`, `plane-ultimate`, `enterprise`, `plane-enterprise`, `silo`, `monitor`, `monitoring`, `ingest`, `disco`, `chat`, `calendar`, `drive`, `channels`, `upgrade`, `billing`, `license`, `licenses`, `pro`, `business`, `one` (`API/utils/constants.py`). Für das Zielsystem gilt ADR-001/ADR-004: Air-Gapped-Betrieb ist der Standardfall; Integrations-/KI-Dienste der Bezahl-Editionen werden (sofern in den Feature-Analysen identifiziert) als Module von `Plane.Worker`/`Plane.Api` bzw. mit pgvector in PostgreSQL abgebildet, nicht als zusätzliche Fremddienste.

### 5.8 Test- und CI-Migration

- Die 113 API-Testdateien (771 Tests) sind überwiegend **Sicherheits-Regressionstests** (GHSA-/WEB-/SECUR-/INFRA-Referenzen in den Docstrings, 2.25.1): Sie sind als Akzeptanzkriterien für die .NET-API zu übernehmen (gleiche Eingaben, gleiche Statuscodes/Antworten).
- Infrastruktur-spezifische Tests mit direktem Gegenstück im Zielsystem: `unit/settings/test_cookie_secure.py`, `test_num_proxies.py`, `test_retention.py`, `test_storage.py`, `test_storage_credentials.py`, `unit/utils/test_redis.py`, `unit/middleware/test_db_routing.py`, `test_logger.py`, `test_api_authentication.py`, `unit/views/test_session_origin_check.py`, `contract/app/test_session_origin_check_app.py`, `contract/app/test_static_asset_disposition_app.py`, `unit/bg_tasks/test_cleanup_task.py`, `test_url_security.py`, `test_ssrf_advisories.py`, `test_work_item_link_task.py`.
- `packages/blocks`-Tests (21 Dateien) beschreiben Interaktionsverhalten der UI-Bausteine und sind als Verhaltensspezifikation für die Angular-Komponenten zu nutzen; zusätzlich Visual-Regression gegen Referenz-Screenshots (ADR-005).
- Live-PDF-Tests (21) definieren den erwarteten Inhalt des .NET-PDF-Exports.
- CI-Gates des Originals, die fachlich übernommen werden sollten: Migrations-Drift-Check (`makemigrations --check` → EF `has-pending-model-changes`), Schutz bereits gemergter Migrationen, Versionsgleichheit Backend/Frontend, i18n-Sync-Check, Lizenz-Header-Check (AGPL-Header), Format/Lint/Typecheck.

---

## 6. Offene Punkte

| Nr. | Frage / Entscheidung | Kontext | Vorschlag |
|---|---|---|---|
| O-01 | Job-Queue: RabbitMQ beibehalten oder PostgreSQL-basierte Queue (Hangfire/Quartz/Wolverine/MassTransit-SQL)? | Original: Celery + RabbitMQ + DB-Beat (2.17) | PostgreSQL-basiert (eine Komponente weniger, Airgap-freundlich); RabbitMQ nur bei nachgewiesenem Durchsatzbedarf |
| O-02 | Edge-Proxy/TLS: YARP allein oder Caddy/Ingress vorgeschaltet? ACME im Airgap nicht verfügbar | 2.8, ADR-004 | YARP-Gateway als Pflichtbestandteil; TLS per Betreiber-Zertifikat; ACME optional über vorgeschalteten Proxy |
| O-03 | Redis/Valkey Pflicht oder optional (PostgreSQL `LISTEN/NOTIFY` für Realtime-Fan-out, DB-Cache)? | 2.18 | Redis beibehalten (Realtime-Skalierung, Rate-Limits); Single-Node-Betrieb ohne Redis als optionaler Modus |
| O-04 | Space: OG-Metadaten serverseitig erforderlich? (Angular-SSR = Node zur Laufzeit) | 3.3, E-29, F-06 | CSR + serverseitiges Index-Templating durch .NET für `/spaces/issues/{anchor}` |
| O-05 | ENV-Namen des Originals als Aliasse unterstützen? | 5.6 | Ja, für die in 5.3 Punkt 14 genannten Variablen |
| O-06 | Telemetrie/Update-Check komplett entfernen oder als abschaltbare Option (Default aus) behalten? | 3.8, 2.28 | Entfernen; Versionsanzeige nur lokal |
| O-07 | Changelog-iframe (`sites.plane.so`) – entfällt, eigene lokale Release-Notes oder konfigurierbare URL? | 2.28 | konfigurierbar, Default leer → Fallback-Ansicht (vorhandenes Verhalten) |
| O-08 | PDF-Engine in .NET (Lizenz/Airgap): QuestPDF (Community-Lizenz-Bedingungen), PdfSharp/MigraDoc, Headless-Chromium (Bundle-Größe) | ADR-002-Konsequenz, 2.22 | Lizenzprüfung durch Auftraggeber; Inhalt gemäß Live-PDF-Tests |
| O-09 | Client-seitiger PDF-Export der web-App (heute `@react-pdf/renderer`) – im Angular-Frontend clientseitig (Browser-JS-Bibliothek) oder serverseitig über den .NET-Export vereinheitlichen? | 2.22 | serverseitig vereinheitlichen (ein Renderer, testbar) |
| O-10 | Emoji-Daten offline (frimousse/Emojibase, jsDelivr-Default) und Callout-Default-Emoji-URL | 2.28 | Daten im Build bündeln, Default-URL lokal |
| O-11 | Deployment-Artefakte: Docker Compose + Helm/K8s (Aspire-Publisher) + AIO-Image beibehalten? Multi-Arch (amd64/arm64)? | 2.6, 2.24 | Compose + K8s-Manifeste aus Aspire; AIO optional; amd64+arm64 |
| O-12 | Betreiber-Tooling (Install/Upgrade/Backup/Restore) neu definieren (pg_dump statt Volume-Tar, Objektspeicher-Sync) | 2.26 | ja, als eigenes Arbeitspaket |
| O-13 | Admin-Cookie-Auswahl: Substring-Verhalten (E-09) bewusst korrigieren? | 3.4 | korrigieren (Präfix `/api/instances/`), als dokumentierte Abweichung |
| O-14 | Body-Limit am Gateway: exakt `FILE_SIZE_LIMIT` (Original) oder mit Multipart-Puffer (E-24)? | 3.6 | Puffer, dokumentierte Abweichung |
| O-15 | `POST /live/convert-document/`: öffentlich wie im Original oder intern? | E-23 | intern (In-Process), kein öffentlicher Endpunkt |
| O-16 | Defaults `ENABLE_SIGNUP`/`ENABLE_MAGIC_LINK_LOGIN` vereinheitlichen (E-12/E-13) | 2.11 | Seed-Werte (`ENABLE_SIGNUP=1`, `ENABLE_MAGIC_LINK_LOGIN=0`) als einzige Defaults |
| O-17 | Frimousse-Default-Datenquelle (jsDelivr) im Original verifizieren | 2.28 | Verhalten im laufenden Original prüfen (Netzwerk-Tab) |
| O-18 | Celery-Task-Registrierung über Django-Checks (2.17.3) – relevant nur für Verständnis, nicht für Port | 2.17.3 | – |
| O-19 | PostgreSQL-Zielversion (Original 15.7; pgvector benötigt) | 2.27 | aktuelle PG-Major mit pgvector-Image; Mindestversion festlegen |
