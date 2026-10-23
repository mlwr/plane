# funk. – Überführung von Plane nach .NET und Angular

Dieser Ordner enthält den vollständigen Plan für **funk.**: eine Neuimplementierung von Plane (Open-Source-Projektmanagement) mit .NET 10, Aspire, Entity Framework Core, PostgreSQL (inkl. pgvector) und Angular 22, einschließlich der ausgewählten Funktionen der kommerziellen Plane-Editionen.

- **Neuer Code:** Repository [`mlwr/funk.`](https://github.com/mlwr/funk.), Hauptbranch `develop`.
- **Referenz:** dieses Repository (`mlwr/plane`) mit dem Original auf Stand `053b2c0` (Plane 1.4.2, Branch `funk-referenz-1.4.2`). Alle Pfad- und Zeilenangaben im Plan beziehen sich auf diesen Stand.
- **Sprache:** Deutsch; Code-Bezeichner Englisch. Zielbezeichner tragen `funk`/`Funk` (ADR-009C).

## Status (23.10.2026)

| Phase | Stand |
|---|---|
| IST-Analyse des Originals | fertig (16 Bereichsanalysen) |
| Feature-Kataloge | fertig (507 CE-Features, 246 Bezahl-Features, Auswahl: 52 Pakete in Wellen W1–W9) |
| Zielarchitektur | fertig (Dokumente 00–11, 14–17, reviewt und abgeglichen) |
| Umsetzungsplan | fertig (Inkremente I0–I7, 180 Arbeitspakete, Agenten-Leitfaden, Risiken) |
| Implementierung | startet mit I0 (Walking Skeleton und Spikes) in `funk.` |

## Leseweg

**Für alle zuerst:**
1. [`architecture/00-grundsatzentscheidungen.md`](architecture/00-grundsatzentscheidungen.md) – verbindliche Entscheidungen des Auftraggebers (ADR-000…009D): Stack, keine Plan-Stufen, YDotNet, Greenfield, Self-hosted/Airgapped, UI 1:1, Forgejo, Keycloak, Repository `funk.`, Branding, Sprachen de/en.
2. [`architecture/01-zielarchitektur-und-tech-stack.md`](architecture/01-zielarchitektur-und-tech-stack.md) – Zielarchitektur, Technologieentscheidungen (ADR-010 ff.), Solution- und Frontend-Struktur, Pflicht-Spikes.
3. [`architecture/17-abgleich-dokumentuebergreifend.md`](architecture/17-abgleich-dokumentuebergreifend.md) – verbindliche Auflösung aller Widersprüche zwischen den Dokumenten, weitere Entscheidungen des Auftraggebers, Umbenennungstabelle Plane → funk.
4. [`plan/01-roadmap-ce.md`](plan/01-roadmap-ce.md) – Inkremente, Meilensteine, Abnahmekriterien, Bezahl-Wellen.

**Für Implementierungs-Agenten:**
5. [`plan/03-agenten-leitfaden.md`](plan/03-agenten-leitfaden.md) – Vorgehen, Konventionen, Branch-/Commit-Regeln, Definition of Done.
6. [`plan/02-arbeitspakete-ce.md`](plan/02-arbeitspakete-ce.md) – das zu bearbeitende Arbeitspaket (`WP-<Inkrement>-<NNN>`) mit Referenzen auf Analyse, Architektur und Original-Code.
7. Die im Arbeitspaket genannten Abschnitte der Architektur- und Analyse-Dokumente, dann der Original-Code.

## Inhalt

### `analysis/` – IST-Analyse des Originals

| Dokument | Bereich |
|---|---|
| [01](analysis/01-gesamtarchitektur-infrastruktur.md) | Monorepo, Dienste, Deployment, ENV, CI, Tests |
| [02a](analysis/02a-datenmodell-kern.md) / [02b](analysis/02b-datenmodell-arbeitsobjekte.md) | Datenmodell (Kern / Arbeitsobjekte), Migrationen |
| [03](analysis/03-api-intern-workspace-projekt-user.md) / [04](analysis/04-api-intern-arbeitsobjekte.md) | Interne App-API |
| [05](analysis/05-api-public-v1-space-instanz.md) | Public API v1, Space, Instanz/God Mode |
| [06](analysis/06-auth-sicherheit-querschnitt.md) | Auth, Berechtigungen, Sicherheit, Utilities |
| [07](analysis/07-hintergrundjobs-mail-storage-webhooks.md) | Celery-Tasks, E-Mail, Storage, Webhooks |
| [08](analysis/08-frontend-web-architektur.md) | Web-App: Routen, Stores, Services |
| [09](analysis/09-frontend-arbeitsobjekte-layouts.md) | Work Items und Layouts |
| [10a](analysis/10a-frontend-workspace-projekt-navigation.md) / [10b](analysis/10b-frontend-cycles-modules-pages-views-weitere.md) | Alle weiteren Screens |
| [11](analysis/11-frontend-admin-space.md) | God Mode und Space |
| [12](analysis/12-editor-echtzeit-live.md) | Editor und Live-Server |
| [13a](analysis/13a-designsystem-ui-tokens.md) / [13b](analysis/13b-shared-packages-i18n.md) | Designsystem, Shared Packages, i18n |

### `features/` – Feature-Kataloge

| Dokument | Inhalt |
|---|---|
| [10](features/10-ce-feature-katalog.md) | Alle 507 Features der Community Edition mit IDs `CE-<DOMÄNE>-<NNN>` |
| [20–28](features/) | Recherchen zu den Bezahl-Features je Themenbereich |
| [29](features/29-paid-feature-matrix.md) | Exakte Bezahl-Feature-Matrix (246 Features, Mindest-Plan je Feature) |
| [30](features/30-paid-auswahlliste.md) | Auswahl des Auftraggebers: 52 Pakete, priorisiert in Wellen W1–W9 |

### `architecture/` – Zielarchitektur

| Dokument | Thema |
|---|---|
| [00](architecture/00-grundsatzentscheidungen.md) | Grundsatzentscheidungen |
| [01](architecture/01-zielarchitektur-und-tech-stack.md) | Zielarchitektur und Tech-Stack |
| [02](architecture/02-backend-solution-und-konventionen.md) | Backend-Solution und Konventionen |
| [03](architecture/03-datenmodell-efcore.md) | Datenmodell (EF Core) |
| [04](architecture/04-api-design-und-endpunktkatalog.md) | API-Design und Endpunktkatalog |
| [05](architecture/05-auth-sicherheit-berechtigungen.md) | Auth (Keycloak), Sicherheit, Berechtigungen |
| [06](architecture/06-hintergrundjobs-events-benachrichtigungen.md) | Hintergrundjobs, Events, Benachrichtigungen |
| [07](architecture/07-realtime-kollaboration-dokumente.md) | Realtime (YDotNet), Dokumente, PDF |
| [08](architecture/08-frontend-angular-architektur.md) | Angular-Frontend-Architektur |
| [09](architecture/09-ui-paritaet-designsystem.md) | UI-Parität und Designsystem-Port |
| [10](architecture/10-editor-angular.md) | Editor in Angular |
| [11](architecture/11-suche-und-ai-basis.md) | Suche und AI-Basis |
| [14](architecture/14-infrastruktur-deployment-betrieb.md) | Infrastruktur, Deployment, Betrieb |
| [15](architecture/15-teststrategie-qualitaet-paritaet.md) | Teststrategie und Paritätsprüfung |
| [16](architecture/16-erweiterungspunkte-bezahl-features.md) | Erweiterungspunkte für die Bezahl-Pakete |
| [17](architecture/17-abgleich-dokumentuebergreifend.md) | Dokumentübergreifender Abgleich |

Die Nummern 12 und 13 sind unbelegt (die früher geplanten Fachdesigns der Bezahl-Features werden erst kurz vor der jeweiligen Welle erstellt).

### `plan/` – Umsetzungsplan

| Dokument | Inhalt |
|---|---|
| [01](plan/01-roadmap-ce.md) | Roadmap I0–I7, Meilensteine M0–M7, Wellen W1–W9 |
| [02](plan/02-arbeitspakete-ce.md) | 180 Arbeitspakete (alle 507 CE-IDs und 564 Endpunkte genau einmal zugeordnet) |
| [03](plan/03-agenten-leitfaden.md) | Leitfaden für Implementierungs-Agenten |
| [04](plan/04-risiken-offene-punkte.md) | Risiken und offene Entscheidungen |

### Daten und Werkzeuge

- `*/_data/` – maschinenlesbare Fassungen (Feature-Listen, Datenmodell, Endpunktkatalog, Event-Katalog, Rechte-Matrix, Testmatrix, Arbeitspakete).
- `_werkzeuge/` – Generatoren und Prüfskripte (z. B. `plan/check_wp.py` prüft die Zuordnung aller CE-IDs; `rename_funk.py` hat die Zielbezeichner umgestellt) sowie die Workflow-Skripte, mit denen der Plan erstellt wurde.

## Pflege

- Der Plan wird zu Beginn von I0 nach `funk./docs/plan/` übernommen und dort weitergepflegt (Abweichungslisten, Spike-Ergebnisse, erledigte Arbeitspakete). In diesem Repository bleibt die eingefrorene Analyse.
- Neue Entscheidungen werden in `architecture/17` bzw. in `plan/04` festgehalten; Grundsatzentscheidungen in `architecture/00`.
