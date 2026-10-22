# A11 – Frontend: God Mode (`apps/admin`) & Public Space (`apps/space`) (IST-Analyse)

> **Status:** IST-Analyse (Plane v1.4.2 Community Edition; `apps/admin/package.json` → `"version": "1.4.2"`, `apps/space/package.json` → `"version": "1.4.2"`)
> **Bindende Leitplanken:** `migration/architecture/00-grundsatzentscheidungen.md` (ADR-000 … ADR-006)
> **Analysierte Quellen (vollständig gelesen):** alle 127 Dateien unter `apps/admin/` und alle 207 Dateien unter `apps/space/` (Quellcode, Konfiguration, Docker/Caddy/nginx, Manifeste; Binär-Assets nur inventarisiert). Zusätzlich für Verträge/Verhalten gelesen: `packages/services/src/{api.service,instance/instance.service,auth/auth.service,auth/sites-auth.service,workspace/instance-workspace.service,user/user.service,user/sites-member.service,label/sites-label.service,state/sites-state.service,module/sites-module.service,cycle/sites-cycle.service,issue/sites-issue.service,project/sites-publish.service,file/sites-file.service,helpers/url}.ts`, `packages/types/src/instance/*.ts`, `packages/types/src/publish.ts`, `packages/types/src/issues/issue.ts` (Public-Typen), `packages/types/src/issues/activity/issue_comment.ts` (`TIssuePublicComment`, `ActorDetail`), `packages/constants/src/{endpoints,workspace,instance,user,subscription}.ts`, `packages/constants/src/auth/*.ts`, `packages/constants/src/issue/{layout,filter,common}.ts`, `packages/utils/src/{validation,auth,file,url,string,theme-legacy}.ts` (verwendete Funktionen), `packages/i18n/src/core/instance.ts`, `packages/i18n/src/constants/language.ts`, `packages/i18n/src/locales/en/*.json` (verwendete Schlüssel), `packages/blocks/src/auth/oauth/*.tsx`, Backend-Gegenstellen `apps/api/plane/license/{urls.py,api/views/*.py,api/serializers/*.py,api/permissions/instance.py,models/instance.py,management/commands/configure_instance.py}`, `apps/api/plane/utils/instance_config_variables/{core,extended}.py`, `apps/api/plane/space/{urls/*.py,views/{project,meta,base,issue,asset,intake}.py,utils/grouper.py,serializer/project.py}`, `apps/api/plane/authentication/{urls.py,adapter/error.py,utils/{host,login,password}.py,middleware/session.py,rate_limit.py,views/space/{check,google}.py}`, `apps/api/plane/settings/common.py` (Cookie-/Base-URL-Settings), `apps/api/plane/db/models/deploy_board.py`, `apps/web/components/project/publish-project/modal.tsx` (Publizieren), `apps/web/components/workspace/billing/comparison/plans.tsx` (Plan-Matrix, nur als Evidenz für Bezahl-Features).
> Alle Pfade relativ zum Repo-Root. Abkürzungen: `ADM/` = `apps/admin/`, `SPC/` = `apps/space/`, `API/` = `apps/api/plane/`, `SVC/` = `packages/services/src/`, `CONST/` = `packages/constants/src/`, `TYPES/` = `packages/types/src/`. In Dateipfaden sind die Klammer-Segmente `(all)`, `(home)`, `(dashboard)` echte Ordnernamen (React-Router-„Route Groups“ ohne URL-Anteil).

---

## Inhaltsverzeichnis

1. Überblick & Verantwortlichkeiten
   - 1.1 God Mode (`apps/admin`)
   - 1.2 Public Space (`apps/space`)
   - 1.3 Community- vs. Bezahl-Edition in diesem Bereich (Kurzfassung, Details in 2.30)
2. Vollständige Inventare
   - **Admin:** 2.1 Routen · 2.2 Seitentitel/Meta · 2.3 Dateien · 2.4 Sidebar-Menü · 2.5 Breadcrumb-Labels · 2.6 Stores · 2.7 API-Aufrufe · 2.8 Instanz-Konfigurationsschlüssel · 2.9 Formularfelder je Seite · 2.10 Toasts/Banner/Modal-Texte · 2.11 Auth-Fehlercodes (Admin) · 2.12 Komponenten · 2.13 Assets · 2.14 Browser-Speicher, Cookies, SWR-Keys
   - **Space:** 2.15 Routen · 2.16 Seitentitel/Meta/HTTP-Header · 2.17 Dateien · 2.18 Stores · 2.19 API-Aufrufe · 2.20 Query-Parameter · 2.21 Auth-Fehlercodes (Space) · 2.22 Komponenten · 2.23 Hart codierte UI-Texte · 2.24 i18n-Schlüssel · 2.25 Assets · 2.26 Browser-Speicher, Cookies, SWR-Keys
   - **Gemeinsam:** 2.27 Verwendete Propel-/Blocks-Bausteine · 2.28 Icons · 2.29 Build-/Laufzeit-Konfiguration · 2.30 Bezahl-Edition-Features mit Bezug zu A11
3. Verhalten, Logik, Abläufe (inkl. Edge-Cases)
4. Abhängigkeiten zu anderen Bereichen
5. Migrationshinweise (.NET/EF Core, Angular)
6. Offene Punkte

---

## 1. Überblick & Verantwortlichkeiten

### 1.1 God Mode (`apps/admin`)

| Aspekt | IST | Quelle |
|---|---|---|
| Zweck | Instanz-Administration („God Mode“) einer selbst gehosteten Plane-Instanz: Erst-Einrichtung (erster Instanz-Admin), Anmeldung des Instanz-Admins, globale Instanzeinstellungen (Name, Telemetrie), SMTP, Authentifizierungsmethoden (Unique Codes, Passwort, Google, GitHub, GitLab, Gitea, Sign-up-Freigabe), Workspace-Verwaltung (Liste, Anlage, Sperre der Workspace-Anlage), AI-Zugangsdaten (OpenAI), Unsplash-Key | `ADM/app/routes.ts` |
| Technologie | React 19 + React Router v8 (Framework-Modus, **SPA**, `ssr: false`), Vite, MobX-Stores, SWR, react-hook-form, next-themes, Tailwind (via `@plane/tailwind-config`), Primitive aus `@makeplane/propel`, Composite aus `@plane/blocks` | `ADM/react-router.config.ts`, `ADM/package.json` |
| Base-Path | `VITE_ADMIN_BASE_PATH` (Default-Build-Arg `/god-mode`), normalisiert über `joinUrlPath(..., "/")` → `/god-mode/` | `ADM/react-router.config.ts`, `ADM/vite.config.ts`, `ADM/Dockerfile.admin` |
| Dev-Port | 3001 (`react-router dev --port 3001`), Host `127.0.0.1` | `ADM/package.json`, `ADM/vite.config.ts` |
| Produktion | Statischer Client-Build (`build/client`) unter `/usr/share/caddy/html/god-mode`, ausgeliefert von Caddy auf `:3000` mit SPA-Fallback `try_files {path} /god-mode/index.html`, Rate-Limit 300 Requests/Minute/IP, Header `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`, `X-XSS-Protection: 1; mode=block`; Healthcheck `curl http://127.0.0.1:3000/god-mode` | `ADM/Dockerfile.admin`, `ADM/caddy/Caddyfile` |
| Sprache | Alle Texte **hart codiert Englisch** (kein `useTranslation`). `TranslationProvider` wird nur gemountet, weil der Toast-Viewport aus `@plane/blocks/toast` `useTranslation` aufruft | `ADM/providers/core.tsx` (Kommentar Z. 30–31) |
| Auth-Modell | Separater Admin-Session-Cookie `admin-session-id` (Laufzeit `ADMIN_SESSION_COOKIE_AGE`, Default 3600 s), automatisch für **jeden** Request-Pfad, der `instances` enthält; Login/Setup/Logout über **native HTML-Form-POSTs** mit `csrfmiddlewaretoken` und Server-Redirects | `API/authentication/middleware/session.py`, `API/settings/common.py` Z. 431–432, `ADM/app/(all)/(home)/sign-in-form.tsx` |
| Berechtigung | Alle Admin-APIs (außer `GET /api/instances/`, Sign-in/up) verlangen `InstanceAdminPermission` = angemeldeter Nutzer mit `InstanceAdmin.role >= 15` für die (einzige) Instanz | `API/license/api/permissions/instance.py` |

### 1.2 Public Space (`apps/space`)

| Aspekt | IST | Quelle |
|---|---|---|
| Zweck | Öffentliche, schreibgeschützte Darstellung publizierter Projekte („Plane Publish“): Liste/Board der Work Items eines Projekts, Filter (Priorität, Status), Peek-Ansicht mit Beschreibung, Eigenschaften, Kommentaren, Emoji-Reaktionen und Up/Down-Votes; eigener Login/Sign-up (E-Mail-Check → Passwort oder Unique Code, OAuth-Buttons) für Interaktionen | `SPC/app/routes.ts`, `SPC/components/**` |
| Technologie | React 19 + React Router v8 Framework-Modus **mit SSR** (`ssr: true`), Laufzeit `react-router-serve` (Node 22) – SSR wird für OpenGraph/Twitter-Meta der Board-Seite genutzt (Server-`loader`) | `SPC/react-router.config.ts`, `SPC/Dockerfile.space`, `SPC/app/issues/[anchor]/layout.tsx` |
| Base-Path | `VITE_SPACE_BASE_PATH` (Default `/spaces`) → `/spaces/` | `SPC/react-router.config.ts`, `SPC/Dockerfile.space` |
| Dev-Port | 3002 | `SPC/package.json` |
| Produktion | `CMD ["./node_modules/.bin/react-router-serve", "./build/server/index.js"]` auf Port 3000, Healthcheck `curl http://127.0.0.1:3000/spaces/`. `SPC/nginx/nginx.conf` (SPA-Fallback `/spaces/index.html`) ist ein Altartefakt und wird vom aktuellen Dockerfile **nicht** verwendet | `SPC/Dockerfile.space`, `SPC/nginx/nginx.conf` |
| Sprache | Gemischt: überwiegend hart codiertes Englisch, einzelne Texte über `@plane/i18n` (`t(...)`), Sprache aus `localStorage["userLanguage"]` (Fallback `en`) – wird mit der Web-App geteilt, wenn gleiche Origin | `SPC/app/entry.client.tsx`, `packages/i18n/src/core/instance.ts` |
| Auth-Modell | Normaler App-Session-Cookie `session-id` (Default 7 Tage), geteilt mit der Web-App; anonym lesbar, Schreibaktionen (Kommentar, Reaktion, Vote, Upload) verlangen Login | `API/settings/common.py` Z. 424–426, `API/space/views/base.py` |
| Einstieg aus Web-App | Projekt-Publish-Modal erzeugt Link `${SPACE_BASE_URL\|\|origin}${SPACE_BASE_PATH}/issues/${anchor}` | `apps/web/components/project/publish-project/modal.tsx` Z. 183–186 |

### 1.3 Community- vs. Bezahl-Edition in diesem Bereich (Kurzfassung)

Das Repo enthält **nur die Community Edition**. Für God Mode und Space existieren im Code ausschließlich leere Erweiterungspunkte (`ADM/providers/extended.tsx`, `ADM/components/common/header/extended.ts`, `SPC/hooks/oauth/extended.tsx`, `SPC/hooks/use-editor-flagging.ts`, `TYPES/instance/auth-ee.ts` mit `never`-Typen) sowie Indizien für Bezahl-Funktionen (ungenutzte Assets/Typen, Backend-Endpunkte ohne UI, Plan-Matrix). Laut ADR-001 sind **alle** diese Funktionen in der Zielplattform immer aktiv. Die vollständige Liste mit Evidenz und Sicherheitsgrad steht in **Abschnitt 2.30**; die Kernpunkte:

| Bereich | Bezahl-Funktion (Plan laut Plan-Matrix) | Evidenz im Repo |
|---|---|---|
| God Mode | OIDC-SSO (One/Pro/Business/Enterprise, „selfHostedOnly“), SAML-SSO (One+), LDAP (Enterprise, „coming soon“) | `apps/web/components/workspace/billing/comparison/plans.tsx` Z. 1060–1127, `packages/i18n/src/locales/en/auth.json` (`sso.providers.saml` / `sso.providers.oidc`, `auth.ldap`), `CONST/subscription.ts` |
| Space | Publish Views (Pro+), Publish Pages (One+, „comment without signing into your workspace“), Intake Forms (Business+), zusätzliche Board-Layouts Calendar/Spreadsheet/Gantt (Typen vorbereitet) | `plans.tsx` Z. 447, 510, 853; `SPC/types/intake.d.ts`; `SPC/app/assets/instance/intake-sent-{dark,light}.png` (ungenutzt); `TYPES/publish.ts` (`TPublishEntityType = "project" \| "page"`, `TProjectPublishLayouts`); `API/db/models/deploy_board.py` (`TYPE_CHOICES` inkl. `page`, `view`, `intake`); `API/space/urls/intake.py` |

---

## 2. Vollständige Inventare

### 2.1 Admin – Routentabelle

Alle URLs relativ zum Base-Path `/god-mode/`. Alle internen Links/Navigationen werden durch die Next-Compat-Shims (`ADM/app/compat/next/link.tsx`, `ADM/app/compat/next/navigation.ts`, Helper `ADM/app/compat/next/helper.ts → ensureTrailingSlash`) **mit abschließendem Slash** erzeugt (z. B. `/general/`), ausgenommen `/`.

| # | URL (unter `/god-mode`) | Layout | Seite (Datei) | Guard / Verhalten | Quelle |
|---|---|---|---|---|---|
| R1 | `/` (index) | `ADM/app/(all)/(home)/layout.tsx` | `ADM/app/(all)/(home)/page.tsx` | Kein Login nötig. Zeigt Spinner (bis Instanzinfo), Fehleransicht, **Setup-Formular** (`is_setup_done=false`) oder **Sign-in-Formular**. Ist `isUserLoggedIn === true` → `replace("/general")` | `ADM/app/routes.ts` Z. 11 |
| R2 | `/general/` | `ADM/app/(all)/(dashboard)/layout.tsx` | `.../(dashboard)/general/page.tsx` + `form.tsx` | Dashboard-Guard: `isUserLoggedIn === false` → `replace("/")`; `undefined` → Spinner | `ADM/app/routes.ts` Z. 13 |
| R3 | `/workspace/` | Dashboard | `.../(dashboard)/workspace/page.tsx` | Dashboard-Guard | Z. 14 |
| R4 | `/workspace/create/` | Dashboard | `.../(dashboard)/workspace/create/page.tsx` + `form.tsx` | Dashboard-Guard | Z. 15 |
| R5 | `/email/` | Dashboard | `.../(dashboard)/email/page.tsx` + `email-config-form.tsx` + `test-email-modal.tsx` | Dashboard-Guard | Z. 16 |
| R6 | `/authentication/` | Dashboard | `.../(dashboard)/authentication/page.tsx` | Dashboard-Guard | Z. 17 |
| R7 | `/authentication/github/` | Dashboard | `.../authentication/github/page.tsx` + `form.tsx` | Dashboard-Guard | Z. 18 |
| R8 | `/authentication/gitlab/` | Dashboard | `.../authentication/gitlab/page.tsx` + `form.tsx` | Dashboard-Guard | Z. 19 |
| R9 | `/authentication/google/` | Dashboard | `.../authentication/google/page.tsx` + `form.tsx` | Dashboard-Guard | Z. 20 |
| R10 | `/authentication/gitea/` | Dashboard | `.../authentication/gitea/page.tsx` + `form.tsx` | Dashboard-Guard | Z. 21 |
| R11 | `/ai/` | Dashboard | `.../(dashboard)/ai/page.tsx` + `form.tsx` | Dashboard-Guard | Z. 22 |
| R12 | `/image/` | Dashboard | `.../(dashboard)/image/page.tsx` + `form.tsx` | Dashboard-Guard | Z. 23 |
| R13 | `*` (Catch-all) | – (kein Layout) | `ADM/app/components/404.tsx` | Kein Guard; Button „Go to general settings“ → `/general/` | Z. 26 |

Server-seitige Redirect-Ziele (Backend → Admin-SPA), relevant für Routing-Kompatibilität:

| Auslöser | Ziel-URL | Quelle |
|---|---|---|
| Erfolgreiches Setup/Sign-in | `{ADMIN_BASE_URL oder WEB_URL/APP_BASE_URL}{ADMIN_BASE_PATH normalisiert "/god-mode/"}general/` | `API/license/api/views/admin.py` (`urljoin(base_host(..., is_admin=True), "general/")`) |
| Fehler bei Setup/Sign-in | `{base_host(is_admin)}?error_code=<int>&error_message=<NAME>[&email=…&first_name=…&last_name=…&company_name=…&is_telemetry_enabled=…]` | `API/license/api/views/admin.py`, `API/authentication/adapter/error.py` Z. 89–94 |
| Rate-Limit überschritten | `{base_host(is_admin)}?error_code=5900&error_message=RATE_LIMIT_EXCEEDED` | `API/authentication/rate_limit.py` Z. 62–95 |
| Sign-out | `{base_host(is_admin)}` (Root `/god-mode/`) | `API/license/api/views/admin.py` (`InstanceAdminSignOutEndpoint`) |

### 2.2 Admin – Seitentitel / Meta

| Route | `<title>` | weitere Meta | Quelle |
|---|---|---|---|
| Root-Default (alle Seiten ohne eigenen Titel, inkl. 404) | `Plane \| Simple, extensible, open-source project management tool.` | `description`: „Open-source project management tool to manage work items, sprints, and product roadmaps with peace of mind.“; `og:title`, `og:description`, `og:url=https://plane.so/`, `keywords` (software development, customer feedback, software, accelerate, code management, release management, project management, work items tracking, agile, scrum, kanban, collaboration), `twitter:site=@planepowers` | `ADM/app/root.tsx` Z. 24–27, 61–73 |
| `/` | `Admin – Instance Setup & Sign-In` | `description`: „Configure your Plane instance or sign in to the admin portal.“ | `ADM/app/(all)/(home)/page.tsx` Z. 47–50 |
| `/general/` | `General Settings - God Mode` | – | `.../general/page.tsx` |
| `/email/` | `Email Settings - God Mode` | – | `.../email/page.tsx` |
| `/authentication/` | `Authentication Settings - Plane Web` (sic, abweichendes Suffix) | – | `.../authentication/page.tsx` Z. 176 |
| `/authentication/github/` | `GitHub Authentication - God Mode` | – | `.../github/page.tsx` |
| `/authentication/gitlab/` | `GitLab Authentication - God Mode` | – | `.../gitlab/page.tsx` |
| `/authentication/google/` | `Google Authentication - God Mode` | – | `.../google/page.tsx` |
| `/authentication/gitea/` | `Gitea Authentication - God Mode` | – | `.../gitea/page.tsx` |
| `/ai/` | `Artificial Intelligence Settings - God Mode` | – | `.../ai/page.tsx` |
| `/image/` | `Images Settings - God Mode` | – | `.../image/page.tsx` |
| `/workspace/` | `Workspace Management - God Mode` | – | `.../workspace/page.tsx` |
| `/workspace/create/` | `Create Workspace - God Mode` | – | `.../workspace/create/page.tsx` |

Head-Links (alle Seiten): `apple-touch-icon` 180×180, `icon` 32×32 & 16×16 PNG, `shortcut icon` `.ico`, `manifest` `/site.webmanifest.json` (absolut ab Origin, **nicht** unter Base-Path!), Stylesheet `globals.css`, Font-Preload `inter-latin-wght-normal.woff2` (`crossOrigin=anonymous`). `<html lang="en">`, `<body class="antialiased">`. Quelle: `ADM/app/root.tsx` Z. 28–59. Manifest-Inhalt: Name/Short-Name „Plane God Mode“, `background_color #f9fafb`, `theme_color #ffffff`, Icons `android-chrome-192x192.png`/`512x512.png` (`ADM/public/site.webmanifest.json`).

### 2.3 Admin – Dateiinventar (Quellcode & Konfiguration)

| Datei | Typ | Inhalt / Verantwortung |
|---|---|---|
| `ADM/app/root.tsx` | Root-Route | HTML-Layout, Head-Links, Fonts (`@fontsource-variable/inter`, `@fontsource/material-symbols-rounded`, `@fontsource/ibm-plex-mono`), `AppProviders`, `<div class="min-h-screen bg-canvas"><Outlet/></div>`, `HydrateFallback` (zentrierter `LogoSpinner`), `ErrorBoundary` (`<p>Something went wrong.</p>`) |
| `ADM/app/routes.ts` | Routing | Route-Konfiguration (2.1) |
| `ADM/app/entry.client.tsx` | Bootstrap | `hydrateRoot(document, <StrictMode><HydratedRouter/></StrictMode>)` in `startTransition` |
| `ADM/app/compat/next/helper.ts` | Util | `ensureTrailingSlash(url)` – hängt `/` an Pfad (nicht an `/`), bewahrt Query/Hash, relative bleiben relativ |
| `ADM/app/compat/next/link.tsx` | Shim | `next/link`-Ersatz → `react-router` `Link` mit `ensureTrailingSlash(href)`; ignoriert `prefetch`, `scroll`, `shallow` |
| `ADM/app/compat/next/navigation.ts` | Shim | `useRouter()` (`push`, `replace` mit Trailing-Slash, `back`, `forward`, `refresh`=`location.reload()`, `prefetch` no-op), `usePathname()`, `useSearchParams()` |
| `ADM/app/types/next-link.d.ts`, `next-navigation.d.ts`, `react-router-virtual.d.ts` | Typen | Typdeklarationen der Shims |
| `ADM/app/components/404.tsx` | Seite | 404-Ansicht (Bild `404.svg` 240/320 px, „Oops! Something went wrong.“, Text, Button) |
| `ADM/app/(all)/(home)/layout.tsx` | Layout | Vollbild-Container `relative z-10 flex h-screen w-screen flex-col items-center overflow-hidden overflow-y-auto bg-surface-1 px-8 pt-6 pb-10`; Redirect eingeloggt → `/general` |
| `ADM/app/(all)/(home)/page.tsx` | Seite | Weiche Spinner / `InstanceFailureView` / `InstanceSetupForm` / `InstanceSignInForm` |
| `ADM/app/(all)/(home)/sign-in-form.tsx` | Formular | Admin-Login (native POST) |
| `ADM/app/(all)/(home)/auth-header.tsx` | Komponente | Sticky Header mit `PlaneLockup` (95×20, `text-primary`), Link `/` |
| `ADM/app/(all)/(home)/auth-banner.tsx` | Komponente | Info-Banner (Accent-Farben) mit Schließen-Button (`aria-label="Dismiss banner"`) |
| `ADM/app/(all)/(home)/auth-helpers.tsx` | Logik | `EErrorAlertType`, Mapping Admin-Fehlercodes → Titel/Nachricht, `authErrorHandler()` |
| `ADM/app/(all)/(dashboard)/layout.tsx` | Layout | Guard, Spinner, Shell: `AdminSidebar` + `<main>` (`AdminHeader` + scrollbarer Outlet) + `NewUserPopup` |
| `ADM/app/(all)/(dashboard)/sidebar.tsx` | Komponente | Sidebar-Container, Responsiveness, Outside-Click |
| `ADM/app/(all)/(dashboard)/sidebar-dropdown.tsx` | Komponente | Kopfzeile „Instance admin“ + Menüs (E-Mail, Theme-Wechsel, Sign-out) + verstecktes Sign-out-Formular |
| `ADM/app/(all)/(dashboard)/sidebar-menu.tsx` | Komponente | Navigationseinträge (2.4) mit Aktiv-Logik und Tooltips im eingeklappten Zustand |
| `ADM/app/(all)/(dashboard)/sidebar-help-section.tsx` | Komponente | Fußzeile: „Redirect to Plane“, Hilfe-Popover (Docs/Forum/Bug + Version), Sidebar-Toggle |
| `ADM/app/(all)/(dashboard)/general/page.tsx` + `form.tsx` | Seite/Form | Instanzname, Admin-E-Mail (read-only), Instance-ID (read-only), Telemetrie-Switch |
| `ADM/app/(all)/(dashboard)/email/page.tsx` | Seite | SMTP-Ein/Aus-Switch im Header, Formular nur bei aktivem SMTP |
| `ADM/app/(all)/(dashboard)/email/email-config-form.tsx` | Form | SMTP-Felder, Security-Select, Speichern, „Send test email“ |
| `ADM/app/(all)/(dashboard)/email/test-email-modal.tsx` | Dialog | 3-Schritt-Dialog (Senden/Erfolg/Fehler) |
| `ADM/app/(all)/(dashboard)/authentication/page.tsx` | Seite | Sign-up-Switch + Liste der 6 Auth-Methoden-Karten, Validierung „mind. eine Methode aktiv“ |
| `ADM/app/(all)/(dashboard)/authentication/{github,gitlab,google,gitea}/page.tsx` | Seite | Provider-Kopfkarte mit Aktiv-Switch + Formular |
| `ADM/app/(all)/(dashboard)/authentication/{github,gitlab,google,gitea}/form.tsx` | Form | Provider-Credentials, „Refresh user attributes…“-Switch, Copy-Felder (Origin/Callback) |
| `ADM/app/(all)/(dashboard)/ai/page.tsx` + `form.tsx` | Seite/Form | `LLM_MODEL`, `LLM_API_KEY` |
| `ADM/app/(all)/(dashboard)/image/page.tsx` + `form.tsx` | Seite/Form | `UNSPLASH_ACCESS_KEY` |
| `ADM/app/(all)/(dashboard)/workspace/page.tsx` | Seite | Switch „Prevent anyone else from creating a workspace.“, Workspace-Liste, „Load more“ |
| `ADM/app/(all)/(dashboard)/workspace/create/page.tsx` + `form.tsx` | Seite/Form | Workspace-Anlage (Name, Slug/URL, Größe) |
| `ADM/components/authentication/authentication-method-card.tsx` | Komponente | Karte (Icon im Kreis, Name, Beschreibung, Config-Slot), Varianten `withBorder`, `unavailable`, `disabled` |
| `ADM/components/authentication/email-config-switch.tsx` | Komponente | Switch `ENABLE_MAGIC_LINK_LOGIN` |
| `ADM/components/authentication/password-config-switch.tsx` | Komponente | Switch `ENABLE_EMAIL_PASSWORD` |
| `ADM/components/authentication/{github,gitlab,google,gitea}-config.tsx` | Komponente | „Configure“-Button (nicht konfiguriert) bzw. „Edit“ + Switch (konfiguriert) |
| `ADM/components/common/banner.tsx` | Komponente | Erfolg/Fehler-Banner (TickCircle/WarningCircle) |
| `ADM/components/common/code-block.tsx` | Komponente | Inline-Code-Chip (`darkerShade`-Variante) |
| `ADM/components/common/confirm-discard-modal.tsx` | Dialog | `ConfirmDialog` „You have unsaved changes“ |
| `ADM/components/common/controller-input.tsx` | Form-Baustein | Gelabeltes Input (text/password mit Auge-Toggle), Pflichtregel `"{label} is required."`, Beschreibung |
| `ADM/components/common/controller-switch.tsx` | Form-Baustein | „Refresh user attributes from {label} during sign in“ + Switch (`"0"/"1"`-Strings) |
| `ADM/components/common/copy-field.tsx` | Komponente | Label + Button mit URL-Text und Copy-Icon, Toast „Copied to clipboard“ |
| `ADM/components/common/header/index.tsx` | Komponente | `AdminHeader` (Breadcrumb) + `HamburgerToggle` (nur < md) |
| `ADM/components/common/header/core.ts` | Daten | Segment-Labels (2.5) |
| `ADM/components/common/header/extended.ts` | Erweiterungspunkt | leer `{}` |
| `ADM/components/common/logo-spinner.tsx` | Komponente | GIF-Spinner (dark: `logo-spinner-light.gif`, sonst `logo-spinner-dark.gif`), `h-6 sm:h-11` |
| `ADM/components/common/new-user-popup.tsx` | Komponente | Hinweis-Karte „Create workspace“ unten rechts |
| `ADM/components/common/page-wrapper.tsx` | Layout | Seitenrahmen mit Header (Titel/Beschreibung/Actions) oder `customHeader`, Größen `md`/`lg` |
| `ADM/components/common/password-strength-indicator.tsx` | Komponente | 3-Segment-Stärkebalken + Kriterienliste |
| `ADM/components/common/plane-lockup.tsx` | Komponente | Inline-SVG Plane-Logo-Lockup (viewBox 0 0 253 53) |
| `ADM/components/common/skeleton.tsx` | Komponente | `Skeleton` + `Skeleton.Item` (animate-pulse, `bg-layer-1`, `role=status`, `aria-label="Loading content"`) |
| `ADM/components/instance/failure.tsx` | Komponente | „Unable to fetch instance details.“ + Retry |
| `ADM/components/instance/form-header.tsx` | Komponente | Überschrift (`text-20 semibold`) + Unterzeile (`text-16 semibold text-placeholder`) |
| `ADM/components/instance/setup-form.tsx` | Formular | Erst-Einrichtung (native POST) |
| `ADM/components/workspace/list-item.tsx` | Komponente | Workspace-Zeile (Logo/Initiale, Name, `[slug]`, Owner, Projekte, Mitglieder, New-Tab-Icon) |
| `ADM/helpers/authentication.ts` | Logik | `canDisableAuthMethod()` |
| `ADM/hooks/oauth/core.tsx` | Daten | `getCoreAuthenticationModesMap()` (6 Methoden) |
| `ADM/hooks/oauth/index.ts` | Hook | `useAuthenticationModes()` – feste Reihenfolge |
| `ADM/hooks/oauth/types.ts` | Typen | `TGetAuthenticationModeProps` |
| `ADM/hooks/store/{index,use-instance,use-theme,use-user,use-workspace}.ts(x)` | Hooks | Kontextzugriff auf Stores (Fehler „… must be used within StoreProvider“) |
| `ADM/hooks/use-sidebar-menu/{core,index,types}.ts` | Daten/Hook | Sidebar-Einträge (2.4) |
| `ADM/lib/b-progress/{AppProgressBar,index}.tsx` | Komponente | Top-Progressbar bei Router-Navigation (`@bprogress/core`) |
| `ADM/providers/{index,core,extended}.tsx` | Provider | Provider-Kette (3.1) |
| `ADM/providers/instance.provider.tsx` | Provider | SWR `INSTANCE_DETAILS` → `fetchInstanceInfo` |
| `ADM/providers/user.provider.tsx` | Provider | SWR `CURRENT_USER`, `INSTANCE_ADMINS`, Sidebar-Zustand aus `localStorage` |
| `ADM/providers/store-context.ts`, `store.provider.tsx` | Provider | Singleton `RootStore`, React-Context |
| `ADM/store/{root,instance,theme,user,workspace}.store.ts` | Stores | MobX-Stores (2.6) |
| `ADM/styles/globals.css` | Styles | Import `@plane/tailwind-config/index.css` + `@makeplane/propel/styles`, `.shadow-custom`, `.backdrop-blur-custom`, `.progress-bar`, BProgress-Variablen (`--bprogress-color: var(--background-color-accent-primary)`, Höhe 2.5px, Gradient 80→100 %, Peg-Schatten) |
| `ADM/caddy/Caddyfile`, `ADM/Dockerfile.admin`, `ADM/Dockerfile.dev`, `ADM/.dockerignore`, `ADM/.prettierignore` | Betrieb | 1.1 |
| `ADM/.env.example` | Konfig | `VITE_API_BASE_URL=http://localhost:8000`, `VITE_WEB_BASE_URL=http://localhost:3000`, `VITE_ADMIN_BASE_URL=http://localhost:3001`, `VITE_ADMIN_BASE_PATH=/god-mode`, `VITE_SPACE_BASE_URL=http://localhost:3002`, `VITE_SPACE_BASE_PATH=/spaces`, `VITE_LIVE_BASE_URL=http://localhost:3100`, `VITE_LIVE_BASE_PATH=/live` |
| `ADM/react-router.config.ts`, `ADM/vite.config.ts`, `ADM/tsconfig.json`, `ADM/postcss.config.js`, `ADM/package.json` | Build | 2.29 |
| `ADM/public/site.webmanifest.json`, `ADM/public/favicon/android-chrome-{192x192,512x512}.png`, `ADM/public/.well-known/appspecific/com.chrome.devtools.json` (`{}`) | Statisch | Manifest/Icons |

### 2.4 Admin – Sidebar-Menü (Reihenfolge = Anzeige)

Reihenfolge aus `ADM/hooks/use-sidebar-menu/index.ts`; Daten aus `ADM/hooks/use-sidebar-menu/core.ts`.

| # | Key | Icon | Name | Beschreibung (2. Zeile) | href |
|---|---|---|---|---|---|
| 1 | `general` | `SettingsOutline` (Propel) | General | Identify your instances and get key details. | `/general/` |
| 2 | `email` | `MailOutline` (Propel) | Email | Configure your SMTP controls. | `/email/` |
| 3 | `authentication` | `LockOutline` (Propel) | Authentication | Configure authentication modes. | `/authentication/` |
| 4 | `workspace` | `WorkspaceOutline` (Propel) | Workspaces | Manage all workspaces on this instance. | `/workspace/` |
| 5 | `ai` | `BrainCog` (**lucide-react**) | Artificial intelligence | Configure your OpenAI creds. | `/ai/` |
| 6 | `image` | `ImageOutline` (Propel) | Images in Plane | Allow third-party image libraries. | `/image/` |

Aktiv-Regel: `item.href === pathName || pathName.startsWith(item.href)` (`ADM/app/(all)/(dashboard)/sidebar-menu.tsx` Z. 34). Styling aktiv: `!bg-layer-transparent-active text-primary`; inaktiv: `text-secondary hover:bg-layer-transparent-hover active:bg-layer-transparent-active`; Zeile `rounded-md px-3 py-2 gap-3`, ausgeklappt `w-[260px]`; Name `text-body-xs-medium`, Beschreibung `text-caption-sm-regular`; eingeklappt nur Icon (16 px) + Tooltip rechts mit Name.

### 2.5 Admin – Breadcrumb-Segment-Labels

`ADM/components/common/header/core.ts` (zusammengeführt mit leerem `extended.ts`):

| Segment | Label |
|---|---|
| `general` | General |
| `ai` | Artificial Intelligence |
| `email` | Email |
| `authentication` | Authentication |
| `image` | Image |
| `google` | Google |
| `github` | GitHub |
| `gitlab` | GitLab |
| `gitea` | Gitea |
| `workspace` | Workspace |
| `create` | Create |
| (unbekannt) | `segment.toUpperCase()` |

Erstes Element ist immer „Settings“ (Icon `SettingsOutline`, Tint `tertiary`, Link `/general/`), danach je Segment Separator + Link; letztes Segment als `BreadcrumbPage` (nicht klickbar). Algorithmus: `pathname.split("/").slice(1)`, dann **letztes Element entfernen** (`pop()`), da Pfade mit `/` enden (`ADM/components/common/header/index.tsx` Z. 50–62).

### 2.6 Admin – Stores (MobX)

`RootStore` (`ADM/store/root.store.ts`) instanziiert `theme`, `instance`, `user`, `workspace` (Reihenfolge Theme → Instance → User → Workspace); `hydrate(initialData)` ruft alle `hydrate`; `resetOnSignOut()` setzt `localStorage.theme="system"` und erzeugt **alle vier Stores neu**. `enableStaticRendering(typeof window === "undefined")`.

**InstanceStore** (`ADM/store/instance.store.ts`)

| Mitglied | Art | Default | Beschreibung |
|---|---|---|---|
| `isLoading` | observable.ref | `true` | Ladezustand Instanzinfo |
| `error` | observable.ref | `undefined` | `{ message: "Failed to fetch the instance info" }` bei Fehler |
| `instanceStatus` | observable | `undefined` | `{ status: EInstanceStatus.ERROR }` bei Fehler (`CONST/instance.ts`: `ERROR`, `NOT_YET_READY`) |
| `instance` | observable | `undefined` | `IInstance` aus `GET /api/instances/` → `.instance` |
| `config` | **nicht observable** (fehlt in `makeObservable`) | `undefined` | `IInstanceConfig` aus `.config` |
| `instanceAdmins` | observable | `undefined` | `IInstanceAdmin[]` |
| `instanceConfigurations` | observable | `undefined` | `IInstanceConfiguration[]` (Key/Value-Liste) |
| `formattedConfig` | computed | – | `Record<key, value>` aus `instanceConfigurations`; `undefined` solange nicht geladen |
| `hydrate(data)` | action | – | setzt `instance`, `config` |
| `fetchInstanceInfo()` | action | – | `isLoading=true` nur beim ersten Mal; `error=undefined`; ruft `InstanceService.info()`; **beim ersten Laden** und `!instance.workspaces_exist` → `theme.toggleNewUserPopup()`; Fehler → `isLoading=false`, `error`, `instanceStatus`, rethrow |
| `updateInstanceInfo(data)` | action | – | `PATCH /api/instances/`; Antwort wird per `set(this.instance, "instance", response)` **als verschachteltes Feld `instance.instance`** abgelegt (Bug: Top-Level-Felder werden nicht aktualisiert) |
| `fetchInstanceAdmins()` | action | – | `GET /api/instances/admins/` |
| `fetchInstanceConfigurations()` | action | – | `GET /api/instances/configurations/` |
| `updateInstanceConfigurations(data)` | action | – | `PATCH /api/instances/configurations/`; ersetzt passende Einträge in `instanceConfigurations` durch Antwort-Einträge; gibt Antwortliste zurück |
| `disableEmail()` | (nicht als action registriert) | – | Optimistisch: setzt Werte von `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `EMAIL_FROM`, `ENABLE_SMTP` auf `""`, dann `DELETE /api/instances/configurations/disable-email-feature/`; bei Fehler Rollback, **kein Rethrow** (Fehler-Toast der Seite wird daher nie ausgelöst) |

**ThemeStore** (`ADM/store/theme.store.ts`)

| Mitglied | Art | Default | Beschreibung |
|---|---|---|---|
| `isNewUserPopup` | observable.ref | `false` | Sichtbarkeit `NewUserPopup` |
| `isSidebarCollapsed` | observable.ref | `undefined` | Sidebar eingeklappt |
| `theme` | observable.ref | `undefined` | wird nur über `hydrate`/`setTheme` gesetzt (UI nutzt next-themes direkt) |
| `toggleNewUserPopup()` | action | – | invertiert |
| `toggleSidebar(collapsed)` | action | – | setzt Wert (bei `undefined` invertiert), schreibt `localStorage["god_mode_sidebar_collapsed"] = String(collapsed)` |
| `setTheme(theme)` | action | – | `localStorage["theme"]=theme`; in UI ungenutzt |

**UserStore** (`ADM/store/user.store.ts`)

| Mitglied | Art | Default | Beschreibung |
|---|---|---|---|
| `isLoading` | observable.ref | `true` | |
| `userStatus` | observable | `undefined` | `{status: EUserStatus.AUTHENTICATION_NOT_DONE \| ERROR, message}` (`CONST/user.ts`) |
| `isUserLoggedIn` | observable.ref | `undefined` | Tri-State: `undefined` = unbekannt (Spinner), `true`, `false` |
| `currentUser` | observable | `undefined` | `IUser` aus `GET /api/instances/admins/me/` |
| `fetchCurrentUser()` | action | – | lädt Admin-„me“; bei Erfolg zusätzlich `instance.fetchInstanceAdmins()`, dann `isUserLoggedIn=true`; leere Antwort → `false`; Fehler → `false`, `userStatus` (403-Zweig greift praktisch nie, da Service nur `response.data` wirft), rethrow |
| `reset()` | action | – | alles zurücksetzen |
| `signOut()` | action | – | `store.resetOnSignOut()` |

**WorkspaceStore** (`ADM/store/workspace.store.ts`)

| Mitglied | Art | Default | Beschreibung |
|---|---|---|---|
| `loader` | observable | `"init-loader"` | `TLoader`: `init-loader` \| `mutation` \| `pagination` \| `loaded` |
| `workspaces` | observable | `{}` | Map `id → IWorkspace` (Einfügereihenfolge = Anzeigereihenfolge) |
| `paginationInfo` | observable | `undefined` | alle Felder der Paginierungsantwort außer `results` |
| `workspaceIds` | computed | – | `Object.keys(workspaces)` |
| `getWorkspaceById(id)` | action | – | |
| `fetchWorkspaces()` | action | – | `loader = mutation` (wenn bereits Daten) sonst `init-loader`; `GET /api/instances/workspaces/` (ohne Cursor); merged in Map; `finally loader="loaded"` |
| `fetchNextWorkspaces()` | action | – | nur wenn `paginationInfo.next_page_results !== false`; `loader="pagination"`; `GET …?cursor=<next_cursor>` |
| `createWorkspace(data)` | action | – | `loader="mutation"`; `POST /api/instances/workspaces/`; fügt Ergebnis ein |

### 2.7 Admin – API-Aufrufe (vollständig)

Basis-URL: `API_BASE_URL = process.env.VITE_API_BASE_URL || ""` (leer = gleiche Origin). Alle Axios-Requests: `withCredentials: true`; Request-Interceptor ergänzt **immer einen abschließenden Slash** am Pfad (außer fremde absolute URLs) (`SVC/api.service.ts`, `SVC/helpers/url.ts`). Native Form-POSTs gehen direkt an `${API_BASE_URL}/...`.

| # | Methode & Pfad | Aufrufer (Service → Store/Komponente) | Request | Response (verwendet) | Backend & Berechtigung |
|---|---|---|---|---|---|
| A1 | `GET /auth/get-csrf-token/` | `AuthService.requestCSRFToken` → Sign-in-Form, Setup-Form, Sidebar-Dropdown (Sign-out) | – (`validateStatus: null`) | `{ csrf_token }` | Auth-App, AllowAny |
| A2 | `GET /api/instances/` | `InstanceService.info` → `InstanceStore.fetchInstanceInfo` (SWR `INSTANCE_DETAILS`) | – (`validateStatus: null`) | `{ instance: IInstance & {workspaces_exist}, config: IInstanceConfig }`; ohne Instanz-Datensatz `{is_activated:false,is_setup_done:false}` | `InstanceEndpoint.get`, AllowAny, Server-Cache 2 h + `Cache-Control: private, max-age=12` (`API/license/api/views/instance.py`) |
| A3 | `PATCH /api/instances/` | `InstanceService.update` → `updateInstanceInfo` (General-Form) | `{ instance_name, is_telemetry_enabled }` | `IInstance` | `InstanceAdminPermission`; read-only: `id, email, last_checked_at, is_setup_done` |
| A4 | `GET /api/instances/admins/` | `InstanceService.admins` → `fetchInstanceAdmins` (SWR `INSTANCE_ADMINS` + in `fetchCurrentUser`) | – (`validateStatus: null`) | `IInstanceAdmin[]` (inkl. `user_detail`) | `InstanceAdminPermission`, Cache 2 h |
| A5 | `GET /api/instances/admins/me/` | `UserService.adminDetails` → `fetchCurrentUser` (SWR `CURRENT_USER`) | – | `IUser`-Teilmenge: `id, avatar, avatar_url, cover_image, date_joined, display_name, email, first_name, last_name, is_active, is_bot, is_email_verified, user_timezone, username, is_password_autoset` | `InstanceAdminUserMeEndpoint`, `InstanceAdminPermission` (`API/license/api/serializers/admin.py`) |
| A6 | `GET /api/instances/configurations/` | `InstanceService.configurations` → `fetchInstanceConfigurations` (SWR `INSTANCE_CONFIGURATIONS`) | – | `IInstanceConfiguration[]`: `{id, key, value (verschlüsselte Werte entschlüsselt!), category, is_encrypted, created_at, updated_at, created_by, updated_by, deleted_at}` | `InstanceAdminPermission`, Cache 2 h |
| A7 | `PATCH /api/instances/configurations/` | `InstanceService.updateConfigurations` → `updateInstanceConfigurations` (alle Formulare/Switches) | `{ <KEY>: "<value>", … }` | Liste **nur der aktualisierten** Konfigurationen | Nur existierende Keys werden aktualisiert; Wert `str().strip()`, `None`→`""`; `is_encrypted` → verschlüsselt gespeichert; invalidiert Cache `/api/instances/configurations/` und `/api/instances/` |
| A8 | `DELETE /api/instances/configurations/disable-email-feature/` | `InstanceService.disableEmail` → `InstanceStore.disableEmail` | – | 200 leer | Setzt `ENABLE_SMTP="0"`, `EMAIL_HOST`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `EMAIL_PORT`, `EMAIL_FROM` = `""` (`EMAIL_USE_TLS/SSL` unverändert) |
| A9 | `POST /api/instances/email-credentials-check/` | `InstanceService.sendTestEmail` → `SendTestEmailModal` | `{ receiver_email }` | 200 `{message:"Email successfully sent."}`; 400 `{error:"…"}` (Texte 3.8) | `EmailCredentialCheckEndpoint`, Default-Permission `InstanceAdminPermission`; Betreff „Email Notification from Plane“, Text „This is a sample email notification sent from Plane application.“ |
| A10 | `GET /api/instances/workspaces/?cursor=…` | `InstanceWorkspaceService.list` → `fetchWorkspaces`/`fetchNextWorkspaces` (SWR `INSTANCE_WORKSPACES`) | `cursor` (optional), Backend unterstützt zusätzlich `search` (UI nutzt es nicht) | `TWorkspacePaginationInfo`: `{results: IWorkspace[] (mit owner{id,email,first_name,last_name}, logo_url, total_projects, total_members), next_cursor, prev_cursor, next_page_results, prev_page_results, count, total_pages, total_results, extra_stats}`; 10 pro Seite (max 10) | `InstanceWorkSpaceEndpoint.get`; Mitglieder zählen nur aktive Nicht-Bots |
| A11 | `GET /api/instances/workspace-slug-check/?slug=<slug>` | `InstanceWorkspaceService.slugCheck` → Create-Form | `slug` | `{ status: true }` = verfügbar | case-insensitive + `RESTRICTED_WORKSPACE_SLUGS` |
| A12 | `POST /api/instances/workspaces/` | `InstanceWorkspaceService.create` → `createWorkspace` | `IWorkspace`-Formdaten `{name, slug, organization_size}` | `IWorkspace` (201) | Validierung Name (keine URL, mind. ein alphanumerisches Zeichen), max Name 80/Slug 48; legt `WorkspaceMember(role=20)` für den Admin an; 409 bei Slug-Konflikt |
| F1 | **Form-POST** `/api/instances/admins/sign-in/` | `InstanceSignInForm` | `application/x-www-form-urlencoded`: `csrfmiddlewaretoken`, `email`, `password` | 302 → `/god-mode/general/` oder `/god-mode/?error_code…` | `InstanceAdminSignInEndpoint` (Django `View`), Throttle |
| F2 | **Form-POST** `/api/instances/admins/sign-up/` | `InstanceSetupForm` | `csrfmiddlewaretoken`, `is_telemetry_enabled` (`"True"`/`"False"`), `first_name`, `last_name`, `email`, `company_name`, `password`, `confirm_password` | 302 → `/god-mode/general/` oder Fehler-Redirect | `InstanceAdminSignUpEndpoint`, atomarer Check (Row-Lock) |
| F3 | **Form-POST** `/api/instances/admins/sign-out/` | `AdminSidebarDropdown` | `csrfmiddlewaretoken` | 302 → `/god-mode/` | `InstanceAdminSignOutEndpoint` |

Nicht genutzte Admin-Endpunkte (Backend vorhanden, keine UI): `GET /api/instances/admins/session/` (`InstanceAdminUserSessionEndpoint`), `POST /api/instances/admins/` (weiteren Admin anlegen), `DELETE /api/instances/admins/<uuid>/`, `POST /api/instances/admins/sign-up-screen-visited/`, `GET /api/instances/changelog/` (`SVC/instance/instance.service.ts` `changelog()`) (`API/license/urls.py`).

### 2.8 Admin – Instanz-Konfigurationsschlüssel (vollständig)

Quelle Seed/Defaults: `API/utils/instance_config_variables/core.py` (beim Kommando `configure_instance` einmalig angelegt, `API/license/management/commands/configure_instance.py`); `extended.py` ist leer. UI-Typen: `TYPES/instance/{ai,auth,email,image,workspace}.ts`. Alle Werte sind **Strings**; Booleans als `"0"`/`"1"`.

| Key | Kategorie | verschlüsselt | Seed-Default (ENV, Default) | UI-Ort | Hinweis |
|---|---|---|---|---|---|
| `ENABLE_SIGNUP` | AUTHENTICATION | nein | `ENABLE_SIGNUP`, `"1"` | `/authentication/` Switch „Allow anyone to sign up even without an invite“ | `GET /api/instances/` nutzt Fallback `"0"` falls Key fehlt |
| `ENABLE_EMAIL_PASSWORD` | AUTHENTICATION | nein | `"1"` | `/authentication/` Karte „Passwords“ | |
| `ENABLE_MAGIC_LINK_LOGIN` | AUTHENTICATION | nein | `"0"` | `/authentication/` Karte „Unique codes“ | Fallback in `GET /api/instances/` `"1"` (inkonsistent zum Seed) |
| `DISABLE_WORKSPACE_CREATION` | WORKSPACE_MANAGEMENT | nein | `"0"` | `/workspace/` Switch | |
| `IS_GOOGLE_ENABLED` | GOOGLE | nein | `"0"` | `/authentication/` & `/authentication/google/` | |
| `GOOGLE_CLIENT_ID` | GOOGLE | nein | – | Google-Form | |
| `GOOGLE_CLIENT_SECRET` | GOOGLE | **ja** | – | Google-Form | |
| `ENABLE_GOOGLE_SYNC` | GOOGLE | nein | `"0"` | Google-Form Switch „Refresh user attributes from Google during sign in“ | |
| `IS_GITHUB_ENABLED` | GITHUB | nein | `"0"` | `/authentication/` & `/authentication/github/` | |
| `GITHUB_CLIENT_ID` | GITHUB | nein | – | GitHub-Form | |
| `GITHUB_CLIENT_SECRET` | GITHUB | **ja** | – | GitHub-Form | |
| `GITHUB_ORGANIZATION_ID` | GITHUB | nein | – | GitHub-Form (optional) | |
| `ENABLE_GITHUB_SYNC` | GITHUB | nein | `"0"` | GitHub-Form Switch | |
| `IS_GITLAB_ENABLED` | GITLAB | nein | `"0"` | `/authentication/` & `/authentication/gitlab/` | |
| `GITLAB_HOST` | GITLAB | nein | – | GitLab-Form | |
| `GITLAB_CLIENT_ID` | GITLAB | nein | – | GitLab-Form („Application ID“) | |
| `GITLAB_CLIENT_SECRET` | GITLAB | **ja** | – | GitLab-Form („Secret“) | |
| `ENABLE_GITLAB_SYNC` | GITLAB | nein | `"0"` | GitLab-Form Switch | |
| `IS_GITEA_ENABLED` | GITEA | nein | `"0"` | `/authentication/` & `/authentication/gitea/` | |
| `GITEA_HOST` | GITEA | nein | – | Gitea-Form („Gitea Host“, UI-Default `https://gitea.com`) | |
| `GITEA_CLIENT_ID` | GITEA | nein | – | Gitea-Form | |
| `GITEA_CLIENT_SECRET` | GITEA | **ja** | – | Gitea-Form | |
| `ENABLE_GITEA_SYNC` | GITEA | nein | `"0"` | Gitea-Form Switch | |
| `ENABLE_SMTP` | SMTP | nein | `"0"` | `/email/` Header-Switch; beim Speichern wird **immer** `"1"` gesendet | |
| `EMAIL_HOST` | SMTP | nein | `""` | Email-Form „Host“ | `is_smtp_configured` in `GET /api/instances/` = `bool(EMAIL_HOST)` |
| `EMAIL_HOST_USER` | SMTP | nein | `""` | Email-Form „Username“ | |
| `EMAIL_HOST_PASSWORD` | SMTP | **ja** | `""` | Email-Form „Password“ | |
| `EMAIL_PORT` | SMTP | nein | `"587"` | Email-Form „Port“ | |
| `EMAIL_FROM` | SMTP | nein | `""` | Email-Form „Sender's email address“ | |
| `EMAIL_USE_TLS` | SMTP | nein | `"1"` | Email-Form Select „Email security“ (TLS) | |
| `EMAIL_USE_SSL` | SMTP | nein | `"0"` | Email-Form Select (SSL) | |
| `LLM_API_KEY` | AI | **ja** | – | `/ai/` „API key“ | `has_llm_configured` = `bool(LLM_API_KEY)` |
| `LLM_PROVIDER` | AI | nein | `"openai"` | **keine UI** | |
| `LLM_MODEL` | AI | nein | `"gpt-4o-mini"` | `/ai/` „LLM Model“ | |
| `GPT_ENGINE` | AI | nein | `"gpt-3.5-turbo"` | **keine UI** (deprecated) | |
| `UNSPLASH_ACCESS_KEY` | UNSPLASH | **ja** | `""` | `/image/` | `has_unsplash_configured` |

Zusätzliche, nur lesend in `GET /api/instances/` → `config` ausgewertete Schlüssel/ENV: `GITHUB_APP_NAME`, `SLACK_CLIENT_ID` (beide ohne God-Mode-UI), `FILE_SIZE_LIMIT` (ENV, Default 5242880), `ADMIN_BASE_URL`, `SPACE_BASE_URL`, `APP_BASE_URL`, `INSTANCE_CHANGELOG_URL`, `IS_SELF_MANAGED` (`API/license/api/views/instance.py`).

`IInstanceConfig` (Antwortfeld `config`, `TYPES/instance/base.ts`): `enable_signup`, `is_workspace_creation_disabled`, `is_google_enabled`, `is_github_enabled`, `is_gitlab_enabled`, `is_gitea_enabled`, `is_magic_login_enabled`, `is_email_password_enabled`, `github_app_name`, `slack_client_id`, `has_unsplash_configured`, `has_llm_configured`, `file_size_limit`, `is_smtp_configured`, `app_base_url`, `space_base_url`, `admin_base_url`, `is_self_managed`, `instance_changelog_url`.

`IInstance` (Antwortfeld `instance`, `TYPES/instance/base.ts`, Backend `fields="__all__"` + `primary_owner_details`, `workspaces_exist`): `id, created_at, updated_at, instance_name, whitelist_emails, instance_id, license_key (nur Typ), current_version, latest_version, last_checked_at, namespace, is_telemetry_enabled, is_support_required, is_activated, is_setup_done, is_signup_screen_visited, user_count (nur Typ), is_verified, created_by, updated_by, workspaces_exist`; Backend liefert zusätzlich `edition`, `domain`, `is_test`, `is_current_version_deprecated`, `deleted_at` (`API/license/models/instance.py`). **Achtung:** In `InstanceEndpoint.get` wird `data["is_activated"]=True` gesetzt, die Antwort enthält aber `instance_data = serializer.data` neu – `is_activated` fehlt daher im `instance`-Objekt der Antwort.

### 2.9 Admin – Formularfelder je Seite (vollständig)

Gemeinsame Bausteine: `ControllerInput` (Label `text-13 text-tertiary`, `InputGroup size="lg"`, `Input size="lg"`, bei `type="password"` Auge-Button `aria-label="Show password"`/`"Hide password"`, Beschreibung `pt-0.5 text-11 text-tertiary`, Pflichtregel `"<Label> is required."` – die Fehlermeldung selbst wird **nicht** angezeigt, nur `aria-invalid`) – `ADM/components/common/controller-input.tsx`.

**F-Setup – Instanz-Einrichtung** (`ADM/components/instance/setup-form.tsx`), Überschrift „Setup your Plane Instance“ / „Post setup you will be able to manage this Plane instance.“, Container `max-w-[22.5rem]`:

| Feld (`name`) | Label | Typ | Placeholder | Pflicht-Stern | Clientseitige Regel | Vorbelegung aus Query |
|---|---|---|---|---|---|---|
| `first_name` | First name | text, `autoFocus`, `maxLength=50` | Wilber | ja | Eingabe wird verworfen, wenn `validatePersonName` ≠ `true` (außer leer) – Regex `^[\p{L}\s'-]+$`, ≤ 50, keine Zeichen `< > ' " { } [ ] * ^ ! # %` | `first_name` |
| `last_name` | Last name | text, `maxLength=50` | Wright | ja (nur optisch, nicht erforderlich) | wie first_name | `last_name` |
| `email` | Email | email | name@company.com | ja | – | `email` |
| `company_name` | Company name | text, `maxLength=80` | Company name | ja (nur optisch) | `validateCompanyName(v,false)`: ≤ 80, Regex `^[\p{L}\p{N}\s_-]+$`, mind. 1 alphanumerisches Zeichen | **`company`** (Backend sendet `company_name` → Vorbelegung greift nie) |
| `password` | Set a password | password + Auge, `autoComplete=new-password` | New password | ja | Stärke muss `STRENGTH_VALID` sein (≥ 8 Zeichen, Groß-, Kleinbuchstabe, Ziffer, Sonderzeichen aus `!@#$%^&*()-_+=[]{}\|;:'",.<>?/`) | – |
| `confirm_password` | Confirm password | password + Auge | Confirm password | ja | muss gleich `password` sein; Fehlertext „Passwords don't match“ (nur wenn Bestätigung nicht fokussiert ist oder Länge ≥ Passwortlänge) | – |
| `is_telemetry_enabled` (hidden `"True"/"False"`) | Checkbox „Allow Plane to anonymously collect usage events.“ + Link „See More“ → `https://developers.plane.so/self-hosting/telemetry` | Checkbox | – | – | – | `is_telemetry_enabled` (Ausdruck `(… === "True" ? true : false) \|\| true` ⇒ **immer `true`**) |
| `csrfmiddlewaretoken` (hidden) | – | hidden | – | – | aus A1 | – |

Submit-Button „Continue“ (`variant=primary`, `size=lg`, `stretch=full`), deaktiviert solange `first_name`, `email`, `password` leer, Passwort nicht stark oder ungleich Bestätigung oder `isSubmitting`. Stärkeanzeige: `PasswordStrengthIndicator` (3 Segmente; Texte „Please enter your password“, „Password is too short“, „Password is weak“, „Password is strong“; Kriterien „Min 8 characters“, „Min 1 upper-case letter“, „Min 1 lower-case letter“, „Min 1 number“, „Min 1 special character“; ausgeblendet, wenn nicht fokussiert und stark) – `ADM/components/common/password-strength-indicator.tsx`, `packages/utils/src/auth.ts`.

**F-SignIn – Admin-Login** (`ADM/app/(all)/(home)/sign-in-form.tsx`), Überschrift „Manage your Plane instance“ / „Configure instance-wide settings to secure your instance“:

| Feld | Label | Typ | Placeholder | Hinweis |
|---|---|---|---|---|
| `email` | Email * | email, `autoFocus`, `autoComplete=off` | name@company.com | vorbelegt aus Query `email` |
| `password` | Password * | password + Auge | Enter your password | |
| `csrfmiddlewaretoken` | – | hidden | – | |

Button „Sign in“ (primary, lg, full), deaktiviert bis beide Felder befüllt; `loading` ab Submit (wird nie zurückgesetzt, da Seite navigiert).

**F-General** (`.../general/form.tsx`), Abschnitt „Instance details“ (Grid 1/2/3 Spalten ab `md`/`lg`) und „Telemetry“:

| Feld | Label | Typ | Placeholder | Pflicht | Bemerkung |
|---|---|---|---|---|---|
| `instance_name` | Name of instance | text | Instance name | ja | |
| (read-only) | Email | email, `disabled` | Admin email | – | Wert `instanceAdmins[0].user_detail.email` |
| (read-only) | Instance ID | text, `disabled` | – | – | `instance.instance_id` |
| `is_telemetry_enabled` | „Let Plane collect anonymous usage data“ + Text „No PII is collected.This anonymized data is used to understand how you use Plane and build new features in line with our Telemetry Policy.“ (Link → `https://developers.plane.so/self-hosting/telemetry`; fehlendes Leerzeichen nach „collected.“ ist Original) | Switch `size=sm` | – | – | Icon `UsageOutline` in 44 px Kachel |

Button „Save changes“/„Saving“ (primary, md) – **immer aktiv** (kein `isDirty`-Check).

**F-Email** (`.../email/email-config-form.tsx`), Grid `max-w-4xl`, 2 Spalten ab `lg`:

| Feld | Label | Typ | Placeholder | Pflicht | Beschreibung |
|---|---|---|---|---|---|
| `EMAIL_HOST` | Host | text | email.google.com | ja | – |
| `EMAIL_PORT` | Port | text | 8080 | ja | – |
| `EMAIL_FROM` | Sender's email address | text | no-reply@projectplane.so | ja | „This is the email address your users will see when getting emails from this instance. You will need to verify this address.“ |
| (abgeleitet) | Email security | Select (lg) | Select email security | – | Optionen `EMAIL_USE_TLS`→„TLS“, `EMAIL_USE_SSL`→„SSL“, `NONE`→„No email security“; setzt `EMAIL_USE_TLS`/`EMAIL_USE_SSL` auf `"1"/"0"` |
| `EMAIL_HOST_USER` | Username | text | getitdone@projectplane.so | nein | Abschnitt „Authentication“: „This is optional, but we recommend setting up a username and a password for your SMTP server.“ |
| `EMAIL_HOST_PASSWORD` | Password | password | Password | nein | |

Buttons: „Save changes“/„Saving“ (primary; deaktiviert wenn `!isValid || !isDirty`), „Send test email“ (secondary; deaktiviert wenn `!isValid`). Payload enthält zusätzlich `ENABLE_SMTP: "1"`.

**F-TestEmail** (`.../email/test-email-modal.tsx`): Dialog `size="sm"`; Input `receiver_email` (email, Placeholder „Receiver email“, `aria-label="Receiver email"`); Titel je Schritt „Send test email“ / „Email send“ (sic) / „Failed“; Buttons „Cancel“/„Close“ (secondary) und „Send email“/„Sending email“ (primary, nur im ersten Schritt). Erfolgstext: „We have sent the test email to {receiverEmail}. Please check your spam folder if you cannot find it.“ + „If you still cannot find it, recheck your SMTP configuration and trigger a new test email.“. Fehlertext: `err.error` oder „Failed to send email“.

**F-Provider – GitHub** (`.../authentication/github/form.tsx`): linke Spalte „GitHub-provided details for Plane“, rechte Spalte „Plane-provided details for GitHub“.

| Feld | Label | Typ | Placeholder | Pflicht | Beschreibung (Link) |
|---|---|---|---|---|---|
| `GITHUB_CLIENT_ID` | Client ID | text | 70a44354520df8bd9bcd | ja | „You will get this from your GitHub OAuth application settings.“ (→ `https://github.com/settings/applications/new`) |
| `GITHUB_CLIENT_SECRET` | Client secret | password | 9b0050f94ec1b744e32ce79ea4ffacd40d4119cb | ja | „Your client secret is also found in your GitHub OAuth application settings.“ (gleicher Link) |
| `GITHUB_ORGANIZATION_ID` | Organization ID | text | 123456789 | nein | „The organization github ID.“ |
| `ENABLE_GITHUB_SYNC` | Refresh user attributes from GitHub during sign in | Switch | – | – | Default `"0"` wenn leer |
| Copy | Origin URL | Copy-Button | – | – | Wert `originURL`; „We will auto-generate this. Paste this into the `Authorized origin URL` field here.“ (→ GitHub-Link) – in Box `bg-layer-1` |
| Copy | Callback URI | Copy-Button | – | – | `${originURL}/auth/github/callback/`; „We will auto-generate this. Paste this into your `Authorized Callback URI` field here.“ – in Box mit Kopf „WEB“ (`MonitorOutline`, `bg-layer-3`, uppercase) |

**F-Provider – Google** (`.../authentication/google/form.tsx`): „Google-provided details for Plane“ / „Plane-provided details for Google“.

| Feld | Label | Typ | Placeholder | Pflicht | Beschreibung (Link) |
|---|---|---|---|---|---|
| `GOOGLE_CLIENT_ID` | Client ID | text | 840195096245-0p2tstej9j5nc4l8o1ah2dqondscqc1g.apps.googleusercontent.com | ja | „Your client ID lives in your Google API Console. Learn more“ (→ `https://developers.google.com/identity/protocols/oauth2/javascript-implicit-flow#creatingcred`) |
| `GOOGLE_CLIENT_SECRET` | Client secret | password | GOCShX-ADp4cI0kPqav1gGCBg5bE02E | ja | „Your client secret should also be in your Google API Console. Learn more“ (→ `https://developers.google.com/identity/oauth2/web/guides/get-google-api-clientid`) |
| `ENABLE_GOOGLE_SYNC` | Refresh user attributes from Google during sign in | Switch | – | – | |
| Copy | Origin URL | – | – | – | `originURL`; „We will auto-generate this. Paste this into your `Authorized JavaScript origins` field. For this OAuth client here.“ (→ `https://console.cloud.google.com/apis/credentials/oauthclient`) |
| Copy | Callback URI | – | – | – | `${originURL}/auth/google/callback/`; „… `Authorized Redirect URI` field. For this OAuth client here.“ (Box „WEB“) |

**F-Provider – GitLab** (`.../authentication/gitlab/form.tsx`): „GitLab-provided details for Plane“ / rechte Box `bg-layer-3` mit Titel „Plane-provided details for GitLab“.

| Feld | Label | Typ | Placeholder | Pflicht | Beschreibung (Link) |
|---|---|---|---|---|---|
| `GITLAB_HOST` | Host | text | https://gitlab.com | ja | „This is either https://gitlab.com or the `domain.tld` where you host GitLab.“ |
| `GITLAB_CLIENT_ID` | Application ID | text | c2ef2e7fc4e9d15aa7630f5637d59e8e4a27ff01dceebdb26b0d267b9adcf3c3 | ja | „Get this from your GitLab OAuth application settings.“ (→ `https://docs.gitlab.com/ee/integration/oauth_provider.html`) |
| `GITLAB_CLIENT_SECRET` | Secret | password | gloas-f79cfa9a03c97f6ffab303177a5a6778a53c61e3914ba093412f68a9298a1b28 | ja | „The client secret is also found in your GitLab OAuth application settings.“ |
| `ENABLE_GITLAB_SYNC` | Refresh user attributes from GitLab during sign in | Switch | – | – | |
| Copy | Callback URL | – | – | – | `${originURL}/auth/gitlab/callback/`; „We will auto-generate this. Paste this into the `Redirect URI` field of your GitLab OAuth application.“ |

**F-Provider – Gitea** (`.../authentication/gitea/form.tsx`): „Gitea-provided details for Plane“ / rechte Box `bg-layer-1` „Plane-provided details for Gitea“.

| Feld | Label | Typ | Placeholder | Pflicht | Beschreibung (Link) |
|---|---|---|---|---|---|
| `GITEA_HOST` | Gitea Host | text (Default `https://gitea.com`) | https://gitea.com | ja | „Use the URL of your Gitea instance. For the official Gitea instance, use "https://gitea.com".“ |
| `GITEA_CLIENT_ID` | Client ID | text | 70a44354520df8bd9bcd | ja | „You will get this from your Gitea OAuth application settings.“ (→ `https://gitea.com/user/settings/applications`) |
| `GITEA_CLIENT_SECRET` | Client secret | password | 9b0050f94ec1b744e32ce79ea4ffacd40d4119cb | ja | „Your client secret is also found in your Gitea OAuth application settings.“ |
| `ENABLE_GITEA_SYNC` | Refresh user attributes from Gitea during sign in | Switch | – | – | |
| Copy | Callback URI | – | – | – | `${originURL}/auth/gitea/callback/`; Link „here.“ → `${GITEA_HOST \|\| "https://gitea.com"}/user/settings/applications` (liest `control._formValues` – nicht reaktiv) |

Alle vier Provider-Formulare: Buttons „Save changes“/„Saving“ (primary, deaktiviert solange `!isDirty`) und „Go back“ (secondary, Link `/authentication`; bei ungespeicherten Änderungen öffnet sich `ConfirmDiscardModal`). `originURL = API_BASE_URL` wenn gesetzt, sonst `window.location.origin`.

**F-AI** (`.../ai/form.tsx`), Abschnitt „OpenAI“ / „If you use ChatGPT, this is for you.“, Grid 3 Spalten ab `lg`:

| Feld | Label | Typ | Placeholder | Pflicht | Beschreibung |
|---|---|---|---|---|---|
| `LLM_MODEL` | LLM Model | text | gpt-4o-mini | nein | „Choose an OpenAI engine. Learn more“ (→ `https://platform.openai.com/docs/models/overview`) |
| `LLM_API_KEY` | API key | password | sk-asddassdfasdefqsdfasd23das3dasdcasd | nein | „You will find your API key here.“ (→ `https://platform.openai.com/api-keys`) |

Button „Save changes“/„Saving“ (immer aktiv). Darunter Hinweisbox (`border-accent-subtle bg-accent-subtle text-accent-secondary`, Icon `ThoughtsOutline`): „If you have a preferred AI models vendor, please get in touch with us.“ (Link → `https://plane.so/contact`).

**F-Image** (`.../image/form.tsx`): `UNSPLASH_ACCESS_KEY`, Label „Access key from your Unsplash account“, password, Placeholder `oXgq-sdfadsaeweqasdfasdf3234234rassd`, Pflicht, Beschreibung „You will find your access key in your Unsplash developer console. Learn more.“ (→ `https://unsplash.com/documentation#creating-a-developer-account`). Button „Save changes“/„Saving“.

**F-Workspace-Create** (`.../workspace/create/form.tsx`, `mode: "onChange"`), Grid `max-w-4xl`, 2 Spalten ab `lg`:

| Feld | Überschrift | Typ | Placeholder | Validierung | Fehlertexte |
|---|---|---|---|---|---|
| `name` | Name your workspace | text (lg) | Something familiar and recognizable is always best. | `validateWorkspaceName(v, true)`: Pflicht, ≤ 80, keine Risikozeichen, Regex `^[\p{L}\p{N}\s_-]+$`, mind. 1 alphanumerisches | „Workspace name is required“, „Workspace name must be 80 characters or less“, „Workspace name cannot contain special characters like < > ' " { } [ ] * ^ ! # %“, „Workspace name can only contain letters, numbers, spaces, hyphens, and underscores“, „Workspace name must contain at least one letter or number“ |
| `slug` | Set your workspace's URL | text mit Präfix `workspaceBaseURL` (`encodeURI(WEB_BASE_URL)` oder `origin + "/"`) | workspace-name | `validateSlug`: Pflicht, ≤ 48, keine Risikozeichen, Regex `^[\p{L}\p{N}_-]+$`; zusätzlich UI-Check `^[a-zA-Z0-9_-]+$` | „Slug is required“, „Slug must be 48 characters or less“, „Slug cannot contain special characters like …“, „Slug can only contain letters, numbers, hyphens, and underscores“; UI: „URLs can contain only ( - ), ( _ ) and alphanumeric characters.“; nach Server-Check: „This URL is taken. Try something else.“ |
| `organization_size` | How many people will use this workspace? | Select (lg), Placeholder „Select a range“ | – | Pflicht | „This is a required field.“ |

Optionen `organization_size` (`CONST/workspace.ts` `ORGANIZATION_SIZE`): `Just myself`, `2-10`, `11-50`, `51-200`, `201-500`, `500+`. Slug-Autogenerierung: bei jeder Namensänderung `slug = name.toLocaleLowerCase().trim().replace(/ /g, "-")` (mit Validierung). Anzeige des Slug-Werts immer kleingeschrieben/Leerzeichen→`-`. Buttons „Create workspace“/„Creating workspace“ (primary, deaktiviert solange `!isValid`), „Go back“ (Link `/workspace`).

### 2.10 Admin – Toasts, Banner-, Dialog- und Statustexte (vollständig)

| Ort | Typ | Titel | Nachricht | Quelle |
|---|---|---|---|---|
| General speichern ok | success | Success | Settings updated successfully | `.../general/form.tsx` |
| Email speichern ok | success | Success | Email Settings updated successfully | `.../email/email-config-form.tsx` |
| SMTP deaktivieren ok | success | Email feature disabled | Email feature has been disabled | `.../email/page.tsx` |
| SMTP deaktivieren Fehler (praktisch unerreichbar, s. 2.6) | error | Error disabling email | Failed to disable email feature. Please try again. | `.../email/page.tsx` |
| Auth-Seite Switch (Promise-Toast) | loading/success/error | – / Success / Error | Saving configuration / Configuration saved successfully / Failed to save configuration | `.../authentication/page.tsx` |
| Auth-Seite letzte Methode deaktivieren | error | Cannot disable authentication | At least one authentication method must remain enabled. Please enable another method before disabling this one. | `.../authentication/page.tsx` |
| Provider-Seite Kopf-Switch (Promise-Toast) | loading/success/error | – / Configuration saved / Error | Saving Configuration / `{GitHub\|GitLab\|Google\|Gitea} authentication is now {active\|disabled}.` / Failed to save configuration | `.../authentication/{provider}/page.tsx` |
| Provider-Formular gespeichert | success | Done! | Your {GitHub\|GitLab\|Google\|Gitea} authentication is configured. You should test it now. | `.../authentication/{provider}/form.tsx` |
| AI speichern ok | success | Success | AI Settings updated successfully | `.../ai/form.tsx` |
| Image speichern ok | success | Success | Image Configuration Settings updated successfully | `.../image/form.tsx` |
| Workspace-Seite Switch (Promise-Toast) | loading/success/error | – / Success / Error | Saving configuration / Configuration saved successfully / Failed to save configuration | `.../workspace/page.tsx` |
| Workspace erstellt | success | Success! | Workspace created successfully. | `.../workspace/create/form.tsx` |
| Workspace-Erstellung Fehler | error | Error! | Workspace could not be created. Please try again. | dito |
| Slug-Check Fehler | error | Error! | Some error occurred while creating workspace. Please try again. | dito |
| Copy-Feld | info | Copied to clipboard | The {label} has been successfully copied to your clipboard | `ADM/components/common/copy-field.tsx` |
| Discard-Dialog | Dialog | You have unsaved changes | Changes you made will be lost if you go back. Do you wish to go back? – Buttons „Go back“ (primary) / „Keep editing“; ohne Icon | `ADM/components/common/confirm-discard-modal.tsx` |
| New-User-Popup | Karte | Create workspace | Instance setup done! Welcome to Plane instance portal. Start your journey with by creating your first workspace. (sic) – Buttons „Create workspace“ (→ `/workspace/create`), „Close“ | `ADM/components/common/new-user-popup.tsx` |
| Instanz-Fehler | Seite | Unable to fetch instance details. | We were unable to fetch the details of the instance. Fret not, it might just be a connectivity issue. – Button „Retry“ (`location.reload()`) | `ADM/components/instance/failure.tsx` |
| 404 | Seite | Oops! Something went wrong. | Sorry, the page you are looking for cannot be found. It may have been removed, had its name changed, or is temporarily unavailable. – Button „Go to general settings“ | `ADM/app/components/404.tsx` |
| Root-ErrorBoundary | Seite | – | Something went wrong. | `ADM/app/root.tsx` |
| Workspace-Liste | Text | All workspaces on this instance • {n} | You can't yet delete workspaces and you can only go to the workspace if you are an Admin or a Member. | `.../workspace/page.tsx` |
| Workspace-Liste Item | Text | – | „Owned by:“, „Total projects:“, „Total members:“, Tooltip „The unique URL of your workspace“ | `ADM/components/workspace/list-item.tsx` |
| Seitenköpfe | Header | s. 3.7–3.13 | | |

### 2.11 Admin – Auth-Fehlercodes & Anzeige

Backend-Codes (`API/authentication/adapter/error.py`, Frontend-Enum `CONST/auth/index.ts` `EAdminAuthErrorCodes`), Anzeige-Mapping `ADM/app/(all)/(home)/auth-helpers.tsx`:

| Code | Name | Titel | Banner-Nachricht (Sign-in-Seite, `AuthBanner`) | Ausgelöst von |
|---|---|---|---|---|
| 5150 | ADMIN_ALREADY_EXIST | Admin already exists | Admin already exists. Please try again. | Sign-up (Setup bereits erfolgt / Admin existiert) |
| 5155 | REQUIRED_ADMIN_EMAIL_PASSWORD_FIRST_NAME | Email, password and first name required | Email, password and first name required. Please try again. | Sign-up |
| 5160 | INVALID_ADMIN_EMAIL | Invalid admin email | Invalid admin email. Please try again. | Sign-up, Sign-in |
| 5165 | INVALID_ADMIN_PASSWORD | Invalid admin password | Invalid admin password. Please try again. | (vom Backend derzeit nicht ausgelöst) |
| 5170 | REQUIRED_ADMIN_EMAIL_PASSWORD | Email and password required | Email and password required. Please try again. | Sign-in |
| 5175 | ADMIN_AUTHENTICATION_FAILED | Authentication failed | Authentication failed. Please try again. | Sign-in (falsches Passwort, kein Instanz-Admin, Bot-User) |
| 5180 | ADMIN_USER_ALREADY_EXIST | Admin user already exists | „Admin user already exists. **Sign In** now.“ (Link → `/admin` ⇒ `/god-mode/admin/` ⇒ 404) | Sign-up (E-Mail bereits registriert) |
| 5185 | ADMIN_USER_DOES_NOT_EXIST | Admin user does not exist | „Admin user does not exist. **Sign In** now.“ (Link → `/admin`, s. o.) | Sign-in |
| 5190 | ADMIN_USER_DEACTIVATED | User account deactivated | User account deactivated. Please contact {SUPPORT_EMAIL \|\| "administrator"}. (`SUPPORT_EMAIL` Default `support@plane.so`) | Sign-in |
| 5000 | INSTANCE_NOT_CONFIGURED | – | **keine Anzeige** | Sign-in/up ohne Instanz |
| 5021 | PASSWORD_TOO_WEAK | – | **keine Anzeige** | Sign-up (zxcvbn-Score < 3) |
| 5900 | RATE_LIMIT_EXCEEDED | – | **keine Anzeige** | Throttle |

Wichtig: Die Setup-Seite wertet Fehlercodes **überhaupt nicht** aus (Vergleich gegen Namen statt Ziffern, s. 3.2) – dort erscheint bei keinem Fehler ein Banner.

### 2.12 Admin – Komponenten-Detailmaße (für 1:1-Nachbau)

| Komponente | Wichtige Klassen / Maße | Quelle |
|---|---|---|
| Sidebar | `fixed inset-y-0 z-20 md:relative`, Breite 290 px / eingeklappt 70 px, `border-r border-subtle bg-surface-1 duration-300`; auf Mobile eingeklappt `-ml-[290px]` | `ADM/app/(all)/(dashboard)/sidebar.tsx` |
| Sidebar-Kopf | `max-h-header px-4 py-2.5 border-b border-subtle`; Kachel 32 px `bg-layer-1` mit `AccessAndRolesOutline` 20 px; Titel „Instance admin“ `text-body-md-medium`; rechts `WorkspaceAvatar size=sm` (Fallback erster Buchstabe `display_name`) | `sidebar-dropdown.tsx` |
| Sidebar-Menü (Dropdown) | `MenuLabel` = E-Mail; Item „Switch to {light\|dark} mode“ (`PaletteOutline`); Separator; Item „Sign out“ (`LogOutOutline`); `side=bottom align=start` | `sidebar-dropdown.tsx` |
| Sidebar-Fuß | Höhe 56 px (`h-14`), `border-t`; „Redirect to Plane“-Chip (`NewTabOutline` 14 px, `bg-layer-1 px-2 py-1 text-body-xs-medium`), Buttons Hilfe (`HelpOutline`) und Toggle (`ArrowNarrowLeftOutline`, rotiert 180° wenn eingeklappt); Tooltips „Redirect to Plane“, „Help“, „Toggle sidebar“ | `sidebar-help-section.tsx` |
| Hilfe-Popover | `absolute bottom-2 z-[15] min-w-[10rem]`, links `-75px` (eingeklappt `left-full`), `animate-fade-in`, Einträge „Documentation“ (`PagesOutline`, `https://docs.plane.so/`), „Join our Forum“ (`ChatOutline`, `https://forum.plane.so`), „Report a bug“ (`Github`, `https://github.com/makeplane/plane/issues/new/choose`), Fuß „Version: v{current_version}“ (`text-10`); Klick außerhalb schließt **nicht** | `sidebar-help-section.tsx` |
| Header | `h-header p-4 border-b bg-surface-1 z-10`; Hamburger (`lucide Menu` 14 px, `size-7 bg-layer-1`, nur `< md`) | `ADM/components/common/header/index.tsx` |
| PageWrapper `md` | `mx-auto max-w-[1000px] md:px-4 2xl:max-w-[1200px] py-4 space-y-6`; Header `mx-4 border-b py-4`, Titel `text-h5-semibold text-primary`, Beschreibung `text-body-sm-regular text-secondary`; Inhalt `px-4 pb-4 overflow-y-scroll vertical-scrollbar scrollbar-sm` | `ADM/components/common/page-wrapper.tsx` |
| AuthenticationMethodCard | `rounded-lg bg-layer-2`, mit Rahmen `border border-subtle px-4 py-3`; Icon-Kreis 40 px `bg-layer-1`; Name `text-13` (mit Rahmen) / `text-18` (ohne); Beschreibung `text-11`/`text-13`; `unavailable` → `opacity-50`; `disabled` → Config-Slot `opacity-70` | `ADM/components/authentication/authentication-method-card.tsx` |
| Workspace-Item | `rounded-lg border border-subtle bg-layer-1 p-3`, Hover `border-subtle-1 bg-layer-1-hover shadow-raised-100`; Logo 32 px (Bild oder Initiale auf `bg-accent-primary text-on-color`) | `ADM/components/workspace/list-item.tsx` |
| NewUserPopup | `absolute right-8 bottom-8 w-96 rounded-lg border p-6 shadow-md`; Bild 80×80 (`takeoff-icon-{dark,light}.svg`) | `new-user-popup.tsx` |
| CopyField | Button secondary md, Icon `CopyOutline` 18 px Farbe `#B9B9B9` rechts | `copy-field.tsx` |
| CodeBlock | `rounded-md border border-subtle bg-surface-2 px-0.5 text-11 font-semibold text-tertiary`; `darkerShade`: `bg-layer-1 text-secondary` | `code-block.tsx` |
| Banner | Fehler `border-danger-strong bg-danger-subtle`, Erfolg `border-success-strong bg-success-subtle`, Text `text-13 font-medium` | `banner.tsx` |
| AuthBanner | `rounded-md border border-accent-strong/50 bg-accent-primary/10 p-2`, Icon `InfoOutline` 16 px, Text `text-13 font-medium text-accent-primary`, Schließen 24 px | `auth-banner.tsx` |
| ControllerSwitch | Label-Klassen `text-sm text-custom-text-300` (**Legacy-Tokens**, in neuer Tailwind-Konfiguration evtl. ohne Wirkung) | `controller-switch.tsx` |
| InstanceFailureView | Titel `text-20 font-medium text-on-color` (im Light-Theme vermutlich kaum sichtbar) | `ADM/components/instance/failure.tsx` |

### 2.13 Admin – Assets

| Datei | Verwendung |
|---|---|
| `ADM/app/assets/favicon/{apple-touch-icon.png,favicon-16x16.png,favicon-32x32.png,favicon.ico}` | Head-Links |
| `ADM/app/assets/images/404.svg` | 404-Seite |
| `ADM/app/assets/images/logo-spinner-dark.gif` (976 KB), `logo-spinner-light.gif` (428 KB) | `LogoSpinner` (Dark-Theme → light-GIF) |
| `ADM/app/assets/images/plane-takeoff.png` | **ungenutzt** |
| `ADM/app/assets/instance/instance-failure.svg`, `instance-failure-dark.svg` | `InstanceFailureView` |
| `ADM/app/assets/logos/gitea-logo.svg`, `gitlab-logo.svg`, `google-logo.svg` | Auth-Karten (20 px) und Provider-Kopf (24 px) |
| `ADM/app/assets/logos/github-black.png` (Light), `github-white.png` (Dark) | GitHub-Icon, themenabhängig |
| `ADM/app/assets/logos/takeoff-icon-dark.svg`, `takeoff-icon-light.svg` | `NewUserPopup` |
| `ADM/public/favicon/android-chrome-{192x192,512x512}.png` | Manifest |

### 2.14 Admin – Browser-Speicher, Cookies, SWR-Keys

| Art | Schlüssel | Werte / Verhalten | Quelle |
|---|---|---|---|
| localStorage | `theme` | `light` \| `dark` \| `system` (next-themes); beim Sign-out auf `system` gesetzt | `ADM/store/root.store.ts`, next-themes |
| localStorage | `god_mode_sidebar_collapsed` | `"true"`/`"false"` | `ADM/store/theme.store.ts`, `ADM/providers/user.provider.tsx` |
| Cookie (HttpOnly, vom Backend) | `admin-session-id` | Admin-Session, Max-Age `ADMIN_SESSION_COOKIE_AGE` (3600 s) | `API/authentication/middleware/session.py` |
| Cookie | `csrftoken` (Django) | CSRF; Token wird zusätzlich über A1 geholt und als Formfeld gesendet | `API/settings/common.py` |
| SWR-Key | `INSTANCE_DETAILS` | `fetchInstanceInfo`, `revalidateOnFocus:false`, `revalidateIfStale:false`, `errorRetryCount:0` | `ADM/providers/instance.provider.tsx` |
| SWR-Key | `CURRENT_USER` | `fetchCurrentUser`, `shouldRetryOnError:false` | `ADM/providers/user.provider.tsx` |
| SWR-Key | `INSTANCE_ADMINS` | `fetchInstanceAdmins` | dito |
| SWR-Key | `INSTANCE_CONFIGURATIONS` | `fetchInstanceConfigurations` (auf jeder Dashboard-Seite außer General/Workspace-Create) | Seiten |
| SWR-Key | `INSTANCE_WORKSPACES` | `fetchWorkspaces` | `.../workspace/page.tsx` |
| SWR-Global | – | `refreshWhenHidden:false`, `revalidateIfStale:false`, `revalidateOnFocus:false`, `revalidateOnMount:true`, `refreshInterval:600000` (**alle 10 min Polling**), `errorRetryCount:3` | `ADM/providers/core.tsx` |

### 2.15 Space – Routentabelle

Alle URLs relativ zum Base-Path `/spaces/`. Space verwendet neben dem `next/navigation`-Shim (`SPC/app/compat/next/navigation.ts`, ebenfalls `ensureTrailingSlash` bei `push/replace`) auch **direkt** `react-router` `Link` (ohne Trailing-Slash-Logik).

| # | URL (unter `/spaces`) | Datei | Lade-/Guard-Verhalten | Quelle |
|---|---|---|---|---|
| S1 | `/` | `SPC/app/page.tsx` | Header `X-Frame-Options: SAMEORIGIN`. Initialisierung → Spinner; eingeloggt + gültiger `next_path` → `router.replace(next_path)` (Spinner); eingeloggt ohne → `UserLoggedIn`; sonst `AuthView` (Login/Sign-up) | `SPC/app/routes.ts` Z. 11 |
| S2 | `/:workspaceSlug/:projectId` | `SPC/app/[workspaceSlug]/[projectId]/page.tsx` | **clientLoader**: `GET /api/public/workspaces/{slug}/projects/{projectId}/anchor/`; bei `entity_name === "project"` → `redirect("/issues/{anchor}[?board=…&peekId=…]")`, sonst/Fehler → `redirect("/404")`; Komponente zeigt nur Spinner (`h-screen min-h-[500px]`) | Z. 12 |
| S3 | `/issues/:anchor` | Layout `SPC/app/issues/[anchor]/layout.tsx` + Seite `SPC/app/issues/[anchor]/page.tsx` | **Server-loader** (SSR) holt `GET {VITE_API_BASE_URL}/api/public/anchor/{anchor}/meta/` für Meta-Tags (Anchor muss `^[a-zA-Z0-9_-]+$` erfüllen); `shouldRevalidate` nur bei Anchor-Wechsel; Client lädt Publish-Settings (SWR) → 404-Seite / Fehlerseite / Board | Z. 13 |
| S4 | `*` | `SPC/app/not-found.tsx` | „That didn't work“ (auch Ziel von `redirect("/404")`) | Z. 15 |

Query-Parameter siehe 2.20. Server-Redirect-Ziele des Backends für Space: `base_host(is_space=True)` = `{SPACE_BASE_URL oder WEB_URL/APP_BASE_URL}{SPACE_BASE_PATH normalisiert "/spaces/"}` (+ `next_path` / Fehlerparameter) (`API/authentication/utils/host.py`).

### 2.16 Space – Seitentitel, Meta, HTTP-Header

| Ort | Inhalt | Quelle |
|---|---|---|
| Root `meta` | `<title>Plane Publish \| Make your Plane boards public with one-click</title>`, `description` „Plane Publish is a customer feedback management tool built on top of plane.so“, `og:title`, `og:description`, `og:url=https://sites.plane.so/`, `keywords` (…, work item tracking, …), `twitter:site=@planepowers` | `SPC/app/root.tsx` Z. 27–28, 72–84 |
| Root `<head>` | `<meta name="robots" content="noindex, nofollow">`; Links: apple-touch-icon, Favicons 32/16, `.ico`, Manifest **`app/assets/favicon/site.webmanifest`** (Name leer), Stylesheet, Font-Preload Inter | `SPC/app/root.tsx` Z. 30–70 |
| Root `<body>` | `<div id="editor-portal"/>` vor den Providern (Portal-Ziel des Editors) | `SPC/app/root.tsx` Z. 64 |
| Root `headers` (alle Antworten) | `Referrer-Policy: origin-when-cross-origin`, `X-Content-Type-Options: nosniff`, `X-DNS-Prefetch-Control: on`, `Strict-Transport-Security: max-age=31536000; includeSubDomains; preload` | `SPC/app/root.tsx` Z. 46–51 |
| `/` `headers` | `X-Frame-Options: SAMEORIGIN` (nur Startseite; Board-Seiten sind iframe-einbettbar) | `SPC/app/page.tsx` Z. 20–22 |
| `/issues/:anchor` `meta` | `title` = `metadata.name` oder „Plane“; `description` = `metadata.description` oder „Made with Plane, an AI-powered work management platform with publishing capabilities.“; `og:title`, `og:description`, `og:type=website`, `twitter:card=summary_large_image`, `twitter:title`, `twitter:description`; wenn `cover_image`: `og:image`, `og:image:width=800`, `og:image:height=600`, `og:image:alt=title`, `twitter:image` | `SPC/app/issues/[anchor]/layout.tsx` Z. 22–89 |
| HydrateFallback | zentrierter `LogoSpinner` auf `bg-surface-1` | `SPC/app/root.tsx` |
| ErrorBoundary | `ErrorPage` („Yikes! That doesn't look good.“ …, Button „Refresh“) | `SPC/app/error.tsx` |

### 2.17 Space – Dateiinventar (Quellcode & Konfiguration)

| Datei | Verantwortung |
|---|---|
| `SPC/app/root.tsx`, `SPC/app/routes.ts`, `SPC/app/entry.client.tsx` (wartet auf `@plane/i18n` `initPromise`, dann `hydrateRoot`), `SPC/app/providers.tsx` | Bootstrap, Provider (3.16) |
| `SPC/app/page.tsx`, `SPC/app/not-found.tsx`, `SPC/app/error.tsx` | Startseite, 404, Fehlerseite |
| `SPC/app/[workspaceSlug]/[projectId]/page.tsx` | Legacy-URL → Anchor-Redirect |
| `SPC/app/issues/[anchor]/layout.tsx`, `page.tsx` | Board-Layout (Navbar, Meta, Publish-Settings), Board-Inhalt (States/Labels laden) |
| `SPC/app/compat/next/helper.ts`, `navigation.ts` | Shims (`useRouter`, `usePathname`, `useSearchParams`, `useParams`) |
| `SPC/app/types/*.d.ts`, `SPC/additional.d.ts` | Typdeklarationen |
| `SPC/components/account/auth-forms/auth-root.tsx` | Auth-Ablaufsteuerung (Modus/Step/Fehler) |
| `SPC/components/account/auth-forms/{email,password,unique-code}.tsx` | Schritte E-Mail, Passwort, Unique Code |
| `SPC/components/account/auth-forms/{auth-banner,auth-header,index}.ts(x)` | Banner, Überschrift |
| `SPC/components/account/terms-and-conditions.tsx` | Rechtshinweis |
| `SPC/components/account/user-logged-in.tsx` | „Nice! Just one more step.“-Ansicht |
| `SPC/components/views/{auth,header,index}.tsx` | Auth-Seitenrahmen, Logo-Header |
| `SPC/components/common/{logo-spinner,powered-by,project-logo}.tsx` | Spinner, „Powered by Plane Publish“, Projekt-Logo (Emoji/Material-Icon) |
| `SPC/components/instance/instance-failure-view.tsx` | Instanzfehler |
| `SPC/components/ui/not-found.tsx` | 404 für unbekannten Anchor |
| `SPC/components/issues/navbar/{root,controls,layout-selection,layout-icon,theme,user-avatar,index}.tsx` | Board-Navbar |
| `SPC/components/issues/filters/{root,selection,priority,state,labels,index}.tsx`, `helpers/{dropdown,filter-header,filter-option}.tsx` | Filter-Popover |
| `SPC/components/issues/filters/applied-filters/{root,filters-list,priority,state,label}.tsx` | Leiste aktiver Filter |
| `SPC/components/issues/issue-layouts/{root,index,error,issue-layout-HOC,with-display-properties-HOC,utils}.tsx` | Layout-Weiche, Lade-/Leerzustand, Gruppierungsspalten |
| `SPC/components/issues/issue-layouts/list/{base-list-root,default,list-group,blocks-list,block}.tsx`, `list/headers/group-by-card.tsx` | List-Layout |
| `SPC/components/issues/issue-layouts/kanban/{base-kanban-root,default,kanban-group,blocks-list,block,block-reactions}.tsx`, `kanban/headers/group-by-card.tsx` | Board-Layout |
| `SPC/components/issues/issue-layouts/kanban/swimlanes.tsx`, `kanban/headers/sub-group-by-card.tsx` | Swimlanes (Sub-Gruppierung) – **nicht eingebunden** (toter Code) |
| `SPC/components/issues/issue-layouts/properties/{all-properties,state,priority,labels,due-date,member,modules,cycle}.tsx` | Eigenschafts-Chips |
| `SPC/components/issues/peek-overview/{layout,side-peek-view,full-screen-peek-view,header,issue-details,issue-properties,issue-reaction,issue-activity,index}.tsx` | Peek-Ansicht |
| `SPC/components/issues/peek-overview/comment/{add-comment,comment-detail-card,comment-reactions}.tsx` | Kommentare |
| `SPC/components/issues/reactions/{issue-emoji-reactions,issue-vote-reactions}.tsx` | Reaktionen & Votes |
| `SPC/components/editor/{lite-text-editor,rich-text-editor,toolbar}.tsx`, `editor/embeds/mentions/{root,user,index}.ts(x)` | Editor-Wrapper (Tiptap aus `@plane/editor`), Kommentar-Toolbar, Mention-Rendering |
| `SPC/helpers/authentication.helper.tsx` | Space-Fehlercodes → Banner |
| `SPC/helpers/{common,date-time,editor,emoji,file,issue,query-param-generator,state,string}.helper.ts(x)` | Hilfsfunktionen (3.x) |
| `SPC/hooks/oauth/{core,extended,index}.tsx` | OAuth-Buttons |
| `SPC/hooks/store/*.ts`, `SPC/hooks/store/publish/*.ts` | Store-Zugriff (`usePublish(anchor)` liefert `{}` wenn unbekannt!) |
| `SPC/hooks/{use-clipboard-write-permission,use-editor-flagging,use-intersection-observer,use-is-in-iframe,use-mention,use-parse-editor-content,use-timer}.ts(x)` | Hooks (`use-mention` ungenutzt) |
| `SPC/lib/{instance-provider,store-provider,toast-provider}.tsx`, `SPC/lib/b-progress/*` | Provider, Progressbar |
| `SPC/store/*.ts`, `SPC/store/helpers/*.ts`, `SPC/store/publish/*.ts` | MobX-Stores (2.18) |
| `SPC/types/{auth,cycle,intake,issue,member,modules}.ts` | Lokale Typen (`intake.d.ts` ungenutzt) |
| `SPC/styles/globals.css` | Import `@plane/tailwind-config/index.css`, `@plane/editor/styles`, Plugin `@tailwindcss/typography`; `:root`-Fallbacks Editor-Hintergrundfarben (`--editor-colors-{gray,peach,pink,orange,green,light-blue,dark-blue,purple}-background`: `#d6d6d8`, `#ffd5d7`, `#fdd4e3`, `#ffe3cd`, `#c3f0de`, `#c5eff9`, `#c9dafb`, `#e3d8fd`); BProgress-Stile wie Admin |
| `SPC/Dockerfile.space`, `SPC/Dockerfile.dev`, `SPC/nginx/nginx.conf` (ungenutzt), `SPC/.env.example` (wie Admin), `SPC/package.json`, `SPC/react-router.config.ts`, `SPC/vite.config.ts`, `SPC/tsconfig.json`, `SPC/postcss.config.js`, `SPC/README.md`, `SPC/.gitignore`, `SPC/.prettierignore`, `SPC/public/site.webmanifest.json` („Plane Space“, ungenutzt im Head), `SPC/public/favicon/*` | Build/Betrieb |

### 2.18 Space – Stores (MobX)

`RootStore` (`SPC/store/root.store.ts`): `instance`, `user`, `issue`, `issueDetail`, `state`, `label`, `module`, `member`, `cycle`, `issueFilter`, `publishList`. `hydrate(data)` → `instance`, `user`. `reset()` → `localStorage.theme="system"` und **Neuerzeugung aller Stores**. Singleton im Client (`SPC/lib/store-provider.tsx`).

| Store | Observables / Computeds | Actions (API) | Quelle |
|---|---|---|---|
| `InstanceStore` | `isLoading`, `instance`, `config`, `error` (`{status:"error",message:"Failed to fetch instance info"}`) | `fetchInstanceInfo()` → `GET /api/instances/` (Fehler wird **nicht** geworfen), `hydrate` | `SPC/store/instance.store.ts` |
| `UserStore` | `isAuthenticated` (false), `isInitializing` (true), `error`, `data: IUser`, `profile: ProfileStore`; computed `currentActor` = `{id, first_name, last_name, display_name, avatar_url, is_bot:false}` | `fetchCurrentUser()` → `GET /api/users/me/`, bei `user.id` zusätzlich `profile.fetchUserProfile()`; Fehler: `isAuthenticated=false`, `error={status:"user-fetch-error",…}`, bei 401 `data=undefined`, rethrow. `updateCurrentUser` (PATCH `/api/users/me/`, optimistisch, ungenutzt), `reset`, `signOut` (= `RootStore.reset()`) | `SPC/store/user.store.ts` |
| `ProfileStore` | `isLoading`, `error`, `data: TUserProfile` (Defaults: `theme`-Objekt leer, `onboarding_step` alle false, `is_onboarded:false`, `start_of_the_week: SUNDAY`, …) | `fetchUserProfile()` → `GET /api/users/me/profile/`; `updateUserProfile` (PATCH, ungenutzt) | `SPC/store/profile.store.ts` |
| `PublishListStore` | `publishMap: Record<anchor, PublishStore>` | `fetchPublishSettings(anchor)` → `GET /api/public/anchor/{anchor}/settings/` (wirft `error.response`) | `SPC/store/publish/publish_list.store.ts` |
| `PublishStore` | alle Felder von `TProjectPublishSettings` (`anchor, is_comments_enabled, created_at, created_by, entity_identifier, entity_name, id, inbox, project, project_details, is_reactions_enabled, updated_at, updated_by, view_props, is_votes_enabled, workspace, workspace_detail`); computed `workspaceSlug`, `canComment`, `canReact`, `canVote` | – | `SPC/store/publish/publish.store.ts` |
| `IssueFilterStore` | `layoutOptions` (Default `{list:true,kanban:false,calendar:false,gantt:false,spreadsheet:false}`), `filters: {[anchor]: {display_filters:{layout}, filters:{state[],priority[],labels[]}}}` | `updateLayoutOptions`, `initIssueFilters(anchor, filters, shouldFetch)`, `updateIssueFilters(anchor, kind, key, value)` (bei Nicht-`layout` → Refetch „mutation“), `getIssueFilters`, `getAppliedFilters` (nur für Layout erlaubte Filter laut `ISSUE_DISPLAY_FILTERS_BY_LAYOUT`: `priority`, `state`, `labels`; Arrays → kommasepariert), `isIssueFiltersUpdated` (Gleichheit der `filters`), `getFilterParams` | `SPC/store/issue-filters.store.ts` |
| `IssueStore` (extends `BaseIssuesStore`) | `loader` (Map Gruppe → `TLoader`), `groupedIssueIds`, `issuePaginationData`, `groupedIssueCount`, `paginationOptions` | `fetchPublicIssues(anchor, loadType, options)`, `fetchNextPublicIssues(anchor, groupId?, subGroupId?)`, `fetchPublicIssuesWithExistingPagination(anchor, loadType="mutation")` → `GET /api/public/anchor/{anchor}/issues/` | `SPC/store/issue.store.ts`, `SPC/store/helpers/base-issues.store.ts` |
| `IssueDetailStore` | `loader`, `error`, `peekId`, `peekMode` (Default `"side"`), `details: Record<issueId, IIssue>` (enthält auch Listen-Issues, `comments`, `reaction_items`, `vote_items`) | `setPeekId`, `setPeekMode`, `getIsIssuePeeked`, `getIssueById`, `fetchIssueDetails` (Issue + Kommentare), `addIssueComment`, `updateIssueComment` (optimistisch, Fehler → Liste neu laden), `deleteIssueComment`, `uploadCommentAsset`, `uploadIssueAsset` (ungenutzt), `addCommentReaction`/`removeCommentReaction` (optimistisch), `addIssueReaction`/`removeIssueReaction` (optimistisch), `addIssueVote`/`removeIssueVote` (optimistisch; `addIssueVote` wirft „Publish settings not found“, wenn PublishStore fehlt) | `SPC/store/issue-detail.store.ts` |
| `StateStore` | `states`, computed `sortedStates` (nach Gruppenreihenfolge `backlog, unstarted, started, completed, cancelled` aus `STATE_GROUPS`, dann `sequence`) | `fetchStates(anchor)` → `GET /api/public/anchor/{anchor}/states/`, `getStateById` | `SPC/store/state.store.ts`, `SPC/helpers/state.helper.ts` |
| `LabelStore` | `labelMap`, computed `labels` | `fetchLabels(anchor)` → `GET …/labels/`, `getLabelById`, `getLabelsByIds` | `SPC/store/label.store.ts` |
| `MemberStore` | `memberMap` (Key = `member` = User-ID), computed `members` | `fetchMembers(anchor)` → `GET …/members/` – **wird nirgends aufgerufen** | `SPC/store/members.store.ts` |
| `ModuleStore` | `moduleMap`, computed `modules` | `fetchModules(anchor)` → `GET …/modules/` – **nirgends aufgerufen** | `SPC/store/module.store.ts` |
| `CycleStore` | `cycles` | `fetchCycles(anchor)` → `GET …/cycles/` – **nirgends aufgerufen** | `SPC/store/cycle.store.ts` |

### 2.19 Space – API-Aufrufe (vollständig)

Alle über Axios (`withCredentials`, Trailing-Slash-Interceptor) außer Form-POSTs und dem SSR-`fetch`.

| # | Methode & Pfad | Aufrufer | Request | Response (verwendet) | Backend-Berechtigung / Besonderheit |
|---|---|---|---|---|---|
| B1 | `GET /api/instances/` | `InstanceStore.fetchInstanceInfo` (SWR `INSTANCE_INFO`) | – | `instance`, `config` (`is_smtp_configured`, `is_magic_login_enabled`, `is_email_password_enabled`, `is_google_enabled`, `is_github_enabled`, `is_gitlab_enabled`, `is_gitea_enabled`) | AllowAny; Pfad enthält „instances“ ⇒ Backend liest **Admin-Cookie** (irrelevant, da AllowAny) |
| B2 | `GET /api/users/me/` | `UserStore.fetchCurrentUser` (SWR `CURRENT_USER`, `revalidateOnFocus:true`, `revalidateIfStale:true`, `shouldRetryOnError:false`) | – | `IUser` | 401 für Anonyme |
| B3 | `GET /api/users/me/profile/` | `ProfileStore.fetchUserProfile` | – | `TUserProfile` | angemeldet |
| B4 | `GET /auth/get-csrf-token/` | Passwort-Form, Unique-Code-Form, `UserAvatar` | – | `{csrf_token}` | AllowAny |
| B5 | `POST /auth/spaces/email-check/` | `SitesAuthService.emailCheck` → `AuthRoot` | `{email}` | `{existing: bool, status: "MAGIC_CODE"\|"CREDENTIAL"}`; Fehler 400 `{error_code, error_message}` | `EmailCheckSpaceEndpoint`, Throttle; `MAGIC_CODE` wenn (bestehend ∧ `is_password_autoset` ∧ SMTP ∧ Magic aktiv) bzw. (neu ∧ SMTP ∧ Magic aktiv) |
| B6 | `POST /auth/spaces/magic-generate/` | `SitesAuthService.generateUniqueCode` → `AuthRoot.generateEmailUniqueCode` | `{email}` | – (Fehler `{error_code}`) | Magic-Code per E-Mail |
| F4 | **Form-POST** `/auth/spaces/sign-in/` | `AuthPasswordForm` (SIGN_IN) | `csrfmiddlewaretoken`, `email` (hidden), `next_path`, `password` | 302 | – |
| F5 | **Form-POST** `/auth/spaces/sign-up/` | `AuthPasswordForm` (SIGN_UP) | wie F4 + `confirm_password` | 302 | – |
| F6 | **Form-POST** `/auth/spaces/magic-sign-in/` | `AuthUniqueCodeForm` (SIGN_IN) | `csrfmiddlewaretoken`, `email`, `next_path`, `code` | 302 | – |
| F7 | **Form-POST** `/auth/spaces/magic-sign-up/` | `AuthUniqueCodeForm` (SIGN_UP) | wie F6 | 302 | – |
| F8 | **Form-POST** `/auth/spaces/sign-out/` | `UserAvatar` | `csrfmiddlewaretoken`, `next_path` = `${pathname}?${queryParam}` | 302 | – |
| N1 | **Navigation** `GET {API_BASE_URL}/auth/{google\|github\|gitlab\|gitea}/[?next_path=…]` | OAuth-Buttons (`SPC/hooks/oauth/core.tsx`) | – | Redirect zum Provider | **App-Flow, nicht `/auth/spaces/{provider}/`** ⇒ Rückkehr landet in der Web-App (`base_host(is_app=True)`), s. 3.18 |
| B7 | `GET /api/public/workspaces/{slug}/projects/{projectId}/anchor/` | `SitesProjectPublishService.retrieveSettingsByProjectId` (S2 clientLoader) | – | `TProjectPublishSettings` | AllowAny |
| B8 | `GET /api/public/anchor/{anchor}/meta/` | SSR-`loader` (natives `fetch`, ohne Cookies) | – | `{id, identifier, name, cover_image, icon_prop, emoji, description}` | AllowAny; 404 „Project is not published“ |
| B9 | `GET /api/public/anchor/{anchor}/settings/` | `PublishListStore.fetchPublishSettings` (SWR `PUBLISH_SETTINGS_{anchor}`) | – | `DeployBoard` `fields="__all__"` + `project_details` (ProjectLite) + `workspace_detail` (WorkspaceLite): u. a. `anchor, entity_identifier, entity_name, is_comments_enabled, is_reactions_enabled, is_votes_enabled, intake, view_props, is_activity_enabled, is_disabled, project, workspace` | AllowAny; Fehler → Axios-`response` (mit `status`) |
| B10 | `GET /api/public/anchor/{anchor}/states/` | `StateStore.fetchStates` (SWR `PUBLIC_STATES_{anchor}`) | – | `IState[]` | AllowAny |
| B11 | `GET /api/public/anchor/{anchor}/labels/` | `LabelStore.fetchLabels` (SWR `PUBLIC_LABELS_{anchor}`) | – | `IIssueLabel[]` `{id,name,color,parent}` | AllowAny |
| B12 | `GET /api/public/anchor/{anchor}/issues/` | `IssueStore` (SWR `PUBLIC_ISSUES_{anchor}` + Filter/Paginierung) | s. 3.22 (`cursor`, `per_page`, `group_by`, `priority`, `state`, `labels`, …) | Paginiert, gruppiert: `{grouped_by, next_cursor, prev_cursor, next_page_results, prev_page_results, total_count, count, total_pages, extra_stats, results}`; Issue-Felder: `id, name, state_id, sort_order, estimate_point, priority, start_date, target_date, sequence_id, project_id, parent_id, cycle_id, created_by, state__group, assignee_ids, label_ids, module_ids, vote_items, reaction_items` (+ `link_count, attachment_count, sub_issues_count`) | AllowAny; Default-Order `-created_at`; `group_by == sub_group_by` ⇒ 400 |
| B13 | `GET /api/public/anchor/{anchor}/issues/{issueId}/` | `IssueDetailStore.fetchIssueById` | – | `IPublicIssue` inkl. `description_html`, `label_ids`, `assignee_ids`, `module_ids`, `vote_items`, `reaction_items` | AllowAny |
| B14 | `GET /api/public/anchor/{anchor}/issues/{issueId}/comments/` | `fetchIssueDetails`, Rollbacks | – | `TIssuePublicComment[]` (nur `access="EXTERNAL"`, sortiert `created_at`; leer wenn Kommentare deaktiviert) | AllowAny |
| B15 | `POST …/issues/{issueId}/comments/` | `addIssueComment` | `{comment_html}` (nur `comment_html`/`comment_json` werden übernommen) | Kommentar (201) | IsAuthenticated; nur bei `is_comments_enabled`; legt `ProjectPublicMember` an, Activity-Event |
| B16 | `PATCH …/issues/{issueId}/comments/{commentId}/` | `updateIssueComment` | `{comment_html}` | Kommentar | nur eigener Kommentar |
| B17 | `DELETE …/issues/{issueId}/comments/{commentId}/` | `deleteIssueComment` | – | 204 | nur eigener Kommentar |
| B18 | `GET …/issues/{issueId}/reactions/` | `listReactions` (nur Rollback) | – | **immer leer** (Backend-Queryset nutzt nicht vorhandene `slug/project_id`-Kwargs) | IsAuthenticated |
| B19 | `POST …/issues/{issueId}/reactions/` | `addIssueReaction` | `{reaction: "<Dezimal-Codepoints mit '-'>"}` | Reaktion (201) | IsAuthenticated; nur bei `is_reactions_enabled` |
| B20 | `DELETE …/issues/{issueId}/reactions/{reactionCode}/` | `removeIssueReaction` | – | 204 | eigener |
| B21 | `POST /api/public/anchor/{anchor}/comments/{commentId}/reactions/` | `addCommentReaction` | `{reaction}` | 201 | IsAuthenticated; nur EXTERNAL-Kommentare |
| B22 | `DELETE …/comments/{commentId}/reactions/{reactionCode}/` | `removeCommentReaction` | – | 204 | eigener |
| B23 | `GET …/issues/{issueId}/votes/` | `listVotes` (nur Rollback) | – | **immer leer** (Queryset filtert `workspace__slug=anchor`) | IsAuthenticated |
| B24 | `POST …/issues/{issueId}/votes/` | `addIssueVote` | `{vote: 1\|-1}` | Vote (201); `get_or_create` + Überschreiben des Werts | IsAuthenticated; nur bei `is_votes_enabled` |
| B25 | `DELETE …/issues/{issueId}/votes/` | `removeIssueVote` | – | 204 | eigener; **ohne** `is_votes_enabled`-Prüfung |
| B26 | `POST /api/public/assets/v2/anchor/{anchor}/` | `SitesFileService.uploadAsset` (Kommentar-Bilder) | `{entity_identifier: commentId\|"", entity_type: "COMMENT_DESCRIPTION", name, type, size}` | `{upload_data:{url, fields}, asset_id, asset_url}` | IsAuthenticated; nur bei Kommentaren aktiv; nur `image/jpeg, png, webp, jpg, gif`; Größe auf `FILE_SIZE_LIMIT` geklemmt |
| B27 | `POST {upload_data.url}` (S3/MinIO presigned) | `FileUploadService.uploadFile` | `multipart/form-data` | – | Speicher |
| B28 | `PATCH /api/public/assets/v2/anchor/{anchor}/{assetId}/` | `updateAssetUploadStatus` | – | 204 | markiert hochgeladen |
| B29 | `POST /api/public/assets/v2/anchor/{anchor}/{commentId}/bulk/` | `AddComment` nach Kommentar-Erstellung | `{asset_ids: string[]}` | 204 | verknüpft Assets mit Kommentar |
| B30 | `GET /api/public/assets/v2/anchor/{anchor}/{assetId}/` | Editor `getAssetSrc` (Bild-URL) | – | 302 auf presigned URL (inline) | AllowAny; nur ISSUE_/COMMENT_DESCRIPTION |
| B31 | `DELETE {getEditorAssetSrc(...)}` bzw. `DELETE /api/workspaces/file-assets/{workspaceId}/{assetKey}/` | Editor `delete` (neue bzw. alte Assets) | – | – | |
| B32 | `POST /api/public/assets/v2/anchor/{anchor}/restore/{assetId}/` bzw. `POST /api/workspaces/file-assets/{workspaceId}/{assetKey}/restore/` | Editor `restore` | – | – | |

Nicht von der UI genutzte Public-Endpunkte: `GET /api/public/anchor/{anchor}/members/`, `…/cycles/`, `…/modules/` (Stores vorhanden, nie aufgerufen), `GET/POST /api/public/anchor/{anchor}/intakes/{intakeId}/intake-issues/` (+ Alias `inbox-issues`), `GET/PATCH/DELETE …/intake-issues/{pk}/`, `GET /api/public/workspaces/{slug}/project-boards/` (View fehlerhaft implementiert), `GET /api/public/anchor/{anchor}/comments/{commentId}/reactions/` (`API/space/urls/*.py`).

### 2.20 Space – Query-Parameter

| Parameter | Seite | Bedeutung / Format | Gesetzt durch | Quelle |
|---|---|---|---|---|
| `next_path` | `/` | Rücksprungpfad nach Login (relativ zu `/spaces`, z. B. `/issues/abc?board=list`); nur wenn `isValidNextPath` (beginnt mit `/`, nicht `//`, kein `\`, keine bösartigen Muster) | „Sign in“-Buttons, Reaktion/Vote anonym | `SPC/app/page.tsx`, `packages/utils/src/url.ts` |
| `email` | `/` | E-Mail-Vorbelegung (nach Fehler-Redirect) | Backend | `auth-root.tsx` |
| `error_code`, `error_message` | `/` | Fehler-Banner/Step-Steuerung | Backend | `auth-root.tsx` |
| `board` | `/issues/:anchor`, S2 | `list` \| `kanban` \| `calendar` \| `gantt` \| `spreadsheet` | Navbar | `navbar/controls.tsx` |
| `peekId` | `/issues/:anchor`, S2 | Issue-ID der geöffneten Peek-Ansicht | Karten-Links | `issue-layouts/root.tsx` |
| `priority` | `/issues/:anchor` | kommaseparierte Prioritäten (`urgent,high,medium,low,none`) | Filter | `filters/root.tsx` |
| `state` | `/issues/:anchor` | kommaseparierte State-IDs | Filter | dito |
| `labels` | `/issues/:anchor` | kommaseparierte Label-IDs (UI-Filter auskommentiert, aber URL-Parameter wird gelesen) | – | dito |
| `states` | `/issues/:anchor` | **Fehlerhafter** Parametername beim Entfernen eines Filters über die Leiste aktiver Filter; wird nirgends gelesen | `applied-filters/root.tsx` Z. 56 | |

`queryParamGenerator` (`SPC/helpers/query-param-generator.ts`): Zahlen/Booleans → `toString()`, nicht-leere Strings unverändert (in `query` als Array gesplittet), nicht-leere Arrays → `toString()` (kommasepariert); leere/undefinierte Werte werden ausgelassen.

### 2.21 Space – Auth-Fehlercodes & Banner

Mapping `SPC/helpers/authentication.helper.tsx` (`EAuthenticationErrorCodes`). Alle aufgeführten Codes werden als `BANNER_ALERT` angezeigt (Komponente `AuthBanner`, Accent-Farben, schließbar):

| Code | Name | Titel | Nachricht |
|---|---|---|---|
| 5000 | INSTANCE_NOT_CONFIGURED | Instance not configured | Instance not configured. Please contact your administrator. |
| 5005 | INVALID_EMAIL | Invalid email | Invalid email. Please try again. |
| 5010 | EMAIL_REQUIRED | Email required | Email required. Please try again. |
| 5015 | SIGNUP_DISABLED | Sign up disabled | Sign up disabled. Please contact your administrator. |
| 5017 | BOT_USER_LOGIN_FORBIDDEN | Sign in not allowed | This account cannot be used to sign in. Please use a personal account. |
| 5019 | USER_ACCOUNT_DEACTIVATED | User account deactivated | User account deactivated. Please contact {SUPPORT_EMAIL \|\| "administrator"}. |
| 5020 | INVALID_PASSWORD | Invalid password | Invalid password. Please try again. |
| 5025 | SMTP_NOT_CONFIGURED | SMTP not configured | SMTP not configured. Please contact your administrator. |
| 5030 | USER_ALREADY_EXIST | User already exists | „Your account is already registered. **Sign In** now.“ (Link `/sign-in?email=…` ⇒ existiert nicht ⇒ 404) |
| 5035 | AUTHENTICATION_FAILED_SIGN_UP | Authentication failed | Authentication failed. Please try again. (setzt SIGN_UP + PASSWORD) |
| 5040 | REQUIRED_EMAIL_PASSWORD_SIGN_UP | Email and password required | Email and password required. Please try again. |
| 5045 | INVALID_EMAIL_SIGN_UP | Invalid email | Invalid email. Please try again. |
| 5050 | INVALID_EMAIL_MAGIC_SIGN_UP | Invalid email | Invalid email. Please try again. |
| 5055 | MAGIC_SIGN_UP_EMAIL_CODE_REQUIRED | Email and code required | Email and code required. Please try again. |
| 5060 | USER_DOES_NOT_EXIST | User does not exist | „No account found. **Create one** to get started.“ (Link `/?email=…`) |
| 5065 | AUTHENTICATION_FAILED_SIGN_IN | Authentication failed | Authentication failed. Please try again. (setzt SIGN_IN + PASSWORD) |
| 5070 | REQUIRED_EMAIL_PASSWORD_SIGN_IN | Email and password required | Email and password required. Please try again. |
| 5075 | INVALID_EMAIL_SIGN_IN | Invalid email | Invalid email. Please try again. |
| 5080 | INVALID_EMAIL_MAGIC_SIGN_IN | Invalid email | Invalid email. Please try again. |
| 5085 | MAGIC_SIGN_IN_EMAIL_CODE_REQUIRED | Email and code required | Email and code required. Please try again. |
| 5090 | INVALID_MAGIC_CODE_SIGN_IN | Authentication failed | Invalid magic code. Please try again. (SIGN_IN + UNIQUE_CODE) |
| 5092 | INVALID_MAGIC_CODE_SIGN_UP | Authentication failed | Invalid magic code. Please try again. (SIGN_UP + UNIQUE_CODE) |
| 5095 | EXPIRED_MAGIC_CODE_SIGN_IN | Expired magic code | Expired magic code. Please try again. (SIGN_IN + UNIQUE_CODE) |
| 5097 | EXPIRED_MAGIC_CODE_SIGN_UP | Expired magic code | Expired magic code. Please try again. (SIGN_UP + UNIQUE_CODE) |
| 5100 | EMAIL_CODE_ATTEMPT_EXHAUSTED_SIGN_IN | Expired magic code | Expired magic code. Please try again. (SIGN_IN + UNIQUE_CODE) |
| 5102 | EMAIL_CODE_ATTEMPT_EXHAUSTED_SIGN_UP | Expired magic code | Expired magic code. Please try again. (SIGN_UP + UNIQUE_CODE) |
| 5104 | OAUTH_NOT_CONFIGURED | OAuth not configured | OAuth not configured. Please contact your administrator. |
| 5105 | GOOGLE_NOT_CONFIGURED | Google not configured | Google not configured. Please contact your administrator. |
| 5110 | GITHUB_NOT_CONFIGURED | GitHub not configured | GitHub not configured. Please contact your administrator. |
| 5111 | GITLAB_NOT_CONFIGURED | GitLab not configured | GitLab not configured. Please contact your administrator. |
| 5115 | GOOGLE_OAUTH_PROVIDER_ERROR | Google OAuth provider error | Google OAuth provider error. Please try again. |
| 5120 | GITHUB_OAUTH_PROVIDER_ERROR | GitHub OAuth provider error | GitHub OAuth provider error. Please try again. |
| 5121 | GITLAB_OAUTH_PROVIDER_ERROR | GitLab OAuth provider error | GitLab OAuth provider error. Please try again. |
| 5125 | INVALID_PASSWORD_TOKEN | Invalid password token | Invalid password token. Please try again. |
| 5130 | EXPIRED_PASSWORD_TOKEN | Expired password token | Expired password token. Please try again. |
| 5135 | INCORRECT_OLD_PASSWORD | Incorrect old password | Incorrect old password. Please try again. |
| 5138 | MISSING_PASSWORD | Password required | Password required. Please try again. (**nicht** in der Banner-Liste ⇒ nie angezeigt) |
| 5140 | INVALID_NEW_PASSWORD | Invalid new password | Invalid new password. Please try again. |
| 5145 | PASSWORD_ALREADY_SET | Password already set | Password already set. Please try again. |
| 5150–5185 | Admin-Codes | wie 2.11 | (Links `/admin` relativ zu `/spaces`) |

Nicht gemappt (kein Banner), obwohl vom Backend definiert (`API/authentication/adapter/error.py`): `5016 MAGIC_LINK_LOGIN_DISABLED`, `5018 PASSWORD_LOGIN_DISABLED`, `5021 PASSWORD_TOO_WEAK`, `5056 EMAIL_PASSWORD_AUTHENTICATION_DISABLED`, `5112 GITEA_NOT_CONFIGURED`, `5122 GITHUB_USER_NOT_IN_ORG`, `5123 GITEA_OAUTH_PROVIDER_ERROR`, `5124 OAUTH_PROVIDER_UNVERIFIED_EMAIL`, `5190 ADMIN_USER_DEACTIVATED`, `5900 RATE_LIMIT_EXCEEDED`, `5999 AUTHENTICATION_FAILED`. Pseudo-Code `"5006"` (s. 3.18) liefert `undefined`.

### 2.22 Space – Komponenten-Detailmaße (für 1:1-Nachbau)

| Komponente | Wichtige Klassen / Maße / Verhalten | Quelle |
|---|---|---|
| Board-Shell | `relative flex h-screen min-h-[500px] w-screen flex-col overflow-hidden`; Navbar-Zeile `h-[60px] border-b border-subtle-1 bg-surface-1 select-none`; Inhalt `bg-surface-2` | `SPC/app/issues/[anchor]/layout.tsx` |
| Navbar links | Logo-Kachel 28 px (`ProjectLogo` `text-16`, Fallback `ProjectsOutline` 16 px), Name `text-16 font-medium max-w-[300px] line-clamp-1`, Platzhalter `...` | `navbar/root.tsx` |
| Layout-Umschalter | `rounded-sm bg-layer-2 p-1 gap-1`; Buttons `h-[22px] w-7`; aktiv `bg-layer-transparent-active`, Icon 14 px `text-primary` (sonst `text-secondary`); Tooltip „List“/„Board“ | `navbar/layout-selection.tsx` |
| Theme-Button | `size-7 rounded-sm`; Icon `MoonOutline` (Theme light) bzw. `AppearanceOutline` (sonst), 14 px | `navbar/theme.tsx` |
| User-Button | secondary md mit `Avatar size=2xs` + Name; Menü `side=bottom align=end sizing=auto` mit „Sign out“ (Icon Tint `danger`); anonym: Button „Sign in“ (secondary sm) | `navbar/user-avatar.tsx` |
| Filter-Button | Propel `Popover` + Button „Filters“ (secondary sm), `PopoverContent variant="rich"` (min. 320 px), Inhalt `max-h-[37.5rem]`; Platzierung `bottom-end` | `filters/helpers/dropdown.tsx` |
| Filter-Suche | `rounded-sm border-[0.5px] border-subtle bg-surface-2 px-1.5 py-1 text-11`, Icon `SearchOutline` 12 px, Placeholder „Search“, Löschen-X | `filters/selection.tsx` |
| Filter-Option | Checkbox 12 px (`rounded-xs`, aktiv `border-accent-strong bg-accent-primary text-on-color` + `TickOutline` 10 px), Icon-Spalte 20 px, Titel `text-11 text-secondary` | `filters/helpers/filter-option.tsx` |
| Aktive-Filter-Leiste | `border-b border-subtle bg-surface-1 p-4`; Gruppe `rounded-md border px-2 py-1 capitalize`, Key `text-11 text-tertiary` (Unterstriche → Leerzeichen); Chips `rounded-sm bg-layer-3 p-1 text-11`; „Clear all“ | `filters/applied-filters/*` |
| List-Gruppenkopf | sticky, `px-2 py-1.5 hover:bg-layer-transparent-hover`, Icon 14 px (Fallback lucide `CircleDashed`), Titel `font-medium`, Zähler `pl-2 text-13 text-tertiary`; Klick klappt Gruppe | `list/headers/group-by-card.tsx` |
| List-Zeile | `min-h-11 p-3 pl-1.5 text-13 border-b-subtle`, Hover `bg-layer-transparent-hover`; aktiv (gepeekt) `border-accent-strong!`; Key `px-4 text-11 font-medium text-tertiary`; Titel truncate mit Tooltip (`side=top align=start`); Properties rechts | `list/block.tsx` |
| List-„Load more“ | `h-11 border-t-subtle-1 bg-surface-1 p-3 pl-6 text-13 font-medium text-accent-primary` „Load more ↓“; Loader-Zeile `h-11` mit Pulse-Platzhaltern | `list/list-group.tsx` |
| Kanban-Spalte | Breite 350 px, `gap-2 px-2`; Kopf sticky `py-1` (Icon 20 px, Titel, Zähler); Spalte `min-h-[120px]`, eigener Scroll `vertical-scrollbar scrollbar-md` | `kanban/default.tsx`, `kanban/kanban-group.tsx` |
| Kanban-Karte | Wrapper `p-1.5`; Karte `rounded-lg border border-subtle bg-layer-2 text-13 hover:bg-layer-2-hover`, gepeekt `border-accent-strong`; Inhalt `px-3 py-2 space-y-2`: Key `text-11 text-tertiary`, Titel `text-13 line-clamp-1` + Tooltip, Properties `pt-1.5 gap-2`; Reaktionsleiste `border-t-subtle-1 bg-surface-2 rounded-b-lg px-3 py-2` (Votes `size=sm`, Trenner `after:h-6 after:w-[1px] after:bg-layer-3`, Emoji-Reaktionen) | `kanban/block.tsx`, `kanban/block-reactions.tsx` |
| Kanban-Loader | `m-1.5 h-28 animate-pulse rounded-sm bg-[var(--illustration-fill-quaternary)]` (3 Stück, letzter als Intersection-Ziel) | `kanban/kanban-group.tsx` |
| Property-Chips | jeweils `h-5`, `rounded-sm border-[0.5px] border-strong px-2.5 py-1 text-11`; State (`StateGroupIcon` + Name, Tooltip „State: …“), Priority (`PriorityIcon` size-3.5, kompakt `px-0.5`, Farbklassen `text-priority-{urgent,high,medium,low,none}`, Tooltip „Priority: …“), Labels (≤ 2 einzeln mit Farbpunkt 8 px & max-w 100 px, > 2 als „{n} Labels“ mit Accent-Punkt; leer: Icon `LabelsOutline` + Tooltip „Labels: None“), Due Date (`DueDateOutline`, Format `MMM dd, yyyy`, überfällig `text-danger-primary`, leer „No Date“) | `properties/*.tsx` |
| Peek „side“ | `fixed top-0 right-0 z-20 h-full w-1/2 border-l border-subtle-1 bg-surface-1 shadow-raised-200` | `peek-overview/layout.tsx` |
| Peek „modal“ | Backdrop `fixed inset-0 z-20 bg-backdrop animate-fade-in`; Panel zentriert `h-[70%] w-3/5 rounded-lg bg-surface-1` | dito |
| Peek „full“ | Panel `size-[95%]`; Grid 10 Spalten: 7 (Header, Details, Kommentare) / 3 (Properties), `divide-x divide-subtle-1` | `peek-overview/full-screen-peek-view.tsx` |
| Peek-Header | `p-5`; links (nur side) Schließen-Pfeil `ArrowNarrowRightOutline`, Modus-Select (`@plane/blocks/select` `variant="icon-sm"`, Optionen „Side Peek“, „Modal“, „Full Screen“ mit Icons; bei `full` Trigger `rotate-45`); rechts Copy-Link-Icon (`LinkOutline` -45°) nur bei Clipboard-Permission und Modus side/modal | `peek-overview/header.tsx` |
| Peek-Details | Key `text-14 font-medium text-placeholder`, Titel `text-20 font-medium break-words`, Beschreibung Rich-Text read-only (`min-h-[100px] py-2`, `large-font`), Reaktionen `mt-4 gap-3` | `peek-overview/issue-details.tsx` |
| Peek-Properties | Zeilen `h-8`, Label-Spalte `w-1/4 text-13 text-tertiary` mit Icon 16 px („State“, „Priority“, „Due date“), Werte `w-3/4`; Priority-Pill `rounded-sm bg-layer-2 px-2.5 py-0.5 capitalize`; leeres Datum „Empty“ | `peek-overview/issue-properties.tsx` |
| Kommentar-Karte | Avatar 28 px (Bild oder Initiale auf `bg-gray-500`), Chat-Badge unten rechts; Name `text-11`; „commented “ `text-11 text-secondary`; Inhalt Lite-Editor read-only `small-font` in Box `rounded-sm border border-subtle p-3`; Aktionsmenü (`IconButton ghost sm`, `MoreVerticalOutline`) mit „Edit“/„Delete“ | `comment/comment-detail-card.tsx` |
| Kommentar-Composer | Lite-Editor editierbar + Toolbar (`TOOLBAR_ITEMS.lite`, Gruppen mit `border-r`, Buttons 14 px, Tooltip mit Shortcut) + Button „Comment“ (primary sm, deaktiviert bei leerem Inhalt); Placeholder „Add comment...“ | `comment/add-comment.tsx`, `editor/toolbar.tsx` |
| Sign-in-Hinweis (Kommentare) | `rounded-sm border border-strong bg-layer-2 px-2 py-2.5`, `LockOutline` + „Sign in to add your comment“ + Button „Sign in“ (primary sm) | `peek-overview/issue-activity.tsx` |
| Votes | Buttons `rounded-sm border`, md `px-2 h-7` / sm `px-1 h-6 min-w-9`; Up (`TopArrowOutline`), aktiv `border-accent-strong-200 text-accent-secondary`; Down (`ArrowDownOutline`), aktiv `border-danger-strong text-danger-primary`; Zahl `text-13` | `reactions/issue-vote-reactions.tsx` |
| Powered-by | `fixed right-5 bottom-2.5 z-[999999] rounded-sm border border-subtle bg-layer-3 px-2 py-1 shadow-raised-100`, `PlaneLogo` h-3, „Powered by **Plane Publish**“ `text-11`, Link `WEBSITE_URL` (neuer Tab) | `common/powered-by.tsx` |
| Auth-Seite | `h-screen w-screen px-8 pt-6 pb-10 bg-surface-1`, Header `PlaneLockup 95×20`; Formular `mt-10 max-w-[22.5rem] gap-6`; Überschriften `text-20 font-semibold` (Zeile 2 `text-placeholder`); Inputs `h-10 rounded-md border bg-surface-1 px-3` (Fehler `border-danger-strong`); OAuth-Buttons `h-9 rounded-md border border-strong` (kompakt nebeneinander nur Icons) + Trenner „or“ | `components/account/**`, `packages/blocks/src/auth/oauth/*` |

### 2.23 Space – Hart codierte UI-Texte (vollständig, außer 2.21)

| Ort | Text(e) | Quelle |
|---|---|---|
| Auth-Header SIGN_UP (Default) | „View, comment, and do more“ / „Sign up or log in to work with Plane work items and Pages.“ | `auth-header.tsx` |
| Auth-Header SIGN_IN | „Sign in to upvote or comment“ / „Contribute in nudging the features you want to get built.“ | dito |
| Auth-Header Fallback (ohne Modus, praktisch unerreichbar) | „Comment or react to work items“ / „Use plane to add your valuable inputs to features.“ | dito |
| E-Mail-Step | Label „Email“, Placeholder „name@company.com“, Fehler „Email is invalid“, `aria-label="Clear email"`, Button „Continue“ | `email.tsx` |
| Passwort-Step | „Email“, „Password“ / „Set a password“, Placeholder „Enter password“, „Confirm password“, „Passwords don't match“, Buttons „Continue“ / „Go to workspace“ (SIGN_IN ohne SMTP), „Sign in with unique code“, „Create account“; `aria-label` „Show password“/„Hide password“ | `password.tsx` |
| Unique-Code-Step | „Unique code“, Placeholder „123456“, „Paste the code sent to your email“, „Resend in {n}s“, „Requesting new code“, „Resend“, Buttons „Sending code“/„Continue“ | `unique-code.tsx` |
| OAuth-Buttons | „{Sign up\|Sign in} with Google\|GitHub\|GitLab\|Gitea“; Trenner „or“ | `hooks/oauth/core.tsx`, `packages/blocks/src/auth/oauth/oauth-options.tsx` |
| Terms | „By creating an account, you agree to our Terms of Service and Privacy Policy.“ bzw. „By signing in, you agree to our …“ (Links `https://plane.so/legals/terms-and-conditions`, `https://plane.so/legals/privacy-policy`) | `terms-and-conditions.tsx` |
| Eingeloggt-Ansicht | „Nice! Just one more step.“ / „Enter the public-share URL or link of the view or Page you are trying to see in the browser's address bar.“ | `user-logged-in.tsx` |
| Instanzfehler | „Unable to fetch instance details.“ / „We were unable to fetch the details of the instance. <br/> Fret not, it might just be a connectivity work items.“ (sic – Suchen/Ersetzen-Artefakt „issue“→„work items“), Button „Retry“ | `instance-failure-view.tsx` |
| 404 (Catch-all) | „That didn't work“ / „Check the URL you are entering in the browser's address bar and try again.“ | `SPC/app/not-found.tsx` |
| 404 (Anchor) | „Oops! Something went wrong.“ / „Sorry, the page you are looking for cannot be found. It may have been removed, had its name changed, or is temporarily unavailable.“ | `components/ui/not-found.tsx` |
| Board-Fehler | „Oops! Something went wrong.“ / „The public board does not exist. Please check the URL.“ | `issue-layouts/error.tsx` |
| Fehlerseite | „Yikes! That doesn't look good.“ / „That crashed Plane, pun intended. No worries, though. Our engineers have been notified. If you have more details, please write to support@plane.so or on our Forum.“ (Links `mailto:support@plane.so`, `https://forum.plane.so`), Button „Refresh“ | `SPC/app/error.tsx` |
| Leerzustand | „No work items found“ | `issue-layout-HOC.tsx` |
| Gruppenspalten | „All work items“ (Default-Gruppe), „None“ (Cycle/Module/Label/Assignee), Kanban „Load More ↓“ (Sub-Gruppen) | `issue-layouts/utils.tsx`, `kanban/kanban-group.tsx` |
| Property-Tooltips | „State: {name}“, „Priority: {Titel}“, „Labels: None“, „Labels: {name}“, „Labels: {a, b, …}“, „{n} Labels“, „Due Date: {Datum\|No Date}“, „No Date“, „Cycle: {name\|No Cycle}“, „Modules: {liste\|None}“, „No Modules“, „{n} Modules“, „No Assignees“, „Sub-work items: {n}“, „Attachments: {n}“, „Links: {n}“, Avatar-Gruppe „{n} total“ | `properties/*.tsx` |
| Filter | „Filters“, „Search“, „Priority (n)“, „State (n)“, „Label (n)“, „View all“, „View less“, „No matches found“ | `filters/*.tsx` |
| Peek | „Side Peek“, „Modal“, „Full Screen“, Toast „Link copied!“ / „Work item link copied to clipboard.“ (success, Header) bzw. „Work item link copied to clipboard“ (info, Properties) ; „State“, „Priority“, „Due date“, „Empty“; „Comments“; „Sign in to add your comment“, „Sign in“ | `peek-overview/*.tsx` |
| Kommentar | „commented “ (Zeitangabe fehlt, s. 3.28), „{first_name} Bot“, Placeholder „Add comment...“, Toast error „Error!“ / „Comment could not be posted. Please try again.“, Toolbar-Button „Comment“ | `comment/*.tsx`, `editor/toolbar.tsx` |
| Mention | „@deactivated user“ (unbekannt), „@{display_name}“ | `editor/embeds/mentions/user.tsx` |
| Votes | Tooltips „No upvotes yet“, „No downvotes yet“, Namensliste (max. 1000) + „ and {n} more“ | `reactions/issue-vote-reactions.tsx` |
| Navbar | „Sign in“, „Sign out“, Anzeigename-Fallback `display_name` → `"{first_name} {first_name}"` (sic) → `email` → „User“ | `navbar/user-avatar.tsx` |
| Powered by | „Powered by Plane Publish“ | `common/powered-by.tsx` |

### 2.24 Space – verwendete i18n-Schlüssel (Englisch-Werte aus `packages/i18n/src/locales/en/*.json`)

| Schlüssel | EN-Wert | Verwendung |
|---|---|---|
| `issue.layouts.list` | List | Tooltip Layout-Umschalter (`CONST/issue/layout.ts` `SITES_ISSUE_LAYOUTS`) |
| `issue.layouts.kanban` | Board | dito |
| `issue.priority.urgent` / `.high` / `.medium` / `.low` | Urgent / High / Medium / Low | Filter, Priority-Tooltip, Peek-Pill |
| `common.none` | None | Priorität „none“ |
| `common.search.no_matches_found` | No matches found | Prioritätsfilter |
| `common.load_more` | Load more | List-Gruppen |
| `common.clear_all` | Clear all | Aktive-Filter-Leiste |
| `common.work_item` | Work item | `aria-label` Peek-Panel (Fallback) |
| `close` | Close | `aria-label` Schließen-Pfeil |
| `copy_link` | Copy link | `aria-label` Copy-Button |
| `edit` | Edit | Kommentar-Menü |
| `delete` | Delete | Kommentar-Menü |
| `aria_labels.common.more_actions` | More actions | Kommentar-Menü-Trigger |

### 2.25 Space – Assets

| Datei | Verwendung |
|---|---|
| `SPC/app/assets/favicon/{apple-touch-icon.png,favicon-16x16.png,favicon-32x32.png,favicon.ico,site.webmanifest}` | Head |
| `SPC/app/assets/images/logo-spinner-{dark,light}.gif` | `LogoSpinner` |
| `SPC/app/assets/auth/background-pattern{,-dark}.svg` | Hintergrund Instanzfehler |
| `SPC/app/assets/instance/instance-failure{,-dark}.svg` | Instanzfehler |
| `SPC/app/assets/404.svg` | Anchor-404 |
| `SPC/app/assets/something-went-wrong.svg` | Catch-all-404, Board-Fehler |
| `SPC/app/assets/user-logged-in.svg` | Eingeloggt-Ansicht |
| `SPC/app/assets/logos/google-logo.svg`, `gitlab-logo.svg`, `gitea-logo.svg`, `github-black.png` (Dark-Theme!), `github-dark.svg` (Light-Theme) | OAuth-Buttons (18 px) |
| `SPC/app/assets/logos/github-square.svg`, `github-white.svg` | **ungenutzt** |
| `SPC/app/assets/instance/intake-sent-dark.png`, `intake-sent-light.png`, `plane-instance-not-ready.webp`, `plane-takeoff.png` | **ungenutzt** (Hinweis auf Bezahl-Features, 2.30) |
| `SPC/app/assets/project-not-published.svg` | **ungenutzt** |
| `SPC/app/assets/robots.txt` (`User-agent: * / Disallow: /`) | **nicht ausgeliefert** (nur Asset-Ordner) |

### 2.26 Space – Browser-Speicher, Cookies, SWR-Keys

| Art | Schlüssel | Verhalten | Quelle |
|---|---|---|---|
| localStorage | `theme` | next-themes (`light`/`dark`/`system`), Toggle in Navbar; beim Sign-out → `system` | `SPC/app/providers.tsx`, `SPC/store/root.store.ts` |
| localStorage | `userLanguage` | i18n-Sprache (nur gelesen) | `packages/i18n/src/core/instance.ts` |
| Cookie | `session-id` | App-Session (Login über Space setzt sie) | `API/settings/common.py` |
| SWR | `INSTANCE_INFO` | `revalidateOnFocus:false`, `revalidateIfStale:false`, `errorRetryCount:0` | `SPC/lib/instance-provider.tsx` |
| SWR | `CURRENT_USER` | `shouldRetryOnError:false`, `revalidateOnFocus:true`, `revalidateIfStale:true` | dito |
| SWR | `PUBLISH_SETTINGS_{anchor}` | SWR-Defaults (u. a. Revalidierung bei Fokus) | `SPC/app/issues/[anchor]/layout.tsx` |
| SWR | `PUBLIC_STATES_{anchor}`, `PUBLIC_LABELS_{anchor}` | SWR-Defaults | `SPC/app/issues/[anchor]/page.tsx` |
| SWR | `PUBLIC_ISSUES_{anchor}` | `revalidateIfStale:false`, `revalidateOnFocus:false` | `issue-layouts/root.tsx` |
| SWR | `currentUser` | nur in ungenutztem `useMention` | `SPC/hooks/use-mention.tsx` |

### 2.27 Gemeinsam – verwendete UI-Bausteine aus `@makeplane/propel` (npm 0.7.3) und `@plane/blocks`

Propel-Quellen liegen nur als gebündeltes Paket vor (Komponentenliste `dist/components/*`); `@plane/blocks` liegt im Repo unter `packages/blocks/src/*` (eigener Analysebereich). Anzahl = Anzahl importierender Dateien.

| Baustein | Admin | Space | Verwendung / Varianten |
|---|---|---|---|
| `@makeplane/propel/components/button` | 21 | 9 | `variant`: `primary`, `secondary`, `ghost`; `size`: `sm`, `md`, `lg`; `stretch`: `auto`, `full`; Props `label`, `loading`, `disabled`, `icon`, `iconPosition="end"`, `nativeButton={false}` + `render={<Link/>}` (Button als Link) |
| `…/tooltip` | 3 | 12 | `label`, `side` (`top`/`right`), `align`, `shortcut` |
| `…/switch` | 15 | 0 | `size="sm"`, `checked`, `onCheckedChange`, `disabled`, `aria-label`/`aria-labelledby` |
| `…/input` (`Input`, `InputGroup`) | 6 | 3 | `size`: `lg` (Admin), `xl` (Space-Auth); `InputGroup` mit Präfix-Text/Suffix-Buttons |
| `…/icon` | 2 | 2 | `<Icon icon={…} tint="tertiary"\|"danger"/>` |
| `…/anchor-button` | 4 | 0 | „Edit“-Link-Button (primary sm) |
| `…/menu` (`Menu`, `MenuTrigger`, `MenuContent`, `MenuGroup`, `MenuLabel`, `MenuItem`, `MenuSeparator`) | 1 | 2 | Base-UI-basiert; schließt bei Item-Klick (daher externe Sign-out-Formulare) |
| `…/avatar`, `…/avatar-group` | 0 | 3 / 1 | `size`: `2xs`, `xs`; `fallback`, `tooltip`, `overflowTooltip` |
| `…/workspace-avatar` | 1 | 0 | Admin-Avatar `size="sm"` |
| `…/select` (`Select`, `SelectTrigger`, `SelectContent`, `SelectList`, `SelectItem`) | 2 | 0 | `size="lg"`, `items`, `placeholder` |
| `…/popover` | 0 | 1 | `PopoverContent variant="rich"` |
| `…/icon-button` | 0 | 1 | `variant="ghost" size="sm"` |
| `…/dialog` | 1 | 0 | `DialogContent size="sm"`, `DialogMain/Header/Heading/Title/Body/Actions`, `onOpenChange`, `onOpenChangeComplete` |
| `…/checkbox` | 1 | 0 | Telemetrie-Checkbox |
| `…/breadcrumb` | 1 | 0 | `Breadcrumb`, `BreadcrumbList/Item/Link/Page/Separator` |
| `@makeplane/propel/styles` | via CSS | via `@plane/tailwind-config` | Design-Tokens (Farben `bg-layer-*`, `bg-surface-*`, `text-primary/secondary/tertiary/placeholder`, `border-subtle/strong`, Typo `text-11 … text-24`, `text-body-*`, `text-h5-semibold`, `text-caption-sm-regular`, Schatten `shadow-raised-100/200`, `animate-fade-in`) |
| `@plane/blocks/toast` (`setToast`, `setPromiseToast`, `PlaneToastProvider`) | 18 | 4 | Typen `success`, `error`, `info`; Promise-Toast mit `loading/success/error` |
| `@plane/blocks/dialog` (`ConfirmDialog`) | 1 | 0 | Discard-Dialog (`variant="primary"`, `hideIcon`) |
| `@plane/blocks/icons` (`PlaneLockup`, `PlaneLogo`, `PriorityIcon`, `StateGroupIcon`, `CycleGroupIcon`, Typen `ISvgIcons`, `TIssuePriorities`) | 0 | 13 | Space |
| `@plane/blocks/skeleton` (`Loader`, `Loader.Item`) | 0 | 4 | Peek/Filter-Lader |
| `@plane/blocks/emoji-reaction` (`EmojiReactionGroup`, `EmojiReactionPicker`, Typ `EmojiReactionType`) | 0 | 2 | Issue-/Kommentar-Reaktionen |
| `@plane/blocks/emoji-icon-picker` (`stringToEmoji`) | 0 | 2 | Dezimal-Codepoints → Emoji |
| `@plane/blocks/auth` (`OAuthOptions`, `PasswordStrengthIndicator`) | 0 | 2 | Space-Auth |
| `@plane/blocks/select` (`Select`, `Select.Trigger`) | 0 | 1 | Peek-Modus |
| `@plane/blocks/common` (`toSideAndAlign`, `TPopoverMenuPlacement`) | 0 | 1 | Filter-Popover |
| `@plane/editor` (`LiteTextEditorWithRef`, `RichTextEditorWithRef`, `TOOLBAR_ITEMS`, Typen) + `@plane/editor/styles` | 0 | 4 | Kommentar-Editor, Beschreibung read-only |
| Admin-lokal statt Propel | `Skeleton`, `PlaneLockup`, `PasswordStrengthIndicator`, `LogoSpinner` | – | Propel hat (laut Kommentaren) kein Skeleton/Lockup; `dist/components/{skeleton,logo-spinner}` existieren in 0.7.3 dennoch |

### 2.28 Gemeinsam – Icons

| Herkunft | Icons |
|---|---|
| `@makeplane/propel/icons` | `AccessAndRolesOutline`, `AppearanceOutline`, `ArrowDownOutline`, `ArrowNarrowLeftOutline`, `ArrowNarrowRightOutline`, `AttachOutline`, `BoardOutline`, `ChatOutline`, `ChevronDownOutline`, `ChevronUpOutline`, `CloseCircleOutline`, `CloseOutline`, `CopyOutline`, `CyclesOutline`, `DueDateOutline`, `FullScreenPeekOutline`, `Github`, `HelpOutline`, `HideOutline`, `ImageOutline`, `InfoOutline`, `KeyOutline`, `LabelsOutline`, `LinkOutline`, `ListOutline`, `LoadingOutline`, `LockOutline`, `LogOutOutline`, `MailOutline`, `MembersOutline`, `ModalPeekOutline`, `ModuleOutline`, `MonitorOutline`, `MoonOutline`, `MoreVerticalOutline`, `NewTabOutline`, `PagesOutline`, `PaletteOutline`, `PriorityOutline`, `ProjectsOutline`, `SearchOutline`, `SettingsOutline`, `ShowOutline`, `SidePeekOutline`, `StateOutline`, `ThoughtsOutline`, `TickCircleOutline`, `TickOutline`, `TopArrowOutline`, `UsageOutline`, `ViewsOutline`, `WarningCircleOutline`, `WorkspaceOutline` |
| `@plane/blocks/icons` | `PlaneLockup`, `PlaneLogo`, `PriorityIcon`, `StateGroupIcon`, `CycleGroupIcon` |
| `lucide-react` | `Menu` (Admin-Hamburger), `BrainCog` (Admin-Sidebar AI), `Circle` (Kanban-Kopf-Fallback), `CircleDashed` (List-Kopf-Fallback), `SignalHigh` (Priorität ohne Wert) |
| Font | `@fontsource/material-symbols-rounded` (Projekt-Icon `material-symbols-rounded`, Emoji-Objekt-Rendering), `@fontsource-variable/inter`, `@fontsource/ibm-plex-mono` |
| Inline-SVG | `ADM/components/common/plane-lockup.tsx` |

### 2.29 Gemeinsam – Build- und Laufzeitkonfiguration

| Thema | Admin | Space | Quelle |
|---|---|---|---|
| Router | React Router Framework, `ssr:false`, `future.unstable_optimizeDeps:true` | `ssr:true`, gleiche Future-Flags | `{ADM,SPC}/react-router.config.ts` |
| Env-Injektion | nur `VITE_*`-Variablen als `process.env` zur **Build-Zeit** (`define`) | dito | `{ADM,SPC}/vite.config.ts` |
| Aliase | `next/link`, `next/navigation` → Shims | nur `next/navigation` | dito |
| Build-Args (Docker) | `VITE_API_BASE_URL=""`, `VITE_API_BASE_PATH=/api`, `VITE_ADMIN_BASE_URL=""`, `VITE_ADMIN_BASE_PATH=/god-mode`, `VITE_SPACE_BASE_URL=""`, `VITE_SPACE_BASE_PATH=/spaces`, `VITE_LIVE_BASE_URL=""`, `VITE_LIVE_BASE_PATH=/live`, `VITE_WEB_BASE_URL=""`, `VITE_WEB_BASE_PATH=""`, `VITE_WEBSITE_URL=https://plane.so`, `VITE_SUPPORT_EMAIL=support@plane.so` | identisch | `{ADM}/Dockerfile.admin`, `{SPC}/Dockerfile.space` |
| Konstanten | `API_BASE_URL`, `WEB_BASE_URL`, `SUPPORT_EMAIL` | `API_BASE_URL`, `SPACE_BASE_PATH`, `WEBSITE_URL`, `SUPPORT_EMAIL`, `MAX_FILE_SIZE` (5 MB) | `CONST/endpoints.ts`, `CONST/file.ts` |
| Laufzeit | Caddy statisch | Node `react-router-serve` (SSR) | Dockerfiles |
| TS | `strict` via `@plane/typescript-config/react-router.json`, Lockerungen | dito + `strictNullChecks` | `tsconfig.json` |

### 2.30 Bezahl-Edition-Features mit Bezug zu A11 (nicht im Repo implementiert)

Gemäß ADR-001 sind diese Funktionen in der Zielplattform **immer aktiv** und müssen gebaut werden. Da der Code der Bezahl-Editionen nicht vorliegt, sind Inhalte aus Repo-Indizien abgeleitet; Spalte „Sicherheit“ bewertet, wie gut die UI aus dem Repo rekonstruierbar ist. Vor Umsetzung gegen eine Referenzinstanz (Plane Commercial Edition) verifizieren (s. Kapitel 6).

| # | Funktion | Plan (Plan-Matrix) | Evidenz im Repo | Erwarteter UI-Ort | Sicherheit | Ableitbarer Inhalt |
|---|---|---|---|---|---|---|
| EE1 | **OIDC-SSO (instanzweit)** | One/Pro/Business/Enterprise, `selfHostedOnly: true` | `apps/web/components/workspace/billing/comparison/plans.tsx` Z. 1071–1081; `CONST/subscription.ts` („OIDC + SAML for SSO“); `packages/i18n/src/locales/en/auth.json` `sso.providers.oidc.*` (Felder „Origin URL“, „Redirect URL“, „Logout URL“ je „Web details“/„Mobile details“) | God Mode `/authentication/` als zusätzliche Karte + Detailseite (analog GitHub) – Erweiterungspunkt `TExtendedInstanceAuthenticationModeKeys` (`TYPES/instance/auth-ee.ts`) und Flag `unavailable` (`TYPES/instance/auth.ts`, `ADM/components/authentication/authentication-method-card.tsx`) | mittel | Formular: Client-ID, Client-Secret, Authorize-/Token-/UserInfo-/Logout-URL, Anzeigename des Buttons; Plane-Werte: Origin-, Callback-, Logout-URL; Aktiv-Switch; Login-Button in Web/Space |
| EE2 | **SAML-SSO (instanzweit)** | One+ | `plans.tsx` Z. 1060–1069; `auth.json` `sso.providers.saml.*` („Entity ID \| Audience \| Metadata information“, „SSO URL“, „SLO URL“, „Mapping details“ IdP↔Plane) | wie EE1 | mittel | IdP-Felder: Entity-ID, SSO-URL, SLO-URL, Zertifikat, Anzeigename; Plane-Werte: Entity-ID/Metadata, ACS/SSO-URL, SLO-URL; Attribut-Mapping |
| EE3 | **LDAP-Login** | Enterprise („comingSoon“) | `plans.tsx` Z. 1117–1127; `CONST/subscription.ts` („LDAP support“); `auth.json` `auth.ldap.header` („Continue with {ldapProviderName}“, „Enter your {ldapProviderName} credentials“), `auth.common.username` | God Mode `/authentication/` + Login-Formular (Username statt E-Mail) in Web/Space | niedrig | Server-URI, Bind-DN, Bind-Passwort, Such-Basis, Filter, Attribut-Mapping, Anzeigename |
| EE4 | Workspace-weites SSO mit Domain-Verifikation | (Cloud/Business) | `auth.json` `sso.domain_management.*`, `sso.providers.*` (Platzhalter `{workspaceName}`) | **Web-App** Workspace-Settings (nicht A11) – nur zur Abgrenzung | hoch (Texte) | Verweis auf Analyse Web-Workspace-Settings |
| EE5 | **Publish Views** (öffentliche Ansichten) | Pro+ | `plans.tsx` Z. 510–518; `SPC/components/account/user-logged-in.tsx` („…view or Page…“); `API/db/models/deploy_board.py` `TYPE_CHOICES` (`view`) | Space-Route für View-Anchor (z. B. `/views/:anchor`) mit denselben Layouts/Filtern; Publish-Dialog an Views in der Web-App | niedrig | Board-Komponenten von `/issues/:anchor` wiederverwendbar; Filter/Display-Props der View |
| EE6 | **Publish Pages** (öffentliche Seiten, Kommentieren ohne Workspace-Login) | One+ | `plans.tsx` Z. 853–862; `TYPES/publish.ts` `TPublishEntityType = "project" \| "page"`; `SPC/hooks/use-editor-flagging.ts` (Flags für `document`-Editor); Auth-Header-Text „…work items and Pages.“ | Space-Route für Page-Anchor (z. B. `/pages/:anchor`) mit read-only Document-Editor (`@plane/editor`), ggf. Kommentare | niedrig | Document-Editor read-only, Asset-Auflösung über `/api/public/assets/v2/anchor/{anchor}/…` |
| EE7 | **Intake Forms** (öffentliches Einreichformular) | Business+ | `plans.tsx` Z. 447–455; `SPC/types/intake.d.ts` (`TIntakeIssueForm {name, email, username, description_html}`); ungenutzte Assets `SPC/app/assets/instance/intake-sent-{dark,light}.png`; Backend `API/space/urls/intake.py` + `API/space/views/intake.py` (`IntakeIssuePublicViewSet.create`: `issue.name` Pflicht, Priorität ∈ `low,medium,high,urgent,none`, HTML-Sanitizing, Triage-State wird bei Bedarf angelegt, `IntakeIssue(source=IN_APP)`); `DeployBoard.intake`-FK | Space-Route für Intake-Anchor (Formular + Erfolgsbild „intake sent“) | mittel (Backend), niedrig (UI) | Felder Name/E-Mail/Username/Beschreibung (Rich-Text), Absenden → `POST /api/public/anchor/{anchor}/intakes/{intakeId}/intake-issues/` |
| EE8 | Weitere Board-Layouts im Space (Calendar, Spreadsheet, Gantt) | Layouts generell alle Pläne; im Space nur List/Board umgesetzt | `TYPES/publish.ts` `TProjectPublishLayouts`, `TProjectPublishViewProps`; `SPC/store/issue-filters.store.ts` `layoutOptions`; `CONST/issue/filter.ts` `ISSUE_DISPLAY_FILTERS_BY_LAYOUT` (alle 5); `SPC/components/issues/navbar/controls.tsx` (akzeptiert alle 5 `board`-Werte) | Space-Board | niedrig | Read-only-Varianten der Web-Layouts (Analysebereich Web-Layouts) |
| EE9 | Swimlanes/Sub-Gruppierung im Board | – | `SPC/components/issues/issue-layouts/kanban/swimlanes.tsx` (fertig, aber nicht eingebunden) | Space-Board | hoch (Code vorhanden) | Nur relevant, wenn View-Publishing (EE5) Display-Filter mit `sub_group_by` überträgt |
| EE10 | Plan-gebundene Upload-Limits („Max file size“ 5/100/200 MB/Custom) | Free…Enterprise | `plans.tsx` Z. 1043–1052; `CONST/file.ts` `MAX_FILE_SIZE` = 5 MB (Space-Editor) | Space-Kommentar-Uploads | hoch | Laut ADR-001 als konfigurierbare Instanzeinstellung (z. B. `FILE_SIZE_LIMIT` aus `GET /api/instances/` → `config.file_size_limit`) statt fixer 5 MB |
| EE11 | Lizenz-/Plan-Verwaltung im God Mode | – | `TYPES/instance/base.ts` `license_key`, `API/license/models/instance.py` `edition` | – | – | **Entfällt** (ADR-001) |

---

## 3. Verhalten, Logik, Abläufe (inkl. Edge-Cases)

### 3.1 Admin – Bootstrapping & Provider-Kette

Reihenfolge (`ADM/app/root.tsx` → `ADM/providers/index.tsx` → `ADM/providers/core.tsx`):

1. `ThemeProvider` (next-themes; `themes=["light","dark"]`, `defaultTheme="system"`, `enableSystem`) – setzt Klasse/Attribut am `<html>`.
2. `AppProgressBar` – startet BProgress bei `navigation.state !== "idle"` (Delay 0, `minimum 0.1`, `speed 400`, `trickleSpeed 800`, kein Spinner); die Kommentar-Aussage „disabled in production“ ist **nicht** umgesetzt (`isDisabled` nie gesetzt).
3. `TranslationProvider` (`@plane/i18n`) → `PlaneToastProvider`.
4. `SWRConfig` mit Defaults (2.14).
5. `StoreProvider` (Singleton `rootStore`, `hydrate({})`).
6. `InstanceProvider` → SWR `INSTANCE_DETAILS` → `GET /api/instances/`.
7. `UserProvider` → SWR `CURRENT_USER` → `GET /api/instances/admins/me/` (bei Erfolg zusätzlich `GET /api/instances/admins/`), parallel SWR `INSTANCE_ADMINS` → `GET /api/instances/admins/` (doppelter Abruf); liest einmalig `localStorage["god_mode_sidebar_collapsed"]` (fehlend ⇒ `false`) und ruft `toggleSidebar(wert)`.
8. `ExtendedProviders` (leer).

`HydrateFallback` (Spinner) erscheint bis zur Client-Hydration; danach Routen.

### 3.2 Admin – Erst-Einrichtung (Instance Setup)

Bedingung: `GET /api/instances/` liefert `instance.is_setup_done === false` (`ADM/app/(all)/(home)/page.tsx`). Ablauf:

1. Formular lädt CSRF-Token (A1) in Hidden-Feld.
2. Query-Parameter-Vorbelegung (`first_name`, `last_name`, `company`, `email`, `is_telemetry_enabled`) – Details und Bugs in 2.9.
3. Client-Validierung (2.9) steuert nur die Button-Aktivierung; Namensfelder verwerfen unzulässige Tastendrücke.
4. Submit = **nativer Form-POST** (F2). `isSubmitting=true` (Button-Spinner), `onError` am `<form>` greift nie.
5. Backend (`API/license/api/views/admin.py` `InstanceAdminSignUpEndpoint`):
   - Throttle → bei Überschreitung Redirect mit 5900.
   - Keine Instanz → 5000.
   - `instance.is_setup_done` oder irgendein `InstanceAdmin` existiert → 5150.
   - Fehlende `email`/`password`/`first_name` → 5155 (+ Payload-Parameter).
   - E-Mail (lowercase/trim) ungültig → 5160.
   - E-Mail existiert bereits als User → 5180.
   - Passwort zxcvbn-Score < 3 → 5021.
   - Atomar mit Row-Lock: erneute Prüfung, `User` anlegen (`username = uuid4().hex`, `is_password_autoset=False`, `is_active=True`, Login-Metadaten), `Profile(company_name)`, `InstanceAdmin` (Rolle Default 20), Instanz: `is_setup_done=True`, `instance_name = company_name`, `is_telemetry_enabled = POST-Wert` (String „True“/„False“!).
   - `user_login(is_admin=True)` → Admin-Session (Expiry 3600 s), Redirect `…/god-mode/general/`.
6. **Edge-Case/Bug (1:1-relevant):** Die Setup-Seite vergleicht `error_code` mit Namen (`"ADMIN_ALREADY_EXIST"` …), das Backend liefert aber Ziffern (`"5150"`). Folge: **kein Fehlerbanner, keine Inline-Fehler** (E-Mail/Passwort) nach einem fehlgeschlagenen Setup – der Nutzer sieht nur das (teilweise vorbelegte) Formular erneut. Die Zweige für `INVALID_EMAIL`/`INVALID_PASSWORD`-Inline-Meldungen (`px-1 text-11 text-danger-primary`) sind damit toter Code (`ADM/components/instance/setup-form.tsx` Z. 103–122, 150–154, 232–234, 298–300).
7. Nach Setup: Dashboard; `NewUserPopup` erscheint, wenn beim **ersten** Laden der Instanzinfo `workspaces_exist === false` war (`ADM/store/instance.store.ts` Z. 108–110).

### 3.3 Admin – Anmeldung (Sign-in)

1. Bedingung: `is_setup_done === true` und nicht eingeloggt.
2. CSRF laden, `email` aus Query vorbelegen.
3. Native POST (F1). Backend-Prüfreihenfolge (`InstanceAdminSignInEndpoint`): Throttle (5900) → Instanz fehlt (5000) → Felder fehlen (5170, Payload `email`) → E-Mail ungültig (5160) → User fehlt (5185) → Bot-User (5175) → inaktiv (5190, **ohne** E-Mail-Payload) → Passwort falsch (5175) → kein `InstanceAdmin` (5175) → Login-Metadaten aktualisieren, `user_login(is_admin=True)` → Redirect `general/`.
4. Fehleranzeige: `authErrorHandler(error_code)` → `AuthBanner` für 5150–5190 (2.11). Der zusätzliche rote `Banner`-Zweig (Vergleich gegen Namen) ist wie beim Setup tot. Für 5000/5900 keine Anzeige.
5. Erfolgreich eingeloggt auf `/` (z. B. zurück-Navigation) → `replace("/general")`.

### 3.4 Admin – Abmeldung

`AdminSidebarDropdown` hält ein **verstecktes Formular außerhalb des Menüs** (Grund: Menü unmountet Items beim Klick). Klick „Sign out“ → `form.requestSubmit()` → `onSubmit` → `userStore.signOut()` → `RootStore.resetOnSignOut()` (`localStorage.theme="system"`, Stores neu) → nativer POST F3 → Backend setzt `last_logout_ip/time`, `logout()`, Redirect `…/god-mode/` (auch bei Fehler). CSRF-Token wird beim Mount geladen; ist er noch nicht da, wird ein leeres Token gesendet (→ Django-CSRF-Fehlerseite `plane.authentication.views.common.csrf_failure`).

### 3.5 Admin – Layout-Guards

| Zustand `isUserLoggedIn` | Home-Layout `/` | Dashboard-Layout |
|---|---|---|
| `undefined` (lädt) | Seite rendert (Spinner bis Instanzinfo) | zentrierter `LogoSpinner` |
| `true` | `replace("/general")` | Shell (Sidebar, Header, Outlet, NewUserPopup) |
| `false` | Setup/Sign-in | `replace("/")`, rendert `<></>` |

Da `fetchCurrentUser` bei 401/403 wirft, wird `isUserLoggedIn=false` gesetzt (kein Retry). Session-Ablauf (1 h) während der Nutzung: Folge-Requests liefern 403, Stores behalten aber `isUserLoggedIn=true` bis zum nächsten erfolgreichen/fehlschlagenden `CURRENT_USER`-Refresh (Polling 10 min) – Formulare zeigen bis dahin nur generische Fehler-Toasts bzw. `console.error`.

### 3.6 Admin – Sidebar-, Header- und Theme-Verhalten

- **Breite:** 290 px / eingeklappt 70 px; `md:relative`, darunter `fixed` Overlay (`z-20`).
- **Auto-Collapse:** Beim Mount und bei jedem `resize` mit `window.innerWidth <= 768` → `toggleSidebar(true)` (überschreibt gespeicherten Zustand) (`sidebar.tsx` Z. 32–43).
- **Outside-Click:** bei `< 768 px` und ausgeklappt → einklappen (`useOutsideClickDetector`).
- **Menü-Klick:** bei `< 768 px` → Zustand invertieren.
- **Eingeklappt:** Kopf zeigt nur Kachel (Menü über Kachel klickbar, sonst `cursor-default`), Menüeinträge nur Icons + Tooltip rechts, Fußzeile vertikal (Tooltip-Varianten).
- **Ausgeklappt:** Avatar-Menü rechts im Kopf (nur wenn `currentUser`); Kachel-Menü nur im eingeklappten Zustand aktiv.
- **Hamburger** im Header nur `< md`, invertiert Zustand.
- **Theme-Wechsel:** Menüeintrag „Switch to dark mode“/„Switch to light mode“ abhängig von `resolvedTheme`; `setTheme` von next-themes (persistiert `localStorage.theme`).
- **Breadcrumb:** s. 2.5; Edge-Case: wird eine URL **ohne** abschließenden Slash direkt aufgerufen (z. B. `/god-mode/general`), entfernt `pop()` das echte Segment → nur „Settings“ sichtbar; ebenso ist dann kein Sidebar-Eintrag aktiv (`"/general".startsWith("/general/")` = false).
- **Hilfe-Popover:** Toggle per Klick, schließt nicht bei Outside-Click, Einblend-Animation ohne Ausblenden; „Redirect to Plane“ = `encodeURI(WEB_BASE_URL + "/")` (bei leerem `WEB_BASE_URL` → `/` derselben Origin).

### 3.7 Admin – General (`/general/`)

Header: Titel „General settings“, Beschreibung „Change the name of your instance and instance admin e-mail addresses. Enable or disable telemetry in your instance.“ Formular nur, wenn `instance` und `instanceAdmins` geladen (sonst leer, kein Skeleton). Speichern → A3 mit `{instance_name, is_telemetry_enabled}` → Toast. Durch den Store-Bug (2.6) wird `instance.instance_name` im Store nicht aktualisiert; das Formular behält aber seine Eingabe. Der Switch ist während `isSubmitting` deaktiviert (`opacity-70`). Fehler nur `console.error`.

### 3.8 Admin – Email/SMTP (`/email/`)

- Header: Titel „Secure emails from your own instance“; Beschreibung „Plane can send useful emails to you and your users from your own instance without talking to the Internet.“ + zweite Zeile „Set it up below and please test your settings before you save them. **Misconfigs can lead to email bounces and errors.**“ (rot). Header-Action: Switch „Enable SMTP email“ (beim Laden Skeleton-Pille 24×16 px).
- Switch-Zustand initial `ENABLE_SMTP === "1"`. **Einschalten** setzt nur lokalen Zustand (zeigt Formular, nichts gespeichert, bis „Save changes“). **Ausschalten** (wenn an) ruft `disableEmail()` (A8) – setzt auch lokal SMTP-Werte leer – und Toast „Email feature disabled“.
- Formular nur bei aktivem lokalem Switch; Skeleton (5 Balken) solange `formattedConfig` fehlt.
- Speichern sendet alle 8 Email-Keys + `ENABLE_SMTP:"1"` (A7).
- Security-Select: abgeleitet aus TLS/SSL (`TLS` wenn `EMAIL_USE_TLS=="1"`, sonst `SSL` wenn `EMAIL_USE_SSL=="1"`, sonst „No email security“); Auswahl setzt beide Felder exklusiv.
- **Test-E-Mail** (`SendTestEmailModal`): nutzt die **gespeicherte** Konfiguration (Backend `get_email_configuration()`), nicht die Formularwerte. Fehlermeldungen des Backends (A9): „Receiver email is required“, „Invalid email header.“, „Invalid credentials provided“, „Could not connect with the SMTP server.“, „From address is invalid.“, „SMTP server disconnected unexpectedly.“, „All recipient addresses were refused.“, „Timeout error while trying to connect to the SMTP server.“, „Network connection error. Please check your internet connection.“, „Could not send email. Please check your configuration“. Der Dialog schließt bei Outside-Click/Escape; Zustand wird nach der Schließanimation zurückgesetzt (`onOpenChangeComplete`).

### 3.9 Admin – Authentifizierung (`/authentication/`)

- Header: „Manage authentication modes for your instance“ / „Configure authentication modes for your team and restrict sign-ups to be invite only.“
- Zeile 1: „Allow anyone to sign up even without an invite“ (`text-16 font-medium`) / „Toggling this off will only let users sign up when they are invited.“ – Switch toggelt `ENABLE_SIGNUP` sofort (A7, Promise-Toast).
- „Available authentication modes“ (`text-lg pt-6`), danach 6 Karten in fester Reihenfolge (`ADM/hooks/oauth/index.ts`):

| # | Key | Name | Beschreibung | Icon | Steuerung | `enabledConfigKey` |
|---|---|---|---|---|---|---|
| 1 | `unique-codes` | Unique codes | Log in or sign up for Plane using codes sent via email. You need to have set up SMTP to use this method. | `MailOutline` 24 px | Switch | `ENABLE_MAGIC_LINK_LOGIN` |
| 2 | `passwords-login` | Passwords | Allow members to create accounts with passwords and use it with their email addresses to sign in. | `KeyOutline` | Switch | `ENABLE_EMAIL_PASSWORD` |
| 3 | `google` | Google | Allow members to log in or sign up for Plane with their Google accounts. | `google-logo.svg` 20 px | Configure/Edit+Switch | `IS_GOOGLE_ENABLED` |
| 4 | `github` | GitHub | Allow members to log in or sign up for Plane with their GitHub accounts. | GitHub-PNG (themenabhängig) | Configure/Edit+Switch | `IS_GITHUB_ENABLED` |
| 5 | `gitlab` | GitLab | Allow members to log in or sign up to plane with their GitLab accounts. | `gitlab-logo.svg` | Configure/Edit+Switch | `IS_GITLAB_ENABLED` |
| 6 | `gitea` | Gitea | Allow members to log in or sign up to plane with their Gitea accounts. | `gitea-logo.svg` | Configure/Edit+Switch | `IS_GITEA_ENABLED` |

- „Konfiguriert“-Regel (`ADM/components/authentication/*-config.tsx`): Google/GitHub/GitLab: `CLIENT_ID` und `CLIENT_SECRET` nicht leer; Gitea zusätzlich `GITEA_HOST`. Nicht konfiguriert → Button „Configure“ (secondary sm, Icon `SettingsOutline`) → Detailseite; konfiguriert → „Edit“ (primary sm Anchor-Button) + Switch.
- **Mindestens-eine-Methode-Regel** (`ADM/helpers/authentication.ts`): Beim Setzen eines `enabledConfigKey` auf `"0"` wird gezählt, wie viele der 6 `enabledConfigKey` aktuell `parseInt(...)` truthy sind; ist die zu deaktivierende Methode aktiv und die einzige → Fehler-Toast „Cannot disable authentication“, kein Request. `ENABLE_SIGNUP` ist kein Methoden-Key und unterliegt der Regel nicht. Die Regel gilt **nicht** auf den Provider-Detailseiten (dort kann die letzte Methode deaktiviert werden) und nicht im Backend.
- Während eines Requests sind alle Switches deaktiviert (`isSubmitting`).
- Skeleton (5 Balken), solange `formattedConfig` fehlt.

### 3.10 Admin – Provider-Detailseiten (`/authentication/{github,google,gitlab,gitea}/`)

- `PageWrapper customHeader`: `AuthenticationMethodCard` ohne Rahmen (`withBorder=false`, Name `text-18`), Beschreibungen: GitHub „Allow members to login or sign up to plane with their GitHub accounts.“, Google „Allow members to login or sign up to plane with their Google accounts.“, GitLab „Allow members to login or sign up to plane with their GitLab accounts.“, Gitea „Allow members to login or sign up to plane with their Gitea accounts.“; Icon 24 px; Switch toggelt `IS_<PROVIDER>_ENABLED` sofort (unabhängig davon, ob Credentials gesetzt sind).
- Formular (2.9) mit `defaultValues` aus `formattedConfig`; Speichern sendet **alle** Formularfelder; danach `reset()` mit Werten aus der Antwort (entschlüsselte Secrets) ⇒ `isDirty=false`.
- „Go back“: bei `isDirty` → `ConfirmDiscardModal` („Go back“ navigiert zu `/authentication/`, „Keep editing“ schließt).
- Copy-Felder: URL wird per `navigator.clipboard.writeText` kopiert (ohne Fallback), Info-Toast.
- Secrets werden im Klartext aus dem Backend geladen und als Passwortfeld angezeigt (Auge-Toggle zeigt sie an) – Sicherheitsaspekt für Migration (5.4).
- Skeleton (5 Balken) solange keine Konfiguration.
- Callback-Pfade: `/auth/github/callback/`, `/auth/google/callback/`, `/auth/gitlab/callback/`, `/auth/gitea/callback/` relativ zu `originURL` (API-Origin). Die Space-eigenen Callback-Endpunkte (`/auth/spaces/{provider}/callback/`) werden im God Mode **nicht** angezeigt.

### 3.11 Admin – AI (`/ai/`)

Header: „AI features for all your workspaces“ / „Configure your AI API credentials so Plane AI features are turned on for all your workspaces.“ Skeleton (1 breiter Balken, 2er-Grid, 1 kurzer Balken). Speichern sendet `LLM_API_KEY`, `LLM_MODEL` (A7). `LLM_PROVIDER` ist nur per ENV/DB änderbar.

### 3.12 Admin – Bilder (`/image/`)

Header: „Third-party image libraries“ / „Let your users search and choose images from third-party libraries“. Skeleton (2 Balken). Pflichtfeld `UNSPLASH_ACCESS_KEY` (leer speichern über UI nicht möglich, Pflichtregel).

### 3.13 Admin – Workspaces (`/workspace/`, `/workspace/create/`)

- Header: „Workspaces on this instance“ / „See all workspaces and control who can create them.“
- Switch „Prevent anyone else from creating a workspace.“ / „Toggling this on will let only you create workspaces. You will have to invite users to new workspaces.“ → `DISABLE_WORKSPACE_CREATION` (A7, Promise-Toast). Skeleton (1 Balken) bis Konfiguration geladen.
- Liste: bis `loader !== "init-loader"` Skeleton (Balken 24 px, 3 × 92 px). Kopf „All workspaces on this instance • {Anzahl geladener}“ (zählt geladene, nicht Gesamtzahl) + Spinner (`LoadingOutline animate-spin`) bei `mutation`/`pagination`; Button „Create workspace“ (primary sm, Link).
- Einträge: Klick öffnet `${WEB_BASE_URL}/${encodeURIComponent(slug)}` in neuem Tab. Logo: `logo_url` (über `getFileURL`), sonst erster Buchstabe; Name `capitalize`; „/“; `[slug]` mit Tooltip; Owner-E-Mail; „Total projects“ / „Total members“ (nur wenn nicht `null`).
- „Load more“ (ghost md) wenn `paginationInfo.next_page_results && next_cursor !== undefined`; 10 je Seite.
- Anlegen: `handleSubmit` → A11 Slug-Check → wenn `status === true` **und** Slug nicht in `RESTRICTED_URLS` (Frontend-Liste `CONST/workspace.ts`: `404, accounts, api, create-workspace, god-mode, installations, invitations, onboarding, profile, spaces, workspace-invitations, password, flags, monitor, monitoring, ingest, plane-pro, plane-ultimate, enterprise, plane-enterprise, disco, silo, chat, calendar, drive, channels, upgrade, billing, sign-in, sign-up, signin, signup, config, live, admin, m, import, importers, integrations, integration, configuration, initiatives, initiative, config, workflow, workflows, epics, epic, story, mobile, dashboard, desktop, onload, real-time, one, pages, mobile, business, pro, settings, monitor, license, licenses, instances, instance`) → A12 → Toast + `router.push("/workspace")`; sonst „This URL is taken. Try something else.“. Beim Unmount werden die Eingaben in `defaultValues` übernommen (bleiben beim Zurücknavigieren nicht erhalten, da Komponente neu erstellt wird).
- Das Backend verbindet den Admin als Workspace-Admin (Rolle 20); `company_role` aus Request (UI sendet keins).

### 3.14 Admin – Sonstiges

- **NewUserPopup** (unten rechts im Dashboard): „Close“ toggelt `isNewUserPopup`; wird nicht persistiert (erscheint bei jedem Neuladen erneut, solange keine Workspaces existieren).
- **404** außerhalb des Dashboards (kein Login-Guard).
- **Progressbar**: nur bei Router-Navigationen.
- **Polling**: Alle SWR-Keys werden alle 10 Minuten neu geladen, auch `INSTANCE_CONFIGURATIONS` – laufende Formulare werden dadurch nicht zurückgesetzt (react-hook-form-`defaultValues` werden nur initial gelesen), Switch-Seiten zeigen aber den neuen Serverzustand.

### 3.15 Space – Bootstrapping

1. **Server (SSR):** `react-router-serve` rendert `Layout` + Providers; für `/issues/:anchor` läuft der Server-`loader` (B8) für Meta-Tags. `InstanceProvider` rendert auf dem Server einen Spinner (kein Instance-Wissen), daher ist der SSR-Body im Wesentlichen ein Spinner + Meta.
2. **Client:** `entry.client.tsx` wartet auf `initPromise` von i18n (lädt alle Namespaces der Sprache aus `localStorage.userLanguage` bzw. `en`), dann `hydrateRoot`.
3. Provider (`SPC/app/providers.tsx`): `ThemeProvider` → `StoreProvider` → `AppProgressBar` → `TranslationProvider` → `ToastProvider` → `InstanceProvider`.
4. `InstanceProvider` startet parallel B1 (`INSTANCE_INFO`) und B2 (`CURRENT_USER`; bei Erfolg B3). Bis Instanz da: Spinner. Instanzfehler: Vollbild mit Logo-Link (`Link to={SPACE_BASE_PATH + "/"}` – relativ zum Router-Basename ⇒ **`/spaces/spaces/`**), Hintergrundmuster (`background-pattern{-dark}.svg`) und `InstanceFailureView`. `is_setup_done=false` wird **nicht** gesondert behandelt.

### 3.16 Space – Startseite `/`

| Zustand | Anzeige |
|---|---|
| `isInitializing` (User lädt) | Spinner `h-screen min-h-[500px]` |
| eingeloggt + gültiger `next_path` | Spinner + `router.replace(next_path)` (mit Trailing-Slash-Shim: `/issues/abc?board=list` → `/issues/abc/?board=list`) |
| eingeloggt ohne/ungültiger `next_path` | `UserLoggedIn`: Kopfzeile (Lockup + `UserAvatar`), Bild `user-logged-in.svg` in Kreis (`size-32 md:size-52 bg-layer-1`), Texte (2.23), `PoweredBy` |
| anonym | `AuthView` |

### 3.17 Space – Authentifizierungsablauf

Zustände: `authMode` (Default `SIGN_UP`), `authStep` (Default `EMAIL`), `email` (aus Query), `errorInfo`, `isPasswordAutoset` (Default `true`, nur gesetzt, nie gelesen). Konfiguration aus `instance.config`.

1. **Fehler aus URL** (`error_code`): Banner (2.21); Sonderfälle setzen Modus/Step: 5065 → SIGN_IN/PASSWORD; 5035 → SIGN_UP/PASSWORD; 5090/5095/5100 → SIGN_IN/UNIQUE_CODE; 5092/5097/5102 → SIGN_UP/UNIQUE_CODE (ohne neuen Code anzufordern).
2. **E-Mail-Step** → B5:
   - `existing=true` ⇒ SIGN_IN: wenn `is_smtp_configured && is_magic_login_enabled && status==="MAGIC_CODE"` → UNIQUE_CODE + B6; sonst wenn `is_email_password_enabled` → PASSWORD; sonst Banner 5005 („Invalid email“).
   - `existing=false` ⇒ SIGN_UP: gleiche Logik; Fallback-Code `"5006"` existiert nicht ⇒ **kein Banner, Nutzer bleibt ohne Hinweis im E-Mail-Step**.
   - Fehler: Banner nur für gemappte Codes (z. B. 5005/5010/5000); Rate-Limit (5900) still.
3. **Passwort-Step:** s. 2.23; Submit: `preventDefault` → CSRF-Promise abwarten → Hidden-Feld setzen → `form.submit()` (F4/F5). Felder: E-Mail-Anzeige ist `disabled` (wird nicht gesendet), Hidden-`email` liefert den Wert; `next_path` Hidden (leer, wenn nicht gesetzt ⇒ Feld mit leerem Wert).
   - SIGN_UP-Button aktiv nur bei starkem Passwort (wie Admin) und Gleichheit; SIGN_IN nur bei nicht-leerem Passwort.
   - SIGN_IN ohne SMTP: Button-Text „Go to workspace“ (Original-Kuriosum).
   - „Sign in with unique code“ (nur mit SMTP) → B6 + UNIQUE_CODE.
   - Clear-X im E-Mail-Feld → zurück zum E-Mail-Step, E-Mail geleert.
4. **Unique-Code-Step:** CSRF wird per `useEffect` geladen (nicht abgewartet); „Resend“ ruft B6 und startet 5-s-Countdown; Fehler beim Anfordern → Timer 0, Banner (falls gemappt). Submit nativer POST (F6/F7).
5. **OAuth:** Sichtbar, wenn mind. ein Provider aktiv (`is_google_enabled || is_github_enabled || is_gitlab_enabled || is_gitea_enabled`); nur aktive Buttons (Reihenfolge Google, GitHub, GitLab, Gitea); im PASSWORD-Step kompakt (nur Icons, nebeneinander). Klick → `window.location.assign(`${API_BASE_URL}/auth/{provider}/?next_path=${next_path}`)` (`next_path` unkodiert). **Edge-Case:** Das sind die **App-Endpunkte**; nach erfolgreichem OAuth leitet das Backend zur Web-App (`base_host(is_app=True)` + `next_path`) – der Nutzer landet nicht im Space (die `/auth/spaces/{provider}/`-Endpunkte existieren, werden aber nicht verwendet; `API/authentication/urls.py` Z. 82–149).
6. **Backend-Erfolg:** Redirect auf `base_host(is_space)` + `next_path` ⇒ Startseite leitet weiter (3.16).
7. Banner-Links: 5030 → `/sign-in?email=` (**existiert nicht** ⇒ Catch-all-404); 5060 → `/?email=`.

### 3.18 Space – Legacy-Route `/:workspaceSlug/:projectId`

`clientLoader` (läuft nur im Browser, auch beim initialen Laden – SSR rendert `HydrateFallback`): fehlen Parameter → `/404`; B7; Fehler → `/404`; `entity_name === "project"` → `/issues/{anchor}` mit übernommenen `board`/`peekId` (andere Parameter wie Filter gehen verloren); sonst `/404`.

### 3.19 Space – Board `/issues/:anchor` – Laden

1. SSR-Meta (2.16). Ungültiger Anchor (Regex) → Default-Meta.
2. Layout: SWR `PUBLISH_SETTINGS_{anchor}` → B9 → `PublishStore` in `publishMap`; danach `updateLayoutOptions` aus `view_props` (fehlende Keys ⇒ `false`; **fehlt `view_props` ganz, bleibt der Default `list:true`**).
3. **Edge-Case Ladeanzeige:** `usePublish(anchor)` liefert `{}` statt `undefined`, daher wird der Spinner (`!publishSettings && !error`) nie gezeigt; stattdessen erscheint sofort die Navbar mit Platzhalter-Icon und „...“, der Inhaltsbereich bleibt leer, bis die Settings da sind.
4. Fehler: `error.status === 404` → `PageNotFound` (Bild `404.svg`); sonst `SomethingWentWrongError`.
5. Seite: SWR `PUBLIC_STATES_{anchor}` (B10) und `PUBLIC_LABELS_{anchor}` (B11). Members/Cycles/Modules werden **nicht** geladen (s. 2.18) ⇒ Mentions zeigen „@deactivated user“, Assignee-/Modul-/Zyklus-Chips wären leer (werden ohnehin nicht angezeigt, 3.24).
6. `IssuesLayoutsRoot`: SWR `PUBLIC_ISSUES_{anchor}` → `fetchPublicIssues(anchor, "init-loader", {groupedBy:"state", canGroup:true, perPageCount:50})`; Fehler → `SomethingWentWrongError`. `peekId` aus URL → `setPeekId`.

### 3.20 Space – Navbar-Steuerung & URL-Synchronisation

Effekt in `NavbarControls` (`SPC/components/issues/navbar/controls.tsx`), sobald `anchor` und `workspace_detail` vorliegen:

1. `viewsAcceptable` = aktivierte Layouts in Reihenfolge `list`, `kanban`, `calendar`, `gantt`, `spreadsheet`.
2. `currentBoard` = `board`-Query, falls akzeptiert, sonst erstes akzeptiertes.
3. Wenn `activeLayout` fehlt oder abweicht: Filter aus Query (`priority`, `state`, `labels` – kommasepariert → Arrays) + `display_filters.layout = currentBoard`; nur wenn sich die **Filter** gegenüber dem Store unterscheiden (`isIssueFiltersUpdated` liefert `false`) → `initIssueFilters` (ohne Fetch) und `router.push("/issues/{anchor}?{query}")` (Query enthält `board`, `peekId`, `priority`, `state`, `labels`).
4. Edge-Cases: Ist nur ein im CE nicht gerendertes Layout (Calendar/Gantt/Spreadsheet) aktiviert, wird `activeLayout` gesetzt, aber `IssuesLayoutsRoot` rendert keinen Inhalt (leere Fläche); der Umschalter zeigt keine Buttons (nur `SITES_ISSUE_LAYOUTS` = List/Board). Ist kein Layout aktiviert, passiert nichts (leere Fläche).
5. Layout-Wechsel per Umschalter: `updateIssueFilters(anchor, "display_filters", "layout", key)` (kein Refetch) + `router.push` mit aktuellen Query-Werten.
6. Theme-Button: `setTheme(theme === "light" ? "dark" : "light")` (bei `system` ⇒ `light`).
7. `UserAvatar` nur außerhalb von iframes.

### 3.21 Space – Issue-Abfrage, Gruppierung, Paginierung

Parameterbildung (`SPC/store/helpers/filter.helpers.ts` `getPaginationParams`):

| Parameter | Erstabruf | Gruppen-Nachladen (List/Kanban) |
|---|---|---|
| `cursor` | `50:0:0` | gespeicherter `nextCursor` der Gruppe, sonst `50:1:0` |
| `per_page` | `50` | `50` |
| `group_by` | `state_id` (`EIssueGroupByToServerOptions.state`) | **entfernt** |
| `state` | aus Filter (kommasepariert) | **überschrieben** mit der Gruppen-ID (`EServerGroupByToFilterOptions.state_id = "state"`) – ein aktiver State-Filter wird dabei ignoriert |
| `priority`, `labels` | aus Filter | aus Filter |
| `sub_group_by`, `order_by`, `target_date` | nicht gesetzt (Optionen ungenutzt) | – |

Antwortverarbeitung (`SPC/store/helpers/base-issues.store.ts`): Array ⇒ Gruppe `"All Issues"` (`ALL_ISSUES`); Objekt ⇒ je Gruppe `results` + `total_results` (Sub-Gruppen als verschachtelte Objekte, Schlüssel `{group}_{subgroup}`). Issues werden in `issueDetail.details` gemerged (bestehende werden **nicht** überschrieben, außer `shouldReplace`). Paginierungsdaten je Gruppe (`prevCursor`, `nextCursor`, `nextPageResults`). Bei Filteränderung: `clear()` (Gruppen/Zähler leeren, Paginierungsoptionen behalten) → Loader `mutation` → erneuter Erstabruf mit Filtern.

Backend (`API/space/views/issue.py` `ProjectIssuesPublicEndpoint`): nur `Issue.issue_objects` (Manager `IssueManager` in `API/db/models/issue.py` Z. 92–101: ohne Triage-State-Gruppe, ohne archivierte Issues/Projekte, ohne Entwürfe; Gruppenzähler zusätzlich mit `count_filter` Intake-Status 1/-1/2 oder kein Intake), `order_by` Default `-created_at`, Gruppierung über `GroupedOffsetPaginator` inkl. leerer Gruppen-Zähler (`issue_group_values`).

### 3.22 Space – List-Layout

- Gruppen = alle sortierten States (auch leere, `showEmptyGroup`). Gruppenkopf klickbar (ein-/ausklappen, Default ausgeklappt); Inhalt nur sichtbar, wenn Gruppe Issues hat **und** ausgeklappt.
- Zeile: Klick auf Titel → `Link to="?board=…&peekId={id}"` (bzw. nur `peekId`) + `setPeekId` ⇒ Filter-Parameter fallen aus der URL (Store behält Filter).
- Nachladen: „Load more ↓“-Zeile, solange `nextPageResults` (oder bei unbekannt: geladene < Gesamt); während Laden Platzhalterzeile. Kein Infinite-Scroll (Intersection-Element nur ohne `groupBy`).
- Keine Reaktions-/Vote-Leiste in Listenzeilen.

### 3.23 Space – Kanban-Layout

- Spalten = alle sortierten States (350 px, leere Spalten sichtbar), horizontaler Scroll (`horizontal-scrollbar scrollbar-lg`), Spalte vertikal scrollbar.
- **Infinite-Scroll**: Intersection-Observer pro Spalte (`rootMargin "0% 100% 100% 100%"`, Root = Spalte), Nachladen debounced (300 ms, leading) und nicht während laufender Paginierung; 3 Pulse-Platzhalter am Ende, solange mehr vorhanden.
- Karte: Link wie in der Liste; darunter Reaktionsleiste, wenn `canVote || canReact` (Votes `sm` + Emoji-Reaktionen; Emoji-Reaktionen hier **ohne** iframe-Prüfung).
- Kein Drag & Drop, keine Sub-Gruppierung (Swimlanes ungenutzt).

### 3.24 Space – Eigenschaften auf Karten/Zeilen

`displayProperties` fest: `key`, `state`, `labels`, `priority`, `due_date` = `true` (`list/base-list-root.tsx`, `kanban/base-kanban-root.tsx`). Damit sichtbar: Kennung `{project_details.identifier}-{sequence_id}`, State-Chip (nur wenn `state_id`), Priority-Chip, Labels-Chip, Due-Date-Chip (nur wenn `target_date`). **Nicht** sichtbar (Keys nicht gesetzt): Start-Datum, Assignees, Module, Cycle, Sub-Issues, Attachments, Links. Überfällig-Hervorhebung: `target_date` ≤ heute (Kalendertage) und State-Gruppe nicht `completed`/`cancelled` (`SPC/helpers/issue.helper.ts`). Datumsformat `MMM dd, yyyy` (date-fns), Datum zeitzonenfrei aus `yyyy-mm-dd` geparst (`SPC/helpers/date-time.helper.ts`).

### 3.25 Space – Filter

- Popover „Filters“ (2.22). Sichtbare Sektionen: **Priority** und **State** (Label-Sektion auskommentiert, `SPC/components/issues/filters/selection.tsx` Z. 72–82). Sektionen einklappbar; State zeigt 5 Einträge + „View all/View less“.
- Suche: Priority filtert über den **englischen Key** (`p.key.includes(query)`), State über Namen (case-insensitive).
- Toggle eines Werts → `updateIssueFilters` (Refetch) + `router.push("/issues/{anchor}?board=…&priority=…&state=…&labels=…")` (leere Arrays entfallen; `peekId` entfällt).
- Leiste aktiver Filter (über dem Layout, nur wenn mind. ein nicht-leerer Filter): Gruppen je Key (Key-Label mit `capitalize`), Chips für Priority (Icon + Key-Text, z. B. „urgent“) und State (Icon + Name); Label-Werte werden nicht als Chips gerendert (nur Gruppen-X). Entfernen eines Werts / einer Gruppe → Refetch + `router.push` mit **`states`** statt `state` (Bug, 2.20); „Clear all“ → alle Filter leer + Refetch + `?board={layout}`.
- Beim Neuladen der Seite werden Filter aus der URL übernommen (3.20 Schritt 3) – nach einem „Entfernen“ (Bug) geht ein verbleibender State-Filter dadurch beim Reload verloren.

### 3.26 Space – Peek-Ansicht

- Öffnen: Klick auf Karte/Zeile (URL `?peekId=`), oder Direktaufruf mit `peekId`. `fetchIssueDetails` lädt B13 + B14 bei jeder `peekId`-Änderung (Loader-Flag wird nie zurückgesetzt).
- Modi (`peekMode`, nicht persistiert, Default `side`): `side` (rechts, halbe Breite, kein Backdrop), `modal` (zentriert 60 % × 70 %, Backdrop), `full` (95 %, Zwei-Spalten-Raster).
- Schließen: Escape (sofern nicht in verschachteltem Popup), Mousedown außerhalb des Panels (Ausnahmen: Portale mit `[data-prevent-outside-click]`, `[role=menu|listbox|dialog]`, Links mit `peekId=` ⇒ Wechsel statt Schließen), Pfeil-Button (nur `side`). Schließen setzt `peekId=null` und `router.push("/issues/{anchor}?board=…[&priority][&state][&labels]")` – fehlt `board`, entsteht `board=undefined`.
- Fokus: Panel bekommt Fokus beim Öffnen/Moduswechsel; Tab-Fokusfalle; beim Schließen Fokus zurück auf vorheriges Element.
- Inhalte: Header (Modus-Select, Copy-Link), Details (Kennung, Titel, Beschreibung nur wenn nicht leer/`<p></p>`, Reaktionen), Properties (State mit `addSpaceIfCamelCase`, Priority-Pill, Due Date oder „Empty“), Kommentare.
- **Asymmetrie:** `side`/`modal` rendern den Kommentarbereich nur bei `canComment`; `full` rendert ihn immer (dann ggf. „Sign in to add your comment“ trotz deaktivierter Kommentare). `PeekOverviewIssueProperties` erhält nie `mode="full"` ⇒ der dafür vorgesehene Kopf (Kennung + Copy-Link) erscheint nie.
- Copy-Link sichtbar nur, wenn `navigator.permissions.query({name:"clipboard-write"})` = `granted` (Firefox/Safari: meist nicht ⇒ Button fehlt).

### 3.27 Space – Kommentare

- Liste: alle EXTERNAL-Kommentare des Issues, chronologisch.
- Composer (nur eingeloggt, `canComment`, nicht iframe): Lite-Editor (Tiptap) mit Toolbar und „Comment“-Button; **Enter sendet** (`onEnterKeyPress`), leere Kommentare werden ignoriert. Bilder-Upload im Editor: B26 (ohne Kommentar-ID) → B27 → B28; Asset-IDs werden gesammelt und nach Erstellung des Kommentars per B29 verknüpft. Nach Erfolg: Formular & Editor leeren. Fehler → Toast.
- Anonym (nicht iframe): Hinweisbox „Sign in to add your comment“ → `/?next_path={pathname}` (ohne Query ⇒ Peek/Board-Parameter gehen verloren).
- Kommentarkarte: Name (`display_name`; Bot: `first_name + " Bot"`), Text „commented “ + `timeAgo(created_at)` – **`timeAgo` gibt nichts zurück** (`SPC/helpers/date-time.helper.ts` Z. 10–23) ⇒ es steht nur „commented“.
- Eigene Kommentare (nicht iframe): Menü „Edit“ (Inline-Editor, Bestätigen ✓/Abbrechen ✕, Enter speichert; optimistisch, Fehler ⇒ Liste neu laden) und „Delete“ (**ohne Bestätigungsdialog**, sofort).
- Kommentar-Reaktionen unter jedem Kommentar (3.28).
- Mentions im Inhalt werden über den (leeren) Member-Store aufgelöst ⇒ „@deactivated user“; eigene ID ⇒ gelbe Hervorhebung (nur wenn Member bekannt).
- Editor-Datei-Handler (`SPC/helpers/editor.helper.ts`): `getAssetSrc`/`getAssetDownloadSrc` – absolute `http…`-Quellen unverändert, sonst `getFileURL("/api/public/assets/v2/anchor/{anchor}/{assetId}/")` (B30); `upload` = übergebener Upload (read-only: `async () => ""`); `delete`/`restore` je nach alter (`http…`, Workspace-Asset-API) bzw. neuer Quelle (Anchor-Asset-API); `checkIfAssetExists` immer `true`; `duplicate` gibt dieselbe ID zurück; `validation.maxFileSize = MAX_FILE_SIZE` (5 MB); `cancel` = `SitesFileService.cancelUpload` (greift auf nie gesetztes `cancelSource` zu ⇒ Laufzeitfehler bei Abbruch).
- Editor-Metadaten (`SPC/hooks/use-parse-editor-content.ts`): parst `image-component`-`src` (→ Asset-URL) und `mention-component`-`entity_identifier` (→ `display_name` aus Member-Store, URL `${window.location.origin}/profile/{id}` – ohne Base-Path/Workspace, zeigt nicht auf eine gültige Seite).
- Editor-Erweiterungen: `useEditorFlagging` liefert für `document`, `liteText`, `richText` jeweils leere `disabled`/`flagged`-Listen (CE: alles aktiv; Bezahl-Editionen nutzen diesen Punkt vermutlich zum Freischalten).

### 3.28 Space – Reaktionen & Votes

| Aspekt | Issue-Reaktionen | Kommentar-Reaktionen | Votes |
|---|---|---|---|
| Sichtbar wenn | `canReact` (Peek: zusätzlich nicht iframe; Kanban: immer) | immer (Liste leer, wenn Reaktionen deaktiviert) | `canVote` |
| Datenquelle | `details[issueId].reaction_items` (aus Liste/Detail) | `comments[].comment_reactions` | `details[issueId].vote_items` |
| Anonym-Klick | `router.push("/?next_path={pathname}?{query}")` | dito (in iframe: nichts) | dito (in iframe: nichts) |
| Toggle | eigener Eintrag gleicher Reaktion vorhanden ⇒ entfernen, sonst hinzufügen | dito | gleicher Wert ⇒ entfernen (B25); anderer Wert ⇒ ersetzen (B24) |
| Kodierung | Emoji → Dezimal-Codepoints mit `-` verbunden (z. B. 👍 = `128077`); Darstellung über `stringToEmoji` | dito | `1` / `-1` |
| Optimistik/Fehler | sofortige lokale Änderung; bei Fehler Neuladen der Liste (B18 ⇒ **leer**, Reaktionen verschwinden bis Reload) | lokal; Fehler ⇒ Kommentare neu laden | lokal; Fehler ⇒ B23 ⇒ **leer** |
| Anzeige | `EmojiReactionGroup` (Anzahl, Hervorhebung eigener, Nutzernamen max. 1000) + „+“-Button → `EmojiReactionPicker` (`bottom-start`) | dito (Add-Button nicht in iframe) | zwei Buttons mit Zähler; Tooltip Namensliste |

### 3.29 Space – iframe-Einbettung

`useIsInIframe` (`window.self !== window.top`). Im iframe: kein `UserAvatar`/„Sign in“ in der Navbar; kein Composer/Sign-in-Hinweis; Peek-Emoji-Reaktionen ausgeblendet; Vote-Klicks wirkungslos (`cursor-default`); Kommentar-Menü ausgeblendet; Kommentar-Reaktionen deaktiviert. **Nicht** abgesichert: Kanban-Emoji-Reaktionen (Klick ⇒ Navigation zur Login-Seite innerhalb des iframes, die per `X-Frame-Options: SAMEORIGIN` nur same-origin einbettbar ist).

### 3.30 Space – Abmeldung

`UserAvatar` lädt CSRF beim Mount; Menüeintrag „Sign out“ erscheint erst mit Token; Klick ⇒ `requestSubmit()` ⇒ `onSubmit` = `signOut` (Stores zurücksetzen, `localStorage.theme="system"`) ⇒ nativer POST F8 mit `next_path` = aktuelle Seite inkl. Query ⇒ Backend leitet zurück.

### 3.31 Bekannte Bugs / Kuriositäten (Sammelliste für Entscheidung „1:1 vs. korrigieren“)

| # | App | Befund | Quelle |
|---|---|---|---|
| K1 | Admin | Setup-Seite zeigt keine Fehler (Code-Vergleich gegen Namen) | `ADM/components/instance/setup-form.tsx` |
| K2 | Admin | Sign-in: roter Banner-Zweig tot; 5000/5900 ohne Anzeige | `ADM/app/(all)/(home)/sign-in-form.tsx` |
| K3 | Admin | Setup-Vorbelegung `company` statt `company_name`; Telemetrie-Param immer `true` | `setup-form.tsx` Z. 67–69 |
| K4 | Admin | Banner-Link „Sign In“ → `/admin` (404) | `auth-helpers.tsx` |
| K5 | Admin | `updateInstanceInfo` schreibt Antwort nach `instance.instance` | `ADM/store/instance.store.ts` Z. 138 |
| K6 | Admin | `disableEmail` schluckt Fehler ⇒ Erfolgs-Toast auch bei Fehler | `instance.store.ts` Z. 199–223, `email/page.tsx` |
| K7 | Admin | Breadcrumb/Aktiv-Markierung bei URL ohne Trailing-Slash falsch | `header/index.tsx`, `sidebar-menu.tsx` |
| K8 | Admin | Seitentitel „Authentication Settings - Plane Web“ | `authentication/page.tsx` |
| K9 | Admin | Workspace-Zähler zeigt nur geladene Workspaces | `workspace/page.tsx` |
| K10 | Admin | Texte „Email send“, „Start your journey with by creating…“, „No PII is collected.This…“ | diverse |
| K11 | Space | OAuth-Buttons nutzen App-Flow ⇒ Rückkehr in Web-App | `SPC/hooks/oauth/core.tsx` |
| K12 | Space | Sign-up ohne verfügbare Methode ⇒ kein Hinweis (Code „5006“) | `auth-root.tsx` |
| K13 | Space | Banner-Link `/sign-in` existiert nicht | `authentication.helper.tsx` |
| K14 | Space | Lade-Spinner der Board-Seite nie sichtbar (`usePublish` → `{}`) | `hooks/store/publish/use-publish.ts` |
| K15 | Space | Filter-Entfernen schreibt `states` statt `state` in URL | `applied-filters/root.tsx` |
| K16 | Space | Gruppen-Paginierung überschreibt State-Filter | `filter.helpers.ts` |
| K17 | Space | „commented“ ohne Zeitangabe (`timeAgo` ohne Rückgabe) | `date-time.helper.ts` |
| K18 | Space | Rollback von Reaktionen/Votes lädt leere Listen (Backend-Querysets fehlerhaft) | `API/space/views/issue.py` |
| K19 | Space | Members/Cycles/Modules nie geladen ⇒ Mentions „@deactivated user“ | `SPC/store/*` |
| K20 | Space | Anzeigename-Fallback `first_name first_name` | `navbar/user-avatar.tsx` |
| K21 | Space | Instanzfehler-Text „connectivity work items“; Logo-Link `/spaces/spaces/` | `instance-failure-view.tsx`, `lib/instance-provider.tsx` |
| K22 | Space | SIGN_IN-Button „Go to workspace“ ohne SMTP | `password.tsx` |
| K23 | Space | Full-Peek zeigt Kommentarbereich auch bei deaktivierten Kommentaren | `full-screen-peek-view.tsx` |
| K24 | Space | Kommentar löschen ohne Bestätigung | `comment-detail-card.tsx` |
| K25 | Space | Close-Peek kann `board=undefined` erzeugen | `peek-overview/layout.tsx` |
| K26 | Space | Kanban-Emoji-Reaktionen ohne iframe-Schutz | `kanban/block-reactions.tsx` |
| K27 | Space | Manifest-Link zeigt auf leeres `site.webmanifest`, `robots.txt` nicht ausgeliefert | `SPC/app/root.tsx` |
| K28 | Admin | Existiert kein `Instance`-Datensatz, liefert `GET /api/instances/` nur `{is_activated:false,is_setup_done:false}` ohne `instance` ⇒ `instance` bleibt `undefined`, kein `error` ⇒ **Endlos-Spinner** auf `/` (statt Setup) | `ADM/app/(all)/(home)/page.tsx`, `API/license/api/views/instance.py` |
| K29 | Space | Gleiches Verhalten im Space-`InstanceProvider` (Endlos-Spinner ohne Instanz-Datensatz) | `SPC/lib/instance-provider.tsx` |
| K30 | Space | Browser-Zurück zwischen `board=list`/`board=kanban` ändert das Layout nicht, wenn die Filter gleich sind (Re-Init nur bei Filterabweichung) | `SPC/components/issues/navbar/controls.tsx` Z. 84–88 |

---

## 4. Abhängigkeiten zu anderen Bereichen

| Abhängigkeit | Richtung | Details | Quelle |
|---|---|---|---|
| Backend „License/Instance“ (`API/license/*`) | Admin → Backend | Instanz-Info, Konfigurationen (Key/Value, Verschlüsselung, Seed), Admins, Workspace-Liste/-Anlage, Slug-Check, Test-E-Mail, SMTP-Deaktivierung, Admin-Sign-in/-up/-out | `API/license/urls.py` |
| Backend „Authentication“ (`API/authentication/*`) | Admin, Space → Backend | CSRF-Endpunkt, Form-POST-Flows, Fehlercodes, Rate-Limit (`AuthenticationThrottle`), Session-Middleware mit Admin-Cookie, OAuth-Provider (Google/GitHub/GitLab/Gitea inkl. „Sync“-Flags `ENABLE_*_SYNC`, `GITHUB_ORGANIZATION_ID`), Magic-Code-Mails | `API/authentication/urls.py`, `middleware/session.py` |
| Backend „Space/Public API“ (`API/space/*`) | Space → Backend | Publish-Settings, Meta, Issues (gruppierte Paginierung), States, Labels, Kommentare, Reaktionen, Votes, Assets, (Intake) | `API/space/urls/*.py` |
| Paginierung/Grouper (`API/utils/paginator.py`, `API/utils/grouper.py`, `API/space/utils/grouper.py`) | Space | Cursor-Format `per_page:page:offset`, `GroupedOffsetPaginator`, `SubGroupedOffsetPaginator` | `API/space/views/issue.py` |
| Datei-Storage (S3/MinIO, presigned POST) | Space | Kommentar-Bilder, Asset-Auslieferung per Redirect | `API/space/views/asset.py`, `SVC/file/*` |
| E-Mail (SMTP) | Admin, Space | Test-Mail, Magic-Codes; Konfiguration aus God Mode | `API/license/api/views/configuration.py` |
| Hintergrundjobs (Celery `issue_activity`) | Space → Backend | Activity-Einträge bei Kommentaren/Reaktionen/Votes; `ProjectPublicMember`-Anlage | `API/space/views/issue.py` |
| Web-App | Web → Space/Admin | Publish-Modal (Anchor, `view_props`, `is_comments_enabled`, `is_reactions_enabled`, `is_votes_enabled`, Publish-URL), Header-Link „published URL“, Menü „Enter god mode“ (`GOD_MODE_URL`), „Instance not ready“-Ansicht mit Link zum God Mode, Hinweis „Only your instance admin can create workspaces“ (bei `is_workspace_creation_disabled`) | `apps/web/components/project/publish-project/modal.tsx`, `apps/web/components/issues/header.tsx`, `apps/web/components/workspace/sidebar/user-menu-root.tsx`, `apps/web/components/instance/not-ready-view.tsx`, `packages/i18n/src/locales/en/workspace.json` |
| Web-App ← Instanz-Konfiguration | Admin → Web | Web liest `GET /api/instances/` `config` (Login-Methoden, `enable_signup`, `is_workspace_creation_disabled`, `has_unsplash_configured`, `has_llm_configured`, `file_size_limit`) | `API/license/api/views/instance.py` |
| `@plane/editor` | Space | Lite-Editor (Kommentare), Rich-Editor read-only (Beschreibung), Toolbar-Definition, Styles, Mention-/Bild-Komponenten (`image-component`, `mention-component`) | `SPC/components/editor/*` |
| `@plane/blocks` | Admin, Space | Toast, ConfirmDialog, Icons, Skeleton/Loader, Emoji-Reaktionen/Picker, OAuth-Optionen, Passwort-Stärke, Select | 2.27 |
| `@makeplane/propel` | Admin, Space | Primitive + Design-Tokens + Icons | 2.27, 2.28 |
| `@plane/i18n` | Space (Admin nur Provider) | Schlüssel 2.24 | 2.24 |
| `@plane/constants`, `@plane/types`, `@plane/utils`, `@plane/services` | Admin, Space | Endpunkt-Konstanten, Fehlercodes, Layout-/Filter-Konstanten, Validierungen, Services | Kopf dieses Dokuments |
| Live-Server (`apps/live`) | – | **keine** Abhängigkeit (Space-Editoren sind nicht kollaborativ) | – |

---

## 5. Migrationshinweise (.NET 10 / Aspire / EF Core 10 / Angular)

### 5.1 Zielbild & Hosting (Aspire)

| Thema | Empfehlung | Begründung / Quelle |
|---|---|---|
| Projekte | Zwei Angular-Anwendungen `plane-admin` (Base-Href `/god-mode/`) und `plane-space` (Base-Href `/spaces/`) im Angular-Workspace, gemeinsame Bibliotheken für Propel-Nachbau, Blocks, Services/Typen | spiegelt `apps/admin`, `apps/space` |
| Auslieferung Admin | Statischer Angular-Build, ausgeliefert von einem ASP.NET-Core-Frontend-Host (oder YARP-Gateway) unter `/god-mode/` mit SPA-Fallback auf `/god-mode/index.html`; Header `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`, `X-XSS-Protection: 1; mode=block`; Rate-Limit 300 Req/min/IP (ASP.NET Core Rate Limiting, Fixed Window) | `ADM/caddy/Caddyfile` |
| Auslieferung Space | Statischer Angular-Build unter `/spaces/` **plus** .NET-Middleware für `GET /spaces/issues/{anchor}`, die `index.html` mit `<title>`, `description`, OG- und Twitter-Tags (2.16) serverseitig anreichert (Daten aus DeployBoard → Project, Anchor-Regex `^[a-zA-Z0-9_-]+$`); Header aus 2.16 (inkl. `X-Frame-Options: SAMEORIGIN` nur für `/spaces/`, `robots noindex,nofollow`) | ersetzt `react-router-serve`-SSR ohne Node (ADR-002, Konsequenz „Kein Node.js zur Laufzeit“); Angular-SSR würde Node erfordern |
| Laufzeitkonfiguration | Statt Build-Zeit-`VITE_*`: Server injiziert `window.__PLANE_CONFIG__` (API-Base-URL, Web-/Admin-/Space-Base-URL/-Path, `WEBSITE_URL`, `SUPPORT_EMAIL`) oder `config.json`; Base-Href wird beim Ausliefern gesetzt | Airgapped-Betrieb ohne Rebuild (ADR-004); IST: `ADM/vite.config.ts` `define` |
| Same-Origin | Default `API_BASE_URL = ""` (gleiche Origin) beibehalten; Gateway routet `/api`, `/auth` an die ASP.NET-API | `CONST/endpoints.ts`, `ADM/Dockerfile.admin` |
| Healthchecks | `/god-mode` und `/spaces/` müssen 200 liefern (Aspire `WithHttpHealthCheck`) | Dockerfiles |

### 5.2 Authentifizierung, Sessions, CSRF in ASP.NET Core

| Original | .NET-Umsetzung | Fallstricke |
|---|---|---|
| Zwei Session-Cookies: `admin-session-id` (Pfad enthält `instances`, Max-Age 3600 s) und `session-id` (7 Tage) | Zwei Cookie-Schemes + `PolicyScheme` mit `ForwardDefaultSelector` nach Pfad (`/api/instances…`) ; Server-Sessions in PostgreSQL (EF-Entity analog `API/db/models/session.py`) oder Cookie-Ticket mit `ITicketStore` | Regel ist **„Pfad enthält `instances`“**, nicht Präfix – auch `GET /api/instances/` (öffentlich) läuft über das Admin-Schema; Sign-in/-up/-out-Endpunkte liegen unter `/api/instances/admins/…` und setzen daher das Admin-Cookie |
| CSRF: `GET /auth/get-csrf-token/` → `{csrf_token}`; Formfeld `csrfmiddlewaretoken` | `IAntiforgery` mit `FormFieldName = "csrfmiddlewaretoken"` (und Header-Name für XHR); Endpoint liefert `GetAndStoreTokens().RequestToken` im JSON-Feld `csrf_token` | Form-POSTs sind `application/x-www-form-urlencoded`; bei CSRF-Fehler zeigt Django eine eigene Seite (`csrf_failure`) – Verhalten festlegen |
| Native Form-POST + 302 mit `?error_code=<int>&error_message=<NAME>&<payload>` | Minimal-API-Endpunkte `[FromForm]` → `Results.Redirect(...)`; Fehlercodes **numerisch identisch** (2.11, 2.21); Payload-Keys identisch (`email`, `first_name`, `last_name`, `company_name`, `is_telemetry_enabled`) | Frontend-Logik hängt an exakten Codes und Query-Namen; Redirect-Basis `base_host` (2.1/2.15) inkl. Normalisierung des Base-Paths (führender/abschließender Slash) |
| Admin-Sign-up atomar mit `select_for_update` | EF-Core-Transaktion + `SELECT … FOR UPDATE` (Npgsql `FromSqlInterpolated`) auf Instanz-Zeile oder Advisory-Lock | Doppelte Admins verhindern (GHSA-p548-28jp-wr4p) |
| Passwortstärke serverseitig zxcvbn Score ≥ 3 (auf ersten/letzten 128 Zeichen) | .NET-zxcvbn-Port (z. B. NuGet `zxcvbn-core`) | Client prüft andere Regel (Zeichenklassen) – beide beibehalten |
| `InstanceAdminPermission` (`role >= 15`) | Authorization-Policy `InstanceAdmin` | Rolle 20 = Admin (`ROLE_CHOICES`) |
| Rate-Limit Auth (`AuthenticationThrottle`) | Partitioniertes IP-Rate-Limit; Form-Endpunkte → Redirect mit 5900, JSON-Endpunkte → 429 | Space-Banner zeigt 5900 nicht an (2.21) |
| Verschlüsselte Konfigurationswerte (`is_encrypted`, Fernet mit `SECRET_KEY`) | ASP.NET Core Data Protection (Schlüsselring in PostgreSQL, airgapped) | API liefert Secrets **entschlüsselt** an den God Mode (Formulare zeigen sie) – Beibehaltung ist Entscheidung (Kap. 6) |

### 5.3 API-Verträge (beibehalten, ADR-003 „JSON-Verträge am Original orientiert“)

- Alle Endpunkte aus 2.7 und 2.19 mit identischen Pfaden, Methoden, `snake_case`-Feldern und Statuscodes. **Trailing Slash**: Clients hängen immer `/` an (`SVC/helpers/url.ts`); ASP.NET-Routing muss Pfade mit `/` akzeptieren (Routen-Templates mit Slash oder Rewrite-Middleware, die einen abschließenden Slash vor dem Routing entfernt).
- Paginierte Workspace-Liste (10/Seite) und gruppierte Issue-Paginierung (Cursor `per_page:page:offset`, Antwortfelder 2.19 B12) exakt nachbilden – gemeinsame Implementierung mit dem Paginierungs-Analysebereich.
- `GET /api/instances/` ist öffentlich und gecacht (2 h Server-Cache, `Cache-Control: private, max-age=12`); Cache-Invalidierung bei allen Konfigurations-/Instanz-Schreibvorgängen (Output-Caching mit Tags).
- `PATCH /api/instances/configurations/` ignoriert unbekannte Keys, trimmt Werte, wandelt `null` in `""`, gibt nur aktualisierte Einträge zurück – Frontend `reset()` hängt daran.
- `DELETE …/disable-email-feature/` setzt `ENABLE_SMTP="0"` und fünf Felder leer, **nicht** `EMAIL_USE_TLS/SSL`.
- Bekannte Backend-Fehler (K18, defekter `project-boards`-Endpunkt) beim Neubau korrigieren (Backend-Verhalten ist keine UI) – Rollback-Verhalten im Frontend dann wieder sinnvoll.

### 5.4 Angular-Architektur (1:1-Port der Store-/Service-Logik)

| Original (React) | Angular-Pendant | Hinweise |
|---|---|---|
| MobX-Stores (`ADM/store/*`, `SPC/store/*`) | `@Injectable({providedIn:'root'})`-Services mit Signals (`signal`, `computed`) oder NgRx SignalStore; gleiche Methodennamen (`fetchInstanceInfo`, `updateInstanceConfigurations`, …) | `computedFn` → memoisierte Selektoren je Parameter; `resetOnSignOut` ⇒ zentrale Reset-Methode statt Store-Neuinstanziierung |
| SWR (Keys, `revalidateOnFocus`, `refreshInterval`, `errorRetryCount`) | Eigener Query-Cache-Service oder TanStack Query (Angular) mit identischen Keys/Optionen (2.14, 2.26) | Admin: globales 10-min-Polling; Space: Default-Revalidierung bei Fenster-Fokus für Publish-Settings/States/Labels/User |
| react-hook-form (`isDirty`, `isValid`, `reset`, `mode:"onChange"`) | Reactive Forms (`dirty`, `valid`, `reset(values)`, `updateOn:'change'`) | Pflichtregeln wie 2.9; Workspace-Slug-Autogenerierung; Provider-Formulare `reset` mit Serverantwort |
| next-themes | `ThemeService` (`localStorage.theme`, `matchMedia('(prefers-color-scheme: dark)')`, Attribut/Klasse am `<html>` wie `@plane/tailwind-config` erwartet) | GIF-/Logo-Umschaltung nach `resolvedTheme` |
| React-Router-Layouts/Guards | Angular-Routen mit Layout-Komponenten; Login-Tri-State **in der Layout-Komponente** (Spinner bei `undefined`), nicht nur über blockierende Guards | Visuelles Verhalten (Spinner) muss identisch bleiben |
| Trailing-Slash-Shims | Eigene `UrlSerializer`/`LocationStrategy`, die Pfade mit `/` erzeugt **und** ohne `/` akzeptiert | Backend leitet auf `…/general/`; Breadcrumb-/Aktivlogik robust machen oder K7 nachbilden |
| `clientLoader` (S2), Server-`loader` (S3) | Route-Resolver (S2) bzw. .NET-Middleware (S3, 5.1) | |
| Propel-Komponenten (Base UI) | Angular-Komponentenbibliothek mit identischem DOM/Klassen/ARIA (Button, Switch, Input/InputGroup, Select, Menu, Tooltip, Dialog, Popover, Breadcrumb, Avatar/AvatarGroup, WorkspaceAvatar, Checkbox, IconButton, AnchorButton, Icon); Angular CDK für Overlay/Fokus | Gemeinsam mit Web-App-Analyse; Referenz-Screenshots pro Variante |
| `@plane/blocks` (Toast, ConfirmDialog, Emoji-Reaktionen, OAuthOptions, PasswordStrengthIndicator, Select, Loader) | Angular-Port in Shared-Lib | Emoji-Daten offline bündeln (ADR-004) |
| `@plane/editor` (Tiptap/React) | Angular-Wrapper um Tiptap-Core bzw. Entscheidung des Editor-Analysebereichs | Space braucht Lite-Editor (editierbar, Toolbar, Enter=Senden, Bild-Upload) und Rich-Editor read-only; Custom-Nodes `image-component`, `mention-component` |
| Tailwind v4 + Tokens (`@plane/tailwind-config`, `@makeplane/propel/styles`) | Tailwind v4 im Angular-Build (PostCSS), Tokens 1:1 übernehmen, `@source` auf `**/*.{html,ts}` | Legacy-Klassen (`text-custom-text-300`) bewusst übernehmen oder ersetzen |
| Fonts (`@fontsource*`), GIF-Spinner, SVG/PNG-Assets | 1:1 kopieren und lokal bündeln | Preload Inter (`inter-latin-wght-normal.woff2`) |
| BProgress-Topbar | Angular-Router-Events (`NavigationStart/End`) + identisches CSS | Höhe 2.5 px, Accent-Gradient |
| IntersectionObserver-Infinite-Scroll (Kanban) | Direktive mit gleichem `rootMargin` | 300 ms Debounce, leading |
| Peek-Fokusfalle/Outside-Click | Angular CDK `FocusTrap` + eigene Outside-Click-Logik (Ausnahmen 3.26) | `peekId`-Links dürfen nicht schließen |

### 5.5 EF-Core-/Domänen-Hinweise (Ausschnitt dieses Bereichs)

| Element | Empfehlung |
|---|---|
| `Instance` (Singleton) | Tabelle mit genau einer Zeile; Felder aus 2.8 (`instance_name`, `instance_id`, `current_version`, `latest_version`, `edition` (entfällt fachlich, ADR-001), `domain`, `last_checked_at`, `namespace`, `is_telemetry_enabled`, `is_support_required`, `is_setup_done`, `is_signup_screen_visited`, `is_verified`, `is_test`, `is_current_version_deprecated`, `whitelist_emails`) |
| `InstanceAdmin` | `(instance_id, user_id)` eindeutig, `role` (20), `is_verified` |
| `InstanceConfiguration` | Key/Value-Tabelle beibehalten (API-Vertrag ist Key/Value): `key` (unique, max 100), `value` (Text, nullable), `category`, `is_encrypted`; Seed beim Start aus ENV (wie `configure_instance`, nur fehlende Keys anlegen) – inkl. neuer Keys für EE1–EE3 (OIDC/SAML/LDAP) und ADR-004-AI-Provider (z. B. Base-URL) |
| Workspace-Liste | EF-Projektion mit Subqueries `total_projects`, `total_members` (nur aktive, keine Bots) |
| Slug-Prüfung | Zwei Listen: Backend `RESTRICTED_WORKSPACE_SLUGS` (`API/utils/constants.py`) und Frontend `RESTRICTED_URLS` (`CONST/workspace.ts`) – beide prüfen; Vergleich case-insensitive |
| DeployBoard | `entity_name` ∈ `project, issue, module, cycle, page, view, intake`; Flags `is_comments_enabled`, `is_reactions_enabled`, `is_votes_enabled`, `is_activity_enabled`, `is_disabled`, `view_props` (JSON), `intake_id`; Anchor unique (`get_anchor`) – Grundlage für EE5–EE7 |

### 5.6 Was ist 1:1 übertragbar, was neu, welche Fallstricke

| Kategorie | Inhalt |
|---|---|
| **1:1 übertragbar** | Routen & Base-Paths; alle Texte (2.9, 2.10, 2.21, 2.23) inkl. Tippfehler (ADR-005); Formularregeln (2.9); Store-Logik (2.6, 2.18) als Signal-Services; API-Verträge (2.7, 2.19); Fehlercode-Mappings; Konfigurationsschlüssel (2.8); Layout-/Spacing-Klassen (2.12, 2.22) mit Tailwind; Assets; Theme-/Sidebar-Persistenz (2.14, 2.26) |
| **Neu zu bauen** | Angular-Komponentenbibliothek für Propel/Blocks; Editor-Integration; Node-freie Meta-Injektion für Space; Laufzeit-Konfiguration statt Build-Zeit-ENV; Bezahl-Features EE1–EE3 (God Mode) und EE5–EE8 (Space); AI-Provider-Konfiguration für lokale LLMs (ADR-004) |
| **Entfällt** | Lizenz/Edition/Plan-Logik (EE11), Upsell-/Kontakt-CTA „If you have a preferred AI models vendor, please get in touch with us.“ (ADR-001 „keine Talk-to-Sales-CTAs“ – Entscheidung Kap. 6), Caddy/nginx/`react-router-serve` |
| **Fallstricke** | (1) Admin-Cookie-Selektion per Pfad-Teilstring; (2) Trailing-Slash in API **und** Frontend-Routen; (3) numerische Fehlercodes als Query-Strings; (4) Form-POST-Flows statt JSON (Browser-Navigation!) – CSRF-Feldname; (5) `usePublish` liefert `{}` ⇒ Ladeverhalten (K14) bewusst nachbilden oder korrigieren; (6) SWR-Fokus-Revalidierung im Space erzeugt zusätzliche Requests – für visuelle Tests deaktivierbar machen; (7) Reaktions-Kodierung als Dezimal-Codepoints mit `-`; (8) Datumsparsing zeitzonenfrei; (9) Overdue-Logik nach Kalendertagen; (10) Peek-Outside-Click-Ausnahmen für Portale; (11) Space-OAuth landet in der Web-App (K11); (12) `GET /api/instances/` ist gecacht – nach Konfigurationsänderung invalidieren, sonst zeigt Space/Web alte Login-Optionen; (13) Secrets im Klartext an den Client; (14) 10-min-Polling im God Mode |

### 5.7 Referenz-Screenshots für visuelle Regressionstests (ADR-005) – Pflichtzustände

| App | Zustände |
|---|---|
| Admin | Spinner; Instanzfehler (light/dark); Setup leer / ausgefüllt / Passwort schwach (Indikator) / Passwörter ungleich; Sign-in leer / mit AuthBanner je Code 5150–5190; Dashboard General (Sidebar aus-/eingeklappt, Mobile-Overlay, Hilfe-Popover offen, Dropdown offen); Email (Switch aus, Switch an mit Formular, Skeleton, Test-Dialog alle 3 Schritte); Authentication (Skeleton; Karten nicht konfiguriert/konfiguriert/aktiv/inaktiv; Fehler-Toast letzte Methode); je Provider-Seite (Skeleton, leer, ausgefüllt, Discard-Dialog, Copy-Toast); AI; Image; Workspaces (Skeleton, Liste mit/ohne Logo, „Load more“, Spinner bei Pagination); Workspace-Create (leer, Validierungsfehler je Regel, Slug vergeben); NewUserPopup; 404; jede Seite in light und dark |
| Space | Spinner; Instanzfehler; Auth (E-Mail leer/ungültig, OAuth sichtbar/kompakt, Passwort SIGN_IN mit/ohne SMTP, SIGN_UP mit Stärkeanzeige/Mismatch, Unique Code mit Countdown, jedes Banner aus 2.21); Eingeloggt-Ansicht; Board-Navbar (Ladeplatzhalter „...“, anonym/eingeloggt, Menü offen); List (Gruppen auf/zu, leer, „Load more“, Loader-Zeile, gepeekte Zeile); Kanban (leere Spalten, Karten mit/ohne Reaktionsleiste, Loader); Filter-Popover (Suche, „View all“), Aktive-Filter-Leiste; Peek side/modal/full (Laden, mit Beschreibung, Kommentare leer/voll, Composer mit Toolbar, Edit-Modus, Sign-in-Hinweis, Reaktions-Picker offen, Votes aktiv/inaktiv); 404 (Catch-all, Anchor), Board-Fehler, Fehlerseite; iframe-Variante; light/dark |

---

## 6. Offene Punkte

| # | Frage | Kontext | Vorschlag |
|---|---|---|---|
| O1 | Sollen die Original-Bugs K1–K27 (3.31) 1:1 nachgebaut oder korrigiert werden? | ADR-005 verlangt verhaltensgleiche Nachbildung; viele Punkte sind offensichtliche Fehler (fehlende Fehleranzeige im Setup, tote Links, falsche URL-Parameter) | Visuell 1:1, funktionale Fehler korrigieren (K1–K7, K11–K19, K21, K25–K27); reine Textkuriositäten (K8, K10, K20, K22) 1:1 belassen – Freigabe durch Auftraggeber |
| O2 | Space-OAuth: App-Flow (Original) oder Space-Flow `/auth/spaces/{provider}/`? | K11; Space-Flow erfordert zusätzliche Callback-URLs beim Provider (God Mode zeigt nur App-Callbacks) | Space-Flow verwenden und im God Mode zusätzliche Copy-Felder „Callback URI (Spaces)“ anzeigen – Abweichung von ADR-005 freigeben lassen |
| O3 | Gilt „Kein Node.js zur Laufzeit“ (ADR-002, Konsequenzen) global, also auch für Space-SSR? | Original nutzt Node-SSR nur für Meta-Tags | Annahme „global“: .NET-Meta-Injektion (5.1) – bestätigen |
| O4 | Genaue UI der Bezahl-Funktionen EE1–EE8 | Code nicht im Repo (2.30) | Referenzinstanz der Commercial Edition (Plan „Enterprise“) bereitstellen bzw. Screenshots/Feldlisten liefern; bis dahin Felder aus 2.30 als Arbeitsgrundlage |
| O5 | AI-Konfiguration für lokale LLM-Provider (ADR-004) erweitert die Original-UI (Provider-Auswahl, Base-URL) | Original: nur `LLM_MODEL`, `LLM_API_KEY`; `LLM_PROVIDER` ohne UI | Zusätzliche Felder im Stil von 2.9 ergänzen; Kontakt-CTA durch Provider-Auswahl ersetzen – Freigabe |
| O6 | Telemetrie (Setup-Checkbox Default an, General-Switch) vs. ADR-004 („keine Telemetrie nach außen“) | `ADM/components/instance/setup-form.tsx`, `general/form.tsx` | UI 1:1 behalten, Backend sendet nie nach außen (Schalter wirkungslos/lokal) oder UI entfernen – Entscheidung |
| O7 | Externe Links (docs.plane.so, forum.plane.so, github.com, plane.so/legals, developers.plane.so, platform.openai.com, unsplash.com, Provider-Konsolen) im Airgapped-Betrieb | ADR-004/ADR-005 | Links beibehalten (sie sind optional) oder per Konfiguration ersetzbar machen |
| O8 | Secrets im Klartext an den God Mode ausliefern? | 3.10, 5.2 | Beibehalten (1:1) oder maskieren mit „unverändert lassen“-Semantik – Sicherheitsentscheidung |
| O9 | Admin-Session 1 h + separate Cookie-Logik beibehalten? | 5.2 | Beibehalten (konfigurierbar) |
| O10 | God Mode bleibt ausschließlich Englisch? | Original ohne i18n | 1:1 Englisch; optional i18n-fähig vorbereiten |
| O11 | Mehrere Instanz-Admins: Backend erlaubt Anlage/Löschung, UI nicht (General zeigt nur ersten Admin) – gibt es in Bezahl-Editionen eine Admin-Verwaltung? | `API/license/urls.py`, `general/form.tsx` | Klären (O4); bis dahin nicht bauen |
| O12 | Space: Label-Filter (auskommentiert), Members/Cycles/Modules (nie geladen), Swimlanes (ungenutzt) aktivieren? | 2.18, 3.25, EE9 | 1:1 deaktiviert lassen, außer EE5 (Views) benötigt sie |
| O13 | Space-Layouts Calendar/Spreadsheet/Gantt (EE8) umsetzen? | Typen und Konfiguration vorbereitet, Rendering fehlt | Mit Views-Publishing (EE5) umsetzen, Read-only-Varianten der Web-Layouts |
| O14 | Plan-abhängige Upload-Limits (EE10) | ADR-001 | Instanzeinstellung `FILE_SIZE_LIMIT` auch im Space-Editor statt fixer 5 MB nutzen – God-Mode-UI dafür? |
| O15 | Base-Paths zur Laufzeit konfigurierbar? | Original: Build-Zeit (`VITE_*`) | Laufzeit (5.1) – bestätigen |
