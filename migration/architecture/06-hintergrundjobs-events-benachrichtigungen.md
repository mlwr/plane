# 06 – Hintergrundjobs, Events und Benachrichtigungen

> **Status:** verbindlich für das Thema Hintergrundverarbeitung (Fachdokument nach `01` Anhang A: „Task→Job-Tabelle, Event-Katalog, Activity-Pipeline, Notifications, E-Mail, Webhooks, Exporte“, baut auf ADR-020, ADR-027, ADR-028).
> **Rangfolge:** `00-grundsatzentscheidungen.md` (ADR-000…009) > `01-zielarchitektur-und-tech-stack.md` (ADR-010…052) > `17-abgleich-dokumentuebergreifend.md` (ABG-001…058 und Auftraggeber-Entscheidungen) > dieses Dokument. Namen und Schnittstellen aus `02`, `05`, `08`, `09`, `14`, `15`, `16` werden übernommen; wo dieses Dokument dort etwas ergänzt, ist es als **Nachtrag** markiert und in §9 als Änderungsauftrag geführt.
> **Stand:** 23.10.2026. **Zielcode:** Repository `funk.` (ADR-009); alle Zielpfade sind relativ zu dessen Wurzel. Original-Referenz: Plane v1.4.2 CE in diesem Repository.
> **Maschinenlesbar:** `migration/architecture/_data/06-event-catalog.json` (Event-Katalog, 82 Einträge, Quelle für `EventCatalogSnapshotTests` und `EventEmissionTests`, ABG-011) und `migration/architecture/_data/06-jobs.json` (Task→Job-Tabelle, Cron-Plan, Aufrufstellen der Activity-Pipeline).
> **Sprache:** Fließtext Deutsch, Bezeichner Englisch.

**Kürzel:** `API/` = `apps/api/plane/`, `BG/` = `apps/api/plane/bgtasks/`, `TPL/` = `apps/api/templates/`, `WEB/` = `apps/web/`. `A07` = `migration/analysis/07-hintergrundjobs-mail-storage-webhooks.md` (IST-Analyse, Nummern T1…T47, B1…B13, C1…C78, A1…A38, W1…W22, M1…M14, E1…E13, N1…N9, EM1…EM7, WH1…WH11 beziehen sich darauf). `BE/` = `src/` in `funk.`, `MSG/` = `src/building-blocks/Plane.BuildingBlocks.Messaging/`, `MAIL/` = `src/platform/Plane.Platform.Mail/`.

## Inhaltsverzeichnis

1. [Ziel & Scope](#1-ziel--scope)
2. [Entscheidungen (D06-ADR-01 ff.)](#2-entscheidungen-d06-adr-01-ff)
3. [Detaildesign](#3-detaildesign)
   - 3.1 Bausteine und Projekte · 3.2 Datenmodell der Messaging-Infrastruktur · 3.3 Outbox und Dispatcher · 3.4 Consumer und Inbox · 3.5 Job-Queue, Retry, Dead-Letter, Queues und Worker-Pools · 3.6 Scheduler (Cron, Leader) · 3.7 EventContext, Akteur, Herkunft, Kausaltiefe · 3.8 Event-Katalog · 3.9 Activity-Pipeline · 3.10 In-App-Benachrichtigungen · 3.11 E-Mail-Benachrichtigungen (Bündelung) · 3.12 Echtzeit-Push (SignalR) · 3.13 E-Mail-Plattform und Templates · 3.14 Webhooks · 3.15 Exporte · 3.16 Cleanup, Retention, Hard-Delete · 3.17 Automationen · 3.18 Weitere Jobs · 3.19 Skalierung · 3.20 Monitoring
4. [Vollständige Mapping-Tabellen Original → Ziel](#4-vollständige-mapping-tabellen-original--ziel)
5. [Code-Skelette](#5-code-skelette)
6. [Erweiterungspunkte für Bezahl-Pakete](#6-erweiterungspunkte-für-bezahl-pakete)
7. [Akzeptanzkriterien & Tests](#7-akzeptanzkriterien--tests)
8. [Risiken & offene Punkte](#8-risiken--offene-punkte)
9. [Abhängigkeiten zu anderen Dokumenten (02–16)](#9-abhängigkeiten-zu-anderen-dokumenten-0216)

---

## 1. Ziel & Scope

### 1.1 Ziel

Dieses Dokument macht die gesamte Hintergrundverarbeitung der Community Edition für einen Implementierungs-Agenten **direkt umsetzbar**:

1. die Messaging-Infrastruktur aus ADR-020 (transaktionale Outbox, Inbox, PostgreSQL-Job-Queue, Cron-Scheduler mit Leader-Lock) mit konkreten Tabellen, Klassen, Algorithmen, Options-Klasse `PlaneWorkerOptions` (benannte Worker-Pools, Pflicht-Restpunkt aus `17` §7) und Tests,
2. den **Port jeder Celery-Task** (47 aktive `@shared_task` + der auskommentierte `restore_related_objects`, A07 §2.3) und **jedes Beat-Eintrags** (B1…B13, A07 §2.2) auf Job, Consumer oder synchronen Domänendienst mit Trigger, Queue, Retry, Idempotenz und Leader-Bedarf (§4.2, §4.3),
3. den **Event-Katalog** (`plane.<aggregat>.<ereignis>.v1`, 82 Einträge, Obermenge der Mindestmenge aus `16` §3.2.4) samt Produzenten-Commands und CE-Consumern,
4. die **Activity-Pipeline** mit allen 78 Aufrufstellen, 27 Activity-Typen, 12 Feld-Trackern und 38 Varianten so, dass jede Feldänderung dieselbe `work_item_activities`-Zeile wie im Original erzeugt (Abweichungen nur als dokumentierte Fehlerkorrekturen),
5. In-App-Benachrichtigungen, E-Mail-Benachrichtigungen mit 5-Minuten-Bündelung und den Echtzeit-Push des Ungelesen-Zählers über SignalR,
6. den Port aller E-Mail-Templates aus `apps/api/templates/` nach Fluid (Liquid) mit MailKit,
7. Webhooks (Events, Payload, Signatur, Retry, Deaktivierung, SSRF), Exporte (CSV/JSON/XLSX, Analytics-CSV per Mail), Cleanup/Retention/Hard-Delete und die Automationen Auto-Archive/Auto-Close inklusive Korrektur des projektübergreifenden Close-State-Fallbacks,
8. die Erweiterungspunkte, die die 🧱-Pakete C1, C3 und H6 (und die übrigen strukturrelevanten Pakete, soweit sie Jobs/Events berühren) später brauchen – ohne Fachdesign.

### 1.2 Scope

| Im Scope | Nicht im Scope (zuständiges Dokument) |
|---|---|
| `Plane.BuildingBlocks.Messaging` vollständig (Outbox-Dispatcher, Inbox, Job-Queue, Scheduler, Event-Katalog, `PlaneWorkerOptions`) | `OutboxInterceptor`, `TransactionBehavior`, Domain-Event-Schleife (Mechanik `02` §3.2.2/§3.19; hier nur genutzt) |
| Task→Job-Tabelle, Cron-Plan, Queue-Zuordnung, Retry-Policies | Endpunktverträge der Notification-, Webhook-, Export- und Asset-APIs (`04`), Berechtigungen (`05` Anhang B) |
| Event-Katalog mit Payload-Feldern und Produzenten | Entitäten/Indizes der Fachtabellen (`03`; hier nur Spalten, die die Pipelines lesen/schreiben, als Vorgabe) |
| Activity-Pipeline (`IActivityRecorder`, Typen, Varianten, Subscriber, Mentions) | Activity-Darstellung im Frontend (`08`/`09`, `ACTIVITY_RENDERERS`) |
| Notifications (Erzeugung, E-Mail-Bündelung, Präferenzen-Auswertung, SignalR-Push) | Inbox-UI und Inbox-Endpunkte (`04`, `08`) |
| E-Mail-Plattform (`IMailSender`, `MailTemplateRenderer`, alle Templates, Bilder, Text-Teil, SMTP-Test-Fehlertexte) | SMTP-Formular im God Mode (`11`-Analyse, `04`) |
| Webhook-Zustellung, Trigger-Abbildung, Payload, Signatur, Logs, Deaktivierung | SSRF-Handler und URL-Prüfung beim Speichern (`05` §3.17.2 – hier nur genutzt) |
| Exporte (Work Items CSV/JSON/XLSX, Analytics-CSV per Mail), Ablauf der Export-Links | Objektspeicher-Abstraktion `IObjectStorage` (`02`/`14` §3.7.6) |
| Cleanup-, Retention- und Hard-Delete-Jobs, Soft-Delete-Kaskaden-Job (Deferred) | Soft-Delete-Mechanik Inline (`02` D02-ADR-03) |
| Automationen (Auto-Archive, Auto-Close, Intake-Unsnooze, Cycle-Abschluss-Erkennung) | State-Change-Pipeline-Interna (`16` §5.9; hier Nutzung durch Auto-Close) |
| Weitere Jobs: Workspace-Seed, Link-Crawler, Asset-Metadaten, Asset-Kopie, Recent Visits, API-Activity-Log, Identity-Jobs aus `05` | Page-Transaktionen/-Versionen im Detail und `convert-document` (`07`; hier nur Einordnung), Suche/Indexierung (`11`) |
| Skalierung und Monitoring der Hintergrundverarbeitung | AppHost/Helm/Compose der Worker-Replikate (`14` §3.11/§3.12) |
| Erweiterungspunkte §6 (nur Andockstellen, kein Fachdesign) | Fachdesign der Bezahl-Pakete (Wellenpläne, `16` §6) |

### 1.3 Wann welcher Teil gebraucht wird (Inkremente nach `01` §1.3)

| Baustein (Abschnitt) | Inkrement | erster Nutzer / Abnahme | Spike |
|---|---|---|---|
| Tabellen `outbox_messages`, `inbox_messages`, `jobs`, `recurring_job_states` (§3.2); Outbox-Dispatcher, JobRunner, Scheduler, Leader-Lock, `PlaneWorkerOptions`, Event-Katalog + Snapshot-Test, `LISTEN/NOTIFY` (§3.3–§3.7) | **I0 (Gerüst)** | Schnitt 2/3 „Workspace/Projekt anlegen“ schreibt `plane.workspace.created.v1`, `plane.project.created.v1`; `identity.expired_sessions_cleanup` (SEC-45) läuft | S12 vor I1 |
| JobRunner im Host `Plane.Realtime` für Queue `realtime` (§3.12) | I0 (Gerüst ohne Consumer) | H6-Hub-Gerüst (`01` §1.4) | – |
| Messaging produktiv (Retry, Dead-Letter, Pools, Kill-Tests), Mail-Plattform (MailKit, Fluid, Mailpit), Templates M5, M7, M8, M9 (§3.13), Workspace-Seed (§3.18.1), Asset-Metadaten-Job, Hard-Delete, Soft-Delete-Kaskade Deferred, Cleanup unbestätigter Assets, IdP-Sync-Job | **I1** | CE-WS-002, CE-WS-010, CE-PRJ-021, CE-OPS-013, CE-OPS-014, CE-OPS-016, CE-AUTH-027 | S12 grün |
| Activity-Pipeline vollständig, Subscriber/Mentions synchron, Beschreibungs-Versionen, Link-Crawler, Work-Item-Events (§3.9, §3.18) | **I2** | CE-WI-003, CE-WI-039, CE-WI-041, CE-WI-044, CE-WI-035 | – |
| Cycle-/Modul-/Intake-/View-Events, Auto-Archive/-Close, Unsnooze, Cycle-Abschluss-Erkennung (§3.17) | **I3** | CE-PRJ-039, CE-PRJ-040, CE-INT-008 | – |
| Page-Events, Page-Versionen/-Log-Einordnung, Asset-Kopie bei Page-Duplikat, Page-Versions-Cleanup | **I4** | CE-PAGE-009, CE-PAGE-012, CE-PAGE-019 | S2 (Konvertierung, `07`) |
| In-App-Notifications, E-Mail-Bündelung (M12), SignalR-Push des Zählers, Recent Visits, Analytics-Export (M11), Suchindex-Consumer (`11`) | **I5** | CE-NOTIF-001…009, CE-HOME-005, CE-ANA-009 | – |
| Webhooks inkl. Deaktivierungs-Mail (M10), Exporte, API-Activity-Log, Webhook-/API-Log-Cleanup, Export-Link-Ablauf | **I6** | CE-WH-001…011, CE-EXP-001/-002, CE-API-003 | – |
| Last-/Ausfalltests der Worker (LT-12, Kill-Tests), Airgap-Prüfung der Mails, Alarme | **I7** | CE-OPS (Rest) | – |
| Erweiterungspunkte §6: C3 (I0), H6 (I0/I5), C1 (I2), F1/F2-Queues (I0 reserviert, W1 genutzt) | je Zeile §6 | `16` §1.4 | – |

---

## 2. Entscheidungen (D06-ADR-01 ff.)

Spalte „ab“ = Inkrement der ersten Umsetzung. Alle Entscheidungen präzisieren `01` ADR-020/-023/-027/-028 und `02` D02-ADR-24/-25; keine widerspricht einer Entscheidung aus `00`, `01` oder `17`.

| ID | Belang | Entscheidung | Alternativen (verworfen) | Begründung | ab |
|---|---|---|---|---|---|
| **D06-ADR-01** | Framework | **Eigene PostgreSQL-Implementierung** nach ADR-020 in `Plane.BuildingBlocks.Messaging`: vier Tabellen (§3.2), drei Hintergrunddienste (`OutboxDispatcherService`, `JobRunnerService`, `RecurringSchedulerService`), `Cronos` für Cron. Fallback bei rotem Spike S12: Wolverine (MIT) hinter denselben Interfaces (`IJobScheduler`, `IEventConsumer<T>`, `IRecurringJobRegistry`). | Hangfire (LGPL, Pro kommerziell), Quartz.NET (nur Cron), MassTransit v9 (kommerziell), RabbitMQ | Bindend durch ADR-020; kein Broker, transaktionale Konsistenz mit Fachdaten, Backup = `pg_dump`, Airgap-tauglich. | I0 |
| **D06-ADR-02** | Zwei asynchrone Wege, eine Regel | (a) **Integration-Event** (Outbox) für Reaktionen **anderer** Module oder späterer Pakete; (b) **transaktionales Job-Enqueue** (`IJobScheduler.EnqueueAsync` innerhalb der Command-Transaktion) für aufgeschobene Arbeit **des eigenen** Moduls (Mails, Seed, Crawl, Export, Metadaten). Ein Command darf beides tun. Synchron in derselben Transaktion bleibt, was das Original zwar asynchron macht, was aber Konsistenz braucht und billig ist (Activity, Subscriber, Mentions, Beschreibungs-/Page-Versionen, PageLog). | alles über Events; alles über Jobs; Celery-Nachbau mit `.delay()` | Hält Modulgrenzen (R5) ein, vermeidet Event-Inflation für rein interne Arbeit und beseitigt die Original-Defekte „Task läuft vor Commit“ (A07 §1.4, E1, WH1). | I0 |
| **D06-ADR-03** | Consumer-Ausführung | Der Dispatcher **fächert** jede Outbox-Nachricht beim Versand in je einen Job `messaging.consume` je registriertem Consumer auf (Queue des Consumers, Dedupe-Schlüssel `evt:{message_id}:{consumer}`); der Job trägt Payload und Kontext als Kopie. Consumer laufen transaktional mit **Inbox** (`inbox_messages (consumer, message_id)`, `ON CONFLICT DO NOTHING`). Nachrichten ohne Consumer werden nur als versandt markiert (`02` §5.2.12). | Dispatcher ruft Consumer direkt; Consumer lesen Outbox selbst | Einheitliche Retry-, Dead-Letter-, Queue- und Pool-Mechanik für Jobs **und** Consumer; Fehler eines Consumers blockiert keinen anderen. | I0 |
| **D06-ADR-04** | Zustellgarantie | **At-least-once** für Jobs und Consumer, **exactly-once-Wirkung** über (a) Inbox für Consumer, (b) `Transactional = true` für reine DB-Jobs (Abschluss-`DELETE` in derselben Transaktion), (c) fachliche Idempotenz für Jobs mit Außenwirkung (Mail: `sent_at` je Log, Webhook: stabile `X-Plane-Delivery`). | exactly-once über verteilte Transaktionen | Mit PostgreSQL allein erreichbar und testbar (S12-Kriterium „Kill -9 verliert keine Nachricht, keine Doppelverarbeitung“). | I0 |
| **D06-ADR-05** | Queues und Worker-Pools | Feste CE-Queues `default`, `notifications`, `emails`, `webhooks`, `exports`, `maintenance`, `realtime`, `indexing`; Paket-Queues nur aus `16` §3.2.5. Jede Host-Instanz verarbeitet die Queues aus **`PlaneWorkerOptions.Queues`/`ExcludeQueues`** (`Plane:Worker:Queues`, Pflicht-Restpunkt `17` §7); Host-Defaults §3.5.6. Damit lassen sich `webhooks`, `exports`, `integrations`, `importers`, `automations` ohne Codeänderung auf eigene Replikate legen. | ein globaler Pool wie Celery (`celery`-Queue) | Original-Defekt WH11 (Webhook-HTTP blockiert den allgemeinen Pool 30 s) entfällt; `16` X9 verlangt benannte Pools. | I0 |
| **D06-ADR-06** | Retry-Policy | `JobRetryPolicy` je Job-Typ; Default **5 Versuche**, exponentiell ab 30 s (Faktor 4, max. 1 h, volle Jitter); Webhook-Zustellung **6 Versuche** (1 + 5 Retries) mit Wartezeit zufällig 0…600 s (= Celery `retry_backoff=600`, `retry_backoff_max=600`, `retry_jitter=True`); Wartungs-Jobs 3 Versuche. Erschöpft → Status `dead` (Dead-Letter) + Metrik + Log `plane.exception`. Unerwartete Ausnahmen gelten als „Retry“, fachlich endgültige Fehler als `JobResult.Fail`. | Original-Verhalten (Exception schlucken, kein Retry, A07 §1.4) | Original verliert Mails/Activities stillschweigend (EM3, N7); Abweichung `DEV-JOB-002`. | I1 |
| **D06-ADR-07** | Scheduler | Cron-Ausdrücke in **UTC** (`Cronos`, 5 Felder), Registrierung im Code (`IRecurringJobRegistry.Register`) **und** optional zur Laufzeit (`IRecurringScheduleStore`, für C3/B7, CE ohne Nutzung). Genau **ein** Leader je Datenbank über `pg_try_advisory_lock(PlaneLocks.Scheduler)` auf einer dedizierten Verbindung; Auslösung = Insert eines Jobs mit Dedupe-Schlüssel `cron:{name}:{occurrence:O}` **und** bedingtes Update `recurring_job_states.last_fired_at` in einer Transaktion (kein Doppellauf auch bei kurzzeitig zwei Leadern). Versäumte Termine: **einmal nachholen** (Celery-Beat-Semantik). | Cron je Worker-Instanz; Quartz-Cluster | Leader-Failover < 30 s und „kein doppelter Cron-Lauf“ (S12) mit Bordmitteln; `14` §4.5 legt `PlaneLocks.Scheduler` fest. | I0 |
| **D06-ADR-08** | Cron-Plan | Alle Beat-Einträge mit **identischer UTC-Zeit** übernommen, außer B3 (Telemetrie, entfällt ADR-004) und B13 (Duplikat von B6, entfällt `14` §4.5); neu: Outbox-/Inbox-/Dead-Letter-Cleanup, Identity-Jobs aus `05`, Cycle-Abschluss-Erkennung (`16` §3.2.4 verlangt `plane.cycle.completed.v1`). Vollständiger Plan §4.2. | Zeiten „entzerren“ | Paritätstest `CronRegistrationTests` vergleicht Original-Zeiten; Abweichung `DEV-OPS-003`. | I1 |
| **D06-ADR-09** | Activity synchron | `IActivityRecorder` (`Plane.WorkItems.Contracts`, Implementierung `Plane.WorkItems`) schreibt Activities **in derselben Transaktion** wie die Fachänderung (`02` D02-ADR-25), inkl. `work_items.updated_at = now`, Assignee-Subscribern und `work_item_mentions`, und veröffentlicht danach **ein** Event `plane.work_item_activity.recorded.v1` je Aufruf. Die Feldlogik ist ein Port von `BG/issue_activities_task.py` (Tabellen §4.5–§4.7). | asynchron wie Original (`issue_activity.delay`) | Activity existiert genau dann, wenn die Änderung committet ist; alles-oder-nichts-Abbruch des Originals (E3, E7) entfällt (`DEV-ACT-001`). | I1 (Gerüst), I2 |
| **D06-ADR-10** | Notifications | Erzeugung **asynchron** im Consumer `ActivityNotificationConsumer` (Queue `notifications`) aus `plane.work_item_activity.recorded.v1`, Algorithmus 1:1 zu `BG/notification_task.py` (A07 §3.2) mit den Korrekturen §4.10; `sender`-Strings, `title` = Activity-`comment`, `data`-JSON mit Python-`str()`-Semantik (`"None"`) **unverändert**, weil das Angular-Frontend die Original-Store-Logik portiert. | Erzeugung synchron im Command | Fan-out auf viele Empfänger gehört nicht in die Request-Latenz; Reihenfolge zur Activity ist durch die Outbox gesichert. | I5 |
| **D06-ADR-11** | E-Mail-Bündelung | Cron `notifications.email_digest` alle 5 min (B1) gruppiert unverarbeitete `email_notification_logs` je **(Empfänger, Work Item)**; je Gruppe ein Job `notifications.send_email_digest` mit **genau den IDs dieser Gruppe** (Korrektur EM2); Sperre über Job-Dedupe statt Redis-Lock; Basis-URL aus Konfiguration (`IPublicUrls.Web`, SEC-31) statt Redis-Origin-Key (Korrektur EM1). Activities aus Automationen erzeugen **keine** E-Mail-Logs (Original versendet sie nie, `DEV-NOTIF-006`). | Redis-Origin/Redis-Lock nachbauen | A07 §5.7 Nr. 3; ADR-004/P4 „so viel wie möglich in PostgreSQL“. | I5 |
| **D06-ADR-12** | Echtzeit-Push | Notifications veröffentlichen `plane.notification.created.v1`; der `RealtimeFanOutConsumer` (Modul `Plane.RealtimeEvents`) läuft auf Queue **`realtime`**, die **nur der JobRunner im Host `Plane.Realtime`** verarbeitet, und ruft dort `IRealtimePublisher` (in-process `IHubContext`, Valkey-Backplane ab 2 Replikas, `14` D14-ADR-21) auf. Live-Event `notification.created` an Gruppe `user:{receiver_id}` mit den Zählern im Format von `GET …/users/notifications/unread/`. | SignalR-Client im Worker; Redis-Publish ohne Hub; Polling | Funktioniert auch im Einzelknoten ohne Valkey (Worker und Realtime sind getrennte Prozesse); AK-D08-35 (< 2 s). | I0 (Gerüst), I5 |
| **D06-ADR-13** | Template-Engine | **Fluid** (Liquid, MIT) nach ADR-027; mechanischer Port jeder Django-Datei unter `TPL/emails/**` nach `MAIL/Templates/<gleicher Pfad>.liquid`; Kontext als `Dictionary<string, object?>` mit den **Original-Variablennamen** (snake_case), damit keine Namensstrategie nötig ist; HTML-Encoder aktiv, Django-`|safe` → `| raw`. Betreffzeilen als Code-Konstanten (`MailSubjects`). | Razor-`HtmlRenderer`, Scriban, RazorLight | Templates bleiben als Dateien 1:1 vergleichbar (G-MAIL, `15` §3.9). | I1 |
| **D06-ADR-14** | Bilder in E-Mails | Externe Bild-URLs der Original-Templates (`media.docs.plane.so`, `plane-marketing.s3…`, `creative-assets.mailinblue.com`, `ik.imagekit.io`) werden durch **gebündelte Dateien** `MAIL/Assets/*.png` ersetzt und per Default als **CID-Inline-Ressourcen** (MimeKit `BodyBuilder.LinkedResources`) eingebettet; Option `Plane:Mail:ImageMode = Inline│Hosted` (`Hosted` → `{WEB_URL}/static/emails/<datei>` über das Gateway). | externe URLs belassen | ADR-004 (keine externen Laufzeitabhängigkeiten); CID funktioniert auch, wenn der Mail-Client die Instanz nicht erreicht (`DEV-MAIL-006`). | I1 |
| **D06-ADR-15** | Webhook-Trigger | Webhooks sind eine **Projektion der Integration-Events**: `WebhookEventConsumer` bildet über eine Trigger-Tabelle (§3.14.2) genau die 24 Original-Auslösestellen (W1…W22, WD1, WD2) ab – Filter auf `EventContext.Origin ∈ {App, V1}` und das Event-Feld `Operation`. Pro geändertem Feld eine Zustellung (Original-Fan-out), Daten = aktueller Stand bei Ausführung (WH3), `deleted` nur für Projekte. Erweiterung für H3/A1/F2 nur über `IWebhookEventSource` (`16` E-08). | Webhooks für alle Änderungen; Aufrufe in den Commands | Vertrag CE-WH-008 1:1; trotzdem keine Webhook-Logik in Fach-Commands. | I6 |
| **D06-ADR-16** | Webhook-Zustellung | Job `webhooks.deliver` je (Webhook, Trigger, Feld) in Queue `webhooks`; Client `webhooks` aus `05` §3.17.2 (SSRF, Pinning, 30 s, keine Redirects, kein Proxy); Signatur `X-Plane-Signature = HexLower(HMACSHA256(secret, body))` über **die gesendeten Bytes**; **HTTP-Status jeder Art = zugestellt** (1:1, WH4); Retry nur bei Transportfehler; nach dem 6. erfolglosen Versuch `is_active=false` + Mail M10. `X-Plane-Delivery` stabil je Zustellung über alle Versuche (Korrektur WH6, `DEV-WH-001`); Logs als JSON (WH9, `DEV-WH-002`). | Retry auch bei 5xx; neue Delivery-ID je Versuch | Vertragstreue für Empfänger, Deaktivierungslogik unverändert; v2-Semantik ist Paket H3. | I6 |
| **D06-ADR-17** | Exporte | Job `exports.work_items` (Queue `exports`, Heartbeat für lange Läufe), Spalten/Reihenfolge/Kopfzeilen/Formel-Schutz wie `API/utils/porters/**`; CSV mit `CsvHelper`, XLSX mit `ClosedXML` (Sheet `Sheet`), JSON mit `System.Text.Json` (Einrückung 2); ZIP über `System.IO.Compression`; Ablage über `IObjectStorage` (privat, kein `public-read`), Download-Link presigned 7 Tage bzw. HMAC-signierte Dateisystem-URL (`14` §3.7.6); Exporttypen über `IExportTypeProvider` (`16` E-16). | EPPlus (kommerziell), MiniExcel | ADR-028; Lizenz-Hygiene; Paritätsgate G-EXPORT (`15`). | I6 |
| **D06-ADR-18** | Cleanup/Retention | Batch-Löschungen per `ExecuteDeleteAsync` in Blöcken à 500 IDs (Server-Cursor wie `process_cleanup_task`), Fristen aus `PlaneRetentionOptions` (`02` §3.15); Hard-Delete löscht zusätzlich die **Objektspeicher-Dateien** hart gelöschter `file_assets` (Korrektur „S3-Objekte werden nie gelöscht“, `DEV-OPS-002`). | Datenbank-Partitionierung; TTL-Index | Original-Kriterien bleiben 1:1, Speicherwachstum wird begrenzt. | I1 |
| **D06-ADR-19** | Automationen | Auto-Archive setzt nur `archived_at` (kein State-Wechsel, ABG-056); **Auto-Close** läuft über `IWorkItemStateChanger` mit `StateChangeOrigin.AutoClose` und erzeugt die Original-Activity-Variante A13; Close-State-Fallback **projektbezogen** (erster State der Gruppe `cancelled` **desselben Projekts**, sonst Projekt überspringen + Warnung; Korrektur `DEV-AUTO-001`); Auswahl per `NOT EXISTS`-Semantik ohne Doppeltreffer und ohne gelöschte Zuordnungen (`DEV-AUTO-002`). | Original-Fallback `State.objects.filter(group="cancelled").first()` (beliebiges Projekt) | Vom Auftraggeber verlangte Korrektur; State-Change-Pipeline ist C1-Andockstelle (`16` §5.9). | I3 |
| **D06-ADR-20** | Akteur und Audit im Hintergrund | Jeder Job/Consumer läuft in einem DI-Scope mit `ICurrentActor` aus `EventContext`/Job-Spalten (`actor_id`, `actor_kind`); Jobs ohne fachlichen Akteur (Cron) laufen als **System-Bot** der Instanz (`users.is_bot = true`, `bot_type = "SYSTEM"` als neuer Wert neben dem Original-Wert `WORKSPACE_SEED` aus `BotTypeEnum`, `username = "plane_system_bot"`, angelegt vom Migrator); Automationen behalten den Original-Akteur `project.created_by`. Audit-Felder werden nie implizit `NULL` (Korrektur A07 §3.8 Punkt 5, `DEV-JOB-003`). | Audit `NULL` im Worker wie Original | `AuditInterceptor` (`02` §3.2.2) braucht immer einen Akteur; `16` D16-ADR-12 (Bot-Akteure). | I0 |
| **D06-ADR-21** | Kausaltiefe | `EventContext.CausationDepth`: Commands aus HTTP-Requests und Cron-Jobs = 0; jedes von einem Consumer/Job ausgelöste Event = Tiefe des auslösenden Kontexts + 1; `> 5` wird **nicht** in die Outbox geschrieben, sondern verworfen + Warnung `plane.worker` + Metrik `plane.outbox.dropped{reason="causation_depth"}` (ABG-053). | keine Begrenzung | Schutz gegen Endlosschleifen späterer Automationen (C3) und Sync-Echos (F2). | I0 |
| **D06-ADR-22** | Payload-Disziplin | Integration-Events tragen IDs, `Operation`, `ChangedFields` und – nur wo Webhooks/Audit es brauchen – `Changes` (Feldname, alter und neuer JSON-Wert der Request-Form), **nie** Entitäten oder Secrets. Jobs tragen ihre Parameter als JSON; personenbezogene Daten nur, wo der Job sie zwingend braucht (Empfänger-E-Mail wird **zur Laufzeit** geladen, nicht gespeichert). | ganze DTOs im Event | `01` §7.15, `16` §3.2.4; Datenschutz; Payload-Größe. | I0 |
| **D06-ADR-23** | Ungenutzter Original-Code | **Nicht portiert:** T2 `export_analytics_to_csv_email`, T24 `issue_task`, T33 `project_invitation` (Template wird für G-MAIL portiert, kein Auslöser wie im Original), T21/T22/T25/T26 Backfills (ADR-003), T47 Telemetrie (ADR-004), `issue_draft.activity.*`-Handler (A35–A37), `restore_related_objects`, `ProjectWebhook`, `Webhook.is_internal`, `EmailNotificationLog.entity/old_value/new_value`. `Webhook.version` (`"v1"`) bleibt als Spalte (H3). | alles portieren | A07 O6; Greenfield. | – |
| **D06-ADR-24** | Entfallene Mails (ADR-008) | M1 Magic-Code, M2/M3 E-Mail-Änderung (`05` D05-ADR-08), M4 Passwort-Reset entfallen samt Templates `emails/auth/magic_signin.html`, `emails/auth/forgot_password.html`, `emails/user/email_updated.html`. M8 Aktivierung wird vom `AccountStateGuardStep` (`05` §3.7.3, Order 350) ausgelöst, M9 von `DeactivateAccountCommand`. | Templates „für später“ behalten | Keycloak übernimmt Login, Passwort und E-Mail-Verifikation. | I1 |

---

## 3. Detaildesign

### 3.1 Bausteine und Projekte

```mermaid
flowchart LR
  subgraph Api["Plane.Api (HTTP)"]
    CMD["Command-Handler<br/>(TransactionBehavior)"] --> REC["IActivityRecorder<br/>(synchron)"]
    CMD --> OI["OutboxInterceptor<br/>(02 §3.2.2 Nr. 5)"]
    CMD --> JS["IJobScheduler<br/>(transaktional)"]
  end
  subgraph PG[("PostgreSQL")]
    OB[(outbox_messages)]
    JB[(jobs)]
    IB[(inbox_messages)]
    RS[(recurring_job_states)]
  end
  OI --> OB
  JS --> JB
  subgraph Worker["Plane.Worker"]
    OD["OutboxDispatcherService"] -->|"messaging.consume je Consumer"| JB
    SCH["RecurringSchedulerService<br/>(Leader, Advisory-Lock)"] -->|"cron:{name}:{occ}"| JB
    JR["JobRunnerService<br/>Queues ≠ realtime"] --> H["IJobHandler / IEventConsumer"]
    H --> IB
    H --> MAIL["IMailSender (MailKit)"]
    H --> HTTP["SSRF-Client webhooks / link-preview"]
    H --> S3["IObjectStorage"]
  end
  OB --> OD
  RS --- SCH
  JB --> JR
  subgraph Rt["Plane.Realtime"]
    JR2["JobRunnerService<br/>Queue realtime"] --> RFC["RealtimeFanOutConsumer"] --> HUB["SignalR-Hub /live/events/"]
  end
  JB --> JR2
  PG -. "LISTEN plane_outbox / plane_jobs" .-> OD & JR & JR2
```

| Projekt / Ordner (relativ zu `funk.`) | Inhalt (Klassen, verbindliche Namen) | ab |
|---|---|---|
| `src/building-blocks/Plane.BuildingBlocks/Messaging/` (Contracts, keine Infrastruktur) | `IIntegrationEvent`, `IDomainEvent`, `IEventConsumer<T>`, `EventContext`, `IJob`, `IJobHandler<TJob>`, `JobContext`, `JobResult`, `JobRetryPolicy`, `IJobScheduler`, `IJobCancellation`, `IRecurringJobRegistry`, `IRecurringScheduleStore`, `IMessagingRegistry`, `FieldChange`, `EventOperations`, `PlaneQueues`, `PlaneLocks`, `JobTypeAttribute` | I0 |
| `MSG/Outbox/` | `OutboxMessage` (Entität, `[OwnedBy("Messaging")]`), `OutboxDispatcherService`, `OutboxWakeup` (`LISTEN plane_outbox`), `OutboxMetrics` | I0 |
| `MSG/Inbox/` | `InboxMessage`, `InboxGuard` (`TryBeginAsync(consumer, messageId)`) | I0 |
| `MSG/Jobs/` | `JobRecord` (Entität), `PostgresJobScheduler : IJobScheduler, IJobCancellation`, `JobClaimer` (SQL §3.5.2), `JobRunnerService`, `JobExecutor`, `JobLeaseReaper`, `JobTypeRegistry`, `ConsumeEventJob` + `ConsumeEventJobHandler`, `JobsWakeup` (`LISTEN plane_jobs`) | I0 |
| `MSG/Scheduling/` | `RecurringJobRegistry`, `RecurringJobState` (Entität), `RecurringSchedulerService`, `SchedulerLeaderElection` (`pg_try_advisory_lock`), `DatabaseRecurringScheduleStore`, `MisfirePolicy` | I0 |
| `MSG/Catalog/` | `EventCatalog` (Liste aller `IIntegrationEvent`-Typen aus den Modul-Registrierungen), `EventCatalogEntry`, `D16MinimumEvents` | I0 |
| `MSG/Options/` | `PlaneWorkerOptions`, `PlaneWorkerOptionsValidator`, `PlaneWorkerOptionsPostConfigure` (Komma-Liste → Array, Host-Defaults) | I0 |
| `MSG/Hosting/` | `MessagingServiceCollectionExtensions.AddPlaneMessaging(IHostApplicationBuilder, HostRole)`, `HostRole { Api, Worker, Realtime, AllInOne, Migrator }` | I0 |
| `MSG/Maintenance/` | `OutboxCleanupJob`, `InboxCleanupJob`, `DeadLetterCleanupJob` | I0 |
| `src/platform/Plane.Platform.Mail/` | `IMailSender`, `SmtpMailSender` (MailKit), `DevSmtpOverride` (Mailpit, `14` §3.2.3), `MailTemplateRenderer` (Fluid), `MailTemplates` (Katalog), `MailSubjects`, `PlainTextFromHtml`, `MailImageResolver`, `SmtpErrorMapper`, `Templates/**.liquid`, `Assets/*.png` | I1 |
| `src/modules/WorkItems/Plane.WorkItems/Activity/` | `WorkItemActivityRecorder : IActivityRecorder`, `ActivityTypeHandlers/*` (27 Handler, §4.5), `FieldTrackers/*` (12 Tracker, §4.6), `MentionExtractor`, `SubscriberMaintenance` | I1/I2 |
| `src/modules/Notifications/Plane.Notifications/` | `Application/Consumers/ActivityNotificationConsumer.cs`, `Application/Jobs/StackEmailNotificationsJob.cs`, `Application/Jobs/SendEmailDigestJob.cs`, `Domain/NotificationRecipientResolver.cs`, `Domain/EmailPreferenceRules.cs`, `Domain/EmailDigestPayloadBuilder.cs`, `Domain/PythonText.cs` | I5 |
| `src/modules/RealtimeEvents/Plane.RealtimeEvents/` | `Application/Consumers/RealtimeFanOutConsumer.cs`, `RealtimeFanOutMap.cs`, `Hub/LiveEventsHub.cs`, `HubRealtimePublisher.cs`; Worker/Api-Seite `QueuedRealtimePublisher.cs` | I0/I5 |
| `src/modules/Webhooks/Plane.Webhooks/` | `Application/Consumers/WebhookEventConsumer.cs`, `Application/Jobs/DeliverWebhookJob.cs`, `Application/Jobs/SendWebhookDeactivationEmailJob.cs`, `Domain/WebhookTriggerMap.cs`, `Domain/WebhookPayloadBuilder.cs`, `Domain/WebhookSigner.cs`, `Sources/*WebhookEventSource.cs` | I6 |
| `src/modules/Exports/Plane.Exports/` | `Application/Jobs/ExportWorkItemsJob.cs`, `Application/Jobs/ExpireExportLinksJob.cs`, `Domain/WorkItemExportColumns.cs`, `Formatters/{Csv,Json,Xlsx}ExportFormatter.cs`, `Domain/SpreadsheetSafeText.cs`, `Sources/WorkItemExportTypeProvider.cs` | I6 |
| `src/hosts/Plane.Worker/` | `Program.cs` (`AddPlaneMessaging(HostRole.Worker)`, `ModuleCatalog`, kein `MapEndpoints`) | I0 |

### 3.2 Datenmodell der Messaging-Infrastruktur

Eigentümer der vier Tabellen ist der Pseudo-Eigentümer `Messaging` (`[OwnedBy("Messaging")]`; nur Klassen in `Plane.BuildingBlocks.Messaging` schreiben sie). `03` übernimmt die Tabellen in die Migration `…_Messaging_Initial` (I0). Spaltennamen sind verbindlich (ABG-053 für `outbox_messages`).

```sql
-- 1) Transaktionale Outbox (geschrieben vom OutboxInterceptor im selben Commit, 02 §3.2.2 Nr. 5)
CREATE TABLE outbox_messages (
  id               uuid        PRIMARY KEY,          -- UUIDv7 = Message-ID
  event_type       text        NOT NULL,             -- "plane.work_item.updated.v1"
  payload          jsonb       NOT NULL,             -- serialisiertes Event (snake_case)
  occurred_at      timestamptz NOT NULL,
  traceparent      text        NULL,                 -- W3C, 01 §7.16
  actor_id         uuid        NULL,                 -- ABG-053
  actor_kind       smallint    NULL,                 -- PrincipalKind: 0 User, 1 ApiKey, 2 App, 3 Bot
  origin           text        NOT NULL,             -- "App" | "V1" | "Space" | "Instance" | "Auth" | "Integrations" | "worker" | StateChangeOrigin-Name
  workspace_id     uuid        NULL,
  project_id       uuid        NULL,
  correlation_id   text        NULL,                 -- Request-/Trace-ID des auslösenden Requests
  causation_depth  int         NOT NULL DEFAULT 0,
  dispatched_at    timestamptz NULL                  -- gesetzt vom Dispatcher
);
CREATE INDEX ix_outbox_pending    ON outbox_messages (id) WHERE dispatched_at IS NULL;
CREATE INDEX ix_outbox_dispatched ON outbox_messages (dispatched_at) WHERE dispatched_at IS NOT NULL;

-- 2) Inbox (Idempotenz je Consumer)
CREATE TABLE inbox_messages (
  consumer      text        NOT NULL,                -- stabiler Consumer-Name, z. B. "notifications.activity"
  message_id    uuid        NOT NULL,
  processed_at  timestamptz NOT NULL,
  PRIMARY KEY (consumer, message_id)
);
CREATE INDEX ix_inbox_processed ON inbox_messages (processed_at);

-- 3) Job-Queue
CREATE TABLE jobs (
  id               uuid        PRIMARY KEY,          -- UUIDv7
  queue            text        NOT NULL,             -- PlaneQueues.* oder reservierte Paket-Queue (16 §3.2.5)
  job_type         text        NOT NULL,             -- stabiler Name aus [JobType("…")]
  payload          jsonb       NOT NULL,
  status           smallint    NOT NULL DEFAULT 0,   -- 0 pending, 1 running, 4 dead (Erfolg = Zeile gelöscht)
  priority         smallint    NOT NULL DEFAULT 0,   -- reserviert, CE nutzt 0
  run_at           timestamptz NOT NULL,
  attempts         int         NOT NULL DEFAULT 0,
  max_attempts     int         NOT NULL,
  dedupe_key       text        NULL,
  locked_by        text        NULL,                 -- "<host>/<pid>/<runner-guid>"
  locked_until     timestamptz NULL,
  last_error       text        NULL,                 -- gekürzt auf 4 000 Zeichen, redigiert
  created_at       timestamptz NOT NULL,
  dead_at          timestamptz NULL,
  -- Kontext (wie outbox_messages, D06-ADR-20/-21)
  actor_id uuid NULL, actor_kind smallint NULL, origin text NOT NULL, workspace_id uuid NULL, project_id uuid NULL,
  correlation_id text NULL, causation_depth int NOT NULL DEFAULT 0, traceparent text NULL
);
CREATE INDEX ix_jobs_ready ON jobs (queue, priority DESC, run_at) WHERE status = 0;
CREATE INDEX ix_jobs_lease ON jobs (locked_until) WHERE status = 1;
CREATE UNIQUE INDEX ux_jobs_dedupe ON jobs (dedupe_key) WHERE dedupe_key IS NOT NULL AND status IN (0, 1);
CREATE INDEX ix_jobs_dead  ON jobs (dead_at) WHERE status = 4;

-- 4) Zustand der wiederkehrenden Jobs (Code-Registrierung und dynamische Definitionen)
CREATE TABLE recurring_job_states (
  name            text        PRIMARY KEY,           -- "notifications.email_digest"
  source          text        NOT NULL,              -- "code" | "dynamic" (IRecurringScheduleStore, §6)
  cron_utc        text        NOT NULL,
  job_type        text        NOT NULL,
  queue           text        NOT NULL,
  payload         jsonb       NOT NULL DEFAULT '{}',
  enabled         bool        NOT NULL DEFAULT true,
  last_fired_at   timestamptz NULL,                  -- Termin (occurrence), nicht Ausführungszeit
  next_fire_at    timestamptz NULL,
  updated_at      timestamptz NOT NULL
);
```

Regeln: (1) `jobs.dedupe_key` ist nur eindeutig, solange ein Job **offen** ist (`pending`/`running`); nach Erfolg darf derselbe Schlüssel erneut eingereiht werden (Recent Visits, Link-Crawl). (2) Erfolgreiche Jobs werden **gelöscht**; Historie liefern Metriken und Logs (`plane.worker`). (3) Tote Jobs (`status = 4`) bleiben `DeadLetterRetentionDays` (30) zur Analyse; `plane-cli jobs requeue --id|--type` setzt sie zurück auf `pending` (Nachtrag `14` §3.22). (4) Beim Schreiben eines Jobs/einer Outbox-Zeile innerhalb einer Transaktion wird `SELECT pg_notify('plane_jobs', <queue>)` bzw. `pg_notify('plane_outbox', '')` in derselben Transaktion ausgeführt – PostgreSQL stellt die Benachrichtigung erst beim Commit zu.

### 3.3 Outbox und Dispatcher

**Schreiben:** ausschließlich durch den `OutboxInterceptor` (`02` §3.2.2 Nr. 5) aus `IHasDomainEvents.DequeueIntegrationEvents()`; Kontextspalten aus `ICurrentActor`/`ICommandOrigin`. Vor dem Insert prüft der Interceptor die Kausaltiefe (D06-ADR-21). Events entstehen dadurch **nur bei Commit** (Original-Defekte E1/WH1 entfallen, `DEV-JOB-001`).

**Versand (`OutboxDispatcherService`, Host-Rollen Worker/AllInOne, beliebig viele Instanzen parallel):**

1. Warten auf `NOTIFY plane_outbox` oder `OutboxPollIntervalMilliseconds` (1 000 ms).
2. In **einer** Transaktion: `SELECT id, event_type, payload, … FROM outbox_messages WHERE dispatched_at IS NULL ORDER BY id LIMIT @batch FOR UPDATE SKIP LOCKED` (`@batch` = `OutboxBatchSize`, 200).
3. Je Nachricht: Consumer-Liste aus `EventCatalog.ConsumersFor(event_type)` (Registrierung über `IModule.RegisterMessaging`, nur Module des Host-Katalogs **aller** Hosts – die Registry ist host-unabhängig, siehe §3.5.6); je Consumer `INSERT INTO jobs (…, queue = consumer.Queue, job_type = 'messaging.consume', dedupe_key = 'evt:' || id || ':' || consumer.Name, payload = {message_id, event_type, consumer, event, context}) ON CONFLICT DO NOTHING`; Kontextspalten 1:1 übernehmen.
4. `UPDATE outbox_messages SET dispatched_at = now() WHERE id = ANY(@ids)`; `pg_notify('plane_jobs', <queue>)` je betroffener Queue; Commit.
5. Metriken: `plane.outbox.dispatch.duration` (je `event_type`), `plane.outbox.lag` (Nachtrag, `dispatched_at − occurred_at`), `plane.outbox.pending` (Gauge, alle 15 s per `count(*)` mit Index).

Reihenfolge: Nachrichten werden in UUIDv7-Reihenfolge eingereiht; eine **globale** Verarbeitungsreihenfolge wird nicht garantiert (das Original garantiert sie ebenfalls nicht). Consumer, die Reihenfolge brauchen, prüfen sie fachlich (z. B. `ActivityNotificationConsumer` liest den Ist-Zustand, nicht den Event-Zustand). Bereinigung: Cron `messaging.outbox_cleanup` löscht versandte Zeilen älter als `OutboxRetentionHours` (24 h).

```mermaid
sequenceDiagram
  autonumber
  participant B as Browser
  participant A as Plane.Api (UpdateWorkItemHandler)
  participant DB as PostgreSQL
  participant D as Worker: OutboxDispatcher
  participant R as Worker: JobRunner (notifications)
  participant RT as Realtime: JobRunner (realtime)
  participant H as SignalR-Hub
  B->>A: PATCH /api/workspaces/{slug}/projects/{pid}/issues/{id}/ {"state_id": …}
  A->>DB: BEGIN; UPDATE work_items …; IActivityRecorder → INSERT work_item_activities (A6), UPDATE work_items.updated_at
  A->>DB: INSERT outbox_messages (work_item.updated, work_item.state_changed, work_item_activity.recorded); pg_notify('plane_outbox')
  A->>DB: COMMIT
  A-->>B: 204
  DB-->>D: NOTIFY plane_outbox
  D->>DB: SELECT … FOR UPDATE SKIP LOCKED; INSERT jobs (messaging.consume × Consumer); UPDATE dispatched_at; COMMIT
  DB-->>R: NOTIFY plane_jobs 'notifications'
  R->>DB: Claim (§3.5.2); BEGIN; INSERT inbox_messages; ActivityNotificationConsumer → INSERT notifications, email_notification_logs, outbox (notification.created); DELETE job; COMMIT
  D->>DB: notification.created → INSERT jobs (queue realtime)
  DB-->>RT: NOTIFY plane_jobs 'realtime'
  RT->>H: RealtimeFanOutConsumer → IHubContext.Clients.Group("user:{id}").SendAsync("event", …)
  H-->>B: notification.created {unread …}
```

### 3.4 Consumer und Inbox

| Regel | Festlegung |
|---|---|
| Registrierung | `IModule.RegisterMessaging(IMessagingRegistry m)`: `m.AddConsumer<TEvent, TConsumer>(name: "notifications.activity", queue: PlaneQueues.Notifications)`; Name **stabil** (Inbox-Schlüssel), Schema `<modul>.<zweck>` in `snake_case`. |
| Ausführung | Job `messaging.consume` → `ConsumeEventJobHandler`: neuer DI-Scope, `ModuleScope` = Assembly des Consumers (R3), `ICurrentActor`/`ICommandOrigin` aus dem Kontext (`Origin = "worker"`, `CausationDepth = ctx + 1` für ausgelöste Events), dann `BEGIN` → `InboxGuard.TryBeginAsync(consumer, message_id)` (`INSERT … ON CONFLICT DO NOTHING`; 0 Zeilen = bereits verarbeitet → `JobResult.Success`) → `consumer.HandleAsync(event, ctx)` → `SaveChangesAsync` → Job-Zeile löschen → `COMMIT`. |
| Verschachtelte Commands | Ein Consumer darf Commands **seines** Moduls über `ISender` senden; sie laufen in der offenen Transaktion (`02` §3.19 „Verschachtelte Commands“). |
| Außenwirkung | Consumer machen **keine** HTTP-/SMTP-Aufrufe; sie reihen dafür Jobs transaktional ein (Webhook-Zustellung, Mail). |
| Deserialisierung | `System.Text.Json` mit `PlaneJsonContext` (snake_case); unbekannte Felder ignoriert (additive Event-Evolution, `15` EP-T11). Unbekannter `event_type` → `JobResult.Fail("unknown event type")` (Dead-Letter). |
| Bereinigung | Cron `messaging.inbox_cleanup` löscht `processed_at < now − InboxRetentionDays` (7 Tage); das Fenster ist größer als jede Retry-Kette (max. ≈ 2 h). |
| Test-Host | `PlaneApiFactory` registriert `InlineOutboxDispatcher` (`IOutboxDrainer`, `15` §3.3.1); `factory.DrainOutboxAsync()` führt Dispatcher **und** alle dadurch eingereihten `messaging.consume`-Jobs synchron aus (Endlosschutz: max. 10 Runden). |

### 3.5 Job-Queue, Retry, Dead-Letter, Queues und Worker-Pools

#### 3.5.1 Job-Vertrag

Ein Job ist ein unveränderlicher `record` mit den Parametern und den statischen Metadaten `JobType`, `Queue`, `RetryPolicy`, `Transactional`; ausgeführt wird er von genau einem `IJobHandler<TJob>` (Skelett §5.2). `IJobScheduler.EnqueueAsync(job, runAt, dedupeKey)` schreibt **innerhalb** einer offenen Command-Transaktion über den `PlaneDbContext` (Commit mit der Fachänderung), **außerhalb** über eine eigene Verbindung sofort. `IJobCancellation.CancelAsync(dedupeKey)` löscht einen noch nicht gestarteten Job (Nachtrag zu `01` §5.5, additiv in einem eigenen Interface).

#### 3.5.2 Claim, Lease, Abschluss

```sql
-- JobClaimer.ClaimAsync(@queue, @free, @worker, @lease)
UPDATE jobs SET status = 1, attempts = attempts + 1, locked_by = @worker, locked_until = now() + @lease
WHERE id IN (
  SELECT id FROM jobs
  WHERE queue = @queue AND status = 0 AND run_at <= now()
  ORDER BY priority DESC, run_at, id
  LIMIT @free
  FOR UPDATE SKIP LOCKED)
RETURNING *;
```

| Schritt | Verhalten |
|---|---|
| Schleife | je verarbeiteter Queue ein `QueueLoop` mit `SemaphoreSlim(Concurrency[queue])`; geweckt durch `NOTIFY plane_jobs` (Payload = Queue) oder `PollIntervalMilliseconds` (2 000 ms); Claim nur für freie Slots (`ClaimBatchSize` max. 20). |
| Ausführung | `JobExecutor`: neuer DI-Scope, `ModuleScope` aus Handler-Assembly, `ICurrentActor` aus Spalten (fehlt der Akteur → System-Bot, D06-ADR-20), `Activity` (`ActivitySource "Plane.Messaging"`, Elternkontext aus `traceparent`), Timeout = `LeaseSeconds − 10 s` als `CancellationToken`. |
| Heartbeat | Handler mit `JobContext.Heartbeat()` (Export, Hard-Delete) verlängern `locked_until` alle `LeaseSeconds / 3`. |
| Erfolg | `DELETE FROM jobs WHERE id = @id AND locked_by = @worker` (bei `Transactional = true` in der Handler-Transaktion). |
| Retry | `UPDATE jobs SET status = 0, run_at = now() + policy.NextDelay(attempts), locked_by = NULL, locked_until = NULL, last_error = @err`; Metrik `plane.jobs.executed{outcome="retry"}`. |
| Dead-Letter | `attempts >= max_attempts` oder `JobResult.Fail` → `status = 4, dead_at = now()`; Log `plane.exception` (Level Error, `job_type`, `job_id`, gekürzte Ursache), Metrik `outcome="dead_letter"`, optional Hook `IJobDeadLetterHandler<TJob>`. |
| Absturz (Kill -9) | `JobLeaseReaper` (alle `ReaperIntervalSeconds` = 30 s, jede Instanz): `UPDATE jobs SET status = 0, locked_by = NULL WHERE status = 1 AND locked_until < now()`; der Versuch zählt (attempts bereits erhöht). |
| Herunterfahren | `IHostApplicationLifetime.ApplicationStopping` → keine neuen Claims, laufende Jobs bekommen `ShutdownGraceSeconds` (30 s), danach Abbruch per Token; nicht beendete Jobs fallen über den Lease zurück. |

#### 3.5.3 Retry-Policies

| Policy (`JobRetryPolicy.*`) | Versuche | Wartezeit vor Versuch n+1 | Verwendung |
|---|---|---|---|
| `Default` | 5 | `random(0, min(3600, 30 · 4^(n−1)))` s (volle Jitter) | Consumer, Mail, Crawl, Metadaten, Seed, Export |
| `Webhook` | 6 | `random(0, 600)` s (Celery-Äquivalent) | `webhooks.deliver` |
| `Maintenance` | 3 | 5 min, 30 min | Cleanup-/Retention-Jobs (Cron holt ohnehin am Folgetag nach) |
| `Once` | 1 | – | God-Mode-Testmail entfällt als Job; `plane-cli`-Einmaljobs |

#### 3.5.4 Queues

| Queue (`PlaneQueues`) | Inhalt | Concurrency-Default | Host-Default |
|---|---|---|---|
| `default` | Seed, Link-Crawl, Asset-Metadaten, Asset-Kopie, Recent Visits, Avatar-Download, Soft-Delete-Kaskade (Deferred), Consumer ohne eigene Queue | 8 | Worker |
| `notifications` | `ActivityNotificationConsumer`, `StackEmailNotificationsJob` | 8 | Worker |
| `emails` | alle Mail-Jobs (M5, M7–M12) | 4 | Worker |
| `webhooks` | `WebhookEventConsumer`, `webhooks.deliver`, Deaktivierungs-Mail-Auslösung | 16 | Worker |
| `exports` | `exports.work_items`, `exports.analytics_email`; mit D5 geteilt (`16` §3.2.5) | 2 | Worker |
| `maintenance` | alle Cleanup-, Retention-, Hard-Delete-, Automations- und Identity-Cron-Jobs | 1 | Worker |
| `realtime` | `RealtimeFanOutConsumer` | 16 | **nur Realtime** |
| `indexing` | `SearchIndexingConsumer` (`11`), später G1/B6 | 4 | Worker |
| reserviert (`16` §3.2.5) | `integrations`, `importers`, `automations`, `sla`, `scheduled_comms`, `pii`, `agents`, `snapshots` | 4 | Worker (sobald ein Paket registriert) |

#### 3.5.5 Options-Klasse `PlaneWorkerOptions` (Abschnitt `Plane:Worker`, Projekt `Plane.BuildingBlocks.Messaging`, ab I0)

| Eigenschaft | Typ = Default | Bedeutung / Validierung |
|---|---|---|
| `Queues` | `string[]` = Host-Default (§3.5.6) | verarbeitete Queues; `"*"` = alle registrierten; ENV als Array (`Plane__Worker__Queues__0=webhooks`) **oder** Komma-Liste (`Plane__Worker__Queues=webhooks,emails`); unbekannter Name → Startfehler, außer reservierte Paket-Queue (Warnung `plane.config`) |
| `ExcludeQueues` | `string[]` = Host-Default | von `"*"` abgezogen |
| `Concurrency` | `Dictionary<string,int>` = Tabelle §3.5.4 | 1…256 je Queue |
| `PollIntervalMilliseconds` | `int` = 2000 | 100…60 000 (Sicherheitsnetz ohne `LISTEN`) |
| `ClaimBatchSize` | `int` = 20 | 1…500 |
| `LeaseSeconds` | `int` = 300 | 30…3 600 |
| `ReaperIntervalSeconds` | `int` = 30 | 5…600 |
| `ShutdownGraceSeconds` | `int` = 30 | 0…600 |
| `UseListenNotify` | `bool` = `true` | `false` bei Transaktions-Pooling (PgBouncer), dann nur Polling |
| `Scheduler.Enabled` | `bool` = Host-Default | Teilnahme an der Leader-Wahl |
| `Scheduler.TickSeconds` | `int` = 10 | 1…60; Leader prüft fällige Termine |
| `Scheduler.LeaderRetrySeconds` | `int` = 10 | Nicht-Leader versuchen den Lock alle n s (Failover < 30 s) |
| `Outbox.Enabled` | `bool` = Host-Default | Dispatcher aktiv |
| `Outbox.BatchSize` | `int` = 200 | 1…5 000 |
| `Outbox.PollIntervalMilliseconds` | `int` = 1000 | 100…60 000 |
| `Outbox.RetentionHours` | `int` = 24 | 1…720 |
| `InboxRetentionDays` | `int` = 7 | 1…90 |
| `DeadLetterRetentionDays` | `int` = 30 | 1…365 |

#### 3.5.6 Host-Defaults und Pool-Beispiele

| Host (`HostRole`) | `Queues` | `ExcludeQueues` | `Scheduler.Enabled` | `Outbox.Enabled` |
|---|---|---|---|---|
| `Plane.Api` | `[]` (kein JobRunner, nur Enqueue) | – | `false` | `false` |
| `Plane.Worker` | `["*"]` | `["realtime"]` | `true` | `true` |
| `Plane.Realtime` | `["realtime"]` | – | `false` | `false` |
| `Plane.AllInOne` | `["*"]` | – | `true` | `true` |
| `Plane.Migrator` | `[]` | – | `false` | `false` |

Beispiel eigener Webhook-Pool (Compose/Helm, `14` §6.1): Replika `worker` mit `Plane__Worker__ExcludeQueues=realtime,webhooks`, Replika `worker-webhooks` mit `Plane__Worker__Queues=webhooks`, `Plane__Worker__Scheduler__Enabled=false`, `Plane__Worker__Outbox__Enabled=false`. Eine Queue ohne verarbeitende Instanz wird durch die Metrik `plane.jobs.oldest_pending_age_seconds{queue}` (Nachtrag `14` §3.19.2) und den Alarm „> 600 s“ sichtbar; eine Startprüfung ist prozessübergreifend nicht möglich.

### 3.6 Scheduler (Cron, Leader)

1. **Registrierung:** `IModule.RegisterMessaging` → `m.Recurring.Register<TJob>(name, cronUtc)`; beim Start schreibt jede Instanz mit `Scheduler.Enabled` die Code-Definitionen idempotent nach `recurring_job_states` (`source = 'code'`; geänderte Cron-Ausdrücke werden überschrieben, entfernte Namen auf `enabled = false` gesetzt).
2. **Leader-Wahl:** `SchedulerLeaderElection` öffnet eine **eigene, langlebige** Npgsql-Verbindung (`Keepalive=10`, `Tcp Keepalive=true`) und ruft `SELECT pg_try_advisory_lock(@PlaneLocks.Scheduler)`; Nicht-Leader wiederholen alle `LeaderRetrySeconds`. Bricht die Verbindung ab, gibt PostgreSQL den Lock frei; der Leader prüft vor jedem Tick `SELECT 1` und tritt bei Fehler zurück. Gauge `plane.scheduler.leader{instance}` = 1/0.
3. **Tick (nur Leader, alle `TickSeconds`):** für jede aktive Definition `next = cron.GetNextOccurrence(last_fired_at ?? updated_at, UTC)`; ist `next <= now`: in **einer** Transaktion `UPDATE recurring_job_states SET last_fired_at = @occ, next_fire_at = @following WHERE name = @n AND (last_fired_at IS NULL OR last_fired_at < @occ)` – nur bei 1 betroffener Zeile `INSERT INTO jobs (…, dedupe_key = 'cron:' || name || ':' || @occ, origin = 'worker', actor = System-Bot) ON CONFLICT DO NOTHING`.
4. **Versäumte Termine (`MisfirePolicy.FireOnceNow`):** liegen mehrere Termine in der Vergangenheit (Stillstand), wird **ein** Job mit dem jüngsten versäumten Termin erzeugt (Celery-Beat-Verhalten bei `DatabaseScheduler`).
5. **Kein Doppellauf:** auch bei kurzzeitig zwei Leadern (Netzwerk-Partition) verhindert die bedingte `UPDATE`-Klausel einen zweiten Job für denselben Termin; der Dedupe-Index verhindert parallele offene Jobs.

```mermaid
sequenceDiagram
  autonumber
  participant W1 as Worker 1 (Leader)
  participant W2 as Worker 2
  participant PG as PostgreSQL
  W1->>PG: pg_try_advisory_lock(PlaneLocks.Scheduler) = true
  W2->>PG: pg_try_advisory_lock(...) = false (Retry alle 10 s)
  loop alle 10 s
    W1->>PG: fällige Definitionen
    W1->>PG: BEGIN; UPDATE recurring_job_states … WHERE last_fired_at < @occ; INSERT jobs (cron:{name}:{occ}); COMMIT
  end
  Note over W1: kill -9
  PG-->>PG: Session-Ende → Lock frei
  W2->>PG: pg_try_advisory_lock(...) = true (≤ 10 s)
  W2->>PG: Tick: bereits gefeuerte Termine werden durch last_fired_at übersprungen
```

`PlaneLocks` (Konstanten in `Plane.BuildingBlocks/Messaging/PlaneLocks.cs`, `bigint`): `Scheduler = 0x504C_4E00_0001`, `InstanceBootstrap = 0x504C_4E00_0002` (`05` S-16), `Migrations = 0x504C_4E00_0003` (`14` §3.15); weitere Werte nur additiv.

### 3.7 EventContext, Akteur, Herkunft, Kausaltiefe

| Feld (`EventContext`, Signatur `16` §5.11) | Quelle beim Schreiben | Rekonstruktion im Consumer |
|---|---|---|
| `MessageId`, `EventType`, `OccurredAt`, `TraceParent` | Interceptor (`IIdGenerator`, `IClock`, `Activity.Current`) | Spalten `id`, `event_type`, `occurred_at`, `traceparent` |
| `ActorId`, `ActorKind` | `ICurrentActor` (Request-Prinzipal, im Worker Job-Akteur) | `actor_id`, `actor_kind` → `ICurrentActor` des Consumer-Scopes |
| `Origin` | `ICommandOrigin`: Oberfläche des Requests (`App`, `V1`, `Space`, `Instance`, `Auth`, `Integrations`), in Jobs/Consumern `worker`; der `WorkItemStateChanger` setzt zusätzlich `StateChangeOrigin` in sein Event | `origin` |
| `WorkspaceId`, `ProjectId` | `IRequestScope` bzw. Event-Payload | `workspace_id`, `project_id` |
| `CorrelationId` | `HttpContext.TraceIdentifier` bzw. `X-Request-Id` (Gateway); in Jobs = CorrelationId des auslösenden Kontexts | `correlation_id` |
| `CausationDepth` | Request/Cron = 0; Consumer/Job = Tiefe des Kontexts + 1 | `causation_depth` |

`ICommandOrigin` (scoped, `Plane.BuildingBlocks/Messaging/ICommandOrigin.cs`): `string Origin`, `int CausationDepth`, `string? CorrelationId`; gesetzt von `SurfaceConventions` (Api) bzw. `JobExecutor` (Worker). Der `OutboxInterceptor` (02) liest ausschließlich diese Schnittstelle.

### 3.8 Event-Katalog

**Regeln** (ergänzen `01` §7.15, `02` §3.1.2, `16` §3.2.4): Name `plane.<aggregat>.<ereignis>.v<n>`, C#-Typ `<Aggregat><Ereignis>V<n>` in `Plane.<Eigentümer>.Contracts/Events/`; nach Merge unveränderlich, Änderungen nur additiv (neues optionales Feld) oder als `.v2` parallel (`15` EP-T11). Payload-Felder in `snake_case`; IDs als UUID-Strings; `Operation` (Konstanten `EventOperations`) unterscheidet die Auslöser eines Events (Webhook-Projektion §3.14.2, Audit E6); `ChangedFields` = Feldnamen der Request-Form; `Changes` = `FieldChange(field, old_value, new_value)` mit JSON-Werten (Diff-Regel §3.14.3). Reservierte Namensräume aus `16` §3.2.4 verwendet die CE nicht (`No_CE_event_uses_reserved_prefix`). Die Tabelle ist aus `_data/06-event-catalog.json` erzeugt; Spalte „Status“: *aktiv* = CE löst aus; *reserviert* = Klasse existiert (Snapshot), CE löst nicht aus; *Webhook* = Quelle einer v1-Webhook-Zustellung; *additiv zu 16* = nicht in der Mindestmenge von `16` §3.2.4 (zulässige Ergänzung, O-16-08).

| Event-Typ | C#-Typ | Eigentümer | Produzenten (Commands/Jobs) | Payload (zusätzlich zu `EventContext`) | ab | CE-Consumer | Paket-Consumer (`16`) | Status |
|---|---|---|---|---|---|---|---|---|
| `plane.identity.user_provisioned.v1` | `UserProvisionedV1` | `Identity` | UserProvisioningPipeline (nach jedem Login-Durchlauf, 05 §3.7) | UserId, IsNewUser | I0 | – | E3, E6, E7 | aktiv |
| `plane.identity.user_deactivated.v1` | `UserDeactivatedV1` | `Identity` | DeactivateAccountCommand (CE-PROF-005) | UserId | I1 | – | E3, E6 | aktiv |
| `plane.identity.user_disabled_in_idp.v1` | `UserDisabledInIdpV1` | `Identity` | IdpUserStateSyncJob (05 §3.10) | UserId, IdpState (`disabled`│`deleted`) | I1 | – | E3, E6, E7 | aktiv |
| `plane.identity.<sicherheitsereignis>.v1` | `IdentitySecurityEventV1 (je Ereignis aus 05 §3.17.8)` | `Identity` | Sicherheitsereignisse 05 §3.17.8, nur bei `Plane:Audit:Enabled=true` (Default `false`) | EventName, UserId?, App?, Reason? | I0 | – | E6 | aktiv (hinter Schalter) |
| `plane.instance_configuration.updated.v1` | `InstanceConfigurationUpdatedV1` | `Instance` | UpdateInstanceConfigurationCommand, DisableEmailFeatureCommand | Keys (nur Namen, nie Werte) | I1 | – | E7 | aktiv |
| `plane.workspace.created.v1` | `WorkspaceCreatedV1` | `Workspaces` | CreateWorkspaceCommand | WorkspaceId, Slug, OwnerId | I0 | – | E6, B1 | aktiv · additiv zu 16 |
| `plane.workspace.updated.v1` | `WorkspaceUpdatedV1` | `Workspaces` | UpdateWorkspaceCommand, SetWorkspaceLogoCommand | WorkspaceId, Operation, Changes: FieldChange[] (Feld, alt, neu; nur geänderte Request-Felder) | I1 | – | E6 | aktiv · additiv zu 16 |
| `plane.workspace.deleted.v1` | `WorkspaceDeletedV1` | `Workspaces` | DeleteWorkspaceCommand | WorkspaceId | I1 | RecentVisitCleanupConsumer (I5) | E6 | aktiv · additiv zu 16 |
| `plane.workspace_member.added.v1` | `WorkspaceMemberAddedV1` | `Workspaces` | AcceptWorkspaceInvitationCommand, JoinAcceptedInvitationsStep (05), CreateWorkspaceCommand (Ersteller als Admin) | WorkspaceId, UserId, Role (20/15/5), OldRole? (nur updated) | I1 | – | E3, E5, E6, B1, F2 | aktiv |
| `plane.workspace_member.updated.v1` | `WorkspaceMemberUpdatedV1` | `Workspaces` | UpdateWorkspaceMemberCommand (Rolle) | WorkspaceId, UserId, Role (20/15/5), OldRole? (nur updated) | I1 | – | E3, E5, E6, B1, F2 | aktiv |
| `plane.workspace_member.removed.v1` | `WorkspaceMemberRemovedV1` | `Workspaces` | RemoveWorkspaceMemberCommand, LeaveWorkspaceCommand, DeactivateAccountCommand | WorkspaceId, UserId, Role (20/15/5), OldRole? (nur updated) | I1 | – | E3, E5, E6, B1, F2 | aktiv |
| `plane.project.created.v1` | `ProjectCreatedV1` | `Projects` | CreateProjectCommand (App/V1), WorkspaceSeedJob | ProjectId, WorkspaceId, Operation (`create`│`seed`) | I0 | WebhookEventConsumer (I6) | E5, E6, B1, F2 | aktiv · Webhook |
| `plane.project.updated.v1` | `ProjectUpdatedV1` | `Projects` | UpdateProjectCommand (`update`), SetProjectCoverCommand (`cover`), UpdateProjectAutomationCommand (`update`, gleicher PATCH-Endpunkt) | ProjectId, WorkspaceId, Operation, Changes: FieldChange[] (Feld, alt, neu; nur geänderte Request-Felder) | I1 | WebhookEventConsumer (I6) | E6, F2 | aktiv · Webhook |
| `plane.project.archived.v1` | `ProjectArchivedV1` | `Projects` | ArchiveProjectCommand | ProjectId, WorkspaceId | I1 | – | E6, B1 | aktiv |
| `plane.project.unarchived.v1` | `ProjectUnarchivedV1` | `Projects` | RestoreProjectCommand | ProjectId, WorkspaceId | I1 | – | E6 | aktiv · additiv zu 16 |
| `plane.project.deleted.v1` | `ProjectDeletedV1` | `Projects` | DeleteProjectCommand (App/V1) | ProjectId, WorkspaceId | I1 | WebhookEventConsumer (I6), RecentVisitCleanupConsumer (I5) | E5, E6, F2 | aktiv · Webhook |
| `plane.project_member.added.v1` | `ProjectMemberAddedV1` | `Projects` | AddProjectMembersCommand, JoinProjectCommand, AcceptProjectInvitationCommand, CreateProjectCommand (Ersteller) | ProjectId, WorkspaceId, UserId, Role, OldRole? (nur updated) | I1 | – | E3, E5, E6, B1, F2 | aktiv |
| `plane.project_member.updated.v1` | `ProjectMemberUpdatedV1` | `Projects` | UpdateProjectMemberCommand | ProjectId, WorkspaceId, UserId, Role, OldRole? (nur updated) | I1 | – | E3, E5, E6, B1, F2 | aktiv |
| `plane.project_member.removed.v1` | `ProjectMemberRemovedV1` | `Projects` | RemoveProjectMemberCommand, LeaveProjectCommand | ProjectId, WorkspaceId, UserId, Role, OldRole? (nur updated) | I1 | – | E3, E5, E6, B1, F2 | aktiv |
| `plane.state.created.v1` | `StateCreatedV1` | `Projects` | CreateStateCommand / UpdateStateCommand (inkl. MarkStateDefaultCommand) / DeleteStateCommand | StateId, ProjectId, WorkspaceId | I1 | RealtimeFanOutConsumer (I5, Gruppe `project:{id}`) | F2, A17, H6 | aktiv |
| `plane.state.updated.v1` | `StateUpdatedV1` | `Projects` | CreateStateCommand / UpdateStateCommand (inkl. MarkStateDefaultCommand) / DeleteStateCommand | StateId, ProjectId, WorkspaceId, ChangedFields | I1 | RealtimeFanOutConsumer (I5, Gruppe `project:{id}`) | F2, A17, H6 | aktiv |
| `plane.state.deleted.v1` | `StateDeletedV1` | `Projects` | CreateStateCommand / UpdateStateCommand (inkl. MarkStateDefaultCommand) / DeleteStateCommand | StateId, ProjectId, WorkspaceId | I1 | RealtimeFanOutConsumer (I5, Gruppe `project:{id}`) | F2, A17, H6 | aktiv |
| `plane.label.created.v1` | `LabelCreatedV1` | `Projects` | CreateLabelCommand, BulkCreateLabelsCommand / UpdateLabelCommand / DeleteLabelCommand (02 §5.2.12) | LabelId, ProjectId, WorkspaceId | I1 | RealtimeFanOutConsumer (I5, Gruppe `project:{id}`) | F2, A17, H6 | aktiv |
| `plane.label.updated.v1` | `LabelUpdatedV1` | `Projects` | CreateLabelCommand, BulkCreateLabelsCommand / UpdateLabelCommand / DeleteLabelCommand (02 §5.2.12) | LabelId, ProjectId, WorkspaceId, ChangedFields | I1 | RealtimeFanOutConsumer (I5, Gruppe `project:{id}`) | F2, A17, H6 | aktiv |
| `plane.label.deleted.v1` | `LabelDeletedV1` | `Projects` | CreateLabelCommand, BulkCreateLabelsCommand / UpdateLabelCommand / DeleteLabelCommand (02 §5.2.12) | LabelId, ProjectId, WorkspaceId | I1 | RealtimeFanOutConsumer (I5, Gruppe `project:{id}`) | F2, A17, H6 | aktiv |
| `plane.estimate.created.v1` | `EstimateCreatedV1` | `Projects` | CreateEstimateCommand | EstimateId, ProjectId, WorkspaceId | I1 | – | A11, F2 | aktiv · additiv zu 16 |
| `plane.estimate.updated.v1` | `EstimateUpdatedV1` | `Projects` | UpdateEstimateCommand, Create/Update/DeleteEstimatePointCommand | EstimateId, ProjectId, WorkspaceId, ChangedFields | I1 | – | A11, F2 | aktiv |
| `plane.estimate.deleted.v1` | `EstimateDeletedV1` | `Projects` | DeleteEstimateCommand | EstimateId, ProjectId, WorkspaceId | I1 | – | A11 | aktiv · additiv zu 16 |
| `plane.work_item.created.v1` | `WorkItemCreatedV1` | `WorkItems` | CreateWorkItemCommand (`create`), UpsertWorkItemCommand (`put_create`), ConvertDraftToWorkItemCommand (`draft_convert`), IWorkItemCommands aus Intake (`intake_create`) und Space-Intake (`space_intake_create`), WorkspaceSeedJob (`seed`) | WorkItemId, ProjectId, WorkspaceId, Operation | I2 | WebhookEventConsumer (I6), SearchIndexingConsumer (I5) | C3, E6, F2, G1, H3, H6, A12 | aktiv · Webhook |
| `plane.work_item.updated.v1` | `WorkItemUpdatedV1` | `WorkItems` | UpdateWorkItemCommand (`update`), UpsertWorkItemCommand (`put`), BulkUpdateWorkItemDatesCommand (`bulk_date_update`), UpdateIntakeWorkItemCommand (`intake_update`), DeleteEstimatePointCommand über IWorkItemCommands (`estimate_point_delete`), Space-Intake-Update (`space_intake_update`) | WorkItemId, ProjectId, WorkspaceId, Operation, ChangedFields, Changes: FieldChange[] (Feld, alt, neu; nur geänderte Request-Felder) | I2 | WebhookEventConsumer (I6), SearchIndexingConsumer (I5) | C3, E6, F2, G1, H3, H6, A14, B3 | aktiv · Webhook |
| `plane.work_item.state_changed.v1` | `WorkItemStateChangedV1` | `WorkItems` | WorkItemStateChanger (alle Pfade, 16 §5.9) | WorkItemId, WorkspaceId, ProjectId, FromStateId?, ToStateId, Origin (StateChangeOrigin), ActorId? | I2 | – | C1, C3, E6, F2, A14, B3 | aktiv |
| `plane.work_item.assignees_changed.v1` | `WorkItemAssigneesChangedV1` | `WorkItems` | UpdateWorkItemCommand, UpsertWorkItemCommand, CreateWorkItemCommand (initiale Werte) | WorkItemId, ProjectId, WorkspaceId, Added[], Removed[] | I2 | – | C3, E6, F2, A12, H6 | aktiv |
| `plane.work_item.labels_changed.v1` | `WorkItemLabelsChangedV1` | `WorkItems` | UpdateWorkItemCommand, UpsertWorkItemCommand, CreateWorkItemCommand (initiale Werte) | WorkItemId, ProjectId, WorkspaceId, Added[], Removed[] | I2 | – | C3, E6, F2, A12, H6 | aktiv |
| `plane.work_item.archived.v1` | `WorkItemArchivedV1` | `WorkItems` | ArchiveWorkItemCommand, BulkArchiveWorkItemsCommand, AutoArchiveAndCloseJob (Origin `AutoArchive`) | WorkItemId, ProjectId, WorkspaceId, ArchivedAt (Datum) | I2 | – | C3, E6, F2 | aktiv |
| `plane.work_item.unarchived.v1` | `WorkItemUnarchivedV1` | `WorkItems` | RestoreArchivedWorkItemCommand | WorkItemId, ProjectId, WorkspaceId | I2 | – | C3, E6 | aktiv |
| `plane.work_item.deleted.v1` | `WorkItemDeletedV1` | `WorkItems` | DeleteWorkItemCommand, BulkDeleteWorkItemsCommand, DeleteIntakeWorkItemCommand (nicht angenommene) | WorkItemId, ProjectId, WorkspaceId | I2 | RecentVisitCleanupConsumer (I5), SearchIndexingConsumer (I5) | C3, E6, F2, G1, A5 | aktiv |
| `plane.work_item.restored.v1` | `WorkItemRestoredV1` | `WorkItems` | – (CE kennt kein Wiederherstellen gelöschter Work Items) | WorkItemId, ProjectId, WorkspaceId | I2 | – | E6 | reserviert (Klasse, kein CE-Auslöser) |
| `plane.work_item.moved.v1` | `WorkItemMovedV1` | `WorkItems` | – (A8) | WorkItemId, FromProjectId, ToProjectId, WorkspaceId | I2 | – | A8 | reserviert (Klasse, kein CE-Auslöser) |
| `plane.work_item.cycle_changed.v1` | `WorkItemCycleChangedV1` | `Cycles` | AddCycleWorkItemsCommand, RemoveCycleWorkItemCommand, TransferCycleWorkItemsCommand, DeleteCycleCommand, ConvertDraftToWorkItemCommand (über ICycleAssignment) | WorkItemId, ProjectId, WorkspaceId, FromCycleId?, ToCycleId? | I3 | – | B4, A12, E6, C3 | aktiv |
| `plane.work_item.module_changed.v1` | `WorkItemModuleChangedV1` | `ProjectModules` | AddModuleWorkItemsCommand, SetWorkItemModulesCommand, RemoveModuleWorkItemCommand, DeleteModuleCommand | WorkItemId, ProjectId, WorkspaceId, Added[], Removed[] | I3 | – | A12, E6, C3 | aktiv |
| `plane.work_item.relation_added.v1` | `WorkItemRelationAddedV1` | `WorkItems` | CreateWorkItemRelationsCommand | WorkItemId, RelatedWorkItemId, RelationType (Katalogschlüssel), WorkspaceId | I2 | – | A9, F2, E6 | aktiv |
| `plane.work_item.relation_removed.v1` | `WorkItemRelationRemovedV1` | `WorkItems` | RemoveWorkItemRelationCommand | WorkItemId, RelatedWorkItemId, RelationType, WorkspaceId | I2 | – | A9, F2, E6 | aktiv |
| `plane.work_item.parent_changed.v1` | `WorkItemParentChangedV1` | `WorkItems` | UpdateWorkItemCommand (`parent_id`), AddSubWorkItemsCommand, UpsertWorkItemCommand | WorkItemId, ProjectId, WorkspaceId, OldParentId?, NewParentId? | I2 | – | A2, A9, E6 | aktiv |
| `plane.work_item_activity.recorded.v1` | `WorkItemActivityRecordedV1` | `WorkItems` | IActivityRecorder (jeder Aufruf, §3.9) | BatchId, ActivityType (Original-Typstring), WorkItemId?, ProjectId, WorkspaceId, ActivityIds[], Notify, EmailEligible, NewDescriptionMentionIds[], CommentMentions[] (CommentId, NewMentionIds[]) | I2 | ActivityNotificationConsumer (I5) | E6, H6, C3 | aktiv · additiv zu 16 |
| `plane.work_item_comment.created.v1` | `WorkItemCommentCreatedV1` | `WorkItems` | CreateWorkItemCommentCommand (App/V1) und Space-Varianten über IWorkItemCommands | CommentId, WorkItemId, ProjectId, WorkspaceId, Operation | I2 | WebhookEventConsumer (I6; nur created/updated, Origin App/V1), SearchIndexingConsumer (I5) | F2, C3, E6, G1, H6, A16 | aktiv · Webhook |
| `plane.work_item_comment.updated.v1` | `WorkItemCommentUpdatedV1` | `WorkItems` | UpdateWorkItemCommentCommand (App/V1) und Space-Varianten über IWorkItemCommands | CommentId, WorkItemId, ProjectId, WorkspaceId, Operation, Changes: FieldChange[] (Feld, alt, neu; nur geänderte Request-Felder) | I2 | WebhookEventConsumer (I6; nur created/updated, Origin App/V1), SearchIndexingConsumer (I5) | F2, C3, E6, G1, H6, A16 | aktiv · Webhook |
| `plane.work_item_comment.deleted.v1` | `WorkItemCommentDeletedV1` | `WorkItems` | DeleteWorkItemCommentCommand (App/V1) und Space-Varianten über IWorkItemCommands | CommentId, WorkItemId, ProjectId, WorkspaceId | I2 | SearchIndexingConsumer (I5) | F2, C3, E6, G1, H6, A16 | aktiv |
| `plane.work_item_reaction.created.v1` | `WorkItemReactionCreatedV1` | `WorkItems` | CreateWorkItemReactionCommand, Space-Variante | ReactionId, WorkItemId, ProjectId, WorkspaceId, Reaction | I2 | – | H6 | aktiv |
| `plane.work_item_comment_reaction.created.v1` | `WorkItemCommentReactionCreatedV1` | `WorkItems` | CreateCommentReactionCommand, Space-Variante | ReactionId, CommentId, WorkItemId, ProjectId, WorkspaceId, Reaction | I2 | – | H6, A16 | aktiv · additiv zu 16 |
| `plane.work_item_vote.created.v1` | `WorkItemVoteCreatedV1` | `WorkItems` | Space: CreatePublicVoteCommand über IWorkItemCommands | WorkItemId, ProjectId, WorkspaceId, Vote (1│-1) | I6 | – | A16 | aktiv · additiv zu 16 |
| `plane.work_item_reaction.deleted.v1` | `WorkItemReactionDeletedV1` | `WorkItems` | DeleteWorkItemReactionCommand, Space-Variante | ReactionId, WorkItemId, ProjectId, WorkspaceId, Reaction | I2 | – | H6 | aktiv |
| `plane.work_item_comment_reaction.deleted.v1` | `WorkItemCommentReactionDeletedV1` | `WorkItems` | DeleteCommentReactionCommand, Space-Variante | ReactionId, CommentId, WorkItemId, ProjectId, WorkspaceId, Reaction | I2 | – | H6, A16 | aktiv · additiv zu 16 |
| `plane.work_item_vote.deleted.v1` | `WorkItemVoteDeletedV1` | `WorkItems` | Space: DeletePublicVoteCommand über IWorkItemCommands | WorkItemId, ProjectId, WorkspaceId, Vote (1│-1) | I6 | – | A16 | aktiv · additiv zu 16 |
| `plane.work_item_link.created.v1` | `WorkItemLinkCreatedV1` | `WorkItems` | CreateWorkItemLinkCommand | LinkId, WorkItemId, ProjectId, WorkspaceId | I2 | – | E6, H6 | aktiv |
| `plane.work_item_link.updated.v1` | `WorkItemLinkUpdatedV1` | `WorkItems` | UpdateWorkItemLinkCommand | LinkId, WorkItemId, ProjectId, WorkspaceId | I2 | – | E6, H6 | aktiv · additiv zu 16 |
| `plane.work_item_link.deleted.v1` | `WorkItemLinkDeletedV1` | `WorkItems` | DeleteWorkItemLinkCommand | LinkId, WorkItemId, ProjectId, WorkspaceId | I2 | – | E6, H6 | aktiv |
| `plane.work_item_attachment.created.v1` | `WorkItemAttachmentCreatedV1` | `WorkItems` | ConfirmWorkItemAttachmentUploadCommand | AttachmentId (Asset-ID), WorkItemId, ProjectId, WorkspaceId | I2 | – | E6, H6 | aktiv |
| `plane.work_item_attachment.deleted.v1` | `WorkItemAttachmentDeletedV1` | `WorkItems` | DeleteWorkItemAttachmentCommand | AttachmentId (Asset-ID), WorkItemId, ProjectId, WorkspaceId | I2 | – | E6, H6 | aktiv |
| `plane.cycle.created.v1` | `CycleCreatedV1` | `Cycles` | CreateCycleCommand (App/V1) | CycleId, ProjectId, WorkspaceId, Operation | I3 | WebhookEventConsumer (I6) | B4, E6, A12 | aktiv · Webhook |
| `plane.cycle.updated.v1` | `CycleUpdatedV1` | `Cycles` | UpdateCycleCommand (App/V1) | CycleId, ProjectId, WorkspaceId, Operation, Changes: FieldChange[] (Feld, alt, neu; nur geänderte Request-Felder) | I3 | WebhookEventConsumer (I6) | B4, E6 | aktiv · Webhook |
| `plane.cycle.completed.v1` | `CycleCompletedV1` | `Cycles` | CycleCompletionDetectionJob (§3.17.4) | CycleId, ProjectId, WorkspaceId, EndDate | I3 | – | B4, A12, B7, E6 | aktiv |
| `plane.cycle.archived.v1` | `CycleArchivedV1` | `Cycles` | ArchiveCycleCommand | CycleId, ProjectId, WorkspaceId | I3 | – | E6 | aktiv · additiv zu 16 |
| `plane.cycle.unarchived.v1` | `CycleUnarchivedV1` | `Cycles` | RestoreCycleCommand | CycleId, ProjectId, WorkspaceId | I3 | – | E6 | aktiv · additiv zu 16 |
| `plane.cycle.deleted.v1` | `CycleDeletedV1` | `Cycles` | DeleteCycleCommand (App/V1) | CycleId, ProjectId, WorkspaceId | I3 | RecentVisitCleanupConsumer (I5) | B4, E6 | aktiv |
| `plane.module.created.v1` | `ModuleCreatedV1` | `ProjectModules` | CreateModuleCommand (App/V1) | ModuleId, ProjectId, WorkspaceId, Operation | I3 | WebhookEventConsumer (I6) | A12, E6 | aktiv · Webhook |
| `plane.module.updated.v1` | `ModuleUpdatedV1` | `ProjectModules` | UpdateModuleCommand (App/V1) | ModuleId, ProjectId, WorkspaceId, Operation, Changes: FieldChange[] (Feld, alt, neu; nur geänderte Request-Felder) | I3 | WebhookEventConsumer (I6) | A12, E6 | aktiv · Webhook |
| `plane.module.archived.v1` | `ModuleArchivedV1` | `ProjectModules` | ArchiveModuleCommand | ModuleId, ProjectId, WorkspaceId | I3 | – | E6 | aktiv · additiv zu 16 |
| `plane.module.unarchived.v1` | `ModuleUnarchivedV1` | `ProjectModules` | RestoreModuleCommand | ModuleId, ProjectId, WorkspaceId | I3 | – | E6 | aktiv · additiv zu 16 |
| `plane.module.deleted.v1` | `ModuleDeletedV1` | `ProjectModules` | DeleteModuleCommand (App/V1) | ModuleId, ProjectId, WorkspaceId | I3 | RecentVisitCleanupConsumer (I5) | A12, E6 | aktiv |
| `plane.intake_work_item.created.v1` | `IntakeWorkItemCreatedV1` | `Intake` | CreateIntakeWorkItemCommand (App/V1), CreatePublicIntakeWorkItemCommand (Space) | IntakeWorkItemId, WorkItemId, ProjectId, WorkspaceId, Source | I3 | – | A15, C3, G1 | aktiv |
| `plane.intake_work_item.status_changed.v1` | `IntakeWorkItemStatusChangedV1` | `Intake` | UpdateIntakeWorkItemCommand (Accept/Decline/Snooze/Duplicate), UnsnoozeIntakeWorkItemsJob (Origin `worker`) | IntakeWorkItemId, WorkItemId, ProjectId, WorkspaceId, OldStatus, NewStatus (-2…2) | I3 | – | A15, C3 | aktiv |
| `plane.view.created.v1` | `ViewCreatedV1` | `Views` | CreateProjectViewCommand, CreateWorkspaceViewCommand | ViewId, WorkspaceId, ProjectId? | I3 | – | B5 | aktiv |
| `plane.view.updated.v1` | `ViewUpdatedV1` | `Views` | UpdateProjectViewCommand, UpdateWorkspaceViewCommand | ViewId, WorkspaceId, ProjectId? | I3 | – | B5 | aktiv |
| `plane.view.deleted.v1` | `ViewDeletedV1` | `Views` | DeleteProjectViewCommand, DeleteWorkspaceViewCommand | ViewId, WorkspaceId, ProjectId? | I3 | RecentVisitCleanupConsumer (I5, nur deleted) | B5 | aktiv |
| `plane.page.created.v1` | `PageCreatedV1` | `Pages` | CreatePageCommand, DuplicatePageCommand, WorkspaceSeedJob | PageId, WorkspaceId, ProjectIds[] | I4 | SearchIndexingConsumer (I5, D11) | D1, D2, D8, D11, G1, H6 | aktiv |
| `plane.page.updated.v1` | `PageUpdatedV1` | `Pages` | UpdatePageCommand (Metadaten, Zugriff, Sperre) | PageId, WorkspaceId, ProjectIds[], ChangedFields | I4 | SearchIndexingConsumer (I5, D11) | D1, D2, D8, D11, G1, H6 | aktiv |
| `plane.page.description_updated.v1` | `PageDescriptionUpdatedV1` | `Pages` | SavePageDescriptionCommand (REST-Fallback und IPageDocumentStore.SaveAsync aus Plane.Collaboration) | PageId, WorkspaceId, ProjectIds[] | I4 | SearchIndexingConsumer (I5, D11) | D1, D2, D8, D11, G1, H6 | aktiv |
| `plane.page.archived.v1` | `PageArchivedV1` | `Pages` | ArchivePageCommand | PageId, WorkspaceId, ProjectIds[] | I4 | – | D1, D2, D8, D11, G1, H6 | aktiv |
| `plane.page.unarchived.v1` | `PageUnarchivedV1` | `Pages` | RestorePageCommand | PageId, WorkspaceId, ProjectIds[] | I4 | – | D1, D2, D8, D11, G1, H6 | aktiv · additiv zu 16 |
| `plane.page.deleted.v1` | `PageDeletedV1` | `Pages` | DeletePageCommand | PageId, WorkspaceId, ProjectIds[] | I4 | SearchIndexingConsumer (I5, D11) | D1, D2, D8, D11, G1, H6 | aktiv |
| `plane.page.moved.v1` | `PageMovedV1` | `Pages` | – (D2) | PageId, OldParentId?, NewParentId?, WorkspaceId | I4 | – | D2 | reserviert (Klasse, kein CE-Auslöser) |
| `plane.notification.created.v1` | `NotificationCreatedV1` | `Notifications` | ActivityNotificationConsumer (je Empfänger und Workspace ein Event pro Batch) | ReceiverId, WorkspaceId, NotificationIds[], Senders[] | I5 | RealtimeFanOutConsumer (Gruppe `user:{id}`, §3.12) | H6 | aktiv · additiv zu 16 |
**`EventOperations`** (Werte des Feldes `Operation`): `create`, `put_create`, `update`, `put`, `cover`, `seed`, `draft_convert`, `intake_create`, `space_intake_create`, `bulk_date_update`, `intake_update`, `space_intake_update`, `estimate_point_delete`, `space_create`, `space_update`. Neue Werte nur additiv.

**CE-Consumer (vollständig):**

| Consumer-Name (Inbox-Schlüssel) | Klasse | Modul | Queue | abonnierte Events | ab |
|---|---|---|---|---|---|
| `notifications.activity` | `ActivityNotificationConsumer` | `Plane.Notifications` | `notifications` | `plane.work_item_activity.recorded.v1` | I5 |
| `webhooks.events` | `WebhookEventConsumer` | `Plane.Webhooks` | `webhooks` | `plane.project.created/updated/deleted.v1`, `plane.work_item.created/updated.v1`, `plane.cycle.created/updated.v1`, `plane.module.created/updated.v1`, `plane.work_item_comment.created/updated.v1` | I6 |
| `realtime.fanout` | `RealtimeFanOutConsumer` | `Plane.RealtimeEvents` | `realtime` | `plane.notification.created.v1` (→ `user:{receiver}`), `plane.label.*.v1`, `plane.state.*.v1` (→ `project:{id}`, `02` §5.2.12) | I5 |
| `home.recent_visit_cleanup` | `RecentVisitCleanupConsumer` | `Plane.Home` | `default` | `plane.work_item.deleted.v1`, `plane.project.deleted.v1`, `plane.cycle.deleted.v1`, `plane.module.deleted.v1`, `plane.view.deleted.v1`, `plane.page.deleted.v1`, `plane.workspace.deleted.v1` | I5 |
| `search.indexing` | `SearchIndexingConsumer` | `Plane.Search` (Detail `11`) | `indexing` | `plane.work_item.created/updated/deleted.v1`, `plane.work_item_comment.created/updated/deleted.v1`, `plane.page.created/updated/description_updated/deleted.v1` | I5 |

Alle übrigen Events haben in der CE keinen Consumer (der Dispatcher markiert sie nur als versandt); sie sind trotzdem Pflicht, weil Pakete daran hängen (`16` §3.2.4) und `EventEmissionTests` (`15` §6.2 C3) sie je Produzenten-Command genau einmal erwarten. Die Liste „Command → erwartetes Event“ für diesen Test ist das Feld `producers` in `_data/06-event-catalog.json`.

### 3.9 Activity-Pipeline

#### 3.9.1 Vertrag (Präzisierung von `02` D02-ADR-25 / §3.19 „Activity“)

`IActivityRecorder` (`Plane.WorkItems.Contracts/Services/IActivityRecorder.cs`) ist der **einzige** Weg, `work_item_activities` zu schreiben. Er wird von Command-Handlern der Module `WorkItems`, `Cycles`, `ProjectModules`, `Intake`, `Projects` (Estimate-Punkt löschen), `PublicSpace` (über `IWorkItemCommands`) und vom `AutoArchiveAndCloseJob` aufgerufen – immer **innerhalb** der offenen Command-Transaktion. Die Implementierung betritt für ihre Schreibzugriffe den Eigentümer-Scope `ModuleScope.Enter("WorkItems")` (Konvention für alle Contracts-Service-Implementierungen mit Schreibwirkung; Bestätigung der Guard-Mechanik durch `02`, O-D06-03).

```text
RecordAsync(ActivityRecordRequest r):
  r.Type            ActivityType (27 Werte, §4.5; Original-Typstring z. B. "issue.activity.updated")
  r.WorkItemId      Guid?   (null bei cycle.activity.* – die Work-Item-IDs stehen in RequestedData)
  r.ProjectId       Guid
  r.RequestedData   JsonObject?   (Request-Form wie Original requested_data; nur gesendete Felder)
  r.CurrentInstance JsonObject?   (Vorher-Zustand wie Original current_instance)
  r.Options         ActivityOptions(Notify, SubscribeActor, EmailEligible)   – je Aufrufstelle §4.4
  r.Epoch           long?   (Default: IClock.UtcNow in Sekunden, wie int(timezone.now().timestamp()))
```

#### 3.9.2 Ablauf (Port von `issue_activity`, A07 §3.1.2)

1. `ProjectId` muss existieren (sonst `InvalidOperationException` → Command scheitert; im Original stiller Abbruch, hier Programmierfehler).
2. `WorkspaceId` aus dem Projekt.
3. Ist `WorkItemId` gesetzt: `work_items.updated_at = now` (über den getrackten Eintrag, sonst `ExecuteUpdateAsync` nur auf `updated_at`) – **jede** Activity verschiebt `updated_at`, auch Reaktionen, Kommentare, Links und Votes (Grundlage für Sortierung „Last updated“ und Automationsfristen, A07 §5.7 Nr. 2).
4. Typ-Handler aus `ActivityTypeHandlers` (§4.5) erzeugt `WorkItemActivity`-Entitäten; bei `issue.activity.updated` iteriert er über **alle Schlüssel von `RequestedData`** und ruft je Schlüssel den Feld-Tracker (§4.6); nicht abgebildete Schlüssel (`sort_order`, `type_id`, `is_draft`, `description_json`, `description_binary`, …) erzeugen keine Activity.
5. Sonderfälle 1:1: A1 (`created the issue`) übernimmt `created_at := work_item.created_at` und `actor_id := work_item.created_by_id`; A3-Deduplizierung (jüngste Activity des Work Items ist `field = "description"` vom selben Akteur → nur `created_at = now` setzen, keine neue Zeile); `extract_ids`-Semantik (`label_ids`│`labels`, `assignee_ids`│`assignees`, `parent_id`│`parent`, `state_id`│`state`).
6. **Subscriber/Mentions synchron** (in der CE ab I2 statt im Notification-Task, `DEV-NOTIF-007`): (a) neu hinzugefügte Assignees (A10) → `work_item_subscribers` (`ON CONFLICT DO NOTHING`, `created_by = updated_by = assignee` wie Original); (b) ist `Options.Notify && Options.SubscribeActor` und der Typ benachrichtigungsfähig (§4.5) → Akteur als Subscriber (`get_or_create`); (c) `description_html` geändert → `MentionExtractor` (AngleSharp, `mention-component[entity_name="user_mention"]`, Attribut `entity_identifier`, nur gültige UUIDs) berechnet `neu = Mentions(neu) − Mentions(alt)`; `work_item_mentions` wird auf die Mentions der neuen Fassung synchronisiert (neue anlegen, entfernte löschen, A07 §3.2.5); neu Erwähnte, die aktive Projektmitglieder und weder Subscriber noch Assignee noch Ersteller sind, werden Subscriber; (d) Kommentar-Activities: Mentions aus `comment_html` (neu minus alt) → Subscriber wie (c).
7. Entitäten in den `PlaneDbContext` (geschrieben im einen `SaveChanges` des Commands, `02` D02-ADR-24).
8. Event `WorkItemActivityRecordedV1` (immer, auch wenn `Notify = false`), Payload §3.8 – inkl. `NewDescriptionMentionIds` und `CommentMentions` aus Schritt 6, damit der Notification-Consumer nicht erneut parsen muss.
9. Unterdrückung durch den Aufrufer wie Original: enthält ein PATCH `skip_activity: true` **und** `description_html`, rufen `UpdateWorkItemCommand` und `UpdateIntakeWorkItemCommand` weder den Recorder noch den Beschreibungs-Versionsdienst auf und erzeugen keine Events mit `Changes` (A07 §3.1.2 Nr. 8).

#### 3.9.3 Tabelle `work_item_activities` (Vorgabe für `03`, Felder 1:1 aus `IssueActivity`)

`id`, `work_item_id` (nullable, **ohne** Kaskade – Original `DO_NOTHING`), `verb` (Default `created`), `field` (nullable), `old_value` (text), `new_value` (text), `comment` (text), `attachments` (`text[]`, max. 10, ungenutzt), `work_item_comment_id` (nullable), `actor_id` (nullable, `SET NULL`), `old_identifier` (uuid), `new_identifier` (uuid), `epoch` (double) + `ProjectEntity`-Spalten. JSON-Namen im API-Vertrag bleiben `issue`, `issue_comment`, `issue_detail` (Serializer-Form `IssueActivitySerializer`, `04`). Indizes: `(work_item_id, created_at DESC)` (Detail-Zeitleiste, A3-Dedupe), `(workspace_id, actor_id, created_at DESC)` (Profil-Aktivität CE-PROF-010).

#### 3.9.4 Feld-Tracker und Eigentümer der Anzeigewerte

Die Tracker sind die in `02` §5.2.10 eingeführten `IActivityFieldResolver` (Feldname → `ActivityFieldChange`-Liste); jeder Resolver gehört dem Modul, das den Anzeigewert besitzt. Zuordnung, Original-Funktion und Varianten: §4.6. Reservierte Paket-Felder (`16` §3.2.3) dürfen nur von Paket-Resolvern erzeugt werden (`ReservationCollisionTests`).

#### 3.9.5 Weitere synchrone Versionierung (gleiche Transaktion)

| Original-Task | Ziel (synchron im Command) | Regel | Eigentümer |
|---|---|---|---|
| T23 `issue_description_version_task` | `WorkItemDescriptionVersionRecorder.RecordAsync(workItem, before, actor, isCreating)` in `UpdateWorkItemCommand`, `CreateWorkItemCommand`, `CreateIntakeWorkItemCommand`, `UpdateIntakeWorkItemCommand` | nur bei geändertem `description_html`; jüngste Version gleicher Besitzer und `now − last_saved_at ≤ 600 s` → überschreiben **inkl.** `last_saved_at = now` (gleitendes Fenster, 1:1); sonst neue Version; Begrenzung über Cron `maintenance.description_versions_cleanup` | `WorkItems` |
| T31 `track_page_version` | `PageVersionRecorder` in `SavePageDescriptionCommand` | festes 10-min-Fenster ohne Aktualisierung von `last_saved_at` (1:1); > `PageVersionsKeep` (20) → älteste soft-löschen | `Pages` (Detail `07`) |
| T30 `page_transaction` | `PageReferenceIndexer` in `CreatePageCommand`, `UpdatePageCommand` (nur mit `description_html`), `SavePageDescriptionCommand`, `DuplicatePageCommand` | Komponenten `mention-component`/`image-component` (A07 §2.15); Löschung **auf die Seite beschränkt** und nur UUID-`src` übernommen (Korrekturen, `DEV-OPS-004`) | `Pages` (Detail `07`) |

### 3.10 In-App-Benachrichtigungen

`ActivityNotificationConsumer.HandleAsync(WorkItemActivityRecordedV1 e)` – Port von `BG/notification_task.py` (A07 §3.2) mit den Korrekturen aus §4.10:

1. `e.ActivityType` in der Ausschlussliste (`cycle.activity.*`, `module.activity.*`, `issue_reaction.activity.*`, `comment_reaction.activity.*`, `issue_vote.activity.*`, `issue_draft.activity.*`) **oder** `e.Notify = false` → Ende.
2. Work Item laden **inkl.** soft-gelöschter (`IgnoreQueryFilters([soft_delete])`); ist es gelöscht (`issue.activity.deleted`), endet der Consumer ohne Notifications – das effektive Original-Verhalten (N2) bleibt bewusst erhalten, aber ohne Ausnahme (`DEV-NOTIF-003`).
3. Activities des Batches laden (`e.ActivityIds`), nur die des **eigenen** Work Items (Relationen auf andere Work Items werden übersprungen, A07 §3.2.3 „Nie benachrichtigt“), ohne `field = "description"`.
4. Aktive Projektmitglieder laden; Empfänger = Subscriber des Work Items ∩ aktive Projektmitglieder − Akteur − `e.NewDescriptionMentionIds` − alle `e.CommentMentions[*].NewMentionIds`.
5. Je Empfänger Präferenzen laden (`user_notification_preferences`; fehlt die Zeile → alle Flags `true`, `DEV-NOTIF-002`); je Activity **eine** `notifications`-Zeile: `entity_name = "issue"`, `entity_identifier = work_item_id`, `title = activity.comment`, `message = NULL`, `sender` = `in_app:issue_activities:created` (Empfänger = Ersteller) │ `…:assigned` (Empfänger ist Assignee und der Ersteller ist kein Assignee) │ `…:subscribed`, `triggered_by_id = actor`, `receiver_id`, `project_id`, `workspace_id`, `data` (Subscriber-Variante A07 §2.8.3, alle Werte außer `old_identifier`/`new_identifier` über `PythonText.Str` – `null` → `"None"`; bei Kommentar-Activities `issue_activity.issue_comment = comment_stripped`).
6. E-Mail-Log nur, wenn `e.EmailEligible` und `EmailPreferenceRules.ShouldEmail(field, newStateGroup, prefs)` (§4.10 `DEV-NOTIF-004`): `field == "state"` → `state_change` **oder** (`issue_completed` und neuer State in Gruppe `completed`); `field == "comment"` → `comment`; jedes andere Feld → `property_change`. `email_notification_logs.data` = Subscriber-Variante A07 §2.8.4 inkl. `activity_time` (ISO-8601 der Activity).
7. Kommentar-Erwähnungen: je `CommentMentions[i].NewMentionIds` ∩ aktive Projektmitglieder − Akteur **eine** Notification (Korrektur N9) mit `sender = in_app:issue_activities:mentioned`, `title = ""`, `message = "<display_name> has mentioned you in a comment in issue <name>"`, `data` ohne `issue_comment`; E-Mail-Log bei `prefs.mention` (Feld `mention`, Empfänger = **Erwähnter**, Korrektur N1).
8. Beschreibungs-Erwähnungen: je `NewDescriptionMentionIds` ∩ aktive Mitglieder − Akteur: ist die jüngste Activity des Work Items ein Beschreibungs-Edit desselben Akteurs (A3-Fall) → **eine** Notification mit `message = "You have been mentioned in the issue <name>"` und `issue_activity` aus dieser letzten Activity (inkl. korrekter `old_identifier`/`new_identifier`, Korrektur N8), sonst eine je Activity des Batches; E-Mail-Log bei `prefs.mention` mit `issue_activity.field = "mention"`, ohne `issue_comment` (Original-Form, `activity_time` hier im Python-Format `YYYY-MM-DD HH:MM:SS.ffffff+00:00` wie Original).
9. `AddRange` aller Notifications und E-Mail-Logs (EF bündelt), `SaveChanges`; danach je (Empfänger, Workspace) ein Event `plane.notification.created.v1` (für den Push §3.12).
10. Fehler (ungültige Mention-UUID, fehlende Benutzer) überspringen nur den betroffenen Eintrag und werden in `plane.worker` geloggt (Korrektur N4, N5, N7).

**Präferenzen** (`user_notification_preferences`, A07 §2.9): werden bei `CreateUserStep` (`05` §3.7.3, Order 500) für jeden Nicht-Bot-Benutzer mit allen Flags `true` angelegt (ersetzt das `post_save`-Signal); API `GET|PATCH /api/users/me/notification-preferences/` bleibt (Detail `04`). Präferenzen steuern **nur** E-Mails; In-App-Benachrichtigungen entstehen immer.

### 3.11 E-Mail-Benachrichtigungen (Bündelung)

```mermaid
sequenceDiagram
  autonumber
  participant S as Scheduler (Leader)
  participant J as Worker: notifications.email_digest
  participant E as Worker: notifications.send_email_digest (Queue emails)
  participant DB as PostgreSQL
  participant M as SMTP (Instanz-Konfiguration)
  S->>DB: INSERT jobs cron:notifications.email_digest:{occ} (alle 5 min)
  J->>DB: BEGIN; SELECT … FROM email_notification_logs WHERE processed_at IS NULL ORDER BY receiver_id, entity_identifier, created_at FOR UPDATE SKIP LOCKED
  J->>DB: je (receiver, work_item): INSERT jobs send_email_digest {receiver_id, work_item_id, log_ids[]} dedupe "mail-digest:{receiver}:{item}:{hash(log_ids)}"
  J->>DB: UPDATE … SET processed_at = now() WHERE id = ANY(gelesen); COMMIT
  E->>DB: Logs (nur log_ids, sent_at IS NULL), Empfänger, Work Item, Akteure, Projekt, Workspace
  E->>E: EmailDigestPayloadBuilder (create_payload) → Fluid issue-updates.liquid + Text-Teil
  E->>M: SMTP senden (MailKit, Timeout 30 s)
  alt Erfolg
    E->>DB: UPDATE email_notification_logs SET sent_at = now() WHERE id = ANY(log_ids)
  else SMTP-Fehler
    E-->>E: JobResult.Retry (Default-Policy, 5 Versuche) → danach Dead-Letter
  end
```

| Regel | Festlegung (Original-Bezug A07 §3.3) |
|---|---|
| Fenster | alles seit dem letzten Lauf, keine Mindestwartezeit (1:1) |
| Gruppierung | eine Mail je **(Empfänger, Work Item)**, innerhalb der Mail je Akteur (`triggered_by_id`) |
| `create_payload` | je Akteur je `field` deduplizierte Listen `old_value`/`new_value` (Strings; `"None"` ist gültig, 1:1); `comment` und `mention` werden als Kommentarblöcke herausgelöst; bei `mention` werden `mention-component`-Tags durch `@<display_name>` ersetzt (fehlender Benutzer → `@` + ursprüngliche ID, Korrektur EM4), bei `comment` nicht (1:1) |
| `activity_time` | je Akteur die **jüngste** Änderungszeit (Korrektur des Tippfehlers `data.get("actor_id")`), Ausgabe `hh:mm tt` (12-h-Format, z. B. `02:05 PM`; Korrektur des Formats `%H:%M %p` → „14:05 PM“, `DEV-MAIL-004`) |
| Betreff | `<IDENT>-<seq> <name ohne Steuerzeichen \x00–\x1F, \x7F–\x9F>` (1:1, M12) |
| Template-Kontext | 1:1 A07 §3.3.4 (`data`, `summary` = `"Updates were made to the issue by"`, `actors_involved`, `issue{issue_identifier,name,issue_url}`, `receiver{email}`, `issue_url`, `project_url`, `workspace`, `project`, `user_preference`, `comments`, `entity_type = "issue"`); URLs aus `IPublicUrls.Web` (Korrektur EM1); Avatar-URL absolut über `IPublicUrls.Asset(...)` (Korrektur EM5) |
| Kommentar-HTML | `{{ actor_comment \| raw }}` wie Original-`|safe`, aber Inhalt vorher durch `HtmlSanitizerProfile` (`05` §3.17.3) – Kommentare sind beim Speichern bereits bereinigt; Doppelprüfung schließt EM6 |
| `sent_at` | nur für die `log_ids` **dieser** Gruppe (Korrektur EM2) |
| SMTP nicht konfiguriert (`EMAIL_HOST` leer) | Job endet mit `JobResult.Success` ohne Versand, Logs bleiben `sent_at IS NULL`, Log `plane.worker` Information `"SMTP not configured, mail skipped"`; `ENABLE_SMTP` wird wie im Original **nicht** ausgewertet (A07 O4, Entscheidung: 1:1, weil „Disable email feature“ ohnehin `EMAIL_HOST` leert) |
| Automationen | erzeugen keine E-Mail-Logs (`EmailEligible = false`, §4.4 C65/C66; Original erzeugt sie, versendet sie aber nie und löscht sie nie – EM1, `DEV-NOTIF-006`) |

### 3.12 Echtzeit-Push (SignalR)

| Element | Festlegung |
|---|---|
| Hub | `LiveEventsHub` unter `/live/events/` im Host `Plane.Realtime` (Modul `Plane.RealtimeEvents`, ABG-058); Authentisierung über das Session-Cookie; Client-Methoden `joinGroup(group)`, `leaveGroup(group)`; Server sendet immer die Methode `event` mit `LiveEvent { event, group, payload, occurred_at }` (`16` §5.12). Beim Verbindungsaufbau tritt der Server den Client automatisch der Gruppe `user:{user_id}` bei. |
| Gruppen-Autorisierung | `IRealtimeGroupAuthorizer` je Präfix (`16` E-22): `user:` nur eigene ID; `ws:` aktives Workspace-Mitglied; `project:` Projektzugriff (`project.project_entity.read`); unbekanntes Präfix → abgelehnt. |
| Publisher | `IRealtimePublisher` (01 §5.5) hat **zwei** Implementierungen: `HubRealtimePublisher` (nur Host `Plane.Realtime`, `IHubContext<LiveEventsHub>`) und `QueuedRealtimePublisher` (Api/Worker: reiht `realtime.push`-Job auf Queue `realtime` transaktional ein). Consumer der Queue `realtime` laufen ausschließlich im Realtime-Host (§3.5.6). |
| Mehrinstanz | ab 2 Realtime-Replikas Valkey-Backplane `AddStackExchangeRedis` (`14` D14-ADR-21); jede Replika verarbeitet die Queue `realtime`, die Backplane verteilt an alle Verbindungen. |
| CE-Event `notification.created` | Gruppe `user:{receiver_id}`, Payload `{"workspace_id": "<uuid>", "workspace_slug": "<slug>", "notification_ids": ["<uuid>", …], "unread": {"total_unread_notifications_count": <int>, "mention_unread_notifications_count": <int>}}`; die Zähler berechnet der `RealtimeFanOutConsumer` beim Senden mit **derselben** Query wie `GET /api/workspaces/{slug}/users/notifications/unread/` (`UnreadNotificationCountQuery` aus `Plane.Notifications.Contracts`), Form = `TUnreadNotificationsCount`. Frontend-Handler (`08` Store 49): ist `workspace_slug` der aktuelle Workspace → `setUnreadNotificationsCount(payload.unread)`, sonst ignorieren. |
| Weitere CE-Events | `label.created│updated│deleted`, `state.created│updated│deleted` an `project:{project_id}` mit `{ "id": "<uuid>" }` (`02` §5.2.12); in der CE ohne Frontend-Handler (Andockstelle H6). |
| Latenz | Ziel < 2 s vom Commit bis zum Client (AK-D08-35): Outbox-`NOTIFY` → Dispatcher → `NOTIFY plane_jobs realtime` → Realtime-JobRunner. |

### 3.13 E-Mail-Plattform und Templates

#### 3.13.1 Versand (`Plane.Platform.Mail`)

| Element | Festlegung |
|---|---|
| Schnittstelle | `IMailSender.SendAsync(MailMessageSpec spec, CancellationToken ct)`; `MailMessageSpec(To[], Subject, HtmlBody, TextBody, Attachments[], LinkedResources[])`; Aufruf **nur** aus Jobs der Queue `emails` (Ausnahme: synchroner God-Mode-Test, siehe unten) |
| Konfiguration | zur Laufzeit je Versand aus `IInstanceConfigurationStore` (`02` §3.16): `EMAIL_HOST`, `EMAIL_PORT` (Default `587`), `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD` (verschlüsselt), `EMAIL_USE_TLS` (`"1"` → `SecureSocketOptions.StartTls`), `EMAIL_USE_SSL` (`"1"` → `SslOnConnect`; beide `"0"` → `None`; beide `"1"` → `SslOnConnect`), `EMAIL_FROM` (Format `Name <adresse>`, leer → `PlaneMailOptions.DefaultFrom` = `Team Plane <team@mailer.plane.so>` wie Original-Lesedefault); Cache `plane:instance:config` (`02` §3.12) |
| Dev/Test | `Plane__Mail__DevSmtp__Host`/`Port` (Mailpit, `14` §3.2.3) überschreibt Host/Port, TLS aus, ohne Anmeldung |
| Verbindung | MailKit `SmtpClient`, `Timeout = 30 s`, je Job eine Verbindung (wie Original `get_connection` je Task); Zertifikatsprüfung Standard, CA-Bundle des Containers |
| Text-Teil | `PlainTextFromHtml.Convert(html)` = Port `generate_plain_text_from_html`: `<style>`-Blöcke entfernen, Tags entfernen (AngleSharp `TextContent` pro Blockelement), HTML-Entities dekodieren, ≥ 3 Leerzeilen → 2, Ergebnis mit `"\n\n"` umschließen; byte-gleich zum Original geprüft (G-MAIL) |
| Bilder | `MailImageResolver`: Template referenziert `{{ images.logo_white }}` usw.; `ImageMode=Inline` → `cid:<name>@plane` + `LinkedResource` (nur tatsächlich gerenderte Bilder werden angehängt), `Hosted` → `{WEB_URL}/static/emails/<datei>` |
| Fehler | SMTP-/Netzwerkfehler → `JobResult.Retry`; `SmtpCommandException` mit `MailboxUnavailable` an **allen** Empfängern → `JobResult.Fail` (Dead-Letter, kein Sinn in Wiederholung) |
| God-Mode-Test (`POST /api/instances/email-credentials-check/`, M13) | **synchron** im Request (wie Original), Klartext-Mail Betreff `Email Notification from Plane`, Text `This is a sample email notification sent from Plane application.`; `SmtpErrorMapper` liefert die Original-Texte (A07 §2.17.1): `Invalid email header.`, `Invalid credentials provided`, `Could not connect with the SMTP server.`, `From address is invalid.`, `SMTP server disconnected unexpectedly.`, `All recipient addresses were refused.`, `Timeout error while trying to connect to the SMTP server.`, `Network connection error. Please check your internet connection.`, sonst `Could not send email. Please check your configuration` (alle 400) – MailKit-Ausnahmen werden darauf abgebildet (`AuthenticationException` → Credentials, `SocketException`/`SslHandshakeException` → Connect, `SmtpCommandException` mit `SenderNotAccepted` → From, `RecipientNotAccepted` → Recipients, `ServiceNotConnectedException` → Disconnected, `TimeoutException`/`OperationCanceledException` → Timeout, `ParseException` → Header) |
| CLI | `plane-cli test-email <to>` (CE-OPS-020) rendert `emails/test_email.liquid`, Betreff `Test email from Plane` (M14) |

#### 3.13.2 Template-Port (Django → Liquid)

Jede Datei `TPL/emails/<pfad>.html` wird nach `MAIL/Templates/emails/<pfad>.liquid` übertragen; HTML, Inline-CSS und Texte bleiben **byte-gleich**, nur Template-Syntax und Bildquellen ändern sich. Die Datei `MAIL/Templates/PORTING.md` dokumentiert je Template den Diff gegenüber dem Original (für Reviews).

| Django (im Original verwendet; Häufigkeit) | Liquid (Fluid) | Hinweis |
|---|---|---|
| `{{ var }}` | `{{ var }}` | HTML-Encoder aktiv (`TemplateOptions` mit `HtmlEncoder.Default`) wie Django-Autoescape |
| `{{ x\|safe }}` (1) | `{{ x \| raw }}` | nur `actor_comment` in `issue-updates` |
| `{% if %}` / `{% elif %}` / `{% else %}` / `{% endif %}` (56/6/11/56) | `{% if %}` / `{% elsif %}` / `{% else %}` / `{% endif %}` | Vergleiche `==` unverändert |
| `{% for x in xs %}` / `{% endfor %}` (8/8) | identisch | – |
| `\|length` (17) | `\| size` | – |
| `\|add:"-1"` (4), `\|add:"-2"` (4) | `\| minus: 1`, `\| minus: 2` | „+N more“-Zähler |
| `\|slice:":2"` (4) | `{% for v in xs limit: 2 %}` bzw. `\| slice: 0, 2` | Verhalten an Golden prüfen |
| `\|last` (15) | `\| last` | – |
| Index `.0`, `.1`, `.2` | `[0]`, `[1]`, `[2]` | – |
| Kommentare `<!-- … {{ … }} -->` | unverändert | werden wie in Django ausgewertet, bleiben unsichtbar |
| externe Bild-URLs (A07 §2.17.3) | `{{ images.<name> }}` (§3.13.1) | `DEV-MAIL-006`; `fonts.googleapis.com`-Import wird entfernt (Fallback-Fonts des Templates greifen) |
| Link-Ziele (`github.com`, `x.com`, `linkedin.com`, `plane.so`, `forum.plane.so`) | unverändert | nur Hyperlinks, keine Laufzeitabrufe |

**Gebündelte Bilder** (`MAIL/Assets/`, einmalig aus den Original-URLs übernommen, Herkunft in `MAIL/Assets/SOURCES.md`, Lizenzklärung O-D06-05): `logo-white.png`, `logo-dark.png` (`media.docs.plane.so/logo/new-logo-{white,dark}.png`), `social-{github,linkedin,twitter,website}-32.png` (`creative-assets.mailinblue.com/…/rounded_colored/*` und `{current_site}/static/logos/*`), `invite-hero.png` (`ik.imagekit.io/…/115727700_n9t8rrnwT.png`), `icon-{due-date,duplicate,assignee,labels,state,backlog,in-progress,todo,done,cancelled,forward-arrow,link,priority,blocking}.png` (`plane-marketing.s3.ap-south-1.amazonaws.com/plane-assets/emails/*`).

**Template-Katalog** (`MailTemplates`, vollständig; Betreffzeilen exakt, A07 §2.17.2): siehe §4.9.

#### 3.13.3 Renderer

`MailTemplateRenderer.RenderAsync(string templatePath, IReadOnlyDictionary<string, object?> model)`: Templates werden beim Start aus eingebetteten Ressourcen geparst (`FluidParser`, Cache je Pfad), Parse-Fehler brechen den Start ab (`MailTemplateStartupCheck`). Der Kontext ist ein `Dictionary<string, object?>` mit den Original-Variablennamen (z. B. `workspace_name`, `abs_url`, `first_name`); verschachtelte Werte als `Dictionary`/`IReadOnlyList` (keine `MemberAccessStrategy`-Registrierung nötig). Achtung Semantik: Django rendert einen Python-`None`-Wert als Text `None`, Fluid rendert `null` als leeren Text. Deshalb übergeben die Aufrufer überall dort, wo das Original `None` in den Kontext legt und es sichtbar würde, den String `"None"` (`PythonText.Str`); wo das Original leere Strings übergibt, wird `""` übergeben. G-MAIL prüft das je Template mit einem Kontext, der diese Fälle enthält.

### 3.14 Webhooks

#### 3.14.1 Datenmodell (Vorgabe für `03`)

`webhooks` (`workspace_id`, `url` varchar(1024), `is_active` bool = true, `secret_key` – DP-geschützt mit Purpose `Plane.Webhooks.Secret.v1` (`05` §3.17.5), Klartextformat `plane_wh_` + 32 Hex –, Flags `project`, `issue`, `module`, `cycle`, `issue_comment` bool = false, `version` varchar(50) = `"v1"`, Audit, Soft-Delete; partieller Unique-Index `(workspace_id, url) WHERE deleted_at IS NULL`). `webhook_logs` (`workspace_id`, `webhook_id` uuid **ohne FK** (1:1), `event_type`, `request_method` (= Aktion `created`/`updated`/`deleted`, 1:1 WH8), `request_headers` text (JSON), `request_body` text (JSON), `response_status` text, `response_headers` text (JSON), `response_body` text (max. 64 KiB, `05` §3.17.2), `retry_count` smallint, `created_at`). `is_internal`, `ProjectWebhook` entfallen (D06-ADR-23).

#### 3.14.2 Trigger-Tabelle (`WebhookTriggerMap`, vollständig)

Der `WebhookEventConsumer` erzeugt nur dann Zustellungen, wenn **alle** Bedingungen einer Zeile zutreffen; `EventContext.Origin` ist die Oberfläche des Requests.

| Integration-Event | Origin | `Operation` | Webhook-`event` (Header `X-Plane-Event`) | Flag | `action` | Fan-out | Original-Stellen |
|---|---|---|---|---|---|---|---|
| `plane.project.created.v1` | App, V1 | `create` | `project` | `project` | `created` | 1 Zustellung, `activity.field = null` | W11, W21 |
| `plane.project.updated.v1` | App, V1 | `update` | `project` | `project` | `updated` | je Eintrag in `Changes` | W12, W22 |
| `plane.project.deleted.v1` | App, V1 | – | `project` | `project` | `deleted` | 1, `data = {"id"}` | WD1, WD2 |
| `plane.work_item.created.v1` | App, V1 | `create`, `put_create` | `issue` | `issue` | `created` | 1 | W3, W5, W15 |
| `plane.work_item.updated.v1` | App, V1 | `update`, `put` | `issue` | `issue` | `updated` | je `Changes` | W4, W6, W16 |
| `plane.cycle.created.v1` | App, V1 | `create` | `cycle` | `cycle` | `created` | 1 | W1, W13 |
| `plane.cycle.updated.v1` | App, V1 | `update` | `cycle` | `cycle` | `updated` | je `Changes` | W2, W14 |
| `plane.module.created.v1` | App, V1 | `create` | `module` | `module` | `created` | 1 | W9, W19 |
| `plane.module.updated.v1` | App, V1 | `update` | `module` | `module` | `updated` | je `Changes` | W10, W20 |
| `plane.work_item_comment.created.v1` | App, V1 | `create` | `issue_comment` | `issue_comment` | `created` | 1 | W7, W17 |
| `plane.work_item_comment.updated.v1` | App, V1 | `update` | `issue_comment` | `issue_comment` | `updated` | je `Changes` | W8, W18 |

Nicht ausgelöst (1:1 A07 §2.10.3): Löschen von Work Items, Cycles, Modulen, Kommentaren; Archivierung; Cycle-/Modul-Zuordnungen; Bulk-Operationen; Automationen; Intake; Links/Anhänge/Reaktionen; Space. Die Event-Arten `cycle_issue`, `module_issue`, `intake_issue`, `user` haben im CE keinen Auslöser (WH7) und werden nicht abgebildet.

#### 3.14.3 Diff-Regel (`Changes`, Port `model_activity`)

`ChangeSetBuilder.FromRequest(JsonObject request, JsonObject before)` (`Plane.BuildingBlocks/Messaging/ChangeSetBuilder.cs`): für **jeden** Schlüssel `k` des Request-JSON, der auch in `before` existiert und dessen Wert sich per **roher JSON-Gleichheit** unterscheidet (`JsonNode.DeepEquals`; typ- und reihenfolgesensitiv wie Python `!=`: `["a","b"] ≠ ["b","a"]`, `"5" ≠ 5`), ein `FieldChange(k, before[k], request[k])`. `before` ist die DTO-Form der Oberfläche **vor** der Änderung (App: Form von `current_instance` im jeweiligen View, V1: v1-Serializer-Form; Detail je Endpunkt in `04`). Der Handler berechnet `Changes` vor `SaveChanges` und legt sie ins Event.

#### 3.14.4 Zustellung

```mermaid
sequenceDiagram
  autonumber
  participant C as WebhookEventConsumer (Queue webhooks)
  participant DB as PostgreSQL
  participant D as DeliverWebhookJob (Queue webhooks)
  participant S as SSRF-Client "webhooks" (05 §3.17.2)
  participant T as Empfänger
  C->>DB: aktive Webhooks des Workspace mit Flag = true
  loop je Webhook × je Change (bzw. 1)
    C->>DB: INSERT jobs webhooks.deliver {webhook_id, event, action, entity_id, change, actor_id} dedupe "wh:{message_id}:{webhook_id}:{field}"; delivery_id = UUIDv7
  end
  D->>DB: Webhook laden (gelöscht/inaktiv → Ende, WH5)
  D->>DB: data = aktueller Stand (v1-Form) bzw. {"id"} bei deleted; actor = UserLite
  D->>D: Body (UTF-8, System.Text.Json) + X-Plane-Signature
  D->>S: POST url (Pinning, 30 s, keine Redirects, kein Proxy)
  alt Antwort (jeder Status)
    D->>DB: webhook_logs (status, headers, body ≤ 64 KiB, retry_count = attempt−1)
  else Transportfehler, Versuch < 6
    D->>DB: webhook_logs (status "500", Fehlertext); JobResult.Retry (0…600 s)
  else Transportfehler, Versuch = 6
    D->>DB: webhook_logs; UPDATE webhooks SET is_active=false; INSERT jobs emails.webhook_deactivated
  else SSRF-Ablehnung
    D->>DB: webhook_logs (status "400", "Webhook URL rejected: <grund>"); JobResult.Success (kein Retry, keine Deaktivierung)
  end
```

| Aspekt | Festlegung |
|---|---|
| Methode/Header | `POST`; `Content-Type: application/json`, `User-Agent: Autopilot`, `X-Plane-Delivery: <delivery_id>` (stabil über alle Versuche einer Zustellung, `DEV-WH-001`), `X-Plane-Event: <event>`, `X-Plane-Signature: <hex>` (nur wenn Secret nicht leer); `Host` = Original-Host (Pinning, `05`) |
| Body | `{"event", "action", "webhook_id", "workspace_id", "workspace_slug", "data", "activity": {"field", "new_value", "old_value", "actor", "old_identifier": null, "new_identifier": null}}` (1:1 A07 §2.10.4); `action` ∈ `created`/`updated`/`deleted`; `actor` = `UserLite`-Form der Public API |
| `data` | aktueller Stand **bei Ausführung** des Zustell-Jobs (WH3, 1:1), geliefert von `IWebhookEventSource.LoadDataAsync` (v1-Serializer-Form: Projekt `ProjectSerializer` + Zähler, Issue `IssueExpandSerializer` mit `expand=["labels","assignees"]`, Cycle/Modul mit Zählern, Kommentar ohne `comment_stripped`/`comment_json` + `is_member`); Objekt inzwischen gelöscht → Zustellung entfällt still (WH2) |
| Serialisierung | `System.Text.Json`, snake_case, kompakt; Abweichung zu Python-`json.dumps` (Leerzeichen nach `,`/`:`) ist zulässig, weil die Signatur über die gesendeten Bytes gebildet wird (`DEV-WH-003`, `05` D15-SEC-09 prüft Signatur gegen Body) |
| Signatur | `WebhookSigner.Sign(secret, bodyBytes)` = `Convert.ToHexStringLower(HMACSHA256.HashData(UTF8(secret), bodyBytes))` |
| Retry | Policy `Webhook` (§3.5.3): nur `HttpRequestException`, `TaskCanceledException` (Timeout), `IOException`; HTTP-Status 1xx–5xx = zugestellt (WH4, 1:1) |
| Deaktivierung | beim 6. Transportfehler: `is_active = false`; Job `emails.webhook_deactivated` an `webhook.created_by` (M10, `reason` wird wie im Original **nicht** angezeigt, WH10) |
| Logs | jede Ausführung eine `webhook_logs`-Zeile; Header/Body als JSON statt Python-Repr (`DEV-WH-002`); Aufbewahrung `WebhookLogDays` (14) |
| Rate/Last | Queue `webhooks` mit 16 parallelen Zustellungen je Instanz; eigener Pool möglich (§3.5.6) |

### 3.15 Exporte

#### 3.15.1 Work-Item-Export (CE-EXP-001/-002)

1. `POST /api/workspaces/{slug}/export-issues/` (Handler in `Plane.Exports`, Endpunkt-Detail `04`): `provider ∉ {csv, xlsx, json}` → 400 `{"error": "Provider '<x>' not found."}`; ohne `project` alle nicht archivierten Projekte mit aktiver Mitgliedschaft; legt `export_histories` (Vorgabe `03`; Original-Tabelle `exporters`, Felder A07 §2.12.1) mit `status = "queued"`, `type = "issue_exports"`, `token = 32 Hex` an und reiht **transaktional** `ExportWorkItemsJob(exportId)` ein; Antwort 200 `{"message": "Once the export is ready you will be able to download it"}`.
2. Job (`exports.work_items`, Queue `exports`, Policy `Default`, Heartbeat): `status = "processing"` → Datenquelle über `IExportTypeProvider` (`type`) → Berechtigungsfilter 1:1 A07 §3.5.2 (inkl. Drafts, archivierter und Intake-Work-Items; aktive Projektmitgliedschaft des **Initiators**; `role > GUEST OR guest_view_all_features OR created_by = initiator`) → Formatierung → ZIP (`CompressionLevel.Optimal`, Deflate): `multiple = true` → je Projekt `"<slug>-<project_id>.<ext>"`, sonst `"<slug>-<workspace_id>.<ext>"`.
3. Ablage: `IObjectStorage.PutAsync(key, zip, "application/zip")` mit `key = "<workspace_id>/export-<slug>-<token[:6]>-<yyyy-MM-dd>.zip"` (1:1); Objekt **privat** (kein `public-read`, Korrektur der MinIO-Sonderlogik inkl. hart kodiertem `/uploads`, `DEV-EXP-003`); `url` = presigned GET 7 Tage über `PublicEndpoint` (S3) bzw. HMAC-signierte Gateway-URL (Dateisystem, `14` §3.7.6); `status = "completed"`, `key`, `url`. Fehler: `status = "failed"`, `reason` = Fehlermeldung (bei unbekanntem Format `"Unsupported format: <x>"`), danach **kein** Retry (Fehler sind deterministisch; `JobResult.Fail` nach Status-Update).
4. Historie `GET …/export-issues/?per_page&cursor` (Frontend pollt alle 3 s, 1:1); Ablauf über Cron `exports.expire_links` (§3.16).

| Format | Implementierung (`Plane.Exports/Formatters/`) | Regeln (1:1 `API/utils/porters/formatters.py`) |
|---|---|---|
| CSV | `CsvExportFormatter` (`CsvHelper`, `NewLine = "\r\n"`, Quoting nur bei Bedarf wie Python-`csv`) | flach: verschachtelte Objekte → `a__b`; Listen → `json.dumps`-Form (`["Alice", "Bob"]`, mit `", "`-Trenner wie Python); Listen von Objekten → JSON-String; Kopfzeile = Vereinigung aller Schlüssel in Erstauftrittsreihenfolge, `key.replace("_"," ").title()` (Python-`title()`-Semantik inkl. „Sequence Id“, `PythonTitleCase`); leere Daten → leerer String |
| XLSX | `XlsxExportFormatter` (`ClosedXML`, ein Blatt `Sheet`) | `None` → `""`; Listen → `", ".join(str(v))`; **Listen von Objekten als JSON** statt Python-Repr (`DEV-EXP-002`); Objekte → JSON; leere Daten → leere Mappe |
| JSON | `JsonExportFormatter` (`System.Text.Json`, Einrückung 2) | `default=str`-Semantik: Datums-/Zeitwerte als Python-`str()` (`YYYY-MM-DD HH:MM:SS.ffffff+00:00`), UUIDs als String |
| alle | `SpreadsheetSafeText.Escape` | Strings mit Präfix `=`, `+`, `-`, `@`, Tab, CR, LF erhalten `'` (CSV, XLSX; `API/utils/csv_utils.py`) |

Spalten (Reihenfolge = `IssueExportSerializer.Meta.fields`): §4.12. Die drei Zählspalten `sub_issues_count`, `link_count`, `attachment_count` fehlen im Original, weil das Export-Queryset sie nicht annotiert und DRF die `read_only`-`IntegerField`s per `SkipField` auslässt (geprüft in `API/utils/porters/serializers/issue.py` und `API/app/serializers/issue.py` Z. 753–755); die Zielversion **befüllt** sie (Korrektur `DEV-EXP-001`, G-EXPORT führt die Abweichung).

#### 3.15.2 Analytics-Export per E-Mail (CE-ANA-009)

`POST /api/workspaces/{slug}/export-analytics/` validiert Achsen (Texte 1:1 A07 §3.6) und reiht `ExportAnalyticsEmailJob(workspaceId, userId, request)` (Queue `exports`) ein; Antwort `{"message": "Once the export is ready it will be emailed to you at <email>"}`. Der Job nutzt dieselbe Distribution wie die Analytics-API (`IAnalyticsPlotQuery` aus `Plane.Analytics.Contracts`), erzeugt CSV (`QUOTE_ALL`, Formel-Schutz, Spaltenköpfe `row_mapping` A07 §2.13) und reiht die Mail M11 (`emails/exports/analytics.liquid`, Anhang `<slug>-analytics.csv`, `text/csv`) ein. Korrekturen: Segment nach Modul verwendet `module_details` (`DEV-EXP-004`); Segmentspalten in stabiler Reihenfolge (sortiert nach Anzeigename, statt Mengen-Reihenfolge).

### 3.16 Cleanup, Retention, Hard-Delete

Alle Jobs dieses Abschnitts laufen auf Queue `maintenance` (Concurrency 1), Policy `Maintenance`, löschen in Blöcken à 500 IDs (`process_cleanup_task`-Semantik: ID-Cursor, je Block eigene Transaktion, fehlerhafter Block → Log + weiter; Abschluss-Log `"<job> cleanup task completed"` mit `total_records_deleted`, `total_batches`) und lesen ihre Fristen aus `PlaneRetentionOptions` (`02` §3.15; ungültige/negative Werte → Default, `_retention_days`-Semantik). Tabellennamen sind Vorgaben für `03`.

| Job (`job_type`) | Kriterium | Löschart | Option (Default) | Original |
|---|---|---|---|---|
| `maintenance.hard_delete` (`HardDeleteJob`) | (1) `file_assets` mit `deleted_at < now − HardDeleteDays`: Objektspeicher-Dateien per `IObjectStorage.DeleteManyAsync` (Blöcke à 1 000), dann Zeilen; (2) in Original-Reihenfolge `workspaces`, `projects`, `cycles`, `modules`, `work_items`, `pages`, `views` (IssueView), `labels`, `states`, `work_item_activities`, `work_item_comments`, `work_item_links`, `work_item_reactions`, `user_favorites`, `module_work_items`, `cycle_work_items`, `estimates`, `estimate_points`; (3) danach **jede** weitere Tabelle mit `deleted_at` (Liste generiert aus dem EF-Modell: alle `ISoftDeletable`-Entitäten, `HardDeleteTableRegistry`) | hart (DB-Kaskaden laut Modell, `03`) | `HardDeleteDays` (60) | T10 `hard_delete`; Objektspeicher-Bereinigung neu (`DEV-OPS-002`) |
| `assets.soft_delete_unuploaded` | `file_assets.is_uploaded = false AND created_at < now − UnuploadedAssetDays` | soft (`deleted_at`, `is_deleted`); Datei fällt mit Hard-Delete | `UnuploadedAssetDays` (7) | T16 |
| `maintenance.api_activity_logs_cleanup` | `api_activity_logs.created_at <= now − ApiActivityLogDays` | hart | `ApiActivityLogDays` (14) | T3 |
| `maintenance.email_notification_logs_cleanup` | `sent_at <= now − EmailLogDays` **und** (neu) `sent_at IS NULL AND processed_at <= now − UnsentEmailLogDays` | hart | `EmailLogDays` (7), `UnsentEmailLogDays` (30, Nachtrag) | T4; unversendete Logs blieben im Original für immer (`DEV-MAIL-007`) |
| `maintenance.page_versions_cleanup` | `ROW_NUMBER() OVER (PARTITION BY page_id ORDER BY created_at DESC) > PageVersionsKeep` | hart | `PageVersionsKeep` (20) | T5 |
| `maintenance.description_versions_cleanup` | `ROW_NUMBER() OVER (PARTITION BY work_item_id ORDER BY created_at DESC) > DescriptionVersionsKeep` | hart | `DescriptionVersionsKeep` (20) | T6 |
| `maintenance.webhook_logs_cleanup` | `webhook_logs.created_at <= now − WebhookLogDays` | hart | `WebhookLogDays` (14) | T7 |
| `exports.expire_links` (Queue `exports`) | `export_histories.url IS NOT NULL AND created_at <= now − ExportLinkDays` | Objekt löschen, `url = NULL` (Zeile bleibt) | `ExportLinkDays` (8) | T15 (B6; B13 entfällt) |
| `identity.expired_sessions_cleanup` | `user_sessions.expires_at < now()` | hart | – | `05` SEC-45 |
| `messaging.outbox_cleanup` | `outbox_messages.dispatched_at < now − Outbox.RetentionHours` | hart | `Plane:Worker:Outbox:RetentionHours` (24) | neu |
| `messaging.inbox_cleanup` | `inbox_messages.processed_at < now − InboxRetentionDays` | hart | `Plane:Worker:InboxRetentionDays` (7) | neu |
| `messaging.dead_letter_cleanup` | `jobs.status = 4 AND dead_at < now − DeadLetterRetentionDays` | hart | `Plane:Worker:DeadLetterRetentionDays` (30) | neu |

**Soft-Delete-Kaskade (Deferred):** `SoftDeleteCascadeJob(RootEntity, RootId, DeletedAt)` (`02` D02-ADR-03, Queue `default`, `Transactional = true`) setzt für Wurzeln `Workspace`/`Project` die Kaskade aus `SoftDeleteCascadeRegistry` rekursiv per `ExecuteUpdateAsync … WHERE deleted_at IS NULL` (idempotent). Ersetzt T9 `soft_delete_related_objects` (für alle übrigen Wurzeln inline, `DEV-OPS-001`).

### 3.17 Automationen

#### 3.17.1 Auto-Archive und Auto-Close (`work_items.auto_archive_close`, Cron `0 1 * * *`, B5)

`AutoArchiveAndCloseJob` (Modul `WorkItems`, Queue `maintenance`, Akteur je Projekt = `project.created_by`, Origin `worker`): zuerst Archiv-, dann Close-Teil (Reihenfolge wie `archive_and_close_old_issues`); je Projekt eine eigene Transaktion (ein fehlerhaftes Projekt blockiert die anderen nicht, wie die Original-`try`-Blöcke je Teilfunktion).

Gemeinsame Auswahl (`AutomationCandidateQuery`, Basis `WorkItemBaseSets.IssueObjects` aus `02` §3.11.4 = ohne Drafts, Archiv, Triage-Intake, archivierte Projekte):

```sql
-- @months = projects.archive_in bzw. projects.close_in (1…12), @groups je Teil
SELECT wi.id FROM work_items wi
JOIN states s ON s.id = wi.state_id
WHERE wi.project_id = @project AND wi.archived_at IS NULL AND wi.deleted_at IS NULL
  AND wi.updated_at <= now() - make_interval(days => @months * 30)
  AND s."group" = ANY(@groups)
  AND NOT EXISTS (SELECT 1 FROM cycle_work_items cw JOIN cycles c ON c.id = cw.cycle_id
                  WHERE cw.work_item_id = wi.id AND cw.deleted_at IS NULL AND c.deleted_at IS NULL
                    AND (c.end_date IS NULL OR c.end_date >= now()))
  AND NOT EXISTS (SELECT 1 FROM module_work_items mw JOIN modules m ON m.id = mw.module_id
                  WHERE mw.work_item_id = wi.id AND mw.deleted_at IS NULL AND m.deleted_at IS NULL
                    AND (m.target_date IS NULL OR m.target_date >= current_date))
  AND (NOT EXISTS (SELECT 1 FROM intake_work_items iw WHERE iw.work_item_id = wi.id AND iw.deleted_at IS NULL)
       OR EXISTS (SELECT 1 FROM intake_work_items iw WHERE iw.work_item_id = wi.id AND iw.deleted_at IS NULL AND iw.status IN (1, -1, 2)))
ORDER BY wi.id;
```

Abweichung zur Original-Join-Auswertung (A07 §3.7 Edge-Cases): Ein Work Item qualifiziert sich nur, wenn **keine** aktive Cycle-/Modul-Zuordnung mehr läuft; gelöschte Zuordnungen zählen nicht; jedes Work Item erscheint genau einmal (keine doppelten Activities) – `DEV-AUTO-002`.

| Teil | Bedingung | Aktion | Activity (Variante) | Optionen | Events |
|---|---|---|---|---|---|
| Archiv | `projects.archive_in > 0`, `@groups = {completed, cancelled}` | `archived_at = heute (UTC-Datum, DateOnly)`; **kein** State-Wechsel, `IWorkItemStateChanger` wird **nicht** aufgerufen (ABG-056) | A12b `Plane has archived the issue` (`requested_data = {"archived_at": "<yyyy-MM-dd>", "automation": true}`, `current_instance = {"archived_at": null}`) | Notify, kein SubscribeActor, **kein** EmailEligible | `plane.work_item.archived.v1` (Origin `worker`) |
| Close | `projects.close_in > 0`, `@groups = {backlog, unstarted, started}` | Ziel-State = `projects.default_state_id`; ist er `NULL`: erster State der Gruppe `cancelled` **desselben Projekts** (`ORDER BY sequence, created_at`); gibt es keinen → Projekt überspringen, Warnung `plane.worker` `"auto-close skipped: project {id} has no cancelled state"` (`DEV-AUTO-001`); je Work Item `IWorkItemStateChanger.ChangeAsync(id, state, StateChangeOrigin.AutoClose)` (Guards/Hooks laufen, `completed_at`-Regel greift – Original umging sie per `bulk_update`, `DEV-AUTO-003`) | A13 `Plane updated the state to ` (`field = "state"`, `old_value = NULL`, `old_identifier = NULL`, `new_value` = State-Name, `new_identifier` = State-ID) – der Changer wählt diese Variante für `Origin = AutoClose` | wie Archiv | `plane.work_item.state_changed.v1` (Origin `AutoClose`) |

Batching: je Projekt höchstens 500 Work Items je Transaktion (Folgeblöcke in weiteren Transaktionen); `updated_at` wird durch die Activity auf `now` gesetzt (1:1), dadurch qualifiziert sich ein Work Item frühestens nach erneutem Ablauf der Frist.

#### 3.17.2 Intake-Unsnooze (`intake.unsnooze`, Cron `*/5 * * * *`, B2)

`UnsnoozeIntakeWorkItemsJob` (Modul `Intake`, Queue `maintenance`): `UPDATE intake_work_items SET status = -2, snoozed_till = NULL, updated_at = now() WHERE status = 0 AND snoozed_till <= now() AND deleted_at IS NULL RETURNING id, work_item_id, project_id, workspace_id` (1:1, `snoozed_till` ist bereits der Weckzeitpunkt in Projekt-Zeitzone, CE-INT-008); **keine** Activity (1:1); je Zeile `plane.intake_work_item.status_changed.v1` (`OldStatus = 0`, `NewStatus = -2`, additiv); Log `plane.worker` `"unsnooze_expired_intake_issues: returned {n} intake issues to pending"`.

#### 3.17.3 Projekt-Einstellungen (Quelle der Automationen)

`projects.archive_in` (0…12, 0 = aus), `projects.close_in` (0…12), `projects.default_state_id` (Close-State; UI `WEB/components/automation/auto-{archive,close}-automation.tsx`) – Eigentümer `Projects`, Änderung über `UpdateProjectCommand` (`Operation = update`, damit Webhook `project`/`updated` wie Original-PATCH). Validierung 0…12 (Original UI-Begrenzung, Backend-Regel aus `04`).

#### 3.17.4 Cycle-Abschluss-Erkennung (`cycles.completion_detection`, Cron `*/15 * * * *`, neu)

`CycleCompletionDetectionJob` (Modul `Cycles`, Queue `maintenance`): `UPDATE cycles SET completion_published_at = now() WHERE end_date IS NOT NULL AND end_date < now() AND completion_published_at IS NULL AND deleted_at IS NULL RETURNING …` → je Zeile `plane.cycle.completed.v1`. `UpdateCycleCommand` setzt `completion_published_at = NULL`, wenn `end_date` in die Zukunft verschoben wird. Neue Spalte `cycles.completion_published_at timestamptz NULL` (Nachtrag `03`). Grund: `16` §3.2.4 verlangt das Event, das Original kennt keinen Auslöser (Cycle-Status ist im Original rein datumsberechnet).

### 3.18 Weitere Jobs

| Job (`job_type`, Klasse) | Modul | Auslöser (transaktional, außer markiert) | Queue | Idempotenz / Dedupe | Verhalten (Original-Bezug) | ab |
|---|---|---|---|---|---|---|
| `workspaces.seed` (`WorkspaceSeedJob`) | Workspaces | `CreateWorkspaceCommand` | `default` | `Transactional`; Abbruch, wenn Bot `bot_user_<workspace_id>` existiert | T46 in **einer** Transaktion (Original ohne Transaktion, Teildaten bei Fehler, `DEV-OPS-005`); Bot-User (`username = bot_user_<ws_id>`, `display_name = first_name = "Plane"`, `is_bot = true`, `bot_type = "WORKSPACE_SEED"`, `email = bot_user_<ws_id>@<Host aus Plane:Urls:Web>`, kein Passwort – Keycloak-Login unmöglich, `05`) über `IBotUserProvisioner` (Identity); Inhalte aus eingebetteten JSON-Dateien `Plane.Workspaces/Seeds/Data/{projects,states,labels,cycles,modules,issues,views,pages}.json` (Kopie von `API/seeds/data/*.json`), ausgeführt durch `IWorkspaceSeedContributor` je Eigentümer-Modul (Projects → Projekt/States/Labels/Mitglieder/`ProjectUserProperty`, Cycles, ProjectModules, WorkItems → 7 Work Items inkl. Sequenz + Activity A1, Views, Pages) in fester Reihenfolge; externe URLs ersetzt: Unsplash-Cover → gebündelte Datei als `PROJECT_COVER`-Asset, jsDelivr-Emoji → `logo_props` mit Unicode-Emoji (`DEV-OPS-005`) | I1 |
| `work_items.crawl_link` (`CrawlWorkItemLinkJob`) | WorkItems | `CreateWorkItemLinkCommand`, `UpdateWorkItemLinkCommand` (nur URL geändert) | `default` | Dedupe `link-crawl:{link_id}` | T44 1:1: Client `link-preview` (`05`: 1 s Seite, 2 s `HEAD /favicon.ico`, 5 Redirects je Hop SSRF-geprüft, max. 2 MiB), Browser-User-Agent wie Original, `<title>` getrimmt, Favicon-Reihenfolge `icon`, `shortcut icon`, `apple-touch-icon`, `apple-touch-icon-precomposed`, sonst `/favicon.ico`, als `data:`-URI; jeder Fehler → Default-Icon (lucide `link`, Base64-SVG des Originals); `metadata = {title, favicon, url, favicon_url}`. Neu: `Plane:LinkPreview:Enabled` (Default `true`, Airgap-Bundle `false`) – aus → sofort Default-Metadaten ohne Netzaufruf | I2 |
| `assets.read_metadata` (`ReadAssetMetadataJob`) | Assets | Upload-Bestätigungen (alle 10 Aufrufstellen A07 §2.16.6), nur wenn `storage_metadata` leer | `default` | Dedupe `asset-meta:{asset_id}` | T35: `IObjectStorage.HeadAsync` → `{ContentType, ContentLength, LastModified (ISO), ETag, Metadata}`; Objekt fehlt → still beenden | I1 |
| `pages.copy_assets` (`CopyPageAssetsJob`) | Pages | `DuplicatePageCommand` | `default` | `Transactional` | T8: `image-component[src]` (UUID) sammeln, Assets im Workspace **und Projekt der Quell-Page** (Korrektur der Schleifenvariable, `DEV-OPS-006`) kopieren (`IObjectStorage.CopyAsync`, neuer Key `<workspace_id>/<uuid32>-<name>`), `src` umschreiben, `description_json`/`description_binary` über `Plane.Documents` in-process (ADR-031, kein `/convert-document/`-HTTP-Aufruf); Detail `07` | I4 |
| `home.record_visit` (`RecordRecentVisitJob`) | Home | Query-Handler der Detail-Endpunkte (`project`, `issue`, `module`, `cycle`, `view`, `page` – Aufrufstellen A07 §3.15) – **außerhalb** einer Transaktion | `default` | Dedupe `recent:{user}:{entity_name}:{entity_id}` | T34 1:1: vorhandener Eintrag → `visited_at = now`; sonst bei genau 20 Einträgen je (User, Workspace) ältesten (`created_at`) soft-löschen, dann anlegen | I5 |
| `identity.write_api_activity_log` (`WriteApiActivityLogJob`) | Identity | `ApiActivityLogMiddleware` (`05` §3.12.2) – außerhalb einer Transaktion | `default` | keine (jede Anfrage) | T27: `api_activity_logs` mit `token_identifier = token_hash`, Header als JSON (redigiert), Body-Regeln wie `MW/logger.py` | I6 |
| `identity.download_avatar` (`DownloadAvatarJob`) | Identity | `CreateUserStep` (`05` §3.7.3) | `default` | Dedupe `avatar:{user_id}` | Client `avatar-import` (`05`), Upload als `USER_AVATAR` | I0 |
| `identity.idp_user_state_sync` (`IdpUserStateSyncJob`) | Identity | Cron `*/15 * * * *` | `maintenance` | – | `05` §3.10 (Keycloak-Status ↔ API-Tokens) | I1 |
| `emails.workspace_invitation` (`SendWorkspaceInvitationEmailJob`) | Workspaces | `CreateWorkspaceInvitationsCommand` (je neu angelegter Einladung) | `emails` | `Transactional`; Dedupe `mail-ws-invite:{invitation_id}` | T45/M5; speichert den Klartext der Mail in `workspace_member_invites.message` (1:1); Einladung gelöscht → still beenden | I1 |
| `emails.project_addition` (`SendProjectAdditionEmailJob`) | Projects | `AddProjectMembersCommand` (je neu hinzugefügtem Mitglied) | `emails` | Dedupe `mail-prj-add:{project_member_id}` | T32/M7 | I1 |
| `emails.user_activation` (`SendUserActivationEmailJob`) | Identity | `AccountStateGuardStep` (Aktivierung vorprovisionierter Konten, `05` §3.7.3) | `emails` | Dedupe `mail-activate:{user_id}:{epoch}` | T36/M8 | I1 |
| `emails.user_deactivation` (`SendUserDeactivationEmailJob`) | Identity | `DeactivateAccountCommand` | `emails` | Dedupe `mail-deactivate:{user_id}:{epoch}` | T37/M9 (`login_url = <web>/login` 1:1; Link führt auf die Keycloak-Einstiegsseite) | I1 |
| `emails.webhook_deactivated` (`SendWebhookDeactivationEmailJob`) | Webhooks | `DeliverWebhookJob` (6. Fehlschlag) | `emails` | Dedupe `mail-wh-off:{webhook_id}:{delivery_id}` | T40/M10 | I6 |
| `notifications.send_email_digest` (`SendEmailDigestJob`) | Notifications | `StackEmailNotificationsJob` | `emails` | Dedupe `mail-digest:{receiver}:{work_item}:{hash}`; `sent_at` je Log | T13/M12 (§3.11) | I5 |
| `exports.analytics_email` (`ExportAnalyticsEmailJob`) | Analytics | `ExportAnalyticsCommand` | `exports` | – | T1/M11 (§3.15.2) | I5 |
| `messaging.consume` (`ConsumeEventJob`) | Messaging | Outbox-Dispatcher | Queue des Consumers | Dedupe `evt:{message_id}:{consumer}` + Inbox | §3.4 | I0 |
| `realtime.push` (`RealtimePushJob`) | RealtimeEvents | `QueuedRealtimePublisher` | `realtime` | – (Push ist idempotent für den Client) | §3.12 | I0 |
| `maintenance.soft_delete_cascade` (`SoftDeleteCascadeJob`) | Persistence (`02`) | `SoftDeleteInterceptor` (Deferred) | `default` | `Transactional`, `WHERE deleted_at IS NULL` | §3.16 | I1 |

### 3.19 Skalierung

| Thema | Festlegung |
|---|---|
| Worker horizontal | beliebig viele `worker`-Replikas; Claims per `FOR UPDATE SKIP LOCKED`, Dispatcher parallel, Scheduler genau ein Leader. **Valkey ist für den Worker nicht nötig** (alle Sperren in PostgreSQL; Korrektur der Formulierung in `14` §3.18 „Notification-Locks bzw. PG-Locks“, Änderungsauftrag §9). |
| Realtime | Queue `realtime` von allen Realtime-Replikas verarbeitet; ab 2 Replikas Valkey-Backplane Pflicht (`14` D14-ADR-21). |
| Verbindungsbudget | Worker `MaxPoolSize = 20` (`02` §3.15): 1 dedizierte `LISTEN`-Verbindung, 1 Leader-Verbindung, Rest für Dispatcher und Handler. Handler halten Verbindungen nur während DB-Arbeit; HTTP-/SMTP-Arbeit (Webhook, Crawl, Mail) läuft **ohne** offene Transaktion. `PlaneWorkerOptionsValidator` warnt, wenn die Summe der Concurrency **transaktionaler** Queues (`notifications`, `maintenance`, `default`, Consumer-Queues) `MaxPoolSize − 4` übersteigt. |
| Durchsatzziele (S12, Nachweis vor I1) | 1 000 Jobs/s mit 3 Worker-Instanzen ohne Doppelverarbeitung; Outbox-Latenz p95 < 500 ms; Leader-Failover < 30 s; Kill -9 ohne Nachrichtenverlust. |
| Lastprofil CE | Spitzen: Bulk-Operationen (z. B. 100 Work Items × Felder → Webhook-Fan-out `Webhooks × Changes`), E-Mail-Digest alle 5 min, Hard-Delete nachts. Gegenmaßnahmen: eigene Queues, Concurrency je Queue, Batch-Größen, nächtliche Cron-Zeiten wie Original. |
| Pools (`16` X9) | `integrations`, `importers`, `automations` (Pakete) und `webhooks`, `exports` (CE) können per `Plane__Worker__Queues` auf eigene Replikas gelegt werden (§3.5.6); Helm: zusätzliche `worker.pools[]` mit eigener `queues`-Liste (Nachtrag `14` §3.12). |
| Einzelknoten/AIO | ein Prozess verarbeitet alle Queues inkl. `realtime` (`HostRole.AllInOne`), Scheduler und Dispatcher aktiv. |

### 3.20 Monitoring

| Signal | Festlegung |
|---|---|
| Metriken (Meter `Plane.Messaging`, Namen verbindlich nach `14` §3.19.2) | `plane.outbox.pending`, `plane.outbox.dispatch.duration{event_type}`, `plane.jobs.executed{queue,job,outcome=success│retry│dead_letter}`, `plane.jobs.duration{queue,job}`, `plane.jobs.queue_depth{queue}`, `plane.scheduler.leader{instance}`; **Nachtrag** (additiv): `plane.outbox.lag` (Histogramm ms), `plane.outbox.dropped{reason}`, `plane.jobs.oldest_pending_age_seconds{queue}`, `plane.mail.sent{template,outcome}`, `plane.webhooks.deliveries{event,outcome=delivered│retry│deactivated│rejected}`, `plane.notifications.created{sender}`, `plane.scheduler.fired{name}`. Die in `02` §3.14 genannten `plane.outbox.lag_ms`/`plane.jobs.failed` werden durch diese Namen ersetzt (Änderungsauftrag §9). |
| Logs | Kategorie `plane.worker` (Start/Ende je Cron-Lauf, Cleanup-Zusammenfassungen, übersprungene Einträge), `plane.exception` (Dead-Letter, unerwartete Ausnahmen mit `job_id`, `job_type`, `queue`, `attempt`, Trace-ID), `plane.external` (ausgehende HTTP-Aufrufe Webhook/Crawl), keine PII/Secrets (`02` §3.14 Redaktion; Webhook-Secrets und SMTP-Passwörter nie im Log). |
| Traces | `ActivitySource "Plane.Messaging"`: Spans `outbox.dispatch`, `job.execute {job_type}` (Elternkontext aus `traceparent`, dadurch Request → Event → Consumer → Mail in einem Trace), `scheduler.tick`. |
| Health (`/health/ready`, Management-Port, ABG-014) | Worker: PostgreSQL, Schema-Gate, Data-Protection-Key-Ring; zusätzlich Check `messaging` = `Degraded` (nicht blockierend), wenn die eigene Runner-Schleife > 60 s nicht gelaufen ist oder `plane.outbox.pending > 10 000`. |
| Alarme (`14` §3.19.4, Ergänzung) | `plane.outbox.pending > 1 000` für 10 min; `plane.jobs.executed{outcome="dead_letter"} > 0` je Stunde; `plane.jobs.oldest_pending_age_seconds > 600` (Queue ohne Verarbeiter); kein Leader (`sum(plane.scheduler.leader) == 0`) > 2 min; `plane.webhooks.deliveries{outcome="deactivated"}` > 0. |
| Betrieb | `plane-cli jobs list --status dead [--queue]`, `plane-cli jobs requeue --id <id>│--type <job_type>`, `plane-cli jobs purge-dead --older-than <tage>`, `plane-cli scheduler status` (Leader, nächste Termine) – Nachtrag `14` §3.22. |
