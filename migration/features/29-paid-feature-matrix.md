# 29 – Bezahl-Feature-Matrix: Was ist NICHT in der Community Edition? (Konsolidierung P01–P09) – IST-Analyse

> **Gegenstand:** Plane v1.4.2 Community Edition (AGPL-3.0), Repo-Root `/home/user/plane`, gegenüber der closed-source Commercial Edition (`github.com/makeplane/plane-ee`, Helm-Chart `plane-enterprise` `version: 3.10.12`, `appVersion: "3.3.3"`, `/home/user/makeplane/helm-charts/charts/plane-enterprise/Chart.yaml` Z. 8–14) und Plane Cloud.
> **Frage des Auftraggebers:** „Welche Features sind NICHT in der Open-Source Community Edition, sondern in den Bezahl-Editionen bis zur Top-Lizenz?“ – Dieses Dokument ist die **zentrale, deduplizierte Antwort**. Es ersetzt keine Detail-Spezifikation; jede Zeile verweist auf die Detail-Dokumente `migration/features/20-*.md` bis `28-*.md`.
> **Eingaben:** alle verifizierten Feature-Listen `migration/features/_data/P01.paid.json` … `P09.paid.json` (450 Einträge), die offizielle In-Repo-Matrix `apps/web/components/workspace/billing/comparison/plans.tsx`, die Plan-Konstanten `packages/constants/src/subscription.ts` / `payment.ts`, die Detail-Dokumente 20–28 und die Offline-Developer-Docs `/home/user/makeplane/developer-docs/docs/**`.
> **Maschinenlesbare Fassung:** `migration/features/_data/paid-features.json` (Array `{id, cluster, name, min_plan, pro, business, enterprise, ce_status, confidence, doc}`, 246 Einträge, identisch mit Kap. 4).
> **Bindende Leitplanke:** `migration/architecture/00-grundsatzentscheidungen.md` – **ADR-001: keine Plan-Stufen, alle Features immer aktiv.** Die Plan-Spalten dieses Dokuments sind reine **Bestandsaufnahme**; die Zielplattform setzt **alle** 246 Features ohne Gating um (Ausnahme: reine Billing-/Lizenz-/Kontingent-Mechanik, Kap. 9).

---

## Inhaltsverzeichnis

0. Kurzantwort
1. Editionsmodell (Community vs. Commercial vs. Airgapped vs. Cloud; Pläne Free/One/Pro/Business/Enterprise bzw. Enterprise Grid)
2. Methode, Deduplizierung und Konsolidierungsregeln (inkl. Legende)
3. Widersprüche und ihre Auflösung
4. Haupttabelle – alle 246 Bezahl-Features (nach Cluster)
5. Listen nach Plan (nur Enterprise · ab Business · ab Pro · Commercial-Free · Cloud-only · Plan unklar; Abstufungen innerhalb eines Features)
6. Im CE-Code vorhanden, aber in Cloud-Free eingeschränkt (gegen den Code geprüft)
7. Coming soon / nicht verifizierbar / nicht gezählt
8. Gesamtzahlen
9. Konsequenzen für die Zielplattform (ADR-001/ADR-004)
- Anhang A: Zusammengeführte Dubletten (Mehrfach-Quellen je Feature)
- Anhang B: Vollständiger Abgleich mit `plans.tsx` und `subscription.ts`
- Anhang C: Rückverfolgung aller 450 Quell-Einträge → EE-ID
- Quellenverzeichnis

---

## 0. Kurzantwort

| Aussage | Wert | Beleg |
|---|---|---|
| Verifizierte Quell-Einträge (9 Cluster) | **450** (P01 105, P02 43, P03 46, P04 53, P05 35, P06 28, P07 46, P08 33, P09 61) | `migration/features/_data/P0*.paid.json` |
| Daraus deduplizierte, **nicht in der CE enthaltene** Features | **246** (+ 6 Kandidaten ohne Existenz-/Gating-Beleg, nicht gezählt, Kap. 7.3) | Kap. 4, Anhang C |
| … davon **nur in Enterprise (Top-Lizenz „Enterprise Grid“), nicht in Business** | **27** | Kap. 5.1 |
| … davon **ab Business, nicht in Pro** | **51** | Kap. 5.2 |
| … davon **ab Pro** | **96** (12 davon laut Matrix bereits im Legacy-Plan „One“) | Kap. 5.3 |
| … davon in **jeder Commercial-Installation** (auch Commercial-Free, aber nicht in der CE) | **16** | Kap. 5.4 |
| … davon **Cloud-only** | **2** (Storage-Kontingente, Flatfile-Importer) | Kap. 5.5 |
| … davon **Plan nicht belegt** (in Commercial/Cloud vorhanden, Plan unbekannt) | **54** | Kap. 5.6 |
| In der Top-Lizenz (Enterprise/Enterprise Grid) enthalten | **245 von 246** (einzige Ausnahme: Flatfile-Importer, nur Plane Cloud) | Kap. 4, Spalte „Enterprise“ |
| CE-Ausgangslage | **126** fehlen vollständig · **74** nur Stub/UI-Hülle (Texte, Icons, No-op-Hooks, Typen) · **44** teilweise im CE · **2** im CE vorhanden, nur in Cloud-Free gesperrt | Kap. 8.4 |
| Matrix „COMING SOON“ | **16** Features weiterhin ohne Auslieferungsbeleg · **9** inzwischen ausgeliefert | Kap. 7.1 |
| Reine Billing-/Lizenz-/Kontingent-/Vertriebsmechanik („entfällt“ nach ADR-001/ADR-004) | **14** | Kap. 9 |
| Aufgelöste Widersprüche | **14** Plan-Widersprüche zwischen Quell-Einträgen · **11** Abweichungen von `plans.tsx`/`subscription.ts` (zusammen **20** Features mit ⚠) · **28** CE-Status-Widersprüche · **25** weitere in den Quellen dokumentierte Plan-Konflikte | Kap. 3 |

**Lesehilfe in einem Satz:** Die CE entspricht funktional dem Free-Plan der Cloud (`/home/user/makeplane/developer-docs/docs/self-hosting/editions-and-versions.md` Z. 25); alles in Kap. 4 ist in der CE nicht (oder nur als Hülle/Teilfunktion) vorhanden und wird in der Commercial Edition bzw. Cloud über einen Plan (Pro, Business, Enterprise Grid) oder bereits im Commercial-Free-Tier freigeschaltet. Umgekehrt gibt es eine kleine Menge Funktionen, die die CE **trotz** `free: false` in der Matrix enthält (Kap. 6).

---

## 1. Editionsmodell

### 1.1 Editionen (Codebasen)

| Edition | Lizenz / Code | Funktionsumfang | Preis-/Lizenzmodell | Quelle |
|---|---|---|---|---|
| **Plane Cloud** | gehostet von Plane | alle Pläne Free/Pro/Business/Enterprise Grid; „New features ship here first“ | Per-Seat-Abo | `/home/user/makeplane/developer-docs/docs/self-hosting/editions-and-versions.md` Z. 9; `…/self-hosting-101.md` Z. 35, 41 |
| **Community Edition (CE)** | AGPL-3.0, eigener Codebase und Release-Zyklus (dieses Repo, v1.4.2) | „at par with the Free tier of the Cloud edition in its feature availability. To upgrade to paid plans, you must first switch to the Commercial Edition.“ | kostenlos, kein Lizenzschlüssel | `editions-and-versions.md` Z. 25; `self-hosting-101.md` Z. 58, 163; `apps/api/plane/license/models/instance.py` Z. 18–19, 29 (`InstanceEdition.PLANE_COMMUNITY`, einziger Enum-Wert); `apps/web/components/workspace/edition-badge.tsx` Z. 38 (Label „Community“) |
| **Commercial Edition** | closed-source (`github.com/makeplane/plane-ee`) | „Full feature parity with our Cloud“; Free-Tier mit „12 Free user seats per workspace“; Pro/Business/Enterprise Grid per Lizenzschlüssel | Per-Seat-Abo + Lizenz (Prime-Portal) | `editions-and-versions.md` Z. 31–37, 66; `self-hosting-101.md` Z. 54, 60; `/home/user/makeplane/helm-charts/charts/plane-enterprise/Chart.yaml` Z. 13–14 |
| **Airgapped Edition** | Commercial Edition für Umgebungen ohne Internet | „the same powerful features as the Commercial Edition“; Offline-Lizenz; Updates aus eigener Registry | „exclusively for Enterprise Grid customers with a minimum commitment of 100 seats“ | `editions-and-versions.md` Z. 41–52; `…/methods/airgapped-requirements.md` Z. 10; `…/methods/airgapped-edition.md` Z. 7–10 |

**Schema-Beziehung:** Eine CE-Datenbank wird beim Wechsel 1:1 in eine Commercial-Instanz übernommen (`/home/user/makeplane/developer-docs/docs/self-hosting/upgrade-from-community.md`; Dok. 22 §1.3) – das Commercial-Schema ist eine Obermenge des CE-Schemas. Viele EE-Felder existieren daher bereits ungenutzt im CE-Modell (z. B. `IssueType`, `Project.is_time_tracking_enabled` in `apps/api/plane/db/models/project.py` Z. 100, `DeployBoard.TYPE_CHOICES` mit `page`/`view` in `apps/api/plane/db/models/deploy_board.py` Z. 20–28) – Grundlage des CE-Status „teilweise“/„Stub“.

### 1.2 Pläne

| Plan | Repo-Bezeichner | Status / Anzeige im CE-Planvergleich | Preis laut Repo | Highlights (`planHighlights`) | Quelle |
|---|---|---|---|---|---|
| **Free** | `free` / `EProductSubscriptionEnum.FREE` | nicht gerendert („Free plan is not required to be shown in the comparison“) | 0 | „Upto 12 users“, „Pages“, „Unlimited projects“, „Unlimited cycles and modules“ | `apps/web/components/workspace/billing/comparison/base.tsx` Z. 26–28; `plans.tsx` Z. 1259–1265, 1304; `packages/types/src/payment.ts` Z. 7–13 |
| **One** (Legacy) | `one` / `ONE` | **nicht mehr erhältlich**: `isActive: false`, nicht gerendert („Plane one plan is not longer available“) | 799 „per workspace“ (Einmalpreis) | „Upto 50 users“, „OIDC and SAML“, „Active cycles“, „Limited time tracking“; `ONE_PLAN_FEATURES` (6 Einträge) | `base.tsx` Z. 29–30; `plans.tsx` Z. 1266–1275, 1305; `packages/constants/src/subscription.ts` Z. 34–41 |
| **Pro** | `pro` / `PRO` | gerendert, Badge „Popular“, Preis „a user per month“ | 8 $ (monatlich) / 6 $ (jährlich) je User; `payment.ts`: 800/7200 Cent | „Unlimited users“, „Custom work items + Properties“, „Work item templates“, „Full Time Tracking“; `PRO_PLAN_FEATURES` (6) | `plans.tsx` Z. 1276–1285, 1306; `plan-detail.tsx` Z. 41, 63; `packages/constants/src/payment.ts` Z. 35–61; `subscription.ts` Z. 25–32 |
| **Business** | `business` / `BUSINESS` | gerendert, CTA „Talk to Sales“, „Quote on request“ (`isActive: false`) | `payment.ts`: 1500 Cent/Monat, 15600 Cent/Jahr („The earliest packaging of Business …“) | „RBAC“, „Project Templates“, „Baselines And Deviations“, „Custom Reports“; `BUSINESS_PLAN_FEATURES` (6) | `plans.tsx` Z. 1286–1293, 1307; `plan-detail.tsx` Z. 41; `payment.ts` Z. 62–88; `subscription.ts` Z. 16–23 |
| **Enterprise** = heute **„Enterprise Grid“** (Top-Lizenz) | `enterprise` / `ENTERPRISE` | gerendert, CTA „Talk to Sales“ | `unit_amount: 0`, `is_active: false` | „Private + managed deployments“, „GAC“, „LDAP support“, „Databases + Formulas“; `ENTERPRISE_PLAN_FEATURES` (6) | `plans.tsx` Z. 1294–1301, 1308; `payment.ts` Z. 89–114; `subscription.ts` Z. 7–14; Docs-Badges `<Badge … text="Enterprise Grid" />` in `…/govern/ldap.md` Z. 7, `…/methods/airgapped-edition.md` Z. 7, `…/methods/fips-deployment.md` Z. 11; `self-hosting-101.md` Z. 54 („Plans are Free, Pro, Business, and Enterprise Grid.“); Blog „Introducing Enterprise Grid“ (12.06.2026): „on top of everything in Business“ (Dok. 21 Verifikation S3) |
| „Business Plus“ | – (kein Enum) | nur eine Nennung: Cloud-Spalte „Audit logs, SCIM, advanced auth → Business Plus“ | – | – | `self-hosting-101.md` Z. 42; Dok. 27 §1.2, O15 (**UNVERIFIZIERT**, ob Plan oder Add-on) |

**Zuordnung „Enterprise“ ↔ „Enterprise Grid“:** Die Spalte `enterprise` der Repo-Matrix und der heute vermarktete Top-Plan „Enterprise Grid“ werden in diesem Dokument gleichgesetzt (Spalte „Enterprise“). GAC wird in einer Quelle als „Enterprise-Add-on“ bezeichnet (Changelog 2026-04-25, Dok. 27 W20); hier dem Top-Plan zugeordnet.

### 1.3 Cloud vs. Self-hosted

| Aspekt | Befund | Quelle |
|---|---|---|
| Darstellung im CE-Planvergleich | `PlansComparison` übergibt fest `isSelfManaged`; angezeigt wird `feature["self-hosted"]?.[plan] ?? feature.cloud[plan]` – nur „Member limit“ hat einen eigenen `self-hosted`-Datensatz | `apps/web/components/workspace/billing/comparison/root.tsx` Z. 49; `base.tsx` Z. 108–112; `plans.tsx` Z. 686–692 |
| Member limit | Cloud: Free 12, Pro/Business/Enterprise „Unlimited“; Self-hosted: ~50 (Free/One), ~200 (Pro/Business), „Unlimited“ (Enterprise) – „Number of users that our standard infra supports“ | `plans.tsx` Z. 675–693 |
| Storage | ganze Sektion `cloudOnly: true` (Free 5GB/5 MB, Pro 1 TB/100 MB, Business 5 TB/200 MB, Enterprise Custom) | `plans.tsx` Z. 1026–1054 |
| OIDC | Zeile `selfHostedOnly: true` | `plans.tsx` Z. 1070–1081 |
| Sektion „Self-hosted“ | `selfHostedOnly: true` (God Mode, One-click Deployment, DigitalOcean, Heroku, AWS AMI, Private deployments) | `plans.tsx` Z. 1130–1203 |
| Versionsfolge | Cloud zuerst, „Commercial gets them next, Community last“ | `self-hosting-101.md` Z. 35 |
| Audit logs, SCIM, advanced auth | Cloud „Business Plus“; Self-hosted „Available on plans (Commercial and Airgapped)“ | `self-hosting-101.md` Z. 42 |
| Nur Cloud | Storage-Kontingente; Flatfile-Importer („only available on Plane Cloud“); Mobile-Push-Benachrichtigungen; 14-Tage-Business-Trial-Banner (`packages/i18n/src/locales/en/home.json` Z. 68–69) | Dok. 28 P09-F58/F60; Dok. 27 P08-19 |

### 1.4 Lizenzbindung (nur dokumentarisch – entfällt nach ADR-001)

| Plan | Bindung | Quelle |
|---|---|---|
| Commercial-Free | ohne Lizenz, 12 Seats je Workspace | `editions-and-versions.md` Z. 35; `self-hosting-101.md` Z. 60 |
| Pro / Business | Workspace-Lizenz „tied to a specific workspace“, „linked to both a workspace and an instance“; Sync plan, Delink | `…/manage/manage-licenses/activate-pro-and-business.md` Z. 9, 37–53 |
| Enterprise Grid | Instanz-Lizenz über God Mode, „available across all workspaces on your instance“ | `…/manage/manage-licenses/activate-enterprise.md` Z. 9, 23 |
| Airgapped | Offline-Lizenzdatei | `…/manage/manage-licenses/activate-airgapped.md`, `…/activate-airgapped-enterprise.md` |
| Gating-Infrastruktur | Go-Dienst `monitor` (Lizenzen + Feature-Flags, Prime-Server) | Dok. 22 §1.5 Nr. 3 |

### 1.5 Lesart dieser Matrix (verbindliche Regeln)

| Nr. | Regel | Begründung / Quelle |
|---|---|---|
| L1 | **CE ≡ Cloud-Free.** Ein Feature ist „Bezahl-Feature“, wenn es in der CE fehlt oder nur als Hülle/Teilfunktion existiert und in Commercial/Cloud vorhanden ist. Ausnahmen in beide Richtungen stehen in Kap. 6. | `editions-and-versions.md` Z. 25; Dok. 20 §1.1 |
| L2 | **„ab Plan“ = niedrigster heute erhältlicher Plan.** Nennt die Matrix nur „One“, gilt **Pro** (Marker ¹), weil One nicht mehr verkauft wird. | `base.tsx` Z. 29–30; `plans.tsx` Z. 1274; Tier-Regel in Dok. 21 §3, Dok. 26 §1.1, Dok. 27 §1.2 |
| L3 | **Aktuellere/spezifischere Quelle gewinnt** (Docs-Badge, docs.plane.so-Label, Blog/Changelog 2026) gegenüber der älteren Repo-Matrix; jeder Fall ist in Kap. 3 dokumentiert (Marker ⚠). | Dok. 25 §1.2, Dok. 27 §1.2 „Hinweis Aktualität“ |
| L4 | **„Commercial-Free“** = in jeder Commercial-Installation enthalten (auch ohne Lizenz), aber nicht in der CE. Wird nur gesetzt, wenn eine Quelle „all plans of the Commercial Edition“, „Commercial Edition (alle Pläne)“ oder Commercial-Infrastruktur belegt. | Dok. 22 P03-F03/F34/F35/F42; Dok. 28 P09-F24/F25/F29/F58 |
| L5 | **„unklar“** = in Commercial/Cloud belegt, Plan nicht belegt. Für die Top-Lizenz wird dann **„✓ (abgeleitet)“** gesetzt, weil Enterprise Grid „on top of everything in Business“ aufsetzt und alle Commercial-Features enthält. | Dok. 21 Verifikation S3; `self-hosting-101.md` Z. 163 |
| L6 | **„Enterprise“** = Repo-Spalte `enterprise` = „Enterprise Grid“. | Kap. 1.2 |
| L7 | Plan-Spalten sind **Bestandsaufnahme**; die Zielplattform kennt keine Pläne (ADR-001). | `migration/architecture/00-grundsatzentscheidungen.md` |

---

## 2. Methode, Deduplizierung und Konsolidierungsregeln

### 2.1 Eingaben

| Datei | Einträge | Detail-Dokument (führend für) | Bemerkung |
|---|---|---|---|
| `_data/P01.paid.json` | 105 (PF-01 … PF-105) | `20-paid-spuren-im-repo.md` | Querschnitt „Repo-Spuren“; nahezu alle Einträge sind Dubletten der Themen-Cluster |
| `_data/P02.paid.json` | 43 (F01 … F43; Reihenfolge in der JSON: F01–F14, F16–F31, F15, F32–F43) | `21-paid-api-referenz-developer-docs.md` | Querschnitt „Public API“; eigene Zeilen nur für reine API-Features |
| `_data/P03.paid.json` | 46 (P03-F01 … P03-F46) | `22-paid-architektur-selfhosting-dienste.md` | Dienste/Betrieb; Integrationen, AI, SSO werden in P08/P09 geführt |
| `_data/P04.paid.json` | 53 (WM-01 … WM-53) | `23-paid-work-management.md` | |
| `_data/P05.paid.json` | 35 (P05-01 … P05-35) | `24-paid-planung-insights-teams.md` | |
| `_data/P06.paid.json` | 28 (F01 … F29 ohne F25) | `25-paid-workflows-automation-templates.md` | F25 (Auto-Archive/Auto-Close) ist CE und bewusst nicht enthalten; `_data/P06.verify.json` (23 Korrekturen, 2 ergänzte, 13 korrigierte Features) ist in `P06.paid.json` bereits eingearbeitet |
| `_data/P07.paid.json` | 46 (P07-01 … P07-47 ohne P07-46) | `26-paid-wissen-pages-wiki.md` | P07-46 (Upgrade-/Downgrade-Flows) nicht in der JSON |
| `_data/P08.paid.json` | 33 (P08-01 … P08-31 inkl. P08-23a–d, ohne P08-30) | `27-paid-sicherheit-admin-lizenz.md` | P08-30 (IdP-Profil-Sync) ist CE |
| `_data/P09.paid.json` | 61 (P09-F01 … P09-F61) | `28-paid-integrationen-importer-ai.md` | |
| **Summe** | **450** | | Für **jeden** Cluster liegt eine verifizierte `*.paid.json` vor; die `*.author.json` (Autorenstand) wurden daher **nicht** als Quelle verwendet, kein Eintrag ist „unverifiziert mangels Verifikation“. |

### 2.2 Deduplizierung

1. **Führender Cluster („Heimat“):** Jedes Feature erhält genau einen Heimat-Cluster mit dem spezifischsten Detail-Dokument (Themen-Cluster P04–P09 vor den Querschnitts-Clustern P01–P03). ID-Schema **`EE-<Cluster>-<NNN>`**, fortlaufend je Heimat-Cluster.
2. **Gleiche Funktion in mehreren Quellen** (z. B. Epics in Dok. 20 PF-14, 21 F01, 23 WM-09) → **eine** Zeile; alle Quell-Einträge sind in Spalte „Detail-Dok.“ und in Anhang A/C genannt (158 Features haben mehr als eine Quelle).
3. **Sammel-Einträge** (z. B. Dok. 20 PF-93 „Workspace-SSO SAML/OIDC“, Dok. 22 P03-F10 „Domain Security, 2FA/Passkeys, Passwort-Policy“, Dok. 28 P09-F39 „AI-Assistent im Editor“) werden der spezifischsten Zeile **führend** und den übrigen Zeilen als **Teilaspekt** (`~`) zugeordnet.
4. **Aufgespaltene Einträge:** Dok. 25 F23 („Pre-defined Templates und Template-Marketplace“) wird in zwei Zeilen geteilt (EE-P06-023, EE-P06-024), weil die Quellen verschiedene Pläne nennen (Matrix-Zeile Pro „coming soon“ vs. Marketplace ohne Plan; Dok. 20 führt sie als PF-24 und PF-28 getrennt).
5. **Nicht gezählt** werden Einträge ohne Existenz- oder Gating-Beleg (6 Einträge, Kap. 7.3).
6. **Vollständigkeitsprüfung (Skript):** Jeder der 450 Quell-Einträge ist mindestens einer EE-ID **führend** zugeordnet oder als nicht gezählt begründet (Anhang C); keine Lücke.

### 2.3 Konsolidierungsregeln je Spalte

| Spalte | Regel |
|---|---|
| **ab Plan** | Ergebnis der Regeln L2–L5; bei Widerspruch Entscheidung laut Kap. 3 (Marker ⚠). Werte: `Pro`, `Business`, `Enterprise (Grid)`, `Commercial-Free`, `Cloud-only`, `unklar`. |
| **Pro / Business / Enterprise** | `✓` enthalten · `–` nicht enthalten · `?` nicht belegt · `✓ (…)` mit Abstufung (z. B. „2 Tage“, „Linear“) · `– (Matrix: ✓)` = ältere Matrix nennt den Plan, aktuellere Quelle nicht · `✓ (abgeleitet)` = Regel L5. |
| **CE-Status** | Wert des führenden Detail-Dokuments; abweichende Bewertungen anderer Dokumente stehen in Kap. 3.5. Werte: `fehlt` (weder Modell noch Route noch UI, höchstens ungenutzte Texte/Icons) · `Stub` (UI-Hülle, No-op-Hooks, Typen, Upsell-UI, ungenutzte Modellfelder) · `teilweise` (fachlicher Kern teilweise vorhanden) · `CE (nur Cloud-Gating)` (Funktion im CE vorhanden, nur in Cloud-Free gesperrt). Die Detail-Dokumente verwenden die Grenze „fehlt“/„Stub“ nicht einheitlich (Dok. 25 legt nur-Texte als „fehlt“ aus, Dok. 28 als „Stub“) – daher die Regel „führendes Dokument“. |
| **Konfidenz** | Stimmen alle führenden Quell-Einträge im (normalisierten) Plan überein, gilt die **höchste** Konfidenz der Quellen; bei Widerspruch die Konfidenz des Heimat-Eintrags, höchstens „mittel“; bei Abweichung von `plans.tsx`/`subscription.ts` höchstens „mittel“. Normalisierung: One → Pro, Enterprise Grid → Enterprise, „unklar“ zählt nicht als Widerspruch. Manuell gesetzt: EE-P05-020 (Auto-schedule Cycles) „niedrig“. |
| **Detail-Dok.** | `<Dok.-Nr.> <Feature-ID>`, führende Quelle zuerst (z. B. `23 WM-09 · 20 PF-14 · 21 F01`). Dok.-Nr.: 20 = `20-paid-spuren-im-repo.md`, 21 = `21-paid-api-referenz-developer-docs.md`, 22 = `22-paid-architektur-selfhosting-dienste.md`, 23 = `23-paid-work-management.md`, 24 = `24-paid-planung-insights-teams.md`, 25 = `25-paid-workflows-automation-templates.md`, 26 = `26-paid-wissen-pages-wiki.md`, 27 = `27-paid-sicherheit-admin-lizenz.md`, 28 = `28-paid-integrationen-importer-ai.md`. |

### 2.4 Legende der Marker (Spalte „ab Plan“)

| Marker | Bedeutung |
|---|---|
| ¹ | Matrix nennt bereits den Legacy-Plan **One** (nicht mehr erhältlich) → heute ab Pro (Regel L2) |
| ᶜˢ | in `plans.tsx` als **COMING SOON** markiert (Zeile, Zelle oder Sektion) bzw. auskommentierte Matrix-Zeile; Auslieferung **nicht** belegt |
| ᶜˢ⁺ | in `plans.tsx` als COMING SOON markiert, laut aktueller Doku/Changelog **inzwischen ausgeliefert** |
| ⚠ | Plan-Widerspruch (zwischen Quell-Einträgen oder gegenüber `plans.tsx`/`subscription.ts`), aufgelöst in Kap. 3 |
| ᵘ | Plan oder Existenz nur indirekt/abgeleitet bzw. als **UNVERIFIZIERT** gekennzeichnet |
| ‡ | Billing-/Lizenz-/Kontingent-/Vertriebsmechanik – **entfällt** in der Zielplattform (ADR-001/ADR-004) bzw. wird zu konfigurierbarer Instanz-Einstellung |

In `paid-features.json` sind die Marker so abgebildet: ᶜˢ → Namenszusatz „[coming soon]“, ᶜˢ⁺ → „[Matrix coming soon, ausgeliefert]“, ‡ → „[entfällt als Plan-/Billing-Mechanik]“, ¹ → Wert `pro` mit Zusatz „(Matrix: bereits One, Legacy)“; `✓/–/?` → „ja“/„nein“/„unklar“.

---
## 3. Widersprüche und ihre Auflösung

### 3.1 Strukturelle Widersprüche der Quellenlage

| Nr. | Widerspruch | Auflösung in diesem Dokument | Quelle |
|---|---|---|---|
| S1 | Die Repo-Matrix `plans.tsx` ist ein **älterer Stand** als die öffentliche Doku 2026 (Umgruppierungen z. B. Custom Automations Pro → Business, Approvals Business → Enterprise Grid, PQL Pro → Enterprise Grid). | Regel L3: aktuellere/spezifischere Quelle gewinnt; jede Abweichung in Kap. 3.3 und Anhang B. | Dok. 25 §1.2; Dok. 27 §1.2 „Hinweis Aktualität“ |
| S2 | Die Matrix führt den Plan **One**, der nicht mehr verkauft wird und nicht gerendert wird. | Regel L2 (Marker ¹): heute ab Pro; 12 Features betroffen (W01). | `base.tsx` Z. 29–30; `plans.tsx` Z. 1274 |
| S3 | Repo-Code nennt den Top-Plan `ENTERPRISE`, die Doku „Enterprise Grid“; einzelne Quellen sprechen von „Enterprise-Add-on“ (GAC) oder „Business Plus“ (Cloud). | Regel L6: `enterprise` = Enterprise Grid; „Business Plus“ nur dokumentiert (UNVERIFIZIERT). | Kap. 1.2 |
| S4 | **CE ≠ Cloud-Free** in Einzelfällen: Die Matrix markiert für Free Funktionen als gesperrt, die die CE enthält (z. B. Versions, Exports, Guests), und umgekehrt hat Cloud-/Commercial-Free Funktionen, die der CE fehlen (Importer). | Kap. 6 (gegen den Code geprüft); Plan „Commercial-Free“ (Regel L4). | `editions-and-versions.md` Z. 25 vs. `plans.tsx` |
| S5 | Das Enum `tier` der Quell-JSONs kennt keinen Wert „Free“; Dok. 28 hat Importer, die ab Commercial-Free verfügbar sind, deshalb per Konvention als „Pro“ geführt. | Plan „Commercial-Free“ (EE-P09-019/020/022/023/027/028). | Dok. 28 P09-F21 tier_details („Enum kennt keinen Wert ‚Free‘“) |
| S6 | Die Detail-Dokumente ziehen die Grenze **„fehlt“ vs. „Stub/UI-Hülle“** unterschiedlich (nur i18n-Texte/Icons: Dok. 25 „fehlt“, Dok. 28 „Stub“). | CE-Status des führenden Dokuments; 28 Abweichungen in Kap. 3.5. | Dok. 25 §2 Legende; Dok. 28 Status-Legende |
| S7 | Die Matrix-Zelle „Nested Pages“ für Business/Enterprise lautet „Word-compatible + other format downloads“ (offensichtlich vertauscht mit „Exports“). | Als Business-Feature gewertet; Zellwert als Fehler dokumentiert. | `plans.tsx` Z. 921–932; Dok. 20 PF-78; Dok. 26 P07-04 |

### 3.2 Plan-Widersprüche zwischen Quell-Einträgen (automatisch ermittelt, 14)

Ermittelt aus den führenden Quell-Einträgen je EE-ID nach Normalisierung (One → Pro, Enterprise Grid → Enterprise; „unklar“ zählt nicht als Widerspruch).

| # | ID | Feature | Plan-Angaben der Quell-Einträge | Entscheidung | Begründung |
|---|---|---|---|---|---|
| P01 | EE-P04-007 | Workspace-Level Properties und Workspace-Level Types (Workspace-Modus: Katalog, Import, Link/Unlink, Governance) | 23 WM-07: Enterprise Grid; 20 PF-07: Business; 21 F43: Enterprise Grid | Enterprise (Grid) | Matrix `plans.tsx` Z. 222–223 „Workspace-level properties and roll-ups“ ab Business (älter) vs. Doku/Blog 06/2026 „On Pro and Business plans, work item types are managed at the project level“ → Enterprise Grid |
| P02 | EE-P04-046 | Property Contexts (kontextabhängige Regeln einer Workspace-Property je Projekt-/Typ-Menge) | 23 WM-52: Enterprise Grid; 21 F40: Business | Enterprise (Grid) | folgt Workspace-Properties (Enterprise Grid); Dok. 21 F40 führt Business nach Matrix Z. 222–223 |
| P03 | EE-P05-027 | PQL (Plane Query Language) | 24 P05-29: Enterprise Grid; 20 PF-52: Pro; 21 F25: Pro | Enterprise (Grid) | Doku-Titel „PQL Enterprise Grid“ und Launch-Blog 12.05.2026 (aktueller) vs. Matrix Z. 658–668 Pro/Business/Enterprise (älter) |
| P04 | EE-P06-018 | Automation-Consumer / Outbox-Architektur (Outbox-Poller → RabbitMQ → Consumer) | 25 F18: unklar; 22 P03-F29: Pro | Commercial-Free | Commercial-Infrastruktur, kein Plan-Feature; Dok. 22 P03-F29 nennt Pro (Trigger & Action) |
| P05 | EE-P06-024 | Template-Marketplace (Publish, Kategorien, Verifizierung, Kopie) | 25 F23: Pro; 20 PF-28: unklar | unklar | Marketplace-Publish ohne Plan-Angabe |
| P06 | EE-P07-019 | Draw.io-Diagramme und -Boards in Pages | 26 P07-21: Business; 28 P09-F59: Business; 22 P03-F31: Pro | Business | Editor-Block-Doku „Advanced Page blocks“ (Business) vs. Dok. 22 P03-F31 „Pro“ (älter, nicht reproduzierbar) |
| P07 | EE-P07-041 | Pages-Public-API (v1/v2: Pages, Collections, Templates, Published Pages, Attachments, Work-Item-Pages, MCP) | 26 P07-45: unklar; 21 F33: Pro | unklar | je Ressource wie zugehöriges Feature; 402-Zeile der v2-Doku ist kein Tier-Beleg |
| P08 | EE-P08-003 | Workspace-Identity: verifizierte Domains und Workspace-SSO (SAML oder OIDC) | 27 P08-03: Business; 22 P03-F06: unklar; 20 PF-93: One | Business | plane.so/business „SSO on Cloud“ (sekundär) vs. Dok. 20 PF-93 (One, Matrix) und Dok. 22 P03-F06 (unklar) |
| P09 | EE-P08-011 | Rollen: System-Rollen / RBAC (Owner, Workspace Admin, Member, Guest; Projekt Admin, Contributor, Commenter, Guest) | 27 P08-11: Business; 20 PF-54: Pro; 21 F26: Business | Business | Matrix Pro „Pre-defined roles“ vs. Doku 2026 „exclusive to the Business plan and higher“ – aktuellere Quelle |
| P10 | EE-P08-017 | API-enabled Audit Logs / Workspace-Audit-Log (Settings + v2-API `audit-logs`) | 27 P08-18: Enterprise Grid; 20 PF-59: Business; 21 F34: Business; 22 P03-F44: Business | Enterprise (Grid) | Matrix Business „coming soon“ (älter) vs. Doku „Workspace Audit Logs Enterprise Grid“; Cloud „Business Plus“; ausgeliefert Commercial v3.1.0 |
| P11 | EE-P08-018 | Workspace-Lizenz und Seite „Billing and plans“ (Sync plan, Delink, Trial, Upgrade-Flow) | 27 P08-19: Pro; 20 PF-103: Cloud-only; 22 P03-F01: unklar | Pro | Lizenzmechanik, kein fachliches Feature; entfällt (ADR-001) |
| P12 | EE-P09-019 | Importer-Framework (Imports-Seite, Job-Status, Historie, Importer-Worker) | 28 P09-F21: Pro; 22 P03-F22: Pro | Commercial-Free | Basis-Import ab Commercial-/Cloud-Free (nicht CE); JSON-Tier „Pro“ war Konvention für den Import mit Custom Props |
| P13 | EE-P09-020 | Jira-Cloud-Importer (inkl. Custom Properties) | 28 P09-F22: Pro; 20 PF-83: Pro | Commercial-Free | Free/One „Without custom props“ (Cloud/Commercial, nicht CE) |
| P14 | EE-P09-028 | GitHub-Importer | 28 P09-F30: Pro | Commercial-Free | Free/One „Without custom props“ |

### 3.3 Abweichungen gegenüber der offiziellen In-Repo-Matrix `plans.tsx` bzw. `subscription.ts` (11)

Alle 94 Zuordnungen Repo-Zeile → EE-ID stehen in Anhang B (71 übereinstimmend, 12 One-Regel, 11 Abweichungen). Die folgenden 11 Features weichen bewusst ab (Marker ⚠, Konfidenz höchstens „mittel“):

| # | ID | Feature | Repo-Quelle (Zeilen) | Plan laut Repo | Plan in dieser Matrix | Begründung |
|---|---|---|---|---|---|---|
| M01 | EE-P04-007 | Workspace-Level Properties und Workspace-Level Types (Workspace-Modus: Katalog, Import, Link/Unlink, Governance) | `apps/web/components/workspace/billing/comparison/plans.tsx` Z. 216–225: Custom Properties (Business „Workspace-level properties and roll-ups“) | Business | Enterprise (Grid) | Matrix `plans.tsx` Z. 222–223 „Workspace-level properties and roll-ups“ ab Business (älter) vs. Doku/Blog 06/2026 „On Pro and Business plans, work item types are managed at the project level“ → Enterprise Grid |
| M02 | EE-P05-027 | PQL (Plane Query Language) | `apps/web/components/workspace/billing/comparison/plans.tsx` Z. 657–668: PQL | Pro | Enterprise (Grid) | Doku-Titel „PQL Enterprise Grid“ und Launch-Blog 12.05.2026 (aktueller) vs. Matrix Z. 658–668 Pro/Business/Enterprise (älter) |
| M03 | EE-P08-011 | Rollen: System-Rollen / RBAC (Owner, Workspace Admin, Member, Guest; Projekt Admin, Contributor, Commenter, Guest) | `apps/web/components/workspace/billing/comparison/plans.tsx` Z. 694–703: Roles (Pro „Pre-defined roles“, Business „RBAC“) | Pro | Business | Matrix Pro „Pre-defined roles“ vs. Doku 2026 „exclusive to the Business plan and higher“ – aktuellere Quelle |
| M04 | EE-P08-012 | Custom Roles (benutzerdefinierte Rollen aus Permission Schemes) | `apps/web/components/workspace/billing/comparison/plans.tsx` Z. 694–703: Roles (Beschreibung „… or create custom ones with RBAC“ = Business) | Business | Enterprise (Grid) | Doku/Changelog 2026: Custom Roles = GAC (Enterprise-Add-on/Enterprise Grid) |
| M05 | EE-P06-003 | Approval Flows an Workflow-Transitionen (Approver, `required_approvals`) | `packages/constants/src/subscription.ts` Z. 16–23: „Workflows + Approvals“ (BUSINESS_PLAN_FEATURES) / Approvals | Business | Enterprise (Grid) | Doku/Blog 2026 Enterprise Grid; Repo `subscription.ts` „Workflows + Approvals“ unter Business – aktuellere Quelle gewinnt |
| M06 | EE-P08-017 | API-enabled Audit Logs / Workspace-Audit-Log (Settings + v2-API `audit-logs`) | `apps/web/components/workspace/billing/comparison/plans.tsx` Z. 750–761: API-enabled Audit Logs (COMING SOON) | Business | Enterprise (Grid) | Matrix Business „coming soon“ (älter) vs. Doku „Workspace Audit Logs Enterprise Grid“; Cloud „Business Plus“; ausgeliefert Commercial v3.1.0 |
| M07 | EE-P06-009 | Custom Automations je Projekt (Trigger → Bedingungen → Aktionen) | `apps/web/components/workspace/billing/comparison/plans.tsx` Z. 768–778: Trigger And Action (+ PRO_PLAN_FEATURES) | Pro | Business | Matrix/PRO_PLAN_FEATURES „Trigger And Action“ ab Pro (älter) vs. Doku 2026 Business |
| M08 | EE-P07-018 | Databases + Formulas in Pages | `packages/constants/src/subscription.ts` Z. 7–14: „Databases + Formulas“ (ENTERPRISE_PLAN_FEATURES, planHighlights.enterprise) | Enterprise | Business | Matrix Business/Enterprise „coming soon“ vs. planHighlights.enterprise/ENTERPRISE_PLAN_FEATURES Enterprise; nicht ausgeliefert |
| M09 | EE-P08-003 | Workspace-Identity: verifizierte Domains und Workspace-SSO (SAML oder OIDC) | `apps/web/components/workspace/billing/comparison/plans.tsx` Z. 1059–1081: SAML / OIDC (Workspace-SSO, Dok. 20 PF-93) | One | Business | plane.so/business „SSO on Cloud“ (sekundär) vs. Dok. 20 PF-93 (One, Matrix) und Dok. 22 P03-F06 (unklar) |
| M10 | EE-P08-024 | Support-Kanäle, SLA und „Chat with us“ | `packages/constants/src/subscription.ts` Z. 7–14: „Full-suite professional services“ (ENTERPRISE_PLAN_FEATURES; betrifft nur die Abstufung, die Matrix nennt sie bereits für Business) | Enterprise | Pro | Free nur Forum; ENTERPRISE_PLAN_FEATURES nennt „Full-suite professional services“ nur für Enterprise; entfällt |
| M11 | EE-P07-015 | Page-Sharing / Access-Control (Mitglieder, Can view/comment/edit; Listenfilter `type=shared`) | `packages/i18n/src/locales/en/wiki.json` Z. 89–91: Upsell `wiki.upgrade_flow.description` „… shared pages … with Plane Pro.“ | Pro | Business | Doku „On the Business plan and above …“ vs. CE-Upsell „shared pages … with Plane Pro“ (älter) |

### 3.4 Weitere in den Quellen dokumentierte Plan-Konflikte (bereits in den Quell-Einträgen aufgelöst, 25)

| Nr. | EE-ID | Feature | Konflikt | Entscheidung | Quelle |
|---|---|---|---|---|---|
| W01 | EE-P03-009, EE-P04-019, EE-P04-028, EE-P05-022, EE-P07-001, EE-P07-007, EE-P07-008, EE-P07-010, EE-P07-012, EE-P08-001, EE-P08-002, EE-P08-014 | Installationskanäle, Bulk Ops, Time Tracking, Active Cycles, Wiki, Real-time Collab, Page-Publish, Work-Item-Embeds, Link Pages ↔ Work Items, SAML, OIDC, Guests-Kontingent | Matrix: ab **One**; aktuelle Quellen: ab **Pro** (Upsell `wiki.json` Z. 89–91 „… with Plane Pro“, Docs-Badges `saml-sso.md`/`oidc-sso.md` Z. 7 „Pro“, Doku-Labels „Work item Pro“, „Publish erfordert Pro“, Billing-Karte „1:5 Guests“ bei Pro) | **Pro** (Regel L2, Marker ¹) | `plans.tsx` Z. 162–203, 819–874, 705–715, 1059–1081, 1146–1189; Dok. 20, 21 F07/F13/F14, 26 P07-01/07/08/11/13, 27 P08-01/02/14 |
| W02 | EE-P04-009 | Epics | Matrix + Doku-Label „Pro“ vs. Plane University „Business“ | Pro | Dok. 20 PF-14; Dok. 23 WM-09 |
| W03 | EE-P04-011 | Initiatives | University-Kurs 05 „Pro“ vs. andere University-Seite „Business“; Sub-Initiativen „nur Enterprise“ (plane-vs-linear) | Pro; Sub-Initiativen UNVERIFIZIERT | Dok. 21 F02; Dok. 23 WM-11 |
| W04 | EE-P05-026 | Publish Views | Matrix Pro vs. `ONE_PLAN_FEATURES` „Real-time collab + public views and page“ (One) | Pro (beide Lesarten ergeben nach L2 Pro) | `subscription.ts` Z. 37; Dok. 24 P05-28 |
| W05 | EE-P05-021 | Auto-transfer / Auto-Rollover | Matrix Pro (nicht coming soon) vs. University 201/09 „Cycle Automation“ Business | Pro (spezifischere Matrix-Zeile) | `plans.tsx` Z. 249–259; Dok. 23 WM-28; Dok. 24 P05-22 |
| W06 | EE-P06-001 | Workflows (Default-Workflow) | Business (Doku 2026, `BUSINESS_PLAN_FEATURES`) vs. WebSearch plane.so/pricing „a single workflow per project“ ab Pro | Business; Pro-Angabe UNVERIFIZIERT | Dok. 25 F01, O21; Dok. 20 PF-68, OP-02 |
| W07 | EE-P06-013, EE-P06-019 | Global Automations, Plane Runner | Doku „nur Enterprise Grid“ vs. Screenshot `create-webhook.webp` (Business-Workspace mit Sidebar-Einträgen „Automations“, „Plane Runner“) | Enterprise (Sperre im Screenshot nicht erkennbar) | Dok. 25 F13/F19, D11 |
| W08 | EE-P04-016 | Customers | University 202 „Business tier“ vs. frühere Suchzusammenfassung „Pro customer profiles“ | Business; Pro-Angabe verworfen | Dok. 20 PF-41/K01; Dok. 23 WM-16 |
| W09 | EE-P07-004 | Nested Pages | Business (Matrix, `BUSINESS_PLAN_FEATURES`, Doku) vs. Suchzusammenfassung plane.so/pricing.md „Pro“ (nicht reproduzierbar) | Business | Dok. 26 P07-04 |
| W10 | EE-P07-013 | Inline-Kommentare | Guide/Blog „Business“ vs. Vergleichsblog „inline and page-level comments … Pro and above“ | Business | Dok. 26 P07-14 |
| W11 | EE-P07-025, EE-P07-026 | AI-Block, Proposals | Doku/Guide „Business“ vs. Blog „Pro+“ (vor dem Launch 2026-06-15) | Business | Dok. 26 P07-28/29; Dok. 28 P09-F39 |
| W12 | EE-P09-030, EE-P09-043 | Plane AI, AI-Credits | Cloud: Credits je bezahltem Seat ab Pro (1,000); Drittquellen Free 500 / Business 2,000; „Kontingent je Workspace“ (ai-usage) vs. „je Seat“ (plane-ai-credits); Self-hosted „Commercial Edition“ ohne Plan | Pro; Credits entfallen | Dok. 22 P03-F12; Dok. 28 P09-F33/F46 |
| W13 | EE-P03-002 | Airgapped Edition | „exclusively for Enterprise Grid customers … 100 seats“ vs. Doku zur Aktivierung von Pro/Business auf Airgapped (`activate-airgapped.md`) | Enterprise | Dok. 27 P08-21/23b, O14 |
| W14 | EE-P07-005 | Page-Versionen | Matrix „2 days“/„3 months“/„Unlimited“ vs. Preisseite „20 versions / 30 days“, „60 versions / 90 days“, „Unlimited“ | beide Stände dokumentiert; ab Pro | `plans.tsx` Z. 897–907; Dok. 26 P07-05 |
| W15 | EE-P06-016 | Anzahl Automationen | Matrix Pro 5,000 – laut Doku 2026 gibt es Custom Automations erst ab Business | Matrix-Wert dokumentiert, Pro-Wert vermutlich veraltet | `plans.tsx` Z. 791–801; Dok. 25 F16 |
| W16 | EE-P04-008 | Roll-ups | Matrix Business; dieselbe Matrix-Zelle (Workspace-Properties) ist laut Doku 06/2026 Enterprise Grid | Business; Verschiebung UNVERIFIZIERT | Dok. 23 WM-08 |
| W17 | EE-P08-005 | IdP Group Sync | Blog „Enterprise Grid“ vs. docs.plane.so „Self-hosted Commercial Edition“ ohne Plan | Enterprise | Dok. 22 O1; Dok. 27 P08-05 |
| W18 | EE-P08-006 | SCIM | Cloud „Business Plus“ / Self-hosted „Available on plans“ vs. Whitepaper „Enterprise Grid“ | Enterprise (UNVERIFIZIERT) | `self-hosting-101.md` Z. 42; Dok. 27 P08-06 |
| W19 | EE-P04-006 | Formula-Properties | Dok. 21 früher „Business oder Enterprise“ (Verwechslung mit „Databases + Formulas“ in Pages) vs. Blog „Introducing Releases“ „advanced custom properties“ ab Pro | Pro | Dok. 21 F10; Dok. 23 WM-06 |
| W20 | EE-P05-001 | Teamspaces | Autorenangabe „Pro Basic / Business+ Advanced“ ohne Beleg | Pro (Abstufung entfernt) | Dok. 21 F05 |
| W21 | EE-P05-011 | Dashboard-Filter inkl. PQL | Standard-Filter wie Dashboards (Pro) vs. PQL-Anteil wie PQL (Enterprise Grid) | unklar | Dok. 24 P05-11 |
| W22 | EE-P05-032 | Text to PQL | Matrix-Zeile PQL (Pro) „Soon, you can write natural language queries“ vs. Launch-Blog „Enterprise-only“ | Enterprise (UNVERIFIZIERT) | `plans.tsx` Z. 657–668; Dok. 24 P05-35 |
| W23 | EE-P04-002, EE-P04-014, EE-P04-015, EE-P04-022, EE-P04-024 | WIT-Hierarchie, Milestones, Releases, Kopie in anderes Projekt, Custom Relations | Dok. 20 (älterer Stand) „unklar“ vs. spätere Verifikation mit Doku-Labels (Enterprise Grid, Pro, Business, Pro, Enterprise Grid) | jeweils der verifizierte Plan | Dok. 20 PF-08/17/42/38/10; Dok. 21 F06/F22/F24; Dok. 23 WM-02/14/15/25/27 |
| W24 | EE-P04-041 | Emails For Intake | Matrix „coming soon“ vs. Docs-Badge „Business“ (`configure-dns-email-service.md` Z. 7) | Business, ausgeliefert (ᶜˢ⁺) | Dok. 21 F28; Dok. 22 P03-F23 |
| W25 | EE-P08-016, EE-P08-017 | Workspace Activity Logs vs. Audit Logs | Changelog v2.2.0 „audit logs for workspace and member activity“ deutet auf ein gemeinsames Feature; Matrix trennt zwei Zeilen | getrennt geführt (Business bzw. Enterprise) | Dok. 27 P08-17/18, O20 |

### 3.5 CE-Status-Widersprüche zwischen den Detail-Dokumenten (28)

| # | ID | Feature | CE-Status der Quell-Einträge | Entscheidung |
|---|---|---|---|---|
| C01 | EE-P04-002 | Work-Item-Type-Hierarchie (Level, Parent/Child-Regeln, Bruch-Validierung; irreversibel) | 23 WM-02: teilweise; 20 PF-08: fehlt | teilweise (Wert des führenden Detail-Dokuments) |
| C02 | EE-P04-013 | Checkpoints und Updates an Projekten/Epics/Initiativen | 23 WM-13: Stub; 20 PF-16: fehlt | Stub (Wert des führenden Detail-Dokuments) |
| C03 | EE-P04-028 | Time Tracking und Worklogs (Zeit je Work Item, Worklogs-Tab, Tracked time) | 23 WM-32: teilweise; 20 PF-03: Stub; 21 F07: teilweise | teilweise (Wert des führenden Detail-Dokuments) |
| C04 | EE-P04-031 | Advanced Estimates (System `time`, Bearbeiten, Umsortieren, Systemwechsel) | 23 WM-35: teilweise; 20 PF-01: teilweise; 21 F21: Stub | teilweise (Wert des führenden Detail-Dokuments) |
| C05 | EE-P04-041 | Emails For Intake (E-Mail-Adresse je Projekt-Intake) | 23 WM-46: Stub; 20 PF-37: Stub; 21 F28: teilweise; 22 P03-F23: Stub | Stub (Wert des führenden Detail-Dokuments) |
| C06 | EE-P05-016 | Custom Reports (Berichte nach beliebiger Dimension/Metrik) | 24 P05-16: fehlt; 20 PF-50: teilweise | fehlt (Wert des führenden Detail-Dokuments) |
| C07 | EE-P05-029 | Advanced Search (OpenSearch-gestützt; Fallback Postgres) | 24 P05-31: fehlt; 20 PF-53: fehlt; 21 F20: fehlt; 22 P03-F11: teilweise | fehlt (Wert des führenden Detail-Dokuments) |
| C08 | EE-P06-019 | Plane Runner (Scripts und Functions für Automationen, Transitionen, Cron) | 25 F19: fehlt; 22 P03-F28: Stub; 28 P09-F54: Stub; 20 PF-69: fehlt | fehlt (Wert des führenden Detail-Dokuments) |
| C09 | EE-P06-021 | Work Item Templates (Projekt und Workspace, inkl. Sub-Work-Items; Templates-API) | 25 F21: Stub; 23 WM-20: Stub; 20 PF-25: Stub; 21 F37: fehlt | Stub (Wert des führenden Detail-Dokuments) |
| C10 | EE-P07-001 | Wiki (Workspace-Seiten ohne Projekt) inkl. Wiki-Home, Sidebar, Feature-Toggle | 26 P07-01: Stub; 20 PF-74: Stub; 21 F14: teilweise | Stub (Wert des führenden Detail-Dokuments) |
| C11 | EE-P08-001 | SAML-SSO instanzweit (God Mode, inkl. God-Mode-Login per SSO) | 27 P08-01: Stub; 22 P03-F04: fehlt | Stub (Wert des führenden Detail-Dokuments) |
| C12 | EE-P08-002 | OIDC-SSO instanzweit (God Mode) | 27 P08-02: Stub; 22 P03-F05: fehlt | Stub (Wert des führenden Detail-Dokuments) |
| C13 | EE-P08-005 | IdP Group Sync (OIDC-Gruppen → Workspace-/Projektrollen) | 27 P08-05: fehlt; 21 F12: fehlt; 22 P03-F08: Stub; 20 PF-98: fehlt | fehlt (Wert des führenden Detail-Dokuments) |
| C14 | EE-P08-009 | Password Policy (eigene Passwort-Richtlinien) | 27 P08-09: teilweise; 20 PF-96: fehlt | teilweise (Wert des führenden Detail-Dokuments) |
| C15 | EE-P08-010 | Domain Security (erlaubte/gesperrte Anmelde-Domains) | 27 P08-10: fehlt; 20 PF-94: fehlt; 22 P03-F10: teilweise | fehlt (Wert des führenden Detail-Dokuments) |
| C16 | EE-P08-011 | Rollen: System-Rollen / RBAC (Owner, Workspace Admin, Member, Guest; Projekt Admin, Contributor, Commenter, Guest) | 27 P08-11: teilweise; 20 PF-54: teilweise; 21 F26: fehlt | teilweise (Wert des führenden Detail-Dokuments) |
| C17 | EE-P08-021 | Prime-Portal und Monitor-Dienst (Lizenzvalidierung, Feature-Flags, Plan-Synchronisation) | 27 P08-22: Stub; 22 P03-F02: fehlt | Stub (Wert des führenden Detail-Dokuments) |
| C18 | EE-P08-023 | Storage-Limits (Workspace-Speicher, Max file size) | 27 P08-25: teilweise; 20 PF-99: fehlt | teilweise (Wert des führenden Detail-Dokuments) |
| C19 | EE-P08-024 | Support-Kanäle, SLA und „Chat with us“ | 27 P08-26: Stub; 20 PF-101: fehlt | Stub (Wert des führenden Detail-Dokuments) |
| C20 | EE-P09-006 | GitLab (gitlab.com): MR-State-Mapping, Issue Sync | 28 P09-F06: Stub; 20 PF-85: fehlt; 22 P03-F16: Stub | Stub (Wert des führenden Detail-Dokuments) |
| C21 | EE-P09-008 | Bitbucket Cloud und Bitbucket Data Center | 28 P09-F08: Stub; 20 PF-88: fehlt; 22 P03-F17: Stub | Stub (Wert des führenden Detail-Dokuments) |
| C22 | EE-P09-012 | Sentry-Integration | 28 P09-F12: Stub; 20 PF-87: fehlt; 22 P03-F19: Stub | Stub (Wert des führenden Detail-Dokuments) |
| C23 | EE-P09-018 | OAuth Bridge (externe IdP-JWTs als API-Credentials) | 28 P09-F20: Stub; 22 P03-F09: Stub; 20 PF-91: fehlt | Stub (Wert des führenden Detail-Dokuments) |
| C24 | EE-P09-029 | Mitglieder-Import per CSV (Workspace und Projekt) | 28 P09-F32: Stub; 27 P08-31: fehlt; 20 PF-60: fehlt | Stub (Wert des führenden Detail-Dokuments) |
| C25 | EE-P09-030 | Plane AI: Dienst „PI“, Workspace-Feature `pi`, Settings-Seite „Plane AI“ | 28 P09-F33: Stub; 22 P03-F12: Stub; 21 F29: fehlt; 20 PF-82: teilweise | Stub (Wert des führenden Detail-Dokuments) |
| C26 | EE-P09-044 | OAuth-App-Plattform („Build your own app“, Consent, Bot-/User-Token, Scopes, Installationen) | 28 P09-F47: Stub; 22 P03-F25: Stub; 21 F31: fehlt; 20 PF-92: fehlt | Stub (Wert des führenden Detail-Dokuments) |
| C27 | EE-P09-047 | Agents-Plattform (Agent Runs, Activities, Signals) | 28 P09-F50: Stub; 22 P03-F26: Stub; 21 F30: fehlt | Stub (Wert des führenden Detail-Dokuments) |
| C28 | EE-P09-049 | Workspace-Access-Tokens | 28 P09-F52: teilweise; 20 PF-62: fehlt | teilweise (Wert des führenden Detail-Dokuments) |

---

## 4. Haupttabelle – alle 246 Bezahl-Features

Spalten und Marker siehe Kap. 2.3/2.4. „Pro“, „Business“, „Enterprise“ geben an, ob der Plan das Feature enthält (Enterprise = Enterprise Grid, Top-Lizenz). Die Spalte „Detail-Dok.“ nennt die führende Spezifikation zuerst; dort stehen Datenmodell, API, UI-Texte, Berechtigungen und Edge-Cases. Identischer Inhalt maschinenlesbar in `migration/features/_data/paid-features.json`.

### 4.1 P01 – nur aus Repo-Spuren belegt (Dok. 20) – 2 Features

| ID | Feature | ab Plan | Pro | Business | Enterprise | CE-Status | Konfidenz | Detail-Dok. |
|---|---|---|---|---|---|---|---|---|
| EE-P01-001 | Multi-Workspace-Management (zentrale Verwaltung mehrerer Workspaces einer Organisation) | Enterprise (Grid) ᵘ | – | – | ✓ | fehlt | niedrig | 20 PF-61 |
| EE-P01-002 | Product Tour / „Get started“ (geführte Touren, Demo-Projekt, Get-started-Checkliste; i18n-Namespace `tour`) | unklar ᵘ | ? | ? | ✓ (abgeleitet) | fehlt | mittel | 20 PF-102 |

### 4.2 P02 – nur aus der API-Referenz belegt (Dok. 21) – 6 Features

| ID | Feature | ab Plan | Pro | Business | Enterprise | CE-Status | Konfidenz | Detail-Dok. |
|---|---|---|---|---|---|---|---|---|
| EE-P02-001 | Work-Item-Type-Schema-Endpunkt (Standard- und Custom-Felder eines Typs für LLM/MCP) | Pro | ✓ | ✓ | ✓ | fehlt | hoch | 21 F11 |
| EE-P02-002 | Projekt-Feature-API (`/features/` bündelt Projekt-Schalter `epics`, `work_item_types`, `parallel_cycles`, `project_updates`, `workflows`) | unklar | ? | ? | ✓ (abgeleitet) | teilweise | hoch | 21 F16 |
| EE-P02-003 | Workspace-Feature-API (`project_grouping`, `initiatives`, `teams`, `customers`, `wiki`, `pi`) | unklar | ? | ? | ✓ (abgeleitet) | fehlt | hoch | 21 F17 |
| EE-P02-004 | Workspace-Mitglied per Public-API entfernen (inkl. Deaktivierung in allen Projekten und Seat-Reduktion) | unklar | ? | ? | ✓ (abgeleitet) | teilweise | hoch | 21 F23 |
| EE-P02-005 | Public API v2 (`/api/v2/`: PATCH-only, problem+json, Offset-/Cursor-Pagination, `?fields=`/`?expand=`, Upsert, Bulk) | unklar ᵘ | ? | ? | ✓ (abgeleitet) | fehlt | hoch | 21 F32 |
| EE-P02-006 | Views-API (Projekt- und Workspace-Views in der Public-API) | unklar | ? | ? | ✓ (abgeleitet) | teilweise | mittel | 21 F36 |

### 4.3 P03 – Architektur, Self-Hosting, Betrieb (Dok. 22) – 10 Features

| ID | Feature | ab Plan | Pro | Business | Enterprise | CE-Status | Konfidenz | Detail-Dok. |
|---|---|---|---|---|---|---|---|---|
| EE-P03-001 | Health-Probes und God-Mode-„System checks“ (`/api/live/`, `/api/ready/`, `/api/health/` je Dienst) | Commercial-Free | ✓ | ✓ | ✓ | teilweise | hoch | 22 P03-F34 · 22 P03-F03 |
| EE-P03-002 | Airgapped Edition (Betrieb ohne Internet, Images aus eigener Registry, Offline-Aktivierung) | Enterprise (Grid) | – | – | ✓ | teilweise | hoch | 22 P03-F36 · 27 P08-23b · 20 PF-100 |
| EE-P03-003 | FIPS-140-3-Images / FIPS-Betriebsprofil | Enterprise (Grid) | – | – | ✓ | fehlt | hoch | 22 P03-F37 · 27 P08-23c · 20 PF-100 |
| EE-P03-004 | Betriebsfeatures des Commercial-Charts (HA, Read-Replica, External Secrets, Custom CA, Storage-Proxy, GCS, OpenTelemetry, PSA/OpenShift) | Commercial-Free | ✓ | ✓ | ✓ | teilweise | hoch | 22 P03-F38 |
| EE-P03-005 | Dedizierte External-API-Instanz (zweiter Backend-Pool für öffentlichen API-Verkehr) | Commercial-Free | ✓ | ✓ | ✓ | fehlt | mittel | 22 P03-F39 |
| EE-P03-006 | GraphQL- und Marketplace-Endpunkte (`/graphql/`, `/marketplace/`) | Commercial-Free ᵘ | ✓ | ✓ | ✓ | fehlt | niedrig | 22 P03-F40 |
| EE-P03-007 | Flux – Realtime-Event-Server (`/flux`, WebSocket mit Redis) | unklar ᵘ | ? | ? | ✓ (abgeleitet) | fehlt | niedrig | 22 P03-F41 |
| EE-P03-008 | Prime CLI und Commercial-Installationsmethoden (Installer, Backup/Restore, Docker AIO, Swarm, Podman, Coolify, Portainer) | Commercial-Free ‡ | ✓ | ✓ | ✓ | teilweise | hoch | 22 P03-F42 |
| EE-P03-009 | Installationskanäle der Matrix: One-click Deployment, DigitalOcean-Marketplace-App, Heroku-App, AWS AMI | Pro ¹‡ | ✓ | ✓ | ✓ | teilweise | hoch | 27 P08-23a · 20 PF-100 |
| EE-P03-010 | Private + managed deployments (vom Hersteller betriebene private Cloud-Instanz) | Enterprise (Grid) ᶜˢ‡ | – | – | ✓ | fehlt | hoch | 22 P03-F46 · 27 P08-23d · 20 PF-100 |

### 4.4 P04 – Work Management (Dok. 23) – 46 Features

| ID | Feature | ab Plan | Pro | Business | Enterprise | CE-Status | Konfidenz | Detail-Dok. |
|---|---|---|---|---|---|---|---|---|
| EE-P04-001 | Work Item Types auf Projekt-Ebene (Name, Beschreibung, Icon, Farbe, Default-Typ, aktiv/inaktiv, Typwechsel) | Pro | ✓ | ✓ | ✓ | teilweise | hoch | 23 WM-01 · 20 PF-05 · 21 F08 |
| EE-P04-002 | Work-Item-Type-Hierarchie (Level, Parent/Child-Regeln, Bruch-Validierung; irreversibel) | Enterprise (Grid) | – | – | ✓ | teilweise | mittel | 23 WM-02 · 20 PF-08 |
| EE-P04-003 | Custom Properties auf Projekt-Ebene (Property-Engine, Werte am Work Item) | Pro | ✓ (Projekt-Ebene) | ✓ (Matrix: + Workspace-Ebene, Roll-ups) | ✓ (wie Business) | Stub | hoch | 23 WM-03 · 20 PF-06 · 21 F09 |
| EE-P04-004 | Property-Typen (Text, Number, Dropdown, Boolean, Date, Member picker, Relation, URL, Email, File, Release picker, Formula) | Pro | ✓ | ✓ | ✓ | fehlt | mittel | 23 WM-04 |
| EE-P04-005 | Pflichtfelder, Default-Werte, Aktiv/Inaktiv und Optionen-Verwaltung von Properties | Pro | ✓ | ✓ | ✓ | fehlt | mittel | 23 WM-05 |
| EE-P04-006 | Formula-Properties (`property_type=FORMULA`) | Pro | ✓ | ✓ | ✓ | fehlt | mittel | 23 WM-06 · 21 F10 |
| EE-P04-007 | Workspace-Level Properties und Workspace-Level Types (Workspace-Modus: Katalog, Import, Link/Unlink, Governance) | Enterprise (Grid) ⚠ | – | – (Matrix: ✓) | ✓ | fehlt | mittel | 23 WM-07 · 20 PF-07 · 21 F43 |
| EE-P04-008 | Roll-ups (Property-Aggregation) | Business ᵘ | – | ✓ | ✓ | fehlt | niedrig | 23 WM-08 |
| EE-P04-009 | Epics (Work-Item-Typ Epic, Epic-Kinder, Epic-API) | Pro | ✓ | ✓ | ✓ | Stub | hoch | 23 WM-09 · 20 PF-14 · 21 F01 |
| EE-P04-010 | Epic-Fortschritt und Epic-Updates | Pro | ✓ | ✓ | ✓ | Stub | mittel | 23 WM-10 |
| EE-P04-011 | Initiatives (Bündelung von Epics/Projekten bzw. Work Items) | Pro ᶜˢ⁺ | ✓ | ✓ | ✓ | Stub | hoch | 23 WM-11 · 20 PF-15 · 21 F02 |
| EE-P04-012 | Initiative-Labels | Pro | ✓ | ✓ | ✓ | fehlt | hoch | 23 WM-12 · 21 F03 |
| EE-P04-013 | Checkpoints und Updates an Projekten/Epics/Initiativen | Pro ᶜˢ | ✓ | ✓ | ✓ | Stub | niedrig | 23 WM-13 · 20 PF-16 |
| EE-P04-014 | Milestones (Projekt-Meilensteine, Work-Item-Zuordnung) | Pro | ✓ | ✓ | ✓ | Stub | hoch | 23 WM-14 · 21 F06 · 20 PF-17 |
| EE-P04-015 | Releases (Workspace- und Projekt-Releases, Tags, Labels, Links, Kommentare, Changelog) | Business | – | ✓ | ✓ | fehlt | hoch | 23 WM-15 · 21 F24 · 20 PF-42 |
| EE-P04-016 | Customers (Kundenprofile, Work-Item-Verknüpfung) | Business | – | ✓ | ✓ | fehlt | hoch | 23 WM-16 · 20 PF-41 · 21 F04 |
| EE-P04-017 | Customer Requests | Business | – | ✓ | ✓ | fehlt | mittel | 23 WM-17 · 21 F04 |
| EE-P04-018 | Customer Properties | Business | – | ✓ | ✓ | fehlt | mittel | 23 WM-18 · 21 F04 |
| EE-P04-019 | Bulk Ops (Mehrfachauswahl, Property-Änderung, Archivieren, Löschen, Abonnieren) | Pro ¹ | ✓ (All props) | ✓ (+ Transfers/Conversions ᶜˢ) | ✓ (+ Transfers/Conversions ᶜˢ) | Stub | hoch | 23 WM-22 · 20 PF-02 |
| EE-P04-020 | Work Item Transfers (Work Item in anderes Projekt oder anderen Cycle verschieben) | Pro | ✓ | ✓ | ✓ | teilweise | mittel | 23 WM-23 · 20 PF-11 |
| EE-P04-021 | Conversions (Work Item ↔ Epic; Bulk-Conversions) | unklar ᶜˢᵘ | ? | ✓ (Bulk ᶜˢ) | ✓ (Bulk ᶜˢ) | Stub | niedrig | 23 WM-24 |
| EE-P04-022 | Kopie eines Work Items in ein anderes Projekt („Duplicate work items and epics across projects“) | Pro | ✓ | ✓ | ✓ | Stub | mittel | 23 WM-25 · 20 PF-38 |
| EE-P04-023 | Dependencies in Gantt (Starts/Finishes Before/After, Verbindungslinien, abhängige Verschiebung; Dependencies-API) | Pro | ✓ | ✓ | ✓ | teilweise | hoch | 23 WM-26 · 20 PF-09 · 21 F39 |
| EE-P04-024 | Custom Relations (frei definierbare Relationstypen, Workspace-Settings „Relations“) | Enterprise (Grid) | – | – | ✓ | fehlt | mittel | 23 WM-27 · 21 F22 · 20 PF-10 |
| EE-P04-025 | Eingebauter Relationstyp „Implements“ / „Implemented by“ | unklar | ? | ? | ✓ (abgeleitet) | teilweise | mittel | 23 WM-53 · 20 PF-10 |
| EE-P04-026 | Module Overview (Übersicht mit Details und Fortschrittsdiagrammen je Modul) | Pro | ✓ | ✓ | ✓ | teilweise | niedrig | 23 WM-30 · 20 PF-18 |
| EE-P04-027 | Auto-assignment in Modules (Zuweisungsregeln Linear, Round Robin, Capacity) | Pro | ✓ (Linear) | ✓ (Round-robin, Capacity) | ✓ (Round-robin, Capacity) | fehlt | niedrig | 23 WM-31 · 20 PF-19 · 25 F29 |
| EE-P04-028 | Time Tracking und Worklogs (Zeit je Work Item, Worklogs-Tab, Tracked time) | Pro ¹ | ✓ (Historical timesheets) | ✓ (+ Approvals) | ✓ (+ Approvals) | teilweise | hoch | 23 WM-32 · 20 PF-03 · 21 F07 |
| EE-P04-029 | Timesheets / Worklog-Downloads (Workspace-Settings „Worklogs“) | Pro | ✓ | ✓ | ✓ | fehlt | mittel | 23 WM-33 |
| EE-P04-030 | Timesheet-Approvals | Business | – | ✓ | ✓ | fehlt | niedrig | 23 WM-34 |
| EE-P04-031 | Advanced Estimates (System `time`, Bearbeiten, Umsortieren, Systemwechsel) | Pro | ✓ (Advanced) | ✓ (Advanced) | ✓ (Advanced) | teilweise | hoch | 23 WM-35 · 20 PF-01 · 21 F21 |
| EE-P04-032 | Public, Private und Secret Projects (Stufe „Private mit Beitrittsgenehmigung“) | Pro | ✓ | ✓ | ✓ | teilweise | mittel | 23 WM-36 · 20 PF-20 |
| EE-P04-033 | State of Projects / Project States (Project Grouping) | Pro | ✓ | ✓ | ✓ | fehlt | mittel | 23 WM-37 · 20 PF-21 · 21 F18 |
| EE-P04-034 | Project Labels | unklar | ? | ? | ✓ (abgeleitet) | fehlt | mittel | 23 WM-38 · 20 PF-21 · 21 F18 |
| EE-P04-035 | Project Overview (Projekt-Übersichtsseite: Snapshot, Links, Attachments, Milestones) | Pro ᶜˢᵘ | ✓ | ✓ | ✓ | Stub | mittel | 23 WM-39 · 20 PF-22 |
| EE-P04-036 | Project Updates (Status-Updates On-Track/Off-Track/At-Risk mit Kommentaren/Reaktionen) | Pro ᶜˢᵘ | ✓ | ✓ | ✓ | Stub | mittel | 23 WM-40 · 20 PF-23 · 21 F27 |
| EE-P04-037 | Baselines And Deviations | Business | – | ✓ | ✓ | fehlt | niedrig | 23 WM-42 · 20 PF-32 |
| EE-P04-038 | Custom SLAs (SLA-Matrizen für zeitkritische Work Items) | Business | – | ✓ | ✓ | fehlt | niedrig | 23 WM-43 · 20 PF-35 |
| EE-P04-039 | Intake Forms (extern erreichbare Web-Formulare) | Business | – | ✓ | ✓ | Stub | hoch | 23 WM-44 · 20 PF-36 |
| EE-P04-040 | Intake Assignees / Intake responsibility (Standard-Bearbeiter, Benachrichtigung) | Business | – | ✓ | ✓ | teilweise | mittel | 23 WM-45 · 20 PF-34 |
| EE-P04-041 | Emails For Intake (E-Mail-Adresse je Projekt-Intake) | Business ᶜˢ⁺ | – | ✓ | ✓ | Stub | hoch | 23 WM-46 · 20 PF-37 · 21 F28 · 22 P03-F23 |
| EE-P04-042 | Work-Item-Votes in der App (Up-/Downvotes an Work Items, Epics, Intake) | unklar | ? | ? | ✓ (abgeleitet) | teilweise | hoch | 23 WM-48 · 20 PF-40 |
| EE-P04-043 | Kommentar-Antworten (Reply-Threads unter Work-Item-Kommentaren) | unklar | ? | ? | ✓ (abgeleitet) | teilweise | mittel | 23 WM-49 · 20 PF-39 |
| EE-P04-044 | Projektübergreifende Sub-Work-Items | unklar | ? | ? | ✓ (abgeleitet) | fehlt | mittel | 23 WM-50 |
| EE-P04-045 | Workspace Governance für States und Labels (Label-Scopes, Sperre der Projekt-Bearbeitung) | Enterprise (Grid) | – | – | ✓ | teilweise | mittel | 23 WM-51 |
| EE-P04-046 | Property Contexts (kontextabhängige Regeln einer Workspace-Property je Projekt-/Typ-Menge) | Enterprise (Grid) ⚠ᵘ | – | – (Dok. 21: ✓) | ✓ | fehlt | niedrig | 23 WM-52 · 21 F40 |

### 4.5 P05 – Planung, Insights, Teams (Dok. 24) – 32 Features

| ID | Feature | ab Plan | Pro | Business | Enterprise | CE-Status | Konfidenz | Detail-Dok. |
|---|---|---|---|---|---|---|---|---|
| EE-P05-001 | Teamspaces (Anlegen/Ändern/Löschen, Lead, Beschreibung, Logo, Mitglieder, Projekte) | Pro | ✓ | ✓ | ✓ | Stub | hoch | 24 P05-01 · 20 PF-30 · 21 F05 |
| EE-P05-002 | Teamspace-Work-Items (Tabs „Team“/„Project“, Gruppierung „Team project“) | Pro ᵘ | ✓ | ✓ | ✓ | Stub | mittel | 24 P05-02 |
| EE-P05-003 | Teamspace-Projekt-Work-Items | Pro ᵘ | ✓ | ✓ | ✓ | Stub | mittel | 24 P05-03 |
| EE-P05-004 | Teamspace-Views und Teamspace-Pages | Pro ᵘ | ✓ | ✓ | ✓ | Stub | mittel | 24 P05-04 · 26 P07-17 |
| EE-P05-005 | Teamspace Cycles (mehrere Cycles mehrerer Projekte gleichzeitig) | Business | – | ✓ | ✓ | fehlt | niedrig | 24 P05-05 · 20 PF-31 |
| EE-P05-006 | Teamspace-Kommentare/-Updates | unklar ᵘ | ? | ? | ✓ (abgeleitet) | Stub | mittel | 24 P05-06 |
| EE-P05-007 | Workspace-Feature „Teamspaces“ (`teams` / `is_teams_enabled`) inkl. Settings-Seite | Pro | ✓ | ✓ | ✓ | fehlt | hoch | 24 P05-07 |
| EE-P05-008 | Teamspace-bezogene Member-Auswahl, Suche, Realtime-Kontext | Pro ᵘ | ✓ | ✓ | ✓ | Stub | mittel | 24 P05-08 |
| EE-P05-009 | Dashboards (eigene Dashboards) | Pro | ✓ | ✓ | ✓ | Stub | hoch | 24 P05-09 · 20 PF-45 |
| EE-P05-010 | Dashboard-Widgets (Typen, Chart-Modelle, Achsen/Metriken, Farbpaletten) | Pro | ✓ | ✓ | ✓ | teilweise | mittel | 24 P05-10 |
| EE-P05-011 | Dashboard-Filter inkl. PQL (Ebenen source, quick, widget) | unklar ᵘ | ? | ? | ✓ (abgeleitet) | fehlt | niedrig | 24 P05-11 |
| EE-P05-012 | Dashboard-Widgets für Intake und Custom Properties | unklar ᵘ | ? | ? | ✓ (abgeleitet) | fehlt | niedrig | 24 P05-12 |
| EE-P05-013 | Dashboard-Widgets in Pages einbetten („Link dashboard widgets“-Block) | Enterprise (Grid) ᵘ | – | – | ✓ | fehlt | niedrig | 24 P05-13 · 26 P07-42 |
| EE-P05-014 | Insights (Hindsight, On-demand insights, Foresights) | Pro ᶜˢ | ✓ | ✓ | ✓ | fehlt | niedrig | 24 P05-14 · 20 PF-48 |
| EE-P05-015 | Erweiterte Analytics-Tabs (Cycles, Modules, Intake, Projects/Users) mit Tab-Gating | unklar ᵘ | ? | ? | ✓ (abgeleitet) | teilweise | mittel | 24 P05-15 · 20 PF-50 |
| EE-P05-016 | Custom Reports (Berichte nach beliebiger Dimension/Metrik) | Business ᶜˢ | – | ✓ | ✓ | fehlt | mittel | 24 P05-16 · 20 PF-50 |
| EE-P05-017 | Time Capsule (Point-in-time-Snapshots) | Business ᶜˢᵘ | – | ✓ | ✓ | fehlt | niedrig | 24 P05-17 · 20 PF-51 |
| EE-P05-018 | Progress Charts (Cycle-Fortschritt v2, Scope-Linie, Burn-down/Burn-up) | Pro | ✓ | ✓ | ✓ | teilweise | hoch | 24 P05-19 · 20 PF-46 |
| EE-P05-019 | Cycle Reports (On-demand, Permalinks) | Pro | ✓ | ✓ | ✓ | teilweise | niedrig | 24 P05-20 · 20 PF-47 |
| EE-P05-020 | Auto-schedule Cycles (wiederkehrende Cycles) | Business ᵘ | – | ✓ | ✓ | fehlt | niedrig | 24 P05-21 · 23 WM-29 · 20 PF-13 · 25 F27 |
| EE-P05-021 | Auto-transfer Cycle Work items / Auto-Rollover | Pro | ✓ | ✓ | ✓ | teilweise | mittel | 24 P05-22 · 23 WM-28 · 20 PF-12 · 25 F28 |
| EE-P05-022 | Workspace-weite Active Cycles | Pro ¹ | ✓ | ✓ | ✓ | Stub | hoch | 24 P05-23 · 20 PF-04 |
| EE-P05-023 | Parallel Cycles (mehrere aktive Cycles je Projekt) | unklar | ? | ? | ✓ (abgeleitet) | fehlt | mittel | 24 P05-24 |
| EE-P05-024 | Cycle-Aktionen „Complete“, manuelles Starten/Beenden und Archivieren laufender Cycles | unklar | ? | ? | ✓ (abgeleitet) | fehlt | mittel | 24 P05-25 |
| EE-P05-025 | Shared Views (View mit ausgewählten Mitgliedern teilen) | Pro | ✓ | ✓ | ✓ | fehlt | mittel | 24 P05-27 · 20 PF-43 |
| EE-P05-026 | Publish Views (View öffentlich ins Internet stellen) | Pro | ✓ | ✓ | ✓ | teilweise | hoch | 24 P05-28 · 20 PF-44 |
| EE-P05-027 | PQL (Plane Query Language) | Enterprise (Grid) ⚠ | – (Matrix: ✓) | – (Matrix: ✓) | ✓ | Stub | mittel | 24 P05-29 · 20 PF-52 · 21 F25 |
| EE-P05-028 | Operator-Kapseln und erweiterte Filteroperatoren (Negation, OR) im Filter-UI | Pro ᶜˢᵘ | ✓ | ✓ | ✓ | Stub | niedrig | 24 P05-30 · 20 PF-52 |
| EE-P05-029 | Advanced Search (OpenSearch-gestützt; Fallback Postgres) | Pro | ✓ | ✓ | ✓ | fehlt | hoch | 24 P05-31 · 20 PF-53 · 21 F20 · 22 P03-F11 |
| EE-P05-030 | Scheduled Comms (geplante Berichte, Benachrichtigungen, Nachrichten an Drittsysteme) | Business | – | ✓ | ✓ | fehlt | niedrig | 24 P05-32 · 20 PF-33 |
| EE-P05-031 | Home-, Your-Work- und Navigations-Erweiterungen (Widgets „New at Plane“, „Quick tutorial“, Commercial-Sidebar-Menüs) | unklar | ? | ? | ✓ (abgeleitet) | Stub | mittel | 24 P05-34 |
| EE-P05-032 | Text to PQL (natürliche Sprache → PQL, AI) | Enterprise (Grid) ᵘ | – | – | ✓ | fehlt | niedrig | 24 P05-35 |

### 4.6 P06 – Workflows, Automationen, Templates (Dok. 25) – 26 Features

| ID | Feature | ab Plan | Pro | Business | Enterprise | CE-Status | Konfidenz | Detail-Dok. |
|---|---|---|---|---|---|---|---|---|
| EE-P06-001 | Workflows: Default-Workflow je Projekt (erlaubte State-Wechsel, Mover/Reviewer, „Allow new work items“, Erzwingung) | Business | – | ✓ | ✓ | Stub | hoch | 25 F01 · 20 PF-68 · 21 F42 |
| EE-P06-002 | Mehrere, typ-spezifische Workflows je Projekt | Enterprise (Grid) | – | – | ✓ | Stub | mittel | 25 F02 · 21 F42 |
| EE-P06-003 | Approval Flows an Workflow-Transitionen (Approver, `required_approvals`) | Enterprise (Grid) ⚠ | – | – (Repo: ✓) | ✓ | fehlt | mittel | 25 F03 |
| EE-P06-004 | Transition Conditions / Workflow Hooks (pre/post, `run_script`, `send_webhook`) | Enterprise (Grid) | – | – | ✓ | fehlt | mittel | 25 F04 |
| EE-P06-005 | Workflow-Änderungshistorie und „Reset workflow“ | Business | – | ✓ | ✓ | fehlt | mittel | 25 F05 |
| EE-P06-006 | Transitions-Tab mit Time-in-State | Business | – | ✓ | ✓ | fehlt | mittel | 25 F06 |
| EE-P06-007 | Workspace Governance für Workflows (Modi, Pins, effektiver Workflow) | Enterprise (Grid) | – | – | ✓ | fehlt | mittel | 25 F07 |
| EE-P06-008 | Approvals auf Workspace-, Projekt- und Work-Item-Type-Ebene (Matrix-Zeile „Approvals“) | Business ᶜˢ | – | ✓ | ✓ | fehlt | mittel | 25 F08 · 20 PF-56 · 27 P08-15 |
| EE-P06-009 | Custom Automations je Projekt (Trigger → Bedingungen → Aktionen) | Business ⚠ | – (Matrix: ✓) | ✓ | ✓ | fehlt | mittel | 25 F09 · 20 PF-63 · 21 F35 |
| EE-P06-010 | Automation-Trigger (Work item created/updated, State changed, Assignee changed, Comment added; Scheduled) | Business | – | ✓ (Event-Trigger) | ✓ (+ Scheduled) | fehlt | mittel | 25 F10 |
| EE-P06-011 | Automation-Bedingungen („Provided“: State, Priority, Assignees, Labels, Work item type, Created by) | Business | – | ✓ | ✓ | fehlt | mittel | 25 F11 |
| EE-P06-012 | Automation-Aktionen (Change property, Add comment; Send webhook, Run script) | Business | – | ✓ (Change property, Add comment) | ✓ (+ Send webhook, Run script) | fehlt | mittel | 25 F12 |
| EE-P06-013 | Global (Workspace-)Automations („All projects“ / „Select projects“) | Enterprise (Grid) | – | – | ✓ | fehlt | mittel | 25 F13 · 20 PF-64 · 21 F35 |
| EE-P06-014 | Scheduled Automations (Fixed Daily/Weekly/Monthly oder Cron; Aktion Run script) | Enterprise (Grid) | – | – | ✓ | fehlt | mittel | 25 F14 |
| EE-P06-015 | Decisions and Loops Automation | Business ᶜˢ | – | ✓ | ✓ | fehlt | niedrig | 25 F15 · 20 PF-65 |
| EE-P06-016 | Anzahl Automationen je Workspace (Limit) | Pro ‡ | ✓ (5.000) | ✓ (10.000) | ✓ (unbegrenzt) | fehlt | hoch | 25 F16 · 20 PF-66 |
| EE-P06-017 | Automation-Ausführungslogs (Activity / Run History) | Business | – | ✓ | ✓ | fehlt | mittel | 25 F17 |
| EE-P06-018 | Automation-Consumer / Outbox-Architektur (Outbox-Poller → RabbitMQ → Consumer) | Commercial-Free ⚠ | ✓ | ✓ | ✓ | fehlt | mittel | 25 F18 · 22 P03-F29 |
| EE-P06-019 | Plane Runner (Scripts und Functions für Automationen, Transitionen, Cron) | Enterprise (Grid) | – | – | ✓ | fehlt | mittel | 25 F19 · 22 P03-F28 · 28 P09-F54 · 20 PF-69 |
| EE-P06-020 | Project Templates (States, Workflows, Automationen, Projekteinstellungen als Vorlage) | Business | – | ✓ | ✓ | Stub | hoch | 25 F20 · 23 WM-41 · 20 PF-26 · 21 F19 |
| EE-P06-021 | Work Item Templates (Projekt und Workspace, inkl. Sub-Work-Items; Templates-API) | Pro | ✓ | ✓ | ✓ | Stub | hoch | 25 F21 · 23 WM-20 · 20 PF-25 · 21 F37 |
| EE-P06-022 | Page Templates (Projekt-Pages und Wiki) | Pro | ✓ | ✓ | ✓ | fehlt | hoch | 25 F22 · 26 P07-10 · 20 PF-27 |
| EE-P06-023 | Pre-defined work item Templates | Pro ᶜˢ | ✓ | ✓ | ✓ | fehlt | mittel | 25 F23 · 23 WM-21 · 20 PF-24 |
| EE-P06-024 | Template-Marketplace (Publish, Kategorien, Verifizierung, Kopie) | unklar ⚠ᵘ | ? | ? | ✓ (abgeleitet) | fehlt | mittel | 25 F23 · 20 PF-28 |
| EE-P06-025 | Recurring Work Items | Business | – | ✓ | ✓ | fehlt | mittel | 25 F24 · 23 WM-19 · 20 PF-29 |
| EE-P06-026 | Auto-Reminders (Fälligkeits-Erinnerungen) | Business | – | ✓ | ✓ | fehlt | mittel | 25 F26 · 20 PF-67 |

### 4.7 P07 – Wissen: Pages, Wiki, Editor (Dok. 26) – 42 Features

| ID | Feature | ab Plan | Pro | Business | Enterprise | CE-Status | Konfidenz | Detail-Dok. |
|---|---|---|---|---|---|---|---|---|
| EE-P07-001 | Wiki (Workspace-Seiten ohne Projekt) inkl. Wiki-Home, Sidebar, Feature-Toggle | Pro ¹ | ✓ | ✓ | ✓ | Stub | hoch | 26 P07-01 · 20 PF-74 · 21 F14 |
| EE-P07-002 | Wiki-Collections (öffentlich, Default „General“) inkl. Drag-and-drop-Reordering | Pro | ✓ | ✓ | ✓ | fehlt | hoch | 26 P07-02 · 20 PF-74 |
| EE-P07-003 | Private Collections (nur eingeladene Mitglieder) | Business | – | ✓ | ✓ | fehlt | hoch | 26 P07-03 |
| EE-P07-004 | Nested Pages (Unterseiten, Hierarchie, Umhängen) | Business ᶜˢ⁺ | – | ✓ | ✓ | teilweise | hoch | 26 P07-04 · 20 PF-78 |
| EE-P07-005 | Page-Versionen: Aufbewahrung | Pro | ✓ (Matrix 2 Tage; Preisseite 20 Versionen/30 Tage) | ✓ (3 Monate; 60 Versionen/90 Tage) | ✓ (unbegrenzt) | teilweise | hoch | 26 P07-05 · 20 PF-76 |
| EE-P07-006 | Page-Versionen: „Highlight changes“, Vergleich zweier Versionen, Server-Restore | unklar ᵘ | ? | ? | ✓ (abgeleitet) | Stub | mittel | 26 P07-06 |
| EE-P07-007 | Real-time Collaboration: Presence-Avatare und Live-Cursor (CRDT-Sync selbst ist CE) | Pro ¹ | ✓ | ✓ | ✓ | teilweise | hoch | 26 P07-07 · 20 PF-70 |
| EE-P07-008 | Page-Publish (öffentlicher Link, Kommentare Externer, Report) | Pro ¹ | ✓ | ✓ | ✓ | Stub | hoch | 26 P07-08 · 20 PF-73 |
| EE-P07-009 | Page-Exports PDF/Word/Markdown, Hintergrund-Queue, ZIP inkl. Unterseiten | Pro | ✓ (ein Download gleichzeitig) | ✓ (Queued downloads) | ✓ (Queued downloads) | teilweise | hoch | 26 P07-09 · 20 PF-75 · 22 P03-F30 |
| EE-P07-010 | Work-Item-Embeds in Pages (Block) | Pro ¹ | ✓ | ✓ | ✓ | Stub | hoch | 26 P07-11 · 20 PF-71 |
| EE-P07-011 | Work-Item-Mentions in Pages und „Create work item from selection“ | Business | – | ✓ | ✓ | Stub | mittel | 26 P07-12 |
| EE-P07-012 | Link Pages ↔ Work Items (Pages-Sektion im Work Item; Work-Item-Pages-API) | Pro ¹ | ✓ | ✓ | ✓ | fehlt | hoch | 26 P07-13 · 20 PF-72 · 21 F13 |
| EE-P07-013 | Inline-Kommentare (an markiertem Text, Threads, Resolve) | Business | – | ✓ | ✓ | fehlt | hoch | 26 P07-14 · 20 PF-79 |
| EE-P07-014 | Page-Level-Kommentare, Kommentar-Filter, Moderation (hide/unhide) | unklar ᵘ | ? | ? | ✓ (abgeleitet) | fehlt | mittel | 26 P07-15 · 20 PF-79 |
| EE-P07-015 | Page-Sharing / Access-Control (Mitglieder, Can view/comment/edit; Listenfilter `type=shared`) | Business ⚠ | – | ✓ | ✓ | Stub | mittel | 26 P07-16 · 21 F15 · 20 PF-80 |
| EE-P07-016 | Page Labels (eigene Workspace-Seitenlabels) | Business | – | ✓ | ✓ | teilweise | hoch | 26 P07-18 |
| EE-P07-017 | Moving Pages (Projekt ↔ Projekt ↔ Teamspace ↔ Wiki/Collection) | Pro ᵘ | ✓ | ✓ | ✓ | Stub | mittel | 26 P07-19 · 20 PF-80 |
| EE-P07-018 | Databases + Formulas in Pages | Business ᶜˢ⚠ | – | ✓ (Matrix) | ✓ | fehlt | niedrig | 26 P07-20 · 20 PF-77 |
| EE-P07-019 | Draw.io-Diagramme und -Boards in Pages | Business ⚠ | – | ✓ | ✓ | fehlt | mittel | 26 P07-21 · 28 P09-F59 · 22 P03-F31 |
| EE-P07-020 | Externe Embeds / Rich Cards (Iframely), Medien per URL | Pro | ✓ | ✓ | ✓ | Stub | hoch | 26 P07-22 · 22 P03-F32 · 20 PF-81 |
| EE-P07-021 | Attachments in Pages (inkl. Office-Bearbeitung) | Pro | ✓ | ✓ | ✓ | Stub | hoch | 26 P07-23 · 20 PF-81 |
| EE-P07-022 | Video-Block | Pro | ✓ | ✓ | ✓ | fehlt | mittel | 26 P07-24 |
| EE-P07-023 | Advanced Pages Analytics (Page + Collection) | Business ᶜˢ⁺ | – | ✓ | ✓ | fehlt | hoch | 26 P07-25 · 24 P05-18 · 20 PF-49 |
| EE-P07-024 | Plane AI im Editor: Selection-Aktionen (Paraphrase, Simplify, Elaborate, Summarize, Get title, Ton) und Seitenzusammenfassung | Pro ᵘ | ✓ | ✓ | ✓ | Stub | mittel | 26 P07-27 · 28 P09-F39 |
| EE-P07-025 | Plane AI: AI-Block (`/ai`) | Business | – | ✓ | ✓ | fehlt | mittel | 26 P07-28 · 28 P09-F39 |
| EE-P07-026 | Plane AI: Prompt/Agent in Pages mit Proposals (accept/reject) | Business ᵘ | – | ✓ | ✓ | fehlt | niedrig | 26 P07-29 · 28 P09-F39 |
| EE-P07-027 | Editor-Block Columns (2/3/4 Spalten) | Pro | ✓ | ✓ | ✓ | fehlt | mittel | 26 P07-30 |
| EE-P07-028 | Editor-Block Tabs (horizontal/vertikal) | Business | – | ✓ | ✓ | fehlt | mittel | 26 P07-31 |
| EE-P07-029 | Editor-Block Toggle (aufklappbar) | Business | – | ✓ | ✓ | fehlt | mittel | 26 P07-32 |
| EE-P07-030 | Editor-Inline Status (farbiges Label) | Pro | ✓ | ✓ | ✓ | fehlt | mittel | 26 P07-33 |
| EE-P07-031 | Editor-Inline Date | Pro | ✓ | ✓ | ✓ | fehlt | hoch | 26 P07-34 |
| EE-P07-032 | Block- und Inline-Gleichungen (LaTeX) | Business | – | ✓ | ✓ | fehlt | hoch | 26 P07-35 |
| EE-P07-033 | Mermaid-Diagramm-Block | unklar | ? | ? | ✓ (abgeleitet) | fehlt | mittel | 26 P07-36 |
| EE-P07-034 | HTML-Artifact-Block (sandboxed) | Business ᵘ | – | ✓ | ✓ | fehlt | niedrig | 26 P07-37 |
| EE-P07-035 | Table-of-contents-Block | Business | – | ✓ | ✓ | fehlt | mittel | 26 P07-38 |
| EE-P07-036 | „Link pages“-Block (Live-Liste von Wiki-Seiten) | Business ᵘ | – | ✓ | ✓ | fehlt | mittel | 26 P07-39 |
| EE-P07-037 | Page-Embed-Block (`/page`) und „Linked page embed“ | Business ᵘ | – | ✓ | ✓ | fehlt | mittel | 26 P07-40 |
| EE-P07-038 | Widget-Block (Chart aus Work-Item-Daten) | unklar ᵘ | ? | ? | ✓ (abgeleitet) | fehlt | niedrig | 26 P07-41 |
| EE-P07-039 | Block-Links (Link auf einen Block kopieren) | unklar ᵘ | ? | ? | ✓ (abgeleitet) | fehlt | niedrig | 26 P07-43 |
| EE-P07-040 | Page-Benachrichtigungen (Freigabe-Mail, Page-Subscriber) | unklar ᵘ | ? | ? | ✓ (abgeleitet) | fehlt | niedrig | 26 P07-44 |
| EE-P07-041 | Pages-Public-API (v1/v2: Pages, Collections, Templates, Published Pages, Attachments, Work-Item-Pages, MCP) | unklar ⚠ | teilweise (Ressourcen der Pro-Features) | teilweise (+ Ressourcen der Business-Features) | ✓ | fehlt | mittel | 26 P07-45 · 21 F33 |
| EE-P07-042 | Erweiterte Mentions im Document-Editor (Seiten/Projekte/Zyklen/Module) und Backlinks | unklar ᵘ | ? | ? | ✓ (abgeleitet) | Stub | niedrig | 26 P07-47 |

### 4.8 P08 – Sicherheit, Administration, Lizenz (Dok. 27) – 27 Features

| ID | Feature | ab Plan | Pro | Business | Enterprise | CE-Status | Konfidenz | Detail-Dok. |
|---|---|---|---|---|---|---|---|---|
| EE-P08-001 | SAML-SSO instanzweit (God Mode, inkl. God-Mode-Login per SSO) | Pro ¹ | ✓ | ✓ | ✓ | Stub | hoch | 27 P08-01 · 22 P03-F04 · 20 PF-93 |
| EE-P08-002 | OIDC-SSO instanzweit (God Mode) | Pro ¹ | ✓ | ✓ | ✓ | Stub | hoch | 27 P08-02 · 22 P03-F05 · 20 PF-93 |
| EE-P08-003 | Workspace-Identity: verifizierte Domains und Workspace-SSO (SAML oder OIDC) | Business ⚠ᵘ | – | ✓ | ✓ | Stub | mittel | 27 P08-03 · 22 P03-F06 · 20 PF-93 |
| EE-P08-004 | LDAP-Authentifizierung | Enterprise (Grid) ᶜˢ⁺ | – | – | ✓ | Stub | hoch | 27 P08-04 · 22 P03-F07 · 20 PF-97 |
| EE-P08-005 | IdP Group Sync (OIDC-Gruppen → Workspace-/Projektrollen) | Enterprise (Grid) | – | – | ✓ | fehlt | hoch | 27 P08-05 · 21 F12 · 22 P03-F08 · 20 PF-98 |
| EE-P08-006 | SCIM-Provisioning | Enterprise (Grid) ᵘ | – | – | ✓ | fehlt | niedrig | 27 P08-06 · 20 PF-98 |
| EE-P08-007 | Zwei-Faktor-Authentifizierung | Pro | ✓ | ✓ | ✓ | fehlt | niedrig | 27 P08-07 · 20 PF-95 · 22 P03-F10 |
| EE-P08-008 | Passkeys | Pro | ✓ | ✓ | ✓ | fehlt | niedrig | 27 P08-08 · 20 PF-95 · 22 P03-F10 |
| EE-P08-009 | Password Policy (eigene Passwort-Richtlinien) | Pro | ✓ | ✓ | ✓ | teilweise | mittel | 27 P08-09 · 20 PF-96 · 22 P03-F10 |
| EE-P08-010 | Domain Security (erlaubte/gesperrte Anmelde-Domains) | Pro | ✓ | ✓ | ✓ | fehlt | niedrig | 27 P08-10 · 20 PF-94 · 22 P03-F10 |
| EE-P08-011 | Rollen: System-Rollen / RBAC (Owner, Workspace Admin, Member, Guest; Projekt Admin, Contributor, Commenter, Guest) | Business ⚠ | – (Matrix: „Pre-defined roles“) | ✓ (RBAC) | ✓ | teilweise | mittel | 27 P08-11 · 20 PF-54 · 21 F26 |
| EE-P08-012 | Custom Roles (benutzerdefinierte Rollen aus Permission Schemes) | Enterprise (Grid) ⚠ | – | – (Matrix-Text: „create custom ones with RBAC“) | ✓ | fehlt | mittel | 27 P08-12 · 21 F26 · 22 P03-F45 |
| EE-P08-013 | GAC – Granular Access Control (Permission Schemes, bedingte Rechte, effektive Berechtigungen) | Enterprise (Grid) | – | – | ✓ | fehlt | mittel | 27 P08-13 · 22 P03-F45 · 21 F26 |
| EE-P08-014 | Guests-Kontingent (5 Gäste je bezahltem Mitglied) | Pro ¹‡ | ✓ (5 je bezahltem Mitglied) | ✓ (5 je bezahltem Mitglied) | ✓ (5 je bezahltem Mitglied) | CE (nur Cloud-Gating) | hoch | 27 P08-14 · 20 PF-55 |
| EE-P08-015 | Admin Interface (Admin-Übersicht für Workspace- und Projekt-Einstellungen) | Business | – | ✓ | ✓ | fehlt | niedrig | 27 P08-16 · 20 PF-57 |
| EE-P08-016 | Workspace Activity Logs (filterbares Aktivitätsprotokoll des gesamten Workspace) | Business | – | ✓ | ✓ | teilweise | mittel | 27 P08-17 · 24 P05-33 · 20 PF-58 |
| EE-P08-017 | API-enabled Audit Logs / Workspace-Audit-Log (Settings + v2-API `audit-logs`) | Enterprise (Grid) ᶜˢ⁺⚠ | – | – (Matrix: ✓ ᶜˢ) | ✓ | fehlt | mittel | 27 P08-18 · 20 PF-59 · 21 F34 · 22 P03-F44 |
| EE-P08-018 | Workspace-Lizenz und Seite „Billing and plans“ (Sync plan, Delink, Trial, Upgrade-Flow) | Pro ⚠‡ | ✓ | ✓ | ✓ | Stub | mittel | 27 P08-19 · 20 PF-103 · 22 P03-F01 |
| EE-P08-019 | Enterprise-Grid-Instanzlizenz (God Mode → Billing) | Enterprise (Grid) ‡ | – | – | ✓ | fehlt | hoch | 27 P08-20 · 22 P03-F01 |
| EE-P08-020 | Offline-Lizenzdatei (Airgapped) | Enterprise (Grid) ‡ | – | – | ✓ | fehlt | hoch | 27 P08-21 · 22 P03-F01 |
| EE-P08-021 | Prime-Portal und Monitor-Dienst (Lizenzvalidierung, Feature-Flags, Plan-Synchronisation) | Commercial-Free ‡ | ✓ | ✓ | ✓ | Stub | hoch | 27 P08-22 · 22 P03-F02 · 22 P03-F01 |
| EE-P08-022 | Member-Limits und Seat-Berechnung (Aufhebung der Mitgliedergrenze) | Pro ‡ | ✓ (Cloud unbegrenzt; Self-hosted ~200) | ✓ (Cloud unbegrenzt; Self-hosted ~200) | ✓ (unbegrenzt) | CE (nur Cloud-Gating) | hoch | 27 P08-24 · 20 PF-55 |
| EE-P08-023 | Storage-Limits (Workspace-Speicher, Max file size) | Cloud-only ‡ | ✓ (1 TB / 100 MB) | ✓ (5 TB / 200 MB) | ✓ (individuell) | teilweise | hoch | 27 P08-25 · 20 PF-99 |
| EE-P08-024 | Support-Kanäle, SLA und „Chat with us“ | Pro ⚠‡ | ✓ (Mail, Forum, Chat; SLA) | ✓ (Full-suite professional services) | ✓ (Full-suite professional services) | Stub | mittel | 27 P08-26 · 20 PF-101 |
| EE-P08-025 | God Mode: User Management (Instanz-Benutzer, Instanz-Admins einladen, Suspend) | Commercial-Free | ✓ | ✓ | ✓ | teilweise | hoch | 27 P08-27 · 22 P03-F03 |
| EE-P08-026 | God Mode: Session-Einstellungen (Session expiry, Admin session expiry) | Commercial-Free | ✓ | ✓ | ✓ | teilweise | hoch | 27 P08-28 · 22 P03-F35 · 22 P03-F03 |
| EE-P08-027 | Argus – Sensitive-Data-/PII-Scanner | unklar | ? | ? | ✓ (abgeleitet) | fehlt | mittel | 27 P08-29 · 22 P03-F33 · 20 PF-105 |

### 4.9 P09 – Integrationen, Importer, Plane AI, Plattform (Dok. 28) – 55 Features

| ID | Feature | ab Plan | Pro | Business | Enterprise | CE-Status | Konfidenz | Detail-Dok. |
|---|---|---|---|---|---|---|---|---|
| EE-P09-001 | Integrations-Framework „Silo“, Integrations-Übersicht, Workspace-/persönliche Connections | Pro ᶜˢ⁺ | ✓ | ✓ | ✓ | Stub | mittel | 28 P09-F01 · 22 P03-F14 |
| EE-P09-002 | GitHub: Organisation verbinden, persönliches Konto, Repository-Mapping | Pro ᶜˢ⁺ | ✓ | ✓ | ✓ | Stub | hoch | 28 P09-F02 · 20 PF-84 · 22 P03-F15 |
| EE-P09-003 | GitHub: Pull-Request-Automation (PR-State-Mapping) | Pro | ✓ | ✓ | ✓ | Stub | mittel | 28 P09-F03 |
| EE-P09-004 | GitHub: Project Issue Sync (bi-/unidirektional inkl. Kommentare, Sub-Issues) | Pro | ✓ | ✓ | ✓ | Stub | mittel | 28 P09-F04 |
| EE-P09-005 | GitHub Enterprise (Server und Enterprise Cloud ghe.com) | Pro | ✓ | ✓ | ✓ | Stub | hoch | 28 P09-F05 · 20 PF-84 · 22 P03-F15 |
| EE-P09-006 | GitLab (gitlab.com): MR-State-Mapping, Issue Sync | Pro | ✓ | ✓ | ✓ | Stub | hoch | 28 P09-F06 · 20 PF-85 · 22 P03-F16 |
| EE-P09-007 | GitLab Self-managed („Gitlab Enterprise“) | Pro | ✓ | ✓ | ✓ | Stub | hoch | 28 P09-F07 · 20 PF-85 · 22 P03-F16 |
| EE-P09-008 | Bitbucket Cloud und Bitbucket Data Center | Pro | ✓ | ✓ | ✓ | Stub | mittel | 28 P09-F08 · 20 PF-88 · 22 P03-F17 |
| EE-P09-009 | Slack: Workspace verbinden, persönliches Konto, DM-Alerts | Pro ᶜˢ⁺ | ✓ | ✓ | ✓ | Stub | hoch | 28 P09-F09 · 20 PF-86 · 22 P03-F18 |
| EE-P09-010 | Slack: Projekt-Benachrichtigungen (Projekt ↔ Channel) | Pro | ✓ | ✓ | ✓ | Stub | hoch | 28 P09-F10 · 22 P03-F18 |
| EE-P09-011 | Slack: `/plane`-Slash-Command, Message-Shortcuts, Thread-Sync, Link-Unfurl | Pro | ✓ | ✓ | ✓ | fehlt | mittel | 28 P09-F11 · 22 P03-F18 |
| EE-P09-012 | Sentry-Integration | Pro | ✓ | ✓ | ✓ | Stub | hoch | 28 P09-F12 · 20 PF-87 · 22 P03-F19 |
| EE-P09-013 | HubSpot-Connector | unklar ᵘ | ? | ? | ✓ (abgeleitet) | fehlt | niedrig | 28 P09-F13 · 22 P03-F20 |
| EE-P09-014 | Cursor-Agent-Integration | unklar ᵘ | ? | ? | ✓ (abgeleitet) | fehlt | niedrig | 28 P09-F14 · 22 P03-F21 |
| EE-P09-015 | Zapier | Pro ᶜˢ | ✓ | ✓ | ✓ | fehlt | niedrig | 28 P09-F15 · 20 PF-89 |
| EE-P09-016 | Zendesk (Work Items aus Tickets) | Pro ᶜˢ | ✓ | ✓ | ✓ | fehlt | niedrig | 28 P09-F16 · 20 PF-90 |
| EE-P09-017 | Freshdesk (Work Items aus Tickets) | Pro ᶜˢ | ✓ | ✓ | ✓ | fehlt | niedrig | 28 P09-F17 · 20 PF-90 |
| EE-P09-018 | OAuth Bridge (externe IdP-JWTs als API-Credentials) | unklar | ? | ? | ✓ (abgeleitet) | Stub | hoch | 28 P09-F20 · 22 P03-F09 · 20 PF-91 |
| EE-P09-019 | Importer-Framework (Imports-Seite, Job-Status, Historie, Importer-Worker) | Commercial-Free ⚠ | ✓ (inkl. Custom Props) | ✓ (inkl. Custom Props) | ✓ (inkl. Custom Props) | Stub | mittel | 28 P09-F21 · 22 P03-F22 · 20 PF-83 |
| EE-P09-020 | Jira-Cloud-Importer (inkl. Custom Properties) | Commercial-Free ⚠ | ✓ (mit Custom Props) | ✓ (mit Custom Props) | ✓ (mit Custom Props) | Stub | mittel | 28 P09-F22 · 20 PF-83 |
| EE-P09-021 | Jira-Server/Data-Center-Importer | unklar | ? | ? | ✓ (abgeleitet) | fehlt | mittel | 28 P09-F23 |
| EE-P09-022 | Linear-Importer | Commercial-Free | ✓ | ✓ | ✓ | fehlt | mittel | 28 P09-F24 |
| EE-P09-023 | Asana-Importer | Commercial-Free | ✓ | ✓ | ✓ | fehlt | mittel | 28 P09-F25 |
| EE-P09-024 | ClickUp-Importer | unklar | ? | ? | ✓ (abgeleitet) | fehlt | mittel | 28 P09-F26 |
| EE-P09-025 | Notion-Importer | unklar ᵘ | ? | ? | ✓ (abgeleitet) | fehlt | niedrig | 28 P09-F27 |
| EE-P09-026 | Confluence-Importer | unklar | ? | ? | ✓ (abgeleitet) | fehlt | mittel | 28 P09-F28 |
| EE-P09-027 | CSV-Importer für Work Items | Commercial-Free | ✓ | ✓ | ✓ | fehlt | mittel | 28 P09-F29 |
| EE-P09-028 | GitHub-Importer | Commercial-Free ⚠ | ✓ (mit Custom Props) | ✓ (mit Custom Props) | ✓ (mit Custom Props) | Stub | mittel | 28 P09-F30 · 20 PF-83 |
| EE-P09-029 | Mitglieder-Import per CSV (Workspace und Projekt) | unklar | ? | ? | ✓ (abgeleitet) | Stub | hoch | 28 P09-F32 · 27 P08-31 · 20 PF-60 |
| EE-P09-030 | Plane AI: Dienst „PI“, Workspace-Feature `pi`, Settings-Seite „Plane AI“ | Pro | ✓ | ✓ | ✓ | Stub | hoch | 28 P09-F33 · 22 P03-F12 · 21 F29 · 20 PF-82 |
| EE-P09-031 | Pi-Chat („Plane AI“-Chat) | Pro | ✓ | ✓ | ✓ | Stub | mittel | 28 P09-F34 |
| EE-P09-032 | Plane AI: Connectors (MCP) | Pro | ✓ | ✓ | ✓ | Stub | mittel | 28 P09-F35 |
| EE-P09-033 | Plane AI: Skills | Pro | ✓ | ✓ | ✓ | Stub | mittel | 28 P09-F36 |
| EE-P09-034 | Plane AI: Memory | Pro ᵘ | ✓ | ✓ | ✓ | Stub | niedrig | 28 P09-F37 |
| EE-P09-035 | Plane AI: eingebaute Agents | Pro | ✓ | ✓ | ✓ | Stub | mittel | 28 P09-F38 |
| EE-P09-036 | Plane AI: Autopilot-Modus (Ausführung ohne Einzelbestätigung) | Pro ᵘ | ✓ | ✓ | ✓ | fehlt | niedrig | 28 P09-F61 |
| EE-P09-037 | AI-Work-Creation (Text → Work Items) und Beschreibungs-Generierung | unklar ᵘ | ? | ? | ✓ (abgeleitet) | teilweise | niedrig | 28 P09-F40 |
| EE-P09-038 | AI-Suche / Semantic Search (Embeddings, Vektorsuche) | unklar | ? | ? | ✓ (abgeleitet) | fehlt | mittel | 28 P09-F41 · 22 P03-F13 |
| EE-P09-039 | Duplicate Detection (Duplikat-Vorschläge beim Anlegen von Work Items und Intake-Requests) | unklar | ? | ? | ✓ (abgeleitet) | Stub | mittel | 28 P09-F42 · 23 WM-47 · 20 PF-104 · 22 P03-F13 |
| EE-P09-040 | AI-Aktionen Summary, Catch-up, Copy-as-prompt, AI-Filter | unklar ᵘ | ? | ? | ✓ (abgeleitet) | fehlt | niedrig | 28 P09-F43 |
| EE-P09-041 | Applets / Artifacts (AI-generierte, versionierte HTML-Dashboards) | unklar | ? | ? | ✓ (abgeleitet) | fehlt | hoch | 28 P09-F44 · 21 F41 |
| EE-P09-042 | LLM-Provider- und Embedding-Konfiguration | unklar | ? | ? | ✓ (abgeleitet) | teilweise | hoch | 28 P09-F45 |
| EE-P09-043 | AI-Usage, Credits, Token-Budget | Pro ‡ | ✓ | ✓ | ✓ | fehlt | mittel | 28 P09-F46 |
| EE-P09-044 | OAuth-App-Plattform („Build your own app“, Consent, Bot-/User-Token, Scopes, Installationen) | unklar | ? | ? | ✓ (abgeleitet) | Stub | hoch | 28 P09-F47 · 22 P03-F25 · 21 F31 · 20 PF-92 |
| EE-P09-045 | App-Marketplace | unklar | ? | ? | ✓ (abgeleitet) | Stub | mittel | 28 P09-F48 · 20 PF-92 · 22 P03-F40 |
| EE-P09-046 | App-Mentions / Bot-User | unklar | ? | ? | ✓ (abgeleitet) | teilweise | hoch | 28 P09-F49 |
| EE-P09-047 | Agents-Plattform (Agent Runs, Activities, Signals) | unklar | ? | ? | ✓ (abgeleitet) | Stub | hoch | 28 P09-F50 · 22 P03-F26 · 21 F30 |
| EE-P09-048 | Webhooks v2 (Webhook-CRUD, Delivery-Logs, v2-Events) | unklar | ? | ? | ✓ (abgeleitet) | teilweise | hoch | 28 P09-F51 · 22 P03-F24 · 21 F38 |
| EE-P09-049 | Workspace-Access-Tokens | unklar | ? | ? | ✓ (abgeleitet) | teilweise | mittel | 28 P09-F52 · 20 PF-62 |
| EE-P09-050 | MCP-Server (OAuth-Transport, Tool-Gates) | unklar | ? | ? | ✓ (abgeleitet) | teilweise | hoch | 28 P09-F53 · 22 P03-F27 |
| EE-P09-051 | Plane Compose (project-as-code CLI) | unklar | ? | ? | ✓ (abgeleitet) | fehlt | hoch | 28 P09-F55 · 22 P03-F43 |
| EE-P09-052 | Offizielle SDKs (Node, Python) | unklar | ? | ? | ✓ (abgeleitet) | fehlt | hoch | 28 P09-F56 |
| EE-P09-053 | Desktop-App (macOS, Linux) | unklar | ? | ? | ✓ (abgeleitet) | Stub | mittel | 28 P09-F57 |
| EE-P09-054 | Mobile-Apps (iOS/Android) | Commercial-Free | ✓ | ✓ | ✓ | Stub | mittel | 28 P09-F58 |
| EE-P09-055 | Flatfile-Importer (CSV über Flatfile, Beta) | Cloud-only ‡ | ? | ? | ? | fehlt | mittel | 28 P09-F60 |

---

## 5. Listen nach Plan

Jede Liste enthält die Features, deren **niedrigster** Plan (Spalte „ab Plan“) dem Abschnitt entspricht. Abstufungen innerhalb eines Features (z. B. „Pro: Linear, Business: Round-robin“) stehen zusätzlich in Kap. 5.7.

### 5.1 Nur in Enterprise (Top-Lizenz „Enterprise Grid“), nicht in Business – 27 Features

| # | ID | Feature | CE-Status | Konfidenz | Hinweis |
|---|---|---|---|---|---|
| 1 | EE-P01-001 | Multi-Workspace-Management (zentrale Verwaltung mehrerer Workspaces einer Organisation) | fehlt | niedrig | nur WebSearch-Beleg (plane.so/business, Changelog v2.2.0); Plan Enterprise Grid |
| 2 | EE-P03-002 | Airgapped Edition (Betrieb ohne Internet, Images aus eigener Registry, Offline-Aktivierung) | teilweise | hoch | „exclusively for Enterprise Grid customers with a minimum commitment of 100 seats“; Widerspruch: Doku zur Aktivierung von Pro/Business auf Airgapped (Dok. 27 O14). Betriebsmodell ist Zielvorgabe (ADR-004) |
| 3 | EE-P03-003 | FIPS-140-3-Images / FIPS-Betriebsprofil | fehlt | hoch | Docs-Badge „Enterprise Grid“ |
| 4 | EE-P03-010 | Private + managed deployments (vom Hersteller betriebene private Cloud-Instanz) | fehlt | hoch | nur Enterprise, Matrix „coming soon“; entfällt (ADR-001/ADR-004) |
| 5 | EE-P04-002 | Work-Item-Type-Hierarchie (Level, Parent/Child-Regeln, Bruch-Validierung; irreversibel) | teilweise | mittel | Doku/Blog 09.06.2026: „available only on Enterprise Grid“; Dok. 20 PF-08 älter („unklar“) |
| 6 | EE-P04-007 | Workspace-Level Properties und Workspace-Level Types (Workspace-Modus: Katalog, Import, Link/Unlink, Governance) | fehlt | mittel | Matrix `plans.tsx` Z. 222–223 „Workspace-level properties and roll-ups“ ab Business (älter) vs. Doku/Blog 06/2026 „On Pro and Business plans, work item types are managed at the project level“ → Enterprise Grid |
| 7 | EE-P04-024 | Custom Relations (frei definierbare Relationstypen, Workspace-Settings „Relations“) | fehlt | mittel | Doku-Label „Enterprise Grid“; Dok. 20 PF-10 älter („unklar“) |
| 8 | EE-P04-045 | Workspace Governance für States und Labels (Label-Scopes, Sperre der Projekt-Bearbeitung) | teilweise | mittel | nur Enterprise Grid, Self-hosted ab v3.2.0, irreversibel |
| 9 | EE-P04-046 | Property Contexts (kontextabhängige Regeln einer Workspace-Property je Projekt-/Typ-Menge) | fehlt | niedrig | folgt Workspace-Properties (Enterprise Grid); Dok. 21 F40 führt Business nach Matrix Z. 222–223 |
| 10 | EE-P05-013 | Dashboard-Widgets in Pages einbetten („Link dashboard widgets“-Block) | fehlt | niedrig | Doku-Label „Enterprise“ nur aus Autoren-Suche, UNVERIFIZIERT |
| 11 | EE-P05-027 | PQL (Plane Query Language) | Stub | mittel | Doku-Titel „PQL Enterprise Grid“ und Launch-Blog 12.05.2026 (aktueller) vs. Matrix Z. 658–668 Pro/Business/Enterprise (älter) |
| 12 | EE-P05-032 | Text to PQL (natürliche Sprache → PQL, AI) | fehlt | niedrig | Launch-Blog 12.05.2026 „Enterprise-only“ (sekundär) |
| 13 | EE-P06-002 | Mehrere, typ-spezifische Workflows je Projekt | Stub | mittel | Business nur Default-Workflow |
| 14 | EE-P06-003 | Approval Flows an Workflow-Transitionen (Approver, `required_approvals`) | fehlt | mittel | Doku/Blog 2026 Enterprise Grid; Repo `subscription.ts` „Workflows + Approvals“ unter Business – aktuellere Quelle gewinnt |
| 15 | EE-P06-004 | Transition Conditions / Workflow Hooks (pre/post, `run_script`, `send_webhook`) | fehlt | mittel | `send_webhook` zusätzlich Plan-Feature „Webhook transition conditions“ |
| 16 | EE-P06-007 | Workspace Governance für Workflows (Modi, Pins, effektiver Workflow) | fehlt | mittel | Self-hosted ab v3.2.0, irreversibel |
| 17 | EE-P06-013 | Global (Workspace-)Automations („All projects“ / „Select projects“) | fehlt | mittel | Gegenindiz: Screenshot `create-webhook.webp` (Business-Workspace mit Eintrag „Automations“) |
| 18 | EE-P06-014 | Scheduled Automations (Fixed Daily/Weekly/Monthly oder Cron; Aktion Run script) | fehlt | mittel | – |
| 19 | EE-P06-019 | Plane Runner (Scripts und Functions für Automationen, Transitionen, Cron) | fehlt | mittel | nur Enterprise Grid; Gegenindiz: Screenshot Business-Workspace; Vollspezifikation Dok. 22 P03-F28 |
| 20 | EE-P08-004 | LDAP-Authentifizierung | Stub | hoch | Matrix nur Enterprise „coming soon“; Docs-Badge „Enterprise Grid“ (ldap.md) belegt Auslieferung |
| 21 | EE-P08-005 | IdP Group Sync (OIDC-Gruppen → Workspace-/Projektrollen) | fehlt | hoch | Doku-Tag „Enterprise Grid“; nur Self-hosted Commercial, nur OIDC |
| 22 | EE-P08-006 | SCIM-Provisioning | fehlt | niedrig | Cloud „Business Plus“, Self-hosted „Available on plans (Commercial and Airgapped)“ (self-hosting-101.md Z. 42); Whitepaper Enterprise Grid; UNVERIFIZIERT |
| 23 | EE-P08-012 | Custom Roles (benutzerdefinierte Rollen aus Permission Schemes) | fehlt | mittel | Doku/Changelog 2026: Custom Roles = GAC (Enterprise-Add-on/Enterprise Grid) |
| 24 | EE-P08-013 | GAC – Granular Access Control (Permission Schemes, bedingte Rechte, effektive Berechtigungen) | fehlt | mittel | Matrix Enterprise „GAC“, ENTERPRISE_PLAN_FEATURES „GAC“ |
| 25 | EE-P08-017 | API-enabled Audit Logs / Workspace-Audit-Log (Settings + v2-API `audit-logs`) | fehlt | mittel | Matrix Business „coming soon“ (älter) vs. Doku „Workspace Audit Logs Enterprise Grid“; Cloud „Business Plus“; ausgeliefert Commercial v3.1.0 |
| 26 | EE-P08-019 | Enterprise-Grid-Instanzlizenz (God Mode → Billing) | fehlt | hoch | entfällt (ADR-001) |
| 27 | EE-P08-020 | Offline-Lizenzdatei (Airgapped) | fehlt | hoch | entfällt (ADR-001) |

### 5.2 Ab Business, nicht in Pro – 51 Features

| # | ID | Feature | CE-Status | Konfidenz | Hinweis |
|---|---|---|---|---|---|
| 1 | EE-P04-008 | Roll-ups (Property-Aggregation) | fehlt | niedrig | nur Matrix-Text; ob mit Workspace-Properties nach Enterprise Grid verschoben, UNVERIFIZIERT |
| 2 | EE-P04-015 | Releases (Workspace- und Projekt-Releases, Tags, Labels, Links, Kommentare, Changelog) | fehlt | hoch | Doku-Seiten „Releases“/„Project Releases“ Label „Business“; Dok. 20 PF-42 älter („unklar“) |
| 3 | EE-P04-016 | Customers (Kundenprofile, Work-Item-Verknüpfung) | fehlt | hoch | University 202 „Business tier“; Pro-Angabe „customer profiles“ UNVERIFIZIERT verworfen |
| 4 | EE-P04-017 | Customer Requests | fehlt | mittel | wie Customers |
| 5 | EE-P04-018 | Customer Properties | fehlt | mittel | wie Customers |
| 6 | EE-P04-030 | Timesheet-Approvals | fehlt | niedrig | Matrix „Historical timesheets and approvals“ |
| 7 | EE-P04-037 | Baselines And Deviations | fehlt | niedrig | planHighlights.business |
| 8 | EE-P04-038 | Custom SLAs (SLA-Matrizen für zeitkritische Work Items) | fehlt | niedrig | nicht zu verwechseln mit dem Support-SLA |
| 9 | EE-P04-039 | Intake Forms (extern erreichbare Web-Formulare) | Stub | hoch | BUSINESS_PLAN_FEATURES „Intake Forms“ |
| 10 | EE-P04-040 | Intake Assignees / Intake responsibility (Standard-Bearbeiter, Benachrichtigung) | teilweise | mittel | – |
| 11 | EE-P04-041 | Emails For Intake (E-Mail-Adresse je Projekt-Intake) | Stub | hoch | Matrix „coming soon“; Docs-Badge „Business“ (configure-dns-email-service.md) belegt Auslieferung |
| 12 | EE-P05-005 | Teamspace Cycles (mehrere Cycles mehrerer Projekte gleichzeitig) | fehlt | niedrig | – |
| 13 | EE-P05-016 | Custom Reports (Berichte nach beliebiger Dimension/Metrik) | fehlt | mittel | Matrix „coming soon“; planHighlights.business |
| 14 | EE-P05-017 | Time Capsule (Point-in-time-Snapshots) | fehlt | niedrig | Matrix-Zeile auskommentiert („coming soon“) |
| 15 | EE-P05-020 | Auto-schedule Cycles (wiederkehrende Cycles) | fehlt | niedrig | nur University 201/09 „Cycle Automation“ (Business); Dok. 20/25 „unklar“; Changelog v1.16.0 ohne Plan |
| 16 | EE-P05-030 | Scheduled Comms (geplante Berichte, Benachrichtigungen, Nachrichten an Drittsysteme) | fehlt | niedrig | – |
| 17 | EE-P06-001 | Workflows: Default-Workflow je Projekt (erlaubte State-Wechsel, Mover/Reviewer, „Allow new work items“, Erzwingung) | Stub | hoch | BUSINESS_PLAN_FEATURES „Workflows + Approvals“; Pro-Angabe „a single workflow per project“ UNVERIFIZIERT (Dok. 25 O21) |
| 18 | EE-P06-005 | Workflow-Änderungshistorie und „Reset workflow“ | fehlt | mittel | abgeleitet aus Workflows |
| 19 | EE-P06-006 | Transitions-Tab mit Time-in-State | fehlt | mittel | „Time in state + transitions“ ab Business |
| 20 | EE-P06-008 | Approvals auf Workspace-, Projekt- und Work-Item-Type-Ebene (Matrix-Zeile „Approvals“) | fehlt | mittel | Matrix „coming soon“; kein öffentlicher Detail-Spec |
| 21 | EE-P06-009 | Custom Automations je Projekt (Trigger → Bedingungen → Aktionen) | fehlt | mittel | Matrix/PRO_PLAN_FEATURES „Trigger And Action“ ab Pro (älter) vs. Doku 2026 Business |
| 22 | EE-P06-010 | Automation-Trigger (Work item created/updated, State changed, Assignee changed, Comment added; Scheduled) | fehlt | mittel | – |
| 23 | EE-P06-011 | Automation-Bedingungen („Provided“: State, Priority, Assignees, Labels, Work item type, Created by) | fehlt | mittel | – |
| 24 | EE-P06-012 | Automation-Aktionen (Change property, Add comment; Send webhook, Run script) | fehlt | mittel | – |
| 25 | EE-P06-015 | Decisions and Loops Automation | fehlt | niedrig | Matrix „coming soon“; ENTERPRISE_PLAN_FEATURES „Unlimited and full Automation Flows“ |
| 26 | EE-P06-017 | Automation-Ausführungslogs (Activity / Run History) | fehlt | mittel | mit Custom Automations |
| 27 | EE-P06-020 | Project Templates (States, Workflows, Automationen, Projekteinstellungen als Vorlage) | Stub | hoch | planHighlights.business, BUSINESS_PLAN_FEATURES |
| 28 | EE-P06-025 | Recurring Work Items | fehlt | mittel | i18n „Upgrade to Business to make recurring work feel effortless.“ |
| 29 | EE-P06-026 | Auto-Reminders (Fälligkeits-Erinnerungen) | fehlt | mittel | nur Web-Belege, kein Repo-Beleg |
| 30 | EE-P07-003 | Private Collections (nur eingeladene Mitglieder) | fehlt | hoch | – |
| 31 | EE-P07-004 | Nested Pages (Unterseiten, Hierarchie, Umhängen) | teilweise | hoch | Matrix „coming soon“ (Zellwert fehlerhaft), BUSINESS_PLAN_FEATURES; Doku/Blog Business+ (ausgeliefert) |
| 32 | EE-P07-011 | Work-Item-Mentions in Pages und „Create work item from selection“ | Stub | mittel | – |
| 33 | EE-P07-013 | Inline-Kommentare (an markiertem Text, Threads, Resolve) | fehlt | hoch | Gegenstimme Vergleichsblog „Pro and above“ |
| 34 | EE-P07-015 | Page-Sharing / Access-Control (Mitglieder, Can view/comment/edit; Listenfilter `type=shared`) | Stub | mittel | Doku „On the Business plan and above …“ vs. CE-Upsell „shared pages … with Plane Pro“ (älter) |
| 35 | EE-P07-016 | Page Labels (eigene Workspace-Seitenlabels) | teilweise | hoch | – |
| 36 | EE-P07-018 | Databases + Formulas in Pages | fehlt | niedrig | Matrix Business/Enterprise „coming soon“ vs. planHighlights.enterprise/ENTERPRISE_PLAN_FEATURES Enterprise; nicht ausgeliefert |
| 37 | EE-P07-019 | Draw.io-Diagramme und -Boards in Pages | fehlt | mittel | Editor-Block-Doku „Advanced Page blocks“ (Business) vs. Dok. 22 P03-F31 „Pro“ (älter, nicht reproduzierbar) |
| 38 | EE-P07-023 | Advanced Pages Analytics (Page + Collection) | fehlt | hoch | Matrix „coming soon“; Doku/Guide Business (ausgeliefert) |
| 39 | EE-P07-025 | Plane AI: AI-Block (`/ai`) | fehlt | mittel | Doku/Guide Business vs. Blog Pro+ (älter) |
| 40 | EE-P07-026 | Plane AI: Prompt/Agent in Pages mit Proposals (accept/reject) | fehlt | niedrig | Doku Business vs. Blog Pro+; Gleichsetzung „Free-form Page editing“ = Proposals UNVERIFIZIERT |
| 41 | EE-P07-028 | Editor-Block Tabs (horizontal/vertikal) | fehlt | mittel | – |
| 42 | EE-P07-029 | Editor-Block Toggle (aufklappbar) | fehlt | mittel | – |
| 43 | EE-P07-032 | Block- und Inline-Gleichungen (LaTeX) | fehlt | hoch | – |
| 44 | EE-P07-034 | HTML-Artifact-Block (sandboxed) | fehlt | niedrig | Doku-Label nur aus Autoren-Suche |
| 45 | EE-P07-035 | Table-of-contents-Block | fehlt | mittel | „Advanced Page blocks“ (Business) |
| 46 | EE-P07-036 | „Link pages“-Block (Live-Liste von Wiki-Seiten) | fehlt | mittel | Doku-Label nur aus Autoren-Suche |
| 47 | EE-P07-037 | Page-Embed-Block (`/page`) und „Linked page embed“ | fehlt | mittel | an Nested Pages gekoppelt |
| 48 | EE-P08-003 | Workspace-Identity: verifizierte Domains und Workspace-SSO (SAML oder OIDC) | Stub | mittel | plane.so/business „SSO on Cloud“ (sekundär) vs. Dok. 20 PF-93 (One, Matrix) und Dok. 22 P03-F06 (unklar) |
| 49 | EE-P08-011 | Rollen: System-Rollen / RBAC (Owner, Workspace Admin, Member, Guest; Projekt Admin, Contributor, Commenter, Guest) | teilweise | mittel | Matrix Pro „Pre-defined roles“ vs. Doku 2026 „exclusive to the Business plan and higher“ – aktuellere Quelle |
| 50 | EE-P08-015 | Admin Interface (Admin-Übersicht für Workspace- und Projekt-Einstellungen) | fehlt | niedrig | nur Matrix-Zeile |
| 51 | EE-P08-016 | Workspace Activity Logs (filterbares Aktivitätsprotokoll des gesamten Workspace) | teilweise | mittel | mögliche Verschmelzung mit Audit-Log (Dok. 27 O20) |

### 5.3 Ab Pro – 96 Features

Davon nennt die Matrix für 12 Features bereits den Legacy-Plan One (Marker ¹ in Kap. 4): EE-P03-009, EE-P04-019, EE-P04-028, EE-P05-022, EE-P07-001, EE-P07-007, EE-P07-008, EE-P07-010, EE-P07-012, EE-P08-001, EE-P08-002, EE-P08-014.

| # | ID | Feature | CE-Status | Konfidenz | Hinweis |
|---|---|---|---|---|---|
| 1 | EE-P02-001 | Work-Item-Type-Schema-Endpunkt (Standard- und Custom-Felder eines Typs für LLM/MCP) | fehlt | hoch | folgt Work Item Types/Custom Properties |
| 2 | EE-P03-009 | Installationskanäle der Matrix: One-click Deployment, DigitalOcean-Marketplace-App, Heroku-App, AWS AMI | teilweise | hoch | Matrix ab One (Legacy); CE liefert eigene Installationsskripte; Marketplace-Apps entfallen (ADR-004) |
| 3 | EE-P04-001 | Work Item Types auf Projekt-Ebene (Name, Beschreibung, Icon, Farbe, Default-Typ, aktiv/inaktiv, Typwechsel) | teilweise | hoch | – |
| 4 | EE-P04-003 | Custom Properties auf Projekt-Ebene (Property-Engine, Werte am Work Item) | Stub | hoch | – |
| 5 | EE-P04-004 | Property-Typen (Text, Number, Dropdown, Boolean, Date, Member picker, Relation, URL, Email, File, Release picker, Formula) | fehlt | mittel | Release picker setzt Releases (Business) voraus |
| 6 | EE-P04-005 | Pflichtfelder, Default-Werte, Aktiv/Inaktiv und Optionen-Verwaltung von Properties | fehlt | mittel | mit Custom Properties |
| 7 | EE-P04-006 | Formula-Properties (`property_type=FORMULA`) | fehlt | mittel | Blog „Introducing Releases“ (13.05.2026): „advanced custom properties“ ab Pro; nicht verwechseln mit „Databases + Formulas“ in Pages |
| 8 | EE-P04-009 | Epics (Work-Item-Typ Epic, Epic-Kinder, Epic-API) | Stub | hoch | Plane University nennt Business; Matrix und Doku-Label Pro gelten |
| 9 | EE-P04-010 | Epic-Fortschritt und Epic-Updates | Stub | mittel | mit Epics |
| 10 | EE-P04-011 | Initiatives (Bündelung von Epics/Projekten bzw. Work Items) | Stub | hoch | Matrix „coming soon“, inzwischen ausgeliefert (API-Referenz, University-Kurs 05 „Pro“); andere University-Seite Business; Sub-Initiativen „nur Enterprise“ UNVERIFIZIERT |
| 11 | EE-P04-012 | Initiative-Labels | fehlt | hoch | wie Initiatives |
| 12 | EE-P04-013 | Checkpoints und Updates an Projekten/Epics/Initiativen | Stub | niedrig | Checkpoints laut Matrix „coming soon“, nicht ausgeliefert (Dok. 21 F06) |
| 13 | EE-P04-014 | Milestones (Projekt-Meilensteine, Work-Item-Zuordnung) | Stub | hoch | Doku-Label „Pro“, University 07; nicht in `plans.tsx`; Dok. 20 PF-17 älter („unklar“) |
| 14 | EE-P04-019 | Bulk Ops (Mehrfachauswahl, Property-Änderung, Archivieren, Löschen, Abonnieren) | Stub | hoch | Matrix: One „Limited props“, Pro „All props“; Business/Enterprise-Zusatz „Work item transfers and conversions“ coming soon |
| 15 | EE-P04-020 | Work Item Transfers (Work Item in anderes Projekt oder anderen Cycle verschieben) | teilweise | mittel | – |
| 16 | EE-P04-022 | Kopie eines Work Items in ein anderes Projekt („Duplicate work items and epics across projects“) | Stub | mittel | Changelog v1.13.0 „Available on Pro plan“; Dok. 20 PF-38 älter („unklar“) |
| 17 | EE-P04-023 | Dependencies in Gantt (Starts/Finishes Before/After, Verbindungslinien, abhängige Verschiebung; Dependencies-API) | teilweise | hoch | – |
| 18 | EE-P04-026 | Module Overview (Übersicht mit Details und Fortschrittsdiagrammen je Modul) | teilweise | niedrig | – |
| 19 | EE-P04-027 | Auto-assignment in Modules (Zuweisungsregeln Linear, Round Robin, Capacity) | fehlt | niedrig | Semantik der Modi UNVERIFIZIERT (Dok. 25 O22) |
| 20 | EE-P04-028 | Time Tracking und Worklogs (Zeit je Work Item, Worklogs-Tab, Tracked time) | teilweise | hoch | Matrix: One „Basic“; Doku-Label „Pro“ |
| 21 | EE-P04-029 | Timesheets / Worklog-Downloads (Workspace-Settings „Worklogs“) | fehlt | mittel | Matrix „Historical timesheets“ |
| 22 | EE-P04-031 | Advanced Estimates (System `time`, Bearbeiten, Umsortieren, Systemwechsel) | teilweise | hoch | Free/One „Basic“ = CE-Umfang (points/categories) |
| 23 | EE-P04-032 | Public, Private und Secret Projects (Stufe „Private mit Beitrittsgenehmigung“) | teilweise | mittel | – |
| 24 | EE-P04-033 | State of Projects / Project States (Project Grouping) | fehlt | mittel | University-Kurs 11 Pro |
| 25 | EE-P04-035 | Project Overview (Projekt-Übersichtsseite: Snapshot, Links, Attachments, Milestones) | Stub | mittel | Matrix-Zeile auskommentiert („coming soon“); indirekt gestützt durch Pro-Milestones im Overview |
| 26 | EE-P04-036 | Project Updates (Status-Updates On-Track/Off-Track/At-Risk mit Kommentaren/Reaktionen) | Stub | mittel | nur auskommentierte Matrix-Zeile; v2-Projekt-Flag `is_project_updates_enabled` |
| 27 | EE-P05-001 | Teamspaces (Anlegen/Ändern/Löschen, Lead, Beschreibung, Logo, Mitglieder, Projekte) | Stub | hoch | PRO_PLAN_FEATURES „Teamspaces“; „Pro Basic / Business Advanced“ in keiner Quelle belegt |
| 28 | EE-P05-002 | Teamspace-Work-Items (Tabs „Team“/„Project“, Gruppierung „Team project“) | Stub | mittel | abgeleitet aus Teamspaces |
| 29 | EE-P05-003 | Teamspace-Projekt-Work-Items | Stub | mittel | abgeleitet aus Teamspaces |
| 30 | EE-P05-004 | Teamspace-Views und Teamspace-Pages | Stub | mittel | abgeleitet aus Teamspaces |
| 31 | EE-P05-007 | Workspace-Feature „Teamspaces“ (`teams` / `is_teams_enabled`) inkl. Settings-Seite | fehlt | hoch | folgt Teamspaces |
| 32 | EE-P05-008 | Teamspace-bezogene Member-Auswahl, Suche, Realtime-Kontext | Stub | mittel | abgeleitet aus Teamspaces |
| 33 | EE-P05-009 | Dashboards (eigene Dashboards) | Stub | hoch | PRO_PLAN_FEATURES „Dashboards + Reports“ |
| 34 | EE-P05-010 | Dashboard-Widgets (Typen, Chart-Modelle, Achsen/Metriken, Farbpaletten) | teilweise | mittel | wie Dashboards |
| 35 | EE-P05-014 | Insights (Hindsight, On-demand insights, Foresights) | fehlt | niedrig | Matrix „coming soon“, keine Auslieferung belegt |
| 36 | EE-P05-018 | Progress Charts (Cycle-Fortschritt v2, Scope-Linie, Burn-down/Burn-up) | teilweise | hoch | – |
| 37 | EE-P05-019 | Cycle Reports (On-demand, Permalinks) | teilweise | niedrig | – |
| 38 | EE-P05-021 | Auto-transfer Cycle Work items / Auto-Rollover | teilweise | mittel | Matrix Pro (nicht coming soon); University ordnet Rollover der Business-„Cycle Automation“ zu – spezifischere Matrix-Zeile gilt |
| 39 | EE-P05-022 | Workspace-weite Active Cycles | Stub | hoch | Matrix ab One (Legacy) |
| 40 | EE-P05-025 | Shared Views (View mit ausgewählten Mitgliedern teilen) | fehlt | mittel | – |
| 41 | EE-P05-026 | Publish Views (View öffentlich ins Internet stellen) | teilweise | hoch | Matrix Pro; ONE_PLAN_FEATURES „public views“ (One, Legacy) |
| 42 | EE-P05-028 | Operator-Kapseln und erweiterte Filteroperatoren (Negation, OR) im Filter-UI | Stub | niedrig | auskommentierte Matrix-Zeile „Search“; soweit aus PQL erzeugt, gilt PQL-Plan |
| 43 | EE-P05-029 | Advanced Search (OpenSearch-gestützt; Fallback Postgres) | fehlt | hoch | Docs-Badge „Pro“ (advanced-search.md Z. 7) |
| 44 | EE-P06-016 | Anzahl Automationen je Workspace (Limit) | fehlt | hoch | Matrix Z. 792–801; falls Automationen erst ab Business existieren (Doku 2026), ist der Pro-Wert veraltet; Limit entfällt (ADR-001) |
| 45 | EE-P06-021 | Work Item Templates (Projekt und Workspace, inkl. Sub-Work-Items; Templates-API) | Stub | hoch | planHighlights.pro „Work item templates“ |
| 46 | EE-P06-022 | Page Templates (Projekt-Pages und Wiki) | fehlt | hoch | Matrix-Zeile „Templates“ (Knowledge management) |
| 47 | EE-P06-023 | Pre-defined work item Templates | fehlt | mittel | Matrix „coming soon“ |
| 48 | EE-P07-001 | Wiki (Workspace-Seiten ohne Projekt) inkl. Wiki-Home, Sidebar, Feature-Toggle | Stub | hoch | Matrix ab One; Upsell „… with Plane Pro“, PRO_PLAN_FEATURES „Wikis“, Doku „Wiki Pro“ |
| 49 | EE-P07-002 | Wiki-Collections (öffentlich, Default „General“) inkl. Drag-and-drop-Reordering | fehlt | hoch | – |
| 50 | EE-P07-005 | Page-Versionen: Aufbewahrung | teilweise | hoch | zwei Stände (Matrix vs. Preisseite); Limits werden konfigurierbar (ADR-001) |
| 51 | EE-P07-007 | Real-time Collaboration: Presence-Avatare und Live-Cursor (CRDT-Sync selbst ist CE) | teilweise | hoch | Matrix ab One; Upsell „real-time collaboration … with Plane Pro“ |
| 52 | EE-P07-008 | Page-Publish (öffentlicher Link, Kommentare Externer, Report) | Stub | hoch | Matrix ab One; Doku „Publish erfordert Pro“ |
| 53 | EE-P07-009 | Page-Exports PDF/Word/Markdown, Hintergrund-Queue, ZIP inkl. Unterseiten | teilweise | hoch | – |
| 54 | EE-P07-010 | Work-Item-Embeds in Pages (Block) | Stub | hoch | Matrix ab One; Doku-Label „Work item Pro“ |
| 55 | EE-P07-012 | Link Pages ↔ Work Items (Pages-Sektion im Work Item; Work-Item-Pages-API) | fehlt | hoch | Matrix ab One; Changelog Pro |
| 56 | EE-P07-017 | Moving Pages (Projekt ↔ Projekt ↔ Teamspace ↔ Wiki/Collection) | Stub | mittel | „Moving is marked as a Pro feature“ nur Autoren-Suche, UNVERIFIZIERT |
| 57 | EE-P07-020 | Externe Embeds / Rich Cards (Iframely), Medien per URL | Stub | hoch | „Rich Page blocks … are available on Pro“ |
| 58 | EE-P07-021 | Attachments in Pages (inkl. Office-Bearbeitung) | Stub | hoch | „Rich Page blocks … Pro“ |
| 59 | EE-P07-022 | Video-Block | fehlt | mittel | „Rich Page blocks … Pro“ |
| 60 | EE-P07-024 | Plane AI im Editor: Selection-Aktionen (Paraphrase, Simplify, Elaborate, Summarize, Get title, Ton) und Seitenzusammenfassung | Stub | mittel | Guide „Page-level AI writing assistance and summaries start on Pro“ (UNVERIFIZIERT) |
| 61 | EE-P07-027 | Editor-Block Columns (2/3/4 Spalten) | fehlt | mittel | – |
| 62 | EE-P07-030 | Editor-Inline Status (farbiges Label) | fehlt | mittel | – |
| 63 | EE-P07-031 | Editor-Inline Date | fehlt | hoch | – |
| 64 | EE-P08-001 | SAML-SSO instanzweit (God Mode, inkl. God-Mode-Login per SSO) | Stub | hoch | Matrix ab One; Docs-Badges „Pro“ + „Business“ (saml-sso.md Z. 7) |
| 65 | EE-P08-002 | OIDC-SSO instanzweit (God Mode) | Stub | hoch | Matrix ab One, `selfHostedOnly: true`; Docs-Badges „Pro“ + „Business“ (oidc-sso.md Z. 7) |
| 66 | EE-P08-007 | Zwei-Faktor-Authentifizierung | fehlt | niedrig | nur Matrix-Zeile „Two-factor authentication and passkeys“ |
| 67 | EE-P08-008 | Passkeys | fehlt | niedrig | nur Matrix-Zeile |
| 68 | EE-P08-009 | Password Policy (eigene Passwort-Richtlinien) | teilweise | mittel | nur Matrix-Zeile |
| 69 | EE-P08-010 | Domain Security (erlaubte/gesperrte Anmelde-Domains) | fehlt | niedrig | nur Matrix-Zeile |
| 70 | EE-P08-014 | Guests-Kontingent (5 Gäste je bezahltem Mitglied) | CE (nur Cloud-Gating) | hoch | Matrix: Free –, ab One „5 per paid member“; Gast-Rolle selbst auf allen Plänen; Kontingent entfällt (ADR-001) |
| 71 | EE-P08-018 | Workspace-Lizenz und Seite „Billing and plans“ (Sync plan, Delink, Trial, Upgrade-Flow) | Stub | mittel | Lizenzmechanik, kein fachliches Feature; entfällt (ADR-001) |
| 72 | EE-P08-022 | Member-Limits und Seat-Berechnung (Aufhebung der Mitgliedergrenze) | CE (nur Cloud-Gating) | hoch | Cloud Free 12, Commercial Free 12 Seats/Workspace; Self-hosted-Richtwerte ~50/~50/~200/~200/Unlimited; entfällt (ADR-001) |
| 73 | EE-P08-024 | Support-Kanäle, SLA und „Chat with us“ | Stub | mittel | Free nur Forum; ENTERPRISE_PLAN_FEATURES nennt „Full-suite professional services“ nur für Enterprise; entfällt |
| 74 | EE-P09-001 | Integrations-Framework „Silo“, Integrations-Übersicht, Workspace-/persönliche Connections | Stub | mittel | Sektion „Integrations“ `comingSoon: true`; PRO_PLAN_FEATURES „Popular integrations“; Docs-Badges „Pro“ |
| 75 | EE-P09-002 | GitHub: Organisation verbinden, persönliches Konto, Repository-Mapping | Stub | hoch | – |
| 76 | EE-P09-003 | GitHub: Pull-Request-Automation (PR-State-Mapping) | Stub | mittel | wie GitHub-Integration |
| 77 | EE-P09-004 | GitHub: Project Issue Sync (bi-/unidirektional inkl. Kommentare, Sub-Issues) | Stub | mittel | – |
| 78 | EE-P09-005 | GitHub Enterprise (Server und Enterprise Cloud ghe.com) | Stub | hoch | Badge „Pro“ gilt für gesamte GitHub-Seite |
| 79 | EE-P09-006 | GitLab (gitlab.com): MR-State-Mapping, Issue Sync | Stub | hoch | Docs-Badge „Pro“ |
| 80 | EE-P09-007 | GitLab Self-managed („Gitlab Enterprise“) | Stub | hoch | – |
| 81 | EE-P09-008 | Bitbucket Cloud und Bitbucket Data Center | Stub | mittel | Docs-Badge „Pro“ |
| 82 | EE-P09-009 | Slack: Workspace verbinden, persönliches Konto, DM-Alerts | Stub | hoch | Matrix-Sektion „coming soon“; Docs-Badge „Pro“ |
| 83 | EE-P09-010 | Slack: Projekt-Benachrichtigungen (Projekt ↔ Channel) | Stub | hoch | – |
| 84 | EE-P09-011 | Slack: `/plane`-Slash-Command, Message-Shortcuts, Thread-Sync, Link-Unfurl | fehlt | mittel | – |
| 85 | EE-P09-012 | Sentry-Integration | Stub | hoch | Docs-Badge „Pro“ |
| 86 | EE-P09-015 | Zapier | fehlt | niedrig | Sektion „Integrations“ „coming soon“; keine Auslieferung belegt |
| 87 | EE-P09-016 | Zendesk (Work Items aus Tickets) | fehlt | niedrig | keine Auslieferung belegt |
| 88 | EE-P09-017 | Freshdesk (Work Items aus Tickets) | fehlt | niedrig | keine Auslieferung belegt |
| 89 | EE-P09-030 | Plane AI: Dienst „PI“, Workspace-Feature `pi`, Settings-Seite „Plane AI“ | Stub | hoch | Cloud: Credits je bezahltem Seat ab Pro; Self-hosted Badge „Commercial Edition“ ohne Plan; Free 500 Credits UNVERIFIZIERT |
| 90 | EE-P09-031 | Pi-Chat („Plane AI“-Chat) | Stub | mittel | wie Plane AI |
| 91 | EE-P09-032 | Plane AI: Connectors (MCP) | Stub | mittel | wie Plane AI |
| 92 | EE-P09-033 | Plane AI: Skills | Stub | mittel | wie Plane AI |
| 93 | EE-P09-034 | Plane AI: Memory | Stub | niedrig | wie Plane AI |
| 94 | EE-P09-035 | Plane AI: eingebaute Agents | Stub | mittel | wie Plane AI; Beta |
| 95 | EE-P09-036 | Plane AI: Autopilot-Modus (Ausführung ohne Einzelbestätigung) | fehlt | niedrig | wie Plane AI; belegt für Mobile |
| 96 | EE-P09-043 | AI-Usage, Credits, Token-Budget | fehlt | mittel | Cloud-Credits je bezahltem Seat; Credits entfallen (ADR-001), Token-Budget als Instanz-Einstellung |

### 5.4 In jeder Commercial-Installation (Commercial-Free), nicht in der CE – 16 Features

Diese Features sind kein Plan-Merkmal, sondern Bestandteil der Commercial Edition selbst (Regel L4). Sie fehlen in der CE, obwohl die CE „at par with the Free tier“ ist (`editions-and-versions.md` Z. 25) – siehe Kap. 6.4.

| # | ID | Feature | CE-Status | Konfidenz | Hinweis |
|---|---|---|---|---|---|
| 1 | EE-P03-001 | Health-Probes und God-Mode-„System checks“ (`/api/live/`, `/api/ready/`, `/api/health/` je Dienst) | teilweise | hoch | Commercial Edition (alle Pläne); CE nur `GET /` |
| 2 | EE-P03-004 | Betriebsfeatures des Commercial-Charts (HA, Read-Replica, External Secrets, Custom CA, Storage-Proxy, GCS, OpenTelemetry, PSA/OpenShift) | teilweise | hoch | Commercial-Kubernetes-Chart; teils auch im CE-Chart |
| 3 | EE-P03-005 | Dedizierte External-API-Instanz (zweiter Backend-Pool für öffentlichen API-Verkehr) | fehlt | mittel | Commercial-Chart, optional |
| 4 | EE-P03-006 | GraphQL- und Marketplace-Endpunkte (`/graphql/`, `/marketplace/`) | fehlt | niedrig | Commercial-Chart-Pflichtrouten; Inhalt nicht dokumentiert |
| 5 | EE-P03-008 | Prime CLI und Commercial-Installationsmethoden (Installer, Backup/Restore, Docker AIO, Swarm, Podman, Coolify, Portainer) | teilweise | hoch | in jeder Commercial-Installation inkl. Commercial-Free; wird durch Aspire-Deployment-Artefakte ersetzt |
| 6 | EE-P06-018 | Automation-Consumer / Outbox-Architektur (Outbox-Poller → RabbitMQ → Consumer) | fehlt | mittel | Commercial-Infrastruktur, kein Plan-Feature; Dok. 22 P03-F29 nennt Pro (Trigger & Action) |
| 7 | EE-P08-021 | Prime-Portal und Monitor-Dienst (Lizenzvalidierung, Feature-Flags, Plan-Synchronisation) | Stub | hoch | Mechanik aller Commercial-Pläne inkl. Commercial-Free; entfällt (ADR-001) |
| 8 | EE-P08-025 | God Mode: User Management (Instanz-Benutzer, Instanz-Admins einladen, Suspend) | teilweise | hoch | Commercial Edition ohne Plan-Badge |
| 9 | EE-P08-026 | God Mode: Session-Einstellungen (Session expiry, Admin session expiry) | teilweise | hoch | Commercial Edition ohne Plan-Badge |
| 10 | EE-P09-019 | Importer-Framework (Imports-Seite, Job-Status, Historie, Importer-Worker) | Stub | mittel | Basis-Import ab Commercial-/Cloud-Free (nicht CE); JSON-Tier „Pro“ war Konvention für den Import mit Custom Props |
| 11 | EE-P09-020 | Jira-Cloud-Importer (inkl. Custom Properties) | Stub | mittel | Free/One „Without custom props“ (Cloud/Commercial, nicht CE) |
| 12 | EE-P09-022 | Linear-Importer | fehlt | mittel | „all plans of the Commercial Edition“ |
| 13 | EE-P09-023 | Asana-Importer | fehlt | mittel | „all plans of the Commercial Edition“ |
| 14 | EE-P09-027 | CSV-Importer für Work Items | fehlt | mittel | „all plans of the Commercial Edition“ |
| 15 | EE-P09-028 | GitHub-Importer | Stub | mittel | Free/One „Without custom props“ |
| 16 | EE-P09-054 | Mobile-Apps (iOS/Android) | Stub | mittel | „all plans of the Commercial Edition“; Push nur Plane Cloud |

### 5.5 Cloud-only – 2 Features

| # | ID | Feature | CE-Status | Konfidenz | Hinweis |
|---|---|---|---|---|---|
| 1 | EE-P08-023 | Storage-Limits (Workspace-Speicher, Max file size) | teilweise | hoch | Sektion `storage` `cloudOnly: true`; Free 5 GB / 5 MB; entfällt (ADR-004) |
| 2 | EE-P09-055 | Flatfile-Importer (CSV über Flatfile, Beta) | fehlt | mittel | „only available on Plane Cloud“; Self-hosted nutzt CSV-Importer |

### 5.6 Plan nicht belegt (in Commercial/Cloud vorhanden) – 54 Features

Für diese Features nennt keine Quelle einen Plan. Spalte „Enterprise“ in Kap. 4 = „✓ (abgeleitet)“ (Regel L5).

| # | ID | Feature | CE-Status | Konfidenz | Hinweis |
|---|---|---|---|---|---|
| 1 | EE-P01-002 | Product Tour / „Get started“ (geführte Touren, Demo-Projekt, Get-started-Checkliste; i18n-Namespace `tour`) | fehlt | mittel | Cloud-/Commercial-Onboarding; kein Plan belegt |
| 2 | EE-P02-002 | Projekt-Feature-API (`/features/` bündelt Projekt-Schalter `epics`, `work_item_types`, `parallel_cycles`, `project_updates`, `workflows`) | teilweise | hoch | kein eigenes Plan-Feature; steuert Bezahl-Features; Toggles bleiben nach ADR-001 fachliche Einstellungen |
| 3 | EE-P02-003 | Workspace-Feature-API (`project_grouping`, `initiatives`, `teams`, `customers`, `wiki`, `pi`) | fehlt | hoch | kein eigenes Plan-Feature |
| 4 | EE-P02-004 | Workspace-Mitglied per Public-API entfernen (inkl. Deaktivierung in allen Projekten und Seat-Reduktion) | teilweise | hoch | Commercial-API v1/v2; Seat-Logik entfällt (ADR-001); vorher als „Cloud-only“ geführt (korrigiert in Dok. 21) |
| 5 | EE-P02-005 | Public API v2 (`/api/v2/`: PATCH-only, problem+json, Offset-/Cursor-Pagination, `?fields=`/`?expand=`, Upsert, Bulk) | fehlt | hoch | Commercial Edition/Cloud; Plan-Gating je Ressource über `402 payment_required`; öffentliche Verfügbarkeit UNVERIFIZIERT |
| 6 | EE-P02-006 | Views-API (Projekt- und Workspace-Views in der Public-API) | teilweise | mittel | Views selbst Free; Public-API dafür nur in v2 |
| 7 | EE-P03-007 | Flux – Realtime-Event-Server (`/flux`, WebSocket mit Redis) | fehlt | niedrig | nur in Docs (Health, FIPS-Images), nicht im Chart |
| 8 | EE-P04-021 | Conversions (Work Item ↔ Epic; Bulk-Conversions) | Stub | niedrig | Einzelkonvertierung = Typwechsel (Epics Pro), Plan nicht belegt; Bulk-Conversions Business coming soon |
| 9 | EE-P04-025 | Eingebauter Relationstyp „Implements“ / „Implemented by“ | teilweise | mittel | Changelog v1.22.0 ohne Planangabe |
| 10 | EE-P04-034 | Project Labels | fehlt | mittel | Changelog v2.5.0 ohne Plan; Dok. 20 PF-21 subsumiert unter Pro, Dok. 21 „nicht belegt“ |
| 11 | EE-P04-042 | Work-Item-Votes in der App (Up-/Downvotes an Work Items, Epics, Intake) | teilweise | hoch | Changelog 31.03.2026 ohne Planangabe |
| 12 | EE-P04-043 | Kommentar-Antworten (Reply-Threads unter Work-Item-Kommentaren) | teilweise | mittel | Changelog v1.22.0 ohne Planangabe |
| 13 | EE-P04-044 | Projektübergreifende Sub-Work-Items | fehlt | mittel | Changelog 31.03.2026 ohne Planangabe |
| 14 | EE-P05-006 | Teamspace-Kommentare/-Updates | Stub | mittel | keine Plan-Quelle |
| 15 | EE-P05-011 | Dashboard-Filter inkl. PQL (Ebenen source, quick, widget) | fehlt | niedrig | Standard-Filter vermutlich wie Dashboards (Pro), PQL-Anteil wie PQL (Enterprise Grid) |
| 16 | EE-P05-012 | Dashboard-Widgets für Intake und Custom Properties | fehlt | niedrig | nur Changelog-Titel |
| 17 | EE-P05-015 | Erweiterte Analytics-Tabs (Cycles, Modules, Intake, Projects/Users) mit Tab-Gating | teilweise | mittel | Text „Upgrade to {plan} to unlock {tab}“; Plan je Tab unbekannt |
| 18 | EE-P05-023 | Parallel Cycles (mehrere aktive Cycles je Projekt) | fehlt | mittel | keine Plan-Quelle |
| 19 | EE-P05-024 | Cycle-Aktionen „Complete“, manuelles Starten/Beenden und Archivieren laufender Cycles | fehlt | mittel | keine Plan-Quelle |
| 20 | EE-P05-031 | Home-, Your-Work- und Navigations-Erweiterungen (Widgets „New at Plane“, „Quick tutorial“, Commercial-Sidebar-Menüs) | Stub | mittel | teils Cloud-Inhalte; Business-Trial-Banner entfällt |
| 21 | EE-P06-024 | Template-Marketplace (Publish, Kategorien, Verifizierung, Kopie) | fehlt | mittel | Marketplace-Publish ohne Plan-Angabe |
| 22 | EE-P07-006 | Page-Versionen: „Highlight changes“, Vergleich zweier Versionen, Server-Restore | Stub | mittel | vermutlich wie Versionen |
| 23 | EE-P07-014 | Page-Level-Kommentare, Kommentar-Filter, Moderation (hide/unhide) | fehlt | mittel | keine Plan-Angabe |
| 24 | EE-P07-033 | Mermaid-Diagramm-Block | fehlt | mittel | weder Doku noch Changelog nennen einen Plan |
| 25 | EE-P07-038 | Widget-Block (Chart aus Work-Item-Daten) | fehlt | niedrig | keine Plan-Angabe |
| 26 | EE-P07-039 | Block-Links (Link auf einen Block kopieren) | fehlt | niedrig | keine Plan-Angabe |
| 27 | EE-P07-040 | Page-Benachrichtigungen (Freigabe-Mail, Page-Subscriber) | fehlt | niedrig | keine Plan-Angabe |
| 28 | EE-P07-041 | Pages-Public-API (v1/v2: Pages, Collections, Templates, Published Pages, Attachments, Work-Item-Pages, MCP) | fehlt | mittel | je Ressource wie zugehöriges Feature; 402-Zeile der v2-Doku ist kein Tier-Beleg |
| 29 | EE-P07-042 | Erweiterte Mentions im Document-Editor (Seiten/Projekte/Zyklen/Module) und Backlinks | Stub | niedrig | keine Plan-Angabe |
| 30 | EE-P08-027 | Argus – Sensitive-Data-/PII-Scanner | fehlt | mittel | Produkt-Flag `PII_SCANNER`; Commercial v3.2.0; Plan nicht belegt |
| 31 | EE-P09-013 | HubSpot-Connector | fehlt | niedrig | nur Helm-Connector belegt |
| 32 | EE-P09-014 | Cursor-Agent-Integration | fehlt | niedrig | nur Silo-Secret belegt |
| 33 | EE-P09-018 | OAuth Bridge (externe IdP-JWTs als API-Credentials) | Stub | hoch | keine Plan-Angabe |
| 34 | EE-P09-021 | Jira-Server/Data-Center-Importer | fehlt | mittel | Cloud und Commercial Edition, Plan nicht genannt |
| 35 | EE-P09-024 | ClickUp-Importer | fehlt | mittel | Plan nicht genannt |
| 36 | EE-P09-025 | Notion-Importer | fehlt | niedrig | Plan nicht genannt |
| 37 | EE-P09-026 | Confluence-Importer | fehlt | mittel | Plan nicht genannt |
| 38 | EE-P09-029 | Mitglieder-Import per CSV (Workspace und Projekt) | Stub | hoch | keine Plan-Angabe; Seat-Limit-Hinweis entfällt (ADR-001) |
| 39 | EE-P09-037 | AI-Work-Creation (Text → Work Items) und Beschreibungs-Generierung | teilweise | niedrig | nur Changelog-Titel |
| 40 | EE-P09-038 | AI-Suche / Semantic Search (Embeddings, Vektorsuche) | fehlt | mittel | Commercial Edition, optional; ohne Embedding-Modell BM25 |
| 41 | EE-P09-039 | Duplicate Detection (Duplikat-Vorschläge beim Anlegen von Work Items und Intake-Requests) | Stub | mittel | Teil von Plane AI, benötigt Embedding-Modell |
| 42 | EE-P09-040 | AI-Aktionen Summary, Catch-up, Copy-as-prompt, AI-Filter | fehlt | niedrig | keine Plan-Angabe |
| 43 | EE-P09-041 | Applets / Artifacts (AI-generierte, versionierte HTML-Dashboards) | fehlt | hoch | Plan-Feature „Applets“ (sonst 402) |
| 44 | EE-P09-042 | LLM-Provider- und Embedding-Konfiguration | teilweise | hoch | Commercial Edition (Env/Helm) |
| 45 | EE-P09-044 | OAuth-App-Plattform („Build your own app“, Consent, Bot-/User-Token, Scopes, Installationen) | Stub | hoch | „Plane Cloud and Plane Commercial Edition; Community Edition does not include it“; Beta |
| 46 | EE-P09-045 | App-Marketplace | Stub | mittel | Supported-Plans-Filter entfällt |
| 47 | EE-P09-046 | App-Mentions / Bot-User | teilweise | hoch | Agents zählen nicht als abrechenbare Nutzer |
| 48 | EE-P09-047 | Agents-Plattform (Agent Runs, Activities, Signals) | Stub | hoch | Beta; Commercial/Cloud |
| 49 | EE-P09-048 | Webhooks v2 (Webhook-CRUD, Delivery-Logs, v2-Events) | teilweise | hoch | Screenshot aus Business-Workspace, kein Plan |
| 50 | EE-P09-049 | Workspace-Access-Tokens | teilweise | mittel | keine Plan-Angabe |
| 51 | EE-P09-050 | MCP-Server (OAuth-Transport, Tool-Gates) | teilweise | hoch | OAuth-Transport nur Cloud/Commercial; CE nur stdio + PAT |
| 52 | EE-P09-051 | Plane Compose (project-as-code CLI) | fehlt | hoch | Client-Werkzeug; Workspace-WIT „(Enterprise)“ |
| 53 | EE-P09-052 | Offizielle SDKs (Node, Python) | fehlt | hoch | kein Plan |
| 54 | EE-P09-053 | Desktop-App (macOS, Linux) | Stub | mittel | Self-managed ab Commercial v3.0.0; Plan nicht genannt |

### 5.7 Abstufungen innerhalb eines Features

#### 5.7.1 Enterprise (Grid) enthält mehr als Business

| # | EE-ID | Feature | Business | Enterprise (Grid) | Quelle |
|---|---|---|---|---|---|
| 1 | EE-P07-005 | Page-Versionen: Aufbewahrung | 3 Monate (Preisseite: 60 Versionen / 90 Tage) | unbegrenzt | `plans.tsx` Z. 897–907; Dok. 26 P07-05 |
| 2 | EE-P06-016 | Anzahl Automationen je Workspace | 10.000 | unbegrenzt („Unlimited and full Automation Flows“) | `plans.tsx` Z. 791–801; `subscription.ts` Z. 12 |
| 3 | EE-P06-010 | Automation-Trigger | Event-Trigger (Work item created/updated, State changed, Assignee changed, Comment added) | zusätzlich Scheduled | Dok. 25 F10 |
| 4 | EE-P06-012 | Automation-Aktionen | Change property, Add comment | zusätzlich Send webhook, Run script | Dok. 25 F12 |
| 5 | EE-P06-001 / EE-P06-002 | Workflows | ein Default-Workflow je Projekt | beliebig viele, typ-spezifische Workflows | Dok. 25 F01/F02 |
| 6 | EE-P08-011 / EE-P08-012 / EE-P08-013 | Rollen | RBAC (System-Rollen inkl. Workspace Admin, Contributor, Commenter) | zusätzlich Custom Roles und GAC (Permission Schemes, bedingte Rechte) | `plans.tsx` Z. 694–703; Dok. 27 P08-11/12/13 |
| 7 | EE-P08-022 | Member-Limit (Self-hosted-Richtwert) | ~200 | Unlimited | `plans.tsx` Z. 686–692 |
| 8 | EE-P08-023 | Storage (nur Cloud) | 5 TB / 200 MB je Datei | Custom | `plans.tsx` Z. 1026–1054 |
| 9 | EE-P04-007 | Work Item Types/Properties | Projekt-Ebene („On Pro and Business plans, work item types are managed at the project level“) | Workspace-Ebene (Workspace-Modus) | Dok. 23 WM-07 |
| 10 | EE-P08-024 | Support | Matrix: „Full-suite professional services“ | Matrix: identisch; `ENTERPRISE_PLAN_FEATURES` führt „Full-suite professional services“ als Enterprise-Merkmal | `plans.tsx` Z. 1230–1231; `subscription.ts` Z. 13 |
| 11 | EE-P03-002 / EE-P03-003 / EE-P03-010 | Betriebsformen | – | Airgapped (≥ 100 Seats), FIPS-140-3, Private + managed deployments | Dok. 22 P03-F36/F37/F46 |

#### 5.7.2 Business enthält mehr als Pro

| # | EE-ID | Feature | Pro | Business | Quelle |
|---|---|---|---|---|---|
| 1 | EE-P04-028 / EE-P04-030 | Time Tracking | „Historical timesheets“ | zusätzlich „approvals“ (Timesheet-Approvals) | `plans.tsx` Z. 183–192 |
| 2 | EE-P04-027 | Auto-assignment in Modules | „Linear“ | „Round-robin and Capacity“ | `plans.tsx` Z. 308–317 |
| 3 | EE-P07-009 | Page-Exports | „One download at a time“ | „Queued downloads“ | `plans.tsx` Z. 875–885 |
| 4 | EE-P07-005 | Page-Versionen | 2 Tage (Preisseite: 20 Versionen / 30 Tage) | 3 Monate (60 Versionen / 90 Tage) | `plans.tsx` Z. 897–907; Dok. 26 P07-05 |
| 5 | EE-P06-016 | Anzahl Automationen | 5.000 | 10.000 | `plans.tsx` Z. 791–801 |
| 6 | EE-P04-019 | Bulk Ops | „All props“ | zusätzlich „Work item transfers and conversions“ (COMING SOON) | `plans.tsx` Z. 162–181 |
| 7 | EE-P04-003 / EE-P04-007 / EE-P04-008 | Custom Properties | „Project-level custom properties“ | Matrix: „Workspace-level properties and roll-ups“ (Workspace-Properties laut Doku 2026 erst Enterprise Grid) | `plans.tsx` Z. 216–225; Dok. 23 WM-07/08 |
| 8 | EE-P07-002 / EE-P07-003 | Wiki-Collections | öffentliche Collections | zusätzlich Private Collections | Dok. 26 P07-02/03 |
| 9 | EE-P08-023 | Storage (nur Cloud) | 1 TB / 100 MB je Datei | 5 TB / 200 MB je Datei | `plans.tsx` Z. 1026–1054 |
| 10 | EE-P08-024 | Support | Mail, Forum, Chat; SLA | „Full-suite professional services“ | `plans.tsx` Z. 1208–1252 |
| 11 | EE-P09-030 | Plane AI (Cloud-Credits) | 1,000 Credits je Seat und Monat | höher (Drittquelle 2,000; UNVERIFIZIERT) | Dok. 20 PF-82; Dok. 22 P03-F12 |

#### 5.7.3 Pro enthält mehr als Free (Cloud) / CE-Umfang

| # | EE-ID | Feature | Free / CE | Pro | Quelle |
|---|---|---|---|---|---|
| 1 | EE-P04-031 | Estimates | „Basic“ (points, categories) | „Advanced“ (time, Bearbeiten, Umsortieren, Systemwechsel) | `plans.tsx` Z. 145–154; `apps/api/plane/db/models/estimate.py` Z. 13–15 |
| 2 | EE-P09-020 / EE-P09-028 | Jira-/GitHub-Importer | Cloud-/Commercial-Free „Without custom props“ (CE: kein Importer) | „With custom props“ | `plans.tsx` Z. 939–960 |
| 3 | EE-P08-022 | Member-Limit | Cloud Free 12, Self-hosted ~50 (CE: kein Limit) | Cloud Unlimited, Self-hosted ~200 | `plans.tsx` Z. 675–693 |
| 4 | EE-P08-014 | Guests | Free „–“ (CE: Rolle Guest ohne Kontingent) | „5 per paid member“ | `plans.tsx` Z. 705–715 |
| 5 | EE-P08-023 | Storage (nur Cloud) | 5GB / 5 MB | 1 TB / 100 MB | `plans.tsx` Z. 1026–1054 |
| 6 | EE-P08-024 | Support-Kanäle | Forum | Mail, Forum, Chat; SLA | `plans.tsx` Z. 1208–1252 |
| 7 | EE-P08-011 | Rollen | „Basic“ (CE: Admin 20, Member 15, Guest 5) | Matrix: „Pre-defined roles“ (Doku 2026: Workspace Admin/Contributor/Commenter erst Business) | `plans.tsx` Z. 694–703; `apps/api/plane/db/models/workspace.py` Z. 19 |

---

## 6. Im CE-Code vorhanden, aber in Cloud-Free eingeschränkt (gegen den Code geprüft)

Prüfgegenstand: alle Zeilen der Repo-Matrix, bei denen `free` `false` oder eine schwächere Abstufung ist (Kap. 1.3), gegen den tatsächlichen CE-Code v1.4.2. „Nutzbar im CE“ = für Endnutzer ohne Codeänderung erreichbar. Pfade relativ zu `/home/user/plane`.

### 6.1 Im CE vorhanden – nur Plane Cloud (Free) sperrt bzw. begrenzt

| # | Matrix-Zeile (Cloud-Free) | CE-Code-Befund | Nutzbar im CE | EE-ID / Bewertung |
|---|---|---|---|---|
| 1 | „Member limit“: Free **12** (Cloud), ~50 (Self-hosted-Richtwert) – `plans.tsx` Z. 675–693 | Keine Seat-/Mitgliederlimit-Logik im Backend: `grep -rli seat apps/api/plane` trifft nur den Demo-Text „driver’s seat“ in `apps/api/plane/seeds/data/projects.json` Z. 6 (vgl. Dok. 20 K19); Einladungen unbegrenzt | ja | EE-P08-022 – „im CE vorhanden (nur Cloud-Gating)“; Kontingent entfällt (ADR-001) |
| 2 | „Guests“: Free **–**, ab One „5 per paid member“ – `plans.tsx` Z. 705–715 | Rolle Guest vorhanden: `ROLE_CHOICES = ((20, "Admin"), (15, "Member"), (5, "Guest"))` in `apps/api/plane/db/models/workspace.py` Z. 19; kein Gast-Kontingent | ja | EE-P08-014 – „im CE vorhanden (nur Cloud-Gating)“; Kontingent entfällt |
| 3 | „Versions“: Free **–**, Pro „2 days“ – `plans.tsx` Z. 897–907 | Versionierung je Seite: `PageVersion` (`apps/api/plane/db/models/page.py` Z. 158–173), Celery `track_page_version` behält max. 20 Versionen („If page versions are greater than 20 delete the oldest one“, `apps/api/plane/bgtasks/page_version_task.py` Z. 71–72), Cleanup `get_page_versions_queryset` „beyond the maximum allowed (20 per page)“ (`apps/api/plane/bgtasks/cleanup_task.py` Z. 107–124); UI `apps/web/components/pages/version/*` | ja (20 Versionen, ohne zeitliche Aufbewahrung, ohne Vergleich/Highlight) | EE-P07-005 „teilweise“: die CE bietet mehr als Cloud-Free; Plan-Bezahlteil = zeitbasierte Aufbewahrung; EE-P07-006 (Vergleich/Highlight/Restore) bleibt Stub |
| 4 | „Exports“: Free **–**, Pro „One download at a time“ – `plans.tsx` Z. 875–885 | Export-Modal mit Formaten `"pdf" \| "markdown"` (`apps/web/components/pages/modals/export-page-modal.tsx` Z. 40, 55, 112); Live-Server-Endpunkt `@Controller("/pdf-export")` (`apps/live/src/controllers/pdf-export.controller.ts` Z. 16, 134–140) | ja (PDF, Markdown, einzeln, synchron) | EE-P07-009 „teilweise“: Bezahlteil = Word/DOCX, Hintergrund-Queue, ZIP inkl. Unterseiten |
| 5 | „Real-time Collab“: Free **–**, ab One – `plans.tsx` Z. 819–829 | CRDT-Mehrbenutzer-Editing ist aktiv: `@tiptap/extension-collaboration` mit `HocuspocusProvider` (`packages/editor/src/hooks/use-collaborative-editor.ts` Z. 7, 9, 80, 167), Hocuspocus-Server `apps/live/src/hocuspocus.ts`, Controller `apps/live/src/controllers/collaboration.controller.ts`; **deaktiviert** ist nur `"collaboration-cursor"` in allen Editoren (`apps/web/hooks/use-editor-flagging.ts` Z. 35–48; Typ `packages/editor/src/types/extensions.ts` Z. 7) | ja (gleichzeitiges Bearbeiten von Projektseiten; ohne Presence-Avatare/Live-Cursor, ohne Wiki-/Teamspace-Seiten) | EE-P07-007 „teilweise“: die Matrix-Beschreibung „Edit a page together with members …“ ist für Projektseiten im CE erfüllt; Bezahlteil = Presence/Cursor + Realtime für Wiki/Teamspace |
| 6 | „Publish Views“: Free **–**, Pro – `plans.tsx` Z. 509–519; `FREE_PLAN_UPGRADE_FEATURES` „Public Views and Pages“ (`subscription.ts` Z. 47) | Projekt-Publish (öffentliches Board) vorhanden: Endpunkte `…/projects/<project_id>/project-deploy-boards/` (`apps/api/plane/app/urls/project.py` Z. 113–120), Modal mit Layout-Auswahl `view_props` (`apps/web/components/project/publish-project/modal.tsx` Z. 50, 144–166), Space-App-Routen `:workspaceSlug/:projectId` und `issues/:anchor` (`apps/space/app/routes.ts` Z. 12–13) | ja (Projekt als Ganzes öffentlich, wählbare Layouts, Kommentare/Reaktionen/Votes) | EE-P05-026 „teilweise“: Bezahlteil = Publish einzelner gespeicherter Views (`DeployBoard.TYPE_CHOICES` kennt `view`, `apps/api/plane/db/models/deploy_board.py` Z. 26, ohne UI/Route) |
| 7 | „One-click Deployment“: Free **–**, ab One – `plans.tsx` Z. 1146–1156; `ONE_PLAN_FEATURES` „Docker, Kubernetes and more“ (`subscription.ts` Z. 40) | Installationsskripte und Varianten im CE: `deployments/cli/community/install.sh`, `…/README.md`, `…/restore-airgapped.sh`, `deployments/{aio,kubernetes,swarm}/community` | ja | EE-P03-009 „teilweise“: Bezahlteil = Marktplatz-Apps (DigitalOcean, Heroku, AWS AMI); entfällt (ADR-004) |
| 8 | „Storage“: Free 5GB / 5 MB (Sektion `cloudOnly`) – `plans.tsx` Z. 1026–1054 | Kein Workspace-Speicherkontingent; instanzweites `FILE_SIZE_LIMIT = int(os.environ.get("FILE_SIZE_LIMIT", 5242880))` (`apps/api/plane/settings/common.py` Z. 389, 403) – Default entspricht den 5 MB von Cloud-Free, ist aber frei konfigurierbar | ja | EE-P08-023 „teilweise“; Kontingente entfallen (ADR-004) |

### 6.2 Teilfunktion im CE – der in der Matrix beschriebene Umfang ist bezahlpflichtig

| # | Matrix-Zeile / Feature | CE-Code-Befund | Nutzbar im CE | EE-ID |
|---|---|---|---|---|
| 1 | „Work item Transfers“ (Pro) | Nur Bulk-Transfer offener Work Items eines Cycles in einen anderen Cycle: `POST …/cycles/<cycle_id>/transfer-issues/` (`apps/api/plane/app/urls/cycle.py` Z. 72–74), UI `apps/web/components/cycles/transfer-issues-modal.tsx`, `transfer-issues.tsx`; Verschieben in ein anderes **Projekt** fehlt | teilweise | EE-P04-020 |
| 2 | „Auto-transfer Cycle Work items“ (Pro) | dieselbe Transferlogik nur manuell; Automatik (`auto_rollover`) nur als Text | nein (nur manuell) | EE-P05-021 |
| 3 | „Progress Charts“ (Pro) | Cycle- und Modul-Burndown: `ProgressChart` (`apps/web/components/core/sidebar/progress-chart.tsx`) in `apps/web/components/cycles/analytics-sidebar/sidebar-chart.tsx` Z. 15, 26 und `apps/web/components/modules/analytics-sidebar/issue-progress.tsx` Z. 22, 133–139 | teilweise (v1-Charts; v2 mit Scope-Linie/Burn-up fehlt) | EE-P05-018 |
| 4 | „Cycle Reports“ (Pro) | Fortschrittsstatistik je Assignee/Label im Cycle-Peek (`apps/web/components/cycles/analytics-sidebar/progress-stats.tsx`); On-demand-Report mit Permalink fehlt | teilweise | EE-P05-019 |
| 5 | „Module Overview“ (Pro) | Modul-Peek mit Burndown/Progress (`apps/web/components/modules/analytics-sidebar/*`); eigene Overview-Seite fehlt | teilweise | EE-P04-026 |
| 6 | „Dependencies in Gantt“ (Pro) | Relationstypen `blocked_by`, `start_before`, `finish_before` (+ Reverse) im Backend (`apps/api/plane/db/models/issue.py` Z. 272–293); Gantt reicht `enableDependency` durch (`apps/web/components/issues/issue-layouts/gantt/base-gantt-root.tsx` Z. 149), `apps/web/components/gantt-chart/helpers/draggable.tsx` deklariert das Prop (Z. 26), wertet es aber nicht aus – keine Verbindungslinien, kein Ziehen | teilweise (Relationen ja, Gantt-Abhängigkeiten nein) | EE-P04-023 |
| 7 | „Public, Private, and Secret projects“ (Pro) | `NETWORK_CHOICES = ((0, "Secret"), (2, "Public"))` (`apps/api/plane/db/models/project.py` Z. 71, 76) – zwei von drei Stufen; „Private mit Beitrittsgenehmigung“ fehlt | teilweise | EE-P04-032 |
| 8 | „Workspace Activity Logs“ (Business) | Aktivität je Benutzer: `workspaces/<slug>/user-activity/<user_id>/` (`apps/api/plane/app/urls/workspace.py` Z. 138–140); workspace-weites filterbares Log fehlt | teilweise | EE-P08-016 |
| 9 | „Password Policy“ (Pro) | feste Regel `is_password_strong` (zxcvbn-Score ≥ 3, `apps/api/plane/authentication/utils/password.py` Z. 13–15); keine konfigurierbare Richtlinie | teilweise (fest) | EE-P08-009 |
| 10 | „Intake Assignees“ (Business) | `Project.default_assignee` (`apps/api/plane/db/models/project.py` Z. 79) wird beim Anlegen von Intake-Work-Items übergeben (`apps/api/plane/app/views/intake/base.py` Z. 266) | teilweise | EE-P04-040 |
| 11 | „Estimates“ (Free „Basic“) | `EstimateType` nur `categories`, `points` (`apps/api/plane/db/models/estimate.py` Z. 13–15) = Basic | ja (Basic) | EE-P04-031 (Advanced) |
| 12 | „Bulk Ops“ (Free –) | Mehrfachauswahl zeigt nur ein Upgrade-Banner (`apps/web/components/issues/bulk-operations/root.tsx` Z. 23–59, Link `MARKETING_PLANE_ONE_PAGE_LINK`); vorhanden sind das Modal „Bulk delete“ (`apps/web/components/core/modals/bulk-delete-issues-modal.tsx`) und die Endpunkte `bulk-delete-issues`, `bulk-archive-issues` (`apps/api/plane/app/urls/issue.py` Z. 94–101) | nur Bulk-Delete | EE-P04-019 (Stub) |
| 13 | „Nested Pages“ (Business) | `Page.parent` (`apps/api/plane/db/models/page.py` Z. 40), rekursives Archivieren und Lösen der Eltern-Beziehung beim Wiederherstellen (Dok. 26 P07-04); keine UI zum Anlegen von Unterseiten | nein (nur Backend) | EE-P07-004 |
| 14 | God Mode: Session-Einstellungen (Commercial) | nur ENV `SESSION_COOKIE_AGE` (604800) und `ADMIN_SESSION_COOKIE_AGE` (3600) (`apps/api/plane/settings/common.py` Z. 425, 432) | nur per ENV | EE-P08-026 |
| 15 | God Mode: User Management (Commercial) | `InstanceAdminEndpoint` `admins/` (`apps/api/plane/license/urls.py` Z. 25–35); keine UI | nein (nur API) | EE-P08-025 |
| 16 | Webhooks v2 (Commercial) | Webhooks v1 vollständig (`apps/api/plane/app/urls/webhook.py`, `apps/api/plane/bgtasks/webhook_task.py`) | ja (v1) | EE-P09-048 |
| 17 | Work-Item-Votes (Commercial) | Modell `IssueVote`, Votes nur im öffentlichen Board der Space-App (`apps/api/plane/space/urls/issue.py` Z. 52–55) | nur Space | EE-P04-042 |
| 18 | Page Labels (Business) | Modell `PageLabel` (`apps/api/plane/db/models/page.py` Z. 120) auf Work-Item-Labels, keine UI | nein (nur Backend) | EE-P07-016 |

### 6.3 Gegenprobe: in der Matrix für Free gesperrt **und** im CE-Code nicht nutzbar

| # | Matrix-Zeile | CE-Code-Befund | EE-ID |
|---|---|---|---|
| 1 | „Publish“ (Pages, ab One) | `DeployBoard.TYPE_CHOICES` enthält `("page", "Page")` (`apps/api/plane/db/models/deploy_board.py` Z. 25), aber kein Publish-Code in `apps/web/components/pages` (grep `publish` ohne Treffer) und keine Space-Route für Seiten (`apps/space/app/routes.ts` Z. 12–15) → **nicht im CE** | EE-P07-008 (Stub) |
| 2 | „Wiki“ (ab One) | Feld `Page.is_global` (`apps/api/plane/db/models/page.py` Z. 51) und Upsell-Text „Upgrade to unlock Wiki … with Plane Pro.“ (`packages/i18n/src/locales/en/wiki.json` Z. 89–91); keine Wiki-Routen | EE-P07-001 (Stub) |
| 3 | „Work item Embeds“ (ab One) | Node `issue-embed-component` nur zum Parsen registriert (`packages/editor/src/extensions/core-without-props.ts` Z. 28, 66); NodeView nicht registriert; Export entfernt Embeds (`apps/web/hooks/use-parse-editor-content.ts` Z. 154–156, 212–214) | EE-P07-010 (Stub) |
| 4 | „Active Cycles“ (workspaceweit, ab One) | Route `:workspaceSlug/active-cycles` existiert (`apps/web/app/routes/core.ts` Z. 66–67), die Seite rendert nur `WorkspaceActiveCyclesUpgrade` (`apps/web/app/(all)/[workspaceSlug]/(projects)/active-cycles/page.tsx` Z. 13, 23) | EE-P05-022 (Stub) |
| 5 | „Time Tracking + Worklogs“ (ab One) | nur Flag `Project.is_time_tracking_enabled` (`apps/api/plane/db/models/project.py` Z. 100), kein Worklog-Modell/-UI | EE-P04-028 („teilweise“ laut Dok. 23, funktional nicht nutzbar) |
| 6 | „Work item Types“ (Pro) | Modelle `IssueType`/`ProjectIssueType` ohne CRUD/UI; Leerzustand „Get Pro to enable Work item types.“ | EE-P04-001 |
| 7 | „Estimates“ Advanced (Pro) | Zeit-System nur als Konstante mit `is_ee: true` (`packages/constants/src/estimates.ts` Z. 140), Auswahl mit `UpgradeBadge` gesperrt (`apps/web/components/estimates/create/stage-one.tsx` Z. 17, 55, 75) | EE-P04-031 |
| 8 | „SAML“, „OIDC“, „LDAP“, „Domain Security“, „Two-factor authentication and passkeys“ | keine Implementierung; nur generische Login-Extension-Points (Dok. 27 Anhang B); `grep two_factor\|2fa\|totp\|mfa\|passkey\|webauthn` nur in `plans.tsx` (Dok. 27 P08-07) | EE-P08-001/002/004/010/007/008 |

### 6.4 Umgekehrte Abweichung: in Cloud-Free bzw. Commercial-Free enthalten, im CE **nicht** vorhanden

| # | Feature | Plan laut Quelle | CE | EE-ID |
|---|---|---|---|---|
| 1 | Jira-Importer (ohne Custom Props) | Matrix Free/One „Without custom props“ (`plans.tsx` Z. 939–949) | fehlt (Stub) | EE-P09-020 |
| 2 | GitHub-Importer (ohne Custom Props) | Matrix Free/One „Without custom props“ (`plans.tsx` Z. 950–960) | fehlt (Stub) | EE-P09-028 |
| 3 | Linear-, Asana-, CSV-Importer | „available on Plane Cloud and on all plans of the Commercial Edition“ | fehlt | EE-P09-022, EE-P09-023, EE-P09-027 |
| 4 | Importer-Framework (Imports-Seite, Job-Status, Worker) | Commercial-Free | Stub | EE-P09-019 |
| 5 | Mobile-Apps | „all plans of the Commercial Edition“; Cloud-Free-Workspace genügt | Stub (Modelle `Device`/`DeviceSession` ungenutzt) | EE-P09-054 |
| 6 | God Mode: User Management, Session-Einstellungen, System checks / Health-Probes | „Commercial Edition“ ohne Plan-Badge | teilweise | EE-P08-025, EE-P08-026, EE-P03-001 |
| 7 | Betriebsfeatures des Commercial-Charts, External-API-Instanz, GraphQL-/Marketplace-Routen, Prime CLI | Commercial-Chart / jede Commercial-Installation | teilweise bzw. fehlt | EE-P03-004, EE-P03-005, EE-P03-006, EE-P03-008 |
| 8 | Automation-Consumer/Outbox-Architektur, Prime/Monitor | Commercial-Infrastruktur | fehlt bzw. Stub | EE-P06-018, EE-P08-021 |

---

## 7. Coming soon / nicht verifizierbar / nicht gezählt

### 7.1 Matrix-„COMING SOON“ und auskommentierte Matrix-Zeilen – aktueller Stand

| # | Matrix-Zeile | Zeilen `plans.tsx` | Plan laut Matrix | Stand laut Quellen | EE-ID |
|---|---|---|---|---|---|
| 1 | Initiatives | 272–282 | Pro | **ausgeliefert** (API-Referenz `AR/initiative/*`, University-Kurs 05) | EE-P04-011 |
| 2 | Checkpoints | 284–295 | Pro | nicht ausgeliefert (Milestones sind ein anderes Feature, Dok. 21 F06) | EE-P04-013 |
| 3 | Pre-defined work item Templates | 368–379 | Pro | nicht belegt | EE-P06-023 |
| 4 | Emails For Intake | 458–468 | Business | **ausgeliefert** (Docs-Badge „Business“, `configure-dns-email-service.md` Z. 7) | EE-P04-041 |
| 5 | Insights | 560–571 | Pro | nicht belegt | EE-P05-014 |
| 6 | Advanced Pages Analytics | 584–595 | Business | **ausgeliefert** (Doku/Guide Business) | EE-P07-023 |
| 7 | Custom Reports | 596–607 | Business | nicht belegt | EE-P05-016 |
| 8 | Approvals (Workspace/Projekt/WIT) | 716–727 | Business | nicht belegt; ausgeliefert sind Workflow-Approval-Flows (Enterprise Grid, EE-P06-003) | EE-P06-008 |
| 9 | API-enabled Audit Logs | 750–761 | Business | **ausgeliefert** (Commercial v3.1.0, Doku Enterprise Grid) | EE-P08-017 |
| 10 | Decisions And Loops Automation | 779–790 | Business | nicht belegt | EE-P06-015 |
| 11 | Databases + Formulas | 908–920 | Business | nicht ausgeliefert (Dok. 26 P07-20) | EE-P07-018 |
| 12 | Nested Pages | 921–932 | Business | **ausgeliefert** (Doku/Blog Business+) | EE-P07-004 |
| 13 | LDAP | 1116–1127 | Enterprise | **ausgeliefert** (Docs-Badge „Enterprise Grid“, `ldap.md` Z. 7) | EE-P08-004 |
| 14 | Private deployments | 1190–1201 | Enterprise | nicht belegt | EE-P03-010 |
| 15 | Sektion „Integrations“ (`comingSoon: true`): Framework | 963–967 | Pro | **ausgeliefert** (Docs-Badges „Pro“) | EE-P09-001 |
| 16 | – GitHub | 968–979 | Pro | **ausgeliefert** | EE-P09-002 (+ EE-P09-003/004/005) |
| 17 | – Slack | 980–990 | Pro | **ausgeliefert** | EE-P09-009 (+ EE-P09-010/011) |
| 18 | – Zapier | 991–1001 | Pro | keine Auslieferung belegt | EE-P09-015 |
| 19 | – Zendesk | 1002–1012 | Pro | keine Auslieferung belegt | EE-P09-016 |
| 20 | – Freshdesk | 1013–1023 | Pro | keine Auslieferung belegt | EE-P09-017 |
| 21 | Bulk Ops, Zellen Business/Enterprise „Work item transfers and conversions“ | 168–179 | Business | nicht belegt | EE-P04-019, EE-P04-021 |
| 22 | auskommentiert: Project Overview | 318–329 | Pro | schwach belegt (Overview-Abschnitt „Milestones“) | EE-P04-035 |
| 23 | auskommentiert: Project Updates | 354–366 | Pro | v2-Projekt-Flag `is_project_updates_enabled` vorhanden, Plan schwach belegt | EE-P04-036 |
| 24 | auskommentiert: Time Capsule | 572–583 | Business | nicht belegt | EE-P05-017 |
| 25 | auskommentiert: Search („Operator capsules from text or PQL“) | 625–656 | Pro | nicht belegt; PQL selbst ausgeliefert (Enterprise Grid, EE-P05-027) | EE-P05-028 |

Ergebnis: Von 14 COMING-SOON-Zeilen, 5 Zeilen der COMING-SOON-Sektion „Integrations“, den Bulk-Ops-Zellen und 4 auskommentierten Zeilen sind 9 Features nachweislich ausgeliefert (Marker ᶜˢ⁺), 16 Features tragen weiterhin den Marker ᶜˢ (inkl. EE-P04-021 Conversions).

### 7.2 Plan oder Existenz nur indirekt belegt / UNVERIFIZIERT (Marker ᵘ, 45 Features)

| # | ID | Feature | ab Plan | Grund |
|---|---|---|---|---|
| 1 | EE-P01-001 | Multi-Workspace-Management (zentrale Verwaltung mehrerer Workspaces einer Organisation) | Enterprise (Grid) | nur WebSearch-Beleg (plane.so/business, Changelog v2.2.0); Plan Enterprise Grid |
| 2 | EE-P01-002 | Product Tour / „Get started“ (geführte Touren, Demo-Projekt, Get-started-Checkliste; i18n-Namespace `tour`) | unklar | Cloud-/Commercial-Onboarding; kein Plan belegt |
| 3 | EE-P02-005 | Public API v2 (`/api/v2/`: PATCH-only, problem+json, Offset-/Cursor-Pagination, `?fields=`/`?expand=`, Upsert, Bulk) | unklar | Commercial Edition/Cloud; Plan-Gating je Ressource über `402 payment_required`; öffentliche Verfügbarkeit UNVERIFIZIERT |
| 4 | EE-P03-006 | GraphQL- und Marketplace-Endpunkte (`/graphql/`, `/marketplace/`) | Commercial-Free | Commercial-Chart-Pflichtrouten; Inhalt nicht dokumentiert |
| 5 | EE-P03-007 | Flux – Realtime-Event-Server (`/flux`, WebSocket mit Redis) | unklar | nur in Docs (Health, FIPS-Images), nicht im Chart |
| 6 | EE-P04-008 | Roll-ups (Property-Aggregation) | Business | nur Matrix-Text; ob mit Workspace-Properties nach Enterprise Grid verschoben, UNVERIFIZIERT |
| 7 | EE-P04-021 | Conversions (Work Item ↔ Epic; Bulk-Conversions) | unklar | Einzelkonvertierung = Typwechsel (Epics Pro), Plan nicht belegt; Bulk-Conversions Business coming soon |
| 8 | EE-P04-035 | Project Overview (Projekt-Übersichtsseite: Snapshot, Links, Attachments, Milestones) | Pro | Matrix-Zeile auskommentiert („coming soon“); indirekt gestützt durch Pro-Milestones im Overview |
| 9 | EE-P04-036 | Project Updates (Status-Updates On-Track/Off-Track/At-Risk mit Kommentaren/Reaktionen) | Pro | nur auskommentierte Matrix-Zeile; v2-Projekt-Flag `is_project_updates_enabled` |
| 10 | EE-P04-046 | Property Contexts (kontextabhängige Regeln einer Workspace-Property je Projekt-/Typ-Menge) | Enterprise (Grid) | folgt Workspace-Properties (Enterprise Grid); Dok. 21 F40 führt Business nach Matrix Z. 222–223 |
| 11 | EE-P05-002 | Teamspace-Work-Items (Tabs „Team“/„Project“, Gruppierung „Team project“) | Pro | abgeleitet aus Teamspaces |
| 12 | EE-P05-003 | Teamspace-Projekt-Work-Items | Pro | abgeleitet aus Teamspaces |
| 13 | EE-P05-004 | Teamspace-Views und Teamspace-Pages | Pro | abgeleitet aus Teamspaces |
| 14 | EE-P05-006 | Teamspace-Kommentare/-Updates | unklar | keine Plan-Quelle |
| 15 | EE-P05-008 | Teamspace-bezogene Member-Auswahl, Suche, Realtime-Kontext | Pro | abgeleitet aus Teamspaces |
| 16 | EE-P05-011 | Dashboard-Filter inkl. PQL (Ebenen source, quick, widget) | unklar | Standard-Filter vermutlich wie Dashboards (Pro), PQL-Anteil wie PQL (Enterprise Grid) |
| 17 | EE-P05-012 | Dashboard-Widgets für Intake und Custom Properties | unklar | nur Changelog-Titel |
| 18 | EE-P05-013 | Dashboard-Widgets in Pages einbetten („Link dashboard widgets“-Block) | Enterprise (Grid) | Doku-Label „Enterprise“ nur aus Autoren-Suche, UNVERIFIZIERT |
| 19 | EE-P05-015 | Erweiterte Analytics-Tabs (Cycles, Modules, Intake, Projects/Users) mit Tab-Gating | unklar | Text „Upgrade to {plan} to unlock {tab}“; Plan je Tab unbekannt |
| 20 | EE-P05-017 | Time Capsule (Point-in-time-Snapshots) | Business | Matrix-Zeile auskommentiert („coming soon“) |
| 21 | EE-P05-020 | Auto-schedule Cycles (wiederkehrende Cycles) | Business | nur University 201/09 „Cycle Automation“ (Business); Dok. 20/25 „unklar“; Changelog v1.16.0 ohne Plan |
| 22 | EE-P05-028 | Operator-Kapseln und erweiterte Filteroperatoren (Negation, OR) im Filter-UI | Pro | auskommentierte Matrix-Zeile „Search“; soweit aus PQL erzeugt, gilt PQL-Plan |
| 23 | EE-P05-032 | Text to PQL (natürliche Sprache → PQL, AI) | Enterprise (Grid) | Launch-Blog 12.05.2026 „Enterprise-only“ (sekundär) |
| 24 | EE-P06-024 | Template-Marketplace (Publish, Kategorien, Verifizierung, Kopie) | unklar | Marketplace-Publish ohne Plan-Angabe |
| 25 | EE-P07-006 | Page-Versionen: „Highlight changes“, Vergleich zweier Versionen, Server-Restore | unklar | vermutlich wie Versionen |
| 26 | EE-P07-014 | Page-Level-Kommentare, Kommentar-Filter, Moderation (hide/unhide) | unklar | keine Plan-Angabe |
| 27 | EE-P07-017 | Moving Pages (Projekt ↔ Projekt ↔ Teamspace ↔ Wiki/Collection) | Pro | „Moving is marked as a Pro feature“ nur Autoren-Suche, UNVERIFIZIERT |
| 28 | EE-P07-024 | Plane AI im Editor: Selection-Aktionen (Paraphrase, Simplify, Elaborate, Summarize, Get title, Ton) und Seitenzusammenfassung | Pro | Guide „Page-level AI writing assistance and summaries start on Pro“ (UNVERIFIZIERT) |
| 29 | EE-P07-026 | Plane AI: Prompt/Agent in Pages mit Proposals (accept/reject) | Business | Doku Business vs. Blog Pro+; Gleichsetzung „Free-form Page editing“ = Proposals UNVERIFIZIERT |
| 30 | EE-P07-034 | HTML-Artifact-Block (sandboxed) | Business | Doku-Label nur aus Autoren-Suche |
| 31 | EE-P07-036 | „Link pages“-Block (Live-Liste von Wiki-Seiten) | Business | Doku-Label nur aus Autoren-Suche |
| 32 | EE-P07-037 | Page-Embed-Block (`/page`) und „Linked page embed“ | Business | an Nested Pages gekoppelt |
| 33 | EE-P07-038 | Widget-Block (Chart aus Work-Item-Daten) | unklar | keine Plan-Angabe |
| 34 | EE-P07-039 | Block-Links (Link auf einen Block kopieren) | unklar | keine Plan-Angabe |
| 35 | EE-P07-040 | Page-Benachrichtigungen (Freigabe-Mail, Page-Subscriber) | unklar | keine Plan-Angabe |
| 36 | EE-P07-042 | Erweiterte Mentions im Document-Editor (Seiten/Projekte/Zyklen/Module) und Backlinks | unklar | keine Plan-Angabe |
| 37 | EE-P08-003 | Workspace-Identity: verifizierte Domains und Workspace-SSO (SAML oder OIDC) | Business | plane.so/business „SSO on Cloud“ (sekundär) vs. Dok. 20 PF-93 (One, Matrix) und Dok. 22 P03-F06 (unklar) |
| 38 | EE-P08-006 | SCIM-Provisioning | Enterprise (Grid) | Cloud „Business Plus“, Self-hosted „Available on plans (Commercial and Airgapped)“ (self-hosting-101.md Z. 42); Whitepaper Enterprise Grid; UNVERIFIZIERT |
| 39 | EE-P09-013 | HubSpot-Connector | unklar | nur Helm-Connector belegt |
| 40 | EE-P09-014 | Cursor-Agent-Integration | unklar | nur Silo-Secret belegt |
| 41 | EE-P09-025 | Notion-Importer | unklar | Plan nicht genannt |
| 42 | EE-P09-034 | Plane AI: Memory | Pro | wie Plane AI |
| 43 | EE-P09-036 | Plane AI: Autopilot-Modus (Ausführung ohne Einzelbestätigung) | Pro | wie Plane AI; belegt für Mobile |
| 44 | EE-P09-037 | AI-Work-Creation (Text → Work Items) und Beschreibungs-Generierung | unklar | nur Changelog-Titel |
| 45 | EE-P09-040 | AI-Aktionen Summary, Catch-up, Copy-as-prompt, AI-Filter | unklar | keine Plan-Angabe |

### 7.3 Nicht gezählte Einträge

Die folgenden Quell-Einträge sind **nicht** in den 246 Features enthalten, weil weder eine Funktion noch ein Bezahl-Gate belegt ist bzw. das Feature zur CE gehört:

| # | Quell-Eintrag | Feature | Grund der Nicht-Zählung |
|---|---|---|---|
| X-01 | 20 PF-105 (`P01#104`) | Weitere Commercial-Produkte ohne Funktionsspur: Desk, Bridge, Briefs, Workgraph, Library/Excerpts, reservierte Slugs `chat`, `calendar`, `drive`, `channels` (Argus siehe EE-P08-027) | nur Icons in `@makeplane/propel` 0.7.3 bzw. reservierte Workspace-Slugs; keine Funktion, keine Texte, keine Endpunkte (Dok. 20 PF-105, OP-09) – nicht spezifizierbar |
| X-02 | 24 P05-26 (`P05#025`) | Cycle Updates (Status-Updates an Cycles) | Existenz UNVERIFIZIERT; Updates-Modul nur für Project Updates belegt (Dok. 24 P05-26) |
| X-03 | 26 P07-26 (`P07#025`) | Stickies-Erweiterungen | kein Bezahl-Gate belegbar; Matrix ohne Stickies-Zeile; Stickies sind CE (Dok. 26 P07-26) |
| X-04 | 28 P09-F18 (`P09#017`) | Microsoft Teams | in keiner Quelle belegt (Negativbefund, Dok. 28 P09-F18) |
| X-05 | 28 P09-F19 (`P09#018`) | Discord | nur Propel-Logo-Icon, keine Integration belegt (Dok. 28 P09-F19) |
| X-06 | 28 P09-F31 (`P09#030`) | Monday.com-Importer | nur Propel-Logo-Icon, Existenz UNVERIFIZIERT (Dok. 28 P09-F31) |

Zusätzlich in den Detail-Dokumenten beschrieben, aber bewusst nicht in den JSON-Listen (CE-Funktionen bzw. Billing): Dok. 25 F25 Auto-Archive/Auto-Close (CE, `apps/api/plane/bgtasks/issue_automation_task.py`), Dok. 26 P07-46 Upgrade-/Downgrade-Flows des Wissensmanagements (Billing, entfällt), Dok. 27 P08-30 IdP-Profil-Sync beim Login (`ENABLE_GOOGLE_SYNC`, `ENABLE_GITHUB_SYNC`, `ENABLE_GITLAB_SYNC`, `ENABLE_GITEA_SYNC`; CE).

---

## 8. Gesamtzahlen

### 8.1 Quellbasis und Deduplizierung

| Kennzahl | Wert |
|---|---|
| Quell-Einträge gesamt | 450 |
| davon führend einer EE-ID zugeordnet oder begründet nicht gezählt | 450 (100 %) |
| deduplizierte Bezahl-Features (EE-IDs) | 246 |
| nicht gezählte Einträge (Kap. 7.3) | 6 |
| Features mit mehr als einem Quell-Eintrag (Dubletten zusammengeführt) | 158 |
| Features mit genau einem Quell-Eintrag | 88 |
| Zuordnungen Quell-Eintrag → EE-ID (inkl. Teilaspekte `~`) | 492 |

### 8.2 Features je Mindest-Plan

| ab Plan | Anzahl | Anteil |
|---|---|---|
| Pro | 96 | 39,0 % |
| Business | 51 | 20,7 % |
| Enterprise (Grid) | 27 | 11,0 % |
| Commercial-Free | 16 | 6,5 % |
| Cloud-only | 2 | 0,8 % |
| unklar | 54 | 22,0 % |
| **Summe** | **246** | 100 % |

Kumuliert je Plan-Spalte (Kap. 4):

| Spalte | enthalten (`✓`) | davon „✓ (abgeleitet)“ | teilweise | nicht enthalten (`–`) | nicht belegt (`?`) | Summe |
|---|---|---|---|---|---|---|
| Pro | 113 | 0 | 1 | 78 | 54 | 246 |
| Business | 165 | 0 | 1 | 27 | 53 | 246 |
| Enterprise (Grid) | 245 | 52 | 0 | 0 | 1 | 246 |

### 8.3 Features je Cluster und Mindest-Plan

| Heimat-Cluster | Quell-Einträge | Features | Pro | Business | Enterprise | Commercial-Free | Cloud-only | unklar |
|---|---|---|---|---|---|---|---|---|
| P01 Repo-Spuren (20) | 105 | 2 | 0 | 0 | 1 | 0 | 0 | 1 |
| P02 API-Referenz (21) | 43 | 6 | 1 | 0 | 0 | 0 | 0 | 5 |
| P03 Architektur/Self-Hosting (22) | 46 | 10 | 1 | 0 | 3 | 5 | 0 | 1 |
| P04 Work Management (23) | 53 | 46 | 24 | 11 | 5 | 0 | 0 | 6 |
| P05 Planung/Insights/Teams (24) | 35 | 32 | 17 | 5 | 3 | 0 | 0 | 7 |
| P06 Workflows/Automation/Templates (25) | 28 | 26 | 4 | 13 | 7 | 1 | 0 | 1 |
| P07 Wissen/Pages (26) | 46 | 42 | 16 | 18 | 0 | 0 | 0 | 8 |
| P08 Sicherheit/Admin/Lizenz (27) | 33 | 27 | 10 | 4 | 8 | 3 | 1 | 1 |
| P09 Integrationen/Importer/AI/Plattform (28) | 61 | 55 | 23 | 0 | 0 | 7 | 1 | 24 |
| **Summe** | **450** | **246** | **96** | **51** | **27** | **16** | **2** | **54** |

Hinweis: P01–P03 sind Querschnitts-Cluster; ihre Einträge sind überwiegend Dubletten und den Themen-Clustern zugeordnet (Anhang C), deshalb sind dort nur 2, 6 bzw. 10 Features beheimatet.

### 8.4 CE-Status je Mindest-Plan

| CE-Status | Pro | Business | Enterprise (Grid) | Commercial-Free | Cloud-only | unklar | Summe |
|---|---|---|---|---|---|---|---|
| fehlt | 30 | 39 | 21 | 6 | 1 | 29 | **126** |
| Stub | 47 | 7 | 3 | 5 | 0 | 12 | **74** |
| teilweise | 17 | 5 | 3 | 5 | 1 | 13 | **44** |
| CE (nur Cloud-Gating) | 2 | 0 | 0 | 0 | 0 | 0 | **2** |
| **Summe** | 96 | 51 | 27 | 16 | 2 | 54 | **246** |

### 8.5 Konfidenz

| Konfidenz | Pro | Business | Enterprise (Grid) | Commercial-Free | Cloud-only | unklar | Summe |
|---|---|---|---|---|---|---|---|
| hoch | 45 | 12 | 7 | 6 | 1 | 16 | **87** |
| mittel | 37 | 26 | 15 | 9 | 1 | 25 | **113** |
| niedrig | 14 | 13 | 5 | 1 | 0 | 13 | **46** |

### 8.6 Marker

| Marker | Bedeutung | Anzahl |
|---|---|---|
| ¹ | Matrix bereits „One“ (Legacy) | 12 |
| ᶜˢ | COMING SOON, Auslieferung nicht belegt | 16 |
| ᶜˢ⁺ | COMING SOON in der Matrix, inzwischen ausgeliefert | 9 |
| ⚠ | Plan-Widerspruch aufgelöst | 20 |
| ᵘ | indirekt/abgeleitet bzw. UNVERIFIZIERT | 45 |
| ‡ | entfällt als Billing-/Lizenz-/Kontingent-/Vertriebsmechanik | 14 |

### 8.7 Widersprüche

| Art | Anzahl | Kapitel |
|---|---|---|
| strukturelle Widersprüche der Quellenlage | 7 | 3.1 |
| Plan-Widersprüche zwischen Quell-Einträgen | 14 | 3.2 |
| Abweichungen gegenüber `plans.tsx`/`subscription.ts`/Upsell-Text | 11 | 3.3 |
| weitere in den Quellen dokumentierte und dort aufgelöste Plan-Konflikte | 25 | 3.4 |
| CE-Status-Widersprüche zwischen Detail-Dokumenten | 28 | 3.5 |

### 8.8 Antwort auf die Auftraggeber-Frage in Zahlen

| Frage | Antwort |
|---|---|
| Wie viele Features fehlen der CE gegenüber der Top-Lizenz (Enterprise Grid, Self-hosted)? | **244** (246 abzüglich der 2 Cloud-only-Features); davon sind 12 reine Billing-/Lizenz-/Kontingent-/Vertriebsmechanik (‡) |
| … davon fachlich umzusetzen (ohne ‡) | **232** |
| … davon laut Matrix weiterhin „coming soon“ ohne Auslieferungsbeleg | 16 |
| Wie viele gibt es **nur** in der Top-Lizenz? | **27** (Kap. 5.1) + 11 Abstufungen (Kap. 5.7.1) |
| Wie viele kommen mit Business hinzu? | **51** (Kap. 5.2) + 11 Abstufungen (Kap. 5.7.2) |
| Wie viele bringt bereits Pro? | **96** (Kap. 5.3) |
| Wie viele sind in jeder Commercial-Installation, aber nicht in der CE? | **16** (Kap. 5.4) |
| Wie viele sind in Commercial/Cloud ohne belegten Plan? | **54** (Kap. 5.6) |

---

## 9. Konsequenzen für die Zielplattform (ADR-001/ADR-004)

Nach ADR-001 werden **alle 246 Features** ohne Plan-Gating umgesetzt; die Spalten „ab Plan“/„Pro“/„Business“/„Enterprise“ steuern **nichts**. Die 14 mit ‡ markierten Features sind keine Fachfunktionen, sondern Mechanik des Originals; ihre Behandlung:

| EE-ID | Feature | Behandlung in der Zielplattform | Grundlage |
|---|---|---|---|
| EE-P03-008 | Prime CLI und Commercial-Installationsmethoden | ersetzt durch Aspire-AppHost/Container-Artefakte; Backup/Restore als Betriebsfunktion separat spezifizieren | ADR-000, ADR-004 |
| EE-P03-009 | Installationskanäle One-click/DigitalOcean/Heroku/AWS AMI | entfällt (keine Marktplatz-Apps) | ADR-004 |
| EE-P03-010 | Private + managed deployments | entfällt (Herstellerleistung) | ADR-001, ADR-004 |
| EE-P06-016 | Anzahl Automationen je Workspace | kein Plan-Limit; optional konfigurierbares Instanz-Limit mit Default „unbegrenzt“ | ADR-001 (Konsequenzen) |
| EE-P08-014 | Guests-Kontingent | entfällt; die Gast-Rolle bleibt (CE-Funktion) | ADR-001 |
| EE-P08-018 | Workspace-Lizenz, Seite „Billing and plans“, Trial, Upgrade-Flows | entfällt vollständig (keine Billing-Seite, keine Upgrade-Modals/-Badges) | ADR-001 |
| EE-P08-019 | Enterprise-Grid-Instanzlizenz | entfällt | ADR-001 |
| EE-P08-020 | Offline-Lizenzdatei (Airgapped) | entfällt; Airgapped-Betrieb selbst bleibt Pflicht (EE-P03-002) | ADR-001, ADR-004 |
| EE-P08-021 | Prime-Portal und Monitor-Dienst | entfällt (kein Feature-Flag-Server, kein Lizenzabgleich) | ADR-001 |
| EE-P08-022 | Member-Limits und Seat-Berechnung | entfällt | ADR-001 |
| EE-P08-023 | Storage-Limits | keine Plan-Kontingente; `FILE_SIZE_LIMIT` (CE) bleibt als Instanz-Einstellung | ADR-004 |
| EE-P08-024 | Support-Kanäle, SLA, „Chat with us“ | entfällt | ADR-001 |
| EE-P09-043 | AI-Usage, Credits, Token-Budget | Credits entfallen; Token-Budget/Nutzungsgrenzen als Instanz-Einstellung | ADR-001, ADR-004 |
| EE-P09-055 | Flatfile-Importer | entfällt (Cloud-only); Ersatz CSV-Importer EE-P09-027 | ADR-004 |

Weitere Folgerungen:

- **Feature-Schalter bleiben** (fachliche Einstellungen, kein Gating): Projekt-Feature-API EE-P02-002 und Workspace-Feature-API EE-P02-003 (`epics`, `work_item_types`, `parallel_cycles`, `project_updates`, `workflows`, `project_grouping`, `initiatives`, `teams`, `customers`, `wiki`, `pi`) – ADR-001.
- **Upsell-Hüllen des CE** (Stub-Status, 74 Features) werden nicht 1:1 übernommen, sondern durch die echte Funktion ersetzt (ADR-005: Abweichung nur durch ADR-001); vollständiges Inventar der Upsell-Stellen in Dok. 20 Kap. 5 (U1–U22) und der CE-Stubs in Dok. 20 Kap. 6 (S1–S66).
- **Plan-Limits werden Instanz-Einstellungen** mit großzügigen Defaults (Page-Versionen EE-P07-005, Automationen EE-P06-016, Exporte EE-P07-009) – ADR-001, Konsequenzen.
- **Airgapped/Self-hosted:** externe Dienste der Commercial Edition (Iframely EE-P07-020, draw.io EE-P07-019, LLM-Provider EE-P09-042, Integrationen EE-P09-001 ff.) sind optional und abschaltbar; AI muss mit lokal betreibbarem, OpenAI-kompatiblem Provider funktionieren – ADR-004.
- **Coming-soon-Features ohne Auslieferungsbeleg** (16, Kap. 7.1) haben keine öffentliche Spezifikation; sie sind Bestandteil der Bestandsaufnahme, ihr Umfang muss vor einer Umsetzung mit dem Auftraggeber geklärt werden.

---

## Anhang A: Zusammengeführte Dubletten (Mehrfach-Quellen je Feature, 158)

`~` = Quell-Eintrag beschreibt nur einen Teilaspekt des Features (Sammel-Eintrag).

| ID | Feature | zusammengeführte Quell-Einträge (führend zuerst; ~ = Teilaspekt) |
|---|---|---|
| EE-P03-001 | Health-Probes und God-Mode-„System checks“ (`/api/live/`, `/api/ready/`, `/api/health/` je Dienst) | P03 P03-F34, ~P03 P03-F03 |
| EE-P03-002 | Airgapped Edition (Betrieb ohne Internet, Images aus eigener Registry, Offline-Aktivierung) | P03 P03-F36, P08 P08-23b, ~P01 PF-100 |
| EE-P03-003 | FIPS-140-3-Images / FIPS-Betriebsprofil | P03 P03-F37, P08 P08-23c, ~P01 PF-100 |
| EE-P03-009 | Installationskanäle der Matrix: One-click Deployment, DigitalOcean-Marketplace-App, Heroku-App, AWS AMI | P08 P08-23a, P01 PF-100 |
| EE-P03-010 | Private + managed deployments (vom Hersteller betriebene private Cloud-Instanz) | P03 P03-F46, P08 P08-23d, ~P01 PF-100 |
| EE-P04-001 | Work Item Types auf Projekt-Ebene (Name, Beschreibung, Icon, Farbe, Default-Typ, aktiv/inaktiv, Typwechsel) | P04 WM-01, P01 PF-05, P02 F08 |
| EE-P04-002 | Work-Item-Type-Hierarchie (Level, Parent/Child-Regeln, Bruch-Validierung; irreversibel) | P04 WM-02, P01 PF-08 |
| EE-P04-003 | Custom Properties auf Projekt-Ebene (Property-Engine, Werte am Work Item) | P04 WM-03, P01 PF-06, P02 F09 |
| EE-P04-006 | Formula-Properties (`property_type=FORMULA`) | P04 WM-06, P02 F10 |
| EE-P04-007 | Workspace-Level Properties und Workspace-Level Types (Workspace-Modus: Katalog, Import, Link/Unlink, Governance) | P04 WM-07, P01 PF-07, P02 F43 |
| EE-P04-009 | Epics (Work-Item-Typ Epic, Epic-Kinder, Epic-API) | P04 WM-09, P01 PF-14, P02 F01 |
| EE-P04-011 | Initiatives (Bündelung von Epics/Projekten bzw. Work Items) | P04 WM-11, P01 PF-15, P02 F02 |
| EE-P04-012 | Initiative-Labels | P04 WM-12, P02 F03 |
| EE-P04-013 | Checkpoints und Updates an Projekten/Epics/Initiativen | P04 WM-13, P01 PF-16 |
| EE-P04-014 | Milestones (Projekt-Meilensteine, Work-Item-Zuordnung) | P04 WM-14, P02 F06, P01 PF-17 |
| EE-P04-015 | Releases (Workspace- und Projekt-Releases, Tags, Labels, Links, Kommentare, Changelog) | P04 WM-15, P02 F24, P01 PF-42 |
| EE-P04-016 | Customers (Kundenprofile, Work-Item-Verknüpfung) | P04 WM-16, P01 PF-41, P02 F04 |
| EE-P04-017 | Customer Requests | P04 WM-17, ~P02 F04 |
| EE-P04-018 | Customer Properties | P04 WM-18, ~P02 F04 |
| EE-P04-019 | Bulk Ops (Mehrfachauswahl, Property-Änderung, Archivieren, Löschen, Abonnieren) | P04 WM-22, P01 PF-02 |
| EE-P04-020 | Work Item Transfers (Work Item in anderes Projekt oder anderen Cycle verschieben) | P04 WM-23, P01 PF-11 |
| EE-P04-022 | Kopie eines Work Items in ein anderes Projekt („Duplicate work items and epics across projects“) | P04 WM-25, P01 PF-38 |
| EE-P04-023 | Dependencies in Gantt (Starts/Finishes Before/After, Verbindungslinien, abhängige Verschiebung; Dependencies-API) | P04 WM-26, P01 PF-09, P02 F39 |
| EE-P04-024 | Custom Relations (frei definierbare Relationstypen, Workspace-Settings „Relations“) | P04 WM-27, P02 F22, ~P01 PF-10 |
| EE-P04-025 | Eingebauter Relationstyp „Implements“ / „Implemented by“ | P04 WM-53, P01 PF-10 |
| EE-P04-026 | Module Overview (Übersicht mit Details und Fortschrittsdiagrammen je Modul) | P04 WM-30, P01 PF-18 |
| EE-P04-027 | Auto-assignment in Modules (Zuweisungsregeln Linear, Round Robin, Capacity) | P04 WM-31, P01 PF-19, P06 F29 |
| EE-P04-028 | Time Tracking und Worklogs (Zeit je Work Item, Worklogs-Tab, Tracked time) | P04 WM-32, P01 PF-03, P02 F07 |
| EE-P04-031 | Advanced Estimates (System `time`, Bearbeiten, Umsortieren, Systemwechsel) | P04 WM-35, P01 PF-01, P02 F21 |
| EE-P04-032 | Public, Private und Secret Projects (Stufe „Private mit Beitrittsgenehmigung“) | P04 WM-36, P01 PF-20 |
| EE-P04-033 | State of Projects / Project States (Project Grouping) | P04 WM-37, P01 PF-21, P02 F18 |
| EE-P04-034 | Project Labels | P04 WM-38, ~P01 PF-21, ~P02 F18 |
| EE-P04-035 | Project Overview (Projekt-Übersichtsseite: Snapshot, Links, Attachments, Milestones) | P04 WM-39, P01 PF-22 |
| EE-P04-036 | Project Updates (Status-Updates On-Track/Off-Track/At-Risk mit Kommentaren/Reaktionen) | P04 WM-40, P01 PF-23, P02 F27 |
| EE-P04-037 | Baselines And Deviations | P04 WM-42, P01 PF-32 |
| EE-P04-038 | Custom SLAs (SLA-Matrizen für zeitkritische Work Items) | P04 WM-43, P01 PF-35 |
| EE-P04-039 | Intake Forms (extern erreichbare Web-Formulare) | P04 WM-44, P01 PF-36 |
| EE-P04-040 | Intake Assignees / Intake responsibility (Standard-Bearbeiter, Benachrichtigung) | P04 WM-45, P01 PF-34 |
| EE-P04-041 | Emails For Intake (E-Mail-Adresse je Projekt-Intake) | P04 WM-46, P01 PF-37, P02 F28, P03 P03-F23 |
| EE-P04-042 | Work-Item-Votes in der App (Up-/Downvotes an Work Items, Epics, Intake) | P04 WM-48, P01 PF-40 |
| EE-P04-043 | Kommentar-Antworten (Reply-Threads unter Work-Item-Kommentaren) | P04 WM-49, P01 PF-39 |
| EE-P04-046 | Property Contexts (kontextabhängige Regeln einer Workspace-Property je Projekt-/Typ-Menge) | P04 WM-52, P02 F40 |
| EE-P05-001 | Teamspaces (Anlegen/Ändern/Löschen, Lead, Beschreibung, Logo, Mitglieder, Projekte) | P05 P05-01, P01 PF-30, P02 F05 |
| EE-P05-004 | Teamspace-Views und Teamspace-Pages | P05 P05-04, P07 P07-17 |
| EE-P05-005 | Teamspace Cycles (mehrere Cycles mehrerer Projekte gleichzeitig) | P05 P05-05, P01 PF-31 |
| EE-P05-009 | Dashboards (eigene Dashboards) | P05 P05-09, P01 PF-45 |
| EE-P05-013 | Dashboard-Widgets in Pages einbetten („Link dashboard widgets“-Block) | P05 P05-13, P07 P07-42 |
| EE-P05-014 | Insights (Hindsight, On-demand insights, Foresights) | P05 P05-14, P01 PF-48 |
| EE-P05-015 | Erweiterte Analytics-Tabs (Cycles, Modules, Intake, Projects/Users) mit Tab-Gating | P05 P05-15, ~P01 PF-50 |
| EE-P05-016 | Custom Reports (Berichte nach beliebiger Dimension/Metrik) | P05 P05-16, P01 PF-50 |
| EE-P05-017 | Time Capsule (Point-in-time-Snapshots) | P05 P05-17, P01 PF-51 |
| EE-P05-018 | Progress Charts (Cycle-Fortschritt v2, Scope-Linie, Burn-down/Burn-up) | P05 P05-19, P01 PF-46 |
| EE-P05-019 | Cycle Reports (On-demand, Permalinks) | P05 P05-20, P01 PF-47 |
| EE-P05-020 | Auto-schedule Cycles (wiederkehrende Cycles) | P05 P05-21, P04 WM-29, P01 PF-13, P06 F27 |
| EE-P05-021 | Auto-transfer Cycle Work items / Auto-Rollover | P05 P05-22, P04 WM-28, P01 PF-12, P06 F28 |
| EE-P05-022 | Workspace-weite Active Cycles | P05 P05-23, P01 PF-04 |
| EE-P05-025 | Shared Views (View mit ausgewählten Mitgliedern teilen) | P05 P05-27, P01 PF-43 |
| EE-P05-026 | Publish Views (View öffentlich ins Internet stellen) | P05 P05-28, P01 PF-44 |
| EE-P05-027 | PQL (Plane Query Language) | P05 P05-29, P01 PF-52, P02 F25 |
| EE-P05-028 | Operator-Kapseln und erweiterte Filteroperatoren (Negation, OR) im Filter-UI | P05 P05-30, ~P01 PF-52 |
| EE-P05-029 | Advanced Search (OpenSearch-gestützt; Fallback Postgres) | P05 P05-31, P01 PF-53, P02 F20, P03 P03-F11 |
| EE-P05-030 | Scheduled Comms (geplante Berichte, Benachrichtigungen, Nachrichten an Drittsysteme) | P05 P05-32, P01 PF-33 |
| EE-P06-001 | Workflows: Default-Workflow je Projekt (erlaubte State-Wechsel, Mover/Reviewer, „Allow new work items“, Erzwingung) | P06 F01, P01 PF-68, P02 F42 |
| EE-P06-002 | Mehrere, typ-spezifische Workflows je Projekt | P06 F02, ~P02 F42 |
| EE-P06-008 | Approvals auf Workspace-, Projekt- und Work-Item-Type-Ebene (Matrix-Zeile „Approvals“) | P06 F08, P01 PF-56, P08 P08-15 |
| EE-P06-009 | Custom Automations je Projekt (Trigger → Bedingungen → Aktionen) | P06 F09, P01 PF-63, P02 F35 |
| EE-P06-013 | Global (Workspace-)Automations („All projects“ / „Select projects“) | P06 F13, P01 PF-64, ~P02 F35 |
| EE-P06-015 | Decisions and Loops Automation | P06 F15, P01 PF-65 |
| EE-P06-016 | Anzahl Automationen je Workspace (Limit) | P06 F16, P01 PF-66 |
| EE-P06-018 | Automation-Consumer / Outbox-Architektur (Outbox-Poller → RabbitMQ → Consumer) | P06 F18, P03 P03-F29 |
| EE-P06-019 | Plane Runner (Scripts und Functions für Automationen, Transitionen, Cron) | P06 F19, P03 P03-F28, P09 P09-F54, P01 PF-69 |
| EE-P06-020 | Project Templates (States, Workflows, Automationen, Projekteinstellungen als Vorlage) | P06 F20, P04 WM-41, P01 PF-26, P02 F19 |
| EE-P06-021 | Work Item Templates (Projekt und Workspace, inkl. Sub-Work-Items; Templates-API) | P06 F21, P04 WM-20, P01 PF-25, P02 F37 |
| EE-P06-022 | Page Templates (Projekt-Pages und Wiki) | P06 F22, P07 P07-10, P01 PF-27 |
| EE-P06-023 | Pre-defined work item Templates | P06 F23, P04 WM-21, P01 PF-24 |
| EE-P06-024 | Template-Marketplace (Publish, Kategorien, Verifizierung, Kopie) | P06 F23, P01 PF-28 |
| EE-P06-025 | Recurring Work Items | P06 F24, P04 WM-19, P01 PF-29 |
| EE-P06-026 | Auto-Reminders (Fälligkeits-Erinnerungen) | P06 F26, P01 PF-67 |
| EE-P07-001 | Wiki (Workspace-Seiten ohne Projekt) inkl. Wiki-Home, Sidebar, Feature-Toggle | P07 P07-01, P01 PF-74, P02 F14 |
| EE-P07-002 | Wiki-Collections (öffentlich, Default „General“) inkl. Drag-and-drop-Reordering | P07 P07-02, ~P01 PF-74 |
| EE-P07-004 | Nested Pages (Unterseiten, Hierarchie, Umhängen) | P07 P07-04, P01 PF-78 |
| EE-P07-005 | Page-Versionen: Aufbewahrung | P07 P07-05, P01 PF-76 |
| EE-P07-007 | Real-time Collaboration: Presence-Avatare und Live-Cursor (CRDT-Sync selbst ist CE) | P07 P07-07, P01 PF-70 |
| EE-P07-008 | Page-Publish (öffentlicher Link, Kommentare Externer, Report) | P07 P07-08, P01 PF-73 |
| EE-P07-009 | Page-Exports PDF/Word/Markdown, Hintergrund-Queue, ZIP inkl. Unterseiten | P07 P07-09, P01 PF-75, P03 P03-F30 |
| EE-P07-010 | Work-Item-Embeds in Pages (Block) | P07 P07-11, P01 PF-71 |
| EE-P07-012 | Link Pages ↔ Work Items (Pages-Sektion im Work Item; Work-Item-Pages-API) | P07 P07-13, P01 PF-72, P02 F13 |
| EE-P07-013 | Inline-Kommentare (an markiertem Text, Threads, Resolve) | P07 P07-14, P01 PF-79 |
| EE-P07-014 | Page-Level-Kommentare, Kommentar-Filter, Moderation (hide/unhide) | P07 P07-15, ~P01 PF-79 |
| EE-P07-015 | Page-Sharing / Access-Control (Mitglieder, Can view/comment/edit; Listenfilter `type=shared`) | P07 P07-16, P02 F15, ~P01 PF-80 |
| EE-P07-017 | Moving Pages (Projekt ↔ Projekt ↔ Teamspace ↔ Wiki/Collection) | P07 P07-19, P01 PF-80 |
| EE-P07-018 | Databases + Formulas in Pages | P07 P07-20, P01 PF-77 |
| EE-P07-019 | Draw.io-Diagramme und -Boards in Pages | P07 P07-21, P09 P09-F59, P03 P03-F31 |
| EE-P07-020 | Externe Embeds / Rich Cards (Iframely), Medien per URL | P07 P07-22, P03 P03-F32, ~P01 PF-81 |
| EE-P07-021 | Attachments in Pages (inkl. Office-Bearbeitung) | P07 P07-23, P01 PF-81 |
| EE-P07-023 | Advanced Pages Analytics (Page + Collection) | P07 P07-25, P05 P05-18, P01 PF-49 |
| EE-P07-024 | Plane AI im Editor: Selection-Aktionen (Paraphrase, Simplify, Elaborate, Summarize, Get title, Ton) und Seitenzusammenfassung | P07 P07-27, P09 P09-F39 |
| EE-P07-025 | Plane AI: AI-Block (`/ai`) | P07 P07-28, ~P09 P09-F39 |
| EE-P07-026 | Plane AI: Prompt/Agent in Pages mit Proposals (accept/reject) | P07 P07-29, ~P09 P09-F39 |
| EE-P07-041 | Pages-Public-API (v1/v2: Pages, Collections, Templates, Published Pages, Attachments, Work-Item-Pages, MCP) | P07 P07-45, P02 F33 |
| EE-P08-001 | SAML-SSO instanzweit (God Mode, inkl. God-Mode-Login per SSO) | P08 P08-01, P03 P03-F04, ~P01 PF-93 |
| EE-P08-002 | OIDC-SSO instanzweit (God Mode) | P08 P08-02, P03 P03-F05, ~P01 PF-93 |
| EE-P08-003 | Workspace-Identity: verifizierte Domains und Workspace-SSO (SAML oder OIDC) | P08 P08-03, P03 P03-F06, P01 PF-93 |
| EE-P08-004 | LDAP-Authentifizierung | P08 P08-04, P03 P03-F07, P01 PF-97 |
| EE-P08-005 | IdP Group Sync (OIDC-Gruppen → Workspace-/Projektrollen) | P08 P08-05, P02 F12, P03 P03-F08, P01 PF-98 |
| EE-P08-006 | SCIM-Provisioning | P08 P08-06, ~P01 PF-98 |
| EE-P08-007 | Zwei-Faktor-Authentifizierung | P08 P08-07, P01 PF-95, ~P03 P03-F10 |
| EE-P08-008 | Passkeys | P08 P08-08, ~P01 PF-95, ~P03 P03-F10 |
| EE-P08-009 | Password Policy (eigene Passwort-Richtlinien) | P08 P08-09, P01 PF-96, ~P03 P03-F10 |
| EE-P08-010 | Domain Security (erlaubte/gesperrte Anmelde-Domains) | P08 P08-10, P01 PF-94, P03 P03-F10 |
| EE-P08-011 | Rollen: System-Rollen / RBAC (Owner, Workspace Admin, Member, Guest; Projekt Admin, Contributor, Commenter, Guest) | P08 P08-11, P01 PF-54, P02 F26 |
| EE-P08-012 | Custom Roles (benutzerdefinierte Rollen aus Permission Schemes) | P08 P08-12, ~P02 F26, ~P03 P03-F45 |
| EE-P08-013 | GAC – Granular Access Control (Permission Schemes, bedingte Rechte, effektive Berechtigungen) | P08 P08-13, P03 P03-F45, ~P02 F26 |
| EE-P08-014 | Guests-Kontingent (5 Gäste je bezahltem Mitglied) | P08 P08-14, ~P01 PF-55 |
| EE-P08-015 | Admin Interface (Admin-Übersicht für Workspace- und Projekt-Einstellungen) | P08 P08-16, P01 PF-57 |
| EE-P08-016 | Workspace Activity Logs (filterbares Aktivitätsprotokoll des gesamten Workspace) | P08 P08-17, P05 P05-33, P01 PF-58 |
| EE-P08-017 | API-enabled Audit Logs / Workspace-Audit-Log (Settings + v2-API `audit-logs`) | P08 P08-18, P01 PF-59, P02 F34, P03 P03-F44 |
| EE-P08-018 | Workspace-Lizenz und Seite „Billing and plans“ (Sync plan, Delink, Trial, Upgrade-Flow) | P08 P08-19, P01 PF-103, P03 P03-F01 |
| EE-P08-019 | Enterprise-Grid-Instanzlizenz (God Mode → Billing) | P08 P08-20, ~P03 P03-F01 |
| EE-P08-020 | Offline-Lizenzdatei (Airgapped) | P08 P08-21, ~P03 P03-F01 |
| EE-P08-021 | Prime-Portal und Monitor-Dienst (Lizenzvalidierung, Feature-Flags, Plan-Synchronisation) | P08 P08-22, P03 P03-F02, ~P03 P03-F01 |
| EE-P08-022 | Member-Limits und Seat-Berechnung (Aufhebung der Mitgliedergrenze) | P08 P08-24, P01 PF-55 |
| EE-P08-023 | Storage-Limits (Workspace-Speicher, Max file size) | P08 P08-25, P01 PF-99 |
| EE-P08-024 | Support-Kanäle, SLA und „Chat with us“ | P08 P08-26, P01 PF-101 |
| EE-P08-025 | God Mode: User Management (Instanz-Benutzer, Instanz-Admins einladen, Suspend) | P08 P08-27, P03 P03-F03 |
| EE-P08-026 | God Mode: Session-Einstellungen (Session expiry, Admin session expiry) | P08 P08-28, P03 P03-F35, ~P03 P03-F03 |
| EE-P08-027 | Argus – Sensitive-Data-/PII-Scanner | P08 P08-29, P03 P03-F33, ~P01 PF-105 |
| EE-P09-001 | Integrations-Framework „Silo“, Integrations-Übersicht, Workspace-/persönliche Connections | P09 P09-F01, P03 P03-F14 |
| EE-P09-002 | GitHub: Organisation verbinden, persönliches Konto, Repository-Mapping | P09 P09-F02, P01 PF-84, P03 P03-F15 |
| EE-P09-005 | GitHub Enterprise (Server und Enterprise Cloud ghe.com) | P09 P09-F05, ~P01 PF-84, ~P03 P03-F15 |
| EE-P09-006 | GitLab (gitlab.com): MR-State-Mapping, Issue Sync | P09 P09-F06, P01 PF-85, P03 P03-F16 |
| EE-P09-007 | GitLab Self-managed („Gitlab Enterprise“) | P09 P09-F07, ~P01 PF-85, ~P03 P03-F16 |
| EE-P09-008 | Bitbucket Cloud und Bitbucket Data Center | P09 P09-F08, P01 PF-88, P03 P03-F17 |
| EE-P09-009 | Slack: Workspace verbinden, persönliches Konto, DM-Alerts | P09 P09-F09, P01 PF-86, P03 P03-F18 |
| EE-P09-010 | Slack: Projekt-Benachrichtigungen (Projekt ↔ Channel) | P09 P09-F10, ~P03 P03-F18 |
| EE-P09-011 | Slack: `/plane`-Slash-Command, Message-Shortcuts, Thread-Sync, Link-Unfurl | P09 P09-F11, ~P03 P03-F18 |
| EE-P09-012 | Sentry-Integration | P09 P09-F12, P01 PF-87, P03 P03-F19 |
| EE-P09-013 | HubSpot-Connector | P09 P09-F13, P03 P03-F20 |
| EE-P09-014 | Cursor-Agent-Integration | P09 P09-F14, P03 P03-F21 |
| EE-P09-015 | Zapier | P09 P09-F15, P01 PF-89 |
| EE-P09-016 | Zendesk (Work Items aus Tickets) | P09 P09-F16, P01 PF-90 |
| EE-P09-017 | Freshdesk (Work Items aus Tickets) | P09 P09-F17, ~P01 PF-90 |
| EE-P09-018 | OAuth Bridge (externe IdP-JWTs als API-Credentials) | P09 P09-F20, P03 P03-F09, P01 PF-91 |
| EE-P09-019 | Importer-Framework (Imports-Seite, Job-Status, Historie, Importer-Worker) | P09 P09-F21, P03 P03-F22, ~P01 PF-83 |
| EE-P09-020 | Jira-Cloud-Importer (inkl. Custom Properties) | P09 P09-F22, P01 PF-83 |
| EE-P09-028 | GitHub-Importer | P09 P09-F30, ~P01 PF-83 |
| EE-P09-029 | Mitglieder-Import per CSV (Workspace und Projekt) | P09 P09-F32, P08 P08-31, P01 PF-60 |
| EE-P09-030 | Plane AI: Dienst „PI“, Workspace-Feature `pi`, Settings-Seite „Plane AI“ | P09 P09-F33, P03 P03-F12, P02 F29, P01 PF-82 |
| EE-P09-038 | AI-Suche / Semantic Search (Embeddings, Vektorsuche) | P09 P09-F41, P03 P03-F13 |
| EE-P09-039 | Duplicate Detection (Duplikat-Vorschläge beim Anlegen von Work Items und Intake-Requests) | P09 P09-F42, P04 WM-47, P01 PF-104, ~P03 P03-F13 |
| EE-P09-041 | Applets / Artifacts (AI-generierte, versionierte HTML-Dashboards) | P09 P09-F44, P02 F41 |
| EE-P09-044 | OAuth-App-Plattform („Build your own app“, Consent, Bot-/User-Token, Scopes, Installationen) | P09 P09-F47, P03 P03-F25, P02 F31, P01 PF-92 |
| EE-P09-045 | App-Marketplace | P09 P09-F48, ~P01 PF-92, ~P03 P03-F40 |
| EE-P09-047 | Agents-Plattform (Agent Runs, Activities, Signals) | P09 P09-F50, P03 P03-F26, P02 F30 |
| EE-P09-048 | Webhooks v2 (Webhook-CRUD, Delivery-Logs, v2-Events) | P09 P09-F51, P03 P03-F24, P02 F38 |
| EE-P09-049 | Workspace-Access-Tokens | P09 P09-F52, P01 PF-62 |
| EE-P09-050 | MCP-Server (OAuth-Transport, Tool-Gates) | P09 P09-F53, P03 P03-F27 |
| EE-P09-051 | Plane Compose (project-as-code CLI) | P09 P09-F55, P03 P03-F43 |

---

## Anhang B: Vollständiger Abgleich mit `plans.tsx` und `subscription.ts` (94 Zuordnungen)

„One-Regel“ = Matrix nennt One, Ergebnis Pro (Regel L2). „Abweichung“ = bewusst anderer Plan (Kap. 3.3). Alle Matrix-Zeilen mit `free: true` (Projects, Work items, Comments, Cycles, Modules, Intake, Layouts, Views, Power K, Pages, God Mode) sind CE-Funktionen und daher nicht zugeordnet.

| # | Matrix-Zeile / Repo-Liste | Zeilen | Plan laut Repo | EE-ID | Plan in dieser Matrix | Abgleich |
|---|---|---|---|---|---|---|
| 1 | Estimates (Free/One „Basic“, ab Pro „Advanced“) | `plans.tsx` Z. 145–154 | Pro | EE-P04-031 | Pro | übereinstimmend |
| 2 | Bulk Ops | `plans.tsx` Z. 162–181 | One | EE-P04-019 | Pro | One-Regel |
| 3 | Time Tracking + Worklogs | `plans.tsx` Z. 183–192 | One | EE-P04-028 | Pro | One-Regel |
| 4 | Active Cycles | `plans.tsx` Z. 194–203 | One | EE-P05-022 | Pro | One-Regel |
| 5 | Work item Types | `plans.tsx` Z. 205–214 | Pro | EE-P04-001 | Pro | übereinstimmend |
| 6 | Custom Properties (Pro „Project-level custom properties“) | `plans.tsx` Z. 216–225 | Pro | EE-P04-003 | Pro | übereinstimmend |
| 7 | Custom Properties (Business „Workspace-level properties and roll-ups“) | `plans.tsx` Z. 216–225 | Business | EE-P04-007 | Enterprise (Grid) | Abweichung |
| 8 | Custom Properties (Business „… roll-ups“) | `plans.tsx` Z. 216–225 | Business | EE-P04-008 | Business | übereinstimmend |
| 9 | Dependencies in Gantt | `plans.tsx` Z. 227–236 | Pro | EE-P04-023 | Pro | übereinstimmend |
| 10 | Work item Transfers | `plans.tsx` Z. 238–247 | Pro | EE-P04-020 | Pro | übereinstimmend |
| 11 | Auto-transfer Cycle Work items | `plans.tsx` Z. 249–259 | Pro | EE-P05-021 | Pro | übereinstimmend |
| 12 | Epics | `plans.tsx` Z. 261–270 | Pro | EE-P04-009 | Pro | übereinstimmend |
| 13 | Initiatives (COMING SOON) | `plans.tsx` Z. 272–282 | Pro | EE-P04-011 | Pro | übereinstimmend |
| 14 | Checkpoints (COMING SOON) | `plans.tsx` Z. 284–295 | Pro | EE-P04-013 | Pro | übereinstimmend |
| 15 | Module Overview | `plans.tsx` Z. 297–306 | Pro | EE-P04-026 | Pro | übereinstimmend |
| 16 | Auto-assignment In Modules | `plans.tsx` Z. 308–317 | Pro | EE-P04-027 | Pro | übereinstimmend |
| 17 | Project Overview (auskommentiert, COMING SOON) | `plans.tsx` Z. 318–329 | Pro | EE-P04-035 | Pro | übereinstimmend |
| 18 | Public, Private, and Secret projects | `plans.tsx` Z. 331–341 | Pro | EE-P04-032 | Pro | übereinstimmend |
| 19 | State Of Projects | `plans.tsx` Z. 343–353 | Pro | EE-P04-033 | Pro | übereinstimmend |
| 20 | Project Updates (auskommentiert, COMING SOON) | `plans.tsx` Z. 354–366 | Pro | EE-P04-036 | Pro | übereinstimmend |
| 21 | Pre-defined work item Templates (COMING SOON) | `plans.tsx` Z. 368–379 | Pro | EE-P06-023 | Pro | übereinstimmend |
| 22 | Teamspace Cycles | `plans.tsx` Z. 381–390 | Business | EE-P05-005 | Business | übereinstimmend |
| 23 | Project Templates | `plans.tsx` Z. 392–401 | Business | EE-P06-020 | Business | übereinstimmend |
| 24 | Baselines And Deviations | `plans.tsx` Z. 403–412 | Business | EE-P04-037 | Business | übereinstimmend |
| 25 | Scheduled Comms | `plans.tsx` Z. 414–423 | Business | EE-P05-030 | Business | übereinstimmend |
| 26 | Intake Assignees | `plans.tsx` Z. 425–434 | Business | EE-P04-040 | Business | übereinstimmend |
| 27 | Custom SLAs | `plans.tsx` Z. 436–445 | Business | EE-P04-038 | Business | übereinstimmend |
| 28 | Intake Forms | `plans.tsx` Z. 447–456 | Business | EE-P04-039 | Business | übereinstimmend |
| 29 | Emails For Intake (COMING SOON) | `plans.tsx` Z. 458–468 | Business | EE-P04-041 | Business | übereinstimmend |
| 30 | Shared Views | `plans.tsx` Z. 498–508 | Pro | EE-P05-025 | Pro | übereinstimmend |
| 31 | Publish Views | `plans.tsx` Z. 509–519 | Pro | EE-P05-026 | Pro | übereinstimmend |
| 32 | Dashboards and Widgets | `plans.tsx` Z. 520–530 | Pro | EE-P05-009 | Pro | übereinstimmend |
| 33 | Dashboards and Widgets | `plans.tsx` Z. 520–530 | Pro | EE-P05-010 | Pro | übereinstimmend |
| 34 | Progress Charts | `plans.tsx` Z. 537–548 | Pro | EE-P05-018 | Pro | übereinstimmend |
| 35 | Cycle Reports | `plans.tsx` Z. 549–559 | Pro | EE-P05-019 | Pro | übereinstimmend |
| 36 | Insights (COMING SOON) | `plans.tsx` Z. 560–571 | Pro | EE-P05-014 | Pro | übereinstimmend |
| 37 | Time Capsule (auskommentiert, COMING SOON) | `plans.tsx` Z. 572–583 | Business | EE-P05-017 | Business | übereinstimmend |
| 38 | Advanced Pages Analytics (COMING SOON) | `plans.tsx` Z. 584–595 | Business | EE-P07-023 | Business | übereinstimmend |
| 39 | Custom Reports (COMING SOON) | `plans.tsx` Z. 596–607 | Business | EE-P05-016 | Business | übereinstimmend |
| 40 | Search (auskommentiert; Pro+ „Operator capsules from text or PQL“, COMING SOON) | `plans.tsx` Z. 625–656 | Pro | EE-P05-028 | Pro | übereinstimmend |
| 41 | PQL | `plans.tsx` Z. 657–668 | Pro | EE-P05-027 | Enterprise (Grid) | Abweichung |
| 42 | Member limit (Cloud Free 12, ab Pro Unlimited; Self-hosted ~50/~50/~200/~200/Unlimited) | `plans.tsx` Z. 675–693 | Pro | EE-P08-022 | Pro | übereinstimmend |
| 43 | Roles (Pro „Pre-defined roles“, Business „RBAC“) | `plans.tsx` Z. 694–703 | Pro | EE-P08-011 | Business | Abweichung |
| 44 | Roles (Beschreibung „… or create custom ones with RBAC“ = Business) | `plans.tsx` Z. 694–703 | Business | EE-P08-012 | Enterprise (Grid) | Abweichung |
| 45 | Roles (Enterprise „GAC“) | `plans.tsx` Z. 694–703 | Enterprise | EE-P08-013 | Enterprise (Grid) | übereinstimmend |
| 46 | Guests („5 per paid member“) | `plans.tsx` Z. 705–715 | One | EE-P08-014 | Pro | One-Regel |
| 47 | Approvals (COMING SOON) | `plans.tsx` Z. 716–727 | Business | EE-P06-008 | Business | übereinstimmend |
| 48 | „Workflows + Approvals“ (BUSINESS_PLAN_FEATURES) / Approvals | `subscription.ts` Z. 16–23 | Business | EE-P06-003 | Enterprise (Grid) | Abweichung |
| 49 | „Workflows + Approvals“ (BUSINESS_PLAN_FEATURES) | `subscription.ts` Z. 16–23 | Business | EE-P06-001 | Business | übereinstimmend |
| 50 | Admin Interface | `plans.tsx` Z. 728–738 | Business | EE-P08-015 | Business | übereinstimmend |
| 51 | Workspace Activity Logs | `plans.tsx` Z. 739–749 | Business | EE-P08-016 | Business | übereinstimmend |
| 52 | API-enabled Audit Logs (COMING SOON) | `plans.tsx` Z. 750–761 | Business | EE-P08-017 | Enterprise (Grid) | Abweichung |
| 53 | Trigger And Action (+ PRO_PLAN_FEATURES) | `plans.tsx` Z. 768–778 | Pro | EE-P06-009 | Business | Abweichung |
| 54 | Decisions And Loops Automation (COMING SOON) | `plans.tsx` Z. 779–790 | Business | EE-P06-015 | Business | übereinstimmend |
| 55 | Number of automations (5,000 / 10,000 / Unlimited) | `plans.tsx` Z. 791–801 | Pro | EE-P06-016 | Pro | übereinstimmend |
| 56 | Real-time Collab | `plans.tsx` Z. 819–829 | One | EE-P07-007 | Pro | One-Regel |
| 57 | Work item Embeds | `plans.tsx` Z. 830–840 | One | EE-P07-010 | Pro | One-Regel |
| 58 | Link-to-work items | `plans.tsx` Z. 841–851 | One | EE-P07-012 | Pro | One-Regel |
| 59 | Publish | `plans.tsx` Z. 852–863 | One | EE-P07-008 | Pro | One-Regel |
| 60 | Wiki | `plans.tsx` Z. 864–874 | One | EE-P07-001 | Pro | One-Regel |
| 61 | Exports (Pro „One download at a time“, Business+ „Queued downloads“) | `plans.tsx` Z. 875–885 | Pro | EE-P07-009 | Pro | übereinstimmend |
| 62 | Templates („Use pages as templates …“) | `plans.tsx` Z. 886–896 | Pro | EE-P06-022 | Pro | übereinstimmend |
| 63 | Versions (2 days / 3 months / Unlimited) | `plans.tsx` Z. 897–907 | Pro | EE-P07-005 | Pro | übereinstimmend |
| 64 | Databases + Formulas (COMING SOON) | `plans.tsx` Z. 908–920 | Business | EE-P07-018 | Business | übereinstimmend |
| 65 | „Databases + Formulas“ (ENTERPRISE_PLAN_FEATURES, planHighlights.enterprise) | `subscription.ts` Z. 7–14 | Enterprise | EE-P07-018 | Business | Abweichung |
| 66 | Nested Pages (COMING SOON) | `plans.tsx` Z. 921–932 | Business | EE-P07-004 | Business | übereinstimmend |
| 67 | Importers: Jira (Free/One „Without custom props“, Pro+ „With custom props“) | `plans.tsx` Z. 939–949 | Free | EE-P09-020 | Commercial-Free | übereinstimmend |
| 68 | Importers: GitHub (Free/One „Without custom props“, Pro+ „With custom props“) | `plans.tsx` Z. 950–960 | Free | EE-P09-028 | Commercial-Free | übereinstimmend |
| 69 | Integrations (Sektion COMING SOON) | `plans.tsx` Z. 963–1025 | Pro | EE-P09-001 | Pro | übereinstimmend |
| 70 | Integrations: GitHub | `plans.tsx` Z. 968–979 | Pro | EE-P09-002 | Pro | übereinstimmend |
| 71 | Integrations: GitHub | `plans.tsx` Z. 968–979 | Pro | EE-P09-003 | Pro | übereinstimmend |
| 72 | Integrations: GitHub („Sync Plane work items and states …“) | `plans.tsx` Z. 968–979 | Pro | EE-P09-004 | Pro | übereinstimmend |
| 73 | Integrations: GitHub | `plans.tsx` Z. 968–979 | Pro | EE-P09-005 | Pro | übereinstimmend |
| 74 | Integrations: Slack | `plans.tsx` Z. 980–990 | Pro | EE-P09-009 | Pro | übereinstimmend |
| 75 | Integrations: Slack | `plans.tsx` Z. 980–990 | Pro | EE-P09-010 | Pro | übereinstimmend |
| 76 | Integrations: Slack („use / commands in Slack“) | `plans.tsx` Z. 980–990 | Pro | EE-P09-011 | Pro | übereinstimmend |
| 77 | Integrations: Zapier | `plans.tsx` Z. 991–1001 | Pro | EE-P09-015 | Pro | übereinstimmend |
| 78 | Integrations: Zendesk | `plans.tsx` Z. 1002–1012 | Pro | EE-P09-016 | Pro | übereinstimmend |
| 79 | Integrations: Freshdesk | `plans.tsx` Z. 1013–1023 | Pro | EE-P09-017 | Pro | übereinstimmend |
| 80 | Storage: Space / Max file size (cloudOnly) | `plans.tsx` Z. 1026–1054 | Pro | EE-P08-023 | Cloud-only | übereinstimmend (Sektion cloudOnly; Kontingente ab Pro) |
| 81 | SAML | `plans.tsx` Z. 1059–1069 | One | EE-P08-001 | Pro | One-Regel |
| 82 | OIDC (selfHostedOnly) | `plans.tsx` Z. 1070–1081 | One | EE-P08-002 | Pro | One-Regel |
| 83 | SAML / OIDC (Workspace-SSO, Dok. 20 PF-93) | `plans.tsx` Z. 1059–1081 | One | EE-P08-003 | Business | Abweichung |
| 84 | Domain Security | `plans.tsx` Z. 1082–1093 | Pro | EE-P08-010 | Pro | übereinstimmend |
| 85 | Two-factor authentication and passkeys | `plans.tsx` Z. 1094–1104 | Pro | EE-P08-007 | Pro | übereinstimmend |
| 86 | Two-factor authentication and passkeys | `plans.tsx` Z. 1094–1104 | Pro | EE-P08-008 | Pro | übereinstimmend |
| 87 | Password Policy | `plans.tsx` Z. 1105–1115 | Pro | EE-P08-009 | Pro | übereinstimmend |
| 88 | LDAP (COMING SOON) | `plans.tsx` Z. 1116–1127 | Enterprise | EE-P08-004 | Enterprise (Grid) | übereinstimmend |
| 89 | One-click Deployment, Digital Ocean Marketplace app, Heroku Platform app, AWS AMI | `plans.tsx` Z. 1146–1189 | One | EE-P03-009 | Pro | One-Regel |
| 90 | Private deployments (COMING SOON) | `plans.tsx` Z. 1190–1201 | Enterprise | EE-P03-010 | Enterprise (Grid) | übereinstimmend |
| 91 | Support: Channels, SLA | `plans.tsx` Z. 1208–1252 | Pro | EE-P08-024 | Pro | übereinstimmend |
| 92 | „Full-suite professional services“ (ENTERPRISE_PLAN_FEATURES; betrifft nur die Abstufung, die Matrix nennt sie bereits für Business) | `subscription.ts` Z. 7–14 | Enterprise | EE-P08-024 | Pro | Abweichung |
| 93 | „Teamspaces“ (PRO_PLAN_FEATURES) | `subscription.ts` Z. 25–32 | Pro | EE-P05-001 | Pro | übereinstimmend |
| 94 | Upsell `wiki.upgrade_flow.description` „… shared pages … with Plane Pro.“ | `wiki.json` Z. 89–91 | Pro | EE-P07-015 | Business | Abweichung |

---

## Anhang C: Rückverfolgung aller 450 Quell-Einträge → EE-ID

Spalte „Plan (Quelle)“ = Feld `tier` des Quell-Eintrags (unverändert). `~EE-…` = Zuordnung als Teilaspekt; `X-…` = nicht gezählt (Kap. 7.3).

#### P01 – `P01.paid.json` (105 Einträge) → Dok. 20

| Quell-ID | Name im Quell-Eintrag | Plan (Quelle) | → EE-ID(s) |
|---|---|---|---|
| PF-01 | Advanced Estimates (Time-System, Edit/Switch/Reorder) | Pro | EE-P04-031 |
| PF-02 | Bulk Ops | One | EE-P04-019 |
| PF-03 | Time Tracking + Worklogs | One | EE-P04-028 |
| PF-04 | Active Cycles (Workspace) | One | EE-P05-022 |
| PF-05 | Work item Types | Pro | EE-P04-001 |
| PF-06 | Custom Properties (Projekt-Ebene) | Pro | EE-P04-003 |
| PF-07 | Workspace-Level Properties und Roll-ups | Business | EE-P04-007 |
| PF-08 | Work-Item-Type-Hierarchie | unklar | EE-P04-002 |
| PF-09 | Dependencies in Gantt | Pro | EE-P04-023 |
| PF-10 | Implements/Implemented by und Workspace-Relationstypen | unklar | ~EE-P04-024, EE-P04-025 |
| PF-11 | Work item Transfers | Pro | EE-P04-020 |
| PF-12 | Auto-transfer Cycle Work items | Pro | EE-P05-021 |
| PF-13 | Auto-schedule Cycles | unklar | EE-P05-020 |
| PF-14 | Epics | Pro | EE-P04-009 |
| PF-15 | Initiatives | Pro | EE-P04-011 |
| PF-16 | Checkpoints | Pro | EE-P04-013 |
| PF-17 | Milestones | unklar | EE-P04-014 |
| PF-18 | Module Overview | Pro | EE-P04-026 |
| PF-19 | Auto-assignment in Modules | Pro | EE-P04-027 |
| PF-20 | Public, Private und Secret Projects | Pro | EE-P04-032 |
| PF-21 | State of Projects / Project Grouping / Projekt-Labels | Pro | EE-P04-033, ~EE-P04-034 |
| PF-22 | Project Overview | Pro | EE-P04-035 |
| PF-23 | Project Updates | Pro | EE-P04-036 |
| PF-24 | Pre-defined work item Templates | Pro | EE-P06-023 |
| PF-25 | Work-Item-Templates | Pro | EE-P06-021 |
| PF-26 | Project Templates | Business | EE-P06-020 |
| PF-27 | Page-Templates | Pro | EE-P06-022 |
| PF-28 | Template-Marketplace | unklar | EE-P06-024 |
| PF-29 | Recurring work items | Business | EE-P06-025 |
| PF-30 | Teamspaces | Pro | EE-P05-001 |
| PF-31 | Teamspace Cycles | Business | EE-P05-005 |
| PF-32 | Baselines And Deviations | Business | EE-P04-037 |
| PF-33 | Scheduled Comms | Business | EE-P05-030 |
| PF-34 | Intake Assignees / Intake-Verantwortung | Business | EE-P04-040 |
| PF-35 | Custom SLAs | Business | EE-P04-038 |
| PF-36 | Intake Forms | Business | EE-P04-039 |
| PF-37 | Emails For Intake | Business | EE-P04-041 |
| PF-38 | Work Item in anderes Projekt duplizieren | unklar | EE-P04-022 |
| PF-39 | Kommentar-Antworten | unklar | EE-P04-043 |
| PF-40 | Up-/Downvotes in der App | unklar | EE-P04-042 |
| PF-41 | Customers | Business | EE-P04-016 |
| PF-42 | Releases | unklar | EE-P04-015 |
| PF-43 | Shared Views | Pro | EE-P05-025 |
| PF-44 | Publish Views | Pro | EE-P05-026 |
| PF-45 | Dashboards and Widgets | Pro | EE-P05-009 |
| PF-46 | Progress Charts | Pro | EE-P05-018 |
| PF-47 | Cycle Reports | Pro | EE-P05-019 |
| PF-48 | Insights | Pro | EE-P05-014 |
| PF-49 | Advanced Pages Analytics | Business | EE-P07-023 |
| PF-50 | Custom Reports / erweiterte Analytics-Tabs | Business | ~EE-P05-015, EE-P05-016 |
| PF-51 | Time Capsule | Business | EE-P05-017 |
| PF-52 | PQL / erweiterte Filteroperatoren | Pro | EE-P05-027, ~EE-P05-028 |
| PF-53 | Advanced Search (OpenSearch) | Pro | EE-P05-029 |
| PF-54 | Rollen: Pre-defined / RBAC / GAC | Pro | EE-P08-011 |
| PF-55 | Member-/Seat-/Guest-Limits | One | ~EE-P08-014, EE-P08-022 |
| PF-56 | Approvals | Business | EE-P06-008 |
| PF-57 | Admin Interface | Business | EE-P08-015 |
| PF-58 | Workspace Activity Logs | Business | EE-P08-016 |
| PF-59 | API-enabled Audit Logs | Business | EE-P08-017 |
| PF-60 | Mitglieder-Import per CSV | unklar | EE-P09-029 |
| PF-61 | Multi-Workspace-Management | Enterprise Grid | EE-P01-001 |
| PF-62 | Workspace-Access-Tokens | unklar | EE-P09-049 |
| PF-63 | Custom Automations (Trigger/Bedingung/Aktion) | Business | EE-P06-009 |
| PF-64 | Globale Workspace-Automationen | Enterprise Grid | EE-P06-013 |
| PF-65 | Decisions And Loops Automation | Business | EE-P06-015 |
| PF-66 | Anzahl Automationen | Pro | EE-P06-016 |
| PF-67 | Auto-Reminders | Business | EE-P06-026 |
| PF-68 | Workflows | Business | EE-P06-001 |
| PF-69 | Plane Runner / Scripts | Enterprise Grid | EE-P06-019 |
| PF-70 | Real-time Collab (Live-Cursor/Presence) | One | EE-P07-007 |
| PF-71 | Work item Embeds | One | EE-P07-010 |
| PF-72 | Link-to-work items | One | EE-P07-012 |
| PF-73 | Publish Pages | One | EE-P07-008 |
| PF-74 | Wiki inkl. Collections | Pro | EE-P07-001, ~EE-P07-002 |
| PF-75 | Page-Exports Word/Queued | Pro | EE-P07-009 |
| PF-76 | Page-Versionen Aufbewahrung | Pro | EE-P07-005 |
| PF-77 | Databases + Formulas in Pages | Business | EE-P07-018 |
| PF-78 | Nested Pages | Business | EE-P07-004 |
| PF-79 | Page-Kommentare | Business | EE-P07-013, ~EE-P07-014 |
| PF-80 | Pages verschieben / teilen | Pro | ~EE-P07-015, EE-P07-017 |
| PF-81 | Editor-Attachments und External Embeds | Pro | ~EE-P07-020, EE-P07-021 |
| PF-82 | Plane AI | Pro | EE-P09-030 |
| PF-83 | Importer mit Custom Props (Jira, GitHub) | Pro | ~EE-P09-019, EE-P09-020, ~EE-P09-028 |
| PF-84 | GitHub-Integration inkl. Enterprise | Pro | EE-P09-002, ~EE-P09-005 |
| PF-85 | GitLab-Integration inkl. Enterprise | Pro | EE-P09-006, ~EE-P09-007 |
| PF-86 | Slack-Integration | Pro | EE-P09-009 |
| PF-87 | Sentry-Integration | Pro | EE-P09-012 |
| PF-88 | Bitbucket Data Center | Pro | EE-P09-008 |
| PF-89 | Zapier | Pro | EE-P09-015 |
| PF-90 | Zendesk / Freshdesk | Pro | EE-P09-016, ~EE-P09-017 |
| PF-91 | OAuth Bridge | unklar | EE-P09-018 |
| PF-92 | Applications / OAuth-Apps / Marketplace | unklar | EE-P09-044, ~EE-P09-045 |
| PF-93 | Workspace-SSO SAML/OIDC mit Domain-Verifizierung | One | ~EE-P08-001, ~EE-P08-002, EE-P08-003 |
| PF-94 | Domain Security | Pro | EE-P08-010 |
| PF-95 | 2FA und Passkeys | Pro | EE-P08-007, ~EE-P08-008 |
| PF-96 | Password Policy | Pro | EE-P08-009 |
| PF-97 | LDAP | Enterprise Grid | EE-P08-004 |
| PF-98 | IdP-Group-Sync (+ SCIM) | Enterprise Grid | EE-P08-005, ~EE-P08-006 |
| PF-99 | Storage-Quoten / Max File Size | Cloud-only | EE-P08-023 |
| PF-100 | Deployment-Varianten / Private deployments | One | ~EE-P03-002, ~EE-P03-003, EE-P03-009, ~EE-P03-010 |
| PF-101 | Support-Kanäle / SLA | Pro | EE-P08-024 |
| PF-102 | Product Tour / Get started | unklar | EE-P01-002 |
| PF-103 | Billing, Trial, Seats, Upgrade-Flows | Cloud-only | EE-P08-018 |
| PF-104 | Duplicate Detection (Duplikat-Vorschläge beim Anlegen von Work Items und Intake-Requests) | unklar | EE-P09-039 |
| PF-105 | Weitere Commercial-Produkte ohne Funktionsspur (Desk, Bridge, Briefs, Workgraph, PII-Scanner 'Argus', Libra… | unklar | ~EE-P08-027, X-01 |

#### P02 – `P02.paid.json` (43 Einträge) → Dok. 21

| Quell-ID | Name im Quell-Eintrag | Plan (Quelle) | → EE-ID(s) |
|---|---|---|---|
| F01 | Epics (Work-Item-Typ Epic + Epic-API) | Pro | EE-P04-009 |
| F02 | Initiatives (inkl. Projekt-/Work-Item-Verknüpfung; Sub-Initiativen UNVERIFIZIERT) | Pro | EE-P04-011 |
| F03 | Initiative-Labels | Pro | EE-P04-012 |
| F04 | Customers (Kunden, Requests, Kunden-Properties, Werte, Work-Item-Links) | Business | EE-P04-016, ~EE-P04-017, ~EE-P04-018 |
| F05 | Teamspaces | Pro | EE-P05-001 |
| F06 | Milestones | Pro | EE-P04-014 |
| F07 | Time Tracking / Worklogs | Pro | EE-P04-028 |
| F08 | Work Item Types | Pro | EE-P04-001 |
| F09 | Custom Properties (Properties, Dropdown-Optionen, Werte) | Pro | EE-P04-003 |
| F10 | Formula-Properties | Pro | EE-P04-006 |
| F11 | Work-Item-Type-Schema-Endpunkt (LLM/MCP) | Pro | EE-P02-001 |
| F12 | IdP Group Sync | Enterprise Grid | EE-P08-005 |
| F13 | Work-Item <-> Page-Links | Pro | EE-P07-012 |
| F14 | Pages-Public-API und Wiki (Workspace-Seiten, Collections, Nested Pages) | Pro | EE-P07-001 |
| F16 | Projekt-Feature-Toggle-API | unklar | EE-P02-002 |
| F17 | Workspace-Feature-Toggle-API | unklar | EE-P02-003 |
| F18 | Project Grouping (Projekt-States + Projekt-Labels) | Pro | EE-P04-033, ~EE-P04-034 |
| F19 | Project Templates | Business | EE-P06-020 |
| F20 | Advanced Search (OpenSearch) | Pro | EE-P05-029 |
| F21 | Zeitbasierte Estimates (type=time) | Pro | EE-P04-031 |
| F22 | Custom Relation Definitions | Enterprise Grid | EE-P04-024 |
| F23 | Workspace-Mitglied per API entfernen (mit Seat-Reduktion) | unklar | EE-P02-004 |
| F24 | Releases (Release, Tags, Labels, Links, Kommentare, Changelog; Workspace- und Projekt-Releases) | Business | EE-P04-015 |
| F25 | PQL (Plane Query Language) | Pro | EE-P05-027 |
| F26 | Rollen-Slugs / RBAC / GAC inkl. Rollen-, Permission-Scheme- und Berechtigungs-API | Business | EE-P08-011, ~EE-P08-012, ~EE-P08-013 |
| F27 | Work-Item-/Projekt-Updates (On/Off-Track) | Pro | EE-P04-036 |
| F28 | Intake per E-Mail | Business | EE-P04-041 |
| F29 | Plane Intelligence / AI (Workspace-Feature pi) | Pro | EE-P09-030 |
| F30 | Agent Runs (Agents-Plattform: Runs, Activities, Scopes) | unklar | EE-P09-047 |
| F31 | OAuth-Apps mit Scopes für die Public-API | unklar | EE-P09-044 |
| F15 | Geteilte private Seiten (Page-Sharing, Listenfilter type=shared) | Business | EE-P07-015 |
| F32 | Public API v2 (Plattform und Konventionen) | unklar | EE-P02-005 |
| F33 | Page-API-Erweiterungen v1 (Seiten bearbeiten/archivieren/löschen, Page-Attachments, Wiki-Collections) | Pro | EE-P07-041 |
| F34 | Audit-Log-API | Business | EE-P08-017 |
| F35 | Automations-API (Projekt- und Workspace-Automationen) | Business | EE-P06-009, ~EE-P06-013 |
| F36 | Views-API (Projekt- und Workspace-Views) | unklar | EE-P02-006 |
| F37 | Work-Item-Templates-API (Projekt und Workspace) | Pro | EE-P06-021 |
| F38 | Webhooks-API v2 und Webhook-Logs | unklar | EE-P09-048 |
| F39 | Work-Item-Dependencies-API | Pro | EE-P04-023 |
| F40 | Property Contexts (kontextabhängige Workspace-Properties) | Business | EE-P04-046 |
| F41 | Artifacts / Applets (AI-Dashboards als versionierte HTML-Dokumente) | unklar | EE-P09-041 |
| F42 | Workflows-API (Workflows, Workflow-States, State-Transitions) | Business | EE-P06-001, ~EE-P06-002 |
| F43 | Workspace-Modus für Work Item Types und Properties | Enterprise Grid | EE-P04-007 |

#### P03 – `P03.paid.json` (46 Einträge) → Dok. 22

| Quell-ID | Name im Quell-Eintrag | Plan (Quelle) | → EE-ID(s) |
|---|---|---|---|
| P03-F01 | Lizenz-, Seat- und Billing-Mechanik (Monitor/Prime, Lizenzschlüssel, Lizenzdatei, Sync/Delink) | unklar | EE-P08-018, ~EE-P08-019, ~EE-P08-020, ~EE-P08-021 |
| P03-F02 | Feature-Flag-Server (Monitor) und Plan-Synchronisation | unklar | EE-P08-021 |
| P03-F03 | God-Mode-Erweiterungen (User Management, System Configurations, System Checks) | unklar | ~EE-P03-001, EE-P08-025, ~EE-P08-026 |
| P03-F04 | SAML-SSO (instanzweit, God Mode) | Pro | EE-P08-001 |
| P03-F05 | OIDC-SSO (instanzweit, God Mode) | Pro | EE-P08-002 |
| P03-F06 | Workspace-Identity: Domain-Verifizierung und Workspace-SSO (SAML/OIDC) | unklar | EE-P08-003 |
| P03-F07 | LDAP-Authentifizierung | Enterprise Grid | EE-P08-004 |
| P03-F08 | IdP Group Sync | Enterprise Grid | EE-P08-005 |
| P03-F09 | OAuth Bridge (externe IdP-JWTs als API-Credentials) | unklar | EE-P09-018 |
| P03-F10 | Domain Security, 2FA/Passkeys, Passwort-Policy | Pro | ~EE-P08-007, ~EE-P08-008, ~EE-P08-009, EE-P08-010 |
| P03-F11 | Advanced Search (OpenSearch) | Pro | EE-P05-029 |
| P03-F12 | Plane AI (PI-Dienst: Chat, Modelle, Voice, Anhänge, Nutzungsbudget) | Pro | EE-P09-030 |
| P03-F13 | Semantische Suche, Embeddings, Duplikaterkennung | unklar | EE-P09-038, ~EE-P09-039 |
| P03-F14 | Integrations-Framework Silo | Pro | EE-P09-001 |
| P03-F15 | GitHub-Integration (Cloud, Enterprise Cloud, Enterprise Server) | Pro | EE-P09-002, ~EE-P09-005 |
| P03-F16 | GitLab-Integration (GitLab.com, Self-managed) | Pro | EE-P09-006, ~EE-P09-007 |
| P03-F17 | Bitbucket-Integration (Cloud, Data Center) | Pro | EE-P09-008 |
| P03-F18 | Slack-Integration | Pro | EE-P09-009, ~EE-P09-010, ~EE-P09-011 |
| P03-F19 | Sentry-Integration | Pro | EE-P09-012 |
| P03-F20 | HubSpot-Connector | unklar | EE-P09-013 |
| P03-F21 | Cursor-Agent-Integration | unklar | EE-P09-014 |
| P03-F22 | Importer (Jira Cloud/Server, Linear, Asana, ClickUp, Notion, Confluence, CSV/Flatfile, GitHub) | Pro | EE-P09-019 |
| P03-F23 | Intake per E-Mail | Business | EE-P04-041 |
| P03-F24 | Webhooks v2 | unklar | EE-P09-048 |
| P03-F25 | OAuth-App-Plattform (Applications, Consent, Bot-/User-Token, Scopes, Installationen) | unklar | EE-P09-044 |
| P03-F26 | Agents (Agent Runs, Activities, Signals) | unklar | EE-P09-047 |
| P03-F27 | MCP-Server | unklar | EE-P09-050 |
| P03-F28 | Plane Runner (Scripts, Functions, geplante Automationen, Transition-Bedingungen) | Enterprise Grid | EE-P06-019 |
| P03-F29 | Automations-Infrastruktur (Outbox, Event-Stream, Automation-Consumer) | Pro | EE-P06-018 |
| P03-F30 | Hintergrund-Export Pages PDF/DOCX (live-exporter) | Pro | EE-P07-009 |
| P03-F31 | draw.io-Diagramme im Wiki-Editor | Pro | EE-P07-019 |
| P03-F32 | Link-Vorschauen/Embeds über Iframely | Pro | EE-P07-020 |
| P03-F33 | Argus – Sensitive-Data-/PII-Scanner | unklar | EE-P08-027 |
| P03-F34 | Health-Probes und System-Checks | unklar | EE-P03-001 |
| P03-F35 | Session-Expiry-Einstellungen im God Mode | unklar | EE-P08-026 |
| P03-F36 | Airgapped Edition | Enterprise Grid | EE-P03-002 |
| P03-F37 | FIPS-140-3-Images | Enterprise Grid | EE-P03-003 |
| P03-F38 | Betriebsfeatures (HA, Read-Replica, External Secrets, Custom CA, Storage-Proxy, GCS, OpenTelemetry, PSA/Ope… | unklar | EE-P03-004 |
| P03-F39 | Dedizierte External-API-Instanz | unklar | EE-P03-005 |
| P03-F40 | GraphQL- und Marketplace-Endpunkte | unklar | EE-P03-006, ~EE-P09-045 |
| P03-F41 | Flux – Realtime-Event-Server | unklar | EE-P03-007 |
| P03-F42 | Prime CLI und Commercial-Installationsmethoden | unklar | EE-P03-008 |
| P03-F43 | Plane Compose (project-as-code CLI) | unklar | EE-P09-051 |
| P03-F44 | Workspace-Audit-Log (Querbezug) | Business | EE-P08-017 |
| P03-F45 | GAC – Granular Access Control / Custom Roles (Querbezug) | Enterprise | ~EE-P08-012, EE-P08-013 |
| P03-F46 | Private + managed deployments (vom Hersteller betriebene private Cloud-Instanz) | Enterprise | EE-P03-010 |

#### P04 – `P04.paid.json` (53 Einträge) → Dok. 23

| Quell-ID | Name im Quell-Eintrag | Plan (Quelle) | → EE-ID(s) |
|---|---|---|---|
| WM-01 | Work Item Types (Projekt- und Workspace-Typen, Default-Typ, aktiv/inaktiv, Typwechsel) | Pro | EE-P04-001 |
| WM-02 | Work-Item-Type-Hierarchie (Level, Parent/Child-Regeln, Bruch-Validierung) | Enterprise Grid | EE-P04-002 |
| WM-03 | Custom Properties – Projekt-Ebene (Property-Engine, Werte am Work Item) | Pro | EE-P04-003 |
| WM-04 | Property-Typen (Text, Number, Dropdown, Boolean, Date, Member picker, Relation, URL, Email, File, Release p… | Pro | EE-P04-004 |
| WM-05 | Pflichtfelder, Default-Werte, Aktiv/Inaktiv, Optionen-Verwaltung | Pro | EE-P04-005 |
| WM-06 | Formula-Properties | Pro | EE-P04-006 |
| WM-07 | Workspace-Level Properties und Workspace-Level Types (Katalog, Import, Link/Unlink, Governance-Modus) | Enterprise Grid | EE-P04-007 |
| WM-08 | Roll-ups | Business | EE-P04-008 |
| WM-09 | Epics | Pro | EE-P04-009 |
| WM-10 | Epic-Fortschritt und Epic-Updates | Pro | EE-P04-010 |
| WM-11 | Initiatives | Pro | EE-P04-011 |
| WM-12 | Initiative-Labels | Pro | EE-P04-012 |
| WM-13 | Checkpoints und Updates an Projekten/Epics/Initiativen | Pro | EE-P04-013 |
| WM-14 | Milestones | Pro | EE-P04-014 |
| WM-15 | Releases (Workspace- und Projekt-Releases, Tags, Labels, Links, Kommentare, Changelog, Work-Item-Zuordnung) | Business | EE-P04-015 |
| WM-16 | Customers (Kundenprofile, Work-Item-Verknüpfung) | Business | EE-P04-016 |
| WM-17 | Customer Requests | Business | EE-P04-017 |
| WM-18 | Customer Properties | Business | EE-P04-018 |
| WM-19 | Recurring Work Items | Business | EE-P06-025 |
| WM-20 | Work Item Templates | Pro | EE-P06-021 |
| WM-21 | Pre-defined work item Templates | Pro | EE-P06-023 |
| WM-22 | Bulk Ops (Mehrfachauswahl, Property-Änderung, Archivieren, Löschen, Abonnieren) | One | EE-P04-019 |
| WM-23 | Work Item Transfers (Projekt- und Cycle-Wechsel) | Pro | EE-P04-020 |
| WM-24 | Conversions (Work Item ↔ Epic) | unklar | EE-P04-021 |
| WM-25 | Kopie eines Work Items in ein anderes Projekt | Pro | EE-P04-022 |
| WM-26 | Dependencies in Gantt | Pro | EE-P04-023 |
| WM-27 | Custom Relations (Relationsdefinitionen, Workspace-Settings „Relations“) | Enterprise Grid | EE-P04-024 |
| WM-28 | Auto-transfer Cycle Work Items (Auto-Rollover) | Pro | EE-P05-021 |
| WM-29 | Auto-schedule Cycles | Business | EE-P05-020 |
| WM-30 | Module Overview | Pro | EE-P04-026 |
| WM-31 | Auto-assignment in Modules | Pro | EE-P04-027 |
| WM-32 | Time Tracking und Worklogs | One | EE-P04-028 |
| WM-33 | Timesheets / Worklog-Downloads (Workspace) | Pro | EE-P04-029 |
| WM-34 | Timesheet-Approvals | Business | EE-P04-030 |
| WM-35 | Advanced Estimates (Time-System, Bearbeiten, Umsortieren, Systemwechsel) | Pro | EE-P04-031 |
| WM-36 | Public, Private und Secret Projects | Pro | EE-P04-032 |
| WM-37 | State of Projects / Project States (Project Grouping) | Pro | EE-P04-033 |
| WM-38 | Project Labels | unklar | EE-P04-034 |
| WM-39 | Project Overview | Pro | EE-P04-035 |
| WM-40 | Project Updates | Pro | EE-P04-036 |
| WM-41 | Project Templates | Business | EE-P06-020 |
| WM-42 | Baselines And Deviations | Business | EE-P04-037 |
| WM-43 | Custom SLAs | Business | EE-P04-038 |
| WM-44 | Intake Forms | Business | EE-P04-039 |
| WM-45 | Intake Assignees / Intake responsibility | Business | EE-P04-040 |
| WM-46 | Emails For Intake | Business | EE-P04-041 |
| WM-47 | Duplicate Detection | unklar | EE-P09-039 |
| WM-48 | Work-Item-Votes in der App (Up-/Downvotes) | unklar | EE-P04-042 |
| WM-49 | Kommentar-Antworten (Replies) | unklar | EE-P04-043 |
| WM-50 | Projektübergreifende Sub-Work-Items | unklar | EE-P04-044 |
| WM-51 | Workspace Governance für States und Labels (Label-Scopes, Projekt-Sperre) | Enterprise Grid | EE-P04-045 |
| WM-52 | Property Contexts (kontextabhängige Regeln einer Workspace-Property je Projekt- und Typ-Menge) | Enterprise Grid | EE-P04-046 |
| WM-53 | Eingebauter Relationstyp „Implements“ / „Implemented by“ | unklar | EE-P04-025 |

#### P05 – `P05.paid.json` (35 Einträge) → Dok. 24

| Quell-ID | Name im Quell-Eintrag | Plan (Quelle) | → EE-ID(s) |
|---|---|---|---|
| P05-01 | Teamspaces (Kern: Anlegen/Ändern/Löschen, Lead, Beschreibung, Logo, Mitglieder, Projekte) | Pro | EE-P05-001 |
| P05-02 | Teamspace-Work-Items (Tabs „Team“/„Project“, Gruppierung „Team project“) | Pro | EE-P05-002 |
| P05-03 | Teamspace-Projekt-Work-Items | Pro | EE-P05-003 |
| P05-04 | Teamspace-Views und Teamspace-Pages | Pro | EE-P05-004 |
| P05-05 | Teamspace Cycles | Business | EE-P05-005 |
| P05-06 | Teamspace-Kommentare/-Updates | unklar | EE-P05-006 |
| P05-07 | Workspace-Feature „Teamspaces“ (teams / is_teams_enabled) inkl. Settings-Seite | Pro | EE-P05-007 |
| P05-08 | Teamspace-bezogene Member-Auswahl, Suche, Realtime-Kontext | Pro | EE-P05-008 |
| P05-09 | Dashboards | Pro | EE-P05-009 |
| P05-10 | Dashboard-Widgets (Typen, Chart-Modelle, Achsen/Metriken, Farbpaletten) | Pro | EE-P05-010 |
| P05-11 | Dashboard-Filter inkl. PQL (Ebenen source, quick, widget) | unklar | EE-P05-011 |
| P05-12 | Dashboard-Widgets für Intake und Custom Properties | unklar | EE-P05-012 |
| P05-13 | Dashboard-Widgets in Pages einbetten („Link dashboard widgets“) | Enterprise Grid | EE-P05-013 |
| P05-14 | Insights (Hindsight, On-demand insights, Foresights) | Pro | EE-P05-014 |
| P05-15 | Erweiterte Analytics-Tabs (Cycles, Modules, Intake, Projects/Users) mit Tab-Gating | unklar | EE-P05-015 |
| P05-16 | Custom Reports | Business | EE-P05-016 |
| P05-17 | Time Capsule | Business | EE-P05-017 |
| P05-18 | Advanced Pages Analytics | Business | EE-P07-023 |
| P05-19 | Progress Charts (Cycle-Fortschritt v2, Scope-Linie, Burn-down/Burn-up) | Pro | EE-P05-018 |
| P05-20 | Cycle Reports (On-demand, Permalinks) | Pro | EE-P05-019 |
| P05-21 | Auto-schedule Cycles (wiederkehrende Cycles) | Business | EE-P05-020 |
| P05-22 | Auto-Rollover (Auto-transfer Cycle Work items) | Pro | EE-P05-021 |
| P05-23 | Workspace-weite Active Cycles | One | EE-P05-022 |
| P05-24 | Parallel Cycles | unklar | EE-P05-023 |
| P05-25 | Cycle-Aktionen „Complete“, manuelles Starten/Beenden und Archivieren laufender Cycles | unklar | EE-P05-024 |
| P05-26 | Cycle Updates (Status-Updates an Cycles) | unklar | X-02 |
| P05-27 | Shared Views | Pro | EE-P05-025 |
| P05-28 | Publish Views | Pro | EE-P05-026 |
| P05-29 | PQL (Plane Query Language) | Enterprise Grid | EE-P05-027 |
| P05-30 | Operator-Kapseln und erweiterte Filteroperatoren (Negation, OR) | Pro | EE-P05-028 |
| P05-31 | Advanced Search (OpenSearch) | Pro | EE-P05-029 |
| P05-32 | Scheduled Comms | Business | EE-P05-030 |
| P05-33 | Workspace Activity Logs | Business | EE-P08-016 |
| P05-34 | Home-, Your-Work- und Navigations-Erweiterungen | unklar | EE-P05-031 |
| P05-35 | Text to PQL (natürliche Sprache → PQL, AI) | Enterprise Grid | EE-P05-032 |

#### P06 – `P06.paid.json` (28 Einträge) → Dok. 25

| Quell-ID | Name im Quell-Eintrag | Plan (Quelle) | → EE-ID(s) |
|---|---|---|---|
| F01 | Workflows: Default-Workflow je Projekt (erlaubte State-Wechsel, Mover/Reviewer, Allow new work items, Enfor… | Business | EE-P06-001 |
| F02 | Mehrere, typ-spezifische Workflows je Projekt | Enterprise Grid | EE-P06-002 |
| F03 | Approval Flows (Workflow-Genehmigungen) | Enterprise Grid | EE-P06-003 |
| F04 | Transition Conditions / Workflow Hooks (pre/post, run_script, send_webhook) | Enterprise Grid | EE-P06-004 |
| F05 | Workflow-Änderungshistorie und Reset workflow | Business | EE-P06-005 |
| F06 | Transitions-Tab mit Time-in-State | Business | EE-P06-006 |
| F07 | Workspace Governance für Workflows (Modi, Pins, effektiver Workflow) | Enterprise Grid | EE-P06-007 |
| F08 | Approvals auf Workspace-, Projekt- und Work-Item-Type-Ebene | Business | EE-P06-008 |
| F09 | Custom Automations (Trigger → Bedingungen → Aktionen), Projektebene | Business | EE-P06-009 |
| F10 | Automation-Trigger (Work item created/updated, State changed, Assignee changed, Comment added, Scheduled) | Business | EE-P06-010 |
| F11 | Automation-Bedingungen ('Provided') | Business | EE-P06-011 |
| F12 | Automation-Aktionen (Change property, Add comment, Send webhook, Run script) | Business | EE-P06-012 |
| F13 | Global (Workspace-)Automations | Enterprise Grid | EE-P06-013 |
| F14 | Scheduled Automations (Fixed Daily/Weekly/Monthly oder Cron) | Enterprise Grid | EE-P06-014 |
| F15 | Decisions and Loops Automation | Business | EE-P06-015 |
| F16 | Anzahl Automationen je Workspace | Pro | EE-P06-016 |
| F17 | Automation-Ausführungslogs (Activity / Run History) | Business | EE-P06-017 |
| F18 | Automation-Consumer / Outbox-Architektur | unklar | EE-P06-018 |
| F19 | Plane Runner (Skripte und Functions für Automationen, Transitionen, Cron) | Enterprise Grid | EE-P06-019 |
| F20 | Project Templates | Business | EE-P06-020 |
| F21 | Work Item Templates (Projekt und Workspace, inkl. Sub-Work-Items) | Pro | EE-P06-021 |
| F22 | Page Templates | Pro | EE-P06-022 |
| F23 | Pre-defined Templates und Template-Marketplace (Publish, Kategorien, Verifizierung, Kopie) | Pro | EE-P06-023, EE-P06-024 |
| F24 | Recurring Work Items | Business | EE-P06-025 |
| F26 | Auto-Reminders (Fälligkeits-Erinnerungen) | Business | EE-P06-026 |
| F27 | Auto-Schedule Cycles (Querverweis Cycles) | unklar | EE-P05-020 |
| F28 | Auto-transfer Cycle Work items (Querverweis Cycles) | Pro | EE-P05-021 |
| F29 | Auto-assignment in Modules (Querverweis Modules) | Pro | EE-P04-027 |

#### P07 – `P07.paid.json` (46 Einträge) → Dok. 26

| Quell-ID | Name im Quell-Eintrag | Plan (Quelle) | → EE-ID(s) |
|---|---|---|---|
| P07-01 | Wiki (Workspace-Seiten ohne Projekt) inkl. Wiki-Home, Sidebar, Feature-Toggle | One | EE-P07-001 |
| P07-02 | Wiki-Collections (öffentlich, Default 'General') inkl. Drag-and-drop-Reordering | Pro | EE-P07-002 |
| P07-03 | Private Collections (nur eingeladene Mitglieder) | Business | EE-P07-003 |
| P07-04 | Nested Pages (Unterseiten, Hierarchie, Umhängen) | Business | EE-P07-004 |
| P07-05 | Page-Versionen: Aufbewahrung | Pro | EE-P07-005 |
| P07-06 | Versionen: 'Highlight changes', Vergleich zweier Versionen, Server-Restore | unklar | EE-P07-006 |
| P07-07 | Real-time Collaboration (Presence-Avatare + Live-Cursor; Realtime für Wiki/Teamspace) | One | EE-P07-007 |
| P07-08 | Page-Publish (öffentlicher Link, Kommentare Externer, Report) | One | EE-P07-008 |
| P07-09 | Page-Exports PDF/Word/Markdown, Hintergrund-Queue, ZIP inkl. Unterseiten | Pro | EE-P07-009 |
| P07-10 | Page Templates (Workspace- und Projekt-Ebene) | Pro | EE-P06-022 |
| P07-11 | Work-Item-Embeds in Pages (Block) | One | EE-P07-010 |
| P07-12 | Work-Item-Mentions in Pages & 'Create work item from selection' | Business | EE-P07-011 |
| P07-13 | Link Pages ↔ Work Items (Pages-Sektion im Work Item) | One | EE-P07-012 |
| P07-14 | Inline-Kommentare (an markiertem Text, Threads, Resolve) | Business | EE-P07-013 |
| P07-15 | Page-Level-Kommentare, Kommentar-Filter, Moderation (hide/unhide) | unklar | EE-P07-014 |
| P07-16 | Page-Sharing / Access-Control (Mitglieder, Can view/comment/edit) | Business | EE-P07-015 |
| P07-17 | Teamspace-Pages | Pro | EE-P05-004 |
| P07-18 | Page Labels (eigene Workspace-Seitenlabels) | Business | EE-P07-016 |
| P07-19 | Moving Pages (Projekt ↔ Projekt ↔ Teamspace ↔ Wiki/Collection) | Pro | EE-P07-017 |
| P07-20 | Databases + Formulas in Pages | Business | EE-P07-018 |
| P07-21 | Draw.io-Diagramme und -Boards | Business | EE-P07-019 |
| P07-22 | Externe Embeds / Rich Cards (Iframely), Medien per URL | Pro | EE-P07-020 |
| P07-23 | Attachments in Pages (inkl. Office-Bearbeitung) | Pro | EE-P07-021 |
| P07-24 | Video-Block | Pro | EE-P07-022 |
| P07-25 | Advanced Pages Analytics (Page + Collection) | Business | EE-P07-023 |
| P07-26 | Stickies-Erweiterungen (Abgrenzungseintrag) | unklar | X-03 |
| P07-27 | Plane AI im Editor: Selection-Aktionen und Seitenzusammenfassung | Pro | EE-P07-024 |
| P07-28 | Plane AI: AI-Block (/ai) | Business | EE-P07-025 |
| P07-29 | Plane AI: Prompt/Agent in Pages mit Proposals (accept/reject) | Business | EE-P07-026 |
| P07-30 | Editor-Block Columns (2/3/4 Spalten) | Pro | EE-P07-027 |
| P07-31 | Editor-Block Tabs (horizontal/vertikal) | Business | EE-P07-028 |
| P07-32 | Editor-Block Toggle (aufklappbar) | Business | EE-P07-029 |
| P07-33 | Editor-Inline Status (farbiges Label) | Pro | EE-P07-030 |
| P07-34 | Editor-Inline Date | Pro | EE-P07-031 |
| P07-35 | Block- und Inline-Gleichungen (LaTeX) | Business | EE-P07-032 |
| P07-36 | Mermaid-Diagramm-Block | unklar | EE-P07-033 |
| P07-37 | HTML-Artifact-Block (sandboxed) | Business | EE-P07-034 |
| P07-38 | Table-of-contents-Block | Business | EE-P07-035 |
| P07-39 | 'Link pages'-Block (Live-Liste von Wiki-Seiten) | Business | EE-P07-036 |
| P07-40 | Page-Embed-Block (/page) und 'Linked page embed' | Business | EE-P07-037 |
| P07-41 | Widget-Block (Chart aus Work-Item-Daten) | unklar | EE-P07-038 |
| P07-42 | 'Link dashboard widgets'-Block | Enterprise Grid | EE-P05-013 |
| P07-43 | Block-Links (Link auf einen Block kopieren) | unklar | EE-P07-039 |
| P07-44 | Page-Benachrichtigungen (Freigabe-Mail, Page-Subscriber) | unklar | EE-P07-040 |
| P07-45 | Pages-Public-API (v1/v2: Pages, Collections, Templates, Published Pages, Attachments, Work-Item-Pages, MCP) | unklar | EE-P07-041 |
| P07-47 | Erweiterte Mentions im Document-Editor (Seiten/Projekte/Zyklen/Module) und Backlinks | unklar | EE-P07-042 |

#### P08 – `P08.paid.json` (33 Einträge) → Dok. 27

| Quell-ID | Name im Quell-Eintrag | Plan (Quelle) | → EE-ID(s) |
|---|---|---|---|
| P08-01 | SAML-SSO (instanzweit, God Mode, inkl. God-Mode-Login per SSO) | Pro | EE-P08-001 |
| P08-02 | OIDC-SSO (instanzweit, God Mode) | Pro | EE-P08-002 |
| P08-03 | Workspace-Identity: verifizierte Domains + Workspace-SSO (SAML oder OIDC) | Business | EE-P08-003 |
| P08-04 | LDAP-Authentifizierung | Enterprise Grid | EE-P08-004 |
| P08-05 | IdP Group Sync | Enterprise Grid | EE-P08-005 |
| P08-06 | SCIM-Provisioning | Enterprise Grid | EE-P08-006 |
| P08-07 | Zwei-Faktor-Authentifizierung | Pro | EE-P08-007 |
| P08-08 | Passkeys | Pro | EE-P08-008 |
| P08-09 | Password Policy | Pro | EE-P08-009 |
| P08-10 | Domain Security | Pro | EE-P08-010 |
| P08-11 | Rollen: System-Rollen / RBAC (Owner, Workspace Admin, Member, Guest; Projekt Admin, Contributor, Commenter,… | Business | EE-P08-011 |
| P08-12 | Custom Roles (benutzerdefinierte Rollen aus Permission Schemes) | Enterprise Grid | EE-P08-012 |
| P08-13 | GAC: Permission Schemes, bedingte Rechte und effektive Berechtigungen | Enterprise Grid | EE-P08-013 |
| P08-14 | Guests (Kontingent 5 je bezahltem Mitglied) | Pro | EE-P08-014 |
| P08-15 | Approvals (Workspace-, Projekt-, Work-Item-Type-Approvals) | Business | EE-P06-008 |
| P08-16 | Admin Interface | Business | EE-P08-015 |
| P08-17 | Workspace Activity Logs | Business | EE-P08-016 |
| P08-18 | API-enabled Audit Logs (Workspace-Audit-Log in Settings + v2-API) | Enterprise Grid | EE-P08-017 |
| P08-19 | Workspace-Lizenz und Seite 'Billing and plans' (inkl. Sync plan, Delink, Trial, Upgrade-Flow) | Pro | EE-P08-018 |
| P08-20 | Enterprise-Grid-Instanzlizenz (God Mode -> Billing) | Enterprise Grid | EE-P08-019 |
| P08-21 | Offline-Lizenzdatei (Airgapped) | Enterprise Grid | EE-P08-020 |
| P08-22 | Prime-Portal und Monitor-Dienst (Lizenzvalidierung, Feature-Flags) | unklar | EE-P08-021 |
| P08-23a | Plan One (Legacy) und Installationskanäle One-click Deployment, DigitalOcean-Marketplace-App, Heroku-App, A… | One | EE-P03-009 |
| P08-23b | Airgapped Edition | Enterprise Grid | EE-P03-002 |
| P08-23c | FIPS-140-3-Images / FIPS-Betriebsprofil | Enterprise Grid | EE-P03-003 |
| P08-23d | Private/Managed Deployments | Enterprise | EE-P03-010 |
| P08-24 | Member-Limits und Seat-Berechnung | Pro | EE-P08-022 |
| P08-25 | Storage-Limits (Workspace-Speicher, Max file size) | Cloud-only | EE-P08-023 |
| P08-26 | Support-Kanäle, SLA und 'Chat with us' | Pro | EE-P08-024 |
| P08-27 | God Mode: User Management (Instanz-Benutzer, Instanz-Admins einladen) | unklar | EE-P08-025 |
| P08-28 | God Mode: Session-Einstellungen | unklar | EE-P08-026 |
| P08-29 | Argus: Sensitive-Data-/PII-Scanner | unklar | EE-P08-027 |
| P08-31 | Mitglieder-CSV-Import (Workspace und Projekt) mit Seat-Limit | unklar | EE-P09-029 |

#### P09 – `P09.paid.json` (61 Einträge) → Dok. 28

| Quell-ID | Name im Quell-Eintrag | Plan (Quelle) | → EE-ID(s) |
|---|---|---|---|
| P09-F01 | Integrations-Framework „Silo“, Integrations-Übersicht, Workspace-/persönliche Connections | Pro | EE-P09-001 |
| P09-F02 | GitHub: Organisation verbinden, persönliches Konto, Repository-Mapping | Pro | EE-P09-002 |
| P09-F03 | GitHub: Pull-Request-Automation (PR-State-Mapping) | Pro | EE-P09-003 |
| P09-F04 | GitHub: Project Issue Sync (bi-/unidirektional inkl. Kommentare, Sub-Issues) | Pro | EE-P09-004 |
| P09-F05 | GitHub Enterprise (Server und Enterprise Cloud ghe.com) | Pro | EE-P09-005 |
| P09-F06 | GitLab (gitlab.com): MR-State-Mapping, Issue Sync | Pro | EE-P09-006 |
| P09-F07 | GitLab Self-managed („Gitlab Enterprise“) | Pro | EE-P09-007 |
| P09-F08 | Bitbucket Cloud und Bitbucket Data Center | Pro | EE-P09-008 |
| P09-F09 | Slack: Workspace verbinden, persönliches Konto, DM-Alerts | Pro | EE-P09-009 |
| P09-F10 | Slack: Projekt-Benachrichtigungen (Projekt ↔ Channel) | Pro | EE-P09-010 |
| P09-F11 | Slack: /plane-Slash-Command, Message-Shortcuts, Thread-Sync, Link-Unfurl | Pro | EE-P09-011 |
| P09-F12 | Sentry-Integration | Pro | EE-P09-012 |
| P09-F13 | HubSpot-Connector | unklar | EE-P09-013 |
| P09-F14 | Cursor-Agent-Integration | unklar | EE-P09-014 |
| P09-F15 | Zapier | Pro | EE-P09-015 |
| P09-F16 | Zendesk | Pro | EE-P09-016 |
| P09-F17 | Freshdesk | Pro | EE-P09-017 |
| P09-F18 | Microsoft Teams | unklar | X-04 |
| P09-F19 | Discord | unklar | X-05 |
| P09-F20 | OAuth Bridge (externe IdP-JWTs als API-Credentials) | unklar | EE-P09-018 |
| P09-F21 | Importer-Framework (Imports-Seite, Job-Status, Historie, Importer-Worker) | Pro | EE-P09-019 |
| P09-F22 | Jira-Cloud-Importer (inkl. Custom Properties) | Pro | EE-P09-020 |
| P09-F23 | Jira-Server/Data-Center-Importer | unklar | EE-P09-021 |
| P09-F24 | Linear-Importer | unklar | EE-P09-022 |
| P09-F25 | Asana-Importer | unklar | EE-P09-023 |
| P09-F26 | ClickUp-Importer | unklar | EE-P09-024 |
| P09-F27 | Notion-Importer | unklar | EE-P09-025 |
| P09-F28 | Confluence-Importer | unklar | EE-P09-026 |
| P09-F29 | CSV-Importer für Work Items | unklar | EE-P09-027 |
| P09-F30 | GitHub-Importer | Pro | EE-P09-028 |
| P09-F31 | Monday.com-Importer | unklar | X-06 |
| P09-F32 | Mitglieder-Import per CSV (Workspace und Projekt) | unklar | EE-P09-029 |
| P09-F33 | Plane AI: Dienst „PI“, Workspace-Feature pi, Settings-Seite „Plane AI“ | Pro | EE-P09-030 |
| P09-F34 | Pi-Chat („Plane AI“-Chat) | Pro | EE-P09-031 |
| P09-F35 | Plane AI: Connectors (MCP) | Pro | EE-P09-032 |
| P09-F36 | Plane AI: Skills | Pro | EE-P09-033 |
| P09-F37 | Plane AI: Memory | Pro | EE-P09-034 |
| P09-F38 | Plane AI: eingebaute Agents | Pro | EE-P09-035 |
| P09-F39 | AI-Assistent im Editor (Ask Pi, Selection-Aktionen, AI-Block, Page-Proposals) | Pro | EE-P07-024, ~EE-P07-025, ~EE-P07-026 |
| P09-F40 | AI-Work-Creation (Text → Work Items) und Beschreibungs-Generierung | unklar | EE-P09-037 |
| P09-F41 | AI-Suche / Semantic Search (Embeddings, Vektorsuche) | unklar | EE-P09-038 |
| P09-F42 | Duplicate Detection | unklar | EE-P09-039 |
| P09-F43 | AI-Aktionen Summary/Catch-up/Copy-as-prompt/AI-Filter | unklar | EE-P09-040 |
| P09-F44 | Applets / Artifacts (AI-generierte HTML-Dashboards) | unklar | EE-P09-041 |
| P09-F45 | LLM-Provider- und Embedding-Konfiguration | unklar | EE-P09-042 |
| P09-F46 | AI-Usage, Credits, Token-Budget | Pro | EE-P09-043 |
| P09-F47 | OAuth-App-Plattform (Build your own app, Consent, Tokens, Scopes, Installationen) | unklar | EE-P09-044 |
| P09-F48 | App-Marketplace | unklar | EE-P09-045 |
| P09-F49 | App-Mentions / Bot-User | unklar | EE-P09-046 |
| P09-F50 | Agents-Plattform (Agent Runs, Activities, Signals) | unklar | EE-P09-047 |
| P09-F51 | Webhooks v2 | unklar | EE-P09-048 |
| P09-F52 | Workspace-Access-Tokens | unklar | EE-P09-049 |
| P09-F53 | MCP-Server | unklar | EE-P09-050 |
| P09-F54 | Plane Runner | Enterprise Grid | EE-P06-019 |
| P09-F55 | Plane Compose | unklar | EE-P09-051 |
| P09-F56 | Offizielle SDKs (Node, Python) | unklar | EE-P09-052 |
| P09-F57 | Desktop-App | unklar | EE-P09-053 |
| P09-F58 | Mobile-Apps (iOS/Android) | unklar | EE-P09-054 |
| P09-F59 | draw.io-Integration (Diagramme/Boards in Pages; Aktivierung über Integrations) – Querverweis | Business | EE-P07-019 |
| P09-F60 | Flatfile-Importer (CSV über Flatfile, Beta) | Cloud-only | EE-P09-055 |
| P09-F61 | Plane AI: Autopilot-Modus (Ausführung ohne Einzelbestätigung) | Pro | EE-P09-036 |

---

## Quellenverzeichnis

| Art | Pfad / URL | Verwendung |
|---|---|---|
| Verifizierte Feature-Listen | `migration/features/_data/P01.paid.json` … `P09.paid.json` | alle 450 Einträge (Kap. 2.1, Anhang C) |
| Verifikationsprotokoll P06 | `migration/features/_data/P06.verify.json` | Gegenprobe der Einarbeitung (Kap. 2.1) |
| Detail-Dokumente | `migration/features/20-paid-spuren-im-repo.md`, `21-paid-api-referenz-developer-docs.md`, `22-paid-architektur-selfhosting-dienste.md`, `23-paid-work-management.md`, `24-paid-planung-insights-teams.md`, `25-paid-workflows-automation-templates.md`, `26-paid-wissen-pages-wiki.md`, `27-paid-sicherheit-admin-lizenz.md`, `28-paid-integrationen-importer-ai.md` | Spalte „Detail-Dok.“, Feature-Tabellen, Widersprüche, CE-Befunde |
| Grundsatzentscheidungen | `migration/architecture/00-grundsatzentscheidungen.md` | ADR-001 … ADR-006 (Kap. 9) |
| Offizielle In-Repo-Matrix | `apps/web/components/workspace/billing/comparison/plans.tsx` (Z. 1–1311) | Kap. 1.2, 1.3, 3.3, 5.7, 7.1, Anhang B |
| Rendering der Matrix | `apps/web/components/workspace/billing/comparison/base.tsx`, `root.tsx`, `plan-detail.tsx`; `apps/web/components/workspace/billing/root.tsx` | Kap. 1.2, 1.3 |
| Plan-Konstanten | `packages/constants/src/subscription.ts`, `packages/constants/src/payment.ts`, `packages/types/src/payment.ts` | Kap. 1.2, 3.3 |
| Editions-Kennzeichnung | `apps/api/plane/license/models/instance.py`, `apps/web/components/workspace/edition-badge.tsx` | Kap. 1.1 |
| CE-Code (Prüfung Kap. 6) | `apps/api/plane/db/models/{workspace,project,page,deploy_board,estimate,issue}.py`, `apps/api/plane/bgtasks/{page_version_task,cleanup_task,webhook_task}.py`, `apps/api/plane/app/urls/{project,cycle,issue,workspace,webhook}.py`, `apps/api/plane/app/views/intake/base.py`, `apps/api/plane/authentication/utils/password.py`, `apps/api/plane/license/urls.py`, `apps/api/plane/space/urls/issue.py`, `apps/api/plane/settings/common.py`, `apps/live/src/controllers/{collaboration,pdf-export}.controller.ts`, `apps/live/src/hocuspocus.ts`, `apps/space/app/routes.ts`, `apps/web/app/routes/core.ts`, `apps/web/app/(all)/[workspaceSlug]/(projects)/active-cycles/page.tsx`, `apps/web/hooks/{use-editor-flagging,use-parse-editor-content}.ts`, `apps/web/components/{pages/modals/export-page-modal,pages/version/*,project/publish-project/modal,cycles/transfer-issues-modal,cycles/analytics-sidebar/*,modules/analytics-sidebar/*,core/sidebar/progress-chart,core/modals/bulk-delete-issues-modal,issues/bulk-operations/root,issues/issue-layouts/gantt/base-gantt-root,gantt-chart/helpers/draggable,estimates/create/stage-one}.tsx`, `packages/editor/src/{hooks/use-collaborative-editor.ts,types/extensions.ts,extensions/core-without-props.ts}`, `packages/constants/src/estimates.ts`, `packages/i18n/src/locales/en/{wiki,home}.json`, `deployments/cli/community/*`, `deployments/{aio,kubernetes,swarm}/community` | Kap. 6 |
| Developer-Docs (offline) | `/home/user/makeplane/developer-docs/docs/self-hosting/{editions-and-versions,self-hosting-101,upgrade-from-community}.md`, `…/manage/manage-licenses/{activate-pro-and-business,activate-enterprise,activate-airgapped,activate-airgapped-enterprise}.md`, `…/methods/{airgapped-requirements,airgapped-edition,airgapped-edition-kubernetes,fips-deployment}.md`, `…/govern/{ldap,saml-sso,oidc-sso,advanced-search,configure-dns-email-service}.md` | Kap. 1, 3 |
| Helm-Charts (offline) | `/home/user/makeplane/helm-charts/charts/plane-enterprise/Chart.yaml`, `…/plane-ce/` | Kopfzeile, Kap. 1.1 |
| Web-Quellen (nur indirekt, über die Detail-Dokumente) | docs.plane.so, plane.so (pricing, pro, business, enterprise-grid, blog, changelog), developers.plane.so, university.plane.so, forum.plane.so – vollständige Listen in den Quellenverzeichnissen der Dokumente 20–28 | Plan-Zuordnungen mit Marker ⚠/ᵘ |
