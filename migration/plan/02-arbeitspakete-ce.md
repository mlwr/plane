# 02 – Arbeitspakete der CE-Portierung (WP-<Inkrement>-<NNN>)

> **Stand:** 23.10.2026. **Verbindlichkeit:** bindend für alle Implementierungs-Agenten der CE-Phase (I0–I7). Rangfolge bei Widersprüchen: `architecture/00-grundsatzentscheidungen.md` > `architecture/17-abgleich-dokumentuebergreifend.md` (Entscheidungen des Auftraggebers, Umbenennungstabelle) > `architecture/01-zielarchitektur-und-tech-stack.md` > Themen-Dokumente 02–16 > dieses Dokument. Wo dieses Dokument eine Zuordnung bewusst anders trifft als ein Architektur-Dokument, steht die Begründung in `plan/04-risiken-offene-punkte.md` (Abschnitt „Planungsentscheidungen OP-PLAN-*“).
>
> **Erzeugt:** Abschnitte 3 und 4 sowie die Anhänge erzeugt `migration/_werkzeuge/plan/build.py` aus den Spezifikationsdateien `wp_spec.py`, `wp_spec_i1_i3.py`, `wp_spec_i4_i7.py`; die Vollständigkeit prüft `migration/_werkzeuge/plan/check_wp.py`. **Änderungen nur in den Spezifikationsdateien**, danach `python3 -I migration/_werkzeuge/plan/build.py && python3 -I migration/_werkzeuge/plan/check_wp.py`. Maschinenlesbar: `plan/_data/wp-ce.json` (Array `{wp, title, phase, ce_ids[], depends_on[], size}`) und `plan/_data/wp-endpoints.json` (registrierter Endpunkt → Arbeitspaket).
>
> **Namen:** Alle Zielbezeichner folgen ADR-009C (`Funk.*`, `FunkDbContext`, `Funk:`-Konfiguration, `X-Funk-*`, Realm `funk`, Clients `funk-*`, `@funk/*`). Wo die Architektur-Dokumente noch `Plane.*` schreiben, gilt die Umbenennungstabelle in 17. Pfade für Zielcode sind relativ zur Wurzel des Repositorys `funk.`; Original-Pfade beziehen sich auf `mlwr/plane@funk-referenz-1.4.2` (Commit `053b2c0`).

> **Prüfergebnis (`check_wp.py`, 23.10.2026):** 180 Arbeitspakete (I0 38, I1 31, I2 35, I3 16, I4 13, I5 13, I6 22, I7 12); 507 von 507 CE-IDs genau einem Paket zugeordnet (27 davon „entfällt“ mit Ersatznachweis); alle Abhängigkeiten existieren, zeigen nicht in spätere Inkremente und bilden einen azyklischen Graphen; 564 registrierte Endpunkte genau einem Paket zugeordnet.

## 1. Lesehilfe

### 1.1 Nummernkreise

| Nummernkreis | Bedeutung | Typ (DoD 15 §3.15.3) | CE-IDs |
|---|---|---|---|
| `WP-In-001` … `WP-In-099` | fachliche Schnitte (vertikal: Endpunkte + Screens + Tests eines Feature-Clusters; Schnittregel 01 §1.3) | V, B, F, D | ja |
| `WP-In-101` … `WP-In-199` | Bausteine und Infrastruktur, die ein Inkrement braucht (Hosts, Plattform, Dokumente, Designsystem-Grundlagen, Betrieb) | I, B, D, F | teilweise (CE-OPS, CE-I18N) |
| `WP-In-201` … `WP-In-299` | **Erweiterungspunkte** für Bezahl-Pakete (P-Andockstellen aus 16 §1.4/§3.3.0) | X | nie |
| `WP-I0-900` … `WP-I0-913` | Spikes des Spike-Tracks (`WP-I0-9nn` = Spike S*nn*, `WP-I0-913` = Scope-FK-Spike) | S | nie |
| `WP-In-999` | Inkrement-Abnahme (Gate G5; für I7 zusätzlich G6) | A | nie |

### 1.2 Felder je Arbeitspaket

| Feld | Bedeutung |
|---|---|
| Inkrement | `I0` … `I7` (01 §1.3). Ein Paket darf nur von Paketen desselben oder eines früheren Inkrements abhängen (geprüft). |
| Typ | DoD-Typ aus 15 §3.15.3: **V** vertikaler Schnitt, **B** Backend-only, **F** Frontend-only, **I** Infrastruktur/Baustein, **D** Editor/Dokumente, **S** Spike, **X** Erweiterungspunkt 🧱; zusätzlich **A** Inkrement-Abnahme. |
| Größe | **S** ≤ 3 Agenten-Arbeitstage, **M** 3–7, **L** 7–12. Größer wird nicht geplant – ein Paket über 12 Tage wird geteilt (Änderungsverfahren §2.4). Für Schätzungen gilt S = 2, M = 5, L = 10 Tage (§3.2). |
| parallelisierbar | **ja**: kann gleichzeitig mit anderen Paketen desselben Inkrements laufen, sobald die Abhängigkeiten erfüllt sind. **nein**: legt gemeinsame Grundlagen (Basis-Store, gemeinsame Registry, zentrale Migration) oder liegt auf dem kritischen Pfad; es soll von genau einem Agenten ohne parallele Arbeit am selben Modul bearbeitet werden. |
| Abhängigkeiten | Pakete, die abgenommen (gemergt, G2 grün) sein müssen, bevor das Paket beginnt. Jedes Paket eines Inkrements `In` (n ≥ 1) hängt direkt oder transitiv an `WP-I(n-1)-999`, außer den ausdrücklich als **Vorlauf** markierten Paketen (Editor-Track ab I1, Dokument-/Realtime-Track ab I3; plan/01 §3). |
| CE-IDs | Features aus `features/10-ce-feature-katalog.md`. **Jede der 507 CE-IDs gehört zu genau einem Arbeitspaket** (Anhang A, `check_wp.py`). CE-IDs mit Status „entfällt“ (27, ADR-008) liegen in dem Paket, das den Ersatznachweis führt (Titelzusatz „Nachweis entfallener …“). |
| Andockstelle | nur Typ X: Quelle in 01 §1.4 bzw. 16 §3.3.0 (E-Nummer) und die Träger-CE-IDs aus 16 §4.6. |
| Endpunkte | registrierte Endpunkte aus dem Katalog 04 (`architecture/_data/endpoints.json`). Jeder registrierte Endpunkt gehört zu genau einem Paket: dem Paket, das eine seiner CE-IDs enthält und im Inkrement des Katalogs liegt, sonst dem frühesten Paket mit einer seiner CE-IDs; „(vorab)“ = Endpunkt wird vor dem Paket seiner CE-ID gebraucht und in einem früheren Paket gebaut; das Paket der CE-ID erweitert ihn dann nur. „(verschoben)“ = Endpunkt kann erst später entstehen, weil seine Daten erst dann existieren (z. B. workspace-weite Cycle-/Modul-Listen in I3). Beide Fälle stehen in der Liste `EP_OVERRIDE` in `wp_spec.py`. |
| Referenzdokumente | „Architektur“ = von Hand gesetzte Abschnitte der Dokumente 00–17; „Analyse/Feature“ = automatisch aus dem Feld `doc` der enthaltenen CE-IDs übernommen. |
| Original-Pfade | automatisch aus `backend_refs`/`frontend_refs` der CE-IDs übernommen, ergänzt um von Hand gesetzte Pfade. |
| Akzeptanzkriterien | paketspezifische Kriterien, danach die Standardkriterien des Typs (15 §3.15.3) und der Abdeckungsnachweis `ce-coverage-check`. Der gemeinsame DoD-Kern aus 15 §3.15.3 und `plan/03-agenten-leitfaden.md` §7 gilt immer zusätzlich. |
| Testumfang | Pflicht-Ebenen, Testprojekte und E2E-Specs aus 15 Anhang B (automatisch) plus paketspezifische Tests. |

### 1.3 Ebenen und Gates (Kurzreferenz, Quelle 15 §3.1/§3.15)

L0 Statik · L1 Unit · L2 Frontend-Komponenten/Stores · L3 Modul-Integration (inkl. portierter Original-Tests) · L4 Golden-Files · L5 Contract-Parität (Parity-Harness) · L6 System (Aspire) · L7 E2E Dual-Target · L8 Visual/DOM/a11y (nur Chromium als Gate, 17 Z-10) · L9 Last/Soak. Gates: G0 lokal, G1 PR, G2 Merge-Queue (vor Merge in `develop`), G3 Golden-Änderung, G4 Nightly, G5 Inkrement-Abnahme, G6 Release.

## 2. Regeln für die Arbeit mit den Paketen

### 2.1 Zuordnungsregeln

1. **CE-ID → genau ein Paket.** Ein Paket kann mehrere CE-IDs enthalten; eine CE-ID wird nie geteilt. Wenn ein früheres Paket einen Teil einer CE-ID braucht (z. B. einen Endpunkt), baut es diesen Teil als „vorab“; die CE-ID wird erst im zugeordneten Paket abgenommen.
2. **Inkrement-Zuordnung.** Grundlage ist 01 §1.3 und die Inkrement-Spalte in 15 Anhang B; Abweichungen (Anhang B dieses Dokuments) sind in plan/04 OP-PLAN-03 begründet.
3. **Erweiterungspunkte bekommen eigene Pakete (Nummernkreis 2xx).** Abweichend von 16 §4.6 („im Arbeitspaket der Träger-CE-ID“) verlangt der Planungsauftrag eigene Pakete; das Träger-Paket hängt vom Erweiterungspunkt-Paket ab und nutzt die Andockstelle (plan/04 OP-PLAN-01). Die DoD Typ X wird im Erweiterungspunkt-Paket erfüllt; das Träger-Paket weist nach, dass es die Andockstelle verwendet (Review-Checkliste) – z. B. liest WP-I1-011 States ausschließlich über `IStateCatalog` aus WP-I1-201.
4. **Spikes** liefern dauerhafte Tests (DoD Typ S) und gaten nur die in 01 §9 Spalte „blockiert“ genannten Folgepakete; S0, S7, S10 (Shell-Teil) und S11 gaten die Abnahme von I0.
5. **Keine Platzhalter-Seiten** (01 §7.19): Ein Paket registriert seine Routen und Sidebar-Einträge erst, wenn sein Screen abgenommen ist.

### 2.2 Reihenfolge innerhalb eines Inkrements

Erweiterungspunkt-Pakete (2xx) und Bausteine (1xx) zuerst, weil fachliche Schnitte auf ihnen aufbauen; danach die Schnitte in der Reihenfolge des Abhängigkeitsgraphen (plan/01 §3). Pakete mit „parallelisierbar = ja“ werden auf mehrere Agenten verteilt. Der kritische Pfad je Inkrement steht in §3.2.

### 2.3 Wellen W1–W9 (Bezahl-Pakete)

Für die Wellen gibt es in dieser Phase **keine** Arbeitspakete. Sie stehen als grobe Blöcke in plan/01 §5 und werden erst kurz vor ihrer Umsetzung nach 16 §6 detailliert geplant (`migration/plan/waves/W<n>-<paket>.md`). Ihre Voraussetzungen im CE-Fundament sind die X-Pakete dieses Dokuments.

### 2.4 Änderungsverfahren

Ein Agent, der feststellt, dass ein Paket zu groß ist, eine Abhängigkeit fehlt oder eine CE-ID falsch zugeordnet ist, ändert **nicht** eigenmächtig den Plan im Repository `funk.`, sondern eröffnet eine Planfrage (plan/03 §9). Nach Freigabe werden die Spezifikationsdateien geändert, `build.py` und `check_wp.py` laufen, und `docs/plan/` in `funk.` wird aktualisiert.

## 3. Übersicht aller Arbeitspakete

| WP | Titel | Inkr. | Typ | Größe | parallel | CE-IDs | Endpunkte | hängt ab von |
|---|---|---|---|---|---|---|---|---|
| [WP-I0-001](#wp-i0-001--schnitt-1-anmeldung-über-keycloak--jit-benutzer--landingleere-shell) | Schnitt 1: Anmeldung über Keycloak → JIT-Benutzer → Landing/leere Shell | I0 | V | L | nein | 10 | 13 | WP-I0-103, WP-I0-105, WP-I0-108, WP-I0-203, WP-I0-204 |
| [WP-I0-002](#wp-i0-002--schnitt-2-workspace-anlegen-formular-slug-prüfung-admin-mitgliedschaft) | Schnitt 2: Workspace anlegen (Formular, Slug-Prüfung, Admin-Mitgliedschaft) | I0 | V | M | nein | 1 | 3 | WP-I0-001, WP-I0-201, WP-I0-202, WP-I0-203 |
| [WP-I0-003](#wp-i0-003--instanz-bootstrap-konfiguration-instanz-info-erst-einrichtung-god-mode-einstieg-inkl-nachweis-entfallener-admin-logins) | Instanz-Bootstrap: Konfiguration, Instanz-Info, Erst-Einrichtung, God-Mode-Einstieg (inkl. Nachweis entfallener Admin-Logins) | I0 | V | M | ja | 12 | 7 | WP-I0-001, WP-I0-208 |
| [WP-I0-004](#wp-i0-004--schnitt-workspace-shell-11-top-navigation-sidebar-header-workspace-switcher-user-menü) | Schnitt: Workspace-Shell 1:1 (Top-Navigation, Sidebar, Header, Workspace-Switcher, User-Menü) | I0 | V | L | nein | 6 | 2 | WP-I0-002, WP-I0-006, WP-I0-208 |
| [WP-I0-005](#wp-i0-005--schnitt-3-projekt-anlegen-identifier-prüfung-default-states-mitgliedschaft) | Schnitt 3: Projekt anlegen (Identifier-Prüfung, Default-States, Mitgliedschaft) | I0 | V | M | nein | 2 | 6 | WP-I0-002, WP-I0-006 |
| [WP-I0-006](#wp-i0-006--designsystem-fundament-css-pipeline-schriften-icons-erste-propel-primitive-toast-galerie) | Designsystem-Fundament: CSS-Pipeline, Schriften, Icons, erste Propel-Primitive, Toast, Galerie | I0 | F | L | ja | 8 | 0 | WP-I0-105, WP-I0-910 |
| [WP-I0-101](#wp-i0-101--repository-funk-aufsetzen-lizenz-plan-spiegel-agentsmd-grundgerüst) | Repository funk. aufsetzen (Lizenz, Plan-Spiegel, AGENTS.md, Grundgerüst) | I0 | I | S | nein | 0 | 0 | – |
| [WP-I0-102](#wp-i0-102--aspire-apphost-und-servicedefaults-profile-devtestprodlike) | Aspire-AppHost und ServiceDefaults (Profile dev/test/prodlike) | I0 | I | M | ja | 1 | 0 | WP-I0-900 |
| [WP-I0-103](#wp-i0-103--gateway-funkgateway-routen-statische-auslieferung-base-urls-health-robotstxt-413) | Gateway Funk.Gateway: Routen, statische Auslieferung, Base-URLs, Health, robots.txt, 413 | I0 | I | M | ja | 4 | 2 | WP-I0-102, WP-I0-104 |
| [WP-I0-104](#wp-i0-104--backend-fundament-buildingblocks-funkdata-migrator-modul-schablone-architekturtests) | Backend-Fundament: BuildingBlocks, Funk.Data, Migrator, Modul-Schablone, Architekturtests | I0 | I | L | ja | 1 | 1 | WP-I0-900 |
| [WP-I0-105](#wp-i0-105--frontend-fundament-angular-workspace-shared-libs-routing-kern-wrapper-runtime-config) | Frontend-Fundament: Angular-Workspace, Shared-Libs, Routing-Kern, Wrapper, Runtime-Config | I0 | F | L | ja | 0 | 0 | WP-I0-900 |
| [WP-I0-106](#wp-i0-106--test--und-ci-infrastruktur-gates-g0g3-lizenz-gate-g-brand-coverage--und-ledger-werkzeuge) | Test- und CI-Infrastruktur: Gates G0–G3, Lizenz-Gate, G-BRAND, Coverage- und Ledger-Werkzeuge | I0 | I | L | ja | 2 | 0 | WP-I0-101, WP-I0-900 |
| [WP-I0-107](#wp-i0-107--realtime-host-gerüst-funkrealtime-health-origin-prüfung-live-fallback) | Realtime-Host-Gerüst Funk.Realtime (Health, Origin-Prüfung, /live-Fallback) | I0 | I | S | ja | 1 | 1 | WP-I0-103, WP-I0-104 |
| [WP-I0-108](#wp-i0-108--keycloak-realm-als-code-devtestprod-inkl-nachweis-entfallener-auth-funktionen) | Keycloak-Realm als Code (dev/test/prod) inkl. Nachweis entfallener Auth-Funktionen | I0 | V | M | ja | 17 | 0 | WP-I0-102, WP-I0-907 |
| [WP-I0-109](#wp-i0-109--keycloak-login-themes-funk-und-funk-space-11-optik-der-sign-in-seite-funk-branding) | Keycloak-Login-Themes funk und funk-space (1:1-Optik der Sign-in-Seite, funk.-Branding) | I0 | V | L | ja | 1 | 0 | WP-I0-108, WP-I0-006 |
| [WP-I0-201](#wp-i0-201--erweiterungspunkt-c3-event-katalog-outboxinbox-gerüst-consumer-registrierung-recurring-jobs-queues) | Erweiterungspunkt C3: Event-Katalog, Outbox/Inbox-Gerüst, Consumer-Registrierung, Recurring Jobs, Queues | I0 | X | M | ja | 0 | 0 | WP-I0-104 |
| [WP-I0-202](#wp-i0-202--erweiterungspunkt-b1a2-scoperef-scopelevel-iscoperesolver-iscopeancestorcontributor-routerstoreteamspaceid) | Erweiterungspunkt B1/A2: ScopeRef, ScopeLevel, IScopeResolver, IScopeAncestorContributor, RouterStore.teamspaceId | I0 | X | S | ja | 0 | 0 | WP-I0-104, WP-I0-105 |
| [WP-I0-203](#wp-i0-203--erweiterungspunkt-e5-permission-katalog-rolesrole_permissions-role_id-isystemrolegrantcontributor-permissionservice) | Erweiterungspunkt E5: Permission-Katalog, roles/role_permissions, role_id, ISystemRoleGrantContributor, PermissionService | I0 | X | M | ja | 0 | 0 | WP-I0-104, WP-I0-105 |
| [WP-I0-204](#wp-i0-204--erweiterungspunkt-h1e3-funkprincipal-policy-scheme-cookiesapikeybearer-usersis_bot-provisioning-kette) | Erweiterungspunkt H1/E3: FunkPrincipal, Policy-Scheme Cookies│ApiKey│Bearer, users.is_bot, Provisioning-Kette | I0 | X | M | ja | 0 | 0 | WP-I0-104, WP-I0-907 |
| [WP-I0-205](#wp-i0-205--erweiterungspunkt-f1-oberfläche-integrations-webhook-ingress-verifier-registry-integration_connections-platzhalter-contracts) | Erweiterungspunkt F1: Oberfläche Integrations, Webhook-Ingress, Verifier-Registry, integration_connections, Platzhalter-Contracts | I0 | X | M | ja | 0 | 1 | WP-I0-104, WP-I0-201 |
| [WP-I0-206](#wp-i0-206--erweiterungspunkt-f2-forgejo-container-keycloak-client-funk-forgejo-forgejo-init-sso-smoke) | Erweiterungspunkt F2: Forgejo-Container, Keycloak-Client funk-forgejo, forgejo-init, SSO-Smoke | I0 | X | S | ja | 0 | 0 | WP-I0-102, WP-I0-108 |
| [WP-I0-207](#wp-i0-207--erweiterungspunkt-h6-signalr-hub-liveevents-gruppen-irealtimepublisher-irealtimegroupauthorizer-liveeventsservice) | Erweiterungspunkt H6: SignalR-Hub /live/events/, Gruppen, IRealtimePublisher, IRealtimeGroupAuthorizer, LiveEventsService | I0 | X | S | ja | 0 | 1 | WP-I0-107, WP-I0-105, WP-I0-201 |
| [WP-I0-208](#wp-i0-208--erweiterungspunkte-querschnitt-reservierungen--kollisionstests-r11r12-frontend-registries-routen-sidebar-admin-fake-extensions) | Erweiterungspunkte Querschnitt: Reservierungen + Kollisionstests, R11/R12, Frontend-Registries (Routen, Sidebar, Admin), Fake-Extensions | I0 | X | M | ja | 0 | 0 | WP-I0-104, WP-I0-105 |
| [WP-I0-900](#wp-i0-900--spike-s0--toolchain--walking-skeleton-gerüst) | Spike S0 – Toolchain & Walking-Skeleton-Gerüst | I0 | S | M | nein | 0 | 0 | WP-I0-101 |
| [WP-I0-901](#wp-i0-901--spike-s1--ydotnet--hocuspocus-protokoll-in-net) | Spike S1 – YDotNet + Hocuspocus-Protokoll in .NET | I0 | S | L | ja | 0 | 0 | WP-I0-900, WP-I0-107 |
| [WP-I0-902](#wp-i0-902--spike-s2--yjs--prosemirror-json--html-und-html--json-ohne-node) | Spike S2 – Yjs → ProseMirror-JSON → HTML (und HTML → JSON) ohne Node | I0 | S | L | ja | 0 | 0 | WP-I0-900 |
| [WP-I0-903](#wp-i0-903--spike-s3--pdf-export-mit-pdfsharpmigradoc) | Spike S3 – PDF-Export mit PDFsharp/MigraDoc | I0 | S | M | ja | 0 | 0 | WP-I0-900 |
| [WP-I0-904](#wp-i0-904--spike-s4--kanbangantt-drag-and-drop-in-angular-zoneless-virtualisiert) | Spike S4 – Kanban/Gantt-Drag-and-Drop in Angular (zoneless, virtualisiert) | I0 | S | M | ja | 0 | 0 | WP-I0-900, WP-I0-105 |
| [WP-I0-905](#wp-i0-905--spike-s5--editor-nodeviews-in-angular-mit-tiptap-227-schema-freeze) | Spike S5 – Editor-NodeViews in Angular mit Tiptap 2.27 (Schema-Freeze) | I0 | S | M | ja | 0 | 0 | WP-I0-900, WP-I0-105 |
| [WP-I0-906](#wp-i0-906--spike-s6--charts-11-mit-d3--angular-svg) | Spike S6 – Charts 1:1 mit D3 + Angular-SVG | I0 | S | S | ja | 0 | 0 | WP-I0-105 |
| [WP-I0-907](#wp-i0-907--spike-s7--keycloak-bff-logout-theme-forgejo-sso) | Spike S7 – Keycloak-BFF, Logout, Theme, Forgejo-SSO | I0 | S | M | ja | 0 | 0 | WP-I0-102 |
| [WP-I0-908](#wp-i0-908--spike-s8--objektspeicher-kompatibilität-presigned-postget-upload-modus) | Spike S8 – Objektspeicher-Kompatibilität (Presigned POST/GET, Upload-Modus) | I0 | S | S | ja | 0 | 0 | WP-I0-102 |
| [WP-I0-909](#wp-i0-909--spike-s9--work-item-listen-performance--filter-engine-ef-core) | Spike S9 – Work-Item-Listen-Performance & Filter-Engine (EF Core) | I0 | S | M | ja | 0 | 0 | WP-I0-104 |
| [WP-I0-910](#wp-i0-910--spike-s10--designsystem-parität-angular-ariacdk--floating-ui) | Spike S10 – Designsystem-Parität (Angular Aria/CDK + floating-ui) | I0 | S | M | ja | 0 | 0 | WP-I0-105 |
| [WP-I0-911](#wp-i0-911--spike-s11--paritäts-harness-original-v142-starten-seed-recordreplay-visual-katalog) | Spike S11 – Paritäts-Harness (Original v1.4.2 starten, Seed, Record/Replay, Visual-Katalog) | I0 | S | M | ja | 0 | 0 | WP-I0-101 |
| [WP-I0-912](#wp-i0-912--spike-s12--eigene-outboxjob-queue-auf-postgresql) | Spike S12 – Eigene Outbox/Job-Queue auf PostgreSQL | I0 | S | S | ja | 0 | 0 | WP-I0-104, WP-I0-201 |
| [WP-I0-913](#wp-i0-913--spike-scope-fk--zusammengesetzter-fremdschlüssel-project_id-workspace_id-inkl-nullable-workspace_id) | Spike Scope-FK – zusammengesetzter Fremdschlüssel (project_id, workspace_id) inkl. nullable workspace_id | I0 | S | S | ja | 0 | 0 | WP-I0-104 |
| [WP-I0-999](#wp-i0-999--abnahme-i0--walking-skeleton-g5) | Abnahme I0 – Walking Skeleton (G5) | I0 | A | S | nein | 0 | 0 | WP-I0-001, WP-I0-002, WP-I0-003, WP-I0-004, WP-I0-005, WP-I0-006, WP-I0-101, WP-I0-102, WP-I0-103, WP-I0-104, WP-I0-105, WP-I0-106, WP-I0-107, WP-I0-108, WP-I0-109, WP-I0-201, WP-I0-202, WP-I0-203, WP-I0-204, WP-I0-205, WP-I0-206, WP-I0-207, WP-I0-208, WP-I0-900, WP-I0-907, WP-I0-910, WP-I0-911 |
| [WP-I1-001](#wp-i1-001--workspace-einstellungen-general-löschen-settings-rahmen-stammdatenlisten-themes-api) | Workspace-Einstellungen (General, Löschen, Settings-Rahmen, Stammdatenlisten, Themes-API) | I1 | V | M | ja | 5 | 14 | WP-I0-999, WP-I1-203, WP-I1-103 |
| [WP-I1-002](#wp-i1-002--mitglieder-rollen-einladungen-inkl-automatischer-beitritt-beim-login) | Mitglieder, Rollen, Einladungen (inkl. automatischer Beitritt beim Login) | I1 | V | L | ja | 6 | 16 | WP-I0-999, WP-I1-102, WP-I1-203 |
| [WP-I1-003](#wp-i1-003--shell-ergänzungen-und-navigation-hilfe-menü-whats-new-star-link-sidebar-more-customize-navigation) | Shell-Ergänzungen und Navigation: Hilfe-Menü, What's new, Star-Link, Sidebar „More“, Customize navigation | I1 | V | M | ja | 5 | 2 | WP-I0-999, WP-I1-203 |
| [WP-I1-004](#wp-i1-004--favoriten-mit-ordnern) | Favoriten mit Ordnern | I1 | V | M | ja | 1 | 7 | WP-I1-005, WP-I1-203 |
| [WP-I1-005](#wp-i1-005--projektliste-projektkarten-projekt-statistiken) | Projektliste, Projektkarten, Projekt-Statistiken | I1 | V | M | ja | 3 | 2 | WP-I0-999, WP-I1-105 |
| [WP-I1-006](#wp-i1-006--projekt-detail-zugriffsschutz-beitretenverlassen-projekt-einladungen-per-e-mail) | Projekt-Detail, Zugriffsschutz, Beitreten/Verlassen, Projekt-Einladungen per E-Mail | I1 | V | M | ja | 3 | 9 | WP-I1-002, WP-I1-005 |
| [WP-I1-007](#wp-i1-007--projekt-archivierenwiederherstellen-und-löschen) | Projekt archivieren/wiederherstellen und löschen | I1 | V | S | ja | 2 | 3 | WP-I1-005, WP-I1-101 |
| [WP-I1-008](#wp-i1-008--projekt-sidebar-kontextmenü-erweiterte-sidebar-feature-navigation-tabs) | Projekt-Sidebar, Kontextmenü, erweiterte Sidebar, Feature-Navigation, Tabs | I1 | V | M | ja | 5 | 0 | WP-I1-005, WP-I1-202 |
| [WP-I1-009](#wp-i1-009--projekt-settings-rahmen-general-benutzerpräferenzen) | Projekt-Settings-Rahmen, General, Benutzerpräferenzen | I1 | V | M | ja | 3 | 4 | WP-I1-005, WP-I1-203 |
| [WP-I1-010](#wp-i1-010--projekt-features-toggles-disabled-zustände-projektmitglieder-gastzugriff) | Projekt-Features (Toggles), Disabled-Zustände, Projektmitglieder, Gastzugriff | I1 | V | M | ja | 4 | 5 | WP-I1-009, WP-I1-202, WP-I1-002 |
| [WP-I1-011](#wp-i1-011--states-gruppen-anlagebearbeitung-reihenfolge-per-dnd-default-state-löschen) | States: Gruppen, Anlage/Bearbeitung, Reihenfolge per DnD, Default-State, Löschen | I1 | V | M | ja | 5 | 6 | WP-I1-009, WP-I1-201, WP-I0-913 |
| [WP-I1-012](#wp-i1-012--labels--referenzmodul-hierarchie-anlage-dnd-gruppierung-löschen-bulk-import) | Labels – Referenzmodul (Hierarchie, Anlage, DnD-Gruppierung, Löschen, Bulk-Import) | I1 | V | M | ja | 6 | 6 | WP-I1-009, WP-I1-201, WP-I1-204, WP-I0-913 |
| [WP-I1-013](#wp-i1-013--estimates-einstellungen-schätzsystem-anlegenändernlöschen-validierung) | Estimates: Einstellungen, Schätzsystem anlegen/ändern/löschen, Validierung | I1 | V | M | ja | 5 | 9 | WP-I1-009, WP-I1-203 |
| [WP-I1-014](#wp-i1-014--profil-und-persönliche-einstellungen-inkl-angepasster-e-mail-änderung-und-konto-deaktivierung) | Profil und persönliche Einstellungen (inkl. angepasster E-Mail-Änderung und Konto-Deaktivierung) | I1 | V | M | ja | 6 | 7 | WP-I0-999, WP-I1-103 |
| [WP-I1-015](#wp-i1-015--onboarding) | Onboarding | I1 | V | M | ja | 1 | 1 | WP-I1-014, WP-I1-002 |
| [WP-I1-016](#wp-i1-016--rate-limits-gegen-brute-force-und-missbrauch) | Rate-Limits gegen Brute-Force und Missbrauch | I1 | B | S | ja | 1 | 0 | WP-I1-104 |
| [WP-I1-017](#wp-i1-017--sprachen-deen-übersetzungen-mit-fallbackicu-datums-zeitdarstellung-zeitzonen) | Sprachen de/en, Übersetzungen mit Fallback/ICU, Datums-/Zeitdarstellung, Zeitzonen | I1 | F | M | ja | 4 | 0 | WP-I1-014 |
| [WP-I1-018](#wp-i1-018--themes-varianten-auswahl-mit-server-persistenz-custom-theme-high-contrast-farb-tokens) | Themes: Varianten, Auswahl mit Server-Persistenz, Custom Theme, High Contrast, Farb-Tokens | I1 | F | M | ja | 5 | 0 | WP-I1-014 |
| [WP-I1-019](#wp-i1-019--ui-querschnitt-1-seiten-header-breadcrumbs-leerzustände-modal-hosts-dialog-dropdown-verhalten-tab-reihenfolge) | UI-Querschnitt 1: Seiten-Header, Breadcrumbs, Leerzustände, Modal-Hosts, Dialog-/Dropdown-Verhalten, Tab-Reihenfolge | I1 | F | M | ja | 5 | 0 | WP-I0-999, WP-I1-105, WP-I1-203 |
| [WP-I1-020](#wp-i1-020--ui-querschnitt-2-localstorage-präferenzen-zwischenablagecsv-ungespeicherte-änderungen-fehlerseiten-stale-chunk-legacy-redirects-link-icons) | UI-Querschnitt 2: LocalStorage-Präferenzen, Zwischenablage/CSV, ungespeicherte Änderungen, Fehlerseiten, Stale-Chunk, Legacy-Redirects, Link-Icons | I1 | F | M | ja | 7 | 0 | WP-I0-999 |
| [WP-I1-101](#wp-i1-101--messaging-produktiv-retry-dead-letter-worker-pools-beat-plan-soft-hard-delete-retention) | Messaging produktiv: Retry, Dead-Letter, Worker-Pools, Beat-Plan, Soft-/Hard-Delete, Retention | I1 | B | M | ja | 3 | 0 | WP-I0-999, WP-I0-912 |
| [WP-I1-102](#wp-i1-102--mail-plattform-mailkit-fluid-templates-mailpit-g-mail) | Mail-Plattform: MailKit, Fluid-Templates, Mailpit, G-MAIL | I1 | B | M | ja | 0 | 0 | WP-I0-999, WP-I1-101 |
| [WP-I1-103](#wp-i1-103--objektspeicher-datei-assets-und-uploads-mit-fortschritt-image-picker) | Objektspeicher, Datei-Assets und Uploads mit Fortschritt (Image-Picker) | I1 | V | M | ja | 3 | 8 | WP-I0-999, WP-I0-908, WP-I0-913 |
| [WP-I1-104](#wp-i1-104--valkey-hybridcache-l2-verteilte-rate-limits-tls) | Valkey: HybridCache L2, verteilte Rate-Limits, TLS | I1 | I | S | ja | 1 | 0 | WP-I0-999 |
| [WP-I1-105](#wp-i1-105--designsystem-ausbau-status-prioritäts-icons-datei-icons-logo-picker-illustrationen-propel-vollbestand-blocks) | Designsystem-Ausbau: Status-/Prioritäts-Icons, Datei-Icons, Logo-Picker, Illustrationen, Propel-Vollbestand, Blocks | I1 | F | L | ja | 6 | 0 | WP-I0-999 |
| [WP-I1-201](#wp-i1-201--erweiterungspunkt-a17-istatecatalogilabelcatalog-als-einzige-lesewege-catalog-sources) | Erweiterungspunkt A17: IStateCatalog/ILabelCatalog als einzige Lesewege, Catalog-Sources | I1 | X | S | nein | 0 | 0 | WP-I0-999 |
| [WP-I1-202](#wp-i1-202--erweiterungspunkt-feature-kataloge-iprojectfeaturecatalog-iworkspacefeaturecatalog-contributors-project_features) | Erweiterungspunkt Feature-Kataloge: IProjectFeatureCatalog, IWorkspaceFeatureCatalog, Contributors, PROJECT_FEATURES | I1 | X | S | nein | 0 | 0 | WP-I0-999 |
| [WP-I1-203](#wp-i1-203--erweiterungspunkte-ui-registries-i1-settings_pages-sidebar_items-dynamisch-favorite_entity_renderers-member_row_decorators-role_options-global_modals-estimate_system_flags) | Erweiterungspunkte UI-Registries I1: SETTINGS_PAGES, SIDEBAR_ITEMS (dynamisch), FAVORITE_ENTITY_RENDERERS, MEMBER_ROW_DECORATORS, ROLE_OPTIONS, GLOBAL_MODALS, ESTIMATE_SYSTEM_FLAGS | I1 | X | S | nein | 0 | 0 | WP-I0-999 |
| [WP-I1-204](#wp-i1-204--erweiterungspunkt-activity-grundgerüst-iactivityrecorder-iactivityfieldresolver-registry-reservierte-felder) | Erweiterungspunkt Activity-Grundgerüst: IActivityRecorder, IActivityFieldResolver-Registry, reservierte Felder | I1 | X | S | nein | 0 | 0 | WP-I0-999, WP-I0-201 |
| [WP-I1-205](#wp-i1-205--erweiterungspunkte-iinstanceconfigkeyprovider-und-b1-schema-vorhalte-teamspace_id) | Erweiterungspunkte IInstanceConfigKeyProvider und B1-Schema-Vorhalte (teamspace_id) | I1 | X | S | ja | 0 | 0 | WP-I0-999 |
| [WP-I1-999](#wp-i1-999--abnahme-i1--workspace-projekte-konto-g5) | Abnahme I1 – Workspace, Projekte, Konto (G5) | I1 | A | S | nein | 0 | 0 | WP-I1-001, WP-I1-002, WP-I1-003, WP-I1-004, WP-I1-005, WP-I1-006, WP-I1-007, WP-I1-008, WP-I1-009, WP-I1-010, WP-I1-011, WP-I1-012, WP-I1-013, WP-I1-014, WP-I1-015, WP-I1-016, WP-I1-017, WP-I1-018, WP-I1-019, WP-I1-020, WP-I1-101, WP-I1-102, WP-I1-103, WP-I1-104, WP-I1-105, WP-I1-201, WP-I1-202, WP-I1-203, WP-I1-204, WP-I1-205 |
| [WP-I2-001](#wp-i2-001--work-item-anlegen-und-bearbeiten-modal-fortlaufende-id-autosave-toasts-drafts-rückfrage-bestehende-hinzufügen) | Work Item anlegen und bearbeiten (Modal, fortlaufende ID, Autosave, Toasts, Drafts-Rückfrage, Bestehende hinzufügen) | I2 | V | L | nein | 8 | 3 | WP-I1-999, WP-I2-202, WP-I2-204, WP-I2-205, WP-I2-206, WP-I2-022 |
| [WP-I2-002](#wp-i2-002--work-item-detailseite-identifier-detaildaten-meta-delta-sync-kopfaktionen) | Work-Item-Detailseite (Identifier, Detaildaten, Meta, Delta-Sync, Kopfaktionen) | I2 | V | M | nein | 6 | 6 | WP-I2-001, WP-I2-205 |
| [WP-I2-003](#wp-i2-003--peek-overview-und-hover-vorschau) | Peek-Overview und Hover-Vorschau | I2 | V | M | ja | 5 | 0 | WP-I2-002 |
| [WP-I2-004](#wp-i2-004--sidebar-properties-und-dropdowns-state-priority-assignees-labels-estimate-projekt-datum-read-only-labels) | Sidebar-Properties und Dropdowns (State, Priority, Assignees, Labels, Estimate, Projekt, Datum, Read-only-Labels) | I2 | V | L | ja | 9 | 0 | WP-I2-001 |
| [WP-I2-005](#wp-i2-005--hierarchie-und-relationen-parent-sub-work-items-relationen-widget-aktionsleiste) | Hierarchie und Relationen (Parent, Sub-Work-Items, Relationen, Widget-Aktionsleiste) | I2 | V | M | ja | 4 | 5 | WP-I2-002, WP-I2-203 |
| [WP-I2-006](#wp-i2-006--links-und-anhänge-an-work-items) | Links und Anhänge an Work Items | I2 | V | M | ja | 2 | 13 | WP-I2-002, WP-I2-102 |
| [WP-I2-007](#wp-i2-007--kommentare-emoji-reaktionen-mentions) | Kommentare, Emoji-Reaktionen, Mentions | I2 | V | M | ja | 4 | 11 | WP-I2-008, WP-I2-021 |
| [WP-I2-008](#wp-i2-008--aktivitätsverlauf-activity-filter-beschreibungs-versionen-eigenschafts-historie-abonnements) | Aktivitätsverlauf, Activity-Filter, Beschreibungs-Versionen, Eigenschafts-Historie, Abonnements | I2 | V | L | ja | 5 | 11 | WP-I2-002, WP-I2-024, WP-I1-204 |
| [WP-I2-009](#wp-i2-009--work-items-archivierenwiederherstellen-und-löschen-einzeln-und-bulk) | Work Items archivieren/wiederherstellen und löschen (einzeln und Bulk) | I2 | V | M | ja | 4 | 6 | WP-I2-002 |
| [WP-I2-010](#wp-i2-010--workspace-drafts) | Workspace-Drafts | I2 | V | M | ja | 1 | 6 | WP-I2-001 |
| [WP-I2-011](#wp-i2-011--layout-umschaltung-projekt-work-items-seite-und-kopf-layout-kontextmenü) | Layout-Umschaltung, Projekt-Work-Items-Seite und Kopf, Layout-Kontextmenü | I2 | V | M | nein | 3 | 0 | WP-I2-012 |
| [WP-I2-012](#wp-i2-012--work-item-liste-mit-gruppierungpagination-backend-rich-filter-andornot-filterzeile-filterwerte-filterfelder) | Work-Item-Liste mit Gruppierung/Pagination (Backend), Rich-Filter (AND/OR/NOT), Filterzeile, Filterwerte, Filterfelder | I2 | V | L | nein | 6 | 1 | WP-I2-201, WP-I0-909, WP-I2-001 |
| [WP-I2-013](#wp-i2-013--klassische-filter-applied-filter-chips-display-dropdown-anzeige-einstellungen-je-nutzerprojekt-und-workspace) | Klassische Filter, Applied-Filter-Chips, Display-Dropdown, Anzeige-Einstellungen je Nutzer/Projekt und Workspace | I2 | V | M | ja | 4 | 4 | WP-I2-012 |
| [WP-I2-014](#wp-i2-014--list-layout-mit-gruppierung-inline-properties-sub-work-items-aufklappen) | List-Layout mit Gruppierung, Inline-Properties, Sub-Work-Items aufklappen | I2 | V | M | ja | 3 | 0 | WP-I2-011 |
| [WP-I2-015](#wp-i2-015--kanban-board-swimlanes-karte-löschzone-drag-and-drop) | Kanban-Board, Swimlanes, Karte, Löschzone, Drag-and-Drop | I2 | V | L | ja | 5 | 0 | WP-I2-011, WP-I0-904 |
| [WP-I2-016](#wp-i2-016--calendar-layout-monatwoche-drag-eintrag-quick-add) | Calendar-Layout (Monat/Woche, Drag, Eintrag, Quick-Add) | I2 | V | M | ja | 4 | 0 | WP-I2-011 |
| [WP-I2-017](#wp-i2-017--gantttimeline-verschieben-dauer-datum-setzen-sidebar-reorder-relationen) | Gantt/Timeline (Verschieben, Dauer, Datum setzen, Sidebar-Reorder, Relationen) | I2 | V | L | ja | 5 | 2 | WP-I2-011, WP-I0-904, WP-I2-203 |
| [WP-I2-018](#wp-i2-018--spreadsheet-tabelle-sortierung-tastaturnavigation-mehrfachauswahl-sprung-zu-sub-items) | Spreadsheet (Tabelle, Sortierung, Tastaturnavigation, Mehrfachauswahl, Sprung zu Sub-Items) | I2 | V | L | ja | 4 | 0 | WP-I2-011 |
| [WP-I2-019](#wp-i2-019--inline-property-leiste-quick-add-je-layout-gruppen--quick-action--und-kontextmenü) | Inline-Property-Leiste, Quick-Add je Layout, Gruppen-„+“, Quick-Action- und Kontextmenü | I2 | V | M | ja | 4 | 0 | WP-I2-014 |
| [WP-I2-020](#wp-i2-020--layout-zustände-empty-states-skeleton-loader-virtualisierungendlos-laden-fehlergrenze) | Layout-Zustände: Empty-States, Skeleton-Loader, Virtualisierung/Endlos-Laden, Fehlergrenze | I2 | V | M | ja | 4 | 0 | WP-I2-014 |
| [WP-I2-021](#wp-i2-021--editor-ed-1-lite-text-editor-kommentare-mentions-emojis-links) | Editor ED-1: Lite-Text-Editor (Kommentare), Mentions, Emojis, Links | I2 | D | M | nein | 4 | 0 | WP-I1-103, WP-I0-905, WP-I2-101, WP-I2-207 |
| [WP-I2-022](#wp-i2-022--editor-ed-2a-rich-text-kern-textstruktur-listen-formatierungfarben-markdown-platzhalter-deep-links-anzeige-konfiguration) | Editor ED-2a: Rich-Text-Kern (Textstruktur, Listen, Formatierung/Farben, Markdown, Platzhalter, Deep-Links, Anzeige-Konfiguration) | I2 | D | L | nein | 9 | 0 | WP-I2-021 |
| [WP-I2-023](#wp-i2-023--editor-ed-2b-menüs-und-blöcke-slash-bubble-drag-handleblock-menü-code-block-tabellen-bilder-callouts) | Editor ED-2b: Menüs und Blöcke (Slash, Bubble, Drag-Handle/Block-Menü, Code-Block, Tabellen, Bilder, Callouts) | I2 | D | L | nein | 7 | 5 | WP-I2-022 |
| [WP-I2-024](#wp-i2-024--editor-ed-3-document-editor-read-only-beschreibungs-versionen) | Editor ED-3: Document-Editor read-only (Beschreibungs-Versionen) | I2 | D | S | nein | 1 | 0 | WP-I2-023 |
| [WP-I2-101](#wp-i2-101--funkdocuments-teil-a-server-schema-htmlpm-json-text-extraktion-sanitizing-yjs-update-validierung) | Funk.Documents Teil A: Server-Schema, HTML↔PM-JSON, Text-Extraktion, Sanitizing, Yjs-Update-Validierung | I2 | D | L | ja | 1 | 0 | WP-I0-999, WP-I0-902 |
| [WP-I2-102](#wp-i2-102--ssrf-sicherer-http-client-und-link-crawler) | SSRF-sicherer HTTP-Client und Link-Crawler | I2 | B | S | ja | 1 | 0 | WP-I1-999 |
| [WP-I2-103](#wp-i2-103--dummy-daten-generator-und-volumen-seeder-smlxl) | Dummy-Daten-Generator und Volumen-Seeder (S/M/L/XL) | I2 | I | S | ja | 1 | 0 | WP-I2-001 |
| [WP-I2-201](#wp-i2-201--erweiterungspunkt-b6a1-filter-ast-parser-liste-feld-gruppen-sortier-registries-payload-extension-basismengen-filter) | Erweiterungspunkt B6/A1: Filter-AST, Parser-Liste, Feld-/Gruppen-/Sortier-Registries, Payload-Extension, Basismengen-Filter | I2 | X | M | nein | 0 | 0 | WP-I1-999, WP-I0-909 |
| [WP-I2-202](#wp-i2-202--erweiterungspunkt-a1-work_itemstype_id-minimal-tabelle-work_item_types-iworkitemtyperesolver) | Erweiterungspunkt A1: work_items.type_id, Minimal-Tabelle work_item_types, IWorkItemTypeResolver | I2 | X | S | nein | 0 | 0 | WP-I1-999 |
| [WP-I2-203](#wp-i2-203--erweiterungspunkt-a9-relationstyp-katalog-iworkitemhierarchypolicy-irelatedscopecheck-relation_types-timeline_flags) | Erweiterungspunkt A9: Relationstyp-Katalog, IWorkItemHierarchyPolicy, IRelatedScopeCheck, RELATION_TYPES, TIMELINE_FLAGS | I2 | X | S | nein | 0 | 0 | WP-I1-999 |
| [WP-I2-204](#wp-i2-204--erweiterungspunkt-c1-state-change-pipeline-iworkitemstatechanger-mit-guardshooks-workflow_guard) | Erweiterungspunkt C1: State-Change-Pipeline IWorkItemStateChanger mit Guards/Hooks, WORKFLOW_GUARD | I2 | X | S | nein | 0 | 0 | WP-I1-999, WP-I1-201 |
| [WP-I2-205](#wp-i2-205--erweiterungspunkte-work-item-fassaden-iworkitemreferenceresolver-iworkitemcommands-iintegrationlinkprovider--external_links-iexpandprovider) | Erweiterungspunkte Work-Item-Fassaden: IWorkItemReferenceResolver, IWorkItemCommands, IIntegrationLinkProvider + external_links, IExpandProvider | I2 | X | S | nein | 0 | 0 | WP-I1-999, WP-I0-205 |
| [WP-I2-206](#wp-i2-206--erweiterungspunkte-work-item-ui-registries-property-renderer-bis-duplicate-detection) | Erweiterungspunkte Work-Item-UI-Registries (Property-Renderer bis Duplicate-Detection) | I2 | X | M | nein | 0 | 0 | WP-I1-999 |
| [WP-I2-207](#wp-i2-207--erweiterungspunkt-editordokument-schema-idocumentnodespecidocumentmarkspec-editor_extensions-editor_flags-lite) | Erweiterungspunkt Editor/Dokument-Schema: IDocumentNodeSpec/IDocumentMarkSpec, EDITOR_EXTENSIONS, EDITOR_FLAGS (Lite) | I2 | X | S | nein | 0 | 0 | WP-I0-999, WP-I0-905 |
| [WP-I2-999](#wp-i2-999--abnahme-i2--work-items--layouts-g5) | Abnahme I2 – Work Items & Layouts (G5) | I2 | A | S | nein | 0 | 0 | WP-I2-001, WP-I2-002, WP-I2-003, WP-I2-004, WP-I2-005, WP-I2-006, WP-I2-007, WP-I2-008, WP-I2-009, WP-I2-010, WP-I2-011, WP-I2-012, WP-I2-013, WP-I2-014, WP-I2-015, WP-I2-016, WP-I2-017, WP-I2-018, WP-I2-019, WP-I2-020, WP-I2-021, WP-I2-022, WP-I2-023, WP-I2-024, WP-I2-101, WP-I2-102, WP-I2-103, WP-I2-201, WP-I2-202, WP-I2-203, WP-I2-204, WP-I2-205, WP-I2-206, WP-I2-207 |
| [WP-I3-001](#wp-i3-001--projekt-archive-und-layout-kontexte-cycle-modul-view-archiv-profil) | Projekt-Archive und Layout-Kontexte (Cycle, Modul, View, Archiv, Profil) | I3 | V | M | ja | 2 | 1 | WP-I2-999 |
| [WP-I3-002](#wp-i3-002--projekt-views-liste-anlagebearbeitung-löschen-kontextmenüfavoriten-detail-speichern-aus-filtern) | Projekt-Views (Liste, Anlage/Bearbeitung, Löschen, Kontextmenü/Favoriten, Detail, Speichern aus Filtern) | I3 | V | L | ja | 6 | 10 | WP-I2-999, WP-I3-201 |
| [WP-I3-003](#wp-i3-003--workspace-views-übersicht-anlagebearbeitunglöschen-all-work-items) | Workspace-Views (Übersicht, Anlage/Bearbeitung/Löschen, All work items) | I3 | V | M | ja | 3 | 4 | WP-I3-002 |
| [WP-I3-004](#wp-i3-004--cycle-liste-mit-gruppen-suchefilter-inline-dashboard-workspace-weite-active-cycles) | Cycle-Liste mit Gruppen, Suche/Filter, Inline-Dashboard, Workspace-weite Active Cycles | I3 | V | M | ja | 4 | 3 | WP-I3-005, WP-I3-101 |
| [WP-I3-005](#wp-i3-005--cycles-anlegenbearbeiten-datumsüberschneidung-archivieren-löschen-kontextmenü-favoriten) | Cycles anlegen/bearbeiten, Datumsüberschneidung, archivieren, löschen, Kontextmenü, Favoriten | I3 | V | L | ja | 6 | 10 | WP-I2-999, WP-I3-201 |
| [WP-I3-006](#wp-i3-006--cycle-peekdetail-fortschritt-verteilungen-burndown-anzeige-je-cycle-und-modul) | Cycle-Peek/Detail, Fortschritt, Verteilungen, Burndown, Anzeige je Cycle und Modul | I3 | V | L | ja | 4 | 7 | WP-I3-005, WP-I3-101 |
| [WP-I3-007](#wp-i3-007--work-items-cycles-zuordnen-unvollständige-übertragen-cycle-dropdown) | Work Items Cycles zuordnen, unvollständige übertragen, Cycle-Dropdown | I3 | V | M | ja | 3 | 4 | WP-I3-005 |
| [WP-I3-008](#wp-i3-008--modul-übersicht-in-drei-layouts-suchefiltersortierung-kontextmenü-und-favoriten) | Modul-Übersicht in drei Layouts, Suche/Filter/Sortierung, Kontextmenü und Favoriten | I3 | V | M | ja | 3 | 4 | WP-I3-009 |
| [WP-I3-009](#wp-i3-009--module-anlegenbearbeiten-status-links-sidebar-archivieren-löschen) | Module anlegen/bearbeiten, Status, Links, Sidebar, archivieren, löschen | I3 | V | L | ja | 6 | 13 | WP-I2-999, WP-I3-201 |
| [WP-I3-010](#wp-i3-010--modul-detailseite-work-items-zuordnen-module-dropdown) | Modul-Detailseite, Work Items zuordnen, Module-Dropdown | I3 | V | M | ja | 3 | 4 | WP-I3-009, WP-I3-101 |
| [WP-I3-011](#wp-i3-011--intake-je-projekt-mit-triage-state-seite-openclosed-filtersortierung-detail-anlage) | Intake: je Projekt mit Triage-State, Seite Open/Closed, Filter/Sortierung, Detail, Anlage | I3 | V | L | ja | 5 | 17 | WP-I2-999 |
| [WP-I3-012](#wp-i3-012--intake-aktionen-annehmen-ablehnen-zurückstellen-duplikat-bearbeitenlöschen-navigation-benachrichtigungs-detail) | Intake-Aktionen: annehmen, ablehnen, zurückstellen, Duplikat, bearbeiten/löschen, Navigation, Benachrichtigungs-Detail | I3 | V | L | ja | 7 | 4 | WP-I3-011 |
| [WP-I3-013](#wp-i3-013--automationen-auto-archive-und-auto-close) | Automationen Auto-Archive und Auto-Close | I3 | B | M | ja | 2 | 0 | WP-I2-999 |
| [WP-I3-101](#wp-i3-101--chart-bausteine-bar-pie-area-line-radar-treemap-burndown-und-farbpaletten) | Chart-Bausteine (Bar, Pie, Area, Line, Radar, TreeMap, Burndown) und Farbpaletten | I3 | F | M | ja | 1 | 0 | WP-I2-999, WP-I0-906 |
| [WP-I3-201](#wp-i3-201--erweiterungspunkte-planung-icycleschedulingpolicy-cycle_flags-entity_quick_actions) | Erweiterungspunkte Planung: ICycleSchedulingPolicy, CYCLE_FLAGS, ENTITY_QUICK_ACTIONS | I3 | X | S | nein | 0 | 0 | WP-I2-999 |
| [WP-I3-999](#wp-i3-999--abnahme-i3--planung-g5) | Abnahme I3 – Planung (G5) | I3 | A | S | nein | 0 | 0 | WP-I3-001, WP-I3-002, WP-I3-003, WP-I3-004, WP-I3-005, WP-I3-006, WP-I3-007, WP-I3-008, WP-I3-009, WP-I3-010, WP-I3-011, WP-I3-012, WP-I3-013, WP-I3-101, WP-I3-201 |
| [WP-I4-001](#wp-i4-001--page-liste-mit-tabs-suchefiltersortierung-anlage-favoriten) | Page-Liste mit Tabs, Suche/Filter/Sortierung, Anlage, Favoriten | I4 | V | M | nein | 4 | 5 | WP-I3-999, WP-I4-201 |
| [WP-I4-002](#wp-i4-002--page-aktionen-datendetail-sperren-zugriff-archivieren-löschen-duplizieren-referenzprotokoll) | Page-Aktionen: Daten/Detail, sperren, Zugriff, archivieren, löschen, duplizieren, Referenzprotokoll | I4 | V | L | ja | 7 | 11 | WP-I4-001 |
| [WP-I4-003](#wp-i4-003--page-export-als-pdf-und-markdown) | Page-Export als PDF und Markdown | I4 | D | M | ja | 1 | 1 | WP-I4-002, WP-I0-903, WP-I4-101 |
| [WP-I4-004](#wp-i4-004--kollaborativer-page-editor-seite-toolbar-kopf-outline-info--assets-panel-anzeigeoptionen--ed-4-hüllen) | Kollaborativer Page-Editor (Seite, Toolbar, Kopf, Outline, Info-, Assets-Panel, Anzeigeoptionen) – ED-4-Hüllen | I4 | V | L | nein | 7 | 0 | WP-I4-007, WP-I4-002 |
| [WP-I4-005](#wp-i4-005--page-versionshistorie) | Page-Versionshistorie | I4 | V | M | ja | 1 | 2 | WP-I4-006 |
| [WP-I4-006](#wp-i4-006--realtime-kollaborationsserver-protokoll-dokument-lebenszyklus-persistenz-titel-sync-fehlerforce-close-konvertierung) | Realtime-Kollaborationsserver: Protokoll, Dokument-Lebenszyklus, Persistenz, Titel-Sync, Fehler/Force-Close, Konvertierung | I4 | D | L | nein | 4 | 1 | WP-I4-101, WP-I4-202, WP-I0-107, WP-I0-901 |
| [WP-I4-007](#wp-i4-007--client-kollaboration-echtzeit-editor-bindung-offline-cache-rest-fallback-seitenereignisse-ed-4-kern) | Client-Kollaboration: Echtzeit-Editor-Bindung, Offline-Cache, REST-Fallback, Seitenereignisse (ED-4-Kern) | I4 | D | L | nein | 3 | 0 | WP-I4-006, WP-I2-024 |
| [WP-I4-008](#wp-i4-008--horizontale-skalierung-des-realtime-servers-valkey-backplane-postgresql-signale) | Horizontale Skalierung des Realtime-Servers (Valkey-Backplane, PostgreSQL-Signale) | I4 | B | M | ja | 1 | 0 | WP-I4-006 |
| [WP-I4-009](#wp-i4-009--demo-inhalte-bei-workspace-anlage-vollständiger-seed-inkl-cycles-module-views-pages) | Demo-Inhalte bei Workspace-Anlage (vollständiger Seed inkl. Cycles, Module, Views, Pages) | I4 | B | M | ja | 1 | 0 | WP-I4-002 |
| [WP-I4-101](#wp-i4-101--funkdocuments-teil-b-yjs--prosemirror-yjsupdatewriter-document-variante-markdown) | Funk.Documents Teil B: Yjs ⇄ ProseMirror, YjsUpdateWriter, Document-Variante, Markdown | I4 | D | L | ja | 0 | 0 | WP-I2-999, WP-I0-901, WP-I0-902 |
| [WP-I4-201](#wp-i4-201--erweiterungspunkte-d1d2-pages-ohne-projektpflicht-project_pages-parent_id-ipagehierarchyqueries-ipageaccessextension-page_-tokens) | Erweiterungspunkte D1/D2: Pages ohne Projektpflicht, project_pages, parent_id, IPageHierarchy(+Queries), IPageAccessExtension, PAGE_*-Tokens | I4 | X | S | nein | 0 | 0 | WP-I3-999 |
| [WP-I4-202](#wp-i4-202--erweiterungspunkte-kollaboration-icollaborationdocumenttype-affectedpages-editor_blocks-editor_mention_types) | Erweiterungspunkte Kollaboration: ICollaborationDocumentType, affectedPages, EDITOR_BLOCKS, EDITOR_MENTION_TYPES | I4 | X | S | nein | 0 | 0 | WP-I2-999, WP-I4-101 |
| [WP-I4-999](#wp-i4-999--abnahme-i4--pages--realtime-g5) | Abnahme I4 – Pages & Realtime (G5) | I4 | A | S | nein | 0 | 0 | WP-I4-001, WP-I4-002, WP-I4-003, WP-I4-004, WP-I4-005, WP-I4-006, WP-I4-007, WP-I4-008, WP-I4-009, WP-I4-101, WP-I4-201, WP-I4-202 |
| [WP-I5-001](#wp-i5-001--workspace-analytics-tabs-kennzahlen-project-insights-active-projects-created-vs-resolved-customized-insights-insight-tabelle-mit-csv) | Workspace-Analytics: Tabs, Kennzahlen, Project Insights, Active Projects, Created vs Resolved, Customized Insights, Insight-Tabelle mit CSV | I5 | V | L | ja | 7 | 3 | WP-I4-999, WP-I3-101 |
| [WP-I5-002](#wp-i5-002--analytics-panel-projekt-cycle-modul-legacy-analytics-gespeicherte-analytics-views-export-per-e-mail) | Analytics-Panel (Projekt, Cycle, Modul), Legacy-Analytics, gespeicherte Analytics-Views, Export per E-Mail | I5 | V | M | ja | 2 | 12 | WP-I5-001, WP-I1-102 |
| [WP-I5-003](#wp-i5-003--workspace-home-widgets-widget-verwaltung-quickstart-quick-links-recents-produkt-tour-legacy-dashboard) | Workspace-Home: Widgets, Widget-Verwaltung, Quickstart, Quick links, Recents, Produkt-Tour, Legacy-Dashboard | I5 | V | L | ja | 7 | 11 | WP-I4-999, WP-I5-202 |
| [WP-I5-004](#wp-i5-004--stickies-widget-seite-bearbeitung-ed-5) | Stickies: Widget, Seite, Bearbeitung (ED-5) | I5 | V | M | ja | 3 | 5 | WP-I5-003 |
| [WP-I5-005](#wp-i5-005--benachrichtigungen-erzeugen-in-app-mentions-automatisches-abonnieren-zähler-push) | Benachrichtigungen erzeugen: In-App, Mentions, automatisches Abonnieren, Zähler-Push | I5 | B | M | nein | 3 | 0 | WP-I4-999, WP-I5-202, WP-I0-207 |
| [WP-I5-006](#wp-i5-006--inbox-seite-liste-filteroptionen-lesenarchivierensnoozen-detail) | Inbox: Seite, Liste, Filter/Optionen, lesen/archivieren/snoozen, Detail | I5 | V | L | ja | 4 | 10 | WP-I5-005 |
| [WP-I5-007](#wp-i5-007--e-mail-benachrichtigungen-mit-5-minuten-bündelung-und-einstellungen) | E-Mail-Benachrichtigungen mit 5-Minuten-Bündelung und Einstellungen | I5 | B | M | ja | 2 | 2 | WP-I5-005, WP-I1-102 |
| [WP-I5-008](#wp-i5-008--suche-globale-suche-entity-suche-für-mentionspicker-work-item-picker) | Suche: Globale Suche, Entity-Suche für Mentions/Picker, Work-Item-Picker | I5 | V | M | ja | 3 | 2 | WP-I5-201 |
| [WP-I5-009](#wp-i5-009--power-k-command-palette-mit-navigations--erstell--kontext--account-preferences-hilfebefehlen-und-shortcuts) | Power-K Command Palette mit Navigations-, Erstell-, Kontext-, Account-/Preferences-/Hilfebefehlen und Shortcuts | I5 | F | L | ja | 6 | 0 | WP-I5-008, WP-I5-202 |
| [WP-I5-010](#wp-i5-010--your-work-summary-work-item-tabs-activity-profil-sidebar) | Your work: Summary, Work-Item-Tabs, Activity, Profil-Sidebar | I5 | V | M | ja | 4 | 6 | WP-I4-999 |
| [WP-I5-201](#wp-i5-201--erweiterungspunkt-g1b6-isearchprovider-iindexingpipeline-search_documents-vector-nullembeddinggenerator-iindexdocumentenricher) | Erweiterungspunkt G1/B6: ISearchProvider, IIndexingPipeline, search_documents, vector, NullEmbeddingGenerator, IIndexDocumentEnricher | I5 | X | M | nein | 0 | 0 | WP-I4-999 |
| [WP-I5-202](#wp-i5-202--erweiterungspunkte-ui-i5-home_widgets-power_k_commands-search_result_renderers-erste-nutzung-live_event_handlers) | Erweiterungspunkte UI I5: HOME_WIDGETS, POWER_K_COMMANDS, SEARCH_RESULT_RENDERERS, erste Nutzung LIVE_EVENT_HANDLERS | I5 | X | S | nein | 0 | 0 | WP-I4-999 |
| [WP-I5-999](#wp-i5-999--abnahme-i5--überblick-g5) | Abnahme I5 – Überblick (G5) | I5 | A | S | nein | 0 | 0 | WP-I5-001, WP-I5-002, WP-I5-003, WP-I5-004, WP-I5-005, WP-I5-006, WP-I5-007, WP-I5-008, WP-I5-009, WP-I5-010, WP-I5-201, WP-I5-202 |
| [WP-I6-001](#wp-i6-001--god-mode-abmeldung-fehleransicht-dashboard-shell-header-konto-menü-hilfe-unsaved-dialog-kopierfelder-404) | God Mode: Abmeldung, Fehleransicht, Dashboard-Shell, Header, Konto-Menü, Hilfe, Unsaved-Dialog, Kopierfelder, 404 | I6 | V | L | ja | 9 | 0 | WP-I5-999, WP-I6-203 |
| [WP-I6-002](#wp-i6-002--god-mode-allgemeine-einstellungen-smtp-test-e-mail-ai-einstellungen-bildbibliotheken) | God Mode: Allgemeine Einstellungen, SMTP, Test-E-Mail, AI-Einstellungen, Bildbibliotheken | I6 | V | M | ja | 5 | 5 | WP-I6-001, WP-I1-102 |
| [WP-I6-003](#wp-i6-003--god-mode-workspace-liste-workspace-anlage-sperren-workspace-anlegen-willkommens-popup) | God Mode: Workspace-Liste, Workspace-Anlage sperren, Workspace anlegen, Willkommens-Popup | I6 | V | M | ja | 4 | 3 | WP-I6-001 |
| [WP-I6-004](#wp-i6-004--projekt-veröffentlichen-publish-modal-board-einstellungen-metadaten) | Projekt veröffentlichen (Publish-Modal, Board-Einstellungen, Metadaten) | I6 | V | M | ja | 2 | 7 | WP-I5-999 |
| [WP-I6-005](#wp-i6-005--space-app-shell-login-einstieg-über-keycloak-fehler-404-seiten-legacy-redirects-social-meta-iframe-badge-inkl-nachweis-entfallener-space-logins) | Space-App: Shell, Login-Einstieg über Keycloak, Fehler-/404-Seiten, Legacy-Redirects, Social-Meta, iframe, Badge (inkl. Nachweis entfallener Space-Logins) | I6 | V | L | ja | 13 | 1 | WP-I6-004, WP-I6-203 |
| [WP-I6-006](#wp-i6-006--space-board-öffentliche-issue-liste-stammdaten-navbar-listkanban-read-only-chips-filter-popover-aktive-filter) | Space-Board: öffentliche Issue-Liste, Stammdaten, Navbar, List/Kanban read-only, Chips, Filter-Popover, aktive Filter | I6 | V | L | ja | 8 | 6 | WP-I6-005 |
| [WP-I6-007](#wp-i6-007--space-öffentliches-issue-detail-peek-kommentarbilderasset-auslieferung-mentions-ed-6) | Space: öffentliches Issue-Detail, Peek, Kommentarbilder/Asset-Auslieferung, Mentions (ED-6) | I6 | V | M | ja | 4 | 7 | WP-I6-006 |
| [WP-I6-008](#wp-i6-008--space-interaktionen-kommentare-reaktionen-votes-öffentliche-intake-einreichung) | Space-Interaktionen: Kommentare, Reaktionen, Votes, öffentliche Intake-Einreichung | I6 | V | M | ja | 5 | 21 | WP-I6-007 |
| [WP-I6-009](#wp-i6-009--public-api-v1-api-key-authentifizierung-rate-limit-je-key-aktivitätsprotokoll-openapi-aktueller-benutzer) | Public API v1: API-Key-Authentifizierung, Rate-Limit je Key, Aktivitätsprotokoll, OpenAPI, aktueller Benutzer | I6 | B | M | nein | 5 | 4 | WP-I6-016, WP-I6-201 |
| [WP-I6-010](#wp-i6-010--public-api-v1-projekte-archiv-summary-states-labels-mitglieder-einladungen) | Public API v1: Projekte, Archiv, Summary, States, Labels, Mitglieder, Einladungen | I6 | B | L | ja | 8 | 37 | WP-I6-009 |
| [WP-I6-011](#wp-i6-011--public-api-v1-stickies-user-assets-generic-workspace-assets) | Public API v1: Stickies, User-Assets, Generic Workspace Assets | I6 | B | S | ja | 3 | 14 | WP-I6-009 |
| [WP-I6-012](#wp-i6-012--public-api-v1-work-items-identifier-suche-links-kommentare-aktivitäten-anhänge-relationen-intake) | Public API v1: Work Items, Identifier, Suche, Links, Kommentare, Aktivitäten, Anhänge, Relationen, Intake | I6 | B | L | ja | 9 | 55 | WP-I6-010 |
| [WP-I6-013](#wp-i6-013--public-api-v1-cycles-work-items-in-cycles-transfer-cycle-archiv-modules-work-items-in-modulen-modul-archiv) | Public API v1: Cycles, Work Items in Cycles, Transfer, Cycle-Archiv, Modules, Work Items in Modulen, Modul-Archiv | I6 | B | M | ja | 7 | 26 | WP-I6-012 |
| [WP-I6-014](#wp-i6-014--webhook-verwaltung-liste-anlage-secret-anzeigenregenerierenherunterladen-bearbeitung-löschung) | Webhook-Verwaltung: Liste, Anlage, Secret anzeigen/regenerieren/herunterladen, Bearbeitung, Löschung | I6 | V | M | ja | 5 | 6 | WP-I5-999 |
| [WP-I6-015](#wp-i6-015--webhook-zustellung-datenmodellevent-typen-zustellung-payload-deaktivierungs-mail-protokoll-ssrf-schutz) | Webhook-Zustellung: Datenmodell/Event-Typen, Zustellung, Payload, Deaktivierungs-Mail, Protokoll, SSRF-Schutz | I6 | B | L | ja | 6 | 1 | WP-I6-014, WP-I6-202 |
| [WP-I6-016](#wp-i6-016--api-tokens-liste-anlage-löschung) | API-Tokens: Liste, Anlage, Löschung | I6 | V | M | ja | 3 | 5 | WP-I5-999 |
| [WP-I6-017](#wp-i6-017--work-item-export-csvxlsxjson-export-historie-und-download) | Work-Item-Export (CSV/XLSX/JSON), Export-Historie und Download | I6 | B | M | ja | 2 | 2 | WP-I6-202 |
| [WP-I6-018](#wp-i6-018--ki-assistent-im-work-item-modal-und-unsplash-bildsuche) | KI-Assistent im Work-Item-Modal und Unsplash-Bildsuche | I6 | V | M | ja | 2 | 3 | WP-I5-999 |
| [WP-I6-201](#wp-i6-201--erweiterungspunkte-public-api-iv1payloadextension-iv1filterparameterbinding-erweiterbare-openapi-gruppen) | Erweiterungspunkte Public API: IV1PayloadExtension, IV1FilterParameterBinding, erweiterbare OpenAPI-Gruppen | I6 | X | S | nein | 0 | 0 | WP-I5-999 |
| [WP-I6-202](#wp-i6-202--erweiterungspunkte-iwebhookeventsource-und-iexporttypeprovider) | Erweiterungspunkte IWebhookEventSource und IExportTypeProvider | I6 | X | S | nein | 0 | 0 | WP-I5-999 |
| [WP-I6-203](#wp-i6-203--erweiterungspunkte-spaceadmin-space_route_extensions-editor_extensions-space-admin-registries-mit-ce-inhalt) | Erweiterungspunkte Space/Admin: SPACE_ROUTE_EXTENSIONS, EDITOR_EXTENSIONS (Space), ADMIN-Registries mit CE-Inhalt | I6 | X | S | nein | 0 | 0 | WP-I5-999 |
| [WP-I6-999](#wp-i6-999--abnahme-i6--außenwirkung--administration-g5) | Abnahme I6 – Außenwirkung & Administration (G5) | I6 | A | S | nein | 0 | 0 | WP-I6-001, WP-I6-002, WP-I6-003, WP-I6-004, WP-I6-005, WP-I6-006, WP-I6-007, WP-I6-008, WP-I6-009, WP-I6-010, WP-I6-011, WP-I6-012, WP-I6-013, WP-I6-014, WP-I6-015, WP-I6-016, WP-I6-017, WP-I6-018, WP-I6-201, WP-I6-202, WP-I6-203 |
| [WP-I7-101](#wp-i7-101--funk-cli-self-hosting-cli-backuprestore-betriebs-commands) | funk-cli: Self-Hosting-CLI, Backup/Restore, Betriebs-Commands | I7 | B | L | ja | 3 | 0 | WP-I6-999 |
| [WP-I7-102](#wp-i7-102--docker-compose-aspire-publisher-und-docker-swarm-deployment) | Docker Compose (Aspire-Publisher) und Docker-Swarm-Deployment | I7 | I | M | ja | 1 | 0 | WP-I6-999 |
| [WP-I7-103](#wp-i7-103--all-in-one-container-funk-aio) | All-in-One-Container funk-aio | I7 | I | M | ja | 1 | 0 | WP-I6-999 |
| [WP-I7-104](#wp-i7-104--read-replica-unterstützung) | Read-Replica-Unterstützung | I7 | B | S | ja | 1 | 0 | WP-I6-999 |
| [WP-I7-105](#wp-i7-105--tls-modi-und-reverse-proxy-mit-automatischem-https-acme) | TLS-Modi und Reverse-Proxy mit automatischem HTTPS (ACME) | I7 | I | M | ja | 1 | 0 | WP-I6-999 |
| [WP-I7-106](#wp-i7-106--helm-chart-deployhelmfunk) | Helm-Chart deploy/helm/funk | I7 | I | M | ja | 0 | 0 | WP-I6-999 |
| [WP-I7-107](#wp-i7-107--airgapped-bundle-und-egress-gesperrter-e2e-lauf) | Airgapped-Bundle und Egress-gesperrter E2E-Lauf | I7 | I | M | ja | 0 | 0 | WP-I6-999 |
| [WP-I7-108](#wp-i7-108--sicherheitshärtung-csp-enforce-zap-permission-matrix-100--upgrade-pfad) | Sicherheitshärtung: CSP-Enforce, ZAP, Permission-Matrix 100 %, Upgrade-Pfad | I7 | I | M | ja | 0 | 0 | WP-I6-999 |
| [WP-I7-109](#wp-i7-109--last--soak--und-performance-abnahme-lt-08-lt-13-lt-21-worker-kill-tests) | Last-, Soak- und Performance-Abnahme (LT-08, LT-13, LT-21, Worker-Kill-Tests) | I7 | I | M | ja | 0 | 0 | WP-I6-999 |
| [WP-I7-110](#wp-i7-110--paritäts-gesamtabnahme-aller-screens-endpunkt-abdeckung-100--abweichungsliste) | Paritäts-Gesamtabnahme aller Screens, Endpunkt-Abdeckung 100 %, Abweichungsliste | I7 | I | M | nein | 0 | 0 | WP-I6-999, WP-I7-107, WP-I7-108 |
| [WP-I7-201](#wp-i7-201--erweiterungspunkte-stabilisieren-contract-snapshots-aller-erweiterungs-interfaces-airgap-test-mit-forgejo) | Erweiterungspunkte stabilisieren: Contract-Snapshots aller Erweiterungs-Interfaces, Airgap-Test mit Forgejo | I7 | X | S | ja | 0 | 0 | WP-I6-999 |
| [WP-I7-999](#wp-i7-999--abnahme-i7--ce-release-kandidat-g5--g6) | Abnahme I7 – CE-Release-Kandidat (G5 + G6) | I7 | A | S | nein | 0 | 0 | WP-I7-101, WP-I7-102, WP-I7-103, WP-I7-104, WP-I7-105, WP-I7-106, WP-I7-107, WP-I7-108, WP-I7-109, WP-I7-110, WP-I7-201 |

Summen: I0 = 38, I1 = 31, I2 = 35, I3 = 16, I4 = 13, I5 = 13, I6 = 22, I7 = 12; insgesamt 180 Arbeitspakete, 507 CE-IDs, 564 registrierte Endpunkte.

### 3.1 Erweiterungspunkt-Pakete (Typ X) und die Pakete, die sie nutzen

| Erweiterungspunkt-Paket | Andockstelle (Quelle) | direkt abhängige Pakete |
|---|---|---|
| WP-I0-201 – Erweiterungspunkt C3 | 01 §1.4 C3; 16 §5.11; 16 §4.6 Zeile „Event-Katalog …“ (Träger CE-OPS-021/-022, erste Events CE-WS-001/CE-PRJ-004) | WP-I0-002, WP-I0-205, WP-I0-207, WP-I0-912, WP-I1-204 |
| WP-I0-202 – Erweiterungspunkt B1/A2 | 01 §1.4 B1/A2; 16 §3.3.0 E-20; 16 §4.6 (Träger CE-WS-001, CE-PRJ-006) | WP-I0-002 |
| WP-I0-203 – Erweiterungspunkt E5 | 01 §1.4 E5; 16 §3.3.0 E-09; 16 §4.6 (Träger CE-WS-008, CE-WS-012) | WP-I0-001, WP-I0-002 |
| WP-I0-204 – Erweiterungspunkt H1/E3 | 01 §1.4 E3/H1; 16 §4.6 (Träger CE-AUTH-001/-024/-025, CE-AUTH-028/-029) | WP-I0-001 |
| WP-I0-205 – Erweiterungspunkt F1 | 01 §1.4 F1/F2; 16 §3.3.0 E-13 (Teil `integration_connections`), E-25; 16 §4.6 (Träger CE-OPS-021, CE-OPS-022) | WP-I2-205 |
| WP-I0-206 – Erweiterungspunkt F2 | 01 §1.4 F2; 16 §3.4.8 (Zeile I0) | – (Abnahme) |
| WP-I0-207 – Erweiterungspunkt H6 | 01 §1.4 H6; 16 §3.3.0 E-22; 16 §4.6 (Walking Skeleton, `RealtimeSmokeTests`) | WP-I5-005 |
| WP-I0-208 – Erweiterungspunkte Querschnitt | 16 §1.4 Zeile I0 (Reservierungen, Registries); 16 §4.6 „Bewusst ohne Träger-CE-ID“ (CE-OPS-022) | WP-I0-003, WP-I0-004 |
| WP-I1-201 – Erweiterungspunkt A17 | 01 §1.4 A17; 16 §3.3.0 E-21; 16 §4.6 (Träger CE-PRJ-023…033) | WP-I1-011, WP-I1-012, WP-I2-204 |
| WP-I1-202 – Erweiterungspunkt Feature-Kataloge | 16 §3.3.0 E-01, E-02, E-26; 16 §4.6 (Träger CE-PRJ-019, CE-PRJ-020) | WP-I1-008, WP-I1-010 |
| WP-I1-203 – Erweiterungspunkte UI-Registries I1 | 16 §1.4 Zeile I1; 16 §4.6 (Träger CE-WS-023, CE-WS-010, CE-PRJ-019, CE-PRJ-034/-035) | WP-I1-001, WP-I1-002, WP-I1-003, WP-I1-004, WP-I1-009, WP-I1-013, WP-I1-019 |
| WP-I1-204 – Erweiterungspunkt Activity-Grundgerüst | 16 §1.4 Zeile I1; 16 §4.6 (Träger CE-WI-039/-040, Gerüst ab I1) | WP-I1-012, WP-I2-008 |
| WP-I1-205 – Erweiterungspunkte IInstanceConfigKeyProvider und B1-Schema-Vorhalte (teamspace_id) | 16 §3.3.0 E-12; 01 §1.4 B1 (I1-Teil); 16 §4.6 (Träger CE-INST-002) | – (Abnahme) |
| WP-I2-201 – Erweiterungspunkt B6/A1 | 01 §1.4 A1/B6; 16 §3.3.0 E-04; 16 §4.6 (Träger CE-LV-006…010, CE-LV-017, CE-LV-046) | WP-I2-012 |
| WP-I2-202 – Erweiterungspunkt A1 | 01 §1.4 A1; 16 §3.3.0 E-03; 16 §4.6 (Träger CE-WI-001, CE-WI-049) | WP-I2-001 |
| WP-I2-203 – Erweiterungspunkt A9 | 01 §1.4 A9; 16 §3.3.0 E-05; 16 §4.6 (Träger CE-WI-031…033, CE-LV-033, CE-API-024) | WP-I2-005, WP-I2-017 |
| WP-I2-204 – Erweiterungspunkt C1 | 01 §1.4 C1; 16 §4.6 (Träger CE-WI-021, CE-WI-003; weitere Origins in I3/I6) | WP-I2-001 |
| WP-I2-205 – Erweiterungspunkte Work-Item-Fassaden | 16 §3.3.0 E-06, E-07 (Teil `expand`), E-13, E-18; 16 §4.6 (Träger CE-WI-009, CE-WI-002, CE-WI-001, CE-WI-010) | WP-I2-001, WP-I2-002 |
| WP-I2-206 – Erweiterungspunkte Work-Item-UI-Registries (Property-Renderer bis Duplicate-Detection) | 16 §1.4 Zeile I2 (Frontend); 16 §4.6 (Träger CE-WI-001/-010/-014/-034, CE-LV-008/-017…037) | WP-I2-001 |
| WP-I2-207 – Erweiterungspunkt Editor/Dokument-Schema | 16 §3.3.0 E-11; 16 §4.6 (Träger CE-WI-037, CE-WI-044) | WP-I2-021 |
| WP-I3-201 – Erweiterungspunkte Planung | 16 §3.3.0 E-14 (I3-Teil), E-15; 16 §4.6 (Träger CE-CYC-002…013, CE-MOD-011, CE-LV-050) | WP-I3-002, WP-I3-005, WP-I3-009 |
| WP-I4-201 – Erweiterungspunkte D1/D2 | 01 §1.4 D1/D2; 16 §3.3.0 E-23; 16 §4.6 (Träger CE-PAGE-001/-003/-004/-006/-007) | WP-I4-001 |
| WP-I4-202 – Erweiterungspunkte Kollaboration | 16 §3.3.0 E-10; 16 §4.6 (Träger CE-RT-001, CE-RT-004, CE-RT-005) | WP-I4-006 |
| WP-I5-201 – Erweiterungspunkt G1/B6 | 01 §1.4 G1/B6; 16 §3.3.0 E-24; 16 §4.6 (Träger CE-SRCH-001…003) | WP-I5-008 |
| WP-I5-202 – Erweiterungspunkte UI I5 | 16 §1.4 Zeile I5; 16 §4.6 (Träger CE-HOME-001/-002, CE-NOTIF-001, CE-SRCH-004) | WP-I5-003, WP-I5-005, WP-I5-009 |
| WP-I6-201 – Erweiterungspunkte Public API | 16 §3.3.0 E-07, E-19; 16 §4.6 (Träger CE-API-017, CE-API-019) | WP-I6-009 |
| WP-I6-202 – Erweiterungspunkte IWebhookEventSource und IExportTypeProvider | 16 §3.3.0 E-08, E-16; 16 §4.6 (Träger CE-WH-001/-007/-008, CE-EXP-001/-002) | WP-I6-015, WP-I6-017 |
| WP-I6-203 – Erweiterungspunkte Space/Admin | 16 §1.4 Zeile I6; 16 §4.6 (Träger CE-SPACE-001/-018/-025, CE-INST-003/-025) | WP-I6-001, WP-I6-005 |
| WP-I7-201 – Erweiterungspunkte stabilisieren | 16 §1.4 Zeile I7; 16 §4.6 (Träger CE-OPS-023) | – (Abnahme) |

### 3.2 Kritischer Pfad je Inkrement (Schätzung)

Dauer-Schätzung je Paket: S = 2, M = 5, L = 10 Agenten-Arbeitstage; Pakete außerhalb des Inkrements gelten als erledigt. Der kritische Pfad bestimmt die Mindestdauer eines Inkrements bei unbegrenzter Parallelität.

| Inkrement | Pakete | Summe (Tage) | kritischer Pfad (Tage) | Pfad |
|---|---|---|---|---|
| I0 | 38 | 205 | 49 | WP-I0-101 → WP-I0-900 → WP-I0-104 → WP-I0-103 → WP-I0-001 → WP-I0-002 → WP-I0-004 → WP-I0-999 |
| I1 | 31 | 138 | 27 | WP-I1-101 → WP-I1-102 → WP-I1-002 → WP-I1-006 → WP-I1-999 |
| I2 | 35 | 198 | 62 | WP-I2-101 → WP-I2-021 → WP-I2-022 → WP-I2-001 → WP-I2-012 → WP-I2-011 → WP-I2-015 → WP-I2-999 |
| I3 | 16 | 104 | 24 | WP-I3-201 → WP-I3-005 → WP-I3-006 → WP-I3-999 |
| I4 | 13 | 81 | 44 | WP-I4-101 → WP-I4-202 → WP-I4-006 → WP-I4-007 → WP-I4-004 → WP-I4-999 |
| I5 | 13 | 79 | 22 | WP-I5-201 → WP-I5-008 → WP-I5-009 → WP-I5-999 |
| I6 | 22 | 125 | 37 | WP-I6-004 → WP-I6-005 → WP-I6-006 → WP-I6-007 → WP-I6-008 → WP-I6-999 |
| I7 | 12 | 56 | 12 | WP-I7-101 → WP-I7-999 |

## 4. Arbeitspakete im Detail

## 4.1 Inkrement I0

### WP-I0-001 – Schnitt 1: Anmeldung über Keycloak → JIT-Benutzer → Landing/leere Shell

| Merkmal | Wert |
|---|---|
| Inkrement | I0 |
| Typ (DoD 15 §3.15.3) | V – Vertikaler Schnitt |
| Größe | L |
| parallelisierbar | nein |
| Abhängigkeiten | WP-I0-103, WP-I0-105, WP-I0-108, WP-I0-203, WP-I0-204 |
| CE-IDs | CE-AUTH-001, CE-AUTH-012, CE-AUTH-014, CE-AUTH-016, CE-AUTH-022, CE-AUTH-023, CE-AUTH-024, CE-AUTH-025, CE-AUTH-027, CE-AUTH-029 |

**Ziel.** Ein Testbenutzer meldet sich per Authorization Code + PKCE über das BFF an; funk. legt beim ersten Login den Benutzer aus den Claims an (nur bei `email_verified`), setzt die HttpOnly-Session `funk-session`, beantwortet `GET /api/users/me/` und leitet nach `next_path` bzw. zur Workspace-Anlage weiter. Abmelden (RP-initiated + Back-Channel), Session-Ablauf, Sperre deaktivierter Konten und Auth-Fehlerbanner verhalten sich wie in 05 festgelegt.

**Enthaltene CE-IDs**

| CE-ID | Feature | Status (15 Anh. B) | Inkrement laut 15 | Pflicht-Ebenen | Testprojekt | E2E-Spec |
|---|---|---|---|---|---|---|
| CE-AUTH-001 | Sign-in-Seite | angepasst | I0/I1 | L1 L2 L3 L6 L7 L8 | Funk.Identity.Tests | `web/auth/keycloak-login.spec.ts` |
| CE-AUTH-012 | Profil- und Avatar-Übernahme vom Identity-Provider | angepasst | I0/I1 | L1 L2 L3 L6 L7 L8 | Funk.Identity.Tests | `web/auth/keycloak-login.spec.ts` |
| CE-AUTH-014 | Auth-Fehlercodes als Banner | angepasst | I0/I1 | L1 L2 L3 L5 L6 L7 L8 | Funk.Identity.Tests | `web/auth/keycloak-login.spec.ts` |
| CE-AUTH-016 | CSRF-Fehlerseite | übernommen | I0/I1 | L1 L2 L3 L6 L7 L8 | Funk.Identity.Tests | `web/auth/keycloak-login.spec.ts` |
| CE-AUTH-022 | Abmelden | angepasst | I0/I1 | L1 L2 L3 L6 L7 L8 | Funk.Identity.Tests | `web/auth/keycloak-login.spec.ts` |
| CE-AUTH-023 | Session-Ablauf | angepasst | I0/I1 | L1 L2 L3 L6 L7 L8 | Funk.Identity.Tests | `web/auth/keycloak-login.spec.ts` |
| CE-AUTH-024 | Sessions und Cookies | angepasst | I0/I1 | L1 L2 L3 L6 L7 L8 L9 (LT-13) | Funk.Identity.Tests | `web/auth/keycloak-login.spec.ts` |
| CE-AUTH-025 | Session-Status-Abfrage | angepasst | I0/I1 | L1 L2 L3 L5 L6 L7 L8 | Funk.Identity.Tests | `web/auth/keycloak-login.spec.ts` |
| CE-AUTH-027 | Login-Sperre deaktivierter Konten | angepasst | I0/I1 | L1 L2 L3 L6 L7 L8 | Funk.Identity.Tests | `web/auth/keycloak-login.spec.ts` |
| CE-AUTH-029 | Weiterleitung nach dem Login | angepasst | I0/I1 | L1 L2 L3 L6 L7 L8 | Funk.Identity.Tests | `web/auth/keycloak-login.spec.ts` |

**Betroffene Module/Libs in `funk.`**

- Backend: `src/modules/Identity/Funk.Identity` (OIDC-Schemata `oidc-web`/`oidc-admin`/`oidc-space`, `OidcBffEndpoints`, `PostgresTicketStore`, `SessionRevalidator`, `BackChannelLogoutEndpoint`)
- Backend: `src/modules/Identity/Funk.Identity.Contracts`
- Backend: `src/data/Funk.Data/Entities/Identity/` (`users`, `user_identities`, `user_sessions`)
- Backend: `tests/modules/Funk.Identity.Tests`
- Frontend: `frontend/libs/web/auth` (Landing, Sign-out, Fehlerbanner)
- Frontend: `frontend/libs/web/core/wrappers/authentication-wrapper.component.ts`
- Frontend: `frontend/apps/web/src/pages/(all)/…` (Sign-in-Einstieg)

**Referenzdokumente**

- Architektur: 05 §3.2–§3.7, §3.10, §4.1–§4.3, §5.1–§5.6, §5.10
- Architektur: 04 §4.1
- Architektur: 03 §3.4.1
- Architektur: 08 §3.3.4, §5.6
- Architektur: 17 ABG-020, ABG-021, Z-03 (max_age)
- Analyse/Feature: `analysis/08-frontend-web-architektur.md` §3.2
- Analyse/Feature: `analysis/10a-frontend-workspace-projekt-navigation.md` §2.14, §3.1
- Analyse/Feature: `analysis/06-auth-sicherheit-querschnitt.md` §3.2, §2.4, §3.14, §3.9, §2.2, §3.17, §3.1
- Analyse/Feature: `analysis/13b-shared-packages-i18n.md` §3.10, §2.4
- Analyse/Feature: `analysis/01-gesamtarchitektur-infrastruktur.md` §2.16
- Analyse/Feature: `analysis/02a-datenmodell-kern.md` §3.9
- Analyse/Feature: `analysis/07-hintergrundjobs-mail-storage-webhooks.md` §3.18
- Analyse/Feature: `analysis/03-api-intern-workspace-projekt-user.md` §3.6
- Feature-Katalog: `features/10-ce-feature-katalog.md` (Einträge CE-AUTH-001, CE-AUTH-012, CE-AUTH-014, CE-AUTH-016, CE-AUTH-022, CE-AUTH-023, CE-AUTH-024, CE-AUTH-025, CE-AUTH-027, CE-AUTH-029)

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- Backend: `apps/api/plane/authentication/views/app/check.py`, `apps/api/plane/authentication/views/space/check.py`, `apps/api/plane/authentication/views/app/email.py`, `apps/api/plane/authentication/provider/credentials/email.py`, `apps/api/plane/authentication/adapter/base.py`, `apps/api/plane/utils/url_security.py`, `apps/api/plane/utils/instance_config_variables/core.py`, `apps/api/plane/authentication/views/common.py`, `apps/api/templates/csrf_failure.html`, `apps/api/plane/authentication/views/app/signout.py`, `apps/api/plane/authentication/views/space/signout.py`, `apps/api/plane/license/api/views/admin.py`, `apps/api/plane/authentication/middleware/session.py`, `apps/api/plane/authentication/session.py`, `apps/api/plane/db/models/session.py`, `apps/api/plane/settings/common.py`, `apps/api/plane/authentication/utils/login.py`, `apps/api/plane/app/views/user/base.py`, `apps/api/plane/db/management/commands/activate_user.py`, `apps/api/plane/bgtasks/user_activation_email_task.py`, `apps/api/plane/bgtasks/user_deactivation_email_task.py`, `apps/api/plane/utils/path_validator.py`, `apps/api/plane/authentication/utils/redirection_path.py`, `apps/api/plane/authentication/utils/host.py`, `apps/api/plane/app/serializers/user.py`
- Frontend: `apps/web/app/(home)/page.tsx`, `apps/web/components/auth-screens/auth-base.tsx`, `apps/web/components/account/auth-forms/password.tsx`, `apps/web/components/account/auth-forms/unique-code.tsx`, `apps/web/hooks/oauth/core.tsx`, `apps/web/components/account/auth-forms/auth-root.tsx`, `apps/web/components/account/auth-forms/form-root.tsx`, `apps/web/components/account/auth-forms/email.tsx`, `apps/web/components/account/auth-forms/auth-header.tsx`, `apps/web/components/auth-screens/header.tsx`, `apps/web/services/auth.service.ts`, `apps/web/helpers/authentication.helper.tsx`, `packages/utils/src/auth.ts`, `packages/constants/src/auth/index.ts`, `packages/services/src/auth/auth.service.ts`, `packages/services/src/auth/sites-auth.service.ts`, `apps/web/store/user/index.ts`, `apps/web/services/api.service.ts`, `apps/web/store/root.store.ts`, `packages/utils/src/get-icon-for-link.ts`, `packages/utils/src/url.ts`, `packages/utils/src/tlds.ts`

**Endpunkte (Katalog 04, `architecture/_data/endpoints.json`; 13 registriert)**

| EP | Methode | Pfad | Oberfläche | Handler | Permission | Inkr. 04 | CE-IDs |
|---|---|---|---|---|---|---|---|
| EP-0001 | GET | `/auth/get-csrf-token/` | Auth | AntiforgeryEndpoints.GetCsrfToken | (anonym) | I0 | CE-AUTH-016, CE-AUTH-024 |
| EP-0002 | POST | `/auth/oidc/backchannel-logout/` | Auth | BackChannelLogoutEndpoint.Handle | (Logout-Token) | I0 | CE-AUTH-022, CE-AUTH-023, CE-AUTH-027 |
| EP-0017 | GET | `/auth/oidc/callback/` | Auth | OidcBffEndpoints.Callback (OIDC-Handler) | (anonym) | I0 | CE-AUTH-012, CE-AUTH-014, CE-AUTH-024, CE-AUTH-027, CE-AUTH-028, CE-AUTH-029 |
| EP-0018 | GET | `/auth/oidc/login/` | Auth | OidcBffEndpoints.Login | (anonym) | I0 | CE-AUTH-001, CE-AUTH-029, CE-SPACE-014 |
| EP-0019 | GET | `/auth/oidc/signed-out/` | Auth | OidcBffEndpoints.SignedOut | (anonym) | I0 | CE-AUTH-022 |
| EP-0023 | POST | `/auth/sign-out/` | Auth | OidcBffEndpoints.SignOut(app=web) | (anonym) | I0 | CE-AUTH-022 |
| EP-0040 | POST | `/auth/spaces/sign-out/` | Auth | OidcBffEndpoints.SignOut(app=space) | (anonym) | I0 | CE-AUTH-022 |
| EP-0047 | GET | `/api/users/last-visited-workspace/` | App | CurrentUserEndpoints.GetLastVisitedWorkspaceQuery | user.user.read | I0 | CE-AUTH-029 |
| EP-0048 | GET | `/api/users/me/` | App | CurrentUserEndpoints.GetCurrentUserQuery | user.user.read | I0 | CE-PROF-001, CE-AUTH-025 |
| EP-0049 (vorab) | PATCH | `/api/users/me/` | App | CurrentUserEndpoints.UpdateCurrentUserCommand | user.user.update | I0 | CE-PROF-003 |
| EP-0052 (vorab) | PATCH | `/api/users/me/onboard/` | App | CurrentUserEndpoints.UpdateOnboardingStatusCommand | user.user.update | I0 | CE-AUTH-030 |
| EP-0053 | GET | `/api/users/me/settings/` | App | CurrentUserEndpoints.GetCurrentUserSettingsQuery | user.user.read | I0 | CE-PROF-001, CE-AUTH-029 |
| EP-0056 | GET | `/api/users/session/` | App | SessionEndpoints.GetSessionStatusQuery | user.session.read | I0 | CE-AUTH-025 |

**Akzeptanzkriterien**

1. `OidcLoginFlowTests` (L6) für web: Login mit PKCE, Cookie `funk-session` HttpOnly/SameSite, RP-Logout, Back-Channel-Logout beendet die Session < 2 s, Sperre in Keycloak verhindert den nächsten Request.
2. JIT legt den Benutzer mit `sub`-Verknüpfung an und verweigert `email_verified=false` mit Fehlercode-Banner (CE-AUTH-014, neue Codes aus 05 §4.3).
3. `next_path`-Validierung 1:1 zu `path_validator.py` (Same-Origin-Pfad inkl. Query, kein Schema/Host).
4. E2E `web/auth/keycloak-login.spec.ts` grün gegen Original (Sign-in-Flow des Originals) und funk. (Keycloak-Flow) mit den Pflichtszenarien 15 §3.9.3.
5. Contract: je Endpunkt dieses Pakets ≥ 1 Szenario mit Golden vom Original (Erfolg, Berechtigungsfehler, Validierungsfehler); Replay grün (L5).
6. Permission-Matrix (05 Anhang B) für alle Endpunkte dieses Pakets als L3-Test grün; Tenant-Isolation geprüft.
7. Signal-Stores strukturgleich zum MobX-Original (`store-parity-check`), Vitest je Action (L2).
8. E2E-Specs dieses Pakets grün gegen Original **und** funk. (Dual-Target, Pflichtszenarien 15 §3.9.3).
9. Visual-/DOM-/a11y-Prüfpunkte der betroffenen Screens (09 §4.14, 15 §3.10.2) innerhalb der Schwellwerte 15 §3.10.3 (Chromium); i18n-Schlüssel nur aus den Original-Locales (de/en).
10. `ce-coverage-check --ids CE-AUTH-001,CE-AUTH-012,CE-AUTH-014,CE-AUTH-016,CE-AUTH-022,CE-AUTH-023,CE-AUTH-024,CE-AUTH-025,CE-AUTH-027,CE-AUTH-029` grün (Mindestebenen 15 Anhang B).

**Testumfang**

- Pflicht-Ebenen (aus 15 Anhang B): L1, L2, L3, L5, L6, L7, L8, L9
- Testprojekte: `Funk.Identity.Tests`
- E2E-Specs (`frontend/apps/e2e/`): `web/auth/keycloak-login.spec.ts`
- L3 Identity (Provisionierung, Ticket-Store, Revalidierung), L6 `OidcLoginFlowTests`, L7 `keycloak-login.spec.ts`, L5 Contract für `/api/users/me/`, `/auth/get-csrf-token/`.

### WP-I0-002 – Schnitt 2: Workspace anlegen (Formular, Slug-Prüfung, Admin-Mitgliedschaft)

| Merkmal | Wert |
|---|---|
| Inkrement | I0 |
| Typ (DoD 15 §3.15.3) | V – Vertikaler Schnitt |
| Größe | M |
| parallelisierbar | nein |
| Abhängigkeiten | WP-I0-001, WP-I0-201, WP-I0-202, WP-I0-203 |
| CE-IDs | CE-WS-001 |

**Ziel.** `/create-workspace` legt mit Name, Slug (Regex, Länge, reservierte Slugs, global eindeutig, 409) und Organisationsgröße einen Workspace mit Admin-Mitgliedschaft (Rolle 20) an und schreibt das erste produktive Integration-Event `funk.workspace.created.v1`. Der Demo-Seed folgt schrittweise und wird in WP-I4-009 abgenommen.

**Enthaltene CE-IDs**

| CE-ID | Feature | Status (15 Anh. B) | Inkrement laut 15 | Pflicht-Ebenen | Testprojekt | E2E-Spec |
|---|---|---|---|---|---|---|
| CE-WS-001 | Workspace anlegen | übernommen | I0/I1 | L1 L2 L3 L5 L7 L8 | Funk.Workspaces.Tests | `web/workspace/create-workspace.spec.ts` |

**Betroffene Module/Libs in `funk.`**

- Backend: `src/modules/Workspaces/Funk.Workspaces` (`CreateWorkspaceCommand`, `WorkspaceAvailabilityQuery`)
- Backend: `src/data/Funk.Data/Entities/Workspaces/`
- Backend: `tests/modules/Funk.Workspaces.Tests`
- Frontend: `frontend/libs/web/workspace` (create-workspace-form)
- Frontend: `frontend/apps/web/src/pages/(all)/create-workspace/`

**Referenzdokumente**

- Architektur: 04 §4.3
- Architektur: 03 §3.4.3
- Architektur: 02 §3.5.3 (Slug-Regeln), §3.7
- Architektur: 06 §3.8 (Event-Katalog)
- Analyse/Feature: `analysis/03-api-intern-workspace-projekt-user.md` §3.1
- Analyse/Feature: `analysis/02a-datenmodell-kern.md` §3.14
- Analyse/Feature: `analysis/08-frontend-web-architektur.md` §2.2
- Analyse/Feature: `analysis/10a-frontend-workspace-projekt-navigation.md` §2.15
- Analyse/Feature: `analysis/13b-shared-packages-i18n.md` §3.10
- Analyse/Feature: `analysis/06-auth-sicherheit-querschnitt.md` §2.13
- Feature-Katalog: `features/10-ce-feature-katalog.md` (Einträge CE-WS-001)

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- Backend: `apps/api/plane/app/urls/workspace.py`, `apps/api/plane/app/views/workspace/base.py`, `apps/api/plane/app/serializers/workspace.py`, `apps/api/plane/utils/constants.py`, `apps/api/plane/bgtasks/workspace_seed_task.py`, `apps/api/plane/db/models/workspace.py`, `apps/api/plane/utils/url.py`, `apps/api/plane/utils/content_validator.py`
- Frontend: `apps/web/services/workspace.service.ts`, `packages/constants/src/workspace.ts`, `apps/web/components/workspace/create-workspace-form.tsx`, `apps/web/app/(all)/create-workspace/page.tsx`, `packages/utils/src/validation.ts`, `packages/services/src/workspace/workspace.service.ts`, `packages/services/src/workspace/instance-workspace.service.ts`

**Endpunkte (Katalog 04, `architecture/_data/endpoints.json`; 3 registriert)**

| EP | Methode | Pfad | Oberfläche | Handler | Permission | Inkr. 04 | CE-IDs |
|---|---|---|---|---|---|---|---|
| EP-0122 | GET | `/api/workspace-slug-check/` | App | WorkspaceEndpoints.CheckWorkspaceSlugQuery | user.workspace.create | I0 | CE-WS-001 |
| EP-0123 | POST | `/api/workspaces/` | App | WorkspaceEndpoints.CreateWorkspaceCommand | user.workspace.create | I0 | CE-WS-001, CE-WS-002, CE-INST-028 |
| EP-0124 (vorab) | GET | `/api/workspaces/{slug}/` | App | WorkspaceEndpoints.GetWorkspaceQuery | workspace.settings.read | I0 | CE-WS-003 |

**Akzeptanzkriterien**

1. Slug-Validierung (Regex `^[a-zA-Z0-9_-]+$`, max. 48, reservierte Slugs inkl. `RESTRICTED_URLS`) liefert dieselben Feldfehler wie das Original (Contract-Golden).
2. `DISABLE_WORKSPACE_CREATION` (Instanz-Konfiguration) blendet den Original-Hinweis ein.
3. Outbox enthält genau ein `funk.workspace.created.v1` je Anlage (Event-Katalog-Snapshot).
4. Contract: je Endpunkt dieses Pakets ≥ 1 Szenario mit Golden vom Original (Erfolg, Berechtigungsfehler, Validierungsfehler); Replay grün (L5).
5. Permission-Matrix (05 Anhang B) für alle Endpunkte dieses Pakets als L3-Test grün; Tenant-Isolation geprüft.
6. Signal-Stores strukturgleich zum MobX-Original (`store-parity-check`), Vitest je Action (L2).
7. E2E-Specs dieses Pakets grün gegen Original **und** funk. (Dual-Target, Pflichtszenarien 15 §3.9.3).
8. Visual-/DOM-/a11y-Prüfpunkte der betroffenen Screens (09 §4.14, 15 §3.10.2) innerhalb der Schwellwerte 15 §3.10.3 (Chromium); i18n-Schlüssel nur aus den Original-Locales (de/en).
9. `ce-coverage-check --ids CE-WS-001` grün (Mindestebenen 15 Anhang B).

**Testumfang**

- Pflicht-Ebenen (aus 15 Anhang B): L1, L2, L3, L5, L7, L8
- Testprojekte: `Funk.Workspaces.Tests`
- E2E-Specs (`frontend/apps/e2e/`): `web/workspace/create-workspace.spec.ts`
- L3 Workspaces (E1–E8), L5 Contract `POST /api/workspaces/`, `GET /api/workspace-slug-check/`, L7 `create-workspace.spec.ts` (Abschnitt Anlage), L8 Visual Create-Workspace.

### WP-I0-003 – Instanz-Bootstrap: Konfiguration, Instanz-Info, Erst-Einrichtung, God-Mode-Einstieg (inkl. Nachweis entfallener Admin-Logins)

| Merkmal | Wert |
|---|---|
| Inkrement | I0 |
| Typ (DoD 15 §3.15.3) | V – Vertikaler Schnitt |
| Größe | M |
| parallelisierbar | ja |
| Abhängigkeiten | WP-I0-001, WP-I0-208 |
| CE-IDs | CE-INST-001, CE-INST-002, CE-INST-003, CE-INST-004, CE-INST-005, CE-INST-006, CE-INST-007, CE-INST-020, CE-INST-021, CE-INST-022, CE-INST-023, CE-INST-024 |

**Ziel.** Instanz-Konfiguration aus ENV und DB (verschlüsselte Keys, 14 Keys), `GET /api/instances/` mit festen Werten der entfallenen Login-Flags, Instanz-Zustände in der Web-App, Erst-Einrichtung ohne Admin-Konto und der God-Mode-Einstieg über die Keycloak-Rolle `funk-instance-admin` (`NO_ADMIN_ROLE`, Seite `general` lauffähig, ABG-024). Admin-Login und Provider-Konfiguration entfallen (ADR-008) und sind mit `OidcLoginFlowTests.InstanceAdminRole_GrantsGodMode` belegt.

**Enthaltene CE-IDs**

| CE-ID | Feature | Status (15 Anh. B) | Inkrement laut 15 | Pflicht-Ebenen | Testprojekt | E2E-Spec |
|---|---|---|---|---|---|---|
| CE-INST-001 | Instanz-Registrierung und Versionsprüfung | angepasst | I0/I6 | L1 L2 L3 L5 L7 L8 | Funk.Instance.Tests | `admin/instance-setup.spec.ts` |
| CE-INST-002 | Instanz-Konfiguration aus ENV und DB | übernommen | I0/I6 | L1 L2 L3 L5 L7 L8 | Funk.Instance.Tests | `admin/instance-setup.spec.ts` |
| CE-INST-003 | Instanz-Info und öffentliche Konfiguration | übernommen | I0/I6 | L1 L2 L3 L5 L7 L8 | Funk.Instance.Tests | `admin/instance-setup.spec.ts` |
| CE-INST-004 | Instanz-Admins verwalten (nur API) | angepasst | I0/I6 | L1 L2 L3 L5 L7 L8 | Funk.Instance.Tests | `admin/instance-setup.spec.ts` |
| CE-INST-005 | Instanz-Zustände in der Web-App | übernommen | I0/I6 | L1 L2 L3 L5 L7 L8 | Funk.Instance.Tests | `admin/instance-setup.spec.ts` |
| CE-INST-006 | Erst-Einrichtung der Instanz | angepasst | I0/I6 | L1 L2 L3 L5 L6 L7 L8 | Funk.Instance.Tests | `admin/instance-setup.spec.ts` |
| CE-INST-007 | Admin-Anmeldung | entfällt – Ersatz: `OidcLoginFlowTests.InstanceAdminRole_GrantsGodMode` (L6), `KeycloakRealmConfigTests` (L3) | – | – | – | – |
| CE-INST-020 | Authentifizierungsmethoden-Übersicht | entfällt – Ersatz: `OidcLoginFlowTests.InstanceAdminRole_GrantsGodMode` (L6), `KeycloakRealmConfigTests` (L3) | – | – | – | – |
| CE-INST-021 | Google-OAuth-Konfiguration | entfällt – Ersatz: `OidcLoginFlowTests.InstanceAdminRole_GrantsGodMode` (L6), `KeycloakRealmConfigTests` (L3) | – | – | – | – |
| CE-INST-022 | GitHub-OAuth-Konfiguration | entfällt – Ersatz: `OidcLoginFlowTests.InstanceAdminRole_GrantsGodMode` (L6), `KeycloakRealmConfigTests` (L3) | – | – | – | – |
| CE-INST-023 | GitLab-OAuth-Konfiguration | entfällt – Ersatz: `OidcLoginFlowTests.InstanceAdminRole_GrantsGodMode` (L6), `KeycloakRealmConfigTests` (L3) | – | – | – | – |
| CE-INST-024 | Gitea-OAuth-Konfiguration | entfällt – Ersatz: `OidcLoginFlowTests.InstanceAdminRole_GrantsGodMode` (L6), `KeycloakRealmConfigTests` (L3) | – | – | – | – |

**Betroffene Module/Libs in `funk.`**

- Backend: `src/modules/Instance/Funk.Instance` (`InstanceConfigurationStore`, `InstanceBootstrap`)
- Backend: `src/modules/Instance/Funk.Instance.Contracts`
- Backend: `src/hosts/Funk.Migrator` (InstanceBootstrap-Schritt)
- Backend: `tests/modules/Funk.Instance.Tests`
- Frontend: `frontend/libs/admin/core`, `frontend/libs/admin/instance`
- Frontend: `frontend/apps/admin/src/pages/` (Einstieg, Setup, `general`)
- Frontend: `frontend/libs/admin/extensions` (Gerüst `ADMIN_SETTINGS_PAGES`)

**Referenzdokumente**

- Architektur: 05 §3.8, §3.9, §4.4
- Architektur: 02 §3.16
- Architektur: 04 §4.2
- Architektur: 03 §3.4.2
- Architektur: 08 §4.2
- Architektur: 17 ABG-024, ABG-143
- Analyse/Feature: `analysis/01-gesamtarchitektur-infrastruktur.md` §3.1, §3.2
- Analyse/Feature: `analysis/05-api-public-v1-space-instanz.md` §2.7, §3.24, §3.21, §3.22, §3.23
- Analyse/Feature: `analysis/02a-datenmodell-kern.md` §3.16
- Analyse/Feature: `analysis/13b-shared-packages-i18n.md` §2.7
- Analyse/Feature: `analysis/06-auth-sicherheit-querschnitt.md` §3.12
- Analyse/Feature: `analysis/10a-frontend-workspace-projekt-navigation.md` §2.16
- Analyse/Feature: `analysis/08-frontend-web-architektur.md` §2.12
- Analyse/Feature: `analysis/11-frontend-admin-space.md` §3.2, §3.3, §3.9, §3.10
- Feature-Katalog: `features/10-ce-feature-katalog.md` (Einträge CE-INST-001, CE-INST-002, CE-INST-003, CE-INST-004, CE-INST-005, CE-INST-006, CE-INST-007, CE-INST-020, CE-INST-021, CE-INST-022, CE-INST-023, CE-INST-024)

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- Backend: `apps/api/plane/license/management/commands/register_instance.py`, `apps/api/bin/docker-entrypoint-api.sh`, `apps/api/plane/license/management/commands/configure_instance.py`, `apps/api/plane/utils/instance_config_variables/core.py`, `apps/api/plane/license/utils/instance_value.py`, `apps/api/plane/license/utils/encryption.py`, `apps/api/plane/license/api/views/instance.py`, `apps/api/plane/license/api/views/configuration.py`, `apps/api/plane/license/models/instance.py`, `apps/api/plane/license/api/views/admin.py`, `apps/api/plane/license/api/serializers/instance.py`, `apps/api/plane/license/api/serializers/admin.py`, `apps/api/plane/utils/cache.py`, `apps/api/plane/authentication/utils/password.py`, `apps/api/plane/authentication/rate_limit.py`, `apps/api/plane/authentication/middleware/session.py`, `apps/api/plane/authentication/utils/login.py`, `apps/api/plane/license/api/permissions/instance.py`
- Frontend: `packages/services/src/instance/instance.service.ts`, `packages/services/src/workspace/instance-workspace.service.ts`, `packages/types/src/instance/base.ts`, `packages/types/src/instance/auth.ts`, `apps/web/components/instance/not-ready-view.tsx`, `apps/web/components/instance/maintenance-view.tsx`, `apps/web/components/instance/maintenance-message.tsx`, `apps/web/app/not-found.tsx`, `apps/web/app/error/dev.tsx`, `apps/web/app/error/prod.tsx`, `apps/web/layouts/auth-layout/workspace-wrapper.tsx`, `apps/web/components/auth-screens/not-authorized-view.tsx`, `apps/admin/components/instance/setup-form.tsx`, `apps/admin/app/(all)/(home)/page.tsx`, `apps/admin/components/common/password-strength-indicator.tsx`, `apps/admin/app/(all)/(home)/sign-in-form.tsx`, `apps/admin/app/(all)/(home)/auth-helpers.tsx`, `apps/admin/app/(all)/(home)/auth-banner.tsx`, `apps/admin/app/(all)/(dashboard)/authentication/page.tsx`, `apps/admin/hooks/oauth/core.tsx`, `apps/admin/components/authentication/authentication-method-card.tsx`, `apps/admin/helpers/authentication.ts`, `apps/admin/components/authentication/email-config-switch.tsx`, `apps/admin/components/authentication/password-config-switch.tsx`, `apps/admin/app/(all)/(dashboard)/authentication/google/page.tsx`, `apps/admin/app/(all)/(dashboard)/authentication/google/form.tsx`, `apps/admin/components/authentication/google-config.tsx`, `apps/admin/app/(all)/(dashboard)/authentication/github/page.tsx`, `apps/admin/app/(all)/(dashboard)/authentication/github/form.tsx`, `apps/admin/components/authentication/github-config.tsx`, `apps/admin/app/(all)/(dashboard)/authentication/gitlab/page.tsx`, `apps/admin/app/(all)/(dashboard)/authentication/gitlab/form.tsx`, `apps/admin/components/authentication/gitlab-config.tsx`, `apps/admin/app/(all)/(dashboard)/authentication/gitea/page.tsx`, `apps/admin/app/(all)/(dashboard)/authentication/gitea/form.tsx`, `apps/admin/components/authentication/gitea-config.tsx`

**Endpunkte (Katalog 04, `architecture/_data/endpoints.json`; 7 registriert)**

| EP | Methode | Pfad | Oberfläche | Handler | Permission | Inkr. 04 | CE-IDs |
|---|---|---|---|---|---|---|---|
| EP-0051 | GET | `/api/users/me/instance-admin/` | App | CurrentUserEndpoints.GetInstanceAdminFlagQuery | user.user.read | I0 | CE-INST-005 |
| EP-0070 | GET | `/api/instances/admins/` | Instance | InstanceAdminEndpoints.ListInstanceAdminsQuery | instance.admin.read | I0 | CE-INST-004 |
| EP-0071 (vorab) | GET | `/api/instances/admins/me/` | Instance | InstanceAdminEndpoints.GetCurrentInstanceAdminQuery | instance.admin.read | I0 | CE-INST-010 |
| EP-0072 (vorab) | GET | `/api/instances/admins/session/` | Instance | InstanceAdminEndpoints.GetInstanceAdminSessionQuery | instance.session.read | I0 | CE-INST-010 |
| EP-0077 | GET | `/api/instances/` | Instance | InstanceEndpoints.GetInstanceInfoQuery | instance.settings.read | I0 | CE-INST-003, CE-INST-001, CE-AUTH-013, CE-INST-028 |
| EP-0079 | POST | `/api/instances/admins/setup/` | Instance | InstanceEndpoints.CompleteInstanceSetupCommand | instance.settings.update | I0 | CE-INST-006 |
| EP-0083 (vorab) | POST | `/api/instances/admins/sign-out/` | Instance | OidcBffEndpoints.OidcBffEndpoints.SignOut(app=admin) | — | I0 | CE-INST-008 |

**Akzeptanzkriterien**

1. `GET /api/instances/` entspricht dem Original-Golden bis auf die dokumentierten `config`-Abweichungen (DEV-API-02).
2. Instanz-Admin ergibt sich ausschließlich aus der Rolle `funk-instance-admin`; ein Benutzer ohne Rolle sieht `NO_ADMIN_ROLE` (Visual wie Original-Fehlerseite).
3. Erst-Einrichtung ohne Passwortfelder (DEV-UI-06); `admin/instance-setup.spec.ts` Abschnitt `@I0` grün.
4. Instanz-Secrets werden im God Mode maskiert (`MaskInstanceSecrets = true`, Z-112).
5. Contract: je Endpunkt dieses Pakets ≥ 1 Szenario mit Golden vom Original (Erfolg, Berechtigungsfehler, Validierungsfehler); Replay grün (L5).
6. Permission-Matrix (05 Anhang B) für alle Endpunkte dieses Pakets als L3-Test grün; Tenant-Isolation geprüft.
7. Signal-Stores strukturgleich zum MobX-Original (`store-parity-check`), Vitest je Action (L2).
8. E2E-Specs dieses Pakets grün gegen Original **und** funk. (Dual-Target, Pflichtszenarien 15 §3.9.3).
9. Visual-/DOM-/a11y-Prüfpunkte der betroffenen Screens (09 §4.14, 15 §3.10.2) innerhalb der Schwellwerte 15 §3.10.3 (Chromium); i18n-Schlüssel nur aus den Original-Locales (de/en).
10. `ce-coverage-check --ids CE-INST-001,CE-INST-002,CE-INST-003,CE-INST-004,CE-INST-005,CE-INST-006,CE-INST-007,CE-INST-020,CE-INST-021,CE-INST-022,CE-INST-023,CE-INST-024` grün (Mindestebenen 15 Anhang B).

**Testumfang**

- Pflicht-Ebenen (aus 15 Anhang B): L1, L2, L3, L5, L6, L7, L8
- Testprojekte: `Funk.Instance.Tests`
- E2E-Specs (`frontend/apps/e2e/`): `admin/instance-setup.spec.ts`
- L3 Instance, L5 Contract `/api/instances/`, L6 `InstanceAdminRole_GrantsGodMode`, L7 `admin/instance-setup.spec.ts` (`@I0`).

### WP-I0-004 – Schnitt: Workspace-Shell 1:1 (Top-Navigation, Sidebar, Header, Workspace-Switcher, User-Menü)

| Merkmal | Wert |
|---|---|
| Inkrement | I0 |
| Typ (DoD 15 §3.15.3) | V – Vertikaler Schnitt |
| Größe | L |
| parallelisierbar | nein |
| Abhängigkeiten | WP-I0-002, WP-I0-006, WP-I0-208 |
| CE-IDs | CE-WS-005, CE-WS-013, CE-WS-016, CE-WS-018, CE-WS-019, CE-WS-020 |

**Ziel.** Die Workspace-Shell (App-Rail/Top-Navigation, resizable Sidebar mit Peek, Sidebar-Kopf mit Quick-Action, Menüeinträge, Workspace-Switcher mit Liste, User-Menü) ist pixel- und DOM-gleich zum Original; nur Einträge abgenommener Funktionen sind sichtbar (01 §7.19).

**Enthaltene CE-IDs**

| CE-ID | Feature | Status (15 Anh. B) | Inkrement laut 15 | Pflicht-Ebenen | Testprojekt | E2E-Spec |
|---|---|---|---|---|---|---|
| CE-WS-005 | Workspace-Switcher und Workspace-Liste | übernommen | I0/I1 | L1 L2 L3 L5 L7 L8 | Funk.Workspaces.Tests | `web/workspace/workspace-shell.spec.ts` |
| CE-WS-013 | Workspace-Shell und Top-Navigation | übernommen | I0/I1 | L2 L7 L8 | Frontend-only | `web/workspace/workspace-shell.spec.ts` |
| CE-WS-016 | User-Menü | übernommen | I0/I1 | L2 L7 L8 | Frontend-only | `web/workspace/workspace-shell.spec.ts` |
| CE-WS-018 | Resizable App-Sidebar mit Peek | übernommen | I0/I1 | L2 L7 L8 | Frontend-only | `web/workspace/workspace-shell.spec.ts` |
| CE-WS-019 | Sidebar-Kopf und Quick-Action 'New work item' | übernommen | I0/I1 | L2 L7 L8 | Frontend-only | `web/workspace/workspace-shell.spec.ts` |
| CE-WS-020 | Sidebar-Menüeinträge | übernommen | I0/I1 | L2 L7 L8 | Frontend-only | `web/workspace/workspace-shell.spec.ts` |

**Betroffene Module/Libs in `funk.`**

- Backend: `src/modules/Workspaces/Funk.Workspaces` (`GET /api/users/me/workspaces/`, Sidebar-Präferenzen)
- Frontend: `frontend/libs/web/core/{sidebar,navigation,breadcrumbs}`
- Frontend: `frontend/libs/web/workspace` (Switcher)
- Frontend: `frontend/libs/web/extensions` (`SIDEBAR_ITEMS` statisch)

**Referenzdokumente**

- Architektur: 08 §4.4, §3.9
- Architektur: 09 §4.14 (Screenshot-Katalog Shell)
- Architektur: 16 §1.4 Zeile I0 (`SIDEBAR_ITEMS`, `APP_RAIL_ENABLED`)
- Analyse/Feature: `analysis/10a-frontend-workspace-projekt-navigation.md` §2.3, §2.2, §3.2
- Analyse/Feature: `analysis/03-api-intern-workspace-projekt-user.md` §2.5
- Analyse/Feature: `analysis/08-frontend-web-architektur.md` §3.3
- Analyse/Feature: `analysis/13b-shared-packages-i18n.md` §2.2
- Feature-Katalog: `features/10-ce-feature-katalog.md` (Einträge CE-WS-005, CE-WS-013, CE-WS-016, CE-WS-018, CE-WS-019, CE-WS-020)

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- Backend: `apps/api/plane/app/views/workspace/base.py`
- Frontend: `apps/web/components/workspace/sidebar/workspace-menu-root.tsx`, `apps/web/components/workspace/sidebar/dropdown-item.tsx`, `apps/web/components/workspace/logo.tsx`, `apps/web/services/workspace.service.ts`, `apps/web/components/navigation/top-navigation-root.tsx`, `apps/web/components/workspace/content-wrapper.tsx`, `apps/web/app/(all)/[workspaceSlug]/layout.tsx`, `apps/web/app/(all)/[workspaceSlug]/(projects)/star-us-link.tsx`, `apps/web/components/workspace/sidebar/user-menu-root.tsx`, `apps/web/components/common/modal/global.tsx`, `apps/web/components/sidebar/resizable-sidebar.tsx`, `apps/web/components/sidebar/sidebar-toggle-button.tsx`, `apps/web/app/(all)/[workspaceSlug]/(projects)/_sidebar.tsx`, `apps/web/store/theme.store.ts`, `apps/web/app/(all)/[workspaceSlug]/(projects)/sidebar.tsx`, `apps/web/components/workspace/sidebar`, `apps/web/components/sidebar/sidebar-wrapper.tsx`, `apps/web/components/workspace/sidebar/quick-actions.tsx`, `apps/web/components/sidebar/add-button.tsx`, `apps/web/components/workspace/sidebar/sidebar-menu-items.tsx`, `apps/web/components/workspace/sidebar/sidebar-item.tsx`, `apps/web/components/workspace/sidebar/helper.tsx`, `apps/web/components/sidebar/sidebar-navigation.tsx`, `packages/constants/src/workspace.ts`, `packages/types/src/navigation-preferences.ts`, `packages/constants/src/sidebar-favorites.ts`, `packages/services/src/user/favorite.service.ts`

**Endpunkte (Katalog 04, `architecture/_data/endpoints.json`; 2 registriert)**

| EP | Methode | Pfad | Oberfläche | Handler | Permission | Inkr. 04 | CE-IDs |
|---|---|---|---|---|---|---|---|
| EP-0055 | GET | `/api/users/me/workspaces/` | App | CurrentUserEndpoints.ListMyWorkspacesQuery | user.user.read | I0 | CE-WS-005 |
| EP-0138 (vorab) | GET | `/api/workspaces/{slug}/workspace-members/me/` | App | WorkspaceMemberEndpoints.GetMyWorkspaceMembershipQuery | workspace.member.read_own | I0 | CE-WS-012 |

**Akzeptanzkriterien**

1. Visual-Prüfpunkte der Shell (hell/dunkel, Sidebar ein-/ausgeklappt, Peek) ≤ 0,2 % Pixelabweichung (15 §3.10.3), DOM-Snapshot gleich.
2. Sidebar-Breite wird wie im Original in `localStorage` gehalten; Tastaturbedienung (Tab-Reihenfolge, Escape) wie Original.
3. Contract: je Endpunkt dieses Pakets ≥ 1 Szenario mit Golden vom Original (Erfolg, Berechtigungsfehler, Validierungsfehler); Replay grün (L5).
4. Permission-Matrix (05 Anhang B) für alle Endpunkte dieses Pakets als L3-Test grün; Tenant-Isolation geprüft.
5. Signal-Stores strukturgleich zum MobX-Original (`store-parity-check`), Vitest je Action (L2).
6. E2E-Specs dieses Pakets grün gegen Original **und** funk. (Dual-Target, Pflichtszenarien 15 §3.9.3).
7. Visual-/DOM-/a11y-Prüfpunkte der betroffenen Screens (09 §4.14, 15 §3.10.2) innerhalb der Schwellwerte 15 §3.10.3 (Chromium); i18n-Schlüssel nur aus den Original-Locales (de/en).
8. `ce-coverage-check --ids CE-WS-005,CE-WS-013,CE-WS-016,CE-WS-018,CE-WS-019,CE-WS-020` grün (Mindestebenen 15 Anhang B).

**Testumfang**

- Pflicht-Ebenen (aus 15 Anhang B): L1, L2, L3, L5, L7, L8
- Testprojekte: `Funk.Workspaces.Tests`, `Frontend-only`
- E2E-Specs (`frontend/apps/e2e/`): `web/workspace/workspace-shell.spec.ts`
- L2 Sidebar-/Switcher-Komponenten, L7 `workspace-shell.spec.ts` (Grundzustand), L8 Visual Shell.

### WP-I0-005 – Schnitt 3: Projekt anlegen (Identifier-Prüfung, Default-States, Mitgliedschaft)

| Merkmal | Wert |
|---|---|
| Inkrement | I0 |
| Typ (DoD 15 §3.15.3) | V – Vertikaler Schnitt |
| Größe | M |
| parallelisierbar | nein |
| Abhängigkeiten | WP-I0-002, WP-I0-006 |
| CE-IDs | CE-PRJ-004, CE-PRJ-005 |

**Ziel.** Das Create-Project-Modal legt ein Projekt mit Identifier-Prüfung (max. 12 Zeichen, Freigabe), Default-States und Admin-Mitgliedschaft an und schreibt `funk.project.created.v1`.

**Enthaltene CE-IDs**

| CE-ID | Feature | Status (15 Anh. B) | Inkrement laut 15 | Pflicht-Ebenen | Testprojekt | E2E-Spec |
|---|---|---|---|---|---|---|
| CE-PRJ-004 | Projekt anlegen | übernommen | I0/I1 | L1 L2 L3 L5 L7 L8 | Funk.Projects.Tests | `web/projects/create-project.spec.ts` |
| CE-PRJ-005 | Projekt-Identifier prüfen und freigeben | übernommen | I0/I1 | L1 L2 L3 L5 L7 L8 | Funk.Projects.Tests | `web/projects/create-project.spec.ts` |

**Betroffene Module/Libs in `funk.`**

- Backend: `src/modules/Projects/Funk.Projects` (`CreateProjectCommand`, Identifier-Endpunkte)
- Backend: `src/data/Funk.Data/Entities/Projects/`
- Backend: `tests/modules/Funk.Projects.Tests`
- Frontend: `frontend/libs/web/project` (create-project-modal)

**Referenzdokumente**

- Architektur: 04 §4.4
- Architektur: 03 §3.4.4
- Architektur: 02 §5.2 (Referenzmodul-Muster)
- Analyse/Feature: `analysis/10a-frontend-workspace-projekt-navigation.md` §2.12, §2.11
- Analyse/Feature: `analysis/03-api-intern-workspace-projekt-user.md` §3.5, §2.6
- Analyse/Feature: `analysis/02a-datenmodell-kern.md` §3.4
- Analyse/Feature: `analysis/06-auth-sicherheit-querschnitt.md` §2.13
- Feature-Katalog: `features/10-ce-feature-katalog.md` (Einträge CE-PRJ-004, CE-PRJ-005)

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- Backend: `apps/api/plane/app/views/project/base.py`, `apps/api/plane/app/serializers/project.py`, `apps/api/plane/db/models/state.py`, `apps/api/plane/db/models/project.py`, `apps/api/plane/app/views/project/member.py`, `apps/api/plane/app/views/project/invite.py`, `apps/api/plane/utils/url.py`, `apps/api/plane/utils/constants.py`, `apps/api/plane/utils/content_validator.py`, `apps/api/plane/app/serializers/workspace.py`
- Frontend: `apps/web/components/project/create-project-modal.tsx`, `apps/web/components/projects/create/root.tsx`, `apps/web/components/project/create/header.tsx`, `apps/web/components/project/create/common-attributes.tsx`, `apps/web/components/projects/create/attributes.tsx`, `apps/web/components/project/project-feature-update.tsx`, `apps/web/components/project/form.tsx`, `apps/web/components/project/settings/control-section.tsx`, `apps/web/components/project/archive-restore-modal.tsx`, `apps/web/components/project/delete-project-modal.tsx`

**Endpunkte (Katalog 04, `architecture/_data/endpoints.json`; 6 registriert)**

| EP | Methode | Pfad | Oberfläche | Handler | Permission | Inkr. 04 | CE-IDs |
|---|---|---|---|---|---|---|---|
| EP-0184 | GET | `/api/workspaces/{slug}/project-identifiers/` | App | ProjectEndpoints.CheckProjectIdentifierQuery | workspace.project.check_identifier | I0 | CE-PRJ-005 |
| EP-0185 | DELETE | `/api/workspaces/{slug}/project-identifiers/` | App | ProjectEndpoints.ReleaseProjectIdentifierCommand | workspace.project.release_identifier | I0 | CE-PRJ-005 |
| EP-0186 (vorab) | GET | `/api/workspaces/{slug}/projects/` | App | ProjectEndpoints.ListProjectsQuery | workspace.project.read | I0 | CE-PRJ-001 |
| EP-0187 | POST | `/api/workspaces/{slug}/projects/` | App | ProjectEndpoints.CreateProjectCommand | workspace.project.create | I0 | CE-PRJ-004 |
| EP-0189 (vorab) | GET | `/api/workspaces/{slug}/projects/{pk}/` | App | ProjectEndpoints.GetProjectQuery | project.project.read | I0 | CE-PRJ-006 |
| EP-0205 (vorab) | GET | `/api/workspaces/{slug}/projects/{project_id}/project-members/me/` | App | ProjectMemberEndpoints.GetMyProjectMembershipQuery | project.member.read_own | I0 | CE-PRJ-006, CE-PRJ-021 |

**Akzeptanzkriterien**

1. Identifier-Konflikt und -Freigabe liefern dieselben Codes/Texte wie das Original (Contract-Golden).
2. Default-States werden in Original-Reihenfolge und -Farben angelegt (Golden).
3. Contract: je Endpunkt dieses Pakets ≥ 1 Szenario mit Golden vom Original (Erfolg, Berechtigungsfehler, Validierungsfehler); Replay grün (L5).
4. Permission-Matrix (05 Anhang B) für alle Endpunkte dieses Pakets als L3-Test grün; Tenant-Isolation geprüft.
5. Signal-Stores strukturgleich zum MobX-Original (`store-parity-check`), Vitest je Action (L2).
6. E2E-Specs dieses Pakets grün gegen Original **und** funk. (Dual-Target, Pflichtszenarien 15 §3.9.3).
7. Visual-/DOM-/a11y-Prüfpunkte der betroffenen Screens (09 §4.14, 15 §3.10.2) innerhalb der Schwellwerte 15 §3.10.3 (Chromium); i18n-Schlüssel nur aus den Original-Locales (de/en).
8. `ce-coverage-check --ids CE-PRJ-004,CE-PRJ-005` grün (Mindestebenen 15 Anhang B).

**Testumfang**

- Pflicht-Ebenen (aus 15 Anhang B): L1, L2, L3, L5, L7, L8
- Testprojekte: `Funk.Projects.Tests`
- E2E-Specs (`frontend/apps/e2e/`): `web/projects/create-project.spec.ts`
- L3 Projects (Anlage), L5 Contract `POST {W}/projects/`, Identifier-Endpunkte, L7 `create-project.spec.ts`, L8 Visual Create-Project-Modal.

### WP-I0-006 – Designsystem-Fundament: CSS-Pipeline, Schriften, Icons, erste Propel-Primitive, Toast, Galerie

| Merkmal | Wert |
|---|---|
| Inkrement | I0 |
| Typ (DoD 15 §3.15.3) | F – Frontend-only |
| Größe | L |
| parallelisierbar | ja |
| Abhängigkeiten | WP-I0-105, WP-I0-910 |
| CE-IDs | CE-I18N-011, CE-I18N-012, CE-I18N-013, CE-I18N-021, CE-I18N-023, CE-I18N-024, CE-I18N-025, CE-I18N-026 |

**Ziel.** Tailwind-4.1-Konfiguration und CSS werden 1:1 übernommen (Vendoring, Import-Reihenfolge, `@source`-Scan), Schriften und Icons gebündelt (Airgap), die ersten Propel-Primitive (Button, Input, Menu, Tooltip, Avatar) sowie Toast, Spinner/Lade-Indikatoren, Animationen, Maßsystem und Avatare/Farbwähler stehen DOM- und pixelgleich in der Galerie; die Brand-Assets werden aus `assets/funk_logo.svg` erzeugt.

**Enthaltene CE-IDs**

| CE-ID | Feature | Status (15 Anh. B) | Inkrement laut 15 | Pflicht-Ebenen | Testprojekt | E2E-Spec |
|---|---|---|---|---|---|---|
| CE-I18N-011 | Typografie | übernommen | I0…I3 | L2 L4 L7 L8 (G-CSS) | Frontend-only | `gallery/design-system.spec.ts` |
| CE-I18N-012 | Gebündelte Schriften (Airgap) | übernommen | I0…I3 | L2 L7 L8 | Frontend-only | `gallery/design-system.spec.ts` |
| CE-I18N-013 | Icon-System | übernommen | I0…I3 | L2 L4 L7 L8 (G-ICONS) | Frontend-only | `gallery/design-system.spec.ts` |
| CE-I18N-021 | Toast-Benachrichtigungen | übernommen | I0…I3 | L2 L7 L8 | Frontend-only | `gallery/design-system.spec.ts` |
| CE-I18N-023 | Animationen | übernommen | I0…I3 | L2 L7 L8 | Frontend-only | `gallery/design-system.spec.ts` |
| CE-I18N-024 | Maßsystem, Elevation und Scrollbars | übernommen | I0…I3 | L2 L4 L7 L8 (G-CSS) | Frontend-only | `gallery/design-system.spec.ts` |
| CE-I18N-025 | Avatare und Farbwähler | übernommen | I0…I3 | L2 L7 L8 | Frontend-only | `gallery/design-system.spec.ts` |
| CE-I18N-026 | Lade-Indikatoren und Navigations-Progressbar | übernommen | I0…I3 | L2 L7 L8 | Frontend-only | `gallery/design-system.spec.ts` |

**Betroffene Module/Libs in `funk.`**

- Frontend: `frontend/libs/shared/tailwind-config`
- Frontend: `frontend/libs/shared/propel` (button, input, menu, tooltip, avatar, toast, spinner, headless/portal, floating)
- Frontend: `frontend/libs/shared/icons-lucide` (generiert)
- Frontend: `frontend/tools/propel-port/{fetch-propel,vendor-css,extract-classes,port-variants,port-icons.mjs}`
- Frontend: `frontend/tools/visual/{css-diff.ts,capture-reference.ts}`
- Frontend: `frontend/tools/reference-gallery`
- Frontend: `frontend/apps/gallery`
- Frontend: `frontend/tools/brand/{render-brand-assets.mjs,brand-i18n.mjs}`

**Referenzdokumente**

- Architektur: 09 §1.4 Zeile I0, §3.1–§3.10, §4.1–§4.6, §4.11, §5.1–§5.8
- Architektur: 01 §7.17
- Architektur: 17 ABG-026, ABG-027, ABG-148
- Architektur: 15 §3.10
- Analyse/Feature: `analysis/13a-designsystem-ui-tokens.md` §2.12, §2.16, §2.25, §2.26, §2.14, §2.10, §2.21
- Analyse/Feature: `analysis/13b-shared-packages-i18n.md` §2.4
- Analyse/Feature: `analysis/08-frontend-web-architektur.md` §2.9
- Feature-Katalog: `features/10-ce-feature-katalog.md` (Einträge CE-I18N-011, CE-I18N-012, CE-I18N-013, CE-I18N-021, CE-I18N-023, CE-I18N-024, CE-I18N-025, CE-I18N-026)

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- Frontend: `@makeplane/propel@0.7.3/dist/styles/variables.css`, `packages/tailwind-config/index.css`, `apps/web/app/root.tsx`, `apps/admin/app/root.tsx`, `apps/space/app/root.tsx`, `packages/blocks/src/emoji-icon-picker/logo.tsx`, `pnpm-workspace.yaml`, `@makeplane/propel@0.7.3/dist/icons/index.js`, `@makeplane/propel@0.7.3/dist/state-icons/index.js`, `packages/blocks/src/toast`, `@makeplane/propel@0.7.3/dist/components/toast`, `@makeplane/propel@0.7.3/dist/styles/animations.css`, `apps/web/styles/globals.css`, `@makeplane/propel@0.7.3/dist/internal/avatar-shared.js`, `@makeplane/propel@0.7.3/dist/components/avatar`, `packages/blocks/src/common/color-picker/color-picker.tsx`, `packages/blocks/src/common`, `packages/constants/src/label.ts`, `packages/utils/src/color.ts`, `packages/utils/src/string.ts`, `apps/web/components/common/logo-spinner.tsx`, `@makeplane/propel@0.7.3/dist/components/logo-spinner`, `packages/blocks/src/spinner`, `packages/blocks/src/skeleton`, `apps/web/lib/b-progress/AppProgressBar.tsx`

**Akzeptanzkriterien**

1. CSS-Diff-Test (G-CSS) der Shell-Selektoren gegen das Original-CSS ohne ungenehmigte Abweichung (09 §3.2.5).
2. Galerie: Button/Input/Menu/Tooltip/Avatar/Toast in allen Varianten DOM-gleich zur Referenz-Galerie und Visual ≤ 0,1 % (hell/dunkel/High-Contrast, Chromium).
3. Keine Schrift, kein Icon und kein Emoji wird zur Laufzeit von einem CDN geladen (Netzwerk-Allowlist-Test).
4. Favicons, App-Icons und Logos sind aus `assets/funk_logo.svg` in Original-Größe/-Dateiname erzeugt (BR-06); G-BRAND grün.
5. Galerie-Eintrag mit allen Varianten/Zuständen; DOM-Vertrag = Referenz-Galerie; Visual in allen Themes (Chromium).
6. Tastatur/Fokus (AX3/AX4) wie Original; portierte `packages/blocks`-Tests grün (falls vorhanden).
7. `ce-coverage-check --ids CE-I18N-011,CE-I18N-012,CE-I18N-013,CE-I18N-021,CE-I18N-023,CE-I18N-024,CE-I18N-025,CE-I18N-026` grün (Mindestebenen 15 Anhang B).

**Testumfang**

- Pflicht-Ebenen (aus 15 Anhang B): L2, L4, L7, L8
- Testprojekte: `Frontend-only`
- E2E-Specs (`frontend/apps/e2e/`): `gallery/design-system.spec.ts`
- L8 Galerie-Visual + DOM-Verträge (`visual/dom-contracts/gallery/**`), L2 Komponenten-Verhalten (Tastatur, Fokus, ARIA), G-CSS.

### WP-I0-101 – Repository funk. aufsetzen (Lizenz, Plan-Spiegel, AGENTS.md, Grundgerüst)

| Merkmal | Wert |
|---|---|
| Inkrement | I0 |
| Typ (DoD 15 §3.15.3) | I – Infrastruktur/Baustein |
| Größe | S |
| parallelisierbar | nein |
| Abhängigkeiten | – |
| CE-IDs | – (keine; Baustein/Spike/Abnahme) |

**Ziel.** Das Repository `github.com/mlwr/funk.` (Hauptbranch `develop`) erhält das verbindliche Grundgerüst: Solution-Datei, zentrale Build-Dateien, AGPL-Lizenz, NOTICE, Logo-Quelle, Plan-Spiegel und Agenten-Einstieg. Danach kann jeder weitere Agent ohne Rückfragen anfangen.

**Betroffene Module/Libs in `funk.`**

- Backend: `Funk.slnx`
- Backend: `global.json` (SDK-Pin 10.0.1xx, Aspire-SDK-Pin)
- Backend: `Directory.Build.props` (Nullable, TreatWarningsAsErrors, AGPL-Header-Check)
- Backend: `Directory.Build.targets` (`FunkInternalsVisibleTo`, R9)
- Backend: `Directory.Packages.props` (Central Package Management)
- Backend: `.editorconfig`, `.gitattributes`, `LICENSE` (AGPL-3.0), `NOTICE`
- Backend: `assets/funk_logo.svg`
- Backend: `docs/plan/` (Kopie von `migration/plan/`), `docs/migration/` (Kopie von `migration/architecture`, `migration/features`)
- Backend: `AGENTS.md`
- Backend: `.github/pull_request_template.md` (DoD-Checklisten 15 §3.15.3)
- Backend: `.github/CODEOWNERS`
- Frontend: `frontend/package.json`, `frontend/pnpm-workspace.yaml` (leerer Catalog)

**Referenzdokumente**

- Architektur: 00 ADR-006, ADR-009, ADR-009C
- Architektur: 01 §5.1 (Verzeichnisbaum)
- Architektur: 01 §6.1
- Architektur: 17 Umbenennungstabelle
- Architektur: 15 §3.15.3 (PR-Vorlage)
- Architektur: plan/03-agenten-leitfaden.md §5

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- `LICENSE.txt` (AGPL-3.0, Herkunftshinweis)
- `.github/pull_request_template.md`
- `.github/workflows/copyright-check.yml`

**Akzeptanzkriterien**

1. `develop` ist Default-Branch mit Branch-Protection (Merge nur über PR mit grünem G1/G2); `main` bleibt unverändert (ADR-009).
2. `AGENTS.md` verweist auf `docs/plan/03-agenten-leitfaden.md`, auf `mlwr/plane@funk-referenz-1.4.2` (nur lesend) und auf die Umbenennungstabelle (17).
3. `docs/plan/` ist byte-gleich zu `migration/plan/` des Referenzstands; `docs/migration/features/_data/ce-features.json` liegt vor (Eingabe für `ce-coverage-check`).
4. `LICENSE` = AGPL-3.0, `NOTICE` enthält den Herkunftshinweis auf Plane (Copyright Plane Software, Inc., AGPL-3.0) und ist durch das Lizenz-Gate fortschreibbar.
5. `dotnet build Funk.slnx` läuft auf leerer Solution fehlerfrei; keine Datei enthält `Plane.`-Zielbezeichner (Ausnahme: Verweise auf das Original).
6. Unit-Tests ≥ 90 % Zeilen; Architekturtest für jede neue Regel; AppHost-Test, falls Topologie betroffen.
7. Kurzreferenz in `docs/` des Repos `funk.`.

**Testumfang**

- L0: `tools/ci/license-header-check` auf das Grundgerüst angewendet (Vorstufe, Vollausbau WP-I0-106).

### WP-I0-102 – Aspire-AppHost und ServiceDefaults (Profile dev/test/prodlike)

| Merkmal | Wert |
|---|---|
| Inkrement | I0 |
| Typ (DoD 15 §3.15.3) | I – Infrastruktur/Baustein |
| Größe | M |
| parallelisierbar | ja |
| Abhängigkeiten | WP-I0-900 |
| CE-IDs | CE-OPS-021 |

**Ziel.** Der AppHost startet die vollständige I0-Topologie (PostgreSQL mit Rollen/DBs funk, keycloak, forgejo; Keycloak; Mailpit; Api; Worker; Realtime; Gateway; Migrator; Angular-Dev-Server) in den Profilen dev, test und prodlike; ServiceDefaults liefern OpenTelemetry, Health, Resilience und Service Discovery.

**Enthaltene CE-IDs**

| CE-ID | Feature | Status (15 Anh. B) | Inkrement laut 15 | Pflicht-Ebenen | Testprojekt | E2E-Spec |
|---|---|---|---|---|---|---|
| CE-OPS-021 | Lokale Entwicklungsumgebung | angepasst | I0 | L0 L6 | Funk.AppHost.Tests | – |

**Betroffene Module/Libs in `funk.`**

- Backend: `src/hosts/Funk.AppHost`
- Backend: `src/hosts/Funk.ServiceDefaults`
- Backend: `deploy/postgres/init/10-roles-and-databases.sh`
- Backend: `tests/Funk.AppHost.Tests`

**Referenzdokumente**

- Architektur: 14 §3.1 (Profile, Ports), §3.2 (AppHost vollständig), §3.6 (ServiceDefaults), §3.20 (lokale Entwicklung)
- Architektur: 01 §3.3/§3.4 (AppHost-Beispiel)
- Architektur: 17 ABG-012, ABG-018
- Analyse/Feature: `analysis/01-gesamtarchitektur-infrastruktur.md` §2.1
- Feature-Katalog: `features/10-ce-feature-katalog.md` (Einträge CE-OPS-021)

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- Backend: `setup.sh`, `docker-compose-local.yml`, `package.json`, `CONTRIBUTING.md`

**Akzeptanzkriterien**

1. `aspire run` (Profil `dev`) bringt alle Ressourcen in < 3 min auf „healthy“; `Funk.AppHost.Tests` (Profil `test`) prüft Start, Health und Referenzen.
2. Parameter (`keycloak-db-password`, `signing-key`, `forgejo-client-secret` …) werden generiert bzw. aus User-Secrets gelesen, nie im Klartext eingecheckt.
3. Profil `prodlike` nutzt die Rolle `keycloak` mit eigenem Passwort (nicht den Superuser) und `keycloak-config`.
4. Keine Ressource lädt zur Laufzeit etwas aus dem Internet nach (Netzwerk-Allowlist-Test ab I0, P6).
5. Unit-Tests ≥ 90 % Zeilen; Architekturtest für jede neue Regel; AppHost-Test, falls Topologie betroffen.
6. Kurzreferenz in `docs/` des Repos `funk.`.
7. `ce-coverage-check --ids CE-OPS-021` grün (Mindestebenen 15 Anhang B).

**Testumfang**

- Pflicht-Ebenen (aus 15 Anhang B): L0, L6
- Testprojekte: `Funk.AppHost.Tests`
- L6: `Funk.AppHost.Tests` (Start/Health/Routing-Smoke).
- Compose-Drift-Check (`aspire publish` → `git diff --exit-code deploy/compose`).

### WP-I0-103 – Gateway Funk.Gateway: Routen, statische Auslieferung, Base-URLs, Health, robots.txt, 413

| Merkmal | Wert |
|---|---|
| Inkrement | I0 |
| Typ (DoD 15 §3.15.3) | I – Infrastruktur/Baustein |
| Größe | M |
| parallelisierbar | ja |
| Abhängigkeiten | WP-I0-102, WP-I0-104 |
| CE-IDs | CE-OPS-006, CE-OPS-007, CE-OPS-008, CE-OPS-009 |

**Ziel.** Das YARP-Gateway bildet die Pfadregeln des Original-Caddy 1:1 ab (Routen G-01…G-17 ohne OG-Meta und Uploads), liefert die Angular-Builds statisch aus, stellt `runtime-config.json` bereit, setzt die Security-Header und beantwortet zu große Uploads mit dem Original-413-Body.

**Enthaltene CE-IDs**

| CE-ID | Feature | Status (15 Anh. B) | Inkrement laut 15 | Pflicht-Ebenen | Testprojekt | E2E-Spec |
|---|---|---|---|---|---|---|
| CE-OPS-006 | Statische Frontend-Auslieferung | übernommen | I0 | L2 L3 L6 L7 | Funk.Gateway.Tests | `ops/deployment-smoke.spec.ts` |
| CE-OPS-007 | Konfigurierbare Base-URLs und -Paths | übernommen | I0 | L1 L2 L3 L6 L7 | Funk.Gateway.Tests, Funk.ServiceDefaults.Tests | `ops/deployment-smoke.spec.ts` |
| CE-OPS-008 | Health-Checks und robots.txt | übernommen | I0 | L2 L3 L6 L7 | Funk.Gateway.Tests, Funk.AppHost.Tests | `ops/deployment-smoke.spec.ts` |
| CE-OPS-009 | Upload-Größenlimit mit 413-Fehler | übernommen | I0/I7 | L1 L2 L3 L5 L7 | Funk.Assets.Tests | `ops/deployment-smoke.spec.ts` |

**Betroffene Module/Libs in `funk.`**

- Backend: `src/hosts/Funk.Gateway` (Routen, `StaticFrontendMiddleware`, `RuntimeConfigEndpoint`)
- Backend: `tests/Funk.Gateway.Tests`

**Referenzdokumente**

- Architektur: 14 §3.7 (Routing-Tabelle, Header, Rate-Limit), §3.5
- Architektur: 05 §3.17.7 (Header-Werte)
- Architektur: 01 §7.12
- Architektur: 17 ABG-015, ABG-016
- Analyse/Feature: `analysis/01-gesamtarchitektur-infrastruktur.md` §2.9, §2.7, §2.21, §2.13
- Analyse/Feature: `analysis/05-api-public-v1-space-instanz.md` §2.8
- Analyse/Feature: `analysis/01-gesamtarchitektur-infrastruktur.md` §2.8.1–§2.8.3
- Feature-Katalog: `features/10-ce-feature-katalog.md` (Einträge CE-OPS-006, CE-OPS-007, CE-OPS-008, CE-OPS-009)

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- Backend: `apps/api/plane/settings/common.py`, `apps/api/plane/authentication/utils/host.py`, `apps/api/plane/web/views.py`, `apps/api/plane/web/urls.py`, `apps/live/src/controllers/health.controller.ts`, `apps/api/plane/middleware/request_body_size.py`, `apps/api/plane/license/api/views/instance.py`
- Frontend: `apps/web/caddy/Caddyfile`, `apps/admin/caddy/Caddyfile`, `apps/web/Dockerfile.web`, `apps/admin/Dockerfile.admin`, `packages/constants/src/endpoints.ts`, `apps/admin/vite.config.ts`, `apps/space/vite.config.ts`, `apps/space/Dockerfile.space`
- `apps/proxy/Caddyfile.ce`

**Endpunkte (Katalog 04, `architecture/_data/endpoints.json`; 2 registriert)**

| EP | Methode | Pfad | Oberfläche | Handler | Permission | Inkr. 04 | CE-IDs |
|---|---|---|---|---|---|---|---|
| EP-0730 | GET | `/` | Root | RootEndpoints.RootEndpoints.HealthOk | (anonym) | I0 | CE-OPS-008 |
| EP-0731 | GET | `/robots.txt` | Root | RootEndpoints.RootEndpoints.RobotsTxt | (anonym) | I0 | CE-OPS-008 |

**Akzeptanzkriterien**

1. `Funk.Gateway.Tests` prüft jede Pfadregel aus A01 §2.8.1 (Priorität, Rewrites, Redirects) gegen eine Tabelle der Original-Caddy-Regeln.
2. Security-Header je Oberfläche wie 05 §3.17.7 (Space ohne `X-Frame-Options` für Boards); CSP im Report-Only-Modus.
3. Upload > `Funk:Uploads:MaxFileSizeBytes` → 413 mit Original-Body; `/robots.txt` und Health-Pfade wie Original.
4. Unit-Tests ≥ 90 % Zeilen; Architekturtest für jede neue Regel; AppHost-Test, falls Topologie betroffen.
5. Kurzreferenz in `docs/` des Repos `funk.`.
6. `ce-coverage-check --ids CE-OPS-006,CE-OPS-007,CE-OPS-008,CE-OPS-009` grün (Mindestebenen 15 Anhang B).

**Testumfang**

- Pflicht-Ebenen (aus 15 Anhang B): L1, L2, L3, L5, L6, L7
- Testprojekte: `Funk.Gateway.Tests`, `Funk.ServiceDefaults.Tests`, `Funk.AppHost.Tests`, `Funk.Assets.Tests`
- E2E-Specs (`frontend/apps/e2e/`): `ops/deployment-smoke.spec.ts`
- L6 `Funk.Gateway.Tests`, E2E `ops/deployment-smoke.spec.ts`.

### WP-I0-104 – Backend-Fundament: BuildingBlocks, Funk.Data, Migrator, Modul-Schablone, Architekturtests

| Merkmal | Wert |
|---|---|
| Inkrement | I0 |
| Typ (DoD 15 §3.15.3) | I – Infrastruktur/Baustein |
| Größe | L |
| parallelisierbar | ja |
| Abhängigkeiten | WP-I0-900 |
| CE-IDs | CE-OPS-019 |

**Ziel.** Alle Backend-Konventionen werden einmal gebaut: Ergebnis-/Fehlertypen (`FunkErrors`), JSON-Konventionen, Oberflächen (`App`, `Auth`, `Instance`, `Space`, `V1`, `Integrations`, `Root`), Trailing-Slash, Validierung mit DRF-Feldfehlern, Pagination-Contracts, Persistenz-Basisklassen mit Audit-/Soft-Delete-/Ownership-Interceptor, `FunkDbContext`, Migrator mit Extensions, Options-Klassen, Health, Request-Logging und die Modul-Schablone mit ArchUnit-Regeln R1–R12.

**Enthaltene CE-IDs**

| CE-ID | Feature | Status (15 Anh. B) | Inkrement laut 15 | Pflicht-Ebenen | Testprojekt | E2E-Spec |
|---|---|---|---|---|---|---|
| CE-OPS-019 | Strukturiertes Request-Logging | übernommen | I0 | L1 L3 | Funk.BuildingBlocks.Tests | – |

**Betroffene Module/Libs in `funk.`**

- Backend: `src/building-blocks/Funk.BuildingBlocks` (Ids/UUIDv7, `IClock`, Results, Pagination, Branding/`Brand.cs`)
- Backend: `src/building-blocks/Funk.BuildingBlocks.Web` (Oberflächen, JSON, ErrorMapping, ValidationFilter, TrailingSlash)
- Backend: `src/building-blocks/Funk.BuildingBlocks.Persistence` (Entity-Basis, Interceptors, Konventionen)
- Backend: `src/building-blocks/Funk.Analyzers` (FUNK0001…FUNK0006)
- Backend: `src/data/Funk.Data` (`FunkDbContext`, Migration `…_Platform_Extensions` mit `pg_trgm`, `unaccent`, `vector`)
- Backend: `src/hosts/Funk.Migrator`, `src/hosts/Funk.Hosting`, `src/hosts/Funk.Api`
- Backend: `tests/Funk.ArchitectureTests`, `tests/Funk.BuildingBlocks.Tests`, `tests/Funk.Migrator.Tests`
- Backend: `src/building-blocks/Funk.BuildingBlocks.Testing` (FunkApiFactory, PostgresContainerFixture, Respawn, FixedClock)

**Referenzdokumente**

- Architektur: 02 §1.3, §3.1–§3.10, §3.14–§3.18, §5.1
- Architektur: 01 §5.2 (R1–R10), §5.3 (Modul-Schablone), §7.1–§7.16
- Architektur: 03 §3.1, §3.13, §5.1, §5.7
- Architektur: 16 D16-ADR-03 (R11/R12)
- Architektur: 14 §3.15 (Migrator)
- Analyse/Feature: `analysis/01-gesamtarchitektur-infrastruktur.md` §2.23
- Analyse/Feature: `analysis/01-gesamtarchitektur-infrastruktur.md` §2.11–§2.13
- Analyse/Feature: `analysis/06-auth-sicherheit-querschnitt.md` §2.12 (Fehlertexte)
- Feature-Katalog: `features/10-ce-feature-katalog.md` (Einträge CE-OPS-019)

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- Backend: `apps/api/plane/middleware/logger.py`, `apps/api/plane/settings/production.py`, `apps/api/plane/utils/logging.py`
- Frontend: `packages/logger/src/config.ts`
- `apps/api/plane/utils/` (Paginator, Exception-Handler)
- `apps/api/plane/app/views/base.py`
- `apps/api/plane/db/mixins.py`
- `apps/api/plane/settings/common.py`
- `apps/api/plane/middleware/`

**Endpunkte (Katalog 04, `architecture/_data/endpoints.json`; 1 registriert)**

| EP | Methode | Pfad | Oberfläche | Handler | Permission | Inkr. 04 | CE-IDs |
|---|---|---|---|---|---|---|---|
| EP-0732 (vorab) | GET | `/api/schema/internal/` | OpenApi | OpenApiEndpoints.OpenApiDocumentEndpoint(internal) | (anonym, nur mit Plane:OpenApi:Enabled) | I0 | CE-API-004 |

**Akzeptanzkriterien**

1. `Funk.ArchitectureTests` prüfen R1–R12 (01 §5.2, 16 D16-ADR-03) und schlagen bei einem absichtlich eingebauten Verstoß (Testfixture) fehl.
2. Leere DB → `Funk.Migrator` legt Schema, Extensions und Referenz-Seeds idempotent an (zweiter Lauf ohne Änderung, `Funk.Migrator.Tests`); `dotnet ef migrations has-pending-model-changes` leer.
3. JSON-Converter, Fehlerfabrik und Cursor-Codec erfüllen die Unit-Tests aus 02 §7.1 (Mikrosekunden-Zeitformat, `snake_case`, Optional<T>-PATCH).
4. Jede Route trägt `.RequirePermission(...)` oder `.AllowAnonymous()` (Architekturtest); Routen akzeptieren Pfade mit und ohne abschließenden Slash ohne Redirect.
5. Strukturiertes Request-Logging `funk.api.request` mit Redaktion (keine Secrets/PII), Health-Checks nicht geloggt (CE-OPS-019).
6. Architekturtest `NamingTests`: kein Projekt, Namespace, Options-Schlüssel, Header, Metrik- oder Event-Name des Zielcodes beginnt mit `Plane`/`plane` (ADR-009C, plan/04 OP-PLAN-04); Verweise auf das Original in Kommentaren/Tests sind ausgenommen.
7. Unit-Tests ≥ 90 % Zeilen; Architekturtest für jede neue Regel; AppHost-Test, falls Topologie betroffen.
8. Kurzreferenz in `docs/` des Repos `funk.`.
9. `ce-coverage-check --ids CE-OPS-019` grün (Mindestebenen 15 Anhang B).

**Testumfang**

- Pflicht-Ebenen (aus 15 Anhang B): L1, L3
- Testprojekte: `Funk.BuildingBlocks.Tests`
- L0 Architekturtests (inkl. `NamingTests`), L1 BuildingBlocks (≥ 90 % Zeilen), L3 Migrator-Tests, Log-Redaktionstest.

### WP-I0-105 – Frontend-Fundament: Angular-Workspace, Shared-Libs, Routing-Kern, Wrapper, Runtime-Config

| Merkmal | Wert |
|---|---|
| Inkrement | I0 |
| Typ (DoD 15 §3.15.3) | F – Frontend-only |
| Größe | L |
| parallelisierbar | ja |
| Abhängigkeiten | WP-I0-900 |
| CE-IDs | – (keine; Baustein/Spike/Abnahme) |

**Ziel.** Der Angular-22-Workspace mit den Apps `web`, `admin`, `space`, `gallery`, `e2e` steht; `libs/shared/*` sind aus den Original-Paketen übernommen, Bootstrap, Interceptor-Kette, QueryCache, RouterStore, `AppRouter`, Wrapper (`AuthenticationWrapper`, `InstanceWrapper`, `StoreWrapper`, `WorkspaceAuthWrapper`), Runtime-Config, Inline-Theme-Script (hell/dunkel/system) und das Laden der Locales `de`/`en` sind fertig.

**Betroffene Module/Libs in `funk.`**

- Frontend: `frontend/angular.json`, `frontend/sheriff.config.ts`, `frontend/eslint.config.js`, `frontend/vitest.config.ts`
- Frontend: `frontend/apps/{web,admin,space,gallery,e2e}`
- Frontend: `frontend/libs/shared/{types,constants,utils,i18n,services,state-kit,runtime-config,cdk,theme}` (`@funk/*`)
- Frontend: `frontend/libs/web/core` (RootStore, RouterStore, Wrapper, Interceptors)
- Frontend: `frontend/tools/eslint-rules`, `frontend/tools/contract-check`, `frontend/tools/i18n-sync-check`

**Referenzdokumente**

- Architektur: 08 §1.3 Spalte I0, §3.1–§3.5, §3.7, §3.8, §3.11, §3.14, §5.1–§5.9
- Architektur: 01 §6
- Architektur: 17 ABG-007, ABG-023, ABG-028
- Analyse/Feature: `analysis/08-frontend-web-architektur.md` §2.2, §2.13
- Analyse/Feature: `analysis/13b-shared-packages-i18n.md` §3

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- `apps/web/app/root.tsx`, `apps/web/app/routes.ts`, `apps/web/app/provider.tsx`
- `apps/web/core/lib/wrappers/`
- `apps/web/core/store/router.store.ts`
- `packages/services/src/api.service.ts`
- `packages/i18n/src/`

**Akzeptanzkriterien**

1. `pnpm build` baut web/admin/space; Sheriff-Grenzen (08 §3.1.5) und Lint-Regeln (`no-plan-identifiers`, `no-external-urls`) laufen in G1.
2. Gleiches Build-Artefakt läuft unter anderen Base-URLs allein über `runtime-config.json` (E2E, 01 §7.12).
3. Routen von `web` sind in Reihenfolge und Verschachtelung 1:1 zu `apps/web/app/routes.ts`; nur Routen abgenommener Schnitte sind registriert (01 §7.19); `route-contract.web.yaml` grün.
4. Locales `de` (Standard) und `en` laden; Sprachauswahl ist auf diese zwei beschränkt (ADR-009D); Theme-Flash-Test (Inline-Script) grün.
5. Contract-Check `openapi-typescript`-Typen ↔ `libs/shared/types` läuft in G1.
6. Galerie-Eintrag mit allen Varianten/Zuständen; DOM-Vertrag = Referenz-Galerie; Visual in allen Themes (Chromium).
7. Tastatur/Fokus (AX3/AX4) wie Original; portierte `packages/blocks`-Tests grün (falls vorhanden).

**Testumfang**

- L0 Sheriff/ESLint/i18n-Sync/Contract-Check, L2 Stores/Interceptors (Vitest), Routing-Contract-Test (08 §7.2).

### WP-I0-106 – Test- und CI-Infrastruktur: Gates G0–G3, Lizenz-Gate, G-BRAND, Coverage- und Ledger-Werkzeuge

| Merkmal | Wert |
|---|---|
| Inkrement | I0 |
| Typ (DoD 15 §3.15.3) | I – Infrastruktur/Baustein |
| Größe | L |
| parallelisierbar | ja |
| Abhängigkeiten | WP-I0-101, WP-I0-900 |
| CE-IDs | CE-OPS-022, CE-OPS-023 |

**Ziel.** Die Quality-Gates sind lokal und in CI identisch ausführbar (`./tools/ci/gate.sh g0…g3`), der isolierte Test-Stack (Aspire-Profil `test`) und die GitHub-Actions-Workflows laufen auf `develop`. `ce-coverage-check`, `original-test-ledger`, `brand-gate`, `license-gate`, gitleaks und Trivy sind aktiv.

**Enthaltene CE-IDs**

| CE-ID | Feature | Status (15 Anh. B) | Inkrement laut 15 | Pflicht-Ebenen | Testprojekt | E2E-Spec |
|---|---|---|---|---|---|---|
| CE-OPS-022 | Isolierter Test-Stack und Testsuites | angepasst | I0 | L0 L6 | Funk.ArchitectureTests, Funk.AppHost.Tests | – |
| CE-OPS-023 | CI/CD-Pipelines | angepasst | I0 | L0 | tools/ci (Gate-Selbsttests) | – |

**Betroffene Module/Libs in `funk.`**

- Backend: `tools/ci/{gate.sh,ce-coverage-check,original-test-ledger,brand-gate,license-gate,license-header-check,seed-manifest-diff,acceptance-report,assert-no-node.sh}`
- Backend: `.github/workflows/{ci.yml,images.yml,nightly.yml,check-version.yml}`
- Backend: `tests/ce-matrix.yaml` (aus 15 Anhang B)
- Backend: `tests/original-tests/ledger.yaml` (1 092 Einträge)
- Backend: `tests/extension-points.yaml`
- Backend: `tests/Funk.Tools.Gates.Tests`
- Frontend: `frontend/apps/e2e/` (Playwright-Gerüst Dual-Target, `AuthDriver` beider Targets)
- Frontend: `frontend/tools/brand/allowlist.json`
- Frontend: axe-Baseline-Mechanik

**Referenzdokumente**

- Architektur: 15 §3.1, §3.2, §3.4, §3.15, §3.16 Zeile I0
- Architektur: 14 §3.21 (CI/CD)
- Architektur: 17 Z-10 (nur Chromium), ABG-149
- Analyse/Feature: `analysis/01-gesamtarchitektur-infrastruktur.md` §2.25, §2.24
- Feature-Katalog: `features/10-ce-feature-katalog.md` (Einträge CE-OPS-022, CE-OPS-023)

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- Backend: `docker-compose-test.yml`, `apps/api/pytest.ini`, `apps/api/plane/tests/conftest.py`, `apps/api/tests/RUNNING_TESTS.md`, `apps/live/vitest.config.ts`, `.github/workflows/build-branch.yml`, `.github/workflows/check-version.yml`, `.github/workflows/codeql.yml`, `.github/workflows/copyright-check.yml`, `.github/workflows/migration-check.yml`, `.github/workflows/pull-request-build-lint-api.yml`, `.github/workflows/pull-request-build-lint-web-apps.yml`, `.github/workflows/i18n-sync-check.yml`, `.github/workflows/react-doctor.yml`, `.github/workflows/feature-deployment.yml`
- Frontend: `packages/blocks/vitest.config.ts`
- `.github/workflows/` (Original-CI als Vorlage)

**Akzeptanzkriterien**

1. `./tools/ci/gate.sh g1` lokal und in CI identisch; G1 < 15 min, G2 < 40 min (15 §3.15.1).
2. Workflows triggern auf `pull_request`/`merge_group` gegen `develop` und `push` auf `develop` (nicht `main`, ADR-009; Korrektur von 14 §3.21.1, siehe plan/04 OP-PLAN-02).
3. `ce-coverage-check --structure` erkennt alle 507 CE-IDs, `entfällt`-IDs ohne Tests; `original-test-ledger` hat alle 1 092 Einträge mit Statusvorschlag.
4. G-BRAND schlägt bei einem eingebauten „Plane“-String in einem Bundle fehl und ist mit leerer Allowlist grün.
5. Visual-Gate läuft ausschließlich mit Chromium (Z-10); Firefox/WebKit sind nicht Teil der CI-Matrix.
6. Unit-Tests ≥ 90 % Zeilen; Architekturtest für jede neue Regel; AppHost-Test, falls Topologie betroffen.
7. Kurzreferenz in `docs/` des Repos `funk.`.
8. `ce-coverage-check --ids CE-OPS-022,CE-OPS-023` grün (Mindestebenen 15 Anhang B).

**Testumfang**

- Pflicht-Ebenen (aus 15 Anhang B): L0, L6
- Testprojekte: `Funk.ArchitectureTests`, `Funk.AppHost.Tests`, `tools/ci (Gate-Selbsttests)`
- `Funk.Tools.Gates.Tests` (Selbsttests der Gate-Werkzeuge), Probe-PR mit absichtlichen Verstößen je Gate.

### WP-I0-107 – Realtime-Host-Gerüst Funk.Realtime (Health, Origin-Prüfung, /live-Fallback)

| Merkmal | Wert |
|---|---|
| Inkrement | I0 |
| Typ (DoD 15 §3.15.3) | I – Infrastruktur/Baustein |
| Größe | S |
| parallelisierbar | ja |
| Abhängigkeiten | WP-I0-103, WP-I0-104 |
| CE-IDs | CE-RT-009 |

**Ziel.** Der Host `Funk.Realtime` mit `RealtimeComposition` läuft: Health `/live/health/` auf dem App-Port, `/health/*` auf dem Management-Port, `WebSocketOriginValidator`, `SessionTicketReader`, Fallback `/live/{**}` → 404 `{"message":"Not Found"}`, Gateway-Routen G-06/G-07.

**Enthaltene CE-IDs**

| CE-ID | Feature | Status (15 Anh. B) | Inkrement laut 15 | Pflicht-Ebenen | Testprojekt | E2E-Spec |
|---|---|---|---|---|---|---|
| CE-RT-009 | Health-Endpunkt des Live-Servers | übernommen | I4 | L1 L2 L3 L5 L6 L7 L8 | Funk.Collaboration.Tests | `web/realtime/collaboration.spec.ts` |

**Betroffene Module/Libs in `funk.`**

- Backend: `src/hosts/Funk.Realtime`
- Backend: `src/hosts/Funk.Hosting/RealtimeComposition.cs`
- Backend: `tests/Funk.Collaboration.Tests` (Smoke-Teil)

**Referenzdokumente**

- Architektur: 07 §1.4 Zeile I0, §3.2
- Architektur: 05 §3.11
- Architektur: 14 §3.7.1 (G-06, G-07)
- Analyse/Feature: `analysis/12-editor-echtzeit-live.md` §2.26
- Feature-Katalog: `features/10-ce-feature-katalog.md` (Einträge CE-RT-009)

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- Backend: `apps/live/src/controllers/health.controller.ts`
- `apps/live/src/server.ts`
- `apps/live/src/controllers/health.controller.ts`

**Endpunkte (Katalog 04, `architecture/_data/endpoints.json`; 1 registriert)**

| EP | Methode | Pfad | Oberfläche | Handler | Permission | Inkr. 04 | CE-IDs |
|---|---|---|---|---|---|---|---|
| EP-0413 | GET | `/live/health/` | Live | RealtimeHealthEndpoint.Get | (anonym) | I0 | CE-RT-009 |

**Akzeptanzkriterien**

1. `GET /live/health/` liefert den Original-Body (Golden), unbekannte `/live/…`-Pfade 404 mit `{"message":"Not Found"}`.
2. WebSocket-Upgrade mit fremdem `Origin` wird abgewiesen (AK-07-01/-02).
3. Unit-Tests ≥ 90 % Zeilen; Architekturtest für jede neue Regel; AppHost-Test, falls Topologie betroffen.
4. Kurzreferenz in `docs/` des Repos `funk.`.
5. `ce-coverage-check --ids CE-RT-009` grün (Mindestebenen 15 Anhang B).

**Testumfang**

- Pflicht-Ebenen (aus 15 Anhang B): L1, L2, L3, L5, L6, L7, L8
- Testprojekte: `Funk.Collaboration.Tests`
- E2E-Specs (`frontend/apps/e2e/`): `web/realtime/collaboration.spec.ts`
- L6 `RealtimeSmokeTests` (Host-Teil).

### WP-I0-108 – Keycloak-Realm als Code (dev/test/prod) inkl. Nachweis entfallener Auth-Funktionen

| Merkmal | Wert |
|---|---|
| Inkrement | I0 |
| Typ (DoD 15 §3.15.3) | V – Vertikaler Schnitt |
| Größe | M |
| parallelisierbar | ja |
| Abhängigkeiten | WP-I0-102, WP-I0-907 |
| CE-IDs | CE-AUTH-002, CE-AUTH-003, CE-AUTH-004, CE-AUTH-005, CE-AUTH-006, CE-AUTH-007, CE-AUTH-008, CE-AUTH-009, CE-AUTH-010, CE-AUTH-011, CE-AUTH-013, CE-AUTH-017, CE-AUTH-018, CE-AUTH-019, CE-AUTH-020, CE-AUTH-021, CE-PROF-007 |

**Ziel.** Realm `funk` (Clients `funk-web`, `funk-admin`, `funk-space`, `funk-backend`, `funk-forgejo`, Rolle `funk-instance-admin`, Flow `funk-browser`, Client-Scopes und Mapper inkl. `groups`, sieben Testbenutzer mit deterministischen IDs) liegt als Code vor: dev-Realm, generierter Test-Realm und Prod-Templates für keycloak-config-cli; Image `funk-keycloak`. Die durch ADR-008 entfallenen Funktionen (Registrierung, Passwort, Magic-Code, OAuth-Provider, Steuerung der Auth-Methoden, verknüpfte Konten) sind als „entfällt“ mit Ersatznachweis `KeycloakRealmConfigTests` belegt.

**Enthaltene CE-IDs**

| CE-ID | Feature | Status (15 Anh. B) | Inkrement laut 15 | Pflicht-Ebenen | Testprojekt | E2E-Spec |
|---|---|---|---|---|---|---|
| CE-AUTH-002 | Sign-up-Seite | entfällt – Ersatz: `KeycloakRealmConfigTests` (L3), Visual-Suite `keycloak` (L8) | – | – | – | – |
| CE-AUTH-003 | E-Mail-Existenzprüfung | entfällt – Ersatz: `KeycloakRealmConfigTests` (L3), Visual-Suite `keycloak` (L8) | – | – | – | – |
| CE-AUTH-004 | Anmeldung mit E-Mail und Passwort | entfällt – Ersatz: `KeycloakRealmConfigTests` (L3), Visual-Suite `keycloak` (L8) | – | – | – | – |
| CE-AUTH-005 | Registrierung mit E-Mail und Passwort | entfällt – Ersatz: `KeycloakRealmConfigTests` (L3), Visual-Suite `keycloak` (L8) | – | – | – | – |
| CE-AUTH-006 | Magic-Code anfordern | entfällt – Ersatz: `KeycloakRealmConfigTests` (L3), Visual-Suite `keycloak` (L8) | – | – | – | – |
| CE-AUTH-007 | Anmeldung/Registrierung mit Magic-Code | entfällt – Ersatz: `KeycloakRealmConfigTests` (L3), Visual-Suite `keycloak` (L8) | – | – | – | – |
| CE-AUTH-008 | Login mit Google | entfällt – Ersatz: `KeycloakRealmConfigTests` (L3), Visual-Suite `keycloak` (L8) | – | – | – | – |
| CE-AUTH-009 | Login mit GitHub inkl. Organisationspflicht | entfällt – Ersatz: `KeycloakRealmConfigTests` (L3), Visual-Suite `keycloak` (L8) | – | – | – | – |
| CE-AUTH-010 | Login mit GitLab (auch self-hosted) | entfällt – Ersatz: `KeycloakRealmConfigTests` (L3), Visual-Suite `keycloak` (L8) | – | – | – | – |
| CE-AUTH-011 | Login mit Gitea | entfällt – Ersatz: `KeycloakRealmConfigTests` (L3), Visual-Suite `keycloak` (L8) | – | – | – | – |
| CE-AUTH-013 | Steuerung der Auth-Methoden | entfällt – Ersatz: `KeycloakRealmConfigTests` (L3), Visual-Suite `keycloak` (L8) | – | – | – | – |
| CE-AUTH-017 | Passwort vergessen | entfällt – Ersatz: `KeycloakRealmConfigTests` (L3), Visual-Suite `keycloak` (L8) | – | – | – | – |
| CE-AUTH-018 | Passwort zurücksetzen | entfällt – Ersatz: `KeycloakRealmConfigTests` (L3), Visual-Suite `keycloak` (L8) | – | – | – | – |
| CE-AUTH-019 | Passwort erstmalig setzen | entfällt – Ersatz: `KeycloakRealmConfigTests` (L3), Visual-Suite `keycloak` (L8) | – | – | – | – |
| CE-AUTH-020 | Passwort ändern | entfällt – Ersatz: `KeycloakRealmConfigTests` (L3), Visual-Suite `keycloak` (L8) | – | – | – | – |
| CE-AUTH-021 | Passwortstärke-Anzeige | entfällt – Ersatz: `KeycloakRealmConfigTests` (L3), Visual-Suite `keycloak` (L8) | – | – | – | – |
| CE-PROF-007 | Verknüpfte OAuth-Konten (nur API) | entfällt – Ersatz: keiner (verknüpfte Konten verwaltet Keycloak) | – | – | – | – |

**Betroffene Module/Libs in `funk.`**

- Backend: `deploy/keycloak/realms/funk-realm.json` (dev)
- Backend: `deploy/keycloak/realms/funk-realm.test.json` (generiert über `Funk.Tools.ParityHarness keycloak-test-realm`, ABG-001)
- Backend: `deploy/keycloak/config/{00-funk-realm,10-funk-bootstrap-admin,20-forgejo-client}.json`
- Backend: Image `funk-keycloak` (Basis `quay.io/keycloak/keycloak:26.x`, `kc.sh build`)
- Backend: `tests/seed/keycloak/{test-overrides,parity-users}.json`
- Backend: `tests/modules/Funk.Identity.Tests/Keycloak/KeycloakRealmConfigTests.cs`

**Referenzdokumente**

- Architektur: 05 §3.15 (Realm als Code), §4.1 (CE-IDs → neues Verhalten)
- Architektur: 14 §3.3.1–§3.3.3
- Architektur: 15 §3.14.2
- Architektur: 17 ABG-001, ABG-002, ABG-003, Umbenennungstabelle
- Architektur: 01 O-06 (Client je App)
- Analyse/Feature: `analysis/08-frontend-web-architektur.md` §3.2
- Analyse/Feature: `analysis/10a-frontend-workspace-projekt-navigation.md` §2.14, §2.13
- Analyse/Feature: `analysis/06-auth-sicherheit-querschnitt.md` §3.4, §3.2, §3.3, §3.5, §3.6, §2.4, §2.6, §3.10, §3.11
- Analyse/Feature: `analysis/13b-shared-packages-i18n.md` §3.10
- Analyse/Feature: `analysis/07-hintergrundjobs-mail-storage-webhooks.md` §2.17
- Analyse/Feature: `analysis/11-frontend-admin-space.md` §3.9
- Analyse/Feature: `analysis/03-api-intern-workspace-projekt-user.md` §3.6
- Analyse/Feature: `analysis/02a-datenmodell-kern.md` §2.3
- Feature-Katalog: `features/10-ce-feature-katalog.md` (Einträge CE-AUTH-002, CE-AUTH-003, CE-AUTH-004, CE-AUTH-005, CE-AUTH-006, CE-AUTH-007, CE-AUTH-008, CE-AUTH-009, CE-AUTH-010, CE-AUTH-011, CE-AUTH-013, CE-AUTH-017, CE-AUTH-018, CE-AUTH-019, CE-AUTH-020, CE-AUTH-021, CE-PROF-007)

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- Backend: `apps/api/plane/authentication/views/app/email.py`, `apps/api/plane/authentication/adapter/base.py`, `apps/api/plane/authentication/utils/password.py`, `apps/api/plane/authentication/views/app/check.py`, `apps/api/plane/authentication/views/space/check.py`, `apps/api/plane/authentication/provider/credentials/email.py`, `apps/api/plane/authentication/views/app/magic.py`, `apps/api/plane/authentication/views/space/magic.py`, `apps/api/plane/authentication/provider/credentials/magic_code.py`, `apps/api/plane/bgtasks/magic_link_code_task.py`, `apps/api/templates/emails/auth/magic_signin.html`, `apps/api/plane/authentication/provider/oauth/google.py`, `apps/api/plane/authentication/views/app/google.py`, `apps/api/plane/authentication/utils/oauth_state.py`, `apps/api/plane/authentication/provider/oauth/github.py`, `apps/api/plane/authentication/views/app/github.py`, `apps/api/plane/authentication/provider/oauth/gitlab.py`, `apps/api/plane/authentication/views/app/gitlab.py`, `apps/api/plane/authentication/provider/oauth/gitea.py`, `apps/api/plane/authentication/views/app/gitea.py`, `apps/api/plane/authentication/views/space/gitea.py`, `apps/api/plane/utils/instance_config_variables/core.py`, `apps/api/plane/license/utils/instance_value.py`, `apps/api/plane/license/api/views/instance.py`, `apps/api/plane/authentication/views/app/password_management.py`, `apps/api/plane/authentication/views/space/password_management.py`, `apps/api/plane/bgtasks/forgot_password_task.py`, `apps/api/templates/emails/auth/forgot_password.html`, `apps/api/plane/authentication/views/common.py`, `apps/api/plane/app/views/user/base.py`, `apps/api/plane/app/serializers/user.py`, `apps/api/plane/authentication/adapter/oauth.py`, `apps/api/plane/db/models/user.py`
- Frontend: `apps/web/app/(all)/sign-up/page.tsx`, `apps/web/app/(all)/sign-up/layout.tsx`, `apps/web/components/account/auth-forms/auth-root.tsx`, `apps/web/components/account/auth-forms/form-root.tsx`, `apps/web/components/account/auth-forms/email.tsx`, `apps/web/components/account/auth-forms/password.tsx`, `apps/web/components/account/auth-forms/unique-code.tsx`, `apps/web/components/account/auth-forms/auth-header.tsx`, `apps/web/components/auth-screens/auth-base.tsx`, `apps/web/components/auth-screens/header.tsx`, `apps/web/services/auth.service.ts`, `packages/utils/src/auth.ts`, `packages/constants/src/auth/index.ts`, `packages/services/src/auth/auth.service.ts`, `packages/services/src/auth/sites-auth.service.ts`, `apps/web/app/(home)/page.tsx`, `apps/web/hooks/oauth/core.tsx`, `apps/admin/app/(all)/(dashboard)/authentication/page.tsx`, `apps/admin/hooks/oauth/core.tsx`, `apps/admin/components/authentication/authentication-method-card.tsx`, `apps/admin/helpers/authentication.ts`, `apps/admin/components/authentication/email-config-switch.tsx`, `apps/admin/components/authentication/password-config-switch.tsx`, `apps/web/components/account/auth-forms/forgot-password.tsx`, `apps/web/components/account/auth-forms/forgot-password-popover.tsx`, `apps/web/app/(all)/accounts/forgot-password/page.tsx`, `apps/web/app/(all)/accounts/reset-password/page.tsx`, `apps/web/app/(all)/accounts/set-password/page.tsx`, `apps/web/components/account/auth-forms/reset-password.tsx`, `apps/web/components/settings/profile/content/pages/security.tsx`

**Akzeptanzkriterien**

1. `KeycloakRealmConfigTests`: Registrierung aus, Passwort-Richtlinie/OTP/WebAuthn gemäß 05 §3.15, keine Social-Provider, Redirect-URIs je Client exakt, Back-Channel-Logout-URL gesetzt; `TestRealm_IsUpToDate` (`--check`) grün.
2. Härtungsprüfungen des Prod-Templates (D15-SEC-11) laufen gegen `deploy/keycloak/config/00-funk-realm.json`.
3. Für jede enthaltene „entfällt“-CE-ID ist der Ersatztest in `tests/ce-matrix.yaml` eingetragen; `ce-coverage-check` meldet keine Tests für diese IDs (Status entfällt).
4. Contract: je Endpunkt dieses Pakets ≥ 1 Szenario mit Golden vom Original (Erfolg, Berechtigungsfehler, Validierungsfehler); Replay grün (L5).
5. Permission-Matrix (05 Anhang B) für alle Endpunkte dieses Pakets als L3-Test grün; Tenant-Isolation geprüft.
6. Signal-Stores strukturgleich zum MobX-Original (`store-parity-check`), Vitest je Action (L2).
7. E2E-Specs dieses Pakets grün gegen Original **und** funk. (Dual-Target, Pflichtszenarien 15 §3.9.3).
8. Visual-/DOM-/a11y-Prüfpunkte der betroffenen Screens (09 §4.14, 15 §3.10.2) innerhalb der Schwellwerte 15 §3.10.3 (Chromium); i18n-Schlüssel nur aus den Original-Locales (de/en).
9. `ce-coverage-check --ids CE-AUTH-002,CE-AUTH-003,CE-AUTH-004,CE-AUTH-005,CE-AUTH-006,CE-AUTH-007,CE-AUTH-008,CE-AUTH-009,CE-AUTH-010,CE-AUTH-011,CE-AUTH-013,CE-AUTH-017,CE-AUTH-018,CE-AUTH-019,CE-AUTH-020,CE-AUTH-021,CE-PROF-007` grün (Mindestebenen 15 Anhang B).

**Testumfang**

- L3 `KeycloakRealmConfigTests`, G-BRAND über den Realm-Export.

### WP-I0-109 – Keycloak-Login-Themes funk und funk-space (1:1-Optik der Sign-in-Seite, funk.-Branding)

| Merkmal | Wert |
|---|---|
| Inkrement | I0 |
| Typ (DoD 15 §3.15.3) | V – Vertikaler Schnitt |
| Größe | L |
| parallelisierbar | ja |
| Abhängigkeiten | WP-I0-108, WP-I0-006 |
| CE-IDs | CE-AUTH-015 |

**Ziel.** Die Login-Themes `funk` (Web/God Mode) und `funk-space` bilden die Original-Sign-in-Seiten von `apps/web` und `apps/space` pixelgleich nach (eigenes `template.ftl` ohne PatternFly, Original-Klassen und -CSS), mit funk.-Logo und -Texten (BR-09), AGB-/Datenschutz-Hinweis und Auth-Fuß (CE-AUTH-015) sowie der Hell/Dunkel-Übernahme aus funk. (Z-08).

**Enthaltene CE-IDs**

| CE-ID | Feature | Status (15 Anh. B) | Inkrement laut 15 | Pflicht-Ebenen | Testprojekt | E2E-Spec |
|---|---|---|---|---|---|---|
| CE-AUTH-015 | AGB-Hinweis und Auth-Fuß | übernommen | I0/I1 | L1 L2 L3 L5 L7 L8 | Funk.Identity.Tests | `web/auth/keycloak-login.spec.ts` |

**Betroffene Module/Libs in `funk.`**

- Backend: `deploy/keycloak/themes/{funk,funk-space}` (`.ftl`, `messages_{de,en}.properties`, `theme.properties`, Ressourcen)
- Frontend: `frontend/apps/e2e/visual/` Suite `keycloak-login`
- Frontend: `frontend/tools/brand/render-brand-assets.mjs` (Theme-Logo)

**Referenzdokumente**

- Architektur: 05 §3.16
- Architektur: 14 §3.3.4
- Architektur: 09 §3.13
- Architektur: 17 ABG-148, Z-08
- Analyse/Feature: `analysis/10a-frontend-workspace-projekt-navigation.md` §2.14
- Feature-Katalog: `features/10-ce-feature-katalog.md` (Einträge CE-AUTH-015)

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- Frontend: `apps/web/components/account/terms-and-conditions.tsx`, `apps/web/components/auth-screens/footer.tsx`
- `apps/web/app/(all)/(home)/page.tsx`
- `apps/web/core/components/account/auth-forms/`
- `apps/space/app/page.tsx`

**Akzeptanzkriterien**

1. Visual-Diff ≤ 1 % gegen die Original-Sign-in-Seite (web und space, hell/dunkel; Referenzen mit vorab ersetztem Branding, BR-13).
2. Theme übernimmt `localStorage.theme` (same-origin `/idp`), Fallback `prefers-color-scheme` (Z-08); Texte nur `de`/`en` (ADR-009D).
3. Abweichungen DEV-UI-01…-03 (kein Einladungskopf, Keycloak-URL, keine Sign-up-/Code-/OAuth-Links) in `ui-deviations.yaml` mit Entscheidungsverweis.
4. Contract: je Endpunkt dieses Pakets ≥ 1 Szenario mit Golden vom Original (Erfolg, Berechtigungsfehler, Validierungsfehler); Replay grün (L5).
5. Permission-Matrix (05 Anhang B) für alle Endpunkte dieses Pakets als L3-Test grün; Tenant-Isolation geprüft.
6. Signal-Stores strukturgleich zum MobX-Original (`store-parity-check`), Vitest je Action (L2).
7. E2E-Specs dieses Pakets grün gegen Original **und** funk. (Dual-Target, Pflichtszenarien 15 §3.9.3).
8. Visual-/DOM-/a11y-Prüfpunkte der betroffenen Screens (09 §4.14, 15 §3.10.2) innerhalb der Schwellwerte 15 §3.10.3 (Chromium); i18n-Schlüssel nur aus den Original-Locales (de/en).
9. `ce-coverage-check --ids CE-AUTH-015` grün (Mindestebenen 15 Anhang B).

**Testumfang**

- Pflicht-Ebenen (aus 15 Anhang B): L1, L2, L3, L5, L7, L8
- Testprojekte: `Funk.Identity.Tests`
- E2E-Specs (`frontend/apps/e2e/`): `web/auth/keycloak-login.spec.ts`
- L8 Visual `keycloak-login` (Chromium), G-BRAND über das Theme.

### WP-I0-201 – Erweiterungspunkt C3: Event-Katalog, Outbox/Inbox-Gerüst, Consumer-Registrierung, Recurring Jobs, Queues

| Merkmal | Wert |
|---|---|
| Inkrement | I0 |
| Typ (DoD 15 §3.15.3) | X – Erweiterungspunkt 🧱 |
| Größe | M |
| parallelisierbar | ja |
| Abhängigkeiten | WP-I0-104 |
| CE-IDs | – (keine; Erweiterungspunkt) |
| Andockstelle | 01 §1.4 C3; 16 §5.11; 16 §4.6 Zeile „Event-Katalog …“ (Träger CE-OPS-021/-022, erste Events CE-WS-001/CE-PRJ-004) |

**Ziel.** Versionierter Event-Katalog (`funk.<aggregat>.<ereignis>.v1`, `IIntegrationEvent`, `EventType`-Schema) mit Snapshot-Test, transaktionale Outbox und Inbox, `IEventConsumer`-Registrierung, `IRecurringJobRegistry`, benannte Queues (`default`, `notifications`, `emails`, `webhooks`, `exports`, `maintenance`, `realtime`, `live`, `indexing`; Paket-Queues reserviert), `EventContext` mit Akteur, Herkunft und Kausaltiefe (> 5 verworfen).

**Betroffene Module/Libs in `funk.`**

- Backend: `src/building-blocks/Funk.BuildingBlocks.Messaging` (Outbox, Inbox, JobQueue, Scheduler-Gerüst, EventCatalog)
- Backend: `src/modules/*/Funk.*.Contracts/Events/`
- Backend: `src/building-blocks/Funk.BuildingBlocks.Testing/Extensions/FakeEventConsumer.cs`
- Backend: `tests/Funk.Worker.Tests`

**Referenzdokumente**

- Architektur: 16 §1.4 Zeile I0, §3.2.4, §3.2.5, §5.11
- Architektur: 06 §3.2–§3.8, §5.1–§5.4, D06-ADR-01…-07, -21
- Architektur: 01 §1.4 Zeile C3

**Akzeptanzkriterien**

1. Event-Katalog-Snapshot-Test schlägt bei jeder nicht additiven Änderung fehl (Typname ↔ Klasse eindeutig).
2. Fake-Consumer aus `Funk.BuildingBlocks.Testing/Extensions` empfängt `funk.workspace.created.v1` ohne CE-Änderung (DoD Typ X).
3. Event mit `CausationDepth > 5` wird verworfen, Metrik `funk.outbox.dropped{reason="causation_depth"}` steigt.
4. Contract (Interface/Schema/Token) + CE-Default-Implementierung; Eintrag in `tests/extension-points.yaml`.
5. Test „CE-Default = Original-Verhalten“ (Contract-Replay unverändert grün).
6. Test mit Fake-Erweiterung aus `Funk.BuildingBlocks.Testing/Extensions` bzw. `provideFakeExtensions()` beweist Erweiterbarkeit ohne CE-Änderung (DoD Typ X).

**Testumfang**

- L1/L3 Outbox/Inbox/Kausaltiefe, Typ-X-Test mit Fake-Consumer.

### WP-I0-202 – Erweiterungspunkt B1/A2: ScopeRef, ScopeLevel, IScopeResolver, IScopeAncestorContributor, RouterStore.teamspaceId

| Merkmal | Wert |
|---|---|
| Inkrement | I0 |
| Typ (DoD 15 §3.15.3) | X – Erweiterungspunkt 🧱 |
| Größe | S |
| parallelisierbar | ja |
| Abhängigkeiten | WP-I0-104, WP-I0-105 |
| CE-IDs | – (keine; Erweiterungspunkt) |
| Andockstelle | 01 §1.4 B1/A2; 16 §3.3.0 E-20; 16 §4.6 (Träger CE-WS-001, CE-PRJ-006) |

**Ziel.** Sichtbarkeitsebenen `ScopeLevel` (Workspace│Teamspace│Project) und `ScopeRef` als einheitlicher Scope-Typ; `IScopeResolver` (CE: Workspace/Project) und `IScopeAncestorContributor` (E-20, CE ohne Beiträge); Frontend `SCOPE_LEVELS` und `RouterStore.teamspaceId` (wie Original).

**Betroffene Module/Libs in `funk.`**

- Backend: `src/building-blocks/Funk.BuildingBlocks/Scoping/`
- Backend: `src/modules/extensions/Teamspaces/Funk.Teamspaces.Contracts` (Platzhalter, R10)
- Frontend: `frontend/libs/web/extensions/src/scope.ts`
- Frontend: `frontend/libs/web/core/router.store.ts` (`teamspaceId`)

**Referenzdokumente**

- Architektur: 16 §5.4, §3.3.0 E-20
- Architektur: 01 §1.4 Zeile B1, §5.5
- Architektur: 02 §3.5

**Akzeptanzkriterien**

1. `ScopeRef`-Gleichheit, Serialisierung und Vorfahrenkette (Project → Workspace) per Unit-Test; Fake-`IScopeAncestorContributor` ergänzt eine Teamspace-Ebene ohne CE-Änderung.
2. Contract (Interface/Schema/Token) + CE-Default-Implementierung; Eintrag in `tests/extension-points.yaml`.
3. Test „CE-Default = Original-Verhalten“ (Contract-Replay unverändert grün).
4. Test mit Fake-Erweiterung aus `Funk.BuildingBlocks.Testing/Extensions` bzw. `provideFakeExtensions()` beweist Erweiterbarkeit ohne CE-Änderung (DoD Typ X).

**Testumfang**

- L1 Scoping, Typ-X-Test (Fake-Contributor), L2 RouterStore.

### WP-I0-203 – Erweiterungspunkt E5: Permission-Katalog, roles/role_permissions, role_id, ISystemRoleGrantContributor, PermissionService

| Merkmal | Wert |
|---|---|
| Inkrement | I0 |
| Typ (DoD 15 §3.15.3) | X – Erweiterungspunkt 🧱 |
| Größe | M |
| parallelisierbar | ja |
| Abhängigkeiten | WP-I0-104, WP-I0-105 |
| CE-IDs | – (keine; Erweiterungspunkt) |
| Andockstelle | 01 §1.4 E5; 16 §3.3.0 E-09; 16 §4.6 (Träger CE-WS-008, CE-WS-012) |

**Ziel.** Permission-Katalog `Permission(Key, Scope, ApiScope)` mit den 258 Keys aus 05 Anhang A (Generator `Funk.PermissionGen`), Tabelle `roles` mit System-Rollen Admin 20 / Member 15 / Guest 5 (`is_system`), `role_permissions`, Mitgliedschaften mit `role_id` (API liefert weiter `role: 20/15/5`), `IRoleDefinitionProvider`, `IVisibilityFilter<T>` + `CompositeVisibilityFilter<T>`, `ISystemRoleGrantContributor` (E-09), `ReservedPermissionKeys`; Frontend-Fassade `PermissionService.allowPermissions(...)` + Token `PERMISSION_EVALUATOR`.

**Betroffene Module/Libs in `funk.`**

- Backend: `src/modules/Authorization/Funk.Authorization`, `Funk.Authorization.Contracts`
- Backend: `src/tools/Funk.PermissionGen` (erzeugt `tests/security/permission-matrix.yaml`)
- Backend: `src/data/Funk.Data/Entities/Authorization/`
- Frontend: `frontend/libs/web/core/permissions`

**Referenzdokumente**

- Architektur: 05 §3.13, §3.14, §5.8, Anhang A/B
- Architektur: 02 §3.6
- Architektur: 16 §5.6, §3.2.1
- Architektur: 01 §1.4 Zeile E5
- Architektur: 17 ABG-036…ABG-038, Z-09 (HARM-00/03/04/06 angenommen)

**Akzeptanzkriterien**

1. Generator erzeugt aus `_data/05-permission-matrix.json` Deskriptoren und Matrix-Datei deterministisch (`--check` in G1).
2. `SystemRoleProvider` bildet die Original-Rollenlogik inkl. WS-Admin-Override (HARM-00) ab; Matrix-Test für die I0-Endpunkte 100 %.
3. Fake-`ISystemRoleGrantContributor` ergänzt einen neuen Key für Member ohne Änderung an `SystemRoleProvider` (Typ X).
4. Frontend prüft Rechte ausschließlich über `PermissionService` (ESLint-Regel verbietet direkte Rollenvergleiche).
5. Contract (Interface/Schema/Token) + CE-Default-Implementierung; Eintrag in `tests/extension-points.yaml`.
6. Test „CE-Default = Original-Verhalten“ (Contract-Replay unverändert grün).
7. Test mit Fake-Erweiterung aus `Funk.BuildingBlocks.Testing/Extensions` bzw. `provideFakeExtensions()` beweist Erweiterbarkeit ohne CE-Änderung (DoD Typ X).

**Testumfang**

- L1 Evaluator, L3 Matrix-Tests (I0-Routen), Typ-X-Test, L2 `PermissionService` gegen Original-Store-Fixtures.

### WP-I0-204 – Erweiterungspunkt H1/E3: FunkPrincipal, Policy-Scheme Cookies│ApiKey│Bearer, users.is_bot, Provisioning-Kette

| Merkmal | Wert |
|---|---|
| Inkrement | I0 |
| Typ (DoD 15 §3.15.3) | X – Erweiterungspunkt 🧱 |
| Größe | M |
| parallelisierbar | ja |
| Abhängigkeiten | WP-I0-104, WP-I0-907 |
| CE-IDs | – (keine; Erweiterungspunkt) |
| Andockstelle | 01 §1.4 E3/H1; 16 §4.6 (Träger CE-AUTH-001/-024/-025, CE-AUTH-028/-029) |

**Ziel.** `FunkPrincipal` mit `Kind` (User│ApiKey│App│Bot), `Groups` (Keycloak-`groups`-Claim) und `ApiScopes`; Authentifizierungs-Policy-Scheme `Cookies│ApiKey│Bearer` mit vorkonfiguriertem, per `Funk:Auth:BearerEnabled=false` deaktiviertem Keycloak-JWT (Audience `funk-api`); Feld `users.is_bot`; `IUserProvisioningStep`-Kette mit freien `Order`-Slots (750/760 für E3) und `ProvisioningOrder`-Konstanten.

**Betroffene Module/Libs in `funk.`**

- Backend: `src/building-blocks/Funk.BuildingBlocks/Security/FunkPrincipal.cs`
- Backend: `src/building-blocks/Funk.BuildingBlocks.Web/Authentication/` (Policy-Scheme)
- Backend: `src/modules/Identity/Funk.Identity.Contracts/Provisioning/`
- Backend: `src/modules/extensions/Apps/Funk.Apps.Contracts` (Platzhalter, R10)

**Referenzdokumente**

- Architektur: 05 §3.7.3, §3.12.1, §5.6, §5.7, §6.2
- Architektur: 16 §5.7, §5.8
- Architektur: 01 §1.4 Zeilen E3, H1

**Akzeptanzkriterien**

1. Bearer-Schema ist registriert, liefert mit `BearerEnabled=false` immer 401 und mit `true` (Testprofil) einen gültigen Prinzipal aus einem Keycloak-Token (Typ X).
2. Fake-`IUserProvisioningStep` (Order 750) läuft beim Login ohne CE-Änderung und sieht `Groups`.
3. Contract (Interface/Schema/Token) + CE-Default-Implementierung; Eintrag in `tests/extension-points.yaml`.
4. Test „CE-Default = Original-Verhalten“ (Contract-Replay unverändert grün).
5. Test mit Fake-Erweiterung aus `Funk.BuildingBlocks.Testing/Extensions` bzw. `provideFakeExtensions()` beweist Erweiterbarkeit ohne CE-Änderung (DoD Typ X).

**Testumfang**

- L1 Principal-Mapping, L3 Schemata, Typ-X-Tests (Bearer an/aus, Fake-Provisioning-Step).

### WP-I0-205 – Erweiterungspunkt F1: Oberfläche Integrations, Webhook-Ingress, Verifier-Registry, integration_connections, Platzhalter-Contracts

| Merkmal | Wert |
|---|---|
| Inkrement | I0 |
| Typ (DoD 15 §3.15.3) | X – Erweiterungspunkt 🧱 |
| Größe | M |
| parallelisierbar | ja |
| Abhängigkeiten | WP-I0-104, WP-I0-201 |
| CE-IDs | – (keine; Erweiterungspunkt) |
| Andockstelle | 01 §1.4 F1/F2; 16 §3.3.0 E-13 (Teil `integration_connections`), E-25; 16 §4.6 (Träger CE-OPS-021, CE-OPS-022) |

**Ziel.** Oberfläche `Integrations` mit `POST /api/integrations/{provider}/webhooks/{connection_id}/` (404 ohne registrierten Verifier), `IWebhookSignatureVerifier`-Registry, `IWebhookIngress` (E-25, Roh-Body, case-insensitive Header-Map), `IWebhookEventHandler`, `IIntegrationProvider`, Inbox-Idempotenz, leere Tabelle `integration_connections`, reservierte Data-Protection-Purposes (`Funk.Integrations.ConnectionSecret.v1`, `Funk.Forgejo.UserToken.v1`), Rate-Limit-Policy `integration_webhook`, Platzhalter-Projekte `Funk.Integrations.Contracts`, `Funk.Forgejo.Contracts`, `Funk.Forgejo.Client` (nur `IForgejoClient` + DTOs), `Funk.Properties.Contracts`.

**Betroffene Module/Libs in `funk.`**

- Backend: `src/building-blocks/Funk.BuildingBlocks.Web/Integrations/`
- Backend: `src/modules/extensions/{Integrations,Forgejo,Properties}/`
- Backend: `src/data/Funk.Data/Entities/Integrations/IntegrationConnection.cs`
- Backend: `src/building-blocks/Funk.BuildingBlocks.Testing/Extensions/FakeWebhookSignatureVerifier.cs`

**Referenzdokumente**

- Architektur: 16 §3.4.1–§3.4.3, §5.10, D16-ADR-09, -10, -13
- Architektur: 04 §4.23
- Architektur: 02 §3.3.1 (Oberflächen), §3.13
- Architektur: 01 §1.4 Zeile F1

**Endpunkte (Katalog 04, `architecture/_data/endpoints.json`; 1 registriert)**

| EP | Methode | Pfad | Oberfläche | Handler | Permission | Inkr. 04 | CE-IDs |
|---|---|---|---|---|---|---|---|
| EP-0729 (vorab) | POST | `/api/integrations/{provider}/webhooks/{connection_id}/` | Integrations | IntegrationWebhookEndpoints.IntegrationWebhookEndpoint → IWebhookIngress | (Signatur, IWebhookSignatureVerifier) | I0 | CE-OPS-018 |

**Akzeptanzkriterien**

1. Ohne Verifier: 404; mit Fake-Verifier und Fake-Handler wird eine Test-Delivery idempotent (zweite Zustellung derselben Delivery-ID ohne Wirkung) verarbeitet – ohne CE-Änderung (Typ X).
2. Architekturtest R10: Platzhalter-Projekte enthalten nur Interfaces, DTOs, Enums, Konstanten.
3. Contract (Interface/Schema/Token) + CE-Default-Implementierung; Eintrag in `tests/extension-points.yaml`.
4. Test „CE-Default = Original-Verhalten“ (Contract-Replay unverändert grün).
5. Test mit Fake-Erweiterung aus `Funk.BuildingBlocks.Testing/Extensions` bzw. `provideFakeExtensions()` beweist Erweiterbarkeit ohne CE-Änderung (DoD Typ X).

**Testumfang**

- L3 Ingress (Signatur falsch → 401, Roh-Body unverändert), Typ-X-Test, L0 R10/R11.

### WP-I0-206 – Erweiterungspunkt F2: Forgejo-Container, Keycloak-Client funk-forgejo, forgejo-init, SSO-Smoke

| Merkmal | Wert |
|---|---|
| Inkrement | I0 |
| Typ (DoD 15 §3.15.3) | X – Erweiterungspunkt 🧱 |
| Größe | S |
| parallelisierbar | ja |
| Abhängigkeiten | WP-I0-102, WP-I0-108 |
| CE-IDs | – (keine; Erweiterungspunkt) |
| Andockstelle | 01 §1.4 F2; 16 §3.4.8 (Zeile I0) |

**Ziel.** Forgejo (gepinnter LTS-Tag) läuft als Aspire-Ressource mit eigener Datenbank auf dem gemeinsamen PostgreSQL, Bootstrap-Skript und `Funk.Tools.ForgejoInit` (Admin, OAuth2-App mit beiden Redirect-URIs, Test-Repos); Anmeldung an Forgejo über denselben Keycloak (Client `funk-forgejo`, Auth-Source `keycloak`). Activity-Typen für Branch/Commit/PR sind im Activity-Katalog reserviert.

**Betroffene Module/Libs in `funk.`**

- Backend: `src/tools/Funk.Tools.ForgejoInit`
- Backend: `deploy/forgejo/bootstrap/forgejo-bootstrap.sh`
- Backend: `deploy/keycloak/config/20-forgejo-client.json`

**Referenzdokumente**

- Architektur: 14 §3.4
- Architektur: 16 §3.4.7, §3.4.8
- Architektur: 00 ADR-007
- Architektur: 17 ABG-003, Z-13

**Akzeptanzkriterien**

1. L6 `ForgejoSsoSmokeTests`: derselbe Keycloak-Testbenutzer meldet sich an funk. und an Forgejo an; Forgejo-Benutzer und funk.-Benutzer tragen dieselbe Keycloak-Identität.
2. Forgejo-LTS-Tag ist gepinnt (O-04) und im Airgap-Image-Inventar `deploy/airgap/images.yaml` eingetragen.
3. Contract (Interface/Schema/Token) + CE-Default-Implementierung; Eintrag in `tests/extension-points.yaml`.
4. Test „CE-Default = Original-Verhalten“ (Contract-Replay unverändert grün).
5. Test mit Fake-Erweiterung aus `Funk.BuildingBlocks.Testing/Extensions` bzw. `provideFakeExtensions()` beweist Erweiterbarkeit ohne CE-Änderung (DoD Typ X).

**Testumfang**

- L6 Forgejo-SSO-Smoke im Profil `test`.

### WP-I0-207 – Erweiterungspunkt H6: SignalR-Hub /live/events/, Gruppen, IRealtimePublisher, IRealtimeGroupAuthorizer, LiveEventsService

| Merkmal | Wert |
|---|---|
| Inkrement | I0 |
| Typ (DoD 15 §3.15.3) | X – Erweiterungspunkt 🧱 |
| Größe | S |
| parallelisierbar | ja |
| Abhängigkeiten | WP-I0-107, WP-I0-105, WP-I0-201 |
| CE-IDs | – (keine; Erweiterungspunkt) |
| Andockstelle | 01 §1.4 H6; 16 §3.3.0 E-22; 16 §4.6 (Walking Skeleton, `RealtimeSmokeTests`) |

**Ziel.** Modul `Funk.RealtimeEvents` (+ `.Contracts`) im Host `Funk.Realtime`: Hub `/live/events/` mit Gruppen `ws:{id}`, `project:{id}`, `user:{id}`, `IRealtimeGroupAuthorizer` (E-22, CE-Präfixe), `IRealtimePublisher` mit `QueuedRealtimePublisher` (Api/Worker) und `HubRealtimePublisher` (Realtime-Host), Queue `live`; Frontend `LiveEventsService` + Token `LIVE_EVENT_HANDLERS` (ohne Handler).

**Betroffene Module/Libs in `funk.`**

- Backend: `src/modules/RealtimeEvents/Funk.RealtimeEvents`, `Funk.RealtimeEvents.Contracts`
- Frontend: `frontend/libs/web/core/live-events`

**Referenzdokumente**

- Architektur: 07 §3.16, §5.11
- Architektur: 06 §3.12, D06-ADR-12
- Architektur: 16 §5.12, §3.3.0 E-22
- Architektur: 17 ABG-106, ABG-112

**Endpunkte (Katalog 04, `architecture/_data/endpoints.json`; 1 registriert)**

| EP | Methode | Pfad | Oberfläche | Handler | Permission | Inkr. 04 | CE-IDs |
|---|---|---|---|---|---|---|---|
| EP-0414 (vorab) | GET | `/live/events/` | Live | LiveEventsHub.LiveEventsHub (SignalR, nur WebSockets) | (Session-Cookie) | I0 | CE-NOTIF-004 |

**Akzeptanzkriterien**

1. `RealtimeSmokeTests` (Hub-Teil): angemeldeter Benutzer tritt `user:{id}` bei, fremde Gruppen werden abgewiesen; Fake-Gruppen-Präfix per Fake-Authorizer ohne CE-Änderung (Typ X).
2. Contract (Interface/Schema/Token) + CE-Default-Implementierung; Eintrag in `tests/extension-points.yaml`.
3. Test „CE-Default = Original-Verhalten“ (Contract-Replay unverändert grün).
4. Test mit Fake-Erweiterung aus `Funk.BuildingBlocks.Testing/Extensions` bzw. `provideFakeExtensions()` beweist Erweiterbarkeit ohne CE-Änderung (DoD Typ X).

**Testumfang**

- L6 Hub-Smoke, Typ-X-Test, L2 `LiveEventsService` (Reconnect).

### WP-I0-208 – Erweiterungspunkte Querschnitt: Reservierungen + Kollisionstests, R11/R12, Frontend-Registries (Routen, Sidebar, Admin), Fake-Extensions

| Merkmal | Wert |
|---|---|
| Inkrement | I0 |
| Typ (DoD 15 §3.15.3) | X – Erweiterungspunkt 🧱 |
| Größe | M |
| parallelisierbar | ja |
| Abhängigkeiten | WP-I0-104, WP-I0-105 |
| CE-IDs | – (keine; Erweiterungspunkt) |
| Andockstelle | 16 §1.4 Zeile I0 (Reservierungen, Registries); 16 §4.6 „Bewusst ohne Träger-CE-ID“ (CE-OPS-022) |

**Ziel.** Reservierte Permission-Namensräume, Routen-Präfixe, Activity-Felder, Event-Namensräume, Queues und Suche/AI-Bezeichner (`Reservations.cs`, `docs/extensions/reservations.yaml`) mit `ReservationCollisionTests`/`RouteReservationTests` (E-17); Architekturregeln R11/R12; Inventar `tests/extension-points.yaml`; Frontend-Registries `ROUTE_EXTENSIONS` + `mergeRoutes`, `SIDEBAR_ITEMS` (statisch), `ADMIN_SETTINGS_PAGES`, `ADMIN_ROUTE_EXTENSIONS`, `ADMIN_HEADER_SEGMENT_LABELS`, `APP_RAIL_ENABLED`, `provideWebExtensions()`/`provideAdminExtensions()`/`provideSpaceExtensions()`; Test-Erweiterungen `provideFakeExtensions()`, `provideFakeAdminExtensions()`, `provideFakeSpaceExtensions()`; Modulkatalog `FunkModuleCatalog`.

**Betroffene Module/Libs in `funk.`**

- Backend: `src/building-blocks/Funk.BuildingBlocks/Extensions/Reservations.cs`
- Backend: `src/hosts/Funk.Hosting/FunkModuleCatalog.cs`
- Backend: `tests/Funk.ArchitectureTests/{ReservationCollisionTests,RouteReservationTests,ExtensionPointInventoryTests}.cs`
- Frontend: `frontend/libs/web/extensions/src/`
- Frontend: `frontend/libs/admin/extensions`, `frontend/libs/space/extensions`
- Frontend: `frontend/libs/shared/cdk/src/extensions/` (`RouteExtension<K>`, `mergeRoutes`, `injectRegistry`)
- Frontend: `frontend/tools/extension-registry-check`

**Referenzdokumente**

- Architektur: 16 §3.1, §3.2, §3.3.0 E-17, D16-ADR-03, -04, -15
- Architektur: 08 §6.1–§6.5
- Architektur: 01 §6.4
- Architektur: 17 ABG-023, ABG-032, ABG-135

**Akzeptanzkriterien**

1. Kollisionstests schlagen fehl, wenn eine CE-Route, ein Permission-Key oder eine Queue einen reservierten Namen benutzt.
2. Eine Fake-Route über `ROUTE_EXTENSIONS` und ein Fake-Sidebar-Eintrag erscheinen ohne Änderung an CE-Dateien (Typ X, Vitest + Playwright).
3. `ExtensionPointInventoryTests` und `extension-registry-check` gleichen `tests/extension-points.yaml` mit dem Code ab (jede P-Andockstelle aus 16 §1.4 hat Inkrement und Test).
4. Contract (Interface/Schema/Token) + CE-Default-Implementierung; Eintrag in `tests/extension-points.yaml`.
5. Test „CE-Default = Original-Verhalten“ (Contract-Replay unverändert grün).
6. Test mit Fake-Erweiterung aus `Funk.BuildingBlocks.Testing/Extensions` bzw. `provideFakeExtensions()` beweist Erweiterbarkeit ohne CE-Änderung (DoD Typ X).

**Testumfang**

- L0 Architektur-/Inventartests, Typ-X-Tests Frontend.

### WP-I0-900 – Spike S0 – Toolchain & Walking-Skeleton-Gerüst

| Merkmal | Wert |
|---|---|
| Inkrement | I0 |
| Typ (DoD 15 §3.15.3) | S – Spike |
| Größe | M |
| parallelisierbar | nein |
| Abhängigkeiten | WP-I0-101 |
| CE-IDs | – (keine; Baustein/Spike/Abnahme) |

**Ziel.** Nachweis, dass Aspire 13 (inkl. Keycloak-Hosting-Preview und JavaScript-Hosting), .NET 10, EF Core 10/Npgsql 10, Angular 22 und pnpm gemeinsam tragen; alle mit ⚠ markierten Versionen werden per Paket-Metadaten bestätigt und gepinnt. Der Spike gatet alle übrigen Arbeitspakete.

**Betroffene Module/Libs in `funk.`**

- Backend: `src/hosts/Funk.AppHost` (Prototyp)
- Backend: `Directory.Packages.props` (Pins aus 01 §8)
- Backend: `docs/spikes/S0-ergebnis.md`
- Frontend: `frontend/pnpm-workspace.yaml` (Catalog-Pins)
- Frontend: `frontend/libs/shared/{types,constants,utils,i18n}` (Quelltext-Kopie, TS-6-Kompilierprobe)

**Referenzdokumente**

- Architektur: 01 §9 Zeile S0
- Architektur: 01 §8 (Library-Liste)
- Architektur: 02 §1.3 (Mediator, DbContext)
- Architektur: 17 Z-01, Z-02, Z-15, Z-106
- Architektur: 08 O-D08-01, O-D08-05, O-D08-06
- Architektur: 14 O-14-04, O-14-11

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- `packages/types`, `packages/constants`, `packages/utils`, `packages/i18n` (Kompilierprobe)
- `pnpm-lock.yaml` (Original-Pins)

**Akzeptanzkriterien**

1. `aspire run` startet alle I0-Ressourcen aus 14 §3.2 (Profil `dev`), Gateway liefert den Angular-Dev-Server same-origin.
2. Alle ⚠-Versionen aus 01 §8 sind per NuGet-/npm-Metadaten bestätigt und in `Directory.Packages.props` bzw. `pnpm-workspace.yaml` gepinnt; Lizenz-Gate grün, Lizenzen in `NOTICE`.
3. `libs/shared/{types,constants,utils,i18n}` kompilieren unter TypeScript 6.0 ohne Logikänderung; Liste der mechanischen Anpassungen in `docs/spikes/S0-ergebnis.md` (O-10).
4. EF-10-Smoke-Test `PgvectorSmokeTests` (Pgvector.EntityFrameworkCore 0.3.x) und SignalR-Backplane-Smoke mit StackExchange.Redis 3.x grün (R-D03-01).
5. Mediator 3: `internal`-Handler aus Modul-Assemblies werden über `InternalsVisibleTo` im Host registriert (Z-01, AK-24 aus 02) – sonst Fallback „Handler public“ (O-D02-09) dokumentiert und aktiviert.
6. Signal-Forms-Probe (Create-Workspace-Formular mit `[plFormField]`, O-D08-01) und Vitest-`runnerConfig` (Z-02) funktionieren; Bundle-Budget des Original-Builds gemessen (O-D08-05).
7. Abbruch-/Fallback-Entscheidung nach 01 §9 dokumentiert; Messungen als dauerhafte Tests im Repo (DoD Typ S).
8. Ergebnisbericht `docs/spikes/<Spike>-ergebnis.md` mit Messwerten; Messungen als automatisierte Tests, die danach dauerhaft in G4 laufen (DoD Typ S).
9. Bei Abbruchkriterium: Fallback aus 01 §9 ohne weitere Diskussion aktiviert (außer ADR-000…009 betroffen → Auftraggeber).

**Testumfang**

- Messungen als automatisierte Tests: `AppHostSmokeTests`, `PgvectorSmokeTests`, `MediatorRegistrationTests`, `OptionalJsonSourceGenTests` (R-D02-08).

### WP-I0-901 – Spike S1 – YDotNet + Hocuspocus-Protokoll in .NET

| Merkmal | Wert |
|---|---|
| Inkrement | I0 |
| Typ (DoD 15 §3.15.3) | S – Spike |
| Größe | L |
| parallelisierbar | ja |
| Abhängigkeiten | WP-I0-900, WP-I0-107 |
| CE-IDs | – (keine; Baustein/Spike/Abnahme) |

**Ziel.** Nachweis, dass ein .NET-Server mit YDotNet den unveränderten `@hocuspocus/provider` 2.15.2 bedient (Auth, Sync, Updates, Awareness, Stateless, Close-Codes, Titel-Fragment, Persistenz, Mehrinstanz über Valkey, Last/Soak). Gatet I4.

**Betroffene Module/Libs in `funk.`**

- Backend: `src/modules/Collaboration/Funk.Collaboration.Protocol` (Prototyp)
- Backend: `tests/Funk.Collaboration.Tests/Browser/ProviderConformanceTests.cs`
- Backend: `docs/spikes/S1-ergebnis.md`

**Referenzdokumente**

- Architektur: 01 §9 Zeile S1
- Architektur: 07 §3.3–§3.10, §7.3 (P-01…P-30), §7.6 S1
- Architektur: 17 Z-101, Z-109

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- `apps/live/src/hocuspocus.ts`
- `apps/live/src/extensions/`
- `apps/live/src/types/admin-commands.ts`
- `packages/editor/src/core/constants/document-collaborative-events.ts`

**Akzeptanzkriterien**

1. Alle Erfolgskriterien aus 01 §9 S1 (u. a. 50 Editoren p95 < 150 ms, 1 h Soak < 5 % Speicherwachstum, zwei Instanzen konvergieren über Valkey) als automatisierte Tests grün – oder Fallback-Kette (y-websocket → YDotNet-Fork → Auftraggeber) aktiviert und dokumentiert.
2. Awareness-Relay funktioniert; damit wird `collaboration-cursor` in I4 aktiviert (Z-109).
3. Ergebnisbericht `docs/spikes/<Spike>-ergebnis.md` mit Messwerten; Messungen als automatisierte Tests, die danach dauerhaft in G4 laufen (DoD Typ S).
4. Bei Abbruchkriterium: Fallback aus 01 §9 ohne weitere Diskussion aktiviert (außer ADR-000…009 betroffen → Auftraggeber).

**Testumfang**

- Browser-Protokolltests mit Original-Provider (Playwright), Last LT-16-Vorstufe.

### WP-I0-902 – Spike S2 – Yjs → ProseMirror-JSON → HTML (und HTML → JSON) ohne Node

| Merkmal | Wert |
|---|---|
| Inkrement | I0 |
| Typ (DoD 15 §3.15.3) | S – Spike |
| Größe | L |
| parallelisierbar | ja |
| Abhängigkeiten | WP-I0-900 |
| CE-IDs | – (keine; Baustein/Spike/Abnahme) |

**Ziel.** Nachweis, dass `Funk.Documents` Ausgabe-Gleichheit mit `@tiptap/html`/`y-prosemirror` erreicht (Korpus ≥ 200 Dokumente, HTML ≥ 99 % byte-gleich nach Normalisierung, JSON 100 % strukturgleich, ≥ 200 Dok./s). HTML/JSON-Teil gatet I2, Yjs-Teil gatet I4.

**Betroffene Module/Libs in `funk.`**

- Backend: `src/documents/Funk.Documents` (Prototyp)
- Backend: `tests/Funk.Documents.Tests/Golden/`
- Backend: `tools/golden/generate.mjs` (Node nur zur Entwicklungszeit)
- Backend: `docs/spikes/S2-ergebnis.md`

**Referenzdokumente**

- Architektur: 01 §9 Zeile S2
- Architektur: 07 §3.12, §3.13, §7.6 S2
- Architektur: 10 §3.2
- Architektur: 17 Z-102

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- `packages/editor/src/core/extensions/`
- `apps/live/src/lib/`
- `packages/editor/src/core/helpers/yjs-utils.ts`

**Akzeptanzkriterien**

1. Erfolgskriterien 01 §9 S2 erreicht oder Fallback F-S2-1 (Jint mit gebündeltem `@tiptap/html`) bzw. F-S2-2 dokumentiert aktiviert.
2. Typisierte Attribute aus Original-yjs werden korrekt gelesen (S2-K6a, O-07-01).
3. Ergebnisbericht `docs/spikes/<Spike>-ergebnis.md` mit Messwerten; Messungen als automatisierte Tests, die danach dauerhaft in G4 laufen (DoD Typ S).
4. Bei Abbruchkriterium: Fallback aus 01 §9 ohne weitere Diskussion aktiviert (außer ADR-000…009 betroffen → Auftraggeber).

**Testumfang**

- L4 Golden-Korpus (G-DOC), Durchsatz-Benchmark als Test.

### WP-I0-903 – Spike S3 – PDF-Export mit PDFsharp/MigraDoc

| Merkmal | Wert |
|---|---|
| Inkrement | I0 |
| Typ (DoD 15 §3.15.3) | S – Spike |
| Größe | M |
| parallelisierbar | ja |
| Abhängigkeiten | WP-I0-900 |
| CE-IDs | – (keine; Baustein/Spike/Abnahme) |

**Ziel.** Nachweis, dass PDFsharp/MigraDoc 6.2.4 (MIT) die Optik von `apps/live/src/lib/pdf` erreicht (20 Referenzseiten ≤ 2 % Pixelabweichung bei 150 dpi, Text extrahierbar, < 3 s für 20 Seiten). Gatet CE-PAGE-011 (I4).

**Betroffene Module/Libs in `funk.`**

- Backend: `src/documents/Funk.Documents.Pdf` (Prototyp)
- Backend: `tests/Funk.Documents.Pdf.Tests`
- Backend: `docs/spikes/S3-ergebnis.md`

**Referenzdokumente**

- Architektur: 01 §9 Zeile S3, O-09
- Architektur: 07 §3.15, §7.6 S3
- Architektur: 17 Z-103

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- `apps/live/src/lib/pdf/`
- `apps/live/tests/`
- `apps/web/core/components/editor/pdf/document.tsx`

**Akzeptanzkriterien**

1. Erfolgskriterien 01 §9 S3 erreicht oder Fallback SkiaSharp `SKDocument` aktiviert; Emoji außerhalb der BMP und Surrogatpaare korrekt (S3-K6).
2. Lizenz/Plattform des Test-Rasterizers geklärt (Docnet.Core vs. PDFtoImage, O-07-04).
3. Ergebnisbericht `docs/spikes/<Spike>-ergebnis.md` mit Messwerten; Messungen als automatisierte Tests, die danach dauerhaft in G4 laufen (DoD Typ S).
4. Bei Abbruchkriterium: Fallback aus 01 §9 ohne weitere Diskussion aktiviert (außer ADR-000…009 betroffen → Auftraggeber).

**Testumfang**

- L4 G-PDF (Text + Raster-Diff), 21 Fälle aus `apps/live/tests`.

### WP-I0-904 – Spike S4 – Kanban/Gantt-Drag-and-Drop in Angular (zoneless, virtualisiert)

| Merkmal | Wert |
|---|---|
| Inkrement | I0 |
| Typ (DoD 15 §3.15.3) | S – Spike |
| Größe | M |
| parallelisierbar | ja |
| Abhängigkeiten | WP-I0-900, WP-I0-105 |
| CE-IDs | – (keine; Baustein/Spike/Abnahme) |

**Ziel.** Nachweis, dass pragmatic-drag-and-drop zoneless mit Virtualisierung verhaltensgleich und performant läuft (1 000 Karten, 8 Spalten, ≥ 55 fps; Gantt verschieben/Größe/Reorder). Gatet I2.

**Betroffene Module/Libs in `funk.`**

- Frontend: `frontend/libs/shared/dnd` (Prototyp)
- Frontend: `docs/spikes/S4-ergebnis.md`

**Referenzdokumente**

- Architektur: 01 §9 Zeile S4
- Architektur: 08 §3.9, §5.12

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- `apps/web/core/components/issues/issue-layouts/kanban/`
- `apps/web/core/components/gantt-chart/`

**Akzeptanzkriterien**

1. Erfolgskriterien 01 §9 S4 als Playwright-Perf-Trace-Tests (LT-14/15) grün oder Fallback (eigene Pointer-Events für Gantt / CDK DragDrop für Kanban) dokumentiert.
2. Ergebnisbericht `docs/spikes/<Spike>-ergebnis.md` mit Messwerten; Messungen als automatisierte Tests, die danach dauerhaft in G4 laufen (DoD Typ S).
3. Bei Abbruchkriterium: Fallback aus 01 §9 ohne weitere Diskussion aktiviert (außer ADR-000…009 betroffen → Auftraggeber).

**Testumfang**

- Perf-Trace-Tests, Playwright-Szenarien des Originals.

### WP-I0-905 – Spike S5 – Editor-NodeViews in Angular mit Tiptap 2.27 (Schema-Freeze)

| Merkmal | Wert |
|---|---|
| Inkrement | I0 |
| Typ (DoD 15 §3.15.3) | S – Spike |
| Größe | M |
| parallelisierbar | ja |
| Abhängigkeiten | WP-I0-900, WP-I0-105 |
| CE-IDs | – (keine; Baustein/Spike/Abnahme) |

**Ziel.** Schnitt ED-0: Kern-Kopie per Codemod, Angular-Bindung, 8 NodeView-/Menü-Prototypen, Schema-Snapshot aller Varianten identisch zum Original, Visual der Editor-Seite ≤ 0,5 %, 5 000 Blöcke ohne Eingabe-Lag. Gatet I2 vollständig; das Kriterium „NodeView-Rendering stabil mit Yjs“ darf bis vor I4 nachgeliefert werden (ABG-114).

**Betroffene Module/Libs in `funk.`**

- Frontend: `frontend/libs/shared/editor/{core,angular-binding,components}` (Prototyp)
- Frontend: `frontend/libs/shared/editor/VERSIONS.json`
- Frontend: `frontend/tools/editor-port/` (Codemod `port-core.mjs`, Drift-Check)
- Frontend: `docs/spikes/S5-ergebnis.md`

**Referenzdokumente**

- Architektur: 01 §9 Zeile S5
- Architektur: 10 §1.5 (ED-0), §3.2–§3.5, §7.3
- Architektur: 17 ABG-114, Z-105

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- `packages/editor/src/`

**Akzeptanzkriterien**

1. Erfolgskriterien 10 §7.3 / 01 §9 S5 als Tests grün; G-SCHEMA (Varianten rich, lite, document, title) identisch.
2. DOM-Details (`FloatingOverlay`, `contentDOM`, Position `tiptap-core.css`) per DOM-Golden festgeschrieben (O-D10-05).
3. Ergebnisbericht `docs/spikes/<Spike>-ergebnis.md` mit Messwerten; Messungen als automatisierte Tests, die danach dauerhaft in G4 laufen (DoD Typ S).
4. Bei Abbruchkriterium: Fallback aus 01 §9 ohne weitere Diskussion aktiviert (außer ADR-000…009 betroffen → Auftraggeber).

**Testumfang**

- G-SCHEMA, DOM-Goldens, Visual Editor-Seite, Eingabe-Latenz-Test.

### WP-I0-906 – Spike S6 – Charts 1:1 mit D3 + Angular-SVG

| Merkmal | Wert |
|---|---|
| Inkrement | I0 |
| Typ (DoD 15 §3.15.3) | S – Spike |
| Größe | S |
| parallelisierbar | ja |
| Abhängigkeiten | WP-I0-105 |
| CE-IDs | – (keine; Baustein/Spike/Abnahme) |

**Ziel.** Nachweis, dass Bar (inkl. Lollipop), Pie (Center-Label), Area mit Vergleichslinie, Line, Radar, TreeMap und Cycle-Burndown pixelgleich (≤ 0,5 %) mit gleichem Tooltip-/Legend-Verhalten nachgebaut werden. Gatet I3.

**Betroffene Module/Libs in `funk.`**

- Frontend: `frontend/libs/shared/blocks/charts` (Prototyp)
- Frontend: `docs/spikes/S6-ergebnis.md`

**Referenzdokumente**

- Architektur: 01 §9 Zeile S6
- Architektur: 09 §3.12

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- `packages/blocks/src/charts/`
- `apps/web/core/components/core/sidebar/progress-chart.tsx`

**Akzeptanzkriterien**

1. Visual-Diff ≤ 0,5 % je Diagrammtyp (hell/dunkel) oder Fallback ECharts mit Abnahme durch den Auftraggeber.
2. Ergebnisbericht `docs/spikes/<Spike>-ergebnis.md` mit Messwerten; Messungen als automatisierte Tests, die danach dauerhaft in G4 laufen (DoD Typ S).
3. Bei Abbruchkriterium: Fallback aus 01 §9 ohne weitere Diskussion aktiviert (außer ADR-000…009 betroffen → Auftraggeber).

**Testumfang**

- L8 Galerie-Visual Charts.

### WP-I0-907 – Spike S7 – Keycloak-BFF, Logout, Theme, Forgejo-SSO

| Merkmal | Wert |
|---|---|
| Inkrement | I0 |
| Typ (DoD 15 §3.15.3) | S – Spike |
| Größe | M |
| parallelisierbar | ja |
| Abhängigkeiten | WP-I0-102 |
| CE-IDs | – (keine; Baustein/Spike/Abnahme) |

**Ziel.** Nachweis, dass der Keycloak-Aufbau ADR-008 vollständig erfüllt (PKCE je Client, HttpOnly-Session, RP- und Back-Channel-Logout < 2 s, Sperre wirkt sofort, JIT, Rolle → God Mode, optionaler Step-up, Theme-Visual ≤ 1 %, Forgejo-SSO). Gatet die Abnahme von I0.

**Betroffene Module/Libs in `funk.`**

- Backend: `docs/spikes/S7-ergebnis.md`

**Referenzdokumente**

- Architektur: 01 §9 Zeile S7, O-06, O-08
- Architektur: 05 §3.3–§3.8, §3.16
- Architektur: 14 §3.3, O-14-01, O-14-10
- Architektur: 17 Z-03, Z-14

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- `apps/web/core/components/account/auth-forms/`
- `apps/space/core/components/account/`

**Akzeptanzkriterien**

1. Erfolgskriterien 01 §9 S7 als automatisierte Tests (werden in WP-I0-001/-108 übernommen); `max_age=0`-Verhalten von Keycloak 26 geklärt (Z-03), Optionsnamen geklärt (Z-14), Kontokonsole-Deep-Links verifiziert (O-D05-01).
2. Ergebnisbericht `docs/spikes/<Spike>-ergebnis.md` mit Messwerten; Messungen als automatisierte Tests, die danach dauerhaft in G4 laufen (DoD Typ S).
3. Bei Abbruchkriterium: Fallback aus 01 §9 ohne weitere Diskussion aktiviert (außer ADR-000…009 betroffen → Auftraggeber).

**Testumfang**

- L6 Login/Logout/Back-Channel, Visual Theme-Prototyp.

### WP-I0-908 – Spike S8 – Objektspeicher-Kompatibilität (Presigned POST/GET, Upload-Modus)

| Merkmal | Wert |
|---|---|
| Inkrement | I0 |
| Typ (DoD 15 §3.15.3) | S – Spike |
| Größe | S |
| parallelisierbar | ja |
| Abhängigkeiten | WP-I0-102 |
| CE-IDs | – (keine; Baustein/Spike/Abnahme) |

**Ziel.** Matrix SeaweedFS, Garage, Ceph-RGW (optional), `pgsty/silo` für Presigned POST mit Bedingungen, Presigned GET mit Response-Overrides, HEAD, Copy, Batch-Delete, Zugriff über Gateway; Dateisystem-Provider im Proxy-Modus besteht dieselben Contract-Tests. Entscheidet O-03. Gatet I1.

**Betroffene Module/Libs in `funk.`**

- Backend: `src/platform/Funk.Platform.Storage` (Prototyp)
- Backend: `tests/Funk.Platform.Tests/Storage/ObjectStorageContractTests.cs`
- Backend: `docs/spikes/S8-ergebnis.md`

**Referenzdokumente**

- Architektur: 01 §9 Zeile S8, O-03
- Architektur: 14 §3.7.6
- Architektur: 05 §3.17.4

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- `apps/api/plane/settings/storage.py`
- `apps/api/plane/app/views/asset/v2.py`

**Akzeptanzkriterien**

1. Default-Backend und Upload-Modus (`Direct`/`Proxy`) festgelegt und in `docs/spikes/S8-ergebnis.md` begründet; `ObjectStorageContractTests` grün für das Default-Backend und den Dateisystem-Provider.
2. Ergebnisbericht `docs/spikes/<Spike>-ergebnis.md` mit Messwerten; Messungen als automatisierte Tests, die danach dauerhaft in G4 laufen (DoD Typ S).
3. Bei Abbruchkriterium: Fallback aus 01 §9 ohne weitere Diskussion aktiviert (außer ADR-000…009 betroffen → Auftraggeber).

**Testumfang**

- Storage-Contract-Tests je Backend.

### WP-I0-909 – Spike S9 – Work-Item-Listen-Performance & Filter-Engine (EF Core)

| Merkmal | Wert |
|---|---|
| Inkrement | I0 |
| Typ (DoD 15 §3.15.3) | S – Spike |
| Größe | M |
| parallelisierbar | ja |
| Abhängigkeiten | WP-I0-104 |
| CE-IDs | – (keine; Baustein/Spike/Abnahme) |

**Ziel.** Nachweis, dass EF Core die Filter-AST mit Gruppierung/Sub-Gruppierung/Pagination effizient übersetzt (50 000 Work Items: gruppiert p95 < 300 ms, Spreadsheet p95 < 200 ms, AND/OR/NOT p95 < 400 ms, kein Seq-Scan bei Projektfilter). Gatet I2.

**Betroffene Module/Libs in `funk.`**

- Backend: `src/modules/WorkItems/Funk.WorkItems/Query/` (Prototyp)
- Backend: `tests/load/` (Volumenprofil L)
- Backend: `docs/spikes/S9-ergebnis.md`

**Referenzdokumente**

- Architektur: 01 §9 Zeile S9
- Architektur: 02 §3.11, R-D02-01
- Architektur: 03 §3.4.5

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- `apps/api/plane/utils/grouper.py`
- `apps/api/plane/utils/paginator.py`
- `apps/api/plane/utils/filters/`

**Akzeptanzkriterien**

1. Zielwerte 01 §9 S9 als `SqlPlanAssertions`-/Lasttests grün oder Fallback (handgeschriebenes SQL mit Window-Functions) aktiviert.
2. Ergebnisbericht `docs/spikes/<Spike>-ergebnis.md` mit Messwerten; Messungen als automatisierte Tests, die danach dauerhaft in G4 laufen (DoD Typ S).
3. Bei Abbruchkriterium: Fallback aus 01 §9 ohne weitere Diskussion aktiviert (außer ADR-000…009 betroffen → Auftraggeber).

**Testumfang**

- L9 LT-01…LT-03-Vorstufe, SQL-Plan-Assertions.

### WP-I0-910 – Spike S10 – Designsystem-Parität (Angular Aria/CDK + floating-ui)

| Merkmal | Wert |
|---|---|
| Inkrement | I0 |
| Typ (DoD 15 §3.15.3) | S – Spike |
| Größe | M |
| parallelisierbar | ja |
| Abhängigkeiten | WP-I0-105 |
| CE-IDs | – (keine; Baustein/Spike/Abnahme) |

**Ziel.** Nachweis, dass 10 Leit-Komponenten (Button, Input, Menu, Combobox/Select, Tooltip, Dialog, Tabs, Popover, Avatar, Toast) und die Workspace-Shell DOM- und pixelgleich (≤ 0,1 %) mit Original-Tastaturbedienung umsetzbar sind; Portal-Schicht ohne CDK-Overlay (Z-06). Der Shell-Teil gehört zu I0.

**Betroffene Module/Libs in `funk.`**

- Frontend: `frontend/libs/shared/propel/headless/` (Prototyp)
- Frontend: `docs/spikes/S10-ergebnis.md`

**Referenzdokumente**

- Architektur: 01 §9 Zeile S10
- Architektur: 09 §3.3–§3.5, §3.14
- Architektur: 17 Z-06, ABG-026

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- `packages/propel/` (npm `@makeplane/propel@0.7.3`)
- `packages/blocks/src/`

**Akzeptanzkriterien**

1. Erfolgskriterien 01 §9 S10 als Galerie-Tests grün; Host-Form der Blocks-Select-Familie festgelegt (O-D09-16).
2. Ergebnisbericht `docs/spikes/<Spike>-ergebnis.md` mit Messwerten; Messungen als automatisierte Tests, die danach dauerhaft in G4 laufen (DoD Typ S).
3. Bei Abbruchkriterium: Fallback aus 01 §9 ohne weitere Diskussion aktiviert (außer ADR-000…009 betroffen → Auftraggeber).

**Testumfang**

- Galerie DOM/Visual, Tastatur-Tests.

### WP-I0-911 – Spike S11 – Paritäts-Harness (Original v1.4.2 starten, Seed, Record/Replay, Visual-Katalog)

| Merkmal | Wert |
|---|---|
| Inkrement | I0 |
| Typ (DoD 15 §3.15.3) | S – Spike |
| Größe | M |
| parallelisierbar | ja |
| Abhängigkeiten | WP-I0-101 |
| CE-IDs | – (keine; Baustein/Spike/Abnahme) |

**Ziel.** Das Original v1.4.2 wird reproduzierbar gestartet und deterministisch geseedet; `Funk.Tools.ParityHarness` zeichnet Requests/Responses als Goldens auf und spielt sie gegen funk. ab. Das Werkzeug ist ab I0 Teil der Definition of Done aller Arbeitspakete.

**Betroffene Module/Libs in `funk.`**

- Backend: `src/tools/Funk.Tools.ParityHarness` (Kommandos `seed`, `record`, `replay`, `diff`, `keycloak-test-realm`)
- Backend: `tools/parity/{start-original.sh,compose.original.yml,original.env}`
- Backend: `tests/seed/parity-seed.yaml`, `tests/seed/original/seed_plane.py`
- Backend: `tests/contracts/{scenarios,golden}/`, `tests/contracts/deviations.yaml`
- Backend: `tests/Funk.Tools.ParityHarness.Tests`
- Frontend: `frontend/apps/e2e/visual/catalog/` (5 Seiten des Originals)
- Frontend: `frontend/apps/e2e/drivers/branding.ts` (Referenz-Branding BR-13)

**Referenzdokumente**

- Architektur: 01 §9 Zeile S11
- Architektur: 15 §3.6 (Harness), §3.6.7 (I0-Umfang), §3.14.1 (Parity-Seed)
- Architektur: 09 §3.14.2 (Referenzumgebung)
- Architektur: 17 ABG-001, ABG-006

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- `deployments/` (Compose-Vorlagen des Originals)
- `apps/api/plane/seeds/`
- `apps/api/plane/db/management/commands/`

**Akzeptanzkriterien**

1. `tools/parity/start-original.sh` startet das Original mit per Digest gepinnten `makeplane/*`-Images hinter `http://localhost:13000`; `--from-source` für Visual-Aufnahmen; `ORIGINAL_SHA` = `053b2c0`.
2. `Funk.Tools.ParityHarness seed` erzeugt auf Original und funk. denselben Datenstand (`manifest.original.json` = `manifest.funk.json`, geprüft durch `tools/ci/seed-manifest-diff`).
3. Recorder zeichnet die 5 I0-Endpunkte (15 §3.6.7) auf; Replay gegen funk. mit Normalisierung (IDs, Zeitstempel, `deviations.yaml`) läuft in CI < 15 min.
4. Playwright-Screenshot-Katalog für 5 Seiten des Originals (Sign-in, Create-Workspace, leere Workspace-Shell, Create-Project, God-Mode-General) liegt als Referenz vor.
5. Fallback (Seeds über Original-API) nur, falls das Original nicht deterministisch seedbar ist; Ergebnisbericht `docs/spikes/S11-ergebnis.md`.
6. Ergebnisbericht `docs/spikes/<Spike>-ergebnis.md` mit Messwerten; Messungen als automatisierte Tests, die danach dauerhaft in G4 laufen (DoD Typ S).
7. Bei Abbruchkriterium: Fallback aus 01 §9 ohne weitere Diskussion aktiviert (außer ADR-000…009 betroffen → Auftraggeber).

**Testumfang**

- `Funk.Tools.ParityHarness.Tests` (Normalisierer, Diff-Regeln 15 §3.6.4), Determinismus-Check (zwei Seeds → gleiche Goldens).

### WP-I0-912 – Spike S12 – Eigene Outbox/Job-Queue auf PostgreSQL

| Merkmal | Wert |
|---|---|
| Inkrement | I0 |
| Typ (DoD 15 §3.15.3) | S – Spike |
| Größe | S |
| parallelisierbar | ja |
| Abhängigkeiten | WP-I0-104, WP-I0-201 |
| CE-IDs | – (keine; Baustein/Spike/Abnahme) |

**Ziel.** Nachweis von Zuverlässigkeit und Durchsatz der eigenen PostgreSQL-Messaging-Implementierung (1 000 Jobs/s mit 3 Workern ohne Doppelverarbeitung, Outbox p95 < 500 ms, Leader-Failover < 30 s, Kill -9 verliert nichts). Gatet I1.

**Betroffene Module/Libs in `funk.`**

- Backend: `tests/Funk.Worker.Tests/Reliability/`
- Backend: `docs/spikes/S12-ergebnis.md`

**Referenzdokumente**

- Architektur: 01 §9 Zeile S12
- Architektur: 06 §3.3–§3.6, R-D06-01, O-D06-11
- Architektur: 17 Z-104, Z-117

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- `apps/api/plane/celery.py`
- `apps/api/plane/bgtasks/`

**Akzeptanzkriterien**

1. Kriterien 01 §9 S12 als Tests grün oder Fallback Wolverine (MIT) hinter denselben Interfaces aktiviert; Entscheidung zur Session-Verbindung `funk-session` hinter PgBouncer (Z-117).
2. Ergebnisbericht `docs/spikes/<Spike>-ergebnis.md` mit Messwerten; Messungen als automatisierte Tests, die danach dauerhaft in G4 laufen (DoD Typ S).
3. Bei Abbruchkriterium: Fallback aus 01 §9 ohne weitere Diskussion aktiviert (außer ADR-000…009 betroffen → Auftraggeber).

**Testumfang**

- Kill-/Failover-Tests, Durchsatz-Benchmark.

### WP-I0-913 – Spike Scope-FK – zusammengesetzter Fremdschlüssel (project_id, workspace_id) inkl. nullable workspace_id

| Merkmal | Wert |
|---|---|
| Inkrement | I0 |
| Typ (DoD 15 §3.15.3) | S – Spike |
| Größe | S |
| parallelisierbar | ja |
| Abhängigkeiten | WP-I0-104 |
| CE-IDs | – (keine; Baustein/Spike/Abnahme) |

**Ziel.** Nachweis, dass die Scope-FK-Konvention (composite FK mit überlappender `workspace_id`, `MATCH SIMPLE`) ohne EF-Fix-up-Probleme funktioniert – für Label (Workspace-Scope), State (Projekt-Scope), `file_assets` und `search_documents`.

**Betroffene Module/Libs in `funk.`**

- Backend: `src/data/Funk.Data/Conventions/ScopeForeignKeyConvention.cs` (Prototyp)
- Backend: `docs/spikes/SFK-ergebnis.md`

**Referenzdokumente**

- Architektur: 03 §5.2, R-D03-02, O-D03-05
- Architektur: 17 Z-107

**Akzeptanzkriterien**

1. Konvention erzeugt die erwarteten Constraints; Fallback (Raw-SQL-Constraint) nur bei EF-Warnungen/Fix-up-Effekten, dokumentiert.
2. Ergebnisbericht `docs/spikes/<Spike>-ergebnis.md` mit Messwerten; Messungen als automatisierte Tests, die danach dauerhaft in G4 laufen (DoD Typ S).
3. Bei Abbruchkriterium: Fallback aus 01 §9 ohne weitere Diskussion aktiviert (außer ADR-000…009 betroffen → Auftraggeber).

**Testumfang**

- L3 Schema-Konformitätstest.

### WP-I0-999 – Abnahme I0 – Walking Skeleton (G5)

| Merkmal | Wert |
|---|---|
| Inkrement | I0 |
| Typ (DoD 15 §3.15.3) | A – Inkrement-Abnahme |
| Größe | S |
| parallelisierbar | nein |
| Abhängigkeiten | WP-I0-001, WP-I0-002, WP-I0-003, WP-I0-004, WP-I0-005, WP-I0-006, WP-I0-101, WP-I0-102, WP-I0-103, WP-I0-104, WP-I0-105, WP-I0-106, WP-I0-107, WP-I0-108, WP-I0-109, WP-I0-201, WP-I0-202, WP-I0-203, WP-I0-204, WP-I0-205, WP-I0-206, WP-I0-207, WP-I0-208, WP-I0-900, WP-I0-907, WP-I0-910, WP-I0-911 |
| CE-IDs | – (keine; Baustein/Spike/Abnahme) |

**Ziel.** Inkrement-Abnahme I0 nach 15 §3.15.1 G5 und Meilenstein M0 (plan/01-roadmap-ce.md §4).

**Referenzdokumente**

- Architektur: plan/01-roadmap-ce.md §4 (M0)
- Architektur: 15 §3.15.1 (G5), §3.16 Zeile I0

**Akzeptanzkriterien**

1. Alle Abnahmekriterien M0 aus plan/01-roadmap-ce.md §4 erfüllt; `docs/acceptance/I0.md` generiert (`tools/ci/acceptance-report`).
2. G5 `--inc <In> --strict` grün: `ce-coverage-check`, `original-test-ledger`, Parity-Report (0 ungenehmigte Abweichungen, Endpunkt-Abdeckung des Inkrements 100 %), Visual/a11y, Lastziele, Security-Report.
3. Demo-Video der Kern-Flows (`--video on`) und Abnahmebericht `docs/acceptance/<In>.md`; fachliche Abnahme durch den Auftraggeber.

**Testumfang**

- G5 `--inc I0`.

## 4.2 Inkrement I1

### WP-I1-001 – Workspace-Einstellungen (General, Löschen, Settings-Rahmen, Stammdatenlisten, Themes-API)

| Merkmal | Wert |
|---|---|
| Inkrement | I1 |
| Typ (DoD 15 §3.15.3) | V – Vertikaler Schnitt |
| Größe | M |
| parallelisierbar | ja |
| Abhängigkeiten | WP-I0-999, WP-I1-203, WP-I1-103 |
| CE-IDs | CE-WS-003, CE-WS-004, CE-WS-006, CE-WS-007, CE-WS-024 |

**Ziel.** Workspace-Settings-Rahmen mit Navigation (über `SETTINGS_PAGES`), Seite General (Name, Logo, Organisationsgröße), Workspace löschen mit Bestätigung, workspace-weite Stammdatenlisten und die Themes-API.

**Enthaltene CE-IDs**

| CE-ID | Feature | Status (15 Anh. B) | Inkrement laut 15 | Pflicht-Ebenen | Testprojekt | E2E-Spec |
|---|---|---|---|---|---|---|
| CE-WS-003 | Workspace-Einstellungen General | übernommen | I1 | L1 L2 L3 L5 L7 L8 | Funk.Workspaces.Tests | `web/workspace/workspace-settings.spec.ts` |
| CE-WS-004 | Workspace löschen | übernommen | I1 | L1 L2 L3 L5 L7 L8 | Funk.Workspaces.Tests | `web/workspace/workspace-settings.spec.ts` |
| CE-WS-006 | Workspace-weite Stammdatenlisten | übernommen | I1 | L1 L3 L5 | Funk.Workspaces.Tests | – |
| CE-WS-007 | Workspace-Themes (nur API) | übernommen | I1 | L1 L3 L5 | Funk.Workspaces.Tests | – |
| CE-WS-024 | Workspace-Settings-Rahmen | übernommen | I1 | L1 L2 L3 L5 L7 L8 | Funk.Workspaces.Tests | `web/workspace/workspace-settings.spec.ts` |

**Betroffene Module/Libs in `funk.`**

- Backend: `src/modules/Workspaces/Funk.Workspaces`
- Frontend: `frontend/libs/web/workspace`, `frontend/libs/web/settings`

**Referenzdokumente**

- Architektur: 04 §4.3
- Architektur: 03 §3.4.3
- Architektur: 08 §4.1
- Architektur: 09 §4.14
- Analyse/Feature: `analysis/10a-frontend-workspace-projekt-navigation.md` §2.10
- Analyse/Feature: `analysis/03-api-intern-workspace-projekt-user.md` §3.1, §2.5
- Analyse/Feature: `analysis/08-frontend-web-architektur.md` §2.2
- Analyse/Feature: `analysis/02a-datenmodell-kern.md` §3.3, §2.3
- Analyse/Feature: `analysis/13b-shared-packages-i18n.md` §2.2
- Feature-Katalog: `features/10-ce-feature-katalog.md` (Einträge CE-WS-003, CE-WS-004, CE-WS-006, CE-WS-007, CE-WS-024)

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- Backend: `apps/api/plane/app/views/workspace/base.py`, `apps/api/plane/db/models/workspace.py`, `apps/api/plane/db/mixins.py`, `apps/api/plane/bgtasks/deletion_task.py`, `apps/api/plane/app/views/workspace/{label,state,estimate,cycle,module}.py`
- Frontend: `apps/web/components/workspace/settings/workspace-details.tsx`, `apps/web/components/core/modals/workspace-image-upload-modal.tsx`, `apps/web/components/global/timezone-select.tsx`, `apps/web/services/workspace.service.ts`, `apps/web/app/(all)/[workspaceSlug]/(settings)/settings/(workspace)/layout.tsx`, `apps/web/app/(all)/[workspaceSlug]/(settings)/settings/(workspace)/page.tsx`, `apps/web/app/(all)/[workspaceSlug]/(settings)/settings/(workspace)/members/page.tsx`, `apps/web/app/(all)/[workspaceSlug]/(settings)/settings/(workspace)/exports/page.tsx`, `apps/web/app/(all)/[workspaceSlug]/(settings)/settings/(workspace)/webhooks/page.tsx`, `apps/web/app/(all)/[workspaceSlug]/(settings)/settings/(workspace)/webhooks/[webhookId]/page.tsx`, `packages/constants/src/settings/workspace.ts`, `apps/web/components/workspace/delete-workspace-section.tsx`, `apps/web/components/workspace/delete-workspace-modal.tsx`, `apps/web/components/workspace/delete-workspace-form.tsx`, `apps/web/components/settings/workspace/sidebar/root.tsx`, `apps/web/components/settings/content-wrapper.tsx`, `apps/web/components/settings/mobile/nav.tsx`, `packages/constants/src/settings/profile.ts`, `packages/constants/src/settings/project.ts`

**Endpunkte (Katalog 04, `architecture/_data/endpoints.json`; 14 registriert)**

| EP | Methode | Pfad | Oberfläche | Handler | Permission | Inkr. 04 | CE-IDs |
|---|---|---|---|---|---|---|---|
| EP-0125 | PATCH | `/api/workspaces/{slug}/` | App | WorkspaceEndpoints.UpdateWorkspaceCommand | workspace.settings.update | I1 | CE-WS-003 |
| EP-0126 | DELETE | `/api/workspaces/{slug}/` | App | WorkspaceEndpoints.DeleteWorkspaceCommand | workspace.settings.delete | I1 | CE-WS-004 |
| EP-0140 | GET | `/api/workspaces/{slug}/estimates/` | App | WorkspaceMetadataEndpoints.ListWorkspaceEstimatesQuery | workspace.project_metadata.read | I1 | CE-WS-006 |
| EP-0141 | GET | `/api/workspaces/{slug}/labels/` | App | WorkspaceMetadataEndpoints.ListWorkspaceLabelsQuery | workspace.project_metadata.read | I1 | CE-WS-006 |
| EP-0143 | GET | `/api/workspaces/{slug}/states/` | App | WorkspaceMetadataEndpoints.ListWorkspaceStatesQuery | workspace.project_metadata.read | I1 | CE-WS-006 |
| EP-0151 | GET | `/api/workspaces/{slug}/workspace-themes/` | App | WorkspaceThemeEndpoints.ListWorkspaceThemesQuery | workspace.theme.read | I1 | CE-WS-007 |
| EP-0152 | POST | `/api/workspaces/{slug}/workspace-themes/` | App | WorkspaceThemeEndpoints.CreateWorkspaceThemeCommand | workspace.theme.create | I1 | CE-WS-007 |
| EP-0153 | GET | `/api/workspaces/{slug}/workspace-themes/{pk}/` | App | WorkspaceThemeEndpoints.GetWorkspaceThemeQuery | workspace.theme.read | I1 | CE-WS-007 |
| EP-0154 | PATCH | `/api/workspaces/{slug}/workspace-themes/{pk}/` | App | WorkspaceThemeEndpoints.UpdateWorkspaceThemeCommand | workspace.theme.update | I1 | CE-WS-007 |
| EP-0155 | DELETE | `/api/workspaces/{slug}/workspace-themes/{pk}/` | App | WorkspaceThemeEndpoints.DeleteWorkspaceThemeCommand | workspace.theme.delete | I1 | CE-WS-007 |
| EP-0427 | POST | `/api/assets/v2/workspaces/{slug}/` | App | WorkspaceAssetEndpoints.CreateWorkspaceAssetUploadCommand | workspace.asset.create | I1 | CE-WS-003, CE-OPS-012, CE-OPS-013 |
| EP-0432 | GET | `/api/assets/v2/workspaces/{slug}/{asset_id}/` | App | WorkspaceAssetEndpoints.GetWorkspaceAssetRedirectQuery | workspace.asset.read | I1 | CE-WS-003, CE-OPS-012, CE-OPS-013 |
| EP-0433 | PATCH | `/api/assets/v2/workspaces/{slug}/{asset_id}/` | App | WorkspaceAssetEndpoints.ConfirmWorkspaceAssetUploadCommand | workspace.asset.update | I1 | CE-WS-003, CE-OPS-012, CE-OPS-013 |
| EP-0434 | DELETE | `/api/assets/v2/workspaces/{slug}/{asset_id}/` | App | WorkspaceAssetEndpoints.DeleteWorkspaceAssetCommand | workspace.asset.delete | I1 | CE-WS-003, CE-OPS-012, CE-OPS-013 |

**Akzeptanzkriterien**

1. Contract: je Endpunkt dieses Pakets ≥ 1 Szenario mit Golden vom Original (Erfolg, Berechtigungsfehler, Validierungsfehler); Replay grün (L5).
2. Permission-Matrix (05 Anhang B) für alle Endpunkte dieses Pakets als L3-Test grün; Tenant-Isolation geprüft.
3. Signal-Stores strukturgleich zum MobX-Original (`store-parity-check`), Vitest je Action (L2).
4. E2E-Specs dieses Pakets grün gegen Original **und** funk. (Dual-Target, Pflichtszenarien 15 §3.9.3).
5. Visual-/DOM-/a11y-Prüfpunkte der betroffenen Screens (09 §4.14, 15 §3.10.2) innerhalb der Schwellwerte 15 §3.10.3 (Chromium); i18n-Schlüssel nur aus den Original-Locales (de/en).
6. `ce-coverage-check --ids CE-WS-003,CE-WS-004,CE-WS-006,CE-WS-007,CE-WS-024` grün (Mindestebenen 15 Anhang B).

**Testumfang**

- Pflicht-Ebenen (aus 15 Anhang B): L1, L2, L3, L5, L7, L8
- Testprojekte: `Funk.Workspaces.Tests`
- E2E-Specs (`frontend/apps/e2e/`): `web/workspace/workspace-settings.spec.ts`

### WP-I1-002 – Mitglieder, Rollen, Einladungen (inkl. automatischer Beitritt beim Login)

| Merkmal | Wert |
|---|---|
| Inkrement | I1 |
| Typ (DoD 15 §3.15.3) | V – Vertikaler Schnitt |
| Größe | L |
| parallelisierbar | ja |
| Abhängigkeiten | WP-I0-999, WP-I1-102, WP-I1-203 |
| CE-IDs | CE-WS-008, CE-WS-009, CE-WS-010, CE-WS-011, CE-WS-012, CE-AUTH-028 |

**Ziel.** Rollen- und Berechtigungsmodell Admin/Member/Guest, Mitgliederverwaltung, Einladungen per E-Mail (Template M5), Annehmen/Ablehnen, eigene Mitgliedschaft und Rollen-Maps; offene Einladungen werden beim ersten Keycloak-Login über die E-Mail-Adresse zugeordnet (Provisioning-Schritt).

**Enthaltene CE-IDs**

| CE-ID | Feature | Status (15 Anh. B) | Inkrement laut 15 | Pflicht-Ebenen | Testprojekt | E2E-Spec |
|---|---|---|---|---|---|---|
| CE-WS-008 | Rollen- und Berechtigungsmodell (Admin/Member/Guest) | übernommen | I1 | L1 L2 L3 L7 L8 | Funk.Authorization.Tests | `web/workspace/members-invitations.spec.ts` |
| CE-WS-009 | Workspace-Mitgliederverwaltung | übernommen | I1 | L1 L2 L3 L5 L7 L8 | Funk.Workspaces.Tests | `web/workspace/members-invitations.spec.ts` |
| CE-WS-010 | Mitglieder einladen und Einladungen verwalten | übernommen | I1 | L1 L2 L3 L4 L5 L6 L7 L8 (G-MAIL) | Funk.Workspaces.Tests | `web/workspace/members-invitations.spec.ts` |
| CE-WS-011 | Einladungen annehmen oder ablehnen | übernommen | I1 | L1 L2 L3 L5 L7 L8 | Funk.Workspaces.Tests | `web/workspace/members-invitations.spec.ts` |
| CE-WS-012 | Eigene Mitgliedschaft und Rollen-Maps | übernommen | I1 | L1 L2 L3 L5 L7 L8 | Funk.Workspaces.Tests | `web/workspace/members-invitations.spec.ts` |
| CE-AUTH-028 | Automatischer Beitritt aus angenommenen Einladungen | übernommen | I0/I1 | L1 L2 L3 L5 L6 L7 L8 | Funk.Identity.Tests | `web/auth/keycloak-login.spec.ts` |

**Betroffene Module/Libs in `funk.`**

- Backend: `src/modules/Workspaces/Funk.Workspaces` (Members, Invitations)
- Backend: `src/modules/Identity/Funk.Identity/Provisioning/AcceptPendingInvitationsStep.cs`
- Frontend: `frontend/libs/web/workspace` (members, invitations)
- Frontend: `frontend/apps/web/src/pages/(all)/invitations/`

**Referenzdokumente**

- Architektur: 04 §4.3
- Architektur: 05 §3.7.5, §3.13, §3.18.1
- Architektur: 06 §3.13
- Architektur: 03 §3.4.3
- Analyse/Feature: `analysis/06-auth-sicherheit-querschnitt.md` §2.10, §3.1
- Analyse/Feature: `analysis/02a-datenmodell-kern.md` §3.15
- Analyse/Feature: `analysis/13b-shared-packages-i18n.md` §2.7
- Analyse/Feature: `analysis/10a-frontend-workspace-projekt-navigation.md` §2.10
- Analyse/Feature: `analysis/03-api-intern-workspace-projekt-user.md` §3.3, §3.2
- Analyse/Feature: `analysis/08-frontend-web-architektur.md` §2.2
- Analyse/Feature: `analysis/07-hintergrundjobs-mail-storage-webhooks.md` §3.18
- Feature-Katalog: `features/10-ce-feature-katalog.md` (Einträge CE-WS-008, CE-WS-009, CE-WS-010, CE-WS-011, CE-WS-012, CE-AUTH-028)

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- Backend: `apps/api/plane/app/permissions/base.py`, `apps/api/plane/app/permissions/workspace.py`, `apps/api/plane/app/permissions/project.py`, `apps/api/plane/db/models/workspace.py`, `apps/api/plane/app/views/workspace/member.py`, `apps/api/plane/app/views/workspace/invite.py`, `apps/api/plane/bgtasks/workspace_invitation_task.py`, `apps/api/plane/app/serializers/workspace.py`, `apps/api/templates/emails/invitations/workspace_invitation.html`, `apps/api/plane/app/views/project/member.py`, `apps/api/plane/authentication/utils/user_auth_workflow.py`, `apps/api/plane/authentication/utils/workspace_project_join.py`
- Frontend: `packages/services/src/workspace/invitation.service.ts`, `packages/services/src/workspace/member.service.ts`, `packages/constants/src/workspace.ts`, `packages/constants/src/members.ts`, `apps/web/app/(all)/[workspaceSlug]/(settings)/settings/(workspace)/members/page.tsx`, `apps/web/components/workspace/settings/members-list.tsx`, `apps/web/components/workspace/settings/members-list-item.tsx`, `apps/web/components/workspace/settings/member-columns.tsx`, `apps/web/components/workspace/settings/useMemberColumns.tsx`, `apps/web/components/workspace/confirm-workspace-member-remove.tsx`, `apps/web/store/member/workspace/workspace-member.store.ts`, `apps/web/app/(all)/[workspaceSlug]/(settings)/settings/(workspace)/layout.tsx`, `apps/web/app/(all)/[workspaceSlug]/(settings)/settings/(workspace)/page.tsx`, `apps/web/app/(all)/[workspaceSlug]/(settings)/settings/(workspace)/exports/page.tsx`, `apps/web/app/(all)/[workspaceSlug]/(settings)/settings/(workspace)/webhooks/page.tsx`, `apps/web/app/(all)/[workspaceSlug]/(settings)/settings/(workspace)/webhooks/[webhookId]/page.tsx`, `packages/constants/src/settings/workspace.ts`, `apps/web/components/workspace/invite-modal/form.tsx`, `apps/web/components/workspace/invite-modal/fields.tsx`, `apps/web/components/workspace/invite-modal/actions.tsx`, `apps/web/components/workspace/settings/invitations-list-item.tsx`, `apps/web/services/workspace.service.ts`, `apps/web/app/(all)/invitations/page.tsx`, `apps/web/app/(all)/workspace-invitations/page.tsx`

**Endpunkte (Katalog 04, `architecture/_data/endpoints.json`; 16 registriert)**

| EP | Methode | Pfad | Oberfläche | Handler | Permission | Inkr. 04 | CE-IDs |
|---|---|---|---|---|---|---|---|
| EP-0099 | GET | `/api/workspaces/{slug}/invitations/{pk}/join/` | App | InvitationJoinEndpoints.GetPublicWorkspaceInvitationQuery | public.invitation.read | I1 | CE-WS-011 |
| EP-0100 | POST | `/api/workspaces/{slug}/invitations/{pk}/join/` | App | InvitationJoinEndpoints.RespondToWorkspaceInvitationCommand | public.invitation.respond | I1 | CE-WS-011 |
| EP-0113 | GET | `/api/users/me/workspaces/invitations/` | App | MyInvitationEndpoints.ListMyWorkspaceInvitationsQuery | user.invitation.read | I1 | CE-WS-011 |
| EP-0114 | POST | `/api/users/me/workspaces/invitations/` | App | MyInvitationEndpoints.AcceptMyWorkspaceInvitationsCommand | user.invitation.accept | I1 | CE-WS-011 |
| EP-0127 | GET | `/api/workspaces/{slug}/invitations/` | App | WorkspaceInvitationEndpoints.ListWorkspaceInvitationsQuery | workspace.invitation.read | I1 | CE-WS-010 |
| EP-0128 | POST | `/api/workspaces/{slug}/invitations/` | App | WorkspaceInvitationEndpoints.CreateWorkspaceInvitationsCommand | workspace.invitation.create | I1 | CE-WS-010 |
| EP-0129 | GET | `/api/workspaces/{slug}/invitations/{pk}/` | App | WorkspaceInvitationEndpoints.GetWorkspaceInvitationQuery | workspace.invitation.read | I1 | CE-WS-010 |
| EP-0130 | PATCH | `/api/workspaces/{slug}/invitations/{pk}/` | App | WorkspaceInvitationEndpoints.UpdateWorkspaceInvitationCommand | workspace.invitation.update | I1 | CE-WS-010 |
| EP-0131 | DELETE | `/api/workspaces/{slug}/invitations/{pk}/` | App | WorkspaceInvitationEndpoints.DeleteWorkspaceInvitationCommand | workspace.invitation.delete | I1 | CE-WS-010 |
| EP-0132 | GET | `/api/workspaces/{slug}/members/` | App | WorkspaceMemberEndpoints.ListWorkspaceMembersQuery | workspace.member.read | I1 | CE-WS-009 |
| EP-0133 | POST | `/api/workspaces/{slug}/members/leave/` | App | WorkspaceMemberEndpoints.LeaveWorkspaceCommand | workspace.member.leave | I1 | CE-WS-009 |
| EP-0134 | GET | `/api/workspaces/{slug}/members/{pk}/` | App | WorkspaceMemberEndpoints.GetWorkspaceMemberQuery | workspace.member.read | I1 | CE-WS-009 |
| EP-0135 | PATCH | `/api/workspaces/{slug}/members/{pk}/` | App | WorkspaceMemberEndpoints.UpdateWorkspaceMemberCommand | workspace.member.update | I1 | CE-WS-009 |
| EP-0136 | DELETE | `/api/workspaces/{slug}/members/{pk}/` | App | WorkspaceMemberEndpoints.DeleteWorkspaceMemberCommand | workspace.member.delete | I1 | CE-WS-009 |
| EP-0137 | GET | `/api/workspaces/{slug}/project-members/` | App | WorkspaceMemberEndpoints.ListWorkspaceProjectMembershipsQuery | workspace.member.read | I1 | CE-WS-012 |
| EP-0183 | GET | `/api/users/me/workspaces/{slug}/project-roles/` | App | ProjectEndpoints.ListMyProjectRolesQuery | workspace.project.read | I1 | CE-WS-012 |

**Akzeptanzkriterien**

1. Permission-Matrix-Tests für alle Mitglieder-/Einladungs-Endpunkte inkl. HARM-00 (WS-Admin-Override) grün.
2. Einladungs-Mail (M5) besteht G-MAIL; Annahme über Link und automatische Zuordnung beim Login führen zur gleichen Mitgliedschaft.
3. Contract: je Endpunkt dieses Pakets ≥ 1 Szenario mit Golden vom Original (Erfolg, Berechtigungsfehler, Validierungsfehler); Replay grün (L5).
4. Permission-Matrix (05 Anhang B) für alle Endpunkte dieses Pakets als L3-Test grün; Tenant-Isolation geprüft.
5. Signal-Stores strukturgleich zum MobX-Original (`store-parity-check`), Vitest je Action (L2).
6. E2E-Specs dieses Pakets grün gegen Original **und** funk. (Dual-Target, Pflichtszenarien 15 §3.9.3).
7. Visual-/DOM-/a11y-Prüfpunkte der betroffenen Screens (09 §4.14, 15 §3.10.2) innerhalb der Schwellwerte 15 §3.10.3 (Chromium); i18n-Schlüssel nur aus den Original-Locales (de/en).
8. `ce-coverage-check --ids CE-WS-008,CE-WS-009,CE-WS-010,CE-WS-011,CE-WS-012,CE-AUTH-028` grün (Mindestebenen 15 Anhang B).

**Testumfang**

- Pflicht-Ebenen (aus 15 Anhang B): L1, L2, L3, L4, L5, L6, L7, L8
- Testprojekte: `Funk.Authorization.Tests`, `Funk.Workspaces.Tests`, `Funk.Identity.Tests`
- E2E-Specs (`frontend/apps/e2e/`): `web/workspace/members-invitations.spec.ts`, `web/auth/keycloak-login.spec.ts`

### WP-I1-003 – Shell-Ergänzungen und Navigation: Hilfe-Menü, What's new, Star-Link, Sidebar „More“, Customize navigation

| Merkmal | Wert |
|---|---|
| Inkrement | I1 |
| Typ (DoD 15 §3.15.3) | V – Vertikaler Schnitt |
| Größe | M |
| parallelisierbar | ja |
| Abhängigkeiten | WP-I0-999, WP-I1-203 |
| CE-IDs | CE-WS-014, CE-WS-015, CE-WS-017, CE-WS-021, CE-WS-022 |

**Ziel.** Hilfe-Menü, Changelog (What's new) und Star-Link mit konfigurierbaren bzw. entfallenden externen Zielen (ADR-004, ADR-009B), erweiterte Sidebar „More“ mit Pin/Sortierung und „Customize navigation“ mit Persistenz.

**Enthaltene CE-IDs**

| CE-ID | Feature | Status (15 Anh. B) | Inkrement laut 15 | Pflicht-Ebenen | Testprojekt | E2E-Spec |
|---|---|---|---|---|---|---|
| CE-WS-014 | Hilfe-Menü | übernommen | I0/I1 | L2 L7 L8 | Frontend-only | `web/workspace/workspace-shell.spec.ts` |
| CE-WS-015 | What's new? (Produkt-Changelog) | übernommen | I0/I1 | L1 L2 L3 L5 L7 L8 | Funk.Workspaces.Tests | `web/workspace/workspace-shell.spec.ts` |
| CE-WS-017 | Star-us-on-GitHub-Link | übernommen | I0/I1 | L2 L7 L8 | Frontend-only | `web/workspace/workspace-shell.spec.ts` |
| CE-WS-021 | Erweiterte Sidebar 'More' mit Pin und Sortierung | übernommen | I1 | L1 L2 L3 L5 L7 L8 | Funk.Workspaces.Tests | `web/workspace/sidebar-navigation.spec.ts` |
| CE-WS-022 | Customize navigation | übernommen | I1 | L1 L2 L3 L5 L7 L8 | Funk.Workspaces.Tests | `web/workspace/sidebar-navigation.spec.ts` |

**Betroffene Module/Libs in `funk.`**

- Backend: `src/modules/Workspaces/Funk.Workspaces` (Sidebar-Präferenzen)
- Frontend: `frontend/libs/web/core/sidebar`, `frontend/libs/web/core/navigation`

**Referenzdokumente**

- Architektur: 08 §4.1, §3.16 (Branding)
- Architektur: 09 §4.11.1
- Architektur: 00 ADR-009B (externe Links)
- Analyse/Feature: `analysis/10a-frontend-workspace-projekt-navigation.md` §2.3, §2.16, §2.2, §3.3
- Analyse/Feature: `analysis/01-gesamtarchitektur-infrastruktur.md` §2.28
- Analyse/Feature: `analysis/08-frontend-web-architektur.md` §3.3
- Analyse/Feature: `analysis/03-api-intern-workspace-projekt-user.md` §3.7, §2.5
- Analyse/Feature: `analysis/02a-datenmodell-kern.md` §3.6
- Feature-Katalog: `features/10-ce-feature-katalog.md` (Einträge CE-WS-014, CE-WS-015, CE-WS-017, CE-WS-021, CE-WS-022)

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- Backend: `apps/api/Dockerfile.api`, `apps/api/plane/settings/common.py`, `apps/api/plane/app/views/workspace/user_preference.py`, `apps/api/plane/db/models/workspace.py`, `apps/api/plane/app/views/workspace/user.py`
- Frontend: `apps/web/components/workspace/sidebar/help-section/root.tsx`, `apps/web/components/global/version-number.tsx`, `apps/web/components/global/product-updates/modal.tsx`, `apps/web/components/global/product-updates/changelog.tsx`, `apps/web/components/global/product-updates/fallback.tsx`, `apps/web/components/global/product-updates/footer.tsx`, `apps/web/components/global/product-updates/header.tsx`, `apps/web/app/(all)/[workspaceSlug]/(projects)/star-us-link.tsx`, `apps/web/app/(all)/[workspaceSlug]/(projects)/extended-sidebar.tsx`, `apps/web/app/(all)/[workspaceSlug]/(projects)/extended-sidebar-wrapper.tsx`, `apps/web/components/workspace/sidebar/extended-sidebar-item.tsx`, `apps/web/hooks/use-navigation-preferences.ts`, `apps/web/services/workspace.service.ts`, `apps/web/store/workspace/index.ts`, `apps/web/components/navigation/customize-navigation-dialog.tsx`, `apps/web/app/(all)/[workspaceSlug]/(projects)/projects/(detail)/[projectId]/layout.tsx`, `apps/web/components/navigation/tab-navigation-root.tsx`, `apps/web/components/navigation/use-navigation-items.ts`, `apps/web/components/navigation/tab-navigation-utils.ts`

**Endpunkte (Katalog 04, `architecture/_data/endpoints.json`; 2 registriert)**

| EP | Methode | Pfad | Oberfläche | Handler | Permission | Inkr. 04 | CE-IDs |
|---|---|---|---|---|---|---|---|
| EP-0146 | GET | `/api/workspaces/{slug}/sidebar-preferences/` | App | WorkspacePreferenceEndpoints.ListSidebarPreferencesQuery | workspace.member_preference.read | I1 | CE-WS-021, CE-WS-022 |
| EP-0147 | PATCH | `/api/workspaces/{slug}/sidebar-preferences/` | App | WorkspacePreferenceEndpoints.UpdateSidebarPreferencesCommand | workspace.member_preference.update | I1 | CE-WS-021, CE-WS-022 |

**Akzeptanzkriterien**

1. Kein Link zeigt auf plane.so, docs.plane.so oder Plane-GitHub (G-BRAND, `no-external-urls`); nicht konfigurierte Ziele blenden den Eintrag aus (dokumentiert in `ui-deviations.yaml`).
2. Contract: je Endpunkt dieses Pakets ≥ 1 Szenario mit Golden vom Original (Erfolg, Berechtigungsfehler, Validierungsfehler); Replay grün (L5).
3. Permission-Matrix (05 Anhang B) für alle Endpunkte dieses Pakets als L3-Test grün; Tenant-Isolation geprüft.
4. Signal-Stores strukturgleich zum MobX-Original (`store-parity-check`), Vitest je Action (L2).
5. E2E-Specs dieses Pakets grün gegen Original **und** funk. (Dual-Target, Pflichtszenarien 15 §3.9.3).
6. Visual-/DOM-/a11y-Prüfpunkte der betroffenen Screens (09 §4.14, 15 §3.10.2) innerhalb der Schwellwerte 15 §3.10.3 (Chromium); i18n-Schlüssel nur aus den Original-Locales (de/en).
7. `ce-coverage-check --ids CE-WS-014,CE-WS-015,CE-WS-017,CE-WS-021,CE-WS-022` grün (Mindestebenen 15 Anhang B).

**Testumfang**

- Pflicht-Ebenen (aus 15 Anhang B): L1, L2, L3, L5, L7, L8
- Testprojekte: `Frontend-only`, `Funk.Workspaces.Tests`
- E2E-Specs (`frontend/apps/e2e/`): `web/workspace/workspace-shell.spec.ts`, `web/workspace/sidebar-navigation.spec.ts`

### WP-I1-004 – Favoriten mit Ordnern

| Merkmal | Wert |
|---|---|
| Inkrement | I1 |
| Typ (DoD 15 §3.15.3) | V – Vertikaler Schnitt |
| Größe | M |
| parallelisierbar | ja |
| Abhängigkeiten | WP-I1-005, WP-I1-203 |
| CE-IDs | CE-WS-023 |

**Ziel.** Favoriten (Projekte, Views, Cycles, Module, Pages) mit Ordnern, Drag-and-Drop-Sortierung und Sidebar-Darstellung über `FAVORITE_ENTITY_RENDERERS`; Entitätstypen späterer Inkremente werden mit deren Schnitt registriert.

**Enthaltene CE-IDs**

| CE-ID | Feature | Status (15 Anh. B) | Inkrement laut 15 | Pflicht-Ebenen | Testprojekt | E2E-Spec |
|---|---|---|---|---|---|---|
| CE-WS-023 | Favoriten mit Ordnern | übernommen | I1 | L1 L2 L3 L5 L7 L8 | Funk.Workspaces.Tests | `web/workspace/favorites.spec.ts` |

**Betroffene Module/Libs in `funk.`**

- Backend: `src/modules/Workspaces/Funk.Workspaces` (Favorites)
- Frontend: `frontend/libs/web/favorites`

**Referenzdokumente**

- Architektur: 04 §4.3
- Architektur: 03 §3.4.3
- Architektur: 08 §4.5 (favorite.store)
- Analyse/Feature: `analysis/10a-frontend-workspace-projekt-navigation.md` §3.4
- Analyse/Feature: `analysis/08-frontend-web-architektur.md` §3.3
- Analyse/Feature: `analysis/03-api-intern-workspace-projekt-user.md` §3.9
- Analyse/Feature: `analysis/02a-datenmodell-kern.md` §3.13
- Analyse/Feature: `analysis/13b-shared-packages-i18n.md` §2.2
- Feature-Katalog: `features/10-ce-feature-katalog.md` (Einträge CE-WS-023)

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- Backend: `apps/api/plane/app/views/workspace/favorite.py`, `apps/api/plane/app/serializers/favorite.py`, `apps/api/plane/app/views/project/base.py`, `apps/api/plane/db/models/favorite.py`
- Frontend: `apps/web/components/workspace/sidebar/favorites/favorites-menu.tsx`, `apps/web/components/workspace/sidebar/favorites/favorite-folder.tsx`, `apps/web/components/workspace/sidebar/favorites/favorite-items/root.tsx`, `apps/web/components/workspace/sidebar/favorites/favorites.helpers.ts`, `apps/web/store/favorite.store.ts`, `apps/web/components/workspace/sidebar/favorites/new-fav-folder.tsx`, `apps/web/hooks/use-favorite-item-details.tsx`, `apps/web/services/favorite/favorite.service.ts`, `packages/constants/src/workspace.ts`, `packages/types/src/navigation-preferences.ts`, `packages/constants/src/sidebar-favorites.ts`, `packages/services/src/user/favorite.service.ts`

**Endpunkte (Katalog 04, `architecture/_data/endpoints.json`; 7 registriert)**

| EP | Methode | Pfad | Oberfläche | Handler | Permission | Inkr. 04 | CE-IDs |
|---|---|---|---|---|---|---|---|
| EP-0094 | GET | `/api/workspaces/{slug}/user-favorites/` | App | FavoriteEndpoints.ListFavoritesQuery | workspace.favorite.read | I1 | CE-WS-023 |
| EP-0095 | POST | `/api/workspaces/{slug}/user-favorites/` | App | FavoriteEndpoints.CreateFavoriteCommand | workspace.favorite.create | I1 | CE-WS-023 |
| EP-0096 | PATCH | `/api/workspaces/{slug}/user-favorites/{favorite_id}/` | App | FavoriteEndpoints.UpdateFavoriteCommand | workspace.favorite.update | I1 | CE-WS-023 |
| EP-0097 | DELETE | `/api/workspaces/{slug}/user-favorites/{favorite_id}/` | App | FavoriteEndpoints.DeleteFavoriteCommand | workspace.favorite.delete | I1 | CE-WS-023 |
| EP-0098 | GET | `/api/workspaces/{slug}/user-favorites/{favorite_id}/group/` | App | FavoriteEndpoints.ListFavoriteGroupQuery | workspace.favorite.read | I1 | CE-WS-023 |
| EP-0118 | POST | `/api/workspaces/{slug}/user-favorite-projects/` | App | ProjectFavoriteEndpoints.FavoriteProjectCommand | workspace.project.favorite | I1 | CE-WS-023, CE-PRJ-012 |
| EP-0119 | DELETE | `/api/workspaces/{slug}/user-favorite-projects/{project_id}/` | App | ProjectFavoriteEndpoints.UnfavoriteProjectCommand | workspace.project.favorite | I1 | CE-WS-023, CE-PRJ-012 |

**Akzeptanzkriterien**

1. Contract: je Endpunkt dieses Pakets ≥ 1 Szenario mit Golden vom Original (Erfolg, Berechtigungsfehler, Validierungsfehler); Replay grün (L5).
2. Permission-Matrix (05 Anhang B) für alle Endpunkte dieses Pakets als L3-Test grün; Tenant-Isolation geprüft.
3. Signal-Stores strukturgleich zum MobX-Original (`store-parity-check`), Vitest je Action (L2).
4. E2E-Specs dieses Pakets grün gegen Original **und** funk. (Dual-Target, Pflichtszenarien 15 §3.9.3).
5. Visual-/DOM-/a11y-Prüfpunkte der betroffenen Screens (09 §4.14, 15 §3.10.2) innerhalb der Schwellwerte 15 §3.10.3 (Chromium); i18n-Schlüssel nur aus den Original-Locales (de/en).
6. `ce-coverage-check --ids CE-WS-023` grün (Mindestebenen 15 Anhang B).

**Testumfang**

- Pflicht-Ebenen (aus 15 Anhang B): L1, L2, L3, L5, L7, L8
- Testprojekte: `Funk.Workspaces.Tests`
- E2E-Specs (`frontend/apps/e2e/`): `web/workspace/favorites.spec.ts`

### WP-I1-005 – Projektliste, Projektkarten, Projekt-Statistiken

| Merkmal | Wert |
|---|---|
| Inkrement | I1 |
| Typ (DoD 15 §3.15.3) | V – Vertikaler Schnitt |
| Größe | M |
| parallelisierbar | ja |
| Abhängigkeiten | WP-I0-999, WP-I1-105 |
| CE-IDs | CE-PRJ-001, CE-PRJ-002, CE-PRJ-003 |

**Ziel.** Projektliste mit Filtern/Sortierung/Suche, Projektkarten (Cover, Logo, Mitglieder, Beitreten) und Projekt-Statistiken.

**Enthaltene CE-IDs**

| CE-ID | Feature | Status (15 Anh. B) | Inkrement laut 15 | Pflicht-Ebenen | Testprojekt | E2E-Spec |
|---|---|---|---|---|---|---|
| CE-PRJ-001 | Projektliste | übernommen | I1 | L1 L2 L3 L5 L7 L8 | Funk.Projects.Tests | `web/projects/project-list.spec.ts` |
| CE-PRJ-002 | Projektkarte | übernommen | I1 | L1 L2 L3 L5 L7 L8 | Funk.Projects.Tests | `web/projects/project-list.spec.ts` |
| CE-PRJ-003 | Projekt-Statistiken | übernommen | I1 | L1 L2 L3 L5 L7 L8 | Funk.Projects.Tests | `web/projects/project-list.spec.ts` |

**Betroffene Module/Libs in `funk.`**

- Backend: `src/modules/Projects/Funk.Projects`
- Frontend: `frontend/libs/web/project`

**Referenzdokumente**

- Architektur: 04 §4.4
- Architektur: 03 §3.4.4
- Architektur: 02 §3.10 (Cursor-Paginator)
- Analyse/Feature: `analysis/10a-frontend-workspace-projekt-navigation.md` §2.12
- Analyse/Feature: `analysis/08-frontend-web-architektur.md` §2.2
- Analyse/Feature: `analysis/03-api-intern-workspace-projekt-user.md` §3.5, §2.11
- Analyse/Feature: `analysis/13b-shared-packages-i18n.md` §2.4
- Feature-Katalog: `features/10-ce-feature-katalog.md` (Einträge CE-PRJ-001, CE-PRJ-002, CE-PRJ-003)

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- Backend: `apps/api/plane/app/views/project/base.py`, `apps/api/plane/app/serializers/project.py`, `apps/api/plane/app/views/analytic/base.py`
- Frontend: `apps/web/components/projects/page.tsx`, `apps/web/components/project/root.tsx`, `apps/web/components/project/card-list.tsx`, `apps/web/components/project/header.tsx`, `apps/web/components/project/search-projects.tsx`, `apps/web/components/project/dropdowns/order-by.tsx`, `apps/web/components/project/dropdowns/filters/root.tsx`, `apps/web/components/project/applied-filters/root.tsx`, `apps/web/app/(all)/[workspaceSlug]/(projects)/projects/(list)/page.tsx`, `apps/web/app/(all)/[workspaceSlug]/(projects)/projects/(detail)/archives/page.tsx`, `apps/web/store/project/project.store.ts`, `apps/web/store/project/project_filter.store.ts`, `apps/web/services/project/project.service.ts`, `packages/constants/src/project.ts`, `packages/utils/src/project.ts`, `apps/web/components/project/card.tsx`, `apps/web/components/project/join-project-modal.tsx`

**Endpunkte (Katalog 04, `architecture/_data/endpoints.json`; 2 registriert)**

| EP | Methode | Pfad | Oberfläche | Handler | Permission | Inkr. 04 | CE-IDs |
|---|---|---|---|---|---|---|---|
| EP-0188 | GET | `/api/workspaces/{slug}/projects/details/` | App | ProjectEndpoints.ListProjectDetailsQuery | workspace.project.read | I1 | CE-PRJ-001, CE-PRJ-002 |
| EP-0480 | GET | `/api/workspaces/{slug}/project-stats/` | App | AnalyticsEndpoints.ListProjectStatsQuery | workspace.analytics.read_basic | I5 | CE-PRJ-003 |

**Akzeptanzkriterien**

1. Contract: je Endpunkt dieses Pakets ≥ 1 Szenario mit Golden vom Original (Erfolg, Berechtigungsfehler, Validierungsfehler); Replay grün (L5).
2. Permission-Matrix (05 Anhang B) für alle Endpunkte dieses Pakets als L3-Test grün; Tenant-Isolation geprüft.
3. Signal-Stores strukturgleich zum MobX-Original (`store-parity-check`), Vitest je Action (L2).
4. E2E-Specs dieses Pakets grün gegen Original **und** funk. (Dual-Target, Pflichtszenarien 15 §3.9.3).
5. Visual-/DOM-/a11y-Prüfpunkte der betroffenen Screens (09 §4.14, 15 §3.10.2) innerhalb der Schwellwerte 15 §3.10.3 (Chromium); i18n-Schlüssel nur aus den Original-Locales (de/en).
6. `ce-coverage-check --ids CE-PRJ-001,CE-PRJ-002,CE-PRJ-003` grün (Mindestebenen 15 Anhang B).

**Testumfang**

- Pflicht-Ebenen (aus 15 Anhang B): L1, L2, L3, L5, L7, L8
- Testprojekte: `Funk.Projects.Tests`
- E2E-Specs (`frontend/apps/e2e/`): `web/projects/project-list.spec.ts`

### WP-I1-006 – Projekt-Detail, Zugriffsschutz, Beitreten/Verlassen, Projekt-Einladungen per E-Mail

| Merkmal | Wert |
|---|---|
| Inkrement | I1 |
| Typ (DoD 15 §3.15.3) | V – Vertikaler Schnitt |
| Größe | M |
| parallelisierbar | ja |
| Abhängigkeiten | WP-I1-002, WP-I1-005 |
| CE-IDs | CE-PRJ-006, CE-PRJ-007, CE-PRJ-010 |

**Ziel.** Projekt-Detail mit `ProjectAuthWrapper` (Zugriff je Rolle/Netzwerk), Beitreten/Verlassen öffentlicher Projekte; die im Original defekte Projekt-Einladung per E-Mail wird repariert (DT-PRJ-01: 500 → 200 + Mail, O-D04-05).

**Enthaltene CE-IDs**

| CE-ID | Feature | Status (15 Anh. B) | Inkrement laut 15 | Pflicht-Ebenen | Testprojekt | E2E-Spec |
|---|---|---|---|---|---|---|
| CE-PRJ-006 | Projekt-Detail und Zugriffsschutz | übernommen | I1 | L1 L2 L3 L5 L7 L8 | Funk.Projects.Tests | `web/projects/project-access.spec.ts` |
| CE-PRJ-007 | Projekt beitreten und verlassen | übernommen | I1 | L1 L2 L3 L5 L7 L8 | Funk.Projects.Tests | `web/projects/project-access.spec.ts` |
| CE-PRJ-010 | Projekt-Einladungen per E-Mail (defekt, nur API) | übernommen | I1 | L1 L2 L3 L4 L7 L8 (G-MAIL) | Funk.Projects.Tests | `web/projects/project-access.spec.ts` |

**Betroffene Module/Libs in `funk.`**

- Backend: `src/modules/Projects/Funk.Projects`
- Frontend: `frontend/libs/web/project`
- Frontend: `frontend/libs/web/core/wrappers/project-auth-wrapper`

**Referenzdokumente**

- Architektur: 04 §4.4, §3.13 (DT-PRJ-01)
- Architektur: 05 §3.13
- Architektur: 08 §3.3.4
- Analyse/Feature: `analysis/08-frontend-web-architektur.md` §2.3
- Analyse/Feature: `analysis/10a-frontend-workspace-projekt-navigation.md` §2.14, §2.12
- Analyse/Feature: `analysis/03-api-intern-workspace-projekt-user.md` §3.5, §3.2
- Feature-Katalog: `features/10-ce-feature-katalog.md` (Einträge CE-PRJ-006, CE-PRJ-007, CE-PRJ-010)

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- Backend: `apps/api/plane/app/views/project/base.py`, `apps/api/plane/app/serializers/project.py`, `apps/api/plane/app/views/project/invite.py`, `apps/api/plane/app/views/project/member.py`, `apps/api/plane/bgtasks/project_add_user_email_task.py`
- Frontend: `apps/web/layouts/auth-layout/project-wrapper.tsx`, `apps/web/components/auth-screens/project/project-access-restriction.tsx`, `apps/web/components/auth-screens/not-authorized-view.tsx`, `apps/web/services/project/project.service.ts`, `apps/web/components/project/join-project-modal.tsx`, `apps/web/components/project/leave-project-modal.tsx`, `apps/web/components/project/confirm-project-member-remove.tsx`, `apps/web/services/user.service.ts`, `apps/web/services/project/project-member.service.ts`

**Endpunkte (Katalog 04, `architecture/_data/endpoints.json`; 9 registriert)**

| EP | Methode | Pfad | Oberfläche | Handler | Permission | Inkr. 04 | CE-IDs |
|---|---|---|---|---|---|---|---|
| EP-0101 | GET | `/api/workspaces/{slug}/projects/{project_id}/join/{pk}/` | App | InvitationJoinEndpoints.GetPublicProjectInvitationQuery | public.invitation.read | I1 | CE-PRJ-010 |
| EP-0102 | POST | `/api/workspaces/{slug}/projects/{project_id}/join/{pk}/` | App | InvitationJoinEndpoints.RespondToProjectInvitationCommand | public.invitation.respond | I1 | CE-PRJ-010 |
| EP-0115 | GET | `/api/users/me/workspaces/{slug}/projects/invitations/` | App | MyInvitationEndpoints.ListMyProjectInvitationsQuery | user.invitation.read | I1 | CE-PRJ-010 |
| EP-0194 | POST | `/api/users/me/workspaces/{slug}/projects/invitations/` | App | ProjectInvitationEndpoints.AcceptMyProjectInvitationsCommand | workspace.project_invitation.accept | I1 | CE-PRJ-010 |
| EP-0195 | GET | `/api/workspaces/{slug}/projects/{project_id}/invitations/` | App | ProjectInvitationEndpoints.ListProjectInvitationsQuery | project.invitation.read | I1 | CE-PRJ-010 |
| EP-0196 | POST | `/api/workspaces/{slug}/projects/{project_id}/invitations/` | App | ProjectInvitationEndpoints.CreateProjectInvitationsCommand | project.invitation.create | I1 | CE-PRJ-010 |
| EP-0197 | GET | `/api/workspaces/{slug}/projects/{project_id}/invitations/{pk}/` | App | ProjectInvitationEndpoints.GetProjectInvitationQuery | project.invitation.read | I1 | CE-PRJ-010 |
| EP-0198 | DELETE | `/api/workspaces/{slug}/projects/{project_id}/invitations/{pk}/` | App | ProjectInvitationEndpoints.DeleteProjectInvitationCommand | project.invitation.delete | I1 | CE-PRJ-010 |
| EP-0201 | POST | `/api/workspaces/{slug}/projects/{project_id}/members/leave/` | App | ProjectMemberEndpoints.LeaveProjectCommand | project.member.leave | I1 | CE-PRJ-007 |

**Akzeptanzkriterien**

1. Contract-Szenario `projects/project-invitations.yaml` mit `golden_source: target` und Abweichung DEV-API-… (04 §5.7) grün.
2. Contract: je Endpunkt dieses Pakets ≥ 1 Szenario mit Golden vom Original (Erfolg, Berechtigungsfehler, Validierungsfehler); Replay grün (L5).
3. Permission-Matrix (05 Anhang B) für alle Endpunkte dieses Pakets als L3-Test grün; Tenant-Isolation geprüft.
4. Signal-Stores strukturgleich zum MobX-Original (`store-parity-check`), Vitest je Action (L2).
5. E2E-Specs dieses Pakets grün gegen Original **und** funk. (Dual-Target, Pflichtszenarien 15 §3.9.3).
6. Visual-/DOM-/a11y-Prüfpunkte der betroffenen Screens (09 §4.14, 15 §3.10.2) innerhalb der Schwellwerte 15 §3.10.3 (Chromium); i18n-Schlüssel nur aus den Original-Locales (de/en).
7. `ce-coverage-check --ids CE-PRJ-006,CE-PRJ-007,CE-PRJ-010` grün (Mindestebenen 15 Anhang B).

**Testumfang**

- Pflicht-Ebenen (aus 15 Anhang B): L1, L2, L3, L4, L5, L7, L8
- Testprojekte: `Funk.Projects.Tests`
- E2E-Specs (`frontend/apps/e2e/`): `web/projects/project-access.spec.ts`

### WP-I1-007 – Projekt archivieren/wiederherstellen und löschen

| Merkmal | Wert |
|---|---|
| Inkrement | I1 |
| Typ (DoD 15 §3.15.3) | V – Vertikaler Schnitt |
| Größe | S |
| parallelisierbar | ja |
| Abhängigkeiten | WP-I1-005, WP-I1-101 |
| CE-IDs | CE-PRJ-008, CE-PRJ-009 |

**Ziel.** Archivieren und Wiederherstellen von Projekten sowie Löschen mit Soft-Delete-Kaskade (Deferred für Projekt-Wurzel).

**Enthaltene CE-IDs**

| CE-ID | Feature | Status (15 Anh. B) | Inkrement laut 15 | Pflicht-Ebenen | Testprojekt | E2E-Spec |
|---|---|---|---|---|---|---|
| CE-PRJ-008 | Projekt archivieren und wiederherstellen | übernommen | I1 | L1 L2 L3 L5 L7 L8 | Funk.Projects.Tests | `web/projects/project-archive-delete.spec.ts` |
| CE-PRJ-009 | Projekt löschen | übernommen | I1 | L1 L2 L3 L5 L7 L8 | Funk.Projects.Tests | `web/projects/project-archive-delete.spec.ts` |

**Betroffene Module/Libs in `funk.`**

- Backend: `src/modules/Projects/Funk.Projects`
- Frontend: `frontend/libs/web/project`, `frontend/libs/web/archives`

**Referenzdokumente**

- Architektur: 04 §4.4
- Architektur: 03 §3.5.4
- Architektur: 02 R-D02-04
- Analyse/Feature: `analysis/10a-frontend-workspace-projekt-navigation.md` §2.12, §2.11
- Analyse/Feature: `analysis/03-api-intern-workspace-projekt-user.md` §3.5
- Analyse/Feature: `analysis/02a-datenmodell-kern.md` §2.3
- Analyse/Feature: `analysis/08-frontend-web-architektur.md` §2.2
- Feature-Katalog: `features/10-ce-feature-katalog.md` (Einträge CE-PRJ-008, CE-PRJ-009)

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- Backend: `apps/api/plane/app/views/project/base.py`, `apps/api/plane/db/models/project.py`
- Frontend: `apps/web/app/(all)/[workspaceSlug]/(projects)/projects/(detail)/archives/page.tsx`, `apps/web/components/project/card.tsx`, `apps/web/components/project/archive-restore-modal.tsx`, `apps/web/components/project/form.tsx`, `apps/web/components/project/settings/control-section.tsx`, `apps/web/components/project/delete-project-modal.tsx`, `apps/web/services/project/project-archive.service.ts`, `apps/web/app/(all)/[workspaceSlug]/(projects)/projects/(list)/page.tsx`, `apps/web/store/project/project.store.ts`, `apps/web/store/project/project_filter.store.ts`

**Endpunkte (Katalog 04, `architecture/_data/endpoints.json`; 3 registriert)**

| EP | Methode | Pfad | Oberfläche | Handler | Permission | Inkr. 04 | CE-IDs |
|---|---|---|---|---|---|---|---|
| EP-0191 | DELETE | `/api/workspaces/{slug}/projects/{pk}/` | App | ProjectEndpoints.DeleteProjectCommand | project.project.delete | I1 | CE-PRJ-009 |
| EP-0192 | POST | `/api/workspaces/{slug}/projects/{project_id}/archive/` | App | ProjectEndpoints.ArchiveProjectCommand | project.project.archive | I1 | CE-PRJ-008 |
| EP-0193 | DELETE | `/api/workspaces/{slug}/projects/{project_id}/archive/` | App | ProjectEndpoints.UnarchiveProjectCommand | project.project.unarchive | I1 | CE-PRJ-008 |

**Akzeptanzkriterien**

1. Contract: je Endpunkt dieses Pakets ≥ 1 Szenario mit Golden vom Original (Erfolg, Berechtigungsfehler, Validierungsfehler); Replay grün (L5).
2. Permission-Matrix (05 Anhang B) für alle Endpunkte dieses Pakets als L3-Test grün; Tenant-Isolation geprüft.
3. Signal-Stores strukturgleich zum MobX-Original (`store-parity-check`), Vitest je Action (L2).
4. E2E-Specs dieses Pakets grün gegen Original **und** funk. (Dual-Target, Pflichtszenarien 15 §3.9.3).
5. Visual-/DOM-/a11y-Prüfpunkte der betroffenen Screens (09 §4.14, 15 §3.10.2) innerhalb der Schwellwerte 15 §3.10.3 (Chromium); i18n-Schlüssel nur aus den Original-Locales (de/en).
6. `ce-coverage-check --ids CE-PRJ-008,CE-PRJ-009` grün (Mindestebenen 15 Anhang B).

**Testumfang**

- Pflicht-Ebenen (aus 15 Anhang B): L1, L2, L3, L5, L7, L8
- Testprojekte: `Funk.Projects.Tests`
- E2E-Specs (`frontend/apps/e2e/`): `web/projects/project-archive-delete.spec.ts`

### WP-I1-008 – Projekt-Sidebar, Kontextmenü, erweiterte Sidebar, Feature-Navigation, Tabs

| Merkmal | Wert |
|---|---|
| Inkrement | I1 |
| Typ (DoD 15 §3.15.3) | V – Vertikaler Schnitt |
| Größe | M |
| parallelisierbar | ja |
| Abhängigkeiten | WP-I1-005, WP-I1-202 |
| CE-IDs | CE-PRJ-011, CE-PRJ-012, CE-PRJ-013, CE-PRJ-014, CE-PRJ-015 |

**Ziel.** Projektliste in der Sidebar mit Kontextmenü und Sortierung, erweiterte Projekt-Sidebar, Feature-Navigation je aktiviertem Feature (über `PROJECT_FEATURES`) und Tab-Navigation (TABBED).

> **Hinweis:** Feature-Einträge erscheinen erst, wenn der Ziel-Screen abgenommen ist (01 §7.19); bis I4 sind z. B. Pages/Intake/Cycles ausgeblendet.

**Enthaltene CE-IDs**

| CE-ID | Feature | Status (15 Anh. B) | Inkrement laut 15 | Pflicht-Ebenen | Testprojekt | E2E-Spec |
|---|---|---|---|---|---|---|
| CE-PRJ-011 | Projektliste in der Sidebar | übernommen | I1 | L2 L7 L8 | Frontend-only | `web/projects/project-sidebar.spec.ts` |
| CE-PRJ-012 | Projekt-Kontextmenü in der Sidebar | übernommen | I1 | L2 L7 L8 | Frontend-only | `web/projects/project-sidebar.spec.ts` |
| CE-PRJ-013 | Erweiterte Projekt-Sidebar | übernommen | I1 | L2 L7 L8 | Frontend-only | `web/projects/project-sidebar.spec.ts` |
| CE-PRJ-014 | Projekt-Feature-Navigation | übernommen | I1 | L2 L7 L8 | Frontend-only | `web/projects/project-sidebar.spec.ts` |
| CE-PRJ-015 | Tab-Navigation (TABBED) | übernommen | I1 | L2 L7 L8 | Frontend-only | `web/projects/project-sidebar.spec.ts` |

**Betroffene Module/Libs in `funk.`**

- Frontend: `frontend/libs/web/project` (sidebar)
- Frontend: `frontend/libs/web/core/sidebar`

**Referenzdokumente**

- Architektur: 08 §4.1, §4.4
- Architektur: 16 §3.2.6
- Analyse/Feature: `analysis/10a-frontend-workspace-projekt-navigation.md` §3.3, §2.4
- Analyse/Feature: `analysis/02a-datenmodell-kern.md` §3.5, §2.5
- Analyse/Feature: `analysis/13b-shared-packages-i18n.md` §2.4
- Analyse/Feature: `analysis/08-frontend-web-architektur.md` §3.3
- Feature-Katalog: `features/10-ce-feature-katalog.md` (Einträge CE-PRJ-011, CE-PRJ-012, CE-PRJ-013, CE-PRJ-014, CE-PRJ-015)

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- Backend: `apps/api/plane/db/models/project.py`, `apps/api/plane/app/views/project/member.py`, `apps/api/plane/app/views/project/invite.py`, `apps/api/plane/db/models/issue.py`
- Frontend: `apps/web/components/workspace/sidebar/projects-list.tsx`, `apps/web/components/workspace/sidebar/projects-list-item.tsx`, `apps/web/components/workspace/sidebar/project-navigation.tsx`, `packages/constants/src/project.ts`, `packages/utils/src/project.ts`, `apps/web/components/project/leave-project-modal.tsx`, `apps/web/components/project/publish-project/modal.tsx`, `apps/web/app/(all)/[workspaceSlug]/(projects)/extended-project-sidebar.tsx`, `apps/web/components/navigation/tab-navigation-utils.ts`, `apps/web/components/navigation/tab-navigation-root.tsx`, `apps/web/components/navigation/tab-navigation-visible-item.tsx`, `apps/web/components/navigation/tab-navigation-overflow-menu.tsx`, `apps/web/components/navigation/use-tab-preferences.ts`, `apps/web/components/navigation/project-header.tsx`, `apps/web/components/navigation/project-actions-menu.tsx`, `apps/web/app/(all)/[workspaceSlug]/(projects)/projects/(detail)/[projectId]/layout.tsx`, `apps/web/components/navigation/use-navigation-items.ts`, `packages/types/src/project/projects.ts`

**Akzeptanzkriterien**

1. Contract: je Endpunkt dieses Pakets ≥ 1 Szenario mit Golden vom Original (Erfolg, Berechtigungsfehler, Validierungsfehler); Replay grün (L5).
2. Permission-Matrix (05 Anhang B) für alle Endpunkte dieses Pakets als L3-Test grün; Tenant-Isolation geprüft.
3. Signal-Stores strukturgleich zum MobX-Original (`store-parity-check`), Vitest je Action (L2).
4. E2E-Specs dieses Pakets grün gegen Original **und** funk. (Dual-Target, Pflichtszenarien 15 §3.9.3).
5. Visual-/DOM-/a11y-Prüfpunkte der betroffenen Screens (09 §4.14, 15 §3.10.2) innerhalb der Schwellwerte 15 §3.10.3 (Chromium); i18n-Schlüssel nur aus den Original-Locales (de/en).
6. `ce-coverage-check --ids CE-PRJ-011,CE-PRJ-012,CE-PRJ-013,CE-PRJ-014,CE-PRJ-015` grün (Mindestebenen 15 Anhang B).

**Testumfang**

- Pflicht-Ebenen (aus 15 Anhang B): L2, L7, L8
- Testprojekte: `Frontend-only`
- E2E-Specs (`frontend/apps/e2e/`): `web/projects/project-sidebar.spec.ts`

### WP-I1-009 – Projekt-Settings-Rahmen, General, Benutzerpräferenzen

| Merkmal | Wert |
|---|---|
| Inkrement | I1 |
| Typ (DoD 15 §3.15.3) | V – Vertikaler Schnitt |
| Größe | M |
| parallelisierbar | ja |
| Abhängigkeiten | WP-I1-005, WP-I1-203 |
| CE-IDs | CE-PRJ-016, CE-PRJ-017, CE-PRJ-018 |

**Ziel.** Projekt-Settings-Rahmen mit Navigation (über `SETTINGS_PAGES`), Seite General (Name, Identifier, Beschreibung, Cover, Logo, Netzwerk, Zeitzone) und Projekt-Benutzerpräferenzen.

**Enthaltene CE-IDs**

| CE-ID | Feature | Status (15 Anh. B) | Inkrement laut 15 | Pflicht-Ebenen | Testprojekt | E2E-Spec |
|---|---|---|---|---|---|---|
| CE-PRJ-016 | Projekt-Benutzerpräferenzen | übernommen | I1 | L1 L2 L3 L5 L7 L8 | Funk.Projects.Tests | `web/projects/project-settings.spec.ts` |
| CE-PRJ-017 | Projekt-Settings-Rahmen | übernommen | I1 | L2 L7 L8 | Frontend-only | `web/projects/project-settings.spec.ts` |
| CE-PRJ-018 | Projekt-Einstellungen General | übernommen | I1 | L1 L2 L3 L5 L7 L8 | Funk.Projects.Tests | `web/projects/project-settings.spec.ts` |

**Betroffene Module/Libs in `funk.`**

- Backend: `src/modules/Projects/Funk.Projects`
- Frontend: `frontend/libs/web/project-settings`

**Referenzdokumente**

- Architektur: 04 §4.4
- Architektur: 03 §3.4.4
- Architektur: 08 §4.1
- Analyse/Feature: `analysis/03-api-intern-workspace-projekt-user.md` §2.6, §3.5
- Analyse/Feature: `analysis/02a-datenmodell-kern.md` §2.5, §3.4
- Analyse/Feature: `analysis/10a-frontend-workspace-projekt-navigation.md` §2.11
- Analyse/Feature: `analysis/08-frontend-web-architektur.md` §2.2
- Analyse/Feature: `analysis/13b-shared-packages-i18n.md` §2.2
- Feature-Katalog: `features/10-ce-feature-katalog.md` (Einträge CE-PRJ-016, CE-PRJ-017, CE-PRJ-018)

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- Backend: `apps/api/plane/app/views/project/base.py`, `apps/api/plane/app/views/project/member.py`, `apps/api/plane/db/models/project.py`, `apps/api/plane/db/models/issue.py`, `apps/api/plane/app/serializers/project.py`
- Frontend: `packages/types/src/project/projects.ts`, `apps/web/components/settings/project/sidebar/root.tsx`, `apps/web/components/settings/project/sidebar/item-categories.tsx`, `apps/web/app/(all)/[workspaceSlug]/(settings)/settings/projects/layout.tsx`, `apps/web/app/(all)/[workspaceSlug]/(settings)/settings/projects/page.tsx`, `packages/constants/src/settings/project.ts`, `apps/web/app/(all)/[workspaceSlug]/(settings)/settings/projects/[projectId]/layout.tsx`, `apps/web/app/(all)/[workspaceSlug]/(settings)/settings/projects/[projectId]/page.tsx`, `apps/web/app/(all)/[workspaceSlug]/(settings)/settings/projects/[projectId]/features/cycles/page.tsx`, `apps/web/app/(all)/[workspaceSlug]/(settings)/settings/projects/[projectId]/states/page.tsx`, `apps/web/app/(all)/[workspaceSlug]/(settings)/settings/projects/[projectId]/labels/page.tsx`, `apps/web/app/(all)/[workspaceSlug]/(settings)/settings/projects/[projectId]/estimates/page.tsx`, `apps/web/app/(all)/[workspaceSlug]/(settings)/settings/projects/[projectId]/automations/page.tsx`, `packages/constants/src/settings/profile.ts`, `packages/constants/src/settings/workspace.ts`, `apps/web/components/project/form.tsx`, `apps/web/components/project/settings/control-section.tsx`, `apps/web/components/project/archive-restore-modal.tsx`, `apps/web/components/project/delete-project-modal.tsx`

**Endpunkte (Katalog 04, `architecture/_data/endpoints.json`; 4 registriert)**

| EP | Methode | Pfad | Oberfläche | Handler | Permission | Inkr. 04 | CE-IDs |
|---|---|---|---|---|---|---|---|
| EP-0190 | PATCH | `/api/workspaces/{slug}/projects/{pk}/` | App | ProjectEndpoints.UpdateProjectCommand | project.project.update | I1 | CE-PRJ-018, CE-PRJ-019, CE-PRJ-022, CE-PRJ-039, CE-PRJ-040 |
| EP-0210 | GET | `/api/workspaces/{slug}/projects/{project_id}/preferences/member/{member_id}/` | App | ProjectPreferenceEndpoints.GetProjectMemberPreferencesQuery | project.member_preference.read | I1 | CE-PRJ-016 |
| EP-0211 | PATCH | `/api/workspaces/{slug}/projects/{project_id}/preferences/member/{member_id}/` | App | ProjectPreferenceEndpoints.UpdateProjectMemberPreferencesCommand | project.member_preference.update | I1 | CE-PRJ-016 |
| EP-0212 | POST | `/api/workspaces/{slug}/projects/{project_id}/project-views/` | App | ProjectPreferenceEndpoints.UpdateProjectViewPreferencesCommand | project.member_preference.update | I1 | CE-PRJ-016 |

**Akzeptanzkriterien**

1. Contract: je Endpunkt dieses Pakets ≥ 1 Szenario mit Golden vom Original (Erfolg, Berechtigungsfehler, Validierungsfehler); Replay grün (L5).
2. Permission-Matrix (05 Anhang B) für alle Endpunkte dieses Pakets als L3-Test grün; Tenant-Isolation geprüft.
3. Signal-Stores strukturgleich zum MobX-Original (`store-parity-check`), Vitest je Action (L2).
4. E2E-Specs dieses Pakets grün gegen Original **und** funk. (Dual-Target, Pflichtszenarien 15 §3.9.3).
5. Visual-/DOM-/a11y-Prüfpunkte der betroffenen Screens (09 §4.14, 15 §3.10.2) innerhalb der Schwellwerte 15 §3.10.3 (Chromium); i18n-Schlüssel nur aus den Original-Locales (de/en).
6. `ce-coverage-check --ids CE-PRJ-016,CE-PRJ-017,CE-PRJ-018` grün (Mindestebenen 15 Anhang B).

**Testumfang**

- Pflicht-Ebenen (aus 15 Anhang B): L1, L2, L3, L5, L7, L8
- Testprojekte: `Funk.Projects.Tests`, `Frontend-only`
- E2E-Specs (`frontend/apps/e2e/`): `web/projects/project-settings.spec.ts`

### WP-I1-010 – Projekt-Features (Toggles), Disabled-Zustände, Projektmitglieder, Gastzugriff

| Merkmal | Wert |
|---|---|
| Inkrement | I1 |
| Typ (DoD 15 §3.15.3) | V – Vertikaler Schnitt |
| Größe | M |
| parallelisierbar | ja |
| Abhängigkeiten | WP-I1-009, WP-I1-202, WP-I1-002 |
| CE-IDs | CE-PRJ-019, CE-PRJ-020, CE-PRJ-021, CE-PRJ-022 |

**Ziel.** Feature-Toggles über den Feature-Katalog, Disabled-Feature-Zustände, Projektmitglieder verwalten und `guest_view_all_features`.

**Enthaltene CE-IDs**

| CE-ID | Feature | Status (15 Anh. B) | Inkrement laut 15 | Pflicht-Ebenen | Testprojekt | E2E-Spec |
|---|---|---|---|---|---|---|
| CE-PRJ-019 | Projekt-Feature-Toggles | übernommen | I1 | L1 L2 L3 L5 L7 L8 | Funk.Projects.Tests | `web/projects/project-settings.spec.ts` |
| CE-PRJ-020 | Disabled-Feature-Zustände | übernommen | I1 | L2 L7 L8 | Frontend-only | `web/projects/project-settings.spec.ts` |
| CE-PRJ-021 | Projektmitglieder verwalten | übernommen | I1 | L1 L2 L3 L5 L7 L8 | Funk.Projects.Tests | `web/projects/project-settings.spec.ts` |
| CE-PRJ-022 | Gastzugriff auf Projektinhalte (guest_view_all_features) | übernommen | I1 | L1 L2 L3 L5 L7 L8 | Funk.Projects.Tests | `web/projects/project-settings.spec.ts` |

**Betroffene Module/Libs in `funk.`**

- Backend: `src/modules/Projects/Funk.Projects`
- Frontend: `frontend/libs/web/project-settings`

**Referenzdokumente**

- Architektur: 04 §4.4
- Architektur: 05 §3.14 (Gast-Sichtbarkeit)
- Architektur: 16 §3.2.6
- Analyse/Feature: `analysis/10a-frontend-workspace-projekt-navigation.md` §2.11
- Analyse/Feature: `analysis/02a-datenmodell-kern.md` §2.3, §3.5
- Analyse/Feature: `analysis/03-api-intern-workspace-projekt-user.md` §3.5, §3.3
- Analyse/Feature: `analysis/08-frontend-web-architektur.md` §2.2
- Analyse/Feature: `analysis/07-hintergrundjobs-mail-storage-webhooks.md` §3.18
- Analyse/Feature: `analysis/06-auth-sicherheit-querschnitt.md` §2.10
- Feature-Katalog: `features/10-ce-feature-katalog.md` (Einträge CE-PRJ-019, CE-PRJ-020, CE-PRJ-021, CE-PRJ-022)

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- Backend: `apps/api/plane/db/models/project.py`, `apps/api/plane/app/views/project/base.py`, `apps/api/plane/app/views/project/member.py`, `apps/api/plane/bgtasks/project_add_user_email_task.py`, `apps/api/plane/app/views/project/invite.py`, `apps/api/templates/emails/notifications/project_addition.html`, `apps/api/plane/app/views/issue/base.py`, `apps/api/plane/app/views/workspace/user.py`, `apps/api/plane/app/permissions/page.py`
- Frontend: `apps/web/components/settings/project/content/feature-control-item.tsx`, `apps/web/components/project/settings/features-list.tsx`, `apps/web/app/(all)/[workspaceSlug]/(settings)/settings/projects/[projectId]/features/cycles/page.tsx`, `apps/web/app/(all)/[workspaceSlug]/(settings)/settings/projects/layout.tsx`, `apps/web/app/(all)/[workspaceSlug]/(settings)/settings/projects/[projectId]/layout.tsx`, `apps/web/app/(all)/[workspaceSlug]/(settings)/settings/projects/[projectId]/page.tsx`, `apps/web/app/(all)/[workspaceSlug]/(settings)/settings/projects/[projectId]/states/page.tsx`, `apps/web/app/(all)/[workspaceSlug]/(settings)/settings/projects/[projectId]/labels/page.tsx`, `apps/web/app/(all)/[workspaceSlug]/(settings)/settings/projects/[projectId]/estimates/page.tsx`, `apps/web/app/(all)/[workspaceSlug]/(settings)/settings/projects/[projectId]/automations/page.tsx`, `packages/constants/src/settings/project.ts`, `apps/web/app/(all)/[workspaceSlug]/(projects)/projects/(detail)/[projectId]/cycles/(list)/page.tsx`, `apps/web/app/(all)/[workspaceSlug]/(projects)/projects/(detail)/[projectId]/modules/(list)/page.tsx`, `apps/web/app/(all)/[workspaceSlug]/(projects)/projects/(detail)/[projectId]/views/(list)/page.tsx`, `apps/web/app/(all)/[workspaceSlug]/(projects)/projects/(detail)/[projectId]/pages/(list)/page.tsx`, `apps/web/app/(all)/[workspaceSlug]/(projects)/projects/(detail)/[projectId]/intake/page.tsx`, `apps/web/components/project/project-settings-member-defaults.tsx`, `apps/web/components/project/member-list.tsx`, `apps/web/components/project/member-list-item.tsx`, `apps/web/components/project/send-project-invitation-modal.tsx`, `apps/web/components/project/confirm-project-member-remove.tsx`, `apps/web/components/projects/settings/useProjectColumns.tsx`, `apps/web/services/project/project-member.service.ts`

**Endpunkte (Katalog 04, `architecture/_data/endpoints.json`; 5 registriert)**

| EP | Methode | Pfad | Oberfläche | Handler | Permission | Inkr. 04 | CE-IDs |
|---|---|---|---|---|---|---|---|
| EP-0199 | GET | `/api/workspaces/{slug}/projects/{project_id}/members/` | App | ProjectMemberEndpoints.ListProjectMembersQuery | project.member.read | I1 | CE-PRJ-021 |
| EP-0200 | POST | `/api/workspaces/{slug}/projects/{project_id}/members/` | App | ProjectMemberEndpoints.CreateProjectMemberCommand | project.member.create | I1 | CE-PRJ-021 |
| EP-0202 | GET | `/api/workspaces/{slug}/projects/{project_id}/members/{pk}/` | App | ProjectMemberEndpoints.GetProjectMemberQuery | project.member.read | I1 | CE-PRJ-021 |
| EP-0203 | PATCH | `/api/workspaces/{slug}/projects/{project_id}/members/{pk}/` | App | ProjectMemberEndpoints.UpdateProjectMemberCommand | project.member.update | I1 | CE-PRJ-021 |
| EP-0204 | DELETE | `/api/workspaces/{slug}/projects/{project_id}/members/{pk}/` | App | ProjectMemberEndpoints.DeleteProjectMemberCommand | project.member.delete | I1 | CE-PRJ-021 |

**Akzeptanzkriterien**

1. Contract: je Endpunkt dieses Pakets ≥ 1 Szenario mit Golden vom Original (Erfolg, Berechtigungsfehler, Validierungsfehler); Replay grün (L5).
2. Permission-Matrix (05 Anhang B) für alle Endpunkte dieses Pakets als L3-Test grün; Tenant-Isolation geprüft.
3. Signal-Stores strukturgleich zum MobX-Original (`store-parity-check`), Vitest je Action (L2).
4. E2E-Specs dieses Pakets grün gegen Original **und** funk. (Dual-Target, Pflichtszenarien 15 §3.9.3).
5. Visual-/DOM-/a11y-Prüfpunkte der betroffenen Screens (09 §4.14, 15 §3.10.2) innerhalb der Schwellwerte 15 §3.10.3 (Chromium); i18n-Schlüssel nur aus den Original-Locales (de/en).
6. `ce-coverage-check --ids CE-PRJ-019,CE-PRJ-020,CE-PRJ-021,CE-PRJ-022` grün (Mindestebenen 15 Anhang B).

**Testumfang**

- Pflicht-Ebenen (aus 15 Anhang B): L1, L2, L3, L5, L7, L8
- Testprojekte: `Funk.Projects.Tests`, `Frontend-only`
- E2E-Specs (`frontend/apps/e2e/`): `web/projects/project-settings.spec.ts`

### WP-I1-011 – States: Gruppen, Anlage/Bearbeitung, Reihenfolge per DnD, Default-State, Löschen

| Merkmal | Wert |
|---|---|
| Inkrement | I1 |
| Typ (DoD 15 §3.15.3) | V – Vertikaler Schnitt |
| Größe | M |
| parallelisierbar | ja |
| Abhängigkeiten | WP-I1-009, WP-I1-201, WP-I0-913 |
| CE-IDs | CE-PRJ-023, CE-PRJ-024, CE-PRJ-025, CE-PRJ-026, CE-PRJ-027 |

**Ziel.** State-Verwaltung nach dem Muster des Referenzmoduls (02 §5.2) über `IStateCatalog`.

**Enthaltene CE-IDs**

| CE-ID | Feature | Status (15 Anh. B) | Inkrement laut 15 | Pflicht-Ebenen | Testprojekt | E2E-Spec |
|---|---|---|---|---|---|---|
| CE-PRJ-023 | State-Gruppen und Default-States | übernommen | I1 | L1 L2 L3 L5 L7 L8 | Funk.Projects.Tests | `web/projects/states.spec.ts` |
| CE-PRJ-024 | State anlegen und bearbeiten | übernommen | I1 | L1 L2 L3 L5 L7 L8 | Funk.Projects.Tests | `web/projects/states.spec.ts` |
| CE-PRJ-025 | State-Reihenfolge per Drag&Drop | übernommen | I1 | L1 L2 L3 L5 L7 L8 | Funk.Projects.Tests | `web/projects/states.spec.ts` |
| CE-PRJ-026 | Default-State festlegen | übernommen | I1 | L1 L2 L3 L5 L7 L8 | Funk.Projects.Tests | `web/projects/states.spec.ts` |
| CE-PRJ-027 | State löschen | übernommen | I1 | L1 L2 L3 L5 L7 L8 | Funk.Projects.Tests | `web/projects/states.spec.ts` |

**Betroffene Module/Libs in `funk.`**

- Backend: `src/modules/Projects/Funk.Projects` (States)
- Frontend: `frontend/libs/web/project-settings` (project-states)

**Referenzdokumente**

- Architektur: 04 §4.4
- Architektur: 03 §3.4.4
- Architektur: 02 §5.2
- Architektur: 16 §5.2
- Analyse/Feature: `analysis/10b-frontend-cycles-modules-pages-views-weitere.md` §2.11, §3.9
- Analyse/Feature: `analysis/02b-datenmodell-arbeitsobjekte.md` §3.7
- Analyse/Feature: `analysis/13b-shared-packages-i18n.md` §2.2
- Analyse/Feature: `analysis/03-api-intern-workspace-projekt-user.md` §3.11
- Feature-Katalog: `features/10-ce-feature-katalog.md` (Einträge CE-PRJ-023, CE-PRJ-024, CE-PRJ-025, CE-PRJ-026, CE-PRJ-027)

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- Backend: `apps/api/plane/db/models/state.py`, `apps/api/plane/app/views/project/base.py:282-296`, `apps/api/plane/app/views/state/base.py:117-138`, `apps/api/plane/db/migrations/0112_auto_20251124_0603.py`, `apps/api/plane/app/views/intake/base.py:247-257`, `apps/api/plane/app/views/state/base.py`, `apps/api/plane/app/serializers/state.py`
- Frontend: `apps/web/components/project-states/root.tsx`, `apps/web/components/project-states/group-list.tsx`, `apps/web/components/project-states/group-item.tsx`, `apps/web/components/project-states/state-list.tsx`, `apps/web/app/(all)/[workspaceSlug]/(settings)/settings/projects/[projectId]/states/page.tsx`, `packages/constants/src/state.ts`, `packages/utils/src/work-item/state.ts`, `apps/web/components/project-states/create-update/form.tsx`, `apps/web/components/project-states/create-update/create.tsx`, `apps/web/components/project-states/create-update/update.tsx`, `apps/web/services/project/project-state.service.ts`, `apps/web/components/project-states/state-item.tsx`, `apps/web/components/project-states/state-item-title.tsx`, `apps/web/components/project-states/options/mark-as-default.tsx`, `apps/web/components/project-states/options/delete.tsx`

**Endpunkte (Katalog 04, `architecture/_data/endpoints.json`; 6 registriert)**

| EP | Methode | Pfad | Oberfläche | Handler | Permission | Inkr. 04 | CE-IDs |
|---|---|---|---|---|---|---|---|
| EP-0216 | GET | `/api/workspaces/{slug}/projects/{project_id}/states/` | App | StateEndpoints.ListStatesQuery | project.state.read | I1 | CE-PRJ-023 |
| EP-0217 | POST | `/api/workspaces/{slug}/projects/{project_id}/states/` | App | StateEndpoints.CreateStateCommand | project.state.create | I1 | CE-PRJ-024 |
| EP-0218 | GET | `/api/workspaces/{slug}/projects/{project_id}/states/{pk}/` | App | StateEndpoints.GetStateQuery | project.state.read | I1 | CE-PRJ-023 |
| EP-0219 | PATCH | `/api/workspaces/{slug}/projects/{project_id}/states/{pk}/` | App | StateEndpoints.UpdateStateCommand | project.state.update | I1 | CE-PRJ-024, CE-PRJ-025 |
| EP-0220 | DELETE | `/api/workspaces/{slug}/projects/{project_id}/states/{pk}/` | App | StateEndpoints.DeleteStateCommand | project.state.delete | I1 | CE-PRJ-027 |
| EP-0221 | POST | `/api/workspaces/{slug}/projects/{project_id}/states/{pk}/mark-default/` | App | StateEndpoints.MarkDefaultStateCommand | project.state.update | I1 | CE-PRJ-026 |

**Akzeptanzkriterien**

1. Contract: je Endpunkt dieses Pakets ≥ 1 Szenario mit Golden vom Original (Erfolg, Berechtigungsfehler, Validierungsfehler); Replay grün (L5).
2. Permission-Matrix (05 Anhang B) für alle Endpunkte dieses Pakets als L3-Test grün; Tenant-Isolation geprüft.
3. Signal-Stores strukturgleich zum MobX-Original (`store-parity-check`), Vitest je Action (L2).
4. E2E-Specs dieses Pakets grün gegen Original **und** funk. (Dual-Target, Pflichtszenarien 15 §3.9.3).
5. Visual-/DOM-/a11y-Prüfpunkte der betroffenen Screens (09 §4.14, 15 §3.10.2) innerhalb der Schwellwerte 15 §3.10.3 (Chromium); i18n-Schlüssel nur aus den Original-Locales (de/en).
6. `ce-coverage-check --ids CE-PRJ-023,CE-PRJ-024,CE-PRJ-025,CE-PRJ-026,CE-PRJ-027` grün (Mindestebenen 15 Anhang B).

**Testumfang**

- Pflicht-Ebenen (aus 15 Anhang B): L1, L2, L3, L5, L7, L8
- Testprojekte: `Funk.Projects.Tests`
- E2E-Specs (`frontend/apps/e2e/`): `web/projects/states.spec.ts`

### WP-I1-012 – Labels – Referenzmodul (Hierarchie, Anlage, DnD-Gruppierung, Löschen, Bulk-Import)

| Merkmal | Wert |
|---|---|
| Inkrement | I1 |
| Typ (DoD 15 §3.15.3) | V – Vertikaler Schnitt |
| Größe | M |
| parallelisierbar | ja |
| Abhängigkeiten | WP-I1-009, WP-I1-201, WP-I1-204, WP-I0-913 |
| CE-IDs | CE-PRJ-028, CE-PRJ-029, CE-PRJ-030, CE-PRJ-031, CE-PRJ-032, CE-PRJ-033 |

**Ziel.** Vollständige Umsetzung des in 02 §5.2 ausgearbeiteten Referenzmoduls Labels – Vorlage für alle weiteren Module (Dateinamen, Commands, Validatoren, Endpunkte, Activity-Beitrag, Tests).

**Enthaltene CE-IDs**

| CE-ID | Feature | Status (15 Anh. B) | Inkrement laut 15 | Pflicht-Ebenen | Testprojekt | E2E-Spec |
|---|---|---|---|---|---|---|
| CE-PRJ-028 | Label-Liste mit Hierarchie | übernommen | I1 | L1 L2 L3 L5 L7 L8 | Funk.Projects.Tests | `web/projects/labels.spec.ts` |
| CE-PRJ-029 | Label anlegen und bearbeiten | übernommen | I1 | L1 L2 L3 L5 L7 L8 | Funk.Projects.Tests | `web/projects/labels.spec.ts` |
| CE-PRJ-030 | Labels per Drag&Drop ordnen und gruppieren | übernommen | I1 | L1 L2 L3 L5 L7 L8 | Funk.Projects.Tests | `web/projects/labels.spec.ts` |
| CE-PRJ-031 | Label aus Gruppe entfernen | übernommen | I1 | L1 L2 L3 L5 L7 L8 | Funk.Projects.Tests | `web/projects/labels.spec.ts` |
| CE-PRJ-032 | Label löschen | übernommen | I1 | L1 L2 L3 L5 L7 L8 | Funk.Projects.Tests | `web/projects/labels.spec.ts` |
| CE-PRJ-033 | Labels per Bulk-Import (nur API) | übernommen | I1 | L1 L2 L3 L5 L7 L8 | Funk.Projects.Tests | `web/projects/labels.spec.ts` |

**Betroffene Module/Libs in `funk.`**

- Backend: `src/modules/Projects/Funk.Projects` (Label*, siehe 02 §5.2.1–§5.2.13)
- Backend: `tests/modules/Funk.Projects.Tests` (02 §5.2.13)
- Frontend: `frontend/libs/web/project-settings` (labels)
- Frontend: `frontend/tools/contract-check/checks/labels.check.ts`

**Referenzdokumente**

- Architektur: 02 §5.2 (vollständig)
- Architektur: 04 §4.4, §5.7, §5.8
- Architektur: 03 §3.4.4
- Architektur: 15 §3.6.2 (Szenario labels-crud)
- Analyse/Feature: `analysis/10b-frontend-cycles-modules-pages-views-weitere.md` §2.10, §3.8
- Analyse/Feature: `analysis/02b-datenmodell-arbeitsobjekte.md` §3.3
- Analyse/Feature: `analysis/04-api-intern-arbeitsobjekte.md` §2.3
- Analyse/Feature: `analysis/13b-shared-packages-i18n.md` §2.4
- Feature-Katalog: `features/10-ce-feature-katalog.md` (Einträge CE-PRJ-028, CE-PRJ-029, CE-PRJ-030, CE-PRJ-031, CE-PRJ-032, CE-PRJ-033)

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- Backend: `apps/api/plane/db/models/label.py`, `apps/api/plane/app/views/issue/label.py:90-112`, `apps/api/plane/app/views/issue/label.py`, `apps/api/plane/app/serializers/issue.py`
- Frontend: `apps/web/components/labels/project-setting-label-list.tsx`, `apps/web/components/labels/project-setting-label-group.tsx`, `apps/web/components/labels/project-setting-label-item.tsx`, `apps/web/components/labels/label-block/label-item-block.tsx`, `apps/web/components/labels/label-block/label-name.tsx`, `apps/web/app/(all)/[workspaceSlug]/(settings)/settings/projects/[projectId]/labels/page.tsx`, `apps/web/components/labels/create-update-label-inline.tsx`, `packages/constants/src/label.ts`, `packages/utils/src/color.ts`, `packages/utils/src/string.ts`, `apps/web/components/labels/label-drag-n-drop-HOC.tsx`, `apps/web/components/labels/label-utils.ts`, `apps/web/store/label.store.ts`, `apps/web/components/labels/delete-label-modal.tsx`

**Endpunkte (Katalog 04, `architecture/_data/endpoints.json`; 6 registriert)**

| EP | Methode | Pfad | Oberfläche | Handler | Permission | Inkr. 04 | CE-IDs |
|---|---|---|---|---|---|---|---|
| EP-0177 | POST | `/api/workspaces/{slug}/projects/{project_id}/bulk-create-labels/` | App | LabelEndpoints.BulkCreateLabelsCommand | project.label.create | I1 | CE-PRJ-033 |
| EP-0178 | GET | `/api/workspaces/{slug}/projects/{project_id}/issue-labels/` | App | LabelEndpoints.ListLabelsQuery | project.label.read | I1 | CE-PRJ-028 |
| EP-0179 | POST | `/api/workspaces/{slug}/projects/{project_id}/issue-labels/` | App | LabelEndpoints.CreateLabelCommand | project.label.create | I1 | CE-PRJ-029 |
| EP-0180 | GET | `/api/workspaces/{slug}/projects/{project_id}/issue-labels/{pk}/` | App | LabelEndpoints.GetLabelQuery | project.label.read | I1 | CE-PRJ-028 |
| EP-0181 | PATCH | `/api/workspaces/{slug}/projects/{project_id}/issue-labels/{pk}/` | App | LabelEndpoints.UpdateLabelCommand | project.label.update | I1 | CE-PRJ-029, CE-PRJ-030, CE-PRJ-031 |
| EP-0182 | DELETE | `/api/workspaces/{slug}/projects/{project_id}/issue-labels/{pk}/` | App | LabelEndpoints.DeleteLabelCommand | project.label.delete | I1 | CE-PRJ-032 |

**Akzeptanzkriterien**

1. Code entspricht den Skeletten 02 §5.2 (Review-Checkliste); O-D02-05 (View-Filter-Bereinigung) im Harness geprüft und entschieden.
2. Contract: je Endpunkt dieses Pakets ≥ 1 Szenario mit Golden vom Original (Erfolg, Berechtigungsfehler, Validierungsfehler); Replay grün (L5).
3. Permission-Matrix (05 Anhang B) für alle Endpunkte dieses Pakets als L3-Test grün; Tenant-Isolation geprüft.
4. Signal-Stores strukturgleich zum MobX-Original (`store-parity-check`), Vitest je Action (L2).
5. E2E-Specs dieses Pakets grün gegen Original **und** funk. (Dual-Target, Pflichtszenarien 15 §3.9.3).
6. Visual-/DOM-/a11y-Prüfpunkte der betroffenen Screens (09 §4.14, 15 §3.10.2) innerhalb der Schwellwerte 15 §3.10.3 (Chromium); i18n-Schlüssel nur aus den Original-Locales (de/en).
7. `ce-coverage-check --ids CE-PRJ-028,CE-PRJ-029,CE-PRJ-030,CE-PRJ-031,CE-PRJ-032,CE-PRJ-033` grün (Mindestebenen 15 Anhang B).

**Testumfang**

- Pflicht-Ebenen (aus 15 Anhang B): L1, L2, L3, L5, L7, L8
- Testprojekte: `Funk.Projects.Tests`
- E2E-Specs (`frontend/apps/e2e/`): `web/projects/labels.spec.ts`

### WP-I1-013 – Estimates: Einstellungen, Schätzsystem anlegen/ändern/löschen, Validierung

| Merkmal | Wert |
|---|---|
| Inkrement | I1 |
| Typ (DoD 15 §3.15.3) | V – Vertikaler Schnitt |
| Größe | M |
| parallelisierbar | ja |
| Abhängigkeiten | WP-I1-009, WP-I1-203 |
| CE-IDs | CE-PRJ-034, CE-PRJ-035, CE-PRJ-036, CE-PRJ-037, CE-PRJ-038 |

**Ziel.** Estimates-Einstellungen mit Schätzsystemen (Punkte, Kategorien; Zeit über `ESTIMATE_SYSTEM_FLAGS` aus), Schätzwert-Validierung, Ändern/Löschen von Punkten und Systemen.

**Enthaltene CE-IDs**

| CE-ID | Feature | Status (15 Anh. B) | Inkrement laut 15 | Pflicht-Ebenen | Testprojekt | E2E-Spec |
|---|---|---|---|---|---|---|
| CE-PRJ-034 | Estimates-Einstellungen | übernommen | I1 | L1 L2 L3 L5 L7 L8 | Funk.Projects.Tests | `web/projects/estimates.spec.ts` |
| CE-PRJ-035 | Schätzsystem anlegen | übernommen | I1 | L1 L2 L3 L5 L7 L8 | Funk.Projects.Tests | `web/projects/estimates.spec.ts` |
| CE-PRJ-036 | Schätzwert-Validierung | übernommen | I1 | L1 L2 L3 L5 L7 L8 | Funk.Projects.Tests | `web/projects/estimates.spec.ts` |
| CE-PRJ-037 | Schätzpunkte ändern und löschen (Backend) | übernommen | I1 | L1 L2 L3 L5 L7 L8 | Funk.Projects.Tests | `web/projects/estimates.spec.ts` |
| CE-PRJ-038 | Schätzsystem löschen | übernommen | I1 | L1 L2 L3 L5 L7 L8 | Funk.Projects.Tests | `web/projects/estimates.spec.ts` |

**Betroffene Module/Libs in `funk.`**

- Backend: `src/modules/Projects/Funk.Projects` (Estimates)
- Frontend: `frontend/libs/web/project-settings` (estimates)

**Referenzdokumente**

- Architektur: 04 §4.4
- Architektur: 03 §3.4.4
- Architektur: 16 §3.3.0 E-14
- Analyse/Feature: `analysis/10b-frontend-cycles-modules-pages-views-weitere.md` §2.9
- Analyse/Feature: `analysis/03-api-intern-workspace-projekt-user.md` §3.11
- Analyse/Feature: `analysis/02b-datenmodell-arbeitsobjekte.md` §2.3
- Analyse/Feature: `analysis/13b-shared-packages-i18n.md` §2.2
- Feature-Katalog: `features/10-ce-feature-katalog.md` (Einträge CE-PRJ-034, CE-PRJ-035, CE-PRJ-036, CE-PRJ-037, CE-PRJ-038)

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- Backend: `apps/api/plane/app/views/estimate/base.py`, `apps/api/plane/app/serializers/estimate.py`, `apps/api/plane/db/models/estimate.py`
- Frontend: `apps/web/components/estimates/root.tsx`, `apps/web/components/estimates/estimate-disable-switch.tsx`, `apps/web/components/estimates/estimate-list.tsx`, `apps/web/components/estimates/estimate-list-item.tsx`, `apps/web/app/(all)/[workspaceSlug]/(settings)/settings/projects/[projectId]/estimates/page.tsx`, `apps/web/services/estimate.service.ts`, `apps/web/components/estimates/`, `packages/constants/src/estimates.ts:12-140`, `apps/web/components/estimates/create/modal.tsx`, `apps/web/components/estimates/create/stage-one.tsx`, `apps/web/components/estimates/radio-select.tsx`, `apps/web/components/estimates/points/create-root.tsx`, `apps/web/components/estimates/points/preview.tsx`, `apps/web/components/estimates/points/create.tsx`, `apps/web/components/estimates/points/update.tsx`, `apps/web/components/estimates/inputs/root.tsx`, `apps/web/components/estimates/inputs/number-input.tsx`, `apps/web/components/estimates/inputs/text-input.tsx`, `packages/constants/src/estimates.ts`, `packages/utils/src/estimates.ts`, `apps/web/components/estimates/delete/modal.tsx`, `apps/web/components/estimates/estimate-list-item-buttons.tsx`

**Endpunkte (Katalog 04, `architecture/_data/endpoints.json`; 9 registriert)**

| EP | Methode | Pfad | Oberfläche | Handler | Permission | Inkr. 04 | CE-IDs |
|---|---|---|---|---|---|---|---|
| EP-0168 | GET | `/api/workspaces/{slug}/projects/{project_id}/estimates/` | App | EstimateEndpoints.ListEstimatesQuery | project.estimate.read | I1 | CE-PRJ-034 |
| EP-0169 | POST | `/api/workspaces/{slug}/projects/{project_id}/estimates/` | App | EstimateEndpoints.CreateEstimateCommand | project.estimate.create | I1 | CE-PRJ-035, CE-PRJ-036 |
| EP-0170 | GET | `/api/workspaces/{slug}/projects/{project_id}/estimates/{estimate_id}/` | App | EstimateEndpoints.GetEstimateQuery | project.estimate.read | I1 | CE-PRJ-034 |
| EP-0171 | PATCH | `/api/workspaces/{slug}/projects/{project_id}/estimates/{estimate_id}/` | App | EstimateEndpoints.UpdateEstimateCommand | project.estimate.update | I1 | CE-PRJ-035, CE-PRJ-036 |
| EP-0172 | DELETE | `/api/workspaces/{slug}/projects/{project_id}/estimates/{estimate_id}/` | App | EstimateEndpoints.DeleteEstimateCommand | project.estimate.delete | I1 | CE-PRJ-038 |
| EP-0173 | POST | `/api/workspaces/{slug}/projects/{project_id}/estimates/{estimate_id}/estimate-points/` | App | EstimateEndpoints.CreateEstimatePointCommand | project.estimate.create | I1 | CE-PRJ-036, CE-PRJ-037 |
| EP-0174 | PATCH | `/api/workspaces/{slug}/projects/{project_id}/estimates/{estimate_id}/estimate-points/{estimate_point_id}/` | App | EstimateEndpoints.UpdateEstimatePointCommand | project.estimate.update | I1 | CE-PRJ-036, CE-PRJ-037 |
| EP-0175 | DELETE | `/api/workspaces/{slug}/projects/{project_id}/estimates/{estimate_id}/estimate-points/{estimate_point_id}/` | App | EstimateEndpoints.DeleteEstimatePointCommand | project.estimate.delete | I1 | CE-PRJ-036, CE-PRJ-037 |
| EP-0176 | GET | `/api/workspaces/{slug}/projects/{project_id}/project-estimates/` | App | EstimateEndpoints.ListProjectEstimatePointsQuery | project.estimate.read_points | I1 | CE-PRJ-034 |

**Akzeptanzkriterien**

1. Contract: je Endpunkt dieses Pakets ≥ 1 Szenario mit Golden vom Original (Erfolg, Berechtigungsfehler, Validierungsfehler); Replay grün (L5).
2. Permission-Matrix (05 Anhang B) für alle Endpunkte dieses Pakets als L3-Test grün; Tenant-Isolation geprüft.
3. Signal-Stores strukturgleich zum MobX-Original (`store-parity-check`), Vitest je Action (L2).
4. E2E-Specs dieses Pakets grün gegen Original **und** funk. (Dual-Target, Pflichtszenarien 15 §3.9.3).
5. Visual-/DOM-/a11y-Prüfpunkte der betroffenen Screens (09 §4.14, 15 §3.10.2) innerhalb der Schwellwerte 15 §3.10.3 (Chromium); i18n-Schlüssel nur aus den Original-Locales (de/en).
6. `ce-coverage-check --ids CE-PRJ-034,CE-PRJ-035,CE-PRJ-036,CE-PRJ-037,CE-PRJ-038` grün (Mindestebenen 15 Anhang B).

**Testumfang**

- Pflicht-Ebenen (aus 15 Anhang B): L1, L2, L3, L5, L7, L8
- Testprojekte: `Funk.Projects.Tests`
- E2E-Specs (`frontend/apps/e2e/`): `web/projects/estimates.spec.ts`

### WP-I1-014 – Profil und persönliche Einstellungen (inkl. angepasster E-Mail-Änderung und Konto-Deaktivierung)

| Merkmal | Wert |
|---|---|
| Inkrement | I1 |
| Typ (DoD 15 §3.15.3) | V – Vertikaler Schnitt |
| Größe | M |
| parallelisierbar | ja |
| Abhängigkeiten | WP-I0-999, WP-I1-103 |
| CE-IDs | CE-PROF-001, CE-PROF-002, CE-PROF-003, CE-PROF-004, CE-PROF-005, CE-PROF-006 |

**Ziel.** Profil-Datenmodell, Profil-Einstellungen (Modal und Seite), Profil bearbeiten, Sprache/Zeitzone/Wochenstart; E-Mail-Änderung öffnet die Keycloak-Kontokonsole (DEV-UI-04), Konto deaktivieren wirkt in funk., Sperre in Keycloak.

**Enthaltene CE-IDs**

| CE-ID | Feature | Status (15 Anh. B) | Inkrement laut 15 | Pflicht-Ebenen | Testprojekt | E2E-Spec |
|---|---|---|---|---|---|---|
| CE-PROF-001 | Profil-Datenmodell und persönliche Einstellungen | übernommen | I1 | L1 L2 L3 L5 L7 L8 | Funk.Identity.Tests | `web/profile/profile-settings.spec.ts` |
| CE-PROF-002 | Profil-Einstellungen (Modal und Seite) | übernommen | I1 | L1 L2 L3 L5 L7 L8 | Funk.Identity.Tests | `web/profile/profile-settings.spec.ts` |
| CE-PROF-003 | Profil bearbeiten | übernommen | I1 | L1 L2 L3 L5 L7 L8 | Funk.Identity.Tests | `web/profile/profile-settings.spec.ts` |
| CE-PROF-004 | E-Mail-Adresse ändern | angepasst | I1 | L1 L2 L3 L5 L7 L8 | Funk.Identity.Tests | `web/profile/profile-settings.spec.ts` |
| CE-PROF-005 | Konto deaktivieren | angepasst | I1 | L1 L2 L3 L5 L7 L8 | Funk.Identity.Tests | `web/profile/profile-settings.spec.ts` |
| CE-PROF-006 | Sprache, Zeitzone und Wochenstart (Preferences) | übernommen | I1 | L1 L2 L3 L5 L7 L8 | Funk.Identity.Tests | `web/profile/profile-settings.spec.ts` |

**Betroffene Module/Libs in `funk.`**

- Backend: `src/modules/Identity/Funk.Identity` (Profile, Preferences)
- Frontend: `frontend/libs/web/profile`

**Referenzdokumente**

- Architektur: 05 §3.10, §4.1, D05-ADR-08
- Architektur: 04 §4.1
- Architektur: 03 §3.4.1
- Analyse/Feature: `analysis/02a-datenmodell-kern.md` §2.3
- Analyse/Feature: `analysis/03-api-intern-workspace-projekt-user.md` §3.6
- Analyse/Feature: `analysis/10a-frontend-workspace-projekt-navigation.md` §2.13
- Analyse/Feature: `analysis/08-frontend-web-architektur.md` §2.2
- Analyse/Feature: `analysis/13b-shared-packages-i18n.md` §2.2, §3.8
- Analyse/Feature: `analysis/06-auth-sicherheit-querschnitt.md` §3.18
- Analyse/Feature: `analysis/07-hintergrundjobs-mail-storage-webhooks.md` §3.18
- Feature-Katalog: `features/10-ce-feature-katalog.md` (Einträge CE-PROF-001, CE-PROF-002, CE-PROF-003, CE-PROF-004, CE-PROF-005, CE-PROF-006)

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- Backend: `apps/api/plane/db/models/user.py`, `apps/api/plane/app/views/user/base.py`, `apps/api/plane/app/serializers/user.py`, `apps/api/plane/bgtasks/user_email_update_task.py`, `apps/api/templates/emails/user/email_updated.html`, `apps/api/plane/bgtasks/user_deactivation_email_task.py`, `apps/api/plane/bgtasks/user_activation_email_task.py`, `apps/api/plane/authentication/adapter/base.py`
- Frontend: `apps/web/store/user/profile.store.ts`, `packages/types/src/users.ts`, `packages/constants/src/themes.ts`, `apps/web/components/settings/profile/modal.tsx`, `apps/web/components/settings/profile/sidebar/root.tsx`, `apps/web/components/settings/profile/content/root.tsx`, `apps/web/app/(all)/settings/profile/[profileTabId]/page.tsx`, `apps/web/app/(all)/settings/profile/layout.tsx`, `apps/web/components/common/modal/global.tsx`, `packages/constants/src/settings/profile.ts`, `apps/web/store/workspace/api-token.store.ts`, `packages/constants/src/settings/project.ts`, `packages/constants/src/settings/workspace.ts`, `apps/web/components/settings/profile/content/pages/general/form.tsx`, `apps/web/components/core/modals/user-image-upload-modal.tsx`, `apps/web/components/core/image-picker-popover.tsx`, `apps/web/components/core/modals/change-email-modal.tsx`, `apps/web/services/user.service.ts`, `apps/web/components/account/deactivate-account-modal.tsx`, `apps/web/components/settings/profile/content/pages/preferences/language-and-timezone-list.tsx`, `apps/web/components/profile/start-of-week-preference.tsx`, `apps/web/components/global/timezone-select.tsx`, `packages/utils/src/calendar.ts`, `packages/constants/src/calendar.ts`, `packages/constants/src/profile.ts`

**Endpunkte (Katalog 04, `architecture/_data/endpoints.json`; 7 registriert)**

| EP | Methode | Pfad | Oberfläche | Handler | Permission | Inkr. 04 | CE-IDs |
|---|---|---|---|---|---|---|---|
| EP-0050 | DELETE | `/api/users/me/` | App | CurrentUserEndpoints.DeactivateCurrentUserCommand | user.user.deactivate | I1 | CE-PROF-005 |
| EP-0057 | GET | `/api/timezones/` | App | TimezoneEndpoints.ListTimezonesQuery | user.timezone.read | I1 | CE-PROF-006 |
| EP-0059 | GET | `/api/users/me/profile/` | App | UserProfileEndpoints.GetCurrentUserProfileQuery | user.user_profile.read | I1 | CE-PROF-001 |
| EP-0060 | PATCH | `/api/users/me/profile/` | App | UserProfileEndpoints.UpdateCurrentUserProfileCommand | user.user_profile.update | I1 | CE-PROF-006 |
| EP-0424 | POST | `/api/assets/v2/user-assets/` | App | UserAssetEndpoints.CreateUserAssetUploadCommand | user.user_asset.create | I1 | CE-PROF-003, CE-OPS-013 |
| EP-0425 | PATCH | `/api/assets/v2/user-assets/{asset_id}/` | App | UserAssetEndpoints.ConfirmUserAssetUploadCommand | user.user_asset.update | I1 | CE-PROF-003, CE-OPS-013 |
| EP-0426 | DELETE | `/api/assets/v2/user-assets/{asset_id}/` | App | UserAssetEndpoints.DeleteUserAssetCommand | user.user_asset.delete | I1 | CE-PROF-003, CE-OPS-013 |

**Akzeptanzkriterien**

1. Contract: je Endpunkt dieses Pakets ≥ 1 Szenario mit Golden vom Original (Erfolg, Berechtigungsfehler, Validierungsfehler); Replay grün (L5).
2. Permission-Matrix (05 Anhang B) für alle Endpunkte dieses Pakets als L3-Test grün; Tenant-Isolation geprüft.
3. Signal-Stores strukturgleich zum MobX-Original (`store-parity-check`), Vitest je Action (L2).
4. E2E-Specs dieses Pakets grün gegen Original **und** funk. (Dual-Target, Pflichtszenarien 15 §3.9.3).
5. Visual-/DOM-/a11y-Prüfpunkte der betroffenen Screens (09 §4.14, 15 §3.10.2) innerhalb der Schwellwerte 15 §3.10.3 (Chromium); i18n-Schlüssel nur aus den Original-Locales (de/en).
6. `ce-coverage-check --ids CE-PROF-001,CE-PROF-002,CE-PROF-003,CE-PROF-004,CE-PROF-005,CE-PROF-006` grün (Mindestebenen 15 Anhang B).

**Testumfang**

- Pflicht-Ebenen (aus 15 Anhang B): L1, L2, L3, L5, L7, L8
- Testprojekte: `Funk.Identity.Tests`
- E2E-Specs (`frontend/apps/e2e/`): `web/profile/profile-settings.spec.ts`

### WP-I1-015 – Onboarding

| Merkmal | Wert |
|---|---|
| Inkrement | I1 |
| Typ (DoD 15 §3.15.3) | V – Vertikaler Schnitt |
| Größe | M |
| parallelisierbar | ja |
| Abhängigkeiten | WP-I1-014, WP-I1-002 |
| CE-IDs | CE-AUTH-030 |

**Ziel.** Onboarding-Ablauf nach dem ersten Login (Profil, Workspace anlegen oder Einladung annehmen) wie Original, ohne Passwortschritt.

**Enthaltene CE-IDs**

| CE-ID | Feature | Status (15 Anh. B) | Inkrement laut 15 | Pflicht-Ebenen | Testprojekt | E2E-Spec |
|---|---|---|---|---|---|---|
| CE-AUTH-030 | Onboarding | angepasst | I1 | L1 L2 L3 L5 L7 L8 | Funk.Identity.Tests | `web/auth/onboarding.spec.ts` |

**Betroffene Module/Libs in `funk.`**

- Backend: `src/modules/Identity/Funk.Identity`
- Frontend: `frontend/libs/web/auth` (onboarding)

**Referenzdokumente**

- Architektur: 05 §4.1
- Architektur: 08 §4.1
- Analyse/Feature: `analysis/10a-frontend-workspace-projekt-navigation.md` §2.15
- Analyse/Feature: `analysis/08-frontend-web-architektur.md` §2.2
- Analyse/Feature: `analysis/13b-shared-packages-i18n.md` §3.10
- Analyse/Feature: `analysis/03-api-intern-workspace-projekt-user.md` §3.6
- Feature-Katalog: `features/10-ce-feature-katalog.md` (Einträge CE-AUTH-030)

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- Backend: `apps/api/plane/app/views/user/base.py`, `apps/api/plane/db/models/user.py`
- Frontend: `apps/web/components/onboarding/root.tsx`, `apps/web/components/onboarding/header.tsx`, `apps/web/components/onboarding/steps/root.tsx`, `apps/web/components/onboarding/steps/profile/root.tsx`, `apps/web/components/onboarding/steps/workspace/create.tsx`, `apps/web/components/onboarding/steps/workspace/join-invites.tsx`, `apps/web/components/onboarding/steps/team/root.tsx`, `apps/web/components/onboarding/switch-account-dropdown.tsx`, `apps/web/app/(all)/onboarding/page.tsx`, `apps/web/components/onboarding`, `packages/constants/src/workspace.ts`, `packages/utils/src/validation.ts`, `packages/services/src/workspace/workspace.service.ts`, `packages/services/src/workspace/instance-workspace.service.ts`

**Endpunkte (Katalog 04, `architecture/_data/endpoints.json`; 1 registriert)**

| EP | Methode | Pfad | Oberfläche | Handler | Permission | Inkr. 04 | CE-IDs |
|---|---|---|---|---|---|---|---|
| EP-0054 (vorab) | PATCH | `/api/users/me/tour-completed/` | App | CurrentUserEndpoints.CompleteProductTourCommand | user.user.update | I1 | CE-HOME-006 |

**Akzeptanzkriterien**

1. Contract: je Endpunkt dieses Pakets ≥ 1 Szenario mit Golden vom Original (Erfolg, Berechtigungsfehler, Validierungsfehler); Replay grün (L5).
2. Permission-Matrix (05 Anhang B) für alle Endpunkte dieses Pakets als L3-Test grün; Tenant-Isolation geprüft.
3. Signal-Stores strukturgleich zum MobX-Original (`store-parity-check`), Vitest je Action (L2).
4. E2E-Specs dieses Pakets grün gegen Original **und** funk. (Dual-Target, Pflichtszenarien 15 §3.9.3).
5. Visual-/DOM-/a11y-Prüfpunkte der betroffenen Screens (09 §4.14, 15 §3.10.2) innerhalb der Schwellwerte 15 §3.10.3 (Chromium); i18n-Schlüssel nur aus den Original-Locales (de/en).
6. `ce-coverage-check --ids CE-AUTH-030` grün (Mindestebenen 15 Anhang B).

**Testumfang**

- Pflicht-Ebenen (aus 15 Anhang B): L1, L2, L3, L5, L7, L8
- Testprojekte: `Funk.Identity.Tests`
- E2E-Specs (`frontend/apps/e2e/`): `web/auth/onboarding.spec.ts`

### WP-I1-016 – Rate-Limits gegen Brute-Force und Missbrauch

| Merkmal | Wert |
|---|---|
| Inkrement | I1 |
| Typ (DoD 15 §3.15.3) | B – Backend-only |
| Größe | S |
| parallelisierbar | ja |
| Abhängigkeiten | WP-I1-104 |
| CE-IDs | CE-AUTH-026 |

**Ziel.** Rate-Limit-Policies (`anon`, `user`, Callback-Limiter `AuthCallbackRateLimiter`, Integrations) mit Original-Grenzwerten und Header-Verhalten.

**Enthaltene CE-IDs**

| CE-ID | Feature | Status (15 Anh. B) | Inkrement laut 15 | Pflicht-Ebenen | Testprojekt | E2E-Spec |
|---|---|---|---|---|---|---|
| CE-AUTH-026 | Rate-Limits gegen Brute-Force und Missbrauch | angepasst | I1 | L1 L3 | Funk.Identity.Tests | – |

**Betroffene Module/Libs in `funk.`**

- Backend: `src/building-blocks/Funk.BuildingBlocks.Web/RateLimiting/`
- Backend: `src/modules/Identity/Funk.Identity/Authentication/AuthCallbackRateLimiter.cs`

**Referenzdokumente**

- Architektur: 05 §3.17.6
- Architektur: 02 §3.13, O-D02-07
- Architektur: 04 §3.12
- Analyse/Feature: `analysis/06-auth-sicherheit-querschnitt.md` §2.9
- Analyse/Feature: `analysis/01-gesamtarchitektur-infrastruktur.md` §2.15
- Feature-Katalog: `features/10-ce-feature-katalog.md` (Einträge CE-AUTH-026)

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- Backend: `apps/api/plane/authentication/rate_limit.py`, `apps/api/plane/throttles/asset.py`, `apps/api/plane/api/rate_limit.py`, `apps/api/plane/authentication/adapter/exception.py`, `apps/api/plane/api/views/base.py`

**Akzeptanzkriterien**

1. `RateLimitPolicyTests` inkl. `Callback_11thRequest_Redirects5900`; Grenzwert ±1 gegen Original (DEV-RL-001).
2. Contract-Szenarien mit Original-Golden für alle HTTP-Endpunkte dieses Pakets; Replay grün.
3. Job-/Consumer-Tests: Idempotenz (Inbox), Retry/Backoff, Zeitsteuerung mit `FixedClock`; neue Ereignistypen im Event-Katalog-Snapshot.
4. Bei Cron-Jobs: Registrierung in `CronRegistrationTests` mit Original-Zeit (UTC).
5. `ce-coverage-check --ids CE-AUTH-026` grün (Mindestebenen 15 Anhang B).

**Testumfang**

- Pflicht-Ebenen (aus 15 Anhang B): L1, L3
- Testprojekte: `Funk.Identity.Tests`

### WP-I1-017 – Sprachen de/en, Übersetzungen mit Fallback/ICU, Datums-/Zeitdarstellung, Zeitzonen

| Merkmal | Wert |
|---|---|
| Inkrement | I1 |
| Typ (DoD 15 §3.15.3) | F – Frontend-only |
| Größe | M |
| parallelisierbar | ja |
| Abhängigkeiten | WP-I1-014 |
| CE-IDs | CE-I18N-001, CE-I18N-002, CE-I18N-003, CE-I18N-004 |

**Ziel.** Sprachauswahl (nur Deutsch und Englisch, Standard Deutsch, ADR-009D) mit Server-Persistenz, `TranslationService` mit Fallback und ICU-Plural, deutsche Texte aus `packages/i18n/src/locales/de` gebrandet (BR-10) und fehlende Schlüssel ergänzt; Datums-/Zeitdarstellung und Zeitzonen-Umrechnung wie Original.

**Enthaltene CE-IDs**

| CE-ID | Feature | Status (15 Anh. B) | Inkrement laut 15 | Pflicht-Ebenen | Testprojekt | E2E-Spec |
|---|---|---|---|---|---|---|
| CE-I18N-001 | Sprachauswahl und Persistenz | übernommen | I1 | L2 L4 L7 L8 (G-I18N) | Frontend-only | `web/i18n/language-timezone.spec.ts` |
| CE-I18N-002 | Übersetzte UI-Texte mit Fallback und ICU-Pluralisierung | übernommen | I1 | L2 L4 L7 L8 (G-I18N) | Frontend-only | `web/i18n/language-timezone.spec.ts` |
| CE-I18N-003 | Datums- und Zeitdarstellung | übernommen | I1 | L2 L7 L8 | Frontend-only | `web/i18n/language-timezone.spec.ts` |
| CE-I18N-004 | Zeitzonen-Auswahl und -Umrechnung | übernommen | I1 | L2 L7 L8 | Frontend-only | `web/i18n/language-timezone.spec.ts` |

**Betroffene Module/Libs in `funk.`**

- Frontend: `frontend/libs/shared/i18n` (`locales/de`, `locales/en`, `brand/{de,en}.json`)
- Frontend: `frontend/tools/i18n-sync-check`

**Referenzdokumente**

- Architektur: 08 §3.7, §5.13, O-D08-08
- Architektur: 00 ADR-009D
- Architektur: 17 Z-113
- Analyse/Feature: `analysis/13b-shared-packages-i18n.md` §2.1, §2.4
- Analyse/Feature: `analysis/08-frontend-web-architektur.md` §3.9, §2.8
- Analyse/Feature: `analysis/10a-frontend-workspace-projekt-navigation.md` §2.13, §2.16
- Analyse/Feature: `analysis/02a-datenmodell-kern.md` §2.3
- Analyse/Feature: `analysis/03-api-intern-workspace-projekt-user.md` §3.18
- Analyse/Feature: `analysis/06-auth-sicherheit-querschnitt.md` §2.13
- Feature-Katalog: `features/10-ce-feature-katalog.md` (Einträge CE-I18N-001, CE-I18N-002, CE-I18N-003, CE-I18N-004)

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- Backend: `apps/api/plane/db/models/user.py`, `apps/api/plane/app/views/timezone/base.py`, `apps/api/plane/utils/timezone_converter.py`, `apps/api/plane/app/views/base.py`
- Frontend: `packages/i18n/src/constants/language.ts`, `packages/i18n/src/core/set-language.ts`, `packages/i18n/src/hooks/use-translation.ts`, `apps/web/components/settings/profile/content/pages/preferences/language-and-timezone-list.tsx`, `apps/web/components/power-k/ui/pages/preferences/languages-menu.tsx`, `apps/web/store/user/profile.store.ts`, `apps/web/store/root.store.ts`, `apps/web/app/entry.client.tsx`, `apps/web/app/provider.tsx`, `apps/web/components/profile/start-of-week-preference.tsx`, `apps/web/components/global/timezone-select.tsx`, `packages/types/src/users.ts`, `packages/constants/src/themes.ts`, `packages/i18n/src/core/instance.ts`, `packages/i18n/src/locales/en/*.json`, `packages/utils/src/datetime.ts`, `packages/utils/src/filter.ts`, `apps/web/services/timezone.service.ts`, `apps/web/hooks/use-timezone.tsx`, `apps/web/hooks/use-timezone-converter.tsx`

**Akzeptanzkriterien**

1. `i18n-sync-check`: jeder in `en` vorhandene Schlüssel existiert in `de` (fehlende ergänzt, Liste in `ui-deviations.yaml`); Sprachauswahl zeigt genau zwei Sprachen.
2. Datumsformat nach Entscheidung OP-PLAN-06 (plan/04).
3. Galerie-Eintrag mit allen Varianten/Zuständen; DOM-Vertrag = Referenz-Galerie; Visual in allen Themes (Chromium).
4. Tastatur/Fokus (AX3/AX4) wie Original; portierte `packages/blocks`-Tests grün (falls vorhanden).
5. `ce-coverage-check --ids CE-I18N-001,CE-I18N-002,CE-I18N-003,CE-I18N-004` grün (Mindestebenen 15 Anhang B).

**Testumfang**

- Pflicht-Ebenen (aus 15 Anhang B): L2, L4, L7, L8
- Testprojekte: `Frontend-only`
- E2E-Specs (`frontend/apps/e2e/`): `web/i18n/language-timezone.spec.ts`

### WP-I1-018 – Themes: Varianten, Auswahl mit Server-Persistenz, Custom Theme, High Contrast, Farb-Tokens

| Merkmal | Wert |
|---|---|
| Inkrement | I1 |
| Typ (DoD 15 §3.15.3) | F – Frontend-only |
| Größe | M |
| parallelisierbar | ja |
| Abhängigkeiten | WP-I1-014 |
| CE-IDs | CE-I18N-005, CE-I18N-006, CE-I18N-007, CE-I18N-008, CE-I18N-009 |

**Ziel.** Theme-System mit hell/dunkel/system, High-Contrast-Varianten, Custom Theme und Server-Persistenz; Farb-Token-System 1:1.

**Enthaltene CE-IDs**

| CE-ID | Feature | Status (15 Anh. B) | Inkrement laut 15 | Pflicht-Ebenen | Testprojekt | E2E-Spec |
|---|---|---|---|---|---|---|
| CE-I18N-005 | Theme-System und Theme-Varianten | übernommen | I1 | L2 L4 L7 L8 (G-CSS) | Frontend-only | `web/i18n/themes.spec.ts` |
| CE-I18N-006 | Theme-Auswahl und Server-Persistenz | übernommen | I1 | L2 L7 L8 | Frontend-only | `web/i18n/themes.spec.ts` |
| CE-I18N-007 | Custom Theme | übernommen | I1 | L2 L4 L7 L8 (G-CSS) | Frontend-only | `web/i18n/themes.spec.ts` |
| CE-I18N-008 | High-Contrast-Themes | übernommen | I1 | L2 L4 L7 L8 (G-CSS) | Frontend-only | `web/i18n/themes.spec.ts` |
| CE-I18N-009 | Farb-Token-System | übernommen | I1 | L2 L4 L7 L8 (G-CSS) | Frontend-only | `web/i18n/themes.spec.ts` |

**Betroffene Module/Libs in `funk.`**

- Frontend: `frontend/libs/shared/theme`
- Frontend: `frontend/libs/web/settings` (appearance)

**Referenzdokumente**

- Architektur: 08 §3.8, §5.1
- Architektur: 09 §3.9, §5.8
- Architektur: 17 ABG-031
- Analyse/Feature: `analysis/13a-designsystem-ui-tokens.md` §2.2, §3.2, §3.3, §3.4, §2.7
- Analyse/Feature: `analysis/13b-shared-packages-i18n.md` §2.2, §3.9, §2.4
- Analyse/Feature: `analysis/08-frontend-web-architektur.md` §3.9
- Analyse/Feature: `analysis/10a-frontend-workspace-projekt-navigation.md` §2.13
- Analyse/Feature: `analysis/02a-datenmodell-kern.md` §2.3
- Feature-Katalog: `features/10-ce-feature-katalog.md` (Einträge CE-I18N-005, CE-I18N-006, CE-I18N-007, CE-I18N-008, CE-I18N-009)

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- Backend: `apps/api/plane/db/models/user.py`
- Frontend: `apps/web/app/root.tsx`, `apps/admin/providers/core.tsx`, `apps/space/app/providers.tsx`, `packages/constants/src/themes.ts`, `@makeplane/propel@0.7.3/dist/styles/variables.css`, `packages/utils/src/theme-legacy.ts`, `apps/web/lib/wrappers/store-wrapper.tsx`, `apps/web/store/user/profile.store.ts`, `apps/web/components/appearance/theme-switcher.tsx`, `apps/web/components/core/theme/theme-switch.tsx`, `apps/web/components/power-k/config/preferences-commands.ts`, `apps/web/components/power-k/ui/pages/preferences/themes-menu.tsx`, `packages/types/src/users.ts`, `apps/web/components/core/theme/custom-theme-selector.tsx`, `packages/utils/src/theme/palette-generator.ts`, `packages/utils/src/theme/theme-application.ts`, `packages/utils/src/theme/theme-inversion.ts`, `packages/utils/src/theme/constants.ts`, `apps/web/components/core/theme/color-inputs.tsx`, `apps/web/components/core/theme/input-color-picker.tsx`, `apps/web/components/core/theme/import-config-button.tsx`, `apps/web/components/core/theme/download-config-button.tsx`, `apps/web/components/core/theme/theme-mode-selector.tsx`, `packages/tailwind-config/index.css`, `packages/tailwind-config/AGENTS.md`, `packages/constants/src/label.ts`, `packages/utils/src/color.ts`, `packages/utils/src/string.ts`

**Akzeptanzkriterien**

1. Galerie-Eintrag mit allen Varianten/Zuständen; DOM-Vertrag = Referenz-Galerie; Visual in allen Themes (Chromium).
2. Tastatur/Fokus (AX3/AX4) wie Original; portierte `packages/blocks`-Tests grün (falls vorhanden).
3. `ce-coverage-check --ids CE-I18N-005,CE-I18N-006,CE-I18N-007,CE-I18N-008,CE-I18N-009` grün (Mindestebenen 15 Anhang B).

**Testumfang**

- Pflicht-Ebenen (aus 15 Anhang B): L2, L4, L7, L8
- Testprojekte: `Frontend-only`
- E2E-Specs (`frontend/apps/e2e/`): `web/i18n/themes.spec.ts`

### WP-I1-019 – UI-Querschnitt 1: Seiten-Header, Breadcrumbs, Leerzustände, Modal-Hosts, Dialog-/Dropdown-Verhalten, Tab-Reihenfolge

| Merkmal | Wert |
|---|---|
| Inkrement | I1 |
| Typ (DoD 15 §3.15.3) | F – Frontend-only |
| Größe | M |
| parallelisierbar | ja |
| Abhängigkeiten | WP-I0-999, WP-I1-105, WP-I1-203 |
| CE-IDs | CE-UIX-001, CE-UIX-002, CE-UIX-003, CE-UIX-004, CE-UIX-005 |

**Ziel.** Querschnittliche UI-Bausteine, die alle folgenden Screens verwenden.

**Enthaltene CE-IDs**

| CE-ID | Feature | Status (15 Anh. B) | Inkrement laut 15 | Pflicht-Ebenen | Testprojekt | E2E-Spec |
|---|---|---|---|---|---|---|
| CE-UIX-001 | Seiten-Header und Breadcrumbs | übernommen | I1 | L2 L7 L8 | Frontend-only | `web/uix/ui-crosscutting.spec.ts` |
| CE-UIX-002 | Leerzustände und Skeletons | übernommen | I1 | L2 L7 L8 | Frontend-only | `web/uix/ui-crosscutting.spec.ts` |
| CE-UIX-003 | Globale Modal-Hosts | übernommen | I1 | L2 L7 L8 | Frontend-only | `web/uix/ui-crosscutting.spec.ts` |
| CE-UIX-004 | Dialog- und Dropdown-Verhalten | übernommen | I1 | L2 L7 L8 | Frontend-only | `web/uix/ui-crosscutting.spec.ts` |
| CE-UIX-005 | Tab-Reihenfolge in Formularen | übernommen | I1 | L2 L7 L8 | Frontend-only | `web/uix/ui-crosscutting.spec.ts` |

**Betroffene Module/Libs in `funk.`**

- Frontend: `frontend/libs/web/core/{breadcrumbs,empty-state,modals,common}`

**Referenzdokumente**

- Architektur: 08 §4.10
- Architektur: 09 §3.5
- Analyse/Feature: `analysis/10a-frontend-workspace-projekt-navigation.md` §2.4, §2.16
- Analyse/Feature: `analysis/13b-shared-packages-i18n.md` §2.5, §2.2
- Feature-Katalog: `features/10-ce-feature-katalog.md` (Einträge CE-UIX-001, CE-UIX-002, CE-UIX-003, CE-UIX-004, CE-UIX-005)

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- Frontend: `apps/web/components/core/app-header.tsx`, `apps/web/components/core/content-wrapper.tsx`, `apps/web/components/core/page-title.tsx`, `apps/web/components/common/breadcrumb-link.tsx`, `apps/web/components/breadcrumbs/project.tsx`, `apps/web/components/breadcrumbs/common.tsx`, `apps/web/components/common/extended-app-header.tsx`, `apps/web/components/empty-state/detailed-empty-state-root.tsx`, `apps/web/components/empty-state/simple-empty-state-root.tsx`, `apps/web/components/empty-state/section-empty-state-root.tsx`, `apps/web/components/ui/loader/projects-loader.tsx`, `apps/web/components/ui/loader/settings/members.tsx`, `apps/web/components/modals/workspace-level.tsx`, `apps/web/components/modals/project-level.tsx`, `apps/web/components/modals/work-item-level.tsx`, `packages/hooks/src/use-dialog-dismissal.tsx`, `packages/hooks/src/use-outside-click-detector.tsx`, `packages/constants/src/tab-indices.ts`, `packages/utils/src/tab-indices.ts`

**Akzeptanzkriterien**

1. Galerie-Eintrag mit allen Varianten/Zuständen; DOM-Vertrag = Referenz-Galerie; Visual in allen Themes (Chromium).
2. Tastatur/Fokus (AX3/AX4) wie Original; portierte `packages/blocks`-Tests grün (falls vorhanden).
3. `ce-coverage-check --ids CE-UIX-001,CE-UIX-002,CE-UIX-003,CE-UIX-004,CE-UIX-005` grün (Mindestebenen 15 Anhang B).

**Testumfang**

- Pflicht-Ebenen (aus 15 Anhang B): L2, L7, L8
- Testprojekte: `Frontend-only`
- E2E-Specs (`frontend/apps/e2e/`): `web/uix/ui-crosscutting.spec.ts`

### WP-I1-020 – UI-Querschnitt 2: LocalStorage-Präferenzen, Zwischenablage/CSV, ungespeicherte Änderungen, Fehlerseiten, Stale-Chunk, Legacy-Redirects, Link-Icons

| Merkmal | Wert |
|---|---|
| Inkrement | I1 |
| Typ (DoD 15 §3.15.3) | F – Frontend-only |
| Größe | M |
| parallelisierbar | ja |
| Abhängigkeiten | WP-I0-999 |
| CE-IDs | CE-UIX-006, CE-UIX-007, CE-UIX-008, CE-UIX-010, CE-UIX-011, CE-UIX-012, CE-UIX-013 |

**Ziel.** Weitere Querschnittsfunktionen des Web-Frontends.

**Enthaltene CE-IDs**

| CE-ID | Feature | Status (15 Anh. B) | Inkrement laut 15 | Pflicht-Ebenen | Testprojekt | E2E-Spec |
|---|---|---|---|---|---|---|
| CE-UIX-006 | Synchronisierte LocalStorage-Präferenzen und Plattformerkennung | übernommen | I1 | L2 L7 L8 | Frontend-only | `web/uix/ui-crosscutting.spec.ts` |
| CE-UIX-007 | Zwischenablage und CSV-Download | übernommen | I1 | L2 L7 L8 | Frontend-only | `web/uix/ui-crosscutting.spec.ts` |
| CE-UIX-008 | Warnung bei ungespeicherten Änderungen | übernommen | I1 | L2 L7 L8 | Frontend-only | `web/uix/ui-crosscutting.spec.ts` |
| CE-UIX-010 | 404-, Fehler- und Zugriffsseiten (Web) | übernommen | I1 | L2 L7 L8 | Frontend-only | `web/uix/ui-crosscutting.spec.ts` |
| CE-UIX-011 | Stale-Chunk-Auto-Reload | übernommen | I1 | L2 L7 L8 | Frontend-only | `web/uix/ui-crosscutting.spec.ts` |
| CE-UIX-012 | Legacy-Redirects | übernommen | I1 | L2 L7 L8 | Frontend-only | `web/uix/ui-crosscutting.spec.ts` |
| CE-UIX-013 | Link-Icons und URL-Erkennung | übernommen | I1 | L2 L7 L8 | Frontend-only | `web/uix/ui-crosscutting.spec.ts` |

**Betroffene Module/Libs in `funk.`**

- Frontend: `frontend/libs/shared/cdk`
- Frontend: `frontend/libs/web/core/{common,lib}`
- Frontend: `frontend/apps/web/src/pages/routes/redirects/`

**Referenzdokumente**

- Architektur: 08 §3.3.5, §3.14, §3.15, §4.10, §5.4
- Architektur: 08 O-D08-09
- Analyse/Feature: `analysis/13b-shared-packages-i18n.md` §2.5, §2.4
- Analyse/Feature: `analysis/08-frontend-web-architektur.md` §2.8, §2.12, §2.9, §2.2
- Analyse/Feature: `analysis/10a-frontend-workspace-projekt-navigation.md` §2.14
- Feature-Katalog: `features/10-ce-feature-katalog.md` (Einträge CE-UIX-006, CE-UIX-007, CE-UIX-008, CE-UIX-010, CE-UIX-011, CE-UIX-012, CE-UIX-013)

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- Frontend: `packages/hooks/src/use-local-storage.tsx`, `packages/hooks/src/use-platform-os.tsx`, `packages/utils/src/string.ts`, `packages/utils/src/file.ts`, `apps/web/hooks/use-reload-confirmation.tsx`, `apps/web/app/not-found.tsx`, `apps/web/app/error/dev.tsx`, `apps/web/app/error/prod.tsx`, `apps/web/components/instance/maintenance-view.tsx`, `apps/web/components/instance/not-ready-view.tsx`, `apps/web/layouts/auth-layout/workspace-wrapper.tsx`, `apps/web/components/auth-screens/not-authorized-view.tsx`, `apps/web/components/auth-screens/project/project-access-restriction.tsx`, `apps/web/lib/stale-asset-error.ts`, `apps/web/app/entry.client.tsx`, `apps/web/app/root.tsx`, `apps/web/app/routes/core.ts`, `apps/web/app/routes/redirects/core`, `packages/utils/src/get-icon-for-link.ts`, `packages/utils/src/url.ts`, `packages/utils/src/tlds.ts`

**Akzeptanzkriterien**

1. Galerie-Eintrag mit allen Varianten/Zuständen; DOM-Vertrag = Referenz-Galerie; Visual in allen Themes (Chromium).
2. Tastatur/Fokus (AX3/AX4) wie Original; portierte `packages/blocks`-Tests grün (falls vorhanden).
3. `ce-coverage-check --ids CE-UIX-006,CE-UIX-007,CE-UIX-008,CE-UIX-010,CE-UIX-011,CE-UIX-012,CE-UIX-013` grün (Mindestebenen 15 Anhang B).

**Testumfang**

- Pflicht-Ebenen (aus 15 Anhang B): L2, L7, L8
- Testprojekte: `Frontend-only`
- E2E-Specs (`frontend/apps/e2e/`): `web/uix/ui-crosscutting.spec.ts`

### WP-I1-101 – Messaging produktiv: Retry, Dead-Letter, Worker-Pools, Beat-Plan, Soft-/Hard-Delete, Retention

| Merkmal | Wert |
|---|---|
| Inkrement | I1 |
| Typ (DoD 15 §3.15.3) | B – Backend-only |
| Größe | M |
| parallelisierbar | ja |
| Abhängigkeiten | WP-I0-999, WP-I0-912 |
| CE-IDs | CE-OPS-014, CE-OPS-015, CE-OPS-016 |

**Ziel.** Job-Queue mit Retry-Policies, Dead-Letter, benannten Worker-Pools (`Funk:Worker:Queues`), Scheduler mit Leader-Lock und dem vollständigen Cron-Plan (11 übernommene Original-Einträge mit identischer UTC-Zeit, 7 neue), Soft-Delete-Kaskaden-Registry, Hard-Delete inkl. Objektspeicher-Dateien und Retention-Jobs.

**Enthaltene CE-IDs**

| CE-ID | Feature | Status (15 Anh. B) | Inkrement laut 15 | Pflicht-Ebenen | Testprojekt | E2E-Spec |
|---|---|---|---|---|---|---|
| CE-OPS-014 | Soft-Delete und endgültige Löschung | übernommen | I1 | L1 L3 | Funk.BuildingBlocks.Tests | – |
| CE-OPS-015 | Aufbewahrung und Bereinigung | übernommen | I1 | L1 L3 | Funk.Worker.Tests | – |
| CE-OPS-016 | Zeitgesteuerte Jobs (Beat-Plan) | übernommen | I1 | L3 L6 L9 (LT-12) | Funk.Worker.Tests | – |

**Betroffene Module/Libs in `funk.`**

- Backend: `src/building-blocks/Funk.BuildingBlocks.Messaging` (Retry, DLQ, Pools)
- Backend: `src/hosts/Funk.Worker`
- Backend: `src/building-blocks/Funk.BuildingBlocks.Persistence/SoftDelete/`
- Backend: `tests/Funk.Worker.Tests` (`CronRegistrationTests`)

**Referenzdokumente**

- Architektur: 06 §3.5, §3.6, §3.16, §4.2, D06-ADR-06…-08, -18
- Architektur: 03 §3.5
- Architektur: 02 §3.2
- Analyse/Feature: `analysis/07-hintergrundjobs-mail-storage-webhooks.md` §3.8, §2.14
- Analyse/Feature: `analysis/02a-datenmodell-kern.md` §3.2
- Analyse/Feature: `analysis/01-gesamtarchitektur-infrastruktur.md` §2.17
- Feature-Katalog: `features/10-ce-feature-katalog.md` (Einträge CE-OPS-014, CE-OPS-015, CE-OPS-016)

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- Backend: `apps/api/plane/bgtasks/deletion_task.py`, `apps/api/plane/db/mixins.py`, `apps/api/plane/celery.py`, `apps/api/plane/bgtasks/cleanup_task.py`, `apps/api/plane/bgtasks/exporter_expired_task.py`, `apps/api/plane/bgtasks/file_asset_task.py`, `apps/api/plane/bgtasks/issue_automation_task.py`

**Akzeptanzkriterien**

1. `CronRegistrationTests`: 11 Original-Einträge mit identischer UTC-Zeit, B3/B13 als entfallen, 7 neue Einträge (AK-D06-05).
2. Kaskaden-Registry deckt 03 §3.5.4 vollständig ab (`SoftDeleteRegistryTests`).
3. Hard-Delete löscht nach `HARD_DELETE_AFTER_DAYS` auch die Objektspeicher-Dateien (DEV-OPS-002).
4. Contract-Szenarien mit Original-Golden für alle HTTP-Endpunkte dieses Pakets; Replay grün.
5. Job-/Consumer-Tests: Idempotenz (Inbox), Retry/Backoff, Zeitsteuerung mit `FixedClock`; neue Ereignistypen im Event-Katalog-Snapshot.
6. Bei Cron-Jobs: Registrierung in `CronRegistrationTests` mit Original-Zeit (UTC).
7. `ce-coverage-check --ids CE-OPS-014,CE-OPS-015,CE-OPS-016` grün (Mindestebenen 15 Anhang B).

**Testumfang**

- Pflicht-Ebenen (aus 15 Anhang B): L1, L3, L6, L9
- Testprojekte: `Funk.BuildingBlocks.Tests`, `Funk.Worker.Tests`

### WP-I1-102 – Mail-Plattform: MailKit, Fluid-Templates, Mailpit, G-MAIL

| Merkmal | Wert |
|---|---|
| Inkrement | I1 |
| Typ (DoD 15 §3.15.3) | B – Backend-only |
| Größe | M |
| parallelisierbar | ja |
| Abhängigkeiten | WP-I0-999, WP-I1-101 |
| CE-IDs | – (keine; Baustein/Spike/Abnahme) |

**Ziel.** Versand über MailKit, Templates als 1:1-Port der Django-Templates nach Liquid (Fluid) mit `DjangoHtmlEncoder`, gebrandete Betreffzeilen und Logos (CID-Inline), Mailpit im Dev/Test, Golden-Tests G-MAIL. Templates M5, M7, M8, M9 in diesem Inkrement.

**Betroffene Module/Libs in `funk.`**

- Backend: `src/platform/Funk.Platform.Mail` (`IMailSender`, `MailTemplateRenderer`, `Templates/**.liquid`, `Assets/logo-{white,dark}.png`)
- Backend: `tests/Funk.Platform.Tests/Mail/`

**Referenzdokumente**

- Architektur: 06 §3.13, §4.9, §5.11, D06-ADR-13, -14, -24, -25
- Architektur: 15 §3.7 (G-MAIL)
- Architektur: 17 ABG-105

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- `apps/api/templates/emails/`
- `apps/api/plane/bgtasks/`(Mail-Tasks)

**Akzeptanzkriterien**

1. G-MAIL: HTML normalisiert gleich, Text-Teil byte-gleich zur gebrandeten Original-Referenz je Template; keine externen Bild-URLs (BRAND-MAIL-05).
2. Sprache der Mails nach Entscheidung OP-PLAN-05 (plan/04) – bis dahin Englisch wie Original.
3. Contract-Szenarien mit Original-Golden für alle HTTP-Endpunkte dieses Pakets; Replay grün.
4. Job-/Consumer-Tests: Idempotenz (Inbox), Retry/Backoff, Zeitsteuerung mit `FixedClock`; neue Ereignistypen im Event-Katalog-Snapshot.
5. Bei Cron-Jobs: Registrierung in `CronRegistrationTests` mit Original-Zeit (UTC).

**Testumfang**

- L1/L3 der betroffenen Module, Contract-Szenarien, Job-/Consumer-Tests.

### WP-I1-103 – Objektspeicher, Datei-Assets und Uploads mit Fortschritt (Image-Picker)

| Merkmal | Wert |
|---|---|
| Inkrement | I1 |
| Typ (DoD 15 §3.15.3) | V – Vertikaler Schnitt |
| Größe | M |
| parallelisierbar | ja |
| Abhängigkeiten | WP-I0-999, WP-I0-908, WP-I0-913 |
| CE-IDs | CE-OPS-012, CE-OPS-013, CE-UIX-009 |

**Ziel.** `IObjectStorage` (S3/Dateisystem), Upload-Policy (Presigned POST bzw. Proxy-Modus nach S8), `file_assets` mit Bestätigung, Metadaten-Job und Cleanup unbestätigter Assets, Gateway-Routen `/uploads`, Frontend Image-Picker und Upload-Fortschritt.

**Enthaltene CE-IDs**

| CE-ID | Feature | Status (15 Anh. B) | Inkrement laut 15 | Pflicht-Ebenen | Testprojekt | E2E-Spec |
|---|---|---|---|---|---|---|
| CE-OPS-012 | Objektspeicher mit Presigned Upload/Download | übernommen | I1 | L1 L3 L5 | Funk.Assets.Tests | – |
| CE-OPS-013 | Datei-Assets (FileAsset) | übernommen | I1 | L1 L2 L3 L5 L7 L8 | Funk.Assets.Tests | `web/uix/ui-crosscutting.spec.ts` |
| CE-UIX-009 | Image-Picker und Uploads mit Fortschritt | übernommen | I1 | L2 L7 L8 | Frontend-only | `web/uix/ui-crosscutting.spec.ts` |

**Betroffene Module/Libs in `funk.`**

- Backend: `src/platform/Funk.Platform.Storage`
- Backend: `src/modules/Assets/Funk.Assets`, `Funk.Assets.Contracts`
- Backend: `src/hosts/Funk.Gateway` (Upload-Routen)
- Backend: `tests/modules/Funk.Assets.Tests`
- Frontend: `frontend/libs/web/core/assets`
- Frontend: `frontend/libs/shared/blocks` (image-picker)

**Referenzdokumente**

- Architektur: 04 §4.13
- Architektur: 03 §3.4.11
- Architektur: 05 §3.17.4
- Architektur: 14 §3.7.6
- Architektur: 06 §1.3 Zeile I1
- Analyse/Feature: `analysis/01-gesamtarchitektur-infrastruktur.md` §2.19
- Analyse/Feature: `analysis/03-api-intern-workspace-projekt-user.md` §3.13, §3.17
- Analyse/Feature: `analysis/02a-datenmodell-kern.md` §3.10
- Analyse/Feature: `analysis/07-hintergrundjobs-mail-storage-webhooks.md` §3.12
- Analyse/Feature: `analysis/13b-shared-packages-i18n.md` §3.11
- Analyse/Feature: `analysis/10a-frontend-workspace-projekt-navigation.md` §2.16
- Analyse/Feature: `analysis/08-frontend-web-architektur.md` §2.7
- Feature-Katalog: `features/10-ce-feature-katalog.md` (Einträge CE-OPS-012, CE-OPS-013, CE-UIX-009)

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- Backend: `apps/api/plane/settings/storage.py`, `apps/api/plane/db/management/commands/create_bucket.py`, `apps/api/plane/app/views/asset/v2.py`, `apps/proxy/Caddyfile.ce`, `apps/api/plane/app/views/asset/base.py`, `apps/api/plane/db/models/asset.py`, `apps/api/plane/bgtasks/file_asset_task.py`, `apps/api/plane/bgtasks/storage_metadata_task.py`, `apps/api/plane/throttles/asset.py`, `apps/api/plane/app/views/external/base.py`
- Frontend: `apps/web/services/file.service.ts`, `packages/services/src/file/helper.ts`, `packages/services/src/file/sites-file.service.ts`, `packages/services/src/file/file-upload.service.ts`, `packages/constants/src/file.ts`, `packages/utils/src/editor/common.ts`, `apps/web/components/core/image-picker-popover.tsx`, `apps/web/components/core/modals/user-image-upload-modal.tsx`, `apps/web/components/core/modals/workspace-image-upload-modal.tsx`, `apps/web/helpers/cover-image.helper.ts`, `apps/web/services/file-upload.service.ts`, `apps/web/store/editor/asset.store.ts`

**Endpunkte (Katalog 04, `architecture/_data/endpoints.json`; 8 registriert)**

| EP | Methode | Pfad | Oberfläche | Handler | Permission | Inkr. 04 | CE-IDs |
|---|---|---|---|---|---|---|---|
| EP-0415 | GET | `/api/assets/v2/files/{token}/` | App | AssetDeliveryEndpoints.GetFileSystemAssetQuery | (HMAC-Download-Token) | I1 | CE-OPS-012 |
| EP-0416 | GET | `/api/assets/v2/static/{asset_id}/` | App | AssetDeliveryEndpoints.GetStaticAssetRedirectQuery | user.asset.read_static | I1 | CE-OPS-012 |
| EP-0417 | POST | `/api/assets/v2/upload/{token}/` | App | AssetDeliveryEndpoints.ProxyUploadAssetCommand | (HMAC-Upload-Token) | I1 | CE-OPS-012 |
| EP-0419 | GET | `/api/assets/v2/workspaces/{slug}/projects/{project_id}/download/{asset_id}/` | App | ProjectAssetEndpoints.GetProjectAssetDownloadQuery | project.asset.read | I2 | CE-OPS-012 |
| EP-0428 | GET | `/api/assets/v2/workspaces/{slug}/check/{asset_id}/` | App | WorkspaceAssetEndpoints.CheckAssetExistsQuery | workspace.asset.read | I1 | CE-OPS-012 |
| EP-0429 | GET | `/api/assets/v2/workspaces/{slug}/download/{asset_id}/` | App | WorkspaceAssetEndpoints.GetWorkspaceAssetDownloadQuery | workspace.asset.read | I1 | CE-OPS-012 |
| EP-0430 | POST | `/api/assets/v2/workspaces/{slug}/duplicate-assets/{asset_id}/` | App | WorkspaceAssetEndpoints.DuplicateAssetCommand | workspace.asset.create | I1 | CE-OPS-013 |
| EP-0431 | POST | `/api/assets/v2/workspaces/{slug}/restore/{asset_id}/` | App | WorkspaceAssetEndpoints.RestoreAssetCommand | workspace.asset.update | I1 | CE-OPS-013 |

**Akzeptanzkriterien**

1. `ObjectStorageContractTests` grün für Default-Backend und Dateisystem; Upload > Limit → 413/Original-Fehler; MIME-/Größenprüfung wie 05 §3.17.4.
2. Contract: je Endpunkt dieses Pakets ≥ 1 Szenario mit Golden vom Original (Erfolg, Berechtigungsfehler, Validierungsfehler); Replay grün (L5).
3. Permission-Matrix (05 Anhang B) für alle Endpunkte dieses Pakets als L3-Test grün; Tenant-Isolation geprüft.
4. Signal-Stores strukturgleich zum MobX-Original (`store-parity-check`), Vitest je Action (L2).
5. E2E-Specs dieses Pakets grün gegen Original **und** funk. (Dual-Target, Pflichtszenarien 15 §3.9.3).
6. Visual-/DOM-/a11y-Prüfpunkte der betroffenen Screens (09 §4.14, 15 §3.10.2) innerhalb der Schwellwerte 15 §3.10.3 (Chromium); i18n-Schlüssel nur aus den Original-Locales (de/en).
7. `ce-coverage-check --ids CE-OPS-012,CE-OPS-013,CE-UIX-009` grün (Mindestebenen 15 Anhang B).

**Testumfang**

- Pflicht-Ebenen (aus 15 Anhang B): L1, L2, L3, L5, L7, L8
- Testprojekte: `Funk.Assets.Tests`, `Frontend-only`
- E2E-Specs (`frontend/apps/e2e/`): `web/uix/ui-crosscutting.spec.ts`

### WP-I1-104 – Valkey: HybridCache L2, verteilte Rate-Limits, TLS

| Merkmal | Wert |
|---|---|
| Inkrement | I1 |
| Typ (DoD 15 §3.15.3) | I – Infrastruktur/Baustein |
| Größe | S |
| parallelisierbar | ja |
| Abhängigkeiten | WP-I0-999 |
| CE-IDs | CE-OPS-011 |

**Ziel.** Valkey als optionale Ressource: HybridCache-L2 mit Tag-Invalidierung, verteilte Rate-Limiter, TLS-Verbindung (`rediss://`); Einzelknoten-Profil ohne Valkey bleibt lauffähig (O-05).

**Enthaltene CE-IDs**

| CE-ID | Feature | Status (15 Anh. B) | Inkrement laut 15 | Pflicht-Ebenen | Testprojekt | E2E-Spec |
|---|---|---|---|---|---|---|
| CE-OPS-011 | Redis mit TLS | übernommen | I1 | L1 L3 | Funk.Platform.Tests | – |

**Betroffene Module/Libs in `funk.`**

- Backend: `src/platform/Funk.Platform.Caching`
- Backend: `src/building-blocks/Funk.BuildingBlocks.Web/RateLimiting/`
- Backend: `tests/Funk.Platform.Tests/Caching/`

**Referenzdokumente**

- Architektur: 02 §3.12, §3.13
- Architektur: 14 §3.1.1, §3.9
- Architektur: 01 O-05
- Analyse/Feature: `analysis/01-gesamtarchitektur-infrastruktur.md` §2.18
- Feature-Katalog: `features/10-ce-feature-katalog.md` (Einträge CE-OPS-011)

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- Backend: `apps/api/plane/settings/common.py`, `apps/api/plane/settings/redis.py`

**Akzeptanzkriterien**

1. Cache-Tests mit und ohne Valkey; TLS-Verbindung im Testprofil mit selbstsigniertem Zertifikat.
2. Unit-Tests ≥ 90 % Zeilen; Architekturtest für jede neue Regel; AppHost-Test, falls Topologie betroffen.
3. Kurzreferenz in `docs/` des Repos `funk.`.
4. `ce-coverage-check --ids CE-OPS-011` grün (Mindestebenen 15 Anhang B).

**Testumfang**

- Pflicht-Ebenen (aus 15 Anhang B): L1, L3
- Testprojekte: `Funk.Platform.Tests`

### WP-I1-105 – Designsystem-Ausbau: Status-/Prioritäts-Icons, Datei-Icons, Logo-Picker, Illustrationen, Propel-Vollbestand, Blocks

| Merkmal | Wert |
|---|---|
| Inkrement | I1 |
| Typ (DoD 15 §3.15.3) | F – Frontend-only |
| Größe | L |
| parallelisierbar | ja |
| Abhängigkeiten | WP-I0-999 |
| CE-IDs | CE-I18N-014, CE-I18N-015, CE-I18N-016, CE-I18N-018, CE-I18N-019, CE-I18N-020 |

**Ziel.** Alle 68 Propel-Komponenten und 57 Elemente, die Blocks-Composites (außer Charts), State-/Cycle-/Modul-/Prioritäts-Icons, Datei-Typ-Icons und Locked-Pill, Logo-Picker (Emoji, Lucide, Material) und die 59 Empty-State-Illustrationen inkl. theme-abhängiger Assets stehen in der Galerie DOM- und pixelgleich.

**Enthaltene CE-IDs**

| CE-ID | Feature | Status (15 Anh. B) | Inkrement laut 15 | Pflicht-Ebenen | Testprojekt | E2E-Spec |
|---|---|---|---|---|---|---|
| CE-I18N-014 | Status-, Zyklus-, Modul- und Prioritäts-Icons | übernommen | I0…I3 | L2 L4 L7 L8 (G-ICONS) | Frontend-only | `gallery/design-system.spec.ts` |
| CE-I18N-015 | Datei-Typ-Icons und Locked-Pill | übernommen | I0…I3 | L2 L4 L7 L8 (G-ICONS) | Frontend-only | `gallery/design-system.spec.ts` |
| CE-I18N-016 | Logo-Picker (Emoji, Lucide, Material) | übernommen | I0…I3 | L2 L7 L8 | Frontend-only | `gallery/design-system.spec.ts` |
| CE-I18N-018 | Empty-State-Illustrationen und theme-abhängige Assets | übernommen | I0…I3 | L2 L7 L8 | Frontend-only | `gallery/design-system.spec.ts` |
| CE-I18N-019 | Propel-Komponentenbibliothek und Varianten | übernommen | I0…I3 | L2 L4 L7 L8 (G-CSS) | Frontend-only | `gallery/design-system.spec.ts` |
| CE-I18N-020 | Blocks-Composites | übernommen | I0…I3 | L2 L7 L8 | Frontend-only | `gallery/design-system.spec.ts` |

**Betroffene Module/Libs in `funk.`**

- Frontend: `frontend/libs/shared/propel` (Vollbestand)
- Frontend: `frontend/libs/shared/blocks`
- Frontend: `frontend/libs/shared/propel/state-icons`

**Referenzdokumente**

- Architektur: 09 §4.2–§4.13, §3.7, §3.8, §3.11
- Architektur: 09 §7.3 (DoD je Baustein)
- Analyse/Feature: `analysis/13a-designsystem-ui-tokens.md` §2.27, §2.28, §2.29, §2.31, §2.22, §2.26
- Feature-Katalog: `features/10-ce-feature-katalog.md` (Einträge CE-I18N-014, CE-I18N-015, CE-I18N-016, CE-I18N-018, CE-I18N-019, CE-I18N-020)

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- Frontend: `packages/blocks/src/icons/state/state-group-icon.tsx`, `packages/blocks/src/icons/cycle`, `packages/blocks/src/icons/module`, `packages/blocks/src/icons/priority-icon.tsx`, `@makeplane/propel@0.7.3/dist/state-icons/index.js`, `apps/web/components/icons/attachment/attachment-icon.tsx`, `apps/web/components/icons/locked-component.tsx`, `packages/blocks/src/emoji-icon-picker`, `packages/blocks/src/emoji-icon-picker/lucide-icons.tsx`, `packages/blocks/src/emoji-icon-picker/material-icons.tsx`, `packages/blocks/src/emoji-icon-picker/logo.tsx`, `packages/blocks/src/empty-state/assets/asset-registry.tsx`, `packages/blocks/src/empty-state`, `apps/web/components/common/logo-spinner.tsx`, `@makeplane/propel@0.7.3/dist/components`, `@makeplane/propel@0.7.3/dist/elements`, `@makeplane/propel@0.7.3/dist/internal`, `packages/blocks/package.json`, `packages/blocks/src/select`, `packages/blocks/src/property-select`, `packages/blocks/src/breadcrumb`, `packages/blocks/src/context-menu`, `packages/blocks/src/dialog`, `packages/blocks/src/layout`, `packages/blocks/src/pill-button`, `packages/blocks/src/portal`, `packages/blocks/src/card`, `packages/blocks/src/virtual-list`

**Akzeptanzkriterien**

1. Jede Komponente aus 09 §4.2/§4.3/§4.7 hat einen Galerie-Eintrag mit allen Varianten; DOM-Vertrag = Referenz-Galerie; Visual ≤ 0,1 %.
2. Emoji-Daten offline gebündelt; `emojibase-data`-Version beim ersten `capture-reference`-Lauf festgeschrieben (Z-04).
3. Galerie-Eintrag mit allen Varianten/Zuständen; DOM-Vertrag = Referenz-Galerie; Visual in allen Themes (Chromium).
4. Tastatur/Fokus (AX3/AX4) wie Original; portierte `packages/blocks`-Tests grün (falls vorhanden).
5. `ce-coverage-check --ids CE-I18N-014,CE-I18N-015,CE-I18N-016,CE-I18N-018,CE-I18N-019,CE-I18N-020` grün (Mindestebenen 15 Anhang B).

**Testumfang**

- Pflicht-Ebenen (aus 15 Anhang B): L2, L4, L7, L8
- Testprojekte: `Frontend-only`
- E2E-Specs (`frontend/apps/e2e/`): `gallery/design-system.spec.ts`

### WP-I1-201 – Erweiterungspunkt A17: IStateCatalog/ILabelCatalog als einzige Lesewege, Catalog-Sources

| Merkmal | Wert |
|---|---|
| Inkrement | I1 |
| Typ (DoD 15 §3.15.3) | X – Erweiterungspunkt 🧱 |
| Größe | S |
| parallelisierbar | nein |
| Abhängigkeiten | WP-I0-999 |
| CE-IDs | – (keine; Erweiterungspunkt) |
| Andockstelle | 01 §1.4 A17; 16 §3.3.0 E-21; 16 §4.6 (Träger CE-PRJ-023…033) |

**Ziel.** States und Labels werden von allen Modulen ausschließlich über `IStateCatalog`/`ILabelCatalog` gelesen; Quellen `IStateCatalogSource`/`ILabelCatalogSource` (E-21, CE: Projekt-Quelle Order 100); `IScopedCatalogEntry` an `State`/`Label`.

**Betroffene Module/Libs in `funk.`**

- Backend: `src/modules/Projects/Funk.Projects.Contracts/Catalogs/`
- Backend: `src/modules/Projects/Funk.Projects/Catalogs/ProjectStateCatalogSource.cs`

**Referenzdokumente**

- Architektur: 16 §5.2, §3.3.0 E-21
- Architektur: 02 §5.2.4
- Architektur: 01 §1.4 Zeile A17

**Akzeptanzkriterien**

1. Architekturtest: kein Modul außer `Funk.Projects` greift direkt auf `states`/`labels` zu.
2. Fake-Quelle (Order 50) liefert zusätzliche Workspace-States ohne CE-Änderung (Typ X).
3. Contract (Interface/Schema/Token) + CE-Default-Implementierung; Eintrag in `tests/extension-points.yaml`.
4. Test „CE-Default = Original-Verhalten“ (Contract-Replay unverändert grün).
5. Test mit Fake-Erweiterung aus `Funk.BuildingBlocks.Testing/Extensions` bzw. `provideFakeExtensions()` beweist Erweiterbarkeit ohne CE-Änderung (DoD Typ X).

**Testumfang**

- Typ-X-Tests (CE-Default unverändert, Fake-Erweiterung wirkt ohne CE-Änderung), L0-Inventarabgleich `ExtensionPointInventoryTests`/`extension-registry-check`.

### WP-I1-202 – Erweiterungspunkt Feature-Kataloge: IProjectFeatureCatalog, IWorkspaceFeatureCatalog, Contributors, PROJECT_FEATURES

| Merkmal | Wert |
|---|---|
| Inkrement | I1 |
| Typ (DoD 15 §3.15.3) | X – Erweiterungspunkt 🧱 |
| Größe | S |
| parallelisierbar | nein |
| Abhängigkeiten | WP-I0-999 |
| CE-IDs | – (keine; Erweiterungspunkt) |
| Andockstelle | 16 §3.3.0 E-01, E-02, E-26; 16 §4.6 (Träger CE-PRJ-019, CE-PRJ-020) |

**Ziel.** Projekt- und Workspace-Feature-Toggles laufen über Kataloge (E-01, E-26) mit Tabellen `project_feature_settings`/`workspace_feature_settings` und `IProjectPayloadExtension`; Frontend-Tokens `PROJECT_FEATURES`/`WORKSPACE_FEATURES` (E-02, CE: `PROJECT_FEATURES_LIST` des Originals).

**Betroffene Module/Libs in `funk.`**

- Backend: `src/modules/Projects/Funk.Projects.Contracts/Features/`
- Backend: `src/modules/Workspaces/Funk.Workspaces.Contracts/Features/`
- Frontend: `frontend/libs/web/extensions/src/features.ts`

**Referenzdokumente**

- Architektur: 16 §3.2.6, §5.1, §3.3.0 E-01/E-02/E-26, D16-ADR-05

**Akzeptanzkriterien**

1. Die fünf CE-Toggles (`cycle_view`, `module_view`, `issue_views_view`, `page_view`, `intake_view`) verhalten sich wie das Original (Contract-Golden des Projekt-Payloads unverändert).
2. Fake-Contributor fügt einen Schalter hinzu, der in der Settings-Liste erscheint und im Payload ausgegeben wird – ohne CE-Änderung (Typ X).
3. Contract (Interface/Schema/Token) + CE-Default-Implementierung; Eintrag in `tests/extension-points.yaml`.
4. Test „CE-Default = Original-Verhalten“ (Contract-Replay unverändert grün).
5. Test mit Fake-Erweiterung aus `Funk.BuildingBlocks.Testing/Extensions` bzw. `provideFakeExtensions()` beweist Erweiterbarkeit ohne CE-Änderung (DoD Typ X).

**Testumfang**

- Typ-X-Tests (CE-Default unverändert, Fake-Erweiterung wirkt ohne CE-Änderung), L0-Inventarabgleich `ExtensionPointInventoryTests`/`extension-registry-check`.

### WP-I1-203 – Erweiterungspunkte UI-Registries I1: SETTINGS_PAGES, SIDEBAR_ITEMS (dynamisch), FAVORITE_ENTITY_RENDERERS, MEMBER_ROW_DECORATORS, ROLE_OPTIONS, GLOBAL_MODALS, ESTIMATE_SYSTEM_FLAGS

| Merkmal | Wert |
|---|---|
| Inkrement | I1 |
| Typ (DoD 15 §3.15.3) | X – Erweiterungspunkt 🧱 |
| Größe | S |
| parallelisierbar | nein |
| Abhängigkeiten | WP-I0-999 |
| CE-IDs | – (keine; Erweiterungspunkt) |
| Andockstelle | 16 §1.4 Zeile I1; 16 §4.6 (Träger CE-WS-023, CE-WS-010, CE-PRJ-019, CE-PRJ-034/-035) |

**Ziel.** Die Frontend-Registries des Inkrements I1 sind gebaut und von der CE selbst befüllt (Original-Einträge), sodass Pakete Settings-Seiten, Sidebar-Einträge, Favoriten-Typen, Mitgliederzeilen-Dekoratoren, Rollenoptionen, globale Modals und Estimate-Systeme additiv ergänzen.

**Betroffene Module/Libs in `funk.`**

- Frontend: `frontend/libs/web/extensions/src/{settings,sidebar,favorites,members,roles,modals,estimates}.ts`

**Referenzdokumente**

- Architektur: 08 §6.1, §6.4, §6.5
- Architektur: 16 §3.3.0 E-14 (I1-Teil), §1.4 Zeile I1
- Architektur: 17 ABG-030

**Akzeptanzkriterien**

1. `extension-registry-check` meldet für jede Registry CE-Einträge und einen Fake-Eintrag-Test (Typ X).
2. Contract (Interface/Schema/Token) + CE-Default-Implementierung; Eintrag in `tests/extension-points.yaml`.
3. Test „CE-Default = Original-Verhalten“ (Contract-Replay unverändert grün).
4. Test mit Fake-Erweiterung aus `Funk.BuildingBlocks.Testing/Extensions` bzw. `provideFakeExtensions()` beweist Erweiterbarkeit ohne CE-Änderung (DoD Typ X).

**Testumfang**

- Typ-X-Tests (CE-Default unverändert, Fake-Erweiterung wirkt ohne CE-Änderung), L0-Inventarabgleich `ExtensionPointInventoryTests`/`extension-registry-check`.

### WP-I1-204 – Erweiterungspunkt Activity-Grundgerüst: IActivityRecorder, IActivityFieldResolver-Registry, reservierte Felder

| Merkmal | Wert |
|---|---|
| Inkrement | I1 |
| Typ (DoD 15 §3.15.3) | X – Erweiterungspunkt 🧱 |
| Größe | S |
| parallelisierbar | nein |
| Abhängigkeiten | WP-I0-999, WP-I0-201 |
| CE-IDs | – (keine; Erweiterungspunkt) |
| Andockstelle | 16 §1.4 Zeile I1; 16 §4.6 (Träger CE-WI-039/-040, Gerüst ab I1) |

**Ziel.** Activity-Pipeline-Gerüst (synchron in derselben Transaktion, Event `funk.work_item_activity.recorded.v1`), Registry `IActivityFieldResolver`, reservierte Activity-Feldnamen (16 §3.2.3); Referenzbeitrag `LabelActivityFieldResolver`.

**Betroffene Module/Libs in `funk.`**

- Backend: `src/modules/WorkItems/Funk.WorkItems.Contracts/Services/IActivityRecorder.cs`
- Backend: `src/modules/Projects/Funk.Projects/Activity/LabelActivityFieldResolver.cs`

**Referenzdokumente**

- Architektur: 06 §3.9, §5.6, D06-ADR-09
- Architektur: 02 §3.19, §5.2.10, D02-ADR-25
- Architektur: 16 §3.2.3

**Akzeptanzkriterien**

1. Fake-Field-Resolver liefert Anzeigewerte für ein Paketfeld ohne CE-Änderung (Typ X); reservierte Feldnamen kollidieren nicht (Kollisionstest).
2. Contract (Interface/Schema/Token) + CE-Default-Implementierung; Eintrag in `tests/extension-points.yaml`.
3. Test „CE-Default = Original-Verhalten“ (Contract-Replay unverändert grün).
4. Test mit Fake-Erweiterung aus `Funk.BuildingBlocks.Testing/Extensions` bzw. `provideFakeExtensions()` beweist Erweiterbarkeit ohne CE-Änderung (DoD Typ X).

**Testumfang**

- Typ-X-Tests (CE-Default unverändert, Fake-Erweiterung wirkt ohne CE-Änderung), L0-Inventarabgleich `ExtensionPointInventoryTests`/`extension-registry-check`.

### WP-I1-205 – Erweiterungspunkte IInstanceConfigKeyProvider und B1-Schema-Vorhalte (teamspace_id)

| Merkmal | Wert |
|---|---|
| Inkrement | I1 |
| Typ (DoD 15 §3.15.3) | X – Erweiterungspunkt 🧱 |
| Größe | S |
| parallelisierbar | ja |
| Abhängigkeiten | WP-I0-999 |
| CE-IDs | – (keine; Erweiterungspunkt) |
| Andockstelle | 16 §3.3.0 E-12; 01 §1.4 B1 (I1-Teil); 16 §4.6 (Träger CE-INST-002) |

**Ziel.** Zusätzliche Instanz-Konfigurationsschlüssel über `IInstanceConfigKeyProvider` (E-12, ersetzt `instance_config_variables/extended.py`); nullable Spalten `teamspace_id` in den in 16 §3.3 B1 genannten Tabellen (Views, Pages, Kommentare) per Migration.

**Betroffene Module/Libs in `funk.`**

- Backend: `src/modules/Instance/Funk.Instance.Contracts/IInstanceConfigKeyProvider.cs`
- Backend: `src/data/Funk.Data/Migrations/…_Teamspaces_ScopeColumns`

**Referenzdokumente**

- Architektur: 16 §3.3.0 E-12, §3.3.2 (B1), §5.4
- Architektur: 02 §4.10
- Architektur: 01 §1.4 Zeile B1 (ABG-058)

**Akzeptanzkriterien**

1. Fake-Key-Provider ergänzt einen Instanz-Key, der in `GET /api/instances/` (Admin) erscheint – ohne CE-Änderung (Typ X).
2. Spalten `teamspace_id` existieren nullable, werden in CE-Verträgen nicht ausgegeben (Contract-Goldens unverändert).
3. Contract (Interface/Schema/Token) + CE-Default-Implementierung; Eintrag in `tests/extension-points.yaml`.
4. Test „CE-Default = Original-Verhalten“ (Contract-Replay unverändert grün).
5. Test mit Fake-Erweiterung aus `Funk.BuildingBlocks.Testing/Extensions` bzw. `provideFakeExtensions()` beweist Erweiterbarkeit ohne CE-Änderung (DoD Typ X).

**Testumfang**

- Typ-X-Tests (CE-Default unverändert, Fake-Erweiterung wirkt ohne CE-Änderung), L0-Inventarabgleich `ExtensionPointInventoryTests`/`extension-registry-check`.

### WP-I1-999 – Abnahme I1 – Workspace, Projekte, Konto (G5)

| Merkmal | Wert |
|---|---|
| Inkrement | I1 |
| Typ (DoD 15 §3.15.3) | A – Inkrement-Abnahme |
| Größe | S |
| parallelisierbar | nein |
| Abhängigkeiten | WP-I1-001, WP-I1-002, WP-I1-003, WP-I1-004, WP-I1-005, WP-I1-006, WP-I1-007, WP-I1-008, WP-I1-009, WP-I1-010, WP-I1-011, WP-I1-012, WP-I1-013, WP-I1-014, WP-I1-015, WP-I1-016, WP-I1-017, WP-I1-018, WP-I1-019, WP-I1-020, WP-I1-101, WP-I1-102, WP-I1-103, WP-I1-104, WP-I1-105, WP-I1-201, WP-I1-202, WP-I1-203, WP-I1-204, WP-I1-205 |
| CE-IDs | – (keine; Baustein/Spike/Abnahme) |

**Ziel.** Inkrement-Abnahme I1 nach G5 und Meilenstein M1 (plan/01-roadmap-ce.md §4).

**Referenzdokumente**

- Architektur: plan/01-roadmap-ce.md §4 (M1)
- Architektur: 15 §3.16 Zeile I1

**Akzeptanzkriterien**

1. Alle Abnahmekriterien M1 erfüllt; `docs/acceptance/I1.md` generiert.
2. G5 `--inc <In> --strict` grün: `ce-coverage-check`, `original-test-ledger`, Parity-Report (0 ungenehmigte Abweichungen, Endpunkt-Abdeckung des Inkrements 100 %), Visual/a11y, Lastziele, Security-Report.
3. Demo-Video der Kern-Flows (`--video on`) und Abnahmebericht `docs/acceptance/<In>.md`; fachliche Abnahme durch den Auftraggeber.

**Testumfang**

- G5 `--inc I1`.

## 4.3 Inkrement I2

### WP-I2-001 – Work Item anlegen und bearbeiten (Modal, fortlaufende ID, Autosave, Toasts, Drafts-Rückfrage, Bestehende hinzufügen)

| Merkmal | Wert |
|---|---|
| Inkrement | I2 |
| Typ (DoD 15 §3.15.3) | V – Vertikaler Schnitt |
| Größe | L |
| parallelisierbar | nein |
| Abhängigkeiten | WP-I1-999, WP-I2-202, WP-I2-204, WP-I2-205, WP-I2-206, WP-I2-022 |
| CE-IDs | CE-WI-001, CE-WI-002, CE-WI-003, CE-WI-004, CE-WI-005, CE-WI-006, CE-WI-007, CE-WI-008 |

**Ziel.** Work-Item-Modal (Anlage/Bearbeitung), nebenläufigkeitssichere `sequence_id` je Projekt (`SequenceAllocator`), Titel- und Beschreibungs-Autosave, Toast-Aktionen, Draft-Rückfrage und Dialog „Bestehende Work Items hinzufügen“; Issue-Store-Grundgerüst (IssueRootStore) 1:1.

**Enthaltene CE-IDs**

| CE-ID | Feature | Status (15 Anh. B) | Inkrement laut 15 | Pflicht-Ebenen | Testprojekt | E2E-Spec |
|---|---|---|---|---|---|---|
| CE-WI-001 | Work Item anlegen (Modal) | übernommen | I2 | L1 L2 L3 L5 L7 L8 | Funk.WorkItems.Tests | `web/work-items/create-edit.spec.ts` |
| CE-WI-002 | Fortlaufende Work-Item-ID (PROJ-123) | übernommen | I2 | L1 L2 L3 L5 L7 L8 | Funk.WorkItems.Tests | `web/work-items/create-edit.spec.ts` |
| CE-WI-003 | Work Item bearbeiten | übernommen | I2 | L1 L2 L3 L5 L7 L8 L9 (LT-07) | Funk.WorkItems.Tests | `web/work-items/create-edit.spec.ts` |
| CE-WI-004 | Titel-Bearbeitung mit Autosave | übernommen | I2 | L1 L2 L3 L5 L7 L8 | Funk.WorkItems.Tests | `web/work-items/create-edit.spec.ts` |
| CE-WI-005 | Beschreibungsfeld mit Autosave | übernommen | I2 | L1 L2 L3 L4 L5 L7 L8 (G-DOC/G-SANITIZE) | Funk.WorkItems.Tests | `web/work-items/create-edit.spec.ts` |
| CE-WI-006 | Toast-Aktionen nach dem Erstellen | übernommen | I2 | L1 L2 L3 L5 L7 L8 | Funk.WorkItems.Tests | `web/work-items/create-edit.spec.ts` |
| CE-WI-007 | Draft-Rückfrage beim Schließen | übernommen | I2 | L1 L2 L3 L5 L7 L8 | Funk.WorkItems.Tests | `web/work-items/create-edit.spec.ts` |
| CE-WI-008 | Bestehende Work Items hinzufügen (Dialog) | übernommen | I2 | L1 L2 L3 L5 L7 L8 | Funk.WorkItems.Tests | `web/work-items/create-edit.spec.ts` |

**Betroffene Module/Libs in `funk.`**

- Backend: `src/modules/WorkItems/Funk.WorkItems`, `Funk.WorkItems.Contracts`
- Backend: `src/data/Funk.Data/Entities/WorkItems/`, `Sequences/PostgresSequenceAllocator.cs`
- Backend: `tests/modules/Funk.WorkItems.Tests`
- Frontend: `frontend/libs/web/work-items` (issue-modal, store/issue)

**Referenzdokumente**

- Architektur: 04 §4.5
- Architektur: 03 §3.4.5, §3.6, §5.4, §5.5
- Architektur: 08 §3.4.6, §5.10
- Architektur: 06 §3.9
- Analyse/Feature: `analysis/09-frontend-arbeitsobjekte-layouts.md` §2.16, §2.13, §3.10, §2.7, §3.11
- Analyse/Feature: `analysis/04-api-intern-arbeitsobjekte.md` §3.4
- Analyse/Feature: `analysis/02b-datenmodell-arbeitsobjekte.md` §3.2, §3.7
- Analyse/Feature: `analysis/13b-shared-packages-i18n.md` §2.2
- Analyse/Feature: `analysis/10b-frontend-cycles-modules-pages-views-weitere.md` §2.17
- Analyse/Feature: `analysis/10a-frontend-workspace-projekt-navigation.md` §2.16
- Feature-Katalog: `features/10-ce-feature-katalog.md` (Einträge CE-WI-001, CE-WI-002, CE-WI-003, CE-WI-004, CE-WI-005, CE-WI-006, CE-WI-007, CE-WI-008)

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- Backend: `apps/api/plane/app/views/issue/base.py`, `apps/api/plane/app/serializers/issue.py`, `apps/api/plane/db/models/issue.py`, `apps/api/plane/db/models/issue.py:104-255`, `apps/api/plane/db/models/issue.py:345-368`, `apps/api/plane/db/models/issue.py:543-554`, `apps/api/plane/db/models/issue.py:180-214`, `apps/api/plane/db/models/issue.py:557-571`, `apps/api/plane/app/serializers/project.py:132-135`, `apps/api/plane/db/management/commands/fix_duplicate_sequences.py`, `apps/api/plane/utils/serializers.py`, `apps/api/plane/bgtasks/issue_description_version_task.py`, `apps/api/plane/db/models/issue.py:240-255`
- Frontend: `apps/web/components/issues/issue-modal/modal.tsx`, `apps/web/components/issues/issue-modal/base.tsx`, `apps/web/components/issues/issue-modal/form.tsx`, `apps/web/components/issues/issue-modal/components/project-select.tsx`, `apps/web/components/issues/issue-modal/components/title-input.tsx`, `apps/web/components/issues/issue-modal/components/description-editor.tsx`, `apps/web/components/issues/issue-modal/components/default-properties.tsx`, `apps/web/components/issues/issue-modal/components/parent-tag.tsx`, `packages/constants/src/tab-indices.ts`, `packages/utils/src/tab-indices.ts`, `apps/web/components/issues/issue-detail/sidebar.tsx`, `apps/web/components/issues/issue-detail/cycle-select.tsx`, `apps/web/components/issues/issue-detail/module-select.tsx`, `apps/web/components/issues/issue-detail/label/root.tsx`, `apps/web/components/issues/title-input.tsx`, `apps/web/components/issues/issue-update-status.tsx`, `apps/web/components/editor/rich-text/description-input/root.tsx`, `apps/web/components/editor/rich-text/description-input/loader.tsx`, `apps/web/components/editor/rich-text/editor.tsx`, `apps/web/components/issues/create-issue-toast-action-items.tsx`, `apps/web/components/issues/issue-modal/draft-issue-layout.tsx`, `apps/web/components/issues/confirm-issue-discard.tsx`, `apps/web/components/core/modals/existing-issues-list-modal.tsx`, `apps/web/components/core/modals/issue-search-modal-empty-state.tsx`

**Endpunkte (Katalog 04, `architecture/_data/endpoints.json`; 3 registriert)**

| EP | Methode | Pfad | Oberfläche | Handler | Permission | Inkr. 04 | CE-IDs |
|---|---|---|---|---|---|---|---|
| EP-0261 | POST | `/api/workspaces/{slug}/projects/{project_id}/issues/` | App | WorkItemEndpoints.CreateWorkItemCommand | project.work_item.create | I2 | CE-WI-001, CE-WI-002 |
| EP-0267 | PATCH | `/api/workspaces/{slug}/projects/{project_id}/issues/{pk}/` | App | WorkItemEndpoints.UpdateWorkItemCommand | project.work_item.update | I2 | CE-WI-003, CE-WI-004, CE-WI-005, CE-WI-020 |
| EP-0272 | GET | `/api/workspaces/{slug}/projects/{project_id}/search-issues/` | App | WorkItemEndpoints.SearchWorkItemsForPickerQuery | project.work_item.search | I2 | CE-SRCH-003, CE-WI-008 |

**Akzeptanzkriterien**

1. Concurrency-Test: 100 parallele Anlagen erzeugen lückenlose, eindeutige `sequence_id` (01 §7.6).
2. Store-Paritätsprüfung (`store-parity-check`) für IssueRootStore-Teile dieses Schnitts grün.
3. Contract: je Endpunkt dieses Pakets ≥ 1 Szenario mit Golden vom Original (Erfolg, Berechtigungsfehler, Validierungsfehler); Replay grün (L5).
4. Permission-Matrix (05 Anhang B) für alle Endpunkte dieses Pakets als L3-Test grün; Tenant-Isolation geprüft.
5. Signal-Stores strukturgleich zum MobX-Original (`store-parity-check`), Vitest je Action (L2).
6. E2E-Specs dieses Pakets grün gegen Original **und** funk. (Dual-Target, Pflichtszenarien 15 §3.9.3).
7. Visual-/DOM-/a11y-Prüfpunkte der betroffenen Screens (09 §4.14, 15 §3.10.2) innerhalb der Schwellwerte 15 §3.10.3 (Chromium); i18n-Schlüssel nur aus den Original-Locales (de/en).
8. `ce-coverage-check --ids CE-WI-001,CE-WI-002,CE-WI-003,CE-WI-004,CE-WI-005,CE-WI-006,CE-WI-007,CE-WI-008` grün (Mindestebenen 15 Anhang B).

**Testumfang**

- Pflicht-Ebenen (aus 15 Anhang B): L1, L2, L3, L4, L5, L7, L8, L9
- Testprojekte: `Funk.WorkItems.Tests`
- E2E-Specs (`frontend/apps/e2e/`): `web/work-items/create-edit.spec.ts`

### WP-I2-002 – Work-Item-Detailseite (Identifier, Detaildaten, Meta, Delta-Sync, Kopfaktionen)

| Merkmal | Wert |
|---|---|
| Inkrement | I2 |
| Typ (DoD 15 §3.15.3) | V – Vertikaler Schnitt |
| Größe | M |
| parallelisierbar | nein |
| Abhängigkeiten | WP-I2-001, WP-I2-205 |
| CE-IDs | CE-WI-009, CE-WI-010, CE-WI-011, CE-WI-012, CE-WI-013, CE-WI-014 |

**Ziel.** Detailseite per Identifier (`browse/:workItem`), Detaildaten, Meta und Mehrfachabruf, Delta-Sync für den Client-Cache (`GlobalPaginator`), Identifier mit Klick-zum-Kopieren, Kopfaktionen.

**Enthaltene CE-IDs**

| CE-ID | Feature | Status (15 Anh. B) | Inkrement laut 15 | Pflicht-Ebenen | Testprojekt | E2E-Spec |
|---|---|---|---|---|---|---|
| CE-WI-009 | Work-Item-Detailseite per Identifier | übernommen | I2 | L1 L2 L3 L5 L7 L8 L9 (LT-06) | Funk.WorkItems.Tests | `web/work-items/detail.spec.ts` |
| CE-WI-010 | Work-Item-Detaildaten | übernommen | I2 | L1 L2 L3 L5 L7 L8 | Funk.WorkItems.Tests | `web/work-items/detail.spec.ts` |
| CE-WI-011 | Work-Item-Meta und Mehrfachabruf | übernommen | I2 | L1 L2 L3 L5 L7 L8 | Funk.WorkItems.Tests | `web/work-items/detail.spec.ts` |
| CE-WI-012 | Delta-Sync für den Client-Cache | übernommen | I2 | L1 L2 L3 L5 L7 L8 L9 (LT-05) | Funk.WorkItems.Tests | `web/work-items/detail.spec.ts` |
| CE-WI-013 | Identifier mit Klick-zum-Kopieren | übernommen | I2 | L1 L2 L3 L5 L7 L8 | Funk.WorkItems.Tests | `web/work-items/detail.spec.ts` |
| CE-WI-014 | Detail-Kopfaktionen | übernommen | I2 | L1 L2 L3 L5 L7 L8 | Funk.WorkItems.Tests | `web/work-items/detail.spec.ts` |

**Betroffene Module/Libs in `funk.`**

- Backend: `src/modules/WorkItems/Funk.WorkItems`
- Frontend: `frontend/libs/web/work-items` (issue-detail)

**Referenzdokumente**

- Architektur: 04 §4.5
- Architektur: 02 §3.10.4
- Architektur: 08 §4.1
- Analyse/Feature: `analysis/09-frontend-arbeitsobjekte-layouts.md` §2.13
- Analyse/Feature: `analysis/08-frontend-web-architektur.md` §3.6
- Analyse/Feature: `analysis/10a-frontend-workspace-projekt-navigation.md` §2.17
- Analyse/Feature: `analysis/04-api-intern-arbeitsobjekte.md` §2.2, §2.8
- Feature-Katalog: `features/10-ce-feature-katalog.md` (Einträge CE-WI-009, CE-WI-010, CE-WI-011, CE-WI-012, CE-WI-013, CE-WI-014)

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- Backend: `apps/api/plane/app/views/issue/base.py`, `apps/api/plane/app/urls/issue.py`, `apps/api/plane/app/serializers/base.py`, `apps/api/plane/app/serializers/issue.py`, `apps/api/plane/utils/global_paginator.py`
- Frontend: `apps/web/components/issues/issue-detail/root.tsx`, `apps/web/components/issues/issue-detail/main-content.tsx`, `apps/web/components/issues/issue-detail/sidebar.tsx`, `apps/web/app/(all)/[workspaceSlug]/(projects)/browse/[workItem]/page.tsx`, `apps/web/app/(all)/[workspaceSlug]/(projects)/projects/(detail)/[projectId]/issues/(detail)/[issueId]/page.tsx`, `apps/web/store/issue/issue-details/issue.store.ts`, `apps/web/components/browse/workItem-detail.tsx`, `apps/web/components/issues/issue-detail/issue-identifier.tsx`, `apps/web/components/issues/issue-detail/identifier-text.tsx`, `apps/web/components/issues/issue-type-switcher.tsx`, `apps/web/components/issues/issue-detail/issue-detail-quick-actions.tsx`, `apps/web/components/issues/issue-detail/subscription.tsx`

**Endpunkte (Katalog 04, `architecture/_data/endpoints.json`; 6 registriert)**

| EP | Methode | Pfad | Oberfläche | Handler | Permission | Inkr. 04 | CE-IDs |
|---|---|---|---|---|---|---|---|
| EP-0257 | GET | `/api/workspaces/{slug}/projects/{project_id}/deleted-issues/` | App | WorkItemEndpoints.ListDeletedWorkItemIdsQuery | project.work_item.read | I2 | CE-WI-012 |
| EP-0262 | GET | `/api/workspaces/{slug}/projects/{project_id}/issues/list/` | App | WorkItemEndpoints.ListWorkItemsByIdsQuery | project.work_item.read | I2 | CE-WI-011 |
| EP-0263 | GET | `/api/workspaces/{slug}/projects/{project_id}/issues/{issue_id}/meta/` | App | WorkItemEndpoints.GetWorkItemMetaQuery | project.work_item.read | I2 | CE-WI-011 |
| EP-0266 | GET | `/api/workspaces/{slug}/projects/{project_id}/issues/{pk}/` | App | WorkItemEndpoints.GetWorkItemQuery | project.work_item.read | I2 | CE-WI-010, CE-WI-015 |
| EP-0273 | GET | `/api/workspaces/{slug}/projects/{project_id}/v2/issues/` | App | WorkItemEndpoints.SyncWorkItemsQuery | project.work_item.read | I2 | CE-WI-012 |
| EP-0274 | GET | `/api/workspaces/{slug}/work-items/{project_identifier}-{issue_identifier}/` | App | WorkItemEndpoints.GetWorkItemByIdentifierQuery | project.work_item.read | I2 | CE-WI-009 |

**Akzeptanzkriterien**

1. Contract: je Endpunkt dieses Pakets ≥ 1 Szenario mit Golden vom Original (Erfolg, Berechtigungsfehler, Validierungsfehler); Replay grün (L5).
2. Permission-Matrix (05 Anhang B) für alle Endpunkte dieses Pakets als L3-Test grün; Tenant-Isolation geprüft.
3. Signal-Stores strukturgleich zum MobX-Original (`store-parity-check`), Vitest je Action (L2).
4. E2E-Specs dieses Pakets grün gegen Original **und** funk. (Dual-Target, Pflichtszenarien 15 §3.9.3).
5. Visual-/DOM-/a11y-Prüfpunkte der betroffenen Screens (09 §4.14, 15 §3.10.2) innerhalb der Schwellwerte 15 §3.10.3 (Chromium); i18n-Schlüssel nur aus den Original-Locales (de/en).
6. `ce-coverage-check --ids CE-WI-009,CE-WI-010,CE-WI-011,CE-WI-012,CE-WI-013,CE-WI-014` grün (Mindestebenen 15 Anhang B).

**Testumfang**

- Pflicht-Ebenen (aus 15 Anhang B): L1, L2, L3, L5, L7, L8, L9
- Testprojekte: `Funk.WorkItems.Tests`
- E2E-Specs (`frontend/apps/e2e/`): `web/work-items/detail.spec.ts`

### WP-I2-003 – Peek-Overview und Hover-Vorschau

| Merkmal | Wert |
|---|---|
| Inkrement | I2 |
| Typ (DoD 15 §3.15.3) | V – Vertikaler Schnitt |
| Größe | M |
| parallelisierbar | ja |
| Abhängigkeiten | WP-I2-002 |
| CE-IDs | CE-WI-015, CE-WI-016, CE-WI-017, CE-WI-018, CE-WI-019 |

**Ziel.** Peek mit drei Modi (Side, Modal, Full), Inhalt, Schließen per Outside-Click/Escape, Fehler-/Ladezustand, Hover-Vorschaukarte.

**Enthaltene CE-IDs**

| CE-ID | Feature | Status (15 Anh. B) | Inkrement laut 15 | Pflicht-Ebenen | Testprojekt | E2E-Spec |
|---|---|---|---|---|---|---|
| CE-WI-015 | Peek-Overview mit drei Modi | übernommen | I2 | L1 L2 L3 L5 L7 L8 | Funk.WorkItems.Tests | `web/work-items/peek.spec.ts` |
| CE-WI-016 | Peek-Inhalt | übernommen | I2 | L1 L2 L3 L5 L7 L8 | Funk.WorkItems.Tests | `web/work-items/peek.spec.ts` |
| CE-WI-017 | Peek schließen per Outside-Click/Escape | übernommen | I2 | L1 L2 L3 L5 L7 L8 | Funk.WorkItems.Tests | `web/work-items/peek.spec.ts` |
| CE-WI-018 | Peek-Fehler- und Ladezustand | übernommen | I2 | L1 L2 L3 L5 L7 L8 | Funk.WorkItems.Tests | `web/work-items/peek.spec.ts` |
| CE-WI-019 | Hover-Vorschaukarte | übernommen | I2 | L1 L2 L3 L5 L7 L8 | Funk.WorkItems.Tests | `web/work-items/peek.spec.ts` |

**Betroffene Module/Libs in `funk.`**

- Frontend: `frontend/libs/web/work-items` (peek-overview)

**Referenzdokumente**

- Architektur: 08 §3.9, §4.1
- Architektur: 09 §4.14
- Analyse/Feature: `analysis/09-frontend-arbeitsobjekte-layouts.md` §2.12, §2.18
- Feature-Katalog: `features/10-ce-feature-katalog.md` (Einträge CE-WI-015, CE-WI-016, CE-WI-017, CE-WI-018, CE-WI-019)

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- Frontend: `apps/web/components/issues/peek-overview/root.tsx`, `apps/web/components/issues/peek-overview/view.tsx`, `apps/web/components/issues/peek-overview/header.tsx`, `apps/web/components/issues/peek-overview/peek-overviews.tsx`, `apps/web/components/issues/peek-overview/issue-detail.tsx`, `apps/web/components/issues/peek-overview/properties.tsx`, `apps/web/hooks/use-peek-overview-outside-click.tsx`, `apps/web/hooks/use-issue-peek-overview-redirection.tsx`, `apps/web/components/issues/peek-overview/error.tsx`, `apps/web/components/issues/peek-overview/loader.tsx`, `apps/web/components/issues/preview-card/root.tsx`, `apps/web/components/issues/preview-card/date.tsx`

**Akzeptanzkriterien**

1. Contract: je Endpunkt dieses Pakets ≥ 1 Szenario mit Golden vom Original (Erfolg, Berechtigungsfehler, Validierungsfehler); Replay grün (L5).
2. Permission-Matrix (05 Anhang B) für alle Endpunkte dieses Pakets als L3-Test grün; Tenant-Isolation geprüft.
3. Signal-Stores strukturgleich zum MobX-Original (`store-parity-check`), Vitest je Action (L2).
4. E2E-Specs dieses Pakets grün gegen Original **und** funk. (Dual-Target, Pflichtszenarien 15 §3.9.3).
5. Visual-/DOM-/a11y-Prüfpunkte der betroffenen Screens (09 §4.14, 15 §3.10.2) innerhalb der Schwellwerte 15 §3.10.3 (Chromium); i18n-Schlüssel nur aus den Original-Locales (de/en).
6. `ce-coverage-check --ids CE-WI-015,CE-WI-016,CE-WI-017,CE-WI-018,CE-WI-019` grün (Mindestebenen 15 Anhang B).

**Testumfang**

- Pflicht-Ebenen (aus 15 Anhang B): L1, L2, L3, L5, L7, L8
- Testprojekte: `Funk.WorkItems.Tests`
- E2E-Specs (`frontend/apps/e2e/`): `web/work-items/peek.spec.ts`

### WP-I2-004 – Sidebar-Properties und Dropdowns (State, Priority, Assignees, Labels, Estimate, Projekt, Datum, Read-only-Labels)

| Merkmal | Wert |
|---|---|
| Inkrement | I2 |
| Typ (DoD 15 §3.15.3) | V – Vertikaler Schnitt |
| Größe | L |
| parallelisierbar | ja |
| Abhängigkeiten | WP-I2-001 |
| CE-IDs | CE-WI-020, CE-WI-021, CE-WI-022, CE-WI-023, CE-WI-024, CE-WI-027, CE-WI-028, CE-WI-029, CE-WI-030 |

**Ziel.** Property-Sidebar und alle Dropdowns außer Cycle/Modul (diese folgen mit I3); State-Wechsel über die State-Change-Pipeline; Date-Picker (Propel `Calendar`).

> **Hinweis:** CE-WI-025 (Cycle-Dropdown) und CE-WI-026 (Module-Dropdown) liegen in WP-I3-007 bzw. WP-I3-010, weil Cycles/Module erst in I3 existieren (Abweichung von 15 Anhang B, plan/04 OP-PLAN-03).

**Enthaltene CE-IDs**

| CE-ID | Feature | Status (15 Anh. B) | Inkrement laut 15 | Pflicht-Ebenen | Testprojekt | E2E-Spec |
|---|---|---|---|---|---|---|
| CE-WI-020 | Sidebar-Properties | übernommen | I2 | L1 L2 L3 L5 L7 L8 | Funk.WorkItems.Tests | `web/work-items/properties.spec.ts` |
| CE-WI-021 | State-Dropdown | übernommen | I2 | L1 L2 L3 L5 L7 L8 | Funk.WorkItems.Tests | `web/work-items/properties.spec.ts` |
| CE-WI-022 | Prioritäten und Priority-Dropdown | übernommen | I2 | L1 L2 L3 L5 L7 L8 | Funk.WorkItems.Tests | `web/work-items/properties.spec.ts` |
| CE-WI-023 | Member-Dropdown (Assignees) | übernommen | I2 | L1 L2 L3 L5 L7 L8 | Funk.WorkItems.Tests | `web/work-items/properties.spec.ts` |
| CE-WI-024 | Label-Dropdown mit Anlage | übernommen | I2 | L1 L2 L3 L5 L7 L8 | Funk.WorkItems.Tests | `web/work-items/properties.spec.ts` |
| CE-WI-027 | Estimate-Dropdown | übernommen | I2 | L1 L2 L3 L5 L7 L8 | Funk.WorkItems.Tests | `web/work-items/properties.spec.ts` |
| CE-WI-028 | Projekt-Dropdown | übernommen | I2 | L1 L2 L3 L5 L7 L8 | Funk.WorkItems.Tests | `web/work-items/properties.spec.ts` |
| CE-WI-029 | Datums- und Datumsbereichsauswahl | übernommen | I2 | L1 L2 L3 L5 L7 L8 | Funk.WorkItems.Tests | `web/work-items/properties.spec.ts` |
| CE-WI-030 | Read-only-Label-Anzeige | übernommen | I2 | L1 L2 L3 L5 L7 L8 | Funk.WorkItems.Tests | `web/work-items/properties.spec.ts` |

**Betroffene Module/Libs in `funk.`**

- Backend: `src/modules/WorkItems/Funk.WorkItems`
- Frontend: `frontend/libs/web/work-items` (dropdowns)

**Referenzdokumente**

- Architektur: 04 §4.5
- Architektur: 08 §1.3 (Date-Picker I2)
- Architektur: 16 §5.9
- Analyse/Feature: `analysis/09-frontend-arbeitsobjekte-layouts.md` §2.13, §2.19, §2.18
- Analyse/Feature: `analysis/13b-shared-packages-i18n.md` §2.2
- Analyse/Feature: `analysis/02b-datenmodell-arbeitsobjekte.md` §3.2
- Analyse/Feature: `analysis/04-api-intern-arbeitsobjekte.md` §2.3
- Feature-Katalog: `features/10-ce-feature-katalog.md` (Einträge CE-WI-020, CE-WI-021, CE-WI-022, CE-WI-023, CE-WI-024, CE-WI-027, CE-WI-028, CE-WI-029, CE-WI-030)

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- Backend: `apps/api/plane/db/models/issue.py:104-255`, `apps/api/plane/db/models/issue.py:345-368`, `apps/api/plane/db/models/issue.py:543-554`, `apps/api/plane/app/views/issue/label.py`, `apps/api/plane/app/serializers/issue.py`, `apps/api/plane/db/models/label.py`
- Frontend: `apps/web/components/issues/issue-detail/sidebar.tsx`, `apps/web/components/issues/issue-detail/cycle-select.tsx`, `apps/web/components/issues/issue-detail/module-select.tsx`, `apps/web/components/issues/issue-detail/label/root.tsx`, `apps/web/components/dropdowns/state/state-select.tsx`, `packages/blocks/src/property-select/state-select.tsx`, `apps/web/components/dropdowns/priority/priority-select.tsx`, `packages/blocks/src/property-select/priority-select.tsx`, `packages/constants/src/issue/common.ts`, `packages/constants/src/issue/filter.ts`, `apps/web/components/dropdowns/member/member-select.tsx`, `apps/web/components/dropdowns/member/avatar.tsx`, `packages/blocks/src/property-select/member-select.tsx`, `apps/web/components/dropdowns/label/label-select.tsx`, `packages/blocks/src/property-select/label-select/label-select.tsx`, `packages/blocks/src/property-select/label-select/create-label-empty-state.tsx`, `apps/web/components/dropdowns/estimate/estimate-select.tsx`, `packages/blocks/src/property-select/estimate-select.tsx`, `apps/web/components/dropdowns/project/project-select.tsx`, `packages/blocks/src/property-select/project-select.tsx`, `packages/blocks/src/property-select/date-select.tsx`, `packages/blocks/src/property-select/date-range-select.tsx`, `packages/blocks/src/property-select/date-select-shell.tsx`, `apps/web/components/dropdowns/merged-date.tsx`, `apps/web/components/issues/label.tsx`

**Akzeptanzkriterien**

1. Contract: je Endpunkt dieses Pakets ≥ 1 Szenario mit Golden vom Original (Erfolg, Berechtigungsfehler, Validierungsfehler); Replay grün (L5).
2. Permission-Matrix (05 Anhang B) für alle Endpunkte dieses Pakets als L3-Test grün; Tenant-Isolation geprüft.
3. Signal-Stores strukturgleich zum MobX-Original (`store-parity-check`), Vitest je Action (L2).
4. E2E-Specs dieses Pakets grün gegen Original **und** funk. (Dual-Target, Pflichtszenarien 15 §3.9.3).
5. Visual-/DOM-/a11y-Prüfpunkte der betroffenen Screens (09 §4.14, 15 §3.10.2) innerhalb der Schwellwerte 15 §3.10.3 (Chromium); i18n-Schlüssel nur aus den Original-Locales (de/en).
6. `ce-coverage-check --ids CE-WI-020,CE-WI-021,CE-WI-022,CE-WI-023,CE-WI-024,CE-WI-027,CE-WI-028,CE-WI-029,CE-WI-030` grün (Mindestebenen 15 Anhang B).

**Testumfang**

- Pflicht-Ebenen (aus 15 Anhang B): L1, L2, L3, L5, L7, L8
- Testprojekte: `Funk.WorkItems.Tests`
- E2E-Specs (`frontend/apps/e2e/`): `web/work-items/properties.spec.ts`

### WP-I2-005 – Hierarchie und Relationen (Parent, Sub-Work-Items, Relationen, Widget-Aktionsleiste)

| Merkmal | Wert |
|---|---|
| Inkrement | I2 |
| Typ (DoD 15 §3.15.3) | V – Vertikaler Schnitt |
| Größe | M |
| parallelisierbar | ja |
| Abhängigkeiten | WP-I2-002, WP-I2-203 |
| CE-IDs | CE-WI-031, CE-WI-032, CE-WI-033, CE-WI-034 |

**Ziel.** Parent setzen/ändern/entfernen mit `IWorkItemHierarchyPolicy`, Sub-Work-Items, Relationen über den Relationstyp-Katalog, Widget-Aktionsleiste.

**Enthaltene CE-IDs**

| CE-ID | Feature | Status (15 Anh. B) | Inkrement laut 15 | Pflicht-Ebenen | Testprojekt | E2E-Spec |
|---|---|---|---|---|---|---|
| CE-WI-031 | Parent setzen, ändern, entfernen | übernommen | I2 | L1 L2 L3 L5 L7 L8 | Funk.WorkItems.Tests | `web/work-items/hierarchy-relations.spec.ts` |
| CE-WI-032 | Sub-Work-Items | übernommen | I2 | L1 L2 L3 L5 L7 L8 | Funk.WorkItems.Tests | `web/work-items/hierarchy-relations.spec.ts` |
| CE-WI-033 | Relationen zwischen Work Items | übernommen | I2 | L1 L2 L3 L5 L7 L8 | Funk.WorkItems.Tests | `web/work-items/hierarchy-relations.spec.ts` |
| CE-WI-034 | Widget-Aktionsleiste | übernommen | I2 | L1 L2 L3 L5 L7 L8 | Funk.WorkItems.Tests | `web/work-items/hierarchy-relations.spec.ts` |

**Betroffene Module/Libs in `funk.`**

- Backend: `src/modules/WorkItems/Funk.WorkItems` (Relations, Hierarchy)
- Frontend: `frontend/libs/web/work-items` (relations, sub-issues)

**Referenzdokumente**

- Architektur: 04 §4.5
- Architektur: 16 §5.3
- Analyse/Feature: `analysis/09-frontend-arbeitsobjekte-layouts.md` §2.13, §2.14, §3.10
- Analyse/Feature: `analysis/02b-datenmodell-arbeitsobjekte.md` §3.9
- Analyse/Feature: `analysis/04-api-intern-arbeitsobjekte.md` §2.6
- Feature-Katalog: `features/10-ce-feature-katalog.md` (Einträge CE-WI-031, CE-WI-032, CE-WI-033, CE-WI-034)

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- Backend: `apps/api/plane/db/models/issue.py:114-120`, `apps/api/plane/bgtasks/deletion_task.py:17-107`, `apps/api/plane/app/views/issue/sub_issue.py`, `apps/api/plane/app/views/issue/relation.py`, `apps/api/plane/utils/issue_relation_mapper.py`, `apps/api/plane/db/models/issue.py`, `apps/api/plane/db/models/issue.py:272-320`, `apps/api/plane/utils/exporters/schemas/issue.py:194-202`
- Frontend: `apps/web/components/issues/issue-detail/parent-select.tsx`, `apps/web/components/issues/parent-select-root.tsx`, `apps/web/components/issues/parent-issues-list-modal.tsx`, `apps/web/components/issues/issue-detail/parent/root.tsx`, `apps/web/components/issues/issue-detail/parent/siblings.tsx`, `apps/web/components/issues/issue-detail/parent/sibling-item.tsx`, `apps/web/components/issues/issue-detail-widgets/sub-issues/root.tsx`, `apps/web/components/issues/issue-detail-widgets/sub-issues/title.tsx`, `apps/web/components/issues/issue-detail-widgets/sub-issues/title-actions.tsx`, `apps/web/components/issues/issue-detail-widgets/sub-issues/display-filters.tsx`, `apps/web/components/issues/issue-detail-widgets/sub-issues/filters.tsx`, `apps/web/components/issues/issue-detail-widgets/sub-issues/quick-action-button.tsx`, `apps/web/components/issues/issue-detail-widgets/sub-issues/content.tsx`, `apps/web/components/issues/issue-detail-widgets/sub-issues/helper.ts`, `apps/web/components/issues/issue-detail-widgets/sub-issues/issues-list/root.tsx`, `apps/web/components/issues/issue-detail-widgets/sub-issues/issues-list/list-group.tsx`, `apps/web/components/issues/issue-detail-widgets/sub-issues/issues-list/list-item.tsx`, `apps/web/components/issues/issue-detail-widgets/sub-issues/issues-list/properties.tsx`, `apps/web/components/issues/issue-detail-widgets/relations/root.tsx`, `apps/web/components/issues/issue-detail-widgets/relations/title.tsx`, `apps/web/components/issues/issue-detail-widgets/relations/quick-action-button.tsx`, `apps/web/components/issues/issue-detail-widgets/relations/content.tsx`, `apps/web/components/issues/issue-detail-widgets/relations/helper.tsx`, `apps/web/components/issues/relations/issue-list.tsx`, `apps/web/components/issues/relations/issue-list-item.tsx`, `apps/web/components/issues/relations/properties.tsx`, `apps/web/components/relations/index.tsx`, `apps/web/components/issues/issue-detail-widgets/root.tsx`, `apps/web/components/issues/issue-detail-widgets/action-buttons.tsx`, `apps/web/components/issues/issue-detail-widgets/widget-button.tsx`, `apps/web/components/issues/issue-detail-widgets/issue-detail-widget-collapsibles.tsx`, `apps/web/components/issues/issue-detail-widgets/issue-detail-widget-modals.tsx`

**Endpunkte (Katalog 04, `architecture/_data/endpoints.json`; 5 registriert)**

| EP | Methode | Pfad | Oberfläche | Handler | Permission | Inkr. 04 | CE-IDs |
|---|---|---|---|---|---|---|---|
| EP-0264 | GET | `/api/workspaces/{slug}/projects/{project_id}/issues/{issue_id}/sub-issues/` | App | WorkItemEndpoints.ListSubWorkItemsQuery | project.work_item.read | I2 | CE-WI-032, CE-WI-031 |
| EP-0265 | POST | `/api/workspaces/{slug}/projects/{project_id}/issues/{issue_id}/sub-issues/` | App | WorkItemEndpoints.SetSubWorkItemsCommand | project.work_item.update | I2 | CE-WI-032, CE-WI-031 |
| EP-0280 | GET | `/api/workspaces/{slug}/projects/{project_id}/issues/{issue_id}/issue-relation/` | App | WorkItemRelationEndpoints.ListWorkItemRelationsQuery | project.work_item_relation.read | I2 | CE-WI-033 |
| EP-0281 | POST | `/api/workspaces/{slug}/projects/{project_id}/issues/{issue_id}/issue-relation/` | App | WorkItemRelationEndpoints.CreateWorkItemRelationsCommand | project.work_item_relation.create | I2 | CE-WI-033 |
| EP-0282 | POST | `/api/workspaces/{slug}/projects/{project_id}/issues/{issue_id}/remove-relation/` | App | WorkItemRelationEndpoints.RemoveWorkItemRelationCommand | project.work_item_relation.delete | I2 | CE-WI-033 |

**Akzeptanzkriterien**

1. Contract: je Endpunkt dieses Pakets ≥ 1 Szenario mit Golden vom Original (Erfolg, Berechtigungsfehler, Validierungsfehler); Replay grün (L5).
2. Permission-Matrix (05 Anhang B) für alle Endpunkte dieses Pakets als L3-Test grün; Tenant-Isolation geprüft.
3. Signal-Stores strukturgleich zum MobX-Original (`store-parity-check`), Vitest je Action (L2).
4. E2E-Specs dieses Pakets grün gegen Original **und** funk. (Dual-Target, Pflichtszenarien 15 §3.9.3).
5. Visual-/DOM-/a11y-Prüfpunkte der betroffenen Screens (09 §4.14, 15 §3.10.2) innerhalb der Schwellwerte 15 §3.10.3 (Chromium); i18n-Schlüssel nur aus den Original-Locales (de/en).
6. `ce-coverage-check --ids CE-WI-031,CE-WI-032,CE-WI-033,CE-WI-034` grün (Mindestebenen 15 Anhang B).

**Testumfang**

- Pflicht-Ebenen (aus 15 Anhang B): L1, L2, L3, L5, L7, L8
- Testprojekte: `Funk.WorkItems.Tests`
- E2E-Specs (`frontend/apps/e2e/`): `web/work-items/hierarchy-relations.spec.ts`

### WP-I2-006 – Links und Anhänge an Work Items

| Merkmal | Wert |
|---|---|
| Inkrement | I2 |
| Typ (DoD 15 §3.15.3) | V – Vertikaler Schnitt |
| Größe | M |
| parallelisierbar | ja |
| Abhängigkeiten | WP-I2-002, WP-I2-102 |
| CE-IDs | CE-WI-035, CE-WI-036 |

**Ziel.** Links mit Metadaten-Crawling (SSRF-sicher) und Anhänge über Datei-Assets.

**Enthaltene CE-IDs**

| CE-ID | Feature | Status (15 Anh. B) | Inkrement laut 15 | Pflicht-Ebenen | Testprojekt | E2E-Spec |
|---|---|---|---|---|---|---|
| CE-WI-035 | Links an Work Items | übernommen | I2 | L1 L2 L3 L5 L7 L8 | Funk.WorkItems.Tests | `web/work-items/links-attachments.spec.ts` |
| CE-WI-036 | Anhänge an Work Items | übernommen | I2 | L1 L2 L3 L5 L7 L8 | Funk.WorkItems.Tests | `web/work-items/links-attachments.spec.ts` |

**Betroffene Module/Libs in `funk.`**

- Backend: `src/modules/WorkItems/Funk.WorkItems` (Links, Attachments)
- Backend: `src/modules/Assets/Funk.Assets`
- Frontend: `frontend/libs/web/work-items` (links, attachments)

**Referenzdokumente**

- Architektur: 04 §4.5, §4.13
- Architektur: 06 §3.18
- Analyse/Feature: `analysis/09-frontend-arbeitsobjekte-layouts.md` §2.14
- Analyse/Feature: `analysis/04-api-intern-arbeitsobjekte.md` §2.5
- Analyse/Feature: `analysis/02b-datenmodell-arbeitsobjekte.md` §2.3
- Analyse/Feature: `analysis/07-hintergrundjobs-mail-storage-webhooks.md` §3.14, §2.16
- Analyse/Feature: `analysis/06-auth-sicherheit-querschnitt.md` §2.14
- Analyse/Feature: `analysis/13b-shared-packages-i18n.md` §2.4
- Feature-Katalog: `features/10-ce-feature-katalog.md` (Einträge CE-WI-035, CE-WI-036)

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- Backend: `apps/api/plane/app/views/issue/link.py`, `apps/api/plane/bgtasks/work_item_link_task.py`, `apps/api/plane/db/models/issue.py:371-384`, `apps/api/plane/utils/url_security.py`, `apps/api/plane/app/views/issue/attachment.py`, `apps/api/plane/db/models/asset.py`, `apps/api/plane/settings/common.py`, `apps/api/plane/db/models/issue.py:387-412`, `apps/api/plane/db/migrations/0079_auto_20241009_0619.py`, `apps/api/plane/db/models/asset.py:50-56`
- Frontend: `apps/web/components/issues/issue-detail-widgets/links/root.tsx`, `apps/web/components/issues/issue-detail-widgets/links/title.tsx`, `apps/web/components/issues/issue-detail-widgets/links/content.tsx`, `apps/web/components/issues/issue-detail-widgets/links/helper.tsx`, `apps/web/components/issues/issue-detail-widgets/links/quick-action-button.tsx`, `apps/web/components/issues/issue-detail/links/create-update-link-modal.tsx`, `apps/web/components/issues/issue-detail/links/link-item.tsx`, `apps/web/components/issues/issue-detail/links/link-list.tsx`, `packages/utils/src/get-icon-for-link.ts`, `packages/utils/src/url.ts`, `packages/utils/src/tlds.ts`, `apps/web/components/issues/issue-detail-widgets/attachments/root.tsx`, `apps/web/components/issues/issue-detail-widgets/attachments/title.tsx`, `apps/web/components/issues/issue-detail-widgets/attachments/content.tsx`, `apps/web/components/issues/issue-detail-widgets/attachments/helper.tsx`, `apps/web/components/issues/issue-detail-widgets/attachments/quick-action-button.tsx`, `apps/web/components/issues/attachment/attachment-item-list.tsx`, `apps/web/components/issues/attachment/attachment-list-item.tsx`, `apps/web/components/issues/attachment/attachment-list-upload-item.tsx`, `apps/web/components/issues/attachment/delete-attachment-modal.tsx`, `apps/web/components/issues/attachment/root.tsx`, `apps/web/components/issues/attachment/attachment-upload.tsx`, `apps/web/components/issues/attachment/attachments-list.tsx`, `apps/web/components/issues/attachment/attachment-detail.tsx`, `apps/web/components/issues/attachment/attachment-upload-details.tsx`

**Endpunkte (Katalog 04, `architecture/_data/endpoints.json`; 13 registriert)**

| EP | Methode | Pfad | Oberfläche | Handler | Permission | Inkr. 04 | CE-IDs |
|---|---|---|---|---|---|---|---|
| EP-0241 | GET | `/api/assets/v2/workspaces/{slug}/projects/{project_id}/issues/{issue_id}/attachments/` | App | WorkItemAttachmentEndpoints.ListWorkItemAttachmentsQuery | project.work_item_attachment.read | I2 | CE-WI-036, CE-OPS-012 |
| EP-0242 | POST | `/api/assets/v2/workspaces/{slug}/projects/{project_id}/issues/{issue_id}/attachments/` | App | WorkItemAttachmentEndpoints.CreateWorkItemAttachmentUploadCommand | project.work_item_attachment.create | I2 | CE-WI-036, CE-OPS-012 |
| EP-0243 | GET | `/api/assets/v2/workspaces/{slug}/projects/{project_id}/issues/{issue_id}/attachments/{pk}/` | App | WorkItemAttachmentEndpoints.GetWorkItemAttachmentRedirectQuery | project.work_item_attachment.read | I2 | CE-WI-036, CE-OPS-012 |
| EP-0244 | PATCH | `/api/assets/v2/workspaces/{slug}/projects/{project_id}/issues/{issue_id}/attachments/{pk}/` | App | WorkItemAttachmentEndpoints.ConfirmWorkItemAttachmentUploadCommand | project.work_item_attachment.update | I2 | CE-WI-036, CE-OPS-012 |
| EP-0245 | DELETE | `/api/assets/v2/workspaces/{slug}/projects/{project_id}/issues/{issue_id}/attachments/{pk}/` | App | WorkItemAttachmentEndpoints.DeleteWorkItemAttachmentCommand | project.work_item_attachment.delete | I2 | CE-WI-036, CE-OPS-012 |
| EP-0246 | GET | `/api/workspaces/{slug}/projects/{project_id}/issues/{issue_id}/issue-attachments/` | App | WorkItemAttachmentEndpoints.ListWorkItemAttachmentsQuery | project.work_item_attachment.read | I2 | CE-WI-036 |
| EP-0247 | POST | `/api/workspaces/{slug}/projects/{project_id}/issues/{issue_id}/issue-attachments/` | App | WorkItemAttachmentEndpoints.CreateWorkItemAttachmentCommand | project.work_item_attachment.create | I2 | CE-WI-036 |
| EP-0248 | DELETE | `/api/workspaces/{slug}/projects/{project_id}/issues/{issue_id}/issue-attachments/{pk}/` | App | WorkItemAttachmentEndpoints.DeleteWorkItemAttachmentCommand | project.work_item_attachment.delete | I2 | CE-WI-036 |
| EP-0275 | GET | `/api/workspaces/{slug}/projects/{project_id}/issues/{issue_id}/issue-links/` | App | WorkItemLinkEndpoints.ListWorkItemLinksQuery | project.work_item_link.read | I2 | CE-WI-035 |
| EP-0276 | POST | `/api/workspaces/{slug}/projects/{project_id}/issues/{issue_id}/issue-links/` | App | WorkItemLinkEndpoints.CreateWorkItemLinkCommand | project.work_item_link.create | I2 | CE-WI-035 |
| EP-0277 | GET | `/api/workspaces/{slug}/projects/{project_id}/issues/{issue_id}/issue-links/{pk}/` | App | WorkItemLinkEndpoints.GetWorkItemLinkQuery | project.work_item_link.read | I2 | CE-WI-035 |
| EP-0278 | PATCH | `/api/workspaces/{slug}/projects/{project_id}/issues/{issue_id}/issue-links/{pk}/` | App | WorkItemLinkEndpoints.UpdateWorkItemLinkCommand | project.work_item_link.update | I2 | CE-WI-035 |
| EP-0279 | DELETE | `/api/workspaces/{slug}/projects/{project_id}/issues/{issue_id}/issue-links/{pk}/` | App | WorkItemLinkEndpoints.DeleteWorkItemLinkCommand | project.work_item_link.delete | I2 | CE-WI-035 |

**Akzeptanzkriterien**

1. Contract: je Endpunkt dieses Pakets ≥ 1 Szenario mit Golden vom Original (Erfolg, Berechtigungsfehler, Validierungsfehler); Replay grün (L5).
2. Permission-Matrix (05 Anhang B) für alle Endpunkte dieses Pakets als L3-Test grün; Tenant-Isolation geprüft.
3. Signal-Stores strukturgleich zum MobX-Original (`store-parity-check`), Vitest je Action (L2).
4. E2E-Specs dieses Pakets grün gegen Original **und** funk. (Dual-Target, Pflichtszenarien 15 §3.9.3).
5. Visual-/DOM-/a11y-Prüfpunkte der betroffenen Screens (09 §4.14, 15 §3.10.2) innerhalb der Schwellwerte 15 §3.10.3 (Chromium); i18n-Schlüssel nur aus den Original-Locales (de/en).
6. `ce-coverage-check --ids CE-WI-035,CE-WI-036` grün (Mindestebenen 15 Anhang B).

**Testumfang**

- Pflicht-Ebenen (aus 15 Anhang B): L1, L2, L3, L5, L7, L8
- Testprojekte: `Funk.WorkItems.Tests`
- E2E-Specs (`frontend/apps/e2e/`): `web/work-items/links-attachments.spec.ts`

### WP-I2-007 – Kommentare, Emoji-Reaktionen, Mentions

| Merkmal | Wert |
|---|---|
| Inkrement | I2 |
| Typ (DoD 15 §3.15.3) | V – Vertikaler Schnitt |
| Größe | M |
| parallelisierbar | ja |
| Abhängigkeiten | WP-I2-008, WP-I2-021 |
| CE-IDs | CE-WI-037, CE-WI-038, CE-WI-044, CE-I18N-017 |

**Ziel.** Kommentare mit Lite-Editor, Emoji-Reaktionen auf Work Items und Kommentare (Reaktions-Komponenten), @Mentions in Beschreibung und Kommentaren mit `work_item_mentions`.

**Enthaltene CE-IDs**

| CE-ID | Feature | Status (15 Anh. B) | Inkrement laut 15 | Pflicht-Ebenen | Testprojekt | E2E-Spec |
|---|---|---|---|---|---|---|
| CE-WI-037 | Kommentare | übernommen | I2 | L1 L2 L3 L4 L5 L7 L8 (G-DOC/G-SANITIZE) | Funk.WorkItems.Tests | `web/work-items/comments-reactions-mentions.spec.ts` |
| CE-WI-038 | Emoji-Reaktionen auf Work Items und Kommentare | übernommen | I2 | L1 L2 L3 L5 L7 L8 | Funk.WorkItems.Tests | `web/work-items/comments-reactions-mentions.spec.ts` |
| CE-WI-044 | Erwähnungen (@Mentions) in Beschreibung und Kommentaren | übernommen | I2 | L1 L2 L3 L5 L7 L8 | Funk.WorkItems.Tests | `web/work-items/comments-reactions-mentions.spec.ts` |
| CE-I18N-017 | Emoji-Reaktions-Komponenten | übernommen | I0…I3 | L2 L7 L8 | Frontend-only | `gallery/design-system.spec.ts` |

**Betroffene Module/Libs in `funk.`**

- Backend: `src/modules/WorkItems/Funk.WorkItems` (Comments, Reactions, Mentions)
- Frontend: `frontend/libs/web/work-items` (comments)
- Frontend: `frontend/libs/shared/blocks` (emoji-reaction)

**Referenzdokumente**

- Architektur: 04 §4.5
- Architektur: 06 §3.9.5
- Architektur: 10 §3.11, §3.17
- Analyse/Feature: `analysis/09-frontend-arbeitsobjekte-layouts.md` §2.15, §2.13
- Analyse/Feature: `analysis/10b-frontend-cycles-modules-pages-views-weitere.md` §2.17
- Analyse/Feature: `analysis/04-api-intern-arbeitsobjekte.md` §2.4
- Analyse/Feature: `analysis/02b-datenmodell-arbeitsobjekte.md` §3.4, §2.7, §2.3
- Analyse/Feature: `analysis/13b-shared-packages-i18n.md` §2.2
- Analyse/Feature: `analysis/12-editor-echtzeit-live.md` §2.18
- Analyse/Feature: `analysis/13a-designsystem-ui-tokens.md` §2.26
- Feature-Katalog: `features/10-ce-feature-katalog.md` (Einträge CE-WI-037, CE-WI-038, CE-WI-044, CE-I18N-017)

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- Backend: `apps/api/plane/app/views/issue/comment.py`, `apps/api/plane/db/models/issue.py`, `apps/api/plane/db/models/issue.py:451-540`, `apps/api/plane/db/models/description.py`, `apps/api/plane/app/views/issue/comment.py:28-30,140`, `apps/api/plane/app/views/issue/reaction.py`, `apps/api/plane/db/models/issue.py:600-651`, `apps/api/plane/db/models/issue.py:323-342`, `apps/api/plane/bgtasks/notification_task.py:145-190`
- Frontend: `apps/web/components/comments/comment-create.tsx`, `apps/web/components/comments/card/root.tsx`, `apps/web/components/comments/card/display.tsx`, `apps/web/components/comments/card/edit-form.tsx`, `apps/web/components/comments/quick-actions.tsx`, `apps/web/components/comments/comment-reaction.tsx`, `apps/web/components/comments/comment-block.tsx`, `apps/web/components/issues/issue-detail/issue-activity/helper.tsx`, `apps/web/components/issues/issue-detail/reactions/issue-comment.tsx`, `apps/web/components/editor/lite-text/editor.tsx`, `apps/web/components/editor/lite-text/toolbar.tsx`, `apps/web/components/editor/lite-text/lite-toolbar.tsx`, `apps/web/components/issues/issue-detail/reactions/issue.tsx`, `packages/constants/src/emoji.ts`, `packages/utils/src/emoji.ts`, `packages/editor/src/extensions/mentions/extension.tsx`, `packages/editor/src/extensions/mentions/mentions-list-dropdown.tsx`, `packages/editor/src/extensions/mentions/utils.ts`, `apps/web/hooks/editor/use-editor-mention.tsx`, `apps/web/components/editor/embeds/mentions/user.tsx`, `packages/blocks/src/emoji-reaction/emoji-reaction.tsx`, `packages/blocks/src/emoji-reaction/animated-counter.tsx`

**Endpunkte (Katalog 04, `architecture/_data/endpoints.json`; 11 registriert)**

| EP | Methode | Pfad | Oberfläche | Handler | Permission | Inkr. 04 | CE-IDs |
|---|---|---|---|---|---|---|---|
| EP-0230 | GET | `/api/workspaces/{slug}/projects/{project_id}/comments/{comment_id}/reactions/` | App | ReactionEndpoints.ListCommentReactionsQuery | project.reaction.read | I2 | CE-WI-038 |
| EP-0231 | POST | `/api/workspaces/{slug}/projects/{project_id}/comments/{comment_id}/reactions/` | App | ReactionEndpoints.AddCommentReactionCommand | project.reaction.create | I2 | CE-WI-038 |
| EP-0232 | DELETE | `/api/workspaces/{slug}/projects/{project_id}/comments/{comment_id}/reactions/{reaction_code}/` | App | ReactionEndpoints.RemoveCommentReactionCommand | project.reaction.delete | I2 | CE-WI-038 |
| EP-0233 | GET | `/api/workspaces/{slug}/projects/{project_id}/issues/{issue_id}/reactions/` | App | ReactionEndpoints.ListWorkItemReactionsQuery | project.reaction.read | I2 | CE-WI-038 |
| EP-0234 | POST | `/api/workspaces/{slug}/projects/{project_id}/issues/{issue_id}/reactions/` | App | ReactionEndpoints.AddWorkItemReactionCommand | project.reaction.create | I2 | CE-WI-038 |
| EP-0235 | DELETE | `/api/workspaces/{slug}/projects/{project_id}/issues/{issue_id}/reactions/{reaction_code}/` | App | ReactionEndpoints.RemoveWorkItemReactionCommand | project.reaction.delete | I2 | CE-WI-038 |
| EP-0249 | GET | `/api/workspaces/{slug}/projects/{project_id}/issues/{issue_id}/comments/` | App | WorkItemCommentEndpoints.ListWorkItemCommentsQuery | project.work_item_comment.read | I2 | CE-WI-037, CE-WI-044 |
| EP-0250 | POST | `/api/workspaces/{slug}/projects/{project_id}/issues/{issue_id}/comments/` | App | WorkItemCommentEndpoints.CreateWorkItemCommentCommand | project.work_item_comment.create | I2 | CE-WI-037, CE-WI-044 |
| EP-0251 | GET | `/api/workspaces/{slug}/projects/{project_id}/issues/{issue_id}/comments/{pk}/` | App | WorkItemCommentEndpoints.GetWorkItemCommentQuery | project.work_item_comment.read | I2 | CE-WI-037, CE-WI-044 |
| EP-0252 | PATCH | `/api/workspaces/{slug}/projects/{project_id}/issues/{issue_id}/comments/{pk}/` | App | WorkItemCommentEndpoints.UpdateWorkItemCommentCommand | project.work_item_comment.update | I2 | CE-WI-037, CE-WI-044 |
| EP-0253 | DELETE | `/api/workspaces/{slug}/projects/{project_id}/issues/{issue_id}/comments/{pk}/` | App | WorkItemCommentEndpoints.DeleteWorkItemCommentCommand | project.work_item_comment.delete | I2 | CE-WI-037, CE-WI-044 |

**Akzeptanzkriterien**

1. Contract: je Endpunkt dieses Pakets ≥ 1 Szenario mit Golden vom Original (Erfolg, Berechtigungsfehler, Validierungsfehler); Replay grün (L5).
2. Permission-Matrix (05 Anhang B) für alle Endpunkte dieses Pakets als L3-Test grün; Tenant-Isolation geprüft.
3. Signal-Stores strukturgleich zum MobX-Original (`store-parity-check`), Vitest je Action (L2).
4. E2E-Specs dieses Pakets grün gegen Original **und** funk. (Dual-Target, Pflichtszenarien 15 §3.9.3).
5. Visual-/DOM-/a11y-Prüfpunkte der betroffenen Screens (09 §4.14, 15 §3.10.2) innerhalb der Schwellwerte 15 §3.10.3 (Chromium); i18n-Schlüssel nur aus den Original-Locales (de/en).
6. `ce-coverage-check --ids CE-WI-037,CE-WI-038,CE-WI-044,CE-I18N-017` grün (Mindestebenen 15 Anhang B).

**Testumfang**

- Pflicht-Ebenen (aus 15 Anhang B): L1, L2, L3, L4, L5, L7, L8
- Testprojekte: `Funk.WorkItems.Tests`, `Frontend-only`
- E2E-Specs (`frontend/apps/e2e/`): `web/work-items/comments-reactions-mentions.spec.ts`, `gallery/design-system.spec.ts`

### WP-I2-008 – Aktivitätsverlauf, Activity-Filter, Beschreibungs-Versionen, Eigenschafts-Historie, Abonnements

| Merkmal | Wert |
|---|---|
| Inkrement | I2 |
| Typ (DoD 15 §3.15.3) | V – Vertikaler Schnitt |
| Größe | L |
| parallelisierbar | ja |
| Abhängigkeiten | WP-I2-002, WP-I2-024, WP-I1-204 |
| CE-IDs | CE-WI-039, CE-WI-040, CE-WI-041, CE-WI-042, CE-WI-043 |

**Ziel.** Vollständige Activity-Pipeline (38 Varianten, 78 Aufrufstellen nach `_data/06-jobs.json`), Activity-Filter und -Sortierung, Beschreibungs-Versionshistorie (ED-3), Eigenschafts-Historie (`work_item_versions`, Aufbewahrung Default 20, 17 Z-114) und Abonnements.

**Enthaltene CE-IDs**

| CE-ID | Feature | Status (15 Anh. B) | Inkrement laut 15 | Pflicht-Ebenen | Testprojekt | E2E-Spec |
|---|---|---|---|---|---|---|
| CE-WI-039 | Aktivitätsverlauf | übernommen | I2 | L1 L2 L3 L5 L7 L8 | Funk.WorkItems.Tests | `web/work-items/activity-history.spec.ts` |
| CE-WI-040 | Activity-Filter und -Sortierung | übernommen | I2 | L1 L2 L3 L5 L7 L8 | Funk.WorkItems.Tests | `web/work-items/activity-history.spec.ts` |
| CE-WI-041 | Beschreibungs-Versionshistorie | übernommen | I2 | L1 L2 L3 L5 L7 L8 | Funk.WorkItems.Tests | `web/work-items/activity-history.spec.ts` |
| CE-WI-042 | Eigenschafts-Historie (IssueVersion) | übernommen | I2 | L1 L2 L3 L5 L7 L8 | Funk.WorkItems.Tests | `web/work-items/activity-history.spec.ts` |
| CE-WI-043 | Work Items abonnieren | übernommen | I2 | L1 L2 L3 L5 L7 L8 | Funk.WorkItems.Tests | `web/work-items/activity-history.spec.ts` |

**Betroffene Module/Libs in `funk.`**

- Backend: `src/modules/WorkItems/Funk.WorkItems/Activity/`
- Frontend: `frontend/libs/web/work-items` (activity)

**Referenzdokumente**

- Architektur: 06 §3.9, §4.4–§4.7
- Architektur: 03 §3.9.2
- Architektur: 06 R-D06-03
- Analyse/Feature: `analysis/09-frontend-arbeitsobjekte-layouts.md` §2.15, §2.13
- Analyse/Feature: `analysis/04-api-intern-arbeitsobjekte.md` §3.9, §2.9, §2.7
- Analyse/Feature: `analysis/07-hintergrundjobs-mail-storage-webhooks.md` §2.5, §3.11
- Analyse/Feature: `analysis/02b-datenmodell-arbeitsobjekte.md` §2.3, §3.6
- Analyse/Feature: `analysis/13b-shared-packages-i18n.md` §2.2
- Analyse/Feature: `analysis/10a-frontend-workspace-projekt-navigation.md` §2.16
- Feature-Katalog: `features/10-ce-feature-katalog.md` (Einträge CE-WI-039, CE-WI-040, CE-WI-041, CE-WI-042, CE-WI-043)

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- Backend: `apps/api/plane/app/views/issue/activity.py`, `apps/api/plane/bgtasks/issue_activities_task.py`, `apps/api/plane/db/models/issue.py`, `apps/api/plane/app/serializers/issue.py`, `apps/api/plane/db/models/issue.py:415-448`, `apps/api/plane/app/views/issue/version.py`, `apps/api/plane/app/views/intake/base.py`, `apps/api/plane/bgtasks/issue_description_version_task.py`, `apps/api/plane/db/models/issue.py:782-822`, `apps/api/plane/bgtasks/cleanup_task.py:128-146`, `apps/api/plane/app/urls/issue.py:256-275`, `apps/api/plane/bgtasks/cleanup_task.py`, `apps/api/plane/db/models/issue.py:677-779`, `apps/api/plane/bgtasks/issue_version_sync.py`, `apps/api/plane/app/views/issue/subscriber.py`, `apps/api/plane/db/models/issue.py:574-597`
- Frontend: `apps/web/components/issues/issue-detail/issue-activity/root.tsx`, `apps/web/components/issues/issue-detail/issue-activity/activity-comment-root.tsx`, `apps/web/components/issues/issue-detail/issue-activity/activity/activity-list.tsx`, `apps/web/components/issues/issue-detail/issue-activity/activity/actions/helpers/activity-block.tsx`, `apps/web/components/issues/issue-detail/issue-activity/filter-root.tsx`, `apps/web/components/issues/issue-detail/issue-activity/activity-filter.tsx`, `apps/web/components/issues/issue-detail/issue-activity/sort-root.tsx`, `packages/constants/src/issue/filter.ts`, `apps/web/components/core/description-versions/root.tsx`, `apps/web/components/core/description-versions/dropdown.tsx`, `apps/web/components/core/description-versions/modal.tsx`, `apps/web/components/core/description-versions`, `apps/web/components/issues/peek-overview/issue-detail.tsx`, `apps/web/components/issues/issue-detail/issue-detail-quick-actions.tsx`, `apps/web/components/issues/issue-detail/subscription.tsx`

**Endpunkte (Katalog 04, `architecture/_data/endpoints.json`; 11 registriert)**

| EP | Methode | Pfad | Oberfläche | Handler | Permission | Inkr. 04 | CE-IDs |
|---|---|---|---|---|---|---|---|
| EP-0236 | GET | `/api/workspaces/{slug}/projects/{project_id}/issues/{issue_id}/history/` | App | WorkItemActivityEndpoints.ListWorkItemHistoryQuery | project.work_item_activity.read | I2 | CE-WI-039, CE-WI-040 |
| EP-0237 | GET | `/api/workspaces/{slug}/projects/{project_id}/issues/{issue_id}/versions/` | App | WorkItemActivityEndpoints.ListWorkItemVersionsQuery | project.work_item_activity.read | I2 | CE-WI-042 |
| EP-0238 | GET | `/api/workspaces/{slug}/projects/{project_id}/issues/{issue_id}/versions/{pk}/` | App | WorkItemActivityEndpoints.GetWorkItemVersionQuery | project.work_item_activity.read | I2 | CE-WI-042 |
| EP-0239 | GET | `/api/workspaces/{slug}/projects/{project_id}/work-items/{work_item_id}/description-versions/` | App | WorkItemActivityEndpoints.ListWorkItemDescriptionVersionsQuery | project.work_item_activity.read | I2 | CE-WI-041 |
| EP-0240 | GET | `/api/workspaces/{slug}/projects/{project_id}/work-items/{work_item_id}/description-versions/{pk}/` | App | WorkItemActivityEndpoints.GetWorkItemDescriptionVersionQuery | project.work_item_activity.read | I2 | CE-WI-041 |
| EP-0283 | GET | `/api/workspaces/{slug}/projects/{project_id}/issues/{issue_id}/issue-subscribers/` | App | WorkItemSubscriptionEndpoints.ListWorkItemSubscribersQuery | project.work_item_subscription.read | I2 | CE-WI-043 |
| EP-0284 | POST | `/api/workspaces/{slug}/projects/{project_id}/issues/{issue_id}/issue-subscribers/` | App | WorkItemSubscriptionEndpoints.AddWorkItemSubscriberCommand | project.work_item_subscription.manage | I2 | CE-WI-043 |
| EP-0285 | DELETE | `/api/workspaces/{slug}/projects/{project_id}/issues/{issue_id}/issue-subscribers/{subscriber_id}/` | App | WorkItemSubscriptionEndpoints.RemoveWorkItemSubscriberCommand | project.work_item_subscription.manage | I2 | CE-WI-043 |
| EP-0286 | GET | `/api/workspaces/{slug}/projects/{project_id}/issues/{issue_id}/subscribe/` | App | WorkItemSubscriptionEndpoints.GetWorkItemSubscriptionStatusQuery | project.work_item_subscription.read | I2 | CE-WI-043 |
| EP-0287 | POST | `/api/workspaces/{slug}/projects/{project_id}/issues/{issue_id}/subscribe/` | App | WorkItemSubscriptionEndpoints.SubscribeWorkItemCommand | project.work_item_subscription.subscribe | I2 | CE-WI-043 |
| EP-0288 | DELETE | `/api/workspaces/{slug}/projects/{project_id}/issues/{issue_id}/subscribe/` | App | WorkItemSubscriptionEndpoints.UnsubscribeWorkItemCommand | project.work_item_subscription.subscribe | I2 | CE-WI-043 |

**Akzeptanzkriterien**

1. Golden je Activity-Variante A1…A38 (AK-D06-10); jede Aufrufstelle C1…C78 aus `_data/06-jobs.json` ist einem Test zugeordnet.
2. Contract: je Endpunkt dieses Pakets ≥ 1 Szenario mit Golden vom Original (Erfolg, Berechtigungsfehler, Validierungsfehler); Replay grün (L5).
3. Permission-Matrix (05 Anhang B) für alle Endpunkte dieses Pakets als L3-Test grün; Tenant-Isolation geprüft.
4. Signal-Stores strukturgleich zum MobX-Original (`store-parity-check`), Vitest je Action (L2).
5. E2E-Specs dieses Pakets grün gegen Original **und** funk. (Dual-Target, Pflichtszenarien 15 §3.9.3).
6. Visual-/DOM-/a11y-Prüfpunkte der betroffenen Screens (09 §4.14, 15 §3.10.2) innerhalb der Schwellwerte 15 §3.10.3 (Chromium); i18n-Schlüssel nur aus den Original-Locales (de/en).
7. `ce-coverage-check --ids CE-WI-039,CE-WI-040,CE-WI-041,CE-WI-042,CE-WI-043` grün (Mindestebenen 15 Anhang B).

**Testumfang**

- Pflicht-Ebenen (aus 15 Anhang B): L1, L2, L3, L5, L7, L8
- Testprojekte: `Funk.WorkItems.Tests`
- E2E-Specs (`frontend/apps/e2e/`): `web/work-items/activity-history.spec.ts`

### WP-I2-009 – Work Items archivieren/wiederherstellen und löschen (einzeln und Bulk)

| Merkmal | Wert |
|---|---|
| Inkrement | I2 |
| Typ (DoD 15 §3.15.3) | V – Vertikaler Schnitt |
| Größe | M |
| parallelisierbar | ja |
| Abhängigkeiten | WP-I2-002 |
| CE-IDs | CE-WI-045, CE-WI-046, CE-WI-047, CE-WI-048 |

**Ziel.** Archivieren und Wiederherstellen, Bulk-Archivieren (Backend), Löschen einzeln und mehrfach mit Soft-Delete-Kaskade.

**Enthaltene CE-IDs**

| CE-ID | Feature | Status (15 Anh. B) | Inkrement laut 15 | Pflicht-Ebenen | Testprojekt | E2E-Spec |
|---|---|---|---|---|---|---|
| CE-WI-045 | Work Items archivieren und wiederherstellen | übernommen | I2 | L1 L2 L3 L5 L7 L8 | Funk.WorkItems.Tests | `web/work-items/archive-delete.spec.ts` |
| CE-WI-046 | Bulk-Archivieren (Backend) | übernommen | I2 | L1 L2 L3 L5 L7 L8 | Funk.WorkItems.Tests | `web/work-items/archive-delete.spec.ts` |
| CE-WI-047 | Work Item löschen | übernommen | I2 | L1 L2 L3 L5 L7 L8 | Funk.WorkItems.Tests | `web/work-items/archive-delete.spec.ts` |
| CE-WI-048 | Mehrere Work Items löschen | übernommen | I2 | L1 L2 L3 L5 L7 L8 | Funk.WorkItems.Tests | `web/work-items/archive-delete.spec.ts` |

**Betroffene Module/Libs in `funk.`**

- Backend: `src/modules/WorkItems/Funk.WorkItems`
- Frontend: `frontend/libs/web/work-items`

**Referenzdokumente**

- Architektur: 04 §4.5, §3.10.1 (Bulk)
- Architektur: 03 §3.5
- Analyse/Feature: `analysis/09-frontend-arbeitsobjekte-layouts.md` §3.13, §2.18
- Analyse/Feature: `analysis/04-api-intern-arbeitsobjekte.md` §2.8, §3.5
- Analyse/Feature: `analysis/02b-datenmodell-arbeitsobjekte.md` §3.13
- Analyse/Feature: `analysis/08-frontend-web-architektur.md` §2.2
- Analyse/Feature: `analysis/10a-frontend-workspace-projekt-navigation.md` §2.16
- Feature-Katalog: `features/10-ce-feature-katalog.md` (Einträge CE-WI-045, CE-WI-046, CE-WI-047, CE-WI-048)

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- Backend: `apps/api/plane/app/views/issue/archive.py`, `apps/api/plane/db/models/issue.py:160`, `apps/api/plane/bgtasks/issue_automation_task.py:26-148`, `apps/api/plane/app/views/issue/base.py`, `apps/api/plane/bgtasks/deletion_task.py`
- Frontend: `apps/web/components/issues/archive-issue-modal.tsx`, `packages/constants/src/state.ts`, `apps/web/components/issues/issue-layouts/quick-action-dropdowns/archived-issue.tsx`, `apps/web/components/issues/issue-detail/issue-detail-quick-actions.tsx`, `apps/web/services/issue/issue_archive.service.ts`, `apps/web/app/(all)/[workspaceSlug]/(projects)/projects/(detail)/[projectId]/archives/issues/(list)/page.tsx`, `apps/web/app/(all)/[workspaceSlug]/(projects)/projects/(detail)/[projectId]/archives/issues/(detail)/[archivedIssueId]/page.tsx`, `apps/web/app/(all)/[workspaceSlug]/(projects)/projects/(detail)/[projectId]/archives/cycles/page.tsx`, `apps/web/app/(all)/[workspaceSlug]/(projects)/projects/(detail)/[projectId]/archives/modules/page.tsx`, `apps/web/store/issue/archived/issue.store.ts`, `apps/web/components/issues/delete-issue-modal.tsx`, `apps/web/components/core/modals/bulk-delete-issues-modal.tsx`, `apps/web/components/core/modals/bulk-delete-issues-modal-item.tsx`, `apps/web/components/modals/work-item-level.tsx`

**Endpunkte (Katalog 04, `architecture/_data/endpoints.json`; 6 registriert)**

| EP | Methode | Pfad | Oberfläche | Handler | Permission | Inkr. 04 | CE-IDs |
|---|---|---|---|---|---|---|---|
| EP-0255 | POST | `/api/workspaces/{slug}/projects/{project_id}/bulk-archive-issues/` | App | WorkItemEndpoints.BulkArchiveWorkItemsCommand | project.work_item.archive | I3 | CE-WI-046 |
| EP-0256 | DELETE | `/api/workspaces/{slug}/projects/{project_id}/bulk-delete-issues/` | App | WorkItemEndpoints.BulkDeleteWorkItemsCommand | project.work_item.delete | I2 | CE-WI-048 |
| EP-0268 | DELETE | `/api/workspaces/{slug}/projects/{project_id}/issues/{pk}/` | App | WorkItemEndpoints.DeleteWorkItemCommand | project.work_item.delete | I2 | CE-WI-047 |
| EP-0269 | GET | `/api/workspaces/{slug}/projects/{project_id}/issues/{pk}/archive/` | App | WorkItemEndpoints.GetArchivedWorkItemQuery | project.work_item.read_archived | I3 | CE-WI-045 |
| EP-0270 | POST | `/api/workspaces/{slug}/projects/{project_id}/issues/{pk}/archive/` | App | WorkItemEndpoints.ArchiveWorkItemCommand | project.work_item.archive | I3 | CE-WI-045 |
| EP-0271 | DELETE | `/api/workspaces/{slug}/projects/{project_id}/issues/{pk}/archive/` | App | WorkItemEndpoints.UnarchiveWorkItemCommand | project.work_item.unarchive | I3 | CE-WI-045 |

**Akzeptanzkriterien**

1. Contract: je Endpunkt dieses Pakets ≥ 1 Szenario mit Golden vom Original (Erfolg, Berechtigungsfehler, Validierungsfehler); Replay grün (L5).
2. Permission-Matrix (05 Anhang B) für alle Endpunkte dieses Pakets als L3-Test grün; Tenant-Isolation geprüft.
3. Signal-Stores strukturgleich zum MobX-Original (`store-parity-check`), Vitest je Action (L2).
4. E2E-Specs dieses Pakets grün gegen Original **und** funk. (Dual-Target, Pflichtszenarien 15 §3.9.3).
5. Visual-/DOM-/a11y-Prüfpunkte der betroffenen Screens (09 §4.14, 15 §3.10.2) innerhalb der Schwellwerte 15 §3.10.3 (Chromium); i18n-Schlüssel nur aus den Original-Locales (de/en).
6. `ce-coverage-check --ids CE-WI-045,CE-WI-046,CE-WI-047,CE-WI-048` grün (Mindestebenen 15 Anhang B).

**Testumfang**

- Pflicht-Ebenen (aus 15 Anhang B): L1, L2, L3, L5, L7, L8
- Testprojekte: `Funk.WorkItems.Tests`
- E2E-Specs (`frontend/apps/e2e/`): `web/work-items/archive-delete.spec.ts`

### WP-I2-010 – Workspace-Drafts

| Merkmal | Wert |
|---|---|
| Inkrement | I2 |
| Typ (DoD 15 §3.15.3) | V – Vertikaler Schnitt |
| Größe | M |
| parallelisierbar | ja |
| Abhängigkeiten | WP-I2-001 |
| CE-IDs | CE-WI-049 |

**Ziel.** Workspace-Drafts mit Anlage, Bearbeitung, Umwandlung in Work Items und Liste.

**Enthaltene CE-IDs**

| CE-ID | Feature | Status (15 Anh. B) | Inkrement laut 15 | Pflicht-Ebenen | Testprojekt | E2E-Spec |
|---|---|---|---|---|---|---|
| CE-WI-049 | Workspace-Drafts | übernommen | I2 | L1 L2 L3 L5 L7 L8 | Funk.WorkItems.Tests | `web/work-items/drafts.spec.ts` |

**Betroffene Module/Libs in `funk.`**

- Backend: `src/modules/WorkItems/Funk.WorkItems` (Drafts)
- Frontend: `frontend/libs/web/work-items` (drafts)

**Referenzdokumente**

- Architektur: 04 §4.5
- Architektur: 03 §3.4.5
- Analyse/Feature: `analysis/09-frontend-arbeitsobjekte-layouts.md` §3.11
- Analyse/Feature: `analysis/08-frontend-web-architektur.md` §2.2
- Analyse/Feature: `analysis/03-api-intern-workspace-projekt-user.md` §3.10
- Analyse/Feature: `analysis/04-api-intern-arbeitsobjekte.md` §2.15
- Analyse/Feature: `analysis/02b-datenmodell-arbeitsobjekte.md` §2.3
- Feature-Katalog: `features/10-ce-feature-katalog.md` (Einträge CE-WI-049)

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- Backend: `apps/api/plane/app/views/workspace/draft.py`, `apps/api/plane/app/serializers/draft.py`, `apps/api/plane/app/urls/workspace.py`, `apps/api/plane/db/models/draft.py`
- Frontend: `apps/web/components/issues/workspace-draft/root.tsx`, `apps/web/components/issues/workspace-draft/draft-issue-block.tsx`, `apps/web/components/issues/workspace-draft/draft-issue-properties.tsx`, `apps/web/components/issues/workspace-draft/quick-action.tsx`, `apps/web/components/issues/workspace-draft/empty-state.tsx`, `apps/web/components/issues/workspace-draft/loader.tsx`, `apps/web/components/issues/workspace-draft/delete-modal.tsx`, `apps/web/app/(all)/[workspaceSlug]/(projects)/drafts/page.tsx`, `apps/web/app/(all)/[workspaceSlug]/(projects)/drafts/header.tsx`, `apps/web/store/issue/workspace-draft/issue.store.ts`, `apps/web/services/issue/workspace_draft.service.ts`

**Endpunkte (Katalog 04, `architecture/_data/endpoints.json`; 6 registriert)**

| EP | Methode | Pfad | Oberfläche | Handler | Permission | Inkr. 04 | CE-IDs |
|---|---|---|---|---|---|---|---|
| EP-0224 | GET | `/api/workspaces/{slug}/draft-issues/` | App | DraftWorkItemEndpoints.ListDraftWorkItemsQuery | workspace.draft_work_item.read | I2 | CE-WI-049 |
| EP-0225 | POST | `/api/workspaces/{slug}/draft-issues/` | App | DraftWorkItemEndpoints.CreateDraftWorkItemCommand | workspace.draft_work_item.create | I2 | CE-WI-049 |
| EP-0226 | GET | `/api/workspaces/{slug}/draft-issues/{pk}/` | App | DraftWorkItemEndpoints.GetDraftWorkItemQuery | workspace.draft_work_item.read | I2 | CE-WI-049 |
| EP-0227 | PATCH | `/api/workspaces/{slug}/draft-issues/{pk}/` | App | DraftWorkItemEndpoints.UpdateDraftWorkItemCommand | workspace.draft_work_item.update | I2 | CE-WI-049 |
| EP-0228 | DELETE | `/api/workspaces/{slug}/draft-issues/{pk}/` | App | DraftWorkItemEndpoints.DeleteDraftWorkItemCommand | workspace.draft_work_item.delete | I2 | CE-WI-049 |
| EP-0229 | POST | `/api/workspaces/{slug}/draft-to-issue/{draft_id}/` | App | DraftWorkItemEndpoints.ConvertDraftWorkItemCommand | workspace.draft_work_item.convert | I2 | CE-WI-049 |

**Akzeptanzkriterien**

1. Contract: je Endpunkt dieses Pakets ≥ 1 Szenario mit Golden vom Original (Erfolg, Berechtigungsfehler, Validierungsfehler); Replay grün (L5).
2. Permission-Matrix (05 Anhang B) für alle Endpunkte dieses Pakets als L3-Test grün; Tenant-Isolation geprüft.
3. Signal-Stores strukturgleich zum MobX-Original (`store-parity-check`), Vitest je Action (L2).
4. E2E-Specs dieses Pakets grün gegen Original **und** funk. (Dual-Target, Pflichtszenarien 15 §3.9.3).
5. Visual-/DOM-/a11y-Prüfpunkte der betroffenen Screens (09 §4.14, 15 §3.10.2) innerhalb der Schwellwerte 15 §3.10.3 (Chromium); i18n-Schlüssel nur aus den Original-Locales (de/en).
6. `ce-coverage-check --ids CE-WI-049` grün (Mindestebenen 15 Anhang B).

**Testumfang**

- Pflicht-Ebenen (aus 15 Anhang B): L1, L2, L3, L5, L7, L8
- Testprojekte: `Funk.WorkItems.Tests`
- E2E-Specs (`frontend/apps/e2e/`): `web/work-items/drafts.spec.ts`

### WP-I2-011 – Layout-Umschaltung, Projekt-Work-Items-Seite und Kopf, Layout-Kontextmenü

| Merkmal | Wert |
|---|---|
| Inkrement | I2 |
| Typ (DoD 15 §3.15.3) | V – Vertikaler Schnitt |
| Größe | M |
| parallelisierbar | nein |
| Abhängigkeiten | WP-I2-012 |
| CE-IDs | CE-LV-001, CE-LV-002, CE-LV-003 |

**Ziel.** Projekt-Work-Items-Seite mit Kopf, Layout-Umschaltung und Layout-Kontextmenü; Layout-Kontexte Cycle/Modul/View/Archiv/Profil folgen mit WP-I3-001.

**Enthaltene CE-IDs**

| CE-ID | Feature | Status (15 Anh. B) | Inkrement laut 15 | Pflicht-Ebenen | Testprojekt | E2E-Spec |
|---|---|---|---|---|---|---|
| CE-LV-001 | Layout-Umschaltung | übernommen | I2 | L2 L7 L8 | Frontend-only | `web/layouts/layout-switch.spec.ts` |
| CE-LV-002 | Projekt-Work-Items-Seite und Kopf | übernommen | I2 | L2 L7 L8 | Frontend-only | `web/layouts/layout-switch.spec.ts` |
| CE-LV-003 | Layout-Kontextmenü im Kopf | übernommen | I2 | L2 L7 L8 | Frontend-only | `web/layouts/layout-switch.spec.ts` |

**Betroffene Module/Libs in `funk.`**

- Frontend: `frontend/libs/web/work-items` (issue-layouts/roots, headers)

**Referenzdokumente**

- Architektur: 08 §4.1, §3.4.6
- Architektur: 09 §4.14
- Analyse/Feature: `analysis/09-frontend-arbeitsobjekte-layouts.md` §2.10, §2.18
- Analyse/Feature: `analysis/13b-shared-packages-i18n.md` §2.2
- Analyse/Feature: `analysis/08-frontend-web-architektur.md` §3.4
- Feature-Katalog: `features/10-ce-feature-katalog.md` (Einträge CE-LV-001, CE-LV-002, CE-LV-003)

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- Frontend: `apps/web/components/issues/issue-layouts/filters/header/layout-selection.tsx`, `apps/web/components/issues/issue-layouts/filters/header/mobile-layout-selection.tsx`, `apps/web/components/issues/filters.tsx`, `apps/web/store/issue/project/filter.store.ts`, `apps/web/components/dropdowns/layout.tsx`, `packages/constants/src/issue/layout.ts`, `packages/types/src/issues/issue.ts`, `packages/constants/src/calendar.ts`, `apps/web/components/issues/header.tsx`, `apps/web/app/(all)/[workspaceSlug]/(projects)/projects/(detail)/[projectId]/issues/(list)/page.tsx`, `apps/web/components/issues/issue-layouts/roots/project-layout-root.tsx`, `apps/web/store/issue/helpers/base-issues.store.ts`, `apps/web/components/issues/layout-quick-actions.tsx`, `apps/web/components/common/quick-actions-helper.tsx`

**Akzeptanzkriterien**

1. Contract: je Endpunkt dieses Pakets ≥ 1 Szenario mit Golden vom Original (Erfolg, Berechtigungsfehler, Validierungsfehler); Replay grün (L5).
2. Permission-Matrix (05 Anhang B) für alle Endpunkte dieses Pakets als L3-Test grün; Tenant-Isolation geprüft.
3. Signal-Stores strukturgleich zum MobX-Original (`store-parity-check`), Vitest je Action (L2).
4. E2E-Specs dieses Pakets grün gegen Original **und** funk. (Dual-Target, Pflichtszenarien 15 §3.9.3).
5. Visual-/DOM-/a11y-Prüfpunkte der betroffenen Screens (09 §4.14, 15 §3.10.2) innerhalb der Schwellwerte 15 §3.10.3 (Chromium); i18n-Schlüssel nur aus den Original-Locales (de/en).
6. `ce-coverage-check --ids CE-LV-001,CE-LV-002,CE-LV-003` grün (Mindestebenen 15 Anhang B).

**Testumfang**

- Pflicht-Ebenen (aus 15 Anhang B): L2, L7, L8
- Testprojekte: `Frontend-only`
- E2E-Specs (`frontend/apps/e2e/`): `web/layouts/layout-switch.spec.ts`

### WP-I2-012 – Work-Item-Liste mit Gruppierung/Pagination (Backend), Rich-Filter (AND/OR/NOT), Filterzeile, Filterwerte, Filterfelder

| Merkmal | Wert |
|---|---|
| Inkrement | I2 |
| Typ (DoD 15 §3.15.3) | V – Vertikaler Schnitt |
| Größe | L |
| parallelisierbar | nein |
| Abhängigkeiten | WP-I2-201, WP-I0-909, WP-I2-001 |
| CE-IDs | CE-LV-005, CE-LV-006, CE-LV-007, CE-LV-008, CE-LV-009, CE-LV-010 |

**Ziel.** Gruppierte und sub-gruppierte Pagination (Port `GroupedOffsetPaginator`), Rich-Filter-Ausdrücke über den Filter-AST, Rich-Filter-Zeile, Filterwert-Eingaben, ungültige Bedingungen, Filterfelder.

**Enthaltene CE-IDs**

| CE-ID | Feature | Status (15 Anh. B) | Inkrement laut 15 | Pflicht-Ebenen | Testprojekt | E2E-Spec |
|---|---|---|---|---|---|---|
| CE-LV-005 | Work-Item-Liste mit Gruppierung und Paginierung (Backend) | übernommen | I2 | L1 L2 L3 L5 L7 L8 L9 (LT-01…03) | Funk.WorkItems.Tests | `web/layouts/filters.spec.ts` |
| CE-LV-006 | Rich-Filter-Ausdrücke (AND/OR/NOT) | übernommen | I2 | L1 L2 L3 L5 L7 L8 L9 (LT-04) | Funk.WorkItems.Tests | `web/layouts/filters.spec.ts` |
| CE-LV-007 | Rich-Filter-Zeile | übernommen | I2 | L2 L7 L8 | Frontend-only | `web/layouts/filters.spec.ts` |
| CE-LV-008 | Filterwert-Eingaben | übernommen | I2 | L2 L7 L8 | Frontend-only | `web/layouts/filters.spec.ts` |
| CE-LV-009 | Ungültige Filterbedingung | übernommen | I2 | L2 L7 L8 | Frontend-only | `web/layouts/filters.spec.ts` |
| CE-LV-010 | Work-Item-Filterfelder | übernommen | I2 | L1 L2 L3 L5 L7 L8 | Funk.WorkItems.Tests | `web/layouts/filters.spec.ts` |

**Betroffene Module/Libs in `funk.`**

- Backend: `src/modules/WorkItems/Funk.WorkItems/Query/`
- Frontend: `frontend/libs/web/work-items` (rich-filters)
- Frontend: `frontend/libs/shared/shared-state` (work-item-filters)

**Referenzdokumente**

- Architektur: 02 §3.11
- Architektur: 04 §3.8
- Architektur: 08 §3.4.6
- Analyse/Feature: `analysis/04-api-intern-arbeitsobjekte.md` §3.1, §3.3
- Analyse/Feature: `analysis/06-auth-sicherheit-querschnitt.md` §2.13
- Analyse/Feature: `analysis/08-frontend-web-architektur.md` §3.4
- Analyse/Feature: `analysis/13b-shared-packages-i18n.md` §3.2
- Analyse/Feature: `analysis/09-frontend-arbeitsobjekte-layouts.md` §2.11
- Feature-Katalog: `features/10-ce-feature-katalog.md` (Einträge CE-LV-005, CE-LV-006, CE-LV-007, CE-LV-008, CE-LV-009, CE-LV-010)

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- Backend: `apps/api/plane/app/views/issue/base.py`, `apps/api/plane/utils/grouper.py`, `apps/api/plane/utils/paginator.py`, `apps/api/plane/utils/order_queryset.py`, `apps/api/plane/utils/issue_filters.py`, `apps/api/plane/utils/filters/filter_backend.py`, `apps/api/plane/utils/filters/filterset.py`, `apps/api/plane/utils/global_paginator.py`
- Frontend: `apps/web/app/(all)/[workspaceSlug]/(projects)/projects/(detail)/[projectId]/issues/(list)/page.tsx`, `apps/web/components/issues/issue-layouts/roots/project-layout-root.tsx`, `apps/web/components/issues/header.tsx`, `apps/web/store/issue/helpers/base-issues.store.ts`, `apps/web/store/issue/project/filter.store.ts`, `packages/types/src/view-props.ts`, `packages/shared-state/src/store/rich-filters/filter.ts`, `packages/shared-state/src/store/rich-filters/config.ts`, `packages/shared-state/src/store/rich-filters/config-manager.ts`, `packages/shared-state/src/store/work-item-filters/filter.store.ts`, `packages/shared-state/src/store/work-item-filters/adapter.ts`, `packages/utils/src/rich-filters`, `packages/utils/src/work-item-filters/configs/filters`, `packages/constants/src/rich-filters/operator-labels/core.ts`, `apps/web/components/rich-filters/filters-row.tsx`, `apps/web/components/rich-filters/filters-toggle.tsx`, `apps/web/components/rich-filters/add-filters/button.tsx`, `apps/web/components/rich-filters/add-filters/dropdown.tsx`, `apps/web/components/rich-filters/filter-item/root.tsx`, `apps/web/components/rich-filters/filter-value-input/root.tsx`, `apps/web/components/rich-filters/filter-value-input/select/multi.tsx`, `apps/web/components/rich-filters/filter-value-input/select/single.tsx`, `apps/web/components/rich-filters/filter-value-input/select/selected-options-display.tsx`, `apps/web/components/rich-filters/filter-value-input/date/single.tsx`, `apps/web/components/rich-filters/filter-value-input/date/range.tsx`, `apps/web/components/rich-filters/filter-item/invalid.tsx`, `apps/web/hooks/work-item-filters/use-work-item-filters-config.tsx`, `packages/utils/src/work-item-filters/configs/filters/priority.ts`, `apps/web/hooks/rich-filters/use-filters-operator-configs.ts`

**Endpunkte (Katalog 04, `architecture/_data/endpoints.json`; 1 registriert)**

| EP | Methode | Pfad | Oberfläche | Handler | Permission | Inkr. 04 | CE-IDs |
|---|---|---|---|---|---|---|---|
| EP-0260 | GET | `/api/workspaces/{slug}/projects/{project_id}/issues/` | App | WorkItemEndpoints.ListWorkItemsQuery | project.work_item.read | I2 | CE-LV-005, CE-LV-006, CE-LV-010 |

**Akzeptanzkriterien**

1. Lasttests LT-01…LT-03 mit Volumenprofil L im Zielbereich von S9.
2. Contract: je Endpunkt dieses Pakets ≥ 1 Szenario mit Golden vom Original (Erfolg, Berechtigungsfehler, Validierungsfehler); Replay grün (L5).
3. Permission-Matrix (05 Anhang B) für alle Endpunkte dieses Pakets als L3-Test grün; Tenant-Isolation geprüft.
4. Signal-Stores strukturgleich zum MobX-Original (`store-parity-check`), Vitest je Action (L2).
5. E2E-Specs dieses Pakets grün gegen Original **und** funk. (Dual-Target, Pflichtszenarien 15 §3.9.3).
6. Visual-/DOM-/a11y-Prüfpunkte der betroffenen Screens (09 §4.14, 15 §3.10.2) innerhalb der Schwellwerte 15 §3.10.3 (Chromium); i18n-Schlüssel nur aus den Original-Locales (de/en).
7. `ce-coverage-check --ids CE-LV-005,CE-LV-006,CE-LV-007,CE-LV-008,CE-LV-009,CE-LV-010` grün (Mindestebenen 15 Anhang B).

**Testumfang**

- Pflicht-Ebenen (aus 15 Anhang B): L1, L2, L3, L5, L7, L8, L9
- Testprojekte: `Funk.WorkItems.Tests`, `Frontend-only`
- E2E-Specs (`frontend/apps/e2e/`): `web/layouts/filters.spec.ts`

### WP-I2-013 – Klassische Filter, Applied-Filter-Chips, Display-Dropdown, Anzeige-Einstellungen je Nutzer/Projekt und Workspace

| Merkmal | Wert |
|---|---|
| Inkrement | I2 |
| Typ (DoD 15 §3.15.3) | V – Vertikaler Schnitt |
| Größe | M |
| parallelisierbar | ja |
| Abhängigkeiten | WP-I2-012 |
| CE-IDs | CE-LV-012, CE-LV-013, CE-LV-014, CE-LV-015 |

**Ziel.** Klassische Filter-Sektionen mit Chips, Display-Dropdown, Anzeige-Einstellungen je Nutzer und Projekt sowie workspace-weit.

**Enthaltene CE-IDs**

| CE-ID | Feature | Status (15 Anh. B) | Inkrement laut 15 | Pflicht-Ebenen | Testprojekt | E2E-Spec |
|---|---|---|---|---|---|---|
| CE-LV-012 | Klassische Filter-Sektionen und Applied-Filter-Chips | übernommen | I2 | L2 L7 L8 | Frontend-only | `web/layouts/filters.spec.ts` |
| CE-LV-013 | Display-Dropdown | übernommen | I2 | L2 L7 L8 | Frontend-only | `web/layouts/filters.spec.ts` |
| CE-LV-014 | Anzeige-Einstellungen je Nutzer und Projekt | übernommen | I2 | L1 L2 L3 L5 L7 L8 | Funk.WorkItems.Tests | `web/layouts/display.spec.ts` |
| CE-LV-015 | Workspace-weite Filter- und Anzeigeeinstellungen | übernommen | I2 | L1 L2 L3 L5 L7 L8 | Funk.WorkItems.Tests | `web/layouts/display.spec.ts` |

**Betroffene Module/Libs in `funk.`**

- Backend: `src/modules/WorkItems/Funk.WorkItems` (Display-Properties)
- Frontend: `frontend/libs/web/work-items` (filters, display)

**Referenzdokumente**

- Architektur: 04 §4.5
- Architektur: 08 §3.4.6
- Analyse/Feature: `analysis/09-frontend-arbeitsobjekte-layouts.md` §2.10
- Analyse/Feature: `analysis/10a-frontend-workspace-projekt-navigation.md` §2.16
- Analyse/Feature: `analysis/13b-shared-packages-i18n.md` §3.3
- Analyse/Feature: `analysis/04-api-intern-arbeitsobjekte.md` §3.19
- Analyse/Feature: `analysis/02a-datenmodell-kern.md` §2.5
- Analyse/Feature: `analysis/03-api-intern-workspace-projekt-user.md` §2.5
- Feature-Katalog: `features/10-ce-feature-katalog.md` (Einträge CE-LV-012, CE-LV-013, CE-LV-014, CE-LV-015)

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- Backend: `apps/api/plane/app/views/issue/base.py`, `apps/api/plane/db/models/project.py`, `apps/api/plane/db/models/issue.py`, `apps/api/plane/app/views/workspace/user.py`, `apps/api/plane/db/models/workspace.py`
- Frontend: `apps/web/components/issues/issue-layouts/filters/header/filters/index.ts`, `apps/web/components/issues/issue-layouts/filters/applied-filters/index.ts`, `apps/web/components/issues/issue-layouts/filters/header/helpers/dropdown.tsx`, `apps/web/components/core/filters/date-filter-modal.tsx`, `apps/web/components/core/filters/date-filter-select.tsx`, `apps/web/components/issues/issue-layouts/filters/header/display-filters/display-filters-selection.tsx`, `apps/web/components/issues/issue-layouts/filters/header/display-filters/display-properties.tsx`, `apps/web/components/issues/issue-layouts/filters/header/display-filters/group-by.tsx`, `apps/web/components/issues/issue-layouts/filters/header/display-filters/sub-group-by.tsx`, `apps/web/components/issues/issue-layouts/filters/header/display-filters/order-by.tsx`, `apps/web/components/issues/issue-layouts/filters/header/display-filters/extra-options.tsx`, `packages/constants/src/issue/filter.ts`, `packages/constants/src/issue/common.ts`, `packages/utils/src/work-item/base.ts`, `packages/types/src/project/projects.ts`, `apps/web/services/workspace.service.ts`

**Endpunkte (Katalog 04, `architecture/_data/endpoints.json`; 4 registriert)**

| EP | Methode | Pfad | Oberfläche | Handler | Permission | Inkr. 04 | CE-IDs |
|---|---|---|---|---|---|---|---|
| EP-0148 | GET | `/api/workspaces/{slug}/user-properties/` | App | WorkspacePreferenceEndpoints.GetWorkspaceUserPropertiesQuery | workspace.member_preference.read | I3 | CE-LV-015 |
| EP-0149 | PATCH | `/api/workspaces/{slug}/user-properties/` | App | WorkspacePreferenceEndpoints.UpdateWorkspaceUserPropertiesCommand | workspace.member_preference.update | I3 | CE-LV-015 |
| EP-0213 | GET | `/api/workspaces/{slug}/projects/{project_id}/user-properties/` | App | ProjectPreferenceEndpoints.GetProjectUserPropertiesQuery | project.member_preference.read | I2 | CE-LV-014 |
| EP-0214 | PATCH | `/api/workspaces/{slug}/projects/{project_id}/user-properties/` | App | ProjectPreferenceEndpoints.UpdateProjectUserPropertiesCommand | project.member_preference.update | I2 | CE-LV-014 |

**Akzeptanzkriterien**

1. Contract: je Endpunkt dieses Pakets ≥ 1 Szenario mit Golden vom Original (Erfolg, Berechtigungsfehler, Validierungsfehler); Replay grün (L5).
2. Permission-Matrix (05 Anhang B) für alle Endpunkte dieses Pakets als L3-Test grün; Tenant-Isolation geprüft.
3. Signal-Stores strukturgleich zum MobX-Original (`store-parity-check`), Vitest je Action (L2).
4. E2E-Specs dieses Pakets grün gegen Original **und** funk. (Dual-Target, Pflichtszenarien 15 §3.9.3).
5. Visual-/DOM-/a11y-Prüfpunkte der betroffenen Screens (09 §4.14, 15 §3.10.2) innerhalb der Schwellwerte 15 §3.10.3 (Chromium); i18n-Schlüssel nur aus den Original-Locales (de/en).
6. `ce-coverage-check --ids CE-LV-012,CE-LV-013,CE-LV-014,CE-LV-015` grün (Mindestebenen 15 Anhang B).

**Testumfang**

- Pflicht-Ebenen (aus 15 Anhang B): L1, L2, L3, L5, L7, L8
- Testprojekte: `Frontend-only`, `Funk.WorkItems.Tests`
- E2E-Specs (`frontend/apps/e2e/`): `web/layouts/filters.spec.ts`, `web/layouts/display.spec.ts`

### WP-I2-014 – List-Layout mit Gruppierung, Inline-Properties, Sub-Work-Items aufklappen

| Merkmal | Wert |
|---|---|
| Inkrement | I2 |
| Typ (DoD 15 §3.15.3) | V – Vertikaler Schnitt |
| Größe | M |
| parallelisierbar | ja |
| Abhängigkeiten | WP-I2-011 |
| CE-IDs | CE-LV-017, CE-LV-018, CE-LV-019 |

**Ziel.** List-Layout inklusive Gruppen, Inline-Property-Zeilen und aufklappbarer Sub-Work-Items mit Virtualisierung (`*plRenderIfVisible`).

**Enthaltene CE-IDs**

| CE-ID | Feature | Status (15 Anh. B) | Inkrement laut 15 | Pflicht-Ebenen | Testprojekt | E2E-Spec |
|---|---|---|---|---|---|---|
| CE-LV-017 | List-Layout mit Gruppierung | übernommen | I2 | L2 L7 L8 | Frontend-only | `web/layouts/list.spec.ts` |
| CE-LV-018 | List-Zeile mit Inline-Properties | übernommen | I2 | L2 L7 L8 | Frontend-only | `web/layouts/list.spec.ts` |
| CE-LV-019 | Sub-Work-Items in der Liste aufklappen | übernommen | I2 | L2 L7 L8 | Frontend-only | `web/layouts/list.spec.ts` |

**Betroffene Module/Libs in `funk.`**

- Frontend: `frontend/libs/web/work-items` (issue-layouts/list)

**Referenzdokumente**

- Architektur: 08 §3.9, §5.11
- Analyse/Feature: `analysis/09-frontend-arbeitsobjekte-layouts.md` §2.2, §3.2
- Feature-Katalog: `features/10-ce-feature-katalog.md` (Einträge CE-LV-017, CE-LV-018, CE-LV-019)

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- Frontend: `apps/web/components/issues/issue-layouts/list/default.tsx`, `apps/web/components/issues/issue-layouts/list/list-group.tsx`, `apps/web/components/issues/issue-layouts/list/headers/group-by-card.tsx`, `apps/web/components/issues/issue-layouts/list/base-list-root.tsx`, `apps/web/components/issues/issue-layouts/list/block-root.tsx`, `apps/web/components/issues/issue-layouts/list/block.tsx`, `apps/web/components/issues/issue-layouts/list/blocks-list.tsx`

**Akzeptanzkriterien**

1. Contract: je Endpunkt dieses Pakets ≥ 1 Szenario mit Golden vom Original (Erfolg, Berechtigungsfehler, Validierungsfehler); Replay grün (L5).
2. Permission-Matrix (05 Anhang B) für alle Endpunkte dieses Pakets als L3-Test grün; Tenant-Isolation geprüft.
3. Signal-Stores strukturgleich zum MobX-Original (`store-parity-check`), Vitest je Action (L2).
4. E2E-Specs dieses Pakets grün gegen Original **und** funk. (Dual-Target, Pflichtszenarien 15 §3.9.3).
5. Visual-/DOM-/a11y-Prüfpunkte der betroffenen Screens (09 §4.14, 15 §3.10.2) innerhalb der Schwellwerte 15 §3.10.3 (Chromium); i18n-Schlüssel nur aus den Original-Locales (de/en).
6. `ce-coverage-check --ids CE-LV-017,CE-LV-018,CE-LV-019` grün (Mindestebenen 15 Anhang B).

**Testumfang**

- Pflicht-Ebenen (aus 15 Anhang B): L2, L7, L8
- Testprojekte: `Frontend-only`
- E2E-Specs (`frontend/apps/e2e/`): `web/layouts/list.spec.ts`

### WP-I2-015 – Kanban-Board, Swimlanes, Karte, Löschzone, Drag-and-Drop

| Merkmal | Wert |
|---|---|
| Inkrement | I2 |
| Typ (DoD 15 §3.15.3) | V – Vertikaler Schnitt |
| Größe | L |
| parallelisierbar | ja |
| Abhängigkeiten | WP-I2-011, WP-I0-904 |
| CE-IDs | CE-LV-020, CE-LV-021, CE-LV-022, CE-LV-023, CE-LV-024 |

**Ziel.** Kanban mit Swimlanes, Karte, Löschzone und DnD zwischen Gruppen inkl. `sort_order` wie Original.

**Enthaltene CE-IDs**

| CE-ID | Feature | Status (15 Anh. B) | Inkrement laut 15 | Pflicht-Ebenen | Testprojekt | E2E-Spec |
|---|---|---|---|---|---|---|
| CE-LV-020 | Kanban-Board | übernommen | I2 | L2 L7 L8 | Frontend-only | `web/layouts/kanban.spec.ts` |
| CE-LV-021 | Kanban-Swimlanes | übernommen | I2 | L2 L7 L8 | Frontend-only | `web/layouts/kanban.spec.ts` |
| CE-LV-022 | Kanban-Karte | übernommen | I2 | L2 L7 L8 | Frontend-only | `web/layouts/kanban.spec.ts` |
| CE-LV-023 | Kanban-Löschzone | übernommen | I2 | L2 L7 L8 | Frontend-only | `web/layouts/kanban.spec.ts` |
| CE-LV-024 | Drag-and-Drop zwischen Gruppen und Reihenfolge | übernommen | I2 | L2 L7 L8 L9 (LT-15) | Frontend-only | `web/layouts/kanban.spec.ts` |

**Betroffene Module/Libs in `funk.`**

- Frontend: `frontend/libs/web/work-items` (issue-layouts/kanban)
- Frontend: `frontend/libs/shared/dnd`

**Referenzdokumente**

- Architektur: 08 §3.9, §5.12
- Architektur: 01 §9 S4
- Analyse/Feature: `analysis/09-frontend-arbeitsobjekte-layouts.md` §2.3, §3.1
- Feature-Katalog: `features/10-ce-feature-katalog.md` (Einträge CE-LV-020, CE-LV-021, CE-LV-022, CE-LV-023, CE-LV-024)

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- Frontend: `apps/web/components/issues/issue-layouts/kanban/default.tsx`, `apps/web/components/issues/issue-layouts/kanban/kanban-group.tsx`, `apps/web/components/issues/issue-layouts/kanban/headers/group-by-card.tsx`, `apps/web/components/issues/issue-layouts/kanban/base-kanban-root.tsx`, `apps/web/components/issues/issue-layouts/kanban/swimlanes.tsx`, `apps/web/components/issues/issue-layouts/kanban/headers/sub-group-by-card.tsx`, `apps/web/components/issues/issue-layouts/kanban/block.tsx`, `apps/web/components/issues/issue-layouts/kanban/blocks-list.tsx`, `apps/web/components/issues/issue-layouts/kanban/kanban-delete-drop-zone.tsx`, `apps/web/components/issues/issue-layouts/utils.tsx`, `apps/web/hooks/use-group-dragndrop.ts`, `apps/web/components/issues/issue-layouts/group-drag-overlay.tsx`

**Akzeptanzkriterien**

1. LT-14 (Drag ≥ 55 fps mit 1 000 Karten) grün.
2. Contract: je Endpunkt dieses Pakets ≥ 1 Szenario mit Golden vom Original (Erfolg, Berechtigungsfehler, Validierungsfehler); Replay grün (L5).
3. Permission-Matrix (05 Anhang B) für alle Endpunkte dieses Pakets als L3-Test grün; Tenant-Isolation geprüft.
4. Signal-Stores strukturgleich zum MobX-Original (`store-parity-check`), Vitest je Action (L2).
5. E2E-Specs dieses Pakets grün gegen Original **und** funk. (Dual-Target, Pflichtszenarien 15 §3.9.3).
6. Visual-/DOM-/a11y-Prüfpunkte der betroffenen Screens (09 §4.14, 15 §3.10.2) innerhalb der Schwellwerte 15 §3.10.3 (Chromium); i18n-Schlüssel nur aus den Original-Locales (de/en).
7. `ce-coverage-check --ids CE-LV-020,CE-LV-021,CE-LV-022,CE-LV-023,CE-LV-024` grün (Mindestebenen 15 Anhang B).

**Testumfang**

- Pflicht-Ebenen (aus 15 Anhang B): L2, L7, L8, L9
- Testprojekte: `Frontend-only`
- E2E-Specs (`frontend/apps/e2e/`): `web/layouts/kanban.spec.ts`

### WP-I2-016 – Calendar-Layout (Monat/Woche, Drag, Eintrag, Quick-Add)

| Merkmal | Wert |
|---|---|
| Inkrement | I2 |
| Typ (DoD 15 §3.15.3) | V – Vertikaler Schnitt |
| Größe | M |
| parallelisierbar | ja |
| Abhängigkeiten | WP-I2-011 |
| CE-IDs | CE-LV-025, CE-LV-026, CE-LV-027, CE-LV-028 |

**Ziel.** Calendar-Layout mit Monats- und Wochenansicht, Drag auf anderen Tag, Eintrag und Quick-Add je Tag.

**Enthaltene CE-IDs**

| CE-ID | Feature | Status (15 Anh. B) | Inkrement laut 15 | Pflicht-Ebenen | Testprojekt | E2E-Spec |
|---|---|---|---|---|---|---|
| CE-LV-025 | Calendar-Layout Monat/Woche | übernommen | I2 | L2 L7 L8 | Frontend-only | `web/layouts/calendar.spec.ts` |
| CE-LV-026 | Calendar-Drag auf anderen Tag | übernommen | I2 | L2 L7 L8 | Frontend-only | `web/layouts/calendar.spec.ts` |
| CE-LV-027 | Calendar-Eintrag | übernommen | I2 | L2 L7 L8 | Frontend-only | `web/layouts/calendar.spec.ts` |
| CE-LV-028 | Calendar-Quick-Add je Tag | übernommen | I2 | L2 L7 L8 | Frontend-only | `web/layouts/calendar.spec.ts` |

**Betroffene Module/Libs in `funk.`**

- Frontend: `frontend/libs/web/work-items` (issue-layouts/calendar)

**Referenzdokumente**

- Architektur: 08 §3.9
- Analyse/Feature: `analysis/09-frontend-arbeitsobjekte-layouts.md` §2.4
- Analyse/Feature: `analysis/13b-shared-packages-i18n.md` §3.8
- Feature-Katalog: `features/10-ce-feature-katalog.md` (Einträge CE-LV-025, CE-LV-026, CE-LV-027, CE-LV-028)

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- Frontend: `apps/web/components/issues/issue-layouts/calendar/calendar.tsx`, `apps/web/components/issues/issue-layouts/calendar/header.tsx`, `apps/web/components/issues/issue-layouts/calendar/dropdowns/months-dropdown.tsx`, `apps/web/components/issues/issue-layouts/calendar/dropdowns/options-dropdown.tsx`, `apps/web/components/issues/issue-layouts/calendar/week-header.tsx`, `apps/web/components/issues/issue-layouts/calendar/week-days.tsx`, `apps/web/components/issues/issue-layouts/calendar/day-tile.tsx`, `packages/utils/src/calendar.ts`, `packages/constants/src/calendar.ts`, `packages/constants/src/profile.ts`, `apps/web/components/issues/issue-layouts/calendar/utils.ts`, `apps/web/components/issues/issue-layouts/calendar/issue-block-root.tsx`, `apps/web/components/issues/issue-layouts/calendar/issue-block.tsx`, `apps/web/components/issues/issue-layouts/calendar/issue-blocks.tsx`, `apps/web/components/issues/issue-layouts/calendar/quick-add-issue-actions.tsx`

**Akzeptanzkriterien**

1. Contract: je Endpunkt dieses Pakets ≥ 1 Szenario mit Golden vom Original (Erfolg, Berechtigungsfehler, Validierungsfehler); Replay grün (L5).
2. Permission-Matrix (05 Anhang B) für alle Endpunkte dieses Pakets als L3-Test grün; Tenant-Isolation geprüft.
3. Signal-Stores strukturgleich zum MobX-Original (`store-parity-check`), Vitest je Action (L2).
4. E2E-Specs dieses Pakets grün gegen Original **und** funk. (Dual-Target, Pflichtszenarien 15 §3.9.3).
5. Visual-/DOM-/a11y-Prüfpunkte der betroffenen Screens (09 §4.14, 15 §3.10.2) innerhalb der Schwellwerte 15 §3.10.3 (Chromium); i18n-Schlüssel nur aus den Original-Locales (de/en).
6. `ce-coverage-check --ids CE-LV-025,CE-LV-026,CE-LV-027,CE-LV-028` grün (Mindestebenen 15 Anhang B).

**Testumfang**

- Pflicht-Ebenen (aus 15 Anhang B): L2, L7, L8
- Testprojekte: `Frontend-only`
- E2E-Specs (`frontend/apps/e2e/`): `web/layouts/calendar.spec.ts`

### WP-I2-017 – Gantt/Timeline (Verschieben, Dauer, Datum setzen, Sidebar-Reorder, Relationen)

| Merkmal | Wert |
|---|---|
| Inkrement | I2 |
| Typ (DoD 15 §3.15.3) | V – Vertikaler Schnitt |
| Größe | L |
| parallelisierbar | ja |
| Abhängigkeiten | WP-I2-011, WP-I0-904, WP-I2-203 |
| CE-IDs | CE-LV-029, CE-LV-030, CE-LV-031, CE-LV-032, CE-LV-033 |

**Ziel.** Gantt-Ansicht mit Verschieben/Größe ändern, Datum für Items ohne Datum, Sidebar-Reorder und Timeline-Daten mit Relationen.

**Enthaltene CE-IDs**

| CE-ID | Feature | Status (15 Anh. B) | Inkrement laut 15 | Pflicht-Ebenen | Testprojekt | E2E-Spec |
|---|---|---|---|---|---|---|
| CE-LV-029 | Gantt/Timeline-Ansicht | übernommen | I2 | L2 L7 L8 | Frontend-only | `web/layouts/gantt.spec.ts` |
| CE-LV-030 | Gantt verschieben und Dauer ändern | übernommen | I2 | L2 L7 L8 | Frontend-only | `web/layouts/gantt.spec.ts` |
| CE-LV-031 | Gantt-Datum für Items ohne Datum setzen | übernommen | I2 | L2 L7 L8 | Frontend-only | `web/layouts/gantt.spec.ts` |
| CE-LV-032 | Gantt-Sidebar-Reorder | übernommen | I2 | L2 L7 L8 | Frontend-only | `web/layouts/gantt.spec.ts` |
| CE-LV-033 | Timeline-Daten mit Relationen (issues-detail) | übernommen | I2 | L1 L2 L3 L5 L7 L8 | Funk.WorkItems.Tests | `web/layouts/gantt.spec.ts` |

**Betroffene Module/Libs in `funk.`**

- Backend: `src/modules/WorkItems/Funk.WorkItems` (issues-detail)
- Frontend: `frontend/libs/web/work-items` (gantt-chart)

**Referenzdokumente**

- Architektur: 08 §3.9
- Architektur: 16 §5.3 (TIMELINE_FLAGS)
- Analyse/Feature: `analysis/09-frontend-arbeitsobjekte-layouts.md` §2.5
- Analyse/Feature: `analysis/08-frontend-web-architektur.md` §2.5
- Analyse/Feature: `analysis/04-api-intern-arbeitsobjekte.md` §2.8, §2.2
- Feature-Katalog: `features/10-ce-feature-katalog.md` (Einträge CE-LV-029, CE-LV-030, CE-LV-031, CE-LV-032, CE-LV-033)

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- Backend: `apps/api/plane/app/views/issue/base.py`, `apps/api/plane/app/serializers/issue.py`
- Frontend: `apps/web/components/gantt-chart/root.tsx`, `apps/web/components/gantt-chart/chart/root.tsx`, `apps/web/components/gantt-chart/chart/header.tsx`, `apps/web/components/gantt-chart/chart/main-content.tsx`, `apps/web/components/gantt-chart/chart/views/week.tsx`, `apps/web/components/gantt-chart/chart/views/month.tsx`, `apps/web/components/gantt-chart/chart/views/quarter.tsx`, `apps/web/components/gantt-chart/blocks/block-row.tsx`, `apps/web/store/timeline/base-timeline.store.ts`, `apps/web/store/timeline/timeline.store.ts`, `apps/web/hooks/use-timeline-chart.ts`, `apps/web/components/gantt-chart/helpers/draggable.tsx`, `apps/web/components/gantt-chart/helpers/blockResizables/left-resizable.tsx`, `apps/web/components/gantt-chart/helpers/blockResizables/right-resizable.tsx`, `apps/web/components/gantt-chart/helpers/blockResizables/use-gantt-resizable.ts`, `apps/web/components/issues/issue-layouts/gantt/base-gantt-root.tsx`, `apps/web/components/gantt-chart/helpers/add-block.tsx`, `apps/web/components/gantt-chart/sidebar/gantt-dnd-HOC.tsx`, `apps/web/components/gantt-chart/sidebar/utils.ts`, `apps/web/components/gantt-chart/sidebar/issues/sidebar.tsx`, `apps/web/components/gantt-chart/sidebar/issues/block.tsx`, `packages/constants/src/issue/filter.ts`

**Endpunkte (Katalog 04, `architecture/_data/endpoints.json`; 2 registriert)**

| EP | Methode | Pfad | Oberfläche | Handler | Permission | Inkr. 04 | CE-IDs |
|---|---|---|---|---|---|---|---|
| EP-0258 | POST | `/api/workspaces/{slug}/projects/{project_id}/issue-dates/` | App | WorkItemEndpoints.BulkUpdateWorkItemDatesCommand | project.work_item.update | I2 | CE-LV-030 |
| EP-0259 | GET | `/api/workspaces/{slug}/projects/{project_id}/issues-detail/` | App | WorkItemEndpoints.ListWorkItemDetailsQuery | project.work_item.read | I2 | CE-LV-033 |

**Akzeptanzkriterien**

1. LT-15 (Gantt-Interaktion) grün.
2. Contract: je Endpunkt dieses Pakets ≥ 1 Szenario mit Golden vom Original (Erfolg, Berechtigungsfehler, Validierungsfehler); Replay grün (L5).
3. Permission-Matrix (05 Anhang B) für alle Endpunkte dieses Pakets als L3-Test grün; Tenant-Isolation geprüft.
4. Signal-Stores strukturgleich zum MobX-Original (`store-parity-check`), Vitest je Action (L2).
5. E2E-Specs dieses Pakets grün gegen Original **und** funk. (Dual-Target, Pflichtszenarien 15 §3.9.3).
6. Visual-/DOM-/a11y-Prüfpunkte der betroffenen Screens (09 §4.14, 15 §3.10.2) innerhalb der Schwellwerte 15 §3.10.3 (Chromium); i18n-Schlüssel nur aus den Original-Locales (de/en).
7. `ce-coverage-check --ids CE-LV-029,CE-LV-030,CE-LV-031,CE-LV-032,CE-LV-033` grün (Mindestebenen 15 Anhang B).

**Testumfang**

- Pflicht-Ebenen (aus 15 Anhang B): L1, L2, L3, L5, L7, L8
- Testprojekte: `Frontend-only`, `Funk.WorkItems.Tests`
- E2E-Specs (`frontend/apps/e2e/`): `web/layouts/gantt.spec.ts`

### WP-I2-018 – Spreadsheet (Tabelle, Sortierung, Tastaturnavigation, Mehrfachauswahl, Sprung zu Sub-Items)

| Merkmal | Wert |
|---|---|
| Inkrement | I2 |
| Typ (DoD 15 §3.15.3) | V – Vertikaler Schnitt |
| Größe | L |
| parallelisierbar | ja |
| Abhängigkeiten | WP-I2-011 |
| CE-IDs | CE-LV-034, CE-LV-035, CE-LV-036, CE-LV-037 |

**Ziel.** Spreadsheet-Layout mit Spalten über `SPREADSHEET_COLUMNS`, Sortierung, Tastaturnavigation, Mehrfachauswahl und Sprung zu Sub-Work-Items.

**Enthaltene CE-IDs**

| CE-ID | Feature | Status (15 Anh. B) | Inkrement laut 15 | Pflicht-Ebenen | Testprojekt | E2E-Spec |
|---|---|---|---|---|---|---|
| CE-LV-034 | Spreadsheet-Tabelle | übernommen | I2 | L2 L7 L8 L9 (LT-03) | Frontend-only | `web/layouts/spreadsheet.spec.ts` |
| CE-LV-035 | Spreadsheet-Sortierung über den Spaltenkopf | übernommen | I2 | L2 L7 L8 | Frontend-only | `web/layouts/spreadsheet.spec.ts` |
| CE-LV-036 | Spreadsheet-Tastaturnavigation und Mehrfachauswahl | übernommen | I2 | L2 L7 L8 | Frontend-only | `web/layouts/spreadsheet.spec.ts` |
| CE-LV-037 | Sprung zu Sub-Work-Items aus dem Spreadsheet | übernommen | I2 | L2 L7 L8 | Frontend-only | `web/layouts/spreadsheet.spec.ts` |

**Betroffene Module/Libs in `funk.`**

- Frontend: `frontend/libs/web/work-items` (issue-layouts/spreadsheet)

**Referenzdokumente**

- Architektur: 08 §3.9
- Architektur: 16 §1.4 Zeile I2
- Analyse/Feature: `analysis/09-frontend-arbeitsobjekte-layouts.md` §2.6
- Analyse/Feature: `analysis/13b-shared-packages-i18n.md` §3.3
- Analyse/Feature: `analysis/08-frontend-web-architektur.md` §2.8
- Feature-Katalog: `features/10-ce-feature-katalog.md` (Einträge CE-LV-034, CE-LV-035, CE-LV-036, CE-LV-037)

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- Frontend: `apps/web/components/issues/issue-layouts/spreadsheet/spreadsheet-view.tsx`, `apps/web/components/issues/issue-layouts/spreadsheet/spreadsheet-table.tsx`, `apps/web/components/issues/issue-layouts/spreadsheet/issue-row.tsx`, `apps/web/components/issues/issue-layouts/spreadsheet/issue-column.tsx`, `apps/web/components/issues/issue-layouts/spreadsheet/columns/index.ts`, `packages/constants/src/issue/common.ts`, `apps/web/components/issues/issue-layouts/spreadsheet/columns/header-column.tsx`, `apps/web/components/issues/issue-layouts/spreadsheet/spreadsheet-header-column.tsx`, `apps/web/components/issues/issue-layouts/spreadsheet/spreadsheet-header.tsx`, `apps/web/hooks/use-table-keyboard-navigation.tsx`, `apps/web/store/multiple_select.store.ts`, `apps/web/hooks/use-multiple-select.ts`, `apps/web/components/issues/issue-layouts/spreadsheet/columns/sub-issue-column.tsx`

**Akzeptanzkriterien**

1. Contract: je Endpunkt dieses Pakets ≥ 1 Szenario mit Golden vom Original (Erfolg, Berechtigungsfehler, Validierungsfehler); Replay grün (L5).
2. Permission-Matrix (05 Anhang B) für alle Endpunkte dieses Pakets als L3-Test grün; Tenant-Isolation geprüft.
3. Signal-Stores strukturgleich zum MobX-Original (`store-parity-check`), Vitest je Action (L2).
4. E2E-Specs dieses Pakets grün gegen Original **und** funk. (Dual-Target, Pflichtszenarien 15 §3.9.3).
5. Visual-/DOM-/a11y-Prüfpunkte der betroffenen Screens (09 §4.14, 15 §3.10.2) innerhalb der Schwellwerte 15 §3.10.3 (Chromium); i18n-Schlüssel nur aus den Original-Locales (de/en).
6. `ce-coverage-check --ids CE-LV-034,CE-LV-035,CE-LV-036,CE-LV-037` grün (Mindestebenen 15 Anhang B).

**Testumfang**

- Pflicht-Ebenen (aus 15 Anhang B): L2, L7, L8, L9
- Testprojekte: `Frontend-only`
- E2E-Specs (`frontend/apps/e2e/`): `web/layouts/spreadsheet.spec.ts`

### WP-I2-019 – Inline-Property-Leiste, Quick-Add je Layout, Gruppen-„+“, Quick-Action- und Kontextmenü

| Merkmal | Wert |
|---|---|
| Inkrement | I2 |
| Typ (DoD 15 §3.15.3) | V – Vertikaler Schnitt |
| Größe | M |
| parallelisierbar | ja |
| Abhängigkeiten | WP-I2-014 |
| CE-IDs | CE-LV-038, CE-LV-039, CE-LV-040, CE-LV-041 |

**Ziel.** Inline-Property-Leiste, Quick-Add in allen Layouts, Gruppen-„+“ mit „Create work item“/„Add an existing work item“, Quick-Action-Menü und Rechtsklick-Kontextmenü (über `WORK_ITEM_ACTIONS`).

**Enthaltene CE-IDs**

| CE-ID | Feature | Status (15 Anh. B) | Inkrement laut 15 | Pflicht-Ebenen | Testprojekt | E2E-Spec |
|---|---|---|---|---|---|---|
| CE-LV-038 | Inline-Property-Leiste | übernommen | I2 | L2 L7 L8 | Frontend-only | `web/layouts/quick-actions.spec.ts` |
| CE-LV-039 | Quick-Add je Layout | übernommen | I2 | L2 L7 L8 | Frontend-only | `web/layouts/quick-actions.spec.ts` |
| CE-LV-040 | Gruppen-'+' mit 'Create work item' / 'Add an existing work item' | übernommen | I2 | L2 L7 L8 | Frontend-only | `web/layouts/quick-actions.spec.ts` |
| CE-LV-041 | Quick-Action-Menü und Rechtsklick-Kontextmenü | übernommen | I2 | L2 L7 L8 | Frontend-only | `web/layouts/quick-actions.spec.ts` |

**Betroffene Module/Libs in `funk.`**

- Frontend: `frontend/libs/web/work-items` (quick-add, quick-action-dropdowns)

**Referenzdokumente**

- Architektur: 08 §6.4
- Architektur: 16 §1.4 Zeile I2
- Analyse/Feature: `analysis/09-frontend-arbeitsobjekte-layouts.md` §2.1, §2.7, §2.2, §2.8
- Analyse/Feature: `analysis/13b-shared-packages-i18n.md` §3.3
- Feature-Katalog: `features/10-ce-feature-katalog.md` (Einträge CE-LV-038, CE-LV-039, CE-LV-040, CE-LV-041)

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- Frontend: `apps/web/components/issues/issue-layouts/properties/all-properties.tsx`, `apps/web/components/issues/issue-layouts/properties/labels.tsx`, `apps/web/components/issues/issue-layouts/properties/with-display-properties-HOC.tsx`, `packages/constants/src/issue/common.ts`, `packages/utils/src/work-item/base.ts`, `apps/web/components/issues/issue-layouts/quick-add/root.tsx`, `apps/web/components/issues/issue-layouts/quick-add/form/root.tsx`, `apps/web/components/issues/issue-layouts/quick-add/form/list.tsx`, `apps/web/components/issues/issue-layouts/quick-add/form/kanban.tsx`, `apps/web/components/issues/issue-layouts/quick-add/form/calendar.tsx`, `apps/web/components/issues/issue-layouts/quick-add/form/gantt.tsx`, `apps/web/components/issues/issue-layouts/quick-add/form/spreadsheet.tsx`, `apps/web/components/issues/issue-layouts/quick-add/button/list.tsx`, `apps/web/components/issues/issue-layouts/quick-add/button/kanban.tsx`, `apps/web/components/issues/issue-layouts/quick-add/button/gantt.tsx`, `apps/web/components/issues/issue-layouts/quick-add/button/spreadsheet.tsx`, `apps/web/components/issues/issue-layouts/list/headers/group-by-card.tsx`, `apps/web/components/issues/issue-layouts/kanban/headers/group-by-card.tsx`, `apps/web/components/core/modals/existing-issues-list-modal.tsx`, `apps/web/components/issues/issue-layouts/quick-action-dropdowns/helper.tsx`, `apps/web/components/issues/issue-layouts/quick-action-dropdowns/project-issue.tsx`, `apps/web/components/issues/issue-layouts/quick-action-dropdowns/cycle-issue.tsx`, `apps/web/components/issues/issue-layouts/quick-action-dropdowns/module-issue.tsx`, `apps/web/components/issues/issue-layouts/quick-action-dropdowns/all-issue.tsx`, `apps/web/components/issues/issue-layouts/quick-action-dropdowns/archived-issue.tsx`, `apps/web/components/issues/issue-layouts/quick-action-dropdowns/issue-detail.tsx`

**Akzeptanzkriterien**

1. Contract: je Endpunkt dieses Pakets ≥ 1 Szenario mit Golden vom Original (Erfolg, Berechtigungsfehler, Validierungsfehler); Replay grün (L5).
2. Permission-Matrix (05 Anhang B) für alle Endpunkte dieses Pakets als L3-Test grün; Tenant-Isolation geprüft.
3. Signal-Stores strukturgleich zum MobX-Original (`store-parity-check`), Vitest je Action (L2).
4. E2E-Specs dieses Pakets grün gegen Original **und** funk. (Dual-Target, Pflichtszenarien 15 §3.9.3).
5. Visual-/DOM-/a11y-Prüfpunkte der betroffenen Screens (09 §4.14, 15 §3.10.2) innerhalb der Schwellwerte 15 §3.10.3 (Chromium); i18n-Schlüssel nur aus den Original-Locales (de/en).
6. `ce-coverage-check --ids CE-LV-038,CE-LV-039,CE-LV-040,CE-LV-041` grün (Mindestebenen 15 Anhang B).

**Testumfang**

- Pflicht-Ebenen (aus 15 Anhang B): L2, L7, L8
- Testprojekte: `Frontend-only`
- E2E-Specs (`frontend/apps/e2e/`): `web/layouts/quick-actions.spec.ts`

### WP-I2-020 – Layout-Zustände: Empty-States, Skeleton-Loader, Virtualisierung/Endlos-Laden, Fehlergrenze

| Merkmal | Wert |
|---|---|
| Inkrement | I2 |
| Typ (DoD 15 §3.15.3) | V – Vertikaler Schnitt |
| Größe | M |
| parallelisierbar | ja |
| Abhängigkeiten | WP-I2-014 |
| CE-IDs | CE-LV-042, CE-LV-043, CE-LV-044, CE-LV-045 |

**Ziel.** Empty-States, Skeleton-Loader je Layout, Virtualisierung mit Sentinel-Pagination und Layout-Fehlergrenze.

**Enthaltene CE-IDs**

| CE-ID | Feature | Status (15 Anh. B) | Inkrement laut 15 | Pflicht-Ebenen | Testprojekt | E2E-Spec |
|---|---|---|---|---|---|---|
| CE-LV-042 | Empty-States der Layouts | übernommen | I2 | L2 L7 L8 | Frontend-only | `web/layouts/layout-states.spec.ts` |
| CE-LV-043 | Skeleton-Loader je Layout | übernommen | I2 | L2 L7 L8 | Frontend-only | `web/layouts/layout-states.spec.ts` |
| CE-LV-044 | Virtualisierung und Endlos-Laden | übernommen | I2 | L2 L7 L8 L9 (LT-14) | Frontend-only | `web/layouts/layout-states.spec.ts` |
| CE-LV-045 | Layout-Fehlergrenze | übernommen | I2 | L2 L7 L8 | Frontend-only | `web/layouts/layout-states.spec.ts` |

**Betroffene Module/Libs in `funk.`**

- Frontend: `frontend/libs/web/work-items` (issue-layouts)

**Referenzdokumente**

- Architektur: 08 §3.9, §3.13
- Analyse/Feature: `analysis/09-frontend-arbeitsobjekte-layouts.md` §2.9, §2.22, §2.1
- Feature-Katalog: `features/10-ce-feature-katalog.md` (Einträge CE-LV-042, CE-LV-043, CE-LV-044, CE-LV-045)

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- Frontend: `apps/web/components/issues/issue-layouts/empty-states/index.tsx`, `apps/web/components/issues/issue-layouts/empty-states/project-issues.tsx`, `apps/web/components/issues/issue-layouts/empty-states/project-view.tsx`, `apps/web/components/issues/issue-layouts/empty-states/archived-issues.tsx`, `apps/web/components/issues/issue-layouts/empty-states/cycle.tsx`, `apps/web/components/issues/issue-layouts/empty-states/module.tsx`, `apps/web/components/issues/issue-layouts/empty-states/global-view.tsx`, `apps/web/components/issues/issue-layouts/empty-states/profile-view.tsx`, `apps/web/components/ui/loader/layouts/list-layout-loader.tsx`, `apps/web/components/ui/loader/layouts/kanban-layout-loader.tsx`, `apps/web/components/ui/loader/layouts/spreadsheet-layout-loader.tsx`, `apps/web/components/ui/loader/layouts/calendar-layout-loader.tsx`, `apps/web/components/ui/loader/layouts/gantt-layout-loader.tsx`, `apps/web/components/issues/issue-layouts/issue-layout-HOC.tsx`, `apps/web/components/issues/issue-layouts/roots/project-layout-root.tsx`, `apps/web/components/core/render-if-visible-HOC.tsx`, `apps/web/hooks/use-intersection-observer.ts`, `apps/web/components/issues/issue-layouts/list/block-root.tsx`, `apps/web/components/common/layout-error-boundary.tsx`

**Akzeptanzkriterien**

1. Contract: je Endpunkt dieses Pakets ≥ 1 Szenario mit Golden vom Original (Erfolg, Berechtigungsfehler, Validierungsfehler); Replay grün (L5).
2. Permission-Matrix (05 Anhang B) für alle Endpunkte dieses Pakets als L3-Test grün; Tenant-Isolation geprüft.
3. Signal-Stores strukturgleich zum MobX-Original (`store-parity-check`), Vitest je Action (L2).
4. E2E-Specs dieses Pakets grün gegen Original **und** funk. (Dual-Target, Pflichtszenarien 15 §3.9.3).
5. Visual-/DOM-/a11y-Prüfpunkte der betroffenen Screens (09 §4.14, 15 §3.10.2) innerhalb der Schwellwerte 15 §3.10.3 (Chromium); i18n-Schlüssel nur aus den Original-Locales (de/en).
6. `ce-coverage-check --ids CE-LV-042,CE-LV-043,CE-LV-044,CE-LV-045` grün (Mindestebenen 15 Anhang B).

**Testumfang**

- Pflicht-Ebenen (aus 15 Anhang B): L2, L7, L8, L9
- Testprojekte: `Frontend-only`
- E2E-Specs (`frontend/apps/e2e/`): `web/layouts/layout-states.spec.ts`

### WP-I2-021 – Editor ED-1: Lite-Text-Editor (Kommentare), Mentions, Emojis, Links

| Merkmal | Wert |
|---|---|
| Inkrement | I2 |
| Typ (DoD 15 §3.15.3) | D – Editor/Dokumente |
| Größe | M |
| parallelisierbar | nein |
| Abhängigkeiten | WP-I1-103, WP-I0-905, WP-I2-101, WP-I2-207 |
| CE-IDs | CE-PAGE-022, CE-PAGE-034, CE-PAGE-035, CE-PAGE-036 |

**Ziel.** `PlEdLiteTextEditor` mit Enter-Key-Verhalten, Mentions, Emoji-Suggestion (offline), Links, Bild-Upload und Lite-Toolbars der Web-Hülle; Read-only-Anzeige von Kommentaren.

**Enthaltene CE-IDs**

| CE-ID | Feature | Status (15 Anh. B) | Inkrement laut 15 | Pflicht-Ebenen | Testprojekt | E2E-Spec |
|---|---|---|---|---|---|---|
| CE-PAGE-022 | Lite-Text-Editor | übernommen | I2/I4 | L2 L4 L7 L8 (G-DOC/G-SCHEMA) | Frontend-only | `web/editor/editor-variants.spec.ts` |
| CE-PAGE-034 | Nutzer-Mentions im Editor | übernommen | I2/I4 | L2 L4 L7 L8 (G-DOC/G-SCHEMA) | Frontend-only | `web/editor/editor-inline.spec.ts` |
| CE-PAGE-035 | Emojis | übernommen | I2/I4 | L2 L4 L7 L8 (G-DOC/G-SCHEMA) | Frontend-only | `web/editor/editor-inline.spec.ts` |
| CE-PAGE-036 | Links im Editor | übernommen | I2/I4 | L2 L4 L7 L8 (G-DOC/G-SCHEMA) | Frontend-only | `web/editor/editor-inline.spec.ts` |

**Betroffene Module/Libs in `funk.`**

- Frontend: `frontend/libs/shared/editor/{core,angular-binding,components}`
- Frontend: `frontend/libs/web/core/editor` (Hüllen)

**Referenzdokumente**

- Architektur: 10 §1.5 (ED-1), §3.6, §3.11, §3.12, §3.17, §3.21
- Analyse/Feature: `analysis/12-editor-echtzeit-live.md` §2.5, §2.18, §2.15
- Analyse/Feature: `analysis/10b-frontend-cycles-modules-pages-views-weitere.md` §2.17
- Analyse/Feature: `analysis/03-api-intern-workspace-projekt-user.md` §3.14
- Feature-Katalog: `features/10-ce-feature-katalog.md` (Einträge CE-PAGE-022, CE-PAGE-034, CE-PAGE-035, CE-PAGE-036)

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- Backend: `apps/api/plane/app/views/search/base.py`
- Frontend: `packages/editor/src/components/editors/lite-text/editor.tsx`, `packages/editor/src/extensions/enter-key.ts`, `apps/web/components/editor/lite-text/editor.tsx`, `apps/web/components/editor/sticky-editor/editor.tsx`, `packages/editor/src/extensions/mentions/extension.tsx`, `packages/editor/src/extensions/mentions/mentions-list-dropdown.tsx`, `packages/editor/src/extensions/mentions/utils.ts`, `apps/web/hooks/editor/use-editor-mention.tsx`, `apps/web/components/editor/embeds/mentions/user.tsx`, `apps/web/components/editor/embeds/mentions/root.tsx`, `apps/web/services/workspace.service.ts`, `packages/editor/src/extensions/emoji/emoji.ts`, `packages/editor/src/extensions/emoji/extension.ts`, `packages/editor/src/extensions/emoji/suggestion.ts`, `packages/editor/src/extensions/emoji/components/emojis-list.tsx`, `packages/editor/src/extensions/custom-link/extension.tsx`, `packages/editor/src/extensions/custom-link/helpers/autolink.ts`, `packages/editor/src/components/editors/link-view-container.tsx`, `packages/editor/src/components/links/link-preview.tsx`, `packages/editor/src/components/links/link-edit-view.tsx`

**Akzeptanzkriterien**

1. AK-D10-01, -05, -08, -12 grün; Visual Kommentar-Editor ≤ 0,5 %.
2. G-SCHEMA unverändert (Schema-Freeze) oder genehmigte Änderung; G-DOC-Fälle für jeden betroffenen Node/Mark.
3. Browser-Roundtrip-Test (Playwright) für Yjs, sofern Kollaboration betroffen; Visual-Prüfpunkte des Editors.
4. `ce-coverage-check --ids CE-PAGE-022,CE-PAGE-034,CE-PAGE-035,CE-PAGE-036` grün (Mindestebenen 15 Anhang B).

**Testumfang**

- Pflicht-Ebenen (aus 15 Anhang B): L2, L4, L7, L8
- Testprojekte: `Frontend-only`
- E2E-Specs (`frontend/apps/e2e/`): `web/editor/editor-variants.spec.ts`, `web/editor/editor-inline.spec.ts`

### WP-I2-022 – Editor ED-2a: Rich-Text-Kern (Textstruktur, Listen, Formatierung/Farben, Markdown, Platzhalter, Deep-Links, Anzeige-Konfiguration)

| Merkmal | Wert |
|---|---|
| Inkrement | I2 |
| Typ (DoD 15 §3.15.3) | D – Editor/Dokumente |
| Größe | L |
| parallelisierbar | nein |
| Abhängigkeiten | WP-I2-021 |
| CE-IDs | CE-PAGE-021, CE-PAGE-027, CE-PAGE-028, CE-PAGE-029, CE-PAGE-037, CE-PAGE-038, CE-PAGE-039, CE-PAGE-040, CE-I18N-010 |

**Ziel.** `PlEdRichTextEditor` mit vollständigem Kern, Markdown-Funktionen, Clipboard/Paste, Platzhaltern, Deep-Links zu Blöcken, Anzeige-Konfiguration und Editor-Farbpalette; `value`-Sync und `isMigrationUpdate`.

> **Hinweis:** Verfeinerung von 10 §1.5: ED-2 wird in ED-2a (Kern) und ED-2b (Menüs/Blöcke) geteilt, damit jedes Paket ≤ L bleibt.

**Enthaltene CE-IDs**

| CE-ID | Feature | Status (15 Anh. B) | Inkrement laut 15 | Pflicht-Ebenen | Testprojekt | E2E-Spec |
|---|---|---|---|---|---|---|
| CE-PAGE-021 | Rich-Text-Editor | übernommen | I2/I4 | L2 L4 L7 L8 L9 (G-DOC/G-SCHEMA; LT-16) | Frontend-only | `web/editor/editor-variants.spec.ts` |
| CE-PAGE-027 | Textstruktur | übernommen | I4 | L2 L4 L7 L8 (G-DOC/G-SCHEMA) | Frontend-only | `web/editor/editor-blocks.spec.ts` |
| CE-PAGE-028 | Listen (Aufzählung, Nummerierung, To-do) | übernommen | I4 | L2 L4 L7 L8 (G-DOC/G-SCHEMA) | Frontend-only | `web/editor/editor-blocks.spec.ts` |
| CE-PAGE-029 | Text-Formatierung und Farben | übernommen | I4 | L2 L4 L7 L8 (G-DOC/G-SCHEMA) | Frontend-only | `web/editor/editor-blocks.spec.ts` |
| CE-PAGE-037 | Markdown-Funktionen | übernommen | I2/I4 | L2 L4 L7 L8 (G-DOC/G-SCHEMA) | Frontend-only | `web/editor/editor-inline.spec.ts` |
| CE-PAGE-038 | Platzhalter | übernommen | I2/I4 | L2 L4 L7 L8 (G-DOC/G-SCHEMA) | Frontend-only | `web/editor/editor-inline.spec.ts` |
| CE-PAGE-039 | Deep-Links zu Blöcken | übernommen | I4 | L2 L4 L7 L8 (G-DOC) | Frontend-only | `web/editor/editor-config.spec.ts` |
| CE-PAGE-040 | Anzeige-Konfiguration des Editors | übernommen | I4 | L2 L4 L7 L8 (G-DOC) | Frontend-only | `web/editor/editor-config.spec.ts` |
| CE-I18N-010 | Editor-Farbpalette | übernommen | I1 | L2 L7 L8 | Frontend-only | `web/i18n/themes.spec.ts` |

**Betroffene Module/Libs in `funk.`**

- Frontend: `frontend/libs/shared/editor`
- Frontend: `frontend/libs/shared/editor/styles` (CSS 1:1)

**Referenzdokumente**

- Architektur: 10 §1.5 (ED-2, Teil Kern), §3.6–§3.8, §3.16, §3.19, §3.20, §3.22
- Analyse/Feature: `analysis/12-editor-echtzeit-live.md` §3.1, §2.5, §3.16, §2.6, §3.21, §3.22, §2.24
- Analyse/Feature: `analysis/13b-shared-packages-i18n.md` §2.4, §2.5
- Analyse/Feature: `analysis/13a-designsystem-ui-tokens.md` §2.19
- Feature-Katalog: `features/10-ce-feature-katalog.md` (Einträge CE-PAGE-021, CE-PAGE-027, CE-PAGE-028, CE-PAGE-029, CE-PAGE-037, CE-PAGE-038, CE-PAGE-039, CE-PAGE-040, CE-I18N-010)

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- Frontend: `packages/editor/src/components/editors/rich-text/editor.tsx`, `packages/editor/src/components/editors/editor-wrapper.tsx`, `packages/editor/src/hooks/use-editor.ts`, `apps/web/components/editor/rich-text/editor.tsx`, `apps/space/components/editor/rich-text-editor.tsx`, `packages/editor/src/extensions/starter-kit.ts`, `packages/editor/src/extensions/text-align.ts`, `packages/editor/src/extensions/quote.ts`, `packages/editor/src/extensions/horizontal-rule.ts`, `packages/editor/src/extensions/custom-list-keymap/list-keymap.ts`, `packages/editor/src/extensions/custom-list-keymap/list-helpers.ts`, `packages/editor/src/extensions/keymap.ts`, `packages/editor/src/extensions/extensions.ts`, `packages/editor/src/styles/editor.css`, `packages/editor/src/extensions/custom-color.ts`, `packages/editor/src/extensions/code-inline/index.tsx`, `packages/editor/src/extensions/typography/inputRules.ts`, `packages/editor/src/constants/common.ts`, `packages/editor/src/styles/variables.css`, `packages/editor/src/plugins/markdown-clipboard.ts`, `packages/editor/src/helpers/editor-ref.ts`, `packages/utils/src/editor/markdown-parser/root.ts`, `apps/web/components/pages/modals/export-page-modal.tsx`, `packages/utils/src/editor/markdown-parser/custom-components-handler.ts`, `packages/utils/src/editor/markdown-parser/marks-handler.ts`, `packages/editor/src/extensions/placeholder.ts`, `packages/editor/src/hooks/use-title-editor.ts`, `packages/editor/src/extensions/headings-list.ts`, `packages/editor/src/helpers/scroll-to-node.ts`, `packages/editor/src/components/editors/editor-container.tsx`, `packages/hooks/src/use-hash-scroll.ts`, `packages/editor/src/constants/config.ts`, `packages/editor/src/styles/title-editor.css`, `apps/web/styles/globals.css`, `apps/space/styles/globals.css`

**Akzeptanzkriterien**

1. AK-D10-01…-04 grün; G-SCHEMA (rich) unverändert.
2. G-SCHEMA unverändert (Schema-Freeze) oder genehmigte Änderung; G-DOC-Fälle für jeden betroffenen Node/Mark.
3. Browser-Roundtrip-Test (Playwright) für Yjs, sofern Kollaboration betroffen; Visual-Prüfpunkte des Editors.
4. `ce-coverage-check --ids CE-PAGE-021,CE-PAGE-027,CE-PAGE-028,CE-PAGE-029,CE-PAGE-037,CE-PAGE-038,CE-PAGE-039,CE-PAGE-040,CE-I18N-010` grün (Mindestebenen 15 Anhang B).

**Testumfang**

- Pflicht-Ebenen (aus 15 Anhang B): L2, L4, L7, L8, L9
- Testprojekte: `Frontend-only`
- E2E-Specs (`frontend/apps/e2e/`): `web/editor/editor-variants.spec.ts`, `web/editor/editor-blocks.spec.ts`, `web/editor/editor-inline.spec.ts`, `web/editor/editor-config.spec.ts`, `web/i18n/themes.spec.ts`

### WP-I2-023 – Editor ED-2b: Menüs und Blöcke (Slash, Bubble, Drag-Handle/Block-Menü, Code-Block, Tabellen, Bilder, Callouts)

| Merkmal | Wert |
|---|---|
| Inkrement | I2 |
| Typ (DoD 15 §3.15.3) | D – Editor/Dokumente |
| Größe | L |
| parallelisierbar | nein |
| Abhängigkeiten | WP-I2-022 |
| CE-IDs | CE-PAGE-024, CE-PAGE-025, CE-PAGE-026, CE-PAGE-030, CE-PAGE-031, CE-PAGE-032, CE-PAGE-033 |

**Ziel.** Slash-Command-Menü, Bubble-Menü, Side-Menü mit Drag-Handle und Block-Menü, Code-Block mit Syntax-Highlighting, Tabellen inkl. Handles, Bilder mit Upload-UI, Callouts mit Emoji-/Icon-Logo.

**Enthaltene CE-IDs**

| CE-ID | Feature | Status (15 Anh. B) | Inkrement laut 15 | Pflicht-Ebenen | Testprojekt | E2E-Spec |
|---|---|---|---|---|---|---|
| CE-PAGE-024 | Slash-Command-Menü | übernommen | I4 | L2 L4 L7 L8 (G-DOC/G-SCHEMA) | Frontend-only | `web/editor/editor-menus.spec.ts` |
| CE-PAGE-025 | Bubble-Menü | übernommen | I4 | L2 L4 L7 L8 (G-DOC) | Frontend-only | `web/editor/editor-menus.spec.ts` |
| CE-PAGE-026 | Drag-Handle, Block-Menü und Block-Drag&Drop | übernommen | I4 | L2 L4 L7 L8 (G-DOC) | Frontend-only | `web/editor/editor-menus.spec.ts` |
| CE-PAGE-030 | Code-Block mit Syntax-Highlighting | übernommen | I4 | L2 L4 L7 L8 (G-DOC/G-SCHEMA) | Frontend-only | `web/editor/editor-blocks.spec.ts` |
| CE-PAGE-031 | Tabellen | übernommen | I4 | L2 L4 L7 L8 (G-DOC/G-SCHEMA) | Frontend-only | `web/editor/editor-blocks.spec.ts` |
| CE-PAGE-032 | Bilder im Editor | übernommen | I4 | L2 L4 L7 L8 (G-DOC/G-SCHEMA) | Frontend-only | `web/editor/editor-blocks.spec.ts` |
| CE-PAGE-033 | Callouts | übernommen | I4 | L2 L4 L7 L8 (G-DOC/G-SCHEMA) | Frontend-only | `web/editor/editor-blocks.spec.ts` |

**Betroffene Module/Libs in `funk.`**

- Frontend: `frontend/libs/shared/editor/components` (Menüs, NodeViews)

**Referenzdokumente**

- Architektur: 10 §1.5 (ED-2, Teil Menüs/Blöcke), §3.9, §3.10, §3.13, §3.14
- Analyse/Feature: `analysis/12-editor-echtzeit-live.md` §2.10, §2.11, §2.12, §2.17, §2.13, §3.10, §2.16
- Analyse/Feature: `analysis/03-api-intern-workspace-projekt-user.md` §3.13
- Feature-Katalog: `features/10-ce-feature-katalog.md` (Einträge CE-PAGE-024, CE-PAGE-025, CE-PAGE-026, CE-PAGE-030, CE-PAGE-031, CE-PAGE-032, CE-PAGE-033)

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- Backend: `apps/api/plane/app/views/asset/v2.py`, `apps/api/plane/app/views/asset/base.py`, `apps/api/plane/settings/storage.py`, `apps/api/plane/db/models/asset.py`
- Frontend: `packages/editor/src/extensions/slash-commands/root.tsx`, `packages/editor/src/extensions/slash-commands/command-items-list.tsx`, `packages/editor/src/extensions/slash-commands/command-menu.tsx`, `packages/editor/src/extensions/slash-commands/command-menu-item.tsx`, `packages/editor/src/components/menus/bubble-menu/root.tsx`, `packages/editor/src/components/menus/bubble-menu/node-selector.tsx`, `packages/editor/src/components/menus/bubble-menu/link-selector.tsx`, `packages/editor/src/components/menus/bubble-menu/color-selector.tsx`, `packages/editor/src/components/menus/bubble-menu/alignment-selector.tsx`, `packages/editor/src/components/menus/floating-menu/root.tsx`, `packages/editor/src/extensions/side-menu.ts`, `packages/editor/src/plugins/drag-handle.ts`, `packages/editor/src/components/menus/block-menu.tsx`, `packages/editor/src/components/menus/block-menu-options.tsx`, `packages/editor/src/styles/drag-drop.css`, `packages/editor/src/extensions/code/code-block.ts`, `packages/editor/src/extensions/code/index.tsx`, `packages/editor/src/extensions/code/lowlight-plugin.ts`, `packages/editor/src/extensions/code/code-block-node-view.tsx`, `packages/editor/src/extensions/code/utils/replace-code-block-with-text.ts`, `packages/editor/src/styles/github-dark.css`, `packages/editor/src/extensions/table/table/table.ts`, `packages/editor/src/extensions/table/table/table-view.tsx`, `packages/editor/src/extensions/table/plugins/drag-handles/column/drag-handle.tsx`, `packages/editor/src/extensions/table/plugins/drag-handles/row/dropdown.tsx`, `packages/editor/src/extensions/table/plugins/insert-handlers/utils.ts`, `packages/editor/src/extensions/table/plugins/selection-outline/plugin.ts`, `packages/editor/src/styles/table.css`, `packages/editor/src/extensions/custom-image/extension.tsx`, `packages/editor/src/extensions/custom-image/components/block.tsx`, `packages/editor/src/extensions/custom-image/components/uploader.tsx`, `packages/editor/src/extensions/custom-image/components/toolbar/full-screen/modal.tsx`, `packages/editor/src/plugins/drop.ts`, `packages/editor/src/plugins/file/delete.ts`, `packages/editor/src/plugins/file/restore.ts`, `packages/editor/src/helpers/asset-duplication.ts`, `apps/web/services/file.service.ts`, `packages/editor/src/extensions/callout/extension.tsx`, `packages/editor/src/extensions/callout/block.tsx`, `packages/editor/src/extensions/callout/logo-selector.tsx`, `packages/editor/src/extensions/callout/color-selector.tsx`, `packages/editor/src/extensions/callout/utils.ts`

**Endpunkte (Katalog 04, `architecture/_data/endpoints.json`; 5 registriert)**

| EP | Methode | Pfad | Oberfläche | Handler | Permission | Inkr. 04 | CE-IDs |
|---|---|---|---|---|---|---|---|
| EP-0418 | POST | `/api/assets/v2/workspaces/{slug}/projects/{project_id}/` | App | ProjectAssetEndpoints.CreateProjectAssetUploadCommand | project.asset.create | I2 | CE-PAGE-032, CE-OPS-012, CE-OPS-013 |
| EP-0420 | POST | `/api/assets/v2/workspaces/{slug}/projects/{project_id}/{entity_id}/bulk/` | App | ProjectAssetEndpoints.BulkConfirmProjectAssetsCommand | project.asset.create | I2 | CE-PAGE-032, CE-OPS-012, CE-OPS-013 |
| EP-0421 | GET | `/api/assets/v2/workspaces/{slug}/projects/{project_id}/{pk}/` | App | ProjectAssetEndpoints.GetProjectAssetRedirectQuery | project.asset.read | I2 | CE-PAGE-032, CE-OPS-012, CE-OPS-013 |
| EP-0422 | PATCH | `/api/assets/v2/workspaces/{slug}/projects/{project_id}/{pk}/` | App | ProjectAssetEndpoints.ConfirmProjectAssetUploadCommand | project.asset.update | I2 | CE-PAGE-032, CE-OPS-012, CE-OPS-013 |
| EP-0423 | DELETE | `/api/assets/v2/workspaces/{slug}/projects/{project_id}/{pk}/` | App | ProjectAssetEndpoints.DeleteProjectAssetCommand | project.asset.delete | I2 | CE-PAGE-032, CE-OPS-012, CE-OPS-013 |

**Akzeptanzkriterien**

1. AK-D10-05…-11 grün; Visual W-046 (Beschreibung) ≤ 0,5 %.
2. G-SCHEMA unverändert (Schema-Freeze) oder genehmigte Änderung; G-DOC-Fälle für jeden betroffenen Node/Mark.
3. Browser-Roundtrip-Test (Playwright) für Yjs, sofern Kollaboration betroffen; Visual-Prüfpunkte des Editors.
4. `ce-coverage-check --ids CE-PAGE-024,CE-PAGE-025,CE-PAGE-026,CE-PAGE-030,CE-PAGE-031,CE-PAGE-032,CE-PAGE-033` grün (Mindestebenen 15 Anhang B).

**Testumfang**

- Pflicht-Ebenen (aus 15 Anhang B): L2, L4, L7, L8
- Testprojekte: `Frontend-only`
- E2E-Specs (`frontend/apps/e2e/`): `web/editor/editor-menus.spec.ts`, `web/editor/editor-blocks.spec.ts`

### WP-I2-024 – Editor ED-3: Document-Editor read-only (Beschreibungs-Versionen)

| Merkmal | Wert |
|---|---|
| Inkrement | I2 |
| Typ (DoD 15 §3.15.3) | D – Editor/Dokumente |
| Größe | S |
| parallelisierbar | nein |
| Abhängigkeiten | WP-I2-023 |
| CE-IDs | CE-PAGE-023 |

**Ziel.** `PlEdDocumentEditor` + `PlEdPageRenderer` + Outline-Extension für die Anzeige von Beschreibungs-Versionen.

**Enthaltene CE-IDs**

| CE-ID | Feature | Status (15 Anh. B) | Inkrement laut 15 | Pflicht-Ebenen | Testprojekt | E2E-Spec |
|---|---|---|---|---|---|---|
| CE-PAGE-023 | Dokument-Editor (read-only, Versionen) | übernommen | I2/I4 | L2 L4 L7 L8 (G-DOC/G-SCHEMA) | Frontend-only | `web/editor/editor-variants.spec.ts` |

**Betroffene Module/Libs in `funk.`**

- Frontend: `frontend/libs/shared/editor/components`

**Referenzdokumente**

- Architektur: 10 §1.5 (ED-3), §3.18
- Analyse/Feature: `analysis/12-editor-echtzeit-live.md` §2.1
- Analyse/Feature: `analysis/10b-frontend-cycles-modules-pages-views-weitere.md` §2.17
- Feature-Katalog: `features/10-ce-feature-katalog.md` (Einträge CE-PAGE-023)

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- Frontend: `packages/editor/src/components/editors/document/editor.tsx`, `packages/editor/src/components/editors/document/page-renderer.tsx`, `apps/web/components/editor/document/editor.tsx`

**Akzeptanzkriterien**

1. AK-D10-01, -13 grün.
2. G-SCHEMA unverändert (Schema-Freeze) oder genehmigte Änderung; G-DOC-Fälle für jeden betroffenen Node/Mark.
3. Browser-Roundtrip-Test (Playwright) für Yjs, sofern Kollaboration betroffen; Visual-Prüfpunkte des Editors.
4. `ce-coverage-check --ids CE-PAGE-023` grün (Mindestebenen 15 Anhang B).

**Testumfang**

- Pflicht-Ebenen (aus 15 Anhang B): L2, L4, L7, L8
- Testprojekte: `Frontend-only`
- E2E-Specs (`frontend/apps/e2e/`): `web/editor/editor-variants.spec.ts`

### WP-I2-101 – Funk.Documents Teil A: Server-Schema, HTML↔PM-JSON, Text-Extraktion, Sanitizing, Yjs-Update-Validierung

| Merkmal | Wert |
|---|---|
| Inkrement | I2 |
| Typ (DoD 15 §3.15.3) | D – Editor/Dokumente |
| Größe | L |
| parallelisierbar | ja |
| Abhängigkeiten | WP-I0-999, WP-I0-902 |
| CE-IDs | CE-OPS-017 |

**Ziel.** Server-Schema aller Nodes/Marks, `HtmlSerializer`, `HtmlParser`, PM-JSON-Modell, `HtmlTextExtractor` (`description_stripped`), `YjsUpdateValidator`, `DocumentReferenceExtractor` (Mentions) und das HtmlSanitizer-Profil (Port von `nh3`) mit Binärprüfung.

**Enthaltene CE-IDs**

| CE-ID | Feature | Status (15 Anh. B) | Inkrement laut 15 | Pflicht-Ebenen | Testprojekt | E2E-Spec |
|---|---|---|---|---|---|---|
| CE-OPS-017 | Rich-Text-Sanitizing und Binary-Prüfung | übernommen | I2 | L1 L3 L4 (G-SANITIZE) | Funk.Platform.Tests, Funk.Documents.Tests | – |

**Betroffene Module/Libs in `funk.`**

- Backend: `src/documents/Funk.Documents`
- Backend: `src/platform/Funk.Platform.Security/Sanitizing/`
- Backend: `tests/Funk.Documents.Tests`

**Referenzdokumente**

- Architektur: 07 §1.4 Zeile I2, §3.12, §3.13
- Architektur: 05 §3.17.3, R-08
- Architektur: 15 §3.7 (G-DOC, G-SANITIZE)
- Analyse/Feature: `analysis/06-auth-sicherheit-querschnitt.md` §2.14
- Feature-Katalog: `features/10-ce-feature-katalog.md` (Einträge CE-OPS-017)

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- Backend: `apps/api/plane/utils/content_validator.py`, `apps/api/plane/app/serializers/issue.py`, `apps/api/plane/app/serializers/page.py`
- `apps/api/plane/utils/content_validator.py`
- `packages/editor/src/core/extensions/`

**Akzeptanzkriterien**

1. G-DOC (HTML↔JSON) und G-SANITIZE grün; Abweichungen des Sanitizers gegenüber `nh3` mit Begründung in `deviations.yaml`.
2. G-SCHEMA unverändert (Schema-Freeze) oder genehmigte Änderung; G-DOC-Fälle für jeden betroffenen Node/Mark.
3. Browser-Roundtrip-Test (Playwright) für Yjs, sofern Kollaboration betroffen; Visual-Prüfpunkte des Editors.
4. `ce-coverage-check --ids CE-OPS-017` grün (Mindestebenen 15 Anhang B).

**Testumfang**

- Pflicht-Ebenen (aus 15 Anhang B): L1, L3, L4
- Testprojekte: `Funk.Platform.Tests`, `Funk.Documents.Tests`

### WP-I2-102 – SSRF-sicherer HTTP-Client und Link-Crawler

| Merkmal | Wert |
|---|---|
| Inkrement | I2 |
| Typ (DoD 15 §3.15.3) | B – Backend-only |
| Größe | S |
| parallelisierbar | ja |
| Abhängigkeiten | WP-I1-999 |
| CE-IDs | CE-OPS-018 |

**Ziel.** `SsrfSafeHttpHandler` mit Ziel-Allowlists, IP-Pinning, ohne Redirects/Proxy; benannte Clients (`webhooks`, `link-crawler`, `integrations`, `forgejo`, `llm`, `unsplash`); Link-Crawler-Job für Work-Item-Links.

**Enthaltene CE-IDs**

| CE-ID | Feature | Status (15 Anh. B) | Inkrement laut 15 | Pflicht-Ebenen | Testprojekt | E2E-Spec |
|---|---|---|---|---|---|---|
| CE-OPS-018 | SSRF-sichere ausgehende Requests | übernommen | I2 | L1 L3 | Funk.Platform.Tests | – |

**Betroffene Module/Libs in `funk.`**

- Backend: `src/platform/Funk.Platform.Security/Ssrf/`
- Backend: `tests/Funk.Platform.Tests/Ssrf/`

**Referenzdokumente**

- Architektur: 05 §3.17.2, §5.9
- Architektur: 17 ABG-040
- Analyse/Feature: `analysis/07-hintergrundjobs-mail-storage-webhooks.md` §2.11
- Feature-Katalog: `features/10-ce-feature-katalog.md` (Einträge CE-OPS-018)

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- Backend: `apps/api/plane/utils/url_security.py`, `apps/api/plane/utils/ip_address.py`, `apps/api/plane/settings/common.py`
- `apps/api/plane/bgtasks/work_item_link_task.py`
- `apps/api/plane/utils/url.py`

**Akzeptanzkriterien**

1. Contract-Szenarien mit Original-Golden für alle HTTP-Endpunkte dieses Pakets; Replay grün.
2. Job-/Consumer-Tests: Idempotenz (Inbox), Retry/Backoff, Zeitsteuerung mit `FixedClock`; neue Ereignistypen im Event-Katalog-Snapshot.
3. Bei Cron-Jobs: Registrierung in `CronRegistrationTests` mit Original-Zeit (UTC).
4. `ce-coverage-check --ids CE-OPS-018` grün (Mindestebenen 15 Anhang B).

**Testumfang**

- Pflicht-Ebenen (aus 15 Anhang B): L1, L3
- Testprojekte: `Funk.Platform.Tests`

### WP-I2-103 – Dummy-Daten-Generator und Volumen-Seeder (S/M/L/XL)

| Merkmal | Wert |
|---|---|
| Inkrement | I2 |
| Typ (DoD 15 §3.15.3) | I – Infrastruktur/Baustein |
| Größe | S |
| parallelisierbar | ja |
| Abhängigkeiten | WP-I2-001 |
| CE-IDs | CE-OPS-024 |

**Ziel.** `funk-cli create-dummy-data` (Port des Management-Commands) und die Volumenprofile aus `tests/seed/volume-profiles.yaml` für Last- und Performancetests.

**Enthaltene CE-IDs**

| CE-ID | Feature | Status (15 Anh. B) | Inkrement laut 15 | Pflicht-Ebenen | Testprojekt | E2E-Spec |
|---|---|---|---|---|---|---|
| CE-OPS-024 | Dummy-Daten-Generator | übernommen | I2 | L1 L3 | Funk.Cli.Tests | – |

**Betroffene Module/Libs in `funk.`**

- Backend: `src/tools/Funk.Cli` (create-dummy-data)
- Backend: `tests/seed/volume-profiles.yaml`

**Referenzdokumente**

- Architektur: 03 §3.15
- Architektur: 15 §3.14.3
- Architektur: 14 §3.1.2 Zeile I2/I3
- Analyse/Feature: `analysis/07-hintergrundjobs-mail-storage-webhooks.md` §3.16
- Feature-Katalog: `features/10-ce-feature-katalog.md` (Einträge CE-OPS-024)

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- Backend: `apps/api/plane/bgtasks/dummy_data_task.py`, `apps/api/plane/db/management/commands/create_dummy_data.py`
- `apps/api/plane/db/management/commands/create_dummy_data.py`

**Akzeptanzkriterien**

1. Unit-Tests ≥ 90 % Zeilen; Architekturtest für jede neue Regel; AppHost-Test, falls Topologie betroffen.
2. Kurzreferenz in `docs/` des Repos `funk.`.
3. `ce-coverage-check --ids CE-OPS-024` grün (Mindestebenen 15 Anhang B).

**Testumfang**

- Pflicht-Ebenen (aus 15 Anhang B): L1, L3
- Testprojekte: `Funk.Cli.Tests`

### WP-I2-201 – Erweiterungspunkt B6/A1: Filter-AST, Parser-Liste, Feld-/Gruppen-/Sortier-Registries, Payload-Extension, Basismengen-Filter

| Merkmal | Wert |
|---|---|
| Inkrement | I2 |
| Typ (DoD 15 §3.15.3) | X – Erweiterungspunkt 🧱 |
| Größe | M |
| parallelisierbar | nein |
| Abhängigkeiten | WP-I1-999, WP-I0-909 |
| CE-IDs | – (keine; Erweiterungspunkt) |
| Andockstelle | 01 §1.4 A1/B6; 16 §3.3.0 E-04; 16 §4.6 (Träger CE-LV-006…010, CE-LV-017, CE-LV-046) |

**Ziel.** Filter-AST (`FilterExpression` And/Or/Not/Condition) mit erweiterbarem Operator-Katalog als einzige Abfragesprache, `IFilterParser`-Liste (legacy, rich), `IFilterFieldProvider`, `IGroupKeyProvider`, `IOrderKeyProvider`, `IWorkItemPayloadExtension`, `IWorkItemBaseSetFilter` (E-04).

**Betroffene Module/Libs in `funk.`**

- Backend: `src/modules/WorkItems/Funk.WorkItems.Contracts/Query/`
- Backend: `src/modules/WorkItems/Funk.WorkItems/Query/`

**Referenzdokumente**

- Architektur: 02 §3.11
- Architektur: 16 §5.5, §3.3.0 E-04
- Architektur: 01 §1.4 Zeilen A1, B6

**Akzeptanzkriterien**

1. Property-Test: Legacy- und Rich-Parser erzeugen für äquivalente Eingaben denselben AST.
2. Fake-Feld-Provider ergänzt ein filter-, gruppier- und sortierbares Feld ohne CE-Änderung (Typ X).
3. Contract (Interface/Schema/Token) + CE-Default-Implementierung; Eintrag in `tests/extension-points.yaml`.
4. Test „CE-Default = Original-Verhalten“ (Contract-Replay unverändert grün).
5. Test mit Fake-Erweiterung aus `Funk.BuildingBlocks.Testing/Extensions` bzw. `provideFakeExtensions()` beweist Erweiterbarkeit ohne CE-Änderung (DoD Typ X).

**Testumfang**

- Typ-X-Tests (CE-Default unverändert, Fake-Erweiterung wirkt ohne CE-Änderung), L0-Inventarabgleich `ExtensionPointInventoryTests`/`extension-registry-check`.

### WP-I2-202 – Erweiterungspunkt A1: work_items.type_id, Minimal-Tabelle work_item_types, IWorkItemTypeResolver

| Merkmal | Wert |
|---|---|
| Inkrement | I2 |
| Typ (DoD 15 §3.15.3) | X – Erweiterungspunkt 🧱 |
| Größe | S |
| parallelisierbar | nein |
| Abhängigkeiten | WP-I1-999 |
| CE-IDs | – (keine; Erweiterungspunkt) |
| Andockstelle | 01 §1.4 A1; 16 §3.3.0 E-03; 16 §4.6 (Träger CE-WI-001, CE-WI-049) |

**Ziel.** Nullable FK `work_items.type_id` auf die leere Minimal-Tabelle `work_item_types` (`id`, `workspace_id`, `project_id` nullable, `name`, `is_default`, Audit) und `IWorkItemTypeResolver` (E-03, CE liefert `null`).

**Betroffene Module/Libs in `funk.`**

- Backend: `src/data/Funk.Data/Entities/WorkItems/WorkItemType.cs`
- Backend: `src/modules/WorkItems/Funk.WorkItems.Contracts/IWorkItemTypeResolver.cs`

**Referenzdokumente**

- Architektur: 16 §5.1, §3.3.0 E-03
- Architektur: 01 §1.4 Zeile A1
- Architektur: 03 §3.4.5

**Akzeptanzkriterien**

1. Contract-Goldens der Work-Item-Payloads unverändert (Feld `type_id` wie Original); Fake-Resolver setzt einen Default-Typ ohne CE-Änderung (Typ X).
2. Contract (Interface/Schema/Token) + CE-Default-Implementierung; Eintrag in `tests/extension-points.yaml`.
3. Test „CE-Default = Original-Verhalten“ (Contract-Replay unverändert grün).
4. Test mit Fake-Erweiterung aus `Funk.BuildingBlocks.Testing/Extensions` bzw. `provideFakeExtensions()` beweist Erweiterbarkeit ohne CE-Änderung (DoD Typ X).

**Testumfang**

- Typ-X-Tests (CE-Default unverändert, Fake-Erweiterung wirkt ohne CE-Änderung), L0-Inventarabgleich `ExtensionPointInventoryTests`/`extension-registry-check`.

### WP-I2-203 – Erweiterungspunkt A9: Relationstyp-Katalog, IWorkItemHierarchyPolicy, IRelatedScopeCheck, RELATION_TYPES, TIMELINE_FLAGS

| Merkmal | Wert |
|---|---|
| Inkrement | I2 |
| Typ (DoD 15 §3.15.3) | X – Erweiterungspunkt 🧱 |
| Größe | S |
| parallelisierbar | nein |
| Abhängigkeiten | WP-I1-999 |
| CE-IDs | – (keine; Erweiterungspunkt) |
| Andockstelle | 01 §1.4 A9; 16 §3.3.0 E-05; 16 §4.6 (Träger CE-WI-031…033, CE-LV-033, CE-API-024) |

**Ziel.** Katalogtabelle `work_item_relation_types` mit 10 Seeds statt Enum, projektübergreifende Relationen im Schema zulässig, `IWorkItemHierarchyPolicy` (E-05, CE: gleiches Projekt, kein Zyklus), `IRelatedScopeCheck`; Frontend `RELATION_TYPES`, `TIMELINE_FLAGS`.

**Betroffene Module/Libs in `funk.`**

- Backend: `src/modules/WorkItems/Funk.WorkItems` (Relations)
- Backend: `src/data/Funk.Data/Seeds/RelationTypes.cs`
- Frontend: `frontend/libs/web/extensions/src/relations.ts`

**Referenzdokumente**

- Architektur: 16 §5.3, §3.3.0 E-05
- Architektur: 01 §1.4 Zeile A9

**Akzeptanzkriterien**

1. Seeds entsprechen `IssueRelationChoices`; Fake-Relationstyp erscheint in Dropdown und Gantt ohne CE-Änderung (Typ X).
2. Contract (Interface/Schema/Token) + CE-Default-Implementierung; Eintrag in `tests/extension-points.yaml`.
3. Test „CE-Default = Original-Verhalten“ (Contract-Replay unverändert grün).
4. Test mit Fake-Erweiterung aus `Funk.BuildingBlocks.Testing/Extensions` bzw. `provideFakeExtensions()` beweist Erweiterbarkeit ohne CE-Änderung (DoD Typ X).

**Testumfang**

- Typ-X-Tests (CE-Default unverändert, Fake-Erweiterung wirkt ohne CE-Änderung), L0-Inventarabgleich `ExtensionPointInventoryTests`/`extension-registry-check`.

### WP-I2-204 – Erweiterungspunkt C1: State-Change-Pipeline IWorkItemStateChanger mit Guards/Hooks, WORKFLOW_GUARD

| Merkmal | Wert |
|---|---|
| Inkrement | I2 |
| Typ (DoD 15 §3.15.3) | X – Erweiterungspunkt 🧱 |
| Größe | S |
| parallelisierbar | nein |
| Abhängigkeiten | WP-I1-999, WP-I1-201 |
| CE-IDs | – (keine; Erweiterungspunkt) |
| Andockstelle | 01 §1.4 C1; 16 §4.6 (Träger CE-WI-021, CE-WI-003; weitere Origins in I3/I6) |

**Ziel.** Jeder State-Wechsel (UI, API, Intake, Cycle-Transfer, Auto-Close, Integrationen) läuft durch `IWorkItemStateChanger` mit `IStateTransitionGuard`/`IStateTransitionHook` und `StateChangeOrigin`; Frontend-Token `WORKFLOW_GUARD`.

**Betroffene Module/Libs in `funk.`**

- Backend: `src/modules/WorkItems/Funk.WorkItems.Contracts/StateChanges/`
- Frontend: `frontend/libs/web/extensions/src/workflow.ts`

**Referenzdokumente**

- Architektur: 16 §5.9
- Architektur: 01 §1.4 Zeile C1
- Architektur: 06 §6.1

**Akzeptanzkriterien**

1. Architekturtest: kein Schreibzugriff auf `work_items.state_id` außerhalb der Pipeline.
2. Fake-Guard verhindert einen Übergang mit Original-Fehlerform; Fake-Hook wird aufgerufen (Typ X).
3. Contract (Interface/Schema/Token) + CE-Default-Implementierung; Eintrag in `tests/extension-points.yaml`.
4. Test „CE-Default = Original-Verhalten“ (Contract-Replay unverändert grün).
5. Test mit Fake-Erweiterung aus `Funk.BuildingBlocks.Testing/Extensions` bzw. `provideFakeExtensions()` beweist Erweiterbarkeit ohne CE-Änderung (DoD Typ X).

**Testumfang**

- Typ-X-Tests (CE-Default unverändert, Fake-Erweiterung wirkt ohne CE-Änderung), L0-Inventarabgleich `ExtensionPointInventoryTests`/`extension-registry-check`.

### WP-I2-205 – Erweiterungspunkte Work-Item-Fassaden: IWorkItemReferenceResolver, IWorkItemCommands, IIntegrationLinkProvider + external_links, IExpandProvider

| Merkmal | Wert |
|---|---|
| Inkrement | I2 |
| Typ (DoD 15 §3.15.3) | X – Erweiterungspunkt 🧱 |
| Größe | S |
| parallelisierbar | nein |
| Abhängigkeiten | WP-I1-999, WP-I0-205 |
| CE-IDs | – (keine; Erweiterungspunkt) |
| Andockstelle | 16 §3.3.0 E-06, E-07 (Teil `expand`), E-13, E-18; 16 §4.6 (Träger CE-WI-009, CE-WI-002, CE-WI-001, CE-WI-010) |

**Ziel.** Zentraler Resolver `<IDENTIFIER>-<sequence>` (E-06), Contracts-Fassade `IWorkItemCommands` (E-18, von Intake und Public API selbst genutzt), Lesefassade `IIntegrationLinkProvider` (E-13, CE `[]`), leere Tabelle `external_links` (FK auf `work_items`/`work_item_comments`, ABG-141) und `IExpandProvider` für den `expand`-Parameter der Work-Item-Endpunkte (E-07, Teil I2).

**Betroffene Module/Libs in `funk.`**

- Backend: `src/modules/WorkItems/Funk.WorkItems.Contracts/Services/`
- Backend: `src/data/Funk.Data/Entities/Integrations/ExternalLink.cs`
- Backend: Migration `…_Integrations_ExternalLinks`

**Referenzdokumente**

- Architektur: 16 §5.16, §3.3.0 E-06/E-13/E-18, D16-ADR-11
- Architektur: 16 §3.4.2
- Architektur: 17 ABG-141

**Akzeptanzkriterien**

1. Resolver löst case-insensitiv, respektiert Archiv/Löschung/Gast-Sichtbarkeit; Fake-Link-Provider liefert Einträge, die im Detail über `INTEGRATION_LINK_PREVIEWS` erscheinen (Typ X).
2. Contract (Interface/Schema/Token) + CE-Default-Implementierung; Eintrag in `tests/extension-points.yaml`.
3. Test „CE-Default = Original-Verhalten“ (Contract-Replay unverändert grün).
4. Test mit Fake-Erweiterung aus `Funk.BuildingBlocks.Testing/Extensions` bzw. `provideFakeExtensions()` beweist Erweiterbarkeit ohne CE-Änderung (DoD Typ X).

**Testumfang**

- Typ-X-Tests (CE-Default unverändert, Fake-Erweiterung wirkt ohne CE-Änderung), L0-Inventarabgleich `ExtensionPointInventoryTests`/`extension-registry-check`.

### WP-I2-206 – Erweiterungspunkte Work-Item-UI-Registries (Property-Renderer bis Duplicate-Detection)

| Merkmal | Wert |
|---|---|
| Inkrement | I2 |
| Typ (DoD 15 §3.15.3) | X – Erweiterungspunkt 🧱 |
| Größe | M |
| parallelisierbar | nein |
| Abhängigkeiten | WP-I1-999 |
| CE-IDs | – (keine; Erweiterungspunkt) |
| Andockstelle | 16 §1.4 Zeile I2 (Frontend); 16 §4.6 (Träger CE-WI-001/-010/-014/-034, CE-LV-008/-017…037) |

**Ziel.** Frontend-Registries `PROPERTY_RENDERERS`, `WORK_ITEM_IDENTIFIER_DECORATORS`, `SPREADSHEET_COLUMNS`, `GROUP_BY_OPTIONS`, `FILTER_FIELDS`, `FILTER_OPERATORS`, `ISSUE_MODAL_CONTEXT`, `WORK_ITEM_PROPERTIES_LOADER`, `WORK_ITEM_DETAIL_WIDGETS`, `WORK_ITEM_ACTIONS`, `ACTIVITY_RENDERERS`, `INTEGRATION_LINK_PREVIEWS`, `DUPLICATE_DETECTION` mit CE-Einträgen (S5–S19, S29, S62–S65).

**Betroffene Module/Libs in `funk.`**

- Frontend: `frontend/libs/web/extensions/src/work-items/`

**Referenzdokumente**

- Architektur: 08 §6.1, §6.4, §6.5
- Architektur: 16 §1.4 Zeile I2
- Architektur: 17 ABG-030

**Akzeptanzkriterien**

1. Jede Registry hat CE-Einträge (Original-Verhalten) und einen Fake-Eintrag-Test (Typ X).
2. Contract (Interface/Schema/Token) + CE-Default-Implementierung; Eintrag in `tests/extension-points.yaml`.
3. Test „CE-Default = Original-Verhalten“ (Contract-Replay unverändert grün).
4. Test mit Fake-Erweiterung aus `Funk.BuildingBlocks.Testing/Extensions` bzw. `provideFakeExtensions()` beweist Erweiterbarkeit ohne CE-Änderung (DoD Typ X).

**Testumfang**

- Typ-X-Tests (CE-Default unverändert, Fake-Erweiterung wirkt ohne CE-Änderung), L0-Inventarabgleich `ExtensionPointInventoryTests`/`extension-registry-check`.

### WP-I2-207 – Erweiterungspunkt Editor/Dokument-Schema: IDocumentNodeSpec/IDocumentMarkSpec, EDITOR_EXTENSIONS, EDITOR_FLAGS (Lite)

| Merkmal | Wert |
|---|---|
| Inkrement | I2 |
| Typ (DoD 15 §3.15.3) | X – Erweiterungspunkt 🧱 |
| Größe | S |
| parallelisierbar | nein |
| Abhängigkeiten | WP-I0-999, WP-I0-905 |
| CE-IDs | – (keine; Erweiterungspunkt) |
| Andockstelle | 16 §3.3.0 E-11; 16 §4.6 (Träger CE-WI-037, CE-WI-044) |

**Ziel.** Server-Schema aus `IEnumerable<IDocumentNodeSpec>`/`IEnumerable<IDocumentMarkSpec>` (E-11) und Editor-Tokens `EDITOR_EXTENSIONS`/`EDITOR_FLAGS` mit CE-Defaults.

**Betroffene Module/Libs in `funk.`**

- Backend: `src/documents/Funk.Documents/Schema/`
- Frontend: `frontend/libs/shared/editor/extensibility`

**Referenzdokumente**

- Architektur: 10 §5.10, §6.1
- Architektur: 07 §5.7
- Architektur: 16 §3.3.0 E-11

**Akzeptanzkriterien**

1. G-SCHEMA unverändert mit CE-Defaults; Fake-Node erweitert Client- und Server-Schema ohne CE-Änderung (Typ X).
2. Contract (Interface/Schema/Token) + CE-Default-Implementierung; Eintrag in `tests/extension-points.yaml`.
3. Test „CE-Default = Original-Verhalten“ (Contract-Replay unverändert grün).
4. Test mit Fake-Erweiterung aus `Funk.BuildingBlocks.Testing/Extensions` bzw. `provideFakeExtensions()` beweist Erweiterbarkeit ohne CE-Änderung (DoD Typ X).

**Testumfang**

- Typ-X-Tests (CE-Default unverändert, Fake-Erweiterung wirkt ohne CE-Änderung), L0-Inventarabgleich `ExtensionPointInventoryTests`/`extension-registry-check`.

### WP-I2-999 – Abnahme I2 – Work Items & Layouts (G5)

| Merkmal | Wert |
|---|---|
| Inkrement | I2 |
| Typ (DoD 15 §3.15.3) | A – Inkrement-Abnahme |
| Größe | S |
| parallelisierbar | nein |
| Abhängigkeiten | WP-I2-001, WP-I2-002, WP-I2-003, WP-I2-004, WP-I2-005, WP-I2-006, WP-I2-007, WP-I2-008, WP-I2-009, WP-I2-010, WP-I2-011, WP-I2-012, WP-I2-013, WP-I2-014, WP-I2-015, WP-I2-016, WP-I2-017, WP-I2-018, WP-I2-019, WP-I2-020, WP-I2-021, WP-I2-022, WP-I2-023, WP-I2-024, WP-I2-101, WP-I2-102, WP-I2-103, WP-I2-201, WP-I2-202, WP-I2-203, WP-I2-204, WP-I2-205, WP-I2-206, WP-I2-207 |
| CE-IDs | – (keine; Baustein/Spike/Abnahme) |

**Ziel.** Inkrement-Abnahme I2 nach G5 und Meilenstein M2.

**Referenzdokumente**

- Architektur: plan/01-roadmap-ce.md §4 (M2)
- Architektur: 15 §3.16 Zeile I2

**Akzeptanzkriterien**

1. Alle Abnahmekriterien M2 erfüllt; `docs/acceptance/I2.md` generiert.
2. G5 `--inc <In> --strict` grün: `ce-coverage-check`, `original-test-ledger`, Parity-Report (0 ungenehmigte Abweichungen, Endpunkt-Abdeckung des Inkrements 100 %), Visual/a11y, Lastziele, Security-Report.
3. Demo-Video der Kern-Flows (`--video on`) und Abnahmebericht `docs/acceptance/<In>.md`; fachliche Abnahme durch den Auftraggeber.

**Testumfang**

- G5 `--inc I2`.

## 4.4 Inkrement I3

### WP-I3-001 – Projekt-Archive und Layout-Kontexte (Cycle, Modul, View, Archiv, Profil)

| Merkmal | Wert |
|---|---|
| Inkrement | I3 |
| Typ (DoD 15 §3.15.3) | V – Vertikaler Schnitt |
| Größe | M |
| parallelisierbar | ja |
| Abhängigkeiten | WP-I2-999 |
| CE-IDs | CE-LV-004, CE-LV-046 |

**Ziel.** Projekt-Archive (Kopf, Tabs für Work Items, Cycles, Module) und die Layout-Kontexte, in denen die I2-Layouts wiederverwendet werden.

> **Hinweis:** CE-LV-004 wurde von I2 nach I3 verschoben, weil die Kontexte erst mit Cycles/Modulen/Views existieren (plan/04 OP-PLAN-03).

**Enthaltene CE-IDs**

| CE-ID | Feature | Status (15 Anh. B) | Inkrement laut 15 | Pflicht-Ebenen | Testprojekt | E2E-Spec |
|---|---|---|---|---|---|---|
| CE-LV-004 | Layout-Kontexte Cycle, Modul, View, Archiv, Profil | übernommen | I2 | L2 L7 L8 | Frontend-only | `web/layouts/layout-switch.spec.ts` |
| CE-LV-046 | Projekt-Archive (Kopf und Tabs) | übernommen | I3 | L2 L7 L8 | Frontend-only | `web/views/archives.spec.ts` |

**Betroffene Module/Libs in `funk.`**

- Frontend: `frontend/libs/web/archives`
- Frontend: `frontend/libs/web/work-items` (Layout-Kontexte)

**Referenzdokumente**

- Architektur: 08 §4.1
- Architektur: 02 §3.11.4 (Basismengen)
- Analyse/Feature: `analysis/09-frontend-arbeitsobjekte-layouts.md` §2.1, §2.18
- Analyse/Feature: `analysis/10a-frontend-workspace-projekt-navigation.md` §2.17
- Analyse/Feature: `analysis/08-frontend-web-architektur.md` §2.2
- Analyse/Feature: `analysis/04-api-intern-arbeitsobjekte.md` §2.8
- Feature-Katalog: `features/10-ce-feature-katalog.md` (Einträge CE-LV-004, CE-LV-046)

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- Backend: `apps/api/plane/app/views/issue/archive.py`
- Frontend: `apps/web/components/issues/issue-layouts/roots/cycle-layout-root.tsx`, `apps/web/components/issues/issue-layouts/roots/module-layout-root.tsx`, `apps/web/components/issues/issue-layouts/roots/project-view-layout-root.tsx`, `apps/web/components/issues/issue-layouts/roots/archived-issue-layout-root.tsx`, `apps/web/components/issues/issue-layouts/list/roots/profile-issues-root.tsx`, `apps/web/components/cycles/transfer-issues.tsx`, `apps/web/components/issues/archived-issues-header.tsx`, `apps/web/components/archives/archive-tabs-list.tsx`, `apps/web/app/(all)/[workspaceSlug]/(projects)/projects/(detail)/[projectId]/archives/issues/(list)/page.tsx`, `apps/web/app/(all)/[workspaceSlug]/(projects)/projects/(detail)/[projectId]/archives/issues/(detail)/[archivedIssueId]/page.tsx`, `apps/web/app/(all)/[workspaceSlug]/(projects)/projects/(detail)/[projectId]/archives/cycles/page.tsx`, `apps/web/app/(all)/[workspaceSlug]/(projects)/projects/(detail)/[projectId]/archives/modules/page.tsx`, `apps/web/store/issue/archived/issue.store.ts`

**Endpunkte (Katalog 04, `architecture/_data/endpoints.json`; 1 registriert)**

| EP | Methode | Pfad | Oberfläche | Handler | Permission | Inkr. 04 | CE-IDs |
|---|---|---|---|---|---|---|---|
| EP-0254 | GET | `/api/workspaces/{slug}/projects/{project_id}/archived-issues/` | App | WorkItemEndpoints.ListArchivedWorkItemsQuery | project.work_item.read_archived | I3 | CE-WI-045, CE-LV-046 |

**Akzeptanzkriterien**

1. Contract: je Endpunkt dieses Pakets ≥ 1 Szenario mit Golden vom Original (Erfolg, Berechtigungsfehler, Validierungsfehler); Replay grün (L5).
2. Permission-Matrix (05 Anhang B) für alle Endpunkte dieses Pakets als L3-Test grün; Tenant-Isolation geprüft.
3. Signal-Stores strukturgleich zum MobX-Original (`store-parity-check`), Vitest je Action (L2).
4. E2E-Specs dieses Pakets grün gegen Original **und** funk. (Dual-Target, Pflichtszenarien 15 §3.9.3).
5. Visual-/DOM-/a11y-Prüfpunkte der betroffenen Screens (09 §4.14, 15 §3.10.2) innerhalb der Schwellwerte 15 §3.10.3 (Chromium); i18n-Schlüssel nur aus den Original-Locales (de/en).
6. `ce-coverage-check --ids CE-LV-004,CE-LV-046` grün (Mindestebenen 15 Anhang B).

**Testumfang**

- Pflicht-Ebenen (aus 15 Anhang B): L2, L7, L8
- Testprojekte: `Frontend-only`
- E2E-Specs (`frontend/apps/e2e/`): `web/layouts/layout-switch.spec.ts`, `web/views/archives.spec.ts`

### WP-I3-002 – Projekt-Views (Liste, Anlage/Bearbeitung, Löschen, Kontextmenü/Favoriten, Detail, Speichern aus Filtern)

| Merkmal | Wert |
|---|---|
| Inkrement | I3 |
| Typ (DoD 15 §3.15.3) | V – Vertikaler Schnitt |
| Größe | L |
| parallelisierbar | ja |
| Abhängigkeiten | WP-I2-999, WP-I3-201 |
| CE-IDs | CE-LV-011, CE-LV-047, CE-LV-048, CE-LV-049, CE-LV-050, CE-LV-051 |

**Ziel.** Projekt-Views auf Basis des Filter-AST inkl. „View aus Filtern speichern/aktualisieren“.

**Enthaltene CE-IDs**

| CE-ID | Feature | Status (15 Anh. B) | Inkrement laut 15 | Pflicht-Ebenen | Testprojekt | E2E-Spec |
|---|---|---|---|---|---|---|
| CE-LV-011 | View aus Filtern speichern oder aktualisieren | übernommen | I2 | L1 L2 L3 L5 L7 L8 | Funk.Views.Tests | `web/layouts/filters.spec.ts` |
| CE-LV-047 | Projekt-View-Liste | übernommen | I3 | L1 L2 L3 L5 L7 L8 | Funk.Views.Tests | `web/views/project-views.spec.ts` |
| CE-LV-048 | Projekt-View anlegen und bearbeiten | übernommen | I3 | L1 L2 L3 L5 L7 L8 | Funk.Views.Tests | `web/views/project-views.spec.ts` |
| CE-LV-049 | Projekt-View löschen | übernommen | I3 | L1 L2 L3 L5 L7 L8 | Funk.Views.Tests | `web/views/project-views.spec.ts` |
| CE-LV-050 | View-Kontextmenü und Favoriten | übernommen | I3 | L1 L2 L3 L5 L7 L8 | Funk.Views.Tests | `web/views/project-views.spec.ts` |
| CE-LV-051 | Projekt-View-Detail | übernommen | I3 | L1 L2 L3 L5 L7 L8 | Funk.Views.Tests | `web/views/project-views.spec.ts` |

**Betroffene Module/Libs in `funk.`**

- Backend: `src/modules/Views/Funk.Views`
- Backend: `tests/modules/Funk.Views.Tests`
- Frontend: `frontend/libs/web/views`

**Referenzdokumente**

- Architektur: 04 §4.6
- Architektur: 03 §3.4.8
- Analyse/Feature: `analysis/09-frontend-arbeitsobjekte-layouts.md` §2.11
- Analyse/Feature: `analysis/10b-frontend-cycles-modules-pages-views-weitere.md` §2.5
- Analyse/Feature: `analysis/08-frontend-web-architektur.md` §2.2
- Analyse/Feature: `analysis/13b-shared-packages-i18n.md` §2.4
- Analyse/Feature: `analysis/04-api-intern-arbeitsobjekte.md` §2.13
- Analyse/Feature: `analysis/02b-datenmodell-arbeitsobjekte.md` §3.10
- Feature-Katalog: `features/10-ce-feature-katalog.md` (Einträge CE-LV-011, CE-LV-047, CE-LV-048, CE-LV-049, CE-LV-050, CE-LV-051)

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- Backend: `apps/api/plane/app/views/view/base.py`, `apps/api/plane/app/serializers/view.py`, `apps/api/plane/db/models/view.py`, `apps/api/plane/utils/issue_filters.py:428-463`
- Frontend: `apps/web/components/work-item-filters/filters-hoc/project-level.tsx`, `apps/web/components/work-item-filters/filters-hoc/workspace-level.tsx`, `apps/web/components/work-item-filters/filters-hoc/base.tsx`, `apps/web/components/views/views-list.tsx`, `apps/web/components/views/view-list-item.tsx`, `apps/web/components/views/view-list-item-action.tsx`, `apps/web/components/views/view-list-header.tsx`, `apps/web/components/views/filters/filter-selection.tsx`, `apps/web/components/views/filters/order-by.tsx`, `apps/web/components/views/applied-filters/root.tsx`, `apps/web/app/(all)/[workspaceSlug]/(projects)/projects/(detail)/[projectId]/views/(list)/page.tsx`, `apps/web/app/(all)/[workspaceSlug]/(projects)/projects/(detail)/[projectId]/views/(detail)/[viewId]/page.tsx`, `apps/web/app/(all)/[workspaceSlug]/(projects)/projects/(detail)/[projectId]/views/(detail)/[viewId]/header.tsx`, `apps/web/store/project-view.store.ts`, `packages/utils/src/page.ts`, `packages/utils/src/project-views.ts`, `packages/constants/src/views.ts`, `packages/constants/src/page.ts`, `apps/web/components/views/modal.tsx`, `apps/web/components/views/form.tsx`, `apps/web/components/views/delete-view-modal.tsx`, `apps/web/components/views/quick-actions.tsx`, `apps/web/components/views/helper.tsx`, `apps/web/components/common/quick-actions-helper.tsx`

**Endpunkte (Katalog 04, `architecture/_data/endpoints.json`; 10 registriert)**

| EP | Methode | Pfad | Oberfläche | Handler | Permission | Inkr. 04 | CE-IDs |
|---|---|---|---|---|---|---|---|
| EP-0120 | POST | `/api/workspaces/{slug}/projects/{project_id}/user-favorite-views/` | App | ViewFavoriteEndpoints.FavoriteViewCommand | project.view.favorite | I3 | CE-LV-050 |
| EP-0121 | DELETE | `/api/workspaces/{slug}/projects/{project_id}/user-favorite-views/{view_id}/` | App | ViewFavoriteEndpoints.UnfavoriteViewCommand | project.view.favorite | I3 | CE-LV-050 |
| EP-0299 | GET | `/api/workspaces/{slug}/projects/{project_id}/views/` | App | ViewEndpoints.ListProjectViewsQuery | project.view.read | I3 | CE-LV-047 |
| EP-0300 | POST | `/api/workspaces/{slug}/projects/{project_id}/views/` | App | ViewEndpoints.CreateProjectViewCommand | project.view.create | I3 | CE-LV-048, CE-LV-011 |
| EP-0301 | GET | `/api/workspaces/{slug}/projects/{project_id}/views/{pk}/` | App | ViewEndpoints.GetProjectViewQuery | project.view.read | I3 | CE-LV-051 |
| EP-0302 | PATCH | `/api/workspaces/{slug}/projects/{project_id}/views/{pk}/` | App | ViewEndpoints.UpdateProjectViewCommand | project.view.update | I3 | CE-LV-048, CE-LV-011 |
| EP-0303 | DELETE | `/api/workspaces/{slug}/projects/{project_id}/views/{pk}/` | App | ViewEndpoints.DeleteProjectViewCommand | project.view.delete | I3 | CE-LV-049 |
| EP-0305 | POST | `/api/workspaces/{slug}/views/` | App | ViewEndpoints.CreateWorkspaceViewCommand | workspace.view.create | I3 | CE-LV-053, CE-LV-011 |
| EP-0307 | PATCH | `/api/workspaces/{slug}/views/{pk}/` | App | ViewEndpoints.UpdateWorkspaceViewCommand | workspace.view.update | I3 | CE-LV-053, CE-LV-011 |
| EP-0308 | DELETE | `/api/workspaces/{slug}/views/{pk}/` | App | ViewEndpoints.DeleteWorkspaceViewCommand | workspace.view.delete | I3 | CE-LV-053, CE-LV-011 |

**Akzeptanzkriterien**

1. Contract: je Endpunkt dieses Pakets ≥ 1 Szenario mit Golden vom Original (Erfolg, Berechtigungsfehler, Validierungsfehler); Replay grün (L5).
2. Permission-Matrix (05 Anhang B) für alle Endpunkte dieses Pakets als L3-Test grün; Tenant-Isolation geprüft.
3. Signal-Stores strukturgleich zum MobX-Original (`store-parity-check`), Vitest je Action (L2).
4. E2E-Specs dieses Pakets grün gegen Original **und** funk. (Dual-Target, Pflichtszenarien 15 §3.9.3).
5. Visual-/DOM-/a11y-Prüfpunkte der betroffenen Screens (09 §4.14, 15 §3.10.2) innerhalb der Schwellwerte 15 §3.10.3 (Chromium); i18n-Schlüssel nur aus den Original-Locales (de/en).
6. `ce-coverage-check --ids CE-LV-011,CE-LV-047,CE-LV-048,CE-LV-049,CE-LV-050,CE-LV-051` grün (Mindestebenen 15 Anhang B).

**Testumfang**

- Pflicht-Ebenen (aus 15 Anhang B): L1, L2, L3, L5, L7, L8
- Testprojekte: `Funk.Views.Tests`
- E2E-Specs (`frontend/apps/e2e/`): `web/layouts/filters.spec.ts`, `web/views/project-views.spec.ts`

### WP-I3-003 – Workspace-Views (Übersicht, Anlage/Bearbeitung/Löschen, All work items)

| Merkmal | Wert |
|---|---|
| Inkrement | I3 |
| Typ (DoD 15 §3.15.3) | V – Vertikaler Schnitt |
| Größe | M |
| parallelisierbar | ja |
| Abhängigkeiten | WP-I3-002 |
| CE-IDs | CE-LV-052, CE-LV-053, CE-LV-054 |

**Ziel.** Workspace-Views inklusive der Standard-Views und der Detailseite „All work items“.

**Enthaltene CE-IDs**

| CE-ID | Feature | Status (15 Anh. B) | Inkrement laut 15 | Pflicht-Ebenen | Testprojekt | E2E-Spec |
|---|---|---|---|---|---|---|
| CE-LV-052 | Workspace-Views-Übersicht | übernommen | I3 | L1 L2 L3 L5 L7 L8 | Funk.Views.Tests | `web/views/workspace-views.spec.ts` |
| CE-LV-053 | Workspace-View anlegen, bearbeiten, löschen | übernommen | I3 | L1 L2 L3 L5 L7 L8 | Funk.Views.Tests | `web/views/workspace-views.spec.ts` |
| CE-LV-054 | Workspace-View-Detail (All work items) | übernommen | I3 | L1 L2 L3 L5 L7 L8 | Funk.Views.Tests | `web/views/workspace-views.spec.ts` |

**Betroffene Module/Libs in `funk.`**

- Backend: `src/modules/Views/Funk.Views`
- Frontend: `frontend/libs/web/views`

**Referenzdokumente**

- Architektur: 04 §4.6
- Architektur: 08 §4.1
- Analyse/Feature: `analysis/10a-frontend-workspace-projekt-navigation.md` §2.17
- Analyse/Feature: `analysis/10b-frontend-cycles-modules-pages-views-weitere.md` §2.5
- Analyse/Feature: `analysis/08-frontend-web-architektur.md` §2.2
- Analyse/Feature: `analysis/04-api-intern-arbeitsobjekte.md` §2.13
- Analyse/Feature: `analysis/09-frontend-arbeitsobjekte-layouts.md` §2.6
- Feature-Katalog: `features/10-ce-feature-katalog.md` (Einträge CE-LV-052, CE-LV-053, CE-LV-054)

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- Backend: `apps/api/plane/app/views/view/base.py`
- Frontend: `apps/web/app/(all)/[workspaceSlug]/(projects)/workspace-views/page.tsx`, `apps/web/components/workspace/views/default-view-list-item.tsx`, `apps/web/components/workspace/views/views-list.tsx`, `apps/web/components/workspace/views/view-list-item.tsx`, `apps/web/app/(all)/[workspaceSlug]/(projects)/workspace-views/header.tsx`, `apps/web/app/(all)/[workspaceSlug]/(projects)/workspace-views/[globalViewId]/page.tsx`, `apps/web/store/global-view.store.ts`, `apps/web/store/issue/workspace/filter.store.ts`, `apps/web/components/workspace/views/modal.tsx`, `apps/web/components/workspace/views/form.tsx`, `apps/web/components/workspace/views/delete-view-modal.tsx`, `apps/web/components/workspace/views/quick-action.tsx`, `apps/web/components/workspace/views/default-view-quick-action.tsx`, `apps/web/components/issues/issue-layouts/roots/all-issue-layout-root.tsx`, `apps/web/components/issues/issue-layouts/spreadsheet/roots/workspace-root.tsx`

**Endpunkte (Katalog 04, `architecture/_data/endpoints.json`; 4 registriert)**

| EP | Methode | Pfad | Oberfläche | Handler | Permission | Inkr. 04 | CE-IDs |
|---|---|---|---|---|---|---|---|
| EP-0150 | POST | `/api/workspaces/{slug}/workspace-views/` | App | WorkspacePreferenceEndpoints.UpdateWorkspaceViewPreferencesCommand | workspace.member_preference.update | I3 | CE-LV-052 |
| EP-0298 | GET | `/api/workspaces/{slug}/issues/` | App | ViewEndpoints.ListWorkspaceViewWorkItemsQuery | workspace.view.read | I3 | CE-LV-054 |
| EP-0304 | GET | `/api/workspaces/{slug}/views/` | App | ViewEndpoints.ListWorkspaceViewsQuery | workspace.view.read | I3 | CE-LV-052 |
| EP-0306 | GET | `/api/workspaces/{slug}/views/{pk}/` | App | ViewEndpoints.GetWorkspaceViewQuery | workspace.view.read | I3 | CE-LV-052 |

**Akzeptanzkriterien**

1. Contract: je Endpunkt dieses Pakets ≥ 1 Szenario mit Golden vom Original (Erfolg, Berechtigungsfehler, Validierungsfehler); Replay grün (L5).
2. Permission-Matrix (05 Anhang B) für alle Endpunkte dieses Pakets als L3-Test grün; Tenant-Isolation geprüft.
3. Signal-Stores strukturgleich zum MobX-Original (`store-parity-check`), Vitest je Action (L2).
4. E2E-Specs dieses Pakets grün gegen Original **und** funk. (Dual-Target, Pflichtszenarien 15 §3.9.3).
5. Visual-/DOM-/a11y-Prüfpunkte der betroffenen Screens (09 §4.14, 15 §3.10.2) innerhalb der Schwellwerte 15 §3.10.3 (Chromium); i18n-Schlüssel nur aus den Original-Locales (de/en).
6. `ce-coverage-check --ids CE-LV-052,CE-LV-053,CE-LV-054` grün (Mindestebenen 15 Anhang B).

**Testumfang**

- Pflicht-Ebenen (aus 15 Anhang B): L1, L2, L3, L5, L7, L8
- Testprojekte: `Funk.Views.Tests`
- E2E-Specs (`frontend/apps/e2e/`): `web/views/workspace-views.spec.ts`

### WP-I3-004 – Cycle-Liste mit Gruppen, Suche/Filter, Inline-Dashboard, Workspace-weite Active Cycles

| Merkmal | Wert |
|---|---|
| Inkrement | I3 |
| Typ (DoD 15 §3.15.3) | V – Vertikaler Schnitt |
| Größe | M |
| parallelisierbar | ja |
| Abhängigkeiten | WP-I3-005, WP-I3-101 |
| CE-IDs | CE-CYC-001, CE-CYC-002, CE-CYC-003, CE-CYC-004 |

**Ziel.** Cycle-Liste (aktiv, kommend, abgeschlossen), Suche und Filter, Inline-Dashboard des aktiven Cycles und workspace-weite Active Cycles (vorgezogen nach D16-ADR-14).

**Enthaltene CE-IDs**

| CE-ID | Feature | Status (15 Anh. B) | Inkrement laut 15 | Pflicht-Ebenen | Testprojekt | E2E-Spec |
|---|---|---|---|---|---|---|
| CE-CYC-001 | Cycle-Liste mit Gruppen | übernommen | I3 | L1 L2 L3 L5 L7 L8 | Funk.Cycles.Tests | `web/cycles/cycle-list.spec.ts` |
| CE-CYC-002 | Cycle-Suche und Filter | übernommen | I3 | L1 L2 L3 L5 L7 L8 | Funk.Cycles.Tests | `web/cycles/cycle-list.spec.ts` |
| CE-CYC-003 | Inline-Dashboard des aktiven Cycles | übernommen | I3 | L1 L2 L3 L5 L7 L8 | Funk.Cycles.Tests | `web/cycles/cycle-list.spec.ts` |
| CE-CYC-004 | Workspace-weite Active Cycles | übernommen | I3 | L1 L2 L3 L5 L7 L8 | Funk.Cycles.Tests | `web/cycles/cycle-list.spec.ts` |

**Betroffene Module/Libs in `funk.`**

- Backend: `src/modules/Cycles/Funk.Cycles`
- Frontend: `frontend/libs/web/cycles`

**Referenzdokumente**

- Architektur: 04 §4.7
- Architektur: 16 D16-ADR-14
- Analyse/Feature: `analysis/10b-frontend-cycles-modules-pages-views-weitere.md` §2.1, §2.2
- Analyse/Feature: `analysis/08-frontend-web-architektur.md` §2.2, §2.16
- Analyse/Feature: `analysis/04-api-intern-arbeitsobjekte.md` §2.11
- Analyse/Feature: `analysis/13b-shared-packages-i18n.md` §3.4
- Feature-Katalog: `features/10-ce-feature-katalog.md` (Einträge CE-CYC-001, CE-CYC-002, CE-CYC-003, CE-CYC-004)

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- Backend: `apps/api/plane/app/views/cycle/base.py`, `apps/api/plane/app/serializers/cycle.py`, `apps/api/plane/utils/timezone_converter.py`, `apps/api/plane/app/views/cycle/issue.py`
- Frontend: `apps/web/components/cycles/cycles-view.tsx`, `apps/web/components/cycles/list/root.tsx`, `apps/web/components/cycles/list/cycles-list-item.tsx`, `apps/web/components/cycles/list/cycle-list-group-header.tsx`, `apps/web/app/(all)/[workspaceSlug]/(projects)/projects/(detail)/[projectId]/cycles/(list)/page.tsx`, `apps/web/app/(all)/[workspaceSlug]/(projects)/projects/(detail)/[projectId]/cycles/(detail)/[cycleId]/page.tsx`, `apps/web/app/(all)/[workspaceSlug]/(projects)/projects/(detail)/[projectId]/cycles/(detail)/header.tsx`, `apps/web/store/cycle.store.ts`, `apps/web/store/issue/cycle/issue.store.ts`, `packages/constants/src/cycle.ts`, `packages/utils/src/cycle.ts`, `packages/utils/src/distribution-update.ts`, `apps/web/components/cycles/cycles-view-header.tsx`, `apps/web/components/cycles/dropdowns/filters/root.tsx`, `apps/web/components/cycles/applied-filters/root.tsx`, `apps/web/store/cycle_filter.store.ts`, `apps/web/components/cycles/active-cycle/root.tsx`, `apps/web/components/cycles/active-cycle/progress.tsx`, `apps/web/components/cycles/active-cycle/productivity.tsx`, `apps/web/components/cycles/active-cycle/cycle-stats.tsx`, `apps/web/components/cycles/active-cycle/use-cycles-details.ts`, `apps/web/components/active-cycles/workspace-active-cycles-upgrade.tsx`, `apps/web/app/(all)/[workspaceSlug]/(projects)/active-cycles/page.tsx`, `apps/web/app/(all)/[workspaceSlug]/(projects)/active-cycles/header.tsx`, `apps/web/components/workspace/upgrade-badge.tsx`

**Endpunkte (Katalog 04, `architecture/_data/endpoints.json`; 3 registriert)**

| EP | Methode | Pfad | Oberfläche | Handler | Permission | Inkr. 04 | CE-IDs |
|---|---|---|---|---|---|---|---|
| EP-0139 (verschoben) | GET | `/api/workspaces/{slug}/cycles/` | App | WorkspaceMetadataEndpoints.ListWorkspaceCyclesQuery | workspace.project_metadata.read | I3 | CE-WS-006 |
| EP-0311 | GET | `/api/workspaces/{slug}/active-cycles/` | App | CycleEndpoints.ListWorkspaceActiveCyclesQuery | workspace.cycle.read_active | I3 | CE-CYC-004 |
| EP-0314 | GET | `/api/workspaces/{slug}/projects/{project_id}/cycles/` | App | CycleEndpoints.ListCyclesQuery | project.cycle.read | I3 | CE-CYC-001, CE-CYC-002, CE-CYC-003 |

**Akzeptanzkriterien**

1. Contract: je Endpunkt dieses Pakets ≥ 1 Szenario mit Golden vom Original (Erfolg, Berechtigungsfehler, Validierungsfehler); Replay grün (L5).
2. Permission-Matrix (05 Anhang B) für alle Endpunkte dieses Pakets als L3-Test grün; Tenant-Isolation geprüft.
3. Signal-Stores strukturgleich zum MobX-Original (`store-parity-check`), Vitest je Action (L2).
4. E2E-Specs dieses Pakets grün gegen Original **und** funk. (Dual-Target, Pflichtszenarien 15 §3.9.3).
5. Visual-/DOM-/a11y-Prüfpunkte der betroffenen Screens (09 §4.14, 15 §3.10.2) innerhalb der Schwellwerte 15 §3.10.3 (Chromium); i18n-Schlüssel nur aus den Original-Locales (de/en).
6. `ce-coverage-check --ids CE-CYC-001,CE-CYC-002,CE-CYC-003,CE-CYC-004` grün (Mindestebenen 15 Anhang B).

**Testumfang**

- Pflicht-Ebenen (aus 15 Anhang B): L1, L2, L3, L5, L7, L8
- Testprojekte: `Funk.Cycles.Tests`
- E2E-Specs (`frontend/apps/e2e/`): `web/cycles/cycle-list.spec.ts`

### WP-I3-005 – Cycles anlegen/bearbeiten, Datumsüberschneidung, archivieren, löschen, Kontextmenü, Favoriten

| Merkmal | Wert |
|---|---|
| Inkrement | I3 |
| Typ (DoD 15 §3.15.3) | V – Vertikaler Schnitt |
| Größe | L |
| parallelisierbar | ja |
| Abhängigkeiten | WP-I2-999, WP-I3-201 |
| CE-IDs | CE-CYC-005, CE-CYC-006, CE-CYC-012, CE-CYC-013, CE-CYC-014, CE-CYC-015 |

**Ziel.** Cycle-CRUD mit Überschneidungsprüfung über `ICycleSchedulingPolicy`, Archiv, Löschen, Kontextmenü und Favoriten; Cycle-Events und Abschluss-Erkennung (`cycles.completion_detection`).

**Enthaltene CE-IDs**

| CE-ID | Feature | Status (15 Anh. B) | Inkrement laut 15 | Pflicht-Ebenen | Testprojekt | E2E-Spec |
|---|---|---|---|---|---|---|
| CE-CYC-005 | Cycle anlegen und bearbeiten | übernommen | I3 | L1 L2 L3 L5 L7 L8 | Funk.Cycles.Tests | `web/cycles/cycle-crud.spec.ts` |
| CE-CYC-006 | Datumsüberschneidung prüfen | übernommen | I3 | L1 L2 L3 L5 L7 L8 | Funk.Cycles.Tests | `web/cycles/cycle-crud.spec.ts` |
| CE-CYC-012 | Cycle archivieren und wiederherstellen | übernommen | I3 | L1 L2 L3 L5 L7 L8 | Funk.Cycles.Tests | `web/cycles/cycle-crud.spec.ts` |
| CE-CYC-013 | Cycle löschen | übernommen | I3 | L1 L2 L3 L5 L7 L8 | Funk.Cycles.Tests | `web/cycles/cycle-crud.spec.ts` |
| CE-CYC-014 | Cycle-Kontextmenü | übernommen | I3 | L1 L2 L3 L5 L7 L8 | Funk.Cycles.Tests | `web/cycles/cycle-crud.spec.ts` |
| CE-CYC-015 | Cycle-Favoriten | übernommen | I3 | L1 L2 L3 L5 L7 L8 | Funk.Cycles.Tests | `web/cycles/cycle-crud.spec.ts` |

**Betroffene Module/Libs in `funk.`**

- Backend: `src/modules/Cycles/Funk.Cycles`, `Funk.Cycles.Contracts`
- Backend: `tests/modules/Funk.Cycles.Tests`
- Frontend: `frontend/libs/web/cycles`

**Referenzdokumente**

- Architektur: 04 §4.7
- Architektur: 03 §3.4.6
- Architektur: 06 §3.17.4, O-D06-06
- Analyse/Feature: `analysis/10b-frontend-cycles-modules-pages-views-weitere.md` §2.1
- Analyse/Feature: `analysis/04-api-intern-arbeitsobjekte.md` §2.11
- Analyse/Feature: `analysis/02b-datenmodell-arbeitsobjekte.md` §3.9
- Feature-Katalog: `features/10-ce-feature-katalog.md` (Einträge CE-CYC-005, CE-CYC-006, CE-CYC-012, CE-CYC-013, CE-CYC-014, CE-CYC-015)

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- Backend: `apps/api/plane/app/views/cycle/base.py`, `apps/api/plane/app/serializers/cycle.py`, `apps/api/plane/utils/timezone_converter.py`, `apps/api/plane/db/models/cycle.py`, `apps/api/plane/utils/cycle_transfer_issues.py:405-431`, `apps/api/plane/app/views/cycle/issue.py:230-299`, `apps/api/plane/app/views/cycle/archive.py`
- Frontend: `apps/web/components/cycles/modal.tsx`, `apps/web/components/cycles/form.tsx`, `apps/web/services/cycle.service.ts`, `apps/web/components/cycles/archived-cycles/modal.tsx`, `apps/web/components/cycles/archived-cycles/root.tsx`, `apps/web/components/cycles/archived-cycles/view.tsx`, `apps/web/components/cycles/archived-cycles/header.tsx`, `apps/web/services/cycle_archive.service.ts`, `apps/web/components/cycles/delete-modal.tsx`, `apps/web/store/cycle.store.ts`, `apps/web/components/cycles/quick-actions.tsx`, `apps/web/components/common/quick-actions-helper.tsx`, `apps/web/components/cycles/list/cycle-list-item-action.tsx`

**Endpunkte (Katalog 04, `architecture/_data/endpoints.json`; 10 registriert)**

| EP | Methode | Pfad | Oberfläche | Handler | Permission | Inkr. 04 | CE-IDs |
|---|---|---|---|---|---|---|---|
| EP-0092 | POST | `/api/workspaces/{slug}/projects/{project_id}/user-favorite-cycles/` | App | CycleFavoriteEndpoints.FavoriteCycleCommand | project.cycle.favorite | I3 | CE-CYC-015 |
| EP-0093 | DELETE | `/api/workspaces/{slug}/projects/{project_id}/user-favorite-cycles/{cycle_id}/` | App | CycleFavoriteEndpoints.UnfavoriteCycleCommand | project.cycle.favorite | I3 | CE-CYC-015 |
| EP-0312 | GET | `/api/workspaces/{slug}/projects/{project_id}/archived-cycles/` | App | CycleEndpoints.ListArchivedCyclesQuery | project.cycle.read_archived | I3 | CE-CYC-012 |
| EP-0313 | GET | `/api/workspaces/{slug}/projects/{project_id}/archived-cycles/{pk}/` | App | CycleEndpoints.GetArchivedCycleQuery | project.cycle.read_archived | I3 | CE-CYC-012 |
| EP-0315 | POST | `/api/workspaces/{slug}/projects/{project_id}/cycles/` | App | CycleEndpoints.CreateCycleCommand | project.cycle.create | I3 | CE-CYC-005 |
| EP-0316 | POST | `/api/workspaces/{slug}/projects/{project_id}/cycles/date-check/` | App | CycleEndpoints.CheckCycleDatesQuery | project.cycle.create | I3 | CE-CYC-006 |
| EP-0318 | POST | `/api/workspaces/{slug}/projects/{project_id}/cycles/{cycle_id}/archive/` | App | CycleEndpoints.ArchiveCycleCommand | project.cycle.archive | I3 | CE-CYC-012 |
| EP-0319 | DELETE | `/api/workspaces/{slug}/projects/{project_id}/cycles/{cycle_id}/archive/` | App | CycleEndpoints.UnarchiveCycleCommand | project.cycle.unarchive | I3 | CE-CYC-012 |
| EP-0322 | PATCH | `/api/workspaces/{slug}/projects/{project_id}/cycles/{pk}/` | App | CycleEndpoints.UpdateCycleCommand | project.cycle.update | I3 | CE-CYC-005 |
| EP-0323 | DELETE | `/api/workspaces/{slug}/projects/{project_id}/cycles/{pk}/` | App | CycleEndpoints.DeleteCycleCommand | project.cycle.delete | I3 | CE-CYC-013 |

**Akzeptanzkriterien**

1. Contract: je Endpunkt dieses Pakets ≥ 1 Szenario mit Golden vom Original (Erfolg, Berechtigungsfehler, Validierungsfehler); Replay grün (L5).
2. Permission-Matrix (05 Anhang B) für alle Endpunkte dieses Pakets als L3-Test grün; Tenant-Isolation geprüft.
3. Signal-Stores strukturgleich zum MobX-Original (`store-parity-check`), Vitest je Action (L2).
4. E2E-Specs dieses Pakets grün gegen Original **und** funk. (Dual-Target, Pflichtszenarien 15 §3.9.3).
5. Visual-/DOM-/a11y-Prüfpunkte der betroffenen Screens (09 §4.14, 15 §3.10.2) innerhalb der Schwellwerte 15 §3.10.3 (Chromium); i18n-Schlüssel nur aus den Original-Locales (de/en).
6. `ce-coverage-check --ids CE-CYC-005,CE-CYC-006,CE-CYC-012,CE-CYC-013,CE-CYC-014,CE-CYC-015` grün (Mindestebenen 15 Anhang B).

**Testumfang**

- Pflicht-Ebenen (aus 15 Anhang B): L1, L2, L3, L5, L7, L8
- Testprojekte: `Funk.Cycles.Tests`
- E2E-Specs (`frontend/apps/e2e/`): `web/cycles/cycle-crud.spec.ts`

### WP-I3-006 – Cycle-Peek/Detail, Fortschritt, Verteilungen, Burndown, Anzeige je Cycle und Modul

| Merkmal | Wert |
|---|---|
| Inkrement | I3 |
| Typ (DoD 15 §3.15.3) | V – Vertikaler Schnitt |
| Größe | L |
| parallelisierbar | ja |
| Abhängigkeiten | WP-I3-005, WP-I3-101 |
| CE-IDs | CE-CYC-007, CE-CYC-008, CE-CYC-009, CE-LV-016 |

**Ziel.** Cycle-Peek und Detail-Sidebar, Fortschritt, Verteilungen und Burndown (`progress_snapshot`), Cycle-Detailseite und Anzeige-Einstellungen je Cycle und Modul.

> **Hinweis:** CE-LV-016 aus I2 hierher verschoben (plan/04 OP-PLAN-03).

**Enthaltene CE-IDs**

| CE-ID | Feature | Status (15 Anh. B) | Inkrement laut 15 | Pflicht-Ebenen | Testprojekt | E2E-Spec |
|---|---|---|---|---|---|---|
| CE-CYC-007 | Cycle-Peek und Detail-Sidebar | übernommen | I3 | L1 L2 L3 L5 L7 L8 | Funk.Cycles.Tests | `web/cycles/cycle-detail.spec.ts` |
| CE-CYC-008 | Fortschritt, Verteilungen und Burndown | übernommen | I3 | L1 L2 L3 L5 L7 L8 | Funk.Cycles.Tests | `web/cycles/cycle-detail.spec.ts` |
| CE-CYC-009 | Cycle-Detailseite | übernommen | I3 | L1 L2 L3 L5 L7 L8 | Funk.Cycles.Tests | `web/cycles/cycle-detail.spec.ts` |
| CE-LV-016 | Anzeige-Einstellungen je Cycle und Modul | übernommen | I2 | L1 L2 L3 L5 L7 L8 | Funk.WorkItems.Tests | `web/layouts/display.spec.ts` |

**Betroffene Module/Libs in `funk.`**

- Backend: `src/modules/Cycles/Funk.Cycles`
- Frontend: `frontend/libs/web/cycles`

**Referenzdokumente**

- Architektur: 04 §4.7
- Architektur: 03 §3.4.6
- Analyse/Feature: `analysis/10b-frontend-cycles-modules-pages-views-weitere.md` §2.1
- Analyse/Feature: `analysis/08-frontend-web-architektur.md` §2.2
- Analyse/Feature: `analysis/04-api-intern-arbeitsobjekte.md` §2.11
- Analyse/Feature: `analysis/06-auth-sicherheit-querschnitt.md` §2.13
- Analyse/Feature: `analysis/13b-shared-packages-i18n.md` §3.4
- Analyse/Feature: `analysis/02b-datenmodell-arbeitsobjekte.md` §2.6
- Feature-Katalog: `features/10-ce-feature-katalog.md` (Einträge CE-CYC-007, CE-CYC-008, CE-CYC-009, CE-LV-016)

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- Backend: `apps/api/plane/app/views/cycle/base.py`, `apps/api/plane/utils/analytics_plot.py`, `apps/api/plane/utils/build_chart.py`, `apps/api/plane/utils/date_utils.py`, `apps/api/plane/app/views/cycle/issue.py`, `apps/api/plane/app/views/module/base.py`, `apps/api/plane/db/models/cycle.py:130-157`, `apps/api/plane/db/models/module.py:190-217`
- Frontend: `apps/web/components/cycles/cycle-peek-overview.tsx`, `apps/web/components/cycles/analytics-sidebar/root.tsx`, `apps/web/components/cycles/analytics-sidebar/sidebar-header.tsx`, `apps/web/components/cycles/analytics-sidebar/sidebar-details.tsx`, `apps/web/components/cycles/analytics-sidebar/issue-progress.tsx`, `apps/web/components/cycles/analytics-sidebar/progress-stats.tsx`, `apps/web/app/(all)/[workspaceSlug]/(projects)/projects/(detail)/[projectId]/cycles/(list)/page.tsx`, `apps/web/app/(all)/[workspaceSlug]/(projects)/projects/(detail)/[projectId]/cycles/(detail)/[cycleId]/page.tsx`, `apps/web/app/(all)/[workspaceSlug]/(projects)/projects/(detail)/[projectId]/cycles/(detail)/header.tsx`, `apps/web/store/cycle.store.ts`, `apps/web/store/issue/cycle/issue.store.ts`, `apps/web/components/cycles/analytics-sidebar/sidebar-chart.tsx`, `apps/web/components/cycles/dropdowns/estimate-type-dropdown.tsx`, `apps/web/components/core/sidebar/progress-chart.tsx`, `packages/constants/src/cycle.ts`, `packages/utils/src/cycle.ts`, `packages/utils/src/distribution-update.ts`, `apps/web/app/(all)/[workspaceSlug]/(projects)/projects/(detail)/[projectId]/cycles/(detail)/mobile-header.tsx`

**Endpunkte (Katalog 04, `architecture/_data/endpoints.json`; 7 registriert)**

| EP | Methode | Pfad | Oberfläche | Handler | Permission | Inkr. 04 | CE-IDs |
|---|---|---|---|---|---|---|---|
| EP-0206 | GET | `/api/workspaces/{slug}/projects/{project_id}/cycles/{cycle_id}/user-properties/` | App | ProjectPreferenceEndpoints.GetCycleUserPropertiesQuery | project.member_preference.read | I3 | CE-LV-016 |
| EP-0207 | PATCH | `/api/workspaces/{slug}/projects/{project_id}/cycles/{cycle_id}/user-properties/` | App | ProjectPreferenceEndpoints.UpdateCycleUserPropertiesCommand | project.member_preference.update | I3 | CE-LV-016 |
| EP-0208 | GET | `/api/workspaces/{slug}/projects/{project_id}/modules/{module_id}/user-properties/` | App | ProjectPreferenceEndpoints.GetModuleUserPropertiesQuery | project.member_preference.read | I3 | CE-LV-016 |
| EP-0209 | PATCH | `/api/workspaces/{slug}/projects/{project_id}/modules/{module_id}/user-properties/` | App | ProjectPreferenceEndpoints.UpdateModuleUserPropertiesCommand | project.member_preference.update | I3 | CE-LV-016 |
| EP-0317 | GET | `/api/workspaces/{slug}/projects/{project_id}/cycles/{cycle_id}/analytics/` | App | CycleEndpoints.GetCycleAnalyticsQuery | project.cycle.read | I3 | CE-CYC-008 |
| EP-0320 | GET | `/api/workspaces/{slug}/projects/{project_id}/cycles/{cycle_id}/progress/` | App | CycleEndpoints.GetCycleProgressQuery | project.cycle.read | I3 | CE-CYC-008 |
| EP-0321 | GET | `/api/workspaces/{slug}/projects/{project_id}/cycles/{pk}/` | App | CycleEndpoints.GetCycleQuery | project.cycle.read_detail | I3 | CE-CYC-007, CE-CYC-009 |

**Akzeptanzkriterien**

1. Contract: je Endpunkt dieses Pakets ≥ 1 Szenario mit Golden vom Original (Erfolg, Berechtigungsfehler, Validierungsfehler); Replay grün (L5).
2. Permission-Matrix (05 Anhang B) für alle Endpunkte dieses Pakets als L3-Test grün; Tenant-Isolation geprüft.
3. Signal-Stores strukturgleich zum MobX-Original (`store-parity-check`), Vitest je Action (L2).
4. E2E-Specs dieses Pakets grün gegen Original **und** funk. (Dual-Target, Pflichtszenarien 15 §3.9.3).
5. Visual-/DOM-/a11y-Prüfpunkte der betroffenen Screens (09 §4.14, 15 §3.10.2) innerhalb der Schwellwerte 15 §3.10.3 (Chromium); i18n-Schlüssel nur aus den Original-Locales (de/en).
6. `ce-coverage-check --ids CE-CYC-007,CE-CYC-008,CE-CYC-009,CE-LV-016` grün (Mindestebenen 15 Anhang B).

**Testumfang**

- Pflicht-Ebenen (aus 15 Anhang B): L1, L2, L3, L5, L7, L8
- Testprojekte: `Funk.Cycles.Tests`, `Funk.WorkItems.Tests`
- E2E-Specs (`frontend/apps/e2e/`): `web/cycles/cycle-detail.spec.ts`, `web/layouts/display.spec.ts`

### WP-I3-007 – Work Items Cycles zuordnen, unvollständige übertragen, Cycle-Dropdown

| Merkmal | Wert |
|---|---|
| Inkrement | I3 |
| Typ (DoD 15 §3.15.3) | V – Vertikaler Schnitt |
| Größe | M |
| parallelisierbar | ja |
| Abhängigkeiten | WP-I3-005 |
| CE-IDs | CE-CYC-010, CE-CYC-011, CE-WI-025 |

**Ziel.** Zuordnung von Work Items zu Cycles, Transfer unvollständiger Work Items (State-Change-Origin `CycleTransfer`) und Cycle-Dropdown in den Work-Item-Properties.

**Enthaltene CE-IDs**

| CE-ID | Feature | Status (15 Anh. B) | Inkrement laut 15 | Pflicht-Ebenen | Testprojekt | E2E-Spec |
|---|---|---|---|---|---|---|
| CE-CYC-010 | Work Items einem Cycle zuordnen | übernommen | I3 | L1 L2 L3 L5 L7 L8 | Funk.Cycles.Tests | `web/cycles/cycle-assign-transfer.spec.ts` |
| CE-CYC-011 | Unvollständige Work Items übertragen | übernommen | I3 | L1 L2 L3 L5 L7 L8 | Funk.Cycles.Tests | `web/cycles/cycle-assign-transfer.spec.ts` |
| CE-WI-025 | Cycle-Dropdown | übernommen | I2 | L1 L2 L3 L5 L7 L8 | Funk.WorkItems.Tests | `web/work-items/properties.spec.ts` |

**Betroffene Module/Libs in `funk.`**

- Backend: `src/modules/Cycles/Funk.Cycles`
- Frontend: `frontend/libs/web/cycles`
- Frontend: `frontend/libs/web/work-items` (dropdowns)

**Referenzdokumente**

- Architektur: 04 §4.7
- Architektur: 16 §5.9
- Analyse/Feature: `analysis/04-api-intern-arbeitsobjekte.md` §2.11
- Analyse/Feature: `analysis/02b-datenmodell-arbeitsobjekte.md` §3.9
- Analyse/Feature: `analysis/10b-frontend-cycles-modules-pages-views-weitere.md` §2.1
- Analyse/Feature: `analysis/06-auth-sicherheit-querschnitt.md` §2.13
- Analyse/Feature: `analysis/09-frontend-arbeitsobjekte-layouts.md` §2.19
- Feature-Katalog: `features/10-ce-feature-katalog.md` (Einträge CE-CYC-010, CE-CYC-011, CE-WI-025)

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- Backend: `apps/api/plane/app/views/cycle/issue.py`, `apps/api/plane/db/models/cycle.py`, `apps/api/plane/utils/cycle_transfer_issues.py:405-431`, `apps/api/plane/app/views/cycle/issue.py:230-299`, `apps/api/plane/app/views/cycle/base.py`, `apps/api/plane/utils/cycle_transfer_issues.py`
- Frontend: `apps/web/store/issue/cycle/issue.store.ts`, `apps/web/components/cycles/transfer-issues-modal.tsx`, `apps/web/components/cycles/transfer-issues.tsx`, `apps/web/components/cycles/list/cycle-list-item-action.tsx`, `apps/web/components/issues/issue-layouts/roots/cycle-layout-root.tsx`, `apps/web/components/dropdowns/cycle/cycle-select.tsx`, `packages/blocks/src/property-select/cycle-select.tsx`

**Endpunkte (Katalog 04, `architecture/_data/endpoints.json`; 4 registriert)**

| EP | Methode | Pfad | Oberfläche | Handler | Permission | Inkr. 04 | CE-IDs |
|---|---|---|---|---|---|---|---|
| EP-0324 | GET | `/api/workspaces/{slug}/projects/{project_id}/cycles/{cycle_id}/cycle-issues/` | App | CycleWorkItemEndpoints.ListCycleWorkItemsQuery | project.cycle_work_item.read | I3 | CE-CYC-010 |
| EP-0325 | POST | `/api/workspaces/{slug}/projects/{project_id}/cycles/{cycle_id}/cycle-issues/` | App | CycleWorkItemEndpoints.AddCycleWorkItemsCommand | project.cycle_work_item.create | I3 | CE-CYC-010 |
| EP-0326 | DELETE | `/api/workspaces/{slug}/projects/{project_id}/cycles/{cycle_id}/cycle-issues/{issue_id}/` | App | CycleWorkItemEndpoints.RemoveCycleWorkItemCommand | project.cycle_work_item.delete | I3 | CE-CYC-010 |
| EP-0327 | POST | `/api/workspaces/{slug}/projects/{project_id}/cycles/{cycle_id}/transfer-issues/` | App | CycleWorkItemEndpoints.TransferCycleWorkItemsCommand | project.cycle_work_item.transfer | I3 | CE-CYC-011 |

**Akzeptanzkriterien**

1. Contract: je Endpunkt dieses Pakets ≥ 1 Szenario mit Golden vom Original (Erfolg, Berechtigungsfehler, Validierungsfehler); Replay grün (L5).
2. Permission-Matrix (05 Anhang B) für alle Endpunkte dieses Pakets als L3-Test grün; Tenant-Isolation geprüft.
3. Signal-Stores strukturgleich zum MobX-Original (`store-parity-check`), Vitest je Action (L2).
4. E2E-Specs dieses Pakets grün gegen Original **und** funk. (Dual-Target, Pflichtszenarien 15 §3.9.3).
5. Visual-/DOM-/a11y-Prüfpunkte der betroffenen Screens (09 §4.14, 15 §3.10.2) innerhalb der Schwellwerte 15 §3.10.3 (Chromium); i18n-Schlüssel nur aus den Original-Locales (de/en).
6. `ce-coverage-check --ids CE-CYC-010,CE-CYC-011,CE-WI-025` grün (Mindestebenen 15 Anhang B).

**Testumfang**

- Pflicht-Ebenen (aus 15 Anhang B): L1, L2, L3, L5, L7, L8
- Testprojekte: `Funk.Cycles.Tests`, `Funk.WorkItems.Tests`
- E2E-Specs (`frontend/apps/e2e/`): `web/cycles/cycle-assign-transfer.spec.ts`, `web/work-items/properties.spec.ts`

### WP-I3-008 – Modul-Übersicht in drei Layouts, Suche/Filter/Sortierung, Kontextmenü und Favoriten

| Merkmal | Wert |
|---|---|
| Inkrement | I3 |
| Typ (DoD 15 §3.15.3) | V – Vertikaler Schnitt |
| Größe | M |
| parallelisierbar | ja |
| Abhängigkeiten | WP-I3-009 |
| CE-IDs | CE-MOD-001, CE-MOD-002, CE-MOD-011 |

**Ziel.** Modul-Übersicht (Liste, Galerie, Gantt), Suche/Filter/Sortierung, Kontextmenü und Favoriten.

**Enthaltene CE-IDs**

| CE-ID | Feature | Status (15 Anh. B) | Inkrement laut 15 | Pflicht-Ebenen | Testprojekt | E2E-Spec |
|---|---|---|---|---|---|---|
| CE-MOD-001 | Modul-Übersicht in drei Layouts | übernommen | I3 | L1 L2 L3 L5 L7 L8 | Funk.ProjectModules.Tests | `web/modules/module-list.spec.ts` |
| CE-MOD-002 | Modul-Suche, Filter und Sortierung | übernommen | I3 | L1 L2 L3 L5 L7 L8 | Funk.ProjectModules.Tests | `web/modules/module-list.spec.ts` |
| CE-MOD-011 | Modul-Kontextmenü und Favoriten | übernommen | I3 | L1 L2 L3 L5 L7 L8 | Funk.ProjectModules.Tests | `web/modules/module-list.spec.ts` |

**Betroffene Module/Libs in `funk.`**

- Backend: `src/modules/ProjectModules/Funk.ProjectModules`
- Frontend: `frontend/libs/web/modules`

**Referenzdokumente**

- Architektur: 04 §4.8
- Analyse/Feature: `analysis/10b-frontend-cycles-modules-pages-views-weitere.md` §2.3
- Analyse/Feature: `analysis/08-frontend-web-architektur.md` §2.2
- Analyse/Feature: `analysis/09-frontend-arbeitsobjekte-layouts.md` §2.5
- Analyse/Feature: `analysis/13b-shared-packages-i18n.md` §2.2
- Analyse/Feature: `analysis/04-api-intern-arbeitsobjekte.md` §2.12
- Feature-Katalog: `features/10-ce-feature-katalog.md` (Einträge CE-MOD-001, CE-MOD-002, CE-MOD-011)

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- Backend: `apps/api/plane/app/views/module/base.py`, `apps/api/plane/app/serializers/module.py`
- Frontend: `apps/web/components/modules/modules-list-view.tsx`, `apps/web/components/modules/module-list-item.tsx`, `apps/web/components/modules/module-card-item.tsx`, `apps/web/components/modules/gantt-chart/modules-list-layout.tsx`, `apps/web/components/modules/gantt-chart/blocks.tsx`, `apps/web/components/modules/module-layout-icon.tsx`, `apps/web/app/(all)/[workspaceSlug]/(projects)/projects/(detail)/[projectId]/modules/(list)/page.tsx`, `apps/web/app/(all)/[workspaceSlug]/(projects)/projects/(detail)/[projectId]/modules/(detail)/[moduleId]/page.tsx`, `apps/web/store/module.store.ts`, `apps/web/store/module_filter.store.ts`, `apps/web/components/gantt-chart/sidebar/modules/sidebar.tsx`, `apps/web/components/gantt-chart/sidebar/modules/block.tsx`, `apps/web/components/gantt-chart/contexts/index.tsx`, `packages/constants/src/module.ts`, `packages/utils/src/module.ts`, `apps/web/components/modules/module-view-header.tsx`, `apps/web/components/modules/dropdowns/filters/root.tsx`, `apps/web/components/modules/dropdowns/order-by.tsx`, `apps/web/components/modules/applied-filters/root.tsx`, `apps/web/components/modules/quick-actions.tsx`, `apps/web/components/modules/module-list-item-action.tsx`, `apps/web/components/common/quick-actions-helper.tsx`

**Endpunkte (Katalog 04, `architecture/_data/endpoints.json`; 4 registriert)**

| EP | Methode | Pfad | Oberfläche | Handler | Permission | Inkr. 04 | CE-IDs |
|---|---|---|---|---|---|---|---|
| EP-0111 | POST | `/api/workspaces/{slug}/projects/{project_id}/user-favorite-modules/` | App | ModuleFavoriteEndpoints.FavoriteModuleCommand | project.module.favorite | I3 | CE-MOD-011 |
| EP-0112 | DELETE | `/api/workspaces/{slug}/projects/{project_id}/user-favorite-modules/{module_id}/` | App | ModuleFavoriteEndpoints.UnfavoriteModuleCommand | project.module.favorite | I3 | CE-MOD-011 |
| EP-0142 (verschoben) | GET | `/api/workspaces/{slug}/modules/` | App | WorkspaceMetadataEndpoints.ListWorkspaceModulesQuery | workspace.project_metadata.read | I3 | CE-WS-006 |
| EP-0339 | GET | `/api/workspaces/{slug}/projects/{project_id}/modules/` | App | ModuleEndpoints.ListModulesQuery | project.module.read | I3 | CE-MOD-001, CE-MOD-002 |

**Akzeptanzkriterien**

1. Contract: je Endpunkt dieses Pakets ≥ 1 Szenario mit Golden vom Original (Erfolg, Berechtigungsfehler, Validierungsfehler); Replay grün (L5).
2. Permission-Matrix (05 Anhang B) für alle Endpunkte dieses Pakets als L3-Test grün; Tenant-Isolation geprüft.
3. Signal-Stores strukturgleich zum MobX-Original (`store-parity-check`), Vitest je Action (L2).
4. E2E-Specs dieses Pakets grün gegen Original **und** funk. (Dual-Target, Pflichtszenarien 15 §3.9.3).
5. Visual-/DOM-/a11y-Prüfpunkte der betroffenen Screens (09 §4.14, 15 §3.10.2) innerhalb der Schwellwerte 15 §3.10.3 (Chromium); i18n-Schlüssel nur aus den Original-Locales (de/en).
6. `ce-coverage-check --ids CE-MOD-001,CE-MOD-002,CE-MOD-011` grün (Mindestebenen 15 Anhang B).

**Testumfang**

- Pflicht-Ebenen (aus 15 Anhang B): L1, L2, L3, L5, L7, L8
- Testprojekte: `Funk.ProjectModules.Tests`
- E2E-Specs (`frontend/apps/e2e/`): `web/modules/module-list.spec.ts`

### WP-I3-009 – Module anlegen/bearbeiten, Status, Links, Sidebar, archivieren, löschen

| Merkmal | Wert |
|---|---|
| Inkrement | I3 |
| Typ (DoD 15 §3.15.3) | V – Vertikaler Schnitt |
| Größe | L |
| parallelisierbar | ja |
| Abhängigkeiten | WP-I2-999, WP-I3-201 |
| CE-IDs | CE-MOD-003, CE-MOD-004, CE-MOD-005, CE-MOD-006, CE-MOD-009, CE-MOD-010 |

**Ziel.** Modul-CRUD mit Status, Links, Sidebar (Lead, Mitglieder, Fortschritt), Archiv und Löschen.

**Enthaltene CE-IDs**

| CE-ID | Feature | Status (15 Anh. B) | Inkrement laut 15 | Pflicht-Ebenen | Testprojekt | E2E-Spec |
|---|---|---|---|---|---|---|
| CE-MOD-003 | Modul anlegen und bearbeiten | übernommen | I3 | L1 L2 L3 L5 L7 L8 | Funk.ProjectModules.Tests | `web/modules/module-crud.spec.ts` |
| CE-MOD-004 | Modul-Status | übernommen | I3 | L1 L2 L3 L5 L7 L8 | Funk.ProjectModules.Tests | `web/modules/module-crud.spec.ts` |
| CE-MOD-005 | Modul-Links | übernommen | I3 | L1 L2 L3 L5 L7 L8 | Funk.ProjectModules.Tests | `web/modules/module-crud.spec.ts` |
| CE-MOD-006 | Modul-Sidebar mit Lead, Mitgliedern und Fortschritt | übernommen | I3 | L1 L2 L3 L5 L7 L8 | Funk.ProjectModules.Tests | `web/modules/module-crud.spec.ts` |
| CE-MOD-009 | Modul archivieren und wiederherstellen | übernommen | I3 | L1 L2 L3 L5 L7 L8 | Funk.ProjectModules.Tests | `web/modules/module-crud.spec.ts` |
| CE-MOD-010 | Modul löschen | übernommen | I3 | L1 L2 L3 L5 L7 L8 | Funk.ProjectModules.Tests | `web/modules/module-crud.spec.ts` |

**Betroffene Module/Libs in `funk.`**

- Backend: `src/modules/ProjectModules/Funk.ProjectModules`, `Funk.ProjectModules.Contracts`
- Backend: `tests/modules/Funk.ProjectModules.Tests`
- Frontend: `frontend/libs/web/modules`

**Referenzdokumente**

- Architektur: 04 §4.8
- Architektur: 03 §3.4.7
- Analyse/Feature: `analysis/10b-frontend-cycles-modules-pages-views-weitere.md` §2.3
- Analyse/Feature: `analysis/04-api-intern-arbeitsobjekte.md` §2.12
- Analyse/Feature: `analysis/02b-datenmodell-arbeitsobjekte.md` §2.5
- Analyse/Feature: `analysis/13b-shared-packages-i18n.md` §2.2
- Feature-Katalog: `features/10-ce-feature-katalog.md` (Einträge CE-MOD-003, CE-MOD-004, CE-MOD-005, CE-MOD-006, CE-MOD-009, CE-MOD-010)

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- Backend: `apps/api/plane/app/views/module/base.py`, `apps/api/plane/app/serializers/module.py`, `apps/api/plane/db/models/module.py`, `apps/api/plane/app/views/module/archive.py`
- Frontend: `apps/web/components/modules/modal.tsx`, `apps/web/components/modules/form.tsx`, `apps/web/components/modules/module-status-dropdown.tsx`, `apps/web/components/modules/select/status.tsx`, `packages/constants/src/module.ts`, `packages/utils/src/module.ts`, `apps/web/components/modules/links/create-update-modal.tsx`, `apps/web/components/modules/links/list.tsx`, `apps/web/components/modules/links/list-item.tsx`, `apps/web/components/modules/module-peek-overview.tsx`, `apps/web/components/modules/analytics-sidebar/root.tsx`, `apps/web/components/modules/analytics-sidebar/issue-progress.tsx`, `apps/web/components/modules/analytics-sidebar/progress-stats.tsx`, `apps/web/components/modules/archived-modules/modal.tsx`, `apps/web/components/modules/archived-modules/root.tsx`, `apps/web/components/modules/archived-modules/view.tsx`, `apps/web/components/modules/delete-module-modal.tsx`, `apps/web/services/module_archive.service.ts`

**Endpunkte (Katalog 04, `architecture/_data/endpoints.json`; 13 registriert)**

| EP | Methode | Pfad | Oberfläche | Handler | Permission | Inkr. 04 | CE-IDs |
|---|---|---|---|---|---|---|---|
| EP-0337 | GET | `/api/workspaces/{slug}/projects/{project_id}/archived-modules/` | App | ModuleEndpoints.ListArchivedModulesQuery | project.module.read_archived | I3 | CE-MOD-009 |
| EP-0338 | GET | `/api/workspaces/{slug}/projects/{project_id}/archived-modules/{pk}/` | App | ModuleEndpoints.GetArchivedModuleQuery | project.module.read_archived | I3 | CE-MOD-009 |
| EP-0340 | POST | `/api/workspaces/{slug}/projects/{project_id}/modules/` | App | ModuleEndpoints.CreateModuleCommand | project.module.create | I3 | CE-MOD-003 |
| EP-0341 | POST | `/api/workspaces/{slug}/projects/{project_id}/modules/{module_id}/archive/` | App | ModuleEndpoints.ArchiveModuleCommand | project.module.archive | I3 | CE-MOD-009 |
| EP-0342 | DELETE | `/api/workspaces/{slug}/projects/{project_id}/modules/{module_id}/archive/` | App | ModuleEndpoints.UnarchiveModuleCommand | project.module.unarchive | I3 | CE-MOD-009 |
| EP-0343 | GET | `/api/workspaces/{slug}/projects/{project_id}/modules/{pk}/` | App | ModuleEndpoints.GetModuleQuery | project.module.read_detail | I3 | CE-MOD-006, CE-MOD-007 |
| EP-0344 | PATCH | `/api/workspaces/{slug}/projects/{project_id}/modules/{pk}/` | App | ModuleEndpoints.UpdateModuleCommand | project.module.update | I3 | CE-MOD-003, CE-MOD-004 |
| EP-0345 | DELETE | `/api/workspaces/{slug}/projects/{project_id}/modules/{pk}/` | App | ModuleEndpoints.DeleteModuleCommand | project.module.delete | I3 | CE-MOD-010 |
| EP-0346 | GET | `/api/workspaces/{slug}/projects/{project_id}/modules/{module_id}/module-links/` | App | ModuleLinkEndpoints.ListModuleLinksQuery | project.module_link.read | I3 | CE-MOD-005 |
| EP-0347 | POST | `/api/workspaces/{slug}/projects/{project_id}/modules/{module_id}/module-links/` | App | ModuleLinkEndpoints.CreateModuleLinkCommand | project.module_link.create | I3 | CE-MOD-005 |
| EP-0348 | GET | `/api/workspaces/{slug}/projects/{project_id}/modules/{module_id}/module-links/{pk}/` | App | ModuleLinkEndpoints.GetModuleLinkQuery | project.module_link.read | I3 | CE-MOD-005 |
| EP-0349 | PATCH | `/api/workspaces/{slug}/projects/{project_id}/modules/{module_id}/module-links/{pk}/` | App | ModuleLinkEndpoints.UpdateModuleLinkCommand | project.module_link.update | I3 | CE-MOD-005 |
| EP-0350 | DELETE | `/api/workspaces/{slug}/projects/{project_id}/modules/{module_id}/module-links/{pk}/` | App | ModuleLinkEndpoints.DeleteModuleLinkCommand | project.module_link.delete | I3 | CE-MOD-005 |

**Akzeptanzkriterien**

1. Contract: je Endpunkt dieses Pakets ≥ 1 Szenario mit Golden vom Original (Erfolg, Berechtigungsfehler, Validierungsfehler); Replay grün (L5).
2. Permission-Matrix (05 Anhang B) für alle Endpunkte dieses Pakets als L3-Test grün; Tenant-Isolation geprüft.
3. Signal-Stores strukturgleich zum MobX-Original (`store-parity-check`), Vitest je Action (L2).
4. E2E-Specs dieses Pakets grün gegen Original **und** funk. (Dual-Target, Pflichtszenarien 15 §3.9.3).
5. Visual-/DOM-/a11y-Prüfpunkte der betroffenen Screens (09 §4.14, 15 §3.10.2) innerhalb der Schwellwerte 15 §3.10.3 (Chromium); i18n-Schlüssel nur aus den Original-Locales (de/en).
6. `ce-coverage-check --ids CE-MOD-003,CE-MOD-004,CE-MOD-005,CE-MOD-006,CE-MOD-009,CE-MOD-010` grün (Mindestebenen 15 Anhang B).

**Testumfang**

- Pflicht-Ebenen (aus 15 Anhang B): L1, L2, L3, L5, L7, L8
- Testprojekte: `Funk.ProjectModules.Tests`
- E2E-Specs (`frontend/apps/e2e/`): `web/modules/module-crud.spec.ts`

### WP-I3-010 – Modul-Detailseite, Work Items zuordnen, Module-Dropdown

| Merkmal | Wert |
|---|---|
| Inkrement | I3 |
| Typ (DoD 15 §3.15.3) | V – Vertikaler Schnitt |
| Größe | M |
| parallelisierbar | ja |
| Abhängigkeiten | WP-I3-009, WP-I3-101 |
| CE-IDs | CE-MOD-007, CE-MOD-008, CE-WI-026 |

**Ziel.** Modul-Detailseite mit Work-Item-Layouts, Zuordnung von Work Items und Module-Dropdown in den Properties.

**Enthaltene CE-IDs**

| CE-ID | Feature | Status (15 Anh. B) | Inkrement laut 15 | Pflicht-Ebenen | Testprojekt | E2E-Spec |
|---|---|---|---|---|---|---|
| CE-MOD-007 | Modul-Detailseite | übernommen | I3 | L1 L2 L3 L5 L7 L8 | Funk.ProjectModules.Tests | `web/modules/module-detail.spec.ts` |
| CE-MOD-008 | Work Items Modulen zuordnen | übernommen | I3 | L1 L2 L3 L5 L7 L8 | Funk.ProjectModules.Tests | `web/modules/module-detail.spec.ts` |
| CE-WI-026 | Module-Dropdown | übernommen | I2 | L1 L2 L3 L5 L7 L8 | Funk.WorkItems.Tests | `web/work-items/properties.spec.ts` |

**Betroffene Module/Libs in `funk.`**

- Backend: `src/modules/ProjectModules/Funk.ProjectModules`
- Frontend: `frontend/libs/web/modules`
- Frontend: `frontend/libs/web/work-items` (dropdowns)

**Referenzdokumente**

- Architektur: 04 §4.8
- Analyse/Feature: `analysis/10b-frontend-cycles-modules-pages-views-weitere.md` §2.3
- Analyse/Feature: `analysis/08-frontend-web-architektur.md` §2.2
- Analyse/Feature: `analysis/04-api-intern-arbeitsobjekte.md` §2.12
- Analyse/Feature: `analysis/02b-datenmodell-arbeitsobjekte.md` §2.5
- Analyse/Feature: `analysis/09-frontend-arbeitsobjekte-layouts.md` §2.19
- Feature-Katalog: `features/10-ce-feature-katalog.md` (Einträge CE-MOD-007, CE-MOD-008, CE-WI-026)

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- Backend: `apps/api/plane/app/views/module/issue.py`, `apps/api/plane/db/models/module.py`
- Frontend: `apps/web/app/(all)/[workspaceSlug]/(projects)/projects/(detail)/[projectId]/modules/(detail)/[moduleId]/page.tsx`, `apps/web/app/(all)/[workspaceSlug]/(projects)/projects/(detail)/[projectId]/modules/(detail)/header.tsx`, `apps/web/app/(all)/[workspaceSlug]/(projects)/projects/(detail)/[projectId]/modules/(detail)/mobile-header.tsx`, `apps/web/app/(all)/[workspaceSlug]/(projects)/projects/(detail)/[projectId]/modules/(list)/page.tsx`, `apps/web/store/module.store.ts`, `apps/web/store/module_filter.store.ts`, `apps/web/components/dropdowns/module/module-select.tsx`, `packages/blocks/src/property-select/module-select.tsx`

**Endpunkte (Katalog 04, `architecture/_data/endpoints.json`; 4 registriert)**

| EP | Methode | Pfad | Oberfläche | Handler | Permission | Inkr. 04 | CE-IDs |
|---|---|---|---|---|---|---|---|
| EP-0351 | POST | `/api/workspaces/{slug}/projects/{project_id}/issues/{issue_id}/modules/` | App | ModuleWorkItemEndpoints.SetWorkItemModulesCommand | project.module_work_item.create | I3 | CE-MOD-008, CE-WI-026 |
| EP-0352 | GET | `/api/workspaces/{slug}/projects/{project_id}/modules/{module_id}/issues/` | App | ModuleWorkItemEndpoints.ListModuleWorkItemsQuery | project.module_work_item.read | I3 | CE-MOD-008 |
| EP-0353 | POST | `/api/workspaces/{slug}/projects/{project_id}/modules/{module_id}/issues/` | App | ModuleWorkItemEndpoints.AddModuleWorkItemsCommand | project.module_work_item.create | I3 | CE-MOD-008 |
| EP-0354 | DELETE | `/api/workspaces/{slug}/projects/{project_id}/modules/{module_id}/issues/{issue_id}/` | App | ModuleWorkItemEndpoints.RemoveModuleWorkItemCommand | project.module_work_item.delete | I3 | CE-MOD-008 |

**Akzeptanzkriterien**

1. Contract: je Endpunkt dieses Pakets ≥ 1 Szenario mit Golden vom Original (Erfolg, Berechtigungsfehler, Validierungsfehler); Replay grün (L5).
2. Permission-Matrix (05 Anhang B) für alle Endpunkte dieses Pakets als L3-Test grün; Tenant-Isolation geprüft.
3. Signal-Stores strukturgleich zum MobX-Original (`store-parity-check`), Vitest je Action (L2).
4. E2E-Specs dieses Pakets grün gegen Original **und** funk. (Dual-Target, Pflichtszenarien 15 §3.9.3).
5. Visual-/DOM-/a11y-Prüfpunkte der betroffenen Screens (09 §4.14, 15 §3.10.2) innerhalb der Schwellwerte 15 §3.10.3 (Chromium); i18n-Schlüssel nur aus den Original-Locales (de/en).
6. `ce-coverage-check --ids CE-MOD-007,CE-MOD-008,CE-WI-026` grün (Mindestebenen 15 Anhang B).

**Testumfang**

- Pflicht-Ebenen (aus 15 Anhang B): L1, L2, L3, L5, L7, L8
- Testprojekte: `Funk.ProjectModules.Tests`, `Funk.WorkItems.Tests`
- E2E-Specs (`frontend/apps/e2e/`): `web/modules/module-detail.spec.ts`, `web/work-items/properties.spec.ts`

### WP-I3-011 – Intake: je Projekt mit Triage-State, Seite Open/Closed, Filter/Sortierung, Detail, Anlage

| Merkmal | Wert |
|---|---|
| Inkrement | I3 |
| Typ (DoD 15 §3.15.3) | V – Vertikaler Schnitt |
| Größe | L |
| parallelisierbar | ja |
| Abhängigkeiten | WP-I2-999 |
| CE-IDs | CE-INT-001, CE-INT-002, CE-INT-003, CE-INT-004, CE-INT-005 |

**Ziel.** Intake je Projekt mit Triage-State, Intake-Seite mit Tabs, Filter/Sortierung, Detail (Editor-Hüllen aus I2) und Anlage.

**Enthaltene CE-IDs**

| CE-ID | Feature | Status (15 Anh. B) | Inkrement laut 15 | Pflicht-Ebenen | Testprojekt | E2E-Spec |
|---|---|---|---|---|---|---|
| CE-INT-001 | Intake je Projekt und Triage-State | übernommen | I3 | L1 L2 L3 L5 L7 L8 | Funk.Intake.Tests | `web/intake/intake.spec.ts` |
| CE-INT-002 | Intake-Seite mit Tabs Open/Closed | übernommen | I3 | L1 L2 L3 L5 L7 L8 | Funk.Intake.Tests | `web/intake/intake.spec.ts` |
| CE-INT-003 | Intake-Filter und Sortierung | übernommen | I3 | L1 L2 L3 L5 L7 L8 | Funk.Intake.Tests | `web/intake/intake.spec.ts` |
| CE-INT-004 | Intake-Detail | übernommen | I3 | L1 L2 L3 L5 L7 L8 | Funk.Intake.Tests | `web/intake/intake.spec.ts` |
| CE-INT-005 | Intake-Eintrag anlegen | übernommen | I3 | L1 L2 L3 L5 L7 L8 | Funk.Intake.Tests | `web/intake/intake.spec.ts` |

**Betroffene Module/Libs in `funk.`**

- Backend: `src/modules/Intake/Funk.Intake`, `Funk.Intake.Contracts`
- Backend: `tests/modules/Funk.Intake.Tests`
- Frontend: `frontend/libs/web/intake`

**Referenzdokumente**

- Architektur: 04 §4.9
- Architektur: 03 §3.4.9
- Architektur: 10 §1.4 Zeile I3
- Analyse/Feature: `analysis/02b-datenmodell-arbeitsobjekte.md` §3.8
- Analyse/Feature: `analysis/04-api-intern-arbeitsobjekte.md` §2.10
- Analyse/Feature: `analysis/10b-frontend-cycles-modules-pages-views-weitere.md` §2.8
- Analyse/Feature: `analysis/08-frontend-web-architektur.md` §3.8
- Analyse/Feature: `analysis/13b-shared-packages-i18n.md` §2.2
- Analyse/Feature: `analysis/09-frontend-arbeitsobjekte-layouts.md` §2.19
- Feature-Katalog: `features/10-ce-feature-katalog.md` (Einträge CE-INT-001, CE-INT-002, CE-INT-003, CE-INT-004, CE-INT-005)

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- Backend: `apps/api/plane/db/models/intake.py`, `apps/api/plane/app/views/project/base.py:359-366`, `apps/api/plane/db/migrations/0112_auto_20251124_0603.py`, `apps/api/plane/app/views/intake/base.py:247-257`, `apps/api/plane/app/views/intake/base.py`, `apps/api/plane/app/serializers/intake.py`, `apps/api/plane/utils/timezone_converter.py`
- Frontend: `packages/types/src/inbox.ts:19-31`, `apps/web/components/inbox/sidebar/root.tsx`, `apps/web/components/inbox/sidebar/inbox-list.tsx`, `apps/web/components/inbox/sidebar/inbox-list-item.tsx`, `apps/web/app/(all)/[workspaceSlug]/(projects)/projects/(detail)/[projectId]/intake/page.tsx`, `apps/web/store/inbox/project-inbox.store.ts`, `apps/web/store/inbox/inbox-issue.store.ts`, `apps/web/components/inbox/inbox-filter/root.tsx`, `apps/web/components/inbox/inbox-filter/filters/filter-selection.tsx`, `apps/web/components/inbox/inbox-filter/sorting/order-by.tsx`, `apps/web/components/inbox/inbox-filter/applied-filters/root.tsx`, `packages/utils/src/intake.ts`, `packages/constants/src/intake.ts`, `packages/types/src/inbox.ts`, `apps/web/components/inbox/content/root.tsx`, `apps/web/components/inbox/content/issue-root.tsx`, `apps/web/components/inbox/content/issue-properties.tsx`, `apps/web/components/inbox/inbox-issue-status.tsx`, `apps/web/components/inbox/inbox-status-icon.tsx`, `apps/web/components/inbox/modals/create-modal/modal.tsx`, `apps/web/components/inbox/modals/create-modal/create-root.tsx`, `apps/web/components/inbox/modals/create-modal/issue-title.tsx`, `apps/web/components/inbox/modals/create-modal/issue-description.tsx`, `apps/web/components/inbox/modals/create-modal/issue-properties.tsx`, `apps/web/components/projects/settings/intake/header.tsx`, `apps/web/app/(all)/[workspaceSlug]/(projects)/projects/(detail)/[projectId]/intake/layout.tsx`, `apps/web/components/dropdowns/intake-state/intake-state-select.tsx`, `packages/blocks/src/property-select/intake-state-select.tsx`

**Endpunkte (Katalog 04, `architecture/_data/endpoints.json`; 17 registriert)**

| EP | Methode | Pfad | Oberfläche | Handler | Permission | Inkr. 04 | CE-IDs |
|---|---|---|---|---|---|---|---|
| EP-0215 | GET | `/api/workspaces/{slug}/projects/{project_id}/intake-state/` | App | StateEndpoints.GetIntakeStateQuery | project.state.read | I3 | CE-INT-001 |
| EP-0365 | GET | `/api/workspaces/{slug}/projects/{project_id}/inboxes/` | App | IntakeEndpoints.ListIntakesQuery | project.intake.read | I3 | CE-INT-001 |
| EP-0366 | GET | `/api/workspaces/{slug}/projects/{project_id}/inboxes/{pk}/` | App | IntakeEndpoints.GetIntakeQuery | project.intake.read | I3 | CE-INT-001 |
| EP-0367 | PATCH | `/api/workspaces/{slug}/projects/{project_id}/inboxes/{pk}/` | App | IntakeEndpoints.UpdateIntakeCommand | project.intake.update | I3 | CE-INT-001 |
| EP-0368 | DELETE | `/api/workspaces/{slug}/projects/{project_id}/inboxes/{pk}/` | App | IntakeEndpoints.DeleteIntakeCommand | project.intake.delete | I3 | CE-INT-001 |
| EP-0369 | GET | `/api/workspaces/{slug}/projects/{project_id}/intakes/` | App | IntakeEndpoints.ListIntakesQuery | project.intake.read | I3 | CE-INT-001 |
| EP-0370 | GET | `/api/workspaces/{slug}/projects/{project_id}/intakes/{pk}/` | App | IntakeEndpoints.GetIntakeQuery | project.intake.read | I3 | CE-INT-001 |
| EP-0371 | PATCH | `/api/workspaces/{slug}/projects/{project_id}/intakes/{pk}/` | App | IntakeEndpoints.UpdateIntakeCommand | project.intake.update | I3 | CE-INT-001 |
| EP-0372 | DELETE | `/api/workspaces/{slug}/projects/{project_id}/intakes/{pk}/` | App | IntakeEndpoints.DeleteIntakeCommand | project.intake.delete | I3 | CE-INT-001 |
| EP-0373 | GET | `/api/workspaces/{slug}/projects/{project_id}/inbox-issues/` | App | IntakeWorkItemEndpoints.ListIntakeWorkItemsQuery | project.intake_work_item.read | I3 | CE-INT-002, CE-INT-003 |
| EP-0374 | POST | `/api/workspaces/{slug}/projects/{project_id}/inbox-issues/` | App | IntakeWorkItemEndpoints.CreateIntakeWorkItemCommand | project.intake_work_item.create | I3 | CE-INT-005 |
| EP-0375 | GET | `/api/workspaces/{slug}/projects/{project_id}/inbox-issues/{pk}/` | App | IntakeWorkItemEndpoints.GetIntakeWorkItemQuery | project.intake_work_item.read | I3 | CE-INT-004, CE-INT-012 |
| EP-0378 | GET | `/api/workspaces/{slug}/projects/{project_id}/intake-issues/` | App | IntakeWorkItemEndpoints.ListIntakeWorkItemsQuery | project.intake_work_item.read | I3 | CE-INT-002, CE-INT-003 |
| EP-0379 | POST | `/api/workspaces/{slug}/projects/{project_id}/intake-issues/` | App | IntakeWorkItemEndpoints.CreateIntakeWorkItemCommand | project.intake_work_item.create | I3 | CE-INT-005 |
| EP-0380 | GET | `/api/workspaces/{slug}/projects/{project_id}/intake-issues/{pk}/` | App | IntakeWorkItemEndpoints.GetIntakeWorkItemQuery | project.intake_work_item.read | I3 | CE-INT-004, CE-INT-012 |
| EP-0383 | GET | `/api/workspaces/{slug}/projects/{project_id}/intake-work-items/{work_item_id}/description-versions/` | App | IntakeWorkItemEndpoints.ListIntakeDescriptionVersionsQuery | project.intake_work_item.read | I3 | CE-INT-004, CE-WI-041 |
| EP-0384 | GET | `/api/workspaces/{slug}/projects/{project_id}/intake-work-items/{work_item_id}/description-versions/{pk}/` | App | IntakeWorkItemEndpoints.GetIntakeDescriptionVersionQuery | project.intake_work_item.read | I3 | CE-INT-004, CE-WI-041 |

**Akzeptanzkriterien**

1. Contract: je Endpunkt dieses Pakets ≥ 1 Szenario mit Golden vom Original (Erfolg, Berechtigungsfehler, Validierungsfehler); Replay grün (L5).
2. Permission-Matrix (05 Anhang B) für alle Endpunkte dieses Pakets als L3-Test grün; Tenant-Isolation geprüft.
3. Signal-Stores strukturgleich zum MobX-Original (`store-parity-check`), Vitest je Action (L2).
4. E2E-Specs dieses Pakets grün gegen Original **und** funk. (Dual-Target, Pflichtszenarien 15 §3.9.3).
5. Visual-/DOM-/a11y-Prüfpunkte der betroffenen Screens (09 §4.14, 15 §3.10.2) innerhalb der Schwellwerte 15 §3.10.3 (Chromium); i18n-Schlüssel nur aus den Original-Locales (de/en).
6. `ce-coverage-check --ids CE-INT-001,CE-INT-002,CE-INT-003,CE-INT-004,CE-INT-005` grün (Mindestebenen 15 Anhang B).

**Testumfang**

- Pflicht-Ebenen (aus 15 Anhang B): L1, L2, L3, L5, L7, L8
- Testprojekte: `Funk.Intake.Tests`
- E2E-Specs (`frontend/apps/e2e/`): `web/intake/intake.spec.ts`

### WP-I3-012 – Intake-Aktionen: annehmen, ablehnen, zurückstellen, Duplikat, bearbeiten/löschen, Navigation, Benachrichtigungs-Detail

| Merkmal | Wert |
|---|---|
| Inkrement | I3 |
| Typ (DoD 15 §3.15.3) | V – Vertikaler Schnitt |
| Größe | L |
| parallelisierbar | ja |
| Abhängigkeiten | WP-I3-011 |
| CE-IDs | CE-INT-006, CE-INT-007, CE-INT-008, CE-INT-009, CE-INT-010, CE-INT-011, CE-INT-012 |

**Ziel.** Annehmen (über `IWorkItemCommands` und State-Pipeline mit Origin `Intake`), Ablehnen, Snooze mit Unsnooze-Cron, Duplikat, Bearbeiten/Löschen, Navigation und Intake-Detail in Benachrichtigungen.

**Enthaltene CE-IDs**

| CE-ID | Feature | Status (15 Anh. B) | Inkrement laut 15 | Pflicht-Ebenen | Testprojekt | E2E-Spec |
|---|---|---|---|---|---|---|
| CE-INT-006 | Intake annehmen | übernommen | I3 | L1 L2 L3 L5 L7 L8 | Funk.Intake.Tests | `web/intake/intake.spec.ts` |
| CE-INT-007 | Intake ablehnen | übernommen | I3 | L1 L2 L3 L5 L7 L8 | Funk.Intake.Tests | `web/intake/intake.spec.ts` |
| CE-INT-008 | Intake zurückstellen (Snooze) | übernommen | I3 | L1 L2 L3 L5 L7 L8 | Funk.Intake.Tests | `web/intake/intake.spec.ts` |
| CE-INT-009 | Als Duplikat markieren | übernommen | I3 | L1 L2 L3 L5 L7 L8 | Funk.Intake.Tests | `web/intake/intake.spec.ts` |
| CE-INT-010 | Intake bearbeiten und löschen | übernommen | I3 | L1 L2 L3 L5 L7 L8 | Funk.Intake.Tests | `web/intake/intake.spec.ts` |
| CE-INT-011 | Intake-Navigation | übernommen | I3 | L1 L2 L3 L5 L7 L8 | Funk.Intake.Tests | `web/intake/intake.spec.ts` |
| CE-INT-012 | Intake-Detail in Benachrichtigungen | übernommen | I3 | L1 L2 L3 L5 L7 L8 | Funk.Intake.Tests | `web/intake/intake.spec.ts` |

**Betroffene Module/Libs in `funk.`**

- Backend: `src/modules/Intake/Funk.Intake`
- Frontend: `frontend/libs/web/intake`

**Referenzdokumente**

- Architektur: 04 §4.9
- Architektur: 06 §3.17.2
- Architektur: 16 §5.16
- Analyse/Feature: `analysis/10b-frontend-cycles-modules-pages-views-weitere.md` §3.6, §2.8
- Analyse/Feature: `analysis/04-api-intern-arbeitsobjekte.md` §2.10
- Analyse/Feature: `analysis/02b-datenmodell-arbeitsobjekte.md` §3.8
- Analyse/Feature: `analysis/07-hintergrundjobs-mail-storage-webhooks.md` §3.7
- Analyse/Feature: `analysis/06-auth-sicherheit-querschnitt.md` §2.13
- Feature-Katalog: `features/10-ce-feature-katalog.md` (Einträge CE-INT-006, CE-INT-007, CE-INT-008, CE-INT-009, CE-INT-010, CE-INT-011, CE-INT-012)

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- Backend: `apps/api/plane/app/views/intake/base.py`, `apps/api/plane/app/serializers/intake.py`, `apps/api/plane/utils/timezone_converter.py`, `apps/api/plane/db/models/intake.py:100-110`, `apps/api/plane/db/models/project.py:169-227`, `apps/api/plane/bgtasks/issue_automation_task.py:151-170`, `apps/api/plane/utils/timezone_converter.py:98-112`, `apps/api/plane/bgtasks/issue_automation_task.py`, `apps/api/plane/app/views/base.py`
- Frontend: `apps/web/components/inbox/content/inbox-issue-header.tsx`, `apps/web/components/issues/issue-modal/base.tsx`, `apps/web/store/inbox/inbox-issue.store.ts`, `apps/web/components/inbox/modals/decline-issue-modal.tsx`, `apps/web/components/inbox/modals/snooze-issue-modal.tsx`, `apps/web/components/inbox/modals/select-duplicate.tsx`, `apps/web/components/inbox/modals/delete-issue-modal.tsx`, `apps/web/components/inbox/content/inbox-issue-mobile-header.tsx`, `apps/web/components/inbox/content/root.tsx`, `apps/web/components/inbox/root.tsx`

**Endpunkte (Katalog 04, `architecture/_data/endpoints.json`; 4 registriert)**

| EP | Methode | Pfad | Oberfläche | Handler | Permission | Inkr. 04 | CE-IDs |
|---|---|---|---|---|---|---|---|
| EP-0376 | PATCH | `/api/workspaces/{slug}/projects/{project_id}/inbox-issues/{pk}/` | App | IntakeWorkItemEndpoints.UpdateIntakeWorkItemCommand | project.intake_work_item.update | I3 | CE-INT-006, CE-INT-007, CE-INT-008, CE-INT-009, CE-INT-010 |
| EP-0377 | DELETE | `/api/workspaces/{slug}/projects/{project_id}/inbox-issues/{pk}/` | App | IntakeWorkItemEndpoints.DeleteIntakeWorkItemCommand | project.intake_work_item.delete | I3 | CE-INT-010 |
| EP-0381 | PATCH | `/api/workspaces/{slug}/projects/{project_id}/intake-issues/{pk}/` | App | IntakeWorkItemEndpoints.UpdateIntakeWorkItemCommand | project.intake_work_item.update | I3 | CE-INT-006, CE-INT-007, CE-INT-008, CE-INT-009, CE-INT-010 |
| EP-0382 | DELETE | `/api/workspaces/{slug}/projects/{project_id}/intake-issues/{pk}/` | App | IntakeWorkItemEndpoints.DeleteIntakeWorkItemCommand | project.intake_work_item.delete | I3 | CE-INT-010 |

**Akzeptanzkriterien**

1. Contract: je Endpunkt dieses Pakets ≥ 1 Szenario mit Golden vom Original (Erfolg, Berechtigungsfehler, Validierungsfehler); Replay grün (L5).
2. Permission-Matrix (05 Anhang B) für alle Endpunkte dieses Pakets als L3-Test grün; Tenant-Isolation geprüft.
3. Signal-Stores strukturgleich zum MobX-Original (`store-parity-check`), Vitest je Action (L2).
4. E2E-Specs dieses Pakets grün gegen Original **und** funk. (Dual-Target, Pflichtszenarien 15 §3.9.3).
5. Visual-/DOM-/a11y-Prüfpunkte der betroffenen Screens (09 §4.14, 15 §3.10.2) innerhalb der Schwellwerte 15 §3.10.3 (Chromium); i18n-Schlüssel nur aus den Original-Locales (de/en).
6. `ce-coverage-check --ids CE-INT-006,CE-INT-007,CE-INT-008,CE-INT-009,CE-INT-010,CE-INT-011,CE-INT-012` grün (Mindestebenen 15 Anhang B).

**Testumfang**

- Pflicht-Ebenen (aus 15 Anhang B): L1, L2, L3, L5, L7, L8
- Testprojekte: `Funk.Intake.Tests`
- E2E-Specs (`frontend/apps/e2e/`): `web/intake/intake.spec.ts`

### WP-I3-013 – Automationen Auto-Archive und Auto-Close

| Merkmal | Wert |
|---|---|
| Inkrement | I3 |
| Typ (DoD 15 §3.15.3) | B – Backend-only |
| Größe | M |
| parallelisierbar | ja |
| Abhängigkeiten | WP-I2-999 |
| CE-IDs | CE-PRJ-039, CE-PRJ-040 |

**Ziel.** Projekt-Einstellung und Cron `work_items.auto_archive_close` (`0 1 * * *`); Auto-Close über `IWorkItemStateChanger` (Origin `AutoClose`) mit projektbezogenem Close-State-Fallback (DEV-AUTO-001/-002).

**Enthaltene CE-IDs**

| CE-ID | Feature | Status (15 Anh. B) | Inkrement laut 15 | Pflicht-Ebenen | Testprojekt | E2E-Spec |
|---|---|---|---|---|---|---|
| CE-PRJ-039 | Auto-Archive | übernommen | I3 | L1 L2 L3 L5 L7 L8 | Funk.Projects.Tests | `web/projects/automations.spec.ts` |
| CE-PRJ-040 | Auto-Close | übernommen | I3 | L1 L2 L3 L5 L7 L8 | Funk.Projects.Tests | `web/projects/automations.spec.ts` |

**Betroffene Module/Libs in `funk.`**

- Backend: `src/modules/WorkItems/Funk.WorkItems/Application/Jobs/AutoArchiveAndCloseJob.cs`
- Frontend: `frontend/libs/web/project-settings` (automations)

**Referenzdokumente**

- Architektur: 06 §3.17.1, §5.10, D06-ADR-19
- Architektur: 17 ABG-056
- Analyse/Feature: `analysis/10b-frontend-cycles-modules-pages-views-weitere.md` §2.15, §3.13
- Analyse/Feature: `analysis/02a-datenmodell-kern.md` §2.3
- Analyse/Feature: `analysis/02b-datenmodell-arbeitsobjekte.md` §3.13
- Analyse/Feature: `analysis/07-hintergrundjobs-mail-storage-webhooks.md` §3.7
- Analyse/Feature: `analysis/08-frontend-web-architektur.md` §2.2
- Feature-Katalog: `features/10-ce-feature-katalog.md` (Einträge CE-PRJ-039, CE-PRJ-040)

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- Backend: `apps/api/plane/db/models/project.py`, `apps/api/plane/celery.py`, `apps/api/plane/db/models/issue.py:160`, `apps/api/plane/bgtasks/issue_automation_task.py:26-148`, `apps/api/plane/bgtasks/issue_automation_task.py`
- Frontend: `apps/web/components/automation/auto-archive-automation.tsx`, `apps/web/components/automation/select-month-modal.tsx`, `apps/web/app/(all)/[workspaceSlug]/(settings)/settings/projects/[projectId]/automations/page.tsx`, `apps/web/app/(all)/[workspaceSlug]/(settings)/settings/projects/layout.tsx`, `apps/web/app/(all)/[workspaceSlug]/(settings)/settings/projects/[projectId]/layout.tsx`, `apps/web/app/(all)/[workspaceSlug]/(settings)/settings/projects/[projectId]/page.tsx`, `apps/web/app/(all)/[workspaceSlug]/(settings)/settings/projects/[projectId]/features/cycles/page.tsx`, `apps/web/app/(all)/[workspaceSlug]/(settings)/settings/projects/[projectId]/states/page.tsx`, `apps/web/app/(all)/[workspaceSlug]/(settings)/settings/projects/[projectId]/labels/page.tsx`, `apps/web/app/(all)/[workspaceSlug]/(settings)/settings/projects/[projectId]/estimates/page.tsx`, `packages/constants/src/settings/project.ts`, `apps/web/components/automation/auto-close-automation.tsx`

**Akzeptanzkriterien**

1. Contract-Szenarien mit Original-Golden für alle HTTP-Endpunkte dieses Pakets; Replay grün.
2. Job-/Consumer-Tests: Idempotenz (Inbox), Retry/Backoff, Zeitsteuerung mit `FixedClock`; neue Ereignistypen im Event-Katalog-Snapshot.
3. Bei Cron-Jobs: Registrierung in `CronRegistrationTests` mit Original-Zeit (UTC).
4. `ce-coverage-check --ids CE-PRJ-039,CE-PRJ-040` grün (Mindestebenen 15 Anhang B).

**Testumfang**

- Pflicht-Ebenen (aus 15 Anhang B): L1, L2, L3, L5, L7, L8
- Testprojekte: `Funk.Projects.Tests`
- E2E-Specs (`frontend/apps/e2e/`): `web/projects/automations.spec.ts`

### WP-I3-101 – Chart-Bausteine (Bar, Pie, Area, Line, Radar, TreeMap, Burndown) und Farbpaletten

| Merkmal | Wert |
|---|---|
| Inkrement | I3 |
| Typ (DoD 15 §3.15.3) | F – Frontend-only |
| Größe | M |
| parallelisierbar | ja |
| Abhängigkeiten | WP-I2-999, WP-I0-906 |
| CE-IDs | CE-I18N-022 |

**Ziel.** Die Diagramm-Bausteine aus `packages/blocks/src/charts` in D3 + Angular-SVG nach dem Ergebnis von S6, mit Farbpaletten, Tooltip und Legende.

**Enthaltene CE-IDs**

| CE-ID | Feature | Status (15 Anh. B) | Inkrement laut 15 | Pflicht-Ebenen | Testprojekt | E2E-Spec |
|---|---|---|---|---|---|---|
| CE-I18N-022 | Diagramm-Bausteine und Farbpaletten | übernommen | I0…I3 | L2 L7 L8 | Frontend-only | `gallery/design-system.spec.ts` |

**Betroffene Module/Libs in `funk.`**

- Frontend: `frontend/libs/shared/blocks/charts/{area,bar,line,pie,radar,tree-map}`

**Referenzdokumente**

- Architektur: 09 §3.12, §4.7
- Architektur: 01 §9 S6
- Analyse/Feature: `analysis/13a-designsystem-ui-tokens.md` §2.26
- Analyse/Feature: `analysis/13b-shared-packages-i18n.md` §2.2
- Feature-Katalog: `features/10-ce-feature-katalog.md` (Einträge CE-I18N-022)

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- Frontend: `packages/blocks/src/charts`, `packages/constants/src/chart.ts`, `packages/constants/src/analytics/common.ts`, `packages/constants/src/graph.ts`

**Akzeptanzkriterien**

1. Galerie-Visual je Diagrammtyp ≤ 0,5 % (hell/dunkel).
2. Galerie-Eintrag mit allen Varianten/Zuständen; DOM-Vertrag = Referenz-Galerie; Visual in allen Themes (Chromium).
3. Tastatur/Fokus (AX3/AX4) wie Original; portierte `packages/blocks`-Tests grün (falls vorhanden).
4. `ce-coverage-check --ids CE-I18N-022` grün (Mindestebenen 15 Anhang B).

**Testumfang**

- Pflicht-Ebenen (aus 15 Anhang B): L2, L7, L8
- Testprojekte: `Frontend-only`
- E2E-Specs (`frontend/apps/e2e/`): `gallery/design-system.spec.ts`

### WP-I3-201 – Erweiterungspunkte Planung: ICycleSchedulingPolicy, CYCLE_FLAGS, ENTITY_QUICK_ACTIONS

| Merkmal | Wert |
|---|---|
| Inkrement | I3 |
| Typ (DoD 15 §3.15.3) | X – Erweiterungspunkt 🧱 |
| Größe | S |
| parallelisierbar | nein |
| Abhängigkeiten | WP-I2-999 |
| CE-IDs | – (keine; Erweiterungspunkt) |
| Andockstelle | 16 §3.3.0 E-14 (I3-Teil), E-15; 16 §4.6 (Träger CE-CYC-002…013, CE-MOD-011, CE-LV-050) |

**Ziel.** `ICycleSchedulingPolicy` (E-15, CE: keine Überschneidung), Token `CYCLE_FLAGS` (`parallelCycles: false`) und `ENTITY_QUICK_ACTIONS` (E-14, Quick Actions für cycle/module/view/layout/intake-header).

**Betroffene Module/Libs in `funk.`**

- Backend: `src/modules/Cycles/Funk.Cycles.Contracts/ICycleSchedulingPolicy.cs`
- Frontend: `frontend/libs/web/extensions/src/{cycles,quick-actions}.ts`

**Referenzdokumente**

- Architektur: 16 §5.15, §3.3.0 E-14/E-15

**Akzeptanzkriterien**

1. Fake-Policy erlaubt parallele Cycles ohne CE-Änderung; Fake-Quick-Action erscheint im Cycle-Menü (Typ X).
2. Contract (Interface/Schema/Token) + CE-Default-Implementierung; Eintrag in `tests/extension-points.yaml`.
3. Test „CE-Default = Original-Verhalten“ (Contract-Replay unverändert grün).
4. Test mit Fake-Erweiterung aus `Funk.BuildingBlocks.Testing/Extensions` bzw. `provideFakeExtensions()` beweist Erweiterbarkeit ohne CE-Änderung (DoD Typ X).

**Testumfang**

- Typ-X-Tests (CE-Default unverändert, Fake-Erweiterung wirkt ohne CE-Änderung), L0-Inventarabgleich `ExtensionPointInventoryTests`/`extension-registry-check`.

### WP-I3-999 – Abnahme I3 – Planung (G5)

| Merkmal | Wert |
|---|---|
| Inkrement | I3 |
| Typ (DoD 15 §3.15.3) | A – Inkrement-Abnahme |
| Größe | S |
| parallelisierbar | nein |
| Abhängigkeiten | WP-I3-001, WP-I3-002, WP-I3-003, WP-I3-004, WP-I3-005, WP-I3-006, WP-I3-007, WP-I3-008, WP-I3-009, WP-I3-010, WP-I3-011, WP-I3-012, WP-I3-013, WP-I3-101, WP-I3-201 |
| CE-IDs | – (keine; Baustein/Spike/Abnahme) |

**Ziel.** Inkrement-Abnahme I3 nach G5 und Meilenstein M3.

**Referenzdokumente**

- Architektur: plan/01-roadmap-ce.md §4 (M3)
- Architektur: 15 §3.16 Zeile I3

**Akzeptanzkriterien**

1. Alle Abnahmekriterien M3 erfüllt; `docs/acceptance/I3.md` generiert.
2. G5 `--inc <In> --strict` grün: `ce-coverage-check`, `original-test-ledger`, Parity-Report (0 ungenehmigte Abweichungen, Endpunkt-Abdeckung des Inkrements 100 %), Visual/a11y, Lastziele, Security-Report.
3. Demo-Video der Kern-Flows (`--video on`) und Abnahmebericht `docs/acceptance/<In>.md`; fachliche Abnahme durch den Auftraggeber.

**Testumfang**

- G5 `--inc I3`.

## 4.5 Inkrement I4

### WP-I4-001 – Page-Liste mit Tabs, Suche/Filter/Sortierung, Anlage, Favoriten

| Merkmal | Wert |
|---|---|
| Inkrement | I4 |
| Typ (DoD 15 §3.15.3) | V – Vertikaler Schnitt |
| Größe | M |
| parallelisierbar | nein |
| Abhängigkeiten | WP-I3-999, WP-I4-201 |
| CE-IDs | CE-PAGE-001, CE-PAGE-002, CE-PAGE-003, CE-PAGE-010 |

**Ziel.** Page-Liste (öffentlich, privat, archiviert), Suche, Filter, Sortierung, Page anlegen und favorisieren.

**Enthaltene CE-IDs**

| CE-ID | Feature | Status (15 Anh. B) | Inkrement laut 15 | Pflicht-Ebenen | Testprojekt | E2E-Spec |
|---|---|---|---|---|---|---|
| CE-PAGE-001 | Page-Liste mit Tabs | übernommen | I4 | L1 L2 L3 L5 L7 L8 | Funk.Pages.Tests | `web/pages/page-list.spec.ts` |
| CE-PAGE-002 | Page-Suche, Filter und Sortierung | übernommen | I4 | L1 L2 L3 L5 L7 L8 | Funk.Pages.Tests | `web/pages/page-list.spec.ts` |
| CE-PAGE-003 | Page anlegen | übernommen | I4 | L1 L2 L3 L5 L7 L8 | Funk.Pages.Tests | `web/pages/page-list.spec.ts` |
| CE-PAGE-010 | Page favorisieren | übernommen | I4 | L1 L2 L3 L5 L7 L8 | Funk.Pages.Tests | `web/pages/page-list.spec.ts` |

**Betroffene Module/Libs in `funk.`**

- Backend: `src/modules/Pages/Funk.Pages`, `Funk.Pages.Contracts`
- Backend: `tests/modules/Funk.Pages.Tests`
- Frontend: `frontend/libs/web/pages`

**Referenzdokumente**

- Architektur: 04 §4.10
- Architektur: 03 §3.4.10
- Analyse/Feature: `analysis/10b-frontend-cycles-modules-pages-views-weitere.md` §2.4
- Analyse/Feature: `analysis/04-api-intern-arbeitsobjekte.md` §2.14
- Analyse/Feature: `analysis/08-frontend-web-architektur.md` §3.7
- Analyse/Feature: `analysis/13b-shared-packages-i18n.md` §2.4
- Feature-Katalog: `features/10-ce-feature-katalog.md` (Einträge CE-PAGE-001, CE-PAGE-002, CE-PAGE-003, CE-PAGE-010)

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- Backend: `apps/api/plane/app/views/page/base.py`, `apps/api/plane/app/serializers/page.py`, `apps/api/plane/app/permissions/page.py`, `apps/api/plane/bgtasks/copy_s3_object.py`
- Frontend: `apps/web/components/pages/pages-list-view.tsx`, `apps/web/components/pages/pages-list-main-content.tsx`, `apps/web/components/pages/list/root.tsx`, `apps/web/components/pages/list/block.tsx`, `apps/web/components/pages/list/block-item-action.tsx`, `apps/web/components/pages/list/tab-navigation.tsx`, `apps/web/app/(all)/[workspaceSlug]/(projects)/projects/(detail)/[projectId]/pages/(list)/page.tsx`, `apps/web/app/(all)/[workspaceSlug]/(projects)/projects/(detail)/[projectId]/pages/(detail)/[pageId]/page.tsx`, `apps/web/store/pages/base-page.ts`, `apps/web/store/pages/project-page.ts`, `apps/web/hooks/use-page-fallback.ts`, `apps/web/hooks/use-realtime-page-events.tsx`, `packages/utils/src/page.ts`, `packages/utils/src/project-views.ts`, `packages/constants/src/views.ts`, `packages/constants/src/page.ts`, `apps/web/components/pages/list/search-input.tsx`, `apps/web/components/pages/list/filters/root.tsx`, `apps/web/components/pages/list/order-by.tsx`, `apps/web/components/pages/list/applied-filters/root.tsx`, `apps/web/hooks/use-page-filters.ts`, `apps/web/app/(all)/[workspaceSlug]/(projects)/projects/(detail)/[projectId]/pages/(list)/header.tsx`, `apps/web/components/pages/modals/create-page-modal.tsx`, `apps/web/components/pages/modals/page-form.tsx`

**Endpunkte (Katalog 04, `architecture/_data/endpoints.json`; 5 registriert)**

| EP | Methode | Pfad | Oberfläche | Handler | Permission | Inkr. 04 | CE-IDs |
|---|---|---|---|---|---|---|---|
| EP-0116 | POST | `/api/workspaces/{slug}/projects/{project_id}/favorite-pages/{page_id}/` | App | PageFavoriteEndpoints.FavoritePageCommand | project.page.favorite | I4 | CE-PAGE-010 |
| EP-0117 | DELETE | `/api/workspaces/{slug}/projects/{project_id}/favorite-pages/{page_id}/` | App | PageFavoriteEndpoints.UnfavoritePageCommand | project.page.favorite | I4 | CE-PAGE-010 |
| EP-0394 | GET | `/api/workspaces/{slug}/projects/{project_id}/pages-summary/` | App | PageEndpoints.GetPagesSummaryQuery | project.page.read | I4 | CE-PAGE-001 |
| EP-0395 | GET | `/api/workspaces/{slug}/projects/{project_id}/pages/` | App | PageEndpoints.ListPagesQuery | project.page.read | I4 | CE-PAGE-001, CE-PAGE-002 |
| EP-0396 | POST | `/api/workspaces/{slug}/projects/{project_id}/pages/` | App | PageEndpoints.CreatePageCommand | project.page.create | I4 | CE-PAGE-003, CE-PAGE-012 |

**Akzeptanzkriterien**

1. Contract: je Endpunkt dieses Pakets ≥ 1 Szenario mit Golden vom Original (Erfolg, Berechtigungsfehler, Validierungsfehler); Replay grün (L5).
2. Permission-Matrix (05 Anhang B) für alle Endpunkte dieses Pakets als L3-Test grün; Tenant-Isolation geprüft.
3. Signal-Stores strukturgleich zum MobX-Original (`store-parity-check`), Vitest je Action (L2).
4. E2E-Specs dieses Pakets grün gegen Original **und** funk. (Dual-Target, Pflichtszenarien 15 §3.9.3).
5. Visual-/DOM-/a11y-Prüfpunkte der betroffenen Screens (09 §4.14, 15 §3.10.2) innerhalb der Schwellwerte 15 §3.10.3 (Chromium); i18n-Schlüssel nur aus den Original-Locales (de/en).
6. `ce-coverage-check --ids CE-PAGE-001,CE-PAGE-002,CE-PAGE-003,CE-PAGE-010` grün (Mindestebenen 15 Anhang B).

**Testumfang**

- Pflicht-Ebenen (aus 15 Anhang B): L1, L2, L3, L5, L7, L8
- Testprojekte: `Funk.Pages.Tests`
- E2E-Specs (`frontend/apps/e2e/`): `web/pages/page-list.spec.ts`

### WP-I4-002 – Page-Aktionen: Daten/Detail, sperren, Zugriff, archivieren, löschen, duplizieren, Referenzprotokoll

| Merkmal | Wert |
|---|---|
| Inkrement | I4 |
| Typ (DoD 15 §3.15.3) | V – Vertikaler Schnitt |
| Größe | L |
| parallelisierbar | ja |
| Abhängigkeiten | WP-I4-001 |
| CE-IDs | CE-PAGE-004, CE-PAGE-005, CE-PAGE-006, CE-PAGE-007, CE-PAGE-008, CE-PAGE-009, CE-PAGE-012 |

**Ziel.** Page-Detail, Sperren/Entsperren, Zugriff öffentlich/privat (Page-Zugriffsregel 05 §3.13.5), Archivieren/Wiederherstellen, Löschen, Duplizieren mit Asset-Umschreibung und PageLog (synchron über `PageReferenceIndexer`).

**Enthaltene CE-IDs**

| CE-ID | Feature | Status (15 Anh. B) | Inkrement laut 15 | Pflicht-Ebenen | Testprojekt | E2E-Spec |
|---|---|---|---|---|---|---|
| CE-PAGE-004 | Page-Daten und Detail | übernommen | I4 | L1 L2 L3 L5 L7 L8 | Funk.Pages.Tests | `web/pages/page-actions.spec.ts` |
| CE-PAGE-005 | Page sperren und entsperren | übernommen | I4 | L1 L2 L3 L5 L7 L8 | Funk.Pages.Tests | `web/pages/page-actions.spec.ts` |
| CE-PAGE-006 | Page-Zugriff öffentlich/privat | übernommen | I4 | L1 L2 L3 L5 L7 L8 | Funk.Pages.Tests | `web/pages/page-actions.spec.ts` |
| CE-PAGE-007 | Page archivieren und wiederherstellen | übernommen | I4 | L1 L2 L3 L5 L7 L8 | Funk.Pages.Tests | `web/pages/page-actions.spec.ts` |
| CE-PAGE-008 | Page löschen | übernommen | I4 | L1 L2 L3 L5 L7 L8 | Funk.Pages.Tests | `web/pages/page-actions.spec.ts` |
| CE-PAGE-009 | Page duplizieren | übernommen | I4 | L1 L2 L3 L5 L7 L8 | Funk.Pages.Tests | `web/pages/page-actions.spec.ts` |
| CE-PAGE-012 | Referenzprotokoll der Inhalte (PageLog) | übernommen | I4 | L1 L2 L3 L5 L7 L8 | Funk.Pages.Tests | `web/pages/page-actions.spec.ts` |

**Betroffene Module/Libs in `funk.`**

- Backend: `src/modules/Pages/Funk.Pages`
- Frontend: `frontend/libs/web/pages`

**Referenzdokumente**

- Architektur: 04 §4.10
- Architektur: 05 §3.13.5
- Architektur: 07 §3.11
- Architektur: 06 D06-ADR-02 (PageLog)
- Architektur: 17 ABG-108
- Analyse/Feature: `analysis/04-api-intern-arbeitsobjekte.md` §2.14
- Analyse/Feature: `analysis/02b-datenmodell-arbeitsobjekte.md` §2.3, §3.12
- Analyse/Feature: `analysis/08-frontend-web-architektur.md` §3.7
- Analyse/Feature: `analysis/10b-frontend-cycles-modules-pages-views-weitere.md` §2.4, §3.3
- Analyse/Feature: `analysis/06-auth-sicherheit-querschnitt.md` §2.10
- Analyse/Feature: `analysis/07-hintergrundjobs-mail-storage-webhooks.md` §3.13, §3.10
- Feature-Katalog: `features/10-ce-feature-katalog.md` (Einträge CE-PAGE-004, CE-PAGE-005, CE-PAGE-006, CE-PAGE-007, CE-PAGE-008, CE-PAGE-009, CE-PAGE-012)

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- Backend: `apps/api/plane/app/views/page/base.py`, `apps/api/plane/app/serializers/page.py`, `apps/api/plane/app/permissions/page.py`, `apps/api/plane/db/models/page.py`, `apps/api/plane/bgtasks/copy_s3_object.py`, `apps/api/plane/db/models/page.py:80-117`, `apps/api/plane/bgtasks/page_transaction_task.py`
- Frontend: `apps/web/app/(all)/[workspaceSlug]/(projects)/projects/(detail)/[projectId]/pages/(list)/page.tsx`, `apps/web/app/(all)/[workspaceSlug]/(projects)/projects/(detail)/[projectId]/pages/(detail)/[pageId]/page.tsx`, `apps/web/store/pages/base-page.ts`, `apps/web/store/pages/project-page.ts`, `apps/web/hooks/use-page-fallback.ts`, `apps/web/hooks/use-realtime-page-events.tsx`, `apps/web/components/pages/header/lock-control.tsx`, `apps/web/components/pages/dropdowns/actions.tsx`, `apps/web/hooks/use-collaborative-page-actions.tsx`, `apps/web/components/common/page-access-icon.tsx`, `apps/web/components/pages/header/archived-badge.tsx`, `apps/web/components/pages/modals/delete-page-modal.tsx`, `apps/web/hooks/use-page-operations.ts`

**Endpunkte (Katalog 04, `architecture/_data/endpoints.json`; 11 registriert)**

| EP | Methode | Pfad | Oberfläche | Handler | Permission | Inkr. 04 | CE-IDs |
|---|---|---|---|---|---|---|---|
| EP-0397 | GET | `/api/workspaces/{slug}/projects/{project_id}/pages/{page_id}/` | App | PageEndpoints.GetPageQuery | project.page.read | I4 | CE-PAGE-004 |
| EP-0398 | PATCH | `/api/workspaces/{slug}/projects/{project_id}/pages/{page_id}/` | App | PageEndpoints.UpdatePageCommand | project.page.update | I4 | CE-PAGE-004, CE-RT-005 |
| EP-0399 | DELETE | `/api/workspaces/{slug}/projects/{project_id}/pages/{page_id}/` | App | PageEndpoints.DeletePageCommand | project.page.delete | I4 | CE-PAGE-008 |
| EP-0400 | POST | `/api/workspaces/{slug}/projects/{project_id}/pages/{page_id}/access/` | App | PageEndpoints.ChangePageAccessCommand | project.page.change_access | I4 | CE-PAGE-006 |
| EP-0401 | POST | `/api/workspaces/{slug}/projects/{project_id}/pages/{page_id}/archive/` | App | PageEndpoints.ArchivePageCommand | project.page.archive | I4 | CE-PAGE-007 |
| EP-0402 | DELETE | `/api/workspaces/{slug}/projects/{project_id}/pages/{page_id}/archive/` | App | PageEndpoints.UnarchivePageCommand | project.page.unarchive | I4 | CE-PAGE-007 |
| EP-0403 | GET | `/api/workspaces/{slug}/projects/{project_id}/pages/{page_id}/description/` | App | PageEndpoints.GetPageDescriptionBinaryQuery | project.page.read | I4 | CE-RT-003, CE-RT-005, CE-PAGE-012 |
| EP-0404 | PATCH | `/api/workspaces/{slug}/projects/{project_id}/pages/{page_id}/description/` | App | PageEndpoints.UpdatePageDescriptionCommand | project.page.update | I4 | CE-RT-003, CE-RT-005, CE-PAGE-012 |
| EP-0405 | POST | `/api/workspaces/{slug}/projects/{project_id}/pages/{page_id}/duplicate/` | App | PageEndpoints.DuplicatePageCommand | project.page.create | I4 | CE-PAGE-009 |
| EP-0406 | POST | `/api/workspaces/{slug}/projects/{project_id}/pages/{page_id}/lock/` | App | PageEndpoints.LockPageCommand | project.page.lock | I4 | CE-PAGE-005 |
| EP-0407 | DELETE | `/api/workspaces/{slug}/projects/{project_id}/pages/{page_id}/lock/` | App | PageEndpoints.UnlockPageCommand | project.page.unlock | I4 | CE-PAGE-005 |

**Akzeptanzkriterien**

1. Contract: je Endpunkt dieses Pakets ≥ 1 Szenario mit Golden vom Original (Erfolg, Berechtigungsfehler, Validierungsfehler); Replay grün (L5).
2. Permission-Matrix (05 Anhang B) für alle Endpunkte dieses Pakets als L3-Test grün; Tenant-Isolation geprüft.
3. Signal-Stores strukturgleich zum MobX-Original (`store-parity-check`), Vitest je Action (L2).
4. E2E-Specs dieses Pakets grün gegen Original **und** funk. (Dual-Target, Pflichtszenarien 15 §3.9.3).
5. Visual-/DOM-/a11y-Prüfpunkte der betroffenen Screens (09 §4.14, 15 §3.10.2) innerhalb der Schwellwerte 15 §3.10.3 (Chromium); i18n-Schlüssel nur aus den Original-Locales (de/en).
6. `ce-coverage-check --ids CE-PAGE-004,CE-PAGE-005,CE-PAGE-006,CE-PAGE-007,CE-PAGE-008,CE-PAGE-009,CE-PAGE-012` grün (Mindestebenen 15 Anhang B).

**Testumfang**

- Pflicht-Ebenen (aus 15 Anhang B): L1, L2, L3, L5, L7, L8
- Testprojekte: `Funk.Pages.Tests`
- E2E-Specs (`frontend/apps/e2e/`): `web/pages/page-actions.spec.ts`

### WP-I4-003 – Page-Export als PDF und Markdown

| Merkmal | Wert |
|---|---|
| Inkrement | I4 |
| Typ (DoD 15 §3.15.3) | D – Editor/Dokumente |
| Größe | M |
| parallelisierbar | ja |
| Abhängigkeiten | WP-I4-002, WP-I0-903, WP-I4-101 |
| CE-IDs | CE-PAGE-011 |

**Ziel.** `Funk.Documents.Pdf` mit den Stilprofilen `live` und `web` nach dem Ergebnis von S3, Endpunkt `POST /live/pdf-export/`, Markdown-Export.

**Enthaltene CE-IDs**

| CE-ID | Feature | Status (15 Anh. B) | Inkrement laut 15 | Pflicht-Ebenen | Testprojekt | E2E-Spec |
|---|---|---|---|---|---|---|
| CE-PAGE-011 | Page exportieren (PDF/Markdown) | übernommen | I4 | L1 L2 L3 L4 L5 L7 L8 (G-PDF) | Funk.Pages.Tests | `web/pages/page-export.spec.ts` |

**Betroffene Module/Libs in `funk.`**

- Backend: `src/documents/Funk.Documents.Pdf`
- Backend: `tests/Funk.Documents.Pdf.Tests`
- Frontend: `frontend/libs/web/pages` (export)

**Referenzdokumente**

- Architektur: 07 §3.15, §5.10
- Architektur: 17 Z-103, Z-116
- Analyse/Feature: `analysis/10b-frontend-cycles-modules-pages-views-weitere.md` §2.4
- Analyse/Feature: `analysis/12-editor-echtzeit-live.md` §3.23
- Feature-Katalog: `features/10-ce-feature-katalog.md` (Einträge CE-PAGE-011)

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- Backend: `apps/live/src/controllers/pdf-export.controller.ts`, `apps/live/src/services/pdf-export/pdf-export.service.ts`, `apps/live/src/lib/pdf/node-renderers.tsx`, `apps/live/src/lib/pdf/mark-renderers.ts`, `apps/live/src/lib/pdf/plane-pdf-exporter.tsx`, `apps/live/src/schema/pdf-export.ts`
- Frontend: `apps/web/components/pages/modals/export-page-modal.tsx`, `apps/web/components/editor/pdf/document.tsx`

**Endpunkte (Katalog 04, `architecture/_data/endpoints.json`; 1 registriert)**

| EP | Methode | Pfad | Oberfläche | Handler | Permission | Inkr. 04 | CE-IDs |
|---|---|---|---|---|---|---|---|
| EP-0412 | POST | `/live/pdf-export/` | Live | PdfExportEndpoint.Post | project.page.read | I4 | CE-PAGE-011 |

**Akzeptanzkriterien**

1. G-PDF, G-PDF-web und G-MD grün; Web-PDF-Kursiv wie Original (Z-116, bis Auftraggeber anders entscheidet).
2. G-SCHEMA unverändert (Schema-Freeze) oder genehmigte Änderung; G-DOC-Fälle für jeden betroffenen Node/Mark.
3. Browser-Roundtrip-Test (Playwright) für Yjs, sofern Kollaboration betroffen; Visual-Prüfpunkte des Editors.
4. `ce-coverage-check --ids CE-PAGE-011` grün (Mindestebenen 15 Anhang B).

**Testumfang**

- Pflicht-Ebenen (aus 15 Anhang B): L1, L2, L3, L4, L5, L7, L8
- Testprojekte: `Funk.Pages.Tests`
- E2E-Specs (`frontend/apps/e2e/`): `web/pages/page-export.spec.ts`

### WP-I4-004 – Kollaborativer Page-Editor (Seite, Toolbar, Kopf, Outline, Info-, Assets-Panel, Anzeigeoptionen) – ED-4-Hüllen

| Merkmal | Wert |
|---|---|
| Inkrement | I4 |
| Typ (DoD 15 §3.15.3) | V – Vertikaler Schnitt |
| Größe | L |
| parallelisierbar | nein |
| Abhängigkeiten | WP-I4-007, WP-I4-002 |
| CE-IDs | CE-PAGE-013, CE-PAGE-014, CE-PAGE-015, CE-PAGE-016, CE-PAGE-017, CE-PAGE-018, CE-PAGE-020 |

**Ziel.** Page-Seite mit `PlEdCollaborativeDocumentEditor`, `PlEdTitleEditor`, Navigation Titel↔Inhalt, Toolbar, Kopf, Outline, Info-Panel, Assets-Panel und Anzeigeoptionen.

**Enthaltene CE-IDs**

| CE-ID | Feature | Status (15 Anh. B) | Inkrement laut 15 | Pflicht-Ebenen | Testprojekt | E2E-Spec |
|---|---|---|---|---|---|---|
| CE-PAGE-013 | Kollaborativer Page-Editor (Seite) | übernommen | I4 | L2 L7 L8 | Frontend-only | `web/pages/page-editor-shell.spec.ts` |
| CE-PAGE-014 | Page-Toolbar | übernommen | I4 | L2 L7 L8 | Frontend-only | `web/pages/page-editor-shell.spec.ts` |
| CE-PAGE-015 | Page-Kopf | übernommen | I4 | L2 L7 L8 | Frontend-only | `web/pages/page-editor-shell.spec.ts` |
| CE-PAGE-016 | Outline | übernommen | I4 | L2 L7 L8 | Frontend-only | `web/pages/page-editor-shell.spec.ts` |
| CE-PAGE-017 | Info-Panel | übernommen | I4 | L2 L7 L8 | Frontend-only | `web/pages/page-editor-shell.spec.ts` |
| CE-PAGE-018 | Assets-Panel | übernommen | I4 | L2 L7 L8 | Frontend-only | `web/pages/page-editor-shell.spec.ts` |
| CE-PAGE-020 | Page-Anzeigeoptionen | übernommen | I4 | L2 L7 L8 | Frontend-only | `web/pages/page-editor-shell.spec.ts` |

**Betroffene Module/Libs in `funk.`**

- Frontend: `frontend/libs/web/pages`
- Frontend: `frontend/libs/web/core/editor` (Page-Hüllen)

**Referenzdokumente**

- Architektur: 10 §1.5 (ED-4), §3.16, §3.21
- Architektur: 08 §4.1
- Analyse/Feature: `analysis/10b-frontend-cycles-modules-pages-views-weitere.md` §2.4
- Analyse/Feature: `analysis/08-frontend-web-architektur.md` §3.7
- Analyse/Feature: `analysis/12-editor-echtzeit-live.md` §3.2, §3.22
- Analyse/Feature: `analysis/04-api-intern-arbeitsobjekte.md` §2.14
- Feature-Katalog: `features/10-ce-feature-katalog.md` (Einträge CE-PAGE-013, CE-PAGE-014, CE-PAGE-015, CE-PAGE-016, CE-PAGE-017, CE-PAGE-018, CE-PAGE-020)

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- Backend: `apps/api/plane/app/views/page/base.py`, `apps/live/src/services/page/core.service.ts`, `apps/api/plane/bgtasks/page_transaction_task.py`, `apps/api/plane/app/views/page/version.py`, `apps/api/plane/bgtasks/page_version_task.py`
- Frontend: `apps/web/components/pages/editor/page-root.tsx`, `apps/web/components/pages/editor/editor-body.tsx`, `apps/web/components/pages/editor/header/root.tsx`, `apps/web/components/pages/editor/header/logo-picker.tsx`, `apps/web/app/(all)/[workspaceSlug]/(projects)/projects/(detail)/[projectId]/pages/(detail)/[pageId]/page.tsx`, `apps/web/app/(all)/[workspaceSlug]/(projects)/projects/(detail)/[projectId]/pages/(list)/page.tsx`, `apps/web/store/pages/base-page.ts`, `apps/web/store/pages/project-page.ts`, `apps/web/hooks/use-page-fallback.ts`, `apps/web/hooks/use-realtime-page-events.tsx`, `packages/editor/src/components/editors/document/collaborative-editor.tsx`, `packages/editor/src/hooks/use-collaborative-editor.ts`, `packages/editor/src/hooks/use-title-editor.ts`, `packages/editor/src/hooks/use-editor-navigation.ts`, `packages/editor/src/components/editors/document/loader.tsx`, `apps/web/components/pages/editor/toolbar/root.tsx`, `apps/web/components/pages/editor/toolbar/toolbar.tsx`, `apps/web/components/pages/editor/toolbar/color-dropdown.tsx`, `apps/web/components/pages/editor/toolbar/options-dropdown.tsx`, `apps/web/app/(all)/[workspaceSlug]/(projects)/projects/(detail)/[projectId]/pages/(detail)/header.tsx`, `apps/web/components/pages/header/root.tsx`, `apps/web/components/pages/header/actions.tsx`, `apps/web/components/pages/header/lock-control.tsx`, `apps/web/components/pages/header/favorite-control.tsx`, `apps/web/components/pages/header/copy-link-control.tsx`, `apps/web/components/pages/header/archived-badge.tsx`, `apps/web/components/pages/header/offline-badge.tsx`, `apps/web/components/pages/header/syncing-badge.tsx`, `apps/web/components/pages/navigation-pane/root.tsx`, `apps/web/components/pages/navigation-pane/tab-panels/outline.tsx`, `apps/web/components/pages/editor/summary/content-browser.tsx`, `apps/web/components/pages/editor/summary/heading-components.tsx`, `packages/editor/src/extensions/headings-list.ts`, `packages/editor/src/helpers/scroll-to-node.ts`, `packages/editor/src/helpers/editor-ref.ts`, `packages/editor/src/components/editors/editor-container.tsx`, `apps/web/components/pages/navigation-pane/tab-panels/info/root.tsx`, `apps/web/components/pages/navigation-pane/tab-panels/info/document-info.tsx`, `apps/web/components/pages/navigation-pane/tab-panels/info/actors-info.tsx`, `apps/web/components/pages/navigation-pane/tab-panels/info/version-history.tsx`, `apps/web/components/pages/navigation-pane/tab-panels/assets.tsx`, `apps/web/components/pages/navigation-pane/tab-panels/empty-state/assets.tsx`, `apps/web/components/pages/dropdowns/actions.tsx`

**Akzeptanzkriterien**

1. Contract: je Endpunkt dieses Pakets ≥ 1 Szenario mit Golden vom Original (Erfolg, Berechtigungsfehler, Validierungsfehler); Replay grün (L5).
2. Permission-Matrix (05 Anhang B) für alle Endpunkte dieses Pakets als L3-Test grün; Tenant-Isolation geprüft.
3. Signal-Stores strukturgleich zum MobX-Original (`store-parity-check`), Vitest je Action (L2).
4. E2E-Specs dieses Pakets grün gegen Original **und** funk. (Dual-Target, Pflichtszenarien 15 §3.9.3).
5. Visual-/DOM-/a11y-Prüfpunkte der betroffenen Screens (09 §4.14, 15 §3.10.2) innerhalb der Schwellwerte 15 §3.10.3 (Chromium); i18n-Schlüssel nur aus den Original-Locales (de/en).
6. `ce-coverage-check --ids CE-PAGE-013,CE-PAGE-014,CE-PAGE-015,CE-PAGE-016,CE-PAGE-017,CE-PAGE-018,CE-PAGE-020` grün (Mindestebenen 15 Anhang B).

**Testumfang**

- Pflicht-Ebenen (aus 15 Anhang B): L2, L7, L8
- Testprojekte: `Frontend-only`
- E2E-Specs (`frontend/apps/e2e/`): `web/pages/page-editor-shell.spec.ts`

### WP-I4-005 – Page-Versionshistorie

| Merkmal | Wert |
|---|---|
| Inkrement | I4 |
| Typ (DoD 15 §3.15.3) | V – Vertikaler Schnitt |
| Größe | M |
| parallelisierbar | ja |
| Abhängigkeiten | WP-I4-006 |
| CE-IDs | CE-PAGE-019 |

**Ziel.** Versionierung beim Speichern (Fix CE-PAGE-019 laut 07), Versionsliste und -anzeige mit Document-Editor read-only, Versions-Cleanup.

**Enthaltene CE-IDs**

| CE-ID | Feature | Status (15 Anh. B) | Inkrement laut 15 | Pflicht-Ebenen | Testprojekt | E2E-Spec |
|---|---|---|---|---|---|---|
| CE-PAGE-019 | Versionshistorie | übernommen | I4 | L1 L2 L3 L5 L7 L8 | Funk.Pages.Tests | `web/pages/page-editor-shell.spec.ts` |

**Betroffene Module/Libs in `funk.`**

- Backend: `src/modules/Pages/Funk.Pages` (Versions)
- Frontend: `frontend/libs/web/pages` (version-history)

**Referenzdokumente**

- Architektur: 07 §3.6.4, §3.20
- Architektur: 06 §1.3 Zeile I4
- Analyse/Feature: `analysis/10b-frontend-cycles-modules-pages-views-weitere.md` §2.4
- Analyse/Feature: `analysis/04-api-intern-arbeitsobjekte.md` §2.14
- Analyse/Feature: `analysis/02b-datenmodell-arbeitsobjekte.md` §3.6
- Analyse/Feature: `analysis/07-hintergrundjobs-mail-storage-webhooks.md` §3.10
- Feature-Katalog: `features/10-ce-feature-katalog.md` (Einträge CE-PAGE-019)

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- Backend: `apps/api/plane/app/views/page/version.py`, `apps/api/plane/bgtasks/page_version_task.py`, `apps/api/plane/db/models/page.py:158-182`, `apps/api/plane/bgtasks/cleanup_task.py:107-125`, `apps/api/plane/bgtasks/cleanup_task.py`, `apps/api/plane/db/models/page.py`
- Frontend: `apps/web/components/pages/version/root.tsx`, `apps/web/components/pages/version/main-content.tsx`, `apps/web/components/pages/version/editor.tsx`

**Endpunkte (Katalog 04, `architecture/_data/endpoints.json`; 2 registriert)**

| EP | Methode | Pfad | Oberfläche | Handler | Permission | Inkr. 04 | CE-IDs |
|---|---|---|---|---|---|---|---|
| EP-0408 | GET | `/api/workspaces/{slug}/projects/{project_id}/pages/{page_id}/versions/` | App | PageVersionEndpoints.ListPageVersionsQuery | project.page_version.read | I4 | CE-PAGE-019 |
| EP-0409 | GET | `/api/workspaces/{slug}/projects/{project_id}/pages/{page_id}/versions/{pk}/` | App | PageVersionEndpoints.GetPageVersionQuery | project.page_version.read | I4 | CE-PAGE-019 |

**Akzeptanzkriterien**

1. Contract: je Endpunkt dieses Pakets ≥ 1 Szenario mit Golden vom Original (Erfolg, Berechtigungsfehler, Validierungsfehler); Replay grün (L5).
2. Permission-Matrix (05 Anhang B) für alle Endpunkte dieses Pakets als L3-Test grün; Tenant-Isolation geprüft.
3. Signal-Stores strukturgleich zum MobX-Original (`store-parity-check`), Vitest je Action (L2).
4. E2E-Specs dieses Pakets grün gegen Original **und** funk. (Dual-Target, Pflichtszenarien 15 §3.9.3).
5. Visual-/DOM-/a11y-Prüfpunkte der betroffenen Screens (09 §4.14, 15 §3.10.2) innerhalb der Schwellwerte 15 §3.10.3 (Chromium); i18n-Schlüssel nur aus den Original-Locales (de/en).
6. `ce-coverage-check --ids CE-PAGE-019` grün (Mindestebenen 15 Anhang B).

**Testumfang**

- Pflicht-Ebenen (aus 15 Anhang B): L1, L2, L3, L5, L7, L8
- Testprojekte: `Funk.Pages.Tests`
- E2E-Specs (`frontend/apps/e2e/`): `web/pages/page-editor-shell.spec.ts`

### WP-I4-006 – Realtime-Kollaborationsserver: Protokoll, Dokument-Lebenszyklus, Persistenz, Titel-Sync, Fehler/Force-Close, Konvertierung

| Merkmal | Wert |
|---|---|
| Inkrement | I4 |
| Typ (DoD 15 §3.15.3) | D – Editor/Dokumente |
| Größe | L |
| parallelisierbar | nein |
| Abhängigkeiten | WP-I4-101, WP-I4-202, WP-I0-107, WP-I0-901 |
| CE-IDs | CE-RT-001, CE-RT-005, CE-RT-006, CE-RT-008 |

**Ziel.** `Funk.Collaboration` (+ `.Protocol`) nach dem Ergebnis von S1: Wire-Protokoll, Zustandsautomaten, Auth über Session-Ticket, Laden/Migration HTML→Binary, Merge-on-Store mit 10-s-Debounce, Titel-Sync, Stateless-Ereignisse, Fehler-Broadcast, Force-Close, Admin-Kanal, Graceful Shutdown und `/live/convert-document/`.

**Enthaltene CE-IDs**

| CE-ID | Feature | Status (15 Anh. B) | Inkrement laut 15 | Pflicht-Ebenen | Testprojekt | E2E-Spec |
|---|---|---|---|---|---|---|
| CE-RT-001 | Realtime-Kollaborationsserver | übernommen | I4 | L1 L2 L3 L6 L7 L8 L9 (LT-17, LT-20) | Funk.Collaboration.Tests | `web/realtime/collaboration.spec.ts` |
| CE-RT-005 | Persistenz und Titel-Sync (Server) | übernommen | I4 | L1 L2 L3 L4 L6 L7 L8 (G-DOC) | Funk.Collaboration.Tests | `web/realtime/collaboration.spec.ts` |
| CE-RT-006 | Fehler-Broadcast und Force-Close | übernommen | I4 | L1 L2 L3 L6 L7 L8 | Funk.Collaboration.Tests | `web/realtime/collaboration.spec.ts` |
| CE-RT-008 | Dokument-Konvertierung | übernommen | I4 | L1 L2 L3 L4 L5 L6 L7 L8 (G-DOC) | Funk.Collaboration.Tests | `web/realtime/collaboration.spec.ts` |

**Betroffene Module/Libs in `funk.`**

- Backend: `src/modules/Collaboration/Funk.Collaboration`, `.Protocol`, `.Contracts`
- Backend: `src/modules/Pages/Funk.Pages/Documents/IPageDocumentStore` (Merge-on-Store)
- Backend: `tests/Funk.Collaboration.Tests`

**Referenzdokumente**

- Architektur: 07 §3.1–§3.9, §3.11, §5.1–§5.6, §7.3
- Architektur: 05 §3.11
- Architektur: 17 Z-101
- Analyse/Feature: `analysis/01-gesamtarchitektur-infrastruktur.md` §2.22
- Analyse/Feature: `analysis/12-editor-echtzeit-live.md` §3.2, §3.5, §3.8, §3.24
- Analyse/Feature: `analysis/04-api-intern-arbeitsobjekte.md` §2.14
- Analyse/Feature: `analysis/02b-datenmodell-arbeitsobjekte.md` §3.5
- Feature-Katalog: `features/10-ce-feature-katalog.md` (Einträge CE-RT-001, CE-RT-005, CE-RT-006, CE-RT-008)

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- Backend: `apps/live/src/server.ts`, `apps/live/src/hocuspocus.ts`, `apps/live/src/controllers/collaboration.controller.ts`, `apps/live/src/controllers/document.controller.ts`, `apps/live/src/controllers/pdf-export.controller.ts`, `apps/live/src/extensions/redis.ts`, `apps/live/src/extensions/database.ts`, `apps/live/src/extensions/title-sync.ts`, `apps/live/src/extensions/title-update/title-update-manager.ts`, `apps/live/src/extensions/title-update/debounce.ts`, `apps/live/src/services/page/core.service.ts`, `apps/api/plane/app/views/page/base.py`, `apps/api/plane/bgtasks/page_transaction_task.py`, `apps/api/plane/app/serializers/page.py:173-222`, `apps/api/plane/app/urls/page.py:57`, `apps/live/src/utils/broadcast-error.ts`, `apps/live/src/extensions/force-close-handler.ts`, `apps/live/src/types/admin-commands.ts`, `apps/api/plane/bgtasks/copy_s3_object.py`
- Frontend: `apps/web/components/pages/editor/editor-body.tsx`, `packages/editor/src/hooks/use-yjs-setup.ts`, `packages/editor/src/contexts/collaboration-context.tsx`, `packages/editor/src/helpers/yjs-utils.ts`, `apps/web/hooks/use-page-fallback.ts`

**Endpunkte (Katalog 04, `architecture/_data/endpoints.json`; 1 registriert)**

| EP | Methode | Pfad | Oberfläche | Handler | Permission | Inkr. 04 | CE-IDs |
|---|---|---|---|---|---|---|---|
| EP-0410 | GET | `/live/collaboration` | Live | CollaborationEndpoint.Upgrade | project.page.read (+PAGE) | I4 | CE-RT-001, CE-RT-002, CE-RT-004, CE-RT-005, CE-RT-006, CE-RT-007 |

**Akzeptanzkriterien**

1. Protokollfälle P-01…P-30 mit dem Original-Provider im Browser grün (`ProviderConformanceTests`).
2. LT-16…LT-18 im Zielbereich.
3. G-SCHEMA unverändert (Schema-Freeze) oder genehmigte Änderung; G-DOC-Fälle für jeden betroffenen Node/Mark.
4. Browser-Roundtrip-Test (Playwright) für Yjs, sofern Kollaboration betroffen; Visual-Prüfpunkte des Editors.
5. `ce-coverage-check --ids CE-RT-001,CE-RT-005,CE-RT-006,CE-RT-008` grün (Mindestebenen 15 Anhang B).

**Testumfang**

- Pflicht-Ebenen (aus 15 Anhang B): L1, L2, L3, L4, L5, L6, L7, L8, L9
- Testprojekte: `Funk.Collaboration.Tests`
- E2E-Specs (`frontend/apps/e2e/`): `web/realtime/collaboration.spec.ts`

### WP-I4-007 – Client-Kollaboration: Echtzeit-Editor-Bindung, Offline-Cache, REST-Fallback, Seitenereignisse (ED-4-Kern)

| Merkmal | Wert |
|---|---|
| Inkrement | I4 |
| Typ (DoD 15 §3.15.3) | D – Editor/Dokumente |
| Größe | L |
| parallelisierbar | nein |
| Abhängigkeiten | WP-I4-006, WP-I2-024 |
| CE-IDs | CE-RT-002, CE-RT-003, CE-RT-004 |

**Ziel.** `CollaborationSession` mit `HocuspocusProvider` 2.15.2, IndexedDB-Offline-Cache, Sync-Status, Stateless-Kanal, REST-Fallback-Speicherung (`setProviderDocument`, `getDocument`) und Echtzeit-Seitenereignisse; `collaboration-cursor` aktiv, sobald S1-Awareness grün ist (Z-109).

**Enthaltene CE-IDs**

| CE-ID | Feature | Status (15 Anh. B) | Inkrement laut 15 | Pflicht-Ebenen | Testprojekt | E2E-Spec |
|---|---|---|---|---|---|---|
| CE-RT-002 | Echtzeit-Kollaboration und Offline-Cache (Client) | übernommen | I4 | L1 L2 L3 L6 L7 L8 L9 (LT-19) | Funk.Collaboration.Tests | `web/realtime/collaboration.spec.ts` |
| CE-RT-003 | REST-Fallback-Speicherung | übernommen | I4 | L1 L2 L3 L5 L7 L8 | Funk.Pages.Tests | `web/realtime/collaboration.spec.ts` |
| CE-RT-004 | Echtzeit-Seitenereignisse | übernommen | I4 | L1 L2 L3 L6 L7 L8 | Funk.Collaboration.Tests | `web/realtime/collaboration.spec.ts` |

**Betroffene Module/Libs in `funk.`**

- Backend: `src/modules/Pages/Funk.Pages` (REST-Fallback)
- Frontend: `frontend/libs/shared/editor/collaboration`

**Referenzdokumente**

- Architektur: 10 §1.5 (ED-4), §3.15, §5.8
- Architektur: 07 §3.7, §3.11
- Architektur: 08 §3.12
- Architektur: 17 Z-109
- Analyse/Feature: `analysis/12-editor-echtzeit-live.md` §3.2, §3.9, §3.7
- Analyse/Feature: `analysis/02b-datenmodell-arbeitsobjekte.md` §3.5
- Analyse/Feature: `analysis/10b-frontend-cycles-modules-pages-views-weitere.md` §3.3
- Feature-Katalog: `features/10-ce-feature-katalog.md` (Einträge CE-RT-002, CE-RT-003, CE-RT-004)

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- Backend: `apps/live/src/controllers/collaboration.controller.ts`, `apps/live/src/hocuspocus.ts`, `apps/api/plane/app/serializers/page.py:173-222`, `apps/api/plane/app/urls/page.py:57`, `apps/live/src/lib/stateless.ts`
- Frontend: `packages/editor/src/hooks/use-yjs-setup.ts`, `packages/editor/src/contexts/collaboration-context.tsx`, `apps/web/hooks/use-page-fallback.ts`, `packages/editor/src/helpers/editor-ref.ts`, `packages/editor/src/helpers/yjs-utils.ts`, `packages/editor/src/constants/document-collaborative-events.ts`, `apps/web/hooks/use-collaborative-page-actions.tsx`, `apps/web/hooks/use-realtime-page-events.tsx`

**Akzeptanzkriterien**

1. AK-D10-14…-18 grün; Abweichung `collaboration-cursor` als FE-ED-01 in `ui-deviations.yaml` dokumentiert und vom Auftraggeber abgenommen.
2. G-SCHEMA unverändert (Schema-Freeze) oder genehmigte Änderung; G-DOC-Fälle für jeden betroffenen Node/Mark.
3. Browser-Roundtrip-Test (Playwright) für Yjs, sofern Kollaboration betroffen; Visual-Prüfpunkte des Editors.
4. `ce-coverage-check --ids CE-RT-002,CE-RT-003,CE-RT-004` grün (Mindestebenen 15 Anhang B).

**Testumfang**

- Pflicht-Ebenen (aus 15 Anhang B): L1, L2, L3, L5, L6, L7, L8, L9
- Testprojekte: `Funk.Collaboration.Tests`, `Funk.Pages.Tests`
- E2E-Specs (`frontend/apps/e2e/`): `web/realtime/collaboration.spec.ts`

### WP-I4-008 – Horizontale Skalierung des Realtime-Servers (Valkey-Backplane, PostgreSQL-Signale)

| Merkmal | Wert |
|---|---|
| Inkrement | I4 |
| Typ (DoD 15 §3.15.3) | B – Backend-only |
| Größe | M |
| parallelisierbar | ja |
| Abhängigkeiten | WP-I4-006 |
| CE-IDs | CE-RT-007 |

**Ziel.** Valkey-Backplane (`BackplaneEnvelope`), In-Memory-Backplane für Einzelknoten/AIO, PostgreSQL-Signale (`CollaborationSignalListener`), Multi-Instanz-Setup (2 × `realtime`) im Profil `test`.

**Enthaltene CE-IDs**

| CE-ID | Feature | Status (15 Anh. B) | Inkrement laut 15 | Pflicht-Ebenen | Testprojekt | E2E-Spec |
|---|---|---|---|---|---|---|
| CE-RT-007 | Horizontale Skalierung | übernommen | I4 | L1 L2 L3 L6 L7 L8 L9 (LT-18) | Funk.Collaboration.Tests | `web/realtime/collaboration.spec.ts` |

**Betroffene Module/Libs in `funk.`**

- Backend: `src/modules/Collaboration/Funk.Collaboration/Backplane/`

**Referenzdokumente**

- Architektur: 07 §3.10, §5.9
- Architektur: 14 §3.1.2 Zeile I4
- Analyse/Feature: `analysis/12-editor-echtzeit-live.md` §3.8
- Feature-Katalog: `features/10-ce-feature-katalog.md` (Einträge CE-RT-007)

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- Backend: `apps/live/src/extensions/redis.ts`, `apps/live/src/redis.ts`, `apps/live/src/utils/broadcast-message.ts`

**Akzeptanzkriterien**

1. Zwei Realtime-Instanzen konvergieren (Konvergenztest), LT-19/LT-20 im Zielbereich; Speicherdruck-Watchdog nach LT-20 entschieden (O-07-05).
2. Contract-Szenarien mit Original-Golden für alle HTTP-Endpunkte dieses Pakets; Replay grün.
3. Job-/Consumer-Tests: Idempotenz (Inbox), Retry/Backoff, Zeitsteuerung mit `FixedClock`; neue Ereignistypen im Event-Katalog-Snapshot.
4. Bei Cron-Jobs: Registrierung in `CronRegistrationTests` mit Original-Zeit (UTC).
5. `ce-coverage-check --ids CE-RT-007` grün (Mindestebenen 15 Anhang B).

**Testumfang**

- Pflicht-Ebenen (aus 15 Anhang B): L1, L2, L3, L6, L7, L8, L9
- Testprojekte: `Funk.Collaboration.Tests`
- E2E-Specs (`frontend/apps/e2e/`): `web/realtime/collaboration.spec.ts`

### WP-I4-009 – Demo-Inhalte bei Workspace-Anlage (vollständiger Seed inkl. Cycles, Module, Views, Pages)

| Merkmal | Wert |
|---|---|
| Inkrement | I4 |
| Typ (DoD 15 §3.15.3) | B – Backend-only |
| Größe | M |
| parallelisierbar | ja |
| Abhängigkeiten | WP-I4-002 |
| CE-IDs | CE-WS-002 |

**Ziel.** `WorkspaceDemoSeedJob` legt die acht Original-Seed-Dateien über die Contracts-Commands der Eigentümer-Module an (Bot-Benutzer, Projekt, States, Labels, Cycles, Module, Work Items, View, Pages), lädt die gebündelten Bilder in den Objektspeicher und ersetzt Branding.

> **Hinweis:** Abweichung von 15 Anhang B (Inkrement I0/I1): Der Seed braucht Cycles, Module, Views und Pages; er wird deshalb in I4 vollständig abgenommen (plan/04 OP-PLAN-03).

**Enthaltene CE-IDs**

| CE-ID | Feature | Status (15 Anh. B) | Inkrement laut 15 | Pflicht-Ebenen | Testprojekt | E2E-Spec |
|---|---|---|---|---|---|---|
| CE-WS-002 | Demo-Inhalte bei Workspace-Anlage (Seed) | übernommen | I0/I1 | L1 L2 L3 L5 L7 L8 | Funk.Workspaces.Tests | `web/workspace/create-workspace.spec.ts` |

**Betroffene Module/Libs in `funk.`**

- Backend: `src/modules/Workspaces/Funk.Workspaces/Application/Jobs/WorkspaceDemoSeedJob.cs`
- Backend: `src/data/Funk.Data/Seeds/Demo/`

**Referenzdokumente**

- Architektur: 03 §3.14.3
- Architektur: 06 §3.18.1
- Architektur: 17 Z-114 (Seed-Bilder)
- Analyse/Feature: `analysis/02a-datenmodell-kern.md` §2.9
- Analyse/Feature: `analysis/07-hintergrundjobs-mail-storage-webhooks.md` §3.16
- Feature-Katalog: `features/10-ce-feature-katalog.md` (Einträge CE-WS-002)

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- Backend: `apps/api/plane/bgtasks/workspace_seed_task.py`, `apps/api/plane/seeds/data/projects.json`, `apps/api/plane/seeds/data/issues.json`, `apps/api/plane/seeds/data/pages.json`, `apps/api/plane/seeds/data/states.json`, `apps/api/plane/seeds/data/labels.json`, `apps/api/plane/seeds/data/cycles.json`, `apps/api/plane/seeds/data/modules.json`, `apps/api/plane/seeds/data/views.json`, `apps/api/plane/app/views/workspace/base.py`

**Akzeptanzkriterien**

1. `WorkspaceDemoSeedTests` vergleicht gegen das gebrandete Golden und prüft `NOT ILIKE '%plane%'` auf allen Seed-Textspalten.
2. Contract-Szenarien mit Original-Golden für alle HTTP-Endpunkte dieses Pakets; Replay grün.
3. Job-/Consumer-Tests: Idempotenz (Inbox), Retry/Backoff, Zeitsteuerung mit `FixedClock`; neue Ereignistypen im Event-Katalog-Snapshot.
4. Bei Cron-Jobs: Registrierung in `CronRegistrationTests` mit Original-Zeit (UTC).
5. `ce-coverage-check --ids CE-WS-002` grün (Mindestebenen 15 Anhang B).

**Testumfang**

- Pflicht-Ebenen (aus 15 Anhang B): L1, L2, L3, L5, L7, L8
- Testprojekte: `Funk.Workspaces.Tests`
- E2E-Specs (`frontend/apps/e2e/`): `web/workspace/create-workspace.spec.ts`

### WP-I4-101 – Funk.Documents Teil B: Yjs ⇄ ProseMirror, YjsUpdateWriter, Document-Variante, Markdown

| Merkmal | Wert |
|---|---|
| Inkrement | I4 |
| Typ (DoD 15 §3.15.3) | D – Editor/Dokumente |
| Größe | L |
| parallelisierbar | ja |
| Abhängigkeiten | WP-I2-999, WP-I0-901, WP-I0-902 |
| CE-IDs | – (keine; Baustein/Spike/Abnahme) |

**Ziel.** Yjs-Abbildung (Port `y-prosemirror` 1.3.7) mit `YjsUpdateWriter`, Typ-Rückwandlung beim Lesen, Document-Variante des Schemas sowie `HtmlToMarkdownConverter` und `MarkdownRenderer`.

**Betroffene Module/Libs in `funk.`**

- Backend: `src/documents/Funk.Documents/Yjs/`, `Markdown/`
- Backend: `tests/Funk.Documents.Tests/Golden/Yjs/`

**Referenzdokumente**

- Architektur: 07 §3.12.5, §3.12.6, §3.14, §5.8
- Architektur: 15 §3.7 (G-DOC Yjs, G-MD)
- Architektur: 17 Z-102

**Akzeptanzkriterien**

1. G-DOC (Yjs-Teil) und G-MD grün; Browser-Roundtrip Yjs (AK-15-14).
2. G-SCHEMA unverändert (Schema-Freeze) oder genehmigte Änderung; G-DOC-Fälle für jeden betroffenen Node/Mark.
3. Browser-Roundtrip-Test (Playwright) für Yjs, sofern Kollaboration betroffen; Visual-Prüfpunkte des Editors.

**Testumfang**

- G-SCHEMA, G-DOC, Browser-Roundtrip (falls Kollaboration betroffen).

### WP-I4-201 – Erweiterungspunkte D1/D2: Pages ohne Projektpflicht, project_pages, parent_id, IPageHierarchy(+Queries), IPageAccessExtension, PAGE_*-Tokens

| Merkmal | Wert |
|---|---|
| Inkrement | I4 |
| Typ (DoD 15 §3.15.3) | X – Erweiterungspunkt 🧱 |
| Größe | S |
| parallelisierbar | nein |
| Abhängigkeiten | WP-I3-999 |
| CE-IDs | – (keine; Erweiterungspunkt) |
| Andockstelle | 01 §1.4 D1/D2; 16 §3.3.0 E-23; 16 §4.6 (Träger CE-PAGE-001/-003/-004/-006/-007) |

**Ziel.** `pages.workspace_id` mit Projektzuordnung über `project_pages`, `pages.parent_id` (CE immer `null`), `IPageHierarchy` und `IPageHierarchyQueries` (E-23, CE flach/`[]`), `IPageAccessExtension` (Default `false`); Frontend `PAGE_STORES`, `PAGE_TREE`, `PAGE_FLAGS`, `PAGE_PANE_EXTENSIONS`.

**Betroffene Module/Libs in `funk.`**

- Backend: `src/modules/Pages/Funk.Pages.Contracts/Hierarchy/`
- Backend: `src/data/Funk.Data/Entities/Pages/`
- Frontend: `frontend/libs/web/extensions/src/pages.ts`

**Referenzdokumente**

- Architektur: 16 §5.13, §3.3.0 E-23
- Architektur: 01 §1.4 Zeilen D1, D2
- Architektur: 03 §3.4.10

**Akzeptanzkriterien**

1. Contract-Goldens der Page-Payloads unverändert; Fake-Hierarchie liefert Kinder, die im `PAGE_TREE` erscheinen (Typ X).
2. Contract (Interface/Schema/Token) + CE-Default-Implementierung; Eintrag in `tests/extension-points.yaml`.
3. Test „CE-Default = Original-Verhalten“ (Contract-Replay unverändert grün).
4. Test mit Fake-Erweiterung aus `Funk.BuildingBlocks.Testing/Extensions` bzw. `provideFakeExtensions()` beweist Erweiterbarkeit ohne CE-Änderung (DoD Typ X).

**Testumfang**

- Typ-X-Tests (CE-Default unverändert, Fake-Erweiterung wirkt ohne CE-Änderung), L0-Inventarabgleich `ExtensionPointInventoryTests`/`extension-registry-check`.

### WP-I4-202 – Erweiterungspunkte Kollaboration: ICollaborationDocumentType, affectedPages, EDITOR_BLOCKS, EDITOR_MENTION_TYPES

| Merkmal | Wert |
|---|---|
| Inkrement | I4 |
| Typ (DoD 15 §3.15.3) | X – Erweiterungspunkt 🧱 |
| Größe | S |
| parallelisierbar | nein |
| Abhängigkeiten | WP-I2-999, WP-I4-101 |
| CE-IDs | – (keine; Erweiterungspunkt) |
| Andockstelle | 16 §3.3.0 E-10; 16 §4.6 (Träger CE-RT-001, CE-RT-004, CE-RT-005) |

**Ziel.** Registry der Hocuspocus-`documentType`-Werte (E-10, CE: `ProjectPageDocumentType` = `project_page`), server-seitig erzeugbares Realtime-Event `affectedPages`, Editor-Tokens `EDITOR_BLOCKS` und `EDITOR_MENTION_TYPES`.

**Betroffene Module/Libs in `funk.`**

- Backend: `src/modules/Collaboration/Funk.Collaboration.Contracts/ICollaborationDocumentType.cs`
- Frontend: `frontend/libs/shared/editor/extensibility`

**Referenzdokumente**

- Architektur: 07 §5.2, §5.3, §3.7.2
- Architektur: 10 §5.10, §6.2
- Architektur: 16 §3.3.0 E-10

**Akzeptanzkriterien**

1. Fake-Dokumenttyp wird über das Protokoll geladen/gespeichert ohne CE-Änderung; Fake-Block erscheint im Slash-Menü (Typ X).
2. Contract (Interface/Schema/Token) + CE-Default-Implementierung; Eintrag in `tests/extension-points.yaml`.
3. Test „CE-Default = Original-Verhalten“ (Contract-Replay unverändert grün).
4. Test mit Fake-Erweiterung aus `Funk.BuildingBlocks.Testing/Extensions` bzw. `provideFakeExtensions()` beweist Erweiterbarkeit ohne CE-Änderung (DoD Typ X).

**Testumfang**

- Typ-X-Tests (CE-Default unverändert, Fake-Erweiterung wirkt ohne CE-Änderung), L0-Inventarabgleich `ExtensionPointInventoryTests`/`extension-registry-check`.

### WP-I4-999 – Abnahme I4 – Pages & Realtime (G5)

| Merkmal | Wert |
|---|---|
| Inkrement | I4 |
| Typ (DoD 15 §3.15.3) | A – Inkrement-Abnahme |
| Größe | S |
| parallelisierbar | nein |
| Abhängigkeiten | WP-I4-001, WP-I4-002, WP-I4-003, WP-I4-004, WP-I4-005, WP-I4-006, WP-I4-007, WP-I4-008, WP-I4-009, WP-I4-101, WP-I4-201, WP-I4-202 |
| CE-IDs | – (keine; Baustein/Spike/Abnahme) |

**Ziel.** Inkrement-Abnahme I4 nach G5 und Meilenstein M4.

**Referenzdokumente**

- Architektur: plan/01-roadmap-ce.md §4 (M4)
- Architektur: 15 §3.16 Zeile I4

**Akzeptanzkriterien**

1. Alle Abnahmekriterien M4 erfüllt; `docs/acceptance/I4.md` generiert.
2. G5 `--inc <In> --strict` grün: `ce-coverage-check`, `original-test-ledger`, Parity-Report (0 ungenehmigte Abweichungen, Endpunkt-Abdeckung des Inkrements 100 %), Visual/a11y, Lastziele, Security-Report.
3. Demo-Video der Kern-Flows (`--video on`) und Abnahmebericht `docs/acceptance/<In>.md`; fachliche Abnahme durch den Auftraggeber.

**Testumfang**

- G5 `--inc I4`.

## 4.6 Inkrement I5

### WP-I5-001 – Workspace-Analytics: Tabs, Kennzahlen, Project Insights, Active Projects, Created vs Resolved, Customized Insights, Insight-Tabelle mit CSV

| Merkmal | Wert |
|---|---|
| Inkrement | I5 |
| Typ (DoD 15 §3.15.3) | V – Vertikaler Schnitt |
| Größe | L |
| parallelisierbar | ja |
| Abhängigkeiten | WP-I4-999, WP-I3-101 |
| CE-IDs | CE-ANA-001, CE-ANA-002, CE-ANA-003, CE-ANA-004, CE-ANA-005, CE-ANA-006, CE-ANA-007 |

**Ziel.** Analytics-Seite mit allen CE-Tabs und Diagrammen, Insight-Tabelle mit CSV-Export.

**Enthaltene CE-IDs**

| CE-ID | Feature | Status (15 Anh. B) | Inkrement laut 15 | Pflicht-Ebenen | Testprojekt | E2E-Spec |
|---|---|---|---|---|---|---|
| CE-ANA-001 | Workspace-Analytics mit Tabs | übernommen | I5 | L1 L2 L3 L5 L7 L8 | Funk.Analytics.Tests | `web/analytics/analytics.spec.ts` |
| CE-ANA-002 | Analytics-Kennzahlen | übernommen | I5 | L1 L2 L3 L5 L7 L8 | Funk.Analytics.Tests | `web/analytics/analytics.spec.ts` |
| CE-ANA-003 | Project Insights | übernommen | I5 | L1 L2 L3 L5 L7 L8 | Funk.Analytics.Tests | `web/analytics/analytics.spec.ts` |
| CE-ANA-004 | Active Projects | übernommen | I5 | L1 L2 L3 L5 L7 L8 | Funk.Analytics.Tests | `web/analytics/analytics.spec.ts` |
| CE-ANA-005 | Created vs Resolved | übernommen | I5 | L1 L2 L3 L5 L7 L8 | Funk.Analytics.Tests | `web/analytics/analytics.spec.ts` |
| CE-ANA-006 | Customized Insights | übernommen | I5 | L1 L2 L3 L5 L7 L8 | Funk.Analytics.Tests | `web/analytics/analytics.spec.ts` |
| CE-ANA-007 | Insight-Tabelle mit CSV-Export | übernommen | I5 | L1 L2 L3 L5 L7 L8 | Funk.Analytics.Tests | `web/analytics/analytics.spec.ts` |

**Betroffene Module/Libs in `funk.`**

- Backend: `src/modules/Analytics/Funk.Analytics`
- Backend: `tests/modules/Funk.Analytics.Tests`
- Frontend: `frontend/libs/web/analytics`

**Referenzdokumente**

- Architektur: 04 §4.14
- Architektur: 03 §3.4.13
- Architektur: 09 §3.12
- Analyse/Feature: `analysis/10b-frontend-cycles-modules-pages-views-weitere.md` §2.6
- Analyse/Feature: `analysis/08-frontend-web-architektur.md` §2.2
- Analyse/Feature: `analysis/03-api-intern-workspace-projekt-user.md` §3.15
- Analyse/Feature: `analysis/06-auth-sicherheit-querschnitt.md` §2.13
- Analyse/Feature: `analysis/13b-shared-packages-i18n.md` §2.2
- Feature-Katalog: `features/10-ce-feature-katalog.md` (Einträge CE-ANA-001, CE-ANA-002, CE-ANA-003, CE-ANA-004, CE-ANA-005, CE-ANA-006, CE-ANA-007)

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- Backend: `apps/api/plane/app/views/analytic/advance.py`, `apps/api/plane/utils/date_utils.py`, `apps/api/plane/utils/build_chart.py`, `apps/api/plane/utils/analytics_plot.py`
- Frontend: `apps/web/app/(all)/[workspaceSlug]/(projects)/analytics/[tabId]/page.tsx`, `apps/web/components/analytics/tabs.tsx`, `apps/web/components/analytics/use-analytics-tabs.tsx`, `apps/web/components/analytics/analytics-filter-actions.tsx`, `apps/web/components/analytics/select/project.tsx`, `apps/web/store/analytics.store.ts`, `apps/web/services/analytics.service.ts`, `apps/web/components/analytics/total-insights.tsx`, `apps/web/components/analytics/insight-card.tsx`, `packages/constants/src/analytics/common.ts`, `packages/constants/src/chart.ts`, `packages/constants/src/graph.ts`, `apps/web/components/analytics/overview/project-insights.tsx`, `apps/web/components/analytics/overview/root.tsx`, `apps/web/components/analytics/overview/active-projects.tsx`, `apps/web/components/analytics/overview/active-project-item.tsx`, `apps/web/components/analytics/work-items/created-vs-resolved.tsx`, `apps/web/components/analytics/work-items/customized-insights.tsx`, `apps/web/components/analytics/work-items/priority-chart.tsx`, `apps/web/components/analytics/select/analytics-params.tsx`, `apps/web/components/analytics/select/select-x-axis.tsx`, `apps/web/components/analytics/select/select-y-axis.tsx`, `apps/web/components/chart/utils.ts`, `apps/web/components/analytics/work-items/utils.ts`, `apps/web/components/analytics/work-items/workitems-insight-table.tsx`, `apps/web/components/analytics/insight-table/root.tsx`, `apps/web/components/analytics/insight-table/data-table.tsx`, `apps/web/components/analytics/export.ts`

**Endpunkte (Katalog 04, `architecture/_data/endpoints.json`; 3 registriert)**

| EP | Methode | Pfad | Oberfläche | Handler | Permission | Inkr. 04 | CE-IDs |
|---|---|---|---|---|---|---|---|
| EP-0474 | GET | `/api/workspaces/{slug}/advance-analytics-charts/` | App | AnalyticsEndpoints.GetAdvanceAnalyticsChartQuery | workspace.analytics.read | I5 | CE-ANA-005, CE-ANA-006 |
| EP-0475 | GET | `/api/workspaces/{slug}/advance-analytics-stats/` | App | AnalyticsEndpoints.GetAdvanceAnalyticsStatsQuery | workspace.analytics.read | I5 | CE-ANA-003, CE-ANA-007 |
| EP-0476 | GET | `/api/workspaces/{slug}/advance-analytics/` | App | AnalyticsEndpoints.GetAdvanceAnalyticsQuery | workspace.analytics.read | I5 | CE-ANA-001, CE-ANA-002, CE-ANA-004 |

**Akzeptanzkriterien**

1. Contract: je Endpunkt dieses Pakets ≥ 1 Szenario mit Golden vom Original (Erfolg, Berechtigungsfehler, Validierungsfehler); Replay grün (L5).
2. Permission-Matrix (05 Anhang B) für alle Endpunkte dieses Pakets als L3-Test grün; Tenant-Isolation geprüft.
3. Signal-Stores strukturgleich zum MobX-Original (`store-parity-check`), Vitest je Action (L2).
4. E2E-Specs dieses Pakets grün gegen Original **und** funk. (Dual-Target, Pflichtszenarien 15 §3.9.3).
5. Visual-/DOM-/a11y-Prüfpunkte der betroffenen Screens (09 §4.14, 15 §3.10.2) innerhalb der Schwellwerte 15 §3.10.3 (Chromium); i18n-Schlüssel nur aus den Original-Locales (de/en).
6. `ce-coverage-check --ids CE-ANA-001,CE-ANA-002,CE-ANA-003,CE-ANA-004,CE-ANA-005,CE-ANA-006,CE-ANA-007` grün (Mindestebenen 15 Anhang B).

**Testumfang**

- Pflicht-Ebenen (aus 15 Anhang B): L1, L2, L3, L5, L7, L8
- Testprojekte: `Funk.Analytics.Tests`
- E2E-Specs (`frontend/apps/e2e/`): `web/analytics/analytics.spec.ts`

### WP-I5-002 – Analytics-Panel (Projekt, Cycle, Modul), Legacy-Analytics, gespeicherte Analytics-Views, Export per E-Mail

| Merkmal | Wert |
|---|---|
| Inkrement | I5 |
| Typ (DoD 15 §3.15.3) | V – Vertikaler Schnitt |
| Größe | M |
| parallelisierbar | ja |
| Abhängigkeiten | WP-I5-001, WP-I1-102 |
| CE-IDs | CE-ANA-008, CE-ANA-009 |

**Ziel.** Analytics-Panel in Projekt-, Cycle- und Modul-Kontexten, Legacy-Analytics, gespeicherte Analytics-Views und Export per E-Mail (Template M11).

**Enthaltene CE-IDs**

| CE-ID | Feature | Status (15 Anh. B) | Inkrement laut 15 | Pflicht-Ebenen | Testprojekt | E2E-Spec |
|---|---|---|---|---|---|---|
| CE-ANA-008 | Analytics-Panel für Projekt, Cycle und Modul | übernommen | I5 | L1 L2 L3 L5 L7 L8 | Funk.Analytics.Tests | `web/analytics/analytics.spec.ts` |
| CE-ANA-009 | Legacy-Analytics, gespeicherte Analytics-Views und Export per E-Mail | übernommen | I5 | L1 L2 L3 L4 L5 L7 L8 (G-MAIL) | Funk.Analytics.Tests | `web/analytics/analytics.spec.ts` |

**Betroffene Module/Libs in `funk.`**

- Backend: `src/modules/Analytics/Funk.Analytics`
- Frontend: `frontend/libs/web/analytics`

**Referenzdokumente**

- Architektur: 04 §4.14
- Architektur: 06 §3.15.2
- Analyse/Feature: `analysis/10b-frontend-cycles-modules-pages-views-weitere.md` §2.6
- Analyse/Feature: `analysis/09-frontend-arbeitsobjekte-layouts.md` §2.10
- Analyse/Feature: `analysis/03-api-intern-workspace-projekt-user.md` §3.15
- Analyse/Feature: `analysis/02a-datenmodell-kern.md` §3.19
- Analyse/Feature: `analysis/07-hintergrundjobs-mail-storage-webhooks.md` §2.13
- Feature-Katalog: `features/10-ce-feature-katalog.md` (Einträge CE-ANA-008, CE-ANA-009)

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- Backend: `apps/api/plane/app/views/analytic/project_analytics.py`, `apps/api/plane/app/views/analytic/base.py`, `apps/api/plane/utils/analytics_plot.py`, `apps/api/plane/bgtasks/analytic_plot_export.py`, `apps/api/plane/db/models/analytic.py`, `apps/api/plane/app/serializers/analytic.py`, `apps/api/templates/emails/exports/analytics.html`
- Frontend: `apps/web/components/analytics/work-items/modal/index.tsx`, `apps/web/components/analytics/work-items/modal/header.tsx`, `apps/web/components/analytics/work-items/modal/content.tsx`, `apps/web/components/issues/filters.tsx`, `apps/web/components/analytics/work-items/modal`, `apps/web/services/analytics.service.ts`

**Endpunkte (Katalog 04, `architecture/_data/endpoints.json`; 12 registriert)**

| EP | Methode | Pfad | Oberfläche | Handler | Permission | Inkr. 04 | CE-IDs |
|---|---|---|---|---|---|---|---|
| EP-0469 | GET | `/api/workspaces/{slug}/analytic-view/` | App | AnalyticViewEndpoints.ListAnalyticViewsQuery | workspace.analytics_view.read | I5 | CE-ANA-009 |
| EP-0470 | POST | `/api/workspaces/{slug}/analytic-view/` | App | AnalyticViewEndpoints.CreateAnalyticViewCommand | workspace.analytics_view.create | I5 | CE-ANA-009 |
| EP-0471 | GET | `/api/workspaces/{slug}/analytic-view/{pk}/` | App | AnalyticViewEndpoints.GetAnalyticViewQuery | workspace.analytics_view.read | I5 | CE-ANA-009 |
| EP-0472 | PATCH | `/api/workspaces/{slug}/analytic-view/{pk}/` | App | AnalyticViewEndpoints.UpdateAnalyticViewCommand | workspace.analytics_view.update | I5 | CE-ANA-009 |
| EP-0473 | DELETE | `/api/workspaces/{slug}/analytic-view/{pk}/` | App | AnalyticViewEndpoints.DeleteAnalyticViewCommand | workspace.analytics_view.delete | I5 | CE-ANA-009 |
| EP-0477 | GET | `/api/workspaces/{slug}/analytics/` | App | AnalyticsEndpoints.GetLegacyAnalyticsPlotQuery | workspace.analytics.read | I5 | CE-ANA-009 |
| EP-0478 | GET | `/api/workspaces/{slug}/default-analytics/` | App | AnalyticsEndpoints.GetDefaultAnalyticsQuery | workspace.analytics.read_basic | I5 | CE-ANA-009 |
| EP-0479 | POST | `/api/workspaces/{slug}/export-analytics/` | App | AnalyticsEndpoints.ExportAnalyticsCommand | workspace.analytics.export | I5 | CE-ANA-009 |
| EP-0481 | GET | `/api/workspaces/{slug}/projects/{project_id}/advance-analytics-charts/` | App | AnalyticsEndpoints.GetProjectAdvanceAnalyticsChartQuery | project.analytics.read_charts | I5 | CE-ANA-008 |
| EP-0482 | GET | `/api/workspaces/{slug}/projects/{project_id}/advance-analytics-stats/` | App | AnalyticsEndpoints.GetProjectAdvanceAnalyticsStatsQuery | project.analytics.read | I5 | CE-ANA-008 |
| EP-0483 | GET | `/api/workspaces/{slug}/projects/{project_id}/advance-analytics/` | App | AnalyticsEndpoints.GetProjectAdvanceAnalyticsQuery | project.analytics.read | I5 | CE-ANA-008 |
| EP-0484 | GET | `/api/workspaces/{slug}/saved-analytic-view/{analytic_id}/` | App | AnalyticsEndpoints.GetSavedAnalyticsQuery | workspace.analytics.read | I5 | CE-ANA-009 |

**Akzeptanzkriterien**

1. Contract: je Endpunkt dieses Pakets ≥ 1 Szenario mit Golden vom Original (Erfolg, Berechtigungsfehler, Validierungsfehler); Replay grün (L5).
2. Permission-Matrix (05 Anhang B) für alle Endpunkte dieses Pakets als L3-Test grün; Tenant-Isolation geprüft.
3. Signal-Stores strukturgleich zum MobX-Original (`store-parity-check`), Vitest je Action (L2).
4. E2E-Specs dieses Pakets grün gegen Original **und** funk. (Dual-Target, Pflichtszenarien 15 §3.9.3).
5. Visual-/DOM-/a11y-Prüfpunkte der betroffenen Screens (09 §4.14, 15 §3.10.2) innerhalb der Schwellwerte 15 §3.10.3 (Chromium); i18n-Schlüssel nur aus den Original-Locales (de/en).
6. `ce-coverage-check --ids CE-ANA-008,CE-ANA-009` grün (Mindestebenen 15 Anhang B).

**Testumfang**

- Pflicht-Ebenen (aus 15 Anhang B): L1, L2, L3, L4, L5, L7, L8
- Testprojekte: `Funk.Analytics.Tests`
- E2E-Specs (`frontend/apps/e2e/`): `web/analytics/analytics.spec.ts`

### WP-I5-003 – Workspace-Home: Widgets, Widget-Verwaltung, Quickstart, Quick links, Recents, Produkt-Tour, Legacy-Dashboard

| Merkmal | Wert |
|---|---|
| Inkrement | I5 |
| Typ (DoD 15 §3.15.3) | V – Vertikaler Schnitt |
| Größe | L |
| parallelisierbar | ja |
| Abhängigkeiten | WP-I4-999, WP-I5-202 |
| CE-IDs | CE-HOME-001, CE-HOME-002, CE-HOME-003, CE-HOME-004, CE-HOME-005, CE-HOME-006, CE-HOME-007 |

**Ziel.** Home mit Widgets über `HOME_WIDGETS`, Widget-Verwaltung, Quickstart-Guide, Quick links, Recents (Recent-Visits-Job), Produkt-Tour und Legacy-Dashboard/Aktivitätsgraphen (nur API).

**Enthaltene CE-IDs**

| CE-ID | Feature | Status (15 Anh. B) | Inkrement laut 15 | Pflicht-Ebenen | Testprojekt | E2E-Spec |
|---|---|---|---|---|---|---|
| CE-HOME-001 | Workspace-Home | übernommen | I5 | L1 L2 L3 L5 L7 L8 | Funk.Home.Tests | `web/home/home.spec.ts` |
| CE-HOME-002 | Home-Widgets verwalten | übernommen | I5 | L1 L2 L3 L5 L7 L8 | Funk.Home.Tests | `web/home/home.spec.ts` |
| CE-HOME-003 | Quickstart-Guide | übernommen | I5 | L1 L2 L3 L5 L7 L8 | Funk.Home.Tests | `web/home/home.spec.ts` |
| CE-HOME-004 | Quick links | übernommen | I5 | L1 L2 L3 L5 L7 L8 | Funk.Home.Tests | `web/home/home.spec.ts` |
| CE-HOME-005 | Recents (zuletzt besucht) | übernommen | I5 | L1 L2 L3 L5 L7 L8 | Funk.Home.Tests | `web/home/home.spec.ts` |
| CE-HOME-006 | Produkt-Tour | übernommen | I5 | L1 L2 L3 L5 L7 L8 | Funk.Home.Tests | `web/home/home.spec.ts` |
| CE-HOME-007 | Legacy-Dashboard und Aktivitätsgraphen (nur API) | übernommen | I5 | L1 L2 L3 L5 L7 L8 | Funk.Home.Tests | `web/home/home.spec.ts` |

**Betroffene Module/Libs in `funk.`**

- Backend: `src/modules/Home/Funk.Home`
- Backend: `tests/modules/Funk.Home.Tests`
- Frontend: `frontend/libs/web/home`

**Referenzdokumente**

- Architektur: 04 §4.15
- Architektur: 03 §3.4.12
- Architektur: 06 O-D06-09
- Analyse/Feature: `analysis/10a-frontend-workspace-projekt-navigation.md` §3.6, §2.15
- Analyse/Feature: `analysis/08-frontend-web-architektur.md` §2.2
- Analyse/Feature: `analysis/03-api-intern-workspace-projekt-user.md` §3.7, §3.6, §2.7
- Analyse/Feature: `analysis/02a-datenmodell-kern.md` §3.6, §2.3, §3.12
- Analyse/Feature: `analysis/13b-shared-packages-i18n.md` §2.7
- Analyse/Feature: `analysis/04-api-intern-arbeitsobjekte.md` §3.19
- Analyse/Feature: `analysis/07-hintergrundjobs-mail-storage-webhooks.md` §3.15
- Feature-Katalog: `features/10-ce-feature-katalog.md` (Einträge CE-HOME-001, CE-HOME-002, CE-HOME-003, CE-HOME-004, CE-HOME-005, CE-HOME-006, CE-HOME-007)

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- Backend: `apps/api/plane/app/views/workspace/home.py`, `apps/api/plane/db/models/workspace.py`, `apps/api/plane/app/views/workspace/quick_link.py`, `apps/api/plane/app/serializers/workspace.py`, `apps/api/plane/app/views/workspace/recent_visit.py`, `apps/api/plane/bgtasks/recent_visited_task.py`, `apps/api/plane/db/models/recent_visit.py`, `apps/api/plane/app/views/user/base.py`, `apps/api/plane/db/models/user.py`, `apps/api/plane/app/views/workspace/base.py`, `apps/api/plane/app/views/workspace/user.py`
- Frontend: `apps/web/components/home/root.tsx`, `apps/web/components/home/user-greetings.tsx`, `apps/web/app/(all)/[workspaceSlug]/(projects)/page.tsx`, `apps/web/app/(all)/[workspaceSlug]/(projects)/header.tsx`, `apps/web/store/workspace/home.ts`, `apps/web/store/workspace/link.store.ts`, `apps/web/services/workspace.service.ts`, `apps/web/components/home/widgets/manage/index.tsx`, `apps/web/components/home/widgets/manage/widget-list.tsx`, `apps/web/components/home/widgets/manage/widget-item.tsx`, `packages/constants/src/dashboard.ts`, `packages/services/src/dashboard/dashboard.service.ts`, `packages/types/src/dashboard.ts`, `packages/types/src/home.ts`, `apps/web/components/home/widgets/empty-states/no-projects.tsx`, `apps/web/components/home/widgets/links/root.tsx`, `apps/web/components/home/widgets/links/links.tsx`, `apps/web/components/home/widgets/links/link-detail.tsx`, `apps/web/components/home/widgets/links/create-update-link-modal.tsx`, `apps/web/components/home/widgets/links/use-links.tsx`, `apps/web/components/home/widgets/recents/index.tsx`, `apps/web/components/home/widgets/recents/filters.tsx`, `apps/web/components/home/widgets/recents/issue.tsx`, `apps/web/components/home/widgets/recents/page.tsx`, `apps/web/components/home/widgets/recents/project.tsx`, `apps/web/components/onboarding/tour/root.tsx`, `apps/web/components/onboarding/tour/sidebar.tsx`

**Endpunkte (Katalog 04, `architecture/_data/endpoints.json`; 11 registriert)**

| EP | Methode | Pfad | Oberfläche | Handler | Permission | Inkr. 04 | CE-IDs |
|---|---|---|---|---|---|---|---|
| EP-0103 | GET | `/api/users/me/workspaces/{slug}/activity-graph/` | App | MemberProfileEndpoints.GetActivityGraphQuery | workspace.member_profile.read_own | I5 | CE-HOME-007 |
| EP-0104 | GET | `/api/users/me/workspaces/{slug}/dashboard/` | App | MemberProfileEndpoints.GetLegacyDashboardQuery | workspace.member_profile.read_own | I5 | CE-HOME-007 |
| EP-0105 | GET | `/api/users/me/workspaces/{slug}/issues-completed-graph/` | App | MemberProfileEndpoints.GetCompletedWorkItemsGraphQuery | workspace.member_profile.read_own | I5 | CE-HOME-007 |
| EP-0144 | GET | `/api/workspaces/{slug}/home-preferences/` | App | WorkspacePreferenceEndpoints.ListHomePreferencesQuery | workspace.member_preference.read | I1 | CE-HOME-001, CE-HOME-002 |
| EP-0145 | PATCH | `/api/workspaces/{slug}/home-preferences/{key}/` | App | WorkspacePreferenceEndpoints.UpdateHomePreferenceCommand | workspace.member_preference.update | I1 | CE-HOME-002 |
| EP-0485 | GET | `/api/workspaces/{slug}/quick-links/` | App | QuickLinkEndpoints.ListQuickLinksQuery | workspace.quick_link.read | I5 | CE-HOME-004 |
| EP-0486 | POST | `/api/workspaces/{slug}/quick-links/` | App | QuickLinkEndpoints.CreateQuickLinkCommand | workspace.quick_link.create | I5 | CE-HOME-004 |
| EP-0487 | GET | `/api/workspaces/{slug}/quick-links/{pk}/` | App | QuickLinkEndpoints.GetQuickLinkQuery | workspace.quick_link.read | I5 | CE-HOME-004 |
| EP-0488 | PATCH | `/api/workspaces/{slug}/quick-links/{pk}/` | App | QuickLinkEndpoints.UpdateQuickLinkCommand | workspace.quick_link.update | I5 | CE-HOME-004 |
| EP-0489 | DELETE | `/api/workspaces/{slug}/quick-links/{pk}/` | App | QuickLinkEndpoints.DeleteQuickLinkCommand | workspace.quick_link.delete | I5 | CE-HOME-004 |
| EP-0490 | GET | `/api/workspaces/{slug}/recent-visits/` | App | RecentVisitEndpoints.ListRecentVisitsQuery | workspace.recent_visit.read | I5 | CE-HOME-005 |

**Akzeptanzkriterien**

1. Contract: je Endpunkt dieses Pakets ≥ 1 Szenario mit Golden vom Original (Erfolg, Berechtigungsfehler, Validierungsfehler); Replay grün (L5).
2. Permission-Matrix (05 Anhang B) für alle Endpunkte dieses Pakets als L3-Test grün; Tenant-Isolation geprüft.
3. Signal-Stores strukturgleich zum MobX-Original (`store-parity-check`), Vitest je Action (L2).
4. E2E-Specs dieses Pakets grün gegen Original **und** funk. (Dual-Target, Pflichtszenarien 15 §3.9.3).
5. Visual-/DOM-/a11y-Prüfpunkte der betroffenen Screens (09 §4.14, 15 §3.10.2) innerhalb der Schwellwerte 15 §3.10.3 (Chromium); i18n-Schlüssel nur aus den Original-Locales (de/en).
6. `ce-coverage-check --ids CE-HOME-001,CE-HOME-002,CE-HOME-003,CE-HOME-004,CE-HOME-005,CE-HOME-006,CE-HOME-007` grün (Mindestebenen 15 Anhang B).

**Testumfang**

- Pflicht-Ebenen (aus 15 Anhang B): L1, L2, L3, L5, L7, L8
- Testprojekte: `Funk.Home.Tests`
- E2E-Specs (`frontend/apps/e2e/`): `web/home/home.spec.ts`

### WP-I5-004 – Stickies: Widget, Seite, Bearbeitung (ED-5)

| Merkmal | Wert |
|---|---|
| Inkrement | I5 |
| Typ (DoD 15 §3.15.3) | V – Vertikaler Schnitt |
| Größe | M |
| parallelisierbar | ja |
| Abhängigkeiten | WP-I5-003 |
| CE-IDs | CE-HOME-008, CE-HOME-009, CE-HOME-010 |

**Ziel.** Stickies-Widget, Stickies-Seite mit Masonry und Sticky-Editor (Lite + Sticky-Toolbar, Farbpalette).

**Enthaltene CE-IDs**

| CE-ID | Feature | Status (15 Anh. B) | Inkrement laut 15 | Pflicht-Ebenen | Testprojekt | E2E-Spec |
|---|---|---|---|---|---|---|
| CE-HOME-008 | Stickies-Widget | übernommen | I5 | L1 L2 L3 L5 L7 L8 | Funk.Home.Tests | `web/home/stickies.spec.ts` |
| CE-HOME-009 | Stickies-Seite | übernommen | I5 | L1 L2 L3 L5 L7 L8 | Funk.Home.Tests | `web/home/stickies.spec.ts` |
| CE-HOME-010 | Sticky bearbeiten | übernommen | I5 | L1 L2 L3 L5 L7 L8 | Funk.Home.Tests | `web/home/stickies.spec.ts` |

**Betroffene Module/Libs in `funk.`**

- Backend: `src/modules/Home/Funk.Home` (Stickies)
- Frontend: `frontend/libs/web/stickies`
- Frontend: `frontend/libs/web/core/editor` (sticky-editor)

**Referenzdokumente**

- Architektur: 04 §4.15
- Architektur: 10 §1.5 (ED-5)
- Analyse/Feature: `analysis/10a-frontend-workspace-projekt-navigation.md` §3.6, §2.6
- Analyse/Feature: `analysis/08-frontend-web-architektur.md` §3.8
- Analyse/Feature: `analysis/03-api-intern-workspace-projekt-user.md` §3.7
- Analyse/Feature: `analysis/02a-datenmodell-kern.md` §3.6
- Analyse/Feature: `analysis/10b-frontend-cycles-modules-pages-views-weitere.md` §2.17
- Feature-Katalog: `features/10-ce-feature-katalog.md` (Einträge CE-HOME-008, CE-HOME-009, CE-HOME-010)

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- Backend: `apps/api/plane/app/views/workspace/sticky.py`, `apps/api/plane/db/models/sticky.py`, `apps/api/plane/api/views/sticky.py`
- Frontend: `apps/web/components/stickies/widget.tsx`, `apps/web/components/stickies/layout/stickies-truncated.tsx`, `apps/web/app/(all)/[workspaceSlug]/(projects)/stickies/page.tsx`, `apps/web/app/(all)/[workspaceSlug]/(projects)/stickies/header.tsx`, `apps/web/components/stickies/layout/stickies-infinite.tsx`, `apps/web/components/stickies/layout/stickies-list.tsx`, `apps/web/components/stickies/modal/search.tsx`, `apps/web/store/sticky/sticky.store.ts`, `apps/web/services/sticky.service.ts`, `apps/web/components/stickies/sticky/root.tsx`, `apps/web/components/stickies/sticky/inputs.tsx`, `apps/web/components/stickies/sticky/sticky-item-drag-handle.tsx`, `apps/web/components/stickies/delete-modal.tsx`, `apps/web/components/stickies/sticky/use-operations.tsx`, `apps/web/components/editor/sticky-editor/editor.tsx`, `apps/web/components/editor/sticky-editor/toolbar.tsx`, `apps/web/components/editor/sticky-editor/color-palette.tsx`

**Endpunkte (Katalog 04, `architecture/_data/endpoints.json`; 5 registriert)**

| EP | Methode | Pfad | Oberfläche | Handler | Permission | Inkr. 04 | CE-IDs |
|---|---|---|---|---|---|---|---|
| EP-0491 | GET | `/api/workspaces/{slug}/stickies/` | App | StickyEndpoints.ListStickiesQuery | workspace.sticky.read | I5 | CE-HOME-008, CE-HOME-009 |
| EP-0492 | POST | `/api/workspaces/{slug}/stickies/` | App | StickyEndpoints.CreateStickyCommand | workspace.sticky.create | I5 | CE-HOME-010 |
| EP-0493 | GET | `/api/workspaces/{slug}/stickies/{pk}/` | App | StickyEndpoints.GetStickyQuery | workspace.sticky.read | I5 | CE-HOME-010 |
| EP-0494 | PATCH | `/api/workspaces/{slug}/stickies/{pk}/` | App | StickyEndpoints.UpdateStickyCommand | workspace.sticky.update | I5 | CE-HOME-010 |
| EP-0495 | DELETE | `/api/workspaces/{slug}/stickies/{pk}/` | App | StickyEndpoints.DeleteStickyCommand | workspace.sticky.delete | I5 | CE-HOME-010 |

**Akzeptanzkriterien**

1. Contract: je Endpunkt dieses Pakets ≥ 1 Szenario mit Golden vom Original (Erfolg, Berechtigungsfehler, Validierungsfehler); Replay grün (L5).
2. Permission-Matrix (05 Anhang B) für alle Endpunkte dieses Pakets als L3-Test grün; Tenant-Isolation geprüft.
3. Signal-Stores strukturgleich zum MobX-Original (`store-parity-check`), Vitest je Action (L2).
4. E2E-Specs dieses Pakets grün gegen Original **und** funk. (Dual-Target, Pflichtszenarien 15 §3.9.3).
5. Visual-/DOM-/a11y-Prüfpunkte der betroffenen Screens (09 §4.14, 15 §3.10.2) innerhalb der Schwellwerte 15 §3.10.3 (Chromium); i18n-Schlüssel nur aus den Original-Locales (de/en).
6. `ce-coverage-check --ids CE-HOME-008,CE-HOME-009,CE-HOME-010` grün (Mindestebenen 15 Anhang B).

**Testumfang**

- Pflicht-Ebenen (aus 15 Anhang B): L1, L2, L3, L5, L7, L8
- Testprojekte: `Funk.Home.Tests`
- E2E-Specs (`frontend/apps/e2e/`): `web/home/stickies.spec.ts`

### WP-I5-005 – Benachrichtigungen erzeugen: In-App, Mentions, automatisches Abonnieren, Zähler-Push

| Merkmal | Wert |
|---|---|
| Inkrement | I5 |
| Typ (DoD 15 §3.15.3) | B – Backend-only |
| Größe | M |
| parallelisierbar | nein |
| Abhängigkeiten | WP-I4-999, WP-I5-202, WP-I0-207 |
| CE-IDs | CE-NOTIF-001, CE-NOTIF-002, CE-NOTIF-003 |

**Ziel.** `ActivityNotificationConsumer` (Queue `notifications`) aus `funk.work_item_activity.recorded.v1` mit Original-Algorithmus, Mention-Benachrichtigungen, Auto-Subscribe; `funk.notification.created.v1` → `RealtimeFanOutConsumer` → Zähler-Push über SignalR.

**Enthaltene CE-IDs**

| CE-ID | Feature | Status (15 Anh. B) | Inkrement laut 15 | Pflicht-Ebenen | Testprojekt | E2E-Spec |
|---|---|---|---|---|---|---|
| CE-NOTIF-001 | Erzeugung von In-App-Benachrichtigungen | übernommen | I5 | L1 L2 L3 L7 L8 L9 (LT-11) | Funk.Notifications.Tests | `web/notifications/inbox.spec.ts` |
| CE-NOTIF-002 | Erwähnungs-Benachrichtigungen | übernommen | I5 | L1 L2 L3 L7 L8 | Funk.Notifications.Tests | `web/notifications/inbox.spec.ts` |
| CE-NOTIF-003 | Automatisches Abonnieren | übernommen | I5 | L1 L2 L3 L7 L8 | Funk.Notifications.Tests | `web/notifications/inbox.spec.ts` |

**Betroffene Module/Libs in `funk.`**

- Backend: `src/modules/Notifications/Funk.Notifications`
- Backend: `src/modules/RealtimeEvents/Funk.RealtimeEvents/Consumers/RealtimeFanOutConsumer.cs`

**Referenzdokumente**

- Architektur: 06 §3.10, §3.12, §5.7, D06-ADR-10, -12
- Architektur: 07 §3.16.4
- Architektur: 17 ABG-106
- Analyse/Feature: `analysis/07-hintergrundjobs-mail-storage-webhooks.md` §2.8, §3.2
- Analyse/Feature: `analysis/02b-datenmodell-arbeitsobjekte.md` §3.11
- Feature-Katalog: `features/10-ce-feature-katalog.md` (Einträge CE-NOTIF-001, CE-NOTIF-002, CE-NOTIF-003)

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- Backend: `apps/api/plane/bgtasks/notification_task.py`, `apps/api/plane/db/models/notification.py`, `apps/api/plane/app/views/notification/base.py`, `apps/api/plane/db/models/notification.py:13-69`, `apps/api/plane/bgtasks/issue_activities_task.py`

**Akzeptanzkriterien**

1. `LiveEventLatencyTests`: Zähler-Push < 2 s mit und ohne Valkey (Z-104); Notification-Daten (`data`-JSON) byte-gleich zum Original-Golden.
2. Contract-Szenarien mit Original-Golden für alle HTTP-Endpunkte dieses Pakets; Replay grün.
3. Job-/Consumer-Tests: Idempotenz (Inbox), Retry/Backoff, Zeitsteuerung mit `FixedClock`; neue Ereignistypen im Event-Katalog-Snapshot.
4. Bei Cron-Jobs: Registrierung in `CronRegistrationTests` mit Original-Zeit (UTC).
5. `ce-coverage-check --ids CE-NOTIF-001,CE-NOTIF-002,CE-NOTIF-003` grün (Mindestebenen 15 Anhang B).

**Testumfang**

- Pflicht-Ebenen (aus 15 Anhang B): L1, L2, L3, L7, L8, L9
- Testprojekte: `Funk.Notifications.Tests`
- E2E-Specs (`frontend/apps/e2e/`): `web/notifications/inbox.spec.ts`

### WP-I5-006 – Inbox: Seite, Liste, Filter/Optionen, lesen/archivieren/snoozen, Detail

| Merkmal | Wert |
|---|---|
| Inkrement | I5 |
| Typ (DoD 15 §3.15.3) | V – Vertikaler Schnitt |
| Größe | L |
| parallelisierbar | ja |
| Abhängigkeiten | WP-I5-005 |
| CE-IDs | CE-NOTIF-004, CE-NOTIF-005, CE-NOTIF-006, CE-NOTIF-007 |

**Ziel.** Inbox-Seite mit Benachrichtigungsliste, Filtern und Optionen, Lesen/Archivieren/Snoozen und Detail.

**Enthaltene CE-IDs**

| CE-ID | Feature | Status (15 Anh. B) | Inkrement laut 15 | Pflicht-Ebenen | Testprojekt | E2E-Spec |
|---|---|---|---|---|---|---|
| CE-NOTIF-004 | Inbox-Seite und Benachrichtigungsliste | übernommen | I5 | L1 L2 L3 L5 L7 L8 | Funk.Notifications.Tests | `web/notifications/inbox.spec.ts` |
| CE-NOTIF-005 | Inbox-Filter und -Optionen | übernommen | I5 | L1 L2 L3 L5 L7 L8 | Funk.Notifications.Tests | `web/notifications/inbox.spec.ts` |
| CE-NOTIF-006 | Benachrichtigung lesen, archivieren, snoozen | übernommen | I5 | L1 L2 L3 L5 L7 L8 | Funk.Notifications.Tests | `web/notifications/inbox.spec.ts` |
| CE-NOTIF-007 | Benachrichtigungs-Detail | übernommen | I5 | L1 L2 L3 L5 L7 L8 | Funk.Notifications.Tests | `web/notifications/inbox.spec.ts` |

**Betroffene Module/Libs in `funk.`**

- Backend: `src/modules/Notifications/Funk.Notifications`
- Frontend: `frontend/libs/web/notifications`

**Referenzdokumente**

- Architektur: 04 §4.16
- Architektur: 03 §3.4.14
- Analyse/Feature: `analysis/10a-frontend-workspace-projekt-navigation.md` §2.7
- Analyse/Feature: `analysis/08-frontend-web-architektur.md` §3.8
- Analyse/Feature: `analysis/03-api-intern-workspace-projekt-user.md` §3.8
- Analyse/Feature: `analysis/13b-shared-packages-i18n.md` §2.2
- Feature-Katalog: `features/10-ce-feature-katalog.md` (Einträge CE-NOTIF-004, CE-NOTIF-005, CE-NOTIF-006, CE-NOTIF-007)

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- Backend: `apps/api/plane/app/views/notification/base.py`
- Frontend: `apps/web/components/workspace-notifications/sidebar/root.tsx`, `apps/web/components/workspace-notifications/sidebar/notification-card/item.tsx`, `apps/web/components/workspace-notifications/sidebar/empty-state.tsx`, `apps/web/app/(all)/[workspaceSlug]/(projects)/notifications/page.tsx`, `apps/web/app/(all)/[workspaceSlug]/(projects)/notifications/layout.tsx`, `apps/web/store/notifications/workspace-notifications.store.ts`, `apps/web/services/workspace-notification.service.ts`, `packages/constants/src/notification.ts`, `packages/services/src/workspace/notification.service.ts`, `apps/web/components/workspace-notifications/sidebar/filters/menu/root.tsx`, `apps/web/components/workspace-notifications/sidebar/filters/applied-filter.tsx`, `apps/web/components/workspace-notifications/sidebar/header/options/root.tsx`, `apps/web/components/workspace-notifications/sidebar/notification-card/options/root.tsx`, `apps/web/components/workspace-notifications/sidebar/notification-card/options/snooze/root.tsx`, `apps/web/components/workspace-notifications/sidebar/notification-card/options/snooze/modal.tsx`, `apps/web/store/notifications/notification.ts`, `apps/web/components/workspace-notifications/root.tsx`, `apps/web/components/workspace-notifications/sidebar/notification-card/content.tsx`

**Endpunkte (Katalog 04, `architecture/_data/endpoints.json`; 10 registriert)**

| EP | Methode | Pfad | Oberfläche | Handler | Permission | Inkr. 04 | CE-IDs |
|---|---|---|---|---|---|---|---|
| EP-0496 | GET | `/api/workspaces/{slug}/users/notifications/` | App | NotificationEndpoints.ListNotificationsQuery | workspace.notification.read | I5 | CE-NOTIF-004, CE-NOTIF-005 |
| EP-0497 | POST | `/api/workspaces/{slug}/users/notifications/mark-all-read/` | App | NotificationEndpoints.MarkAllNotificationsReadCommand | workspace.notification.update | I5 | CE-NOTIF-006 |
| EP-0498 | GET | `/api/workspaces/{slug}/users/notifications/unread/` | App | NotificationEndpoints.GetUnreadNotificationCountsQuery | workspace.notification.read | I5 | CE-NOTIF-004 |
| EP-0499 | GET | `/api/workspaces/{slug}/users/notifications/{pk}/` | App | NotificationEndpoints.GetNotificationQuery | workspace.notification.read | I5 | CE-NOTIF-007 |
| EP-0500 | PATCH | `/api/workspaces/{slug}/users/notifications/{pk}/` | App | NotificationEndpoints.UpdateNotificationCommand | workspace.notification.update | I5 | CE-NOTIF-007 |
| EP-0501 | DELETE | `/api/workspaces/{slug}/users/notifications/{pk}/` | App | NotificationEndpoints.DeleteNotificationCommand | workspace.notification.delete | I5 | CE-NOTIF-007 |
| EP-0502 | POST | `/api/workspaces/{slug}/users/notifications/{pk}/archive/` | App | NotificationEndpoints.ArchiveNotificationCommand | workspace.notification.update | I5 | CE-NOTIF-006 |
| EP-0503 | DELETE | `/api/workspaces/{slug}/users/notifications/{pk}/archive/` | App | NotificationEndpoints.UnarchiveNotificationCommand | workspace.notification.update | I5 | CE-NOTIF-006 |
| EP-0504 | POST | `/api/workspaces/{slug}/users/notifications/{pk}/read/` | App | NotificationEndpoints.MarkNotificationReadCommand | workspace.notification.update | I5 | CE-NOTIF-006 |
| EP-0505 | DELETE | `/api/workspaces/{slug}/users/notifications/{pk}/read/` | App | NotificationEndpoints.MarkNotificationUnreadCommand | workspace.notification.delete | I5 | CE-NOTIF-006 |

**Akzeptanzkriterien**

1. Contract: je Endpunkt dieses Pakets ≥ 1 Szenario mit Golden vom Original (Erfolg, Berechtigungsfehler, Validierungsfehler); Replay grün (L5).
2. Permission-Matrix (05 Anhang B) für alle Endpunkte dieses Pakets als L3-Test grün; Tenant-Isolation geprüft.
3. Signal-Stores strukturgleich zum MobX-Original (`store-parity-check`), Vitest je Action (L2).
4. E2E-Specs dieses Pakets grün gegen Original **und** funk. (Dual-Target, Pflichtszenarien 15 §3.9.3).
5. Visual-/DOM-/a11y-Prüfpunkte der betroffenen Screens (09 §4.14, 15 §3.10.2) innerhalb der Schwellwerte 15 §3.10.3 (Chromium); i18n-Schlüssel nur aus den Original-Locales (de/en).
6. `ce-coverage-check --ids CE-NOTIF-004,CE-NOTIF-005,CE-NOTIF-006,CE-NOTIF-007` grün (Mindestebenen 15 Anhang B).

**Testumfang**

- Pflicht-Ebenen (aus 15 Anhang B): L1, L2, L3, L5, L7, L8
- Testprojekte: `Funk.Notifications.Tests`
- E2E-Specs (`frontend/apps/e2e/`): `web/notifications/inbox.spec.ts`

### WP-I5-007 – E-Mail-Benachrichtigungen mit 5-Minuten-Bündelung und Einstellungen

| Merkmal | Wert |
|---|---|
| Inkrement | I5 |
| Typ (DoD 15 §3.15.3) | B – Backend-only |
| Größe | M |
| parallelisierbar | ja |
| Abhängigkeiten | WP-I5-005, WP-I1-102 |
| CE-IDs | CE-NOTIF-008, CE-NOTIF-009 |

**Ziel.** Cron `notifications.email_digest` (alle 5 min) gruppiert je (Empfänger, Work Item), Versand-Job mit genau den IDs der Gruppe, Template M12, Benachrichtigungseinstellungen.

**Enthaltene CE-IDs**

| CE-ID | Feature | Status (15 Anh. B) | Inkrement laut 15 | Pflicht-Ebenen | Testprojekt | E2E-Spec |
|---|---|---|---|---|---|---|
| CE-NOTIF-008 | E-Mail-Benachrichtigungen (5-Minuten-Bündelung) | übernommen | I5 | L1 L2 L3 L4 L6 L7 L8 (G-MAIL) | Funk.Notifications.Tests | `web/notifications/inbox.spec.ts` |
| CE-NOTIF-009 | E-Mail-Benachrichtigungseinstellungen | übernommen | I5 | L1 L2 L3 L5 L7 L8 | Funk.Notifications.Tests | `web/notifications/inbox.spec.ts` |

**Betroffene Module/Libs in `funk.`**

- Backend: `src/modules/Notifications/Funk.Notifications`
- Frontend: `frontend/libs/web/settings` (notifications)

**Referenzdokumente**

- Architektur: 06 §3.11, D06-ADR-11
- Analyse/Feature: `analysis/07-hintergrundjobs-mail-storage-webhooks.md` §3.3, §2.9
- Analyse/Feature: `analysis/02b-datenmodell-arbeitsobjekte.md` §3.11
- Analyse/Feature: `analysis/10a-frontend-workspace-projekt-navigation.md` §2.13
- Analyse/Feature: `analysis/03-api-intern-workspace-projekt-user.md` §2.9
- Feature-Katalog: `features/10-ce-feature-katalog.md` (Einträge CE-NOTIF-008, CE-NOTIF-009)

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- Backend: `apps/api/plane/bgtasks/email_notification_task.py`, `apps/api/templates/emails/notifications/issue-updates.html`, `apps/api/plane/celery.py`, `apps/api/plane/db/models/notification.py:81-149`, `apps/api/plane/app/views/notification/base.py`, `apps/api/plane/db/models/notification.py`
- Frontend: `apps/web/components/settings/profile/content/pages/notifications/root.tsx`, `apps/web/components/settings/profile/content/pages/notifications/email-notification-form.tsx`, `apps/web/services/user.service.ts`

**Endpunkte (Katalog 04, `architecture/_data/endpoints.json`; 2 registriert)**

| EP | Methode | Pfad | Oberfläche | Handler | Permission | Inkr. 04 | CE-IDs |
|---|---|---|---|---|---|---|---|
| EP-0506 | GET | `/api/users/me/notification-preferences/` | App | NotificationPreferenceEndpoints.GetNotificationPreferencesQuery | user.notification_preference.read | I5 | CE-NOTIF-009 |
| EP-0507 | PATCH | `/api/users/me/notification-preferences/` | App | NotificationPreferenceEndpoints.UpdateNotificationPreferencesCommand | user.notification_preference.update | I5 | CE-NOTIF-009 |

**Akzeptanzkriterien**

1. Contract-Szenarien mit Original-Golden für alle HTTP-Endpunkte dieses Pakets; Replay grün.
2. Job-/Consumer-Tests: Idempotenz (Inbox), Retry/Backoff, Zeitsteuerung mit `FixedClock`; neue Ereignistypen im Event-Katalog-Snapshot.
3. Bei Cron-Jobs: Registrierung in `CronRegistrationTests` mit Original-Zeit (UTC).
4. `ce-coverage-check --ids CE-NOTIF-008,CE-NOTIF-009` grün (Mindestebenen 15 Anhang B).

**Testumfang**

- Pflicht-Ebenen (aus 15 Anhang B): L1, L2, L3, L4, L5, L6, L7, L8
- Testprojekte: `Funk.Notifications.Tests`
- E2E-Specs (`frontend/apps/e2e/`): `web/notifications/inbox.spec.ts`

### WP-I5-008 – Suche: Globale Suche, Entity-Suche für Mentions/Picker, Work-Item-Picker

| Merkmal | Wert |
|---|---|
| Inkrement | I5 |
| Typ (DoD 15 §3.15.3) | V – Vertikaler Schnitt |
| Größe | M |
| parallelisierbar | ja |
| Abhängigkeiten | WP-I5-201 |
| CE-IDs | CE-SRCH-001, CE-SRCH-002, CE-SRCH-003 |

**Ziel.** Endpunkte SR-01 (global), SR-03 (Entity) und SR-02 (Work-Item-Picker) mit `icontains`→`ILIKE`-Semantik, Trigramm-Indizes und Sichtbarkeitsprädikaten.

**Enthaltene CE-IDs**

| CE-ID | Feature | Status (15 Anh. B) | Inkrement laut 15 | Pflicht-Ebenen | Testprojekt | E2E-Spec |
|---|---|---|---|---|---|---|
| CE-SRCH-001 | Globale Suche | übernommen | I5 | L1 L2 L3 L5 L7 L8 L9 (LT-09) | Funk.Search.Tests | `web/search/search.spec.ts` |
| CE-SRCH-002 | Entity-Suche für Mentions und Picker | übernommen | I5 | L1 L2 L3 L5 L7 L8 | Funk.Search.Tests | `web/search/search.spec.ts` |
| CE-SRCH-003 | Work-Item-Picker-Suche | übernommen | I5 | L1 L2 L3 L5 L7 L8 | Funk.Search.Tests | `web/search/search.spec.ts` |

**Betroffene Module/Libs in `funk.`**

- Backend: `src/modules/Search/Funk.Search`
- Backend: `tests/modules/Funk.Search.Tests`
- Frontend: `frontend/libs/web/core` (search services)

**Referenzdokumente**

- Architektur: 11 §3.2, §3.4–§3.6, §3.8, §3.9, §5.3–§5.5
- Architektur: 04 §4.17
- Analyse/Feature: `analysis/03-api-intern-workspace-projekt-user.md` §3.14
- Analyse/Feature: `analysis/06-auth-sicherheit-querschnitt.md` §2.13
- Feature-Katalog: `features/10-ce-feature-katalog.md` (Einträge CE-SRCH-001, CE-SRCH-002, CE-SRCH-003)

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- Backend: `apps/api/plane/app/views/search/base.py`, `apps/api/plane/app/views/search/issue.py`, `apps/api/plane/utils/issue_search.py`
- Frontend: `apps/web/services/workspace.service.ts`, `apps/web/services/project/project.service.ts`

**Endpunkte (Katalog 04, `architecture/_data/endpoints.json`; 2 registriert)**

| EP | Methode | Pfad | Oberfläche | Handler | Permission | Inkr. 04 | CE-IDs |
|---|---|---|---|---|---|---|---|
| EP-0508 | GET | `/api/workspaces/{slug}/entity-search/` | App | SearchEndpoints.SearchEntitiesQuery | workspace.search.read | I5 | CE-SRCH-002, CE-WI-044 |
| EP-0509 | GET | `/api/workspaces/{slug}/search/` | App | SearchEndpoints.GlobalSearchQuery | workspace.search.read | I5 | CE-SRCH-001, CE-SRCH-004 |

**Akzeptanzkriterien**

1. SQL-Pläne ohne Seq-Scan bei Workspace-Filter (11 §3.9); 403 für Nicht-Mitglieder (O-D11-01, DEV-SRCH-011).
2. Contract: je Endpunkt dieses Pakets ≥ 1 Szenario mit Golden vom Original (Erfolg, Berechtigungsfehler, Validierungsfehler); Replay grün (L5).
3. Permission-Matrix (05 Anhang B) für alle Endpunkte dieses Pakets als L3-Test grün; Tenant-Isolation geprüft.
4. Signal-Stores strukturgleich zum MobX-Original (`store-parity-check`), Vitest je Action (L2).
5. E2E-Specs dieses Pakets grün gegen Original **und** funk. (Dual-Target, Pflichtszenarien 15 §3.9.3).
6. Visual-/DOM-/a11y-Prüfpunkte der betroffenen Screens (09 §4.14, 15 §3.10.2) innerhalb der Schwellwerte 15 §3.10.3 (Chromium); i18n-Schlüssel nur aus den Original-Locales (de/en).
7. `ce-coverage-check --ids CE-SRCH-001,CE-SRCH-002,CE-SRCH-003` grün (Mindestebenen 15 Anhang B).

**Testumfang**

- Pflicht-Ebenen (aus 15 Anhang B): L1, L2, L3, L5, L7, L8, L9
- Testprojekte: `Funk.Search.Tests`
- E2E-Specs (`frontend/apps/e2e/`): `web/search/search.spec.ts`

### WP-I5-009 – Power-K Command Palette mit Navigations-, Erstell-, Kontext-, Account-/Preferences-/Hilfebefehlen und Shortcuts

| Merkmal | Wert |
|---|---|
| Inkrement | I5 |
| Typ (DoD 15 §3.15.3) | F – Frontend-only |
| Größe | L |
| parallelisierbar | ja |
| Abhängigkeiten | WP-I5-008, WP-I5-202 |
| CE-IDs | CE-SRCH-004, CE-SRCH-005, CE-SRCH-006, CE-SRCH-007, CE-SRCH-008, CE-SRCH-009 |

**Ziel.** Power-K (cmdk-DOM nachgebaut) mit allen CE-Befehlsgruppen über `POWER_K_COMMANDS` und Tastatur-Shortcuts.

> **Hinweis:** Power-K zeigt bei Pages den Projekt-Identifier nicht an (Original-Defekt `project__identifiers`, O-D11-04) – optisch 1:1 belassen, Eintrag in `ui-deviations.yaml`.

**Enthaltene CE-IDs**

| CE-ID | Feature | Status (15 Anh. B) | Inkrement laut 15 | Pflicht-Ebenen | Testprojekt | E2E-Spec |
|---|---|---|---|---|---|---|
| CE-SRCH-004 | Power-K Command Palette | übernommen | I5 | L2 L7 L8 | Frontend-only | `web/search/power-k.spec.ts` |
| CE-SRCH-005 | Power-K-Navigationsbefehle | übernommen | I5 | L2 L7 L8 | Frontend-only | `web/search/power-k.spec.ts` |
| CE-SRCH-006 | Power-K-Erstellbefehle | übernommen | I5 | L2 L7 L8 | Frontend-only | `web/search/power-k.spec.ts` |
| CE-SRCH-007 | Power-K-Kontextbefehle | übernommen | I5 | L2 L7 L8 | Frontend-only | `web/search/power-k.spec.ts` |
| CE-SRCH-008 | Power-K-Account-, Preferences- und Hilfebefehle | übernommen | I5 | L2 L7 L8 | Frontend-only | `web/search/power-k.spec.ts` |
| CE-SRCH-009 | Tastatur-Shortcuts | übernommen | I5 | L2 L7 L8 | Frontend-only | `web/search/power-k.spec.ts` |

**Betroffene Module/Libs in `funk.`**

- Frontend: `frontend/libs/web/power-k`

**Referenzdokumente**

- Architektur: 08 §3.10
- Architektur: 11 §3.11
- Architektur: 09 §4.14
- Analyse/Feature: `analysis/10a-frontend-workspace-projekt-navigation.md` §2.9, §3.9
- Analyse/Feature: `analysis/08-frontend-web-architektur.md` §3.3
- Analyse/Feature: `analysis/13a-designsystem-ui-tokens.md` §2.15
- Analyse/Feature: `analysis/03-api-intern-workspace-projekt-user.md` §3.14
- Feature-Katalog: `features/10-ce-feature-katalog.md` (Einträge CE-SRCH-004, CE-SRCH-005, CE-SRCH-006, CE-SRCH-007, CE-SRCH-008, CE-SRCH-009)

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- Backend: `apps/api/plane/app/views/search/base.py`
- Frontend: `apps/web/components/power-k/ui/modal/wrapper.tsx`, `apps/web/components/power-k/ui/modal/commands-list.tsx`, `apps/web/components/power-k/ui/modal/header.tsx`, `apps/web/components/power-k/ui/modal/footer.tsx`, `apps/web/components/navigation/top-nav-power-k.tsx`, `apps/web/components/power-k/projects-app-provider.tsx`, `apps/web/store/base-power-k.store.ts`, `apps/web/styles/power-k.css`, `apps/web/services/workspace.service.ts`, `apps/web/components/power-k/config/navigation/commands.ts`, `apps/web/components/power-k/config/navigation/root.ts`, `apps/web/components/power-k/config/creation/command.ts`, `apps/web/components/power-k/config/creation/root.ts`, `apps/web/components/power-k/ui/pages/context-based/root.tsx`, `apps/web/components/power-k/ui/pages/context-based/work-item/commands.ts`, `apps/web/components/power-k/ui/pages/context-based/cycle/commands.ts`, `apps/web/components/power-k/ui/pages/context-based/module/commands.tsx`, `apps/web/components/power-k/ui/pages/context-based/page/commands.ts`, `apps/web/components/power-k/core/context-detector.ts`, `apps/web/components/power-k/config/account-commands.ts`, `apps/web/components/power-k/config/preferences-commands.ts`, `apps/web/components/power-k/config/help-commands.ts`, `apps/web/components/power-k/config/miscellaneous-commands.ts`, `apps/web/components/power-k/ui/pages/preferences/timezone-menu.tsx`, `apps/web/components/power-k/core/shortcut-handler.ts`, `apps/web/components/power-k/core/registry.ts`, `apps/web/components/power-k/global-shortcuts.tsx`, `apps/web/components/power-k/ui/modal/shortcuts-root.tsx`

**Akzeptanzkriterien**

1. Galerie-Eintrag mit allen Varianten/Zuständen; DOM-Vertrag = Referenz-Galerie; Visual in allen Themes (Chromium).
2. Tastatur/Fokus (AX3/AX4) wie Original; portierte `packages/blocks`-Tests grün (falls vorhanden).
3. `ce-coverage-check --ids CE-SRCH-004,CE-SRCH-005,CE-SRCH-006,CE-SRCH-007,CE-SRCH-008,CE-SRCH-009` grün (Mindestebenen 15 Anhang B).

**Testumfang**

- Pflicht-Ebenen (aus 15 Anhang B): L2, L7, L8
- Testprojekte: `Frontend-only`
- E2E-Specs (`frontend/apps/e2e/`): `web/search/power-k.spec.ts`

### WP-I5-010 – Your work: Summary, Work-Item-Tabs, Activity, Profil-Sidebar

| Merkmal | Wert |
|---|---|
| Inkrement | I5 |
| Typ (DoD 15 §3.15.3) | V – Vertikaler Schnitt |
| Größe | M |
| parallelisierbar | ja |
| Abhängigkeiten | WP-I4-999 |
| CE-IDs | CE-PROF-008, CE-PROF-009, CE-PROF-010, CE-PROF-011 |

**Ziel.** Profilseiten „Your work“ mit Zusammenfassung, Work-Item-Tabs (Layout-Kontext Profil), Activity und Profil-Sidebar.

**Enthaltene CE-IDs**

| CE-ID | Feature | Status (15 Anh. B) | Inkrement laut 15 | Pflicht-Ebenen | Testprojekt | E2E-Spec |
|---|---|---|---|---|---|---|
| CE-PROF-008 | Your work – Summary | übernommen | I5 | L1 L2 L3 L5 L7 L8 | Funk.Workspaces.Tests | `web/profile/your-work.spec.ts` |
| CE-PROF-009 | Your work – Work-Item-Tabs | übernommen | I5 | L1 L2 L3 L5 L7 L8 | Funk.Workspaces.Tests | `web/profile/your-work.spec.ts` |
| CE-PROF-010 | Your work – Activity | übernommen | I5 | L1 L2 L3 L5 L7 L8 | Funk.Workspaces.Tests | `web/profile/your-work.spec.ts` |
| CE-PROF-011 | Profil-Sidebar | übernommen | I5 | L1 L2 L3 L5 L7 L8 | Funk.Workspaces.Tests | `web/profile/your-work.spec.ts` |

**Betroffene Module/Libs in `funk.`**

- Backend: `src/modules/Workspaces/Funk.Workspaces` (Member-Profile)
- Frontend: `frontend/libs/web/profile`

**Referenzdokumente**

- Architektur: 04 §4.3
- Architektur: 08 §4.1
- Analyse/Feature: `analysis/10a-frontend-workspace-projekt-navigation.md` §2.8
- Analyse/Feature: `analysis/08-frontend-web-architektur.md` §2.2
- Analyse/Feature: `analysis/03-api-intern-workspace-projekt-user.md` §3.4
- Feature-Katalog: `features/10-ce-feature-katalog.md` (Einträge CE-PROF-008, CE-PROF-009, CE-PROF-010, CE-PROF-011)

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- Backend: `apps/api/plane/app/views/workspace/user.py`, `apps/api/plane/app/views/workspace/base.py`
- Frontend: `apps/web/app/(all)/[workspaceSlug]/(projects)/profile/[userId]/page.tsx`, `apps/web/components/profile/overview/stats.tsx`, `apps/web/components/profile/overview/workload.tsx`, `apps/web/components/profile/overview/priority-distribution.tsx`, `apps/web/components/profile/overview/state-distribution.tsx`, `apps/web/components/profile/overview/activity.tsx`, `apps/web/app/(all)/[workspaceSlug]/(projects)/profile/[userId]/layout.tsx`, `apps/web/app/(all)/[workspaceSlug]/(projects)/profile/[userId]/[profileViewId]/page.tsx`, `apps/web/app/(all)/[workspaceSlug]/(projects)/profile/[userId]/activity/page.tsx`, `apps/web/services/user.service.ts`, `apps/web/store/user/profile.store.ts`, `apps/web/components/profile/profile-issues.tsx`, `apps/web/components/profile/profile-issues-filter.tsx`, `apps/web/app/(all)/[workspaceSlug]/(projects)/profile/[userId]/mobile-header.tsx`, `apps/web/components/profile/activity/activity-list.tsx`, `apps/web/components/profile/activity/download-button.tsx`, `apps/web/components/profile/activity/workspace-activity-list.tsx`, `apps/web/components/profile/sidebar.tsx`, `apps/web/components/profile/time.tsx`, `apps/web/app/(all)/[workspaceSlug]/(projects)/profile/[userId]/header.tsx`, `apps/web/app/(all)/[workspaceSlug]/(projects)/profile/[userId]/navbar.tsx`

**Endpunkte (Katalog 04, `architecture/_data/endpoints.json`; 6 registriert)**

| EP | Methode | Pfad | Oberfläche | Handler | Permission | Inkr. 04 | CE-IDs |
|---|---|---|---|---|---|---|---|
| EP-0058 | GET | `/api/users/me/activities/` | App | UserActivityEndpoints.ListCurrentUserActivitiesQuery | user.user_activity.read | I5 | CE-PROF-010 |
| EP-0106 | GET | `/api/workspaces/{slug}/user-activity/{user_id}/` | App | MemberProfileEndpoints.ListMemberActivityQuery | workspace.member_profile.read | I5 | CE-PROF-010 |
| EP-0107 | POST | `/api/workspaces/{slug}/user-activity/{user_id}/export/` | App | MemberProfileEndpoints.ExportMemberActivityCommand | workspace.member_profile.export | I5 | CE-PROF-010 |
| EP-0108 | GET | `/api/workspaces/{slug}/user-issues/{user_id}/` | App | MemberProfileEndpoints.ListMemberWorkItemsQuery | workspace.member_profile.read | I5 | CE-PROF-009 |
| EP-0109 | GET | `/api/workspaces/{slug}/user-profile/{user_id}/` | App | MemberProfileEndpoints.GetMemberProfileQuery | workspace.member_profile.read | I5 | CE-PROF-008 |
| EP-0110 | GET | `/api/workspaces/{slug}/user-stats/{user_id}/` | App | MemberProfileEndpoints.GetMemberStatsQuery | workspace.member_profile.read | I5 | CE-PROF-008 |

**Akzeptanzkriterien**

1. Contract: je Endpunkt dieses Pakets ≥ 1 Szenario mit Golden vom Original (Erfolg, Berechtigungsfehler, Validierungsfehler); Replay grün (L5).
2. Permission-Matrix (05 Anhang B) für alle Endpunkte dieses Pakets als L3-Test grün; Tenant-Isolation geprüft.
3. Signal-Stores strukturgleich zum MobX-Original (`store-parity-check`), Vitest je Action (L2).
4. E2E-Specs dieses Pakets grün gegen Original **und** funk. (Dual-Target, Pflichtszenarien 15 §3.9.3).
5. Visual-/DOM-/a11y-Prüfpunkte der betroffenen Screens (09 §4.14, 15 §3.10.2) innerhalb der Schwellwerte 15 §3.10.3 (Chromium); i18n-Schlüssel nur aus den Original-Locales (de/en).
6. `ce-coverage-check --ids CE-PROF-008,CE-PROF-009,CE-PROF-010,CE-PROF-011` grün (Mindestebenen 15 Anhang B).

**Testumfang**

- Pflicht-Ebenen (aus 15 Anhang B): L1, L2, L3, L5, L7, L8
- Testprojekte: `Funk.Workspaces.Tests`
- E2E-Specs (`frontend/apps/e2e/`): `web/profile/your-work.spec.ts`

### WP-I5-201 – Erweiterungspunkt G1/B6: ISearchProvider, IIndexingPipeline, search_documents, vector, NullEmbeddingGenerator, IIndexDocumentEnricher

| Merkmal | Wert |
|---|---|
| Inkrement | I5 |
| Typ (DoD 15 §3.15.3) | X – Erweiterungspunkt 🧱 |
| Größe | M |
| parallelisierbar | nein |
| Abhängigkeiten | WP-I4-999 |
| CE-IDs | – (keine; Erweiterungspunkt) |
| Andockstelle | 01 §1.4 G1/B6; 16 §3.3.0 E-24; 16 §4.6 (Träger CE-SRCH-001…003) |

**Ziel.** Such-Abstraktion `ISearchProvider` (`PostgresSearchProvider`), Indexierungs-Pipeline als `IEventConsumer` auf der CE-Queue `indexing`, Tabelle `search_documents` (`tsvector`, Surrogat-PK `id`), Extension `vector` aktiv, `IEmbeddingGenerator<string, Embedding<float>>` mit `NullEmbeddingGenerator`, `IIndexDocumentEnricher` (E-24), `SearchVisibilityFilter`.

**Betroffene Module/Libs in `funk.`**

- Backend: `src/platform/Funk.Platform.Search`
- Backend: `src/platform/Funk.Platform.Ai`
- Backend: `src/modules/Search/Funk.Search`

**Referenzdokumente**

- Architektur: 11 §3.3, §3.10, §5.1, §5.6, §6
- Architektur: 16 §5.14, §3.2.7, §3.3.0 E-24
- Architektur: 17 ABG-122, ABG-125

**Akzeptanzkriterien**

1. Index-Konsistenz-Job `indexing.reconcile` repariert absichtlich gelöschte Index-Zeilen; Fake-Enricher ergänzt Felder ohne CE-Änderung (Typ X).
2. Contract (Interface/Schema/Token) + CE-Default-Implementierung; Eintrag in `tests/extension-points.yaml`.
3. Test „CE-Default = Original-Verhalten“ (Contract-Replay unverändert grün).
4. Test mit Fake-Erweiterung aus `Funk.BuildingBlocks.Testing/Extensions` bzw. `provideFakeExtensions()` beweist Erweiterbarkeit ohne CE-Änderung (DoD Typ X).

**Testumfang**

- Typ-X-Tests (CE-Default unverändert, Fake-Erweiterung wirkt ohne CE-Änderung), L0-Inventarabgleich `ExtensionPointInventoryTests`/`extension-registry-check`.

### WP-I5-202 – Erweiterungspunkte UI I5: HOME_WIDGETS, POWER_K_COMMANDS, SEARCH_RESULT_RENDERERS, erste Nutzung LIVE_EVENT_HANDLERS

| Merkmal | Wert |
|---|---|
| Inkrement | I5 |
| Typ (DoD 15 §3.15.3) | X – Erweiterungspunkt 🧱 |
| Größe | S |
| parallelisierbar | nein |
| Abhängigkeiten | WP-I4-999 |
| CE-IDs | – (keine; Erweiterungspunkt) |
| Andockstelle | 16 §1.4 Zeile I5; 16 §4.6 (Träger CE-HOME-001/-002, CE-NOTIF-001, CE-SRCH-004) |

**Ziel.** Frontend-Registries für Home-Widgets (E-14, CE-Widgets aus `apps/web/core/components/home/widgets`), Power-K-Befehle und Such-Ergebnis-Renderer; erste Handler für `LIVE_EVENT_HANDLERS` (Notification-Zähler).

**Betroffene Module/Libs in `funk.`**

- Frontend: `frontend/libs/web/extensions/src/{home,power-k,search}.ts`
- Frontend: `frontend/libs/web/notifications/src/live/`

**Referenzdokumente**

- Architektur: 08 §6.4
- Architektur: 16 §1.4 Zeile I5
- Architektur: 06 §5.12

**Akzeptanzkriterien**

1. Fake-Widget, Fake-Befehl und Fake-Renderer erscheinen ohne CE-Änderung (Typ X).
2. Contract (Interface/Schema/Token) + CE-Default-Implementierung; Eintrag in `tests/extension-points.yaml`.
3. Test „CE-Default = Original-Verhalten“ (Contract-Replay unverändert grün).
4. Test mit Fake-Erweiterung aus `Funk.BuildingBlocks.Testing/Extensions` bzw. `provideFakeExtensions()` beweist Erweiterbarkeit ohne CE-Änderung (DoD Typ X).

**Testumfang**

- Typ-X-Tests (CE-Default unverändert, Fake-Erweiterung wirkt ohne CE-Änderung), L0-Inventarabgleich `ExtensionPointInventoryTests`/`extension-registry-check`.

### WP-I5-999 – Abnahme I5 – Überblick (G5)

| Merkmal | Wert |
|---|---|
| Inkrement | I5 |
| Typ (DoD 15 §3.15.3) | A – Inkrement-Abnahme |
| Größe | S |
| parallelisierbar | nein |
| Abhängigkeiten | WP-I5-001, WP-I5-002, WP-I5-003, WP-I5-004, WP-I5-005, WP-I5-006, WP-I5-007, WP-I5-008, WP-I5-009, WP-I5-010, WP-I5-201, WP-I5-202 |
| CE-IDs | – (keine; Baustein/Spike/Abnahme) |

**Ziel.** Inkrement-Abnahme I5 nach G5 und Meilenstein M5.

**Referenzdokumente**

- Architektur: plan/01-roadmap-ce.md §4 (M5)
- Architektur: 15 §3.16 Zeile I5

**Akzeptanzkriterien**

1. Alle Abnahmekriterien M5 erfüllt; `docs/acceptance/I5.md` generiert.
2. G5 `--inc <In> --strict` grün: `ce-coverage-check`, `original-test-ledger`, Parity-Report (0 ungenehmigte Abweichungen, Endpunkt-Abdeckung des Inkrements 100 %), Visual/a11y, Lastziele, Security-Report.
3. Demo-Video der Kern-Flows (`--video on`) und Abnahmebericht `docs/acceptance/<In>.md`; fachliche Abnahme durch den Auftraggeber.

**Testumfang**

- G5 `--inc I5`.

## 4.7 Inkrement I6

### WP-I6-001 – God Mode: Abmeldung, Fehleransicht, Dashboard-Shell, Header, Konto-Menü, Hilfe, Unsaved-Dialog, Kopierfelder, 404

| Merkmal | Wert |
|---|---|
| Inkrement | I6 |
| Typ (DoD 15 §3.15.3) | V – Vertikaler Schnitt |
| Größe | L |
| parallelisierbar | ja |
| Abhängigkeiten | WP-I5-999, WP-I6-203 |
| CE-IDs | CE-INST-008, CE-INST-009, CE-INST-010, CE-INST-011, CE-INST-012, CE-INST-013, CE-INST-014, CE-INST-015, CE-INST-016 |

**Ziel.** Vollständige Admin-Shell mit Sidebar, Breadcrumb-Header, Konto-Menü mit Theme-Umschaltung, Hilfe-Bereich, Dialog für ungespeicherte Änderungen, Kopierfeldern für funk.-URLs, Fehler- und 404-Seiten.

**Enthaltene CE-IDs**

| CE-ID | Feature | Status (15 Anh. B) | Inkrement laut 15 | Pflicht-Ebenen | Testprojekt | E2E-Spec |
|---|---|---|---|---|---|---|
| CE-INST-008 | Admin-Abmeldung | angepasst | I6 | L1 L2 L3 L5 L6 L7 L8 | Funk.Instance.Tests | `admin/admin-shell.spec.ts` |
| CE-INST-009 | Instanzfehler-Ansicht (God Mode) | übernommen | I6 | L1 L2 L3 L5 L7 L8 | Funk.Instance.Tests | `admin/admin-shell.spec.ts` |
| CE-INST-010 | Dashboard-Shell mit Sidebar | übernommen | I6 | L1 L2 L3 L5 L7 L8 | Funk.Instance.Tests | `admin/admin-shell.spec.ts` |
| CE-INST-011 | Header mit Breadcrumb | übernommen | I6 | L1 L2 L3 L5 L7 L8 | Funk.Instance.Tests | `admin/admin-shell.spec.ts` |
| CE-INST-012 | Konto-Menü mit Theme-Umschaltung | übernommen | I6 | L1 L2 L3 L5 L7 L8 | Funk.Instance.Tests | `admin/admin-shell.spec.ts` |
| CE-INST-013 | Hilfe-Bereich der Admin-Sidebar | übernommen | I6 | L1 L2 L3 L5 L7 L8 | Funk.Instance.Tests | `admin/admin-shell.spec.ts` |
| CE-INST-014 | Dialog für ungespeicherte Änderungen (God Mode) | übernommen | I6 | L1 L2 L3 L5 L7 L8 | Funk.Instance.Tests | `admin/admin-shell.spec.ts` |
| CE-INST-015 | Kopierfelder für Plane-URLs | übernommen | I6 | L1 L2 L3 L5 L7 L8 | Funk.Instance.Tests | `admin/admin-shell.spec.ts` |
| CE-INST-016 | 404-Seite und Fehlerbehandlung (God Mode) | übernommen | I6 | L1 L2 L3 L5 L7 L8 | Funk.Instance.Tests | `admin/admin-shell.spec.ts` |

**Betroffene Module/Libs in `funk.`**

- Backend: `src/modules/Instance/Funk.Instance`
- Frontend: `frontend/apps/admin`
- Frontend: `frontend/libs/admin/{core,common}`

**Referenzdokumente**

- Architektur: 08 §4.2
- Architektur: 05 §3.8
- Architektur: 09 §4.14
- Analyse/Feature: `analysis/11-frontend-admin-space.md` §3.4, §3.1, §2.4, §2.5, §3.6, §3.10, §3.14
- Analyse/Feature: `analysis/05-api-public-v1-space-instanz.md` §3.23
- Feature-Katalog: `features/10-ce-feature-katalog.md` (Einträge CE-INST-008, CE-INST-009, CE-INST-010, CE-INST-011, CE-INST-012, CE-INST-013, CE-INST-014, CE-INST-015, CE-INST-016)

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- Backend: `apps/api/plane/license/api/views/admin.py`, `apps/api/plane/authentication/middleware/session.py`, `apps/api/plane/authentication/utils/login.py`
- Frontend: `apps/admin/app/(all)/(dashboard)/sidebar-dropdown.tsx`, `apps/admin/store/root.store.ts`, `apps/admin/components/instance/failure.tsx`, `apps/admin/app/(all)/(dashboard)/layout.tsx`, `apps/admin/app/(all)/(dashboard)/sidebar.tsx`, `apps/admin/app/(all)/(dashboard)/sidebar-menu.tsx`, `apps/admin/hooks/use-sidebar-menu/core.ts`, `apps/admin/store/theme.store.ts`, `apps/admin/components/common/header/index.tsx`, `apps/admin/components/common/header/core.ts`, `apps/admin/app/(all)/(dashboard)/sidebar-help-section.tsx`, `apps/admin/components/common/confirm-discard-modal.tsx`, `apps/admin/components/common/copy-field.tsx`, `apps/admin/app/components/404.tsx`, `apps/admin/app/root.tsx`, `apps/admin/lib/b-progress/AppProgressBar.tsx`

**Akzeptanzkriterien**

1. Contract: je Endpunkt dieses Pakets ≥ 1 Szenario mit Golden vom Original (Erfolg, Berechtigungsfehler, Validierungsfehler); Replay grün (L5).
2. Permission-Matrix (05 Anhang B) für alle Endpunkte dieses Pakets als L3-Test grün; Tenant-Isolation geprüft.
3. Signal-Stores strukturgleich zum MobX-Original (`store-parity-check`), Vitest je Action (L2).
4. E2E-Specs dieses Pakets grün gegen Original **und** funk. (Dual-Target, Pflichtszenarien 15 §3.9.3).
5. Visual-/DOM-/a11y-Prüfpunkte der betroffenen Screens (09 §4.14, 15 §3.10.2) innerhalb der Schwellwerte 15 §3.10.3 (Chromium); i18n-Schlüssel nur aus den Original-Locales (de/en).
6. `ce-coverage-check --ids CE-INST-008,CE-INST-009,CE-INST-010,CE-INST-011,CE-INST-012,CE-INST-013,CE-INST-014,CE-INST-015,CE-INST-016` grün (Mindestebenen 15 Anhang B).

**Testumfang**

- Pflicht-Ebenen (aus 15 Anhang B): L1, L2, L3, L5, L6, L7, L8
- Testprojekte: `Funk.Instance.Tests`
- E2E-Specs (`frontend/apps/e2e/`): `admin/admin-shell.spec.ts`

### WP-I6-002 – God Mode: Allgemeine Einstellungen, SMTP, Test-E-Mail, AI-Einstellungen, Bildbibliotheken

| Merkmal | Wert |
|---|---|
| Inkrement | I6 |
| Typ (DoD 15 §3.15.3) | V – Vertikaler Schnitt |
| Größe | M |
| parallelisierbar | ja |
| Abhängigkeiten | WP-I6-001, WP-I1-102 |
| CE-IDs | CE-INST-017, CE-INST-018, CE-INST-019, CE-INST-025, CE-INST-026 |

**Ziel.** Instanz-Einstellungen General, SMTP mit Test-E-Mail, AI-Einstellungen (OpenAI-kompatibler Endpunkt, lokal betreibbar) und Unsplash; Secrets maskiert (`MaskInstanceSecrets = true`).

**Enthaltene CE-IDs**

| CE-ID | Feature | Status (15 Anh. B) | Inkrement laut 15 | Pflicht-Ebenen | Testprojekt | E2E-Spec |
|---|---|---|---|---|---|---|
| CE-INST-017 | Allgemeine Instanzeinstellungen | übernommen | I6 | L1 L2 L3 L5 L7 L8 | Funk.Instance.Tests | `admin/admin-settings.spec.ts` |
| CE-INST-018 | SMTP-Konfiguration | übernommen | I6 | L1 L2 L3 L5 L7 L8 | Funk.Instance.Tests | `admin/admin-settings.spec.ts` |
| CE-INST-019 | Test-E-Mail senden | übernommen | I6 | L1 L2 L3 L4 L5 L6 L7 L8 (G-MAIL) | Funk.Instance.Tests | `admin/admin-settings.spec.ts` |
| CE-INST-025 | AI-Einstellungen | übernommen | I6 | L1 L2 L3 L5 L7 L8 | Funk.Instance.Tests | `admin/admin-settings.spec.ts` |
| CE-INST-026 | Bildbibliotheken (Unsplash) | übernommen | I6 | L1 L2 L3 L5 L7 L8 | Funk.Instance.Tests | `admin/admin-settings.spec.ts` |

**Betroffene Module/Libs in `funk.`**

- Backend: `src/modules/Instance/Funk.Instance`
- Frontend: `frontend/libs/admin/instance`

**Referenzdokumente**

- Architektur: 05 §4.4
- Architektur: 11 §3.13, §3.17
- Architektur: 04 §4.2
- Architektur: 17 Z-112
- Analyse/Feature: `analysis/11-frontend-admin-space.md` §3.7, §3.8, §3.11, §3.12
- Analyse/Feature: `analysis/05-api-public-v1-space-instanz.md` §2.7, §3.24
- Analyse/Feature: `analysis/07-hintergrundjobs-mail-storage-webhooks.md` §2.17
- Feature-Katalog: `features/10-ce-feature-katalog.md` (Einträge CE-INST-017, CE-INST-018, CE-INST-019, CE-INST-025, CE-INST-026)

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- Backend: `apps/api/plane/license/api/views/instance.py`, `apps/api/plane/license/api/views/configuration.py`, `apps/api/plane/license/utils/instance_value.py`, `apps/api/plane/utils/instance_config_variables/core.py`, `apps/api/plane/license/utils/encryption.py`, `apps/api/plane/license/management/commands/configure_instance.py`
- Frontend: `apps/admin/app/(all)/(dashboard)/general/page.tsx`, `apps/admin/app/(all)/(dashboard)/general/form.tsx`, `apps/admin/store/instance.store.ts`, `apps/admin/app/(all)/(dashboard)/email/page.tsx`, `apps/admin/app/(all)/(dashboard)/email/email-config-form.tsx`, `apps/admin/app/(all)/(dashboard)/email/test-email-modal.tsx`, `apps/admin/app/(all)/(dashboard)/ai/page.tsx`, `apps/admin/app/(all)/(dashboard)/ai/form.tsx`, `apps/admin/app/(all)/(dashboard)/image/page.tsx`, `apps/admin/app/(all)/(dashboard)/image/form.tsx`

**Endpunkte (Katalog 04, `architecture/_data/endpoints.json`; 5 registriert)**

| EP | Methode | Pfad | Oberfläche | Handler | Permission | Inkr. 04 | CE-IDs |
|---|---|---|---|---|---|---|---|
| EP-0073 | GET | `/api/instances/configurations/` | Instance | InstanceConfigurationEndpoints.ListInstanceConfigurationsQuery | instance.configuration.read | I6 | CE-INST-002, CE-INST-017, CE-INST-018, CE-INST-025, CE-INST-026 |
| EP-0074 | PATCH | `/api/instances/configurations/` | Instance | InstanceConfigurationEndpoints.UpdateInstanceConfigurationsCommand | instance.configuration.update | I6 | CE-INST-002, CE-INST-017, CE-INST-018, CE-INST-025, CE-INST-026, CE-INST-028 |
| EP-0075 | DELETE | `/api/instances/configurations/disable-email-feature/` | Instance | InstanceConfigurationEndpoints.DisableEmailFeatureCommand | instance.configuration.delete | I6 | CE-INST-018 |
| EP-0076 | POST | `/api/instances/email-credentials-check/` | Instance | InstanceConfigurationEndpoints.SendTestEmailCommand | instance.configuration.create | I6 | CE-INST-019 |
| EP-0078 | PATCH | `/api/instances/` | Instance | InstanceEndpoints.UpdateInstanceCommand | instance.settings.update | I6 | CE-INST-017 |

**Akzeptanzkriterien**

1. Contract: je Endpunkt dieses Pakets ≥ 1 Szenario mit Golden vom Original (Erfolg, Berechtigungsfehler, Validierungsfehler); Replay grün (L5).
2. Permission-Matrix (05 Anhang B) für alle Endpunkte dieses Pakets als L3-Test grün; Tenant-Isolation geprüft.
3. Signal-Stores strukturgleich zum MobX-Original (`store-parity-check`), Vitest je Action (L2).
4. E2E-Specs dieses Pakets grün gegen Original **und** funk. (Dual-Target, Pflichtszenarien 15 §3.9.3).
5. Visual-/DOM-/a11y-Prüfpunkte der betroffenen Screens (09 §4.14, 15 §3.10.2) innerhalb der Schwellwerte 15 §3.10.3 (Chromium); i18n-Schlüssel nur aus den Original-Locales (de/en).
6. `ce-coverage-check --ids CE-INST-017,CE-INST-018,CE-INST-019,CE-INST-025,CE-INST-026` grün (Mindestebenen 15 Anhang B).

**Testumfang**

- Pflicht-Ebenen (aus 15 Anhang B): L1, L2, L3, L4, L5, L6, L7, L8
- Testprojekte: `Funk.Instance.Tests`
- E2E-Specs (`frontend/apps/e2e/`): `admin/admin-settings.spec.ts`

### WP-I6-003 – God Mode: Workspace-Liste, Workspace-Anlage sperren, Workspace anlegen, Willkommens-Popup

| Merkmal | Wert |
|---|---|
| Inkrement | I6 |
| Typ (DoD 15 §3.15.3) | V – Vertikaler Schnitt |
| Größe | M |
| parallelisierbar | ja |
| Abhängigkeiten | WP-I6-001 |
| CE-IDs | CE-INST-027, CE-INST-028, CE-INST-029, CE-INST-030 |

**Ziel.** Workspace-Verwaltung der Instanz.

**Enthaltene CE-IDs**

| CE-ID | Feature | Status (15 Anh. B) | Inkrement laut 15 | Pflicht-Ebenen | Testprojekt | E2E-Spec |
|---|---|---|---|---|---|---|
| CE-INST-027 | Workspace-Liste der Instanz | übernommen | I6 | L1 L2 L3 L5 L7 L8 | Funk.Instance.Tests | `admin/admin-workspaces.spec.ts` |
| CE-INST-028 | Workspace-Anlage sperren | übernommen | I6 | L1 L2 L3 L5 L7 L8 | Funk.Instance.Tests | `admin/admin-workspaces.spec.ts` |
| CE-INST-029 | Workspace anlegen (God Mode) | übernommen | I6 | L1 L2 L3 L5 L7 L8 | Funk.Instance.Tests | `admin/admin-workspaces.spec.ts` |
| CE-INST-030 | Willkommens-Popup 'Create workspace' | übernommen | I6 | L1 L2 L3 L5 L7 L8 | Funk.Instance.Tests | `admin/admin-workspaces.spec.ts` |

**Betroffene Module/Libs in `funk.`**

- Backend: `src/modules/Instance/Funk.Instance`
- Backend: `src/modules/Workspaces/Funk.Workspaces.Contracts`
- Frontend: `frontend/libs/admin/workspace`

**Referenzdokumente**

- Architektur: 04 §4.2
- Architektur: 08 §4.2
- Analyse/Feature: `analysis/11-frontend-admin-space.md` §3.13, §3.14
- Analyse/Feature: `analysis/05-api-public-v1-space-instanz.md` §2.7, §3.24
- Analyse/Feature: `analysis/13b-shared-packages-i18n.md` §2.7
- Feature-Katalog: `features/10-ce-feature-katalog.md` (Einträge CE-INST-027, CE-INST-028, CE-INST-029, CE-INST-030)

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- Backend: `apps/api/plane/license/api/views/workspace.py`, `apps/api/plane/license/api/serializers/workspace.py`, `apps/api/plane/utils/constants.py`, `apps/api/plane/license/api/views/configuration.py`, `apps/api/plane/license/utils/encryption.py`, `apps/api/plane/license/utils/instance_value.py`, `apps/api/plane/utils/instance_config_variables/core.py`, `apps/api/plane/license/management/commands/configure_instance.py`
- Frontend: `apps/admin/app/(all)/(dashboard)/workspace/page.tsx`, `apps/admin/components/workspace/list-item.tsx`, `apps/admin/store/workspace.store.ts`, `packages/services/src/instance/instance.service.ts`, `packages/services/src/workspace/instance-workspace.service.ts`, `packages/types/src/instance/base.ts`, `packages/types/src/instance/auth.ts`, `apps/admin/app/(all)/(dashboard)/workspace/create/form.tsx`, `packages/constants/src/workspace.ts`, `packages/utils/src/validation.ts`, `apps/admin/components/common/new-user-popup.tsx`, `apps/admin/store/instance.store.ts`

**Endpunkte (Katalog 04, `architecture/_data/endpoints.json`; 3 registriert)**

| EP | Methode | Pfad | Oberfläche | Handler | Permission | Inkr. 04 | CE-IDs |
|---|---|---|---|---|---|---|---|
| EP-0080 | GET | `/api/instances/workspace-slug-check/` | Instance | InstanceWorkspaceEndpoints.CheckWorkspaceSlugQuery | instance.workspace.read | I6 | CE-INST-029 |
| EP-0081 | GET | `/api/instances/workspaces/` | Instance | InstanceWorkspaceEndpoints.ListInstanceWorkspacesQuery | instance.workspace.read | I6 | CE-INST-027 |
| EP-0082 | POST | `/api/instances/workspaces/` | Instance | InstanceWorkspaceEndpoints.CreateWorkspaceCommand | instance.workspace.create | I6 | CE-INST-029 |

**Akzeptanzkriterien**

1. Contract: je Endpunkt dieses Pakets ≥ 1 Szenario mit Golden vom Original (Erfolg, Berechtigungsfehler, Validierungsfehler); Replay grün (L5).
2. Permission-Matrix (05 Anhang B) für alle Endpunkte dieses Pakets als L3-Test grün; Tenant-Isolation geprüft.
3. Signal-Stores strukturgleich zum MobX-Original (`store-parity-check`), Vitest je Action (L2).
4. E2E-Specs dieses Pakets grün gegen Original **und** funk. (Dual-Target, Pflichtszenarien 15 §3.9.3).
5. Visual-/DOM-/a11y-Prüfpunkte der betroffenen Screens (09 §4.14, 15 §3.10.2) innerhalb der Schwellwerte 15 §3.10.3 (Chromium); i18n-Schlüssel nur aus den Original-Locales (de/en).
6. `ce-coverage-check --ids CE-INST-027,CE-INST-028,CE-INST-029,CE-INST-030` grün (Mindestebenen 15 Anhang B).

**Testumfang**

- Pflicht-Ebenen (aus 15 Anhang B): L1, L2, L3, L5, L7, L8
- Testprojekte: `Funk.Instance.Tests`
- E2E-Specs (`frontend/apps/e2e/`): `admin/admin-workspaces.spec.ts`

### WP-I6-004 – Projekt veröffentlichen (Publish-Modal, Board-Einstellungen, Metadaten)

| Merkmal | Wert |
|---|---|
| Inkrement | I6 |
| Typ (DoD 15 §3.15.3) | V – Vertikaler Schnitt |
| Größe | M |
| parallelisierbar | ja |
| Abhängigkeiten | WP-I5-999 |
| CE-IDs | CE-SPACE-001, CE-SPACE-002 |

**Ziel.** Publish-Modal im Web und Board-Einstellungen/-Metadaten (`deploy_boards`, Anchor als 32-Zeichen-Hex).

**Enthaltene CE-IDs**

| CE-ID | Feature | Status (15 Anh. B) | Inkrement laut 15 | Pflicht-Ebenen | Testprojekt | E2E-Spec |
|---|---|---|---|---|---|---|
| CE-SPACE-001 | Projekt veröffentlichen (Publish) | übernommen | I6 | L1 L2 L3 L5 L7 L8 | Funk.PublicSpace.Tests | `web/space/publish.spec.ts` |
| CE-SPACE-002 | Board-Einstellungen und Metadaten | übernommen | I6 | L1 L2 L3 L5 L7 L8 | Funk.PublicSpace.Tests | `web/space/publish.spec.ts` |

**Betroffene Module/Libs in `funk.`**

- Backend: `src/modules/PublicSpace/Funk.PublicSpace`, `Funk.PublicSpace.Contracts`
- Frontend: `frontend/libs/web/project-publish`

**Referenzdokumente**

- Architektur: 04 §4.18
- Architektur: 03 §3.4.15
- Analyse/Feature: `analysis/10a-frontend-workspace-projekt-navigation.md` §2.11
- Analyse/Feature: `analysis/03-api-intern-workspace-projekt-user.md` §2.6
- Analyse/Feature: `analysis/05-api-public-v1-space-instanz.md` §2.6, §3.17
- Analyse/Feature: `analysis/02a-datenmodell-kern.md` §3.17
- Analyse/Feature: `analysis/13b-shared-packages-i18n.md` §2.7
- Feature-Katalog: `features/10-ce-feature-katalog.md` (Einträge CE-SPACE-001, CE-SPACE-002)

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- Backend: `apps/api/plane/app/views/project/base.py`, `apps/api/plane/app/serializers/project.py`, `apps/api/plane/db/models/deploy_board.py`, `apps/api/plane/db/models/project.py`, `apps/api/plane/space/views/issue.py`, `apps/api/plane/space/views/project.py`, `apps/api/plane/space/views/meta.py`, `apps/api/plane/space/urls/project.py`
- Frontend: `apps/web/components/project/publish-project/modal.tsx`, `apps/web/services/project/project-publish.service.ts`, `packages/types/src/publish.ts`, `packages/services/src/issue/sites-issue.service.ts`, `packages/services/src/project/sites-publish.service.ts`, `packages/services/src/label/sites-label.service.ts`, `packages/services/src/state/sites-state.service.ts`, `packages/services/src/user/sites-member.service.ts`, `packages/services/src/module/sites-module.service.ts`, `packages/services/src/cycle/sites-cycle.service.ts`

**Endpunkte (Katalog 04, `architecture/_data/endpoints.json`; 7 registriert)**

| EP | Methode | Pfad | Oberfläche | Handler | Permission | Inkr. 04 | CE-IDs |
|---|---|---|---|---|---|---|---|
| EP-0510 | GET | `/api/workspaces/{slug}/projects/{project_id}/project-deploy-boards/` | App | DeployBoardEndpoints.ListDeployBoardsQuery | project.publish.read | I6 | CE-SPACE-001, CE-SPACE-002 |
| EP-0511 | POST | `/api/workspaces/{slug}/projects/{project_id}/project-deploy-boards/` | App | DeployBoardEndpoints.CreateDeployBoardCommand | project.publish.create | I6 | CE-SPACE-001, CE-SPACE-002 |
| EP-0512 | GET | `/api/workspaces/{slug}/projects/{project_id}/project-deploy-boards/{pk}/` | App | DeployBoardEndpoints.GetDeployBoardQuery | project.publish.read | I6 | CE-SPACE-001, CE-SPACE-002 |
| EP-0513 | PATCH | `/api/workspaces/{slug}/projects/{project_id}/project-deploy-boards/{pk}/` | App | DeployBoardEndpoints.UpdateDeployBoardCommand | project.publish.update | I6 | CE-SPACE-001, CE-SPACE-002 |
| EP-0514 | DELETE | `/api/workspaces/{slug}/projects/{project_id}/project-deploy-boards/{pk}/` | App | DeployBoardEndpoints.DeleteDeployBoardCommand | project.publish.delete | I6 | CE-SPACE-001, CE-SPACE-002 |
| EP-0520 | GET | `/api/public/anchor/{anchor}/meta/` | Space | PublicBoardEndpoints.GetBoardMetaQuery | public.board.read | I6 | CE-SPACE-002, CE-SPACE-017 |
| EP-0522 | GET | `/api/public/anchor/{anchor}/settings/` | Space | PublicBoardEndpoints.GetBoardSettingsQuery | public.board.read | I6 | CE-SPACE-002, CE-SPACE-017 |

**Akzeptanzkriterien**

1. Contract: je Endpunkt dieses Pakets ≥ 1 Szenario mit Golden vom Original (Erfolg, Berechtigungsfehler, Validierungsfehler); Replay grün (L5).
2. Permission-Matrix (05 Anhang B) für alle Endpunkte dieses Pakets als L3-Test grün; Tenant-Isolation geprüft.
3. Signal-Stores strukturgleich zum MobX-Original (`store-parity-check`), Vitest je Action (L2).
4. E2E-Specs dieses Pakets grün gegen Original **und** funk. (Dual-Target, Pflichtszenarien 15 §3.9.3).
5. Visual-/DOM-/a11y-Prüfpunkte der betroffenen Screens (09 §4.14, 15 §3.10.2) innerhalb der Schwellwerte 15 §3.10.3 (Chromium); i18n-Schlüssel nur aus den Original-Locales (de/en).
6. `ce-coverage-check --ids CE-SPACE-001,CE-SPACE-002` grün (Mindestebenen 15 Anhang B).

**Testumfang**

- Pflicht-Ebenen (aus 15 Anhang B): L1, L2, L3, L5, L7, L8
- Testprojekte: `Funk.PublicSpace.Tests`
- E2E-Specs (`frontend/apps/e2e/`): `web/space/publish.spec.ts`

### WP-I6-005 – Space-App: Shell, Login-Einstieg über Keycloak, Fehler-/404-Seiten, Legacy-Redirects, Social-Meta, iframe, Badge (inkl. Nachweis entfallener Space-Logins)

| Merkmal | Wert |
|---|---|
| Inkrement | I6 |
| Typ (DoD 15 §3.15.3) | V – Vertikaler Schnitt |
| Größe | L |
| parallelisierbar | ja |
| Abhängigkeiten | WP-I6-004, WP-I6-203 |
| CE-IDs | CE-SPACE-008, CE-SPACE-009, CE-SPACE-010, CE-SPACE-011, CE-SPACE-012, CE-SPACE-013, CE-SPACE-014, CE-SPACE-015, CE-SPACE-016, CE-SPACE-017, CE-SPACE-029, CE-SPACE-031, CE-SPACE-032 |

**Ziel.** Space-App unter `/spaces/`: Keycloak-Anmeldung (Client `funk-space`, Theme `funk-space`) mit Rücksprung inkl. Peek-Query, Fehlerbanner, Rechtshinweis, Eingeloggt-Ansicht, Instanzfehler, Legacy-URL-Weiterleitung, OG-Meta-Middleware im Gateway, iframe-Einbettung, Fehler-/404-Seiten und Badge „Powered by funk.“. Die Space-Login-Varianten des Originals entfallen (ADR-008) und sind mit `OidcLoginFlowTests.SpaceLogin_*` belegt.

**Enthaltene CE-IDs**

| CE-ID | Feature | Status (15 Anh. B) | Inkrement laut 15 | Pflicht-Ebenen | Testprojekt | E2E-Spec |
|---|---|---|---|---|---|---|
| CE-SPACE-008 | Space-Login: E-Mail-Check | entfällt – Ersatz: `OidcLoginFlowTests.SpaceLogin_*` (L6), `space/interactions.spec.ts` (Weiterleitung zu Keycloak) | – | – | – | – |
| CE-SPACE-009 | Space-Login und -Sign-up mit Passwort | entfällt – Ersatz: `OidcLoginFlowTests.SpaceLogin_*` (L6), `space/interactions.spec.ts` (Weiterleitung zu Keycloak) | – | – | – | – |
| CE-SPACE-010 | Space-Login mit Unique Code | entfällt – Ersatz: `OidcLoginFlowTests.SpaceLogin_*` (L6), `space/interactions.spec.ts` (Weiterleitung zu Keycloak) | – | – | – | – |
| CE-SPACE-011 | OAuth-Buttons im Space | entfällt – Ersatz: `OidcLoginFlowTests.SpaceLogin_*` (L6), `space/interactions.spec.ts` (Weiterleitung zu Keycloak) | – | – | – | – |
| CE-SPACE-012 | Fehlerbanner aus Auth-Redirects (Space) | angepasst | I6 | L1 L2 L3 L5 L7 L8 | Funk.PublicSpace.Tests | `space/board.spec.ts` |
| CE-SPACE-013 | Rechtshinweis Terms/Privacy (Space) | übernommen | I6 | L1 L2 L3 L5 L7 L8 | Funk.PublicSpace.Tests | `space/board.spec.ts` |
| CE-SPACE-014 | Eingeloggt-Ansicht und next_path-Weiterleitung | angepasst | I6 | L1 L2 L3 L5 L7 L8 | Funk.PublicSpace.Tests | `space/board.spec.ts` |
| CE-SPACE-015 | Instanzfehler-Ansicht (Space) | übernommen | I6 | L1 L2 L3 L5 L7 L8 | Funk.PublicSpace.Tests | `space/board.spec.ts` |
| CE-SPACE-016 | Legacy-URL-Weiterleitung | übernommen | I6 | L1 L2 L3 L5 L7 L8 | Funk.PublicSpace.Tests | `space/board.spec.ts` |
| CE-SPACE-017 | Öffentliches Projekt-Board mit Social-Meta | übernommen | I6 | L1 L2 L3 L5 L6 L7 L8 | Funk.PublicSpace.Tests | `space/board.spec.ts` |
| CE-SPACE-029 | iframe-Einbettung | übernommen | I6 | L1 L2 L3 L5 L7 L8 | Funk.PublicSpace.Tests | `space/board.spec.ts` |
| CE-SPACE-031 | Fehler- und 404-Seiten (Space) | übernommen | I6 | L1 L2 L3 L5 L7 L8 | Funk.PublicSpace.Tests | `space/board.spec.ts` |
| CE-SPACE-032 | 'Powered by Plane Publish'-Badge | übernommen | I6 | L1 L2 L3 L5 L7 L8 | Funk.PublicSpace.Tests | `space/board.spec.ts` |

**Betroffene Module/Libs in `funk.`**

- Backend: `src/hosts/Funk.Gateway` (OgMetaMiddleware)
- Backend: `src/modules/PublicSpace/Funk.PublicSpace`
- Frontend: `frontend/apps/space`
- Frontend: `frontend/libs/space/core`

**Referenzdokumente**

- Architektur: 08 §4.3
- Architektur: 05 §3.3.2, O-D05-05
- Architektur: 14 §3.7.5
- Architektur: 09 §4.14
- Analyse/Feature: `analysis/11-frontend-admin-space.md` §3.17, §2.21, §3.16, §3.15, §3.18, §3.19, §3.29, §2.23
- Analyse/Feature: `analysis/06-auth-sicherheit-querschnitt.md` §3.8
- Analyse/Feature: `analysis/05-api-public-v1-space-instanz.md` §3.17
- Feature-Katalog: `features/10-ce-feature-katalog.md` (Einträge CE-SPACE-008, CE-SPACE-009, CE-SPACE-010, CE-SPACE-011, CE-SPACE-012, CE-SPACE-013, CE-SPACE-014, CE-SPACE-015, CE-SPACE-016, CE-SPACE-017, CE-SPACE-029, CE-SPACE-031, CE-SPACE-032)

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- Backend: `apps/api/plane/authentication/views/space/email.py`, `apps/api/plane/authentication/views/space/magic.py`, `apps/api/plane/space/views/project.py`, `apps/api/plane/space/views/meta.py`, `apps/api/plane/space/urls/project.py`
- Frontend: `apps/space/components/account/auth-forms/auth-root.tsx`, `apps/space/components/account/auth-forms/email.tsx`, `packages/services/src/auth/sites-auth.service.ts`, `apps/space/hooks/oauth/core.tsx`, `apps/space/components/account/auth-forms/password.tsx`, `apps/space/components/account/auth-forms/unique-code.tsx`, `apps/space/hooks/use-timer.tsx`, `packages/blocks/src/auth/oauth/oauth-options.tsx`, `apps/space/helpers/authentication.helper.tsx`, `apps/space/components/account/auth-forms/auth-banner.tsx`, `apps/space/components/account/terms-and-conditions.tsx`, `apps/space/app/page.tsx`, `apps/space/components/account/user-logged-in.tsx`, `apps/space/lib/instance-provider.tsx`, `apps/space/components/instance/instance-failure-view.tsx`, `apps/space/app/[workspaceSlug]/[projectId]/page.tsx`, `apps/space/app/issues/[anchor]/layout.tsx`, `apps/space/app/issues/[anchor]/page.tsx`, `apps/space/store/publish/publish_list.store.ts`, `apps/space/hooks/use-is-in-iframe.tsx`, `apps/space/components/issues/navbar/controls.tsx`, `apps/space/app/not-found.tsx`, `apps/space/components/ui/not-found.tsx`, `apps/space/components/issues/issue-layouts/error.tsx`, `apps/space/app/error.tsx`, `apps/space/components/issues/issue-layouts/issue-layout-HOC.tsx`, `apps/space/components/common/powered-by.tsx`

**Endpunkte (Katalog 04, `architecture/_data/endpoints.json`; 1 registriert)**

| EP | Methode | Pfad | Oberfläche | Handler | Permission | Inkr. 04 | CE-IDs |
|---|---|---|---|---|---|---|---|
| EP-0524 | GET | `/api/public/workspaces/{slug}/projects/{project_id}/anchor/` | Space | PublicBoardEndpoints.GetBoardAnchorQuery | public.board.read | I6 | CE-SPACE-016 |

**Akzeptanzkriterien**

1. Space-Boards bleiben anonym lesbar; Startseite zeigt Anmelde-Button, kein Auto-Redirect (O-D05-05).
2. Contract: je Endpunkt dieses Pakets ≥ 1 Szenario mit Golden vom Original (Erfolg, Berechtigungsfehler, Validierungsfehler); Replay grün (L5).
3. Permission-Matrix (05 Anhang B) für alle Endpunkte dieses Pakets als L3-Test grün; Tenant-Isolation geprüft.
4. Signal-Stores strukturgleich zum MobX-Original (`store-parity-check`), Vitest je Action (L2).
5. E2E-Specs dieses Pakets grün gegen Original **und** funk. (Dual-Target, Pflichtszenarien 15 §3.9.3).
6. Visual-/DOM-/a11y-Prüfpunkte der betroffenen Screens (09 §4.14, 15 §3.10.2) innerhalb der Schwellwerte 15 §3.10.3 (Chromium); i18n-Schlüssel nur aus den Original-Locales (de/en).
7. `ce-coverage-check --ids CE-SPACE-008,CE-SPACE-009,CE-SPACE-010,CE-SPACE-011,CE-SPACE-012,CE-SPACE-013,CE-SPACE-014,CE-SPACE-015,CE-SPACE-016,CE-SPACE-017,CE-SPACE-029,CE-SPACE-031,CE-SPACE-032` grün (Mindestebenen 15 Anhang B).

**Testumfang**

- Pflicht-Ebenen (aus 15 Anhang B): L1, L2, L3, L5, L6, L7, L8
- Testprojekte: `Funk.PublicSpace.Tests`
- E2E-Specs (`frontend/apps/e2e/`): `space/board.spec.ts`

### WP-I6-006 – Space-Board: öffentliche Issue-Liste, Stammdaten, Navbar, List/Kanban read-only, Chips, Filter-Popover, aktive Filter

| Merkmal | Wert |
|---|---|
| Inkrement | I6 |
| Typ (DoD 15 §3.15.3) | V – Vertikaler Schnitt |
| Größe | L |
| parallelisierbar | ja |
| Abhängigkeiten | WP-I6-005 |
| CE-IDs | CE-SPACE-003, CE-SPACE-005, CE-SPACE-018, CE-SPACE-019, CE-SPACE-020, CE-SPACE-021, CE-SPACE-022, CE-SPACE-023 |

**Ziel.** Öffentliches Board mit List- und Kanban-Layout (read-only), Eigenschafts-Chips, Filtern und Navbar.

**Enthaltene CE-IDs**

| CE-ID | Feature | Status (15 Anh. B) | Inkrement laut 15 | Pflicht-Ebenen | Testprojekt | E2E-Spec |
|---|---|---|---|---|---|---|
| CE-SPACE-003 | Öffentliche Issue-Liste | übernommen | I6 | L1 L2 L3 L5 L7 L8 | Funk.PublicSpace.Tests | `space/board.spec.ts` |
| CE-SPACE-005 | Board-Stammdaten | übernommen | I6 | L1 L2 L3 L5 L7 L8 | Funk.PublicSpace.Tests | `space/board.spec.ts` |
| CE-SPACE-018 | Board-Navbar | übernommen | I6 | L1 L2 L3 L5 L7 L8 | Funk.PublicSpace.Tests | `space/board.spec.ts` |
| CE-SPACE-019 | List-Layout (read-only) | übernommen | I6 | L1 L2 L3 L5 L7 L8 | Funk.PublicSpace.Tests | `space/board.spec.ts` |
| CE-SPACE-020 | Kanban-Layout (read-only) | übernommen | I6 | L1 L2 L3 L5 L7 L8 | Funk.PublicSpace.Tests | `space/board.spec.ts` |
| CE-SPACE-021 | Eigenschafts-Chips | übernommen | I6 | L1 L2 L3 L5 L7 L8 | Funk.PublicSpace.Tests | `space/board.spec.ts` |
| CE-SPACE-022 | Filter-Popover | übernommen | I6 | L1 L2 L3 L5 L7 L8 | Funk.PublicSpace.Tests | `space/board.spec.ts` |
| CE-SPACE-023 | Leiste aktiver Filter | übernommen | I6 | L1 L2 L3 L5 L7 L8 | Funk.PublicSpace.Tests | `space/board.spec.ts` |

**Betroffene Module/Libs in `funk.`**

- Backend: `src/modules/PublicSpace/Funk.PublicSpace` (`/api/public/`)
- Frontend: `frontend/libs/space/issues`, `frontend/libs/space/views`

**Referenzdokumente**

- Architektur: 04 §4.18
- Architektur: 08 §4.3, §4.6
- Analyse/Feature: `analysis/05-api-public-v1-space-instanz.md` §3.17, §2.6
- Analyse/Feature: `analysis/11-frontend-admin-space.md` §3.22, §3.20, §3.23, §3.24, §3.25
- Analyse/Feature: `analysis/13b-shared-packages-i18n.md` §2.7
- Feature-Katalog: `features/10-ce-feature-katalog.md` (Einträge CE-SPACE-003, CE-SPACE-005, CE-SPACE-018, CE-SPACE-019, CE-SPACE-020, CE-SPACE-021, CE-SPACE-022, CE-SPACE-023)

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- Backend: `apps/api/plane/space/views/issue.py`, `apps/api/plane/space/utils/grouper.py`, `apps/api/plane/utils/issue_filters.py`, `apps/api/plane/space/views/state.py`, `apps/api/plane/space/views/label.py`, `apps/api/plane/space/views/project.py`, `apps/api/plane/space/views/cycle.py`, `apps/api/plane/space/views/module.py`
- Frontend: `apps/space/components/issues/issue-layouts/list/base-list-root.tsx`, `apps/space/components/issues/issue-layouts/list/list-group.tsx`, `apps/space/components/issues/issue-layouts/list/block.tsx`, `apps/space/components/issues/issue-layouts/kanban/base-kanban-root.tsx`, `apps/space/components/issues/issue-layouts/kanban/default.tsx`, `apps/space/components/issues/issue-layouts/kanban/kanban-group.tsx`, `apps/space/components/issues/issue-layouts/kanban/block.tsx`, `apps/space/components/issues/issue-layouts/kanban/block-reactions.tsx`, `packages/services/src/issue/sites-issue.service.ts`, `packages/services/src/project/sites-publish.service.ts`, `packages/services/src/label/sites-label.service.ts`, `packages/services/src/state/sites-state.service.ts`, `packages/services/src/user/sites-member.service.ts`, `packages/services/src/module/sites-module.service.ts`, `packages/services/src/cycle/sites-cycle.service.ts`, `apps/space/components/issues/navbar/root.tsx`, `apps/space/components/issues/navbar/controls.tsx`, `apps/space/components/issues/navbar/layout-selection.tsx`, `apps/space/components/issues/navbar/theme.tsx`, `apps/space/components/issues/navbar/user-avatar.tsx`, `apps/space/components/issues/issue-layouts/properties/all-properties.tsx`, `apps/space/components/issues/issue-layouts/properties/state.tsx`, `apps/space/components/issues/issue-layouts/properties/priority.tsx`, `apps/space/components/issues/issue-layouts/properties/labels.tsx`, `apps/space/components/issues/issue-layouts/properties/due-date.tsx`, `apps/space/helpers/issue.helper.ts`, `apps/space/components/issues/filters/root.tsx`, `apps/space/components/issues/filters/selection.tsx`, `apps/space/components/issues/filters/priority.tsx`, `apps/space/components/issues/filters/state.tsx`, `apps/space/store/issue-filters.store.ts`, `apps/space/components/issues/filters/applied-filters/root.tsx`, `apps/space/components/issues/filters/applied-filters/filters-list.tsx`

**Endpunkte (Katalog 04, `architecture/_data/endpoints.json`; 6 registriert)**

| EP | Methode | Pfad | Oberfläche | Handler | Permission | Inkr. 04 | CE-IDs |
|---|---|---|---|---|---|---|---|
| EP-0515 | GET | `/api/public/anchor/{anchor}/cycles/` | Space | PublicBoardEndpoints.ListBoardCyclesQuery | public.board.read | I6 | CE-SPACE-005 |
| EP-0516 | GET | `/api/public/anchor/{anchor}/issues/` | Space | PublicBoardEndpoints.ListBoardWorkItemsQuery | public.board.read | I6 | CE-SPACE-003, CE-SPACE-019, CE-SPACE-020, CE-SPACE-022 |
| EP-0518 | GET | `/api/public/anchor/{anchor}/labels/` | Space | PublicBoardEndpoints.ListBoardLabelsQuery | public.board.read | I6 | CE-SPACE-005 |
| EP-0519 | GET | `/api/public/anchor/{anchor}/members/` | Space | PublicBoardEndpoints.ListBoardMembersQuery | public.board.read | I6 | CE-SPACE-005 |
| EP-0521 | GET | `/api/public/anchor/{anchor}/modules/` | Space | PublicBoardEndpoints.ListBoardModulesQuery | public.board.read | I6 | CE-SPACE-005 |
| EP-0523 | GET | `/api/public/anchor/{anchor}/states/` | Space | PublicBoardEndpoints.ListBoardStatesQuery | public.board.read | I6 | CE-SPACE-005 |

**Akzeptanzkriterien**

1. Contract: je Endpunkt dieses Pakets ≥ 1 Szenario mit Golden vom Original (Erfolg, Berechtigungsfehler, Validierungsfehler); Replay grün (L5).
2. Permission-Matrix (05 Anhang B) für alle Endpunkte dieses Pakets als L3-Test grün; Tenant-Isolation geprüft.
3. Signal-Stores strukturgleich zum MobX-Original (`store-parity-check`), Vitest je Action (L2).
4. E2E-Specs dieses Pakets grün gegen Original **und** funk. (Dual-Target, Pflichtszenarien 15 §3.9.3).
5. Visual-/DOM-/a11y-Prüfpunkte der betroffenen Screens (09 §4.14, 15 §3.10.2) innerhalb der Schwellwerte 15 §3.10.3 (Chromium); i18n-Schlüssel nur aus den Original-Locales (de/en).
6. `ce-coverage-check --ids CE-SPACE-003,CE-SPACE-005,CE-SPACE-018,CE-SPACE-019,CE-SPACE-020,CE-SPACE-021,CE-SPACE-022,CE-SPACE-023` grün (Mindestebenen 15 Anhang B).

**Testumfang**

- Pflicht-Ebenen (aus 15 Anhang B): L1, L2, L3, L5, L7, L8
- Testprojekte: `Funk.PublicSpace.Tests`
- E2E-Specs (`frontend/apps/e2e/`): `space/board.spec.ts`

### WP-I6-007 – Space: öffentliches Issue-Detail, Peek, Kommentarbilder/Asset-Auslieferung, Mentions (ED-6)

| Merkmal | Wert |
|---|---|
| Inkrement | I6 |
| Typ (DoD 15 §3.15.3) | V – Vertikaler Schnitt |
| Größe | M |
| parallelisierbar | ja |
| Abhängigkeiten | WP-I6-006 |
| CE-IDs | CE-SPACE-004, CE-SPACE-007, CE-SPACE-024, CE-SPACE-030 |

**Ziel.** Issue-Detail und Peek mit Rich-Editor read-only, Space-Datei-Handler (Anchor-Asset-URLs) und Space-Mentions.

**Enthaltene CE-IDs**

| CE-ID | Feature | Status (15 Anh. B) | Inkrement laut 15 | Pflicht-Ebenen | Testprojekt | E2E-Spec |
|---|---|---|---|---|---|---|
| CE-SPACE-004 | Öffentliches Issue-Detail | übernommen | I6 | L1 L2 L3 L5 L7 L8 | Funk.PublicSpace.Tests | `space/board.spec.ts` |
| CE-SPACE-007 | Kommentarbilder und Asset-Auslieferung | übernommen | I6 | L1 L2 L3 L5 L7 L8 | Funk.PublicSpace.Tests | `space/board.spec.ts` |
| CE-SPACE-024 | Peek-Ansicht eines Work Items | übernommen | I6 | L1 L2 L3 L5 L7 L8 | Funk.PublicSpace.Tests | `space/board.spec.ts` |
| CE-SPACE-030 | Mention-Darstellung (Space) | übernommen | I6 | L1 L2 L3 L5 L7 L8 | Funk.PublicSpace.Tests | `space/board.spec.ts` |

**Betroffene Module/Libs in `funk.`**

- Backend: `src/modules/Assets/Funk.Assets` (Space-Auslieferung)
- Frontend: `frontend/libs/space/editor`, `frontend/libs/space/issues`

**Referenzdokumente**

- Architektur: 10 §1.5 (ED-6)
- Architektur: 04 §4.13, §4.18
- Analyse/Feature: `analysis/05-api-public-v1-space-instanz.md` §2.6, §3.20
- Analyse/Feature: `analysis/11-frontend-admin-space.md` §3.26, §3.27
- Analyse/Feature: `analysis/13b-shared-packages-i18n.md` §3.11
- Feature-Katalog: `features/10-ce-feature-katalog.md` (Einträge CE-SPACE-004, CE-SPACE-007, CE-SPACE-024, CE-SPACE-030)

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- Backend: `apps/api/plane/space/views/issue.py`, `apps/api/plane/space/views/asset.py`, `apps/api/plane/space/urls/asset.py`
- Frontend: `apps/space/components/issues/peek-overview/layout.tsx`, `apps/space/components/issues/peek-overview/side-peek-view.tsx`, `apps/space/components/issues/peek-overview/full-screen-peek-view.tsx`, `apps/space/components/issues/peek-overview/header.tsx`, `apps/space/components/issues/peek-overview/issue-details.tsx`, `apps/space/components/issues/peek-overview/issue-properties.tsx`, `packages/services/src/file/helper.ts`, `packages/services/src/file/sites-file.service.ts`, `packages/services/src/file/file-upload.service.ts`, `packages/constants/src/file.ts`, `packages/utils/src/editor/common.ts`, `apps/space/components/editor/embeds/mentions/user.tsx`, `apps/space/hooks/use-parse-editor-content.ts`

**Endpunkte (Katalog 04, `architecture/_data/endpoints.json`; 7 registriert)**

| EP | Methode | Pfad | Oberfläche | Handler | Permission | Inkr. 04 | CE-IDs |
|---|---|---|---|---|---|---|---|
| EP-0459 | POST | `/api/public/assets/v2/anchor/{anchor}/` | Space | PublicAssetEndpoints.CreatePublicAssetUploadCommand | public.asset.create | I6 | CE-SPACE-007 |
| EP-0460 | POST | `/api/public/assets/v2/anchor/{anchor}/restore/{pk}/` | Space | PublicAssetEndpoints.RestorePublicAssetCommand | public.asset.create | I6 | CE-SPACE-007 |
| EP-0461 | POST | `/api/public/assets/v2/anchor/{anchor}/{entity_id}/bulk/` | Space | PublicAssetEndpoints.BulkConfirmPublicAssetsCommand | public.asset.create | I6 | CE-SPACE-007 |
| EP-0462 | GET | `/api/public/assets/v2/anchor/{anchor}/{pk}/` | Space | PublicAssetEndpoints.GetPublicAssetRedirectQuery | public.asset.read | I6 | CE-SPACE-007 |
| EP-0463 | PATCH | `/api/public/assets/v2/anchor/{anchor}/{pk}/` | Space | PublicAssetEndpoints.ConfirmPublicAssetUploadCommand | public.asset.update | I6 | CE-SPACE-007 |
| EP-0464 | DELETE | `/api/public/assets/v2/anchor/{anchor}/{pk}/` | Space | PublicAssetEndpoints.DeletePublicAssetCommand | public.asset.delete | I6 | CE-SPACE-007 |
| EP-0517 | GET | `/api/public/anchor/{anchor}/issues/{issue_id}/` | Space | PublicBoardEndpoints.GetBoardWorkItemQuery | public.board.read | I6 | CE-SPACE-004, CE-SPACE-024 |

**Akzeptanzkriterien**

1. Contract: je Endpunkt dieses Pakets ≥ 1 Szenario mit Golden vom Original (Erfolg, Berechtigungsfehler, Validierungsfehler); Replay grün (L5).
2. Permission-Matrix (05 Anhang B) für alle Endpunkte dieses Pakets als L3-Test grün; Tenant-Isolation geprüft.
3. Signal-Stores strukturgleich zum MobX-Original (`store-parity-check`), Vitest je Action (L2).
4. E2E-Specs dieses Pakets grün gegen Original **und** funk. (Dual-Target, Pflichtszenarien 15 §3.9.3).
5. Visual-/DOM-/a11y-Prüfpunkte der betroffenen Screens (09 §4.14, 15 §3.10.2) innerhalb der Schwellwerte 15 §3.10.3 (Chromium); i18n-Schlüssel nur aus den Original-Locales (de/en).
6. `ce-coverage-check --ids CE-SPACE-004,CE-SPACE-007,CE-SPACE-024,CE-SPACE-030` grün (Mindestebenen 15 Anhang B).

**Testumfang**

- Pflicht-Ebenen (aus 15 Anhang B): L1, L2, L3, L5, L7, L8
- Testprojekte: `Funk.PublicSpace.Tests`
- E2E-Specs (`frontend/apps/e2e/`): `space/board.spec.ts`

### WP-I6-008 – Space-Interaktionen: Kommentare, Reaktionen, Votes, öffentliche Intake-Einreichung

| Merkmal | Wert |
|---|---|
| Inkrement | I6 |
| Typ (DoD 15 §3.15.3) | V – Vertikaler Schnitt |
| Größe | M |
| parallelisierbar | ja |
| Abhängigkeiten | WP-I6-007 |
| CE-IDs | CE-SPACE-006, CE-SPACE-025, CE-SPACE-026, CE-SPACE-027, CE-SPACE-028 |

**Ziel.** Öffentliche Kommentare (Lite-Editor mit Bild-Upload), Kommentar- und Work-Item-Reaktionen, Up-/Downvotes (Keycloak-Anmeldung erforderlich) und die öffentliche Intake-Einreichung (nur API).

**Enthaltene CE-IDs**

| CE-ID | Feature | Status (15 Anh. B) | Inkrement laut 15 | Pflicht-Ebenen | Testprojekt | E2E-Spec |
|---|---|---|---|---|---|---|
| CE-SPACE-006 | Öffentliche Intake-Einreichung (nur API) | übernommen | I6 | L1 L2 L3 L5 L7 L8 | Funk.Intake.Tests | `space/board.spec.ts` |
| CE-SPACE-025 | Öffentliche Kommentare | übernommen | I6 | L1 L2 L3 L5 L7 L8 | Funk.PublicSpace.Tests | `space/interactions.spec.ts` |
| CE-SPACE-026 | Kommentar-Reaktionen | übernommen | I6 | L1 L2 L3 L5 L7 L8 | Funk.PublicSpace.Tests | `space/interactions.spec.ts` |
| CE-SPACE-027 | Emoji-Reaktionen auf Work Items | übernommen | I6 | L1 L2 L3 L5 L7 L8 | Funk.PublicSpace.Tests | `space/interactions.spec.ts` |
| CE-SPACE-028 | Up- und Downvotes | übernommen | I6 | L1 L2 L3 L5 L7 L8 | Funk.PublicSpace.Tests | `space/interactions.spec.ts` |

**Betroffene Module/Libs in `funk.`**

- Backend: `src/modules/PublicSpace/Funk.PublicSpace`
- Backend: `src/modules/Intake/Funk.Intake` (öffentliche Einreichung)
- Frontend: `frontend/libs/space/issues`

**Referenzdokumente**

- Architektur: 04 §4.9, §4.18
- Architektur: 00 ADR-008 (Space)
- Analyse/Feature: `analysis/05-api-public-v1-space-instanz.md` §3.19, §3.18
- Analyse/Feature: `analysis/11-frontend-admin-space.md` §3.27, §3.28
- Analyse/Feature: `analysis/13b-shared-packages-i18n.md` §2.7
- Analyse/Feature: `analysis/02b-datenmodell-arbeitsobjekte.md` §2.7
- Feature-Katalog: `features/10-ce-feature-katalog.md` (Einträge CE-SPACE-006, CE-SPACE-025, CE-SPACE-026, CE-SPACE-027, CE-SPACE-028)

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- Backend: `apps/api/plane/space/views/intake.py`, `apps/api/plane/space/urls/intake.py`, `apps/api/plane/space/views/issue.py`, `apps/api/plane/space/urls/issue.py`, `apps/api/plane/db/models/issue.py:654-674`
- Frontend: `apps/space/components/issues/peek-overview/issue-activity.tsx`, `apps/space/components/issues/peek-overview/comment/add-comment.tsx`, `apps/space/components/issues/peek-overview/comment/comment-detail-card.tsx`, `apps/space/components/editor/lite-text-editor.tsx`, `apps/space/components/editor/toolbar.tsx`, `apps/space/helpers/editor.helper.ts`, `packages/services/src/issue/sites-issue.service.ts`, `packages/services/src/project/sites-publish.service.ts`, `packages/services/src/label/sites-label.service.ts`, `packages/services/src/state/sites-state.service.ts`, `packages/services/src/user/sites-member.service.ts`, `packages/services/src/module/sites-module.service.ts`, `packages/services/src/cycle/sites-cycle.service.ts`, `apps/space/components/issues/peek-overview/comment/comment-reactions.tsx`, `apps/space/components/issues/reactions/issue-emoji-reactions.tsx`, `apps/space/components/issues/peek-overview/issue-reaction.tsx`, `apps/space/components/issues/reactions/issue-vote-reactions.tsx`

**Endpunkte (Katalog 04, `architecture/_data/endpoints.json`; 21 registriert)**

| EP | Methode | Pfad | Oberfläche | Handler | Permission | Inkr. 04 | CE-IDs |
|---|---|---|---|---|---|---|---|
| EP-0387 | GET | `/api/public/anchor/{anchor}/intakes/{intake_id}/inbox-issues/` | Space | PublicIntakeEndpoints.ListPublicIntakeWorkItemsQuery | public.intake.read | I6 | CE-SPACE-006 |
| EP-0388 | POST | `/api/public/anchor/{anchor}/intakes/{intake_id}/inbox-issues/` | Space | PublicIntakeEndpoints.CreatePublicIntakeWorkItemCommand | public.intake.create | I6 | CE-SPACE-006 |
| EP-0389 | GET | `/api/public/anchor/{anchor}/intakes/{intake_id}/intake-issues/` | Space | PublicIntakeEndpoints.ListPublicIntakeWorkItemsQuery | public.intake.read | I6 | CE-SPACE-006 |
| EP-0390 | POST | `/api/public/anchor/{anchor}/intakes/{intake_id}/intake-issues/` | Space | PublicIntakeEndpoints.CreatePublicIntakeWorkItemCommand | public.intake.create | I6 | CE-SPACE-006 |
| EP-0391 | GET | `/api/public/anchor/{anchor}/intakes/{intake_id}/intake-issues/{pk}/` | Space | PublicIntakeEndpoints.GetPublicIntakeWorkItemQuery | public.intake.read | I6 | CE-SPACE-006 |
| EP-0392 | PATCH | `/api/public/anchor/{anchor}/intakes/{intake_id}/intake-issues/{pk}/` | Space | PublicIntakeEndpoints.UpdatePublicIntakeWorkItemCommand | public.intake.update | I6 | CE-SPACE-006 |
| EP-0393 | DELETE | `/api/public/anchor/{anchor}/intakes/{intake_id}/intake-issues/{pk}/` | Space | PublicIntakeEndpoints.DeletePublicIntakeWorkItemCommand | public.intake.delete | I6 | CE-SPACE-006 |
| EP-0525 | GET | `/api/public/anchor/{anchor}/issues/{issue_id}/comments/` | Space | PublicCommentEndpoints.ListPublicCommentsQuery | public.comment.read | I6 | CE-SPACE-025 |
| EP-0526 | POST | `/api/public/anchor/{anchor}/issues/{issue_id}/comments/` | Space | PublicCommentEndpoints.CreatePublicCommentCommand | public.comment.create | I6 | CE-SPACE-025 |
| EP-0527 | GET | `/api/public/anchor/{anchor}/issues/{issue_id}/comments/{pk}/` | Space | PublicCommentEndpoints.GetPublicCommentQuery | public.comment.read | I6 | CE-SPACE-025 |
| EP-0528 | PATCH | `/api/public/anchor/{anchor}/issues/{issue_id}/comments/{pk}/` | Space | PublicCommentEndpoints.UpdatePublicCommentCommand | public.comment.update | I6 | CE-SPACE-025 |
| EP-0529 | DELETE | `/api/public/anchor/{anchor}/issues/{issue_id}/comments/{pk}/` | Space | PublicCommentEndpoints.DeletePublicCommentCommand | public.comment.delete | I6 | CE-SPACE-025 |
| EP-0530 | GET | `/api/public/anchor/{anchor}/comments/{comment_id}/reactions/` | Space | PublicReactionEndpoints.ListPublicCommentReactionsQuery | public.reaction.read | I6 | CE-SPACE-026 |
| EP-0531 | POST | `/api/public/anchor/{anchor}/comments/{comment_id}/reactions/` | Space | PublicReactionEndpoints.AddPublicCommentReactionCommand | public.reaction.create | I6 | CE-SPACE-026 |
| EP-0532 | DELETE | `/api/public/anchor/{anchor}/comments/{comment_id}/reactions/{reaction_code}/` | Space | PublicReactionEndpoints.RemovePublicCommentReactionCommand | public.reaction.delete | I6 | CE-SPACE-026 |
| EP-0533 | GET | `/api/public/anchor/{anchor}/issues/{issue_id}/reactions/` | Space | PublicReactionEndpoints.ListPublicWorkItemReactionsQuery | public.reaction.read | I6 | CE-SPACE-027 |
| EP-0534 | POST | `/api/public/anchor/{anchor}/issues/{issue_id}/reactions/` | Space | PublicReactionEndpoints.AddPublicWorkItemReactionCommand | public.reaction.create | I6 | CE-SPACE-027 |
| EP-0535 | DELETE | `/api/public/anchor/{anchor}/issues/{issue_id}/reactions/{reaction_code}/` | Space | PublicReactionEndpoints.RemovePublicWorkItemReactionCommand | public.reaction.delete | I6 | CE-SPACE-027 |
| EP-0536 | GET | `/api/public/anchor/{anchor}/issues/{issue_id}/votes/` | Space | PublicVoteEndpoints.ListVotesQuery | public.vote.read | I6 | CE-SPACE-028 |
| EP-0537 | POST | `/api/public/anchor/{anchor}/issues/{issue_id}/votes/` | Space | PublicVoteEndpoints.CastVoteCommand | public.vote.create | I6 | CE-SPACE-028 |
| EP-0538 | DELETE | `/api/public/anchor/{anchor}/issues/{issue_id}/votes/` | Space | PublicVoteEndpoints.RemoveVoteCommand | public.vote.delete | I6 | CE-SPACE-028 |

**Akzeptanzkriterien**

1. Contract: je Endpunkt dieses Pakets ≥ 1 Szenario mit Golden vom Original (Erfolg, Berechtigungsfehler, Validierungsfehler); Replay grün (L5).
2. Permission-Matrix (05 Anhang B) für alle Endpunkte dieses Pakets als L3-Test grün; Tenant-Isolation geprüft.
3. Signal-Stores strukturgleich zum MobX-Original (`store-parity-check`), Vitest je Action (L2).
4. E2E-Specs dieses Pakets grün gegen Original **und** funk. (Dual-Target, Pflichtszenarien 15 §3.9.3).
5. Visual-/DOM-/a11y-Prüfpunkte der betroffenen Screens (09 §4.14, 15 §3.10.2) innerhalb der Schwellwerte 15 §3.10.3 (Chromium); i18n-Schlüssel nur aus den Original-Locales (de/en).
6. `ce-coverage-check --ids CE-SPACE-006,CE-SPACE-025,CE-SPACE-026,CE-SPACE-027,CE-SPACE-028` grün (Mindestebenen 15 Anhang B).

**Testumfang**

- Pflicht-Ebenen (aus 15 Anhang B): L1, L2, L3, L5, L7, L8
- Testprojekte: `Funk.Intake.Tests`, `Funk.PublicSpace.Tests`
- E2E-Specs (`frontend/apps/e2e/`): `space/board.spec.ts`, `space/interactions.spec.ts`

### WP-I6-009 – Public API v1: API-Key-Authentifizierung, Rate-Limit je Key, Aktivitätsprotokoll, OpenAPI, aktueller Benutzer

| Merkmal | Wert |
|---|---|
| Inkrement | I6 |
| Typ (DoD 15 §3.15.3) | B – Backend-only |
| Größe | M |
| parallelisierbar | nein |
| Abhängigkeiten | WP-I6-016, WP-I6-201 |
| CE-IDs | CE-API-001, CE-API-002, CE-API-003, CE-API-004, CE-API-005 |

**Ziel.** Oberfläche `/api/v1/` mit `X-Api-Key`, Rate-Limit je Key, API-Activity-Log (Queue), OpenAPI (Scalar offline, Default aus, im God Mode einschaltbar, Z-112) und `GET …/users/me/`.

**Enthaltene CE-IDs**

| CE-ID | Feature | Status (15 Anh. B) | Inkrement laut 15 | Pflicht-Ebenen | Testprojekt | E2E-Spec |
|---|---|---|---|---|---|---|
| CE-API-001 | API-Key-Authentifizierung | übernommen | I6 | L1 L3 L5 | Funk.PublicApi.Tests | – |
| CE-API-002 | Rate-Limiting je API-Key | übernommen | I6 | L1 L3 L5 L9 (LT-10) | Funk.PublicApi.Tests | – |
| CE-API-003 | API-Aktivitätsprotokoll | übernommen | I6 | L1 L3 L5 | Funk.PublicApi.Tests | – |
| CE-API-004 | OpenAPI-Dokumentation | übernommen | I6 | L1 L3 L5 L6 | Funk.PublicApi.Tests | – |
| CE-API-005 | Aktueller Benutzer | übernommen | I6 | L1 L3 L5 | Funk.PublicApi.Tests | – |

**Betroffene Module/Libs in `funk.`**

- Backend: `src/modules/PublicApi/Funk.PublicApi`
- Backend: `tests/modules/Funk.PublicApi.Tests`

**Referenzdokumente**

- Architektur: 04 §3.11, §3.14, §4.19
- Architektur: 05 §3.12
- Architektur: 06 O-D06-08
- Analyse/Feature: `analysis/05-api-public-v1-space-instanz.md` §2.1, §3.1, §2.8, §2.2
- Analyse/Feature: `analysis/06-auth-sicherheit-querschnitt.md` §2.9
- Analyse/Feature: `analysis/01-gesamtarchitektur-infrastruktur.md` §2.13, §2.20
- Analyse/Feature: `analysis/02a-datenmodell-kern.md` §3.11
- Analyse/Feature: `analysis/07-hintergrundjobs-mail-storage-webhooks.md` §3.17
- Feature-Katalog: `features/10-ce-feature-katalog.md` (Einträge CE-API-001, CE-API-002, CE-API-003, CE-API-004, CE-API-005)

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- Backend: `apps/api/plane/api/middleware/api_authentication.py`, `apps/api/plane/api/views/base.py`, `apps/api/plane/db/models/api.py`, `apps/api/plane/api/rate_limit.py`, `apps/api/plane/authentication/adapter/exception.py`, `apps/api/plane/settings/common.py`, `apps/api/plane/middleware/logger.py`, `apps/api/plane/bgtasks/logger_task.py`, `apps/api/plane/bgtasks/cleanup_task.py`, `apps/api/plane/settings/openapi.py`, `apps/api/plane/urls.py`, `apps/api/plane/utils/openapi/hooks.py`, `apps/api/plane/utils/openapi/auth.py`, `apps/api/plane/utils/openapi/decorators.py`, `apps/api/plane/utils/openapi/parameters.py`, `apps/api/plane/api/apps.py`, `apps/api/plane/api/views/user.py`, `apps/api/plane/api/urls/user.py`, `apps/api/plane/api/serializers/user.py`

**Endpunkte (Katalog 04, `architecture/_data/endpoints.json`; 4 registriert)**

| EP | Methode | Pfad | Oberfläche | Handler | Permission | Inkr. 04 | CE-IDs |
|---|---|---|---|---|---|---|---|
| EP-0540 | GET | `/api/v1/users/me/` | V1 | V1CurrentUserEndpoints.GetCurrentUserQuery | user.user.read | I6 | CE-API-005 |
| EP-0711 | GET | `/api/schema/` | OpenApi | OpenApiEndpoints.OpenApiDocumentEndpoint(v1) | (anonym, nur mit Plane:OpenApi:Enabled) | I6 | CE-API-004 |
| EP-0712 | GET | `/api/schema/redoc/` | OpenApi | OpenApiEndpoints.ScalarUi | (anonym, nur mit Plane:OpenApi:Enabled) | I6 | CE-API-004 |
| EP-0713 | GET | `/api/schema/swagger-ui/` | OpenApi | OpenApiEndpoints.ScalarUi | (anonym, nur mit Plane:OpenApi:Enabled) | I6 | CE-API-004 |

**Akzeptanzkriterien**

1. `OpenApiDocumentTests` gegen `v1.original.json`; LT-10 im Zielbereich.
2. Contract-Szenarien mit Original-Golden für alle HTTP-Endpunkte dieses Pakets; Replay grün.
3. Job-/Consumer-Tests: Idempotenz (Inbox), Retry/Backoff, Zeitsteuerung mit `FixedClock`; neue Ereignistypen im Event-Katalog-Snapshot.
4. Bei Cron-Jobs: Registrierung in `CronRegistrationTests` mit Original-Zeit (UTC).
5. `ce-coverage-check --ids CE-API-001,CE-API-002,CE-API-003,CE-API-004,CE-API-005` grün (Mindestebenen 15 Anhang B).

**Testumfang**

- Pflicht-Ebenen (aus 15 Anhang B): L1, L3, L5, L6, L9
- Testprojekte: `Funk.PublicApi.Tests`

### WP-I6-010 – Public API v1: Projekte, Archiv, Summary, States, Labels, Mitglieder, Einladungen

| Merkmal | Wert |
|---|---|
| Inkrement | I6 |
| Typ (DoD 15 §3.15.3) | B – Backend-only |
| Größe | L |
| parallelisierbar | ja |
| Abhängigkeiten | WP-I6-009 |
| CE-IDs | CE-API-006, CE-API-007, CE-API-008, CE-API-009, CE-API-010, CE-API-011, CE-API-012, CE-API-013 |

**Ziel.** v1-Adapter auf die Contracts-Commands der Fachmodule (R6), inkl. HARM-03/-04/-06.

**Enthaltene CE-IDs**

| CE-ID | Feature | Status (15 Anh. B) | Inkrement laut 15 | Pflicht-Ebenen | Testprojekt | E2E-Spec |
|---|---|---|---|---|---|---|
| CE-API-006 | Projekte verwalten | übernommen | I6 | L1 L3 L5 | Funk.PublicApi.Tests | – |
| CE-API-007 | Projekt archivieren/dearchivieren | übernommen | I6 | L1 L3 L5 | Funk.PublicApi.Tests | – |
| CE-API-008 | Projekt-Summary | übernommen | I6 | L1 L3 L5 | Funk.PublicApi.Tests | – |
| CE-API-009 | States verwalten | übernommen | I6 | L1 L3 L5 | Funk.PublicApi.Tests | – |
| CE-API-010 | Labels verwalten | übernommen | I6 | L1 L3 L5 | Funk.PublicApi.Tests | – |
| CE-API-011 | Workspace-Mitglieder lesen | übernommen | I6 | L1 L3 L5 | Funk.PublicApi.Tests | – |
| CE-API-012 | Projekt-Mitglieder verwalten | übernommen | I6 | L1 L3 L5 | Funk.PublicApi.Tests | – |
| CE-API-013 | Workspace-Einladungen | übernommen | I6 | L1 L3 L5 | Funk.PublicApi.Tests | – |

**Betroffene Module/Libs in `funk.`**

- Backend: `src/modules/PublicApi/Funk.PublicApi`

**Referenzdokumente**

- Architektur: 04 §4.19, §5.3
- Architektur: 05 §3.18.1
- Analyse/Feature: `analysis/05-api-public-v1-space-instanz.md` §3.2, §2.2, §3.13
- Feature-Katalog: `features/10-ce-feature-katalog.md` (Einträge CE-API-006, CE-API-007, CE-API-008, CE-API-009, CE-API-010, CE-API-011, CE-API-012, CE-API-013)

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- Backend: `apps/api/plane/api/views/project.py`, `apps/api/plane/api/urls/project.py`, `apps/api/plane/api/serializers/project.py`, `apps/api/plane/api/views/state.py`, `apps/api/plane/api/urls/state.py`, `apps/api/plane/api/serializers/state.py`, `apps/api/plane/api/views/issue.py`, `apps/api/plane/api/urls/label.py`, `apps/api/plane/api/serializers/issue.py`, `apps/api/plane/api/views/member.py`, `apps/api/plane/api/urls/member.py`, `apps/api/plane/api/serializers/member.py`, `apps/api/plane/api/views/invite.py`, `apps/api/plane/api/urls/invite.py`, `apps/api/plane/api/serializers/invite.py`

**Endpunkte (Katalog 04, `architecture/_data/endpoints.json`; 37 registriert)**

| EP | Methode | Pfad | Oberfläche | Handler | Permission | Inkr. 04 | CE-IDs |
|---|---|---|---|---|---|---|---|
| EP-0563 | GET | `/api/v1/workspaces/{slug}/invitations/` | V1 | V1InvitationEndpoints.ListWorkspaceInvitationsQuery | workspace.invitation.read | I6 | CE-API-013 |
| EP-0564 | POST | `/api/v1/workspaces/{slug}/invitations/` | V1 | V1InvitationEndpoints.CreateWorkspaceInvitationsCommand | workspace.invitation.create | I6 | CE-API-013 |
| EP-0565 | GET | `/api/v1/workspaces/{slug}/invitations/{pk}/` | V1 | V1InvitationEndpoints.GetWorkspaceInvitationQuery | workspace.invitation.read | I6 | CE-API-013 |
| EP-0566 | PATCH | `/api/v1/workspaces/{slug}/invitations/{pk}/` | V1 | V1InvitationEndpoints.UpdateWorkspaceInvitationCommand | workspace.invitation.update | I6 | CE-API-013 |
| EP-0567 | DELETE | `/api/v1/workspaces/{slug}/invitations/{pk}/` | V1 | V1InvitationEndpoints.DeleteWorkspaceInvitationCommand | workspace.invitation.delete | I6 | CE-API-013 |
| EP-0568 | GET | `/api/v1/workspaces/{slug}/projects/{project_id}/labels/` | V1 | V1LabelEndpoints.ListLabelsQuery | project.label.read | I6 | CE-API-010 |
| EP-0569 | POST | `/api/v1/workspaces/{slug}/projects/{project_id}/labels/` | V1 | V1LabelEndpoints.CreateLabelCommand | project.label.create | I6 | CE-API-010 |
| EP-0570 | GET | `/api/v1/workspaces/{slug}/projects/{project_id}/labels/{pk}/` | V1 | V1LabelEndpoints.GetLabelQuery | project.label.read | I6 | CE-API-010 |
| EP-0571 | PATCH | `/api/v1/workspaces/{slug}/projects/{project_id}/labels/{pk}/` | V1 | V1LabelEndpoints.UpdateLabelCommand | project.label.update | I6 | CE-API-010 |
| EP-0572 | DELETE | `/api/v1/workspaces/{slug}/projects/{project_id}/labels/{pk}/` | V1 | V1LabelEndpoints.DeleteLabelCommand | project.label.delete | I6 | CE-API-010 |
| EP-0573 | GET | `/api/v1/workspaces/{slug}/members-lite/` | V1 | V1MemberEndpoints.ListWorkspaceMembersLiteQuery | workspace.member.read | I6 | CE-API-011 |
| EP-0574 | GET | `/api/v1/workspaces/{slug}/members/` | V1 | V1MemberEndpoints.ListWorkspaceMembersQuery | workspace.member.read | I6 | CE-API-011 |
| EP-0575 | GET | `/api/v1/workspaces/{slug}/projects/{project_id}/members/` | V1 | V1MemberEndpoints.ListProjectMembersQuery | project.member.read | I6 | CE-API-012 |
| EP-0576 | POST | `/api/v1/workspaces/{slug}/projects/{project_id}/members/` | V1 | V1MemberEndpoints.CreateProjectMemberCommand | project.member.create | I6 | CE-API-012 |
| EP-0577 | GET | `/api/v1/workspaces/{slug}/projects/{project_id}/members/{pk}/` | V1 | V1MemberEndpoints.GetProjectMemberQuery | project.member.read | I6 | CE-API-012 |
| EP-0578 | PATCH | `/api/v1/workspaces/{slug}/projects/{project_id}/members/{pk}/` | V1 | V1MemberEndpoints.UpdateProjectMemberCommand | project.member.update | I6 | CE-API-012 |
| EP-0579 | DELETE | `/api/v1/workspaces/{slug}/projects/{project_id}/members/{pk}/` | V1 | V1MemberEndpoints.DeleteProjectMemberCommand | project.member.delete | I6 | CE-API-012 |
| EP-0580 | GET | `/api/v1/workspaces/{slug}/projects/{project_id}/project-members-lite/` | V1 | V1MemberEndpoints.ListProjectMembersLiteQuery | project.member.read | I6 | CE-API-012 |
| EP-0581 | GET | `/api/v1/workspaces/{slug}/projects/{project_id}/project-members/` | V1 | V1MemberEndpoints.ListProjectMembersQuery | project.member.read | I6 | CE-API-012 |
| EP-0582 | POST | `/api/v1/workspaces/{slug}/projects/{project_id}/project-members/` | V1 | V1MemberEndpoints.CreateProjectMemberCommand | project.member.create | I6 | CE-API-012 |
| EP-0583 | GET | `/api/v1/workspaces/{slug}/projects/{project_id}/project-members/{pk}/` | V1 | V1MemberEndpoints.GetProjectMemberQuery | project.member.read | I6 | CE-API-012 |
| EP-0584 | PATCH | `/api/v1/workspaces/{slug}/projects/{project_id}/project-members/{pk}/` | V1 | V1MemberEndpoints.UpdateProjectMemberCommand | project.member.update | I6 | CE-API-012 |
| EP-0585 | DELETE | `/api/v1/workspaces/{slug}/projects/{project_id}/project-members/{pk}/` | V1 | V1MemberEndpoints.DeleteProjectMemberCommand | project.member.delete | I6 | CE-API-012 |
| EP-0598 | GET | `/api/v1/workspaces/{slug}/projects-lite/` | V1 | V1ProjectEndpoints.ListProjectsLiteQuery | workspace.project.read | I6 | CE-API-006 |
| EP-0599 | GET | `/api/v1/workspaces/{slug}/projects/` | V1 | V1ProjectEndpoints.ListProjectsQuery | workspace.project.read | I6 | CE-API-006 |
| EP-0600 | POST | `/api/v1/workspaces/{slug}/projects/` | V1 | V1ProjectEndpoints.CreateProjectCommand | workspace.project.create | I6 | CE-API-006 |
| EP-0601 | GET | `/api/v1/workspaces/{slug}/projects/{pk}/` | V1 | V1ProjectEndpoints.GetProjectQuery | project.project.read | I6 | CE-API-006 |
| EP-0602 | PATCH | `/api/v1/workspaces/{slug}/projects/{pk}/` | V1 | V1ProjectEndpoints.UpdateProjectCommand | project.project.update | I6 | CE-API-006 |
| EP-0603 | DELETE | `/api/v1/workspaces/{slug}/projects/{pk}/` | V1 | V1ProjectEndpoints.DeleteProjectCommand | project.project.delete | I6 | CE-API-006 |
| EP-0604 | POST | `/api/v1/workspaces/{slug}/projects/{project_id}/archive/` | V1 | V1ProjectEndpoints.ArchiveProjectCommand | project.project.archive | I6 | CE-API-007 |
| EP-0605 | DELETE | `/api/v1/workspaces/{slug}/projects/{project_id}/archive/` | V1 | V1ProjectEndpoints.UnarchiveProjectCommand | project.project.unarchive | I6 | CE-API-007 |
| EP-0606 | GET | `/api/v1/workspaces/{slug}/projects/{project_id}/summary/` | V1 | V1ProjectEndpoints.GetProjectSummaryQuery | project.project.read_summary | I6 | CE-API-008 |
| EP-0607 | GET | `/api/v1/workspaces/{slug}/projects/{project_id}/states/` | V1 | V1StateEndpoints.ListStatesQuery | project.state.read | I6 | CE-API-009 |
| EP-0608 | POST | `/api/v1/workspaces/{slug}/projects/{project_id}/states/` | V1 | V1StateEndpoints.CreateStateCommand | project.state.create | I6 | CE-API-009 |
| EP-0609 | GET | `/api/v1/workspaces/{slug}/projects/{project_id}/states/{state_id}/` | V1 | V1StateEndpoints.GetStateQuery | project.state.read | I6 | CE-API-009 |
| EP-0610 | PATCH | `/api/v1/workspaces/{slug}/projects/{project_id}/states/{state_id}/` | V1 | V1StateEndpoints.UpdateStateCommand | project.state.update | I6 | CE-API-009 |
| EP-0611 | DELETE | `/api/v1/workspaces/{slug}/projects/{project_id}/states/{state_id}/` | V1 | V1StateEndpoints.DeleteStateCommand | project.state.delete | I6 | CE-API-009 |

**Akzeptanzkriterien**

1. Contract-Szenarien mit Original-Golden für alle HTTP-Endpunkte dieses Pakets; Replay grün.
2. Job-/Consumer-Tests: Idempotenz (Inbox), Retry/Backoff, Zeitsteuerung mit `FixedClock`; neue Ereignistypen im Event-Katalog-Snapshot.
3. Bei Cron-Jobs: Registrierung in `CronRegistrationTests` mit Original-Zeit (UTC).
4. `ce-coverage-check --ids CE-API-006,CE-API-007,CE-API-008,CE-API-009,CE-API-010,CE-API-011,CE-API-012,CE-API-013` grün (Mindestebenen 15 Anhang B).

**Testumfang**

- Pflicht-Ebenen (aus 15 Anhang B): L1, L3, L5
- Testprojekte: `Funk.PublicApi.Tests`

### WP-I6-011 – Public API v1: Stickies, User-Assets, Generic Workspace Assets

| Merkmal | Wert |
|---|---|
| Inkrement | I6 |
| Typ (DoD 15 §3.15.3) | B – Backend-only |
| Größe | S |
| parallelisierbar | ja |
| Abhängigkeiten | WP-I6-009 |
| CE-IDs | CE-API-014, CE-API-015, CE-API-016 |

**Ziel.** v1-Endpunkte für Stickies und Assets.

**Enthaltene CE-IDs**

| CE-ID | Feature | Status (15 Anh. B) | Inkrement laut 15 | Pflicht-Ebenen | Testprojekt | E2E-Spec |
|---|---|---|---|---|---|---|
| CE-API-014 | Stickies | übernommen | I6 | L1 L3 L5 | Funk.PublicApi.Tests | – |
| CE-API-015 | User-Assets (Avatar/Cover) | übernommen | I6 | L1 L3 L5 | Funk.PublicApi.Tests | – |
| CE-API-016 | Generic Workspace Assets | übernommen | I6 | L1 L3 L5 | Funk.PublicApi.Tests | – |

**Betroffene Module/Libs in `funk.`**

- Backend: `src/modules/PublicApi/Funk.PublicApi`

**Referenzdokumente**

- Architektur: 04 §4.19
- Analyse/Feature: `analysis/05-api-public-v1-space-instanz.md` §3.14, §3.15
- Feature-Katalog: `features/10-ce-feature-katalog.md` (Einträge CE-API-014, CE-API-015, CE-API-016)

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- Backend: `apps/api/plane/api/views/sticky.py`, `apps/api/plane/api/urls/sticky.py`, `apps/api/plane/api/serializers/sticky.py`, `apps/api/plane/api/views/asset.py`, `apps/api/plane/api/urls/asset.py`, `apps/api/plane/settings/storage.py`

**Endpunkte (Katalog 04, `architecture/_data/endpoints.json`; 14 registriert)**

| EP | Methode | Pfad | Oberfläche | Handler | Permission | Inkr. 04 | CE-IDs |
|---|---|---|---|---|---|---|---|
| EP-0555 | POST | `/api/v1/workspaces/{slug}/assets/` | V1 | V1GenericAssetEndpoints.CreateGenericAssetUploadCommand | workspace.asset.create | I6 | CE-API-016 |
| EP-0556 | GET | `/api/v1/workspaces/{slug}/assets/{asset_id}/` | V1 | V1GenericAssetEndpoints.GetGenericAssetQuery | workspace.asset.read | I6 | CE-API-016 |
| EP-0557 | PATCH | `/api/v1/workspaces/{slug}/assets/{asset_id}/` | V1 | V1GenericAssetEndpoints.ConfirmGenericAssetUploadCommand | workspace.asset.update | I6 | CE-API-016 |
| EP-0612 | GET | `/api/v1/workspaces/{slug}/stickies/` | V1 | V1StickyEndpoints.ListStickiesQuery | workspace.sticky.read | I6 | CE-API-014 |
| EP-0613 | POST | `/api/v1/workspaces/{slug}/stickies/` | V1 | V1StickyEndpoints.CreateStickyCommand | workspace.sticky.create | I6 | CE-API-014 |
| EP-0614 | GET | `/api/v1/workspaces/{slug}/stickies/{pk}/` | V1 | V1StickyEndpoints.GetStickyQuery | workspace.sticky.read | I6 | CE-API-014 |
| EP-0615 | PATCH | `/api/v1/workspaces/{slug}/stickies/{pk}/` | V1 | V1StickyEndpoints.UpdateStickyCommand | workspace.sticky.update | I6 | CE-API-014 |
| EP-0616 | DELETE | `/api/v1/workspaces/{slug}/stickies/{pk}/` | V1 | V1StickyEndpoints.DeleteStickyCommand | workspace.sticky.delete | I6 | CE-API-014 |
| EP-0617 | POST | `/api/v1/assets/user-assets/` | V1 | V1UserAssetEndpoints.CreateUserAssetUploadCommand | user.user_asset.create | I6 | CE-API-015 |
| EP-0618 | POST | `/api/v1/assets/user-assets/server/` | V1 | V1UserAssetEndpoints.CreateUserServerAssetUploadCommand | user.user_asset.create | I6 | CE-API-015 |
| EP-0619 | PATCH | `/api/v1/assets/user-assets/{asset_id}/` | V1 | V1UserAssetEndpoints.ConfirmUserAssetUploadCommand | user.user_asset.update | I6 | CE-API-015 |
| EP-0620 | DELETE | `/api/v1/assets/user-assets/{asset_id}/` | V1 | V1UserAssetEndpoints.DeleteUserAssetCommand | user.user_asset.delete | I6 | CE-API-015 |
| EP-0621 | PATCH | `/api/v1/assets/user-assets/{asset_id}/server/` | V1 | V1UserAssetEndpoints.ConfirmUserServerAssetUploadCommand | user.user_asset.update | I6 | CE-API-015 |
| EP-0622 | DELETE | `/api/v1/assets/user-assets/{asset_id}/server/` | V1 | V1UserAssetEndpoints.DeleteUserServerAssetCommand | user.user_asset.delete | I6 | CE-API-015 |

**Akzeptanzkriterien**

1. Contract-Szenarien mit Original-Golden für alle HTTP-Endpunkte dieses Pakets; Replay grün.
2. Job-/Consumer-Tests: Idempotenz (Inbox), Retry/Backoff, Zeitsteuerung mit `FixedClock`; neue Ereignistypen im Event-Katalog-Snapshot.
3. Bei Cron-Jobs: Registrierung in `CronRegistrationTests` mit Original-Zeit (UTC).
4. `ce-coverage-check --ids CE-API-014,CE-API-015,CE-API-016` grün (Mindestebenen 15 Anhang B).

**Testumfang**

- Pflicht-Ebenen (aus 15 Anhang B): L1, L3, L5
- Testprojekte: `Funk.PublicApi.Tests`

### WP-I6-012 – Public API v1: Work Items, Identifier, Suche, Links, Kommentare, Aktivitäten, Anhänge, Relationen, Intake

| Merkmal | Wert |
|---|---|
| Inkrement | I6 |
| Typ (DoD 15 §3.15.3) | B – Backend-only |
| Größe | L |
| parallelisierbar | ja |
| Abhängigkeiten | WP-I6-010 |
| CE-IDs | CE-API-017, CE-API-018, CE-API-019, CE-API-020, CE-API-021, CE-API-022, CE-API-023, CE-API-024, CE-API-025 |

**Ziel.** v1-Work-Item-Endpunkte inkl. Alias-Routen `issues`/`work-items`, State-Wechsel mit Origin `PublicApi`.

**Enthaltene CE-IDs**

| CE-ID | Feature | Status (15 Anh. B) | Inkrement laut 15 | Pflicht-Ebenen | Testprojekt | E2E-Spec |
|---|---|---|---|---|---|---|
| CE-API-017 | Work Items verwalten | übernommen | I6 | L1 L3 L5 | Funk.PublicApi.Tests | – |
| CE-API-018 | Work Item per Identifier | übernommen | I6 | L1 L3 L5 | Funk.PublicApi.Tests | – |
| CE-API-019 | Work-Item-Suche | übernommen | I6 | L1 L3 L5 | Funk.PublicApi.Tests | – |
| CE-API-020 | Work-Item-Links | übernommen | I6 | L1 L3 L5 | Funk.PublicApi.Tests | – |
| CE-API-021 | Work-Item-Kommentare | übernommen | I6 | L1 L3 L5 | Funk.PublicApi.Tests | – |
| CE-API-022 | Work-Item-Aktivitäten | übernommen | I6 | L1 L3 L5 | Funk.PublicApi.Tests | – |
| CE-API-023 | Work-Item-Anhänge | übernommen | I6 | L1 L3 L5 | Funk.PublicApi.Tests | – |
| CE-API-024 | Work-Item-Relationen | übernommen | I6 | L1 L3 L5 | Funk.PublicApi.Tests | – |
| CE-API-025 | Intake über die API | übernommen | I6 | L1 L3 L5 | Funk.PublicApi.Tests | – |

**Betroffene Module/Libs in `funk.`**

- Backend: `src/modules/PublicApi/Funk.PublicApi`

**Referenzdokumente**

- Architektur: 04 §4.19, R-D04-07
- Architektur: 11 §3.7
- Architektur: 16 §5.9
- Analyse/Feature: `analysis/05-api-public-v1-space-instanz.md` §3.5, §2.2, §3.7, §3.8, §3.12
- Feature-Katalog: `features/10-ce-feature-katalog.md` (Einträge CE-API-017, CE-API-018, CE-API-019, CE-API-020, CE-API-021, CE-API-022, CE-API-023, CE-API-024, CE-API-025)

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- Backend: `apps/api/plane/api/views/issue.py`, `apps/api/plane/api/urls/work_item.py`, `apps/api/plane/api/serializers/issue.py`, `apps/api/plane/bgtasks/work_item_link_task.py`, `apps/api/plane/settings/storage.py`, `apps/api/plane/settings/common.py`, `apps/api/plane/utils/issue_relation_mapper.py`, `apps/api/plane/api/views/intake.py`, `apps/api/plane/api/urls/intake.py`, `apps/api/plane/api/serializers/intake.py`

**Endpunkte (Katalog 04, `architecture/_data/endpoints.json`; 55 registriert)**

| EP | Methode | Pfad | Oberfläche | Handler | Permission | Inkr. 04 | CE-IDs |
|---|---|---|---|---|---|---|---|
| EP-0558 | GET | `/api/v1/workspaces/{slug}/projects/{project_id}/intake-issues/` | V1 | V1IntakeWorkItemEndpoints.ListIntakeWorkItemsQuery | project.intake_work_item.read | I6 | CE-API-025 |
| EP-0559 | POST | `/api/v1/workspaces/{slug}/projects/{project_id}/intake-issues/` | V1 | V1IntakeWorkItemEndpoints.CreateIntakeWorkItemCommand | project.intake_work_item.create | I6 | CE-API-025 |
| EP-0560 | GET | `/api/v1/workspaces/{slug}/projects/{project_id}/intake-issues/{issue_id}/` | V1 | V1IntakeWorkItemEndpoints.GetIntakeWorkItemQuery | project.intake_work_item.read | I6 | CE-API-025 |
| EP-0561 | PATCH | `/api/v1/workspaces/{slug}/projects/{project_id}/intake-issues/{issue_id}/` | V1 | V1IntakeWorkItemEndpoints.UpdateIntakeWorkItemCommand | project.intake_work_item.update | I6 | CE-API-025 |
| EP-0562 | DELETE | `/api/v1/workspaces/{slug}/projects/{project_id}/intake-issues/{issue_id}/` | V1 | V1IntakeWorkItemEndpoints.DeleteIntakeWorkItemCommand | project.intake_work_item.delete | I6 | CE-API-025 |
| EP-0623 | GET | `/api/v1/workspaces/{slug}/projects/{project_id}/issues/{issue_id}/activities/` | V1 | V1WorkItemActivityEndpoints.ListWorkItemActivitiesQuery | project.work_item_activity.read | I6 | CE-API-022 |
| EP-0624 | GET | `/api/v1/workspaces/{slug}/projects/{project_id}/issues/{issue_id}/activities/{pk}/` | V1 | V1WorkItemActivityEndpoints.GetWorkItemActivityQuery | project.work_item_activity.read | I6 | CE-API-022 |
| EP-0625 | GET | `/api/v1/workspaces/{slug}/projects/{project_id}/work-items/{issue_id}/activities/` | V1 | V1WorkItemActivityEndpoints.ListWorkItemActivitiesQuery | project.work_item_activity.read | I6 | CE-API-022 |
| EP-0626 | GET | `/api/v1/workspaces/{slug}/projects/{project_id}/work-items/{issue_id}/activities/{pk}/` | V1 | V1WorkItemActivityEndpoints.GetWorkItemActivityQuery | project.work_item_activity.read | I6 | CE-API-022 |
| EP-0627 | GET | `/api/v1/workspaces/{slug}/projects/{project_id}/issues/{issue_id}/issue-attachments/` | V1 | V1WorkItemAttachmentEndpoints.ListWorkItemAttachmentsQuery | project.work_item_attachment.read | I6 | CE-API-023 |
| EP-0628 | POST | `/api/v1/workspaces/{slug}/projects/{project_id}/issues/{issue_id}/issue-attachments/` | V1 | V1WorkItemAttachmentEndpoints.CreateWorkItemAttachmentUploadCommand | project.work_item_attachment.create | I6 | CE-API-023 |
| EP-0629 | GET | `/api/v1/workspaces/{slug}/projects/{project_id}/issues/{issue_id}/issue-attachments/{pk}/` | V1 | V1WorkItemAttachmentEndpoints.GetWorkItemAttachmentQuery | project.work_item_attachment.read | I6 | CE-API-023 |
| EP-0630 | PATCH | `/api/v1/workspaces/{slug}/projects/{project_id}/issues/{issue_id}/issue-attachments/{pk}/` | V1 | V1WorkItemAttachmentEndpoints.ConfirmWorkItemAttachmentUploadCommand | project.work_item_attachment.update | I6 | CE-API-023 |
| EP-0631 | DELETE | `/api/v1/workspaces/{slug}/projects/{project_id}/issues/{issue_id}/issue-attachments/{pk}/` | V1 | V1WorkItemAttachmentEndpoints.DeleteWorkItemAttachmentCommand | project.work_item_attachment.delete | I6 | CE-API-023 |
| EP-0632 | GET | `/api/v1/workspaces/{slug}/projects/{project_id}/work-items/{issue_id}/attachments/` | V1 | V1WorkItemAttachmentEndpoints.ListWorkItemAttachmentsQuery | project.work_item_attachment.read | I6 | CE-API-023 |
| EP-0633 | POST | `/api/v1/workspaces/{slug}/projects/{project_id}/work-items/{issue_id}/attachments/` | V1 | V1WorkItemAttachmentEndpoints.CreateWorkItemAttachmentUploadCommand | project.work_item_attachment.create | I6 | CE-API-023 |
| EP-0634 | GET | `/api/v1/workspaces/{slug}/projects/{project_id}/work-items/{issue_id}/attachments/{pk}/` | V1 | V1WorkItemAttachmentEndpoints.GetWorkItemAttachmentQuery | project.work_item_attachment.read | I6 | CE-API-023 |
| EP-0635 | PATCH | `/api/v1/workspaces/{slug}/projects/{project_id}/work-items/{issue_id}/attachments/{pk}/` | V1 | V1WorkItemAttachmentEndpoints.ConfirmWorkItemAttachmentUploadCommand | project.work_item_attachment.update | I6 | CE-API-023 |
| EP-0636 | DELETE | `/api/v1/workspaces/{slug}/projects/{project_id}/work-items/{issue_id}/attachments/{pk}/` | V1 | V1WorkItemAttachmentEndpoints.DeleteWorkItemAttachmentCommand | project.work_item_attachment.delete | I6 | CE-API-023 |
| EP-0637 | GET | `/api/v1/workspaces/{slug}/projects/{project_id}/issues/{issue_id}/comments/` | V1 | V1WorkItemCommentEndpoints.ListWorkItemCommentsQuery | project.work_item_comment.read | I6 | CE-API-021 |
| EP-0638 | POST | `/api/v1/workspaces/{slug}/projects/{project_id}/issues/{issue_id}/comments/` | V1 | V1WorkItemCommentEndpoints.CreateWorkItemCommentCommand | project.work_item_comment.create | I6 | CE-API-021 |
| EP-0639 | GET | `/api/v1/workspaces/{slug}/projects/{project_id}/issues/{issue_id}/comments/{pk}/` | V1 | V1WorkItemCommentEndpoints.GetWorkItemCommentQuery | project.work_item_comment.read | I6 | CE-API-021 |
| EP-0640 | PATCH | `/api/v1/workspaces/{slug}/projects/{project_id}/issues/{issue_id}/comments/{pk}/` | V1 | V1WorkItemCommentEndpoints.UpdateWorkItemCommentCommand | project.work_item_comment.update | I6 | CE-API-021 |
| EP-0641 | DELETE | `/api/v1/workspaces/{slug}/projects/{project_id}/issues/{issue_id}/comments/{pk}/` | V1 | V1WorkItemCommentEndpoints.DeleteWorkItemCommentCommand | project.work_item_comment.delete | I6 | CE-API-021 |
| EP-0642 | GET | `/api/v1/workspaces/{slug}/projects/{project_id}/work-items/{issue_id}/comments/` | V1 | V1WorkItemCommentEndpoints.ListWorkItemCommentsQuery | project.work_item_comment.read | I6 | CE-API-021 |
| EP-0643 | POST | `/api/v1/workspaces/{slug}/projects/{project_id}/work-items/{issue_id}/comments/` | V1 | V1WorkItemCommentEndpoints.CreateWorkItemCommentCommand | project.work_item_comment.create | I6 | CE-API-021 |
| EP-0644 | GET | `/api/v1/workspaces/{slug}/projects/{project_id}/work-items/{issue_id}/comments/{pk}/` | V1 | V1WorkItemCommentEndpoints.GetWorkItemCommentQuery | project.work_item_comment.read | I6 | CE-API-021 |
| EP-0645 | PATCH | `/api/v1/workspaces/{slug}/projects/{project_id}/work-items/{issue_id}/comments/{pk}/` | V1 | V1WorkItemCommentEndpoints.UpdateWorkItemCommentCommand | project.work_item_comment.update | I6 | CE-API-021 |
| EP-0646 | DELETE | `/api/v1/workspaces/{slug}/projects/{project_id}/work-items/{issue_id}/comments/{pk}/` | V1 | V1WorkItemCommentEndpoints.DeleteWorkItemCommentCommand | project.work_item_comment.delete | I6 | CE-API-021 |
| EP-0647 | GET | `/api/v1/workspaces/{slug}/issues/{project_identifier}-{issue_identifier}/` | V1 | V1WorkItemEndpoints.GetWorkItemByIdentifierQuery | project.work_item.read | I6 | CE-API-018 |
| EP-0648 | GET | `/api/v1/workspaces/{slug}/projects/{project_id}/issues/` | V1 | V1WorkItemEndpoints.ListWorkItemsQuery | project.work_item.read | I6 | CE-API-017 |
| EP-0649 | POST | `/api/v1/workspaces/{slug}/projects/{project_id}/issues/` | V1 | V1WorkItemEndpoints.CreateWorkItemCommand | project.work_item.create | I6 | CE-API-017 |
| EP-0650 | GET | `/api/v1/workspaces/{slug}/projects/{project_id}/issues/{pk}/` | V1 | V1WorkItemEndpoints.GetWorkItemQuery | project.work_item.read | I6 | CE-API-017 |
| EP-0651 | PATCH | `/api/v1/workspaces/{slug}/projects/{project_id}/issues/{pk}/` | V1 | V1WorkItemEndpoints.UpdateWorkItemCommand | project.work_item.update | I6 | CE-API-017 |
| EP-0652 | DELETE | `/api/v1/workspaces/{slug}/projects/{project_id}/issues/{pk}/` | V1 | V1WorkItemEndpoints.DeleteWorkItemCommand | project.work_item.delete | I6 | CE-API-017 |
| EP-0653 | GET | `/api/v1/workspaces/{slug}/projects/{project_id}/work-items/` | V1 | V1WorkItemEndpoints.ListWorkItemsQuery | project.work_item.read | I6 | CE-API-017 |
| EP-0654 | POST | `/api/v1/workspaces/{slug}/projects/{project_id}/work-items/` | V1 | V1WorkItemEndpoints.CreateWorkItemCommand | project.work_item.create | I6 | CE-API-017 |
| EP-0655 | GET | `/api/v1/workspaces/{slug}/projects/{project_id}/work-items/{pk}/` | V1 | V1WorkItemEndpoints.GetWorkItemQuery | project.work_item.read | I6 | CE-API-017 |
| EP-0656 | PATCH | `/api/v1/workspaces/{slug}/projects/{project_id}/work-items/{pk}/` | V1 | V1WorkItemEndpoints.UpdateWorkItemCommand | project.work_item.update | I6 | CE-API-017 |
| EP-0657 | DELETE | `/api/v1/workspaces/{slug}/projects/{project_id}/work-items/{pk}/` | V1 | V1WorkItemEndpoints.DeleteWorkItemCommand | project.work_item.delete | I6 | CE-API-017 |
| EP-0658 | GET | `/api/v1/workspaces/{slug}/work-items/{project_identifier}-{issue_identifier}/` | V1 | V1WorkItemEndpoints.GetWorkItemByIdentifierQuery | project.work_item.read | I6 | CE-API-018 |
| EP-0659 | GET | `/api/v1/workspaces/{slug}/projects/{project_id}/issues/{issue_id}/links/` | V1 | V1WorkItemLinkEndpoints.ListWorkItemLinksQuery | project.work_item_link.read | I6 | CE-API-020 |
| EP-0660 | POST | `/api/v1/workspaces/{slug}/projects/{project_id}/issues/{issue_id}/links/` | V1 | V1WorkItemLinkEndpoints.CreateWorkItemLinkCommand | project.work_item_link.create | I6 | CE-API-020 |
| EP-0661 | GET | `/api/v1/workspaces/{slug}/projects/{project_id}/issues/{issue_id}/links/{pk}/` | V1 | V1WorkItemLinkEndpoints.GetWorkItemLinkQuery | project.work_item_link.read | I6 | CE-API-020 |
| EP-0662 | PATCH | `/api/v1/workspaces/{slug}/projects/{project_id}/issues/{issue_id}/links/{pk}/` | V1 | V1WorkItemLinkEndpoints.UpdateWorkItemLinkCommand | project.work_item_link.update | I6 | CE-API-020 |
| EP-0663 | DELETE | `/api/v1/workspaces/{slug}/projects/{project_id}/issues/{issue_id}/links/{pk}/` | V1 | V1WorkItemLinkEndpoints.DeleteWorkItemLinkCommand | project.work_item_link.delete | I6 | CE-API-020 |
| EP-0664 | GET | `/api/v1/workspaces/{slug}/projects/{project_id}/work-items/{issue_id}/links/` | V1 | V1WorkItemLinkEndpoints.ListWorkItemLinksQuery | project.work_item_link.read | I6 | CE-API-020 |
| EP-0665 | POST | `/api/v1/workspaces/{slug}/projects/{project_id}/work-items/{issue_id}/links/` | V1 | V1WorkItemLinkEndpoints.CreateWorkItemLinkCommand | project.work_item_link.create | I6 | CE-API-020 |
| EP-0666 | GET | `/api/v1/workspaces/{slug}/projects/{project_id}/work-items/{issue_id}/links/{pk}/` | V1 | V1WorkItemLinkEndpoints.GetWorkItemLinkQuery | project.work_item_link.read | I6 | CE-API-020 |
| EP-0667 | PATCH | `/api/v1/workspaces/{slug}/projects/{project_id}/work-items/{issue_id}/links/{pk}/` | V1 | V1WorkItemLinkEndpoints.UpdateWorkItemLinkCommand | project.work_item_link.update | I6 | CE-API-020 |
| EP-0668 | DELETE | `/api/v1/workspaces/{slug}/projects/{project_id}/work-items/{issue_id}/links/{pk}/` | V1 | V1WorkItemLinkEndpoints.DeleteWorkItemLinkCommand | project.work_item_link.delete | I6 | CE-API-020 |
| EP-0669 | GET | `/api/v1/workspaces/{slug}/projects/{project_id}/work-items/{issue_id}/relations/` | V1 | V1WorkItemRelationEndpoints.ListWorkItemRelationsQuery | project.work_item_relation.read | I6 | CE-API-024 |
| EP-0670 | POST | `/api/v1/workspaces/{slug}/projects/{project_id}/work-items/{issue_id}/relations/` | V1 | V1WorkItemRelationEndpoints.CreateWorkItemRelationsCommand | project.work_item_relation.create | I6 | CE-API-024 |
| EP-0671 | GET | `/api/v1/workspaces/{slug}/issues/search/` | V1 | V1WorkItemSearchEndpoints.SearchWorkItemsQuery | workspace.search.read | I6 | CE-API-019 |
| EP-0672 | GET | `/api/v1/workspaces/{slug}/work-items/search/` | V1 | V1WorkItemSearchEndpoints.SearchWorkItemsQuery | workspace.search.read | I6 | CE-API-019 |

**Akzeptanzkriterien**

1. Contract-Szenarien mit Original-Golden für alle HTTP-Endpunkte dieses Pakets; Replay grün.
2. Job-/Consumer-Tests: Idempotenz (Inbox), Retry/Backoff, Zeitsteuerung mit `FixedClock`; neue Ereignistypen im Event-Katalog-Snapshot.
3. Bei Cron-Jobs: Registrierung in `CronRegistrationTests` mit Original-Zeit (UTC).
4. `ce-coverage-check --ids CE-API-017,CE-API-018,CE-API-019,CE-API-020,CE-API-021,CE-API-022,CE-API-023,CE-API-024,CE-API-025` grün (Mindestebenen 15 Anhang B).

**Testumfang**

- Pflicht-Ebenen (aus 15 Anhang B): L1, L3, L5
- Testprojekte: `Funk.PublicApi.Tests`

### WP-I6-013 – Public API v1: Cycles, Work Items in Cycles, Transfer, Cycle-Archiv, Modules, Work Items in Modulen, Modul-Archiv

| Merkmal | Wert |
|---|---|
| Inkrement | I6 |
| Typ (DoD 15 §3.15.3) | B – Backend-only |
| Größe | M |
| parallelisierbar | ja |
| Abhängigkeiten | WP-I6-012 |
| CE-IDs | CE-API-026, CE-API-027, CE-API-028, CE-API-029, CE-API-030, CE-API-031, CE-API-032 |

**Ziel.** v1-Endpunkte für Cycles und Module.

**Enthaltene CE-IDs**

| CE-ID | Feature | Status (15 Anh. B) | Inkrement laut 15 | Pflicht-Ebenen | Testprojekt | E2E-Spec |
|---|---|---|---|---|---|---|
| CE-API-026 | Cycles verwalten | übernommen | I6 | L1 L3 L5 | Funk.PublicApi.Tests | – |
| CE-API-027 | Work Items in Cycles | übernommen | I6 | L1 L3 L5 | Funk.PublicApi.Tests | – |
| CE-API-028 | Cycle-Transfer | übernommen | I6 | L1 L3 L5 | Funk.PublicApi.Tests | – |
| CE-API-029 | Cycle-Archiv | übernommen | I6 | L1 L3 L5 | Funk.PublicApi.Tests | – |
| CE-API-030 | Modules verwalten | übernommen | I6 | L1 L3 L5 | Funk.PublicApi.Tests | – |
| CE-API-031 | Work Items in Modulen | übernommen | I6 | L1 L3 L5 | Funk.PublicApi.Tests | – |
| CE-API-032 | Modul-Archiv | übernommen | I6 | L1 L3 L5 | Funk.PublicApi.Tests | – |

**Betroffene Module/Libs in `funk.`**

- Backend: `src/modules/PublicApi/Funk.PublicApi`

**Referenzdokumente**

- Architektur: 04 §4.19
- Analyse/Feature: `analysis/05-api-public-v1-space-instanz.md` §3.9, §3.11
- Feature-Katalog: `features/10-ce-feature-katalog.md` (Einträge CE-API-026, CE-API-027, CE-API-028, CE-API-029, CE-API-030, CE-API-031, CE-API-032)

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- Backend: `apps/api/plane/api/views/cycle.py`, `apps/api/plane/api/urls/cycle.py`, `apps/api/plane/api/serializers/cycle.py`, `apps/api/plane/utils/cycle_transfer_issues.py`, `apps/api/plane/api/views/module.py`, `apps/api/plane/api/urls/module.py`, `apps/api/plane/api/serializers/module.py`

**Endpunkte (Katalog 04, `architecture/_data/endpoints.json`; 26 registriert)**

| EP | Methode | Pfad | Oberfläche | Handler | Permission | Inkr. 04 | CE-IDs |
|---|---|---|---|---|---|---|---|
| EP-0541 | GET | `/api/v1/workspaces/{slug}/projects/{project_id}/archived-cycles/` | V1 | V1CycleEndpoints.ListArchivedCyclesQuery | project.cycle.read_archived | I6 | CE-API-029 |
| EP-0542 | DELETE | `/api/v1/workspaces/{slug}/projects/{project_id}/archived-cycles/{cycle_id}/unarchive/` | V1 | V1CycleEndpoints.UnarchiveCycleCommand | project.cycle.unarchive | I6 | CE-API-029 |
| EP-0543 | GET | `/api/v1/workspaces/{slug}/projects/{project_id}/cycles-lite/` | V1 | V1CycleEndpoints.ListCyclesLiteQuery | project.cycle.read | I6 | CE-API-026 |
| EP-0544 | GET | `/api/v1/workspaces/{slug}/projects/{project_id}/cycles/` | V1 | V1CycleEndpoints.ListCyclesQuery | project.cycle.read | I6 | CE-API-026 |
| EP-0545 | POST | `/api/v1/workspaces/{slug}/projects/{project_id}/cycles/` | V1 | V1CycleEndpoints.CreateCycleCommand | project.cycle.create | I6 | CE-API-026 |
| EP-0546 | POST | `/api/v1/workspaces/{slug}/projects/{project_id}/cycles/{cycle_id}/archive/` | V1 | V1CycleEndpoints.ArchiveCycleCommand | project.cycle.archive | I6 | CE-API-029 |
| EP-0547 | GET | `/api/v1/workspaces/{slug}/projects/{project_id}/cycles/{pk}/` | V1 | V1CycleEndpoints.GetCycleQuery | project.cycle.read | I6 | CE-API-026 |
| EP-0548 | PATCH | `/api/v1/workspaces/{slug}/projects/{project_id}/cycles/{pk}/` | V1 | V1CycleEndpoints.UpdateCycleCommand | project.cycle.update | I6 | CE-API-026 |
| EP-0549 | DELETE | `/api/v1/workspaces/{slug}/projects/{project_id}/cycles/{pk}/` | V1 | V1CycleEndpoints.DeleteCycleCommand | project.cycle.delete | I6 | CE-API-026 |
| EP-0550 | GET | `/api/v1/workspaces/{slug}/projects/{project_id}/cycles/{cycle_id}/cycle-issues/` | V1 | V1CycleWorkItemEndpoints.ListCycleWorkItemsQuery | project.cycle_work_item.read | I6 | CE-API-027 |
| EP-0551 | POST | `/api/v1/workspaces/{slug}/projects/{project_id}/cycles/{cycle_id}/cycle-issues/` | V1 | V1CycleWorkItemEndpoints.AddCycleWorkItemsCommand | project.cycle_work_item.create | I6 | CE-API-027 |
| EP-0552 | GET | `/api/v1/workspaces/{slug}/projects/{project_id}/cycles/{cycle_id}/cycle-issues/{issue_id}/` | V1 | V1CycleWorkItemEndpoints.GetCycleWorkItemQuery | project.cycle_work_item.read | I6 | CE-API-027 |
| EP-0553 | DELETE | `/api/v1/workspaces/{slug}/projects/{project_id}/cycles/{cycle_id}/cycle-issues/{issue_id}/` | V1 | V1CycleWorkItemEndpoints.RemoveCycleWorkItemCommand | project.cycle_work_item.delete | I6 | CE-API-027 |
| EP-0554 | POST | `/api/v1/workspaces/{slug}/projects/{project_id}/cycles/{cycle_id}/transfer-issues/` | V1 | V1CycleWorkItemEndpoints.TransferCycleWorkItemsCommand | project.cycle_work_item.transfer | I6 | CE-API-028 |
| EP-0586 | GET | `/api/v1/workspaces/{slug}/projects/{project_id}/archived-modules/` | V1 | V1ModuleEndpoints.ListArchivedModulesQuery | project.module.read_archived | I6 | CE-API-032 |
| EP-0587 | DELETE | `/api/v1/workspaces/{slug}/projects/{project_id}/archived-modules/{pk}/unarchive/` | V1 | V1ModuleEndpoints.UnarchiveModuleCommand | project.module.unarchive | I6 | CE-API-032 |
| EP-0588 | GET | `/api/v1/workspaces/{slug}/projects/{project_id}/modules-lite/` | V1 | V1ModuleEndpoints.ListModulesLiteQuery | project.module.read | I6 | CE-API-030 |
| EP-0589 | GET | `/api/v1/workspaces/{slug}/projects/{project_id}/modules/` | V1 | V1ModuleEndpoints.ListModulesQuery | project.module.read | I6 | CE-API-030 |
| EP-0590 | POST | `/api/v1/workspaces/{slug}/projects/{project_id}/modules/` | V1 | V1ModuleEndpoints.CreateModuleCommand | project.module.create | I6 | CE-API-030 |
| EP-0591 | GET | `/api/v1/workspaces/{slug}/projects/{project_id}/modules/{pk}/` | V1 | V1ModuleEndpoints.GetModuleQuery | project.module.read | I6 | CE-API-030 |
| EP-0592 | PATCH | `/api/v1/workspaces/{slug}/projects/{project_id}/modules/{pk}/` | V1 | V1ModuleEndpoints.UpdateModuleCommand | project.module.update | I6 | CE-API-030 |
| EP-0593 | DELETE | `/api/v1/workspaces/{slug}/projects/{project_id}/modules/{pk}/` | V1 | V1ModuleEndpoints.DeleteModuleCommand | project.module.delete | I6 | CE-API-030 |
| EP-0594 | POST | `/api/v1/workspaces/{slug}/projects/{project_id}/modules/{pk}/archive/` | V1 | V1ModuleEndpoints.ArchiveModuleCommand | project.module.archive | I6 | CE-API-032 |
| EP-0595 | GET | `/api/v1/workspaces/{slug}/projects/{project_id}/modules/{module_id}/module-issues/` | V1 | V1ModuleWorkItemEndpoints.ListModuleWorkItemsQuery | project.module_work_item.read | I6 | CE-API-031 |
| EP-0596 | POST | `/api/v1/workspaces/{slug}/projects/{project_id}/modules/{module_id}/module-issues/` | V1 | V1ModuleWorkItemEndpoints.AddModuleWorkItemsCommand | project.module_work_item.create | I6 | CE-API-031 |
| EP-0597 | DELETE | `/api/v1/workspaces/{slug}/projects/{project_id}/modules/{module_id}/module-issues/{issue_id}/` | V1 | V1ModuleWorkItemEndpoints.RemoveModuleWorkItemCommand | project.module_work_item.delete | I6 | CE-API-031 |

**Akzeptanzkriterien**

1. Contract-Szenarien mit Original-Golden für alle HTTP-Endpunkte dieses Pakets; Replay grün.
2. Job-/Consumer-Tests: Idempotenz (Inbox), Retry/Backoff, Zeitsteuerung mit `FixedClock`; neue Ereignistypen im Event-Katalog-Snapshot.
3. Bei Cron-Jobs: Registrierung in `CronRegistrationTests` mit Original-Zeit (UTC).
4. `ce-coverage-check --ids CE-API-026,CE-API-027,CE-API-028,CE-API-029,CE-API-030,CE-API-031,CE-API-032` grün (Mindestebenen 15 Anhang B).

**Testumfang**

- Pflicht-Ebenen (aus 15 Anhang B): L1, L3, L5
- Testprojekte: `Funk.PublicApi.Tests`

### WP-I6-014 – Webhook-Verwaltung: Liste, Anlage, Secret anzeigen/regenerieren/herunterladen, Bearbeitung, Löschung

| Merkmal | Wert |
|---|---|
| Inkrement | I6 |
| Typ (DoD 15 §3.15.3) | V – Vertikaler Schnitt |
| Größe | M |
| parallelisierbar | ja |
| Abhängigkeiten | WP-I5-999 |
| CE-IDs | CE-WH-002, CE-WH-003, CE-WH-004, CE-WH-005, CE-WH-006 |

**Ziel.** Settings-Seiten für Webhooks mit Secret-Verwaltung (`funk_wh_`-Präfix).

**Enthaltene CE-IDs**

| CE-ID | Feature | Status (15 Anh. B) | Inkrement laut 15 | Pflicht-Ebenen | Testprojekt | E2E-Spec |
|---|---|---|---|---|---|---|
| CE-WH-002 | Webhook-Liste | übernommen | I6 | L1 L2 L3 L5 L7 L8 | Funk.Webhooks.Tests | `web/settings/webhooks.spec.ts` |
| CE-WH-003 | Webhook anlegen | übernommen | I6 | L1 L2 L3 L5 L7 L8 | Funk.Webhooks.Tests | `web/settings/webhooks.spec.ts` |
| CE-WH-004 | Webhook-Secret anzeigen, regenerieren und herunterladen | übernommen | I6 | L1 L2 L3 L5 L7 L8 | Funk.Webhooks.Tests | `web/settings/webhooks.spec.ts` |
| CE-WH-005 | Webhook bearbeiten | übernommen | I6 | L1 L2 L3 L5 L7 L8 | Funk.Webhooks.Tests | `web/settings/webhooks.spec.ts` |
| CE-WH-006 | Webhook löschen | übernommen | I6 | L1 L2 L3 L5 L7 L8 | Funk.Webhooks.Tests | `web/settings/webhooks.spec.ts` |

**Betroffene Module/Libs in `funk.`**

- Backend: `src/modules/Webhooks/Funk.Webhooks`
- Frontend: `frontend/libs/web/settings` (web-hooks)

**Referenzdokumente**

- Architektur: 04 §4.20
- Architektur: 03 §3.4.16
- Analyse/Feature: `analysis/10b-frontend-cycles-modules-pages-views-weitere.md` §2.12, §3.10
- Analyse/Feature: `analysis/08-frontend-web-architektur.md` §2.2
- Analyse/Feature: `analysis/03-api-intern-workspace-projekt-user.md` §3.12
- Analyse/Feature: `analysis/13b-shared-packages-i18n.md` §2.7
- Analyse/Feature: `analysis/07-hintergrundjobs-mail-storage-webhooks.md` §2.10
- Feature-Katalog: `features/10-ce-feature-katalog.md` (Einträge CE-WH-002, CE-WH-003, CE-WH-004, CE-WH-005, CE-WH-006)

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- Backend: `apps/api/plane/app/views/webhook/base.py`, `apps/api/plane/app/serializers/webhook.py`, `apps/api/plane/utils/ip_address.py`
- Frontend: `apps/web/components/web-hooks/webhooks-list.tsx`, `apps/web/components/web-hooks/webhooks-list-item.tsx`, `apps/web/app/(all)/[workspaceSlug]/(settings)/settings/(workspace)/webhooks/page.tsx`, `apps/web/app/(all)/[workspaceSlug]/(settings)/settings/(workspace)/layout.tsx`, `apps/web/app/(all)/[workspaceSlug]/(settings)/settings/(workspace)/page.tsx`, `apps/web/app/(all)/[workspaceSlug]/(settings)/settings/(workspace)/members/page.tsx`, `apps/web/app/(all)/[workspaceSlug]/(settings)/settings/(workspace)/exports/page.tsx`, `apps/web/app/(all)/[workspaceSlug]/(settings)/settings/(workspace)/webhooks/[webhookId]/page.tsx`, `packages/constants/src/settings/workspace.ts`, `apps/web/services/webhook.service.ts`, `apps/web/components/web-hooks/create-webhook-modal.tsx`, `apps/web/components/web-hooks/form/form.tsx`, `apps/web/components/web-hooks/form/input.tsx`, `apps/web/components/web-hooks/form/event-types.tsx`, `apps/web/components/web-hooks/form/individual-event-options.tsx`, `packages/services/src/developer/webhook.service.ts`, `packages/services/src/developer/api-token.service.ts`, `packages/types/src/webhook.ts`, `packages/types/src/api_token.ts`, `apps/web/components/web-hooks/form/secret-key.tsx`, `apps/web/components/web-hooks/generated-hook-details.tsx`, `apps/web/components/web-hooks/utils.ts`, `apps/web/components/web-hooks/form/toggle.tsx`, `apps/web/components/web-hooks/form/delete-section.tsx`, `apps/web/components/web-hooks/delete-webhook-modal.tsx`

**Endpunkte (Katalog 04, `architecture/_data/endpoints.json`; 6 registriert)**

| EP | Methode | Pfad | Oberfläche | Handler | Permission | Inkr. 04 | CE-IDs |
|---|---|---|---|---|---|---|---|
| EP-0715 | GET | `/api/workspaces/{slug}/webhooks/` | App | WebhookEndpoints.ListWebhooksQuery | workspace.webhook.read | I6 | CE-WH-002 |
| EP-0716 | POST | `/api/workspaces/{slug}/webhooks/` | App | WebhookEndpoints.CreateWebhookCommand | workspace.webhook.create | I6 | CE-WH-003, CE-WH-011 |
| EP-0717 | GET | `/api/workspaces/{slug}/webhooks/{pk}/` | App | WebhookEndpoints.GetWebhookQuery | workspace.webhook.read | I6 | CE-WH-004, CE-WH-005 |
| EP-0718 | PATCH | `/api/workspaces/{slug}/webhooks/{pk}/` | App | WebhookEndpoints.UpdateWebhookCommand | workspace.webhook.update | I6 | CE-WH-005, CE-WH-011 |
| EP-0719 | DELETE | `/api/workspaces/{slug}/webhooks/{pk}/` | App | WebhookEndpoints.DeleteWebhookCommand | workspace.webhook.delete | I6 | CE-WH-006 |
| EP-0720 | POST | `/api/workspaces/{slug}/webhooks/{pk}/regenerate/` | App | WebhookEndpoints.RegenerateWebhookSecretCommand | workspace.webhook.create | I6 | CE-WH-004 |

**Akzeptanzkriterien**

1. Contract: je Endpunkt dieses Pakets ≥ 1 Szenario mit Golden vom Original (Erfolg, Berechtigungsfehler, Validierungsfehler); Replay grün (L5).
2. Permission-Matrix (05 Anhang B) für alle Endpunkte dieses Pakets als L3-Test grün; Tenant-Isolation geprüft.
3. Signal-Stores strukturgleich zum MobX-Original (`store-parity-check`), Vitest je Action (L2).
4. E2E-Specs dieses Pakets grün gegen Original **und** funk. (Dual-Target, Pflichtszenarien 15 §3.9.3).
5. Visual-/DOM-/a11y-Prüfpunkte der betroffenen Screens (09 §4.14, 15 §3.10.2) innerhalb der Schwellwerte 15 §3.10.3 (Chromium); i18n-Schlüssel nur aus den Original-Locales (de/en).
6. `ce-coverage-check --ids CE-WH-002,CE-WH-003,CE-WH-004,CE-WH-005,CE-WH-006` grün (Mindestebenen 15 Anhang B).

**Testumfang**

- Pflicht-Ebenen (aus 15 Anhang B): L1, L2, L3, L5, L7, L8
- Testprojekte: `Funk.Webhooks.Tests`
- E2E-Specs (`frontend/apps/e2e/`): `web/settings/webhooks.spec.ts`

### WP-I6-015 – Webhook-Zustellung: Datenmodell/Event-Typen, Zustellung, Payload, Deaktivierungs-Mail, Protokoll, SSRF-Schutz

| Merkmal | Wert |
|---|---|
| Inkrement | I6 |
| Typ (DoD 15 §3.15.3) | B – Backend-only |
| Größe | L |
| parallelisierbar | ja |
| Abhängigkeiten | WP-I6-014, WP-I6-202 |
| CE-IDs | CE-WH-001, CE-WH-007, CE-WH-008, CE-WH-009, CE-WH-010, CE-WH-011 |

**Ziel.** `WebhookEventConsumer` (Trigger-Tabelle: 24 Original-Stellen + 6 Auslöser, ABG-137), Job `webhooks.deliver` mit `X-Funk-Signature` (HMAC-SHA256 über die gesendeten Bytes), stabiler `X-Funk-Delivery`, 6 Versuche, Deaktivierung + Mail M10, Zustellprotokoll, SSRF-Client `webhooks`.

**Enthaltene CE-IDs**

| CE-ID | Feature | Status (15 Anh. B) | Inkrement laut 15 | Pflicht-Ebenen | Testprojekt | E2E-Spec |
|---|---|---|---|---|---|---|
| CE-WH-001 | Webhook-Datenmodell und Event-Typen | übernommen | I6 | L1 L2 L3 L5 L7 L8 | Funk.Webhooks.Tests | `web/settings/webhooks.spec.ts` |
| CE-WH-007 | Webhook-Zustellung | übernommen | I6 | L1 L2 L3 L6 L7 L8 | Funk.Webhooks.Tests | `web/settings/webhooks.spec.ts` |
| CE-WH-008 | Webhook-Payload-Format | übernommen | I6 | L1 L2 L3 L4 L5 L7 L8 (D15-SEC-09) | Funk.Webhooks.Tests | `web/settings/webhooks.spec.ts` |
| CE-WH-009 | Webhook-Deaktivierungs-Mail | übernommen | I6 | L1 L2 L3 L4 L6 L7 L8 (G-MAIL) | Funk.Webhooks.Tests | `web/settings/webhooks.spec.ts` |
| CE-WH-010 | Webhook-Zustellprotokoll (nur API) | übernommen | I6 | L1 L2 L3 L5 L7 L8 | Funk.Webhooks.Tests | `web/settings/webhooks.spec.ts` |
| CE-WH-011 | SSRF-Schutz und Ziel-Allowlists für Webhooks | übernommen | I6 | L1 L2 L3 L7 L8 | Funk.Webhooks.Tests | `web/settings/webhooks.spec.ts` |

**Betroffene Module/Libs in `funk.`**

- Backend: `src/modules/Webhooks/Funk.Webhooks`

**Referenzdokumente**

- Architektur: 06 §3.14, §5.8, D06-ADR-15, -16
- Architektur: 05 §3.17.2
- Architektur: 04 §3.17, §4.27
- Analyse/Feature: `analysis/02a-datenmodell-kern.md` §2.3
- Analyse/Feature: `analysis/10b-frontend-cycles-modules-pages-views-weitere.md` §2.12
- Analyse/Feature: `analysis/07-hintergrundjobs-mail-storage-webhooks.md` §2.10, §3.4, §2.11
- Analyse/Feature: `analysis/06-auth-sicherheit-querschnitt.md` §2.14
- Analyse/Feature: `analysis/05-api-public-v1-space-instanz.md` §3.16
- Analyse/Feature: `analysis/03-api-intern-workspace-projekt-user.md` §3.12
- Analyse/Feature: `analysis/01-gesamtarchitektur-infrastruktur.md` §2.6
- Feature-Katalog: `features/10-ce-feature-katalog.md` (Einträge CE-WH-001, CE-WH-007, CE-WH-008, CE-WH-009, CE-WH-010, CE-WH-011)

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- Backend: `apps/api/plane/db/models/webhook.py`, `apps/api/plane/app/serializers/webhook.py`, `apps/api/plane/bgtasks/webhook_task.py`, `apps/api/plane/app/views/webhook/base.py`, `apps/api/plane/utils/ip_address.py`, `apps/api/plane/utils/url_security.py`, `apps/api/plane/api/serializers/__init__.py`, `apps/api/templates/emails/notifications/webhook-deactivate.html`, `apps/api/plane/bgtasks/cleanup_task.py`, `apps/api/plane/settings/common.py`
- Frontend: `apps/web/components/web-hooks/create-webhook-modal.tsx`, `apps/web/components/web-hooks/form/form.tsx`, `apps/web/components/web-hooks/form/input.tsx`, `apps/web/components/web-hooks/form/event-types.tsx`, `apps/web/components/web-hooks/form/individual-event-options.tsx`, `apps/web/services/webhook.service.ts`

**Endpunkte (Katalog 04, `architecture/_data/endpoints.json`; 1 registriert)**

| EP | Methode | Pfad | Oberfläche | Handler | Permission | Inkr. 04 | CE-IDs |
|---|---|---|---|---|---|---|---|
| EP-0714 | GET | `/api/workspaces/{slug}/webhook-logs/{webhook_id}/` | App | WebhookEndpoints.ListWebhookLogsQuery | workspace.webhook.read | I6 | CE-WH-010 |

**Akzeptanzkriterien**

1. `WebhookTriggerCoverageTests` grün; Payload-Golden je Ereignis gegen das Original (Header-Namen gemäß ADR-009C, Abweichung dokumentiert).
2. Contract-Szenarien mit Original-Golden für alle HTTP-Endpunkte dieses Pakets; Replay grün.
3. Job-/Consumer-Tests: Idempotenz (Inbox), Retry/Backoff, Zeitsteuerung mit `FixedClock`; neue Ereignistypen im Event-Katalog-Snapshot.
4. Bei Cron-Jobs: Registrierung in `CronRegistrationTests` mit Original-Zeit (UTC).
5. `ce-coverage-check --ids CE-WH-001,CE-WH-007,CE-WH-008,CE-WH-009,CE-WH-010,CE-WH-011` grün (Mindestebenen 15 Anhang B).

**Testumfang**

- Pflicht-Ebenen (aus 15 Anhang B): L1, L2, L3, L4, L5, L6, L7, L8
- Testprojekte: `Funk.Webhooks.Tests`
- E2E-Specs (`frontend/apps/e2e/`): `web/settings/webhooks.spec.ts`

### WP-I6-016 – API-Tokens: Liste, Anlage, Löschung

| Merkmal | Wert |
|---|---|
| Inkrement | I6 |
| Typ (DoD 15 §3.15.3) | V – Vertikaler Schnitt |
| Größe | M |
| parallelisierbar | ja |
| Abhängigkeiten | WP-I5-999 |
| CE-IDs | CE-WH-012, CE-WH-013, CE-WH-014 |

**Ziel.** Persönliche API-Tokens (`funk_api_`-Präfix) mit Liste, Anlage (einmalige Anzeige) und Löschung.

**Enthaltene CE-IDs**

| CE-ID | Feature | Status (15 Anh. B) | Inkrement laut 15 | Pflicht-Ebenen | Testprojekt | E2E-Spec |
|---|---|---|---|---|---|---|
| CE-WH-012 | API-Token-Liste | übernommen | I6 | L1 L2 L3 L5 L7 L8 | Funk.Identity.Tests | `web/settings/api-tokens.spec.ts` |
| CE-WH-013 | API-Token anlegen | übernommen | I6 | L1 L2 L3 L5 L7 L8 | Funk.Identity.Tests | `web/settings/api-tokens.spec.ts` |
| CE-WH-014 | API-Token löschen | übernommen | I6 | L1 L2 L3 L5 L7 L8 | Funk.Identity.Tests | `web/settings/api-tokens.spec.ts` |

**Betroffene Module/Libs in `funk.`**

- Backend: `src/modules/Identity/Funk.Identity` (ApiTokens)
- Frontend: `frontend/libs/web/settings` (api-token)

**Referenzdokumente**

- Architektur: 05 §3.12.3
- Architektur: 04 §4.1
- Analyse/Feature: `analysis/10b-frontend-cycles-modules-pages-views-weitere.md` §2.13
- Analyse/Feature: `analysis/10a-frontend-workspace-projekt-navigation.md` §2.13
- Analyse/Feature: `analysis/02a-datenmodell-kern.md` §3.11
- Analyse/Feature: `analysis/03-api-intern-workspace-projekt-user.md` §3.12
- Analyse/Feature: `analysis/13b-shared-packages-i18n.md` §2.7
- Feature-Katalog: `features/10-ce-feature-katalog.md` (Einträge CE-WH-012, CE-WH-013, CE-WH-014)

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- Backend: `apps/api/plane/db/models/api.py`, `apps/api/plane/app/views/api.py`, `apps/api/plane/app/serializers/api.py`, `apps/api/plane/api/middleware/api_authentication.py`
- Frontend: `apps/web/components/api-token/token-list-item.tsx`, `apps/web/components/settings/profile/content/pages/api-tokens.tsx`, `packages/services/src/developer/api-token.service.ts`, `packages/services/src/developer/webhook.service.ts`, `packages/types/src/webhook.ts`, `packages/types/src/api_token.ts`, `apps/web/components/api-token/modal/create-token-modal.tsx`, `apps/web/components/api-token/modal/form.tsx`, `apps/web/components/api-token/modal/generated-token-details.tsx`, `apps/web/components/api-token/delete-token-modal.tsx`

**Endpunkte (Katalog 04, `architecture/_data/endpoints.json`; 5 registriert)**

| EP | Methode | Pfad | Oberfläche | Handler | Permission | Inkr. 04 | CE-IDs |
|---|---|---|---|---|---|---|---|
| EP-0042 | GET | `/api/users/api-tokens/` | App | ApiTokenEndpoints.ListApiTokensQuery | user.api_token.read | I6 | CE-WH-012 |
| EP-0043 | POST | `/api/users/api-tokens/` | App | ApiTokenEndpoints.CreateApiTokenCommand | user.api_token.create | I6 | CE-WH-013 |
| EP-0044 | GET | `/api/users/api-tokens/{pk}/` | App | ApiTokenEndpoints.GetApiTokenQuery | user.api_token.read | I6 | CE-WH-012 |
| EP-0045 | PATCH | `/api/users/api-tokens/{pk}/` | App | ApiTokenEndpoints.UpdateApiTokenCommand | user.api_token.update | I6 | CE-WH-012 |
| EP-0046 | DELETE | `/api/users/api-tokens/{pk}/` | App | ApiTokenEndpoints.DeleteApiTokenCommand | user.api_token.delete | I6 | CE-WH-014 |

**Akzeptanzkriterien**

1. Contract: je Endpunkt dieses Pakets ≥ 1 Szenario mit Golden vom Original (Erfolg, Berechtigungsfehler, Validierungsfehler); Replay grün (L5).
2. Permission-Matrix (05 Anhang B) für alle Endpunkte dieses Pakets als L3-Test grün; Tenant-Isolation geprüft.
3. Signal-Stores strukturgleich zum MobX-Original (`store-parity-check`), Vitest je Action (L2).
4. E2E-Specs dieses Pakets grün gegen Original **und** funk. (Dual-Target, Pflichtszenarien 15 §3.9.3).
5. Visual-/DOM-/a11y-Prüfpunkte der betroffenen Screens (09 §4.14, 15 §3.10.2) innerhalb der Schwellwerte 15 §3.10.3 (Chromium); i18n-Schlüssel nur aus den Original-Locales (de/en).
6. `ce-coverage-check --ids CE-WH-012,CE-WH-013,CE-WH-014` grün (Mindestebenen 15 Anhang B).

**Testumfang**

- Pflicht-Ebenen (aus 15 Anhang B): L1, L2, L3, L5, L7, L8
- Testprojekte: `Funk.Identity.Tests`
- E2E-Specs (`frontend/apps/e2e/`): `web/settings/api-tokens.spec.ts`

### WP-I6-017 – Work-Item-Export (CSV/XLSX/JSON), Export-Historie und Download

| Merkmal | Wert |
|---|---|
| Inkrement | I6 |
| Typ (DoD 15 §3.15.3) | B – Backend-only |
| Größe | M |
| parallelisierbar | ja |
| Abhängigkeiten | WP-I6-202 |
| CE-IDs | CE-EXP-001, CE-EXP-002 |

**Ziel.** Job `exports.work_items` mit Spalten/Reihenfolge/Kopfzeilen/Formel-Schutz wie `API/utils/porters/**` (CsvHelper, ClosedXML), Ablage im Objektspeicher, Download-Link 7 Tage, Historie.

**Enthaltene CE-IDs**

| CE-ID | Feature | Status (15 Anh. B) | Inkrement laut 15 | Pflicht-Ebenen | Testprojekt | E2E-Spec |
|---|---|---|---|---|---|---|
| CE-EXP-001 | Work-Item-Export (CSV/XLSX/JSON) | übernommen | I6 | L1 L2 L3 L4 L5 L7 L8 (G-EXPORT) | Funk.Exports.Tests | `web/settings/exports.spec.ts` |
| CE-EXP-002 | Export-Historie und Download | übernommen | I6 | L1 L2 L3 L4 L5 L7 L8 (G-MAIL) | Funk.Exports.Tests | `web/settings/exports.spec.ts` |

**Betroffene Module/Libs in `funk.`**

- Backend: `src/modules/Exports/Funk.Exports`
- Frontend: `frontend/libs/web/settings` (exporter)

**Referenzdokumente**

- Architektur: 06 §3.15.1, §4.12, D06-ADR-17
- Analyse/Feature: `analysis/10b-frontend-cycles-modules-pages-views-weitere.md` §2.14
- Analyse/Feature: `analysis/07-hintergrundjobs-mail-storage-webhooks.md` §2.12
- Analyse/Feature: `analysis/03-api-intern-workspace-projekt-user.md` §3.16
- Analyse/Feature: `analysis/02a-datenmodell-kern.md` §3.18
- Analyse/Feature: `analysis/06-auth-sicherheit-querschnitt.md` §2.13
- Feature-Katalog: `features/10-ce-feature-katalog.md` (Einträge CE-EXP-001, CE-EXP-002)

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- Backend: `apps/api/plane/bgtasks/export_task.py`, `apps/api/plane/utils/porters/serializers/issue.py`, `apps/api/plane/utils/porters/formatters.py`, `apps/api/plane/app/views/exporter/base.py`, `apps/api/plane/db/models/exporter.py`, `apps/api/plane/bgtasks/exporter_expired_task.py`, `apps/api/plane/utils/porters/exporter.py`, `apps/api/plane/utils/csv_utils.py`
- Frontend: `apps/web/components/exporter/export-form.tsx`, `apps/web/components/exporter/guide.tsx`, `apps/web/app/(all)/[workspaceSlug]/(settings)/settings/(workspace)/exports/page.tsx`, `apps/web/services/project/project-export.service.ts`, `apps/web/services/integrations/integration.service.ts`, `apps/web/components/exporter/prev-exports.tsx`, `apps/web/components/exporter/column.tsx`

**Endpunkte (Katalog 04, `architecture/_data/endpoints.json`; 2 registriert)**

| EP | Methode | Pfad | Oberfläche | Handler | Permission | Inkr. 04 | CE-IDs |
|---|---|---|---|---|---|---|---|
| EP-0724 | GET | `/api/workspaces/{slug}/export-issues/` | App | ExportEndpoints.ListExportsQuery | workspace.export.read | I6 | CE-EXP-001, CE-EXP-002 |
| EP-0725 | POST | `/api/workspaces/{slug}/export-issues/` | App | ExportEndpoints.CreateWorkItemExportCommand | workspace.export.create | I6 | CE-EXP-001, CE-EXP-002 |

**Akzeptanzkriterien**

1. G-EXPORT (28 Spalten, 06 §4.12) grün.
2. Contract-Szenarien mit Original-Golden für alle HTTP-Endpunkte dieses Pakets; Replay grün.
3. Job-/Consumer-Tests: Idempotenz (Inbox), Retry/Backoff, Zeitsteuerung mit `FixedClock`; neue Ereignistypen im Event-Katalog-Snapshot.
4. Bei Cron-Jobs: Registrierung in `CronRegistrationTests` mit Original-Zeit (UTC).
5. `ce-coverage-check --ids CE-EXP-001,CE-EXP-002` grün (Mindestebenen 15 Anhang B).

**Testumfang**

- Pflicht-Ebenen (aus 15 Anhang B): L1, L2, L3, L4, L5, L7, L8
- Testprojekte: `Funk.Exports.Tests`
- E2E-Specs (`frontend/apps/e2e/`): `web/settings/exports.spec.ts`

### WP-I6-018 – KI-Assistent im Work-Item-Modal und Unsplash-Bildsuche

| Merkmal | Wert |
|---|---|
| Inkrement | I6 |
| Typ (DoD 15 §3.15.3) | V – Vertikaler Schnitt |
| Größe | M |
| parallelisierbar | ja |
| Abhängigkeiten | WP-I5-999 |
| CE-IDs | CE-AI-001, CE-AI-002 |

**Ziel.** KI-Assistent über `IChatClient` (Microsoft.Extensions.AI, OpenAI-kompatibler Endpunkt, lokal betreibbar) und Unsplash-Suche; beides optional und abschaltbar (ADR-004).

**Enthaltene CE-IDs**

| CE-ID | Feature | Status (15 Anh. B) | Inkrement laut 15 | Pflicht-Ebenen | Testprojekt | E2E-Spec |
|---|---|---|---|---|---|---|
| CE-AI-001 | KI-Assistent im Work-Item-Modal | übernommen | I6 | L1 L2 L3 L5 L7 L8 | Funk.Assistant.Tests | `web/ai/ai-unsplash.spec.ts` |
| CE-AI-002 | Unsplash-Bildsuche | übernommen | I6 | L1 L2 L3 L5 L7 L8 | Funk.Assistant.Tests | `web/ai/ai-unsplash.spec.ts` |

**Betroffene Module/Libs in `funk.`**

- Backend: `src/modules/Assistant/Funk.Assistant`
- Backend: `src/platform/Funk.Platform.Ai`
- Frontend: `frontend/libs/web/work-items` (gpt-assistant)
- Frontend: `frontend/libs/shared/blocks` (image-picker Unsplash-Tab)

**Referenzdokumente**

- Architektur: 11 §3.13–§3.17, §5.7, §5.8
- Architektur: 04 §4.22
- Architektur: 17 Z-111
- Analyse/Feature: `analysis/09-frontend-arbeitsobjekte-layouts.md` §2.16
- Analyse/Feature: `analysis/10a-frontend-workspace-projekt-navigation.md` §2.16
- Analyse/Feature: `analysis/03-api-intern-workspace-projekt-user.md` §3.17
- Analyse/Feature: `analysis/13b-shared-packages-i18n.md` §2.7
- Feature-Katalog: `features/10-ce-feature-katalog.md` (Einträge CE-AI-001, CE-AI-002)

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- Backend: `apps/api/plane/app/views/external/base.py`
- Frontend: `apps/web/components/issues/issue-modal/components/description-editor.tsx`, `apps/web/components/core/modals/gpt-assistant-popover.tsx`, `apps/web/services/ai.service.ts`, `packages/services/src/ai/ai.service.ts`, `packages/constants/src/ai.ts`, `apps/web/services/file.service.ts`, `apps/web/components/core/image-picker-popover.tsx`

**Endpunkte (Katalog 04, `architecture/_data/endpoints.json`; 3 registriert)**

| EP | Methode | Pfad | Oberfläche | Handler | Permission | Inkr. 04 | CE-IDs |
|---|---|---|---|---|---|---|---|
| EP-0726 | POST | `/api/workspaces/{slug}/ai-assistant/` | App | AiAssistantEndpoints.RunWorkspaceAiAssistantCommand | workspace.ai_assistant.use | I6 | CE-AI-001 |
| EP-0727 | POST | `/api/workspaces/{slug}/projects/{project_id}/ai-assistant/` | App | AiAssistantEndpoints.RunProjectAiAssistantCommand | project.ai_assistant.use | I6 | CE-AI-001 |
| EP-0728 | GET | `/api/unsplash/` | App | UnsplashImageEndpoints.SearchUnsplashQuery | user.unsplash.read | I6 | CE-AI-002 |

**Akzeptanzkriterien**

1. Contract: je Endpunkt dieses Pakets ≥ 1 Szenario mit Golden vom Original (Erfolg, Berechtigungsfehler, Validierungsfehler); Replay grün (L5).
2. Permission-Matrix (05 Anhang B) für alle Endpunkte dieses Pakets als L3-Test grün; Tenant-Isolation geprüft.
3. Signal-Stores strukturgleich zum MobX-Original (`store-parity-check`), Vitest je Action (L2).
4. E2E-Specs dieses Pakets grün gegen Original **und** funk. (Dual-Target, Pflichtszenarien 15 §3.9.3).
5. Visual-/DOM-/a11y-Prüfpunkte der betroffenen Screens (09 §4.14, 15 §3.10.2) innerhalb der Schwellwerte 15 §3.10.3 (Chromium); i18n-Schlüssel nur aus den Original-Locales (de/en).
6. `ce-coverage-check --ids CE-AI-001,CE-AI-002` grün (Mindestebenen 15 Anhang B).

**Testumfang**

- Pflicht-Ebenen (aus 15 Anhang B): L1, L2, L3, L5, L7, L8
- Testprojekte: `Funk.Assistant.Tests`
- E2E-Specs (`frontend/apps/e2e/`): `web/ai/ai-unsplash.spec.ts`

### WP-I6-201 – Erweiterungspunkte Public API: IV1PayloadExtension, IV1FilterParameterBinding, erweiterbare OpenAPI-Gruppen

| Merkmal | Wert |
|---|---|
| Inkrement | I6 |
| Typ (DoD 15 §3.15.3) | X – Erweiterungspunkt 🧱 |
| Größe | S |
| parallelisierbar | nein |
| Abhängigkeiten | WP-I5-999 |
| CE-IDs | – (keine; Erweiterungspunkt) |
| Andockstelle | 16 §3.3.0 E-07, E-19; 16 §4.6 (Träger CE-API-017, CE-API-019) |

**Ziel.** `IV1PayloadExtension` (Typ-/Property-Felder in v1-Antworten, E-07 Teil v1; `IExpandProvider` liegt seit WP-I2-205 vor und wird für v1-`expand` mitbenutzt), `IV1FilterParameterBinding` (E-19, ohne Bindung Original-400 für `pql`/`filters`), erweiterbare OpenAPI-Dokumentgruppen.

**Betroffene Module/Libs in `funk.`**

- Backend: `src/modules/PublicApi/Funk.PublicApi/Extensions/`
- Backend: `src/modules/WorkItems/Funk.WorkItems.Contracts/Query/IV1FilterParameterBinding.cs`

**Referenzdokumente**

- Architektur: 04 §5.6
- Architektur: 16 §3.3.0 E-07/E-19

**Akzeptanzkriterien**

1. OpenAPI-Golden `v1.original.json` unverändert mit CE-Defaults; Fake-Payload-Extension ergänzt ein Feld ohne CE-Änderung (Typ X).
2. Contract (Interface/Schema/Token) + CE-Default-Implementierung; Eintrag in `tests/extension-points.yaml`.
3. Test „CE-Default = Original-Verhalten“ (Contract-Replay unverändert grün).
4. Test mit Fake-Erweiterung aus `Funk.BuildingBlocks.Testing/Extensions` bzw. `provideFakeExtensions()` beweist Erweiterbarkeit ohne CE-Änderung (DoD Typ X).

**Testumfang**

- Typ-X-Tests (CE-Default unverändert, Fake-Erweiterung wirkt ohne CE-Änderung), L0-Inventarabgleich `ExtensionPointInventoryTests`/`extension-registry-check`.

### WP-I6-202 – Erweiterungspunkte IWebhookEventSource und IExportTypeProvider

| Merkmal | Wert |
|---|---|
| Inkrement | I6 |
| Typ (DoD 15 §3.15.3) | X – Erweiterungspunkt 🧱 |
| Größe | S |
| parallelisierbar | nein |
| Abhängigkeiten | WP-I5-999 |
| CE-IDs | – (keine; Erweiterungspunkt) |
| Andockstelle | 16 §3.3.0 E-08, E-16; 16 §4.6 (Träger CE-WH-001/-007/-008, CE-EXP-001/-002) |

**Ziel.** Zusätzliche Webhook-Ereignisarten über `IWebhookEventSource` (E-08, CE: `project`, `issue`, `module`, `cycle`, `issue_comment`) und Exporttypen über `IExportTypeProvider` (E-16).

**Betroffene Module/Libs in `funk.`**

- Backend: `src/modules/Webhooks/Funk.Webhooks.Contracts`
- Backend: `src/modules/Exports/Funk.Exports.Contracts`

**Referenzdokumente**

- Architektur: 06 §5.9
- Architektur: 16 §3.3.0 E-08/E-16

**Akzeptanzkriterien**

1. Fake-Quelle erzeugt eine neue Webhook-Ereignisart, Fake-Exporttyp erscheint in der Export-Auswahl (Typ X).
2. Contract (Interface/Schema/Token) + CE-Default-Implementierung; Eintrag in `tests/extension-points.yaml`.
3. Test „CE-Default = Original-Verhalten“ (Contract-Replay unverändert grün).
4. Test mit Fake-Erweiterung aus `Funk.BuildingBlocks.Testing/Extensions` bzw. `provideFakeExtensions()` beweist Erweiterbarkeit ohne CE-Änderung (DoD Typ X).

**Testumfang**

- Typ-X-Tests (CE-Default unverändert, Fake-Erweiterung wirkt ohne CE-Änderung), L0-Inventarabgleich `ExtensionPointInventoryTests`/`extension-registry-check`.

### WP-I6-203 – Erweiterungspunkte Space/Admin: SPACE_ROUTE_EXTENSIONS, EDITOR_EXTENSIONS (Space), ADMIN-Registries mit CE-Inhalt

| Merkmal | Wert |
|---|---|
| Inkrement | I6 |
| Typ (DoD 15 §3.15.3) | X – Erweiterungspunkt 🧱 |
| Größe | S |
| parallelisierbar | nein |
| Abhängigkeiten | WP-I5-999 |
| CE-IDs | – (keine; Erweiterungspunkt) |
| Andockstelle | 16 §1.4 Zeile I6; 16 §4.6 (Träger CE-SPACE-001/-018/-025, CE-INST-003/-025) |

**Ziel.** Space-Routen-Registry, Editor-Erweiterungen im Space-Scope (S44) und Befüllung der Admin-Registries (`ADMIN_SETTINGS_PAGES`, `ADMIN_ROUTE_EXTENSIONS`, `ADMIN_HEADER_SEGMENT_LABELS`) mit allen CE-Seiten.

**Betroffene Module/Libs in `funk.`**

- Frontend: `frontend/libs/space/extensions`
- Frontend: `frontend/libs/admin/extensions`

**Referenzdokumente**

- Architektur: 08 §6.4
- Architektur: 16 §1.4 Zeile I6
- Architektur: 17 ABG-023

**Akzeptanzkriterien**

1. Fake-Space-Route und Fake-Admin-Seite erscheinen ohne CE-Änderung (Typ X).
2. Contract (Interface/Schema/Token) + CE-Default-Implementierung; Eintrag in `tests/extension-points.yaml`.
3. Test „CE-Default = Original-Verhalten“ (Contract-Replay unverändert grün).
4. Test mit Fake-Erweiterung aus `Funk.BuildingBlocks.Testing/Extensions` bzw. `provideFakeExtensions()` beweist Erweiterbarkeit ohne CE-Änderung (DoD Typ X).

**Testumfang**

- Typ-X-Tests (CE-Default unverändert, Fake-Erweiterung wirkt ohne CE-Änderung), L0-Inventarabgleich `ExtensionPointInventoryTests`/`extension-registry-check`.

### WP-I6-999 – Abnahme I6 – Außenwirkung & Administration (G5)

| Merkmal | Wert |
|---|---|
| Inkrement | I6 |
| Typ (DoD 15 §3.15.3) | A – Inkrement-Abnahme |
| Größe | S |
| parallelisierbar | nein |
| Abhängigkeiten | WP-I6-001, WP-I6-002, WP-I6-003, WP-I6-004, WP-I6-005, WP-I6-006, WP-I6-007, WP-I6-008, WP-I6-009, WP-I6-010, WP-I6-011, WP-I6-012, WP-I6-013, WP-I6-014, WP-I6-015, WP-I6-016, WP-I6-017, WP-I6-018, WP-I6-201, WP-I6-202, WP-I6-203 |
| CE-IDs | – (keine; Baustein/Spike/Abnahme) |

**Ziel.** Inkrement-Abnahme I6 nach G5 und Meilenstein M6.

**Referenzdokumente**

- Architektur: plan/01-roadmap-ce.md §4 (M6)
- Architektur: 15 §3.16 Zeile I6

**Akzeptanzkriterien**

1. Alle Abnahmekriterien M6 erfüllt; `docs/acceptance/I6.md` generiert.
2. G5 `--inc <In> --strict` grün: `ce-coverage-check`, `original-test-ledger`, Parity-Report (0 ungenehmigte Abweichungen, Endpunkt-Abdeckung des Inkrements 100 %), Visual/a11y, Lastziele, Security-Report.
3. Demo-Video der Kern-Flows (`--video on`) und Abnahmebericht `docs/acceptance/<In>.md`; fachliche Abnahme durch den Auftraggeber.

**Testumfang**

- G5 `--inc I6`.

## 4.8 Inkrement I7

### WP-I7-101 – funk-cli: Self-Hosting-CLI, Backup/Restore, Betriebs-Commands

| Merkmal | Wert |
|---|---|
| Inkrement | I7 |
| Typ (DoD 15 §3.15.3) | B – Backend-only |
| Größe | L |
| parallelisierbar | ja |
| Abhängigkeiten | WP-I6-999 |
| CE-IDs | CE-OPS-001, CE-OPS-002, CE-OPS-020 |

**Ziel.** `funk-cli` mit `install`, `init`, `config check`, `migrate`, `seed`, `backup`, `restore [--include-secrets]`, `test-email`, `clear-cache`, `reset-instance-admin-mapping`, `identities relink`, `realtime …`; Backup = `pg_dump` + Objektspeicher + Key-Ring.

**Enthaltene CE-IDs**

| CE-ID | Feature | Status (15 Anh. B) | Inkrement laut 15 | Pflicht-Ebenen | Testprojekt | E2E-Spec |
|---|---|---|---|---|---|---|
| CE-OPS-001 | Self-Hosting-CLI | angepasst | I7 | L3 L6 | Funk.Cli.Tests, tests/deploy | – |
| CE-OPS-002 | Daten-Restore | angepasst | I7 | L3 L6 | Funk.Cli.Tests, tests/deploy | – |
| CE-OPS-020 | Betriebs-CLI (Management-Commands) | übernommen | I7 | L3 | Funk.Cli.Tests | – |

**Betroffene Module/Libs in `funk.`**

- Backend: `src/tools/Funk.Cli`
- Backend: `tests/Funk.Cli.Tests`
- Backend: `tests/deploy/`

**Referenzdokumente**

- Architektur: 14 §3.11.3, §3.16, §3.22
- Architektur: 05 §4.6
- Architektur: 07 §3.8.4
- Analyse/Feature: `analysis/01-gesamtarchitektur-infrastruktur.md` §2.26
- Analyse/Feature: `analysis/02a-datenmodell-kern.md` §2.8
- Feature-Katalog: `features/10-ce-feature-katalog.md` (Einträge CE-OPS-001, CE-OPS-002, CE-OPS-020)

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- Backend: `deployments/cli/community/install.sh`, `deployments/cli/community/docker-compose.yml`, `deployments/cli/community/variables.env`, `deployments/cli/community/README.md`, `deployments/cli/community/restore.sh`, `deployments/cli/community/restore-airgapped.sh`, `apps/api/plane/db/management/commands/`, `apps/api/plane/license/management/commands/`, `apps/api/bin/docker-entrypoint-api.sh`
- `deployments/cli/community/install.sh`
- `apps/api/plane/db/management/commands/`

**Akzeptanzkriterien**

1. Backup/Restore-Test (G6): Restore auf leerer Instanz reproduziert Daten, Dateien und Login-Fähigkeit.
2. Contract-Szenarien mit Original-Golden für alle HTTP-Endpunkte dieses Pakets; Replay grün.
3. Job-/Consumer-Tests: Idempotenz (Inbox), Retry/Backoff, Zeitsteuerung mit `FixedClock`; neue Ereignistypen im Event-Katalog-Snapshot.
4. Bei Cron-Jobs: Registrierung in `CronRegistrationTests` mit Original-Zeit (UTC).
5. `ce-coverage-check --ids CE-OPS-001,CE-OPS-002,CE-OPS-020` grün (Mindestebenen 15 Anhang B).

**Testumfang**

- Pflicht-Ebenen (aus 15 Anhang B): L3, L6
- Testprojekte: `Funk.Cli.Tests`, `tests/deploy`

### WP-I7-102 – Docker Compose (Aspire-Publisher) und Docker-Swarm-Deployment

| Merkmal | Wert |
|---|---|
| Inkrement | I7 |
| Typ (DoD 15 §3.15.3) | I – Infrastruktur/Baustein |
| Größe | M |
| parallelisierbar | ja |
| Abhängigkeiten | WP-I6-999 |
| CE-IDs | CE-OPS-003 |

**Ziel.** Generierte `deploy/compose/docker-compose.yaml` mit Profilen (`bundled-s3`, `forgejo`, `valkey`, `acme`, `observability`, `tools`), Swarm-Kompatibilität und Smoke-Test.

**Enthaltene CE-IDs**

| CE-ID | Feature | Status (15 Anh. B) | Inkrement laut 15 | Pflicht-Ebenen | Testprojekt | E2E-Spec |
|---|---|---|---|---|---|---|
| CE-OPS-003 | Docker-Swarm-Deployment | angepasst | I7 | L6 | tests/deploy | – |

**Betroffene Module/Libs in `funk.`**

- Backend: `deploy/compose/`
- Backend: `tests/deploy/compose/`

**Referenzdokumente**

- Architektur: 14 §3.11
- Analyse/Feature: `analysis/01-gesamtarchitektur-infrastruktur.md` §2.26
- Feature-Katalog: `features/10-ce-feature-katalog.md` (Einträge CE-OPS-003)

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- Backend: `deployments/swarm/community/swarm.sh`

**Akzeptanzkriterien**

1. Compose- und Swarm-Smoke grün; Compose-Drift-Gate leer.
2. Unit-Tests ≥ 90 % Zeilen; Architekturtest für jede neue Regel; AppHost-Test, falls Topologie betroffen.
3. Kurzreferenz in `docs/` des Repos `funk.`.
4. `ce-coverage-check --ids CE-OPS-003` grün (Mindestebenen 15 Anhang B).

**Testumfang**

- Pflicht-Ebenen (aus 15 Anhang B): L6
- Testprojekte: `tests/deploy`

### WP-I7-103 – All-in-One-Container funk-aio

| Merkmal | Wert |
|---|---|
| Inkrement | I7 |
| Typ (DoD 15 §3.15.3) | I – Infrastruktur/Baustein |
| Größe | M |
| parallelisierbar | ja |
| Abhängigkeiten | WP-I6-999 |
| CE-IDs | CE-OPS-004 |

**Ziel.** `Funk.AllInOne` (Gateway+Api+Realtime+Worker in einem Prozess, In-Memory-Backplane) und Image `funk-aio` mit generierter `docker-compose.aio.yaml`.

**Enthaltene CE-IDs**

| CE-ID | Feature | Status (15 Anh. B) | Inkrement laut 15 | Pflicht-Ebenen | Testprojekt | E2E-Spec |
|---|---|---|---|---|---|---|
| CE-OPS-004 | All-in-One-Container | angepasst | I7 | L6 | tests/deploy | – |

**Betroffene Module/Libs in `funk.`**

- Backend: `src/hosts/Funk.AllInOne`

**Referenzdokumente**

- Architektur: 14 §3.13
- Architektur: 07 §1.4 Zeile I7
- Architektur: 17 ABG-019
- Analyse/Feature: `analysis/01-gesamtarchitektur-infrastruktur.md` §2.26
- Feature-Katalog: `features/10-ce-feature-katalog.md` (Einträge CE-OPS-004)

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- Backend: `deployments/aio/community/Dockerfile`, `deployments/aio/community/start.sh`, `deployments/aio/community/supervisor.conf`, `deployments/aio/community/build.sh`, `apps/proxy/Caddyfile.aio.ce`

**Akzeptanzkriterien**

1. Unit-Tests ≥ 90 % Zeilen; Architekturtest für jede neue Regel; AppHost-Test, falls Topologie betroffen.
2. Kurzreferenz in `docs/` des Repos `funk.`.
3. `ce-coverage-check --ids CE-OPS-004` grün (Mindestebenen 15 Anhang B).

**Testumfang**

- Pflicht-Ebenen (aus 15 Anhang B): L6
- Testprojekte: `tests/deploy`

### WP-I7-104 – Read-Replica-Unterstützung

| Merkmal | Wert |
|---|---|
| Inkrement | I7 |
| Typ (DoD 15 §3.15.3) | B – Backend-only |
| Größe | S |
| parallelisierbar | ja |
| Abhängigkeiten | WP-I6-999 |
| CE-IDs | CE-OPS-010 |

**Ziel.** Zweite Verbindung für lesende Endpunkte mit `read_replica: true` laut Endpunktkatalog.

**Enthaltene CE-IDs**

| CE-ID | Feature | Status (15 Anh. B) | Inkrement laut 15 | Pflicht-Ebenen | Testprojekt | E2E-Spec |
|---|---|---|---|---|---|---|
| CE-OPS-010 | Read-Replica-Unterstützung | übernommen | I7 | L1 L3 | Funk.BuildingBlocks.Tests | – |

**Betroffene Module/Libs in `funk.`**

- Backend: `src/building-blocks/Funk.BuildingBlocks.Persistence/ReadReplica/`

**Referenzdokumente**

- Architektur: 04 §4 (Spalte `read_replica`)
- Architektur: 14 §3.18
- Analyse/Feature: `analysis/01-gesamtarchitektur-infrastruktur.md` §2.13
- Feature-Katalog: `features/10-ce-feature-katalog.md` (Einträge CE-OPS-010)

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- Backend: `apps/api/plane/middleware/db_routing.py`, `apps/api/plane/utils/core/dbrouters.py`, `apps/api/plane/utils/core/request_scope.py`, `apps/api/plane/settings/common.py`

**Akzeptanzkriterien**

1. Contract-Szenarien mit Original-Golden für alle HTTP-Endpunkte dieses Pakets; Replay grün.
2. Job-/Consumer-Tests: Idempotenz (Inbox), Retry/Backoff, Zeitsteuerung mit `FixedClock`; neue Ereignistypen im Event-Katalog-Snapshot.
3. Bei Cron-Jobs: Registrierung in `CronRegistrationTests` mit Original-Zeit (UTC).
4. `ce-coverage-check --ids CE-OPS-010` grün (Mindestebenen 15 Anhang B).

**Testumfang**

- Pflicht-Ebenen (aus 15 Anhang B): L1, L3
- Testprojekte: `Funk.BuildingBlocks.Tests`

### WP-I7-105 – TLS-Modi und Reverse-Proxy mit automatischem HTTPS (ACME)

| Merkmal | Wert |
|---|---|
| Inkrement | I7 |
| Typ (DoD 15 §3.15.3) | I – Infrastruktur/Baustein |
| Größe | M |
| parallelisierbar | ja |
| Abhängigkeiten | WP-I6-999 |
| CE-IDs | CE-OPS-005 |

**Ziel.** TLS-Modi des Gateways (aus, eigenes Zertifikat, ACME) und Compose-Profil `acme`; Zertifikatspflicht für Data Protection in Produktion.

> **Hinweis:** Abweichung von 15 Anhang B (I0): Das Gateway-Grundrouting ist I0 (WP-I0-103), automatisches HTTPS gehört nach 14 §3.1.2 zu I7 (plan/04 OP-PLAN-03).

**Enthaltene CE-IDs**

| CE-ID | Feature | Status (15 Anh. B) | Inkrement laut 15 | Pflicht-Ebenen | Testprojekt | E2E-Spec |
|---|---|---|---|---|---|---|
| CE-OPS-005 | Reverse-Proxy mit automatischem HTTPS | übernommen | I0 | L1 L2 L3 L6 L7 | Funk.Gateway.Tests | `ops/deployment-smoke.spec.ts` |

**Betroffene Module/Libs in `funk.`**

- Backend: `src/hosts/Funk.Gateway` (TLS)
- Backend: `deploy/compose/` (Profil acme)

**Referenzdokumente**

- Architektur: 14 §3.8
- Analyse/Feature: `analysis/01-gesamtarchitektur-infrastruktur.md` §2.8
- Feature-Katalog: `features/10-ce-feature-katalog.md` (Einträge CE-OPS-005)

**Original-Pfade** (Referenzstand `funk-referenz-1.4.2`)

- Backend: `apps/proxy/Caddyfile.ce`, `apps/proxy/Dockerfile.ce`

**Akzeptanzkriterien**

1. Unit-Tests ≥ 90 % Zeilen; Architekturtest für jede neue Regel; AppHost-Test, falls Topologie betroffen.
2. Kurzreferenz in `docs/` des Repos `funk.`.
3. `ce-coverage-check --ids CE-OPS-005` grün (Mindestebenen 15 Anhang B).

**Testumfang**

- Pflicht-Ebenen (aus 15 Anhang B): L1, L2, L3, L6, L7
- Testprojekte: `Funk.Gateway.Tests`
- E2E-Specs (`frontend/apps/e2e/`): `ops/deployment-smoke.spec.ts`

### WP-I7-106 – Helm-Chart deploy/helm/funk

| Merkmal | Wert |
|---|---|
| Inkrement | I7 |
| Typ (DoD 15 §3.15.3) | I – Infrastruktur/Baustein |
| Größe | M |
| parallelisierbar | ja |
| Abhängigkeiten | WP-I6-999 |
| CE-IDs | – (keine; Baustein/Spike/Abnahme) |

**Ziel.** Helm-Chart mit allen Diensten, Keycloak (Deployment für Einzelknoten, Operator-Hinweis für HA), Secrets und `NOTES.txt` (G-BRAND).

**Betroffene Module/Libs in `funk.`**

- Backend: `deploy/helm/funk/`

**Referenzdokumente**

- Architektur: 14 §3.12, O-14-08

**Akzeptanzkriterien**

1. `helm lint`, `helm template | kubeconform` und Kind-Smoke grün.
2. Unit-Tests ≥ 90 % Zeilen; Architekturtest für jede neue Regel; AppHost-Test, falls Topologie betroffen.
3. Kurzreferenz in `docs/` des Repos `funk.`.

**Testumfang**

- L1 ≥ 90 % Zeilen, Architekturtest je neuer Regel, AppHost-Test bei Topologie-Änderung.

### WP-I7-107 – Airgapped-Bundle und Egress-gesperrter E2E-Lauf

| Merkmal | Wert |
|---|---|
| Inkrement | I7 |
| Typ (DoD 15 §3.15.3) | I – Infrastruktur/Baustein |
| Größe | M |
| parallelisierbar | ja |
| Abhängigkeiten | WP-I6-999 |
| CE-IDs | – (keine; Baustein/Spike/Abnahme) |

**Ziel.** `funk-airgap-<version>-<arch>.tar.zst` mit vollständiger Image-Liste (inkl. Forgejo, Keycloak), Prüfliste „keine externen Calls“ und E2E-Lauf mit gesperrtem Egress in CI.

**Betroffene Module/Libs in `funk.`**

- Backend: `deploy/airgap/`

**Referenzdokumente**

- Architektur: 14 §3.14
- Architektur: 00 ADR-004
- Architektur: 01 P6

**Akzeptanzkriterien**

1. Airgap-E2E grün, CSP-Report leer, keine DNS-Anfragen nach außen.
2. Unit-Tests ≥ 90 % Zeilen; Architekturtest für jede neue Regel; AppHost-Test, falls Topologie betroffen.
3. Kurzreferenz in `docs/` des Repos `funk.`.

**Testumfang**

- L1 ≥ 90 % Zeilen, Architekturtest je neuer Regel, AppHost-Test bei Topologie-Änderung.

### WP-I7-108 – Sicherheitshärtung: CSP-Enforce, ZAP, Permission-Matrix 100 %, Upgrade-Pfad

| Merkmal | Wert |
|---|---|
| Inkrement | I7 |
| Typ (DoD 15 §3.15.3) | I – Infrastruktur/Baustein |
| Größe | M |
| parallelisierbar | ja |
| Abhängigkeiten | WP-I6-999 |
| CE-IDs | – (keine; Baustein/Spike/Abnahme) |

**Ziel.** CSP von Report-Only auf Enforce (Z-108), ZAP-API-Scan, Permission-Matrix für 100 % der Endpunkte, Upgrade-Test (Migrator auf Dump der Vorversion), Image-Signaturen.

**Betroffene Module/Libs in `funk.`**

- Backend: `tests/security/`
- Backend: `.github/workflows/images.yml` (cosign)

**Referenzdokumente**

- Architektur: 05 §3.17.7, R-12
- Architektur: 15 §3.13
- Architektur: 14 §3.17, §3.21

**Akzeptanzkriterien**

1. 0 ungenehmigte Matrix-Abweichungen; keine Critical/High-CVE mit verfügbarem Fix.
2. Unit-Tests ≥ 90 % Zeilen; Architekturtest für jede neue Regel; AppHost-Test, falls Topologie betroffen.
3. Kurzreferenz in `docs/` des Repos `funk.`.

**Testumfang**

- L1 ≥ 90 % Zeilen, Architekturtest je neuer Regel, AppHost-Test bei Topologie-Änderung.

### WP-I7-109 – Last-, Soak- und Performance-Abnahme (LT-08, LT-13, LT-21, Worker-Kill-Tests)

| Merkmal | Wert |
|---|---|
| Inkrement | I7 |
| Typ (DoD 15 §3.15.3) | I – Infrastruktur/Baustein |
| Größe | M |
| parallelisierbar | ja |
| Abhängigkeiten | WP-I6-999 |
| CE-IDs | – (keine; Baustein/Spike/Abnahme) |

**Ziel.** Restliche Lastziele aus `tests/load/thresholds.yaml` sowie Worker-Ausfalltests (LT-12) und Revalidierungslast auf Keycloak (LT-13).

**Betroffene Module/Libs in `funk.`**

- Backend: `tests/load/`

**Referenzdokumente**

- Architektur: 15 §3.12
- Architektur: 06 §1.3 Zeile I7
- Architektur: 05 R-06

**Akzeptanzkriterien**

1. Unit-Tests ≥ 90 % Zeilen; Architekturtest für jede neue Regel; AppHost-Test, falls Topologie betroffen.
2. Kurzreferenz in `docs/` des Repos `funk.`.

**Testumfang**

- L1 ≥ 90 % Zeilen, Architekturtest je neuer Regel, AppHost-Test bei Topologie-Änderung.

### WP-I7-110 – Paritäts-Gesamtabnahme aller Screens, Endpunkt-Abdeckung 100 %, Abweichungsliste

| Merkmal | Wert |
|---|---|
| Inkrement | I7 |
| Typ (DoD 15 §3.15.3) | I – Infrastruktur/Baustein |
| Größe | M |
| parallelisierbar | nein |
| Abhängigkeiten | WP-I6-999, WP-I7-107, WP-I7-108 |
| CE-IDs | – (keine; Baustein/Spike/Abnahme) |

**Ziel.** Visual-/DOM-Abnahme aller Einträge des Screenshot-Katalogs (09 §4.14), `coverage --fail-under 100` für Endpunkte, konsolidierte Abweichungsliste (`deviations.yaml`, `ui-deviations.yaml`, `BRAND-*`) zur Abnahme durch den Auftraggeber.

**Referenzdokumente**

- Architektur: 15 §3.10, §3.16 Zeile I7
- Architektur: 09 §3.14.8
- Architektur: 04 §4.29

**Akzeptanzkriterien**

1. Unit-Tests ≥ 90 % Zeilen; Architekturtest für jede neue Regel; AppHost-Test, falls Topologie betroffen.
2. Kurzreferenz in `docs/` des Repos `funk.`.

**Testumfang**

- L1 ≥ 90 % Zeilen, Architekturtest je neuer Regel, AppHost-Test bei Topologie-Änderung.

### WP-I7-201 – Erweiterungspunkte stabilisieren: Contract-Snapshots aller Erweiterungs-Interfaces, Airgap-Test mit Forgejo

| Merkmal | Wert |
|---|---|
| Inkrement | I7 |
| Typ (DoD 15 §3.15.3) | X – Erweiterungspunkt 🧱 |
| Größe | S |
| parallelisierbar | ja |
| Abhängigkeiten | WP-I6-999 |
| CE-IDs | – (keine; Erweiterungspunkt) |
| Andockstelle | 16 §1.4 Zeile I7; 16 §4.6 (Träger CE-OPS-023) |

**Ziel.** C#-Snapshot per `PublicApiGenerator` + Verify (`ExtensionContractsSnapshotTests`), TS-Snapshot per `api-extractor` von `libs/web/extensions/public-api.ts`, Airgap-Lauf mit gebündeltem Forgejo.

**Betroffene Module/Libs in `funk.`**

- Backend: `tests/Funk.ArchitectureTests/ExtensionContractsSnapshotTests.cs`
- Frontend: `frontend/libs/web/extensions/api-report.md`

**Referenzdokumente**

- Architektur: 16 D16-ADR-07, §1.4 Zeile I7, §7

**Akzeptanzkriterien**

1. Jede nicht additive Änderung an einem Erweiterungs-Interface bricht den Snapshot-Test.
2. Contract (Interface/Schema/Token) + CE-Default-Implementierung; Eintrag in `tests/extension-points.yaml`.
3. Test „CE-Default = Original-Verhalten“ (Contract-Replay unverändert grün).
4. Test mit Fake-Erweiterung aus `Funk.BuildingBlocks.Testing/Extensions` bzw. `provideFakeExtensions()` beweist Erweiterbarkeit ohne CE-Änderung (DoD Typ X).

**Testumfang**

- Typ-X-Tests (CE-Default unverändert, Fake-Erweiterung wirkt ohne CE-Änderung), L0-Inventarabgleich `ExtensionPointInventoryTests`/`extension-registry-check`.

### WP-I7-999 – Abnahme I7 – CE-Release-Kandidat (G5 + G6)

| Merkmal | Wert |
|---|---|
| Inkrement | I7 |
| Typ (DoD 15 §3.15.3) | A – Inkrement-Abnahme |
| Größe | S |
| parallelisierbar | nein |
| Abhängigkeiten | WP-I7-101, WP-I7-102, WP-I7-103, WP-I7-104, WP-I7-105, WP-I7-106, WP-I7-107, WP-I7-108, WP-I7-109, WP-I7-110, WP-I7-201 |
| CE-IDs | – (keine; Baustein/Spike/Abnahme) |

**Ziel.** Inkrement-Abnahme I7 und Release-Gate G6 – Meilenstein M7 (CE-Release).

**Referenzdokumente**

- Architektur: plan/01-roadmap-ce.md §4 (M7)
- Architektur: 15 §3.15.1 (G6)

**Akzeptanzkriterien**

1. Alle Abnahmekriterien M7 erfüllt; `docs/acceptance/I7.md` und Release-Bericht generiert.
2. G5 `--inc <In> --strict` grün: `ce-coverage-check`, `original-test-ledger`, Parity-Report (0 ungenehmigte Abweichungen, Endpunkt-Abdeckung des Inkrements 100 %), Visual/a11y, Lastziele, Security-Report.
3. Demo-Video der Kern-Flows (`--video on`) und Abnahmebericht `docs/acceptance/<In>.md`; fachliche Abnahme durch den Auftraggeber.

**Testumfang**

- G5 `--inc I7`, G6.

## Anhang A – Zuordnung CE-ID → Arbeitspaket (vollständig, 507 Einträge)

| CE-ID | Feature | WP | Inkrement WP | Inkrement laut 15 Anh. B | Status |
|---|---|---|---|---|---|
| CE-WS-001 | Workspace anlegen | WP-I0-002 | I0 | I0/I1 | übernommen |
| CE-WS-002 | Demo-Inhalte bei Workspace-Anlage (Seed) | WP-I4-009 | I4 | I0/I1 | übernommen |
| CE-WS-003 | Workspace-Einstellungen General | WP-I1-001 | I1 | I1 | übernommen |
| CE-WS-004 | Workspace löschen | WP-I1-001 | I1 | I1 | übernommen |
| CE-WS-005 | Workspace-Switcher und Workspace-Liste | WP-I0-004 | I0 | I0/I1 | übernommen |
| CE-WS-006 | Workspace-weite Stammdatenlisten | WP-I1-001 | I1 | I1 | übernommen |
| CE-WS-007 | Workspace-Themes (nur API) | WP-I1-001 | I1 | I1 | übernommen |
| CE-WS-008 | Rollen- und Berechtigungsmodell (Admin/Member/Guest) | WP-I1-002 | I1 | I1 | übernommen |
| CE-WS-009 | Workspace-Mitgliederverwaltung | WP-I1-002 | I1 | I1 | übernommen |
| CE-WS-010 | Mitglieder einladen und Einladungen verwalten | WP-I1-002 | I1 | I1 | übernommen |
| CE-WS-011 | Einladungen annehmen oder ablehnen | WP-I1-002 | I1 | I1 | übernommen |
| CE-WS-012 | Eigene Mitgliedschaft und Rollen-Maps | WP-I1-002 | I1 | I1 | übernommen |
| CE-WS-013 | Workspace-Shell und Top-Navigation | WP-I0-004 | I0 | I0/I1 | übernommen |
| CE-WS-014 | Hilfe-Menü | WP-I1-003 | I1 | I0/I1 | übernommen |
| CE-WS-015 | What's new? (Produkt-Changelog) | WP-I1-003 | I1 | I0/I1 | übernommen |
| CE-WS-016 | User-Menü | WP-I0-004 | I0 | I0/I1 | übernommen |
| CE-WS-017 | Star-us-on-GitHub-Link | WP-I1-003 | I1 | I0/I1 | übernommen |
| CE-WS-018 | Resizable App-Sidebar mit Peek | WP-I0-004 | I0 | I0/I1 | übernommen |
| CE-WS-019 | Sidebar-Kopf und Quick-Action 'New work item' | WP-I0-004 | I0 | I0/I1 | übernommen |
| CE-WS-020 | Sidebar-Menüeinträge | WP-I0-004 | I0 | I0/I1 | übernommen |
| CE-WS-021 | Erweiterte Sidebar 'More' mit Pin und Sortierung | WP-I1-003 | I1 | I1 | übernommen |
| CE-WS-022 | Customize navigation | WP-I1-003 | I1 | I1 | übernommen |
| CE-WS-023 | Favoriten mit Ordnern | WP-I1-004 | I1 | I1 | übernommen |
| CE-WS-024 | Workspace-Settings-Rahmen | WP-I1-001 | I1 | I1 | übernommen |
| CE-PRJ-001 | Projektliste | WP-I1-005 | I1 | I1 | übernommen |
| CE-PRJ-002 | Projektkarte | WP-I1-005 | I1 | I1 | übernommen |
| CE-PRJ-003 | Projekt-Statistiken | WP-I1-005 | I1 | I1 | übernommen |
| CE-PRJ-004 | Projekt anlegen | WP-I0-005 | I0 | I0/I1 | übernommen |
| CE-PRJ-005 | Projekt-Identifier prüfen und freigeben | WP-I0-005 | I0 | I0/I1 | übernommen |
| CE-PRJ-006 | Projekt-Detail und Zugriffsschutz | WP-I1-006 | I1 | I1 | übernommen |
| CE-PRJ-007 | Projekt beitreten und verlassen | WP-I1-006 | I1 | I1 | übernommen |
| CE-PRJ-008 | Projekt archivieren und wiederherstellen | WP-I1-007 | I1 | I1 | übernommen |
| CE-PRJ-009 | Projekt löschen | WP-I1-007 | I1 | I1 | übernommen |
| CE-PRJ-010 | Projekt-Einladungen per E-Mail (defekt, nur API) | WP-I1-006 | I1 | I1 | übernommen |
| CE-PRJ-011 | Projektliste in der Sidebar | WP-I1-008 | I1 | I1 | übernommen |
| CE-PRJ-012 | Projekt-Kontextmenü in der Sidebar | WP-I1-008 | I1 | I1 | übernommen |
| CE-PRJ-013 | Erweiterte Projekt-Sidebar | WP-I1-008 | I1 | I1 | übernommen |
| CE-PRJ-014 | Projekt-Feature-Navigation | WP-I1-008 | I1 | I1 | übernommen |
| CE-PRJ-015 | Tab-Navigation (TABBED) | WP-I1-008 | I1 | I1 | übernommen |
| CE-PRJ-016 | Projekt-Benutzerpräferenzen | WP-I1-009 | I1 | I1 | übernommen |
| CE-PRJ-017 | Projekt-Settings-Rahmen | WP-I1-009 | I1 | I1 | übernommen |
| CE-PRJ-018 | Projekt-Einstellungen General | WP-I1-009 | I1 | I1 | übernommen |
| CE-PRJ-019 | Projekt-Feature-Toggles | WP-I1-010 | I1 | I1 | übernommen |
| CE-PRJ-020 | Disabled-Feature-Zustände | WP-I1-010 | I1 | I1 | übernommen |
| CE-PRJ-021 | Projektmitglieder verwalten | WP-I1-010 | I1 | I1 | übernommen |
| CE-PRJ-022 | Gastzugriff auf Projektinhalte (guest_view_all_features) | WP-I1-010 | I1 | I1 | übernommen |
| CE-PRJ-023 | State-Gruppen und Default-States | WP-I1-011 | I1 | I1 | übernommen |
| CE-PRJ-024 | State anlegen und bearbeiten | WP-I1-011 | I1 | I1 | übernommen |
| CE-PRJ-025 | State-Reihenfolge per Drag&Drop | WP-I1-011 | I1 | I1 | übernommen |
| CE-PRJ-026 | Default-State festlegen | WP-I1-011 | I1 | I1 | übernommen |
| CE-PRJ-027 | State löschen | WP-I1-011 | I1 | I1 | übernommen |
| CE-PRJ-028 | Label-Liste mit Hierarchie | WP-I1-012 | I1 | I1 | übernommen |
| CE-PRJ-029 | Label anlegen und bearbeiten | WP-I1-012 | I1 | I1 | übernommen |
| CE-PRJ-030 | Labels per Drag&Drop ordnen und gruppieren | WP-I1-012 | I1 | I1 | übernommen |
| CE-PRJ-031 | Label aus Gruppe entfernen | WP-I1-012 | I1 | I1 | übernommen |
| CE-PRJ-032 | Label löschen | WP-I1-012 | I1 | I1 | übernommen |
| CE-PRJ-033 | Labels per Bulk-Import (nur API) | WP-I1-012 | I1 | I1 | übernommen |
| CE-PRJ-034 | Estimates-Einstellungen | WP-I1-013 | I1 | I1 | übernommen |
| CE-PRJ-035 | Schätzsystem anlegen | WP-I1-013 | I1 | I1 | übernommen |
| CE-PRJ-036 | Schätzwert-Validierung | WP-I1-013 | I1 | I1 | übernommen |
| CE-PRJ-037 | Schätzpunkte ändern und löschen (Backend) | WP-I1-013 | I1 | I1 | übernommen |
| CE-PRJ-038 | Schätzsystem löschen | WP-I1-013 | I1 | I1 | übernommen |
| CE-PRJ-039 | Auto-Archive | WP-I3-013 | I3 | I3 | übernommen |
| CE-PRJ-040 | Auto-Close | WP-I3-013 | I3 | I3 | übernommen |
| CE-WI-001 | Work Item anlegen (Modal) | WP-I2-001 | I2 | I2 | übernommen |
| CE-WI-002 | Fortlaufende Work-Item-ID (PROJ-123) | WP-I2-001 | I2 | I2 | übernommen |
| CE-WI-003 | Work Item bearbeiten | WP-I2-001 | I2 | I2 | übernommen |
| CE-WI-004 | Titel-Bearbeitung mit Autosave | WP-I2-001 | I2 | I2 | übernommen |
| CE-WI-005 | Beschreibungsfeld mit Autosave | WP-I2-001 | I2 | I2 | übernommen |
| CE-WI-006 | Toast-Aktionen nach dem Erstellen | WP-I2-001 | I2 | I2 | übernommen |
| CE-WI-007 | Draft-Rückfrage beim Schließen | WP-I2-001 | I2 | I2 | übernommen |
| CE-WI-008 | Bestehende Work Items hinzufügen (Dialog) | WP-I2-001 | I2 | I2 | übernommen |
| CE-WI-009 | Work-Item-Detailseite per Identifier | WP-I2-002 | I2 | I2 | übernommen |
| CE-WI-010 | Work-Item-Detaildaten | WP-I2-002 | I2 | I2 | übernommen |
| CE-WI-011 | Work-Item-Meta und Mehrfachabruf | WP-I2-002 | I2 | I2 | übernommen |
| CE-WI-012 | Delta-Sync für den Client-Cache | WP-I2-002 | I2 | I2 | übernommen |
| CE-WI-013 | Identifier mit Klick-zum-Kopieren | WP-I2-002 | I2 | I2 | übernommen |
| CE-WI-014 | Detail-Kopfaktionen | WP-I2-002 | I2 | I2 | übernommen |
| CE-WI-015 | Peek-Overview mit drei Modi | WP-I2-003 | I2 | I2 | übernommen |
| CE-WI-016 | Peek-Inhalt | WP-I2-003 | I2 | I2 | übernommen |
| CE-WI-017 | Peek schließen per Outside-Click/Escape | WP-I2-003 | I2 | I2 | übernommen |
| CE-WI-018 | Peek-Fehler- und Ladezustand | WP-I2-003 | I2 | I2 | übernommen |
| CE-WI-019 | Hover-Vorschaukarte | WP-I2-003 | I2 | I2 | übernommen |
| CE-WI-020 | Sidebar-Properties | WP-I2-004 | I2 | I2 | übernommen |
| CE-WI-021 | State-Dropdown | WP-I2-004 | I2 | I2 | übernommen |
| CE-WI-022 | Prioritäten und Priority-Dropdown | WP-I2-004 | I2 | I2 | übernommen |
| CE-WI-023 | Member-Dropdown (Assignees) | WP-I2-004 | I2 | I2 | übernommen |
| CE-WI-024 | Label-Dropdown mit Anlage | WP-I2-004 | I2 | I2 | übernommen |
| CE-WI-025 | Cycle-Dropdown | WP-I3-007 | I3 | I2 | übernommen |
| CE-WI-026 | Module-Dropdown | WP-I3-010 | I3 | I2 | übernommen |
| CE-WI-027 | Estimate-Dropdown | WP-I2-004 | I2 | I2 | übernommen |
| CE-WI-028 | Projekt-Dropdown | WP-I2-004 | I2 | I2 | übernommen |
| CE-WI-029 | Datums- und Datumsbereichsauswahl | WP-I2-004 | I2 | I2 | übernommen |
| CE-WI-030 | Read-only-Label-Anzeige | WP-I2-004 | I2 | I2 | übernommen |
| CE-WI-031 | Parent setzen, ändern, entfernen | WP-I2-005 | I2 | I2 | übernommen |
| CE-WI-032 | Sub-Work-Items | WP-I2-005 | I2 | I2 | übernommen |
| CE-WI-033 | Relationen zwischen Work Items | WP-I2-005 | I2 | I2 | übernommen |
| CE-WI-034 | Widget-Aktionsleiste | WP-I2-005 | I2 | I2 | übernommen |
| CE-WI-035 | Links an Work Items | WP-I2-006 | I2 | I2 | übernommen |
| CE-WI-036 | Anhänge an Work Items | WP-I2-006 | I2 | I2 | übernommen |
| CE-WI-037 | Kommentare | WP-I2-007 | I2 | I2 | übernommen |
| CE-WI-038 | Emoji-Reaktionen auf Work Items und Kommentare | WP-I2-007 | I2 | I2 | übernommen |
| CE-WI-039 | Aktivitätsverlauf | WP-I2-008 | I2 | I2 | übernommen |
| CE-WI-040 | Activity-Filter und -Sortierung | WP-I2-008 | I2 | I2 | übernommen |
| CE-WI-041 | Beschreibungs-Versionshistorie | WP-I2-008 | I2 | I2 | übernommen |
| CE-WI-042 | Eigenschafts-Historie (IssueVersion) | WP-I2-008 | I2 | I2 | übernommen |
| CE-WI-043 | Work Items abonnieren | WP-I2-008 | I2 | I2 | übernommen |
| CE-WI-044 | Erwähnungen (@Mentions) in Beschreibung und Kommentaren | WP-I2-007 | I2 | I2 | übernommen |
| CE-WI-045 | Work Items archivieren und wiederherstellen | WP-I2-009 | I2 | I2 | übernommen |
| CE-WI-046 | Bulk-Archivieren (Backend) | WP-I2-009 | I2 | I2 | übernommen |
| CE-WI-047 | Work Item löschen | WP-I2-009 | I2 | I2 | übernommen |
| CE-WI-048 | Mehrere Work Items löschen | WP-I2-009 | I2 | I2 | übernommen |
| CE-WI-049 | Workspace-Drafts | WP-I2-010 | I2 | I2 | übernommen |
| CE-LV-001 | Layout-Umschaltung | WP-I2-011 | I2 | I2 | übernommen |
| CE-LV-002 | Projekt-Work-Items-Seite und Kopf | WP-I2-011 | I2 | I2 | übernommen |
| CE-LV-003 | Layout-Kontextmenü im Kopf | WP-I2-011 | I2 | I2 | übernommen |
| CE-LV-004 | Layout-Kontexte Cycle, Modul, View, Archiv, Profil | WP-I3-001 | I3 | I2 | übernommen |
| CE-LV-005 | Work-Item-Liste mit Gruppierung und Paginierung (Backend) | WP-I2-012 | I2 | I2 | übernommen |
| CE-LV-006 | Rich-Filter-Ausdrücke (AND/OR/NOT) | WP-I2-012 | I2 | I2 | übernommen |
| CE-LV-007 | Rich-Filter-Zeile | WP-I2-012 | I2 | I2 | übernommen |
| CE-LV-008 | Filterwert-Eingaben | WP-I2-012 | I2 | I2 | übernommen |
| CE-LV-009 | Ungültige Filterbedingung | WP-I2-012 | I2 | I2 | übernommen |
| CE-LV-010 | Work-Item-Filterfelder | WP-I2-012 | I2 | I2 | übernommen |
| CE-LV-011 | View aus Filtern speichern oder aktualisieren | WP-I3-002 | I3 | I2 | übernommen |
| CE-LV-012 | Klassische Filter-Sektionen und Applied-Filter-Chips | WP-I2-013 | I2 | I2 | übernommen |
| CE-LV-013 | Display-Dropdown | WP-I2-013 | I2 | I2 | übernommen |
| CE-LV-014 | Anzeige-Einstellungen je Nutzer und Projekt | WP-I2-013 | I2 | I2 | übernommen |
| CE-LV-015 | Workspace-weite Filter- und Anzeigeeinstellungen | WP-I2-013 | I2 | I2 | übernommen |
| CE-LV-016 | Anzeige-Einstellungen je Cycle und Modul | WP-I3-006 | I3 | I2 | übernommen |
| CE-LV-017 | List-Layout mit Gruppierung | WP-I2-014 | I2 | I2 | übernommen |
| CE-LV-018 | List-Zeile mit Inline-Properties | WP-I2-014 | I2 | I2 | übernommen |
| CE-LV-019 | Sub-Work-Items in der Liste aufklappen | WP-I2-014 | I2 | I2 | übernommen |
| CE-LV-020 | Kanban-Board | WP-I2-015 | I2 | I2 | übernommen |
| CE-LV-021 | Kanban-Swimlanes | WP-I2-015 | I2 | I2 | übernommen |
| CE-LV-022 | Kanban-Karte | WP-I2-015 | I2 | I2 | übernommen |
| CE-LV-023 | Kanban-Löschzone | WP-I2-015 | I2 | I2 | übernommen |
| CE-LV-024 | Drag-and-Drop zwischen Gruppen und Reihenfolge | WP-I2-015 | I2 | I2 | übernommen |
| CE-LV-025 | Calendar-Layout Monat/Woche | WP-I2-016 | I2 | I2 | übernommen |
| CE-LV-026 | Calendar-Drag auf anderen Tag | WP-I2-016 | I2 | I2 | übernommen |
| CE-LV-027 | Calendar-Eintrag | WP-I2-016 | I2 | I2 | übernommen |
| CE-LV-028 | Calendar-Quick-Add je Tag | WP-I2-016 | I2 | I2 | übernommen |
| CE-LV-029 | Gantt/Timeline-Ansicht | WP-I2-017 | I2 | I2 | übernommen |
| CE-LV-030 | Gantt verschieben und Dauer ändern | WP-I2-017 | I2 | I2 | übernommen |
| CE-LV-031 | Gantt-Datum für Items ohne Datum setzen | WP-I2-017 | I2 | I2 | übernommen |
| CE-LV-032 | Gantt-Sidebar-Reorder | WP-I2-017 | I2 | I2 | übernommen |
| CE-LV-033 | Timeline-Daten mit Relationen (issues-detail) | WP-I2-017 | I2 | I2 | übernommen |
| CE-LV-034 | Spreadsheet-Tabelle | WP-I2-018 | I2 | I2 | übernommen |
| CE-LV-035 | Spreadsheet-Sortierung über den Spaltenkopf | WP-I2-018 | I2 | I2 | übernommen |
| CE-LV-036 | Spreadsheet-Tastaturnavigation und Mehrfachauswahl | WP-I2-018 | I2 | I2 | übernommen |
| CE-LV-037 | Sprung zu Sub-Work-Items aus dem Spreadsheet | WP-I2-018 | I2 | I2 | übernommen |
| CE-LV-038 | Inline-Property-Leiste | WP-I2-019 | I2 | I2 | übernommen |
| CE-LV-039 | Quick-Add je Layout | WP-I2-019 | I2 | I2 | übernommen |
| CE-LV-040 | Gruppen-'+' mit 'Create work item' / 'Add an existing work item' | WP-I2-019 | I2 | I2 | übernommen |
| CE-LV-041 | Quick-Action-Menü und Rechtsklick-Kontextmenü | WP-I2-019 | I2 | I2 | übernommen |
| CE-LV-042 | Empty-States der Layouts | WP-I2-020 | I2 | I2 | übernommen |
| CE-LV-043 | Skeleton-Loader je Layout | WP-I2-020 | I2 | I2 | übernommen |
| CE-LV-044 | Virtualisierung und Endlos-Laden | WP-I2-020 | I2 | I2 | übernommen |
| CE-LV-045 | Layout-Fehlergrenze | WP-I2-020 | I2 | I2 | übernommen |
| CE-LV-046 | Projekt-Archive (Kopf und Tabs) | WP-I3-001 | I3 | I3 | übernommen |
| CE-LV-047 | Projekt-View-Liste | WP-I3-002 | I3 | I3 | übernommen |
| CE-LV-048 | Projekt-View anlegen und bearbeiten | WP-I3-002 | I3 | I3 | übernommen |
| CE-LV-049 | Projekt-View löschen | WP-I3-002 | I3 | I3 | übernommen |
| CE-LV-050 | View-Kontextmenü und Favoriten | WP-I3-002 | I3 | I3 | übernommen |
| CE-LV-051 | Projekt-View-Detail | WP-I3-002 | I3 | I3 | übernommen |
| CE-LV-052 | Workspace-Views-Übersicht | WP-I3-003 | I3 | I3 | übernommen |
| CE-LV-053 | Workspace-View anlegen, bearbeiten, löschen | WP-I3-003 | I3 | I3 | übernommen |
| CE-LV-054 | Workspace-View-Detail (All work items) | WP-I3-003 | I3 | I3 | übernommen |
| CE-CYC-001 | Cycle-Liste mit Gruppen | WP-I3-004 | I3 | I3 | übernommen |
| CE-CYC-002 | Cycle-Suche und Filter | WP-I3-004 | I3 | I3 | übernommen |
| CE-CYC-003 | Inline-Dashboard des aktiven Cycles | WP-I3-004 | I3 | I3 | übernommen |
| CE-CYC-004 | Workspace-weite Active Cycles | WP-I3-004 | I3 | I3 | übernommen |
| CE-CYC-005 | Cycle anlegen und bearbeiten | WP-I3-005 | I3 | I3 | übernommen |
| CE-CYC-006 | Datumsüberschneidung prüfen | WP-I3-005 | I3 | I3 | übernommen |
| CE-CYC-007 | Cycle-Peek und Detail-Sidebar | WP-I3-006 | I3 | I3 | übernommen |
| CE-CYC-008 | Fortschritt, Verteilungen und Burndown | WP-I3-006 | I3 | I3 | übernommen |
| CE-CYC-009 | Cycle-Detailseite | WP-I3-006 | I3 | I3 | übernommen |
| CE-CYC-010 | Work Items einem Cycle zuordnen | WP-I3-007 | I3 | I3 | übernommen |
| CE-CYC-011 | Unvollständige Work Items übertragen | WP-I3-007 | I3 | I3 | übernommen |
| CE-CYC-012 | Cycle archivieren und wiederherstellen | WP-I3-005 | I3 | I3 | übernommen |
| CE-CYC-013 | Cycle löschen | WP-I3-005 | I3 | I3 | übernommen |
| CE-CYC-014 | Cycle-Kontextmenü | WP-I3-005 | I3 | I3 | übernommen |
| CE-CYC-015 | Cycle-Favoriten | WP-I3-005 | I3 | I3 | übernommen |
| CE-MOD-001 | Modul-Übersicht in drei Layouts | WP-I3-008 | I3 | I3 | übernommen |
| CE-MOD-002 | Modul-Suche, Filter und Sortierung | WP-I3-008 | I3 | I3 | übernommen |
| CE-MOD-003 | Modul anlegen und bearbeiten | WP-I3-009 | I3 | I3 | übernommen |
| CE-MOD-004 | Modul-Status | WP-I3-009 | I3 | I3 | übernommen |
| CE-MOD-005 | Modul-Links | WP-I3-009 | I3 | I3 | übernommen |
| CE-MOD-006 | Modul-Sidebar mit Lead, Mitgliedern und Fortschritt | WP-I3-009 | I3 | I3 | übernommen |
| CE-MOD-007 | Modul-Detailseite | WP-I3-010 | I3 | I3 | übernommen |
| CE-MOD-008 | Work Items Modulen zuordnen | WP-I3-010 | I3 | I3 | übernommen |
| CE-MOD-009 | Modul archivieren und wiederherstellen | WP-I3-009 | I3 | I3 | übernommen |
| CE-MOD-010 | Modul löschen | WP-I3-009 | I3 | I3 | übernommen |
| CE-MOD-011 | Modul-Kontextmenü und Favoriten | WP-I3-008 | I3 | I3 | übernommen |
| CE-INT-001 | Intake je Projekt und Triage-State | WP-I3-011 | I3 | I3 | übernommen |
| CE-INT-002 | Intake-Seite mit Tabs Open/Closed | WP-I3-011 | I3 | I3 | übernommen |
| CE-INT-003 | Intake-Filter und Sortierung | WP-I3-011 | I3 | I3 | übernommen |
| CE-INT-004 | Intake-Detail | WP-I3-011 | I3 | I3 | übernommen |
| CE-INT-005 | Intake-Eintrag anlegen | WP-I3-011 | I3 | I3 | übernommen |
| CE-INT-006 | Intake annehmen | WP-I3-012 | I3 | I3 | übernommen |
| CE-INT-007 | Intake ablehnen | WP-I3-012 | I3 | I3 | übernommen |
| CE-INT-008 | Intake zurückstellen (Snooze) | WP-I3-012 | I3 | I3 | übernommen |
| CE-INT-009 | Als Duplikat markieren | WP-I3-012 | I3 | I3 | übernommen |
| CE-INT-010 | Intake bearbeiten und löschen | WP-I3-012 | I3 | I3 | übernommen |
| CE-INT-011 | Intake-Navigation | WP-I3-012 | I3 | I3 | übernommen |
| CE-INT-012 | Intake-Detail in Benachrichtigungen | WP-I3-012 | I3 | I3 | übernommen |
| CE-PAGE-001 | Page-Liste mit Tabs | WP-I4-001 | I4 | I4 | übernommen |
| CE-PAGE-002 | Page-Suche, Filter und Sortierung | WP-I4-001 | I4 | I4 | übernommen |
| CE-PAGE-003 | Page anlegen | WP-I4-001 | I4 | I4 | übernommen |
| CE-PAGE-004 | Page-Daten und Detail | WP-I4-002 | I4 | I4 | übernommen |
| CE-PAGE-005 | Page sperren und entsperren | WP-I4-002 | I4 | I4 | übernommen |
| CE-PAGE-006 | Page-Zugriff öffentlich/privat | WP-I4-002 | I4 | I4 | übernommen |
| CE-PAGE-007 | Page archivieren und wiederherstellen | WP-I4-002 | I4 | I4 | übernommen |
| CE-PAGE-008 | Page löschen | WP-I4-002 | I4 | I4 | übernommen |
| CE-PAGE-009 | Page duplizieren | WP-I4-002 | I4 | I4 | übernommen |
| CE-PAGE-010 | Page favorisieren | WP-I4-001 | I4 | I4 | übernommen |
| CE-PAGE-011 | Page exportieren (PDF/Markdown) | WP-I4-003 | I4 | I4 | übernommen |
| CE-PAGE-012 | Referenzprotokoll der Inhalte (PageLog) | WP-I4-002 | I4 | I4 | übernommen |
| CE-PAGE-013 | Kollaborativer Page-Editor (Seite) | WP-I4-004 | I4 | I4 | übernommen |
| CE-PAGE-014 | Page-Toolbar | WP-I4-004 | I4 | I4 | übernommen |
| CE-PAGE-015 | Page-Kopf | WP-I4-004 | I4 | I4 | übernommen |
| CE-PAGE-016 | Outline | WP-I4-004 | I4 | I4 | übernommen |
| CE-PAGE-017 | Info-Panel | WP-I4-004 | I4 | I4 | übernommen |
| CE-PAGE-018 | Assets-Panel | WP-I4-004 | I4 | I4 | übernommen |
| CE-PAGE-019 | Versionshistorie | WP-I4-005 | I4 | I4 | übernommen |
| CE-PAGE-020 | Page-Anzeigeoptionen | WP-I4-004 | I4 | I4 | übernommen |
| CE-PAGE-021 | Rich-Text-Editor | WP-I2-022 | I2 | I2/I4 | übernommen |
| CE-PAGE-022 | Lite-Text-Editor | WP-I2-021 | I2 | I2/I4 | übernommen |
| CE-PAGE-023 | Dokument-Editor (read-only, Versionen) | WP-I2-024 | I2 | I2/I4 | übernommen |
| CE-PAGE-024 | Slash-Command-Menü | WP-I2-023 | I2 | I4 | übernommen |
| CE-PAGE-025 | Bubble-Menü | WP-I2-023 | I2 | I4 | übernommen |
| CE-PAGE-026 | Drag-Handle, Block-Menü und Block-Drag&Drop | WP-I2-023 | I2 | I4 | übernommen |
| CE-PAGE-027 | Textstruktur | WP-I2-022 | I2 | I4 | übernommen |
| CE-PAGE-028 | Listen (Aufzählung, Nummerierung, To-do) | WP-I2-022 | I2 | I4 | übernommen |
| CE-PAGE-029 | Text-Formatierung und Farben | WP-I2-022 | I2 | I4 | übernommen |
| CE-PAGE-030 | Code-Block mit Syntax-Highlighting | WP-I2-023 | I2 | I4 | übernommen |
| CE-PAGE-031 | Tabellen | WP-I2-023 | I2 | I4 | übernommen |
| CE-PAGE-032 | Bilder im Editor | WP-I2-023 | I2 | I4 | übernommen |
| CE-PAGE-033 | Callouts | WP-I2-023 | I2 | I4 | übernommen |
| CE-PAGE-034 | Nutzer-Mentions im Editor | WP-I2-021 | I2 | I2/I4 | übernommen |
| CE-PAGE-035 | Emojis | WP-I2-021 | I2 | I2/I4 | übernommen |
| CE-PAGE-036 | Links im Editor | WP-I2-021 | I2 | I2/I4 | übernommen |
| CE-PAGE-037 | Markdown-Funktionen | WP-I2-022 | I2 | I2/I4 | übernommen |
| CE-PAGE-038 | Platzhalter | WP-I2-022 | I2 | I2/I4 | übernommen |
| CE-PAGE-039 | Deep-Links zu Blöcken | WP-I2-022 | I2 | I4 | übernommen |
| CE-PAGE-040 | Anzeige-Konfiguration des Editors | WP-I2-022 | I2 | I4 | übernommen |
| CE-RT-001 | Realtime-Kollaborationsserver | WP-I4-006 | I4 | I4 | übernommen |
| CE-RT-002 | Echtzeit-Kollaboration und Offline-Cache (Client) | WP-I4-007 | I4 | I4 | übernommen |
| CE-RT-003 | REST-Fallback-Speicherung | WP-I4-007 | I4 | I4 | übernommen |
| CE-RT-004 | Echtzeit-Seitenereignisse | WP-I4-007 | I4 | I4 | übernommen |
| CE-RT-005 | Persistenz und Titel-Sync (Server) | WP-I4-006 | I4 | I4 | übernommen |
| CE-RT-006 | Fehler-Broadcast und Force-Close | WP-I4-006 | I4 | I4 | übernommen |
| CE-RT-007 | Horizontale Skalierung | WP-I4-008 | I4 | I4 | übernommen |
| CE-RT-008 | Dokument-Konvertierung | WP-I4-006 | I4 | I4 | übernommen |
| CE-RT-009 | Health-Endpunkt des Live-Servers | WP-I0-107 | I0 | I4 | übernommen |
| CE-ANA-001 | Workspace-Analytics mit Tabs | WP-I5-001 | I5 | I5 | übernommen |
| CE-ANA-002 | Analytics-Kennzahlen | WP-I5-001 | I5 | I5 | übernommen |
| CE-ANA-003 | Project Insights | WP-I5-001 | I5 | I5 | übernommen |
| CE-ANA-004 | Active Projects | WP-I5-001 | I5 | I5 | übernommen |
| CE-ANA-005 | Created vs Resolved | WP-I5-001 | I5 | I5 | übernommen |
| CE-ANA-006 | Customized Insights | WP-I5-001 | I5 | I5 | übernommen |
| CE-ANA-007 | Insight-Tabelle mit CSV-Export | WP-I5-001 | I5 | I5 | übernommen |
| CE-ANA-008 | Analytics-Panel für Projekt, Cycle und Modul | WP-I5-002 | I5 | I5 | übernommen |
| CE-ANA-009 | Legacy-Analytics, gespeicherte Analytics-Views und Export per E-Mail | WP-I5-002 | I5 | I5 | übernommen |
| CE-HOME-001 | Workspace-Home | WP-I5-003 | I5 | I5 | übernommen |
| CE-HOME-002 | Home-Widgets verwalten | WP-I5-003 | I5 | I5 | übernommen |
| CE-HOME-003 | Quickstart-Guide | WP-I5-003 | I5 | I5 | übernommen |
| CE-HOME-004 | Quick links | WP-I5-003 | I5 | I5 | übernommen |
| CE-HOME-005 | Recents (zuletzt besucht) | WP-I5-003 | I5 | I5 | übernommen |
| CE-HOME-006 | Produkt-Tour | WP-I5-003 | I5 | I5 | übernommen |
| CE-HOME-007 | Legacy-Dashboard und Aktivitätsgraphen (nur API) | WP-I5-003 | I5 | I5 | übernommen |
| CE-HOME-008 | Stickies-Widget | WP-I5-004 | I5 | I5 | übernommen |
| CE-HOME-009 | Stickies-Seite | WP-I5-004 | I5 | I5 | übernommen |
| CE-HOME-010 | Sticky bearbeiten | WP-I5-004 | I5 | I5 | übernommen |
| CE-NOTIF-001 | Erzeugung von In-App-Benachrichtigungen | WP-I5-005 | I5 | I5 | übernommen |
| CE-NOTIF-002 | Erwähnungs-Benachrichtigungen | WP-I5-005 | I5 | I5 | übernommen |
| CE-NOTIF-003 | Automatisches Abonnieren | WP-I5-005 | I5 | I5 | übernommen |
| CE-NOTIF-004 | Inbox-Seite und Benachrichtigungsliste | WP-I5-006 | I5 | I5 | übernommen |
| CE-NOTIF-005 | Inbox-Filter und -Optionen | WP-I5-006 | I5 | I5 | übernommen |
| CE-NOTIF-006 | Benachrichtigung lesen, archivieren, snoozen | WP-I5-006 | I5 | I5 | übernommen |
| CE-NOTIF-007 | Benachrichtigungs-Detail | WP-I5-006 | I5 | I5 | übernommen |
| CE-NOTIF-008 | E-Mail-Benachrichtigungen (5-Minuten-Bündelung) | WP-I5-007 | I5 | I5 | übernommen |
| CE-NOTIF-009 | E-Mail-Benachrichtigungseinstellungen | WP-I5-007 | I5 | I5 | übernommen |
| CE-SRCH-001 | Globale Suche | WP-I5-008 | I5 | I5 | übernommen |
| CE-SRCH-002 | Entity-Suche für Mentions und Picker | WP-I5-008 | I5 | I5 | übernommen |
| CE-SRCH-003 | Work-Item-Picker-Suche | WP-I5-008 | I5 | I5 | übernommen |
| CE-SRCH-004 | Power-K Command Palette | WP-I5-009 | I5 | I5 | übernommen |
| CE-SRCH-005 | Power-K-Navigationsbefehle | WP-I5-009 | I5 | I5 | übernommen |
| CE-SRCH-006 | Power-K-Erstellbefehle | WP-I5-009 | I5 | I5 | übernommen |
| CE-SRCH-007 | Power-K-Kontextbefehle | WP-I5-009 | I5 | I5 | übernommen |
| CE-SRCH-008 | Power-K-Account-, Preferences- und Hilfebefehle | WP-I5-009 | I5 | I5 | übernommen |
| CE-SRCH-009 | Tastatur-Shortcuts | WP-I5-009 | I5 | I5 | übernommen |
| CE-PROF-001 | Profil-Datenmodell und persönliche Einstellungen | WP-I1-014 | I1 | I1 | übernommen |
| CE-PROF-002 | Profil-Einstellungen (Modal und Seite) | WP-I1-014 | I1 | I1 | übernommen |
| CE-PROF-003 | Profil bearbeiten | WP-I1-014 | I1 | I1 | übernommen |
| CE-PROF-004 | E-Mail-Adresse ändern | WP-I1-014 | I1 | I1 | angepasst |
| CE-PROF-005 | Konto deaktivieren | WP-I1-014 | I1 | I1 | angepasst |
| CE-PROF-006 | Sprache, Zeitzone und Wochenstart (Preferences) | WP-I1-014 | I1 | I1 | übernommen |
| CE-PROF-007 | Verknüpfte OAuth-Konten (nur API) | WP-I0-108 | I0 | – | entfällt |
| CE-PROF-008 | Your work – Summary | WP-I5-010 | I5 | I5 | übernommen |
| CE-PROF-009 | Your work – Work-Item-Tabs | WP-I5-010 | I5 | I5 | übernommen |
| CE-PROF-010 | Your work – Activity | WP-I5-010 | I5 | I5 | übernommen |
| CE-PROF-011 | Profil-Sidebar | WP-I5-010 | I5 | I5 | übernommen |
| CE-AUTH-001 | Sign-in-Seite | WP-I0-001 | I0 | I0/I1 | angepasst |
| CE-AUTH-002 | Sign-up-Seite | WP-I0-108 | I0 | – | entfällt |
| CE-AUTH-003 | E-Mail-Existenzprüfung | WP-I0-108 | I0 | – | entfällt |
| CE-AUTH-004 | Anmeldung mit E-Mail und Passwort | WP-I0-108 | I0 | – | entfällt |
| CE-AUTH-005 | Registrierung mit E-Mail und Passwort | WP-I0-108 | I0 | – | entfällt |
| CE-AUTH-006 | Magic-Code anfordern | WP-I0-108 | I0 | – | entfällt |
| CE-AUTH-007 | Anmeldung/Registrierung mit Magic-Code | WP-I0-108 | I0 | – | entfällt |
| CE-AUTH-008 | Login mit Google | WP-I0-108 | I0 | – | entfällt |
| CE-AUTH-009 | Login mit GitHub inkl. Organisationspflicht | WP-I0-108 | I0 | – | entfällt |
| CE-AUTH-010 | Login mit GitLab (auch self-hosted) | WP-I0-108 | I0 | – | entfällt |
| CE-AUTH-011 | Login mit Gitea | WP-I0-108 | I0 | – | entfällt |
| CE-AUTH-012 | Profil- und Avatar-Übernahme vom Identity-Provider | WP-I0-001 | I0 | I0/I1 | angepasst |
| CE-AUTH-013 | Steuerung der Auth-Methoden | WP-I0-108 | I0 | – | entfällt |
| CE-AUTH-014 | Auth-Fehlercodes als Banner | WP-I0-001 | I0 | I0/I1 | angepasst |
| CE-AUTH-015 | AGB-Hinweis und Auth-Fuß | WP-I0-109 | I0 | I0/I1 | übernommen |
| CE-AUTH-016 | CSRF-Fehlerseite | WP-I0-001 | I0 | I0/I1 | übernommen |
| CE-AUTH-017 | Passwort vergessen | WP-I0-108 | I0 | – | entfällt |
| CE-AUTH-018 | Passwort zurücksetzen | WP-I0-108 | I0 | – | entfällt |
| CE-AUTH-019 | Passwort erstmalig setzen | WP-I0-108 | I0 | – | entfällt |
| CE-AUTH-020 | Passwort ändern | WP-I0-108 | I0 | – | entfällt |
| CE-AUTH-021 | Passwortstärke-Anzeige | WP-I0-108 | I0 | – | entfällt |
| CE-AUTH-022 | Abmelden | WP-I0-001 | I0 | I0/I1 | angepasst |
| CE-AUTH-023 | Session-Ablauf | WP-I0-001 | I0 | I0/I1 | angepasst |
| CE-AUTH-024 | Sessions und Cookies | WP-I0-001 | I0 | I0/I1 | angepasst |
| CE-AUTH-025 | Session-Status-Abfrage | WP-I0-001 | I0 | I0/I1 | angepasst |
| CE-AUTH-026 | Rate-Limits gegen Brute-Force und Missbrauch | WP-I1-016 | I1 | I1 | angepasst |
| CE-AUTH-027 | Login-Sperre deaktivierter Konten | WP-I0-001 | I0 | I0/I1 | angepasst |
| CE-AUTH-028 | Automatischer Beitritt aus angenommenen Einladungen | WP-I1-002 | I1 | I0/I1 | übernommen |
| CE-AUTH-029 | Weiterleitung nach dem Login | WP-I0-001 | I0 | I0/I1 | angepasst |
| CE-AUTH-030 | Onboarding | WP-I1-015 | I1 | I1 | angepasst |
| CE-INST-001 | Instanz-Registrierung und Versionsprüfung | WP-I0-003 | I0 | I0/I6 | angepasst |
| CE-INST-002 | Instanz-Konfiguration aus ENV und DB | WP-I0-003 | I0 | I0/I6 | übernommen |
| CE-INST-003 | Instanz-Info und öffentliche Konfiguration | WP-I0-003 | I0 | I0/I6 | übernommen |
| CE-INST-004 | Instanz-Admins verwalten (nur API) | WP-I0-003 | I0 | I0/I6 | angepasst |
| CE-INST-005 | Instanz-Zustände in der Web-App | WP-I0-003 | I0 | I0/I6 | übernommen |
| CE-INST-006 | Erst-Einrichtung der Instanz | WP-I0-003 | I0 | I0/I6 | angepasst |
| CE-INST-007 | Admin-Anmeldung | WP-I0-003 | I0 | – | entfällt |
| CE-INST-008 | Admin-Abmeldung | WP-I6-001 | I6 | I6 | angepasst |
| CE-INST-009 | Instanzfehler-Ansicht (God Mode) | WP-I6-001 | I6 | I6 | übernommen |
| CE-INST-010 | Dashboard-Shell mit Sidebar | WP-I6-001 | I6 | I6 | übernommen |
| CE-INST-011 | Header mit Breadcrumb | WP-I6-001 | I6 | I6 | übernommen |
| CE-INST-012 | Konto-Menü mit Theme-Umschaltung | WP-I6-001 | I6 | I6 | übernommen |
| CE-INST-013 | Hilfe-Bereich der Admin-Sidebar | WP-I6-001 | I6 | I6 | übernommen |
| CE-INST-014 | Dialog für ungespeicherte Änderungen (God Mode) | WP-I6-001 | I6 | I6 | übernommen |
| CE-INST-015 | Kopierfelder für Plane-URLs | WP-I6-001 | I6 | I6 | übernommen |
| CE-INST-016 | 404-Seite und Fehlerbehandlung (God Mode) | WP-I6-001 | I6 | I6 | übernommen |
| CE-INST-017 | Allgemeine Instanzeinstellungen | WP-I6-002 | I6 | I6 | übernommen |
| CE-INST-018 | SMTP-Konfiguration | WP-I6-002 | I6 | I6 | übernommen |
| CE-INST-019 | Test-E-Mail senden | WP-I6-002 | I6 | I6 | übernommen |
| CE-INST-020 | Authentifizierungsmethoden-Übersicht | WP-I0-003 | I0 | – | entfällt |
| CE-INST-021 | Google-OAuth-Konfiguration | WP-I0-003 | I0 | – | entfällt |
| CE-INST-022 | GitHub-OAuth-Konfiguration | WP-I0-003 | I0 | – | entfällt |
| CE-INST-023 | GitLab-OAuth-Konfiguration | WP-I0-003 | I0 | – | entfällt |
| CE-INST-024 | Gitea-OAuth-Konfiguration | WP-I0-003 | I0 | – | entfällt |
| CE-INST-025 | AI-Einstellungen | WP-I6-002 | I6 | I6 | übernommen |
| CE-INST-026 | Bildbibliotheken (Unsplash) | WP-I6-002 | I6 | I6 | übernommen |
| CE-INST-027 | Workspace-Liste der Instanz | WP-I6-003 | I6 | I6 | übernommen |
| CE-INST-028 | Workspace-Anlage sperren | WP-I6-003 | I6 | I6 | übernommen |
| CE-INST-029 | Workspace anlegen (God Mode) | WP-I6-003 | I6 | I6 | übernommen |
| CE-INST-030 | Willkommens-Popup 'Create workspace' | WP-I6-003 | I6 | I6 | übernommen |
| CE-SPACE-001 | Projekt veröffentlichen (Publish) | WP-I6-004 | I6 | I6 | übernommen |
| CE-SPACE-002 | Board-Einstellungen und Metadaten | WP-I6-004 | I6 | I6 | übernommen |
| CE-SPACE-003 | Öffentliche Issue-Liste | WP-I6-006 | I6 | I6 | übernommen |
| CE-SPACE-004 | Öffentliches Issue-Detail | WP-I6-007 | I6 | I6 | übernommen |
| CE-SPACE-005 | Board-Stammdaten | WP-I6-006 | I6 | I6 | übernommen |
| CE-SPACE-006 | Öffentliche Intake-Einreichung (nur API) | WP-I6-008 | I6 | I6 | übernommen |
| CE-SPACE-007 | Kommentarbilder und Asset-Auslieferung | WP-I6-007 | I6 | I6 | übernommen |
| CE-SPACE-008 | Space-Login: E-Mail-Check | WP-I6-005 | I6 | – | entfällt |
| CE-SPACE-009 | Space-Login und -Sign-up mit Passwort | WP-I6-005 | I6 | – | entfällt |
| CE-SPACE-010 | Space-Login mit Unique Code | WP-I6-005 | I6 | – | entfällt |
| CE-SPACE-011 | OAuth-Buttons im Space | WP-I6-005 | I6 | – | entfällt |
| CE-SPACE-012 | Fehlerbanner aus Auth-Redirects (Space) | WP-I6-005 | I6 | I6 | angepasst |
| CE-SPACE-013 | Rechtshinweis Terms/Privacy (Space) | WP-I6-005 | I6 | I6 | übernommen |
| CE-SPACE-014 | Eingeloggt-Ansicht und next_path-Weiterleitung | WP-I6-005 | I6 | I6 | angepasst |
| CE-SPACE-015 | Instanzfehler-Ansicht (Space) | WP-I6-005 | I6 | I6 | übernommen |
| CE-SPACE-016 | Legacy-URL-Weiterleitung | WP-I6-005 | I6 | I6 | übernommen |
| CE-SPACE-017 | Öffentliches Projekt-Board mit Social-Meta | WP-I6-005 | I6 | I6 | übernommen |
| CE-SPACE-018 | Board-Navbar | WP-I6-006 | I6 | I6 | übernommen |
| CE-SPACE-019 | List-Layout (read-only) | WP-I6-006 | I6 | I6 | übernommen |
| CE-SPACE-020 | Kanban-Layout (read-only) | WP-I6-006 | I6 | I6 | übernommen |
| CE-SPACE-021 | Eigenschafts-Chips | WP-I6-006 | I6 | I6 | übernommen |
| CE-SPACE-022 | Filter-Popover | WP-I6-006 | I6 | I6 | übernommen |
| CE-SPACE-023 | Leiste aktiver Filter | WP-I6-006 | I6 | I6 | übernommen |
| CE-SPACE-024 | Peek-Ansicht eines Work Items | WP-I6-007 | I6 | I6 | übernommen |
| CE-SPACE-025 | Öffentliche Kommentare | WP-I6-008 | I6 | I6 | übernommen |
| CE-SPACE-026 | Kommentar-Reaktionen | WP-I6-008 | I6 | I6 | übernommen |
| CE-SPACE-027 | Emoji-Reaktionen auf Work Items | WP-I6-008 | I6 | I6 | übernommen |
| CE-SPACE-028 | Up- und Downvotes | WP-I6-008 | I6 | I6 | übernommen |
| CE-SPACE-029 | iframe-Einbettung | WP-I6-005 | I6 | I6 | übernommen |
| CE-SPACE-030 | Mention-Darstellung (Space) | WP-I6-007 | I6 | I6 | übernommen |
| CE-SPACE-031 | Fehler- und 404-Seiten (Space) | WP-I6-005 | I6 | I6 | übernommen |
| CE-SPACE-032 | 'Powered by Plane Publish'-Badge | WP-I6-005 | I6 | I6 | übernommen |
| CE-API-001 | API-Key-Authentifizierung | WP-I6-009 | I6 | I6 | übernommen |
| CE-API-002 | Rate-Limiting je API-Key | WP-I6-009 | I6 | I6 | übernommen |
| CE-API-003 | API-Aktivitätsprotokoll | WP-I6-009 | I6 | I6 | übernommen |
| CE-API-004 | OpenAPI-Dokumentation | WP-I6-009 | I6 | I6 | übernommen |
| CE-API-005 | Aktueller Benutzer | WP-I6-009 | I6 | I6 | übernommen |
| CE-API-006 | Projekte verwalten | WP-I6-010 | I6 | I6 | übernommen |
| CE-API-007 | Projekt archivieren/dearchivieren | WP-I6-010 | I6 | I6 | übernommen |
| CE-API-008 | Projekt-Summary | WP-I6-010 | I6 | I6 | übernommen |
| CE-API-009 | States verwalten | WP-I6-010 | I6 | I6 | übernommen |
| CE-API-010 | Labels verwalten | WP-I6-010 | I6 | I6 | übernommen |
| CE-API-011 | Workspace-Mitglieder lesen | WP-I6-010 | I6 | I6 | übernommen |
| CE-API-012 | Projekt-Mitglieder verwalten | WP-I6-010 | I6 | I6 | übernommen |
| CE-API-013 | Workspace-Einladungen | WP-I6-010 | I6 | I6 | übernommen |
| CE-API-014 | Stickies | WP-I6-011 | I6 | I6 | übernommen |
| CE-API-015 | User-Assets (Avatar/Cover) | WP-I6-011 | I6 | I6 | übernommen |
| CE-API-016 | Generic Workspace Assets | WP-I6-011 | I6 | I6 | übernommen |
| CE-API-017 | Work Items verwalten | WP-I6-012 | I6 | I6 | übernommen |
| CE-API-018 | Work Item per Identifier | WP-I6-012 | I6 | I6 | übernommen |
| CE-API-019 | Work-Item-Suche | WP-I6-012 | I6 | I6 | übernommen |
| CE-API-020 | Work-Item-Links | WP-I6-012 | I6 | I6 | übernommen |
| CE-API-021 | Work-Item-Kommentare | WP-I6-012 | I6 | I6 | übernommen |
| CE-API-022 | Work-Item-Aktivitäten | WP-I6-012 | I6 | I6 | übernommen |
| CE-API-023 | Work-Item-Anhänge | WP-I6-012 | I6 | I6 | übernommen |
| CE-API-024 | Work-Item-Relationen | WP-I6-012 | I6 | I6 | übernommen |
| CE-API-025 | Intake über die API | WP-I6-012 | I6 | I6 | übernommen |
| CE-API-026 | Cycles verwalten | WP-I6-013 | I6 | I6 | übernommen |
| CE-API-027 | Work Items in Cycles | WP-I6-013 | I6 | I6 | übernommen |
| CE-API-028 | Cycle-Transfer | WP-I6-013 | I6 | I6 | übernommen |
| CE-API-029 | Cycle-Archiv | WP-I6-013 | I6 | I6 | übernommen |
| CE-API-030 | Modules verwalten | WP-I6-013 | I6 | I6 | übernommen |
| CE-API-031 | Work Items in Modulen | WP-I6-013 | I6 | I6 | übernommen |
| CE-API-032 | Modul-Archiv | WP-I6-013 | I6 | I6 | übernommen |
| CE-WH-001 | Webhook-Datenmodell und Event-Typen | WP-I6-015 | I6 | I6 | übernommen |
| CE-WH-002 | Webhook-Liste | WP-I6-014 | I6 | I6 | übernommen |
| CE-WH-003 | Webhook anlegen | WP-I6-014 | I6 | I6 | übernommen |
| CE-WH-004 | Webhook-Secret anzeigen, regenerieren und herunterladen | WP-I6-014 | I6 | I6 | übernommen |
| CE-WH-005 | Webhook bearbeiten | WP-I6-014 | I6 | I6 | übernommen |
| CE-WH-006 | Webhook löschen | WP-I6-014 | I6 | I6 | übernommen |
| CE-WH-007 | Webhook-Zustellung | WP-I6-015 | I6 | I6 | übernommen |
| CE-WH-008 | Webhook-Payload-Format | WP-I6-015 | I6 | I6 | übernommen |
| CE-WH-009 | Webhook-Deaktivierungs-Mail | WP-I6-015 | I6 | I6 | übernommen |
| CE-WH-010 | Webhook-Zustellprotokoll (nur API) | WP-I6-015 | I6 | I6 | übernommen |
| CE-WH-011 | SSRF-Schutz und Ziel-Allowlists für Webhooks | WP-I6-015 | I6 | I6 | übernommen |
| CE-WH-012 | API-Token-Liste | WP-I6-016 | I6 | I6 | übernommen |
| CE-WH-013 | API-Token anlegen | WP-I6-016 | I6 | I6 | übernommen |
| CE-WH-014 | API-Token löschen | WP-I6-016 | I6 | I6 | übernommen |
| CE-EXP-001 | Work-Item-Export (CSV/XLSX/JSON) | WP-I6-017 | I6 | I6 | übernommen |
| CE-EXP-002 | Export-Historie und Download | WP-I6-017 | I6 | I6 | übernommen |
| CE-AI-001 | KI-Assistent im Work-Item-Modal | WP-I6-018 | I6 | I6 | übernommen |
| CE-AI-002 | Unsplash-Bildsuche | WP-I6-018 | I6 | I6 | übernommen |
| CE-I18N-001 | Sprachauswahl und Persistenz | WP-I1-017 | I1 | I1 | übernommen |
| CE-I18N-002 | Übersetzte UI-Texte mit Fallback und ICU-Pluralisierung | WP-I1-017 | I1 | I1 | übernommen |
| CE-I18N-003 | Datums- und Zeitdarstellung | WP-I1-017 | I1 | I1 | übernommen |
| CE-I18N-004 | Zeitzonen-Auswahl und -Umrechnung | WP-I1-017 | I1 | I1 | übernommen |
| CE-I18N-005 | Theme-System und Theme-Varianten | WP-I1-018 | I1 | I1 | übernommen |
| CE-I18N-006 | Theme-Auswahl und Server-Persistenz | WP-I1-018 | I1 | I1 | übernommen |
| CE-I18N-007 | Custom Theme | WP-I1-018 | I1 | I1 | übernommen |
| CE-I18N-008 | High-Contrast-Themes | WP-I1-018 | I1 | I1 | übernommen |
| CE-I18N-009 | Farb-Token-System | WP-I1-018 | I1 | I1 | übernommen |
| CE-I18N-010 | Editor-Farbpalette | WP-I2-022 | I2 | I1 | übernommen |
| CE-I18N-011 | Typografie | WP-I0-006 | I0 | I0…I3 | übernommen |
| CE-I18N-012 | Gebündelte Schriften (Airgap) | WP-I0-006 | I0 | I0…I3 | übernommen |
| CE-I18N-013 | Icon-System | WP-I0-006 | I0 | I0…I3 | übernommen |
| CE-I18N-014 | Status-, Zyklus-, Modul- und Prioritäts-Icons | WP-I1-105 | I1 | I0…I3 | übernommen |
| CE-I18N-015 | Datei-Typ-Icons und Locked-Pill | WP-I1-105 | I1 | I0…I3 | übernommen |
| CE-I18N-016 | Logo-Picker (Emoji, Lucide, Material) | WP-I1-105 | I1 | I0…I3 | übernommen |
| CE-I18N-017 | Emoji-Reaktions-Komponenten | WP-I2-007 | I2 | I0…I3 | übernommen |
| CE-I18N-018 | Empty-State-Illustrationen und theme-abhängige Assets | WP-I1-105 | I1 | I0…I3 | übernommen |
| CE-I18N-019 | Propel-Komponentenbibliothek und Varianten | WP-I1-105 | I1 | I0…I3 | übernommen |
| CE-I18N-020 | Blocks-Composites | WP-I1-105 | I1 | I0…I3 | übernommen |
| CE-I18N-021 | Toast-Benachrichtigungen | WP-I0-006 | I0 | I0…I3 | übernommen |
| CE-I18N-022 | Diagramm-Bausteine und Farbpaletten | WP-I3-101 | I3 | I0…I3 | übernommen |
| CE-I18N-023 | Animationen | WP-I0-006 | I0 | I0…I3 | übernommen |
| CE-I18N-024 | Maßsystem, Elevation und Scrollbars | WP-I0-006 | I0 | I0…I3 | übernommen |
| CE-I18N-025 | Avatare und Farbwähler | WP-I0-006 | I0 | I0…I3 | übernommen |
| CE-I18N-026 | Lade-Indikatoren und Navigations-Progressbar | WP-I0-006 | I0 | I0…I3 | übernommen |
| CE-UIX-001 | Seiten-Header und Breadcrumbs | WP-I1-019 | I1 | I1 | übernommen |
| CE-UIX-002 | Leerzustände und Skeletons | WP-I1-019 | I1 | I1 | übernommen |
| CE-UIX-003 | Globale Modal-Hosts | WP-I1-019 | I1 | I1 | übernommen |
| CE-UIX-004 | Dialog- und Dropdown-Verhalten | WP-I1-019 | I1 | I1 | übernommen |
| CE-UIX-005 | Tab-Reihenfolge in Formularen | WP-I1-019 | I1 | I1 | übernommen |
| CE-UIX-006 | Synchronisierte LocalStorage-Präferenzen und Plattformerkennung | WP-I1-020 | I1 | I1 | übernommen |
| CE-UIX-007 | Zwischenablage und CSV-Download | WP-I1-020 | I1 | I1 | übernommen |
| CE-UIX-008 | Warnung bei ungespeicherten Änderungen | WP-I1-020 | I1 | I1 | übernommen |
| CE-UIX-009 | Image-Picker und Uploads mit Fortschritt | WP-I1-103 | I1 | I1 | übernommen |
| CE-UIX-010 | 404-, Fehler- und Zugriffsseiten (Web) | WP-I1-020 | I1 | I1 | übernommen |
| CE-UIX-011 | Stale-Chunk-Auto-Reload | WP-I1-020 | I1 | I1 | übernommen |
| CE-UIX-012 | Legacy-Redirects | WP-I1-020 | I1 | I1 | übernommen |
| CE-UIX-013 | Link-Icons und URL-Erkennung | WP-I1-020 | I1 | I1 | übernommen |
| CE-OPS-001 | Self-Hosting-CLI | WP-I7-101 | I7 | I7 | angepasst |
| CE-OPS-002 | Daten-Restore | WP-I7-101 | I7 | I7 | angepasst |
| CE-OPS-003 | Docker-Swarm-Deployment | WP-I7-102 | I7 | I7 | angepasst |
| CE-OPS-004 | All-in-One-Container | WP-I7-103 | I7 | I7 | angepasst |
| CE-OPS-005 | Reverse-Proxy mit automatischem HTTPS | WP-I7-105 | I7 | I0 | übernommen |
| CE-OPS-006 | Statische Frontend-Auslieferung | WP-I0-103 | I0 | I0 | übernommen |
| CE-OPS-007 | Konfigurierbare Base-URLs und -Paths | WP-I0-103 | I0 | I0 | übernommen |
| CE-OPS-008 | Health-Checks und robots.txt | WP-I0-103 | I0 | I0 | übernommen |
| CE-OPS-009 | Upload-Größenlimit mit 413-Fehler | WP-I0-103 | I0 | I0/I7 | übernommen |
| CE-OPS-010 | Read-Replica-Unterstützung | WP-I7-104 | I7 | I7 | übernommen |
| CE-OPS-011 | Redis mit TLS | WP-I1-104 | I1 | I1 | übernommen |
| CE-OPS-012 | Objektspeicher mit Presigned Upload/Download | WP-I1-103 | I1 | I1 | übernommen |
| CE-OPS-013 | Datei-Assets (FileAsset) | WP-I1-103 | I1 | I1 | übernommen |
| CE-OPS-014 | Soft-Delete und endgültige Löschung | WP-I1-101 | I1 | I1 | übernommen |
| CE-OPS-015 | Aufbewahrung und Bereinigung | WP-I1-101 | I1 | I1 | übernommen |
| CE-OPS-016 | Zeitgesteuerte Jobs (Beat-Plan) | WP-I1-101 | I1 | I1 | übernommen |
| CE-OPS-017 | Rich-Text-Sanitizing und Binary-Prüfung | WP-I2-101 | I2 | I2 | übernommen |
| CE-OPS-018 | SSRF-sichere ausgehende Requests | WP-I2-102 | I2 | I2 | übernommen |
| CE-OPS-019 | Strukturiertes Request-Logging | WP-I0-104 | I0 | I0 | übernommen |
| CE-OPS-020 | Betriebs-CLI (Management-Commands) | WP-I7-101 | I7 | I7 | übernommen |
| CE-OPS-021 | Lokale Entwicklungsumgebung | WP-I0-102 | I0 | I0 | angepasst |
| CE-OPS-022 | Isolierter Test-Stack und Testsuites | WP-I0-106 | I0 | I0 | angepasst |
| CE-OPS-023 | CI/CD-Pipelines | WP-I0-106 | I0 | I0 | angepasst |
| CE-OPS-024 | Dummy-Daten-Generator | WP-I2-103 | I2 | I2 | übernommen |

## Anhang B – CE-IDs, deren Inkrement von 15 Anhang B abweicht (Begründung plan/04 OP-PLAN-03)

| CE-ID | 15 Anh. B | Plan | WP |
|---|---|---|---|
| CE-WS-002 | I0/I1 | I4 | WP-I4-009 |
| CE-WI-025 | I2 | I3 | WP-I3-007 |
| CE-WI-026 | I2 | I3 | WP-I3-010 |
| CE-LV-004 | I2 | I3 | WP-I3-001 |
| CE-LV-011 | I2 | I3 | WP-I3-002 |
| CE-LV-016 | I2 | I3 | WP-I3-006 |
| CE-PAGE-024 | I4 | I2 | WP-I2-023 |
| CE-PAGE-025 | I4 | I2 | WP-I2-023 |
| CE-PAGE-026 | I4 | I2 | WP-I2-023 |
| CE-PAGE-027 | I4 | I2 | WP-I2-022 |
| CE-PAGE-028 | I4 | I2 | WP-I2-022 |
| CE-PAGE-029 | I4 | I2 | WP-I2-022 |
| CE-PAGE-030 | I4 | I2 | WP-I2-023 |
| CE-PAGE-031 | I4 | I2 | WP-I2-023 |
| CE-PAGE-032 | I4 | I2 | WP-I2-023 |
| CE-PAGE-033 | I4 | I2 | WP-I2-023 |
| CE-PAGE-039 | I4 | I2 | WP-I2-022 |
| CE-PAGE-040 | I4 | I2 | WP-I2-022 |
| CE-RT-009 | I4 | I0 | WP-I0-107 |
| CE-I18N-010 | I1 | I2 | WP-I2-022 |
| CE-OPS-005 | I0 | I7 | WP-I7-105 |

## Anhang C – Endpunkte, deren Inkrement im Katalog 04 vom Arbeitspaket abweicht

Ein registrierter Endpunkt gehört zu genau einem Arbeitspaket: dem Paket, das eine seiner CE-IDs enthält und im Inkrement des Katalogs 04 liegt, sonst dem frühesten Paket mit einer seiner CE-IDs. Die folgenden Endpunkte entstehen deshalb in einem anderen Inkrement als in 04 notiert; maßgeblich ist dieser Plan (Begründung plan/04 OP-PLAN-03).

| EP | Methode | Pfad | Inkr. 04 | WP | Inkr. WP |
|---|---|---|---|---|---|
| EP-0144 | GET | `/api/workspaces/{slug}/home-preferences/` | I1 | WP-I5-003 | I5 |
| EP-0145 | PATCH | `/api/workspaces/{slug}/home-preferences/{key}/` | I1 | WP-I5-003 | I5 |
| EP-0148 | GET | `/api/workspaces/{slug}/user-properties/` | I3 | WP-I2-013 | I2 |
| EP-0149 | PATCH | `/api/workspaces/{slug}/user-properties/` | I3 | WP-I2-013 | I2 |
| EP-0255 | POST | `/api/workspaces/{slug}/projects/{project_id}/bulk-archive-issues/` | I3 | WP-I2-009 | I2 |
| EP-0269 | GET | `/api/workspaces/{slug}/projects/{project_id}/issues/{pk}/archive/` | I3 | WP-I2-009 | I2 |
| EP-0270 | POST | `/api/workspaces/{slug}/projects/{project_id}/issues/{pk}/archive/` | I3 | WP-I2-009 | I2 |
| EP-0271 | DELETE | `/api/workspaces/{slug}/projects/{project_id}/issues/{pk}/archive/` | I3 | WP-I2-009 | I2 |
| EP-0419 | GET | `/api/assets/v2/workspaces/{slug}/projects/{project_id}/download/{asset_id}/` | I2 | WP-I1-103 | I1 |
| EP-0480 | GET | `/api/workspaces/{slug}/project-stats/` | I5 | WP-I1-005 | I1 |

