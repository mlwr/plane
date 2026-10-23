# -*- coding: utf-8 -*-
"""Arbeitspaket-Spezifikation der CE-Portierung (Eingabe fuer build.py).

Jedes Arbeitspaket (WP) ist ein dict mit den Schluesseln
  wp, title, phase, type, size, parallel, ce, deps, goal,
  be (Backend-Projekte/Ordner in funk.), fe (Frontend-Libs/Apps in funk.),
  arch (Architektur-Referenzen mit Abschnitt), ana (zusaetzliche Analyse-Referenzen),
  orig (zusaetzliche Original-Pfade), ak (spezifische Akzeptanzkriterien),
  tests (spezifischer Testumfang), ep (Andockstellen-Referenz, nur Typ X), note.
Analyse-Referenzen, Original-Pfade, Endpunkte und Pflicht-Testebenen der
enthaltenen CE-IDs ergaenzt build.py automatisch aus
  migration/features/_data/ce-features.json,
  migration/architecture/_data/15-ce-testmatrix.json,
  migration/architecture/_data/endpoints.json.
Zielbezeichner nach ADR-009C (Funk.*, @funk/*, Funk:).
"""

WPS = []


def W(wp, title, typ, size, parallel, ce, deps, goal, be=(), fe=(), arch=(), ana=(), orig=(),
      ak=(), tests=(), ep="", note=""):
    phase = wp.split("-")[1]
    WPS.append(dict(wp=wp, title=title, phase=phase, type=typ, size=size, parallel=parallel,
                    ce=list(ce), deps=list(deps), goal=goal, be=list(be), fe=list(fe),
                    arch=list(arch), ana=list(ana), orig=list(orig), ak=list(ak),
                    tests=list(tests), ep=ep, note=note))


def rng(prefix, a, b):
    return ["%s-%03d" % (prefix, i) for i in range(a, b + 1)]


# =====================================================================================
# I0 – Walking Skeleton
# =====================================================================================

W("WP-I0-101", "Repository funk. aufsetzen (Lizenz, Plan-Spiegel, AGENTS.md, Grundgerüst)", "I", "S", False,
  [], [],
  "Das Repository `github.com/mlwr/funk.` (Hauptbranch `develop`) erhält das verbindliche Grundgerüst: Solution-Datei, zentrale Build-Dateien, AGPL-Lizenz, NOTICE, Logo-Quelle, Plan-Spiegel und Agenten-Einstieg. Danach kann jeder weitere Agent ohne Rückfragen anfangen.",
  be=["`Funk.slnx`", "`global.json` (SDK-Pin 10.0.1xx, Aspire-SDK-Pin)", "`Directory.Build.props` (Nullable, TreatWarningsAsErrors, AGPL-Header-Check)", "`Directory.Build.targets` (`FunkInternalsVisibleTo`, R9)", "`Directory.Packages.props` (Central Package Management)", "`.editorconfig`, `.gitattributes`, `LICENSE` (AGPL-3.0), `NOTICE`", "`assets/funk_logo.svg`", "`docs/plan/` (Kopie von `migration/plan/`), `docs/migration/` (Kopie von `migration/architecture`, `migration/features`)", "`AGENTS.md`", "`.github/pull_request_template.md` (DoD-Checklisten 15 §3.15.3)", "`.github/CODEOWNERS`"],
  fe=["`frontend/package.json`, `frontend/pnpm-workspace.yaml` (leerer Catalog)"],
  arch=["00 ADR-006, ADR-009, ADR-009C", "01 §5.1 (Verzeichnisbaum)", "01 §6.1", "17 Umbenennungstabelle", "15 §3.15.3 (PR-Vorlage)", "plan/03-agenten-leitfaden.md §5"],
  orig=["`LICENSE.txt` (AGPL-3.0, Herkunftshinweis)", "`.github/pull_request_template.md`", "`.github/workflows/copyright-check.yml`"],
  ak=["`develop` ist Default-Branch mit Branch-Protection (Merge nur über PR mit grünem G1/G2); `main` bleibt unverändert (ADR-009).",
      "`AGENTS.md` verweist auf `docs/plan/03-agenten-leitfaden.md`, auf `mlwr/plane@funk-referenz-1.4.2` (nur lesend) und auf die Umbenennungstabelle (17).",
      "`docs/plan/` ist byte-gleich zu `migration/plan/` des Referenzstands; `docs/migration/features/_data/ce-features.json` liegt vor (Eingabe für `ce-coverage-check`).",
      "`LICENSE` = AGPL-3.0, `NOTICE` enthält den Herkunftshinweis auf Plane (Copyright Plane Software, Inc., AGPL-3.0) und ist durch das Lizenz-Gate fortschreibbar.",
      "`dotnet build Funk.slnx` läuft auf leerer Solution fehlerfrei; keine Datei enthält `Plane.`-Zielbezeichner (Ausnahme: Verweise auf das Original)."],
  tests=["L0: `tools/ci/license-header-check` auf das Grundgerüst angewendet (Vorstufe, Vollausbau WP-I0-106)."])

W("WP-I0-900", "Spike S0 – Toolchain & Walking-Skeleton-Gerüst", "S", "M", False,
  [], ["WP-I0-101"],
  "Nachweis, dass Aspire 13 (inkl. Keycloak-Hosting-Preview und JavaScript-Hosting), .NET 10, EF Core 10/Npgsql 10, Angular 22 und pnpm gemeinsam tragen; alle mit ⚠ markierten Versionen werden per Paket-Metadaten bestätigt und gepinnt. Der Spike gatet alle übrigen Arbeitspakete.",
  be=["`src/hosts/Funk.AppHost` (Prototyp)", "`Directory.Packages.props` (Pins aus 01 §8)", "`docs/spikes/S0-ergebnis.md`"],
  fe=["`frontend/pnpm-workspace.yaml` (Catalog-Pins)", "`frontend/libs/shared/{types,constants,utils,i18n}` (Quelltext-Kopie, TS-6-Kompilierprobe)"],
  arch=["01 §9 Zeile S0", "01 §8 (Library-Liste)", "02 §1.3 (Mediator, DbContext)", "17 Z-01, Z-02, Z-15, Z-106", "08 O-D08-01, O-D08-05, O-D08-06", "14 O-14-04, O-14-11"],
  orig=["`packages/types`, `packages/constants`, `packages/utils`, `packages/i18n` (Kompilierprobe)", "`pnpm-lock.yaml` (Original-Pins)"],
  ak=["`aspire run` startet alle I0-Ressourcen aus 14 §3.2 (Profil `dev`), Gateway liefert den Angular-Dev-Server same-origin.",
      "Alle ⚠-Versionen aus 01 §8 sind per NuGet-/npm-Metadaten bestätigt und in `Directory.Packages.props` bzw. `pnpm-workspace.yaml` gepinnt; Lizenz-Gate grün, Lizenzen in `NOTICE`.",
      "`libs/shared/{types,constants,utils,i18n}` kompilieren unter TypeScript 6.0 ohne Logikänderung; Liste der mechanischen Anpassungen in `docs/spikes/S0-ergebnis.md` (O-10).",
      "EF-10-Smoke-Test `PgvectorSmokeTests` (Pgvector.EntityFrameworkCore 0.3.x) und SignalR-Backplane-Smoke mit StackExchange.Redis 3.x grün (R-D03-01).",
      "Mediator 3: `internal`-Handler aus Modul-Assemblies werden über `InternalsVisibleTo` im Host registriert (Z-01, AK-24 aus 02) – sonst Fallback „Handler public“ (O-D02-09) dokumentiert und aktiviert.",
      "Signal-Forms-Probe (Create-Workspace-Formular mit `[plFormField]`, O-D08-01) und Vitest-`runnerConfig` (Z-02) funktionieren; Bundle-Budget des Original-Builds gemessen (O-D08-05).",
      "Abbruch-/Fallback-Entscheidung nach 01 §9 dokumentiert; Messungen als dauerhafte Tests im Repo (DoD Typ S)."],
  tests=["Messungen als automatisierte Tests: `AppHostSmokeTests`, `PgvectorSmokeTests`, `MediatorRegistrationTests`, `OptionalJsonSourceGenTests` (R-D02-08)."])

W("WP-I0-911", "Spike S11 – Paritäts-Harness (Original v1.4.2 starten, Seed, Record/Replay, Visual-Katalog)", "S", "M", True,
  [], ["WP-I0-101"],
  "Das Original v1.4.2 wird reproduzierbar gestartet und deterministisch geseedet; `Funk.Tools.ParityHarness` zeichnet Requests/Responses als Goldens auf und spielt sie gegen funk. ab. Das Werkzeug ist ab I0 Teil der Definition of Done aller Arbeitspakete.",
  be=["`src/tools/Funk.Tools.ParityHarness` (Kommandos `seed`, `record`, `replay`, `diff`, `keycloak-test-realm`)", "`tools/parity/{start-original.sh,compose.original.yml,original.env}`", "`tests/seed/parity-seed.yaml`, `tests/seed/original/seed_plane.py`", "`tests/contracts/{scenarios,golden}/`, `tests/contracts/deviations.yaml`", "`tests/Funk.Tools.ParityHarness.Tests`"],
  fe=["`frontend/apps/e2e/visual/catalog/` (5 Seiten des Originals)", "`frontend/apps/e2e/drivers/branding.ts` (Referenz-Branding BR-13)"],
  arch=["01 §9 Zeile S11", "15 §3.6 (Harness), §3.6.7 (I0-Umfang), §3.14.1 (Parity-Seed)", "09 §3.14.2 (Referenzumgebung)", "17 ABG-001, ABG-006"],
  orig=["`deployments/` (Compose-Vorlagen des Originals)", "`apps/api/plane/seeds/`", "`apps/api/plane/db/management/commands/`"],
  ak=["`tools/parity/start-original.sh` startet das Original mit per Digest gepinnten `makeplane/*`-Images hinter `http://localhost:13000`; `--from-source` für Visual-Aufnahmen; `ORIGINAL_SHA` = `053b2c0`.",
      "`Funk.Tools.ParityHarness seed` erzeugt auf Original und funk. denselben Datenstand (`manifest.original.json` = `manifest.funk.json`, geprüft durch `tools/ci/seed-manifest-diff`).",
      "Recorder zeichnet die 5 I0-Endpunkte (15 §3.6.7) auf; Replay gegen funk. mit Normalisierung (IDs, Zeitstempel, `deviations.yaml`) läuft in CI < 15 min.",
      "Playwright-Screenshot-Katalog für 5 Seiten des Originals (Sign-in, Create-Workspace, leere Workspace-Shell, Create-Project, God-Mode-General) liegt als Referenz vor.",
      "Fallback (Seeds über Original-API) nur, falls das Original nicht deterministisch seedbar ist; Ergebnisbericht `docs/spikes/S11-ergebnis.md`."],
  tests=["`Funk.Tools.ParityHarness.Tests` (Normalisierer, Diff-Regeln 15 §3.6.4), Determinismus-Check (zwei Seeds → gleiche Goldens)."])

W("WP-I0-102", "Aspire-AppHost und ServiceDefaults (Profile dev/test/prodlike)", "I", "M", True,
  ["CE-OPS-021"], ["WP-I0-900"],
  "Der AppHost startet die vollständige I0-Topologie (PostgreSQL mit Rollen/DBs funk, keycloak, forgejo; Keycloak; Mailpit; Api; Worker; Realtime; Gateway; Migrator; Angular-Dev-Server) in den Profilen dev, test und prodlike; ServiceDefaults liefern OpenTelemetry, Health, Resilience und Service Discovery.",
  be=["`src/hosts/Funk.AppHost`", "`src/hosts/Funk.ServiceDefaults`", "`deploy/postgres/init/10-roles-and-databases.sh`", "`tests/Funk.AppHost.Tests`"],
  arch=["14 §3.1 (Profile, Ports), §3.2 (AppHost vollständig), §3.6 (ServiceDefaults), §3.20 (lokale Entwicklung)", "01 §3.3/§3.4 (AppHost-Beispiel)", "17 ABG-012, ABG-018"],
  ak=["`aspire run` (Profil `dev`) bringt alle Ressourcen in < 3 min auf „healthy“; `Funk.AppHost.Tests` (Profil `test`) prüft Start, Health und Referenzen.",
      "Parameter (`keycloak-db-password`, `signing-key`, `forgejo-client-secret` …) werden generiert bzw. aus User-Secrets gelesen, nie im Klartext eingecheckt.",
      "Profil `prodlike` nutzt die Rolle `keycloak` mit eigenem Passwort (nicht den Superuser) und `keycloak-config`.",
      "Keine Ressource lädt zur Laufzeit etwas aus dem Internet nach (Netzwerk-Allowlist-Test ab I0, P6)."],
  tests=["L6: `Funk.AppHost.Tests` (Start/Health/Routing-Smoke).", "Compose-Drift-Check (`aspire publish` → `git diff --exit-code deploy/compose`)."])

W("WP-I0-104", "Backend-Fundament: BuildingBlocks, Funk.Data, Migrator, Modul-Schablone, Architekturtests", "I", "L", True,
  ["CE-OPS-019"], ["WP-I0-900"],
  "Alle Backend-Konventionen werden einmal gebaut: Ergebnis-/Fehlertypen (`FunkErrors`), JSON-Konventionen, Oberflächen (`App`, `Auth`, `Instance`, `Space`, `V1`, `Integrations`, `Root`), Trailing-Slash, Validierung mit DRF-Feldfehlern, Pagination-Contracts, Persistenz-Basisklassen mit Audit-/Soft-Delete-/Ownership-Interceptor, `FunkDbContext`, Migrator mit Extensions, Options-Klassen, Health, Request-Logging und die Modul-Schablone mit ArchUnit-Regeln R1–R12.",
  be=["`src/building-blocks/Funk.BuildingBlocks` (Ids/UUIDv7, `IClock`, Results, Pagination, Branding/`Brand.cs`)", "`src/building-blocks/Funk.BuildingBlocks.Web` (Oberflächen, JSON, ErrorMapping, ValidationFilter, TrailingSlash)", "`src/building-blocks/Funk.BuildingBlocks.Persistence` (Entity-Basis, Interceptors, Konventionen)", "`src/building-blocks/Funk.Analyzers` (FUNK0001…FUNK0006)", "`src/data/Funk.Data` (`FunkDbContext`, Migration `…_Platform_Extensions` mit `pg_trgm`, `unaccent`, `vector`)", "`src/hosts/Funk.Migrator`, `src/hosts/Funk.Hosting`, `src/hosts/Funk.Api`", "`tests/Funk.ArchitectureTests`, `tests/Funk.BuildingBlocks.Tests`, `tests/Funk.Migrator.Tests`", "`src/building-blocks/Funk.BuildingBlocks.Testing` (FunkApiFactory, PostgresContainerFixture, Respawn, FixedClock)"],
  arch=["02 §1.3, §3.1–§3.10, §3.14–§3.18, §5.1", "01 §5.2 (R1–R10), §5.3 (Modul-Schablone), §7.1–§7.16", "03 §3.1, §3.13, §5.1, §5.7", "16 D16-ADR-03 (R11/R12)", "14 §3.15 (Migrator)"],
  ana=["`analysis/01-gesamtarchitektur-infrastruktur.md` §2.11–§2.13", "`analysis/06-auth-sicherheit-querschnitt.md` §2.12 (Fehlertexte)"],
  orig=["`apps/api/plane/utils/` (Paginator, Exception-Handler)", "`apps/api/plane/app/views/base.py`", "`apps/api/plane/db/mixins.py`", "`apps/api/plane/settings/common.py`", "`apps/api/plane/middleware/`"],
  ak=["`Funk.ArchitectureTests` prüfen R1–R12 (01 §5.2, 16 D16-ADR-03) und schlagen bei einem absichtlich eingebauten Verstoß (Testfixture) fehl.",
      "Leere DB → `Funk.Migrator` legt Schema, Extensions und Referenz-Seeds idempotent an (zweiter Lauf ohne Änderung, `Funk.Migrator.Tests`); `dotnet ef migrations has-pending-model-changes` leer.",
      "JSON-Converter, Fehlerfabrik und Cursor-Codec erfüllen die Unit-Tests aus 02 §7.1 (Mikrosekunden-Zeitformat, `snake_case`, Optional<T>-PATCH).",
      "Jede Route trägt `.RequirePermission(...)` oder `.AllowAnonymous()` (Architekturtest); Routen akzeptieren Pfade mit und ohne abschließenden Slash ohne Redirect.",
      "Strukturiertes Request-Logging `funk.api.request` mit Redaktion (keine Secrets/PII), Health-Checks nicht geloggt (CE-OPS-019).",
      "Architekturtest `NamingTests`: kein Projekt, Namespace, Options-Schlüssel, Header, Metrik- oder Event-Name des Zielcodes beginnt mit `Plane`/`plane` (ADR-009C, plan/04 OP-PLAN-04); Verweise auf das Original in Kommentaren/Tests sind ausgenommen."],
  tests=["L0 Architekturtests (inkl. `NamingTests`), L1 BuildingBlocks (≥ 90 % Zeilen), L3 Migrator-Tests, Log-Redaktionstest."])

W("WP-I0-105", "Frontend-Fundament: Angular-Workspace, Shared-Libs, Routing-Kern, Wrapper, Runtime-Config", "F", "L", True,
  [], ["WP-I0-900"],
  "Der Angular-22-Workspace mit den Apps `web`, `admin`, `space`, `gallery`, `e2e` steht; `libs/shared/*` sind aus den Original-Paketen übernommen, Bootstrap, Interceptor-Kette, QueryCache, RouterStore, `AppRouter`, Wrapper (`AuthenticationWrapper`, `InstanceWrapper`, `StoreWrapper`, `WorkspaceAuthWrapper`), Runtime-Config, Inline-Theme-Script (hell/dunkel/system) und das Laden der Locales `de`/`en` sind fertig.",
  fe=["`frontend/angular.json`, `frontend/sheriff.config.ts`, `frontend/eslint.config.js`, `frontend/vitest.config.ts`", "`frontend/apps/{web,admin,space,gallery,e2e}`", "`frontend/libs/shared/{types,constants,utils,i18n,services,state-kit,runtime-config,cdk,theme}` (`@funk/*`)", "`frontend/libs/web/core` (RootStore, RouterStore, Wrapper, Interceptors)", "`frontend/tools/eslint-rules`, `frontend/tools/contract-check`, `frontend/tools/i18n-sync-check`"],
  arch=["08 §1.3 Spalte I0, §3.1–§3.5, §3.7, §3.8, §3.11, §3.14, §5.1–§5.9", "01 §6", "17 ABG-007, ABG-023, ABG-028"],
  ana=["`analysis/08-frontend-web-architektur.md` §2.2, §2.13", "`analysis/13b-shared-packages-i18n.md` §3"],
  orig=["`apps/web/app/root.tsx`, `apps/web/app/routes.ts`, `apps/web/app/provider.tsx`", "`apps/web/core/lib/wrappers/`", "`apps/web/core/store/router.store.ts`", "`packages/services/src/api.service.ts`", "`packages/i18n/src/`"],
  ak=["`pnpm build` baut web/admin/space; Sheriff-Grenzen (08 §3.1.5) und Lint-Regeln (`no-plan-identifiers`, `no-external-urls`) laufen in G1.",
      "Gleiches Build-Artefakt läuft unter anderen Base-URLs allein über `runtime-config.json` (E2E, 01 §7.12).",
      "Routen von `web` sind in Reihenfolge und Verschachtelung 1:1 zu `apps/web/app/routes.ts`; nur Routen abgenommener Schnitte sind registriert (01 §7.19); `route-contract.web.yaml` grün.",
      "Locales `de` (Standard) und `en` laden; Sprachauswahl ist auf diese zwei beschränkt (ADR-009D); Theme-Flash-Test (Inline-Script) grün.",
      "Contract-Check `openapi-typescript`-Typen ↔ `libs/shared/types` läuft in G1."],
  tests=["L0 Sheriff/ESLint/i18n-Sync/Contract-Check, L2 Stores/Interceptors (Vitest), Routing-Contract-Test (08 §7.2)."])

W("WP-I0-106", "Test- und CI-Infrastruktur: Gates G0–G3, Lizenz-Gate, G-BRAND, Coverage- und Ledger-Werkzeuge", "I", "L", True,
  ["CE-OPS-022", "CE-OPS-023"], ["WP-I0-101", "WP-I0-900"],
  "Die Quality-Gates sind lokal und in CI identisch ausführbar (`./tools/ci/gate.sh g0…g3`), der isolierte Test-Stack (Aspire-Profil `test`) und die GitHub-Actions-Workflows laufen auf `develop`. `ce-coverage-check`, `original-test-ledger`, `brand-gate`, `license-gate`, gitleaks und Trivy sind aktiv.",
  be=["`tools/ci/{gate.sh,ce-coverage-check,original-test-ledger,brand-gate,license-gate,license-header-check,seed-manifest-diff,acceptance-report,assert-no-node.sh}`", "`.github/workflows/{ci.yml,images.yml,nightly.yml,check-version.yml}`", "`tests/ce-matrix.yaml` (aus 15 Anhang B)", "`tests/original-tests/ledger.yaml` (1 092 Einträge)", "`tests/extension-points.yaml`", "`tests/Funk.Tools.Gates.Tests`"],
  fe=["`frontend/apps/e2e/` (Playwright-Gerüst Dual-Target, `AuthDriver` beider Targets)", "`frontend/tools/brand/allowlist.json`", "axe-Baseline-Mechanik"],
  arch=["15 §3.1, §3.2, §3.4, §3.15, §3.16 Zeile I0", "14 §3.21 (CI/CD)", "17 Z-10 (nur Chromium), ABG-149"],
  orig=["`.github/workflows/` (Original-CI als Vorlage)"],
  ak=["`./tools/ci/gate.sh g1` lokal und in CI identisch; G1 < 15 min, G2 < 40 min (15 §3.15.1).",
      "Workflows triggern auf `pull_request`/`merge_group` gegen `develop` und `push` auf `develop` (nicht `main`, ADR-009; Korrektur von 14 §3.21.1, siehe plan/04 OP-PLAN-02).",
      "`ce-coverage-check --structure` erkennt alle 507 CE-IDs, `entfällt`-IDs ohne Tests; `original-test-ledger` hat alle 1 092 Einträge mit Statusvorschlag.",
      "G-BRAND schlägt bei einem eingebauten „Plane“-String in einem Bundle fehl und ist mit leerer Allowlist grün.",
      "Visual-Gate läuft ausschließlich mit Chromium (Z-10); Firefox/WebKit sind nicht Teil der CI-Matrix."],
  tests=["`Funk.Tools.Gates.Tests` (Selbsttests der Gate-Werkzeuge), Probe-PR mit absichtlichen Verstößen je Gate."])

W("WP-I0-103", "Gateway Funk.Gateway: Routen, statische Auslieferung, Base-URLs, Health, robots.txt, 413", "I", "M", True,
  ["CE-OPS-006", "CE-OPS-007", "CE-OPS-008", "CE-OPS-009"], ["WP-I0-102", "WP-I0-104"],
  "Das YARP-Gateway bildet die Pfadregeln des Original-Caddy 1:1 ab (Routen G-01…G-17 ohne OG-Meta und Uploads), liefert die Angular-Builds statisch aus, stellt `runtime-config.json` bereit, setzt die Security-Header und beantwortet zu große Uploads mit dem Original-413-Body.",
  be=["`src/hosts/Funk.Gateway` (Routen, `StaticFrontendMiddleware`, `RuntimeConfigEndpoint`)", "`tests/Funk.Gateway.Tests`"],
  arch=["14 §3.7 (Routing-Tabelle, Header, Rate-Limit), §3.5", "05 §3.17.7 (Header-Werte)", "01 §7.12", "17 ABG-015, ABG-016"],
  ana=["`analysis/01-gesamtarchitektur-infrastruktur.md` §2.8.1–§2.8.3"],
  orig=["`apps/proxy/Caddyfile.ce`"],
  ak=["`Funk.Gateway.Tests` prüft jede Pfadregel aus A01 §2.8.1 (Priorität, Rewrites, Redirects) gegen eine Tabelle der Original-Caddy-Regeln.",
      "Security-Header je Oberfläche wie 05 §3.17.7 (Space ohne `X-Frame-Options` für Boards); CSP im Report-Only-Modus.",
      "Upload > `Funk:Uploads:MaxFileSizeBytes` → 413 mit Original-Body; `/robots.txt` und Health-Pfade wie Original."],
  tests=["L6 `Funk.Gateway.Tests`, E2E `ops/deployment-smoke.spec.ts`."])

W("WP-I0-107", "Realtime-Host-Gerüst Funk.Realtime (Health, Origin-Prüfung, /live-Fallback)", "I", "S", True,
  ["CE-RT-009"], ["WP-I0-103", "WP-I0-104"],
  "Der Host `Funk.Realtime` mit `RealtimeComposition` läuft: Health `/live/health/` auf dem App-Port, `/health/*` auf dem Management-Port, `WebSocketOriginValidator`, `SessionTicketReader`, Fallback `/live/{**}` → 404 `{\"message\":\"Not Found\"}`, Gateway-Routen G-06/G-07.",
  be=["`src/hosts/Funk.Realtime`", "`src/hosts/Funk.Hosting/RealtimeComposition.cs`", "`tests/Funk.Collaboration.Tests` (Smoke-Teil)"],
  arch=["07 §1.4 Zeile I0, §3.2", "05 §3.11", "14 §3.7.1 (G-06, G-07)"],
  orig=["`apps/live/src/server.ts`", "`apps/live/src/controllers/health.controller.ts`"],
  ak=["`GET /live/health/` liefert den Original-Body (Golden), unbekannte `/live/…`-Pfade 404 mit `{\"message\":\"Not Found\"}`.",
      "WebSocket-Upgrade mit fremdem `Origin` wird abgewiesen (AK-07-01/-02)."],
  tests=["L6 `RealtimeSmokeTests` (Host-Teil)."])

W("WP-I0-108", "Keycloak-Realm als Code (dev/test/prod) inkl. Nachweis entfallener Auth-Funktionen", "V", "M", True,
  ["CE-AUTH-002", "CE-AUTH-003", "CE-AUTH-004", "CE-AUTH-005", "CE-AUTH-006", "CE-AUTH-007", "CE-AUTH-008", "CE-AUTH-009", "CE-AUTH-010", "CE-AUTH-011", "CE-AUTH-013", "CE-AUTH-017", "CE-AUTH-018", "CE-AUTH-019", "CE-AUTH-020", "CE-AUTH-021", "CE-PROF-007"],
  ["WP-I0-102", "WP-I0-907"],
  "Realm `funk` (Clients `funk-web`, `funk-admin`, `funk-space`, `funk-backend`, `funk-forgejo`, Rolle `funk-instance-admin`, Flow `funk-browser`, Client-Scopes und Mapper inkl. `groups`, sieben Testbenutzer mit deterministischen IDs) liegt als Code vor: dev-Realm, generierter Test-Realm und Prod-Templates für keycloak-config-cli; Image `funk-keycloak`. Die durch ADR-008 entfallenen Funktionen (Registrierung, Passwort, Magic-Code, OAuth-Provider, Steuerung der Auth-Methoden, verknüpfte Konten) sind als „entfällt“ mit Ersatznachweis `KeycloakRealmConfigTests` belegt.",
  be=["`deploy/keycloak/realms/funk-realm.json` (dev)", "`deploy/keycloak/realms/funk-realm.test.json` (generiert über `Funk.Tools.ParityHarness keycloak-test-realm`, ABG-001)", "`deploy/keycloak/config/{00-funk-realm,10-funk-bootstrap-admin,20-forgejo-client}.json`", "Image `funk-keycloak` (Basis `quay.io/keycloak/keycloak:26.x`, `kc.sh build`)", "`tests/seed/keycloak/{test-overrides,parity-users}.json`", "`tests/modules/Funk.Identity.Tests/Keycloak/KeycloakRealmConfigTests.cs`"],
  arch=["05 §3.15 (Realm als Code), §4.1 (CE-IDs → neues Verhalten)", "14 §3.3.1–§3.3.3", "15 §3.14.2", "17 ABG-001, ABG-002, ABG-003, Umbenennungstabelle", "01 O-06 (Client je App)"],
  ak=["`KeycloakRealmConfigTests`: Registrierung aus, Passwort-Richtlinie/OTP/WebAuthn gemäß 05 §3.15, keine Social-Provider, Redirect-URIs je Client exakt, Back-Channel-Logout-URL gesetzt; `TestRealm_IsUpToDate` (`--check`) grün.",
      "Härtungsprüfungen des Prod-Templates (D15-SEC-11) laufen gegen `deploy/keycloak/config/00-funk-realm.json`.",
      "Für jede enthaltene „entfällt“-CE-ID ist der Ersatztest in `tests/ce-matrix.yaml` eingetragen; `ce-coverage-check` meldet keine Tests für diese IDs (Status entfällt)."],
  tests=["L3 `KeycloakRealmConfigTests`, G-BRAND über den Realm-Export."])

W("WP-I0-109", "Keycloak-Login-Themes funk und funk-space (1:1-Optik der Sign-in-Seite, funk.-Branding)", "V", "L", True,
  ["CE-AUTH-015"], ["WP-I0-108", "WP-I0-006", "WP-I0-106", "WP-I0-911"],
  "Die Login-Themes `funk` (Web/God Mode) und `funk-space` bilden die Original-Sign-in-Seiten von `apps/web` und `apps/space` pixelgleich nach (eigenes `template.ftl` ohne PatternFly, Original-Klassen und -CSS), mit funk.-Logo und -Texten (BR-09), AGB-/Datenschutz-Hinweis und Auth-Fuß (CE-AUTH-015) sowie der Hell/Dunkel-Übernahme aus funk. (Z-08).",
  be=["`deploy/keycloak/themes/{funk,funk-space}` (`.ftl`, `messages_{de,en}.properties`, `theme.properties`, Ressourcen)"],
  fe=["`frontend/apps/e2e/visual/` Suite `keycloak-login`", "`frontend/tools/brand/render-brand-assets.mjs` (Theme-Logo)"],
  arch=["05 §3.16", "14 §3.3.4", "09 §3.13", "17 ABG-148, Z-08"],
  orig=["`apps/web/app/(all)/(home)/page.tsx`", "`apps/web/core/components/account/auth-forms/`", "`apps/space/app/page.tsx`"],
  ak=["Visual-Diff ≤ 1 % gegen die Original-Sign-in-Seite (web und space, hell/dunkel; Referenzen mit vorab ersetztem Branding, BR-13).",
      "Theme übernimmt `localStorage.theme` (same-origin `/idp`), Fallback `prefers-color-scheme` (Z-08); Texte nur `de`/`en` (ADR-009D).",
      "Abweichungen DEV-UI-01…-03 (kein Einladungskopf, Keycloak-URL, keine Sign-up-/Code-/OAuth-Links) in `ui-deviations.yaml` mit Entscheidungsverweis."],
  tests=["L8 Visual `keycloak-login` (Chromium), G-BRAND über das Theme."])

W("WP-I0-006", "Designsystem-Fundament: CSS-Pipeline, Schriften, Icons, erste Propel-Primitive, Toast, Galerie", "F", "L", True,
  ["CE-I18N-011", "CE-I18N-012", "CE-I18N-013", "CE-I18N-021", "CE-I18N-023", "CE-I18N-024", "CE-I18N-025", "CE-I18N-026"],
  ["WP-I0-105", "WP-I0-910", "WP-I0-106"],
  "Tailwind-4.1-Konfiguration und CSS werden 1:1 übernommen (Vendoring, Import-Reihenfolge, `@source`-Scan), Schriften und Icons gebündelt (Airgap), die ersten Propel-Primitive (Button, Input, Menu, Tooltip, Avatar) sowie Toast, Spinner/Lade-Indikatoren, Animationen, Maßsystem und Avatare/Farbwähler stehen DOM- und pixelgleich in der Galerie; die Brand-Assets werden aus `assets/funk_logo.svg` erzeugt.",
  fe=["`frontend/libs/shared/tailwind-config`", "`frontend/libs/shared/propel` (button, input, menu, tooltip, avatar, toast, spinner, headless/portal, floating)", "`frontend/libs/shared/icons-lucide` (generiert)", "`frontend/tools/propel-port/{fetch-propel,vendor-css,extract-classes,port-variants,port-icons.mjs}`", "`frontend/tools/visual/{css-diff.ts,capture-reference.ts}`", "`frontend/tools/reference-gallery`", "`frontend/apps/gallery`", "`frontend/tools/brand/{render-brand-assets.mjs,brand-i18n.mjs}`"],
  arch=["09 §1.4 Zeile I0, §3.1–§3.10, §4.1–§4.6, §4.11, §5.1–§5.8", "01 §7.17", "17 ABG-026, ABG-027, ABG-148", "15 §3.10"],
  ak=["CSS-Diff-Test (G-CSS) der Shell-Selektoren gegen das Original-CSS ohne ungenehmigte Abweichung (09 §3.2.5).",
      "Galerie: Button/Input/Menu/Tooltip/Avatar/Toast in allen Varianten DOM-gleich zur Referenz-Galerie und Visual ≤ 0,1 % (hell/dunkel/High-Contrast, Chromium).",
      "Keine Schrift, kein Icon und kein Emoji wird zur Laufzeit von einem CDN geladen (Netzwerk-Allowlist-Test).",
      "Favicons, App-Icons und Logos sind aus `assets/funk_logo.svg` in Original-Größe/-Dateiname erzeugt (BR-06); G-BRAND grün."],
  tests=["L8 Galerie-Visual + DOM-Verträge (`visual/dom-contracts/gallery/**`), L2 Komponenten-Verhalten (Tastatur, Fokus, ARIA), G-CSS."])

W("WP-I0-001", "Schnitt 1: Anmeldung über Keycloak → JIT-Benutzer → Landing/leere Shell", "V", "L", False,
  ["CE-AUTH-001", "CE-AUTH-012", "CE-AUTH-014", "CE-AUTH-016", "CE-AUTH-022", "CE-AUTH-023", "CE-AUTH-024", "CE-AUTH-025", "CE-AUTH-027", "CE-AUTH-029"],
  ["WP-I0-103", "WP-I0-105", "WP-I0-108", "WP-I0-203", "WP-I0-204", "WP-I0-106", "WP-I0-911"],
  "Ein Testbenutzer meldet sich per Authorization Code + PKCE über das BFF an; funk. legt beim ersten Login den Benutzer aus den Claims an (nur bei `email_verified`), setzt die HttpOnly-Session `funk-session`, beantwortet `GET /api/users/me/` und leitet nach `next_path` bzw. zur Workspace-Anlage weiter. Abmelden (RP-initiated + Back-Channel), Session-Ablauf, Sperre deaktivierter Konten und Auth-Fehlerbanner verhalten sich wie in 05 festgelegt.",
  be=["`src/modules/Identity/Funk.Identity` (OIDC-Schemata `oidc-web`/`oidc-admin`/`oidc-space`, `OidcBffEndpoints`, `PostgresTicketStore`, `SessionRevalidator`, `BackChannelLogoutEndpoint`)", "`src/modules/Identity/Funk.Identity.Contracts`", "`src/data/Funk.Data/Entities/Identity/` (`users`, `user_identities`, `user_sessions`)", "`tests/modules/Funk.Identity.Tests`"],
  fe=["`frontend/libs/web/auth` (Landing, Sign-out, Fehlerbanner)", "`frontend/libs/web/core/wrappers/authentication-wrapper.component.ts`", "`frontend/apps/web/src/pages/(all)/…` (Sign-in-Einstieg)"],
  arch=["05 §3.2–§3.7, §3.10, §4.1–§4.3, §5.1–§5.6, §5.10", "04 §4.1", "03 §3.4.1", "08 §3.3.4, §5.6", "17 ABG-020, ABG-021, Z-03 (max_age)"],
  ak=["`OidcLoginFlowTests` (L6) für web: Login mit PKCE, Cookie `funk-session` HttpOnly/SameSite, RP-Logout, Back-Channel-Logout beendet die Session < 2 s, Sperre in Keycloak verhindert den nächsten Request.",
      "JIT legt den Benutzer mit `sub`-Verknüpfung an und verweigert `email_verified=false` mit Fehlercode-Banner (CE-AUTH-014, neue Codes aus 05 §4.3).",
      "`next_path`-Validierung 1:1 zu `path_validator.py` (Same-Origin-Pfad inkl. Query, kein Schema/Host).",
      "E2E `web/auth/keycloak-login.spec.ts` grün gegen Original (Sign-in-Flow des Originals) und funk. (Keycloak-Flow) mit den Pflichtszenarien 15 §3.9.3."],
  tests=["L3 Identity (Provisionierung, Ticket-Store, Revalidierung), L6 `OidcLoginFlowTests`, L7 `keycloak-login.spec.ts`, L5 Contract für `/api/users/me/`, `/auth/get-csrf-token/`."])

W("WP-I0-002", "Schnitt 2: Workspace anlegen (Formular, Slug-Prüfung, Admin-Mitgliedschaft)", "V", "M", False,
  ["CE-WS-001"],
  ["WP-I0-001", "WP-I0-201", "WP-I0-202", "WP-I0-203"],
  "`/create-workspace` legt mit Name, Slug (Regex, Länge, reservierte Slugs, global eindeutig, 409) und Organisationsgröße einen Workspace mit Admin-Mitgliedschaft (Rolle 20) an und schreibt das erste produktive Integration-Event `funk.workspace.created.v1`. Der Demo-Seed folgt schrittweise und wird in WP-I4-009 abgenommen.",
  be=["`src/modules/Workspaces/Funk.Workspaces` (`CreateWorkspaceCommand`, `WorkspaceAvailabilityQuery`)", "`src/data/Funk.Data/Entities/Workspaces/`", "`tests/modules/Funk.Workspaces.Tests`"],
  fe=["`frontend/libs/web/workspace` (create-workspace-form)", "`frontend/apps/web/src/pages/(all)/create-workspace/`"],
  arch=["04 §4.3", "03 §3.4.3", "02 §3.5.3 (Slug-Regeln), §3.7", "06 §3.8 (Event-Katalog)"],
  ak=["Slug-Validierung (Regex `^[a-zA-Z0-9_-]+$`, max. 48, reservierte Slugs inkl. `RESTRICTED_URLS`) liefert dieselben Feldfehler wie das Original (Contract-Golden).",
      "`DISABLE_WORKSPACE_CREATION` (Instanz-Konfiguration) blendet den Original-Hinweis ein.",
      "Outbox enthält genau ein `funk.workspace.created.v1` je Anlage (Event-Katalog-Snapshot)."],
  tests=["L3 Workspaces (E1–E8), L5 Contract `POST /api/workspaces/`, `GET /api/workspace-slug-check/`, L7 `create-workspace.spec.ts` (Abschnitt Anlage), L8 Visual Create-Workspace."])

W("WP-I0-003", "Instanz-Bootstrap: Konfiguration, Instanz-Info, Erst-Einrichtung, God-Mode-Einstieg (inkl. Nachweis entfallener Admin-Logins)", "V", "M", True,
  ["CE-INST-001", "CE-INST-002", "CE-INST-003", "CE-INST-004", "CE-INST-005", "CE-INST-006", "CE-INST-007", "CE-INST-020", "CE-INST-021", "CE-INST-022", "CE-INST-023", "CE-INST-024"],
  ["WP-I0-001", "WP-I0-208"],
  "Instanz-Konfiguration aus ENV und DB (verschlüsselte Keys, 14 Keys), `GET /api/instances/` mit festen Werten der entfallenen Login-Flags, Instanz-Zustände in der Web-App, Erst-Einrichtung ohne Admin-Konto und der God-Mode-Einstieg über die Keycloak-Rolle `funk-instance-admin` (`NO_ADMIN_ROLE`, Seite `general` lauffähig, ABG-024). Admin-Login und Provider-Konfiguration entfallen (ADR-008) und sind mit `OidcLoginFlowTests.InstanceAdminRole_GrantsGodMode` belegt.",
  be=["`src/modules/Instance/Funk.Instance` (`InstanceConfigurationStore`, `InstanceBootstrap`)", "`src/modules/Instance/Funk.Instance.Contracts`", "`src/hosts/Funk.Migrator` (InstanceBootstrap-Schritt)", "`tests/modules/Funk.Instance.Tests`"],
  fe=["`frontend/libs/admin/core`, `frontend/libs/admin/instance`", "`frontend/apps/admin/src/pages/` (Einstieg, Setup, `general`)", "`frontend/libs/admin/extensions` (Gerüst `ADMIN_SETTINGS_PAGES`)"],
  arch=["05 §3.8, §3.9, §4.4", "02 §3.16", "04 §4.2", "03 §3.4.2", "08 §4.2", "17 ABG-024, ABG-143"],
  ak=["`GET /api/instances/` entspricht dem Original-Golden bis auf die dokumentierten `config`-Abweichungen (DEV-API-02).",
      "Instanz-Admin ergibt sich ausschließlich aus der Rolle `funk-instance-admin`; ein Benutzer ohne Rolle sieht `NO_ADMIN_ROLE` (Visual wie Original-Fehlerseite).",
      "Erst-Einrichtung ohne Passwortfelder (DEV-UI-06); `admin/instance-setup.spec.ts` Abschnitt `@I0` grün.",
      "Instanz-Secrets werden im God Mode maskiert (`MaskInstanceSecrets = true`, Z-112)."],
  tests=["L3 Instance, L5 Contract `/api/instances/`, L6 `InstanceAdminRole_GrantsGodMode`, L7 `admin/instance-setup.spec.ts` (`@I0`)."])

W("WP-I0-004", "Schnitt: Workspace-Shell 1:1 (Top-Navigation, Sidebar, Header, Workspace-Switcher, User-Menü)", "V", "L", False,
  ["CE-WS-005", "CE-WS-013", "CE-WS-016", "CE-WS-018", "CE-WS-019", "CE-WS-020"],
  ["WP-I0-002", "WP-I0-006", "WP-I0-208"],
  "Die Workspace-Shell (App-Rail/Top-Navigation, resizable Sidebar mit Peek, Sidebar-Kopf mit Quick-Action, Menüeinträge, Workspace-Switcher mit Liste, User-Menü) ist pixel- und DOM-gleich zum Original; nur Einträge abgenommener Funktionen sind sichtbar (01 §7.19).",
  fe=["`frontend/libs/web/core/{sidebar,navigation,breadcrumbs}`", "`frontend/libs/web/workspace` (Switcher)", "`frontend/libs/web/extensions` (`SIDEBAR_ITEMS` statisch)"],
  be=["`src/modules/Workspaces/Funk.Workspaces` (`GET /api/users/me/workspaces/`, Sidebar-Präferenzen)"],
  arch=["08 §4.4, §3.9", "09 §4.14 (Screenshot-Katalog Shell)", "16 §1.4 Zeile I0 (`SIDEBAR_ITEMS`, `APP_RAIL_ENABLED`)"],
  ak=["Visual-Prüfpunkte der Shell (hell/dunkel, Sidebar ein-/ausgeklappt, Peek) ≤ 0,2 % Pixelabweichung (15 §3.10.3), DOM-Snapshot gleich.",
      "Sidebar-Breite wird wie im Original in `localStorage` gehalten; Tastaturbedienung (Tab-Reihenfolge, Escape) wie Original."],
  tests=["L2 Sidebar-/Switcher-Komponenten, L7 `workspace-shell.spec.ts` (Grundzustand), L8 Visual Shell."])

W("WP-I0-005", "Schnitt 3: Projekt anlegen (Identifier-Prüfung, Default-States, Mitgliedschaft)", "V", "M", False,
  ["CE-PRJ-004", "CE-PRJ-005"],
  ["WP-I0-002", "WP-I0-006", "WP-I0-913"],
  "Das Create-Project-Modal legt ein Projekt mit Identifier-Prüfung (max. 12 Zeichen, Freigabe), Default-States und Admin-Mitgliedschaft an und schreibt `funk.project.created.v1`.",
  be=["`src/modules/Projects/Funk.Projects` (`CreateProjectCommand`, Identifier-Endpunkte)", "`src/data/Funk.Data/Entities/Projects/`", "`tests/modules/Funk.Projects.Tests`"],
  fe=["`frontend/libs/web/project` (create-project-modal)"],
  arch=["04 §4.4", "03 §3.4.4", "02 §5.2 (Referenzmodul-Muster)"],
  ak=["Identifier-Konflikt und -Freigabe liefern dieselben Codes/Texte wie das Original (Contract-Golden).",
      "Default-States werden in Original-Reihenfolge und -Farben angelegt (Golden).",
      "Die neuen Tabellen mit `workspace_id` und `project_id` (`states`, `project_members`, `project_identifiers`) tragen den zusammengesetzten Scope-FK `fk_<tabelle>_project_scope (project_id, workspace_id) → projects (id, workspace_id)` nach der in WP-I0-913 bestätigten Konvention (03 D03-ADR-05, Schema-Konformitätstest); ein Insert mit `project_id` aus einem fremden Workspace scheitert in der DB."],
  tests=["L3 Projects (Anlage), L5 Contract `POST {W}/projects/`, Identifier-Endpunkte, L7 `create-project.spec.ts`, L8 Visual Create-Project-Modal."])

# --- Erweiterungspunkte I0 (Typ X) -----------------------------------------------------

W("WP-I0-201", "Erweiterungspunkt C3: Event-Katalog, Outbox/Inbox-Gerüst, Consumer-Registrierung, Recurring Jobs, Queues", "X", "M", True,
  [], ["WP-I0-104"],
  "Versionierter Event-Katalog (`funk.<aggregat>.<ereignis>.v1`, `IIntegrationEvent`, `EventType`-Schema) mit Snapshot-Test, transaktionale Outbox und Inbox, `IEventConsumer`-Registrierung, `IRecurringJobRegistry`, benannte Queues (`default`, `notifications`, `emails`, `webhooks`, `exports`, `maintenance`, `realtime`, `live`, `indexing`; Paket-Queues reserviert), `EventContext` mit Akteur, Herkunft und Kausaltiefe (> 5 verworfen).",
  be=["`src/building-blocks/Funk.BuildingBlocks.Messaging` (Outbox, Inbox, JobQueue, Scheduler-Gerüst, EventCatalog)", "`src/modules/*/Funk.*.Contracts/Events/`", "`src/building-blocks/Funk.BuildingBlocks.Testing/Extensions/FakeEventConsumer.cs`", "`tests/Funk.Worker.Tests`"],
  arch=["16 §1.4 Zeile I0, §3.2.4, §3.2.5, §5.11", "06 §3.2–§3.8, §5.1–§5.4, D06-ADR-01…-07, -21", "01 §1.4 Zeile C3"],
  ep="01 §1.4 C3; 16 §5.11; 16 §4.6 Zeile „Event-Katalog …“ (Träger CE-OPS-021/-022, erste Events CE-WS-001/CE-PRJ-004)",
  ak=["Event-Katalog-Snapshot-Test schlägt bei jeder nicht additiven Änderung fehl (Typname ↔ Klasse eindeutig).",
      "Fake-Consumer aus `Funk.BuildingBlocks.Testing/Extensions` empfängt `funk.workspace.created.v1` ohne CE-Änderung (DoD Typ X).",
      "Event mit `CausationDepth > 5` wird verworfen, Metrik `funk.outbox.dropped{reason=\"causation_depth\"}` steigt.",
      "AK-16-09 (Gerüst): `EventCatalogSnapshotTests.Catalog_contains_minimum_set_of_D16` existiert und prüft ab I0 die Event-Typen der in I0 entstehenden Aggregate (`funk.identity.user_provisioned.v1`, `funk.workspace.created.v1`, `funk.project.created.v1`); jedes spätere Inkrement ergänzt seine Aggregate."],
  tests=["L1/L3 Outbox/Inbox/Kausaltiefe, Typ-X-Test mit Fake-Consumer.",
      "16 §7.2: `EventCatalogSnapshotTests` (`Funk.Contracts.Tests`), `ConsumerRegistrationTests` (`Funk.BuildingBlocks.Tests`), `RecurringJobRegistryTests` (`Funk.Worker.Tests`)."])

W("WP-I0-202", "Erweiterungspunkt B1/A2: ScopeRef, ScopeLevel, IScopeResolver, IScopeAncestorContributor, RouterStore.teamspaceId", "X", "S", True,
  [], ["WP-I0-104", "WP-I0-105"],
  "Sichtbarkeitsebenen `ScopeLevel` (Workspace│Teamspace│Project) und `ScopeRef` als einheitlicher Scope-Typ; `IScopeResolver` (CE: Workspace/Project) und `IScopeAncestorContributor` (E-20, CE ohne Beiträge); Frontend `SCOPE_LEVELS` und `RouterStore.teamspaceId` (wie Original).",
  be=["`src/building-blocks/Funk.BuildingBlocks/Scoping/`", "`src/modules/extensions/Teamspaces/Funk.Teamspaces.Contracts` (Platzhalter, R10)"],
  fe=["`frontend/libs/web/extensions/src/scope.ts`", "`frontend/libs/web/core/router.store.ts` (`teamspaceId`)"],
  arch=["16 §5.4, §3.3.0 E-20", "01 §1.4 Zeile B1, §5.5", "02 §3.5"],
  ep="01 §1.4 B1/A2; 16 §3.3.0 E-20; 16 §4.6 (Träger CE-WS-001, CE-PRJ-006)",
  ak=["`ScopeRef`-Gleichheit, Serialisierung und Vorfahrenkette (Project → Workspace) per Unit-Test; Fake-`IScopeAncestorContributor` ergänzt eine Teamspace-Ebene ohne CE-Änderung.",
      "AK-16-14 (Scope-Teil): `IScopeResolver` mit `FakeScopeAncestorContributor` liefert einen Teamspace in der Vorfahrenkette; ohne Contributor ergibt `ScopeLevel.Teamspace` `NotSupported`."],
  tests=["L1 Scoping, Typ-X-Test (Fake-Contributor), L2 RouterStore.",
      "16 §7.2: `ScopeResolverTests` (`Funk.BuildingBlocks.Tests`)."])

W("WP-I0-203", "Erweiterungspunkt E5: Permission-Katalog, roles/role_permissions, role_id, ISystemRoleGrantContributor, PermissionService", "X", "M", True,
  [], ["WP-I0-104", "WP-I0-105"],
  "Permission-Katalog `Permission(Key, Scope, ApiScope)` mit den 258 Keys aus 05 Anhang A (Generator `Funk.PermissionGen`), Tabelle `roles` mit System-Rollen Admin 20 / Member 15 / Guest 5 (`is_system`), `role_permissions`, Mitgliedschaften mit `role_id` (API liefert weiter `role: 20/15/5`), `IRoleDefinitionProvider`, `IVisibilityFilter<T>` + `CompositeVisibilityFilter<T>`, `ISystemRoleGrantContributor` (E-09), `ReservedPermissionKeys`; Frontend-Fassade `PermissionService.allowPermissions(...)` + Token `PERMISSION_EVALUATOR`.",
  be=["`src/modules/Authorization/Funk.Authorization`, `Funk.Authorization.Contracts`", "`src/tools/Funk.PermissionGen` (erzeugt `tests/security/permission-matrix.yaml`)", "`src/data/Funk.Data/Entities/Authorization/`"],
  fe=["`frontend/libs/web/core/permissions`"],
  arch=["05 §3.13, §3.14, §5.8, Anhang A/B", "02 §3.6", "16 §5.6, §3.2.1", "01 §1.4 Zeile E5", "17 ABG-036…ABG-038, Z-09 (HARM-00/03/04/06 angenommen)"],
  ep="01 §1.4 E5; 16 §3.3.0 E-09; 16 §4.6 (Träger CE-WS-008, CE-WS-012)",
  ak=["Generator erzeugt aus `_data/05-permission-matrix.json` Deskriptoren und Matrix-Datei deterministisch (`--check` in G1).",
      "`SystemRoleProvider` bildet die Original-Rollenlogik inkl. WS-Admin-Override (HARM-00) ab; Matrix-Test für die I0-Endpunkte 100 %.",
      "Fake-`ISystemRoleGrantContributor` ergänzt einen neuen Key für Member ohne Änderung an `SystemRoleProvider` (Typ X).",
      "Frontend prüft Rechte ausschließlich über `PermissionService` (ESLint-Regel verbietet direkte Rollenvergleiche).",
      "AK-16-14 (Rollen-Teil): der Katalog-Validator akzeptiert die Fake-Permission `teamspace.fake.read` (Scope Teamspace); ein `ISystemRoleGrantContributor`-Fake gewährt der Rolle Member `project.fake.read`, ohne `SystemRoleProvider` zu ändern; reservierte Namensräume (16 §3.2.1) werden von keinem CE-Key verwendet."],
  tests=["L1 Evaluator, L3 Matrix-Tests (I0-Routen), Typ-X-Test, L2 `PermissionService` gegen Original-Store-Fixtures.",
      "16 §7.2: `PermissionCatalogExtensionTests` (`Funk.Authorization.Tests`), `ReservedKeysUnusedInCe` (`Funk.ArchitectureTests`)."])

W("WP-I0-204", "Erweiterungspunkt H1/E3: FunkPrincipal, Policy-Scheme Cookies│ApiKey│Bearer, users.is_bot, Provisioning-Kette", "X", "M", True,
  [], ["WP-I0-104", "WP-I0-907"],
  "`FunkPrincipal` mit `Kind` (User│ApiKey│App│Bot), `Groups` (Keycloak-`groups`-Claim) und `ApiScopes`; Authentifizierungs-Policy-Scheme `Cookies│ApiKey│Bearer` mit vorkonfiguriertem, per `Funk:Auth:BearerEnabled=false` deaktiviertem Keycloak-JWT (Audience `funk-api`); Feld `users.is_bot`; `IUserProvisioningStep`-Kette mit freien `Order`-Slots (750/760 für E3) und `ProvisioningOrder`-Konstanten.",
  be=["`src/building-blocks/Funk.BuildingBlocks/Security/FunkPrincipal.cs`", "`src/building-blocks/Funk.BuildingBlocks.Web/Authentication/` (Policy-Scheme)", "`src/modules/Identity/Funk.Identity.Contracts/Provisioning/`", "`src/modules/extensions/Apps/Funk.Apps.Contracts` (Platzhalter, R10)"],
  arch=["05 §3.7.3, §3.12.1, §5.6, §5.7, §6.2", "16 §5.7, §5.8", "01 §1.4 Zeilen E3, H1"],
  ep="01 §1.4 E3/H1; 16 §4.6 (Träger CE-AUTH-001/-024/-025, CE-AUTH-028/-029)",
  ak=["Bearer-Schema ist registriert, liefert mit `BearerEnabled=false` immer 401 und mit `true` (Testprofil) einen gültigen Prinzipal aus einem Keycloak-Token (Typ X).",
      "Fake-`IUserProvisioningStep` (Order 750) läuft beim Login ohne CE-Änderung und sieht `Groups`.",
      "Bearer-Schema mit `Enabled=false` → 401; mit aktivem Fake-Bearer erhält ein Prinzipal `Kind = App` ohne passenden `ApiScope` 403; ein Fake-Provisioning-Schritt mit `Order = 750` läuft genau zwischen den CE-Schritten der Slots davor und danach."],
  tests=["L1 Principal-Mapping, L3 Schemata, Typ-X-Tests (Bearer an/aus, Fake-Provisioning-Step).",
      "16 §7.2: `ProvisioningPipelineOrderTests`, `BearerSchemeDisabledTests` (`Funk.Identity.Tests`)."])

W("WP-I0-205", "Erweiterungspunkt F1: Oberfläche Integrations, Webhook-Ingress, Verifier-Registry, integration_connections, Platzhalter-Contracts", "X", "M", True,
  [], ["WP-I0-104", "WP-I0-201"],
  "Oberfläche `Integrations` mit `POST /api/integrations/{provider}/webhooks/{connection_id}/` (404 ohne registrierten Verifier), `IWebhookSignatureVerifier`-Registry, `IWebhookIngress` (E-25, Roh-Body, case-insensitive Header-Map), `IWebhookEventHandler`, `IIntegrationProvider`, Inbox-Idempotenz, leere Tabelle `integration_connections`, reservierte Data-Protection-Purposes (`Funk.Integrations.ConnectionSecret.v1`, `Funk.Forgejo.UserToken.v1`), Rate-Limit-Policy `integration_webhook`, Platzhalter-Projekte `Funk.Integrations.Contracts`, `Funk.Forgejo.Contracts`, `Funk.Forgejo.Client` (nur `IForgejoClient` + DTOs), `Funk.Properties.Contracts`.",
  be=["`src/building-blocks/Funk.BuildingBlocks.Web/Integrations/`", "`src/modules/extensions/{Integrations,Forgejo,Properties}/`", "`src/data/Funk.Data/Entities/Integrations/IntegrationConnection.cs`", "`src/building-blocks/Funk.BuildingBlocks.Testing/Extensions/FakeWebhookSignatureVerifier.cs`"],
  arch=["16 §3.4.1–§3.4.3, §5.10, D16-ADR-09, -10, -13", "04 §4.23", "02 §3.3.1 (Oberflächen), §3.13", "01 §1.4 Zeile F1"],
  ep="01 §1.4 F1/F2; 16 §3.3.0 E-13 (Teil `integration_connections`), E-25; 16 §4.6 (Träger CE-OPS-021, CE-OPS-022)",
  ak=["Ohne Verifier: 404; mit Fake-Verifier und Fake-Handler wird eine Test-Delivery idempotent (zweite Zustellung derselben Delivery-ID ohne Wirkung) verarbeitet – ohne CE-Änderung (Typ X).",
      "Architekturtest R10: Platzhalter-Projekte enthalten nur Interfaces, DTOs, Enums, Konstanten.",
      "AK-16-07: `POST /api/integrations/forgejo/webhooks/{connection_id}/` (beliebige GUID) ohne Cookie → 404 `{\"error\": \"Page not found.\"}`; `…/webhooks/not-a-guid/` → 404; mit `FakeWebhookSignatureVerifier` + `FakeWebhookIngress`: gültige Signatur → 202, ungültige → 401, dieselbe Delivery-ID zweimal → 200 `duplicate`, Header in Kleinbuchstaben (`x-forgejo-signature`) wird erkannt, Body > 5 MiB → 413, 601. Request/min derselben `connection_id` → 429; die Endpunkt-Datei liegt in `Funk.BuildingBlocks.Web/Integrations/`."],
  tests=["L3 Ingress (Signatur falsch → 401, Roh-Body unverändert), Typ-X-Test, L0 R10/R11.",
      "16 §7.2: `IntegrationWebhookRouteTests` (`Funk.Integrations.Tests`, CE-Teil)."])

W("WP-I0-206", "Erweiterungspunkt F2: Forgejo-Container, Keycloak-Client funk-forgejo, forgejo-init, SSO-Smoke", "X", "S", True,
  [], ["WP-I0-102", "WP-I0-108"],
  "Forgejo (gepinnter LTS-Tag) läuft als Aspire-Ressource mit eigener Datenbank auf dem gemeinsamen PostgreSQL, Bootstrap-Skript und `Funk.Tools.ForgejoInit` (Admin, OAuth2-App mit beiden Redirect-URIs, Test-Repos); Anmeldung an Forgejo über denselben Keycloak (Client `funk-forgejo`, Auth-Source `keycloak`). Activity-Typen für Branch/Commit/PR sind im Activity-Katalog reserviert.",
  be=["`src/tools/Funk.Tools.ForgejoInit`", "`deploy/forgejo/bootstrap/forgejo-bootstrap.sh`", "`deploy/keycloak/config/20-forgejo-client.json`"],
  arch=["14 §3.4", "16 §3.4.7, §3.4.8", "00 ADR-007", "17 ABG-003, Z-13"],
  ep="01 §1.4 F2; 16 §3.4.8 (Zeile I0)",
  ak=["L6 `ForgejoSsoSmokeTests`: derselbe Keycloak-Testbenutzer meldet sich an funk. und an Forgejo an; Forgejo-Benutzer und funk.-Benutzer tragen dieselbe Keycloak-Identität.",
      "Forgejo-LTS-Tag ist gepinnt (O-04) und im Airgap-Image-Inventar `deploy/airgap/images.yaml` eingetragen.",
      "AK-16-08: `aspire run` (dev/test) – Forgejo `/api/healthz` 200, SSO-Login des Testbenutzers `member` in Forgejo über Keycloak erfolgreich, `artifacts/dev/forgejo.json` enthält die OAuth-App mit beiden Redirect-URIs aus 16 D16-ADR-09."],
  tests=["L6 Forgejo-SSO-Smoke im Profil `test`.",
      "16 §7.2: `ForgejoSsoSmokeTests` (`Funk.AppHost.Tests`)."])

W("WP-I0-207", "Erweiterungspunkt H6: SignalR-Hub /live/events/, Gruppen, IRealtimePublisher, IRealtimeGroupAuthorizer, LiveEventsService", "X", "S", True,
  [], ["WP-I0-107", "WP-I0-105", "WP-I0-201"],
  "Modul `Funk.RealtimeEvents` (+ `.Contracts`) im Host `Funk.Realtime`: Hub `/live/events/` mit Gruppen `ws:{id}`, `project:{id}`, `user:{id}`, `IRealtimeGroupAuthorizer` (E-22, CE-Präfixe), `IRealtimePublisher` mit `QueuedRealtimePublisher` (Api/Worker) und `HubRealtimePublisher` (Realtime-Host), Queue `live`; Frontend `LiveEventsService` + Token `LIVE_EVENT_HANDLERS` (ohne Handler).",
  be=["`src/modules/RealtimeEvents/Funk.RealtimeEvents`, `Funk.RealtimeEvents.Contracts`"],
  fe=["`frontend/libs/web/core/live-events`"],
  arch=["07 §3.16, §5.11", "06 §3.12, D06-ADR-12", "16 §5.12, §3.3.0 E-22", "17 ABG-106, ABG-112"],
  ep="01 §1.4 H6; 16 §3.3.0 E-22; 16 §4.6 (Walking Skeleton, `RealtimeSmokeTests`)",
  ak=["`RealtimeSmokeTests` (Hub-Teil): angemeldeter Benutzer tritt `user:{id}` bei, fremde Gruppen werden abgewiesen; Fake-Gruppen-Präfix per Fake-Authorizer ohne CE-Änderung (Typ X).",
      "Beitritt zu einer fremden Gruppe `ws:{id}`/`project:{id}`/`user:{id}` wird abgewiesen; ein Fake-Präfix mit registriertem `IRealtimeGroupAuthorizer` ist beitretbar, ohne Registrierung nicht."],
  tests=["L6 Hub-Smoke, Typ-X-Test, L2 `LiveEventsService` (Reconnect).",
      "16 §7.2: `RealtimeGroupAuthorizationTests` (`Funk.RealtimeEvents.Tests`; in 15 §6 als `HubGroupAuthorizationTests` geführt – ein Testname, Alias im Inventar)."])

W("WP-I0-208", "Erweiterungspunkte Querschnitt: Reservierungen + Kollisionstests, R11/R12, Frontend-Registries (Routen, Sidebar, Admin), Fake-Extensions", "X", "M", True,
  [], ["WP-I0-104", "WP-I0-105"],
  "Reservierte Permission-Namensräume, Routen-Präfixe, Activity-Felder, Event-Namensräume, Queues und Suche/AI-Bezeichner (`Reservations.cs`, `docs/extensions/reservations.yaml`) mit `ReservationCollisionTests`/`RouteReservationTests` (E-17); Architekturregeln R11/R12; Inventar `tests/extension-points.yaml`; Frontend-Registries `ROUTE_EXTENSIONS` + `mergeRoutes`, `SIDEBAR_ITEMS` (statisch), `ADMIN_SETTINGS_PAGES`, `ADMIN_ROUTE_EXTENSIONS`, `ADMIN_HEADER_SEGMENT_LABELS`, `APP_RAIL_ENABLED`, `provideWebExtensions()`/`provideAdminExtensions()`/`provideSpaceExtensions()`; Test-Erweiterungen `provideFakeExtensions()`, `provideFakeAdminExtensions()`, `provideFakeSpaceExtensions()`; Modulkatalog `FunkModuleCatalog`.",
  be=["`src/building-blocks/Funk.BuildingBlocks/Extensions/Reservations.cs`",
      "`src/hosts/Funk.Hosting/FunkModuleCatalog.cs`",
      "`tests/Funk.ArchitectureTests/{ReservationCollisionTests,RouteReservationTests,ExtensionPointInventoryTests}.cs`",
      "`tools/ci/assert-no-package-code`",
      "`tests/Funk.ArchitectureTests/{ReservationCollisionTests,RouteReservationTests,ExtensionRules,ExtensionPointInventoryTests,ReservedContractFieldsTests}.cs`"],
  fe=["`frontend/libs/web/extensions/src/`",
      "`frontend/libs/admin/extensions`, `frontend/libs/space/extensions`",
      "`frontend/libs/shared/cdk/src/extensions/` (`RouteExtension<K>`, `mergeRoutes`, `injectRegistry`)",
      "`frontend/tools/extension-registry-check`",
      "`frontend/apps/e2e/web/extensions.spec.ts`"],
  arch=["16 §3.1, §3.2, §3.3.0 E-17, D16-ADR-03, -04, -15", "08 §6.1–§6.5", "01 §6.4", "17 ABG-023, ABG-032, ABG-135"],
  ep="16 §1.4 Zeile I0 (Reservierungen, Registries); 16 §4.6 „Bewusst ohne Träger-CE-ID“ (CE-OPS-022)",
  ak=["Kollisionstests schlagen fehl, wenn eine CE-Route, ein Permission-Key oder eine Queue einen reservierten Namen benutzt.",
      "Eine Fake-Route über `ROUTE_EXTENSIONS` und ein Fake-Sidebar-Eintrag erscheinen ohne Änderung an CE-Dateien (Typ X, Vitest + Playwright).",
      "`ExtensionPointInventoryTests` und `extension-registry-check` gleichen `tests/extension-points.yaml` mit dem Code ab (jede P-Andockstelle aus 16 §1.4 hat Inkrement und Test).",
      "AK-16-03, AK-16-04, AK-16-17: `ReservationCollisionTests`, `RouteReservationTests`, `ExtensionRules` (R11/R12) und `tools/ci/assert-no-package-code` (Platzhalter-Projekte nur Interfaces/DTOs/Enums/Konstanten, keine Tabellen außer den in 16 §3.3/§3.4.2 als CE markierten) laufen in jedem Build mit 0 Verstößen.",
      "AK-16-01: `ExtensionPointInventoryTests` und `frontend/tools/extension-registry-check` melden für I0 0 fehlende Einträge in `tests/extension-points.yaml`; `ReservedContractFieldsTests` (AK-16-12) ist angelegt und wird von den Paketen I1–I4 um ihre V-Felder (16 §4.1/§4.2) ergänzt.",
      "E2E `frontend/apps/e2e/web/extensions.spec.ts` startet die Web-App mit `provideFakeExtensions()` (Build-Konfiguration `fake-extensions`, nur CI) und findet Fake-Route und Fake-Sidebar-Eintrag; Fake-Settings-Seite (WP-I1-203), Fake-Detail-Widget und Fake-Spreadsheet-Spalte (WP-I2-206) folgen."],
  tests=["L0 Architektur-/Inventartests, Typ-X-Tests Frontend."])

# --- Spikes I0 (Spike-Track) -----------------------------------------------------------

W("WP-I0-901", "Spike S1 – YDotNet + Hocuspocus-Protokoll in .NET", "S", "L", True,
  [], ["WP-I0-900", "WP-I0-107"],
  "Nachweis, dass ein .NET-Server mit YDotNet den unveränderten `@hocuspocus/provider` 2.15.2 bedient (Auth, Sync, Updates, Awareness, Stateless, Close-Codes, Titel-Fragment, Persistenz, Mehrinstanz über Valkey, Last/Soak). Gatet I4.",
  be=["`src/modules/Collaboration/Funk.Collaboration.Protocol` (Prototyp)", "`tests/Funk.Collaboration.Tests/Browser/ProviderConformanceTests.cs`", "`docs/spikes/S1-ergebnis.md`"],
  arch=["01 §9 Zeile S1", "07 §3.3–§3.10, §7.3 (P-01…P-30), §7.6 S1", "17 Z-101, Z-109"],
  orig=["`apps/live/src/hocuspocus.ts`", "`apps/live/src/extensions/`", "`apps/live/src/types/admin-commands.ts`", "`packages/editor/src/core/constants/document-collaborative-events.ts`"],
  ak=["Alle Erfolgskriterien aus 01 §9 S1 (u. a. 50 Editoren p95 < 150 ms, 1 h Soak < 5 % Speicherwachstum, zwei Instanzen konvergieren über Valkey) als automatisierte Tests grün – oder Fallback-Kette (y-websocket → YDotNet-Fork → Auftraggeber) aktiviert und dokumentiert.",
      "Awareness-Relay: der Awareness-Zustand von Client A erscheint bei Client B und wird beim Disconnect von A bei B entfernt (Playwright, 2 Clients mit Original-Provider, je Richtung ≥ 20 Wiederholungen ohne Fehlschlag); damit wird `collaboration-cursor` in I4 aktiviert (Z-109)."],
  tests=["Browser-Protokolltests mit Original-Provider (Playwright), Last LT-16-Vorstufe."])

W("WP-I0-902", "Spike S2 – Yjs → ProseMirror-JSON → HTML (und HTML → JSON) ohne Node", "S", "L", True,
  [], ["WP-I0-900"],
  "Nachweis, dass `Funk.Documents` Ausgabe-Gleichheit mit `@tiptap/html`/`y-prosemirror` erreicht (Korpus ≥ 200 Dokumente, HTML ≥ 99 % byte-gleich nach Normalisierung, JSON 100 % strukturgleich, ≥ 200 Dok./s). HTML/JSON-Teil gatet I2, Yjs-Teil gatet I4.",
  be=["`src/documents/Funk.Documents` (Prototyp)", "`tests/Funk.Documents.Tests/Golden/`", "`tools/golden/generate.mjs` (Node nur zur Entwicklungszeit)", "`docs/spikes/S2-ergebnis.md`"],
  arch=["01 §9 Zeile S2", "07 §3.12, §3.13, §7.6 S2", "10 §3.2", "17 Z-102"],
  orig=["`packages/editor/src/core/extensions/`", "`apps/live/src/lib/`", "`packages/editor/src/core/helpers/yjs-utils.ts`"],
  ak=["Erfolgskriterien 01 §9 S2 erreicht oder Fallback F-S2-1 (Jint mit gebündeltem `@tiptap/html`) bzw. F-S2-2 dokumentiert aktiviert.",
      "Typisierte Attribute aus Original-yjs (Zahl, Bool, `null`, Objekt) werden typgleich gelesen: die Korpusfälle S2-K6a ergeben JSON ohne Diff zum Original (O-07-01)."],
  tests=["L4 Golden-Korpus (G-DOC), Durchsatz-Benchmark als Test."])

W("WP-I0-903", "Spike S3 – PDF-Export mit PDFsharp/MigraDoc", "S", "M", True,
  [], ["WP-I0-900"],
  "Nachweis, dass PDFsharp/MigraDoc 6.2.4 (MIT) die Optik von `apps/live/src/lib/pdf` erreicht (20 Referenzseiten ≤ 2 % Pixelabweichung bei 150 dpi, Text extrahierbar, < 3 s für 20 Seiten). Gatet CE-PAGE-011 (I4).",
  be=["`src/documents/Funk.Documents.Pdf` (Prototyp)", "`tests/Funk.Documents.Pdf.Tests`", "`docs/spikes/S3-ergebnis.md`"],
  arch=["01 §9 Zeile S3, O-09", "07 §3.15, §7.6 S3", "17 Z-103"],
  orig=["`apps/live/src/lib/pdf/`", "`apps/live/tests/`", "`apps/web/core/components/editor/pdf/document.tsx`"],
  ak=["Erfolgskriterien 01 §9 S3 erreicht oder Fallback SkiaSharp `SKDocument` aktiviert; Emoji außerhalb der BMP und Surrogatpaare werden als Glyphen gerendert (Raster-Diff im Grenzwert) und sind als identischer Text extrahierbar (S3-K6).",
      "Lizenz/Plattform des Test-Rasterizers geklärt (Docnet.Core vs. PDFtoImage, O-07-04)."],
  tests=["L4 G-PDF (Text + Raster-Diff), 21 Fälle aus `apps/live/tests`."])

W("WP-I0-904", "Spike S4 – Kanban/Gantt-Drag-and-Drop in Angular (zoneless, virtualisiert)", "S", "M", True,
  [], ["WP-I0-900", "WP-I0-105"],
  "Nachweis, dass pragmatic-drag-and-drop zoneless mit Virtualisierung verhaltensgleich und performant läuft (1 000 Karten, 8 Spalten, ≥ 55 fps; Gantt verschieben/Größe/Reorder). Gatet I2.",
  fe=["`frontend/libs/shared/dnd` (Prototyp)", "`docs/spikes/S4-ergebnis.md`"],
  arch=["01 §9 Zeile S4", "08 §3.9, §5.12"],
  orig=["`apps/web/core/components/issues/issue-layouts/kanban/`", "`apps/web/core/components/gantt-chart/`"],
  ak=["Erfolgskriterien 01 §9 S4 als Playwright-Perf-Trace-Tests (LT-14/15) grün oder Fallback (eigene Pointer-Events für Gantt / CDK DragDrop für Kanban) dokumentiert."],
  tests=["Perf-Trace-Tests, Playwright-Szenarien des Originals."])

W("WP-I0-905", "Spike S5 – Editor-NodeViews in Angular mit Tiptap 2.27 (Schema-Freeze)", "S", "M", True,
  [], ["WP-I0-900", "WP-I0-105"],
  "Schnitt ED-0: Kern-Kopie per Codemod, Angular-Bindung, 8 NodeView-/Menü-Prototypen, Schema-Snapshot aller Varianten identisch zum Original, Visual der Editor-Seite ≤ 0,5 %, 5 000 Blöcke ohne Eingabe-Lag. Gatet I2 vollständig; das Kriterium „NodeView-Rendering stabil mit Yjs“ darf bis vor I4 nachgeliefert werden (ABG-114).",
  fe=["`frontend/libs/shared/editor/{core,angular-binding,components}` (Prototyp)", "`frontend/libs/shared/editor/VERSIONS.json`", "`frontend/tools/editor-port/` (Codemod `port-core.mjs`, Drift-Check)", "`docs/spikes/S5-ergebnis.md`"],
  arch=["01 §9 Zeile S5", "10 §1.5 (ED-0), §3.2–§3.5, §7.3", "17 ABG-114, Z-105"],
  orig=["`packages/editor/src/`"],
  ak=["Erfolgskriterien 10 §7.3 / 01 §9 S5 als Tests grün; G-SCHEMA (Varianten rich, lite, document, title) identisch.",
      "DOM-Details (`FloatingOverlay`, `contentDOM`, Position `tiptap-core.css`) per DOM-Golden festgeschrieben (O-D10-05)."],
  tests=["G-SCHEMA, DOM-Goldens, Visual Editor-Seite, Eingabe-Latenz-Test."])

W("WP-I0-906", "Spike S6 – Charts 1:1 mit D3 + Angular-SVG", "S", "S", True,
  [], ["WP-I0-105"],
  "Nachweis, dass Bar (inkl. Lollipop), Pie (Center-Label), Area mit Vergleichslinie, Line, Radar, TreeMap und Cycle-Burndown pixelgleich (≤ 0,5 %) mit gleichem Tooltip-/Legend-Verhalten nachgebaut werden. Gatet I3.",
  fe=["`frontend/libs/shared/blocks/charts` (Prototyp)", "`docs/spikes/S6-ergebnis.md`"],
  arch=["01 §9 Zeile S6", "09 §3.12"],
  orig=["`packages/blocks/src/charts/`", "`apps/web/core/components/core/sidebar/progress-chart.tsx`"],
  ak=["Visual-Diff ≤ 0,5 % je Diagrammtyp (hell/dunkel) oder Fallback ECharts mit Abnahme durch den Auftraggeber."],
  tests=["L8 Galerie-Visual Charts."])

W("WP-I0-907", "Spike S7 – Keycloak-BFF, Logout, Theme, Forgejo-SSO", "S", "M", True,
  [], ["WP-I0-102"],
  "Nachweis, dass der Keycloak-Aufbau ADR-008 vollständig erfüllt (PKCE je Client, HttpOnly-Session, RP- und Back-Channel-Logout < 2 s, Sperre wirkt sofort, JIT, Rolle → God Mode, optionaler Step-up, Theme-Visual ≤ 1 %, Forgejo-SSO). Gatet die Abnahme von I0.",
  be=["`docs/spikes/S7-ergebnis.md`"],
  arch=["01 §9 Zeile S7, O-06, O-08", "05 §3.3–§3.8, §3.16", "14 §3.3, O-14-01, O-14-10", "17 Z-03, Z-14"],
  orig=["`apps/web/core/components/account/auth-forms/`", "`apps/space/core/components/account/`"],
  ak=["Erfolgskriterien 01 §9 S7 als automatisierte Tests (werden in WP-I0-001/-108 übernommen); `max_age=0`-Verhalten von Keycloak 26 geklärt (Z-03), Optionsnamen geklärt (Z-14), Kontokonsole-Deep-Links verifiziert (O-D05-01)."],
  tests=["L6 Login/Logout/Back-Channel, Visual Theme-Prototyp."])

W("WP-I0-908", "Spike S8 – Objektspeicher-Kompatibilität (Presigned POST/GET, Upload-Modus)", "S", "S", True,
  [], ["WP-I0-102"],
  "Matrix SeaweedFS, Garage, Ceph-RGW (optional), `pgsty/silo` für Presigned POST mit Bedingungen, Presigned GET mit Response-Overrides, HEAD, Copy, Batch-Delete, Zugriff über Gateway; Dateisystem-Provider im Proxy-Modus besteht dieselben Contract-Tests. Entscheidet O-03. Gatet I1.",
  be=["`src/platform/Funk.Platform.Storage` (Prototyp)", "`tests/Funk.Platform.Tests/Storage/ObjectStorageContractTests.cs`", "`docs/spikes/S8-ergebnis.md`"],
  arch=["01 §9 Zeile S8, O-03", "14 §3.7.6", "05 §3.17.4"],
  orig=["`apps/api/plane/settings/storage.py`", "`apps/api/plane/app/views/asset/v2.py`"],
  ak=["Default-Backend und Upload-Modus (`Direct`/`Proxy`) festgelegt und in `docs/spikes/S8-ergebnis.md` begründet; `ObjectStorageContractTests` grün für das Default-Backend und den Dateisystem-Provider."],
  tests=["Storage-Contract-Tests je Backend."])

W("WP-I0-909", "Spike S9 – Work-Item-Listen-Performance & Filter-Engine (EF Core)", "S", "M", True,
  [], ["WP-I0-104"],
  "Nachweis, dass EF Core die Filter-AST mit Gruppierung/Sub-Gruppierung/Pagination effizient übersetzt (50 000 Work Items: gruppiert p95 < 300 ms, Spreadsheet p95 < 200 ms, AND/OR/NOT p95 < 400 ms, kein Seq-Scan bei Projektfilter). Gatet I2.",
  be=["`src/modules/WorkItems/Funk.WorkItems/Query/` (Prototyp)", "`tests/load/` (Volumenprofil L)", "`docs/spikes/S9-ergebnis.md`"],
  arch=["01 §9 Zeile S9", "02 §3.11, R-D02-01", "03 §3.4.5"],
  orig=["`apps/api/plane/utils/grouper.py`", "`apps/api/plane/utils/paginator.py`", "`apps/api/plane/utils/filters/`"],
  ak=["Zielwerte 01 §9 S9 als `SqlPlanAssertions`-/Lasttests grün oder Fallback (handgeschriebenes SQL mit Window-Functions) aktiviert."],
  tests=["L9 LT-01…LT-03-Vorstufe, SQL-Plan-Assertions."])

W("WP-I0-910", "Spike S10 – Designsystem-Parität (Angular Aria/CDK + floating-ui)", "S", "M", True,
  [], ["WP-I0-105"],
  "Nachweis, dass 10 Leit-Komponenten (Button, Input, Menu, Combobox/Select, Tooltip, Dialog, Tabs, Popover, Avatar, Toast) und die Workspace-Shell DOM- und pixelgleich (≤ 0,1 %) mit Original-Tastaturbedienung umsetzbar sind; Portal-Schicht ohne CDK-Overlay (Z-06). Der Shell-Teil gehört zu I0.",
  fe=["`frontend/libs/shared/propel/headless/` (Prototyp)", "`docs/spikes/S10-ergebnis.md`"],
  arch=["01 §9 Zeile S10", "09 §3.3–§3.5, §3.14", "17 Z-06, ABG-026"],
  orig=["`packages/propel/` (npm `@makeplane/propel@0.7.3`)", "`packages/blocks/src/`"],
  ak=["Erfolgskriterien 01 §9 S10 als Galerie-Tests grün; Host-Form der Blocks-Select-Familie festgelegt (O-D09-16)."],
  tests=["Galerie DOM/Visual, Tastatur-Tests."])

W("WP-I0-912", "Spike S12 – Eigene Outbox/Job-Queue auf PostgreSQL", "S", "S", True,
  [], ["WP-I0-104", "WP-I0-201"],
  "Nachweis von Zuverlässigkeit und Durchsatz der eigenen PostgreSQL-Messaging-Implementierung (1 000 Jobs/s mit 3 Workern ohne Doppelverarbeitung, Outbox p95 < 500 ms, Leader-Failover < 30 s, Kill -9 verliert nichts). Gatet I1.",
  be=["`tests/Funk.Worker.Tests/Reliability/`", "`docs/spikes/S12-ergebnis.md`"],
  arch=["01 §9 Zeile S12", "06 §3.3–§3.6, R-D06-01, O-D06-11", "17 Z-104, Z-117"],
  orig=["`apps/api/plane/celery.py`", "`apps/api/plane/bgtasks/`"],
  ak=["Kriterien 01 §9 S12 als Tests grün oder Fallback Wolverine (MIT) hinter denselben Interfaces aktiviert; Entscheidung zur Session-Verbindung `funk-session` hinter PgBouncer (Z-117)."],
  tests=["Kill-/Failover-Tests, Durchsatz-Benchmark."])

W("WP-I0-913", "Spike Scope-FK – zusammengesetzter Fremdschlüssel (project_id, workspace_id) inkl. nullable workspace_id", "S", "S", True,
  [], ["WP-I0-104"],
  "Nachweis, dass die Scope-FK-Konvention (composite FK mit überlappender `workspace_id`, `MATCH SIMPLE`) ohne EF-Fix-up-Probleme funktioniert – für Label (Workspace-Scope), State (Projekt-Scope), `file_assets` und `search_documents`.",
  be=["`src/data/Funk.Data/Conventions/ScopeForeignKeyConvention.cs` (Prototyp)", "`docs/spikes/SFK-ergebnis.md`"],
  arch=["03 §5.2, R-D03-02, O-D03-05", "17 Z-107"],
  ak=["Konvention erzeugt die erwarteten Constraints; Fallback (Raw-SQL-Constraint) nur bei EF-Warnungen/Fix-up-Effekten, dokumentiert."],
  tests=["L3 Schema-Konformitätstest."])

W("WP-I0-999", "Abnahme I0 – Walking Skeleton (G5)", "A", "S", False,
  [], ["WP-I0-001", "WP-I0-002", "WP-I0-003", "WP-I0-004", "WP-I0-005", "WP-I0-006", "WP-I0-101", "WP-I0-102", "WP-I0-103", "WP-I0-104", "WP-I0-105", "WP-I0-106", "WP-I0-107", "WP-I0-108", "WP-I0-109", "WP-I0-201", "WP-I0-202", "WP-I0-203", "WP-I0-204", "WP-I0-205", "WP-I0-206", "WP-I0-207", "WP-I0-208", "WP-I0-900", "WP-I0-907", "WP-I0-910", "WP-I0-911"],
  "Inkrement-Abnahme I0 nach 15 §3.15.1 G5 und Meilenstein M0 (plan/01-roadmap-ce.md §4).",
  arch=["plan/01-roadmap-ce.md §4 (M0)", "15 §3.15.1 (G5), §3.16 Zeile I0"],
  ak=["Alle Abnahmekriterien M0 aus plan/01-roadmap-ce.md §4 erfüllt; `docs/acceptance/I0.md` generiert (`tools/ci/acceptance-report`)."],
  tests=["G5 `--inc I0`."])


# Endpunkte, die vor dem Arbeitspaket ihrer CE-ID gebraucht werden (Vorab-Endpunkte;
# das spätere CE-Paket erweitert sie nur). Schlüssel = EP-ID aus architecture/_data/endpoints.json.
# Vorlauf-Pakete (plan/01 L-8, plan/04 OP-PLAN-11): dürfen vor dem Meilenstein des Vorgänger-Inkrements
# beginnen, registrieren keine Screens und werden mit ihrem Inkrement abgenommen. build.py prüft, dass genau
# diese Pakete nicht (transitiv) vom Vorgänger-Meilenstein abhängen.
VORLAUF = {
    # Editor-Track (ab M0 bzw. nach WP-I1-103)
    "WP-I2-101", "WP-I2-207", "WP-I2-021", "WP-I2-022", "WP-I2-023", "WP-I2-024",
    # Dokument-/Realtime-Track (ab M2)
    "WP-I4-101", "WP-I4-201", "WP-I4-202", "WP-I4-006", "WP-I4-008",
}

EP_OVERRIDE = {
    "EP-0049": "WP-I0-001",  # PATCH /api/users/me/ (Profil-Grunddaten nach JIT)
    "EP-0052": "WP-I0-001",  # PATCH /api/users/me/onboard/
    "EP-0071": "WP-I0-003",  # GET /api/instances/admins/me/
    "EP-0072": "WP-I0-003",  # GET /api/instances/admins/session/
    "EP-0083": "WP-I0-003",  # POST /api/instances/admins/sign-out/
    "EP-0124": "WP-I0-002",  # GET /api/workspaces/{slug}/
    "EP-0138": "WP-I0-004",  # GET {W}/workspace-members/me/
    "EP-0186": "WP-I0-005",  # GET {W}/projects/
    "EP-0189": "WP-I0-005",  # GET {W}/projects/{pk}/
    "EP-0205": "WP-I0-005",  # GET {P}/project-members/me/
    "EP-0414": "WP-I0-207",  # GET /live/events/ (SignalR-Hub)
    "EP-0729": "WP-I0-205",  # POST /api/integrations/{provider}/webhooks/{connection_id}/
    "EP-0732": "WP-I0-104",  # GET /api/schema/internal/ (Contract-Check)
    "EP-0054": "WP-I1-015",  # PATCH /api/users/me/tour-completed/
    "EP-0139": "WP-I3-004",  # GET {W}/cycles/
    "EP-0142": "WP-I3-008",  # GET {W}/modules/
}
