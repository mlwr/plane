# 04 – Risikoregister und konsolidierte offene Entscheidungen

> **Stand:** 23.10.2026. **Zweck:** ein Ort für (1) die Risiken der Umsetzung mit Gegenmaßnahmen, (2) die Planungsentscheidungen dieses Plans, die von einem Architektur-Dokument abweichen oder eine Lücke schließen (OP-PLAN-*), und (3) alle noch offenen Entscheidungen aus den Dokumenten 00–17 mit Empfehlung, Entscheider und Frist. **Quellen:** Abschnitte §8 („Risiken & offene Punkte“) und Review-Protokolle der Architektur-Dokumente 01–11, 14–16, die Tabellen „Zurückgestellt“ und „Entscheidungen des Auftraggebers“ in 17 (Teil 1 und Teil 2) sowie die Planung in `plan/01`–`plan/03`.
>
> **Pflege:** Neue Risiken und beantwortete Planfragen (plan/03 §10) werden hier nachgetragen; erledigte Punkte bleiben mit Status „entschieden“ stehen, damit niemand dieselbe Frage erneut stellt. Hinweis zur Nummerierung: Architektur-Dokumente mit den Nummern 12 und 13 existieren nicht; die Reihe 00–17 ist vollständig berücksichtigt.

## Inhaltsverzeichnis

1. Bewertungsschema
2. Risikoregister
3. Planungsentscheidungen dieses Plans (OP-PLAN-*)
4. Konsolidierte offene Entscheidungen mit Empfehlung
5. Bereits getroffene Entscheidungen (nicht erneut fragen)
6. Nachpflegebedarf in den Architektur-Dokumenten

---

## 1. Bewertungsschema

| Wert | Wahrscheinlichkeit (W) | Auswirkung (A) |
|---|---|---|
| **hoch** | ohne Gegenmaßnahme eher wahrscheinlich als nicht | gefährdet eine Grundsatzentscheidung, ein ganzes Inkrement oder den CE-Release |
| **mittel** | realistisch möglich | verzögert ein Inkrement oder erzwingt eine dokumentierte Abweichung |
| **niedrig** | unwahrscheinlich | lokaler Mehraufwand in einem Paket |

Priorität = W × A (hoch × hoch zuerst). „Frühindikator“ ist das messbare Signal, an dem die Steuerung (plan/01 §7) das Eintreten erkennt.

---

## 2. Risikoregister

| ID | Risiko | Quelle | W | A | Gegenmaßnahme (in welchem Paket) | Frühindikator | betroffen |
|---|---|---|---|---|---|---|---|
| **R-P01** | **YDotNet (0.6.x, frühes Stadium) trägt das Hocuspocus-Protokoll nicht stabil** (Abstürze, Speicherlecks, fehlende Awareness-API) – gefährdet ADR-002 „Realtime in reinem .NET“. | 01 O-02, §9 S1; 07 §8.1; 17 Z-101, Z-102 | mittel | hoch | Spike S1 ab Tag 3 von I0 (WP-I0-901) mit 10 PT und harter Fallback-Kette (y-websocket-Protokoll → YDotNet-Fork mit aktuellem yrs → Node-Sidecar nur mit ADR-Änderung durch den Auftraggeber); Soak-Test 1 h, 50 Editoren; Ergebnis spätestens vor Start I3, damit der Realtime-Vorlauf in I3 beginnen kann. | S1-Kriterien nach 5 PT < 50 % grün; native Abstürze im Soak | I4, W3 |
| **R-P02** | **Konvertierung Yjs ⇄ ProseMirror-JSON ⇄ HTML erreicht keine Ausgabe-Gleichheit** ohne Node. | 01 §9 S2; 07 §8.1; 17 Z-102 | mittel | hoch | Spike S2 (WP-I0-902) mit Korpus ≥ 200 Dokumente; Fallback Jint mit gebündeltem `@tiptap/html`; HTML/JSON-Teil gatet I2, Yjs-Teil I4; G-DOC dauerhaft in G4. | HTML-Gleichheit < 95 % nach 4 PT | I2, I4 |
| **R-P03** | **Pixel-/DOM-Parität der Angular-Komponenten** zu Propel/Base UI scheitert an Host-Elementen, Overlay-Verhalten oder Angular-Aria-Lücken. | 01 §9 S10; 09 §8.1 (R-D09-01); 17 Z-06 | hoch | mittel | Spike S10 (WP-I0-910) vor dem Designsystem-Fundament; Konvention `display: contents`, eigene Portal-Schicht; Galerie mit DOM-Verträgen ab I0 (WP-I0-006); Fallback eigene Headless-Implementierung auf CDK a11y. | Visual-Diff der Leit-Komponenten > 0,1 % nach S10 | alle UI-Pakete |
| **R-P04** | **Activity-Parität** (38 Varianten, 78 Aufrufstellen) wird von parallel arbeitenden Agenten uneinheitlich umgesetzt. | 06 R-D06-03 | hoch | hoch | Zentraler `IActivityRecorder` bereits in I1 (WP-I1-204), Vollausbau in einem Paket (WP-I2-008, nicht parallelisiert); Golden je Variante; `_data/06-jobs.json` als Checkliste je Aufrufstelle. | Activity-Goldens mit Abweichungen in Schnitten außerhalb WP-I2-008 | I2–I3 |
| **R-P05** | **Work-Item-Listen-Performance** (gruppierte Pagination, Rich-Filter) verfehlt Zielwerte mit EF Core. | 01 §9 S9; 02 R-D02-01 | mittel | hoch | Spike S9 (WP-I0-909) vor I2; Variante „SQL-Prädikat aus AST“ vorbereitet; Lasttests LT-01…LT-03 im Paket WP-I2-012; Indizes ab erster Migration. | p95 > 2× Ziel im S9-Benchmark | I2 |
| **R-P06** | **Eigene Outbox/Job-Queue** verfehlt Zuverlässigkeit (Doppelverarbeitung, Verlust bei Kill -9, Leader-Failover). | 01 §9 S12; 06 R-D06-01, R-D06-02 | mittel | hoch | Spike S12 (WP-I0-912) vor I1; Fallback Wolverine (MIT) hinter denselben Interfaces; Kill-/Failover-Tests dauerhaft in G4. | ein S12-Kriterium rot | I1 ff. |
| **R-P07** | **Abweichende Namen** in den Architektur-Dokumenten (`Plane.*`, `X-Plane-*`, Realm `plane`) führen zu Zielcode mit Plane-Bezeichnern entgegen ADR-009C. | 00 ADR-009C; 17 Umbenennungstabelle; 01 §5.1, §7.21 (veraltet) | hoch | mittel | Umbenennungstabelle in der Pflichtlektüre (plan/03 §4.1); Architekturtest `NamingTests` (WP-I0-104); G-BRAND für sichtbare Artefakte; Review-Checkliste. | Treffer von `NamingTests` in PRs | alle |
| **R-P08** | **Permission-Deskriptoren** werden falsch aus Original-Klassen abgeleitet (Vorbedingungen, DenyStyle, dynamische `get_permissions`). | 02 R-D02-02; 05 R-10 | hoch | mittel | Generator `Funk.PermissionGen` als einzige Quelle (WP-I0-203); Matrix-Tests je Endpunkt gegen Original-Aufzeichnung (DoD V); Abweichungen → Korrektur der Matrix-Datei, nicht des Codes. | Matrix-Abweichungen im Parity-Report | alle V/B |
| **R-P09** | **Paritäts-Harness** nicht deterministisch (Original-Seeds, Zeitstempel, IDs) → Goldens unbrauchbar. | 01 §9 S11; 15 §8 | mittel | hoch | Spike S11 (WP-I0-911) gatet I0; Determinismus-Check in G3; Fallback Seeds über Original-API und strukturvergleichende Goldens. | Determinismus-Check rot | alle |
| **R-P10** | **Editor-Port** (Tiptap 2.27, eigene Angular-Bindung, NodeViews) instabil oder Schema weicht ab. | 01 §9 S5; 10 §8.1; 17 Z-105 | mittel | hoch | Spike S5 (WP-I0-905) vor I2; Schema-Freeze mit G-SCHEMA; Editor-Vorlauf-Track ab I1 (plan/01 L-8); Fallback framework-freie DOM-NodeViews. | G-SCHEMA-Diff, Eingabe-Lag > 50 ms | I2, I4 |
| **R-P11** | **I2 ist das größte Inkrement** (35 Pakete, 114 CE-IDs, kritischer Pfad 62 Tage) – Verzug gefährdet die Gesamtplanung. | plan/02 §3.2 | mittel | mittel | Editor-Vorlauf in I1; Layout-Pakete parallelisierbar; Re-Planung nach M1 mit Teilung großer Pakete (plan/01 §7.3). | Durchlaufzeit L-Pakete > 12 Tage | I2 |
| **R-P12** | **Keycloak-Login-Theme** erreicht keine Pixel-Parität zur React-Sign-in-Seite. | 05 R-01 | mittel | mittel | eigenes `template.ftl` ohne PatternFly (WP-I0-109); Visual-Diff in CI; Fallback Keycloakify (Node nur im Build). | Visual-Diff > 1 % | I0 |
| **R-P13** | **Aspire-Preview-APIs** (Keycloak-Hosting, generierte Parameter) brechen bei Updates. | 01 O-01; 05 R-02; 17 Z-15 | mittel | mittel | Versionen pinnen (S0), Fallback `AddContainer`; Update nur mit grünem AppHost-Test. | AppHost-Test rot nach Update | I0 ff. |
| **R-P14** | **Back-Channel-Logout** in Dev/Prod nicht erreichbar → Sessions enden erst per Revalidierung. | 05 R-03; 14 O-14-11 | mittel | mittel | getrennte Back-Channel-Basis-URL, Systemtest „Logout < 2 s“ (WP-I0-001); `host.docker.internal`-Klärung in S0. | L6-Test rot | I0 |
| **R-P15** | **HtmlSanitizer** weicht in Randfällen von `nh3` ab → Editor-Inhalte ändern sich beim Speichern. | 05 R-08 | mittel | mittel | Golden-Korpus mit DOM-Vergleich (WP-I2-101); Abweichungsliste mit Begründung. | G-SANITIZE-Diff | I2 |
| **R-P16** | **CSP-Enforce** blockiert Editor, Emoji, Worker oder Changelog. | 05 R-12; 10 §3.20.4; 17 Z-108 | mittel | mittel | Report-Only ab I0, Auswertung je E2E-Lauf; Enforce erst in WP-I7-108; Entscheidung `style-src-attr` vor I7. | CSP-Reports in E2E | I7 |
| **R-P17** | **Versteckte externe Aufrufe** (Fonts, Emoji-Daten via CDN, Bilder in Mails/Seeds) verletzen Airgap. | 00 ADR-004; 09 §3.8.2; 03 R-D03-07 | mittel | mittel | Netzwerk-Allowlist-Test ab I0 (WP-I0-102), gebündelte Assets (WP-I0-006, WP-I1-105), Airgap-E2E (WP-I7-107). | Allowlist-Test meldet Egress | alle |
| **R-P18** | **Lizenzrisiken:** kommerziell gewordene Bibliotheken, PDFsharp ≥ 6.5 (AGPL-3.0-only), Demo-Seed-Bilder, Emoji-Grafiken. | 01 O-09; 03 R-D03-07; Auftrag (Lizenz-Hygiene) | mittel | mittel | Lizenz-Gate ab I0 (WP-I0-106); Bibliotheken nur aus 01 §8; PDFsharp bei 6.2.4 (MIT); Seed-Bilder ersetzen (OE-05). | Lizenz-Gate rot | I0, I4, I7 |
| **R-P19** | **Andockstellen reichen für eine Welle nicht** (z. B. Pflicht-Properties A1, geänderte Default-Rechte E5) → CE-Umbau nötig. | 15 O-D15-10; 16 §8; 17 Z-16 | mittel | hoch | Typ-X-Tests mit Fake-Erweiterungen je Andockstelle; Definition of Ready je Welle (16 §6.1) prüft Andockstellen vor Start; Änderungsverfahren 16 §6.3; Contract-Snapshots ab I7. | DoR-Prüfung einer Welle findet fehlende Andockstelle | W1–W9 |
| **R-P20** | **Forgejo-Spezifika** (Signatur-Header, Hook-Typ, Scopes, `status`-Event) weichen von Gitea ab. | 16 O-16-01/-02; 17 Z-13 | mittel | mittel | Spike S-F2-1 vor W1 gegen den gepinnten Forgejo-Container; Verifier akzeptiert alle drei Header-Varianten (16 D16-ADR-10). | S-F2-1-Befund | W1 |
| **R-P21** | **Synchrone Activity** und API-Activity-Log erhöhen die Schreiblatenz. | 06 R-D06-09, O-D06-08 | mittel | mittel | gebündelte Lookups; Messung im I2- und I6-Lasttest (LT-10); Puffer hinter derselben Schnittstelle bei Überschreitung. | p95 +20 ms gegenüber Request ohne Activity | I2, I6 |
| **R-P22** | **Migrations-Konflikte** paralleler Agenten im EF-Modell-Snapshot. | 03 R-D03-10 | hoch | niedrig | Regel 01 §7.14, ein Modul je Migration, Drift-Gate in CI, nicht parallelisierbare Pakete pro Modul (plan/03 §3). | Rebase-Konflikte im Snapshot | alle |
| **R-P23** | **Pgvector.EntityFrameworkCore 0.3.x** ohne ausdrückliche EF-10-Freigabe. | 03 R-D03-01; 17 Z-106 | niedrig | mittel | `PgvectorSmokeTests` in S0; in der CE wird nur die Extension aktiviert (G1 nicht gewählt). | Smoke-Test rot | I0, I5 |
| **R-P24** | **Original-Quellen nicht TS-6-kompilierbar** (Angular 22). | 01 O-10 | mittel | niedrig | mechanische Korrekturen per Codemod in S0, Liste der Anpassungen. | Compile-Fehlerzahl in S0 | I0 |
| **R-P25** | **PDF-Optik** (PDFsharp/MigraDoc) erreicht die Vorlage nicht. | 01 §9 S3; 07 §8.1; 17 Z-103 | mittel | niedrig | Spike S3; Fallback SkiaSharp; Abnahme einer Abweichung durch den Auftraggeber. | Raster-Diff > 5 % | I4 |
| **R-P26** | **Charts** mit D3 nicht pixelgleich zu recharts. | 01 §9 S6 | mittel | niedrig | Spike S6 vor I3; Fallback ECharts mit Abnahme der Abweichung. | Visual-Diff > 2 % | I3, I5 |
| **R-P27** | **Späte Entscheidungen des Auftraggebers** blockieren Pakete. | §4 | mittel | mittel | Fristen je offener Entscheidung (§4) an Paket-Start gekoppelt; vorläufige Festlegungen nur, wo dokumentiert umkehrbar. | Planfrage mit `blocker` > 3 Tage offen | alle |
| **R-P28** | **Automatisch erzeugte Paketangaben** (Analyse-Referenzen, Original-Pfade, Endpunkt-Zuordnung) sind im Einzelfall ungenau. | plan/02 (Generator) | niedrig | mittel | Agent prüft im Schritt „Original lesen“ (plan/03 §5.1) und meldet Abweichungen als Planfrage; Endpunkt-Ausnahmen über `EP_OVERRIDE`. | Planfragen zu Paketangaben | alle |
| **R-P29** | **Sprach-Inkonsistenz:** Oberfläche standardmäßig Deutsch (ADR-009D), Original-Mails und Original-Datumsformate nur Englisch; Tests und Referenzen des Originals in `en`. | ADR-009D; 06 O-D06-10; 08 O-D08-08; 15 §3.9.1 | hoch | mittel | Entscheidungen OP-PLAN-05/-06/-07 vor I1; bis dahin Mails Englisch, Datumsformat 1:1, Paritäts-Gates in `en`. | – | I1, I5 |
| **R-P30** | **Valkey-/Realtime-Ausfall** führt zu verlorenen Live-Ereignissen bzw. Rückstau. | 06 R-D06-08; 07 §8.1 | niedrig | niedrig | Client lädt Zähler bei Reconnect per REST; Verwerfen alter Nachrichten (> 60 s); Alarm auf Queue-Alter. | Alarm `oldest_pending_age` | I5 |

---

## 3. Planungsentscheidungen dieses Plans (OP-PLAN-*)

Diese Entscheidungen trifft der Plan, weil der Auftrag es verlangt oder weil Architektur-Dokumente eine Lücke bzw. einen Widerspruch enthalten. Status „Plan“ = gilt für die Umsetzung; „Bestätigung erbeten“ = gilt vorläufig, der Auftraggeber möge bestätigen.

| ID | Thema | Entscheidung | Begründung | Status |
|---|---|---|---|---|
| **OP-PLAN-01** | Erweiterungspunkte als eigene Arbeitspakete | Die P-Andockstellen aus 16 §1.4/§3.3.0 bekommen eigene Pakete (Nummernkreis 2xx, Typ X, 29 Pakete); das Paket der Träger-CE-ID (16 §4.6) hängt vom X-Paket ab und nutzt die Andockstelle. Abweichung von 16 §4.6 („kein eigenes Arbeitspaket Erweiterungspunkte“). | Ausdrückliche Vorgabe des Planungsauftrags; macht Andockstellen einzeln abnehmbar und für die Wellen sichtbar; Schnittregel bleibt erfüllt, weil jedes X-Paket einen eigenen Typ-X-Nachweis liefert. | Plan |
| **OP-PLAN-02** | Hauptbranch in CI und Gates | Alle Workflows und Gates beziehen sich auf `develop` (PR-Ziel, Merge-Queue, `push`-Trigger, `edge`-Images); `main` bleibt unangetastet. 14 §3.21.1 (`push` auf `main`) und 15 §3.15.1 (G2 „vor Merge in `main`“) sind entsprechend zu lesen. | ADR-009 (Rang 00) legt `develop` als Hauptbranch fest. | Plan |
| **OP-PLAN-03** | Inkrement-Zuordnung einzelner CE-IDs abweichend von 15 Anhang B | CE-WS-002 Demo-Seed → I4 (braucht Cycles, Module, Views, Pages); CE-WI-025/-026 Cycle-/Module-Dropdown, CE-LV-004 Layout-Kontexte, CE-LV-011 View speichern, CE-LV-016 Anzeige je Cycle/Modul → I3 (Fachobjekte existieren erst dort); CE-PAGE-024…-033, -039, -040 und CE-I18N-010 → I2 (Rich-/Lite-/Document-Editor mit allen Menüs und NodeViews gehören nach 01 ABG-114 und 10 §1.4 zu I2); CE-RT-009 → I0 (Realtime-Host mit Health ist I0-Gerüst, 07 §1.4); CE-OPS-005 → I7 (automatisches HTTPS ist nach 14 §3.1.2/§3.8 Teil von I7, das HTTP-Grundrouting liefert WP-I0-103). Zehn Endpunkte entstehen ohne Sonderregel in einem anderen Inkrement als im Katalog 04 notiert (plan/02 Anhang C); über `EP_OVERRIDE` werden 14 Endpunkte als Vorab-Endpunkte früher gebaut (u. a. `GET /api/workspaces/{slug}/`, `GET {W}/projects/`, `/live/events/`, `/api/integrations/{provider}/webhooks/{connection_id}/`) und 2 später (`GET {W}/cycles/`, `GET {W}/modules/` mit I3). | Fachliche Abhängigkeiten bzw. höherrangige Festlegungen (01, 10, 07, 14). | Plan |
| **OP-PLAN-04** | Zielbezeichner in Architektur-Dokumenten | Für Zielcode gilt ausschließlich die Umbenennungstabelle (17); Formulierungen „Präfix bleibt `Plane.*`“ (01 §5.1, 16 Kopf) und die BR-02-Ausnahmen für Namespaces/Realm/Header (01 §7.21) sind durch ADR-009C überholt. Absicherung durch `NamingTests` (WP-I0-104). Realm-Dateien heißen `funk-realm.json`/`funk-realm.test.json`, Konfigurationsdateien `00-funk-realm.json`, `10-funk-bootstrap-admin.json`; Webhook-Header `X-Funk-Signature`/`X-Funk-Delivery`/`X-Funk-Event`. | ADR-009C (Auftraggeber, Z-110) hat Rang über 01–16. | Plan |
| **OP-PLAN-05** | Sprache der E-Mails | **Empfehlung:** Mails in der Sprache des Empfängers (`de` oder `en`, Fallback Instanz-Standard `de`); `en`-Templates 1:1 aus dem Original (G-MAIL gegen Original), `de`-Templates als geprüfte Übersetzung (G-MAIL gegen freigegebene Referenz); Betreffzeilen in `MailSubjects` je Sprache. Bis zur Entscheidung: Englisch wie Original (06 O-D06-10). | ADR-009D macht Deutsch zur Standardsprache; rein englische Mails wären für deutschsprachige Nutzer ein Bruch. Aufwand gering (rund 15 Templates). | Bestätigung erbeten – vor WP-I1-102 |
| **OP-PLAN-06** | Datums- und Zeitformate in `de` | **Empfehlung:** In `de` deutsche Datumsformate (z. B. `23.10.2026`, deutsche Monatsnamen) über die Locale-Formatierung; in `en` 1:1 wie Original (`en-US`). Abweichung als `ui-deviations.yaml`-Eintrag `kind: behavior`. Bis zur Entscheidung: 1:1 (08 O-D08-08). | Das Original formatiert unabhängig von der Sprache englisch; mit Deutsch als Standard wirkt das fehlerhaft. | Bestätigung erbeten – vor WP-I1-017 |
| **OP-PLAN-07** | Sprache der Paritäts-Tests und Referenzen | Contract-, E2E- und Visual-Paritätsgates laufen mit Testbenutzern in `en` gegen das Original in `en` (15 §3.9.1 Selektor-Regel); zusätzlich ein `de`-Visual-Satz (Shell, Work-Item-Liste, Detail, Settings, Page-Editor, God Mode, Space) gegen das Original in `de` mit gebrandeten Ausnahmetabellen. | Hält die bestehende Teststrategie stabil und prüft die Standardsprache trotzdem sichtbar. | Plan (Bestätigung erbeten zusammen mit OP-PLAN-06) |
| **OP-PLAN-08** | Start der Welle W1 (Forgejo) | Standard: W1 beginnt nach M7 (CE-Release). Option „verzahnt“: W1 beginnt nach M6 mit einem eigenen Team, wenn I7 dadurch nicht verzögert wird; technisch sind alle Andockstellen ab M6 vorhanden. | Strategie „CE zuerst, vollständig“ vs. hohe Priorität von Forgejo (ADR-007). | Entscheidung Auftraggeber bei M5 |
| **OP-PLAN-09** | Keycloak-Realm und Login-Theme getrennt | Realm als Code (WP-I0-108, M) und Login-Themes (WP-I0-109, L) sind getrennte Pakete, damit der Login-Schnitt nicht auf die Pixel-Parität des Themes wartet. | verkürzt den kritischen Pfad von I0 um rund 10 Tage. | Plan |
| **OP-PLAN-10** | Editor-Schnitt ED-2 geteilt | ED-2 aus 10 §1.5 wird in ED-2a (Rich-Text-Kern, WP-I2-022) und ED-2b (Menüs und Blöcke, WP-I2-023) geteilt. | Paketgröße ≤ L (≤ 12 Tage). | Plan |
| **OP-PLAN-11** | Vorlauf-Tracks | Editor-Track (WP-I2-101, -207, -021 … -024) darf ab M0 bzw. nach WP-I1-103 beginnen, Dokument-/Realtime-Track (WP-I4-101, -202, -006) ab M2; abgenommen werden sie mit ihrem Inkrement. | verkürzt die längsten kritischen Pfade (I2, I4); keine Platzhalter-Routen, weil diese Pakete keine Screens registrieren bzw. erst im Inkrement freigeschaltet werden. | Plan |
| **OP-PLAN-12** | Nachweis entfallener CE-IDs | Die 27 durch ADR-008 entfallenen CE-IDs liegen in den Paketen, die den Ersatznachweis führen: WP-I0-108 (Registrierung, Passwort, Magic-Code, OAuth-Provider, Auth-Methoden, verknüpfte Konten – `KeycloakRealmConfigTests`), WP-I0-003 (Admin-Login, Provider-Konfiguration im God Mode – `OidcLoginFlowTests.InstanceAdminRole_GrantsGodMode`), WP-I6-005 (Space-Login-Varianten – `OidcLoginFlowTests.SpaceLogin_*`). | Erfüllt „jede CE-ID genau einem Paket“ und macht den Wegfall prüfbar (15 Anhang B). | Plan |

---

## 4. Konsolidierte offene Entscheidungen mit Empfehlung

Spalten: **Frist** = spätestens vor diesem Paket/Meilenstein; **Entscheider** = Auftraggeber (AG), Architektur-Review (AR), Spike-Ergebnis (Spike). Bis zur Entscheidung gilt die Empfehlung als vorläufige Arbeitsgrundlage, sofern die Spalte „vorläufig“ „ja“ zeigt.

### 4.1 Entscheidungen des Auftraggebers

| ID | Thema | Quelle | Empfehlung | Frist | vorläufig | betroffene Pakete |
|---|---|---|---|---|---|---|
| OE-01 | E-Mail-Sprache | OP-PLAN-05, 06 O-D06-10 | Empfängersprache `de`/`en`, Standard `de` | vor WP-I1-102 (I1) | ja (bis dahin `en`) | WP-I1-102, WP-I1-002, WP-I5-007, WP-I6-015 |
| OE-02 | Datumsformate in `de` | OP-PLAN-06, 08 O-D08-08 | deutsche Formate in `de`, `en` 1:1 | vor WP-I1-017 | ja (bis dahin 1:1) | WP-I1-017 |
| OE-03 | Sprache der Paritäts-Referenzen | OP-PLAN-07 | Gates in `en`, zusätzlicher `de`-Visual-Satz | vor WP-I0-911/-106 | ja | WP-I0-106, WP-I0-911 |
| OE-04 | Aufbewahrung `work_item_versions` | 03 O-D03-02, 17 Z-114 | Default 20 je Work Item (`Funk:Retention:WorkItemVersionsKeep`) | vor M2 | ja | WP-I2-008 |
| OE-05 | Demo-Seed-Bilder (Lizenz, Plane-Branding) | 03 O-D03-04, R-D03-07, 17 Z-114 | Unsplash-/Apple-Emoji-/`media.docs.plane.so`-Bilder durch eigene oder frei lizenzierte Bilder ersetzen (`DEV-DM-13`) | vor WP-I4-009 | ja | WP-I4-009 |
| OE-06 | Pflicht-Extensions `pg_trgm`/`unaccent`/`vector` auch für externe Datenbanken | 03 O-D03-06, 17 Z-114 | Pflicht, Betreiberdoku mit SQL-Vorlage | vor M7 | ja | WP-I0-104, WP-I7-101 |
| OE-07 | Gruppensummen-Quirk `DEV-GRP-001` (0 → 1) | 02 O-D02-04 („beibehalten“) vs. 04 O-D04-04 („korrigieren“), 17 Z-115 | **korrigieren** (falsche Zahl = funktionaler Fehler nach 17 Z-12), per Schalter abschaltbar | vor WP-I2-012 | nein | WP-I2-012, WP-I2-013 |
| OE-08 | Korrigierte Tooltip-Kürzel im Editor (FE-ED-04) | 10 O-D10-02, 17 Z-109 | korrigieren (falsche Information) | vor WP-I2-023 | nein | WP-I2-023 |
| OE-09 | `nodeHighlight` (E22) aktivieren | 10 §3.22, 17 Z-109 | nicht aktivieren (fehlendes Feature, optisch 1:1); Kandidat für spätere Abnahme | vor WP-I2-022 | ja | WP-I2-022 |
| OE-10 | Power-K zeigt bei Pages keinen Projekt-Identifier (Original-Defekt) | 11 O-D11-04, 17 Z-111 | optisch 1:1 belassen, als „bekannt, nicht korrigiert“ führen | vor WP-I5-009 | ja | WP-I5-009 |
| OE-11 | Host aus `LLM_BASE_URL` automatisch in SSRF-Allowlist | 11 O-D11-02, 17 Z-111 | nein; Allowlist über `Funk:Ai:AllowedInternalHosts` in Compose/Helm | vor WP-I6-018 | ja | WP-I6-018, WP-I2-102 |
| OE-12 | Editor-KI-Menü (`rephrase-grammar`) in der CE | 11 O-D11-05 | nein (G3 nicht gewählt), Route reserviert | vor WP-I6-018 | ja | WP-I6-018 |
| OE-13 | Ollama als optionaler Dev-Container | 11 O-D11-06 | ja, Opt-in-Parameter `Funk:Dev:LocalLlm`, nicht im Prod-Compose | vor WP-I6-018 | ja | WP-I0-102 (Nachtrag), WP-I6-018 |
| OE-14 | Kursivschrift im Web-PDF (Q-07-04) | 07 O-07-06, 17 Z-116 | 1:1 aufrecht wie Original | vor WP-I4-003 | ja | WP-I4-003 |
| OE-15 | Passwortlose Anmeldung (Passkeys) im Keycloak-Flow | 05 O-D05-04 | Passkeys als Option im Flow, standardmäßig deaktiviert; kein E-Mail-OTP | vor M1 | ja | WP-I0-108 |
| OE-16 | Auto-Redirect zu Keycloak auf Space-Seiten | 05 O-D05-05 | nein: Space-Startseite mit Button, Boards anonym | vor WP-I6-005 | ja | WP-I6-005 |
| OE-17 | Umgang mit a11y-Verstößen des Originals | 15 O-D15-06 | übernehmen (ADR-005), Liste „Original-Baseline“ je Inkrement vorlegen; Korrektur nur auf Beschluss | je Meilenstein | ja | alle V/F |
| OE-18 | Start der Welle W1 | OP-PLAN-08 | nach M7; verzahnt ab M6 nur mit eigenem Team | bei M5 | ja | W1 |
| OE-19 | Forgejo in Produktion unter eigener Subdomain | 14 O-14-02 | eigene Subdomain | vor W1 | ja | W1, WP-I7-102/-106 |
| OE-20 | Import von Forgejo-Milestones | 16 O-16-03 | in W1 als funk.-Module, nach W2 optional als A5-Milestones | W1-Wellenplan | ja | W1 |
| OE-21 | Additiv-Regel bei Pflicht-Properties (A1) und geänderten Default-Rechten (E5) | 15 O-D15-10, 17 Z-16 | Pflicht-Properties dürfen CE-Requests nicht ungültig machen; geänderte Default-Rechte nur über neue Rollen-Grants | vor W2 bzw. W4 | ja | W2, W4 |
| OE-22 | Workspace-States (`states.project_id` NOT NULL) | 16 O-16-04 | CE NOT NULL; W6 lockert per Expand-Migration oder eigene Tabelle – Entscheidung im W6-Plan | W6-Wellenplan | ja | W6 |
| OE-23 | `teamspace_id` an Work-Item-Kommentaren | 16 O-16-05 | Spalte anlegen (01 bindend), Nutzung im B1-Plan | W5-Wellenplan | ja | WP-I1-205, W5 |
| OE-24 | Bestätigung der Planungsentscheidungen OP-PLAN-05 … -08 | §3 | wie in §3 empfohlen | M0 | ja | – |

### 4.2 Durch Spikes zu entscheiden

| ID | Thema | Quelle | Empfehlung / Erwartung | Spike (Paket) | Frist |
|---|---|---|---|---|---|
| OE-30 | Aspire-Keycloak-Hosting (Preview) nutzbar | 01 O-01, 17 Z-15 | nutzen, Fallback `AddContainer` | S0 (WP-I0-900) | Ende S0 |
| OE-31 | Mediator: `internal`-Handler über `InternalsVisibleTo`; Contract-Command-Dispatch über Assemblies | 02 O-D02-09, 04 O-D04-01, 17 Z-01, Z-106 | `InternalsVisibleTo`; Fallback `public sealed` bzw. `<M>CommandDispatch` | S0 | Ende S0 |
| OE-32 | Vitest-`runnerConfig`, MTP-Optionen, xunit.v3-Trait-API | 17 Z-02 | gemeinsame `frontend/vitest.config.ts` | S0 | Ende S0 |
| OE-33 | TypeScript 6.0 für Original-Quellen | 01 O-10 | mechanisch anpassen, Liste führen | S0 | Ende S0 |
| OE-34 | Signal Forms (`[formField]`/`FormValueControl`) an Propel-Komponenten | 08 O-D08-01 | Direktive `[plFormField]` | S0 | Ende S0 |
| OE-35 | Bundle-Budgets, `jsdom`-Major, Node-Version für den Build | 08 O-D08-05, O-D08-06, 14 O-14-04 | Original-Build messen ± 10 %; jsdom laut `@angular/build` 22; Node 24 LTS, sonst 22 LTS | S0 | Ende S0 |
| OE-36 | `OwnershipGuardInterceptor` für Contracts-Services (Modul-Scope je Entität) | 06 O-D06-03 | Scope beim `Add`/`Attach` erfassen, `IModuleScope.Enter(owner)` | S0 | Ende S0 |
| OE-37 | `host.docker.internal` unter Linux für Back-Channel und Forgejo-Webhooks | 14 O-14-11, 17 Z-15 | sonst `--add-host=host.docker.internal:host-gateway` | S0 | Ende S0 |
| OE-38 | Keycloak 26: `max_age=0`, Optionsnamen (Theme-Cache, Health-Pfad), `CreateDefaultClientScopes`, Back-Channel-Hostname | 17 Z-03, Z-14, 14 O-14-10 | gegen gepinntes Image verifizieren; sonst `prompt=login` | S7 (WP-I0-907) | Ende S7 |
| OE-39 | Keycloak-Clients je App, Keycloak in Produktion unter `/idp/` | 01 O-06, 14 O-14-01 | je App ein Client; `/idp/` als Default, Subdomain optional | S7 | Ende S7 |
| OE-40 | Deep-Links der Keycloak-Kontokonsole; `next_path` mit Query | 05 O-D05-01, 08 O-D08-13 | in `FunkAuthOptions` hinterlegen; Query in `next_path` zulässig | S7 | Ende S7 |
| OE-41 | Default-Objektspeicher und Upload-Modus | 01 O-03 | SeaweedFS + `Direct`, falls grün, sonst `Proxy` | S8 (WP-I0-908) | Ende S8 |
| OE-42 | Scope-FK inkl. nullable `workspace_id` (MATCH SIMPLE), auch `search_documents` | 03 O-D03-05, R-D03-02, 17 Z-107 | Konvention greift; Fallback Raw-SQL-Constraint | Scope-FK (WP-I0-913) | Ende I0 |
| OE-43 | Session-Verbindung `funk-session` für Leader-Lock und `LISTEN` hinter PgBouncer | 06 O-D06-11, 17 Z-117 | eigener Connection-String, Fallback Hauptverbindung; Nachtrag in 02 §3.15/14 | S12 (WP-I0-912) | Ende S12 |
| OE-44 | Live-Event-Latenz mit zwei Job-Hops | 17 Z-104 | < 2 s mit und ohne Valkey | S12, gemessen in WP-I5-005 | M5 |
| OE-45 | Host-Form der Blocks-Select-Familie; Angular-Aria-Popups ohne CDK-Overlay | 09 O-D09-16, 17 Z-06 | Attribut-Selektor je Wurzel-Tag aus den S10-DOM-Verträgen | S10 (WP-I0-910) | Ende S10 |
| OE-46 | Referenz-Galerie (`@makeplane/propel@0.7.3` aus Registry-Cache mit SHA-512-Pin) | 15 O-D15-08 | wie empfohlen, Build im `parity`-Kontext | S10 | Ende S10 |
| OE-47 | Editor-DOM-Details, doppelte Tastaturnavigation im Slash-Menü (E10) | 10 O-D10-03, O-D10-05, 17 Z-105 | per DOM-Golden festschreiben; E10 nach Messung | S5 (WP-I0-905) | vor I2 |
| OE-48 | Hocuspocus-Wire-Verhalten (PermissionDenied, 4403, Reihenfolge Sync) | 17 Z-101 | Golden-Transkripte vom Original | S1 (WP-I0-901) | vor I4 |
| OE-49 | Typisierte Attribute aus Original-yjs, Mark-/Attribut-Reihenfolge | 07 O-07-01, O-07-02, 17 Z-102 | aus G-SCHEMA/G-DOC übernehmen; Fallback F-S2-2 | S2 (WP-I0-902) | vor I2 (HTML), vor I4 (Yjs) |
| OE-50 | PDF: Emoji außerhalb der BMP, Noto-Emoji-Version, Test-Rasterizer-Lizenz | 07 O-07-03, O-07-04, 17 Z-103 | Version passend zu `emojibase-data`; `PDFtoImage` (MIT) bei Lizenzproblem | S3 (WP-I0-903) | vor WP-I4-003 |
| OE-51 | YDotNet-Reife / Fallback-Wahl | 01 O-02 | siehe R-P01 | S1 | vor I4 |
| OE-52 | Forgejo 15: Signatur-Header, Hook-Typ, `status`-Event, OAuth2-Scopes | 16 O-16-01, O-16-02, 17 Z-13 | alle Header-Varianten akzeptieren; Scopes granular, sonst Org-Rechte des Bot-Kontos | S-F2-1 (W1) | vor W1 |

### 4.3 Entscheidungen des Architektur-Reviews (technisch, innerhalb der ADRs)

| ID | Thema | Quelle | Empfehlung | Frist | betroffene Pakete |
|---|---|---|---|---|---|
| OE-60 | Forgejo-LTS-Tag, Playwright-Image-Digest, `fonts-noto-color-emoji`, Registry-Namensraum der Images | 01 O-04, 09 O-D09-08, 17 Z-05, 14 O-14-03 | zum Start I0 pinnen; Images unter `ghcr.io/mlwr/funk-*` | Start I0 | WP-I0-102, -106, -206 |
| OE-61 | Ablage der Visual-Baselines in airgapped CI; Aufbewahrung von Traces/Videos | 15 O-D15-04, O-D15-09, 17 Z-07 | Git LFS (Budget 2 GB), sonst OCI-Artefakt; 14 Tage PR, 90 Tage G5/G6 | Ende I0 | WP-I0-106 |
| OE-62 | Ablage der Lint-Regeln; Nachladen bei `app_version`-Wechsel | 08 O-D08-12, O-D08-09 | `frontend/tools/eslint-rules/` + `tools/ci/`; Vollnavigation ohne Toast | Start I0 | WP-I0-105 |
| OE-63 | Vorbedingungs-Keys der Permission-Matrix (`WS(A) ∧ WS(A)`; tote Keys V1, V6–V9) | 05 O-D05-08 | keine Vorbedingung bei identischen Stufen; Generator erzeugt nur referenzierte Keys | Start I0 | WP-I0-203 |
| OE-64 | Zeitzone der Datum-Zeit-Ausgabe | 02 O-D02-01 | UTC beibehalten; nur bei nachgewiesener textueller Auswertung Benutzer-Zeitzone | Ende S11 | alle V |
| OE-65 | Metriknamen (Meter `Funk.Messaging` aus 14 maßgeblich) | 06 O-D06-04 | 14 §3.19.2 maßgeblich; 02 §3.14 angleichen | Start I1 | WP-I1-101 |
| OE-66 | Rate-Limit-Algorithmus (Sliding Window, 6 Segmente) | 02 O-D02-07 | akzeptieren (`DEV-RL-001`), Grenzwert ±1 | I1 | WP-I1-016 |
| OE-67 | Label löschen bereinigt View-Filter? | 02 O-D02-05 | im Harness prüfen; ohne Nachweis nicht implementieren | WP-I1-012 | WP-I1-012 |
| OE-68 | Status des reparierten `POST {P}/invitations/`; Ziel-Goldens für defekte Routen | 04 O-D04-05, O-D04-06, 17 Z-115 | 200; `golden_source: target` | vor WP-I1-006 | WP-I1-006, WP-I0-911 |
| OE-69 | `issue_comment.description` im Vertrag | 03 O-D03-01, 17 Z-114 | `null` ausgeben (`DEV-DM-03`) | vor WP-I2-007 | WP-I2-007 |
| OE-70 | Mutationstests (Stryker.NET) als Gate | 15 O-D15-07 | informativ bis I2, danach ≥ 60 % für `Domain/` prüfen | Ende I2 | – |
| OE-71 | `cycles.completion_published_at` im Schema | 06 O-D06-06 | in 03 aufnehmen (additive Migration) | Start I3 | WP-I3-005 |
| OE-72 | Speicherdruck-Watchdog im Realtime-Host; Server-Broadcast bei REST-Lock/-Archiv | 07 O-07-05, O-07-07, 17 Z-116 | Watchdog aus bis LT-20-Messung; kein Server-Broadcast (Parität) | Ende I4 | WP-I4-006, -008 |
| OE-73 | `before`-Form der `Changes` je webhook-relevantem Endpunkt | 06 O-D06-07 | 04 dokumentiert je Endpunkt die Serializer-Form; Test vergleicht `activity.old_value` | Start I6 | WP-I6-015 |
| OE-74 | OpenAPI-Version für `v1` | 02 O-D02-06 | 3.1; Option `Funk:OpenApi:Version` für 3.0 | I6 | WP-I6-009 |
| OE-75 | Schreiblast API-Activity-Log und Recent Visits | 06 O-D06-08, O-D06-09 | in LT-10 messen; bei Bedarf gebündeltes Schreiben hinter derselben Schnittstelle | I6/I7 | WP-I6-009, WP-I5-003, WP-I7-109 |
| OE-76 | CSP `style-src-attr 'unsafe-inline'` | 10 O-D10-06, 17 Z-108 | übernehmen (Editor-Ausrichtung/-Farben) | vor WP-I7-108 | WP-I7-108 |
| OE-77 | Valkey in Produktion Pflicht | 01 O-05 | Pflicht ab 2 Instanzen eines Hosts; Einzelknoten-Profil ohne Valkey testen | I7 | WP-I7-102/-106 |
| OE-78 | PostgreSQL 17 oder 18; Keycloak-HA; Prometheus-Endpunkt | 14 O-14-06, O-14-08, O-14-09 | 17; Chart-Deployment Einzelknoten, Operator für HA; kein Prometheus-Endpunkt in der CE | I7 | WP-I7-106 |
| OE-79 | PDFsharp/MigraDoc-Version | 01 O-09 | bei 6.2.4 (MIT) bleiben | Ende S3 | WP-I4-003 |
| OE-80 | `emojibase-data`-Version festschreiben | 09 O-D09-09, 17 Z-04 | Version des ersten `capture-reference`-Laufs | Start I1 | WP-I1-105 |
| OE-81 | CE-INST-004 in 00 als „angepasst“ nachtragen | 01 O-11 | nachtragen (Spiegel der Keycloak-Rolle) | Start I0 | WP-I0-003 |
| OE-82 | `ExternalLinkDto` ohne Titel/Status | 16 O-16-07 | Anzeige-Felder in `Metadata`; bei 01-Revision additiv | W1 | W1 |
| OE-83 | Paritätsläufe nach W1 mit „CE-Sicht“ | 15 O-D15-12 | nein, solange die Additiv-Regel trägt | Start W1 | W1 |

---

## 5. Bereits getroffene Entscheidungen (nicht erneut fragen)

| Thema | Entscheidung | Quelle |
|---|---|---|
| Plan-Stufen, Billing, Upsell | entfallen; alles aktiv | ADR-001 |
| Realtime | reines .NET mit YDotNet, kein Node zur Laufzeit | ADR-002 |
| Datenübernahme | Greenfield | ADR-003 |
| Betrieb | Self-hosted inkl. Airgapped | ADR-004 |
| UI | 1:1; optisch 1:1, funktionale Fehler korrigieren und dokumentieren | ADR-005, 17 Z-12 |
| Code-Hosting | nur Forgejo, stark; Forgejo-Logo darf verwendet werden | ADR-007, 17 Z-11 |
| Anmeldung | nur Keycloak (OIDC + PKCE, BFF); God-Mode-Step-up Default aus | ADR-008, ADR-009, 01 O-08 |
| Repository | `funk.` (Hauptbranch `develop`), AGPL-3.0; Übernahme von AGPL-3.0-only-Quellen (Propel, CSS, Reference-Gallery) erlaubt | ADR-009, 17 Z-11 |
| Marke und Namen | „funk.“ überall sichtbar; technische Bezeichner direkt `funk` (kein Umbenennungspaket) | ADR-009B, ADR-009C, 17 Z-110 |
| Sprachen | nur `de` (Standard) und `en`; Übersetzungsprüfung nur für diese beiden | ADR-009D, 17 Z-113 |
| Rechte-Harmonisierung | HARM-00, -03, -04, -06 angenommen | 17 Z-09 |
| Login-Theme Hell/Dunkel | übernimmt die App-Einstellung (`localStorage.theme`), Fallback `prefers-color-scheme` | 17 Z-08 |
| Test-Browser | nur Chromium, auch ab I7 | 17 Z-10 |
| Instanz-Secrets, OpenAPI | `MaskInstanceSecrets = true`; OpenAPI in Produktion standardmäßig aus, im God Mode einschaltbar | 17 Z-112 |
| `collaboration-cursor` | an (Paket D4), sobald S1-Awareness grün ist | 17 Z-109 |
| Default-Modelle für `anthropic`/`gemini` | kein Default, `LLM_MODEL` Pflicht (`DEV-AI-001`) | 11 O-D11-03 |
| Suche für Nicht-Mitglieder | 403 beibehalten (`DEV-SRCH-011`) | 11 O-D11-01, 05 Anhang B |
| Galerie im Release-Image | nein; nur im Profil `test` unter `/__gallery/` | 08 O-D08-10, 17 ABG-008 |
| Webhook-Ereignisse bei Löschungen/Zuordnungen | werden ausgelöst (24 Original-Stellen + 6) | 04 O-D04-09, 17 ABG-137 |
| Mail-Bilder | Marketing-/Social-Bilder entfallen, Logos aus `assets/funk_logo.svg` | 06 O-D06-05, 17 ABG-105 |

---

## 6. Nachpflegebedarf in den Architektur-Dokumenten

Die folgenden Stellen widersprechen höherrangigen Entscheidungen oder diesem Plan. Sie werden beim Spiegeln nach `funk./docs/migration/` **nicht** stillschweigend geändert; bis zur Nachpflege gilt die rechte Spalte.

| Nr. | Stelle | Befund | gilt bis zur Nachpflege |
|---|---|---|---|
| N-P01 | 14 §3.21.1 (`push` auf `main`, `edge`-Tag auf `main`), 15 §3.15.1 G2 („vor Merge in `main`“) | widerspricht ADR-009 (Hauptbranch `develop`) | `develop` (OP-PLAN-02) |
| N-P02 | 01 §5.1 („Projekt-, Assembly- und Namespace-Präfix bleibt `Plane.*`“), 16 Kopf, 01 §7.21 (BR-02-Ausnahmen für Namespaces, `Plane:`-Schlüssel, Realm/Client/Cookie-Namen) | überholt durch ADR-009C und Z-110 | Umbenennungstabelle 17 (OP-PLAN-04) |
| N-P03 | 00 ADR-009B („i18n-Strings (alle 22 Sprachen)“) | durch ADR-009D auf `de`/`en` eingeschränkt | ADR-009D |
| N-P04 | 15 §3.15.1 G4 („L8 alle Browser“), 15 §3.1 Tabelle L8 („Firefox/WebKit nightly“), 09 D09-ADR-17 | Z-10: nur Chromium, auch kein informativer Gate-Status nötig | nur Chromium; Firefox/WebKit höchstens freiwillig informativ |
| N-P05 | 16 §4.6 („kein eigenes Arbeitspaket Erweiterungspunkte“) | Planungsauftrag verlangt eigene Pakete | OP-PLAN-01 |
| N-P06 | 15 Anhang B Spalte „Inkrement“ für die in OP-PLAN-03 genannten CE-IDs | Zuordnung nach 01/10/07/14 bzw. fachlicher Abhängigkeit geändert | plan/02 Anhang A |
| N-P07 | 04 Endpunktkatalog Spalte `increment` für die Endpunkte aus plan/02 Anhang C und die Vorab-Endpunkte | Bau früher bzw. später als notiert | plan/02 (`_data/wp-endpoints.json`) |
| N-P08 | 05 §3.15.1/14 §3.3.3 Dateinamen `plane-realm.json`, `plane-realm.test.json`, `00-plane-realm.json`, Themes `plane`/`plane-space` | ADR-009C | `funk-realm.json`, `funk-realm.test.json`, `00-funk-realm.json`, Themes `funk`/`funk-space` |
| N-P09 | 06 D06-ADR-16, 04 §3.17 (`X-Plane-Signature`, `X-Plane-Delivery`, `plane_wh_`) und 04 O-D04-02/06 O-D06-12 („nicht umbenennen“) | durch Z-110 entschieden: `X-Funk-*`, `funk_wh_`, `funk_api_` | ADR-009C |
| N-P10 | 02 O-D02-04 („Gruppensummen-Quirk beibehalten“) vs. 04 O-D04-04 („korrigieren“) | widersprüchliche Empfehlungen | OE-07 (Empfehlung: korrigieren) |
| N-P11 | 15 §3.9.1 (E2E-Selektoren auf Englisch) vs. ADR-009D (Standardsprache Deutsch) | Testsprache nicht festgelegt | OP-PLAN-07 |
| N-P12 | 01 §1.3 Zeile I0 („die 🧱-Andockstellen mit ‚ab I0‘ … H6 Hub-Gerüst“) nennt den Scope-FK-Spike nicht | Spike nur in 03/17 Z-107 | WP-I0-913 |
